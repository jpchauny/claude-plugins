"""Tests of scripts/find_layer1.py: ORC-34 with the entries of project.json that are no layer (ORC-20, PRJ-2)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "find_layer1.py"
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t",
           GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null")
REPOSITORIES = [
    {"owner": "acme", "name": "billing-specs", "layer": 1, "path": "billing-specs"},
    {"owner": "acme", "name": "billing-norms", "layer": 2, "path": "billing-norms"},
    {"owner": "acme", "name": "billing-orchestration", "role": "orchestration", "path": "billing-orchestration"},
    {"owner": "acme", "name": "billing-tooling", "role": "tooling", "path": "billing-tooling"},
]


def repository(folder: Path, name: str, project_json: str) -> Path:
    path = folder / name
    path.mkdir()
    for args in (["init", "-q", "-b", "main"], ["remote", "add", "origin", f"https://github.com/acme/{name}"]):
        subprocess.run(["git", "-C", str(path), *args], check=True, env=ENV)
    (path / "project.json").write_text(project_json, encoding="utf-8")
    for args in (["add", "project.json"], ["commit", "-q", "-m", "start"]):
        subprocess.run(["git", "-C", str(path), *args], check=True, env=ENV)
    return path


def run(repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-I", str(SCRIPT), "--repo", str(repo)], capture_output=True, text=True,
                          env=ENV)


def test_the_entries_of_the_orchestration_and_the_tooling_repository_are_neither_required_nor_refused(tmp_path):
    project_json = json.dumps({"project": "billing", "repositories": REPOSITORIES}) + "\n"
    specs = repository(tmp_path, "billing-specs", project_json)
    result = run(repository(tmp_path, "billing-norms", project_json))
    assert (result.returncode, result.stdout.strip()) == (0, str(specs))


def test_the_tooling_repository_is_not_the_repository_of_layer_2(tmp_path):
    project_json = json.dumps({"project": "billing", "repositories": REPOSITORIES}) + "\n"
    result = run(repository(tmp_path, "billing-tooling", project_json))
    assert result.returncode == 1
    assert result.stderr == "error: this repository is the tooling repository, not of layer 2 (ORC-34)\n"
