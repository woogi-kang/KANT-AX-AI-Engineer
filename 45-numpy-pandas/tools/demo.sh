#!/usr/bin/env bash
# Makes the ml-basics project like the deck (uv init, uv add numpy pandas, ipykernel) and runs every notebook cell
# shown in the deck with its kernel for real output. A second project without pandas makes the ModuleNotFoundError.
# Usage: bash tools/demo.sh /tmp/numpy-pandas-demo > /tmp/numpy-pandas-demo.log 2>&1
set -u
TOOLS=$(cd "$(dirname "$0")" && pwd)
ROOT=${1:-/tmp/numpy-pandas-demo}
if [ -e "$ROOT" ]; then echo "$ROOT already exists. Pick a new folder."; exit 1; fi
mkdir -p "$ROOT" && cd "$ROOT" || exit 1
unset VIRTUAL_ENV UV_NATIVE_TLS
export NO_COLOR=1
[ -f /root/.ccr/ca-bundle.crt ] && export UV_SYSTEM_CERTS=1
run() { echo; echo "\$ $*"; eval "$@" 2>&1; }
run uv --version
run uv init ml-basics
run cd ml-basics
run uv add numpy pandas
run uv add --dev ipykernel
run cat pyproject.toml
# nbclient stands in for VS Code. It goes into copies so the projects stay as students have them.
cp -r "$ROOT/ml-basics" "$ROOT/nb-check"
(cd "$ROOT/nb-check" && uv sync -q && uv pip install -q nbclient nbformat && echo && .venv/bin/python --version && .venv/bin/python "$TOOLS/run_nb.py" main 2>/dev/null)
# The same notebook in a project that only has ipykernel: import pandas fails.
cd "$ROOT" && uv init -q no-pandas && cd no-pandas && uv add -q --dev ipykernel && uv pip install -q nbclient nbformat \
  && .venv/bin/python "$TOOLS/run_nb.py" nopandas 2>/dev/null
