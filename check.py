#!/usr/bin/env python3
"""Build and verify core; print N checks, M failed."""
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
KIT = Path(os.environ.get("TOOLCHAIN_DIR", HERE.parent / "usdaeco-toolchain"))
sys.path[:0] = [str(KIT / "tools"), str(HERE), str(HERE / "tools"), str(HERE / "testenv")]
from usdaeco_check import Report, can_apply, registry_probe, validate_examples, plugin_requires
from usdaeco_core.structure import check_structure
from usdaeco_check.example import check_example


def main():
    report = Report()
    print("== stage: core boundary", flush=True)
    from testUsdAecoCoreOnly import add_checks
    add_checks(report)
    print("== stage: build", flush=True)
    env = {**os.environ, "PYTHON": sys.executable}
    env.pop("PYTHONPATH", None)
    env.pop("PXR_PLUGINPATH_NAME", None)
    out = HERE / "out"
    out.mkdir(exist_ok=True)
    with (out / "build.log").open("w") as log:
        build = subprocess.run(["bash", str(HERE / "build.sh"), "--install-root", str(out)], env=env, stdout=log, stderr=subprocess.STDOUT)
    if not report.check("build codeless install layout", build.returncode == 0, "out/build.log"):
        return report.finish()
    # Register before the S09 compatibility probe constructs SchemaRegistry.
    if not report.add(plugin_requires([out / "plugins/usdAeco/resources"])):
        return report.finish()
    print("== stage: structure", flush=True)
    for result in check_structure(HERE, deps=[out / "plugins/usdAeco/resources"]):
        report.add(result)
    print("== stage: registry and design claims", flush=True)
    from pxr import Plug, Usd, UsdValidation
    Plug.Registry().RegisterPlugins(str(HERE / "usdAecoValidators"))
    from usdaeco_core.example import load_validators
    load_validators(HERE)
    from claims import run_claims
    run_claims(report)
    from testUsdAecoBuilding import walls_meet
    try:
        report.check("walls meet", True, walls_meet(Usd.Stage.Open(str(HERE / "usdAeco/examples/small_building.usda"))))
    except ValueError as error:
        report.check("walls meet", False, str(error))
    report.add(registry_probe(["AecoProjectAPI", "AecoElementAPI", "AecoClassificationAPI", "AecoTypeAPI", "AecoDerivedGeometryAPI"],
        ["AecoSite", "AecoFacility", "AecoFacilityPart", "AecoLevel", "AecoSpace", "AecoSystem", "AecoZone", "AecoPort"]))
    report.add(can_apply([("Xform", "AecoElementAPI", True), ("AecoSystem", "AecoElementAPI", False),
        ("Mesh", "AecoDerivedGeometryAPI", True), ("Xform", "AecoDerivedGeometryAPI", False),
        ("Material", "AecoProjectAPI", False), ("Xform", "AecoClassificationAPI", True, "ifc")]))
    registry = UsdValidation.ValidationRegistry()
    metadata = registry.GetValidatorMetadataForKeyword("UsdAecoValidators")
    report.check("validator plugin listing", len(metadata) == 8 and all(registry.GetOrLoadValidatorByName(m.name) for m in metadata), "8 Python validators")
    from usdaeco_tools.validators import validate_stage
    # The helper includes the six stages and their minimal alias.
    report.add(validate_examples(HERE / "usdAeco/examples", validators=[lambda s: validate_stage(s, False)]))
    print("== stage: worked examples", flush=True)
    from testUsdAecoWorkedExamples import check_worked_examples
    try:
        for name, detail in check_worked_examples():
            report.check("worked " + name + " example", True, detail)
    except Exception as error:
        report.check("worked core examples", False, str(error))
    print("== stage: E15 and B7", flush=True)
    from testUsdAecoValidators import marked, errors
    stage, prim = marked(tolerance=1e-6)
    report.check("E15 seeded exact Mesh is an error", [e.GetName() for e in errors(stage)] == ["DerivedExactOnMesh"])
    stage, prim = marked("Cube", 1e-6)
    report.check("E15 analytic Cube is exact", errors(stage) == [])
    prim.GetAttribute("aeco:derived:tolerance").Set(0)
    findings = errors(stage)
    report.check("E15 unknown exact tolerance warns", len(findings) == 1 and findings[0].GetName() == "ExactWithoutTolerance"
        and findings[0].GetType() == UsdValidation.ValidationErrorType.Warn)
    probe = subprocess.run([sys.executable, str(HERE / "testenv/vanilla_probe.py"), str(HERE / "testenv/brepTwin/stage.usda")], env=env, capture_output=True, text=True)
    report.check("B7 unknown BrepArray and linked renderable Mesh twin", probe.returncode == 0, probe.stdout.strip() or probe.stderr[-600:])
    print("== stage: committed core results", flush=True)
    from types import SimpleNamespace
    from usdaeco_core.example import EXAMPLES
    from usdaeco_check.structure import example_files, example_manifest
    for name in EXAMPLES:
        print("== stage: verify " + name, flush=True)
        example = HERE / "examples" / name
        try:
            context = SimpleNamespace(root=HERE, example=example)
            example_files(context)
            example_manifest(context)
            result = check_example(example)
            report.check("published " + name + " (S21–S28)", result.ok, result.detail)
        except (OSError, ValueError) as error:
            report.check("published " + name + " (S21–S28)", False, str(error))
    return report.finish()


if __name__ == "__main__":
    raise SystemExit(main())
