#!/usr/bin/env python3
"""The deterministic part of the use case derive-semantics of the plugin clean-derived-norms.

Run from the root of the repository of layer 2, the working directory, as:
    uv run --with "lark[interegular]" python3 -I -B <this script> <command>
Commands: worklist, tree <norm ID>..., seal --model <model ID>, check,
stale-citations. The script never writes a declaration of the Lean code,
never decides the state of a fragment, and holds nothing specific to Clean.

Spec: use-cases/derive-semantics/specs/derive-semantics.md (DSM) of the plugin.
"""

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import types
from pathlib import Path

# The script of the grammar, used as a library: the tree, the case text, the
# citations, the plugin and the parser of DGR-11 and DGR-13 (DSM-7).
GRAMMAR_SCRIPT = Path(__file__).resolve().parents[1] / "derive-grammar" / "derive_grammar.py"


def load_grammar_script():
    """Load the script of the grammar as a module.

    Spec: DSM-7 (Deliberate design: the parser of the grammar).
    """
    spec = importlib.util.spec_from_file_location("derive_grammar_for_semantics", GRAMMAR_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


dg = load_grammar_script()
InputError = dg.InputError

TREE_REL = dg.TREE_REL
GRAMMAR_REL = dg.GRAMMAR_REL
FOLDER_REL = "specs-derived/semantics"
STATUS_NAME = "clean-language-code-examples-status.jsonl"
STATUS_REL = FOLDER_REL + "/" + STATUS_NAME
LEAN_CODE = ["Clean.lean", "Clean/Ast.lean", "Clean/Syntax.lean", "Clean/Typing.lean", "Clean/Evaluation.lean"]

PLUGIN_NAME = dg.PLUGIN_NAME
PLUGIN_ROOT = Path(__file__).resolve().parents[2]
INSTALLED_PLUGINS = dg.INSTALLED_PLUGINS

NO_FORM_REASON = dg.NO_FORM_REASON
NOT_PARSED_REASON = "the grammar does not parse it"
FIXED_REASONS = (NO_FORM_REASON, NOT_PARSED_REASON)
OUTPUT_INFO = "clean-language-output"
STATES = ("derived", "pending")
BUILD_SECONDS = 900
RUN_SECONDS = 10

VALID_FORM = re.compile(r"clean-language expect=valid")
ERROR_FORM = re.compile(r"clean-language expect=error code=(" + dg.CODE + r")")
SYNTAX_FORM = re.compile(r"clean-language expect=syntax-error code=" + dg.CODE + r" line=(0|[1-9][0-9]*)")
CASE_RE = re.compile(r"run|error " + dg.CODE)
CODE_RE = re.compile(dg.CODE)
LEAN_CITATION_RE = re.compile(r"^-- (" + dg.NORM_ID + r")@([0-9a-f]{8}): (\S.*)$")
# The names of the parse tree of a program of several files, which no grammar of Lark gives (DSM-7).
PROGRAM_RULE = "%program"
FILE_RULE = "%file"
PATH_TYPE = "%path"

# ---------------------------------------------------------------- the fixed files (DSM-3)

LAKEFILE = """name = "clean-semantics"
version = "0.1.0"
defaultTargets = ["fragment"]

[[lean_lib]]
name = "Fragment"

[[lean_lib]]
name = "Clean"

[[lean_exe]]
name = "fragment"
root = "Main"
"""

TOOLCHAIN = "leanprover/lean4:v4.34.1\n"

FRAGMENT_LEAN = r"""namespace Fragment

inductive Tree where
  | rule (name : String) (children : List Tree)
  | token (type : String) (text : String)
  | absent
  deriving Repr, Inhabited, BEq

structure Outcome where
  code : Option String
  output : String
  deriving Repr, Inhabited, BEq

def unescape (text : String) : String := Id.run do
  let mut out := ""
  let mut escaped := false
  for c in text.toList do
    if escaped then
      out := out.push (if c == 'n' then '\n' else if c == 'r' then '\r' else c)
      escaped := false
    else if c == '\\' then
      escaped := true
    else
      out := out.push c
  return out

partial def readAt (lines : Array String) (index : Nat) : Option (Tree × Nat) := do
  let line ← lines[index]?
  match line.splitOn " " with
  | ["absent"] => return (Tree.absent, index + 1)
  | "token" :: type :: _ =>
    let text := String.mk (line.toList.drop (6 + type.length + 1))
    return (Tree.token type (unescape text), index + 1)
  | ["rule", name, count] =>
    let total ← count.toNat?
    let mut next := index + 1
    let mut children : Array Tree := #[]
    for _ in [0:total] do
      let (child, after) ← readAt lines next
      children := children.push child
      next := after
    return (Tree.rule name children.toList, next)
  | _ => none

def read (input : String) : Option Tree := do
  let lines := (input.splitOn "\n").toArray
  let (tree, next) ← readAt lines 0
  if lines.size == next + 1 && lines[next]! == "" then some tree else none

end Fragment
"""

MAIN_LEAN = """import Fragment
import Clean

partial def readAll (stream : IO.FS.Stream) (text : String) : IO String := do
  let line ← stream.getLine
  if line.isEmpty then return text else readAll stream (text ++ line)

def main : IO UInt32 := do
  let input ← readAll (← IO.getStdin) ""
  match Fragment.read input with
  | none =>
    IO.eprintln "fragment: the parse tree on standard input is not well formed"
    return 2
  | some tree =>
    let outcome := Clean.outcome tree
    IO.print ((outcome.code.getD "-") ++ "\\n" ++ outcome.output)
    return 0
"""

FIXED = {"lakefile.toml": LAKEFILE, "lean-toolchain": TOOLCHAIN, "Fragment.lean": FRAGMENT_LEAN, "Main.lean": MAIN_LEAN}
HASHED = [("lakefile_sha256", "lakefile.toml"), ("lean_toolchain_sha256", "lean-toolchain"),
          ("fragment_sha256", "Fragment.lean"), ("main_sha256", "Main.lean"), ("clean_sha256", "Clean.lean"),
          ("ast_sha256", "Clean/Ast.lean"), ("syntax_sha256", "Clean/Syntax.lean"),
          ("typing_sha256", "Clean/Typing.lean"), ("evaluation_sha256", "Clean/Evaluation.lean")]
META_KEYS = ["type", "specs_commit", "generator", "model"] + [k for k, _ in HASHED] + ["status_sha256"]
FRAGMENT_KEYS = ["type", "id", "hash", "cases", "expected_output", "parse_tree_hash", "state", "reason", "issue"]
LAYOUT = set(FIXED) | set(LEAN_CODE) | {STATUS_NAME}
IMPORTS = {"Fragment"} | {p[:-len(".lean")].replace("/", ".") for p in LEAN_CODE if "/" in p}

# ---------------------------------------------------------------- fragments (DSM-2, DSM-6)


def info(node):
    """The info string of a code block, or None.

    Spec: DSM-2.
    """
    return dg.info_string(node.get("own_text", ""))


def is_semantic_fragment(node):
    """A fragment whose info string is not of the form expect=syntax-error of CEX-4.

    Spec: DSM-2 (Terms: Semantic fragment).
    """
    return dg.is_fragment(node) and not SYNTAX_FORM.fullmatch(info(node) or "")


def case_kinds(node):
    """The cases of a semantic fragment: ["run"], ["error <code>"], or [] with no form of CEX-4.

    Spec: DSM-6.
    """
    text = info(node) or ""
    if VALID_FORM.fullmatch(text):
        return ["run"]
    match = ERROR_FORM.fullmatch(text)
    return [f"error {match.group(1)}"] if match else []


def is_output_block(node):
    """An active code block whose info string is exactly clean-language-output.

    Spec: DSM-2 (Terms: Expected output block).
    """
    return node.get("kind") == "code_block" and node.get("status") == "active" and info(node) == OUTPUT_INFO


def own_offset(tree, parent, position):
    """The offset in the own text of a parent of a byte position of its file.

    The own text of a parent is its bytes without the spans of its active children.

    Spec: DSM-2 (Terms: Expected output of a fragment).
    """
    children = tree.children.get(parent["id"], [])
    return (position - parent["start"]) - sum(c["end"] - c["start"] for c in children if c["end"] <= position)


def expected_output(tree, node):
    """The expected output block of a fragment with expect=valid, or None.

    It is the next active child of the fragment's parent, in the order of
    data/tree.jsonl, when it is an expected output block and the own text of
    the parent between the two holds only blanks and line breaks.

    Spec: DSM-2 (Terms: Expected output of a fragment).
    """
    if case_kinds(node) != ["run"]:
        return None
    parent = tree.nodes.get(node.get("parent"))
    if parent is None:
        return None
    siblings = tree.children.get(parent["id"], [])
    index = next((i for i, s in enumerate(siblings) if s["id"] == node["id"]), None)
    if index is None or index + 1 >= len(siblings) or not is_output_block(siblings[index + 1]):
        return None
    following = siblings[index + 1]
    own = parent.get("own_text", "").encode("utf-8")
    start, end = own_offset(tree, parent, node["end"]), own_offset(tree, parent, following["start"])
    if not 0 <= start <= end <= len(own):
        return None
    between = own[start:end].decode("utf-8", "replace")
    return following if between.strip(" \t\r\n") == "" else None


def expected_output_citation(tree, node):
    """The expected output of a fragment as "<norm ID>@<norm hash>", or None.

    Spec: DSM-5.
    """
    block = expected_output(tree, node)
    return f"{block['id']}@{tree.norm_hash(block['id'])}" if block else None


def expected_output_text(tree, block):
    """The code of an expected output block, without the indentation of its fence, each line followed by one line feed.

    Spec: DSM-2 (Terms: Expected output text), CEX-29.
    """
    lines = block["own_text"].split("\n")
    fence = dg.opening_match(block["own_text"]).group(2)
    indent = dg.fence_indent(tree, block)
    body = lines[1:]
    if body and re.match(r"^[ \t]*" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}[ \t]*$", body[-1]):
        body = body[:-1]
    return "".join(dg.strip_columns(line, indent) + "\n" for line in body)


# ---------------------------------------------------------------- the parse tree (DSM-7)


def load_grammar(root):
    """The parser of the grammar, as DGR-11 and DGR-13 build it, keeping every token in the tree.

    The parser is built by the script of the grammar; only keep_all_tokens is
    added to its options. A missing grammar, or one that does not build, is an
    InputError.

    Spec: DSM-1, DSM-7.
    """
    path = root / GRAMMAR_REL
    if not path.is_file():
        raise InputError(f"{path} does not exist: derive-grammar runs first")
    text = path.read_text(encoding="utf-8")
    statements, _ = dg.parse_grammar(text)
    lark, indenter_class = dg.import_lark()

    class KeepAllTokens(lark.Lark):
        """Lark with the options of the script of the grammar, and keep_all_tokens.

        Spec: DSM-7.
        """

        def __init__(self, grammar, **options):
            """Add keep_all_tokens to the options.

            Spec: DSM-7.
            """
            options["keep_all_tokens"] = True
            super().__init__(grammar, **options)

    original = dg.import_lark
    dg.import_lark = lambda: (types.SimpleNamespace(Lark=KeepAllTokens), indenter_class)
    try:
        return dg.build_parser(text, statements)
    except Exception as error:  # noqa: BLE001 - every build error stops the script
        first = (str(error).strip().split("\n") or [""])[0]
        raise InputError(f"{path}: the grammar does not build: {type(error).__name__}: {first}")
    finally:
        dg.import_lark = original


def parse(grammar, text):
    """Parse the program of a case text: (its parse tree, None), or (None, the message of the failure).

    The files are split and parsed alone, in their order, as DGR-19 says. A
    case text with no file line gives the tree of its one file; one with a
    file line gives a rule %program of one rule %file per file: a token %path
    with its path, or absent, then the tree of the file.

    Spec: DSM-7.
    """
    parser, indenter = grammar
    files, trees, failure = dg.parse_program(parser, indenter, text)
    if failure is not None:
        return None, failure[2]
    if not files[0].file_line:
        return generic(trees[0]), None
    return ("rule", PROGRAM_RULE, [
        ("rule", FILE_RULE, [("token", PATH_TYPE, f.path_of_file_line) if f.path_of_file_line is not None else ("absent",), generic(tree)])
        for f, tree in zip(files, trees)]), None


def generic(node):
    """The parse tree as nested tuples: ("rule", name, children), ("token", type, text) or ("absent",).

    A token of a terminal that the grammar names with one leading "_", such
    as _NL, is left out; a type that Lark gives a string of the grammar, such
    as __ANON_0, starts with two and is kept.

    Spec: DSM-7.
    """
    from lark import Token
    if node is None:
        return ("absent",)
    if isinstance(node, Token):
        return ("token", node.type, str(node))
    children = [generic(c) for c in node.children if not (isinstance(c, Token) and hidden_terminal(c.type))]
    return ("rule", str(node.data), children)


def hidden_terminal(name):
    """A terminal that the grammar names with one leading "_", which the tree leaves out.

    Spec: DSM-7.
    """
    return name.startswith("_") and not name.startswith("__")


def escape(text):
    """A token text with "\\" written "\\\\", a line feed "\\n" and a carriage return "\\r".

    Spec: DSM-7.
    """
    return text.replace("\\", "\\\\").replace("\n", "\\n").replace("\r", "\\r")


def serialize(tree):
    """The serialized tree: one line per node, in preorder, each ended by a line feed.

    Spec: DSM-7.
    """
    out, todo = [], [tree]
    while todo:
        node = todo.pop()
        if node[0] == "absent":
            out.append("absent")
        elif node[0] == "token":
            out.append(f"token {node[1]} {escape(node[2])}")
        else:
            out.append(f"rule {node[1]} {len(node[2])}")
            todo.extend(reversed(node[2]))
    return "".join(line + "\n" for line in out)


def display(tree):
    """The parse tree for the deriver: one node per line, two spaces per level.

    Spec: DSM-7.
    """
    out, todo = [], [(tree, 0)]
    while todo:
        node, depth = todo.pop()
        pad = "  " * depth
        if node[0] == "absent":
            out.append(pad + "(absent)")
        elif node[0] == "token":
            out.append(f"{pad}{node[1]} {json.dumps(node[2], ensure_ascii=False)}")
        else:
            out.append(pad + node[1])
            todo.extend((child, depth + 1) for child in reversed(node[2]))
    return "\n".join(out) + "\n"


def tree_hash(serialized):
    """The parse tree hash: the first 8 hex digits of the SHA-256 of the serialized tree.

    Spec: DSM-7 (Terms: Parse tree hash).
    """
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:8]


