"""Traceability from the code to the specs: writes docs/traceability.md.

The specs are the single source of truth (specs/norms-tree.md,
specs/norms-annotation-cases.md, specs/norms-versions.md). The code and the
tests cite the requirements (R<n>), the decisions of the user (U<n>) and the
examples (E<n>) they implement or check. This module reads those citations
and writes, for each requirement and decision, its title, the code and the
tests that cite it, and its examples with their fixtures. Run

    uv run python tests/traceability.py

after the code, the tests or the specs changed. tests/test_traceability.py
checks that every citation names an id that exists, that every citation has
the one format below, and that docs/traceability.md is what this module
makes of the sources now.

The format of a citation, the same under src/ and tests/:

- The docstring of a module, class or function that implements or checks a
  rule ends with one paragraph, a single line such as
  `Spec: R35, R39, U4 (E28, E40)`: the requirements and the decisions of the
  user, R before U and each sorted by number, then the examples in
  parentheses, sorted by number; ids separated by ", ", never a range. A
  docstring that cites examples only ends with `Spec: (E28)`.
- A comment on a branch that applies one specific case starts with its ids:
  `# R39: <short reason> (E41)`. The comment may run on over the comment
  lines right below it; examples appear only in parentheses.
- An implementation note of docs/generator-decisions.md is cited as
  `Note: D2` (`Note: D27c, D40`), in a docstring or a comment.

No other R, U, E or D token may appear in a docstring or a comment. A string
that is not a docstring (a message, test data, a fixture name) is not a
citation, but every id it names must exist. A requirement that only module
docstrings cite counts as having no citation of its own: a module docstring
sums up its module.
"""

from __future__ import annotations

import ast
import io
import re
import tokenize
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPECS = ROOT / "specs"
SPEC_FILES = ("norms-tree.md", "norms-annotation-cases.md", "norms-versions.md")
DECISIONS = ROOT / "docs" / "generator-decisions.md"
FIXTURES = ROOT / "tests" / "fixtures"
OUTPUT = ROOT / "docs" / "traceability.md"
SRC = ROOT / "src"
TESTS = ROOT / "tests"
TOOLS = {"traceability.py", "spec_examples.py", "test_traceability.py"}  # tooling: neither code nor tests of a rule; its prose shows ids

# `R12`, `E03b`, `R53-R57`, `E25–E31`, `R53-57`; never a letter or digit around it.
_CITE_RE = re.compile(
    r"(?<![\w-])(?P<k>[REU])(?P<n>\d+)(?P<s>[a-z]?)"
    r"(?:[–-](?P<k2>[REU])?(?P<n2>\d+)(?P<s2>[a-z]?))?(?![\w])"
)
_D_RE = re.compile(r"(?<![\w-])D(?P<n>\d+)(?P<s>[a-z]?)(?![\w])")
# the linter codes after `noqa` (`# noqa: E501, E731`) are no citation; anything after them is read
_NOQA_RE = re.compile(r"#\s*noqa\b(?::\s*[A-Z]+\d+(?:\s*,\s*[A-Z]+\d+)*)?")

_REQ_RE = re.compile(r"^- \*\*(?P<id>[RU]\d+)\.\s*(?P<title>.*?)\*\*")
_EX_RE = re.compile(r"^### (?P<id>E\d+)\.\s*(?P<title>.*)$")
_HEADING_RE = re.compile(r"^#{1,3} ")
_FENCE_RE = re.compile(r"^ {0,3}(?P<f>`{3,}|~{3,})")


@dataclass(frozen=True)
class Cite:
    """One citation of one id."""

    id: str
    path: str  # relative to the repository root
    line: int
    scope: str  # innermost function, class or constant, or "(module)"


@dataclass
class Entry:
    """A requirement, a decision of the user or an example of the specs."""

    id: str
    title: str
    spec: str
    text: str  # its whole text in the spec
    examples: set[str] = field(default_factory=set)


def _num(ident: str) -> int:
    return int(ident[1:])


def _sort_key(ident: str) -> tuple[str, int]:
    return ({"R": "0", "U": "1", "E": "2"}.get(ident[0], ident[0]), _num(ident))


# --- the specs ----------------------------------------------------------------


