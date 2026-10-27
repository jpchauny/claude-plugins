"""The hook that keeps a session of layer 3 out of the code repositories (ACU-38, ACU-40, ACU-45, ACU-46).

Usage:
    python3 -I deny_code_repositories.py < <PreToolUse input as JSON>

Run by the PreToolUse hook of the plugin acceptance-management. Reads the
input of the hook on stdin: the tool name, its input and the working
directory. Takes as the repository of the session the folder of the
environment variable CLAUDE_PROJECT_DIR, or else the field "cwd" of the input;
finds the project folder from its remote `origin` and `project.json`, as
ORC-21 says (the folder of the repository must end with its `path`), and takes as code repositories the entries of layer 4, each at
the project folder followed by its `path`. Resolves relative paths against
"cwd". Refuses, by printing on stdout the JSON that denies it, a call whose
fields name a path inside a code repository, a shell pattern in any path
included (ACU-45) (complete list, ACU-38):
Read, Edit and Write by "file_path"; NotebookEdit by "notebook_path"; Grep by
"path", also when it holds a code repository; Glob by "path" and by "pattern"
resolved against "path" or "cwd"; Bash by each word of "command", and by a word that holds a code repository when another
word is a recursive reader (ACU-46). In every other case, and
when the paths cannot be found (ACU-40), prints nothing and exits with
status 0.
Writes no file and uses no network. Python 3.9 or later, standard library only.
"""

import fnmatch
import json
import os
import re
import shlex
import subprocess
import sys

PATH_FIELDS = {  # ACU-38: the tools checked and the fields that hold a path
    "Read": ("file_path",),
    "Edit": ("file_path",),
    "Write": ("file_path",),
    "NotebookEdit": ("notebook_path",),
    "Grep": ("path",),
    "Glob": ("path",),
}
TOOLS = tuple(PATH_FIELDS) + ("Bash",)
GLOB_CHARS = re.compile(r"[*?\[]")
RECURSIVE_READERS = {"rg", "ag", "fd", "find", "tree"}  # ACU-46
GREPS = {"grep", "egrep", "fgrep"}
RECURSIVE_OPTIONS = {"--recursive", "--dereference-recursive"}


