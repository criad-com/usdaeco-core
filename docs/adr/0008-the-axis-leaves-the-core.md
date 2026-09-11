# ADR-0008 — The axis leaves the core

**Status:** Accepted

## Context

A representation-first dataset must be admissible. Requiring a driving axis on every path element makes that route impossible and couples generic identity to a specific editing model.

## Decision

Core requires no path drivers and keeps `AecoDerivedGeometryAPI` as its
one representation mark. This supersedes the path-driver ownership part
of ADR-0007. Identity, containment, ports and classification remain usable
with representations alone.

## Consequences

Core has five applied schemas. E13 and E14 remain unchanged: editors author
drivers and derived values belong in separate layers. Consumers can read
and display a core stage without a path-editing model.
