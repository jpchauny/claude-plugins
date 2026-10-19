"""The examples of the three spec documents as test cases.

specs/norms-tree.md, specs/norms-annotation-cases.md and
specs/norms-versions.md hold the examples. tests/spec_examples.py reads
them byte for byte and writes them under tests/fixtures/ (its docstring
gives the layout); `test_fixtures_match_specs` fails as soon as a fixture
and its spec differ, so the two cannot drift. After a spec changes, run
`uv run python tests/spec_examples.py`.

Annotation examples: one folder per input/annotated pair, with
input.md and expected.md, and notes.md when the pair is not annotated
with the defaults (prefix TYP, no file marker). Each is checked:
annotate == expected, strip == input, markers valid, structure kept.

Version examples: one folder per foundation version. Each
version is committed to a throwaway git foundation and built with
`norms-gen build` on top of the previous one; its annotated files, its
statuses and its report must be the spec's, and `verify` must pass.

Structure is compared with the cmark-gfm library shipped inside
`cmarkgfm`, reached through ctypes, rendered to XML.

Spec: R17, R28
"""

from __future__ import annotations

import ctypes
import difflib
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from types import ModuleType

import cmarkgfm
import pytest

import spec_examples

FIXTURES = Path(__file__).parent / "fixtures"

# R29: every marker matches this.
MARKER_RE = re.compile(r"⟬([A-Z]+(?:-[0-9]+)?)( begin| end)?⟭")
# R19: anything between the delimiters, to catch malformed markers too.
ANY_MARKER_RE = re.compile(r"⟬[^⟬⟭]*⟭")

CASES = sorted(
    d.name
    for d in FIXTURES.iterdir()
    if d.is_dir() and (d / "input.md").exists() and (d / "expected.md").exists()
)
VERSION_CASES = sorted(d.name for d in FIXTURES.iterdir() if (d / "v1").is_dir())

# R48, R64: the unclosed blocks: their end marker falls inside them for a
# parser, which only the generator's own structure check tolerates (E61, E62, E63).
UNCLOSED = {"E61", "E62", "E63"}


def same_structure(case: str, a: bytes, b: bytes) -> bool:
    """a and b parse to the same blocks: by the check verify uses, and,
    but for an unclosed block, by this file's stricter one too.

    Spec: R64
    """
    from norms_generator.structure import block_structure as verify_structure

    if verify_structure(a) != verify_structure(b):
        return False
    return case in UNCLOSED or block_structure(a) == block_structure(b)


def read(case: str, name: str) -> bytes:
    """Return the bytes of one fixture file."""
    return (FIXTURES / case / name).read_bytes()


def annotate_module() -> ModuleType:
    """Return norms_generator.annotate, or skip the test until it exists."""
    module = pytest.importorskip("norms_generator.annotate")
    for name in ("annotate_text", "strip"):
        if not hasattr(module, name):
            pytest.skip(f"norms_generator.annotate.{name} not implemented yet")
    return module


# --- cmark-gfm through ctypes ---------------------------------------------------

_P = ctypes.c_void_p
_EXTENSIONS = (b"table", b"strikethrough", b"autolink", b"tagfilter", b"tasklist")


def _load_cmark() -> ctypes.CDLL:
    """Load the cmark-gfm library inside cmarkgfm and declare what we call.

    Spec: R17
    """
    lib = ctypes.CDLL(cmarkgfm._cmark.__file__)
    lib.cmark_gfm_core_extensions_ensure_registered.restype = None
    lib.cmark_gfm_core_extensions_ensure_registered.argtypes = []
    lib.cmark_parser_new.restype = _P
    lib.cmark_parser_new.argtypes = [ctypes.c_int]
    lib.cmark_find_syntax_extension.restype = _P
    lib.cmark_find_syntax_extension.argtypes = [ctypes.c_char_p]
    lib.cmark_parser_attach_syntax_extension.restype = ctypes.c_int
    lib.cmark_parser_attach_syntax_extension.argtypes = [_P, _P]
    lib.cmark_parser_feed.restype = None
    lib.cmark_parser_feed.argtypes = [_P, ctypes.c_char_p, ctypes.c_size_t]
    lib.cmark_parser_finish.restype = _P
    lib.cmark_parser_finish.argtypes = [_P]
    lib.cmark_parser_free.restype = None
    lib.cmark_parser_free.argtypes = [_P]
    lib.cmark_render_xml.restype = _P  # char*, freed with libc free()
    lib.cmark_render_xml.argtypes = [_P, ctypes.c_int]
    lib.cmark_node_free.restype = None
    lib.cmark_node_free.argtypes = [_P]
    lib.cmark_gfm_core_extensions_ensure_registered()
    return lib


