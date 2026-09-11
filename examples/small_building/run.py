#!/usr/bin/env python3
"""Publish this core example through the shared run_example harness and hook."""
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
KIT = Path(os.environ.get("TOOLCHAIN_DIR", ROOT.parent / "usdaeco-toolchain"))
sys.path[:0] = [str(ROOT), str(ROOT / "tools"), str(KIT / "tools")]
from usdaeco_core.example import prepare
from usdaeco_check.example import run_example

if __name__ == "__main__":
    example, options = prepare(Path(__file__).resolve().parent)
    manifest = run_example(example, **options)
    print(f"Published evidence: {manifest['result']['prim_count']} prims; 8 core validators")
