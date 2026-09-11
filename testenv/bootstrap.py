"""Resolve source packages without contaminating the USD Python ABI."""
import os
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "tools"),
    str(Path(os.environ.get("TOOLCHAIN_DIR", ROOT.parent / "usdaeco-toolchain")) / "tools")]
from pxr import Plug
Plug.Registry().RegisterPlugins(str(ROOT / "usdAeco"))
Plug.Registry().RegisterPlugins(str(ROOT / "usdAecoValidators"))
