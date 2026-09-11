"""Publish core stages and optional, explicitly schematic tree symbols."""
import argparse
import os
from pathlib import Path
import shutil
import sys

from pxr import Gf, Plug, Sdf, Usd, UsdGeom, UsdShade, UsdValidation
from usdaeco_check.validation import run

EXAMPLES = ('small_building', 'early_design', 'hard_cases', 'renovation', 'road', 'service_campus')


def load_validators(root):
    Plug.Registry().RegisterPlugins(str(root / 'usdAeco'))
    Plug.Registry().RegisterPlugins(str(root / 'usdAecoValidators'))
    # Required import: a missing Python plugin must never pass by omission.
    import usdAecoValidators
    registry = UsdValidation.ValidationRegistry()
    metadata = registry.GetValidatorMetadataForKeyword('UsdAecoValidators')
    if len(metadata) != 8 or not all(registry.GetOrLoadValidatorByName(m.name) for m in metadata):
        raise RuntimeError('all 8 core validators must load')


def mark(prim, owner, approx='exact'):
    prim.ApplyAPI('AecoDerivedGeometryAPI')
    values = [('source', owner.GetAttribute('aeco:id').Get(), Sdf.ValueTypeNames.String),
              ('role', 'symbol', Sdf.ValueTypeNames.Token),
              ('approx', approx, Sdf.ValueTypeNames.Token),
              ('stamp', 'core hierarchy symbols 0.9.2', Sdf.ValueTypeNames.String)]
    for name, value, typ in values:
        prim.CreateAttribute('aeco:derived:' + name, typ, custom=False).Set(value)
    if approx == 'exact':
        prim.CreateAttribute('aeco:derived:tolerance', Sdf.ValueTypeNames.Double, custom=False).Set(1e-6)


def label(stage, owner, transform, title, material):
    """Use plain Mesh quads for readable labels; no external font or texture asset."""
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.load_default(size=10)
    image = Image.new('L', (180, 16))
    ImageDraw.Draw(image).text((0, 0), title, font=font, fill=255)
    scale = min(.03, 1.96 / max(font.getlength(title), 1))
    points, indices, counts = [], [], []
    # Coalesce each lit pixel run into one quad to keep the layer small.
    for y in range(image.height):
        x = 0
        while x < image.width:
            if image.getpixel((x, y)) < 100:
                x += 1
                continue
            start = x
            while x < image.width and image.getpixel((x, y)) >= 100:
                x += 1
            left, right = -.98 + start * scale, -.98 + x * scale
            top, bottom = .17 - y * scale, .17 - (y + 1) * scale
            offset = len(points)
            points.extend([(left,bottom,.051),(right,bottom,.051),(right,top,.051),(left,top,.051)])
            indices.extend(range(offset, offset + 4))
            counts.append(4)
    mesh = UsdGeom.Mesh.Define(stage, owner.GetPath().AppendChild('ReviewLabel'))
    mesh.CreatePointsAttr(points)
    mesh.CreateFaceVertexCountsAttr(counts)
    mesh.CreateFaceVertexIndicesAttr(indices)
    mesh.CreateSubdivisionSchemeAttr('none')
    mesh.CreateDoubleSidedAttr(True)
    mesh.CreateDisplayColorAttr([(.015,.022,.028)])
    mesh.CreateExtentAttr(UsdGeom.PointBased(mesh).ComputeExtent(points))
    mesh.AddTransformOp().Set(transform)
    mark(mesh.GetPrim(), owner, 'tessellated')
    UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(material)


def flat_material(stage, name, color):
    material = UsdShade.Material.Define(stage, '/ReviewMaterials/' + name)
    shader = UsdShade.Shader.Define(stage, material.GetPath().AppendChild('Surface'))
    shader.CreateIdAttr('UsdPreviewSurface')
    shader.CreateInput('diffuseColor', Sdf.ValueTypeNames.Color3f).Set((0,0,0))
    shader.CreateInput('emissiveColor', Sdf.ValueTypeNames.Color3f).Set(color)
    shader.CreateInput('useSpecularWorkflow', Sdf.ValueTypeNames.Int).Set(1)
    shader.CreateInput('specularColor', Sdf.ValueTypeNames.Color3f).Set((0,0,0))
    material.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), 'surface')
    return material


