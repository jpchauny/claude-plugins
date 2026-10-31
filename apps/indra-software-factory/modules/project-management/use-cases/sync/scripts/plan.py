"""Compare the source project.json with the copy of every target (ORC-30).

Usage:
    python3 -I plan.py --repo <root of the repository of layer 1>

Reads project.json at the commit HEAD of the repository of layer 1 (ORC-29),
finds the entry of that repository by its remote origin (ORC-21), and prints
one JSON object: the source commit, the source bytes' path in a temporary
file, and for each target its name, its absolute path and its state:
"differs", "same" or "skipped" with a reason (ORC-32). For each target of
layer 3 or 4 it also compares the rules "deny" of its .claude/settings.json
with those that ORC-5 writes for the source (SNC-1): it replaces the managed
rules, those that name a repository of layer 3 or 4 of the source, of the
target's project.json before the sync or of any version of it committed in
the target, and keeps every other rule, and gives
"settings_state": "differs", "same" or "skipped" with "settings_reason"; when
it differs, "settings_file" is a temporary file with the whole new
.claude/settings.json, its rules "deny" replaced and every other setting
kept. The orchestration repository and the tooling repository, the entries
with "role", are targets of project.json only (SNC-2, SNC-3). Writes nothing
in any repository.
"""

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from deny_rules import deny_rules, managed, merged  # noqa: E402  (the module's shared code, DEV-7)


def git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True)


def owner_name(url: str) -> str | None:
    m = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$", url.strip())
    return f"{m.group(1)}/{m.group(2)}" if m else None


def temporary(data: bytes, suffix: str) -> str:
    tmp = tempfile.NamedTemporaryFile(prefix="sync-", suffix=suffix, delete=False)
    tmp.write(data)
    tmp.close()
    return tmp.name


ROLES = ("orchestration", "tooling")  # ORC-20


def has_the_form_of_orc_20(repos) -> bool:
    """The entries of project.json as ORC-20 lists them: each names its owner,
    name and path, and has either a layer or a role, "orchestration" or
    "tooling", each role at most once (SNC-2, SNC-3)."""
    if not isinstance(repos, list) or not all(isinstance(r, dict) for r in repos):
        return False
    roles = [r["role"] for r in repos if "role" in r]
    return (all({"owner", "name", "path"} <= set(r) and (("layer" in r) != ("role" in r)) for r in repos)
            and all(role in ROLES for role in roles) and len(roles) == len(set(roles)))


def repos_of(text: bytes | str) -> list[dict]:
    """The repositories of one version of project.json, or none when it has
    not the form of ORC-20."""
    try:
        repos = json.loads(text)["repositories"]
        return [r for r in repos if isinstance(r, dict) and "path" in r]
    except (ValueError, KeyError, TypeError):
        return []


def previous_repos(path: Path) -> list[dict]:
    """The repositories of the project.json of the target before the sync and
    of every version of it committed in the target (SNC-1), so that a rule
    stays managed after a sync that wrote project.json but skipped the
    settings."""
    repos = []
    try:
        repos += repos_of((path / "project.json").read_bytes())
    except OSError:
        pass
    log = git(path, "log", "--format=%H", "--", "project.json")
    for commit in log.stdout.decode().split() if not log.returncode else []:
        shown = git(path, "show", f"{commit}:project.json")
        if not shown.returncode:
            repos += repos_of(shown.stdout)
    return repos


def settings_plan(path: Path, repos: list[dict], entry: dict) -> dict:
    """The rules "deny" of a target of layer 3 or 4, against the source (SNC-1)."""
    settings = path / ".claude" / "settings.json"
    if not settings.is_file():
        return {"settings_state": "skipped", "settings_reason": "no .claude/settings.json"}
    if git(path, "status", "--porcelain", "--", ".claude/settings.json").stdout.strip():
        return {"settings_state": "skipped", "settings_reason": "uncommitted changes in .claude/settings.json"}
    try:
        data = json.loads(settings.read_text(encoding="utf-8"))
        permissions = data.setdefault("permissions", {})
        current = permissions.get("deny", [])
        assert isinstance(permissions, dict) and isinstance(current, list)
        assert all(isinstance(rule, str) for rule in current)
    except (ValueError, AttributeError, AssertionError):
        return {"settings_state": "skipped", "settings_reason": ".claude/settings.json is not a JSON object of Claude Code"}
    wanted = merged(current, deny_rules(repos, entry), managed(repos, previous_repos(path)))
    if wanted == current:
        return {"settings_state": "same"}
    if wanted:
        permissions["deny"] = wanted
    else:
        permissions.pop("deny", None)
    text = json.dumps(data, indent=2) + "\n"
    return {"settings_state": "differs", "deny": wanted, "settings_file": temporary(text.encode("utf-8"), ".json")}


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
        assert has_the_form_of_orc_20(repos)
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
    if self_entry.get("layer") != 1:
        print(json.dumps({"error": "sync runs only in the repository of layer 1 (ORC-28)", "layer": self_entry.get("layer")}))
        return 1
    rel = Path(self_entry["path"])
    folder = repo
    for _ in rel.parts:
        folder = folder.parent

    source_file = temporary(source, ".json")
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
                if r.get("layer") in (3, 4):
                    t |= settings_plan(path, data["repositories"], r)
        targets.append(t)
    print(json.dumps({"source_commit": commit, "source_file": source_file, "targets": targets}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
