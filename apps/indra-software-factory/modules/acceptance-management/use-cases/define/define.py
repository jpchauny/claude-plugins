"""The script of the use case define of acceptance-management, with no model (ACU-57 to ACU-73).

Spec: specs/define.md of this folder, and specs/module.md of the module. The
fingerprints (ACU-51 to ACU-54) are those of scripts/acceptance_hashes.py of the
module; the checks that every use case of the module shares (ACU-74), the
checks before a commit, the commit command and the diff of a file of a
commit (ACU-75) those of
scripts/acceptance_repository_checks.py; and the inventory (ACU-60 to ACU-62:
the norms, the files of areas/ and units/, their format errors and the
citation statuses, and the ID fields of ACU-55 and ACU-61) that of
scripts/acceptance_repository_files.py, which write-acceptance-tests reads
too. This script imports all three.

Usage (REPO is the working directory of the skill; every command reads, and
only `ids`, `fill`, `delete-tests` and `rollback` write, in the acceptance
repository only):

    define.py start REPO [-- ARG...]
        ACU-74, then ACU-58: the checks, in their order, with the fetch of
        both repositories; on the first that fails, prints
        "acceptance-management:define: <message>" and exits 1. Otherwise
        prints one JSON object: "acceptance_repository" and
        "norms_repository" (<owner>/<name>), "specs_repository" (<owner>/<name>
        of the entry of layer 1, or null), "acceptance_default_branch" and
        "norms_default_branch", "norms_commit", "acceptance_commit",
        "summary" (the line of ACU-64), "empty_fields_of_acceptance_json"
        ("test_command" and "product" when each is empty at HEAD, ACU-77) and
        "code_repositories" (<owner>/<name> of each entry of layer 4 of
        project.json, in its order).
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
    define.py fill REPO FILE [--dry-run]
        ACU-77: FILE, outside the repository, is one JSON object with the
        values that the requester stated, "test_command" and/or "product".
        Checks each value; on a problem prints one line
        "acceptance-management:define: <message>" per problem and exits 1.
        With --dry-run prints a JSON object: "change" (the line of the change,
        or null when FILE fills nothing), "lines" (the lines under it) and
        "fields_left_empty" (the message of each field that stays empty).
        Without it writes the values into acceptance.json on disk, nothing
        else, and prints the fields filled.
    define.py delete-tests REPO UNIT_ID
        ACU-10, ACU-70: deletes from the working tree each file of
        tests/<unit ID>/ that HEAD holds.
    define.py commit REPO --norms-commit SHA --expected-head SHA --change "<verb> <ID>"...
        (a change is "add", "change" or "delete" and an area ID or a unit ID,
        or "fill acceptance.json")
        ACU-71, ACU-75: fetches; when the fetch fails, the default branch
        cannot be found, origin/<branch> moved, HEAD holds a commit that
        origin/<branch> does not, or HEAD is not the expected head, prints the
        message and exits 3. Runs `check`; refuses a deleted acceptance unit whose
        tests/<unit ID>/ is still there (ACU-70), and a file of areas/ or
        units/ that belongs to no change. Prints a JSON object: "display" (the whole diff and the
        message), "paths", "message" and "command", which fetches again and
        exits 3 with the same messages, and otherwise stages each path by
        name, commits only them, and pushes to the default branch; a rejected
        push prints the message of ACU-75 and exits 4, and a pushed commit
        prints its 40 hex digits as the last line, the expected head of the
        next command.
    define.py rollback REPO [--change "<verb> <ID>"...]
        ACU-71: puts each file of areas/, units/ and acceptance.json back as
        HEAD holds it, removes the new ones, and gives back the files of
        tests/<unit ID>/ of each "delete <unit ID>", in the working tree and,
        for those paths only, in the index.
    define.py next REPO --since SHA
        ACU-72: prints the line "Next: ..." for the commits from SHA to HEAD,
        or nothing; SHA must be a commit in the history of HEAD.
    define.py hash FILE...
        Prints the unit hash, the area hash and the scenarios, each with its
        scenario hash, of each file, wherever it is, as ACU-52 to ACU-54
        compute them.

Never runs git stash, reset, checkout, restore or clean (ACU-73); never
changes the working tree, the index or a local branch of the norms repository
(ACU-59). --norms-commit is 40 lower-case hex digits, the head of a branch of
origin of the norms repository. Python 3.9 or later, standard library only.
The names of the JSON keys and of the identifiers follow the terms of the
specs: "acceptance_unit", "acceptance_area", "unit_hash", "norm_citations"...
"""

