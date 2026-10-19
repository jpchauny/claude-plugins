"""The examples of the three spec documents, as test fixtures.

The examples E1-E89 are requirements and test cases. This module reads
them from the specs, byte for byte, and writes them as fixtures under
tests/fixtures/. The specs are the source: the fixtures are never edited
by hand. Run

    uv run python tests/spec_examples.py

to write them again after a spec changed. tests/test_examples.py checks
that the fixtures on disk are exactly what this module makes of the
specs, so the two cannot drift apart.

Two kinds of example, two fixture layouts:

* Annotation examples (specs/norms-tree.md, specs/norms-annotation-cases.md):
  each `### E<n>.` section holds one or more pairs of ```markdown fences,
  a foundation text and its annotated copy. The first pair is fixture
  `E<nn>`, the next ones `E<nn>b`, `E<nn>c`, ...

      input.md     the foundation text
      expected.md  its annotated copy
      notes.md     only when the fixture is not annotated with the
                   defaults (prefix TYP, no file marker): it holds
                   `prefix: <P>` and/or `file_marker: true`

  The options come from the spec's own output: an annotated copy that
  starts with a bare prefix marker (`⟬TYP⟭`) shows the file marker.

* Version examples (specs/norms-versions.md): each is a sequence of
  foundation versions built one after the other. Fixture `E<nn>`
  holds one folder per version:

      v<k>/input/<path>     each foundation file of version k
      v<k>/expected/<path>  its annotated copy (with the file marker)
      v<k>/statuses.md      from v2 on: the spec's list of statuses, and
                            its `retired_prefixes` line when there is one
      v<k>/report.md        when the spec shows it: data/report.md
                            without its `Foundation` line

E20 (a folder) has no text to annotate: its fixture is notes.md alone,
written by hand, and its test builds a small foundation.

This module is tooling: its prose names examples and fixtures, so
tests/traceability.py leaves it out of the check of the format.

Spec: R28
"""

from __future__ import annotations

import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPECS = ROOT / "specs"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

ANNOTATION_SPECS = ("norms-tree.md", "norms-annotation-cases.md")
VERSION_SPECS = ("norms-versions.md",)

# Fixtures written by hand, kept as they are.
HAND_WRITTEN = {"E20"}

DEFAULT_PREFIX = "TYP"

_SECTION_RE = re.compile(r"^### (E\d+)\.[^\n]*\n", re.M)
_PAIR_RE = re.compile(
    r"^(?P<f1>`{3,})markdown\n(?P<src>.*?)^(?P=f1)\n\n"
    r"(?P<f2>`{3,})markdown\n(?P<ann>.*?)^(?P=f2)\n",
    re.M | re.S,
)
_VERSION_TOKEN_RE = re.compile(
    r"^v(?P<v>\d+), `(?P<path>[^`\n]+)`:\n\n"
    r"(?P<f1>`{3,})markdown\n(?P<src>.*?)^(?P=f1)\n\n"
    r"(?P<f2>`{3,})markdown\n(?P<ann>.*?)^(?P=f2)\n"
    r"|^Statuses at v(?P<sv>\d+):\n\n(?P<st>(?:- [^\n]*\n)+)"
    r"|^(?P<rp>`retired_prefixes`: [^\n]*\n)"
    r"|^`data/report\.md` at v(?P<rv>\d+), without its `Foundation` line:\n\n"
    r"(?P<f3>`{3,})markdown\n(?P<rep>.*?)^(?P=f3)\n",
    re.M | re.S,
)
_FILE_MARKER_RE = re.compile(r"(?:﻿)?⟬([A-Z]+)⟭(?:\r\n|\r|\n)")
_ID_RE = re.compile(r"⟬([A-Z]+)-[0-9]+(?: begin| end)?⟭")


@dataclass
class Pair:
    """One foundation text and its annotated copy."""

    name: str  # fixture name: E03, E03b, ...
    spec: str  # the spec file it comes from
    source: bytes
    expected: bytes

    @property
    def file_marker(self) -> bool:
        return _FILE_MARKER_RE.match(self.expected.decode("utf-8")) is not None

    @property
    def prefix(self) -> str:
        text = self.expected.decode("utf-8")
        found = _FILE_MARKER_RE.match(text) or _ID_RE.search(text)
        return found.group(1) if found else DEFAULT_PREFIX


@dataclass
class Version:
    """One foundation version of a version example."""

    number: int
    files: dict[str, bytes] = field(default_factory=dict)  # path -> foundation bytes
    annotated: dict[str, bytes] = field(default_factory=dict)  # path -> annotated bytes
    statuses: str | None = None  # the spec's list, plus its retired_prefixes line
    report: str | None = None  # data/report.md without its Foundation line


@dataclass
class VersionExample:
    name: str  # E69, ...
    versions: list[Version]


def fixture_name(number: int, index: int) -> str:
    """E3, pair 0 -> E03; pair 1 -> E03b; pair 2 -> E03c."""
    return f"E{number:02d}" + ("" if index == 0 else chr(ord("a") + index))


def _sections(spec: str) -> list[tuple[str, str]]:
    """The `### E<n>.` sections of a spec: (E<n>, body up to the next heading of level 1-3)."""
    text = (SPECS / spec).read_text(encoding="utf-8")
    heads = list(_SECTION_RE.finditer(text))
    out = []
    for k, head in enumerate(heads):
        end = heads[k + 1].start() if k + 1 < len(heads) else len(text)
        body = text[head.end() : end]
        # a section ends at the next heading of level 1-3 outside a fence
        stop = _next_heading(body)
        out.append((head.group(1), body[:stop]))
    return out


