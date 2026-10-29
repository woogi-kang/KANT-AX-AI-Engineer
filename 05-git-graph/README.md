# 05 · VS Code Git Graph로 기록 보기

> VS Code 확장 Git Graph를 설치해서 터미널로 만든 커밋과 브랜치를 그림으로 봐요. 명령은 지금처럼 터미널에서 치고, 친 결과를 Git Graph로 확인해요.

| 슬라이드 | 분량 | 이전 모듈 | 다음 모듈 |
| --- | --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/05-git-graph/git-graph-slides.html) | 23장 · 4개 파트 | [04 · Git diff로 확인하기](../04-git-diff) | 준비 중 |

## 학습 목표

이 모듈을 마치면 다음을 할 수 있어요.

- VS Code에 Git Graph 확장을 설치하고 저장소를 열어요.
- 점(커밋), 이름표(브랜치), HEAD, origin/main을 화면에서 찾아요.
- commit, push, fetch, pull, checkout, merge를 친 뒤 그림이 어떻게 바뀌는지 말해요.
- 커밋 줄을 눌러 그 커밋에서 바뀐 파일을 봐요.

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1–3 | `git log --oneline`과 같은 기록을 그림으로 보기 |
| 1. 설치하고 열기 | 4–5 | 확장 탭에서 설치, 여는 법 세 가지 |
| 2. 화면 읽기 | 6–9 | 표의 다섯 칸, 위가 최신, 굵은 이름표와 빈 점, origin/main |
| 3. 명령 치고 확인하기 | 10–20 | 고치기, commit, push, fetch, pull, checkout -b, 브랜치 커밋, 갈라지기, merge, 커밋 상세 |
| 4. 쓸 때 주의, 막힐 때 | 21–22 | 메뉴 대신 터미널, 안 열리거나 안 바뀔 때 |
| 요약 | 23 | 한 장 요약 |

## 설치하고 열기

1. VS Code 왼쪽 막대에서 확장 아이콘을 눌러요. Windows는 `Ctrl+Shift+X`, Mac은 `Cmd+Shift+X`예요.
2. 검색창에 `git graph`를 쳐요.
3. 만든 사람이 mhutchie인 Git Graph에서 Install을 눌러요.
4. File > Open Folder로 `hello-git` 폴더를 열어요.
5. 아래 상태 표시줄의 Git Graph를 눌러요. 소스 제어 탭 위의 그래프 아이콘이나 명령 팔레트의 `Git Graph: View Git Graph (git log)`로도 열려요.

## 화면 읽기

| 보이는 것 | 뜻 |
| --- | --- |
| 점 하나 | 커밋 하나. 맨 위가 가장 최근이에요 |
| 굵은 글씨에 색 테두리인 이름표 | 지금 있는 브랜치. 터미널의 `HEAD ->`와 같아요 |
| 속이 빈 점 | HEAD가 가리키는 커밋 |
| `main` 이름표 옆의 기울어진 `origin` | `main`과 `origin/main`이 같은 커밋 |
| `origin/main` 이름표가 따로 있음 | GitHub과 차이가 있어요. 위에 있는 쪽이 앞서요 |
| 맨 위 회색 빈 점 `Uncommitted Changes (1)` | 아직 커밋하지 않은 파일 1개 |
| 오른쪽 커밋 번호 | 8자리. 터미널의 7자리와 앞부분이 같아요 |

03 슬라이드는 시간이 왼쪽에서 오른쪽으로 흘러요. Git Graph는 아래에서 위로 쌓여요.

## 실습

터미널에서 한 줄씩 치고, 줄마다 Git Graph가 어떻게 바뀌는지 봐요. GitHub에 올라간 커밋이 하나 있는 `hello-git` 저장소에서 시작해요.

