"""The rules "deny" of ACU-13, level 1, shared by create-project and sync.

create-project writes them when the project is created (ORC-5); sync keeps
them in step with project.json (SNC-1). Both import this file, so the rules
are computed in one place (DEV-4).
"""

TOOLS = ("Read", "Edit")


def folder(r: dict) -> str:
    """The folder of the repository `r`, its path, at any depth under the root.

    The project folder is written nowhere (ORC-20), and a rule of Claude Code
    matches only under its anchor, so the rule is anchored at the root of the
    file system.
    """
    return f"//**/{r['path']}/**"


def deny_rules(repos: list[dict], this: dict) -> list[str]:
    """The rules "deny" of the repository `this` (ORC-5).

    The acceptance repository may not read or edit a code repository; a code
    repository may not edit the acceptance repository; the other layers deny
    nothing, and neither do the repositories with a "role", which are no layer
    (SNC-2, SNC-3).
    """
    if this.get("layer") == 3:
        return [f"{tool}({folder(r)})" for r in repos if r.get("layer") == 4 for tool in ("Read", "Edit")]
    if this.get("layer") == 4:
        return [f"Edit({folder(r)})" for r in repos if r.get("layer") == 3]
    return []


def managed(*project_repos: list[dict]) -> set[str]:
    """The managed rules "deny" (SNC-1): "Read" or "Edit" of the folder of a
    repository of layer 3 or 4 of any of the given lists of repositories, which
    are the source, the project.json of the target before the sync and every
    version of it committed in the target.
    """
    return {f"{tool}({folder(r)})" for repos in project_repos for r in repos if r.get("layer") in (3, 4) for tool in TOOLS}


def merged(current: list[str], wanted: list[str], own: set[str]) -> list[str]:
    """The rules "deny" after a sync (SNC-1).

    The managed rules `own` are replaced by `wanted`; every other rule,
    written by a person, is kept unchanged, after them.
    """
    return wanted + [rule for rule in current if rule not in own and rule not in wanted]
