# 1 · Motivation — the problem, stated as risks

usdAeco is one small **codeless OpenUSD schema library** for the built
environment (architecture, engineering, construction, operations). This
document explains *why it is shaped the way it is* before the later
documents say *what* it is. If you disagree with a design choice, the
argument for it almost always starts here.

## 1.1 What is actually wrong

AECO does not lack schemas; it lacks **convergent datasets** — two tools
describing one building in a way a third tool can join. The published
evidence is consistent:

- Independent audits of real-world IFC models find only a small minority
  pass full semantic checks; classic authoring-tool round trips preserved
  well under a quarter of element GUIDs; a leading authoring tool
  re-importing its own IFC export downgrades typed elements to generic
  proxies.
- buildingSMART's own retrospective on IFC counts over two hundred
  `IfcProduct` subtypes, each adding a median of *one* attribute, and
  concedes that MVD-based (subset-based) interoperability collapsed.
- IFC's successor work (ifcX) is converging on a USD-like shape — path
  addressed nodes, layered overrides, components, external dictionaries —
  which both validates the approach taken here and sets an alignment
  target.

The failure mode is structural, not a matter of effort: a large, closed,
release-gated taxonomy plus an under-constrained encoding (many legal ways
to say one fact) guarantees divergence.

## 1.2 The method

The design separates domain, design and code models; the numbering in
every later document follows these three views:

| Model | Question | Labels |
|---|---|---|
| **Domain model** ([02](02-domain-model.md)) | What is *true* about the built thing, in no USD vocabulary at all? | **D1…D12** |
| **Design model** ([03](03-design-model.md)) | Which commitments map those truths onto USD — with the refused alternatives? | promises **B1…B9**, extension rules **E1…E15** |
| **Code model** (the schema, examples, `check.py`) | What runs, and which claim does each test verify? | — |

The payoff is precision in argument: every mechanism appears three times —
as a truth, as a commitment, as a running artifact — so a disagreement can
name which model it targets. "Spaces can sit directly on sites" is a
domain claim. "Facility kind belongs to classification, not subtypes" is a
design claim. "The fallback override composes" is a code claim (and
`check.py` verifies it).

## 1.3 The core exists only to mitigate named risks

Per the risk-driven method, everything in the core is there to mitigate a
named risk; everything else — including things that feel obligatory, like
a wall entity, a document register or a coarse category token — is
deliberately absent.

| # | Risk | Mitigation |
|---|---|---|
| **R1** | **Divergence** — two tools encode one building differently (IFC's core failure: many encodings of one fact) | One-obvious-way rules closed off *in the schema*: containment is the namespace; element-ness is one applied API; kind is one mechanism (classification); grouping is one base with a built-in collection; ports are prims; each spatial concept has exactly one encoding — spatial *type* as a typed schema, spatial *kind* as classification |
| **R2** | **Taxonomy capture** — the type system accretes element and space kinds until releases gate the industry (IFC's ~880 entities; closed authoring-tool category enums) | No element types and **no taxonomy of its own at all**: kind is late-bound to external dictionaries (IFC entities, Uniclass, bSDD, …) through one applied schema. Spatial and group kinds likewise |
| **R3** | **Parallel-structure drift** — each library invents its own containment, grouping or connectivity | Exactly one of each mechanism, and a contract (E1–E15) forbidding alternatives; enforced mechanically where USD allows (`apiSchemaCanOnlyApplyTo`, built-in API schemas), by validators elsewhere |
| **R4** | **Adoption friction** — compiled plugins, vendor toolchains | Codeless-only data contract on stock `usd-core`; graceful degradation to vanilla USD via `fallbackPrimTypes` (measured: identical transforms with no schema loaded) |
| **R5** | **Version coupling** — vocabulary changes tied to downstream and core schema releases | Separate versioned artifacts: registry updates do not require downstream or core schema changes |
| **R6** | **Restructure fragility** — containment-as-namespace couples location to path, so re-slicing the tree breaks path-anchored overlays in federated layers | The grammar legalizes the shapes whose absence forced most historical restructures; identity on every container, group and element makes re-anchoring mechanical (`repath`: longest-prefix remap by `aeco:id`); repairs compose as opinions in a stronger layer |
| **R7** | **Core creep** — every adjacent concern (documents, programme, cost, issues, product data) is "obviously" needed and lands in the core, until the core is the whole industry and nobody can review it | A referent test for admission (ADR-0001): the core types only things the built world *is made of* and *addressed by*; everything *said about* it is a downstream tier that applies to core prims and never subclasses them |

## 1.4 Non-goals, routed to their owners

The core carries **semantics of the built thing only**. It never defines
geometry, materials, physics, lighting or rendering (rule E10); it
references the existing USD domains for those. Explicitly out of scope,
with the body or tier that owns them:

- **Geometry kind** (meshes, BREP, parametric solids) → the OpenUSD
  geometry work and its BREP proposals.
- **Geospatial CRS** → the OpenUSD geospatial efforts.
- **Units beyond stage metrics** → the core USD specification work.
- **What a wall, a pipe, a tray *knows*** (width, material, nominal
  diameter, fill) → element-kind libraries applying to elements
  (see the extension contract in [03](03-design-model.md)).
- **The project record** — documents, parties, issues, changes,
  programme, cost, responsibility, status of any kind → the record tier
  (see the extension contract in [03](03-design-model.md)).
- **Datums** (grids, alignments, benchmarks) → a datum library, a
  candidate for the core once evidence lands.
- **Scheduling engines, price books, workflow engines, signatures/PKI**:
  never re-derived anywhere in the family.

## 1.5 One rule that keeps all of this small

> If two tools must agree on what the data *says*, it is schema (codeless).
> If it computes, checks or conveniences, it is a library (codeful,
> optional).

The schema carries types, fallbacks, vocabularies, application
restrictions and documentation, loadable by any modern USD with no
compiled code. The optional companion (`tools/usdaeco_tools`) carries
validators (registered with USD's own `UsdValidation` framework), graph
services, the two registries and the restructure repair. This is the
shape UsdPhysics already established — data schema, external behaviour —
applied to AECO.
