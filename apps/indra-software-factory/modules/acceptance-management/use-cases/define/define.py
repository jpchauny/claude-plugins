"""The script of the use case define of acceptance-management, with no model (ACU-57 to ACU-73).

Spec: specs/define.md of this folder, and specs/module.md of the module. The
fingerprints (ACU-51 to ACU-54) are those of scripts/acceptance_hashes.py of the
module, which this script imports.

Usage (REPO is the working directory of the skill; every command reads, and
only `ids`, `delete-tests` and `rollback` write, in the acceptance repository
only):

    define.py start REPO [-- ARG...]
        ACU-58: the checks, in their order, with the fetch of both
        repositories; on the first that fails, prints
        "acceptance-management:define: <message>" and exits 1. Otherwise
        prints one JSON object: "acceptance" and "norms" (<owner>/<name>),
        "layer1" (<owner>/<name> of the entry of layer 1, or null), "branch"
        and "norms_branch" (the default branches), "norms_commit",
        "acceptance_commit" and "summary" (the line of ACU-64).
    define.py inventory REPO --norms-commit SHA [--worktree]
        ACU-60, ACU-61, ACU-62: prints the inventory, at HEAD, or with
        --worktree of areas/, units/ and acceptance.json as they are on disk.
    define.py check REPO --norms-commit SHA
        ACU-69 and ACU-73: the files written (those of areas/, units/ and
        acceptance.json that differ from HEAD) and each problem; exits 1 when
        there is one.
    define.py ids REPO
        ACU-55, ACU-65: sets last_area_id, last_unit_id and last_scenario_id of
        acceptance.json on disk to the value that ACU-61 asks, and nothing else.
    define.py delete-tests REPO UNIT_ID
        ACU-10, ACU-70: deletes from the working tree each file of
        tests/<unit ID>/ that HEAD holds.
    define.py commit REPO --norms-commit SHA --change "<verb> <ID>"...
        ACU-71: fetches; when the fetch fails or origin/<branch> moved, exits
        3. Runs `check`; refuses a deleted unit whose tests/<unit ID>/ is
        still there (ACU-70), and a file of areas/ or units/ that belongs to
        no change. Prints a JSON object: "display" (the whole diff and the
        message), "paths", "message" and "command", which fetches again and
        exits 3 with the same message when the fetch fails or origin/<branch>
        moved, and otherwise stages each path by name, commits only them, and
        pushes to the default branch.
    define.py rollback REPO [--change "<verb> <ID>"...]
        ACU-71: puts each file of areas/, units/ and acceptance.json back as
        HEAD holds it, removes the new ones, and gives back the files of
        tests/<unit ID>/ of each "delete <unit ID>".
    define.py next REPO --since SHA
        ACU-72: prints the line "Next: ..." for the commits from SHA to HEAD,
        or nothing.
    define.py hash FILE...
        Prints the unit hash, area hash and scenarios of each file, wherever it
        is, as ACU-52 to ACU-54 compute them.

Never runs git stash, reset, checkout, restore or clean (ACU-73); never
changes the working tree, the index or a local branch of the norms repository
(ACU-59). --norms-commit is 40 lower-case hex digits, the head of a branch of
origin of the norms repository. Python 3.9 or later, standard library only.
"""

from __future__ import annotations

import difflib
import json
import os
import re
import shlex
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(HERE)), "scripts")
sys.path.insert(0, SCRIPTS)
sys.dont_write_bytecode = True

import acceptance_hashes as hashes  # noqa: E402
from deny_code_repositories import owner_name, valid_path  # noqa: E402

PREFIX = "acceptance-management:define: "
PROFILES = ("prototype", "product", "critical")  # ACU-19
KINDS = ("test", "demo", "validation", "deviation", "event")  # ACU-35
ID_FIELDS = (("area", "AA", "last_area_id"), ("unit", "AU", "last_unit_id"), ("scenario", "SC", "last_scenario_id"))
ACCEPTANCE_FIELDS = {"default_profile": str, "last_area_id": int, "last_unit_id": int,
                     "last_scenario_id": int, "test_command": str, "product": dict}  # ACU-6
NORM_ID = re.compile(r"[A-Z]{3,}(?:-[1-9][0-9]*)?")  # ACU-56, R61
PREFIX_FORM = re.compile(r"[A-Z]{3,}")
UNIT_FILE = re.compile(r"units/(AU-[1-9][0-9]*)\.md")
AREA_FILE = re.compile(r"areas/(AA-[1-9][0-9]*)\.md")
CHANGE = re.compile(r"(add|change|delete) ((?:AA|AU)-[1-9][0-9]*)")
SC_LIKE = re.compile(r"@SC-([0-9]+)")
NODE_KINDS = {"file", "section", "heading", "paragraph", "code_block", "html_block", "link_ref_def", "table",
              "table_row", "table_cell", "block_quote", "list", "item"}  # R61
UNIT_PARTS = ["## Narrative", "## Norms", "## Scenarios", "## Non-goals", "## Assumptions"]  # ACU-8
AREA_PARTS = ["## Purpose", "## Scenarios"]  # ACU-7
ASSUMPTION_END = re.compile(r"\(([^()]*)\)\.?$")
NARRATIVE = (re.compile(r"In order to \S"), re.compile(r"As an? \S"), re.compile(r"I want \S"))


class Stop(Exception):
    """A refusal: its message is said after PREFIX, and the command exits with `code`."""

    def __init__(self, message, code=1):
        super().__init__(message)
        self.code = code


# ---------------------------------------------------------------- git

def git(cwd, *args, binary=False, check=False):
    """The completed git process; output as text, or as bytes when `binary`."""
    done = subprocess.run(["git", "-C", cwd, *args], capture_output=True, text=not binary)
    if check and done.returncode != 0:
        raise Stop(f"git {' '.join(args)} failed in {cwd}")
    return done


def out(cwd, *args):
    """The output of a git command, stripped, or None when it fails."""
    done = git(cwd, *args)
    return done.stdout.strip() if done.returncode == 0 else None


def show(cwd, rev, path):
    """The bytes of `path` at `rev`, or None when `rev` holds no such file."""
    done = git(cwd, "show", f"{rev}:{path}", binary=True)
    return done.stdout if done.returncode == 0 else None


def ls_tree(cwd, rev, *paths):
    """The files that `rev` holds under `paths`, in path order."""
    done = git(cwd, "ls-tree", "-r", "-z", "--name-only", rev, "--", *paths, binary=True)
    if done.returncode != 0:
        return []
    return sorted(p.decode("utf-8", "surrogateescape") for p in done.stdout.split(b"\0") if p)


