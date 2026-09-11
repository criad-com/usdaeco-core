# 8 · Open questions about the core

These questions concern the core boundary or its guarantees. They do not
change the published fifteen-class surface.

**Default classification.** Should a core exchange profile require an `ifc`
classification on every element, or should any registered system suffice?
The schema is neutral; the default profile currently warns on missing codes.

**Group vocabulary.** Do recurring group requirements justify a third type,
or can `AecoSystem`, `AecoZone` and ordinary collections express them? Any
addition needs evidence that classification and applied aspects cannot.

**Units beyond length.** How should consumers discover units for quarantined
quantities without inventing a competing measurement schema? Core lengths
use stage units, except the derived tolerance explicitly fixed in metres.

**Geospatial anchoring.** Which existing USD geolocation conventions should
anchor sites? No provisional core coordinate-reference attributes are defined.

**Space boundaries and adjacency.** Is an additional core relationship ever
necessary, or should boundaries remain geometric descriptions attached to
existing spatial referents? An exchange must demonstrate the need before
expanding the contract.

**Datum admission.** Would grids, alignments or benchmarks meet the threshold
for expanding the closed referent sets? Required evidence includes linear
infrastructure addressing and the effect on the containment grammar.

**Sub-element identity.** Can native subsets identify a face, weld or detail
without duplicating element identity? `UsdGeomSubset` is not Imageable, so
`AecoElementAPI` cannot apply to it under the current restriction.

**Scale.** A benchmark with at least 50,000 elements and instanced prototypes
is still owed before a 1.0 performance claim. Measure stage-open time,
validation, membership queries and identity-based path repair separately.

**Representation correlation.** The core records source links and tolerance,
but does not prove geometric equivalence. Further requirements must separate
what the mark can validate from what requires geometric computation.
