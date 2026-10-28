"""Tests of use-cases/define/define.py.

The script of the use case define, as ACU-57 to ACU-73 of
use-cases/define/specs/define.md say, with the files of ACU-6 to ACU-8 and the
fingerprints of ACU-51 to ACU-56 of specs/module.md. Each test names the
clause it checks. The fixtures are temporary git repositories: a project
folder with the norms repository (data/tree.jsonl and specs-repo-annotated/)
and the acceptance repository, each a clone of a bare repository that stands
for GitHub. Run with:

    python3 -m unittest discover -s apps/indra-software-factory/modules/acceptance-management/tests
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
SCRIPT = os.path.join(PLUGIN, "use-cases", "define", "define.py")

sys.dont_write_bytecode = True

ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t",
           GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null")

PREFIX = "acceptance-management:define: "

# The files of AA-1 (ACU-7) and AU-3 (ACU-8) of specs/module.md, and two more units of AA-1.
AA1 = """# AA-1 Billing

## Purpose

The people of the company issue, cancel and export the invoices of their customers.

## Scenarios

```gherkin
@SC-9 @unit:AU-1 @unit:AU-2 @unit:AU-3 @INV-15
Scenario: A cancelled invoice is not exported
  Given a customer with one issued invoice
  When the user cancels the invoice
  And the user exports the invoices to CSV
  Then the CSV has no row for that invoice
```
"""

AU3 = """# AU-3 Export the invoices to CSV

Area: AA-1

## Narrative

In order to take my invoices to my accounting program
As a user of the company
I want to export my invoices to a CSV file

## Norms

- INV-7@5a627175: one row per invoice
- INV-12@0c1d2e3f: amounts with two decimals
- INV-15@9e8d7c6b: cancelled invoices are not exported

## Scenarios

```gherkin
@SC-5 @INV-7 @INV-12
Scenario: Three invoices give three rows
  Given a user with 3 issued invoices
  When the user runs "app export --format csv"
  Then the CSV has 3 rows
  And every amount has two decimals

@SC-6 @INV-15
Scenario: A cancelled invoice gives no row
  Given a user with 2 issued invoices and 1 cancelled invoice
  When the user runs "app export --format csv"
  Then the CSV has 2 rows
```

## Non-goals

- The unit does not export to PDF.
- The unit does not export to Excel.

## Assumptions

- The invoices are already in the database (environment).
- The user may see every invoice of the company (USR-4).
"""


def unit(uid, title, norm, sc, area="AA-1", extra=""):
    """A valid unit file (ACU-8) that cites one norm and has one scenario."""
    return (f"# {uid} {title}\n\nArea: {area}\n{extra}\n## Narrative\n\nIn order to {title.lower()}\n"
            f"As a user\nI want to {title.lower()}\n\n## Norms\n\n- {norm}: {title.lower()}\n\n## Scenarios\n\n"
            f"```gherkin\n@{sc} @{norm.split('@')[0]}\nScenario: {title}\n  When the user does it\n"
            f"  Then it is done\n```\n\n## Non-goals\n\nNone.\n\n## Assumptions\n\nNone.\n")


AU1 = unit("AU-1", "Issue an invoice", "INV-1@11111111", "SC-1")
AU2 = unit("AU-2", "Cancel an invoice", "INV-9@22222222", "SC-2")

NORMS = [  # (id, kind, parent, tree hash prefix, own text)
    ("INV", "file", None, "aaaaaaaa", ""),
    ("INV-1", "item", "INV-3", "11111111", "- An invoice is issued."),
    ("INV-3", "list", "INV", "33333333", ""),
    ("INV-7", "item", "INV-3", "5a627175", "- Each invoice is one row of the CSV."),
    ("INV-9", "item", "INV-3", "22222222", "- An invoice may be cancelled."),
    ("INV-12", "item", "INV-3", "7d6e5f40", "- Every amount has two decimals, with a point."),
    ("INV-15", "item", "INV-3", "9e8d7c6b", "- A cancelled invoice is not exported."),
    ("USR", "file", None, "bbbbbbbb", ""),
    ("USR-4", "paragraph", "USR", "44444444", "The user may see every invoice."),
    ("CUS-1", "paragraph", "USR", "c0c0c0c0", "A customer has a name."),
]


def tree_jsonl(norms=NORMS, retired=("INV-20",)):
    lines = [{"type": "meta", "specs_commit": "0" * 40, "generator_version": "0.1.0", "retired_prefixes": []},
             {"type": "file", "path": "billing/invoices.md", "prefix": "INV", "sha256": "", "insertions": []},
             {"type": "file", "path": "billing/users.md", "prefix": "USR", "sha256": "", "insertions": []}]
    for k, (nid, kind, parent, h, text) in enumerate(norms):
        lines.append({"type": "node", "id": nid, "file": "billing/users.md" if nid.startswith(("USR", "CUS"))
                      else "billing/invoices.md", "kind": kind, "parent": parent, "start": k, "end": k + 1,
                      "own_text": text, "own_hash": h + "0" * 56, "tree_hash": h + "f" * 56, "status": "active",
                      "to_review": False, "changed_since": None})
    for nid in retired:
        lines.append({"type": "node", "id": nid, "file": "billing/invoices.md", "kind": "item", "parent": "INV-3",
                      "start": 0, "end": 1, "own_text": "- gone", "own_hash": "0" * 64, "tree_hash": "1" * 64,
                      "status": "retired", "to_review": False, "changed_since": None})
    return "".join(json.dumps(x, sort_keys=True, separators=(",", ":")) + "\n" for x in lines)


def git(cwd, *args, check=True):
    return subprocess.run(["git", *args], cwd=cwd, env=ENV, capture_output=True, text=True, check=check)


def write(path, text, mode="w"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, mode, **({} if "b" in mode else {"encoding": "utf-8"})) as f:
        f.write(text)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


class Fixture(unittest.TestCase):
    """A project folder `p` with billing-norms and billing-acceptance, cloned from bare remotes."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = os.path.realpath(self.tmp.name)
        self.remotes = os.path.join(self.root, "remotes", "acme")
        self.folder = os.path.join(self.root, "p")
        os.makedirs(self.remotes)
        os.makedirs(self.folder)
        repos = [{"owner": "acme", "name": "billing-specs", "layer": 1, "path": "billing-specs"},
                 {"owner": "acme", "name": "billing-norms", "layer": 2, "path": "billing-norms"},
                 {"owner": "acme", "name": "billing-acceptance", "layer": 3, "path": "billing-acceptance"},
                 {"owner": "acme", "name": "billing-code", "layer": 4, "path": "billing-code"}]
        self.project = json.dumps({"project": "billing", "repositories": repos}, indent=2) + "\n"
        self.norms = self.clone("billing-norms", {
            "data/tree.jsonl": tree_jsonl(),
            "specs-repo-annotated/project.json": self.project,
            "specs-repo-annotated/billing/invoices.md": "# Invoices\n"})
        self.acc = self.clone("billing-acceptance", {
            "project.json": self.project,
            "acceptance.json": self.acceptance(),
            "areas/AA-1.md": AA1, "units/AU-1.md": AU1, "units/AU-2.md": AU2, "units/AU-3.md": AU3,
            "records/AU-3.jsonl": "".join(json.dumps({"kind": k}) + "\n" for k in ("test", "test", "validation")),
            "records/AA-1.jsonl": json.dumps({"kind": "test"}) + "\n",
            "records/AU-2.jsonl": "".join(json.dumps({"kind": k}) + "\n" for k in ("test",) * 3 + ("validation",)),
            "tests/AU-2/test_cancel.py": "# AU-2@00000000: Cancel an invoice\n",
            "tests/AU-2/data/one.csv": "a\n",
            "tests/AU-3/test_export.py": "# AU-3@efc7ae86: Export the invoices to CSV\n"})

    def tearDown(self):
        self.tmp.cleanup()

    def acceptance(self, **fields):
        data = {"default_done_profile": "product", "last_area_id": 1, "last_unit_id": 3, "last_scenario_id": 9,
                "test_command": "", "product": {}}
        data.update(fields)
        return json.dumps(data, indent=2) + "\n"

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
        """A commit pushed to the remote from another clone, so that the clone of the project falls behind."""
        other = os.path.join(self.root, "other-" + name)
        git(self.root, "clone", "-q", os.path.join(self.remotes, name + ".git"), other)
        write(os.path.join(other, rel), text)
        self.commit_all(other)

    def run_script(self, *args, cwd=None):
        return subprocess.run([sys.executable, "-I", SCRIPT, *args], cwd=cwd or self.acc, env=ENV,
                              capture_output=True, text=True)

    def start(self, *extra, cwd=None):
        return self.run_script("start", cwd or self.acc, *extra)

    def started(self):
        r = self.start()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return json.loads(r.stdout)

    def inventory(self, worktree=False):
        commit = git(self.norms, "rev-parse", "origin/main").stdout.strip()
        args = ["inventory", self.acc, "--norms-commit", commit] + (["--worktree"] if worktree else [])
        r = self.run_script(*args)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return json.loads(r.stdout)

    def norms_commit(self):
        return git(self.norms, "rev-parse", "origin/main").stdout.strip()

    def unit_of(self, inv, unit_id):
        return next(u for u in inv["acceptance_units"] if u["unit_id"] == unit_id)

    def area_of(self, inv, area_id):
        return next(a for a in inv["acceptance_areas"] if a["area_id"] == area_id)

    def messages(self, item):
        return [e["message"] for e in item["errors"]]


