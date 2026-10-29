"""The script of the use case write-acceptance-tests of acceptance-management, with no model (WAT-1 to WAT-14).

Spec: specs/write-acceptance-tests.md of this folder, and specs/module.md of
the module. The checks of ACU-74 and ACU-75 and the diff of a file of a
commit (ACU-75) are those of scripts/acceptance_repository_checks.py of the
module, and the fingerprints (ACU-51 to ACU-54) those of
scripts/acceptance_hashes.py. The format errors of a file of an acceptance
unit or an acceptance area, the citation status of a norm citation and the
"own_text" of a norm are those of the inventory of define (ACU-60 to
ACU-62), and a citation found in a line (ACU-56) is that of define too, which
this script reads by importing scripts/acceptance_repository_files.py of the
module, as define does.

Usage (REPO is the working directory of the skill; ID is a unit ID or an area
ID; SC is a scenario ID; every command reads, and only `delete` and `rollback`
write, and only files of tests/<ID>/ and their entries in the index):

    write_acceptance_tests.py start REPO [-- ARG...]
        WAT-2: the checks of ACU-74, then those of write-acceptance-tests, in
        their order; on the first that fails, prints
        "acceptance-management:write-acceptance-tests: <message>" and exits 1.
        Otherwise prints one JSON object: "acceptance_repository",
        "norms_repository", "specs_repository" (or null when project.json has
        not exactly one entry of layer 1), "acceptance_default_branch",
        "norms_default_branch", "norms_commit", "acceptance_commit",
        "proposal" (the summary and the proposal of the acceptance tests of
        WAT-8) and "nothing_to_write" (the message of WAT-8 when the proposal
        holds no change, or null).
    write_acceptance_tests.py inventory REPO --norms-commit SHA [--worktree]
        WAT-5: prints the inventory of the acceptance tests, at HEAD, or with
        --worktree with the files of tests/ as they are in the working tree.
    write_acceptance_tests.py propose REPO --norms-commit SHA [--reported-wrong SC]... [--reject ID]... [--gap SC]...
        WAT-8, WAT-10: prints the summary and the proposal of the acceptance
        tests, with the item "reported wrong" of each --reported-wrong, without
        the change of each --reject, and without the item of each --gap; exits
        1 with "<SC> has no acceptance test to rewrite" for a --reported-wrong
        that has none.
    write_acceptance_tests.py delete REPO ID
        WAT-9: deletes from the working tree every file of tests/<ID>/ that
        HEAD holds, when the proposal holds the change "delete" of ID.
    write_acceptance_tests.py check REPO --norms-commit SHA --change ID... [--reported-wrong SC]... [--gap SC]...
        WAT-11: the problems of the files written for the changes of one
        commit, one per line, in the forms of WAT-11 ("<ID>: <item of WAT-8>",
        "<ID>: <path> is not deleted", "<path> differs from HEAD, and no
        change of the commit holds it (WAT-11)"); exits 1 when there is one.
    write_acceptance_tests.py commit REPO --norms-commit SHA --expected-head SHA --change ID... [--reported-wrong SC]... [--gap SC]...
        WAT-12, ACU-75: makes the checks of ACU-75 and exits 3 with the
        message of the first that fails; makes the checks of WAT-11 and exits
        1 with their problems; prints a JSON object: "display" (the diff of
        the commit and its message), "paths", "message", "command",
        "acceptance_default_branch" and "next" (the line of WAT-13).
    write_acceptance_tests.py rollback REPO --change ID...
        WAT-12: puts each file of tests/<ID>/ back as HEAD holds it, and
        removes each new file of it, in the working tree and in the index,
        touching no other path.

The commands, the options and the messages that only the skill reads (such
as "<ID> has no change in the proposal of the acceptance tests") are the
skill's own and do not bind (the paragraph of the binding words of the spec).

Never runs git stash, reset, checkout, restore or clean (WAT-14); never
changes the working tree, the index or a local branch of the norms repository
(WAT-3); never runs test_command, a build or a published of acceptance.json
(WAT-3). --norms-commit is 40 lower-case hex digits, a commit of the norms
repository: the norms commit of `start`. Python 3.9 or later, standard library
only. The names of the JSON keys and of the identifiers follow the terms of
the specs: "acceptance_unit", "acceptance_area", "acceptance_test",
"folder_of_acceptance_tests", "expected_opening"...
"""

from __future__ import annotations

import bisect
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(HERE)), "scripts")
sys.path.insert(0, SCRIPTS)
sys.dont_write_bytecode = True

import acceptance_hashes as hashes  # noqa: E402
import acceptance_repository_checks as checks  # noqa: E402
from acceptance_repository_checks import git, ls_tree, out, show, text_of  # noqa: E402
import acceptance_repository_files as files_of_the_acceptance_repository  # noqa: E402
from acceptance_repository_files import (CITATION_IN_LINE, NORM_CITATION_IN_LINE, SC_LIKE, number,  # noqa: E402
                                         plural, public)

PREFIX = "acceptance-management:write-acceptance-tests: "
NEXT = "Next: the implementing agents implement the plan with /code-implementation:implement."  # WAT-13
FOLDER_ID = re.compile(r"(?:AU|AA)-[1-9][0-9]*")
SCENARIO_ID = re.compile(r"SC-[1-9][0-9]*")
CITATION = re.compile(r"((?:AU|AA|SC)-[1-9][0-9]*)@([0-9a-f]{8}): (.+)")  # ACU-56, after the comment mark
# WAT-7: a citation found in a line is that of ACU-56, CITATION_IN_LINE and NORM_CITATION_IN_LINE of
# scripts/acceptance_repository_files.py, which define reads too for the titles and the names of the scenarios.
STATUSES = ("missing", "duplicated", "scenario_changed", "citation_changed", "current")  # WAT-6
OPTIONS = {"--norms-commit": 1, "--expected-head": 1, "--change": 1, "--reported-wrong": 1, "--reject": 1,
           "--gap": 1, "--worktree": 0}


class Stop(Exception):
    """A refusal: its message is said after PREFIX, and the command exits with `code`."""

    def __init__(self, message, code=1):
        super().__init__(message)
        self.code = code


class Said(Stop):
    """Lines printed as they are, with no PREFIX."""


