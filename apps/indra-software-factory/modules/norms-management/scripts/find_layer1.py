"""Find the repository of layer 1 of the project, through project.json (ORC-34).

Usage:
    python3 -I find_layer1.py --repo <root of the repository of layer 2>

Reads project.json of the repository, finds its entry by the remote origin
(ORC-21), requires it to be of layer 2, and prints the absolute path of the
repository of layer 1 (project folder followed by its path). When the
repository of layer 1 is not at its path, prints the command that clones it
(ORC-22). Before it prints, it compares the bytes of the repository's
project.json with project.json at the commit HEAD of the repository of
layer 1, the canonical copy (ORC-23, ORC-24); when they differ, it fails and
recommends /project-management:sync. Exits 1 with the reason on standard
error on any failure.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def fail(message: str) -> int:
    print(f"error: {message}", file=sys.stderr)
    return 1


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", required=True, type=Path)
    repo = parser.parse_args(argv).repo.resolve()

    try:
        data = json.loads((repo / "project.json").read_text(encoding="utf-8"))
        repos = data["repositories"]
        assert isinstance(repos, list) and all({"owner", "name", "layer", "path"} <= set(r) for r in repos)
    except FileNotFoundError:
        return fail(f"no project.json in {repo}")
    except (ValueError, KeyError, TypeError, AssertionError):
        return fail("project.json does not have the form of ORC-20")

    origin = subprocess.run(["git", "-C", str(repo), "remote", "get-url", "origin"], capture_output=True, text=True)
    m = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$", origin.stdout.strip()) if origin.returncode == 0 else None
    me = f"{m.group(1)}/{m.group(2)}" if m else None
    mine = [r for r in repos if f"{r['owner']}/{r['name']}" == me]
    if not mine:
        return fail("this repository is not in project.json (ORC-21)")
    if mine[0]["layer"] != 2:
        return fail(f"this repository is of layer {mine[0]['layer']}, not of layer 2 (ORC-34)")
    folder = repo
    for _ in Path(mine[0]["path"]).parts:
        folder = folder.parent
    layer1 = [r for r in repos if r["layer"] == 1]
    if len(layer1) != 1:
        return fail("project.json must list exactly one repository of layer 1 (ORC-20)")
    r = layer1[0]
    path = folder / r["path"]
    if not (path / ".git").exists():
        return fail(f"{r['owner']}/{r['name']} is not at {path} (ORC-22); clone it with: git clone https://github.com/{r['owner']}/{r['name']} {path}")
    canonical = subprocess.run(["git", "-C", str(path), "show", "HEAD:project.json"], capture_output=True)
    if canonical.returncode != 0:
        return fail(f"no project.json at HEAD of {r['owner']}/{r['name']} (ORC-23)")
    if canonical.stdout != (repo / "project.json").read_bytes():
        return fail(f"project.json of this repository differs from the one of {r['owner']}/{r['name']} (ORC-24); run /project-management:sync in the repository of layer 1")
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
