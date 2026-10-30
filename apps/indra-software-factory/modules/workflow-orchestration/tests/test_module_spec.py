"""Tests of specs/module.md of workflow-orchestration, which has no code yet.

They check that the spec can be followed: each clause has one ID, each WFO-n
that it names exists, and each link to another spec reaches a section that
defines the clauses that the link names, such as ORC-10, NRM-11 and NRM-12
for WFO-13, ACU-35 for WFO-8 and ACU-26 and NRM-12 for WFO-10. Run with:

    python3 -m unittest discover -s apps/indra-software-factory/modules/workflow-orchestration/tests
"""

import os
import re
import sys
import unittest

sys.dont_write_bytecode = True  # no __pycache__ inside the plugin

PLUGIN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = os.path.join(PLUGIN, "specs", "module.md")

LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
CLAUSE_ID = re.compile(r"\b([A-Z]{1,4}-\d+|R\d+)\b")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def outside_code_blocks(text):
    return re.sub(r"```.*?```", "", text, flags=re.S)


def github_anchor(heading):
    anchor = heading.strip().lower()
    anchor = re.sub(r"[^\w\- ]", "", anchor)
    return anchor.replace(" ", "-")


def sections(text):
    """Map the anchor of each heading, as GitHub makes it, to the text of its
    section, the sections below it included. GitHub gives the second heading
    with the same anchor `<anchor>-1`, the third `<anchor>-2`, and so on."""
    headings = []
    lines = text.splitlines()
    in_fence = False
    for number, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        m = None if in_fence else re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            headings.append((number, len(m.group(1)), github_anchor(m.group(2))))
    result = {}
    seen = {}
    for index, (number, level, anchor) in enumerate(headings):
        end = len(lines)
        for later_number, later_level, _ in headings[index + 1:]:
            if later_level <= level:
                end = later_number
                break
        count = seen.get(anchor, 0)
        seen[anchor] = count + 1
        result[anchor if count == 0 else f"{anchor}-{count}"] = "\n".join(lines[number + 1:end])
    return result


def defines(section_text, clause_id):
    """A clause is defined as `**ID.**` in a spec, or as `Rule: ID` in a use case."""
    escaped = re.escape(clause_id)
    return re.search(r"\*\*" + escaped + r"[.\s]|Rule: " + escaped + r"\b", section_text) is not None