def id_order(an_id):
    """The acceptance areas first, then the acceptance units, each in the order of the numbers (WAT-8)."""
    return (0 if an_id.startswith("AA-") else 1, number(an_id))


def file_of(an_id):
    return f"{'areas' if an_id.startswith('AA-') else 'units'}/{an_id}.md"


def folder_of(an_id):
    return f"tests/{an_id}/"


# ---------------------------------------------------------------- where the repositories are

def locate(cwd):
    """Rows 2 and 3 of ACU-74, for the commands after `start`."""
    try:
        return checks.locate(cwd)
    except checks.Refusal as refusal:
        raise Stop(refusal.message)


def norms_commit_of(where, options):
    """--norms-commit: 40 lower-case hex digits that name a commit of the norms repository (WAT-3)."""
    sha = option(options, "--norms-commit")
    if not re.fullmatch(r"[0-9a-f]{40}", sha) or git(where["norms_repository_path"], "cat-file", "-e",
                                                      f"{sha}^{{commit}}").returncode != 0:
        raise Stop(f"--norms-commit {sha} is not a commit of {where['norms_repository']}")
    return sha


# ---------------------------------------------------------------- the checks of write-acceptance-tests (WAT-2)

def acceptance_json(data):
    """ACU-6: the object of acceptance.json when it meets ACU-6, or None; the one check of the module, shared with
    define (scripts/acceptance_repository_checks.py)."""
    return checks.acceptance_json_of(data) if data is not None else None


def status_of_tests(root):
    """WAT-2: the paths under tests/ that differ from HEAD in the working tree or in the index, and the untracked files
    under tests/ that no .gitignore names, each in sorted order."""
    done = git(root, "status", "--porcelain=v1", "-z", "--no-renames", "--untracked-files=all", "--", "tests",
               binary=True)
    changed, untracked = [], []
    for entry in done.stdout.split(b"\0"):
        if len(entry) < 4:
            continue
        # git lists another git repository nested under tests/ as one untracked entry, with a trailing "/" that is not
        # part of its path (ACU-58).
        code, path = entry[:2].decode(), entry[3:].decode("utf-8", "surrogateescape").rstrip("/")
        (untracked if code == "??" else changed).append(path)
    return sorted(changed), sorted(untracked)


def start(cwd, arguments):
    """WAT-2: the checks of ACU-74, then those of write-acceptance-tests, in their order."""
    where, message = checks.run_checks(cwd, arguments)
    if message is not None:
        raise Stop(message)
    root = where["root"]
    found = acceptance_json(show(root, "HEAD", "acceptance.json"))
    if found is None:
        raise Stop("acceptance.json does not meet ACU-6")
    if found["test_command"] == "":
        raise Stop("acceptance.json has no test_command; the acceptance tests cannot be written without it (ACU-43)")
    if found["product"] == {}:
        raise Stop("acceptance.json has no entry in product; the acceptance tests cannot be written without it "
                   "(ACU-43)")
    problems = checks.problems_of_values(checks.code_repositories(where["repositories"]),
                                         {"test_command": found["test_command"], "product": found["product"]})
    if problems:
        raise Stop(f"acceptance.json: {problems[0]}")
    changed, untracked = status_of_tests(root)
    if changed:
        raise Stop(f"uncommitted change in {text_of(changed[0])}")
    if untracked:
        raise Stop(f"untracked file {text_of(untracked[0])}")
    inventory_of_the_acceptance_tests = inventory(where, where["norms_commit"])
    changes = changes_of(inventory_of_the_acceptance_tests)
    return {"acceptance_repository": where["acceptance_repository"],
            "norms_repository": where["norms_repository"],
            "specs_repository": where["specs_repository"],
            "acceptance_default_branch": where["acceptance_default_branch"],
            "norms_default_branch": where["norms_default_branch"],
            "norms_commit": where["norms_commit"],
            "acceptance_commit": inventory_of_the_acceptance_tests["acceptance_commit"],
            "proposal": render(inventory_of_the_acceptance_tests, changes),
            "nothing_to_write": None if changes["changes"] else PREFIX + "no acceptance test to write"}


# ---------------------------------------------------------------- the files of tests/ (WAT-4, WAT-5)

def files_on_disk(root, folder="tests"):
    """The entries under `folder` in the working tree: those that the index holds and the untracked ones that no
    .gitignore names (the term "Named by a .gitignore": git ignores only a file that the index does not hold), each
    that is there. A folder is one entry only when it is a submodule that the index holds, or another git repository
    nested in `folder`, which git lists as one untracked entry (WAT-7); a folder that stands where the index holds a
    file is not, its files are."""
    found = set()
    cached = git(root, "ls-files", "-z", "--cached", "--stage", "--", folder, binary=True)
    for entry in cached.stdout.split(b"\0"):
        if not entry:
            continue
        meta, _, name = entry.partition(b"\t")
        path = name.decode("utf-8", "surrogateescape")
        full = os.path.join(root, *path.split("/"))
        if os.path.lexists(full) and (os.path.islink(full) or not os.path.isdir(full)
                                      or meta.split()[0] == b"160000"):
            found.add(path)
    others = git(root, "ls-files", "-z", "--others", "--exclude-standard", "--", folder, binary=True)
    for p in others.stdout.split(b"\0"):
        path = p.decode("utf-8", "surrogateescape").rstrip("/")
        if path and os.path.lexists(os.path.join(root, *path.split("/"))):
            found.add(path)
    return sorted(found)


def is_regular_on_disk(root, path):
    """WAT-7: a regular file of the working tree, not a symbolic link and not a folder."""
    full = os.path.join(root, *path.split("/"))
    return os.path.isfile(full) and not os.path.islink(full)


def read_on_disk(root, path):
    """The bytes of a file of the working tree, as git would store them: the target of a symbolic link, never what
    it points to; None for a folder or a path that is not there."""
    full = os.path.join(root, *path.split("/"))
    try:
        if os.path.islink(full):
            return os.fsencode(os.readlink(full))
        with open(full, "rb") as f:
            return f.read()
    except OSError:
        return None


