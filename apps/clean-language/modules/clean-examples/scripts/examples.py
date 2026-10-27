"""The rules of the Clean examples that the text decides alone, shared by the audit and the hook.

Spec: specs/module.md (CEX-1 to CEX-26) and use-cases/audit/specs/audit.md (CAU-1 to CAU-9).
Python 3.9 or later, standard library only.
"""

import json
import os
import re
import subprocess
from collections import Counter

INFO_VALID = re.compile(r"clean-language expect=valid")
INFO_SYNTAX = re.compile(r"clean-language expect=syntax-error code=([A-Z]{3,6}[0-9]{3}) line=(0|[1-9][0-9]*)")
INFO_ERROR = re.compile(r"clean-language expect=error code=([A-Z]{3,6}[0-9]{3})")
FENCE_OPEN = re.compile(r"^( *)(`{3,}|~{3,})(.*)$")  # at most 3 spaces: checked in blocks()
DEFINITION = re.compile(r"^ {0,3}#{3,6}[ \t]+([A-Z]{3,6}[0-9]{3}) — \S")
CODE_TOKEN = re.compile(r"\b([A-Z]{3,6}[0-9]{3})\b")
FILE_LINE = re.compile(r"^// file: \S")
FAILS = re.compile(r"^//[ \t]*fails:")
REGISTRY = "specs/platform/error-codes.md"

# CEX term "Section line" (complete list).
SECTION_LINE = [re.compile(p) for p in (
    r"^libraries:\s+\S",
    r"^import:$", r"^source:$", r"^constant:$", r"^state:$",
    r"^can [A-Za-z][A-Za-z0-9_]*:$",
    r"^class [A-Za-z][A-Za-z0-9_]*(\s.*)?$",
    r"^functions:$",
    r"^watch [A-Za-z][A-Za-z0-9_]*:$",
    r"^tests:$", r"^start:$",
    r"^compiletime function\s+\S",
    r"^handles block\s+\S",
    r"^host interface\s+\S.*:$",
    r"^[a-z][A-Za-z0-9_]*:(\s.*)?$",
)]

MESSAGES = {  # CAU-8
    "CEX-2": "the info string clean is replaced by clean-language",
    "CEX-4": "the info string is not one of the forms of CEX-4",
    "CEX-6": "a syntax-error needs a code of prefix SYN and a line within the code",
    "CEX-7": "an error needs a code whose prefix is not SYN",
    "CEX-9": "the expected outcome goes on the opening line, not in a fails: comment",
    "CEX-10": "code at column 1 outside a section",
    "CEX-11": "a second file line, or a file line that is not line 1",
    "CEX-13": "a space in the indentation",
    "CEX-15": "a second definition of the error code",
    "CEX-16": "the error code has neither a definition nor a registry row",
    "CEX-17": "the error code is retired",
    "CEX-18": "a definition of a retired code",
}
SUSPECT_MESSAGE = "looks like a Clean source file outside a Clean example"


class Block:
    """A fenced block (CEX term) or an indented code block: its first line, info string and code."""

    def __init__(self, line, info, code, fenced=True):
        self.line = line  # the line of the file of its opening line (fenced) or first line (indented)
        self.info = info
        self.code = code  # list of str, line 1 of the code first
        self.fenced = fenced

    def key(self):
        return (self.info, tuple(self.code))

    def is_example(self):
        return self.fenced and (self.info == "clean-language" or self.info.startswith("clean-language "))

    def is_old(self):
        return self.fenced and (self.info == "clean" or self.info.startswith("clean "))


def split_lines(text):
    """The lines of a text: line ends are LF, CR or CRLF; no empty line after the last line end."""
    lines = re.split(r"\r\n|\r|\n", text)
    if len(lines) > 1 and lines[-1] == "":
        lines.pop()
    return lines


LIST_ITEM = re.compile(r"^( {0,3})([-*+]|[0-9]{1,9}[.)])( {1,4}(?! )|\t|$)")
QUOTE = re.compile(r"^ {0,3}> ?")
ATX = re.compile(r"^ {0,3}#{1,6}([ \t]|$)")


def leading(line):
    return len(line) - len(line.lstrip(" "))


