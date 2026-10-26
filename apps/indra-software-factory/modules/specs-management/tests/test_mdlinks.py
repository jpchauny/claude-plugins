"""Tests of scripts/mdlinks.py, the CommonMark 0.31.2 link finder of the move.

Spec: specs/module.md, section "Move specs between layers 0 and 1", term Link
(an inline link of CommonMark 0.31.2 section 6.3; not a link: an image, text
in a code span, in a fenced or indented code block, in an HTML block or in an
HTML comment). The cases named "gap" are the repro cases of the parser audit.
Run with:

    python3 -m unittest discover -s apps/indra-software-factory/modules/specs-management/tests -p test_mdlinks.py
"""

import os
import sys
import unittest

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

import mdlinks  # noqa: E402


def dests(text):
    """Raw destinations of the links of text, checking the offsets of each link."""
    out = []
    for l in mdlinks.find_links(text):
        assert set(l) == {"open", "close", "dest_start", "dest_end", "end", "line", "angle", "title"}, l
        assert text[l["open"]] == "[" and text[l["close"]] == "]" and text[l["end"] - 1] == ")", l
        assert l["open"] < l["close"] < l["dest_start"] <= l["dest_end"] < l["end"], l
        out.append(text[l["dest_start"]:l["dest_end"]])
    return out


class Normal(unittest.TestCase):
    def test_simple(self):
        t = "See [Glossary](glossary.md).\n"
        [l] = mdlinks.find_links(t)
        self.assertEqual(l, dict(open=4, close=13, dest_start=15, dest_end=26, end=27, line=1,
                                 angle=False, title=False))
        self.assertEqual(t[l["open"] + 1:l["close"]], "Glossary")

    def test_order_and_lines(self):
        t = "a [x](1.md) [y](2.md)\n\nb [z](3.md)\n"
        self.assertEqual(dests(t), ["1.md", "2.md", "3.md"])
        self.assertEqual([l["line"] for l in mdlinks.find_links(t)], [1, 1, 3])

    def test_list_item(self):
        self.assertEqual(dests("- one [x](a.md)\n  - two [y](b.md)\n1. three [z](c.md)\n"),
                         ["a.md", "b.md", "c.md"])

    def test_blockquote(self):
        self.assertEqual(dests("> quote [x](a.md)\n> > deeper [y](b.md)\nlazy [z](c.md)\n"),
                         ["a.md", "b.md", "c.md"])

    def test_table_row_is_paragraph_text(self):
        t = "| a | b |\n|---|---|\n| [x](a.md) | `[y](b.md)` |\n"
        self.assertEqual(dests(t), ["a.md"])

    def test_wrapped_link_text(self):
        t = "See [the\nspec](a.md).\n"
        [l] = mdlinks.find_links(t)
        self.assertEqual(t[l["open"] + 1:l["close"]], "the\nspec")
        self.assertEqual(l["line"], 1)

    def test_wrapped_code_span(self):
        self.assertEqual(dests("Use `foo\n[x](a.md) bar` here.\n"), [])

    def test_nested_lists_with_fences(self):
        t = ("- a\n"
             "  - b\n"
             "    ```\n"
             "    [x](in-fence.md)\n"
             "    ```\n"
             "    [y](after.md)\n"
             "  ```\n"
             "  [z](in-second-fence.md)\n")
        self.assertEqual(dests(t), ["after.md"])

    def test_crlf(self):
        t = "a [x](a.md)\r\nb [y](\r\nb.md)\r\n\r\n```\r\n[z](c.md)\r\n```\r\n"
        self.assertEqual(dests(t), ["a.md", "b.md"])
        self.assertEqual([l["line"] for l in mdlinks.find_links(t)], [1, 2])

    def test_cr_only(self):
        self.assertEqual(dests("a\r[x](a.md)\r    [y](b.md)\r"), ["a.md", "b.md"])

    def test_tabs(self):
        self.assertEqual(dests("-\t[x](a.md)\n>\t[y](b.md)\n\n\t[z](code.md)\n"), ["a.md", "b.md"])
        self.assertEqual(dests("-\titem\n\n\t\t[x](code.md)\n"), [])    # indented code in the item

    def test_heading_content(self):
        self.assertEqual(dests("# Title [x](a.md) #\n\nSetext [y](b.md)\n---\n"), ["a.md", "b.md"])

    def test_angle_and_title(self):
        t = '[a](<b c.md> "t") [d](e.md\n\'u\') [f](g.md (v)) [h](<>) [i]()\n'
        ls = mdlinks.find_links(t)
        self.assertEqual(dests(t), ["<b c.md>", "e.md", "g.md", "<>", ""])
        self.assertEqual([l["angle"] for l in ls], [True, False, False, True, False])
        self.assertEqual([l["title"] for l in ls], [True, True, True, False, False])

    def test_balanced_parentheses(self):
        self.assertEqual(dests("[a](b(c)d.md) [e](f\\)g.md) [h](i(j.md)\n"), ["b(c)d.md", "f\\)g.md"])

    def test_not_links(self):
        t = ("[ref][r] [short] ![img](i.png) [space](a b) [nl](a\n\nb) [r]: x\n\n"
             "<div>\n[html](a.md)\n</div>\n\n<!-- [c](a.md)\n\n-->\n")
        self.assertEqual(dests(t), [])

    def test_surrogateescape(self):
        t = b"Caf\xe9 see [G](glossary.md)\n".decode("utf-8", "surrogateescape")
        self.assertEqual(dests(t), ["glossary.md"])

    def test_link_inside_image_inside_link(self):
        # commonmark.js: the inner link deactivates the outer bracket.
        self.assertEqual(dests("[p ![a [x](a.md)](i.png)](q.md)\n"), [])

    def test_reference_link_blocks_outer_link(self):
        self.assertEqual(dests("[a [b]](d.md)\n\n[b]: x\n"), [])
        self.assertEqual(dests("[a [b]](d.md)\n"), ["d.md"])


