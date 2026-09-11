"""usdaeco_tools — OPTIONAL codeful companion to the codeless usdAeco core.

The schema itself is a pure data contract: any vanilla USD runtime
resolves it from plugInfo.json + generatedSchema.usda with no compiled
code. Everything BEHAVIORAL lives here instead — plugin registration
convenience, graph queries, the id-based restructure repair (repath), and
UsdValidation validators — mirroring how UsdShade/UsdPhysics keep
renderers and simulators outside the schema.

Nothing in this package is required to read, write, render, or exchange
usdAeco stages. It is required only if you want the extra services.

Layout assumed (repository root = two directories above this file):
    usdAeco/                    the flat codeless schema module
    registries/*.json            governed token vocabularies
"""
import os
from pxr import Plug, Usd, Sdf, Tf

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

AECO_LIBS = ("usdAeco",)

# Schema identifier tokens (string-based on purpose: codeless schemas have
# no generated C++/Python classes, so the generic Usd API is the API).
ELEMENT_API = "AecoElementAPI"
CLASSIFICATION_API = "AecoClassificationAPI"
TYPE_API = "AecoTypeAPI"
DERIVED_GEOMETRY_API = "AecoDerivedGeometryAPI" # v0.7: the mark on derived gprims
PORT_TYPE = "AecoPort"
SYSTEM_TYPE = "AecoSystem"
ZONE_TYPE = "AecoZone"
SPATIAL_BASE_TYPE = "UsdAecoSpatialBase"       # abstract spatial root
FACILITY_PART_TYPE = "UsdAecoFacilityPart"     # parts incl. levels (IsA)
GROUP_BASE_TYPE = "UsdAecoGroupBase"           # abstract group root

# The spatial type of a spatial prim is its TYPE (closed set of five);
# spatial KIND is classification, exactly like element kind.
_SPATIAL_TYPE_BY_NAME = {"AecoSite": "site", "AecoFacility": "facility",
                         "AecoFacilityPart": "part", "AecoLevel": "part",
                         "AecoSpace": "space"}


def register_plugins(plugin_root=None):
    """Register core from a source checkout or an explicit plugin directory."""
    from pathlib import Path
    from usdaeco_check.plugins import discover
    paths = [plugin_root or os.environ.get("CORE_PLUGIN_DIR") or Path(ROOT) / "usdAeco"]
    plugins = discover(paths)
    return [plugin for descriptor in dict.fromkeys(p.descriptor for p in plugins.values())
            for plugin in Plug.Registry().RegisterPlugins(str(descriptor))]


def _isa(prim, type_name):
    t = Tf.Type.FindByName(type_name)
    return (not t.isUnknown) and prim.IsA(t)


# ---------------------------------------------------------------------------
# Queries (examples of behavior that must NOT live in the schema)
# ---------------------------------------------------------------------------

def iter_elements(stage):
    """Yield every prim carrying AecoElementAPI."""
    for prim in stage.Traverse():
        if prim.HasAPI(ELEMENT_API):
            yield prim


def find_by_id(stage, aeco_id):
    """Look up any identified prim (element, spatial prim, group, port)
    by its stable aeco:id — the interchange join key."""
    for prim in stage.Traverse():
        attr = prim.GetAttribute("aeco:id")
        if attr and attr.Get() == aeco_id:
            return prim
    return None


def classifications(prim):
    """Return {system: {code, name, uri}} for all AecoClassificationAPI
    instances on the prim."""
    out = {}
    for instance in prim.GetAppliedSchemas():
        if instance.startswith(CLASSIFICATION_API + ":"):
            name = instance.split(":", 1)[1]
            out[name] = {
                key: (prim.GetAttribute("aeco:class:%s:%s" % (name, key)).Get() or "")
                for key in ("code", "name", "uri")
            }
    return out


def classified_as(stage, code, system="ifc", prefix=True):
    """Yield elements whose classification code in `system` equals
    `code`, or starts with it when prefix=True (so 'IfcWall' also
    matches 'IfcWall.PARTITIONING') — the census query the core offers
    instead of a category token."""
    for prim in iter_elements(stage):
        attr = prim.GetAttribute("aeco:class:%s:code" % system)
        value = (attr.Get() if attr else None) or ""
        if value == code or (prefix and value.startswith(code + ".")):
            yield prim