from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(HERE)), "scripts")
sys.path.insert(0, SCRIPTS)
sys.dont_write_bytecode = True

import acceptance_hashes as hashes  # noqa: E402
import acceptance_repository_checks as checks  # noqa: E402
from acceptance_repository_checks import git, ls_tree, out, show  # noqa: E402
from acceptance_repository_files import (ACCEPTANCE_AREA_FILE, ACCEPTANCE_UNIT_FILE, ID_FIELDS, Layer3,  # noqa: E402
                                         acceptance_ok, expected_fields, field_line, inventory, number, plural,
                                         public, read_norms)

PREFIX = "acceptance-management:define: "
CHANGE = re.compile(r"(add|change|delete) ((?:AA|AU)-[1-9][0-9]*)")
FILL_CHANGE = ("fill", "acceptance.json")  # ACU-77: the change that fills test_command and product
FILLABLE_FIELDS = ("test_command", "product")  # ACU-43, ACU-77: filled by define only while empty at HEAD


class Stop(Exception):
    """A refusal: its message is said after PREFIX, and the command exits with `code`."""

    def __init__(self, message, code=1):
        super().__init__(message)
        self.code = code


# ---------------------------------------------------------------- where the repositories are

def locate(cwd):
    """ORC-20, ORC-21: the acceptance repository, the norms repository and the specs repository, as rows 2 and 3 of
    ACU-74 find them in scripts/acceptance_repository_checks.py; raises Stop with the message of the row that
    fails."""
    try:
        return checks.locate(cwd)
    except checks.Refusal as refusal:
        raise Stop(refusal.message)


# ---------------------------------------------------------------- the summary (ACU-64)

def summary(inv):
    """ACU-64: the line that sums up the inventory."""
    norm_citations = [c for u in inv["acceptance_units"] for c in u["norm_citations"]]
    changed = sum(c["citation_status"] == "changed" for c in norm_citations)
    retired = sum(c["citation_status"] == "retired" for c in norm_citations)
    errors = len(inv["errors"]) + sum(len(x["errors"]) for x in inv["acceptance_areas"] + inv["acceptance_units"])
    return (f"Layer 2 at {inv['norms_commit'][:7]}: {plural(len(inv['norms']), 'norm')}. "
            f"Layer 3 at {inv['acceptance_commit'][:7]}: {plural(len(inv['acceptance_areas']), 'acceptance area')}, "
            f"{plural(len(inv['acceptance_units']), 'acceptance unit')}; "
            f"{plural(changed, 'norm citation')} changed, {retired} retired; {plural(errors, 'format error')}.")


# ---------------------------------------------------------------- start (ACU-74, ACU-58)

def start(cwd, args):
    """ACU-74, then ACU-58: the checks, in their order; the first that fails ends the skill."""
    where, message = checks.run_checks(cwd, args)
    if message is not None:
        raise Stop(message)
    root = where["root"]
    changed, untracked = status(root)
    if changed:
        raise Stop(f"uncommitted change in {checks.text_of(changed[0])}")
    if untracked:
        raise Stop(f"untracked file {checks.text_of(untracked[0])}")
    acceptance_at_head = acceptance_ok(show(root, "HEAD", "acceptance.json") or b"")
    if acceptance_at_head is None:
        raise Stop("acceptance.json does not meet ACU-6")
    inv = inventory(where, where["norms_commit"])
    return {"acceptance_repository": where["acceptance_repository"], "norms_repository": where["norms_repository"],
            "specs_repository": where["specs_repository"],
            "acceptance_default_branch": where["acceptance_default_branch"],
            "norms_default_branch": where["norms_default_branch"], "norms_commit": where["norms_commit"],
            "acceptance_commit": inv["acceptance_commit"], "summary": summary(inv),
            "empty_fields_of_acceptance_json": [field for field in FILLABLE_FIELDS
                                                if is_empty(acceptance_at_head[field])],
            "code_repositories": code_repositories(where)}


