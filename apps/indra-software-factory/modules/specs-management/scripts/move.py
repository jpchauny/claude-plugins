"""Move specs between layers 0 and 1: the shared part of promote and demote.

Spec: specs/module.md, section "Move specs between layers 0 and 1" (ORC-35 to
ORC-48); use-cases/promote/specs/promote.md and use-cases/demote/specs/demote.md.

Usage (python3 -I, from any folder):

    move.py plan     <use case> <repo> [--part K] -- <path>...
    move.py apply    <use case> <repo> <side> --fingerprint F -- <path>...
    move.py rollback <use case> <repo> <side> -- <path>...

<use case> is promote or demote; <repo> is the root of the repository the
session runs in; <side> is target or source.

- `plan` writes nothing. It prints one JSON object: `display`, the text of
  ORC-42 in parts of at most 20000 characters, `parts`, `resume`, and the
  `fingerprints` of each side. On a refusal it prints the lines of ORC-48 and
  exits 1.
- `apply` plans again and, when the side's fingerprint is unchanged, writes and
  stages that side only, and prints the commit command of ORC-43, the paths it
  wrote and `head`, the commit the side was at. Exit 3: something changed since
  the plan, nothing written. Exit 1: git failed; what it wrote is given back.
- `rollback` gives back the bytes `apply` changed on one side (ORC-44).

The commits and pushes are git commands that the session runs, so that each one
asks the person (LAY-2).
"""

import difflib
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import layers  # noqa: E402
import mdlinks  # noqa: E402
from layers import has_scheme, link_target, owner_name  # noqa: E402,F401

PART = 20000
SUFFIX = " (not specified yet)"
SCHEME = "absent:"
SUBJECTS = {
    "promote": ("docs: promote specs from layer 0", "docs: promote specs to layer 1"),
    "demote": ("docs: demote specs from layer 1", "docs: demote specs to layer 0"),
}
LAYER = {0: "layer 0", 1: "layer 1"}


class Refused(Exception):
    def __init__(self, lines):
        super().__init__("\n".join(lines))
        self.lines = lines


# ---------------------------------------------------------------- git

def git(repo, *args, check=True, data=None):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", LC_ALL="C")
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, input=data, env=env)
    if check and p.returncode:
        err = p.stderr.decode("utf-8", "replace").strip().splitlines()
        raise RuntimeError(err[0] if err else f"git {args[0]} failed")
    return p


def head_files(repo):
    """Path -> (mode, object id) of every entry in the tree of HEAD."""
    out = git(repo, "ls-tree", "-r", "-z", "--full-tree", "HEAD").stdout
    files = {}
    for rec in out.split(b"\0"):
        if rec:
            meta, path = rec.split(b"\t", 1)
            mode, _, oid = meta.split(b" ")
            files[path.decode("utf-8", "surrogateescape")] = (mode.decode(), oid.decode())
    return files


def blobs(repo, ids):
    """Blob id -> bytes, in one git cat-file call."""
    ids = sorted(set(ids))
    if not ids:
        return {}
    out = git(repo, "cat-file", "--batch", data="".join(i + "\n" for i in ids).encode()).stdout
    res, pos = {}, 0
    for i in ids:
        nl = out.index(b"\n", pos)
        size = int(out[pos:nl].split(b" ")[2])
        res[i] = out[nl + 1:nl + 1 + size]
        pos = nl + 1 + size + 1
    return res


def default_branch(repo):
    p = git(repo, "symbolic-ref", "--short", "refs/remotes/origin/HEAD", check=False)
    return p.stdout.decode().strip().removeprefix("origin/") if p.returncode == 0 else "main"


def rev(repo, ref):
    return git(repo, "rev-parse", "--verify", "-q", ref, check=False).stdout.decode().strip()


# ---------------------------------------------------------------- repositories (ORC-37)

def find_repos(repo, uc):
    """Return {0: path, 1: path}, the repositories of layers 0 and 1, as ORC-21, ORC-22 and ORC-24 say."""
    def origin():
        p = git(repo, "remote", "get-url", "origin", check=False)
        return p.stdout.decode() if p.returncode == 0 else None

    try:
        return layers.locate(repo, origin)[1]
    except layers.NotFound as e:
        i = e.info
        line = {
            "form": "project.json is missing or does not have the form of ORC-20",
            "not_listed": "this repository is not in project.json",
            "layer": "runs only from the repository of layer 0 or of layer 1",
            "no_layer": f"project.json has no repository of layer {i.get('layer')}",
            "missing": f"{i.get('owner')}/{i.get('name')} is not at {i.get('path')}; "
                       f"clone it: git clone https://github.com/{i.get('owner')}/{i.get('name')} {i.get('path')}",
            "differs": "project.json differs from the copy of layer 1; run /project-management:sync",
        }[e.code]
        raise Refused([f"specs-management:{uc}: {line}"])


