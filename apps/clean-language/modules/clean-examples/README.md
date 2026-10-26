# clean-examples

Module `clean-examples` of the app Clean Language: the rules of how a Clean
example of the specs is written ([specs/module.md](specs/module.md)), the
audit of the examples of a layer, `/clean-examples:audit`
([use-cases/audit/specs/audit.md](use-cases/audit/specs/audit.md)), and the
hook that refuses a malformed example as it is written.

Enabled in the repositories of layers 0 and 1 of the Clean Language project
([CLN-1](../../specs/app.md#rules)).

Tests:

```sh
python3 -m unittest discover -s apps/clean-language/modules/clean-examples/tests
```
