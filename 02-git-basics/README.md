# 02 · Git 기본 흐름

> 명령을 칠 때마다 파일이 어느 칸으로 가는지 보며 Git을 익혀요. 내 컴퓨터에 저장소를 만들고, GitHub에 올리고, 팀원과 주고받고, 실수를 되돌리는 데까지 이어서 해요.

| 슬라이드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/02-git-basics/git-basics-slides.html) | [01 · 터미널 기초](../01-linux-terminal) | [03 · Git 브랜치와 협업](../03-git-branch) |

## 학습 목표

이 챕터를 마치면 다음을 할 수 있어요.

- 작업 폴더, 대기실, 내 저장소, GitHub 네 칸으로 Git의 흐름을 설명해요.
- `git status`로 파일 상태를 읽고 `add`, `commit`으로 기록을 남겨요.
- GitHub 저장소를 연결해 `push origin main`, `pull origin main`, `clone`으로 주고받아요.
- 상황에 맞게 `reset`, `revert`, `reflog`로 커밋을 되돌려요.
- 커밋 메시지를 Conventional Commits 형식으로 써요.

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 1. 개념 잡기 | 3–8 | 네 칸, 파일 상태 |
| 2. 혼자 기록하기 | 9–18 | `config` `init` `add` `commit`, 커밋 메시지 규칙 |
| 3. GitHub과 연결 | 19–23 | 빈 저장소 만들기, `remote add`, `push` |
| 4. 함께 작업하기 | 24–28 | `clone` `fetch` `pull` |
| 5. 되돌리기 | 29–35 | `reset` `reflog` `revert` |
| 6. 문제 해결 | 36–42 | `git status` 읽기, 자주 나는 에러 |
| 요약 | 43 | 한 장 요약 |

## 핵심 개념

### 네 칸

Git의 모든 명령은 파일을 아래 네 칸 사이로 옮기는 일이에요.

| 칸 | 이름 | 실제 위치 |
| :---: | --- | --- |
| ① | 작업 폴더 (Working Directory) | 내가 파일을 고치는 폴더 |
| ② | 대기실 (Staging Area) | `.git/index` |
| ③ | 내 저장소 (Local Repository) | `.git` 폴더 |
| ④ | 원격 저장소 (Remote) | GitHub |

```
① 작업 폴더 --add--> ② 대기실 --commit--> ③ 내 저장소 --push origin main--> ④ GitHub
① 작업 폴더 <------------------ pull origin main ------------------------- ④ GitHub
```

### 파일 상태

| 상태 | 뜻 | `git status` 화면 |
| --- | --- | --- |
| Untracked | Git이 처음 보는 새 파일 | `Untracked files:` 아래 빨간 글씨 |
| Staged | add 해서 대기실에 올린 파일 | `Changes to be committed:` 아래 초록 글씨 |
| Committed | 마지막 커밋과 똑같은 파일 | `nothing to commit, working tree clean` |
| Modified | 커밋한 뒤에 고친 파일 | `Changes not staged for commit:` 아래 빨간 글씨 |

### 커밋 메시지

`타입: 무엇을 했는지` 형식으로 써요.

| 타입 | 쓰는 때 |
| --- | --- |
| `feat` | 새 기능 |
| `fix` | 버그 수정 |
| `docs` | README 같은 문서 |
| `style` | 동작은 그대로, 모양만 정리 |
| `refactor` | 동작은 그대로, 구조 개선 |
| `test` | 테스트 코드 |
| `chore` | 설정, 패키지 |

## 실습

이름, 이메일, 주소의 `kim`은 내 것으로 바꿔서 쳐요.

### 1. 처음 한 번만 설정

```bash
git config --global user.name "홍길동"
git config --global user.email "gildong@example.com"
git config --global init.defaultBranch main
```

### 2. 혼자 기록하기

```bash
mkdir hello-git && cd hello-git
git init
echo "hello" > hello.md
git status                      # Untracked
git add hello.md
git status                      # Staged
git commit -m "feat: 인사 파일 추가"
```

### 3. GitHub에 올리기

GitHub에서 `hello-git`이라는 빈 저장소를 먼저 만들어요. README 추가는 체크하지 않아요.

```bash
git remote add origin https://github.com/kim/hello-git.git
git remote -v
git push origin main
```

### 4. 받아 오기

