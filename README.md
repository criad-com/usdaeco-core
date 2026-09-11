# usdAeco — a small semantic core for the built environment on OpenUSD

## Use case

Represent the built thing with stable identity, a five-type spatial grammar,
classification, groups, ports, catalog inheritance, phase and one derived
geometry mark. Both driver-based and representation-first data use this core.
Read [the design commitments](docs/03-design-model.md), then
[the schema reference](docs/04-schema-reference.md).

| Reading order | Document |
|---|---|
| 1–2 | [Motivation](docs/01-motivation.md), [domain model](docs/02-domain-model.md) |
| 3–4 | [Design model](docs/03-design-model.md), [schema reference](docs/04-schema-reference.md) |
| 5–6 | [IFC mapping](docs/05-ifc-mapping.md), [other formats](docs/06-interfacing-other-formats.md) |
| 7–8 | [Worked examples](docs/07-worked-examples.md), [open questions](docs/08-open-questions.md) |

## The schema on an index card

| Surface | Core schemas | Contract |
|---|---|---|
| Spatial structure | `AecoSite`, `AecoFacility`, `AecoFacilityPart`, `AecoLevel`, `AecoSpace` over abstract `AecoSpatialBase` | Namespace containment; stable id and phase |
| Groups | `AecoSystem`, `AecoZone` over abstract `AecoGroupBase` | Stable id and built-in members; systems add serves |
| Connectivity | `AecoPort` | Child connection points, medium, direction and symmetric links |
| Project and elements | `AecoProjectAPI`, `AecoElementAPI` | Identity; element phase and secondary spatial anchors |
| Classification and catalog | `AecoClassificationAPI`, `AecoTypeAPI` | Kind from dictionaries; product values through inherits |
| Representation | `AecoDerivedGeometryAPI` | Source, role, approximation, stamp, source links and tolerance |

Eight concrete types, two abstract bases and five applied schemas.
No schema dependencies, dates, status, money or taxonomy of its own.

## The example

The [six stages](examples/README.md) exercise the core directly. The minimal
alias selects the zero-geometry early-design stage. The small building shows
16 elements, two levels, catalog inheritance and connected cylindrical pipework.
Its 6 × 4 m room has adjoining 0.2 m walls, a floor and roof, a door opening,
window, corridor stub and cable tray. Every gprim carries the derived mark.
Each example includes a flattened `result/example.usdc`, editable own layers
and a stock USD preview. The five stages without geometry publish labelled
hierarchy diagrams in separate derived layers; their symbols are schematic.
[Worked examples](docs/07-worked-examples.md) show a classified pipe run and
wall corner with derived geometry in separate layers.

![Small building](usdAeco/userDoc/usdAecoExample.png)

## Build and check

Use Python 3.11+ with OpenUSD 26.8+, jinja2, numpy, packaging and pytest.
Rendering additionally needs Pillow and the standard `usdrecord` utility.
Place `usdaeco-toolchain` v0.3.1 beside this repository, or set TOOLCHAIN_DIR.
Source checks need no package installation or build backend.

```sh
export PYTHON=python3
export TOOLCHAIN_DIR="../usdaeco-toolchain"
export PATH="$(dirname "$(command -v "$PYTHON")"):$PATH"
env -u PYTHONPATH ./build.sh
env -u PYTHONPATH PYTHONPATH="$PWD" "$PYTHON" check.py
env -u PYTHONPATH "$PYTHON" -m pytest -q
export PXR_PLUGINPATH_NAME="$PWD/out/plugins/usdAeco/resources:$PWD/usdAecoValidators"
env -u PYTHONPATH "$PYTHON" tools/aeco_core.py check usdAeco/examples/small_building.usda
env -u PYTHONPATH "$PYTHON" tools/render_example.py
env -u PYTHONPATH "$PYTHON" examples/small_building/run.py --publish
nix flake check --no-write-lock-file
```

`build.sh` regenerates the committed resource files beside `schema.usda`.
`check.py` builds into `out/`, runs S01–S28 including generator validation,
requires all eight Python validators to load, and exercises core contracts.
It calls `check_example()` for all six publications, including fresh-run
comparison, relocated stock USD composition and fresh plugin-free rendering.
The core resource and validator packages are loaded from this checkout.
The core-only sweep scans repository text and enforces the documentation
boundary; seeded tests verify that violations fail the check.

Keep the core resource path first when loading extensions: core registers
`aecoDerived`. A source checkout may instead register `$PWD/usdAeco`; avoid
registering two versions of the same plugin. The Python validator requires
companion modules on the interpreter's import path; the source CLI sets this
up. Schema composition itself needs no Python companion.

Flake inputs use public release refs. Local registry and `--override-input`
configuration is described in the
[build kit documentation](https://github.com/usdaeco/usdaeco-toolchain#build-and-check).
Repeat overrides for transitive inputs; keep deployment lockfiles uncommitted.
The shared harness requires a data-release pin even in minimal mode. That pin
is unused bookkeeping here: all six examples compose their own source stages,
reject external source overrides and make no claim about the pinned data.

## Family

See the [family manifest](https://github.com/usdaeco/usdaeco-scenarios/blob/main/family.json) for related libraries, integrations and examples.

## Layout

| Path | Contents |
|---|---|
| usdAeco/ | Schema, generated resources, user documentation and six example stages plus minimal alias |
| usdAecoValidators/ | Eight Python UsdValidation rules |
| tools/ | Core queries, validation, path repair and preview entry point |
| testenv/ | Registry, validation, composition, documentation and boundary checks |
| registries/, conformance/ | Classification-system names, property-set families and core validation profile |
| docs/ | Chapters 01–08 and ADRs |
| examples/ | Six minimal publication harnesses, committed results and measured manifests |
| out/ | Ignored build installation and logs |

## Status

Verified: **70 checks, 2 failed** (the S01/S25 licence-policy mismatches below);
**27 tests and 115 subtests passed**. All six publication checks pass, including
relocated composition and fresh stock USD renders.

Version 0.9.2 publishes six standalone results, improves the small building,
removes process prescriptions from the documentation and adopts MIT.
The schema's 8/2/5 class surface, property names, types and defaults are unchanged
from 0.9.1. The gate measures wall continuity and slab containment; general
geometric accuracy remains outside the core's guarantees.

Toolchain 0.3.1 still assumes Apache (S01) and flags the MIT copyright line
(S25). Both failures are reported without wrappers or exemptions; the complete
MIT licence is retained. The example hook serializes real UsdValidation finding
sites with the USD 26.8 API and runs all eight validators. Nix is **not proven**:
the single offline attempt failed to resolve a public input (HTTP 404).

## Licence

[MIT](LICENSE).