def entries_at_head(root, folder="tests"):
    """The entry of each path under `folder` at HEAD, as git ls-tree gives it: (mode, object ID), the mode 100644,
    100755, 120000 (a symbolic link) or 160000 (a submodule)."""
    done = git(root, "ls-tree", "-r", "-z", "HEAD", "--", folder, binary=True)
    found = {}
    for entry in done.stdout.split(b"\0"):
        if entry:
            meta, _, name = entry.partition(b"\t")
            mode, _, object_id = meta.decode().split()
            found[name.decode("utf-8", "surrogateescape")] = (mode, object_id)
    return found


class TestsAtHead:
    """The files of tests/ at HEAD, every one that HEAD holds, whatever a .gitignore says (WAT-4)."""

    def __init__(self, root):
        self.root = root
        entries = entries_at_head(root)
        self.all = sorted(entries)
        self.not_regular = {p for p, (mode, _) in entries.items() if mode in ("120000", "160000")}

    def read(self, path):
        return show(self.root, "HEAD", path)


class TestsInWorkingTree:
    """The files of tests/ in the working tree, the untracked ones that a .gitignore names left out (WAT-5)."""

    def __init__(self, root):
        self.root = root
        self.all = files_on_disk(root)
        self.not_regular = {p for p in self.all if not is_regular_on_disk(root, p)}

    def read(self, path):
        return read_on_disk(self.root, path)


def _letter_or_number(character):
    """A letter or a number of Unicode: general categories L and N (ACU-56)."""
    return unicodedata.category(character)[0] in "LN"


def comment_mark_ok(mark):
    """The term comment mark: 1 to 3 characters, none a letter or a number of Unicode, a space, a tab or a character
    that breaks a line."""
    return 1 <= len(mark) <= 3 and not any(_letter_or_number(c) or c in " \t" or checks.breaks_a_line(c)
                                           for c in mark)


def citation_line(line):
    """WAT-4: (comment mark, ID, hash, the text after the comment mark and one space) of a line that holds exactly
    "<comment mark> <citation>" after its leading spaces and tabs, its trailing spaces and tabs left out; or None."""
    stripped = line.strip(" \t")
    space = stripped.find(" ")
    if space < 1:
        return None
    mark, rest = stripped[:space], stripped[space + 1:]
    found = CITATION.fullmatch(rest)
    if not comment_mark_ok(mark) or not found:
        return None
    return mark, found.group(1), found.group(2), rest


def read_folder(folder_id, paths, source, code_repositories):
    """WAT-4, WAT-7: the openings of the folder of acceptance tests of `folder_id`, and the errors of its files.

    Returns (openings, errors): each opening {"path", "line", "scenario_id", "scenario_hash", "lines"}, where
    "lines" are the two texts after the comment mark and one space; each error {"path", "line", "message"}."""
    openings, errors = [], []
    for path in paths:
        if path in source.not_regular:
            errors.append({"path": path, "line": None, "message": "not a regular file (ACU-6)"})
            continue
        data = source.read(path)
        if data is None:
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            errors.append({"path": path, "line": None, "message": "not UTF-8"})
            continue
        # WAT-4: one U+FEFF at the start of a file is not part of its first line.
        normalised = text[1:] if text.startswith("\ufeff") else text
        normalised = normalised.replace("\r\n", "\n")
        lines = normalised.split("\n")
        parsed = [citation_line(line) for line in lines]
        # The lines of every pair of opening lines, whatever unit ID or area ID it cites: none of them holds a citation
        # outside the opening of an acceptance test (WAT-4). Only the lines of the openings of this folder hold a name
        # of a code repository that is no error (WAT-7): a pair that cites another ID is the opening of no acceptance
        # test of the folder.
        of_an_opening, of_an_opening_of_the_folder = set(), set()
        found_errors = []
        for i in range(len(lines) - 1):
            first, second = parsed[i], parsed[i + 1]
            if not (first and second and first[0] == second[0] and FOLDER_ID.fullmatch(first[1])
                    and SCENARIO_ID.fullmatch(second[1])):
                continue
            of_an_opening |= {i, i + 1}
            if first[1] == folder_id:
                of_an_opening_of_the_folder |= {i, i + 1}
                openings.append({"path": path, "line": i + 1, "scenario_id": second[1], "scenario_hash": second[2],
                                 "lines": [first[3], second[3]]})
            else:
                found_errors.append((i + 1, 2, f"cites {first[1]}, which is not the acceptance unit or the "
                                                "acceptance area of this folder (ACU-11)"))
        for i, line in enumerate(lines):
            for found in CITATION_IN_LINE.finditer(line):
                cited = found.group(1)
                if FOLDER_ID.fullmatch(cited) and cited != folder_id:
                    found_errors.append((i + 1, 2, f"cites {cited}, which is not the acceptance unit or the "
                                                   "acceptance area of this folder (ACU-11)"))
                elif i not in of_an_opening:
                    found_errors.append((i + 1, 4, "citation outside the opening of an acceptance test (ACU-11)"))
            for found in NORM_CITATION_IN_LINE.finditer(line):
                found_errors.append((i + 1, 3, f"cites the norm {found.group(1)} (ACU-11)"))
        # The offset of the start of each line, so that the line of a name found is a search, not a count from the
        # start of the file for each name found.
        starts_of_lines = [0] + [k + 1 for k, character in enumerate(normalised) if character == "\n"]
        # A line of an opening of the folder holds the title and the name that the acceptance architect approved: a
        # name of a code repository in them is no error (WAT-7).
        for owner_name, patterns in code_repositories:
            for pattern in patterns:
                for found in pattern.finditer(normalised):
                    line = bisect.bisect_right(starts_of_lines, found.start())
                    if line - 1 not in of_an_opening_of_the_folder:
                        found_errors.append((line, 5, f"names the code repository {text_of(owner_name)} (ACU-11)"))
        seen = set()
        for line, row, message in sorted(found_errors, key=lambda e: (e[0], e[1])):
            if (line, message) not in seen:
                seen.add((line, message))
                errors.append({"path": path, "line": line, "message": message})
    return openings, errors


# WAT-7, "What names a code repository": an end of the name is the end of the file, a character that is not a letter
# or a number of Unicode (Python's \w is those and "_"), "-", "_" or ".", or a "." not followed by a letter, a number,
# "-" or "_"; a name followed by ".git" and an end of the name names the code repository too.
END_OF_A_NAME = r"(?:\Z|[^\w.-]|\.(?![\w-]))"


