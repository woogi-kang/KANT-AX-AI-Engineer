# 번외 · AI 에이전트 하네스 만들기

> 정규 챕터에 들어가지 않는 번외 자료예요. AI 코딩 에이전트에게 규칙, 도구, 권한, 검사를 붙여 주는 "하네스"를 Claude Code로 봐요. 같은 생각이 Codex CLI, Antigravity CLI에서도 그대로 통한다는 것과, AI 엔지니어링이 프롬프트에서 하네스까지 넓어진 흐름도 같이 봐요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 관련 챕터 | 번외 목록 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/extras/agent-harness/agent-harness-slides.html) · [PDF 받기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/extras/agent-harness/agent-harness-slides.pdf) | [09 · uv로 파이썬 시작하기](../../09-python-uv) | [번외 목록](../README.md) |

<!-- /curriculum:top -->

09에서 uv로 파이썬 프로젝트를 만들어 봤다면 언제 봐도 돼요. 예제는 카페 주문 합계를 내는 `main.py` 하나짜리 프로젝트예요.

## 이런 분께 맞아요

- AI 에이전트에게 일을 시켰는데 고치고 나서 확인을 안 하고 끝내요.
- 매번 같은 부탁("uv run으로 실행해 줘")을 다시 적어요.
- 에이전트가 지우면 안 되는 파일을 지울까 봐 불안해요.
- CLAUDE.md, AGENTS.md, 스킬, MCP, 훅 같은 말이 무엇이 다른지 헷갈려요.

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 1. 왜 필요한가 | 3–6 | 도구 없는 모델과 Claude Code 비교, 하네스 여섯 칸, 에이전트 고리, 실제로 돈 고리 |
| 2. AI 엔지니어링의 흐름 | 7–12 | 프롬프트, 컨텍스트, 루프, 그래프, 하네스 엔지니어링과 각 단계가 부딪힌 벽 |
| 3. 규칙과 컨텍스트 | 13–18 | CLAUDE.md, 규칙 몇 줄의 효과, 좋은 규칙, 컨텍스트 창, 다른 도구 비교, AGENTS.md |
| 4. 도구와 권한 | 19–23 | 도구 설명, MCP, 권한 모드와 allow deny, 훅, 훅이 rm -rf를 막은 실제 실행 |
| 5. 검사, 스킬, 서브에이전트 | 24–27 | 검사 스크립트, 스킬, 서브에이전트, 무엇을 어디에 둘까 |
| 6. 함정과 실제 예 | 28–31 | 함정 여섯 가지, 이 레포의 하네스, 카페 프로젝트에 쌓기, 도구를 바꿀 때 |
| 정리 | 32 | 한 장 요약 |

## 핵심 개념

### 하네스는 모델을 뺀 나머지예요

같은 모델이라도 둘레에 무엇을 붙이느냐로 결과가 달라져요. 이 덱은 여섯 칸으로 나눠요.

| 칸 | Claude Code에서 | 하는 일 |
| --- | --- | --- |
| 규칙 파일 | `CLAUDE.md` (없으면 `AGENTS.md`) | 매번 지킬 약속 |
| 도구 | Read, Edit, Bash, MCP | 읽고, 고치고, 실행하기 |
| 루프 | 에이전트 고리 | 될 때까지 다시 하기 |
| 권한과 훅 | `.claude/settings.json` | 묻기, 바로 하기, 막기 |
| 검사 | 테스트, 검사 스크립트 | 맞았는지 기계가 확인 |
| 나눠 맡기기 | 서브에이전트 | 큰 일을 나눠서 요약만 받기 |

### 프롬프트에서 하네스까지

