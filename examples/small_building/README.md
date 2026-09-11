# Small Building

Open `result/example.usdc` with stock USD; no family plugin or sibling checkout
is needed. `result/vanilla.png` is the independently rendered stock USD proof.

The source is [the authored core stage](../../usdAeco/examples/small_building.usda).
Run `env -u PYTHONPATH python run.py --publish` to refresh the committed result
in the environment described by the [root README](../../README.md).
An ordinary run only writes transient `out/` evidence.

The room is 6 x 4 m clear with 0.2 m walls, 2.7 m high, on a 0.2 m slab.
The south wall has two piers and a lintel around a 1 x 2.1 m door opening;
the west wall surrounds a 1.2 x 1.2 m window. The approach corridor has low
side walls. The original upper level and plumbing identities remain, including
the roof-level service fixture. All 16 elements are classified; all 38 gprims
carry the derived mark. The view is isometric and framed from geometry bounds.

`result/layers/out/authored.usda` preserves the original example;
other own layers retain the view and any derived symbols. The flattened crate
is the standalone entry point. Findings are checked through all eight core
UsdValidation rules; any pre-existing warning is recorded explicitly in
`expected/findings.json`. Publication uses the harness's minimal source mode.