def facts(tree, grammar, node):
    """What the script gives for a semantic fragment: cases, expected output, parse tree and its hash.

    Spec: DSM-5, DSM-6, DSM-7.
    """
    cases = case_kinds(node)
    block = expected_output(tree, node)
    out = {"cases": cases, "expected_output": expected_output_citation(tree, node),
           "expected_output_text": expected_output_text(tree, block) if block else None,
           "parse_tree_hash": None, "parse_error": None, "serialized": None, "generic": None}
    if cases:
        parsed, error = parse(grammar, dg.case_text(tree, node))
        if error is not None:
            out["parse_error"] = error
        else:
            out["generic"] = parsed
            out["serialized"] = serialize(out["generic"])
            out["parse_tree_hash"] = tree_hash(out["serialized"])
    return out


def semantic_fragments(tree):
    """The semantic fragments of the tree, in its order.

    Spec: DSM-2.
    """
    return [n for n in tree.fragments if is_semantic_fragment(n)]


# ---------------------------------------------------------------- the Lean code (DSM-8, DSM-10)

DECLARATION_RE = re.compile(
    r"^(?:@\[[^\]]*\][ \t]*)*(?:(?:private|protected|noncomputable|partial|unsafe|nonrec)[ \t]+)*"
    r"(deriving[ \t]+instance|def|theorem|abbrev|inductive|structure|class|instance|opaque|example|macro_rules|macro"
    r"|syntax|notation|infixl|infixr|infix|prefix|postfix)(?=[ \t(\[{:]|$)(.*)$")
