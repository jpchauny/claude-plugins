"""The script of the use case plan of acceptance-management, with no model (PLN-1 to PLN-14).

Spec: specs/plan.md of this folder, and specs/module.md of the module. The
checks of ACU-74 are those of scripts/acceptance_repository_checks.py of the
module, and the fingerprints (ACU-51, ACU-52, ACU-54) those of
scripts/acceptance_hashes.py, which this script imports.

Usage (REPO is the working directory of the skill; DRAFT is a file in the
form of plan.json, outside every repository of the project; every command
reads, and only `write` and `rollback` write, and only plan.json):

    plan.py start REPO [-- ARG...]
        PLN-2: the checks of ACU-74, then those of plan, in their order; on the
        first that fails, prints "acceptance-management:plan: <message>" and
        exits 1. Otherwise prints one JSON object: "acceptance_repository",
        "norms_repository", "acceptance_default_branch",
        "norms_default_branch", "norms_commit", "acceptance_commit",
        "plan_commit", "summary" (the line of PLN-8, followed, when plan.json
        at HEAD has errors, by "plan.json is not valid:" and one line per
        error), "nothing_to_plan" (the message of PLN-8, or null) and
        "hand_off_errors" (the lines of PLN-13 for a hand-off with this
        plan.json, or null when it has no error).
    plan.py inventory REPO --norms-commit SHA
        PLN-4: prints the inventory of the plan.
    plan.py propose REPO --norms-commit SHA --draft DRAFT [--rename OLD NEW]...
        PLN-5, PLN-9, PLN-10: when the draft fails a check of PLN-5, prints its
        errors, one per line, and exits 1. When it holds no change of the
        plan, prints the message of "Nothing to propose" (PLN-8) and exits 4.
        Otherwise prints the proposal of the plan: the rendering of the draft,
        the line "Changes:" and the numbered changes of the plan. --rename
        names an increment of the current plan that the draft renames.
    plan.py kept-error REPO --norms-commit SHA [--draft DRAFT]
        PLN-8: the message of a rejected required change of the plan, with the
        first error of PLN-5 of the draft, or of plan.json at HEAD without
        --draft; prints nothing when there is none.
    plan.py write REPO --norms-commit SHA --draft DRAFT
        PLN-11: writes plan.json from the draft, in the form of PLN-11, and
        checks it as PLN-5 says; when it finds an error, puts plan.json back
        as HEAD holds it, prints the errors and exits 1.
    plan.py commit REPO --norms-commit SHA --acceptance-commit SHA [--rename OLD NEW]...
        PLN-12, PLN-13: fetches the norms repository, and exits 3 when the
        fetch fails or origin/<its default branch> is no longer --norms-commit
        (rows 1 to 3 of PLN-12); then makes the checks of ACU-75 (the fetch,
        the default branch, origin/<branch> moved, HEAD holds a commit that
        origin/<branch> does not, HEAD is no longer --acceptance-commit, the
        acceptance_commit of `start`), and exits 3 with the message of the
        first that fails. Checks plan.json on disk again.
        Prints a JSON object: "display" (the whole diff of plan.json and the
        message), "message", "acceptance_default_branch", "command" (it
        fetches again and exits 3 with the same messages, and otherwise stages plan.json by its path, commits
        only plan.json and pushes to the default branch; a rejected push
        prints the message of PLN-12 and exits 4) and "next" (the line
        "Next: ..." of PLN-13 to say once the push is done, or null).
    plan.py rollback REPO
        PLN-12: puts plan.json back as HEAD holds it, or removes it when HEAD
        holds none, in the working tree and in the index, touching no other
        path; only a regular file is written or removed.

Never runs git stash, reset, checkout, restore or clean (PLN-14); never
changes the working tree, the index or a local branch of the norms repository
(PLN-3). --norms-commit is 40 lower-case hex digits, a commit of the norms
repository: the norms commit of `start`, which stays readable after origin
moves; only `commit` checks that it is still the head of the default branch of
origin (row 3 of PLN-12). Python 3.9 or later, standard library only.
The names of the JSON keys and of the identifiers follow the terms of the
specs: "acceptance_unit", "increment_name", "since_the_plan_commit"...
"""

from __future__ import annotations

import difflib
import json
import math
import os
import re
import shlex
import stat
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(HERE)), "scripts")
sys.path.insert(0, SCRIPTS)
sys.dont_write_bytecode = True

import acceptance_hashes as hashes  # noqa: E402
import acceptance_repository_checks as checks  # noqa: E402
from acceptance_repository_checks import git, ls_tree, out, show  # noqa: E402

PREFIX = "acceptance-management:plan: "
UNIT_ID = re.compile(r"AU-[1-9][0-9]*")
ACCEPTANCE_UNIT_FILE = re.compile(r"units/(AU-[1-9][0-9]*)\.md")
ACCEPTANCE_AREA_FILE = re.compile(r"areas/(AA-[1-9][0-9]*)\.md")
INCREMENT_FIELDS = ("name", "acceptance_units")  # ACU-39
PLANNED_ACCEPTANCE_UNIT_FIELDS = ("acceptance_unit", "depends_on", "components")  # ACU-39
EMPTY_PLAN = {"increments": []}
MAXIMUM_NESTING_DEPTH = 64  # row 2 of PLN-5: no version of Python that the script runs on fails below it


class Stop(Exception):
    """A refusal: its message is said after PREFIX, and the command exits with `code`."""

    def __init__(self, message, code=1):
        super().__init__(message)
        self.code = code


class Errors(Stop):
    """The errors of PLN-5 of a plan, printed as they are, one per line, with the exit status 1."""

    def __init__(self, errors):
        super().__init__("\n".join(errors), code=1)


class Said(Stop):
    """A message that already holds PREFIX, printed as it is."""


def number(an_id):
    return int(an_id.split("-")[1])


def plural(count, noun):
    return f"{count} {noun}" if count == 1 else f"{count} {noun}s"


# ---------------------------------------------------------------- the checks of plan (PLN-2)

def components_of(repositories):
    """ORC-20, ACU-39: the components of layer 4, in the order of project.json, or None when its entries of layer 4
    are not one entry without "component", nor one or more entries each with a different "component"."""
    entries = [e for e in repositories if e.get("layer") == 4]
    if len(entries) == 1 and "component" not in entries[0]:
        name = entries[0].get("name")
        return [name] if isinstance(name, str) and name else None
    if not entries or any("component" not in e for e in entries):
        return None
    components = [e["component"] for e in entries]
    if not all(isinstance(c, str) and c for c in components) or len(set(components)) != len(components):
        return None
    return components


