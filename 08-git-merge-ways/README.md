# 08 · 갈라진 기록 합치는 방법 비교하기

> 같은 예시 하나로 합치는 방법 네 가지를 나란히 놓고 결과 그림을 비교해요. fast-forward, merge(`--no-ff` 포함), rebase, squash예요. 이어서 `git pull`이 이 중 무엇을 하는지, GitHub PR의 Merge 버튼 세 개가 각각 무엇인지 연결해요. 연습용 저장소 `merge-lab`을 새로 만들어 내 컴퓨터에서만 해 봐요.

| 슬라이드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/08-git-merge-ways/git-merge-ways-slides.html) | [07 · 커밋 전 변경 취소하기와 잠깐 보관하기](../07-git-restore-stash) | [09 · uv로 파이썬 시작하기](../09-python-uv) |

## 학습 목표

이 챕터를 마치면 다음을 할 수 있어요.

- 같은 갈라진 기록을 fast-forward, merge, rebase, squash로 합쳤을 때 그래프가 어떻게 다른지 그려요.
- 합치기 커밋이 생기는지, 커밋 해시가 바뀌는지로 네 방법을 구분해요.
- `git pull`의 설정 세 가지(`pull.rebase false`, `pull.rebase true`, `pull.ff only`)가 각각 어떤 합치기인지 말해요.
- GitHub PR의 Create a merge commit, Squash and merge, Rebase and merge 버튼을 명령과 연결해요.
- 충돌은 어느 방법이든 같은 줄이면 난다는 걸 알고, rebase 중 충돌을 이어 가거나 그만둬요.
- push한 브랜치에서는 rebase하지 않는 이유를 말해요.

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1–4 | 오늘의 순서, 예시 소개(A, B 뒤 브랜치에 D, E) |
| 1. 갈라지지 않았을 때 | 5–6 | fast-forward, `--no-ff` |
| 2. 갈라졌을 때 | 7–14 | main에 C, merge, rebase와 바뀌는 해시, squash와 `branch -D` |
| 3. 한눈에 비교 | 15–16 | 네 가지 결과 그림, 비교 표 |
| 4. git pull은 무엇을 하나 | 17–22 | 설정이 없을 때, `pull.rebase false`, `pull.rebase true`, `pull.ff only`, 수업이 false를 쓰는 이유 |
| 5. GitHub PR의 Merge 버튼 | 23–25 | 버튼 세 개와 명령, 버튼별 기록 모양, 합친 뒤 브랜치 지우기 |
| 6. 충돌과 주의 | 26–29 | 어느 방법이든 같은 줄이면 충돌, rebase 중 충돌, push한 브랜치는 rebase 금지, 언제 무엇을 |
| 막힐 때와 요약 | 30–31 | 자주 나오는 메시지, 한 장 요약 |

## 핵심 개념

### 같은 출발점, 네 가지 결과

출발점은 A, B 뒤에 main에는 C, `feature/login-button`에는 D, E가 있는 모습이에요.

```
        D ── E          feature/login-button
       /
A ── B ── C             main
```

| 방법 | 명령 | 새로 생기는 커밋 | D, E 해시 | main 기록 |
| --- | --- | --- | --- | --- |
| fast-forward | `git merge 브랜치` (갈라지지 않았을 때) | 없음 | 그대로 | 한 줄 |
| merge | `git merge 브랜치`, `git merge --no-ff 브랜치` | 합치기 커밋 M | 그대로 | 두 줄이 만나요 |
| rebase | 브랜치에서 `git rebase main`, main에서 `git merge 브랜치` | D', E' | 바뀌어요 | 한 줄 |
| squash | `git merge --squash 브랜치` 뒤 `git commit -m "..."` | S 하나 | main에 없어요 | 한 줄, 커밋 하나 |

출발점이 같으면 어느 방법으로 합쳐도 파일 내용은 같아요. 다른 건 기록 모양과 해시예요. fast-forward와 `--no-ff`는 C가 생기기 전 모습에서 해요.

### git pull은 fetch 뒤 합치기

| 설정 | 갈라졌을 때 pull이 하는 일 | 수업 |
| --- | --- | --- |
| `pull.rebase false` | merge로 합쳐요. 합치기 커밋이 생겨요 | 이 설정 하나만 써요 |
| `pull.rebase true` | 내 커밋을 받은 커밋 뒤로 rebase해요. 내 커밋 해시가 바뀌어요 | 보기만 해요 |
| `pull.ff only` | fast-forward만 받아요. 갈라졌으면 `fatal: Not possible to fast-forward, aborting.`로 멈춰요 | 보기만 해요 |
| 설정 없음 | `fatal: Need to specify how to reconcile divergent branches.`로 멈추고 위 세 줄을 힌트로 보여 줘요 | 06에서 false로 설정 |