class Gaps(unittest.TestCase):
    """The repro cases of the audit (parser_gaps.json), as CommonMark 0.31.2 reads them."""

    def test_comment_opener_in_code_span(self):
        t = "Write `<!--` to open a comment. See [Glossary](glossary.md).\n\nPlain [Glossary](glossary.md).\n"
        self.assertEqual(dests(t), ["glossary.md", "glossary.md"])

    def test_code_and_html_blocks_hide_links(self):
        for t in ["> ```\n> [x](a.md)\n> ```\n",
                  "<pre>\nline\n\n[x](a.md)\n</pre>\n",
                  "- item\n\n        [x](a.md)\n",
                  "# H\n    [x](a.md)\n",
                  "T\n===\n    [x](a.md)\n",
                  "<?php\n\n[x](a.md)\n?>\n",
                  "```\ncode\n     ```\n[x](a.md)\n```\n",
                  "<script>\n\n[x](a.md)\n</script>\n",
                  "<style>\n\n[x](a.md)\n</style>\n",
                  "<textarea>\n\n[x](a.md)\n</textarea>\n",
                  "<!DOCTYPE html\n[x](a.md)\n>\n",
                  "<![CDATA[\n\n[x](a.md)\n]]>\n",
                  "<div>\n[x](a.md)\n",
                  "<span>\n[x](a.md)\n"]:
            with self.subTest(t=t):
                self.assertEqual(dests(t), [])

    def test_blocks_that_do_not_hide_links(self):
        for t in ["<kbd>Ctrl</kbd> then see [x](a.md)\n",
                  "text\n<span>\n[x](a.md)\n",
                  "Para\n\n    ```\n\n[x](a.md)\n",
                  "\t```\n[x](a.md)\n",
                  "``` a`b\n[x](a.md)\n",
                  "<div>\n\n[x](a.md)\n",
                  "<pre>\n</pre>\n[x](a.md)\n"]:
            with self.subTest(t=t):
                self.assertEqual(dests(t), ["a.md"])

    def test_inline_over_whole_paragraph(self):
        self.assertEqual(dests("See [the\nspec](a.md).\n"), ["a.md"])
        self.assertEqual(dests("[x](\na.md)\n"), ["a.md"])
        self.assertEqual(dests("Use `foo\n[x](a.md) bar` here.\n"), [])

    def test_latin1_bytes(self):
        t = "Caf\xe9 see [G](glossary.md)\n".encode("latin-1").decode("utf-8", "surrogateescape")
        [l] = mdlinks.find_links(t)
        self.assertEqual(t[l["dest_start"]:l["dest_end"]], "glossary.md")

    def test_inline_precedence(self):
        self.assertEqual(dests("[a [b](c.md)](d.md)\n"), ["c.md"])
        self.assertEqual(dests("\\![x](a.md)\n"), ["a.md"])
        self.assertEqual(dests("<http://h/[x](a.md)>\n"), [])
        self.assertEqual(dests('Text <span title="[x](a.md)">y</span>\n'), [])
        self.assertEqual(dests("![a [x](a.md)](i.png)\n"), [])
        self.assertEqual(dests("<!-->\n\n[x](a.md)\n"), ["a.md"])
        self.assertEqual(dests("<!--->\n\n[x](a.md)\n"), ["a.md"])
        self.assertEqual(dests("a <!-- [x](a.md) --> b [y](b.md)\n"), ["b.md"])
        self.assertEqual(dests("a <!--> [x](a.md)\n"), ["a.md"])

    def test_whitespace_around_destination(self):
        t = "[x]( a.md) [y](b.md )\n"
        ls = mdlinks.find_links(t)
        self.assertEqual(dests(t), ["a.md", "b.md"])
        self.assertEqual(t[ls[0]["dest_start"] - 1], " ")
        self.assertEqual(t[ls[1]["dest_end"]:ls[1]["end"]], " )")


class Refdefs(unittest.TestCase):
    def defs(self, t):
        return [(d["line"], t[d["dest_start"]:d["dest_end"]], d["angle"]) for d in mdlinks.find_refdefs(t)]

    def test_definitions(self):
        t = '[a]: a.md\n[b]:\n  <b c.md> "t"\n\n> [c]: c.md\n- [d]: d.md\n'
        self.assertEqual(self.defs(t), [(1, "a.md", False), (2, "<b c.md>", True), (5, "c.md", False),
                                        (6, "d.md", False)])
        self.assertEqual(mdlinks.find_refdefs(t)[0], dict(line=1, dest_start=5, dest_end=9, angle=False))

    def test_not_definitions(self):
        t = ("text\n[a]: a.md\n\n    [b]: b.md\n\n```\n[c]: c.md\n```\n\n<div>\n[d]: d.md\n\n"
             '[e]: e.md "t" x\ny\n\n`[f]: f.md`\n\n[g]:\n\n[]: h.md\n')
        self.assertEqual(self.defs(t), [])

    def test_title_on_next_line_falls_back(self):
        t = '[a]: a.md\n"t" text\n'
        self.assertEqual(self.defs(t), [(1, "a.md", False)])

    def test_definition_is_not_a_link(self):
        self.assertEqual(dests("[a]: (b.md)\n"), [])


if __name__ == "__main__":
    unittest.main()