def default_branch(cwd):
    """The branch that `git ls-remote --symref origin HEAD` names, or None."""
    text = out(cwd, "ls-remote", "--symref", "origin", "HEAD")
    for line in (text or "").splitlines():
        m = re.match(r"ref: refs/heads/(\S+)\s+HEAD$", line)
        if m:
            return m.group(1)
    return None


# ---------------------------------------------------------------- where the repositories are

def locate(cwd):
    """ORC-20, ORC-21: the acceptance repository, its entry, and the entries of layers 1 and 2.

    Raises Stop with the message of the second row of ACU-58 when the repository is not that of layer 3, and
    with that of the third row when project.json has not exactly one entry of layer 2 with a valid path."""
    refused = Stop("runs only from the repository of layer 3")
    root = out(cwd, "rev-parse", "--show-toplevel")
    if not root:
        raise refused
    root = os.path.realpath(root)
    try:
        with open(os.path.join(root, "project.json"), "rb") as f:
            project_bytes = f.read()
        project = json.loads(project_bytes.decode("utf-8"))
    except (OSError, ValueError):
        raise refused
    entries = project.get("repositories") if isinstance(project, dict) else None
    if not isinstance(entries, list) or not all(isinstance(e, dict) for e in entries):
        raise refused
    remote = out(root, "config", "--get", "remote.origin.url")
    me = owner_name(remote) if remote else None
    mine = [e for e in entries if f"{e.get('owner')}/{e.get('name')}" == me]
    if len(mine) != 1 or mine[0].get("layer") != 3 or not valid_path(mine[0].get("path")):
        raise refused
    parts = mine[0]["path"].split("/")
    if root.split(os.sep)[-len(parts):] != parts:
        raise refused
    folder = root
    for _ in parts:
        folder = os.path.dirname(folder)
    layer2 = [e for e in entries if e.get("layer") == 2]
    if len(layer2) != 1 or not valid_path(layer2[0].get("path")):
        raise Stop("project.json has not exactly one entry of layer 2 with a valid path")
    layer1 = [e for e in entries if e.get("layer") == 1]
    norms = layer2[0]
    return {
        "root": root,
        "project_bytes": project_bytes,
        "acceptance": f"{mine[0]['owner']}/{mine[0]['name']}",
        "norms": f"{norms['owner']}/{norms['name']}",
        "norms_path": os.path.join(folder, *norms["path"].split("/")),
        "layer1": f"{layer1[0]['owner']}/{layer1[0]['name']}" if len(layer1) == 1 else None,
    }


def norms_present(where):
    """ORC-22: whether the norms repository is a git repository at its path, with its remote origin."""
    path = where["norms_path"]
    top = out(path, "rev-parse", "--show-toplevel") if os.path.isdir(path) else None
    if not top or os.path.realpath(top) != os.path.realpath(path):
        return False
    remote = out(path, "config", "--get", "remote.origin.url")
    return bool(remote) and owner_name(remote) == where["norms"]


# ---------------------------------------------------------------- layer 2

def _strings_ok(value):
    """R61: every string is valid Unicode (no lone surrogate)."""
    if isinstance(value, str):
        try:
            value.encode("utf-8")
        except UnicodeEncodeError:
            return False
        return True
    if isinstance(value, list):
        return all(_strings_ok(v) for v in value)
    if isinstance(value, dict):
        return all(_strings_ok(k) and _strings_ok(v) for k, v in value.items())
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
    if not isinstance(obj, dict) or not _strings_ok(obj):
        return False
    kind = obj.get("type")
    if kind == "meta":
        rp = obj.get("retired_prefixes", [])
        return (isinstance(obj.get("specs_commit", ""), str) and isinstance(obj.get("generator_version", ""), str)
                and isinstance(rp, list) and all(isinstance(p, str) and PREFIX_FORM.fullmatch(p) for p in rp))
    if kind == "file":
        ins = obj.get("insertions", [])
        return ("path" in obj and "prefix" in obj and _path_ok(obj["path"], True)
                and isinstance(obj["prefix"], str) and PREFIX_FORM.fullmatch(obj["prefix"]) is not None
                and isinstance(obj.get("sha256", ""), str) and isinstance(ins, list)
                and all(isinstance(i, list) and len(i) == 2 and _int_ok(i[0]) and isinstance(i[1], str)
                        for i in ins))
    if kind == "copy":
        return "path" in obj and _path_ok(obj["path"], False) and isinstance(obj.get("sha256", ""), str)
    if kind == "node":
        required = ("id", "file", "kind", "start", "end", "own_text", "own_hash", "tree_hash")
        if any(field not in obj for field in required):
            return False
        parent = obj.get("parent")
        changed = obj.get("changed_since")
        return (_id_ok(obj["id"]) and _path_ok(obj["file"]) and obj["kind"] in NODE_KINDS
                and (parent is None or _id_ok(parent)) and _int_ok(obj["start"]) and _int_ok(obj["end"])
                and all(isinstance(obj[f], str) for f in ("own_text", "own_hash", "tree_hash"))
                and obj.get("status", "active") in ("active", "retired")
                and isinstance(obj.get("to_review", False), bool)
                and (changed is None or isinstance(changed, str)))
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


def read_norms(where, commit):
    """The norms at the norms commit (ACU-60): one dict per norm, in the order of data/tree.jsonl."""
    data = show(where["norms_path"], commit, "data/tree.jsonl")
    if data is None:
        raise Stop(f"{where['norms']} has no data/tree.jsonl at {commit[:7]}")
    try:
        nodes = read_tree(data)
    except (ValueError, UnicodeDecodeError):
        raise Stop(f"{where['norms']}: data/tree.jsonl is not valid")
    norms, seen = [], set()
    for node in nodes:
        if node["id"] in seen:
            continue
        seen.add(node["id"])
        norms.append({"id": node["id"], "file": node["file"], "kind": node["kind"], "parent": node.get("parent"),
                      "hash": node["tree_hash"][:8].lower(), "text": node["own_text"]})
    return norms


# ---------------------------------------------------------------- layer 3: the files

def acceptance_ok(data):
    """ACU-6: the object of acceptance.json, or None when it does not meet ACU-6."""
    try:
        obj = json.loads(data.decode("utf-8"))
    except (ValueError, UnicodeDecodeError, AttributeError):
        return None
    if not isinstance(obj, dict) or set(obj) != set(ACCEPTANCE_FIELDS):
        return None
    for field, kind in ACCEPTANCE_FIELDS.items():
        value = obj[field]
        if not isinstance(value, kind) or isinstance(value, bool):
            return None
        if kind is int and value < 0:
            return None
    if obj["default_profile"] not in PROFILES:
        return None
    return obj


