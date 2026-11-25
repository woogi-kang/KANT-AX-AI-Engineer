#!/usr/bin/env bash
# Makes the ml-basics project like chapters 45 to 49 (numpy pandas ipykernel, seaborn matplotlib, scikit-learn) and runs
# tools/terms.py with its Python, so every snippet and number in the ML terms deck is real output.
# The class's usa_housing.csv comes from chapter 47's datasets folder. seaborn's titanic needs the internet (46).
# Usage: bash tools/demo.sh /tmp/ml-terms-demo > tools/demo.log 2>&1
set -u
TOOLS=$(cd "$(dirname "$0")" && pwd)
ROOT=${1:-/tmp/ml-terms-demo}
CSV=${CSV:-$TOOLS/../../../47-plot-data/datasets/usa_housing.csv}
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
run mkdir datasets
run cp "$CSV" datasets/
run .venv/bin/python --version
.venv/bin/python -c "import sklearn, pandas, numpy; print('scikit-learn', sklearn.__version__, 'pandas', pandas.__version__, 'numpy', numpy.__version__)"
echo
.venv/bin/python "$TOOLS/terms.py" "$TOOLS/data.json"