class Start(Fixture):
    """ACU-57, ACU-58: the checks, in their order."""

    def refused(self, message, *extra, cwd=None):
        r = self.start(*extra, cwd=cwd)
        self.assertEqual((r.returncode, r.stdout.strip()), (1, PREFIX + message), r.stderr)

    def test_acu58_all_pass_and_summary_acu64(self):
        out = self.started()
        self.assertEqual(out["acceptance_repository"], "acme/billing-acceptance")
        self.assertEqual(out["norms_repository"], "acme/billing-norms")
        self.assertEqual(out["specs_repository"], "acme/billing-specs")
        self.assertEqual((out["acceptance_default_branch"], out["norms_default_branch"]), ("main", "main"))
        self.assertEqual(out["norms_commit"], self.norms_commit())
        head = git(self.acc, "rev-parse", "HEAD").stdout.strip()
        self.assertEqual(out["acceptance_commit"], head)
        self.assertEqual(out["summary"],
                         f"Layer 2 at {self.norms_commit()[:7]}: 10 norms. Layer 3 at {head[:7]}: 1 acceptance area, 3 acceptance units; "
                         "1 norm citation changed, 0 retired; 0 format errors.")

    def test_acu58_argument(self):
        self.refused("takes no argument", "--", "AA-1")

    def test_acu58_blank_argument_is_none(self):
        self.assertEqual(self.start("--", "  ").returncode, 0)

    def test_acu58_not_a_git_repository(self):
        other = os.path.join(self.root, "plain")
        os.mkdir(other)
        self.refused("runs only from the acceptance repository", cwd=other)

    def test_acu58_another_layer(self):
        self.refused("runs only from the acceptance repository", cwd=self.norms)

    def test_acu58_no_project_json(self):
        os.remove(os.path.join(self.acc, "project.json"))
        self.refused("runs only from the acceptance repository")

    def test_acu58_no_entry_matches_origin(self):
        git(self.acc, "remote", "set-url", "origin", "https://github.com/acme/elsewhere")
        self.refused("runs only from the acceptance repository")

    def test_acu58_norms_repository_not_at_its_path(self):
        shutil.rmtree(self.norms)
        self.refused(f"acme/billing-norms not found at {self.norms}; run: git clone "
                     f"https://github.com/acme/billing-norms {self.norms}")

    def test_acu58_cannot_fetch_acceptance(self):
        git(self.acc, "remote", "set-url", "origin", os.path.join(self.root, "nowhere", "acme", "billing-acceptance"))
        self.refused("cannot fetch acme/billing-acceptance")

    def test_acu58_cannot_fetch_norms(self):
        git(self.norms, "remote", "set-url", "origin", os.path.join(self.root, "nowhere", "acme", "billing-norms"))
        self.refused("cannot fetch acme/billing-norms")

    def test_acu58_no_default_branch_acceptance(self):
        git(os.path.join(self.remotes, "billing-acceptance.git"), "symbolic-ref", "HEAD", "refs/heads/nope")
        self.refused("cannot find the default branch of acme/billing-acceptance")

    def test_acu58_no_default_branch_norms(self):
        git(os.path.join(self.remotes, "billing-norms.git"), "symbolic-ref", "HEAD", "refs/heads/nope")
        self.refused("cannot find the default branch of acme/billing-norms")

    def test_acu58_no_tree_jsonl(self):
        git(self.norms, "rm", "-q", "data/tree.jsonl")
        self.commit_all(self.norms)
        self.refused("acme/billing-norms has no data/tree.jsonl on main")

    def test_acu58_tree_jsonl_not_valid(self):
        for bad in ('{"type":"node","id":"INV-01"}\n', "[1]\n", '{"type":"meta","specs_commit":NaN}\n', b"\xff\n"):
            with self.subTest(bad=bad):
                write(os.path.join(self.norms, "data", "tree.jsonl"), bad, "wb" if isinstance(bad, bytes) else "w")
                self.commit_all(self.norms)
                self.refused("acme/billing-norms: data/tree.jsonl is not valid")

    def test_acu58_tree_jsonl_crlf_and_blank_lines_read(self):
        write(os.path.join(self.norms, "data", "tree.jsonl"), tree_jsonl().replace("\n", "\r\n") + "   \n")
        self.commit_all(self.norms)
        self.assertEqual(self.start().returncode, 0)

    def test_acu58_no_annotated_project_json(self):
        git(self.norms, "rm", "-q", "specs-repo-annotated/project.json")
        self.commit_all(self.norms)
        self.refused("acme/billing-norms has no specs-repo-annotated/project.json on main")

    def test_acu58_project_json_differs(self):
        write(os.path.join(self.norms, "specs-repo-annotated", "project.json"), self.project + " ")
        self.commit_all(self.norms)
        self.refused("project.json differs from that of acme/billing-norms; run /project-management:sync")

    def test_acu58_not_on_default_branch(self):
        git(self.acc, "checkout", "-q", "-b", "other")
        self.refused("the acceptance repository is not on main")

    def test_acu58_ahead(self):
        write(os.path.join(self.acc, "notes.txt"), "x")
        self.commit_all(self.acc, push=False)
        self.refused("the acceptance repository has commits that are not on origin/main")

    def test_acu58_behind(self):
        self.push_from_other_clone("billing-acceptance", "notes.txt", "x")
        self.refused("the acceptance repository is behind origin/main; run git pull")

    def test_acu58_uncommitted_change_first_in_sorted_order(self):
        write(os.path.join(self.acc, "units", "AU-3.md"), AU3 + "\n")
        write(os.path.join(self.acc, "units", "AU-2.md"), AU2 + "\n")
        write(os.path.join(self.acc, "units", "AU-4.md"), "new")
        self.refused("uncommitted change in units/AU-2.md")

    def test_acu58_staged_deletion_is_a_change(self):
        git(self.acc, "rm", "-q", "--cached", "acceptance.json")
        self.refused("uncommitted change in acceptance.json")

    def test_acu58_untracked(self):
        write(os.path.join(self.acc, "units", "AU-4.md"), "new")
        write(os.path.join(self.acc, "areas", "x", "y.md"), "new")
        self.refused("untracked file areas/x/y.md")

    def test_acu58_other_uncommitted_changes_pass(self):
        write(os.path.join(self.acc, "tests", "AU-3", "test_export.py"), "changed")
        write(os.path.join(self.acc, "records", "AU-3.jsonl"), "changed")
        write(os.path.join(self.acc, "tests", "AU-9", "new.py"), "new")
        self.assertEqual(self.start().returncode, 0)

    def test_acu58_acceptance_json_does_not_meet_acu6(self):
        bad = [self.acceptance(last_unit_id=-1), self.acceptance(last_unit_id="3"), self.acceptance(product=[]),
               self.acceptance(increments=[]), self.acceptance(last_area_id=True),
               self.acceptance(default_done_profile="gold"), "[]"]
        for text in bad:
            with self.subTest(text=text):
                write(os.path.join(self.acc, "acceptance.json"), text)
                self.commit_all(self.acc)
                self.refused("acceptance.json does not meet ACU-6")

    def test_acu58_no_single_entry_of_layer_2(self):
        project = json.loads(self.project)
        project["repositories"] = [r for r in project["repositories"] if r["layer"] != 2]
        write(os.path.join(self.acc, "project.json"), json.dumps(project))
        self.refused("project.json has not exactly one entry of layer 2, the norms repository, with a valid path")

    def test_acu58_folder_does_not_end_with_its_path(self):
        project = json.loads(self.project)
        project["repositories"][2]["path"] = "elsewhere/billing-acceptance"
        write(os.path.join(self.acc, "project.json"), json.dumps(project))
        self.refused("runs only from the acceptance repository")

    def test_acu68_no_entry_of_layer_1(self):
        project = json.loads(self.project)
        project["repositories"] = [r for r in project["repositories"] if r["layer"] != 1]
        text = json.dumps(project, indent=2) + "\n"
        write(os.path.join(self.acc, "project.json"), text)
        self.commit_all(self.acc)
        write(os.path.join(self.norms, "specs-repo-annotated", "project.json"), text)
        self.commit_all(self.norms)
        self.assertIsNone(self.started()["specs_repository"])

    def test_acu58_the_first_check_that_fails_in_their_order(self):
        """Each step adds a failure of an earlier check than the one before, so the message moves up the list."""
        steps = []
        steps.append(("acceptance.json does not meet ACU-6",
                      lambda: (write(os.path.join(self.acc, "acceptance.json"), "[]"), self.commit_all(self.acc))))
        steps.append(("untracked file units/AU-4.md",
                      lambda: write(os.path.join(self.acc, "units", "AU-4.md"), "new")))
        steps.append(("uncommitted change in units/AU-3.md",
                      lambda: write(os.path.join(self.acc, "units", "AU-3.md"), AU3 + "\n")))
        steps.append(("the acceptance repository is behind origin/main; run git pull",
                      lambda: self.push_from_other_clone("billing-acceptance", "notes.txt", "x")))
        steps.append(("the acceptance repository has commits that are not on origin/main",
                      lambda: (write(os.path.join(self.acc, "local.txt"), "x"), git(self.acc, "add", "local.txt"),
                               git(self.acc, "commit", "-q", "-m", "local"))))
        steps.append(("the acceptance repository is not on main",
                      lambda: git(self.acc, "checkout", "-q", "-b", "other")))
        steps.append(("project.json differs from that of acme/billing-norms; run /project-management:sync",
                      lambda: (write(os.path.join(self.norms, "specs-repo-annotated", "project.json"),
                                     self.project + " "), self.commit_all(self.norms))))
        steps.append(("acme/billing-norms has no specs-repo-annotated/project.json on main",
                      lambda: (git(self.norms, "rm", "-q", "specs-repo-annotated/project.json"),
                               self.commit_all(self.norms))))
        steps.append(("acme/billing-norms: data/tree.jsonl is not valid",
                      lambda: (write(os.path.join(self.norms, "data", "tree.jsonl"), "[1]\n"),
                               self.commit_all(self.norms))))
        steps.append(("acme/billing-norms has no data/tree.jsonl on main",
                      lambda: (git(self.norms, "rm", "-q", "data/tree.jsonl"), self.commit_all(self.norms))))
        steps.append(("cannot find the default branch of acme/billing-norms",
                      lambda: git(os.path.join(self.remotes, "billing-norms.git"), "symbolic-ref", "HEAD",
                                  "refs/heads/nope")))
        steps.append(("cannot find the default branch of acme/billing-acceptance",
                      lambda: git(os.path.join(self.remotes, "billing-acceptance.git"), "symbolic-ref", "HEAD",
                                  "refs/heads/nope")))
        steps.append(("cannot fetch acme/billing-norms",
                      lambda: git(self.norms, "remote", "set-url", "origin",
                                  os.path.join(self.root, "nowhere", "acme", "billing-norms"))))
        steps.append(("cannot fetch acme/billing-acceptance",
                      lambda: git(self.acc, "remote", "set-url", "origin",
                                  os.path.join(self.root, "nowhere", "acme", "billing-acceptance"))))
        steps.append((f"acme/billing-norms not found at {self.norms}; run: git clone "
                      f"https://github.com/acme/billing-norms {self.norms}",
                      lambda: shutil.rmtree(self.norms)))
        steps.append(("project.json has not exactly one entry of layer 2, the norms repository, with a valid path",
                      lambda: write(os.path.join(self.acc, "project.json"), self.project.replace(
                          '"layer": 2', '"layer": 7'))))
        steps.append(("runs only from the acceptance repository",
                      lambda: write(os.path.join(self.acc, "project.json"), self.project.replace(
                          '"layer": 2', '"layer": 7').replace('"layer": 3', '"layer": 4'))))
        steps.append(("takes no argument", lambda: None))
        for message, make in steps:
            with self.subTest(message=message):
                make()
                if message == "takes no argument":
                    self.refused(message, "--", "AA-1")
                else:
                    self.refused(message)

    def test_acu59_norms_working_tree_untouched(self):
        self.push_from_other_clone("billing-norms", "data/tree.jsonl",
                                   tree_jsonl(NORMS + [("INV-30", "item", "INV-3", "30303030", "- New.")]))
        git(self.norms, "checkout", "-q", "-b", "old")
        write(os.path.join(self.norms, "data", "tree.jsonl"), "not json\n")
        before = (git(self.norms, "status", "--porcelain").stdout, git(self.norms, "branch").stdout,
                  git(self.norms, "rev-parse", "HEAD", "main").stdout)
        out = self.started()
        self.assertEqual(out["norms_commit"], git(self.norms, "rev-parse", "origin/main").stdout.strip())
        self.assertIn("11 norms", out["summary"])
        after = (git(self.norms, "status", "--porcelain").stdout, git(self.norms, "branch").stdout,
                 git(self.norms, "rev-parse", "HEAD", "main").stdout)
        self.assertEqual(before, after)
        self.assertEqual(read(os.path.join(self.norms, "data", "tree.jsonl")), "not json\n")