def number(an_id):
    return int(an_id.split("-")[1])


def _err(errors, line, message):
    errors.append({"line": line, "message": message})


def _parts(lines, start):
    """The parts of a file: (preamble indexes, [(heading, index of its line, [content indexes])]).

    A part starts at a line that starts with "## " outside a code fence."""
    heads, fence = [], False
    for i in range(start, len(lines)):
        stripped = lines[i].lstrip(" \t")
        if stripped.startswith("```"):
            fence = not fence
            continue
        if not fence and lines[i].startswith("## "):
            heads.append(i)
    preamble = list(range(start, heads[0] if heads else len(lines)))
    parts = []
    for k, head in enumerate(heads):
        end = heads[k + 1] if k + 1 < len(heads) else len(lines)
        parts.append((lines[head], head, list(range(head + 1, end))))
    return preamble, parts


def _trimmed(lines, indexes):
    """The indexes of a part without its empty lines at either end."""
    indexes = list(indexes)
    while indexes and lines[indexes[0]] == "":
        indexes.pop(0)
    while indexes and lines[indexes[-1]] == "":
        indexes.pop()
    return indexes


def _check_parts(lines, parts, expected, errors, name):
    """ACU-7, ACU-8: the parts are those expected, in their order."""
    names = [p[0] for p in parts]
    if names == expected:
        return True
    line = None
    for k, (heading, index, _) in enumerate(parts):
        if k >= len(expected) or heading != expected[k]:
            line = index + 1
            break
    _err(errors, line, f"parts are not those of {name}")
    return False


def _gherkin(lines, indexes, errors, allow_none):
    """ACU-7, ACU-8: whether "## Scenarios" is one gherkin block (or "None." in an area)."""
    body = _trimmed(lines, indexes)
    if allow_none and [lines[i] for i in body] == ["None."]:
        return True
    ok = (len(body) >= 2 and lines[body[0]].strip() == "```gherkin" and lines[body[-1]].strip() == "```"
          and not any(lines[i].lstrip(" \t").startswith("```") for i in body[1:-1]))
    if not ok:
        _err(errors, (body[0] + 1) if body else None, "## Scenarios is not one gherkin block")
        return False
    for i in body[1:-1]:
        stripped = lines[i].lstrip(" \t")
        for word in hashes.FORBIDDEN:
            if stripped.startswith(word):
                _err(errors, i + 1, f"{word} is not allowed in ## Scenarios")
                break
    return True


def _scenarios(data, lines, errors, in_area):
    """ACU-50, ACU-54: the scenarios of a file, with the errors of their tags."""
    found = []
    for s in hashes.scenarios(data):
        tag_line = s.line
        sc_like = [t for t in s.tags if SC_LIKE.fullmatch(t)]
        for tag in s.tags:
            if SC_LIKE.fullmatch(tag) or hashes.NORM_TAG.match(tag) or (in_area and hashes.UNIT_TAG.match(tag)):
                continue
            _err(errors, tag_line, f"tag {tag} is not a scenario, norm or unit tag")
        if s.id is None or len(sc_like) != 1:
            _err(errors, tag_line, f'scenario "{s.name}" has not exactly one tag @SC-<n>')
            sid = None
        else:
            sid = s.id
        entry = {"id": sid, "name": s.name, "hash": s.hash, "norms": list(dict.fromkeys(s.norms))}
        if in_area:
            entry["units"] = list(dict.fromkeys(s.units))
        entry["_line"] = tag_line
        found.append(entry)
    return found


def parse_unit(uid, data, ctx):
    """ACU-8, ACU-52, ACU-60, ACU-61: one unit of the inventory, with its errors."""
    unit = {"id": uid, "path": f"units/{uid}.md", "title": None, "area": None,
            "profile": ctx["default_profile"], "hash": None, "citations": [], "scenarios": [],
            "evidence": ctx["evidence"](uid), "errors": []}
    errors = unit["errors"]
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        _err(errors, None, "not UTF-8")
        return unit
    lines = hashes.lines_of(data)
    heading = re.fullmatch(re.escape(f"# {uid} ") + r"(.*\S.*)", lines[0])
    if heading:
        unit["title"] = heading.group(1)
    else:
        _err(errors, 1, f'heading is not "# {uid} <title>"')
    unit["hash"] = hashes.unit_hash(data)
    preamble, parts = _parts(lines, 1)
    filled = [i for i in preamble if lines[i] != ""]
    area_match = re.fullmatch(r"Area: (AA-[1-9][0-9]*)", lines[filled[0]]) if filled else None
    extra = filled[1:]
    if area_match:
        unit["area"] = area_match.group(1)
        if unit["area"] not in ctx["area_ids"]:
            _err(errors, filled[0] + 1, f"area {unit['area']} has no file")
        nxt = filled[0] + 1
        if len(filled) > 1 and filled[1] == nxt and lines[nxt].startswith("Profile:"):
            extra = filled[2:]
            profile = lines[nxt][len("Profile:"):].strip()
            unit["profile"] = profile
            if profile not in PROFILES:
                _err(errors, nxt + 1, f"profile {profile} is not prototype, product or critical")
            elif profile == ctx["default_profile"]:
                _err(errors, nxt + 1, f"profile {profile} is the default profile")
    else:
        _err(errors, (filled[0] + 1) if filled else None, 'no line "Area: <area ID>"')
        extra = filled[1:]
    in_order = _check_parts(lines, parts, UNIT_PARTS, errors, "ACU-8")
    if extra and in_order:
        _err(errors, extra[0] + 1, "parts are not those of ACU-8")
    by_name = {}
    for heading_text, index, content in parts:
        by_name.setdefault(heading_text, (index, content))

    if "## Narrative" in by_name:
        index, content = by_name["## Narrative"]
        body = _trimmed(lines, content)
        if len(body) != 3 or body != list(range(body[0], body[0] + 3)) or not all(
                NARRATIVE[k].match(lines[body[k]]) for k in range(3)):
            _err(errors, index + 1, "narrative is not In order to, As a, I want")

    cited = {}
    if "## Norms" in by_name:
        index, content = by_name["## Norms"]
        items = [i for i in content if lines[i] != ""]
        if not any(lines[i].startswith("- ") for i in items):
            _err(errors, index + 1, "no citation in ## Norms")
        for i in items:
            m = hashes.NORM_CITATION.match(lines[i])
            if not m:
                _err(errors, i + 1, "not a citation of a norm")
                continue
            norm, cited_hash = m.group(1), m.group(2)
            if norm in cited:
                _err(errors, i + 1, f"{norm} is cited twice")
                continue
            cited[norm] = i + 1
            now = ctx["norm_hashes"].get(norm)
            status = "retired" if now is None else ("current" if now == cited_hash else "changed")
            unit["citations"].append({"norm": norm, "hash": cited_hash, "status": status, "norm_hash": now,
                                      "_line": i + 1})

    if "## Scenarios" in by_name:
        index, content = by_name["## Scenarios"]
        if _gherkin(lines, content, errors, allow_none=False):
            unit["scenarios"] = _scenarios(data, lines, errors, in_area=False)
    tagged = set()
    for s in unit["scenarios"]:
        for norm in s["norms"]:
            tagged.add(norm)
            if norm not in cited:
                _err(errors, s["_line"], f"tag @{norm} is not in ## Norms")
    for norm, line in cited.items():
        if norm not in tagged:
            _err(errors, line, f"{norm} is checked by no scenario")

    for name in ("## Non-goals", "## Assumptions"):
        if name not in by_name:
            continue
        index, content = by_name[name]
        body = _trimmed(lines, content)
        if [lines[i] for i in body] == ["None."]:
            continue
        items = [i for i in body if lines[i] != ""]
        if not items or not all(re.match(r"- \S", lines[i]) for i in items):
            _err(errors, index + 1, f"{name} is not a list or None.")
            continue
        if name == "## Assumptions":
            for i in items:
                m = ASSUMPTION_END.search(lines[i])
                rest = m.group(1) if m else None
                if rest != "environment" and rest not in ctx["norm_hashes"]:
                    _err(errors, i + 1, "assumption rests on no norm and not on (environment)")
    unit["_cited"] = list(cited)
    return unit