def git(cwd, *args):
    """The output of one git command, stripped, or None when it fails."""
    try:
        done = subprocess.run(
            ["git", "-C", cwd] + list(args),
            capture_output=True, text=True, timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if done.returncode != 0:
        return None
    return done.stdout.strip()


def owner_name(url):
    """`<owner>/<name>` of a GitHub remote URL (https, ssh or scp form), or None."""
    url = url.strip()
    if url.endswith("/"):
        url = url[:-1]
    if url.endswith(".git"):
        url = url[:-4]
    parts = re.split(r"[/:]", url)
    parts = [p for p in parts if p]
    if len(parts) < 2:
        return None
    return "%s/%s" % (parts[-2], parts[-1])


def valid_path(path):
    """ORC-20: parts separated by '/', none of them empty, '.' or '..'."""
    if not isinstance(path, str) or not path:
        return False
    return all(part not in ("", ".", "..") for part in path.split("/"))


def code_repositories(cwd):
    """ACU-45: the real paths of the code repositories, or [] when they cannot be found (ACU-40)."""
    root = git(cwd, "rev-parse", "--show-toplevel")
    if not root:
        return []
    try:
        with open(os.path.join(root, "project.json"), encoding="utf-8") as f:
            project = json.load(f)
    except (OSError, ValueError):
        return []
    remote = git(root, "config", "--get", "remote.origin.url")
    if not remote:
        return []
    me = owner_name(remote)
    repositories = project.get("repositories") if isinstance(project, dict) else None
    if not isinstance(repositories, list):
        return []
    entries = [r for r in repositories if isinstance(r, dict)]
    mine = [r for r in entries if "%s/%s" % (r.get("owner"), r.get("name")) == me]
    if len(mine) != 1 or not valid_path(mine[0].get("path")):
        return []
    parts = mine[0]["path"].split("/")
    root = os.path.realpath(root)
    if root.split(os.sep)[-len(parts):] != parts:  # ACU-40: the folder does not end with its path
        return []
    folder = root
    for _ in parts:
        folder = os.path.dirname(folder)
    found = []
    for entry in entries:
        if entry.get("layer") == 4 and valid_path(entry.get("path")):
            found.append(os.path.realpath(os.path.join(folder, *entry["path"].split("/"))))
    return found


def inside(path, directory):
    return path == directory or path.startswith(directory + os.sep)


def resolve(text, cwd):
    """The real absolute path that a path written in a tool call names."""
    text = os.path.expandvars(os.path.expanduser(text))
    if not os.path.isabs(text):
        text = os.path.join(cwd, text)
    return os.path.realpath(text)


def holds(path_text, cwd, repositories):
    """ACU-45: the code repository that one written path holds, such as the project folder, or None."""
    if not path_text or GLOB_CHARS.search(path_text):
        return None
    candidate = resolve(path_text, cwd)
    for repository in repositories:
        if repository.startswith(candidate.rstrip(os.sep) + os.sep):
            return repository
    return None


def recursive(all_words):
    """ACU-46: whether one of the words is a recursive reader."""
    if any(word in RECURSIVE_READERS for word in all_words):
        return True
    if not any(word in GREPS for word in all_words):
        return False
    for word in all_words:
        if word in RECURSIVE_OPTIONS:
            return True
        if word.startswith("-") and not word.startswith("--") and ("r" in word or "R" in word):
            return True
    return False


def names(path_text, cwd, repositories):
    """The code repository that one written path names, or None."""
    if not path_text:
        return None
    if GLOB_CHARS.search(path_text):
        return glob_names(path_text, cwd, repositories)
    candidate = resolve(path_text, cwd)
    for repository in repositories:
        if inside(candidate, repository):
            return repository
    return None


def glob_names(pattern, cwd, repositories):
    """The code repository that a shell pattern may name, such as `../billing-a*/x`, or None."""
    pattern = os.path.expandvars(os.path.expanduser(pattern))
    if not os.path.isabs(pattern):
        pattern = os.path.join(cwd, pattern)
    parts = os.path.normpath(pattern).split(os.sep)
    fixed = next(i for i, part in enumerate(parts) if GLOB_CHARS.search(part))
    prefix = os.path.realpath(os.sep.join(parts[:fixed]) or os.sep)
    parts = prefix.split(os.sep) + parts[fixed:]
    for repository in repositories:
        depth = len(repository.split(os.sep))
        if len(parts) >= depth and fnmatch.fnmatchcase(repository, os.sep.join(parts[:depth])):
            return repository
        if len(parts) < depth and inside(repository, os.sep.join(parts)):
            return repository
    return None


def words(command):  # ACU-46
    """The words of a shell command, and the parts of each around '=' and ':'."""
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        tokens = list(lexer)
    except ValueError:
        tokens = command.split()
    found = []
    for token in tokens:
        found.append(token)
        found += [part for part in re.split(r"[=:]", token) if part and part != token]
    return found


def named_repository(tool, tool_input, cwd, repositories):
    """ACU-38: the code repository that the tool call names, or None."""
    if not isinstance(tool_input, dict):
        return None
    if tool in PATH_FIELDS:
        for field in PATH_FIELDS[tool]:
            path = tool_input.get(field)
            found = names(path, cwd, repositories) if isinstance(path, str) else None
            if found:
                return found
        if tool == "Grep":
            path = tool_input.get("path")
            return holds(path, cwd, repositories) if isinstance(path, str) else None
        if tool == "Glob":
            pattern = tool_input.get("pattern")
            base = tool_input.get("path")
            if not isinstance(base, str) or not base:
                base = cwd
            if isinstance(pattern, str) and pattern:
                return names(pattern, resolve(base, cwd), repositories)
        return None
    if tool == "Bash":
        command = tool_input.get("command")
        if not isinstance(command, str):
            return None
        for repository in repositories:
            if re.search(re.escape(repository) + r"(?![^/\s'\";|&<>()`])", command):
                return repository
        all_words = words(command)
        for word in all_words:
            found = names(word, cwd, repositories)
            if found:
                return found
        if recursive(all_words):
            for word in all_words:
                found = holds(word, cwd, repositories)
                if found:
                    return found
    return None


def main():
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    if not isinstance(event, dict):
        return 0
    tool = event.get("tool_name")
    if tool not in TOOLS:
        return 0
    cwd = event.get("cwd") if isinstance(event.get("cwd"), str) and event.get("cwd") else os.getcwd()
    repositories = code_repositories(os.environ.get("CLAUDE_PROJECT_DIR") or cwd)
    if not repositories:
        return 0
    repository = named_repository(tool, event.get("tool_input"), cwd, repositories)
    if repository is None:
        return 0
    reason = (
        "ACU-12 and LAY-8: a session of layer 3 never reads or writes a code "
        "repository of layer 4, and this call names %s." % repository
    )
    json.dump({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }, sys.stdout)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # ACU-40: a hook that cannot decide refuses nothing
        sys.exit(0)
