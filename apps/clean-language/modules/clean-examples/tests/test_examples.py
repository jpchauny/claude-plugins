"""Tests of scripts/examples.py, scripts/hook.py and use-cases/audit/audit.py.

Spec: specs/module.md (CEX-n) and use-cases/audit/specs/audit.md (CAU-n). Each test names the
clause it checks. Run with:

    python3 -m unittest discover -s apps/clean-language/modules/clean-examples/tests
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
PLUGIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PLUGIN, "scripts"))
sys.path.insert(0, os.path.join(PLUGIN, "use-cases", "audit"))
import audit  # noqa: E402
import examples as ex  # noqa: E402
import hook  # noqa: E402

F = "```"


def md(info, *code):
    return "\n".join([F + info, *code, F, ""])


def rules(text, codes=None):
    return sorted({(line, rule) for b in ex.blocks(text) if b.fenced for line, rule in ex.check_block(b, codes)})


def git(cwd, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t",
               GIT_CONFIG_NOSYSTEM="1", HOME=cwd)
    subprocess.run(["git", "-C", cwd] + list(args), check=True, capture_output=True, env=env)


REGISTRY = """# Error Code Registry

## 5. Code Index

| Code | Name |
|---|---|
| `SYN011` | `PlaceholderNotAName` |
| [SEM004 (not specified yet)](absent:x.md) | `InvalidOperationForType` |

## 6. Reserved Codes

