"""usdAeco core validators for OpenUSD's UsdValidation framework.

The executable counterpart of IFC-world Information Delivery
Specifications: machine-checkable rules registered with USD's own
validation framework, running alongside the built-in UsdCoreValidators.
They live in the codeful companion so the data schema stays codeless.
Core rules issue WARNINGS where sector context could legitimately differ;
validation PROFILES (per exchange/jurisdiction) may harden them to errors
(docs/03-design-model.md, D12).

Validators (keyword 'UsdAecoValidators'; legacy error names retained):
  usdAecoValidators:IdentityChecker         elements: unique well-formed aeco:id
                                 (error); spatial/group/port prims: id
                                 present (warn)
  usdAecoValidators:SpatialGrammarChecker   the five-type containment grammar
                                 (recursion legal; facility-in-facility and
                                 other violations are ERRORS); a spatial
                                 prim or port wearing AecoElementAPI
                                 (error); level elevation vs placement
                                 drift; spatial prims inside element
                                 subtrees
  usdAecoValidators:ClassificationChecker   the kind mechanism, measured: elements
                                 with no classification code (warn),
                                 proxy-classified elements (warn),
                                 instance names outside the registry
                                 (warn), empty codes (warn)
  usdAecoValidators:PortConnectivityChecker symmetry + flow + MEDIUM compatibility
  usdAecoValidators:GroupChecker            zones never author aeco:serves (a system
                                 fact); aeco:serves targets spatial prims
                                 or zones; dangling members (warn)
"""
import re
from pxr import Usd, UsdGeom, UsdValidation, Sdf, Tf, Gf

from . import registry

_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")

KEYWORD = "UsdAecoValidators"

# The five-type containment grammar: spatial type -> allowed spatial types
# of the NEAREST spatial ancestor (None = a legal root). Recursion at
# every spatial type is deliberate: site>site (campus/parcel), part>part
# (wing>storey, section>segment; AecoLevel IS a part, so level>level
# covers mezzanines), space>space (open plan>work zone).
# facility>facility is the one recursion REFUSED: composite developments
# are one facility with parts.
_PARENT_RULES = {
    "site": (None, "site"),
    "facility": (None, "site"),
    "part": ("facility", "part"),
    "space": ("site", "facility", "part", "space"),
}
_SPATIAL_TYPE_BY_NAME = {"AecoSite": "site", "AecoFacility": "facility",
                         "AecoFacilityPart": "part", "AecoLevel": "part",
                         "AecoSpace": "space"}
_FLOW_OK = {("source", "sink"), ("sink", "source"),
            ("bidirectional", "source"), ("bidirectional", "sink"),
            ("source", "bidirectional"), ("sink", "bidirectional"),
            ("bidirectional", "bidirectional")}
_MEDIA_WILD = {"other", "undefined"}


def _err(name, stage, path, msg,
         etype=UsdValidation.ValidationErrorType.Error):
    site = UsdValidation.ValidationErrorSite(stage, path)
    return UsdValidation.ValidationError(name, etype, [site], msg)


def _warn(name, stage, path, msg):
    return _err(name, stage, path, msg, UsdValidation.ValidationErrorType.Warn)


def _isa(prim, type_name):
    t = Tf.Type.FindByName(type_name)
    return (not t.isUnknown) and prim.IsA(t)


def _is_spatial(prim):
    return _isa(prim, "UsdAecoSpatialBase")


def _is_group(prim):
    return _isa(prim, "UsdAecoGroupBase")


def _spatial_type(prim):
    if not _is_spatial(prim):
        return None
    return _SPATIAL_TYPE_BY_NAME.get(str(prim.GetTypeName()))


# --- identity ---------------------------------------------------------------

def _validate_identity(stage, timeRange):
    errors, seen = [], {}
    for prim in stage.Traverse():
        is_elem = prim.HasAPI("AecoElementAPI")
        is_addr = (is_elem or _is_spatial(prim) or _is_group(prim)
                   or prim.GetTypeName() == "AecoPort")
        if not is_addr:
            continue
        attr = prim.GetAttribute("aeco:id")
        value = (attr.Get() if attr else None) or ""
        if not value:
            if is_elem:
                errors.append(_err("missingId", stage, prim.GetPath(),
                                   "Element %s has no aeco:id." % prim.GetPath()))
            else:
                errors.append(_warn("missingId", stage, prim.GetPath(),
                                    "%s (%s) has no aeco:id; spatial/group/"
                                    "port prims should be addressable."
                                    % (prim.GetPath(), prim.GetTypeName())))
            continue
        if not _UUID_RE.match(value):
            errors.append(_warn("malformedId", stage, prim.GetPath(),
                                "%s aeco:id %r is not a lowercase hyphenated "
                                "UUID." % (prim.GetPath(), value)))
        if value in seen:
            errors.append(_err("duplicateId", stage, prim.GetPath(),
                               "%s reuses aeco:id %r already used by %s."
                               % (prim.GetPath(), value, seen[value])))
        seen.setdefault(value, prim.GetPath())
    return errors