STRUCTURAL_RE = re.compile(r"^(import|namespace|end|open|section|mutual|variable|universe|set_option)(?=[ \t]|$)(.*)$")
CONTINUATION_RE = re.compile(r"^(\||where|deriving|termination_by|decreasing_by)(?=[ \t]|$)")
NAMED = ("def", "theorem", "abbrev", "inductive", "structure", "class", "opaque", "instance")
NAME_RE = re.compile(r"^[ \t]+([A-Za-z_][A-Za-z0-9_.'!?]*)")
CHAR_RE = re.compile(r"'(?:\\(?:x[0-9a-fA-F]{2}|u\{[0-9a-fA-F]+\}|.)|[^'\\\n])'")
SHORTCUT_RE = re.compile(r"(?<![A-Za-z0-9_.'])(sorry|admit|axiom)(?![A-Za-z0-9_'!?])")


class Declaration:
    """One declaration of the Lean code, with the citations just above it.

    Spec: DSM-8 (Terms: Declaration, Key of a declaration).
    """

    def __init__(self, path, line, key, citations):
        """A declaration at its first line.

        Spec: DSM-8.
        """
        self.path = path
        self.line = line
        self.key = key
        self.citations = citations


def lean_scan(text):
    """The Lean text with its comments and literals blanked, its comments and its string literals.

    Returns (code, comments, strings): code keeps every line break and
    column; comments is [(offset, end, is_line_comment)]; strings is
    [(offset, content)], the content with its escapes as written.

    Spec: DSM-8, DSM-10.
    """
    code, comments, strings = list(text), [], []
    index, size = 0, len(text)

    def blank(start, end):
        """Blank a span, keeping its line breaks.

        Spec: DSM-8.
        """
        for k in range(start, end):
            if code[k] != "\n":
                code[k] = " "

    while index < size:
        if text.startswith("--", index):
            end = text.find("\n", index)
            end = size if end < 0 else end
            comments.append((index, end, True))
            blank(index, end)
            index = end
        elif text.startswith("/-", index):
            depth, end = 1, index + 2
            while end < size and depth:
                if text.startswith("/-", end):
                    depth, end = depth + 1, end + 2
                elif text.startswith("-/", end):
                    depth, end = depth - 1, end + 2
                else:
                    end += 1
            comments.append((index, end, False))
            blank(index, end)
            index = end
        elif text[index] == '"':
            end = index + 1
            while end < size and text[end] != '"':
                end += 2 if text[end] == "\\" else 1
            strings.append((index, text[index + 1:end]))
            blank(index, min(end + 1, size))
            index = end + 1
        elif text[index] == "'" and (index == 0 or not (text[index - 1].isalnum() or text[index - 1] in "_'.!?")):
            match = CHAR_RE.match(text, index)
            if match:
                blank(index, match.end())
                index = match.end()
            else:
                index += 1
        else:
            index += 1
    return "".join(code), comments, strings