| Code | Name | Use instead |
|---|---|---|
| `SYN006` | `IndentationError` | `SYN003` |
"""


class Project:
    """Two repositories, layer 0 and layer 1, in one project folder."""

    def __init__(self):
        self.root = tempfile.mkdtemp()
        self.l0, self.l1 = os.path.join(self.root, "drafts"), os.path.join(self.root, "specs")
        project = {"project": "p", "repositories": [
            {"owner": "o", "name": "drafts", "layer": 0, "path": "drafts"},
            {"owner": "o", "name": "specs", "layer": 1, "path": "specs"}]}
        for repo, name in ((self.l0, "drafts"), (self.l1, "specs")):
            os.makedirs(os.path.join(repo, "specs"))
            git(repo, "init", "-q")
            git(repo, "remote", "add", "origin", f"https://github.com/o/{name}.git")
            self.write(repo, "project.json", json.dumps(project))
        self.write(self.l1, "specs/platform/error-codes.md", REGISTRY)

    def write(self, repo, path, text):
        full = os.path.join(repo, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(text)
        return full

    def close(self):
        shutil.rmtree(self.root)


class OpeningLine(unittest.TestCase):
    def test_cex4_the_three_forms(self):
        for info in ("clean-language expect=valid", "clean-language expect=syntax-error code=SYN011 line=1",
                     "clean-language expect=error code=SEM004"):
            self.assertEqual(rules(md(info, "start:", "\tprint(1)")), [], info)

    def test_cex4_any_other_form(self):
        for info in ("clean-language", "clean-language expect=valid code=SEM004", "clean-language expect=syntax-error code=SYN011",
                     "clean-language expect=error  code=SEM004", "clean-language expect=syntax-error line=1 code=SYN011",
                     "clean-language expect=syntax-error code=SYN011 line=01", "clean-language expect=maybe"):
            self.assertIn((1, "CEX-4"), rules(md(info, "start:", "\tprint(1)")), info)

    def test_cex2_old_info_string(self):
        self.assertEqual(rules(md("clean", "start:")), [(1, "CEX-2")])
        self.assertEqual(rules(md("clean title", "start:")), [(1, "CEX-2")])
        self.assertEqual(rules(md("cleaner", "start:")), [])

    def test_cex6_prefix_and_line_range(self):
        self.assertIn((1, "CEX-6"), rules(md("clean-language expect=syntax-error code=SEM004 line=1", "start:")))
        self.assertIn((1, "CEX-6"), rules(md("clean-language expect=syntax-error code=SYN011 line=3", "start:", "\tx")))
        self.assertEqual(rules(md("clean-language expect=syntax-error code=SYN011 line=2", "start:", "\tx")), [])

    def test_cex7_prefix(self):
        self.assertEqual(rules(md("clean-language expect=error code=SYN011", "start:")), [(1, "CEX-7")])

    def test_cex9_fails_comment(self):
        text = md("clean-language expect=valid", "start:", "\tx = 1   // fails: SYN002", "\ty = 2  // prints: 2")
        self.assertEqual(rules(text), [(3, "CEX-9")])

    def test_cex9_not_inside_a_string(self):
        self.assertEqual(rules(md("clean-language expect=valid", "start:", '\tprint("// fails: x")')), [])


class Code(unittest.TestCase):
    def test_cex10_loose_code(self):
        text = md("clean-language expect=valid", "integer x = 5", "start:", "\tprint(x)")
        self.assertEqual(rules(text), [(2, "CEX-10")])

    def test_cex10_section_lines(self):
        lines = ["libraries: data, server", "import:", "source:", "constant:", "state:", "can Check:", "class Point",
                 "class StrongPassword can Check", "functions:", "watch count:", "tests:", "start:",
                 "compiletime function x()", "handles block \"data\" with f", 'host interface dom version "1.0.0":',
                 "endpoints:", "component: Page", "// a comment", "/* block */", ""]
        text = md("clean-language expect=valid", *lines)
        self.assertEqual(rules(text), [])

    def test_cex10_not_for_a_syntax_error(self):
        text = md("clean-language expect=syntax-error code=SYN011 line=1", "integer x = 5")
        self.assertEqual(rules(text), [])

    def test_cex10_comment_at_end_of_section_line(self):
        self.assertEqual(rules(md("clean-language expect=valid", "start:   // entry", "\tprint(1)")), [])

    def test_cex11_file_line(self):
        self.assertEqual(rules(md("clean-language expect=valid", "// file: app/a.cln", "start:")), [])
        text = md("clean-language expect=valid", "start:", "// file: app/b.cln")
        self.assertEqual(rules(text), [(3, "CEX-11")])

    def test_cex13_space_in_indentation(self):
        text = md("clean-language expect=valid", "start:", "    print(1)", "\t print(2)")
        self.assertEqual(rules(text), [(3, "CEX-13"), (4, "CEX-13")])

    def test_cex13_inside_an_open_bracket(self):
        text = md("clean-language expect=valid", "start:", "\ttotal = (a +", "\t         b)", '\ts = "(" + x', "\t  y = 1")
        self.assertEqual(rules(text), [(6, "CEX-13")])

    def test_cex13_syn003(self):
        self.assertEqual(rules(md("clean-language expect=syntax-error code=SYN003 line=2", "start:", "  print(1)")), [])


class ErrorCodes(unittest.TestCase):
    CODES = ({"SYN011", "SEM004", "SYN006"}, {"SYN006"})

    def test_cex16_undefined(self):
        text = md("clean-language expect=error code=SEM999", "start:")
        self.assertEqual(rules(text, self.CODES), [(1, "CEX-16")])

    def test_cex17_retired(self):
        text = md("clean-language expect=syntax-error code=SYN006 line=1", "start:")
        self.assertEqual(rules(text, self.CODES), [(1, "CEX-17")])

    def test_registry_rows_and_retired(self):
        rows, retired = ex.registry(REGISTRY)
        self.assertEqual((rows, retired), ({"SYN011", "SEM004"}, {"SYN006"}))

    def test_cex15_cex18_definitions(self):
        p = Project()
        try:
            p.write(p.l0, "specs/a.md", "### SYN011 — Placeholder Not a Name\n")
            p.write(p.l1, "specs/b.md", "#### SYN011 — Placeholder Not a Name\n\n### SYN006 — Old\n")
            codes = ex.Codes([(None, p.l0), ("o/specs", p.l1)], layer1=p.l1)
            self.assertEqual(codes.violations(), [("o/specs", "specs/b.md", 1, "CEX-15"), ("o/specs", "specs/b.md", 3, "CEX-18")])
        finally:
            p.close()

    def test_definition_inside_a_fenced_block_is_none(self):
        self.assertEqual(ex.headings("```text\n### SYN011 — x\n```\n"), [])


class Markdown(unittest.TestCase):
    """Regressions of the check against the spec (DEV-3)."""

    def test_crlf_and_cr(self):
        text = "```clean-language expect=valid\r\nstart:\r\n\tprint(1)\r\n```\r\n\r\n```clean\r\nstart:\r\n```\r\n"
        self.assertEqual(rules(text), [(6, "CEX-2")])

    def test_prefix_is_compared_whole(self):
        self.assertIn((1, "CEX-6"), rules(md("clean-language expect=syntax-error code=SYNX001 line=1", "start:")))
        self.assertEqual(rules(md("clean-language expect=error code=SYNTAX001", "start:")), [])

    def test_block_comment_at_end_of_section_line(self):
        self.assertEqual(rules(md("clean-language expect=valid", "can Run: /* cap */", "\tx", "watch y: /* w */", "\tz")), [])

    def test_fence_indented_four_spaces_is_no_fence(self):
        self.assertEqual(rules("para\n\n    ```clean\n    start:\n    ```\n"), [])
        text = "```clean-language expect=valid\nstart:\n\tx = 1\n    ```\n\tprint(x)\n```\n"
        self.assertEqual([b.line for b in ex.blocks(text) if b.fenced], [1])

    def test_unclosed_fence_line_count(self):
        self.assertIn((1, "CEX-6"), rules("```clean-language expect=syntax-error code=SYN001 line=3\nstart:\n\tfoo\n"))

    def test_line_zero_is_cex6(self):
        self.assertEqual(rules(md("clean-language expect=syntax-error code=SYN001 line=0", "start:")), [(1, "CEX-6")])

    def test_definition_headings(self):
        self.assertEqual(ex.headings("   ### SYN011 — P\n###  SYN012 — X\n###\tSYN013 — Y\n"),
                         [(1, "SYN011"), (2, "SYN012"), (3, "SYN013")])

    def test_quote_and_html_comment(self):
        self.assertEqual(rules("> ```clean\n> start:\n> ```\n"), [(1, "CEX-2")])
        self.assertEqual(rules("<!--\n```clean\nstart:\n```\n### SYN011 — X\n-->\n"), [])
        self.assertEqual(ex.headings("<!--\n### SYN011 — X\n-->\n"), [])

    def test_html_comment_inside_a_fenced_block_is_code(self):
        self.assertEqual(rules("```html\n<!-- a -->\n<!--\n```\n\n```clean\nstart:\n```\n"), [(6, "CEX-2")])
        self.assertEqual(rules("```text\n- item\n```\n```clean\nstart:\n```\n"), [(4, "CEX-2")])

    def test_list_items(self):
        self.assertEqual(rules("- item\n\n  ```clean\n  start:\n  ```\n"), [(3, "CEX-2")])
        self.assertEqual(rules("- ```clean\n  start:\n  ```\n"), [(1, "CEX-2")])
        text = "- item\n\n      start:\n      \tprint(1)\n\n- item2\n\n    start:\n    \tprint(1)\n"
        self.assertEqual([b.line for b in ex.blocks(text) if ex.is_suspect(b)], [3])


class Suspects(unittest.TestCase):
    def test_cau6_suspects(self):
        for text in ("```\nstart:\n\tprint(1)\n```\n", "```text\nfunctions:\n\tvoid f()\n```\n",
                     "para\n\n    class Point\n    \tinteger x\n"):
            self.assertTrue(any(ex.is_suspect(b) for b in ex.blocks(text)), text)

    def test_cau6_not_suspects(self):
        for text in ("```text\nSYN007: `state:` must come after `import:`\n```\n", "```text\nstart:\n```\n",
                     "```clean\nstart:\n\tprint(1)\n```\n", md("clean-language expect=valid", "start:", "\tx")):
            self.assertFalse(any(ex.is_suspect(b) for b in ex.blocks(text)), text)


class Audit(unittest.TestCase):
    def setUp(self):
        self.p = Project()

    def tearDown(self):
        self.p.close()

    def test_cau8_report(self):
        p = self.p
        p.write(p.l1, "specs/z.md", md("clean", "start:"))
        p.write(p.l1, "specs/a.md", "text\n\n" + md("clean-language expect=error code=SEM999", "x = 1", "start:"))
        report = audit.run(p.l1)
        self.assertEqual(report, "\n".join([
            "Audit of Clean examples in o/specs: 1 Clean examples in 3 selected files, 3 violations, 0 suspects.",
            "",
            "## Violations",
            "",
            "- specs/a.md:3 · CEX-16 · the error code has neither a definition nor a registry row",
            "- specs/a.md:4 · CEX-10 · code at column 1 outside a section",
            "- specs/z.md:1 · CEX-2 · the info string clean is replaced by clean-language",
            "",
            "## Suspects",
            "",
            "None.",
            ""]))

    def test_cau9_same_report(self):
        self.p.write(self.p.l0, "specs/a.md", md("clean", "start:"))
        self.assertEqual(audit.run(self.p.l0), audit.run(self.p.l0))

    def test_cau3_argument(self):
        p = self.p
        p.write(p.l1, "specs/language/a.md", md("clean", "start:"))
        p.write(p.l1, "specs/other/b.md", md("clean", "start:"))
        self.assertIn("in 1 selected files", audit.run(p.l1, "specs/language"))
        self.assertIn("selects no file", audit.run(p.l1, "specs/none"))

    def test_cau4_not_a_layer(self):
        os.remove(os.path.join(self.p.l1, "project.json"))
        self.assertEqual(audit.run(self.p.l1), "Audit of Clean examples: the repository has no project.json; nothing checked.\n")

    def test_cau7_other_repository_missing(self):
        shutil.rmtree(self.p.l0)
        self.assertIn("CEX-15 to CEX-18 skipped", audit.run(self.p.l1))

    def test_cau7_no_other_layer_in_project_json(self):
        p = self.p
        p.write(p.l1, "project.json", json.dumps({"repositories": [{"owner": "o", "name": "specs", "layer": 1, "path": "specs"}]}))
        self.assertIn("lists no repository of layer 0", audit.run(p.l1))

    def test_cau7_registry_missing(self):
        os.remove(os.path.join(self.p.l1, "specs/platform/error-codes.md"))
        self.p.write(self.p.l0, "specs/a.md", "x\n")
        self.assertIn("Not found: the registry, expected at", audit.run(self.p.l0))

    def test_cau3_folder_starting_with_two_dots(self):
        p = self.p
        p.write(p.l1, "..foo/x.md", md("clean", "start:"))
        self.assertIn("..foo/x.md:1 · CEX-2", audit.run(p.l1, "..foo"))

    def test_cau7_definition_in_the_other_layer(self):
        p = self.p
        p.write(p.l0, "specs/s.md", "### SEM777 — Something\n")
        p.write(p.l1, "specs/a.md", md("clean-language expect=error code=SEM777", "start:"))
        self.assertIn("0 violations", audit.run(p.l1))


class Hook(unittest.TestCase):
    def setUp(self):
        self.p = Project()

    def tearDown(self):
        self.p.close()

    def call(self, tool, **inp):
        return hook.main(json.dumps({"tool_name": tool, "tool_input": inp}))

    def test_cex22_cex23_refuses_a_new_malformed_example(self):
        path = os.path.join(self.p.l0, "specs/new.md")
        code, _, err = self.call("Write", file_path=path, content=md("clean-language expect=valid", "x = 1"))
        self.assertEqual(code, 2)
        self.assertIn("specs/new.md:2 · CEX-10", err)

    def test_cex23_an_old_violation_never_refuses(self):
        path = self.p.write(self.p.l0, "specs/a.md", "intro\n\n" + md("clean", "start:"))
        code, _, _ = self.call("Edit", file_path=path, old_string="intro", new_string="intro, longer")
        self.assertEqual(code, 0)

    def test_cex23_moving_a_block_never_refuses_copying_does(self):
        block = md("clean", "start:")
        path = self.p.write(self.p.l0, "specs/a.md", "a\n\n" + block + "\nb\n")
        self.assertEqual(self.call("Write", file_path=path, content="b\n\n" + block + "\na\n")[0], 0)
        self.assertEqual(self.call("Write", file_path=path, content="a\n\n" + block + "\n" + block)[0], 2)

    def test_cex22_not_a_spec_file(self):
        self.assertEqual(self.call("Write", file_path=os.path.join(self.p.l0, "a.txt"), content=md("clean", "x"))[0], 0)
        self.p.write(self.p.l0, ".gitignore", "ignored.md\n")
        self.assertEqual(self.call("Write", file_path=os.path.join(self.p.l0, "ignored.md"), content=md("clean", "x"))[0], 0)

    def test_cex25_other_repository_missing(self):
        shutil.rmtree(self.p.l1)
        path = os.path.join(self.p.l0, "specs/n.md")
        code, out, _ = self.call("Write", file_path=path, content=md("clean-language expect=error code=SEM999", "start:"))
        self.assertEqual(code, 0)
        self.assertIn("CEX-15 to CEX-18 not checked", out)

    def test_cex16_through_the_hook(self):
        path = os.path.join(self.p.l1, "specs/n.md")
        code, _, err = self.call("Write", file_path=path, content=md("clean-language expect=error code=SEM999", "start:"))
        self.assertEqual(code, 2)
        self.assertIn("CEX-16", err)

    def test_cex22_new_nested_folders(self):
        path = os.path.join(self.p.l0, "n1/n2/q.md")
        self.assertEqual(self.call("Write", file_path=path, content=md("clean", "q"))[0], 2)

    def test_cex25_message_also_on_refusal(self):
        os.remove(os.path.join(self.p.l1, "specs/platform/error-codes.md"))
        code, _, err = self.call("Write", file_path=os.path.join(self.p.l0, "q.md"), content=md("clean", "q"))
        self.assertEqual(code, 2)
        self.assertIn("the registry not read at " + os.path.join(os.path.realpath(self.p.l1), "specs/platform/error-codes.md"), err)

    def test_cex26_never_changes_a_file(self):
        path = self.p.write(self.p.l0, "specs/a.md", "x\n")
        self.call("Write", file_path=path, content=md("clean", "start:"))
        self.assertEqual(ex.read(path), "x\n")


if __name__ == "__main__":
    unittest.main()
