# CLAUDE.md

## What this repository is

The tooling repository of `{{project}}`: no layer. It holds the project's own
code, its plugins, such as the derived-norms generators of layer 2 and the
helpers of layers 0 and 1, with their specs and their tests, and is the Claude
Code marketplace `{{repository}}` from which the repositories of the layers
install them ([LAY-14](https://github.com/jpchauny/indra-software-factory/blob/main/apps/indra-software-factory/modules/development-methodology/specs/layers.md#the-tooling-repository)). The
repositories of layers 0 to 3 hold no tool ([LAY-13](https://github.com/jpchauny/indra-software-factory/blob/main/apps/indra-software-factory/modules/development-methodology/specs/layers.md#rules)).

{{repositories}}

## Working here

- Develop with the meta methodology, by [development.md](https://github.com/jpchauny/indra-software-factory/blob/main/specs/development.md), cited here and never copied: every change starts in a meta spec, the person approves it, and the implementation follows from it alone. Write each meta spec by [writing-specs.md](https://github.com/jpchauny/indra-software-factory/blob/main/specs/writing-specs.md).
- Never develop here with the modules of Indra Software Factory: none but `utilities` is enabled, and these specs are no layer 1, have no norm and go through no run.
- Each plugin is listed in `.claude-plugin/marketplace.json`, and has a `version` in its `.claude-plugin/plugin.json`; a derived-norms generator changes its `version` whenever its behaviour changes ([NRM-5 and NRM-7](https://github.com/jpchauny/indra-software-factory/blob/main/apps/indra-software-factory/modules/norms-management/specs/module.md#derive-the-derived-norms)).
- A repository of a layer that uses a plugin of this repository installs it in its `.claude/settings.json`: the marketplace in `extraKnownMarketplaces`, as `"{{repository}}": {"source": {"source": "github", "repo": "{{owner}}/{{repository}}"}}`, and the plugin in `enabledPlugins`, as `"<plugin>@{{repository}}": true` ([LAY-14](https://github.com/jpchauny/indra-software-factory/blob/main/apps/indra-software-factory/modules/development-methodology/specs/layers.md#the-tooling-repository)).
- Open this repository alone in its VS Code window: a folder added to the same workspace becomes readable and writable from the session.

## Issues

Pending items and findings go to the issue tree with `/utilities:issue`.