수업은 `pull.rebase false`로 통일해요. 기록을 바꾸지 않아서 push한 커밋과 어긋나지 않고, 충돌도 03, 06과 같은 방법으로 풀어요.

### GitHub PR의 Merge 버튼

| 버튼 | 같은 명령 | GitHub main에 남는 것 |
| --- | --- | --- |
| Create a merge commit | `git merge --no-ff` | `Merge pull request #1 from kim/feature/login-button` 합치기 커밋 |
| Squash and merge | `git merge --squash` | `feat: 로그인 버튼 추가 (#1)` 커밋 하나 |
| Rebase and merge | `git rebase` 뒤 fast-forward | 새 해시의 D', E' |

어느 버튼을 쓸지는 팀이 정해요. Squash and merge나 Rebase and merge로 합친 뒤에는 내 컴퓨터의 브랜치가 `git branch -d`로 지워지지 않아요. PR이 Merged인 걸 확인한 뒤 `git branch -D 브랜치`로 지워요.

> **주의** push한 브랜치와 main에서는 rebase하지 않아요. rebase는 커밋을 새로 만들어서 GitHub과 팀원이 가진 옛 커밋과 어긋나요. 이때 pull하면 같은 커밋이 기록에 두 번 들어가요. rebase는 push 전, 나만 가진 커밋에만 써요.

## 실습

수업 저장소와 팀 레포는 건드리지 않아요. 연습용 저장소를 새로 만들고, 방법마다 폴더를 `cp -r`로 복사해서 같은 출발점에서 해 봐요. push는 하지 않아요.

### 1. 출발점 만들기

```bash
mkdir merge-lab
cd merge-lab
git init
echo "# 로그인" > login.md
git add login.md
git commit -m "feat: 로그인 화면 추가"
echo "아이디" >> login.md
git add login.md
git commit -m "feat: 아이디 입력 추가"
git checkout -b feature/login-button
echo "로그인 버튼" >> login.md
git add login.md
git commit -m "feat: 로그인 버튼 추가"
```

VS Code에서 `login.md` 마지막 줄 `로그인 버튼`을 `[로그인] 버튼`으로 고쳐 저장한 뒤 이어서 쳐요.

```bash
git add login.md
git commit -m "fix: 버튼 글자 고치기"
git checkout main
cd ..
cp -r merge-lab ff-lab             # 갈라지기 전 모습 복사 (1부용)
cp -r merge-lab noff-lab
cd merge-lab
echo "# merge-lab" > README.md
git add README.md
git commit -m "docs: README 추가"   # main에 C, 이제 갈라졌어요
cd ..
cp -r merge-lab try-merge          # 갈라진 모습 복사 (2부용)
cp -r merge-lab try-rebase
cp -r merge-lab try-squash
```

### 2. 갈라지지 않았을 때

```bash
cd ff-lab
git merge feature/login-button              # Fast-forward
git log --oneline
cd ../noff-lab
git merge --no-ff feature/login-button      # 편집기가 열리면 그대로 저장하고 닫기
git log --oneline                           # 맨 위에 Merge branch 'feature/login-button'
cd ..
```

### 3. 갈라졌을 때

```bash
cd try-merge
git merge feature/login-button              # 합치기 커밋, 편집기는 그대로 저장하고 닫기
git log --oneline

cd ../try-rebase
git checkout feature/login-button
git log --oneline                           # D, E 해시를 적어 둬요
git rebase main
git log --oneline                           # D, E 해시가 바뀌었어요
git checkout main
git merge feature/login-button              # Fast-forward

cd ../try-squash
git merge --squash feature/login-button
git status                                  # Changes to be committed
git commit -m "feat: 로그인 버튼 추가"
git log --oneline                           # D, E 없이 커밋 하나
git branch -d feature/login-button          # not fully merged
git branch -D feature/login-button
cd ..
```

네 폴더를 VS Code Git Graph(05)로 열어 슬라이드 그림과 비교해 봐요.

### 4. rebase 중 충돌이 나면

1. 표시 줄 세 개를 지우고 남길 내용으로 고쳐요.
2. `git add 파일`
3. `git rebase --continue` 로 다음 커밋을 이어서 옮겨요. 편집기가 열리면 그대로 저장하고 닫아요.

