"""Tests of scripts/deny_code_repositories.py, the PreToolUse hook of acceptance-management.

Spec: specs/module.md, ACU-38, ACU-40, ACU-45 and ACU-46 (and ACU-13, level 1). Run with:

    python3 -m unittest discover -s apps/indra-software-factory/modules/acceptance-management/tests
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

PLUGIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(PLUGIN, "scripts", "deny_code_repositories.py")
HOOKS = os.path.join(PLUGIN, "hooks", "hooks.json")

sys.dont_write_bytecode = True  # no __pycache__ inside the plugin


def project(code_paths=("billing-api", "billing-web"), acceptance_path="billing-acceptance"):
    repositories = [
        {"owner": "acme", "name": "billing-drafts", "layer": 0, "path": "billing-drafts"},
        {"owner": "acme", "name": "billing-specs", "layer": 1, "path": "billing-specs"},
        {"owner": "acme", "name": "billing-norms", "layer": 2, "path": "billing-norms"},
        {"owner": "acme", "name": "billing-acceptance", "layer": 3, "path": acceptance_path},
    ]
    for path in code_paths:
        name = path.split("/")[-1]
        repositories.append({"owner": "acme", "name": name, "layer": 4,
                             "component": name.split("-")[-1], "path": path})
    return {"project": "billing", "repositories": repositories}


class Hook(unittest.TestCase):
    def setUp(self):
        self.folder = os.path.realpath(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.folder)
        self.make(project())

    def make(self, data, acceptance_path="billing-acceptance",
             remote="git@github.com:acme/billing-acceptance.git", write_project=True):
        self.acceptance = os.path.join(self.folder, *acceptance_path.split("/"))
        os.makedirs(self.acceptance, exist_ok=True)
        subprocess.run(["git", "init", "-q", self.acceptance], check=True)
        if remote:
            subprocess.run(["git", "-C", self.acceptance, "remote", "remove", "origin"], capture_output=True)
            subprocess.run(["git", "-C", self.acceptance, "remote", "add", "origin", remote], check=True)
        if write_project:
            with open(os.path.join(self.acceptance, "project.json"), "w") as f:
                f.write(data if isinstance(data, str) else json.dumps(data))
        if isinstance(data, dict):
            for entry in data["repositories"]:
                if entry["layer"] == 4:
                    os.makedirs(os.path.join(self.folder, *entry["path"].split("/")), exist_ok=True)

    def run_hook(self, tool, tool_input, cwd=None, project_dir=None):
        event = {"hook_event_name": "PreToolUse", "tool_name": tool,
                 "tool_input": tool_input, "cwd": cwd or self.acceptance}
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
        if project_dir:
            env["CLAUDE_PROJECT_DIR"] = project_dir
        done = subprocess.run([sys.executable, "-I", SCRIPT], input=json.dumps(event),
                              capture_output=True, text=True, env=env)
        self.assertEqual(done.returncode, 0, done.stderr)
        return done.stdout

    def assertDenied(self, out):
        self.assertTrue(out.strip(), "the call was not refused")
        decision = json.loads(out)["hookSpecificOutput"]
        self.assertEqual(decision["hookEventName"], "PreToolUse")
        self.assertEqual(decision["permissionDecision"], "deny")
        self.assertIn("ACU-12", decision["permissionDecisionReason"])

    def assertAllowed(self, out):
        self.assertEqual(out, "")

    def api(self, *parts):
        return os.path.join(self.folder, "billing-api", *parts)

    # ACU-38: the file tools

    def test_read_of_a_code_repository_is_refused(self):
        self.assertDenied(self.run_hook("Read", {"file_path": self.api("main.py")}))

    def test_edit_and_write_of_a_code_repository_are_refused(self):
        self.assertDenied(self.run_hook("Edit", {"file_path": self.api("main.py"),
                                                 "old_string": "a", "new_string": "b"}))
        self.assertDenied(self.run_hook("Write", {"file_path": os.path.join(
            self.folder, "billing-web", "new.py"), "content": "x"}))

    def test_the_code_repository_itself_is_refused(self):
        self.assertDenied(self.run_hook("Read", {"file_path": self.api()}))

    def test_relative_path_is_refused(self):
        self.assertDenied(self.run_hook("Read", {"file_path": "../billing-api/main.py"}))

    def test_symbolic_link_into_a_code_repository_is_refused(self):
        os.symlink(self.api(), os.path.join(self.acceptance, "link"))
        self.assertDenied(self.run_hook("Read", {"file_path": os.path.join(self.acceptance, "link", "x")}))

    def test_acceptance_repository_is_allowed(self):
        self.assertAllowed(self.run_hook("Read", {"file_path": os.path.join(self.acceptance, "units", "AU-1.md")}))
        self.assertAllowed(self.run_hook("Write", {"file_path": os.path.join(self.acceptance, "tests", "x.py"),
                                                   "content": "x"}))

    def test_a_sibling_with_a_longer_name_is_allowed(self):
        self.assertAllowed(self.run_hook("Read", {"file_path": os.path.join(self.folder, "billing-api2", "x")}))

    def test_layers_0_to_2_are_not_this_hooks_concern(self):
        self.assertAllowed(self.run_hook("Read", {"file_path": os.path.join(self.folder, "billing-norms", "x.md")}))

    # ACU-38 and ACU-46: Bash

    def test_bash_with_an_absolute_path_is_refused(self):
        self.assertDenied(self.run_hook("Bash", {"command": "cat %s" % self.api("main.py")}))

    def test_bash_with_a_relative_path_is_refused(self):
        self.assertDenied(self.run_hook("Bash", {"command": "ls ../billing-web && echo done"}))

    def test_bash_with_a_quoted_or_assigned_path_is_refused(self):
        self.assertDenied(self.run_hook("Bash", {"command": "grep -r x '../billing-api/src'"}))
        self.assertDenied(self.run_hook("Bash", {"command": "PRODUCT=../billing-api/bin/app pytest"}))

    def test_bash_with_a_glob_is_refused(self):
        self.assertDenied(self.run_hook("Bash", {"command": "cat ../billing-a*/main.py"}))
        self.assertDenied(self.run_hook("Bash", {"command": "ls ../*"}))
        self.assertAllowed(self.run_hook("Bash", {"command": "ls tests/*.py ../billing-n*"}))

    def test_bash_inside_the_acceptance_repository_is_allowed(self):
        self.assertAllowed(self.run_hook("Bash", {"command": "pytest tests/AU-1 && git status"}))

    def test_bash_naming_a_longer_sibling_is_allowed(self):
        self.assertAllowed(self.run_hook("Bash", {"command": "ls %s-old" % self.api()}))

    # ACU-38: NotebookEdit, Grep and Glob

    def test_notebook_edit_of_a_code_repository_is_refused(self):
        self.assertDenied(self.run_hook("NotebookEdit", {"notebook_path": self.api("n.ipynb"),
                                                         "new_source": "x"}))
        self.assertAllowed(self.run_hook("NotebookEdit", {"notebook_path": os.path.join(
            self.acceptance, "n.ipynb"), "new_source": "x"}))

    def test_grep_in_a_code_repository_is_refused(self):
        self.assertDenied(self.run_hook("Grep", {"pattern": "def ", "path": self.api()}))
        self.assertDenied(self.run_hook("Grep", {"pattern": "def ", "path": "../billing-web/src"}))
        self.assertAllowed(self.run_hook("Grep", {"pattern": "billing-api", "path": "tests"}))
        self.assertAllowed(self.run_hook("Grep", {"pattern": "def "}))

    def test_grep_over_a_folder_that_holds_a_code_repository_is_refused(self):
        self.assertDenied(self.run_hook("Grep", {"pattern": "def ", "path": ".."}))
        self.assertDenied(self.run_hook("Grep", {"pattern": "def ", "path": self.folder}))
        self.assertDenied(self.run_hook("Grep", {"pattern": "def ", "path": "/"}))
        self.assertAllowed(self.run_hook("Grep", {"pattern": "def ", "path": "."}))

    def test_bash_recursive_reader_over_a_folder_that_holds_a_code_repository_is_refused(self):
        for command in ("grep -r invoice ..", "grep -rn invoice ..", "grep --recursive x ..",
                        "egrep -R x " + self.folder, "rg invoice ..", "find .. -name '*.py'",
                        "tree ..", "cd tests && rg x ../.."):
            self.assertDenied(self.run_hook("Bash", {"command": command}))
        for command in ("ls ..", "grep invoice ../README.md", "grep -r invoice tests",
                        "rg invoice .", "find . -name '*.py'", "grep -i x ..",
                        "grep --include=x y .."):
            self.assertAllowed(self.run_hook("Bash", {"command": command}))

    def test_glob_in_a_code_repository_is_refused(self):
        self.assertDenied(self.run_hook("Glob", {"pattern": "*", "path": self.api()}))
        self.assertDenied(self.run_hook("Glob", {"pattern": "../billing-api/**/*.py"}))
        self.assertDenied(self.run_hook("Glob", {"pattern": self.api("src", "*.py")}))
        self.assertDenied(self.run_hook("Glob", {"pattern": "billing-a*/**", "path": self.folder}))
        self.assertDenied(self.run_hook("Glob", {"pattern": "src/*.py", "path": "../billing-web"}))
        self.assertAllowed(self.run_hook("Glob", {"pattern": "**/*.py"}))
        self.assertAllowed(self.run_hook("Glob", {"pattern": "billing-n*/**", "path": self.folder}))
        self.assertDenied(self.run_hook("Glob", {"pattern": "**/*.py", "path": self.folder}))

    def test_a_shell_pattern_in_a_field_path_is_refused(self):  # ACU-45
        self.assertDenied(self.run_hook("Read", {"file_path": "../billing-a*/main.py"}))
        self.assertAllowed(self.run_hook("Read", {"file_path": "../billing-n*/x.md"}))

    def test_other_tools_are_allowed(self):
        self.assertAllowed(self.run_hook("WebFetch", {"url": "file://" + self.api("main.py")}))

    # ACU-45, ORC-20 and ORC-21: where the repositories are

    def test_nested_paths(self):
        shutil.rmtree(self.acceptance)
        self.make(project(code_paths=("code/billing-api",), acceptance_path="layers/billing-acceptance"),
                  acceptance_path="layers/billing-acceptance")
        self.assertDenied(self.run_hook("Read", {"file_path": os.path.join(self.folder, "code", "billing-api", "x")}))
        self.assertAllowed(self.run_hook("Read", {"file_path": os.path.join(self.folder, "layers", "x")}))

    def test_one_code_repository_without_component(self):
        data = project(code_paths=())
        data["repositories"].append({"owner": "acme", "name": "billing-code", "layer": 4, "path": "billing-code"})
        self.make(data)
        self.assertDenied(self.run_hook("Read", {"file_path": os.path.join(self.folder, "billing-code", "x")}))

    def test_https_remote(self):
        subprocess.run(["git", "-C", self.acceptance, "remote", "set-url", "origin",
                        "https://github.com/acme/billing-acceptance"], check=True)
        self.assertDenied(self.run_hook("Read", {"file_path": self.api("main.py")}))

    def test_from_a_subfolder(self):
        sub = os.path.join(self.acceptance, "tests")
        os.makedirs(sub)
        self.assertDenied(self.run_hook("Read", {"file_path": "../../billing-api/x"}, cwd=sub))

    # ACU-38: the repository of the session is CLAUDE_PROJECT_DIR, or else cwd

    def test_project_dir_with_cwd_outside_the_repository(self):
        plain = os.path.realpath(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, plain)
        self.assertDenied(self.run_hook("Read", {"file_path": self.api("main.py")},
                                        cwd=plain, project_dir=self.acceptance))
        self.assertDenied(self.run_hook("Bash", {"command": "cat %s" % self.api("main.py")},
                                        cwd=plain, project_dir=self.acceptance))
        self.assertAllowed(self.run_hook("Read", {"file_path": os.path.join(plain, "x")},
                                         cwd=plain, project_dir=self.acceptance))

    def test_relative_paths_resolve_against_cwd_not_project_dir(self):
        sub = os.path.join(self.acceptance, "tests")
        os.makedirs(sub)
        self.assertDenied(self.run_hook("Read", {"file_path": "../../billing-api/x"},
                                        cwd=sub, project_dir=self.acceptance))
        self.assertAllowed(self.run_hook("Read", {"file_path": "../billing-api/x"},
                                         cwd=sub, project_dir=self.acceptance))

    # ACU-40: when the paths cannot be found, the hook refuses nothing

    def test_no_project_json_refuses_nothing(self):
        os.remove(os.path.join(self.acceptance, "project.json"))
        self.assertAllowed(self.run_hook("Read", {"file_path": self.api("main.py")}))

    def test_invalid_project_json_refuses_nothing(self):
        with open(os.path.join(self.acceptance, "project.json"), "w") as f:
            f.write("{not json")
        self.assertAllowed(self.run_hook("Read", {"file_path": self.api("main.py")}))

    def test_no_matching_remote_refuses_nothing(self):
        subprocess.run(["git", "-C", self.acceptance, "remote", "set-url", "origin",
                        "git@github.com:other/repo.git"], check=True)
        self.assertAllowed(self.run_hook("Read", {"file_path": self.api("main.py")}))

    def test_no_remote_refuses_nothing(self):
        subprocess.run(["git", "-C", self.acceptance, "remote", "remove", "origin"], check=True)
        self.assertAllowed(self.run_hook("Read", {"file_path": self.api("main.py")}))

    def test_not_a_git_repository_refuses_nothing(self):
        plain = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, plain)
        self.assertAllowed(self.run_hook("Read", {"file_path": self.api("main.py")}, cwd=plain))

    def test_folder_that_does_not_end_with_its_path_refuses_nothing(self):
        shutil.rmtree(self.acceptance)
        self.make(project(acceptance_path="layers/billing-acceptance"), acceptance_path="elsewhere/billing-acceptance")
        self.assertAllowed(self.run_hook("Read", {"file_path": self.api("main.py")}))

    def test_refusal_reason_word_for_word(self):
        out = self.run_hook("Read", {"file_path": self.api("main.py")})
        self.assertEqual(json.loads(out)["hookSpecificOutput"]["permissionDecisionReason"],
                         "ACU-12 and LAY-8: a session of layer 3 never reads or writes a code repository "
                         "of layer 4, and this call names %s." % self.api())

    def test_bad_input_refuses_nothing(self):
        done = subprocess.run([sys.executable, "-I", SCRIPT], input="not json",
                              capture_output=True, text=True)
        self.assertEqual((done.returncode, done.stdout), (0, ""))

    def test_project_dir_that_is_not_a_project_refuses_nothing(self):
        plain = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, plain)
        self.assertAllowed(self.run_hook("Read", {"file_path": self.api("main.py")}, project_dir=plain))

    # ACU-38 and DEV-7: the declaration of the hook

    def test_hooks_json_declares_the_hook(self):
        with open(HOOKS) as f:
            hooks = json.load(f)["hooks"]
        self.assertEqual(list(hooks), ["PreToolUse"])
        [group] = hooks["PreToolUse"]
        self.assertEqual(set(group["matcher"].split("|")), {"Read", "Edit", "Write", "NotebookEdit", "Grep", "Glob", "Bash"})
        [hook] = group["hooks"]
        self.assertEqual(hook["type"], "command")
        self.assertIn("${CLAUDE_PLUGIN_ROOT}/scripts/deny_code_repositories.py", hook["command"])


if __name__ == "__main__":
    unittest.main()
