"""Traceability from the code to the specs (tests/traceability.py).

Every R, U and E that src/ and tests/ name exists in the specs, every
D-number is an implementation note or a pointer of
docs/generator-decisions.md, every citation has the one format (a `Spec:`
line ending a docstring, or a `# R39: <reason> (E41)` comment), every test
cites what it checks, and docs/traceability.md is up to date. After the
code, the tests or the specs change, run
`uv run python tests/traceability.py`.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import traceability


def test_spec_ids_are_contiguous() -> None:
    """The specs define R1-R64, U1-U7 and E1-E89, each once."""
    entries = traceability.specs()
    for kind, last in (("R", 64), ("U", 7), ("E", 89)):
        ids = sorted(int(i[1:]) for i in entries if i[0] == kind)
        assert ids == list(range(1, last + 1)), kind


def test_every_citation_exists() -> None:
    """No comment, docstring or string names an id that the specs and the notes lack."""
    assert traceability.problems() == []


def test_every_citation_has_the_format() -> None:
    """No R, U, E or D token of a docstring or a comment is outside a `Spec:` line, a `# R39:` comment or a `Note:`."""
    assert traceability.format_problems() == []


def test_every_test_cites_what_it_checks() -> None:
    """Every test function has a `Spec:` line, in its docstring or its class's, or a `# R39:` comment."""
    assert traceability.untraced_tests() == []


GOOD = '''"""A module.

Note: D2

Spec: R3, R19, U6 (E20)
"""


def f(x):
    """Only examples.

    Spec: (E7, E20)
    """
    if x:  # R39: an empty item's blank line, which goes on
        # over this line (E41, E42); Note: D2
        return 1
    return 0  # noqa: E731
'''


def _check(tmp_path: Path, text: str) -> tuple[list[str], list[str]]:
    path = tmp_path / "m.py"
    path.write_text(text, encoding="utf-8")
    cites, bad = traceability._analyse(path)
    return sorted({f"{c.id}@{c.scope}" for c in cites}), bad


@pytest.mark.parametrize(
    "text",
    [
        '"""Prose citing R3.\n\nSpec: R3\n"""\n',
        '"""Prose (R3).\n"""\n',
        '"""A range.\n\nSpec: R3-R5\n"""\n',
        '"""Unsorted.\n\nSpec: R5, R3\n"""\n',
        '"""U before R.\n\nSpec: U1, R3\n"""\n',
        '"""Examples outside parentheses.\n\nSpec: R3, E5\n"""\n',
        '"""Two lines.\n\nSpec: R3\n\nSpec: R4\n"""\n',
        '"""Not last.\n\nSpec: R3\n\nMore prose.\n"""\n',
        '"""Bare D-number, D2.\n\nSpec: R3\n"""\n',
        "x = 1  # a trailing citation (R3)\n",
        "x = 1  # see R3: the head must come first\n",
        "x = 1  # (E5)\n",
        "x = 1  # R3: an example outside parentheses, E5\n",
        "x = 1  # R3: a range of examples (E5-E7)\n",
        "# Spec: R3\nx = 1\n",
        "x = 1  # noqa: E501 R3\n",
        "x = 1  # noqa: E501 written as prose, R3\n",
    ],
)
def test_every_other_form_is_a_problem(tmp_path: Path, text: str) -> None:
    """Prose citations, ranges, unsorted ids, a misplaced Spec: line and a comment without its head are refused."""
    _, bad = _check(tmp_path, text)
    assert bad, text


def test_the_format_cites_by_scope(tmp_path: Path) -> None:
    """Spec: lines cite for their module, class or function; a `# R39:` comment for its scope."""
    cites, bad = _check(tmp_path, GOOD)
    assert bad == []
    assert cites == sorted(
        ["R3@(module)", "R19@(module)", "U6@(module)", "E20@(module)", "E7@f", "E20@f", "R39@f", "E41@f", "E42@f"]
    )


def test_a_noqa_hides_only_its_linter_codes(tmp_path: Path) -> None:
    """An id that does not exist after `# noqa: <codes>` is still found by the existence check."""
    missing = "R" + "999"  # spelled apart, so that this file names no id the specs lack
    line = traceability._NOQA_RE.sub("", f"x = 1  # noqa: E501, E731 {missing}\n")
    assert [m.group(0) for m in traceability._CITE_RE.finditer(line)] == [missing]


def test_a_comment_above_a_method_cites_for_the_method(tmp_path: Path) -> None:
    """A `# R39:` comment just above a method belongs to that method, not to its class."""
    text = (
        "class TestX:\n"
        "    def test_a(self):\n"
        "        pass\n"
        "\n"
        "    # R39: the reason\n"
        "    def test_b(self):\n"
        "        pass\n"
    )
    cites, bad = _check(tmp_path, text)
    assert bad == []
    assert cites == ["R39@TestX.test_b"]


def test_traceability_md_is_up_to_date() -> None:
    """Regenerating docs/traceability.md gives the same bytes."""
    assert traceability.OUTPUT.read_bytes() == traceability.render().encode("utf-8"), (
        "docs/traceability.md is out of date: run `uv run python tests/traceability.py`"
    )