def decode_lean_string(content):
    """The text of a Lean string literal, its simple escapes decoded.

    Spec: DSM-10.
    """
    table = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\", '"': '"', "'": "'"}
    return re.sub(r"\\(.)", lambda m: table.get(m.group(1), m.group(0)), content, flags=re.S)


def parse_lean(path, text):
    """The declarations of one file of the Lean code, and the problems of its comments, citations and lines.

    Spec: DSM-8, DSM-10.
    """
    code, comments, strings = lean_scan(text)
    starts = [0] + [i + 1 for i, c in enumerate(text) if c == "\n"]

    def line_of(offset):
        """The line, from 1, of an offset.

        Spec: DSM-8.
        """
        low, high = 0, len(starts) - 1
        while low < high:
            middle = (low + high + 1) // 2
            if starts[middle] <= offset:
                low = middle
            else:
                high = middle - 1
        return low + 1

    problems, citation_lines = [], {}
    for start, end, is_line in comments:
        number = line_of(start)
        match = LEAN_CITATION_RE.match(text[start:end]) if is_line and start == starts[number - 1] else None
        if match:
            citation_lines[number] = (match.group(1), match.group(2))
        else:
            what = "a comment that is not a citation" if is_line else "a block comment"
            problems.append(("comment", f"{path}:{number}", what))
    declarations, pending, current, spaces = [], [], None, []
    lines, raw_lines = code.split("\n"), text.split("\n")

    def flush(where):
        """Report the citations that stand above no declaration.

        Spec: DSM-8.
        """
        for number, _, _ in pending:
            problems.append(("citation", f"{path}:{number}", f"a citation not just above a declaration{where}"))
        pending.clear()

    for number, line in enumerate(lines, 1):
        if number in citation_lines:
            pending.append((number, *citation_lines[number]))
            continue
        if not line.strip():
            flush("")
            continue
        if line[0] in " \t":
            if current is None:
                problems.append(("declaration", f"{path}:{number}", "an indented line outside a declaration"))
            flush(", inside a declaration")
            continue
        declaration = DECLARATION_RE.match(line)
        structural = STRUCTURAL_RE.match(line)
        if declaration:
            word = re.sub(r"[ \t]+", " ", declaration.group(1))
            name = NAME_RE.match(declaration.group(2)) if word in NAMED else None
            qualified = None
            if name:
                qualified = name.group(1)
                if qualified.startswith("_root_."):
                    qualified = qualified[len("_root_."):]
                else:
                    qualified = ".".join([s for s in spaces if s] + [qualified])
            key = f"{path}:{qualified}" if qualified else f"{path}:{raw_lines[number - 1].rstrip()}"
            current = Declaration(path, number, key, list(pending))
            pending.clear()
            if not current.citations:
                problems.append(("citation", key, "a declaration with no citation just above it"))
            declarations.append(current)
        elif structural:
            flush(f", above the structural line {structural.group(1)}")
            current = None
            word, rest = structural.group(1), structural.group(2).split()
            if word == "namespace":
                spaces.append(rest[0] if rest else "")
            elif word == "section":
                spaces.append("")
            elif word == "end" and spaces:
                spaces.pop()
            elif word == "import":
                for module in rest:
                    if module not in IMPORTS:
                        problems.append(("shortcut", f"{path}:{number}", f"imports {module}; only Fragment and the files of Clean/"))
        elif CONTINUATION_RE.match(line) and current is not None:
            flush(", inside a declaration")
        else:
            problems.append(("declaration", f"{path}:{number}", "a line at column 1 that is no citation, no declaration, no structural line, and continues no declaration"))
    flush("")
    for match in SHORTCUT_RE.finditer(code):
        problems.append(("shortcut", f"{path}:{line_of(match.start())}", f"the Lean code holds {match.group(1)}"))
    literals = [(line_of(offset), decode_lean_string(content)) for offset, content in strings]
    return declarations, problems, literals


def read_lean(folder):
    """The declarations, the problems and the string literals of every file of the Lean code that exists.

    Spec: DSM-8, DSM-10.
    """
    declarations, problems, literals = [], [], []
    for rel in LEAN_CODE:
        path = folder / rel
        if path.is_file():
            found, issues, strings = parse_lean(rel, path.read_text(encoding="utf-8"))
            declarations += found
            problems += issues
            literals += [(rel, number, text) for number, text in strings]
    return declarations, problems, literals