| 단계 | 다듬는 것 | 부딪힌 벽 |
| --- | --- | --- |
| 프롬프트 | 질문 한 문장 | 모델이 모르는 것은 잘 물어도 못 답해요 |
| 컨텍스트 | 모델에게 보여 줄 자료 | 한 번 답하면 끝이라 실행해서 확인을 못 해요 |
| 루프 | 도구를 쓰며 반복하기 | 길어지면 길을 잃고 매번 가는 길이 달라요 |
| 그래프 | 단계, 갈림길, 나눠 맡기기 | 큰 흐름은 사람이 미리 그려요 |
| 하네스 | 넷을 묶은 환경 전체 | |

연도 순서라기보다 다듬는 범위가 넓어진 순서예요. LangGraph 같은 그래프 도구는 2024년부터 있었어요.

### 부탁과 강제는 달라요

- 규칙 파일은 부탁이에요. 모델이 잊을 수 있어요.
- 권한의 deny와 훅은 강제예요. 코드가 늘 돌아서 모델이 잊어도 막혀요.
- 검사 스크립트는 확인이에요. "다 했어요"를 믿지 않고 기계가 봐요.

### 다른 도구에서도 같아요

| | Claude Code | Codex CLI | Antigravity CLI |
| --- | --- | --- | --- |
| 실행 명령 | `claude` | `codex` | `agy` |
| 규칙 파일 | `CLAUDE.md` (없으면 `AGENTS.md`) | `AGENTS.md` | `GEMINI.md`, `AGENTS.md` |
| 스킬 폴더 | `.claude/skills` | `.agents/skills` | `.agents/skills` |
| 외부 도구 연결 | MCP | MCP | MCP |

여러 도구를 같이 쓰면 공통 규칙은 `AGENTS.md`에 두고, `CLAUDE.md` 첫 줄에 `@AGENTS.md`를 적어 불러와요. 2026년 11월 기준이에요.

## 실습

Claude Code는 유료 구독이나 API 키가 있어야 로그인돼요. 설치는 macOS `brew install --cask claude-code`, Windows `winget install Anthropic.ClaudeCode`예요. 계정이 없으면 슬라이드의 실제 실행 결과를 따라 읽기만 해도 돼요.

### 1. 연습 프로젝트 만들기

```bash
mkdir -p ~/kant
cd ~/kant
uv init cafe-order
cd cafe-order
```

`main.py`를 아래처럼 바꿔요. 일부러 넣은 버그가 있어요(`+=` 자리에 `=`).

```python
prices = {"아메리카노": 4500, "라떼": 5000, "케이크": 6000}
order = ["아메리카노", "라떼", "라떼"]

total = 0
for item in order:
    total = prices[item]

print("합계:", total)
```

```bash
uv run main.py            # 합계: 5000 (원래는 14500이어야 해요)
```

### 2. 규칙 파일 없이 부탁하기

```bash
claude
```

`main.py를 실행하면 합계가 이상해. 고쳐 줘.`라고 적어요. 모델이 무엇으로 실행하려는지 봐요. `python3 main.py`로 실행하려고 하면 규칙이 없어서예요.

### 3. CLAUDE.md 다섯 줄 쓰기

`/exit`로 나와서 `main.py`를 1번의 버그 있는 코드로 다시 바꿔요. 그다음 프로젝트 폴더에 `CLAUDE.md`를 만들어요.

```markdown
# 카페 주문 프로젝트

- 실행은 `uv run main.py`로 해요.
- 돈은 천 단위 콤마와 "원"을 붙여 출력해요. 예: `print(f"합계: {total:,}원")`
- 고친 뒤에는 꼭 다시 실행해서 결과를 확인해요.
```

`claude`를 다시 켜고 같은 부탁을 해요. 이번에는 `uv run main.py`로 확인하고 `합계: 14,500원`으로 끝나요.

### 4. 창과 권한 살펴보기

```text
/context                  # 창에 무엇이 얼마나 찼는지
Shift+Tab                 # 권한 모드 바꾸기
/clear                    # 새 대화로
```

## 명령어 요약

