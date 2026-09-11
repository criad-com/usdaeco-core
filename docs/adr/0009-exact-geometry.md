# ADR-0009 — Exact geometry is a derived representation

**Status:** Accepted

## Context

An exact body and its display tessellation describe the same referent. The representation mark needs to record their correlation and modelling precision without adding a family geometry domain.

## Decision

The core mark records representation source links (`aeco:derived:from`),
tolerance in metres, the `wireframe` role and `driverEval` approximation.
Exact bodies use render purpose; a Mesh twin uses proxy purpose. The exact
body targets its twin through `proxyPrim`, and the Mesh targets its source
through `aeco:derived:from`. E15 rejects exact Meshes and warns on unknown
exact tolerance. Straight guides and wireframes can be exact; segmented
arcs declare `arcSegmented`.

## Consequences

B7 requires a renderable Mesh twin when an exact representation is unknown
to a consumer. An unknown geometry type must not fall back to `Xform` or an
abstract gprim. Core introduces no geometry carrier or opaque payload.
The composition fixture checks fallback display and correlation only;
topology, measurement accuracy and reconstruction are not core guarantees.
