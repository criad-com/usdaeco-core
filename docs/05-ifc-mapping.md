# 5 · IFC and the core concept map

The map preserves identity and the built thing's structure. It does not
promise reconstruction of every IFC feature. A reference converter exists
outside the core.

## 5.1 The concept map

| IFC concept | Core representation | Contract |
|---|---|---|
| `IfcProject` | Root `Xform` with `AecoProjectAPI` | Project name and id; units and up direction are stage metrics |
| `IfcSite` | `AecoSite` | Sites may nest |
| `IfcBuilding`, `IfcFacility` and facility subtypes | `AecoFacility` with classification | The IFC entity names the kind |
| `IfcFacilityPart` and its subtypes | `AecoFacilityPart` with classification | Recursive parts express wings, sections and subdivisions |
| `IfcBuildingStorey` | `AecoLevel` | Retain empty and partial levels; placement determines elevation |
| `IfcSpace`, `IfcExternalSpatialElement` | `AecoSpace` | Interior and exterior spaces share one type |
| Aggregation and spatial containment | Namespace descent | The nearest spatial ancestor is the primary container |
| Referenced spatial containment | `aeco:referencedContainers` on an element | Secondary spatial anchors do not reparent the element |
| Physical element and `PredefinedType` | `AecoElementAPI` plus `AecoClassificationAPI:ifc` | For example `IfcWall.PARTITIONING`; no separate kind token |
| `IfcTypeObject` and type assignment | Class prim with `AecoTypeAPI`; occurrence `inherits` | Product values compose; occurrence overrides win; identity stays on the occurrence |
| `IfcSystem`, `IfcDistributionSystem` and group assignment | `AecoSystem` with `CollectionAPI:members` | Classification supplies system kind; `displayName` supplies its label |
| `IfcRelServicesBuildings` | `aeco:serves` | A system's spatial service scope is independent of its members |
| `IfcZone`, `IfcSpatialZone` | `AecoZone` with members | Any required spatial extent is a space in the containment tree |
| `IfcDistributionPort`, connected ports | Child `AecoPort` prims | Relative placement, medium, flow and symmetric `aeco:connectedPorts` |
| `GlobalId` | `aeco:id` | Decode the same UUID, as below |
| Psets and quantities | Custom `aeco:props:<Set>:<name>` attributes | Preserve value types and units; a list remains an array |
| Enumeration property | Scalar for one selection, ordered array for several | Keep property types compatible across catalog and occurrence opinions |
| Common `Status` on occurrence, else type | `aeco:phase` | NEW → proposed, EXISTING → existing, DEMOLISH → demolished, TEMPORARY → temporary; unknown leaves no opinion |
| Body geometry | Plain USD gprims under the element | Separate derived layer; `AecoDerivedGeometryAPI` identifies source, role, approximation and stamp |
| Space body geometry | Marked gprim under the space | Role `extent`, purpose `guide`; the volume is not an obstacle |

Placements must be converted consistently to stage units, including local
vertices, nested transforms and the level datum. A stage authors
`fallbackPrimTypes` for every used core type so it composes without plugins.
The reverse structural map compresses ids, reconstructs containment,
classification, membership and port links, and reads resolved catalog values.

## 5.2 Identity recipe

An IFC `GlobalId` encodes a 128-bit UUID in 22 characters. The core uses the
same UUID in lowercase hyphenated form:

```python
import uuid
import ifcopenshell.guid

aeco_id = str(uuid.UUID(hex=ifcopenshell.guid.expand(global_id)))
global_id = ifcopenshell.guid.compress(uuid.UUID(aeco_id).hex)
```

For a source with no UUID, agree a stable project key, route, kind and source
key. Derive the namespace and id from these exact UTF-8 strings, without
normalizing case or whitespace:

```python
root_namespace = uuid.uuid5(uuid.NAMESPACE_URL, "urn:usdaeco:id:v1")
project_namespace = uuid.uuid5(root_namespace, project_key)
aeco_id = str(uuid.uuid5(project_namespace, f"{route}:{kind}:{source_key}"))
```

Publish those inputs as part of the exchange contract. Retain a known source
UUID whenever one exists. Several exports of the same referent compose
opinions on one `aeco:id`; core has no alternate identity or equivalence
property. Path repair joins by id after a rename or move.

## 5.3 Deliberately lossy features

| Source feature | What survives; what is not preserved |
|---|---|
| Objectified `IfcRel*` entities | Containment, links and membership survive; relationship entity identity does not |
| `CompositionType` | Recursive containment survives; the separate composition enum does not |
| Deprecated storey `Elevation` | Placement-derived datum survives; a conflicting source elevation does not |
| Property-set definitions | Typed values survive in the quarantine; the IFC definition graph does not |
| Material layer sets and swept profiles | Descriptive values may survive in the quarantine; editable construction recipes are outside core |
| Openings and virtual elements | The represented body may include their effects; core defines no opening or void mechanism |
| Grids and alignments | Core defines no datum or stationing contract |
| Tasks, actors, documents and costs | Core defines no project-record mapping |
| Exact topology and geometric operations | The mark records provenance and approximation; geometric reconstruction is not guaranteed |
