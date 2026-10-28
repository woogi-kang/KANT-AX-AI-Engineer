# 01. 터미널 기초

명령을 칠 때마다 폴더 지도가 어떻게 바뀌는지 따라가면서 터미널을 익혀요. 홈 폴더에 `kant` 폴더를 만들고, 그 안에서 파일을 만들고 옮기고 지우는 데까지 한 번에 이어서 봐요.

## 슬라이드 받기

| 형식 | 받기 | 이럴 때 |
| --- | --- | --- |
| HTML (애니메이션 포함) | [브라우저에서 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/01-linux-terminal/linux-terminal-slides.html) | 클릭하면 바로 열려요. 키보드 →, ← 로 넘겨요 |
| PDF (32장) | [바로 받기](https://github.com/woogi-kang/KANT-AX-AI-Engineer/raw/main/01-linux-terminal/linux-terminal-slides.pdf) · [GitHub에서 보기](./linux-terminal-slides.pdf) | 인쇄하거나 휴대폰으로 볼 때 |

HTML은 인터넷에 연결돼 있어야 글꼴이 제대로 보여요. PDF에는 애니메이션이 끝난 모습이 한 장씩 담겨 있어요.

## 터미널 열기

| 컴퓨터 | 여는 프로그램 | 홈 폴더 주소 |
| --- | --- | --- |
| Mac | 터미널 앱 | `/Users/내이름` |
| Windows | Git Bash (Git을 설치하면 같이 깔려요) | `/c/Users/내이름` |
| Linux | 터미널 | `/home/내이름` |

슬라이드는 Linux 기준이라 홈 폴더가 `/home/kim`으로 나와요. 명령은 세 컴퓨터에서 똑같이 동작해요.

## 먼저 기호 네 개를 기억해요

| 기호 | 뜻 |
| --- | --- |
| `.` | 지금 폴더 |
| `..` | 한 칸 위 폴더 |
| `~` | 내 홈 폴더 |
| `/` | 맨 위 폴더 (루트) |

`/`로 시작하는 경로는 절대 경로예요. 어디서 쳐도 같은 곳을 가리켜요. 그 밖의 경로는 지금 위치에서 출발하는 상대 경로예요.

## 마크다운 기호

실습 파일은 `.md`(마크다운)로 만들어요. 마크다운은 글자 사이에 기호 몇 개를 넣어 꾸미는 텍스트 파일이에요. GitHub과 VS Code 미리보기에서 꾸며진 모습으로 보여요. 이 README도 마크다운이에요.

| 이렇게 쓰면 | 이렇게 보여요 |
| --- | --- |
| `# 제목` | 큰 제목 |
| `## 작은 제목` | 작은 제목 |
| `- 항목` | 점 목록 |
| `1. 항목` | 번호 목록 |
| `**굵게**` | **굵게** |
| `` `코드` `` | `코드` |
| `[글자](주소)` | 누르면 주소로 가는 링크 |

기호 뒤에는 띄어쓰기를 한 칸 넣어요. `#제목`처럼 붙이면 제목이 되지 않아요.

## 슬라이드 순서

| 파트 | 쪽 | 다루는 것 |
| --- | --- | --- |
| 1. 개념 잡기 | 3–5 | 터미널, 프롬프트, 폴더 트리 |
| 2. 둘러보기 | 6–9 | `pwd`, `ls`, `mkdir`, `cd` |
| 3. 파일 만들기 | 10–13 | `touch`, `echo`, `cat`, 마크다운 |
| 4. 경로 | 14–19 | 절대 경로와 상대 경로, `cd ..`, `cd ~` |
| 5. 옮기고 지우기 | 20–25 | `mv`, `cp`, `rm`, `rm -r` |
| 6. 더 편하게 | 26–28 | `ls -a`, `ls -al`, Tab, 위 화살표, Ctrl + C, `clear` |
| 7. 막힐 때 | 29–31 | 자주 보는 에러 3가지 |

마지막 32쪽은 한 장 요약이에요.

## 따라 해 보기

슬라이드의 실습을 순서대로 모았어요. 터미널을 열고 한 줄씩 쳐요. `#` 뒤는 설명이라 치지 않아도 돼요.

**둘러보기**

```bash
pwd                       # 지금 위치
ls                        # 안에 든 것
mkdir kant                # 폴더 만들기
cd kant                   # 들어가기
```

**파일 만들기**

```bash
touch memo.md
echo "# hello" > memo.md
cat memo.md
mkdir notes
ls
```

**경로**

```bash
cd notes                  # 상대 경로
cd ..                     # 한 칸 위로
cd ~/kant/notes           # 홈 폴더에서 출발하는 경로
cd ~                      # 홈 폴더로
cd kant
```

**옮기고 지우기**

```bash
mv memo.md notes/        # 옮기기
cp notes/memo.md plan.md
mv plan.md todo.md      # 이름 바꾸기
rm todo.md               # 파일 지우기
rm -r notes               # 폴더 지우기
ls
```

**숨김 파일 보기**

```bash
ls -a                     # 점(.)으로 시작하는 숨김 파일까지
ls -al                    # 숨김까지 자세히. 맨 앞이 d면 폴더, -면 파일
```

`rm`은 휴지통을 거치지 않아요. 지우기 전에 `pwd`와 `ls`로 위치와 이름을 확인해요.

## 막혔을 때

| 이런 메시지가 나오면 | 이렇게 해요 |
| --- | --- |
| `No such file or directory` | 이름 오타이거나 지금 위치에 없어요. `pwd`, `ls`로 확인하고 이름은 Tab으로 자동 완성 |
| `command not found` | 명령 이름 오타예요. 철자가 맞으면 그 프로그램이 설치되지 않은 거예요 |
| `Is a directory` | 폴더에 `rm`을 쳤어요. 폴더는 `rm -r` |
| 폴더가 두 개 생겼어요 | 이름에 띄어쓰기를 넣었어요. `"my folder"`처럼 따옴표로 묶거나 `my-folder`로 지어요 |

---

## 강사용

```
slides/
  deck.json        슬라이드 순서와 파트 구분
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen_scenes.py    터미널과 폴더 지도 장면을 만드는 스크립트
  check.js         글자 넘침, 겹침, 여백을 검사하고 스크린샷을 남기는 스크립트
  export.js        deck.json 순서대로 전체 슬라이드를 PDF 한 파일로 뽑는 스크립트
  build_player.js  애니메이션째 넘겨 보는 HTML 한 파일을 만드는 스크립트
  deckrender.js    export.js와 build_player.js가 같이 쓰는 그리기 코드
  icons/           HTML과 PDF에 넣는 아이콘 (Lucide, ISC 라이선스)
linux-terminal-slides.html  수강생 배포용 HTML
linux-terminal-slides.pdf   수강생 배포용 PDF
```

폴더 지도가 나오는 장면(`tree-map`, `s*`, `paths`, `special`, `err-*`)은 직접 고치지 말고 스크립트를 고친 뒤 다시 만들어요. 나머지 장은 `slides/`에서 바로 고쳐요.

```bash
python3 tools/gen_scenes.py slides
node tools/check.js slides shots           # 전체 검사 (Playwright 필요)
node tools/check.js slides shots s12-mv    # 특정 장만
node tools/build_player.js slides linux-terminal-slides.html   # 슬라이드를 고친 뒤 HTML 다시 만들기
node tools/export.js slides linux-terminal-slides.pdf          # PDF 다시 만들기
```

터미널 출력은 bash 5.2, GNU coreutils 9.4에서 실제로 실행해 확인했어요. 프롬프트는 화면을 아끼려고 `~/kant $`처럼 위치만 남긴 모양으로 바꿨어요.