# ---------------------------------------------------------------- links (terms Link, Absent link, Link target)

def decode(data):
    return data.decode("utf-8", "surrogateescape")


def encode(text):
    return text.encode("utf-8", "surrogateescape")


def text_lines(data):
    """The lines of `data` as git splits them, at each "\\n" only, each with its line end."""
    return re.findall(r"[^\n]*\n|[^\n]+$", decode(data))


def diff_lines(lines):
    """The lines of a unified diff, each with its line end; a line that had none is followed by
    git's marker, so that it never runs into the next line of the diff."""
    for line in lines:
        yield line if line.endswith("\n") else line + "\n\\ No newline at end of file\n"


def split_dest(raw, angle):
    """(path, simple) of a raw destination; simple is False where ORC-39 condition 6 forbids rewriting it."""
    s = raw[1:-1] if angle else raw
    escaped = re.search(r"\\[!-/:-@\[-`{-~]", s) is not None
    encoded = re.search(r"%[0-9A-Fa-f]{2}", s) is not None
    return s.partition("#")[0], not (angle or escaped or encoded)


def links(file, text):
    """Every link of a .md file, as a dict: line, open, close, dest_start, absent, target, simple."""
    found = []
    for l in mdlinks.find_links(text):
        raw = text[l["dest_start"]:l["dest_end"]]
        label = text[l["open"] + 1:l["close"]]
        absent = not l["angle"] and raw.startswith(SCHEME)
        if absent and not label.endswith(SUFFIX):
            continue  # a destination with the scheme absent: but not an absent link
        path, simple = split_dest(raw[len(SCHEME):] if absent else raw, l["angle"])
        if not path or path.startswith("/") or (has_scheme(path) and not absent):
            continue
        target = link_target(file, path)
        if target is None:
            continue
        found.append(dict(line=l["line"], open=l["open"], close=l["close"], dest_start=l["dest_start"],
                          absent=absent, target=target, simple=simple and not l["title"]))
    return found


def refdefs(file, text):
    """(line, link target) of each reference-style link definition of a .md file."""
    res = []
    for d in mdlinks.find_refdefs(text):
        path, _ = split_dest(text[d["dest_start"]:d["dest_end"]], d["angle"])
        if path and not path.startswith("/") and not has_scheme(path):
            t = link_target(file, path)
            if t is not None:
                res.append((d["line"], t))
    return res


def rewrite(file, data, rule):
    """Apply `rule(link) -> 'mark' | 'unmark' | None` to the links of a file (ORC-36, ORC-41).

    Return the new bytes and the links that changed."""
    text = decode(data)
    changed = [(l, act) for l in links(file, text) for act in [rule(l)] if act]
    for l, act in sorted(changed, key=lambda x: -x[0]["open"]):
        d, c = l["dest_start"], l["close"]
        if act == "mark":
            text = text[:d] + SCHEME + text[d:]
            text = text[:c] + SUFFIX + text[c:]
        else:
            text = text[:d] + text[d + len(SCHEME):]
            text = text[:c - len(SUFFIX)] + text[c:]
    return encode(text), changed


def exists(tree, target):
    """Term Exists: a file, or a folder that holds a file, of the tree."""
    if target == "":
        return bool(tree)
    prefix = target + "/"
    return target in tree or any(p.startswith(prefix) for p in tree)


# ---------------------------------------------------------------- plan

