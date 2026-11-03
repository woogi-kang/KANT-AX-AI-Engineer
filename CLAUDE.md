# 이 레포에서 작업할 때

KANT AX/AI 엔지니어 트랙 수강생에게 공유하는 학습 자료 레포예요. 수강생은 나이와 배경이 다양하고, 대부분 개발이 처음이에요.

## 작업 방식 (Claude와 강사 공통)

1. 작업을 시작하기 전에 `git pull origin main`으로 main을 받아요. 여러 작업이 동시에 같은 파일을 고쳐요.
2. 끝난 작업은 항상 main에 반영해요. 작업 브랜치에만 두지 않아요.
3. README와 CLAUDE.md는 덮어쓰지 말고 합쳐요. 받은 main 위에 내 변경만 더하고, 다른 작업이 넣은 줄은 지우지 않아요.
4. push한 뒤 GitHub 저장소 첫 화면의 README에 변경이 보이는지 확인하고 보고해요. 첫 화면은 기본 브랜치를 보여 주니 기본 브랜치는 main이어야 해요.
5. main에 다 합쳐진 작업 브랜치는 지워요.

## 폴더 규칙

- 자료는 배우는 순서대로 `01-주제`, `02-주제`처럼 두 자리 번호와 영문 소문자 이름으로 만들어요. (예: `01-linux-terminal`, `02-git-basics`, `03-git-branch`, `04-git-diff`, `05-git-graph`, `06-team-repo`, `07-git-restore-stash`, `08-git-merge-ways`, `09-python-uv`, `10-vscode-jupyter`, `11-gh-cli`, `12-python-basics`, `13-python-strings-lists`, `14-python-2d-lists`, `15-python-dict`, `16-python-sets`)
- 폴더마다 수강생이 읽을 `README.md`를 둬요. 무엇을 배우는지, 어떤 순서로 보면 되는지, 꼭 기억할 명령을 적어요.
- 슬라이드가 있는 폴더에는 수강생이 바로 받을 HTML(`주제-slides.html`, 애니메이션 포함)과 PDF(`주제-slides.pdf`)를 같이 둬요. 슬라이드를 고치면 둘 다 다시 만들어요. 만드는 스크립트는 맨 위 `tools/`의 `build_player.js`, `export.js`예요. 챕터 폴더에서 `node ../tools/build_player.js slides 주제-slides.html`처럼 쳐요.
- 새 내용은 만들기 전에 자리부터 정해요. 아래 순서로 처음 맞는 곳에 넣어요.
  1. 이미 있는 챕터의 보강이나 예시면 그 챕터의 파트로 넣어요.
  2. 넣었을 때 덱이 40장을 넘거나 파트가 6개를 넘으면, 같은 주제의 다음 챕터로 나눠요(예: 파이썬 기초 1, 2).
  3. 새 도구나 새 개념이면 맨 뒤 번호로 새 챕터를 만들어요.
  4. 배우는 순서와 상관없이 막혔을 때 보는 자료면 번외로 만들어요.
