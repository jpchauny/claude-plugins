"""The deterministic part of /specs-management:write.

Spec: use-cases/write/specs/write.md (ORC-59 to ORC-69). The repositories,
the links and the git helpers are those of scripts/move.py (ORC-37, term Link).

Usage (python3 -I, from any folder):

    write.py locate   <repo> [-- <path>]
    write.py check    <repo> -- <path>
    write.py scope    <repo> -- <path>
    write.py diff     <repo> <case> -- <path>
    write.py commit   <repo> <case> <layer> --fingerprint F -- <path>
    write.py links    <repo> -- <path>
    write.py delete   <repo> --fingerprint F -- <path>
    write.py rollback <repo> <layer> -- <path>

<repo> is the root of the repository the session runs in; <case> is new,
change-draft, change-spec or delete (ORC-60); <layer> is 0 or 1.

- `locate` writes nothing. It prints the case of ORC-60 as JSON, or the
  refusal of ORC-59 or ORC-60 and exits 1.
- `check` writes nothing. It prints the checks of ORC-65 as JSON.
- `scope` writes nothing. It prints the files of layers 0 and 1 that the full
  check of ORC-67 reads (consistency.js).
- `diff` writes nothing. It prints the whole diff of the change (ORC-66, and
  of both layers for a deletion, ORC-68), its commits and one fingerprint per
  layer.
- `commit` prints the command that commits and pushes one layer, when that
  layer's fingerprint is unchanged (exit 3 otherwise). It writes nothing: the
  session runs the command, so that the person approves it (LAY-2).
- `links` writes nothing. It prints the plan of a deletion (ORC-68): each link
  to the deleted path, the line before and after its deletion.
- `delete` deletes the draft from layer 0 and each link to it in both layers,
  when the fingerprint of `links` is unchanged (exit 3 otherwise).
- `rollback` gives back the bytes of HEAD to the files a deletion changed in
  one layer.

Refusals are lines `specs-management:write: ...`, exit 1.
"""

import difflib
import hashlib
import json
import os
import re
import shlex
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "scripts"))
import layers  # noqa: E402
import mdlinks  # noqa: E402
import move  # noqa: E402
from move import LAYER, Refused, blobs, decode, default_branch, encode, git, head_files, rev  # noqa: E402

UC = "write"
CASES = ("new", "change-draft", "change-spec", "delete")
# ORC-66 and ORC-68: the subjects of the commits, byte for byte.
SUBJECTS = {"new": "docs: add draft spec", "change-draft": "docs: change draft spec",
            "change-spec": "docs: change draft spec", "delete": "docs: delete spec"}
LINKS_SUBJECT = "docs: delete links to a deleted spec"
CASE_NAMES = {"new": "new draft spec", "change-draft": "change of a draft spec",
              "change-spec": "change of a spec", "delete": "deletion of a spec"}
SPECIAL = ("120000", "160000")  # a symbolic link, a submodule


def say(text):
    return f"specs-management:{UC}: {text}"


# ---------------------------------------------------------------- the path (ORC-60)

def valid(path):
    """ORC-38, which ORC-60 reuses for its invalid path; and the draft is a .md file."""
    return bool(path) and not path.startswith("/") and not any(x in (".", "..", "") for x in path.split("/")) \
        and path.endswith(".md")


def is_folder(tree, path):
    return any(p.startswith(path + "/") for p in tree)


def repos_and_trees(repo):
    repos = move.find_repos(repo, UC)
    return repos, {layer: head_files(repos[layer]) for layer in (0, 1)}


def layer_of(repo, repos):
    return 0 if repo.resolve() == repos[0] else 1


def check_path(path, trees):
    if not valid(path) or is_folder(trees[0], path) or is_folder(trees[1], path):
        raise Refused([say(f"{path}: invalid path")])


def locate(repo, path):
    repos, trees = repos_and_trees(repo)
    out = dict(layer=layer_of(repo, repos), repos={str(k): str(v) for k, v in repos.items()}, path=path,
               case=None, choices=[], in_both=False, on_disk=False)
    if path is None:
        out["case"] = CASE_NAMES["new"]
        return out
    check_path(path, trees)
    in0, in1 = path in trees[0], path in trees[1]
    out["in_both"] = in0 and in1
    out["on_disk"] = (repos[0] / path).is_file()
    if in1:
        # A path of layer 1 (also when a demote left it in both, ORC-45): change or delete, after its demote.
        out["choices"] = [CASE_NAMES["change-spec"], CASE_NAMES["delete"]]
    elif in0:
        out["case"] = CASE_NAMES["change-draft"]
    else:
        out["case"] = CASE_NAMES["new"]
    return out


