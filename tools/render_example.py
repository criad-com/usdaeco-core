#!/usr/bin/env python3
"""Render the small building isometrically, framed from its visible bounds."""
import json
import os
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
KIT = Path(os.environ.get('TOOLCHAIN_DIR', ROOT.parent / 'usdaeco-toolchain'))
sys.path.insert(0, str(KIT / 'tools'))
from pxr import Plug, Sdf, Usd
from usdaeco_core.views import frame_view
from usdaeco_render import render


def main():
    print('== stage: isometric building render', flush=True)
    Plug.Registry().RegisterPlugins(str(ROOT / 'usdAeco'))
    out = ROOT / 'out/preview'
    out.mkdir(parents=True, exist_ok=True)
    view_path = out / 'view.usda'
    view_path.unlink(missing_ok=True)
    layer = Sdf.Layer.CreateNew(str(view_path))
    layer.subLayerPaths = [os.path.relpath(ROOT / 'usdAeco/examples/small_building.usda', out)]
    stage = Usd.Stage.Open(layer)
    frame_view(stage, layer)
    record, = render(view_path, output=out / 'renders', purposes='guide,proxy,render',
                     executable=shutil.which('usdrecord') or str(Path(sys.executable).with_name('usdrecord')))
    target = ROOT / 'usdAeco/userDoc/usdAecoExample.png'
    shutil.copyfile(out / record['path'], target)
    record['path'] = 'userDoc/' + target.name
    (target.parent / 'render.json').write_text(json.dumps({'renders': [record]}, indent=2) + '\n')
    print(json.dumps(record, sort_keys=True))


if __name__ == '__main__':
    main()
