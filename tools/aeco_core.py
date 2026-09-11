#!/usr/bin/env python3
"""Source-checkout equivalent of the aeco-core entry point."""
from pathlib import Path
import os
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "tools"), str(Path(os.environ.get("TOOLCHAIN_DIR", ROOT.parent / "usdaeco-toolchain")) / "tools")]
from usdaeco_core.cli import main
if __name__ == "__main__":
    raise SystemExit(main())
