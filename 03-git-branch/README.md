# 03 · Git 브랜치와 협업

> 커밋을 점으로, 브랜치를 그 점에 붙은 이름표로 그려서 명령마다 그래프가 어떻게 바뀌는지 봐요. 로그인 기능을 브랜치에서 만들고, 합치고, 충돌을 풀고, Pull Request로 팀과 합치는 데까지 이어서 해요. 02에서 만든 `hello-git` 저장소를 그대로 써요.

| 슬라이드 | 분량 | 이전 모듈 | 다음 모듈 |
| --- | --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/03-git-branch/git-branch-slides.html) | 68장 · 9개 파트 | [02 · Git 기본 흐름](../02-git-basics) | 준비 중 |

## 학습 목표

이 모듈을 마치면 다음을 할 수 있어요.

- 커밋 그래프에서 커밋, 브랜치, `HEAD`가 무엇을 가리키는지 읽어요.
- `branch`, `checkout`으로 브랜치를 만들고 옮겨 다니며 작업해요. 같은 일을 하는 `switch`도 읽고 써요.
- `merge`로 브랜치를 합치고 fast-forward와 merge 커밋을 구분해요.
- push 전에 커밋과 merge를 `reset --soft`, `--mixed`, `--hard`로 되돌리고 셋의 차이를 설명해요.
- 충돌 메시지를 보고 종류를 알아낸 뒤 직접 풀어요.
- 브랜치를 GitHub에 올리고 Pull Request로 합쳐요.

## 구성

한 장에 개념 하나, 그래프 변화 하나만 담았어요.

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 1. 브랜치란? | 3–6 | 왜 쓰는지, 커밋(점), 브랜치(이름표), `HEAD` |
| 2. 만들고 옮기기 | 7–14 | `branch` `checkout` `switch`, 브랜치에서 커밋, 폴더 파일이 바뀌는 모습 |
| 3. 합치기 | 15–19 | merge는 받는 쪽에서, fast-forward, `branch -d`, 이름 규칙 |
| 4. 갈라진 길 | 20–25 | `checkout -b`, merge 커밋 |
| 5. 되돌리기 | 26–38 | `reset --soft` `--mixed` `--hard`, 일반 커밋과 merge 커밋 두 경우, 다시 merge |
| 6. 충돌 풀기 | 39–45 | 충돌이 나는 때, 표시 읽기, 고치고 커밋, `merge --abort` |
| 7. GitHub에서 함께 | 46–52 | `push origin 브랜치`, Pull Request, GitHub Flow |
| 8. 충돌 시나리오 | 53–64 | 바로 옆 줄, 지움 vs 고침, 같은 이름 새 파일, pull, Pull Request |
| 9. 문제 해결 | 65–67 | 자주 나는 에러 |
| 요약 | 68 | 한 장 요약 |

## 핵심 개념

### 그래프 읽기

| 모양 | 뜻 |
| --- | --- |
| 점 | 커밋 하나 |
| 흰 점 | 두 줄기를 합친 merge 커밋 |
| 색 이름표 (`main`, `feature/login`) | 브랜치. 커밋 하나를 가리키는 이름표예요 |
| 검은 `HEAD` | 지금 내가 있는 브랜치 |
| 보라 이름표 (`origin/main`) | GitHub에 있는 브랜치 위치 |

### checkout과 switch

`git switch`는 Git 2.23(2019년)에 생긴, 브랜치를 옮기는 일만 하는 명령이에요. checkout은 브랜치 말고 파일을 되돌리는 일도 해서 헷갈리기 쉬워요. 하는 일과 출력은 같으니 편한 쪽을 쓰면 돼요. 슬라이드는 checkout으로 보여 줘요.

| 하는 일 | checkout | switch |
| --- | --- | --- |
| 브랜치로 옮겨 가기 | `git checkout 이름` | `git switch 이름` |
| 만들고 바로 옮겨 가기 | `git checkout -b 이름` | `git switch -c 이름` |

### merge가 끝나는 두 모습

| 모습 | 언제 | 그래프 |
| --- | --- | --- |
| Fast-forward | main에 새 커밋이 없을 때 | main 이름표만 앞으로 옮겨져요 |
| merge 커밋 | main과 브랜치 양쪽에 새 커밋이 있을 때 | 둘을 잇는 흰 점이 새로 생겨요 |