def make_plan(uc, repo, paths):
    repos = find_repos(repo, uc)
    sl, tl = (0, 1) if uc == "promote" else (1, 0)
    src, tgt = repos[sl], repos[tl]
    errs = []  # (condition, path, line, message)

    def say(cond, text, path="", line=0):
        errs.append((cond, path, line, f"specs-management:{uc}: {text}"))

    trees = {0: head_files(repos[0]), 1: head_files(repos[1])}
    st, tt = trees[sl], trees[tl]

    # Conditions 1 and 2: the paths (ORC-38).
    moved = set()
    if not paths:
        say(1, "expected at least one path")
    for p in paths:
        if not p or p.startswith("/") or any(x in (".", "..") for x in p.split("/")) or not p.strip("/"):
            say(1, f"{p}: invalid path", p)
            continue
        q = p.rstrip("/")
        hit = {f for f in st if f == q or f.startswith(q + "/")}
        if not hit:
            say(2, f"{p}: not in {LAYER[sl]}", p)
        moved |= hit
    moved = sorted(moved)
    moved_set = set(moved)

    # Condition 3: only regular files move.
    for m in moved:
        if st[m][0] in ("120000", "160000"):
            say(3, f"{m}: a symbolic link or a submodule", m)
    files = [m for m in moved if st[m][0] not in ("120000", "160000")]

    # Resume (ORC-45): every moved file is already in the target, and still in the source.
    resume = bool(moved) and all(m in tt for m in moved)

    before = {0: set(trees[0]), 1: set(trees[1])}
    if resume:
        before[tl] -= moved_set
    after = {sl: before[sl] - moved_set, tl: before[tl] | moved_set}

    # Condition 4: the target has nothing at a moved path, ignoring case.
    if not resume:
        untracked = git(tgt, "ls-files", "-z", "--others", "--exclude-standard").stdout
        known = {p.lower() for p in tt} | {decode(u).lower() for u in untracked.split(b"\0") if u}
        for m in moved:
            parts = m.split("/")
            folder_file = any("/".join(parts[:k]).lower() in known for k in range(1, len(parts)))
            if m.lower() in known or os.path.lexists(tgt / m) or folder_file:
                say(4, f"{m}: already in {LAYER[tl]}", m)

    # The bytes of layer 1's .md files and of the moved files.
    md1 = [p for p in trees[1] if p.endswith(".md") and trees[1][p][0] not in ("120000", "160000")]
    content1 = blobs(repos[1], {trees[1][p][1] for p in md1})
    content_src = blobs(src, {st[m][1] for m in files})

    # The links to rewrite (ORC-40).
    writes = {0: {}, 1: {}}
    unsafe = set()

    def keep(f, data, rule, layer):
        new, ch = rewrite(f, data, rule) if f.endswith(".md") else (data, [])
        unsafe.update((f, l["line"]) for l, _ in ch if not l["simple"])
        writes[layer][f] = new
        return ch

    if uc == "promote":
        for m in files:
            keep(m, content_src[st[m][1]], lambda l: "mark" if not l["absent"] and not exists(after[1], l["target"])
                 and exists(after[0], l["target"]) else None, 1)
        for f in md1:
            if f not in moved_set:
                if not keep(f, content1[trees[1][f][1]], lambda l: "unmark" if l["absent"]
                            and not exists(before[1], l["target"]) and exists(after[1], l["target"]) else None, 1):
                    del writes[1][f]
    else:
        for m in files:
            keep(m, content_src[st[m][1]], lambda l: "unmark" if l["absent"] and exists(after[0], l["target"]) else None, 0)
        for f in md1:
            if f not in moved_set:
                if not keep(f, content1[trees[1][f][1]], lambda l: "mark" if not l["absent"]
                            and exists(before[1], l["target"]) and not exists(after[1], l["target"]) else None, 1):
                    del writes[1][f]

    # Condition 6, second part: reference-style links of layer 1 left with no target.
    for f in md1:
        if f not in moved_set:
            for n, t in refdefs(f, decode(content1[trees[1][f][1]])):
                if exists(before[1], t) and not exists(after[1], t):
                    unsafe.add((f, n))
    if uc == "promote":
        for m in files:
            if m.endswith(".md"):
                for n, t in refdefs(m, decode(content_src[st[m][1]])):
                    if not exists(after[1], t) and exists(after[0], t):
                        unsafe.add((m, n))
    for f, n in unsafe:
        say(6, f"{f}:{n}: link cannot be rewritten", f, n)

    # Condition 5: uncommitted changes in the files to move or to rewrite.
    touched = {sl: set(files), tl: set()}
    for layer in (0, 1):
        if not (resume and layer == tl):
            touched[layer] |= {f for f in writes[layer] if f in trees[layer]}
    for layer in (0, 1):
        if touched[layer]:
            out = git(repos[layer], "status", "--porcelain", "-z", "--untracked-files=no", "--",
                      *sorted(touched[layer])).stdout
            for rec in decode(out).split("\0"):
                if len(rec) > 3 and rec[3:] in touched[layer]:
                    say(5, f"{rec[3:]}: uncommitted changes in {LAYER[layer]}", rec[3:])

    # Conditions 7 and 8: the default branch, at the commit of origin.
    branches, heads = {}, {}
    for layer in (0, 1):
        r = repos[layer]
        b = branches[layer] = default_branch(r)
        if git(r, "rev-parse", "--abbrev-ref", "HEAD").stdout.decode().strip() != b:
            say(7, f"{LAYER[layer]}: not on its default branch {b}", LAYER[layer])
        fetched = git(r, "fetch", "-q", "origin", check=False)
        if fetched.returncode:
            err = fetched.stderr.decode("utf-8", "replace").strip().splitlines()
            raise RuntimeError(f"{LAYER[layer]}: {err[0] if err else 'git fetch failed'}")
        heads[layer] = rev(r, "HEAD")
        if rev(r, f"refs/heads/{b}") != rev(r, f"refs/remotes/origin/{b}"):
            say(8, f"{LAYER[layer]}: not at origin/{b}", LAYER[layer])

    # On a resume, the target must hold the bytes the move would write.
    if resume:
        tb = blobs(tgt, {tt[m][1] for m in files})
        for m in files:
            if tb[tt[m][1]] != writes[tl][m]:
                say(4, f"{m}: already in {LAYER[tl]}", m)

    if errs:
        errs.sort(key=lambda e: (e[0], e[1], e[2]))
        raise Refused([e[3] for e in errs])

    # ORC-42 item 4: untracked files of layer 1 that link to a moved file.
    loose = []
    for u in git(repos[1], "ls-files", "-z", "--others", "--exclude-standard", "--", "*.md").stdout.split(b"\0"):
        if u:
            u = decode(u)
            try:
                text = decode((repos[1] / u).read_bytes())
            except OSError:
                continue
            if any(exists(moved_set, l["target"]) for l in links(u, text)):
                loose.append(u)

    subjects = SUBJECTS[uc]
    message = {tl: subjects[0], sl: subjects[1]}
    side_paths = {tl: [] if resume else sorted(writes[tl]), sl: sorted(moved_set | set(writes[sl]))}

    def command(layer):
        r = shlex.quote(str(repos[layer]))
        ps = " ".join(shlex.quote(p) for p in side_paths[layer])
        # --literal-pathspecs: a path with `*`, `?` or `[` names that file only, never another (ORC-69).
        g = f"git --literal-pathspecs -C {r}"
        return (f"{g} commit -q -m {shlex.quote(message[layer])} -m {shlex.quote(chr(10).join(moved))}"
                f" -- {ps} && git -C {r} push -q origin HEAD:{branches[layer]}")

    def fingerprint(layer, *extra):
        data = [uc, moved, heads[layer], side_paths[layer], sorted((p, v.hex()) for p, v in writes[layer].items()), *extra]
        return hashlib.sha256(json.dumps(data).encode()).hexdigest()

    fp_source = fingerprint(sl)
    fp_target = fingerprint(tl, fp_source, heads[sl], sorted(loose))
    display = render(uc, moved, writes, sl, tl, trees, content1, content_src, st, loose, message, resume)
    return dict(use_case=uc, resume=resume, moved=moved, sides={"source": sl, "target": tl},
                repos={"source": str(src), "target": str(tgt)}, heads={"source": heads[sl], "target": heads[tl]},
                paths={"source": side_paths[sl], "target": side_paths[tl]},
                commands={"source": command(sl), "target": None if resume else command(tl)},
                fingerprints={"source": fp_source, "target": None if resume else fp_target},
                writes={"source": writes[sl], "target": {} if resume else writes[tl]}), display


