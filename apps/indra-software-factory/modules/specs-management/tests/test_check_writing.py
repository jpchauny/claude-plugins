"""Tests of use-cases/check-writing/check_writing.py, the deterministic parts of /specs-management:check-writing.

Spec: use-cases/check-writing/specs/check-writing.md. Each test names the AUD-n or
AUD-En it checks. Run with:

    python3 -m unittest discover -s apps/indra-software-factory/modules/specs-management/tests
"""

import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest

PLUGIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(PLUGIN, "use-cases", "check-writing", "check_writing.py")
GUIDELINE = os.path.join(PLUGIN, "writing-specs.md")

sys.dont_write_bytecode = True  # no __pycache__ inside the plugin
sys.path.insert(0, os.path.dirname(SCRIPT))
import check_writing  # noqa: E402


def git(cwd, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t",
               GIT_CONFIG_NOSYSTEM="1", HOME=cwd)
    subprocess.run(["git", "-c", "protocol.file.allow=always"] + list(args), cwd=cwd, env=env, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = os.path.realpath(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        # A copy of the plugin: check_writing.py and the guideline two folders above it (AUD-15).
        self.plugin = os.path.join(self.tmp, "plugin")
        os.makedirs(os.path.join(self.plugin, "use-cases", "check-writing"))
        self.script = os.path.join(self.plugin, "use-cases", "check-writing", "check_writing.py")
        shutil.copy(SCRIPT, self.script)
        # AUD-54: the shared scripts of the plugin, mdlinks.py and layers.py among them.
        shutil.copytree(os.path.join(PLUGIN, "scripts"), os.path.join(self.plugin, "scripts"),
                        ignore=shutil.ignore_patterns("__pycache__"))
        self.guideline = os.path.join(self.plugin, "writing-specs.md")
        shutil.copy(GUIDELINE, self.guideline)
        self.repo = os.path.join(self.tmp, "repo")
        os.makedirs(self.repo)
        git(self.repo, "init", "-q")

    def write(self, rel, content, base=None):
        path = os.path.join(base or self.repo, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(content if isinstance(content, bytes) else content.encode("utf-8"))
        return path

    def run_script(self, *args, stdin=b"", cwd=None, env=None):
        if args[:1] == ("render",) and stdin:
            # render needs prepare's two fields of the links between layers (AUD-56, AUD-59); a test of
            # another requirement gives the check as done, with nothing to report, unless it sets them.
            try:
                data = json.loads(stdin)
            except ValueError:
                data = None
            if isinstance(data, dict):
                data.setdefault("link_reports", [])
                data.setdefault("links_not_checked", None)
                stdin = json.dumps(data).encode()
        proc = subprocess.run([sys.executable, self.script] + list(args), cwd=cwd or self.repo, input=stdin,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        return proc.returncode, proc.stdout.decode("utf-8", "surrogateescape"), proc.stderr.decode()

    def prepare(self, *args, cwd=None, env=None):
        status, out, err = self.run_script("prepare", *args, cwd=cwd, env=env)
        if status == 0:
            return status, json.loads(out)
        return status, out

    def json_cmd(self, command, data):
        status, out, err = self.run_script(command, stdin=json.dumps(data).encode())
        self.assertEqual(status, 0, err)
        return json.loads(out) if command == "filter" else out


class SplitWords(unittest.TestCase):
    """AUD-11: POSIX quoting (2.2), token recognition (2.3) and quote removal (2.6.7)."""

    def test_blanks_and_quotes(self):
        """AUD-11: blanks split; single and double quotes keep blanks and are removed."""
        self.assertEqual(check_writing.split_words(""), [])
        self.assertEqual(check_writing.split_words("  specs/a.md  "), ["specs/a.md"])
        self.assertEqual(check_writing.split_words("'my specs/a b.md'"), ["my specs/a b.md"])
        self.assertEqual(check_writing.split_words('"my specs"/x.md'), ["my specs/x.md"])
        self.assertEqual(check_writing.split_words("a b"), ["a", "b"])
        self.assertEqual(check_writing.split_words("''"), [""])

    def test_backslash(self):
        """AUD-11: an unquoted backslash keeps the next character; in double quotes only before $ ` \" \\ newline."""
        self.assertEqual(check_writing.split_words(r"my\ specs"), ["my specs"])
        self.assertEqual(check_writing.split_words(r'"a\"b\x"'), ['a"b\\x'])
        self.assertEqual(check_writing.split_words("a\\\nb"), ["ab"])
        self.assertEqual(check_writing.split_words(r"'a\b'"), [r"a\b"])

    def test_operators_and_comments(self):
        """AUD-11: operators are tokens of their own; `#` starts a comment only at the start of a word."""
        self.assertEqual(check_writing.split_words("a>b"), ["a", ">", "b"])
        self.assertEqual(check_writing.split_words("a&&b"), ["a", "&&", "b"])
        self.assertEqual(check_writing.split_words("a#b # c d"), ["a#b"])
        self.assertEqual(check_writing.split_words("'$HOME' $x"), ["$HOME", "$x"])

    def test_substitutions_are_one_token(self):
        """AUD-11, 2.3 rule 5: a backquote, `$(` or `${` runs to its matching end inside one word, verbatim."""
        self.assertEqual(check_writing.split_words("`specs/my file.md`"), ["`specs/my file.md`"])
        self.assertEqual(check_writing.split_words("a$(b c)"), ["a$(b c)"])
        self.assertEqual(check_writing.split_words("${x y} z"), ["${x y}", "z"])
        self.assertEqual(check_writing.split_words("a$(b ')' $(c d)) e"), ["a$(b ')' $(c d))", "e"])
        self.assertEqual(check_writing.split_words('"x$(a "b c")y"'), ['x$(a "b c")y'])
        self.assertEqual(check_writing.split_words("`a b"), ["`a b"])


class Refusals(Base):
    """AUD-40: the conditions, in order, each with its message byte for byte."""

    def test_more_than_one_argument(self):
        """AUD-40: more than one argument, tested first, before the guideline."""
        os.remove(self.guideline)
        self.assertEqual(self.prepare("a", "b"), (1, "specs-management:check-writing: expected at most one path, got 2 arguments\n"))
        self.assertEqual(self.prepare("--raw", "a 'b c' d"),
                         (1, "specs-management:check-writing: expected at most one path, got 3 arguments\n"))

    def test_guideline_missing(self):
        """AUD-40, AUD-15: the guideline missing, tested before the path."""
        os.remove(self.guideline)
        self.assertEqual(self.prepare("nope.md"), (1, "specs-management:check-writing: writing-specs.md is missing from the plugin specs-management\n"))

    def test_guideline_unreadable(self):
        """AUD-40: a guideline that cannot be read (a folder at its path)."""
        os.remove(self.guideline)
        os.makedirs(self.guideline)
        self.assertEqual(self.prepare(), (1, "specs-management:check-writing: writing-specs.md is missing from the plugin specs-management\n"))

    def test_no_such_path(self):
        """AUD-40: the path does not exist; <path> is the argument after quote removal."""
        self.assertEqual(self.prepare("--raw", "'no such.md'"), (1, "specs-management:check-writing: no such.md: no such file or folder\n"))
        self.assertEqual(self.prepare(""), (1, "specs-management:check-writing: : no such file or folder\n"))

    def test_not_inside_git(self):
        """AUD-40: the path is not inside a git repository."""
        outside = os.path.join(self.tmp, "outside")
        self.write("a.md", "# A\n", base=outside)
        self.assertEqual(self.prepare(os.path.join(outside, "a.md")),
                         (1, "specs-management:check-writing: %s: not inside a git repository\n" % os.path.join(outside, "a.md")))
        self.assertEqual(self.prepare(cwd=outside), (1, "specs-management:check-writing: %s: not inside a git repository\n" % outside))

    def test_git_fails(self):
        """AUD-40, AUD-53: a git that fails gives the first line of its error output."""
        fake = os.path.join(self.tmp, "bin")
        os.makedirs(fake)
        self.write("git", "#!/bin/sh\necho 'fatal: something broke' >&2\necho 'second line' >&2\nexit 128\n", base=fake)
        os.chmod(os.path.join(fake, "git"), 0o755)
        env = dict(os.environ, PATH=fake)
        self.write("a.md", "# A\n")
        self.assertEqual(self.prepare(env=env), (1, "specs-management:check-writing: git failed: fatal: something broke\n"))

    def test_git_cannot_start(self):
        """AUD-40, AUD-53: git that cannot be started."""
        empty = os.path.join(self.tmp, "empty")
        os.makedirs(empty)
        self.assertEqual(self.prepare(env=dict(os.environ, PATH=empty)),
                         (1, "specs-management:check-writing: git failed: git could not be started\n"))

    def test_no_spec_file(self):
        """AUD-40, AUD-13: the argument selects no spec file; without argument <path> is the working directory."""
        self.write("notes.txt", "x\n")
        self.write("CLAUDE.md", "# agents\n")
        self.write("docs/x.txt", "x\n")
        self.assertEqual(self.prepare(), (1, "specs-management:check-writing: %s: no spec file found\n" % self.repo))
        self.assertEqual(self.prepare("CLAUDE.md"), (1, "specs-management:check-writing: CLAUDE.md: no spec file found\n"))
        self.assertEqual(self.prepare("docs"), (1, "specs-management:check-writing: docs: no spec file found\n"))
        self.assertEqual(self.prepare("notes.txt"), (1, "specs-management:check-writing: notes.txt: no spec file found\n"))

    def test_inside_git_directory(self):
        """AUD-11, AUD-13, AUD-40: a path inside the git directory selects no spec file; git does not fail."""
        self.write("a.md", "# a\n")
        git(self.repo, "add", "a.md")
        git(self.repo, "commit", "-q", "-m", "x")
        self.assertEqual(self.prepare(".git"), (1, "specs-management:check-writing: .git: no spec file found\n"))
        self.assertEqual(self.prepare(".git/HEAD"), (1, "specs-management:check-writing: .git/HEAD: no spec file found\n"))
        self.assertEqual(self.prepare(".git/objects"), (1, "specs-management:check-writing: .git/objects: no spec file found\n"))
        self.assertEqual(self.prepare("refs", cwd=os.path.join(self.repo, ".git")),
                         (1, "specs-management:check-writing: refs: no spec file found\n"))

    def test_backquoted_path(self):
        """AUD-11, AUD-40: a path in Markdown backquotes is one argument (2.3 rule 5), so the message is about the path."""
        self.assertEqual(self.prepare("--raw", "`specs/my file.md`"),
                         (1, "specs-management:check-writing: `specs/my file.md`: no such file or folder\n"))

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root searches every folder")
    def test_folder_that_cannot_be_searched(self):
        """AUD-40, AUD-42: a path in a folder that cannot be searched exists, and git runs; its file cannot be read."""
        self.write("a.md", "# a\n")
        self.write("locked/l.md", "# l\n")
        git(self.repo, "add", "-A")
        locked = os.path.join(self.repo, "locked")
        os.chmod(locked, 0)
        self.addCleanup(os.chmod, locked, stat.S_IRWXU)
        for arg in ("locked", "locked/l.md"):
            status, out = self.prepare(arg)
            self.assertEqual(status, 0, out)
            self.assertEqual((out["selected"], out["unreadable"]), (["locked/l.md"], ["locked/l.md"]))

    def test_inside_linked_worktree_and_module_git_directories(self):
        """AUD-11, AUD-13, AUD-40: .git/worktrees/<name> and .git/modules/<name> are inside the outer repository."""
        src = os.path.join(self.tmp, "src")
        os.makedirs(src)
        git(src, "init", "-q")
        self.write("inner.md", "# inner\n", base=src)
        git(src, "add", "-A")
        git(src, "commit", "-q", "-m", "x")
        self.write("outer.md", "# outer\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "x")
        git(self.repo, "submodule", "add", "-q", src, "mod")
        git(self.repo, "worktree", "add", "-q", os.path.join(self.tmp, "wt"))
        self.assertEqual(self.prepare(".git/worktrees/wt"), (1, "specs-management:check-writing: .git/worktrees/wt: no spec file found\n"))
        # Without argument, from inside those git directories: the outer repository, all its spec files (AUD-13).
        for cwd in (os.path.join(self.repo, ".git", "worktrees", "wt"), os.path.join(self.repo, ".git", "modules", "mod")):
            status, out = self.prepare(cwd=cwd)
            self.assertEqual((status, out["repo_root"], out["spec_files"]), (0, self.repo, ["outer.md"]), cwd)
        self.assertEqual(self.prepare(".git/modules/mod"), (1, "specs-management:check-writing: .git/modules/mod: no spec file found\n"))

    def test_hard_link_to_spec_file(self):
        """AUD-13: an ignored or R62-excluded name hard-linked to a spec file selects no file."""
        self.write("b.md", "# b\n")
        self.write(".gitignore", "ign/\n")
        os.makedirs(os.path.join(self.repo, "ign"))
        os.link(os.path.join(self.repo, "b.md"), os.path.join(self.repo, "ign", "c.md"))
        os.link(os.path.join(self.repo, "b.md"), os.path.join(self.repo, "CLAUDE.md"))
        self.assertEqual(self.prepare("ign/c.md"), (1, "specs-management:check-writing: ign/c.md: no spec file found\n"))
        self.assertEqual(self.prepare("CLAUDE.md"), (1, "specs-management:check-writing: CLAUDE.md: no spec file found\n"))
        self.assertEqual(self.prepare("b.md")[1]["selected"], ["b.md"])


class SpecFiles(Base):
    """AUD-12, AUD-13 and the outputs of prepare."""

    def test_selection_example(self):
        """AUD-E3: the spec files are README.md, docs/LICENSE.md and specs/a.md; session mode."""
        for rel in ("README.md", "CLAUDE.md", ".github/notes.md", "docs/LICENSE.md", "LICENSE.md", "specs/a.md"):
            self.write(rel, "# %s\n" % rel)
        self.write("specs/logo.png", b"\x89PNG")
        status, out = self.prepare()
        self.assertEqual(status, 0)
        self.assertEqual(out["spec_files"], ["README.md", "docs/LICENSE.md", "specs/a.md"])
        self.assertEqual(out["selected"], out["spec_files"])
        self.assertEqual((out["n"], out["s"], out["mode"]), (3, 3, "session"))
        self.assertEqual(out["repo_root"], self.repo)
        self.assertEqual(out["unreadable"], [])

    def test_conditions(self):
        """AUD-12: uncommitted files count; ignored, deleted, symbolic links, other names, R62 paths and the guideline's bytes do not."""
        self.write("committed.md", "# c\n")
        self.write("gone.md", "# g\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "x")
        os.remove(os.path.join(self.repo, "gone.md"))
        self.write("committed.md", "# changed\n")
        self.write("untracked.md", "# u\n")
        self.write(".gitignore", "ignored.md\nbuild/\n")
        self.write("ignored.md", "# i\n")
        self.write("build/out.md", "# b\n")
        os.symlink("committed.md", os.path.join(self.repo, "link.md"))
        self.write("upper.MD", "# upper\n")
        self.write("sub/claude.md", "# agents\n")
        self.write("sub/AGENTS.md", "# agents\n")
        self.write("License.MD", "# l\n")
        self.write("security.md", "# s\n")
        self.write("x/.hidden/a.md", "# h\n")
        with open(self.guideline, "rb") as f:
            self.write("copy-of-guideline.md", f.read())
        self.write("sub/CHANGELOG.md", "# kept: only the root's is excluded\n")
        status, out = self.prepare()
        self.assertEqual(status, 0)
        self.assertEqual(out["spec_files"], ["committed.md", "sub/CHANGELOG.md", "untracked.md"])

    def test_folder_replaced_by_symbolic_link(self):
        """AUD-12, AUD-38: a tracked docs/a.md whose folder docs is now a link to a folder outside is not in the working tree."""
        self.write("docs/a.md", "# a\n")
        self.write("b.md", "# b\n")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "x")
        outside = os.path.join(self.tmp, "outside")
        self.write("a.md", "# outside, never read\n", base=outside)
        shutil.rmtree(os.path.join(self.repo, "docs"))
        os.symlink(outside, os.path.join(self.repo, "docs"))
        _, out = self.prepare()
        self.assertEqual(out["spec_files"], ["b.md"])
        self.assertEqual(out["word_counts"], {"b.md": 1})
        self.assertEqual(self.prepare(os.path.join("docs", "a.md")),
                         (1, "specs-management:check-writing: %s: not inside a git repository\n" % os.path.join("docs", "a.md")))

    def test_case_insensitive_name(self):
        """AUD-13: on a case-insensitive file system, another spelling of a spec file's path selects it."""
        self.write("specs/a.md", "# a\n")
        if not os.path.exists(os.path.join(self.repo, "SPECS", "A.md")):
            self.skipTest("case-sensitive file system")
        self.assertEqual(self.prepare("SPECS/A.md")[1]["selected"], ["specs/a.md"])

    def test_tracked_file_that_matches_ignore(self):
        """AUD-12: git does not ignore a tracked file, even when a pattern matches it."""
        self.write("a.md", "# a\n")
        git(self.repo, "add", "a.md")
        self.write(".gitignore", "*.md\n")
        self.write("b.md", "# b\n")
        self.assertEqual(self.prepare()[1]["spec_files"], ["a.md"])

    def test_code_point_order(self):
        """AUD-34, AUD-12: spec files in code point order of path."""
        for rel in ("b.md", "Z.md", "a/z.md", "a.md", "é.md"):
            self.write(rel, "# x %s\n" % rel)
        self.assertEqual(self.prepare()[1]["spec_files"], ["Z.md", "a.md", "a/z.md", "b.md", "é.md"])

    def test_selection(self):
        """AUD-13: the root or no argument selects all; a folder selects the files under it; a file itself."""
        for rel in ("README.md", "specs/a.md", "specs/b.md", "specs/deep/c.md", "specsx/d.md"):
            self.write(rel, "# %s\n" % rel)
        everything = ["README.md", "specs/a.md", "specs/b.md", "specs/deep/c.md", "specsx/d.md"]
        self.assertEqual(self.prepare()[1]["selected"], everything)
        self.assertEqual(self.prepare(self.repo)[1]["selected"], everything)
        self.assertEqual(self.prepare(".")[1]["selected"], everything)
        _, out = self.prepare("specs")
        self.assertEqual(out["selected"], ["specs/a.md", "specs/b.md", "specs/deep/c.md"])
        self.assertEqual((out["n"], out["s"], out["mode"]), (5, 3, "workflow"))
        self.assertEqual(self.prepare("a.md", cwd=os.path.join(self.repo, "specs"))[1]["selected"], ["specs/a.md"])
        self.assertEqual(self.prepare("specs/deep/")[1]["selected"], ["specs/deep/c.md"])
        # Without argument from a subfolder: the whole repository.
        self.assertEqual(self.prepare(cwd=os.path.join(self.repo, "specs"))[1]["selected"], everything)

    def test_threshold(self):
        """AUD-E1, AUD-23, AUD-24: 3 spec files is session mode; 4 is workflow mode with 4 selected files."""
        for i in range(3):
            self.write("s%d.md" % i, "# %d\n" % i)
        self.assertEqual(self.prepare()[1]["mode"], "session")
        self.write("s3.md", "# 3\n")
        _, out = self.prepare()
        self.assertEqual((out["mode"], out["n"], len(out["selected"])), ("workflow", 4, 4))
        # AUD-24: the threshold counts spec files, not selected files.
        self.assertEqual(self.prepare("s0.md")[1]["mode"], "workflow")

    def test_symbolic_link_argument_resolved(self):
        """AUD-11, AUD-13: the argument's symbolic links are resolved, so its repository is the target's."""
        other = os.path.join(self.tmp, "other")
        os.makedirs(other)
        git(other, "init", "-q")
        self.write("specs/t.md", "# t\n", base=other)
        self.write("mine.md", "# m\n")
        os.symlink(os.path.join(other, "specs"), os.path.join(self.repo, "ext"))
        _, out = self.prepare("ext")
        self.assertEqual(out["repo_root"], other)
        self.assertEqual(out["selected"], ["specs/t.md"])

    def test_submodule_is_innermost(self):
        """AUD-11: inside a submodule, the repository is the submodule."""
        src = os.path.join(self.tmp, "src")
        os.makedirs(src)
        git(src, "init", "-q")
        self.write("inner.md", "# inner\n", base=src)
        git(src, "add", "-A")
        git(src, "commit", "-q", "-m", "x")
        self.write("outer.md", "# outer\n")
        git(self.repo, "submodule", "add", "-q", src, "mod")
        _, out = self.prepare()
        self.assertEqual(out["spec_files"], ["outer.md"])  # the submodule's files are not the parent's
        _, out = self.prepare("mod")
        self.assertEqual(out["repo_root"], os.path.join(self.repo, "mod"))
        self.assertEqual(out["spec_files"], ["inner.md"])

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root reads every file")
    def test_unreadable(self):
        """AUD-42: a spec file that cannot be read is listed as unreadable; it still counts in n."""
        self.write("a.md", "# a\n")
        path = self.write("b.md", "# b\n")
        os.chmod(path, 0)
        self.addCleanup(os.chmod, path, stat.S_IRUSR | stat.S_IWUSR)
        _, out = self.prepare()
        self.assertEqual((out["spec_files"], out["unreadable"], out["n"]), (["a.md", "b.md"], ["b.md"], 2))
        self.assertNotIn("b.md", out["word_counts"])

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root searches every folder")
    def test_unreadable_in_folder_that_cannot_be_searched(self):
        """AUD-12, AUD-42, AUD-24: a tracked spec file whose folder cannot be searched is in the working
        tree: it is listed as unreadable and counts in n, never dropped from the spec set."""
        self.write("a.md", "# a\n")
        self.write("locked/l.md", "# l\n")
        self.write("locked/deeper/m.md", "# m\n")
        git(self.repo, "add", "-A")
        locked = os.path.join(self.repo, "locked")
        os.chmod(locked, 0)
        self.addCleanup(os.chmod, locked, stat.S_IRWXU)
        _, out = self.prepare()
        self.assertEqual((out["spec_files"], out["unreadable"], out["n"]),
                         (["a.md", "locked/deeper/m.md", "locked/l.md"], ["locked/deeper/m.md", "locked/l.md"], 3))

    def test_words_code_spans_per_paragraph(self):
        """AUD-36: a code span cannot cross a blank line, and an escaped backtick opens none."""
        self.assertEqual(check_writing.count_words(
            b"Use the ` key to quote.\n\nLas reglas del sistema de reservas se aplican a todos los clientes y "
            b"empleados del hotel.\n\nRun `x` now.\n"), 23)
        self.assertEqual(check_writing.count_words(b"\\`not code` real words here`\n"), 2)
        self.assertEqual(check_writing.count_words(b"One `two\nthree` four ``five ` six`` seven\n"), 3)

    def test_guideline_path_and_words(self):
        """AUD-15: the guideline is writing-specs.md at the plugin root; AUD-36: words outside code spans and literal blocks."""
        self.write("a.md", "# Título uno\n\nDos `tres cuatro` cinco.\n\n```\nnot counted here\n```\n\n~~~~\nnor\n~~~~\nseis\n"
                   # An indented code block, a blank line inside it, a tab-indented line: not counted.
                   "\n    indented code skipped\n\n    still code\n\tand this\n"
                   # A paragraph's indented continuation line, and a list item's indented paragraph: counted.
                   "siete\n    ocho\n\n- nueve\n\n    diez\n")
        _, out = self.prepare()
        self.assertEqual(out["guideline"], self.guideline)
        self.assertEqual(out["word_counts"], {"a.md": 9})

    def test_writes_nothing(self):
        """AUD-5, AUD-41: prepare changes no file of the repository, git's data included."""
        self.write("a.md", "# a\n")
        git(self.repo, "add", "a.md")
        git(self.repo, "commit", "-q", "-m", "x")
        self.write("a.md", "# a changed\n")
        self.write("new.md", "# n\n")

        def snapshot():
            seen = {}
            for base, dirs, files in os.walk(self.repo):
                for name in dirs + files:
                    p = os.path.join(base, name)
                    st = os.lstat(p)
                    data = None
                    if stat.S_ISREG(st.st_mode):
                        with open(p, "rb") as f:
                            data = f.read()
                    seen[p] = (st.st_mtime_ns, data)
            return seen

        before = snapshot()
        self.prepare()
        self.prepare("a.md")
        self.assertEqual(before, snapshot())

    def test_raw_stdin(self):
        """AUD-11: the words may also come on stdin."""
        self.write("my specs/a b.md", "# a\n")
        status, out, _ = self.run_script("prepare", "--raw-stdin", stdin=b"'my specs/a b.md'\n")
        self.assertEqual(status, 0)
        self.assertEqual(json.loads(out)["selected"], ["my specs/a b.md"])


class Filter(Base):
    """AUD-29 steps 2 and 3, the terms Line and Quote, and AUD-19."""

    def finding(self, path, line, rule, quote, **extra):
        f = {"path": path, "line": line, "rule": rule, "quote": quote, "problem": "p", "rewrite": "r", "see_also": []}
        f.update(extra)
        return f

    def setUp(self):
        super().setUp()
        lines = ["# Shipping"] + ["line %d" % i for i in range(2, 12)] + ["Large orders get free shipping, etc."]
        self.write("specs/shipping.md", "\n".join(lines) + "\n")
        self.write("specs/crlf.md", b"# T\r\n- Large orders get free shipping,\r\n  etc.\r\nlast\r")
        self.write("specs/other.md", "# Other\n")

    SPEC_FILES = ["specs/a.md", "specs/b.md", "specs/c.md", "specs/crlf.md", "specs/other.md", "specs/shipping.md"]

    def run_filter(self, findings, selected=("specs/shipping.md", "specs/crlf.md"), **extra):
        data = {"repo_root": self.repo, "selected": list(selected), "spec_files": self.SPEC_FILES, "findings": findings}
        data.update(extra)
        return self.json_cmd("filter", data)

    def test_kept(self):
        """AUD-E4, AUD-29: a finding whose path, line, quote and rule hold is kept."""
        out = self.run_filter([self.finding("specs/shipping.md", 12, "WSP-2", ["Large orders get free shipping, etc."])])
        self.assertEqual(len(out["findings"]), 1)
        self.assertEqual(out["dropped"], [])

    def test_drops(self):
        """AUD-29 step 2: path not selected, line missing, quote different, rule not binding."""
        q = ["Large orders get free shipping, etc."]
        cases = [
            (self.finding("specs/other.md", 1, "WSP-2", ["# Other"]), "path is not a selected file"),
            (self.finding("specs/shipping.md", 13, "WSP-2", [""]), "line does not exist"),
            (self.finding("specs/shipping.md", 0, "WSP-2", q), "line does not exist"),
            (self.finding("specs/shipping.md", 11, "WSP-2", q), "quote differs from the file"),
            (self.finding("specs/shipping.md", 12, "WSP-2", ["Large orders get free shipping, etc. "]), "quote differs from the file"),
            (self.finding("specs/shipping.md", 12, "WSP-2", q + ["more"]), "quote differs from the file"),
            (self.finding("specs/shipping.md", 12, "WSP-2", []), "quote differs from the file"),
            (self.finding("specs/shipping.md", 12, "WSP-21", q), "rule is not a binding rule"),
            (self.finding("specs/shipping.md", 12, "WSP-Q2", q), "rule is not a binding rule"),
            (self.finding("specs/shipping.md", 12, "WSP-T1", q), "rule is not a binding rule"),
            (self.finding("specs/shipping.md", 12, "spc-2", q), "rule is not a binding rule"),
        ]
        out = self.run_filter([c[0] for c in cases])
        self.assertEqual(out["findings"], [])
        self.assertEqual([d["reason"] for d in out["dropped"]], [c[1] for c in cases])

    def test_every_binding_rule_kept(self):
        """Term "Binding rule": WSP-1 to WSP-20 and WSP-T4, WSP-T5, WSP-T11, WSP-T14, WSP-T15 (complete list)."""
        rules = ["WSP-%d" % i for i in range(1, 21)] + ["WSP-T4", "WSP-T5", "WSP-T11", "WSP-T14", "WSP-T15"]
        out = self.run_filter([self.finding("specs/shipping.md", 1, r, ["# Shipping"]) for r in rules])
        self.assertEqual([f["rule"] for f in out["findings"]], rules)

    def test_line_term(self):
        """Term "Line", AUD-E11: CR before LF is not part of a line; a last line without LF is a line.
        Term "Quote", AUD-29 step 2: a quote line matches with or without the line's other CRs."""
        out = self.run_filter([
            self.finding("specs/crlf.md", 2, "WSP-2", ["- Large orders get free shipping,", "  etc."]),
            self.finding("specs/crlf.md", 4, "WSP-2", ["last\r"]),
            self.finding("specs/crlf.md", 4, "WSP-4", ["last"]),
            self.finding("specs/crlf.md", 4, "WSP-5", ["lost"]),
            self.finding("specs/crlf.md", 5, "WSP-2", [""]),
        ])
        self.assertEqual([(f["line"], f["rule"]) for f in out["findings"]], [(2, "WSP-2"), (4, "WSP-2"), (4, "WSP-4")])
        self.assertEqual([d["reason"] for d in out["dropped"]], ["quote differs from the file", "line does not exist"])

    def test_merge(self):
        """AUD-29 step 3: same path, line, rule, See also places and problem merge into the first one given."""
        self.write("specs/a.md", "x\n" * 10)
        q = ["Large orders get free shipping, etc."]
        out = self.run_filter([
            self.finding("specs/shipping.md", 12, "WSP-2", q, problem="first", see_also=["specs/a.md:10", "specs/a.md:2"]),
            self.finding("specs/shipping.md", 12, "WSP-3", q),
            self.finding("specs/shipping.md", 12, "WSP-2", q, problem="first", rewrite="other",
                         see_also=["specs/a.md:2", "specs/a.md:10"]),
            self.finding("specs/shipping.md", 12, "WSP-3", q, rewrite="again"),
        ])
        self.assertEqual([(f["rule"], f["problem"], f["rewrite"]) for f in out["findings"]],
                         [("WSP-2", "first", "r"), ("WSP-3", "p", "r")])
        # AUD-20 (round 5, defect 14): a finding of one file has no See also places.
        self.assertEqual(out["findings"][0]["see_also"], [])

    def test_merge_keeps_distinct_findings_across_files(self):
        """AUD-29 step 3, AUD-19: two findings at one place and rule with different See also
        places are distinct defects; neither problem nor rewrite is lost."""
        self.write("specs/a.md", "# Terms\n| Member | a person with a card; Card: a paid pass |\n")
        self.write("specs/b.md", "A user borrows.\nA pass is needed.\n")
        member = {"path": "specs/a.md", "line": 2, "quote": ["| Member | a person with a card; Card: a paid pass |"],
                  "rewrite": "r"}
        out = self.run_filter([
            {"rule": "WSP-3", "problem": "Member is called user in b.md.",
             "involved": [member, {"path": "specs/b.md", "line": 1, "quote": ["A user borrows."], "rewrite": "r"}]},
            {"rule": "WSP-3", "problem": "Card is called pass in b.md.",
             "involved": [member, {"path": "specs/b.md", "line": 2, "quote": ["A pass is needed."], "rewrite": "r"}]},
        ], selected=["specs/a.md", "specs/b.md"])
        self.assertEqual([(f["problem"], f["see_also"]) for f in out["findings"]],
                         [("Member is called user in b.md.", ["specs/b.md:1"]), ("Card is called pass in b.md.", ["specs/b.md:2"])])

    def test_across_files(self):
        """AUD-19, AUD-E9: under the first selected file at its first involved line; the other places in See also."""
        self.write("specs/a.md", "1\n2\n3\nMember: a person with a card.\n5\n6\nAnother member line.\n")
        self.write("specs/b.md", "1\n2\n3\n4\n5\n6\n7\n8\nA user borrows.\n")
        self.write("specs/c.md", "1\nThe user returns.\n")
        involved = [
            {"path": "specs/c.md", "line": 2, "quote": ["The user returns."], "rewrite": "r"},
            {"path": "specs/b.md", "line": 9, "quote": ["A user borrows."], "rewrite": "r"},
            {"path": "specs/a.md", "line": 7, "quote": ["Another member line."], "rewrite": "r"},
            {"path": "specs/a.md", "line": 4, "quote": ["Member: a person with a card."], "rewrite": "r"},
        ]
        f = {"rule": "WSP-3", "involved": involved, "problem": "p"}
        out = self.run_filter([f], selected=["specs/a.md"])
        self.assertEqual(len(out["findings"]), 1)
        got = out["findings"][0]
        self.assertEqual((got["path"], got["line"], got["quote"]), ("specs/a.md", 4, ["Member: a person with a card."]))
        self.assertEqual(got["see_also"], ["specs/a.md:7", "specs/b.md:9", "specs/c.md:2"])
        # No involved line in a selected file: not reported.
        out = self.run_filter([f], selected=["specs/other.md"])
        self.assertEqual((out["findings"], out["dropped"][0]["reason"]),
                         ([], "no involved line is in a selected file that was checked"))

    def test_across_files_checked_only(self):
        """AUD-19, AUD-35: a finding across files goes to the first selected file that was checked."""
        self.write("specs/a.md", "Member: a person with a card.\n")
        self.write("specs/b.md", "A user borrows.\n")
        f = {"rule": "WSP-3", "problem": "p", "involved": [
            {"path": "specs/a.md", "line": 1, "quote": ["Member: a person with a card."], "rewrite": "r"},
            {"path": "specs/b.md", "line": 1, "quote": ["A user borrows."], "rewrite": "r"}]}
        out = self.run_filter([f], selected=["specs/a.md", "specs/b.md"], checked=["specs/b.md"])
        got = out["findings"][0]
        self.assertEqual((got["path"], got["line"], got["see_also"]), ("specs/b.md", 1, ["specs/a.md:1"]))
        out = self.run_filter([f], selected=["specs/a.md", "specs/b.md"], checked=[])
        self.assertEqual(out["findings"], [])
        # A finding of a single file on a file that was not checked is dropped too.
        out = self.json_cmd("filter", {"repo_root": self.repo, "selected": ["specs/a.md"], "checked": [],
                                       "findings": [self.finding("specs/a.md", 1, "WSP-2", ["Member: a person with a card."])]})
        self.assertEqual(out["dropped"][0]["reason"], "file was not checked")

    def test_types_refused(self):
        """SKILL.md section 3: quote a list of strings, rewrite one string, see_also "path:line" strings; else exit 2."""
        q = ["Large orders get free shipping, etc."]
        cases = [
            (self.finding("specs/shipping.md", 12, "WSP-2", "Large orders get free shipping, etc."), "'quote' must be"),
            (self.finding("specs/shipping.md", 12, "WSP-2", q, rewrite=["One.", "Two."]), "'rewrite' must be"),
            (self.finding("specs/shipping.md", 12, "WSP-2", q, see_also="specs/a.md:2"), "'see_also' must be"),
            (self.finding("specs/shipping.md", 12, "WSP-2", q, see_also=["specs/a.md"]), "'see_also' must be"),
            (self.finding("specs/shipping.md", 12, "WSP-2", q, see_also=[{"path": "a.md", "line": 2}]), "'see_also' must be"),
            (self.finding("specs/shipping.md", "12", "WSP-2", q), "'line' must be"),
            ({"path": "specs/shipping.md", "line": 12, "rule": "WSP-2", "quote": q, "problem": "p"}, "'rewrite' is missing"),
            ({"rule": "WSP-3", "problem": "p", "involved": ["specs/shipping.md:12"]}, "each place of"),
            ({"rule": "WSP-3", "problem": "p", "involved": [{"path": "specs/shipping.md", "line": 12, "quote": q}]},
             "each place of"),
            ({"rule": "WSP-3", "problem": "p", "path": "specs/shipping.md",
              "involved": [{"path": "specs/shipping.md", "line": 12, "quote": q, "rewrite": "r"}]}, "not both"),
            ({"rule": "WSP-3", "problem": "p", "see_also": [],
              "involved": [{"path": "specs/shipping.md", "line": 12, "quote": q, "rewrite": "r"}]}, "not both"),
            ({"rule": "WSP-3", "problem": "p", "rewrite": "r",
              "involved": [{"path": "specs/shipping.md", "line": 12, "quote": q, "rewrite": "r"}]}, "not both"),
        ]
        for finding, message in cases:
            data = {"repo_root": self.repo, "selected": ["specs/shipping.md"], "spec_files": self.SPEC_FILES,
                    "findings": [self.finding("specs/shipping.md", 12, "WSP-2", q), finding]}
            status, out, err = self.run_script("filter", stdin=json.dumps(data).encode())
            self.assertEqual((status, out), (2, ""), finding)
            self.assertIn("finding 2", err)
            self.assertIn(message, err)

    def test_non_utf8_bytes(self):
        """Term "Quote": byte for byte, also for bytes that are not UTF-8 (passed as surrogate escapes)."""
        self.write("specs/latin.md", b"caf\xe9\n")
        quote = [b"caf\xe9".decode("utf-8", "surrogateescape")]
        data = json.dumps({"repo_root": self.repo, "selected": ["specs/latin.md"],
                           "findings": [self.finding("specs/latin.md", 1, "WSP-2", quote)]})
        status, out, err = self.run_script("filter", stdin=data.encode())
        self.assertEqual((status, len(json.loads(out)["findings"])), (0, 1), err)

    def test_literal_tab_in_json(self):
        """AUD-29, AUD-46: a tab copied raw into a JSON string (a heredoc, SKILL.md section 1) is accepted, not refused as non-JSON."""
        self.write("specs/tabs.md", "# Tabs\n\t- nested etc.\n")
        raw = ('{"repo_root": %s, "selected": ["specs/tabs.md"], "findings": [{"path": "specs/tabs.md", "line": 2, '
               '"rule": "WSP-2", "quote": ["\t- nested etc."], "problem": "p", "rewrite": "r"}]}' % json.dumps(self.repo))
        self.assertIn("\t", raw)
        status, out, err = self.run_script("filter", stdin=raw.encode())
        self.assertEqual(status, 0, err)
        self.assertEqual(json.loads(out)["findings"][0]["quote"], ["\t- nested etc."])

    def test_empty_file_has_line_1(self):
        """Term "Line", AUD-21: a file with no bytes has one empty line 1, so a finding on it is kept."""
        self.write("specs/empty.md", b"")
        out = self.run_filter([self.finding("specs/empty.md", 1, "WSP-1", [""]),
                               self.finding("specs/empty.md", 2, "WSP-1", [""])], selected=["specs/empty.md"])
        self.assertEqual([f["line"] for f in out["findings"]], [1])
        self.assertEqual(out["dropped"][0]["reason"], "line does not exist")

    def test_quote_as_the_read_tool_shows_it(self):
        """Term "Line", term "Quote", AUD-E6: a leading UTF-8 BOM is not part of line 1; a lone CR is left out;
        a byte that is not UTF-8 is read as U+FFFD. The raw bytes still match."""
        self.write("specs/booking.md", b"\xef\xbb\xbf# Booking\r\nfirst\n")
        self.write("specs/cr.md", b"# Title\rfirst etc.\rsecond\n")
        self.write("specs/latin.md", b"caf\xe9 must be fast.\n")
        sel = ["specs/booking.md", "specs/cr.md", "specs/latin.md"]
        out = self.run_filter([
            self.finding("specs/booking.md", 1, "WSP-1", ["# Booking"]),
            self.finding("specs/booking.md", 1, "WSP-2", ["\ufeff# Booking"]),
            self.finding("specs/cr.md", 1, "WSP-2", ["# Titlefirst etc.second"]),
            self.finding("specs/cr.md", 1, "WSP-4", ["# Title\rfirst etc.\rsecond"]),
            self.finding("specs/latin.md", 1, "WSP-2", ["caf\ufffd must be fast."]),
            self.finding("specs/latin.md", 1, "WSP-4", [b"caf\xe9 must be fast.".decode("utf-8", "surrogateescape")]),
            self.finding("specs/latin.md", 1, "WSP-5", ["cafe must be fast."]),
        ], selected=sel)
        self.assertEqual([(f["path"], f["rule"]) for f in out["findings"]], [
            ("specs/booking.md", "WSP-1"), ("specs/booking.md", "WSP-2"), ("specs/cr.md", "WSP-2"), ("specs/cr.md", "WSP-4"),
            ("specs/latin.md", "WSP-2"), ("specs/latin.md", "WSP-4")])
        self.assertEqual([d["reason"] for d in out["dropped"]], ["quote differs from the file"])

    def test_involved_places_validated_and_render_accepts(self):
        """AUD-19, AUD-46: an involved place that is not a line of a spec file never reaches See also,
        so render accepts filter's output as it is."""
        self.write("specs/booking.md", "# Booking\nA member books.\n")
        bad = [{"path": "specs/other.md", "line": 0, "quote": ["x"], "rewrite": "r"},
               {"path": "../../../../etc/passwd", "line": 99999, "quote": ["x"], "rewrite": "r"},
               {"path": "specs/other.md", "line": 2, "quote": ["x"], "rewrite": "r"},
               {"path": "specs/x\n.md", "line": 1, "quote": ["x"], "rewrite": "r"}]
        f = {"rule": "WSP-11", "problem": "p",
             "involved": [{"path": "specs/booking.md", "line": 2, "quote": ["A member books."], "rewrite": "r"},
                          {"path": "specs/other.md", "line": 1, "quote": ["# Other"], "rewrite": "r"}] + bad}
        sel = ["specs/booking.md"]
        spec = ["specs/booking.md", "specs/other.md"]
        out = self.run_filter([f], selected=sel, spec_files=spec)
        self.assertEqual(out["findings"][0]["see_also"], ["specs/other.md:1"])
        status, report, err = self.run_script("render", stdin=json.dumps({
            "repo_root": self.repo, "n": 2, "s": 1, "mode": "session", "spec_files": spec, "selected": sel,
            "checked": sel, "findings": out["findings"]}).encode())
        self.assertEqual(status, 0, err)
        self.assertIn("  See also: specs/other.md:1\n", report)
        # Without spec_files, a finding across files is refused: its places cannot be checked.
        data = {"repo_root": self.repo, "selected": sel, "findings": [f]}
        self.assertEqual(self.run_script("filter", stdin=json.dumps(data).encode())[0], 2)

    def test_verify_list(self):
        """AUD-29 step 4, SKILL.md 4b.4: filter gives each kept finding's skeptic input, aligned by index, without
        quotes, with the problem it claims (round 2, defect 13)."""
        q = ["Large orders get free shipping, etc."]
        out = self.run_filter([
            self.finding("specs/shipping.md", 12, "WSP-2", q),
            self.finding("specs/crlf.md", 2, "WSP-2", ["- Large orders get free shipping,", "  etc."], see_also=["specs/shipping.md:1"]),
        ])
        self.assertEqual(out["verify"], [
            {"path": "specs/shipping.md", "line": 12, "lines": 1, "rule": "WSP-2", "see_also": [], "problem": "p"},
            {"path": "specs/crlf.md", "line": 2, "lines": 2, "rule": "WSP-2", "see_also": [],
             "problem": "p"}])  # AUD-20 (round 5, defect 14): no See also for a finding of one file
        self.assertEqual([(f["path"], f["line"]) for f in out["findings"]], [("specs/shipping.md", 12), ("specs/crlf.md", 2)])

    def test_bad_input(self):
        """filter refuses input that is not a JSON object with its fields."""
        self.assertEqual(self.run_script("filter", stdin=b"[]")[0], 2)
        self.assertEqual(self.run_script("filter", stdin=b"nope")[0], 2)


QUESTIONS = None


def questions():
    global QUESTIONS
    if QUESTIONS is None:
        QUESTIONS = {}
        with open(GUIDELINE, encoding="utf-8") as f:
            lines = f.read().splitlines()
        for line in lines:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if cells and cells[0].startswith("WSP-Q") and cells[0][5:].isdigit():
                QUESTIONS[cells[0]] = cells[1]
    return QUESTIONS


class Render(Base):
    """AUD-30 to AUD-35, AUD-42, AUD-43: the report."""

    SPEC_FILES = ("B.md", "a.md", "b.md", "specs/a.md", "specs/shipping.md")

    def setUp(self):
        super().setUp()
        # Render re-runs AUD-29 step 2, so the quoted lines exist in the repository.
        self.write("a.md", "# A\n" + "x\n" * 9)
        self.write("b.md", "x\n" * 9)
        self.write("B.md", "x\n" * 9)
        self.write("specs/a.md", "1\n2\n3\nMember: a person with a card.\n")
        lines = ["# Shipping"] + ["x"] * 5 + ["- Large orders get free shipping,", "  etc."] + ["y"] * 3 + \
                ["Large orders get free shipping, etc."]
        self.write("specs/shipping.md", "\n".join(lines) + "\n")

    def base(self, **extra):
        data = {
            "repo_root": self.repo, "n": 1, "s": 1, "mode": "session", "checked": [], "findings": [],
            "conditional": [{"rule": "WSP-%d" % i, "applies_to": [], "why": "No line meets it."} for i in range(13, 21)],
            "questions": [], "not_checked": [],
        }
        data.update(extra)
        if "selected" not in extra:
            data["selected"] = sorted(set(data["checked"]) | {e["what"] for e in data["not_checked"]
                                                              if "what" in e and e["reason"] != "could not be read (context only)"})
        if "spec_files" not in extra:
            data["spec_files"] = sorted(set(data["selected"]) | set(self.SPEC_FILES))
        return data

    def report(self, **extra):
        return self.json_cmd("render", self.base(**extra))

    def tail(self):
        lines = ["", "## Links between layers", "", "None."]  # AUD-30, AUD-35
        lines += ["", "## Conditional rules", "", "| Rule | Applies to | Why |", "|---|---|---|"]
        lines += ["| WSP-%d | none | No line meets it. |" % i for i in range(13, 21)]
        lines += ["", "## Questions for the approver", ""]
        for i in range(1, 18):
            lines += ["- WSP-Q%d %s" % (i, questions()["WSP-Q%d" % i]), "  Evidence: none."]
        return lines

    def test_whole_report(self):
        """AUD-30, AUD-33, AUD-35, AUD-E4, AUD-E11: the skeleton byte for byte, empty lines included."""
        q12 = ["Large orders get free shipping, etc."]
        out = self.report(
            n=2, s=2,
            checked=["specs/shipping.md", "specs/a.md"],
            findings=[
                {"path": "specs/shipping.md", "line": 12, "rule": "WSP-2", "quote": q12,
                 "problem": "The list ends in etc.", "rewrite": "An order of 50.00 EUR or more must ship free.", "see_also": []},
                {"path": "specs/shipping.md", "line": 7, "rule": "WSP-2", "quote": ["- Large orders get free shipping,", "  etc."],
                 "problem": "Two readings.", "rewrite": "One.; Two.", "see_also": []},
            ],
        )
        expected = [
            "Check of writing of %s against writing-specs.md: 2 of 2 selected spec files checked, 2 findings. Spec set: 2 spec files. Mode: session." % self.repo,
            "",
            "## Findings",
            "",
            "### specs/a.md",
            "",
            "No findings.",
            "",
            "### specs/shipping.md",
            "",
            "- specs/shipping.md:7 · WSP-2",
            "  > - Large orders get free shipping,",
            "  >   etc.",
            "  Problem: Two readings.",
            "  Rewrite: One.; Two.",
            "",
            "- specs/shipping.md:12 · WSP-2",
            "  > Large orders get free shipping, etc.",
            "  Problem: The list ends in etc.",
            "  Rewrite: An order of 50.00 EUR or more must ship free.",
        ] + self.tail() + ["", "## Not checked", "", "None."]
        self.assertEqual(out, "\n".join(expected) + "\n")

    def test_singular(self):
        """AUD-32, AUD-E1: `file` when <s> or <n> is 1, `finding` when <f> is 1; Mode: session."""
        out = self.report(checked=["a.md"], findings=[{"path": "a.md", "line": 1, "rule": "WSP-1", "quote": ["# A"],
                                                       "problem": "p", "rewrite": "r"}])
        self.assertTrue(out.startswith("Check of writing of " + self.repo + " against writing-specs.md: 1 of 1 selected spec file checked, "
                                       "1 finding. Spec set: 1 spec file. Mode: session.\n"))
        out = self.report(checked=["a.md"], n=4, s=1, mode="workflow")
        self.assertTrue(out.startswith("Check of writing of " + self.repo + " against writing-specs.md: 1 of 1 selected spec file checked, "
                                       "0 findings. Spec set: 4 spec files. Mode: workflow.\n"))

    def test_finding_order(self):
        """AUD-34: file sections by path; findings by rule (WSP-1..WSP-20, then the decisions), then by line."""
        def f(path, line, rule):
            return {"path": path, "line": line, "rule": rule, "quote": ["x"], "problem": "p", "rewrite": "r"}
        out = self.report(n=2, s=2, checked=["b.md", "B.md"], findings=[
            f("b.md", 1, "WSP-T4"), f("b.md", 5, "WSP-10"), f("b.md", 9, "WSP-2"), f("b.md", 2, "WSP-2"),
            f("b.md", 1, "WSP-T15"), f("b.md", 1, "WSP-T11"), f("B.md", 3, "WSP-20")])
        firsts = [l for l in out.splitlines() if l.startswith("- ") and "WSP-Q" not in l]
        self.assertEqual(firsts, ["- B.md:3 · WSP-20", "- b.md:2 · WSP-2", "- b.md:9 · WSP-2", "- b.md:5 · WSP-10",
                                  "- b.md:1 · WSP-T4", "- b.md:1 · WSP-T11", "- b.md:1 · WSP-T15"])

    def test_see_also(self):
        """AUD-E9, AUD-31, AUD-34: See also places by path then line, separated by `, `."""
        self.write("specs/b.md", "x\n" * 10)
        self.write("specs/c.md", "x\n" * 2)
        out = self.report(n=3, checked=["specs/a.md"], spec_files=["specs/a.md", "specs/b.md", "specs/c.md"], findings=[{
            "path": "specs/a.md", "line": 4, "rule": "WSP-3", "quote": ["Member: a person with a card."],
            "problem": "p", "rewrite": "r", "see_also": ["specs/c.md:2", "specs/b.md:10", "specs/b.md:9"]}])
        self.assertIn("- specs/a.md:4 · WSP-3\n  > Member: a person with a card.\n  Problem: p\n  Rewrite: r\n"
                      "  See also: specs/b.md:9, specs/b.md:10, specs/c.md:2\n\n## Links between layers", out)

    def test_not_verified(self):
        """AUD-43: a finding whose skeptic failed ends its first line with ` · not verified`."""
        out = self.report(checked=["a.md"], findings=[
            {"path": "a.md", "line": 1, "rule": "WSP-1", "quote": ["# A"], "problem": "p", "rewrite": "r", "verified": False},
            {"path": "a.md", "line": 1, "rule": "WSP-2", "quote": ["# A"], "problem": "p", "rewrite": "r", "verified": True}])
        self.assertIn("- a.md:1 · WSP-1 · not verified\n", out)
        self.assertIn("- a.md:1 · WSP-2\n", out)
        self.assertIn("2 findings", out)

    def test_failed_checker(self):
        """AUD-E8, AUD-35, AUD-42: 4 of 5 checked; the failed file only under Not checked."""
        files = ["specs/a.md", "specs/b.md", "specs/c.md", "specs/d.md", "specs/e.md"]
        out = self.report(n=5, s=5, mode="workflow", selected=files, checked=[f for f in files if f != "specs/b.md"],
                          not_checked=[{"what": "specs/b.md", "reason": "the checker failed or did not finish"}])
        self.assertIn(": 4 of 5 selected spec files checked, 0 findings.", out)
        self.assertTrue(out.endswith("## Not checked\n\n- specs/b.md — the checker failed or did not finish\n"))
        self.assertNotIn("### specs/b.md", out)

    def test_not_checked_order(self):
        """AUD-42: files in code point order of path, then the pass across files, then the readers; Q2 and Q3 hold only Evidence: none."""
        out = self.report(n=4, s=2, checked=[], findings=[], not_checked=[
            {"pass": "readers"},
            {"what": "z.md", "reason": "the run was stopped"},
            {"pass": "across"},
            {"what": "a.md", "reason": "could not be read (context only)"},
            {"what": "B.md", "reason": "could not be read"},
        ], questions=[
            {"id": "WSP-Q2", "evidence": [{"path": "a.md", "line": 1, "text": "Readers differ."}]},
            {"id": "WSP-Q4", "evidence": [{"path": "a.md", "line": 2, "text": "No error path."}]},
        ])
        self.assertTrue(out.endswith(
            "## Not checked\n\n"
            "- B.md — could not be read\n"
            "- a.md — could not be read (context only)\n"
            "- z.md — the run was stopped\n"
            "- across files (WSP-3, WSP-11, WSP-13, WSP-14, WSP-Q4, WSP-Q12) — the pass failed or did not finish\n"
            "- readers (WSP-Q2, WSP-Q3) — a reader failed or did not finish\n"))
        self.assertIn("## Findings\n\nNone.\n\n## Links between layers\n\nNone.\n\n## Conditional rules", out)
        self.assertIn("- WSP-Q2 %s\n  Evidence: none.\n" % questions()["WSP-Q2"], out)
        self.assertIn("- WSP-Q4 %s\n  Evidence: a.md:2 No error path.\n" % questions()["WSP-Q4"], out)

    def test_questions(self):
        """AUD-22, AUD-27, AUD-34: evidence by path, line, text; ` (not independent)`, never after Evidence: none."""
        out = self.report(questions=[
            {"id": "WSP-Q3", "not_independent": True, "evidence": [
                {"path": "b.md", "line": 2, "text": "Gap."}, {"path": "a.md", "line": 10, "text": "Two readings."},
                {"path": "a.md", "line": 9, "text": "Z."}, {"path": "a.md", "line": 9, "text": "A."}]},
            {"id": "WSP-Q2", "not_independent": True, "evidence": []},
            {"id": "WSP-Q1", "evidence": [{"path": "a.md", "line": 1, "text": "No audience."}, {"text": "no place"}]},
        ])
        self.assertIn("- WSP-Q1 %s\n  Evidence: a.md:1 No audience.\n- WSP-Q2 %s\n  Evidence: none.\n- WSP-Q3 %s\n"
                      "  Evidence: a.md:9 A. (not independent)\n  Evidence: a.md:9 Z. (not independent)\n"
                      "  Evidence: a.md:10 Two readings. (not independent)\n  Evidence: b.md:2 Gap. (not independent)\n- WSP-Q4"
                      % (questions()["WSP-Q1"], questions()["WSP-Q2"], questions()["WSP-Q3"]), out)
        self.assertEqual(out.count("\n- WSP-Q"), 17)

    def test_question_texts_from_guideline(self):
        """AUD-15, AUD-22: the question texts are read from the guideline at run time."""
        with open(self.guideline, encoding="utf-8") as f:
            text = f.read()
        with open(self.guideline, "w", encoding="utf-8") as f:
            f.write(text.replace(questions()["WSP-Q7"], "Changed question seven?"))
        self.assertIn("- WSP-Q7 Changed question seven?\n", self.report())
        os.remove(self.guideline)
        self.assertEqual(self.run_script("render", stdin=json.dumps(self.base()).encode())[0], 2)

    def test_conditional_rules(self):
        """AUD-31, AUD-34, AUD-35: one row per WSP-13 to WSP-20 in order; paths in code point order, or none."""
        out = self.report(checked=["specs/a.md", "specs/b.md"], conditional=[
            {"rule": "WSP-17", "applies_to": ["specs/b.md", "specs/a.md"], "why": "It reads | files."},
        ] + [{"rule": "WSP-%d" % i, "applies_to": [], "why": "No."} for i in range(13, 21) if i != 17])
        rows = [l for l in out.splitlines() if l.startswith("| WSP-")]
        self.assertEqual([r.split(" | ")[0] for r in rows], ["| WSP-%d" % i for i in range(13, 21)])
        self.assertIn("| WSP-17 | specs/a.md, specs/b.md | It reads \\| files. |", rows)
        self.assertIn("| WSP-13 | none | No. |", rows)

    def test_partition_enforced(self):
        """AUD-35: a selected file never appears both under Findings and under Not checked."""
        data = self.base(checked=["a.md"], not_checked=[{"what": "a.md", "reason": "could not be read"}])
        self.assertEqual(self.run_script("render", stdin=json.dumps(data).encode())[0], 2)
        data = self.base(checked=["a.md"], selected=["a.md", "b.md"])
        self.assertEqual(self.run_script("render", stdin=json.dumps(data).encode())[0], 2)
        data = self.base(checked=[], selected=["a.md"], not_checked=[{"what": "a.md", "reason": "could not be read"}],
                         findings=[{"path": "a.md", "line": 1, "rule": "WSP-1", "quote": ["# A"], "problem": "p", "rewrite": "r"}])
        status, _, err = self.run_script("render", stdin=json.dumps(data).encode())
        self.assertEqual(status, 2)
        self.assertIn("not checked", err)

    def test_step2_rerun(self):
        """AUD-46, AUD-29 step 2: render refuses a finding that step 2 drops, naming it, and prints no report."""
        good = {"path": "a.md", "line": 1, "rule": "WSP-1", "quote": ["# A"], "problem": "p", "rewrite": "r"}
        cases = [
            (dict(good, quote=["# A "]), "quote differs from the file"),
            (dict(good, quote=["#  A"]), "quote differs from the file"),
            (dict(good, quote=["# A", "more"]), "quote differs from the file"),
            (dict(good, quote=[]), "quote differs from the file"),
            (dict(good, line=11), "line does not exist"),
            (dict(good, line=0), "line does not exist"),
            (dict(good, rule="WSP-Q1"), "rule is not a binding rule"),
            (dict(good, path="b.md", quote=["x"]), "path is not a selected file"),
        ]
        for finding, reason in cases:
            data = self.base(checked=["a.md"], findings=[good, finding])
            status, out, err = self.run_script("render", stdin=json.dumps(data).encode())
            self.assertEqual((status, out), (2, ""), finding)
            self.assertIn("finding 2 (%s:%d %s)" % (finding["path"], finding["line"], finding["rule"]), err)
            self.assertIn(reason, err)
        self.assertIn("- a.md:1 · WSP-1\n", self.report(checked=["a.md"], findings=[good]))

    def test_types_refused(self):
        """SKILL.md section 3: render takes only the exact types; a quote string or a rewrite list is refused."""
        good = {"path": "a.md", "line": 1, "rule": "WSP-1", "quote": ["# A"], "problem": "p", "rewrite": "r"}
        cases = [
            (dict(good, quote="# A"), "'quote' must be"),
            (dict(good, rewrite=["One.", "Two."]), "'rewrite' must be"),
            (dict(good, see_also=["b.md"]), "'see_also' must be"),
            (dict(good, verified="yes"), "'verified' must be"),
            ({k: v for k, v in good.items() if k != "problem"}, "'problem' is missing"),
            (dict(good, involved=[{"path": "a.md", "line": 1, "quote": ["# A"]}]), "unplaced"),
        ]
        for finding, message in cases:
            data = self.base(checked=["a.md"], findings=[finding])
            status, out, err = self.run_script("render", stdin=json.dumps(data).encode())
            self.assertEqual((status, out), (2, ""), finding)
            self.assertIn("finding 1", err)
            self.assertIn(message, err)

    def test_selected_required(self):
        """AUD-35, AUD-46: render needs `selected`, so a selected file left out of the input cannot vanish."""
        data = self.base(checked=["a.md"])
        del data["selected"]
        self.assertEqual(self.run_script("render", stdin=json.dumps(data).encode())[0], 2)
        data = self.base(checked=["a.md"], selected=["a.md", "forgotten.md"])
        status, _, err = self.run_script("render", stdin=json.dumps(data).encode())
        self.assertEqual(status, 2)
        self.assertIn("forgotten.md", err)

    def test_applies_to_only_selected(self):
        """AUD-31: <paths> of a conditional rule lists only selected files."""
        out = self.report(checked=["a.md"], conditional=[
            {"rule": "WSP-15", "applies_to": ["a.md", "other.md"], "why": "It reads the clock."},
            {"rule": "WSP-16", "applies_to": ["other.md"], "why": "No."}])
        self.assertIn("| WSP-15 | a.md | It reads the clock. |", out)
        self.assertIn("| WSP-16 | none | No. |", out)

    def test_evidence_places_validated(self):
        """AUD-46, AUD-26: an Evidence line cites a line of a spec file; line 0, negative, past the end,
        a string line and a path outside the spec set are left out."""
        out = self.report(checked=["a.md"], questions=[{"id": "WSP-Q1", "evidence": [
            {"path": "a.md", "line": 0, "text": "zero"}, {"path": "nope.md", "line": -4, "text": "neg"},
            {"path": "a.md", "line": "007", "text": "str"}, {"path": "a.md", "line": 11, "text": "past"},
            {"path": "../../etc/passwd", "line": 1, "text": "outside"}, {"path": "b.md", "line": 9, "text": "kept"}]}])
        self.assertIn("- WSP-Q1 %s\n  Evidence: b.md:9 kept\n- WSP-Q2" % questions()["WSP-Q1"], out)

    def test_unreadable_listed(self):
        """AUD-42, AUD-35: render lists prepare's unreadable files under Not checked, also in workflow mode."""
        out = self.report(n=4, s=2, mode="workflow", checked=["a.md"], selected=["a.md", "c.md"],
                          unreadable=["c.md", "d.md"])
        self.assertTrue(out.endswith("## Not checked\n\n- c.md — could not be read\n"
                                     "- d.md — could not be read (context only)\n"))
        # Listed by the session too: once.
        out = self.report(checked=["a.md"], selected=["a.md", "c.md"], unreadable=["c.md"],
                          not_checked=[{"what": "c.md", "reason": "could not be read"}])
        self.assertEqual(out.count("- c.md — could not be read"), 1)

    def test_file_changed_after_filter(self):
        """AUD-41, AUD-46: a file that another session changes between filter and render does not make
        render refuse forever; a finding changed by hand on an unchanged file is still refused."""
        self.write("specs/x.md", "# X\n\nLarge orders ship free, etc.\n")
        base = {"repo_root": self.repo, "selected": ["specs/x.md"], "spec_files": ["specs/x.md"]}
        kept = self.json_cmd("filter", dict(base, findings=[
            {"path": "specs/x.md", "line": 3, "rule": "WSP-2", "quote": ["Large orders ship free, etc."],
             "problem": "p", "rewrite": "r"}]))["findings"]
        data = dict(base, n=1, s=1, mode="session", checked=["specs/x.md"])
        # Round 4, defect 7: a mis-copied quote is repaired from the file, which `check` proves;
        # a finding moved to another line is still refused.
        mangled = [dict(kept[0], quote=["Large orders ship free etc."])]
        status, out, err = self.run_script("render", stdin=json.dumps(dict(data, findings=mangled)).encode())
        self.assertEqual(status, 0, err)
        self.assertIn("  > Large orders ship free, etc.\n", out)
        moved = [dict(kept[0], line=2)]
        self.assertEqual(self.run_script("render", stdin=json.dumps(dict(data, findings=moved)).encode())[0], 2)
        self.write("specs/x.md", "# X\n\nAdded.\nAdded.\n\nLarge orders ship free, etc.\n")
        status, out, err = self.run_script("render", stdin=json.dumps(dict(data, findings=kept)).encode())
        self.assertEqual(status, 0, err)
        self.assertIn("- specs/x.md:3 · WSP-2\n  > Large orders ship free, etc.\n", out)

    def test_paths_escaped(self):
        """AUD-31, AUD-8, AUD-30: a path with a line feed or `|` cannot add headings, items or table cells."""
        evil = "x.md\n\n## Not checked\n\n- y.md"
        try:
            self.write(evil, "# X\n")
        except OSError:
            self.skipTest("the file system refuses a line feed in a name")
        self.write("a|b.md", "# AB\n")
        out = self.report(n=2, s=2, checked=[evil, "a|b.md"], findings=[
            {"path": evil, "line": 1, "rule": "WSP-1", "quote": ["# X"], "problem": "p", "rewrite": "r",
             "see_also": ["a|b.md:1"]}],
            conditional=[{"rule": "WSP-17", "applies_to": ["a|b.md"], "why": "w"}])
        shown = "x.md\\u000a\\u000a## Not checked\\u000a\\u000a- y.md"
        self.assertIn("### %s\n" % shown, out)
        self.assertIn("- %s:1 · WSP-1\n" % shown, out)
        self.assertEqual(out.count("\n## Not checked\n"), 1)
        self.assertNotIn("\n- y.md", out)
        self.assertIn("| WSP-17 | a\\|b.md | w |", out)
        self.assertIn("  See also: a|b.md:1\n", out)

    def test_mode_not_available(self):
        """AUD-25, AUD-31: <mode> as given, `session (workflow not available)` included."""
        out = self.report(mode="session (workflow not available)", n=5)
        self.assertIn(" Mode: session (workflow not available).\n", out.splitlines(True)[0])


WORKFLOW = os.path.join(PLUGIN, "use-cases", "check-writing", "workflow.js")
NODE = shutil.which("node")

# Runs workflow.js as the Workflow tool does, with agent() answering from a
# table keyed by label prefix; prints the result or the error, and every prompt.
HARNESS = r"""
const fs = require('fs')
const [script, argsJson, answersJson] = process.argv.slice(1)
const src = fs.readFileSync(script, 'utf8').replace(/^export const meta/m, 'const meta')
const answers = JSON.parse(answersJson)
const prompts = {}, logs = []
const agent = async (prompt, opts) => {
  prompts[opts.label] = prompt
  const key = Object.keys(answers).find((k) => opts.label.startsWith(k))
  return key === undefined ? null : answers[key]
}
const parallel = async (ts) => Promise.all(ts.map((t) => t().catch(() => null)))
const pipeline = async (items, f) => Promise.all(items.map((x, i) => f(x, x, i).catch(() => null)))
const AF = Object.getPrototypeOf(async function () {}).constructor
new AF('args', 'agent', 'parallel', 'pipeline', 'phase', 'log', src)(
  JSON.parse(argsJson), agent, parallel, pipeline, () => {}, (m) => logs.push(m))
  .then((result) => console.log(JSON.stringify({ result, prompts, logs })))
  .catch((e) => console.log(JSON.stringify({ error: String(e && e.message), prompts, logs })))
"""


@unittest.skipIf(NODE is None, "node is not installed")
class WorkflowScript(unittest.TestCase):
    """workflow.js, the agents of workflow mode (AUD-23, AUD-26, AUD-29 step 4, AUD-43)."""

    ARGS = {"repo_root": "/r", "guideline": "/p/writing-specs.md", "spec_files": ["README.md", "specs/a.md", "specs/b.md", "specs/c.md"],
            "selected": ["specs/a.md"], "language": "English"}

    def run_workflow(self, args, answers):
        proc = subprocess.run([NODE, "-e", HARNESS, WORKFLOW, json.dumps(args), json.dumps(answers)],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return json.loads(proc.stdout)

    def verify(self, findings, answers=None):
        return self.run_workflow(dict(self.ARGS, stage="verify", findings=findings),
                                 answers or {"skeptic": {"verdict": "confirmed", "reason": "x"}})

    def test_verify_refuses_findings_that_are_not_a_list(self):
        """AUD-43, SKILL.md 4b.4: findings given as a string or an empty list make the call fail; never zero verdicts."""
        item = {"path": "specs/a.md", "line": 3, "lines": 1, "rule": "WSP-2", "see_also": [], "problem": "p"}
        for bad in (json.dumps([item]), [], [dict(item, line="3")], [{"path": "specs/a.md", "line": 3, "rule": "WSP-2"}]):
            out = self.verify(bad)
            self.assertIn("error", out, bad)
            self.assertEqual(out["prompts"], {})
        out = self.verify([item])
        self.assertEqual(out["result"]["verdicts"], [{"verdict": "confirmed", "reason": "x"}])
        self.assertEqual((out["result"]["part"], out["result"]["parts"]), (1, 1))

    def test_skeptic_judges_see_also_places_and_takes_applicability_as_given(self):
        """AUD-29 step 4, AUD-19, AUD-17: the skeptic judges the quote with the See also places, from the
        compact verify entry, and never refutes because a rule's "Applies when:" line does not hold."""
        out = self.verify([{"path": "specs/a.md", "line": 3, "lines": 2, "rule": "WSP-3", "see_also": ["specs/b.md:5"],
                            "problem": "p"},
                           {"path": "specs/a.md", "line": 7, "lines": 1, "rule": "WSP-17", "see_also": [], "problem": "p"}])
        first, second = (out["prompts"][k] for k in sorted(out["prompts"]))
        self.assertIn("line 3 to 4 of \"specs/a.md\"", first)
        self.assertIn("specs/b.md:5", first)
        self.assertIn("together", first)
        self.assertIn("never refute because a rule's \"Applies when:\" line does not hold", second)
        self.assertNotIn("line does not hold for that file", second)

    def test_agents_and_their_inputs(self):
        """AUD-23, AUD-26, AUD-8: checkers read the spec set as context; both readers share one definition
        of a behaviour and the guideline's convention; reader places outside the selected files are dropped."""
        reader = {"behaviours": [{"path": "/r/specs/a.md", "line": 1, "behaviour": "b"},
                                 {"path": "specs/b.md", "line": 2, "behaviour": "outside"}],
                  "two_readings": [{"path": "specs/c.md", "line": 1, "text": "outside"}],
                  "gaps": [{"path": "specs/a.md", "line": 1, "text": "g"}]}
        out = self.run_workflow(dict(self.ARGS, stage="check"), {
            "checker": {"findings": [], "evidence": [],
                        "conditional": {"WSP-%d" % i: {"applies": False, "why": "No."} for i in range(15, 21)}},
            "across files": {"conditional": {"WSP-13": {"applies_to": [], "why": "w"}, "WSP-14": {"applies_to": [], "why": "w"}},
                             "findings": [], "evidence": []},
            "reader": reader})
        self.assertEqual((out["result"]["checkers"][0]["ok"], out["result"]["cross"] is None), (True, False))
        self.assertEqual(out["result"]["readers_ok"], [True, True])
        checker = out["prompts"]["checker specs/a.md"]
        for other in ("README.md", "specs/b.md", "specs/c.md"):
            self.assertIn(json.dumps("/r/" + other), checker)
        self.assertIn("Report only on the spec file you check", checker)
        a, b = out["prompts"]["reader A (build)"], out["prompts"]["reader B (questions)"]
        definition = "each statement of the selected files that makes the system do, refuse, produce or keep something"
        for prompt in (a, b, checker):
            self.assertIn("CLAUDE.md", prompt)
        for prompt in (a, b):
            self.assertIn(definition, prompt)
            self.assertIn('"must" and "must not" state an obligation', prompt)
        result = out["result"]
        self.assertEqual(result["behaviours"], [{"reader": r, "path": "specs/a.md", "line": 1, "behaviour": "b"}
                                                for r in (0, 1)])
        self.assertEqual(result["two_readings"], [])
        self.assertEqual(result["gaps"], [{"path": "specs/a.md", "line": 1, "text": "g"}] * 2)


class RoundTwoPrepare(Base):
    """Round 2 defects of prepare (AUD-11, AUD-13, AUD-40)."""

    def test_repository_folder_spelled_in_another_case(self):
        """AUD-11, AUD-13, AUD-40 (round 2, defect 1): a folder above the root spelled in another case
        or Unicode form still finds the spec file, by identity, not by string."""
        self.write("docs/a.md", "# a\n")
        git(self.repo, "add", "-A")
        upper = os.path.join(self.tmp, "REPO")
        if not os.path.exists(upper):
            self.skipTest("case-sensitive file system")
        self.assertEqual(self.prepare(os.path.join(upper, "docs", "a.md"))[1]["selected"], ["docs/a.md"])
        self.assertEqual(self.prepare(os.path.join("REPO", "docs", "a.md"), cwd=self.tmp)[1]["selected"], ["docs/a.md"])
        self.assertEqual(self.prepare(os.path.join("REPO", "DOCS", "A.md"), cwd=self.tmp)[1]["selected"], ["docs/a.md"])
        nfc = os.path.join(self.tmp, "répo")
        os.makedirs(nfc)
        git(nfc, "init", "-q")
        self.write("b.md", "# b\n", base=nfc)
        nfd = os.path.join(self.tmp, "répo", "b.md")
        if not os.path.exists(nfd):
            self.skipTest("normalization-sensitive file system")
        self.assertEqual(self.prepare(nfd)[1]["selected"], ["b.md"])

    def test_git_directory_spelled_in_another_case(self):
        """AUD-11, AUD-13, AUD-40 (round 2, defect 2): `.GIT` is the git directory too: no spec file found."""
        self.write("a.md", "# a\n")
        git(self.repo, "add", "a.md")
        git(self.repo, "commit", "-q", "-m", "x")
        if not os.path.exists(os.path.join(self.repo, ".GIT")):
            self.skipTest("case-sensitive file system")
        self.assertEqual(self.prepare(".GIT"), (1, "specs-management:check-writing: .GIT: no spec file found\n"))
        self.assertEqual(self.prepare(".GIT/HEAD"), (1, "specs-management:check-writing: .GIT/HEAD: no spec file found\n"))

    def test_absolute_path_from_deleted_working_directory(self):
        """AUD-40 (round 2, defect 3): an absolute argument does not need the working directory."""
        self.write("docs/a.md", "# a\n")
        target = os.path.join(self.repo, "docs", "a.md")
        gone = os.path.join(self.tmp, "gone")
        os.makedirs(gone)
        cmd = 'cd "$1" && rmdir "$1" && exec "$2" "$3" prepare "$4"'
        proc = subprocess.run(["sh", "-c", cmd, "sh", gone, sys.executable, self.script, target],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["selected"], ["docs/a.md"])
        os.makedirs(gone)  # a relative argument still needs it
        proc = subprocess.run(["sh", "-c", cmd, "sh", gone, sys.executable, self.script, "docs/a.md"],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual((proc.returncode, proc.stdout), (1, b"specs-management:check-writing: docs/a.md: no such file or folder\n"))

    def test_broken_git_file(self):
        """AUD-11, AUD-40 (round 2, defect 4): a folder whose .git file points nowhere is not 'outside any
        repository'; git's own error is reported."""
        self.write("a.md", "# a\n")
        self.write("broken/.git", "gitdir: ../.git/modules/broken\n")
        self.write("broken/s.md", "# s\n")
        status, out = self.prepare("broken/s.md")
        self.assertEqual(status, 1)
        self.assertTrue(out.startswith("specs-management:check-writing: git failed: fatal: not a git repository: "), out)


class RoundTwoWords(unittest.TestCase):
    """Round 2 defects of the word count (AUD-36)."""

    def test_backtick_fence_info_string(self):
        """AUD-36 (round 2, defect 5): a backtick line whose info string holds a backtick is a code span, not a fence."""
        self.assertEqual(check_writing.count_words(b"```npm install```\n\nEste texto en castellano tiene muchas palabras aqui.\n\n"
                                           b"Otro parrafo largo en castellano.\n"), 13)

    def test_closing_fence_indented_four_columns(self):
        """AUD-36 (round 2, defect 5): a closing fence is indented at most 3 columns."""
        self.assertEqual(check_writing.count_words(b"Text\n\n```\ncode here\n        ```\nmore code words here\n```\n"), 1)
        self.assertEqual(check_writing.count_words(b"Text\n\n```\ncode here\n   ```\nmore words here\n"), 4)

    def test_unspaced_scripts(self):
        """AUD-36 (round 2, defect 6): each Han, Hiragana, Katakana or Thai letter counts as one word."""
        zh = "本规范定义了审计工具的行为，以及它如何处理每一个文件和每一条规则。"
        self.assertEqual(check_writing.count_words(zh.encode()), 31)
        self.assertEqual(check_writing.count_words("このスペックは監査ツールの動作を定義します。".encode()), 21)
        self.assertEqual(check_writing.count_words("ภาษาไทย".encode()), 7)
        self.assertEqual(check_writing.count_words("The check 規則 reads.".encode()), 5)

    def test_crlf_paragraphs(self):
        """AUD-36 (round 2, defect 20): a blank line of a CRLF file ends a paragraph, so a stray backtick
        does not pair with one several paragraphs later."""
        lf = b"# T\n\nUse `x for this.\n\nOne two three four five six seven eight nine ten.\n\nAnother `y` here.\n"
        self.assertEqual(check_writing.count_words(lf), 17)
        self.assertEqual(check_writing.count_words(lf.replace(b"\n", b"\r\n")), 17)


class RoundTwoFilter(Base):
    """Round 2 defects of filter (AUD-19, AUD-29)."""

    SPEC = ["specs/a.md", "specs/b.md", "specs/c.md"]

    def setUp(self):
        super().setUp()
        self.write("specs/a.md", "# A\nMember: a person with a card.\n")
        self.write("specs/b.md", "x\n" * 12)

    def run_filter(self, findings, selected=("specs/a.md",), **extra):
        data = {"repo_root": self.repo, "selected": list(selected), "spec_files": self.SPEC, "findings": findings}
        data.update(extra)
        return self.json_cmd("filter", data)

    def f(self, **extra):
        f = {"path": "specs/a.md", "line": 2, "rule": "WSP-3", "quote": ["Member: a person with a card."],
             "problem": "p", "rewrite": "r", "see_also": []}
        f.update(extra)
        return f

    def test_see_also_places_validated(self):
        """AUD-29 step 3, AUD-19, AUD-46 (round 2, defect 7): a See also place that is not a line of a spec
        file is left out before the merge, so the same finding is not reported twice."""
        # Round 5, defect 14: only a finding across files has See also places (AUD-20), from its involved places.
        a = {"path": "specs/a.md", "line": 2, "quote": ["Member: a person with a card."], "rewrite": "r"}

        def across(*others):
            return {"rule": "WSP-3", "problem": "p",
                    "involved": [a] + [{"path": p, "line": n, "quote": ["x"], "rewrite": "r"} for p, n in others]}
        out = self.run_filter([across(("specs/b.md", 9)), across(("specs/b.md", 9), ("specs/b.md", 999)),
                               across(("./specs/b.md", 9)), across(("README.md", 1))])
        self.assertEqual([x["see_also"] for x in out["findings"]], [["specs/b.md:9"], []])
        self.assertEqual([x["see_also"] for x in out["verify"]], [["specs/b.md:9"], []])

    def test_double_byte_order_mark(self):
        """Term "Line", AUD-29 step 2 (round 2, defect 10): only the first BOM is not part of line 1,
        so a quote that keeps the second one matches."""
        self.write("specs/c.md", b"\xef\xbb\xbf\xef\xbb\xbfdouble bom\n")
        out = self.run_filter([self.f(path="specs/c.md", line=1, quote=["﻿double bom"]),
                               self.f(path="specs/c.md", line=1, rule="WSP-2", quote=["﻿﻿double bom"]),
                               self.f(path="specs/c.md", line=1, rule="WSP-4", quote=["double bom"])],
                              selected=["specs/c.md"])
        # Round 4, defect 19: the term "Quote" leaves format characters (Cf), a BOM among them, out
        # on both sides, so the quote without the second BOM matches too; filter gives the file's line.
        self.assertEqual([x["rule"] for x in out["findings"]], ["WSP-3", "WSP-2", "WSP-4"])
        self.assertEqual([x["quote"] for x in out["findings"]], [["\ufeffdouble bom"]] * 3)

    def test_verify_entry_holds_the_problem(self):
        """AUD-23, AUD-29 step 4 (round 2, defect 13): the skeptic gets the claim it judges."""
        out = self.run_filter([self.f(problem="Member is called user in b.md.")])
        self.assertEqual(out["verify"][0]["problem"], "Member is called user in b.md.")

    def test_wsp14_placed_only_where_it_applies(self):
        """AUD-19, AUD-17 (round 2, defect 14): a WSP-14 finding across files goes only to a file where WSP-14 applies."""
        self.write("specs/b.md", "1\n2\n3\n4\n5\n6\nAs stated in section 3.2, second bullet.\n")
        f = {"rule": "WSP-14", "problem": "p", "involved": [
            {"path": "specs/a.md", "line": 2, "quote": ["Member: a person with a card."], "rewrite": "r"},
            {"path": "specs/b.md", "line": 7, "quote": ["As stated in section 3.2, second bullet."], "rewrite": "r"}]}
        sel = ["specs/a.md", "specs/b.md"]
        got = self.run_filter([f], selected=sel, wsp14_applies_to=["specs/b.md"])["findings"][0]
        self.assertEqual((got["path"], got["line"], got["see_also"]), ("specs/b.md", 7, ["specs/a.md:2"]))
        out = self.run_filter([f], selected=sel, wsp14_applies_to=[])
        self.assertEqual(out["findings"], [])
        status, _, err = self.run_script("filter", stdin=json.dumps(
            {"repo_root": self.repo, "selected": sel, "spec_files": self.SPEC, "findings": [f]}).encode())
        self.assertEqual(status, 2)
        self.assertIn("wsp14_applies_to", err)

    def test_distinct_problems_not_merged(self):
        """AUD-29 step 3, AUD-21 (round 2, defect 16): two missing-text findings of one rule at one heading
        are kept; the same finding given twice is merged."""
        self.write("specs/booking.md", "# Booking\nGuests reserve rooms.\n")
        head = dict(path="specs/booking.md", line=1, rule="WSP-1", quote=["# Booking"])
        out = self.run_filter([self.f(problem="No out-of-scope statement.", **head),
                               self.f(problem="No statement of what must never happen.", **head),
                               self.f(problem="No out-of-scope statement.", rewrite="other", **head)],
                              selected=["specs/booking.md"], spec_files=["specs/booking.md"])
        self.assertEqual([x["problem"] for x in out["findings"]],
                         ["No out-of-scope statement.", "No statement of what must never happen."])


class RoundTwoRender(Base):
    """Round 2 defects of render (AUD-31, AUD-42)."""

    def setUp(self):
        super().setUp()
        self.write("a.md", "one\rtwo etc.\rthree\n")
        self.write("b.md", "# B\n")

    def data(self, **extra):
        d = {"repo_root": self.repo, "n": 3, "s": 2, "mode": "session", "spec_files": ["README.md", "a.md", "b.md"],
             "selected": ["a.md", "b.md"], "checked": ["a.md", "b.md"], "findings": [], "conditional": [],
             "questions": [], "not_checked": []}
        d.update(extra)
        return d

    def test_carriage_return_in_quote(self):
        """AUD-31, AUD-30 (round 2, defect 8): a CR inside a quote line is shown as \\u000d, so the
        skeleton keeps one `  > ` line per line."""
        out = self.json_cmd("render", self.data(findings=[
            {"path": "a.md", "line": 1, "rule": "WSP-2", "quote": ["one\rtwo etc.\rthree"], "problem": "p", "rewrite": "r"}]))
        self.assertIn("  > one\\u000dtwo etc.\\u000dthree\n", out)
        self.assertNotIn("\r", out)

    def test_not_checked_entries_checked(self):
        """AUD-42, AUD-35 (round 2, defect 9): render refuses a not-checked file that is not selected, a file
        listed twice, and a reason outside AUD-42's list."""
        self.write("README.md", "# R\n")
        stopped = {"what": "b.md", "reason": "the run was stopped"}
        cases = [
            [{"what": "b.md", "reason": "the checker failed or did not finish"}, stopped],
            [stopped, {"what": "README.md", "reason": "could not be read"}],
            [{"what": "b.md", "reason": "it was too long"}],
            [{"what": "b.md", "reason": "could not be read (context only)"}],
            [stopped, {"what": "other.md", "reason": "could not be read (context only)"}],
        ]
        for entries in cases:
            status, out, err = self.run_script("render", stdin=json.dumps(
                self.data(checked=["a.md"], not_checked=entries)).encode())
            self.assertEqual((status, out), (2, ""), entries)
        out = self.json_cmd("render", self.data(checked=["a.md"], not_checked=[
            stopped, {"what": "README.md", "reason": "could not be read (context only)"}]))
        self.assertTrue(out.endswith("- README.md — could not be read (context only)\n- b.md — the run was stopped\n"))


@unittest.skipIf(NODE is None, "node is not installed")
class RoundTwoWorkflow(unittest.TestCase):
    """Round 2 defects of workflow.js (AUD-17, AUD-23)."""

    ARGS, run_workflow, verify = WorkflowScript.ARGS, WorkflowScript.run_workflow, WorkflowScript.verify

    CHECKER_ROWS = {"WSP-%d" % i: {"applies": False, "why": "No."} for i in range(15, 21)}
    CROSS_ROWS = {"WSP-13": {"applies_to": [], "why": "Small."}, "WSP-14": {"applies_to": ["specs/a.md"], "why": "IDs."}}

    def test_skeptic_sees_the_problem(self):
        """AUD-23, AUD-29 step 4 (round 2, defect 13): the skeptic judges the stated problem."""
        item = {"path": "specs/a.md", "line": 1, "lines": 1, "rule": "WSP-1", "see_also": [],
                "problem": "The file has no out-of-scope statement."}
        out = self.verify([item])
        prompt = next(iter(out["prompts"].values()))
        self.assertIn("The file has no out-of-scope statement.", prompt)
        self.assertIn("the stated problem is not true", prompt)
        self.assertIn("error", self.verify([{k: v for k, v in item.items() if k != "problem"}]))

    def test_one_conditional_row_per_rule(self):
        """AUD-17 (round 2, defect 15): a checker or pass whose rows do not decide each rule once fails;
        rows given one per rule are used."""
        finding = {"line": 2, "rule": "WSP-20", "quote": ["x"], "problem": "p", "rewrite": "r"}
        dup = [{"rule": r, "applies": True, "why": "w"} for r in ("WSP-15", "WSP-15", "WSP-16", "WSP-17", "WSP-18", "WSP-19")]
        out = self.run_workflow(dict(self.ARGS, stage="check"), {
            "checker": {"findings": [finding], "conditional": dup, "evidence": []},
            "across files": {"conditional": [{"rule": "WSP-13", "applies_to": [], "why": "w"}] * 2,
                             "findings": [], "evidence": []},
            "reader": None})
        self.assertEqual(out["result"]["checkers"][0]["ok"], False)
        self.assertIsNone(out["result"]["cross"])
        rows = dict(self.CHECKER_ROWS, **{"WSP-20": {"applies": True, "why": "A model writes the output."}})
        out = self.run_workflow(dict(self.ARGS, stage="check"), {
            "checker": {"findings": [finding], "conditional": rows, "evidence": []},
            "across files": {"conditional": self.CROSS_ROWS, "findings": [], "evidence": []},
            "reader": None})
        checker = out["result"]["checkers"][0]
        self.assertEqual((checker["ok"], [f["rule"] for f in out["result"]["findings"]]), (True, ["WSP-20"]))
        self.assertEqual([c["rule"] for c in checker["conditional"]], ["WSP-%d" % i for i in range(15, 21)])
        # Round 5, defect 9: the files of a row are the items of the list applies_to.
        self.assertEqual(out["result"]["cross"]["conditional"][1], {"rule": "WSP-14", "why": "IDs."})
        self.assertEqual(out["result"]["applies_to"], [{"rule": "WSP-14", "path": "specs/a.md"}])


class EndToEnd(Base):
    """AUD-E4, AUD-E11, AUD-46: prepare, filter and render together keep the quote byte for byte."""

    def test_pipeline(self):
        lines = ["# Shipping"] + ["x"] * 5 + ["- Large orders get free shipping,", "  etc."] + ["y"] * 3 + \
                ["Large orders get free shipping, etc."]
        self.write("specs/shipping.md", "\n".join(lines) + "\n")
        _, prep = self.prepare()
        kept = self.json_cmd("filter", {"repo_root": prep["repo_root"], "selected": prep["selected"], "findings": [
            {"path": "specs/shipping.md", "line": 12, "rule": "WSP-2", "quote": ["Large orders get free shipping, etc."],
             "problem": "p", "rewrite": "r"},
            {"path": "specs/shipping.md", "line": 7, "rule": "WSP-2", "quote": ["- Large orders get free shipping,", "  etc."],
             "problem": "p", "rewrite": "r"},
            {"path": "specs/shipping.md", "line": 3, "rule": "WSP-2", "quote": ["invented"], "problem": "p", "rewrite": "r"},
        ]})["findings"]
        out = self.json_cmd("render", {"repo_root": prep["repo_root"], "n": prep["n"], "s": prep["s"], "mode": prep["mode"],
                                       "checked": prep["selected"], "selected": prep["selected"],
                                       "spec_files": prep["spec_files"], "findings": kept,
                                       "conditional": [], "questions": [], "not_checked": []})
        self.assertIn("- specs/shipping.md:7 · WSP-2\n  > - Large orders get free shipping,\n  >   etc.\n", out)
        self.assertIn("- specs/shipping.md:12 · WSP-2\n  > Large orders get free shipping, etc.\n", out)
        self.assertNotIn("invented", out)
        self.assertIn(": 1 of 1 selected spec file checked, 2 findings. Spec set: 1 spec file. Mode: session.\n", out)



def case_insensitive(folder):
    """Whether the file system of `folder` matches names case-insensitively."""
    probe = os.path.join(folder, "CaseProbe")
    open(probe, "w").close()
    try:
        return os.path.exists(os.path.join(folder, "caseprobe"))
    finally:
        os.remove(probe)


class RoundThreePrepare(Base):
    """Round 3 defects of prepare (AUD-12, AUD-40, AUD-42)."""

    def test_two_index_names_for_one_file(self):
        """AUD-12, AUD-24, AUD-36 (round 3, defect 1): two case variants of one name in git's index are one
        file of the working tree: listed once, counted once, and the threshold counts it once."""
        if not case_insensitive(self.repo):
            self.skipTest("the file system matches names case-sensitively")
        for name in ("a", "b", "c"):
            self.write("specs/%s.md" % name, "# %s\n\nOne two three.\n" % name)
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "x")
        blob = subprocess.run(["git", "hash-object", "-w", "specs/a.md"], cwd=self.repo, check=True,
                              stdout=subprocess.PIPE).stdout.decode().strip()
        git(self.repo, "update-index", "--add", "--cacheinfo", "100644,%s,specs/A.md" % blob)
        _, out = self.prepare()
        self.assertEqual((out["spec_files"], out["n"], out["mode"]),
                         (["specs/a.md", "specs/b.md", "specs/c.md"], 3, "session"))
        self.assertEqual(sorted(out["word_counts"]), ["specs/a.md", "specs/b.md", "specs/c.md"])
        _, out = self.prepare("specs/A.md")
        self.assertEqual(out["selected"], ["specs/a.md"])

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root searches every folder")
    def test_folder_git_cannot_search(self):
        """AUD-42, AUD-12 (round 3, defect 2): a folder that git cannot open for files not yet committed is
        reported, never silently left out; a folder that R62 excludes is not."""
        self.write("specs/a.md", "# a\n")
        self.write("locked/b.md", "# b\n")
        self.write(".hidden/c.md", "# c\n")
        for folder in ("locked", ".hidden"):
            path = os.path.join(self.repo, folder)
            os.chmod(path, 0)
            self.addCleanup(os.chmod, path, stat.S_IRWXU)
        _, out = self.prepare()
        self.assertEqual((out["spec_files"], out["unsearchable"]), (["specs/a.md"], ["locked/"]))
        report = self.json_cmd("render", {
            "repo_root": out["repo_root"], "n": out["n"], "s": out["s"], "mode": out["mode"],
            "spec_files": out["spec_files"], "selected": out["selected"], "unreadable": out["unreadable"],
            "unsearchable": out["unsearchable"], "checked": out["selected"], "findings": []})
        self.assertTrue(report.endswith("## Not checked\n\n- locked/ — could not be searched\n"), report)

    def test_name_too_long_or_looping_link(self):
        """AUD-40 (round 3, defect 3): a path that cannot exist, a name too long or a looping symbolic link,
        is `no such file or folder`, also outside a repository."""
        self.write("a.md", "# a\n")
        long_name = "x" * 300
        self.assertEqual(self.prepare(long_name), (1, "specs-management:check-writing: %s: no such file or folder\n" % long_name))
        os.symlink("loop2", os.path.join(self.repo, "loop1"))
        os.symlink("loop1", os.path.join(self.repo, "loop2"))
        self.assertEqual(self.prepare("loop1"), (1, "specs-management:check-writing: loop1: no such file or folder\n"))
        outside = os.path.join(self.tmp, "outside")
        os.makedirs(outside)
        self.assertEqual(self.prepare(long_name, cwd=outside),
                         (1, "specs-management:check-writing: %s: no such file or folder\n" % long_name))


class RoundThreeWords(unittest.TestCase):
    """Round 3 defects of the word count (AUD-36)."""

    def test_list_item_fence_and_indented_code_after_heading(self):
        """AUD-36 (round 3, defect 4): a line indented less than a list item's fence ends the item and its fence;
        indented lines right after a heading or a closing fence are an indented code block."""
        self.assertEqual(check_writing.count_words(b"- item\n  ```\n  code\n\nUno dos tres cuatro cinco seis siete ocho.\n"), 9)
        self.assertEqual(check_writing.count_words(b"- item\n  ```\n  code\n  ```\n  still item\n"), 3)
        self.assertEqual(check_writing.count_words(b"# Title\n    alpha beta gamma\n"), 1)
        self.assertEqual(check_writing.count_words(b"```\nx\n```\n    alpha beta gamma\n"), 0)
        self.assertEqual(check_writing.count_words(b"Para\n    continued line\n"), 3)

    def test_byte_order_mark_before_fence(self):
        """AUD-36, term "Line" (round 3, defect 17): a byte order mark before a fence on line 1 changes no count."""
        body = b"```\n" + b"the code word here\n" * 5 + b"```\n\n" + "los pedidos grandes tienen envío gratis\n".encode() * 5
        self.assertEqual(check_writing.count_words(body), 30)
        self.assertEqual(check_writing.count_words(b"\xef\xbb\xbf" + body), 30)
        self.assertEqual(check_writing.count_words(b"\xef\xbb\xbf    indented code only\n"), 0)

    def test_more_unspaced_scripts(self):
        """AUD-36 (round 3, defect 12): each Khmer, Lao, Myanmar or Tibetan letter counts as one word."""
        for text in ("ភាសាខ្មែរ", "ພາສາລາວ", "မြန်မာဘာသာ", "བོད་ཡིག"):
            letters = sum(1 for ch in text if ch.isalpha())
            self.assertGreater(letters, 2, text)
            self.assertEqual(check_writing.count_words(text.encode()), letters, text)


class RoundThreeFilterRender(Base):
    """Round 3 defects of filter and render (AUD-19, AUD-17, AUD-33, AUD-30)."""

    def setUp(self):
        super().setUp()
        self.write("specs/members.md", "# Members\n\nMember: a person with a paid membership card.\n")
        self.write("specs/orders.md", "# Orders\n\nOrders are paid online.\n\n"
                   "A customer with a card gets 10% off an order of 100.00 EUR or more.\n")
        self.spec = ["specs/members.md", "specs/orders.md"]

    def test_cross_rewrite_follows_the_place(self):
        """AUD-19, AUD-20 (round 3, defect 5): the placed finding carries the rewrite of the place it is
        reported at, never a rewrite written for another place (the live WSP-3 finding)."""
        f = {"rule": "WSP-3", "problem": "A customer with a card is a synonym of member.", "involved": [
            {"path": "specs/orders.md", "line": 5,
             "quote": ["A customer with a card gets 10% off an order of 100.00 EUR or more."],
             "rewrite": "A member must get 10% off an order of 100.00 EUR or more."},
            {"path": "specs/members.md", "line": 3, "quote": ["Member: a person with a paid membership card."],
             "rewrite": "Member: a person with a paid membership card."}]}
        out = self.json_cmd("filter", {"repo_root": self.repo, "spec_files": self.spec, "selected": self.spec,
                                       "findings": [f]})
        got = out["findings"][0]
        self.assertEqual((got["path"], got["line"], got["rewrite"], got["see_also"]),
                         ("specs/members.md", 3, "Member: a person with a paid membership card.", ["specs/orders.md:5"]))
        out = self.json_cmd("filter", {"repo_root": self.repo, "spec_files": self.spec, "selected": ["specs/orders.md"],
                                       "findings": [f]})
        self.assertEqual(out["findings"][0]["rewrite"], "A member must get 10% off an order of 100.00 EUR or more.")

    def report(self, **extra):
        data = {"repo_root": self.repo, "n": 2, "s": 2, "mode": "session", "spec_files": self.spec,
                "selected": self.spec, "checked": self.spec, "findings": []}
        data.update(extra)
        return data

    def test_spc13_row_every_selected_file_or_none(self):
        """AUD-17 (round 3, defect 7): a WSP-13 row that lists some selected files lists every selected file."""
        out = self.json_cmd("render", self.report(conditional=[
            {"rule": "WSP-13", "applies_to": ["specs/orders.md"], "why": "w"}]))
        self.assertIn("| WSP-13 | specs/members.md, specs/orders.md | w |\n", out)

    def test_rewrite_items_separator(self):
        """AUD-33, AUD-50 (round 3, defect 14): a rewrite's items are joined by ` ¶ `, which no item holds, so
        an item that holds `; ` stays one item."""
        self.assertEqual(check_writing.rewrite_line("Parking must cost 2.00 EUR per hour.\n- parking must be free on Sundays;"),
                         "Parking must cost 2.00 EUR per hour. ¶ - parking must be free on Sundays;")

    def test_output_in_parts(self):
        """AUD-30, AUD-38 (round 3, defect 15): filter's output is compact, its dropped entries hold only
        index and reason, and a long report or filter output comes in parts of at most 25000 characters
        that join into the whole."""
        line = "A customer with a card gets 10% off an order of 100.00 EUR or more."
        findings = [{"path": "specs/orders.md", "line": 5, "rule": "WSP-2", "quote": [line],
                     "problem": "p%d %s" % (i, "x" * 300), "rewrite": "r " + "y" * 300} for i in range(120)]
        findings.append({"path": "specs/orders.md", "line": 99, "rule": "WSP-2", "quote": ["x"], "problem": "p",
                         "rewrite": "r"})
        data = {"repo_root": self.repo, "spec_files": self.spec, "selected": self.spec, "findings": findings}
        status, out, err = self.run_script("filter", stdin=json.dumps(data).encode())
        self.assertEqual(status, 0, err)
        self.assertLessEqual(len(out), 25000)
        first = json.loads(out)
        self.assertNotIn("\n ", out)
        self.assertEqual(first["dropped"], [{"index": 120, "reason": "line does not exist"}])
        parts, kept, verify = first["parts"], [], []
        self.assertGreater(parts, 1)
        for k in range(1, parts + 1):
            status, out, err = self.run_script("filter", "--part", str(k), stdin=json.dumps(data).encode())
            self.assertEqual(status, 0, err)
            self.assertLessEqual(len(out), 25000)
            got = json.loads(out)
            self.assertEqual((got["part"], got["parts"]), (k, parts))
            kept += got["findings"]
            verify += got["verify"]
        whole = check_writing.filter_findings(json.loads(json.dumps(data)))
        self.assertEqual((kept, verify), (whole["findings"], whole["verify"]))
        rdata = dict(self.report(findings=kept), link_reports=[], links_not_checked=None)
        status, out, err = self.run_script("render", stdin=json.dumps(rdata).encode())
        self.assertEqual(status, 0, err)
        head, _, rest = out.partition("\n")
        self.assertRegex(head, r"^\[part 1 of \d+, run [0-9a-f]{12}\]$")
        total = int(head.split()[3][:-1])
        run = head.split()[-1][:-1]
        report = rest
        for k in range(2, total + 1):
            status, out, err = self.run_script("render", "--part", str(k), stdin=json.dumps(rdata).encode())
            self.assertEqual(status, 0, err)
            self.assertLessEqual(len(out), 25000 + 20)
            head, _, rest = out.partition("\n")
            self.assertEqual(head, "[part %d of %d, run %s]" % (k, total, run))
            report += rest
        self.assertEqual(report, check_writing.render(json.loads(json.dumps(rdata))))
        # A report that fits is printed whole, with no part line.
        out = self.json_cmd("render", self.report())
        self.assertTrue(out.startswith("Check of writing of "))


@unittest.skipIf(NODE is None, "node is not installed")
class RoundThreeWorkflow(unittest.TestCase):
    """Round 3 defects of workflow.js (AUD-8, AUD-17, AUD-19, AUD-21, term "Non-binding text")."""

    ARGS, run_workflow = WorkflowScript.ARGS, WorkflowScript.run_workflow
    CHECKER_ROWS = RoundTwoWorkflow.CHECKER_ROWS

    def test_spc13_every_selected_file_or_none(self):
        """AUD-17 (round 3, defect 7): a WSP-13 decision for some selected files holds for every selected
        file, so no checker's WSP-13 finding is dropped for a file left out of the list."""
        args = dict(self.ARGS, stage="check", selected=["specs/a.md", "specs/b.md", "specs/c.md"])
        finding = {"line": 1, "rule": "WSP-13", "quote": ["x"], "problem": "p", "rewrite": "r"}
        out = self.run_workflow(args, {
            "checker": {"findings": [finding], "conditional": self.CHECKER_ROWS, "evidence": []},
            "across files": {"conditional": {"WSP-13": {"applies_to": ["/r/specs/a.md"], "why": "Large."},
                                             "WSP-14": {"applies_to": [], "why": "No."}},
                             "findings": [], "evidence": []},
            "reader": None})
        # Round 5, defect 9: the files of a row are the items of the list applies_to.
        self.assertEqual([x["path"] for x in out["result"]["applies_to"] if x["rule"] == "WSP-13"],
                         ["specs/a.md", "specs/b.md", "specs/c.md"])
        self.assertEqual([f["path"] for f in out["result"]["findings"]], ["specs/a.md", "specs/b.md", "specs/c.md"])

    def test_cross_place_rewrite_and_prompts(self):
        """AUD-19 (round 3, defect 5): each involved place carries its own rewrite; AUD-17 (defect 8): a
        reference in another file shows WSP-14's condition; AUD-8 (defect 13), the term "Non-binding text"
        (defect 16), AUD-21 (defect 11) and the term "Involved place" (defect 9) reach the agents."""
        place = {"path": "/r/specs/a.md", "line": 1, "quote": ["x"], "rewrite": "rx"}
        out = self.run_workflow(dict(self.ARGS, stage="check"), {
            "checker": {"findings": [], "conditional": self.CHECKER_ROWS, "evidence": []},
            "across files": {"conditional": {"WSP-13": {"applies_to": [], "why": "w"},
                                             "WSP-14": {"applies_to": [], "why": "w"}},
                             "findings": [{"rule": "WSP-3", "problem": "p", "involved": [place]}], "evidence": []},
            "reader": None})
        self.assertEqual(out["result"]["findings"],
                         [{"rule": "WSP-3", "problem": "p",
                           "involved": [{"path": "specs/a.md", "line": 1, "quote": ["x"], "rewrite": "rx"}]}])
        cross, checker = out["prompts"]["across files"], out["prompts"]["checker specs/a.md"]
        self.assertIn("refers to an individual statement of", cross)
        self.assertIn("first line of each statement that such a reference points to", cross)
        for prompt in (cross, checker):
            self.assertIn(".claude/", prompt)
            self.assertIn("each translation of one of them into the language of the file that holds it", prompt)
            self.assertIn(" ¶ ", prompt)
        self.assertIn("what is out of scope, what must never happen, the convention for binding words", checker)


class RoundThreeSkill(unittest.TestCase):
    """Round 3 defect 6 (AUD-26, AUD-44, AUD-19): SKILL.md's stop path normalises the agents' results as
    workflow.js does, so reader items outside the selected files and absolute applies_to paths never reach render."""

    def test_stop_path_normalises_like_workflow(self):
        with open(os.path.join(PLUGIN, "use-cases", "check-writing", "SKILL.md"), encoding="utf-8") as f:
            skill = f.read()
        stop = " ".join(skill[skill.index("When the user stops the workflow task"):skill.index("## 5. Render")].split())
        for text in ("relative to `repo_root`", "only the items of the selected files",
                     "only the selected files, each once", "every selected file or none"):
            self.assertIn(text, stop)


class RoundFourWords(unittest.TestCase):
    """Round 4 defects of the word count (AUD-36)."""

    def test_stray_backtick_stays_in_its_block(self):
        """AUD-36 (round 4, defect 1): a code span cannot cross a list item, a heading or a table cell, so a
        stray backtick never pairs with one of the next item, line or row and never hides the prose between."""
        count = check_writing.count_words
        self.assertEqual(count(b"- AUD-1. a stray ` backtick here\n- one two three four five six seven eight nine ten\n"
                               b"- AUD-3. uses `x` here\n"), 18)
        self.assertEqual(count(b"# Title with ` tick\none two three four five `x`\n"), 8)
        self.assertEqual(count(b"| a ` b | c |\n|---|---|\n| one two three four | `x` |\n"), 7)
        # A code span inside one list item or cell is still left out.
        self.assertEqual(count(b"- one `two three` four\n| a `b c` |\n|---|\n"), 3)

    def test_combining_marks_belong_to_their_word(self):
        """AUD-36 (round 4, defect 2): vowel signs, viramas, harakat and niqqud do not split a word."""
        for text, words in (("हिन्दी में लिखा गया नियम", 5), ("தமிழ் மொழி விதி", 3), ("قَالَ الْمُعَلِّمُ", 2),
                            ("שָׁלוֹם עוֹלָם", 2), ("the rule is written here", 5)):
            self.assertEqual(check_writing.count_words(text.encode()), words, text)


class RoundFourPrepare(Base):
    """Round 4 defects of prepare (AUD-13, AUD-42, AUD-38)."""

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root searches every folder")
    def test_folder_argument_below_folder_that_cannot_be_searched(self):
        """AUD-13, AUD-42 (round 4, defect 3): a folder argument below a folder that cannot be searched
        selects the tracked spec files under it, listed as could not be read."""
        self.write("locked/inner/a.md", "# a\n")
        self.write("locked/inner2.md", "# x\n")
        self.write("b.md", "# b\n")
        git(self.repo, "add", "-A")
        locked = os.path.join(self.repo, "locked")
        os.chmod(locked, 0)
        self.addCleanup(os.chmod, locked, stat.S_IRWXU)
        status, out = self.prepare("--", "locked/inner")
        self.assertEqual(status, 0, out)
        self.assertEqual((out["selected"], out["unreadable"]),
                         (["locked/inner/a.md"], ["locked/inner/a.md", "locked/inner2.md"]))
        status, out = self.prepare("--", "locked/inner/a.md")
        self.assertEqual((status, out["selected"]), (0, ["locked/inner/a.md"]))
        self.assertEqual(self.prepare("--", "locked/none")[0], 1)

    def test_output_in_parts(self):
        """AUD-38 (round 4, defect 9): prepare's output for a large spec set comes in parts of at most 25000
        characters, each with the same run, that join list by list into the whole."""
        for i in range(400):
            self.write("docs/architecture/decisions/adr-%04d-some-decision.md" % i, "# Decision %d\n" % i)
        status, out, err = self.run_script("prepare")
        self.assertEqual(status, 0, err)
        self.assertLessEqual(len(out), 25000)
        first = json.loads(out)
        self.assertGreater(first["parts"], 1)
        joined = {k: ([] if isinstance(v, list) else {}) for k, v in first.items() if isinstance(v, (list, dict))}
        for k in range(1, first["parts"] + 1):
            status, out, err = self.run_script("prepare", "--part", str(k))
            self.assertEqual(status, 0, err)
            self.assertLessEqual(len(out), 25000)
            got = json.loads(out)
            self.assertEqual((got["part"], got["run"], got["n"], got["mode"]), (k, first["run"], 400, "workflow"))
            for key, value in joined.items():
                value.update(got[key]) if isinstance(value, dict) else value.extend(got[key])
        self.assertEqual(len(joined["spec_files"]), 400)
        self.assertEqual(joined["selected"], joined["spec_files"])
        self.assertEqual(len(joined["word_counts"]), 400)
        self.assertEqual(self.run_script("prepare", "--part", str(first["parts"] + 1))[0], 2)
        # A path such as --part after -- is an argument, not an option.
        self.assertEqual(self.prepare("--", "--part")[0], 1)


class RoundFourFilterRender(Base):
    """Round 4 defects of filter and render (AUD-19, AUD-29, AUD-31, AUD-46, AUD-30, AUD-38, term "Quote")."""

    def setUp(self):
        super().setUp()
        self.write("specs/a.md", "1\n2\n3\nMember: a person with a card.\n")
        self.write("specs/b.md", "# B\n" + "x\n" * 7 + "A user may borrow 5 books.\n")
        self.write("specs/c.md", "# C\nA user pays fees.\n")
        self.spec = ["specs/a.md", "specs/b.md", "specs/c.md"]

    def filter(self, findings, selected=("specs/a.md",), **extra):
        data = {"repo_root": self.repo, "spec_files": self.spec, "selected": list(selected), "findings": findings}
        data.update(extra)
        return self.json_cmd("filter", data)

    def render_input(self, findings, checked=("specs/a.md",), **extra):
        data = {"repo_root": self.repo, "n": 3, "s": len(checked), "mode": "session", "spec_files": self.spec,
                "selected": list(checked), "checked": list(checked), "findings": findings}
        data.update(extra)
        return data

    def across(self, a_quote=("Member: a person with a card.",), b_line=9, b_quote=("A user may borrow 5 books.",),
               c_line=2, c_quote=("A user pays fees.",)):
        return {"rule": "WSP-3", "problem": "user is a synonym of member.", "involved": [
            {"path": "specs/a.md", "line": 4, "quote": list(a_quote), "rewrite": "Member: a person with a card."},
            {"path": "specs/b.md", "line": b_line, "quote": list(b_quote), "rewrite": "A member may borrow 5 books."},
            {"path": "specs/c.md", "line": c_line, "quote": list(c_quote), "rewrite": "A member pays fees."}]}

    def test_fabricated_findings_refused(self):
        """AUD-46, AUD-29 step 2 (round 4, defect 4): a made-up sha256 never lets a finding skip step 2;
        line 0 and an empty quote are always refused."""
        base = {"path": "specs/a.md", "rule": "WSP-2", "problem": "p", "rewrite": "r"}
        for f in (dict(base, line=0, quote=["text that is nowhere"], sha256=""),
                  dict(base, line=77, quote=[], sha256="abc"),
                  dict(base, line=4, quote=["Member: a person with no card."], sha256="0" * 64, check="0" * 64)):
            status, out, err = self.run_script("render", stdin=json.dumps(self.render_input([f])).encode())
            self.assertEqual(status, 2, (f, out))
            self.assertIn("AUD-29 step 2", err)

    def test_involved_place_quotes_checked(self):
        """AUD-19 (round 4, defect 13): a place whose quote does not match the file is left out before the
        finding is placed, so a wrong line never reaches See also and a wrong first place never drops it."""
        out = self.filter([self.across(b_line=8, c_line=1)])
        self.assertEqual(out["findings"][0]["see_also"], [])
        out = self.filter([self.across(a_quote=("Member: a person with a cart.",))],
                          selected=self.spec, checked=self.spec)
        got = out["findings"][0]
        self.assertEqual((got["path"], got["line"], got["see_also"]), ("specs/b.md", 9, ["specs/c.md:2"]))

    def test_rewrite_of_every_place_that_changes(self):
        """AUD-19, AUD-20, AUD-E9 (round 4, defect 12): a finding across files keeps the rewrite of each other
        place that needs a change, shown in a `Rewrite at` line in See also order; a place whose rewrite is its
        quote gets none."""
        out = self.filter([self.across()])
        got = out["findings"][0]
        self.assertEqual((got["path"], got["line"], got["see_also"]), ("specs/a.md", 4, ["specs/b.md:9", "specs/c.md:2"]))
        self.assertEqual(got["rewrites"], [{"place": "specs/b.md:9", "rewrite": "A member may borrow 5 books."},
                                           {"place": "specs/c.md:2", "rewrite": "A member pays fees."}])
        report = self.json_cmd("render", self.render_input([dict(got, verified=True)]))
        self.assertIn("  Rewrite: Member: a person with a card.\n  See also: specs/b.md:9, specs/c.md:2\n"
                      "  Rewrite at specs/b.md:9: A member may borrow 5 books.\n"
                      "  Rewrite at specs/c.md:2: A member pays fees.\n", report)

    def test_report_shows_the_file_line(self):
        """AUD-31, term "Quote" (round 4, defect 6): the report shows each quote line as the file holds it,
        never a CR or a BOM that a matching quote added."""
        self.write("specs/a.md", b"\xef\xbb\xbf# A\r\nline two\r\n")
        f = {"path": "specs/a.md", "rule": "WSP-2", "problem": "p", "rewrite": "r"}
        out = self.filter([dict(f, line=2, quote=["line two\r"]), dict(f, line=1, rule="WSP-4", quote=["﻿# A", "line \r\r\rtwo"])])
        self.assertEqual([x["quote"] for x in out["findings"]], [["line two"], ["# A", "line two"]])
        raw = [dict(f, line=2, quote=["line two\r"])]
        report = self.json_cmd("render", self.render_input(raw))
        self.assertIn("  > line two\n", report)
        self.assertNotIn("\\u000d", report)

    def test_quote_with_unicode_spaces_and_decomposed_accents(self):
        """Term "Quote", AUD-29 step 2 (round 4, defect 19): a quote matches when it differs from the file
        only by a space separator such as U+00A0, a format character or the Unicode normalization form."""
        self.write("specs/a.md", "# Prix\n\nLes grosses commandes ont la livraison gratuite : etc.\n"
                   "Livraison en 5 jours.\nenvío y Añadir​.\n")
        f = {"path": "specs/a.md", "rule": "WSP-2", "problem": "p", "rewrite": "r"}
        out = self.filter([dict(f, line=3, quote=["Les grosses commandes ont la livraison gratuite : etc."]),
                           dict(f, line=4, rule="WSP-4", quote=["Livraison en 5 jours."]),
                           dict(f, line=5, rule="WSP-5", quote=["envío y Añadir."]),
                           dict(f, line=5, rule="WSP-6", quote=["envio y Anadir."])])
        self.assertEqual([x["rule"] for x in out["findings"]], ["WSP-2", "WSP-4", "WSP-5"])
        self.assertEqual(out["findings"][0]["quote"], ["Les grosses commandes ont la livraison gratuite : etc."])
        self.assertEqual([d["reason"] for d in out["dropped"]], ["quote differs from the file"])

    def test_non_ascii_output_as_it_is(self):
        """AUD-29 step 5, AUD-31 (round 4, defect 7): filter prints non-ASCII text as it is, so the session
        copies it verbatim, and render repairs a mis-copied quote that `check` proves, never dropping it."""
        self.write("specs/a.md", "# 訂單\n系統必須保存訂單。\n")
        status, out, err = self.run_script("filter", stdin=json.dumps(
            {"repo_root": self.repo, "spec_files": self.spec, "selected": ["specs/a.md"], "findings": [
                {"path": "specs/a.md", "line": 2, "rule": "WSP-2", "quote": ["系統必須保存訂單。"],
                 "problem": "問題", "rewrite": "系統必須保存每張訂單。"}]}).encode())
        self.assertEqual(status, 0, err)
        self.assertIn("系統必須保存訂單。", out)
        self.assertNotIn("\\u", out)
        kept = json.loads(out)["findings"]
        miscopied = [dict(kept[0], quote=["系統必須保存訂单。"], verified=True)]
        report = self.json_cmd("render", self.render_input(miscopied))
        self.assertIn("  > 系統必須保存訂單。\n", report)

    def test_long_finding_in_pieces_and_long_line_split(self):
        """AUD-38, AUD-30 (round 4, defect 5): a finding longer than a part comes in pieces, a line of the
        report longer than a part is split, so that every part holds at most 25000 characters."""
        rows = ["| row %d | value %d |" % (i, i) for i in range(1500)]
        self.write("specs/a.md", "# T\n" + "\n".join(rows) + "\n")
        rewrite = " ¶ ".join("- Row %d must have value %d." % (i, i) for i in range(1500))
        small = {"path": "specs/a.md", "line": 1, "rule": "WSP-4", "quote": ["# T"], "problem": "p", "rewrite": "r"}
        data = {"repo_root": self.repo, "spec_files": self.spec, "selected": ["specs/a.md"], "findings": [
            small, {"path": "specs/a.md", "line": 2, "rule": "WSP-2", "quote": rows, "problem": "p", "rewrite": rewrite},
            dict(small, rule="WSP-5")]}
        status, out, err = self.run_script("filter", stdin=json.dumps(data).encode())
        self.assertEqual(status, 0, err)
        first = json.loads(out)
        findings, verify, pieces = [], [], []
        for k in range(1, first["parts"] + 1):
            status, out, err = self.run_script("filter", "--part", str(k), stdin=json.dumps(data).encode())
            self.assertEqual(status, 0, err)
            self.assertLessEqual(len(out), 25000)
            head, _, rest = out.partition("\n")
            got = json.loads(head)
            self.assertEqual(got["run"], first["run"])
            findings += got["findings"]
            verify += got["verify"]
            if "piece" in got:
                pieces.append(rest[:-1])
                if got["piece"]["number"] == got["piece"]["of"]:
                    findings.append(json.loads("".join(pieces)))
                    pieces = []
        whole = check_writing.filter_findings(json.loads(json.dumps(data)))
        self.assertEqual((findings, verify), (whole["findings"], whole["verify"]))
        rdata = dict(self.render_input(findings), link_reports=[], links_not_checked=None)
        status, out, err = self.run_script("render", stdin=json.dumps(rdata).encode())
        self.assertEqual(status, 0, err)
        total = int(out.split("\n", 1)[0].split()[3][:-1])
        report, continued = "", False
        for k in range(1, total + 1):
            status, out, err = self.run_script("render", "--part", str(k), stdin=json.dumps(rdata).encode())
            self.assertEqual(status, 0, err)
            self.assertLessEqual(len(out), 25000)
            head, _, rest = out.partition("\n")
            continued = continued or head.endswith(", continues the line]")
            report += rest
        self.assertTrue(continued)
        self.assertEqual(report, check_writing.render(json.loads(json.dumps(rdata))))

    def test_parts_carry_the_run(self):
        """AUD-41 (round 4, defect 8): the parts of one output carry the same run, and the parts of an output
        computed after another session changed a file carry another, so they are never joined."""
        findings = [{"path": "specs/a.md", "line": 4, "rule": "WSP-2", "quote": ["Member: a person with a card."],
                     "problem": "p%d %s" % (i, "x" * 300), "rewrite": "r " + "y" * 300} for i in range(100)]
        data = json.dumps({"repo_root": self.repo, "spec_files": self.spec, "selected": ["specs/a.md"],
                           "findings": findings}).encode()
        runs = {json.loads(self.run_script("filter", "--part", str(k), stdin=data)[1])["run"] for k in (1, 2)}
        self.assertEqual(len(runs), 1)
        self.write("specs/a.md", "1\n2\n3\nMember: a person with a card.\nAdded.\n")
        self.assertNotIn(json.loads(self.run_script("filter", "--part", "2", stdin=data)[1])["run"], runs)


@unittest.skipIf(NODE is None, "node is not installed")
class RoundFourWorkflow(unittest.TestCase):
    """Round 4 defects of workflow.js (AUD-38, AUD-26, AUD-21, AUD-18, term "Involved place")."""

    ARGS, run_workflow = WorkflowScript.ARGS, WorkflowScript.run_workflow
    CHECKER_ROWS = RoundTwoWorkflow.CHECKER_ROWS
    CROSS = {"conditional": {"WSP-13": {"applies_to": [], "why": "w"}, "WSP-14": {"applies_to": [], "why": "w"}},
             "findings": [], "evidence": []}

    def test_check_result_in_parts(self):
        """AUD-38 (round 4, defect 11): the check stage's result comes in parts of at most about 20000
        characters, each with the same run, that join list by list; a behaviour that one reader lists alone,
        which is never WSP-Q2 evidence (AUD-26), is left out."""
        findings = [{"line": 1, "rule": "WSP-2", "quote": ["x" * 200], "problem": "p" * 200, "rewrite": "r" * 200}] * 40
        a = {"behaviours": [{"path": "specs/a.md", "line": 1, "behaviour": "A"},
                            {"path": "specs/a.md", "line": 2, "behaviour": "only A"}], "two_readings": [], "gaps": []}
        b = {"behaviours": [{"path": "specs/a.md", "line": 1, "behaviour": "B"}], "two_readings": [], "gaps": []}
        answers = {"checker": {"findings": findings, "conditional": self.CHECKER_ROWS, "evidence": []},
                   "across files": self.CROSS, "reader A": a, "reader B": b}
        args = dict(self.ARGS, stage="check", selected=["specs/a.md", "specs/b.md", "specs/c.md"])
        first = self.run_workflow(args, answers)["result"]
        self.assertGreater(first["parts"], 1)
        joined = {"findings": [], "behaviours": [], "checkers": []}
        for k in range(1, first["parts"] + 1):
            got = self.run_workflow(dict(args, part=k), answers)["result"]
            self.assertLessEqual(len(json.dumps(got, separators=(",", ":"), ensure_ascii=False)), 20000)
            self.assertEqual((got["run"], got["readers_ok"]), (first["run"], [True, True]))
            for key in joined:
                joined[key] += got[key]
        self.assertEqual(len(joined["findings"]), 120)
        self.assertEqual([x["path"] for x in joined["checkers"]], args["selected"])
        self.assertEqual(joined["behaviours"], [{"reader": 0, "path": "specs/a.md", "line": 1, "behaviour": "A"},
                                                {"reader": 1, "path": "specs/a.md", "line": 1, "behaviour": "B"}])
        self.assertIn("error", self.run_workflow(dict(args, part=first["parts"] + 1), answers))

    def test_prompts(self):
        """Term "Involved place" (round 4, defects 15 and 16), AUD-21 (defect 14), AUD-18 (defect 18): the
        agents get the extended list, the missing-text rule only where it applies, and WSP-T14 for non-binding text."""
        out = self.run_workflow(dict(self.ARGS, stage="check"), {
            "checker": {"findings": [], "conditional": self.CHECKER_ROWS, "evidence": []},
            "across files": self.CROSS, "reader": None})
        cross, checker = out["prompts"]["across files"], out["prompts"]["checker specs/a.md"]
        for text in ("the finding says lacks an identifier", "can collide with no stated winner",
                     "outside literal blocks and user-facing text", "AUD-21 does not apply to a finding across files"):
            self.assertIn(text, cross)
        self.assertNotIn("cites and quotes the heading line of the innermost section", cross)
        self.assertIn("cites and quotes the heading line of the innermost section", checker)
        self.assertIn("WSP-9, WSP-12 and WSP-T14 (AUD-18)", checker)
        item = {"path": "specs/a.md", "line": 3, "lines": 1, "see_also": [], "problem": "p"}
        out = WorkflowScript.verify(self, [dict(item, rule="WSP-14"), dict(item, rule="WSP-1")])
        across, one = (out["prompts"][k] for k in sorted(out["prompts"]))
        self.assertIn("AUD-21 does not apply to it", across)
        self.assertIn("the quote is only the heading of the section", one)
        self.assertIn("WSP-3, WSP-9, WSP-12 or WSP-T14 (AUD-18)", one)



class RoundFiveWords(unittest.TestCase):
    """Round 5 defects of the word count (AUD-36)."""

    def test_setext_thematic_break_and_block_quote(self):
        """AUD-36 (round 5, defect 1): a setext underline and a thematic break end a block, so a stray backtick
        never pairs across them; block-quote markers are left out first, so a heading in a quote is a block and
        a fence in a quote is a literal block."""
        count = check_writing.count_words
        tail = b"uno dos tres cuatro cinco seis siete ocho `x` nueve\n"
        self.assertEqual(count(b"Use the ` key\n=============\n" + tail), 12)
        self.assertEqual(count(b"Use the ` key\n---\n" + tail), 12)
        self.assertEqual(count(b"word ` one\n***\n" + tail), 11)
        self.assertEqual(count(b"> Use the ` key\n> # T\xc3\xadtulo\n> " + tail), 13)
        self.assertEqual(count(b"Prosa.\n\n> ~~~\n> code code code code code code code code code code\n> ~~~\n"), 1)
        # A fence in a block quote ends with the quote; the prose after it counts again.
        self.assertEqual(count(b"> ~~~\n> code code\nafter the quote\n"), 3)
        # A code span inside one quoted paragraph is still left out.
        self.assertEqual(count(b"> one `two three` four\n"), 2)
        # A quoted fence shown inside a fenced block of no quote does not close it.
        self.assertEqual(count(b"Prose.\n```\n> ```\ncode code code\n```\n"), 1)


class RoundFivePrepare(Base):
    """Round 5 defects of prepare (AUD-42)."""

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root reads every folder")
    def test_unreadable_root(self):
        """AUD-42, AUD-12 (round 5, defect 2): when git cannot open the repository root for files not yet
        committed, the root is listed as `./` with could not be searched, never dropped as an R62 dot-folder."""
        self.write("t.md", "# t\n")
        git(self.repo, "add", "t.md")
        self.write("v.md", "# v\n")
        self.write("docs/u.md", "# u\n")
        os.chmod(self.repo, stat.S_IWUSR | stat.S_IXUSR)
        self.addCleanup(os.chmod, self.repo, stat.S_IRWXU)
        status, out = self.prepare()
        self.assertEqual(status, 0, out)
        self.assertEqual((out["spec_files"], out["unsearchable"]), (["t.md"], ["./"]))
        self.assertEqual(check_writing.unsearchable_folders("warning: could not open directory '': Permission denied\n"), ["./"])
        os.chmod(self.repo, stat.S_IRWXU)
        report = self.json_cmd("render", {
            "repo_root": out["repo_root"], "n": out["n"], "s": out["s"], "mode": out["mode"],
            "spec_files": out["spec_files"], "selected": out["selected"], "unreadable": out["unreadable"],
            "unsearchable": out["unsearchable"], "checked": out["selected"], "findings": []})
        self.assertTrue(report.endswith("## Not checked\n\n- ./ — could not be searched\n"), report)


class RoundFiveFilterRender(Base):
    """Round 5 defects of filter and render (AUD-29, AUD-38, AUD-20, AUD-30, AUD-34, terms Line and Quote)."""

    def run_parts(self, command, data):
        """Every part of filter's output, joined as SKILL.md 4a.3 says; each part at most 25000 characters."""
        first, joined, pieces = None, {"findings": [], "verify": [], "dropped": []}, []
        k = 1
        while first is None or k <= first["parts"]:
            status, out, err = self.run_script(command, "--part", str(k), stdin=json.dumps(data).encode())
            self.assertEqual(status, 0, err)
            self.assertLessEqual(len(out), 25000)
            head, _, rest = out.partition("\n")
            got = json.loads(head)
            first = first or got
            self.assertEqual(got["run"], first["run"])
            for key in joined:
                joined[key] += got[key]
            if "piece" in got:
                pieces.append(rest[:-1])
                if got["piece"]["number"] == got["piece"]["of"]:
                    joined["findings"].append(json.loads("".join(pieces)))
                    pieces = []
            k += 1
        return joined

    def test_long_dropped_list_keeps_every_finding(self):
        """AUD-29 step 5, AUD-38 (round 5, defect 4): a dropped list longer than a part never makes filter lose
        the kept findings; every part stays within 25000 characters."""
        self.write("s.md", "line one\nline two\n")
        bad = [{"path": "s.md", "line": 1, "rule": "WSP-2", "quote": ["wrong %d" % i], "problem": "p", "rewrite": "r"}
               for i in range(700)]
        good = [{"path": "s.md", "line": 2, "rule": "WSP-2", "quote": ["line two"], "problem": "good %d" % i,
                 "rewrite": "r"} for i in range(5)]
        data = {"repo_root": self.repo, "spec_files": ["s.md"], "selected": ["s.md"], "findings": bad + good}
        joined = self.run_parts("filter", data)
        self.assertEqual([f["problem"] for f in joined["findings"]], ["good %d" % i for i in range(5)])
        self.assertEqual(len(joined["verify"]), 5)
        self.assertEqual([d["index"] for d in joined["dropped"]], list(range(700)))

    def test_utf16_file(self):
        """Term "Line", AUD-29 step 2 (round 5, defect 5): a file with a UTF-16 byte order mark is read as its
        decoded text, as the Read tool shows it, so a quote copied from it matches."""
        self.write("specs/u16.md", "# Título\nThe system should be fast.\n".encode("utf-16"))
        self.write("specs/u16be.md", b"\xfe\xff" + "# Be\nSecond.\n".encode("utf-16-be"))
        sel = ["specs/u16.md", "specs/u16be.md"]
        data = {"repo_root": self.repo, "spec_files": sel, "selected": sel, "findings": [
            {"path": "specs/u16.md", "line": 2, "rule": "WSP-4", "quote": ["The system should be fast."],
             "problem": "p", "rewrite": "r"},
            {"path": "specs/u16.md", "line": 1, "rule": "WSP-1", "quote": ["# Título"], "problem": "p", "rewrite": "r"},
            {"path": "specs/u16be.md", "line": 2, "rule": "WSP-1", "quote": ["Second."], "problem": "p", "rewrite": "r"}]}
        out = self.json_cmd("filter", data)
        self.assertEqual(out["dropped"], [])
        self.assertEqual([f["quote"] for f in out["findings"]], [["The system should be fast."], ["# Título"], ["Second."]])
        self.assertEqual(check_writing.count_words("one two three\n".encode("utf-16")), 3)

    def test_maximal_subparts(self):
        """Term "Quote", AUD-31 (round 5, defect 6): each maximal subpart of an ill-formed UTF-8 sequence is one
        U+FFFD, as the Read tool shows it, so a quote copied from the Read tool matches and is shown that way."""
        self.write("specs/bytes.md", b"a\xe2\x82b\n\xf0\x9f\x98c\nd\xc0\x80e\n")
        shown = ["a�b", "�c", "d��e"]
        findings = [{"path": "specs/bytes.md", "line": i + 1, "rule": "WSP-2", "quote": [q], "problem": "p", "rewrite": "r"}
                    for i, q in enumerate(shown)]
        data = {"repo_root": self.repo, "spec_files": ["specs/bytes.md"], "selected": ["specs/bytes.md"],
                "findings": findings}
        out = self.json_cmd("filter", data)
        self.assertEqual(out["dropped"], [])
        self.assertEqual([f["quote"] for f in out["findings"]], [[q] for q in shown])
        # The raw bytes, passed as surrogate escapes, match too.
        raw = [b"a\xe2\x82b".decode("utf-8", "surrogateescape")]
        data["findings"] = [dict(findings[0], quote=raw)]
        status, got, err = self.run_script("filter", stdin=json.dumps(data).encode())
        self.assertEqual((status, len(json.loads(got)["findings"])), (0, 1), err)

    def test_finding_of_one_file_has_no_see_also(self):
        """AUD-20, AUD-30 (round 5, defect 14): a See also line belongs only to a finding across files (AUD-19);
        filter gives a finding of one file no See also places."""
        self.write("specs/a.md", "# A\nOne.\nIt is two.\n")
        data = {"repo_root": self.repo, "spec_files": ["specs/a.md"], "selected": ["specs/a.md"], "findings": [
            {"path": "specs/a.md", "line": 3, "rule": "WSP-2", "quote": ["It is two."], "problem": "p", "rewrite": "r",
             "see_also": ["specs/a.md:2"]}]}
        out = self.json_cmd("filter", data)
        self.assertEqual((out["findings"][0]["see_also"], out["verify"][0]["see_also"]), ([], []))

    def test_same_rule_and_line_order(self):
        """AUD-34 (round 5, defect 15): two findings with the same rule and line are ordered by problem, then by
        rewrite, whatever the order they are given in."""
        self.write("specs/a.md", "# A\n")
        base = {"path": "specs/a.md", "line": 1, "rule": "WSP-5", "quote": ["# A"]}
        findings = [dict(base, problem="b", rewrite="r"), dict(base, problem="a", rewrite="z"),
                    dict(base, problem="a", rewrite="y")]
        data = {"repo_root": self.repo, "n": 1, "s": 1, "mode": "session", "spec_files": ["specs/a.md"],
                "selected": ["specs/a.md"], "checked": ["specs/a.md"], "findings": findings}
        one = self.json_cmd("render", data)
        two = self.json_cmd("render", dict(data, findings=list(reversed(findings))))
        self.assertEqual(one, two)
        self.assertLess(one.index("Rewrite: y"), one.index("Rewrite: z"))
        self.assertLess(one.index("Rewrite: z"), one.index("Problem: b"))


class RoundFiveSkill(unittest.TestCase):
    """Round 5 defects of SKILL.md (AUD-40, AUD-41, AUD-30, AUD-37, AUD-44, AUD-43, term "Involved place")."""

    @classmethod
    def setUpClass(cls):
        with open(os.path.join(PLUGIN, "use-cases", "check-writing", "SKILL.md"), encoding="utf-8") as f:
            cls.skill = " ".join(f.read().split())

    def section(self, start, end):
        return self.skill[self.skill.index(start):self.skill.index(end)]

    def test_part_call_after_concurrent_edit(self):
        """AUD-40, AUD-41 (round 5, defect 3): only exit 1 is the whole reply; a --part k call whose output has
        fewer parts now came from another run, which starts again from part 1."""
        rules = self.section("## Rules of every run", "## 1. Prepare")
        self.assertIn("exits 2 with `the output has", rules)
        prepare = self.section("## 1. Prepare", "## 2. Guideline")
        self.assertIn("On exit 1, reply with exactly its output", prepare)
        self.assertNotIn("On a non-zero exit", prepare)

    def test_every_part_without_its_header_and_translated(self):
        """AUD-30, AUD-37 (round 5, defect 7): each part of the report is sent without its [part …] line and
        with its fixed texts translated; never 'as you first read it'."""
        reply = self.skill[self.skill.index("When the first line of `render`'s output"):]
        self.assertNotIn("as you first read it", reply)
        self.assertIn("each part without its `[part …]` line", reply)
        self.assertIn("translated", reply)

    def test_stop_path_gives_checker_path(self):
        """AUD-44, AUD-22 (round 5, defect 8): after a stop, each finding and evidence item of a checker gets
        that checker's file as its path, as workflow.js does."""
        stop = self.section("When the user stops the workflow task", "## 5. Render")
        self.assertIn("each evidence item of `checker <path>` the path `<path>`", stop)

    def test_verify_parts_resume_from_verify(self):
        """AUD-41, AUD-43 (round 5, defect 11): verify part 1 takes the args of the first audit call without
        "part"; its parts 2.. resume from the runId of verify part 1."""
        step4 = self.section("4. When findings remain", "When the user stops the workflow task")
        self.assertIn("without `\"part\"`", step4)
        self.assertIn("the `runId` of this first verify call", step4)

    def test_involved_places_of_the_finding(self):
        """Term "Involved place", AUD-E13 (round 5, defect 12): only the places the finding is about."""
        how = self.section("## 3. How to check", "## 4a. Session mode")
        self.assertIn("every involved place of that finding", how)
        self.assertIn("each statement that the finding says lacks an identifier", how)
        self.assertNotIn("lacks an identifier where WSP-14 applies", how)


def join_workflow_parts(test, run, args, answers, limit=20000):
    """Every part of a workflow stage's result, joined list by list, pieces included (SKILL.md 4b.2)."""
    first = run(args, answers)["result"]
    lists = [k for k, v in first.items() if isinstance(v, list) and k != "readers_ok"]
    joined, pieces = {k: [] for k in lists}, []
    for k in range(1, first["parts"] + 1):
        got = run(dict(args, part=k), answers)["result"]
        test.assertLessEqual(len(json.dumps(got, separators=(",", ":"), ensure_ascii=False)), limit)
        test.assertEqual(got["run"], first["run"])
        for key in lists:
            joined[key] += got[key]
        if "piece" in got:
            pieces.append(got["text"])
            if got["piece"]["number"] == got["piece"]["of"]:
                joined[got["piece"]["list"]].append(json.loads("".join(pieces)))
                pieces = []
    return first, joined


@unittest.skipIf(NODE is None, "node is not installed")
class RoundFiveWorkflow(unittest.TestCase):
    """Round 5 defects of workflow.js (AUD-38, AUD-28, term "Involved place")."""

    ARGS, run_workflow = WorkflowScript.ARGS, WorkflowScript.run_workflow
    CHECKER_ROWS = RoundTwoWorkflow.CHECKER_ROWS

    def test_conditional_rows_split_across_parts(self):
        """AUD-38 (round 5, defect 9): the files of the WSP-13 and WSP-14 rows are list items, not copied into
        every part, so a large spec set gives parts that each stay within the limit."""
        files = ["specs/billing/module-%04d.md" % i for i in range(600)]
        args = dict(self.ARGS, stage="check", spec_files=files, selected=files)
        answers = {"checker": {"findings": [], "conditional": self.CHECKER_ROWS, "evidence": []},
                   "across files": {"conditional": {"WSP-13": {"applies_to": [files[0]], "why": "Large."},
                                                    "WSP-14": {"applies_to": files, "why": "IDs."}},
                                    "findings": [], "evidence": []},
                   "reader": None}
        first, joined = join_workflow_parts(self, self.run_workflow, args, answers)
        self.assertLess(first["parts"], 40)
        self.assertEqual(first["cross"], {"conditional": [{"rule": "WSP-13", "why": "Large."},
                                                          {"rule": "WSP-14", "why": "IDs."}]})
        self.assertEqual(joined["applies_to"], [{"rule": r, "path": p} for r in ("WSP-13", "WSP-14") for p in files])
        self.assertEqual(len(joined["checkers"]), 600)

    def test_item_larger_than_a_part_in_pieces(self):
        """AUD-38, AUD-28 (round 5, defect 10): an item longer than a part comes in pieces, each part within the
        limit, and the pieces joined give the item back."""
        files = ["specs/f%03d.md" % i for i in range(200)]
        involved = [{"path": p, "line": 3, "quote": ["Dieser Satz ist auf Deutsch geschrieben, nicht auf Englisch."],
                     "rewrite": "This sentence is written in English, as the rest of the spec set is."} for p in files]
        args = dict(self.ARGS, stage="check", spec_files=files, selected=files[:2])
        answers = {"checker": {"findings": [], "conditional": self.CHECKER_ROWS, "evidence": []},
                   "across files": {"conditional": {"WSP-13": {"applies_to": [], "why": "w"},
                                                    "WSP-14": {"applies_to": [], "why": "w"}},
                                    "findings": [{"rule": "WSP-3", "problem": "p \"quoted\" \\ text", "involved": involved}],
                                    "evidence": []},
                   "reader": None}
        first, joined = join_workflow_parts(self, self.run_workflow, args, answers)
        self.assertGreater(first["parts"], 1)
        self.assertEqual(joined["findings"], [{"rule": "WSP-3", "involved": involved, "problem": "p \"quoted\" \\ text"}])

    def test_involved_places_of_the_finding(self):
        """Term "Involved place", AUD-E13 (round 5, defect 12): the pass gives only the places its finding is
        about; a statement without identifier is involved only when the finding says it lacks one."""
        out = self.run_workflow(dict(self.ARGS, stage="check"), {
            "checker": {"findings": [], "conditional": self.CHECKER_ROWS, "evidence": []},
            "across files": RoundFourWorkflow.CROSS, "reader": None})
        cross = out["prompts"]["across files"]
        self.assertIn("each statement that the finding says lacks an identifier", cross)
        self.assertIn("every involved place of that finding", cross)
        self.assertNotIn("where WSP-14 applies. An involved place", cross)


class LinksBetweenLayers(Base):
    """AUD-54 to AUD-59, AUD-E14 to AUD-E18: the check of the links between layers 0 and 1."""

    PROJECT = {"project": "p", "repositories": [
        {"owner": "acme", "name": "p-drafts", "layer": 0, "path": "p-drafts"},
        {"owner": "acme", "name": "p-specs", "layer": 1, "path": "p-specs"},
        {"owner": "acme", "name": "p-norms", "layer": 2, "path": "p-norms"}]}

    def setUp(self):
        super().setUp()
        self.project = json.dumps(self.PROJECT, indent=1) + "\n"
        self.layer = {}
        for n, name in ((0, "p-drafts"), (1, "p-specs"), (2, "p-norms")):
            self.layer[n] = self.make(name)

    def make(self, name, project=None):
        work = os.path.join(self.tmp, "proj", name)
        os.makedirs(work)
        git(work, "init", "-q")
        git(work, "remote", "add", "origin", "https://github.com/acme/%s.git" % name)
        self.write("project.json", self.project if project is None else project, work)
        self.write("doc.md", "# Doc\n", work)  # a spec file, so that prepare does not refuse (AUD-40)
        self.commit(work)
        return work

    def commit(self, work, *files):
        for rel, text in files:
            self.write(rel, text, work)
        git(work, "add", "-A")
        git(work, "commit", "-q", "--allow-empty", "-m", "c")

    def check(self, n, *args):
        status, out = self.prepare(*args, cwd=self.layer[n])
        self.assertEqual(status, 0, out)
        return out

    def rendered(self, prep):
        """The report of a run with no findings, from prepare's output."""
        return self.json_cmd("render", {
            "repo_root": prep["repo_root"], "n": prep["n"], "s": prep["s"], "mode": prep["mode"],
            "spec_files": prep["spec_files"], "selected": prep["selected"], "unreadable": prep["unreadable"],
            "unsearchable": prep["unsearchable"], "checked": prep["selected"], "findings": [], "conditional": [],
            "questions": [], "not_checked": [], "link_reports": prep["link_reports"],
            "links_not_checked": prep["links_not_checked"]})

    def process(self, line6="See [Fees (not specified yet)](absent:fees.md)."):
        self.commit(self.layer[1], ("specs/process.md", "# Process\n\n1\n2\n3\n%s\n" % line6))

    def test_absent_link_to_a_draft(self):
        """AUD-E14, AUD-56: an absent link of layer 1 whose link target exists in layer 0 only is not reported."""
        self.process()
        self.commit(self.layer[0], ("specs/fees.md", "# Fees\n"))
        out = self.check(1)
        self.assertEqual((out["link_reports"], out["links_not_checked"]), ([], None))
        self.assertIn("## Links between layers\n\nNone.\n\n## Conditional rules", self.rendered(out))

    def test_absent_link_to_a_deleted_spec(self):
        """AUD-E15, AUD-56 case 2, AUD-57, AUD-58: the report byte for byte; <f> does not count it."""
        self.process()
        out = self.check(1)
        self.assertEqual(out["link_reports"], [{"path": "specs/process.md", "line": 6, "layer": "layer 1", "case": 2,
                                                "link": "[Fees (not specified yet)](absent:fees.md)"}])
        report = self.rendered(out)
        self.assertIn("2 of 2 selected spec files checked, 0 findings.", report)
        self.assertIn(
            "## Links between layers\n\n"
            "- specs/process.md:6 · layer 1\n"
            "  Link: [Fees (not specified yet)](absent:fees.md)\n"
            "  Problem: absent link whose link target exists neither in layer 1 nor in layer 0\n"
            "  Rewrite: delete the whole link, its text and its destination, and rewrite or delete its sentence\n"
            "\n## Conditional rules", report)
        self.assertTrue(report.endswith("## Not checked\n\nNone.\n"))

    def test_absent_link_to_a_promoted_spec(self):
        """AUD-E16, AUD-56 case 1, AUD-57: the rewrite is the plain link of ORC-41, also when layer 0 holds it too."""
        self.process()
        self.commit(self.layer[1], ("specs/fees.md", "# Fees\n"))
        self.commit(self.layer[0], ("specs/fees.md", "# Fees\n"))
        report = self.rendered(self.check(1))
        self.assertIn("- specs/process.md:6 · layer 1\n  Link: [Fees (not specified yet)](absent:fees.md)\n"
                      "  Problem: absent link whose link target exists in layer 1\n  Rewrite: [Fees](fees.md)\n", report)

    def test_broken_link_of_a_draft(self):
        """AUD-E17, AUD-56 case 3: a plain link of layer 0 to no spec of either layer; none when layer 1 holds it."""
        self.commit(self.layer[0], ("drafts/a.md", "# A\n\nUses [B](b.md).\n"))
        report = self.rendered(self.check(0))
        self.assertIn("## Links between layers\n\n- drafts/a.md:3 · layer 0\n  Link: [B](b.md)\n"
                      "  Problem: plain link whose link target exists neither in layer 0 nor in layer 1\n"
                      "  Rewrite: delete the link, or fix its destination\n\n## Conditional rules", report)
        self.commit(self.layer[1], ("drafts/b.md", "# B\n"))
        self.assertEqual(self.check(0)["link_reports"], [])

    def test_repository_with_no_project(self):
        """AUD-E18, AUD-59 condition 1, AUD-35, AUD-42: no refusal; Skipped., and the line of Not checked, last."""
        self.write("specs/a.md", "# A\n")
        status, out = self.prepare()
        self.assertEqual(status, 0, out)
        self.assertEqual((out["link_reports"], out["links_not_checked"]),
                         ([], "project.json is missing or does not have the form of ORC-20"))
        data = dict(out, checked=[], findings=[], not_checked=[{"what": "specs/a.md", "reason": "could not be read"},
                                                              {"pass": "readers"}])
        report = self.json_cmd("render", data)
        self.assertIn("## Links between layers\n\nSkipped.\n\n## Conditional rules", report)
        self.assertTrue(report.endswith(
            "## Not checked\n\n- specs/a.md — could not be read\n- readers (WSP-Q2, WSP-Q3) — a reader failed or did not finish\n"
            "- links between layers — project.json is missing or does not have the form of ORC-20\n"))

    def reason(self, n):
        return self.check(n)["links_not_checked"]

    def test_conditions_in_order(self):
        """AUD-59: each condition with its reason, in order; the check never refuses (AUD-46)."""
        bad = self.make("bad", project="{not json")
        self.layer["bad"] = bad
        self.assertEqual(self.reason("bad"), "project.json is missing or does not have the form of ORC-20")
        self.write("project.json", json.dumps({"repositories": [{"owner": "acme", "layer": 0, "path": "../x"}]}), bad)
        self.assertEqual(self.reason("bad"), "project.json is missing or does not have the form of ORC-20")
        git(self.layer[1], "remote", "set-url", "origin", "https://github.com/acme/other.git")
        self.assertEqual(self.reason(1), "this repository is not in project.json")
        git(self.layer[1], "remote", "remove", "origin")
        self.assertEqual(self.reason(1), "this repository is not in project.json")
        self.assertEqual(self.reason(2), "the repository is not of layer 0 or of layer 1")
        one = json.dumps({"project": "p", "repositories": self.PROJECT["repositories"][:1]})
        self.write("project.json", one, self.layer[0])
        self.assertEqual(self.reason(0), "project.json has no repository of layer 1")
        self.write("project.json", self.project, self.layer[0])
        shutil.rmtree(self.layer[1])
        self.assertEqual(self.reason(0), "acme/p-specs is not at %s" % os.path.join(self.tmp, "proj", "p-specs"))

    def test_no_remote_before_git_2_30(self):
        """AUD-59 condition 2: a git before 2.30 says `fatal: No such remote` (exit 128) for a repository with no
        origin; the reason is the same as with `error:`."""
        fake = os.path.join(self.tmp, "bin")
        os.makedirs(fake)
        self.write("git", "#!/bin/sh\ncase \" $* \" in *\" remote get-url origin \"*)\n"
                   "  echo \"fatal: No such remote 'origin'\" >&2; exit 128;;\nesac\nexec '%s' \"$@\"\n"
                   % shutil.which("git"), base=fake)
        os.chmod(os.path.join(fake, "git"), 0o755)
        status, out = self.prepare(cwd=self.layer[1], env=dict(os.environ, PATH=fake + os.pathsep + os.environ["PATH"]))
        self.assertEqual(status, 0, out)
        self.assertEqual(out["links_not_checked"], "this repository is not in project.json")

    def test_path_that_cannot_be_resolved(self):
        """AUD-59 condition 5, AUD-46: a `path` of layer 1 that is a symlink loop, or holds a NUL, is not found; the
        check does not refuse."""
        os.symlink("loop", os.path.join(self.tmp, "proj", "loop"))
        for bad in ("loop", "a\u0000b"):
            data = json.loads(self.project)
            next(e for e in data["repositories"] if e["layer"] == 1)["path"] = bad
            self.write("project.json", json.dumps(data), self.layer[0])
            reason = self.reason(0)
            self.assertTrue(reason.startswith("acme/p-specs is not at "), reason)

    def test_project_json_differs(self):
        """AUD-59 condition 6, AUD-54: the repository's copy is compared with that of layer 1, as ORC-24 says; the copy
        of layer 1 is that copy, and the other layer's is not read for it."""
        self.write("project.json", self.project + " ", self.layer[0])
        self.assertEqual(self.reason(0), "project.json differs from the copy of layer 1")
        self.assertIsNone(self.reason(1))

    def test_git_fails_in_the_other_layer(self):
        """AUD-59 condition 7: a git command of the check fails; the audit goes on (AUD-40 does not apply)."""
        self.commit(self.layer[1], ("specs/a.md", "# A\n"))
        git_dir = os.path.join(self.layer[0], ".git")
        shutil.rmtree(git_dir)
        with open(git_dir, "w") as f:
            f.write("gitdir: %s\n" % os.path.join(self.tmp, "nowhere"))
        reason = self.reason(1)
        self.assertTrue(reason.startswith("git failed: fatal: not a git repository"), reason)

    def test_other_layer_inside_another_repository(self):
        """AUD-59 condition 7, AUD-55: when the .git of the other layer is no repository, git fails; it never reads
        the tree of a repository that holds the project folder (AUD-46)."""
        self.process()
        git(self.tmp, "init", "-q")
        self.write("specs/fees.md", "# Fees\n", self.tmp)
        git(self.tmp, "add", "--", "specs/fees.md")
        git(self.tmp, "commit", "-q", "-m", "outer")
        git_dir = os.path.join(self.layer[0], ".git")
        shutil.rmtree(git_dir)
        os.mkdir(git_dir)
        out = self.check(1)
        self.assertEqual(out["link_reports"], [])
        self.assertTrue(out["links_not_checked"].startswith("git failed: "), out["links_not_checked"])

    def test_branch_names_a_missing_object(self):
        """AUD-59 condition 7, AUD-55: a branch whose commit is missing is a git failure, in each layer, never an
        empty tree that would report every link (AUD-46)."""
        self.process()
        self.commit(self.layer[0], ("specs/x.md", "[Y](y.md)\n"))
        for n in (0, 1):
            with self.subTest(layer=n):
                ref = subprocess.run(["git", "symbolic-ref", "HEAD"], cwd=self.layer[n], capture_output=True,
                                     text=True, check=True).stdout.strip()
                path = os.path.join(self.layer[n], ".git", *ref.split("/"))
                with open(path) as f:
                    good = f.read()
                with open(path, "w") as f:
                    f.write("1" * 40 + "\n")
                try:
                    for m in (0, 1):
                        out = self.check(m)
                        self.assertEqual(out["link_reports"], [])
                        self.assertTrue(out["links_not_checked"].startswith("git failed: "), out["links_not_checked"])
                finally:
                    with open(path, "w") as f:
                        f.write(good)

    def test_no_lazy_fetch(self):
        """AUD-38: git fetches no missing object of a partial clone."""
        self.assertEqual(check_writing.git_env()["GIT_NO_LAZY_FETCH"], "1")

    def test_what_counts_as_a_link_and_as_existing(self):
        """AUD-56, AUD-54: the destination as the file holds it; working tree read, HEAD for existence; folders exist."""
        lines = [
            "# Process",
            "[A (not specified yet)](absent:../specs/)",       # 2: a folder of layer 1 that holds a file: case 1
            "`[B (not specified yet)](absent:nope.md)`",       # 3: in a code span, not a link
            "[C](absent:nope.md)",                             # 4: absent: without the suffix, neither kind
            "[D (not specified yet)](<absent:x%20y.md>)",      # 5: angle brackets, percent-encoding kept: case 2
            "[E (not specified yet)](absent:../../out.md)",    # 6: outside the repository, no link target
            "[F](nope.md) [G (not specified yet)](https://x)", # 7: plain links of layer 1 and a URI: not reported
            "[H\nI (not specified yet)](absent:uncommitted.md)",  # 8-9: a line feed, shown as \u000a
        ]
        self.commit(self.layer[1], ("specs/process.md", "# x\n"))
        self.write("specs/process.md", "\n".join(lines) + "\n", self.layer[1])  # not committed: read as it is
        self.write("specs/uncommitted.md", "# U\n", self.layer[1])  # in the working tree only: does not exist
        out = self.check(1, "specs/process.md")
        got = [(r["line"], r["case"], r["link"], r.get("plain")) for r in out["link_reports"]]
        self.assertEqual(got, [
            (2, 1, "[A (not specified yet)](absent:../specs/)", "[A](../specs/)"),
            (5, 2, "[D (not specified yet)](<absent:x%20y.md>)", None),
            (8, 2, "[H\nI (not specified yet)](absent:uncommitted.md)", None),
        ])
        self.assertIn("  Link: [H\\u000aI (not specified yet)](absent:uncommitted.md)\n", self.rendered(out))

    def test_order_and_empty_lines(self):
        """AUD-34, AUD-33: by path, then line, then link; one empty line between two reports; only selected files."""
        self.commit(self.layer[0], ("b.md", "[Z](z.md) [Y](y.md)\n"), ("a.md", "x\n[Q](q.md)\n"), ("c.md", "[W](w.md)\n"))
        out = self.check(0)
        self.assertEqual([(r["path"], r["line"], r["link"]) for r in out["link_reports"]],
                         [("a.md", 2, "[Q](q.md)"), ("b.md", 1, "[Y](y.md)"), ("b.md", 1, "[Z](z.md)"), ("c.md", 1, "[W](w.md)")])
        report = self.rendered(out)
        self.assertIn("  Rewrite: delete the link, or fix its destination\n\n- b.md:1 · layer 0\n  Link: [Y](y.md)\n", report)
        self.assertEqual([r["path"] for r in self.check(0, "b.md")["link_reports"]], ["b.md", "b.md"])

    def test_reads_only_and_writes_nothing(self):
        """AUD-55, AUD-38, AUD-46: no file of either repository differs and the plugin gets no __pycache__."""
        self.process()
        self.write("specs/fees.md", "# Fees\n", self.layer[0])  # not committed in layer 0: does not exist
        def state(work):
            out = subprocess.run(["git", "status", "--porcelain", "--ignored"], cwd=work, capture_output=True).stdout
            return out, sorted(os.listdir(work))
        before = {n: state(self.layer[n]) for n in (0, 1)}
        self.assertEqual(self.check(1)["link_reports"][0]["case"], 2)
        self.assertEqual({n: state(self.layer[n]) for n in (0, 1)}, before)
        for folder, _, _ in os.walk(self.plugin):
            self.assertNotEqual(os.path.basename(folder), "__pycache__")

    def test_unborn_head_and_utf8(self):
        """AUD-55, AUD-31, term Line: a layer with no commit has an empty tree; a byte order mark is not on line 1's
        count, an ill-formed UTF-8 sequence is shown as U+FFFD."""
        fresh = os.path.join(self.tmp, "proj", "p-drafts")
        shutil.rmtree(fresh)
        os.makedirs(fresh)
        git(fresh, "init", "-q")
        git(fresh, "remote", "add", "origin", "https://github.com/acme/p-drafts.git")
        self.write("project.json", self.project, fresh)
        self.write("a.md", b"\xef\xbb\xbf[N\xff](n.md)\n", fresh)
        out = self.check(0)
        self.assertEqual(out["link_reports"], [{"path": "a.md", "line": 1, "layer": "layer 0", "case": 3,
                                                "link": "[N�](n.md)"}])

    def test_render_refuses_what_prepare_does_not_give(self):
        """AUD-56 to AUD-59, AUD-46: render exits 2 on link reports or a reason of another form, and on missing fields."""
        self.process()
        prep = self.check(1)
        good = dict(prep, checked=prep["selected"], findings=[], not_checked=[])
        report = dict(prep["link_reports"][0])
        for bad in ({"links_not_checked": "some reason"}, {"link_reports": [dict(report, case=3)]},
                    {"link_reports": [dict(report, path="other.md")]}, {"link_reports": [dict(report, line="6")]},
                    {"link_reports": [dict(report, plain="[x](y)")]}, {"link_reports": [dict(report, case=1)]},
                    {"link_reports": [report], "links_not_checked": "git failed: x"}, {"link_reports": "none"}):
            status, _, err = self.run_script("render", stdin=json.dumps(dict(good, **bad)).encode())
            self.assertEqual(status, 2, bad)
        self.assertEqual(check_writing.render(dict(good))[:16], "Check of writing")
        for key in ("link_reports", "links_not_checked"):
            with self.assertRaises(check_writing.BadInput):
                check_writing.render({k: v for k, v in good.items() if k != key})


if __name__ == "__main__":
    unittest.main()
