#!/usr/bin/env bash
# Runs every command of the uv deck in a fresh folder and prints the real output.
# Usage: bash tools/demo.sh /tmp/uv-demo > /tmp/uv-demo.log 2>&1
# uv's own cache and Python downloads go inside the folder, so the first run downloads Python
# like a student's computer with no Python installed.
set -u
TOOLS=$(cd "$(dirname "$0")" && pwd)
ROOT=${1:-/tmp/uv-demo}
if [ -e "$ROOT" ]; then echo "$ROOT already exists. Pick a new folder."; exit 1; fi
mkdir -p "$ROOT"
cd "$ROOT" || exit 1
unset UV_NATIVE_TLS VIRTUAL_ENV
export UV_CACHE_DIR="$ROOT/.uv-cache" UV_PYTHON_INSTALL_DIR="$ROOT/.uv-python" UV_PYTHON_PREFERENCE=only-managed NO_COLOR=1
export GIT_AUTHOR_DATE="2026-10-30T10:00:00+09:00" GIT_COMMITTER_DATE="2026-10-30T10:00:00+09:00"
printf "[init]\n\tdefaultBranch = main\n[user]\n\tname = kim\n\temail = kim@example.com\n" > "$ROOT/.gitconfig"
export GIT_CONFIG_GLOBAL="$ROOT/.gitconfig"
export PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
[ -f /root/.ccr/ca-bundle.crt ] && export UV_SYSTEM_CERTS=1 PIP_CERT=/root/.ccr/ca-bundle.crt
run() { echo; echo "\$ $*"; eval "$@" 2>&1; }

echo "===== uv 버전"
run uv --version

echo "===== 3부 uv init"
run uv init hello-uv
run cd hello-uv
run ls -a
run cat pyproject.toml
run cat .python-version
run cat main.py
run cat .gitignore
run uv run main.py
run ls -a
run uv run main.py

echo "===== 4부 가상환경 직접 켜기"
run source .venv/bin/activate
echo "(프롬프트 이름: $VIRTUAL_ENV_PROMPT)"
run which python
run python --version
run python main.py
run deactivate
run which python3

echo "===== 5부 add / remove"
run uv add fastapi
run cat pyproject.toml
run uv tree --depth 2
cat > main.py <<'PY'
import fastapi

print("fastapi 버전:", fastapi.__version__)
PY
run cat main.py
run uv run main.py
run uv remove fastapi
run cat pyproject.toml
run uv run main.py
run uv add fastapi
run uv run main.py

echo "===== 5부 다른 컴퓨터에서 uv sync"
git init -q --bare "$ROOT/github-hello-uv.git"
run git status --short
run git add .
run 'git commit -m "feat: hello-uv 프로젝트 만들기" | head -1'
git config --global url."$ROOT/github-hello-uv.git".insteadOf https://github.com/kim/hello-uv.git
run git remote add origin https://github.com/kim/hello-uv.git
run git push origin main
cd "$ROOT"
mkdir lee && cd lee
# lee는 다른 컴퓨터예요. uv 캐시와 파이썬을 따로 둬요.
export UV_CACHE_DIR="$ROOT/lee/.uv-cache" UV_PYTHON_INSTALL_DIR="$ROOT/lee/.uv-python"
run git clone https://github.com/kim/hello-uv.git
run cd hello-uv
run ls -a
run uv sync
run ls -a
run uv run main.py

export UV_CACHE_DIR="$ROOT/.uv-cache" UV_PYTHON_INSTALL_DIR="$ROOT/.uv-python"

echo "===== 7부 Jupyter 커널"
cd "$ROOT/hello-uv"
run uv add --dev ipykernel
run cat pyproject.toml
run 'uv run python -c "print(\"안녕하세요\")"'
run 'uv run python -c "import sys; print(sys.executable)"'
run 'uv run python -c "import fastapi; print(fastapi.__version__)"'
run 'uv run python -c "import ipykernel; print(ipykernel.__version__)"'
# 노트북 셀을 VS Code처럼 프로젝트 커널로 실행해요. 원본을 건드리지 않게 복사본에 nbclient를 넣어요.
cp -r "$ROOT/hello-uv" "$ROOT/nb-check" && rm -rf "$ROOT/nb-check/.venv"
(cd "$ROOT/nb-check" && uv sync -q && uv pip install -q nbclient nbformat && echo && echo "# 노트북 셀 실행" && .venv/bin/python "$TOOLS/run_nb.py" 2>/dev/null)
echo "===== 6부 파이썬 버전"
cd "$ROOT"
run uv init --python 3.13 hello-313
run cd hello-313
run cat .python-version
run "grep requires-python pyproject.toml"
run uv run python --version
run uv run main.py

echo "===== 1부 예전 방식 (uv가 받은 파이썬을 python3로 씀)"
PYBIN=$(dirname "$(uv python find 3.14)")
mkdir -p "$ROOT/shim" && ln -s "$PYBIN/python3.14" "$ROOT/shim/python3"
export PATH="$ROOT/shim:$PATH"
cd "$ROOT"
mkdir old-way && cd old-way
cp "$ROOT/hello-uv/main.py" .
run python3 --version
echo 'print("안녕하세요")' > hello.py
run cat hello.py
run python3 hello.py
run python3 main.py
run python3 -m venv .venv
run ls -a
run source .venv/bin/activate
run pip install fastapi
run 'pip freeze > requirements.txt'
run cat requirements.txt
run python main.py
run pip uninstall -y fastapi
run 'pip freeze | wc -l'
run pip freeze
run deactivate
run python3 main.py

echo "===== 막힐 때"
cd "$ROOT"
run uv add fastapi
echo; echo '$ uv --version'; echo 'uv --version' | env PATH=/usr/bin:/bin bash -i 2>&1 | grep 'not found'
cd "$ROOT/hello-uv"
run uv init