_CMARK = _load_cmark()
_LIBC = ctypes.CDLL(None)
_LIBC.free.restype = None
_LIBC.free.argtypes = [_P]


def cmark_xml(source: bytes) -> ET.Element:
    """Parse GFM source with the GFM extensions and return its XML tree.

    Spec: R3, R17
    """
    parser = _CMARK.cmark_parser_new(0)
    try:
        for name in _EXTENSIONS:
            ext = _CMARK.cmark_find_syntax_extension(name)
            assert ext, f"cmark-gfm extension {name!r} not found"
            _CMARK.cmark_parser_attach_syntax_extension(parser, ext)
        _CMARK.cmark_parser_feed(parser, source, len(source))
        document = _CMARK.cmark_parser_finish(parser)
    finally:
        _CMARK.cmark_parser_free(parser)
    try:
        rendered = _CMARK.cmark_render_xml(document, 0)
        try:
            xml = ctypes.string_at(rendered)
        finally:
            _LIBC.free(rendered)
    finally:
        _CMARK.cmark_node_free(document)
    return ET.fromstring(xml)


# --- block structure, ignoring the annotations ---------------------------

Structure = tuple[object, ...]

_TEXT_BLOCKS = {"paragraph", "heading", "table_cell"}
_INLINE_WRAP = {
    "emph": ("*", "*"),
    "strong": ("**", "**"),
    "strikethrough": ("~~", "~~"),
}


def _tag(elem: ET.Element) -> str:
    """Return an element's tag without the CommonMark namespace."""
    return elem.tag.rsplit("}", 1)[-1]


def _inline_text(elem: ET.Element) -> str:
    """Flatten the inlines of a block into a string that keeps their kinds."""
    parts: list[str] = []
    for child in elem:
        tag = _tag(child)
        if tag in ("text", "html_inline"):
            parts.append(child.text or "")
        elif tag == "code":
            parts.append("`" + (child.text or "") + "`")
        elif tag == "softbreak":
            parts.append("\n")
        elif tag == "linebreak":
            parts.append("<br>")
        elif tag in _INLINE_WRAP:
            left, right = _INLINE_WRAP[tag]
            parts.append(left + _inline_text(child) + right)
        elif tag in ("link", "image"):
            bang = "!" if tag == "image" else ""
            url = child.get("destination", "")
            parts.append(f"{bang}[{_inline_text(child)}]({url})")
        else:
            parts.append(f"<{tag}>{_inline_text(child)}</{tag}>")
    return "".join(parts)


def _clean_text(text: str) -> str:
    """Remove ID markers and normalize whitespace, for comparing node texts.

    Begin and end markers stay: one that a paragraph, heading or cell
    absorbed (a missing blank line) makes the texts differ.

    Spec: R30
    """
    inline = MARKER_RE.sub(lambda m: " " if not m.group(2) else m.group(0), text)
    return " ".join(inline.split())


def _structure(elem: ET.Element) -> Structure | None:
    """Return the block structure of an element; None for a marker-only paragraph.

    Ignored: list tightness (frame markers inside a list make it loose),
    paragraphs that hold only markers, and the marker text in paragraphs,
    headings and cells, as verify's block comparison does. Code and HTML
    blocks must match exactly.

    Spec: R26, R64, U2
    """
    tag = _tag(elem)
    if tag in _TEXT_BLOCKS:
        raw = _inline_text(elem)
        if tag == "paragraph" and not MARKER_RE.sub("", raw).strip():
            return None  # a paragraph of markers only: a marker line
        text = _clean_text(raw)
        return (tag, elem.get("level"), text)
    if tag in ("code_block", "html_block"):
        return (tag, elem.get("info"), elem.text or "")
    attrs: tuple[object, ...] = ()
    if tag == "list":
        attrs = (elem.get("type"), elem.get("start"), elem.get("delim"))
    elif tag == "tasklist":
        attrs = (elem.get("completed"),)
    children = tuple(s for s in (_structure(c) for c in elem) if s is not None)
    return (tag, attrs, children)


def block_structure(source: bytes) -> Structure | None:
    """Parse source and return its block structure, annotations ignored."""
    return _structure(cmark_xml(source))


# --- checks shared by fixture and generator tests ------------------------