# ---------------------------------------------------------------- the files of both layers

def md_files(repos, trees, draft=None):
    """(layer, path) -> text of every .md file at HEAD of layers 0 and 1; the draft from the working tree."""
    texts = {}
    for layer in (0, 1):
        tree = trees[layer]
        paths = [p for p in tree if p.endswith(".md") and tree[p][0] not in SPECIAL]
        data = blobs(repos[layer], {tree[p][1] for p in paths})
        for p in paths:
            texts[(layer, p)] = decode(data[tree[p][1]])
    if draft is not None:
        texts.pop((0, draft), None)
        try:
            texts[(0, draft)] = decode((repos[0] / draft).read_bytes())
        except OSError:
            pass
    return texts


def exists_anywhere(trees, target, draft):
    return target == draft or move.exists(trees[0], target) or move.exists(trees[1], target)


# ---------------------------------------------------------------- terms and statement IDs (ORC-65)

FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
ID = r"[A-Z][A-Z0-9]*-[A-Z]?[0-9]+"
# A statement that the file itself declares: a Gherkin rule, a bold ID at the start of an item, a heading.
DECLARED = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)?(?:Rule:\s*|\*\*|#{1,6}\s+)(" + ID + r")(?![A-Za-z0-9-])")


def lines_of(text):
    """The lines of a text as mdlinks numbers them: each ends at CR LF, LF or CR, and at nothing else."""
    lines = mdlinks.EOL.split(text)
    return lines[:-1] if lines[-1] == "" else lines


def prose_lines(text):
    """(line number, line) of each line outside a fenced code block."""
    fence = None
    for n, line in enumerate(lines_of(text), 1):
        m = FENCE.match(line)
        if fence:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) and not line.strip(" `~"):
                fence = None
            continue
        if m and not (m.group(1)[0] == "`" and "`" in line[m.end():]):
            fence = m.group(1)
            continue
        yield n, line


def cells(line):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", s)]


def plain(term):
    """A term as its table cell writes it, without bold, italics or code marks."""
    t = term.strip()
    while len(t) > 1 and t[0] == t[-1] and t[0] in "*_`":
        t = t[1:-1].strip()
    t = re.sub(r"^\*\*(.*)\*\*$", r"\1", t)
    return t.strip()


def terms(text):
    """(line, term) of each row of each table whose first header cell is "Term" (writing-specs.md, Terms)."""
    lines = list(prose_lines(text))
    found = []
    i = 0
    while i < len(lines):
        n, line = lines[i]
        if line.lstrip().startswith("|") and plain(cells(line)[0]).lower() == "term" and i + 1 < len(lines) \
                and re.match(r"^\s*\|?\s*:?-{3,}", lines[i + 1][1]):
            i += 2
            while i < len(lines) and lines[i][1].lstrip().startswith("|") and lines[i][0] == lines[i - 1][0] + 1:
                t = plain(cells(lines[i][1])[0])
                if t:
                    found.append((lines[i][0], t))
                i += 1
            continue
        i += 1
    return found


def declared_ids(text):
    """(line, ID) of each statement the file declares, fenced blocks included: Gherkin rules live in them."""
    return [(n, m.group(1)) for n, line in enumerate(lines_of(text), 1) for m in [DECLARED.match(line)] if m]


