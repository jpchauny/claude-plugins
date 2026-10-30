"""SPC-3: every term that a spec of the module takes from another spec is in the table of terms of that spec."""

import re
from pathlib import Path

import pytest

MODULE = Path(__file__).resolve().parent.parent
MODULES = MODULE.parent

SPECS_OF_THE_MODULE = [
    MODULE / "specs" / "module.md",
    MODULE / "use-cases" / "implement" / "specs" / "implement.md",
]

IMPORT = re.compile(r"the terms? ([^.;]+?) (?:are|is) (?:those|that) of \[[^\]]+\]\(([^)#]+)#terms\)", re.IGNORECASE)
TERM_ROW = re.compile(r"^\| ([^|]+?) \|", re.MULTILINE)


def terms_of(spec: Path) -> set[str]:
    return {name.strip().lower() for name in TERM_ROW.findall(spec.read_text(encoding="utf-8"))} - {"term", "---"}


def imports_of(spec: Path):
    text = spec.read_text(encoding="utf-8")
    for match in IMPORT.finditer(text):
        names = [name for name in re.split(r", | and ", match.group(1)) if name]
        yield names, (spec.parent / match.group(2)).resolve()


@pytest.mark.parametrize("spec", SPECS_OF_THE_MODULE, ids=lambda spec: spec.name)
def test_every_imported_term_is_defined_where_it_comes_from(spec):
    imports = list(imports_of(spec))
    assert imports, f"{spec.name} takes no term from another spec"
    for names, source_spec in imports:
        defined = terms_of(source_spec)
        missing = [name for name in names if name.lower() not in defined]
        assert not missing, f"{spec.name} takes {missing} from {source_spec.relative_to(MODULES)}, which does not define them"


def test_run_of_code_citations_is_the_term_used():
    for spec in SPECS_OF_THE_MODULE:
        assert "run of citation lines" not in spec.read_text(encoding="utf-8"), spec.name


def test_marketplace_repository_is_the_term_used():
    """SPC-3: the repository of an issue of a defect of a derived-norms generator has one name, the term of define.md."""
    implement = SPECS_OF_THE_MODULE[1].read_text(encoding="utf-8")
    assert "marketplace repository" in implement
    for spec in [*SPECS_OF_THE_MODULE, MODULE / "README.md"]:
        text = spec.read_text(encoding="utf-8")
        assert "repository of the plugin of" not in text, spec.name
        assert "repository of the marketplace" not in text, spec.name


def test_au_11_cites_the_unit_hash_of_its_file():
    """ACU-52, ACU-56: AU-11 of ACU-8 has the unit hash a596f507, and 7b0d942f with the part ## Derived norms of ACU-78."""
    implement = SPECS_OF_THE_MODULE[1].read_text(encoding="utf-8")
    for line in implement.splitlines():
        if "AU-11 of ACU-8 with the part" in line:
            assert "a596f507" not in line, line
            assert "7b0d942f" in line or "<unit hash>" in line, line
        if "which holds no \"## Derived norms\"" in line:
            assert "7b0d942f" not in line and "a596f507" in line, line


def test_the_types_of_derived_norms_come_from_the_types_of_derived_norms_of_a_commit():
    """CIM-9, CIM-10, NRM-16: the types of derived norms of a commit come from its record, not from derived_norms of project.json."""
    module = SPECS_OF_THE_MODULE[0].read_text(encoding="utf-8")
    for clause in ("CIM-9", "CIM-10"):
        start = module.index(f"- **{clause}.**")
        end = module.index("\n- **", start + 1)
        text_of_clause = module[start:end]
        assert "types of derived norms" in text_of_clause, clause
        assert "`derived_norms`" not in text_of_clause, clause
    for spec in SPECS_OF_THE_MODULE:
        text = spec.read_text(encoding="utf-8")
        assert '"derived_norms" of "project.json"' not in text, spec.name
        assert "types of derived norms of a commit" in text, spec.name