class Inventory(Fixture):
    """ACU-60, ACU-61, ACU-62: the inventory and the format errors."""

    def test_acu60_binding_example(self):
        inv = self.inventory()
        self.assertEqual(list(inv), ["norms_commit", "acceptance_commit", "default_done_profile", "next_ids", "norms",
                                     "acceptance_areas", "acceptance_units", "errors"])
        self.assertEqual(inv["norms_commit"], self.norms_commit())
        self.assertEqual(inv["default_done_profile"], "product")
        self.assertEqual(inv["next_ids"], {"acceptance_area": "AA-2", "acceptance_unit": "AU-4", "scenario": "SC-10"})
        self.assertEqual(inv["norms"][3], {"norm_id": "INV-7", "file": "billing/invoices.md", "kind": "item",
                                           "parent_norm_id": "INV-3", "norm_hash": "5a627175",
                                           "own_text": "- Each invoice is one row of the CSV."})
        self.assertNotIn("INV-20", [n["norm_id"] for n in inv["norms"]])
        self.assertEqual([n["norm_id"] for n in inv["norms"]], [n[0] for n in NORMS])
        self.assertEqual(inv["acceptance_areas"], [{
            "area_id": "AA-1", "path": "areas/AA-1.md", "title": "Billing", "area_hash": "3b0900fb",
            "acceptance_units": ["AU-1", "AU-2", "AU-3"],
            "scenarios": [{"scenario_id": "SC-9", "name": "A cancelled invoice is not exported",
                           "scenario_hash": "1bd67ec5", "norms": ["INV-15"], "acceptance_units": ["AU-1", "AU-2", "AU-3"]}],
            "evidence": {"test": 1, "demo": 0, "validation": 0, "deviation": 0, "event": 0}, "errors": []}])
        self.assertEqual(self.unit_of(inv, "AU-3"), {
            "unit_id": "AU-3", "path": "units/AU-3.md", "title": "Export the invoices to CSV", "area_id": "AA-1",
            "done_profile": "product", "unit_hash": "efc7ae86",
            "norm_citations": [
                {"norm_id": "INV-7", "hash_in_acceptance_unit": "5a627175", "citation_status": "current",
                 "hash_in_norms_repository": "5a627175"},
                {"norm_id": "INV-12", "hash_in_acceptance_unit": "0c1d2e3f", "citation_status": "changed",
                 "hash_in_norms_repository": "7d6e5f40"},
                {"norm_id": "INV-15", "hash_in_acceptance_unit": "9e8d7c6b", "citation_status": "current",
                 "hash_in_norms_repository": "9e8d7c6b"}],
            "scenarios": [{"scenario_id": "SC-5", "name": "Three invoices give three rows", "scenario_hash": "147d88d2",
                           "norms": ["INV-7", "INV-12"]},
                          {"scenario_id": "SC-6", "name": "A cancelled invoice gives no row",
                           "scenario_hash": "a67eb609", "norms": ["INV-15"]}],
            "evidence": {"test": 2, "demo": 0, "validation": 1, "deviation": 0, "event": 0}, "errors": []})
        self.assertEqual(inv["errors"], [])
        self.assertEqual([u["unit_id"] for u in inv["acceptance_units"]], ["AU-1", "AU-2", "AU-3"])

    def test_acu60_order_of_the_numbers(self):
        write(os.path.join(self.acc, "units", "AU-10.md"), unit("AU-10", "Ten", "INV-1@11111111", "SC-10"))
        write(os.path.join(self.acc, "acceptance.json"), self.acceptance(last_unit_id=10, last_scenario_id=10))
        self.commit_all(self.acc)
        self.assertEqual([u["unit_id"] for u in self.inventory()["acceptance_units"]], ["AU-1", "AU-2", "AU-3", "AU-10"])

    def test_acu60_profile_line(self):
        write(os.path.join(self.acc, "units", "AU-1.md"),
              unit("AU-1", "Issue an invoice", "INV-1@11111111", "SC-1", extra="Profile: critical\n"))
        self.commit_all(self.acc)
        au1 = self.unit_of(self.inventory(), "AU-1")
        self.assertEqual((au1["done_profile"], au1["errors"]), ("critical", []))

    def test_acu52_title_area_and_profile_outside_the_unit_hash(self):
        before = self.unit_of(self.inventory(), "AU-3")["unit_hash"]
        text = AU3.replace("# AU-3 Export the invoices to CSV", "# AU-3 Export to CSV").replace(
            "Area: AA-1\n", "Area: AA-1\nProfile: critical\n")
        write(os.path.join(self.acc, "units", "AU-3.md"), text)
        self.commit_all(self.acc)
        self.assertEqual(self.unit_of(self.inventory(), "AU-3")["unit_hash"], before)

    def test_acu62_status_of_a_citation(self):
        cases = [("0c1d2e3f", None, "current"), ("7d6e5f40", None, "changed"), (None, "INV-12", "retired"),
                 (None, None, "retired")]
        for hash_now, retired, status in cases:
            with self.subTest(status=status, retired=retired):
                norms = [n for n in NORMS if n[0] != "INV-12"]
                if hash_now:
                    norms.append(("INV-12", "item", "INV-3", hash_now, "- amounts"))
                write(os.path.join(self.norms, "data", "tree.jsonl"),
                      tree_jsonl(norms, ("INV-20",) + ((retired,) if retired else ())))
                self.commit_all(self.norms)
                git(self.norms, "fetch", "-q", "origin")
                c = self.unit_of(self.inventory(), "AU-3")["norm_citations"][1]
                self.assertEqual((c["norm_id"], c["citation_status"], c["hash_in_norms_repository"]),
                                 ("INV-12", status, hash_now if status != "retired" else None))

    def unit_errors(self, text, uid="AU-3"):
        write(os.path.join(self.acc, "units", f"{uid}.md"), text)
        self.commit_all(self.acc)
        return self.unit_of(self.inventory(), uid)

    def test_acu61_format_errors_of_a_unit(self):
        cases = [
            (AU3.replace("# AU-3 Export the invoices to CSV", "# AU-3"), 'heading is not "# AU-3 <title>"', 1),
            (AU3.replace("Area: AA-1", "Area AA-1"), 'no line "Area: <area ID>"', 3),
            (AU3.replace("Area: AA-1", "Area: AA-7"), "acceptance area AA-7 has no file", 3),
            (AU3.replace("Area: AA-1\n", "Area: AA-1\nProfile: gold\n"),
             "done profile gold is not prototype, product or critical", 4),
            (AU3.replace("Area: AA-1\n", "Area: AA-1\nProfile: product\n"),
             "done profile product is the default done profile", 4),
            (AU3.replace("Area: AA-1\n", "Area: AA-1\nIncrement: first\n"), "parts are not those of ACU-8", 4),
            (AU3.replace("## Non-goals", "## Goals"), "parts are not those of ACU-8", None),
            (AU3.replace("As a user of the company\n", ""), "narrative is not In order to, As a, I want", 5),
            (AU3.replace("I want to export", "I wish to export"), "narrative is not In order to, As a, I want", 5),
            (AU3.replace("- INV-7@5a627175: one row per invoice", "- INV-7@5A627175: one row per invoice"),
             "not a norm citation", 13),
            (AU3.replace("- INV-12@0c1d2e3f: amounts with two decimals", "- INV-7@5a627175: again"),
             "INV-7 is cited twice", 14),
            (AU3.replace("@SC-6 @INV-15", "@SC-6"), "INV-15 is checked by no scenario", 15),
            (AU3.replace("@SC-6 @INV-15", "@SC-6 @INV-15 @INV-99"), "tag @INV-99 is not in ## Norms", 27),
            (AU3.replace("- The unit does not export to PDF.", "Nothing to say."),
             "## Non-goals is not a list or None.", None),
            (AU3.replace("(environment).", "(nowhere)."), "assumption rests on no norm and not on (environment)", 41),
            (AU3.replace("(USR-4).", "(USR-99)."), "assumption rests on no norm and not on (environment)", 42),
            (AU3.replace("@SC-6 @INV-15", "@SC-6 @INV-15 @wip"), "tag @wip is not @SC-<n> or @<norm ID>", 27),
            (AU3.replace("@SC-6 @INV-15", "@SC-6 @INV-15 @unit:AU-1"),
             "tag @unit:AU-1 is not @SC-<n> or @<norm ID>", 27),
            (AU3.replace("Scenario: A cancelled", "Scenario Outline: A cancelled"),
             "Scenario Outline: is not allowed in ## Scenarios", 28),
            (AU3.replace("```gherkin", "```"), "## Scenarios is not one gherkin block", 19),
            (AU3.replace("@SC-5 @INV-7", "@INV-7"),
             'scenario "Three invoices give three rows" has not exactly one tag @SC-<n>', 20),
            (AU3.replace("@SC-5 @INV-7", "@SC-05 @INV-7"),
             'scenario "Three invoices give three rows" has not exactly one tag @SC-<n>', 20),
            (AU3.replace("@SC-5 @INV-7", "@SC-5 @SC-7 @INV-7"),
             'scenario "Three invoices give three rows" has not exactly one tag @SC-<n>', 20),
        ]
        for text, message, line in cases:
            with self.subTest(message=message):
                au3 = self.unit_errors(text)
                self.assertIn(message, self.messages(au3))
                found = next(e for e in au3["errors"] if e["message"] == message)
                if line is not None:
                    self.assertEqual(found["line"], line)

    def test_acu61_no_citation(self):
        text = AU3.replace("- INV-7@5a627175: one row per invoice\n- INV-12@0c1d2e3f: amounts with two decimals\n"
                           "- INV-15@9e8d7c6b: cancelled invoices are not exported\n", "")
        self.assertIn("no norm citation in ## Norms", self.messages(self.unit_errors(text)))

    def test_acu61_not_utf8(self):
        write(os.path.join(self.acc, "units", "AU-3.md"), AU3.encode("utf-8") + b"\xff", "wb")
        self.commit_all(self.acc)
        au3 = self.unit_of(self.inventory(), "AU-3")
        self.assertEqual(au3["errors"], [{"line": None, "message": "not UTF-8"}])
        self.assertEqual((au3["title"], au3["area_id"], au3["unit_hash"], au3["norm_citations"], au3["scenarios"]),
                         (None, None, None, [], []))

    def test_acu61_a_valid_unit_has_no_error(self):
        self.assertEqual(self.unit_errors(AU3)["errors"], [])

    def test_acu61_format_errors_of_an_area(self):
        cases = [
            (AA1.replace("# AA-1 Billing", "# AA-1 "), 'heading is not "# AA-1 <title>"'),
            (AA1.replace("The people of the company issue, cancel and export the invoices of their customers.\n", ""),
             "parts are not those of ACU-7"),
            (AA1.replace("## Purpose", "## Why"), "parts are not those of ACU-7"),
            (AA1.replace("# AA-1 Billing\n", "# AA-1 Billing\nIntro\n"), "parts are not those of ACU-7"),
            (AA1.replace("@unit:AU-1 @unit:AU-2 @unit:AU-3", "@unit:AU-3"), "scenario SC-9 crosses fewer than two acceptance units"),
            (AA1.replace("@unit:AU-3", "@unit:AU-3 @unit:AU-8"), "AU-8 is not an acceptance unit of AA-1"),
            (AA1.replace("@INV-15", "@INV-15 @INV-40"), "tag @INV-40 is in ## Norms of no acceptance unit it crosses"),
            (AA1.replace("```gherkin", "```"), "## Scenarios is not one gherkin block"),
        ]
        for text, message in cases:
            with self.subTest(message=message):
                write(os.path.join(self.acc, "areas", "AA-1.md"), text)
                self.commit_all(self.acc)
                self.assertIn(message, self.messages(self.area_of(self.inventory(), "AA-1")))

    def test_acu7_scenarios_none(self):
        text = AA1[:AA1.index("```gherkin")] + "None.\n"
        write(os.path.join(self.acc, "areas", "AA-1.md"), text)
        self.commit_all(self.acc)
        aa1 = self.area_of(self.inventory(), "AA-1")
        self.assertEqual((aa1["errors"], aa1["scenarios"]), ([], []))

    def test_acu61_errors_of_the_repository(self):
        write(os.path.join(self.acc, "units", "AU-2.md"), AU2.replace("@SC-2", "@SC-5"))
        write(os.path.join(self.acc, "units", "AU-9.md"), unit("AU-9", "Nine", "INV-1@11111111", "SC-12"))
        write(os.path.join(self.acc, "units", "notes.md"), "x")
        write(os.path.join(self.acc, "areas", "AU-4.md"), "x")
        self.commit_all(self.acc)
        errors = self.inventory()["errors"]
        self.assertIn({"path": "units/AU-2.md", "line": 18, "message": "SC-5 is the ID of more than one scenario"},
                      errors)
        self.assertIn({"path": "units/AU-9.md", "line": None,
                       "message": "AU-9 is greater than last_unit_id of acceptance.json"}, errors)
        self.assertIn({"path": "units/AU-9.md", "line": 18,
                       "message": "SC-12 is greater than last_scenario_id of acceptance.json"}, errors)
        self.assertIn({"path": "units/notes.md", "line": None, "message": "not the file of an acceptance area or an acceptance unit"},
                      errors)
        self.assertIn({"path": "areas/AU-4.md", "line": None, "message": "not the file of an acceptance area or an acceptance unit"},
                      errors)

    def test_acu61_worktree_already_given_and_last_fields(self):
        git(self.acc, "rm", "-q", "units/AU-2.md")
        self.commit_all(self.acc)
        write(os.path.join(self.acc, "units", "AU-2.md"), AU2.replace("@SC-2", "@SC-3"))
        write(os.path.join(self.acc, "units", "AU-5.md"), unit("AU-5", "Five", "INV-1@11111111", "SC-11"))
        write(os.path.join(self.acc, "areas", "AA-2.md"), AA1.replace("AA-1", "AA-2").replace("@SC-9", "@SC-10"))
        write(os.path.join(self.acc, "acceptance.json"), self.acceptance(last_unit_id=4))
        errors = self.inventory(worktree=True)["errors"]
        messages = [e["message"] for e in errors]
        self.assertIn("AU-2 was already given", messages)
        self.assertIn("SC-3 was already given", messages)
        self.assertIn("last_unit_id of acceptance.json is 4, not 5", messages)
        self.assertIn("last_area_id of acceptance.json is 1, not 2", messages)
        self.assertIn("last_scenario_id of acceptance.json is 9, not 11", messages)
        self.assertIn({"path": "acceptance.json", "line": 4,
                       "message": "last_unit_id of acceptance.json is 4, not 5"}, errors)

    def test_acu61_moved_scenario_is_not_new(self):
        text = AU3.replace("@SC-6 @INV-15\nScenario: A cancelled invoice gives no row\n"
                           "  Given a user with 2 issued invoices and 1 cancelled invoice\n"
                           "  When the user runs \"app export --format csv\"\n  Then the CSV has 2 rows\n", "")
        text = text.replace("@SC-5 @INV-7 @INV-12", "@SC-5 @INV-7 @INV-12 @INV-15")
        write(os.path.join(self.acc, "units", "AU-3.md"), text)
        write(os.path.join(self.acc, "units", "AU-1.md"), AU1.replace(
            "```\n\n## Non-goals", "\n@SC-6 @INV-1\nScenario: Moved\n  Then moved\n```\n\n## Non-goals"))
        self.assertEqual(self.inventory(worktree=True)["errors"], [])

    def test_acu61_as_an(self):
        self.assertEqual(self.unit_errors(AU3.replace("As a user of the company", "As an accountant"))["errors"], [])

    def test_acu61_assumptions_not_a_list(self):
        au3 = self.unit_errors(AU3.replace("- The invoices are already in the database (environment).", "Text."))
        self.assertIn("## Assumptions is not a list or None.", self.messages(au3))

    def test_acu61_an_area_that_is_not_utf8(self):
        write(os.path.join(self.acc, "areas", "AA-1.md"), AA1.encode("utf-8") + b"\xff", "wb")
        self.commit_all(self.acc)
        aa1 = self.area_of(self.inventory(), "AA-1")
        self.assertEqual(aa1["errors"], [{"line": None, "message": "not UTF-8"}])
        self.assertEqual((aa1["title"], aa1["area_hash"], aa1["scenarios"]), (None, None, []))

    def test_acu61_area_ids_greater_and_already_given(self):
        write(os.path.join(self.acc, "areas", "AA-3.md"), AA1.replace("AA-1", "AA-3").replace(
            "@SC-9 @unit:AU-1 @unit:AU-2 @unit:AU-3 @INV-15\n", "@SC-8\n"))
        self.commit_all(self.acc)
        errors = self.inventory()["errors"]
        self.assertIn({"path": "areas/AA-3.md", "line": None,
                       "message": "AA-3 is greater than last_area_id of acceptance.json"}, errors)
        git(self.acc, "rm", "-q", "areas/AA-3.md")
        write(os.path.join(self.acc, "acceptance.json"), self.acceptance(last_area_id=3))
        self.commit_all(self.acc)
        write(os.path.join(self.acc, "areas", "AA-2.md"), AA1.replace("AA-1", "AA-2").replace("@SC-9", "@SC-10"))
        write(os.path.join(self.acc, "acceptance.json"), self.acceptance(last_area_id=3, last_scenario_id=10))
        messages = [e["message"] for e in self.inventory(worktree=True)["errors"]]
        self.assertIn("AA-2 was already given", messages)

    def test_acu61_acu65_a_field_lower_than_an_id_at_head(self):
        write(os.path.join(self.acc, "units", "AU-9.md"), unit("AU-9", "Nine", "INV-1@11111111", "SC-8"))
        write(os.path.join(self.acc, "acceptance.json"), self.acceptance(last_unit_id=8))
        self.commit_all(self.acc)
        inv = self.inventory()
        self.assertIn("AU-9 is greater than last_unit_id of acceptance.json", [e["message"] for e in inv["errors"]])
        self.assertEqual(inv["next_ids"], {"acceptance_area": "AA-2", "acceptance_unit": "AU-10", "scenario": "SC-10"})
        # A change of AU-9 is not blocked: ids raises the field, and the check passes.
        write(os.path.join(self.acc, "units", "AU-9.md"), unit("AU-9", "Nine again", "INV-1@11111111", "SC-8"))
        self.assertEqual(json.loads(self.run_script("ids", self.acc).stdout), {"last_unit_id": 9})
        commit = self.norms_commit()
        r = self.run_script("check", self.acc, "--norms-commit", commit)
        self.assertEqual(json.loads(r.stdout)["problems"], [], r.stdout)
        # Deleting AU-9 does not give its ID again.
        os.remove(os.path.join(self.acc, "units", "AU-9.md"))
        self.run_script("ids", self.acc)
        self.assertEqual(json.loads(read(os.path.join(self.acc, "acceptance.json")))["last_unit_id"], 9)
        self.assertEqual(self.inventory(worktree=True)["next_ids"]["acceptance_unit"], "AU-10")

    def test_acu64_singular_and_plural(self):
        sys.path.insert(0, os.path.dirname(SCRIPT))
        try:
            import define
        finally:
            sys.path.pop(0)
        unit_one = {"norm_citations": [{"citation_status": "changed"}, {"citation_status": "retired"}],
                    "errors": [{"message": "x"}]}
        inv = {"norms_commit": "9fceb02d0", "acceptance_commit": "1a410efbd", "norms": [{}], "acceptance_areas": [
            {"errors": []}], "acceptance_units": [unit_one], "errors": []}
        self.assertEqual(define.summary(inv), "Layer 2 at 9fceb02: 1 norm. Layer 3 at 1a410ef: 1 acceptance area, "
                                              "1 acceptance unit; 1 norm citation changed, 1 retired; 1 format error.")
        inv.update(norms=[], acceptance_areas=[], acceptance_units=[], errors=[])
        self.assertEqual(define.summary(inv), "Layer 2 at 9fceb02: 0 norms. Layer 3 at 1a410ef: 0 acceptance areas, "
                                              "0 acceptance units; 0 norm citations changed, 0 retired; "
                                              "0 format errors.")

    def test_python_3_9(self):
        python = "/usr/bin/python3"
        if not os.path.exists(python):
            self.skipTest("no /usr/bin/python3")
        version = subprocess.run([python, "-c", "import sys; print(sys.version_info[:2] >= (3, 9))"],
                                 capture_output=True, text=True).stdout.strip()
        if version != "True":
            self.skipTest("/usr/bin/python3 is older than 3.9")
        path = os.path.join(self.acc, "units", "AU-3.md")
        r = subprocess.run([python, "-I", SCRIPT, "hash", path], capture_output=True, text=True, env=ENV)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)["unit_hash"], "efc7ae86")
        ci = os.path.join(PLUGIN, "scripts", "acceptance_ci.py")
        self.assertEqual(subprocess.run([python, "-I", ci, "--help"], capture_output=True).returncode, 0)

    def test_acu59_norms_commit_must_be_the_head_of_a_branch_of_origin(self):
        git(self.norms, "checkout", "-q", "-b", "old")
        write(os.path.join(self.norms, "data", "tree.jsonl"), tree_jsonl([n for n in NORMS if n[0] != "INV-7"]))
        self.commit_all(self.norms, push=False)
        for bad in ("HEAD", "origin/main", self.norms_commit()[:7], git(self.norms, "rev-parse", "HEAD").stdout.strip(),
                    self.norms_commit().upper()):
            with self.subTest(bad=bad):
                r = self.run_script("inventory", self.acc, "--norms-commit", bad)
                self.assertEqual(r.returncode, 1)
                self.assertTrue(r.stdout.startswith(PREFIX + f"--norms-commit {bad} is not the head of a branch"),
                                r.stdout)

    def test_acu60_worktree_reads_the_disk(self):
        write(os.path.join(self.acc, "units", "AU-3.md"), AU3.replace("INV-12@0c1d2e3f", "INV-12@7d6e5f40"))
        inv = self.inventory(worktree=True)
        self.assertEqual(self.unit_of(inv, "AU-3")["norm_citations"][1]["citation_status"], "current")
        self.assertEqual(self.unit_of(self.inventory(), "AU-3")["norm_citations"][1]["citation_status"], "changed")