# --- spatial grammar --------------------------------------------------------

def _nearest_spatial_ancestor(prim):
    parent = prim.GetParent()
    while parent and parent.GetPath() != Sdf.Path.absoluteRootPath:
        if _is_spatial(parent):
            return parent
        parent = parent.GetParent()
    return None


def _element_between(prim):
    """True if an ELEMENT prim sits between this spatial prim and its
    nearest spatial ancestor (spaces don't live inside walls)."""
    parent = prim.GetParent()
    while parent and parent.GetPath() != Sdf.Path.absoluteRootPath:
        if _is_spatial(parent):
            return False
        if parent.HasAPI("AecoElementAPI"):
            return True
        parent = parent.GetParent()
    return False


def _validate_spatial_grammar(prim, timeRange):
    stage = prim.GetStage()
    errors = []
    # Referent kinds are disjoint: a container or a port is never also an
    # element. apiSchemaCanOnlyApplyTo can only say "Imageable", and both
    # are Xformable, so the refusal is the validator's.
    if prim.HasAPI("AecoElementAPI"):
        if _is_spatial(prim):
            errors.append(_err(
                "spatialIsElement", stage, prim.GetPath(),
                "%s is a spatial container (%s) and also wears "
                "AecoElementAPI — containers hold elements, they are not "
                "elements." % (prim.GetPath(), prim.GetTypeName())))
        elif prim.GetTypeName() == "AecoPort":
            errors.append(_err(
                "portIsElement", stage, prim.GetPath(),
                "%s is an AecoPort and also wears AecoElementAPI — a port "
                "belongs to an element, it is not one." % prim.GetPath()))
    stype = _spatial_type(prim)
    if stype is None:
        return errors
    ancestor = _nearest_spatial_ancestor(prim)
    ancestor_type = _spatial_type(ancestor) if ancestor else None

    allowed = _PARENT_RULES[stype]
    if ancestor_type not in allowed:
        if stype == "facility" and ancestor_type == "facility":
            errors.append(_err(
                "facilityInFacility", stage, prim.GetPath(),
                "Facility %s is contained in facility %s. A composite "
                "development is ONE facility whose major divisions are "
                "AecoFacilityPart prims; separately-operated assets are "
                "sibling facilities related by systems/references."
                % (prim.GetPath(), ancestor.GetPath())))
        elif ancestor is None and stype in ("part", "space"):
            errors.append(_warn(
                "unanchoredSpatial", stage, prim.GetPath(),
                "%s (%s) has no spatial ancestor — legitimate for "
                "work-in-progress or library fragments, incomplete for "
                "exchange." % (prim.GetPath(), stype)))
        else:
            errors.append(_err(
                "badSpatialNesting", stage, prim.GetPath(),
                "%s (%s) sits under %s; the grammar allows parent types %s."
                % (prim.GetPath(), stype,
                   ("%s (%s)" % (ancestor.GetPath(), ancestor_type))
                   if ancestor else "no spatial prim",
                   [a if a else "<root>" for a in allowed])))

    if _element_between(prim):
        errors.append(_warn(
            "spatialInsideElement", stage, prim.GetPath(),
            "Spatial prim %s sits inside an element subtree — spaces "
            "don't live inside walls." % prim.GetPath()))

    if str(prim.GetTypeName()) == "AecoLevel":
        elev = prim.GetAttribute("aeco:elevation")
        if not elev.HasAuthoredValue():
            errors.append(_warn(
                "levelWithoutElevation", stage, prim.GetPath(),
                "Level %s does not author aeco:elevation." % prim.GetPath()))
        elif prim.GetAttribute("xformOpOrder").HasAuthoredValue():
            up = UsdGeom.GetStageUpAxis(stage)
            axis = {"Z": 2, "Y": 1, "X": 0}[str(up)]
            m = Gf.Matrix4d(1)
            p = prim
            while p and p.GetPath() != Sdf.Path.absoluteRootPath:
                if str(p.GetTypeName()) == "AecoFacility":
                    break
                x = UsdGeom.Xformable(p)
                if x:
                    m = m * x.GetLocalTransformation(Usd.TimeCode.Default())
                p = p.GetParent()
            offset = m.ExtractTranslation()[axis]
            if abs(offset - elev.Get()) > 1e-3:
                errors.append(_warn(
                    "elevationDrift", stage, prim.GetPath(),
                    "Level %s declares aeco:elevation=%s but placement puts "
                    "the datum at %.4f in the facility frame — declarative "
                    "datum and geometry have drifted (the failure IFC's "
                    "deprecated storey Elevation institutionalized)."
                    % (prim.GetPath(), elev.Get(), offset)))
    return errors


