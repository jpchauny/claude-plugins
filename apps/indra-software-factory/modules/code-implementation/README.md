# code-implementation

Layer 4, in each repository of layer 4: the implementation method. Code and unit
tests are built from the norms and the derived norms of layer 2 alone, within the acceptance units of layer 3, and
cite the units they implement, each with its unit hash, and the derived norms they are built from, each with its
derived norm fingerprint, never a norm ID
([ACU-56](../acceptance-management/specs/module.md#hashes-and-citations),
[CIM-11](specs/module.md#the-derived-norms-of-the-code)); the acceptance tests of layer 3 are run, never changed
([LAY-4](../development-methodology/specs/layers.md#rules));
an inconsistency goes back to layer 1 first, and a derived norm that does not follow from right norms to the
marketplace repository of its derived-norms generator
([LAY-5](../development-methodology/specs/layers.md#rules)).

## Tools

The hook [hooks/hooks.json](hooks/hooks.json), on every call of `Edit`, `Write`,
`NotebookEdit` or `Bash`, refuses the calls that write the acceptance repository of layer 3,
whose path it reads from `project.json`; reading it is allowed
([CIM-1 and CIM-3 to CIM-8](specs/module.md#the-hook-of-the-session)). Its script is
[scripts/guard_acceptance.py](scripts/guard_acceptance.py), tested by
[tests/test_guard_acceptance.py](tests/test_guard_acceptance.py).

Planned:

- `/code-implementation:implement`, specified in
  [implement.md](use-cases/implement/specs/implement.md): it implements only
  acceptance units of layer 3, one at a time, in the order of the plan of
  implementation, and codes nothing that is not in layer 2 and grouped by
  that unit.
- Traceability: the scripts that compare each citation of a unit with its unit hash in the acceptance
  repository, and each derived norm citation with its derived norm fingerprint in the lists of derived
  norms of the norms repository ([ORC-25, CIM-2, CIM-9 and CIM-10](specs/module.md#implement-the-changed-norms)),
  find the derived norms of the task ([CIM-11](specs/module.md#the-derived-norms-of-the-code)), and check each
  citation that implement writes ([IMP-8](use-cases/implement/specs/implement.md#implement-a-task)).
- Running the acceptance tests as feedback, and recording each AI decision as a decision block
  ([acceptance-management](../acceptance-management/specs/module.md)).
- Reporting an inconsistency as an issue in the repository of layer 1, and a derived norm that does not follow
  from right norms as an issue in the marketplace repository of its derived-norms generator, found by a script as
  [ACU-79](../acceptance-management/use-cases/define/specs/define.md#define-the-acceptance-areas-and-acceptance-units)
  says ([IMP-10](use-cases/implement/specs/implement.md#implement-a-task)).
- Keeping the session from writing layer 2.
