# 11 · 터미널에서 GitHub 다루기 (gh)

> GitHub 웹사이트에서 버튼으로 하던 일을 터미널 명령 `gh`(GitHub CLI)로 해요. 브라우저 코드로 로그인하고, 이미 있는 레포를 받고, 새 레포를 만들어요. 레포를 지울 때 권한이 모자라서 막히는 장면과 `gh auth refresh`로 권한을 더하는 법도 봐요. 마지막에 이슈와 PR을 다루는 간단한 명령을 써요. 커밋과 push는 지금까지처럼 git으로 해요.

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/11-gh-cli/gh-cli-slides.html) | [10 · VS Code에서 Jupyter 노트북 쓰기](../10-vscode-jupyter) | 준비 중 |

## 학습 목표

이 챕터를 마치면 다음을 할 수 있어요.

- git, GitHub 웹사이트, gh가 각각 맡는 일을 구분해요.
- `gh auth login`의 질문 네 개에 답하고, 브라우저에 코드를 넣어 로그인해요.
- `gh auth status`에서 로그인한 계정과 권한(scope) 목록을 읽어요.
- `gh repo clone`으로 레포를 받고, 레포 폴더 안에서 `gh repo view`, `gh browse`를 써요.
- `gh repo create`로 내 폴더를 GitHub 레포로 만들고 `git push origin main`으로 올려요.
- `gh repo delete`가 막히면 `gh auth refresh -h github.com -s delete_repo`로 권한을 더한 뒤 지워요.
- `gh issue create`, `gh pr create`, `gh pr merge`로 웹 버튼 없이 이슈와 PR을 다뤄요.

## 시작하기 전에

| 필요한 것 | 배운 곳 |
| --- | --- |
| `git add`, `git commit -m`, `git push origin main` | 02 |
| 브랜치와 Pull Request | 03 |
| 팀 레포 `team-intro` | 06 |
| PR Merge 버튼 세 가지 | 08 |
| Homebrew (Mac) | 09 |

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1–4 | 표지, 오늘의 순서, git·GitHub·gh 구분, 웹 버튼과 gh 명령 짝 |
| 1. 설치하고 로그인하기 | 5–14 | 설치, `gh auth status`, `gh auth login` 질문 네 개, 브라우저 코드, 토큰과 권한 목록, git도 gh로 로그인 |
| 2. 이미 있는 레포 연결하기 | 15–18 | `gh repo clone`, origin 확인, `gh repo view`, `gh browse`, `gh repo list` |
| 3. 새 레포 만들기 | 19–23 | 웹과 비교, 먼저 커밋 만들기, `gh repo create`, `git push origin main`, 질문으로 만들기 |
| 4. 레포 지우기와 권한 추가 | 24–29 | 사라지는 것, 첫 `gh repo delete`의 403, delete_repo 권한, `gh auth refresh`, 다시 지우기 |
| 5. 자주 쓰는 gh 명령 | 30–34 | `gh issue create`·`list`, `gh pr create`·`list`·`view`·`merge`, `gh --help` |
| 정리 | 35–36 | 막힐 때, 한 장 요약 |

## 핵심 개념

### 세 도구가 맡는 일

| 도구 | 하는 일 | 예 |
| --- | --- | --- |
| git | 내 컴퓨터에 기록을 남기고 GitHub과 주고받아요 | `git commit`, `git push origin main` |
| GitHub 웹사이트 | 브라우저로 여는 저장소 집이에요 | New repository, Pull request 버튼 |
| gh | 웹사이트 버튼을 터미널 명령으로 눌러요 | `gh repo create`, `gh pr create` |

gh는 git을 대신하지 않아요. 커밋과 push는 계속 git으로 해요.

### gh auth login 질문 네 개

| 질문 | 고를 것 |
| --- | --- |
| Where do you use GitHub? | GitHub.com |
| What is your preferred protocol for Git operations on this host? | HTTPS |
| Authenticate Git with your GitHub credentials? | Yes |
| How would you like to authenticate GitHub CLI? | Login with a web browser |

화살표로 고르고 Enter로 정해요. 질문이 끝나면 터미널에 나온 여덟 글자 코드를 브라우저(`github.com/login/device`)에 넣고 Continue, Authorize github를 눌러요.

세 번째 질문에서 Yes를 고르면 git도 gh 로그인을 써요. 02의 첫 push에서 뜨던 로그인 창이나 토큰 입력 창이 더는 뜨지 않아요.

### 토큰과 권한(scope)

로그인하면 GitHub이 gh에게 출입증(토큰)을 줘요. 출입증으로 할 수 있는 일의 목록이 권한(scope)이에요. `gh auth status`의 `Token scopes` 줄에서 봐요.

