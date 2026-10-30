# clean-derived-norms

Module `clean-derived-norms` of the app Clean Language: the derived norms of
Clean in layer 2, one use case per type ([specs/module.md](specs/module.md)),
each a derived-norms generator of the interface of `norms-management`
(NRM-1 to NRM-15):

- `/clean-derived-norms:derive-grammar`: the Lark grammar of Clean,
  `specs-derived/grammar/` ([spec](use-cases/derive-grammar/specs/derive-grammar.md)).
- `/clean-derived-norms:derive-semantics`: the semantics of Clean in Lean 4
  (abstract syntax, typing, evaluation), a Lake project in
  `specs-derived/semantics/`, checked against every fragment and its expected
  output ([spec](use-cases/derive-semantics/specs/derive-semantics.md)). It
  runs after `derive-grammar`, and its check needs `lake`
  (`leanprover/lean4:v4.34.1`, through elan).

Each one also writes, in its folder, `derived-norms.jsonl`: the list of its
derived norms (a statement of the grammar, a declaration of the Lean code),
each with its own derived norm ID (`grammar:<n>`, `semantics:<n>`) and its
derived norm fingerprint, which layers 3 and 4 cite (NRM-12 to NRM-15, CDN-8).
The derived norms new, changed and gone are not compared here: the step of
layer 2 compares them for its report (NRM-11).

Enabled in the repository of layer 2 of the Clean Language project
([CLN-1](../../specs/app.md#rules)), and listed in its `project.json` under
`derived_norms`.

Tests (the tests that build Lean are skipped when `lake` is absent):

```sh
uv run --with pytest --with "lark[interegular]" python3 -I -B -m pytest -q -p no:cacheprovider apps/clean-language/modules/clean-derived-norms/tests
```