# --- classification: the kind mechanism, measured ---------------------------

def _validate_classification(prim, timeRange):
    errors = []
    stage = prim.GetStage()
    instances = registry.classification_instances(prim)
    coded = False
    for name in instances:
        code = prim.GetAttribute("aeco:class:%s:code" % name).Get() or ""
        if name not in registry.CLASSIFICATION_SYSTEMS:
            errors.append(_warn(
                "unregisteredClassificationSystem", stage, prim.GetPath(),
                "%s classifies under instance %r, not a registered system "
                "name (registry warn: two tools must name one dictionary "
                "one way)." % (prim.GetPath(), name)))
        if not code:
            errors.append(_warn(
                "emptyClassificationCode", stage, prim.GetPath(),
                "%s applies AecoClassificationAPI:%s with no code."
                % (prim.GetPath(), name)))
        else:
            coded = True
        if name == "ifc" and code.startswith(registry.PROXY_CODE_PREFIX):
            errors.append(_warn(
                "proxyClassified", stage, prim.GetPath(),
                "%s is classified %r — a proxy says nothing about kind "
                "(health metric)." % (prim.GetPath(), code)))
    if prim.HasAPI("AecoElementAPI") and not coded:
        errors.append(_warn(
            "unclassifiedElement", stage, prim.GetPath(),
            "Element %s carries no classification code; kind queries "
            "will not see it (health metric)." % prim.GetPath()))
    return errors


# --- ports ------------------------------------------------------------------

def _validate_port(prim, timeRange):
    if prim.GetTypeName() != "AecoPort":
        return []
    errors = []
    stage = prim.GetStage()
    my_flow = prim.GetAttribute("aeco:flowDirection").Get() or "undefined"
    my_medium = prim.GetAttribute("aeco:medium").Get() or "undefined"
    rel = prim.GetRelationship("aeco:connectedPorts")
    for target in (rel.GetTargets() if rel else []):
        peer = stage.GetPrimAtPath(target)
        if not peer or peer.GetTypeName() != "AecoPort":
            errors.append(_err("danglingPortLink", stage, prim.GetPath(),
                               "%s connects to %s which is not an AecoPort."
                               % (prim.GetPath(), target)))
            continue
        peer_rel = peer.GetRelationship("aeco:connectedPorts")
        if prim.GetPath() not in (peer_rel.GetTargets() if peer_rel else []):
            errors.append(_err("asymmetricPortLink", stage, prim.GetPath(),
                               "%s connects to %s but not vice versa."
                               % (prim.GetPath(), target)))
        peer_flow = peer.GetAttribute("aeco:flowDirection").Get() or "undefined"
        if ("undefined" not in (my_flow, peer_flow)
                and (my_flow, peer_flow) not in _FLOW_OK):
            errors.append(_err(
                "incompatibleFlow", stage, prim.GetPath(),
                "%s (%s) connected to %s (%s); pair source with sink or "
                "use bidirectional." % (prim.GetPath(), my_flow, target,
                                        peer_flow)))
        peer_medium = peer.GetAttribute("aeco:medium").Get() or "undefined"
        if (my_medium != peer_medium
                and my_medium not in _MEDIA_WILD
                and peer_medium not in _MEDIA_WILD):
            errors.append(_err(
                "mediumMismatch", stage, prim.GetPath(),
                "%s carries medium %r but its connected port %s carries %r "
                "— the core refuses pipe-to-cable connections without any "
                "downstream schema loaded."
                % (prim.GetPath(), my_medium, target, peer_medium)))
    return errors


# --- groups -----------------------------------------------------------------

def _validate_group(prim, timeRange):
    if not _is_group(prim):
        return []
    errors = []
    stage = prim.GetStage()
    serves = prim.GetRelationship("aeco:serves")
    targets = serves.GetTargets() if serves else []
    if prim.GetTypeName() == "AecoZone" and targets:
        errors.append(_warn(
            "zoneAuthorsServes", stage, prim.GetPath(),
            "Zone %s authors aeco:serves — a SYSTEM fact; move it to the "
            "serving system or drop it." % prim.GetPath()))
    for t in targets:
        target = stage.GetPrimAtPath(t.GetPrimPath())
        if target and not (_is_spatial(target)
                           or target.GetTypeName() == "AecoZone"):
            errors.append(_warn(
                "servesTargetsNonSpatial", stage, prim.GetPath(),
                "%s serves %s (%s) — aeco:serves names the spatial prims "
                "or zones a system serves; member connectivity is the "
                "members collection and ports."
                % (prim.GetPath(), t, target.GetTypeName() or "untyped")))
    includes = prim.GetRelationship("collection:members:includes")
    for t in (includes.GetTargets() if includes else []):
        if not stage.GetPrimAtPath(t.GetPrimPath()):
            errors.append(_warn(
                "danglingMember", stage, prim.GetPath(),
                "%s lists member %s which does not resolve — a restructure "
                "moved it; usdaeco_tools.repath repairs by aeco:id."
                % (prim.GetPath(), t)))
    return errors


