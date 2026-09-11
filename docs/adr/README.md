# Architecture Decision Records

Load-bearing decisions, one file each, Nygard format (Status · Context ·
Decision · Consequences · Precedent). ADRs codify the razors the design
documents argue for; a design document cites ADRs, an ADR never restates
a design.

| # | Title | Status |
|---|---|---|
| [0001](0001-types-for-referents-apis-for-aspects.md) | Types are for referents; aspects are applied APIs | Accepted |
| [0002](0002-proxy-geometry-plain-gprims-plus-applied-api.md) | Derived / proxy geometry is plain gprims + an applied API | Accepted |
| [0003](0003-time-in-layers-variants-for-representation.md) | Time composes in layers; variants select representation | Accepted |
| [0004](0004-vanilla-composability.md) | Everything a consumer looks at composes in a vanilla USD runtime | Accepted |
| [0005](0005-kind-is-classification-no-category-token.md) | Kind is classification; the core carries no category token | Accepted |
| [0006](0006-register-row-leaves-the-core.md) | The register row leaves the core; groups are referents | Accepted |
| [0007](0007-drivers-in-derived-out.md) | Drivers in, derived out: the core representation contract | Accepted |

- [ADR-0008 — The axis leaves the core](0008-the-axis-leaves-the-core.md)
- [ADR-0009 — Exact geometry is a derived representation](0009-exact-geometry.md)
- [ADR-0010 — Validators are UsdValidation plugins](0010-validator-plugins.md)
- [ADR-0011 — One skeleton for every repository](0011-one-skeleton.md)
