"""The paths of the spec files of layers 0 and 1, shared by /specs-management:write and
/specs-management:check-consistency.

Specs: use-cases/write/specs/write.md (ORC-60, its invalid path) and
use-cases/check-consistency/specs/check-consistency.md (CNS-3, term Files of the
check). The tree of a layer is that of move.head_files: path -> (mode, object id).
"""

import move

SPECIAL = ("120000", "160000")  # a symbolic link, a submodule


def valid_spec_path(path):
    """ORC-38, which ORC-60 and CNS-3 reuse for their invalid path; and the file is a .md file."""
    return bool(path) and not path.startswith("/") and not any(x in (".", "..", "") for x in path.split("/")) \
        and path.endswith(".md")


def is_folder(tree, path):
    return any(p.startswith(path + "/") for p in tree)


def md_paths(tree):
    """Each path of the tree whose name ends in .md, but a symbolic link and a submodule."""
    return [p for p in tree if p.endswith(".md") and tree[p][0] not in SPECIAL]


def exists_in_either_layer(trees, target):
    """Term Exists of module.md, in the tree of layer 0 or in that of layer 1."""
    return move.exists(trees[0], target) or move.exists(trees[1], target)