```bash
git clone https://github.com/kim/hello-git.git   # 처음 받을 때
cd hello-git

git fetch origin                                  # 받아만 오기
git log --oneline origin/main                     # GitHub 쪽 기록 보기
git pull origin main                              # 받아서 합치기
```

GitHub과 비교할 땐 `git fetch origin` 뒤에 기록을 봐요.

- `git log --oneline`에서 `main`이 `origin/main`보다 위에 있으면 `git push origin main`
- `git log --oneline origin/main`에서 `origin/main`이 `main`보다 위에 있으면 `git pull origin main`

이 과정은 `git push -u`를 쓰지 않아요. 그래서 `git status`는 GitHub보다 앞섰는지 뒤처졌는지 알려 주지 않아요.

## 커밋 되돌리기

push 했는지부터 확인해요.

| 상황 | 명령 | 결과 |
| --- | --- | --- |
| push 전 | `git reset HEAD~1` | 커밋만 취소하고 고친 내용은 작업 폴더에 남아요 |
| push 후 | `git revert 커밋해시` | 반대로 고친 커밋을 하나 더 쌓아요. 팀원 기록은 그대로예요 |
| reset을 잘못했을 때 | `git reflog` | 지운 커밋의 해시를 찾아 `git reset --hard 해시`로 돌아가요 |

> **주의** `git reset --hard`는 작업 폴더에서 고친 내용까지 지워요. 쓰기 전에 `git status`로 남은 변경이 없는지 확인해요.

## 명령어 요약

| 명령 | 하는 일 |
| --- | --- |
| `git init` | 지금 폴더를 저장소로 만들기 |
| `git status` | 파일 상태 보기 |
| `git add 파일` | 대기실에 올리기 |
| `git commit -m "타입: 내용"` | 기록 남기기 |
| `git log --oneline` | 기록 보기 |
| `git remote add origin 주소` | GitHub 저장소 연결 |
| `git push origin main` | GitHub에 올리기 |
| `git clone 주소` | GitHub 저장소 처음 받기 |
| `git fetch origin` | 받아만 오기 |
| `git pull origin main` | 받아서 합치기 |
| `git reset HEAD~1` | push 전 커밋 취소 |
| `git revert 해시` | push 후 커밋 되돌리기 |

## 문제 해결

| 메시지 | 원인과 해결 |
| --- | --- |
| `index.lock': File exists` | 다른 git 작업이 끝났는지 확인한 뒤 `.git/index.lock` 파일 하나만 지우고 다시 실행 |
| `nothing added to commit` | 대기실이 비어 있어요. `git add` 먼저 |
| `remote origin already exists` | 이미 등록돼 있어요. `git remote -v`로 확인하고 바꿀 땐 `git remote set-url origin 새주소` |
| `'origin' does not appear to be a git repository` | 아직 등록하지 않았어요. `git remote add origin 주소` |
| `has no upstream branch` | `git push`만 쳤어요. `git push origin main`처럼 끝까지 적어요 |
| `! [rejected] ... (fetch first)` | GitHub에 내가 모르는 커밋이 있어요. `git pull origin main` 뒤에 다시 push. `--force`는 쓰지 않아요 |

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen_scenes.py    네 칸 실습 장면(s1~s18) 생성
  check.js         글자 넘침, 겹침, 여백 검사와 스크린샷
  deckrender.js    export.js와 build_player.js가 같이 쓰는 렌더링 코드
  export.js        PDF 내보내기
  build_player.js  애니메이션이 재생되는 HTML 한 파일 만들기
  icons/           아이콘 (Lucide, ISC 라이선스)
git-basics-slides.html  배포용 HTML
git-basics-slides.pdf   강사용 PDF
```

실습 장면은 `slides/s*.html`을 직접 고치지 말고 스크립트를 고친 뒤 다시 만들어요.

```bash
python3 tools/gen_scenes.py slides
node tools/check.js slides shots                          # 전체 검사 (Playwright 필요)
node tools/check.js slides shots reflog                   # 특정 장만
node tools/build_player.js slides git-basics-slides.html
node tools/export.js slides git-basics-slides.pdf
```

터미널 출력은 git 2.43에서 실제로 실행해 확인했어요. 해시는 이야기 흐름에 맞춰 고정한 값이라 내 화면과 달라요.

</details>

---

[← 이전: 01 · 터미널 기초](../01-linux-terminal) · [커리큘럼](../README.md) · [다음: 03 · Git 브랜치와 협업 →](../03-git-branch)
