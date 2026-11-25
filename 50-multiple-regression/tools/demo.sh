#!/usr/bin/env bash
# Makes the ml-basics project like the deck (45's numpy pandas ipykernel, 46's seaborn matplotlib, 48's scikit-learn)
# and runs every notebook cell shown in the deck with its kernel for real output. Charts are saved as PNG in tools/img.
# Usage: FONT=/path/NanumGothic.ttf bash tools/demo.sh /tmp/multi-demo > tools/demo.log 2>&1
set -u
TOOLS=$(cd "$(dirname "$0")" && pwd)
ROOT=${1:-/tmp/multi-demo}
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
run uv add seaborn matplotlib
run uv add scikit-learn
run cat pyproject.toml
# nbclient stands in for VS Code. It goes into a copy so the project stays as students have it.
# FONT: a Korean TTF for the charts (Malgun Gothic and AppleGothic are not on Linux).
cp -r "$ROOT/ml-basics" "$ROOT/nb-check"
cd "$ROOT/nb-check" && uv sync -q && uv pip install -q nbclient nbformat \
  && { [ -z "${FONT:-}" ] || cp "$FONT" .venv/lib/python3*/site-packages/matplotlib/mpl-data/fonts/ttf/; } && echo && .venv/bin/python --version \
  && .venv/bin/python -c "import sklearn, seaborn; print('scikit-learn', sklearn.__version__); print('seaborn', seaborn.__version__)" \
  && FONT=${FONT:-} SHOTS="$TOOLS/img" .venv/bin/python "$TOOLS/run_nb.py" 2>/dev/null
