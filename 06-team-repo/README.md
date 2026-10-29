# 06 · 팀 레포에서 같이 작업하고 충돌 풀기

> 2~3명이 팀을 짜서 GitHub에 레포 하나를 만들고, 각자 clone해서 커밋, push, pull을 해요. push가 거절되는 장면, pull로 저절로 합쳐지는 장면, 같은 줄을 고쳐 충돌이 나는 장면을 일부러 만들고 풀어요. 마지막 5부에는 브랜치와 Pull Request로 일할 때 자주 만나는 경우 8가지를 모았어요.

| 슬라이드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/06-team-repo/team-repo-slides.html) | [05 · VS Code Git Graph로 기록 보기](../05-git-graph) | [07 · 커밋 전 변경 취소하기와 잠깐 보관하기](../07-git-restore-stash) |

## 학습 목표

이 챕터를 마치면 다음을 할 수 있어요.

- GitHub에 팀 레포를 만들고 팀원을 Collaborator로 초대해요.
- push가 `! [rejected] ... (fetch first)`로 거절되면 pull로 받아 합친 뒤 다시 push해요.
- 다른 파일을 고친 경우와 같은 줄을 고친 경우에 pull 결과가 어떻게 다른지 말해요.
- pull 충돌을 직접 풀고 팀원이 pull로 받게 해요.
- 브랜치와 PR로 일하다 막히면 메시지로 케이스를 찾아 해결해요.

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1–3 | 한 저장소를 셋이 같이 쓰기, 오늘 만날 메시지 세 가지 |
| 1. 팀 레포 준비 | 4–8 | 역할 나누기, 레포 만들기, Collaborator 초대와 수락, clone, pull 설정 |
| 2. 다른 파일은 저절로 | 9–17 | push 거절, pull로 merge 커밋, vim 닫기, 설정이 없을 때, fast-forward, fetch로 먼저 보기 |
| 3. 같은 줄은 충돌 | 18–23 | 같은 줄 고치고 push 거절, `CONFLICT`, 충돌 표시 읽기, 고쳐서 push, 팀원이 pull |
| 4. 팀 규칙 | 24–26 | 팀 규칙 다섯 가지, 작업 순서, 브랜치와 Pull Request로 넘어가기 |
| 5. 팀 작업 케이스 | 27–40 | 케이스 목록, 막혔을 때 찾기, 케이스 8가지 |
| 요약 | 41 | 한 장 요약 |

슬라이드 위쪽 네 칸은 GitHub(보라), kim(파랑), lee(초록), park(주황)의 저장소예요. 점 색은 그 커밋을 만든 사람이고, 흰 점은 merge 커밋이에요.

## 시작 전에 한 번

셋 다 쳐요. 출력은 없어요.

```bash
git config --global pull.rebase false
```

pull은 GitHub 커밋을 받아 와서(fetch) 내 main과 합쳐요(merge). 이 설정은 합칠 때 merge로 하라는 뜻이에요. 설정이 없으면 내 main과 GitHub main이 갈라졌을 때 pull이 `fatal: Need to specify how to reconcile divergent branches.`로 멈춰요. 오늘 실습에서는 꼭 그 상황이 생겨요.

## 실습

팀원 이름을 kim, lee, park 자리에 넣어요. 2인 팀이면 park 차례는 건너뛰어요.

### 1. 팀 레포 준비

| 누가 | 할 일 |
| --- | --- |
| kim (팀장) | GitHub 오른쪽 위 + 버튼 > New repository. 이름 `team-intro`, Add README를 켜고 Create repository |
| kim (팀장) | 레포 Settings > Collaborators > Add people로 lee, park 초대 |
| lee, park | 메일이나 `github.com/kim/team-intro/invitations`에서 Accept invitation |

셋 다 clone해요. 주소는 레포 화면의 초록색 Code 버튼에서 복사해요.

```bash
git clone https://github.com/kim/team-intro.git
cd team-intro
git log --oneline                # Initial commit 하나
```

### 2. 다른 파일은 저절로 합쳐져요

kim과 lee가 거의 같이 시작해요. kim이 먼저 push해요.

```bash
# kim
echo "안녕하세요, kim이에요" > kim.md
git add kim.md
git commit -m "docs: kim 자기소개 추가"
git push origin main             # 올라가요
```