def check_root_imports(folder):
    """Clean.lean imports the four files of Clean/, so that one build builds them all.

    Spec: DSM-3, DSM-13.
    """
    path = folder / "Clean.lean"
    imported = set()
    for line in path.read_text(encoding="utf-8").split("\n") if path.is_file() else []:
        match = STRUCTURAL_RE.match(line)
        if match and match.group(1) == "import":
            imported |= set(match.group(2).split())
    return [("layout", "Clean.lean", f"does not import {module}") for module in sorted(IMPORTS - {"Fragment"} - imported)]


def check_declarations(tree, declarations, status_by_id):
    """The citations of the declarations: each checks, once per norm, and one at least is a prose norm.

    Spec: DSM-8, DSM-9.
    """
    problems = []
    for d in declarations:
        cited, prose = set(), False
        for number, norm_id, norm_hash in d.citations:
            if norm_id in cited:
                problems.append(("citation", d.key, f"line {number}: {norm_id} is cited twice; one citation line per norm"))
            cited.add(norm_id)
            message = dg.check_citation(tree, norm_id, norm_hash)
            node = tree.nodes.get(norm_id)
            if message is None and node is not None and is_semantic_fragment(node):
                line = status_by_id.get(norm_id)
                if line is None or line.get("state") != "derived":
                    message = f"{norm_id} is {line.get('state') if line else 'without a status line'}"
            if message:
                problems.append(("citation", d.key, f"line {number}: {message}"))
            if node is not None and not dg.is_fragment(node) and not is_output_block(node):
                prose = True
        if d.citations and not prose:
            problems.append(("citation", d.key, "cites no prose norm"))
    return problems


def check_literals(tree, literals, outputs):
    """No string literal holds the norm ID of a fragment, or is the expected output text of a fragment of two lines or more.

    Spec: DSM-10 (No shortcut).
    """
    problems = []
    ids = [n["id"] for n in tree.fragments]
    pattern = re.compile(r"(?<![A-Za-z0-9-])(" + "|".join(re.escape(i) for i in ids) + r")(?![0-9])") if ids else None
    long_outputs = {text: norm_id for norm_id, text in outputs.items() if text and text.count("\n") >= 2}
    for path, number, text in literals:
        found = pattern.search(text) if pattern else None
        if found:
            problems.append(("shortcut", f"{path}:{number}", f"a string literal holds the norm ID of the fragment {found.group(1)}"))
        if text in long_outputs:
            problems.append(("shortcut", f"{path}:{number}", f"a string literal is the expected output text of {long_outputs[text]}"))
    return problems


# ---------------------------------------------------------------- status and meta (DSM-4, DSM-5)


def previous_status(root):
    """The fragment lines of the status file of the previous run, or None when it does not exist.

    Spec: DSM-12.
    """
    path = root / STATUS_REL
    if not path.is_file():
        return None
    return [r for r in dg.load_jsonl(path, "status") if r.get("type") == "fragment"]


def check_status(tree, status_path, rows, current):
    """The checks of the fragment lines of the status file.

    current: {norm ID: facts} of every semantic fragment.

    Spec: DSM-5, DSM-9, DSM-13.
    """
    problems, by_id, counts, order = [], {}, {}, []
    for index, (number, line, value, error) in enumerate(rows):
        where = f"{status_path}:{number}"
        if value is None:
            problems.append(("status", where, error))
            continue
        if value.get("type") == "meta":
            if index > 0:
                problems.append(("meta", where, "a meta line that is not the first line"))
            continue
        if list(value) != FRAGMENT_KEYS or value.get("type") != "fragment":
            missing = [k for k in FRAGMENT_KEYS if k not in value]
            what = f"lacks the fields {', '.join(missing)}" if missing else f"does not have exactly the fields {', '.join(FRAGMENT_KEYS)}, in that order"
            problems.append(("status", where, what))
            if missing:
                continue
        norm_id = value["id"]
        if not isinstance(norm_id, str):
            problems.append(("status", where, "id is not a string"))
            continue
        counts[norm_id] = counts.get(norm_id, 0) + 1
        by_id.setdefault(norm_id, value)
        order.append(norm_id)
        state, reason, issue, cases = value["state"], value["reason"], value["issue"], value["cases"]
        if not (isinstance(cases, list) and len(cases) <= 1 and all(isinstance(c, str) and CASE_RE.fullmatch(c) for c in cases)):
            problems.append(("status", norm_id, f"cases {json.dumps(cases)} is not [\"run\"], [\"error <error code>\"] or []"))
        if not isinstance(state, str) or state not in STATES:
            problems.append(("status", norm_id, f"state {state!r} is not derived or pending"))
        if not isinstance(value["hash"], str) or not re.fullmatch(r"[0-9a-f]{8}", value["hash"]):
            problems.append(("status", norm_id, "hash is not 8 hex digits"))
        if state == "derived" and reason is not None:
            problems.append(("status", norm_id, "a derived fragment has a reason"))
        if state != "derived" and not (isinstance(reason, str) and reason.strip()):
            problems.append(("status", norm_id, f"a {state} fragment has no reason"))
        if state != "pending" and issue is not None:
            problems.append(("status", norm_id, "an issue on a fragment that is not pending"))
        if state == "pending" and issue is not None and not (isinstance(issue, str) and dg.ISSUE_RE.fullmatch(issue)):
            problems.append(("status", norm_id, "the issue is not an issue URL of the foundation"))
        if reason in FIXED_REASONS and issue is not None:
            problems.append(("issue", norm_id, f"pending with the reason \"{reason}\", which opens no issue of its own (DSM-5)"))
        if isinstance(reason, str):
            for cited, cited_hash in dg.INLINE_CITATION_RE.findall(reason):
                message = dg.check_citation(tree, cited, cited_hash)
                if message:
                    problems.append(("reason-citation", norm_id, message))
    problems += dg.check_unique_issues(rows)
    for norm_id, count in counts.items():
        if norm_id not in current:
            problems.append(("status", norm_id, "a status line of a norm that is not a semantic fragment"))
        elif count > 1:
            problems.append(("status", norm_id, f"{count} status lines"))
    known = [i for i in order if i in current]
    if known != sorted(known, key=lambda i: tree.order[i]):
        problems.append(("status", str(status_path), "the fragment lines do not follow the order of data/tree.jsonl"))
    for norm_id, fact in current.items():
        line = by_id.get(norm_id)
        if line is None:
            problems.append(("status", norm_id, "no status line"))
            continue
        if line["hash"] != tree.norm_hash(norm_id):
            problems.append(("status", norm_id, f"the status line holds the hash {line['hash']}; the norm hash is {tree.norm_hash(norm_id)}"))
        for field in ("cases", "expected_output", "parse_tree_hash"):
            if line[field] != fact[field]:
                problems.append(("status", norm_id, f"the status line holds the {field} {json.dumps(line[field])}; the script gives {json.dumps(fact[field])}"))
        reason = line["reason"] if isinstance(line["reason"], str) else ""
        if not fact["cases"] and (line["state"] != "pending" or reason != NO_FORM_REASON):
            problems.append(("opening line", norm_id, f"{NO_FORM_REASON}: the fragment is pending with exactly that reason"))
        elif fact["cases"] and fact["parse_error"] is not None and (line["state"] != "pending" or reason != NOT_PARSED_REASON):
            problems.append(("parse", norm_id, f"{NOT_PARSED_REASON}: the fragment is pending with exactly that reason; {fact['parse_error']}"))
        if line["state"] == "pending":
            problems.append(("pending", norm_id, f"pending: {reason}"))
            if reason not in FIXED_REASONS and not dg.INLINE_CITATION_RE.search(reason):
                problems.append(("pending", norm_id, "the reason cites no norm"))
    return problems, by_id


