# ADR-0003 — Time composes in layers; variants select representation

**Status:** Accepted (restates E12 for the variant question)

## Context

VariantSets are attractive for old/new states of a document or model:
switchable in any viewer's UI, no tooling needed. But re-implementing time
outside the information clock (E12) forfeits every composition service —
partial re-derivation, atomicity, provenance, `?at=` resolution.

## Decision

**Which state exists is layer selection; how a state is shown is a
variant.** Issue revisions, document supersessions, review states: always
stamped layers, selected by slice roots or muting. Variants are reserved
for representation choices on one state — `repr` on representations — and for
design options on spatial referents (`designOption`). A `revision`-like
variantSet is forbidden.

## Consequences

- Old/new toggling ships as authored slice roots (plain sublayer lists),
  not variant switching; vanilla-viewer convenience is preserved by the
  slices themselves.
- Variant names form a closed grammar; adding one is an ADR-level change.
- Identity and phase queries retain one meaning across representation choices.

## Precedent

E12 (one information clock); baseline-vs-current by stamped-layer muting;
the ruling that "version diffing is composition, not snapshot arithmetic".
