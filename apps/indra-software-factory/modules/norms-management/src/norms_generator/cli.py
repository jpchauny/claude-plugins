"""Command line of the layer 2 generator: `norms-gen build | verify | report`.

    norms-gen build  --specs REPO [--commit SHA] [--out DIR]
    norms-gen verify --specs REPO [--out DIR]
    norms-gen report [--out DIR] [--json]

The specs are read through git, never from its working tree: every
regular file of the repository at the commit, in any folder, but the
excluded paths (excluded()), with its exact bytes, line endings included
(`git ls-tree`, `git cat-file blob`). Its `.md` files are annotated; every
other file is a plain copy, written byte for byte. Paths are relative
to the specs repository's root (`specs/language/type-system.md`),
the same every run, so that a path present in both keeps its prefix.

Output, under `--out` (default: the git repository of the working directory):

    data/tree.jsonl       the norms tree, the only source of truth for the
                          IDs and their history (the specs' is the content)
    data/report.md        what changed since the previous version, by ID
    data/report.json      the same, as JSON Lines
    specs-repo-annotated/<path>
                          each spec file with its IDs, and each plain
                          copy, at the same relative path: the folder tree
                          is kept

`build` refuses (exit status 2, nothing written) when the repository
holds no selected `.md` file at the commit, which the wrong repository
gives and which would retire every ID and prefix, when a file is not UTF-8
or holds a delimiter `⟬` or `⟭`, naming the file, when
a selected path holds a control character, when two paths or folders of
them differ only in case or Unicode normalization (check_paths),
and when the previous `data/tree.jsonl` cannot be read or is not
consistent: an ID stored twice, a prefix shared by two files, a retired
prefix in use, an active node of no file line, and when an
output path is in the way (check_outputs).

`build` matches the new trees against the previous `data/tree.jsonl`
(the empty store on a first run) and rewrites the outputs: the
copies first, after everything else under specs-repo-annotated/ is
removed, so that it holds exactly this build's copies and their folders,
then the JSONL, then the reports. Every output is written as a new file
(store.write_new), never into the file at its path, so a hard link there
never carries a write outside the output folder. It is deterministic: with
the same generator, a rebuild of the same commit
leaves every output byte for byte as it was, when both reports exist.
In particular, a rebuild of the commit the JSONL is already
pinned to, when it holds a file line, keeps the `to_review` and
`changed_since` flags of the unchanged nodes and the report of that
version, which describe the step from the previous version, not the
rebuild.

`verify` re-reads the specs at the commit pinned in the JSONL, checks
the JSONL itself (each ID stored once, file prefixes unique, no retired
prefix in use), runs verify.check_file() on every file, checks every
plain copy against the specs, and names every path under
specs-repo-annotated/ that is no copy of them, a copy with more than one
link, and a specs-repo-annotated/ that is a link or a file.
It exits with 1 when it finds a problem, a JSONL it cannot read
included, 0 otherwise.

`report` prints the last report.

Exit statuses, the same for every command: 0 success; 1 verify
found a problem, or report has no report to print; 2 a refusal of
build or a usage error, nothing written; 3 the system stopped build
part way (`cannot be written`), some outputs written; 4 an unexpected
error, worded `norms-gen: unexpected error: <type>: <message>` and
followed by the full stack trace. An interrupt (KeyboardInterrupt) keeps
Python's default behaviour. A reader that closes standard output early
(`norms-gen report | head`) ends the writing, not the command: no message,
and the status of what the command did.

Spec: R3, R19, R21, R23, R34, R53, R58, R60, R61, R62, R63, R64, U3, U6 (E20)
"""

from __future__ import annotations

import argparse
import hashlib
import io
import os
import shutil
import stat
import subprocess
import sys
import traceback
import unicodedata
from collections.abc import Sequence
from importlib import metadata
from pathlib import Path

from norms_generator.annotate import annotate
from norms_generator.model import Insertion, TreeNode
from norms_generator.prefixes import assign_prefixes
from norms_generator.store import (
    Change,
    Status,
    Store,
    StoredNode,
    StoreError,
    assign_ids,
    build_store,
    detect_renames,
    escape_controls,
    has_control,
    read_store,
    report_json,
    store_absent,
    report_markdown,
    write_new,
    write_store,
)
from norms_generator.tree import build_tree
from norms_generator.verify import check_file

