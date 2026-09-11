#!/usr/bin/env python3
"""Run all shared rules with the documented native-override correction."""
import aeco_core
from usdaeco_check import Report
from usdaeco_core.structure import check_structure
from pxr import Plug
Plug.Registry().RegisterPlugins(str(aeco_core.ROOT / "usdAeco"))
report = Report()
for result in check_structure(aeco_core.ROOT, deps=[aeco_core.ROOT / "usdAeco"]):
    report.add(result)
report.exit()
