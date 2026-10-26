"""Tests of scripts/move.py, the shared part of /specs-management:promote and /specs-management:demote.

Specs: specs/module.md (ORC-35 to ORC-48), use-cases/promote/specs/promote.md
(ORC-49 to ORC-52) and use-cases/demote/specs/demote.md (ORC-53 to ORC-57).
Each test names the ORC-n it checks. Run with:

    python3 -m unittest discover -s apps/indra-software-factory/modules/specs-management/tests
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

PLUGIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(PLUGIN, "scripts", "move.py")

sys.dont_write_bytecode = True

ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t",
           GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null")


def sh(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, shell=True, env=ENV, capture_output=True, text=True)


def git(cwd, *args):
    p = subprocess.run(["git", *args], cwd=cwd, env=ENV, capture_output=True, text=True)
    if p.returncode:
        raise AssertionError(p.stderr)
    return p.stdout


class Base(unittest.TestCase):
    """A project with layers 0, 1 and 2, each a clone of a bare repository under <tmp>/origin/acme/."""

    def setUp(self):
        self.tmp = os.path.realpath(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.project = json.dumps({"project": "p", "repositories": [
            {"owner": "acme", "name": "p-drafts", "layer": 0, "path": "p-drafts"},
            {"owner": "acme", "name": "p-specs", "layer": 1, "path": "p-specs"},
            {"owner": "acme", "name": "p-norms", "layer": 2, "path": "p-norms"},
            {"owner": "acme", "name": "p-code", "layer": 3, "path": "p-code"}]}, indent=1) + "\n"
        self.r = {}
        for layer, name in ((0, "p-drafts"), (1, "p-specs"), (2, "p-norms")):
            bare = os.path.join(self.tmp, "origin", "acme", name + ".git")
            os.makedirs(bare)
            git(bare, "init", "-q", "--bare", "-b", "main")
            work = os.path.join(self.tmp, "proj", name)
            git(self.tmp, "clone", "-q", bare, work)
            git(work, "checkout", "-q", "-b", "main")
            self.write(work, "project.json", self.project)
            git(work, "add", "project.json")
            git(work, "commit", "-q", "-m", "init")
            git(work, "push", "-q", "-u", "origin", "main")
            git(work, "remote", "set-head", "origin", "main")
            self.r[layer] = work

    def write(self, repo, rel, text):
        path = os.path.join(repo, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(text.encode() if isinstance(text, str) else text)

    def read(self, repo, rel):
        with open(os.path.join(repo, rel), "rb") as f:
            return f.read().decode()

    def commit(self, layer, files, msg="add"):
        for rel, text in files.items():
            self.write(self.r[layer], rel, text)
        git(self.r[layer], "add", "--", *files)
        git(self.r[layer], "commit", "-q", "-m", msg)
        git(self.r[layer], "push", "-q", "origin", "main")

    def move(self, cmd, uc, *paths, layer=1, opts=()):
        p = subprocess.run([sys.executable, "-I", SCRIPT, cmd, uc, self.r[layer], *opts, "--", *paths],
                           env=ENV, capture_output=True, text=True)
        return p.returncode, p.stdout

    def run_all(self, uc, *paths, layer=1):
        """The flow of the skill with a yes: plan, apply and run the target's command, then the source's."""
        code, out = self.move("plan", uc, *paths, layer=layer)
        self.assertEqual(code, 0, out)
        plan = json.loads(out)
        if not plan["resume"]:
            code, out = self.move("apply", uc, *paths, layer=layer,
                                  opts=("target", "--fingerprint", plan["fingerprints"]["target"]))
            self.assertEqual(code, 0, out)
            p = sh(json.loads(out)["command"], self.tmp)
            self.assertEqual(p.returncode, 0, p.stderr)
        code, out = self.move("apply", uc, *paths, layer=layer,
                              opts=("source", "--fingerprint", plan["fingerprints"]["source"]))
        self.assertEqual(code, 0, out)
        p = sh(json.loads(out)["command"], self.tmp)
        self.assertEqual(p.returncode, 0, p.stderr)
        return plan

    def tracked(self, layer):
        return set(git(self.r[layer], "ls-files").split())

    def snapshot(self, layer):
        return {f: self.read(self.r[layer], f) for f in self.tracked(layer)}


class Promote(Base):
    def test_one_file_and_links(self):
        """ORC-49, ORC-50: moved at the same path; absent links of layer 1 become plain; links to drafts become absent."""
        self.commit(0, {"specs/language/expressions.md": "[Types](types.md) and [Spec](https://x.org/a.md)\n",
                        "specs/language/types.md": "# Types\n"})
        self.commit(1, {"specs/process.md": "See [Expressions (not specified yet)](absent:language/expressions.md#ops).\n"})
        self.run_all("promote", "specs/language/expressions.md", layer=0)
        self.assertIn("specs/language/expressions.md", self.tracked(1))
        self.assertNotIn("specs/language/expressions.md", self.tracked(0))
        self.assertEqual(self.read(self.r[1], "specs/process.md"), "See [Expressions](language/expressions.md#ops).\n")
        self.assertEqual(self.read(self.r[1], "specs/language/expressions.md"),
                         "[Types (not specified yet)](absent:types.md) and [Spec](https://x.org/a.md)\n")
        self.assertEqual(git(self.r[1], "log", "-1", "--format=%B").strip(),
                         "docs: promote specs from layer 0\n\nspecs/language/expressions.md")
        self.assertEqual(git(self.r[0], "log", "-1", "--format=%s").strip(), "docs: promote specs to layer 1")
        for layer in (0, 1):
            self.assertEqual(git(self.r[layer], "rev-parse", "HEAD"), git(self.r[layer], "rev-parse", "origin/main"))

    def test_two_files_together(self):
        """ORC-50: a link between two files promoted in the same run stays plain."""
        self.commit(0, {"specs/language/expressions.md": "[Types](types.md)\n", "specs/language/types.md": "# T\n"})
        self.run_all("promote", "specs/language", layer=0)
        self.assertEqual(self.read(self.r[1], "specs/language/expressions.md"), "[Types](types.md)\n")

    def test_not_links(self):
        """ORC-50 (must not): images, code spans, fenced code and URLs do not change."""
        text = ("![Diagram](types.md) `[Types](types.md)` [S](https://e.com/types.md)\n"
                "```\n[Types](types.md)\n```\n<!-- [Types](types.md) -->\n")
        self.commit(0, {"specs/a.md": text, "specs/types.md": "# T\n"})
        self.run_all("promote", "specs/a.md", layer=0)
        self.assertEqual(self.read(self.r[1], "specs/a.md"), text)

    def test_folder(self):
        """ORC-49: a folder selects its files, and nothing else."""
        self.commit(0, {"specs/manager/README.md": "# M\n", "specs/manager/cln.md": "# C\n", "specs/other.md": "# O\n"})
        self.run_all("promote", "specs/manager", layer=0)
        self.assertEqual(self.tracked(1), {"project.json", "specs/manager/README.md", "specs/manager/cln.md"})


class Demote(Base):
    def test_links_become_absent(self):
        """ORC-53, ORC-54: links of layer 1 to a demoted file or emptied folder become absent; layer 0 is not rewritten."""
        self.commit(1, {"specs/process.md": "[cln](manager/cln.md#run) [Manager](manager/) [P](process.md)\n",
                        "specs/manager/cln.md": "[Lockfile (not specified yet)](absent:lockfile.md)\n",
                        "specs/manager/README.md": "# M\n"})
        self.commit(0, {"specs/manager/lockfile.md": "# L\n", "specs/index.md": "[cln](manager/cln.md)\n"})
        self.run_all("demote", "specs/manager/cln.md", "specs/manager/README.md")
        self.assertEqual(self.read(self.r[1], "specs/process.md"),
                         "[cln (not specified yet)](absent:manager/cln.md#run) "
                         "[Manager (not specified yet)](absent:manager/) [P](process.md)\n")
        self.assertEqual(self.read(self.r[0], "specs/manager/cln.md"), "[Lockfile](lockfile.md)\n")
        self.assertEqual(self.read(self.r[0], "specs/index.md"), "[cln](manager/cln.md)\n")
        self.assertEqual(git(self.r[0], "log", "-1", "--format=%s").strip(), "docs: demote specs from layer 1")
        self.assertEqual(git(self.r[1], "log", "-1", "--format=%s").strip(), "docs: demote specs to layer 0")

    def test_round_trip(self):
        """ORC-41, ORC-55: demote then promote gives back every file byte for byte, and the reverse too."""
        self.commit(1, {"specs/process.md": "[cln](manager/cln.md) [L](manager/lockfile.md)\n",
                        "specs/manager/cln.md": "[Lock](lockfile.md) [Back](../process.md)\n",
                        "specs/manager/lockfile.md": "# L\n"})
        self.commit(0, {"specs/draft.md": "# D\n"})
        s1, s0 = self.snapshot(1), self.snapshot(0)
        self.run_all("demote", "specs/manager")
        self.run_all("promote", "specs/manager", layer=0)
        self.assertEqual((self.snapshot(1), self.snapshot(0)), (s1, s0))
        self.run_all("promote", "specs/draft.md", layer=0)
        self.run_all("demote", "specs/draft.md")
        self.assertEqual((self.snapshot(1), self.snapshot(0)), (s1, s0))


class Refusals(Base):
    def test_messages(self):
        """ORC-39, ORC-48, ORC-51, ORC-56: every condition that holds, in order, and nothing written."""
        self.commit(1, {"specs/a.md": "# A\n", "specs/b.md": "[A](a.md \"title\")\n", "specs/c.md": "[A](a.md)\n"})
        self.commit(0, {"specs/a.md": "# draft\n"})
        self.write(self.r[1], "specs/c.md", "[A](a.md) changed\n")
        before = (git(self.r[0], "status", "--porcelain"), git(self.r[1], "status", "--porcelain"))
        code, out = self.move("plan", "demote", "specs/a.md", "specs/x.md", "../y")
        self.assertEqual(code, 1)
        self.assertEqual(out.splitlines(), [
            "specs-management:demote: ../y: invalid path",
            "specs-management:demote: specs/x.md: not in layer 1",
            "specs-management:demote: specs/a.md: already in layer 0",
            "specs-management:demote: specs/c.md: uncommitted changes in layer 1",
            "specs-management:demote: specs/b.md:1: link cannot be rewritten",
        ])
        self.assertEqual(before, (git(self.r[0], "status", "--porcelain"), git(self.r[1], "status", "--porcelain")))

    def test_case_and_branch_and_origin(self):
        """ORC-39 conditions 4, 7, 8."""
        self.commit(0, {"specs/a.md": "# a\n"})
        self.commit(1, {"specs/A.md": "# A\n"})
        code, out = self.move("plan", "promote", "specs/a.md", layer=0)
        self.assertEqual(out.strip(), "specs-management:promote: specs/a.md: already in layer 1")
        git(self.r[1], "rm", "-q", "specs/A.md")
        git(self.r[1], "commit", "-q", "-m", "local only")
        code, out = self.move("plan", "promote", "specs/a.md", layer=0)
        self.assertEqual(out.strip(), "specs-management:promote: layer 1: not at origin/main")
        git(self.r[0], "checkout", "-q", "-b", "work")
        code, out = self.move("plan", "promote", "specs/a.md", layer=0)
        self.assertEqual(out.splitlines(), ["specs-management:promote: layer 0: not on its default branch main",
                                            "specs-management:promote: layer 1: not at origin/main"])

    def test_no_path_and_layer_2(self):
        """ORC-37, ORC-39 condition 1."""
        self.assertEqual(self.move("plan", "promote", layer=0),
                         (1, "specs-management:promote: expected at least one path\n"))
        self.assertEqual(self.move("plan", "promote", "specs/a.md", layer=2),
                         (1, "specs-management:promote: runs only from the repository of layer 0 or of layer 1\n"))


class Safety(Base):
    def test_change_while_waiting(self):
        """ORC-43: a file that changes after the plan makes apply write nothing (exit 3)."""
        self.commit(1, {"specs/a.md": "# A\n", "specs/b.md": "[A](a.md)\n"})
        code, out = self.move("plan", "demote", "specs/a.md")
        fp = json.loads(out)["fingerprints"]["target"]
        self.commit(1, {"specs/b.md": "[A](a.md) more\n"})
        self.assertEqual(self.move("apply", "demote", "specs/a.md", opts=("target", "--fingerprint", fp)), (3, "changed\n"))
        self.assertNotIn("specs/a.md", os.listdir(self.r[0]))

    def test_other_session_staged_file_is_not_committed(self):
        """ORC-43, ORC-46: only the move's paths are committed."""
        self.commit(1, {"specs/a.md": "# A\n"})
        self.commit(0, {"notes.md": "# N\n"})
        self.write(self.r[0], "notes.md", "# N edited\n")
        git(self.r[0], "add", "notes.md")
        self.run_all("demote", "specs/a.md")
        self.assertEqual(git(self.r[0], "show", "--name-only", "--format=", "HEAD").split(), ["specs/a.md"])
        self.assertEqual(git(self.r[0], "status", "--porcelain").strip(), "M  notes.md")

    def target_step(self, uc, path, layer=1):
        code, out = self.move("plan", uc, path, layer=layer)
        plan = json.loads(out)
        code, out = self.move("apply", uc, path, layer=layer, opts=("target", "--fingerprint", plan["fingerprints"]["target"]))
        self.assertEqual(code, 0, out)
        return plan, json.loads(out)

    def test_resume_and_rollback(self):
        """ORC-44, ORC-45: a rollback gives back the target; a rerun after the target's push only does the source."""
        self.commit(1, {"specs/a.md": "# A\n", "specs/b.md": "[A](a.md)\n"})
        plan, out = self.target_step("demote", "specs/a.md")
        self.assertEqual(self.move("rollback", "demote", *out["paths"], opts=("target",)), (0, ""))
        self.assertEqual(git(self.r[0], "status", "--porcelain"), "")
        plan, out = self.target_step("demote", "specs/a.md")
        self.assertEqual(sh(out["command"], self.tmp).returncode, 0)
        code, out = self.move("plan", "demote", "specs/a.md")
        resumed = json.loads(out)
        self.assertTrue(resumed["resume"])
        self.assertEqual(resumed["fingerprints"]["source"], plan["fingerprints"]["source"])
        self.run_all("demote", "specs/a.md")
        self.assertNotIn("specs/a.md", self.tracked(1))
        self.assertEqual(self.read(self.r[1], "specs/b.md"), "[A (not specified yet)](absent:a.md)\n")
        code, out = self.move("plan", "demote", "specs/a.md")
        self.assertEqual(out.strip(), "specs-management:demote: specs/a.md: not in layer 1")

    def test_source_command_fails(self):
        """ORC-44 state 3, ORC-45: a failed source commit is rolled back, the files are in both, a rerun resumes."""
        self.commit(1, {"specs/a.md": "# A\n", "specs/b.md": "[A](a.md)\n"})
        plan, out = self.target_step("demote", "specs/a.md")
        self.assertEqual(sh(out["command"], self.tmp).returncode, 0)
        code, out = self.move("apply", "demote", "specs/a.md", opts=("source", "--fingerprint", plan["fingerprints"]["source"]))
        self.assertEqual(code, 0, out)
        # The person denies the command: it never runs. The skill rolls the source back.
        self.assertEqual(self.move("rollback", "demote", *json.loads(out)["paths"], opts=("source",)), (0, ""))
        self.assertEqual(git(self.r[1], "status", "--porcelain"), "")
        self.assertIn("specs/a.md", self.tracked(0))
        self.assertIn("specs/a.md", self.tracked(1))
        self.assertTrue(json.loads(self.move("plan", "demote", "specs/a.md")[1])["resume"])

    def test_source_changed_after_the_yes(self):
        """ORC-43: a file of the source that changes after the plan makes apply source write nothing."""
        self.commit(1, {"specs/a.md": "# A\n", "specs/b.md": "[A](a.md)\n"})
        plan, out = self.target_step("demote", "specs/a.md")
        self.assertEqual(sh(out["command"], self.tmp).returncode, 0)
        self.commit(1, {"specs/c.md": "also [A](a.md)\n"})
        self.assertEqual(self.move("apply", "demote", "specs/a.md", opts=("source", "--fingerprint", plan["fingerprints"]["source"])),
                         (3, "changed\n"))
        self.assertEqual(git(self.r[1], "status", "--porcelain"), "")

    def test_failed_apply_gives_back(self):
        """ORC-44 state 1: when git fails while apply writes the target, what it wrote is given back."""
        self.commit(0, {"n/a.md": "# A\n"})
        code, out = self.move("plan", "promote", "n", layer=0)
        fp = json.loads(out)["fingerprints"]["target"]
        open(os.path.join(self.r[1], ".git", "index.lock"), "w").close()
        code, out = self.move("apply", "promote", "n", layer=0, opts=("target", "--fingerprint", fp))
        os.remove(os.path.join(self.r[1], ".git", "index.lock"))
        self.assertEqual(code, 1)
        self.assertTrue(out.startswith("specs-management:promote: git failed: "))
        self.assertFalse(os.path.exists(os.path.join(self.r[1], "n")))