| 권한 | 할 수 있는 일 | 처음 로그인할 때 |
| --- | --- | :---: |
| `repo` | 레포 읽고 쓰기 | 받아요 |
| `read:org` | 조직 정보 보기 | 받아요 |
| `gist` | gist(코드 메모) | 받아요 |
| `workflow` | GitHub Actions 설정 | 받아요 |
| `delete_repo` | 레포 지우기 | 안 받아요 |

실수로 레포를 지우지 않게 `delete_repo`는 처음에 빠져 있어요. 지울 일이 생기면 그때 `gh auth refresh -h github.com -s delete_repo`로 더해요. 여기서 `-h`는 도움말이 아니라 사이트 주소(host), `-s`는 권한(scope)이에요.

### gh repo create 옵션

```bash
gh repo create my-notes --public --source=. --remote=origin
```

| 옵션 | 뜻 |
| --- | --- |
| `my-notes` | GitHub에 만들 레포 이름 |
| `--public` | 누구나 볼 수 있게. 나만 보려면 `--private` |
| `--source=.` | 지금 폴더를 레포로 써요 |
| `--remote=origin` | origin 이름으로 연결해요 |

`--push` 옵션은 붙이지 않아요. 이 과정에서 쓰지 않는 push 설정까지 바꿔요. 만든 뒤 `git push origin main`을 직접 쳐요.

## 실습

명령의 `kim`은 내 GitHub 아이디로 바꿔서 쳐요. 3번에서 만든 `my-notes`로 4번 이슈와 PR을 연습하고, 5번에서 지워요. 슬라이드 5파트는 같은 명령을 `team-intro`에서 보여 줘요.

### 1. 설치하고 로그인

```bash
brew install gh                       # Mac
winget install --id GitHub.cli -e     # Windows. 설치 뒤 Git Bash를 다시 열어요
gh --version
gh auth status                        # 아직 로그인 전
gh auth login                         # GitHub.com, HTTPS, Yes, Login with a web browser
gh auth status                        # Logged in to github.com account 내아이디
```

### 2. 이미 있는 레포 받고 보기

```bash
cd ~/kant
gh repo clone kim/team-intro          # 06에서 받은 폴더가 이미 있으면 건너뛰어요
cd team-intro
git remote -v                         # origin  https://github.com/kim/team-intro.git
gh repo view                          # 레포 이름과 README
gh browse                             # 브라우저로 열기
gh repo list                          # 내 레포 목록
```

### 3. 새 레포 만들고 올리기

```bash
cd ~/kant
mkdir my-notes
cd my-notes
git init
echo '# my-notes' > README.md
git add README.md
git commit -m 'docs: README 추가'
gh repo create my-notes --public --source=. --remote=origin
git remote -v
git push origin main                  # 로그인 창 없이 올라가요
gh repo list                          # my-notes가 생겼어요
```

### 4. 이슈와 PR 만들고 합치기

```bash
gh issue create --title "할 일 적기" --body "README에 할 일을 적어요"
gh issue list
git checkout -b feature/todo
echo '- gh 연습하기' >> README.md
git add README.md
git commit -m 'docs: 할 일 추가'
git push origin feature/todo          # PR 전에 브랜치를 먼저 올려요
gh pr create --title "docs: 할 일 추가" --body "README에 할 일을 적었어요"
gh pr list
gh pr view 2                          # 이슈가 1번이라 PR은 2번이에요
gh pr merge 2 --merge
git checkout main
git pull origin main
git log --oneline                     # 맨 위에 Merge pull request #2
```

### 5. 연습용 레포 지우기

```bash
cd ~/kant
gh repo delete kim/my-notes           # 이름을 한 번 더 치면 HTTP 403
gh auth refresh -h github.com -s delete_repo
gh auth status                        # Token scopes에 'delete_repo'
gh repo delete kim/my-notes           # ✓ Deleted repository kim/my-notes
gh repo list
```

> **주의** 지운 레포는 되돌릴 수 없어요. 연습용 `my-notes`만 지우고, `team-intro`처럼 팀이 쓰는 레포는 지우지 않아요. 내 컴퓨터의 `~/kant/my-notes` 폴더는 남아요.

## 명령어 요약