# ---------------------------------------------------------------- fill acceptance.json (ACU-43, ACU-77)

def is_empty(value):
    """ACU-6: test_command is empty as the empty string, product as the empty object."""
    return value == "" or value == {}


def code_repositories(where):
    """<owner>/<name> of each entry of layer 4 of project.json, in its order."""
    return checks.code_repositories(where["repositories"])


def fill_problems(where, acceptance_at_head, values):
    """ACU-77: the message of each value that ACU-77 refuses, in the order of the fields and of the entries; the checks
    of the values are those of the module (scripts/acceptance_repository_checks.py), which write-acceptance-tests
    makes on the values at HEAD (WAT-2)."""
    problems = [f"{field} of acceptance.json is not empty; define fills only an empty field (ACU-43)"
                for field in FILLABLE_FIELDS if field in values and not is_empty(acceptance_at_head[field])]
    checked = {field: values[field] for field in FILLABLE_FIELDS
               if field in values and is_empty(acceptance_at_head[field])}
    return problems + checks.problems_of_values(code_repositories(where), checked)


def fill_proposal(where, acceptance_at_head, values):
    """ACU-77: the line of the change, the lines under it (its values and those of ACU-49), and the message of each
    field that stays empty."""
    text_of = checks.text_of
    filled = [field for field in FILLABLE_FIELDS if field in values]
    lines = []
    if "test_command" in values:
        lines.append(f"test_command: {text_of(values['test_command'])}")
    if "product" in values:
        product = values["product"]
        for key, entry in product.items():
            line = f"product {text_of(key)}: build {text_of(entry['build'])}; env {text_of(entry['env'])}"
            if "published" in entry:
                line += f"; published {text_of(entry['published'])}"
            lines.append(line)
        known = code_repositories(where)
        for repository in known:
            if repository not in product:
                lines.append(f"{text_of(repository)} has no entry in product: its implementing agent runs no "
                             "acceptance test (ACU-49)")
        for repository in known:
            if repository in product and "published" not in product[repository]:
                others = [r for r in known if r in product and r != repository]
                if others:
                    lines.append(f"{text_of(repository)} has no published: no acceptance test runs in the tasks of "
                                 f"{', '.join(text_of(other) for other in others)} (ACU-49)")
    left_empty = [PREFIX + f"acceptance.json keeps {field} empty; /acceptance-management:write-acceptance-tests "
                  "stops until define fills it (WAT-2)"
                  for field in FILLABLE_FIELDS if is_empty(acceptance_at_head[field]) and field not in values]
    return {"change": f"fill acceptance.json: {', '.join(filled)}" if filled else None, "lines": lines,
            "fields_left_empty": left_empty}


def read_fill_values(path):
    """The values that the requester stated: one JSON object of test_command and/or product."""
    try:
        with open(path, "rb") as f:
            values = json.loads(f.read().decode("utf-8"))
    except (OSError, ValueError, UnicodeDecodeError, RecursionError):
        values = None
    if not isinstance(values, dict) or not set(values) <= set(FILLABLE_FIELDS):
        raise Stop(f"{checks.text_of(path)} is not one JSON object of test_command and product")
    return values