```bash
echo "로그인 버튼" >> login.md
git status                      # Git Graph 맨 위에 Uncommitted Changes (1)
git add login.md
git commit -m "feat: 로그인 버튼 추가"   # main이 origin/main보다 위로
git push origin main            # main | origin으로 합쳐져요
git fetch origin                # 팀원이 올린 커밋이 있으면 origin/main이 위로
git pull origin main            # main이 따라 올라가요
git checkout -b feature/login   # 같은 점에 feature/login 이름표가 더 붙어요
echo "비밀번호 찾기" >> login.md
git add login.md
git commit -m "feat: 비밀번호 찾기 추가"  # feature/login만 위로
git checkout main
echo "실행 방법은 준비 중이에요" >> README.md
git add README.md
git commit -m "docs: README에 실행 방법 추가"  # 길이 둘로 갈라져요
git merge feature/login         # 두 선이 merge 커밋에서 만나요
git push origin main
```

`git merge`에서 vim이 열리면 Esc를 누른 뒤 `:wq`와 Enter를 쳐요. 팀원이 없으면 `git fetch origin`과 `git pull origin main`은 새로 받을 게 없어서 그림이 그대로예요.

커밋 줄을 한 번 누르면 아래에 상세 정보와 바뀐 파일이 펼쳐져요. 파일 이름을 누르면 04에서 본 diff 화면이 열려요.

## 쓸 때 주의

Git Graph에서 커밋이나 이름표를 오른쪽 클릭하면 checkout, merge, reset 같은 메뉴가 나와요. 수업에서는 메뉴를 쓰지 않아요. 명령은 터미널에 치고 Git Graph로는 결과만 확인해요. 터미널에 남아야 오류가 났을 때 읽고 고칠 수 있어요. Fetch 버튼 대신 `git fetch origin`을 쳐요.

## 문제 해결

| 증상 | 원인과 해결 |
| --- | --- |
| `No Git repositories were found`가 나와요 | 저장소가 아닌 폴더를 열었어요. File > Open Folder로 `git init`을 한 `hello-git` 폴더를 열어요 |
| 상태 표시줄에 Git Graph가 안 보여요 | 확장이 설치됐는지 확장 탭에서 봐요. 명령 팔레트에서 `git graph`를 쳐서 열어도 돼요 |
| 팀원이 올린 커밋이 안 보여요 | Git Graph는 내 컴퓨터에 받아 둔 기록만 보여 줘요. `git fetch origin`을 쳐요 |
| 명령을 쳤는데 그림이 그대로예요 | 보통 저절로 바뀌어요. 안 바뀌면 Git Graph 탭 오른쪽 위 새로고침 아이콘을 눌러요 |

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py           모든 장 생성 (VS Code와 Git Graph 화면을 HTML과 SVG로 그림)
  demo.sh          실습을 새 저장소에서 다시 실행해 실제 출력 확인
  check.js         글자 넘침, 겹침, 여백 검사와 스크린샷
  deckrender.js    export.js와 build_player.js가 같이 쓰는 렌더링 코드
  export.js        PDF 내보내기
  build_player.js  애니메이션이 재생되는 HTML 한 파일 만들기
  icons/           아이콘 (Lucide, ISC 라이선스)
git-graph-slides.html  배포용 HTML
git-graph-slides.pdf   강사용 PDF
```

슬라이드 HTML을 직접 고치지 말고 스크립트를 고친 뒤 다시 만들어요.

```bash
bash tools/demo.sh /tmp/graph-demo
python3 tools/gen.py slides
node tools/check.js slides shots
node tools/build_player.js slides git-graph-slides.html
node tools/export.js slides git-graph-slides.pdf
```

터미널 출력과 해시는 `tools/demo.sh`로 git 2.43에서 실제로 실행해 옮겼어요. 날짜를 고정해서 해시가 매번 같게 나와요. GitHub 자리는 내 컴퓨터의 빈 저장소로 대신하고 주소만 `https://github.com/kim/hello-git.git`으로 보이게 했어요. Git Graph 화면은 확장 소스(mhutchie/vscode-git-graph)의 기본 설정을 따라 그렸어요. 이름표 모양, 선 색(#0085D9, #D9008F), HEAD 빈 점, 8자리 커밋 번호가 그 예예요. status의 안내 문구처럼 화면 폭 때문에 뺀 줄은 발표자 노트에 적어 두었어요.

</details>

---

[← 이전: 04 · Git diff로 확인하기](../04-git-diff) · [커리큘럼](../README.md)
