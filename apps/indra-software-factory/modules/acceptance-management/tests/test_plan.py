"""Tests of use-cases/plan/plan.py and of scripts/acceptance_repository_checks.py.

The script of the use case plan, as PLN-1 to PLN-14 of
use-cases/plan/specs/plan.md say, with the checks of ACU-74 and the plan of
implementation of ACU-39 and ACU-42 of specs/module.md. Each test names the
clause it checks. The fixtures are temporary git repositories: a project
folder with the norms repository (data/tree.jsonl and specs-repo-annotated/)
and the acceptance repository, each a clone of a bare repository that stands
for GitHub. The scenarios that only the model decides (the judgement of PLN-7
and the prose of PLN-7 and PLN-8) are judged by the requester (open question 1
of the spec); the tests of the class Skill check that the skill states their
bound messages and limits. Run with:

    python3 -m unittest discover -s apps/indra-software-factory/modules/acceptance-management/tests
"""

import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest

PLUGIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(PLUGIN, "use-cases", "plan", "plan.py")
SKILL = os.path.join(PLUGIN, "use-cases", "plan", "SKILL.md")
CHECKS = os.path.join(PLUGIN, "scripts", "acceptance_repository_checks.py")
FILES = os.path.join(PLUGIN, "scripts", "acceptance_repository_files.py")

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_define import AA1, AU1, AU2, AU3, ENV, git, read, tree_jsonl, unit, write  # noqa: E402

PREFIX = "acceptance-management:plan: "

# The binding example of PLN-11, byte for byte.
PLAN_OF_PLN_11 = """{
  "increments": [
    {
      "name": "first-release",
      "acceptance_units": [
        {
          "acceptance_unit": "AU-1",
          "depends_on": [],
          "components": [
            ["api"]
          ]
        },
        {
          "acceptance_unit": "AU-3",
          "depends_on": ["AU-1"],
          "components": [
            ["api"],
            ["web"]
          ]
        }
      ]
    }
  ]
}
"""

AU3_AT_PLAN_COMMIT = AU3.replace("Then the CSV has 3 rows", "Then the CSV has three rows")


def planned(unit_id, depends_on=(), components=(("api",),)):
    return {"acceptance_unit": unit_id, "depends_on": list(depends_on), "components": [list(g) for g in components]}


def increment(name, *units):
    return {"name": name, "acceptance_units": list(units)}


def plan(*increments):
    return {"increments": list(increments)}


BINDING_PLAN = plan(increment("first-release", planned("AU-1"), planned("AU-3", ["AU-1"], [["api"], ["web"]])))


class Fixture(unittest.TestCase):
    """A project folder `p` with billing-norms and billing-acceptance, cloned from bare remotes.

    The acceptance repository has two commits: the plan commit, with AA-1, AU-1, AU-3 and the plan.json of PLN-11,
    and HEAD, which adds AU-2 and changes the unit hash of AU-3: the repository of the binding example of PLN-4."""

    layer_4 = [{"owner": "acme", "name": "billing-code-api", "layer": 4, "component": "api",
                "path": "billing-code-api"},
               {"owner": "acme", "name": "billing-code-web", "layer": 4, "component": "web",
                "path": "billing-code-web"}]

    def files_of_the_plan_commit(self):
        return {"areas/AA-1.md": AA1, "units/AU-1.md": AU1, "units/AU-3.md": AU3_AT_PLAN_COMMIT,
                "plan.json": PLAN_OF_PLN_11}

    def files_of_head(self):
        return {"units/AU-2.md": AU2, "units/AU-3.md": AU3}

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = os.path.realpath(self.tmp.name)
        self.remotes = os.path.join(self.root, "remotes", "acme")
        self.folder = os.path.join(self.root, "p")
        self.drafts = os.path.join(self.root, "drafts")
        os.makedirs(self.remotes)
        os.makedirs(self.folder)
        os.makedirs(self.drafts)
        repos = [{"owner": "acme", "name": "billing-specs", "layer": 1, "path": "billing-specs"},
                 {"owner": "acme", "name": "billing-norms", "layer": 2, "path": "billing-norms"},
                 {"owner": "acme", "name": "billing-acceptance", "layer": 3, "path": "billing-acceptance"}]
        self.project = json.dumps({"project": "billing", "repositories": repos + self.layer_4}, indent=2) + "\n"
        self.norms = self.clone("billing-norms", {
            "data/tree.jsonl": tree_jsonl(),
            "specs-repo-annotated/project.json": self.project,
            "specs-repo-annotated/billing/invoices.md": "# Invoices\n"})
        files = {"project.json": self.project, "acceptance.json": json.dumps(
            {"default_done_profile": "product", "last_area_id": 2, "last_unit_id": 20, "last_scenario_id": 40,
             "test_command": "", "product": {}}, indent=2) + "\n",
            "records/AU-3.jsonl": json.dumps({"kind": "test"}) + "\n",
            "tests/AU-3/test_export.py": "# AU-3@efc7ae86: Export the invoices to CSV\n"}
        files.update(self.files_of_the_plan_commit())
        self.acc = self.clone("billing-acceptance", files)
        self.plan_commit = git(self.acc, "rev-parse", "HEAD").stdout.strip()
        head = self.files_of_head()
        if head:
            for rel, text in head.items():
                write(os.path.join(self.acc, rel), text)
            self.commit_all(self.acc)

    def tearDown(self):
        self.tmp.cleanup()

    def clone(self, name, files):
        bare = os.path.join(self.remotes, name + ".git")
        git(self.root, "init", "-q", "--bare", "-b", "main", bare)
        path = os.path.join(self.folder, name)
        git(self.root, "clone", "-q", bare, path)
        git(path, "checkout", "-q", "-b", "main")
        for rel, text in files.items():
            write(os.path.join(path, rel), text)
        git(path, "add", "-A")
        git(path, "commit", "-q", "-m", "first")
        git(path, "push", "-q", "-u", "origin", "main")
        return path

    def commit_all(self, path, msg="more", push=True):
        git(path, "add", "-A")
        if git(path, "diff", "--cached", "--quiet", check=False).returncode != 0:
            git(path, "commit", "-q", "-m", msg)
        if push:
            git(path, "push", "-q", "origin", "HEAD:main")

    def push_from_other_clone(self, name, rel, text):
        other = os.path.join(self.root, "other-" + name)
        if not os.path.exists(other):
            git(self.root, "clone", "-q", os.path.join(self.remotes, name + ".git"), other)
        write(os.path.join(other, rel), text)
        self.commit_all(other)

    def commit_plan_json(self, value):
        """A commit of plan.json made outside the skill, such as by an earlier run."""
        text = value if isinstance(value, (str, bytes)) else json.dumps(value)
        write(os.path.join(self.acc, "plan.json"), text, "wb" if isinstance(text, bytes) else "w")
        self.commit_all(self.acc)

    def run_script(self, *args, cwd=None):
        return subprocess.run([sys.executable, "-I", SCRIPT, *args], cwd=cwd or self.acc, env=ENV,
                              capture_output=True, text=True)

    def script(self, *args, code=0):
        r = self.run_script(*args)
        self.assertEqual(r.returncode, code, r.stdout + r.stderr)
        return r.stdout

    def norms_commit(self):
        return git(self.norms, "rev-parse", "origin/main").stdout.strip()

    def head(self):
        return git(self.acc, "rev-parse", "HEAD").stdout.strip()

    def start(self, *extra, cwd=None):
        return self.run_script("start", cwd or self.acc, *extra)

    def started(self):
        r = self.start()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return json.loads(r.stdout)

    def refused(self, message, *extra, cwd=None):
        r = self.start(*extra, cwd=cwd)
        self.assertEqual((r.returncode, r.stdout.strip()), (1, PREFIX + message), r.stderr)

    def inventory(self):
        return json.loads(self.script("inventory", self.acc, "--norms-commit", self.norms_commit()))

    def unit_of(self, inv, unit_id):
        return next(u for u in inv["acceptance_units"] if u["unit_id"] == unit_id)

    def draft(self, value):
        path = os.path.join(self.drafts, f"draft-{len(os.listdir(self.drafts))}.json")
        write(path, value if isinstance(value, str) else json.dumps(value, ensure_ascii=False))
        return path

    def propose(self, value, *extra, code=0):
        return self.script("propose", self.acc, "--norms-commit", self.norms_commit(), "--draft", self.draft(value),
                           *extra, code=code).rstrip("\n")

    def changes(self, value, *extra):
        text = self.propose(value, *extra)
        lines = text.split("\n")
        return [re.sub(r"^  \d+\. ", "", line) for line in lines[lines.index("Changes:") + 1:]]

    def errors_of(self, value):
        """The errors of PLN-5 of a plan given as a draft (the same function checks plan.json at HEAD)."""
        r = self.run_script("propose", self.acc, "--norms-commit", self.norms_commit(), "--draft",
                            self.draft(value))
        if r.returncode == 0 or r.returncode == 4:
            return []
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        return r.stdout.rstrip("\n").split("\n")

    def write_plan(self, value, code=0):
        return self.script("write", self.acc, "--norms-commit", self.norms_commit(), "--draft", self.draft(value),
                           code=code)

    def commit(self, *extra, code=0, acceptance_commit=None):
        r = self.run_script("commit", self.acc, "--norms-commit", self.norms_commit(), "--acceptance-commit",
                            acceptance_commit or self.head(), *extra)
        self.assertEqual(r.returncode, code, r.stdout + r.stderr)
        return json.loads(r.stdout) if code == 0 else r.stdout.strip()

    def approve(self, prepared):
        return subprocess.run(prepared["command"], shell=True, env=ENV, capture_output=True, text=True)

    def remote_log(self):
        return git(os.path.join(self.remotes, "billing-acceptance.git"), "log", "-1", "--format=%B%n--%n",
                   "--name-status", "main").stdout


