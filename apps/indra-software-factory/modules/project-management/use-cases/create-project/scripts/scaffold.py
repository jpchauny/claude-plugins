"""Render the initial files of a new project's three repositories.

Usage:
    python3 -I scaffold.py --project <name> --owner <github owner> --out <parent folder>

Writes <out>/<project>-specs, <out>/<project>-norms and <out>/<project>-code
from ../templates, replacing {{project}} and {{owner}}, and prints the
absolute path of each file it writes. Refuses, and writes
nothing, when the name is not lowercase-dash or a target folder exists.
Creates no repository on GitHub and runs no git command: the skill does that.
"""

import argparse
import re
import sys
from pathlib import Path

LAYERS = ("specs", "norms", "code")
TEMPLATES = Path(__file__).resolve().parent.parent / "templates"
NAME = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")


def render(text: str, project: str, owner: str) -> str:
    return text.replace("{{project}}", project).replace("{{owner}}", owner)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--project", required=True)
    parser.add_argument("--owner", required=True)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)

    if not NAME.match(args.project):
        print(f"error: project name must be lowercase-dash: {args.project!r}", file=sys.stderr)
        return 1
    targets = {layer: args.out.resolve() / f"{args.project}-{layer}" for layer in LAYERS}
    taken = [str(t) for t in targets.values() if t.exists()]
    if taken:
        print("error: already exists: " + ", ".join(taken), file=sys.stderr)
        return 1

    for layer, target in targets.items():
        source = TEMPLATES / layer
        for file in sorted(p for p in source.rglob("*") if p.is_file()):
            dest = target / file.relative_to(source)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(render(file.read_text(encoding="utf-8"), args.project, args.owner), encoding="utf-8")
            print(dest)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
