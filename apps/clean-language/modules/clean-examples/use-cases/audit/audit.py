"""The audit of the Clean examples of a layer: prints the report of CAU-8.

Spec: use-cases/audit/specs/audit.md (CAU-1 to CAU-9), specs/module.md (CEX-20).
Usage: python3 -I audit.py [<path>]   (run from the working directory)
"""

import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "scripts"))
import examples as ex  # noqa: E402


def selected(cwd, repo, files, arg):
    """CAU-3: the spec files that the argument selects."""
    if not arg:
        return files
    target = os.path.realpath(os.path.join(cwd, arg))
    rel = os.path.relpath(target, os.path.realpath(repo))
    if rel == ".":
        return files
    if rel == ".." or rel.startswith(".." + os.sep):
        return []
    return [p for p in files if p == rel or p.startswith(rel.rstrip("/") + "/")]


def run(cwd, arg=None):
    """The report, as text. Spec: CAU-3 to CAU-9."""
    repo = ex.toplevel(cwd)
    if repo is None:
        return "Audit of Clean examples: the working directory is in no git repository; nothing checked.\n"
    entry, other_path, other = ex.where(repo)
    if entry is None:
        return f"Audit of Clean examples: {other_path}; nothing checked.\n"  # CAU-4
    me = f"{entry['owner']}/{entry['name']}"
    files = ex.spec_files(repo)
    chosen = selected(cwd, repo, files, arg)
    if not chosen:
        return f"Audit of Clean examples in {me}: the argument selects no file; nothing checked.\n"
    notes, repos = [], [(None, repo)]
    layer1 = repo if entry["layer"] == 1 else other_path
    if other is None:
        notes.append(f"Not found: project.json lists no repository of layer {1 - entry['layer']}; CEX-15 to CEX-18 skipped.")
    elif ex.toplevel(other_path) == os.path.realpath(other_path):
        repos.append((f"{other['owner']}/{other['name']}", other_path))
    else:
        notes.append(f"Not found: the repository {other['owner']}/{other['name']}, expected at {other_path}; CEX-15 to CEX-18 skipped.")
    codes = ex.Codes(repos, layer1=layer1) if len(repos) == 2 else None
    if codes is not None and not codes.has_registry:
        notes.append(f"Not found: the registry, expected at {os.path.join(layer1, ex.REGISTRY)}; CEX-15 to CEX-18 skipped.")
        codes = None
    violations, suspects, count = [], [], 0
    for p in chosen:
        try:
            text = ex.read(os.path.join(repo, p))
        except OSError:
            continue
        for b in ex.blocks(text):
            if b.is_example():
                count += 1
            if b.fenced:
                pair = None if codes is None else (codes.defined(), codes.retired)
                for line, rule in ex.check_block(b, pair):
                    violations.append(("", p, line, rule))
            if ex.is_suspect(b):
                suspects.append((p, b.line))
    if codes is not None:
        for label, p, line, rule in codes.violations():
            violations.append((f"{label}:" if label else "", p, line, rule))
    violations = sorted(set(violations), key=lambda v: (v[0] + v[1], v[2], v[3]))
    suspects = sorted(set(suspects))
    out = [f"Audit of Clean examples in {me}: {count} Clean examples in {len(chosen)} selected files, "
           f"{len(violations)} violations, {len(suspects)} suspects.", ""]
    out += notes + ([""] if notes else [])
    out += ["## Violations", ""]
    out += [ex.finding(*v) for v in violations] or ["None."]
    out += ["", "## Suspects", ""]
    out += [f"- {p}:{line} · {ex.SUSPECT_MESSAGE}" for p, line in suspects] or ["None."]
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    sys.stdout.write(run(os.getcwd(), sys.argv[1] if len(sys.argv) > 1 else None))