헷갈리면 `git rebase --abort`로 rebase 전 모습으로 돌아가요. 내 브랜치에서 쳤어도 `<<<<<<< HEAD` 쪽은 main 내용이고, 아래쪽이 내 커밋이에요.

## 명령어 요약

| 명령 | 하는 일 |
| --- | --- |
| `git merge 브랜치` | 갈라지지 않았으면 fast-forward, 갈라졌으면 합치기 커밋 |
| `git merge --no-ff 브랜치` | fast-forward가 될 때도 합치기 커밋 만들기 |
| `git rebase main` | 지금 브랜치 커밋을 main 끝 뒤로 옮겨 붙이기 (push 전에만) |
| `git rebase --continue` | rebase 충돌을 풀고 add한 뒤 이어 가기 |
| `git rebase --abort` | rebase 그만두고 전 모습으로 |
| `git merge --squash 브랜치` | 브랜치 변경을 모아 대기실에 올리기. 커밋은 직접 |
| `git branch -D 브랜치` | 합쳐지지 않았다고 나와도 지우기 (squash, Rebase and merge 뒤) |
| `git config --global pull.rebase` | 지금 pull 설정 보기. `false`가 나오면 수업 설정 |

## 문제 해결

| 증상 | 원인과 해결 |
| --- | --- |
| `fatal: Need to specify how to reconcile divergent branches.` | pull 설정이 없어요. `git config --global pull.rebase false` 뒤 다시 pull |
| `fatal: Not possible to fast-forward, aborting.` | `pull.ff only`가 설정돼 있어요. `git config --global --unset pull.ff`로 지우고 다시 pull |
| `error: the branch '...' is not fully merged.` | squash나 Rebase and merge로 합쳤어요. 변경이 main에 있는 걸 확인하고 `git branch -D 브랜치` |
| `error: could not apply ...` 와 `CONFLICT` | rebase 중 충돌이에요. 고치고 `git add` 뒤 `git rebase --continue`, 그만두려면 `git rebase --abort` |
| rebase 뒤 push가 `! [rejected] ... (non-fast-forward)` | push한 브랜치를 rebase했어요. pull하면 같은 커밋이 기록에 두 번 들어가니 더 치지 말고 강사에게 물어봐요 |
| `interactive rebase in progress` 가 status에 보여요 | rebase가 멈춘 상태예요. 충돌을 풀고 `--continue` 하거나 `--abort` |

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분 (gen.py가 만들어요)
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py           모든 장과 deck.json 생성 (커밋 그래프, 비교 카드, PR 버튼 그림)
  demo.sh          모든 방법을 새 저장소에서 다시 실행해 실제 출력 확인
  check.js         글자 넘침, 겹침, 여백 검사와 스크린샷
  deckrender.js    export.js와 build_player.js가 같이 쓰는 렌더링 코드
  export.js        PDF 내보내기
  build_player.js  애니메이션이 재생되는 HTML 한 파일 만들기
  icons/           아이콘 (Lucide, ISC 라이선스)
git-merge-ways-slides.html  배포용 HTML
git-merge-ways-slides.pdf   강사용 PDF
```

슬라이드 HTML을 직접 고치지 말고 스크립트를 고친 뒤 다시 만들어요.

```bash
bash tools/demo.sh /tmp/merge-demo
python3 tools/gen.py slides
node tools/check.js slides shots
node tools/build_player.js slides git-merge-ways-slides.html
node tools/export.js slides git-merge-ways-slides.pdf
```

터미널 출력은 `tools/demo.sh`로 git 2.43에서 실제로 실행해 옮겼어요. 방법마다 같은 출발점을 폴더째 복사해서 시작해요. GitHub 자리는 내 컴퓨터의 빈 저장소로 대신하고 주소만 `https://github.com/kim/merge-lab.git`으로 보이게 했어요. 팀원 lee와 GitHub의 Squash and merge 버튼은 같은 저장소를 하나 더 clone해서 흉내 냈어요. 날짜를 고정해서 해시가 매번 같게 나와요. pull 합치기 커밋 메시지에 폴더 경로가 들어가서 `/tmp/merge-demo`에서 실행해야 be1e0e1이 나와요. 화면 폭 때문에 뺀 줄은 발표자 노트에 적어 두었어요.

</details>

---

[← 이전: 07 · 커밋 전 변경 취소하기와 잠깐 보관하기](../07-git-restore-stash) · [커리큘럼](../README.md) · [다음: 09 · uv로 파이썬 시작하기 →](../09-python-uv)
