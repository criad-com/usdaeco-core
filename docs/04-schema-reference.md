# 4 · Schema reference

Every property, with its fallback, for the core library. The
authoritative source is `usdAeco/schema.usda` — the doc strings
there carry the reasoning; this page is the index. ° marks an abstract
type (never serialized in a stage).

Conventions: `aeco:` is the core namespace; each downstream library owns
exactly one namespace of its own (`aeco:<library>:`). Ad-hoc
data lives under `aeco:props:<Set>:<name>` only. Lengths are stage linear
units.

## 4.1 The spatial structure

| Schema | Kind | Properties (· fallback) |
|---|---|---|
| `AecoSpatialBase`° | abstract typed (Xformable) | `aeco:id` string · ""; `aeco:phase` token [proposed, existing, demolished, temporary] · proposed |
| `AecoSite` | typed (fallback Xform) | — (nests; may directly contain facilities, spaces and site-works elements) |
| `AecoFacility` | typed (fallback Xform) | — (kind = classification, e.g. `aeco:class:ifc:code = "IfcRoad"`; facility ⊃ facility is an error) |
| `AecoFacilityPart` | typed (fallback Xform) | — (concrete and recursive: wing > storey, section > segment) |
| `AecoLevel` (: `AecoFacilityPart`) | typed (fallback Xform) | `aeco:elevation` double · 0 — declarative datum in the nearest facility's frame; a validator warns on drift from placement |
| `AecoSpace` | typed (fallback Xform) | — (nests; legal under site, facility, part or space) |

## 4.2 Groups

| Schema | Kind | Properties (· fallback) |
|---|---|---|
| `AecoGroupBase`° | abstract typed | `aeco:id` string · ""; built-in `CollectionAPI:members`; `collection:members:expansionRule` · explicitOnly |
| `AecoSystem` | typed (fallback Scope) | `rel aeco:serves` — the spatial prims and/or zones this system serves |
| `AecoZone` | typed (fallback Scope) | — |

A group's human label is the prim's `displayName` metadata; its kind is a
classification instance (`IfcDistributionSystem.DOMESTICCOLDWATER`,
`IfcSpatialZone.FIRESAFETY`); everything a project *says* about it
(title as data, status, owner) is the record tier's applied row.

## 4.3 Ports

| Schema | Kind | Properties (· fallback) |
|---|---|---|
| `AecoPort` | typed (Xformable, fallback Xform) | `purpose` token · guide (fallback override: ports hide in vanilla viewers unless guides are shown); `aeco:id` string · ""; `aeco:medium` token [pipe, duct, cable, cableCarrier, wireless, other, undefined] · undefined; `aeco:flowDirection` token [source, sink, bidirectional, undefined] · undefined; `rel aeco:connectedPorts` (author on both ends) |

`undefined` is a wildcard on both medium and flow: the validator refuses
only *stated* incompatibilities (pipe ↔ cable, source ↔ source).

## 4.4 Applied schemas