# --- Derived representations ---------------------------------------------

def _has_api(prim, api_name):
    return api_name in [a.split(":")[0] for a in prim.GetAppliedSchemas()]


def _validate_derived_geometry(prim, timeRange):
    """AecoDerivedGeometryAPI: the gprim must be a descendant of the referent
    whose id it names (the derived mark survives referencing only if the
    source id is repeated), and the role must agree with the purpose."""
    errs = []
    if not _has_api(prim, "AecoDerivedGeometryAPI"):
        return errs
    stage, path = prim.GetStage(), prim.GetPath()
    source = prim.GetAttribute("aeco:derived:source").Get() or ""
    anc = prim.GetParent(); found = None
    while anc and anc.IsValid() and not anc.IsPseudoRoot():
        a = anc.GetAttribute("aeco:id")
        if a and a.Get():
            found = a.Get(); break
        anc = anc.GetParent()
    if not source:
        errs.append(_warn("derivedGeometryOrphan", stage, path,
                          "aeco:derived:source is empty"))
    elif found is not None and found != source:
        errs.append(_warn("derivedGeometryOrphan", stage, path,
                          "aeco:derived:source %s is not the enclosing referent's id %s"
                          % (source, found)))
    role = prim.GetAttribute("aeco:derived:role").Get()
    allowed = prim.GetAttribute("aeco:derived:role").GetMetadata("allowedTokens") or ()
    if role not in allowed:
        errs.append(_warn("derivedGeometryRole", stage, path,
                          "unknown derived geometry role '%s'" % role))
    purpose = UsdGeom.Imageable(prim).ComputePurpose() if prim.IsA(UsdGeom.Imageable) else None
    expected = {"proxy": "proxy", "axis": "guide", "extent": "guide",
                "sector": "guide", "coverage": "guide", "wireframe": "guide"}.get(role)
    if expected and purpose not in (expected,):
        errs.append(_warn("derivedGeometryPurpose", stage, path,
                          "role '%s' expects purpose '%s', found '%s'" % (role, expected, purpose)))
    return errs


def _validate_exact_mesh(prim, time_range):
    """E15: tessellation never declares exact geometry."""
    if (_has_api(prim, "AecoDerivedGeometryAPI") and prim.IsA(UsdGeom.Mesh)
            and prim.GetAttribute("aeco:derived:approx").Get() == "exact"):
        return [_err("DerivedExactOnMesh", prim.GetStage(), prim.GetPath(),
                     "A Mesh is tessellated; use approx = tessellated and link its exact source.")]
    return []


def _validate_exact_tolerance(prim, time_range):
    """E15: exact geometry declares a positive finite modelling tolerance."""
    import math
    if _has_api(prim, "AecoDerivedGeometryAPI") and prim.GetAttribute("aeco:derived:approx").Get() == "exact":
        tolerance = prim.GetAttribute("aeco:derived:tolerance").Get()
        if tolerance is None or not math.isfinite(tolerance) or tolerance <= 0:
            return [_warn("ExactWithoutTolerance", prim.GetStage(), prim.GetPath(),
                          "Exact geometry must declare a positive finite tolerance in metres.")]
    return []


def register():
    """Discover the Python plugin; loading is delegated to UsdValidation."""
    from pathlib import Path
    from pxr import Plug
    source = Path(__file__).resolve()
    candidates = [source.parents[2] / "usdAecoValidators", source.parent.parent / "usdAecoValidators"]
    for candidate in candidates:
        if candidate.is_dir():
            Plug.Registry().RegisterPlugins(str(candidate))
            break


def validate_stage(stage, include_builtin=True):
    """Run the shared registry adapter, optionally with USD's core rules."""
    from usdaeco_check.validation import run
    register()
    return run(stage, [KEYWORD] + (["UsdCoreValidators"] if include_builtin else []))


def split(errors):
    """(errors, warnings) — the two severities separated."""
    hard = [e for e in errors
            if e.GetType() == UsdValidation.ValidationErrorType.Error]
    soft = [e for e in errors
            if e.GetType() != UsdValidation.ValidationErrorType.Error]
    return hard, soft