def _spec_entries() -> dict[str, Entry]:
    """Every R, U and E of the specs, with its text (outside fences for headings)."""
    entries: dict[str, Entry] = {}
    for spec in SPEC_FILES:
        lines = (SPECS / spec).read_text(encoding="utf-8").splitlines()
        current: Entry | None = None
        kind = ""  # "req": a top-level bullet; "ex": a ### section
        fence = ""
        for line in lines:
            if fence:
                if re.match(r"^ {0,3}" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}\s*$", line):
                    fence = ""
                if current:
                    current.text += line + "\n"
                continue
            opened = _FENCE_RE.match(line)
            if opened:
                fence = opened.group("f")
                if current and kind == "req" and not line.startswith((" ", "\t")):
                    current = None
                if current:
                    current.text += line + "\n"
                continue
            req = _REQ_RE.match(line)
            ex = _EX_RE.match(line)
            if req or ex:
                m = req or ex
                ident = m.group("id")
                title = re.sub(r"[.,:;]+$", "", m.group("title").strip())
                if ident in entries:
                    raise ValueError(f"{ident} is defined twice ({entries[ident].spec}, {spec})")
                current = Entry(ident, title, f"specs/{spec}", line + "\n")
                entries[ident] = current
                kind = "req" if req else "ex"
                continue
            if _HEADING_RE.match(line):
                current = None
            elif current and kind == "req" and line.strip() and not line.startswith((" ", "\t")):
                current = None
            if current:
                current.text += line + "\n"
    return entries


def _decision_numbers() -> tuple[set[str], set[str]]:
    """The implementation notes (`D27c`) and the pointer lines (`D27`) of generator-decisions.md."""
    notes: set[str] = set()
    pointers: set[str] = set()
    for line in DECISIONS.read_text(encoding="utf-8").splitlines():
        note = re.match(r"^- \*\*D(\d+[a-z]?)\.", line)
        pointer = re.match(r"^- D(\d+)\b", line)
        if note:
            notes.add("D" + note.group(1))
        elif pointer:
            pointers.add("D" + pointer.group(1))
    return notes, pointers


def _expand(match: re.Match[str]) -> tuple[list[str], bool]:
    """The ids a citation names, and whether it is a range."""
    k, n = match.group("k"), int(match.group("n"))
    if match.group("n2") is None:
        return [f"{k}{n}"], False
    k2 = match.group("k2") or k
    n2 = int(match.group("n2"))
    if k2 != k or n2 < n:
        return [f"{k}{n}", f"{k2}{n2}"], False  # not a range: checked as two ids
    return [f"{k}{i}" for i in range(n, n2 + 1)], True


def _ids_in(text: str) -> set[str]:
    out: set[str] = set()
    for m in _CITE_RE.finditer(text):
        out.update(_expand(m)[0])
    return out


def _fixtures() -> dict[str, list[str]]:
    """Example id -> its fixture folders under tests/fixtures/."""
    out: dict[str, list[str]] = {}
    for d in sorted(p.name for p in FIXTURES.iterdir() if p.is_dir()):
        m = re.fullmatch(r"E(\d+)[a-z]?", d)
        if m:
            out.setdefault(f"E{int(m.group(1))}", []).append(d)
    return out


def specs() -> dict[str, Entry]:
    """The entries of the specs, each requirement and decision with its examples.

    The examples of a requirement are those its text cites and those whose
    section cites it.
    """
    entries = _spec_entries()
    examples = [e for e in entries.values() if e.id.startswith("E")]
    for entry in entries.values():
        if entry.id.startswith("E"):
            continue
        entry.examples = {i for i in _ids_in(entry.text) if i.startswith("E") and i in entries}
        entry.examples |= {e.id for e in examples if entry.id in _ids_in(e.text)}
    return entries


# --- the code and the tests ---------------------------------------------------

_SPEC_RE = re.compile(
    r"^Spec: (?:(?P<ids>[RU]\d+(?:, [RU]\d+)*)(?: \((?P<ex>E\d+(?:, E\d+)*)\))?"
    r"|\((?P<only>E\d+(?:, E\d+)*)\))$"
)
_INLINE_RE = re.compile(r"^#\s*(?P<ids>[RU]\d+(?:, [RU]\d+)*): (?=\S)")
_EX_PAREN_RE = re.compile(r"\((?P<ex>E\d+(?:, E\d+)*)\)")
_NOTE_RE = re.compile(r"\bNote: D\d+[a-z]?(?:, D\d+[a-z]?)*")


