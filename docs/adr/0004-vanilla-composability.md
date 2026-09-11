# ADR-0004 — Everything a consumer looks at composes in a vanilla USD runtime

**Status:** Accepted

## Context

Review and coordination surfaces could be built as plugin-dependent viewer
features (custom panels, injected state). That couples the surface to one
viewer build and makes every artifact invisible to clients, other DCCs and
future runtimes.

## Decision

Everything a reader looks at is **authored USD that composes in a
vanilla runtime**: roots are plain sublayer lists; representations are plain gprims
(ADR-0002); toggles are variants (ADR-0003) and purposes. Core plugins enrich
semantic queries without gating composition.
Applied API schemas may enrich behaviour when loaded but must degrade to
inert extra properties when not.

## Consequences

- Any USD-capable tool can open a slice and see the review state.
- Features are designed data-first: if it cannot be expressed as authored
  composition, it needs an ADR-level argument for viewer code.
- Conformance checks run per runtime cheaply (open, compose, render)
  because nothing depends on plugin presence.

## Precedent

The codeless-schema doctrine (pure data contracts); `purpose = guide` on
ports and datums chosen for vanilla-viewer behaviour; ADR-0002's collapse
of the fallback machinery by using native prim types; promise B7.
