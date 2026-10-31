"""Tests of use-cases/define/define.py.

The script of the use case define, as ACU-57 to ACU-73 of
use-cases/define/specs/define.md say, with the checks of ACU-74, the files of
ACU-6 to ACU-8 and the fingerprints of ACU-51 to ACU-56 of specs/module.md. Each test names the
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

    code_repository_names = ("billing-code",)  # the entries of layer 4 of project.json, in its order

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = os.path.realpath(self.tmp.name)
        self.remotes = os.path.join(self.root, "remotes", "acme")
        self.folder = os.path.join(self.root, "p")
        os.makedirs(self.remotes)
        os.makedirs(self.folder)
        repos = [{"owner": "acme", "name": "billing-specs", "layer": 1, "path": "billing-specs"},
                 {"owner": "acme", "name": "billing-norms", "layer": 2, "path": "billing-norms"},
                 {"owner": "acme", "name": "billing-acceptance", "layer": 3, "path": "billing-acceptance"}]
        repos += [{"owner": "acme", "name": name, "layer": 4, "path": name} for name in self.code_repository_names]
        self.project = json.dumps({"project": "billing", "repositories": repos}, indent=2) + "\n"
        self.norms = self.clone("billing-norms", {
            "data/tree.jsonl": tree_jsonl(),
            "project.json": self.project,
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
    """ACU-57, ACU-74 then ACU-58: the checks, in their order."""

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

    def test_acu74_argument(self):
        self.refused("takes no argument", "--", "AA-1")

    def test_acu74_blank_argument_is_none(self):
        self.assertEqual(self.start("--", "  ").returncode, 0)

    def test_acu74_not_a_git_repository(self):
        other = os.path.join(self.root, "plain")
        os.mkdir(other)
        self.refused("runs only from the acceptance repository", cwd=other)

    def test_acu74_another_layer(self):
        self.refused("runs only from the acceptance repository", cwd=self.norms)

    def test_acu74_no_project_json(self):
        os.remove(os.path.join(self.acc, "project.json"))
        self.refused("runs only from the acceptance repository")

    def test_acu74_no_entry_matches_origin(self):
        git(self.acc, "remote", "set-url", "origin", "https://github.com/acme/elsewhere")
        self.refused("runs only from the acceptance repository")

    def test_acu74_norms_repository_not_at_its_path(self):
        shutil.rmtree(self.norms)
        self.refused(f"acme/billing-norms not found at {self.norms}; run: git clone "
                     f"https://github.com/acme/billing-norms {self.norms}")

    def test_acu74_cannot_fetch_acceptance(self):
        git(self.acc, "remote", "set-url", "origin", os.path.join(self.root, "nowhere", "acme", "billing-acceptance"))
        self.refused("cannot fetch acme/billing-acceptance")

    def test_acu74_cannot_fetch_norms(self):
        git(self.norms, "remote", "set-url", "origin", os.path.join(self.root, "nowhere", "acme", "billing-norms"))
        self.refused("cannot fetch acme/billing-norms")

    def test_acu74_no_default_branch_acceptance(self):
        git(os.path.join(self.remotes, "billing-acceptance.git"), "symbolic-ref", "HEAD", "refs/heads/nope")
        self.refused("cannot find the default branch of acme/billing-acceptance")

    def test_acu74_no_default_branch_norms(self):
        git(os.path.join(self.remotes, "billing-norms.git"), "symbolic-ref", "HEAD", "refs/heads/nope")
        self.refused("cannot find the default branch of acme/billing-norms")

    def test_acu74_no_tree_jsonl(self):
        git(self.norms, "rm", "-q", "data/tree.jsonl")
        self.commit_all(self.norms)
        self.refused("acme/billing-norms has no data/tree.jsonl on main")

    def test_acu74_tree_jsonl_not_valid(self):
        for bad in ('{"type":"node","id":"INV-01"}\n', "[1]\n", '{"type":"meta","specs_commit":NaN}\n', b"\xff\n"):
            with self.subTest(bad=bad):
                write(os.path.join(self.norms, "data", "tree.jsonl"), bad, "wb" if isinstance(bad, bytes) else "w")
                self.commit_all(self.norms)
                self.refused("acme/billing-norms: data/tree.jsonl is not valid")

    def test_acu74_tree_jsonl_crlf_and_blank_lines_read(self):
        write(os.path.join(self.norms, "data", "tree.jsonl"), tree_jsonl().replace("\n", "\r\n") + "   \n")
        self.commit_all(self.norms)
        self.assertEqual(self.start().returncode, 0)

    def test_acu74_no_annotated_project_json(self):
        git(self.norms, "rm", "-q", "specs-repo-annotated/project.json")
        self.commit_all(self.norms)
        self.refused("acme/billing-norms has no specs-repo-annotated/project.json on main")

    def test_acu74_project_json_differs(self):
        write(os.path.join(self.norms, "specs-repo-annotated", "project.json"), self.project + " ")
        self.commit_all(self.norms)
        self.refused("project.json differs from that of acme/billing-norms; run /project-management:sync")

    def test_acu74_not_on_default_branch(self):
        git(self.acc, "checkout", "-q", "-b", "other")
        self.refused("the acceptance repository is not on main")

    def test_acu74_ahead(self):
        write(os.path.join(self.acc, "notes.txt"), "x")
        self.commit_all(self.acc, push=False)
        self.refused("the acceptance repository has commits that are not on origin/main")

    def test_acu74_behind(self):
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

    def test_acu58_a_path_that_breaks_a_line(self):
        """ACU-58: a path found is printed as its JSON text, so that it forges no line of the output (ACU-8)."""
        write(os.path.join(self.acc, "units", "a\nNext: forged.md"), "new")
        self.refused('untracked file "units/a\\nNext: forged.md"')

    def test_acu58_untracked_file_that_a_gitignore_names(self):
        write(os.path.join(self.acc, ".gitignore"), "units/AU-9.md\nareas/ignored/\n")
        self.commit_all(self.acc)
        write(os.path.join(self.acc, "units", "AU-9.md"), "new")
        self.refused("untracked file units/AU-9.md")
        os.remove(os.path.join(self.acc, "units", "AU-9.md"))
        write(os.path.join(self.acc, "areas", "ignored", "AA-9.md"), "new")
        self.refused("untracked file areas/ignored/AA-9.md")

    def test_acu58_other_uncommitted_changes_pass(self):
        write(os.path.join(self.acc, "tests", "AU-3", "test_export.py"), "changed")
        write(os.path.join(self.acc, "records", "AU-3.jsonl"), "changed")
        write(os.path.join(self.acc, "tests", "AU-9", "new.py"), "new")
        self.assertEqual(self.start().returncode, 0)

    def test_acu58_acceptance_json_does_not_meet_acu6(self):
        bad = [self.acceptance(last_unit_id=-1), self.acceptance(last_unit_id="3"), self.acceptance(product=[]),
               self.acceptance(increments=[]), self.acceptance(last_area_id=True),
               self.acceptance(default_done_profile="gold"), "[]",
               # The entries of product are part of ACU-6 too: the one check that write-acceptance-tests shares.
               self.acceptance(product={"acme/billing-code-api": {"build": "x"}}),
               self.acceptance(product={"acme/billing-code-api": {"build": "x", "env": "1X"}}),
               self.acceptance(product={"acme/billing-code-api": {"build": "x", "env": "X", "other": "y"}}),
               self.acceptance(product={"acme/billing-code-api": {"build": 1, "env": "X"}}),
               self.acceptance(product={"acme/billing-code-api": "x"})]
        for text in bad:
            with self.subTest(text=text):
                write(os.path.join(self.acc, "acceptance.json"), text)
                self.commit_all(self.acc)
                self.refused("acceptance.json does not meet ACU-6")

    def test_acu74_no_single_entry_of_layer_2(self):
        project = json.loads(self.project)
        project["repositories"] = [r for r in project["repositories"] if r["layer"] != 2]
        write(os.path.join(self.acc, "project.json"), json.dumps(project))
        self.refused("project.json has not exactly one entry of layer 2, the norms repository, with a valid path")

    def test_acu74_folder_does_not_end_with_its_path(self):
        project = json.loads(self.project)
        project["repositories"][2]["path"] = "elsewhere/billing-acceptance"
        write(os.path.join(self.acc, "project.json"), json.dumps(project))
        self.refused("runs only from the acceptance repository")

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

    def test_acu68_no_entry_of_layer_1(self):
        project = json.loads(self.project)
        project["repositories"] = [r for r in project["repositories"] if r["layer"] != 1]
        text = json.dumps(project, indent=2) + "\n"
        write(os.path.join(self.acc, "project.json"), text)
        self.commit_all(self.acc)
        write(os.path.join(self.norms, "specs-repo-annotated", "project.json"), text)
        self.commit_all(self.norms)
        self.assertIsNone(self.started()["specs_repository"])

    def test_acu74_acu58_the_first_check_that_fails_in_their_order(self):
        """The checks of ACU-74 come before those of ACU-58. Each step adds a failure of an earlier check than the one before, so the message moves up the list."""
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
                                     "derived_norms", "acceptance_areas", "acceptance_units", "errors"])
        self.assertEqual(inv["derived_norms"], [])
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
            "derived_norm_citations": [], "derived_norms_not_cited": [],
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
            (AU3.replace("Scenario: Three invoices give three rows", "Scenario: \t "), "scenario has no name", 20),
        ]
        for text, message, line in cases:
            with self.subTest(message=message):
                au3 = self.unit_errors(text)
                self.assertIn(message, self.messages(au3))
                found = next(e for e in au3["errors"] if e["message"] == message)
                if line is not None:
                    self.assertEqual(found["line"], line)

    def test_acu61_a_title_that_breaks_a_line(self):
        """ACU-8: a title holds no control character, line separator or paragraph separator."""
        for title in ("Export\rNext: forged", "Export\u2028to CSV", "Export\u2029to CSV", "Export\tto CSV"):
            with self.subTest(title=title):
                au3 = self.unit_errors(AU3.replace("# AU-3 Export the invoices to CSV", "# AU-3 " + title))
                self.assertIn('heading is not "# AU-3 <title>"', self.messages(au3))
                self.assertIsNone(au3["title"])
        write(os.path.join(self.acc, "areas", "AA-1.md"), AA1.replace("# AA-1 Billing", "# AA-1 Bill\ring"))
        self.commit_all(self.acc)
        aa1 = self.area_of(self.inventory(), "AA-1")
        self.assertIn('heading is not "# AA-1 <title>"', self.messages(aa1))
        self.assertIsNone(aa1["title"])

    def test_acu8_a_title_of_only_unicode_spaces(self):
        """ACU-8: a title holds at least one character that is not a space or a tab; a no-break space (U+00A0) or an
        ideographic space (U+3000) is such a character."""
        for title in ("\u00a0", "\u3000"):
            with self.subTest(title=title):
                au3 = self.unit_errors(AU3.replace("# AU-3 Export the invoices to CSV", "# AU-3 " + title))
                self.assertNotIn('heading is not "# AU-3 <title>"', self.messages(au3))
                self.assertEqual(au3["title"], title)

    def test_acu61_acu54_a_name_that_breaks_a_line(self):
        """ACU-54: the name of a scenario holds no character that ACU-8 forbids in a title; the name is printed as
        ACU-58 says for a path when it holds one."""
        for name, printed in (("Three\rinvoices", '"Three\\rinvoices"'), ("Three\u2028rows", '"Three\\u2028rows"'),
                              ("Three\x1b[2Kinvoices", '"Three\\u001b[2Kinvoices"'), ("Three\x0brows", '"Three\\u000brows"')):
            with self.subTest(name=name):
                au3 = self.unit_errors(AU3.replace("Scenario: Three invoices give three rows", "Scenario: " + name))
                found = [e for e in au3["errors"] if e["message"].endswith("has a character that breaks a line")]
                self.assertEqual(found, [{"line": 20, "message": f"scenario {printed} has a character that breaks "
                                                                 "a line"}])

    def test_acu61_acu56_a_title_or_a_name_that_holds_a_citation(self):
        """ACU-56: a title and the name of a scenario hold no citation found in a line."""
        for name in ("A CSV@deadbeef row", "Like AU-4@12345678", "(SC-9@1bd67ec5)", "INV@5a627175"):
            with self.subTest(name=name):
                au3 = self.unit_errors(AU3.replace("Scenario: Three invoices give three rows", "Scenario: " + name))
                self.assertIn({"line": 20, "message": f'scenario "{name}" holds a citation'}, au3["errors"])
        for name in ("A CSV@deadbeef1 row", "xAU-4@12345678", "AU-4@12345678é", "A row@home"):
            with self.subTest(name=name):
                au3 = self.unit_errors(AU3.replace("Scenario: Three invoices give three rows", "Scenario: " + name))
                self.assertEqual(au3["errors"], [])
        au3 = self.unit_errors(AU3.replace("# AU-3 Export the invoices to CSV", "# AU-3 Export AU-4@12345678"))
        self.assertEqual((au3["title"], au3["errors"]), ("Export AU-4@12345678",
                                                         [{"line": 1, "message": "title holds a citation"}]))
        write(os.path.join(self.acc, "areas", "AA-1.md"), AA1.replace("# AA-1 Billing", "# AA-1 Billing INV-7@5a627175"))
        self.commit_all(self.acc)
        self.assertIn("title holds a citation", self.messages(self.area_of(self.inventory(), "AA-1")))

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


class WritingFixture(Fixture):
    """The commands of the script after the proposal is final, with no test of its own."""

    def script(self, *args, code=0):
        r = self.run_script(*args)
        self.assertEqual(r.returncode, code, r.stdout + r.stderr)
        return r.stdout

    def check(self, code=0):
        return json.loads(self.script("check", self.acc, "--norms-commit", self.norms_commit(), code=code))

    def head(self):
        return git(self.acc, "rev-parse", "HEAD").stdout.strip()

    def commit(self, *changes, code=0, expected_head=None):
        args = ["commit", self.acc, "--norms-commit", self.norms_commit(), "--expected-head",
                expected_head or self.head()]
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


class Writing(WritingFixture):
    """ACU-65, ACU-69, ACU-70, ACU-71, ACU-72, ACU-73: after the proposal is final."""

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
        message = ("only last_area_id, last_unit_id and last_scenario_id, and test_command and product while they "
                   "are empty at HEAD, may change (ACU-73)")
        write(os.path.join(self.acc, "acceptance.json"), self.acceptance(default_done_profile="critical"))
        self.assertIn(message, [p["message"] for p in self.check(code=1)["problems"]])
        write(os.path.join(self.acc, "acceptance.json"), self.acceptance(test_command="pytest"))
        self.commit_all(self.acc)
        write(os.path.join(self.acc, "acceptance.json"), self.acceptance(test_command="pytest -x"))
        self.assertIn(message, [p["message"] for p in self.check(code=1)["problems"]])

    def test_acu69_acu77_a_filled_value_is_checked(self):
        """test_command and product, empty at HEAD, may be filled, with values that ACU-77 does not refuse."""
        write(os.path.join(self.acc, "acceptance.json"), self.acceptance(test_command="pytest"))
        self.assertEqual(self.check()["problems"], [])
        write(os.path.join(self.acc, "acceptance.json"), self.acceptance(test_command=" \n"))
        problems = self.check(code=1)["problems"]
        self.assertEqual([(p["path"], p["message"]) for p in problems],
                         [("acceptance.json", "test_command is not a command")])
        write(os.path.join(self.acc, "acceptance.json"),
              self.acceptance(product={"acme/billing-code": {"build": "make", "env": "ACCEPTANCE_REPORT"}}))
        self.assertEqual([p["message"] for p in self.check(code=1)["problems"]],
                         ["env ACCEPTANCE_REPORT of acme/billing-code is a variable of test_command (ACU-6)"])

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
        r = self.run_script("commit", self.acc, "--norms-commit", self.norms_commit(), "--expected-head",
                            git(self.acc, "rev-parse", "HEAD").stdout.strip(), "--change", "add AU-4")
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
                 (["fill acceptance.json"], "docs: fill acceptance.json"),
                 (["add AU-4", "change AU-3"], "docs: change acceptance areas and units"),
                 (["fill acceptance.json", "add AU-4"], "docs: change acceptance areas and units")]
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

    def test_acu75_cannot_fetch_comes_before_the_default_branch(self):
        """ACU-75: an unreachable origin gives the message of the fetch, with the status 3, not that of the default
        branch."""
        self.add_au4()
        self.script("ids", self.acc)
        git(self.acc, "remote", "set-url", "origin", os.path.join(self.root, "nowhere", "acme", "billing-acceptance"))
        self.assertEqual(self.commit("add AU-4", code=3), PREFIX + "cannot fetch acme/billing-acceptance")

    def test_acu75_cannot_find_the_default_branch(self):
        self.add_au4()
        self.script("ids", self.acc)
        git(os.path.join(self.remotes, "billing-acceptance.git"), "symbolic-ref", "HEAD", "refs/heads/nope")
        self.assertEqual(self.commit("add AU-4", code=3),
                         PREFIX + "cannot find the default branch of acme/billing-acceptance")

    def test_acu71_a_gitignore_does_not_refuse_the_files_of_the_commit(self):
        write(os.path.join(self.acc, ".gitignore"), "units/AU-4.md\n")
        self.commit_all(self.acc)
        self.add_au4()
        self.script("ids", self.acc)
        r = self.approve(self.commit("add AU-4"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("units/AU-4.md", self.remote_log())

    def test_acu60_records_and_acceptance_json_nested_deeply(self):
        """A value nested deeper than json.loads reads gives no traceback on any version of Python."""
        deep = "[" * 100000 + "]" * 100000
        write(os.path.join(self.acc, "records", "AU-1.jsonl"), deep + "\n")
        write(os.path.join(self.acc, "acceptance.json"), deep + "\n")
        self.commit_all(self.acc)
        r = self.run_script("start", self.acc)
        self.assertNotIn("Traceback", r.stdout + r.stderr)

    def test_acu71_the_default_branch_moves_after_the_command_is_shown(self):
        self.add_au4()
        self.script("ids", self.acc)
        plan = self.commit("add AU-4")
        self.push_from_other_clone("billing-acceptance", "notes.txt", "x")
        head = git(self.acc, "rev-parse", "HEAD").stdout
        r = self.approve(plan)
        self.assertEqual((r.returncode, (r.stdout + r.stderr).strip()),
                         (3, PREFIX + "origin/main moved; run the skill again"))
        self.assertEqual(git(self.acc, "rev-parse", "HEAD").stdout, head)
        self.assertEqual(git(self.acc, "diff", "--cached", "--name-only").stdout, "")
        self.assertNotIn("AU-4", self.remote_log())

    def test_acu71_a_local_commit_made_after_the_start(self):
        self.add_au4()
        self.script("ids", self.acc)
        expected_head = self.head()
        plan = self.commit("add AU-4")
        git(self.acc, "commit", "-q", "--allow-empty", "-m", "another session")
        r = self.approve(plan)
        message = PREFIX + "the acceptance repository has commits that are not on origin/main"
        self.assertEqual((r.returncode, (r.stdout + r.stderr).strip()), (3, message))
        self.assertEqual(self.commit("add AU-4", code=3, expected_head=expected_head), message)
        self.assertNotIn("another session", self.remote_log())
        self.assertEqual(git(self.acc, "diff", "--cached", "--name-only").stdout, "")

    def test_acu71_head_is_no_longer_the_expected_head(self):
        self.add_au4()
        self.script("ids", self.acc)
        expected_head = self.head()
        plan = self.commit("add AU-4")
        git(self.acc, "commit", "-q", "--allow-empty", "-m", "another session")
        git(self.acc, "push", "-q", "origin", "HEAD:main")
        moved = PREFIX + "origin/main moved; run the skill again"
        r = self.approve(plan)
        self.assertEqual((r.returncode, (r.stdout + r.stderr).strip()), (3, moved))
        self.assertEqual(self.commit("add AU-4", code=3, expected_head=expected_head), moved)
        self.assertNotIn("AU-4", self.remote_log())

    def test_acu71_the_command_prints_the_commit_it_pushed(self):
        self.add_au4()
        self.script("ids", self.acc)
        r = self.approve(self.commit("add AU-4"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(r.stdout.strip().split("\n")[-1], self.head())

    def test_acu71_the_push_is_rejected(self):
        self.add_au4()
        self.script("ids", self.acc)
        plan = self.commit("add AU-4")
        hook = os.path.join(self.remotes, "billing-acceptance.git", "hooks", "pre-receive")
        write(hook, "#!/bin/sh\nexit 1\n")
        os.chmod(hook, 0o755)
        r = self.approve(plan)
        self.assertEqual(r.returncode, 4, r.stdout + r.stderr)
        self.assertEqual((r.stdout + r.stderr).strip(),
                         PREFIX + f"push rejected; commit {self.head()[:7]} is not on origin/main; run git pull "
                                  "--rebase, then git push, and run the skill again")
        self.assertNotIn("AU-4", self.remote_log())

    def test_acu71_git_or_a_hook_refuses_the_commit(self):
        self.add_au4()
        self.script("ids", self.acc)
        plan = self.commit("add AU-4")
        head = self.head()
        hook = os.path.join(self.acc, ".git", "hooks", "pre-commit")
        write(hook, "#!/bin/sh\nexit 1\n")
        os.chmod(hook, 0o755)
        r = self.approve(plan)
        self.assertNotIn(r.returncode, (0, 3, 4), r.stdout + r.stderr)
        self.assertEqual(self.head(), head)
        self.script("rollback", self.acc, "--change", "add AU-4")
        self.assertEqual(git(self.acc, "status", "--porcelain").stdout, "")

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

    def test_acu58_rollback_prints_a_path_that_breaks_a_line_as_an_escape(self):
        """ACU-58: the JSON output of rollback writes a character that breaks a line, such as U+2028, U+0085 or
        U+009B, as \\u and 4 lower-case hex digits, so that no path forges a line or a terminal escape."""
        name = "t\u2028x\u0085y\u009bz.py"
        write(os.path.join(self.acc, "tests", "AU-2", name), "old")
        self.commit_all(self.acc)
        os.remove(os.path.join(self.acc, "units", "AU-2.md"))
        for output in (self.script("delete-tests", self.acc, "AU-2"),
                       self.script("rollback", self.acc, "--change", "delete AU-2")):
            self.assertIn('"tests/AU-2/t\\u2028x\\u0085y\\u009bz.py"', output)
            self.assertFalse(any(c in output for c in "\u2028\u0085\u009b"))
            self.assertIn(f"tests/AU-2/{name}", json.loads(output))

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

    def fields_filled(self):
        """A commit made outside the skill that fills test_command and product, so that the part of the test agent of
        ACU-72 can apply."""
        write(os.path.join(self.acc, "acceptance.json"), self.acceptance(
            test_command="pytest", product={"acme/billing-code-api": {"build": "make", "env": "APP"}}))
        self.commit_all(self.acc)

    def test_acu72_next_line(self):
        self.fields_filled()
        since = git(self.acc, "rev-parse", "HEAD").stdout.strip()
        self.assertEqual(self.script("next", self.acc, "--since", since), "")
        write(os.path.join(self.acc, "units", "AU-3.md"), AU3.replace("# AU-3 Export the invoices to CSV",
                                                                     "# AU-3 Export to CSV"))
        self.commit_all(self.acc)
        # "Only a title": no unit hash and no area hash changed (ACU-52), so no line "Next:".
        self.assertEqual(self.script("next", self.acc, "--since", since), "")
        write(os.path.join(self.acc, "units", "AU-3.md"), AU3.replace("INV-12@0c1d2e3f", "INV-12@7d6e5f40"))
        self.add_au4()
        write(os.path.join(self.acc, "areas", "AA-1.md"), AA1 + "\n")
        self.commit_all(self.acc)
        self.assertEqual(self.script("next", self.acc, "--since", since).strip(),
                         "Next: the implementation planner updates plan.json with /acceptance-management:plan; "
                         "the test agent updates the acceptance tests of AU-3, AU-4 with "
                         "/acceptance-management:write-acceptance-tests.")
        write(os.path.join(self.acc, "areas", "AA-1.md"), AA1.replace("Then the CSV", "Then the file"))
        self.commit_all(self.acc)
        self.assertIn("of AA-1, AU-3, AU-4 with /acceptance-management:write-acceptance-tests.",
                      self.script("next", self.acc, "--since", since))

    def test_acu72_since_is_not_a_commit_of_head(self):
        for since in ("nonexistent", "0" * 40):
            self.assertEqual(self.script("next", self.acc, "--since", since, code=1).strip(),
                             PREFIX + f"--since {since} is not a commit of HEAD")
        # A commit outside the history of HEAD: a commit with no parent, made with the tree of HEAD.
        side = git(self.acc, "commit-tree", "HEAD^{tree}", "-m", "side").stdout.strip()
        self.assertEqual(self.script("next", self.acc, "--since", side, code=1).strip(),
                         PREFIX + f"--since {side} is not a commit of HEAD")

    def test_acu72_only_a_deletion(self):
        since = git(self.acc, "rev-parse", "HEAD").stdout.strip()
        self.script("delete-tests", self.acc, "AU-2")
        os.remove(os.path.join(self.acc, "units", "AU-2.md"))
        self.commit_all(self.acc)
        self.assertEqual(self.script("next", self.acc, "--since", since).strip(),
                         "Next: the implementation planner updates plan.json with /acceptance-management:plan.")

    def test_acu72_only_the_area_line_or_the_profile_line(self):
        since = git(self.acc, "rev-parse", "HEAD").stdout.strip()
        write(os.path.join(self.acc, "units", "AU-3.md"), AU3.replace("Area: AA-1\n", "Area: AA-1\nProfile: critical\n"))
        self.commit_all(self.acc)
        self.assertEqual(self.script("next", self.acc, "--since", since), "")

    def test_acu72_a_unit_hash_changed_with_no_new_test(self):
        """A change of the unit hash outside "## Norms" and "## Scenarios" names both agents."""
        self.fields_filled()
        since = git(self.acc, "rev-parse", "HEAD").stdout.strip()
        write(os.path.join(self.acc, "units", "AU-3.md"), AU3.replace("- The unit does not export to PDF.\n", ""))
        self.commit_all(self.acc)
        self.assertEqual(self.script("next", self.acc, "--since", since).strip(),
                         "Next: the implementation planner updates plan.json with /acceptance-management:plan; "
                         "the test agent updates the acceptance tests of AU-3 with "
                         "/acceptance-management:write-acceptance-tests.")

    def test_acu72_hash_changed_product_still_empty(self):
        """ACU-72, "Hash changed, product still empty": no part of the test agent while a field is empty at HEAD,
        since write-acceptance-tests would refuse to start (WAT-2)."""
        write(os.path.join(self.acc, "acceptance.json"), self.acceptance(test_command="pytest"))
        self.commit_all(self.acc)
        since = self.head()
        write(os.path.join(self.acc, "units", "AU-3.md"), AU3.replace("- The unit does not export to PDF.\n", ""))
        self.commit_all(self.acc)
        self.assertEqual(self.script("next", self.acc, "--since", since).strip(),
                         "Next: the implementation planner updates plan.json with /acceptance-management:plan.")
        write(os.path.join(self.acc, "areas", "AA-1.md"), AA1.replace("Then the CSV", "Then the file"))
        self.commit_all(self.acc)
        self.assertEqual(self.script("next", self.acc, "--since", self.head() + "~1"), "")

    def test_acu72_only_an_area(self):
        self.fields_filled()
        since = git(self.acc, "rev-parse", "HEAD").stdout.strip()
        write(os.path.join(self.acc, "areas", "AA-1.md"), AA1.replace("Then the CSV", "Then the file"))
        self.commit_all(self.acc)
        self.assertEqual(self.script("next", self.acc, "--since", since).strip(),
                         "Next: the test agent updates the acceptance tests of AA-1 with "
                         "/acceptance-management:write-acceptance-tests.")

    def test_hash_command(self):
        path = os.path.join(self.acc, "units", "AU-3.md")
        out = json.loads(self.script("hash", path))
        self.assertEqual((out["unit_hash"], [s["scenario_hash"] for s in out["scenarios"]]),
                         ("efc7ae86", ["147d88d2", "a67eb609"]))


TEST_COMMAND = 'pytest "$ACCEPTANCE_TARGET" --junitxml "$ACCEPTANCE_REPORT"'
PRODUCT = {"acme/billing-code-api": {"build": 'make dist && echo "$PWD/dist/app"', "env": "PRODUCT_CMD"},
           "acme/billing-code-web": {"build": "make serve-local", "env": "WEB_URL",
                                     "published": "echo https://staging.billing.example.com"}}
LEFT_EMPTY = PREFIX + ("acceptance.json keeps {} empty; /acceptance-management:write-acceptance-tests stops until "
                       "define fills it (WAT-2)")


class Fill(WritingFixture):
    """ACU-77: while test_command or product of acceptance.json is empty at HEAD, define fills it with the values
    that the requester states; and ACU-69, ACU-71, ACU-72, ACU-73 for that change."""

    code_repository_names = ("billing-code-api", "billing-code-web", "billing-code-cli")

    def fill(self, values, *extra, code=0):
        path = os.path.join(self.root, "values", "fill.json")
        write(path, json.dumps(values))
        r = self.run_script("fill", self.acc, path, *extra)
        self.assertEqual(r.returncode, code, r.stdout + r.stderr)
        return json.loads(r.stdout) if code == 0 else r.stdout.strip()

    def test_acu77_start_names_the_empty_fields_and_the_code_repositories(self):
        out = self.started()
        self.assertEqual(out["empty_fields_of_acceptance_json"], ["test_command", "product"])
        self.assertEqual(out["code_repositories"],
                         ["acme/billing-code-api", "acme/billing-code-web", "acme/billing-code-cli"])

    def test_acu77_the_change_and_the_lines_of_acu49(self):
        before = read(os.path.join(self.acc, "acceptance.json"))
        out = self.fill({"test_command": TEST_COMMAND, "product": PRODUCT}, "--dry-run")
        self.assertEqual(out, {
            "change": "fill acceptance.json: test_command, product",
            "lines": [
                'test_command: pytest "$ACCEPTANCE_TARGET" --junitxml "$ACCEPTANCE_REPORT"',
                'product acme/billing-code-api: build make dist && echo "$PWD/dist/app"; env PRODUCT_CMD',
                "product acme/billing-code-web: build make serve-local; env WEB_URL; "
                "published echo https://staging.billing.example.com",
                "acme/billing-code-cli has no entry in product: its implementing agent runs no acceptance test "
                "(ACU-49)",
                "acme/billing-code-api has no published: no acceptance test runs in the tasks of "
                "acme/billing-code-web (ACU-49)"],
            "fields_left_empty": []})
        self.assertEqual(read(os.path.join(self.acc, "acceptance.json")), before)

    def test_acu77_a_value_that_breaks_a_line_is_shown_as_its_json_text(self):
        out = self.fill({"test_command": "pytest\nrm -rf /"}, "--dry-run")
        self.assertEqual(out["lines"], ['test_command: "pytest\\nrm -rf /"'])
        with self.subTest("the name of a code repository, in the lines of ACU-49"):
            project = json.loads(self.project)
            project["repositories"].append({"owner": "acme", "name": "a\nb", "layer": 4, "path": "billing-code-x"})
            text = json.dumps(project, indent=2) + "\n"
            write(os.path.join(self.acc, "project.json"), text)
            self.commit_all(self.acc)
            write(os.path.join(self.norms, "specs-repo-annotated", "project.json"), text)
            self.commit_all(self.norms)
            api, odd = "acme/billing-code-api", "acme/a\nb"
            out = self.fill({"product": {api: {"build": "make", "env": "X"}}}, "--dry-run")
            self.assertIn('"acme/a\\nb" has no entry in product: its implementing agent runs no acceptance test '
                          '(ACU-49)', out["lines"])
            out = self.fill({"product": {api: {"build": "make", "env": "X"}, odd: {"build": "make", "env": "Y"}}},
                            "--dry-run")
            self.assertEqual(out["lines"][-2:], [
                f'{api} has no published: no acceptance test runs in the tasks of "acme/a\\nb" (ACU-49)',
                f'"acme/a\\nb" has no published: no acceptance test runs in the tasks of {api} (ACU-49)'])
            self.assertFalse(any("\n" in line for line in out["lines"]))

    def test_acu77_the_requester_does_not_know_a_value_yet(self):
        out = self.fill({"test_command": TEST_COMMAND}, "--dry-run")
        self.assertEqual((out["change"], out["fields_left_empty"]),
                         ("fill acceptance.json: test_command", [LEFT_EMPTY.format("product")]))
        out = self.fill({}, "--dry-run")
        self.assertEqual(out, {"change": None, "lines": [],
                               "fields_left_empty": [LEFT_EMPTY.format("test_command"),
                                                     LEFT_EMPTY.format("product")]})

    def test_acu77_a_value_that_does_not_meet_acu6(self):
        api = "acme/billing-code-api"
        cases = [
            ({"test_command": " \t\n"}, "test_command is not a command"),
            # ACU-77, ACU-8: every character that breaks a line, not only the line feed and the carriage return.
            ({"test_command": "\u2028"}, "test_command is not a command"),
            ({"test_command": " \x0c\x0b\x85\u2029"}, "test_command is not a command"),
            ({"product": {api: {"build": "\u2028", "env": "X"}}}, f"build of {api} is not a command"),
            ({"test_command": 3}, "test_command is not a command"),
            ({"test_command": "pytest \udcff"}, "test_command is not a command"),
            ({"product": {api: {"build": "make \ud800", "env": "X"}}}, f"build of {api} is not a command"),
            ({"product": {}}, "product has no entry"),
            ({"product": []}, "product has no entry"),
            ({"product": {"acme/billing-code": {"build": "make", "env": "X"}}},
             "acme/billing-code is not a code repository of project.json"),
            ({"product": {api: {"build": "make"}}}, f"the entry {api} of product has not the fields of ACU-6"),
            ({"product": {api: {"build": "make", "env": "X", "url": "u"}}},
             f"the entry {api} of product has not the fields of ACU-6"),
            ({"product": {api: {"build": " ", "env": "X"}}}, f"build of {api} is not a command"),
            ({"product": {api: {"build": "make", "env": "X", "published": ""}}},
             f"published of {api} is not a command"),
            ({"product": {api: {"build": "make", "env": "web-url"}}},
             f"env web-url of {api} is not a name of A-Z, 0-9 and _ that does not start with a digit"),
            ({"product": {api: {"build": "make", "env": "9X"}}},
             f"env 9X of {api} is not a name of A-Z, 0-9 and _ that does not start with a digit"),
            ({"product": {api: {"build": "make", "env": "ACCEPTANCE_TARGET"}}},
             f"env ACCEPTANCE_TARGET of {api} is a variable of test_command (ACU-6)"),
            ({"product": {api: {"build": "make", "env": "X"}, "acme/billing-code-web": {"build": "m", "env": "X"}}},
             "env X is named by more than one entry of product"),
            ({"product": {"acme/a\nb": {"build": "make", "env": "X"}}},
             '"acme/a\\nb" is not a code repository of project.json'),
        ]
        for values, message in cases:
            with self.subTest(message=message):
                self.assertEqual(self.fill(values, "--dry-run", code=1), PREFIX + message)
                self.assertEqual(self.fill(values, code=1), PREFIX + message)
        self.assertEqual(self.check()["written"], [])

    def test_acu77_a_field_that_holds_a_value(self):
        write(os.path.join(self.acc, "acceptance.json"), self.acceptance(test_command="pytest"))
        self.commit_all(self.acc)
        self.assertEqual(self.started()["empty_fields_of_acceptance_json"], ["product"])
        self.assertEqual(self.fill({"test_command": "pytest -x"}, "--dry-run", code=1),
                         PREFIX + "test_command of acceptance.json is not empty; define fills only an empty field "
                                  "(ACU-43)")
        out = self.fill({}, "--dry-run")
        self.assertEqual(out["fields_left_empty"], [LEFT_EMPTY.format("product")])

    def test_acu77_acu71_acu72_fill_commit_and_next(self):
        since = self.head()
        self.assertEqual(self.fill({"test_command": TEST_COMMAND, "product": PRODUCT}),
                         ["test_command", "product"])
        data = read(os.path.join(self.acc, "acceptance.json"))
        self.assertEqual(json.loads(data), json.loads(self.acceptance(test_command=TEST_COMMAND, product=PRODUCT)))
        before = self.acceptance().split("\n")
        changed = [line for line in data.split("\n") if line not in before]
        self.assertEqual(len(changed), 2, changed)  # only the lines of the two fields filled
        self.assertEqual(self.check(), {"written": ["acceptance.json"], "problems": []})
        plan = self.commit("fill acceptance.json")
        self.assertEqual(plan["paths"], ["acceptance.json"])
        self.assertEqual(plan["message"], "docs: fill acceptance.json\n\nfill acceptance.json")
        r = self.approve(plan)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(self.remote_log().startswith("docs: fill acceptance.json\n\nfill acceptance.json\n"))
        self.assertEqual(self.script("next", self.acc, "--since", since).strip(),
                         "Next: the test agent updates the acceptance tests of AA-1, AU-1, AU-2, AU-3 with "
                         "/acceptance-management:write-acceptance-tests.")

    def test_acu72_only_product_filled(self):
        write(os.path.join(self.acc, "acceptance.json"), self.acceptance(test_command="pytest"))
        self.commit_all(self.acc)
        since = self.head()
        self.fill({"product": {"acme/billing-code-api": {"build": "make", "env": "APP"}}})
        self.commit_all(self.acc)
        self.assertEqual(self.script("next", self.acc, "--since", since).strip(),
                         "Next: the test agent updates the acceptance tests of AA-1, AU-1, AU-2, AU-3 with "
                         "/acceptance-management:write-acceptance-tests.")

    def test_acu72_one_field_left_empty_names_nobody(self):
        since = self.head()
        self.fill({"test_command": "pytest"})
        self.commit_all(self.acc)
        self.assertEqual(self.script("next", self.acc, "--since", since), "")

    def test_acu71_one_commit_with_the_fill_and_a_unit(self):
        self.fill({"test_command": TEST_COMMAND})
        self.add_au4()
        self.script("ids", self.acc)
        self.assertEqual(self.commit("add AU-4", code=1),
                         PREFIX + "acceptance.json differs from HEAD in test_command or product, and no change of "
                                  "the commit names it (ACU-71)")
        plan = self.commit("fill acceptance.json", "add AU-4")
        self.assertEqual(plan["message"], "docs: change acceptance areas and units\n\nfill acceptance.json\nadd AU-4")
        self.assertEqual(self.approve(plan).returncode, 0)
        pushed = json.loads(git(self.acc, "show", "origin/main:acceptance.json").stdout)
        self.assertEqual((pushed["test_command"], pushed["last_unit_id"]), (TEST_COMMAND, 4))

    def test_acu71_fill_that_fills_nothing(self):
        self.add_au4()
        self.script("ids", self.acc)
        self.assertEqual(self.commit("fill acceptance.json", "add AU-4", code=1),
                         PREFIX + "fill acceptance.json: acceptance.json is not filled as it says")

    def test_acu71_rollback_of_the_fill(self):
        before = read(os.path.join(self.acc, "acceptance.json"))
        self.fill({"test_command": TEST_COMMAND})
        self.assertEqual(json.loads(self.script("rollback", self.acc, "--change", "fill acceptance.json")),
                         ["acceptance.json"])
        self.assertEqual(read(os.path.join(self.acc, "acceptance.json")), before)


# ---------------------------------------------------------------- the derived norms (ACU-58, ACU-60 to ACU-62, ACU-78)

def derived_norm_line(type_of_derived_norms, derived_norm_number, derived_norm_fingerprint, name, path, first, last,
                      cited):
    return json.dumps({"kind": "derived_norm", "derived_norm_id": f"{type_of_derived_norms}:{derived_norm_number}",
                       "derived_norm_fingerprint": derived_norm_fingerprint, "name": name, "path": path, "first_line": first,
                       "last_line": last, "cited_norms": [{"norm_id": n, "norm_hash": h} for n, h in cited]})


def list_of_derived_norms(type_of_derived_norms, last, *lines):
    """NRM-12: a list of derived norms, its header line first."""
    header = json.dumps({"kind": "header", "type": type_of_derived_norms, "last_derived_norm_number": last})
    return "".join(line + "\n" for line in (header,) + lines)


GRAMMAR = list_of_derived_norms(
    "grammar", 7,
    derived_norm_line("grammar", 2, "2b2b2b2b", "customer", "specs-derived/grammar/billing.lark", 1, 2,
                      [("CUS-1", "c0c0c0c0")]),
    derived_norm_line("grammar", 7, "3a4b5c6d", "row", "specs-derived/grammar/billing.lark", 4, 6,
                      [("INV-7", "5a627175")]))
SEMANTICS = list_of_derived_norms(
    "semantics", 32,
    derived_norm_line("semantics", 31, "6a7b8c9d", "E-Export", "specs-derived/semantics/eval.md", 10, 15,
                      [("INV-12", "7d6e5f40"), ("INV-15", "9e8d7c6b")]),
    derived_norm_line("semantics", 32, "9c0d1e2f", "E-Row", "specs-derived/semantics/eval.md", 17, 20,
                      [("INV-7", "5a627175")]))

DERIVED_NORMS_OF_AU3 = """
## Derived norms