@dataclass
class _Source:
    """The docstrings and the comments of one .py file."""

    rel: str
    lines: list[str]
    scopes: list[tuple[int, int, str]]
    docstrings: list[tuple[int, str, str]]  # (first line, scope, raw text)
    comments: list[tuple[int, str, bool]]  # (line, text, after code on its line)


def _parse(path: Path) -> _Source:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    docstrings: list[tuple[int, str, str]] = []

    def visit(node: ast.AST, name: str) -> None:
        body = getattr(node, "body", [])
        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            docstrings.append((body[0].lineno, name, body[0].value.value))
        for child in body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                visit(child, child.name if name == "(module)" else f"{name}.{child.name}")

    visit(tree, "(module)")
    comments = [
        (tok.start[0], tok.string, bool(tok.line[: tok.start[1]].strip()))
        for tok in tokenize.generate_tokens(io.StringIO(text).readline)
        if tok.type == tokenize.COMMENT
    ]
    rel = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.name
    return _Source(rel, text.split("\n"), _scopes(tree), docstrings, comments)


def _ordered(ids: list[str]) -> bool:
    return ids == sorted(set(ids), key=_sort_key)


def _stray(text: str) -> list[str]:
    """The R, U, E and D tokens of `text` once its `Note:` citations are taken out."""
    text = _NOTE_RE.sub("", _NOQA_RE.sub("", text))
    found = [m.group(0) for m in _CITE_RE.finditer(text)]
    return found + [m.group(0) for m in _D_RE.finditer(text)]


def _comment_blocks(src: _Source) -> list[list[tuple[int, str]]]:
    """The comments grouped: a citing comment and the comment lines right below it."""
    blocks: list[list[tuple[int, str]]] = []
    prev = -1
    for line, text, after_code in src.comments:
        text = _NOQA_RE.sub("", text).rstrip()
        cont = blocks and not after_code and line == prev + 1 and not _INLINE_RE.match(text)
        if cont:
            blocks[-1].append((line, text))
        else:
            blocks.append([(line, text)])
        prev = line
    return blocks


def _analyse(path: Path) -> tuple[list[Cite], list[str]]:
    """The citations of a file, and the problems of their format."""
    src = _parse(path)
    cites: list[Cite] = []
    bad: list[str] = []

    for first, scope, raw in src.docstrings:
        lines = raw.split("\n")
        specs_at = [i for i, x in enumerate(lines) if x.strip().startswith("Spec:")]
        if len(specs_at) > 1:
            bad.append(f"{src.rel}:{first + specs_at[1]}: a second Spec: line in one docstring")
        for i in specs_at[:1]:
            line = lines[i].strip()
            no = first + i
            if any(x.strip() for x in lines[i + 1 :]) or (i > 0 and lines[i - 1].strip()):
                bad.append(f"{src.rel}:{no}: the Spec: line is not the docstring's last paragraph")
            m = _SPEC_RE.match(line)
            if not m:
                bad.append(f"{src.rel}:{no}: not of the form `Spec: R1, R2, U1 (E1, E2)`: {line}")
                continue
            ids = m.group("ids").split(", ") if m.group("ids") else []
            exs = (m.group("ex") or m.group("only") or "").split(", ") if (m.group("ex") or m.group("only")) else []
            if not _ordered(ids) or not _ordered(exs):
                bad.append(f"{src.rel}:{no}: ids not sorted, or repeated: {line}")
            cites.extend(Cite(x, src.rel, no, scope) for x in ids + exs)
        for i, x in enumerate(lines):
            if i in specs_at[:1]:
                continue
            for token in _stray(x):
                bad.append(f"{src.rel}:{first + i}: {token} in a docstring, outside its Spec: line")

    for block in _comment_blocks(src):
        head_no, head = block[0]
        m = _INLINE_RE.match(head)
        rest = " ".join([head[m.end() :] if m else head] + [t for _, t in block[1:]])
        if m:
            ids = m.group("ids").split(", ")
            exs = [e for p in _EX_PAREN_RE.finditer(rest) for e in p.group("ex").split(", ")]
            if not _ordered(ids) or not _ordered(exs):
                bad.append(f"{src.rel}:{head_no}: ids not sorted, or repeated: {head}")
            scope = _scope_of(head_no, src.lines, src.scopes)
            cites.extend(Cite(x, src.rel, head_no, scope) for x in ids + exs)
            rest = _EX_PAREN_RE.sub("", rest)
        for token in _stray(rest):
            bad.append(
                f"{src.rel}:{head_no}: {token} in a comment that does not start with its ids "
                "(`# R39: <reason> (E41)`)"
            )
    return cites, bad


