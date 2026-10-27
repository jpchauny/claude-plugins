"""Tests of scripts/index.py, the SessionStart hook of development-methodology.

Spec: specs/module.md. Each test names the MTH-n it checks. Run with:

    python3 -m unittest discover -s apps/indra-software-factory/modules/development-methodology/tests
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

PLUGIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(PLUGIN, "scripts", "index.py")
LAYERS = os.path.join(PLUGIN, "specs", "layers.md")
HOOKS = os.path.join(PLUGIN, "hooks", "hooks.json")
APP_URL = "https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/specs/app.md"
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(PLUGIN))))

sys.dont_write_bytecode = True  # no __pycache__ inside the plugin

LAYERS_TABLE = (
    "| Layer | Recommended name | Holds | Written by |\n"
    "|---|---|---|---|\n"
    "| 0. Drafts | `<project>-drafts` | The draft specs, in plain prose | People |\n"
    "| 1. Specs | `<project>-specs` | The specs | People |\n"
)
MODULES_TABLE = (
    "  | Module | Where |\n"
    "  |---|---|\n"
    "  | `a` | Everywhere. |\n"
    "  | `b`, `c` | Not yet decided. |\n"
)
TABLE = LAYERS_TABLE + "\n- **APP-6.** Where:\n\n" + MODULES_TABLE


def run(script, cwd=None, env=None):
    proc = subprocess.run([sys.executable, "-I", script], cwd=cwd, env=env,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc.returncode, proc.stdout, proc.stderr


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = os.path.realpath(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        # A copy of the plugin: scripts/index.py and specs/ (MTH-6: the root is found from the script's path).
        self.root = os.path.join(self.tmp, "plugin")
        os.makedirs(os.path.join(self.root, "scripts"))
        os.makedirs(os.path.join(self.root, "specs"))
        self.script = os.path.join(self.root, "scripts", "index.py")
        shutil.copy(SCRIPT, self.script)

    def write_layers(self, content):
        with open(os.path.join(self.root, "specs", "layers.md"), "wb") as f:
            f.write(content if isinstance(content, bytes) else content.encode("utf-8"))

    def expected(self, layer_lines, module_lines):
        r = self.root
        return ("Development methodology of Indra Software Factory (plugin development-methodology).\n"
                "This repository is one repository of a project, in one of five layers:\n"
                + "".join(line + "\n" for line in layer_lines)
                + "The modules of the app, each one a plugin, and where each is installed:\n"
                + "".join(line + "\n" for line in module_lines)
                + "Read for detail, before answering about the process:\n"
                "- The five layers, their rules, their terms, and where each module is installed: %s/specs/layers.md\n"
                "- The flow across the layers (a run, its steps and hand-offs): %s/specs/flow.md\n"
                "- What carries the methodology to every repository: %s/specs/module.md\n"
                "- What each module of the app does: %s\n" % (r, r, r, APP_URL)).encode("utf-8")

    def assert_fails(self):
        status, out, err = run(self.script)
        self.assertEqual(status, 1)
        self.assertEqual(out, b"")
        self.assertEqual(err, ("development-methodology: cannot read the tables of layers and of modules in %s/specs/layers.md\n"
                               % self.root).encode("utf-8"))


class Index(Base):
    def test_exact_index(self):
        """MTH-6: the index byte for byte, one line per row of each table, in the order of the table."""
        self.write_layers("# Layers\n\nIntro.\n\n" + TABLE + "\nAfter the table.\n")
        status, out, err = run(self.script)
        self.assertEqual((status, err), (0, b""))
        self.assertEqual(out, self.expected([
            "- 0. Drafts: The draft specs, in plain prose; written by: People; repository: `<project>-drafts`",
            "- 1. Specs: The specs; written by: People; repository: `<project>-specs`",
        ], [
            "- `a`: Everywhere.",
            "- `b`, `c`: Not yet decided.",
        ]))

    def test_working_directory_does_not_matter(self):
        """MTH-5: the output does not depend on the working directory."""
        self.write_layers(TABLE)
        other = os.path.join(self.tmp, "elsewhere")
        os.makedirs(other)
        self.assertEqual(run(self.script, cwd=other), run(self.script, cwd=self.root))

    def test_root_from_script_path_not_environment(self):
        """MTH-6: the plugin root comes from the script's path, not from CLAUDE_PLUGIN_ROOT."""
        self.write_layers(TABLE)
        env = dict(os.environ, CLAUDE_PLUGIN_ROOT="/elsewhere")
        status, out, _ = run(self.script, env=env)
        self.assertEqual(status, 0)
        self.assertIn(("%s/specs/layers.md\n" % self.root).encode(), out)
        self.assertNotIn(b"/elsewhere", out)

    def test_cells_keep_their_characters(self):
        """MTH-6: each cell without the spaces around it, every other character as it is."""
        self.write_layers("| Layer | Recommended name | Holds | Written by |\n|---|---|---|---|\n"
                          "|  4. Code  | `a`, or `b-<c>`  |  Code — and tests |Agents|\n\n" + MODULES_TABLE)
        status, out, _ = run(self.script)
        self.assertEqual(status, 0)
        self.assertIn("- 4. Code: Code — and tests; written by: Agents; repository: `a`, or `b-<c>`\n"
                      .encode("utf-8"), out)

    def test_binding_example(self):
        """MTH-6: with the real layers.md, the third line and the line after the layers are the binding example."""
        shutil.copy(LAYERS, os.path.join(self.root, "specs", "layers.md"))
        status, out, _ = run(self.script)
        self.assertEqual(status, 0)
        lines = out.decode("utf-8").split("\n")
        self.assertEqual(lines[2], "- 0. Drafts: The draft specs, in plain prose; written by: People; "
                                   "repository: `<project>-drafts`")
        self.assertEqual(lines[7], "The modules of the app, each one a plugin, and where each is installed:")

    def test_no_rule_restated(self):
        """MTH-7: besides the rows of the two tables, only the fixed lines, the paths and the URL."""
        shutil.copy(LAYERS, os.path.join(self.root, "specs", "layers.md"))
        _, out, _ = run(self.script)
        lines = out.decode("utf-8").split("\n")
        self.assertEqual(lines[-1], "")
        self.assertEqual(len(lines) - 1, 2 + 5 + 1 + 8 + 5)  # header, five layers, the eight rows of APP-6, the documents
        self.assertNotRegex(out.decode("utf-8"), r"(LAY|ORC|MTH|FLW)-\d")


