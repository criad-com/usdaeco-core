"""Fresh-process B7 probe: deliberately imports no family package."""
import json
import sys
from pxr import Plug, Sdf, Usd, UsdGeom


def probe(filename):
    stage = Usd.Stage.Open(filename)
    assert stage and not stage.GetCompositionErrors()
    assert not [p for p in Plug.Registry().GetAllPlugins() if p.name.startswith("usdAeco")]
    assert "BrepArray" not in (stage.GetMetadata("fallbackPrimTypes") or {})
    elements = [p for p in stage.Traverse() if "AecoElementAPI" in (p.GetMetadata("apiSchemas").GetAppliedItems() if p.GetMetadata("apiSchemas") else [])]
    twins = 0
    for element in elements:
        exact = [p for p in element.GetChildren() if p.GetTypeName() == "BrepArray"]
        assert exact
        meshes = [p for p in element.GetChildren() if p.IsA(UsdGeom.Mesh)]
        for body in exact:
            assert body.GetPrimTypeInfo().GetSchemaType().isUnknown
            linked = [m for m in meshes if body.GetPath() in m.GetRelationship("aeco:derived:from").GetTargets()]
            assert linked, "Exact representation has no linked Mesh twin"
            mesh = UsdGeom.Mesh(linked[0])
            assert mesh.GetPointsAttr().Get() and mesh.GetFaceVertexIndicesAttr().Get()
            assert sum(mesh.GetFaceVertexCountsAttr().Get()) == len(mesh.GetFaceVertexIndicesAttr().Get())
            assert mesh.ComputePurpose() in ("default", "proxy", "render")
            assert mesh.ComputeVisibility() == "inherited"
            assert body.GetRelationship("proxyPrim").GetTargets() == [mesh.GetPath()]
            bounds = UsdGeom.BBoxCache(Usd.TimeCode.Default(), ["default", "proxy", "render"]).ComputeWorldBound(element).ComputeAlignedRange()
            assert not bounds.IsEmpty()
            twins += 1
    assert elements
    return {"elements": len(elements), "mesh_twins": twins, "plugins": 0}


if __name__ == "__main__":
    print(json.dumps(probe(sys.argv[1]), sort_keys=True))
