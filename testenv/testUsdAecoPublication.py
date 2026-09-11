#!/pxrpythonsubst
"""Publication retains real findings, representation marks and source transforms."""
from pathlib import Path
import shutil
import tempfile
import unittest
import bootstrap
from pxr import Plug, Usd, UsdGeom
from usdaeco_core.example import hook, load_validators

Plug.Registry().RegisterPlugins(str(bootstrap.ROOT / "usdAecoValidators"))


class TestPublication(unittest.TestCase):
    def test_small_building_marks(self):
        load_validators(bootstrap.ROOT)
        stage = Usd.Stage.Open(str(bootstrap.ROOT / "usdAeco/examples/small_building.usda"))
        prims = [p for p in stage.Traverse() if p.IsA(UsdGeom.Gprim)]
        self.assertGreater(len(prims), 30)
        for prim in prims:
            with self.subTest(prim=str(prim.GetPath())):
                self.assertTrue(prim.HasAPI("AecoDerivedGeometryAPI"))
                self.assertEqual(prim.GetAttribute("aeco:derived:approx").Get(),
                                 "tessellated" if prim.IsA(UsdGeom.Mesh) else "exact")
                self.assertGreater(prim.GetAttribute("aeco:derived:tolerance").Get(), 0)

    def test_warning_survives_hook(self):
        load_validators(bootstrap.ROOT)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "usdAeco/examples"
            source.mkdir(parents=True)
            shutil.copyfile(bootstrap.ROOT / "usdAeco/examples/hard_cases.usda", source / "hard_cases.usda")
            out = root / "examples/hard_cases/out"
            out.mkdir(parents=True)
            from pxr import Sdf
            layer = Sdf.Layer.CreateAnonymous()
            layer.subLayerPaths = [str(source / "hard_cases.usda")]
            stage = Usd.Stage.Open(layer)
            base = Usd.Stage.Open(str(source / "hard_cases.usda"))
            for key in ("upAxis", "metersPerUnit", "fallbackPrimTypes"):
                stage.SetMetadata(key, base.GetMetadata(key))
            before = {p.GetPath(): UsdGeom.Xformable(p).ComputeLocalToWorldTransform(Usd.TimeCode.Default())
                      for p in stage.Traverse() if p.IsA(UsdGeom.Xformable)}
            findings = hook(stage, out)
            self.assertEqual([f["name"] for f in findings], ["danglingMember"])
            self.assertEqual(findings[0]["severity"], "warn")
            self.assertEqual(findings[0]["paths"], ["/Metro/Zones/DesignOptionStudy"])
            self.assertTrue(all(UsdGeom.Xformable(stage.GetPrimAtPath(path)).ComputeLocalToWorldTransform(
                Usd.TimeCode.Default()) == transform for path, transform in before.items()))
