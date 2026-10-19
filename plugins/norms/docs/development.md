# Developing the generator

Run from `plugins/norms`.

## Tests

```sh
uv run pytest -q
```

The examples E1–E89 of the specs are test cases. `tests/spec_examples.py`
writes them under `tests/fixtures/`, and a test fails when a fixture and
its spec differ. After changing a spec, write them again:

```sh
uv run python tests/spec_examples.py
```

## Traceability

The code and the tests cite the requirements (`R<n>`), the decisions of
the user (`U<n>`) and the examples (`E<n>`) of the specs in one format:

- The docstring of a module, class or function that implements or checks
  a rule ends with one line, `Spec: R35, R39, U4 (E28, E40)`: requirements
  and decisions first, R before U, each sorted by number, then the
  examples in parentheses; ids separated by `, `, never a range.
  `Spec: (E28)` cites examples only.
- A comment on a branch that applies one specific case starts with its
  ids: `# R39: <short reason> (E41)`.
- An implementation note of
  [generator-decisions.md](generator-decisions.md) is cited as
  `Note: D2`.

No other id may appear in a docstring or a comment, and every test cites
what it checks. [traceability.md](traceability.md) lists, for
each requirement and decision, the code and the tests that cite it and
its examples. After changing the code, the tests or the specs, write it
again:

```sh
uv run python tests/traceability.py
```

`tests/test_traceability.py` fails when it is out of date, when a
citation names an id no spec defines, or when a citation has another
format.