def check_meta(tree, folder, status_path, rows, version):
    """The meta line: first, its fields, the specs commit, the generator, the model and the hashes.

    Spec: DSM-4, DSM-13, DSM-16.
    """
    where = str(status_path)
    if not rows:
        return [("meta", where, "the status file has no meta line")]
    number, _, meta, _ = rows[0]
    if meta is None:
        return []  # check_status reports a first line that is not JSON
    if meta.get("type") != "meta":
        return [("meta", f"{where}:{number}", "the first line is not the meta line")]
    problems = []
    if list(meta) != META_KEYS:
        problems.append(("meta", f"{where}:{number}", f"the meta line does not have exactly the fields {', '.join(META_KEYS)}, in that order"))
    if meta.get("specs_commit") != tree.specs_commit:
        problems.append(("meta", "specs_commit", f"{meta.get('specs_commit')}; data/tree.jsonl has {tree.specs_commit}"))
    problems += dg.check_generator(meta, version)
    problems += dg.check_model(meta)
    for key, rel in HASHED:
        path = folder / rel
        if not path.is_file() or meta.get(key) != dg.sha256(path.read_bytes()):
            problems.append(("meta", key, f"{rel} does not match the hash of its meta line: changed after the last seal"))
    if meta.get("status_sha256") != dg.sha256(dg.body_bytes(status_path.read_text(encoding="utf-8"))):
        problems.append(("meta", "status_sha256", "the status file does not match the hash of its meta line: changed after the last seal"))
    return problems


def check_layout(folder):
    """The semantics folder holds exactly the files of DSM-3, and each fixed file holds the text of the script.

    Spec: DSM-3.
    """
    problems = []
    entries = sorted(folder.iterdir()) + (sorted((folder / "Clean").iterdir()) if (folder / "Clean").is_dir() else [])
    for path in entries:
        rel = path.relative_to(folder).as_posix()
        if path.is_dir() and rel != "Clean":
            problems.append(("layout", str(path), "a folder that DSM-3 does not list"))
        elif not path.is_dir() and rel not in LAYOUT:
            problems.append(("layout", str(path), "a file that DSM-3 does not list"))
    for rel, text in FIXED.items():
        path = folder / rel
        if not path.is_file() or path.read_text(encoding="utf-8") != text:
            problems.append(("fixed", rel, "does not hold the text that the script holds: seal writes it"))
    return problems


# ---------------------------------------------------------------- build and run (DSM-11, DSM-13)


def lake_command():
    """The lake on PATH; InputError when there is none.

    Spec: DSM-13.
    """
    found = shutil.which("lake")
    if found is None:
        raise InputError("lake cannot be run: it is not on PATH")
    return found