class Start(Fixture):
    """PLN-1, PLN-2: the checks of ACU-74 with "plan" as the use case, then those of plan, in their order."""

    def test_pln2_all_pass(self):
        out = self.started()
        self.assertEqual((out["acceptance_repository"], out["norms_repository"]),
                         ("acme/billing-acceptance", "acme/billing-norms"))
        self.assertEqual((out["acceptance_default_branch"], out["norms_default_branch"]), ("main", "main"))
        self.assertEqual(out["norms_commit"], self.norms_commit())
        self.assertEqual(out["acceptance_commit"], self.head())
        self.assertEqual(out["plan_commit"], self.plan_commit)
        self.assertIsNone(out["nothing_to_plan"])
        self.assertIsNone(out["hand_off_errors"])

    def test_pln1_refusals_an_argument(self):
        self.refused("takes no argument", "--", "AU-3")

    def test_pln1_refusals_another_repository(self):
        self.refused("runs only from the acceptance repository", cwd=self.norms)
        plain = os.path.join(self.root, "plain")
        os.mkdir(plain)
        self.refused("runs only from the acceptance repository", cwd=plain)

    def test_acu74_an_entry_without_owner_or_name(self):
        """ORC-20: an entry with no owner or no name makes project.json one that ORC-21 cannot read."""
        for layer in (1, 2):
            for field in ("owner", "name"):
                with self.subTest(layer=layer, field=field):
                    project = json.loads(self.project)
                    entry = next(r for r in project["repositories"] if r["layer"] == layer)
                    del entry[field]
                    write(os.path.join(self.acc, "project.json"), json.dumps(project))
                    self.refused("runs only from the acceptance repository")

    def test_pln2_the_checks_of_the_module_in_their_order(self):
        """ACU-74: each step adds a failure of an earlier check than the one before, so the message moves up."""
        steps = [
            ("the acceptance repository is behind origin/main; run git pull",
             lambda: self.push_from_other_clone("billing-acceptance", "notes.txt", "x")),
            ("the acceptance repository has commits that are not on origin/main",
             lambda: (write(os.path.join(self.acc, "local.txt"), "x"), git(self.acc, "add", "local.txt"),
                      git(self.acc, "commit", "-q", "-m", "local"))),
            ("the acceptance repository is not on main", lambda: git(self.acc, "checkout", "-q", "-b", "other")),
            ("project.json differs from that of acme/billing-norms; run /project-management:sync",
             lambda: (write(os.path.join(self.norms, "specs-repo-annotated", "project.json"), self.project + " "),
                      self.commit_all(self.norms))),
            ("acme/billing-norms has no specs-repo-annotated/project.json on main",
             lambda: (git(self.norms, "rm", "-q", "specs-repo-annotated/project.json"), self.commit_all(self.norms))),
            ("acme/billing-norms: data/tree.jsonl is not valid",
             lambda: (write(os.path.join(self.norms, "data", "tree.jsonl"), "[1]\n"), self.commit_all(self.norms))),
            ("acme/billing-norms has no data/tree.jsonl on main",
             lambda: (git(self.norms, "rm", "-q", "data/tree.jsonl"), self.commit_all(self.norms))),
            ("cannot find the default branch of acme/billing-norms",
             lambda: git(os.path.join(self.remotes, "billing-norms.git"), "symbolic-ref", "HEAD", "refs/heads/nope")),
            ("cannot find the default branch of acme/billing-acceptance",
             lambda: git(os.path.join(self.remotes, "billing-acceptance.git"), "symbolic-ref", "HEAD",
                         "refs/heads/nope")),
            ("cannot fetch acme/billing-norms",
             lambda: git(self.norms, "remote", "set-url", "origin",
                         os.path.join(self.root, "nowhere", "acme", "billing-norms"))),
            ("cannot fetch acme/billing-acceptance",
             lambda: git(self.acc, "remote", "set-url", "origin",
                         os.path.join(self.root, "nowhere", "acme", "billing-acceptance"))),
            (f"acme/billing-norms not found at {self.norms}; run: git clone https://github.com/acme/billing-norms "
             f"{self.norms}", lambda: shutil.rmtree(self.norms)),
            ("project.json has not exactly one entry of layer 2, the norms repository, with a valid path",
             lambda: write(os.path.join(self.acc, "project.json"), self.project.replace('"layer": 2', '"layer": 7'))),
            ("runs only from the acceptance repository",
             lambda: write(os.path.join(self.acc, "project.json"), self.project.replace(
                 '"layer": 2', '"layer": 7').replace('"layer": 3', '"layer": 1'))),
            ("takes no argument", lambda: None),
        ]
        for message, make in steps:
            with self.subTest(message=message):
                make()
                if message == "takes no argument":
                    self.refused(message, "--", "AU-3")
                else:
                    self.refused(message)

    def layer_4_is(self, entries):
        project = json.loads(self.project)
        project["repositories"] = [r for r in project["repositories"] if r["layer"] != 4] + entries
        text = json.dumps(project, indent=2) + "\n"
        write(os.path.join(self.acc, "project.json"), text)
        self.commit_all(self.acc)
        write(os.path.join(self.norms, "specs-repo-annotated", "project.json"), text)
        self.commit_all(self.norms)

    def test_pln2_layer_4_does_not_meet_orc20(self):
        api = {"owner": "acme", "name": "billing-code-api", "layer": 4, "path": "billing-code-api"}
        web = {"owner": "acme", "name": "billing-code-web", "layer": 4, "path": "billing-code-web"}
        cases = [[], [api, web], [dict(api, component="api"), web], [dict(api, component="x"), dict(web, component="x")],
                 [dict(api, component="")]]
        for entries in cases:
            with self.subTest(entries=entries):
                self.layer_4_is(entries)
                self.refused("project.json: the entries of layer 4 do not meet ORC-20")

    def test_pln2_layer_4_one_entry_without_component(self):
        self.layer_4_is([{"owner": "acme", "name": "billing-code", "layer": 4, "path": "billing-code"}])
        self.assertEqual(self.inventory()["components"], ["billing-code"])

    def test_pln2_uncommitted_change_in_plan_json(self):
        message = "uncommitted change in plan.json; commit it, or discard it with: git restore --staged --worktree plan.json"
        write(os.path.join(self.acc, "plan.json"), PLAN_OF_PLN_11 + "\n")
        self.refused(message)
        git(self.acc, "add", "plan.json")
        self.refused(message)
        write(os.path.join(self.acc, "plan.json"), PLAN_OF_PLN_11)
        self.refused(message)

    def test_pln2_untracked_plan_json(self):
        git(self.acc, "rm", "-q", "plan.json")
        self.commit_all(self.acc)
        write(os.path.join(self.acc, "plan.json"), PLAN_OF_PLN_11)
        self.refused("untracked file plan.json; commit it, or remove it with: rm plan.json")

    def test_pln2_untracked_plan_json_ignored(self):
        git(self.acc, "rm", "-q", "plan.json")
        write(os.path.join(self.acc, ".gitignore"), "plan.json\n")
        self.commit_all(self.acc)
        write(os.path.join(self.acc, "plan.json"), PLAN_OF_PLN_11)
        self.refused("untracked file plan.json; commit it, or remove it with: rm plan.json")

    def test_pln2_the_checks_of_the_module_come_first(self):
        write(os.path.join(self.acc, "plan.json"), "x")
        self.refused("takes no argument", "--", "x")
        self.push_from_other_clone("billing-acceptance", "notes.txt", "x")
        self.refused("the acceptance repository is behind origin/main; run git pull")

    def test_pln2_other_uncommitted_changes(self):
        write(os.path.join(self.acc, "units", "AU-3.md"), AU3.replace("# AU-3 Export the invoices to CSV", "# AU-3 X"))
        write(os.path.join(self.acc, "acceptance.json"), "changed")
        write(os.path.join(self.acc, "tests", "AU-3", "test_export.py"), "changed")
        write(os.path.join(self.acc, "records", "AU-3.jsonl"), "changed")
        git(self.acc, "add", "units/AU-3.md")
        self.assertEqual(self.start().returncode, 0)
        self.assertEqual(self.unit_of(self.inventory(), "AU-3")["title"], "Export the invoices to CSV")
        status = git(self.acc, "status", "--porcelain").stdout
        self.assertIn("M  units/AU-3.md", status)


class Inventory(Fixture):
    """PLN-3, PLN-4, PLN-6: the inventory of the plan."""

    def test_pln4_binding_example(self):
        inv = self.inventory()
        self.assertEqual(list(inv), ["norms_commit", "acceptance_commit", "plan_commit", "components",
                                     "acceptance_areas", "acceptance_units", "current_plan", "plan_json_at_head",
                                     "errors"])
        self.assertEqual(inv["norms_commit"], self.norms_commit())
        self.assertEqual(inv["acceptance_commit"], self.head())
        self.assertEqual(inv["plan_commit"], self.plan_commit)
        self.assertEqual(inv["components"], ["api", "web"])
        self.assertEqual(inv["acceptance_areas"], [{"area_id": "AA-1", "title": "Billing", "scenarios": [
            {"scenario_id": "SC-9", "acceptance_units": ["AU-1", "AU-2", "AU-3"], "increment_name": None}]}])
        self.assertEqual(inv["acceptance_units"], [
            {"unit_id": "AU-1", "title": "Issue an invoice", "area_id": "AA-1",
             "unit_hash": self.unit_of(inv, "AU-1")["unit_hash"], "since_the_plan_commit": "unchanged",
             "behind_layer_2": False, "increment_name": "first-release", "position_in_current_plan": 1},
            {"unit_id": "AU-2", "title": "Cancel an invoice", "area_id": "AA-1",
             "unit_hash": self.unit_of(inv, "AU-2")["unit_hash"], "since_the_plan_commit": "added",
             "behind_layer_2": False, "increment_name": None, "position_in_current_plan": None},
            {"unit_id": "AU-3", "title": "Export the invoices to CSV", "area_id": "AA-1", "unit_hash": "efc7ae86",
             "since_the_plan_commit": "changed", "behind_layer_2": True, "increment_name": "first-release",
             "position_in_current_plan": 2}])
        self.assertEqual(inv["current_plan"], BINDING_PLAN)
        self.assertEqual(inv["plan_json_at_head"], BINDING_PLAN)
        self.assertEqual(inv["errors"], [])

    def test_pln4_order_of_the_numbers_and_nulls(self):
        write(os.path.join(self.acc, "units", "AU-10.md"), "# AU-10\n\nno heading title, no area\n")
        write(os.path.join(self.acc, "areas", "AA-10.md"), "#AA-10 x\n\n## Purpose\n\nx\n\n## Scenarios\n\n```gherkin\n"
              "@unit:AU-1 @unit:AU-3\nScenario: no ID\n  Then x\n```\n")
        self.commit_all(self.acc)
        inv = self.inventory()
        self.assertEqual([u["unit_id"] for u in inv["acceptance_units"]], ["AU-1", "AU-2", "AU-3", "AU-10"])
        au10 = self.unit_of(inv, "AU-10")
        self.assertEqual((au10["title"], au10["area_id"], au10["unit_hash"]), (None, None, None))
        self.assertEqual(inv["acceptance_areas"][1], {"area_id": "AA-10", "title": None, "scenarios": [
            {"scenario_id": None, "acceptance_units": ["AU-1", "AU-3"], "increment_name": "first-release"}]})

    def test_pln4_no_plan_json(self):
        git(self.acc, "rm", "-q", "plan.json")
        self.commit_all(self.acc)
        inv = self.inventory()
        self.assertEqual((inv["current_plan"], inv["plan_json_at_head"], inv["errors"]), ({"increments": []}, None, []))
        # PLN-6, "A plan.json deleted by a commit": with no plan.json at HEAD there is no plan commit (the term).
        self.assertIsNone(inv["plan_commit"])
        self.assertEqual([u["since_the_plan_commit"] for u in inv["acceptance_units"]], ["added"] * 3)
        self.assertIsNone(self.started()["plan_commit"])

    def test_pln3_reads_head_not_the_working_tree(self):
        write(os.path.join(self.acc, "units", "AU-4.md"), unit("AU-4", "Register", "CUS-1@c0c0c0c0", "SC-10"))
        write(os.path.join(self.acc, "units", "AU-1.md"), "# AU-1 Changed on disk\n")
        inv = self.inventory()
        self.assertEqual([u["unit_id"] for u in inv["acceptance_units"]], ["AU-1", "AU-2", "AU-3"])
        self.assertEqual(self.unit_of(inv, "AU-1")["title"], "Issue an invoice")

    def test_pln3_norms_working_tree_untouched(self):
        git(self.norms, "checkout", "-q", "-b", "old")
        write(os.path.join(self.norms, "data", "tree.jsonl"), "not json\n")
        before = (git(self.norms, "status", "--porcelain").stdout, git(self.norms, "branch").stdout)
        self.started()
        self.inventory()
        self.assertEqual(before, (git(self.norms, "status", "--porcelain").stdout, git(self.norms, "branch").stdout))
        self.assertEqual(read(os.path.join(self.norms, "data", "tree.jsonl")), "not json\n")

    def test_pln6_since_the_plan_commit(self):
        inv = self.inventory()
        self.assertEqual(self.unit_of(inv, "AU-2")["since_the_plan_commit"], "added")  # no file at the plan commit
        self.assertEqual(self.unit_of(inv, "AU-3")["since_the_plan_commit"], "changed")  # the unit hash differs
        self.assertEqual(self.unit_of(inv, "AU-1")["since_the_plan_commit"], "unchanged")  # the same, not null
        # Null at HEAD only: no line "## Narrative".
        write(os.path.join(self.acc, "units", "AU-1.md"), AU1.replace("## Narrative", "## Story"))
        self.commit_all(self.acc)
        self.assertEqual(self.unit_of(self.inventory(), "AU-1")["since_the_plan_commit"], "changed")
        # Null at both: a new plan commit that holds AU-1 without its narrative.
        self.commit_plan_json(BINDING_PLAN)
        inv = self.inventory()
        self.assertEqual(self.unit_of(inv, "AU-1")["since_the_plan_commit"], "changed")
        self.assertEqual(self.unit_of(inv, "AU-2")["since_the_plan_commit"], "unchanged")

    def test_pln6_only_a_title_changed(self):
        self.commit_plan_json(BINDING_PLAN)
        write(os.path.join(self.acc, "units", "AU-3.md"), AU3.replace("# AU-3 Export the invoices to CSV",
                                                                     "# AU-3 Export to CSV").replace(
            "Area: AA-1", "Area: AA-1\nProfile: critical"))
        self.commit_all(self.acc)
        self.assertEqual(self.unit_of(self.inventory(), "AU-3")["since_the_plan_commit"], "unchanged")

    def test_pln6_added_and_changed_stay_until_the_next_commit_of_plan_json(self):
        write(os.path.join(self.acc, "notes.txt"), "a commit that does not change plan.json")
        self.commit_all(self.acc)
        inv = self.inventory()
        self.assertEqual([u["since_the_plan_commit"] for u in inv["acceptance_units"]], ["unchanged", "added", "changed"])

    def test_pln6_an_acceptance_unit_that_was_deleted(self):
        git(self.acc, "rm", "-q", "units/AU-1.md")
        self.commit_all(self.acc)
        inv = self.inventory()
        self.assertNotIn("AU-1", [u["unit_id"] for u in inv["acceptance_units"]])
        self.assertEqual(inv["errors"], ["AU-1 is in plan.json and has no file units/AU-1.md"])
        self.assertEqual(inv["current_plan"], BINDING_PLAN)
        self.assertEqual(self.unit_of(inv, "AU-3")["position_in_current_plan"], 2)

    def test_pln6_behind_layer_2(self):
        self.assertFalse(self.unit_of(self.inventory(), "AU-1")["behind_layer_2"])
        self.assertTrue(self.unit_of(self.inventory(), "AU-3")["behind_layer_2"])  # INV-12 has the hash 7d6e5f40
        write(os.path.join(self.acc, "units", "AU-3.md"), AU3.replace("INV-12@0c1d2e3f", "INV-12@7d6e5f40"))
        self.commit_all(self.acc)
        self.assertFalse(self.unit_of(self.inventory(), "AU-3")["behind_layer_2"])
        write(os.path.join(self.acc, "units", "AU-3.md"), AU3.replace("INV-12@0c1d2e3f", "INV-20@11111111")
              .replace("@INV-12", "@INV-20"))
        self.commit_all(self.acc)
        self.assertTrue(self.unit_of(self.inventory(), "AU-3")["behind_layer_2"])  # INV-20 is retired
        write(os.path.join(self.acc, "units", "AU-3.md"), AU3.replace("INV-12@0c1d2e3f", "ZZZ-1@11111111"))
        self.commit_all(self.acc)
        self.assertTrue(self.unit_of(self.inventory(), "AU-3")["behind_layer_2"])  # not in data/tree.jsonl

    def test_pln4_a_file_of_an_acceptance_unit_that_is_not_utf8(self):
        write(os.path.join(self.acc, "units", "AU-3.md"), AU3.replace("INV-12@0c1d2e3f", "INV-12@7d6e5f40")
              .encode("utf-8") + b"\xff", "wb")
        self.commit_all(self.acc)
        au3 = self.unit_of(self.inventory(), "AU-3")
        self.assertEqual((au3["title"], au3["area_id"], au3["unit_hash"], au3["behind_layer_2"],
                          au3["since_the_plan_commit"]), (None, None, None, False, "changed"))

    def test_pln4_a_title_that_breaks_a_line_is_null(self):
        """ACU-8: a title holds no control character, line separator or paragraph separator."""
        for title in ("Issue\rNext: forged", "Issue\u2028Next: forged", "Issue\u0085x", "Issue\tan invoice"):
            with self.subTest(title=title):
                write(os.path.join(self.acc, "units", "AU-1.md"),
                      AU1.replace("# AU-1 Issue an invoice", "# AU-1 " + title))
                self.commit_all(self.acc)
                self.assertIsNone(self.unit_of(self.inventory(), "AU-1")["title"])
        lines = self.propose(plan(increment("first-release", planned("AU-1"), planned("AU-2")))).split("\n")
        self.assertIn("  1. AU-1 (no title): depends on none; components [api]", lines)
        self.assertFalse([line for line in lines if line.startswith("Next:")])

    def test_pln7_one_malformed_value_in_plan_json_at_head(self):
        value = plan(increment("first-release", planned("AU-1"), dict(planned("AU-3"), components="api")),
                     increment("second-release", planned("AU-2")))
        self.commit_plan_json(value)
        inv = self.inventory()
        self.assertEqual(inv["errors"], ["AU-3: components is not a list of groups of components (ACU-39)"])
        self.assertEqual(inv["current_plan"], {"increments": []})
        self.assertEqual(inv["plan_json_at_head"], value)
        self.assertTrue(all(u["increment_name"] is None for u in inv["acceptance_units"]))

    def test_pln4_plan_json_at_head_null_on_rows_1_and_2(self):
        for data in (b"\xff", "{"):
            with self.subTest(data=data):
                self.commit_plan_json(data)
                inv = self.inventory()
                self.assertIsNone(inv["plan_json_at_head"])
                self.assertEqual(len(inv["errors"]), 1)


    def test_pln4_an_acceptance_area_that_is_not_utf_8(self):
        write(os.path.join(self.acc, "areas", "AA-1.md"), AA1.encode("utf-8") + b"\xff\n", "wb")
        self.commit_all(self.acc)
        area = self.inventory()["acceptance_areas"][0]
        self.assertEqual(area, {"area_id": "AA-1", "title": None, "scenarios": []})

    def test_pln3_the_norms_origin_moved_after_the_start(self):
        """PLN-3: the reading stays at the norms commit of `start` when origin of the norms repository moves and is
        fetched afterwards; only row 3 of PLN-12 stops, at the commit."""
        norms_commit = self.norms_commit()
        self.push_from_other_clone("billing-norms", "notes.txt", "x")
        git(self.norms, "fetch", "-q", "origin")
        self.assertNotEqual(self.norms_commit(), norms_commit)
        r = self.run_script("inventory", self.acc, "--norms-commit", norms_commit)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(json.loads(r.stdout)["norms_commit"], norms_commit)
        r = self.run_script("inventory", self.acc, "--norms-commit", "0" * 40)
        self.assertEqual((r.returncode, r.stdout.strip()),
                         (1, PREFIX + "--norms-commit " + "0" * 40 + " is not a commit of acme/billing-norms"))


