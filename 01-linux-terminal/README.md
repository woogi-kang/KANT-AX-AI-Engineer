# 01 · 터미널 기초

> 명령을 칠 때마다 폴더 지도가 어떻게 바뀌는지 보며 터미널을 익혀요. 홈 폴더에 `kant` 폴더를 만들고, 그 안에서 파일을 만들고 옮기고 지우는 데까지 이어서 해요.

| 슬라이드 | 분량 | 이전 모듈 | 다음 모듈 |
| --- | --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/01-linux-terminal/linux-terminal-slides.html) | 34장 · 7개 파트 | 없음 | [02 · Git 기본 흐름](../02-git-basics) |

## 학습 목표

이 모듈을 마치면 다음을 할 수 있어요.

- `pwd`, `ls`, `cd`로 지금 위치를 확인하고 폴더 사이를 옮겨 다녀요.
- 절대 경로와 상대 경로를 구분하고 `.`, `..`, `~`, `/`를 써요.
- `mkdir`, `touch`, `echo`, `mv`, `cp`, `rm`으로 파일과 폴더를 관리해요.
- 마크다운(`.md`) 파일을 만들고 기본 기호를 써요.
- 자주 나는 에러 메시지를 읽고 스스로 고쳐요.

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 1. 개념 잡기 | 3–5 | 터미널, 프롬프트, 폴더 트리 |
| 2. 둘러보기 | 6–9 | `pwd` `ls` `mkdir` `cd` |
| 3. 파일 만들기 | 10–13 | `touch` `echo` `cat`, 마크다운 |
| 4. 경로 | 14–19 | 절대 경로와 상대 경로, `cd ..`, `cd ~` |
| 5. 옮기고 지우기 | 20–27 | `mv` `cp` `rm` `rm -r` `rm -rf` |
| 6. 더 편하게 | 28–30 | `ls -a` `ls -al`, Tab, 위 화살표, Ctrl + C, `clear` |
| 7. 문제 해결 | 31–33 | 자주 보는 에러 3가지 |
| 요약 | 34 | 한 장 요약 |

## 시작하기 전에

| 운영체제 | 여는 프로그램 | 홈 폴더 경로 |
| --- | --- | --- |
| macOS | 터미널 앱 | `/Users/내이름` |
| Windows | Git Bash (Git을 설치하면 함께 설치) | `/c/Users/내이름` |
| Linux | 터미널 | `/home/내이름` |

슬라이드는 Linux 기준이라 홈 폴더가 `/home/kim`으로 나와요. 명령은 세 운영체제에서 똑같이 동작해요.

## 핵심 개념

### 경로 기호

| 기호 | 뜻 |
| :---: | --- |
| `.` | 지금 폴더 |
| `..` | 한 칸 위 폴더 |
| `~` | 내 홈 폴더 |
| `/` | 맨 위 폴더 (루트) |

`/`로 시작하는 경로는 절대 경로라서 어디서 쳐도 같은 곳을 가리켜요. 그 밖의 경로는 지금 위치에서 출발하는 상대 경로예요.

### 마크다운

실습 파일은 `.md`(마크다운)로 만들어요. 마크다운은 기호 몇 개로 꾸미는 텍스트 파일이에요. GitHub과 VS Code 미리보기에서 꾸며진 모습으로 보여요. 이 README도 마크다운이에요.

