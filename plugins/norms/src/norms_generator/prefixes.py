"""File path -> prefix.

Every foundation file gets a prefix: upper-case ASCII letters, at least
three, unique across the whole corpus and over time. The nodes of the
file are numbered under it (`TYP-1`, `TYP-2`, ...) and the file itself
is cited by the bare prefix (`TYP`).

Algorithm (`assign_prefixes`):

1. A renamed or moved file keeps the prefix of the old path it comes
   from (`renames`, found by `store.detect_renames`). The old path may
   still exist, holding another file (a new file at the old path, or two
   files that swapped names).
2. A path already in the previous JSONL keeps its prefix, unless a
   renamed file took it or `renames` maps the path to None: a new file
   was put at the old path.
3. Every other path, in sorted order, takes the first candidate (see
   `candidates`) that is neither retired, nor held by a previous file,
   nor already given in this run. A retired prefix is never reused.

Candidates of one path, letters only (`A`-`Z`, anything else dropped),
from the file name without `.md` (the *name*) and its folders, nearest
folder first:

- length 3: the first three letters of the name (`type-system.md` ->
  `TYP`); then, for each folder, nearest first, `k` letters of the folder
  followed by `3 - k` letters of the name, `k = 1, 2`
  (`compiler/architecture.md` -> `CAR`, then `COA`);
- the same for length 4, 5, ... up to the length of name plus folder;
- if all of those are taken, the first three of the name's letters
  followed by its folders' letters, nearest folder first, padded with
  `X`, then a counter in letters (`REAA`, `REAB`, ...;
  `specs/1.md` -> `SPEA`, `ai.md` -> `AIXA`).

A name with fewer than three letters (`ai.md`) has no length-3 name
candidate and starts with folder letters (`language/ai.md` -> `LAI`).
Because the paths are sorted and the previous prefixes are kept, the
result is deterministic and stable: rerunning on the same input gives
the same prefixes, and adding a file never changes another file's.

Spec: R9, R10, R12, R14, R29, R58 (E78, E79, E80)
"""

from __future__ import annotations

from collections.abc import Iterator
from itertools import count
from pathlib import PurePosixPath
import re

PREFIX_RE = re.compile(r"[A-Z]{3,}")  # R10: a prefix's form; used with fullmatch


def _letters(text: str) -> str:
    """ASCII letters of `text`, upper-cased, everything else dropped.

    Filtered before upper-casing: Unicode case mapping would turn "ß" into
    "SS" and "ﬁ" into "FI", letters the name does not have.

    Spec: R10
    """
    return "".join(c for c in text if "A" <= c <= "Z" or "a" <= c <= "z").upper()


def _counter_letters(n: int) -> str:
    """0 -> "A", 25 -> "Z", 26 -> "AA", ... (bijective base 26): the counter.

    Spec: R10
    """
    out = ""
    n += 1
    while n > 0:
        n, rem = divmod(n - 1, 26)
        out = chr(ord("A") + rem) + out
    return out


def candidates(path: str) -> Iterator[str]:
    """Candidate prefixes of `path`, best first, without duplicates.

    The sequence is infinite: after the letter combinations it falls
    back to the name's first letters plus a letter counter.

    Spec: R10
    """
    p = PurePosixPath(path)
    # the file name without ".md": a file named ".md" has an empty name (stem would be ".md")
    name = _letters(p.name[: -len(".md")] if p.name.endswith(".md") else p.stem)
    folders = [f for f in (_letters(d) for d in reversed(p.parent.parts)) if f]
    seen: set[str] = set()
    longest = len(name) + sum(len(f) for f in folders)
    for length in range(3, max(longest, 3) + 1):
        options: list[str] = []
        if len(name) >= length:
            options.append(name[:length])
        for folder in folders:
            for k in range(1, length):
                if k <= len(folder) and length - k <= len(name):
                    options.append(folder[:k] + name[: length - k])
        for option in options:
            if len(option) == length and option not in seen:
                seen.add(option)
                yield option
    stem = (name + "".join(folders) + "XXX")[:3]
    for n in count():
        option = stem + _counter_letters(n)
        if option not in seen:
            seen.add(option)
            yield option


def assign_prefixes(
    paths: list[str],
    previous: dict[str, str],
    retired: set[str],
    renames: dict[str, str | None],
) -> dict[str, str]:
    """Give every path in `paths` its prefix.

    Args:
        paths: foundation file paths of this run.
        previous: path -> prefix of the files in the previous JSONL.
        retired: prefixes of files that vanished in earlier runs; never
            reused.
        renames: new path -> old path of a file renamed or moved; the
            new path keeps the old path's prefix. Both paths may be in
            `previous` and in `paths`. A path mapped to None gets a new
            prefix although it is in `previous`.

    Returns:
        path -> prefix for every path in `paths`.

    Raises:
        ValueError: on a rename whose old path is unknown, two renames of
            one old path, or a previous prefix that is not well formed.

    Spec: R10, R12, R58, R61 (E78, E79, E80, E81)
    """
    result: dict[str, str] = {}
    current = set(paths)
    for path, prefix in previous.items():
        if not PREFIX_RE.fullmatch(prefix):  # R61: the reader refuses it first
            raise ValueError(f"bad prefix {prefix!r} for {path}")
    used_old: set[str] = set()
    fresh = {path for path, old_path in renames.items() if old_path is None}
    # R58: a renamed or moved file keeps its prefix, even from a path still there (E78, E79)
    for new_path, old_path in sorted((k, v) for k, v in renames.items() if v is not None):
        if new_path not in current:
            continue
        if old_path not in previous:
            raise ValueError(f"rename of unknown path {old_path}")
        if old_path in used_old:
            raise ValueError(f"{old_path} renamed twice")
        used_old.add(old_path)
        result[new_path] = previous[old_path]
    claimed = set(result.values())
    # R58: a path present in both keeps its prefix unless renamed away or replaced (E81)
    for path in sorted(current):
        if path in previous and path not in result and path not in fresh and previous[path] not in claimed:
            result[path] = previous[path]
    # R10, R58: new and replaced paths take the first candidate not retired, held, or given
    taken = set(retired) | set(previous.values()) | set(result.values())
    for path in sorted(current):
        if path in result:
            continue
        for option in candidates(path):
            if option not in taken:
                result[path] = option
                taken.add(option)
                break
    return result