class Errors(Fixture):
    """PLN-5: the errors of a plan, the same for plan.json at HEAD and for a draft."""

    def test_pln5_rows_1_to_3(self):
        self.assertEqual(self.errors_of_bytes(b"\xff\xfe"), ["plan.json is not UTF-8"])
        self.assertEqual(self.errors_of("{"), ["plan.json is not valid JSON"])
        self.assertEqual(self.errors_of('{"increments": NaN}'), ["plan.json is not valid JSON"])
        # A lone surrogate is no Unicode text, and a repeated key gives two readers two plans.
        self.assertEqual(self.errors_of('{"increments": [{"name": "a\\ud800", "acceptance_units": [{"acceptance_unit": '
                                        '"AU-1", "depends_on": [], "components": [["api"]]}]}]}'),
                         ["plan.json is not valid JSON"])
        self.assertEqual(self.errors_of('{"increments": [{"name": "a", "acceptance_units": [{"acceptance_unit": '
                                        '"AU-1", "depends_on": [], "components": [["api\\udfff"]]}]}]}'),
                         ["plan.json is not valid JSON"])
        self.assertEqual(self.errors_of('{"increments": [{"name": "a", "acceptance_units": [{"acceptance_unit": '
                                        '"AU-1", "depends_on": [], "components": [["api"]]}]}], "increments": []}'),
                         ["plan.json is not valid JSON"])
        self.assertEqual(self.errors_of('{"increments": [{"name": "a", "name": "b", "acceptance_units": []}]}'),
                         ["plan.json is not valid JSON"])

    def test_pln5_row_2_at_head(self):
        self.commit_plan_json('{"increments": [{"name": "a\\ud800", "acceptance_units": []}]}')
        inventory_of_the_plan = self.inventory()
        self.assertEqual(inventory_of_the_plan["errors"], ["plan.json is not valid JSON"])
        self.assertIsNone(inventory_of_the_plan["plan_json_at_head"])
        self.commit_plan_json('{"increments": [{"name": "a", "acceptance_units": [{"acceptance_unit": "AU-1", '
                              '"depends_on": [], "components": [["api"]]}]}], "increments": []}')
        self.assertEqual(self.inventory()["errors"], ["plan.json is not valid JSON"])
        for value in ([], {"increments": {}}, {"increments": [], "x": 1}):
            self.assertEqual(self.errors_of(value),
                             ["plan.json is not one object with the one field increments (ACU-39)"])

    def errors_of_bytes(self, data):
        path = os.path.join(self.drafts, "bytes.json")
        write(path, data, "wb")
        r = self.run_script("propose", self.acc, "--norms-commit", self.norms_commit(), "--draft", path)
        return r.stdout.rstrip("\n").split("\n")

    def test_pln5_rows_4_to_12(self):
        good = planned("AU-1")
        cases = [
            (plan(increment("a", good), ["x"]),
             "increment 2 is not an object with the fields name and acceptance_units (ACU-39)"),
            (plan(increment("a", good), dict(increment("b", planned("AU-2")), extra=1)),
             "increment 2 is not an object with the fields name and acceptance_units (ACU-39)"),
            (plan(increment("a", good), increment(" b", planned("AU-2"))), "increment 2 has no valid name (ACU-39)"),
            (plan(increment("a", good), increment("", planned("AU-2"))), "increment 2 has no valid name (ACU-39)"),
            (plan(increment("a", good), increment("b\nc", planned("AU-2"))), "increment 2 has no valid name (ACU-39)"),
            (plan(increment("a", good), increment(3, planned("AU-2"))), "increment 2 has no valid name (ACU-39)"),
            (plan(increment("first-release", good), increment("first-release", planned("AU-2"))),
             "increment name first-release is used twice (ACU-9)"),
            (plan({"name": "first-release", "acceptance_units": {}}),
             "increment first-release: acceptance_units is not a list (ACU-39)"),
            (plan(increment("first-release", good, planned("AU-2"), {"acceptance_unit": "AU-3"})),
             "increment first-release, acceptance unit 3: not an object with the fields acceptance_unit, depends_on "
             "and components (ACU-39)"),
            (plan(increment("first-release", good, planned("AU-2"), planned("U3"))),
             "increment first-release, acceptance unit 3: U3 is not a unit ID"),
            (plan(increment("first-release", planned("AU-3"), planned("AU-3"))), "AU-3 is in plan.json twice (ACU-9)"),
            (plan(increment("a", dict(planned("AU-12"), depends_on=["x"]))),
             "AU-12: depends_on is not a list of unit IDs (ACU-39)"),
            (plan(increment("a", dict(planned("AU-12"), depends_on="AU-1"))),
             "AU-12: depends_on is not a list of unit IDs (ACU-39)"),
            (plan(increment("a", dict(planned("AU-12"), components=[]))),
             "AU-12: components is not a list of groups of components (ACU-39)"),
            (plan(increment("a", dict(planned("AU-12"), components=[[]]))),
             "AU-12: components is not a list of groups of components (ACU-39)"),
            (plan(increment("a", dict(planned("AU-12"), components=[[1]]))),
             "AU-12: components is not a list of groups of components (ACU-39)"),
        ]
        for value, message in cases:
            with self.subTest(message=message):
                self.assertEqual(self.errors_of(value), [message])

    def test_pln5_row_5_a_character_that_breaks_a_line(self):
        for name in ("b\rc", "b\u2028c", "b\u2029c", "b\tc", "\tb", "b\u007fc"):
            with self.subTest(name=name):
                self.assertEqual(self.errors_of(plan(increment("a", planned("AU-1")), increment(name, planned("AU-2")))),
                                 ["increment 2 has no valid name (ACU-39)"])
        self.assertEqual(self.errors_of(plan(increment("b c ü", planned("AU-1")))), [])

    def test_pln5_how_a_name_or_a_value_found_is_printed(self):
        self.assertEqual(self.errors_of(plan(increment("a", planned("AU-1")), {"name": 7, "acceptance_units": {}})),
                         ["increment 2 has no valid name (ACU-39)",
                          "increment 7: acceptance_units is not a list (ACU-39)"])
        self.assertEqual(self.errors_of(plan({"name": "a\nb", "acceptance_units": {}}))[1],
                         'increment "a\\nb": acceptance_units is not a list (ACU-39)')
        self.assertEqual(self.errors_of(plan({"name": "a\rb\u2028", "acceptance_units": {}}))[1],
                         'increment "a\\rb\\u2028": acceptance_units is not a list (ACU-39)')
        self.assertEqual(self.errors_of(plan(increment("first-release", planned("AU-1"), planned("AU-2"),
                                                       dict(planned("AU-3"), acceptance_unit=None)))),
                         ["increment first-release, acceptance unit 3: null is not a unit ID"])
        # Rows 8 and 9 number the planned acceptance unit within its increment.
        self.assertEqual(self.errors_of(plan(increment("a", planned("AU-1")),
                                             increment("b", planned("AU-2"), planned("U3")))),
                         ["increment b, acceptance unit 2: U3 is not a unit ID"])

    def test_pln5_a_value_repeated_gives_one_error_at_its_first_occurrence(self):
        value = plan(increment("x", planned("AU-1")), increment("y", planned("AU-2")),
                     increment("y", planned("AU-3")), increment("x", planned("AU-4")), increment("x", planned("AU-5")))
        self.assertEqual(self.errors_of(value), ["increment name x is used twice (ACU-9)",
                                                 "increment name y is used twice (ACU-9)"])
        value = plan(increment("a", planned("AU-1"), planned("AU-2"),
                               planned("AU-3", ["AU-2", "AU-1", "AU-1", "AU-2", "AU-1"],
                                       [["web", "api"], ["web"], ["api"], ["web"]])))
        self.assertEqual(self.errors_of(value), ["AU-3 depends on AU-2 twice (ACU-39)",
                                                 "AU-3 depends on AU-1 twice (ACU-39)",
                                                 "AU-3: component web is named twice (ACU-39)",
                                                 "AU-3: component api is named twice (ACU-39)"])

    def test_pln5_rows_13_to_19(self):
        cases = [
            (plan(increment("first-release", planned("AU-1")), increment("empty")),
             "increment empty holds no acceptance unit (ACU-39)"),
            (plan(increment("a", planned("AU-1"), planned("AU-7"))), "AU-7 is in plan.json and has no file units/AU-7.md"),
            (plan(increment("a", planned("AU-1", ["AU-1"]))), "AU-1 depends on itself (ACU-39)"),
            (plan(increment("a", planned("AU-1"), planned("AU-2", ["AU-1", "AU-1"]))),
             "AU-2 depends on AU-1 twice (ACU-39)"),
            (plan(increment("a", planned("AU-2", ["AU-3"]), planned("AU-3"))),
             "AU-2 depends on AU-3, which does not come before it in plan.json (ACU-42)"),
            (plan(increment("a", planned("AU-2", ["AU-3"]))),
             "AU-2 depends on AU-3, which does not come before it in plan.json (ACU-42)"),
            (plan(increment("a", planned("AU-2", components=[["mobile"]]))),
             "AU-2: mobile is not a component of layer 4 of project.json (ACU-39)"),
            (plan(increment("a", planned("AU-2", components=[["api", "api"]]))), "AU-2: component api is named twice (ACU-39)"),
            (plan(increment("a", planned("AU-2", components=[["api"], ["web", "api"]]))),
             "AU-2: component api is named twice (ACU-39)"),
        ]
        for value, message in cases:
            with self.subTest(message=message):
                self.assertEqual(self.errors_of(value), [message])

    def test_pln5_the_order_of_the_errors(self):
        value = plan(increment("x", planned("AU-3", ["AU-2"], [["mobile"]]), planned("AU-7")),
                     increment("y", planned("AU-2", ["AU-2"]), planned("AU-9")), increment("z"))
        self.assertEqual(self.errors_of(value), [
            "increment z holds no acceptance unit (ACU-39)",
            "AU-7 is in plan.json and has no file units/AU-7.md",
            "AU-9 is in plan.json and has no file units/AU-9.md",
            "AU-2 depends on itself (ACU-39)",
            "AU-3 depends on AU-2, which does not come before it in plan.json (ACU-42)",
            "AU-3: mobile is not a component of layer 4 of project.json (ACU-39)"])
        # One of the rows 1 to 12: the rows 13 to 19 are not checked.
        value["increments"].append(increment("x", planned("AU-1")))
        self.assertEqual(self.errors_of(value), ["increment name x is used twice (ACU-9)"])
        # Rows 4 and 5 and 11 together, in the order of the rows.
        value = plan(increment(" ", dict(planned("AU-1"), depends_on=[1])), "bad")
        self.assertEqual(self.errors_of(value), [
            "increment 2 is not an object with the fields name and acceptance_units (ACU-39)",
            "increment 1 has no valid name (ACU-39)",
            "AU-1: depends_on is not a list of unit IDs (ACU-39)"])

    def test_pln5_before_means_earlier_in_the_order_of_the_plan(self):
        self.assertEqual(self.errors_of(plan(increment("a", planned("AU-1")), increment("b", planned("AU-2", ["AU-1"]))))
                         , [])
        self.assertEqual(self.errors_of(plan(increment("a", planned("AU-2", ["AU-1"])), increment("b", planned("AU-1")))),
                         ["AU-2 depends on AU-1, which does not come before it in plan.json (ACU-42)"])

    def test_pln5_a_dependency_cycle_is_an_error_of_order(self):
        self.assertEqual(self.errors_of(plan(increment("a", planned("AU-1", ["AU-2"]), planned("AU-2", ["AU-1"])))),
                         ["AU-1 depends on AU-2, which does not come before it in plan.json (ACU-42)"])

    def test_pln5_what_is_not_an_error(self):
        self.assertEqual(self.errors_of(plan(increment("a", planned("AU-1")))), [])  # AU-2 left out
        self.assertEqual(self.errors_of(plan(increment("a", planned("AU-3")))), [])  # behind layer 2
        self.assertEqual(self.errors_of(json.dumps(BINDING_PLAN)), [])  # another layout
        self.assertEqual(self.errors_of({"increments": []}), [])

    def test_pln5_head_and_draft_get_the_same_errors(self):
        value = plan(increment("a", planned("AU-2", ["AU-3"]), planned("AU-3")))
        self.commit_plan_json(value)
        self.assertEqual(self.inventory()["errors"], self.errors_of(value))

    def test_pln5_what_the_script_does_not_judge(self):
        self.assertEqual(self.errors_of(plan(increment("a", planned("AU-1", components=[["web"], ["api"]]),
                                                      planned("AU-2", ["AU-1"])))), [])