def schematic(stage, out):
    """A labelled hierarchy view; never inferred physical placement or dimensions."""
    owners = [p for p in stage.Traverse() if p.IsA(UsdGeom.Xformable)
              and p.GetAttribute('aeco:id').Get() and p.GetTypeName() != 'AecoPort']
    by_path = {p.GetPath(): p for p in owners}
    parents = {}
    for prim in owners:
        parent = prim.GetParent()
        while parent and parent.GetPath() not in by_path:
            parent = parent.GetParent()
        parents[prim.GetPath()] = parent.GetPath() if parent else None
    layer = Sdf.Layer.CreateNew(str(out / 'symbols.usda'))
    layer.documentation = 'Schematic hierarchy symbols only. Sizes and positions are diagram layout, not surveyed geometry.'
    stage.GetRootLayer().subLayerPaths.insert(0, str(layer.realPath))
    cache = UsdGeom.XformCache()
    centers, depths = {}, {}
    with Usd.EditContext(stage, layer):
        colors = {'Site': (.20,.40,.65), 'Part': (.25,.57,.37),
                  'Space': (.22,.65,.67), 'Element': (.85,.57,.20), 'Ink': (.01,.015,.02),
                  'Link': (.35,.40,.45)}
        materials = {name: flat_material(stage, name, color) for name, color in colors.items()}
        for row, owner in enumerate(owners):
            parent = parents[owner.GetPath()]
            depth = depths.get(parent, -1) + 1
            depths[owner.GetPath()] = depth
            center = Gf.Vec3d(depth * 2.5, -row * .75, 0)
            centers[owner.GetPath()] = center
            inverse = cache.GetLocalToWorldTransform(owner).GetInverse()
            transform = Gf.Matrix4d().SetTranslate(center) * inverse
            kind = {'AecoSite': 'Site', 'AecoFacility': 'Site', 'AecoFacilityPart': 'Part',
                    'AecoLevel': 'Part', 'AecoSpace': 'Space'}.get(owner.GetTypeName(), 'Element')
            shape = UsdGeom.Cube.Define(stage, owner.GetPath().AppendChild('ReviewSymbol'))
            shape.CreateSizeAttr(1)
            shape.CreateExtentAttr([(-.5,-.5,-.5),(.5,.5,.5)])
            shape.AddTransformOp().Set(transform)
            shape.AddScaleOp().Set((2.12,.5,.08))
            shape.CreateDisplayColorAttr([colors[kind]])
            mark(shape.GetPrim(), owner)
            UsdShade.MaterialBindingAPI.Apply(shape.GetPrim()).Bind(materials[kind])
            label(stage, owner, transform, owner.GetName(), materials['Ink'])
            if parent is not None:
                parent_center = centers[parent]
                start = parent_center + Gf.Vec3d(1.06,0,0)
                end = center - Gf.Vec3d(1.06,0,0)
                bend = Gf.Vec3d(start[0]+.13,end[1],0)
                points = (start, Gf.Vec3d(bend[0],start[1],0), bend, end)
                for index, (a, b) in enumerate(zip(points, points[1:])):
                    link = UsdGeom.Cube.Define(stage, owner.GetPath().AppendChild('ReviewLink' + str(index)))
                    link.CreateSizeAttr(1)
                    link.CreateExtentAttr([(-.5,-.5,-.5),(.5,.5,.5)])
                    link.AddTransformOp().Set(Gf.Matrix4d().SetTranslate((a+b)/2) * inverse)
                    link.AddScaleOp().Set(tuple(max(abs(b[i]-a[i]), .04) for i in range(3)))
                    link.CreateDisplayColorAttr([colors['Link']])
                    UsdShade.MaterialBindingAPI.Apply(link.GetPrim()).Bind(materials['Link'])
                    mark(link.GetPrim(), owner)
    layer.Save()


def hook(stage, out):
    root = out.parents[2]
    source = root / 'usdAeco/examples' / (out.parent.name + '.usda')
    # Archive the example's own authored source as well as its generated symbols.
    shutil.copyfile(source, out / 'authored.usda')
    if not any(p.IsA(UsdGeom.Gprim) for p in stage.Traverse()):
        schematic(stage, out)
    # USD 26.8 exposes site.GetPrim/GetProperty, not site.GetPath.
    # Execute all registered rules here and serialize their real sites.
    findings = []
    for error in run(stage, ['UsdAecoValidators']):
        paths = []
        for site in error.GetSites():
            target = site.GetProperty() if site.IsProperty() else site.GetPrim()
            if not target:
                raise ValueError('validator returned an unresolved finding site')
            paths.append(str(target.GetPath()))
        findings.append({'name': error.GetName(), 'message': error.GetMessage(),
                         'severity': str(error.GetType()).split('.')[-1].lower(), 'paths': paths})
    return findings


def prepare(example_dir):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    example = Path(example_dir).resolve()
    root = example.parents[1]
    if example.name not in EXAMPLES:
        raise ValueError('unknown core example')
    if os.environ.get('AECO_DATACENTRE_ROOT') or os.environ.get('AECO_DATACENTRE_STAGE'):
        raise ValueError('core examples require their own minimal source; unset external source overrides')
    os.environ['PATH'] = str(Path(sys.executable).parent) + os.pathsep + os.environ.get('PATH', '')
    load_validators(root)
    # The hook runs the registry itself to support this USD Python site API.
    return example, dict(hook=hook, minimal=root / 'usdAeco/examples' / (example.name + '.usda'),
                         publish=args.publish, keywords=[])
