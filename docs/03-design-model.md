# 3 · Design model — the commitments

The design model maps the truths of [02](02-domain-model.md) onto USD.
It has a *boundary* — the promises a conformant dataset makes and the
contract downstream authors sign (§3.1–3.2) — and *internals* — the
mechanisms chosen, each with the alternatives considered and refused
(§3.3 onward). This is where a USD engineer or a schema author should aim
their disagreement.

## 3.1 Boundary: promises to consumers

A conformant dataset guarantees, to a tool that has loaded **only the core
library**:

| # | Promise | What it enables |
|---|---|---|
| **B1** | A five-type spatial grammar exists (`AecoSite` / `AecoFacility` / `AecoFacilityPart` / `AecoLevel` / `AecoSpace`, recursion legal); containment is the namespace; nearest-spatial-ancestor is the container relation | Floor plans, level filters, per-container scoping — with zero downstream knowledge |
| **B2** | Every element carries `AecoElementAPI`: a stable `aeco:id` and an asset-clock `aeco:phase` | Census, diffing, issue anchoring, FM inventories — joined by id across every route |
| **B3** | **Kind is classification, everywhere.** What an element, a container, a group or a catalog type *is* comes only from `AecoClassificationAPI:<system>` instances with codes and URIs into external dictionaries; the core has no kind vocabulary of its own | "All walls" is one query in any dictionary the data uses; requirement checking against IFC entities or Uniclass/bSDD without vendor mappings; nothing in the core to re-map when a dictionary revises |
| **B4** | All grouping is an `AecoGroupBase` prim with a built-in `members` collection — two types, `AecoSystem` (adds `aeco:serves`) and `AecoZone`; all connectivity is `AecoPort` prims | One system browser, one network tracer, one zone report for every discipline |
| **B5** | Type/occurrence rides `inherits`: resolved values are already right; occurrence overrides type by composition strength | `attr.Get()` with no relationship-chasing |
| **B6** | Standardized downstream data sits in documented `aeco:<lib>:` namespaces; ad-hoc data only under `aeco:props:` | Safe generic display of unknown libraries; governed vs project data mechanically distinguishable |
| **B7** | The stage passes the conformance suite **and remains an ordinary USD stage** — `fallbackPrimTypes` written, so schema-unaware tools compose identical transforms | Trust without bilateral testing; renderers install nothing |
| **B8** | **The core is closed and small**: a consumer that knows 5 spatial types, 2 group types, 1 port type and 5 applied schemas can traverse the *entire* built thing and will never meet another core structure; everything downstream applies to these prims and never subclasses them | An afternoon-reviewable core; tier-blind queries; the core stage survives the removal of any downstream layer bit-identically |
| **B9** | **Representations declare their source.** Every derived gprim carries `AecoDerivedGeometryAPI`: referent identity, role, approximation and stamp. Drivers are optional in core; path traversal is outside the core (ADR-0008). | Both driver-based and representation-first datasets remain readable with the core alone |

## 3.2 Boundary: the extension contract (E-rules)

A downstream library — an element-kind library (walls, pipes), the record
tier (documents, programme, cost), a sector, an organization — is
conformant iff:

- **E1 · Extend vocabulary, never structure.** Libraries may add applied
  APIs freely and typed prims only for genuinely new *referents* with no
  core counterpart (ADR-0001; justify in review). Libraries MUST NOT
  subclass `AecoSpatialBase` or `AecoGroupBase` — both type sets are
  core-governed; spatial and group *kinds* are always classification. No
  new containment, grouping, connectivity or identity mechanisms, ever.
- **E2 · Decorate, never capture.** Library semantics attach via applied
  APIs in the library's own namespace. Never retype or reparent another
  discipline's prims; never author in another library's namespace. Facts
  about *your* element that involve *their* container (a riser serving
  Level 2) live on **your** prim (`aeco:referencedContainers`).