```bash
# lee
echo "안녕하세요, lee예요" > lee.md
git add lee.md
git commit -m "docs: lee 자기소개 추가"
git push origin main             # ! [rejected] ... (fetch first)
git pull origin main             # Merge made by the 'ort' strategy. (vim이 열리면 Esc, :wq, Enter)
git push origin main             # 이번엔 올라가요
```

```bash
# kim
git pull origin main             # Fast-forward, lee.md가 생겨요
```

```bash
# park: 작업 전에 먼저 보고 받아요
git fetch origin
git log --oneline
git log --oneline origin/main    # 팀원 커밋 세 개가 더 있어요
git pull origin main             # Fast-forward
```

### 3. 같은 줄은 충돌

README.md 첫 줄 `# team-intro`를 kim과 lee가 서로 다르게 고쳐요. VS Code로 고쳐도 돼요.

```bash
# kim
printf '# 깃벗 팀\n' > README.md
git diff
git add README.md
git commit -m "docs: 팀 이름을 깃벗으로 정하기"
git push origin main             # 올라가요
```

```bash
# lee
printf '# 커밋조 팀\n' > README.md
git add README.md
git commit -m "docs: 팀 이름을 커밋조로 정하기"
git push origin main             # ! [rejected]
git pull origin main             # CONFLICT (content): Merge conflict in README.md
git status                       # both modified: README.md
```

lee가 README.md를 열면 이렇게 보여요.

```
<<<<<<< HEAD
# 커밋조 팀
=======
# 깃벗 팀
>>>>>>> 058635425c086372cec618e885f0483ba8c58d08
```

위쪽 `HEAD` 아래가 lee 자기 것, 아래쪽이 GitHub에서 받아 온 kim의 것이에요. 팀이 말로 정한 내용만 남기고 표시 세 줄을 지워요. 해시는 사람마다 달라요.

```bash
# lee
git add README.md
git commit -m "fix: 팀 이름 충돌 해결"
git push origin main
```

```bash
# kim, park
git pull origin main             # Fast-forward
cat README.md                    # # 깃벗 팀
```

시간이 남으면 역할을 바꿔서 lee가 먼저 push하고 kim이 충돌을 풀어 봐요.

## 팀 규칙

1. 작업 전에 `git pull origin main`부터 쳐요.
2. 작게 자주 커밋하고 바로 push해요.
3. 누가 어떤 파일, 어떤 줄을 고칠지 미리 나눠요.
4. push가 거절되면 pull해요. `--force`는 팀원 커밋을 지우니 쓰지 않아요.
5. 충돌은 혼자 지우지 말고 고친 사람과 같이 보고 정해요.

오늘은 모두 main에 바로 push했어요. 실제 팀은 각자 브랜치에서 일하고 Pull Request로 합쳐요. 그 흐름은 [03 · Git 브랜치와 협업](../03-git-branch)의 7부에 있어요.

## 팀 작업 케이스 (5부)

브랜치와 Pull Request로 일할 때 자주 만나는 경우예요. 막히면 슬라이드 28쪽의 찾기 표에서 메시지로 쪽수를 찾아요.

| 케이스 | 쪽 | 상황 | 이렇게 해요 |
| :---: | :---: | --- | --- |
| 1 | 29 | 작업 시작 | `git checkout main`, `git pull origin main`, `git checkout -b feature/이름` |
| 2 | 30–31 | 브랜치 push, PR 만들기 | `git push origin feature/이름`, GitHub에서 Compare & pull request |
| 3 | 32 | PR이 합쳐진 뒤 | `git checkout main`, `git pull origin main`, `git branch -d feature/이름`, 다음 브랜치 |
| 4 | 33 | 다른 파일을 고친 PR 두 개 | 둘 다 바로 Merge, 각자 main에서 pull |
| 5 | 34–36 | 같은 줄을 고친 PR (`This branch has conflicts`) | 내 브랜치에서 `git pull origin main`, 충돌 풀고 add, commit, `git push origin feature/이름` |
| 6 | 37–38 | 고친 파일이 있는데 pull (`would be overwritten by merge`) | 브랜치를 만들어 커밋한 뒤 다시 pull |
| 7 | 39 | 고친 파일이 있는데 checkout (`would be overwritten by checkout`) | 지금 브랜치에서 커밋한 뒤 옮기기 |
| 8 | 40 | main에 커밋해 버림 (push 전) | `git branch feature/이름`, `git reset --hard HEAD~1`, `git checkout feature/이름` |