class Proposal(Fixture):
    """PLN-8, PLN-9, PLN-10: the summary, the proposal of the plan and the changes of the plan."""

    def test_pln8_the_summary_of_the_inventory_of_the_plan(self):
        self.assertEqual(self.started()["summary"],
                         f"Layer 3 at {self.head()[:7]}: 3 acceptance units, 2 in the plan in 1 increment; since the "
                         "plan commit: 1 added, 1 changed; 1 behind layer 2; 0 errors in plan.json.")

    def test_pln8_singular_and_plural(self):
        git(self.acc, "rm", "-q", "units/AU-2.md", "units/AU-3.md")
        self.commit_all(self.acc)
        self.assertEqual(self.started()["summary"].split("\n")[0],
                         f"Layer 3 at {self.head()[:7]}: 1 acceptance unit, 1 in the plan in 1 increment; since the "
                         "plan commit: 0 added, 0 changed; 0 behind layer 2; 1 error in plan.json.")
        self.commit_plan_json(plan(increment("a", planned("AU-1")), increment("b", planned("AU-1"))))
        self.assertIn("0 in the plan in 0 increments", self.started()["summary"])

    def test_pln8_a_plan_json_that_is_not_valid(self):
        git(self.acc, "rm", "-q", "units/AU-1.md")
        self.commit_all(self.acc)
        summary = self.started()["summary"].split("\n")
        self.assertEqual(summary[1:], ["plan.json is not valid:", "  AU-1 is in plan.json and has no file units/AU-1.md"])

    def test_pln8_nothing_to_plan(self):
        git(self.acc, "rm", "-q", "-r", "units", "plan.json")
        self.commit_all(self.acc)
        self.assertEqual(self.started()["nothing_to_plan"], PREFIX + "no acceptance unit to plan")
        self.commit_plan_json({"increments": []})
        self.assertEqual(self.started()["nothing_to_plan"], PREFIX + "no acceptance unit to plan")
        self.commit_plan_json(plan(increment("first-release", planned("AU-7"))))
        self.assertIsNone(self.started()["nothing_to_plan"])

    def test_pln8_no_acceptance_unit_left(self):
        git(self.acc, "rm", "-q", "-r", "units")
        self.commit_all(self.acc)
        self.commit_plan_json(plan(increment("first-release", planned("AU-7"))))
        self.assertEqual(self.changes({"increments": []}), [
            'unplan acceptance unit AU-7 from "first-release": no file units/AU-7.md (required)',
            'delete increment "first-release"'])
        self.write_plan({"increments": []})
        self.assertEqual(read(os.path.join(self.acc, "plan.json")), '{\n  "increments": []\n}\n')

    def test_pln8_the_form_of_the_proposal_of_the_plan(self):
        draft = plan(increment("first-release", planned("AU-1"), planned("AU-2", ["AU-1"], [["api"], ["web"]]),
                               planned("AU-3", ["AU-1"], [["api"], ["web"]])))
        self.assertEqual(self.propose(draft).split("\n"), [
            "Plan of implementation (draft):",
            'Increment "first-release"',
            '  1. AU-1 "Issue an invoice": depends on none; components [api]',
            '  2. AU-2 "Cancel an invoice": depends on AU-1; components [api] then [web]',
            '  3. AU-3 "Export the invoices to CSV": depends on AU-1; components [api] then [web]; behind layer 2',
            "Scenarios of acceptance areas that change increment:",
            '  SC-9 of AA-1: none -> "first-release"',
            'Warning: increment "first-release" receives AU-2, SC-9 of AA-1; if it was done, it stops being done '
            '(ACU-31).',
            "Changes:",
            '  1. plan acceptance unit AU-2 "Cancel an invoice" in "first-release" after AU-1: depends on AU-1; '
            "components [api] then [web]"])

    def test_pln8_the_requester_proposes(self):
        draft = plan(increment("first-release", planned("AU-1"), planned("AU-2", ["AU-1"])),
                     increment("second-release", planned("AU-3", ["AU-1"], [["api"], ["web"]])))
        found = self.changes(draft)
        self.assertIn('add increment "second-release" after "first-release"', found)
        self.assertIn('move acceptance unit AU-3 "Export the invoices to CSV" to "second-release" first', found)

    def test_pln8_the_requester_rejects_a_required_change(self):
        git(self.acc, "rm", "-q", "units/AU-1.md")
        self.commit_all(self.acc)
        kept = self.script("kept-error", self.acc, "--norms-commit", self.norms_commit(), "--draft",
                           self.draft(BINDING_PLAN)).strip()
        self.assertEqual(kept, PREFIX + "without this change plan.json keeps the error AU-1 is in plan.json and has "
                                        "no file units/AU-1.md (PLN-5); reject the whole proposal to keep plan.json "
                                        "as it is.")
        self.assertEqual(self.script("kept-error", self.acc, "--norms-commit", self.norms_commit()).strip(), kept)
        self.assertEqual(self.script("kept-error", self.acc, "--norms-commit", self.norms_commit(), "--draft",
                                     self.draft(plan(increment("first-release", planned("AU-3")))), ), "")

    def test_pln8_nothing_to_propose(self):
        self.commit_plan_json(BINDING_PLAN)
        self.assertEqual(self.propose(BINDING_PLAN, code=4), PREFIX + "no change to propose")
        write(os.path.join(self.acc, "units", "AU-3.md"), AU3_AT_PLAN_COMMIT)
        write(os.path.join(self.acc, "units", "AU-5.md"), AU2.replace("AU-2", "AU-5"))
        write(os.path.join(self.acc, "units", "AU-1.md"), AU1.replace("When the user", "When the person"))
        self.commit_all(self.acc)
        self.assertEqual(self.propose(BINDING_PLAN, code=4), PREFIX + "no change to propose; reviewed AU-1, AU-3, AU-5")

    def test_pln9_the_acceptance_units_left_out_and_those_removed(self):
        draft = plan(increment("first-release", planned("AU-1")))
        lines = self.propose(draft).split("\n")
        self.assertIn('Not planned: AU-2 "Cancel an invoice", AU-3 "Export the invoices to CSV"', lines)
        self.assertIn("Removed: AU-3", lines)
        lines = self.propose(plan(increment("first-release", planned("AU-1"), planned("AU-2"),
                                            planned("AU-3", ["AU-1"], [["api"], ["web"]])))).split("\n")
        self.assertFalse([x for x in lines if x.startswith(("Not planned:", "Removed:"))])

    def test_pln9_no_title_and_no_escaping(self):
        write(os.path.join(self.acc, "units", "AU-2.md"), AU2.replace("# AU-2 Cancel an invoice", '# AU-2 Say "hi" ü'))
        write(os.path.join(self.acc, "units", "AU-4.md"), "no heading\n")
        self.commit_all(self.acc)
        lines = self.propose(plan(increment('first "release"', planned("AU-1"), planned("AU-2")))).split("\n")
        self.assertIn('Increment "first "release""', lines)
        self.assertIn('  2. AU-2 "Say "hi" ü": depends on none; components [api]', lines)
        self.assertIn('Not planned: AU-3 "Export the invoices to CSV", AU-4 (no title)', lines)

    def test_pln9_the_scenarios_of_acceptance_areas_that_change_increment(self):
        write(os.path.join(self.acc, "areas", "AA-1.md"), AA1.replace("```\n", "\n@unit:AU-1 @unit:AU-3\nScenario: two\n"
                                                                              "  Then x\n\n@SC-2 @unit:AU-1 @unit:AU-3\n"
                                                                              "Scenario: three\n  Then y\n```\n", 1)
              .replace("```gherkin\n@SC-9", "```gherkin\n@SC-9"))
        self.commit_all(self.acc)
        lines = self.propose(plan(increment("first-release", planned("AU-1"), planned("AU-2")),
                                  increment("second-release", planned("AU-3", ["AU-1"])))).split("\n")
        start = lines.index("Scenarios of acceptance areas that change increment:")
        self.assertEqual(lines[start + 1:start + 4], ['  SC-2 of AA-1: "first-release" -> "second-release"',
                                                      '  SC-9 of AA-1: none -> "second-release"',
                                                      '  (no ID) of AA-1: "first-release" -> "second-release"'])
        lines = self.propose(plan(increment("first-release", planned("AU-1"), planned("AU-3", ["AU-1"]))))
        self.assertNotIn("Scenarios of acceptance areas", lines)
        # A renamed increment is the same increment: its scenarios do not change increment.
        lines = self.propose(plan(increment("edition-1", planned("AU-1"),
                                            planned("AU-3", ["AU-1"], [["api"], ["web"]]))),
                             "--rename", "first-release", "edition-1")
        self.assertNotIn("Scenarios of acceptance areas", lines)
        self.assertTrue(lines.endswith('Changes:\n  1. rename increment "first-release" to "edition-1"'), lines)
        lines = self.propose(plan(increment("edition-1", planned("AU-1")),
                                  increment("second-release", planned("AU-3", ["AU-1"]))),
                             "--rename", "first-release", "edition-1").split("\n")
        self.assertIn('  SC-2 of AA-1: "first-release" -> "second-release"', lines)
        self.assertFalse([line for line in lines if line.endswith('-> "edition-1"')], lines)

    def test_pln9_an_increment_of_the_current_plan_that_receives_acceptance_units(self):
        self.commit_plan_json(plan(increment("edition-1", planned("AU-1")), increment("edition-2", planned("AU-3"))))
        lines = self.propose(plan(increment("edition-1", planned("AU-1"), planned("AU-2"), planned("AU-3")))).split("\n")
        warning = ('Warning: increment "edition-1" receives AU-2, AU-3, SC-9 of AA-1; if it was done, it stops being '
                   'done (ACU-31).')
        self.assertIn(warning, lines)
        self.assertLess(lines.index(warning), lines.index("Changes:"))
        # A renamed increment is the same increment; a new increment and a move inside an increment get no warning.
        lines = self.propose(plan(increment("first", planned("AU-3"), planned("AU-1"), planned("AU-2"))),
                             "--rename", "edition-1", "first")
        self.assertIn('Warning: increment "first" receives AU-3, AU-2, SC-9 of AA-1;', lines)
        lines = self.propose(plan(increment("edition-0", planned("AU-2")), increment("edition-1", planned("AU-1")),
                                  increment("edition-2", planned("AU-3"))))
        self.assertNotIn('Warning: increment "edition-0"', lines)
        self.assertNotIn('Warning: increment "edition-1"', lines)
        self.assertIn('Warning: increment "edition-2" receives SC-9 of AA-1;', lines)

    def test_pln9_an_increment_of_the_current_plan_that_receives_a_scenario_of_an_acceptance_area(self):
        """SC-9 crosses AU-1, AU-2 and AU-3: once all three are planned, it belongs to the latest (ACU-29)."""
        self.commit_plan_json(plan(increment("edition-1", planned("AU-1"), planned("AU-3", ["AU-1"]))))
        lines = self.propose(plan(increment("edition-0", planned("AU-2")),
                                  increment("edition-1", planned("AU-1"), planned("AU-3", ["AU-1"])))).split("\n")
        self.assertIn('  SC-9 of AA-1: none -> "edition-1"', lines)
        self.assertIn('Warning: increment "edition-1" receives SC-9 of AA-1; if it was done, it stops being done '
                      '(ACU-31).', lines)

    def test_pln9_no_warning_when_plan_json_at_head_cannot_be_read(self):
        self.commit_plan_json('{"increments": [{"name": "edition-1", "acceptance_units": []}], "x": 1}')
        lines = self.propose(plan(increment("edition-1", planned("AU-1"), planned("AU-2")))).split("\n")
        self.assertFalse([line for line in lines if line.startswith("Warning")], lines)

    def test_pln10_after_names_the_increment_of_the_draft(self):
        self.commit_plan_json(plan(increment("first", planned("AU-1")), increment("delta", planned("AU-2"))))
        self.assertEqual(self.changes(plan(increment("edition-0", planned("AU-3")), increment("delta", planned("AU-2")),
                                           increment("edition-1", planned("AU-1"))), "--rename", "first", "edition-1"),
                         ['add increment "edition-0" first', 'rename increment "first" to "edition-1"',
                          'move increment "edition-1" after "delta"',
                          'plan acceptance unit AU-3 "Export the invoices to CSV" in "edition-0" first: depends on '
                          "none; components [api]"])
        # "after" may name an increment that the draft adds, or an acceptance unit that it plans.
        self.assertEqual(self.changes(plan(increment("delta", planned("AU-2")), increment("new", planned("AU-3")),
                                           increment("first", planned("AU-1")))),
                         ['add increment "new" after "delta"', 'move increment "first" after "new"',
                          'plan acceptance unit AU-3 "Export the invoices to CSV" in "new" first: depends on none; '
                          "components [api]"])
        self.commit_plan_json(plan(increment("first", planned("AU-1"), planned("AU-2"))))
        self.assertEqual(self.changes(plan(increment("first", planned("AU-2"), planned("AU-3"), planned("AU-1")))),
                         ['plan acceptance unit AU-3 "Export the invoices to CSV" in "first" after AU-2: depends on '
                          "none; components [api]",
                          'move acceptance unit AU-1 "Issue an invoice" to "first" after AU-3'])

    def test_pln9_a_draft_with_an_error(self):
        out = self.propose(plan(increment("a", planned("AU-7"))), code=1)
        self.assertEqual(out, "AU-7 is in plan.json and has no file units/AU-7.md")

    def test_pln10_kinds_in_order(self):
        self.commit_plan_json(plan(increment("beta", planned("AU-20")), increment("gamma", planned("AU-1")),
                                   increment("first", planned("AU-3")), increment("delta", planned("AU-2"))))
        write(os.path.join(self.acc, "units", "AU-20.md"), AU2.replace("AU-2 Cancel an invoice", "AU-20 Divide"))
        write(os.path.join(self.acc, "units", "AU-4.md"), AU2.replace("AU-2 Cancel an invoice", "AU-4 Register"))
        self.commit_all(self.acc)
        git(self.acc, "rm", "-q", "units/AU-20.md")
        self.commit_all(self.acc)
        draft = plan(increment("edition-0", planned("AU-4")), increment("delta", planned("AU-2", components=[["web"]])),
                     increment("edition-1", planned("AU-1"), planned("AU-3")))
        self.assertEqual(self.changes(draft, "--rename", "first", "edition-1"), [
            'unplan acceptance unit AU-20 from "beta": no file units/AU-20.md (required)',
            'add increment "edition-0" first',
            'rename increment "first" to "edition-1"',
            'move increment "edition-1" after "delta"',
            'delete increment "beta"',
            'delete increment "gamma"',
            'plan acceptance unit AU-4 "Register" in "edition-0" first: depends on none; components [api]',
            'move acceptance unit AU-1 "Issue an invoice" to "edition-1" first',
            'change acceptance unit AU-2 "Cancel an invoice": components [api] -> [web]'])

    def test_pln10_replace_plan_json_which_cannot_be_read(self):
        self.commit_plan_json("{")
        found = self.changes(plan(increment("edition-1", planned("AU-1"))))
        self.assertEqual(found, ["replace plan.json, which cannot be read: plan.json is not valid JSON (required)",
                                 'add increment "edition-1" first',
                                 'plan acceptance unit AU-1 "Issue an invoice" in "edition-1" first: depends on none; '
                                 "components [api]"])

    def test_pln10_add_after_and_unplan_with_a_file(self):
        found = self.changes(plan(increment("first-release", planned("AU-1")), increment("edition-2", planned("AU-2"))))
        self.assertEqual(found, ['add increment "edition-2" after "first-release"',
                                 'plan acceptance unit AU-2 "Cancel an invoice" in "edition-2" first: depends on none; '
                                 "components [api]",
                                 'unplan acceptance unit AU-3 "Export the invoices to CSV" from "first-release"'])

    def test_pln10_two_increments_swapped(self):
        self.commit_plan_json(plan(increment("beta", planned("AU-1")), increment("gamma", planned("AU-2"))))
        self.assertEqual(self.changes(plan(increment("gamma", planned("AU-2")), increment("beta", planned("AU-1")))),
                         ['move increment "beta" after "gamma"'])

    def test_pln10_move_an_increment_first(self):
        self.commit_plan_json(plan(increment("a", planned("AU-1")), increment("b", planned("AU-2")),
                                   increment("c", planned("AU-3"))))
        self.assertEqual(self.changes(plan(increment("c", planned("AU-3")), increment("a", planned("AU-1")),
                                           increment("b", planned("AU-2")))),
                         ['move increment "c" first'])

    def test_pln10_what_is_moved(self):
        self.commit_plan_json(plan(increment("a", planned("AU-1"), planned("AU-2"), planned("AU-3"))))
        self.assertEqual(self.changes(plan(increment("a", planned("AU-3"), planned("AU-1"), planned("AU-2")))),
                         ['move acceptance unit AU-3 "Export the invoices to CSV" to "a" first'])
        self.assertEqual(self.changes(plan(increment("a", planned("AU-2"), planned("AU-1"), planned("AU-3")))),
                         ['move acceptance unit AU-1 "Issue an invoice" to "a" after AU-2'])

    def test_pln10_a_change_of_an_acceptance_unit(self):
        self.commit_plan_json(plan(increment("a", planned("AU-1"), planned("AU-2", ["AU-1"]),
                                             planned("AU-3", ["AU-1", "AU-2"]))))
        self.assertEqual(self.changes(plan(increment("a", planned("AU-1"), planned("AU-2"),
                                                     planned("AU-3", ["AU-2", "AU-1"], [["api"], ["web"]])))), [
            'change acceptance unit AU-2 "Cancel an invoice": depends on AU-1 -> none',
            'change acceptance unit AU-3 "Export the invoices to CSV": depends on AU-1, AU-2 -> AU-2, AU-1; '
            "components [api] -> [api] then [web]"])

    def test_pln10_a_required_change_of_an_acceptance_unit(self):
        self.commit_plan_json(plan(increment("a", planned("AU-1"), planned("AU-2", ["AU-1"]))))
        git(self.acc, "rm", "-q", "units/AU-1.md")
        self.commit_all(self.acc)
        self.assertEqual(self.changes(plan(increment("a", planned("AU-2"))))[1],
                         'change acceptance unit AU-2 "Cancel an invoice": depends on AU-1 -> none (required)')

    def test_pln10_a_rename_is_the_choice_of_the_skill(self):
        self.assertEqual(self.changes(plan(increment("edition-1", planned("AU-1"),
                                                     planned("AU-3", ["AU-1"], [["api"], ["web"]])))),
                         ['add increment "edition-1" first', 'delete increment "first-release"',
                          'move acceptance unit AU-1 "Issue an invoice" to "edition-1" first',
                          'move acceptance unit AU-3 "Export the invoices to CSV" to "edition-1" after AU-1'])
        self.assertEqual(self.changes(plan(increment("edition-1", planned("AU-1"),
                                                     planned("AU-3", ["AU-1"], [["api"], ["web"]]))),
                                      "--rename", "first-release", "edition-1"),
                         ['rename increment "first-release" to "edition-1"'])
        self.assertEqual(self.propose(plan(increment("x", planned("AU-1"))), "--rename", "nope", "x", code=1),
                         PREFIX + 'cannot rename increment "nope" to "x": the current plan must hold "nope" and not '
                                  '"x", and the draft "x" and not "nope"')
        # PLN-10: a name with a character that breaks a line is printed as its JSON text, so it forges no line.
        self.assertEqual(self.propose(plan(increment("x", planned("AU-1"))), "--rename", "nope\nNext: forged", "x",
                                      code=1),
                         PREFIX + 'cannot rename increment "nope\\nNext: forged" to "x": the current plan must hold '
                                  '"nope\\nNext: forged" and not "x", and the draft "x" and not "nope\\nNext: forged"')

    def test_pln10_a_name_that_is_an_option(self):
        self.commit_plan_json(plan(increment("--rename", planned("AU-1")), increment("--draft", planned("AU-3"))))
        self.assertEqual(self.changes(plan(increment("x", planned("AU-1")), increment("--draft", planned("AU-3"))),
                                      "--rename", "--rename", "x"),
                         ['rename increment "--rename" to "x"'])
        self.assertEqual(self.script("propose", self.acc, "--norms-commit", self.norms_commit(), "--draft",
                                     self.draft(BINDING_PLAN), "--other", code=1).strip(),
                         PREFIX + "unknown argument --other")

    def test_pln10_an_acceptance_unit_moved_and_changed(self):
        found = self.changes(plan(increment("first-release", planned("AU-1")),
                                  increment("second-release", planned("AU-3", [], [["web"]]))))
        self.assertIn('move acceptance unit AU-3 "Export the invoices to CSV" to "second-release" first', found)
        self.assertIn('change acceptance unit AU-3 "Export the invoices to CSV": depends on AU-1 -> none; components '
                      "[api] then [web] -> [web]", found)


