"""Everything of the generator is in the plugin norms-management.

Spec: U7
"""

from __future__ import annotations

import subprocess
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
PARTS = ("specs", "src/norms_generator", "tests", "docs", "use-cases", "pyproject.toml", "uv.lock")
OWN_NAMES = ("norms_generator", "norms-tree.md", "norms-versions.md", "norms-annotation-cases.md")


def test_every_part_is_in_the_plugin_folder() -> None:
    """Specs, code, tests, docs, skills and the package files are all under the plugin's folder.

    Spec: U7
    """
    assert [part for part in PARTS if not (PLUGIN / part).exists()] == []
    assert (PLUGIN / ".claude-plugin" / "plugin.json").is_file()


def test_no_part_of_the_generator_is_outside_the_plugin_folder() -> None:
    """In the repository that holds the plugin, no tracked path outside apps/indra-software-factory/modules/norms-management/ is a part of the generator.

    Spec: U7
    """
    done = subprocess.run(["git", "-C", str(PLUGIN), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if done.returncode != 0:  # an installed copy is no git repository: nothing else to look at
        return
    root = Path(done.stdout.strip())
    listed = subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True, check=True).stdout
    inside = PLUGIN.resolve().relative_to(root.resolve()).as_posix() + "/"
    outside = [p for p in listed.splitlines() if not p.startswith(inside) and any(n in p.split("/") for n in OWN_NAMES)]
    assert outside == []