def components_message(components):
    """PLN-2: the message of the first check of the components that fails, or None: the entries of layer 4 meet
    ORC-20, and no component breaks a line or starts or ends with a space (_valid_name, row 5 of PLN-5)."""
    if components is None:
        return "project.json: the entries of layer 4 do not meet ORC-20"
    if not all(_valid_name(component) for component in components):
        return "project.json: a component of layer 4 breaks a line or starts or ends with a space"
    return None


def plan_json_is_regular(root):
    """PLN-2: whether plan.json, at HEAD and in the working tree, is a regular file or absent."""
    entry = out(root, "ls-tree", "HEAD", "--", "plan.json")
    if entry and entry.split()[0] not in ("100644", "100755"):
        return False
    return _plan_json_kind(root) in (None, "file")


def plan_json_status(root):
    """PLN-2: the message of the check of plan.json in the working tree and the index, or None."""
    done = git(root, "status", "--porcelain=v1", "-z", "--no-renames", "--untracked-files=all",
               "--ignored=matching", "--", "plan.json", binary=True)
    codes = [entry[:2].decode() for entry in done.stdout.split(b"\0") if len(entry) >= 4]
    if any(code not in ("??", "!!") for code in codes):
        return "uncommitted change in plan.json; commit it, or discard it with: git restore --staged --worktree plan.json"
    if "??" in codes or "!!" in codes:
        return "untracked file plan.json; commit it, or remove it with: rm plan.json"
    return None


def locate(cwd):
    """Rows 2 and 3 of ACU-74 and the components of PLN-2, for the commands after `start`."""
    try:
        where = checks.locate(cwd)
    except checks.Refusal as refusal:
        raise Stop(refusal.message)
    where["components"] = components_of(where["repositories"])
    message = components_message(where["components"])
    if message is not None:
        raise Stop(message)
    return where


# ---------------------------------------------------------------- the errors of a plan (PLN-5)

def _reject_constant(name):
    raise ValueError(name)


def _finite_float(text):
    """Row 2 of PLN-5: a number outside the range of a finite double, such as 1e999, is no value a reader can use."""
    value = float(text)
    if not math.isfinite(value):
        raise ValueError("number out of range")
    return value


def _finite_int(text):
    """Row 2 of PLN-5: an integer outside the range of a finite double; checked by length first, so that the limit of
    the digits of int of Python 3.11 and later never decides it."""
    if len(text.lstrip("-")) > 400:
        raise ValueError("number out of range")
    value = int(text)
    try:
        float(value)
    except OverflowError:
        raise ValueError("number out of range")
    return value


def _reject_repeated_keys(pairs):
    """A JSON object whose keys are all different: a repeated key gives two readers two different plans."""
    keys = [key for key, _ in pairs]
    if len(set(keys)) != len(keys):
        raise ValueError("repeated key")
    return dict(pairs)


def _text_of(value):
    """PLN-5, "How a name or a value found is printed": a string with no control character, line separator or
    paragraph separator as it is; anything else as its JSON text, each such character escaped, so that every error
    stays one line (PLN-8) and no text of a file read forges a line of the output (PLN-14)."""
    return checks.text_of(value)


def _valid_name(name):
    """Row 5 of PLN-5: a string, not empty, with no character that breaks a line (the tab included), and that neither
    starts nor ends with a space."""
    return (isinstance(name, str) and name != "" and not any(checks.breaks_a_line(c) for c in name)
            and name[0] != " " and name[-1] != " ")


def _is_unit_id(value):
    return isinstance(value, str) and UNIT_ID.fullmatch(value) is not None


def _repeated(values):
    """PLN-5, "The order of the errors": the values that occur two or more times, each once, at the place of its first
    occurrence."""
    counts = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return [value for value, count in counts.items() if count > 1]


def check_plan(data, unit_ids_with_file, components):
    """PLN-5: the errors of a plan given as bytes, against the unit IDs that have a file at HEAD and the components.

    Returns (errors, error_of_reading, value), where `value` is the JSON value, or None when row 1 or row 2 holds."""
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return ["plan.json is not UTF-8"], True, None
    if checks.nesting_depth(text) > MAXIMUM_NESTING_DEPTH:
        return ["plan.json is not valid JSON"], True, None
    try:
        value = json.loads(text, parse_constant=_reject_constant, parse_float=_finite_float, parse_int=_finite_int,
                           object_pairs_hook=_reject_repeated_keys)
    except (ValueError, RecursionError):
        return ["plan.json is not valid JSON"], True, None
    if not checks.strings_ok(value):
        # A lone surrogate, such as the escape \ud800, is no Unicode text: no reader of plan.json can use it.
        return ["plan.json is not valid JSON"], True, None
    if not (isinstance(value, dict) and set(value) == {"increments"} and isinstance(value["increments"], list)):
        return ["plan.json is not one object with the one field increments (ACU-39)"], True, value
    rows = {row: [] for row in range(4, 20)}
    increments = []
    for i, increment in enumerate(value["increments"], 1):
        if not (isinstance(increment, dict) and set(increment) == set(INCREMENT_FIELDS)):
            rows[4].append(f"increment {i} is not an object with the fields name and acceptance_units (ACU-39)")
            continue
        if not _valid_name(increment["name"]):
            rows[5].append(f"increment {i} has no valid name (ACU-39)")
        increments.append(increment)
    for name in _repeated([increment["name"] for increment in increments if _valid_name(increment["name"])]):
        rows[6].append(f"increment name {_text_of(name)} is used twice (ACU-9)")
    planned = []
    for increment in increments:
        label = _text_of(increment["name"])
        if not isinstance(increment["acceptance_units"], list):
            rows[7].append(f"increment {label}: acceptance_units is not a list (ACU-39)")
            continue
        for k, planned_acceptance_unit in enumerate(increment["acceptance_units"], 1):
            if not (isinstance(planned_acceptance_unit, dict)
                    and set(planned_acceptance_unit) == set(PLANNED_ACCEPTANCE_UNIT_FIELDS)):
                rows[8].append(f"increment {label}, acceptance unit {k}: not an object with the fields "
                               "acceptance_unit, depends_on and components (ACU-39)")
                continue
            acceptance_unit = planned_acceptance_unit["acceptance_unit"]
            if not _is_unit_id(acceptance_unit):
                rows[9].append(f"increment {label}, acceptance unit {k}: {_text_of(acceptance_unit)} is not a unit ID")
                continue
            planned.append(planned_acceptance_unit)
    for unit_id in _repeated([planned_acceptance_unit["acceptance_unit"] for planned_acceptance_unit in planned]):
        rows[10].append(f"{unit_id} is in plan.json twice (ACU-9)")
    for planned_acceptance_unit in planned:
        depends_on = planned_acceptance_unit["depends_on"]
        if not (isinstance(depends_on, list) and all(_is_unit_id(d) for d in depends_on)):
            rows[11].append(f"{planned_acceptance_unit['acceptance_unit']}: depends_on is not a list of unit IDs "
                            "(ACU-39)")
    for planned_acceptance_unit in planned:
        groups = planned_acceptance_unit["components"]
        if not (isinstance(groups, list) and groups and all(
                isinstance(g, list) and g and all(isinstance(c, str) for c in g) for g in groups)):
            rows[12].append(f"{planned_acceptance_unit['acceptance_unit']}: components is not a list of groups of "
                            "components (ACU-39)")
    if any(rows[row] for row in range(4, 13)):
        return [e for row in range(4, 13) for e in rows[row]], True, value
    for increment in increments:
        if not increment["acceptance_units"]:
            rows[13].append(f"increment {_text_of(increment['name'])} holds no acceptance unit (ACU-39)")
    before = set()
    for planned_acceptance_unit in planned:
        unit_id = planned_acceptance_unit["acceptance_unit"]
        if unit_id not in unit_ids_with_file:
            rows[14].append(f"{unit_id} is in plan.json and has no file units/{unit_id}.md")
        if unit_id in planned_acceptance_unit["depends_on"]:
            rows[15].append(f"{unit_id} depends on itself (ACU-39)")
        for dependency in _repeated(planned_acceptance_unit["depends_on"]):
            rows[16].append(f"{unit_id} depends on {dependency} twice (ACU-39)")
        for dependency in dict.fromkeys(planned_acceptance_unit["depends_on"]):
            if dependency != unit_id and dependency not in before:
                rows[17].append(f"{unit_id} depends on {dependency}, which does not come before it in plan.json "
                                "(ACU-42)")
        named = [c for group in planned_acceptance_unit["components"] for c in group]
        for component in dict.fromkeys(named):
            if component not in components:
                rows[18].append(f"{unit_id}: {_text_of(component)} is not a component of layer 4 of project.json (ACU-39)")
        for component in _repeated(named):
            rows[19].append(f"{unit_id}: component {_text_of(component)} is named twice (ACU-39)")
        before.add(unit_id)
    return [e for row in range(13, 20) for e in rows[row]], False, value


