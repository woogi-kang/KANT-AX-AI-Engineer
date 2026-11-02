#!/usr/bin/env bash
# Runs every gh and git command the deck shows, so the slides carry real output.
# gh cannot log in to the real github.com from a script, so github.com and api.github.com
# point to tools/mock_github.py on this machine for the run (a self-signed certificate).
# gh 2.89 and git run unchanged; only the answers from "GitHub" come from the mock.
# Needs root (edits /etc/hosts, listens on 443, makes /home/kim), openssl, python3 with pexpect.
# Usage: bash tools/demo.sh > /tmp/gh-cli.log 2>&1          (slides)
#        bash tools/demo.sh practice > /tmp/gh-practice.log 2>&1 (README 실습 1~5)
set -eu
if [ -e /home/kim ]; then echo "/home/kim already exists. Remove it first."; exit 1; fi
TOOLS=$(cd "$(dirname "$0")" && pwd)
WORK=$(mktemp -d)
cd "$WORK"
openssl req -x509 -newkey rsa:2048 -nodes -keyout ca.key -out ca.crt -days 2 -subj "/CN=demo-ca" 2>/dev/null
openssl req -newkey rsa:2048 -nodes -keyout srv.key -out srv.csr -subj "/CN=github.com" 2>/dev/null
printf "subjectAltName=DNS:github.com,DNS:api.github.com\n" > ext
openssl x509 -req -in srv.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out srv.crt -days 2 -extfile ext 2>/dev/null
cat srv.crt ca.crt > chain.crt
cp /etc/hosts hosts.bak
echo "127.0.0.1 github.com api.github.com" >> /etc/hosts
mkdir -p repos
python3 "$TOOLS/mock_github.py" "$WORK/repos" "$WORK" 2> mock.log &
MOCK=$!
trap 'cp "$WORK/hosts.bak" /etc/hosts; kill $MOCK 2>/dev/null' EXIT
sleep 1
GH_DEMO_CA="$WORK/ca.crt" GH_DEMO_REPOS="$WORK/repos" python3 "$TOOLS/${1:-demo}.py"