def fill(where, path, dry_run):
    """ACU-77: checks the values; with dry_run, the proposal of the change; otherwise writes them into acceptance.json
    on disk, changing only the bytes of the empty fields."""
    root = where["root"]
    values = read_fill_values(path)
    acceptance_at_head = acceptance_ok(show(root, "HEAD", "acceptance.json") or b"")
    if acceptance_at_head is None:
        raise Stop("acceptance.json does not meet ACU-6")
    problems = fill_problems(where, acceptance_at_head, values)
    if problems:
        raise Stop(("\n" + PREFIX).join(problems))
    if dry_run:
        return fill_proposal(where, acceptance_at_head, values)
    disk_path = os.path.join(root, "acceptance.json")
    with open(disk_path, "rb") as f:
        data = f.read()
    on_disk = acceptance_ok(data)
    if on_disk is None:
        raise Stop("acceptance.json does not meet ACU-6")
    text = data.decode("utf-8")
    filled = []
    for field in FILLABLE_FIELDS:
        if field not in values or on_disk[field] == values[field]:
            continue
        empty = '""' if field == "test_command" else r"\{\s*\}"
        pattern = re.compile(r'("' + field + r'"\s*:\s*)' + empty)
        if not is_empty(on_disk[field]) or len(pattern.findall(text)) != 1:
            raise Stop(f"cannot fill {field} of acceptance.json")
        value = json.dumps(values[field], ensure_ascii=False)
        text = pattern.sub(lambda m: m.group(1) + value, text)
        filled.append(field)
    written_object = acceptance_ok(text.encode("utf-8"))
    if written_object is None or any(written_object[f] != values.get(f, on_disk[f]) for f in FILLABLE_FIELDS):
        raise Stop("cannot fill acceptance.json")
    if filled:
        with open(disk_path, "wb") as f:
            f.write(text.encode("utf-8"))
    return filled


def status(root):
    """ACU-58, after the checks of ACU-74: the paths with an uncommitted change among acceptance.json, areas/ and units/, and the untracked
    files under areas/ and units/, each in sorted order. An untracked file that a .gitignore names is untracked too
    (--ignored=traditional, which with --untracked-files=all lists each file of an ignored folder), since the
    inventory of the working tree reads it and the command stages it with -f."""
    done = git(root, "status", "--porcelain=v1", "-z", "--no-renames", "--untracked-files=all",
               "--ignored=traditional", "--", "acceptance.json", "areas", "units", binary=True)
    changed, untracked = [], []
    for entry in done.stdout.split(b"\0"):
        if len(entry) < 4:
            continue
        code, path = entry[:2].decode(), entry[3:].decode("utf-8", "surrogateescape")
        if code in ("??", "!!"):
            (changed if path == "acceptance.json" else untracked).append(path)
        else:
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
    for acceptance_unit in after["acceptance_units"]:
        if acceptance_unit["path"] in paths:
            for c in acceptance_unit["norm_citations"]:
                if c["citation_status"] != "current":
                    now = c["hash_in_norms_repository"] or "none: the norm is not in layer 2"
                    problems.append({"path": acceptance_unit["path"], "line": c["_line"],
                                     "message": f"{c['norm_id']}@{c['hash_in_acceptance_unit']} is "
                                                f"{c['citation_status']}; its norm hash at the norms commit is {now}"})
    old = {(e["path"], e["message"]) for e in before["errors"]}
    for x in before["acceptance_areas"] + before["acceptance_units"]:
        old |= {(x["path"], e["message"]) for e in x["errors"]}
    for e in after["errors"]:
        if e["path"] in paths or (e["path"], e["message"]) not in old:
            problems.append(e)
    for x in after["acceptance_areas"] + after["acceptance_units"]:
        for e in x["errors"]:
            if x["path"] in paths or (x["path"], e["message"]) not in old:
                problems.append({"path": x["path"], "line": e["line"], "message": e["message"]})
    for path, old_bytes, new_bytes in files:
        if path == "acceptance.json":
            a, b = acceptance_ok(old_bytes or b""), acceptance_ok(new_bytes or b"")
            if not (a and b):
                continue
            # ACU-73, ACU-77: besides the ID fields, only test_command and product, while they are empty at HEAD,
            # with values that ACU-77 does not refuse.
            if a["default_done_profile"] != b["default_done_profile"] or any(
                    a[k] != b[k] and not is_empty(a[k]) for k in FILLABLE_FIELDS):
                problems.append({"path": path, "line": None, "message":
                                 "only last_area_id, last_unit_id and last_scenario_id, and test_command and product "
                                 "while they are empty at HEAD, may change (ACU-73)"})
            for field in FILLABLE_FIELDS:
                if a[field] != b[field] and is_empty(a[field]):
                    for problem in fill_problems(where, a, {field: b[field]}):
                        problems.append({"path": path, "line": field_line(new_bytes, field), "message": problem})
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
    present = {kind: [] for kind, _, _ in ID_FIELDS}
    for p in disk.paths():
        match_of_acceptance_unit_file = ACCEPTANCE_UNIT_FILE.fullmatch(p)
        match_of_acceptance_area_file = ACCEPTANCE_AREA_FILE.fullmatch(p)
        if not (match_of_acceptance_unit_file or match_of_acceptance_area_file):
            continue
        found = match_of_acceptance_unit_file or match_of_acceptance_area_file
        present["acceptance_unit" if match_of_acceptance_unit_file else "acceptance_area"].append(
            (found.group(1), p, None))
        try:
            present["scenario"] += [(s.scenario_id, p, s.line) for s in hashes.scenarios(disk.read(p) or b"")
                                    if s.scenario_id]
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