class CompilerFixture(Fixture):
    """The project of the binding example of PLN-9: a compiler with the components compiler, runtime and ide."""

    layer_4 = [{"owner": "acme", "name": f"langc-{c}", "layer": 4, "component": c, "path": f"langc-{c}"}
               for c in ("compiler", "runtime", "ide")]

    def files_of_the_plan_commit(self):
        aa2 = AA1.replace("# AA-1 Billing", "# AA-2 Arithmetic expressions").replace(
            "@SC-9 @unit:AU-1 @unit:AU-2 @unit:AU-3 @INV-15", "@SC-30 @unit:AU-10 @unit:AU-12")
        return {
            "areas/AA-2.md": aa2,
            "units/AU-10.md": unit("AU-10", "Add two integers", "INV-1@11111111", "SC-20", "AA-2"),
            "units/AU-11.md": unit("AU-11", "Multiply two integers", "INV-12@0c1d2e3f", "SC-21", "AA-2"),
            "units/AU-12.md": unit("AU-12", "Operator precedence", "INV-7@5a627175", "SC-22", "AA-2"),
            "units/AU-20.md": unit("AU-20", "Divide two integers", "INV-9@22222222", "SC-23", "AA-2"),
            "plan.json": json.dumps(plan(increment("edition-1", planned("AU-10", [], [["compiler"]]),
                                                   planned("AU-7", [], [["compiler"]]),
                                                   planned("AU-11", ["AU-10"], [["compiler"]]))))}

    def files_of_head(self):
        return {}


