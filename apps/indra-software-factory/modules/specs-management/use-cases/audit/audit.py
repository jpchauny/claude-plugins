#!/usr/bin/env python3
"""Deterministic parts of /specs-management:audit (spec: use-cases/audit/specs/audit.md).

Commands, run as `python3 audit.py <command>`:

  prepare [--part N] [--] [arg]       the arguments, already split (AUD-11)
  prepare [--part N] --raw '<words>'  the words after /specs-management:audit, split here (AUD-11)
  prepare [--part N] --raw-stdin      the same words, read from stdin
  filter [--part N]          AUD-29 steps 2 and 3, and the placement of AUD-19;
                             JSON on stdin and stdout; `spec_files` (from
                             prepare) required for a finding across files,
                             the only kind with See also places (AUD-20);
                             `spc14_applies_to` (the
                             selected files where SPC-14 applies) required for
                             an SPC-14 finding across files
  render [--part N]          the report of AUD-30 to AUD-35; JSON on stdin,
                             `selected`, `spec_files`, `link_reports` and
                             `links_not_checked` (from prepare) required
                             (AUD-35, AUD-46); refuses a finding that
                             AUD-29 step 2 drops on the bytes filter read (AUD-46)

prepare also does the check of the links between layers 0 and 1 (AUD-54 to
AUD-59): `link_reports`, the links of AUD-56, and `links_not_checked`, null or
the reason of AUD-59 when the other layer cannot be found or read; that check
never makes prepare refuse. It reads, of the other layer, only the paths of its
tree at HEAD and its project.json (AUD-55), with scripts/layers.py and
scripts/mdlinks.py of the plugin.

prepare, filter and render print at most PART_SIZE characters per call, so that
the Bash tool shows their output whole (AUD-30, AUD-38): a longer output comes
in parts, part N with `--part N` (1 when left out), each carrying the same
`run`, a digest of the whole output (AUD-41). prepare's and filter's every part
is one JSON object with "part", "parts" and "run" (a filter part with "piece"
is followed by a slice of one finding's JSON text); render's report, when it
has more than one part, starts each part with the line `[part N of M, run R]`,
not part of the report.

prepare tests the conditions of AUD-40 in order; at the first that holds
it prints only its message on stdout and exits with status 1. Otherwise it
prints JSON and exits with status 0. filter and render exit with status 2
on input they cannot use, a finding whose fields have other types than
SKILL.md states included, with the reason on stderr.

AUD-5: this script never creates, edits, moves or deletes a file. Data
comes on stdin and goes to stdout. Python 3.9+, standard library only.
"""

import errno
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import unicodedata

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
# AUD-54: the links are found as scripts/mdlinks.py finds them, and the layers as ORC-37 says.
# AUD-5: importing them writes no __pycache__.
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(PLUGIN_ROOT, "scripts"))
import layers  # noqa: E402
# AUD-15: the guideline is writing-specs.md at the root of the plugin specs-management, and no other place.
GUIDELINE = os.path.join(PLUGIN_ROOT, "writing-specs.md")

# Term "Binding rule" (complete list), in the order of AUD-34.
BINDING_RULES = ["SPC-%d" % i for i in range(1, 21)] + ["SPC-T4", "SPC-T5", "SPC-T11", "SPC-T14", "SPC-T15"]
RULE_ORDER = {rule: index for index, rule in enumerate(BINDING_RULES)}
CONDITIONAL_RULES = ["SPC-%d" % i for i in range(13, 21)]
QUESTION_IDS = ["SPC-Q%d" % i for i in range(1, 18)]

# AUD-42: the labels and reasons of the passes under "Not audited".
ACROSS_LABEL = "across files (SPC-3, SPC-11, SPC-13, SPC-14, SPC-Q4, SPC-Q12)"
ACROSS_REASON = "the pass failed or did not finish"
READERS_LABEL = "readers (SPC-Q2, SPC-Q3)"
READERS_REASON = "a reader failed or did not finish"
CONTEXT_REASON = "could not be read (context only)"
FOLDER_REASON = "could not be searched"
FILE_REASONS = ("could not be read", "the auditor failed or did not finish", "the run was stopped", CONTEXT_REASON)
LINKS_LABEL = "links between layers"
# AUD-59: the reasons of the line of LINKS_LABEL, in the order of its conditions.
LINKS_REASONS = re.compile(
    r"\A(project\.json is missing or does not have the form of ORC-20|this repository is not in project\.json"
    r"|the repository is not of layer 0 or of layer 1|project\.json has no repository of layer [01]"
    r"|.+ is not at .+|project\.json differs from the copy of layer 1|git failed: .*)\Z", re.S)

# AUD-57: the problem and the rewrite of each case of AUD-56; None is the plain link of ORC-41.
LINK_CASES = {
    1: ("layer 1", "absent link whose link target exists in layer 1", None),
    2: ("layer 1", "absent link whose link target exists neither in layer 1 nor in layer 0",
        "delete the whole link, its text and its destination, and rewrite or delete its sentence"),
    3: ("layer 0", "plain link whose link target exists neither in layer 0 nor in layer 1",
        "delete the link, or fix its destination"),
}