def tests_of(root, unit_id):
    """The files of tests/<unit ID>/ that HEAD holds."""
    return ls_tree(root, "HEAD", f"tests/{unit_id}")


def delete_tests(root, unit_id):
    """ACU-10, ACU-70: deletes from the working tree each file of tests/<unit ID>/ that HEAD holds."""
    if not re.fullmatch(r"AU-[1-9][0-9]*", unit_id):
        raise Stop(f"{unit_id} is not a unit ID")
    deleted = []
    for path in tests_of(root, unit_id):
        full = os.path.join(root, *path.split("/"))
        if os.path.lexists(full):
            os.remove(full)
            deleted.append(path)
    base = os.path.join(root, "tests", unit_id)
    for folder, _, _ in sorted(os.walk(base), key=lambda x: -len(x[0])):
        try:
            os.rmdir(folder)
        except OSError:
            pass
    return deleted


def parse_changes(changes):
    parsed = []
    for change in changes:
        if change.strip() == " ".join(FILL_CHANGE):
            parsed.append(FILL_CHANGE)
            continue
        m = CHANGE.fullmatch(change.strip())
        if not m:
            raise Stop(f"not a change: {change}")
        parsed.append((m.group(1), m.group(2)))
    return parsed


def message(changes):
    """ACU-71: the subject and the body of the commit message."""
    if changes == [FILL_CHANGE]:
        subject = "docs: fill acceptance.json"
    elif len(changes) == 1:
        verb, an_id = changes[0]
        subject = f"docs: {verb} acceptance {'area' if an_id.startswith('AA-') else 'unit'}"
    else:
        subject = "docs: change acceptance areas and units"
    return subject, "\n".join(f"{verb} {an_id}" for verb, an_id in changes)


def deleted_tests(root, changes):
    """The files of tests/<unit ID>/ that HEAD holds and the working tree does not, for each acceptance unit
    deleted."""
    found = []
    for verb, an_id in changes:
        if verb == "delete" and an_id.startswith("AU-"):
            found += [p for p in tests_of(root, an_id) if not os.path.lexists(os.path.join(root, *p.split("/")))]
    return found


