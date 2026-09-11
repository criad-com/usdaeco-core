# ADR-0007 — Drivers in, derived out: the core representation contract

**Status:** Accepted; axis ownership superseded by [ADR-0008](0008-the-axis-leaves-the-core.md). E13/E14 remain in force.

## Context

The first element-kind libraries — walls and pipes — exist to let an
element be edited in USD and rebuilt natively in an authoring tool or an
IFC toolchain, with geometry and validation returning. Research across
the three environments found
one anatomy for every path-based element: a driving axis, a section
owned by the type, a derived body, and end relations. Every host derives
length from the axis; none consumes a mesh as an input; each regenerates
its own body. Two things would otherwise be re-minted by every
path-based library and every adapter: the axis, and the mark that says a
gprim was derived from an element by a tool. ADR-0002 already committed
to the second (plain gprims plus an applied API) but the v0.6 core ships
no such API.

## Decision

`AecoDerivedGeometryAPI` marks an existing gprim with its source identity,
role, approximation and derivation stamp. The current contract also carries
representation source links and tolerance (ADR-0009). It adds no geometry
type. Path drivers are optional and outside the core (ADR-0008).

E13 distinguishes drivers from derived properties through the registered
boolean property metadatum `aecoDerived`. Editors author drivers; derived
opinions are authored in separate layers. E14 makes geometry an output of
derivation, with marked gprims beneath their referent.

## Consequences

Core consumers can identify derived representations without interpreting
the inputs that produced them. Five applied schemas and one registered
metadata field suffice; no driver set is required to read a core stage.
The source is the referent's existing `aeco:id`, never a second identity.

## Precedent

`UsdGeomImageable.purpose` and `proxyPrim`; ADR-0001's applied-aspect rule;
ADR-0002's plain-gprim representation pattern.
