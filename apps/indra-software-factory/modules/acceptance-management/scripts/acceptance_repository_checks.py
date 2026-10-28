"""The checks of ACU-74, shared by every use case of this module that runs from the acceptance repository.

Spec: specs/module.md of acceptance-management, ACU-74 (The files of the
acceptance repository): before it reads anything else, the use case define
(ACU-58) and the use case plan (PLN-2) run these checks, with no model, in
this order (complete list); the first that fails ends the use case, which
writes nothing and says "acceptance-management:<use case>: <message>". Each
message binds byte for byte; this module returns it without the prefix, which
each use case adds.

API:

    run_checks(cwd, arguments) -> (context, message | None)
        Runs CHECKS in their order; `message` is that of the first check that
        fails, or None when every check passes.
    CHECKS
        The checks, in the order of ACU-74, one function per row. Each takes the
        context (a dict) and returns the bound message of its row when it
        fails, or None; when it passes it adds to the context what it found.
    locate(cwd) -> context
        Rows 2 and 3 only, for the commands that a use case runs after its
        checks passed; raises Refusal with the message of the row that fails.
    read_tree(data) -> list[dict]
        R23, R61: the active nodes of data/tree.jsonl, in its order; raises
        ValueError or UnicodeDecodeError when it is not valid (row 10).
    breaks_a_line(character) -> bool
        A control character (Unicode category Cc), a line separator or a
        paragraph separator: the characters that ACU-8 forbids in a title and
        PLN-5 in the name of an increment.
    heading_title(lines, an_id) -> str | None
        ACU-7, ACU-8: the title of the heading "# <an_id> <title>" on the first
        of `lines`, or None when the heading does not meet ACU-7 or ACU-8.
    git(cwd, *args, binary=False), out(cwd, *args), show(cwd, revision, path),
    ls_tree(cwd, revision, *paths), default_branch(cwd)
        The git helpers that the checks use, for the use cases too.

The context starts as {"cwd", "arguments"}, and the checks add, in this order:
"root", "project_bytes", "project", "repositories" (the entries of
project.json), "acceptance_repository", "project_folder", "norms_repository",
"norms_repository_path", "specs_repository" (or None when project.json has not
exactly one entry of layer 1), "acceptance_default_branch",
"norms_default_branch", "norms_commit" and "tree_jsonl" (its bytes).

Never changes the working tree, the index or a local branch of either
repository: only `git fetch origin` moves their remote-tracking branches.
Python 3.9 or later, standard library only.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import unicodedata

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from deny_code_repositories import owner_name, valid_path  # noqa: E402

NORM_ID = re.compile(r"[A-Z]{3,}(?:-[1-9][0-9]*)?")  # ACU-56, R61
PREFIX_FORM = re.compile(r"[A-Z]{3,}")
NODE_KINDS = {"file", "section", "heading", "paragraph", "code_block", "html_block", "link_ref_def", "table",
              "table_row", "table_cell", "block_quote", "list", "item"}  # R61


class Refusal(Exception):
    """A check of ACU-74 that failed: `message` is its bound message, without the prefix of the use case."""

    def __init__(self, message):
        super().__init__(message)
        self.message = message


# ---------------------------------------------------------------- the title (ACU-7, ACU-8)

def breaks_a_line(character):
    """A control character (Unicode category Cc), a line separator (U+2028) or a paragraph separator (U+2029)."""
    return unicodedata.category(character) in ("Cc", "Zl", "Zp")


def _lone_surrogate(character):
    """A code point of U+D800 to U+DFFF: a byte that is not UTF-8, in a path decoded with surrogateescape."""
    return 0xD800 <= ord(character) <= 0xDFFF


def text_of(value):
    """A name, a value or a path found, as a message prints it: a string with no character that breaks a line and no
    lone surrogate as it is; anything else as its JSON text, each such character escaped as \\u and 4 lower-case hex
    digits, so that the message stays one line, no text found forges a line of the output, and print never fails."""
    if isinstance(value, str) and not any(breaks_a_line(c) or _lone_surrogate(c) for c in value):
        return value
    text = json.dumps(value, ensure_ascii=False)
    return "".join(f"\\u{ord(c):04x}" if breaks_a_line(c) or _lone_surrogate(c) else c for c in text)


def heading_title(lines, an_id):
    """The title of the heading "# <an_id> <title>" on the first line, or None: a title holds a character that is not
    a space or a tab, and no character for which breaks_a_line is true (ACU-8)."""
    found = re.fullmatch(re.escape(f"# {an_id} ") + r"(.*\S.*)", lines[0], re.DOTALL) if lines else None
    if not found or any(breaks_a_line(c) for c in found.group(1)):
        return None
    return found.group(1)


# ---------------------------------------------------------------- git

def git(cwd, *args, binary=False):
    """The completed git process; output as text, or as bytes when `binary`."""
    return subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=not binary)


def out(cwd, *args):
    """The output of a git command, stripped, or None when it fails."""
    done = git(cwd, *args)
    return done.stdout.strip() if done.returncode == 0 else None


def show(cwd, revision, path):
    """The bytes of `path` at `revision`, or None when `revision` holds no such file."""
    done = git(cwd, "show", f"{revision}:{path}", binary=True)
    return done.stdout if done.returncode == 0 else None


def ls_tree(cwd, revision, *paths):
    """The files that `revision` holds under `paths`, in path order."""
    done = git(cwd, "ls-tree", "-r", "-z", "--name-only", revision, "--", *paths, binary=True)
    if done.returncode != 0:
        return []
    return sorted(p.decode("utf-8", "surrogateescape") for p in done.stdout.split(b"\0") if p)


def default_branch(cwd):
    """The branch that `git ls-remote --symref origin HEAD` names, or None."""
    text = out(cwd, "ls-remote", "--symref", "origin", "HEAD")
    for line in (text or "").splitlines():
        found = re.match(r"ref: refs/heads/(\S+)\s+HEAD$", line)
        if found:
            return found.group(1)
    return None


def nesting_depth(text):
    """The deepest nesting of lists and objects of a JSON text, the outermost value being level 1, counted by a scan
    with no recursion: brackets inside strings do not count. On a text that is not JSON it still returns a number."""
    depth = deepest = 0
    in_string = escaped = False
    for character in text:
        if in_string:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
        elif character == '"':
            in_string = True
        elif character in "[{":
            depth += 1
            deepest = max(deepest, depth)
        elif character in "]}":
            depth -= 1
    return deepest


# ---------------------------------------------------------------- data/tree.jsonl (R23, R61)

def strings_ok(value):
    """R61: every string is valid Unicode (no lone surrogate).

    Walks the value with a stack of its own, not by recursion, so that a value nested as deep as json.loads reads
    never raises RecursionError."""
    pending = [value]
    while pending:
        item = pending.pop()
        if isinstance(item, str):
            try:
                item.encode("utf-8")
            except UnicodeEncodeError:
                return False
        elif isinstance(item, list):
            pending.extend(item)
        elif isinstance(item, dict):
            pending.extend(item.keys())
            pending.extend(item.values())
    return True


def _path_ok(path, md=None):
    if not isinstance(path, str) or not path or path.startswith("/"):
        return False
    if any(not part or part in (".", "..") or any(ord(c) < 32 or ord(c) == 127 or 0x80 <= ord(c) <= 0x9f
                                                  for c in part) for part in path.split("/")):
        return False
    return md is None or path.endswith(".md") == md


def _int_ok(value):
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _id_ok(value):
    return isinstance(value, str) and NORM_ID.fullmatch(value) is not None


def _reject_constant(name):
    raise ValueError(name)


def _line_ok(obj):
    """R61: whether one object of data/tree.jsonl has its required fields, each of its type and form."""
    if not isinstance(obj, dict) or not strings_ok(obj):
        return False
    kind = obj.get("type")
    if kind == "meta":
        retired_prefixes = obj.get("retired_prefixes", [])
        return (isinstance(obj.get("specs_commit", ""), str) and isinstance(obj.get("generator_version", ""), str)
                and isinstance(retired_prefixes, list)
                and all(isinstance(p, str) and PREFIX_FORM.fullmatch(p) for p in retired_prefixes))
    if kind == "file":
        insertions = obj.get("insertions", [])
        return ("path" in obj and "prefix" in obj and _path_ok(obj["path"], True)
                and isinstance(obj["prefix"], str) and PREFIX_FORM.fullmatch(obj["prefix"]) is not None
                and isinstance(obj.get("sha256", ""), str) and isinstance(insertions, list)
                and all(isinstance(i, list) and len(i) == 2 and _int_ok(i[0]) and isinstance(i[1], str)
                        for i in insertions))
    if kind == "copy":
        return "path" in obj and _path_ok(obj["path"], False) and isinstance(obj.get("sha256", ""), str)
    if kind == "node":
        required = ("id", "file", "kind", "start", "end", "own_text", "own_hash", "tree_hash")
        if any(field not in obj for field in required):
            return False
        parent = obj.get("parent")
        changed_since = obj.get("changed_since")
        return (_id_ok(obj["id"]) and _path_ok(obj["file"]) and obj["kind"] in NODE_KINDS
                and (parent is None or _id_ok(parent)) and _int_ok(obj["start"]) and _int_ok(obj["end"])
                and all(isinstance(obj[f], str) for f in ("own_text", "own_hash", "tree_hash"))
                and obj.get("status", "active") in ("active", "retired")
                and isinstance(obj.get("to_review", False), bool)
                and (changed_since is None or isinstance(changed_since, str)))
    return False


def read_tree(data):
    """R23, R61: the active nodes of data/tree.jsonl, in its order. Raises ValueError when it is not valid."""
    text = data.decode("utf-8")
    found = []
    for line in text.split("\n"):
        if line.endswith("\r"):
            line = line[:-1]
        if not line or line.isspace():
            continue
        try:
            obj = json.loads(line, parse_constant=_reject_constant)
        except RecursionError:
            raise ValueError("too deep")
        if not _line_ok(obj):
            raise ValueError("bad line")
        if obj["type"] == "node" and obj.get("status", "active") == "active":
            found.append(obj)
    return found


# ---------------------------------------------------------------- the checks of ACU-74, one per row

def check_argument(context):
    """Row 1: the user gave an argument (a blank one is none)."""
    if any(str(a).strip() for a in context.get("arguments") or []):
        return "takes no argument"
    return None


def check_acceptance_repository(context):
    """Row 2 (ORC-20, ORC-21): the working directory is in the acceptance repository of its project.json."""
    refused = "runs only from the acceptance repository"
    root = out(context["cwd"], "rev-parse", "--show-toplevel") if os.path.isdir(context["cwd"]) else None
    if not root:
        return refused
    root = os.path.realpath(root)
    try:
        with open(os.path.join(root, "project.json"), "rb") as f:
            project_bytes = f.read()
        project = json.loads(project_bytes.decode("utf-8"))
    except (OSError, ValueError, RecursionError):
        return refused
    repositories = project.get("repositories") if isinstance(project, dict) else None
    if not isinstance(repositories, list) or not all(isinstance(e, dict) for e in repositories):
        return refused
    # ORC-20: every entry names its repository by owner and name; without them ORC-21 cannot read project.json.
    if not all(isinstance(e.get(field), str) and e.get(field) for e in repositories for field in ("owner", "name")):
        return refused
    remote = out(root, "config", "--get", "remote.origin.url")
    me = owner_name(remote) if remote else None
    mine = [e for e in repositories if f"{e.get('owner')}/{e.get('name')}" == me]
    if len(mine) != 1 or mine[0].get("layer") != 3 or not valid_path(mine[0].get("path")):
        return refused
    parts = mine[0]["path"].split("/")
    if root.split(os.sep)[-len(parts):] != parts:
        return refused
    project_folder = root
    for _ in parts:
        project_folder = os.path.dirname(project_folder)
    specs_entries = [e for e in repositories if e.get("layer") == 1]
    context.update(root=root, project_bytes=project_bytes, project=project, repositories=repositories,
                   acceptance_repository=f"{mine[0]['owner']}/{mine[0]['name']}", project_folder=project_folder,
                   specs_repository=(f"{specs_entries[0]['owner']}/{specs_entries[0]['name']}"
                                     if len(specs_entries) == 1 else None))
    return None


def check_norms_entry(context):
    """Row 3 (ORC-20): project.json has exactly one entry of layer 2, with a valid path."""
    norms_entries = [e for e in context["repositories"] if e.get("layer") == 2]
    if len(norms_entries) != 1 or not valid_path(norms_entries[0].get("path")):
        return "project.json has not exactly one entry of layer 2, the norms repository, with a valid path"
    entry = norms_entries[0]
    context.update(norms_repository=f"{entry['owner']}/{entry['name']}",
                   norms_repository_path=os.path.join(context["project_folder"], *entry["path"].split("/")))
    return None


def check_norms_repository_present(context):
    """Row 4 (ORC-22): the norms repository is a git repository at its path, with its remote origin."""
    path, name = context["norms_repository_path"], context["norms_repository"]
    top = out(path, "rev-parse", "--show-toplevel") if os.path.isdir(path) else None
    remote = out(path, "config", "--get", "remote.origin.url") if top else None
    if not top or os.path.realpath(top) != os.path.realpath(path) or not remote or owner_name(remote) != name:
        return f"{name} not found at {path}; run: git clone https://github.com/{name} {path}"
    return None


def check_fetch_acceptance_repository(context):
    """Row 5: git fetch origin in the acceptance repository."""
    if git(context["root"], "fetch", "-q", "origin").returncode != 0:
        return f"cannot fetch {context['acceptance_repository']}"
    return None


def check_fetch_norms_repository(context):
    """Row 6: git fetch origin in the norms repository."""
    if git(context["norms_repository_path"], "fetch", "-q", "origin").returncode != 0:
        return f"cannot fetch {context['norms_repository']}"
    return None


def check_acceptance_default_branch(context):
    """Row 7: the default branch of the acceptance repository."""
    branch = default_branch(context["root"])
    if not branch:
        return f"cannot find the default branch of {context['acceptance_repository']}"
    context["acceptance_default_branch"] = branch
    return None


def check_norms_default_branch(context):
    """Row 8: the default branch of the norms repository, and its head at origin: the norms commit."""
    path = context["norms_repository_path"]
    branch = default_branch(path)
    norms_commit = branch and out(path, "rev-parse", "--verify", "-q", f"refs/remotes/origin/{branch}^{{commit}}")
    if not norms_commit:
        return f"cannot find the default branch of {context['norms_repository']}"
    context.update(norms_default_branch=branch, norms_commit=norms_commit)
    return None


def check_tree_jsonl_present(context):
    """Row 9: the head of the default branch of the norms repository holds data/tree.jsonl."""
    data = show(context["norms_repository_path"], context["norms_commit"], "data/tree.jsonl")
    if data is None:
        return f"{context['norms_repository']} has no data/tree.jsonl on {context['norms_default_branch']}"
    context["tree_jsonl"] = data
    return None


def check_tree_jsonl_valid(context):
    """Row 10: data/tree.jsonl is UTF-8 and each line can be read as R23 and R61 say."""
    try:
        read_tree(context["tree_jsonl"])
    except (ValueError, UnicodeDecodeError):
        return f"{context['norms_repository']}: data/tree.jsonl is not valid"
    return None


def check_annotated_project_json_present(context):
    """Row 11: that commit holds specs-repo-annotated/project.json."""
    copy = show(context["norms_repository_path"], context["norms_commit"], "specs-repo-annotated/project.json")
    if copy is None:
        return (f"{context['norms_repository']} has no specs-repo-annotated/project.json on "
                f"{context['norms_default_branch']}")
    context["annotated_project_bytes"] = copy
    return None


def check_project_json_same(context):
    """Row 12 (ORC-24): project.json is byte for byte that of specs-repo-annotated/ of that commit."""
    if context["annotated_project_bytes"] != context["project_bytes"]:
        return f"project.json differs from that of {context['norms_repository']}; run /project-management:sync"
    return None


def check_on_default_branch(context):
    """Row 13: the acceptance repository is on its default branch."""
    branch = context["acceptance_default_branch"]
    if out(context["root"], "symbolic-ref", "-q", "--short", "HEAD") != branch:
        return f"the acceptance repository is not on {branch}"
    return None


def check_not_ahead(context):
    """Row 14: HEAD holds no commit that origin/<default branch> does not."""
    branch, root = context["acceptance_default_branch"], context["root"]
    upstream = f"refs/remotes/origin/{branch}"
    if (out(root, "rev-parse", "--verify", "-q", upstream) is None
            or out(root, "rev-list", "--count", f"{upstream}..HEAD") != "0"):
        return f"the acceptance repository has commits that are not on origin/{branch}"
    return None


def check_not_behind(context):
    """Row 15: origin/<default branch> holds no commit that HEAD does not."""
    branch = context["acceptance_default_branch"]
    if out(context["root"], "rev-list", "--count", f"HEAD..refs/remotes/origin/{branch}") != "0":
        return f"the acceptance repository is behind origin/{branch}; run git pull"
    return None


CHECKS = (check_argument, check_acceptance_repository, check_norms_entry, check_norms_repository_present,
          check_fetch_acceptance_repository, check_fetch_norms_repository, check_acceptance_default_branch,
          check_norms_default_branch, check_tree_jsonl_present, check_tree_jsonl_valid,
          check_annotated_project_json_present, check_project_json_same, check_on_default_branch,
          check_not_ahead, check_not_behind)


def run_checks(cwd, arguments):
    """ACU-74: the checks in their order; (context, the message of the first that fails, or None)."""
    context = {"cwd": cwd, "arguments": list(arguments)}
    for check in CHECKS:
        message = check(context)
        if message is not None:
            return context, message
    return context, None


def locate(cwd):
    """Rows 2 and 3 of ACU-74 only: the context of the repositories; raises Refusal when one fails."""
    context = {"cwd": cwd, "arguments": []}
    for check in (check_acceptance_repository, check_norms_entry):
        message = check(context)
        if message is not None:
            raise Refusal(message)
    return context
