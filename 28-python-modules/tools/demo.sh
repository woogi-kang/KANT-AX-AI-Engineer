#!/usr/bin/env bash
# Makes the class's shopping-cart project with uv and runs every scene in tools/scenes.py for real output.
# The project sits in /home/kim/shopping-cart so error paths read like a student's folder.
# Usage: bash tools/demo.sh   (writes tools/out.json and prints a log)
set -u
TOOLS=$(cd "$(dirname "$0")" && pwd)
ROOT=/home/kim
unset VIRTUAL_ENV UV_NATIVE_TLS
export NO_COLOR=1 PYTHON_COLORS=0
export UV_PYTHON=3.14.6
[ -f /root/.ccr/ca-bundle.crt ] && export UV_SYSTEM_CERTS=1
rm -rf "$ROOT/shopping-cart" "$ROOT/base"
mkdir -p "$ROOT" && cd "$ROOT" || exit 1
uv init -q base && rm -f base/README.md
(cd base && uv sync -q)
python3 -I "$TOOLS/run_scenes.py" "$ROOT" "$TOOLS/out.json"
