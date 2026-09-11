#!/pxrpythonsubst
"""Measure enclosure continuity and reject separated walls or an undersized slab."""
import unittest
import bootstrap
from pxr import Gf, Plug, Usd, UsdGeom
from claims import open_copy

Plug.Registry().RegisterPlugins(str(bootstrap.ROOT / "usdAeco"))
BASE = "/SmallProject/Site/Building/Level1/"


def walls_meet(stage):
    cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), ["default", "proxy", "render"])
    def bounds(name):
        prim = stage.GetPrimAtPath(BASE + name)
        if not prim:
            raise ValueError("missing enclosure prim: " + name)
        return cache.ComputeWorldBound(prim).ComputeAlignedRange()
    names = ["WallNorth", "WallEast", "WallPartition", "WallWest"]
    walls = [bounds(name) for name in names]
    slab = bounds("FloorSlab")
    for i, wall in enumerate(walls):
        overlap = Gf.Range3d.GetIntersection(wall, walls[(i + 1) % 4])
        if overlap.IsEmpty() or any(overlap.GetSize()[axis] < .2 - 1e-6 for axis in (0, 1)):
            raise ValueError("separated corner: " + names[i] + " / " + names[(i + 1) % 4])
        if any(slab.GetMin()[axis] > wall.GetMin()[axis] + 1e-6 or
               slab.GetMax()[axis] < wall.GetMax()[axis] - 1e-6 for axis in (0, 1)):
            raise ValueError("slab does not contain " + names[i])
        if abs(wall.GetSize()[2] - 2.7) > 1e-6 or abs(wall.GetMin()[2] - slab.GetMax()[2]) > 1e-6:
            raise ValueError("wall height or bearing differs from the room dimensions")
    if abs(slab.GetSize()[2] - .2) > 1e-6:
        raise ValueError("floor slab is not 0.2 m thick")
    return "4 corners overlap by 0.2 m; slab contains all 4 wall footprints; walls 2.7 m, slab 0.2 m"


class TestBuilding(unittest.TestCase):
    def stage(self):
        return open_copy(bootstrap.ROOT / "usdAeco/examples/small_building.usda")

    def test_walls_meet(self):
        self.assertIn("4 corners", walls_meet(self.stage()))

    def test_gap_fails(self):
        stage = self.stage()
        UsdGeom.Xformable(stage.GetPrimAtPath(BASE + "WallEast")).AddTranslateOp().Set((.5, 0, 0))
        with self.assertRaisesRegex(ValueError, "separated corner"):
            walls_meet(stage)

    def test_small_slab_fails(self):
        stage = self.stage()
        stage.GetPrimAtPath(BASE + "FloorSlab/Geom").GetAttribute("xformOp:scale").Set((5, 4.6, .2))
        with self.assertRaisesRegex(ValueError, "slab does not contain"):
            walls_meet(stage)
