# Early Design

Open `result/example.usdc` with stock USD; no family plugin or sibling checkout
is needed. `result/vanilla.png` is the independently rendered stock USD proof.

The source is [the authored core stage](../../usdAeco/examples/early_design.usda).
Run `env -u PYTHONPATH python run.py --publish` to refresh the committed result
in the environment described by the [root README](../../README.md).
An ordinary run only writes transient `out/` evidence.

The source intentionally contains no geometry. A separate derived layer adds
a labelled hierarchy diagram: blue site/facility, green part/level, teal space,
and amber element symbols. Lines show nearest represented ancestry; group
membership and port connections remain in the USD relationships. Symbol positions
and sizes are diagram layout, not physical dimensions or surveyed placement.
The original referent transforms and semantics are preserved. Mute the symbols
layer when reusing the editable composition to recover the zero-geometry stage.

`result/layers/out/authored.usda` preserves the original example;
other own layers retain the view and any derived symbols. The flattened crate
is the standalone entry point. Findings are checked through all eight core
UsdValidation rules; any pre-existing warning is recorded explicitly in
`expected/findings.json`. Publication uses the harness's minimal source mode.
