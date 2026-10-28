# KANT AX/AI 엔지니어 트랙 · 학습 자료

KANT AX/AI 엔지니어 트랙의 공식 학습 자료 저장소예요. 터미널과 Git처럼 개발을 시작할 때 매일 쓰는 도구를 다뤄요. 명령을 칠 때마다 무엇이 바뀌는지 애니메이션 슬라이드로 보여 줘요.

## 커리큘럼

| 모듈 | 주제 | 다루는 명령 | 슬라이드 |
| :---: | --- | --- | --- |
| [01](./01-linux-terminal) | 터미널 기초 | `pwd` `ls` `cd` `mkdir` `touch` `mv` `cp` `rm` | [열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/01-linux-terminal/linux-terminal-slides.html) · 34장 |
| [02](./02-git-basics) | Git 기본 흐름 | `init` `add` `commit` `push` `pull` `clone` `reset` `revert` | [열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/02-git-basics/git-basics-slides.html) · 43장 |
| [03](./03-git-branch) | Git 브랜치와 협업 | `branch` `checkout` `merge`, Pull Request, 충돌 해결 | [열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/03-git-branch/git-branch-slides.html) · 54장 |

모듈은 번호 순서대로 이어져요. 앞 모듈에서 만든 폴더와 저장소를 다음 모듈에서 그대로 써요.

## 학습 방법

1. 커리큘럼 표의 **열기**를 눌러 슬라이드를 브라우저에서 봐요.
2. 모듈 폴더의 `README.md`를 열고 실습 명령을 터미널에서 한 줄씩 따라 쳐요.
3. 막히면 모듈 README의 문제 해결 표에서 같은 메시지를 찾아요.

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

슬라이드의 출력은 bash 5.2, GNU coreutils 9.4, git 2.43에서 실제로 실행한 결과예요. 커밋 해시는 실행할 때마다 달라요.

## 과정 규칙

모든 모듈이 같은 규칙을 따라요.

| 항목 | 규칙 |
| --- | --- |
| push, pull | `git push origin main`, `git pull origin main`처럼 원격과 브랜치를 끝까지 적어요. `-u`는 쓰지 않아요 |
| 원격과 비교 | `git fetch origin` 뒤에 `git log --oneline`, `git log --oneline origin/main`. `--graph`, `--all`은 쓰지 않아요 |
| 커밋 메시지 | [Conventional Commits](https://www.conventionalcommits.org/ko/v1.0.0/) 형식: `feat:` `fix:` `docs:` … |
| 브랜치 이름 | `feature/login`, `fix/12-login-error`, `docs/login-guide`처럼 `타입/하는-일` |

## 저장소 구조

```
.
├── 01-linux-terminal/
├── 02-git-basics/
├── 03-git-branch/
│   ├── README.md                 모듈 안내 (학습 목표, 실습, 문제 해결)
│   ├── git-branch-slides.html    슬라이드 (브라우저용)
│   ├── git-branch-slides.pdf     슬라이드 (강사용 인쇄본)
│   ├── slides/                   슬라이드 원본 (한 장에 한 파일)
│   └── tools/                    슬라이드 생성, 검사, 내보내기 스크립트
└── CLAUDE.md                     자료 작성 규칙
```

## 자료를 고칠 때

- 슬라이드를 고치면 모듈의 `tools/`로 HTML과 PDF를 다시 만들어요. 명령은 모듈 README의 강사용 절에 있어요.
- 새 모듈은 `04-주제` 형식으로 폴더를 만들고 커리큘럼 표에 한 줄을 더해요.
- 글쓰기와 폴더 규칙은 [CLAUDE.md](./CLAUDE.md)를 따라요.
