"""Tests of prefixes.py.

Spec: R9, R10, R12, R14, R58
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from norms_generator.prefixes import assign_prefixes, candidates

SPECS_REPO = Path("/Users/jpchauny/Documents/Clean Language/clean-language-foundation")
MARKER_PREFIX = re.compile(r"^[A-Z]{3,}$")


def spec_paths() -> list[str]:
    root = SPECS_REPO / "specs"
    if not root.is_dir():
        pytest.skip("specs repository not found")
    return sorted(str(p.relative_to(SPECS_REPO)) for p in root.rglob("*.md"))


def test_type_system_is_typ() -> None:
    """`type-system.md` takes the name's first three letters.

    Spec: R9, R10
    """
    assert assign_prefixes(["specs/language/types/type-system.md"], {}, set(), {}) == {
        "specs/language/types/type-system.md": "TYP"
    }


def test_real_specs_unique_and_stable() -> None:
    """Every spec file gets a unique prefix of 3+ upper-case letters, in any order, and a rerun keeps them.

    Spec: R10, R14, R58
    """
    paths = spec_paths()
    assert paths
    first = assign_prefixes(paths, {}, set(), {})
    assert set(first) == set(paths)
    assert len(set(first.values())) == len(paths)
    assert all(MARKER_PREFIX.match(p) for p in first.values())
    assert first["specs/language/types/type-system.md"] == "TYP"
    # Same input, any order: same result.
    assert assign_prefixes(list(reversed(paths)), {}, set(), {}) == first
    # Rerun with the previous prefixes: nothing changes.
    assert assign_prefixes(paths, first, set(), {}) == first


def test_collisions_use_folder_letters() -> None:
    """Colliding names fall back to folder letters, nearest folder first.

    Spec: R10
    """
    paths = [
        "specs/components/compiler/architecture.md",
        "specs/components/framework/architecture.md",
        "specs/platform/architecture.md",
    ]
    result = assign_prefixes(paths, {}, set(), {})
    assert result == {
        "specs/components/compiler/architecture.md": "ARC",
        "specs/components/framework/architecture.md": "FAR",
        "specs/platform/architecture.md": "PAR",
    }


def test_short_name_takes_folder_letters() -> None:
    """A name with fewer than three letters starts with folder letters: `language/ai.md` -> `LAI`.

    Spec: R10
    """
    assert assign_prefixes(["specs/language/ai.md"], {}, set(), {}) == {"specs/language/ai.md": "LAI"}


def test_new_file_never_takes_existing_or_retired_prefix() -> None:
    """A new path takes the first candidate not retired and not held by a file of the previous JSONL.

    Spec: R10, R58
    """
    previous = {"specs/a/type-system.md": "TYP"}
    retired = {"TYPE", "TTY"}
    result = assign_prefixes(
        ["specs/a/type-system.md", "specs/types/types.md"], previous, retired, {}
    )
    assert result["specs/a/type-system.md"] == "TYP"
    assert result["specs/types/types.md"] not in {"TYP", "TYPE", "TTY"}
    assert MARKER_PREFIX.match(result["specs/types/types.md"])


def test_adding_a_file_changes_no_other_prefix() -> None:
    """Adding a file never changes another file's prefix.

    Spec: R10
    """
    paths = spec_paths()
    first = assign_prefixes(paths, {}, set(), {})
    more = assign_prefixes(paths + ["specs/language/types/types.md"], first, set(), {})
    assert {p: more[p] for p in paths} == first
    assert more["specs/language/types/types.md"] not in first.values()


def test_rename_keeps_prefix() -> None:
    """A renamed or moved file keeps its prefix.

    Spec: R12, R58
    """
    previous = {"specs/language/types/type-system.md": "TYP"}
    result = assign_prefixes(
        ["specs/language/typing.md"],
        previous,
        set(),
        {"specs/language/typing.md": "specs/language/types/type-system.md"},
    )
    assert result == {"specs/language/typing.md": "TYP"}


def test_vanished_file_prefix_not_reused_when_retired() -> None:
    """A retired prefix is never given again.

    Spec: R10, R58
    """
    result = assign_prefixes(["specs/type-system.md"], {}, {"TYP"}, {})
    assert result["specs/type-system.md"] != "TYP"


def test_bad_rename_raises() -> None:
    """A rename must come from a path of the previous JSONL, and an old path is renamed to one new path only.

    Spec: R58
    """
    with pytest.raises(ValueError):
        assign_prefixes(["b.md"], {}, set(), {"b.md": "a.md"})
    with pytest.raises(ValueError):
        assign_prefixes(["b.md", "c.md"], {"a.md": "AAA"}, set(), {"b.md": "a.md", "c.md": "a.md"})


def test_rename_onto_a_path_that_still_exists_r12() -> None:
    """A file moved away, a new file at its old path: the moved file keeps the prefix.

    Spec: R12, R58
    """
    previous = {"specs/lang/types.md": "TYP"}
    result = assign_prefixes(
        ["specs/lang/types.md", "specs/types/overview.md"],
        previous,
        set(),
        {"specs/types/overview.md": "specs/lang/types.md"},
    )
    assert result["specs/types/overview.md"] == "TYP"
    assert result["specs/lang/types.md"] not in ("TYP", "")


def test_swapped_names_swap_prefixes_r12() -> None:
    """Two files that swapped names swap their prefixes.

    Spec: R12, R58 (E79)
    """
    result = assign_prefixes(["a.md", "b.md"], {"a.md": "AAA", "b.md": "BBB"}, set(), {"a.md": "b.md", "b.md": "a.md"})
    assert result == {"a.md": "BBB", "b.md": "AAA"}


def test_candidates_are_unique_and_endless() -> None:
    """Candidates never repeat, and the letter counter never runs out.

    Spec: R10
    """
    seen = []
    for option in candidates("x/ab.md"):
        seen.append(option)
        if len(seen) == 60:
            break
    assert len(seen) == len(set(seen)) == 60
    assert all(MARKER_PREFIX.match(o) for o in seen)