class Details(Base):
    def test_submodule_and_order(self):
        """ORC-39 condition 3, ORC-48 order: a submodule is refused; lines by path, then by line number."""
        git(self.r[1], "update-index", "--add", "--cacheinfo", "160000,1234567890123456789012345678901234567890,specs/sub")
        git(self.r[1], "commit", "-q", "-m", "sub")
        git(self.r[1], "push", "-q", "origin", "main")
        self.commit(1, {"specs/a.md": "# A\n", "specs/b.md": "\n" * 8 + "[A](a.md 't')\n[A](a.md 't')\n"})
        code, out = self.move("plan", "demote", "specs/sub", "specs/a.md")
        self.assertEqual(out.splitlines(), ["specs-management:demote: specs/sub: a symbolic link or a submodule",
                                            "specs-management:demote: specs/b.md:9: link cannot be rewritten",
                                            "specs-management:demote: specs/b.md:10: link cannot be rewritten"])

    def test_percent_and_whitespace(self):
        """ORC-39 condition 6 lists only real escapes; ORC-36 keeps the whitespace around a destination."""
        self.commit(1, {"specs/100%.md": "# P\n", "specs/b.md": "[P](100%.md) [Q]( 100%.md )\n"})
        self.run_all("demote", "specs/100%.md")
        self.assertEqual(self.read(self.r[1], "specs/b.md"),
                         "[P (not specified yet)](absent:100%.md) [Q (not specified yet)]( absent:100%.md )\n")

    def test_not_utf8(self):
        """ORC-40: a file that is not valid UTF-8 is rewritten too, and its other bytes come back exact."""
        self.commit(1, {"specs/a.md": "# A\n", "specs/b.md": "Caf\xe9 [A](a.md)\n".encode("latin-1")})
        self.run_all("demote", "specs/a.md")
        with open(os.path.join(self.r[1], "specs/b.md"), "rb") as f:
            self.assertEqual(f.read(), "Caf\xe9 [A (not specified yet)](absent:a.md)\n".encode("latin-1"))

    def test_no_path_tests_the_rest(self):
        """ORC-39: with no path, conditions 7 and 8 are still tested."""
        git(self.r[1], "checkout", "-q", "-b", "feat")
        self.assertEqual(self.move("plan", "promote", layer=0)[1].splitlines(),
                         ["specs-management:promote: expected at least one path",
                          "specs-management:promote: layer 1: not on its default branch main"])


if __name__ == "__main__":
    unittest.main()
