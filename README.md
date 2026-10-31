# KANT AX/AI 엔지니어 트랙 · 학습 자료

KANT AX/AI 엔지니어 트랙의 공식 학습 자료 저장소예요. 터미널, Git, 파이썬 프로젝트 도구 uv처럼 개발을 시작할 때 매일 쓰는 도구를 다뤄요. 명령을 칠 때마다 무엇이 바뀌는지 애니메이션 슬라이드로 보여 줘요.

## 커리큘럼

| 챕터 | 다루는 명령 | 슬&#8288;라&#8288;이&#8288;드 |
| --- | --- | --- |
| [01 · 터미널 기초](./01-linux-terminal) | `pwd` `ls` `cd` `mkdir` `touch` `mv` `cp` `rm` | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/01-linux-terminal/linux-terminal-slides.html) |
| [02 · Git 기본 흐름](./02-git-basics) | `init` `add` `commit` `push` `pull` `clone` `reset` `revert` | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/02-git-basics/git-basics-slides.html) |
| [03 · Git 브랜치와 협업](./03-git-branch) | `branch` `checkout` `switch` `merge`, `reset`, Pull Request, 충돌 해결 | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/03-git-branch/git-branch-slides.html) |
| [04 · Git diff로 확인하기](./04-git-diff) | `diff` `diff --staged` `show`, 브랜치 비교, `.gitignore` | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/04-git-diff/git-diff-slides.html) |
| [05 · VS Code Git Graph로 기록 보기](./05-git-graph) | Git Graph 설치, 점·이름표·HEAD·origin/main 읽기, 명령 뒤 그림 확인 | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/05-git-graph/git-graph-slides.html) |
| [06 · 팀 레포에서 같이 작업하고 충돌 풀기](./06-team-repo) | Collaborator 초대, push 거절 뒤 `pull`, 자동 합치기, pull 충돌 해결, 팀 규칙, 브랜치와 PR 케이스 8가지 | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/06-team-repo/team-repo-slides.html) |
| [07 · 커밋 전 변경 취소하기와 잠깐 보관하기](./07-git-restore-stash) | `restore` `restore --staged` `stash` `stash list` `stash pop` `stash drop` | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/07-git-restore-stash/git-restore-stash-slides.html) |
| [08 · 갈라진 기록 합치는 방법 비교하기](./08-git-merge-ways) | fast-forward, `merge --no-ff`, `rebase`, `merge --squash`, pull 설정 세 가지, PR Merge 버튼 세 가지 | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/08-git-merge-ways/git-merge-ways-slides.html) |
| [09 · uv로 파이썬 시작하기](./09-python-uv) | 예전 방식(venv, pip)과 나란히 비교, `brew`·`winget`으로 uv 설치, `uv init` `uv run` `uv add` `uv remove` `uv tree` `uv sync`, 가상환경 켜기(`activate`), fastapi 넣고 빼기, VS Code Jupyter(`uv add --dev ipykernel`) | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/09-python-uv/python-uv-slides.html) |
| [10 · VS Code에서 Jupyter 노트북 쓰기](./10-vscode-jupyter) | 셀 실행 키 세 가지(`Shift+Enter` 등), 코드 셀과 마크다운 셀, 실행 번호, Restart와 Run All, 명령 모드와 편집 모드, 마크다운 셀로 변수 이름 규칙과 컨벤션 정리, 자료형과 `type()`, Windows·Mac 단축키 표 | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/10-vscode-jupyter/vscode-jupyter-slides.html) |

챕터는 번호 순서대로 이어져요. 앞 챕터에서 만든 폴더와 저장소를 다음 챕터에서 그대로 써요.

## 번외

정규 챕터와 따로 보는 보충 자료예요. 순서 없이 필요한 것만 골라 봐요. 목록은 [extras](./extras)에도 있어요.

| 제&#8288;목 | 다루는 내용 | 슬&#8288;라&#8288;이&#8288;드 |
| --- | --- | --- |
| [터미널 환경에 적응하기](./extras/terminal-path-help) | 탐색기와 터미널 맞춰 보기(`cd ..` `cd -` `cd ~`), 위치에 따라 달라지는 명령, `-h`와 `--help`, origin과 main 이름의 관례, git과 uv 도움말 읽기 | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/extras/terminal-path-help/terminal-path-help-slides.html) |

## 학습 방법

1. 커리큘럼 표의 **열기**를 눌러 슬라이드를 브라우저에서 봐요.
2. 챕터 폴더의 `README.md`를 열고 실습 명령을 터미널에서 한 줄씩 따라 쳐요.
3. 막히면 챕터 README의 문제 해결 표에서 같은 메시지를 찾아요.