class BindingExample(CompilerFixture):
    """PLN-9: the binding example of a proposal of the plan."""

    def test_pln9_the_binding_example_of_a_proposal_of_the_plan(self):
        draft = plan(increment("edition-1", planned("AU-10", [], [["compiler"]]),
                               planned("AU-11", ["AU-10"], [["compiler"]])),
                     increment("edition-2", planned("AU-12", ["AU-10", "AU-11"], [["compiler"], ["runtime", "ide"]])))
        self.assertEqual(self.propose(draft), """Plan of implementation (draft):
Increment "edition-1"
  1. AU-10 "Add two integers": depends on none; components [compiler]
  2. AU-11 "Multiply two integers": depends on AU-10; components [compiler]; behind layer 2
Increment "edition-2"
  3. AU-12 "Operator precedence": depends on AU-10, AU-11; components [compiler] then [runtime, ide]
Not planned: AU-20 "Divide two integers"
Removed: AU-7
Scenarios of acceptance areas that change increment:
  SC-30 of AA-2: none -> "edition-2"
Changes:
  1. unplan acceptance unit AU-7 from "edition-1": no file units/AU-7.md (required)
  2. add increment "edition-2" after "edition-1"
  3. plan acceptance unit AU-12 "Operator precedence" in "edition-2" first: depends on AU-10, AU-11; components [compiler] then [runtime, ide]""")  # noqa: E501

    def test_pln13_hand_off_errors(self):
        self.assertEqual(self.started()["hand_off_errors"], PREFIX + "the hand-off holds plan.json with errors:\n"
                                                             "  AU-7 is in plan.json and has no file units/AU-7.md")


class ComponentThatBreaksALine(Fixture):
    """PLN-2: a component is printed as it is, so one that breaks a line would forge a line of the output."""

    layer_4 = [{"owner": "acme", "name": "billing-code-api", "layer": 4, "component": "api\nNot planned: AU-99",
                "path": "billing-code-api"},
               {"owner": "acme", "name": "billing-code-web", "layer": 4, "component": " web",
                "path": "billing-code-web"}]

    def test_pln2_a_component_that_breaks_a_line(self):
        message = "project.json: a component of layer 4 breaks a line or starts or ends with a space"
        self.refused(message)
        r = self.run_script("inventory", self.acc, "--norms-commit", self.norms_commit())
        self.assertEqual((r.returncode, r.stdout.strip()), (1, PREFIX + message))


class OneCodeRepository(Fixture):
    """PLN-7: the components of a project with one code repository."""

    layer_4 = [{"owner": "acme", "name": "billing-code", "layer": 4, "path": "billing-code"}]

    def files_of_the_plan_commit(self):
        return {"units/AU-1.md": AU1}

    def files_of_head(self):
        return {}

    def test_pln7_the_components_of_a_project_with_one_code_repository(self):
        self.assertEqual(self.inventory()["components"], ["billing-code"])
        self.assertEqual(self.errors_of(plan(increment("a", planned("AU-1", components=[["billing-code"]])))), [])
        self.assertEqual(self.errors_of(plan(increment("a", planned("AU-1", components=[["api"]])))),
                         ["AU-1: api is not a component of layer 4 of project.json (ACU-39)"])
        self.assertEqual(self.started()["plan_commit"], None)
        self.assertEqual(self.started()["summary"].split(";")[1], " since the plan commit: 1 added, 0 changed")

    def test_pln6_no_plan_commit(self):
        inventory_of_the_plan = self.inventory()
        self.assertIsNone(inventory_of_the_plan["plan_commit"])
        self.assertEqual(self.unit_of(inventory_of_the_plan, "AU-1")["since_the_plan_commit"], "added")


