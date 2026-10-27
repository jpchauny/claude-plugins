"""The repositories of layers 0 and 1 of a project, and the links between them.

Specs: specs/module.md, ORC-37 and the terms Path, Exists, Link, Absent link,
Plain link and Link target; project-management/specs/module.md, ORC-20 to
ORC-24; use-cases/audit/specs/audit.md, AUD-54 to AUD-59.

    locate(repo, origin)                 -> (layer, {0: path, 1: path})
    link_reports(layer, texts, trees)    -> [report], the cases of AUD-56

`locate` raises NotFound with the condition that holds, in the order of
AUD-59; each caller words it (move.find_repos for promote and demote, the
audit for its "Not audited" line). This module runs no command and writes
nothing: the caller gives the URL of the remote `origin` and the trees at
`HEAD`, so that each use case runs git its own way.
"""

import json
import posixpath
import re
from pathlib import Path

import mdlinks

SUFFIX = " (not specified yet)"
SCHEME = "absent:"


class NotFound(Exception):
    """A condition of ORC-21, ORC-22 or ORC-24 holds. `code` names it, in the order of AUD-59:
    form, not_listed, layer, no_layer (layer), missing (owner, name, path), differs."""

    def __init__(self, code, **info):
        super().__init__(code)
        self.code = code
        self.info = info


def owner_name(url):
    m = re.search(r"[:/]([^/:]+)/([^/]+?)(?:\.git)?/?$", url.strip())
    return f"{m.group(1)}/{m.group(2)}" if m else None


def valid_path(path):
    """ORC-20: relative to the project folder, its parts separated by `/`, none empty, `.` or `..`."""
    return isinstance(path, str) and all(part not in ("", ".", "..") for part in path.split("/"))


def locate(repo, origin, own_at_repo=False):
    """The layer of `repo` and the repositories of layers 0 and 1 (ORC-37, with ORC-21, ORC-22, ORC-24).

    `origin` is called, after project.json is read, for the URL of the remote `origin` of `repo`, or
    None when it has none; an exception it raises goes to the caller. With `own_at_repo`, the
    repository of the layer of `repo` is `repo` itself, and only the other layer is looked for at its
    `path` (AUD-59 condition 5)."""
    repo = Path(repo)
    try:
        own = (repo / "project.json").read_bytes()
        entries = json.loads(own)["repositories"]
        if not isinstance(entries, list) or not all(isinstance(e, dict) and valid_path(e.get("path"))
                                                    for e in entries):
            raise TypeError
    except (OSError, ValueError, KeyError, TypeError, RecursionError):
        raise NotFound("form")
    url = origin()
    me = owner_name(url) if url is not None else None
    mine = [e for e in entries if f"{e.get('owner')}/{e.get('name')}" == me]
    if not mine:
        raise NotFound("not_listed")
    # `type(...) is int`: JSON true is not layer 1.
    layer = mine[0].get("layer")
    if type(layer) is not int or layer not in (0, 1):
        raise NotFound("layer")
    chosen = {}
    for n in (0, 1):
        e = next((e for e in entries if type(e.get("layer")) is int and e.get("layer") == n), None)
        if e is None:
            raise NotFound("no_layer", layer=n)
        chosen[n] = e
    # ORC-21: the project folder is the folder of the repository without its `path`.
    folder = repo
    for _ in mine[0]["path"].split("/"):
        folder = folder.parent
    found = {}
    for n in (0, 1):
        e = chosen[n]
        if own_at_repo and n == layer:
            found[n] = repo
            continue
        path = folder / e["path"]
        try:
            path = path.resolve()
            there = (path / ".git").exists()
        # A folder on the way that cannot be searched, a NUL in the path, a symlink loop (Python 3.9).
        except (OSError, ValueError, RuntimeError):
            there = False
        if not there:
            raise NotFound("missing", owner=e.get("owner"), name=e.get("name"), path=path)
        found[n] = path
    try:
        same = (found[1] / "project.json").read_bytes() == own
    except (OSError, ValueError, RuntimeError):
        same = False
    if not same:
        raise NotFound("differs")
    return layer, found


# ---------------------------------------------------------------- links (terms Link, Absent link, Link target)

def has_scheme(dest):
    return re.match(r"^[A-Za-z][A-Za-z0-9+.-]{1,31}:", dest) is not None


def link_target(file, dest_path):
    """The link target of a destination path, or None when it resolves outside the repository."""
    joined = posixpath.normpath(posixpath.join(posixpath.dirname(file), dest_path))
    if joined == ".." or joined.startswith("../") or joined.startswith("/"):
        return None
    return "" if joined == "." else joined.rstrip("/")


def tree_paths(paths):
    """Term Exists: every path of a tree at HEAD, and every folder that holds one of them."""
    found = set()
    for p in paths:
        while p and p not in found:
            found.add(p)
            p = posixpath.dirname(p)
    if found:
        found.add("")  # the root holds a file
    return found


def layer_links(file, text):
    """(link, absent, target) of each link of `text` that has a link target, the destination taken as
    the file holds it, without its angle brackets, no escape or percent-encoding decoded (AUD-56)."""
    res = []
    for l in mdlinks.find_links(text):
        dest = text[l["dest_start"]:l["dest_end"]]
        if l["angle"]:
            dest = dest[1:-1]
        label = text[l["open"] + 1:l["close"]]
        absent = dest.startswith(SCHEME)
        if absent and not label.endswith(SUFFIX):
            continue  # neither an absent link nor a plain link
        if not dest or dest.startswith(("/", "#")) or (has_scheme(dest) and not absent):
            continue  # term Link: not a link
        path = (dest[len(SCHEME):] if absent else dest).partition("#")[0]
        target = link_target(file, path) if path else None
        if target is not None:
            res.append((l, absent, target))
    return res


def plain_link(text, l):
    """ORC-41: the absent link `l` as a plain link: ` (not specified yet)` off the end of its text and
    `absent:` off the start of its destination, nothing else."""
    dest = l["dest_start"] + (1 if l["angle"] else 0)
    return (text[l["open"]:l["close"] - len(SUFFIX)] + text[l["close"]:dest]
            + text[dest + len(SCHEME):l["end"]])


def link_reports(layer, texts, trees):
    """AUD-56: the links to report, in the files `texts` ({path: text}) of the repository of `layer`,
    given `trees` ({0: paths, 1: paths} from tree_paths). Each report: path, line, open, end, case and,
    for case 1, plain."""
    reports = []
    for path, text in texts.items():
        for l, absent, target in layer_links(path, text):
            in0, in1 = target in trees[0], target in trees[1]
            case = None
            if layer == 1 and absent:
                case = 1 if in1 else 2 if not in0 else None
            elif layer == 0 and not absent and not in0 and not in1:
                case = 3
            if case is None:
                continue
            # Term Line of audit.md: lines end at each LF only.
            r = dict(path=path, line=text.count("\n", 0, l["open"]) + 1, open=l["open"], end=l["end"], case=case)
            if case == 1:
                r["plain"] = plain_link(text, l)
            reports.append(r)
    return reports
