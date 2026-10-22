# Project management

**Audience:** The people who use the app; whoever builds a use case of the plugin `project-management`

**Scope:** The module `project-management`: the three repositories of a project, their creation and their life cycle. For now, only their creation is specified

The module `project-management` of the app Indra Software Factory, listed in [app.md](../../../specs/app.md).

## Terms

| Term | Meaning |
|---|---|
| Project | The three repositories `<project>-specs`, `<project>-norms` and `<project>-code`. |

## Use cases

| Use case | Spec |
|---|---|
| `create-project` | [create-project.md](../use-cases/create-project/specs/create-project.md) |

## Where the three repositories are

- **ORC-20.** The three repositories of a project are sibling folders, `<project>-specs`, `<project>-norms` and `<project>-code`, as the creation leaves them ([ORC-5](../use-cases/create-project/specs/create-project.md#create-a-project)). There is no configuration of their paths. Every skill that needs one of them looks for it there, and when it is not there asks the user for its path.
