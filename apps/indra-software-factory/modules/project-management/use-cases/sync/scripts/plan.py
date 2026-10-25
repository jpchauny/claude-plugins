"""Compare the source project.json with the copy of every target (ORC-30).

Usage:
    python3 -I plan.py --repo <root of the repository of layer 1>

Reads project.json at the commit HEAD of the repository of layer 1 (ORC-29),
finds the entry of that repository by its remote origin (ORC-21), and prints
one JSON object: the source commit, the source bytes' path in a temporary
file, and for each target its name, its absolute path and its state:
"differs", "same" or "skipped" with a reason (ORC-32). Writes nothing in any
repository.
"""

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True)


def owner_name(url: str) -> str | None:
    m = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$", url.strip())
    return f"{m.group(1)}/{m.group(2)}" if m else None


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", required=True, type=Path)
    repo = parser.parse_args(argv).repo.resolve()

    shown = git(repo, "show", "HEAD:project.json")
    if shown.returncode:
        print(json.dumps({"error": "no project.json at HEAD"}))
        return 1
    source = shown.stdout
    try:
        data = json.loads(source)
        repos = data["repositories"]
        assert isinstance(repos, list) and all({"owner", "name", "layer", "path"} <= set(r) for r in repos)
    except (ValueError, KeyError, TypeError, AssertionError):
        print(json.dumps({"error": "project.json at HEAD does not have the form of ORC-20"}))
        return 1
    origin = git(repo, "remote", "get-url", "origin")
    me = owner_name(origin.stdout.decode()) if not origin.returncode else None
    entries = [r for r in data["repositories"] if f"{r['owner']}/{r['name']}" == me]
    if not entries:
        print(json.dumps({"error": "this repository is not in project.json (ORC-21)"}))
        return 1
    self_entry = entries[0]
    if self_entry["layer"] != 1:
        print(json.dumps({"error": "sync runs only in the repository of layer 1 (ORC-28)", "layer": self_entry["layer"]}))
        return 1
    rel = Path(self_entry["path"])
    folder = repo
    for _ in rel.parts:
        folder = folder.parent

    tmp = tempfile.NamedTemporaryFile(prefix="project-", suffix=".json", delete=False)
    tmp.write(source)
    tmp.close()
    commit = git(repo, "rev-parse", "HEAD").stdout.decode().strip()

    targets = []
    for r in data["repositories"]:
        if r is self_entry:
            continue
        path = folder / r["path"]
        t = {"name": f"{r['owner']}/{r['name']}", "path": str(path)}
        if not (path / ".git").exists():
            t |= {"state": "skipped", "reason": f"not at its path {path} (ORC-22); clone: git clone https://github.com/{r['owner']}/{r['name']} {path}"}
        elif git(path, "status", "--porcelain", "--", "project.json").stdout.strip():
            t |= {"state": "skipped", "reason": "uncommitted changes in project.json"}
        else:
            head = git(path, "rev-parse", "--abbrev-ref", "HEAD").stdout.decode().strip()
            default = git(path, "symbolic-ref", "--short", "refs/remotes/origin/HEAD").stdout.decode().strip().removeprefix("origin/") or "main"
            if head != default:
                t |= {"state": "skipped", "reason": f"not on its default branch {default} (on {head})"}
            else:
                current = path / "project.json"
                same = current.is_file() and current.read_bytes() == source
                t |= {"state": "same" if same else "differs", "branch": default}
        targets.append(t)
    print(json.dumps({"source_commit": commit, "source_file": tmp.name, "targets": targets}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
