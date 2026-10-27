"""Tests of scripts/acceptance_ci.py.

The script that the workflow of the acceptance repository runs, as ACU-6,
ACU-34 and ACU-35 of specs/module.md say. Each test names the clause it
checks. Run with:

    python3 -m unittest discover -s apps/indra-software-factory/modules/acceptance-management/tests
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

PLUGIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(PLUGIN, "scripts", "acceptance_ci.py")

sys.dont_write_bytecode = True

ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t",
           GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null")

JUNIT = """cat > "$ACCEPTANCE_REPORT" <<'XML'
<testsuite><testcase classname="AU-1" name="adds"/><testcase classname="AU-1" name="subtracts"><failure/></testcase></testsuite>
XML
"""


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, env=ENV, capture_output=True, text=True, check=True)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


class AcceptanceCI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = os.path.realpath(self.tmp.name)
        self.code = os.path.join(self.root, "billing-code")
        os.mkdir(self.code)
        git(self.code, "init", "-q", "-b", "main")
        write(os.path.join(self.code, "build.sh"), "echo building\necho product-v1\n")
        git(self.code, "add", "build.sh")
        git(self.code, "commit", "-q", "-m", "code")
        self.code_commit = git(self.code, "rev-parse", "HEAD").stdout.strip()

        self.acc = os.path.join(self.root, "billing-acceptance")
        os.mkdir(self.acc)
        git(self.acc, "init", "-q", "-b", "main")
        repos = [{"owner": "acme", "name": "billing-acceptance", "layer": 3, "path": "billing-acceptance"},
                 {"owner": "acme", "name": "billing-code", "layer": 4, "path": "billing-code"}]
        write(os.path.join(self.acc, "project.json"), json.dumps({"project": "billing", "repositories": repos}))
        write(os.path.join(self.acc, "units", "AU-1.md"), "# AU-1 Add\n")
        write(os.path.join(self.acc, "units", "AU-2.md"), "# AU-2 Subtract\n")
        write(os.path.join(self.acc, "areas", "AA-1.md"), "# AA-1 Math\n@unit:AU-1 @unit:AU-2\n")
        write(os.path.join(self.acc, "tests", "AU-1", "run.sh"),
              "# AU-1: Two integers give their sum\n# INV-7@5a627175: the sum\n"
              'test "$PRODUCT_CMD" = product-v1\n')
        write(os.path.join(self.acc, "tests", "AU-2", "run.sh"), "# AU-2: x\nexit 1\n")
        write(os.path.join(self.acc, "tests", "AA-1", "run.sh"), "# AA-1: y\n# INV-9@0c1d2e3f: both\nexit 0\n")
        self.configure('sh "$ACCEPTANCE_TARGET/run.sh"', {"build": "sh build.sh", "env": "PRODUCT_CMD"})

    def tearDown(self):
        self.tmp.cleanup()

    def configure(self, command, entry):
        product = {"acme/billing-code": entry} if entry else {}
        write(os.path.join(self.acc, "acceptance.json"), json.dumps(
            {"default_profile": "product", "increments": [], "test_command": command, "product": product}))
        git(self.acc, "add", "-A")
        git(self.acc, "commit", "-q", "-m", "config")

    def run_ci(self, work=None, date="2026-10-27T00:00:00+00:00", env=None, git_url=None):
        return subprocess.run(
            [sys.executable, "-I", SCRIPT, "--repo", self.acc, "--work", work or os.path.join(self.root, "work"),
             "--produced-by", "https://ci/run/1", "--git-url", git_url or os.path.join(self.root, "{name}"),
             "--date", date],
            env=env or ENV, capture_output=True, text=True)

    def commit_records(self):
        git(self.acc, "add", "-A", "records")
        git(self.acc, "commit", "-q", "-m", "records")

    def records(self, target):
        path = os.path.join(self.acc, "records", f"{target}.jsonl")
        if not os.path.exists(path):
            return None
        with open(path, encoding="utf-8") as f:
            return [json.loads(line) for line in f]

    def test_acu6_empty_test_command_records_nothing(self):
        self.configure("", None)
        r = self.run_ci()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.acc, "records")))

    def test_acu34_acu35_one_line_per_folder_without_a_report(self):
        r = self.run_ci()
        self.assertEqual(r.returncode, 0, r.stderr)
        au1, au2, aa1 = self.records("AU-1"), self.records("AU-2"), self.records("AA-1")
        self.assertEqual([(x["test"], x["result"]) for x in au1], [("tests/AU-1", "pass")])
        self.assertEqual([x["result"] for x in au2], ["fail"])
        self.assertEqual([x["result"] for x in aa1], ["pass"])
        line = au1[0]
        self.assertEqual(line["kind"], "test")
        self.assertEqual(line["date"], "2026-10-27T00:00:00+00:00")
        self.assertEqual(line["produced_by"], "https://ci/run/1")
        self.assertEqual(line["for"]["reference_commits"], {"acme/billing-code": self.code_commit})
        self.assertEqual(line["for"]["norm_hashes"], {"INV-7": "5a627175"})
        self.assertEqual(sorted(line["for"]["files"]), ["tests/AU-1/run.sh", "units/AU-1.md"])
        blob = git(self.acc, "rev-parse", "HEAD:units/AU-1.md").stdout.strip()
        self.assertEqual(line["for"]["files"]["units/AU-1.md"], blob)
        self.assertEqual(sorted(aa1[0]["for"]["files"]),
                         ["areas/AA-1.md", "tests/AA-1/run.sh", "units/AU-1.md", "units/AU-2.md"])

    def test_acu35_lines_are_only_added(self):
        self.assertEqual(self.run_ci().returncode, 0)
        first = self.records("AU-1")
        self.commit_records()
        write(os.path.join(self.acc, "units", "AU-1.md"), "# AU-1 Add two integers\n")
        git(self.acc, "commit", "-q", "-am", "unit")
        self.assertEqual(self.run_ci(date="2026-10-27T01:00:00+00:00").returncode, 0)
        self.assertEqual(self.records("AU-1")[:1], first)
        self.assertEqual(len(self.records("AU-1")), 2)

    def test_acu34_step3_nothing_changed_records_nothing(self):
        self.assertEqual(self.run_ci().returncode, 0)
        self.commit_records()
        r = self.run_ci(date="2026-10-27T01:00:00+00:00")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("nothing recorded", r.stdout)
        self.assertEqual(len(self.records("AU-1")), 1)

    def test_acu34_step3_a_changed_reference_commit_runs_again(self):
        self.assertEqual(self.run_ci().returncode, 0)
        self.commit_records()
        write(os.path.join(self.code, "README"), "x\n")
        git(self.code, "add", "README")
        git(self.code, "commit", "-q", "-m", "more code")
        new = git(self.code, "rev-parse", "HEAD").stdout.strip()
        r = self.run_ci(date="2026-10-27T01:00:00+00:00")
        self.assertEqual(r.returncode, 0, r.stderr)
        au1 = self.records("AU-1")
        self.assertEqual(len(au1), 2)
        self.assertEqual(au1[1]["for"]["reference_commits"], {"acme/billing-code": new})

    def test_acu34_step3_an_unreadable_acceptance_commit_runs_again(self):
        self.assertEqual(self.run_ci().returncode, 0)
        path = os.path.join(self.acc, "records", "AU-1.jsonl")
        line = self.records("AU-1")[0]
        line["acceptance_commit"] = "0" * 40
        write(path, json.dumps(line) + "\n")
        for other in ("AU-2", "AA-1"):
            os.remove(os.path.join(self.acc, "records", f"{other}.jsonl"))
        self.commit_records()
        r = self.run_ci(date="2026-10-27T01:00:00+00:00")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(len(self.records("AU-1")), 2)

    def test_acu6_published_is_accepted_and_not_run(self):
        self.configure('sh "$ACCEPTANCE_TARGET/run.sh"',
                       {"build": "sh build.sh", "env": "PRODUCT_CMD", "published": "exit 7"})
        r = self.run_ci()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual([x["result"] for x in self.records("AU-1")], ["pass"])

    def test_acu6_an_empty_published_is_refused(self):
        self.configure("true", {"build": "sh build.sh", "env": "PRODUCT_CMD", "published": ""})
        r = self.run_ci()
        self.assertEqual(r.returncode, 1)
        self.assertIn("ACU-6", r.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.acc, "records")))

    def test_acu35_a_date_of_another_form_is_refused(self):
        r = self.run_ci(date="2026-10-27T00:00:00Z")
        self.assertEqual(r.returncode, 1)
        self.assertIn("ACU-35", r.stderr)

    def test_acu35_one_line_per_test_case_with_a_junit_report(self):
        self.configure(JUNIT, {"build": "sh build.sh", "env": "PRODUCT_CMD"})
        r = self.run_ci()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual([(x["test"], x["result"]) for x in self.records("AU-1")],
                         [("AU-1::adds", "pass"), ("AU-1::subtracts", "fail")])

    def test_acu34_a_failed_build_records_nothing(self):
        self.configure('sh "$ACCEPTANCE_TARGET/run.sh"', {"build": "exit 3", "env": "PRODUCT_CMD"})
        r = self.run_ci()
        self.assertEqual(r.returncode, 1)
        self.assertIn("build of acme/billing-code failed", r.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.acc, "records")))

    def test_acu6_a_product_entry_with_another_field_is_refused(self):
        self.configure("true", {"build": "sh build.sh", "env": "PRODUCT_CMD", "publish": "true"})
        r = self.run_ci()
        self.assertEqual(r.returncode, 1)
        self.assertIn("ACU-6", r.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.acc, "records")))

    def test_acu34_build_and_test_command_never_see_the_token(self):
        token_file = os.path.join(self.root, "token")
        write(token_file, "secret-token\n")
        # The build looks for the token in its environment, in the environment
        # of its parent (where /proc exists) and in the files of its clone.
        build = ('if env | grep -q secret-token; then echo leak; '
                 'elif [ -r /proc/$PPID/environ ] && grep -aq secret-token /proc/$PPID/environ; then echo leak; '
                 'elif grep -rq secret-token . 2>/dev/null; then echo leak; else echo clean; fi')
        self.configure('test "$PRODUCT_CMD" = clean && ! env | grep -q secret-token',
                       {"build": build, "env": "PRODUCT_CMD"})
        r = subprocess.run(
            [sys.executable, "-I", SCRIPT, "--repo", self.acc, "--work", os.path.join(self.root, "work"),
             "--produced-by", "https://ci/run/1", "--git-url", os.path.join(self.root, "{name}"),
             "--date", "2026-10-27T00:00:00+00:00", "--token-file", token_file],
            env=ENV, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual({x["result"] for x in self.records("AU-1")}, {"pass"})
        self.assertFalse(os.path.exists(token_file))

    def test_acu34_a_token_in_the_environment_is_refused(self):
        r = self.run_ci(env=ENV | {"CODE_READ_TOKEN": "secret"})
        self.assertEqual(r.returncode, 1)
        self.assertIn("--token-file", r.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.acc, "records")))

    def test_acu34_an_unreadable_reference_commit_records_nothing(self):
        r = self.run_ci(git_url=os.path.join(self.root, "missing-{name}"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("reference commit of acme/billing-code", r.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.acc, "records")))

    def test_acu6_product_of_an_unknown_repository_is_refused(self):
        write(os.path.join(self.acc, "acceptance.json"), json.dumps(
            {"default_profile": "product", "increments": [], "test_command": "true",
             "product": {"acme/other": {"build": "true", "env": "X"}}}))
        r = self.run_ci()
        self.assertEqual(r.returncode, 1)
        self.assertIn("acme/other", r.stderr)

    def test_acu34_folders_run_in_the_order_of_the_ids(self):
        write(os.path.join(self.acc, "tests", "AU-10", "run.sh"), "# AU-10: z\nexit 0\n")
        self.configure('sh "$ACCEPTANCE_TARGET/run.sh"', {"build": "sh build.sh", "env": "PRODUCT_CMD"})
        r = self.run_ci()
        self.assertEqual(r.returncode, 0, r.stderr)
        order = [line.split(":")[0] for line in r.stdout.splitlines() if line.startswith(("AA-", "AU-"))]
        self.assertEqual(order, ["AA-1", "AU-1", "AU-2", "AU-10"])

    def test_acu34_a_work_folder_inside_the_acceptance_repository_is_refused(self):
        r = self.run_ci(work=os.path.join(self.acc, ".ci", "work"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("must be outside the acceptance repository", r.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.acc, ".ci")))
        self.assertFalse(os.path.exists(os.path.join(self.acc, "records")))


if __name__ == "__main__":
    unittest.main()
