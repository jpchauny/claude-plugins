"""The reading of the files of the acceptance repository: the inventory of define (ACU-60 to ACU-62), shared by the
use cases of this module that read it.

Spec: specs/module.md of acceptance-management (ACU-6 to ACU-8, ACU-50 to
ACU-56) and specs/define.md of the use case define (ACU-60 to ACU-62). The
use case define (ACU-58 to ACU-73) and the use case write-acceptance-tests
(WAT-5, WAT-6: the format errors of a file of an acceptance unit or an
acceptance area, the citation status of a norm citation and the "own_text"
of a norm, "as the inventory of define computes them") import it; the use
case plan imports the forms of the paths of areas/ and units/
(files_of_layer_3) and the helpers number and plural. Code that several use
cases of the module share lives in the module's folder (DEV-7), once (DEV-4).

API:

    read_norms(where, norms_commit) -> list[dict]
        ACU-60: the norms of data/tree.jsonl at the norms commit, one dict per
        norm ("norm_id", "file", "kind", "parent_norm_id", "norm_hash",
        "own_text"); raises acceptance_repository_checks.Refusal with the
        message "<owner>/<name> has no data/tree.jsonl at <7 hex digits>" or
        "<owner>/<name>: data/tree.jsonl is not valid", which each use case
        says after its own prefix.
    inventory(where, norms_commit, rev="HEAD", norms=None) -> dict
        ACU-60, ACU-61, ACU-62: the inventory of the acceptance repository at
        `rev`, or of the working tree when `rev` is None; raises Refusal as
        read_norms does when `norms` is None. The keys that start with "_"
        are for the scripts only; `public` removes them.
    parse_acceptance_unit, parse_acceptance_area
        ACU-7, ACU-8, ACU-52, ACU-53, ACU-61: one file, with its format errors.
    Layer3(root, rev)
        The files of areas/, units/ and acceptance.json at a commit, or on
        disk when `rev` is None.
    files_of_layer_3(paths) -> (acceptance_unit_files, acceptance_area_files, other_paths)
        The unit ID of each path "units/AU-<n>.md" and the area ID of each
        path "areas/AA-<n>.md", and the paths that are neither.
    head_ids(root), expected_fields(root, present), worktree_errors(...)
        ACU-55, ACU-61: the IDs at HEAD, and the value that each ID field of
        acceptance.json must have on disk.
    evidence_counter(root, rev), field_line(data, field), acceptance_ok(data)
    public(value), number(an_id), plural(count, noun)
    CITATION_IN_LINE, NORM_CITATION_IN_LINE, holds_a_citation(text)
        ACU-56: a citation found in a line, of a file, a title or a name; the
        use case write-acceptance-tests reads its errors of WAT-7 with them.
    quoted_name(name)
        ACU-61: the name of a scenario as a message prints it.

Never writes anything. Python 3.9 or later, standard library only. The names
of the JSON keys and of the identifiers follow the terms of the specs:
"acceptance_unit", "acceptance_area", "unit_hash", "norm_citations"...
"""

from __future__ import annotations

import json
import os
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import acceptance_hashes as hashes  # noqa: E402
import acceptance_repository_checks as checks  # noqa: E402
from acceptance_repository_checks import ls_tree, out, read_tree, show  # noqa: E402

PROFILES = checks.DONE_PROFILES  # ACU-19
KINDS = ("test", "demo", "validation", "deviation", "event")  # ACU-35
ID_FIELDS = (("acceptance_area", "AA", "last_area_id"), ("acceptance_unit", "AU", "last_unit_id"),
             ("scenario", "SC", "last_scenario_id"))  # ACU-55
ACCEPTANCE_UNIT_FILE = re.compile(r"units/(AU-[1-9][0-9]*)\.md")
ACCEPTANCE_AREA_FILE = re.compile(r"areas/(AA-[1-9][0-9]*)\.md")
SC_LIKE = re.compile(r"@SC-([0-9]+)")  # ACU-50
ACCEPTANCE_UNIT_PARTS = ["## Narrative", "## Norms", "## Scenarios", "## Non-goals", "## Assumptions"]  # ACU-8
ACCEPTANCE_AREA_PARTS = ["## Purpose", "## Scenarios"]  # ACU-7
ASSUMPTION_END = re.compile(r"\(([^()]*)\)\.?$")
NARRATIVE = (re.compile(r"In order to \S"), re.compile(r"As an? \S"), re.compile(r"I want \S"))
# ACU-56, "a citation found in a line": defined once, in acceptance_hashes. The norm ID is the whole run of
# characters from its boundary.
CITATION_IN_LINE = hashes.CITATION
NORM_CITATION_IN_LINE = hashes.NORM_CITATION_IN_LINE