| 이렇게 쓰면 | 이렇게 보여요 |
| --- | --- |
| `# 제목` | 큰 제목 |
| `## 작은 제목` | 작은 제목 |
| `- 항목` | 점 목록 |
| `1. 항목` | 번호 목록 |
| `**굵게**` | **굵게** |
| 백틱 세 개(```` ``` ````)로 위아래 감싸기 | 코드 블록 |
| `[글자](주소)` | 링크 |

기호 뒤에는 띄어쓰기를 한 칸 넣어요. `#제목`처럼 붙이면 제목이 되지 않아요.

코드 블록은 첫 줄 백틱 뒤에 `bash`처럼 언어 이름을 적으면 GitHub이 색을 입혀 줘요.

````markdown
```bash
cd ~/kant
ls -al
```
````

백틱(`` ` ``)은 한글 키보드에서 숫자 1 왼쪽의 ₩ 키예요. 한/영을 영문으로 바꾸고 눌러요.

## 실습

터미널을 열고 한 줄씩 쳐요. `#` 뒤는 설명이라 치지 않아도 돼요.

### 1. 둘러보기

```bash
pwd                       # 지금 위치
ls                        # 안에 든 것
mkdir kant                # 폴더 만들기
cd kant                   # 들어가기
```

### 2. 파일 만들기

```bash
touch memo.md
echo "# hello" > memo.md
cat memo.md
mkdir notes
ls
```

### 3. 경로

```bash
cd notes                  # 상대 경로
cd ..                     # 한 칸 위로
cd ~/kant/notes           # 홈 폴더에서 출발하는 경로
cd ~                      # 홈 폴더로
cd kant
```

### 4. 옮기고 지우기

```bash
mv memo.md notes/         # 옮기기
cp notes/memo.md plan.md  # 복사하기
mv plan.md todo.md        # 이름 바꾸기
rm todo.md                # 파일 지우기
rm -r notes               # 폴더 지우기
ls
```

### 5. 숨김 파일 보기

```bash
ls -a                     # 점(.)으로 시작하는 숨김 파일까지
ls -al                    # 숨김까지 자세히. 맨 앞이 d면 폴더, -면 파일
```

> **주의** `rm`은 휴지통을 거치지 않아요. 지우기 전에 `pwd`와 `ls`로 위치와 이름을 확인해요.
>
> `rm -rf`는 폴더 안까지 묻지 않고 지우고, 없는 이름을 지워도 에러가 나지 않아요. `rm -rf ~`, `rm -rf /`, `rm -rf *`는 홈 폴더, 컴퓨터 전체, 지금 폴더 안을 통째로 지우니 치지 않아요.

## 명령어 요약

| 명령 | 하는 일 |
| --- | --- |
| `pwd` | 지금 위치 보기 |
| `ls` / `ls -al` | 목록 보기 / 숨김 파일까지 자세히 |
| `cd 경로` | 옮겨 가기 |
| `mkdir 이름` | 폴더 만들기 |
| `touch 이름` | 빈 파일 만들기 |
| `echo "글" > 파일` | 파일에 글 쓰기 |
| `cat 파일` | 파일 내용 보기 |
| `mv 원래 새것` | 옮기기, 이름 바꾸기 |
| `cp 원래 새것` | 복사하기 |
| `rm 파일` / `rm -r 폴더` | 파일 지우기 / 폴더 지우기 |

## 문제 해결

| 메시지 | 원인과 해결 |
| --- | --- |
| `No such file or directory` | 이름 오타이거나 지금 위치에 없어요. `pwd`, `ls`로 확인하고 이름은 Tab으로 자동 완성 |
| `command not found` | 명령 이름 오타예요. 철자가 맞으면 그 프로그램이 설치되지 않은 거예요 |
| `Is a directory` | 폴더에 `rm`을 쳤어요. 폴더는 `rm -r` |
| 폴더가 두 개 생김 | 이름에 띄어쓰기를 넣었어요. `"my folder"`처럼 따옴표로 묶거나 `my-folder`로 지어요 |

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen_scenes.py    터미널과 폴더 지도 장면 생성
  check.js         글자 넘침, 겹침, 여백 검사와 스크린샷
  deckrender.js    export.js와 build_player.js가 같이 쓰는 렌더링 코드
  export.js        PDF 내보내기
  build_player.js  애니메이션이 재생되는 HTML 한 파일 만들기
  icons/           아이콘 (Lucide, ISC 라이선스)
linux-terminal-slides.html  배포용 HTML
linux-terminal-slides.pdf   강사용 PDF
```

폴더 지도가 나오는 장면(`tree-map`, `s*`, `paths`, `special`, `err-*`)은 스크립트를 고친 뒤 다시 만들어요. 나머지 장은 `slides/`에서 바로 고쳐요.

```bash
python3 tools/gen_scenes.py slides
node tools/check.js slides shots                              # 전체 검사 (Playwright 필요)
node tools/check.js slides shots s12-mv                       # 특정 장만
node tools/build_player.js slides linux-terminal-slides.html
node tools/export.js slides linux-terminal-slides.pdf
```

터미널 출력은 bash 5.2, GNU coreutils 9.4에서 실제로 실행해 확인했어요. 프롬프트는 화면을 아끼려고 `~/kant $`처럼 위치만 남겼어요.

</details>

---

[커리큘럼](../README.md) · [다음: 02 · Git 기본 흐름 →](../02-git-basics)
