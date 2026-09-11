"""Core design claims ported from the v0.8 check script."""
import os
import subprocess
import sys
import textwrap
from pathlib import Path
import usdaeco_tools
from usdaeco_tools import validators, registry
from pxr import Usd, UsdGeom, Sdf, Tf, Plug
EXAMPLES = str(Path(__file__).resolve().parents[1] / "usdAeco/examples")

TYPED = ["AecoSite", "AecoFacility", "AecoFacilityPart", "AecoLevel",
         "AecoSpace", "AecoSystem", "AecoZone", "AecoPort"]
APIS = ["AecoProjectAPI", "AecoElementAPI", "AecoClassificationAPI",
        "AecoTypeAPI", "AecoDerivedGeometryAPI"]
ABSTRACT = ["AecoSpatialBase", "AecoGroupBase"]


def open_copy(path):
    source = Sdf.Layer.FindOrOpen(str(path))
    layer = Sdf.Layer.CreateAnonymous(Path(path).name)
    layer.TransferContent(source)
    return Usd.Stage.Open(layer)


def can(prim, api):
    answer = prim.CanApplyAPI(api)
    return answer[0] if isinstance(answer, tuple) else bool(answer)


def run_claims(report):
    check = report.check
    # 1. Registry: the whole core resolves, and the plugin carries no code ------
    sr = Usd.SchemaRegistry()
    missing = [t for t in TYPED if sr.FindConcretePrimDefinition(t) is None]
    missing += [a for a in APIS if sr.FindAppliedAPIPrimDefinition(a) is None]
    check("the core resolves: %d concrete types, %d applied schemas, nothing else"
          % (len(TYPED), len(APIS)), not missing,
          "missing: %s" % missing if missing else "")
    codeful = [p.name for p in Plug.Registry().GetAllPlugins()
               if p.name.startswith("usdAeco") and p.name == "usdAeco" and not p.isResource]
    check("plugin is codeless (no compiled library) [E9]", not codeful,
          "codeful: %s" % codeful if codeful else "")
    from usdaeco_check.plugins import read_json
    descriptor = Path(EXAMPLES).parent / "plugInfo.json"
    types = read_json(descriptor)["Plugins"][0]["Info"]["Types"]
    expected = {"Usd" + name for name in TYPED + ABSTRACT + APIS}
    check("core registry is exactly 8 concrete / 2 abstract / 5 applied schemas",
          set(types) == expected, f"{len(types)} registered classes")
    abstract_ok = all(not Tf.Type.FindByName(n).isUnknown for n in
                      ("UsdAecoSpatialBase", "UsdAecoGroupBase"))
    check("abstract bases known to the type system (IsA queries) [B1/B4]",
          abstract_ok)

    # 2. The extension contract is mechanical where USD allows it ----------------
    s = Usd.Stage.CreateInMemory()
    xf = s.DefinePrim("/Xf", "Xform")
    mesh = s.DefinePrim("/Mesh", "Mesh")
    sysp = s.DefinePrim("/Sys", "AecoSystem")
    zone = s.DefinePrim("/Zone", "AecoZone")
    contract = [
        (can(xf, "AecoElementAPI"), "element API accepted on an Xform"),
        (can(mesh, "AecoElementAPI"), "element API accepted on a Mesh"),
        (not can(sysp, "AecoElementAPI"), "element API refused on AecoSystem (not Imageable)"),
        (not can(zone, "AecoElementAPI"), "element API refused on AecoZone"),
        (zone.HasAPI(Usd.CollectionAPI, "members"), "members collection built into AecoZone"),
        (sysp.HasAPI(Usd.CollectionAPI, "members"), "members collection built into AecoSystem"),
        (Usd.CollectionAPI(zone, "members").GetExpansionRuleAttr().Get() == "explicitOnly",
         "members expansionRule falls back to explicitOnly"),
        (not sysp.GetAttribute("aeco:status") and not sysp.GetAttribute("aeco:title"),
         "a core group carries no register row"),
        (sysp.GetRelationship("aeco:serves") and not zone.GetRelationship("aeco:serves"),
         "aeco:serves exists on systems only"),
    ]
    bad = [d for ok, d in contract if not ok]
    check("CanApplyAPI restrictions and built-ins hold [E1/E5]", not bad, "; ".join(bad))

    # 3. Every example validates with zero errors and complete fallbacks --------
    for name in sorted(os.listdir(EXAMPLES)):
        if not name.endswith(".usda") or name == "minimal.usda":
            continue
        stage = Usd.Stage.Open(os.path.join(EXAMPLES, name))
        errs, warns = validators.split(validators.validate_stage(stage))
        authored = dict(stage.GetMetadata("fallbackPrimTypes") or {})
        used = {str(p.GetTypeName()) for p in stage.Traverse()
                if str(p.GetTypeName()).startswith("Aeco")}
        fb_ok = all(t in authored for t in used)
        check("examples/%s: 0 errors, fallbackPrimTypes complete" % name,
              not errs and fb_ok,
              ("%d warning(s)" % len(warns))
              + ("" if fb_ok else "; fallbacks missing for %s" % sorted(used - set(authored)))
              + "".join("; ERROR %s: %s" % (e.GetName(), e.GetMessage()) for e in errs))

    # 4. Seeded defects are caught ------------------------------------------------
    stage = open_copy(os.path.join(EXAMPLES, "small_building.usda"))
    bld = stage.GetPrimAtPath("/SmallProject/Site/Building")
    stage.DefinePrim(bld.GetPath().AppendChild("Annex"), "AecoFacility")   # facility in facility
    wall = stage.GetPrimAtPath("/SmallProject/Site/Building/Level1/WallNorth")
    stage.DefinePrim(wall.GetPath().AppendChild("Closet"), "AecoSpace")    # space inside a wall
    port = stage.GetPrimAtPath("/SmallProject/Site/Building/Level1/CWEntry/Out")
    port.GetAttribute("aeco:medium").Set("cable")                          # pipe-to-cable
    door = stage.GetPrimAtPath("/SmallProject/Site/Building/Level1/DoorMain")
    door.GetAttribute("aeco:id").Set(wall.GetAttribute("aeco:id").Get())  # duplicate id
    stage.GetPrimAtPath("/SmallProject/Site/Building/Level2").ApplyAPI("AecoElementAPI")  # a level that is an element
    blob = stage.DefinePrim("/SmallProject/Site/Building/Level1/Blob", "Xform")
    blob.ApplyAPI("AecoElementAPI")                                        # element with no kind
    blob.GetAttribute("aeco:id").Set("0f0f0f0f-0f0f-5f0f-8f0f-0f0f0f0f0f0f")
    zone = stage.DefinePrim("/SmallProject/Zone", "AecoZone")
    zone.CreateRelationship("aeco:serves").AddTarget(bld.GetPath())        # a zone that serves
    errs, warns = validators.split(validators.validate_stage(stage, include_builtin=False))
    names = sorted({e.GetName() for e in errs} | {w.GetName() for w in warns})
    expected = ["duplicateId", "facilityInFacility", "mediumMismatch",
                "spatialInsideElement", "spatialIsElement", "unclassifiedElement",
                "zoneAuthorsServes"]
    check("seeded defects caught (%s)" % ", ".join(expected),
          all(n in names for n in expected), "raised: %s" % names)

    # 5. Type/occurrence rides `inherits` [B5] ------------------------------------
    stage = open_copy(os.path.join(EXAMPLES, "small_building.usda"))
    wall = stage.GetPrimAtPath("/SmallProject/Site/Building/Level1/WallNorth")
    code = wall.GetAttribute("aeco:class:uniclass:code")
    model = wall.GetAttribute("aeco:type:model")
    inherited = (code.Get() == "Ss_25_10_20" and wall.HasAPI("AecoClassificationAPI", "uniclass")
                 and (model.Get() or "").startswith("Cavity wall"))
    typ = stage.GetPrimAtPath("/_TypeCatalog/ExternalCavityWall")
    typ.GetAttribute("aeco:class:uniclass:code").Set("Ss_25_10_25")        # edit the type
    broadcast = code.Get() == "Ss_25_10_25"
    code.Set("Ss_25_10_30")                                                # occurrence override
    override = code.Get() == "Ss_25_10_30"
    catalog = [p.GetName() for p in usdaeco_tools.iter_catalog_types(stage)]
    check("type/occurrence: type values compose in, type edits broadcast, "
          "occurrence overrides win; catalog = class prims only [B5]",
          inherited and broadcast and override and catalog == ["ExternalCavityWall"],
          "catalog: %s" % catalog)

    # 6. Spatial queries: one IsA over the abstract base; levels are parts [B1] ---
    stage = Usd.Stage.Open(os.path.join(EXAMPLES, "hard_cases.usda"))
    spatial = list(usdaeco_tools.iter_spatial(stage))
    levels = [p for p in spatial if p.IsA(Tf.Type.FindByName("UsdAecoFacilityPart"))
              and p.GetTypeName() == "AecoLevel"]
    mezz = stage.GetPrimAtPath(
        "/Metro/Campus/ParcelNorth/Development/Parts/Podium/L0/Mezzanine")
    door = stage.GetPrimAtPath(
        "/Metro/Campus/ParcelNorth/Development/Parts/TowerA/A_L1/CurtainWallEast/PassDoor")
    check("hard cases: %d spatial prims by one IsA; level>level (mezzanine) legal; "
          "nested element's container seen through the wall [B1]" % len(spatial),
          len(levels) >= 5 and usdaeco_tools.spatial_type_of(mezz) == "part"
          and usdaeco_tools.container_of(door).GetName() == "A_L1")

    # 7. Groups: one IsA, membership resolves, serves is a system fact [B4] -------
    groups = list(usdaeco_tools.iter_groups(stage))
    fc1 = stage.GetPrimAtPath("/Metro/Zones/FireCompartmentFC1")
    members = [p.GetName() for p in usdaeco_tools.group_members(fc1)]
    lobby = stage.GetPrimAtPath("/Metro/Campus/ParcelNorth/Development/Parts/Podium/L0/Lobby")
    of = [g.GetName() for g in usdaeco_tools.groups_of(stage, lobby)]
    check("groups: %d by one IsA; zone members resolve (%s); reverse lookup "
          "finds the zone from the space [B4]" % (len(groups), ", ".join(members)),
          len(groups) == 3 and members == ["Lobby", "Bathroom"] and of == ["FireCompartmentFC1"])

    # 8. Restructure drill: rename a space, overlay targets dangle, repath by id --
    stage = open_copy(os.path.join(EXAMPLES, "small_building.usda"))
    before = usdaeco_tools.snapshot_ids(stage)
    layer = stage.GetRootLayer()
    edit = Sdf.BatchNamespaceEdit()
    old = Sdf.Path("/SmallProject/Site/Building/Level2/Bathroom")
    edit.Add(Sdf.NamespaceEdit.Rename(old, "WC"))
    layer.Apply(edit)
    dangling = usdaeco_tools.dangling_targets(stage)
    repaired, unresolved = usdaeco_tools.repath(stage, before)
    after = usdaeco_tools.dangling_targets(stage)
    check("restructure drill: %d targets dangled after a rename, repath repaired %d "
          "by aeco:id, %d unresolved, %d still dangling [R6]"
          % (len(dangling), repaired, unresolved, len(after)),
          len(dangling) >= 3 and unresolved == 0 and not after)

    # 9. Vanilla degradation: no plugins, same transforms, data legible [B7] -----
    probe = r'''
    import sys
    from pxr import Usd, UsdGeom
    st = Usd.Stage.Open(sys.argv[1])
    p = st.GetPrimAtPath("/SmallProject/Site/Building/Level2")
    print(p.GetTypeName(), p.GetPrimTypeInfo().GetSchemaTypeName(),
          UsdGeom.Xformable(p).ComputeLocalToWorldTransform(Usd.TimeCode.Default())[3][2],
          p.GetAttribute("aeco:elevation").Get(),
          st.GetPrimAtPath("/SmallProject/Site/Building/Level1/WallNorth").GetAttribute("aeco:id").Get(),
          st.GetPrimAtPath("/SmallProject/Systems/DomesticColdWater").GetPrimTypeInfo().GetSchemaTypeName())
    '''
    env = {k: v for k, v in os.environ.items() if k not in ("PXR_PLUGINPATH_NAME",)}
    out = subprocess.run([sys.executable, "-c", textwrap.dedent(probe),
                          os.path.join(EXAMPLES, "small_building.usda")],
                         capture_output=True, text=True, env=env)
    tokens = out.stdout.split()
    stage = Usd.Stage.Open(os.path.join(EXAMPLES, "small_building.usda"))
    here_z = UsdGeom.Xformable(stage.GetPrimAtPath(
        "/SmallProject/Site/Building/Level2")).ComputeLocalToWorldTransform(
            Usd.TimeCode.Default())[3][2]
    vanilla_ok = (len(tokens) == 6 and tokens[0] == "AecoLevel"
                  and tokens[1] == "Xform" and abs(float(tokens[2]) - here_z) < 1e-9
                  and tokens[3] == "3.2" and tokens[4] == "e1337f59-b0e2-5dd0-8474-c578c5b0afbd"
                  and tokens[5] == "Scope")
    check("vanilla USD (no plugins): AecoLevel falls back to Xform, AecoSystem to "
          "Scope, world transform identical, authored data legible [B7]", vanilla_ok,
          out.stdout.strip() + out.stderr.strip()[-200:])

    # 10. Zero-geometry stage is conformant ---------------------------------------
    stage = Usd.Stage.Open(os.path.join(EXAMPLES, "early_design.usda"))
    gprims = [p for p in stage.Traverse() if p.IsA(UsdGeom.Gprim)]
    errs, _ = validators.split(validators.validate_stage(stage))
    check("zero-geometry early-design stage: %d gprims, conformant" % len(gprims),
          not gprims and not errs)

    # 11. Kind is classification: census and health metric [D4/E4] ---------------
    stage = Usd.Stage.Open(os.path.join(EXAMPLES, "small_building.usda"))
    unclassified, proxy, systems, total = registry.classification_health(stage)
    census = registry.classification_census(stage)
    walls = [p.GetName() for p in usdaeco_tools.classified_as(stage, "IfcWall")]
    check("classification: %d elements, %d unclassified, %d proxy, systems %s; "
          "'IfcWall' query finds %s [D4/E4]"
          % (total, unclassified, proxy, sorted(systems), walls),
          total == 16 and unclassified == 0 and proxy == 0
          and systems == {"ifc", "uniclass"} and sorted(walls) ==
          ["WallEast", "WallLeft", "WallNorth", "WallPartition", "WallRight", "WallWest"],
          str(census))

    # 12. Port graph trace [D7] --------------------------------------------------
    start = stage.GetPrimAtPath("/SmallProject/Site/Building/Level2/Bathroom/Basin/In")
    chain = [p.GetName() for p in usdaeco_tools.trace_flow(start)]
    check("port graph traced basin -> mains: %s [D7]" % " -> ".join(chain),
          chain[0] == "Basin" and chain[-1] == "CWEntry")

    # 13. Grouping never moves geometry: mute the groups, transforms identical ----
    root = Sdf.Layer.CreateAnonymous("groups-drill")
    base = Sdf.Layer.FindOrOpen(os.path.join(EXAMPLES, "small_building.usda"))
    root.subLayerPaths.append(base.identifier)
    stage = Usd.Stage.Open(root)
    elems = list(usdaeco_tools.iter_elements(stage))
    xf_before = {p.GetPath(): UsdGeom.Xformable(p).ComputeLocalToWorldTransform(
        Usd.TimeCode.Default()) for p in elems}
    over = Sdf.Layer.CreateAnonymous("more-groups")
    root.subLayerPaths.insert(0, over.identifier)
    stage.SetEditTarget(Usd.EditTarget(over))
    z = stage.DefinePrim("/SmallProject/Zones/Wet", "AecoZone")
    Usd.CollectionAPI(z, "members").GetIncludesRel().AddTarget(
        "/SmallProject/Site/Building/Level2/Bathroom")
    same_with = all(UsdGeom.Xformable(p).ComputeLocalToWorldTransform(
        Usd.TimeCode.Default()) == xf_before[p.GetPath()] for p in elems)
    stage.MuteLayer(over.identifier)
    same_muted = (all(UsdGeom.Xformable(p).ComputeLocalToWorldTransform(
        Usd.TimeCode.Default()) == xf_before[p.GetPath()] for p in elems)
        and not stage.GetPrimAtPath("/SmallProject/Zones/Wet"))
    check("grouping never moves geometry: a zone layer added then muted, every "
          "element's world transform unchanged [B4/E11]", same_with and same_muted)