class TestClauses(unittest.TestCase):
    def setUp(self):
        self.text = outside_code_blocks(read(SPEC))

    def test_each_clause_id_is_defined_once(self):
        ids = re.findall(r"^- \*\*([A-Z]+-\d+)\.\*\*", self.text, flags=re.M)
        self.assertEqual(len(ids), len(set(ids)), ids)

    def test_each_wfo_named_is_defined(self):
        defined = set(re.findall(r"^- \*\*(WFO-\d+)\.\*\*", self.text, flags=re.M))
        named = set(re.findall(r"\bWFO-\d+\b", self.text))
        self.assertEqual(named - defined, set())

    def test_wfo_13_decides_the_end_after_layer_2(self):
        """WFO-13 follows ORC-10: no comparison, a list that cannot be read, or no change of a norm, of a
        derived norm or of the order of the types."""
        clause = self.text.split("- **WFO-13.**", 1)[1].split("\n- **", 1)[0]
        for needed in ("ORC-10", "NRM-11", "NRM-12", "data/report.json", "commit before the last step",
                       "no norm changed, no derived norm changed and the order of the types did not change"):
            self.assertIn(needed, clause)

    def wfo_13_with_code_blocks(self):
        return read(SPEC).split("- **WFO-13.**", 1)[1].split("\n- **WFO-4.**", 1)[0]

    def test_wfo_13_a_step_with_no_commit_is_compared_as_if_it_had_made_it(self):
        """NRM-11 rule 1: with no commit, the head from before the step is the commit of layer 2 of the run."""
        clause = self.wfo_13_with_code_blocks()
        self.assertIn("the commit of layer 2 of the run is the head before the step of layer 2, as NRM-11 says", clause)
        self.assertNotIn("no derived norm changed, as NRM-11 says", clause)
        self.assertNotIn("Accepted cost", clause)

    def test_wfo_13_after_a_pull_compares_the_commit_of_the_step(self):
        """NRM-11: after a pull of NRM-10, the commit of the step is compared, never the merge commit."""
        clause = self.wfo_13_with_code_blocks()
        for needed in ("it walks the first parents from the head after the step of layer 2",
                       "the first commit that is the head before the step of layer 2 or one of its ancestors",
                       "the merge commit of a pull of [NRM-10]",
                       "When exactly one commit of the step has one parent, it is the commit that the step made, "
                       "and it is the commit of layer 2 of the run, never the merge commit of the pull",
                       "workflow-orchestration: the commit of layer 2 of the run cannot be found between <before> "
                       "and <after> of the norms repository (NRM-11): <count> commits of the step have one parent, "
                       "and one must; the run stops after layer 2"):
            self.assertIn(needed, clause)
        self.assertNotIn("it reads that head again: it is the commit of layer 2 of the run", clause)
        find = clause.index("It then finds the commit of layer 2 of the run")
        compare = clause.index("the files of the norms repository at the commit of layer 2 of the run")
        self.assertLess(find, compare)

    def test_the_head_after_the_step_of_layer_2_is_not_the_commit_of_layer_2(self):
        """SPC-3: the head after the step and the commit of layer 2 of the run are two terms."""
        terms = self.text.split("## Terms", 1)[1].split("\n## ", 1)[0]
        self.assertIn("| Head before the step of layer 2 |", terms)
        self.assertIn("| Head after the step of layer 2 |", terms)
        self.assertIn("after a pull of NRM-10 it is the merge commit of the pull", terms)
        self.assertIn("commit of layer 2 of the run and commit before the last step are those of [norms-management]"
                      "(../../norms-management/specs/module.md#terms)", terms)
        norms_management = read(os.path.join(PLUGIN, "..", "norms-management", "specs", "module.md"))
        self.assertIn("| Commit of layer 2 of the run |", norms_management)

    def test_the_types_of_derived_norms_of_a_commit_is_a_term_of_norms_management(self):
        """SPC-3: WFO-13 uses the term types of derived norms of a commit; the module takes it from
        norms-management, where it is defined, and defines no meaning of its own."""
        terms = self.text.split("## Terms", 1)[1].split("\n## ", 1)[0]
        self.assertIn("the terms list of derived norms, derived norm behind its norms, types of derived norms of a "
                      "commit, commit of layer 2 of the run and commit before the last step are those of "
                      "[norms-management]"
                      "(../../norms-management/specs/module.md#terms)", terms)
        self.assertNotIn("| Types of derived norms", terms)
        self.assertIn("the types of derived norms of <commit>", self.wfo_13_with_code_blocks())
        norms_management = read(os.path.join(PLUGIN, "..", "norms-management", "specs", "module.md"))
        self.assertIn("| Types of derived norms of a commit |", norms_management)

    def test_a_commit_of_layer_2_that_cannot_be_found_is_a_stop_of_wfo_13(self):
        clause = self.wfo_13_with_code_blocks()
        cannot_find = clause.index("cannot be found between")
        end = clause.index("Otherwise, when no norm changed, no derived norm changed and the order of the types did not change, the run ends")
        self.assertLess(cannot_find, end)

    def test_wfo_13_a_list_that_cannot_be_read_stops_the_run(self):
        """ORC-10 case 1 and NRM-11: a list that cannot be read at the commit of layer 2 stops the run."""
        clause = self.wfo_13_with_code_blocks()
        self.assertIn("Otherwise, when a list cannot be read at the commit of layer 2 of the run (NRM-11, rule 5), "
                      "the run stops before the step of layer 3.", clause)
        self.assertIn("workflow-orchestration: the list of derived norms of the type <type>, <path>, cannot be read "
                      "at <commit> of the norms repository (NRM-11): <why>; the run stops after layer 2 (ORC-10)",
                      clause)
        self.assertIn("as NRM-12 says of a list read alone", clause)

    def test_wfo_13_the_why_of_a_list_that_cannot_be_read_follows_nrm_11(self):
        """NRM-11 rules 5 and 7: `<why>` names the first thing of NRM-12, or of the check against data/tree.jsonl,
        that the list does not meet; WFO-13 restates neither (DEV-4)."""
        clause = self.wfo_13_with_code_blocks()
        step_5 = clause.split("  5. Otherwise, when a list cannot be read", 1)[1].split("\n  6. ", 1)[0]
        self.assertIn("`<why>` `it does not exist` when the list does not exist at that commit, and otherwise "
                      "the first thing of NRM-12, or of the check against `data/tree.jsonl`, that the list does not "
                      "meet, as rule 7 of NRM-11 says, in the words of the table of rule 7 of NRM-11 and of the "
                      "cases of the check against `data/tree.jsonl` below that table", step_5)
        self.assertNotIn("use case `run`", step_5)
        for restated in ("never what of NRM-12 it does not meet there", "begins with a byte order mark",
                         "greater than `last_derived_norm_number`", "line <n> does not meet NRM-12"):
            self.assertNotIn(restated, step_5)
        norms_management = read(os.path.join(PLUGIN, "..", "norms-management", "specs", "module.md"))
        self.assertIn("the first thing of these that the list does not meet, in the words of rule 7", norms_management)
        self.assertNotIn("cites EXP-11@e105eaa8, and the norm hash", step_5)
        self.assertNotIn("counts as a change of a derived norm", clause)
        self.assertNotIn("cannot be compared", clause)
        wfo_7 = self.text.split("- **WFO-7.**", 1)[1].split("\n- **", 1)[0]
        self.assertIn("WFO-13", wfo_7)

    def test_wfo_13_a_derived_norm_behind_its_norms_stops_the_run(self):
        """NRM-11 rule 5, ORC-10, LAY-12: the orchestrator checks the lists of the commit of layer 2 of the run
        against data/tree.jsonl of that commit, as NRM-11 says, so that a derived norm behind its norms stops the run."""
        step_3 = self.wfo_13_with_code_blocks().split("\n  3. ", 1)[1].split("\n  4. ", 1)[0]
        self.assertIn("against `data/tree.jsonl` of that commit, as rule 5 of NRM-11 says, so that a derived norm "
                      "behind its norms stops the run", step_3)
        norms_management = read(os.path.join(PLUGIN, "..", "norms-management", "specs", "module.md"))
        self.assertIn("| Derived norm behind its norms |", norms_management)

    def test_wfo_13_compares_with_the_commit_before_the_last_step_by_every_rule_of_nrm_11(self):
        """NRM-11 binds the script of the orchestrator: the commit before the last step, never the first parent,
        and every rule, with no restated one."""
        clause = self.wfo_13_with_code_blocks()
        step_3 = clause.split("\n  3. ", 1)[1].split("\n  4. ", 1)[0]
        for needed in ("by every rule of NRM-11, and by no other",
                       "which is the commit before the last step, not merely the first parent of the commit of "
                       "layer 2 of the run",
                       "the types compared and their order", "`new`, `changed` and `gone`",
                       "the change of the order of the types", "the commit that gives no comparison",
                       "only as NRM-12 says of a list read alone"):
            self.assertIn(needed, step_3)
        for outdated in ("at its first parent", "For each type of `derived_norms` of `project.json`"):
            self.assertNotIn(outdated, clause)
        norms_management = read(os.path.join(PLUGIN, "..", "norms-management", "specs", "module.md"))
        nrm_11 = norms_management.split("- **NRM-11.**", 1)[1].split("\n- **", 1)[0]
        self.assertIn("with the commit before the last step", nrm_11)
        self.assertIn("the one with which the orchestrator decides ORC-10", nrm_11)
        terms = self.text.split("## Terms", 1)[1].split("\n## ", 1)[0]
        self.assertIn("commit before the last step are those of [norms-management]", terms)
        self.assertIn("| Commit before the last step |", norms_management)

    def test_wfo_13_no_comparison_stops_the_run(self):
        """NRM-11 rule 2 and ORC-10 case 1: a commit of layer 2 of the run that gives no comparison stops the run."""
        clause = self.wfo_13_with_code_blocks()
        self.assertIn("When the commit of layer 2 of the run gives no comparison (NRM-11, rule 2), the run stops "
                      "before the step of layer 3", clause)
        self.assertIn("workflow-orchestration: the types of derived norms of <commit> of the norms repository cannot "
                      "be read (NRM-11): <reason>; the run stops after layer 2 (ORC-10)", clause)
        step_4 = clause.split("\n  4. ", 1)[1].split("\n  5. ", 1)[0]
        self.assertIn("`<reason>` the words of the first case of the list of rule 7.2 of NRM-11 that holds", step_4)

    def test_wfo_13_the_reason_of_no_comparison_covers_every_case_of_nrm_11_from_github(self):
        """NRM-11 rules 2 and 7.2: the reasons of no comparison that a commit read from GitHub can meet are
        complete, the parents of a commit of the walk included, and their words stay in NRM-11 (DEV-4)."""
        step_4 = self.wfo_13_with_code_blocks().split("\n  4. ", 1)[1].split("\n  5. ", 1)[0]
        self.assertIn("A commit read from GitHub can meet only the last three cases of that list, in its order "
                      "(complete list): the parents of a commit of the walk along the first parents cannot be read, "
                      "`project.json` cannot be read at that commit, and its `derived_norms` does not meet", step_4)
        for restated in ("`project.json cannot be read`", "`derived_norms of project.json does not meet ORC-20`",
                         "`the parents of <commit of the walk> cannot be read`", "otherwise:"):
            self.assertNotIn(restated, step_4)
        norms_management = read(os.path.join(PLUGIN, "..", "norms-management", "specs", "module.md"))
        nrm_11 = norms_management.split("- **NRM-11.**", 1)[1].split("\n- **", 1)[0]
        self.assertIn("`the parents of <commit of the walk> cannot be read`, in its 40 hex digits; "
                      "`project.json cannot be read`; `derived_norms of project.json does not meet ORC-20`", nrm_11)

    def test_wfo_13_a_new_order_of_the_types_goes_on_with_layer_3(self):
        """NRM-11 rule 6 and ORC-10 case 2: the run ends only when the order of the types did not change either."""
        clause = self.wfo_13_with_code_blocks()
        self.assertIn("Otherwise, when no norm changed, no derived norm changed and the order of the types did not change, the run ends", clause)
        self.assertIn("workflow-orchestration: no norm, no derived norm and no order of the types of derived norms "
                      "changed at <commit> of the norms repository; the run ends after layer 2 (ORC-10)", clause)
        self.assertNotIn("Otherwise, when no norm and no derived norm changed", clause)
        norms_management = read(os.path.join(PLUGIN, "..", "norms-management", "specs", "module.md"))
        orc_10 = norms_management.split("- **ORC-10.**", 1)[1].split("\n- **", 1)[0]
        self.assertIn("no change of the order of the types", orc_10)

    def test_wfo_13_follows_the_order_of_the_cases_of_orc_10(self):
        """ORC-10: the first case that holds; the stops first, then the end, then layers 3 and 4."""
        clause = self.wfo_13_with_code_blocks()
        no_comparison = clause.index("gives no comparison (NRM-11, rule 2), the run stops before the step of layer 3")
        stop = clause.index("Otherwise, when a list cannot be read")
        end = clause.index("Otherwise, when no norm changed, no derived norm changed and the order of the types did not change, the run ends")
        layer_3 = clause.index("Otherwise the orchestrator starts the step of layer 3")
        self.assertLess(no_comparison, stop)
        self.assertLess(stop, end)
        self.assertLess(end, layer_3)

    def test_wfo_13_computes_the_inputs_of_orc_10_by_the_rules_of_nrm_11(self):
        """ORC-10 reads the report of NRM-11; WFO-13 computes the same by a script."""
        clause = self.wfo_13_with_code_blocks()
        for needed in ("ORC-10 reads two inputs", "by the rules of NRM-11",
                       "the lists of derived norms that cannot be read",
                       "the change of the order of the types", "the case of no comparison",
                       "never reads them from the last message of the headless session",
                       "Before it starts the headless session of the step",
                       "When the two heads are the same commit, the step made no commit"):
            self.assertIn(needed, clause)

    def test_wfo_13_a_read_from_github_that_fails_stops_the_run(self):
        """SPC-5 and SPC-6: a timeout, a failed connection, a refused or limited read, and an answer that cannot be
        read each stop the run with one exact message, and are never taken for a file that does not exist."""
        clause = self.wfo_13_with_code_blocks()
        reads = clause.split("The script reads GitHub through its REST API", 1)[1].split("Rationale:", 1)[0]
        for needed in ("makes each read once, with no retry",
                       "`no answer within 30 seconds`", "`the connection failed`", "`it does not exist`",
                       "`GitHub answered with status <status>`", "`the answer cannot be read`",
                       "credentials that GitHub refuses and a rate limit that is reached",
                       "to the read of a file at a commit, the file does not exist at that commit",
                       "the parents of the commit of the walk whose parent it is cannot be read",
                       "before the step of layer 2, with no headless session started, when it is the read of the "
                       "head before the step of layer 2, and otherwise before the step of layer 3",
                       "A read that fails is never a file that does not exist, a list that cannot be read nor a "
                       "commit that gives no comparison",
                       "workflow-orchestration: <what> of the norms repository cannot be read from GitHub: <why>; "
                       "the run stops <when>"):
            self.assertIn(needed, reads)
        step_2 = clause.split("\n  2. ", 1)[1].split("\n  3. ", 1)[0]
        self.assertIn("does not exist, which GitHub answers as the paragraph below these steps says", step_2)
        self.assertLess(clause.index("  7. Otherwise the orchestrator starts the step of layer 3"),
                        clause.index("The script reads GitHub through its REST API"))

    def test_evidence_lines_hold_derived_norm_fingerprints(self):
        clause = self.text.split("- **WFO-8.**", 1)[1].split("\n- **", 1)[0]
        self.assertIn("`derived_norm_fingerprints`", clause)

    def test_done_script_reads_the_lists_of_derived_norms(self):
        clause = self.text.split("- **WFO-10.**", 1)[1].split("\n- **", 1)[0]
        for needed in ("copy of the norms repository", "lists of derived norms", "ACU-26", "LAY-10"):
            self.assertIn(needed, clause)


class TestLinks(unittest.TestCase):
    def test_each_relative_link_reaches_a_section_that_defines_its_clauses(self):
        text = outside_code_blocks(read(SPEC))
        problems = []
        cache = {}
        for label, target in LINK.findall(text):
            if target.startswith("http"):
                continue
            path, _, anchor = target.partition("#")
            full = os.path.normpath(os.path.join(os.path.dirname(SPEC), path))
            if not os.path.isfile(full):
                problems.append(f"{target}: no such file")
                continue
            if not anchor:
                continue
            if full not in cache:
                cache[full] = sections(read(full))
            section = cache[full].get(anchor)
            if section is None:
                problems.append(f"{target}: no such heading")
                continue
            for clause_id in CLAUSE_ID.findall(label):
                if not defines(section, clause_id):
                    problems.append(f"{target}: {clause_id} is not defined in that section")
        self.assertEqual(problems, [])


if __name__ == "__main__":
    unittest.main()