def _facts(data):
    """The scenario IDs, the norm IDs cited in "## Norms", the area ID of the line "Area:" and the scenarios of a
    file."""
    if data is None:
        return set(), set(), None, []
    try:
        found = hashes.scenarios(data)
        cited = {norm_id for norm_id, _, _ in hashes.norm_citations(data)}
        area_id = next((m.group(1) for m in map(re.compile(r"Area: (AA-[1-9][0-9]*)").fullmatch,
                                                 hashes.lines_of(data)) if m), None)
    except UnicodeDecodeError:
        return set(), set(), None, []
    return {x.scenario_id for x in found if x.scenario_id}, cited, area_id, found


def strays(root, changes, files):
    """ACU-71: the files of areas/ and units/ that differ from HEAD and belong to no change (the term Change).

    A file belongs to a change when it is the file of its ID; when the change moves a scenario or a norm citation
    out of it into the file of a change (ACU-67); or, for an acceptance area, when a scenario of it at HEAD crosses
    an acceptance unit that the change deletes, moves to another acceptance area, or makes cite no longer a norm of
    a tag of that scenario (ACU-10, ACU-70)."""
    disk, head = Layer3(root, None), Layer3(root, "HEAD")
    named = {f"{'areas' if an_id.startswith('AA-') else 'units'}/{an_id}.md": (verb, an_id) for verb, an_id in changes
             if (verb, an_id) != FILL_CHANGE}
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
    acceptance_units = {}
    for path in list(named) + sorted(moved):
        m = ACCEPTANCE_UNIT_FILE.fullmatch(path)
        if m:
            verb = named[path][0] if path in named else "change"
            acceptance_units[m.group(1)] = (verb, _facts(head.read(path)), _facts(disk.read(path)))
    found = []
    for path, old, new in files:
        if path == "acceptance.json" or path in named or path in moved:
            continue
        old_scenarios = _facts(old)[3]
        crossed = False
        if ACCEPTANCE_AREA_FILE.fullmatch(path):
            for scenario in old_scenarios:
                for unit_id in scenario.acceptance_units:
                    if unit_id not in acceptance_units:
                        continue
                    verb, (_, cited_before, area_before, _), (_, cited_now, area_now, _) = acceptance_units[unit_id]
                    lost = cited_before - cited_now
                    if verb == "delete" or area_before != area_now or set(scenario.norms) & lost:
                        crossed = True
        if not crossed:
            found.append(path)
    return found


def commit(where, norms_commit, change_texts, expected_head):
    """ACU-71: the diff, the message and the one command that fetches, stages, commits and pushes.

    `expected_head` is the expected head of ACU-71: the proposal was made from it, and a commit that another session
    adds to HEAD after it must never be pushed with the commit of define."""
    root = where["root"]
    changes = parse_changes(change_texts)
    if not changes:
        raise Stop("no change given")
    # ACU-75, in its order (scripts/acceptance_repository_checks.py); every row exits 3, so that the skill puts back
    # what it wrote.
    branch, refusal = checks.checks_before_commit(root, where["acceptance_repository"], expected_head)
    if refusal is not None:
        raise Stop(refusal, code=3)
    result = check(where, norms_commit)
    if result["problems"]:
        raise Stop("the checks of ACU-69 fail:\n" + "\n".join(
            f"{p['path']}:{p['line'] or ''}: {p['message']}" for p in result["problems"]))
    files = written(root)
    present = {p for p, _, new in files if new is not None}
    gone = {p for p, _, new in files if new is None}
    acceptance_at_head = acceptance_ok(show(root, "HEAD", "acceptance.json") or b"")
    acceptance_on_disk = acceptance_ok(Layer3(root, None).read("acceptance.json") or b"")
    fields_filled = bool(acceptance_at_head and acceptance_on_disk and any(
        acceptance_at_head[f] != acceptance_on_disk[f] for f in FILLABLE_FIELDS))
    if fields_filled and FILL_CHANGE not in changes:
        raise Stop("acceptance.json differs from HEAD in test_command or product, and no change of the commit names "
                   "it (ACU-71)")
    for verb, an_id in changes:
        if (verb, an_id) == FILL_CHANGE:
            if not fields_filled:
                raise Stop("fill acceptance.json: acceptance.json is not filled as it says")
            continue
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
        raise Stop(f"{checks.text_of(stray[0])} differs from HEAD, and no change of the commit names it (ACU-71)")
    tests = deleted_tests(root, changes)
    paths = sorted({p for p, _, _ in files} | set(tests))
    subject, body = message(changes)
    # ACU-71, ACU-75: the command makes the checks again before it stages anything, stages and commits each path by
    # its name, and prints the 40 hex digits of the commit pushed, the expected head of the next command.
    command = checks.commit_command(PREFIX, root, where["acceptance_repository"], branch, expected_head, paths,
                                    subject, body)
    # ACU-75: the diff of each file, computed by the script of the module that every use case shows.
    diffs = [checks.diff_of_a_file(p, old, new) for p, old, new in files]
    diffs += [checks.diff_of_a_file(p, show(root, "HEAD", p), None) for p in tests]
    display = "\n".join(["Diff:", ""] + diffs + ["Commit:", f"    {subject}", ""] +
                        [f"    {line}" for line in body.split("\n")])
    return {"display": display, "paths": paths, "message": f"{subject}\n\n{body}", "command": command,
            "default_branch": branch}


