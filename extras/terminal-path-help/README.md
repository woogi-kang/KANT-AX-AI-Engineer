# 번외 · 터미널 환경에서 적응하기

> 정규 챕터에 들어가지 않는 번외 자료예요. 터미널에서 지금 위치를 왜 계속 확인해야 하는지, 명령을 잊었을 때 `-h`와 `--help`로 어떻게 스스로 찾는지 봐요.

| 슬&#8288;라&#8288;이&#8288;드 | 관련 챕터 | 번외 목록 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/extras/terminal-path-help/terminal-path-help-slides.html) | [01 · 터미널 기초](../../01-linux-terminal), [02 · Git 기본 흐름](../../02-git-basics), [09 · uv로 파이썬 시작하기](../../09-python-uv) | [번외 목록](../README.md) |

01을 본 뒤라면 언제 봐도 돼요. git 장면은 02와 06에서 만든 `team-intro`, uv 장면은 09에서 만든 `hello-uv`를 그대로 써요.

## 이런 분께 맞아요

- 명령을 쳤는데 `No such file or directory`, `not a git repository`가 자주 떠요.
- 탐색기에서는 폴더를 찾겠는데 터미널에서는 어디에 있는지 모르겠어요.
- 명령이나 옵션 이름이 기억나지 않아서 매번 검색해요.

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 3 | 탐색기는 그림으로, 터미널은 글자로 위치를 알려 줘요 |
| 1. 탐색기와 터미널 맞춰 보기 | 4–12 | 더블클릭과 `cd`, 위로와 `cd ..`, 뒤로와 `cd -`, 홈과 `cd ~`, `open .` |
| 2. 위치가 맞아야 명령이 동작해요 | 13–19 | 같은 명령 다른 결과, 홈 폴더 `git init` 되돌리기, 확인 습관, `git status` 읽기, 프롬프트 읽기 |
| 3. 이름에 담긴 관례 | 20–25 | 명령 이름의 뜻, 대시 하나와 둘, 자주 보는 옵션과 예외, origin과 main |
| 4. 도움말로 스스로 찾기 | 26–34 | Usage 기호, 옵션 목록 읽기, git과 uv 도움말, 설명서 화면에서 `q`, 오타 힌트 |
| 정리 | 35–36 | 막힐 때 표, 한 장 요약 |

## 핵심 개념

### 탐색기 버튼과 터미널 명령

| 탐색기 | 터미널 | 하는 일 |
| --- | --- | --- |
| 폴더 더블클릭 | `cd 폴더이름` | 들어가기 |
| ↑ 위 폴더 | `cd ..` | 한 칸 위로 |
| ← 뒤로 | `cd -` | 바로 전 폴더로 |
| → 앞으로 | `cd -` 한 번 더 | 두 폴더 오가기 |
| ⌂ 홈 | `cd ~` | 홈 폴더로 |
| 주소 줄 | `pwd` | 지금 위치 전체 |

탐색기와 터미널을 같은 폴더에 띄우려면 Mac은 `open .`, Windows Git Bash는 `explorer .`를 쳐요.

### 치기 전에 보고, 친 뒤에 다시 보기

1. 어디? 프롬프트나 `pwd`
2. 무엇이? `ls`
3. 명령 치기
4. 잘 됐나? `ls`, `git status`

`cd`, `mkdir`, `git add`는 성공해도 아무것도 출력하지 않아요. 4번으로 결과를 확인해요.

### 옵션 이름의 약속

대시 하나 뒤에는 한 글자(`-a`), 대시 둘 뒤에는 단어(`--all`)를 적어요. 뜻은 같아요. 한 글자 옵션은 `ls -al`처럼 붙여 써요.

약속일 뿐이라 예외가 있어요. `ls -h`는 도움말이 아니라 크기를 읽기 쉽게 보여 주는 옵션이에요. 헷갈리면 `--help`부터 쳐요.

### 도움말 기호

| 기호 | 뜻 |
| :---: | --- |
| `[ ]` | 넣어도 되고 빼도 돼요 |
| `< >` | 내 값으로 바꿔 적어요 |
| `...` | 여러 개 적을 수 있어요 |
| `\|` | 둘 중 하나만 골라요 |

## 실습

터미널을 열고 한 줄씩 쳐요. `#` 뒤는 설명이라 치지 않아도 돼요. 09의 `~/kant/hello-uv`, 06의 `~/kant/team-intro`가 있다고 생각하고 적었어요. 폴더가 없으면 1번만 따라 하고 2번부터는 내 프로젝트 폴더로 바꿔 쳐요.