def parse_area(aid, data, ctx, units):
    """ACU-7, ACU-53, ACU-60, ACU-61: one area of the inventory, with its errors."""
    area = {"id": aid, "path": f"areas/{aid}.md", "title": None, "hash": None,
            "units": [u["id"] for u in units if u["area"] == aid], "scenarios": [],
            "evidence": ctx["evidence"](aid), "errors": []}
    errors = area["errors"]
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        _err(errors, None, "not UTF-8")
        return area
    lines = hashes.lines_of(data)
    heading = re.fullmatch(re.escape(f"# {aid} ") + r"(.*\S.*)", lines[0])
    if heading:
        area["title"] = heading.group(1)
    else:
        _err(errors, 1, f'heading is not "# {aid} <title>"')
    area["hash"] = hashes.area_hash(data)
    preamble, parts = _parts(lines, 1)
    filled = [i for i in preamble if lines[i] != ""]
    in_order = _check_parts(lines, parts, AREA_PARTS, errors, "ACU-7")
    by_name = {}
    for heading_text, index, content in parts:
        by_name.setdefault(heading_text, (index, content))
    purpose_empty = "## Purpose" in by_name and not _trimmed(lines, by_name["## Purpose"][1])
    if in_order and (filled or purpose_empty):
        _err(errors, (filled[0] + 1) if filled else by_name["## Purpose"][0] + 1, "parts are not those of ACU-7")
    if "## Scenarios" in by_name:
        index, content = by_name["## Scenarios"]
        if _gherkin(lines, content, errors, allow_none=True):
            area["scenarios"] = _scenarios(data, lines, errors, in_area=True)
    by_id = {u["id"]: u for u in units}
    for s in area["scenarios"]:
        label = s["id"] or f'"{s["name"]}"'
        if len(s["units"]) < 2:
            _err(errors, s["_line"], f"scenario {label} crosses fewer than two units")
        norms_of_crossed = set()
        for uid in s["units"]:
            unit = by_id.get(uid)
            if unit is None or unit["area"] != aid:
                _err(errors, s["_line"], f"{uid} is not a unit of {aid}")
            if unit is not None:
                norms_of_crossed.update(unit.get("_cited", []))
        for norm in s["norms"]:
            if norm not in norms_of_crossed:
                _err(errors, s["_line"], f"tag @{norm} is in ## Norms of no unit it crosses")
    return area


# ---------------------------------------------------------------- the inventory

class Layer3:
    """The files of areas/, units/ and acceptance.json at a commit, or on disk when `rev` is None."""

    def __init__(self, root, rev):
        self.root, self.rev = root, rev

    def paths(self):
        if self.rev is not None:
            return ls_tree(self.root, self.rev, "areas", "units")
        found = []
        for top in ("areas", "units"):
            base = os.path.join(self.root, top)
            for folder, dirs, files in os.walk(base):
                dirs.sort()
                for name in files:
                    found.append(os.path.relpath(os.path.join(folder, name), self.root).replace(os.sep, "/"))
        return sorted(found)

    def read(self, path):
        if self.rev is not None:
            return show(self.root, self.rev, path)
        try:
            with open(os.path.join(self.root, path), "rb") as f:
                return f.read()
        except OSError:
            return None


def evidence_counter(root, rev):
    """ACU-60: the count of the lines of each kind of records/<ID>.jsonl at `rev`."""
    def count(an_id):
        counts = {kind: 0 for kind in KINDS}
        data = show(root, rev, f"records/{an_id}.jsonl") or b""
        for line in data.decode("utf-8", "replace").split("\n"):
            try:
                obj = json.loads(line)
            except ValueError:
                continue
            if isinstance(obj, dict) and obj.get("kind") in counts:
                counts[obj["kind"]] += 1
        return counts
    return count


def _field_line(data, field):
    """The number of the line of acceptance.json that holds `field`, or None."""
    for i, line in enumerate((data or b"").decode("utf-8", "replace").split("\n")):
        if f'"{field}"' in line:
            return i + 1
    return None


