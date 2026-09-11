# 6 · Interfacing with other formats

Every writer meets the same core contract: identity, spatial containment,
classification, phase, groups, ports, catalog inheritance and marked derived
representations. File syntax and transport do not change those meanings.

## 6.1 The exporter contract

A writer of conformant data must:

1. Author the five spatial types as a legal namespace tree. Choose stable
   names; the nearest spatial ancestor is the element's primary container.
2. Apply `AecoElementAPI` to elements, retain one `aeco:id` per referent, and
   author classification instances for known kinds. Keep occurrence ids off
   catalog classes; compose type values with `inherits`.
3. Author systems and zones with `members` collections, and connections as
   symmetric relationships between child `AecoPort` prims. Translate medium,
   flow, placement and lifecycle phase consistently.
4. Put ad-hoc values under `aeco:props:<Set>:`. Keep derived geometry under
   its referent in a separate layer and apply `AecoDerivedGeometryAPI` with
   source identity, role, approximation and stamp. Record tolerance where known.
5. Author stage units, up direction and `fallbackPrimTypes`, then validate
   both the composed stage and its plugin-free fallback behavior.

The [IFC map](05-ifc-mapping.md) supplies the identity recipe and loss list
for that exchange. No transport or exporter implementation is part of core.

## 6.2 Ways data arrives

| Route | USD mechanism | Core obligation |
|---|---|---|
| Materialized export | An ordinary `.usda` or `.usdc` layer | Open and compose without optional plugins |
| File-format adapter | `SdfFileFormat` exposes a source as a layer | Materialize an ordinary USD export for plugin-free exchange |
| Resolved asset | `ArResolver` resolves an asset identifier | Preserve identity and return data satisfying the same stage contract |

These are extension mechanisms, not implementations shipped here. A layer
that still requires a custom file format or resolver is not by itself a
plugin-free exchange artifact.

## 6.3 Pull tiers

**Context tier.** Core semantics support selection by spatial subtree,
classification, phase, system or zone. A receiver can display geometry and
read identity and membership without understanding construction recipes.
That is the core's guaranteed exchange depth.

**Native tier.** A receiver with an additional kind contract may reconstruct
editable native elements from that contract's drivers. It must preserve the
same core identity and containment on re-export. The core representation
mark alone is not a reconstruction recipe.

## 6.4 Selection and pushdown

Selection is a set operation over the composed core stage: collection
membership, containment, classification and phase. Fetching then filtering
is always available when a complete core stage can be obtained. Pushing
selection to a source is an optimization that must produce the same result.
A source may express classification or level filters directly; it may not
express a composed collection or namespace path. In that case fetch a
superset and filter after composition. State the selection contract and
source capabilities rather than silently returning an incomplete set.

## 6.5 Optional semantic labels

`SemanticsLabelsAPI` may mirror classification for consumers that already
understand USD labels. It does not replace `AecoClassificationAPI`: labels
alone do not carry the core code and URI contract. The small-building example
shows both channels on the same referents.
