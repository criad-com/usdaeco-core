#!/pxrpythonsubst
import unittest
import bootstrap
from pxr import Plug, Sdf, Usd, UsdGeom, UsdValidation
from usdaeco_tools import validators

Plug.Registry().RegisterPlugins(str(bootstrap.ROOT / "usdAecoValidators"))


def marked(kind="Mesh", tolerance=None):
    stage = Usd.Stage.CreateInMemory()
    element = stage.DefinePrim("/Element", "Xform")
    element.CreateAttribute("aeco:id", Sdf.ValueTypeNames.String).Set("element")
    prim = stage.DefinePrim("/Element/Body", kind)
    prim.ApplyAPI("AecoDerivedGeometryAPI")
    prim.GetAttribute("aeco:derived:source").Set("element")
    prim.GetAttribute("aeco:derived:approx").Set("exact")
    if tolerance is not None:
        prim.GetAttribute("aeco:derived:tolerance").Set(tolerance)
    return stage, prim


def errors(stage):
    return validators.validate_stage(stage, include_builtin=False)


class TestValidators(unittest.TestCase):
    def test_DerivedExactOnMesh(self):
        stage, prim = marked(tolerance=1e-6)
        findings = errors(stage)
        self.assertEqual([e.GetName() for e in findings], ["DerivedExactOnMesh"])
        self.assertEqual(findings[0].GetType(), UsdValidation.ValidationErrorType.Error)
        self.assertEqual(str(findings[0].GetSites()[0].GetPrim().GetPath()), "/Element/Body")
        prim.GetAttribute("aeco:derived:approx").Set("tessellated")
        self.assertEqual(errors(stage), [])
        for kind in ("Cube", "Cylinder", "Sphere", "Cone", "Capsule", "BrepArray"):
            with self.subTest(kind=kind):
                stage, prim = marked(kind, 1e-6)
                self.assertEqual(errors(stage), [])

    def test_ExactWithoutTolerance(self):
        stage, prim = marked("Cube")
        for tolerance in (0, -1, float("nan"), float("inf")):
            with self.subTest(tolerance=tolerance):
                prim.GetAttribute("aeco:derived:tolerance").Set(tolerance)
                findings = errors(stage)
                self.assertEqual([e.GetName() for e in findings], ["ExactWithoutTolerance"])
                self.assertEqual(findings[0].GetType(), UsdValidation.ValidationErrorType.Warn)
        prim.GetAttribute("aeco:derived:tolerance").Set(1e-6)
        self.assertEqual(errors(stage), [])
        prim.GetAttribute("aeco:derived:approx").Set("driverEval")
        prim.GetAttribute("aeco:derived:tolerance").Set(0)
        self.assertEqual(errors(stage), [])

    def test_plugin_listing(self):
        from usdAecoValidators.validatorTokens import KEYWORD
        registry = UsdValidation.ValidationRegistry()
        metadata = registry.GetValidatorMetadataForKeyword(KEYWORD)
        self.assertEqual(len(metadata), 8)
        self.assertTrue(all(registry.GetOrLoadValidatorByName(m.name) for m in metadata))

    def test_legacy_error_names(self):
        # Retained validators still emit the public v0.8 codes, through the adapter.
        stage = Usd.Stage.CreateInMemory()
        a = stage.DefinePrim("/A", "Xform"); a.ApplyAPI("AecoElementAPI")
        b = stage.DefinePrim("/B", "Xform"); b.ApplyAPI("AecoElementAPI")
        self.assertIn("missingId", [e.GetName() for e in errors(stage)])
        for p in (a, b): p.GetAttribute("aeco:id").Set("same")
        names = {e.GetName() for e in errors(stage)}
        self.assertTrue({"malformedId", "duplicateId", "unclassifiedElement"} <= names)

    def test_wireframe_purpose(self):
        stage, prim = marked("BasisCurves", 1e-6)
        prim.GetAttribute("aeco:derived:role").Set("wireframe")
        self.assertIn("derivedGeometryPurpose", [e.GetName() for e in errors(stage)])
        UsdGeom.Imageable(prim).CreatePurposeAttr("guide")
        self.assertEqual(errors(stage), [])


if __name__ == "__main__":
    unittest.main()