def inventory(where, norms_commit, rev="HEAD", norms=None):
    """ACU-60: the inventory of the acceptance repository at `rev`, or of the working tree when `rev` is None.

    The keys that start with "_" are for this script only; `public` removes them."""
    root = where["root"]
    if norms is None:
        norms = read_norms(where, norms_commit)
    source = Layer3(root, rev)
    errors = []
    acc_bytes = source.read("acceptance.json")
    acc = acceptance_ok(acc_bytes) if acc_bytes is not None else None
    if acc is None:
        errors.append({"path": "acceptance.json", "line": None, "message": "acceptance.json does not meet ACU-6"})
        acc = {"default_profile": "product", "last_area_id": 0, "last_unit_id": 0, "last_scenario_id": 0}
    head_rev = rev if rev is not None else "HEAD"
    ctx = {"default_profile": acc["default_profile"], "norm_hashes": {n["id"]: n["hash"] for n in norms},
           "evidence": evidence_counter(root, head_rev)}
    unit_files, area_files = {}, {}
    for path in source.paths():
        m_unit, m_area = UNIT_FILE.fullmatch(path), AREA_FILE.fullmatch(path)
        if m_unit:
            unit_files[m_unit.group(1)] = path
        elif m_area:
            area_files[m_area.group(1)] = path
        else:
            errors.append({"path": path, "line": None, "message": "not the file of an area or a unit"})
    ctx["area_ids"] = set(area_files)
    units = [parse_unit(uid, source.read(path) or b"", ctx) for uid, path in
             sorted(unit_files.items(), key=lambda kv: number(kv[0]))]
    areas = [parse_area(aid, source.read(path) or b"", ctx, units) for aid, path in
             sorted(area_files.items(), key=lambda kv: number(kv[0]))]

    holders = {}
    for item in sorted(areas + units, key=lambda x: x["path"]):
        for s in item["scenarios"]:
            if s["id"]:
                holders.setdefault(s["id"], []).append((item["path"], s["_line"]))
    for sid, places in sorted(holders.items(), key=lambda kv: number(kv[0])):
        if len(places) > 1:
            errors.append({"path": places[0][0], "line": places[0][1],
                           "message": f"{sid} is the ID of more than one scenario"})

    present = {"area": [(a["id"], a["path"], None) for a in areas],
               "unit": [(u["id"], u["path"], None) for u in units],
               "scenario": [(sid, places[0][0], places[0][1]) for sid, places in holders.items()]}
    for kind, _, field in ID_FIELDS:
        for an_id, path, line in sorted(present[kind], key=lambda x: number(x[0])):
            if number(an_id) > acc[field]:
                errors.append({"path": path, "line": line,
                               "message": f"{an_id} is greater than {field} of acceptance.json"})

    tops = {field: max([acc[field]] + [number(an_id) for an_id, _, _ in present[kind]])
            for kind, _, field in ID_FIELDS}
    if rev is None:
        expected, more = worktree_errors(where, acc, acc_bytes, present)
        errors += more
        tops = {field: max(tops[field], expected[field]) for field in tops}

    result = {
        "norms_commit": norms_commit,
        "acceptance_commit": out(root, "rev-parse", head_rev),
        "default_profile": acc["default_profile"],
        "next_ids": {kind: f"{prefix}-{tops[field] + 1}" for kind, prefix, field in ID_FIELDS},
        "norms": norms,
        "areas": areas,
        "units": units,
        "errors": errors,
    }
    return result


def head_ids(root):
    """The area IDs, unit IDs and scenario IDs that HEAD holds in any file, and the fields of acceptance.json there."""
    head = Layer3(root, "HEAD")
    ids = {"area": set(), "unit": set(), "scenario": set()}
    for path in head.paths():
        m_unit, m_area = UNIT_FILE.fullmatch(path), AREA_FILE.fullmatch(path)
        if m_unit:
            ids["unit"].add(m_unit.group(1))
        elif m_area:
            ids["area"].add(m_area.group(1))
        else:
            continue
        try:
            for s in hashes.scenarios(head.read(path) or b""):
                if s.id:
                    ids["scenario"].add(s.id)
        except UnicodeDecodeError:
            pass
    acc = acceptance_ok(head.read("acceptance.json") or b"") or {f: 0 for _, _, f in ID_FIELDS}
    return ids, acc


def expected_fields(root, present):
    """ACU-55, ACU-61: the value that each ID field must have on disk, and the new IDs already given.

    The value is the highest of the field at HEAD and the numbers of the IDs of its kind at HEAD and on disk, so
    that a field lower than an ID at HEAD is raised by the next commit. A new ID, not at HEAD, is already given
    when its number is not above the highest of the field at HEAD and the numbers of the IDs at HEAD."""
    ids, head_acc = head_ids(root)
    expected, reused = {}, []
    for kind, _, field in ID_FIELDS:
        given = max([head_acc[field]] + [number(an_id) for an_id in ids[kind]])
        value = given
        for an_id, path, line in present[kind]:
            if an_id in ids[kind]:
                continue
            if number(an_id) <= given:
                reused.append((an_id, path, line))
            else:
                value = max(value, number(an_id))
        expected[field] = value
    return expected, reused


def worktree_errors(where, acc, acc_bytes, present):
    """ACU-61: the value that each ID field must have on disk, and the errors that compare the working tree with
    HEAD."""
    errors = []
    expected, reused = expected_fields(where["root"], present)
    for an_id, path, line in sorted(reused, key=lambda x: (x[0][:2], number(x[0]))):
        errors.append({"path": path, "line": line, "message": f"{an_id} was already given"})
    for _, _, field in ID_FIELDS:
        if acc[field] != expected[field]:
            errors.append({"path": "acceptance.json", "line": _field_line(acc_bytes, field),
                           "message": f"{field} of acceptance.json is {acc[field]}, not {expected[field]}"})
    return expected, errors


def public(value):
    """The inventory without the keys of this script."""
    if isinstance(value, dict):
        return {k: public(v) for k, v in value.items() if not k.startswith("_")}
    if isinstance(value, list):
        return [public(v) for v in value]
    return value


def plural(count, noun):
    return f"{count} {noun}" if count == 1 else f"{count} {noun}s"


def summary(inv):
    """ACU-64: the line that sums up the inventory."""
    citations = [c for u in inv["units"] for c in u["citations"]]
    changed = sum(c["status"] == "changed" for c in citations)
    retired = sum(c["status"] == "retired" for c in citations)
    errors = len(inv["errors"]) + sum(len(x["errors"]) for x in inv["areas"] + inv["units"])
    return (f"Layer 2 at {inv['norms_commit'][:7]}: {plural(len(inv['norms']), 'norm')}. "
            f"Layer 3 at {inv['acceptance_commit'][:7]}: {plural(len(inv['areas']), 'area')}, "
            f"{plural(len(inv['units']), 'unit')}; {plural(changed, 'citation')} changed, {retired} retired; "
            f"{plural(errors, 'format error')}.")


# ---------------------------------------------------------------- start (ACU-58)