def test_acceptance_architect_and_implementing_agent_are_taken_from_acceptance_management():
    """SPC-3: module.md uses acceptance architect and implementing agent, so it takes them from acceptance-management."""
    module = SPECS_OF_THE_MODULE[0].read_text(encoding="utf-8")
    taken = {name.lower() for names, source_spec in imports_of(SPECS_OF_THE_MODULE[0])
             if source_spec.parent.parent.name == "acceptance-management" for name in names}
    for term in ("acceptance architect", "implementing agent"):
        assert term in module
        assert term in taken, term


CLAUSE_OF_ANOTHER_SPEC = re.compile(r"\b((?:LAY|ORC|CIM|ACU|NRM|PLN)-\d+)\b")


def test_every_clause_of_another_spec_cited_by_implement_is_in_the_complete_list_of_its_scope():
    """SPC-3: the Scope of implement.md lists every clause of another spec that its rules cite (for example ACU-62)."""
    implement = SPECS_OF_THE_MODULE[1].read_text(encoding="utf-8")
    scope = next(line for line in implement.splitlines() if line.startswith("**Scope:**"))
    clauses_in_the_complete_list = set(CLAUSE_OF_ANOTHER_SPEC.findall(scope.split("(complete list):", 1)[1]))
    rules = implement.split("\n## Terms", 1)[1]
    clauses_cited_by_the_rules = set(CLAUSE_OF_ANOTHER_SPEC.findall(rules))
    missing = sorted(clauses_cited_by_the_rules - clauses_in_the_complete_list)
    assert not missing, f"implement.md cites {missing} without listing them in its Scope"


BARE_FINGERPRINT = re.compile(r"(?<!derived norm )\bfingerprints?\b", re.IGNORECASE)


def test_derived_norm_fingerprint_is_never_a_bare_fingerprint():
    """SPC-3: fingerprint is a term of acceptance-management (ACU-51); the module only takes derived norm fingerprint."""
    for spec in [*SPECS_OF_THE_MODULE, MODULE / "README.md"]:
        for line in spec.read_text(encoding="utf-8").splitlines():
            line = line.replace("derived_norm_fingerprint", "")
            assert not BARE_FINGERPRINT.search(line), f"{spec.name}: {line}"


def test_the_states_of_orc_25_are_those_of_a_citation_of_an_acceptance_unit():
    """SPC-2, SPC-11: the complete list of states of ORC-25 is for a citation of an acceptance unit; CIM-9 gives those of a derived norm citation."""
    module = SPECS_OF_THE_MODULE[0].read_text(encoding="utf-8")
    start = module.index("- **ORC-25.**")
    text_of_clause = module[start:module.index("\n- **", start + 1)]
    assert "Each citation gets one state" not in text_of_clause
    assert "Each citation of an acceptance unit gets one state (complete list)" in text_of_clause
    assert "each derived norm citation gets the one of CIM-9" in text_of_clause


def test_every_case_of_derived_norms_that_cannot_be_read_has_its_message_word_for_word():
    """ACU-78, SPC-5, SPC-6: implement words, byte for byte, the message of each case in which the derived norms cannot be read."""
    implement = SPECS_OF_THE_MODULE[1].read_text(encoding="utf-8")
    start = implement.index("Scenario Outline: The derived norms of the commit of the norms repository cannot be read")
    scenario = implement[start:implement.index("\n  Rule: ", start)]
    assert 'it says "code-implementation:implement: <message>"' in scenario
    assert "byte for byte" in scenario
    for message in (
        "| acme/billing-norms: the types of derived norms at 9fceb02 cannot be read (NRM-16) |",
        "| acme/billing-norms has no specs-derived/grammar/derived-norms.jsonl at 9fceb02 |",
        "| acme/billing-norms: specs-derived/grammar/derived-norms.jsonl does not meet NRM-12 |",
    ):
        assert message in scenario, message
    assert "it says that it cannot read the list of derived norms" not in implement