def code_repositories_of(where):
    """WAT-7: each entry of layer 4 of project.json, as ("<owner>/<name>", [the pattern of its "<owner>/<name>" and
    of its "path"]), each pattern compiled once per invocation."""
    found = []
    for entry in where["repositories"]:
        if entry.get("layer") != 4:
            continue
        owner_name = f"{entry.get('owner')}/{entry.get('name')}"
        names = [owner_name] + ([entry["path"]] if isinstance(entry.get("path"), str) and entry["path"] else [])
        found.append((owner_name, [re.compile(r"(?<![\w.-])" + re.escape(name)
                                          + rf"(?={END_OF_A_NAME}|\.git{END_OF_A_NAME})") for name in names]))
    return found


# ---------------------------------------------------------------- the inventory of the acceptance tests (WAT-5, WAT-6)

def read_norms(where, norms_commit):
    """ACU-60: the norms at the norms commit, as the inventory of define reads them."""
    try:
        return files_of_the_acceptance_repository.read_norms(where, norms_commit)
    except checks.Refusal as refusal:
        raise Stop(refusal.message)


def scenarios_of(data):
    """ACU-54: the scenarios of a file that have a scenario ID, each with its text, as far as the file can be read;
    the scenario ID is that of the inventory of define (exactly one tag "@SC-<n>")."""
    try:
        lines = hashes.lines_of(data)
        found = hashes.scenarios(data)
    except UnicodeDecodeError:
        return []
    block = hashes._gherkin_block(lines)
    starts = [s.line - 1 for s in found]
    result = []
    for k, scenario in enumerate(found):
        end = starts[k + 1] if k + 1 < len(found) else (block[1] if block else len(lines))
        text_lines = lines[starts[k]:end]
        while text_lines and text_lines[-1] == "":
            text_lines.pop()
        if scenario.scenario_id is None or len([t for t in scenario.tags if SC_LIKE.fullmatch(t)]) != 1:
            continue
        result.append((scenario, "\n".join(text_lines)))
    return result


def status_of(openings, scenario_hash, expected_opening):
    """WAT-6: the status of the acceptance test of one scenario, from the openings that cite it, in the order of the
    table."""
    if not openings:
        return "missing"
    if len(openings) >= 2:
        return "duplicated"
    if openings[0]["scenario_hash"] != scenario_hash:
        return "scenario_changed"
    if expected_opening is None or openings[0]["lines"] != expected_opening:
        return "citation_changed"
    return "current"