class Writing(Fixture):
    """ACU-65, ACU-69, ACU-70, ACU-71, ACU-72, ACU-73: after the proposal is final."""

    def script(self, *args, code=0):
        r = self.run_script(*args)
        self.assertEqual(r.returncode, code, r.stdout + r.stderr)
        return r.stdout

    def check(self, code=0):
        return json.loads(self.script("check", self.acc, "--norms-commit", self.norms_commit(), code=code))

    def commit(self, *changes, code=0):
        args = ["commit", self.acc, "--norms-commit", self.norms_commit()]
        for change in changes:
            args += ["--change", change]
        r = self.run_script(*args)
        self.assertEqual(r.returncode, code, r.stdout + r.stderr)
        return json.loads(r.stdout) if code == 0 else r.stdout.strip()

    def approve(self, plan):
        return subprocess.run(plan["command"], shell=True, env=ENV, capture_output=True, text=True)

    def remote_log(self):
        return git(os.path.join(self.remotes, "billing-acceptance.git"), "log", "-1", "--format=%B%n--%n",
                   "--name-status", "main").stdout

    def add_au4(self):
        write(os.path.join(self.acc, "units", "AU-4.md"),
              unit("AU-4", "Register a customer", "CUS-1@c0c0c0c0", "SC-10"))

    def test_acu65_ids_sets_the_fields(self):
        self.add_au4()
        self.assertEqual(json.loads(self.script("ids", self.acc)), {"last_unit_id": 4, "last_scenario_id": 10})
        data = json.loads(read(os.path.join(self.acc, "acceptance.json")))
        self.assertEqual((data["last_area_id"], data["last_unit_id"], data["last_scenario_id"]), (1, 4, 10))
        self.assertEqual(read(os.path.join(self.acc, "acceptance.json")),
                         self.acceptance(last_unit_id=4, last_scenario_id=10))

    def test_acu65_a_deleted_id_is_never_given_again(self):
        os.remove(os.path.join(self.acc, "units", "AU-3.md"))
        self.assertEqual(json.loads(self.script("ids", self.acc)), {})
        inv = self.inventory(worktree=True)
        self.assertEqual(inv["next_ids"]["acceptance_unit"], "AU-4")

    def test_acu69_check_passes_and_fails(self):
        self.add_au4()
        self.script("ids", self.acc)
        self.assertEqual(self.check(), {"written": ["acceptance.json", "units/AU-4.md"], "problems": []})
        write(os.path.join(self.acc, "units", "AU-4.md"),
              unit("AU-4", "Register a customer", "CUS-1@00000000", "SC-10"))
        problems = self.check(code=1)["problems"]
        self.assertEqual([p["message"] for p in problems], ["CUS-1@00000000 is changed; its norm hash at the norms commit is c0c0c0c0"])

    def test_acu69_written_unit_must_cite_current_hashes(self):
        write(os.path.join(self.acc, "units", "AU-3.md"), AU3.replace("amounts with two decimals", "two decimals"))
        problems = self.check(code=1)["problems"]
        self.assertEqual(problems[0]["path"], "units/AU-3.md")
        self.assertIn("INV-12@0c1d2e3f is changed", problems[0]["message"])

    def test_acu69_error_already_at_head_does_not_stop(self):
        write(os.path.join(self.acc, "units", "AU-2.md"), AU2.replace("Area: AA-1", "Area AA-1"))
        self.commit_all(self.acc)
        self.add_au4()
        self.script("ids", self.acc)
        self.assertEqual(self.check()["problems"], [])

    def test_acu69_new_error_stops(self):
        self.add_au4()
        self.assertIn("last_unit_id of acceptance.json is 3, not 4",
                      [p["message"] for p in self.check(code=1)["problems"]])

    def test_acu73_other_fields_of_acceptance_json(self):
        write(os.path.join(self.acc, "acceptance.json"), self.acceptance(test_command="pytest"))
        self.assertIn("only last_area_id, last_unit_id and last_scenario_id may change (ACU-73)",
                      [p["message"] for p in self.check(code=1)["problems"]])

    def test_acu71_one_commit_add_unit(self):
        self.add_au4()
        self.script("ids", self.acc)
        write(os.path.join(self.acc, "tests", "AU-3", "test_export.py"), "another session")
        plan = self.commit("add AU-4")
        self.assertEqual(plan["paths"], ["acceptance.json", "units/AU-4.md"])
        self.assertEqual(plan["message"], "docs: add acceptance unit\n\nadd AU-4")
        self.assertIn("units/AU-4.md", plan["display"])
        self.assertNotIn("git add -A", plan["command"])
        r = self.approve(plan)
        self.assertEqual(r.returncode, 0, r.stderr)
        log = self.remote_log()
        self.assertTrue(log.startswith("docs: add acceptance unit\n\nadd AU-4\n"), log)
        self.assertIn("A\tunits/AU-4.md", log)
        self.assertIn("M\tacceptance.json", log)
        self.assertNotIn("tests/AU-3", log)
        self.assertEqual(read(os.path.join(self.acc, "tests", "AU-3", "test_export.py")), "another session")

    def test_acu71_commit_only_its_paths_when_others_are_staged(self):
        write(os.path.join(self.acc, "tests", "AU-3", "staged.py"), "x")
        git(self.acc, "add", "tests/AU-3/staged.py")
        self.add_au4()
        self.script("ids", self.acc)
        r = self.approve(self.commit("add AU-4"))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("staged.py", self.remote_log())

    def test_acu70_delete_unit_with_its_tests(self):
        deleted = json.loads(self.script("delete-tests", self.acc, "AU-2"))
        self.assertEqual(deleted, ["tests/AU-2/data/one.csv", "tests/AU-2/test_cancel.py"])
        self.assertFalse(os.path.exists(os.path.join(self.acc, "tests", "AU-2")))
        os.remove(os.path.join(self.acc, "units", "AU-2.md"))
        write(os.path.join(self.acc, "areas", "AA-1.md"), AA1.replace(" @unit:AU-2", ""))
        plan = self.commit("delete AU-2", "change AA-1")
        self.assertEqual(plan["paths"], ["areas/AA-1.md", "tests/AU-2/data/one.csv", "tests/AU-2/test_cancel.py",
                                         "units/AU-2.md"])
        self.assertEqual(plan["message"], "docs: change acceptance areas and units\n\ndelete AU-2\nchange AA-1")
        r = self.approve(plan)
        self.assertEqual(r.returncode, 0, r.stderr)
        log = self.remote_log()
        for line in ("D\tunits/AU-2.md", "D\ttests/AU-2/test_cancel.py", "D\ttests/AU-2/data/one.csv",
                     "M\tareas/AA-1.md"):
            self.assertIn(line, log)
        self.assertTrue(os.path.exists(os.path.join(self.acc, "records", "AU-3.jsonl")))
        # ACU-70: the record of the deleted unit stays as it is, at the remote and in the working tree.
        record = git(self.acc, "show", "HEAD~1:records/AU-2.jsonl").stdout
        self.assertEqual(git(os.path.join(self.remotes, "billing-acceptance.git"), "show",
                             "main:records/AU-2.jsonl").stdout, record)
        self.assertEqual(read(os.path.join(self.acc, "records", "AU-2.jsonl")), record)
        self.assertNotIn("records/AU-2.jsonl", plan["paths"])
        self.assertEqual(self.unit_of(self.inventory(), "AU-1")["unit_id"], "AU-1")

    def test_acu70_delete_refused_while_its_tests_are_there(self):
        os.remove(os.path.join(self.acc, "units", "AU-2.md"))
        write(os.path.join(self.acc, "areas", "AA-1.md"), AA1.replace(" @unit:AU-2", ""))
        self.assertEqual(self.commit("delete AU-2", "change AA-1", code=1),
                         PREFIX + "delete AU-2: tests/AU-2/ is not deleted (ACU-70)")

    def test_acu70_a_scenario_left_with_fewer_than_two_units_is_removed(self):
        for uid in ("AU-1", "AU-2"):
            self.script("delete-tests", self.acc, uid)
            os.remove(os.path.join(self.acc, "units", f"{uid}.md"))
        write(os.path.join(self.acc, "areas", "AA-1.md"), AA1[:AA1.index("```gherkin")] + "None.\n")
        self.assertEqual(json.loads(self.script("ids", self.acc)), {})
        plan = self.commit("delete AU-1", "delete AU-2", "change AA-1")
        self.assertEqual(self.approve(plan).returncode, 0)
        self.assertNotIn("SC-9", read(os.path.join(self.acc, "areas", "AA-1.md")))
        self.assertEqual(self.inventory()["next_ids"], {"acceptance_area": "AA-2", "acceptance_unit": "AU-4", "scenario": "SC-10"})

    def test_acu70_a_unit_moves_to_another_area(self):
        write(os.path.join(self.acc, "units", "AU-3.md"), AU3.replace("INV-12@0c1d2e3f", "INV-12@7d6e5f40"))
        self.commit_all(self.acc)
        before = self.unit_of(self.inventory(), "AU-3")["unit_hash"]
        write(os.path.join(self.acc, "areas", "AA-2.md"),
              "# AA-2 Exports\n\n## Purpose\n\nThe exports.\n\n## Scenarios\n\nNone.\n")
        write(os.path.join(self.acc, "units", "AU-3.md"),
              AU3.replace("Area: AA-1", "Area: AA-2").replace("INV-12@0c1d2e3f", "INV-12@7d6e5f40"))
        write(os.path.join(self.acc, "areas", "AA-1.md"),
              AA1.replace(" @unit:AU-3", "").replace(" @INV-15", ""))
        self.script("ids", self.acc)
        plan = self.commit("add AA-2", "change AU-3", "change AA-1")
        self.assertEqual(plan["paths"], ["acceptance.json", "areas/AA-1.md", "areas/AA-2.md", "units/AU-3.md"])
        self.assertEqual(self.approve(plan).returncode, 0)
        inv = self.inventory()
        self.assertEqual((self.unit_of(inv, "AU-3")["area_id"], self.unit_of(inv, "AU-3")["unit_hash"]), ("AA-2", before))
        self.assertTrue(os.path.exists(os.path.join(self.acc, "tests", "AU-3", "test_export.py")))
        self.assertEqual(self.area_of(inv, "AA-1")["scenarios"][0]["acceptance_units"], ["AU-1", "AU-2"])

    def test_acu71_a_file_that_belongs_to_no_change(self):
        write(os.path.join(self.acc, "areas", "AA-1.md"), AA1 + "\n")
        write(os.path.join(self.acc, "units", "AU-1.md"), AU1.replace("Issue an invoice", "Issue one invoice"))
        self.assertEqual(self.commit("change AU-1", code=1),
                         PREFIX + "areas/AA-1.md differs from HEAD, and no change of the commit names it (ACU-71)")

    def test_acu67_a_scenario_moved_out_of_another_unit_belongs_to_the_change(self):
        au3 = AU3.replace("INV-12@0c1d2e3f", "INV-12@7d6e5f40").replace("- INV-15@9e8d7c6b: cancelled invoices are not exported\n", "").replace(
            "\n@SC-6 @INV-15\nScenario: A cancelled invoice gives no row\n"
            "  Given a user with 2 issued invoices and 1 cancelled invoice\n"
            "  When the user runs \"app export --format csv\"\n  Then the CSV has 2 rows\n", "")
        write(os.path.join(self.acc, "units", "AU-3.md"), au3)
        write(os.path.join(self.acc, "units", "AU-4.md"),
              "# AU-4 Leave out the cancelled invoices\n\nArea: AA-1\n\n## Narrative\n\nIn order to x\n"
              "As a user\nI want y\n\n## Norms\n\n- INV-15@9e8d7c6b: cancelled\n\n## Scenarios\n\n```gherkin\n"
              "@SC-6 @INV-15\nScenario: A cancelled invoice gives no row\n  Then the CSV has 2 rows\n```\n\n"
              "## Non-goals\n\nNone.\n\n## Assumptions\n\nNone.\n")
        write(os.path.join(self.acc, "areas", "AA-1.md"), AA1.replace("@unit:AU-3", "@unit:AU-3 @unit:AU-4"))
        self.script("ids", self.acc)
        r = self.run_script("commit", self.acc, "--norms-commit", self.norms_commit(), "--change", "add AU-4")
        # AA-1 crosses AU-3, which no longer cites INV-15 of the tag of SC-9; AU-3 lost SC-6 to AU-4.
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertEqual(json.loads(r.stdout)["paths"], ["acceptance.json", "areas/AA-1.md", "units/AU-3.md",
                                                         "units/AU-4.md"])

    def test_acu69_a_citation_that_is_not_current_has_its_line(self):
        write(os.path.join(self.acc, "units", "AU-3.md"), AU3.replace("amounts with two decimals", "two decimals"))
        problem = self.check(code=1)["problems"][0]
        self.assertEqual((problem["path"], problem["line"]), ("units/AU-3.md", 14))

    def test_acu71_the_diff_of_a_new_and_a_deleted_file(self):
        self.script("delete-tests", self.acc, "AU-2")
        os.remove(os.path.join(self.acc, "units", "AU-2.md"))
        write(os.path.join(self.acc, "areas", "AA-1.md"), AA1.replace(" @unit:AU-2", ""))
        display = self.commit("delete AU-2", "change AA-1")["display"]
        self.assertIn("--- a/units/AU-2.md\n+++ /dev/null\n", display)
        self.assertIn("--- a/tests/AU-2/test_cancel.py\n+++ /dev/null\n", display)
        os.remove(os.path.join(self.acc, "areas", "AA-1.md"))
        self.script("rollback", self.acc, "--change", "delete AU-2")
        self.add_au4()
        self.script("ids", self.acc)
        self.assertIn("--- /dev/null\n+++ b/units/AU-4.md\n", self.commit("add AU-4")["display"])

    def test_acu71_subjects(self):
        cases = [(["add AU-4"], "docs: add acceptance unit"), (["change AU-3"], "docs: change acceptance unit"),
                 (["delete AU-2"], "docs: delete acceptance unit"), (["add AA-2"], "docs: add acceptance area"),
                 (["change AA-1"], "docs: change acceptance area"), (["delete AA-1"], "docs: delete acceptance area"),
                 (["add AU-4", "change AU-3"], "docs: change acceptance areas and units")]
        sys.path.insert(0, os.path.dirname(SCRIPT))
        try:
            import define
        finally:
            sys.path.pop(0)
        for changes, subject in cases:
            with self.subTest(subject=subject):
                self.assertEqual(define.message(define.parse_changes(changes))[0], subject)

    def test_acu71_change_must_match_the_files(self):
        self.add_au4()
        self.script("ids", self.acc)
        self.assertIn("change AU-4", self.commit("change AU-4", code=1))

    def test_acu71_checks_before_the_command(self):
        self.add_au4()
        out = self.commit("add AU-4", code=1)
        self.assertTrue(out.startswith(PREFIX + "the checks of ACU-69 fail"), out)

    def test_acu71_default_branch_moved(self):
        self.add_au4()
        self.script("ids", self.acc)
        self.push_from_other_clone("billing-acceptance", "notes.txt", "x")
        self.assertEqual(self.commit("add AU-4", code=3), PREFIX + "origin/main moved; run the skill again")

    def test_acu71_the_default_branch_moves_after_the_command_is_shown(self):
        self.add_au4()
        self.script("ids", self.acc)
        plan = self.commit("add AU-4")
        self.push_from_other_clone("billing-acceptance", "notes.txt", "x")
        head = git(self.acc, "rev-parse", "HEAD").stdout
        r = self.approve(plan)
        self.assertEqual((r.returncode, r.stdout.strip()), (3, PREFIX + "origin/main moved; run the skill again"))
        self.assertEqual(git(self.acc, "rev-parse", "HEAD").stdout, head)
        self.assertEqual(git(self.acc, "diff", "--cached", "--name-only").stdout, "")
        self.assertNotIn("AU-4", self.remote_log())

    def test_acu71_refused_command_after_an_earlier_change_was_pushed(self):
        self.add_au4()
        self.script("ids", self.acc)
        self.assertEqual(self.approve(self.commit("add AU-4")).returncode, 0)
        write(os.path.join(self.acc, "units", "AU-5.md"), unit("AU-5", "Five", "CUS-1@c0c0c0c0", "SC-11"))
        write(os.path.join(self.acc, "units", "AU-6.md"), unit("AU-6", "Six", "INV-1@11111111", "SC-12"))
        self.script("ids", self.acc)
        self.commit("add AU-5", "add AU-6")  # shown, and refused by the requester
        restored = json.loads(self.script("rollback", self.acc, "--change", "add AU-5", "--change", "add AU-6"))
        self.assertEqual(restored, ["acceptance.json", "units/AU-5.md", "units/AU-6.md"])
        self.assertEqual(git(self.acc, "status", "--porcelain").stdout, "")
        self.assertEqual(json.loads(read(os.path.join(self.acc, "acceptance.json")))["last_unit_id"], 4)
        # The next change takes the IDs that follow those already committed (ACU-65).
        self.assertEqual(self.inventory()["next_ids"], {"acceptance_area": "AA-2", "acceptance_unit": "AU-5", "scenario": "SC-11"})

    def test_acu71_rollback(self):
        self.script("delete-tests", self.acc, "AU-2")
        os.remove(os.path.join(self.acc, "units", "AU-2.md"))
        self.add_au4()
        write(os.path.join(self.acc, "units", "AU-3.md"), AU3 + "\n- more\n")
        write(os.path.join(self.acc, "tests", "AU-3", "test_export.py"), "another session")
        restored = json.loads(self.script("rollback", self.acc, "--change", "delete AU-2"))
        self.assertEqual(restored, ["tests/AU-2/data/one.csv", "tests/AU-2/test_cancel.py", "units/AU-2.md",
                                    "units/AU-3.md", "units/AU-4.md"])
        self.assertEqual(git(self.acc, "status", "--porcelain").stdout, " M tests/AU-3/test_export.py\n")

    def test_acu71_one_commit_per_change(self):
        self.add_au4()
        self.script("ids", self.acc)
        self.assertEqual(self.approve(self.commit("add AU-4")).returncode, 0)
        write(os.path.join(self.acc, "units", "AU-3.md"), AU3.replace("INV-12@0c1d2e3f", "INV-12@7d6e5f40"))
        plan = self.commit("change AU-3")
        self.assertEqual(plan["paths"], ["units/AU-3.md"])
        self.assertEqual(self.approve(plan).returncode, 0)
        self.assertTrue(self.remote_log().startswith("docs: change acceptance unit\n\nchange AU-3\n"))

    def test_acu72_next_line(self):
        since = git(self.acc, "rev-parse", "HEAD").stdout.strip()
        self.assertEqual(self.script("next", self.acc, "--since", since), "")
        write(os.path.join(self.acc, "units", "AU-3.md"), AU3.replace("# AU-3 Export the invoices to CSV",
                                                                     "# AU-3 Export to CSV"))
        self.commit_all(self.acc)
        self.assertEqual(self.script("next", self.acc, "--since", since).strip(),
                         "Next: the implementation planner updates plan.json.")
        write(os.path.join(self.acc, "units", "AU-3.md"), AU3.replace("INV-12@0c1d2e3f", "INV-12@7d6e5f40"))
        self.add_au4()
        write(os.path.join(self.acc, "areas", "AA-1.md"), AA1 + "\n")
        self.commit_all(self.acc)
        self.assertEqual(self.script("next", self.acc, "--since", since).strip(),
                         "Next: the implementation planner updates plan.json; "
                         "the test agent updates the acceptance tests of AU-3, AU-4.")
        write(os.path.join(self.acc, "areas", "AA-1.md"), AA1.replace("Then the CSV", "Then the file"))
        self.commit_all(self.acc)
        self.assertIn("of AA-1, AU-3, AU-4.", self.script("next", self.acc, "--since", since))

    def test_acu72_only_a_deletion(self):
        since = git(self.acc, "rev-parse", "HEAD").stdout.strip()
        self.script("delete-tests", self.acc, "AU-2")
        os.remove(os.path.join(self.acc, "units", "AU-2.md"))
        self.commit_all(self.acc)
        self.assertEqual(self.script("next", self.acc, "--since", since).strip(),
                         "Next: the implementation planner updates plan.json.")

    def test_hash_command(self):
        path = os.path.join(self.acc, "units", "AU-3.md")
        out = json.loads(self.script("hash", path))
        self.assertEqual((out["unit_hash"], [s["scenario_hash"] for s in out["scenarios"]]),
                         ("efc7ae86", ["147d88d2", "a67eb609"]))


if __name__ == "__main__":
    unittest.main()
