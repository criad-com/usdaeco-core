"""Python UsdValidation plugin wrapping the core companion rules."""
from pathlib import Path
import os
import sys
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(Path(os.environ.get("TOOLCHAIN_DIR", ROOT.parent / "usdaeco-toolchain")) / "tools"))
from usdaeco_tools import validators as legacy
from usdaeco_check.validation import register_prim_validator, register_stage_validator, wrap_legacy
from . import validatorTokens as tokens

register_stage_validator(tokens.IDENTITY_CHECKER, wrap_legacy(tokens.IDENTITY_CHECKER, lambda target: legacy._validate_identity(target, None)))
register_prim_validator(tokens.SPATIAL_GRAMMAR_CHECKER, wrap_legacy(tokens.SPATIAL_GRAMMAR_CHECKER, lambda target: legacy._validate_spatial_grammar(target, None)), ['UsdGeomImageable'])
register_prim_validator(tokens.CLASSIFICATION_CHECKER, wrap_legacy(tokens.CLASSIFICATION_CHECKER, lambda target: legacy._validate_classification(target, None)), ['UsdTyped'])
register_prim_validator(tokens.PORT_CONNECTIVITY_CHECKER, wrap_legacy(tokens.PORT_CONNECTIVITY_CHECKER, lambda target: legacy._validate_port(target, None)), ['UsdAecoPort'])
register_prim_validator(tokens.GROUP_CHECKER, wrap_legacy(tokens.GROUP_CHECKER, lambda target: legacy._validate_group(target, None)), ['UsdAecoGroupBase'])
register_prim_validator(tokens.DERIVED_GEOMETRY_CHECKER, wrap_legacy(tokens.DERIVED_GEOMETRY_CHECKER, lambda target: legacy._validate_derived_geometry(target, None)), ['UsdAecoDerivedGeometryAPI'])
register_prim_validator(tokens.DERIVED_EXACT_ON_MESH_CHECKER, wrap_legacy(tokens.DERIVED_EXACT_ON_MESH_CHECKER, lambda target: legacy._validate_exact_mesh(target, None)), ['UsdAecoDerivedGeometryAPI'])
register_prim_validator(tokens.EXACT_WITHOUT_TOLERANCE_CHECKER, wrap_legacy(tokens.EXACT_WITHOUT_TOLERANCE_CHECKER, lambda target: legacy._validate_exact_tolerance(target, None)), ['UsdAecoDerivedGeometryAPI'])
