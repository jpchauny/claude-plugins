"""The hook that keeps a session of layer 4 from writing the acceptance repository (CIM-1).

Usage:
    python3 -I guard_acceptance.py < <hook input>

Run by the PreToolUse hook of the plugin code-implementation, declared in
hooks/hooks.json for the tools Edit, Write, NotebookEdit and Bash. Reads the hook input, a
JSON object, on stdin. Each time it runs, it finds the repository of the
session (the folder of CLAUDE_PROJECT_DIR, or else the field "cwd" of the
input), reads its project.json, finds its own entry by the remote origin
(ORC-21) and, from it, the path of the acceptance repository: the entry with
"layer" 3 (ORC-20).

It refuses, with the JSON answer "permissionDecision": "deny":
  - an Edit or a Write whose "file_path", or a NotebookEdit whose
    "notebook_path", is inside the acceptance repository;
  - a Bash command that names the acceptance repository, unless each part of
    it that names that repository is a command known to only read files, with
    no output written inside it, as CIM-8 lists them (READ_COMMANDS,
    WRITE_OPTIONS, FIND_WRITES, GIT_READS). A shell command can name a path in more ways
    than this script recognises: the hook guards against mistakes, and levels
    2 and 3 of ACU-13 are the barrier.

Reading the acceptance repository is allowed: the implementing agent reads it
and runs its tests from a copy made outside it (LAY-4, IMP-16).

When there is nothing to guard (not a git repository, no project.json, a project.json that is not
valid JSON, no entry for the remote origin, a folder that does not end with
the path of its entry, a path that ORC-20 does not allow, no single
acceptance repository, an input it cannot read), it allows the call
and prints nothing. Writes no file and uses no network. Python 3.9 or later,
standard library only.
"""

import json
import os
import re
import shlex
import subprocess
import sys

# Commands that only read the files they name (complete list for this hook, CIM-8).
READ_COMMANDS = {
    "cat", "head", "tail", "less", "more", "ls", "tree", "grep", "egrep", "fgrep", "rg",
    "wc", "diff", "cmp", "stat", "file", "du", "realpath", "readlink", "basename",
    "dirname", "pwd", "echo", "printf", "test", "[", "true", "false", "jq",
    "md5", "md5sum", "shasum", "sha1sum", "sha256sum", "cd", "pushd", "popd", "find",
    "cp", "rsync", "git",
}
# Options that make a command of READ_COMMANDS write a file or run a program (CIM-8):
# the short option letters, alone or in a cluster such as "-ao", and the long options.
WRITE_OPTIONS = {
    "tree": ("o", ()),
    "less": ("oO", ("--log-file", "--LOG-FILE")),
    "rg": ("", ("--pre",)),
    "file": ("C", ()),
}
# Options of find that run or write something.
FIND_WRITES = {"-delete", "-exec", "-execdir", "-ok", "-okdir", "-fprint", "-fprint0", "-fprintf", "-fls"}
# Subcommands of git that only read the repository they name.
GIT_READS = {
    "log", "show", "diff", "status", "rev-parse", "ls-files", "ls-tree", "cat-file",
    "archive", "clone", "describe", "blame", "grep", "shortlog", "rev-list",
    "for-each-ref", "show-ref",
}
# Global options of git that make any subcommand run what they configure.
GIT_CONFIG_OPTIONS = ("-c", "--config-env")
# Global options of git that take a value in the next word.
GIT_VALUE_OPTIONS = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}
# Options of git clone that take a value in the next word.
CLONE_VALUE_OPTIONS = {
    "-b", "--branch", "-o", "--origin", "-u", "--upload-pack", "-c", "--config", "-j", "--jobs",
    "--reference", "--reference-if-able", "--separate-git-dir", "--depth", "--template",
    "--shallow-since", "--shallow-exclude", "--filter", "--bundle-uri", "--server-option",
    "--recurse-submodules-default",
}
SEPARATORS = {";", "&&", "||", "|", "&", "|&", "(", ")", "\n"}
REDIRECTIONS = {">", ">>", ">|", ">&", "&>", "&>>", "<>"}
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")