STORE_PATH = Path("data/tree.jsonl")
STORE_TMP = Path("data/tree.jsonl.tmp")  # R62: where write_store writes it aside; Note: D45
REPORT_MD = Path("data/report.md")
REPORT_JSON = Path("data/report.json")
ANNOTATED = Path("specs-repo-annotated")

def default_out() -> Path:
    """The output folder when --out is not given: the root of the norms repository.

    The generator ships in a plugin, apart from the repository it builds, so
    the norms repository is the git repository of the working directory
    (`git rev-parse --show-toplevel`), or the working directory itself when
    it is in no git repository.

    Spec: R62
    """
    try:
        top = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return Path.cwd()
    return Path(top) if top else Path.cwd()

# R62: the exit statuses of every command.
EXIT_OK = 0
EXIT_PROBLEMS = 1  # R62, R64: verify found a problem, or report has no report to print
EXIT_REFUSED = 2  # R34: a refusal of build or a usage error (argparse's own status), nothing written
EXIT_STOPPED = 3  # R62: the system stopped build part way, some outputs written
EXIT_UNEXPECTED = 4  # R62: an error no requirement words, with its stack trace


def generator_version() -> str:
    """The version of the norms-generator package, stored in the JSONL header line.

    Spec: R61
    """
    try:
        return metadata.version("norms-generator")
    except metadata.PackageNotFoundError:  # pragma: no cover - not installed
        return "0"


# --- the specs through git -------------------------------------------------


class OutputError(RuntimeError):
    """Something in the output folder stands where build must write and is not the generator's to remove.

    Spec: R34, R62
    """


class BuildStopped(RuntimeError):
    """The system refused a read, a write or a removal while build wrote its outputs: exit status 3.

    Spec: R62
    """


class GitError(RuntimeError):
    """A git command on the specs repository failed.

    Spec: R34
    """


class SpecsError(RuntimeError):
    """The specs at the commit cannot be built: no Markdown file, or a file or path refused.

    Spec: R34
    """


def _git(repo: Path, *args: str) -> bytes:
    """Run git in `repo` and return its standard output.

    A failure is worded as the command without `git -C <path>`, then git's
    own message.

    Spec: R34
    """
    done = subprocess.run(["git", "-C", str(repo), *args], capture_output=True)
    if done.returncode != 0:
        message = done.stderr.decode("utf-8", "replace").strip()
        raise GitError(f"git {' '.join(args)}: {message}")
    return done.stdout


def resolve_commit(repo: Path, commit: str) -> str:
    """The full SHA of `commit` (HEAD, a branch, a short SHA, ...), as the header line stores it.

    `--quiet` makes git silent when the commit is unknown, so that case
    gets its own message.

    Spec: R34, R61
    """
    try:
        return _git(repo, "rev-parse", "--verify", "--quiet", f"{commit}^{{commit}}").decode().strip()
    except GitError as exc:
        if str(exc).endswith(": "):
            raise GitError(f"{commit!r} is not a commit of {repo}") from None
        raise