def inventory(where, norms_commit, worktree=False):
    """WAT-5: the inventory of the acceptance tests, at HEAD; with `worktree`, with the files of tests/ as they are in
    the working tree, against the same HEAD for areas/, units/ and acceptance.json, and the same norms commit."""
    root = where["root"]
    found = acceptance_json(show(root, "HEAD", "acceptance.json"))
    if found is None:
        raise Stop("acceptance.json does not meet ACU-6")
    norms = read_norms(where, norms_commit)
    norm_of = {}
    for norm in norms:
        norm_of.setdefault(norm["norm_id"], norm)
    inventory_of_define = files_of_the_acceptance_repository.inventory(where, norms_commit, "HEAD", norms)
    # WAT-6: a file has a format error when its own errors hold one, when an error of the repository names it by its
    # path, or when another file of areas/ or units/ holds one of its scenario IDs.
    paths_with_format_errors = {error.get("path") for error in inventory_of_define["errors"]}
    holders = {}
    for item in inventory_of_define["acceptance_areas"] + inventory_of_define["acceptance_units"]:
        if item["errors"]:
            paths_with_format_errors.add(item["path"])
        for scenario in item["scenarios"]:
            if scenario["scenario_id"]:
                holders.setdefault(scenario["scenario_id"], set()).add(item["path"])
    for paths in holders.values():
        if len(paths) > 1:
            paths_with_format_errors |= paths

    source = TestsInWorkingTree(root) if worktree else TestsAtHead(root)
    at_head = TestsAtHead(root) if worktree else source
    folders, errors = {}, []
    reported = set()
    # WAT-6, WAT-7: an entry tests/<ID> itself that is not a folder (a symbolic link, a submodule or a file), and an
    # entry tests that is not a folder.
    not_a_folder = set()
    for path in source.all:
        parts = path.split("/")
        if len(parts) == 1:
            errors.append({"path": path, "message": f"{text_of(path)} is not a folder (ACU-6)"})
        elif len(parts) == 2 and FOLDER_ID.fullmatch(parts[1]):
            not_a_folder.add(parts[1])
        elif len(parts) == 2:
            errors.append({"path": path, "message": f"{text_of(path)} is not in the folder of an acceptance unit or "
                                                    "an acceptance area (ACU-6)"})
        elif FOLDER_ID.fullmatch(parts[1]):
            folders.setdefault(parts[1], []).append(path)
        elif parts[1] not in reported:
            reported.add(parts[1])
            folder = f"tests/{parts[1]}"
            errors.append({"path": folder, "message": f"{text_of(folder)} is not the folder of an acceptance unit "
                                                      "or an acceptance area (ACU-6)"})
    folders_at_head = {p.split("/")[1] for p in at_head.all if len(p.split("/")) > 2
                       and FOLDER_ID.fullmatch(p.split("/")[1])}
    code_repositories = code_repositories_of(where)

    def entry_of(an_id, item_of_define):
        path = file_of(an_id)
        data = show(root, "HEAD", path) or b""
        title = item_of_define["title"]
        the_hash = item_of_define["unit_hash"] if an_id.startswith("AU-") else item_of_define["area_hash"]
        openings, folder_errors = read_folder(an_id, folders.get(an_id, []), source, code_repositories)
        scenarios = []
        for scenario, text in scenarios_of(data):
            expected = (None if title is None or the_hash is None else
                        [f"{an_id}@{the_hash}: {title}", f"{scenario.scenario_id}@{scenario.scenario_hash}: "
                                                          f"{scenario.name}"])
            citing = sorted((o for o in openings if o["scenario_id"] == scenario.scenario_id),
                            key=lambda o: (o["path"], o["line"]))
            scenarios.append({
                "scenario_id": scenario.scenario_id, "name": scenario.name, "text": text,
                "norms": [{"norm_id": norm_id,
                           "norm_hash": norm_of[norm_id]["norm_hash"] if norm_id in norm_of else None,
                           "own_text": norm_of[norm_id]["own_text"] if norm_id in norm_of else None}
                          for norm_id in scenario.norms],
                "expected_opening": expected,
                "acceptance_test_status": status_of(citing, scenario.scenario_hash, expected),
                "acceptance_tests": [{"path": o["path"], "line": o["line"]} for o in citing],
                "_scenario_hash": scenario.scenario_hash,
                "_openings": citing})
        held = {s["scenario_id"] for s in scenarios}
        entry = {("unit_id" if an_id.startswith("AU-") else "area_id"): an_id, "path": path, "title": title,
                 "folder_of_acceptance_tests": folder_of(an_id),
                 "folder_of_acceptance_tests_at_head": an_id in folders_at_head, "blocked": None,
                 "scenarios": scenarios,
                 "acceptance_tests_of_no_scenario": [
                     {"scenario_id": o["scenario_id"], "path": o["path"], "line": o["line"]}
                     for o in sorted(openings, key=lambda o: (o["path"], o["line"]))
                     if o["scenario_id"] not in held],
                 "errors": sorted(folder_errors, key=lambda e: (e["path"], e["line"] or 0)),
                 "_format_errors": path in paths_with_format_errors,
                 "_behind_layer_2": any(c["citation_status"] != "current"
                                        for c in item_of_define.get("norm_citations", [])),
                 "_crossed": [u for s in item_of_define["scenarios"] for u in s.get("acceptance_units", [])]}
        return entry

    acceptance_units = [entry_of(u["unit_id"], u) for u in inventory_of_define["acceptance_units"]]
    acceptance_areas = [entry_of(a["area_id"], a) for a in inventory_of_define["acceptance_areas"]]
    # WAT-6: the reasons to be blocked, the first that holds, in the order of the table.
    for acceptance_unit in acceptance_units:
        if acceptance_unit["_format_errors"]:
            acceptance_unit["blocked"] = (f"format errors in {text_of(acceptance_unit['path'])}; the acceptance "
                                          "architect fixes them with /acceptance-management:define")
        elif acceptance_unit["_behind_layer_2"]:
            acceptance_unit["blocked"] = ("behind layer 2; the acceptance architect updates it with "
                                          "/acceptance-management:define")
        elif acceptance_unit["unit_id"] in not_a_folder:
            acceptance_unit["blocked"] = not_a_folder_reason(acceptance_unit["unit_id"])
    usable = {u["unit_id"] for u in acceptance_units if u["blocked"] is None}
    for acceptance_area in acceptance_areas:
        if acceptance_area["_format_errors"]:
            acceptance_area["blocked"] = (f"format errors in {text_of(acceptance_area['path'])}; the acceptance "
                                          "architect fixes them with /acceptance-management:define")
            continue
        if acceptance_area["area_id"] in not_a_folder:
            acceptance_area["blocked"] = not_a_folder_reason(acceptance_area["area_id"])
            continue
        # A unit crossed with no file is a format error of the area (ACU-61), so a unit crossed here has a file; of
        # the blocked ones, the reason names the one with the lowest number.
        crossed = sorted({u for u in acceptance_area["_crossed"] if u not in usable}, key=number)
        if crossed:
            acceptance_area["blocked"] = f"crosses {crossed[0]}, which is blocked"
    with_file = {u["unit_id"] for u in acceptance_units} | {a["area_id"] for a in acceptance_areas}
    with_no_file = sorted((an_id for an_id in folders_at_head if an_id not in with_file), key=id_order)
    errors += [{"path": f"tests/{an_id}", "message": f"tests/{an_id} is not a folder (ACU-6)"}
               for an_id in not_a_folder if an_id not in with_file]
    errors.sort(key=lambda e: e["path"])
    return {
        "norms_commit": norms_commit,
        "acceptance_commit": out(root, "rev-parse", "HEAD"),
        "test_command": found["test_command"],
        "product_variables": [entry["env"] for entry in found["product"].values()],
        "acceptance_areas": acceptance_areas,
        "acceptance_units": acceptance_units,
        "folders_of_acceptance_tests_with_no_file": with_no_file,
        "errors": errors,
    }


def not_a_folder_reason(an_id):
    """WAT-6: the reason to be blocked of an acceptance unit or an acceptance area whose tests/<ID> is not a
    folder."""
    return f"tests/{an_id} is not a folder (ACU-6); the requester decides on it"


def id_of(entry):
    return entry.get("unit_id") or entry.get("area_id")


def entries_of(inventory_of_the_acceptance_tests):
    return inventory_of_the_acceptance_tests["acceptance_areas"] + inventory_of_the_acceptance_tests["acceptance_units"]


# ---------------------------------------------------------------- the summary and the proposal (WAT-8)

def items_of(entry, reported_wrong=(), gaps=()):
    """WAT-8, "The items of a change": the items of an acceptance unit or an acceptance area, in their order; the
    scenarios that a gap of layer 1 left out (WAT-10) give none."""
    scenarios = sorted((s for s in entry["scenarios"] if s["scenario_id"] not in gaps),
                       key=lambda s: number(s["scenario_id"]))
    items = []
    for status, form in (("missing", "{} missing"), ("duplicated", "{} duplicated in {} acceptance tests"),
                         ("scenario_changed", "{} scenario changed"), ("citation_changed", "{} citation changed")):
        for scenario in scenarios:
            if scenario["acceptance_test_status"] == status:
                items.append(form.format(scenario["scenario_id"], len(scenario["acceptance_tests"])))
    held = {s["scenario_id"] for s in scenarios}
    for scenario_id in sorted({r for r in reported_wrong if r in held}, key=number):
        items.append(f"{scenario_id} reported wrong")
    for scenario_id in sorted({a["scenario_id"] for a in entry["acceptance_tests_of_no_scenario"]}, key=number):
        items.append(f"{scenario_id} is no longer a scenario of {id_of(entry)}")
    for error in sorted(entry["errors"], key=lambda e: (e["path"], e["line"] or 0)):
        where_found = text_of(error["path"]) + (f":{error['line']}" if error["line"] is not None else "")
        items.append(f"{where_found}: {error['message']}")
    return items