def canonical(plan):
    """A plan that passes the rows 1 to 12, with the keys in the order of ACU-39."""
    return {"increments": [{"name": increment["name"], "acceptance_units": [
        {"acceptance_unit": planned_acceptance_unit["acceptance_unit"],
         "depends_on": list(planned_acceptance_unit["depends_on"]),
         "components": [list(g) for g in planned_acceptance_unit["components"]]}
        for planned_acceptance_unit in increment["acceptance_units"]]}
        for increment in plan["increments"]]}


# ---------------------------------------------------------------- the inventory of the plan (PLN-4, PLN-6)

def norm_hashes_at(where, norms_commit):
    """The norm hash of each norm of data/tree.jsonl at the norms commit (active nodes only)."""
    data = show(where["norms_repository_path"], norms_commit, "data/tree.jsonl")
    try:
        nodes = checks.read_tree(data) if data is not None else None
    except (ValueError, UnicodeDecodeError):
        nodes = None
    if nodes is None:
        raise Stop(f"{where['norms_repository']}: data/tree.jsonl is not valid")
    found = {}
    for node in nodes:
        found.setdefault(node["id"], node["tree_hash"][:8].lower())
    return found


def _area_line(lines):
    """The area ID of the line "Area:" of an acceptance unit: the first line after the heading that is not empty."""
    for line in lines[1:]:
        if line.startswith("## "):
            return None
        if line != "":
            found = re.fullmatch(r"Area: (AA-[1-9][0-9]*)", line)
            return found.group(1) if found else None
    return None


def _unit_hash(data):
    try:
        return hashes.unit_hash(data) if data is not None else None
    except UnicodeDecodeError:
        return None


def read_acceptance_unit(unit_id, data, data_at_plan_commit, plan_commit, norm_hashes):
    acceptance_unit = {"unit_id": unit_id, "title": None, "area_id": None, "unit_hash": None,
                       "since_the_plan_commit": None, "behind_layer_2": False, "increment_name": None,
                       "position_in_current_plan": None}
    try:
        lines = hashes.lines_of(data)
        acceptance_unit["title"] = checks.heading_title(lines, unit_id)
        acceptance_unit["area_id"] = _area_line(lines)
        acceptance_unit["unit_hash"] = hashes.unit_hash(data)
        acceptance_unit["behind_layer_2"] = any(norm_hashes.get(norm_id) != norm_hash
                                                for norm_id, norm_hash, _ in hashes.norm_citations(data))
    except UnicodeDecodeError:
        pass
    if plan_commit is None or data_at_plan_commit is None:
        since = "added"
    else:
        before, now = _unit_hash(data_at_plan_commit), acceptance_unit["unit_hash"]
        since = "unchanged" if before is not None and before == now else "changed"
    acceptance_unit["since_the_plan_commit"] = since
    return acceptance_unit


def increment_of(plan):
    """The name of the increment of each planned acceptance unit, and its index."""
    found = {}
    for index, increment in enumerate(plan["increments"]):
        for planned_acceptance_unit in increment["acceptance_units"]:
            found.setdefault(planned_acceptance_unit["acceptance_unit"], (index, increment["name"]))
    return found


def scenario_increment(acceptance_units, increments_of_units):
    """ACU-29: the latest increment among the acceptance units that a scenario crosses, or None."""
    if not acceptance_units or any(u not in increments_of_units for u in acceptance_units):
        return None
    return max((increments_of_units[u] for u in acceptance_units), key=lambda index_and_name: index_and_name[0])[1]


def read_acceptance_area(area_id, data, increments_of_units):
    acceptance_area = {"area_id": area_id, "title": None, "scenarios": []}
    try:
        lines = hashes.lines_of(data)
        acceptance_area["title"] = checks.heading_title(lines, area_id)
        found = hashes.scenarios(data)
    except UnicodeDecodeError:
        return acceptance_area
    for scenario in found:
        crossed = list(dict.fromkeys(scenario.acceptance_units))
        acceptance_area["scenarios"].append({"scenario_id": scenario.scenario_id, "acceptance_units": crossed,
                                             "increment_name": scenario_increment(crossed, increments_of_units)})
    return acceptance_area