def render(uc, moved, writes, sl, tl, trees, content1, content_src, st, loose, message, resume):
    """The display of ORC-42."""
    out = [f"{'Promote' if uc == 'promote' else 'Demote'}: {LAYER[sl]} -> {LAYER[tl]}"
           + (" (resume: the target is already committed and pushed)" if resume else ""), "", "Moved files:"]
    out += [f"  {m}" for m in moved]
    diffs = []
    for layer in (tl, sl):
        for p in sorted(writes[layer]):
            old = content_src[st[p][1]] if p in st and p in moved else content1[trees[1][p][1]]
            if writes[layer][p] != old:
                a = text_lines(old)
                b = text_lines(writes[layer][p])
                diffs.append("".join(diff_lines(difflib.unified_diff(a, b, f"a/{p}", f"b/{p}", n=0))))
    out += ["", "Rewritten links:" if diffs else "Rewritten links: none"] + diffs
    if loose:
        out += ["", "Untracked files of layer 1 that link to a moved file:"]
        out += [f"  {u} (untracked, not rewritten)" for u in loose]
    out += ["", "Commits:"]
    for layer in ([] if resume else [tl]) + [sl]:
        out += [f"  {LAYER[layer]}:", f"    {message[layer]}", ""] + [f"    {m}" for m in moved] + [""]
    return "\n".join(out).rstrip("\n")