merge 커밋을 만들 때 메시지 편집기가 열려요. 그대로 저장하고 닫으면 돼요. vim이면 Esc를 누르고 `:wq`, Enter를 쳐요.

### 되돌리기 (git reset)

push 전에 커밋을 없던 일로 할 땐 `git reset 옵션 HEAD~1`을 써요. 지금 브랜치 이름표를 한 칸 아래 커밋으로 옮겨요. 일반 커밋이든 merge 커밋이든 명령은 같아요. 옵션은 빠진 커밋의 변경을 어디에 남길지 정해요.

| 옵션 | 빠진 커밋의 변경 | merge를 되돌렸을 때 브랜치 |
| --- | --- | --- |
| `--soft` | 대기실에 남아요 | 그대로 |
| `--mixed` (기본값) | 작업 폴더에 남아요 | 그대로 |
| `--hard` | 지워져요 | 그대로 |

> **주의** `--hard`는 커밋하지 않은 다른 변경까지 지우고 되찾을 수 없어요. 쓰기 전에 `git status`가 깨끗한지 봐요.

일반 커밋을 `--hard`로 지우면 그 변경은 남는 곳이 없어요. merge는 브랜치가 남아 있으면 `git merge 브랜치`로 다시 합칠 수 있어요. 그래서 브랜치는 되돌릴 일이 없는지 확인한 뒤에 지워요. 이미 push한 커밋은 `git revert`로 되돌리고, push한 merge는 팀에 먼저 알려요.

### 브랜치 이름

`타입/하는-일` 형식으로 소문자와 하이픈만 써요.

| 타입 | 쓰는 때 | 예 |
| --- | --- | --- |
| `feature/` | 새 기능 | `feature/login-button` |
| `fix/` | 버그 수정 | `fix/12-login-error` |
| `docs/` | 문서 | `docs/login-guide` |
| `refactor/` | 구조 개선 | `refactor/user-api` |
| `chore/` | 설정, 패키지 | `chore/eslint-setup` |

브랜치는 `feature/`로 시작하지만 그 안에서 하는 커밋 메시지는 `feat:`로 써요. `login`, `final2`처럼 무슨 일인지 모르는 이름이나 `Feature/Login Button`처럼 대문자와 띄어쓰기가 든 이름은 피해요.

## 실습

### 1. 브랜치 만들고 커밋하기

```bash
git branch                          # 브랜치 목록, * 가 지금 있는 곳
git branch feature/login            # 만들기만
git checkout feature/login          # 옮겨 가기 (두 줄을 한 번에: git checkout -b feature/login)
printf "# 로그인\n아이디\n" > login.md
git add login.md
git commit -m "feat: 로그인 화면 추가"
```

### 2. main으로 합치기

merge는 받는 쪽에서 해요. 먼저 main으로 가서 가져올 브랜치 이름을 적어요.

```bash
git checkout main
git merge feature/login
git branch -d feature/login         # 다 쓴 브랜치 지우기
git log --oneline
```

### 3. Pull Request로 합치기

```bash
git checkout -b feature/login-button
echo "로그인 버튼" >> login.md
git add login.md
git commit -m "feat: 로그인 버튼 추가"
git push origin feature/login-button
```

GitHub에서 Pull Request를 만들고 Merge 버튼으로 합쳐요. 그다음 내 컴퓨터의 main도 맞춰요.

```bash
git checkout main
git pull origin main
git branch -d feature/login-button
```

## 충돌 해결

### 기본 순서

1. `git status`로 충돌 난 파일을 찾아요.
2. 파일을 열어 `<<<<<<<`, `=======`, `>>>>>>>` 사이에서 남길 내용만 두고 표시 세 줄을 지워요.
3. `git add 파일`
4. `git commit -m "fix: 충돌 해결"`

`<<<<<<< HEAD` 아래는 지금 내 브랜치 내용이고, `=======` 아래는 합치려는 쪽 내용이에요. 헷갈리면 `git merge --abort`로 합치기 전으로 돌아가요.

### 메시지별 해결