def holds_a_citation(text):
    """ACU-56: whether `text` (a title, the name of a scenario or a line) holds a citation found in a line."""
    return bool(CITATION_IN_LINE.search(text) or NORM_CITATION_IN_LINE.search(text))


def quoted_name(name):
    """ACU-61: the name of a scenario in a message: between double quotes, or as ACU-58 says for a path (its JSON
    text, which brings its own double quotes) when it holds a character that ACU-58 escapes."""
    printed = checks.text_of(name)
    return f'"{name}"' if printed == name else printed


# ---------------------------------------------------------------- layer 2

def read_norms(where, commit):
    """The norms at the norms commit (ACU-60): one dict per norm, in the order of data/tree.jsonl."""
    data = show(where["norms_repository_path"], commit, "data/tree.jsonl")
    if data is None:
        raise checks.Refusal(f"{where['norms_repository']} has no data/tree.jsonl at {commit[:7]}")
    try:
        nodes = read_tree(data)
    except (ValueError, UnicodeDecodeError):
        raise checks.Refusal(f"{where['norms_repository']}: data/tree.jsonl is not valid")
    norms, seen = [], set()
    for node in nodes:
        if node["id"] in seen:
            continue
        seen.add(node["id"])
        norms.append({"norm_id": node["id"], "file": node["file"], "kind": node["kind"],
                      "parent_norm_id": node.get("parent"), "norm_hash": node["tree_hash"][:8].lower(),
                      "own_text": node["own_text"]})
    return norms


# ---------------------------------------------------------------- layer 3: the files

def acceptance_ok(data):
    """ACU-6: the object of acceptance.json, or None when it does not meet ACU-6; the one check of the module, in
    scripts/acceptance_repository_checks.py."""
    return checks.acceptance_json_of(data)


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
    """ACU-7, ACU-8: whether "## Scenarios" is one gherkin block (or "None." in an acceptance area)."""
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


def _scenarios(data, lines, errors, in_acceptance_area):
    """ACU-50, ACU-54: the scenarios of a file, with the errors of their tags."""
    found = []
    allowed = "@SC-<n>, @<norm ID> or @unit:<unit ID>" if in_acceptance_area else "@SC-<n> or @<norm ID>"
    for s in hashes.scenarios(data):
        tag_line = s.line
        sc_like = [t for t in s.tags if SC_LIKE.fullmatch(t)]
        for tag in s.tags:
            if (SC_LIKE.fullmatch(tag) or hashes.NORM_TAG.match(tag)
                    or (in_acceptance_area and hashes.ACCEPTANCE_UNIT_TAG.match(tag))):
                continue
            _err(errors, tag_line, f"tag {tag} is not {allowed}")
        if s.name == "":
            _err(errors, tag_line, "scenario has no name")
        if any(checks.breaks_a_line(c) for c in s.name):
            _err(errors, tag_line, f"scenario {quoted_name(s.name)} has a character that breaks a line")
        if holds_a_citation(s.name):
            _err(errors, tag_line, f"scenario {quoted_name(s.name)} holds a citation")
        if s.scenario_id is None or len(sc_like) != 1:
            _err(errors, tag_line, f"scenario {quoted_name(s.name)} has not exactly one tag @SC-<n>")
            scenario_id = None
        else:
            scenario_id = s.scenario_id
        entry = {"scenario_id": scenario_id, "name": s.name, "scenario_hash": s.scenario_hash,
                 "norms": list(dict.fromkeys(s.norms))}
        if in_acceptance_area:
            entry["acceptance_units"] = list(dict.fromkeys(s.acceptance_units))
        entry["_line"] = tag_line
        found.append(entry)
    return found