| 명령, 파일 | 하는 일 |
| --- | --- |
| `claude` | Claude Code 켜기 |
| `claude -p "부탁"` | 한 번만 답하고 끝내기 (스크립트에서 쓰기) |
| `CLAUDE.md` | 매번 읽는 규칙 파일 |
| `@AGENTS.md` | CLAUDE.md 안에서 AGENTS.md 불러오기 |
| `/context` `/compact` `/clear` | 창 보기, 요약하기, 새로 시작 |
| `Shift+Tab` | 권한 모드 바꾸기 |
| `.claude/settings.json` | allow, deny, 훅 설정 |
| `claude mcp add` | MCP 서버 붙이기 |
| `.claude/skills/이름/SKILL.md` | 필요할 때 읽는 절차 |
| `.claude/agents/이름.md` | 서브에이전트 |

## 문제 해결

| 증상 | 원인과 해결 |
| --- | --- |
| AGENTS.md를 고쳤는데 모르는 척해요 | CLAUDE.md가 있으면 AGENTS.md는 안 읽어요. CLAUDE.md 첫 줄에 `@AGENTS.md` |
| 고치고 확인 없이 끝내요 | 실행 명령을 모르거나 허락이 없어요. 규칙에 명령을 적고 allow에 더해요 |
| "지우지 마"라고 적었는데 지웠어요 | 규칙은 부탁이에요. deny나 훅으로 막아요 |
| 앞에서 정한 걸 잊어요 | 창이 차서 대화가 요약됐어요. 오래 지킬 약속은 CLAUDE.md에 적어요 |
| `This command requires approval` | allow에 없는 명령이에요. 맞는 명령이면 allow에 더해요 |
| `PreToolUse:Bash hook error` | 훅이 막았어요. 뒤에 붙은 이유를 읽고 다른 방법으로 해요 |

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py           모든 장 생성
  demo.sh          claude -p를 카페 프로젝트에서 실제로 실행해 tools/log/에 남겨요
  log/             실제 실행에서 뽑은 도구 호출과 마지막 답
agent-harness-slides.html  배포용 HTML
agent-harness-slides.pdf   슬라이드 PDF
```

장 배치는 Stageshow 원칙을 따라요. 장마다 주인공 하나를 크게 두고, 설명은 지시선과 밑줄로 붙여요. 실제 실행 장(6, 14, 18, 23쪽)은 줄 스포트라이트와 밑줄로 한 줄씩 짚고, 고리 그림은 점이 길을 따라 돌아요. 흐름 장은 같은 갈색으로 묶고, 하네스 점수는 숫자 하나만 크게 세워요. 글자가 한 자씩 찍히는 효과는 쓰지 않아요.

명령은 이 폴더에서 쳐요.

```bash
DEMO_DIR=/tmp/agent-demo bash tools/demo.sh    # 실제 실행 (로그인된 claude, uv, jq 필요)
python3 tools/gen.py slides
node ../../tools/check.js slides shots
node ../../tools/boxcheck.js slides > tools/log/boxcheck.txt
node ../../tools/build_player.js slides agent-harness-slides.html
node ../../tools/export.js slides agent-harness-slides.pdf
```

출력은 Claude Code 2.1.331로 실제로 실행했어요. 모델 답은 실행할 때마다 조금씩 달라요. 클라우드 세션 안에서 `claude`를 다시 부르면 바깥 세션의 `CLAUDE_*` 환경 변수 때문에 프로젝트 훅을 읽지 않아요. `demo.sh`는 로그인 변수만 남기고 나머지를 지운 뒤 `< /dev/null`로 실행해요. 원본 기록(jsonl)에는 실행 환경 정보가 들어 있어서 남기지 않고, 도구 호출과 마지막 답만 txt로 남겨요. 스킬 단계(30쪽)는 실행하지 않은 예시예요.

</details>

---

<!-- curriculum:nav -->

[커리큘럼](../../README.md) · [번외 목록](../README.md)

<!-- /curriculum:nav -->