- main에 올린 챕터의 번호와 폴더 이름은 바꾸지 않아요. 슬라이드 주소(GitHub Pages)와 수강생이 저장한 링크가 깨져요. 새 챕터는 중간에 끼우지 않고 뒤에 붙여요. 챕터를 나눌 때도 앞부분은 원래 폴더에 남겨요.
- 챕터 README가 400줄을 넘으면 챕터를 나눌 때예요.
- 자료 단위는 "챕터"라고 불러요. README 커리큘럼 표와 챕터 README에는 슬라이드 장수(34장 같은 표시)를 적지 않아요. 챕터 README 맨 위 표는 슬라이드, 이전 챕터, 다음 챕터 세 칸이에요.
- README 표에서 내용이 제목보다 짧은 칸(예: `열기`)은 GitHub이 한글 제목을 글자 중간에서 끊어요. 제목과 짧은 셀은 글자 사이에 `&#8288;`(줄바꿈 막는 보이지 않는 문자)를 넣어요. 예: `슬&#8288;라&#8288;이&#8288;드`, `열&#8288;기`
- 슬라이드 HTML 조작은 `tools/build_player.js` 한 곳에서 정해요. 마우스는 화면 좌우 끝 15%를 눌렀을 때만 넘기고, 가운데 클릭과 글자 고르기는 넘기지 않아요. 고정폭 글꼴(JetBrains Mono) 코드 칸에는 복사 버튼이 자동으로 붙어요(터미널 칸은 `$ ` 뒤 명령만). 뒤로 가면 애니메이션이 끝난 화면, `A`로 애니메이션 끄기, 숫자+Enter로 쪽 이동이에요. 조작법을 바꾸면 맨 위 README의 키 표도 같이 고쳐요.
- 모든 챕터가 같이 쓰는 도구(`check.js`, `deckrender.js`, `build_player.js`, `export.js`, `icons/`)는 맨 위 `tools/`에 한 벌만 둬요. 챕터 `tools/`에는 그 챕터만 쓰는 `gen.py`, `demo.sh` 같은 파일만 둬요. 공용 도구를 고치면 모든 덱이 영향을 받으니, 한 덱을 다시 만들어서 전과 같은지 비교해요.
- 정규 챕터에 넣지 않는 보충 자료는 "번외"라고 불러요. `extras/주제`처럼 번호 없이 영문 소문자 이름으로 만들어요. (예: `extras/terminal-path-help`)
  - 번외 폴더도 README, `주제-slides.html`, `주제-slides.pdf`, `tools/`를 챕터와 같은 방식으로 둬요.
  - 번외 README 맨 위 표는 슬라이드, 관련 챕터, 번외 목록 세 칸이에요.
  - 새 번외는 `curriculum.json`의 `extras`에 한 줄 더하고 `python3 tools/build_readme.py`를 쳐요. 맨 위 README의 "번외" 표와 `extras/README.md` 표가 같이 바뀌어요. 커리큘럼 표에는 넣지 않아요.
  - 번외도 수업 규칙과 배포 전 점검을 똑같이 따라요. 아직 안 배운 명령은 관련 챕터를 밝히고 써요.
- 챕터와 번외 목록은 `curriculum.json` 한 곳에서만 고쳐요. `python3 tools/build_readme.py`가 맨 위 커리큘럼 표, 번외 표, 챕터 README 맨 위 표와 맨 아래 이동 링크를 만들어요. 만든 내용은 `<!-- curriculum:이름 -->`과 `<!-- /curriculum:이름 -->` 사이에만 들어가요. 그 사이를 README에서 직접 고치지 않아요. 올리기 전에 `python3 tools/build_readme.py --check`가 조용히 끝나는지 봐요.
- 커리큘럼 표는 챕터, 분류, 한 줄 목표, 핵심 명령, 슬라이드 다섯 칸이에요. 분류는 터미널, Git, GitHub, 파이썬 중 하나예요. 한 줄 목표는 "~해요"로 끝나는 한 문장이에요. 핵심 명령은 다섯 개 안팎만 적고, 나머지는 챕터 README 명령어 요약에 적어요.
- 새 챕터 README는 `templates/chapter-README.md`를 복사해서 시작해요. 절 순서는 학습 목표, 시작하기 전에, 구성, 핵심 개념, 실습, 명령어 요약, 문제 해결, 강사용이에요.
- HTML 링크는 GitHub Pages 주소(`https://woogi-kang.github.io/KANT-AX-AI-Engineer/폴더/파일.html`)로 걸어요. README에는 PDF 다운로드 링크를 넣지 않아요(PDF 파일은 강사용으로 계속 만들어 둬요).

## 수업 규칙 (자료 내용)