| Schema | Apply | Properties (· fallback) |
|---|---|---|
| `AecoProjectAPI` | single → Xform, on the root model prim | `aeco:project:name` string · ""; `aeco:project:id` string · "" |
| `AecoElementAPI` | single → Imageable (validator refuses it on spatial prims and ports) | `aeco:id` string · ""; `aeco:phase` token [proposed, existing, demolished, temporary] · proposed; `rel aeco:referencedContainers` (secondary spatial anchors, any type, any facility) |
| `AecoClassificationAPI` | multi-apply → Typed, `aeco:class:<system>:`; instance names from `registries/classification_systems.json` | `code` string · ""; `name` string · ""; `uri` string · "" |
| `AecoTypeAPI` | single → Typed, on catalog class prims (occurrences compose it through `inherits`) | `aeco:type:manufacturer` / `model` / `catalogUri` string · "" |
| `AecoDerivedGeometryAPI` (extended v0.9.0) | single → Gprim; the mark on derived geometry, a descendant of its element or spatial referent | `aeco:derived:source` string · "" (the referent's `aeco:id`); `aeco:derived:role` token [body, proxy, axis, footprint, symbol, extent, sector, coverage, wireframe] · body; `aeco:derived:approx` token [exact, driverEval, tessellated, arcSegmented, defaultDims, bbox] · exact; `aeco:derived:stamp` string · ""; `rel aeco:derived:from` · [] (representation sources, N:1); `aeco:derived:tolerance` double · 0 m (unknown) |

The additive roles `extent` (a spatial volume, **never an obstacle**),
`sector` (an analytic view sector) and `coverage` (analytic clipped
coverage) require `purpose = guide`. An extent belongs under its spatial
referent; sensor guides remain descendants of their element.
Source identity and stamp follow the same derived-geometry contract.
Guide geometry stays out of ordinary imaging and bounds, including in a
runtime without AECO plugins, unless guides are explicitly requested.

**Drivers and derived (E13).** A property whose schema definition carries the `aecoDerived` metadatum (registered by this plugin's `plugInfo.json`; the build script bootstraps it for generation) is host-reported; everything else is a driver an editor may author. `usdaeco_tools.is_derived(prop)` reads the flag through the registry.

## 4.5 Registries (versioned data)

| File | Governs | Consumers |
|---|---|---|
| `classification_systems.json` | the instance names of `AecoClassificationAPI` (`ifc`, `uniclass`, `omniclass`, `uniformat`, `masterformat`, `etim`, `bsdd`) with the code form and URI root of each | validators warn on an unknown instance name; the census and health metric read `ifc` by default |
| `prop_sets.json` | sanctioned `aeco:props:<set>` families (`Pset_*`, `Qto_*`, `Ifc*`, `source`) | report/warn on unsanctioned |

That is the whole registry surface of the core. Neither file is a
taxonomy: what a thing *is* comes from the dictionaries themselves.

## 4.6 Validators (`tools/usdaeco_tools/validators.py`)

| Validator | Rules (error unless marked warn) |
|---|---|
| `usdAecoValidators:IdentityChecker` | `missingId` (elements; warn for spatial/group/port prims), `malformedId` (warn), `duplicateId` |
| `usdAecoValidators:SpatialGrammarChecker` | `facilityInFacility`, `badSpatialNesting`, `unanchoredSpatial` (warn), `spatialInsideElement` (warn), `spatialIsElement`, `portIsElement`, `levelWithoutElevation` (warn), `elevationDrift` (warn) |
| `usdAecoValidators:ClassificationChecker` | `unclassifiedElement` (warn), `emptyClassificationCode` (warn), `unregisteredClassificationSystem` (warn), `proxyClassified` (warn) |
| `usdAecoValidators:PortConnectivityChecker` | `danglingPortLink`, `asymmetricPortLink`, `incompatibleFlow`, `mediumMismatch` |
| `usdAecoValidators:GroupChecker` | `zoneAuthorsServes` (warn), `servesTargetsNonSpatial` (warn), `danglingMember` (warn) |
| `usdAecoValidators:DerivedGeometryChecker` | `derivedGeometryOrphan`, `derivedGeometryRole` (unknown token), `derivedGeometryPurpose` (proxy requires proxy; axis, extent, sector, coverage and wireframe require guide); all warn |

| `usdAecoValidators:DerivedExactOnMeshChecker` | `DerivedExactOnMesh`: a Mesh cannot declare `approx = exact` (error) |
| `usdAecoValidators:ExactWithoutToleranceChecker` | `ExactWithoutTolerance`: exact representation has unknown, non-positive or non-finite tolerance (warn) |

The plugin keyword is `UsdAecoValidators`. Existing lower-camel error names
are retained for compatibility; new errors are ProperCase. `driverEval` names
stage-side kernel evaluation of drivers, before host joins, clips and take-outs.
Path drivers and traversal are outside the core.

## 4.7 Conformance profiles

`conformance/profiles/core.json` is the default: universal rules error,
sector-contextual rules warn (D12). A sector or exchange profile is the
same JSON shape with `severity_overrides` hardening named rules
(`"unclassifiedElement": "error"`, `"levelWithoutElevation": "error"`, …)
— rules are never *added* by a profile, only re-graded; new rules are
validators.
