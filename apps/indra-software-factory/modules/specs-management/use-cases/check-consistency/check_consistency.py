"""The deterministic part of /specs-management:check-consistency.

Spec: use-cases/check-consistency/specs/check-consistency.md (CNS-1 to CNS-8).
The repositories, the trees and the git helpers are those of scripts/move.py,
the links those of scripts/layers.py, the paths those of scripts/spec_paths.py.

Usage (python3 -I, from any folder):

    check_consistency.py scope <repository> [--part N] -- <path>

<repository> is the root of the repository the session runs in. `scope` writes
nothing (CNS-7). It prints, as JSON: `roots` ("0" and "1", the roots of
layers 0 and 1), `checked_spec` ({layer, path}, CNS-3), `files_of_the_check`
(each other file of the check, {layer, path}, CNS-4) and `broken_links` (each
link of the checked spec whose link target exists in neither layer, {line,
target, absent, quote}). A refusal of CNS-2 or CNS-3 is one line
`specs-management:check-consistency: ...`, exit 1. An output longer than
20000 characters comes in parts: {part, parts, text}, the texts joined in part
order being the JSON; a --part out of range exits 2 with `the output has <m>
parts`.
"""

import json
import os
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "scripts"))
import layers  # noqa: E402
import mdlinks  # noqa: E402
import move  # noqa: E402
from move import Refused, decode, head_files  # noqa: E402
from spec_paths import SPECIAL, exists_in_either_layer, is_folder, md_paths, valid_spec_path  # noqa: E402

USE_CASE = "check-consistency"
PART = 20000


def say(text):
    return f"specs-management:{USE_CASE}: {text}"


def code_point_key(path):
    return path.encode("utf-8", "surrogateescape")


def checked_spec_layer(path, layer_of_repository, trees):
    """CNS-3: the layer of the repository the session runs in when its HEAD tracks the path, else the other."""
    if not valid_spec_path(path) or is_folder(trees[0], path) or is_folder(trees[1], path):
        raise Refused([say(f"{path}: invalid path")])
    other_layer = 1 - layer_of_repository
    for layer in (layer_of_repository, other_layer):
        if path in trees[layer] and trees[layer][path][0] not in SPECIAL:
            return layer
    raise Refused([say(f"{path}: not in layer 0 or layer 1")])


def lines_of(text):
    """The lines of a text as mdlinks numbers them."""
    lines = mdlinks.EOL.split(text)
    return lines[:-1] if lines and lines[-1] == "" else lines


def scope(repository, path):
    repositories = move.find_repos(repository, USE_CASE)
    trees = {layer: head_files(repositories[layer]) for layer in (0, 1)}
    layer_of_repository = 0 if repository.resolve() == repositories[0] else 1
    layer = checked_spec_layer(path, layer_of_repository, trees)
    files_of_the_check = [dict(layer=other_layer, path=p)
                          for other_layer in (0, 1)
                          for p in sorted(md_paths(trees[other_layer]), key=code_point_key)
                          if (other_layer, p) != (layer, path)]
    try:
        text_of_checked_spec = decode((repositories[layer] / path).read_bytes())
    except OSError:
        raise Refused([say(f"{path}: not in layer 0 or layer 1")])
    lines = lines_of(text_of_checked_spec)
    broken_links = []
    for link, absent, target in layers.layer_links(path, text_of_checked_spec):
        if not exists_in_either_layer(trees, target):
            line = link["line"]
            broken_links.append(dict(line=line, target=target, absent=absent,
                                     quote=lines[line - 1] if 0 < line <= len(lines) else ""))
    return dict(roots={"0": str(repositories[0]), "1": str(repositories[1])},
                checked_spec=dict(layer=layer, path=path),
                files_of_the_check=files_of_the_check,
                broken_links=broken_links)


def dumps(value, **kw):
    """JSON with each non-ASCII character as it is; a lone surrogate keeps its \\u escape."""
    text = json.dumps(value, ensure_ascii=False, **kw)
    return re.sub("[\ud800-\udfff]", lambda m: "\\u%04x" % ord(m.group(0)), text)


def main(argv):
    if len(argv) < 2 or argv[0] != "scope" or "--" not in argv:
        print(__doc__, file=sys.stderr)
        return 2
    repository = Path(argv[1]).resolve()
    options, paths = argv[2:argv.index("--")], argv[argv.index("--") + 1:]
    part = 1
    if options:
        if len(options) != 2 or options[0] != "--part" or not options[1].isdigit():
            print(__doc__, file=sys.stderr)
            return 2
        part = int(options[1])
    try:
        if len(paths) != 1:
            move.find_repos(repository, USE_CASE)
            raise Refused([say("expected one path")])
        result = scope(repository, paths[0])
    except Refused as e:
        print("\n".join(e.lines))
        return 1
    except (RuntimeError, OSError) as e:
        print(say(f"git failed: {e}"))
        return 1
    text = dumps(result, indent=1)
    if len(text) > PART:
        chunks = [text[i:i + PART] for i in range(0, len(text), PART)]
        if not 1 <= part <= len(chunks):
            print(f"the output has {len(chunks)} parts")
            return 2
        text = dumps(dict(part=part, parts=len(chunks), text=chunks[part - 1]))
    elif part != 1:
        print("the output has 1 parts")
        return 2
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