def parse_acceptance_unit(unit_id, data, ctx):
    """ACU-8, ACU-52, ACU-60, ACU-61: one acceptance unit of the inventory, with its errors."""
    acceptance_unit = {"unit_id": unit_id, "path": f"units/{unit_id}.md", "title": None, "area_id": None,
                       "done_profile": ctx["default_done_profile"], "unit_hash": None, "norm_citations": [],
                       "scenarios": [], "evidence": ctx["evidence"](unit_id), "errors": []}
    errors = acceptance_unit["errors"]
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        _err(errors, None, "not UTF-8")
        return acceptance_unit
    lines = hashes.lines_of(data)
    title = checks.heading_title(lines, unit_id)
    if title is not None:
        acceptance_unit["title"] = title
        if holds_a_citation(title):
            _err(errors, 1, "title holds a citation")
    else:
        _err(errors, 1, f'heading is not "# {unit_id} <title>"')
    acceptance_unit["unit_hash"] = hashes.unit_hash(data)
    preamble, parts = _parts(lines, 1)
    filled = [i for i in preamble if lines[i] != ""]
    area_match = re.fullmatch(r"Area: (AA-[1-9][0-9]*)", lines[filled[0]]) if filled else None
    extra = filled[1:]
    if area_match:
        acceptance_unit["area_id"] = area_match.group(1)
        if acceptance_unit["area_id"] not in ctx["area_ids"]:
            _err(errors, filled[0] + 1, f"acceptance area {acceptance_unit['area_id']} has no file")
        nxt = filled[0] + 1
        if len(filled) > 1 and filled[1] == nxt and lines[nxt].startswith("Profile:"):
            extra = filled[2:]
            done_profile = lines[nxt][len("Profile:"):].strip()
            acceptance_unit["done_profile"] = done_profile
            if done_profile not in PROFILES:
                _err(errors, nxt + 1, f"done profile {done_profile} is not prototype, product or critical")
            elif done_profile == ctx["default_done_profile"]:
                _err(errors, nxt + 1, f"done profile {done_profile} is the default done profile")
    else:
        _err(errors, (filled[0] + 1) if filled else None, 'no line "Area: <area ID>"')
        extra = filled[1:]
    in_order = _check_parts(lines, parts, ACCEPTANCE_UNIT_PARTS, errors, "ACU-8")
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
            _err(errors, index + 1, "no norm citation in ## Norms")
        for i in items:
            m = hashes.NORM_CITATION.match(lines[i])
            if not m:
                _err(errors, i + 1, "not a norm citation")
                continue
            norm_id, hash_in_acceptance_unit = m.group(1), m.group(2)
            if norm_id in cited:
                _err(errors, i + 1, f"{norm_id} is cited twice")
                continue
            cited[norm_id] = i + 1
            hash_in_norms_repository = ctx["norm_hashes"].get(norm_id)
            if hash_in_norms_repository is None:
                citation_status = "retired"
            elif hash_in_norms_repository == hash_in_acceptance_unit:
                citation_status = "current"
            else:
                citation_status = "changed"
            acceptance_unit["norm_citations"].append({
                "norm_id": norm_id, "hash_in_acceptance_unit": hash_in_acceptance_unit,
                "citation_status": citation_status, "hash_in_norms_repository": hash_in_norms_repository,
                "_line": i + 1})

    if "## Scenarios" in by_name:
        index, content = by_name["## Scenarios"]
        if _gherkin(lines, content, errors, allow_none=False):
            acceptance_unit["scenarios"] = _scenarios(data, lines, errors, in_acceptance_area=False)
    tagged = set()
    for scenario in acceptance_unit["scenarios"]:
        for norm_id in scenario["norms"]:
            tagged.add(norm_id)
            if norm_id not in cited:
                _err(errors, scenario["_line"], f"tag @{norm_id} is not in ## Norms")
    for norm_id, line in cited.items():
        if norm_id not in tagged:
            _err(errors, line, f"{norm_id} is checked by no scenario")

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
    acceptance_unit["_cited"] = list(cited)
    return acceptance_unit