def inventory(where, norms_commit):
    """PLN-4: the inventory of the plan, at HEAD of the acceptance repository and at the plan commit."""
    root = where["root"]
    norm_hashes = norm_hashes_at(where, norms_commit)
    plan_bytes = show(root, "HEAD", "plan.json")
    # The plan commit (Terms): none when HEAD holds no plan.json, even when a commit deleted it.
    plan_commit = (out(root, "log", "-1", "--format=%H", "HEAD", "--", "plan.json") or None
                   if plan_bytes is not None else None)
    acceptance_unit_files, acceptance_area_files = {}, {}
    for path in ls_tree(root, "HEAD", "units", "areas"):
        match_of_acceptance_unit_file = ACCEPTANCE_UNIT_FILE.fullmatch(path)
        match_of_acceptance_area_file = ACCEPTANCE_AREA_FILE.fullmatch(path)
        if match_of_acceptance_unit_file:
            acceptance_unit_files[match_of_acceptance_unit_file.group(1)] = path
        elif match_of_acceptance_area_file:
            acceptance_area_files[match_of_acceptance_area_file.group(1)] = path
    acceptance_units = []
    for unit_id, path in sorted(acceptance_unit_files.items(), key=lambda kv: number(kv[0])):
        at_plan_commit = show(root, plan_commit, path) if plan_commit else None
        acceptance_units.append(read_acceptance_unit(unit_id, show(root, "HEAD", path) or b"", at_plan_commit,
                                                     plan_commit, norm_hashes))
    if plan_bytes is None:
        errors, error_of_reading, value = [], False, None
    else:
        errors, error_of_reading, value = check_plan(plan_bytes, set(acceptance_unit_files), where["components"])
    current_plan = canonical(value) if plan_bytes is not None and not error_of_reading else EMPTY_PLAN
    increments_of_units = increment_of(current_plan)
    positions = [unit_id for increment in current_plan["increments"] for unit_id in _unit_ids_of(increment)]
    for acceptance_unit in acceptance_units:
        unit_id = acceptance_unit["unit_id"]
        if unit_id in increments_of_units:
            acceptance_unit["increment_name"] = increments_of_units[unit_id][1]
            acceptance_unit["position_in_current_plan"] = positions.index(unit_id) + 1
    acceptance_areas = [read_acceptance_area(area_id, show(root, "HEAD", path) or b"", increments_of_units)
                        for area_id, path in sorted(acceptance_area_files.items(), key=lambda kv: number(kv[0]))]
    return {
        "norms_commit": norms_commit,
        "acceptance_commit": out(root, "rev-parse", "HEAD"),
        "plan_commit": plan_commit,
        "components": where["components"],
        "acceptance_areas": acceptance_areas,
        "acceptance_units": acceptance_units,
        "current_plan": current_plan,
        "plan_json_at_head": value if plan_bytes is not None else None,
        "errors": errors,
        "_plan_json_at_head_holds": plan_bytes is not None,
        "_error_of_reading": error_of_reading,
    }


def public(inventory_of_the_plan):
    return {k: v for k, v in inventory_of_the_plan.items() if not k.startswith("_")}


def summary(inventory_of_the_plan):
    """PLN-8: the line that sums up the inventory of the plan, and the errors of plan.json at HEAD."""
    acceptance_units = inventory_of_the_plan["acceptance_units"]
    errors = inventory_of_the_plan["errors"]
    planned = sum(u["increment_name"] is not None for u in acceptance_units)
    added = sum(u["since_the_plan_commit"] == "added" for u in acceptance_units)
    changed = sum(u["since_the_plan_commit"] == "changed" for u in acceptance_units)
    behind = sum(u["behind_layer_2"] for u in acceptance_units)
    increments = inventory_of_the_plan["current_plan"]["increments"]
    lines = [f"Layer 3 at {inventory_of_the_plan['acceptance_commit'][:7]}: "
             f"{plural(len(acceptance_units), 'acceptance unit')}, {planned} in the plan in "
             f"{plural(len(increments), 'increment')}; since the plan commit: "
             f"{added} added, {changed} changed; {behind} behind layer 2; "
             f"{plural(len(errors), 'error')} in plan.json."]
    if errors:
        lines.append("plan.json is not valid:")
        lines += [f"  {e}" for e in errors]
    return "\n".join(lines)


def nothing_to_plan(inventory_of_the_plan):
    """PLN-8: the message when HEAD holds no acceptance unit and no plan.json to change, or None."""
    empty = (not inventory_of_the_plan["_plan_json_at_head_holds"]
             or (not inventory_of_the_plan["errors"] and not inventory_of_the_plan["current_plan"]["increments"]))
    if not inventory_of_the_plan["acceptance_units"] and empty:
        return PREFIX + "no acceptance unit to plan"
    return None


def hand_off_errors(inventory_of_the_plan):
    """PLN-13: the lines said before a run goes on with a plan.json that has errors, or None."""
    if not inventory_of_the_plan["errors"]:
        return None
    return "\n".join([PREFIX + "the hand-off holds plan.json with errors:"]
                     + [f"  {e}" for e in inventory_of_the_plan["errors"]])


# ---------------------------------------------------------------- start (PLN-2)

def start(cwd, arguments):
    context, message = checks.run_checks(cwd, arguments)
    if message is not None:
        raise Stop(message)
    context["components"] = components_of(context["repositories"])
    message = components_message(context["components"])
    if message is not None:
        raise Stop(message)
    if not plan_json_is_regular(context["root"]):
        raise Stop("plan.json is not a regular file")
    message = plan_json_status(context["root"])
    if message is not None:
        raise Stop(message)
    inventory_of_the_plan = inventory(context, context["norms_commit"])
    return {"acceptance_repository": context["acceptance_repository"],
            "norms_repository": context["norms_repository"],
            "acceptance_default_branch": context["acceptance_default_branch"],
            "norms_default_branch": context["norms_default_branch"],
            "norms_commit": context["norms_commit"],
            "acceptance_commit": inventory_of_the_plan["acceptance_commit"],
            "plan_commit": inventory_of_the_plan["plan_commit"],
            "summary": summary(inventory_of_the_plan),
            "nothing_to_plan": nothing_to_plan(inventory_of_the_plan),
            "hand_off_errors": hand_off_errors(inventory_of_the_plan)}


# ---------------------------------------------------------------- the proposal of the plan (PLN-9, PLN-10)

def _unit_ids(ids):
    return ", ".join(ids) if ids else "none"


def _groups(groups):
    return " then ".join(f"[{', '.join(group)}]" for group in groups)


def _titled(unit_id, titles):
    title = titles.get(unit_id)
    return f'{unit_id} "{title}"' if title is not None else f"{unit_id} (no title)"


def _smallest_longest_kept(positions):
    """PLN-10: the indexes kept in place: the longest increasing subsequence of `positions`, and among those the one
    whose list of positions is the smallest, compared element by element."""
    n = len(positions)
    longest_from = [1] * n
    for i in range(n - 1, -1, -1):
        for j in range(i + 1, n):
            if positions[j] > positions[i]:
                longest_from[i] = max(longest_from[i], longest_from[j] + 1)
    kept, last, need, start = [], None, max(longest_from, default=0), 0
    while need:
        candidates = [i for i in range(start, n) if longest_from[i] == need
                      and (last is None or positions[i] > positions[last])]
        best = min(candidates, key=lambda i: positions[i])
        kept.append(best)
        last, start, need = best, best + 1, need - 1
    return set(kept)


