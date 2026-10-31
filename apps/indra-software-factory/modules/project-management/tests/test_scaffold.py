"""Tests of use-cases/create-project/scripts/scaffold.py.

Specs: specs/module.md (ORC-20) and use-cases/create-project/specs/create-project.md
(ORC-2, ORC-5, CRP-1, CRP-2, CRP-4). Each test names the clause it checks. Run with:

    python3 -m unittest discover -s apps/indra-software-factory/modules/project-management/tests
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

PLUGIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(PLUGIN, "use-cases", "create-project", "scripts", "scaffold.py")

sys.dont_write_bytecode = True

ASK = ["Bash(git commit *)", "Bash(git push *)", "Bash(git * commit *)", "Bash(git * push *)"]
MODULE = {
    0: "specs-management",
    1: "specs-management",
    2: "norms-management",
    3: "acceptance-management",
    4: "code-implementation",
    "orchestration": "workflow-orchestration",
}
ROLES = [("billing-orchestration", "orchestration"), ("billing-tooling", "tooling")]


def scaffold(folder, *extra):
    return subprocess.run(
        [sys.executable, "-I", SCRIPT, "--project", "billing", "--owner", "acme", "--folder", folder,
         *([] if "--profile" in extra else ["--profile", "product"]), *extra],
        capture_output=True, text=True,
    )


class Scaffold(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.folder = os.path.join(os.path.realpath(self.tmp.name), "billing")

    def tearDown(self):
        self.tmp.cleanup()

    def project_json(self, name):
        with open(os.path.join(self.folder, name, "project.json"), encoding="utf-8") as f:
            return f.read()

    def settings(self, name):
        with open(os.path.join(self.folder, name, ".claude", "settings.json"), encoding="utf-8") as f:
            return json.load(f)

    def test_orc5_crp4_no_component_gives_five_layers_the_orchestration_and_the_tooling_repository(self):
        r = scaffold(self.folder)
        self.assertEqual(r.returncode, 0, r.stderr)
        heads = [line for line in r.stdout.splitlines() if not line.startswith("/")]
        self.assertEqual(heads, ["0 billing-drafts", "1 billing-specs", "2 billing-norms",
                                 "3 billing-acceptance", "4 billing-code",
                                 "orchestration billing-orchestration", "tooling billing-tooling"])

    def test_orc20_project_json_same_bytes_and_form(self):
        self.assertEqual(scaffold(self.folder).returncode, 0)
        names = ["billing-drafts", "billing-specs", "billing-norms", "billing-acceptance", "billing-code"]
        texts = {self.project_json(n) for n in names + [name for name, _ in ROLES]}
        self.assertEqual(len(texts), 1)
        data = json.loads(texts.pop())
        self.assertEqual(data["project"], "billing")
        self.assertEqual(list(data), ["project", "repositories"])  # no derived_norms (ORC-5)
        self.assertEqual([(r["name"], r.get("layer"), r.get("role")) for r in data["repositories"]],
                         [(n, l, None) for n, l in zip(names, [0, 1, 2, 3, 4])]
                         + [(n, None, role) for n, role in ROLES])
        for r in data["repositories"]:
            self.assertEqual(r["owner"], "acme")
            self.assertEqual(r["path"], r["name"])
            self.assertNotIn("component", r)

    def test_orc20_orc5_components_are_of_layer_4_and_acceptance_is_one(self):
        self.assertEqual(scaffold(self.folder, "--components", "api, web").returncode, 0)
        data = json.loads(self.project_json("billing-acceptance"))
        layers = [(r["name"], r.get("layer"), r.get("component")) for r in data["repositories"]]
        self.assertEqual(layers, [
            ("billing-drafts", 0, None), ("billing-specs", 1, None), ("billing-norms", 2, None),
            ("billing-acceptance", 3, None),
            ("billing-code-api", 4, "api"), ("billing-code-web", 4, "web"),
            ("billing-orchestration", None, None), ("billing-tooling", None, None),
        ])
        self.assertFalse(os.path.exists(os.path.join(self.folder, "billing-code")))

    def test_orc5_modules_of_each_layer(self):
        self.assertEqual(scaffold(self.folder).returncode, 0)
        data = json.loads(self.project_json("billing-code"))
        for r in data["repositories"]:
            if r.get("role") == "tooling":
                continue
            enabled = {k for k, v in self.settings(r["name"])["enabledPlugins"].items() if v}
            self.assertEqual(enabled, {"development-methodology@jpchauny-plugins", "utilities@jpchauny-plugins",
                                       f"{MODULE[r.get('layer', r.get('role'))]}@jpchauny-plugins"}, r["name"])

    def test_orc5_ask_rules_where_a_person_approves_every_change(self):
        self.assertEqual(scaffold(self.folder).returncode, 0)
        for name in ["billing-drafts", "billing-specs", "billing-acceptance"]:
            self.assertEqual(self.settings(name).get("permissions", {}).get("ask"), ASK, name)

    def test_orc5_deny_rules_of_layers_3_and_4(self):
        self.assertEqual(scaffold(self.folder, "--components", "api,web").returncode, 0)
        deny = lambda name: self.settings(name).get("permissions", {}).get("deny")
        self.assertEqual(deny("billing-acceptance"), [
            "Read(//**/billing-code-api/**)", "Edit(//**/billing-code-api/**)",
            "Read(//**/billing-code-web/**)", "Edit(//**/billing-code-web/**)",
        ])
        for name in ["billing-code-api", "billing-code-web"]:
            self.assertEqual(deny(name), ["Edit(//**/billing-acceptance/**)"], name)
        for name in ["billing-drafts", "billing-specs", "billing-norms", "billing-orchestration", "billing-tooling"]:
            self.assertIsNone(deny(name), name)
        self.assertEqual(self.settings("billing-acceptance")["permissions"]["ask"], ASK)

    def test_orc5_deny_rules_without_components(self):
        self.assertEqual(scaffold(self.folder).returncode, 0)
        self.assertEqual(self.settings("billing-acceptance")["permissions"]["deny"],
                         ["Read(//**/billing-code/**)", "Edit(//**/billing-code/**)"])
        self.assertEqual(self.settings("billing-code")["permissions"]["deny"],
                         ["Edit(//**/billing-acceptance/**)"])

    def test_orc5_each_repository_has_claude_md_readme_and_no_placeholder_left(self):
        self.assertEqual(scaffold(self.folder, "--components", "api,web").returncode, 0)
        for name in os.listdir(self.folder):
            for file in ["CLAUDE.md", "README.md"]:
                path = os.path.join(self.folder, name, file)
                self.assertTrue(os.path.isfile(path), path)
                with open(path, encoding="utf-8") as f:
                    text = f.read()
                self.assertNotIn("{{", text, path)
                self.assertNotIn("four layers", text, path)

    def test_lay5_claude_md_of_layers_3_and_4_restate_the_issue_of_an_inconsistency(self):
        # LAY-5 (An inconsistency is fixed in layer 1 first) and ORC-14: the issue is opened
        # once the person confirms its text, and a generator defect goes to the marketplace
        # of the generator's plugin, not to the repository of layer 1.
        self.assertEqual(scaffold(self.folder).returncode, 0)
        for name in ["billing-acceptance", "billing-code"]:
            with open(os.path.join(self.folder, name, "CLAUDE.md"), encoding="utf-8") as f:
                line = next(l for l in f.read().splitlines() if "#rules)" in l and "LAY-5" in l)
            self.assertIn("a derived norm is wrong, missing or contradictory", line, name)
            self.assertIn("open an issue in `acme/billing-specs`, once the person confirms its text", line, name)
            self.assertIn("is a defect of its generator", line, name)
            self.assertIn("in the repository of the marketplace that holds the plugin that `generator`"
                          " of the status file of its type names, not in `acme/billing-specs`", line, name)
            self.assertIn("drift-management/specs/module.md#report-a-drift", line, name)

    def test_lay3_claude_md_of_layer_2_restates_what_regenerates_it(self):
        # LAY-3 (How layer 2 is derived) and NRM-7: layer 2 is regenerated where layer 1
        # changed or where a derived-norms generator has a new version, even with no norm
        # changed; its derived norms are listed with their derived norm ID (NRM-12).
        self.assertEqual(scaffold(self.folder).returncode, 0)
        with open(os.path.join(self.folder, "billing-norms", "CLAUDE.md"), encoding="utf-8") as f:
            text = " ".join(f.read().split())
        self.assertIn("regenerated only where layer 1 or a derived-norms generator changed", text)
        self.assertIn("also when no norm changed", text)
        self.assertNotIn("regenerated only where layer 1 changed", text)
        self.assertIn("specs-derived/<type>/derived-norms.jsonl", text)
        self.assertIn("layers.md#rules", text)

    def test_crp4_the_tooling_repository(self):
        r = scaffold(self.folder, "--components", "api,web")
        self.assertEqual(r.returncode, 0, r.stderr)
        tooling = os.path.join(self.folder, "billing-tooling")
        lines = r.stdout.splitlines()
        files = lines[lines.index("tooling billing-tooling") + 1:]
        self.assertEqual(sorted(os.path.relpath(f, tooling) for f in files),
                         [".claude-plugin/marketplace.json", ".claude/settings.json", "CLAUDE.md", "README.md",
                          "project.json"])
        settings = self.settings("billing-tooling")
        self.assertEqual({k for k, v in settings["enabledPlugins"].items() if v}, {"utilities@jpchauny-plugins"})
        self.assertNotIn("permissions", settings)
        with open(os.path.join(tooling, ".claude-plugin", "marketplace.json"), encoding="utf-8") as f:
            self.assertEqual(f.read(), '{\n  "name": "billing-tooling",\n  "owner": {\n    "name": "acme"\n  },\n'
                                       '  "plugins": []\n}\n')
        with open(os.path.join(tooling, "CLAUDE.md"), encoding="utf-8") as f:
            text = " ".join(f.read().split())
        self.assertIn("The tooling repository of `billing`: no layer.", text)
        self.assertIn("every change starts in a spec, the person approves it", text)
        self.assertIn("/specs/development.md", text)
        self.assertIn('"billing-tooling": {"source": {"source": "github", "repo": "acme/billing-tooling"}}', text)
        self.assertIn('"<plugin>@billing-tooling": true', text)

    def test_crp4_no_layer_installs_the_tooling_repository_when_the_project_is_created(self):
        self.assertEqual(scaffold(self.folder).returncode, 0)
        for name in os.listdir(self.folder):
            with open(os.path.join(self.folder, name, ".claude", "settings.json"), encoding="utf-8") as f:
                self.assertNotIn("billing-tooling", f.read(), name)

    def test_lay13_claude_md_of_layer_2_says_that_nothing_is_written_by_hand(self):
        self.assertEqual(scaffold(self.folder).returncode, 0)
        with open(os.path.join(self.folder, "billing-norms", "CLAUDE.md"), encoding="utf-8") as f:
            text = " ".join(f.read().split())
        self.assertNotIn("generators/", text)
        self.assertIn("plugins of `acme/billing-tooling`", text)

    def test_crp2_acceptance_json_with_the_profile_chosen(self):
        for profile in ("prototype", "product", "critical"):
            folder = os.path.join(os.path.realpath(self.tmp.name), profile)
            r = scaffold(folder, "--profile", profile)
            self.assertEqual(r.returncode, 0, r.stderr)
            path = os.path.join(folder, "billing-acceptance", "acceptance.json")
            self.assertIn(path, r.stdout.splitlines())
            with open(path, encoding="utf-8") as f:
                self.assertEqual(json.load(f), {"default_done_profile": profile, "last_area_id": 0,
                                                "last_unit_id": 0, "last_scenario_id": 0,
                                                "test_command": "", "product": {}})
            for name in ["billing-drafts", "billing-specs", "billing-norms", "billing-code"]:
                self.assertFalse(os.path.exists(os.path.join(folder, name, "acceptance.json")), name)

    def test_crp1_workflow_of_acu34_only_in_the_acceptance_repository(self):
        r = scaffold(self.folder, "--components", "api,web")
        self.assertEqual(r.returncode, 0, r.stderr)
        acceptance = os.path.join(self.folder, "billing-acceptance", ".github", "workflows", "acceptance.yml")
        self.assertIn(acceptance, r.stdout.splitlines())
        with open(acceptance, encoding="utf-8") as f:
            text = f.read()
        events = text[text.index("\non:\n"):text.index("\npermissions:")]
        self.assertIn('  schedule:\n    - cron: "17 * * * *"\n', events)
        self.assertIn("  push:\n    branches: [main]\n", events)
        self.assertIn('"records/**"', events)
        self.assertEqual(re.findall(r"^  (\w+):", events, re.M), ["schedule", "push"])
        self.assertNotIn("repository_dispatch", text)
        self.assertIn("modules/acceptance-management/scripts/acceptance_ci.py", text)
        self.assertIn("${{ secrets.CODE_READ_TOKEN }}", text)
        self.assertNotIn("{{", text.replace("${{", ""))
        for name in ["billing-drafts", "billing-specs", "billing-norms", "billing-code-api", "billing-code-web"]:
            self.assertFalse(os.path.exists(os.path.join(self.folder, name, ".github")), name)

    def test_crp1_layer4_code_runs_without_write_credential_and_full_history(self):
        r = scaffold(self.folder)
        self.assertEqual(r.returncode, 0, r.stderr)
        path = os.path.join(self.folder, "billing-acceptance", ".github", "workflows", "acceptance.yml")
        with open(path, encoding="utf-8") as f:
            text = f.read()
        run = text[text.index("\n  run:\n"):text.index("\n  record:\n")]
        record = text[text.index("\n  record:\n"):]
        self.assertIn("    permissions:\n      contents: read\n", run)
        self.assertNotIn("write", run)
        self.assertEqual(run.count("persist-credentials: false"), run.count("uses: actions/checkout@"))
        self.assertIn("acceptance_ci.py", run)
        self.assertIn("fetch-depth: 0", run[:run.index("Check out the plugin")])
        self.assertIn("    permissions:\n      contents: write\n", record)
        self.assertNotIn("acceptance_ci.py", record)
        self.assertNotIn("CODE_READ_TOKEN", record)
        self.assertIn("Check and take the records", record)
        self.assertIn("permissions:\n  contents: read\n", text[:text.index("\njobs:")])

    def test_crp1_token_reaches_the_script_in_a_file_not_in_its_environment(self):
        r = scaffold(self.folder)
        self.assertEqual(r.returncode, 0, r.stderr)
        path = os.path.join(self.folder, "billing-acceptance", ".github", "workflows", "acceptance.yml")
        with open(path, encoding="utf-8") as f:
            text = f.read()
        steps = re.split(r"\n      - name: ", text[text.index("\n  run:\n"):text.index("\n  record:\n")])[1:]
        named = {s.splitlines()[0]: s for s in steps}
        write = named["Write the token to a file"]
        runner = named["Run the acceptance tests and record them"]
        self.assertIn("CODE_READ_TOKEN: ${{ secrets.CODE_READ_TOKEN }}", write)
        self.assertIn('> "$RUNNER_TEMP/code-read-token"', write)
        self.assertIn("acceptance_ci.py", runner)
        self.assertNotIn("CODE_READ_TOKEN", runner)
        self.assertIn('--token-file "$RUNNER_TEMP/code-read-token"', runner)
        self.assertEqual([n for n, s in named.items() if "CODE_READ_TOKEN" in s], ["Write the token to a file"])
        self.assertLess(list(named).index("Write the token to a file"),
                        list(named).index("Run the acceptance tests and record them"))

    def push_step(self):
        """The script of the step "Push the records" of the scaffolded acceptance.yml."""
        return self.step("Push the records")

    def step(self, name):
        """The script of the step called name of the scaffolded acceptance.yml."""
        if not os.path.exists(self.folder):
            r = scaffold(self.folder)
            self.assertEqual(r.returncode, 0, r.stderr)
        path = os.path.join(self.folder, "billing-acceptance", ".github", "workflows", "acceptance.yml")
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
        start = lines.index("      - name: " + name)
        while lines[start + 1].strip() != "run: |":
            start += 1
        body = []
        for line in lines[start + 2:]:
            if line.strip() and not line.startswith(" " * 10):
                break
            body.append(line[10:])
        return "\n".join(body) + "\n"

    def test_crp1_the_push_step_succeeds_with_no_records(self):
        step = self.push_step()
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null")
        for make_records in (False, True):
            with tempfile.TemporaryDirectory() as repo:
                subprocess.run(["git", "init", "-q", "-b", "main", repo], env=env, check=True)
                if make_records:
                    os.makedirs(os.path.join(repo, "records"))
                # GitHub Actions runs a step with "bash --noprofile --norc -eo pipefail".
                r = subprocess.run(["bash", "--noprofile", "--norc", "-eo", "pipefail", "-c", step],
                                   cwd=repo, env=env, capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, (make_records, r.stderr))
                log = subprocess.run(["git", "log", "--oneline"], cwd=repo, env=env, capture_output=True, text=True)
                self.assertEqual(log.stdout, "")

    def test_crp1_the_record_job_takes_only_appended_lines_of_this_run(self):
        step = self.step("Check and take the records")
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null", GIT_AUTHOR_NAME="t",
                   GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        url = "https://github.com/acme/billing-acceptance/actions/runs/"
        def line(kind="test", date="2026-10-27T10:00:00+00:00", by=url + "2"):
            return json.dumps({"kind": kind, "test": "t", "result": "pass", "date": date, "produced_by": by}) + "\n"
        old = line(date="2026-10-27T09:00:00+00:00", by=url + "1")
        cases = {
            "append": ({"AU-3.jsonl": old + line(), "AU-4.jsonl": line()}, True),
            "nothing new": ({"AU-3.jsonl": old}, True),
            "truncated": ({"AU-3.jsonl": ""}, False),
            "edited": ({"AU-3.jsonl": old.replace("pass", "fail") + line()}, False),
            "not a test": ({"AU-3.jsonl": old + line(kind="event")}, False),
            "another run": ({"AU-3.jsonl": old + line(by=url + "9")}, False),
            "older date": ({"AU-3.jsonl": old + line(date="2026-10-27T08:00:00+00:00")}, False),
            "two dates": ({"AU-3.jsonl": old + line(), "AU-4.jsonl": line(date="2026-10-27T11:00:00+00:00")}, False),
            "not JSON": ({"AU-3.jsonl": old + "x\n"}, False),
            "bad name": ({"x y.jsonl": line()}, False),
        }
        for case, (files, ok) in cases.items():
            with tempfile.TemporaryDirectory() as tmp:
                repo, src = os.path.join(tmp, "acceptance"), os.path.join(tmp, "records")
                os.makedirs(os.path.join(repo, "records"))
                os.makedirs(src)
                subprocess.run(["git", "init", "-q", "-b", "main", repo], env=env, check=True)
                with open(os.path.join(repo, "records", "AU-3.jsonl"), "w") as f:
                    f.write(old)
                subprocess.run(["git", "add", "-A"], cwd=repo, env=env, check=True)
                subprocess.run(["git", "commit", "-qm", "r"], cwd=repo, env=env, check=True)
                commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, env=env,
                                        capture_output=True, text=True).stdout.strip()
                for name, text in files.items():
                    with open(os.path.join(src, name), "w") as f:
                        f.write(text)
                run_env = env | {"RUNNER_TEMP": tmp, "COMMIT": commit,
                                 "RUN_URL": url + "2"}
                r = subprocess.run(["bash", "--noprofile", "--norc", "-eo", "pipefail", "-c", step],
                                   cwd=repo, env=run_env, capture_output=True, text=True)
                self.assertEqual(r.returncode == 0, ok, (case, r.stderr))
                with open(os.path.join(repo, "records", "AU-3.jsonl")) as f:
                    got = f.read()
                self.assertEqual(got, files["AU-3.jsonl"] if ok else old, case)
                if not ok:
                    self.assertFalse(os.path.exists(os.path.join(repo, "records", "AU-4.jsonl")), case)

    def test_crp1_the_script_of_the_workflow_exists(self):
        workflow = os.path.join(PLUGIN, "use-cases", "create-project", "templates", "acceptance",
                                ".github", "workflows", "acceptance.yml")
        with open(workflow, encoding="utf-8") as f:
            rel = re.search(r"\.\./claude-plugins/(\S+/acceptance_ci\.py)", f.read()).group(1)
        repo = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(PLUGIN))))
        self.assertTrue(os.path.isfile(os.path.join(repo, rel)), rel)
        self.assertFalse(os.path.exists(os.path.join(PLUGIN, "use-cases", "create-project", "scripts", "acceptance_ci.py")))

    def test_orc2_refusals_write_nothing(self):
        for extra in (["--components", "Web App"], ["--components", "api,api"], ["--profile", "beta"]):
            r = scaffold(self.folder, *extra)
            self.assertEqual(r.returncode, 1, extra)
            self.assertFalse(os.path.exists(self.folder), extra)


if __name__ == "__main__":
    unittest.main()
