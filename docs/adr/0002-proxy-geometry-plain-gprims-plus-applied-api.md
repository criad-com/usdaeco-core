# ADR-0002 — Derived / proxy geometry is plain gprims + an applied API

**Status:** Accepted

## Context

Simplified stand-in geometry for elements (a slab for a wall, a run for a
duct, a box for equipment) is needed for review, fast display and
projection. An earlier design proposed concrete typed proxies inheriting
the gprims (`AecoArchWallProxy` ← `Cube`, `AecoMepRoundProxy` ←
`Cylinder`, …) with `fallbackPrimTypes` degradation. Stress-tested against
ADR-0001 and its precedents, the typed design fails the referent test: a
proxy prim's entity identity is its *shape*; proxy-ness — "this gprim
stands in for element X, derived by tool Y under approximation Z" — is an
aspect. Typing it repeats pre-21.02 usdLux, and hits the same wall: when
native meshes arrive they must be markable as proxies too, and a `Mesh`
cannot be retyped into a proxy class. It would also be the family's first
gprim-inheriting schema, breaking E10.

## Decision

Derived representations are plain USD gprims beneath their referent, marked
with `AecoDerivedGeometryAPI`. The mark supplies source identity, role,
approximation and stamp, plus representation source links and tolerance
(ADRs 0007 and 0009). A proxy carries role `proxy` and `purpose = proxy`;
`proxyPrim` connects a full representation to its proxy where appropriate.

## Consequences

Plain gprims render in stock USD. Unknown applied schemas leave extra
properties inert, so the mark requires no custom geometry type or fallback.
Queries use the mark and the referent's classification. Prim names remain
human-readable hints; role and approximation are the machine-readable data.

## Precedent

usdLux 21.02 refactor (aspect typed → API, at real migration cost);
usdPhysics decorate-don't-mint; E10 and the attribute-only-API house
idiom; UsdGeom `purpose`/`proxyPrim` as the native proxy aspect.
