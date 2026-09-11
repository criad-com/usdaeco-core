#!/pxrpythonsubst
"""Validate the exact USD blocks published in the worked examples."""
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
import bootstrap
from pxr import Usd, UsdGeom
from claims import TYPED, APIS
from usdaeco_tools.validators import split, validate_stage


def check_worked_examples():
    content = (bootstrap.ROOT / "docs/07-worked-examples.md").read_text()
    blocks = re.findall(r"### `([^`]+\.usda)`\n\n```usda\n(.*?)```", content, re.DOTALL)
    assert len(blocks) == 6, "expected six complete layer blocks"
    results = []
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        for name, data in blocks:
            assert Path(name).name == name
            (root / name).write_text(data)
        for name in ("pipe", "wall"):
            stage = Usd.Stage.Open(str(root / f"{name}.usda"))
            assert stage and not stage.GetCompositionErrors()
            errors, warnings = split(validate_stage(stage))
            assert not errors and not warnings, [e.GetMessage() for e in errors + warnings]
            elements, ports, bodies = [], [], []
            for prim in stage.Traverse():
                if prim.GetTypeName().startswith("Aeco"):
                    assert prim.GetTypeName() in TYPED
                    assert prim.GetTypeName() in stage.GetMetadata("fallbackPrimTypes")
                assert all(api.split(":")[0] in APIS for api in prim.GetAppliedSchemas()
                           if api.startswith("Aeco"))
                if prim.HasAPI("AecoElementAPI"):
                    elements.append(prim)
                if prim.GetTypeName() == "AecoPort":
                    ports.append(prim)
                if prim.IsA(UsdGeom.Gprim):
                    assert prim.HasAPI("AecoDerivedGeometryAPI")
                    assert prim.GetPrimStack()[0].layer.realPath.endswith(".derived.usda")
                    bodies.append(prim)
            assert (len(elements), len(ports), len(bodies)) == (2, 2, 2)
            identities = {p.GetPath(): p.GetAttribute("aeco:id").Get() for p in elements + ports}
            stage.MuteLayer(str(root / f"{name}.derived.usda"))
            assert not any(p.IsA(UsdGeom.Gprim) for p in stage.Traverse())
            assert identities == {p.GetPath(): p.GetAttribute("aeco:id").Get()
                                  for p in stage.Traverse() if p.GetPath() in identities}
            import os
            environment = {k: v for k, v in os.environ.items()
                           if k not in ("PYTHONPATH", "PXR_PLUGINPATH_NAME", "PXR_AR_DEFAULT_SEARCH_PATH")}
            probe = subprocess.run([sys.executable, "-c", """
from pxr import Plug, Usd, UsdGeom
import sys
stage = Usd.Stage.Open(sys.argv[1])
assert stage and not stage.GetCompositionErrors()
assert not any(p.name.startswith('usdAeco') for p in Plug.Registry().GetAllPlugins())
assert len([p for p in stage.Traverse() if p.IsA(UsdGeom.Gprim)]) == 2
for prim in stage.Traverse():
    if prim.GetTypeName().startswith('Aeco'):
        assert prim.GetPrimTypeInfo().GetSchemaTypeName() == 'Xform'
""", str(root / f"{name}.usda")], env=environment, capture_output=True, text=True)
            assert probe.returncode == 0, probe.stderr
            results.append((name, "2 elements, 2 ports, 2 marked bodies; 0 errors/warnings; vanilla composition"))
    return results


class TestWorkedExamples(unittest.TestCase):
    def test_published_stages(self):
        self.assertEqual(len(check_worked_examples()), 2)


if __name__ == "__main__":
    unittest.main()
