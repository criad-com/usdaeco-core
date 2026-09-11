# Core examples

Each of the six [authored stages](../usdAeco/examples/) has a minimal publication
harness and a committed result. Open any `result/example.usdc` with stock USD;
no family plugin, external asset or sibling checkout is needed.

| Example | Core concepts | Published view |
|---|---|---|
| [Small building](small_building/README.md) | 16 classified elements, two levels, catalog inheritance, six ports | [Dimensioned building](small_building/result/vanilla.png) |
| [Early design](early_design/README.md) | Spaces, groups and service scope before geometry | [Hierarchy schematic](early_design/result/vanilla.png) |
| [Hard cases](hard_cases/README.md) | Recursive containment, mezzanines and nested elements | [Hierarchy schematic](hard_cases/result/vanilla.png) |
| [Renovation](renovation/README.md) | Existing and proposed spatial fabric | [Hierarchy schematic](renovation/result/vanilla.png) |
| [Road](road/README.md) | A non-building facility using the same grammar | [Hierarchy schematic](road/result/vanilla.png) |
| [Service campus](service_campus/README.md) | Shared services and overlapping spatial groups | [Hierarchy schematic](service_campus/result/vanilla.png) |

`minimal.usda` aliases `early_design.usda`. The five non-building source stages
remain without geometry. Their published views add labelled symbols in a
separate derived layer; symbol dimensions and positions are diagram layout,
not physical building geometry. The source's transforms and identity remain
unchanged. The hard-cases stage deliberately retains one dangling-member warning.

Each example directory includes `run.py`, `expected/findings.json`, `inputs/`,
`renders/`, `manifest.json` and `result/`. The result contains a self-contained
flattened crate, the original authored source and own presentation layers, a
README and an independently rendered `vanilla.png`. Hashes, sizes, source mode,
pins and prim counts are recorded in the manifest.

Regenerate one example with `env -u PYTHONPATH python examples/small_building/run.py --publish`
in the environment from the [root README](../README.md). Use the other directory
names to regenerate their results. Ordinary runs write only ignored `out/`.
`check.py` compares fresh results with all six committed outputs, relocates each
crate and renders it in a fresh process with family plugins removed.

The [worked examples](../docs/07-worked-examples.md) add two complete compositions
with separate semantic and derived layers.