def _scopes(tree: ast.Module) -> list[tuple[int, int, str]]:
    """(first line, last line, qualified name) of every def, class and named constant."""
    out: list[tuple[int, int, str]] = []

    def visit(body: list[ast.stmt], prefix: str, in_def: bool) -> None:
        for node in body:
            first = min([node.lineno] + [d.lineno for d in getattr(node, "decorator_list", [])])
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                name = prefix + node.name
                out.append((first, node.end_lineno or node.lineno, name))
                visit(node.body, name + ".", in_def or not isinstance(node, ast.ClassDef))
            elif not in_def and isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                names = [t.id for t in targets if isinstance(t, ast.Name)]
                if names:
                    out.append((node.lineno, node.end_lineno or node.lineno, prefix + names[0]))

    visit(tree.body, "", False)
    return out


def _scope_of(line: int, lines: list[str], scopes: list[tuple[int, int, str]]) -> str:
    """The innermost scope holding `line`; a comment just above a def belongs to it."""
    target = line
    if lines[line - 1].lstrip().startswith("#"):
        k = line
        while k < len(lines) and lines[k].lstrip().startswith("#"):
            k += 1
        nxt = k + 1  # the first line after the comment block, 1-based
        if nxt <= len(lines) and any(a == nxt for a, _, _ in scopes):  # a method's comment too
            target = nxt
    best = "(module)"
    best_len = None
    for a, b, name in scopes:
        if a <= target <= b and (best_len is None or b - a < best_len):
            best, best_len = name, b - a
    return best


def python_files() -> list[Path]:
    """Every .py file under src/ and tests/ (not tests/fixtures/), in path order."""
    files = [p for p in SRC.rglob("*.py")] + [p for p in TESTS.glob("*.py")]
    return sorted(files, key=lambda p: p.relative_to(ROOT).as_posix())


def _is_tool(path: Path) -> bool:
    return path.parent == TESTS and path.name in TOOLS


def citations(path: Path) -> list[Cite]:
    """The citations of a file: its Spec: lines and its `# R39:` comments."""
    return _analyse(path)[0]


def format_problems() -> list[str]:
    """Every R, U, E or D token of a docstring or a comment that is not a citation of the format.

    The tooling (TOOLS) is left out: its prose shows the format.
    """
    out: list[str] = []
    for path in python_files():
        if not _is_tool(path):
            out.extend(_analyse(path)[1])
    return out


def untraced_tests() -> list[str]:
    """Every test function that no Spec: line or `# R39:` comment of its own, or of its class, cites."""
    out: list[str] = []
    for path in python_files():
        if path.parent != TESTS or _is_tool(path) or not path.name.startswith("test_"):
            continue
        cites = citations(path)
        scoped = {c.scope for c in cites}
        for node in ast.parse(path.read_text(encoding="utf-8")).body:
            tests = [(node.name, node)] if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else []
            if isinstance(node, ast.ClassDef):
                tests = [(f"{node.name}.{n.name}", n) for n in node.body if isinstance(n, ast.FunctionDef)]
            for name, fn in tests:
                if not fn.name.startswith("test_"):
                    continue
                cls = name.rpartition(".")[0]
                if not any(s == name or s.startswith(name + ".") or (cls and s == cls) for s in scoped):
                    out.append(f"{path.relative_to(ROOT).as_posix()}:{fn.lineno}: {name} cites no rule")
    return out


