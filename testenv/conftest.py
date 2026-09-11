"""Run source tests without an installed package or build backend."""
from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(Path(os.environ.get("TOOLCHAIN_DIR", ROOT.parent / "usdaeco-toolchain")) / "tools"))