def contents(lines):
    """Per line: its text without the markers and the indentation of its block quotes and list items, or None
    inside an HTML comment (CommonMark 5.1, 5.2, 4.6, adopted in part)."""
    out, cols, in_html, fence = [], [], False, None  # fence: the close pattern of the open fenced block
    for raw in lines:
        if fence:
            line = raw
            while QUOTE.match(line):
                line = QUOTE.sub("", line, count=1)
            base = cols[-1] if cols else 0
            out.append(line[base:] if leading(line) >= base else line.lstrip(" "))
            fence = None if fence.match(out[-1]) else fence  # inside it, no HTML comment and no list item
            continue
        if in_html:
            out.append(None)
            in_html = "-->" not in raw
            continue
        line = raw
        while QUOTE.match(line):
            line = QUOTE.sub("", line, count=1)
        if re.match(r"^ {0,3}<!--", line):
            out.append(None)
            in_html = "-->" not in line.split("<!--", 1)[1]
            continue
        if line.strip():
            while cols and leading(line) < cols[-1]:
                if LIST_ITEM.match(line[cols[-2]:] if len(cols) > 1 else line) and len(cols) > 1:
                    break
                cols.pop()
            base = cols[-1] if cols else 0
            m = LIST_ITEM.match(line[base:])
            if m:
                width = len(m.group(1)) + len(m.group(2)) + max(1, len(m.group(3)))
                cols.append(base + width)
                line = " " * (base + width) + line[base + m.end():]
        base = cols[-1] if cols else 0
        out.append(line[base:] if leading(line) >= base else line.lstrip(" "))
        m = FENCE_OPEN.match(out[-1])
        if m and len(m.group(1)) <= 3 and not (m.group(2)[0] == "`" and "`" in m.group(3)):
            fence = re.compile("^ {0,3}" + re.escape(m.group(2)[0]) + "{" + str(len(m.group(2))) + r",}[ \t]*$")
    return out


def blocks(text):
    """The fenced blocks of a Markdown text, then its indented code blocks (CommonMark 4.5, 4.4, adopted in part)."""
    lines = split_lines(text)
    body = contents(lines)
    out, i, n, para = [], 0, len(lines), False
    while i < n:
        line = body[i]
        if line is None:
            i, para = i + 1, False
            continue
        m = FENCE_OPEN.match(line)
        if m and len(m.group(1)) <= 3 and not (m.group(2)[0] == "`" and "`" in m.group(3)):
            indent, fence, info = len(m.group(1)), m.group(2), m.group(3).strip()
            close = re.compile("^ {0,3}" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}[ \t]*$")
            j, code = i + 1, []
            while j < n and body[j] is not None and not close.match(body[j]):
                code.append(strip_indent(body[j], indent))
                j += 1
            out.append(Block(i + 1, info, code))
            i, para = j + 1, False
            continue
        if not line.strip():
            i, para = i + 1, False
            continue
        if indented(line) and not para:
            j, code = i, []
            while j < n and body[j] is not None and (indented(body[j]) or not body[j].strip()):
                code.append(body[j][1:] if body[j].startswith("\t") else body[j][4:])
                j += 1
            while code and not code[-1].strip():
                code.pop()
            out.append(Block(i + 1, "", code, fenced=False))
            i, para = j, False
            continue
        para = not ATX.match(line)
        i += 1
    out.sort(key=lambda b: (not b.fenced, b.line))
    return out


def indented(line):
    return line.startswith("    ") or line.startswith("\t")


def strip_indent(line, indent):
    k = 0
    while k < indent and k < len(line) and line[k] == " ":
        k += 1
    return line[k:]


def lex(code):
    """Per line of the code: (text outside comments, line comments, open brackets at its start)."""
    out, in_block, depth = [], False, 0
    for line in code:
        start_depth, kept, comments, k, n = depth, [], [], 0, len(line)
        while k < n:
            if in_block:
                end = line.find("*/", k)
                if end < 0:
                    k = n
                else:
                    in_block, k = False, end + 2
                continue
            c = line[k]
            if c == '"':
                j = k + 1
                while j < n and line[j] != '"':
                    j += 2 if line[j] == "\\" else 1
                kept.append(line[k:j + 1])
                k = j + 1
            elif line.startswith("//", k):
                comments.append(line[k:])
                k = n
            elif line.startswith("/*", k):
                in_block, k = True, k + 2
            else:
                if c in "([{":
                    depth += 1
                elif c in ")]}" and depth:
                    depth -= 1
                kept.append(c)
                k += 1
        out.append(("".join(kept), comments, start_depth))
    return out


