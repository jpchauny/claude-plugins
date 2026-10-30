"""SPC-3, DEV-4 and MTH-2 on the spec of the module drift-management."""

import re
from pathlib import Path

MODULE = Path(__file__).resolve().parent.parent
MODULES = MODULE.parent
SPEC_OF_THE_MODULE = MODULE / "specs" / "module.md"
LAYERS = MODULES / "development-methodology" / "specs" / "layers.md"

IMPORT = re.compile(r"the terms? ([^.;]+?) (?:are|is) (?:those|that) of \[[^\]]+\]\(([^)#]+)#terms\)", re.IGNORECASE)
TERM_ROW = re.compile(r"^\| ([^|]+?) \|", re.MULTILINE)


def terms_of(spec: Path) -> set[str]:
    return {name.strip().lower() for name in TERM_ROW.findall(spec.read_text(encoding="utf-8"))} - {"term", "---"}


def imported_terms() -> dict[str, Path]:
    text = SPEC_OF_THE_MODULE.read_text(encoding="utf-8")
    imported = {}
    for match in IMPORT.finditer(text):
        for name in re.split(r", | and ", match.group(1)):
            if name:
                imported[name.lower()] = (SPEC_OF_THE_MODULE.parent / match.group(2)).resolve()
    return imported


def orc_14() -> str:
    text = SPEC_OF_THE_MODULE.read_text(encoding="utf-8")
    return text[text.index("- **ORC-14.**"):]


def test_every_imported_term_is_defined_where_it_comes_from():
    """SPC-3: every term taken from another spec is in the table of terms of that spec."""
    imported = imported_terms()
    assert imported
    for name, source_spec in imported.items():
        assert name in terms_of(source_spec), f"{name} is not a term of {source_spec.relative_to(MODULES)}"


def test_orc_14_takes_the_terms_it_uses():
    """SPC-3: the terms of other specs that ORC-14 uses are taken in the preamble of the terms."""
    imported = imported_terms()
    for name in [
        "norm",
        "norm hash",
        "derived norm",
        "derived norm id",
        "derived norm fingerprint",
        "derived-norms generator",
        "status file",
        "list of derived norms",
        "acceptance unit",
        "scenario",
        "marketplace repository",
        "run",
    ]:
        assert name in imported, name


def test_marketplace_repository_is_the_term_used():
    """SPC-3: the repository of an issue of a defect of a derived-norms generator has one name, the term of define.md."""
    assert "the marketplace repository" in orc_14()
    for document in [SPEC_OF_THE_MODULE, MODULE / "README.md"]:
        text = document.read_text(encoding="utf-8")
        assert "repository of the marketplace" not in text, document.name
        assert "repository of the plugin of" not in text, document.name


def test_orc_14_cites_the_reason_of_lay_5_and_does_not_restate_it():
    """MTH-2, DEV-4: the reason of the exception of LAY-5 is written with LAY-5 only; ORC-14 cites it."""
    assert "misreads right norms" in LAYERS.read_text(encoding="utf-8")
    rationale = orc_14().split("Rationale:", 1)[1]
    assert "misreads right norms" not in rationale
    assert "already right" not in rationale
    assert "is the reason of [LAY-5]" in rationale


def test_orc_14_finds_the_marketplace_repository_as_acu_79_says():
    """DEV-4, SPC-2: the status file holds no repository; ORC-14 cites ACU-79 for how the marketplace repository is found."""
    issue_of_a_defect = orc_14().split("for every other drift", 1)[0]
    assert "read from the status file" not in issue_of_a_defect
    assert "installed_plugins.json" not in issue_of_a_defect
    assert "`generator` of the status file" in issue_of_a_defect
    assert "[ACU-79](../../acceptance-management/use-cases/define/specs/define.md#" in issue_of_a_defect


def test_orc_14_states_its_exceptions_with_the_general_statement():
    """SPC-11: the cases in which no issue is opened follow the general statement of ORC-14, each with the rule that specifies it."""
    rule = orc_14().split("Rationale:", 1)[0]
    general_statement = rule.index("opens one issue for it")
    exceptions = rule.index("Exceptions, in which the step opens no issue for the drift (complete list):")
    assert general_statement < exceptions
    listed = rule[exceptions:rule.index("The run ends there")]
    assert "does not say yes" in listed
    assert "`project.json` has not exactly one entry of layer 1" in listed
    assert "no status file of the type with a `generator`" in listed
    assert "no installed marketplace on GitHub holds the plugin" in listed
    assert "cannot be looked up" in listed
    assert "`gh issue create` fails" in listed
    for rule_id, spec in [
        ("ACU-68", "acceptance-management/use-cases/define/specs/define.md"),
        ("ACU-79", "acceptance-management/use-cases/define/specs/define.md"),
        ("IMP-10", "code-implementation/use-cases/implement/specs/implement.md"),
    ]:
        assert f"[{rule_id}](../../{spec}#" in listed, rule_id
        assert f"Rule: {rule_id} " in (MODULES / spec).read_text(encoding="utf-8"), rule_id
    assert "the run still ends for the norms and the derived norms it touches" in listed


def test_orc_14_gives_a_message_for_every_step_and_every_destination():
    """ORC-14: each case with no issue has its message, for the step of each layer and for each destination of the issue."""
    rule = orc_14().split("Rationale:", 1)[0]
    messages = rule[rule.index("The message is (complete list):"):rule.index("In each of the three")]
    define = (MODULES / "acceptance-management/use-cases/define/specs/define.md").read_text(encoding="utf-8")
    implement = (MODULES / "code-implementation/use-cases/implement/specs/implement.md").read_text(encoding="utf-8")
    acu_68 = define[define.index("Rule: ACU-68 "):define.index("Rule:", define.index("Rule: ACU-68 ") + 1)]
    imp_10 = implement[implement.index("Rule: IMP-10 "):implement.index("Rule:", implement.index("Rule: IMP-10 ") + 1)]
    for message_of_acu_68 in [
        "acceptance-management:define: project.json has not exactly one entry of layer 1, the specs repository; no issue is opened",
        "acceptance-management:define: cannot open the issue in ",
    ]:
        assert message_of_acu_68 in acu_68
        message_of_layer_4 = message_of_acu_68.replace("acceptance-management:define:", "code-implementation:implement:")
        assert message_of_layer_4 in messages
    # IMP-10 gives no message for a drift sent to layer 1; when it does, ORC-14 must cite it instead (DEV-4).
    assert "exactly one entry" not in imp_10
    for given in re.findall(r'Given "gh issue create" fails for (.+)', imp_10):
        assert "defect of a derived-norms generator" in given
    assert "for the step of acceptance-management:" in messages
    assert "for the step of code-implementation, for a defect of a derived-norms generator:" in messages
    assert "for the step of code-implementation, for a drift sent to layer 1:" in messages
    assert "because IMP-10 gives none for a drift sent to layer 1" in messages