def problems() -> list[str]:
    """Every id of src/ and tests/ (docstrings, comments and strings) that no spec and no note defines."""
    entries = specs()
    notes, pointers = _decision_numbers()
    out = []
    for path in python_files():
        rel = path.relative_to(ROOT).as_posix()
        for no, raw in enumerate(path.read_text(encoding="utf-8").split("\n"), start=1):
            line = _NOQA_RE.sub("", raw)
            for m in _CITE_RE.finditer(line):
                for i in _expand(m)[0]:
                    if i not in entries:
                        out.append(f"{rel}:{no}: {i} is in no spec")
            for m in _D_RE.finditer(line):
                d = "D" + m.group("n") + m.group("s")
                if d not in notes and re.sub(r"[a-z]$", "", d) not in pointers:
                    out.append(
                        f"{rel}:{no}: {d} is neither an implementation note "
                        "nor a pointer of docs/generator-decisions.md"
                    )
    return out


# --- docs/traceability.md -----------------------------------------------------


def _locations(cites: list[Cite]) -> list[str]:
    """One line per file: `file`: scope, scope (scopes in order of first citation)."""
    by_file: dict[str, dict[str, None]] = {}
    for c in cites:
        by_file.setdefault(c.path, {})[c.scope] = None
    out = []
    for path in sorted(by_file):
        names = [f"`{s}`" for s in by_file[path]]
        out.append(f"`{path}`: " + ", ".join(names))
    return out


def render() -> str:
    """The text of docs/traceability.md."""
    entries = specs()
    fixtures = _fixtures()
    code: dict[str, list[Cite]] = {}
    tests: dict[str, list[Cite]] = {}
    for path in python_files():
        if _is_tool(path):
            continue
        side = code if path.is_relative_to(SRC) else tests
        for c in citations(path):
            side.setdefault(c.id, []).append(c)

    heads = sorted((e for e in entries.values() if e.id[0] in "RU"), key=lambda e: _sort_key(e.id))
    out = [
        "# Traceability",
        "",
        "Generated by `uv run python tests/traceability.py`; do not edit by hand.",
        "`tests/test_traceability.py` fails when this file is out of date, when the",
        "code or the tests cite an id that no spec defines, or when a citation is not",
        "a `Spec:` line of a docstring or a `# R39: <reason> (E41)` comment.",
        "",
        "For each requirement (R) and decision of the user (U): the code under `src/`",
        "and the tests under `tests/` that cite it, by file and by function, class or",
        "constant, and its examples, with their fixtures under `tests/fixtures/`. The",
        "examples of a requirement are those it cites and those that cite it. A",
        "requirement that only `(module)`, a module's docstring, cites counts as having",
        "no citation of its own.",
        "",
    ]
    no_code: list[Entry] = []
    no_test: list[Entry] = []
    for e in heads:
        c, t = code.get(e.id, []), tests.get(e.id, [])
        if not any(x.scope != "(module)" for x in c):
            no_code.append(e)
        if not any(x.scope != "(module)" for x in t):
            no_test.append(e)
        out += [f"## {e.id}. {e.title}", "", f"Spec: `{e.spec}`", ""]
        out.append("Code:" if c else "Code: none")
        out += [f"- {line}" for line in _locations(c)]
        out.append("")
        out.append("Tests:" if t else "Tests: none")
        out += [f"- {line}" for line in _locations(t)]
        out.append("")
        exs = sorted(e.examples, key=_sort_key)
        if exs:
            out.append("Examples:")
            for x in exs:
                fx = ", ".join(f"`{f}`" for f in fixtures.get(x, [])) or "no fixture"
                out.append(f"- {x}. {entries[x].title} ({fx})")
        else:
            out.append("Examples: none")
        out.append("")

    def gap(title: str, items: list[Entry], what: str) -> None:
        out.extend([f"## {title}", ""])
        if not items:
            out.extend([f"Every requirement and decision has {what}.", ""])
            return
        for e in items:
            exs = sorted(e.examples, key=_sort_key)
            fx = [f for x in exs for f in fixtures.get(x, [])]
            note = f"; examples with fixtures: {', '.join(exs)}" if fx else ""
            out.append(f"- {e.id}. {e.title}{note}")
        out.append("")

    gap("Requirements no code cites", no_code, "a citation of its own in `src/`")
    gap("Requirements no test cites", no_test, "a citation of its own in a test")
    return "\n".join(out).rstrip("\n") + "\n"


def main() -> int:
    bad = problems() + format_problems()
    if bad:
        print("\n".join(bad), file=sys.stderr)
        return 1
    OUTPUT.write_text(render(), encoding="utf-8", newline="\n")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