- grammar:7@3a4b5c6d: the rule of a row
- semantics:31@5e6f7a8b: the export
"""


def with_derived_norms(text, part=DERIVED_NORMS_OF_AU3):
    """The file of an acceptance unit with `part` between "## Norms" and "## Scenarios" (ACU-8)."""
    return text.replace("\n## Scenarios\n", part + "\n## Scenarios\n", 1)


class DerivedNormsFixture(Fixture):
    """A project whose project.json names the types "grammar" and "semantics" of derived_norms, with their lists."""

    types_of_derived_norms = ("grammar", "semantics")

    def setUp(self):
        super().setUp()
        project = json.loads(self.project)
        project["derived_norms"] = [{"type": t, "use_case": f"/clean-derived-norms:derive-{t}"}
                                    for t in self.types_of_derived_norms]
        self.set_project(json.dumps(project, indent=2) + "\n")
        self.set_lists({"grammar": GRAMMAR, "semantics": SEMANTICS})

    def set_project(self, text):
        self.project = text
        write(os.path.join(self.norms, "project.json"), text)
        write(os.path.join(self.norms, "specs-repo-annotated", "project.json"), text)
        self.commit_all(self.norms)
        write(os.path.join(self.acc, "project.json"), text)
        self.commit_all(self.acc)

    def set_lists(self, lists):
        for type_of_derived_norms, text in lists.items():
            path = os.path.join(self.norms, "specs-derived", type_of_derived_norms, "derived-norms.jsonl")
            if text is None:
                if os.path.exists(path):
                    os.remove(path)
            else:
                write(path, text, "wb" if isinstance(text, bytes) else "w")
        self.commit_all(self.norms)
        git(self.norms, "fetch", "-q", "origin")


class DerivedNorms(DerivedNormsFixture):
    """ACU-58, ACU-60, ACU-61, ACU-62, ACU-64, ACU-78 of define.md."""

    def test_acu60_acu62_binding_example_of_the_derived_norms(self):
        write(os.path.join(self.acc, "units", "AU-3.md"), with_derived_norms(AU3))
        self.commit_all(self.acc)
        inv = self.inventory()
        self.assertEqual([d["derived_norm_id"] for d in inv["derived_norms"]],
                         ["grammar:2", "grammar:7", "semantics:31", "semantics:32"])
        self.assertEqual(inv["derived_norms"][1], {
            "derived_norm_id": "grammar:7", "derived_norm_fingerprint": "3a4b5c6d", "name": "row",
            "path": "specs-derived/grammar/billing.lark", "first_line": 4, "last_line": 6,
            "cited_norms": [{"norm_id": "INV-7", "norm_hash": "5a627175"}]})
        au3 = self.unit_of(inv, "AU-3")
        self.assertEqual(au3["derived_norm_citations"], [
            {"derived_norm_id": "grammar:7", "derived_norm_fingerprint_in_acceptance_unit": "3a4b5c6d", "citation_status": "current",
             "derived_norm_fingerprint_in_norms_repository": "3a4b5c6d"},
            {"derived_norm_id": "semantics:31", "derived_norm_fingerprint_in_acceptance_unit": "5e6f7a8b",
             "citation_status": "changed", "derived_norm_fingerprint_in_norms_repository": "6a7b8c9d"}])
        self.assertEqual(au3["derived_norms_not_cited"],
                         [{"derived_norm_id": "semantics:32", "derived_norm_fingerprint": "9c0d1e2f"}])
        self.assertEqual(au3["errors"], [])
        # AU-1 cites only INV-1, which no derived norm cites: its scope is empty.
        au1 = self.unit_of(inv, "AU-1")
        self.assertEqual((au1["derived_norm_citations"], au1["derived_norms_not_cited"]), ([], []))

    def test_acu62_retired_derived_norm_citation(self):
        part = DERIVED_NORMS_OF_AU3.replace("semantics:31@5e6f7a8b", "semantics:99@5e6f7a8b")
        au3 = self.unit_errors(with_derived_norms(AU3, part))
        self.assertEqual([(c["derived_norm_id"], c["citation_status"], c["derived_norm_fingerprint_in_norms_repository"])
                          for c in au3["derived_norm_citations"]],
                         [("grammar:7", "current", "3a4b5c6d"), ("semantics:99", "retired", None)])
        self.assertEqual([d["derived_norm_id"] for d in au3["derived_norms_not_cited"]], ["semantics:31", "semantics:32"])

    def test_acu62_a_type_that_project_json_does_not_name_is_retired(self):
        part = DERIVED_NORMS_OF_AU3 + "- zzz:1@5e6f7a8b: none\n"
        au3 = self.unit_errors(with_derived_norms(AU3, part))
        self.assertEqual(au3["derived_norm_citations"][-1]["citation_status"], "retired")

    def unit_errors(self, text, uid="AU-3"):
        write(os.path.join(self.acc, "units", f"{uid}.md"), text)
        self.commit_all(self.acc)
        return self.unit_of(self.inventory(), uid)

    def test_acu61_format_errors_of_derived_norms(self):
        current = "\n## Derived norms\n\n- grammar:7@3a4b5c6d: a row\n- semantics:31@6a7b8c9d: the export\n"
        cases = [
            (with_derived_norms(AU3, "\n## Derived norms\n\nNone.\n"), "no derived norm citation in ## Derived norms", 17),
            (with_derived_norms(AU3, current + "- grammar:7: no fingerprint\n"), "not a derived norm citation", 21),
            (with_derived_norms(AU3, current + "- INV-7@5a627175: a norm\n"), "not a derived norm citation", 21),
            (with_derived_norms(AU3, current + "- grammar:7@3a4b5c6d: again\n"), "grammar:7 is cited twice", 21),
            (with_derived_norms(AU3, current + "- grammar:2@2b2b2b2b: a customer\n"),
             "grammar:2 is not in the scope of AU-3 (ACU-78)", 21),
            (with_derived_norms(AU3, "\n## Derived norms\n\n- semantics:31@6a7b8c9d: the export\n"
                                     "- grammar:7@3a4b5c6d: a row\n- semantics:32@9c0d1e2f: a row\n"),
             "grammar:7 is not in the order of ACU-78", 20),
            (with_derived_norms(AU3, "\n## Derived norms\n\n- zzz:1@3a4b5c6d: x\n- grammar:7@3a4b5c6d: a row\n"),
             "grammar:7 is not in the order of ACU-78", 20),
            (AU3.replace("\n## Non-goals\n", "\n## Derived norms\n\n- grammar:7@3a4b5c6d: a row\n\n## Non-goals\n"),
             "parts are not those of ACU-8", 17),
            (with_derived_norms(AU3, current + "\n## Derived norms\n\n- semantics:32@9c0d1e2f: a row\n"),
             "parts are not those of ACU-8", 22),
        ]
        for text, message, line in cases:
            with self.subTest(message=message, line=line):
                au3 = self.unit_errors(text)
                self.assertIn(message, self.messages(au3))
                found = next(e for e in au3["errors"] if e["message"] == message)
                self.assertEqual(found["line"], line)
        # A changed citation out of the scope is no error of ACU-61: its citation status says it (ACU-62).
        au3 = self.unit_errors(with_derived_norms(AU3, current.replace(
            "\n- grammar:7", "\n- grammar:2@00000000: a customer\n- grammar:7")))
        self.assertEqual(au3["errors"], [])
        self.assertEqual(au3["derived_norm_citations"][0]["citation_status"], "changed")
        # The scope and the order hold: no error.
        self.assertEqual(self.unit_errors(with_derived_norms(
            AU3, current + "- semantics:32@9c0d1e2f: a row\n"))["errors"], [])

    def test_acu61_only_one_order_error(self):
        part = ("\n## Derived norms\n\n- semantics:32@9c0d1e2f: a row\n- semantics:31@6a7b8c9d: the export\n"
                "- grammar:7@3a4b5c6d: a row\n")
        au3 = self.unit_errors(with_derived_norms(AU3, part))
        self.assertEqual(self.messages(au3), ["semantics:31 is not in the order of ACU-78"])

    def test_acu61_a_title_or_a_name_that_holds_a_derived_norm_citation(self):
        au3 = self.unit_errors(AU3.replace("# AU-3 Export the invoices to CSV", "# AU-3 Export grammar:7@3a4b5c6d"))
        self.assertIn("title holds a citation", self.messages(au3))
        au3 = self.unit_errors(AU3.replace("Scenario: Three invoices give three rows",
                                           "Scenario: Three rows (xgrammar:12@0ced57c3)"))
        self.assertIn('scenario "Three rows (xgrammar:12@0ced57c3)" holds a citation', self.messages(au3))

    def test_acu8_a_scenario_never_tags_a_derived_norm(self):
        au3 = self.unit_errors(AU3.replace("@SC-6 @INV-15", "@SC-6 @INV-15 @grammar:7"))
        self.assertIn("tag @grammar:7 is not @SC-<n> or @<norm ID>", self.messages(au3))

    def test_acu61_not_utf8(self):
        write(os.path.join(self.acc, "units", "AU-3.md"), b"\xff" + with_derived_norms(AU3).encode(), "wb")
        self.commit_all(self.acc)
        au3 = self.unit_of(self.inventory(), "AU-3")
        self.assertEqual((au3["derived_norm_citations"], au3["derived_norms_not_cited"]), ([], []))

    def test_acu64_the_summary_with_derived_norms(self):
        write(os.path.join(self.acc, "units", "AU-3.md"), with_derived_norms(AU3))
        self.commit_all(self.acc)
        out = self.started()
        head = git(self.acc, "rev-parse", "HEAD").stdout.strip()
        self.assertEqual(out["summary"],
                         f"Layer 2 at {self.norms_commit()[:7]}: 10 norms, 4 derived norms. Layer 3 at {head[:7]}: "
                         "1 acceptance area, 3 acceptance units; 1 norm citation changed, 0 retired; "
                         "1 derived norm citation changed, 0 retired, 1 not cited; 0 format errors.")

    def test_acu64_the_example_of_the_summary(self):
        sys.path.insert(0, os.path.dirname(SCRIPT))
        try:
            import define
        finally:
            sys.path.pop(0)
        units = [{"norm_citations": [{"citation_status": "changed"}],
                  "derived_norm_citations": [{"citation_status": "changed"}, {"citation_status": "changed"}],
                  "derived_norms_not_cited": [{}], "errors": []}] + [
            {"norm_citations": [], "derived_norm_citations": [], "derived_norms_not_cited": [], "errors": []}] * 4
        inv = {"norms_commit": "9fceb02d0", "acceptance_commit": "1a410efbd", "norms": [{}] * 240,
               "derived_norms": [{}] * 31, "acceptance_areas": [{"errors": []}] * 2, "acceptance_units": units,
               "errors": []}
        self.assertEqual(define.summary(inv, True),
                         "Layer 2 at 9fceb02: 240 norms, 31 derived norms. Layer 3 at 1a410ef: 2 acceptance areas, "
                         "5 acceptance units; 1 norm citation changed, 0 retired; 2 derived norm citations changed, "
                         "0 retired, 1 not cited; 0 format errors.")

    def refused(self, message):
        r = self.start()
        self.assertEqual((r.returncode, r.stdout.strip()), (1, PREFIX + message), r.stderr)

    def types_cannot_be_read(self):
        return f"acme/billing-norms: the types of derived norms at {self.norms_commit()[:7]} cannot be read (NRM-16)"

    def set_record(self, data):
        """The record of the types of derived norms of the norms repository (NRM-16), or none when `data` is None."""
        path = os.path.join(self.norms, "specs-derived", "types-of-derived-norms.json")
        if data is None:
            if os.path.exists(path):
                os.remove(path)
        else:
            write(path, data, "wb" if isinstance(data, bytes) else "w")
        self.commit_all(self.norms)
        git(self.norms, "fetch", "-q", "origin")

    def test_acu58_derived_norms_of_project_json_does_not_meet_orc20(self):
        """ACU-58, ACU-78: with no record of the types of derived norms, the types come from project.json of the norms
        commit, read as NRM-1 says, use_case included."""
        for value in ("grammar", [{"type": "Grammar"}], [{"type": "grammar"}, {"type": "grammar"}], [{"use_case": "x"}],
                      [{"type": "grammar\n"}], ["grammar"], [{"type": "grammar"}],
                      [{"type": "grammar", "use_case": "not a use case"}], [{"type": "grammar", "use_case": 7}]):
            with self.subTest(value=value):
                project = json.loads(self.project)
                project["derived_norms"] = value
                self.set_project(json.dumps(project, indent=2) + "\n")
                self.refused(self.types_cannot_be_read())

    def test_acu58_project_json_of_the_norms_commit_cannot_be_read(self):
        """ACU-58, NRM-1: no record, and a project.json at the root of the norms commit that cannot be read."""
        for data in (None, b"\xff", b"not json", b"[]"):
            with self.subTest(data=data):
                path = os.path.join(self.norms, "project.json")
                if data is None:
                    os.remove(path)
                else:
                    write(path, data, "wb")
                self.commit_all(self.norms)
                git(self.norms, "fetch", "-q", "origin")
                self.refused(self.types_cannot_be_read())

    def test_acu78_the_record_gives_the_types_before_project_json(self):
        """ACU-78, NRM-16: a record that meets NRM-16 gives the types of derived norms and their order, whatever
        derived_norms of project.json, of the norms commit or of the acceptance repository, names."""
        write(os.path.join(self.acc, "units", "AU-3.md"), with_derived_norms(AU3))
        self.commit_all(self.acc)
        self.set_record('{"types_of_derived_norms": ["semantics", "grammar"]}\n')
        self.assertEqual([d["derived_norm_id"] for d in self.inventory()["derived_norms"]],
                         ["semantics:31", "semantics:32", "grammar:2", "grammar:7"])
        au3 = self.unit_of(self.inventory(), "AU-3")
        self.assertIn("semantics:31 is not in the order of ACU-78", [e["message"] for e in au3["errors"]])
        self.set_record('{"types_of_derived_norms": ["grammar"]}\n')
        self.assertEqual([d["derived_norm_id"] for d in self.inventory()["derived_norms"]], ["grammar:2", "grammar:7"])
        au3 = self.unit_of(self.inventory(), "AU-3")
        self.assertEqual([c["citation_status"] for c in au3["derived_norm_citations"]], ["current", "retired"])
        # The record holds no type: the norms commit has no derived norm, and no list is read.
        self.set_lists({"semantics": "not a list\n"})
        self.set_record('{"types_of_derived_norms": []}\n')
        self.assertEqual(self.inventory()["derived_norms"], [])
        self.assertNotIn("derived norm", self.started()["summary"])

    def test_acu78_a_record_that_does_not_meet_nrm16_leaves_project_json(self):
        """ACU-78, NRM-16: a record that does not meet NRM-16 gives no type; project.json of the norms commit does."""
        for data in ('{"types_of_derived_norms": ["semantics"]}', '{"types_of_derived_norms": ["semantics"]}\n\n',
                     '\ufeff{"types_of_derived_norms": ["semantics"]}\n', b'{"types_of_derived_norms": ["\xff"]}\n',
                     '{"types_of_derived_norms": ["semantics"], "x": 1}\n', '{"types_of_derived_norms": ["Semantics"]}\n',
                     '{"types_of_derived_norms": ["semantics", "semantics"]}\n', '{"types_of_derived_norms": "x"}\n',
                     '["semantics"]\n', '{"types_of_derived_norms": [NaN]}\n'):
            with self.subTest(data=data):
                self.set_record(data)
                self.assertEqual([d["derived_norm_id"] for d in self.inventory()["derived_norms"]],
                                 ["grammar:2", "grammar:7", "semantics:31", "semantics:32"])
        # Neither the record nor project.json of the norms commit can be read.
        project = json.loads(self.project)
        project["derived_norms"] = [{"type": "Grammar"}]
        self.set_project(json.dumps(project, indent=2) + "\n")
        self.refused(self.types_cannot_be_read())

    def test_acu78_never_the_project_json_of_the_acceptance_repository(self):
        """ACU-78: the types come from the norms commit, never from project.json of the acceptance repository."""
        project = json.loads(self.project)
        project["derived_norms"] = [{"type": "Grammar"}]
        text = json.dumps(project, indent=2) + "\n"
        write(os.path.join(self.acc, "project.json"), text)
        self.commit_all(self.acc)
        write(os.path.join(self.norms, "specs-repo-annotated", "project.json"), text)
        self.commit_all(self.norms)
        git(self.norms, "fetch", "-q", "origin")
        self.assertEqual([d["derived_norm_id"] for d in self.inventory()["derived_norms"]],
                         ["grammar:2", "grammar:7", "semantics:31", "semantics:32"])
        self.started()

    def test_acu58_a_list_of_derived_norms_is_missing(self):
        self.set_lists({"grammar": None})
        self.refused(f"acme/billing-norms has no specs-derived/grammar/derived-norms.jsonl at {self.norms_commit()[:7]}")

    def test_acu58_the_first_type_in_the_order_of_derived_norms(self):
        self.set_lists({"grammar": GRAMMAR.replace('"grammar:7"', '"grammar:9"'), "semantics": None})
        self.refused(f"acme/billing-norms: specs-derived/grammar/derived-norms.jsonl does not meet NRM-12")

    def test_acu58_a_list_that_does_not_meet_nrm12(self):
        good = derived_norm_line("grammar", 2, "2b2b2b2b", "customer", "specs-derived/grammar/billing.lark", 1, 2,
                                 [("CUS-1", "c0c0c0c0")])
        header = '{"kind": "header", "type": "grammar", "last_derived_norm_number": 7}'
        bad_lists = {
            "a byte order mark": "﻿" + GRAMMAR,
            "not UTF-8": GRAMMAR.encode() + b"\xff\n",
            "no line feed at the end": GRAMMAR[:-1],
            "an empty line": GRAMMAR + "\n",
            "a carriage return": GRAMMAR.replace("\n", "\r\n"),
            "empty": "",
            "the header line of another type": GRAMMAR.replace('"type": "grammar"', '"type": "semantics"'),
            "the fields of the header line in another order":
                '{"type": "grammar", "kind": "header", "last_derived_norm_number": 7}\n',
            "a header line of another kind": GRAMMAR.replace('"kind": "header"', '"kind": "other"'),
            "a negative last number": GRAMMAR.replace('"last_derived_norm_number": 7', '"last_derived_norm_number": -1'),
            "a boolean last number": GRAMMAR.replace('"last_derived_norm_number": 7',
                                                     '"last_derived_norm_number": true'),
            "an ID above the last number": GRAMMAR.replace('"last_derived_norm_number": 7',
                                                          '"last_derived_norm_number": 6'),
            "an ID of another type": GRAMMAR.replace('"grammar:7"', '"semantics:7"'),
            "an ID with a leading zero": GRAMMAR.replace('"grammar:7"', '"grammar:07"'),
            "the IDs not in order": list_of_derived_norms("grammar", 7, *GRAMMAR.splitlines()[:0:-1]),
            "an ID twice": GRAMMAR + good + "\n",
            "a fingerprint in upper case": GRAMMAR.replace("3a4b5c6d", "3A4B5C6D"),
            "a name of blanks": GRAMMAR.replace('"name": "row"', '"name": " \\t"'),
            "a name that breaks a line": GRAMMAR.replace('"name": "row"', '"name": "r\\u2028ow"'),
            "a name that is not valid Unicode": GRAMMAR.replace('"name": "row"', '"name": "\\ud800"'),
            "a path outside the output": GRAMMAR.replace("specs-derived/grammar/billing.lark",
                                                         "specs-derived/semantics/billing.lark"),
            "a path that is the list": GRAMMAR.replace("specs-derived/grammar/billing.lark",
                                                       "specs-derived/grammar/derived-norms.jsonl"),
            "a path with ..": GRAMMAR.replace("specs-derived/grammar/billing.lark", "specs-derived/grammar/../x"),
            "a first line of 0": GRAMMAR.replace('"first_line": 1', '"first_line": 0'),
            "a first line after the last": GRAMMAR.replace('"first_line": 4', '"first_line": 7'),
            "two derived norms that share a line": GRAMMAR.replace('"first_line": 4', '"first_line": 2'),
            "no cited norm": GRAMMAR.replace('[{"norm_id": "INV-7", "norm_hash": "5a627175"}]', "[]"),
            "cited norms not in order": GRAMMAR.replace(
                '[{"norm_id": "INV-7", "norm_hash": "5a627175"}]',
                '[{"norm_id": "INV-7", "norm_hash": "5a627175"}, {"norm_id": "INV-12", "norm_hash": "7d6e5f40"}]'),
            "a cited norm that is not a norm ID": GRAMMAR.replace('"norm_id": "INV-7"', '"norm_id": "IN-7"'),
            "a norm hash in upper case": GRAMMAR.replace('"norm_hash": "5a627175"', '"norm_hash": "5A627175"'),
            "a norm hash of 7 digits": GRAMMAR.replace('"norm_hash": "5a627175"', '"norm_hash": "5a62717"'),
            "a field more": GRAMMAR.replace('"kind": "derived_norm",', '"kind": "derived_norm", "x": 1,', 1),
            "a field given twice": GRAMMAR.replace('"name": "row",', '"name": "row", "name": "row",'),
            "a line of another kind": header + "\n" + good.replace('"derived_norm"', '"rule"') + "\n",
            "a constant": GRAMMAR.replace('"first_line": 4', '"first_line": NaN'),
            "not JSON": header + "\nnot json\n",
        }
        for case, text in bad_lists.items():
            with self.subTest(case=case):
                self.set_lists({"grammar": text})
                self.refused("acme/billing-norms: specs-derived/grammar/derived-norms.jsonl does not meet NRM-12")

    def test_acu58_a_list_with_only_its_meta_line(self):
        self.set_lists({"grammar": list_of_derived_norms("grammar", 0), "semantics": list_of_derived_norms("semantics", 4)})
        self.assertEqual(self.inventory()["derived_norms"], [])
        self.started()

    def test_acu78_a_project_without_derived_norms_reads_no_list(self):
        project = json.loads(self.project)
        del project["derived_norms"]
        self.set_project(json.dumps(project, indent=2) + "\n")
        self.set_lists({"grammar": "not a list\n"})
        write(os.path.join(self.acc, "units", "AU-3.md"), with_derived_norms(AU3))
        self.commit_all(self.acc)
        out = self.started()
        self.assertNotIn("derived norm", out["summary"])
        au3 = self.unit_of(self.inventory(), "AU-3")
        self.assertEqual([c["citation_status"] for c in au3["derived_norm_citations"]], ["retired", "retired"])
        self.assertEqual(au3["derived_norms_not_cited"], [])

    def test_nrm12_a_list_written_before_the_header_line_was_named_so(self):
        """NRM-12: a header line of kind "meta" is read as "header"."""
        self.set_lists({"grammar": GRAMMAR.replace('"kind": "header"', '"kind": "meta"')})
        write(os.path.join(self.acc, "units", "AU-3.md"), with_derived_norms(AU3))
        r = self.run_script("derived-norms", self.acc, "--norms-commit", self.norms_commit(), "AU-3")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("grammar:7", [d["derived_norm_id"] for d in json.loads(r.stdout)])

    def test_acu78_the_derived_norms_of_the_scope(self):
        write(os.path.join(self.norms, "specs-derived", "grammar", "billing.lark"),
              "// CUS-1@c0c0c0c0: x\ncustomer: NAME\n\n// INV-7@5a627175: a row \t\r\nrow: invoice\n  | x\n")
        self.set_lists({})
        write(os.path.join(self.acc, "units", "AU-3.md"), with_derived_norms(AU3))
        r = self.run_script("derived-norms", self.acc, "--norms-commit", self.norms_commit(), "AU-3")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        found = json.loads(r.stdout)
        # ACU-67: exactly these fields, in this order.
        self.assertEqual([list(d) for d in found], [["derived_norm_id", "derived_norm_fingerprint", "name", "path",
                                                     "first_line", "last_line", "lines_of_derived_norm",
                                                     "reason_in_acceptance_unit", "derived_norm_citation_without_reason"]] * 3)
        self.assertEqual([(d["derived_norm_id"], d["derived_norm_fingerprint"], d["reason_in_acceptance_unit"],
                           d["derived_norm_citation_without_reason"]) for d in found],
                         [("grammar:7", "3a4b5c6d", "the rule of a row", "- grammar:7@3a4b5c6d: "),
                          ("semantics:31", "6a7b8c9d", "the export", "- semantics:31@6a7b8c9d: "),
                          ("semantics:32", "9c0d1e2f", None, "- semantics:32@9c0d1e2f: ")])
        self.assertEqual({k: found[0][k] for k in ("name", "path", "first_line", "last_line")},
                         {"name": "row", "path": "specs-derived/grammar/billing.lark", "first_line": 4, "last_line": 6})
        # Its text: its lines at the norms commit, as steps 1 and 2 of NRM-14 give them (ACU-67).
        self.assertEqual(found[0]["lines_of_derived_norm"], "// INV-7@5a627175: a row\nrow: invoice\n  | x")
        self.assertIsNone(found[1]["lines_of_derived_norm"])  # the norms commit holds no specs-derived/semantics/eval.md
        # The scope follows "## Norms" of the working tree: without INV-12 and INV-15, semantics:31 leaves it.
        write(os.path.join(self.acc, "units", "AU-1.md"), AU1)
        r = self.run_script("derived-norms", self.acc, "--norms-commit", self.norms_commit(), "AU-1")
        self.assertEqual(json.loads(r.stdout), [])


STATUS_LINE_OF_GRAMMAR = ('{"type":"header","specs_commit":"' + "a" * 40 + '","generator":{"plugin":"clean-derived-norms",'
                          '"version":"0.5.0","tooling_commit":"' + "b" * 40 + '"},"model":"m"}\n'
                          '{"type":"rule","name":"row"}\n')
# NRM-5: a status file written before its first line was named the header line.
STATUS_LINE_OF_GRAMMAR_BEFORE_THE_HEADER_LINE = (STATUS_LINE_OF_GRAMMAR.replace('"type":"header"', '"type":"meta"')
                                                 .replace('"tooling_commit"', '"marketplace_commit"'))


class DefectOfDerivedNormsGenerator(DerivedNormsFixture):
    """ACU-79: what the script prints for the issue of a defect of a derived-norms generator."""

    def setUp(self):
        super().setUp()
        self.home = os.path.join(self.root, "home")
        os.makedirs(os.path.join(self.home, ".claude", "plugins"))
        write(os.path.join(self.norms, "specs-derived", "grammar", "status.jsonl"), STATUS_LINE_OF_GRAMMAR)
        write(os.path.join(self.norms, "specs-derived", "grammar", "billing.lark"), "row: invoice\n")
        self.set_lists({})
        self.set_plugins_of_claude_code({"clean-derived-norms@clean-language-tooling": [{"gitCommitSha": "c" * 40}]},
                                        {"clean-language-tooling": {"source": {"source": "github",
                                                                               "repo": "jpchauny/clean-language-tooling"}}})

    def set_plugins_of_claude_code(self, plugins, marketplaces):
        folder = os.path.join(self.home, ".claude", "plugins")
        for name, value in (("installed_plugins.json", {"version": 2, "plugins": plugins}),
                            ("known_marketplaces.json", marketplaces)):
            path = os.path.join(folder, name)
            if value is None or (name == "installed_plugins.json" and plugins is None):
                if os.path.exists(path):
                    os.remove(path)
            else:
                write(path, json.dumps(value))

    def generator_of(self, derived_norm_id="grammar:7", code=0):
        env = dict(ENV, HOME=self.home)
        r = subprocess.run([sys.executable, "-I", SCRIPT, "derived-norms-generator", self.acc, "--norms-commit",
                            self.norms_commit(), derived_norm_id], cwd=self.acc, env=env, capture_output=True,
                           text=True)
        self.assertEqual(r.returncode, code, r.stdout + r.stderr)
        return json.loads(r.stdout) if code == 0 else r.stdout

    def test_acu79_what_the_script_prints(self):
        found = self.generator_of()
        self.assertEqual(list(found), ["derived_norm_id", "derived_norm_fingerprint", "type", "name", "path",
                                       "first_line", "last_line", "cited_norms", "status_file", "generator",
                                       "marketplace_repository", "issue_body_start", "no_issue_message"])
        self.assertEqual(found["status_file"], "specs-derived/grammar/status.jsonl")
        self.assertEqual(found["generator"], {"plugin": "clean-derived-norms", "version": "0.5.0",
                                              "tooling_commit": "b" * 40})
        self.assertEqual(found["marketplace_repository"], "jpchauny/clean-language-tooling")
        self.assertIsNone(found["no_issue_message"])
        self.assertEqual(found["issue_body_start"],
                         "Derived norm: grammar:7@3a4b5c6d, of the type grammar, lines 4 to 6 of "
                         "specs-derived/grammar/billing.lark\n"
                         "Cited norms: INV-7@5a627175\n"
                         f"Generator: clean-derived-norms 0.5.0, tooling commit {'b' * 40}\n"
                         f"Norms commit: {self.norms_commit()}\n")
        self.assertEqual(self.generator_of("semantics:31")["issue_body_start"].splitlines()[1],
                         "Cited norms: INV-12@7d6e5f40, INV-15@9e8d7c6b")

    def test_acu79_no_status_file(self):
        for files in ({"status.jsonl": None}, {"other.jsonl": STATUS_LINE_OF_GRAMMAR}):
            with self.subTest(files=files):
                for name, text in files.items():
                    path = os.path.join(self.norms, "specs-derived", "grammar", name)
                    if text is None:
                        os.remove(path)
                    else:
                        write(path, text)
                self.set_lists({})
                found = self.generator_of()
                self.assertEqual((found["status_file"], found["generator"], found["marketplace_repository"]),
                                 (None, None, None))
                self.assertEqual(found["issue_body_start"].splitlines()[2],
                                 "Generator: no status file with a generator (NRM-5)")
                self.assertEqual(found["no_issue_message"],
                                 PREFIX + "the output of grammar has no status file with a generator (NRM-5); "
                                 "no issue is opened for grammar:7")
                write(os.path.join(self.norms, "specs-derived", "grammar", "status.jsonl"), STATUS_LINE_OF_GRAMMAR)
                self.set_lists({})

    def test_acu79_a_status_file_written_before_the_header_line(self):
        """NRM-5: "type" "meta" and "marketplace_commit" are read as "header" and "tooling_commit"."""
        expected = self.generator_of()
        write(os.path.join(self.norms, "specs-derived", "grammar", "status.jsonl"),
              STATUS_LINE_OF_GRAMMAR_BEFORE_THE_HEADER_LINE)
        self.set_lists({})
        found = self.generator_of()
        self.assertEqual(found["generator"], expected["generator"])
        self.assertEqual(found["issue_body_start"].splitlines()[2], expected["issue_body_start"].splitlines()[2])
        for mixed in (STATUS_LINE_OF_GRAMMAR.replace('"tooling_commit"', '"marketplace_commit"').replace(
                          '"version"', '"tooling_commit":"x","version"'),
                      STATUS_LINE_OF_GRAMMAR.replace('"type":"header"', '"type":"other"')):
            with self.subTest(mixed=mixed):
                write(os.path.join(self.norms, "specs-derived", "grammar", "status.jsonl"), mixed)
                self.set_lists({})
                self.assertIsNone(self.generator_of()["generator"])

    def test_acu79_a_generator_that_does_not_meet_nrm5(self):
        write(os.path.join(self.norms, "specs-derived", "grammar", "status.jsonl"),
              STATUS_LINE_OF_GRAMMAR.replace('"version":"0.5.0",', ""))
        self.set_lists({})
        self.assertIsNone(self.generator_of()["generator"])

    def test_acu79_the_marketplace_repository(self):
        a = {"source": {"source": "github", "repo": "acme/a"}}
        b = {"source": {"source": "github", "repo": "acme/b"}}
        sha = "b" * 40
        cases = [
            ({"clean-derived-norms@a": [{"gitCommitSha": sha}], "clean-derived-norms@b": [{"gitCommitSha": "c"}]},
             {"a": a, "b": b}, "acme/a"),
            ({"clean-derived-norms@a": [{"gitCommitSha": sha}], "clean-derived-norms@b": [{"gitCommitSha": sha}]},
             {"a": a, "b": b}, None),
            ({"clean-derived-norms@a": [{"gitCommitSha": "c"}], "clean-derived-norms@b": [{"gitCommitSha": "d"}]},
             {"a": a, "b": b}, None),
            ({"other@a": [{"gitCommitSha": sha}]}, {"a": a}, None),
            ({"clean-derived-norms@a": []}, {"a": {"source": {"source": "git", "url": "https://x/a.git"}}}, None),
            ({"clean-derived-norms@a": []}, {"a": {"source": {"source": "github", "repo": "no-slash"}}}, None),
            (None, {"a": a}, None),
            ({"clean-derived-norms@a": []}, None, None),
        ]
        for plugins, marketplaces, expected in cases:
            with self.subTest(plugins=plugins, marketplaces=marketplaces):
                self.set_plugins_of_claude_code(plugins, marketplaces)
                found = self.generator_of()
                self.assertEqual(found["marketplace_repository"], expected)
                self.assertEqual(found["no_issue_message"], None if expected else
                                 PREFIX + "no installed marketplace on GitHub holds the plugin clean-derived-norms; "
                                 "no issue is opened for grammar:7")

    def test_acu79_a_derived_norm_id_that_the_norms_commit_does_not_hold(self):
        self.assertEqual(self.generator_of("grammar:99", code=1).strip(),
                         PREFIX + "grammar:99 is not a derived norm of the norms commit")
        # A type that the types of derived norms of the norms commit do not hold has no list to read.
        self.assertEqual(self.generator_of("zzz:1", code=1).strip(),
                         PREFIX + "zzz:1 is not a derived norm of the norms commit")

    def test_acu79_the_list_of_its_type_cannot_be_read(self):
        commit = lambda: self.norms_commit()[:7]  # noqa: E731
        self.set_lists({"grammar": None})
        self.assertEqual(self.generator_of(code=1).strip(),
                         PREFIX + f"acme/billing-norms has no specs-derived/grammar/derived-norms.jsonl at {commit()}")
        self.set_lists({"grammar": b"x\n"})
        self.assertEqual(self.generator_of(code=1).strip(),
                         PREFIX + "acme/billing-norms: specs-derived/grammar/derived-norms.jsonl does not meet NRM-12")

    def test_acu79_project_json_that_does_not_meet_orc20(self):
        project = json.loads(self.project)
        project["derived_norms"] = [{"type": "grammar"}, {"type": "grammar"}]
        self.set_project(json.dumps(project, indent=2) + "\n")
        self.assertEqual(self.generator_of(code=1).strip(), PREFIX + f"acme/billing-norms: the types of derived norms "
                         f"at {self.norms_commit()[:7]} cannot be read (NRM-16)")

    def test_acu79_the_types_of_the_record(self):
        """ACU-79: a type that the record of the types of derived norms does not hold has no derived norm."""
        write(os.path.join(self.norms, "specs-derived", "types-of-derived-norms.json"),
              '{"types_of_derived_norms": ["semantics"]}\n')
        self.commit_all(self.norms)
        git(self.norms, "fetch", "-q", "origin")
        self.assertEqual(self.generator_of(code=1).strip(), PREFIX + "grammar:7 is not a derived norm of the norms commit")

    def test_acu79_reads_only_the_list_of_its_type(self):
        """ACU-79: of the lists of derived norms, the script reads only that of the type of the derived norm ID."""
        expected = self.generator_of()
        for semantics in (None, b"x\n"):
            with self.subTest(semantics=semantics):
                self.set_lists({"semantics": semantics})
                found = self.generator_of()
                self.assertEqual({k: v for k, v in found.items() if k != "issue_body_start"},
                                 {k: v for k, v in expected.items() if k != "issue_body_start"})
                self.assertEqual(found["issue_body_start"].splitlines()[:3],
                                 expected["issue_body_start"].splitlines()[:3])

    def test_acu79_the_name_of_a_plugin_forges_no_line(self):
        write(os.path.join(self.norms, "specs-derived", "grammar", "status.jsonl"),
              STATUS_LINE_OF_GRAMMAR.replace('"clean-derived-norms"', '"clean\\nderived"'))
        self.set_lists({})
        self.assertEqual(self.generator_of()["no_issue_message"],
                         PREFIX + 'no installed marketplace on GitHub holds the plugin "clean\\nderived"; '
                         "no issue is opened for grammar:7")


class WritingDerivedNorms(DerivedNormsFixture, WritingFixture):
    """ACU-67, ACU-69 with derived norms."""

    def test_acu69_a_written_unit_cites_its_scope(self):
        write(os.path.join(self.acc, "units", "AU-3.md"), with_derived_norms(
            AU3.replace("INV-12@0c1d2e3f", "INV-12@7d6e5f40")))
        problems = self.check(code=1)["problems"]
        self.assertEqual([p["message"] for p in problems], [
            "semantics:31@5e6f7a8b is changed; its derived norm fingerprint at the norms commit is 6a7b8c9d",
            "semantics:32@9c0d1e2f is in the scope of AU-3 and not in ## Derived norms (ACU-78)"])
        self.assertEqual(problems[0]["line"], 20)
        part = ("\n## Derived norms\n\n- grammar:7@3a4b5c6d: a row\n- semantics:31@6a7b8c9d: the export\n"
                "- semantics:32@9c0d1e2f: the row\n")
        write(os.path.join(self.acc, "units", "AU-3.md"), with_derived_norms(
            AU3.replace("INV-12@0c1d2e3f", "INV-12@7d6e5f40"), part))
        self.assertEqual(self.check()["problems"], [])

    def test_acu69_a_retired_derived_norm_citation(self):
        part = "\n## Derived norms\n\n- grammar:7@3a4b5c6d: a row\n- grammar:8@3a4b5c6d: gone\n"
        write(os.path.join(self.acc, "units", "AU-3.md"), with_derived_norms(
            AU3.replace("INV-12@0c1d2e3f", "INV-12@7d6e5f40"), part))
        messages = [p["message"] for p in self.check(code=1)["problems"]]
        self.assertIn("grammar:8@3a4b5c6d is retired; its derived norm fingerprint at the norms commit is none: the "
                      "derived norm is not in layer 2", messages)


if __name__ == "__main__":
    unittest.main()