# ---------------------------------------------------------------- apply and rollback

def write_side(plan, side):
    # --literal-pathspecs: a path with `*`, `?` or `[` names that file only, never another (ORC-69).
    r = Path(plan["repos"][side])
    writes = plan["writes"][side]
    if side == "target":
        for p, data in writes.items():
            (r / p).parent.mkdir(parents=True, exist_ok=True)
            (r / p).write_bytes(data)
        if plan["paths"]["target"]:
            git(r, "--literal-pathspecs", "add", "--", *plan["paths"]["target"])
    else:
        git(r, "--literal-pathspecs", "rm", "-q", "--", *plan["moved"])
        rest = [p for p in writes if p not in plan["moved"]]
        for p in rest:
            (r / p).write_bytes(writes[p])
        if rest:
            git(r, "--literal-pathspecs", "add", "--", *rest)


def rollback(repo, paths):
    """Give back to one repository the bytes its paths have at HEAD; delete those not at HEAD (ORC-44)."""
    head = head_files(repo)
    created = [p for p in paths if p not in head]
    kept = [p for p in paths if p in head]
    if created:
        unstaged = git(repo, "--literal-pathspecs", "rm", "-q", "--cached", "--ignore-unmatch", "--", *created, check=False)
        for p in created:
            f = repo / p
            if f.is_file() or f.is_symlink():
                f.unlink()
            d = f.parent
            while d != repo and d.is_dir() and not any(d.iterdir()):
                d.rmdir()
                d = d.parent
        if unstaged.returncode:
            err = unstaged.stderr.decode("utf-8", "replace").strip().splitlines()
            raise RuntimeError(err[0] if err else "git rm failed")
    if kept:
        data = blobs(repo, {head[p][1] for p in kept})
        for p in kept:
            (repo / p).parent.mkdir(parents=True, exist_ok=True)
            (repo / p).write_bytes(data[head[p][1]])
        git(repo, "--literal-pathspecs", "add", "--", *kept)


# ---------------------------------------------------------------- main

def main(argv):
    if len(argv) < 3 or argv[0] not in ("plan", "apply", "rollback") or argv[1] not in SUBJECTS:
        print(__doc__, file=sys.stderr)
        return 2
    cmd, uc, repo = argv[0], argv[1], Path(argv[2]).resolve()
    rest = argv[3:]
    opts, paths = (rest[:rest.index("--")], rest[rest.index("--") + 1:]) if "--" in rest else (rest, [])
    side = opts[0] if opts and opts[0] in ("target", "source") else None
    part = int(opts[opts.index("--part") + 1]) if "--part" in opts else 1
    fp = opts[opts.index("--fingerprint") + 1] if "--fingerprint" in opts else None
    if cmd != "plan" and side is None or cmd == "apply" and fp is None:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        if cmd == "rollback":
            repos = find_repos(repo, uc)
            layer = {"promote": {"source": 0, "target": 1}, "demote": {"source": 1, "target": 0}}[uc][side]
            rollback(repos[layer], paths)
            return 0
        plan, display = make_plan(uc, repo, paths)
    except Refused as e:
        print("\n".join(e.lines))
        return 3 if cmd == "apply" else 1
    except RuntimeError as e:
        print(f"specs-management:{uc}: git failed: {e}")
        return 1
    if cmd == "plan":
        chunks = [display[i:i + PART] for i in range(0, len(display), PART)] or [""]
        if not 1 <= part <= len(chunks):
            print(f"the output has {len(chunks)} parts")
            return 2
        print(json.dumps(dict(part=part, parts=len(chunks), display=chunks[part - 1], resume=plan["resume"],
                              fingerprints=plan["fingerprints"]), indent=1))
        return 0
    if fp != plan["fingerprints"][side]:
        print("changed")
        return 3
    try:
        write_side(plan, side)
    except (RuntimeError, OSError) as e:
        print(f"specs-management:{uc}: git failed: {e}")
        try:
            rollback(Path(plan["repos"][side]), plan["paths"][side])
        except (RuntimeError, OSError) as e2:
            print(f"specs-management:{uc}: could not give back {plan['repos'][side]}: {e2}")
        return 1
    print(json.dumps(dict(command=plan["commands"][side], paths=plan["paths"][side], head=plan["heads"][side])))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