def is_code_line(lexed):
    return bool(lexed[0].strip())


def is_section_line(raw, lexed):
    if not raw or raw[0] in " \t" or not is_code_line(lexed):
        return False
    head = lexed[0].rstrip()  # the comments of the line are left out
    return any(p.match(head) for p in SECTION_LINE)


def prefix(code):
    return re.match(r"[A-Z]+", code).group()


def parse_info(info):
    """(expect, code, line) of a Clean example, or None when its info string is no form of CEX-4."""
    if INFO_VALID.fullmatch(info):
        return ("valid", None, None)
    m = INFO_SYNTAX.fullmatch(info)
    if m:
        return ("syntax-error", m.group(1), int(m.group(2)))
    m = INFO_ERROR.fullmatch(info)
    if m:
        return ("error", m.group(1), None)
    return None


def check_block(block, codes):
    """The violations of one fenced block: [(line of the file, rule ID)]. codes is None to skip CEX-16, CEX-17."""
    if block.is_old():
        return [(block.line, "CEX-2")]
    if not block.is_example():
        return []
    found, parsed = [], parse_info(block.info)
    if parsed is None:
        found.append((block.line, "CEX-4"))
    else:
        expect, code, line = parsed
        if expect == "syntax-error" and (prefix(code) != "SYN" or not 1 <= line <= len(block.code)):
            found.append((block.line, "CEX-6"))
        if expect == "error" and prefix(code) == "SYN":
            found.append((block.line, "CEX-7"))
        if code and codes is not None:
            defined, retired = codes
            if code not in defined:
                found.append((block.line, "CEX-16"))
            if code in retired:
                found.append((block.line, "CEX-17"))
    lexed = lex(block.code)
    sy003 = parsed is not None and parsed[0] == "syntax-error" and parsed[1] == "SYN003"
    for k, (raw, lx) in enumerate(zip(block.code, lexed)):
        at = block.line + 1 + k
        if any(FAILS.match(c) for c in lx[1]):
            found.append((at, "CEX-9"))
        if parsed is not None and parsed[0] != "syntax-error" and raw and raw[0] not in " \t" \
                and is_code_line(lx) and not is_section_line(raw, lx):
            found.append((at, "CEX-10"))
        if FILE_LINE.match(raw) and k != 0:
            found.append((at, "CEX-11"))
        if is_code_line(lx) and not sy003 and lx[2] == 0:
            lead = raw[: len(raw) - len(raw.lstrip(" \t"))]
            if " " in lead:
                found.append((at, "CEX-13"))
    return found


def is_suspect(block):
    """CAU-6."""
    if block.is_example() or block.is_old():
        return False
    lexed = lex(block.code)
    for k in range(len(block.code) - 1):
        nxt = block.code[k + 1]
        if is_section_line(block.code[k], lexed[k]) and nxt[:1] in (" ", "\t") and nxt.strip():
            return True
    return False


# ---------------------------------------------------------------- repositories