def parse_acceptance_area(area_id, data, ctx, acceptance_units):
    """ACU-7, ACU-53, ACU-60, ACU-61: one acceptance area of the inventory, with its errors."""
    acceptance_area = {"area_id": area_id, "path": f"areas/{area_id}.md", "title": None, "area_hash": None,
                       "acceptance_units": [u["unit_id"] for u in acceptance_units if u["area_id"] == area_id],
                       "scenarios": [], "evidence": ctx["evidence"](area_id), "errors": []}
    errors = acceptance_area["errors"]
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        _err(errors, None, "not UTF-8")
        return acceptance_area
    lines = hashes.lines_of(data)
    title = checks.heading_title(lines, area_id)
    if title is not None:
        acceptance_area["title"] = title
        if holds_a_citation(title):
            _err(errors, 1, "title holds a citation")
    else:
        _err(errors, 1, f'heading is not "# {area_id} <title>"')
    acceptance_area["area_hash"] = hashes.area_hash(data)
    preamble, parts = _parts(lines, 1)
    filled = [i for i in preamble if lines[i] != ""]
    in_order = _check_parts(lines, parts, ACCEPTANCE_AREA_PARTS, errors, "ACU-7")
    by_name = {}
    for heading_text, index, content in parts:
        by_name.setdefault(heading_text, (index, content))
    purpose_empty = "## Purpose" in by_name and not _trimmed(lines, by_name["## Purpose"][1])
    if in_order and (filled or purpose_empty):
        _err(errors, (filled[0] + 1) if filled else by_name["## Purpose"][0] + 1, "parts are not those of ACU-7")
    if "## Scenarios" in by_name:
        index, content = by_name["## Scenarios"]
        if _gherkin(lines, content, errors, allow_none=True):
            acceptance_area["scenarios"] = _scenarios(data, lines, errors, in_acceptance_area=True)
    by_unit_id = {u["unit_id"]: u for u in acceptance_units}
    for scenario in acceptance_area["scenarios"]:
        label = scenario["scenario_id"] or quoted_name(scenario["name"])
        if len(scenario["acceptance_units"]) < 2:
            _err(errors, scenario["_line"], f"scenario {label} crosses fewer than two acceptance units")
        norms_of_crossed = set()
        for unit_id in scenario["acceptance_units"]:
            acceptance_unit = by_unit_id.get(unit_id)
            if acceptance_unit is None or acceptance_unit["area_id"] != area_id:
                _err(errors, scenario["_line"], f"{unit_id} is not an acceptance unit of {area_id}")
            if acceptance_unit is not None:
                norms_of_crossed.update(acceptance_unit.get("_cited", []))
        for norm_id in scenario["norms"]:
            if norm_id not in norms_of_crossed:
                _err(errors, scenario["_line"], f"tag @{norm_id} is in ## Norms of no acceptance unit it crosses")
    return acceptance_area


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


def files_of_layer_3(paths):
    """ACU-7, ACU-8: the path of each file "units/AU-<n>.md" by its unit ID, the path of each file "areas/AA-<n>.md"
    by its area ID, and the other paths, in their order."""
    acceptance_unit_files, acceptance_area_files, other_paths = {}, {}, []
    for path in paths:
        match_of_acceptance_unit_file = ACCEPTANCE_UNIT_FILE.fullmatch(path)
        match_of_acceptance_area_file = ACCEPTANCE_AREA_FILE.fullmatch(path)
        if match_of_acceptance_unit_file:
            acceptance_unit_files[match_of_acceptance_unit_file.group(1)] = path
        elif match_of_acceptance_area_file:
            acceptance_area_files[match_of_acceptance_area_file.group(1)] = path
        else:
            other_paths.append(path)
    return acceptance_unit_files, acceptance_area_files, other_paths


def evidence_counter(root, rev):
    """ACU-60: the count of the lines of each kind of records/<ID>.jsonl at `rev`."""
    def count(an_id):
        counts = {kind: 0 for kind in KINDS}
        data = show(root, rev, f"records/{an_id}.jsonl") or b""
        for line in data.decode("utf-8", "replace").split("\n"):
            try:
                obj = json.loads(line)
            except (ValueError, RecursionError):
                continue
            if isinstance(obj, dict) and obj.get("kind") in counts:
                counts[obj["kind"]] += 1
        return counts
    return count


def field_line(data, field):
    """The number of the line of acceptance.json that holds `field`, or None."""
    for i, line in enumerate((data or b"").decode("utf-8", "replace").split("\n")):
        if f'"{field}"' in line:
            return i + 1
    return None