def build(folder, workdir, lake):
    """Copy the Lake project to a work folder and build it: (path of the executable, None) or (None, the error).

    Spec: DSM-1, DSM-13.
    """
    target = workdir / "semantics"
    for rel in list(FIXED) + LEAN_CODE:
        (target / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(folder / rel, target / rel)
    try:
        result = subprocess.run([lake, "build"], cwd=target, capture_output=True, text=True, timeout=BUILD_SECONDS)
    except subprocess.TimeoutExpired:
        return None, f"the build took more than {BUILD_SECONDS} seconds"
    except OSError as error:
        raise InputError(f"lake cannot be run: {error}")
    if result.returncode != 0:
        lines = (result.stdout + "\n" + result.stderr).split("\n")
        first = next((l.strip() for l in lines if "error" in l.lower()), next((l.strip() for l in lines if l.strip()), ""))
        return None, f"lake build exited with {result.returncode}: {first}"
    return target / ".lake" / "build" / "bin" / "fragment", None


def run_fragment(executable, serialized):
    """Run one fragment: (code or None, output bytes, None), or (None, None, the error).

    Spec: DSM-11.
    """
    try:
        result = subprocess.run([str(executable)], input=serialized.encode("utf-8"), capture_output=True, timeout=RUN_SECONDS)
    except subprocess.TimeoutExpired:
        return None, None, f"the run took more than {RUN_SECONDS} seconds"
    except OSError as error:
        return None, None, f"the executable cannot run: {error}"
    if result.returncode != 0:
        message = result.stderr.decode("utf-8", "replace").strip().split("\n")[0]
        return None, None, f"the executable exited with {result.returncode}: {message}"
    head, newline, output = result.stdout.partition(b"\n")
    if not newline:
        return None, None, "the executable printed no line feed after the code"
    code = head.decode("utf-8", "replace")
    return (None if code == "-" else code), output, None


def judge(case, expected_text, code, output):
    """Whether a case passes: None, or what is wrong.

    Spec: DSM-11.
    """
    if case == "run":
        if code is not None:
            return f"a valid program gives no code, and the semantics gives {code}"
        if expected_text is not None and output != expected_text.encode("utf-8"):
            return f"the output {json.dumps(output.decode('utf-8', 'replace'), ensure_ascii=False)} is not the expected output {json.dumps(expected_text, ensure_ascii=False)}"
        return None
    wanted = case.split(" ", 1)[1]
    if code != wanted:
        return f"the semantics gives {code if code is not None else 'no code'}, and the case is {wanted}"
    return None


# ---------------------------------------------------------------- commands


def worklist(root):
    """The items that a change calls for, one JSON object each.

    Spec: DSM-12.
    """
    tree = dg.load_tree(root)
    grammar = load_grammar(root)
    lines = previous_status(root)
    absent = lines is None
    lines = lines or []
    by_id = {}
    for line in lines:
        if isinstance(line.get("id"), str):
            by_id.setdefault(line["id"], line)
    items, ids = [], set()
    for node in semantic_fragments(tree):
        norm_id = node["id"]
        ids.add(norm_id)
        fact = facts(tree, grammar, node)
        old = by_id.get(norm_id)
        item = {"kind": None, "id": norm_id, "old_hash": None, "new_hash": tree.norm_hash(norm_id), "cases": fact["cases"],
                "expected_output": fact["expected_output"], "parse_tree_hash": fact["parse_tree_hash"],
                "parse_error": fact["parse_error"], "file": node.get("file")}
        if old is None:
            item["kind"] = "new"
        else:
            item["old_hash"] = old.get("hash")
            reason = old.get("reason") if isinstance(old.get("reason"), str) else ""
            moved = any(dg.stale(tree, i, h) for i, h in dg.INLINE_CITATION_RE.findall(reason))
            if moved or old.get("hash") != item["new_hash"] or any(old.get(f) != fact[f] for f in ("cases", "expected_output", "parse_tree_hash")):
                item["kind"] = "changed"
        if item["kind"]:
            items.append(item)
    for line in lines:
        if isinstance(line.get("id"), str) and line["id"] not in ids:
            node = tree.nodes.get(line["id"])
            items.append({"kind": "gone", "id": line["id"], "old_hash": line.get("hash"), "new_hash": None,
                          "cases": line.get("cases"), "expected_output": line.get("expected_output"),
                          "parse_tree_hash": line.get("parse_tree_hash"), "parse_error": None,
                          "file": node.get("file") if node else None})
    if not absent:
        declarations, _, _ = read_lean(root / FOLDER_REL)
        for d in declarations:
            for _, norm_id, norm_hash in d.citations:
                change = dg.stale(tree, norm_id, norm_hash)
                if change:
                    items.append({"kind": "norm", "declaration": d.key, "old_hash": norm_hash, "new_hash": change[0],
                                  "citation": f"{norm_id}@{norm_hash}"})
    return items


def tree_report(root, ids):
    """The text that "tree" prints for the given norm IDs.

    Spec: DSM-7.
    """
    tree = dg.load_tree(root)
    grammar = load_grammar(root)
    for norm_id in ids:
        node = tree.nodes.get(norm_id)
        if node is None or not is_semantic_fragment(node):
            raise InputError(f"{norm_id} is not a semantic fragment")
    out = []
    for norm_id in ids:
        node = tree.nodes[norm_id]
        fact = facts(tree, grammar, node)
        out.append(f"== {norm_id}@{tree.norm_hash(norm_id)} cases={json.dumps(fact['cases'])} "
                   f"expected_output={json.dumps(fact['expected_output'])} parse_tree_hash={json.dumps(fact['parse_tree_hash'])} {node.get('file')}")
        out.append(dg.fragment_lines(tree, node)[0])
        out.append(dg.case_text(tree, node).rstrip("\n"))
        if fact["expected_output_text"] is not None:
            out.append("-- expected output --")
            out.append(fact["expected_output_text"].rstrip("\n"))
        if fact["generic"] is not None:
            out.append("-- parse tree --")
            out.append(display(fact["generic"]).rstrip("\n"))
        elif fact["parse_error"] is not None:
            out.append("-- parse error --")
            out.append(fact["parse_error"])
    return "\n".join(out) + "\n"


def seal(root, model, plugin_root=None, installed=None):
    """Write the fixed files, order the fragment lines as data/tree.jsonl and write the meta line first.

    Every input is read before anything is written.

    Spec: DSM-3, DSM-4, DSM-5, DSM-16.
    """
    tree = dg.load_tree(root)
    folder, status_path = root / FOLDER_REL, root / STATUS_REL
    for rel in LEAN_CODE:
        if not (folder / rel).is_file():
            raise InputError(f"{folder / rel} does not exist")
    version = dg.plugin_version(plugin_root if plugin_root is not None else PLUGIN_ROOT)
    fragments = []
    if status_path.is_file():
        for number, line, value, error in dg.read_status(status_path):
            if value is None:
                raise InputError(f"status {status_path}:{number}: {error}")
            if value.get("type") != "meta":
                fragments.append((line, value))
    end = len(tree.order)
    fragments.sort(key=lambda f: tree.order.get(f[1].get("id"), end))
    body = "".join(line + "\n" for line, _ in fragments)
    commit = dg.marketplace_commit(plugin_root if plugin_root is not None else PLUGIN_ROOT,
                                   installed if installed is not None else INSTALLED_PLUGINS)
    for rel, text in FIXED.items():
        (folder / rel).write_text(text, encoding="utf-8")
    meta = {"type": "meta", "specs_commit": tree.specs_commit,
            "generator": {"plugin": PLUGIN_NAME, "version": version, "marketplace_commit": commit},
            "model": model}
    for key, rel in HASHED:
        meta[key] = dg.sha256((folder / rel).read_bytes())
    meta["status_sha256"] = dg.sha256(body.encode("utf-8"))
    head = json.dumps(meta, ensure_ascii=False, separators=(",", ":"))
    status_path.write_text(head + "\n" + body, encoding="utf-8")
    return head


def check(root, script_path, plugin_root=None):
    """Every check of DSM-13; returns the problems and the counts.

    Spec: DSM-9, DSM-11, DSM-13.
    """
    tree = dg.load_tree(root)
    folder, status_path = root / FOLDER_REL, root / STATUS_REL
    for path in [status_path] + [folder / rel for rel in LEAN_CODE]:
        if not path.is_file():
            raise InputError(f"{path} does not exist")
    grammar = load_grammar(root)
    version = dg.plugin_version(plugin_root if plugin_root is not None else PLUGIN_ROOT)
    rows = dg.read_status(status_path)
    script_problems = dg.check_script(tree, script_path.read_text(encoding="utf-8"))
    counts = {state: 0 for state in STATES}
    passed = {"run": [0, 0], "error": [0, 0]}
    fragments = semantic_fragments(tree)
    if not fragments:
        problems = [p for p in check_layout(folder) if p[0] == "fixed"]
        problems += [("status", f"{status_path}:{n}", e) for n, _, v, e in rows[:1] if v is None]
        problems += check_meta(tree, folder, status_path, rows, version) + script_problems
        return problems, {"states": counts, "passed": passed}
    lake = lake_command()
    current = {n["id"]: facts(tree, grammar, n) for n in fragments}
    problems = check_layout(folder) + check_root_imports(folder)
    problems += check_meta(tree, folder, status_path, rows, version)
    status_problems, by_id = check_status(tree, status_path, rows, current)
    problems += status_problems
    declarations, lean_problems, literals = read_lean(folder)
    problems += lean_problems
    problems += check_declarations(tree, declarations, by_id)
    outputs = {i: f["expected_output_text"] for i, f in current.items()}
    problems += check_literals(tree, literals, outputs)
    problems += script_problems
    for norm_id, line in by_id.items():
        if norm_id in current and isinstance(line.get("state"), str) and line["state"] in counts:
            counts[line["state"]] += 1
    runnable = [(i, f) for i, f in current.items()
                if by_id.get(i, {}).get("state") == "derived" and f["cases"] and f["serialized"] is not None]
    if runnable:
        with tempfile.TemporaryDirectory(prefix="derive-semantics-") as work:
            executable, error = build(folder, Path(work), lake)
            if error:
                problems.append(("build", str(folder), error))
            for norm_id, fact in runnable:
                case = fact["cases"][0]
                kind = "run" if case == "run" else "error"
                passed[kind][1] += 1
                if executable is None:
                    continue
                code, output, failure = run_fragment(executable, fact["serialized"])
                wrong = failure or judge(case, fact["expected_output_text"], code, output)
                if wrong:
                    problems.append(("run", norm_id, wrong))
                else:
                    passed[kind][0] += 1
    return problems, {"states": counts, "passed": passed}


def main(argv=None):
    """The command line: worklist, tree <norm ID>..., seal --model <model ID>, check, stale-citations.

    Spec: DSM-4, DSM-7, DSM-12, DSM-13, DSM-17.
    """
    parser = argparse.ArgumentParser(prog="derive_semantics.py", description="The deterministic part of /clean-derived-norms:derive-semantics.")
    parser.add_argument("command", choices=["worklist", "tree", "seal", "check", "stale-citations"])
    parser.add_argument("ids", nargs="*", help="tree only: the norm IDs of the fragments")
    parser.add_argument("--model", help="seal only, and required there: the exact model ID the deriver runs as, such as claude-opus-5-5")
    args = parser.parse_args(argv)
    root = Path.cwd()
    if args.command == "seal" and args.model is None:
        print("error: seal needs --model <model ID>, the exact model ID the deriver runs as", file=sys.stderr)
        return 2
    if args.command == "tree" and not args.ids:
        print("error: tree needs one norm ID or more", file=sys.stderr)
        return 2
    script = Path(__file__).resolve()
    try:
        if args.command == "worklist":
            for item in worklist(root):
                print(json.dumps(item, ensure_ascii=False))
            return 0
        if args.command == "tree":
            sys.stdout.write(tree_report(root, args.ids))
            return 0
        if args.command == "seal":
            print(seal(root, args.model))
            return 0
        if args.command == "stale-citations":
            for item in dg.stale_script_citations(root, dg.load_tree(root), script.read_text(encoding="utf-8")):
                print(json.dumps(item, ensure_ascii=False))
            return 0
        problems, summary = check(root, script)
    except InputError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    for name, subject, message in problems:
        print(f"{name}: {subject}: {message}")
    states, passed = summary["states"], summary["passed"]
    print(f"fragments: {states['derived']} derived, {states['pending']} pending; "
          f"run passed {passed['run'][0]}/{passed['run'][1]}; "
          f"error passed {passed['error'][0]}/{passed['error'][1]}; "
          f"problems: {len(problems)}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
