"""Tests of scripts/derived_norms.py, the module script, and of how the scripts of the use cases use it.

Run from the root of the marketplace:
    uv run --with pytest --with "lark[interegular]" python3 -I -B -m pytest -q -p no:cacheprovider \
        apps/clean-language/modules/clean-derived-norms/tests
Spec: specs/module.md (CDN-7). The functions of the module script are tested
by the tests of the use case whose rule they implement.
"""

import ast
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1]
MODULE_SCRIPT = MODULE / "scripts" / "derived_norms.py"
SCRIPTS_OF_THE_USE_CASES = sorted((MODULE / "use-cases").glob("*/*.py"))


def imported_modules(path):
    """The names of the modules that a file imports."""
    names = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            names |= {alias.name for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def test_cdn7_each_script_of_a_use_case_imports_the_module_script():
    assert [p.relative_to(MODULE).as_posix() for p in SCRIPTS_OF_THE_USE_CASES] == [
        "use-cases/derive-grammar/derive_grammar.py", "use-cases/derive-semantics/derive_semantics.py"]
    for path in SCRIPTS_OF_THE_USE_CASES:
        assert "derived_norms" in imported_modules(path), path


def test_cdn7_no_script_of_a_use_case_imports_the_script_of_another():
    stems = {p.stem for p in SCRIPTS_OF_THE_USE_CASES}
    for path in SCRIPTS_OF_THE_USE_CASES:
        text = path.read_text(encoding="utf-8")
        assert not (imported_modules(path) & (stems - {path.stem})), path
        assert "importlib" not in imported_modules(path), path
        for other in SCRIPTS_OF_THE_USE_CASES:
            if other != path:
                assert other.stem not in text, (path, other)


def test_cdn7_the_module_script_imports_no_script_of_a_use_case():
    assert not imported_modules(MODULE_SCRIPT) & {p.stem for p in SCRIPTS_OF_THE_USE_CASES}


def test_every_function_of_the_module_script_cites_its_rule():
    tree = ast.parse(MODULE_SCRIPT.read_text(encoding="utf-8"))
    missing = [n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.ClassDef))
               and not any(f"Spec: {prefix}-" in (ast.get_docstring(n) or "") for prefix in ("DGR", "DSM", "CDN"))]
    assert missing == []