def inventory(where, norms_commit, rev="HEAD", norms=None):
    """ACU-60: the inventory of the acceptance repository at `rev`, or of the working tree when `rev` is None.

    The keys that start with "_" are for the scripts only; `public` removes them."""
    root = where["root"]
    if norms is None:
        norms = read_norms(where, norms_commit)
    source = Layer3(root, rev)
    errors = []
    acc_bytes = source.read("acceptance.json")
    acc = acceptance_ok(acc_bytes) if acc_bytes is not None else None
    if acc is None:
        errors.append({"path": "acceptance.json", "line": None, "message": "acceptance.json does not meet ACU-6"})
        acc = {"default_done_profile": "product", "last_area_id": 0, "last_unit_id": 0, "last_scenario_id": 0}
    head_rev = rev if rev is not None else "HEAD"
    ctx = {"default_done_profile": acc["default_done_profile"], "norm_hashes": {n["norm_id"]: n["norm_hash"] for n in norms},
           "evidence": evidence_counter(root, head_rev)}
    acceptance_unit_files, acceptance_area_files, other_paths = files_of_layer_3(source.paths())
    for path in other_paths:
        errors.append({"path": path, "line": None,
                       "message": "not the file of an acceptance area or an acceptance unit"})
    ctx["area_ids"] = set(acceptance_area_files)
    acceptance_units = [parse_acceptance_unit(unit_id, source.read(path) or b"", ctx) for unit_id, path in
                        sorted(acceptance_unit_files.items(), key=lambda kv: number(kv[0]))]
    acceptance_areas = [parse_acceptance_area(area_id, source.read(path) or b"", ctx, acceptance_units)
                        for area_id, path in sorted(acceptance_area_files.items(), key=lambda kv: number(kv[0]))]

    holders = {}
    for item in sorted(acceptance_areas + acceptance_units, key=lambda x: x["path"]):
        for scenario in item["scenarios"]:
            if scenario["scenario_id"]:
                holders.setdefault(scenario["scenario_id"], []).append((item["path"], scenario["_line"]))
    for scenario_id, places in sorted(holders.items(), key=lambda kv: number(kv[0])):
        if len(places) > 1:
            errors.append({"path": places[0][0], "line": places[0][1],
                           "message": f"{scenario_id} is the ID of more than one scenario"})

    present = {"acceptance_area": [(a["area_id"], a["path"], None) for a in acceptance_areas],
               "acceptance_unit": [(u["unit_id"], u["path"], None) for u in acceptance_units],
               "scenario": [(scenario_id, places[0][0], places[0][1]) for scenario_id, places in holders.items()]}
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
        "default_done_profile": acc["default_done_profile"],
        "next_ids": {kind: f"{prefix}-{tops[field] + 1}" for kind, prefix, field in ID_FIELDS},
        "norms": norms,
        "acceptance_areas": acceptance_areas,
        "acceptance_units": acceptance_units,
        "errors": errors,
    }
    return result


def head_ids(root):
    """The area IDs, unit IDs and scenario IDs that HEAD holds in any file, and the fields of acceptance.json there."""
    head = Layer3(root, "HEAD")
    ids = {kind: set() for kind, _, _ in ID_FIELDS}
    acceptance_unit_files, acceptance_area_files, _ = files_of_layer_3(head.paths())
    ids["acceptance_unit"].update(acceptance_unit_files)
    ids["acceptance_area"].update(acceptance_area_files)
    for path in sorted(set(acceptance_unit_files.values()) | set(acceptance_area_files.values())):
        try:
            for scenario in hashes.scenarios(head.read(path) or b""):
                if scenario.scenario_id:
                    ids["scenario"].add(scenario.scenario_id)
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
            errors.append({"path": "acceptance.json", "line": field_line(acc_bytes, field),
                           "message": f"{field} of acceptance.json is {acc[field]}, not {expected[field]}"})
    return expected, errors


def public(value):
    """The inventory without the keys of the scripts."""
    if isinstance(value, dict):
        return {k: public(v) for k, v in value.items() if not k.startswith("_")}
    if isinstance(value, list):
        return [public(v) for v in value]
    return value


def plural(count, noun):
    return f"{count} {noun}" if count == 1 else f"{count} {noun}s"


