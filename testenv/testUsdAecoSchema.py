#!/pxrpythonsubst
import unittest
import bootstrap
from pxr import Plug, Usd, Tf
from usdaeco_check import Report
from claims import run_claims

Plug.Registry().RegisterPlugins(str(bootstrap.ROOT / "usdAeco"))


class TestSchema(unittest.TestCase):
    def test_design_claims(self):
        report = Report()
        run_claims(report)
        for result in report.results:
            with self.subTest(claim=result.name):
                self.assertTrue(result.ok, result.detail)

    def test_closed_surface(self):
        from usdaeco_check.plugins import read_json
        types = read_json(bootstrap.ROOT / "usdAeco/plugInfo.json")["Plugins"][0]["Info"]["Types"]
        self.assertEqual(len(types), 15)
        from claims import TYPED, ABSTRACT, APIS
        self.assertEqual(set(types), {"Usd" + name for name in TYPED + ABSTRACT + APIS})

    def test_mark_schema(self):
        mark = Usd.SchemaRegistry().FindAppliedAPIPrimDefinition("AecoDerivedGeometryAPI")
        self.assertEqual(len(mark.GetPropertyNames()), 6)
        self.assertEqual(mark.GetAttributeFallbackValue("aeco:derived:tolerance"), 0)
        self.assertIn("wireframe", mark.GetPropertyMetadata("aeco:derived:role", "allowedTokens"))
        self.assertIn("driverEval", mark.GetPropertyMetadata("aeco:derived:approx", "allowedTokens"))
        stage = Usd.Stage.CreateInMemory()
        prim = stage.DefinePrim("/Mesh", "Mesh")
        prim.ApplyAPI("AecoDerivedGeometryAPI")
        self.assertTrue(prim.GetRelationship("aeco:derived:from"))

class TestNativeCollectionOverride(unittest.TestCase):
    def test_known_override(self):
        from usdaeco_check.structure import Context
        from usdaeco_core.structure import collection_override
        context = Context(bootstrap.ROOT, [bootstrap.ROOT / "usdAeco"], [])
        collection_override(context)

    def test_unrelated_foreign_property_still_fails(self):
        from usdaeco_check.structure import Context
        from usdaeco_core.structure import collection_override
        context = Context(bootstrap.ROOT, [bootstrap.ROOT / "usdAeco"], [])
        context.schema_data["classes"][0]["properties"].append("foreign:driver")
        with self.assertRaises(ValueError):
            collection_override(context)


if __name__ == "__main__":
    unittest.main()
