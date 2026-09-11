"""Bounds-framed isometric views for the published core examples."""
from pxr import Gf, Usd, UsdGeom


def frame_view(stage, layer):
    """Author a stock orthographic view, excluding spatial extent guides."""
    bounds = Gf.Range3d()
    cache = UsdGeom.BBoxCache(Usd.TimeCode.Default(), ["default", "guide", "proxy", "render"])
    for prim in stage.Traverse():
        if prim.IsA(UsdGeom.Gprim) and prim.GetAttribute("aeco:derived:role").Get() != "extent":
            bounds.UnionWith(cache.ComputeWorldBound(prim).ComputeAlignedRange())
    if bounds.IsEmpty():
        raise ValueError("no visible geometry to frame")
    center = bounds.GetMidpoint()
    distance = max(bounds.GetSize().GetLength(), 1) * 3
    view = Gf.Matrix4d().SetLookAt(center + Gf.Vec3d(-1, -1, 1).GetNormalized() * distance,
                                  center, Gf.Vec3d(0, 0, 1))
    projected = Gf.Range3d()
    for i in range(8):
        projected.UnionWith(view.Transform(bounds.GetCorner(i)))
    width = 1.2 * max(projected.GetSize()[0], projected.GetSize()[1] * 1.6)
    with Usd.EditContext(stage, layer):
        camera = UsdGeom.Camera.Define(stage, "/Renders/overview")
        camera.CreateProjectionAttr("orthographic")
        camera.CreateHorizontalApertureAttr(width * 10)
        camera.CreateVerticalApertureAttr(width * 10 / 1.6)
        camera.CreateClippingRangeAttr(Gf.Vec2f(.01, distance * 3))
        camera.AddTransformOp().Set(view.GetInverse())
        for prim in stage.Traverse():
            if prim.IsA(UsdGeom.Gprim) and prim.GetAttribute("aeco:derived:role").Get() == "extent":
                UsdGeom.Imageable(prim).CreateVisibilityAttr().Set("invisible")
    layer.Save()
