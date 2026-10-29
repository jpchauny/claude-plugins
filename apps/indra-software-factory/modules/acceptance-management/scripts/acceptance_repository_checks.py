"""The checks of ACU-74 and ACU-75, shared by every use case of this module that runs from the acceptance repository.

Spec: specs/module.md of acceptance-management, ACU-74 (The files of the
acceptance repository): before it reads anything else, the use case define
(ACU-58), the use case plan (PLN-2) and the use case write-acceptance-tests
(WAT-2) run these checks, with no model, in this order (complete list); the
first that fails ends the use case, which writes nothing and says
"acceptance-management:<use case>: <message>". Each message binds byte for
byte; this module returns it without the prefix, which each use case adds.
ACU-75: the checks before a commit, and the command that makes them again,
stages, commits and pushes (used by define, ACU-71; plan, PLN-12; and
write-acceptance-tests, WAT-12).

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
    acceptance_json_of(data) -> dict | None
        ACU-6: the object of the bytes of acceptance.json when it meets ACU-6,
        as the paragraph "acceptance.json meets ACU-6" of that clause says, or
        None; the one check of every use case of the module (define,
        write-acceptance-tests).
    problems_of_values(code_repositories, values) -> list[str]
        ACU-77: the message of each value of "test_command" and "product" in
        `values` that ACU-77 refuses (all but its row of a field that is not
        empty), in the order of the fields, of the entries and of the rows;
        define checks with it the values that the requester states (ACU-77),
        and write-acceptance-tests the values at HEAD (WAT-2).
    code_repositories(repositories) -> list[str]
        <owner>/<name> of each entry of layer 4 of project.json, in its order.
    git(cwd, *args, binary=False), out(cwd, *args), show(cwd, revision, path),
    ls_tree(cwd, revision, *paths), default_branch(cwd)
        The git helpers that the checks use, for the use cases too.
    checks_before_commit(root, acceptance_repository, expected_head) -> (branch, message | None)
        ACU-75: the rows in their order, made by the script that builds the
        command of a commit; `branch` is the default branch found.
    json_text(value) -> str
        The JSON text that the scripts print, valid UTF-8 whatever path or
        value it holds.
    diff_of_a_file(path, bytes_at_head, bytes_in_working_tree) -> str
        ACU-75: the diff of one file of a commit, as every use case shows it.
    commit_command(prefix, root, acceptance_repository, branch, expected_head, paths, subject, body,
                   prints_the_commit=True) -> str
        ACU-75: the shell command that makes the rows again (all but the row of
        the default branch) before it stages anything, and exits 3 with the
        message of the first that fails; then stages each path by its name,
        commits only them, pushes to `branch` (a rejected push exits 4 with the
        message of ACU-75) and, with `prints_the_commit`, prints the 40 hex
        digits of the commit pushed as its last line (the expected head of
        the next command of define, ACU-71, and of write-acceptance-tests,
        WAT-12; plan, PLN-12, names none and passes False). It prints nothing
        of the output of its fetch and its push.

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

import difflib
import json
import os
import re
import shlex
import subprocess
import sys
import unicodedata

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from deny_code_repositories import owner_name, valid_path  # noqa: E402

NORM_ID = re.compile(r"[A-Z]{3,}(?:-[1-9][0-9]*)?")  # ACU-56, R61
PREFIX_FORM = re.compile(r"[A-Z]{3,}")
DONE_PROFILES = ("prototype", "product", "critical")  # ACU-19
FIELDS_OF_ACCEPTANCE_JSON = {"default_done_profile": str, "last_area_id": int, "last_unit_id": int,
                             "last_scenario_id": int, "test_command": str, "product": dict}  # ACU-6
FIELDS_OF_AN_ENTRY_OF_PRODUCT = ({"build", "env"}, {"build", "env", "published"})  # ACU-6
ENV_NAME = re.compile(r"[A-Z_][A-Z0-9_]*")  # ACU-6
VARIABLES_OF_TEST_COMMAND = ("ACCEPTANCE_TARGET", "ACCEPTANCE_REPORT")  # ACU-6
NODE_KINDS = {"file", "section", "heading", "paragraph", "code_block", "html_block", "link_ref_def", "table",
              "table_row", "table_cell", "block_quote", "list", "item"}  # R61


class Refusal(Exception):
    """A check of ACU-74 that failed: `message` is its bound message, without the prefix of the use case."""

    def __init__(self, message):
        super().__init__(message)
        self.message = message


# ---------------------------------------------------------------- acceptance.json (ACU-6)

def acceptance_json_of(data):
    """ACU-6, "acceptance.json meets ACU-6": the object of `data` (the bytes of acceptance.json) when it is one JSON
    object with exactly the fields of ACU-6, each of its type and form, every entry of "product" an object with
    exactly "build" and "env", or "build", "env" and "published", each a string, and "env" a name of A-Z, 0-9 and _
    that does not start with a digit, and every string valid Unicode (no lone surrogate, which a JSON escape can
    write); otherwise None. An empty string or an empty object meets it; the keys of "product", whether a command
    holds anything, and the values of "env" beyond their form are not part of it."""
    try:
        found = json.loads(data.decode("utf-8"))
    except (ValueError, UnicodeDecodeError, AttributeError, RecursionError):
        return None
    if not isinstance(found, dict) or set(found) != set(FIELDS_OF_ACCEPTANCE_JSON) or not strings_ok(found):
        return None
    for field, kind in FIELDS_OF_ACCEPTANCE_JSON.items():
        value = found[field]
        if not isinstance(value, kind) or isinstance(value, bool) or (kind is int and value < 0):
            return None
    if found["default_done_profile"] not in DONE_PROFILES:
        return None
    for entry in found["product"].values():
        if not (isinstance(entry, dict) and set(entry) in FIELDS_OF_AN_ENTRY_OF_PRODUCT
                and all(isinstance(value, str) for value in entry.values()) and ENV_NAME.fullmatch(entry["env"])):
            return None
    return found


# ---------------------------------------------------------------- the values of test_command and product (ACU-77)

def code_repositories(repositories):
    """<owner>/<name> of each entry of layer 4 of project.json, in its order."""
    return [f"{e['owner']}/{e['name']}" for e in repositories if e.get("layer") == 4]


def is_command(value):
    """ACU-77: a string, valid Unicode (ACU-6), that holds a character other than spaces, tabs and characters that
    break a line (ACU-8)."""
    return isinstance(value, str) and strings_ok(value) and not all(c in " \t" or breaks_a_line(c) for c in value)


def problems_of_values(known_code_repositories, values):
    """ACU-77: the message of each value of "test_command" and "product" in `values` that ACU-77 refuses, other than
    for a field that is not empty: that of test_command, then those of each entry of product in its order, each in the
    order of the rows of the table of ACU-77, then those of two entries with the same env."""
    problems = []
    if "test_command" in values and not is_command(values["test_command"]):
        problems.append("test_command is not a command")
    if "product" not in values:
        return problems
    product = values["product"]
    if not isinstance(product, dict) or not product:
        problems.append("product has no entry")
        return problems
    names = {}
    for key, entry in product.items():
        if key not in known_code_repositories:
            problems.append(f"{text_of(key)} is not a code repository of project.json")
        if not isinstance(entry, dict) or set(entry) not in FIELDS_OF_AN_ENTRY_OF_PRODUCT:
            problems.append(f"the entry {text_of(key)} of product has not the fields of ACU-6")
            continue
        for field in ("build", "published"):
            if field in entry and not is_command(entry[field]):
                problems.append(f"{field} of {text_of(key)} is not a command")
        env = entry["env"]
        if not isinstance(env, str) or not ENV_NAME.fullmatch(env):
            problems.append(f"env {text_of(env)} of {text_of(key)} is not a name of A-Z, 0-9 and _ that does not "
                            "start with a digit")
        elif env in VARIABLES_OF_TEST_COMMAND:
            problems.append(f"env {env} of {text_of(key)} is a variable of test_command (ACU-6)")
        else:
            names[env] = names.get(env, 0) + 1
    for env, count in names.items():
        if count > 1:
            problems.append(f"env {env} is named by more than one entry of product")
    return problems


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


def json_text(value):
    """The JSON text of `value` on one line, as the scripts print it: every character as it is, but each character
    that breaks a line and each lone surrogate (a byte that is not UTF-8, in a path decoded with surrogateescape)
    written as its JSON escape \\u and 4 lower-case hex digits, so that the output is always valid UTF-8, no path
    forges a line or a terminal escape of the output (ACU-58), and print never fails."""
    text = json.dumps(value, ensure_ascii=False)
    return "".join(f"\\u{ord(c):04x}" if breaks_a_line(c) or _lone_surrogate(c) else c for c in text)


def _line_of_a_diff(line):
    """ACU-75: one line of a diff, each character that breaks a line, other than the tab and the line feed that ends
    the line, written as \\u and 4 lower-case hex digits."""
    body = line[:-1] if line.endswith("\n") else line
    return "".join(f"\\u{ord(c):04x}" if (breaks_a_line(c) and c != "\t") or _lone_surrogate(c) else c
                   for c in body) + "\n"


def _lines_of_a_diff(data):
    """The lines of a file for its diff, split only at the line feed, each with its line feed."""
    parts = (data or b"").decode("utf-8", "replace").split("\n")
    return [part + "\n" for part in parts[:-1]] + ([parts[-1]] if parts[-1] else [])


def diff_of_a_file(path, bytes_at_head, bytes_in_working_tree):
    """ACU-75: the diff of one file of a commit, as define (ACU-71), plan (PLN-12) and write-acceptance-tests (WAT-12)
    show it: a line with its path printed as ACU-58 says, after "new " or "deleted " when HEAD or the working tree
    holds none, then its unified diff against HEAD, so that no path or text of a file forges a line of the diff."""
    printed = text_of(path)
    head = "deleted " if bytes_in_working_tree is None else ("new " if bytes_at_head is None else "")
    lines = difflib.unified_diff(_lines_of_a_diff(bytes_at_head), _lines_of_a_diff(bytes_in_working_tree),
                                 "/dev/null" if bytes_at_head is None else f"a/{printed}",
                                 "/dev/null" if bytes_in_working_tree is None else f"b/{printed}")
    return f"{head}{printed}\n" + "".join(_line_of_a_diff(line) for line in lines)


def heading_title(lines, an_id):
    """The title of the heading "# <an_id> <title>" on the first line, or None: a title holds a character that is not
    a space or a tab, and no character for which breaks_a_line is true (ACU-8)."""
    found = re.fullmatch(re.escape(f"# {an_id} ") + r"(.*[^ \t].*)", lines[0], re.DOTALL) if lines else None
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



# ---------------------------------------------------------------- the checks before a commit (ACU-75)

def checks_before_commit(root, acceptance_repository, expected_head):
    """ACU-75, in its order: the fetch, the default branch (found after the fetch, so that an unreachable origin gives
    the message of the fetch), origin moved, HEAD ahead of origin, HEAD no longer the expected head. Returns
    (the default branch, None), or (None, the message of the first row that fails)."""
    if git(root, "fetch", "-q", "origin").returncode != 0:
        return None, f"cannot fetch {acceptance_repository}"
    branch = default_branch(root)
    if not branch:
        return None, f"cannot find the default branch of {acceptance_repository}"
    if out(root, "rev-list", "--count", f"HEAD..refs/remotes/origin/{branch}") != "0":
        return None, f"origin/{branch} moved; run the skill again"
    if out(root, "rev-list", "--count", f"refs/remotes/origin/{branch}..HEAD") != "0":
        return None, f"the acceptance repository has commits that are not on origin/{branch}"
    if out(root, "rev-parse", "HEAD") != expected_head:
        return None, f"origin/{branch} moved; run the skill again"
    return branch, None


def commit_command(prefix, root, acceptance_repository, branch, expected_head, paths, subject, body,
                   prints_the_commit=True):
    """ACU-75: the command of one commit. It fetches again first, so that a move of the default branch, or a commit
    that another session adds to HEAD, while the requester reads the diff stops it, with status 3, before it stages
    anything; it stages and commits each path by its name, never a folder; a rejected push exits 4 with its message;
    with `prints_the_commit`, a pushed commit prints its 40 hex digits, the expected head of the next command."""
    if not paths:
        raise ValueError("a commit names at least one path")
    r = shlex.quote(root)
    ps = " ".join(shlex.quote(p) for p in paths)
    g = f"git --literal-pathspecs -C {r}"
    cannot = shlex.quote(prefix + f"cannot fetch {acceptance_repository}")
    moved = shlex.quote(prefix + f"origin/{branch} moved; run the skill again")
    behind = shlex.quote(f"HEAD..refs/remotes/origin/{branch}")
    ahead = shlex.quote(f"refs/remotes/origin/{branch}..HEAD")
    not_on_origin = shlex.quote(prefix + f"the acceptance repository has commits that are not on origin/{branch}")
    rejected_before = shlex.quote(prefix + "push rejected; commit ")
    rejected_after = shlex.quote(f" is not on origin/{branch}; run git pull --rebase, then git push, and run the "
                                 "skill again")
    return (f"{{ git -C {r} fetch -q origin >/dev/null 2>&1 || {{ echo {cannot}; (exit 3); }}; }}"
            f" && {{ test \"$(git -C {r} rev-list --count {behind})\" = 0 || {{ echo {moved}; (exit 3); }}; }}"
            f" && {{ test \"$(git -C {r} rev-list --count {ahead})\" = 0"
            f" || {{ echo {not_on_origin}; (exit 3); }}; }}"
            f" && {{ test \"$(git -C {r} rev-parse HEAD)\" = {shlex.quote(expected_head)}"
            f" || {{ echo {moved}; (exit 3); }}; }}"
            f" && {g} add -f -- {ps} && {g} commit -q -m {shlex.quote(subject)} -m {shlex.quote(body)} -- {ps}"
            f" && {{ git -C {r} push -q origin {shlex.quote('HEAD:' + branch)} >/dev/null 2>&1"
            f" || {{ echo {rejected_before}\"$(git -C {r} rev-parse HEAD | cut -c1-7)\"{rejected_after}; (exit 4); }}; }}"
            + (f" && git -C {r} rev-parse HEAD" if prints_the_commit else ""))