def check_markers(annotated: bytes, file_marker: bool) -> None:
    """Every marker is well formed; every ID appears once, or begin+end.

    Spec: R29
    """
    text = annotated.decode("utf-8")
    for found in ANY_MARKER_RE.findall(text):
        assert MARKER_RE.fullmatch(found), f"malformed marker {found!r}"
    seen: dict[str, list[str]] = {}
    for match in MARKER_RE.finditer(text):
        seen.setdefault(match.group(1), []).append((match.group(2) or "").strip())
    for ident, uses in seen.items():
        assert uses in (["begin", "end"], [""]), f"{ident} used as {uses}"
    file_ids = [ident for ident in seen if "-" not in ident]
    if file_marker:
        assert len(file_ids) == 1, "the file is marked once (R29)"
        assert text.startswith(f"⟬{file_ids[0]}⟭\n"), "file marker on line 1"
    else:
        assert not file_ids, "fragments carry no file marker"


_MARKER_LINE_RE = re.compile(r"[ >]*" + MARKER_RE.pattern)


def check_blank_lines(annotated: bytes) -> None:
    """A marker on a line of its own has a blank line around it.

    Except at the start or end of the file. Inside a block quote the
    blank line is a bare `>`. A marker at the end of a line has a
    space before it.

    Spec: R30, R38
    """
    lines = annotated.decode("utf-8").split("\n")
    if lines and lines[-1] == "":
        lines.pop()

    def blank(line: str) -> bool:
        return not line.replace(">", "").strip()

    for n, line in enumerate(lines):
        if _MARKER_LINE_RE.fullmatch(line):
            assert n == 0 or blank(lines[n - 1]), f"no blank line before {line!r}"
            last = n == len(lines) - 1
            assert last or blank(lines[n + 1]), f"no blank line after {line!r}"
        else:
            for match in MARKER_RE.finditer(line):
                before = line[: match.start()]
                # a tab is the blank too, after "-\t": a space would move the content column
                assert before.endswith((" ", "\t")), f"no space before marker: {line!r}"


def check_pure_insertion(source: bytes, annotated: bytes) -> None:
    """The annotated text is the source with bytes inserted only.

    The markers are removed first, so that the diff cannot align an item
    marker `-` with the `-` of an ID; what is left besides the source may
    only be blanks, line endings, `>` and `|`.

    Spec: R23, R64
    """
    a = source.decode("utf-8")
    b = MARKER_RE.sub("", annotated.decode("utf-8"))
    matcher = difflib.SequenceMatcher(None, a, b, autojunk=False)
    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        assert op in ("equal", "insert"), f"{op} {a[i1:i2]!r} -> {b[j1:j2]!r}"
        if op == "insert":
            assert set(b[j1:j2]) <= set(" \t\r\n>|"), f"inserted {b[j1:j2]!r}"


# --- the fixtures themselves ---------------------------------------------


def options(case: str) -> tuple[str, bool]:
    """The prefix and file_marker an annotation fixture is annotated with."""
    return spec_examples.fixture_options(case)


def test_fixtures_match_specs() -> None:
    """Every fixture file is exactly what tests/spec_examples.py makes of the specs.

    Spec: R28
    """
    wanted = spec_examples.fixture_files()
    on_disk = spec_examples.files_on_disk()
    stale = sorted(set(on_disk) - set(wanted))
    missing = sorted(set(wanted) - set(on_disk))
    differ = sorted(k for k in set(wanted) & set(on_disk) if wanted[k] != on_disk[k])
    hint = "run `uv run python tests/spec_examples.py`"
    assert not stale, f"fixtures no spec holds: {stale}; {hint}"
    assert not missing, f"fixtures missing: {missing}; {hint}"
    assert not differ, f"fixtures that differ from the spec: {differ}; {hint}"


def test_all_examples_present() -> None:
    """The examples are numbered from 1 without gaps, each has its fixture, and the folder example has notes only.

    Spec: R28 (E20)
    """
    ids = spec_examples.example_ids()
    assert ids == [f"E{n}" for n in range(1, len(ids) + 1)]
    assert len(ids) == 89
    with_pairs = {c[:3] for c in CASES} | set(VERSION_CASES)
    assert with_pairs == {f"E{n:02d}" for n in range(1, 90)} - {"E20"}
    assert set(CASES) & set(VERSION_CASES) == set()
    assert (FIXTURES / "E20" / "notes.md").exists()