def is_spatial(prim):
    """True if prim is any spatial container — one IsA test via the
    abstract base, whatever concrete spatial type it is."""
    return _isa(prim, SPATIAL_BASE_TYPE)


def is_group(prim):
    """True if prim is an AecoSystem or AecoZone (one IsA via the base)."""
    return _isa(prim, GROUP_BASE_TYPE)


def spatial_type_of(prim):
    """'site' | 'facility' | 'part' | 'space' for a spatial prim (levels
    report 'part' — AecoLevel IS an AecoFacilityPart), else None."""
    return _SPATIAL_TYPE_BY_NAME.get(str(prim.GetTypeName())) if is_spatial(prim) else None


def iter_spatial(stage, type_name=None):
    """Yield spatial prims, optionally filtered by exact type name."""
    for prim in stage.Traverse():
        if is_spatial(prim) and (type_name is None
                                 or str(prim.GetTypeName()) == type_name):
            yield prim


def iter_groups(stage, type_name=None):
    """Yield group prims (systems and zones), optionally by type name."""
    for prim in stage.Traverse():
        if is_group(prim) and (type_name is None
                               or str(prim.GetTypeName()) == type_name):
            yield prim


def iter_catalog_types(stage):
    """Yield the catalog: CLASS prims carrying AecoTypeAPI. Occurrences
    compose the API through their inherits arc, so HasAPI alone would
    also return every occurrence — the abstract test is what makes this
    the catalog."""
    for prim in stage.TraverseAll():
        if prim.IsAbstract() and prim.HasAPI(TYPE_API):
            yield prim


def container_of(prim):
    """The spatial container of a prim = its NEAREST spatial ancestor —
    the one containment answer the core defines. Organizational Scopes
    and Xforms interleave invisibly; element subtrees are seen through
    (a door nested in a curtain wall is contained by the wall's space)."""
    parent = prim.GetParent()
    while parent and parent.GetPath() != Sdf.Path.absoluteRootPath:
        if is_spatial(parent):
            return parent
        parent = parent.GetParent()
    return None


def elements_in_container(stage, container_prim):
    """(contained, referencing): elements namespace-contained in the
    container, plus elements elsewhere that reference it through
    aeco:referencedContainers (risers, skybridges, culverts...)."""
    contained = [p for p in Usd.PrimRange(container_prim)
                 if p.HasAPI(ELEMENT_API)]
    referencing = []
    for prim in iter_elements(stage):
        rel = prim.GetRelationship("aeco:referencedContainers")
        if rel and container_prim.GetPath() in rel.GetTargets():
            referencing.append(prim)
    return contained, referencing


def group_members(group_prim):
    """Resolve the members collection of a group (system or zone) —
    handles explicit and pattern-based collections."""
    query = Usd.CollectionAPI(group_prim, "members").ComputeMembershipQuery()
    return [p for p in group_prim.GetStage().Traverse()
            if query.IsPathIncluded(p.GetPath())]


def groups_of(stage, prim):
    """The groups whose members collection includes this prim."""
    return [g for g in iter_groups(stage)
            if Usd.CollectionAPI(g, "members").ComputeMembershipQuery()
            .IsPathIncluded(prim.GetPath())]


def connected_ports(port_prim):
    """Ports targeted by this port's aeco:connectedPorts relationship."""
    rel = port_prim.GetRelationship("aeco:connectedPorts")
    if not rel:
        return []
    stage = port_prim.GetStage()
    return [stage.GetPrimAtPath(t) for t in rel.GetTargets()]


def element_of_port(port_prim):
    """The element a port belongs to (nearest ancestor with AecoElementAPI)."""
    prim = port_prim.GetParent()
    while prim and prim.GetPath() != Sdf.Path.absoluteRootPath:
        if prim.HasAPI(ELEMENT_API):
            return prim
        prim = prim.GetParent()
    return None


def trace_flow(start_port):
    """Walk the port graph from start_port, returning the ordered list of
    element prims visited — exactly the kind of computed service that
    belongs in a codeful companion, not in the data schema."""
    visited, chain = set(), []
    frontier = [start_port]
    while frontier:
        port = frontier.pop(0)
        if port.GetPath() in visited:
            continue
        visited.add(port.GetPath())
        elem = element_of_port(port)
        if elem and (not chain or chain[-1] != elem):
            chain.append(elem)
        for peer in connected_ports(port):          # cross to other elements
            if peer and peer.GetPath() not in visited:
                frontier.append(peer)
        if elem:                                     # flow passes through
            for child in Usd.PrimRange(elem):
                if (child.GetTypeName() == PORT_TYPE
                        and child.GetPath() not in visited
                        and child.GetPath() != port.GetPath()):
                    frontier.append(child)
    return chain