def _renames(current, draft, rename_pairs):
    """The increment of the current plan that each increment of the draft is, by name or by a rename of the skill."""
    current_names = [increment["name"] for increment in current["increments"]]
    draft_names = [increment["name"] for increment in draft["increments"]]
    new_to_old = {}
    for old, new in rename_pairs:
        if old not in current_names or new not in draft_names or old in draft_names or new in current_names \
                or new in new_to_old or old in new_to_old.values():
            o, w = _quoted_name(old), _quoted_name(new)
            raise Stop(f"cannot rename increment {o} to {w}: the current plan must hold {o} and not {w}, "
                       f"and the draft {w} and not {o}")
        new_to_old[new] = old
    return {d: new_to_old.get(d, d if d in current_names else None) for d in draft_names}


def _quoted_name(name):
    """PLN-10, "A rename is the skill's choice": a name between double quotes, or its JSON text (PLN-5)."""
    text = _text_of(name)
    return f'"{text}"' if text == name else text


def _unit_ids_of(increment):
    return [planned_acceptance_unit["acceptance_unit"] for planned_acceptance_unit in increment["acceptance_units"]]


def changes_of_the_plan(inventory_of_the_plan, draft, rename_pairs):
    """PLN-10: the changes of the plan from the current plan to the draft, each (kind, line, unit ID or None), in
    the order of the kinds."""
    current = inventory_of_the_plan["current_plan"]
    titles = {u["unit_id"]: u["title"] for u in inventory_of_the_plan["acceptance_units"]}
    unit_ids_with_file = set(titles)
    matched = _renames(current, draft, rename_pairs)
    current_by_name = {increment["name"]: increment for increment in current["increments"]}
    planned_acceptance_units_in_current_plan = {
        planned_acceptance_unit["acceptance_unit"]: (increment["name"], planned_acceptance_unit)
        for increment in current["increments"] for planned_acceptance_unit in increment["acceptance_units"]}
    unit_ids_in_draft = {unit_id for increment in draft["increments"] for unit_id in _unit_ids_of(increment)}
    draft_names = [increment["name"] for increment in draft["increments"]]
    kinds = {k: [] for k in ("replace", "unplan_no_file", "add_increment", "rename_increment", "move_increment",
                             "delete_increment", "plan", "move", "change", "unplan")}

    def after(names, j):
        return f'after "{names[j - 1]}"' if j else "first"

    if inventory_of_the_plan["_error_of_reading"]:
        kinds["replace"].append((f"replace plan.json, which cannot be read: {inventory_of_the_plan['errors'][0]} "
                                 "(required)", None))
    for increment in current["increments"]:
        for unit_id in _unit_ids_of(increment):
            if unit_id not in unit_ids_in_draft and unit_id not in unit_ids_with_file:
                kinds["unplan_no_file"].append((f'unplan acceptance unit {unit_id} from "{increment["name"]}": no file '
                                                f"units/{unit_id}.md (required)", unit_id))
    for j, name in enumerate(draft_names):
        if matched[name] is None:
            kinds["add_increment"].append((f'add increment "{name}" {after(draft_names, j)}', None))
        elif matched[name] != name:
            kinds["rename_increment"].append((f'rename increment "{matched[name]}" to "{name}"', None))
    both = [(i, draft_names.index(d)) for i, increment in enumerate(current["increments"])
            for d in draft_names if matched[d] == increment["name"]]
    kept = _smallest_longest_kept([j for _, j in both])
    moved = {both[k][1] for k in range(len(both)) if k not in kept}
    for j, name in enumerate(draft_names):
        if j in moved:
            kinds["move_increment"].append((f'move increment "{name}" {after(draft_names, j)}', None))
    for increment in current["increments"]:
        if increment["name"] not in matched.values():
            kinds["delete_increment"].append((f'delete increment "{increment["name"]}"', None))
    for increment in draft["increments"]:
        unit_ids_in_draft_increment = _unit_ids_of(increment)
        old_name = matched[increment["name"]]
        unit_ids_in_current_increment = _unit_ids_of(current_by_name[old_name]) if old_name is not None else []
        acceptance_units_in_both = [
            (unit_ids_in_current_increment.index(unit_id), unit_ids_in_draft_increment.index(unit_id))
            for unit_id in unit_ids_in_current_increment if unit_id in unit_ids_in_draft_increment]
        kept_acceptance_units = _smallest_longest_kept([j for _, j in acceptance_units_in_both])
        moved_acceptance_units = {acceptance_units_in_both[k][1] for k in range(len(acceptance_units_in_both))
                                  if k not in kept_acceptance_units}

        def place(j):
            return f"after {unit_ids_in_draft_increment[j - 1]}" if j else "first"

        for j, planned_acceptance_unit in enumerate(increment["acceptance_units"]):
            unit_id = planned_acceptance_unit["acceptance_unit"]
            depends_on, components = planned_acceptance_unit["depends_on"], planned_acceptance_unit["components"]
            fields = f"depends on {_unit_ids(depends_on)}; components {_groups(components)}"
            if unit_id not in planned_acceptance_units_in_current_plan:
                kinds["plan"].append((f'plan acceptance unit {_titled(unit_id, titles)} in "{increment["name"]}" '
                                      f"{place(j)}: {fields}", unit_id))
                continue
            name_in_current_plan, before = planned_acceptance_units_in_current_plan[unit_id]
            if name_in_current_plan != old_name or j in moved_acceptance_units:
                kinds["move"].append((f'move acceptance unit {_titled(unit_id, titles)} to "{increment["name"]}" '
                                      f"{place(j)}", unit_id))
            differences = []
            if before["depends_on"] != depends_on:
                differences.append(f"depends on {_unit_ids(before['depends_on'])} -> {_unit_ids(depends_on)}")
            if before["components"] != components:
                differences.append(f"components {_groups(before['components'])} -> {_groups(components)}")
            if differences:
                removed = [d for d in before["depends_on"] if d not in depends_on]
                required = (before["components"] == components and removed
                            and all(d not in unit_ids_with_file for d in removed)
                            and depends_on == [d for d in before["depends_on"] if d not in removed])
                kinds["change"].append((f"change acceptance unit {_titled(unit_id, titles)}: {'; '.join(differences)}"
                                        + (" (required)" if required else ""), unit_id))
    for increment in current["increments"]:
        for unit_id in _unit_ids_of(increment):
            if unit_id not in unit_ids_in_draft and unit_id in unit_ids_with_file:
                kinds["unplan"].append((f'unplan acceptance unit {_titled(unit_id, titles)} from '
                                        f'"{increment["name"]}"', None))
    return [(kind, line, unit_id) for kind, found in kinds.items() for line, unit_id in found]


