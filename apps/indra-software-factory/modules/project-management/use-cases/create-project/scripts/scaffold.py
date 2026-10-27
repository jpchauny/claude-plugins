"""Render the initial files of the repositories of a new project.

Usage:
    python3 -I scaffold.py --project <name> --owner <github owner> \
        --folder <project folder> --profile <prototype|product|critical> \
        [--components <a,b,...>]

Writes, in the project folder, one folder per repository of the five layers
of the project (LAY-1): <project>-drafts, <project>-specs, <project>-norms,
<project>-acceptance, and <project>-code or one <project>-code-<component> per
component. Each gets the files of
../templates/<layer>, with {{project}}, {{owner}}, {{repository}},
{{repositories}} and {{links}} replaced, and the project.json of the project (ORC-20),
the same bytes in every repository. The .claude/settings.json of the
repository of layer 3 also gets the rules "deny" of ACU-13, level 1, that
forbid reading and editing each repository of layer 4, and that of each
repository of layer 4 the rule that forbids editing the repository of layer 3
(ORC-5). The repository of layer 3 also gets acceptance.json, with the default
done profile given (CRP-2). The template of layer 3 holds the workflow of
GitHub Actions of ACU-34 (CRP-1); that of layer 4 holds none. Prints, for each repository, a
line "<layer> <name>" and then the absolute path of each file it wrote.
Refuses, and writes nothing, when a name or a component is not lowercase-dash,
a component is repeated, the profile is not a done profile, or the project
folder exists.
Creates no repository on GitHub and runs no git command: the skill does that.
"""

import argparse
import json
import re
import sys
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from deny_rules import deny_rules  # noqa: E402  (the module's shared code, DEV-7)

PROFILES = ("prototype", "product", "critical")
NAME = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
LAYER_NAMES = {0: "Drafts", 1: "Specs", 2: "Norms", 3: "Acceptance", 4: "Code"}
TEMPLATE_OF = {0: "drafts", 1: "specs", 2: "norms", 3: "acceptance", 4: "code"}


def repositories(project: str, owner: str, components: list[str]) -> list[dict]:
    repos = [
        {"owner": owner, "name": f"{project}-drafts", "layer": 0},
        {"owner": owner, "name": f"{project}-specs", "layer": 1},
        {"owner": owner, "name": f"{project}-norms", "layer": 2},
        {"owner": owner, "name": f"{project}-acceptance", "layer": 3},
    ]
    if components:
        repos += [{"owner": owner, "name": f"{project}-code-{c}", "layer": 4, "component": c} for c in components]
    else:
        repos.append({"owner": owner, "name": f"{project}-code", "layer": 4})
    for r in repos:
        r["path"] = r["name"]
    return repos


def table(repos: list[dict], this: str) -> str:
    rows = ["| Layer | Repository |", "|---|---|"]
    for r in repos:
        mark = " (this one)" if r["name"] == this else ""
        rows.append(f"| {r['layer']}. {LAYER_NAMES[r['layer']]} | `{r['owner']}/{r['name']}`{mark} |")
    return "\n".join(rows)


def add_deny(settings: Path, rules: list[str]) -> None:
    data = json.loads(settings.read_text(encoding="utf-8"))
    data.setdefault("permissions", {})["deny"] = rules
    settings.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def acceptance_json(profile: str) -> str:
    """The acceptance.json of ACU-6, as the project starts (CRP-2)."""
    data = {"default_profile": profile, "increments": [], "test_command": "", "product": {}}
    return json.dumps(data, indent=2) + "\n"


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
    parser.add_argument("--profile", required=True)
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
    if args.profile not in PROFILES:
        print(f"error: the default done profile must be one of {', '.join(PROFILES)}: {args.profile!r}", file=sys.stderr)
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
        rules = deny_rules(repos, r)
        if rules:
            add_deny(target / ".claude" / "settings.json", rules)
        if r["layer"] == 3:
            dest = target / "acceptance.json"
            dest.write_text(acceptance_json(args.profile), encoding="utf-8")
            print(dest)
        dest = target / "project.json"
        dest.write_text(project_json, encoding="utf-8")
        print(dest)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
