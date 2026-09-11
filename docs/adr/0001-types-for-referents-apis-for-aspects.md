# ADR-0001 — Types are for referents; aspects are applied APIs

**Status:** Accepted (codifies standing practice)

## Context

Every schema addition faces the same fork: mint a concrete prim type
("is-a") or apply an API schema to an existing prim ("has-aspect"). The
family needs one rule, because the fork keeps recurring — proxies, derived
representations, review markers, future physics-adjacent needs — and
inconsistent answers fragment queries, validators and composition
behaviour.

## Decision

**Mint a concrete type only for a referent: an entity with no other
existence in the scene graph** — a thing that owns identity and children (spatial containers,
groups, ports; datums and record prims in their own tiers). **Everything that decorates a prim that is
already something else is an applied API schema** — attribute-only where
possible, so it survives instancing and composes onto any base.

The test: *if the prim were deleted, would a referent vanish, or only a
property of something else?* Referent → type. Property → API.

## Consequences

- Prim-type growth is bounded; the closed type sets stay closed.
- `IsA` queries on aspects become `HasAPI` queries — an accepted trade.
- New aspects reach *foreign* geometry (imported meshes, native exports)
  without retyping, which typing makes impossible.
- A proposal that mints a type must argue the referent test explicitly.

## Precedent

- **usdLux, USD 21.02**: lights shipped as a typed hierarchy and had to be
  refactored into `UsdLuxLightAPI` so geometry could *be* a light — the
  canonical cost of typing an aspect. Concrete light types survive only
  for pure luminaires (referents with no other existence).
- **usdPhysics**: `RigidBodyAPI`, `CollisionAPI`, `MassAPI` decorate
  existing prims; types exist only for entities with no prior scene
  presence (`PhysicsScene`, joints, `CollisionGroup`).
- **usdShade / UsdGeom**: `MaterialBindingAPI`, `ModelAPI`, `MotionAPI` —
  aspects on existing prims throughout.
- **usdAeco**: `AecoElementAPI`, the kind-library APIs (chosen
  attribute-only explicitly to survive instancing); concrete types only
  for referents (spatial types, group types, ports; datums and record
  prims in their tiers) — all with container fallbacks (`Xform`,
  `Scope`), none inheriting gprims (E10: schema points at geometry, never
  encodes it). ADR-0006 applies the same test to the register row.
