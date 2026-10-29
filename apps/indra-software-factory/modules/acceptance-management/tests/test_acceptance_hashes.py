"""Tests of scripts/acceptance_hashes.py.

The fingerprints and the citations of ACU-51 to ACU-56 of specs/module.md.
The binding examples are read from the spec itself, so that a change of the
spec that breaks a binding hash fails here. Run with:

    python3 -m unittest discover -s apps/indra-software-factory/modules/acceptance-management/tests
"""

import os
import re
import sys
import unittest

PLUGIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(PLUGIN, "scripts"))

import acceptance_hashes as h  # noqa: E402

with open(os.path.join(PLUGIN, "specs", "module.md"), encoding="utf-8") as f:
    SPEC = f.read()


def example(heading: str) -> str:
    """The file of the binding example of the spec that starts with `heading`, without the two spaces of
    indentation of each of its lines (ACU-52)."""
    block = re.search(r"^  ````markdown\n(  " + re.escape(heading) + r"\n.*?)^  ````$", SPEC, re.S | re.M)
    return "".join(line[2:] + "\n" for line in block.group(1).splitlines())


AU3 = example("# AU-3 Export the invoices to CSV")
AA1 = example("# AA-1 Billing")
AU11 = example("# AU-11 Multiply two integers")


class BindingExamples(unittest.TestCase):
    def test_acu52_the_unit_hash_of_au3(self):
        self.assertEqual(h.unit_hash(AU3), "efc7ae86")
        self.assertIn("unit hash `efc7ae86`", SPEC)

    def test_acu53_the_area_hash_of_aa1(self):
        self.assertEqual(h.area_hash(AA1), "3b0900fb")
        self.assertIn("area hash `3b0900fb`", SPEC)

    def test_acu54_the_scenario_hash_of_sc5(self):
        sc5 = h.scenarios(AU3)[0]
        self.assertEqual((sc5.scenario_id, sc5.scenario_hash), ("SC-5", "147d88d2"))
        self.assertIn("scenario hash `147d88d2`", SPEC)

    def test_acu11_the_citations_of_the_examples_are_the_hashes(self):
        self.assertIn(f"# AU-3@{h.unit_hash(AU3)}: Export the invoices to CSV", SPEC)
        self.assertIn(f"# SC-5@{h.scenarios(AU3)[0].scenario_hash}: Three invoices give three rows", SPEC)
        self.assertIn(f"// AU-11@{h.unit_hash(AU11)}: Multiply two integers", SPEC)
        self.assertIn(f"// SC-21@{h.scenarios(AU11)[0].scenario_hash}: Two integers give their product", SPEC)
        self.assertIn(f'"SC-6": "{h.scenarios(AU3)[1].scenario_hash}"', SPEC)


class Fingerprint(unittest.TestCase):
    def test_acu51_crlf_trailing_blanks_and_trailing_empty_lines_do_not_count(self):
        messy = AU3.replace("\n", " \t\r\n") + "\r\n\r\n   \n"
        self.assertEqual(h.unit_hash(messy.encode("utf-8")), h.unit_hash(AU3))

    def test_acu51_one_final_newline_is_added(self):
        self.assertEqual(h.fingerprint(["a"]), h.fingerprint(["a", "", ""]))
        self.assertEqual(h.fingerprint(["a"]), "87428fc5")  # the SHA-256 of "a\n"

    def test_acu51_bytes_that_are_not_utf8_are_refused(self):
        with self.assertRaises(UnicodeDecodeError):
            h.unit_hash(b"## Narrative\n\xff\n")


class UnitHash(unittest.TestCase):
    def test_acu52_title_area_and_profile_are_outside_the_hash(self):
        moved = (AU3.replace("# AU-3 Export the invoices to CSV", "# AU-3 Export to CSV")
                 .replace("Area: AA-1", "Area: AA-7\nProfile: critical"))
        self.assertEqual(h.unit_hash(moved), "efc7ae86")

    def test_acu52_a_norm_hash_of_norms_is_inside_the_hash(self):
        self.assertNotEqual(h.unit_hash(AU3.replace("INV-12@0c1d2e3f", "INV-12@7d6e5f40")), "efc7ae86")

    def test_acu52_a_non_goal_is_inside_the_hash(self):
        self.assertNotEqual(h.unit_hash(AU3.replace("to Excel.", "to ODS.")), "efc7ae86")

    def test_acu52_no_narrative_no_unit_hash(self):
        self.assertIsNone(h.unit_hash("# AU-1 Add\n\nArea: AA-1\n"))
        self.assertIsNone(h.unit_hash("# AU-1 Add\n\n## Narrative of it\n"))

    def test_acu53_no_purpose_no_area_hash(self):
        self.assertIsNone(h.area_hash("# AA-1 Billing\n"))
        self.assertEqual(h.area_hash(AA1.replace("# AA-1 Billing", "# AA-1 Invoicing")), "3b0900fb")