class Writing(Fixture):
    """PLN-11, PLN-12, PLN-13, PLN-14: writing plan.json, its commit and the line after it."""

    def test_pln11_the_form_of_plan_json(self):
        git(self.acc, "rm", "-q", "plan.json")
        self.commit_all(self.acc)
        self.write_plan(json.loads(PLAN_OF_PLN_11))
        with open(os.path.join(self.acc, "plan.json"), "rb") as f:
            self.assertEqual(f.read(), PLAN_OF_PLN_11.encode("utf-8"))

    def test_pln11_characters_outside_ascii_and_key_order(self):
        value = {"increments": [{"acceptance_units": [{"components": [["api"]], "depends_on": [],
                                                       "acceptance_unit": "AU-1"}], "name": "édition"}]}
        self.write_plan(value)
        text = read(os.path.join(self.acc, "plan.json"))
        self.assertIn('"name": "édition"', text)
        self.assertLess(text.index('"name"'), text.index('"acceptance_units"'))
        self.assertLess(text.index('"acceptance_unit"'), text.index('"depends_on"'))

    def test_pln11_a_plan_with_no_increment(self):
        self.write_plan({"increments": []})
        self.assertEqual(read(os.path.join(self.acc, "plan.json")), '{\n  "increments": []\n}\n')

    def test_pln11_the_check_before_the_commit(self):
        out = self.write_plan(plan(increment("a", planned("AU-7"))), code=1)
        self.assertEqual(out.strip(), "AU-7 is in plan.json and has no file units/AU-7.md")
        self.assertEqual(read(os.path.join(self.acc, "plan.json")), PLAN_OF_PLN_11)

    def test_pln11_a_draft_that_no_reader_can_use(self):
        out = self.write_plan('{"increments": [{"name": "a\\ud800", "acceptance_units": [{"acceptance_unit": "AU-1", '
                              '"depends_on": [], "components": [["api"]]}]}]}', code=1)
        self.assertEqual(out.strip(), "plan.json is not valid JSON")
        self.assertEqual(read(os.path.join(self.acc, "plan.json")), PLAN_OF_PLN_11)
        self.assertEqual(git(self.acc, "status", "--porcelain").stdout, "")

    def test_pln11_a_plan_that_keeps_an_error_of_head(self):
        git(self.acc, "rm", "-q", "units/AU-1.md")
        self.commit_all(self.acc)
        self.write_plan(BINDING_PLAN, code=1)
        write(os.path.join(self.acc, "plan.json"), PLAN_OF_PLN_11 + " ")
        self.assertEqual(self.commit(code=1), "AU-1 is in plan.json and has no file units/AU-1.md")

    def final(self):
        return plan(increment("first-release", planned("AU-1"), planned("AU-2", ["AU-1"], [["api"], ["web"]]),
                              planned("AU-3", ["AU-1"], [["api"], ["web"]])))

    def test_pln12_the_commit_and_a_body(self):
        self.write_plan(self.final())
        prepared = self.commit()
        self.assertEqual(prepared["message"], 'docs: change the plan of implementation\n\nplan acceptance unit AU-2 '
                                              '"Cancel an invoice" in "first-release" after AU-1: depends on AU-1; '
                                              "components [api] then [web]")
        self.assertIn("+        {", prepared["display"])
        self.assertIn("docs: change the plan of implementation", prepared["display"])
        self.assertIn("origin", prepared["command"])
        self.assertIn("HEAD:main", prepared["command"])
        for forbidden in ("add -A", "add .", "commit -a", "stash", "reset", "checkout", "restore", "clean"):
            self.assertNotIn(forbidden, prepared["command"])
        r = self.approve(prepared)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        # PLN-12 names no expected head: the command prints no commit (prints_the_commit=False of ACU-75).
        self.assertIsNone(re.search(r"^[0-9a-f]{40}$", r.stdout, re.M), r.stdout)
        log = self.remote_log()
        self.assertTrue(log.startswith(prepared["message"] + "\n"), log)
        self.assertEqual(log.split("--\n")[1].strip(), "M\tplan.json")
        self.assertEqual(git(self.acc, "status", "--porcelain").stdout, "")

    def test_pln12_the_subject_when_head_holds_no_plan_json(self):
        git(self.acc, "rm", "-q", "plan.json")
        self.commit_all(self.acc)
        self.write_plan(self.final())
        prepared = self.commit()
        self.assertTrue(prepared["message"].startswith("docs: add the plan of implementation\n\nadd increment "
                                                       '"first-release" first\n'), prepared["message"])
        self.assertIn("new plan.json", prepared["display"])
        self.assertEqual(self.approve(prepared).returncode, 0)
        self.assertIn("A\tplan.json", self.remote_log())

    def test_pln12_the_commit_holds_only_plan_json(self):
        write(os.path.join(self.acc, "units", "AU-3.md"), AU3 + "\n")
        git(self.acc, "add", "units/AU-3.md")
        write(os.path.join(self.acc, "tests", "AU-3", "test_export.py"), "another session")
        self.write_plan(self.final())
        r = self.approve(self.commit())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.remote_log().split("--\n")[1].strip(), "M\tplan.json")
        status = git(self.acc, "status", "--porcelain").stdout
        self.assertIn("M  units/AU-3.md", status)
        self.assertIn(" M tests/AU-3/test_export.py", status)

    def test_pln12_the_requester_refuses_the_command(self):
        self.write_plan(self.final())
        self.commit()
        self.script("rollback", self.acc)
        self.assertEqual(read(os.path.join(self.acc, "plan.json")), PLAN_OF_PLN_11)
        self.assertEqual(git(self.acc, "status", "--porcelain").stdout, "")
        git(self.acc, "rm", "-q", "plan.json")
        self.commit_all(self.acc)
        self.write_plan(self.final())
        git(self.acc, "add", "plan.json")
        self.script("rollback", self.acc)
        self.assertFalse(os.path.exists(os.path.join(self.acc, "plan.json")))
        self.assertEqual(git(self.acc, "status", "--porcelain").stdout, "")

    def test_pln12_the_default_branch_moved(self):
        self.write_plan(self.final())
        self.push_from_other_clone("billing-acceptance", "notes.txt", "x")
        self.assertEqual(self.commit(code=3), PREFIX + "origin/main moved; run the skill again")

    def test_pln12_the_default_branch_moves_after_the_command_is_shown(self):
        self.write_plan(self.final())
        prepared = self.commit()
        self.push_from_other_clone("billing-acceptance", "notes.txt", "x")
        head = self.head()
        r = self.approve(prepared)
        self.assertEqual((r.returncode, (r.stdout + r.stderr).strip()),
                         (3, PREFIX + "origin/main moved; run the skill again"))
        self.assertEqual(self.head(), head)
        self.assertEqual(git(self.acc, "diff", "--cached", "--name-only").stdout, "")

    def test_pln12_a_commit_of_another_session(self):
        """ACU-74: a commit that another session adds to HEAD is never pushed with the commit of plan.json."""
        self.write_plan(self.final())
        acceptance_commit = self.head()
        prepared = self.commit()
        write(os.path.join(self.acc, "notes.txt"), "another session")
        git(self.acc, "add", "notes.txt")
        git(self.acc, "commit", "-q", "-m", "another session")
        message = PREFIX + "the acceptance repository has commits that are not on origin/main"
        r = self.approve(prepared)
        self.assertEqual((r.returncode, r.stdout.strip()), (3, message))
        self.assertEqual(git(self.acc, "diff", "--cached", "--name-only").stdout, "")
        self.assertEqual(self.commit(code=3, acceptance_commit=acceptance_commit), message)
        self.assertNotIn("notes.txt", self.remote_log())

    def test_pln12_head_is_no_longer_the_acceptance_commit(self):
        self.write_plan(self.final())
        acceptance_commit = self.head()
        prepared = self.commit()
        git(self.acc, "commit", "-q", "--allow-empty", "-m", "another session")
        git(self.acc, "push", "-q", "origin", "HEAD:main")
        r = self.approve(prepared)
        moved = PREFIX + "origin/main moved; run the skill again"
        self.assertEqual((r.returncode, r.stdout.strip()), (3, moved))
        self.assertEqual(self.commit(code=3, acceptance_commit=acceptance_commit), moved)

    def test_pln12_cannot_fetch(self):
        self.write_plan(self.final())
        prepared = self.commit()
        git(self.acc, "remote", "set-url", "origin", os.path.join(self.root, "nowhere", "acme", "billing-acceptance"))
        r = self.approve(prepared)
        self.assertEqual((r.returncode, (r.stdout + r.stderr).strip()),
                         (3, PREFIX + "cannot fetch acme/billing-acceptance"))
        self.assertEqual(self.commit(code=3), PREFIX + "cannot fetch acme/billing-acceptance")

    def test_pln12_the_push_is_rejected(self):
        self.write_plan(self.final())
        prepared = self.commit()
        hook = os.path.join(self.remotes, "billing-acceptance.git", "hooks", "pre-receive")
        write(hook, "#!/bin/sh\nexit 1\n")
        os.chmod(hook, 0o755)
        r = self.approve(prepared)
        self.assertEqual((r.returncode, (r.stdout + r.stderr).strip()),
                         (4, PREFIX + f"push rejected; commit {self.head()[:7]} is not on origin/main; run git pull "
                                      "--rebase, then git push, and run the skill again"))
        # Run again after a rejected push (ACU-74).
        self.refused("the acceptance repository has commits that are not on origin/main")

    def test_pln12_run_again_after_an_interruption_before_the_commit(self):
        self.write_plan(self.final())
        self.refused("uncommitted change in plan.json; commit it, or discard it with: git restore --staged --worktree "
                     "plan.json")
        self.script("rollback", self.acc)
        git(self.acc, "rm", "-q", "plan.json")
        self.commit_all(self.acc)
        self.write_plan(self.final())
        self.refused("untracked file plan.json; commit it, or remove it with: rm plan.json")

    def test_pln12_run_again_after_an_interruption_after_the_push(self):
        self.write_plan(self.final())
        self.assertEqual(self.approve(self.commit()).returncode, 0)
        out = self.started()
        self.assertEqual(out["plan_commit"], self.head())
        self.assertEqual(self.propose(self.final(), code=4), PREFIX + "no change to propose")

    def test_pln12_nothing_to_commit(self):
        self.write_plan(BINDING_PLAN)
        self.assertEqual(self.commit(code=4), PREFIX + "no change to propose; reviewed AU-2, AU-3")

    def test_pln13_the_line_after_the_commit(self):
        self.write_plan(self.final())
        self.assertEqual(self.commit()["next"], "Next: the acceptance architect updates AU-3 with "
                                                "/acceptance-management:define; the implementing agents of api, web "
                                                "implement the plan with /code-implementation:implement.")

    def test_pln13_no_part_applies(self):
        write(os.path.join(self.acc, "units", "AU-3.md"), AU3.replace("INV-12@0c1d2e3f", "INV-12@7d6e5f40"))
        self.commit_all(self.acc)
        self.write_plan(plan(increment("first-release", planned("AU-1"))))
        self.assertIsNone(self.commit()["next"])
        self.write_plan(plan(increment("first-release", planned("AU-1"), planned("AU-2", components=[["web"]]))))
        self.assertEqual(self.commit()["next"], "Next: the implementing agents of web implement the plan with "
                                                "/code-implementation:implement.")

    def test_pln14_what_the_skill_writes(self):
        before = {p: git(self.acc, "hash-object", p).stdout for p in
                  ("units/AU-1.md", "areas/AA-1.md", "acceptance.json", "records/AU-3.jsonl",
                   "tests/AU-3/test_export.py")}
        self.write_plan(self.final())
        self.assertEqual(self.approve(self.commit()).returncode, 0)
        after = {p: git(self.acc, "hash-object", p).stdout for p in before}
        self.assertEqual(before, after)
        self.assertNotIn("Increment:", read(os.path.join(self.acc, "units", "AU-1.md")))

    def test_pln14_the_work_of_other_sessions(self):
        for path in (SCRIPT, CHECKS):
            source = read(path)
            for word in ("stash", "reset", "checkout", "restore", "clean"):
                self.assertNotRegex(source, rf'git\([^)]*"{word}"', path)

    def nowhere(self, name):
        return os.path.join(self.root, "nowhere", "acme", name)

    def test_pln12_row_3_the_norms_repository_moved_since_the_start(self):
        """PLN-12, row 3: PLAN commit fetches the norms repository itself, so a push to it after `start` stops the
        commit even when nothing else fetched; rollback lets the next invocation start."""
        norms_commit = self.norms_commit()
        self.write_plan(self.final())
        self.push_from_other_clone("billing-norms", "notes.txt", "x")
        r = self.run_script("commit", self.acc, "--norms-commit", norms_commit, "--acceptance-commit", self.head())
        self.assertEqual((r.returncode, r.stdout.strip()),
                         (3, PREFIX + f"the norms commit {norms_commit} is not the head of the default branch of "
                                      "origin in acme/billing-norms; run the skill again"), r.stderr)
        self.script("rollback", self.acc)
        self.started()

    def test_pln12_row_1_cannot_fetch_the_norms_repository(self):
        self.write_plan(self.final())
        git(self.norms, "remote", "set-url", "origin", self.nowhere("billing-norms"))
        self.assertEqual(self.commit(code=3), PREFIX + "cannot fetch acme/billing-norms")

    def test_pln12_row_2_no_default_branch_of_the_norms_repository(self):
        self.write_plan(self.final())
        git(os.path.join(self.remotes, "billing-norms.git"), "symbolic-ref", "HEAD", "refs/heads/nope")
        self.assertEqual(self.commit(code=3), PREFIX + "cannot find the default branch of acme/billing-norms")

    def test_acu75_no_default_branch_of_the_acceptance_repository(self):
        self.write_plan(self.final())
        git(os.path.join(self.remotes, "billing-acceptance.git"), "symbolic-ref", "HEAD", "refs/heads/nope")
        self.assertEqual(self.commit(code=3), PREFIX + "cannot find the default branch of acme/billing-acceptance")

    def test_pln12_row_4_plan_json_is_not_written(self):
        self.write_plan(self.final())
        os.remove(os.path.join(self.acc, "plan.json"))
        self.assertEqual(self.commit(code=1), PREFIX + "plan.json is not written; run the skill again")
        os.mkdir(os.path.join(self.acc, "plan.json"))
        self.assertEqual(self.commit(code=1), PREFIX + "plan.json is not written; run the skill again")

    def test_pln12_row_6_plan_json_is_not_in_the_form_of_pln_11(self):
        self.write_plan(self.final())
        with open(os.path.join(self.acc, "plan.json"), "a") as f:
            f.write(" ")
        self.assertEqual(self.commit(code=1), PREFIX + "plan.json is not in the form of PLN-11; run the skill again")

    def test_pln12_the_order_of_the_stops(self):
        """Rows 1 to 3, then ACU-75, then rows 4 to 7."""
        self.write_plan(self.final())
        with open(os.path.join(self.acc, "plan.json"), "a") as f:
            f.write(" ")
        acceptance_remote = os.path.join(self.remotes, "billing-acceptance.git")
        git(acceptance_remote, "symbolic-ref", "HEAD", "refs/heads/nope")
        self.assertEqual(self.commit(code=3), PREFIX + "cannot find the default branch of acme/billing-acceptance")
        git(self.acc, "remote", "set-url", "origin", self.nowhere("billing-acceptance"))
        self.assertEqual(self.commit(code=3), PREFIX + "cannot fetch acme/billing-acceptance")
        norms_commit = self.norms_commit()
        self.push_from_other_clone("billing-norms", "notes.txt", "x")
        r = self.run_script("commit", self.acc, "--norms-commit", norms_commit, "--acceptance-commit", self.head())
        self.assertEqual((r.returncode, r.stdout.strip()),
                         (3, PREFIX + f"the norms commit {norms_commit} is not the head of the default branch of "
                                      "origin in acme/billing-norms; run the skill again"))
        git(self.norms, "remote", "set-url", "origin", self.nowhere("billing-norms"))
        self.assertEqual(self.commit(code=3), PREFIX + "cannot fetch acme/billing-norms")

    def test_pln12_a_gitignore_that_names_plan_json(self):
        git(self.acc, "rm", "-q", "plan.json")
        write(os.path.join(self.acc, ".gitignore"), "plan.json\n")
        self.commit_all(self.acc)
        self.write_plan(self.final())
        r = self.approve(self.commit())
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("plan.json", self.remote_log())

    def test_pln5_row_2_the_limit_of_nesting(self):
        at_the_limit = '{"increments": ' + "[" * 63 + "]" * 63 + "}"
        over_the_limit = '{"increments": ' + "[" * 64 + "]" * 64 + "}"
        self.assertEqual(self.errors_of(at_the_limit), ["increment 1 is not an object with the fields name and "
                                                        "acceptance_units (ACU-39)"])
        self.assertEqual(self.errors_of(over_the_limit), ["plan.json is not valid JSON"])
        in_a_string = plan({"name": "[" * 100, "acceptance_units": "x"})
        self.assertEqual(self.errors_of(in_a_string), ["increment " + "[" * 100 + ": acceptance_units is not a list "
                                                                                 "(ACU-39)"])

    def test_acu74_project_json_nested_deeply(self):
        write(os.path.join(self.acc, "project.json"), "[" * 100000 + "]" * 100000 + "\n")
        self.refused("runs only from the acceptance repository")

    def commit_symbolic_link(self, target):
        os.remove(os.path.join(self.acc, "plan.json"))
        os.symlink(target, os.path.join(self.acc, "plan.json"))
        self.commit_all(self.acc)

    def test_pln2_plan_json_at_head_is_a_symbolic_link(self):
        outside = os.path.join(self.root, "outside.txt")
        write(outside, "outside\n")
        self.commit_symbolic_link(outside)
        self.refused("plan.json is not a regular file")
        # PLN-11, "Only a regular file": write follows no symbolic link and writes nothing.
        r = self.run_script("write", self.acc, "--norms-commit", self.norms_commit(), "--draft",
                            self.draft(self.final()))
        self.assertEqual((r.returncode, r.stdout.strip()), (1, PREFIX + "cannot write plan.json"), r.stderr)
        path = os.path.join(self.acc, "plan.json")
        self.script("rollback", self.acc)
        self.assertEqual(os.readlink(path), outside)
        self.assertEqual(read(outside), "outside\n")
        self.assertEqual(git(self.acc, "status", "--porcelain").stdout, "")

    def test_pln2_plan_json_at_head_is_a_folder(self):
        os.remove(os.path.join(self.acc, "plan.json"))
        write(os.path.join(self.acc, "plan.json", "x.txt"), "x\n")
        self.commit_all(self.acc)
        self.refused("plan.json is not a regular file")
        r = self.run_script("write", self.acc, "--norms-commit", self.norms_commit(), "--draft",
                            self.draft(self.final()))
        self.assertEqual((r.returncode, r.stdout.strip()), (1, PREFIX + "cannot write plan.json"), r.stderr)
        self.script("rollback", self.acc)
        self.assertEqual(read(os.path.join(self.acc, "plan.json", "x.txt")), "x\n")
        self.assertEqual(git(self.acc, "status", "--porcelain").stdout, "")

    def test_pln2_plan_json_in_the_working_tree_is_not_a_regular_file(self):
        git(self.acc, "rm", "-q", "plan.json")
        self.commit_all(self.acc)
        os.symlink(os.path.join(self.root, "outside.txt"), os.path.join(self.acc, "plan.json"))
        self.refused("plan.json is not a regular file")
        os.remove(os.path.join(self.acc, "plan.json"))
        write(os.path.join(self.acc, "plan.json", "x.txt"), "x\n")
        self.refused("plan.json is not a regular file")

    def test_pln11_a_staged_symbolic_link_in_place_of_plan_json(self):
        """PLN-11, "Only a regular file": write writes nothing and leaves the index as it is."""
        path = os.path.join(self.acc, "plan.json")
        os.remove(path)
        os.symlink(os.path.join(self.root, "outside.txt"), path)
        git(self.acc, "add", "plan.json")
        index = git(self.acc, "ls-files", "-s", "plan.json").stdout
        r = self.run_script("write", self.acc, "--norms-commit", self.norms_commit(), "--draft",
                            self.draft(self.final()))
        self.assertEqual((r.returncode, r.stdout.strip()), (1, PREFIX + "cannot write plan.json"), r.stderr)
        self.assertEqual(git(self.acc, "ls-files", "-s", "plan.json").stdout, index)
        self.assertTrue(os.path.islink(path))

    def test_pln2_plan_json_in_the_working_tree_is_a_fifo(self):
        """PLN-2 row 3, PLN-11 "Only a regular file", PLN-12: a FIFO is no regular file; nothing waits on it, and
        rollback leaves it as it is."""
        git(self.acc, "rm", "-q", "plan.json")
        self.commit_all(self.acc)
        path = os.path.join(self.acc, "plan.json")
        os.mkfifo(path)
        self.refused("plan.json is not a regular file")
        r = subprocess.run([sys.executable, "-I", SCRIPT, "write", self.acc, "--norms-commit", self.norms_commit(),
                            "--draft", self.draft(self.final())], cwd=self.acc, env=ENV, capture_output=True,
                           text=True, timeout=60)
        self.assertEqual((r.returncode, r.stdout.strip()), (1, PREFIX + "cannot write plan.json"), r.stderr)
        self.script("rollback", self.acc)
        self.assertTrue(stat.S_ISFIFO(os.lstat(path).st_mode))

    def test_pln2_a_fifo_in_place_of_a_tracked_plan_json(self):
        path = os.path.join(self.acc, "plan.json")
        os.remove(path)
        os.mkfifo(path)
        self.refused("plan.json is not a regular file")

    def git_or_a_hook_refuses_the_commit(self):
        hook = os.path.join(self.acc, ".git", "hooks", "pre-commit")
        write(hook, "#!/bin/sh\nexit 1\n")
        os.chmod(hook, 0o755)
        head, remote_log = self.head(), self.remote_log()
        self.write_plan(self.final())
        r = self.approve(self.commit())
        self.assertNotIn(r.returncode, (0, 3, 4), r.stdout + r.stderr)
        self.assertEqual(self.head(), head)
        self.assertEqual(self.remote_log(), remote_log)
        self.assertIn("plan.json", git(self.acc, "status", "--porcelain").stdout)
        self.script("rollback", self.acc)
        self.assertEqual(git(self.acc, "status", "--porcelain").stdout, "")

    def test_pln12_git_or_a_hook_refuses_the_commit(self):
        """PLN-12, "Git or a hook refuses the commit": the command exits with another status than 0, 3 and 4 after it
        staged plan.json, and rollback puts the index entry and the working tree back as HEAD holds them."""
        self.git_or_a_hook_refuses_the_commit()
        self.assertEqual(read(os.path.join(self.acc, "plan.json")), PLAN_OF_PLN_11)

    def test_pln12_git_or_a_hook_refuses_the_commit_with_no_plan_json_at_head(self):
        git(self.acc, "rm", "-q", "plan.json")
        self.commit_all(self.acc)
        self.git_or_a_hook_refuses_the_commit()
        self.assertFalse(os.path.lexists(os.path.join(self.acc, "plan.json")))

    def test_pln12_rollback_touches_only_plan_json_in_the_index(self):
        write(os.path.join(self.acc, "units", "AU-1.md"), AU1.replace("When the user", "When the person"))
        git(self.acc, "add", "units/AU-1.md")
        self.write_plan(self.final())
        git(self.acc, "add", "plan.json")
        self.script("rollback", self.acc)
        self.assertEqual(git(self.acc, "status", "--porcelain").stdout, "M  units/AU-1.md\n")
        source = read(SCRIPT)
        self.assertEqual(sorted(set(re.findall(r'git\(root, "([a-z-]+)"', source[source.index("def rollback"):
                                                                                source.index("def write(")]))),
                         ["ls-files", "rm", "update-index"])

    def test_pln5_a_number_outside_the_range_of_a_double(self):
        def no_constant(name):
            raise ValueError(name)
        for text in ('{"increments": 1e999}', '{"increments": -1e999}', '{"increments": 1' + "0" * 400 + "}",
                     '{"increments": 1' + "0" * 5000 + "}"):
            self.assertEqual(self.errors_of(text), ["plan.json is not valid JSON"], text[:40])
            self.commit_plan_json(text)
            inv = json.loads(self.script("inventory", self.acc, "--norms-commit", self.norms_commit()),
                             parse_constant=no_constant)
            self.assertEqual((inv["errors"], inv["plan_json_at_head"]), (["plan.json is not valid JSON"], None))
        self.assertEqual(self.errors_of(plan(increment("a", {"acceptance_unit": 1e300, "depends_on": [],
                                                             "components": [["api"]]}))),
                         ["increment a, acceptance unit 1: 1e+300 is not a unit ID"])

    def test_pln5_a_value_nested_deeply(self):
        deep = '{"increments": ' + "[" * 100000 + "]" * 100000 + "}"
        errors = self.errors_of(deep)
        self.assertTrue(errors)
        self.assertNotIn("Traceback", "\n".join(errors))
        self.commit_plan_json(deep)
        self.started()
        self.inventory()

    def test_acu74_a_line_of_tree_jsonl_nested_deeply(self):
        write(os.path.join(self.norms, "data", "tree.jsonl"), "[" * 100000 + "]" * 100000 + "\n")
        self.commit_all(self.norms)
        self.refused("acme/billing-norms: data/tree.jsonl is not valid")

    def test_pln5_every_error_is_one_line(self):
        forged = "a\n  FORGED"
        errors = self.errors_of(plan({"name": forged, "acceptance_units": "x"},
                                     increment("b", {"acceptance_unit": "U\nX", "depends_on": [],
                                                     "components": [["api"]]})))
        self.assertEqual(errors, ["increment 1 has no valid name (ACU-39)",
                                  'increment "a\\n  FORGED": acceptance_units is not a list (ACU-39)',
                                  'increment b, acceptance unit 1: "U\\nX" is not a unit ID'])
        errors = self.errors_of(plan(increment("a", planned("AU-1", components=[["api\u2028FORGED"]]))))
        self.assertEqual(errors, ['AU-1: "api\\u2028FORGED" is not a component of layer 4 of project.json (ACU-39)'])

    def test_python_3_9(self):
        import ast
        for path in (SCRIPT, CHECKS, FILES):
            tree = ast.parse(read(path), feature_version=(3, 9))
            self.assertTrue(tree.body)


