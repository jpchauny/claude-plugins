"""The index of the development methodology, for every session (MTH-4 to MTH-10).

Usage:
    python3 -I index.py

Run by the SessionStart hook of the plugin development-methodology. Reads the
tables of layers and of modules in <plugin root>/specs/layers.md, where
<plugin root> is the folder that holds the folder scripts/ of this file, and
prints the index (MTH-6). When a table cannot be read, prints nothing on stdout, one line on
stderr, and exits with status 1 (MTH-8). Reads no other file, writes none,
runs no other program and uses no network (MTH-9). Python 3.9 or later,
standard library only (MTH-5).
"""

import os
import sys

LAYERS = ["Layer", "Recommended name", "Holds", "Written by"]
MODULES = ["Module", "Where"]
APP_URL = "https://github.com/jpchauny/claude-plugins/blob/main/apps/indra-software-factory/specs/app.md"


def plugin_root():
    """MTH-6: the folder that holds scripts/, from the script's own path, without a final '/'."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def cells(line):
    """The cells of one Markdown table row, without the spaces around each; None if it is no row."""
    line = line.strip()
    if not line.startswith("|"):
        return None
    inner = line[1:-1] if line.endswith("|") and len(line) > 1 else line[1:]
    return [cell.strip() for cell in inner.split("|")]


def is_separator(row):
    return bool(row) and all(cell and set(cell) <= set("-: ") and "-" in cell for cell in row)


def table(text, columns):
    """The rows of the first table with these columns (MTH Terms), or None when there is none or it has no row."""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if cells(line) != columns:
            continue
        if i + 1 >= len(lines) or not is_separator(cells(lines[i + 1]) or []):
            continue
        rows = []
        for row_line in lines[i + 2:]:
            row = cells(row_line)
            if row is None:
                break
            if len(row) != len(columns):
                return None
            rows.append(row)
        return rows or None
    return None


def index(root, layers, modules):
    """MTH-6: the index, line by line."""
    lines = [
        "Development methodology of Indra Software Factory (plugin development-methodology).",
        "This repository is one repository of a project: of one of its five layers, or its orchestration repository, which is no layer.",
        "The five layers:",
    ]
    for layer, name, holds, written_by in layers:
        lines.append("- %s: %s; written by: %s; repository: %s" % (layer, holds, written_by, name))
    lines.append("The modules of the app, each one a plugin, and where each is installed:")
    for module, where in modules:
        lines.append("- %s: %s" % (module, where))
    lines += [
        "Read for detail, before answering about the process:",
        ("- The five layers, the orchestration repository, the tooling repository, their rules, their terms, and where each "
         "module is installed: "
         "%s/specs/layers.md" % root),
        "- The flow across the layers (a run, its steps and hand-offs): %s/specs/flow.md" % root,
        "- What carries the methodology to every repository: %s/specs/module.md" % root,
        "- What each module of the app does: %s" % APP_URL,
    ]
    return "".join(line + "\n" for line in lines)


def main():
    root = plugin_root()
    path = os.path.join(root, "specs", "layers.md")
    try:
        with open(path, "rb") as f:
            text = f.read().decode("utf-8")
        layers, modules = table(text, LAYERS), table(text, MODULES)
    except (OSError, UnicodeDecodeError):
        layers = modules = None
    if layers is None or modules is None:
        message = ("development-methodology: cannot read the tables of layers and of modules in %s/specs/layers.md\n"
                   % root)
        sys.stderr.buffer.write(message.encode("utf-8"))
        sys.stderr.flush()
        return 1
    sys.stdout.buffer.write(index(root, layers, modules).encode("utf-8"))
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