def rendering(inventory_of_the_plan, draft, rename_pairs):
    """PLN-9: the lines of the rendering of a draft that passes the checks of PLN-5."""
    current = inventory_of_the_plan["current_plan"]
    acceptance_units = inventory_of_the_plan["acceptance_units"]
    titles = {u["unit_id"]: u["title"] for u in acceptance_units}
    behind = {u["unit_id"] for u in acceptance_units if u["behind_layer_2"]}
    lines, n = ["Plan of implementation (draft):"], 0
    for increment in draft["increments"]:
        lines.append(f'Increment "{increment["name"]}"')
        for planned_acceptance_unit in increment["acceptance_units"]:
            n += 1
            unit_id = planned_acceptance_unit["acceptance_unit"]
            lines.append(f"  {n}. {_titled(unit_id, titles)}: depends on "
                         f"{_unit_ids(planned_acceptance_unit['depends_on'])}; components "
                         f"{_groups(planned_acceptance_unit['components'])}"
                         + ("; behind layer 2" if unit_id in behind else ""))
    increment_of_acceptance_unit_in_draft = increment_of(draft)
    increment_of_acceptance_unit_in_current_plan = increment_of(current)
    not_planned = [_titled(u["unit_id"], titles) for u in acceptance_units
                   if u["unit_id"] not in increment_of_acceptance_unit_in_draft]
    if not_planned:
        lines.append(f"Not planned: {', '.join(not_planned)}")
    removed = sorted((u for u in increment_of_acceptance_unit_in_current_plan
                      if u not in increment_of_acceptance_unit_in_draft), key=number)
    if removed:
        lines.append(f"Removed: {', '.join(removed)}")
    matched = _renames(current, draft, rename_pairs)
    moving, received_scenarios = [], {}
    for area in inventory_of_the_plan["acceptance_areas"]:
        with_id = sorted((s for s in area["scenarios"] if s["scenario_id"]), key=lambda s: number(s["scenario_id"]))
        without_id = [s for s in area["scenarios"] if not s["scenario_id"]]
        for scenario in with_id + without_id:
            before = scenario_increment(scenario["acceptance_units"], increment_of_acceptance_unit_in_current_plan)
            now = scenario_increment(scenario["acceptance_units"], increment_of_acceptance_unit_in_draft)
            # A renamed increment is the same increment (PLN-10): compare with the name it has in the current plan.
            # A new increment has no such name, and its name is no name of the current plan.
            if before != (matched[now] or now if now is not None else None):
                label = f"{scenario['scenario_id'] or '(no ID)'} of {area['area_id']}"
                moving.append(f"  {label}: {_quoted(before)} -> {_quoted(now)}")
                if now is not None:
                    received_scenarios.setdefault(now, []).append(label)
    if moving:
        lines.append("Scenarios of acceptance areas that change increment:")
        lines += moving
    current_by_name = {increment["name"]: increment for increment in current["increments"]}
    for increment in draft["increments"]:
        old_name = matched[increment["name"]]
        if old_name is None:
            continue
        held = set(_unit_ids_of(current_by_name[old_name]))
        received = [unit_id for unit_id in _unit_ids_of(increment) if unit_id not in held]
        received += received_scenarios.get(increment["name"], [])
        if received:
            lines.append(f'Warning: increment "{increment["name"]}" receives {", ".join(received)}; if it was done, '
                         "it stops being done (ACU-31).")
    return lines


def _quoted(name):
    return f'"{name}"' if name is not None else "none"


def no_change_message(inventory_of_the_plan):
    """PLN-8: the message when the draft holds no change of the plan."""
    reviewed = [u["unit_id"] for u in inventory_of_the_plan["acceptance_units"]
                if u["since_the_plan_commit"] in ("added", "changed")]
    if reviewed:
        return PREFIX + "no change to propose; reviewed " + ", ".join(reviewed)
    return PREFIX + "no change to propose"


def read_draft(path):
    try:
        with open(path, "rb") as f:
            return f.read()
    except OSError:
        raise Stop(f"cannot read the draft {path}")


def _unit_ids_with_file(inventory_of_the_plan):
    return {u["unit_id"] for u in inventory_of_the_plan["acceptance_units"]}


def checked_draft(where, inventory_of_the_plan, data):
    """The draft as a plan in the order of ACU-39, or Stop with its errors of PLN-5, one per line."""
    errors, _, value = check_plan(data, _unit_ids_with_file(inventory_of_the_plan), where["components"])
    if errors:
        raise Errors(errors)
    return canonical(value)


def propose(where, norms_commit, draft_path, rename_pairs):
    inventory_of_the_plan = inventory(where, norms_commit)
    draft = checked_draft(where, inventory_of_the_plan, read_draft(draft_path))
    found = changes_of_the_plan(inventory_of_the_plan, draft, rename_pairs)
    if not found:
        raise Said(no_change_message(inventory_of_the_plan), code=4)
    lines = rendering(inventory_of_the_plan, draft, rename_pairs) + ["Changes:"]
    lines += [f"  {k}. {line}" for k, (_, line, _) in enumerate(found, 1)]
    return "\n".join(lines)


def kept_error(where, norms_commit, draft_path):
    """PLN-8: the message of a rejected required change of the plan, or None when no error of PLN-5 is left."""
    inventory_of_the_plan = inventory(where, norms_commit)
    if draft_path is None:
        errors = inventory_of_the_plan["errors"]
    else:
        errors = check_plan(read_draft(draft_path), _unit_ids_with_file(inventory_of_the_plan),
                            where["components"])[0]
    if not errors:
        return None
    return (PREFIX + f"without this change plan.json keeps the error {errors[0]} (PLN-5); reject the whole proposal "
            "to keep plan.json as it is.")


# ---------------------------------------------------------------- write, commit, rollback (PLN-11, PLN-12, PLN-13)

def plan_json_form(value, indent=0):
    """PLN-11: the JSON of a plan, indented by 2 spaces per level, every object and every list on lines of their own
    except a list of strings and an empty list."""
    pad = " " * indent
    if isinstance(value, list) and (not value or all(isinstance(v, str) for v in value)):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list):
        return "[\n" + ",\n".join(f"{pad}  {plan_json_form(v, indent + 2)}" for v in value) + f"\n{pad}]"
    if isinstance(value, dict):
        return "{\n" + ",\n".join(f"{pad}  {json.dumps(k, ensure_ascii=False)}: {plan_json_form(v, indent + 2)}"
                                  for k, v in value.items()) + f"\n{pad}}}"
    return json.dumps(value, ensure_ascii=False)


