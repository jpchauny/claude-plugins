"""Tests of the text of specs/layers.md and of the table of modules of app.md, where a rule of the methodology must
agree with the module that carries it out (DEV-4). Each test names the clause it checks. Run with:

    python3 -m unittest discover -s apps/indra-software-factory/modules/development-methodology/tests
"""

import os
import unittest

PLUGIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODULES = os.path.dirname(PLUGIN)
LAYERS = os.path.join(PLUGIN, "specs", "layers.md")
APP = os.path.join(os.path.dirname(MODULES), "specs", "app.md")
NORMS_MANAGEMENT = os.path.join(MODULES, "norms-management", "specs", "module.md")
CODE_IMPLEMENTATION = os.path.join(MODULES, "code-implementation", "specs", "module.md")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def clause(text, clause_id):
    return text.split("- **%s.**" % clause_id, 1)[1].split("\n- **", 1)[0].split("\n## ", 1)[0]


NORMS_MANAGEMENT_URL = ("https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/modules/"
                        "norms-management/specs/module.md")


class DerivedNormBehindItsNorms(unittest.TestCase):
    def setUp(self):
        self.layers = read(LAYERS)
        self.norms_management = read(NORMS_MANAGEMENT)

    def test_lay_12_a_changed_norm_reaches_a_derived_norm_through_its_generator(self):
        """LAY-12 item 1: a derived norm gets another fingerprint when its generator updates its citation; one that
        still holds the old norm hash is behind its norms, and the run stops after layer 2 (NRM-11, ORC-10)."""
        item_1 = clause(self.layers, "LAY-12").split("\n  1. ", 1)[1].split("\n  2. ", 1)[0]
        self.assertIn("Its derived-norms generator updates the citation of each derived norm that cites it", item_1)
        self.assertIn("is a derived norm behind its norms", item_1)
        self.assertIn("the run stops after layer 2, so layers 3 and 4 never take it as current", item_1)
        self.assertIn("[NRM-11](" + NORMS_MANAGEMENT_URL + "#derive-the-derived-norms)", item_1)
        self.assertIn("[ORC-10](" + NORMS_MANAGEMENT_URL + "#regenerate-the-norms)", item_1)
        self.assertNotIn("[NRM-11 and ORC-10]", item_1)
        self.assertNotIn("each derived norm that cites it gets another derived norm fingerprint", item_1)

    def test_the_term_derived_norm_fingerprint_does_not_restate_lay_12(self):
        """Term Derived norm fingerprint: what it hashes, and LAY-12 for how a change of a norm reaches it."""
        row = self.layers.split("| Derived norm fingerprint |", 1)[1].split("\n", 1)[0]
        self.assertIn("how a change of a norm reaches it is LAY-12", row)
        self.assertNotIn("It changes when a norm that the derived norm cites changes", row)

    def test_derived_norm_behind_its_norms_is_a_term_of_norms_management(self):
        """SPC-3: layers.md takes the term from norms-management, which defines it with NRM-11, rule 5."""
        self.assertIn("list of derived norms and derived norm behind its norms are those of [norms-management]",
                      self.layers)
        row = self.norms_management.split("| Derived norm behind its norms |", 1)[1].split("\n", 1)[0]
        self.assertIn("(NRM-11, rule 5)", row)
        orc_10 = clause(self.norms_management, "ORC-10")
        self.assertIn("a derived norm behind its norms among them (NRM-11, rule 5)", orc_10)


class TableOfModules(unittest.TestCase):
    def test_the_row_of_code_implementation_traces_as_its_scope_does(self):
        """DEV-4, LAY-4: the row of code-implementation in app.md traces the code to the acceptance units and to
        the derived norms it is built from, as the Scope of code-implementation says."""
        row = read(APP).split("| `code-implementation` |", 1)[1].split("\n", 1)[0]
        traceability = ("its traceability to the acceptance units it implements and to the derived norms it is built "
                        "from, and through them to their norms")
        self.assertIn(traceability, row)
        scope = read(CODE_IMPLEMENTATION).split("**Scope:**", 1)[1].split("\n", 1)[0]
        self.assertIn(traceability, scope)


if __name__ == "__main__":
    unittest.main()
