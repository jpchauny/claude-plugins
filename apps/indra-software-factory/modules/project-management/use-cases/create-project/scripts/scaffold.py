"""Render the initial files of the repositories of a new project.

Usage:
    python3 -I scaffold.py --project <name> --owner <github owner> \
        --folder <project folder> [--components <a,b,...>]

Writes, in the project folder, one folder per repository of the project:
<project>-drafts, <project>-specs, <project>-norms, and <project>-code or one
<project>-code-<component> per component. Each gets the files of
../templates/<layer>, with {{project}}, {{owner}}, {{repository}},
{{repositories}} and {{links}} replaced, and the project.json of the
project (ORC-20), the same bytes in every repository. Prints, for each
repository, a line "<layer> <name>" and then the absolute path of each file
it wrote. Refuses, and writes nothing, when a name or a component is not
lowercase-dash, a component is repeated, or the project folder exists.
Creates no repository on GitHub and runs no git command: the skill does that.
"""

import argparse
import json
import re
import sys
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"
NAME = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
LAYER_NAMES = {0: "Drafts", 1: "Specs", 2: "Norms", 3: "Code"}
TEMPLATE_OF = {0: "drafts", 1: "specs", 2: "norms", 3: "code"}


def repositories(project: str, owner: str, components: list[str]) -> list[dict]:
    repos = [
        {"owner": owner, "name": f"{project}-drafts", "layer": 0},
        {"owner": owner, "name": f"{project}-specs", "layer": 1},
        {"owner": owner, "name": f"{project}-norms", "layer": 2},
    ]
    if components:
        repos += [{"owner": owner, "name": f"{project}-code-{c}", "layer": 3, "component": c} for c in components]
    else:
        repos.append({"owner": owner, "name": f"{project}-code", "layer": 3})
    for r in repos:
        r["path"] = r["name"]
    return repos


def table(repos: list[dict], this: str) -> str:
    rows = ["| Layer | Repository |", "|---|---|"]
    for r in repos:
        mark = " (this one)" if r["name"] == this else ""
        rows.append(f"| {r['layer']}. {LAYER_NAMES[r['layer']]} | `{r['owner']}/{r['name']}`{mark} |")
    return "\n".join(rows)


def links(repos: list[dict]) -> str:
    return ", ".join(f"[{r['name']}](https://github.com/{r['owner']}/{r['name']})" for r in repos)


def render(text: str, values: dict) -> str:
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--project", required=True)
    parser.add_argument("--owner", required=True)
    parser.add_argument("--folder", required=True, type=Path)
    parser.add_argument("--components", default="")
    args = parser.parse_args(argv)

    components = [c.strip() for c in args.components.split(",") if c.strip()]
    if not NAME.match(args.project):
        print(f"error: project name must be lowercase-dash: {args.project!r}", file=sys.stderr)
        return 1
    bad = [c for c in components if not NAME.match(c)]
    if bad:
        print("error: components must be lowercase-dash: " + ", ".join(repr(c) for c in bad), file=sys.stderr)
        return 1
    if len(set(components)) != len(components):
        print("error: a component is repeated", file=sys.stderr)
        return 1
    folder = args.folder.resolve()
    if folder.exists():
        print(f"error: already exists: {folder}", file=sys.stderr)
        return 1

    repos = repositories(args.project, args.owner, components)
    project_json = json.dumps({"project": args.project, "repositories": repos}, indent=2) + "\n"
    for r in repos:
        target = folder / r["path"]
        values = {
            "project": args.project,
            "owner": args.owner,
            "repository": r["name"],
            "repositories": table(repos, r["name"]),
            "links": links(repos),
        }
        print(f"{r['layer']} {r['name']}")
        source = TEMPLATES / TEMPLATE_OF[r["layer"]]
        for file in sorted(p for p in source.rglob("*") if p.is_file()):
            dest = target / file.relative_to(source)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(render(file.read_text(encoding="utf-8"), values), encoding="utf-8")
            print(dest)
        dest = target / "project.json"
        dest.write_text(project_json, encoding="utf-8")
        print(dest)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