def git(repo, *args):
    r = subprocess.run(["git", "-C", repo] + list(args), capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def toplevel(path):
    d = path if os.path.isdir(path) else os.path.dirname(path) or "."
    out = git(d, "rev-parse", "--show-toplevel")
    return out.strip() if out else None


def remote_name(repo):
    url = (git(repo, "remote", "get-url", "origin") or "").strip()
    m = re.search(r"[/:]([^/:]+)/([^/]+?)(\.git)?/?$", url)
    return f"{m.group(1)}/{m.group(2)}" if m else None


def where(repo):
    """(entry, other path, other entry) of a repository of layer 0 or 1, or (None, reason, None). Spec: CAU-4, ORC-21."""
    pj = os.path.join(repo, "project.json")
    if not os.path.isfile(pj):
        return None, "the repository has no project.json", None
    try:
        with open(pj, encoding="utf-8") as f:
            project = json.load(f)
    except (OSError, ValueError):
        return None, "the repository has no project.json", None
    name = remote_name(repo)
    entries = project.get("repositories", [])
    entry = next((e for e in entries if f"{e.get('owner')}/{e.get('name')}" == name), None)
    if entry is None:
        return None, "no entry of project.json matches the remote origin", None
    if entry.get("layer") not in (0, 1):
        return None, "the layer of the entry of project.json is not 0 or 1", None
    folder = repo[: -len(entry["path"])].rstrip("/") if repo.endswith(entry["path"]) else os.path.dirname(repo)
    other = next((e for e in entries if e.get("layer") == 1 - entry["layer"]), None)
    other_path = os.path.join(folder, other["path"]) if other else None
    return entry, other_path, other


def spec_files(repo):
    """Paths of the spec files of a repository, relative, in code point order."""
    out = git(repo, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
    if out is None:
        return []
    paths = sorted({p for p in out.split("\0") if p.endswith(".md")})
    return [p for p in paths if os.path.isfile(os.path.join(repo, p)) and not os.path.islink(os.path.join(repo, p))]


def read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def headings(text):
    """[(line, code)] of the definitions of a text, outside its fenced blocks and HTML comments."""
    lines = split_lines(text)
    body = contents(lines)
    fenced = set()
    for b in blocks(text):
        if b.fenced:
            fenced.update(range(b.line, b.line + len(b.code) + 2))
    out = []
    for k, line in enumerate(body, 1):
        m = DEFINITION.match(line) if line is not None else None
        if m and k not in fenced:
            out.append((k, m.group(1)))
    return out


def registry(text):
    """(codes of registry rows, retired codes) of the registry."""
    rows, retired, section = set(), set(), None
    for line in split_lines(text):
        if line.startswith("## "):
            section = "rows" if line.startswith("## 5. Code Index") else "retired" if line.startswith("## 6. Reserved Codes") else None
            continue
        if section and line.startswith("|"):
            cells = line.split("|")
            if len(cells) > 2:
                m = CODE_TOKEN.search(cells[1])
                if m:
                    (rows if section == "rows" else retired).add(m.group(1))
    return rows, retired


class Codes:
    """The definitions, registry rows and retired codes of both repositories. Spec: CEX-14 to CEX-18, CAU-7."""

    def __init__(self, repos, overrides=None, layer1=None):
        """repos: [(label, root)], label None for the working repository; layer1: the root of layer 1;
        overrides: {absolute path: text}."""
        layer1 = os.path.realpath(layer1) if layer1 else None
        overrides = overrides or {}
        self.definitions = []  # (label, path, line, code), in code point order of path then line
        self.rows, self.retired, self.has_registry = set(), set(), False
        for label, root in repos:
            root = os.path.realpath(root)
            paths = spec_files(root)
            for full in overrides:  # a file that does not exist yet
                p = os.path.relpath(full, root)
                if not p.startswith("..") and p.endswith(".md") and p not in paths:
                    paths.append(p)
            for p in sorted(paths):
                full = os.path.join(root, p)
                text = overrides.get(full)
                if text is None:
                    try:
                        text = read(full)
                    except OSError:
                        continue
                for line, code in headings(text):
                    self.definitions.append((label, p, line, code))
                if p == REGISTRY and root == layer1:
                    self.rows, self.retired = registry(text)
                    self.has_registry = True
        self.definitions.sort(key=lambda d: (d[1], d[2]))

    def defined(self):
        return {d[3] for d in self.definitions} | self.rows

    def violations(self):
        """[(label, path, line, rule)] of CEX-15 and CEX-18."""
        out, seen = [], set()
        for label, p, line, code in self.definitions:
            if code in seen:
                out.append((label, p, line, "CEX-15"))
            seen.add(code)
            if code in self.retired:
                out.append((label, p, line, "CEX-18"))
        return out


def new_blocks(before, after):
    """The fenced blocks of after that are new (CEX-23), counted with multiplicity."""
    old = Counter(b.key() for b in blocks(before) if b.fenced)
    out = []
    for b in blocks(after):
        if not b.fenced:
            continue
        if old[b.key()] > 0:
            old[b.key()] -= 1
        else:
            out.append(b)
    return out


def finding(prefix, path, line, rule):
    return f"- {prefix}{path}:{line} · {rule} · {MESSAGES[rule]}"