class Failure(Base):
    def test_missing(self):
        """MTH-8: no layers.md."""
        self.assert_fails()

    def test_not_utf8(self):
        """MTH-8: layers.md is not UTF-8."""
        self.write_layers(b"\xff\xfe" + TABLE.encode("utf-16-le"))
        self.assert_fails()

    def test_no_table_of_layers(self):
        """MTH-8: no table with the four columns of the layers, in their order."""
        self.write_layers("| Layer | Holds | Recommended name | Written by |\n|---|---|---|---|\n| a | b | c | d |\n\n"
                          + MODULES_TABLE)
        self.assert_fails()

    def test_no_table_of_modules(self):
        """MTH-8: no table with the columns Module and Where."""
        self.write_layers(LAYERS_TABLE)
        self.assert_fails()

    def test_no_row_of_layers(self):
        """MTH-8: the table of layers has no row."""
        self.write_layers(LAYERS_TABLE.split("\n", 2)[0] + "\n|---|---|---|---|\n\nText.\n\n" + MODULES_TABLE)
        self.assert_fails()

    def test_no_row_of_modules(self):
        """MTH-8: the table of modules has no row."""
        self.write_layers(LAYERS_TABLE + "\n| Module | Where |\n|---|---|\n\nText.\n")
        self.assert_fails()


class InstalledPlugin(unittest.TestCase):
    def test_real_plugin(self):
        """MTH-6, MTH-10: the installed plugin prints its index, and every path it names exists."""
        status, out, err = run(SCRIPT)
        self.assertEqual((status, err), (0, b""))
        text = out.decode("utf-8")
        paths = re.findall(r": (/\S+)$", text, re.M)
        self.assertEqual(len(paths), 3)
        for path in paths:
            self.assertTrue(os.path.isfile(path), path)
            self.assertTrue(path.startswith(PLUGIN + "/"), path)
        self.assertTrue(text.endswith(": %s\n" % APP_URL))
        local = os.path.join(REPO, APP_URL.split("/blob/main/", 1)[1])
        self.assertTrue(os.path.isfile(local), local)

    def test_hook_declaration(self):
        """MTH-4, MTH-5: one SessionStart hook, no matcher, that runs scripts/index.py, and nothing else."""
        with open(HOOKS, encoding="utf-8") as f:
            hooks = json.load(f)
        self.assertEqual(list(hooks), ["hooks"])
        self.assertEqual(list(hooks["hooks"]), ["SessionStart"])
        groups = hooks["hooks"]["SessionStart"]
        self.assertEqual(len(groups), 1)
        self.assertNotIn("matcher", groups[0])
        self.assertEqual(len(groups[0]["hooks"]), 1)
        hook = groups[0]["hooks"][0]
        self.assertEqual(hook["type"], "command")
        self.assertIn('"${CLAUDE_PLUGIN_ROOT}/scripts/index.py"', hook["command"])

    def test_no_skill(self):
        """MTH-4: the plugin has no use case and no skill."""
        self.assertFalse(os.path.exists(os.path.join(PLUGIN, "use-cases")))
        self.assertFalse(os.path.exists(os.path.join(PLUGIN, "skills")))
        with open(os.path.join(PLUGIN, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
            self.assertNotIn("skills", json.load(f))


if __name__ == "__main__":
    unittest.main()
