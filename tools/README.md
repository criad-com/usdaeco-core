# Core companion tools

`usdaeco_tools` provides core spatial and group queries, classification
registries, port traversal, identity-based path repair and validator callbacks.
`usdaeco_core` provides `aeco-core check`; `usdAecoValidators` exposes the same
rules through `UsdValidation.ValidationRegistry`.

Run from source with `python tools/aeco_core.py check <stage.usda>` after the
build described in the root README. `render_example.py` produces a preview
of the small-building stage through the standard CPU renderer.