- **E3 · No dependencies between kind libraries.** Shared *section*
  libraries form an explicit lower sub-tier: build-up for layered
  elements, flow-segment for profile runs. Kind libraries may sublayer
  these section libraries (core ← section ← kind), as a kind library sublayers a shared section contract; a kind library must not depend on another kind library.
  Data between kinds flows through core concepts (ids, classifications,
  collections, ports, containers). Cross-kind *rules* (a firestop matching
  a wall's rating) live in validation packages, keeping the schema graph
  acyclic (E12 gives it tiers).
- **E4 · Kind via classification only.** Never a typed prim, a parallel
  enum, or a census token per product kind — coarse *or* fine. A library
  that needs "all walls" tests its applied API or reads a classification code; it never mints a vocabulary the next tool cannot
  join. If the ecosystem ever needs a schema-neutral census vocabulary,
  it is *another classification system* (an instance name in the
  registry), never a core property (ADR-0005).
- **E5 · Groups through the core.** Library system/zone kinds are applied
  refinement APIs on `AecoSystem`/`AecoZone` with `apiSchemaCanOnlyApplyTo`
  declared. Never a subclass, never a private membership mechanism.
- **E6 · Connectivity through ports.** Refine `AecoPort` with applied
  APIs; never invent alternative connection entities.
- **E7 · Properties, two tiers, no third place.** Standardized properties
  are schema attributes with docs, SI-fixed units, fallbacks and
  `allowedTokens`. Ad-hoc data goes under `aeco:props:<Set>:<name>`.
- **E8 · One identity.** `aeco:id` everywhere; no alternative identity
  attributes; per-occurrence ids on occurrences, never on type prims.
- **E9 · Ship conformant.** Codeless build; declared core-version
  conformance; registered tokens; application restrictions authored; the
  shared validation suite green on a submitted example.
- **E10 · Semantics only.** Geometry, materials, physics, lighting and
  rendering belong to the existing USD domains; AECO schemas may only
  reference them.
- **E11 · One spatial structure; everything else is collections and
  relationships.** No library may introduce a containment hierarchy for
  built things. Work breakdowns, cost breakdowns, package structures are
  trees *of record prims*; their leaves bind to the built thing via
  `members` collections or id-anchored relationships. Muting any
  downstream layer never moves geometry (`check.py` drills it).
- **E13 · Drivers and derived.** In every library namespace a property is
  a driver unless its schema definition carries `aecoDerived = true`, the
  boolean property metadatum the core plugin registers. Only drivers may
  be authored by an editing party; derived values are written by hosts
  and derivations; a validator flags a derived opinion in an intent layer.
  The derived declaration belongs on properties in schema files, never
  in stage data.
- **E14 · Geometry flows out.** A library never presents a
  mesh to a host as input; every host-facing representation is a driver
  set. Derived gprims carry `AecoDerivedGeometryAPI` (source, role,
  approximation, stamp, representation sources and tolerance) and are
  children of their referent. Hosts and stage-side derivations write
  geometry; they never consume it as editing intent.
- **E15 · Exactness is declared.** A Mesh is never `approx = exact`:
  `DerivedExactOnMesh` is an error. Exact bodies use `BrepArray` or analytic
  UsdGeom primitives (`Cube`, `Cylinder`, `Sphere`, `Cone`, `Capsule`).
  Exact straight guides and extracted wireframes retain their guide
  roles; a segmented arc declares `arcSegmented`. Exact geometry declares
  a positive finite `aeco:derived:tolerance` in metres; missing/unknown
  tolerance raises `ExactWithoutTolerance` (warn). A Mesh twin links its
  exact source through `aeco:derived:from`. No claim of exactness can be
  inferred from a body's name or tessellation density (ADR-0009).
- **E12 · Clock discipline, and the library DAG.** Asset time is
  `aeco:phase` (core); information time is layers and layer metadata
  (USD); work time — dates — is ISO-8601 attributes on *record* prims in
  the record tier. The core carries no date, and no downstream library
  may encode a revision as an attribute, a work date as layer structure,
  or either as `UsdTimeCode` samples. Dependencies form a tiered DAG:
  core ← shared section ← element-kind ← record ← sector ← organization
  ← project profile. Section is the lower sub-tier for shared section
  contracts; kind libraries may depend on it and directly on core, never
  on other kind libraries (E3). Edges point strictly toward the more
  generic tier, every tier specializes by addition only, and core queries
  are tier-blind (`IsA`
  and core-property reads return identical results whatever upper tiers
  are installed).

The contract is enforceable at three moments: schema review (E1/E3/E9/E10
are visible in the library), authoring time (`CanApplyAPI` refusals and
vocabularies — `check.py` exercises them), and validation time (the
suite). *The glue is the contract*: the core's small size is what makes
the contract reviewable in an afternoon.

## 3.3 Designation: every truth, one mechanism, and the refused alternative

| Truth | Committed mechanism | Refused alternative (and why) |
|---|---|---|
| D1 project | `AecoProjectAPI` on the root model prim (name, id); units/axis = UsdGeom stage metrics | Typed project root (competes with pipeline root conventions); stage-wide conventions of downstream tiers (calendar epoch, currency) in the core (each tier declares its own) |
| D2 spatial tree | **Five typed spatial types** over abstract `AecoSpatialBase` (Xformable, carries `aeco:id` + `aeco:phase`); containment = namespace; a four-rule grammar with recursion, validator-enforced at ERROR tier; kind = classification (§3.4) | Fixed ladder (the impossibility list); one generic prim + role tokens (advisory in USD, loses per-type `CanApplyAPI` targeting); typed kind subtypes à la `IfcRoadPart` (the median-one-attribute disease) |
| D3 element | `AecoElementAPI` applied to any Imageable; containment = namespace; spans = `aeco:referencedContainers` on the element; a container or port wearing the API is a validator error | Typed element hierarchy (IFC's fate); referenced-element collections on *containers* (inverts federation ownership, E2) |
| D4 kind | Multi-apply `AecoClassificationAPI:<system>` → code/name/URI, on elements AND spatial prims AND groups AND catalog types; instance names from a registry; `ifc` recommended as the default system; health metric = elements with no code, or coded as a proxy | A core census token (a dual encoding of the IFC class, a home-grown taxonomy, a parallel vocabulary maintenance burden on the core — ADR-0005); baking one national system in; UsdSemantics labels as primary (no code/URI/version semantics — kept as an optional mirror) |
| D5 type/occurrence | Class prims + `AecoTypeAPI` + `inherits`; override = composition strength; catalog = class prims | Explicit type relationship (two sources of truth); denormalized copies |
| D6 groups | `AecoGroupBase`° (identity + built-in `members`) → `AecoSystem` (+ `aeco:serves`) and `AecoZone`; kind = classification; refinement = applied APIs (§3.5) | Zones as spatial subtrees (overlap inexpressible in a namespace); one merged group type (makes a fire compartment a *system*); a generic escape group (plain `CollectionAPI` already is one); the register row on the group (a statement about the group, not the group — ADR-0006) |
| D7 connectivity | `AecoPort` typed child prims: id, **medium**, flow direction, symmetric `aeco:connectedPorts`; `purpose = guide` by fallback; `undefined` is a wildcard for both medium and flow | Ports as multi-apply properties (need transforms and rel targets); connection entities; shading-style attribute connections (dataflow ≠ physical topology) |
| D8 phase | `aeco:phase` token on elements *and* spatial prims | Per-phase layers only (still freely available on top) |
| D9 federation | Plain USD: one layer per discipline over a shared spatial structure; provenance = the opinion stack | Anything bespoke |
| D10 identity everywhere | `aeco:id` on `AecoSpatialBase`, `AecoGroupBase`, `AecoPort` and `AecoElementAPI` — one uniqueness space | Element-only identity (leaves spaces/systems unaddressable) |
| D11 two-tier properties | Downstream schema attributes vs quarantined `aeco:props:` (E7); set names enumerable through a registry | Everything ad-hoc (Pset free-for-all); everything standardized (IFC's enormous, still insufficient catalog) |
| D12 two-tier rules | Core validators (warnings) + validation **profiles** per sector/exchange that harden them | Schema subsets per use case (the MVD failure); rules as schema structure (inexpressible) |

## 3.4 The spatial structure — the method, worked end-to-end

The design iterated on this decision more than any other; the iteration
is the best short demonstration of the method.

**The truth.** D2 says the containment *pattern* is universal while the
*kind* vocabulary churns by sector. Any design must be exactly as rigid as
the pattern and exactly as open as the vocabulary. And the everyday world
is full of shapes a fixed ladder cannot say: campuses of parcels, podium
developments with towers sharing a basement, hospital wings, mezzanines,
subdivided open plans, atria belonging to no storey, plazas belonging to
no building, and every facility that is not a building.

**The candidate commitments.**

| Option | Shape | Verdict |
|---|---|---|
| (a) Fixed ladder | `Site→Building→Level→Space`, order enforced | **Wrong domain model**: the impossibility list above; kind hardcoded; IFC has retreated from exactly this in four documented steps |
| (b) One type + role tokens | Single region prim, a role attribute with reserved + free values | **Right truth, costly design**: tokens are advisory in USD; per-type `CanApplyAPI` targeting lost; the 90% case pays for the 10% |
| (c) Types serving roles | Typed structure with role *fallbacks* + a generic escape prim | **Sound but heavier than its problem**: once parts are concrete and recursive, no generic remainder exists, and the role machinery polices a distinction that no longer occurs |
| (d) **A grammar of five types** | `Site`, `Facility`, `FacilityPart`, `Level` (: part), `Space`; recursion at every type; kind = classification; no roles, no building type | **Aligned with all three models, and smaller than every predecessor** — type is structure (typed, closed, five), kind is taxonomy (data, open), grammar is validation |

**The commitment (d), precisely.** Abstract `AecoSpatialBase` (Xformable)
carries identity and phase. Five concrete types: `AecoSite` (nests),
`AecoFacility` (a building, a road, a plant — *kind by classification*, per
IFC 4.3's own concession that the facility-kind list is open-ended),
`AecoFacilityPart` (wing, tower, podium, road section — concrete and
recursive), `AecoLevel : AecoFacilityPart` (the one universal part, typed
for its one universal property, the datum elevation — and since levels ARE
parts, level > level covers mezzanines), and `AecoSpace` (room, hall, yard,
atrium, plaza — nests; sits under site, facility, part or space). The
grammar is four rules with the recursions built in:

```
site     ⊃ { site, facility, space }
facility ⊃ { part, space }
part     ⊃ { part, space }          (level is a part)
space    ⊃ { space }
```

enforced at ERROR tier, with one deliberate refusal: facility ⊃ facility
is an error whose message says "use AecoFacilityPart". Organizational
`Scope`s interleave invisibly (nearest-spatial-ancestor is the container
relation); unanchored parts/spaces warn rather than error; a spatial prim
inside an element's subtree warns; a spatial prim that is also an element
errors; declarative elevation drifting from authored placement warns
(governing the redundancy IFC left ungoverned until it had to deprecate
the storey `Elevation` attribute).

**The element boundary.** An element is where the containment grammar
*stops*. Below an element, namespace is assembly structure, not spatial
containment — a door nested inside a curtain-wall element is legal and
ordinary; containment queries see *through* element subtrees.

**What the deletion buys.** Removing a Building type, the generic escape
type and the entire role apparatus removes the *last dual encodings* and
the validator machinery that policed them. One rule survives: **type =
structure, kind = classification.** The hard cases stop being hard: the
same five types express a campus of parcels, a podium with two towers, a
mezzanine, an atrium, a plaza and a road in sections, in one stage,
validating clean (`usdAeco/examples/hard_cases.usda`).

**The honest cost, priced (R6).** Containment-as-namespace couples
location to path, so restructuring breaks path-anchored overlays in
federated layers. Three mitigations: most historical "restructures" were
workarounds for shapes the grammar now legalizes; identity on every
container, group and element makes repair mechanical (`repath` re-anchors
dangling targets by `aeco:id` with longest-prefix remap so ports and nested
prims under a moved element follow it); repairs compose as opinions in a
stronger layer without touching the stale one. `check.py` drills it.

## 3.5 Groups — one base, two types, and what a group is *not*

**The base.** `AecoGroupBase`° (inherits `Typed`) carries `aeco:id` and a
built-in `CollectionAPI:members` (expansionRule `explicitOnly` by fallback).
A group *is* its members plus an identity — the counterpart of `IfcGroup`.

**The types.** `AecoSystem` (adds `rel aeco:serves` — the spatial prims or
zones a service reaches, valid before any pipe is drawn) and `AecoZone`
(nothing beyond the base). Both `fallbackTypes = ["Scope"]`. Two types,
not one, because the domain language is different and downstream APIs
must target them separately (`apiSchemaCanOnlyApplyTo = ["AecoSystem"]`
on a circuit API; `["AecoZone"]` on a compartment API). Kind is
classification, exactly as for everything else: `IfcDistributionSystem.
CHILLEDWATER`, `IfcSpatialZone.FIRESAFETY`.

**What a group is not.** A group carries **no register row** — no
title-as-data, no status, no owning party, no discipline token. Those are
statements *about* a group (a system appears in an O&M register with a
status; a compartment appears in a fire strategy with an author), and the
family's whole shape depends on statements sitting *on top of* referents.
The core's `displayName` metadata covers the human label. Nor does the core have a generic third group
type: a selection set is a plain `CollectionAPI` instance on any prim —
USD's own grouping — and needs no AECO type.

**The element trait, by contrast.** `AecoElementAPI` (id · phase ·
referencedContainers) is exactly what a *referent* may carry: identity,
the asset clock, and its own spatial facts. No title, no status, no party,
no about, no kind token — the asymmetry between referents and statements
is enforced by what the API omits.

**The whole core on an index card:**

| | Spatial types | Group types | Elements |
|---|---|---|---|
| Structure (typed, closed) | Site · Facility · FacilityPart · Level · Space | System · Zone | any Imageable + `AecoElementAPI` |
| Meaning (data, open) | classification | classification | classification |
| Base | `AecoSpatialBase`°: identity + phase | `AecoGroupBase`°: identity + members | — |
| Reference to the world | containment = namespace | `members`; systems `serves` | namespace + `referencedContainers` |
| Dates / status | none — referents have no clock but phase | none | none |
| Restructure repair | `repath` by id | same machinery | same |

## 3.6 Time — what the core keeps, what it delegates

The domain has three clocks (a wall can be *existing*, scheduled for
*demolition in phase 3*, on a drawing at *revision C02*), and conflating
them is the industry's standing confusion. The core keeps exactly the
clocks that belong to referents and to USD itself:

| Clock | Mechanism | Where |
|---|---|---|
| **Asset time** — what exists when | `aeco:phase` token on elements and spatial prims | core |
| **Information time** — what was said when | layers and layer metadata (stamped issue layers, `customLayerData`); supersession and "in force at" are composition | USD itself; conventions in the record tier |
| **Work time** — when work happens | ISO-8601 attributes on *record* prims (activities, milestones) | record tier |

The core therefore carries **no date at all**, and E12 forbids every
downstream library from smuggling one in through the wrong mechanism:
revisions are never attributes, work dates are never layer structure,
neither is ever a `UsdTimeCode` sample (timeCode is a sampling axis for
*derived* views such as 4D playback, which the record tier may generate
and never treats as truth). Design options are a `VariantSet` on the
spatial referent — a representation choice on one state, never a clock
(ADR-0003; `usdAeco/examples/hard_cases.usda`, TowerB).

## 3.7 One spatial structure, three organizing axes

USD natively provides **three** independent ways to organize the same
data, and the one-spatial-structure rule constrains exactly one of them:

| Axis | What it organizes | Who owns it | Multiplicity |
|---|---|---|---|
| **Namespace** (the spatial structure) | *Location*: where things are; transform inheritance; addressing; streaming/payload boundaries | No discipline (neutral) | **One** — this is the whole of E11 |
| **Layers** | *Delivery and ownership*: who said it, in what package, at what issue | Each author/party | **Free** |
| **Collections / relationships** | *Groups and statements*: systems, zones, and everything the record tier says | Each group's author | **Free** |

The deep reason the spatial tree is the one namespace is the medium's
grain: **in USD, the namespace is the transform tree, and transform
inheritance is a geometric fact about physical support.** Move a level and
its rooms and walls move with it. No other candidate structure has this
property: a circuit does not move its devices; a work package does not
move its scope. Putting any other breakdown in the namespace means fighting
the medium; putting this one there means the medium does half the work.

The engineer who "wants the model organized by system" wants the layer
axis or the collection axis — both of which they already fully own — not a
second namespace. A rule-shaped corollary: **no consumer semantics may
depend on layer names or nesting** (stamps are data in `customLayerData`;
layer structure is convenience).

Stress cases graded against this (early design with no geometry;
system-primary mental models; linear infrastructure; grids; renovation;
design options; sub-element structure; modular construction; movable FM
assets; network operators; analytical models; portfolio scale;
cross-ownership networks; scopes with no location) all either **hold** or
reduce to two **additive** gaps — datums and spatial phase — with zero
structural ones. Spatial phase is in the core; datums are outside it.

## 3.8 The codeless/codeful division and the three views

**Module view.** `usdAeco` is a resource plugin: schema definitions,
fallbacks and property metadata. `usdAecoValidators` is a Python plugin
with eight registered checks. The optional companion provides queries,
classification health metrics and identity-based target repair.

**Runtime view.** A core stage composes spatial structure and element
semantics with separate derived representation layers. Additional opinions
may decorate referents but cannot change the core containment, grouping or
identity mechanisms. Muting those opinions leaves the core traversal and
world transforms intact (B8, E11).

**Versioned artifacts** — each changes independently:

| Layer | Contents | Versioned artifact |
|---|---|---|
| The closed core | 5 spatial + 2 group types, 2 bases, AecoPort, 5 applied schemas | Core schema |
| Applied schemas | Element-kind libraries; the record tier | Downstream library |
| Vocabularies | Classification system names; props-set families | Registry data; unknown values warn |
| Profiles | Numbering rules; sector and exchange requirements | Profile data |
| Projections | Register, takeoff, handover | Companion tools |

## 3.9 Strengthenings carried from the stress test

- **The asset clock on the spatial structure**: `aeco:phase` on
  `AecoSpatialBase`, so a renovation models existing fabric and the
  proposed remodel in one structure (`usdAeco/examples/renovation.usda`).
- **Design options as variants**: a `VariantSet` on the spatial referent,
  with groups targeting variant-specific prims — never sibling twin
  subtrees (`usdAeco/examples/hard_cases.usda`, TowerB).
- **Designed-vs-current location**: the spatial structure is where a thing
  *belongs* (as designed / as built); logistics and live position are
  record or telemetry data. Re-parenting is never movement.
- **Zero-geometry conformance**: an early-design stage with spaces, a
  system and a zone and no meshes is a complete, conformant dataset
  (`usdAeco/examples/early_design.usda`) — the spatial structure exists *before*
  geometry and receives it.
- **Referent kinds are disjoint**: a container or a port is never also an
  element (validator error), closing the one hole `apiSchemaCanOnlyApplyTo
  = ["Imageable"]` cannot close on its own.

## 3.10 What `check.py` verifies

| Check | Claim |
|---|---|
| the core resolves; the plugin is resource-only; nothing from the record tier is present | E9 codeless; B8 closed and small |
| `CanApplyAPI` refusals; built-in `members` on both group types; groups carry no row | E1/E5 mechanical contract; ADR-0006 |
| every example: 0 validation errors, `fallbackPrimTypes` complete | the grammar, ports, identity, group rules; B7 |
| seeded defects caught | facility-in-facility, space-in-wall, level-as-element, pipe-to-cable, duplicate id, unclassified element, zone that serves |
| type edits broadcast; occurrence overrides win; the catalog is the class prims | B5 |
| one `IsA` sweeps the spatial structure; mezzanine legal; container seen through a wall | B1, element boundary |
| one `IsA` sweeps the groups; membership resolves; reverse lookup | B4 |
| rename a space → 5 dangling targets → `repath` repairs 5 by id | R6 |
| no plugins loaded: `AecoLevel` falls back to `Xform`, `AecoSystem` to `Scope`, transforms identical, data legible | B7 |
| zero-gprim stage conformant | the semantic-structure claim |
| classification census; zero unclassified; `IfcWall` query finds both walls | B3 / D4 |
| port graph traced basin → mains | D7 |
| a zone layer added then muted: every element's world transform unchanged | E11 |

| Python validator plugin discovery | the same registered rules serve the CLI, profiles and tests |
| Mesh marked exact errors; analytic Cube passes; absent tolerance warns | E15 |
| unknown BrepArray composes plugin-free with a linked renderable Mesh twin | B7 / ADR-0009 |
| S01–S26 and usdGenSchema --validate | skeleton and generated-file drift |
