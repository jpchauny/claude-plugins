# norms

Layer 2, used in `<project>-norms`: the norms generator, common to every
project. It mirrors the whole layer 1 repository into `specs-repo-annotated/`, its Markdown annotated with stable norm IDs
([LAY-3](../../spec-driven-design-process/layers.md#lay-3--layer-2-is-regenerated-whole-from-layer-1-only)).

| Skill | What for |
|---|---|
| `/norms:build` | Regenerate layer 2 from layer 1, verify it, show the change report |
| `/norms:verify` | Check that layer 2 is exactly what the generator produces |

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
uvx --from "git+https://github.com/jpchauny/claude-plugins#subdirectory=plugins/norms" \
    norms-gen build --foundation <layer 1 repository>
```

## Develop

See [docs/development.md](docs/development.md).
