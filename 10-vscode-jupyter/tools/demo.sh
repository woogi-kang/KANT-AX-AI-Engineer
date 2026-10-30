#!/usr/bin/env bash
# Makes hello-uv like chapter 09 and runs the deck's notebook cells with its kernel for real output.
# Usage: bash tools/demo.sh /tmp/nb-demo > /tmp/nb-demo.log 2>&1
set -u
TOOLS=$(cd "$(dirname "$0")" && pwd)
ROOT=${1:-/tmp/nb-demo}
if [ -e "$ROOT" ]; then echo "$ROOT already exists. Pick a new folder."; exit 1; fi
mkdir -p "$ROOT" && cd "$ROOT" || exit 1
unset VIRTUAL_ENV UV_NATIVE_TLS
export NO_COLOR=1
[ -f /root/.ccr/ca-bundle.crt ] && export UV_SYSTEM_CERTS=1
run() { echo; echo "\$ $*"; eval "$@" 2>&1; }
run uv --version
run uv init hello-uv
run cd hello-uv
run uv add --dev ipykernel
# nbclient stands in for VS Code. It goes into a copy so hello-uv stays as students have it.
cp -r "$ROOT/hello-uv" "$ROOT/nb-check"
(cd "$ROOT/nb-check" && uv sync -q && uv pip install -q nbclient nbformat && echo && .venv/bin/python "$TOOLS/run_nb.py" 2>/dev/null)