| 명령 | 하는 일 |
| --- | --- |
| `gh auth login` | 로그인 |
| `gh auth status` | 로그인한 계정과 권한 목록 |
| `gh auth refresh -h github.com -s 권한` | 권한 더하기 |
| `gh repo clone 주인/이름` | 레포 받기 |
| `gh repo view` / `gh browse` | 지금 레포 보기 / 브라우저로 열기 |
| `gh repo list` | 내 레포 목록 |
| `gh repo create 이름 --public --source=. --remote=origin` | 지금 폴더로 레포 만들고 origin 연결 |
| `gh repo delete 주인/이름` | 레포 지우기 |
| `gh issue create` / `gh issue list` | 이슈 만들기 / 목록 |
| `gh pr create` / `gh pr list` / `gh pr view 번호` | PR 만들기 / 목록 / 보기 |
| `gh pr merge 번호 --merge` | PR 합치기 (Create a merge commit) |
| `gh --help` | 명령 묶음 목록 |

## 문제 해결

| 메시지 | 원인과 해결 |
| --- | --- |
| `gh: command not found` | 설치 직후 터미널이 gh를 몰라요. 터미널을 닫고 다시 열어요 |
| `You are not logged into any GitHub hosts` | 로그인 전이에요. `gh auth login` |
| `HTTP 403: Must have admin rights to Repository.` 와 `needs the "delete_repo" scope` | 지우기 권한이 없어요. `gh auth refresh -h github.com -s delete_repo` 뒤 다시 지워요 (슬라이드 25–27쪽) |
| `failed to run git: fatal: not a git repository` | 레포 폴더 밖에서 `gh repo view`, `gh pr list`를 쳤어요. `pwd`로 보고 레포 폴더로 `cd` |
| `? Where should we push the 'feature/…' branch?` | 브랜치를 push하기 전에 `gh pr create`를 쳤어요. Cancel을 고르고 `git push origin 브랜치` 뒤 다시 해요 |
| 브라우저가 저절로 안 열려요 | 터미널의 코드를 보고 `github.com/login/device`를 직접 열어요 |
| `fatal: repository '…' not found` | GitHub에서 지운 레포에 push했어요. 레포 이름과 `git remote -v`를 확인해요 |

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분 (gen.py가 만들어요)
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py           모든 장과 deck.json 생성 (터미널, 브라우저, 권한 칸 그림)
  demo.sh          슬라이드의 gh, git 명령을 실제로 실행 (root 필요)
  demo.py          kim으로 명령을 차례로 치고 화면에 남는 글자를 출력
  drive.py         가상 터미널에서 gh 질문에 답하고 화면 글자를 정리
  mock_github.py   github.com 대신 응답하는 작은 서버 (로그인, 레포, 이슈, PR, git push)
  demo-output.txt  슬라이드에 옮긴 실행 결과
  check.js         글자 넘침, 겹침, 여백 검사와 스크린샷
  deckrender.js    export.js와 build_player.js가 같이 쓰는 렌더링 코드
  export.js        PDF 내보내기
  build_player.js  애니메이션이 재생되는 HTML 한 파일 만들기
  icons/           아이콘 (Lucide, ISC 라이선스)
gh-cli-slides.html  배포용 HTML
gh-cli-slides.pdf   강사용 PDF
```

슬라이드 HTML을 직접 고치지 말고 스크립트를 고친 뒤 다시 만들어요. demo.sh는 python3에 pexpect 패키지가 있어야 해요.

```bash
bash tools/demo.sh > /tmp/gh-cli.log 2>&1        # 실제 출력 확인
python3 tools/gen.py slides
node tools/check.js slides shots
node tools/build_player.js slides gh-cli-slides.html
node tools/export.js slides gh-cli-slides.pdf
```

gh는 스크립트로 진짜 github.com에 로그인할 수 없어요. 그래서 `tools/demo.sh`가 잠깐 `/etc/hosts`에서 github.com과 api.github.com을 이 컴퓨터로 돌리고, `tools/mock_github.py`가 GitHub 대신 응답해요. gh 2.89.0과 git 2.43은 그대로 실행돼요. 질문 화면, 코드 안내, ✓ 줄, 403 뒤의 `gh auth refresh` 안내, 표 모양은 gh가 실제로 출력한 글자예요. 레포 이름, 코드(`8F2A-71C4`), 이슈와 PR 번호, 403 메시지 본문은 mock 서버가 돌려준 값이라 실제와 다를 수 있어요. `remote:`로 시작하는 줄과 받은 바이트 수도 진짜 GitHub과 조금 달라요. 커밋 해시는 실행할 때마다 달라요.

`saved in plain text` 줄은 이 환경에 비밀 보관함이 없어서 나왔어요. Mac 키체인, Windows 자격 증명 관리자가 있으면 보통 나오지 않아요. 설치 화면(brew, winget), 브라우저 화면은 이 환경에서 실행할 수 없어서 출력을 옮기지 않고 단순하게 그렸어요.

</details>

---

[← 이전: 10 · VS Code에서 Jupyter 노트북 쓰기](../10-vscode-jupyter) · [커리큘럼](../README.md)