def start(cwd, args):
    if any(a.strip() for a in args):
        raise Stop("takes no argument")
    where = locate(cwd)
    root, acc_name, norms_name, npath = where["root"], where["acceptance"], where["norms"], where["norms_path"]
    if not norms_present(where):
        raise Stop(f"{norms_name} not found at {npath}; run: git clone https://github.com/{norms_name} {npath}")
    if git(root, "fetch", "-q", "origin").returncode != 0:
        raise Stop(f"cannot fetch {acc_name}")
    if git(npath, "fetch", "-q", "origin").returncode != 0:
        raise Stop(f"cannot fetch {norms_name}")
    branch = default_branch(root)
    if not branch:
        raise Stop(f"cannot find the default branch of {acc_name}")
    norms_branch = default_branch(npath)
    norms_commit = norms_branch and out(npath, "rev-parse", "--verify", "-q",
                                        f"refs/remotes/origin/{norms_branch}^{{commit}}")
    if not norms_commit:
        raise Stop(f"cannot find the default branch of {norms_name}")
    tree = show(npath, norms_commit, "data/tree.jsonl")
    if tree is None:
        raise Stop(f"{norms_name} has no data/tree.jsonl on {norms_branch}")
    try:
        read_tree(tree)
    except (ValueError, UnicodeDecodeError):
        raise Stop(f"{norms_name}: data/tree.jsonl is not valid")
    copy = show(npath, norms_commit, "specs-repo-annotated/project.json")
    if copy is None:
        raise Stop(f"{norms_name} has no specs-repo-annotated/project.json on {norms_branch}")
    if copy != where["project_bytes"]:
        raise Stop(f"project.json differs from that of {norms_name}; run /project-management:sync")
    if out(root, "symbolic-ref", "-q", "--short", "HEAD") != branch:
        raise Stop(f"the acceptance repository is not on {branch}")
    upstream = f"refs/remotes/origin/{branch}"
    if out(root, "rev-parse", "--verify", "-q", upstream) is None:
        raise Stop(f"the acceptance repository has commits that are not on origin/{branch}")
    if out(root, "rev-list", "--count", f"{upstream}..HEAD") != "0":
        raise Stop(f"the acceptance repository has commits that are not on origin/{branch}")
    if out(root, "rev-list", "--count", f"HEAD..{upstream}") != "0":
        raise Stop(f"the acceptance repository is behind origin/{branch}; run git pull")
    changed, untracked = status(root)
    if changed:
        raise Stop(f"uncommitted change in {changed[0]}")
    if untracked:
        raise Stop(f"untracked file {untracked[0]}")
    if acceptance_ok(show(root, "HEAD", "acceptance.json") or b"") is None:
        raise Stop("acceptance.json does not meet ACU-6")
    inv = inventory(where, norms_commit)
    return {"acceptance": acc_name, "norms": norms_name, "layer1": where["layer1"], "branch": branch,
            "norms_branch": norms_branch, "norms_commit": norms_commit,
            "acceptance_commit": inv["acceptance_commit"], "summary": summary(inv)}


def status(root):
    """ACU-58: the paths with an uncommitted change among acceptance.json, areas/ and units/, and the untracked
    files under areas/ and units/, each in sorted order."""
    done = git(root, "status", "--porcelain=v1", "-z", "--no-renames", "--untracked-files=all",
               "--", "acceptance.json", "areas", "units", binary=True)
    changed, untracked = [], []
    for entry in done.stdout.split(b"\0"):
        if len(entry) < 4:
            continue
        code, path = entry[:2].decode(), entry[3:].decode("utf-8", "surrogateescape")
        if code == "??":
            (changed if path == "acceptance.json" else untracked).append(path)
        elif code != "!!":
            changed.append(path)
    return sorted(changed), sorted(untracked)


# ---------------------------------------------------------------- after writing (ACU-65, ACU-69, ACU-70)

def written(root):
    """The files of areas/, units/ and acceptance.json that differ from HEAD: (path, bytes at HEAD, bytes on disk)."""
    head = Layer3(root, "HEAD")
    disk = Layer3(root, None)
    paths = sorted(set(head.paths()) | set(disk.paths()) | {"acceptance.json"})
    found = []
    for path in paths:
        old, new = head.read(path), disk.read(path)
        if old != new:
            found.append((path, old, new))
    return found


def check(where, norms_commit):
    """ACU-69, ACU-73: the problems of the files written."""
    root = where["root"]
    norms = read_norms(where, norms_commit)
    before = inventory(where, norms_commit, "HEAD", norms)
    after = inventory(where, norms_commit, None, norms)
    files = written(root)
    paths = [p for p, _, new in files]
    problems = []
    for unit in after["units"]:
        if unit["path"] in paths:
            for c in unit["citations"]:
                if c["status"] != "current":
                    now = c["norm_hash"] or "none: the norm is not in layer 2"
                    problems.append({"path": unit["path"], "line": c["_line"],
                                     "message": f"{c['norm']}@{c['hash']} is {c['status']}; its norm hash is {now}"})
    old = {(e["path"], e["message"]) for e in before["errors"]}
    for x in before["areas"] + before["units"]:
        old |= {(x["path"], e["message"]) for e in x["errors"]}
    for e in after["errors"]:
        if e["path"] in paths or (e["path"], e["message"]) not in old:
            problems.append(e)
    for x in after["areas"] + after["units"]:
        for e in x["errors"]:
            if x["path"] in paths or (x["path"], e["message"]) not in old:
                problems.append({"path": x["path"], "line": e["line"], "message": e["message"]})
    for path, old_bytes, new_bytes in files:
        if path == "acceptance.json":
            a, b = acceptance_ok(old_bytes or b""), acceptance_ok(new_bytes or b"")
            if a and b and any(a[k] != b[k] for k in ACCEPTANCE_FIELDS if not k.startswith("last_")):
                problems.append({"path": path, "line": None, "message":
                                 "only last_area_id, last_unit_id and last_scenario_id may change (ACU-73)"})
    return {"written": paths, "problems": problems}


def set_ids(root):
    """ACU-55, ACU-65: writes on disk the value of each ID field that ACU-61 asks; returns the fields changed."""
    path = os.path.join(root, "acceptance.json")
    with open(path, "rb") as f:
        data = f.read()
    acc = acceptance_ok(data)
    if acc is None:
        raise Stop("acceptance.json does not meet ACU-6")
    disk = Layer3(root, None)
    present = {"area": [], "unit": [], "scenario": []}
    for p in disk.paths():
        m_unit, m_area = UNIT_FILE.fullmatch(p), AREA_FILE.fullmatch(p)
        if not (m_unit or m_area):
            continue
        present["unit" if m_unit else "area"].append(((m_unit or m_area).group(1), p, None))
        try:
            present["scenario"] += [(s.id, p, s.line) for s in hashes.scenarios(disk.read(p) or b"") if s.id]
        except UnicodeDecodeError:
            pass
    expected, _ = expected_fields(root, present)
    text = data.decode("utf-8")
    changed = {}
    for _, _, field in ID_FIELDS:
        if acc[field] == expected[field]:
            continue
        pattern = re.compile(r'("' + field + r'"\s*:\s*)(\d+)')
        if len(pattern.findall(text)) != 1:
            raise Stop(f"cannot set {field} of acceptance.json")
        text = pattern.sub(lambda m: m.group(1) + str(expected[field]), text)
        changed[field] = expected[field]
    if changed:
        with open(path, "wb") as f:
            f.write(text.encode("utf-8"))
    return changed


