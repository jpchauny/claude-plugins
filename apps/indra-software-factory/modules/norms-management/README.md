# norms-management

Layer 2, used in the repository of layer 2: the norms generator, common to every
project. It mirrors the whole layer 1 repository into `specs-repo-annotated/`, its Markdown annotated with stable norm IDs, which makes it norms
([LAY-3](../development-methodology/specs/layers.md#rules)). The derived
norms of each type of the project go to `specs-derived/<type>/`, listed with
their derived norm IDs and derived norm fingerprints in
`specs-derived/<type>/derived-norms.jsonl`
([NRM-12](specs/module.md#the-list-of-derived-norms)).

| Skill | What for |
|---|---|
| `/norms-management:build` | Regenerate layer 2 from layer 1, verify it, run the derived-norms generators, commit, and show the change report: the norms that changed by norm ID, and the derived norms new, changed and gone by derived norm ID |
| `/norms-management:verify` | Check that layer 2 is exactly what the generator produces |

## Map

| Path | What it is |
|---|---|
| [specs/](specs/) | The generator's specification: the source of truth for its output |
| [use-cases/](use-cases/) | The skills, and the scripts of `build` that write the record of the types of derived norms and compare the lists of derived norms of the commit of layer 2 of the run with those of the commit before the last step |
| [src/norms_generator/](src/norms_generator/) | The generator, a Python package with the command `norms-gen` |
| [tests/](tests/) | Its tests, one or more per requirement and example of the specs |
| [docs/](docs/) | How to develop the generator, its implementation decisions, and the generated traceability from requirements to code and tests |

## Without Claude Code

Automation, such as a CI job, installs the generator straight from this
repository, with [uv](https://docs.astral.sh/uv/):

```sh
uvx --from "git+https://github.com/jpchauny/indra-software-factory#subdirectory=apps/indra-software-factory/modules/norms-management" \
    norms-gen build --specs <layer 1 repository>
```

## Develop

See [docs/development.md](docs/development.md).