def _next_heading(body: str) -> int:
    """Offset of the first `#`, `##` or `###` heading outside a fence."""
    fence: str | None = None
    pos = 0
    for line in body.splitlines(keepends=True):
        stripped = line.rstrip("\n")
        ticks = re.match(r"`{3,}", stripped)
        if fence is None and ticks:
            fence = ticks.group(0)
        elif fence is not None and stripped == fence:
            fence = None
        elif fence is None and re.match(r"#{1,3} ", stripped):
            return pos
        pos += len(line)
    return len(body)


def example_ids() -> list[str]:
    """Every example heading of the three specs, in document order."""
    ids: list[str] = []
    for spec in (*ANNOTATION_SPECS, *VERSION_SPECS):
        ids += [eid for eid, _ in _sections(spec)]
    return ids


def annotation_pairs() -> list[Pair]:
    """Every input/annotated pair of the annotation specs."""
    pairs: list[Pair] = []
    for spec in ANNOTATION_SPECS:
        for eid, body in _sections(spec):
            number = int(eid[1:])
            for index, m in enumerate(_PAIR_RE.finditer(body)):
                pairs.append(
                    Pair(
                        fixture_name(number, index),
                        spec,
                        m.group("src").encode("utf-8"),
                        m.group("ann").encode("utf-8"),
                    )
                )
    return pairs


def version_examples() -> list[VersionExample]:
    """Every example of the versions spec, version by version."""
    examples: list[VersionExample] = []
    for spec in VERSION_SPECS:
        for eid, body in _sections(spec):
            versions: dict[int, Version] = {}
            last: Version | None = None
            for m in _VERSION_TOKEN_RE.finditer(body):
                if m.group("v"):
                    n = int(m.group("v"))
                    last = versions.setdefault(n, Version(n))
                    last.files[m.group("path")] = m.group("src").encode("utf-8")
                    last.annotated[m.group("path")] = m.group("ann").encode("utf-8")
                elif m.group("sv"):
                    last = versions[int(m.group("sv"))]
                    last.statuses = m.group("st")
                elif m.group("rp"):
                    assert last is not None and last.statuses is not None, eid
                    last.statuses += "\n" + m.group("rp")
                else:
                    versions[int(m.group("rv"))].report = m.group("rep")
            numbers = sorted(versions)
            assert numbers == list(range(1, len(numbers) + 1)), (eid, numbers)
            examples.append(VersionExample(eid, [versions[n] for n in numbers]))
    return examples


def fixture_files() -> dict[str, bytes]:
    """Every generated fixture file, by path relative to tests/fixtures."""
    files: dict[str, bytes] = {}
    for pair in annotation_pairs():
        files[f"{pair.name}/input.md"] = pair.source
        files[f"{pair.name}/expected.md"] = pair.expected
        options = []
        if pair.prefix != DEFAULT_PREFIX:
            options.append(f"prefix: {pair.prefix}")
        if pair.file_marker:
            options.append("file_marker: true")
        if options:
            files[f"{pair.name}/notes.md"] = (
                f"# {pair.name}\n\n"
                f"Generated from specs/{pair.spec} by tests/spec_examples.py.\n"
                "This example is annotated with:\n\n" + "".join(f"{o}\n" for o in options)
            ).encode("utf-8")
    for example in version_examples():
        for version in example.versions:
            base = f"{example.name}/v{version.number}"
            for path, data in version.files.items():
                files[f"{base}/input/{path}"] = data
                files[f"{base}/expected/{path}"] = version.annotated[path]
            if version.statuses is not None:
                files[f"{base}/statuses.md"] = version.statuses.encode("utf-8")
            if version.report is not None:
                files[f"{base}/report.md"] = version.report.encode("utf-8")
    return files


def fixture_options(case: str) -> tuple[str, bool]:
    """(prefix, file_marker) of an annotation fixture, from its notes.md."""
    notes = FIXTURES / case / "notes.md"
    text = notes.read_text(encoding="utf-8") if notes.exists() else ""
    prefix = re.search(r"^prefix: ([A-Z]+)$", text, re.M)
    marker = re.search(r"^file_marker: true$", text, re.M)
    return (prefix.group(1) if prefix else DEFAULT_PREFIX), marker is not None


def files_on_disk() -> dict[str, bytes]:
    """The fixture files on disk, hand-written ones left out."""
    return {
        p.relative_to(FIXTURES).as_posix(): p.read_bytes()
        for p in sorted(FIXTURES.rglob("*"))
        if p.is_file() and p.relative_to(FIXTURES).parts[0] not in HAND_WRITTEN
    }


def write_fixtures() -> None:
    """Write every fixture from the specs, removing the ones the specs no longer hold."""
    wanted = fixture_files()
    for case in FIXTURES.iterdir():
        if case.is_dir() and case.name not in HAND_WRITTEN:
            shutil.rmtree(case)
    for rel, data in wanted.items():
        path = FIXTURES / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


if __name__ == "__main__":
    write_fixtures()
    print(f"wrote {len(fixture_files())} fixture files under {FIXTURES}", file=sys.stderr)
