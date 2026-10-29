"""The fingerprints and citations of the acceptance repository, shared by the scripts of this module.

Spec: specs/module.md of acceptance-management, section "Hashes and
citations": the fingerprint of ACU-51, the unit hash of ACU-52, the area hash
of ACU-53, the scenarios and the scenario hash of ACU-54, and the citations of
ACU-56. A fingerprint is computed here, never by the model, and never stored
(ACU-51).

API (every function that takes `data` takes the bytes or the text of one file):

    lines_of(data)        -> list[str]          steps 1 to 4 of ACU-51
    fingerprint(lines)    -> str                steps 6 to 8 of ACU-51, on the lines of a range
    unit_hash(data)       -> str | None         ACU-52; None when no line is "## Narrative"
    area_hash(data)       -> str | None         ACU-53; None when no line is "## Purpose"
    scenarios(data)       -> list[Scenario]     ACU-54, in the order of the file
    forbidden_lines(data) -> list[int]          ACU-54: the numbers, from 1, of the lines of the
                                                "gherkin" block that start with a keyword it may not hold
    norm_citations(data)  -> list[tuple[str, str, str]]  the norm citations of "## Norms" (ACU-8):
                                                (norm ID, norm hash, reason), in the order of the file
    citations(data)       -> list[tuple[str, str]]  every citation of an acceptance unit, an
                                                acceptance area or a scenario in a file (ACU-56):
                                                (unit ID, area ID or scenario ID; its unit hash,
                                                area hash or scenario hash)

A Scenario has these fields: "scenario_id", its scenario ID ("SC-5"), or None
when its tag lines hold not exactly one tag "@SC-<n>" (ACU-50); "name"; "tags",
every tag of its tag lines, in order, with its "@"; "norms", the norm IDs of
its tags "@<norm ID>"; "acceptance_units", the unit IDs of its tags
"@unit:<unit ID>"; "scenario_hash", its scenario hash; "line", the number, from
1, of its first line in the file.

Usage as a command, to print the hashes of files:

    python3 -I acceptance_hashes.py <file>...
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from dataclasses import dataclass, asdict

NORM_ID = r"[A-Z]{3,}(?:-[1-9][0-9]*)?"  # ACU-56, R61
NORM_TAG = re.compile(rf"^@({NORM_ID})$")
ACCEPTANCE_UNIT_TAG = re.compile(r"^@unit:(AU-[1-9][0-9]*)$")
SC_TAG = re.compile(r"^@(SC-[1-9][0-9]*)$")
NORM_CITATION = re.compile(rf"^- ({NORM_ID})@([0-9a-f]{{8}}): (\S.*)$")  # ACU-8, ACU-56
# ACU-56, "a citation found in a line": an ID and "@" and 8 lower-case hex digits, between two boundaries: before
# the ID the start of the line or a character that is not a letter or a number of Unicode, "_" or "-"; after the 8
# hex digits the end of the line or such a character. The one definition of it: the evidence run and every use
# case of this module use these two.
CITATION = re.compile(r"(?<![\w-])((?:AU|AA|SC)-[1-9][0-9]*)@([0-9a-f]{8})(?![\w-])")
NORM_CITATION_IN_LINE = re.compile(rf"(?<![\w-])({NORM_ID})@([0-9a-f]{{8}})(?![\w-])")
FORBIDDEN = ("Feature:", "Rule:", "Background:", "Example:", "Scenario Outline:", "Scenario Template:",
             "Examples:", "Scenarios:")  # ACU-54


@dataclass
class Scenario:
    scenario_id: str | None
    name: str
    tags: list[str]
    norms: list[str]
    acceptance_units: list[str]
    scenario_hash: str
    line: int


def _text(data) -> str:
    if isinstance(data, bytes):
        return data.decode("utf-8")
    return data


def lines_of(data) -> list[str]:
    """Steps 1 to 4 of ACU-51: decode as UTF-8, replace each "\\r\\n" by "\\n", split at each "\\n",
    and remove the spaces and tabs at the end of each line. Bytes that are not UTF-8 raise
    UnicodeDecodeError."""
    text = _text(data).replace("\r\n", "\n")
    return [line.rstrip(" \t") for line in text.split("\n")]


def fingerprint(lines: list[str]) -> str:
    """Steps 6 to 8 of ACU-51, on the lines of the range."""
    lines = list(lines)
    while lines and lines[-1] == "":
        lines.pop()
    return hashlib.sha256("".join(line + "\n" for line in lines).encode("utf-8")).hexdigest()[:8]


def _from_heading(data, heading: str) -> str | None:
    lines = lines_of(data)
    if heading not in lines:
        return None
    return fingerprint(lines[lines.index(heading):])


def unit_hash(data) -> str | None:
    """ACU-52: the fingerprint from the first line that is exactly "## Narrative" to the end of the file."""
    return _from_heading(data, "## Narrative")


def area_hash(data) -> str | None:
    """ACU-53: the fingerprint from the first line that is exactly "## Purpose" to the end of the file."""
    return _from_heading(data, "## Purpose")


def _section(lines: list[str], heading: str) -> tuple[int, int] | None:
    """The indexes [start, end) of the lines after the line `heading`, up to the next heading of level 2."""
    if heading not in lines:
        return None
    start = lines.index(heading) + 1
    end = start
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    return start, end


def _gherkin_block(lines: list[str]) -> tuple[int, int] | None:
    """The indexes [first line inside, closing fence) of the first "gherkin" block of "## Scenarios"."""
    section = _section(lines, "## Scenarios")
    if section is None:
        return None
    start, end = section
    for i in range(start, end):
        if lines[i].strip() == "```gherkin":
            for j in range(i + 1, end):
                if lines[j].strip() == "```":
                    return i + 1, j
            return i + 1, end
    return None


def _starts(line: str, prefix: str) -> bool:
    return line.lstrip(" \t").startswith(prefix)


def forbidden_lines(data) -> list[int]:
    """ACU-54: the numbers, from 1, of the lines of the "gherkin" block that start with a keyword it may not hold."""
    lines = lines_of(data)
    block = _gherkin_block(lines)
    if block is None:
        return []
    return [i + 1 for i in range(*block) if any(_starts(lines[i], k) for k in FORBIDDEN)]


def scenarios(data) -> list[Scenario]:
    """ACU-54: the scenarios of the "gherkin" block of "## Scenarios", each with its scenario hash."""
    lines = lines_of(data)
    block = _gherkin_block(lines)
    if block is None:
        return []
    first, fence = block
    heads = [i for i in range(first, fence) if _starts(lines[i], "Scenario:")]
    starts = []
    for head in heads:
        start = head
        while start - 1 >= first and _starts(lines[start - 1], "@"):
            start -= 1
        starts.append(start)
    found = []
    for k, head in enumerate(heads):
        start = starts[k]
        end = starts[k + 1] if k + 1 < len(heads) else fence
        tags = [tag for line in lines[start:head] for tag in line.split()]
        ids = [m.group(1) for m in map(SC_TAG.match, tags) if m]
        found.append(Scenario(
            scenario_id=ids[0] if len(ids) == 1 else None,
            name=lines[head].lstrip(" \t")[len("Scenario:"):].strip(" \t"),
            tags=tags,
            norms=[m.group(1) for m in map(NORM_TAG.match, tags) if m],
            acceptance_units=[m.group(1) for m in map(ACCEPTANCE_UNIT_TAG.match, tags) if m],
            scenario_hash=fingerprint(lines[start:end]),
            line=start + 1,
        ))
    return found


def norm_citations(data) -> list[tuple[str, str, str]]:
    """The norm citations of "## Norms" of the file of an acceptance unit (ACU-8, ACU-56): (norm ID, norm hash,
    reason)."""
    lines = lines_of(data)
    section = _section(lines, "## Norms")
    if section is None:
        return []
    return [m.groups() for m in map(NORM_CITATION.match, lines[slice(*section)]) if m]


def citations(data) -> list[tuple[str, str]]:
    """Every citation of an acceptance unit, an acceptance area or a scenario in a file (ACU-56), as (its unit ID,
    area ID or scenario ID, its unit hash, area hash or scenario hash), in order."""
    return CITATION.findall(_text(data))


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__.split("Usage as a command")[1].strip(), file=sys.stderr)
        return 2
    for path in argv:
        with open(path, "rb") as f:
            data = f.read()
        print(json.dumps({"path": path, "unit_hash": unit_hash(data), "area_hash": area_hash(data),
                          "scenarios": [asdict(s) for s in scenarios(data)]}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