# ---------------------------------------------------------------------------
# repath — the id-based repair for restructure fragility (risk R6)
# ---------------------------------------------------------------------------

# Every relationship the core defines whose targets can dangle after a
# spatial-structure restructure. Downstream libraries extend this tuple
# (usdaeco_tools.AECO_RELS += (...)) for their own relationships.
AECO_RELS = ("aeco:connectedPorts", "aeco:referencedContainers",
             "aeco:serves", "collection:members:includes",
             "collection:members:excludes")


def snapshot_ids(stage):
    """{path: aeco:id} for every identified prim — taken against a
    published spatial structure, this is the input repath needs."""
    out = {}
    for prim in stage.Traverse():
        attr = prim.GetAttribute("aeco:id")
        value = attr.Get() if attr else None
        if value:
            out[str(prim.GetPath())] = value
    return out


def repath(stage, old_index, rels=None):
    """Re-anchor dangling relationship targets by aeco:id after a tree
    restructure. old_index = snapshot_ids() taken BEFORE the restructure.

    Dangling targets are resolved by longest-prefix match against the old
    index (so ports and nested prims under a moved or renamed element
    remap with it), then retargeted to the id's current path. Repairs are
    authored at the stage's current edit target, so a coordination layer
    can repair a stale discipline layer without touching it.
    Returns (repaired, unresolved) counts."""
    rels = rels or AECO_RELS
    new_by_id = {}
    for prim in stage.Traverse():
        attr = prim.GetAttribute("aeco:id")
        value = attr.Get() if attr else None
        if value:
            new_by_id[value] = prim.GetPath()

    def resolve(dangling):
        s = str(dangling)
        best = None
        for old_path in old_index:
            if ((s == old_path or s.startswith(old_path + "/"))
                    and (best is None or len(old_path) > len(best))):
                best = old_path
        if best is None:
            return None
        new_root = new_by_id.get(old_index[best])
        if new_root is None:
            return None
        return Sdf.Path(str(new_root) + s[len(best):])

    repaired, unresolved = 0, 0
    for prim in stage.Traverse():
        for rel_name in rels:
            rel = prim.GetRelationship(rel_name)
            if not rel:
                continue
            changed, out = False, []
            for t in rel.GetTargets():
                if stage.GetPrimAtPath(t.GetPrimPath()):
                    out.append(t)
                    continue
                fixed = resolve(t)
                if fixed and stage.GetPrimAtPath(fixed.GetPrimPath()):
                    out.append(fixed)
                    repaired += 1
                    changed = True
                else:
                    out.append(t)
                    unresolved += 1
            if changed:
                rel.SetTargets(out)
    return repaired, unresolved


def dangling_targets(stage, rels=None):
    """[(prim path, rel name, target)] for every aeco relationship target
    that does not resolve — the restructure-damage report."""
    rels = rels or AECO_RELS
    out = []
    for prim in stage.Traverse():
        for rel_name in rels:
            rel = prim.GetRelationship(rel_name)
            if not rel:
                continue
            for t in rel.GetTargets():
                if not stage.GetPrimAtPath(t.GetPrimPath()):
                    out.append((prim.GetPath(), rel_name, t))
    return out


# --- Derived geometry ------------------------------------

def is_derived(prop):
    """True when a property is DERIVED (E13): its schema definition carries
    the `aecoDerived` metadatum the core plugin registers. Drivers are
    everything else. Works on Usd.Property objects."""
    try:
        return bool(prop.GetMetadata("aecoDerived"))
    except Exception:
        return False


def derived_gprims(prim):
    """{role: [child prims]} for the gprims under `prim` that carry
    AecoDerivedGeometryAPI (body, proxy, axis, footprint, symbol)."""
    out = {}
    for child in prim.GetChildren():
        if DERIVED_GEOMETRY_API in [a.split(":")[0]
                                    for a in child.GetAppliedSchemas()]:
            role = child.GetAttribute("aeco:derived:role").Get() or "body"
            out.setdefault(role, []).append(child)
    return out