def check(repo, path):
    repos, trees = repos_and_trees(repo)
    check_path(path, trees)
    try:
        draft = decode((repos[0] / path).read_bytes())
    except OSError:
        raise Refused([say(f"{path}: not in layer 0")])
    texts = md_files(repos, trees, path)
    others = {k: v for k, v in texts.items() if k != (0, path)}
    neighbours = {}

    def near(layer, p, why):
        neighbours.setdefault((layer, p), set()).add(why)

    # Each link of the draft whose link target does not exist; each file it links to.
    broken = []
    for l in move.links(path, draft):
        t = l["target"]
        if not exists_anywhere(trees, t, path):
            broken.append(dict(line=l["line"], target=t, absent=l["absent"]))
        for layer in (0, 1):
            if t in trees[layer] and (layer, t) != (0, path):
                near(layer, t, "linked from the draft")
    # Each file that links to the draft.
    for (layer, p), text in sorted(others.items()):
        if any(l["target"] == path for l in move.links(p, text)):
            near(layer, p, "links to the draft")

    # Each term of the draft that another file also defines (SPC-3).
    defined = {}
    for (layer, p), text in sorted(others.items()):
        for n, t in terms(text):
            defined.setdefault(t.lower(), []).append(dict(layer=layer, path=p, line=n))
    term_rows = []
    for n, t in terms(draft):
        also = defined.get(t.lower(), [])
        if also:
            term_rows.append(dict(term=t, line=n, also=also))
            for a in also:
                near(a["layer"], a["path"], "defines a term of the draft")
    # Each file that holds a term of the draft in its prose (term Neighbour).
    for _, t in terms(draft):
        word = re.compile(r"(?<![A-Za-z0-9-])" + re.escape(t) + r"(?![A-Za-z0-9-])", re.I)
        for (layer, p), text in sorted(others.items()):
            if any(word.search(line) for _, line in prose_lines(text)):
                near(layer, p, "holds a term of the draft")

    # Each statement ID of the draft that another file also uses (SPC-14): first line per file.
    id_rows = []
    for n, i in declared_ids(draft):
        word = re.compile(r"(?<![A-Za-z0-9-])" + re.escape(i) + r"(?![A-Za-z0-9-])")
        also = []
        for (layer, p), text in sorted(others.items()):
            decl = {m for _, m in declared_ids(text)}
            for k, line in enumerate(lines_of(text), 1):
                if word.search(line):
                    also.append(dict(layer=layer, path=p, line=k, declared=i in decl))
                    break
        if also:
            id_rows.append(dict(id=i, line=n, also=also))

    return dict(draft=path, broken_links=broken, terms=term_rows, ids=id_rows,
                neighbours=[dict(layer=layer, path=p, why=sorted(w)) for (layer, p), w in
                            sorted(neighbours.items(), key=lambda x: (x[0][0], x[0][1].encode("utf-8", "surrogateescape")))])


def scope(repo, path):
    repos, trees = repos_and_trees(repo)
    check_path(path, trees)
    files = [dict(layer=layer, path=p) for (layer, p) in sorted(md_files(repos, trees))
             if (layer, p) != (0, path)]
    return dict(roots={"0": str(repos[0]), "1": str(repos[1])}, draft=path, files=files)


# ---------------------------------------------------------------- the deletion (ORC-68)

def link_spans(file, text, path):
    """(open, end, line) of each link of `file` whose link target is `path`, absent or plain, as move.links
    or as the audit (layers.layer_links) reads it: an absent link in angle brackets goes too (AUD-56)."""
    opens = {l["open"] for l in move.links(file, text) if l["target"] == path}
    opens |= {l["open"] for l, _, t in layers.layer_links(file, text) if t == path}
    return [(l["open"], l["end"], l["line"]) for l in mdlinks.find_links(text) if l["open"] in opens]


def cut(text, spans):
    for o, e, _ in sorted(spans, reverse=True):
        text = text[:o] + text[e:]
    return text


def deletion(repos, trees, path):
    """{layer: {file: new bytes}} and the lines of ORC-68, from the files at HEAD."""
    texts = md_files(repos, trees)
    writes, lines = {0: {}, 1: {}}, []
    for (layer, p), text in sorted(texts.items()):
        if (layer, p) == (0, path):
            continue
        spans = link_spans(p, text, path)
        if spans:
            new = cut(text, spans)
            writes[layer][p] = encode(new)
            old_lines, new_lines = lines_of(text), lines_of(new)
            # A link spans one line or more; report each line where one starts, as it is after the deletion.
            shift = 0
            for o, e, n in sorted(spans):
                gone = len(mdlinks.EOL.findall(text[o:e]))
                lines.append(dict(layer=layer, path=p, line=n, before=old_lines[n - 1],
                                  after=new_lines[n - 1 - shift] if n - 1 - shift < len(new_lines) else ""))
                shift += gone
    return writes, lines


