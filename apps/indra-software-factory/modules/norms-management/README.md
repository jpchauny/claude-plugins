# norms-management

Layer 2, used in the repository of layer 2: the norms generator, common to every
project. It mirrors the whole layer 1 repository into `specs-repo-annotated/`, its Markdown annotated with stable norm IDs, which makes it norms
([LAY-3](../../specs/layers.md#lay-3--layer-2-is-derived-from-layer-1-only-and-only-what-changed-is-regenerated)).

| Skill | What for |
|---|---|
| `/norms-management:build` | Regenerate layer 2 from layer 1, verify it, show the change report |
| `/norms-management:verify` | Check that layer 2 is exactly what the generator produces |

## Map

| Path | What it is |
|---|---|
| [specs/](specs/) | The generator's specification: the source of truth for its output |
| [src/norms_generator/](src/norms_generator/) | The generator, a Python package with the command `norms-gen` |
| [tests/](tests/) | Its tests, one or more per requirement and example of the specs |
| [docs/](docs/) | How to develop the generator, its implementation decisions, and the generated traceability from requirements to code and tests |

## Without Claude Code

Automation, such as a CI job, installs the generator straight from this
repository, with [uv](https://docs.astral.sh/uv/):

```sh
uvx --from "git+https://github.com/jpchauny/claude-plugins#subdirectory=apps/indra-software-factory/modules/norms-management" \
    norms-gen build --specs <layer 1 repository>
```

## Develop

See [docs/development.md](docs/development.md).