def git(folder, *args):
    try:
        result = subprocess.run(["git", "-C", folder, *args], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def owner_name(url):
    """The <owner>/<name> of a GitHub remote URL, https or ssh, without a final .git."""
    match = re.search(r"[:/]([^/:]+)/([^/]+?)(?:\.git)?/?$", url or "")
    return f"{match.group(1)}/{match.group(2)}" if match else None


def valid_path(path):
    """ORC-20: parts separated by '/', none of them empty, '.' or '..'."""
    return isinstance(path, str) and bool(path) and all(p not in ("", ".", "..") for p in path.split("/"))


class Acceptance(str):
    """The real path of the acceptance repository; labels are the names that name it in the text of a command (CIM-6)."""

    def __new__(cls, real, path):
        self = super().__new__(cls, real)
        self.labels = {path.split("/")[-1], os.path.basename(real)}
        return self

    def named_in(self, parts):
        return any(label in parts for label in self.labels)


def acceptance_path(start):
    """The real path of the acceptance repository, from the project.json of the repository of start; None when there is none."""
    root = git(start, "rev-parse", "--show-toplevel")
    if not root:
        return None
    try:
        with open(os.path.join(root, "project.json"), encoding="utf-8") as f:
            project = json.load(f)
        entries = [e for e in project["repositories"] if isinstance(e, dict)]
    except (OSError, ValueError, KeyError, TypeError):
        return None
    own = owner_name(git(root, "remote", "get-url", "origin"))
    mine = [e for e in entries if f"{e.get('owner')}/{e.get('name')}" == own]
    accepted = [e for e in entries if e.get("layer") == 3]
    if len(mine) != 1 or len(accepted) != 1:
        return None
    own_path, acc_path = mine[0].get("path"), accepted[0].get("path")
    if not valid_path(own_path) or not valid_path(acc_path):
        return None
    parts = own_path.split("/")
    folder = root
    for _ in parts:  # ORC-21: the project folder is the repository's folder without its path
        folder = os.path.dirname(folder)
    if os.path.join(folder, *parts) != root:
        return None
    return Acceptance(os.path.realpath(os.path.join(folder, *acc_path.split("/"))), acc_path)


def inside(path, folder):
    path = os.path.realpath(path)
    return path == folder or path.startswith(folder + os.sep)


def resolve(word, current):
    """A path made absolute against current, after ~ and the environment variables are replaced (CIM-1, ACU-45)."""
    word = os.path.expanduser(os.path.expandvars(word))
    return word if os.path.isabs(word) else os.path.join(current, word)


def names(word, current, accept):
    """Whether one word of a command names the acceptance repository."""
    if word.startswith("-") and "=" in word:
        word = word.split("=", 1)[1]
    if "$" in word or "`" in word:  # not resolvable here: its text decides
        return accept.named_in(re.split(r"[/\"'$(){}`\s]+", word))
    return bool(word) and inside(resolve(word, current), accept)


def segments(command):
    """The simple commands of a shell command, each as a list of words; None when it cannot be split."""
    lexer = shlex.shlex(command.replace("\n", " ; "), posix=True, punctuation_chars=";&|()<>")
    lexer.whitespace_split = True
    try:
        words = list(lexer)
    except ValueError:
        return None
    parts, part = [], []
    for word in words:
        if word in REDIRECTIONS:  # ">|" holds "|" but is a redirection, not a pipe
            part.append(word)
        elif word in SEPARATORS or (set(word) <= set(";&|()<>") and set(word) & set(";|()")
                                  or word in ("&", "&&")):
            if part:
                parts.append(part)
            part = []
        else:
            part.append(word)
    if part:
        parts.append(part)
    return parts


def has_option(args, letters, longs):
    """Whether args hold a short option of letters (alone or in a cluster) or one of the long options."""
    for a in args:
        if a == "--":
            return False
        if a.startswith("--"):
            if a.split("=", 1)[0] in longs:
                return True
        elif a.startswith("-") and len(a) > 1 and any(c in letters for c in a[1:]):
            return True
    return False


def writes(words, current, accept):
    """Whether one simple command that names the acceptance repository may write a file of it."""
    # Outputs written inside the repository, whatever the command.
    for i, word in enumerate(words[:-1]):
        if word in REDIRECTIONS or (word.endswith(">") and word.rstrip(">").isdigit()):
            if word == ">&" and (words[i + 1].isdigit() or words[i + 1] == "-"):
                continue  # ">&2" duplicates a descriptor; it writes no file
            if names(words[i + 1], current, accept):
                return True
    plain = [w for i, w in enumerate(words)
             if w not in REDIRECTIONS and w not in ("<", "<<", "<<<")
             and not (i and (words[i - 1] in REDIRECTIONS or words[i - 1] in ("<", "<<", "<<<")))]
    while plain and ASSIGNMENT.match(plain[0]):
        plain = plain[1:]
    if not plain:
        return False
    program, args = os.path.basename(plain[0]), plain[1:]
    if program not in READ_COMMANDS:
        return True
    if program in WRITE_OPTIONS and has_option(args, *WRITE_OPTIONS[program]):
        return True
    if program == "find":
        return any(a in FIND_WRITES for a in args)
    if program in ("cp", "rsync"):
        if program == "rsync" and any(a.startswith("--remove-source") or a.startswith("--delete") for a in args):
            return True
        target, positional, i = None, [], 0
        while i < len(args):
            a = args[i]
            if a == "--":
                positional += args[i + 1:]
                break
            if program == "cp" and a.startswith("--target-directory="):
                target = a.split("=", 1)[1]
            elif program == "cp" and a == "--target-directory":
                target, i = (args[i + 1] if i + 1 < len(args) else ""), i + 1
            elif program == "cp" and a.startswith("-") and not a.startswith("--") and "t" in a[1:]:
                rest = a[a.index("t", 1) + 1:]  # "-t DIR", "-tDIR", "-at DIR"
                if rest:
                    target = rest
                else:
                    target, i = (args[i + 1] if i + 1 < len(args) else ""), i + 1
            elif not a.startswith("-"):
                positional.append(a)
            i += 1
        if target is not None:  # CIM-8: the value of -t is the destination of cp
            return names(target, current, accept)
        return bool(positional) and names(positional[-1], current, accept)
    if program == "git":
        i = 0
        while i < len(args) and args[i].startswith("-"):
            if args[i].split("=", 1)[0] in GIT_CONFIG_OPTIONS:
                return True
            i += 2 if args[i] in GIT_VALUE_OPTIONS else 1
        if i >= len(args) or args[i] not in GIT_READS:
            return True
        sub, rest = args[i], args[i + 1:]
        outputs = ("-o", "--output") if sub == "archive" else ("--output",)
        for j, a in enumerate(rest):
            if a in outputs and j + 1 < len(rest) and names(rest[j + 1], current, accept):
                return True
            if a.startswith("--output=") and names(a, current, accept):
                return True
        if sub == "grep" and has_option(rest, "O", ("--open-files-in-pager",)):
            return True
        if sub == "clone":
            positional, j = [], 0
            while j < len(rest):
                a = rest[j]
                if a == "--":
                    positional += rest[j + 1:]
                    break
                if a in CLONE_VALUE_OPTIONS:
                    j += 1
                elif not a.startswith("-"):
                    positional.append(a)
                j += 1
            if not positional:
                return False
            if len(positional) >= 2:
                return names(positional[1], current, accept)
            # CIM-8: with no destination, git clone creates a folder named after the URL in the working directory.
            url = re.sub(r"/\.git$", "", positional[0].rstrip("/"))
            folder = re.sub(r"\.git$", "", re.split(r"[/:]", url)[-1]) or "repository"
            return inside(os.path.join(current, folder), accept)
        return False
    return False


def bash_reason(command, cwd, accept):
    """Why a Bash command is refused, or None when it is allowed."""
    current = cwd
    named_by_cwd = inside(cwd, accept) and bool(command.strip())
    parts = segments(command)
    if parts is None:
        if any(label in command for label in accept.labels) or named_by_cwd:
            return "it names the acceptance repository and cannot be read as a shell command"
        return None
    if ("$(" in command or "`" in command) and (any(label in command for label in accept.labels) or named_by_cwd):
        return "it names the acceptance repository and runs a command substitution"
    in_accept = named_by_cwd
    named_before = False
    for words in parts:
        named = in_accept or any(names(w, current, accept) for w in words)
        if words and os.path.basename(words[0]) in ("xargs", "parallel") and named_before:
            named = True  # it runs a command on what an earlier part found there
        named_before = named_before or named
        if words and os.path.basename(words[0]) in ("cd", "pushd"):
            target = cd_target(words)
            if target != "-":
                current = resolve(target, current)
                in_accept = inside(current, accept)
        if named and writes(words, current, accept):
            return f"the command '{' '.join(words)}' may write it"
    return None


def cd_target(words):
    """CIM-3: the first word after the program name that is not an option, or the home directory."""
    options = True
    for word in words[1:]:
        if options and word == "--":
            options = False
        elif options and word.startswith("-") and word != "-":
            continue
        else:
            return word
    return os.path.expanduser("~")


def reason(data, accept):
    tool, tool_input = data.get("tool_name"), data.get("tool_input")
    cwd = data.get("cwd")
    if not isinstance(tool_input, dict):
        return None
    if not isinstance(cwd, str) or not cwd:
        cwd = os.getcwd()
    if tool in ("Edit", "Write", "NotebookEdit"):
        path = tool_input.get("notebook_path" if tool == "NotebookEdit" else "file_path")
        if isinstance(path, str) and path and inside(resolve(path, cwd), accept):
            return f"{path} is a file of it"
        return None
    if tool == "Bash":
        command = tool_input.get("command")
        return bash_reason(command, cwd, accept) if isinstance(command, str) else None
    return None


def main():
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return 0
    if not isinstance(data, dict):
        return 0
    cwd = data.get("cwd")
    start = os.environ.get("CLAUDE_PROJECT_DIR") or (cwd if isinstance(cwd, str) else "") or os.getcwd()
    accept = acceptance_path(start)
    if not accept:
        return 0
    why = reason(data, accept)
    if why:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                f"A session of layer 4 never writes the acceptance repository {accept} (CIM-1, LAY-4): {why}. "
                "Reading it is allowed; run its acceptance tests in a copy made outside it (IMP-16)."),
        }}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # a hook that cannot decide refuses nothing (CIM-5)
        sys.exit(0)