def untracked_links(repos, path):
    """Each untracked .md file of either layer that links to the path: listed, never rewritten (ORC-69)."""
    found = []
    for layer in (0, 1):
        out = git(repos[layer], "ls-files", "-z", "--others", "--exclude-standard", "--", "*.md").stdout
        for u in out.split(b"\0"):
            if u:
                u = decode(u)
                try:
                    text = decode((repos[layer] / u).read_bytes())
                except OSError:
                    continue
                if link_spans(u, text, path):
                    found.append(dict(layer=layer, path=u))
    return found


def refdefs_to(repos, trees, path):
    """Reference-style definitions that point at the path: not links, never deleted; reported."""
    return [dict(layer=layer, path=p, line=n) for (layer, p), text in sorted(md_files(repos, trees).items())
            if (layer, p) != (0, path) for n, t in move.refdefs(p, text) if t == path]


def branches_ok(repos, layers, errs):
    """ORC-39 conditions 7 and 8, for the layers a commit of write touches."""
    branches = {}
    for layer in layers:
        r = repos[layer]
        b = branches[layer] = default_branch(r)
        if git(r, "rev-parse", "--abbrev-ref", "HEAD").stdout.decode().strip() != b:
            errs.append(say(f"{LAYER[layer]}: not on its default branch {b}"))
        fetched = git(r, "fetch", "-q", "origin", check=False)
        if fetched.returncode:
            err = fetched.stderr.decode("utf-8", "replace").strip().splitlines()
            raise RuntimeError(f"{LAYER[layer]}: {err[0] if err else 'git fetch failed'}")
        if rev(r, f"refs/heads/{b}") != rev(r, f"refs/remotes/origin/{b}"):
            errs.append(say(f"{LAYER[layer]}: not at origin/{b}"))
    return branches


def dirty(repos, layer, paths):
    """The paths of one layer that have uncommitted changes, staged or not (ORC-69)."""
    if not paths:
        return []
    out = git(repos[layer], "status", "--porcelain", "-z", "--untracked-files=no", "--", *sorted(paths)).stdout
    return sorted({decode(rec)[3:] for rec in out.split(b"\0") if len(rec) > 3} & set(paths))


def fingerprint(*data):
    return hashlib.sha256(json.dumps(data, default=lambda b: b.hex()).encode()).hexdigest()


def plan_deletion(repo, path):
    repos, trees = repos_and_trees(repo)
    check_path(path, trees)
    errs = []
    if path in trees[1]:
        errs.append(say(f"{path}: in layer 1; demote it first"))
    elif path not in trees[0]:
        errs.append(say(f"{path}: not in layer 0"))
    writes, lines = deletion(repos, trees, path)
    for layer in (0, 1):
        touched = set(writes[layer]) | ({path} if layer == 0 and path in trees[0] else set())
        for p in dirty(repos, layer, touched):
            errs.append(say(f"{p}: uncommitted changes in {LAYER[layer]}"))
    branches_ok(repos, (0, 1), errs)
    if errs:
        raise Refused(errs)
    heads = {layer: rev(repos[layer], "HEAD") for layer in (0, 1)}
    fp = fingerprint(path, heads[0], heads[1], sorted((layer, p, v) for layer in (0, 1) for p, v in writes[layer].items()))
    old = md_files(repos, trees)
    diffs = [unified(f"{p}", encode(old[(layer, p)]), writes[layer][p], LAYER[layer]) for layer in (0, 1)
             for p in sorted(writes[layer])]
    display = "\n".join([f"Delete: {path} from layer 0", "", "Deleted links:" if diffs else "Deleted links: none",
                         *diffs]).rstrip("\n")
    return dict(repos=repos, writes=writes, fingerprint=fp, lines=lines,
                untracked=untracked_links(repos, path), refdefs=refdefs_to(repos, trees, path), display=display)


def apply_deletion(plan, path):
    repos = plan["repos"]
    draft = repos[0] / path
    if draft.is_file():
        draft.unlink()
    for layer in (0, 1):
        for p, data in plan["writes"][layer].items():
            (repos[layer] / p).write_bytes(data)
    return {str(layer): sorted(plan["writes"][layer]) + ([path] if layer == 0 else []) for layer in (0, 1)}


# ---------------------------------------------------------------- the diff and the commits (ORC-66, ORC-68)

