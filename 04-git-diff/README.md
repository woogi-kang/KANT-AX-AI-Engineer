# 04 · Git diff로 확인하기

> 02의 네 칸 그림에서 diff가 어느 두 칸을 비교하는지 봐요. add 전, commit 전, merge 전에 무엇이 바뀌는지 확인하는 습관을 만들어요. 03에서 쓰던 `hello-git` 저장소와 `login.md`를 그대로 써요.

| 슬라이드 | 분량 | 이전 모듈 | 다음 모듈 |
| --- | --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/04-git-diff/git-diff-slides.html) | 25장 · 8개 파트 | [03 · Git 브랜치와 협업](../03-git-branch) | [05 · VS Code Git Graph로 기록 보기](../05-git-graph) |

## 학습 목표

이 모듈을 마치면 다음을 할 수 있어요.

- `git diff`와 `git diff --staged`가 네 칸 중 어느 두 칸을 비교하는지 말해요.
- diff 출력에서 지운 줄(`-`), 넣은 줄(`+`), 위치(`@@`)를 읽어요.
- `git show`로 커밋 하나가 무엇을 바꿨는지 봐요.
- merge 전에 `git diff main feature/login`으로 들어올 변경을 미리 봐요.
- 충돌이 났을 때 `git diff`로 충돌 난 곳을 찾아요.
- `.gitignore`로 올리면 안 되는 파일을 Git에서 빼요.

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 1. diff란? | 3–4 | 두 모습을 비교하는 명령, 네 칸 중 어느 두 칸을 보나 |
| 2. git diff | 5–8 | add 전에 고친 줄 보기, 출력 읽는 법, add 뒤엔 빈 화면 |
| 3. git diff --staged | 9–12 | 커밋될 내용 확인, add 뒤에 또 고쳤을 때 |
| 4. git show | 13 | 커밋 하나 들여다보기 |
| 5. 브랜치 비교 | 14–16 | merge 전에 미리 보기, 순서를 바꾸면 뒤집히는 기호, 충돌 예고 |
| 6. 충돌 볼 때 | 17–18 | 충돌 중 `git diff`, 풀고 나서 `--staged`로 확인 |
| 7. .gitignore | 19–22 | `.env` 숨기기, 자주 적는 것, 이미 커밋한 파일 |
| 8. 막힐 때 | 23–24 | 아무것도 안 나올 때, 화면이 안 끝날 때 |
| 요약 | 25 | 한 장 요약 |

## 핵심 개념

### 어느 두 칸을 비교하나

| 명령 | 비교하는 두 칸 | 언제 |
| --- | --- | --- |
| `git diff` | ① 작업 폴더와 ② 대기실 | add 전. status의 빨간 글씨 파일 |
| `git diff --staged` | ② 대기실과 ③ 마지막 커밋 | commit 전. status의 초록 글씨 파일 |
| `git show` | 커밋 하나와 바로 전 커밋 | commit 뒤 |
| `git diff main feature/login` | 두 브랜치의 마지막 커밋 | merge 전 |

대기실이 비어 있으면 마지막 커밋과 같은 모습이 기준이 돼요. `--staged` 대신 `--cached`라고 써도 같아요.

### 출력 읽기

```
diff --git a/login.md b/login.md      어느 파일인지 (a/ = 예전, b/ = 지금)
index ef88ce3..7d67f3e 100644
--- a/login.md
+++ b/login.md
@@ -1,3 +1,4 @@                       예전 1번째 줄부터 3줄, 지금 1번째 줄부터 4줄
 # 로그인                              앞이 빈칸: 그대로인 줄
 아이디
-비밀번호                              - 지운 줄 (빨강)
+비밀번호 (8자 이상)                   + 넣은 줄 (초록)
+로그인 버튼
```

한 줄을 고치면 `-` 한 줄과 `+` 한 줄이 짝으로 나와요.

### 브랜치 비교는 순서가 중요해요

`git diff A B`는 A에서 B로 가려면 무엇을 바꿔야 하는지 보여 줘요. merge 전에는 받을 쪽을 앞에 써요.

```bash
git diff main feature/login     # main에 들어올 변경
git diff feature/login main     # 같은 차이가 반대 기호로 나와요
```

## 실습

### 1. add 전과 commit 전에 확인하기

