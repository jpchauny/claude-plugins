"""Compare the derived norms of the commit of layer 2 of the run with those of the commit before the last step (NRM-11).

Usage:
    python3 -I compare_derived_norms.py --norms-repository <root of the norms repository>
        --commit <commit of layer 2 of the run>

The commit of layer 2 of the run is the commit that the step made (NRM-9),
or the head from before the step when the step made none (ORC-9); never the
merge commit, nor a commit brought, of the pull of NRM-10 that the step
itself made. The last commit of a step is the first commit met along the
first parents of that commit, that commit included, that has one parent or
none and changes a file of data/, specs-repo-annotated/ or specs-derived/;
the commit before the last step is its first parent.

The types compared are the types of derived norms of the commit of layer 2
of the run (its record specs-derived/types-of-derived-norms.json, NRM-16, or
else derived_norms of its project.json, NRM-1), in their order, then those
of the commit before the last step that the first do not hold. For each,
reads specs-derived/<type>/derived-norms.jsonl (NRM-12) at both commits
through git, and lists by derived norm ID the derived norms that are new,
changed (another derived norm fingerprint) or gone. It also says when two
types are in another order than at the commit before the last step.

At the commit before the last step, the list of a type that is not one of
its types, a list that does not exist or does not meet NRM-12, and every
list when there is no commit before the last step, counts as a list with no
derived norm. At the commit of layer 2 of the run, the list of a type that
is not one of its types counts as a list with no derived norm; the list of
one of its types that does not exist or does not meet NRM-12, as NRM-12 says
of a list read alone, cannot be read; so cannot a list of one of its types
that holds a derived norm behind its norms: one that cites a norm ID that
data/tree.jsonl of that commit does not hold, or a norm hash that is not the
norm hash of that norm there. It is named with its path and the first thing
it does not meet, and the run stops (ORC-10).

The output, byte for byte, is that of NRM-11, rule 7: on standard output,
one line per type compared, the change of the order of the types, and last
`derived norms cannot be read`, `derived norms changed: yes` or `derived
norms changed: no`, exit 0; or, when the commit gives no comparison (NRM-11,
rule 2), one line on standard error, exit 1.

Runs with Python 3.9 or later and its standard library only (MTH-5).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

LIST_OF_DERIVED_NORMS_FILE_NAME = "derived-norms.jsonl"  # NRM-12
TREE_PATH = "data/tree.jsonl"  # R61; NRM-11, rule 5
RECORD_OF_THE_TYPES_OF_DERIVED_NORMS_PATH = "specs-derived/types-of-derived-norms.json"  # NRM-16
RECORD_OF_THE_TYPES_OF_DERIVED_NORMS_FIELDS = ["types_of_derived_norms"]  # NRM-16
FOLDERS_OF_A_STEP = ["data", "specs-repo-annotated", "specs-derived"]  # NRM-9, Commit of a step
TYPE_OF_DERIVED_NORMS = re.compile(r"[a-z0-9-]+")  # ORC-20
USE_CASE_OF_DERIVED_NORMS = re.compile(r"/[a-z0-9-]+:[a-z0-9-]+")  # ORC-20, NRM-1: /<module>:<use case>
DERIVED_NORM_FINGERPRINT = re.compile(r"[0-9a-f]{8}")  # NRM-14
NORM_HASH = re.compile(r"[0-9a-f]{8}")  # layers.md, Norm hash
NORM_ID = re.compile(r"[A-Z]{3,}(?:-[1-9][0-9]*)?")  # R10, R61
META_LINE_FIELDS = ["kind", "type", "last_derived_norm_number"]  # NRM-12
DERIVED_NORM_LINE_FIELDS = ["kind", "derived_norm_id", "derived_norm_fingerprint", "name", "path", "first_line",
                            "last_line", "cited_norms"]  # NRM-12
CITED_NORM_FIELDS = ["norm_id", "norm_hash"]  # NRM-12
_DERIVED_NORM_NUMBER = re.compile(r":([1-9][0-9]*)$")


class ListOfDerivedNormsError(Exception):
    """A list of derived norms that does not meet NRM-12; its message is the first thing it does not meet."""


class TypesOfDerivedNormsError(Exception):
    """Types of derived norms that cannot be read: a project.json or a derived_norms that does not meet ORC-20, or a
    record of the types of derived norms that does not meet NRM-16. For a project.json, its message is the reason of
    NRM-11, rule 7, and of NRM-16."""


class NoComparison(Exception):
    """NRM-11, rule 2: the commit of layer 2 of the run gives no comparison; its message is the reason of rule 7."""

    def __init__(self, commit: str, reason: str):
        super().__init__(reason)
        self.commit = commit
        self.reason = reason


PROJECT_JSON_CANNOT_BE_READ = "project.json cannot be read"  # NRM-11 rule 7, NRM-16
DERIVED_NORMS_DO_NOT_MEET_ORC_20 = "derived_norms of project.json does not meet ORC-20"  # NRM-11 rule 7, NRM-16


class _Object(list):
    """A JSON object as the list of its (key, value) pairs, in their order, so that the order of its fields and a
    field given twice can be checked (NRM-12, NRM-16)."""


def _reject_constant(name):
    raise ValueError(name)


def git(norms_repository: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(norms_repository), *args], capture_output=True)


def resolve_commit(norms_repository: Path, commit: str) -> str:
    result = git(norms_repository, "rev-parse", "--verify", "--quiet", "--end-of-options", f"{commit}^{{commit}}")
    if result.returncode != 0:
        raise NoComparison(commit, f"it is not a commit of {norms_repository}")
    return result.stdout.decode().strip()


def parents_of(norms_repository: Path, commit: str) -> list[str]:
    result = git(norms_repository, "rev-list", "--parents", "-n", "1", commit)
    if result.returncode != 0:
        raise NoComparison(commit, f"the parents of {commit} cannot be read")
    return result.stdout.decode().split()[1:]


def is_commit_of_a_step(norms_repository: Path, commit: str, parents: list[str]) -> bool:
    """Commit of a step: one parent or none, and a change of a file of data/, specs-repo-annotated/ or specs-derived/
    against its first parent, or such a file held when it has no parent (NRM-9)."""
    if len(parents) > 1:
        return False
    if parents:
        return git(norms_repository, "diff", "--quiet", parents[0], commit, "--", *FOLDERS_OF_A_STEP).returncode != 0
    return git(norms_repository, "ls-tree", "-r", "--name-only", commit, "--", *FOLDERS_OF_A_STEP).stdout.strip() != b""


def find_last_commit_of_a_step(norms_repository: Path, commit_of_layer_2_of_the_run: str) -> str | None:
    """NRM-11: the first commit of a step along the first parents of the commit of layer 2 of the run, that commit
    included; None when the walk meets none."""
    commit: str | None = commit_of_layer_2_of_the_run
    while commit is not None:
        parents = parents_of(norms_repository, commit)
        if is_commit_of_a_step(norms_repository, commit, parents):
            return commit
        commit = parents[0] if parents else None
    return None


def find_commit_before_the_last_step(norms_repository: Path, last_commit_of_a_step: str | None) -> str | None:
    """NRM-11: the first parent of the last commit of a step; None when there is none, or it has no parent."""
    if last_commit_of_a_step is None:
        return None
    parents = parents_of(norms_repository, last_commit_of_a_step)
    return parents[0] if parents else None


def read_file(norms_repository: Path, commit: str, path: str) -> bytes | None:
    """The bytes of the file at the commit, or None when the commit holds no file there."""
    if git(norms_repository, "cat-file", "-e", f"{commit}:{path}").returncode != 0:
        return None
    result = git(norms_repository, "cat-file", "blob", f"{commit}:{path}")
    return result.stdout if result.returncode == 0 else None


def _types_meet_orc_20(types) -> bool:
    # A JSON object of the record is an _Object, a subclass of list: only a JSON array is a list of types.
    return (type(types) is list and all(isinstance(t, str) and TYPE_OF_DERIVED_NORMS.fullmatch(t) for t in types)
            and len(set(types)) == len(types))


def _use_case_meets_orc_20(use_case) -> bool:
    return isinstance(use_case, str) and USE_CASE_OF_DERIVED_NORMS.fullmatch(use_case) is not None


def types_of_derived_norms_of_project_json(data: bytes | None) -> list[str]:
    """NRM-1, ORC-20: the type of each entry of derived_norms of a project.json, in its order; [] without
    derived_norms. Raises TypesOfDerivedNormsError when the project.json cannot be read or its derived_norms does not
    meet ORC-20, both as NRM-1 says."""
    if data is None:
        raise TypesOfDerivedNormsError(PROJECT_JSON_CANNOT_BE_READ)
    try:
        project = json.loads(data.decode("utf-8"), parse_constant=_reject_constant)
    except (ValueError, RecursionError):  # UnicodeDecodeError is a ValueError.
        raise TypesOfDerivedNormsError(PROJECT_JSON_CANNOT_BE_READ)
    if not isinstance(project, dict):
        raise TypesOfDerivedNormsError(PROJECT_JSON_CANNOT_BE_READ)
    if "derived_norms" not in project:
        return []
    entries = project["derived_norms"]
    if not isinstance(entries, list) or not all(isinstance(e, dict) for e in entries):
        raise TypesOfDerivedNormsError(DERIVED_NORMS_DO_NOT_MEET_ORC_20)
    types = [e.get("type") for e in entries]
    if not _types_meet_orc_20(types):
        raise TypesOfDerivedNormsError(DERIVED_NORMS_DO_NOT_MEET_ORC_20)
    if not all(_use_case_meets_orc_20(e.get("use_case")) for e in entries):
        raise TypesOfDerivedNormsError(DERIVED_NORMS_DO_NOT_MEET_ORC_20)
    return types


def text_of_record_of_the_types_of_derived_norms(types: list[str]) -> str:
    """NRM-16: the record of the types of derived norms that the step of layer 2 writes."""
    return json.dumps({"types_of_derived_norms": types}, ensure_ascii=False) + "\n"


def types_of_derived_norms_of_record(data: bytes | None) -> list[str]:
    """NRM-16: the types of a record of the types of derived norms. Raises TypesOfDerivedNormsError when the record
    does not exist or does not meet NRM-16."""
    if data is None:
        raise TypesOfDerivedNormsError("no record of the types of derived norms")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        raise TypesOfDerivedNormsError("the record of the types of derived norms is not UTF-8")
    if not text.endswith("\n") or "\n" in text[:-1] or "\r" in text:
        raise TypesOfDerivedNormsError("the record of the types of derived norms is not one line")
    if not (text.startswith("{") and text.endswith("}\n")):
        raise TypesOfDerivedNormsError("the record of the types of derived norms holds something before or after its "
                                       "JSON object")
    try:
        record = json.loads(text, object_pairs_hook=_Object, parse_constant=_reject_constant)
    except (ValueError, RecursionError):
        raise TypesOfDerivedNormsError("the record of the types of derived norms is not a JSON object")
    if not isinstance(record, _Object) or [key for key, _ in record] != RECORD_OF_THE_TYPES_OF_DERIVED_NORMS_FIELDS:
        raise TypesOfDerivedNormsError("the record of the types of derived norms is not the field types_of_derived_norms")
    types = dict(record)["types_of_derived_norms"]
    if not _types_meet_orc_20(types):
        raise TypesOfDerivedNormsError("the types of the record of the types of derived norms do not meet ORC-20")
    return types


def types_of_derived_norms_of_commit(norms_repository: Path, commit: str) -> list[str]:
    """Types of derived norms of a commit (NRM-11, NRM-16): those of its record when it holds one that meets NRM-16,
    otherwise those of derived_norms of its project.json (NRM-1). Raises TypesOfDerivedNormsError when neither can
    be read."""
    try:
        return types_of_derived_norms_of_record(read_file(norms_repository, commit, RECORD_OF_THE_TYPES_OF_DERIVED_NORMS_PATH))
    except TypesOfDerivedNormsError:
        return types_of_derived_norms_of_project_json(read_file(norms_repository, commit, "project.json"))


def _a_valid_string(value) -> bool:
    """A string that is valid Unicode: no lone surrogate, which a JSON escape can write."""
    if not isinstance(value, str):
        return False
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        return False
    return True


def _an_integer(value, smallest: int) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= smallest


def _breaks_a_line(character: str) -> bool:
    """A control character (Unicode category Cc), a line separator (U+2028) or a paragraph separator (U+2029)."""
    return unicodedata.category(character) in ("Cc", "Zl", "Zp")


def _fields(value, names: list[str], number: int) -> dict:
    if not isinstance(value, _Object) or [key for key, _ in value] != names:
        raise ListOfDerivedNormsError(f"line {number}: not the fields {', '.join(names)}, in this order")
    return dict(value)


def norm_hashes_of_tree(data: bytes | None) -> dict[str, str]:
    """NRM-11, rule 5: norm ID -> norm hash, the first 8 characters of the tree_hash, of each active node of
    data/tree.jsonl: a line of type node whose status is active or absent (R61). A retired node, or a node with any
    other status, holds no norm. Raises ListOfDerivedNormsError when data/tree.jsonl cannot be read."""
    cannot_be_read = ListOfDerivedNormsError(f"{TREE_PATH} cannot be read")
    if data is None:
        raise cannot_be_read
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        raise cannot_be_read
    norm_hashes: dict[str, str] = {}
    lines = text.split("\n")  # Never splitlines: a JSON string of the tree may hold U+2028 as it is (R61).
    if lines[-1] == "":
        lines.pop()
    for line in lines:
        try:
            value = json.loads(line, parse_constant=_reject_constant)
        except (ValueError, RecursionError):
            raise cannot_be_read
        if not isinstance(value, dict):
            raise cannot_be_read
        if value.get("type") == "node":
            norm_id, tree_hash = value.get("id"), value.get("tree_hash")
            if not (isinstance(norm_id, str) and isinstance(tree_hash, str)):
                raise cannot_be_read
            if value.get("status", "active") == "active":
                norm_hashes[norm_id] = tree_hash[:8]
    return norm_hashes


def check_derived_norms_against_tree(data: bytes, read_tree) -> None:
    """NRM-11, rule 5: a list that meets NRM-12 and holds a derived norm behind its norms cannot be read. read_tree
    gives the bytes of data/tree.jsonl of the same commit, or None; it is called only when the list holds a derived
    norm. Raises ListOfDerivedNormsError with the first case of rule 7 that holds."""
    lines = data.decode("utf-8")[:-1].split("\n")[1:]
    if not lines:
        return
    norm_hashes_in_tree = norm_hashes_of_tree(read_tree())
    for number, line in enumerate(lines, start=2):
        derived_norm = json.loads(line)
        for cited_norm in derived_norm["cited_norms"]:
            if cited_norm["norm_id"] not in norm_hashes_in_tree:
                raise ListOfDerivedNormsError(
                    f"line {number}: {derived_norm['derived_norm_id']} cites {cited_norm['norm_id']}, "
                    f"which {TREE_PATH} does not hold")
    for number, line in enumerate(lines, start=2):
        derived_norm = json.loads(line)
        for cited_norm in derived_norm["cited_norms"]:
            norm_hash_in_tree = norm_hashes_in_tree[cited_norm["norm_id"]]
            if cited_norm["norm_hash"] != norm_hash_in_tree:
                raise ListOfDerivedNormsError(
                    f"line {number}: {derived_norm['derived_norm_id']} cites "
                    f"{cited_norm['norm_id']}@{cited_norm['norm_hash']}, and the norm hash of "
                    f"{cited_norm['norm_id']} in {TREE_PATH} is {norm_hash_in_tree}")


def derived_norm_fingerprints_of_list_of_derived_norms(data: bytes, type_of_derived_norms: str) -> dict[str, str]:
    """NRM-12, as it says of a list read alone: derived_norm_id -> derived_norm_fingerprint of one list of derived
    norms. Reads no file that a path names and computes no derived norm fingerprint (NRM-15). Raises
    ListOfDerivedNormsError with the first thing of NRM-12 that the list does not meet."""
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        raise ListOfDerivedNormsError("not UTF-8")
    if text.startswith("﻿"):
        raise ListOfDerivedNormsError("a byte order mark")
    if text == "":
        raise ListOfDerivedNormsError("no meta line")
    if not text.endswith("\n"):
        raise ListOfDerivedNormsError("its last line is not followed by a line feed")
    if "\r" in text:
        raise ListOfDerivedNormsError("a carriage return")
    lines = text[:-1].split("\n")
    objects = []
    for number, line in enumerate(lines, start=1):
        try:
            objects.append(json.loads(line, object_pairs_hook=_Object, parse_constant=_reject_constant))
        except (ValueError, RecursionError):
            raise ListOfDerivedNormsError(f"line {number}: not a JSON object")
    meta = _fields(objects[0], META_LINE_FIELDS, 1)
    if meta["kind"] != "meta":
        raise ListOfDerivedNormsError("line 1: not the meta line")
    if meta["type"] != type_of_derived_norms:
        raise ListOfDerivedNormsError(f"line 1: its type is not {type_of_derived_norms}")
    if not _an_integer(meta["last_derived_norm_number"], 0):
        raise ListOfDerivedNormsError("line 1: last_derived_norm_number is not an integer, 0 or greater")
    derived_norm_id_form = re.compile(re.escape(type_of_derived_norms) + r":([1-9][0-9]*)")
    derived_norm_fingerprints: dict[str, str] = {}
    last_derived_norm_number = 0
    lines_by_path: dict[str, list[tuple[int, int, int]]] = {}
    for number, value in enumerate(objects[1:], start=2):
        line = _fields(value, DERIVED_NORM_LINE_FIELDS, number)
        if line["kind"] != "derived_norm":
            raise ListOfDerivedNormsError(f"line {number}: kind is not derived_norm")
        derived_norm_id = line["derived_norm_id"]
        matched = derived_norm_id_form.fullmatch(derived_norm_id) if isinstance(derived_norm_id, str) else None
        if not matched:
            raise ListOfDerivedNormsError(
                f"line {number}: derived_norm_id is not a derived norm ID of {type_of_derived_norms} (NRM-13)")
        derived_norm_number = int(matched.group(1))
        if derived_norm_number <= last_derived_norm_number:
            raise ListOfDerivedNormsError(f"line {number}: {derived_norm_id} is not after the derived norm ID before it")
        if derived_norm_number > meta["last_derived_norm_number"]:
            raise ListOfDerivedNormsError(f"line {number}: {derived_norm_id} is after last_derived_norm_number")
        last_derived_norm_number = derived_norm_number
        derived_norm_fingerprint = line["derived_norm_fingerprint"]
        if not (isinstance(derived_norm_fingerprint, str) and DERIVED_NORM_FINGERPRINT.fullmatch(derived_norm_fingerprint)):
            raise ListOfDerivedNormsError(
                f"line {number}: derived_norm_fingerprint is not 8 lower-case hex digits (NRM-14)")
        name = line["name"]
        if not (_a_valid_string(name) and any(c not in " \t" for c in name)
                and not any(_breaks_a_line(c) for c in name)):
            raise ListOfDerivedNormsError(f"line {number}: name is not a name of NRM-12")
        path = line["path"]
        if not (_a_valid_string(path) and path.startswith(f"specs-derived/{type_of_derived_norms}/")
                and path != f"specs-derived/{type_of_derived_norms}/{LIST_OF_DERIVED_NORMS_FILE_NAME}"
                and all(part not in ("", ".", "..") for part in path.split("/"))):
            raise ListOfDerivedNormsError(f"line {number}: path is not a file of the output of {type_of_derived_norms}")
        first_line, last_line = line["first_line"], line["last_line"]
        if not (_an_integer(first_line, 1) and _an_integer(last_line, 1) and first_line <= last_line):
            raise ListOfDerivedNormsError(
                f"line {number}: first_line and last_line are not line numbers, the first not after the last")
        cited_norms = line["cited_norms"]
        # A JSON object is an _Object, a subclass of list: only a JSON array is a list of cited norms (row 20).
        if type(cited_norms) is not list or not cited_norms:
            raise ListOfDerivedNormsError(f"line {number}: cited_norms is not a list of at least one norm")
        last_norm_id = None
        for cited in cited_norms:
            cited_norm = _fields(cited, CITED_NORM_FIELDS, number)
            if not (isinstance(cited_norm["norm_id"], str) and NORM_ID.fullmatch(cited_norm["norm_id"])
                    and isinstance(cited_norm["norm_hash"], str) and NORM_HASH.fullmatch(cited_norm["norm_hash"])):
                raise ListOfDerivedNormsError(f"line {number}: a cited norm is not a norm ID and its norm hash")
            if last_norm_id is not None and last_norm_id >= cited_norm["norm_id"]:
                raise ListOfDerivedNormsError(f"line {number}: cited_norms is not in the order of the norm IDs, each once")
            last_norm_id = cited_norm["norm_id"]
        lines_by_path.setdefault(path, []).append((first_line, last_line, number))
        derived_norm_fingerprints[derived_norm_id] = derived_norm_fingerprint
    for ranges in lines_by_path.values():  # Row 22: the paths in the order in which the list first names them.
        ranges.sort()
        for k in range(1, len(ranges)):
            if ranges[k][0] <= ranges[k - 1][1]:
                lower, higher = sorted((ranges[k - 1][2], ranges[k][2]))
                raise ListOfDerivedNormsError(f"lines {lower} and {higher}: two derived norms share a line")
    return derived_norm_fingerprints


def order_of_derived_norm_id(derived_norm_id: str) -> tuple:
    match = _DERIVED_NORM_NUMBER.search(derived_norm_id)
    return (int(match.group(1)), derived_norm_id) if match else (0, derived_norm_id)


def path_of_list_of_derived_norms(type_of_derived_norms: str) -> str:
    return f"specs-derived/{type_of_derived_norms}/{LIST_OF_DERIVED_NORMS_FILE_NAME}"


def compare_type_of_derived_norms(norms_repository: Path, type_of_derived_norms: str,
                                  commit_of_layer_2_of_the_run: str,
                                  types_of_derived_norms_of_commit_of_layer_2_of_the_run: list[str],
                                  commit_before_the_last_step: str | None,
                                  types_of_derived_norms_of_commit_before_the_last_step: list[str]) -> dict:
    """NRM-11, rules 3 to 5, for one type: new, changed and gone, or the error of a list that cannot be read at the
    commit of layer 2 of the run."""
    named = type_of_derived_norms in types_of_derived_norms_of_commit_of_layer_2_of_the_run
    result = {"type": type_of_derived_norms, "named_by_derived_norms": named, "new": [], "changed": [], "gone": [],
              "error": None}
    path = path_of_list_of_derived_norms(type_of_derived_norms)
    derived_norm_fingerprints_at_commit_of_layer_2_of_the_run: dict[str, str] = {}
    if named:  # Rule 5: the list of a type that is not one of its types counts as a list with no derived norm.
        list_of_derived_norms_at_commit_of_layer_2_of_the_run = read_file(
            norms_repository, commit_of_layer_2_of_the_run, path)
        try:
            if list_of_derived_norms_at_commit_of_layer_2_of_the_run is None:
                raise ListOfDerivedNormsError("it does not exist")
            derived_norm_fingerprints_at_commit_of_layer_2_of_the_run = \
                derived_norm_fingerprints_of_list_of_derived_norms(
                    list_of_derived_norms_at_commit_of_layer_2_of_the_run, type_of_derived_norms)
            check_derived_norms_against_tree(
                list_of_derived_norms_at_commit_of_layer_2_of_the_run,
                lambda: read_file(norms_repository, commit_of_layer_2_of_the_run, TREE_PATH))
        except ListOfDerivedNormsError as error:
            result["error"] = f"{path} at {commit_of_layer_2_of_the_run}: {error}"
            return result
    derived_norm_fingerprints_at_commit_before_the_last_step: dict[str, str] = {}
    if (commit_before_the_last_step is not None
            and type_of_derived_norms in types_of_derived_norms_of_commit_before_the_last_step):  # Rule 4.
        list_of_derived_norms_at_commit_before_the_last_step = read_file(
            norms_repository, commit_before_the_last_step, path)
        if list_of_derived_norms_at_commit_before_the_last_step is not None:
            try:
                derived_norm_fingerprints_at_commit_before_the_last_step = \
                    derived_norm_fingerprints_of_list_of_derived_norms(
                        list_of_derived_norms_at_commit_before_the_last_step, type_of_derived_norms)
            except ListOfDerivedNormsError:
                pass
    derived_norm_ids_at_commit_of_layer_2_of_the_run = set(derived_norm_fingerprints_at_commit_of_layer_2_of_the_run)
    derived_norm_ids_at_commit_before_the_last_step = set(derived_norm_fingerprints_at_commit_before_the_last_step)
    result["new"] = sorted(
        derived_norm_ids_at_commit_of_layer_2_of_the_run - derived_norm_ids_at_commit_before_the_last_step,
        key=order_of_derived_norm_id)
    result["gone"] = sorted(
        derived_norm_ids_at_commit_before_the_last_step - derived_norm_ids_at_commit_of_layer_2_of_the_run,
        key=order_of_derived_norm_id)
    result["changed"] = sorted(
        (derived_norm_id for derived_norm_id
         in derived_norm_ids_at_commit_of_layer_2_of_the_run & derived_norm_ids_at_commit_before_the_last_step
         if derived_norm_fingerprints_at_commit_before_the_last_step[derived_norm_id]
         != derived_norm_fingerprints_at_commit_of_layer_2_of_the_run[derived_norm_id]),
        key=order_of_derived_norm_id,
    )
    return result


def order_of_the_types_changed(types_of_derived_norms_of_commit_of_layer_2_of_the_run: list[str],
                               types_of_derived_norms_of_commit_before_the_last_step: list[str]) -> bool:
    """NRM-11, rule 6: two types of both commits in one order before and in the other now."""
    types_of_both_commits = (set(types_of_derived_norms_of_commit_of_layer_2_of_the_run)
                             & set(types_of_derived_norms_of_commit_before_the_last_step))
    return ([t for t in types_of_derived_norms_of_commit_of_layer_2_of_the_run if t in types_of_both_commits]
            != [t for t in types_of_derived_norms_of_commit_before_the_last_step if t in types_of_both_commits])


def is_change(result: dict) -> bool:
    return bool(result["new"] or result["changed"] or result["gone"])


def compare(norms_repository: Path, commit_of_layer_2_of_the_run: str) -> dict:
    """NRM-11: the whole comparison. Raises NoComparison when the commit gives none (rule 2), with the first reason
    that holds in the order of rule 7, outcome 2: the parents of a commit of the walk before project.json."""
    try:
        last_commit_of_a_step = find_last_commit_of_a_step(norms_repository, commit_of_layer_2_of_the_run)
        commit_before_the_last_step = find_commit_before_the_last_step(norms_repository, last_commit_of_a_step)
    except NoComparison as no_comparison:  # Rule 7: the message names the commit of layer 2 of the run.
        raise NoComparison(commit_of_layer_2_of_the_run, no_comparison.reason)
    try:
        types_of_derived_norms_of_commit_of_layer_2_of_the_run = types_of_derived_norms_of_commit(
            norms_repository, commit_of_layer_2_of_the_run)
    except TypesOfDerivedNormsError as error:  # Rule 2: no comparison.
        raise NoComparison(commit_of_layer_2_of_the_run, str(error))
    types_of_derived_norms_of_commit_before_the_last_step: list[str] = []
    if commit_before_the_last_step is not None:
        try:
            types_of_derived_norms_of_commit_before_the_last_step = types_of_derived_norms_of_commit(
                norms_repository, commit_before_the_last_step)
        except TypesOfDerivedNormsError:  # Rule 4: no types of derived norms.
            types_of_derived_norms_of_commit_before_the_last_step = []
    types_compared = types_of_derived_norms_of_commit_of_layer_2_of_the_run + [
        t for t in types_of_derived_norms_of_commit_before_the_last_step
        if t not in types_of_derived_norms_of_commit_of_layer_2_of_the_run]
    results = [compare_type_of_derived_norms(norms_repository, t, commit_of_layer_2_of_the_run,
                                             types_of_derived_norms_of_commit_of_layer_2_of_the_run,
                                             commit_before_the_last_step,
                                             types_of_derived_norms_of_commit_before_the_last_step)
               for t in types_compared]
    return {"commit_of_layer_2_of_the_run": commit_of_layer_2_of_the_run,
            "last_commit_of_a_step": last_commit_of_a_step,
            "commit_before_the_last_step": commit_before_the_last_step,
            "types_of_derived_norms_of_commit_of_layer_2_of_the_run":
                types_of_derived_norms_of_commit_of_layer_2_of_the_run,
            "types_of_derived_norms_of_commit_before_the_last_step":
                types_of_derived_norms_of_commit_before_the_last_step,
            "comparisons_of_types_of_derived_norms": results,
            "order_of_the_types_changed": order_of_the_types_changed(
                types_of_derived_norms_of_commit_of_layer_2_of_the_run,
                types_of_derived_norms_of_commit_before_the_last_step),
            "derived_norms_changed": any(is_change(r) for r in results),
            "derived_norms_readable": not any(r["error"] for r in results)}


def text_of(comparison: dict) -> str:
    """NRM-11, rule 7, outcome 1: the lines of the standard output."""
    results = comparison["comparisons_of_types_of_derived_norms"]
    lines = []
    if not results:
        lines.append("no type of derived norms")
    for result in results:
        label = result["type"] if result["named_by_derived_norms"] else f"{result['type']} (no longer in derived_norms)"
        if result["error"]:
            lines.append(f"{label}: cannot be read: {result['error']}")
        elif not is_change(result):
            lines.append(f"{label}: no change")
        else:
            lines.append(f"{label}: {len(result['new'])} new, {len(result['changed'])} changed, {len(result['gone'])} gone")
            for state in ("new", "changed", "gone"):
                if result[state]:
                    lines.append(f"  {state}: {', '.join(result[state])}")
    if comparison["order_of_the_types_changed"]:
        lines.append("order of the types changed: "
                     f"{', '.join(comparison['types_of_derived_norms_of_commit_before_the_last_step'])} -> "
                     f"{', '.join(comparison['types_of_derived_norms_of_commit_of_layer_2_of_the_run'])}")
    if not comparison["derived_norms_readable"]:
        lines.append("derived norms cannot be read")
    else:
        changed = comparison["derived_norms_changed"] or comparison["order_of_the_types_changed"]
        lines.append(f"derived norms changed: {'yes' if changed else 'no'}")
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    # NRM-11, rule 7, outcome 3: no abbreviated option and no --help, so any other argument exits with status 2.
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0], allow_abbrev=False, add_help=False)
    parser.add_argument("--norms-repository", required=True, type=Path)
    parser.add_argument("--commit", required=True,
                        help="the commit of layer 2 of the run: the commit of NRM-9, or the head from before the step when it made "
                             "none; never the merge commit of the pull of NRM-10 that the step made")
    arguments = parser.parse_args(argv)
    norms_repository = arguments.norms_repository.resolve()
    try:
        if not norms_repository.is_dir() or git(norms_repository, "rev-parse", "--git-dir").returncode != 0:
            raise NoComparison(arguments.commit, f"{norms_repository} is not a git repository")
        comparison = compare(norms_repository, resolve_commit(norms_repository, arguments.commit))
    except NoComparison as no_comparison:  # NRM-11, rule 7, outcome 2.
        sys.stderr.buffer.write(
            (f"norms-management: the derived norms of {no_comparison.commit} of the norms repository cannot be "
             f"compared (NRM-11): {no_comparison.reason}; the run stops after layer 2 (ORC-10)\n").encode("utf-8"))
        return 1
    sys.stdout.buffer.write(text_of(comparison).encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