| 키 | 동작 |
| --- | --- |
| `→` `Space` | 다음 |
| `←` | 이전 |
| `N` | 발표자 노트 열고 닫기 |
| `F` | 전체 화면 |

주소 끝에 `#12`처럼 번호를 붙이면 그 장부터 열려요.

## 실습 환경

| 운영체제 | 터미널 | 비고 |
| --- | --- | --- |
| macOS | 터미널 앱 | 기본 설치 |
| Windows | Git Bash | [Git for Windows](https://git-scm.com/download/win)를 설치하면 함께 설치 |
| Linux | 기본 터미널 | 기본 설치 |

슬라이드의 출력은 bash 5.2, GNU coreutils 9.4, git 2.43, uv 0.11.32(Python 3.14)에서 실제로 실행한 결과예요. 커밋 해시는 실행할 때마다 달라요.

## 과정 규칙

모든 챕터가 같은 규칙을 따라요.

| 항목 | 규칙 |
| --- | --- |
| push, pull | `git push origin main`, `git pull origin main`처럼 원격과 브랜치를 끝까지 적어요. `-u`는 쓰지 않아요 |
| pull 설정 | 처음 한 번 `git config --global pull.rebase false`. pull은 merge로 합쳐요. `pull.rebase true`, `pull.ff only`는 08에서 비교로만 봐요 |
| 원격과 비교 | `git fetch origin` 뒤에 `git log --oneline`, `git log --oneline origin/main`. `--graph`, `--all`은 쓰지 않아요 |
| 그림으로 보기 | VS Code의 Git Graph로 결과만 확인해요. checkout, merge, reset은 Git Graph 메뉴 대신 터미널에서 쳐요 |
| 커밋 | `git add 파일` 뒤 `git commit -m "..."`. `-am`은 쓰지 않아요 |
| 커밋 전 되돌리기 | `git restore`, `git stash`는 07에서 배워요. 01~06 자료에는 나오지 않아요 |
| 합치는 방법 | `rebase`, `merge --squash`, `--no-ff`는 08에서 배워요. rebase는 push 전 내 브랜치에만 쓰고, push한 브랜치와 main에서는 쓰지 않아요 |
| 커밋 메시지 | [Conventional Commits](https://www.conventionalcommits.org/ko/v1.0.0/) 형식: `feat:` `fix:` `docs:` … |
| 브랜치 이동 | 슬라이드는 `git checkout`으로 보여 줘요. 같은 일을 하는 `git switch`도 03에서 소개해요 |
| 파이썬 프로젝트 | `uv init`으로 만들고 `uv run`으로 실행해요. 패키지는 `uv add`, `uv remove`. 가상환경을 직접 켤 땐 `source .venv/bin/activate`(Windows Git Bash는 `.venv/Scripts/activate`). uv 설치는 Mac `brew install uv`, Windows `winget install --id=astral-sh.uv -e`. `pip install`은 09에서 예전 방식 비교로만 봐요 |
| 브랜치 이름 | `feature/login`, `fix/12-login-error`, `docs/login-guide`처럼 `타입/하는-일` |

## 저장소 구조

```
.
├── 01-linux-terminal/
├── 02-git-basics/
├── 03-git-branch/
│   ├── README.md                 챕터 안내 (학습 목표, 실습, 문제 해결)
│   ├── git-branch-slides.html    슬라이드 (브라우저용)
│   ├── git-branch-slides.pdf     슬라이드 (강사용 인쇄본)
│   ├── slides/                   슬라이드 원본 (한 장에 한 파일)
│   └── tools/                    슬라이드 생성, 검사, 내보내기 스크립트
├── 04-git-diff/
├── 05-git-graph/
├── 06-team-repo/
├── 07-git-restore-stash/
├── 08-git-merge-ways/
├── 09-python-uv/
├── 10-vscode-jupyter/
├── extras/                       번외 자료 (주제마다 폴더 하나)
│   └── terminal-path-help/
└── CLAUDE.md                     자료 작성 규칙
```

## 자료를 고칠 때

- 슬라이드를 고치면 챕터의 `tools/`로 HTML과 PDF를 다시 만들어요. 명령은 챕터 README의 강사용 절에 있어요.
- 새 챕터는 `11-주제`처럼 다음 번호로 폴더를 만들고 커리큘럼 표에 한 줄을 더해요.
- 번외는 `extras/주제` 폴더에 번호 없이 만들고, 위 번외 표와 `extras/README.md`에 한 줄씩 더해요.
- 글쓰기와 폴더 규칙은 [CLAUDE.md](./CLAUDE.md)를 따라요.
