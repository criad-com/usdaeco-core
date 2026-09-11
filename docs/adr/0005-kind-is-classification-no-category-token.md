# ADR-0005 — Kind is classification; the core carries no category token

**Status:** Accepted (supersedes the v0.5 `aeco:category` design)

## Context

The previous core carried a coarse, registry-governed `aeco:category`
token on every element (`wall`, `door`, `pipeSegment`, …) beside the
`AecoClassificationAPI` instances that carried fine kind. It was argued
as census vocabulary: a query surface independent of any dictionary, an
unset-rate health metric, and a 1:1 pushdown target for authoring-tool
category filters.

In practice it was three things the family's own rules forbid. A **dual
encoding**: on every converted element `aeco:category = "wall"` and
`aeco:class:ifc:code = "IfcWall"` said the same fact twice, with a table
in between that could drift. A **home-grown taxonomy**: a fifty-token
list that would grow to hundreds, competing with the published,
URI-addressed dictionaries rule E4 says to use — and needing sector
overlays, divergence tables and a parallel vocabulary maintenance process in
the *core*. And a **discipline-shaped** one, since the natural
extension was one token per product kind — the IFC entity list rebuilt
by hand.

## Decision

**The core has exactly one kind mechanism, classification, and no kind
vocabulary of its own.** What an element, a spatial container, a group
or a catalog type *is* comes only from `AecoClassificationAPI:<system>`
instances — code, name, URI — into external dictionaries. The core
governs only the *names* of the systems (`registries/
classification_systems.json`) so two tools name one dictionary one way,
and recommends `ifc` as the default instance because every mainstream
tool can emit an IFC entity name.

The coarse census is a classification query (`classified_as(stage,
"IfcWall")` matches `IfcWall` and `IfcWall.PARTITIONING`). The health
metric is the share of elements with no classification code, plus the
share coded as `IfcBuildingElementProxy` — IFC's own "kind unknown",
carried verbatim. If the ecosystem ever needs a schema-neutral
census vocabulary, it is *another classification system* — an instance
name in the registry with codes from a registry file — never a core
property.

## Consequences

- The core loses a property, a registry, a validator and the sector
  overlay mechanism; `AecoElementAPI` is identity + phase +
  referencedContainers.
- The IFC classification code needs no class-to-category table.
- Authoring-tool pushdown keys on a classification code instead of a
  token; where the tool has an IFC-class or category filter the mapping
  is still 1:1.
- Existing v0.5 stages stay legible (the old attribute becomes an
  ignorable custom property) and migrate by one inversion of the old
  registry's IFC mapping.
- Lost: a dictionary-free coarse vocabulary. Accepted — every surveyed
  writer can name an IFC class, and the family's whole argument is that
  home-grown vocabularies are how convergence fails.

## Precedent

Rule E4 and risk R2 (taxonomy capture); the `IfcWallStandardCase` saga
as the canonical cost of a second encoding for one concept; UsdSemantics
labels kept as an optional mirror precisely because they carry no
code/URI/version semantics.