케이스 6, 7에서 커밋하지 않고 잠깐 치워 두는 stash는 [07](../07-git-restore-stash)에서 배워요. 케이스 8의 `--hard`는 커밋 안 한 변경을 지우니 `git status`가 깨끗한지 먼저 봐요. 이미 push했다면 되돌리지 말고 팀에 알려요.

## 명령어 요약

| 명령 | 하는 일 |
| --- | --- |
| `git config --global pull.rebase false` | pull할 때 merge로 합치기 (처음 한 번) |
| `git clone 주소` | 팀 레포 받기 |
| `git push origin main` | 내 커밋 올리기 |
| `git pull origin main` | 팀원 커밋 받아서 합치기 |
| `git fetch origin` | 받아만 오기 |
| `git log --oneline origin/main` | GitHub 쪽 기록 보기 |
| `git status` | 충돌 난 파일 찾기 |
| `git merge --abort` | 충돌 난 pull을 pull 전으로 되돌리기 |
| `git push origin feature/이름` | 내 브랜치 올리기 |
| `git branch -d feature/이름` | 합쳐진 브랜치 지우기 |

## 문제 해결

| 메시지 | 원인과 해결 |
| --- | --- |
| `! [rejected] main -> main (fetch first)` | GitHub에 내가 모르는 커밋이 있어요. `git pull origin main` 뒤에 다시 push |
| `fatal: Need to specify how to reconcile divergent branches.` | pull 설정이 없어요. `git config --global pull.rebase false` 뒤에 다시 pull |
| `CONFLICT (content): Merge conflict in 파일` | 같은 줄을 둘 다 고쳤어요. 파일을 고치고 `git add 파일`, `git commit -m "fix: ..."`, `git push origin main` |
| `error: Pulling is not possible because you have unmerged files.` | 충돌을 다 풀기 전에 또 pull했어요. 충돌부터 고치고 add, commit |
| `error: Your local changes to the following files would be overwritten by merge` | 커밋하지 않은 파일을 팀원도 고쳐서 올렸어요. `git add 파일`, `git commit -m "..."` 뒤에 다시 pull. 커밋하지 않고 잠깐 치워 두는 stash는 [07](../07-git-restore-stash)에서 배워요 |
| `Permission to kim/team-intro.git denied to lee` (403) | 초대를 아직 수락하지 않았어요. `github.com/kim/team-intro/invitations`에서 Accept |
| pull 중에 vim이 열려요 | merge 커밋 메시지 화면이에요. Esc를 누르고 `:wq`, Enter |

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py           모든 장 생성 (네 칸 저장소 그림, 터미널, GitHub 화면)
  demo.sh          kim, lee, park 실습(1~3부)을 새 저장소에서 다시 실행해 실제 출력 확인
  cases.sh         5부 팀 작업 케이스를 kim, lee로 다시 실행 (PR Merge 버튼은 세 번째 clone이 대신)
  check.js         글자 넘침, 겹침, 여백 검사와 스크린샷
  deckrender.js    export.js와 build_player.js가 같이 쓰는 렌더링 코드
  export.js        PDF 내보내기
  build_player.js  애니메이션이 재생되는 HTML 한 파일 만들기
  icons/           아이콘 (Lucide, ISC 라이선스)
team-repo-slides.html  배포용 HTML
team-repo-slides.pdf   강사용 PDF
```

슬라이드 HTML을 직접 고치지 말고 스크립트를 고친 뒤 다시 만들어요.

```bash
bash tools/demo.sh /tmp/team-demo
bash tools/cases.sh /tmp/team-cases
python3 tools/gen.py slides
node tools/check.js slides shots
node tools/build_player.js slides team-repo-slides.html
node tools/export.js slides team-repo-slides.pdf
```

터미널 출력과 해시는 `tools/demo.sh`로 git 2.43에서 실제로 실행해 옮겼어요. 사람마다 HOME을 따로 둬서 설정이 섞이지 않아요. 날짜를 고정해서 해시가 매번 같아요. GitHub 자리는 내 컴퓨터의 빈 저장소로 대신하고 주소만 `https://github.com/kim/team-intro.git`으로 보이게 했어요. 화면 폭 때문에 뺀 줄은 발표자 노트에 적어 두었어요. 403 메시지는 GitHub이 보내는 것이라 로컬에서 재현하지 못했어요.

</details>

---

[← 이전: 05 · VS Code Git Graph로 기록 보기](../05-git-graph) · [커리큘럼](../README.md) · [다음: 07 · 커밋 전 변경 취소하기와 잠깐 보관하기 →](../07-git-restore-stash)