# R62 of the module norms-management, specs/norms-versions.md: the excluded paths (fixed list).
AGENT_FILES = frozenset(n.casefold() for n in ("CLAUDE.md", "CLAUDE.local.md", "AGENTS.md"))
ROOT_COMMUNITY_FILES = frozenset(
    n.casefold() for n in ("LICENSE.md", "CHANGELOG.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "SECURITY.md")
)


class Refusal(Exception):
    """An AUD-40 condition holds; the message is the whole reply."""


class BadInput(Exception):
    """filter or render got input they cannot use."""


# ---------------------------------------------------------------- arguments


# AUD-11: POSIX.1-2017, Shell Command Language, adopted in part: quoting (2.2),
# token recognition (2.3) and quote removal (2.6.7). No expansion, no alias,
# no here-document. Operators (2.3, rules 2, 3 and 6) are tokens, so they
# count as arguments; a newline operator separates commands and is not an argument.
# A `$(`, `${` or backquote (2.3 rule 5) runs to its matching end inside one
# word and stays in it verbatim, since nothing is expanded.
OPERATORS = frozenset(["&", "&&", "(", ")", ";", ";;", "|", "||", "<", ">", ">|", "<<", ">>", "<&", ">&", "<>", "<<-"])
OPERATOR_START = frozenset("&();|<>")
BLANKS = frozenset(" \t")
DQUOTE_ESCAPES = frozenset('$`"\\\n')


def substitution_end(text, i):
    """2.3 rule 5: the index just after the `$(...)`, `${...}` or backquoted text that starts at `i`.

    Quotes and backslashes inside are honoured, `$(` and `${` nest; an
    unterminated one runs to the end of the input.
    """
    n = len(text)
    if text[i] == "`":
        j = i + 1
        while j < n and text[j] != "`":
            j += 2 if text[j] == "\\" else 1
        return min(j + 1, n)
    close = ")" if text[i + 1] == "(" else "}"
    opener = text[i + 1]
    depth, j = 1, i + 2
    while j < n:
        c = text[j]
        if c == "\\":
            j += 2
            continue
        if c == "'":
            end = text.find("'", j + 1)
            j = n if end < 0 else end + 1
            continue
        if c == '"':
            j += 1
            while j < n and text[j] != '"':
                if text[j] == "\\":
                    j += 2
                elif text[j] == "`" or (text[j] == "$" and j + 1 < n and text[j + 1] in "({"):
                    j = substitution_end(text, j)
                else:
                    j += 1
            j += 1
            continue
        if c == "`" or (c == "$" and j + 1 < n and text[j + 1] in "({"):
            j = substitution_end(text, j)
            continue
        if c == opener:
            depth += 1
        elif c == close:
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1
    return n


def starts_substitution(text, i):
    return text[i] == "`" or (text[i] == "$" and i + 1 < len(text) and text[i + 1] in "({")


def split_words(text):
    """Split `text` into arguments (AUD-11), quote removal applied."""
    tokens = []
    word = None  # characters of the current word after quote removal, or None outside a word
    operator = None
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if operator is not None:
            if operator + c in OPERATORS:  # 2.3 rule 2
                operator += c
                i += 1
                continue
            tokens.append(operator)  # 2.3 rule 3; c is processed again
            operator = None
            continue
        if c == "\\":  # 2.2.1
            if i + 1 < n and text[i + 1] == "\n":  # line continuation, removed whole
                i += 2
                continue
            word = [] if word is None else word
            if i + 1 < n:
                word.append(text[i + 1])
                i += 2
            else:  # nothing follows: the backslash stays as it is
                word.append(c)
                i += 1
            continue
        if c == "'":  # 2.2.2; an unterminated quote runs to the end of the input
            end = text.find("'", i + 1)
            end = n if end < 0 else end
            word = [] if word is None else word
            word.append(text[i + 1:end])
            i = end + 1
            continue
        if c == '"':  # 2.2.3; an unterminated quote runs to the end of the input
            word = [] if word is None else word
            j = i + 1
            while j < n and text[j] != '"':
                if starts_substitution(text, j):  # 2.3 rule 5, also inside double quotes
                    end = substitution_end(text, j)
                    word.append(text[j:end])
                    j = end
                    continue
                if text[j] == "\\" and j + 1 < n and text[j + 1] in DQUOTE_ESCAPES:
                    if text[j + 1] != "\n":
                        word.append(text[j + 1])
                    j += 2
                    continue
                word.append(text[j])
                j += 1
            i = j + 1
            continue
        if starts_substitution(text, i):  # 2.3 rule 5
            end = substitution_end(text, i)
            word = [] if word is None else word
            word.append(text[i:end])
            i = end
            continue
        if c == "\n":  # the newline operator: delimits, is not an argument
            if word is not None:
                tokens.append("".join(word))
                word = None
            i += 1
            continue
        if c in OPERATOR_START:  # 2.3 rule 6
            if word is not None:
                tokens.append("".join(word))
                word = None
            operator = c
            i += 1
            continue
        if c in BLANKS:  # 2.3 rule 7
            if word is not None:
                tokens.append("".join(word))
                word = None
            i += 1
            continue
        if word is None and c == "#":  # 2.3 rule 9: a comment, up to the newline
            end = text.find("\n", i)
            i = n if end < 0 else end
            continue
        word = [] if word is None else word  # 2.3 rules 8 and 10
        word.append(c)
        i += 1
    if operator is not None:
        tokens.append(operator)
    if word is not None:
        tokens.append("".join(word))
    return tokens


# ---------------------------------------------------------------- git


def git_env():
    # AUD-38: no setting of the environment points git at another repository
    # or makes it write traces, and git fetches no missing object of a partial
    # clone (GIT_NO_LAZY_FETCH, git 2.44+): fetch nothing; git's messages in
    # English (AUD-40).
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(
        GIT_NO_LAZY_FETCH="1",
        GIT_OPTIONAL_LOCKS="0",
        GIT_TERMINAL_PROMPT="0",
        GIT_TRACE="0",
        GIT_TRACE2="0",
        GIT_TRACE2_EVENT="0",
        GIT_TRACE2_PERF="0",
        LC_ALL="C",
        LANGUAGE="C",
    )
    return env


def run_git(args, cwd, alone=False):
    """Run git; return (status, stdout bytes, stderr text). None status: git could not be started.
    `alone`: git looks for the repository in `cwd` only, never in a folder that holds it."""
    # AUD-38: only commands that change no file and run no other program: no
    # fsmonitor, no untracked cache written, no pager; no filter or hook runs
    # for rev-parse or ls-files.
    cmd = [
        "git", "--no-pager",
        "-c", "core.fsmonitor=false",
        "-c", "core.untrackedCache=false",
    ] + args
    try:
        env = git_env()
        if alone:
            env["GIT_CEILING_DIRECTORIES"] = os.path.dirname(os.path.realpath(cwd))
        proc = subprocess.run(cmd, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError:
        return None, b"", ""
    return proc.returncode, proc.stdout, proc.stderr.decode("utf-8", "surrogateescape")


def git_error(stderr):
    lines = stderr.splitlines()
    return lines[0] if lines else ""


# ---------------------------------------------------------------- spec files


def excluded(path):
    """R62: whether `path` (relative, '/' separators) is certainly not specification."""
    parts = path.split("/")
    if any(part.startswith(".") for part in parts):
        return True
    name = parts[-1].casefold()
    return name in AGENT_FILES or (len(parts) == 1 and name in ROOT_COMMUNITY_FILES)


# A path that is not in the working tree: no such name, a name too long, or a
# symbolic link that loops and so resolves to nothing (AUD-11, AUD-40).
ABSENT = frozenset([errno.ENOENT, errno.ENOTDIR, errno.ENAMETOOLONG, errno.ELOOP])
# The errors of a path that is there but cannot be searched or read (AUD-12, AUD-40, AUD-42).
DENIED = frozenset([errno.EACCES, errno.EPERM])


def path_exists(path):
    """AUD-40: whether `path` exists; a path that cannot be searched exists, any other error does not."""
    try:
        os.stat(path)
    except OSError as exc:
        return exc.errno in DENIED
    return True


def searchable(folder):
    """The nearest folder at or above `folder` that the process can enter (AUD-11, AUD-40)."""
    while not os.access(folder, os.X_OK) and os.path.dirname(folder) != folder:
        folder = os.path.dirname(folder)
    return folder


def read_bytes(path):
    with open(path, "rb") as f:
        return f.read()


# git's warning for a folder it cannot open while it lists the files not yet committed (dir.c).
CANNOT_OPEN = re.compile(r"^warning: could not open directory '(.*)': [^:]*$")


def unsearchable_folders(stderr):
    """AUD-42: the folders that git could not search, each as its path followed by `/`, the root of
    the repository (which git names `.` or ``) as `./`; a folder that R62 excludes holds no spec file
    and is left out."""
    folders = set()
    for line in stderr.splitlines():
        m = CANNOT_OPEN.match(line)
        if m:
            folder = m.group(1).rstrip("/")
            if folder in ("", "."):
                folders.add("./")  # the root: never an R62 dot-folder
            elif not excluded(folder + "/x.md"):
                folders.add(folder + "/")
    return sorted(folders)


def readdir_names(root, rel, cache):
    """The names that the folder of `rel` lists, or an empty set when it cannot be listed."""
    folder = os.path.dirname(rel)
    if folder not in cache:
        try:
            cache[folder] = set(os.listdir(os.path.join(root, folder)))
        except OSError:
            cache[folder] = set()
    return cache[folder]


def list_spec_files(root, guideline_bytes):
    """AUD-12, AUD-42: (spec files in code point order, unreadable ones, {path: bytes}, folders git could not search)."""
    status, out, err = run_git(["ls-files", "-z", "--cached", "--others", "--exclude-standard"], root)
    if status is None:
        raise Refusal("specs-management:audit: git failed: git could not be started")
    if status != 0:
        raise Refusal("specs-management:audit: git failed: " + git_error(err))
    unsearchable = unsearchable_folders(err)
    names = sorted(set(os.fsdecode(p) for p in out.split(b"\0") if p))
    spec, unreadable, contents = [], [], {}
    folders = {}
    # AUD-12: one file of the working tree is one spec file, also when git's index holds two
    # spellings of its name that a case-insensitive file system maps to it: by identity and name.
    seen, listed = {}, {}

    def real_folders(rel):
        # AUD-12, AUD-38: a path is in the working tree only when every folder on
        # it is a real folder, not a symbolic link: git sees docs/a.md as deleted
        # when docs is a link, and its bytes would come from outside the repository.
        # True, False, or None when a folder cannot be searched (AUD-42: unreadable).
        parts = rel.split("/")[:-1]
        for depth in range(1, len(parts) + 1):
            folder = "/".join(parts[:depth])
            if folder not in folders:
                try:
                    folders[folder] = stat.S_ISDIR(os.lstat(os.path.join(root, folder)).st_mode)
                except OSError as exc:
                    folders[folder] = False if exc.errno in ABSENT else None
            if not folders[folder]:
                return folders[folder]
        return True

    for rel in names:
        # AUD-12: name ends in `.md` (case-sensitive), path not excluded by R62
        if not rel.endswith(".md") or rel.endswith("/") or excluded(rel):
            continue
        real = real_folders(rel)
        if real is False:
            continue
        full = os.path.join(root, rel)
        try:
            if real is None:
                raise PermissionError(errno.EACCES, "folder cannot be searched")
            st = os.lstat(full)  # AUD-12: in the working tree
        except OSError as exc:
            if exc.errno in ABSENT:
                continue
            # AUD-12, AUD-42: in the working tree, as git lists it, but its folder
            # cannot be searched: a spec file that cannot be read.
            spec.append(rel)
            unreadable.append(rel)
            continue
        if not stat.S_ISREG(st.st_mode):  # AUD-12: a regular file, not a symbolic link
            continue
        key = (st.st_dev, st.st_ino, fold(rel))
        if key in seen:
            # Keep the spelling the folder lists, or else the first in code point order.
            first = seen[key]
            if rel.rsplit("/", 1)[-1] in readdir_names(root, rel, listed) and \
                    first.rsplit("/", 1)[-1] not in readdir_names(root, first, listed):
                seen[key] = rel
                if first in contents:
                    contents[rel] = contents.pop(first)
                spec[:] = [rel if p == first else p for p in spec]
                unreadable[:] = [rel if p == first else p for p in unreadable]
            continue
        seen[key] = rel
        try:
            data = read_bytes(full)
        except OSError:
            spec.append(rel)
            unreadable.append(rel)
            continue
        if data == guideline_bytes:  # AUD-12: its bytes differ from the guideline's
            continue
        spec.append(rel)
        contents[rel] = data
    spec.sort()
    unreadable.sort()
    return spec, unreadable, contents, unsearchable


def select(root, spec_files, resolved):
    """AUD-13: the selected files for the argument `resolved` (symbolic links resolved)."""
    try:
        os.stat(resolved)
    except OSError as exc:
        if exc.errno in DENIED:
            # AUD-13, AUD-42: a path below a folder that cannot be searched cannot be told
            # file or folder; it selects the spec files git lists at it or under it, which
            # are then listed as could not be read.
            rel = rel_by_identity(root, resolved)
            if rel is None:
                rel = os.path.relpath(resolved, root).replace(os.sep, "/")
            return [p for p in spec_files if p == rel or p.startswith(rel + "/")]
    if os.path.isdir(resolved):
        # Every spec file under the folder; the root of the repository selects all.
        # Folders compare by identity, so a case-insensitive file system matches too.
        target = os.stat(resolved)
        key = (target.st_dev, target.st_ino)
        cache = {}

        def under(rel):
            parts = rel.split("/")[:-1]
            for depth in range(len(parts), -1, -1):
                folder = os.path.join(root, *parts[:depth]) if depth else root
                if folder not in cache:
                    try:
                        st = os.stat(folder)
                        cache[folder] = (st.st_dev, st.st_ino)
                    except OSError:
                        cache[folder] = None
                if cache[folder] == key:
                    return True
            return False

        return [rel for rel in spec_files if under(rel)]
    # The file's place under the root, found by identity: a folder above the root
    # may be spelled in another case or Unicode form than git's --show-toplevel.
    rel = rel_by_identity(root, resolved)
    if rel is None:
        rel = os.path.relpath(resolved, root).replace(os.sep, "/")
    if rel in spec_files:
        return [rel]
    # A case-insensitive file system: the same file under another spelling. The
    # names must match case-insensitively too, so that a hard link (an ignored or
    # R62-excluded name for a spec file's bytes) selects nothing (AUD-13).
    try:
        st = os.stat(resolved)
    except OSError:
        return []
    for cand in spec_files:
        if fold(cand) != fold(rel):
            continue
        try:
            other = os.lstat(os.path.join(root, cand))
        except OSError:
            continue
        if (other.st_dev, other.st_ino) == (st.st_dev, st.st_ino):
            return [cand]
    return []


def identity(path):
    """(st_dev, st_ino) of `path`, or None when it cannot be reached."""
    try:
        st = os.stat(path)
    except OSError:
        return None
    return st.st_dev, st.st_ino


def inside(path, folder):
    """Whether `path` is `folder` or under it, by identity, so that another case
    or Unicode form of a folder's name on a case-insensitive file system matches."""
    key = identity(folder)
    if key is None:
        return False
    while True:
        if identity(path) == key:
            return True
        parent = os.path.dirname(path)
        if parent == path:
            return False
        path = parent


def rel_by_identity(root, path):
    """`path` relative to `root`, with `/`, found by walking up to the folder that is `root`; None if not under it."""
    key = identity(root)
    parts = []
    while key is not None:
        if identity(path) == key:
            return "/".join(reversed(parts))
        parent = os.path.dirname(path)
        if parent == path:
            return None
        parts.append(os.path.basename(path))
        path = parent
    return None


def fold(path):
    return unicodedata.normalize("NFC", unicodedata.normalize("NFC", path).casefold())


FENCE = re.compile(r"^[ \t]*(`{3,}|~{3,})(.*)$")
LIST_ITEM = re.compile(r"^ {0,3}([-+*]|\d{1,9}[.)])([ \t]|$)")
BACKTICKS = re.compile(r"`+")
WORD = re.compile(r"[^\W_]+")
# A table's delimiter row (GitHub Flavored Markdown).
TABLE_DELIMITER = re.compile(r"^ {0,3}\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*$")
# AUD-36: scripts written without spaces between words (complete list): Thai, Lao, Tibetan,
# Myanmar, Khmer, Hiragana, Katakana, Han (CJK blocks, compatibility ideographs and the
# supplementary planes 2 and 3).
UNSPACED = re.compile("[\u0e00-\u0fff\u1000-\u109f\u1780-\u17ff\u19e0-\u19ff\ua9e0-\ua9ff\uaa60-\uaa7f"
                      "\u3040-\u30ff\u31f0-\u31ff\u3400-\u4dbf\u4e00-\u9fff"
                      "\uf900-\ufaff\uff66-\uff9f\U00020000-\U0003ffff]")
ATX_HEADING = re.compile(r"^ {0,3}#{1,6}([ \t]|$)")
# A setext heading's underline and a thematic break (CommonMark), which end a paragraph.
SETEXT_UNDERLINE = re.compile(r"^ {0,3}(=+|-+)[ \t]*$")
THEMATIC_BREAK = re.compile(r"^ {0,3}([-*_])([ \t]*\1){2,}[ \t]*$")
# The markers of a block quote, each `>` with one optional space after it (CommonMark).
QUOTE_MARKER = re.compile(r" {0,3}> ?")


def unquote(line, limit=None):
    """The line without its block-quote markers, at most `limit` of them, and how many there were."""
    depth = 0
    m = QUOTE_MARKER.match(line)
    while m and (limit is None or depth < limit):
        line, depth = line[m.end():], depth + 1
        m = QUOTE_MARKER.match(line)
    return line, depth


UTF16_BOMS = (b"\xff\xfe", b"\xfe\xff")


def as_utf8(data):
    """Term "Line": a file that starts with a UTF-16 byte order mark is read as its text decoded from
    UTF-16 in the byte order of the mark, without the mark, each unpaired surrogate as U+FFFD, and
    encoded in UTF-8, as the Read tool shows it; any other file as it is."""
    if data[:2] in UTF16_BOMS:
        return data.decode("utf-16", "replace").encode("utf-8")
    return data


def indent_width(line):
    """Columns of leading blanks, a tab advancing to the next multiple of 4 (CommonMark)."""
    width = 0
    for ch in line:
        if ch == " ":
            width += 1
        elif ch == "\t":
            width += 4 - width % 4
        else:
            break
    return width


def count_words(data):
    """AUD-36: the words of a file outside code spans and literal blocks.

    Literal blocks are fenced blocks and indented code blocks (CommonMark: lines
    indented 4 columns or more that start after a blank line, a heading or a
    fenced block, outside a list, where such a line continues a list item
    instead). A fence opened inside a list item ends with the item, at the first
    line indented less than the fence.
    """
    text = as_utf8(data).decode("utf-8", "replace")  # term "Line": a UTF-16 file is read as its text
    if text.startswith("\ufeff"):  # term "Line": a byte order mark is not part of line 1
        text = text[1:]
    # AUD-36: the kept text, as the blocks of CommonMark in which a code span is matched: a
    # code span cannot cross a blank line, a heading, a thematic break, a list item's start,
    # a block quote's start or a table cell.
    blocks, fence, fence_indent = [[]], None, 0
    indented = in_list = in_table = False
    code_may_start = True  # an indented code block may start on line 1
    depth = code_depth = 0  # block-quote depth of the line before, and of the open literal block

    def own_block(*parts):
        if blocks[-1]:
            blocks.append([])
        for part in parts:
            blocks[-1].append(part)
            blocks.append([])

    for line in text.split("\n"):
        line = line[:-1] if line.endswith("\r") else line  # a CRLF line ending (term "Line")
        # AUD-36: a block quote's content is read without its markers; a deeper quote starts a block,
        # and a literal block opened in a quote ends with the quote.
        raw = line
        # Inside a literal block, only the markers of its own quote are left out.
        line, quoted = unquote(raw, code_depth if fence is not None or indented else None)
        if (fence is not None or indented) and quoted < code_depth:
            fence, indented = None, False
            line, quoted = unquote(raw)
        if quoted > depth:
            own_block()
        depth = quoted
        blank = not line.strip()
        width = indent_width(line)
        if fence is not None:
            m = FENCE.match(line)
            # A closing fence: the same character, at least as long, nothing after it, indented
            # at most 3 columns, relative to the list item's content in a list (CommonMark).
            if (m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) and not m.group(2).strip()
                    and width <= fence_indent + 3):
                fence = None
                code_may_start = True
                continue
            if not (fence_indent and not blank and width < fence_indent):
                continue
            # A line indented less than a list item's fence ends the item, and the fence with it.
            fence = None
            if width <= 1:
                in_list = False
        if indented:
            if blank or width >= 4:
                continue  # AUD-36: inside an indented code block
            indented = False
        if blank:
            code_may_start = True
            in_table = False
            own_block()
            continue
        m = FENCE.match(line)
        # A backtick fence's info string cannot hold a backtick: such a line is a code span (CommonMark).
        if m and (width <= 3 or in_list) and not (m.group(1)[0] == "`" and "`" in m.group(2)):
            fence = m.group(1)
            fence_indent = width if in_list else 0
            code_depth = quoted
            code_may_start = False
            in_table = False
            continue
        if width >= 4 and code_may_start and not in_list:
            indented = True  # AUD-36: an indented code block is a literal block
            code_depth = quoted
            continue
        # A thematic break, or a setext underline after a paragraph line, ends the block (CommonMark).
        if THEMATIC_BREAK.match(line) or (SETEXT_UNDERLINE.match(line) and blocks[-1] and not in_table):
            if width <= 1 and THEMATIC_BREAK.match(line):
                in_list = False
            code_may_start, in_table = True, False
            own_block()
            continue
        heading = bool(ATX_HEADING.match(line))
        item = bool(LIST_ITEM.match(line))
        if item:
            in_list = True
        elif width <= 1 and (code_may_start or heading):
            in_list = False
        code_may_start = heading
        if TABLE_DELIMITER.match(line) and "|" in line and blocks[-1] and "|" in blocks[-1][-1]:
            # A table: its header row, the line before, and each row after are split into cells.
            header = blocks[-1].pop()
            own_block(*table_cells(header))
            in_table = True
            continue
        if in_table and not heading and not item:
            own_block(*table_cells(line))
            continue
        in_table = False
        if heading:
            own_block(line)
        elif item:
            own_block()
            blocks[-1].append(line)
        else:
            blocks[-1].append(line)
    # AUD-36: code spans, matched in each block.
    prose = " ".join(strip_code_spans("\n".join(b)) for b in blocks if b)
    # AUD-36: each letter of an unspaced script is one word; other scripts split on non-letters.
    unspaced = sum(1 for ch in UNSPACED.findall(prose) if ch.isalpha())
    prose = UNSPACED.sub(" ", prose)
    # AUD-36: a combining mark (vowel sign, virama, harakat, niqqud) belongs to its word.
    if not prose.isascii():
        prose = "".join(ch for ch in prose if not unicodedata.category(ch).startswith("M"))
    return unspaced + sum(1 for w in WORD.findall(prose) if any(ch.isalpha() for ch in w))


def table_cells(row):
    """The cells of a table row, split at each `|` that no backslash escapes (GitHub Flavored Markdown)."""
    return [c for c in re.split(r"(?<!\\)\|", row) if c.strip()]


def strip_code_spans(text):
    """The text of one paragraph without its code spans (CommonMark): a run of n
    backticks opens a span that the next run of exactly n backticks closes; a
    backslash-escaped backtick and a run that is never closed are literal."""
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c == "\\" and i + 1 < n:
            out.append(text[i:i + 2])
            i += 2
            continue
        if c != "`":
            out.append(c)
            i += 1
            continue
        run = BACKTICKS.match(text, i).group(0)
        close = None
        for m in BACKTICKS.finditer(text, i + len(run)):
            if len(m.group(0)) == len(run):
                close = m
                break
        if close is None:
            out.append(run)
            i += len(run)
            continue
        out.append(" ")
        i = close.end()
    return "".join(out)


# git's message when no folder at or above the path is a repository (setup.c).
NOT_IN_REPOSITORY = re.compile(r"not a git repository \(or any (of the parent directories|parent up to mount point)")


def prepare(argv):
    if argv[:1] == ["--raw"] and len(argv) == 2:
        args = split_words(argv[1])
    elif argv == ["--raw-stdin"]:
        args = split_words(sys.stdin.buffer.read().decode("utf-8", "surrogateescape"))
    else:
        args = argv[1:] if argv[:1] == ["--"] else argv

    # AUD-40, in this order.
    if len(args) > 1:
        raise Refusal("specs-management:audit: expected at most one path, got %d arguments" % len(args))
    try:
        guideline_bytes = read_bytes(GUIDELINE)
    except OSError:
        raise Refusal("specs-management:audit: writing-specs.md is missing from the plugin specs-management")
    if args:
        shown = args[0]
        if not shown:
            raise Refusal("specs-management:audit: %s: no such file or folder" % shown)
        if os.path.isabs(shown):
            full = shown  # needs no working directory, which may have been deleted
        else:
            try:
                full = os.path.join(os.getcwd(), shown)
            except OSError:
                raise Refusal("specs-management:audit: %s: no such file or folder" % shown)
        if not path_exists(full):
            raise Refusal("specs-management:audit: %s: no such file or folder" % shown)
    else:
        try:
            full = os.getcwd()
        except OSError:
            raise Refusal("specs-management:audit: %s: no such file or folder" % os.environ.get("PWD", "."))
        shown = full
    # AUD-11: the argument with its symbolic links resolved.
    resolved = os.path.realpath(full)
    folder = resolved if os.path.isdir(resolved) else os.path.dirname(resolved)
    # AUD-40: git runs in a folder it can enter; a folder that cannot be searched
    # belongs to the repository of the nearest folder above it that can.
    folder = searchable(folder)
    # AUD-11, AUD-13, AUD-40: a path inside a git directory (.git, .git/worktrees/<name>,
    # .git/modules/<name> or a file under them) is inside the repository whose working
    # tree holds the outermost such directory; it selects no spec file. This is
    # checked before --show-toplevel, which a submodule's git directory answers
    # with the submodule's working tree (core.worktree), and by the git directory's
    # path, since --is-inside-git-dir answers false there for the same reason.
    for _ in range(64):
        gstatus, gout, _ = run_git(["rev-parse", "--absolute-git-dir"], folder)
        if gstatus != 0 or not gout.strip():
            break
        gitdir = os.path.realpath(os.fsdecode(gout.rstrip(b"\n")))
        # By identity, so that `.GIT` on a case-insensitive file system is the git directory too.
        if not inside(folder, gitdir):
            break
        parent = os.path.dirname(gitdir)
        if parent == gitdir:
            break
        folder = parent
    # AUD-11: the innermost git repository, a submodule included.
    status, out, err = run_git(["rev-parse", "--show-toplevel"], folder)
    if status is None:
        raise Refusal("specs-management:audit: git failed: git could not be started")
    if status != 0:
        # Only git's discovery message: a broken .git file ("not a git repository: <gitdir>")
        # is inside the working tree of the repository around it, so git failed.
        if NOT_IN_REPOSITORY.search(err):
            raise Refusal("specs-management:audit: %s: not inside a git repository" % shown)
        raise Refusal("specs-management:audit: git failed: " + git_error(err))
    top = os.fsdecode(out.rstrip(b"\n"))
    if not top:
        raise Refusal("specs-management:audit: %s: not inside a git repository" % shown)
    root = os.path.realpath(top)

    spec_files, unreadable, contents, unsearchable = list_spec_files(root, guideline_bytes)
    # AUD-13: without argument, every spec file, whatever the working directory.
    selected = select(root, spec_files, resolved) if args else list(spec_files)
    if not selected:
        raise Refusal("specs-management:audit: %s: no spec file found" % shown)
    n = len(spec_files)
    link_reports, links_not_checked = check_links(root, selected, contents)
    return {
        "repo_root": root,
        "guideline": GUIDELINE,
        "spec_files": spec_files,
        "selected": selected,
        "unreadable": unreadable,
        "unsearchable": unsearchable,
        "n": n,
        "s": len(selected),
        # AUD-23, AUD-24: the threshold counts spec files, not selected files.
        "mode": "workflow" if n > 3 else "session",
        "word_counts": {p: count_words(contents[p]) for p in spec_files if p in contents},
        # AUD-56 to AUD-59: the link reports, or the reason the check was skipped.
        "link_reports": link_reports,
        "links_not_checked": links_not_checked,
    }


# ---------------------------------------------------------------- links between layers


class GitFailed(Exception):
    """A git command of the check of AUD-56 failed; the message is <error> of AUD-40."""


def unborn(repo):
    """Whether HEAD names a branch that does not exist yet."""
    status, out, err = run_git(["symbolic-ref", "-q", "HEAD"], repo, alone=True)
    if status != 0 or err.strip():
        return False
    ref = out.strip().decode("utf-8", "surrogateescape")
    status, out, err = run_git(["for-each-ref", "--format=%(refname)", ref], repo, alone=True)
    return status == 0 and not out.strip() and not err.strip()


def head_tree(repo):
    """AUD-55: the paths of the tree of the commit HEAD of `repo`, with the folders that hold them
    (term Exists); no paths when HEAD has no commit yet. Reads no file's content. Git reads `repo` only:
    when its .git is no repository, git fails, and never reads the tree of a repository that holds `repo`."""
    status, out, err = run_git(["rev-parse", "-q", "--verify", "HEAD^{commit}"], repo, alone=True)
    if status is None:
        raise GitFailed("git could not be started")
    if status == 1 and not out.strip() and not err.strip():
        if unborn(repo):
            return set()  # HEAD names no commit yet: an empty tree
        # A branch that names a missing object is a failure, never an empty tree (AUD-59).
        status, out, err = run_git(["rev-parse", "--verify", "HEAD^{commit}"], repo, alone=True)
        if status is None:
            raise GitFailed("git could not be started")
        raise GitFailed(git_error(err) or "HEAD names no commit")
    if status != 0:
        raise GitFailed(git_error(err))
    commit = out.strip().decode("ascii", "replace")
    status, out, err = run_git(["ls-tree", "-r", "-z", "--name-only", "--full-tree", commit], repo, alone=True)
    if status is None:
        raise GitFailed("git could not be started")
    if status != 0:
        raise GitFailed(git_error(err))
    return layers.tree_paths(os.fsdecode(p) for p in out.split(b"\0") if p)


NO_REMOTE = re.compile(r"^(?:error|fatal): No such remote '")  # fatal before git 2.30


def check_links(root, selected, contents):
    """AUD-54 to AUD-59: (the link reports, None), or ([], the reason) when the other layer cannot be
    found or read. Never refuses (AUD-46)."""
    def origin():
        status, out, err = run_git(["remote", "get-url", "origin"], root)
        if status is None:
            raise GitFailed("git could not be started")
        if status != 0:
            if NO_REMOTE.match(err):
                return None  # ORC-21: no remote origin, so no entry matches it
            raise GitFailed(git_error(err))
        return os.fsdecode(out)

    try:
        layer, repos = layers.locate(root, origin, own_at_repo=True)
        other = repos[1 - layer]
        trees = {layer: head_tree(root), 1 - layer: head_tree(str(other))}
    except GitFailed as exc:
        return [], "git failed: " + str(exc)
    except layers.NotFound as exc:
        i = exc.info
        return [], {
            "form": "project.json is missing or does not have the form of ORC-20",
            "not_listed": "this repository is not in project.json",
            "layer": "the repository is not of layer 0 or of layer 1",
            "no_layer": "project.json has no repository of layer %s" % i.get("layer"),
            "missing": "%s/%s is not at %s" % (i.get("owner"), i.get("name"), i.get("path")),
            "differs": "project.json differs from the copy of layer 1",
        }[exc.code]
    texts = {}
    for path in selected:
        if path in contents:  # AUD-56: the selected files the script could read
            data = as_utf8(contents[path])
            if data.startswith(BOM):
                data = data[len(BOM):]  # term Line: not part of line 1
            texts[path] = data.decode("utf-8", "surrogateescape")
    reports = []
    for r in layers.link_reports(layer, texts, trees):
        text = texts[r["path"]]
        report = {"path": r["path"], "line": r["line"], "layer": LINK_CASES[r["case"]][0], "case": r["case"],
                  "link": as_shown(text[r["open"]:r["end"]])}  # AUD-31: ill-formed UTF-8 as U+FFFD
        if r["case"] == 1:
            report["plain"] = as_shown(r["plain"])
        reports.append(report)
    reports.sort(key=lambda r: (r["path"], r["line"], r["link"]))  # AUD-34
    return reports, None


# ---------------------------------------------------------------- filter


BOM = b"\xef\xbb\xbf"


def file_lines(data):
    """Term "Line": split on LF, drop one CR before each LF, keep a last line without LF;
    a leading UTF-8 byte order mark is not part of line 1; no bytes are one empty line;
    a file with a UTF-16 byte order mark is read as its text."""
    data = as_utf8(data)
    if data.startswith(BOM):
        data = data[len(BOM):]
    parts = data.split(b"\n")
    lines = [p[:-1] if p.endswith(b"\r") else p for p in parts[:-1]]
    if parts[-1] or not lines:
        lines.append(parts[-1])
    return lines


def shown_line(raw):
    """A line as the file holds it, each maximal subpart of an ill-formed UTF-8 sequence read as
    one U+FFFD, as the Unicode Standard recommends and the Read tool shows it (AUD-31)."""
    return raw.decode("utf-8", "replace")


def as_shown(text):
    """Term "Quote": a quote line with its raw bytes (surrogate escapes) read as shown_line reads them."""
    try:
        return text.encode("utf-8", "surrogateescape").decode("utf-8", "replace")
    except UnicodeEncodeError:  # a lone surrogate that is not a raw byte
        return re.sub("[\ud800-\udfff]", "\ufffd", text)


def match_key(text):
    """Term "Quote": the form in which a quote line and its line are compared: each CR and each
    format character (Cf) left out, each space separator (Zs) read as U+0020, each maximal subpart
    of an ill-formed UTF-8 sequence read as one U+FFFD, in Normalization Form C."""
    text = as_shown(text)
    out = []
    for ch in text:
        if ch == "\r":
            continue
        if ch.isascii():
            out.append(ch)
            continue
        category = unicodedata.category(ch)
        if category == "Cf":
            continue
        out.append(" " if category == "Zs" else ch)
    return unicodedata.normalize("NFC", "".join(out))


def file_quote(lines, line, count):
    """The `count` lines of a file from `line` on, as the file holds them (AUD-31), or None."""
    if not is_int(line) or line < 1 or count < 1 or line - 1 + count > len(lines):
        return None
    return [shown_line(x) for x in lines[line - 1:line - 1 + count]]


def quote_matches(lines, line, quote):
    """Term "Quote", AUD-29 step 2: whether `quote` (a non-empty list) matches the lines from `line` on."""
    if lines is None or not quote:
        return False
    got = file_quote(lines, line, len(quote))
    return got is not None and [match_key(q) for q in quote] == [match_key(g) for g in got]


def check_of(sha256, path, line, rule, quote):
    """AUD-46: the digest that binds a finding kept by filter to the bytes filter read, so that render
    knows a finding as filter gave it, and only such a finding, after the file changed (AUD-41)."""
    return hashlib.sha256(json.dumps([sha256, path, line, rule, quote]).encode("utf-8", "surrogateescape")).hexdigest()


# A place "path:line"; the path may hold any character, a line feed included (AUD-31).
PLACE = re.compile(r"^(.+):([1-9][0-9]*)$", re.S)


def place_key(place):
    path, _, line = place.rpartition(":")
    if path and line.isdigit():
        return (path, int(line), place)
    return (place, 0, place)


def is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def is_str_list(value):
    return isinstance(value, list) and all(isinstance(x, str) for x in value)


def label(index, f):
    """How stderr names a finding: its position in the input and, when known, its place and rule."""
    name = "finding %d" % (index + 1)
    if isinstance(f, dict) and isinstance(f.get("path"), str) and is_int(f.get("line")):
        name += " (%s:%d %s)" % (esc(f["path"]), f["line"], f.get("rule"))
    return name


# The types of a finding (SKILL.md, section 3), exactly; anything else is refused.
TYPES = {
    "path": (lambda v: isinstance(v, str), "a string"),
    "line": (is_int, "an integer"),
    "rule": (lambda v: isinstance(v, str), "a string"),
    "quote": (is_str_list, "a list of strings, one per line"),
    "problem": (lambda v: isinstance(v, str), "a string"),
    "rewrite": (lambda v: isinstance(v, str), 'one string, its items already joined with " ¶ " (AUD-33)'),
    "see_also": (lambda v: is_str_list(v) and all(PLACE.match(x) for x in v), 'a list of "path:line" strings'),
    "verified": (lambda v: isinstance(v, bool), "true or false"),
    "sha256": (lambda v: isinstance(v, str), "the string filter gave"),
    "check": (lambda v: isinstance(v, str), "the string filter gave"),
    "rewrites": (lambda v: isinstance(v, list) and all(
        isinstance(x, dict) and set(x) == {"place", "rewrite"} and isinstance(x["place"], str)
        and PLACE.match(x["place"]) and isinstance(x["rewrite"], str) for x in v),
        'a list of {"place": "path:line", "rewrite": "..."}, as filter gave it'),
}


def check_types(index, f, keys, required):
    """Raise BadInput unless each of `keys` present in `f` has its type and each of `required` is present."""
    if not isinstance(f, dict):
        raise BadInput("%s: a finding must be a JSON object" % label(index, f))
    for key in required:
        if key not in f:
            raise BadInput("%s: %r is missing" % (label(index, f), key))
    for key in keys:
        if key in f:
            ok, what = TYPES[key]
            if not ok(f[key]):
                raise BadInput("%s: %r must be %s, got %s" % (label(index, f), key, what, json.dumps(f[key])[:200]))


PLACE_KEYS = ("path", "line", "quote", "rewrite")


def check_involved(index, f):
    """A finding across files (AUD-19): "involved", a list of {path, line, quote, rewrite}, instead of
    path, line, quote, rewrite and see_also; each place has the rewrite of its own text (AUD-19)."""
    for key in ("path", "line", "quote", "rewrite", "see_also"):
        if key in f:
            raise BadInput("%s: give either path, line, quote, rewrite and see_also, or involved, not both"
                           % label(index, f))
    places = f["involved"]
    if not isinstance(places, list) or not places:
        raise BadInput('%s: "involved" must be a non-empty list of {"path", "line", "quote", "rewrite"}' % label(index, f))
    for p in places:
        if not isinstance(p, dict) or set(p) != set(PLACE_KEYS):
            raise BadInput('%s: each place of "involved" must be {"path", "line", "quote", "rewrite"}, got %s'
                           % (label(index, f), json.dumps(p)[:200]))
        check_types(index, p, PLACE_KEYS, ())


class Files:
    """The bytes of the repository's files, each read once per command."""

    def __init__(self, root):
        self.root, self.data = root, {}

    def bytes(self, path):
        if path not in self.data:
            try:
                self.data[path] = read_bytes(os.path.join(self.root, path))
            except (OSError, ValueError):
                self.data[path] = None
        return self.data[path]

    def lines(self, path):
        data = self.bytes(path)
        return None if data is None else file_lines(data)

    def sha256(self, path):
        data = self.bytes(path)
        return None if data is None else hashlib.sha256(data).hexdigest()

    def has_line(self, path, line):
        lines = self.lines(path)
        return lines is not None and is_int(line) and 1 <= line <= len(lines)


def step2_reason(f, selected, files):
    """AUD-29 step 2, in the order the spec lists the conditions: the reason to drop `f`, or None."""
    if f["path"] not in selected:
        return "path is not a selected file"
    lines = files.lines(f["path"])
    if lines is None:
        return "file could not be read"
    if not 1 <= f["line"] <= len(lines):
        return "line does not exist"
    # Term "Quote": a byte order mark the Read tool shows, a format character (Cf) like it,
    # is left out on both sides.
    if not quote_matches(lines, f["line"], f["quote"]):
        return "quote differs from the file"
    if f["rule"] not in RULE_ORDER:
        return "rule is not a binding rule"
    return None


def place_across(f, eligible, spc14):
    """AUD-19: under the first eligible file in code point order of path, at its first involved line,
    with the rewrite of that place; every other involved place goes to See also. None when no involved
    line is in an eligible file (for SPC-14, an eligible file in `spc14`, where SPC-14 applies)."""
    places = f.pop("involved")
    mine = [p for p in places if p["path"] in eligible]
    if f["rule"] == "SPC-14":
        mine = [p for p in mine if p["path"] in spc14]  # AUD-19, AUD-17: only where SPC-14 applies
    if not mine:
        return None
    main = min(mine, key=lambda p: (p["path"], p["line"]))
    f["path"], f["line"], f["quote"], f["rewrite"] = main["path"], main["line"], main["quote"], main["rewrite"]
    others = [p for p in places if p is not main]
    f["see_also"] = ["%s:%d" % (p["path"], p["line"]) for p in others]
    # AUD-19: each other place whose text needs a change keeps its rewrite, for its `Rewrite at` line.
    f["rewrites"] = [{"place": "%s:%d" % (p["path"], p["line"]), "rewrite": p["rewrite"]}
                     for p in others if not unchanged(p["rewrite"], p["quote"])]
    return f


def unchanged(rewrite, quote):
    """Whether a place's rewrite is its quote unchanged, blanks and the item separator aside (AUD-19)."""
    def words(text):
        return match_key(" ".join(text.replace("¶", " ").split()))
    return words(rewrite) == words(" ".join(quote))


def own_see_also(f, is_line):
    """The places of a See also line: each a line of a spec file, each once, never the finding's
    own place, by path then line (AUD-34)."""
    own = "%s:%d" % (f["path"], f["line"])
    places = set()
    for p in f.get("see_also", []):
        path, line, _ = place_key(p)
        if p != own and is_line(path, line):
            places.add(p)
    return sorted(places, key=place_key)


def filter_findings(data):
    root = data.get("repo_root")
    selected = data.get("selected")
    findings = data.get("findings")
    audited = data.get("audited")
    spec_files = data.get("spec_files")
    spc14 = data.get("spc14_applies_to")
    if not isinstance(root, str) or not is_str_list(selected) or not isinstance(findings, list):
        raise BadInput("filter needs repo_root, selected and findings")
    if audited is not None and not is_str_list(audited):
        raise BadInput("audited must be a list of paths")
    if spec_files is not None and not is_str_list(spec_files):
        raise BadInput("spec_files must be a list of paths")
    if spc14 is not None and not is_str_list(spc14):
        raise BadInput("spc14_applies_to must be a list of paths")
    selected = set(selected)
    # AUD-35: a file not audited is listed under "Not audited" only, so no finding may go to it.
    eligible = selected if audited is None else selected & set(audited)
    # Refuse the whole input on a wrong type before dropping anything (SKILL.md, section 3).
    for i, f in enumerate(findings):
        if isinstance(f, dict) and "involved" in f:
            check_involved(i, f)
            check_types(i, f, ("rule", "problem"), ("rule", "problem"))
            if spec_files is None:
                raise BadInput("%s: a finding across files needs spec_files from prepare (AUD-19)" % label(i, f))
            if f["rule"] == "SPC-14" and spc14 is None:
                raise BadInput("%s: an SPC-14 finding across files needs spc14_applies_to, the selected files "
                               "where SPC-14 applies (AUD-19, AUD-17)" % label(i, f))
        else:
            check_types(i, f, ("path", "line", "rule", "quote", "problem", "rewrite", "see_also"),
                        ("path", "line", "rule", "quote", "problem", "rewrite"))
    spec = set(spec_files or [])
    files = Files(root)
    kept, dropped = [], []
    for position, original in enumerate(findings):
        f = json.loads(json.dumps(original))
        # AUD-20, AUD-30: only a finding across files (AUD-19) has See also places.
        f["see_also"] = []
        if "involved" in f:
            # AUD-19: an involved place counts only when its quote matches the lines of a spec file
            # from that place on; any other place is left out before the finding is placed.
            f["involved"] = [p for p in f["involved"]
                             if p["path"] in spec and quote_matches(files.lines(p["path"]), p["line"], p["quote"])]
            f = place_across(f, eligible, set(spc14 or []))
            if f is None:
                dropped.append({"index": position, "reason": "no involved line is in a selected file that was audited"})
                continue
        reason = step2_reason(f, selected, files)
        if reason is None and f["path"] not in eligible:
            reason = "file was not audited"
        if reason:
            dropped.append({"index": position, "reason": reason})
            continue
        # AUD-19, AUD-46: a See also place is a line of a spec file; any other is left out
        # here, so the merge, the skeptic and render all see the same places.
        f["see_also"] = own_see_also(f, lambda p, line: p in spec and files.has_line(p, line))
        if "rewrites" in f:
            seen = set()
            f["rewrites"] = sorted((r for r in f["rewrites"] if r["place"] in f["see_also"]
                                    and not (r["place"] in seen or seen.add(r["place"]))),
                                   key=lambda r: place_key(r["place"]))
        # AUD-31, term "Quote": the quote as the file holds it, which the match allowed to differ.
        f["quote"] = file_quote(files.lines(f["path"]), f["line"], len(f["quote"]))
        # AUD-46: render checks step 2 on the bytes this step read; `check` binds the finding to them.
        f["sha256"] = files.sha256(f["path"])
        f["check"] = check_of(f["sha256"], f["path"], f["line"], f["rule"], f["quote"])
        kept.append(f)
    # AUD-29 step 3: same path, line, rule, See also places and problem merge into the first one given.
    merged, index = [], set()
    for f in kept:
        key = (f["path"], f["line"], f["rule"], tuple(f["see_also"]), f["problem"])
        if key in index:
            continue
        index.add(key)
        merged.append(f)
    # AUD-29 step 4 in workflow mode: what each skeptic needs, aligned by index with
    # "findings" (SKILL.md 4b.4); the skeptic reads the quoted lines from the file and
    # judges the stated problem (AUD-23: "its one finding").
    verify = [{"path": f["path"], "line": f["line"], "lines": len(f["quote"]), "rule": f["rule"],
               "see_also": f["see_also"], "problem": f["problem"]} for f in merged]
    return {"findings": merged, "verify": verify, "dropped": dropped}


# ---------------------------------------------------------------- render


def questions_from_guideline():
    """AUD-15, AUD-22: the question texts, as the guideline words them, read at run time."""
    try:
        text = read_bytes(GUIDELINE).decode("utf-8")
    except (OSError, UnicodeDecodeError):
        raise BadInput("writing-specs.md is missing from the plugin specs-management")
    found = {}
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and re.fullmatch(r"SPC-Q\d+", cells[0]) and cells[0] not in found:
            found[cells[0]] = cells[1]
    missing = [q for q in QUESTION_IDS if q not in found]
    if missing:
        raise BadInput("the checklist of writing-specs.md lacks " + ", ".join(missing))
    return found


CONTROL = re.compile("[\x00-\x1f\x7f]")


def esc(path):
    """AUD-31: a path with each control character shown as \\u and its 4 lowercase hexadecimal digits."""
    return CONTROL.sub(lambda m: "\\u%04x" % ord(m.group(0)), path)


def cell(path):
    """AUD-31: a path in a table cell, each `|` shown as `\\|`."""
    return esc(path).replace("|", "\\|")


def one_line(text):
    return " ".join(str(text).split("\n")).replace("\r", " ")


# AUD-33: the separator of a rewrite's items, which no item holds.
ITEM_SEPARATOR = " ¶ "


def rewrite_line(value):
    # AUD-33: a rewrite is on one line, its items separated by " ¶ ".
    items = [x.strip() for x in value.replace("\r", "\n").split("\n")]
    return ITEM_SEPARATOR.join(x for x in items if x)


def plural(count, word):
    # AUD-32: `files` as `file`, `findings` as `finding`, when the number is 1.
    return word if count == 1 else word + "s"


LINK_KEYS = ("path", "line", "layer", "case", "link", "plain")


def check_link_reports(data, sel):
    """The link reports and the reason of AUD-59 that prepare gave, refused when they are not of the
    form prepare gives (AUD-56 to AUD-59)."""
    reports, reason = data["link_reports"], data["links_not_checked"]
    if reason is not None and (not isinstance(reason, str) or not LINKS_REASONS.match(reason)):
        raise BadInput("links_not_checked must be null or a reason of AUD-59, as prepare gives it")
    if not isinstance(reports, list):
        raise BadInput("link_reports must be a list")
    if reason is not None and reports:
        raise BadInput("link_reports must be empty when links_not_checked gives a reason (AUD-59)")
    for i, r in enumerate(reports):
        what = "link report %d" % i
        if not isinstance(r, dict) or not set(r) <= set(LINK_KEYS):
            raise BadInput("%s: must be an object with only %s" % (what, ", ".join(LINK_KEYS)))
        if not is_int(r.get("case")) or r["case"] not in LINK_CASES:
            raise BadInput("%s: case must be 1, 2 or 3" % what)
        if r.get("layer") != LINK_CASES[r["case"]][0]:
            raise BadInput("%s: case %d is of %s" % (what, r["case"], LINK_CASES[r["case"]][0]))
        if not isinstance(r.get("path"), str) or r["path"] not in sel:
            raise BadInput("%s: not a selected file" % what)
        if not is_int(r.get("line")) or r["line"] < 1:
            raise BadInput("%s: line must be an integer of at least 1" % what)
        if not isinstance(r.get("link"), str):
            raise BadInput("%s: link must be a string" % what)
        if (r["case"] == 1) != isinstance(r.get("plain"), str) or (r["case"] != 1 and "plain" in r):
            raise BadInput("%s: plain is a string in case 1 and absent otherwise" % what)
    return reports, reason


def render(data):
    for key in ("repo_root", "n", "s", "mode", "selected", "spec_files", "link_reports", "links_not_checked"):
        if key not in data:
            raise BadInput("render needs " + key)
    questions_text = questions_from_guideline()
    audited = sorted(set(data.get("audited") or []))
    findings = data.get("findings") or []
    not_audited = data.get("not_audited") or []
    unreadable = data.get("unreadable") or []
    unsearchable = data.get("unsearchable") or []
    n, s = int(data["n"]), int(data["s"])
    if not is_str_list(data["selected"]):
        raise BadInput("selected must be a list of paths")
    if not is_str_list(data["spec_files"]) or not is_str_list(unreadable) or not is_str_list(unsearchable):
        raise BadInput("spec_files, unreadable and unsearchable must be lists of paths")
    if any(not p.endswith("/") for p in unsearchable):
        raise BadInput("unsearchable must hold folders as prepare gives them, each ending in /")
    if not isinstance(data["repo_root"], str):
        raise BadInput("repo_root must be a string")
    sel = set(data["selected"])
    spec = set(data["spec_files"]) | sel
    link_reports, links_not_checked = check_link_reports(data, sel)

    files_out, passes = [], {}
    for entry in not_audited:
        if entry.get("pass") == "across" or entry.get("what") == ACROSS_LABEL:
            passes["across"] = (ACROSS_LABEL, ACROSS_REASON)
        elif entry.get("pass") == "readers" or entry.get("what") == READERS_LABEL:
            passes["readers"] = (READERS_LABEL, READERS_REASON)
        else:
            what, reason = entry["what"], entry["reason"]
            # AUD-42: a selected file with one of its three reasons, or another spec file that
            # could not be read; each file once (AUD-35).
            if reason not in FILE_REASONS:
                raise BadInput("not_audited %s: the reason must be one of %s" % (esc(str(what)), ", ".join(FILE_REASONS)))
            if reason == CONTEXT_REASON:
                if what in sel or what not in spec:
                    raise BadInput("not_audited %s: %r is for a spec file that is not selected" % (esc(str(what)), reason))
            elif what not in sel:
                raise BadInput("not_audited %s: not a selected file" % esc(str(what)))
            if what in {w for w, _ in files_out}:
                raise BadInput("not_audited %s: listed twice" % esc(str(what)))
            files_out.append((what, reason))
    # AUD-42: each spec file that prepare could not read, unless the input lists it already.
    listed = {w for w, _ in files_out}
    for path in unreadable:
        if path not in listed and path not in audited:
            files_out.append((path, "could not be read" if path in sel else CONTEXT_REASON))
    # AUD-35: each selected file under "Findings" or under "Not audited", never both.
    both = sorted(set(audited) & {w for w, _ in files_out})
    if both:
        raise BadInput("listed as audited and not audited: " + ", ".join(both))
    outside = sorted(set(audited) - sel)
    if outside:
        raise BadInput("audited but not selected: " + ", ".join(outside))
    missing = sorted(sel - set(audited) - {w for w, _ in files_out})
    if missing:
        raise BadInput("selected but neither audited nor not audited: " + ", ".join(missing))
    by_file = {path: [] for path in audited}
    if not isinstance(findings, list):
        raise BadInput("findings must be a list")
    files = Files(data["repo_root"])

    def place_ok(path, line):
        # AUD-19, AUD-46: a place of the report is a line of a spec file.
        return isinstance(path, str) and path in spec and files.has_line(path, line)

    for i, f in enumerate(findings):
        check_types(i, f, ("path", "line", "rule", "quote", "problem", "rewrite", "see_also", "rewrites", "verified",
                           "sha256", "check"),
                    ("path", "line", "rule", "quote", "problem", "rewrite"))
        if "involved" in f:
            raise BadInput("%s: an unplaced finding across files; give render filter's output" % label(i, f))
        f = dict(f)
        findings[i] = f
        # AUD-46: the report holds no finding that step 2 of AUD-29 drops, judged on the bytes
        # that step read. A finding that passes step 2 now shows the file's own lines (AUD-31).
        # Any other is kept only when its `check` proves it is a finding filter kept: then the
        # file changed after filter read it (AUD-41), and the finding is shown as filter gave it,
        # or only its quote or sha256 was mis-copied, and the file's own lines repair it.
        reason = step2_reason(f, sel, files)
        lines = files.lines(f["path"]) if f["path"] in sel else None
        here = None if lines is None else file_quote(lines, f["line"], len(f["quote"]))
        if reason is None:
            f["quote"] = here
        else:
            proven = None
            if f["path"] in sel and f["line"] >= 1 and f["quote"] and f["rule"] in RULE_ORDER and "check" in f:
                for sha in (f.get("sha256"), files.sha256(f["path"])):
                    for quote in (f["quote"], here):
                        if sha is not None and quote is not None and proven is None and \
                                check_of(sha, f["path"], f["line"], f["rule"], quote) == f["check"]:
                            proven = quote
            if proven is None:
                raise BadInput("%s: %s (AUD-29 step 2); copy filter's output findings verbatim, sha256 and check "
                               "included" % (label(i, f), reason))
            f["quote"] = proven
        if f["path"] not in by_file:
            raise BadInput("%s: a finding on a file that is not audited" % label(i, f))
        by_file[f["path"]].append(f)

    out = []
    # AUD-30, AUD-31: the summary line.
    out.append(
        "Audit of %s against writing-specs.md: %d of %d selected spec %s audited, %d %s. Spec set: %d spec %s. Mode: %s."
        % (esc(data["repo_root"]), len(audited), s, plural(s, "file"), len(findings), plural(len(findings), "finding"),
           n, plural(n, "file"), data["mode"])
    )
    out += ["", "## Findings", ""]
    if not audited:
        out.append("None.")
    for fi, path in enumerate(audited):  # AUD-34: file sections by path
        if fi:
            out.append("")  # AUD-33: one empty line before each repeated `### <path>`
        out += ["### " + esc(path), ""]
        # AUD-34: by rule, then by line, then by problem, then by rewrite, in code point order.
        items = sorted(by_file[path], key=lambda f: (RULE_ORDER[f["rule"]], int(f["line"]), f["problem"], f["rewrite"]))
        if not items:
            out.append("No findings.")
        for k, f in enumerate(items):
            if k:
                out.append("")  # AUD-33: one empty line between two findings of one file
            first = "- %s:%d · %s" % (esc(path), int(f["line"]), f["rule"])
            if f.get("verified") is False:
                first += " · not verified"  # AUD-43
            out.append(first)
            out += ["  > " + q.replace("\r", "\\u000d") for q in f["quote"]]  # AUD-31: a CR as \u000d
            out.append("  Problem: " + one_line(f["problem"]))
            out.append("  Rewrite: " + rewrite_line(f["rewrite"]))
            see = []
            for place in sorted(set(f.get("see_also", [])), key=place_key):
                p, line, _ = place_key(place)
                if place_ok(p, line):
                    see.append("%s:%d" % (esc(p), line))
            if see:
                out.append("  See also: " + ", ".join(see))  # AUD-19, AUD-31
            shown = set()
            for r in sorted(f.get("rewrites", []), key=lambda r: place_key(r["place"])):
                p, line, _ = place_key(r["place"])
                place = "%s:%d" % (esc(p), line)
                if place in see and place not in shown:  # AUD-19, AUD-34: in the order of See also
                    shown.add(place)
                    out.append("  Rewrite at %s: %s" % (place, rewrite_line(r["rewrite"])))
    out += ["", "## Links between layers", ""]
    if links_not_checked is not None:
        out.append("Not checked.")  # AUD-35: AUD-59 skipped the check
    elif not link_reports:
        out.append("None.")
    # AUD-34: by path, then by line, then by link.
    for k, r in enumerate(sorted(link_reports, key=lambda r: (r["path"], r["line"], r["link"]))):
        if k:
            out.append("")  # AUD-33: one empty line between two link reports
        _, problem, rewrite = LINK_CASES[r["case"]]
        out.append("- %s:%d · %s" % (esc(r["path"]), r["line"], r["layer"]))
        out.append("  Link: " + esc(r["link"]))  # AUD-31: on one line, each control character as a path shows it
        out.append("  Problem: " + problem)
        out.append("  Rewrite: " + (esc(r["plain"]) if rewrite is None else rewrite))
    out += ["", "## Conditional rules", "", "| Rule | Applies to | Why |", "|---|---|---|"]
    rows = {}
    for c in data.get("conditional") or []:
        rows.setdefault(c.get("rule"), c)
    for rule in CONDITIONAL_RULES:  # AUD-35: one row per rule, in the order of their numbers
        c = rows.get(rule, {})
        # AUD-31: <paths> are the selected files where the rule applies.
        paths = sorted(set(p for p in c.get("applies_to") or [] if p in sel))
        if rule == "SPC-13" and paths:
            paths = sorted(sel)  # AUD-17: SPC-13 holds for every selected file or for none
        why = one_line(c.get("why", "Not decided in this run.")).replace("|", "\\|")
        out.append("| %s | %s | %s |" % (rule, ", ".join(cell(p) for p in paths) if paths else "none", why))
    out += ["", "## Questions for the approver", ""]
    evidence = {}
    for q in data.get("questions") or []:
        evidence.setdefault(q.get("id"), {"items": [], "not_independent": False})
        evidence[q.get("id")]["items"].extend(q.get("evidence") or [])
        if q.get("not_independent"):
            evidence[q.get("id")]["not_independent"] = True
    for qid in QUESTION_IDS:
        out.append("- %s %s" % (qid, questions_text[qid]))
        ev = evidence.get(qid, {"items": [], "not_independent": False})
        items = []
        for e in ev["items"]:
            # AUD-46: every Evidence line cites its place as <path>:<line>, a line of a spec file.
            if isinstance(e, dict) and place_ok(e.get("path"), e.get("line")):
                items.append((e["path"], e["line"], one_line(e.get("text", ""))))
        if qid in ("SPC-Q2", "SPC-Q3") and "readers" in passes:
            items = []  # AUD-42: a reader failed
        if not items:
            out.append("  Evidence: none.")
        suffix = " (not independent)" if ev["not_independent"] else ""  # AUD-27
        for p, line, text in sorted(set(items)):  # AUD-34: by path, then line, then text
            out.append("  Evidence: %s:%d %s%s" % (esc(p), line, text, suffix))
    out += ["", "## Not audited", ""]
    # AUD-42: files and folders in code point order of path, then the pass across files, then the readers.
    na = sorted(set(files_out) | {(folder, FOLDER_REASON) for folder in unsearchable})
    for key in ("across", "readers"):
        if key in passes:
            na.append(passes[key])
    if links_not_checked is not None:
        na.append((LINKS_LABEL, esc(links_not_checked)))  # AUD-42: last, AUD-59
    if not na:
        out.append("None.")
    out += ["- %s — %s" % (esc(what), reason) for what, reason in na]
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- main


def read_json_stdin():
    raw = sys.stdin.buffer.read().decode("utf-8", "surrogateescape")
    try:
        # Control characters inside strings, a tab copied from a spec line included,
        # are accepted as they are (SKILL.md, section 1).
        data = json.loads(raw, strict=False)
    except ValueError as exc:
        raise BadInput("stdin is not JSON: %s" % exc)
    if not isinstance(data, dict):
        raise BadInput("stdin must hold a JSON object")
    return data


# AUD-30, AUD-38: the Bash tool shows an output of up to 30000 characters whole; keep each part below.
PART_SIZE = 25000


def part_number(rest):
    """The N of `--part N` (1 when left out)."""
    if not rest:
        return 1
    if len(rest) == 2 and rest[0] == "--part" and rest[1].isdigit() and int(rest[1]) >= 1:
        return int(rest[1])
    raise BadInput("expected nothing or --part N, got %s" % " ".join(rest))


def compact(value):
    """Compact JSON with each non-ASCII character as it is, so that the session sees and copies the
    text itself (SKILL.md, section 5); a lone surrogate, a byte of a name that is not UTF-8, keeps
    its \\u escape, so that it survives the copy."""
    text = json.dumps(value, separators=(",", ":"), ensure_ascii=False)
    return re.sub("[\ud800-\udfff]", lambda m: "\\u%04x" % ord(m.group(0)), text)


def run_of(text):
    """AUD-41: a digest of a command's whole output, carried by each of its parts, so that the session
    never joins the parts of two runs that read different bytes."""
    return hashlib.sha256(text.encode("utf-8", "surrogatepass")).hexdigest()[:12]


def check_part(number, count):
    if number > count:
        raise BadInput("--part %d: the output has %d parts" % (number, count))


def prepare_part(result, number):
    """prepare's output in parts of at most PART_SIZE characters (AUD-38): each part holds the single
    values and a slice of each list and of word_counts; the parts join list by list, in part order."""
    run = run_of(compact(result))
    keys = [k for k, v in result.items() if isinstance(v, (list, dict))]

    def build(number, count, chunk):
        part = {"part": number, "parts": count, "run": run}
        for k, v in result.items():
            if k in keys:
                mine = [x for key, x in chunk if key == k]
                part[k] = dict(mine) if isinstance(v, dict) else mine
            else:
                part[k] = v
        return part

    empty = len(compact(build(99999, 99999, []))) + 1
    parts, current, size = [], [], empty
    for k in keys:
        for x in (result[k].items() if isinstance(result[k], dict) else result[k]):
            length = len(compact(dict([x]) if isinstance(result[k], dict) else [x]))
            if current and size + length > PART_SIZE:
                parts.append(current)
                current, size = [], empty
            current.append((k, x))
            size += length
    parts.append(current)
    check_part(number, len(parts))
    return compact(build(number, len(parts), parts[number - 1])) + "\n"


def filter_part(result, number):
    """filter's output, split into parts of at most PART_SIZE characters each; the dropped entries
    come first, then the findings, each part holding its findings and their verify entries, aligned
    by index, and its slice of the dropped list. A finding too long for a part of its own comes in
    pieces: each piece part is a JSON line with `piece`, then a slice of that finding's JSON text;
    the slices, joined in order with nothing between them, are the finding (AUD-38)."""
    run = run_of(compact(result))
    findings, verify, dropped = result["findings"], result["verify"], result["dropped"]

    def header(items, drops, piece=None, verify_of=None):
        head = {"part": 99999, "parts": 99999, "run": run, "findings": [findings[i] for i in items],
                "verify": [verify[i] for i in items] if verify_of is None else verify_of,
                "dropped": [dropped[j] for j in drops]}
        if piece is not None:
            head["piece"] = piece
        return head

    def size(items, drops):
        return len(compact(header(items, drops))) + 1

    # each part: ("findings", [indices], [dropped indices]) or ("piece", index, number, of, text)
    parts, items, drops = [], [], []
    for j in range(len(dropped)):
        if drops and size(items, drops + [j]) > PART_SIZE:
            parts.append(("findings", items, drops))
            items, drops = [], []
        drops.append(j)
    for i in range(len(findings)):
        # A finding alone, without dropped entries, decides whether it comes in pieces.
        if size([i], []) > PART_SIZE:
            if items or drops:
                parts.append(("findings", items, drops))
                items, drops = [], []
            text = compact(findings[i])
            room = PART_SIZE - len(compact(header([], [], {"number": 99999, "of": 99999}, [verify[i]]))) - 2
            if room < 1000:
                raise BadInput("%s: its verify entry is too long for a part" % label(i, findings[i]))
            slices = [text[k:k + room] for k in range(0, len(text), room)]
            for k, chunk in enumerate(slices):
                parts.append(("piece", i, k + 1, len(slices), chunk))
            continue
        if (items or drops) and size(items + [i], drops) > PART_SIZE:
            parts.append(("findings", items, drops))
            items, drops = [], []
        items.append(i)
    if items or drops or not parts:
        parts.append(("findings", items, drops))
    # Every finding and every dropped entry is in exactly one part.
    assert sorted(i for p in parts for i in (p[1] if p[0] == "findings" else [p[1]] if p[2] == 1 else [])) == \
        list(range(len(findings)))
    assert [j for p in parts if p[0] == "findings" for j in p[2]] == list(range(len(dropped)))
    check_part(number, len(parts))
    chosen = parts[number - 1]
    if chosen[0] == "findings":
        head = header(chosen[1], chosen[2])
        head.update(part=number, parts=len(parts))
        return compact(head) + "\n"
    _, i, k, of, chunk = chosen
    head = header([], [], {"number": k, "of": of}, [verify[i]] if k == 1 else [])
    head.update(part=number, parts=len(parts))
    return compact(head) + "\n" + chunk + "\n"


def report_part(report, number):
    """The report whole when it fits in one part; otherwise part `number`, after the line
    `[part N of M, run R]`, which is not part of the report. Parts end at a line end, except where
    one line is longer than a part: the part that goes on with it says `continues the line`. The
    parts joined in order, with nothing between them, are the report."""
    if len(report) <= PART_SIZE and number == 1:
        return report
    run = run_of(report)
    room = PART_SIZE - 80
    parts, current = [], ""
    for line in report.splitlines(True):
        if current and len(current) + len(line) > room:
            parts.append(current)
            current = ""
        while len(current) + len(line) > room:
            parts.append(current + line[:room - len(current)])
            line = line[room - len(current):]
            current = ""
        current += line
    if current:
        parts.append(current)
    check_part(number, len(parts))
    goes_on = number > 1 and not parts[number - 2].endswith("\n")
    return "[part %d of %d, run %s%s]\n" % (number, len(parts), run, ", continues the line" if goes_on else "") + \
        parts[number - 1]


def write(text):
    sys.stdout.buffer.write(text.encode("utf-8", "surrogateescape"))
    sys.stdout.flush()


def main(argv):
    if not argv or argv[0] not in ("prepare", "filter", "render"):
        sys.stderr.write("usage: audit.py prepare [--part N] [arg] | prepare [--part N] --raw '<words>' | "
                         "prepare [--part N] --raw-stdin | filter [--part N] | render [--part N]\n")
        return 2
    command, rest = argv[0], argv[1:]
    try:
        if command == "prepare":
            number = 1
            if rest[:1] == ["--part"]:
                number, rest = part_number(rest[:2]), rest[2:]
            write(prepare_part(prepare(rest), number))
        elif command == "filter":
            number = part_number(rest)
            write(filter_part(filter_findings(read_json_stdin()), number))
        else:
            number = part_number(rest)
            write(report_part(render(read_json_stdin()), number))
    except Refusal as exc:
        write(str(exc) + "\n")  # AUD-40: only its message
        return 1
    except (BadInput, KeyError, TypeError, ValueError, AttributeError) as exc:
        sys.stderr.write("audit.py %s: %s\n" % (command, exc))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