- `git push -u`, `--set-upstream`, `push.autoSetupRemote`는 쓰지 않아요. push와 pull은 항상 `git push origin main`, `git pull origin main`처럼 끝까지 적어요.
- pull 설정은 `git config --global pull.rebase false`(merge로 합치기) 하나로 통일해요. `git pull --rebase`, `pull.rebase true`, `pull.ff only`는 쓰지 않아요. 08은 이 설정들을 비교로만 보여 주고, 설정을 바꾸게 하지 않아요. pull이 나오는 덱은 이 설정이 없을 때 나는 `fatal: Need to specify how to reconcile divergent branches.`와 해결을 함께 보여 줘요.
- 팀 실습의 사람과 색은 kim(파랑 #2459C9), lee(초록 #1F8A4C), park(주황 #B26A00), GitHub(보라 #5A3BB8)로 맞춰요. 팀 레포 주소 예시는 `https://github.com/kim/team-intro.git`이에요.
- GitHub과 비교할 땐 `git fetch origin` 뒤 `git log --oneline`과 `git log --oneline origin/main`을 봐요.
- `git log`에 `--graph`, `--all` 옵션은 쓰지 않아요. 자료, README, 슬라이드 모두 같아요.
- `git restore`와 `git stash`는 07 챕터에서만 다뤄요. 01~06 자료에는 넣지 않아요.
- `git rebase`, `git merge --squash`, `git merge --no-ff`, `git branch -D`는 08 챕터부터 다뤄요. 01~07 자료에는 넣지 않아요. rebase 실습은 연습용 저장소에서 push 전 커밋에만 하고, push한 브랜치와 main에서는 rebase하지 않는다고 함께 알려 줘요.
- 커밋은 `git add 파일` 뒤 `git commit -m "..."`으로 써요. `git commit -am`처럼 add를 합친 옵션은 배우지 않았으니 쓰지 않아요.
- 커밋 메시지는 Conventional Commits 형식(`feat:`, `fix:`, `docs:` …)으로 써요. 이 레포에 커밋할 때도 같아요.
- 터미널 출력은 실제 git으로 실행해 보고 그대로 옮겨요. 지어낸 출력은 넣지 않아요.
- VS Code Git Graph는 결과를 그림으로 확인할 때만 써요. checkout, merge, reset 같은 명령은 Git Graph 메뉴 대신 터미널에서 쳐요.
- 브랜치를 가리키는 말은 모든 덱에서 "이름표"로 통일해요. 꼬리표, 라벨처럼 다른 말을 섞지 않아요.
- gh(GitHub CLI)는 11 챕터부터 다뤄요. 설치는 macOS `brew install gh`, Windows `winget install --id GitHub.cli -e`로 적어요. 로그인은 `gh auth login`에서 GitHub.com, HTTPS, Authenticate Git Yes, Login with a web browser를 골라요. SSH와 토큰 붙여 넣기는 쓰지 않아요. `gh repo create`는 `이름 --public --source=. --remote=origin`으로 만들고 `--push`는 붙이지 않아요(upstream을 설정해요). push는 `git push origin main`으로 직접 쳐요. `gh pr create` 전에 `git push origin 브랜치`로 먼저 올려요. 레포 지우기 권한은 `gh auth refresh -h github.com -s delete_repo`로 더해요. gh 출력은 11의 `tools/demo.sh`(mock GitHub 앞에서 실제 gh 실행)로 만들어 옮겨요.
- 파이썬 프로젝트는 uv로 만들어요. `uv init`, `uv run 파일`, `uv add 패키지`, `uv remove 패키지`, `uv sync`를 써요. `pip install`, `python -m venv`, `requirements.txt`는 09에서 예전 방식 비교로만 보여 주고 따라 치게 하지 않아요. 가상환경 직접 켜기는 uv가 만든 `.venv`에 한해 보여 줘요. macOS, Linux는 `source .venv/bin/activate`, Windows Git Bash는 `source .venv/Scripts/activate`, PowerShell은 `.venv\Scripts\activate`, 끄기는 `deactivate`예요. 실습 명령은 그래도 `uv run`을 기본으로 적어요. 다른 자료에 `pip install 패키지`가 나오면 `uv add 패키지`로 바꿔 적어요.
- Jupyter 노트북은 VS Code의 Python, Jupyter 확장(Microsoft)으로 열어요. 커널 패키지는 `uv add --dev ipykernel`로 넣고, 노트북 커널은 프로젝트의 `.venv`를 골라요. VS Code 알림의 Install 버튼(pip 설치)은 쓰지 않아요. 노트북 단축키는 Windows와 Mac을 나란히 적고, Mac 셀 실행은 VS Code 기본값인 `control+Enter`로 적어요(10 챕터).
- uv 설치는 macOS `brew install uv`, Windows `winget install --id=astral-sh.uv -e`로 적어요. curl, PowerShell 설치 스크립트는 쓰지 않아요.
- fastapi 예시는 `uv add fastapi`로만 넣어요. `fastapi[standard]`, uvicorn, `fastapi dev`로 서버 켜기는 쓰지 않고, `import fastapi` 뒤 `print("fastapi 버전:", fastapi.__version__)`처럼 불러오는 데까지만 보여 줘요.
- 파이썬 예제는 수업에서 배운 범위로 적어요. f-string(`f"...{변수}"`)은 13의 1파트(문자열과 출력)에서 처음 배워요. 그 앞의 자료(09~12)에는 쓰지 않아요. `%` 포맷팅과 `format()`은 13의 1파트에서 f-string과 나란히 읽는 법만 보여 주고, 새 예제는 f-string으로 적어요. `input()`은 아직 배우지 않았으니 쓰지 않아요. 값을 보여 줄 땐 `print(변수)`, `print("설명", 변수)`나 셀 마지막 줄의 변수 이름으로 보여 줘요. 변수 할당, 변수 타입과 타입 바꾸기(`int()`, `float()`, `str()`), 사칙연산, 비교와 논리연산(`and`, `or`, `not`)은 12에서 배워요. 문자열 인덱스와 슬라이싱, `print()`의 `sep` `end`, 칸 수·소수점·천 단위 콤마 포맷팅, 리스트와 튜플(`[ ]`, `( )`, 번호 두 개로 꺼내기, `[시작:끝:간격]` 자르기, 메서드 `append` `insert` `remove` `pop` `count` `index` `sort` `extend` `reverse` `copy` `clear`, `sorted()`, `split` `join`, `in`, `len` `sum` `max` `min`, `list()` `tuple()`, `a, b, c = 튜플`로 꺼내 담기)은 13에서 배워요. `for` 반복문(`for 이름 in 리스트:`, `for a, b, c in 튜플리스트:`)은 13의 2파트에서 처음 배워요. 그 앞의 예제에는 `for`를 쓰지 않아요. `in`과 `not in`(리스트, 튜플, 문자열에서 True, False로 묻기)과 2차원 리스트(`scores[1][2]`, `len(scores[0])`, `for row in scores:`)는 14에서 정리해요. 딕셔너리(`{키: 값}`, `menu["latte"]`로 꺼내기, `KeyError`, `get()`과 기본값, `None`, 같은 문법으로 추가와 수정, 키는 겹치지 않고 같은 키에 넣으면 덮어쓰기, `del`, `pop`, 키를 보는 `in`, `keys` `values` `items`, `for k, v in d.items():`, 값이 리스트인 딕셔너리, 딕셔너리 리스트)는 15에서 배워요. `setdefault`, `zip()`, 딕셔너리 컴프리헨션, JSON, 키에 리스트를 못 쓰는 이유는 15에서 다루지 않아요. 집합(`{1, 2, 3}`, `set(리스트)`로 중복 없애기, 빈 집합 `set()`, 순서가 없어서 `sorted()`로 줄 세우기(`sort()`는 없어서 `AttributeError`, `reverse=True`, `sorted(set(리스트))`), `set("banana")`가 글자로 쪼개지는 함정, 숫자·문자열·튜플은 담고 리스트는 못 담기(딕셔너리 키도 같은 규칙), `add` `remove` `discard` `update` `pop` `clear`, `in`, 번호로 못 꺼내기, `for`, 합집합 `|` 교집합 `&` 차집합 `-`와 `union` `intersection` `difference`)은 16에서 배워요. 대칭차집합 `^`, `issubset`, frozenset은 16에서 다루지 않아요. 16은 `set(리스트)`, `discard`, `|` `&` `-`를 원래 긴 코드와 나란히 보여 줘요. `if`가 없는 긴 코드(`for`와 `add`)는 따라 치고, `if`가 필요한 긴 코드는 "참고" 칸에 읽기만 하게 둬요. 집합을 `print`한 순서는 실행할 때마다 달라서, 실습에서 순서가 보여야 하는 곳은 `sorted()`로 찍어요. `if` 문은 아직 배우지 않았으니 16까지의 예제에 넣지 않아요. 단, 15의 get 비교 장처럼 줄인 메서드의 원래 긴 방법은 "참고, 읽기만"으로 보여 줄 수 있어요. `for` 안에서도 `if`는 쓰지 않아요.
- 파이썬 실행은 `uv run main.py`로 적어요. `python main.py`는 가상환경을 켠 상태, 예전 방식, 오류 예시에서만 써요. `.venv`는 GitHub에 올리지 않고, `pyproject.toml`, `uv.lock`, `.python-version`은 올려요.

## 챕터 설계 틀

새 챕터와 번외는 주제(파이썬, 프론트엔드, 백엔드, RAG 등)와 상관없이 이 틀로 만들어요. 기초부터 쌓아서 실제 상황 예제로 끝나게 하려는 틀이에요.

### 1. 시작 전 범위 정하기

- 위 수업 규칙에서 지금까지 배운 것과 아직 안 배운 것을 먼저 확인해요.
- 이번 챕터에서 처음 나오는 개념을 목록으로 적어요.
- 깊은 내용은 "뺄 것" 목록에 따로 적어 두고 덱에 넣지 않아요. 다음 챕터나 번외로 미뤄요.
- 덱은 40장 이하로 잡아요. 넘으면 위 폴더 규칙대로 챕터를 나눠요.
- 범위가 정해지면 수업 규칙에 "몇 챕터에서 무엇을 배우고 무엇은 다루지 않는다"를 한 줄 더해요.

### 2. 덱 흐름 (모든 챕터 공통)

덱은 항상 이 순서로 짜요.

1. 왜 필요한가: 지금 아는 것만으로는 불편하거나 안 되는 장면 하나를 보여 줘요.
2. 큰 그림: 이 개념이 전체 시스템의 어디에 있는지 그림 한 장으로 보여 줘요. (예: 브라우저, 서버, DB 사이에 요청이 오가는 그림. 질문이 검색을 거쳐 LLM으로 가는 그림.)
3. 가장 작은 동작 예제: 제일 짧은 코드나 명령으로 한 번 돌려 봐요.
4. 구성 요소 하나씩: 개념, 메서드, 옵션을 장마다 하나씩 그림과 실제 결과로 보여 줘요.
5. 이전 내용과 연결하고 비교하기: 앞 챕터에서 배운 것과 무엇이 같고 다른지 표나 그림으로 보여 줘요.
6. 자주 나는 오류와 함정: 실제 오류 메시지를 그대로 옮기고 고치는 법을 붙여요.
7. 실제 상황 예제 2~3개: 앞에서 배운 것을 섞어서 풀어요. 소재는 카페 주문처럼 트랙 전체에서 이어지는 것으로 골라요.
8. 정리 한 장: 언제 쓰는지 표와 다음 챕터로 이어지는 내용을 적어요.

분야마다 3, 4번에서 보여 주는 결과만 바꿔요.

| 분야 | 3, 4번에서 보여 줄 것 |
| --- | --- |
| 터미널, Git | 실제로 친 명령과 터미널 출력, 바뀐 상태 그림 |
| 파이썬 | 코드와 셀 실행 결과, 값이 담긴 칸 그림 |
| 프론트엔드 | 화면 캡처, 코드를 바꾸면 화면이 어떻게 바뀌는지 |
| 백엔드 | 요청과 응답 흐름 그림, curl이나 브라우저 결과 |
| RAG, AI | 데이터가 지나가는 단계 그림, 단계별 중간 결과 |

### 3. 장마다 지킬 것

- 개념 하나에 장 하나를 써요.
- 장마다 코드나 명령, 실제 실행 결과, 그림을 같이 둬요. 결과는 직접 실행해서 옮겨요.
- 메서드와 옵션은 "언제 쓰는지" 예시까지 붙여요.
- 줄여 쓰는 문법과 메서드(`get`, 슬라이싱 등)는 원래 긴 방법과 나란히 보여 줘요. 긴 방법에 아직 안 배운 문법(`if` 등)이 들어가면 "참고, 읽기만"으로 표시하고 따라 치게 하지 않아요(예: 15의 `menu["cakee"] if "cakee" in menu else 5000`과 `menu.get("cakee", 5000)`).
- 오류 예시는 실제 오류 메시지를 그대로 써요.
- 집합 순서처럼 실행할 때마다 달라지는 출력은 수강생 화면이 슬라이드와 다를 수 있다고 그 장에 적어요. 슬라이드를 다시 만들어도 같게 나오도록 만드는 스크립트에서 고정해요(16은 `PYTHONHASHSEED`).

### 4. 끝나고 점검

- 범위 밖 문법이나 명령을 쓰지 않았는지 봐요.
- 덱이 위 2번 흐름 순서대로인지 봐요.
- 챕터 README, `curriculum.json`, 수업 규칙을 덱에 맞춰 고쳐요.
- 그다음 아래 "배포 전 점검"을 그대로 따라요.

## 배포 전 점검

main에 올리기 전에 매번 아래를 확인해요.

1. 새로 넣은 장이 배우는 순서와 "챕터 설계 틀"의 덱 흐름에 맞는 자리인지 봐요. 아직 안 배운 명령이나 개념이 먼저 나오면 안 돼요.
2. 같은 덱과 다른 덱(01, 02, 03 …)의 내용, 용어, 해시, 발표자 노트의 앞 장 참조와 어긋나지 않는지 봐요.
3. 위 수업 규칙에 어긋나는 명령이 없는지 검색해요. (`-u`, `--graph`, `--all`, `commit -am`, 07 밖의 `restore`, `stash`, 08 앞의 `rebase`, `--squash`, `--no-ff`, 09 비교 장 밖의 `pip install`)
4. 챕터 README(구성의 쪽 번호, 명령어 요약, 실습, 문제 해결), `curriculum.json`(한 줄 목표, 핵심 명령), 맨 위 README(과정 규칙)를 슬라이드에 맞춰 고쳐요. 그다음 `python3 tools/build_readme.py`로 표를 다시 만들어요.
5. README의 실습 명령을 순서대로 쳤을 때 실제로 동작하는지 확인해요.
6. HTML과 PDF를 다시 만들어요.

## 한국어 글쓰기 지침 (korean-humanizer)

자료, README, 커밋 메시지, 발표자 노트 등 이 레포에 들어가는 한국어는 모두 이 기준으로 써요. 다 쓴 뒤 아래 목록으로 한 번 더 훑어서 고쳐요.

**말투**
- 수강생에게 말하듯 해요체로 통일해요. 한 문서 안에서 "~합니다"와 "~해요"를 섞지 않아요. (README 표나 목록의 짧은 항목은 명사형으로 끝내도 돼요.)
- 한 문장에는 한 가지만 말해요. 쉼표로 세 개 이상 이어 붙이면 문장을 나눠요.
- 주어가 뻔하면 생략해요. "여러분은", "우리는", "사용자는"을 문장마다 붙이지 않아요.

**번역투와 AI 티 나는 표현 고치기**

| 이렇게 쓰지 말고 | 이렇게 |
| --- | --- |
| ~에 대해 알아보겠습니다 | ~를 봐요 / 바로 본론 |
| ~을 통해 ~할 수 있습니다 | ~로 ~해요 |
| ~하는 것이 중요합니다 | 왜 중요한지 바로 말하기 |
| ~되어집니다, ~되어진 | ~돼요, ~된 |
| ~라고 할 수 있습니다, ~인 것입니다 | ~예요 |
| 그것은, 이를, 이러한 | 가리키는 대상을 다시 적기 |
| 다양한, 효율적인, 핵심적인, 강력한, 혁신적인 | 구체적인 사실이나 숫자로 바꾸기, 아니면 빼기 |
| 결론적으로, 요약하자면, 이처럼 (마무리 문단) | 빼기. 마지막 문장은 할 일로 끝내기 |
| ~에 있어서, ~에 있어 | ~에서, ~할 때 |
| 가지고 있다 | 있다 |

**모양**
- 긴 대시(—)와 화살표 연쇄(A → B → C → D)로 문장을 잇지 않아요. 순서는 번호 목록으로 써요. (명령 흐름을 보여 주는 짧은 표기 `add → commit`은 괜찮아요.)
- 굵은 글씨는 한 단락에 한 번까지만 써요.
- 이모지와 느낌표는 쓰지 않아요. 경고가 필요하면 무엇이 왜 위험한지 한 줄로 적어요.
- 영어 용어는 처음 나올 때 한 번만 풀어 쓰고(예: 스테이징 영역(대기실)), 그 뒤로는 같은 말을 계속 써요.
- 같은 내용을 제목, 본문, 요약에서 반복하지 않아요.

**마지막 점검**
1. 소리 내어 읽었을 때 강사가 실제로 할 말처럼 들리나요?
2. 빼도 뜻이 그대로인 문장이 있나요? 있으면 빼요.
3. 수강생이 따라 칠 명령은 복사해서 바로 실행되나요?
