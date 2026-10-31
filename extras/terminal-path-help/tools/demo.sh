#!/usr/bin/env bash
# Builds /home/kim like the course (kant/hello-uv from 09, kant/team-intro from 06) and runs
# every command the deck shows, so the slides carry real output.
# Needs root (it makes /home/kim). Usage: bash tools/demo.sh > /tmp/path-help.log 2>&1
set -u
if [ -e /home/kim ]; then echo "/home/kim already exists. Remove it first."; exit 1; fi
unset VIRTUAL_ENV UV_NATIVE_TLS
export HOME=/home/kim NO_COLOR=1 GIT_PAGER=cat PAGER=cat UV_CACHE_DIR=$(mktemp -d)
[ -f /root/.ccr/ca-bundle.crt ] && export UV_SYSTEM_CERTS=1
BARE=$(mktemp -d)/team-intro.git
mkdir -p /home/kim/Desktop /home/kim/Documents /home/kim/kant
touch /home/kim/Desktop/photo.png /home/kim/Documents/report.pdf
git config --global user.name kim
git config --global user.email kim@example.com
git config --global init.defaultBranch main
git config --global pull.rebase false
run() { echo; echo "\$ $*"; eval "$@" 2>&1; }

# setup (not shown): hello-uv from 09, team-intro cloned from GitHub in 06
cd /home/kim/kant
uv init -q hello-uv
(cd hello-uv && uv sync -q)
rm -f hello-uv/uv.lock
git init -q --bare "$BARE"
git clone -q "$BARE" team-intro 2>/dev/null
(cd team-intro && echo "# team-intro" > README.md && git add README.md && git commit -q -m "docs: README 추가" && git push -q origin main && git remote set-url origin https://github.com/kim/team-intro.git)

echo "== part 1: moving around"
cd /home/kim
run pwd
run ls
run cd kant
run ls
run cd hello-uv
run ls
run cd ..
run pwd
run cd -
run cd -
run 'cd ~'
run pwd

echo "== part 2: same command, different folder"
cd /home/kim/kant
run pwd
run uv run main.py
run git status
run cd hello-uv
run uv run main.py
run cd ../team-intro
run git status
run echo '"# kim"' '>' kim.md
run git status
rm kim.md

echo "== part 2: git init in the home folder"
cd /home/kim
run pwd
run git init
run git status
run ls -a
run rm -rf .git
run git status

echo "== part 3: names"
cd /home/kim/kant/team-intro
run git remote -v
run git branch
run cd ../hello-uv
run ls -h
run git -v
run uv -V
run git push -h '|' head -1

echo "== part 4: help"
cd /home/kim/kant/hello-uv
run ls --help '|' head -8
run git --help
run git commit -h
run uv --help '|' head -22
run uv add -h '|' head -6
run uv tree -h '|' head -3
run uv tree
run git stauts
run uv ad fastapi