def rollback(root, change_texts):
    """ACU-71: gives back to areas/, units/ and acceptance.json the bytes of HEAD, and the tests of each acceptance unit
    deleted."""
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
    for path in restored:
        _index_as_at_head(root, path)
    return sorted(restored)


def _index_as_at_head(root, path):
    """ACU-71: the entry of one path in the index as HEAD holds it, after a command that staged it and whose commit
    was refused; "git update-index --cacheinfo" and "git rm --cached" change the index of that path alone (ACU-73)."""
    entry = out(root, "--literal-pathspecs", "ls-tree", "HEAD", "--", path)
    if entry:
        mode, _, blob = entry.split("\t")[0].split()
        git(root, "update-index", "--cacheinfo", f"{mode},{blob},{path}")
    elif git(root, "--literal-pathspecs", "ls-files", "--error-unmatch", "--", path).returncode == 0:
        git(root, "--literal-pathspecs", "rm", "-q", "--cached", "--", path)


def next_line(root, since):
    """ACU-72: the line "Next: ..." for the commits from `since` to HEAD, or None.

    The part of the implementation planner applies when the commits added or deleted an acceptance unit, or changed
    its unit hash; a change of the title, of "Area:" or of "Profile:" alone, which no hash holds (ACU-52), names
    nobody. The part of the test agent applies only when neither test_command nor product is empty at HEAD, since
    write-acceptance-tests refuses to start otherwise (WAT-2); it names every acceptance area and acceptance unit of
    HEAD when the commits filled test_command or product (ACU-77)."""
    since_commit = out(root, "rev-parse", "-q", "--verify", f"{since}^{{commit}}")
    if since_commit is None or git(root, "merge-base", "--is-ancestor", since_commit, "HEAD").returncode != 0:
        raise Stop(f"--since {since} is not a commit of HEAD")
    old, new = Layer3(root, since_commit), Layer3(root, "HEAD")
    paths = sorted(set(old.paths()) | set(new.paths()))
    acceptance_units_planned, ids = False, []
    for path in paths:
        match_of_acceptance_unit_file = ACCEPTANCE_UNIT_FILE.fullmatch(path)
        match_of_acceptance_area_file = ACCEPTANCE_AREA_FILE.fullmatch(path)
        if not (match_of_acceptance_unit_file or match_of_acceptance_area_file):
            continue
        a, b = old.read(path), new.read(path)
        if a == b:
            continue
        if match_of_acceptance_unit_file and (a is None or b is None):
            acceptance_units_planned = True
        if b is None:
            continue
        compute = hashes.unit_hash if match_of_acceptance_unit_file else hashes.area_hash
        try:
            before = compute(a) if a is not None else None
            after = compute(b)
        except UnicodeDecodeError:
            continue
        if after is not None and after != before:
            ids.append((match_of_acceptance_unit_file or match_of_acceptance_area_file).group(1))
            if match_of_acceptance_unit_file:
                acceptance_units_planned = True
    acceptance_before = acceptance_ok(old.read("acceptance.json") or b"")
    acceptance_after = acceptance_ok(new.read("acceptance.json") or b"")
    if (acceptance_before and acceptance_after
            and any(is_empty(acceptance_before[f]) for f in FILLABLE_FIELDS)
            and not any(is_empty(acceptance_after[f]) for f in FILLABLE_FIELDS)):
        ids = [m.group(1) for m in (ACCEPTANCE_UNIT_FILE.fullmatch(p) or ACCEPTANCE_AREA_FILE.fullmatch(p)
                                    for p in new.paths()) if m]
    if acceptance_after is None or any(is_empty(acceptance_after[f]) for f in FILLABLE_FIELDS):
        ids = []
    ids.sort(key=lambda x: (x[:2] != "AA", number(x)))
    parts = []
    if acceptance_units_planned:
        parts.append("the implementation planner updates plan.json with /acceptance-management:plan")
    if ids:
        parts.append(f"the test agent updates the acceptance tests of {', '.join(ids)} "
                     "with /acceptance-management:write-acceptance-tests")
    return f"Next: {'; '.join(parts)}." if parts else None