@pytest.mark.parametrize("case", CASES)
def test_fixture_files_end_with_one_newline(case: str) -> None:
    """Each fixture file ends with exactly one newline, as the spec's fences give it.

    Spec: R28
    """
    for path in (FIXTURES / case).glob("*.md"):
        data = path.read_bytes()
        assert data.endswith(b"\n") and not data.endswith(b"\n\n"), path


@pytest.mark.parametrize("case", CASES)
def test_fixture_markers(case: str) -> None:
    """The expected output's markers are well formed and each ID is used once.

    Spec: R25, R29, R30
    """
    check_markers(read(case, "expected.md"), options(case)[1])
    check_blank_lines(read(case, "expected.md"))


@pytest.mark.parametrize("case", CASES)
def test_fixture_is_pure_insertion(case: str) -> None:
    """expected.md is input.md with bytes inserted, nothing moved.

    Spec: R23
    """
    check_pure_insertion(read(case, "input.md"), read(case, "expected.md"))


@pytest.mark.parametrize("case", CASES)
def test_fixture_structure_survives(case: str) -> None:
    """input.md and expected.md parse to the same blocks, markers aside, unclosed blocks aside.

    Spec: R50, R64, U1 (E61, E62, E63)
    """
    assert same_structure(case, read(case, "expected.md"), read(case, "input.md"))


# --- the generator -------------------------------------------------------


@pytest.mark.parametrize("case", CASES)
def test_annotate_matches_expected(case: str) -> None:
    """annotate(input) == expected, byte for byte.

    Spec: R28
    """
    annotate = annotate_module()
    prefix, file_marker = options(case)
    result, _ = annotate.annotate_text(read(case, "input.md"), prefix, file_marker=file_marker)
    assert result.decode("utf-8") == read(case, "expected.md").decode("utf-8")


@pytest.mark.parametrize("case", CASES)
def test_strip_gives_back_input(case: str) -> None:
    """Removing the insertions gives back the foundation file.

    Spec: R23
    """
    annotate = annotate_module()
    source = read(case, "input.md")
    prefix, file_marker = options(case)
    result, insertions = annotate.annotate_text(source, prefix, file_marker=file_marker)
    assert annotate.strip(result, insertions) == source


@pytest.mark.parametrize("case", CASES)
def test_annotated_markers_and_structure(case: str) -> None:
    """The generator's output is well formed and keeps the input's blocks.

    Spec: R23, R29, R30, R50, R64
    """
    annotate = annotate_module()
    source = read(case, "input.md")
    prefix, file_marker = options(case)
    result, _ = annotate.annotate_text(source, prefix, file_marker=file_marker)
    check_markers(result, file_marker)
    check_blank_lines(result)
    check_pure_insertion(source, result)
    assert same_structure(case, result, source)


def test_e20_output_mirrors_folders(tmp_path: Path) -> None:
    """The folder example: `annotated/` keeps the folder tree of foundation; folders get no ID; file marker first.

    Spec: R14, R29, R62 (E20)
    """
    from norms_generator.cli import main

    foundation = tmp_path / "foundation"
    files = {
        "specs/README.md": "# Foundation\n\nThe specs of Clean.\n",
        "specs/language/type-system.md": "# Types\n\nClean has types.\n",
        "specs/tooling/build.md": "Run the build.\n",
    }
    for rel, text in files.items():
        path = foundation / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", "-C", str(foundation)]
    subprocess.run([*git, "init", "-q"], check=True)
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-q", "-m", "c"], check=True)
    out = tmp_path / "norms"
    assert main(["build", "--foundation", str(foundation), "--out", str(out)]) == 0
    annotated = out / "annotated"
    written = {
        p.relative_to(annotated).as_posix() for p in annotated.rglob("*.md")
    }
    assert written == set(files)
    for rel in files:
        text = (annotated / rel).read_text(encoding="utf-8")
        first = MARKER_RE.match(text)
        assert first and "-" not in first.group(1), f"{rel}: file marker first"
    for folder in ("specs", "language", "tooling"):  # R14: no folder ID
        assert f"⟬{folder.upper()}" not in "".join(
            (annotated / rel).read_text(encoding="utf-8") for rel in files
        )


# --- the version examples (specs/norms-versions.md) ----------------------


def _versions(case: str) -> list[Path]:
    """The version folders of a version fixture, v1 first."""
    return sorted((FIXTURES / case).glob("v*"), key=lambda p: int(p.name[1:]))


def _tree_files(folder: Path) -> dict[str, bytes]:
    """The files under a folder, by relative path."""
    return {
        p.relative_to(folder).as_posix(): p.read_bytes()
        for p in sorted(folder.rglob("*"))
        if p.is_file()
    }