```bash
printf "# 로그인\n아이디\n비밀번호 (8자 이상)\n로그인 버튼\n" > login.md
git diff                            # 고친 줄 보기
git add login.md
git diff                            # 아무것도 안 나와요
git diff --staged                   # 커밋될 내용
git commit -m "feat: 로그인 화면에 안내와 버튼 추가"
git show                            # 방금 만든 커밋 보기
```

### 2. merge 전에 브랜치 비교하기

```bash
git checkout -b feature/login
# login.md 제목을 # 로그인하기로 바꾸고 비밀번호 찾기 줄을 더해요
git add login.md
git commit -m "feat: 로그인 제목 바꾸고 비밀번호 찾기 추가"
git checkout main
git diff main feature/login
git diff --stat main feature/login  # 파일 이름과 줄 수만
```

### 3. .gitignore 만들기

```bash
echo "API_KEY=abc123" > .env
git status                          # .env가 빨간 글씨로 나와요
echo ".env" > .gitignore
git status                          # .env는 사라지고 .gitignore만 나와요
git add .gitignore
git commit -m "chore: .env를 gitignore에 추가"
```

자주 적는 것들이에요. 한 줄에 하나씩 쓰고, 끝에 `/`는 폴더, `*`는 아무 글자, `#`은 메모예요.

```
.env
node_modules/
__pycache__/
.venv/
*.log
.DS_Store
```

> **주의** `.gitignore`는 Git이 아직 모르는 파일에만 통해요. 이미 커밋한 파일은 `git rm --cached 파일`로 기록 대상에서 뺀 뒤 commit 해요. 내 폴더의 파일은 그대로 있어요. 비밀 값을 이미 push했다면 키를 새로 발급받아요.

## 명령어 요약

| 명령 | 하는 일 |
| --- | --- |
| `git diff` | add 전에 고친 줄 보기 |
| `git diff --staged` | 커밋될 줄 보기 |
| `git show` | 마지막 커밋이 바꾼 것 보기 |
| `git show 해시` | 그 커밋이 바꾼 것 보기 |
| `git diff main 브랜치` | merge하면 main에 들어올 변경 보기 |
| `git diff --stat` | 파일 이름과 바뀐 줄 수만 보기 |
| `git rm --cached 파일` | 이미 커밋한 파일을 기록 대상에서 빼기 (파일은 남아요) |

## 문제 해결

| 증상 | 원인과 해결 |
| --- | --- |
| `git diff`에 아무것도 안 나와요 | 이미 add했으면 `git diff --staged`, 이미 commit했으면 `git show`로 봐요 |
| 새로 만든 파일이 `git diff`에 안 나와요 | Untracked 파일은 안 나와요. `git add` 뒤에 `git diff --staged`로 봐요 |
| 화면 아래에 `:`나 `(END)`가 보이고 멈춰요 | 출력이 길어서 한 화면씩 보여 주는 중이에요. Space로 넘기고 `q`로 나와요 |
| `.gitignore`에 적었는데 status에 계속 나와요 | 이미 커밋한 파일이에요. `git rm --cached 파일` 뒤에 commit 해요 |

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py           모든 장 생성 (네 칸 장면, 출력 읽기, 브랜치 그래프, .gitignore)
  demo.sh          실습을 새 저장소에서 다시 실행해 실제 출력 확인
  check.js         글자 넘침, 겹침, 여백 검사와 스크린샷
  deckrender.js    export.js와 build_player.js가 같이 쓰는 렌더링 코드
  export.js        PDF 내보내기
  build_player.js  애니메이션이 재생되는 HTML 한 파일 만들기
  icons/           아이콘 (Lucide, ISC 라이선스)
git-diff-slides.html  배포용 HTML
git-diff-slides.pdf   강사용 PDF
```

슬라이드 HTML을 직접 고치지 말고 스크립트를 고친 뒤 다시 만들어요.

```bash
bash tools/demo.sh /tmp/diff-demo
python3 tools/gen.py slides
node tools/check.js slides shots
node tools/build_player.js slides git-diff-slides.html
node tools/export.js slides git-diff-slides.pdf
```

터미널 출력은 `tools/demo.sh`로 git 2.43에서 실제로 실행해 옮겼어요. 날짜를 고정해서 해시가 매번 같게 나와요. 수강생 화면의 해시는 달라요. status의 안내 문구처럼 화면 폭 때문에 뺀 줄은 발표자 노트에 적어 두었어요.

</details>

---

[← 이전: 03 · Git 브랜치와 협업](../03-git-branch) · [커리큘럼](../README.md) · [다음: 05 · VS Code Git Graph로 기록 보기 →](../05-git-graph)
