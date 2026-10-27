# development-methodology

The module `development-methodology` of Indra Software Factory: the
development methodology of every project, carried to every repository of the
project, of the five layers
([APP-6](specs/layers.md#where-each-module-is-installed)).
It is specified in [specs/module.md](specs/module.md).

## The methodology

- [specs/layers.md](specs/layers.md): the five layers, their rules and their terms, and where each module is installed.
- [specs/flow.md](specs/flow.md): the flow across the layers, a run, its steps and their hand-offs.

## Use cases

None: the module has no skill. Its hook, at every start of a session, adds to
the session an index of the methodology, with the paths of the specs above
([MTH-4 to MTH-6](specs/module.md#the-index-of-every-session)). The hook is
[hooks/hooks.json](hooks/hooks.json); its script is
[scripts/index.py](scripts/index.py), tested by
[tests/test_index.py](tests/test_index.py).