def unified(path, old, new, layer=None):
    a = move.text_lines(old)
    b = move.text_lines(new)
    head = f"{layer}: " if layer else ""
    text = "".join(move.diff_lines(difflib.unified_diff(a, b, f"a/{path}", f"b/{path}")))
    return (head + text) if text else ""


def change(repo, case, path):
    """Per layer: the files of the change, their bytes at HEAD and in the working tree, and the diff."""
    repos, trees = repos_and_trees(repo)
    check_path(path, trees)
    errs = []
    sides = {0: {}, 1: {}}  # layer -> {path: (old bytes or None, new bytes or None)}

    def head_bytes(layer, p):
        e = trees[layer].get(p)
        return blobs(repos[layer], [e[1]])[e[1]] if e else None

    def disk(layer, p):
        f = repos[layer] / p
        return f.read_bytes() if f.is_file() and not f.is_symlink() else None

    if path in trees[1]:
        # ORC-62, ORC-69: a spec of layer 1 is changed or deleted only after its demote.
        errs.append(say(f"{path}: in layer 1; demote it first"))
    elif case == "delete":
        # The files that hold a link to the path at HEAD; once layer 0 is committed, only layer 1 is left.
        writes, _ = deletion(repos, trees, path)
        if path in trees[0]:
            sides[0][path] = (head_bytes(0, path), disk(0, path))
        for layer in (0, 1):
            for p in writes[layer]:
                sides[layer][p] = (head_bytes(layer, p), disk(layer, p))
    else:
        if case == "new" and path in trees[0]:
            errs.append(say(f"{path}: already in layer 0"))
        elif case != "new" and path not in trees[0]:
            errs.append(say(f"{path}: not in layer 0"))
        new = disk(0, path)
        if new is None:
            errs.append(say(f"{path}: not written in layer 0"))
        sides[0][path] = (head_bytes(0, path), new)
    for layer in (0, 1):
        sides[layer] = {p: v for p, v in sides[layer].items() if v[0] != v[1]}
    if not errs and not sides[0] and not sides[1]:
        errs.append(say(f"{path}: nothing to commit"))
    layers = [layer for layer in (0, 1) if sides[layer]]
    # A deletion tests both layers, so that layer 1 never goes before a commit of layer 0 left unpushed.
    branches = branches_ok(repos, (0, 1) if case == "delete" else (0,), errs)
    if errs:
        raise Refused(errs)
    heads = {layer: rev(repos[layer], "HEAD") for layer in (0, 1)}
    message = {0: SUBJECTS[case], 1: LINKS_SUBJECT}

    def command(layer):
        r = shlex.quote(str(repos[layer]))
        ps = " ".join(shlex.quote(p) for p in sorted(sides[layer]))
        # --literal-pathspecs: a path with `*`, `?` or `[` names that file only, never another (ORC-69).
        g = f"git --literal-pathspecs -C {r}"
        return (f"{g} add -- {ps} && {g} commit -q -m {shlex.quote(message[layer])} -m {shlex.quote(path)}"
                f" -- {ps} && git -C {r} push -q origin HEAD:{branches[layer]}")

    out = [f"{CASE_NAMES[case][0].upper() + CASE_NAMES[case][1:]}: {path}", "", "Diff:"]
    for layer in layers:
        for p in sorted(sides[layer]):
            old, new = sides[layer][p]
            out.append(unified(p, old or b"", new or b"", LAYER[layer]) if new is not None else
                       f"{LAYER[layer]}: deleted {p}\n" + unified(p, old or b"", b""))
    out += ["", "Commits:"]
    for layer in layers:
        out += [f"  {LAYER[layer]}:", f"    {message[layer]}", "", f"    {path}", ""]
    fps = {str(layer): fingerprint(case, path, layer, heads[layer], sorted(sides[layer].items())) for layer in layers}
    return dict(layers=layers, display="\n".join(out).rstrip("\n"), fingerprints=fps,
                commands={str(layer): command(layer) for layer in layers},
                paths={str(layer): sorted(sides[layer]) for layer in layers},
                heads={str(layer): heads[layer] for layer in layers})