class Skill(unittest.TestCase):
    """PLN-1, PLN-7, PLN-8, PLN-13, PLN-14: what only the skill does, and the messages it binds."""

    def setUp(self):
        self.text = read(SKILL)

    def test_pln1_invocation(self):
        front = self.text.split("---")[1]
        self.assertIn("name: plan", front)
        self.assertIn("/acceptance-management:plan", front)
        self.assertIn("Never on your own", front)

    def test_pln8_bound_messages_of_the_skill(self):
        for message in (PREFIX + "what an acceptance unit is, is decided with /acceptance-management:define (ACU-44)",):
            self.assertIn(message, self.text)

    def test_pln7_a_plan_json_at_head_with_an_error_of_reading(self):
        self.assertIn("A\n  planned acceptance unit that an error names stays where it is", self.text)

    def test_pln9_the_warning_forbids_nothing(self):
        text = " ".join(self.text.split())
        self.assertIn('A line `Warning: increment "<name>" receives ...` forbids nothing: do not refuse the draft '
                      "for it, and do not ask the requester to confirm it apart from the proposal of the plan", text)
        self.assertIn("Never say whether an increment is done", text)
        self.assertIn("LAY-10", text)

    def test_pln12_every_stop_after_write_rolls_back(self):
        self.assertIn("Any non-zero exit of `PLAN commit` (1, 3 or 4)", self.text)
        # PLN-11, PLN-12 row 5: an error of PLN-5 found by `PLAN commit` is a stop, never a new write.
        self.assertNotIn("you may instead", " ".join(self.text.split()))
        self.assertNotIn("the norms origin moved", " ".join(self.text.split()))
        self.assertIn("`acceptance-management:plan: stopped; nothing is committed, and plan.json is as it was before "
                      "the skill ran`", self.text)

    def test_pln5_a_stop_is_not_an_error_of_the_draft(self):
        text = " ".join(self.text.split())
        self.assertIn("Exit 1 with output that starts with `acceptance-management:plan: `: a stop", text)
        self.assertIn("When its output starts with `acceptance-management:plan: ` otherwise, it is a stop", text)
        # PLN-11, "Only a regular file": nothing was written, so nothing is put back.
        self.assertIn("`acceptance-management:plan: cannot write plan.json`, it wrote nothing: say it as it is and "
                      "stop, with no `PLAN rollback`", text)

    def test_pln7_a_cycle_is_left_out_of_the_draft(self):
        text = " ".join(self.text.split())
        self.assertIn("Place every acceptance unit that the current plan does not hold, except the acceptance units "
                      "of a dependency cycle you find", text)
        self.assertIn("leave every acceptance unit of the cycle out of the draft (unplan those that the current plan "
                      "holds; the rendering names them under `Not planned:`)", text)

    def test_pln13_the_hand_off_errors_whenever_plan_json_holds_an_error(self):
        text = " ".join(self.text.split())
        self.assertIn("In a run, when `hand_off_errors` of step 1 is not null, say it as it is before the run goes on",
                      text)
        self.assertNotIn("when the proposal held a change that ends with `(required)`", text)

    def test_pln14_never_these_commands(self):
        self.assertIn("git stash", self.text)
        self.assertIn("never", self.text.lower())


if __name__ == "__main__":
    unittest.main()