### 1. 탐색기와 같이 움직이기

```bash
cd ~/kant
open .                    # Mac. Windows Git Bash는 explorer .
cd hello-uv               # 탐색기에서도 hello-uv를 더블클릭
cd ..                     # 위로
cd -                      # 뒤로. 간 곳을 한 줄 출력해요
cd -                      # 한 번 더 치면 다시 kant
cd ~                      # 홈
```

### 2. 같은 명령, 다른 폴더

```bash
cd ~/kant
uv run main.py            # error: Failed to spawn: `main.py`
git status                # fatal: not a git repository
cd hello-uv
uv run main.py            # Hello from hello-uv!
cd ../team-intro
git status                # On branch main
```

### 3. 도움말 찾아가기

```bash
ls --help                 # Mac은 man ls, 나올 땐 q
git --help                # 자주 쓰는 git 명령 목록
git commit -h             # commit 옵션표. -m을 찾아봐요
git push -h               # 첫 줄의 <repository>, <refspec> 보기
cd ~/kant/hello-uv
uv --help                 # uv 명령 목록
uv tree -h                # tree 사용법
uv tree
```

> **주의** `git commit --help`, `man ls`는 설명서 화면을 열어요. 명령이 안 먹는 것처럼 보이면 `q`를 눌러 나와요. Windows Git Bash는 `--help`가 브라우저로 열려요.

## 명령어 요약

| 명령 | 하는 일 |
| --- | --- |
| `pwd` / `ls` | 지금 위치 / 안에 든 것 |
| `cd -` | 바로 전 폴더로 |
| `open .` / `explorer .` | 지금 폴더를 탐색기로 열기 (Mac / Windows Git Bash) |
| `명령 --help` | 도움말 |
| `git 명령 -h` | git 명령의 짧은 옵션표 |
| `git 명령 --help` | git 명령의 설명서 전체 |
| `uv 명령 -h` | uv 명령 도움말 (`--help`와 같아요) |
| `q` | 설명서 화면 나가기 |

## 문제 해결

| 메시지 | 원인과 해결 |
| --- | --- |
| `fatal: not a git repository` | git 저장소 폴더 밖이에요. `pwd`로 보고 `cd`로 저장소 폴더에 들어가요 |
| `error: Failed to spawn: main.py` | `main.py`가 없는 폴더예요. `ls`로 보고 `cd hello-uv` |
| 화면 맨 아래에 `:`이나 `(END)`만 보여요 | 설명서 화면이에요. `q` |
| 홈 폴더에서 `git status`가 동작해요 | 홈에서 `git init`을 쳤어요. `pwd`로 홈인지 보고 `ls -a`로 `.git`을 확인한 뒤 `rm -rf .git` (슬라이드 16쪽) |
| `git: 'stauts' is not a git command` | 오타예요. 아래 `The most similar command is` 줄의 이름으로 다시 쳐요 |

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py           모든 장 생성 (탐색기, 터미널, 폴더 지도 장면)
  demo.sh          슬라이드에 넣은 출력을 실제로 실행 (/home/kim을 만들어서 root로 실행)
  check.js         글자 넘침, 겹침, 여백 검사와 스크린샷
  deckrender.js    export.js와 build_player.js가 같이 쓰는 렌더링 코드
  export.js        PDF 내보내기
  build_player.js  애니메이션이 재생되는 HTML 한 파일 만들기
  icons/           아이콘 (Lucide, ISC 라이선스)
terminal-path-help-slides.html  배포용 HTML
terminal-path-help-slides.pdf   강사용 PDF
```

```bash
bash tools/demo.sh > /tmp/path-help.log 2>&1   # 실제 출력 확인
python3 tools/gen.py slides
node tools/check.js slides shots
node tools/build_player.js slides terminal-path-help-slides.html
node tools/export.js slides terminal-path-help-slides.pdf
```

터미널 출력은 bash 5.2, GNU coreutils 9.4, git 2.43, uv 0.11.32에서 실제로 실행했어요. 터미널 창에서 보이는 모양대로 `ls`는 가로로 옮겼어요. Mac의 `ls --help`, 설명서 화면, `open .`, `explorer .`는 이 환경에서 실행할 수 없어서 출력을 옮기지 않았어요.

</details>

---

[커리큘럼](../../README.md) · [번외 목록](../README.md)
