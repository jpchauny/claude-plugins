# Code implementation

**Audience:** The people who run a project's flow from specs to code; whoever builds the skills of the plugin `code-implementation`

**Scope:** Layer 3: code built from the norms and the derived norms, and its traceability to norm IDs. What every use case of the module does before it implements anything is here; how a task is implemented is in [implement.md](../use-cases/implement/specs/implement.md)

The module `code-implementation` of the app Indra Software Factory, listed in [app.md](../../../specs/app.md). The terms citation, norm, norm ID, norm hash, code repository and norms repository are those of [implement.md](../use-cases/implement/specs/implement.md#terms).

## Terms

| Term | Meaning |
|---|---|
| Comparison | The result of ORC-25: the state of each citation of the code repository. |
| Plan | What the agent proposes from the comparison, which the user confirms (ORC-26). |

## Use cases

| Use case | Spec |
|---|---|
| `implement` | [implement.md](../use-cases/implement/specs/implement.md) |

## Implement the changed norms

- **ORC-25.** Before it implements anything, every use case of the module compares each citation of its own code repository with the commit of the norms repository that it reads. A script makes the comparison, not the model. Each citation gets one state (complete list):
  - `unchanged`: its norm is active, and its norm hash is the one of the citation;
  - `changed`: its norm is active, and its norm hash is another;
  - `retired`: its norm is retired;
  - `unknown`: no norm has the norm ID of the citation.
- **ORC-26.** From the comparison, the agent proposes a plan to review the changes. The plan lists every citation `changed`, `retired` or `unknown`, and, as candidates, every active norm that no citation of the code repository names. The agent proposes which candidates apply to its component; one norm may apply to several repositories of layer 3. The agent writes nothing until the user confirms the plan.
- **ORC-27.** When the comparison cannot run, the use case implements nothing, and says why.