# ---------------------------------------------------------------- main

def norms_commit_of(where, rest):
    """The option --norms-commit: 40 lower-case hex digits, the head of a branch of origin of the norms repository
    (ACU-59), never a local branch, HEAD or a short SHA."""
    sha = option(rest, "--norms-commit")
    refs = out(where["norms_repository_path"], "for-each-ref", "--points-at", sha, "--format=%(refname)", "refs/remotes/origin/")
    if not re.fullmatch(r"[0-9a-f]{40}", sha) or not refs:
        raise Stop(f"--norms-commit {sha} is not the head of a branch of origin in {where['norms_repository']}; "
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
            print(checks.json_text({"path": path, "unit_hash": hashes.unit_hash(data),
                                    "area_hash": hashes.area_hash(data),
                                    "scenarios": [{"scenario_id": s.scenario_id, "name": s.name,
                                                   "scenario_hash": s.scenario_hash}
                                                  for s in hashes.scenarios(data)]}))
        return 0
    if not args:
        raise Stop(f"{command}: REPO is required")
    repo, rest = args[0], args[1:]
    if command == "start":
        extra = rest[1:] if rest[:1] == ["--"] else rest
        print(checks.json_text(start(repo, extra)))
        return 0
    where = locate(repo)
    root = where["root"]
    if command == "inventory":
        inv = inventory(where, norms_commit_of(where, rest), None if "--worktree" in rest else "HEAD")
        print(checks.json_text(public(inv)))
        return 0
    if command == "check":
        result = check(where, norms_commit_of(where, rest))
        print(checks.json_text(result))
        return 1 if result["problems"] else 0
    if command == "ids":
        print(checks.json_text(set_ids(root)))
        return 0
    if command == "fill":
        if not rest or rest[0].startswith("--"):
            raise Stop("fill takes the path of a file")
        print(checks.json_text(fill(where, rest[0], "--dry-run" in rest[1:])))
        return 0
    if command == "delete-tests":
        if len(rest) != 1:
            raise Stop("delete-tests takes one unit ID")
        print(checks.json_text(delete_tests(root, rest[0])))
        return 0
    if command == "commit":
        result = commit(where, norms_commit_of(where, rest), option(rest, "--change", many=True),
                        option(rest, "--expected-head"))
        print(checks.json_text(result))
        return 0
    if command == "rollback":
        print(checks.json_text(rollback(root, option(rest, "--change", many=True))))
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
    except checks.Refusal as refusal:
        # The norms of the norms commit cannot be read (scripts/acceptance_repository_files.py, read_norms).
        print(PREFIX + refusal.message)
        sys.exit(1)
