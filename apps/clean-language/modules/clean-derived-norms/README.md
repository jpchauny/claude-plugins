# clean-derived-norms

Module `clean-derived-norms` of the app Clean Language: the derived norms of
Clean in layer 2, one use case per type ([specs/module.md](specs/module.md)),
each a derived-norms generator of the interface of `norms-management`
(NRM-1 to NRM-11):

- `/clean-derived-norms:derive-grammar`: the Lark grammar of Clean,
  `specs-derived/grammar/` ([spec](use-cases/derive-grammar/specs/derive-grammar.md)).

Enabled in the repository of layer 2 of the Clean Language project
([CLN-1](../../specs/app.md#rules)), and listed in its `project.json` under
`derived_norms`.

Tests:

```sh
uv run --with pytest --with "lark[interegular]" python3 -I -B -m pytest -q -p no:cacheprovider apps/clean-language/modules/clean-derived-norms/tests
```
