"""The hook of the plugin clean-examples: refuses a change that writes a malformed Clean example.

Spec: specs/module.md, CEX-22 to CEX-26, with the rules of CEX-20. A PreToolUse hook of Claude Code: it reads the tool call
as JSON on stdin; it exits 2 with the violations on stderr to refuse the change, and 0 otherwise.
"""

import json
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import examples as ex  # noqa: E402


def after_text(tool, inp, before):
    """The text of the file after the change, or None when the change cannot apply."""
    if tool == "Write":
        return inp.get("content")
    edits = [inp] if tool == "Edit" else inp.get("edits") if tool == "MultiEdit" else None
    if edits is None:
        return None
    text = before
    for e in edits:
        old, new = e.get("old_string", ""), e.get("new_string", "")
        if old == "":
            if text:
                return None
            text = new
            continue
        if old not in text:
            return None
        text = text.replace(old, new) if e.get("replace_all") else text.replace(old, new, 1)
    return text


def main(stdin):
    call = json.loads(stdin or "{}")
    tool, inp = call.get("tool_name"), call.get("tool_input") or {}
    path = inp.get("file_path") or inp.get("notebook_path")
    if tool not in ("Write", "Edit", "MultiEdit", "NotebookEdit") or not path or not path.endswith(".md"):
        return 0, "", ""
    path = os.path.realpath(path)
    near = os.path.dirname(path)
    while not os.path.isdir(near) and os.path.dirname(near) != near:
        near = os.path.dirname(near)
    repo = ex.toplevel(near)
    if repo is None or git_ignored(repo, path):
        return 0, "", ""
    entry, other_path, other = ex.where(repo)
    if entry is None:
        return 0, "", ""
    try:
        before = ex.read(path) if os.path.exists(path) else ""
    except OSError as e:
        return 0, json.dumps({"systemMessage": f"clean-examples: not checked, {path} not read: {e}"}), ""
    after = after_text(tool, inp, before)
    if after is None:
        return 0, "", ""
    message, codes = None, None
    layer1 = repo if entry["layer"] == 1 else other_path
    if other is None:
        message = f"clean-examples: CEX-15 to CEX-18 not checked, project.json lists no repository of layer {1 - entry['layer']}"
    elif ex.toplevel(other_path) == os.path.realpath(other_path):
        codes = ex.Codes([(None, repo), ("other", other_path)], {path: after}, layer1)
        if not codes.has_registry:
            message = f"clean-examples: CEX-15 to CEX-18 not checked, the registry not read at {os.path.join(layer1, ex.REGISTRY)}"
            codes = None
    else:
        message = f"clean-examples: CEX-15 to CEX-18 not checked, the other repository not found at {other_path}"
    pair = None if codes is None else (codes.defined(), codes.retired)
    rel = os.path.relpath(path, repo)
    new = ex.new_blocks(before, after)
    found = {(line, rule) for b in new for line, rule in ex.check_block(b, pair)}
    opening_lines = {b.line for b in new}
    found |= {(line, rule) for line, rule in ex.check_outputs(after) if line in opening_lines}  # CEX-27, CEX-28
    found = sorted(found)
    out = json.dumps({"systemMessage": message}) if message else ""
    if found:
        lines = [f"clean-examples refused the change: {len(found)} violations in new Clean examples."]
        lines += [ex.finding("", rel, line, rule) for line, rule in found]
        lines.append("The rules are in the plugin clean-examples, specs/module.md.")
        if message:
            lines.append(message)
        return 2, out, "\n".join(lines) + "\n"
    return 0, out, ""


def git_ignored(repo, path):
    import subprocess
    r = subprocess.run(["git", "-C", repo, "check-ignore", "-q", path], capture_output=True)
    return r.returncode == 0


if __name__ == "__main__":
    code, out, err = main(sys.stdin.read())
    if out:
        sys.stdout.write(out)
    if err:
        sys.stderr.write(err)
    sys.exit(code)
