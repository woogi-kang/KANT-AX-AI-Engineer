#!/usr/bin/env bash
# Runs every command of the uv deck in a fresh folder and prints the real output.
# Usage: bash tools/demo.sh /tmp/uv-demo > /tmp/uv-demo.log 2>&1
# uv's own cache and Python downloads go inside the folder, so the first run downloads Python
# like a student's computer with no Python installed.
set -u
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

echo "===== 4부 add / remove"
run uv add requests
run cat pyproject.toml
run "head -3 uv.lock"
run uv tree
cat > main.py <<'PY'
import requests


def main():
    r = requests.get("https://api.github.com")
    print("상태 코드:", r.status_code)


if __name__ == "__main__":
    main()
PY
run cat main.py
run uv run main.py
run uv remove requests
run cat pyproject.toml
run uv run main.py
run uv add requests
run uv run python --version

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
run pip install requests
run 'pip freeze > requirements.txt'
run cat requirements.txt
run python main.py
run pip uninstall -y requests
run pip freeze
run deactivate
run python3 main.py

echo "===== 막힐 때"
cd "$ROOT"
run uv add requests
echo; echo '$ uv --version'; echo 'uv --version' | env PATH=/usr/bin:/bin bash -i 2>&1 | grep 'not found'
cd "$ROOT/hello-uv"
run uv init
