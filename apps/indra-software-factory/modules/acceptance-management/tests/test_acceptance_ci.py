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

# The files of a unit (ACU-8) and of an area (ACU-7); AU1_HASH and AU2_HASH are
# their unit hashes (ACU-52), computed by hand.
AU1 = ("# AU-1 Add\n\nArea: AA-1\n\n## Narrative\n\nIn order to add\nAs a user\nI want sums\n\n"
       "## Norms\n\n- INV-7@5a627175: the sum\n")
AU2 = ("# AU-2 Subtract\n\nArea: AA-1\n\n## Narrative\n\nIn order to subtract\nAs a user\nI want differences\n\n"
       "## Norms\n\n- INV-9@0c1d2e3f: the difference\n")
AA1 = ("# AA-1 Math\n\n## Purpose\n\nArithmetic.\n\n## Scenarios\n\n```gherkin\n"
       "@SC-3 @unit:AU-1 @unit:AU-2 @INV-7 @INV-9\nScenario: Both together\n  Then it works\n```\n")
AU1_HASH, AU2_HASH = "f84f8333", "554a95b2"

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
        write(os.path.join(self.acc, "units", "AU-1.md"), AU1)
        write(os.path.join(self.acc, "units", "AU-2.md"), AU2)
        write(os.path.join(self.acc, "areas", "AA-1.md"), AA1)
        write(os.path.join(self.acc, "tests", "AU-1", "run.sh"),
              f"# AU-1@{AU1_HASH}: Add\n# SC-1@1234abcd: Two integers give their sum\n"
              'test "$PRODUCT_CMD" = product-v1\n')
        write(os.path.join(self.acc, "tests", "AU-2", "run.sh"), f"# AU-2@{AU2_HASH}: Subtract\nexit 1\n")
        write(os.path.join(self.acc, "tests", "AA-1", "run.sh"),
              "# AA-1@aaaa1111: Math\n# SC-3@bbbb2222: Both together\nexit 0\n")
        self.configure('sh "$ACCEPTANCE_TARGET/run.sh"', {"build": "sh build.sh", "env": "PRODUCT_CMD"})

    def tearDown(self):
        self.tmp.cleanup()

    def configure(self, command, entry):
        product = {"acme/billing-code": entry} if entry else {}
        write(os.path.join(self.acc, "acceptance.json"), json.dumps(
            {"default_done_profile": "product", "last_area_id": 0, "last_unit_id": 0, "last_scenario_id": 0,
             "test_command": command, "product": product}))
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
        self.assertEqual(line["for"]["hashes"], {"AU-1": AU1_HASH, "SC-1": "1234abcd"})
        self.assertEqual(line["for"]["norm_hashes"], {"INV-7": "5a627175"})
        self.assertEqual(sorted(line["for"]["files"]), ["tests/AU-1/run.sh"])
        blob = git(self.acc, "rev-parse", "HEAD:tests/AU-1/run.sh").stdout.strip()
        self.assertEqual(line["for"]["files"]["tests/AU-1/run.sh"], blob)
        self.assertEqual(aa1[0]["for"]["hashes"],
                         {"AA-1": "aaaa1111", "AU-1": AU1_HASH, "AU-2": AU2_HASH, "SC-3": "bbbb2222"})
        self.assertEqual(aa1[0]["for"]["norm_hashes"], {"INV-7": "5a627175", "INV-9": "0c1d2e3f"})
        self.assertEqual(sorted(aa1[0]["for"]["files"]), ["tests/AA-1/run.sh"])

    def test_acu35_an_id_cited_with_two_hashes_maps_to_the_empty_string(self):
        write(os.path.join(self.acc, "tests", "AA-1", "run.sh"),
              "# AA-1@aaaa1111: Math\n# AU-1@00000000: Add\n# SC-3@bbbb2222: Both together\nexit 0\n")
        write(os.path.join(self.acc, "units", "AU-2.md"), AU2.replace("0c1d2e3f", "11112222")
              + "\n")
        write(os.path.join(self.acc, "units", "AU-3.md"),
              AU1.replace("AU-1", "AU-3").replace("5a627175", "99998888"))
        write(os.path.join(self.acc, "areas", "AA-1.md"), AA1.replace("@unit:AU-2", "@unit:AU-2 @unit:AU-3"))
        git(self.acc, "add", "-A")
        git(self.acc, "commit", "-q", "-m", "conflicts")
        self.assertEqual(self.run_ci().returncode, 0)
        line = self.records("AA-1")[0]
        self.assertEqual(line["for"]["hashes"]["AU-1"], "")
        self.assertEqual(line["for"]["norm_hashes"]["INV-7"], "")
        self.assertEqual(line["for"]["norm_hashes"]["INV-9"], "11112222")

    def test_acu35_an_area_crosses_only_the_units_of_its_scenarios(self):
        write(os.path.join(self.acc, "areas", "AA-1.md"),
              AA1.replace("Arithmetic.", "Arithmetic, as @unit:AU-2 says.").replace("@unit:AU-2 ", "@unit:AU-4 "))
        git(self.acc, "add", "-A")
        git(self.acc, "commit", "-q", "-m", "area")
        self.assertEqual(self.run_ci().returncode, 0)
        line = self.records("AA-1")[0]
        # AU-2 is named only in the prose; AU-4 has no file, so it has no unit hash (ACU-35).
        self.assertEqual(line["for"]["hashes"],
                         {"AA-1": "aaaa1111", "AU-1": AU1_HASH, "AU-4": "", "SC-3": "bbbb2222"})
        self.assertEqual(line["for"]["norm_hashes"], {"INV-7": "5a627175"})

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
            {"default_done_profile": "product", "last_area_id": 0, "last_unit_id": 0, "last_scenario_id": 0,
             "test_command": "true",
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

    def test_acu35_for_is_read_from_the_commit_not_the_working_tree(self):
        # The code of layer 4 runs in test_command: it changes units/ and tests/, and Python writes __pycache__.
        self.configure('printf -- "- INV-9@11112222: injected\\n" >> units/AU-1.md; '
                       'echo "# AU-1@99999999: forged" >> tests/AU-1/run.sh; '
                       'mkdir -p "$ACCEPTANCE_TARGET/__pycache__"; echo x > "$ACCEPTANCE_TARGET/__pycache__/t.pyc"; '
                       'sh "$ACCEPTANCE_TARGET/run.sh"', {"build": "sh build.sh", "env": "PRODUCT_CMD"})
        r = self.run_ci()
        self.assertEqual(r.returncode, 0, r.stderr)
        line = self.records("AU-1")[0]
        self.assertEqual(line["for"]["norm_hashes"], {"INV-7": "5a627175"})
        self.assertEqual(line["for"]["hashes"], {"AU-1": AU1_HASH, "SC-1": "1234abcd"})
        self.assertEqual(sorted(line["for"]["files"]), ["tests/AU-1/run.sh"])
        self.assertEqual(line["for"]["files"]["tests/AU-1/run.sh"],
                         git(self.acc, "rev-parse", "HEAD:tests/AU-1/run.sh").stdout.strip())
        self.assertEqual(sorted(self.records("AA-1")[0]["for"]["norm_hashes"]), ["INV-7", "INV-9"])
        self.assertEqual(self.records("AA-1")[0]["for"]["norm_hashes"]["INV-9"], "0c1d2e3f")

    def test_acu34_a_folder_that_is_not_committed_is_not_run(self):
        write(os.path.join(self.acc, "tests", "AU-5", "run.sh"), "exit 0\n")
        self.assertEqual(self.run_ci().returncode, 0)
        self.assertIsNone(self.records("AU-5"))

    def test_acu35_no_commit_records_nothing(self):
        other = os.path.join(self.root, "empty-acceptance")
        os.mkdir(other)
        git(other, "init", "-q", "-b", "main")
        for name in ("project.json", "acceptance.json"):
            with open(os.path.join(self.acc, name), encoding="utf-8") as f:
                write(os.path.join(other, name), f.read())
        self.acc = other
        r = self.run_ci()
        self.assertEqual(r.returncode, 1)
        self.assertIn("cannot read the commit HEAD", r.stderr)
        self.assertFalse(os.path.exists(os.path.join(other, "records")))

    def test_acu34_an_empty_last_line_of_the_build_fails(self):
        self.configure("true", {"build": "printf 'x\\n\\n'", "env": "PRODUCT_CMD"})
        r = self.run_ci()
        self.assertEqual(r.returncode, 1)
        self.assertIn("build of acme/billing-code failed", r.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.acc, "records")))

    def test_acu6_acceptance_json_of_another_form_is_refused(self):
        good = {"default_done_profile": "product", "last_area_id": 0, "last_unit_id": 0, "last_scenario_id": 0,
                "test_command": "true", "product": {}}
        bad = ["[]", json.dumps(dict(good, test_command=7)), json.dumps(dict(good, test_command=["true"])),
               json.dumps(dict(good, test_command=0)), json.dumps(dict(good, last_unit_id="1")),
               json.dumps(dict(good, last_unit_id=-1)), json.dumps(dict(good, increments=[])),
               json.dumps(dict(good, product=[])), json.dumps(dict(good, default_done_profile="gold")), "not json"]
        for text in bad:
            with self.subTest(text=text):
                write(os.path.join(self.acc, "acceptance.json"), text)
                r = self.run_ci()
                self.assertEqual(r.returncode, 1)
                self.assertIn("fields of ACU-6", r.stderr)
                self.assertFalse(os.path.exists(os.path.join(self.acc, "records")))

    def test_acu55_a_folder_that_is_not_an_id_is_not_run(self):
        for name in ("AU-0", "AU-03"):
            write(os.path.join(self.acc, "tests", name, "run.sh"), "exit 0\n")
        self.configure('sh "$ACCEPTANCE_TARGET/run.sh"', {"build": "sh build.sh", "env": "PRODUCT_CMD"})
        self.assertEqual(self.run_ci().returncode, 0)
        self.assertIsNone(self.records("AU-0"))
        self.assertIsNone(self.records("AU-03"))

    def test_acu34_a_work_folder_inside_the_acceptance_repository_is_refused(self):
        r = self.run_ci(work=os.path.join(self.acc, ".ci", "work"))
        self.assertEqual(r.returncode, 1)
        self.assertIn("must be outside the acceptance repository", r.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.acc, ".ci")))
        self.assertFalse(os.path.exists(os.path.join(self.acc, "records")))


if __name__ == "__main__":
    unittest.main()
