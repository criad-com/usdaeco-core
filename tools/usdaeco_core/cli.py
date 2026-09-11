"""Validate a USD stage with the core plugin."""
import argparse
import json
from usdaeco_tools import register_plugins, validators


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["check"])
    parser.add_argument("stage")
    args = parser.parse_args(argv)
    register_plugins()
    from pxr import Usd
    findings = validators.validate_stage(Usd.Stage.Open(args.stage))
    print(json.dumps([{"name": e.GetName(), "message": e.GetMessage()} for e in findings], indent=2))
    return int(bool(validators.split(findings)[0]))


if __name__ == "__main__":
    raise SystemExit(main())