| 메시지 | 상황 | 해결 |
| --- | --- | --- |
| `CONFLICT (content)` | 같은 줄이나 바로 옆 줄을 양쪽에서 고침 | 기본 순서 1~4 |
| `CONFLICT (modify/delete)` | 한쪽은 파일을 지우고 한쪽은 고침 | 지우려면 `git rm 파일`, 남기려면 `git add 파일`, 그다음 commit |
| `CONFLICT (add/add)` | 양쪽이 같은 이름의 새 파일을 만듦 | 기본 순서 1~4 |
| `fatal: Need to specify how to reconcile divergent branches.` | 내 main과 GitHub main이 갈라진 채 pull | 아래 설정을 한 번 하고 다시 `git pull origin main` |
| PR 화면의 `This branch has conflicts` | PR을 올린 사이 main이 같은 곳을 바꿈 | 내 브랜치에서 `git pull origin main`, 충돌을 풀고 `git push origin 브랜치` |

pull할 때 merge로 합치라는 설정이에요. 처음 한 번만 해요.

```bash
git config --global pull.rebase false
```

## 명령어 요약

| 명령 | 하는 일 |
| --- | --- |
| `git branch` | 브랜치 목록 보기 |
| `git branch 이름` | 브랜치 만들기 |
| `git checkout 이름` | 브랜치로 옮겨 가기 |
| `git checkout -b 이름` | 만들고 바로 옮겨 가기 |
| `git switch 이름`, `git switch -c 이름` | checkout과 같은 일 (브랜치 전용) |
| `git merge 이름` | 지금 브랜치로 합치기 |
| `git branch -d 이름` | 합친 브랜치 지우기 |
| `git merge --abort` | 충돌 난 merge 취소 |
| `git reset HEAD~1` | push 전 커밋 취소, 변경은 작업 폴더에 |
| `git reset --hard HEAD~1` | push 전에 끝낸 merge 되돌리기 |
| `git push origin 이름` | 브랜치를 GitHub에 올리기 |
| `git log --oneline` | 커밋 기록과 브랜치 이름표 보기 |

## 문제 해결

| 메시지 | 원인과 해결 |
| --- | --- |
| `pathspec 'feature/nope' did not match` | 없는 브랜치예요. `git branch`로 이름을 확인하고, 새로 만들 땐 `git checkout -b` |
| `invalid reference: feature/nope` | switch에서 없는 브랜치로 갈 때 나와요. 새로 만들 땐 `git switch -c` |
| `a branch named 'feature/login' already exists` | 이미 있어요. `-b`(switch는 `-c`) 없이 `git checkout feature/login` |
| `would be overwritten by checkout` | 고친 내용이 남아 있어요. `git add`, `git commit` 뒤에 옮겨요 |
| `is not fully merged` | 아직 합치지 않은 커밋이 있어요. `git checkout main`, `git merge 브랜치` 뒤에 지워요 |

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen_branch.py    커밋 그래프 장면(g, b, d, r, u, c, p로 시작하는 장) 생성
  gen_pages.py     표지, 목차, 개념, 충돌 시나리오, PR, 에러 장 생성
  check.js         글자 넘침, 겹침, 여백 검사와 스크린샷
  deckrender.js    export.js와 build_player.js가 같이 쓰는 렌더링 코드
  export.js        PDF 내보내기
  build_player.js  애니메이션이 재생되는 HTML 한 파일 만들기
  icons/           아이콘 (Lucide, ISC 라이선스)
git-branch-slides.html  배포용 HTML
git-branch-slides.pdf   강사용 PDF
```

슬라이드 HTML을 직접 고치지 말고 스크립트를 고친 뒤 다시 만들어요.

```bash
python3 tools/gen_branch.py slides
python3 tools/gen_pages.py slides
node tools/check.js slides shots
node tools/build_player.js slides git-branch-slides.html
node tools/export.js slides git-branch-slides.pdf
```

터미널 출력은 git 2.43에서 실제로 실행해 확인했어요. 해시는 날짜를 고정해서 만든 값이라 내 화면과 달라요. 충돌 시나리오 2~6은 시나리오마다 저장소를 따로 만들어 실행했어요. 화면 폭 때문에 줄인 출력은 발표자 노트에 적어 두었어요.

</details>

---

[← 이전: 02 · Git 기본 흐름](../02-git-basics) · [커리큘럼](../README.md)