class Scenarios(unittest.TestCase):
    def test_acu54_names_tags_norms_and_units(self):
        sc5, sc6 = h.scenarios(AU3)
        self.assertEqual((sc5.name, sc5.tags, sc5.norms, sc5.acceptance_units), (
            "Three invoices give three rows", ["@SC-5", "@INV-7", "@INV-12"], ["INV-7", "INV-12"], []))
        self.assertEqual((sc6.scenario_id, sc6.name, sc6.norms), ("SC-6", "A cancelled invoice gives no row", ["INV-15"]))
        (sc9,) = h.scenarios(AA1)
        self.assertEqual((sc9.scenario_id, sc9.acceptance_units, sc9.norms), ("SC-9", ["AU-1", "AU-2", "AU-3"], ["INV-15"]))

    def test_acu54_a_scenario_ends_before_the_tags_of_the_next(self):
        start = AU3.index("@SC-5")
        end = AU3.index("@SC-6")
        alone = "## Scenarios\n\n```gherkin\n" + AU3[start:end] + "```\n"
        self.assertEqual(h.scenarios(alone)[0].scenario_hash, "147d88d2")

    def test_acu54_the_text_of_another_scenario_does_not_change_the_hash(self):
        changed = AU3.replace("Then the CSV has 2 rows", "Then the CSV has two rows")
        self.assertEqual(h.scenarios(changed)[0].scenario_hash, h.scenarios(AU3)[0].scenario_hash)
        self.assertNotEqual(h.scenarios(changed)[1].scenario_hash, h.scenarios(AU3)[1].scenario_hash)

    def test_acu54_the_tags_are_inside_the_hash(self):
        self.assertNotEqual(h.scenarios(AU3.replace("@SC-5 @INV-7 @INV-12", "@SC-5 @INV-7"))[0].scenario_hash, "147d88d2")

    def test_acu50_not_exactly_one_scenario_id(self):
        none = h.scenarios(AU3.replace("@SC-5 @INV-7", "@INV-7"))[0]
        two = h.scenarios(AU3.replace("@SC-5 @INV-7", "@SC-5 @SC-8 @INV-7"))[0]
        zero = h.scenarios(AU3.replace("@SC-5 @INV-7", "@SC-05 @INV-7"))[0]
        self.assertEqual((none.scenario_id, two.scenario_id, zero.scenario_id), (None, None, None))

    def test_acu54_only_the_gherkin_block_of_scenarios(self):
        text = "## Narrative\n\nScenario: not one\n\n## Scenarios\n\nNone.\n"
        self.assertEqual(h.scenarios(text), [])

    def test_acu54_forbidden_keywords(self):
        text = "## Scenarios\n\n```gherkin\nFeature: x\n@SC-1\nScenario: a\n  Examples:\n```\n"
        self.assertEqual(h.forbidden_lines(text), [4, 7])
        self.assertEqual(h.forbidden_lines(AU3), [])


class Citations(unittest.TestCase):
    def test_acu56_the_citations_of_norms(self):
        self.assertEqual(h.norm_citations(AU3), [("INV-7", "5a627175", "one row per invoice"),
                                                 ("INV-12", "0c1d2e3f", "amounts with two decimals"),
                                                 ("INV-15", "9e8d7c6b", "cancelled invoices are not exported")])
        self.assertEqual(h.norm_citations("## Norms\n\n- IN-7@5a627175: two letters\n- INV-7@5A627175: upper\n"), [])

    def test_acu56_the_citations_of_units_areas_and_scenarios(self):
        text = ("# AU-3@efc7ae86: Export the invoices to CSV\n# SC-5@147d88d2: Three invoices\n"
                "# AA-1@3b0900fb: Billing\n# XAU-3@efc7ae86: no\n# AU-03@efc7ae86: no\n# INV-7@5a627175: no\n")
        self.assertEqual(h.citations(text), [("AU-3", "efc7ae86"), ("SC-5", "147d88d2"), ("AA-1", "3b0900fb")])

    def test_acu56_a_citation_found_in_a_line_has_a_boundary_on_each_side(self):
        """The evidence run and write-acceptance-tests find the same citations (WAT-7)."""
        for text in ("SC-5@147d88d2_v2", "SC-5@147d88d2-2", "SC-5@147d88d2é", "éSC-5@147d88d2", "_SC-5@147d88d2"):
            self.assertEqual(h.citations(text), [], text)
        self.assertEqual(h.citations("(SC-5@147d88d2)."), [("SC-5", "147d88d2")])
        self.assertEqual(h.NORM_CITATION_IN_LINE.findall("XINV-7@5a627175 INV-7@5a627175_v2"), [("XINV-7", "5a627175")])


if __name__ == "__main__":
    unittest.main()
