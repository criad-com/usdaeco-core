"""Governed token registries — DATA, released out-of-band from the schema.

The core keeps exactly two registries, because the core has exactly two
open conventions that must stay measurable without becoming schema:

  classification_systems.json   the sanctioned INSTANCE NAMES of
                                AecoClassificationAPI (ifc, uniclass, ...)
                                so two tools name one dictionary one way
  prop_sets.json                the sanctioned aeco:props:<set> families
                                (the ad-hoc data quarantine, rule E7)

Neither registry is a taxonomy: what a thing IS comes from the external
dictionaries themselves. Consumers WARN (never error) on unknown tokens,
so data authored against a newer registry still opens everywhere.

This module is only the loader plus the health metrics the core
promises: the share of elements with no classification at all (the
measurable version of IFC's proxy abuse) and the props-set census.
"""
import json
import os

_REG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "registries")

CLASSIFICATION_API = "AecoClassificationAPI"
PROXY_CODE_PREFIX = "IfcBuildingElementProxy"


def _load(name):
    with open(os.path.join(_REG_DIR, name), encoding="utf-8") as f:
        return json.load(f)


def load_classification_systems():
    return _load("classification_systems.json")


def load_prop_sets():
    return _load("prop_sets.json")


CLASSIFICATION_SYSTEMS = set(load_classification_systems()["systems"])
PROP_SET_PATTERNS = load_prop_sets()["sanctioned"]


def add_classification_systems(names):
    """Sanction further instance names for this process (a project or
    sector profile's extras). Returns the names newly added."""
    new = set(names) - CLASSIFICATION_SYSTEMS
    CLASSIFICATION_SYSTEMS.update(new)
    return new


# --- classification: the kind mechanism, measured ---------------------------

def classification_instances(prim):
    """The instance names of AecoClassificationAPI applied on a prim."""
    return [s.split(":", 1)[1] for s in prim.GetAppliedSchemas()
            if s.startswith(CLASSIFICATION_API + ":")]


def classification_health(stage):
    """(unclassified, proxy, systems_used, total) over all elements:
    unclassified = elements with no classification instance carrying a
    code; proxy = elements whose IFC code is IfcBuildingElementProxy;
    systems_used = the instance names seen. The core's model-health
    metric — a stage with unclassified > 0 is legible but unqueryable
    by kind."""
    unclassified, proxy, systems, total = 0, 0, set(), 0
    for prim in stage.Traverse():
        if not prim.HasAPI("AecoElementAPI"):
            continue
        total += 1
        coded = False
        for name in classification_instances(prim):
            systems.add(name)
            code = prim.GetAttribute("aeco:class:%s:code" % name).Get() or ""
            if code:
                coded = True
            if name == "ifc" and code.startswith(PROXY_CODE_PREFIX):
                proxy += 1
        if not coded:
            unclassified += 1
    return unclassified, proxy, systems, total


def classification_census(stage, system="ifc", entity_only=True):
    """{code: count} over all elements for one system ('' = no code in
    that system). With entity_only, 'IfcWall.PARTITIONING' counts under
    'IfcWall' — the coarse census."""
    out = {}
    for prim in stage.Traverse():
        if not prim.HasAPI("AecoElementAPI"):
            continue
        attr = prim.GetAttribute("aeco:class:%s:code" % system)
        code = (attr.Get() if attr else None) or ""
        if entity_only and "." in code:
            code = code.split(".", 1)[0]
        out[code] = out.get(code, 0) + 1
    return out


# --- the props quarantine, measured -----------------------------------------

def _sanctioned_set(name):
    for pat in PROP_SET_PATTERNS:
        if pat.endswith("*"):
            if name.startswith(pat[:-1]):
                return True
        elif name == pat:
            return True
    return False


def prop_set_health(stage):
    """(used_sets, unsanctioned_sets): the aeco:props:<set> names a stage
    uses — consumers WARN on unsanctioned, never error (the family is
    open by design; this only makes it measurable)."""
    used = set()
    for prim in stage.Traverse():
        for attr in prim.GetAttributes():
            n = attr.GetName()
            if n.startswith("aeco:props:"):
                rest = n[len("aeco:props:"):]
                if ":" in rest:
                    used.add(rest.split(":", 1)[0])
    unsanctioned = sorted(s for s in used if not _sanctioned_set(s))
    return sorted(used), unsanctioned
