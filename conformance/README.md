# Conformance profiles

A profile grades the validator suite for a sector, jurisdiction or
exchange (D12: rules are two-tier). It never adds rules — new rules are
validators — it only re-grades named ones.

```json
{
  "name": "core",
  "keywords": ["UsdAecoValidators"],
  "description": "Universal rules error, sector-contextual rules warn.",
  "include_builtin": true,
  "severity_overrides": {}
}
```

A stricter exchange profile hardens warnings that this exchange cannot
tolerate:

```json
{
  "name": "handover",
  "keywords": ["UsdAecoValidators"],
  "description": "Every element classified; every level at a datum.",
  "include_builtin": true,
  "severity_overrides": {
    "unclassifiedElement": "error",
    "proxyClassified": "error",
    "levelWithoutElevation": "error",
    "unanchoredSpatial": "error",
    "missingId": "error"
  }
}
```

Rule names are the `ValidationError` names the validators emit
(`tools/usdaeco_tools/validators.py`). `include_builtin` also runs USD's
own `UsdCoreValidators`.