# R62: what is certainly not specification, in any project; the list is fixed
AGENT_FILES = frozenset(name.casefold() for name in ("CLAUDE.md", "CLAUDE.local.md", "AGENTS.md"))
ROOT_COMMUNITY_FILES = frozenset(
    name.casefold() for name in ("LICENSE.md", "CHANGELOG.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "SECURITY.md")
)


def excluded(path: str) -> bool:
    """Whether `path` is one of the excluded paths, which are certainly not specification.

    A folder or a file whose name starts with `.` (tool configuration), a
    `CLAUDE.md`, `CLAUDE.local.md` or `AGENTS.md` in any folder
    (instructions for agents), or a community file at the root. Names
    are compared after `str.casefold()`.

    Spec: R62
    """
    parts = path.split("/")
    if any(part.startswith(".") for part in parts):
        return True
    name = parts[-1].casefold()
    return name in AGENT_FILES or (len(parts) == 1 and name in ROOT_COMMUNITY_FILES)


def list_selected(repo: Path, commit: str) -> tuple[dict[str, str], dict[str, str]]:
    """path -> blob SHA of the selected files at `commit`: the `.md` files, and every other file.

    Every regular file of the repository (modes 100644 and 100755), in any
    folder, but the excluded paths; symbolic links and submodules are
    left out. A selected path that is not UTF-8, or that holds a control
    character, is refused (SpecsError); an excluded path is ignored,
    whatever it holds.

    Spec: R34, R62
    """
    out = _git(repo, "ls-tree", "-r", "-z", "--full-tree", commit)
    markdown: dict[str, str] = {}
    others: dict[str, str] = {}
    for entry in out.split(b"\0"):
        if not entry:
            continue
        info, path_bytes = entry.split(b"\t", 1)
        mode, kind, sha = info.decode().split()
        if not (kind == "blob" and mode in ("100644", "100755")):
            continue
        if excluded(path_bytes.decode("utf-8", errors="replace")):
            continue
        try:
            path = path_bytes.decode("utf-8")
        except UnicodeDecodeError:
            # R34: a path is cited in the JSONL, the report and specs-repo-annotated/;
            # its control characters escaped too: a line break would split the message
            name = escape_controls(path_bytes.decode("utf-8", errors="backslashreplace"))
            raise SpecsError(f"{name}: path not UTF-8") from None
        if has_control(path):  # R34: a line break would split a report heading or a message line
            raise SpecsError(f"{escape_controls(path)}: path holds a control character")
        (markdown if path.endswith(".md") else others)[path] = sha
    return dict(sorted(markdown.items())), dict(sorted(others.items()))


def _fold(path: str) -> str:
    """`path` as a file system that ignores case and Unicode normalization sees it (macOS, Windows).

    Spec: R34
    """
    return unicodedata.normalize("NFD", unicodedata.normalize("NFD", path).casefold())


def check_paths(paths: list[str]) -> None:
    """Raise SpecsError when two paths, or folders of them, differ only in case or normalization.

    Their copies would be one file, or one folder, on such a
    file system: one copy would overwrite the other, and the folder tree
    would not be kept.

    Spec: R34, R62 (E20)
    """
    files = set(paths)
    seen: dict[str, str] = {}
    for path in sorted(paths):
        parts = path.split("/")
        for n in range(1, len(parts) + 1):
            name = "/".join(parts[:n])
            first = seen.setdefault(_fold(name), name)
            if first != name:
                if first in files and name in files:
                    what = "their copies would be one file and overwrite each other"
                elif first in files or name in files:
                    what = "a copy and a folder of copies would take one name"
                else:
                    what = "their copies would share one folder, and the folder tree would not be kept"
                raise SpecsError(
                    f"{first} and {name} differ only in case or Unicode normalization; "
                    f"on a file system that ignores both, {what} (R34)"
                )


_DELIMITERS = ("⟬".encode(), "⟭".encode())


def check_source(path: str, source: bytes) -> None:
    """Raise SpecsError, naming the file, unless `source` is UTF-8 without ⟬ or ⟭.

    Spec files are UTF-8, and the delimiters appear nowhere in
    the specs: a file holding one would give markers that are not IDs,
    and a search for an ID could find the specs' own text.

    Spec: R3, R19, R34
    """
    try:
        source.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SpecsError(
            f"{path}: not UTF-8 (byte 0x{source[exc.start]:02x} at offset {exc.start}); "
            "spec files must be UTF-8 (R34)"
        ) from None
    found = [(source.find(d), d) for d in _DELIMITERS if d in source]
    if found:
        offset, delimiter = min(found)
        raise SpecsError(
            f"{path}: holds the delimiter {delimiter.decode()} at offset {offset}; "
            "the specs never hold ⟬ or ⟭ (R19, R34)"
        )


def read_blob(repo: Path, sha: str) -> bytes:
    """The exact bytes of a blob (no filters, no line-ending conversion: LF, CRLF and a lone CR stay).

    Spec: R3, R62
    """
    return _git(repo, "cat-file", "blob", sha)


def read_file(repo: Path, commit: str, path: str) -> bytes:
    """The exact bytes of `path` at `commit`, the pinned one for verify.

    Spec: R64
    """
    return _git(repo, "cat-file", "blob", f"{commit}:{path}")


# --- output -----------------------------------------------------------------


def check_outputs(out: Path) -> None:
    """Raise OutputError, before anything is written, when an output path is in the way.

    `data/` and `specs-repo-annotated/` must be folders, not symbolic links, and
    `data/report.md`, `data/report.json` and `data/tree.jsonl.tmp` must
    not be folders or symbolic links: writing through a link would write
    outside the output folder, and a folder there is no file of the
    generator's to remove. `data/tree.jsonl` itself was read already
    (read_store), and write_store replaces it, never writes through it.

    Spec: R34, R62
    """
    for folder in (out / STORE_PATH.parent, out / ANNOTATED):
        if folder.is_symlink():
            raise OutputError(f"{folder}: a symbolic link; a build never writes outside the output folder through a link")
        if os.path.lexists(folder) and not folder.is_dir():
            raise OutputError(f"{folder}: not a folder")
    for path in (out / REPORT_MD, out / REPORT_JSON, out / STORE_TMP):
        if path.is_symlink():
            raise OutputError(f"{path}: a symbolic link; a build never writes outside the output folder through a link")
        if path.is_dir():
            raise OutputError(f"{path}: a folder")


def _own_file(path: Path) -> bool:
    """Whether `path` is a regular file, no symbolic link, with one name (one link): no hard link.

    Spec: R62, U6
    """
    try:
        st = os.lstat(path)
    except OSError:
        return False
    return stat.S_ISREG(st.st_mode) and st.st_nlink == 1


def _write_if_changed(path: Path, data: bytes) -> None:
    """Write `data` to `path` as a new file, unless a file of its own there holds exactly that.

    A file it cannot read is replaced, unread. A file with more than one
    link is replaced whatever it holds: written into, it would change the
    other names too, and kept, it would stay shared with them.

    Spec: R62, U6
    """
    try:
        if _own_file(path) and path.read_bytes() == data:
            return
    except OSError:  # no permission to read it: compare nothing, write it
        pass
    write_new(path, data)


def _kept_names(paths: Sequence[str]) -> tuple[set[str], set[str]]:
    """The copies of `paths` and the folders that hold them, relative to specs-repo-annotated/.

    Spec: R62, U6
    """
    files = set(paths)
    folders = {"/".join(path.split("/")[:n]) for path in paths for n in range(1, path.count("/") + 1)}
    return files, folders


def _sweep_annotated(root: Path, paths: Sequence[str]) -> None:
    """Remove everything under specs-repo-annotated/ but the copies of `paths` and their folders.

    Kept: a regular file at the path of a copy, which is then written anew
    when its bytes differ or it has more than one link (_write_if_changed),
    and a real folder at the path of a folder of copies, each name exactly
    as written. Everything else is removed: a file that is no copy (a
    vanished copy, one a lost JSONL left), a folder that holds no copy or
    stands at a copy's path, with everything in it, a file at a folder's
    path, and every symbolic link, removed itself and never followed, so
    nothing behind it is touched. Removing a name never changes the file
    another hard link names.
    `root` itself is no link (check_outputs). Runs before the copies
    are written, on a rebuild of the same commit too.

    Spec: R34, R62, U6
    """
    if not root.is_dir():
        return
    files, folders = _kept_names(paths)
    pending = [(root, "")]
    while pending:
        folder, prefix = pending.pop()
        with os.scandir(folder) as entries:
            found = sorted(entries, key=lambda e: e.name)
        for entry in found:
            rel = prefix + entry.name
            if entry.is_symlink():  # U6: never followed, the link itself goes
                os.unlink(entry.path)
            elif entry.is_dir(follow_symlinks=False):
                if rel in folders:
                    pending.append((Path(entry.path), rel + "/"))
                else:  # no copy in it, or at a copy's path; rmtree removes links inside, never follows them
                    shutil.rmtree(entry.path)
            elif rel not in files or not entry.is_file(follow_symlinks=False):
                os.unlink(entry.path)  # no copy, a file at a folder's path, or no regular file (a FIFO)


def _foreign_paths(root: Path, paths: Sequence[str]) -> list[str]:
    """verify's problems for what stands under specs-repo-annotated/ and is no copy of `paths` nor a folder of them.

    Never follows a link and never looks into a foreign folder; what stands
    at a copy's or a folder's path is check_file's `no annotated file`, not
    named again. In the code point order of the paths, each path with its
    control characters escaped, so that a problem stays on one line. A link
    or a file at specs-repo-annotated/ itself is the problem build refuses it with.

    Spec: R34, R64, U6
    """
    if root.is_symlink():  # R34, R64: build refuses it; never followed
        return [f"{escape_controls(str(root))}: a symbolic link; a build never writes outside the output folder through a link"]
    if os.path.lexists(root) and not root.is_dir():  # R34, R64: build refuses it
        return [f"{escape_controls(str(root))}: not a folder"]
    if not root.is_dir():
        return []
    files, folders = _kept_names(paths)
    found: list[tuple[str, str]] = []
    pending = [(root, "")]
    while pending:
        folder, prefix = pending.pop()
        try:
            with os.scandir(folder) as entries:
                names = sorted(entries, key=lambda e: e.name)
        except OSError as exc:  # R64: its names cannot be read
            found.append((prefix.rstrip("/"), f"{escape_controls(str(folder))}: cannot be opened: {exc.strerror or exc}"))
            continue
        for entry in names:
            rel = prefix + entry.name
            if rel in folders:
                if entry.is_dir(follow_symlinks=False):
                    pending.append((Path(entry.path), rel + "/"))
            elif rel not in files:
                where = escape_controls(entry.path)  # R34, R62: a line break would split the problem
                found.append((rel, f"{where}: not a copy of a JSONL file; build removes it (U6)"))
    return [problem for _, problem in sorted(found)]


def _is_copy(root: Path, rel: str) -> bool:
    """Whether `root/rel` is a regular file, reached through no symbolic link from `root` on.

    Spec: R64, U6
    """
    target = root / rel
    on_the_way = [folder for folder in target.parents if folder == root or root in folder.parents]
    if any(folder.is_symlink() for folder in on_the_way) or target.is_symlink():
        return False
    return target.is_file()


def _report_text(changes_md: str, old_commit: str, new_commit: str) -> str:
    """report_markdown() with the two versions of the specs under its title.

    Spec: R63
    """
    head, _, rest = changes_md.partition("\n")
    since = f"`{old_commit}`" if old_commit else "nothing (first run)"
    return f"{head}\n\nSpecs {since} -> `{new_commit}`.\n{rest}"


# --- commands -----------------------------------------------------------------


def build(specs: Path, commit: str, out: Path) -> Store:
    """Build layer 2 from `specs` at `commit` into `out`; return the new store.

    The new trees are matched against the previous JSONL, their files
    take prefixes and their nodes IDs, and the nodes get their statuses
    and flags.

    Spec: R9, R10, R14, R53, R54, R55, R56, R57, R58, R59, R60
    """
    sha = resolve_commit(specs, commit)
    blobs, plain_blobs = list_selected(specs, sha)
    if not blobs:  # R34: the wrong repository would retire every ID and prefix for good
        raise SpecsError(f"no .md file to build at {sha}; is --specs right?")
    check_paths(list(blobs) + list(plain_blobs))
    sources = {path: read_blob(specs, blob) for path, blob in blobs.items()}
    plain = {path: read_blob(specs, blob) for path, blob in plain_blobs.items()}  # R62: copied byte for byte
    for path, src in sources.items():
        check_source(path, src)
    trees: dict[str, TreeNode] = {path: build_tree(src, path) for path, src in sources.items()}

    store_path = out / STORE_PATH
    previous = read_store(store_path)
    problems = _check_store(previous) + _check_node_files(previous)
    if problems:  # R34: its output would break unique IDs, prefixes or their history
        raise StoreError(f"{store_path}: not consistent: " + "; ".join(problems))
    check_outputs(out)
    renames = detect_renames(trees, previous)
    prefixes = assign_prefixes(sorted(trees), previous.prefixes(), previous.retired_prefixes(), renames)
    changes = assign_ids(trees, previous, prefixes)

    annotated: dict[str, bytes] = {}
    insertions: dict[str, list[Insertion]] = {}
    for path, root in trees.items():
        annotated[path], insertions[path] = annotate(sources[path], root)
    store = build_store(
        trees,
        prefixes,
        previous,
        changes,
        specs_commit=sha,
        generator_version=generator_version(),
        sha256s={path: hashlib.sha256(src).hexdigest() for path, src in sources.items()},
        insertions=insertions,
    )
    # R61: a copy line records each plain copy's path and sha256
    store.copies = {path: hashlib.sha256(data).hexdigest() for path, data in plain.items()}
    rebuild = bool(previous.files) and previous.specs_commit == sha
    if rebuild:  # R60, U3: same version again, keep its flags
        old = {n.id: n for n in previous.nodes}
        unchanged = {c.id for c in changes if c.status is Status.UNCHANGED}
        for node in store.nodes:
            if node.id in unchanged and node.id in old:
                node.to_review = old[node.id].to_review
                node.changed_since = old[node.id].changed_since
            elif node.status == "retired" and node.id in old and old[node.id].status == "retired":
                node.changed_since = old[node.id].changed_since  # retired in this version

    try:
        _write_outputs(out, previous, {**annotated, **plain}, store, store_path, rebuild, changes, sha)
    except OSError as exc:  # R62: the system refused a write or a removal, stop there
        where = escape_controls(str(exc.filename if exc.filename is not None else out))  # R34: one line
        raise BuildStopped(f"{where}: cannot be written: {exc.strerror or exc}") from None
    return store


def _write_outputs(
    out: Path,
    previous: Store,
    annotated: dict[str, bytes],
    store: Store,
    store_path: Path,
    rebuild: bool,
    changes: list[Change],
    sha: str,
) -> None:
    """Write the outputs of build(): the copies, annotated and plain, then the JSONL, then the reports.

    Spec: R60, R62, R63, U6
    """
    # R62, U6: first everything that is no copy of this build, the vanished
    # copies included: a new `x.md` may replace a folder `x.md/` of the
    # previous version, or the other way round
    _sweep_annotated(out / ANNOTATED, list(annotated))
    for path, data in annotated.items():
        _write_if_changed(out / ANNOTATED / path, data)
    write_store(store_path, store)

    # R60, R63: a rebuild that changed nothing keeps both reports, when both exist
    changed = any(c.status is not Status.UNCHANGED for c in changes)
    # R62: kept only as files of their own, no hard link
    keep_report = rebuild and not changed and _own_file(out / REPORT_MD) and _own_file(out / REPORT_JSON)
    if not keep_report:
        md = _report_text(report_markdown(changes), previous.specs_commit, sha)
        _write_if_changed(out / REPORT_MD, md.encode("utf-8"))
        _write_if_changed(out / REPORT_JSON, report_json(changes).encode("utf-8"))


def verify(specs: Path, out: Path) -> list[str]:
    """Problems found in the layer 2 under `out`, worded as the spec lists them; empty when it is sound.

    Spec: R34, R64, U6
    """
    store_path = out / STORE_PATH
    if store_absent(store_path):  # R34, R64: a broken link there cannot be opened
        return [f"{store_path}: no JSONL; run `norms-gen build` first"]
    try:
        store = read_store(store_path)
    except StoreError as exc:  # corrupt: a problem to report, not a crash
        return [f"cannot read the JSONL: {exc}"]
    problems: list[str] = []
    try:
        commit = resolve_commit(specs, store.specs_commit)
    except GitError as exc:
        return [f"pinned commit {store.specs_commit!r} not in {specs}: {exc}"]
    by_file: dict[str, list[StoredNode]] = {path: [] for path in store.files}
    problems += _check_store(store) + _check_node_files(store)
    for node in store.active():
        if node.file in by_file:
            by_file[node.file].append(node)
    for path, stored in sorted(store.files.items()):
        try:
            source = read_file(specs, commit, path)
        except GitError as exc:
            problems.append(f"{path}: not in the specs at {commit}: {exc}")
            continue
        annotated_path = out / ANNOTATED / path
        try:
            if not _is_copy(out / ANNOTATED, path):  # a folder or a symbolic link is not a copy
                problems.append(f"{path}: no annotated file at {annotated_path}")
                continue
            links = os.lstat(annotated_path).st_nlink
            annotated_bytes = annotated_path.read_bytes()
        except OSError as exc:  # no permission to read it, or to search a folder of it
            problems.append(f"{path}: annotated file at {annotated_path} cannot be opened: {exc.strerror or exc}")
            continue
        if links > 1:  # R64, U6: another name could write the copy
            problems.append(f"{path}: annotated file at {annotated_path} has {links} links; build writes it anew (U6)")
        problems += check_file(path, source, annotated_bytes, stored, by_file[path])
    for path, digest in sorted(store.copies.items()):  # R64: each plain copy, as a file
        problems += _check_plain_copy(specs, commit, out, path, digest)
    return problems + _foreign_paths(out / ANNOTATED, list(store.files) + list(store.copies))  # U6: what build did not write


def _check_plain_copy(specs: Path, commit: str, out: Path, path: str, digest: str) -> list[str]:
    """verify's problems for one plain copy: in the specs, a file of one name, the bytes of the spec file.

    Its `sha256` is the whole of its content: the JSONL's must be
    the specs', and the copy's.

    Spec: R64
    """
    try:
        source = read_file(specs, commit, path)
    except GitError as exc:
        return [f"{path}: not in the specs at {commit}: {exc}"]
    copy_path = out / ANNOTATED / path
    try:
        if not _is_copy(out / ANNOTATED, path):  # a folder or a symbolic link is not a copy
            return [f"{path}: no copy at {copy_path}"]
        links = os.lstat(copy_path).st_nlink
        data = copy_path.read_bytes()
    except OSError as exc:  # no permission to read it, or to search a folder of it
        return [f"{path}: copy at {copy_path} cannot be opened: {exc.strerror or exc}"]
    problems: list[str] = []
    if links > 1:  # R64, U6: another name could write the copy
        problems.append(f"{path}: copy at {copy_path} has {links} links; build writes it anew (U6)")
    source_digest = hashlib.sha256(source).hexdigest()
    if source_digest != digest:  # R61: the specs are the version the JSONL recorded
        problems.append(f"{path}: sha256 {source_digest} differs from the JSONL's {digest}")
    if hashlib.sha256(data).hexdigest() != digest:
        problems.append(f"{path}: copy at {copy_path} differs from the specs")
    return problems


def _check_store(store: Store) -> list[str]:
    """The JSONL's own consistency: each ID stored once, prefixes unique, never reused.

    Spec: R9, R14, R34, R58, R64
    """
    problems: list[str] = []
    seen: dict[str, StoredNode] = {}
    for node in store.nodes:
        first = seen.get(node.id)
        if first is not None:
            problems.append(f"{node.id} is stored twice ({first.status} in {first.file}, {node.status} in {node.file})")
        else:
            seen[node.id] = node
    owners: dict[str, str] = {}
    for path, stored in sorted(store.files.items()):
        if stored.prefix in owners:
            problems.append(f"prefix {stored.prefix} is used by {owners[stored.prefix]} and {path}")
        owners.setdefault(stored.prefix, path)
    for prefix in sorted(set(store.retired_prefix_list) & set(owners)):
        problems.append(f"prefix {prefix} is retired but used by {owners[prefix]}")
    return problems


def _check_node_files(store: Store) -> list[str]:
    """Each active node is in a file of the JSONL.

    Spec: R34, R64
    """
    return [
        f"{node.id} is in {node.file}, which is not a JSONL file"
        for node in store.active()
        if node.file not in store.files
    ]


# --- entry point ----------------------------------------------------------------


def _parser() -> argparse.ArgumentParser:
    """The command line; a usage error exits with status 2.

    Spec: R62
    """
    parser = argparse.ArgumentParser(prog="norms-gen", description="Layer 2 generator: the norms tree of the specs.")
    commands = parser.add_subparsers(dest="command", required=True)

    b = commands.add_parser("build", help="build data/tree.jsonl, specs-repo-annotated/ and the report")
    b.add_argument("--specs", required=True, type=Path, help="path of the specs git repository")
    b.add_argument("--commit", default="HEAD", help="specs commit to build (default HEAD)")
    b.add_argument("--out", type=Path, default=None, help="output folder (default: the git repository of the working directory)")

    v = commands.add_parser("verify", help="check the output against the specs at the pinned commit")
    v.add_argument("--specs", required=True, type=Path, help="path of the specs git repository")
    v.add_argument("--out", type=Path, default=None, help="output folder (default: the git repository of the working directory)")

    r = commands.add_parser("report", help="print the last report")
    r.add_argument("--out", type=Path, default=None, help="output folder (default: the git repository of the working directory)")
    r.add_argument("--json", action="store_true", help="print report.json instead of report.md")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run one command; return its exit status, with the spec's messages.

    A usage error leaves through argparse's SystemExit with status 2, and
    an interrupt (KeyboardInterrupt) through Python's default handling:
    neither is an Exception. Any other exception that no requirement
    words is caught here: its type, its message and its stack trace go to
    standard error, and the status is 4.

    Spec: R34, R62
    """
    args = _parser().parse_args(argv)
    if args.out is None:
        args.out = default_out()
    try:
        return _run(args)
    except (GitError, SpecsError, StoreError, OutputError) as exc:  # R34: a refusal, nothing written
        print(f"norms-gen: {exc}", file=sys.stderr)
        return EXIT_REFUSED
    except BuildStopped as exc:  # R62: the system stopped build part way
        print(f"norms-gen: {exc}", file=sys.stderr)
        return EXIT_STOPPED
    except Exception as exc:  # R62: an unexpected error, a defect or a failure no requirement words
        sys.stdout.flush()
        print(f"norms-gen: unexpected error: {type(exc).__name__}: {exc}", file=sys.stderr)
        traceback.print_exception(type(exc), exc, exc.__traceback__, file=sys.stderr)
        return EXIT_UNEXPECTED


def _run(args: argparse.Namespace) -> int:
    """The command of `args`, with the spec's messages; a known error is raised to main().

    Spec: R62, R64
    """
    if args.command == "build":
        store = build(args.specs, args.commit, args.out)
        active = len(store.active())
        _say(
            f"built {len(store.files)} files, {active} active nodes, "
            f"{len(store.nodes) - active} retired, at {store.specs_commit}"
        )
        return EXIT_OK
    if args.command == "verify":
        problems = verify(args.specs, args.out)
        for problem in problems:
            print(problem, file=sys.stderr)
        if problems:  # R64: verify found a problem
            print(f"verify: {len(problems)} problems", file=sys.stderr)
            return EXIT_PROBLEMS
        store = read_store(args.out / STORE_PATH)
        _say(f"verify: {len(store.files)} files, {len(store.active())} active nodes, all sound")
        return EXIT_OK
    path = args.out / (REPORT_JSON if args.json else REPORT_MD)
    if store_absent(path):  # R62: as for the JSONL, a broken link there cannot be opened
        print(f"no report at {path}; run `norms-gen build` first", file=sys.stderr)
        return EXIT_PROBLEMS
    try:
        data = path.read_bytes()
    except OSError as exc:  # R62: a folder or a broken link at its path, no permission to read it
        print(f"{path}: cannot be opened: {exc.strerror or exc}", file=sys.stderr)
        return EXIT_PROBLEMS
    try:
        sys.stdout.flush()  # its exact bytes: read_text() would turn CRLF and a lone CR into LF
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()
    except BrokenPipeError:  # R62: the reader stopped reading, as `| head`
        _drop_stdout()
    return EXIT_OK


def _say(line: str) -> None:
    """Print `line` on standard output; a reader that closed it ends the writing, not the command.

    Spec: R62
    """
    try:
        print(line)
        sys.stdout.flush()
    except BrokenPipeError:
        _drop_stdout()


def _drop_stdout() -> None:
    """Send what is left for standard output to the null device, so the exit's flush raises nothing.

    Spec: R62
    """
    try:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        os.close(devnull)
    except (OSError, ValueError, AttributeError, io.UnsupportedOperation):  # not a file, as under pytest
        pass


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
