#!/bin/bash
# Runs real Claude Code (claude -p) on a tiny cafe project and keeps the tool calls and answers in tools/log/.
# Usage: bash tools/demo.sh   (needs a logged-in claude, uv, python3, jq)
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
LOG="$HERE/log"; mkdir -p "$LOG"
W="${DEMO_DIR:-/tmp/agent-demo}/cafe-order"
unset UV_NATIVE_TLS
# Inside a cloud Claude Code session the CLAUDE_* variables of the outer session change how the inner one loads
# project settings and hooks. Drop them (keeping only the login) so the inner run behaves like a fresh terminal.
U=$(env | grep -oE '^CLAUDE[A-Z_]*' | grep -vE 'OAUTH|SESSION_INGRESS|ACCOUNT_UUID|ORGANIZATION_UUID|USER_EMAIL' | sed 's/^/-u /' | tr '\n' ' ')
cc() { env $U claude "$@" < /dev/null 2>>"$LOG/stderr.txt"; }
: > "$LOG/stderr.txt"

fresh() {
  rm -rf "$W"; mkdir -p "$W"; cd "$W"
  cat > main.py <<'PY'
prices = {"아메리카노": 4500, "라떼": 5000, "케이크": 6000}
order = ["아메리카노", "라떼", "라떼"]

total = 0
for item in order:
    total = prices[item]

print("합계:", total)
PY
  git init -q . && git add main.py && git -c user.name=kim -c user.email=kim@example.com commit -qm "feat: 주문 합계"
}

ask='main.py를 실행하면 합계가 이상해. 고쳐 줘.'
tools_log() { grep "^{" "$1" | jq -c 'select(.type=="assistant") | .message.content[] | select(.type=="tool_use") | {name, input}'; }
final() { grep "^{" "$1" | jq -r 'select(.type=="result") | .result'; }

echo "== A. no tools"
fresh
cc -p "$ask" --tools "" > "$LOG/a-notools.txt" 2>&1
cat "$LOG/a-notools.txt"

echo "== B. tools, agent loop"
fresh
uv run main.py > "$LOG/b-before.txt" 2>&1; cat "$LOG/b-before.txt"
cc -p --permission-mode acceptEdits --allowedTools "Bash(uv run *)" --output-format stream-json --verbose "$ask" > "$LOG/b-loop.jsonl" 2>&1
tools_log "$LOG/b-loop.jsonl" | tee "$LOG/b-tools.txt"
final "$LOG/b-loop.jsonl" | tee "$LOG/b-final.txt"
git diff > "$LOG/b-diff.txt"; cat "$LOG/b-diff.txt"
uv run main.py > "$LOG/b-after.txt" 2>&1; cat "$LOG/b-after.txt"

echo "== C. CLAUDE.md rule"
fresh
cat > CLAUDE.md <<'MD'
# 카페 주문 프로젝트

- 실행은 `uv run main.py`로 해요.
- 돈은 천 단위 콤마와 "원"을 붙여 출력해요. 예: `print(f"합계: {total:,}원")`
- 고친 뒤에는 꼭 다시 실행해서 결과를 확인해요.
MD
cc -p --permission-mode acceptEdits --allowedTools "Bash(uv run *)" --output-format stream-json --verbose "$ask" > "$LOG/c-rule.jsonl" 2>&1
tools_log "$LOG/c-rule.jsonl" | tee "$LOG/c-tools.txt"
uv run main.py > "$LOG/c-after.txt" 2>&1; cat "$LOG/c-after.txt"

echo "== D. same rule in AGENTS.md only"
fresh
cat > AGENTS.md <<'MD'
# 카페 주문 프로젝트

- 실행은 `uv run main.py`로 해요.
- 돈은 천 단위 콤마와 "원"을 붙여 출력해요. 예: `print(f"합계: {total:,}원")`
- 고친 뒤에는 꼭 다시 실행해서 결과를 확인해요.
MD
cc -p --permission-mode acceptEdits --allowedTools "Bash(uv run *)" --output-format stream-json --verbose "$ask" > "$LOG/d-agents.jsonl" 2>&1
tools_log "$LOG/d-agents.jsonl" | tee "$LOG/d-tools.txt"
uv run main.py > "$LOG/d-after.txt" 2>&1; cat "$LOG/d-after.txt"

echo "== E. hook blocks rm -rf"
fresh
mkdir -p build .claude/hooks && touch build/old.txt
cat > .claude/hooks/block_rm.py <<'PY'
import json
import sys

data = json.load(sys.stdin)
command = data["tool_input"].get("command", "")

if "rm -rf" in command:
    print("rm -rf는 막아 두었어요. 지울 파일을 하나씩 적어 주세요.", file=sys.stderr)
    sys.exit(2)
PY
cat > .claude/settings.json <<'JS'
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "python3 .claude/hooks/block_rm.py" }
        ]
      }
    ]
  }
}
JS
echo '{"tool_name": "Bash", "tool_input": {"command": "rm -rf build"}}' | python3 .claude/hooks/block_rm.py > "$LOG/e-manual.txt" 2>&1; echo "종료 코드: $?" >> "$LOG/e-manual.txt"; cat "$LOG/e-manual.txt"
cc -p --allowedTools "Bash" --output-format stream-json --verbose "rm -rf build 명령으로 build 폴더를 지워 줘." > "$LOG/e-hook.jsonl" 2>&1
tools_log "$LOG/e-hook.jsonl" | tee "$LOG/e-tools.txt"
grep "^{" "$LOG/e-hook.jsonl" | jq -r 'select(.type=="user") | .message.content[]? | select(.type=="tool_result") | .content | if type=="array" then .[].text else . end' | tee "$LOG/e-results.txt"
final "$LOG/e-hook.jsonl" | tee "$LOG/e-final.txt"
ls -R build > "$LOG/e-ls.txt" 2>&1; cat "$LOG/e-ls.txt"
env $U claude --version > "$LOG/version.txt"

# 원본 기록(jsonl)에는 실행 환경 정보가 들어 있어서 지우고, 위에서 뽑은 txt만 남겨요.
rm -f "$LOG"/*.jsonl "$LOG/stderr.txt"
sed -i "s|${DEMO_DIR:-/tmp/agent-demo}|/tmp/agent-demo|g" "$LOG"/*.txt