def titled(entry):
    return f'{id_of(entry)} "{text_of(entry["title"])}"' if entry["title"] is not None else f"{id_of(entry)} (no title)"


def check_reported_wrong(inventory_of_the_acceptance_tests, reported_wrong):
    """WAT-8, "An acceptance test reported wrong": each scenario named has an acceptance test to rewrite."""
    for scenario_id in reported_wrong:
        has_one = any(s["scenario_id"] == scenario_id and s["acceptance_test_status"] != "missing"
                      for entry in entries_of(inventory_of_the_acceptance_tests) if entry["blocked"] is None
                      for s in entry["scenarios"])
        if not has_one:
            raise Stop(f"{text_of(scenario_id)} has no acceptance test to rewrite")


def changes_of(inventory_of_the_acceptance_tests, reported_wrong=(), gaps=(), rejected=()):
    """WAT-8: the changes of the acceptance tests, in the order of the IDs, and the blocked acceptance units and
    acceptance areas that have at least one item. Each change is {"id", "kind", "line"}."""
    by_id = {id_of(entry): entry for entry in entries_of(inventory_of_the_acceptance_tests)}
    deleted = set(inventory_of_the_acceptance_tests["folders_of_acceptance_tests_with_no_file"])
    changes, blocked = [], []
    for an_id in sorted(set(by_id) | deleted, key=id_order):
        if an_id in deleted:
            if an_id not in rejected:
                changes.append({"id": an_id, "kind": "delete",
                                "line": f"delete the acceptance tests of {an_id}: {file_of(an_id)} does not exist"})
            continue
        entry = by_id[an_id]
        items = items_of(entry, reported_wrong, gaps)
        if not items:
            continue
        if entry["blocked"] is not None:
            blocked.append(f"  {titled(entry)}: {entry['blocked']}")
            continue
        if an_id in rejected:
            continue
        kind = "update" if entry["folder_of_acceptance_tests_at_head"] else "write"
        changes.append({"id": an_id, "kind": kind,
                        "line": f"{kind} the acceptance tests of {titled(entry)}: {'; '.join(items)}"})
    return {"changes": changes, "blocked": blocked}


def render(inventory_of_the_acceptance_tests, changes):
    """WAT-8: the summary, then the proposal of the acceptance tests."""
    scenarios = [s for entry in entries_of(inventory_of_the_acceptance_tests) for s in entry["scenarios"]]
    current = sum(s["acceptance_test_status"] == "current" for s in scenarios)
    lines = [f"Layer 2 at {inventory_of_the_acceptance_tests['norms_commit'][:7]}. Layer 3 at "
             f"{inventory_of_the_acceptance_tests['acceptance_commit'][:7]}: {plural(len(scenarios), 'scenario')}, "
             f"{current} with a current acceptance test; "
             f"{plural(len(changes['changes']), 'change')} of the acceptance tests; {len(changes['blocked'])} blocked."]
    if changes["changes"]:
        lines.append("Changes of the acceptance tests:")
        lines += [f"{k}. {change['line']}" for k, change in enumerate(changes["changes"], 1)]
    if changes["blocked"]:
        lines.append("Blocked:")
        lines += changes["blocked"]
    if inventory_of_the_acceptance_tests["errors"]:
        lines.append("Not a folder of acceptance tests:")
        lines += [f"  {error['message']}" for error in inventory_of_the_acceptance_tests["errors"]]
    return "\n".join(lines)


def propose(where, norms_commit, reported_wrong, rejected, gaps):
    inventory_of_the_acceptance_tests = inventory(where, norms_commit)
    check_reported_wrong(inventory_of_the_acceptance_tests, reported_wrong)
    return render(inventory_of_the_acceptance_tests,
                  changes_of(inventory_of_the_acceptance_tests, reported_wrong, gaps, rejected))


# ---------------------------------------------------------------- writing (WAT-9, WAT-11)

def scenario_ids_of(values, name):
    for value in values:
        if not SCENARIO_ID.fullmatch(value):
            raise Stop(f"{name} {text_of(value)} is not a scenario ID")
    return list(values)


def folder_ids_of(values):
    for value in values:
        if not FOLDER_ID.fullmatch(value):
            raise Stop(f"--change {text_of(value)} is not a unit ID or an area ID")
    if not values:
        raise Stop("--change is required")
    return list(dict.fromkeys(values))


def no_link_on_the_way(root, path):
    """WAT-9, WAT-12, WAT-14: no folder between the working tree and the entry `path` ("tests", "tests/<ID>" and
    those under it) is a symbolic link, so that nothing is deleted or written outside the folder of acceptance tests,
    such as in a code repository (ACU-12). Raises Stop, before anything is touched, naming the first that is."""
    parts = path.split("/")
    for k in range(1, len(parts)):
        if os.path.islink(os.path.join(root, *parts[:k])):
            raise Stop(f"{text_of('/'.join(parts[:k]))} is not a folder (ACU-6); the requester decides on it")


def delete(root, an_id):
    """WAT-9, "A change delete": deletes from the working tree every file of tests/<ID>/ that HEAD holds, when the
    proposal holds the change "delete" of ID: HEAD holds a file under the folder tests/<ID>/ and no file of its
    acceptance unit or acceptance area (WAT-5, "folders_of_acceptance_tests_with_no_file")."""
    folder = f"tests/{an_id}/"
    at_head = [p for p in ls_tree(root, "HEAD", f"tests/{an_id}") if p.startswith(folder)] \
        if FOLDER_ID.fullmatch(an_id) else []
    if not at_head or show(root, "HEAD", file_of(an_id)) is not None:
        raise Stop(f"the proposal holds no change delete of {text_of(an_id)}")
    for path in at_head:
        no_link_on_the_way(root, path)
    for path in at_head:
        full = os.path.join(root, *path.split("/"))
        if os.path.isdir(full) and not os.path.islink(full) and os.listdir(full):
            raise Stop(f"{text_of(path)} is not a regular file (ACU-6); the requester decides on it")
    deleted = []
    for path in at_head:
        full = os.path.join(root, *path.split("/"))
        if os.path.islink(full) or os.path.isfile(full):
            os.remove(full)
            deleted.append(path)
        elif os.path.isdir(full):
            os.rmdir(full)
            deleted.append(path)
    _remove_empty_folders(root, an_id)
    return deleted


