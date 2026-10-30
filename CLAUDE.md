# 이 레포에서 작업할 때

KANT AX/AI 엔지니어 트랙 수강생에게 공유하는 학습 자료 레포예요. 수강생은 나이와 배경이 다양하고, 대부분 개발이 처음이에요.

## 작업 방식 (Claude와 강사 공통)

1. 작업을 시작하기 전에 `git pull origin main`으로 main을 받아요. 여러 작업이 동시에 같은 파일을 고쳐요.
2. 끝난 작업은 항상 main에 반영해요. 작업 브랜치에만 두지 않아요.
3. README와 CLAUDE.md는 덮어쓰지 말고 합쳐요. 받은 main 위에 내 변경만 더하고, 다른 작업이 넣은 줄은 지우지 않아요.
4. push한 뒤 GitHub 저장소 첫 화면의 README에 변경이 보이는지 확인하고 보고해요. 첫 화면은 기본 브랜치를 보여 주니 기본 브랜치는 main이어야 해요.
5. main에 다 합쳐진 작업 브랜치는 지워요.

## 폴더 규칙

- 자료는 배우는 순서대로 `01-주제`, `02-주제`처럼 두 자리 번호와 영문 소문자 이름으로 만들어요. (예: `01-linux-terminal`, `02-git-basics`, `03-git-branch`, `04-git-diff`, `05-git-graph`, `06-team-repo`, `07-git-restore-stash`, `08-git-merge-ways`, `09-python-uv`, `10-vscode-jupyter`)
- 폴더마다 수강생이 읽을 `README.md`를 둬요. 무엇을 배우는지, 어떤 순서로 보면 되는지, 꼭 기억할 명령을 적어요.
- 슬라이드가 있는 폴더에는 수강생이 바로 받을 HTML(`주제-slides.html`, 애니메이션 포함)과 PDF(`주제-slides.pdf`)를 같이 둬요. 슬라이드를 고치면 둘 다 다시 만들어요. 만드는 스크립트는 `02-git-basics/tools/`의 `build_player.js`, `export.js`예요.
- 자료 단위는 "챕터"라고 불러요. README 커리큘럼 표와 챕터 README에는 슬라이드 장수(34장 같은 표시)를 적지 않아요. 챕터 README 맨 위 표는 슬라이드, 이전 챕터, 다음 챕터 세 칸이에요.
- README 표에서 내용이 제목보다 짧은 칸(예: `열기`)은 GitHub이 한글 제목을 글자 중간에서 끊어요. 제목과 짧은 셀은 글자 사이에 `&#8288;`(줄바꿈 막는 보이지 않는 문자)를 넣어요. 예: `슬&#8288;라&#8288;이&#8288;드`, `열&#8288;기`
- 강사용 도구(생성·검사·PDF 내보내기 스크립트)는 해당 폴더의 `tools/`에 둬요.
- 레포 맨 위 `README.md`의 목차에 새 폴더와 HTML 링크를 추가해요. HTML은 GitHub Pages 주소(`https://woogi-kang.github.io/KANT-AX-AI-Engineer/폴더/파일.html`)로 걸어요. README에는 PDF 다운로드 링크를 넣지 않아요(PDF 파일은 강사용으로 계속 만들어 둬요).

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
- 파이썬 프로젝트는 uv로 만들어요. `uv init`, `uv run 파일`, `uv add 패키지`, `uv remove 패키지`, `uv sync`를 써요. `pip install`, `python -m venv`, `requirements.txt`는 09에서 예전 방식 비교로만 보여 주고 따라 치게 하지 않아요. 가상환경 직접 켜기는 uv가 만든 `.venv`에 한해 보여 줘요. macOS, Linux는 `source .venv/bin/activate`, Windows Git Bash는 `source .venv/Scripts/activate`, PowerShell은 `.venv\Scripts\activate`, 끄기는 `deactivate`예요. 실습 명령은 그래도 `uv run`을 기본으로 적어요. 다른 자료에 `pip install 패키지`가 나오면 `uv add 패키지`로 바꿔 적어요.
- Jupyter 노트북은 VS Code의 Python, Jupyter 확장(Microsoft)으로 열어요. 커널 패키지는 `uv add --dev ipykernel`로 넣고, 노트북 커널은 프로젝트의 `.venv`를 골라요. VS Code 알림의 Install 버튼(pip 설치)은 쓰지 않아요. 노트북 단축키는 Windows와 Mac을 나란히 적고, Mac 셀 실행은 VS Code 기본값인 `control+Enter`로 적어요(10 챕터).
- uv 설치는 macOS `brew install uv`, Windows `winget install --id=astral-sh.uv -e`로 적어요. curl, PowerShell 설치 스크립트는 쓰지 않아요.
- fastapi 예시는 `uv add fastapi`로만 넣어요. `fastapi[standard]`, uvicorn, `fastapi dev`로 서버 켜기는 쓰지 않고, `import fastapi` 뒤 `print("fastapi 버전:", fastapi.__version__)`처럼 불러오는 데까지만 보여 줘요.
- 파이썬 예제는 수업에서 배운 범위로 적어요. f-string(`f"...{변수}"`)과 `input()`은 아직 배우지 않았으니 쓰지 않아요. 값을 보여 줄 땐 `print(변수)`, `print("설명", 변수)`나 셀 마지막 줄의 변수 이름으로 보여 줘요.
- 파이썬 실행은 `uv run main.py`로 적어요. `python main.py`는 가상환경을 켠 상태, 예전 방식, 오류 예시에서만 써요. `.venv`는 GitHub에 올리지 않고, `pyproject.toml`, `uv.lock`, `.python-version`은 올려요.

## 배포 전 점검

main에 올리기 전에 매번 아래를 확인해요.

1. 새로 넣은 장이 배우는 순서에 맞는 자리인지 봐요. 아직 안 배운 명령이나 개념이 먼저 나오면 안 돼요.
2. 같은 덱과 다른 덱(01, 02, 03 …)의 내용, 용어, 해시, 발표자 노트의 앞 장 참조와 어긋나지 않는지 봐요.
3. 위 수업 규칙에 어긋나는 명령이 없는지 검색해요. (`-u`, `--graph`, `--all`, `commit -am`, 07 밖의 `restore`, `stash`, 08 앞의 `rebase`, `--squash`, `--no-ff`, 09 비교 장 밖의 `pip install`)
4. 챕터 README(구성의 쪽 번호, 명령어 요약, 실습, 문제 해결)와 맨 위 README(다루는 명령, 과정 규칙)를 슬라이드에 맞춰 고쳐요.
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