def plan_json_bytes(plan):
    return (plan_json_form(canonical(plan)) + "\n").encode("utf-8")


def _plan_json_kind(root):
    """What the working tree holds at plan.json, never following a symbolic link: "file" (a regular file only),
    "link", "folder", "other" (a FIFO, a socket or a device) or None."""
    try:
        mode = os.lstat(os.path.join(root, "plan.json")).st_mode
    except FileNotFoundError:
        return None
    if stat.S_ISREG(mode):
        return "file"
    if stat.S_ISLNK(mode):
        return "link"
    if stat.S_ISDIR(mode):
        return "folder"
    return "other"


def _write_plan_json(root, data):
    """Writes plan.json as a regular file of the acceptance repository (PLN-11, "Only a regular file"): anything else
    at plan.json raises OSError, no symbolic link is ever followed, and no FIFO is waited on (O_NONBLOCK, which
    changes nothing for a regular file)."""
    path = os.path.join(root, "plan.json")
    if _plan_json_kind(root) not in (None, "file"):
        raise OSError("plan.json is not a regular file")
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NONBLOCK
                         | getattr(os, "O_NOFOLLOW", 0), 0o644)
    with os.fdopen(descriptor, "wb") as f:
        f.write(data)


def _read_plan_json(root):
    """The bytes of plan.json in the working tree, never through a symbolic link; OSError when it is no file."""
    if _plan_json_kind(root) != "file":
        raise OSError("plan.json is no file")
    descriptor = os.open(os.path.join(root, "plan.json"), os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0))
    with os.fdopen(descriptor, "rb") as f:
        return f.read()


def rollback(root):
    """PLN-12: plan.json as HEAD holds it, or removed when HEAD holds none, in the working tree and in the index,
    touching no other path: the index with "git update-index --cacheinfo" or "git rm --cached" of plan.json only
    (PLN-14). Only a regular file is written or removed; anything else at plan.json is left as it is."""
    entry = out(root, "ls-tree", "HEAD", "--", "plan.json")
    if not entry:
        if git(root, "ls-files", "--error-unmatch", "--", "plan.json").returncode == 0:
            git(root, "rm", "-q", "--cached", "--", "plan.json")
        if _plan_json_kind(root) == "file":
            os.remove(os.path.join(root, "plan.json"))
        return
    mode, _, blob = entry.split("\t")[0].split()
    if mode not in ("100644", "100755"):
        return
    if _plan_json_kind(root) in (None, "file"):
        _write_plan_json(root, show(root, "HEAD", "plan.json"))
    git(root, "update-index", "--cacheinfo", f"{mode},{blob},plan.json")


def write(where, norms_commit, draft_path):
    """PLN-11: writes plan.json from the draft, then checks it; on an error, puts it back and stops."""
    inventory_of_the_plan = inventory(where, norms_commit)
    draft = checked_draft(where, inventory_of_the_plan, read_draft(draft_path))
    root = where["root"]
    written = plan_json_bytes(draft)
    # PLN-11, "Only a regular file": another process made plan.json something else since PLN-2; nothing is written,
    # so there is nothing to put back, and the index is left as it is.
    if _plan_json_kind(root) not in (None, "file"):
        raise Stop("cannot write plan.json")
    try:
        _write_plan_json(root, written)
        errors = check_plan(_read_plan_json(root), _unit_ids_with_file(inventory_of_the_plan),
                            where["components"])[0]
    except OSError:
        rollback(root)
        raise Stop("cannot write plan.json")
    if errors:
        rollback(root)
        raise Errors(errors)
    return "plan.json"


def unified(old, new):
    a = (old or b"").decode("utf-8", "replace").splitlines(keepends=True)
    b = (new or b"").decode("utf-8", "replace").splitlines(keepends=True)
    head = "new " if old is None else ""
    lines = list(difflib.unified_diff(a, b, "/dev/null" if old is None else "a/plan.json", "b/plan.json"))
    return f"{head}plan.json\n" + "".join(line if line.endswith("\n") else line + "\n" for line in lines)


def next_line(inventory_of_the_plan, final, found):
    """PLN-13: the line "Next: ..." after the commit is pushed, or None."""
    behind = {u["unit_id"] for u in inventory_of_the_plan["acceptance_units"] if u["behind_layer_2"]}
    planned = increment_of(final)
    parts = []
    behind_planned = sorted((u for u in planned if u in behind), key=number)
    if behind_planned:
        parts.append(f"the acceptance architect updates {', '.join(behind_planned)} with /acceptance-management:define")
    touched = {unit_id for kind, _, unit_id in found if kind in ("plan", "move", "change")}
    if touched:
        named = {c for increment in final["increments"] for planned_acceptance_unit in increment["acceptance_units"]
                 if planned_acceptance_unit["acceptance_unit"] in touched
                 for group in planned_acceptance_unit["components"] for c in group}
        components = [c for c in inventory_of_the_plan["components"] if c in named]
        parts.append(f"the implementing agents of {', '.join(components)} implement the plan with "
                     "/code-implementation:implement")
    return f"Next: {'; '.join(parts)}." if parts else None


