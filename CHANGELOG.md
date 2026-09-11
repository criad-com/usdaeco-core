# Changelog

## 0.9.2

- Re-author the small building as a dimensioned enclosure: 6 × 4 m clear room,
  0.2 m floor slab and walls, 2.7 m wall height, roof, door opening, window,
  approach corridor, cylindrical pipework and cable tray. Preserve all original
  identities and connectivity; increase the classified element census to 16.
- Add an isometric bounds-framed preview and a measured walls-meet check.
- Publish all six examples with flattened crates, own USDA layers, manifests
  and fresh stock USD renders. Keep the five zero-geometry sources unchanged;
  derive labelled schematic hierarchy views separately.
- Pin toolchain v0.3.1; run check_example for all six results with all eight
  core validators loaded. The shared harness's unused data pin is metadata only.
- Remove governance prescriptions and their chapter; renumber worked examples
  to 07 and open questions to 08 and update all links. Registry commentary uses
  notes instead of governance keys.
- Switch the repository licence to MIT. Report toolchain 0.3.1's Apache-only
  S01 and copyright-line S25 failures without wrappers or exemptions. Use the
  USD 26.8 finding-site API in the example hook. No schema property, type,
  default or class changes.
- Nix remains unproven: one offline check could not resolve a public input (404).

## 0.9.1

- Documentation and hygiene release: current contracts and examples are core-only.
- Remove obsolete documents and archived verification artifacts.
- Add a permanent core vocabulary and documentation-boundary check with seeded failures.
- Add executable pipe-run and wall-corner examples with separate derived layers.
- Schema changes are doc strings only; the 8/2/5 registry, properties and defaults are unchanged.
- Check against the exact build dependency v0.2.1.

## 0.9.0

- Move the axis API and converter to their owning libraries.
- Adopt the flat schema skeleton, Python validator plugin, testenv and public pins.
- Extend the derived mark with source links, tolerance, wireframe and driverEval;
  add E15 validation and plugin-free Mesh twin composition checks.
- Add the family map, ADRs 0008–0011 and a reproducible small-building render.

## 0.8.4

- Reconcile the README and example documentation with the then-current releases.
- Update open questions and documented exchange limitations.
- Bump manifest and rebuilt plugin metadata to 0.8.4.
- Documentation release; schema declarations and examples are unchanged.

## 0.8.3

- Normalize single-item IFC enumerations to scalar quarantined values on
  both catalog types and occurrences. Keep multi-value selections ordered;
  choose arrays consistently when a type/occurrence family mixes cardinality.
- Distinguish enumerations from ordinary IFC lists, retaining one-item
  string and numeric lists as arrays. Common Status phase mapping is unchanged.
- Add three generated converter regressions and a standalone demo conversion
  validation probe. Preserve every existing check and all six USD examples.
- Publish version 0.8.3 in `library.json` and rebuilt codeless plugin metadata.

## 0.8.1

- Emit spatial children, elements, catalog types, systems, ports and meshes
  in stable source-identity order. Catalog name collisions use the decoded
  type UUID instead of its STEP entity number (issue #6).
- Resolve group membership after declaring all groups, preserving targets
  that refer to a group declared later. Preserve relationship sequences,
  ordered values, mesh arrays, transforms and explicit USD reorder opinions.
- Add independent IFC builds with shuffled creation order and numbering,
  name collisions, distinct hash seeds and one/two tessellation threads.
  Compare emitted bytes and layer texts without declaration normalization.
- Give every converter claim and pytest case a fresh temporary directory
  and subprocess. Seed stale artifacts to verify they are ignored and left
  untouched across repeated probes; retain the original determinism claim.
- Publish version 0.8.1 in the source manifest and rebuilt plugin metadata;
  document ordering and test reproduction in the mapping guide and README.

## 0.8.0

- Preserve IFC4 building/storey containment, traverse unmapped aggregates,
  and retain empty roof levels without changing element world placements.
- Map occurrence Common Status, then type Status when absent, to authored
  element phases. Unknown or conflicting source values stay unauthored.
- Retain space bodies as placed `Extent` guide meshes in the geometry
  layer, with spatial source identity and derivation provenance.
- Add `extent`, `sector` and `coverage` derived-geometry roles. Validate
  role vocabulary and require guide purpose for these three roles.
- Omit blank property headings before sanitization, preserve genuine
  name collisions, and report omission, phase and extent counts.
- Declare version 0.8.0 in `library.json`; build plugin metadata from it.
- Keep all 25 existing checks; add 15 generated IFC/converter claims and
  15 pytest cases. Six authored USD examples remain byte-identical.