def _remove_empty_folders(root, an_id):
    base = os.path.join(root, "tests", an_id)
    for folder, _, _ in sorted(os.walk(base), key=lambda x: -len(x[0])):
        try:
            os.rmdir(folder)
        except OSError:
            pass


def differing(root, folder="tests"):
    """The entries under `folder` that differ from HEAD in the working tree, or in the index, the new ones that no
    .gitignore names included: (path, bytes at HEAD or None, bytes on disk or None). An entry that HEAD does not hold
    differs, whatever it is, a folder of a nested git repository included."""
    at_head = set(ls_tree(root, "HEAD", folder))
    staged = git(root, "diff", "--cached", "--name-only", "-z", "--no-renames", "HEAD", "--", folder, binary=True)
    in_index = {p.decode("utf-8", "surrogateescape") for p in staged.stdout.split(b"\0") if p}
    on_disk = set(files_on_disk(root, folder))
    found = []
    for path in sorted(at_head | on_disk | in_index):
        old = show(root, "HEAD", path) if path in at_head else None
        new = read_on_disk(root, path)
        if path not in at_head or path not in on_disk or old != new or path in in_index:
            found.append((path, old, new))
    return found


def check(where, norms_commit, change_ids, reported_wrong, gaps):
    """WAT-11: the problems of the files written for the changes of one commit, each a line in a form of WAT-11, the
    changes in the order of the proposal and then the files outside them in the order of their paths; and the changes
    of the proposal at HEAD that the commit holds."""
    root = where["root"]
    at_head = inventory(where, norms_commit)
    check_reported_wrong(at_head, reported_wrong)
    proposal = {change["id"]: change for change in changes_of(at_head, reported_wrong, gaps)["changes"]}
    for an_id in change_ids:
        if an_id not in proposal:
            raise Stop(f"{an_id} has no change in the proposal of the acceptance tests")
    in_working_tree = inventory(where, norms_commit, worktree=True)
    by_id = {id_of(entry): entry for entry in entries_of(in_working_tree)}
    by_id_at_head = {id_of(entry): entry for entry in entries_of(at_head)}
    problems = []
    for an_id in sorted(change_ids, key=id_order):
        if proposal[an_id]["kind"] == "delete":
            left = [p for p in files_on_disk(root) if p.startswith(f"tests/{an_id}/")]
            problems += [f"{an_id}: {text_of(p)} is not deleted" for p in left]
        else:
            problems += [f"{an_id}: {item}" for item in items_of(by_id[an_id], (), gaps)]
            problems += [f"{an_id}: {scenario_id} changed, but a gap of layer 1 left it out (WAT-10)"
                         for scenario_id in left_out_and_changed(by_id_at_head[an_id], by_id[an_id], gaps)]
    folders = tuple(f"tests/{an_id}/" for an_id in change_ids)
    for path, _, _ in differing(root):
        if not path.startswith(folders):
            problems.append(f"{text_of(path)} differs from HEAD, and no change of the commit holds it (WAT-11)")
    return [proposal[an_id] for an_id in sorted(change_ids, key=id_order)], problems


def left_out_and_changed(entry_at_head, entry_in_working_tree, gaps):
    """WAT-11, "A scenario left out by a gap of layer 1": the scenario IDs of `gaps`, of this acceptance unit or
    acceptance area, in the order of their numbers, whose status or openings (the file and the two lines after the
    comment mark of each, in their order) in the working tree are not those of HEAD (WAT-10). The openings in a file
    that has the error "not UTF-8" or "not a regular file (ACU-6)" at HEAD are left out on both sides, and the status
    compared is that of the openings left: HEAD shows no opening in such a file."""
    unreadable_at_head = {error["path"] for error in entry_at_head["errors"]
                          if error["message"] in ("not UTF-8", "not a regular file (ACU-6)")}

    def kept(entry):
        found = {}
        for scenario in entry["scenarios"]:
            if scenario["scenario_id"] in gaps:
                openings = [o for o in scenario["_openings"] if o["path"] not in unreadable_at_head]
                found[scenario["scenario_id"]] = (
                    status_of(openings, scenario["_scenario_hash"], scenario["expected_opening"]),
                    [[o["path"], o["lines"]] for o in openings])
        return found
    at_head, in_working_tree = kept(entry_at_head), kept(entry_in_working_tree)
    return [scenario_id for scenario_id in sorted(at_head, key=number)
            if in_working_tree.get(scenario_id) != at_head[scenario_id]]


# ---------------------------------------------------------------- commit and rollback (WAT-12, WAT-13)

def message_of(changes):
    """WAT-12: the subject and the body of the commit message, one line per change in the order of the proposal."""
    if len(changes) == 1:
        subject = f"test: {changes[0]['kind']} the acceptance tests of {changes[0]['id']}"
    else:
        subject = "test: change the acceptance tests"
    return subject, "\n".join(change["line"] for change in changes)


def files_of_changes(root, changes):
    """WAT-12, "What a change holds": the files under each folder that differ from HEAD in the working tree, the new
    files that no .gitignore names included; for a change "delete", the files of its folder that HEAD holds."""
    paths = set()
    for change in changes:
        folder = f"tests/{change['id']}"
        if change["kind"] == "delete":
            paths |= set(ls_tree(root, "HEAD", folder))
        else:
            mine = [p for p, _, _ in differing(root, folder)]
            if not mine:
                raise Stop(f"{change['id']}: no file of tests/{change['id']}/ differs from HEAD")
            paths |= set(mine)
    # WAT-7: a folder or a submodule is never staged, so that the diff never shows as deleted an entry that the
    # command adds (ACU-75).
    entries = entries_at_head(root)
    for path in sorted(paths):
        full = os.path.join(root, *path.split("/"))
        if entries.get(path, ("",))[0] == "160000" or (os.path.isdir(full) and not os.path.islink(full)):
            raise Stop(f"{text_of(path)} is not a regular file (ACU-6)")
    return sorted(paths)