def tests_of(root, uid):
    """The files of tests/<unit ID>/ that HEAD holds."""
    return ls_tree(root, "HEAD", f"tests/{uid}")


def delete_tests(root, uid):
    """ACU-10, ACU-70: deletes from the working tree each file of tests/<unit ID>/ that HEAD holds."""
    if not re.fullmatch(r"AU-[1-9][0-9]*", uid):
        raise Stop(f"{uid} is not a unit ID")
    deleted = []
    for path in tests_of(root, uid):
        full = os.path.join(root, *path.split("/"))
        if os.path.lexists(full):
            os.remove(full)
            deleted.append(path)
    base = os.path.join(root, "tests", uid)
    for folder, _, _ in sorted(os.walk(base), key=lambda x: -len(x[0])):
        try:
            os.rmdir(folder)
        except OSError:
            pass
    return deleted


def parse_changes(changes):
    parsed = []
    for change in changes:
        m = CHANGE.fullmatch(change.strip())
        if not m:
            raise Stop(f"not a change: {change}")
        parsed.append((m.group(1), m.group(2)))
    return parsed


def message(changes):
    """ACU-71: the subject and the body of the commit message."""
    if len(changes) == 1:
        verb, an_id = changes[0]
        subject = f"docs: {verb} acceptance {'area' if an_id.startswith('AA-') else 'unit'}"
    else:
        subject = "docs: change acceptance areas and units"
    return subject, "\n".join(f"{verb} {an_id}" for verb, an_id in changes)


def deleted_tests(root, changes):
    """The files of tests/<unit ID>/ that HEAD holds and the working tree does not, for each unit deleted."""
    found = []
    for verb, an_id in changes:
        if verb == "delete" and an_id.startswith("AU-"):
            found += [p for p in tests_of(root, an_id) if not os.path.lexists(os.path.join(root, *p.split("/")))]
    return found


def unified(path, old, new):
    a = (old or b"").decode("utf-8", "replace").splitlines(keepends=True)
    b = (new or b"").decode("utf-8", "replace").splitlines(keepends=True)
    head = "deleted " if new is None else ("new " if old is None else "")
    lines = list(difflib.unified_diff(a, b, "/dev/null" if old is None else f"a/{path}",
                                      "/dev/null" if new is None else f"b/{path}"))
    return f"{head}{path}\n" + "".join(line if line.endswith("\n") else line + "\n" for line in lines)


def _facts(data):
    """The scenario IDs, the norms cited in "## Norms", the line "Area:" and the scenarios of a file."""
    if data is None:
        return set(), set(), None, []
    try:
        found = hashes.scenarios(data)
        cited = {norm for norm, _, _ in hashes.norm_citations(data)}
        area = next((m.group(1) for m in map(re.compile(r"Area: (AA-[1-9][0-9]*)").fullmatch,
                                              hashes.lines_of(data)) if m), None)
    except UnicodeDecodeError:
        return set(), set(), None, []
    return {x.id for x in found if x.id}, cited, area, found


def strays(root, changes, files):
    """ACU-71: the files of areas/ and units/ that differ from HEAD and belong to no change (the term Change).

    A file belongs to a change when it is the file of its ID; when the change moves a scenario or a citation out
    of it into the file of a change (ACU-67); or, for an area, when a scenario of it at HEAD crosses a unit that
    the change deletes, moves to another area, or makes cite no longer a norm of a tag of that scenario (ACU-10,
    ACU-70)."""
    disk, head = Layer3(root, None), Layer3(root, "HEAD")
    named = {f"{'areas' if an_id.startswith('AA-') else 'units'}/{an_id}.md": (verb, an_id) for verb, an_id in changes}
    now_sc, now_norms = set(), set()
    for path in named:
        sc, cited, _, _ = _facts(disk.read(path))
        now_sc |= sc
        now_norms |= cited
    moved = set()
    for path, old, new in files:
        if path == "acceptance.json" or path in named:
            continue
        old_sc, old_norms, _, _ = _facts(old)
        new_sc, new_norms, _, _ = _facts(new)
        if (old_sc - new_sc) & now_sc or (old_norms - new_norms) & now_norms:
            moved.add(path)
    units = {}
    for path in list(named) + sorted(moved):
        m = UNIT_FILE.fullmatch(path)
        if m:
            verb = named[path][0] if path in named else "change"
            units[m.group(1)] = (verb, _facts(head.read(path)), _facts(disk.read(path)))
    found = []
    for path, old, new in files:
        if path == "acceptance.json" or path in named or path in moved:
            continue
        old_scenarios = _facts(old)[3]
        crossed = False
        if AREA_FILE.fullmatch(path):
            for scenario in old_scenarios:
                for uid in scenario.units:
                    if uid not in units:
                        continue
                    verb, (_, cited_before, area_before, _), (_, cited_now, area_now, _) = units[uid]
                    lost = cited_before - cited_now
                    if verb == "delete" or area_before != area_now or set(scenario.norms) & lost:
                        crossed = True
        if not crossed:
            found.append(path)
    return found


