#!/pxrpythonsubst
"""Plugin-free acceptance must fail when either twin or correlation is lost."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import bootstrap
from pxr import Sdf


class TestB7(unittest.TestCase):
    def run_probe(self, filename):
        environment = {k:v for k,v in os.environ.items()
                       if k not in ("PYTHONPATH", "PXR_PLUGINPATH_NAME", "PXR_AR_DEFAULT_SEARCH_PATH")}
        return subprocess.run([sys.executable, str(bootstrap.ROOT / "testenv/vanilla_probe.py"), str(filename)],
                              env=environment, capture_output=True, text=True)

    def test_plugin_free_twin(self):
        probe = self.run_probe(bootstrap.ROOT / "testenv/brepTwin/stage.usda")
        self.assertEqual(probe.returncode, 0, probe.stderr)
        self.assertIn('"mesh_twins": 1', probe.stdout)

    def broken(self, mutation):
        layer = Sdf.Layer.CreateAnonymous()
        layer.TransferContent(Sdf.Layer.FindOrOpen(str(bootstrap.ROOT / "testenv/brepTwin/stage.usda")))
        mutation(layer)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "broken.usda"
            layer.Export(str(path))
            self.assertNotEqual(self.run_probe(path).returncode, 0)

    def test_missing_mesh_fails(self):
        def remove(layer):
            edit = Sdf.BatchNamespaceEdit()
            edit.Add("/World/Facility/Element/Body", Sdf.Path.emptyPath)
            self.assertTrue(layer.Apply(edit))
        self.broken(remove)

    def test_missing_from_fails(self):
        self.broken(lambda layer: setattr(layer.GetRelationshipAtPath("/World/Facility/Element/Body.aeco:derived:from").targetPathList, "explicitItems", []))

    def test_brep_fallback_is_refused(self):
        from pxr import Vt
        self.broken(lambda layer: layer.pseudoRoot.SetInfo("fallbackPrimTypes", {"BrepArray": Vt.TokenArray(["Xform"])}))


if __name__ == "__main__":
    unittest.main()