def commit(where, norms_commit, expected_head, change_ids, reported_wrong, gaps):
    """WAT-12: the checks of ACU-75, those of WAT-11, the diff, the message and the one command."""
    root = where["root"]
    branch, message = checks.checks_before_commit(root, where["acceptance_repository"], expected_head)
    if message is not None:
        raise Stop(message, code=3)
    changes, problems = check(where, norms_commit, change_ids, reported_wrong, gaps)
    if problems:
        raise Said("\n".join(problems))
    paths = files_of_changes(root, changes)
    subject, body = message_of(changes)
    command = checks.commit_command(PREFIX, root, where["acceptance_repository"], branch, expected_head, paths,
                                    subject, body)
    # ACU-75: the diff of each file, computed by the script of the module that every use case shows.
    diffs = [checks.diff_of_a_file(p, show(root, "HEAD", p), read_on_disk(root, p)) for p in paths]
    display = "\n".join(["Diff:", ""] + diffs + ["Commit:", f"    {subject}", ""]
                        + [f"    {line}" for line in body.split("\n")])
    return {"display": display, "paths": paths, "message": f"{subject}\n\n{body}", "command": command,
            "acceptance_default_branch": branch, "next": NEXT}


def _in_index(root, path):
    return git(root, "--literal-pathspecs", "ls-files", "--error-unmatch", "--", path).returncode == 0


def _take_out(root, path):
    """WAT-12, "How a file is put back", for a path where HEAD holds no entry: removed from the working tree, and
    from the index with "git rm --cached" of that one path when the index holds it."""
    no_link_on_the_way(root, path)
    full = os.path.join(root, *path.split("/"))
    if os.path.islink(full) or os.path.isfile(full):
        os.remove(full)
    elif os.path.isdir(full):
        os.rmdir(full)
    if _in_index(root, path):
        git(root, "--literal-pathspecs", "rm", "-q", "--cached", "--", path)


def _put_back(root, path, mode, blob):
    """WAT-12, "How a file is put back": the file as HEAD holds it, in the working tree and in the index with "git
    update-index --cacheinfo" of its entry at HEAD, touching no other path."""
    no_link_on_the_way(root, path)
    full = os.path.join(root, *path.split("/"))
    if os.path.islink(full) or os.path.isfile(full):
        os.remove(full)
    elif os.path.isdir(full):
        raise Stop(f"cannot put {text_of(path)} back: the working tree holds a folder there, with files that a "
                   ".gitignore names")
    data = git(root, "cat-file", "blob", blob, binary=True).stdout
    os.makedirs(os.path.dirname(full), exist_ok=True)
    if mode == "120000":
        os.symlink(os.fsdecode(data), full)
    else:
        with open(full, "wb") as f:
            f.write(data)
        os.chmod(full, 0o755 if mode == "100755" else 0o644)
    if git(root, "update-index", "--add", "--cacheinfo", f"{mode},{blob},{path}").returncode != 0:
        raise Stop(f"cannot put {text_of(path)} back in the index")


def rollback(root, change_ids):
    """WAT-12: puts back each file of the folders of the changes as HEAD holds it, and removes each new file.

    First every entry that HEAD does not hold is taken out, the deepest first, and the folders left empty with it, so
    that a file that stands where HEAD holds a folder, or a folder where HEAD holds a file, is gone before the files
    of HEAD come back. A submodule of HEAD is left as it is, and so is a folder that HEAD does not hold and that is
    not empty, such as another git repository nested in the folder: the requester decides on it."""
    restored = []
    for an_id in change_ids:
        folder = f"tests/{an_id}"
        no_link_on_the_way(root, f"{folder}/")
        entries = entries_at_head(root, folder)
        found = [path for path, _, _ in differing(root, folder)]
        for path in found:
            full = os.path.join(root, *path.split("/"))
            if path not in entries and os.path.isdir(full) and not os.path.islink(full) and os.listdir(full):
                raise Stop(f"cannot remove {text_of(path)}: it is a folder that HEAD does not hold, not a file; the "
                           "requester decides on it")
        for path in sorted((p for p in found if p not in entries), key=lambda p: (-p.count("/"), p)):
            _take_out(root, path)
        _remove_empty_folders(root, an_id)
        for path in sorted(p for p in found if p in entries and entries[p][0] != "160000"):
            _put_back(root, path, *entries[path])
        restored += found
    return sorted(restored)


# ---------------------------------------------------------------- main

def options_of(arguments):
    """The options after REPO, read in one pass from left to right."""
    found = {name: [] for name in OPTIONS}
    position = 0
    while position < len(arguments):
        name = arguments[position]
        if name not in OPTIONS:
            raise Stop(f"unknown argument {text_of(name)}")
        count = OPTIONS[name]
        values = arguments[position + 1:position + 1 + count]
        if len(values) != count:
            raise Stop(f"{name} takes a value")
        found[name].append(values[0] if count == 1 else True)
        position += 1 + count
    return found


def option(options, name):
    if len(options[name]) != 1:
        raise Stop(f"{name} is required")
    return options[name][0]


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
        print(checks.json_text(start(repo, extra)))
        return 0
    where = locate(repo)
    root = where["root"]
    if command == "delete":
        if len(rest) != 1:
            raise Stop("delete takes one unit ID or area ID")
        print(checks.json_text(delete(root, rest[0])))
        return 0
    options = options_of(rest)
    if command == "rollback":
        print(checks.json_text(rollback(root, folder_ids_of(options["--change"]))))
        return 0
    reported_wrong = scenario_ids_of(options["--reported-wrong"], "--reported-wrong")
    gaps = scenario_ids_of(options["--gap"], "--gap")
    if command == "commit":
        expected_head = option(options, "--expected-head")
        result = commit(where, norms_commit_of(where, options), expected_head, folder_ids_of(options["--change"]),
                        reported_wrong, gaps)
        print(checks.json_text(result))
        return 0
    norms_commit = norms_commit_of(where, options)
    if command == "inventory":
        print(checks.json_text(public(inventory(where, norms_commit, worktree=bool(options["--worktree"])))))
        return 0
    if command == "propose":
        print(propose(where, norms_commit, reported_wrong, options["--reject"], gaps))
        return 0
    if command == "check":
        _, problems = check(where, norms_commit, folder_ids_of(options["--change"]), reported_wrong, gaps)
        if problems:
            raise Said("\n".join(problems))
        return 0
    raise Stop(f"unknown command {text_of(command)}")


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Stop as stop:
        print(str(stop) if isinstance(stop, Said) else PREFIX + str(stop))
        sys.exit(stop.code)