def commit(where, norms_commit, change_texts):
    """ACU-71: the diff, the message and the one command that fetches, stages, commits and pushes."""
    root = where["root"]
    changes = parse_changes(change_texts)
    if not changes:
        raise Stop("no change given")
    branch = default_branch(root)
    if not branch:
        raise Stop(f"cannot find the default branch of {where['acceptance']}")
    if git(root, "fetch", "-q", "origin").returncode != 0:
        raise Stop(f"cannot fetch {where['acceptance']}", code=3)
    if out(root, "rev-list", "--count", f"HEAD..refs/remotes/origin/{branch}") != "0":
        raise Stop(f"origin/{branch} moved; run the skill again", code=3)
    result = check(where, norms_commit)
    if result["problems"]:
        raise Stop("the checks of ACU-69 fail:\n" + "\n".join(
            f"{p['path']}:{p['line'] or ''}: {p['message']}" for p in result["problems"]))
    files = written(root)
    present = {p for p, _, new in files if new is not None}
    gone = {p for p, _, new in files if new is None}
    for verb, an_id in changes:
        path = f"{'areas' if an_id.startswith('AA-') else 'units'}/{an_id}.md"
        at_head = show(root, "HEAD", path) is not None
        ok = {"add": path in present and not at_head, "change": path in present and at_head,
              "delete": path in gone}[verb]
        if not ok:
            raise Stop(f"{verb} {an_id}: {path} is not {'deleted' if verb == 'delete' else 'written'} as it says")
        if verb == "delete" and an_id.startswith("AU-") and any(
                os.path.lexists(os.path.join(root, *p.split("/"))) for p in tests_of(root, an_id)):
            raise Stop(f"delete {an_id}: tests/{an_id}/ is not deleted (ACU-70)")
    stray = strays(root, changes, files)
    if stray:
        raise Stop(f"{stray[0]} differs from HEAD, and no change of the commit names it (ACU-71)")
    tests = deleted_tests(root, changes)
    paths = sorted({p for p, _, _ in files} | set(tests))
    subject, body = message(changes)
    r = shlex.quote(root)
    ps = " ".join(shlex.quote(p) for p in paths)
    g = f"git --literal-pathspecs -C {r}"
    cannot = shlex.quote(PREFIX + f"cannot fetch {where['acceptance']}")
    moved = shlex.quote(PREFIX + f"origin/{branch} moved; run the skill again")
    behind = shlex.quote(f"HEAD..refs/remotes/origin/{branch}")
    # ACU-71: the command fetches again first, so that a move of the default branch while the requester reads the
    # diff stops it, with status 3, before it stages anything.
    command = (f"{{ git -C {r} fetch -q origin || {{ echo {cannot}; (exit 3); }}; }}"
               f" && {{ test \"$(git -C {r} rev-list --count {behind})\" = 0 || {{ echo {moved}; (exit 3); }}; }}"
               f" && {g} add -- {ps} && {g} commit -q -m {shlex.quote(subject)} -m {shlex.quote(body)} -- {ps}"
               f" && git -C {r} push -q origin {shlex.quote('HEAD:' + branch)}")
    diffs = [unified(p, old, new) for p, old, new in files]
    diffs += [unified(p, show(root, "HEAD", p), None) for p in tests]
    display = "\n".join(["Diff:", ""] + diffs + ["Commit:", f"    {subject}", ""] +
                        [f"    {line}" for line in body.split("\n")])
    return {"display": display, "paths": paths, "message": f"{subject}\n\n{body}", "command": command,
            "branch": branch}


def rollback(root, change_texts):
    """ACU-71: gives back to areas/, units/ and acceptance.json the bytes of HEAD, and the tests of each unit deleted."""
    changes = parse_changes(change_texts)
    restored = []
    for path, old, new in written(root):
        full = os.path.join(root, *path.split("/"))
        if old is None:
            os.remove(full)
        else:
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "wb") as f:
                f.write(old)
        restored.append(path)
    for path in deleted_tests(root, changes):
        full = os.path.join(root, *path.split("/"))
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "wb") as f:
            f.write(show(root, "HEAD", path))
        restored.append(path)
    return sorted(restored)


def next_line(root, since):
    """ACU-72: the line "Next: ..." for the commits from `since` to HEAD, or None."""
    old, new = Layer3(root, since), Layer3(root, "HEAD")
    paths = sorted(set(old.paths()) | set(new.paths()))
    units_touched, ids = False, []
    for path in paths:
        m_unit, m_area = UNIT_FILE.fullmatch(path), AREA_FILE.fullmatch(path)
        if not (m_unit or m_area):
            continue
        a, b = old.read(path), new.read(path)
        if a == b:
            continue
        if m_unit:
            units_touched = True
        if b is None:
            continue
        compute = hashes.unit_hash if m_unit else hashes.area_hash
        try:
            before = compute(a) if a is not None else None
            after = compute(b)
        except UnicodeDecodeError:
            continue
        if after is not None and after != before:
            ids.append((m_unit or m_area).group(1))
    ids.sort(key=lambda x: (x[:2] != "AA", number(x)))
    parts = []
    if units_touched:
        parts.append("the implementation planner updates plan.json")
    if ids:
        parts.append(f"the test agent updates the acceptance tests of {', '.join(ids)}")
    return f"Next: {'; '.join(parts)}." if parts else None


# ---------------------------------------------------------------- main

def norms_commit_of(where, rest):
    """The option --norms-commit: 40 lower-case hex digits, the head of a branch of origin of the norms repository
    (ACU-59), never a local branch, HEAD or a short SHA."""
    sha = option(rest, "--norms-commit")
    refs = out(where["norms_path"], "for-each-ref", "--points-at", sha, "--format=%(refname)", "refs/remotes/origin/")
    if not re.fullmatch(r"[0-9a-f]{40}", sha) or not refs:
        raise Stop(f"--norms-commit {sha} is not the head of a branch of origin in {where['norms']}; "
                   "run the skill again")
    return sha


def option(args, name, many=False):
    values = [args[i + 1] for i, a in enumerate(args[:-1]) if a == name]
    if many:
        return values
    if len(values) != 1:
        raise Stop(f"{name} is required")
    return values[0]


def main(argv):
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    command, args = argv[0], argv[1:]
    if command == "hash":
        for path in args:
            with open(path, "rb") as f:
                data = f.read()
            print(json.dumps({"path": path, "unit_hash": hashes.unit_hash(data), "area_hash": hashes.area_hash(data),
                              "scenarios": [{"id": s.id, "name": s.name, "hash": s.hash}
                                            for s in hashes.scenarios(data)]}, ensure_ascii=False))
        return 0
    if not args:
        raise Stop(f"{command}: REPO is required")
    repo, rest = args[0], args[1:]
    if command == "start":
        extra = rest[1:] if rest[:1] == ["--"] else rest
        print(json.dumps(start(repo, extra), ensure_ascii=False))
        return 0
    where = locate(repo)
    root = where["root"]
    if command == "inventory":
        inv = inventory(where, norms_commit_of(where, rest), None if "--worktree" in rest else "HEAD")
        print(json.dumps(public(inv), ensure_ascii=False))
        return 0
    if command == "check":
        result = check(where, norms_commit_of(where, rest))
        print(json.dumps(result, ensure_ascii=False))
        return 1 if result["problems"] else 0
    if command == "ids":
        print(json.dumps(set_ids(root)))
        return 0
    if command == "delete-tests":
        if len(rest) != 1:
            raise Stop("delete-tests takes one unit ID")
        print(json.dumps(delete_tests(root, rest[0])))
        return 0
    if command == "commit":
        result = commit(where, norms_commit_of(where, rest), option(rest, "--change", many=True))
        print(json.dumps(result, ensure_ascii=False))
        return 0
    if command == "rollback":
        print(json.dumps(rollback(root, option(rest, "--change", many=True))))
        return 0
    if command == "next":
        line = next_line(root, option(rest, "--since"))
        if line:
            print(line)
        return 0
    raise Stop(f"unknown command {command}")


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Stop as stop:
        print(PREFIX + str(stop))
        sys.exit(stop.code)
