#!/usr/bin/env bash
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
TOOLCHAIN_DIR="${TOOLCHAIN_DIR:-$HERE/../usdaeco-toolchain}"
bash "$TOOLCHAIN_DIR/build.sh" usdAeco "$HERE" "$@"

# The Python validator needs its companion modules in the same install root.
while (( $# )); do
    if [[ "$1" == "--install-root" ]]; then
        mkdir -p "$2/python"
        cp -RL "$HERE/tools/usdaeco_core" "$HERE/tools/usdaeco_tools" "$2/python/"
        break
    fi
    shift
done
