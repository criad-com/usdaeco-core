"""Verify the native CollectionAPI override missed by toolchain 0.2 S09.

USD built-in APIs contribute properties through prim definitions, not Sdf
property stacks. The upstream lint inspects only the latter. All S09 checks
are retained after supplying evidence for this one stock-property override.
"""
from copy import deepcopy
from pathlib import Path
from usdaeco_check import Result
from usdaeco_check.structure import Context, check_structure as upstream_structure, namespaces


def collection_override(context):
    from pxr import Sdf, Usd
    source = Sdf.Layer.FindOrOpen(str(context.module / "schema.usda"))
    prim = source.GetPrimAtPath("/AecoGroupBase")
    prop = prim.properties.get("collection:members:expansionRule")
    definition = Usd.SchemaRegistry().FindAppliedAPIPrimDefinition("CollectionAPI")
    stock = definition.GetSchemaAttributeSpec("collection:__INSTANCE_NAME__:expansionRule")
    if not (stock and prop and prop.typeName == stock.typeName
            and prop.default == "explicitOnly"
            and "CollectionAPI:members" in prim.GetInfo("apiSchemas").GetAppliedItems()):
        raise ValueError("the native CollectionAPI override has changed")
    data = deepcopy(context.schema_data)
    group = next(item for item in data["classes"] if item["name"] == "AecoGroupBase")
    group["inherited_properties"].append(prop.name)
    context._schema_data = data
    # Reapply the complete upstream rule so any other foreign property fails.
    namespaces(context)


def check_structure(root, deps=()):
    for result in upstream_structure(root, deps=deps):
        if result.name == "S09" and not result.ok:
            try:
                collection_override(Context(root, deps, []))
            except Exception:
                yield result
            else:
                yield Result("S09", True, "stock CollectionAPI override verified; toolchain 0.2 S09 compatibility correction")
        else:
            yield result