def rollback(repo, layer, path):
    """Give back the bytes of HEAD to the draft and to each file of one layer that links to it at HEAD."""
    repos, trees = repos_and_trees(repo)
    check_path(path, trees)
    writes, _ = deletion(repos, trees, path)
    paths = sorted(set(writes[layer]) | ({path} if layer == 0 and path in trees[0] else set()))
    if paths:
        move.rollback(repos[layer], paths)
    return paths


# ---------------------------------------------------------------- main

PART = 20000


def dumps(value, **kw):
    """JSON with each non-ASCII character as it is; a lone surrogate, a byte of a path or a text that
    is not UTF-8, keeps its \\u escape, so that print() never fails on it (as audit.py compact)."""
    text = json.dumps(value, ensure_ascii=False, **kw)
    return re.sub("[\ud800-\udfff]", lambda m: "\\u%04x" % ord(m.group(0)), text)


def main(argv):
    cmds = ("locate", "check", "scope", "diff", "commit", "links", "delete", "rollback")
    if len(argv) < 2 or argv[0] not in cmds:
        print(__doc__, file=sys.stderr)
        return 2
    cmd, repo = argv[0], Path(argv[1]).resolve()
    rest = argv[2:]
    opts, paths = (rest[:rest.index("--")], rest[rest.index("--") + 1:]) if "--" in rest else (rest, None)
    fp = opts[opts.index("--fingerprint") + 1] if "--fingerprint" in opts and opts.index("--fingerprint") + 1 < len(opts) else None
    try:
        part = int(opts[opts.index("--part") + 1]) if "--part" in opts else 1
    except (IndexError, ValueError):
        print(__doc__, file=sys.stderr)
        return 2
    pos = [o for i, o in enumerate(opts) if not o.startswith("--") and (i == 0 or opts[i - 1] not in ("--fingerprint", "--part"))]
    case = pos[0] if pos and cmd in ("diff", "commit") else None
    layer = pos[-1] if pos and cmd in ("commit", "rollback") else None
    if paths is not None and len(paths) > 1:
        try:
            move.find_repos(repo, UC)
        except Refused as e:
            print("\n".join(e.lines))
            return 1
        print(say("expected one path"))
        return 1
    path = paths[0] if paths else None
    bad = (cmd != "locate" and path is None
           or cmd in ("diff", "commit") and case not in CASES
           or cmd in ("commit", "rollback") and layer not in ("0", "1")
           or cmd in ("commit", "delete") and fp is None)
    if bad:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        if cmd == "locate":
            result = locate(repo, path)
        elif cmd == "check":
            result = check(repo, path)
        elif cmd == "scope":
            result = scope(repo, path)
        elif cmd in ("diff", "commit"):
            plan = change(repo, case, path)
            if cmd == "commit":
                if layer not in plan["fingerprints"] or plan["fingerprints"][layer] != fp:
                    print("changed")
                    return 3
                result = dict(command=plan["commands"][layer], paths=plan["paths"][layer], head=plan["heads"][layer])
            else:
                result = {k: plan[k] for k in ("layers", "display", "fingerprints")}
        elif cmd == "links":
            plan = plan_deletion(repo, path)
            result = {k: plan[k] for k in ("display", "fingerprint", "lines", "untracked", "refdefs")}
        elif cmd == "delete":
            plan = plan_deletion(repo, path)
            if plan["fingerprint"] != fp:
                print("changed")
                return 3
            result = dict(changed=apply_deletion(plan, path), lines=plan["lines"])
        else:
            result = dict(given_back=rollback(repo, int(layer), path))
    except Refused as e:
        print("\n".join(e.lines))
        return 1
    except (RuntimeError, OSError) as e:
        print(say(f"git failed: {e}"))
        return 1
    text = dumps(result, indent=1)
    if cmd in ("check", "scope", "diff", "links") and len(text) > PART:
        # Long outputs come in parts, so that the tool shows each whole: the display, or the JSON text.
        key = "display" if "display" in result else None
        whole = result[key] if key else text
        chunks = [whole[i:i + PART] for i in range(0, len(whole), PART)]
        if not 1 <= part <= len(chunks):
            print(f"the output has {len(chunks)} parts")
            return 2
        if key:
            result = dict(result, display=chunks[part - 1], part=part, parts=len(chunks))
            text = dumps(result, indent=1)
        else:
            text = dumps(dict(part=part, parts=len(chunks), text=chunks[part - 1]))
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