def commit(where, norms_commit, acceptance_commit, rename_pairs):
    """PLN-12: the diff, the message, the one command that fetches, stages, commits and pushes, and the next line.

    `acceptance_commit` is HEAD at `start`: the proposal of the plan was made from it, and a commit that another
    session adds to HEAD after it must never be pushed with the commit of plan.json (ACU-75). The command stages
    plan.json with -f, so that a .gitignore that names it does not refuse it; with one path, -f stages only it."""
    root, name = where["root"], where["acceptance_repository"]
    norms_path, norms_name = where["norms_repository_path"], where["norms_repository"]
    # PLN-12, rows 1 to 3 of "The other stops before the command": the norms repository has not moved since `start`.
    if git(norms_path, "fetch", "-q", "origin").returncode != 0:
        raise Stop(f"cannot fetch {norms_name}", code=3)
    norms_branch = checks.default_branch(norms_path)
    if not norms_branch:
        raise Stop(f"cannot find the default branch of {norms_name}", code=3)
    if out(norms_path, "rev-parse", "-q", "--verify", f"refs/remotes/origin/{norms_branch}^{{commit}}") != norms_commit:
        raise Stop(f"the norms commit {norms_commit} is not the head of the default branch of origin in {norms_name}; "
                   "run the skill again", code=3)
    # ACU-75, in its order.
    if git(root, "fetch", "-q", "origin").returncode != 0:
        raise Stop(f"cannot fetch {name}", code=3)
    branch = checks.default_branch(root)
    if not branch:
        raise Stop(f"cannot find the default branch of {name}", code=3)
    if out(root, "rev-list", "--count", f"HEAD..refs/remotes/origin/{branch}") != "0":
        raise Stop(f"origin/{branch} moved; run the skill again", code=3)
    if out(root, "rev-list", "--count", f"refs/remotes/origin/{branch}..HEAD") != "0":
        raise Stop(f"the acceptance repository has commits that are not on origin/{branch}", code=3)
    if out(root, "rev-parse", "HEAD") != acceptance_commit:
        raise Stop(f"origin/{branch} moved; run the skill again", code=3)
    inventory_of_the_plan = inventory(where, norms_commit)
    try:
        written = _read_plan_json(root)
    except OSError:
        raise Stop("plan.json is not written; run the skill again")
    errors, _, value = check_plan(written, _unit_ids_with_file(inventory_of_the_plan), where["components"])
    if errors:
        raise Errors(errors)
    final = canonical(value)
    if written != plan_json_bytes(final):
        raise Stop("plan.json is not in the form of PLN-11; run the skill again")
    found = changes_of_the_plan(inventory_of_the_plan, final, rename_pairs)
    if not found:
        raise Said(no_change_message(inventory_of_the_plan), code=4)
    at_head = show(root, "HEAD", "plan.json")
    subject = ("docs: change the plan of implementation" if at_head is not None
               else "docs: add the plan of implementation")
    body = "\n".join(line for _, line, _ in found)
    r = shlex.quote(root)
    g = f"git --literal-pathspecs -C {r}"
    cannot = shlex.quote(PREFIX + f"cannot fetch {name}")
    moved = shlex.quote(PREFIX + f"origin/{branch} moved; run the skill again")
    behind = shlex.quote(f"HEAD..refs/remotes/origin/{branch}")
    ahead = shlex.quote(f"refs/remotes/origin/{branch}..HEAD")
    not_on_origin = shlex.quote(PREFIX + f"the acceptance repository has commits that are not on origin/{branch}")
    rejected_before = shlex.quote(PREFIX + "push rejected; commit ")
    rejected_after = shlex.quote(f" is not on origin/{branch}; run git pull --rebase, then git push, and run the "
                                 "skill again")
    # PLN-12: the command fetches again first, so that a move of the default branch, or a commit that another
    # session adds to HEAD, while the requester reads the diff stops it, with status 3, before it stages anything.
    command = (f"{{ git -C {r} fetch -q origin 2>/dev/null || {{ echo {cannot}; (exit 3); }}; }}"
               f" && {{ test \"$(git -C {r} rev-list --count {behind})\" = 0 || {{ echo {moved}; (exit 3); }}; }}"
               f" && {{ test \"$(git -C {r} rev-list --count {ahead})\" = 0"
               f" || {{ echo {not_on_origin}; (exit 3); }}; }}"
               f" && {{ test \"$(git -C {r} rev-parse HEAD)\" = {shlex.quote(acceptance_commit)}"
               f" || {{ echo {moved}; (exit 3); }}; }}"
               f" && {g} add -f -- plan.json && {g} commit -q -m {shlex.quote(subject)} -m {shlex.quote(body)}"
               f" -- plan.json"
               f" && {{ git -C {r} push -q origin {shlex.quote('HEAD:' + branch)} 2>/dev/null || {{ echo {rejected_before}"
               f"\"$(git -C {r} rev-parse HEAD | cut -c1-7)\"{rejected_after}; (exit 4); }}; }}")
    display = "\n".join(["Diff:", "", unified(at_head, written), "Commit:", f"    {subject}", ""]
                        + [f"    {line}" for line in body.split("\n")])
    return {"display": display, "message": f"{subject}\n\n{body}", "command": command,
            "acceptance_default_branch": branch,
            "next": next_line(inventory_of_the_plan, final, found)}


# ---------------------------------------------------------------- main

OPTIONS = {"--norms-commit": 1, "--draft": 1, "--acceptance-commit": 1, "--rename": 2}


def options_of(arguments):
    """The options after REPO, read in one pass from left to right: each option takes the values that follow it, so
    a value is never read as an option, even when it is the name of one, such as an increment named "--rename"."""
    found = {name: [] for name in OPTIONS}
    position = 0
    while position < len(arguments):
        name = arguments[position]
        if name not in OPTIONS:
            raise Stop(f"unknown argument {name}")
        count = OPTIONS[name]
        values = arguments[position + 1:position + 1 + count]
        if len(values) != count:
            raise Stop("--rename takes the old name and the new name" if name == "--rename"
                       else f"{name} takes a value")
        found[name].append(values[0] if count == 1 else tuple(values))
        position += 1 + count
    return found


def option(options, name):
    if len(options[name]) != 1:
        raise Stop(f"{name} is required")
    return options[name][0]


def norms_commit_of(where, options):
    """The option --norms-commit: 40 lower-case hex digits that name a commit of the norms repository (PLN-3), never a
    branch, HEAD or a short SHA. That origin moved since `start` does not stop the reading, which stays at that
    commit; only `commit` stops when it moved (row 3 of PLN-12)."""
    sha = option(options, "--norms-commit")
    if not re.fullmatch(r"[0-9a-f]{40}", sha) or git(where["norms_repository_path"], "cat-file", "-e",
                                                      f"{sha}^{{commit}}").returncode != 0:
        raise Stop(f"--norms-commit {sha} is not a commit of {where['norms_repository']}")
    return sha


def main(argv):
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    command, args = argv[0], argv[1:]
    if not args:
        raise Stop(f"{command}: REPO is required")
    repo, rest = args[0], args[1:]
    if command == "start":
        extra = rest[1:] if rest[:1] == ["--"] else rest
        print(json.dumps(start(repo, extra), ensure_ascii=False))
        return 0
    where = locate(repo)
    if command == "rollback":
        rollback(where["root"])
        return 0
    options = options_of(rest)
    if command == "commit":
        # PLN-12: commit checks the norms commit against origin after a fetch (rows 1 to 3), not with the local refs.
        print(json.dumps(commit(where, option(options, "--norms-commit"), option(options, "--acceptance-commit"),
                                options["--rename"]), ensure_ascii=False))
        return 0
    norms_commit = norms_commit_of(where, options)
    if command == "inventory":
        print(json.dumps(public(inventory(where, norms_commit)), ensure_ascii=False))
        return 0
    if command == "propose":
        print(propose(where, norms_commit, option(options, "--draft"), options["--rename"]))
        return 0
    if command == "kept-error":
        drafts = options["--draft"]
        message = kept_error(where, norms_commit, drafts[0] if drafts else None)
        if message:
            print(message)
        return 0
    if command == "write":
        print(write(where, norms_commit, option(options, "--draft")))
        return 0
    raise Stop(f"unknown command {command}")


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Stop as stop:
        print(str(stop) if isinstance(stop, (Errors, Said)) else PREFIX + str(stop))
        sys.exit(stop.code)
