"""Tests of use-cases/write/write.py, the deterministic part of /specs-management:write.

Spec: use-cases/write/specs/write.md (ORC-59 to ORC-69). Each test names the
ORC-n it checks. The rules that only the model follows (the interview of
ORC-63, the writing of ORC-64, the full check of ORC-67) are in SKILL.md and
consistency.js, not here. Run with:

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
SCRIPT = os.path.join(PLUGIN, "use-cases", "write", "write.py")
MOVE = os.path.join(PLUGIN, "scripts", "move.py")

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
    """A project of five layers (LAY-1); layers 0 and 1 are cloned in setUp, each a clone of a bare
    repository under <tmp>/origin/acme/, and layer 2 only by the tests that need it (clone)."""

    def setUp(self):
        self.tmp = os.path.realpath(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.project = json.dumps({"project": "p", "repositories": [
            {"owner": "acme", "name": "p-drafts", "layer": 0, "path": "p-drafts"},
            {"owner": "acme", "name": "p-specs", "layer": 1, "path": "p-specs"},
            {"owner": "acme", "name": "p-norms", "layer": 2, "path": "p-norms"},
            {"owner": "acme", "name": "p-acceptance", "layer": 3, "path": "p-acceptance"},
            {"owner": "acme", "name": "p-code", "layer": 4, "path": "p-code"}]}, indent=1) + "\n"
        self.r = {}
        for layer, name in ((0, "p-drafts"), (1, "p-specs")):
            self.clone(layer, name)

    def clone(self, layer, name):
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

    def run_write(self, cmd, *opts, path=None, layer=0):
        argv = [sys.executable, "-I", SCRIPT, cmd, self.r[layer], *opts]
        if path is not None:
            argv += ["--", path]
        p = subprocess.run(argv, env=ENV, capture_output=True, text=True)
        return p.returncode, p.stdout

    def ok(self, cmd, *opts, path=None, layer=0):
        code, out = self.run_write(cmd, *opts, path=path, layer=layer)
        self.assertEqual(code, 0, out)
        return json.loads(out)

    def commit_change(self, case, path, layer=0):
        """The flow of step 7 with a yes: diff, commit, and the command it prints."""
        plan = self.ok("diff", case, path=path, layer=layer)
        for side in plan["layers"]:
            out = self.ok("commit", case, str(side), "--fingerprint", plan["fingerprints"][str(side)],
                          path=path, layer=layer)
            p = sh(out["command"], self.tmp)
            self.assertEqual(p.returncode, 0, p.stderr)
        return plan

    def status(self, layer):
        return git(self.r[layer], "status", "--porcelain")

    def last(self, layer):
        return git(self.r[layer], "log", "-1", "--format=%B").strip()


class Locate(Base):
    def test_cases(self):
        """ORC-60: the four cases, and a path of layer 1 without a verb gives the two choices."""
        self.assertEqual(self.ok("locate")["case"], "new draft spec")
        self.assertEqual(self.ok("locate", path="specs/a.md")["case"], "new draft spec")
        self.commit(0, {"specs/d.md": "# D\n"})
        self.assertEqual(self.ok("locate", path="specs/d.md", layer=1)["case"], "change of a draft spec")
        self.commit(1, {"specs/a.md": "# A\n"})
        out = self.ok("locate", path="specs/a.md")
        self.assertIsNone(out["case"])
        self.assertEqual(out["choices"], ["change of a spec", "deletion of a spec"])
        self.assertEqual(out["repos"], {"0": self.r[0], "1": self.r[1]})

    def test_invalid_path(self):
        """ORC-60: an invalid path writes nothing and gives the message of the spec."""
        self.commit(0, {"specs/x/a.md": "# A\n"})
        for p in ("../a.md", "/a.md", "specs/./a.md", "", "specs/x", "specs/a.txt"):
            code, out = self.run_write("locate", path=p)
            self.assertEqual(code, 1, p)
            self.assertEqual(out.strip(), f"specs-management:write: {p}: invalid path")
        self.assertEqual(self.status(0), "")

    def test_only_layers_0_and_1(self):
        """ORC-59: from a layer other than 0 and 1 the skill writes nothing, with the message of the spec."""
        self.clone(2, "p-norms")
        code, out = self.run_write("locate", layer=2)
        self.assertEqual((code, out.strip()),
                         (1, "specs-management:write: runs only from the repository of layer 0 or of layer 1"))
        code, out = self.run_write("check", path="specs/a.md", layer=2)
        self.assertEqual(code, 1)


class Change(Base):
    def test_new_draft(self):
        """ORC-61, ORC-66: a new draft is committed in layer 0 alone, by explicit path, with its message."""
        self.write(self.r[0], "specs/a.md", "# A\n")
        self.write(self.r[0], "other.md", "work of another session\n")
        self.write(self.r[0], "staged.md", "staged by another session\n")
        git(self.r[0], "add", "staged.md")
        plan = self.commit_change("new", "specs/a.md")
        self.assertEqual(plan["layers"], [0])
        self.assertIn("+# A", plan["display"])
        self.assertIn("docs: add draft spec", plan["display"])
        self.assertEqual(self.last(0), "docs: add draft spec\n\nspecs/a.md")
        self.assertEqual(git(self.r[0], "show", "--name-only", "--format=", "HEAD").split(), ["specs/a.md"])
        self.assertEqual(git(self.r[0], "rev-parse", "HEAD"), git(self.r[0], "rev-parse", "origin/main"))
        self.assertEqual(self.status(0), "A  staged.md\n?? other.md\n")
        self.assertEqual(git(self.r[1], "ls-files").split(), ["project.json"])

    def test_change_messages(self):
        """ORC-66: change of a draft spec and change of a spec share the subject "docs: change draft spec"."""
        self.commit(0, {"specs/a.md": "# A\n"})
        for case in ("change-draft", "change-spec"):
            self.write(self.r[0], "specs/a.md", self.read(self.r[0], "specs/a.md") + case + "\n")
            self.commit_change(case, "specs/a.md")
            self.assertEqual(self.last(0), "docs: change draft spec\n\nspecs/a.md")

    def test_second_change_after_new(self):
        """ORC-66: once the commit of a new draft is pushed, the next change of the run is a change of a draft."""
        self.write(self.r[0], "specs/a.md", "# A\n")
        self.commit_change("new", "specs/a.md")
        self.write(self.r[0], "specs/a.md", "# A\n\nMore.\n")
        code, out = self.run_write("diff", "new", path="specs/a.md")
        self.assertEqual((code, out.strip()), (1, "specs-management:write: specs/a.md: already in layer 0"))
        self.commit_change("change-draft", "specs/a.md")
        self.assertEqual(self.last(0), "docs: change draft spec\n\nspecs/a.md")
        self.assertEqual(self.status(0), "")

    def test_no_final_newline(self):
        """ORC-66: a line with no line end is shown as git shows it, never run into the next line of the diff."""
        self.commit(0, {"specs/a.md": "x\nold"})
        self.write(self.r[0], "specs/a.md", "x\nnew\nmore")
        plan = self.ok("diff", "change-draft", path="specs/a.md")
        self.assertIn("\n x\n-old\n\\ No newline at end of file\n+new\n+more\n\\ No newline at end of file\n",
                      plan["display"])
        self.write(self.r[0], "specs/a.md", "x\nold\n")
        plan = self.ok("diff", "change-draft", path="specs/a.md")
        self.assertIn("\n x\n-old\n\\ No newline at end of file\n+old\n", plan["display"])
        self.write(self.r[0], "specs/a.md", "x\x0cy\nold")
        plan = self.ok("diff", "change-draft", path="specs/a.md")
        self.assertIn("\n-x\n+x\x0cy\n old\n", plan["display"])

    def test_glob_characters_in_path(self):
        """ORC-66, ORC-69: a path with `[` stages and commits that file only, never one that the glob matches."""
        self.write(self.r[0], "s/[ab].md", "# AB\n")
        self.write(self.r[0], "s/a.md", "work of another session\n")
        self.commit_change("new", "s/[ab].md")
        self.assertEqual(git(self.r[0], "show", "--name-only", "--format=", "HEAD").split(), ["s/[ab].md"])
        self.assertEqual(self.status(0), "?? s/a.md\n")

    def test_glob_characters_in_promote(self):
        """ORC-35, ORC-69: the commands of a promote commit the moved file only, never one that the glob matches."""
        self.commit(0, {"s/[ab].md": "# AB\n", "s/a.md": "# A0\n"})
        self.commit(1, {"s/a.md": "# A1\n"})
        self.write(self.r[0], "s/a.md", "work of another session\n")
        self.write(self.r[1], "s/a.md", "work of another session\n")

        def mv(*args):
            p = subprocess.run([sys.executable, "-I", MOVE, *args], env=ENV, capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stdout)
            return json.loads(p.stdout)
        plan = mv("plan", "promote", self.r[0], "--", "s/[ab].md")
        for side in ("target", "source"):
            out = mv("apply", "promote", self.r[0], side, "--fingerprint", plan["fingerprints"][side], "--", "s/[ab].md")
            self.assertEqual(sh(out["command"], self.tmp).returncode, 0)
        for layer in (0, 1):
            self.assertEqual(git(self.r[layer], "show", "--name-only", "--format=", "HEAD").split(), ["s/[ab].md"])
            self.assertEqual(self.status(layer), " M s/a.md\n")

    def test_layer_1_needs_demote(self):
        """ORC-62, ORC-69: a spec of layer 1 is never changed in place; after its demote it is a draft."""
        self.commit(1, {"specs/a.md": "# A\n", "specs/b.md": "[A](a.md)\n"})
        self.write(self.r[0], "specs/a.md", "# A changed\n")
        code, out = self.run_write("diff", "change-spec", path="specs/a.md")
        self.assertEqual((code, out.strip()), (1, "specs-management:write: specs/a.md: in layer 1; demote it first"))
        os.remove(os.path.join(self.r[0], "specs/a.md"))
        self.demote("specs/a.md")
        self.assertEqual(self.ok("locate", path="specs/a.md")["case"], "change of a draft spec")
        self.write(self.r[0], "specs/a.md", "# A changed\n")
        self.commit_change("change-spec", "specs/a.md")
        self.assertEqual(self.read(self.r[0], "specs/a.md"), "# A changed\n")

    def demote(self, path):
        def mv(*args):
            p = subprocess.run([sys.executable, "-I", MOVE, *args], env=ENV, capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stdout)
            return json.loads(p.stdout)
        plan = mv("plan", "demote", self.r[1], "--", path)
        for side in ("target", "source"):
            out = mv("apply", "demote", self.r[1], side, "--fingerprint", plan["fingerprints"][side], "--", path)
            self.assertEqual(sh(out["command"], self.tmp).returncode, 0)

    def test_refusals_before_commit(self):
        """ORC-66: nothing to commit, a draft not written, a new draft already in layer 0, a stale fingerprint."""
        self.commit(0, {"specs/a.md": "# A\n"})
        code, out = self.run_write("diff", "change-draft", path="specs/a.md")
        self.assertEqual((code, out.strip()), (1, "specs-management:write: specs/a.md: nothing to commit"))
        code, out = self.run_write("diff", "new", path="specs/b.md")
        self.assertEqual((code, out.strip()), (1, "specs-management:write: specs/b.md: not written in layer 0"))
        self.write(self.r[0], "specs/a.md", "# A2\n")
        code, out = self.run_write("diff", "new", path="specs/a.md")
        self.assertEqual((code, out.strip()), (1, "specs-management:write: specs/a.md: already in layer 0"))
        plan = self.ok("diff", "change-draft", path="specs/a.md")
        self.write(self.r[0], "specs/a.md", "# A3\n")
        code, out = self.run_write("commit", "change-draft", "0", "--fingerprint", plan["fingerprints"]["0"],
                                   path="specs/a.md")
        self.assertEqual((code, out.strip()), (3, "changed"))

    def test_branch_and_origin(self):
        """ORC-66: the push goes to the default branch of layer 0, at the commit of origin."""
        self.write(self.r[0], "specs/a.md", "# A\n")
        git(self.r[0], "commit", "-q", "--allow-empty", "-m", "local only")
        code, out = self.run_write("diff", "new", path="specs/a.md")
        self.assertEqual((code, out.strip()), (1, "specs-management:write: layer 0: not at origin/main"))


class Check(Base):
    def test_cheap_checks(self):
        """ORC-65: broken links, terms defined elsewhere, statement IDs used elsewhere, and the neighbours."""
        self.commit(1, {"specs/process.md": "# P\n\n| Term | Meaning |\n|---|---|\n| Draft | A file. |\n\n"
                                            "- **ORC-90.** Taken. See [A](a.md).\n",
                        "specs/other.md": "Refers to ORC-91.\n", "specs/uses.md": "The intent is kept.\n"})
        self.commit(0, {"specs/side.md": "[A](a.md)\n"})
        self.write(self.r[0], "specs/a.md",
                   "# A\n\n| Term | Meaning |\n|---|---|\n| **Draft** | The file. |\n| Intent | What. |\n\n"
                   "- **ORC-90.** One.\n- **ORC-91.** Two. See [P](process.md), [X](x.md) and "
                   "[Y (not specified yet)](absent:y.md).\n\n```\n| Term | Meaning |\n|---|---|\n| Code | no |\n```\n")
        out = self.ok("check", path="specs/a.md")
        self.assertEqual(out["broken_links"], [{"line": 9, "target": "specs/x.md", "absent": False},
                                               {"line": 9, "target": "specs/y.md", "absent": True}])
        self.assertEqual(out["terms"], [{"term": "Draft", "line": 5,
                                         "also": [{"layer": 1, "path": "specs/process.md", "line": 5}]}])
        self.assertEqual(out["ids"], [
            {"id": "ORC-90", "line": 8, "also": [{"layer": 1, "path": "specs/process.md", "line": 7, "declared": True}]},
            {"id": "ORC-91", "line": 9, "also": [{"layer": 1, "path": "specs/other.md", "line": 1, "declared": False}]}])
        self.assertEqual(out["neighbours"], [
            {"layer": 0, "path": "specs/side.md", "why": ["links to the draft"]},
            {"layer": 1, "path": "specs/process.md",
             "why": ["defines a term of the draft", "holds a term of the draft", "linked from the draft",
                     "links to the draft"]},
            {"layer": 1, "path": "specs/uses.md", "why": ["holds a term of the draft"]}])
        self.assertEqual(self.status(0), "?? specs/a.md\n")

    def test_gherkin_rules(self):
        """ORC-65: a statement ID declared as a Gherkin rule, in a fenced block, is checked too."""
        self.commit(1, {"specs/b.md": "```gherkin\n  Rule: ORC-70 Taken\n```\n"})
        self.write(self.r[0], "specs/a.md", "```gherkin\nFeature: A\n  Rule: ORC-70 Mine\n  Rule: ORC-71 Free\n```\n")
        out = self.ok("check", path="specs/a.md")
        self.assertEqual(out["ids"], [{"id": "ORC-70", "line": 3,
                                       "also": [{"layer": 1, "path": "specs/b.md", "line": 2, "declared": True}]}])

    def test_scope(self):
        """ORC-67: the full check reads every .md file of layers 0 and 1 but the draft."""
        self.commit(0, {"specs/a.md": "# A\n", "specs/b.md": "# B\n", "x.txt": "x\n"})
        self.commit(1, {"specs/a.md": "# A1\n"})
        out = self.ok("scope", path="specs/a.md")
        self.assertEqual(out["files"], [{"layer": 0, "path": "specs/b.md"}, {"layer": 1, "path": "specs/a.md"}])
        self.assertEqual(out["roots"], {"0": self.r[0], "1": self.r[1]})


class Delete(Base):
    def setUp(self):
        super().setUp()
        self.commit(1, {"specs/process.md": "See [A (not specified yet)](absent:a.md) now.\n"
                                            "Also [the spec A](a.md#x \"t\").\n",
                        "specs/keep.md": "[B](b.md)\n"})
        self.commit(0, {"specs/a.md": "# A\n", "specs/b.md": "Uses [A](./a.md) here.\n",
                        "specs/ref.md": "[r]: a.md\n"})

    def flow(self):
        plan = self.ok("links", path="specs/a.md")
        out = self.ok("delete", "--fingerprint", plan["fingerprint"], path="specs/a.md")
        return plan, out

    def test_deletion(self):
        """ORC-68: the draft and every link to it, absent or plain, in both layers, with its text; two commits."""
        plan, out = self.flow()
        self.assertEqual(out["changed"], {"0": ["specs/b.md", "specs/a.md"], "1": ["specs/process.md"]})
        self.assertEqual(self.read(self.r[1], "specs/process.md"), "See  now.\nAlso .\n")
        self.assertNotIn("A (not specified yet)", self.read(self.r[1], "specs/process.md"))
        self.assertEqual(self.read(self.r[0], "specs/b.md"), "Uses  here.\n")
        self.assertFalse(os.path.exists(os.path.join(self.r[0], "specs/a.md")))
        self.assertEqual(self.read(self.r[1], "specs/keep.md"), "[B](b.md)\n")
        self.assertEqual(plan["refdefs"], [{"layer": 0, "path": "specs/ref.md", "line": 1}])
        self.assertIn({"layer": 1, "path": "specs/process.md", "line": 1,
                       "before": "See [A (not specified yet)](absent:a.md) now.", "after": "See  now."}, out["lines"])
        # The model rewrites a broken sentence after the user's yes; the diff shows it.
        self.write(self.r[1], "specs/process.md", "See now.\nAlso .\n")
        diff = self.commit_change("delete", "specs/a.md")
        self.assertEqual(diff["layers"], [0, 1])
        self.assertIn("layer 1: --- a/specs/process.md", diff["display"])
        self.assertEqual(self.last(0), "docs: delete spec\n\nspecs/a.md")
        self.assertEqual(self.last(1), "docs: delete links to a deleted spec\n\nspecs/a.md")
        self.assertEqual(sorted(git(self.r[0], "show", "--name-only", "--format=", "HEAD").split()),
                         ["specs/a.md", "specs/b.md"])
        self.assertEqual(git(self.r[1], "show", "--name-only", "--format=", "HEAD").split(), ["specs/process.md"])
        for layer in (0, 1):
            self.assertEqual(self.status(layer), "")

    def test_absent_link_in_angle_brackets(self):
        """ORC-68: an absent link whose destination is in angle brackets is a link of the audit, and goes too."""
        self.commit(1, {"specs/angle.md": "See [X (not specified yet)](<absent:a.md>) now.\n"})
        _, out = self.flow()
        self.assertIn("specs/angle.md", out["changed"]["1"])
        self.assertEqual(self.read(self.r[1], "specs/angle.md"), "See  now.\n")

    def test_bytes_not_utf8(self):
        """A byte that is not UTF-8 near a link keeps its escape in the output, under a UTF-8 locale."""
        self.commit(1, {"specs/bytes.md": b"Caf\xe9 [A (not specified yet)](absent:a.md).\n"})
        plan = self.ok("links", path="specs/a.md")
        env = dict(ENV, LANG="en_US.UTF-8", LC_ALL="en_US.UTF-8")
        p = subprocess.run([sys.executable, "-I", SCRIPT, "delete", self.r[0], "--fingerprint", plan["fingerprint"],
                            "--", "specs/a.md"], env=env, capture_output=True)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn(b"Caf\\udce9 .", p.stdout)
        self.assertEqual(self.read(self.r[1], "specs/process.md"), "See  now.\nAlso .\n")

    def test_no_layer_1_commit_when_nothing_changed(self):
        """ORC-68: layer 1 gets a commit only when a file of layer 1 changed."""
        self.commit(1, {"specs/process.md": "Nothing here.\n"})
        self.flow()
        diff = self.commit_change("delete", "specs/a.md")
        self.assertEqual(diff["layers"], [0])
        self.assertEqual(self.last(1), "add")

    def test_resume_layer_1(self):
        """ORC-68: when only layer 0 is committed, the same diff gives the commit of layer 1 alone."""
        self.flow()
        plan = self.ok("diff", "delete", path="specs/a.md")
        out = self.ok("commit", "delete", "0", "--fingerprint", plan["fingerprints"]["0"], path="specs/a.md")
        self.assertEqual(sh(out["command"], self.tmp).returncode, 0)
        plan = self.ok("diff", "delete", path="specs/a.md", layer=1)
        self.assertEqual(plan["layers"], [1])

    def test_layer_0_left_unpushed(self):
        """ORC-68: layer 1 is not committed while the commit of layer 0 is not pushed."""
        self.flow()
        plan = self.ok("diff", "delete", path="specs/a.md")
        out = self.ok("commit", "delete", "0", "--fingerprint", plan["fingerprints"]["0"], path="specs/a.md")
        self.assertEqual(sh(out["command"].rsplit(" && ", 1)[0], self.tmp).returncode, 0)
        code, out = self.run_write("diff", "delete", path="specs/a.md")
        self.assertEqual((code, out.strip()), (1, "specs-management:write: layer 0: not at origin/main"))

    def test_commit_refused_after_delete(self):
        """ORC-68: a refused commit exits 1, not 3 (which is a stale fingerprint only), so the skill gives back the
        files; the rollback gives back both layers."""
        self.flow()
        plan = self.ok("diff", "delete", path="specs/a.md")
        other = os.path.join(self.tmp, "other")
        git(self.tmp, "clone", "-q", os.path.join(self.tmp, "origin", "acme", "p-drafts.git"), other)
        self.write(other, "x.md", "another session\n")
        git(other, "add", "x.md")
        git(other, "commit", "-q", "-m", "x")
        git(other, "push", "-q", "origin", "main")
        code, out = self.run_write("commit", "delete", "0", "--fingerprint", plan["fingerprints"]["0"],
                                   path="specs/a.md")
        self.assertEqual((code, out.strip()), (1, "specs-management:write: layer 0: not at origin/main"))
        self.ok("rollback", "1", path="specs/a.md")
        self.ok("rollback", "0", path="specs/a.md")
        self.assertEqual((self.status(0), self.status(1)), ("", ""))

    def test_rollback(self):
        """ORC-68, ORC-69: a refused diff gives back the files of the deletion, and nothing else."""
        self.write(self.r[1], "notes.md", "another session\n")
        self.flow()
        self.ok("rollback", "1", path="specs/a.md")
        self.ok("rollback", "0", path="specs/a.md")
        self.assertEqual(self.status(0), "")
        self.assertEqual(self.status(1), "?? notes.md\n")
        self.assertEqual(self.read(self.r[0], "specs/a.md"), "# A\n")

    def test_rollback_glob_characters(self):
        """ORC-69: the rollback reads each path literally; another session's file that its glob matches stays."""
        self.commit(0, {"specs/a[1].md": "# A1\n", "specs/a1.md": "# other\n"})
        plan = self.ok("links", path="specs/a[1].md")
        self.ok("delete", "--fingerprint", plan["fingerprint"], path="specs/a[1].md")
        self.write(self.r[0], "specs/a1.md", "# another session\n")
        self.ok("rollback", "0", path="specs/a[1].md")
        self.assertEqual(self.status(0), " M specs/a1.md\n")
        self.assertEqual(self.read(self.r[0], "specs/a[1].md"), "# A1\n")

    def test_line_separators_are_not_line_ends(self):
        """ORC-65, ORC-68: lines end at CR LF, LF or CR only, as mdlinks counts them; U+2028 is inside a line."""
        self.commit(0, {"specs/c.md": "Intro\u2028more\nSee [A](a.md) here.\n"})
        plan = self.ok("links", path="specs/a.md")
        row = next(l for l in plan["lines"] if l["path"] == "specs/c.md")
        self.assertEqual((row["line"], row["before"], row["after"]), (2, "See [A](a.md) here.", "See  here."))
        self.commit(1, {"specs/p.md": "| Term | Meaning |\n|---|---|\n| Draft | A file. |\n"})
        self.write(self.r[0], "specs/d.md", "# D\u2028x\n\n| Term | Meaning |\n|---|---|\n| Draft | The file. |\n")
        out = self.ok("check", path="specs/d.md")
        self.assertEqual(out["terms"], [{"term": "Draft", "line": 5,
                                         "also": [{"layer": 1, "path": "specs/p.md", "line": 3}]}])

    def test_refusals(self):
        """ORC-62, ORC-69: not after its demote, or a file to touch with uncommitted changes."""
        self.commit(1, {"specs/c.md": "# C\n"})
        code, out = self.run_write("links", path="specs/c.md")
        self.assertEqual((code, out.strip()), (1, "specs-management:write: specs/c.md: in layer 1; demote it first"))
        self.write(self.r[1], "specs/process.md", "[A](a.md) edited by another session\n")
        code, out = self.run_write("links", path="specs/a.md")
        self.assertEqual((code, out.strip()),
                         (1, "specs-management:write: specs/process.md: uncommitted changes in layer 1"))
        self.assertEqual(self.read(self.r[0], "specs/a.md"), "# A\n")

    def test_untracked_not_rewritten(self):
        """ORC-69: an untracked file that links to the deleted spec is listed and left as it is."""
        self.write(self.r[1], "specs/new.md", "[A](a.md)\n")
        plan, _ = self.flow()
        self.assertEqual(plan["untracked"], [{"layer": 1, "path": "specs/new.md"}])
        self.assertEqual(self.read(self.r[1], "specs/new.md"), "[A](a.md)\n")

    def test_stale_fingerprint(self):
        """ORC-68: the deletion writes only what the user approved."""
        plan = self.ok("links", path="specs/a.md")
        self.commit(1, {"specs/more.md": "[A](a.md)\n"})
        code, out = self.run_write("delete", "--fingerprint", plan["fingerprint"], path="specs/a.md")
        self.assertEqual((code, out.strip()), (3, "changed"))
        self.assertTrue(os.path.exists(os.path.join(self.r[0], "specs/a.md")))


class Skill(unittest.TestCase):
    def test_trigger_and_prohibitions(self):
        """ORC-59, ORC-69: the skill starts only when asked, and never names a forbidden git command to run."""
        with open(os.path.join(PLUGIN, "use-cases", "write", "SKILL.md"), encoding="utf-8") as f:
            text = f.read()
        head = text.split("---")[1]
        self.assertIn("name: write", head)
        self.assertIn("Use only when the user types /specs-management:write", head)
        self.assertIn("Never on your own", head)
        # The only commands the skill runs itself are those of write.py: no git command of its own.
        blocks = text.split("```sh")[1:]
        self.assertTrue(blocks)
        for b in blocks:
            self.assertNotIn("git ", b.split("```")[0])

if __name__ == "__main__":
    unittest.main()
