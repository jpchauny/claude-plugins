"""Tests of use-cases/sync/scripts/plan.py.

Spec: use-cases/sync/specs/sync.md (ORC-28, ORC-30, SNC-1, SNC-2, SNC-3). Each test names the clause
it checks. Run with:

    python3 -m unittest discover -s apps/indra-software-factory/modules/project-management/tests
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

PLUGIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(PLUGIN, "use-cases", "sync", "scripts", "plan.py")

sys.dont_write_bytecode = True

ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t",
           GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null")

LAYERS = [("billing-drafts", 0), ("billing-specs", 1), ("billing-norms", 2),
          ("billing-acceptance", 3), ("billing-code", 4)]
DENY = {"billing-acceptance": ["Read(//**/billing-code/**)", "Edit(//**/billing-code/**)"],
        "billing-code": ["Edit(//**/billing-acceptance/**)"]}


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, env=ENV, capture_output=True, text=True, check=True)


class Plan(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.folder = self.tmp.name
        repos = [{"owner": "acme", "name": n, "layer": l, "path": n} for n, l in LAYERS]
        self.source = json.dumps({"project": "billing", "repositories": repos}, indent=2) + "\n"
        for name, _ in LAYERS:
            self.make_repo(name, self.source, DENY.get(name))

    def make_repo(self, name, project_json, deny=None):
        path = os.path.join(self.folder, name)
        os.makedirs(os.path.join(path, ".claude"))
        git(path, "init", "-q", "-b", "main")
        git(path, "remote", "add", "origin", f"https://github.com/acme/{name}")
        with open(os.path.join(path, "project.json"), "w", encoding="utf-8") as f:
            f.write(project_json)
        settings = {"enabledPlugins": {"utilities@indra-software-factory": True}}
        if deny is not None:
            settings["permissions"] = {"deny": deny}
        with open(os.path.join(path, ".claude", "settings.json"), "w", encoding="utf-8") as f:
            f.write(json.dumps(settings, indent=2) + "\n")
        git(path, "add", "project.json", ".claude/settings.json")
        git(path, "commit", "-q", "-m", "start")

    def change_source(self, repos):
        source = json.dumps({"project": "billing", "repositories": repos}, indent=2) + "\n"
        path = os.path.join(self.folder, "billing-specs")
        with open(os.path.join(path, "project.json"), "w", encoding="utf-8") as f:
            f.write(source)
        git(path, "commit", "-q", "-am", "change")
        return source

    def tearDown(self):
        self.tmp.cleanup()

    def plan(self, name):
        r = subprocess.run([sys.executable, "-I", SCRIPT, "--repo", os.path.join(self.folder, name)],
                           env=ENV, capture_output=True, text=True)
        out = json.loads(r.stdout)
        if "source_file" in out:
            os.unlink(out["source_file"])
        self.settings_files = {}
        for t in out.get("targets", []):
            if "settings_file" in t:
                with open(t["settings_file"], encoding="utf-8") as f:
                    self.settings_files[t["name"]] = json.load(f)
                os.unlink(t["settings_file"])
        return r.returncode, out

    def test_orc28_refused_outside_layer_1(self):
        for name, layer in LAYERS:
            if layer == 1:
                continue
            code, out = self.plan(name)
            self.assertEqual(code, 1, name)
            self.assertEqual(out["layer"], layer)

    def test_orc30_every_layer_is_a_target(self):
        with open(os.path.join(self.folder, "billing-code", "project.json"), "w", encoding="utf-8") as f:
            f.write("{}\n")
        git(os.path.join(self.folder, "billing-code"), "commit", "-q", "-am", "old")
        code, out = self.plan("billing-specs")
        self.assertEqual(code, 0)
        states = {t["name"]: t["state"] for t in out["targets"]}
        self.assertEqual(states, {"acme/billing-drafts": "same", "acme/billing-norms": "same",
                                  "acme/billing-acceptance": "same", "acme/billing-code": "differs"})


    def test_snc1_rules_in_step_report_same(self):
        code, out = self.plan("billing-specs")
        self.assertEqual(code, 0)
        states = {t["name"]: t.get("settings_state") for t in out["targets"]}
        self.assertEqual(states, {"acme/billing-drafts": None, "acme/billing-norms": None,
                                  "acme/billing-acceptance": "same", "acme/billing-code": "same"})

    def test_snc1_a_repository_of_layer_4_is_added(self):
        repos = [{"owner": "acme", "name": n, "layer": l, "path": n} for n, l in LAYERS]
        repos.append({"owner": "acme", "name": "billing-code-mobile", "layer": 4, "path": "billing-code-mobile"})
        source = self.change_source(repos)
        self.make_repo("billing-code-mobile", source, deny=None)
        code, out = self.plan("billing-specs")
        self.assertEqual(code, 0)
        by = {t["name"]: t for t in out["targets"]}
        self.assertEqual(by["acme/billing-acceptance"]["settings_state"], "differs")
        self.assertEqual(self.settings_files["acme/billing-acceptance"]["permissions"]["deny"], [
            "Read(//**/billing-code/**)", "Edit(//**/billing-code/**)",
            "Read(//**/billing-code-mobile/**)", "Edit(//**/billing-code-mobile/**)",
        ])
        self.assertEqual(self.settings_files["acme/billing-acceptance"]["enabledPlugins"],
                         {"utilities@indra-software-factory": True})
        self.assertEqual(by["acme/billing-code-mobile"]["settings_state"], "differs")
        self.assertEqual(self.settings_files["acme/billing-code-mobile"]["permissions"]["deny"],
                         ["Edit(//**/billing-acceptance/**)"])
        self.assertEqual(by["acme/billing-code"]["settings_state"], "same")

    def test_snc1_a_repository_of_layer_4_is_removed_and_a_persons_rule_is_kept(self):
        repos = [{"owner": "acme", "name": n, "layer": l, "path": n} for n, l in LAYERS if l != 4]
        repos.append({"owner": "acme", "name": "billing-code-api", "layer": 4, "component": "api", "path": "billing-code-api"})
        self.change_source(repos)
        path = os.path.join(self.folder, "billing-acceptance", ".claude", "settings.json")
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        data["permissions"]["deny"] += ["Bash(rm -rf *)", "Bash(rm -rf billing-code/tmp)"]
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps(data, indent=2) + "\n")
        git(os.path.join(self.folder, "billing-acceptance"), "commit", "-q", "-am", "person")
        code, out = self.plan("billing-specs")
        self.assertEqual(code, 0)
        self.assertEqual(self.settings_files["acme/billing-acceptance"]["permissions"]["deny"], [
            "Read(//**/billing-code-api/**)", "Edit(//**/billing-code-api/**)",
            "Bash(rm -rf *)", "Bash(rm -rf billing-code/tmp)",
        ])

    def test_snc1_a_removed_repository_whose_rules_were_skipped_once(self):
        repos = [{"owner": "acme", "name": n, "layer": l, "path": n} for n, l in LAYERS if l != 4]
        repos.append({"owner": "acme", "name": "billing-code-api", "layer": 4, "component": "api", "path": "billing-code-api"})
        source = self.change_source(repos)
        acceptance = os.path.join(self.folder, "billing-acceptance")
        # A first sync wrote project.json, and skipped the uncommitted settings.
        with open(os.path.join(acceptance, "project.json"), "w", encoding="utf-8") as f:
            f.write(source)
        git(acceptance, "commit", "-q", "-am", "chore: sync project.json")
        with open(os.path.join(acceptance, ".claude", "settings.json"), "a", encoding="utf-8") as f:
            f.write(" ")
        git(acceptance, "commit", "-q", "-am", "person")
        code, out = self.plan("billing-specs")
        self.assertEqual(code, 0)
        by = {t["name"]: t for t in out["targets"]}
        self.assertEqual(by["acme/billing-acceptance"]["state"], "same")
        self.assertEqual(self.settings_files["acme/billing-acceptance"]["permissions"]["deny"], [
            "Read(//**/billing-code-api/**)", "Edit(//**/billing-code-api/**)",
        ])

    def test_snc1_a_persons_rule_of_the_same_shape_is_kept(self):
        repos = [{"owner": "acme", "name": n, "layer": l, "path": n} for n, l in LAYERS if l != 4]
        repos.append({"owner": "acme", "name": "billing-code-api", "layer": 4, "component": "api", "path": "billing-code-api"})
        self.change_source(repos)
        path = os.path.join(self.folder, "billing-acceptance", ".claude", "settings.json")
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        data["permissions"]["deny"].append("Read(//**/secrets/**)")
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps(data, indent=2) + "\n")
        git(os.path.join(self.folder, "billing-acceptance"), "commit", "-q", "-am", "person")
        code, out = self.plan("billing-specs")
        self.assertEqual(code, 0)
        self.assertEqual(self.settings_files["acme/billing-acceptance"]["permissions"]["deny"], [
            "Read(//**/billing-code-api/**)", "Edit(//**/billing-code-api/**)", "Read(//**/secrets/**)",
        ])

    def test_snc1_uncommitted_settings_are_skipped(self):
        path = os.path.join(self.folder, "billing-code", ".claude", "settings.json")
        with open(path, "a", encoding="utf-8") as f:
            f.write(" ")
        code, out = self.plan("billing-specs")
        by = {t["name"]: t for t in out["targets"]}
        self.assertEqual(by["acme/billing-code"]["settings_state"], "skipped")
        self.assertIn("uncommitted", by["acme/billing-code"]["settings_reason"])

    def test_snc1_a_rule_that_is_not_a_string_is_skipped(self):
        path = os.path.join(self.folder, "billing-code", ".claude", "settings.json")
        with open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps({"permissions": {"deny": [1]}}) + "\n")
        git(os.path.join(self.folder, "billing-code"), "commit", "-q", "-am", "typo")
        code, out = self.plan("billing-specs")
        self.assertEqual(code, 0)
        by = {t["name"]: t for t in out["targets"]}
        self.assertEqual(by["acme/billing-code"]["settings_state"], "skipped")
        self.assertIn("not a JSON object of Claude Code", by["acme/billing-code"]["settings_reason"])

    def write_settings(self, text):
        path = os.path.join(self.folder, "billing-code", ".claude", "settings.json")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        git(os.path.join(self.folder, "billing-code"), "commit", "-q", "-am", "settings")

    def settings_of_code(self):
        code, out = self.plan("billing-specs")
        self.assertEqual(code, 0)
        return {t["name"]: t for t in out["targets"]}["acme/billing-code"]

    def test_snc1_missing_settings_are_skipped(self):
        git(os.path.join(self.folder, "billing-code"), "rm", "-q", ".claude/settings.json")
        git(os.path.join(self.folder, "billing-code"), "commit", "-q", "-m", "remove")
        t = self.settings_of_code()
        self.assertEqual((t["settings_state"], t["settings_reason"]), ("skipped", "no .claude/settings.json"))

    def test_snc1_settings_of_the_wrong_form_are_skipped(self):
        for text in ("{not json\n", "[]\n", '{"permissions": []}\n', '{"permissions": {"deny": "x"}}\n'):
            self.write_settings(text)
            t = self.settings_of_code()
            self.assertEqual((t["settings_state"], t["settings_reason"]),
                             ("skipped", ".claude/settings.json is not a JSON object of Claude Code"), text)

    def test_snc1_settings_without_deny_get_the_rules(self):
        for data in ({"enabledPlugins": {"utilities@indra-software-factory": True}},
                     {"enabledPlugins": {"utilities@indra-software-factory": True}, "permissions": {"ask": ["Bash(x)"]}}):
            self.write_settings(json.dumps(data) + "\n")
            t = self.settings_of_code()
            self.assertEqual(t["settings_state"], "differs")
            got = self.settings_files["acme/billing-code"]
            self.assertEqual(got["permissions"]["deny"], ["Edit(//**/billing-acceptance/**)"])
            self.assertEqual(got["enabledPlugins"], data["enabledPlugins"])
            self.assertEqual(got["permissions"].get("ask"), data.get("permissions", {}).get("ask"))

    def with_roles(self):
        """The source with the orchestration repository and the tooling repository (ORC-20), each a clone."""
        repos = [{"owner": "acme", "name": n, "layer": l, "path": n} for n, l in LAYERS]
        repos += [{"owner": "acme", "name": "billing-orchestration", "role": "orchestration", "path": "billing-orchestration"},
                  {"owner": "acme", "name": "billing-tooling", "role": "tooling", "path": "billing-tooling"}]
        source = self.change_source(repos)
        self.make_repo("billing-orchestration", "{}\n")
        self.make_repo("billing-tooling", "{}\n")
        return repos, source

    def test_snc2_snc3_the_repositories_with_a_role_are_targets_of_project_json_only(self):
        self.with_roles()
        code, out = self.plan("billing-specs")
        self.assertEqual(code, 0, out)
        targets = {t["name"]: t for t in out["targets"]}
        for name in ("acme/billing-orchestration", "acme/billing-tooling"):
            self.assertEqual(targets[name]["state"], "differs", name)
            self.assertNotIn("settings_state", targets[name], name)
        self.assertEqual(targets["acme/billing-acceptance"]["settings_state"], "same")

    def test_orc28_refused_in_a_repository_with_a_role(self):
        self.with_roles()
        for name in ("billing-orchestration", "billing-tooling"):
            path = os.path.join(self.folder, name)
            with open(os.path.join(self.folder, "billing-specs", "project.json"), encoding="utf-8") as f:
                source = f.read()
            with open(os.path.join(path, "project.json"), "w", encoding="utf-8") as f:
                f.write(source)
            git(path, "commit", "-q", "-am", "sync")
            code, out = self.plan(name)
            self.assertEqual(code, 1, name)
            self.assertEqual(out["error"], "sync runs only in the repository of layer 1 (ORC-28)", name)

    def test_snc3_a_source_whose_roles_do_not_have_the_form_of_orc_20(self):
        base = [{"owner": "acme", "name": n, "layer": l, "path": n} for n, l in LAYERS]
        tooling = {"owner": "acme", "name": "billing-tooling", "role": "tooling", "path": "billing-tooling"}
        for extra in ([dict(tooling, layer=2)], [tooling, dict(tooling, name="other-tooling", path="other-tooling")],
                      [dict(tooling, role="builder")]):
            self.change_source(base + extra)
            code, out = self.plan("billing-specs")
            self.assertEqual(code, 1, extra)
            self.assertEqual(out["error"], "project.json at HEAD does not have the form of ORC-20", extra)


if __name__ == "__main__":
    unittest.main()
