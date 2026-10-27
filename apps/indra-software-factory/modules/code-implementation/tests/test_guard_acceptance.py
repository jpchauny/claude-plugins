"""Tests of scripts/guard_acceptance.py, the PreToolUse hook of code-implementation.

Spec: specs/module.md, CIM-1 and CIM-3 to CIM-8. Run with:

    python3 -B -m unittest discover -s apps/indra-software-factory/modules/code-implementation/tests
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

PLUGIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(PLUGIN, "scripts", "guard_acceptance.py")
HOOKS = os.path.join(PLUGIN, "hooks", "hooks.json")

sys.dont_write_bytecode = True  # no __pycache__ inside the plugin

PROJECT = {
    "project": "billing",
    "repositories": [
        {"owner": "acme", "name": "billing-drafts", "layer": 0, "path": "billing-drafts"},
        {"owner": "acme", "name": "billing-specs", "layer": 1, "path": "billing-specs"},
        {"owner": "acme", "name": "billing-norms", "layer": 2, "path": "billing-norms"},
        {"owner": "acme", "name": "billing-acceptance", "layer": 3, "path": "billing-acceptance"},
        {"owner": "acme", "name": "billing-api", "layer": 4, "component": "api", "path": "billing-api"},
        {"owner": "acme", "name": "billing-web", "layer": 4, "component": "web", "path": "billing-web"},
    ],
}


def git(folder, *args):
    subprocess.run(["git", "-C", folder, *args], check=True, capture_output=True)


class GuardTest(unittest.TestCase):
    def setUp(self):
        self.folder = os.path.realpath(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.folder)
        self.code = os.path.join(self.folder, "billing-api")
        self.accept = os.path.join(self.folder, "billing-acceptance")
        for repo, name in ((self.code, "billing-api"), (self.accept, "billing-acceptance")):
            os.makedirs(os.path.join(repo, "units"))
            git(repo, "init", "-q")
            git(repo, "remote", "add", "origin", f"https://github.com/acme/{name}.git")
            with open(os.path.join(repo, "project.json"), "w", encoding="utf-8") as f:
                json.dump(PROJECT, f)

    def run_hook(self, tool, tool_input, cwd=None, env_dir=None, extra_env=None):
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
        env.update(extra_env or {})
        if env_dir:
            env["CLAUDE_PROJECT_DIR"] = env_dir
        data = {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": tool_input,
                "cwd": cwd or self.code}
        result = subprocess.run([sys.executable, "-I", SCRIPT], input=json.dumps(data),
                                capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        if not result.stdout.strip():
            return "allow"
        answer = json.loads(result.stdout)["hookSpecificOutput"]
        self.assertEqual(answer["hookEventName"], "PreToolUse")
        self.assertIn("CIM-1", answer["permissionDecisionReason"])
        return answer["permissionDecision"]

    def bash(self, command, **kw):
        return self.run_hook("Bash", {"command": command}, **kw)

    # CIM-1: the plugin declares one PreToolUse hook for Edit, Write, NotebookEdit and Bash.
    def test_hooks_json(self):
        with open(HOOKS, encoding="utf-8") as f:
            hooks = json.load(f)["hooks"]
        self.assertEqual(list(hooks), ["PreToolUse"])
        self.assertEqual(len(hooks["PreToolUse"]), 1)
        entry = hooks["PreToolUse"][0]
        self.assertEqual(set(entry["matcher"].split("|")), {"Edit", "Write", "NotebookEdit", "Bash"})
        self.assertEqual(entry["hooks"][0]["command"],
                         'python3 -I "${CLAUDE_PLUGIN_ROOT}/scripts/guard_acceptance.py"')

    # CIM-1: Edit and Write of a file of the acceptance repository are refused.
    def test_edit_write_inside_refused(self):
        target = os.path.join(self.accept, "tests", "AU-3", "test_x.py")
        self.assertEqual(self.run_hook("Write", {"file_path": target}), "deny")
        self.assertEqual(self.run_hook("Edit", {"file_path": target}), "deny")
        self.assertEqual(self.run_hook("Edit", {"file_path": "../billing-acceptance/units/AU-3.md"}), "deny")
        self.assertEqual(self.run_hook("NotebookEdit", {"notebook_path": os.path.join(self.accept, "n.ipynb")}), "deny")
        self.assertEqual(self.run_hook("NotebookEdit", {"notebook_path": os.path.join(self.code, "n.ipynb")}), "allow")

    def test_edit_write_outside_allowed(self):
        self.assertEqual(self.run_hook("Write", {"file_path": os.path.join(self.code, "src", "a.py")}), "allow")
        self.assertEqual(self.run_hook("Edit", {"file_path": os.path.join(self.folder, "billing-acceptance-copy", "x")}),
                         "allow")

    # CIM-1: reading the acceptance repository is allowed.
    def test_read_allowed(self):
        self.assertEqual(self.run_hook("Read", {"file_path": os.path.join(self.accept, "units", "AU-3.md")}), "allow")
        for command in (
            "cat ../billing-acceptance/units/AU-3.md",
            f"ls -la {self.accept}/tests",
            f"grep -rn INV-7 {self.accept} | head -5",
            f"git -C {self.accept} log --oneline -3",
            f"git -C {self.accept} archive HEAD | tar -x -C /tmp/copy",
            f"git clone {self.accept} /tmp/acceptance-copy",
            f"cp -R {self.accept} /tmp/acceptance-copy",
            f"find {self.accept}/tests -name '*.py'",
            f"cat {self.accept}/acceptance.json > /tmp/a.json",
            "cd ../billing-acceptance && git status",
            f"git -C {self.accept} diff --output=/tmp/d.patch",
            f"tree -a {self.accept}",
            f"rg -n INV-7 {self.accept}",
            f"less {self.accept}/units/AU-3.md",
            f"git -C {self.accept} grep -n INV-7",
            f"cat {self.accept}/units/AU-3.md 2>&1 | head",
            f"ls {self.accept} >&2",
        ):
            self.assertEqual(self.bash(command), "allow", command)

    # CIM-1: a Bash command that writes a file of the acceptance repository is refused.
    def test_bash_writes_refused(self):
        for command in (
            f"echo x > {self.accept}/units/AU-3.md",
            "echo x >> ../billing-acceptance/tests/AU-3/t.py",
            f"rm -rf {self.accept}/tests",
            f"sed -i '' s/a/b/ {self.accept}/units/AU-3.md",
            f"touch {self.accept}/x",
            f"cp src/a.py {self.accept}/tests/",
            f"mv {self.accept}/units/AU-3.md /tmp/",
            f"git -C {self.accept} commit -am x",
            f"git -C {self.accept} checkout -- .",
            "cd ../billing-acceptance && rm units/AU-3.md",
            "cd ../billing-acceptance; echo x > units/AU-3.md",
            f"find {self.accept} -name '*.py' -delete",
            f"find {self.accept} -name '*.py' | xargs rm",
            f"python3 -m pytest {self.accept}/tests",
            f"cat a | tee {self.accept}/x",
            f"git clone https://github.com/acme/x {self.accept}/x",
            f"echo $(rm -rf {self.accept})",
            "rm -rf $HOME/work/billing-acceptance/tests",
            f"echo 'unbalanced {self.accept}",
            "echo x >| ../billing-acceptance/units/cat",
            "echo x >| ../billing-acceptance/ls",
            "echo x >& ../billing-acceptance/units/AU-3.md",
        ):
            self.assertEqual(self.bash(command), "deny", command)

    # CIM-8: options that make a reading command write a file or run a program.
    def test_bash_write_options_refused(self):
        for command in (
            "git diff --output=../billing-acceptance/x",
            "git log --output ../billing-acceptance/x",
            f"git -C {self.accept} show --output={self.accept}/x HEAD",
            "tree -o ../billing-acceptance/x",
            f"tree -ao /tmp/t {self.accept}",
            f"less -o /tmp/log {self.accept}/units/AU-3.md",
            f"less --log-file=/tmp/log {self.accept}/units/AU-3.md",
            f"rg --pre rm x {self.accept}",
            f"rg --pre=rm x {self.accept}",
            f"file -C -m {self.accept}/magic",
            f"git -C {self.accept} -c core.pager=rm log",
            f"git -C {self.accept} --config-env=core.pager=X log",
            f"git -C {self.accept} grep -Orm x",
            f"git -C {self.accept} grep --open-files-in-pager=rm x",
        ):
            self.assertEqual(self.bash(command), "deny", command)

    # CIM-8: the destination of cp is the value of -t when it has one; rsync -t names no destination.
    def test_cp_target_directory(self):
        for command in (
            f"cp -t /tmp/x {self.accept}/f",
            f"cp --target-directory /tmp/x {self.accept}/f",
            f"cp --target-directory=/tmp/x {self.accept}/f",
            f"cp -at /tmp/x {self.accept}/f",
            f"cp -t/tmp/x {self.accept}/f",
            f"rsync -t {self.accept}/f /tmp/x",
        ):
            self.assertEqual(self.bash(command), "allow", command)
        for command in (
            f"cp -t {self.accept}/tests src/a.py",
            f"cp --target-directory={self.accept} src/a.py",
            f"rsync -t /tmp/src {self.accept}/",
        ):
            self.assertEqual(self.bash(command), "deny", command)

    # CIM-8: with no destination, git clone writes a folder named after the URL in the working directory.
    def test_clone_without_destination(self):
        for command, cwd in (
            ("git clone https://github.com/x/y", self.accept),
            ("git clone https://github.com/x/y.git", self.accept),
            ("cd ../billing-acceptance && git clone https://github.com/x/y", self.code),
            ("cd ../billing-acceptance && git clone -b main https://github.com/x/y", self.code),
            ("git clone https://github.com/acme/x billing-acceptance/x", self.folder),
        ):
            self.assertEqual(self.bash(command, cwd=cwd, env_dir=self.code), "deny", command)
        for command, cwd in (
            (f"git clone {self.accept}", self.code),
            (f"git clone -b main {self.accept}", self.code),
            (f"git clone {self.accept} /tmp/acceptance-copy", self.accept),
        ):
            self.assertEqual(self.bash(command, cwd=cwd), "allow", command)

    def test_bash_outside_allowed(self):
        for command in ("rm -rf build", "python3 -m pytest tests", "echo x > /tmp/y",
                        "cd /tmp/acceptance-copy && PRODUCT_CMD=x make test"):
            self.assertEqual(self.bash(command), "allow", command)

    # CIM-1: with the session inside the acceptance repository, every write is refused.
    def test_cwd_inside(self):
        self.assertEqual(self.bash("rm units/AU-3.md", cwd=self.accept), "deny")
        self.assertEqual(self.bash("cat units/AU-3.md", cwd=self.accept), "allow")
        self.assertEqual(self.bash("cat units/AU-3.md 2>&1", cwd=self.accept), "allow")
        self.assertEqual(self.run_hook("Write", {"file_path": "units/AU-3.md"}, cwd=self.accept), "deny")

    # CIM-1: the path is read from project.json each time the hook runs.
    def test_path_from_project_json(self):
        moved = dict(PROJECT, repositories=[
            dict(e, path="elsewhere") if e["layer"] == 3 else e for e in PROJECT["repositories"]])
        with open(os.path.join(self.code, "project.json"), "w", encoding="utf-8") as f:
            json.dump(moved, f)
        self.assertEqual(self.run_hook("Write", {"file_path": os.path.join(self.accept, "x")}), "allow")
        self.assertEqual(self.run_hook("Write", {"file_path": os.path.join(self.folder, "elsewhere", "x")}), "deny")

    def test_project_dir_env_wins(self):
        self.assertEqual(self.run_hook("Write", {"file_path": os.path.join(self.accept, "x")},
                                       cwd="/", env_dir=self.code), "deny")

    # CIM-5: nothing to guard, so nothing is refused.
    def test_nothing_to_guard_more(self):
        target = {"file_path": os.path.join(self.accept, "x")}
        with open(os.path.join(self.code, "project.json"), "w", encoding="utf-8") as f:
            f.write("{not json")
        self.assertEqual(self.run_hook("Write", target), "allow")
        no_layer3 = dict(PROJECT, repositories=[e for e in PROJECT["repositories"] if e["layer"] != 3])
        with open(os.path.join(self.code, "project.json"), "w", encoding="utf-8") as f:
            json.dump(no_layer3, f)
        self.assertEqual(self.run_hook("Write", target), "allow")
        wrong_path = dict(PROJECT, repositories=[
            dict(e, path="elsewhere/billing-api") if e["name"] == "billing-api" else e
            for e in PROJECT["repositories"]])
        with open(os.path.join(self.code, "project.json"), "w", encoding="utf-8") as f:
            json.dump(wrong_path, f)
        self.assertEqual(self.run_hook("Write", target), "allow")

    # CIM-5: a path that ORC-20 does not allow leaves nothing to guard.
    def test_invalid_path(self):
        target = {"file_path": os.path.join(self.accept, "x")}
        for name, path in (("billing-acceptance", "../billing-acceptance"), ("billing-acceptance", ""),
                           ("billing-api", "./billing-api")):
            bad = dict(PROJECT, repositories=[
                dict(e, path=path) if e["name"] == name else e for e in PROJECT["repositories"]])
            with open(os.path.join(self.code, "project.json"), "w", encoding="utf-8") as f:
                json.dump(bad, f)
            self.assertEqual(self.run_hook("Write", target), "allow", (name, path))

    # CIM-4: the reason of a refusal, word for word.
    def test_reason_text(self):
        data = {"hook_event_name": "PreToolUse", "tool_name": "Write",
                "tool_input": {"file_path": os.path.join(self.accept, "x")}, "cwd": self.code}
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
        result = subprocess.run([sys.executable, "-I", SCRIPT], input=json.dumps(data),
                                capture_output=True, text=True, env=env)
        reason = json.loads(result.stdout)["hookSpecificOutput"]["permissionDecisionReason"]
        self.assertEqual(reason, (
            f"A session of layer 4 never writes the acceptance repository {self.accept} (CIM-1, LAY-4): "
            f"{os.path.join(self.accept, 'x')} is a file of it. "
            "Reading it is allowed; run its acceptance tests in a copy made outside it (IMP-16)."))

    # CIM-1: file_path and notebook_path are resolved as ACU-45 says: ~, environment variables, symbolic links.
    def test_path_resolution(self):
        target = {"file_path": "$ACC_DIR/units/AU-3.md"}
        self.assertEqual(self.run_hook("Write", target, extra_env={"ACC_DIR": self.accept}), "deny")
        self.assertEqual(self.run_hook("Write", {"file_path": "~/units/AU-3.md"}, extra_env={"HOME": self.accept}), "deny")
        link = os.path.join(self.code, "link")
        os.symlink(self.accept, link)
        self.assertEqual(self.run_hook("Edit", {"file_path": "link/units/AU-3.md"}), "deny")
        self.assertEqual(self.run_hook("NotebookEdit", {"notebook_path": os.path.join(link, "n.ipynb")}), "deny")

    # CIM-3, CIM-6: the current directory set by an earlier cd, and xargs after any earlier command that names it.
    def test_names_cases(self):
        self.assertEqual(self.bash("cd ../billing-acceptance; rm units/AU-3.md"), "deny")
        self.assertEqual(self.bash("cd ../billing-acceptance; cd -; cat x"), "allow")
        self.assertEqual(self.bash("cd /tmp && rm units/AU-3.md"), "allow")
        # CIM-3: options of cd are skipped; the first word that is not an option is the directory.
        self.assertEqual(self.bash("cd -P ../billing-acceptance; rm units/AU-3.md"), "deny")
        self.assertEqual(self.bash("cd -- ../billing-acceptance; rm units/AU-3.md"), "deny")
        self.assertEqual(self.bash("cd -L /tmp && rm units/AU-3.md"), "allow")
        self.assertEqual(self.bash(f"find {self.accept} -name '*.py'; echo done | xargs rm"), "deny")
        self.assertEqual(self.bash(f"ls {self.accept} | grep x | xargs rm"), "deny")
        self.assertEqual(self.bash("ls /tmp | xargs rm"), "allow")
        self.assertEqual(self.bash("rm $HOME/billing-acceptance/x"), "deny")

    # CIM-6: the names of the acceptance repository are the last part of its path and of its real path.
    def test_names_through_a_link(self):
        real = os.path.join(self.folder, "real-acceptance")
        os.rename(self.accept, real)
        os.symlink(real, self.accept)
        self.assertEqual(self.bash("rm $HOME/billing-acceptance/x"), "deny")
        self.assertEqual(self.bash("rm $HOME/real-acceptance/x"), "deny")
        self.assertEqual(self.bash("rm $HOME/other/x"), "allow")
        self.assertEqual(self.bash("echo 'unbalanced real-acceptance"), "deny")

    # CIM-4: the reason for Bash quotes the simple command, its words joined by single blanks.
    def test_reason_text_bash(self):
        data = {"hook_event_name": "PreToolUse", "tool_name": "Bash",
                "tool_input": {"command": "rm  -f  \"../billing-acceptance/it's.md\""}, "cwd": self.code}
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
        result = subprocess.run([sys.executable, "-I", SCRIPT], input=json.dumps(data),
                                capture_output=True, text=True, env=env)
        reason = json.loads(result.stdout)["hookSpecificOutput"]["permissionDecisionReason"]
        self.assertIn(": the command 'rm -f ../billing-acceptance/it's.md' may write it. ", reason)

    # Nothing to guard: no project.json, or no entry for the remote origin.
    def test_nothing_to_guard(self):
        os.remove(os.path.join(self.code, "project.json"))
        self.assertEqual(self.run_hook("Write", {"file_path": os.path.join(self.accept, "x")}), "allow")
        with open(os.path.join(self.code, "project.json"), "w", encoding="utf-8") as f:
            json.dump(PROJECT, f)
        git(self.code, "remote", "set-url", "origin", "https://github.com/other/repo.git")
        self.assertEqual(self.run_hook("Write", {"file_path": os.path.join(self.accept, "x")}), "allow")

    def test_not_a_git_repository(self):
        shutil.rmtree(os.path.join(self.code, ".git"))
        self.assertEqual(self.run_hook("Write", {"file_path": os.path.join(self.accept, "x")}), "allow")

    def test_bad_input(self):
        result = subprocess.run([sys.executable, "-I", SCRIPT], input="not json", capture_output=True, text=True)
        self.assertEqual((result.returncode, result.stdout), (0, ""))
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
        for data in ({"tool_name": "Write", "tool_input": "x", "cwd": self.code},
                     {"tool_name": "Write", "tool_input": {"file_path": 3}, "cwd": self.code},
                     {"tool_name": "Bash", "tool_input": {"command": "rm x"}, "cwd": 7}):
            result = subprocess.run([sys.executable, "-I", SCRIPT], input=json.dumps(data),
                                    capture_output=True, text=True, env=env)
            self.assertEqual((result.returncode, result.stdout, result.stderr), (0, "", ""), data)


if __name__ == "__main__":
    unittest.main()