def status_lines(changes: list[dict[str, object]], flags: dict[str, tuple[bool, str | None]], commits: dict[str, str]) -> str:
    """The spec's list of statuses (norms-versions.md, Examples), from report.json and tree.jsonl.

    One line per ID that is not unchanged or that carries a flag, in the
    order of report.json; `changed_since` is written as the commit's name.
    """
    out: list[str] = []
    for c in changes:
        status = c["status"]
        parts = [f"`{status}`"]
        if c["similarity"] is not None:
            parts.append(f"similarity {c['similarity']}")
        if c["moved"]:
            word = "from" if status == "moved" else "moved from"
            if c["kind"] == "file":
                parts.append(f"{word} `{c['old_file']}`")
            elif c["old_file"] not in (None, c["file"]):
                parts.append(f"{word} `{c['old_file']}`, parent `{c['old_parent']}` → `{c['new_parent']}`")
            elif status == "moved":
                parts.append(f"parent `{c['old_parent']}` → `{c['new_parent']}`")
            else:
                parts.append(f"moved, parent `{c['old_parent']}` → `{c['new_parent']}`")
        if c["reordered"]:
            parts.append("reordered")
        if c["changed_children"]:
            parts.append("changed children " + ", ".join(f"`{x}`" for x in c["changed_children"]))
        if c["id"] in flags:
            to_review, since = flags[c["id"]]
            if to_review:
                parts.append("`to_review`")
            parts.append(f"`changed_since` {'`' + commits[since] + '`' if since else 'null'}")
        out.append(f"- `{c['id']}` ({c['kind']}): " + ", ".join(parts) + ".")
    if not out:
        out.append("- None: every ID is `unchanged`, with no flag set.")
    return "\n".join(out) + "\n"


@pytest.mark.parametrize("case", VERSION_CASES)
def test_version_example(case: str, tmp_path: Path) -> None:
    """Each version, built on the previous one, gives the spec's files, statuses and report.

    Spec: R28, R59, R60, R63, R64
    """
    import json

    from norms_generator import cli
    from norms_generator.store import read_store

    foundation = tmp_path / "foundation"
    foundation.mkdir()
    out = tmp_path / "norms"
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false", "-C", str(foundation)]
    subprocess.run([*git, "init", "-q", "-b", "main"], check=True)
    commits: dict[str, str] = {}  # sha -> c1, c2, ...
    previous: str | None = None
    for folder in _versions(case):
        name = "c" + folder.name[1:]
        for old in [p for p in foundation.rglob("*") if p.is_file() and ".git" not in p.parts]:
            old.unlink()
        inputs = _tree_files(folder / "input")
        for rel, data in inputs.items():
            path = foundation / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        subprocess.run([*git, "add", "-A"], check=True)
        subprocess.run([*git, "commit", "-q", "--allow-empty", "-m", name], check=True)
        sha = subprocess.run([*git, "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
        commits[sha] = name

        cli.build(foundation, "HEAD", "specs", out)
        assert cli.verify(foundation, out) == [], folder.name

        annotated = _tree_files(out / "annotated")
        expected = _tree_files(folder / "expected")
        assert sorted(annotated) == sorted(expected), folder.name
        for rel, data in expected.items():
            assert annotated[rel].decode("utf-8") == data.decode("utf-8"), f"{folder.name} {rel}"
            check_markers(data, file_marker=True)
            check_blank_lines(data)
            check_pure_insertion(inputs[rel], data)

        report_md = (out / "data" / "report.md").read_text(encoding="utf-8")
        since = f"`{previous}`" if previous else "nothing (first run)"
        foundation_line = f"\nFoundation {since} -> `{sha}`.\n"
        assert foundation_line in report_md
        if (folder / "statuses.md").exists():
            changes = [json.loads(line) for line in (out / "data" / "report.json").read_text(encoding="utf-8").splitlines()]
            store = read_store(out / "data" / "tree.jsonl")
            flags = {n.id: (n.to_review, n.changed_since) for n in store.nodes}
            text = status_lines(changes, flags, commits)
            if store.retired_prefix_list:
                text += "\n`retired_prefixes`: " + ", ".join(f"`{p}`" for p in store.retired_prefix_list) + ".\n"
            assert text == (folder / "statuses.md").read_text(encoding="utf-8"), folder.name
        if (folder / "report.md").exists():
            assert report_md.replace(foundation_line, "", 1) == (folder / "report.md").read_text(encoding="utf-8")
        previous = sha
