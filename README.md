# KANT AX/AI 엔지니어 트랙 · 학습 자료

KANT AX/AI 엔지니어 트랙의 공식 학습 자료 저장소예요. 터미널, Git, GitHub CLI(gh), 파이썬 프로젝트 도구 uv처럼 개발을 시작할 때 매일 쓰는 도구를 다뤄요. 명령을 칠 때마다 무엇이 바뀌는지 애니메이션 슬라이드로 보여 줘요.

## 커리큘럼

<!-- curriculum:chapters -->

| 챕터 | 분&#8288;류 | 한 줄 목표 | 핵심 명령 | 슬&#8288;라&#8288;이&#8288;드 |
| --- | --- | --- | --- | --- |
| [01 · 터미널 기초](./01-linux-terminal) | 터&#8288;미&#8288;널 | 터미널에서 폴더와 파일을 만들고 옮기고 지워요 | `pwd` `ls` `cd` `mkdir` `rm` | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/01-linux-terminal/linux-terminal-slides.html) |
| [02 · Git 기본 흐름](./02-git-basics) | G&#8288;i&#8288;t | 변경을 커밋하고 GitHub에 올리고 받아요 | `add` `commit` `push` `pull` `clone` | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/02-git-basics/git-basics-slides.html) |
| [03 · Git 브랜치와 협업](./03-git-branch) | G&#8288;i&#8288;t | 브랜치에서 작업하고 합치고 충돌을 풀어요 | `branch` `checkout` `merge` `reset` Pull Request | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/03-git-branch/git-branch-slides.html) |
| [04 · Git diff로 확인하기](./04-git-diff) | G&#8288;i&#8288;t | add, commit, merge 전에 무엇이 바뀌는지 확인해요 | `diff` `diff --staged` `show` `.gitignore` | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/04-git-diff/git-diff-slides.html) |
| [05 · VS Code Git Graph로 기록 보기](./05-git-graph) | G&#8288;i&#8288;t | 터미널로 만든 커밋과 브랜치를 그림으로 확인해요 | Git Graph 확장, HEAD, `origin/main` | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/05-git-graph/git-graph-slides.html) |
| [06 · 팀 레포에서 같이 작업하고 충돌 풀기](./06-team-repo) | G&#8288;i&#8288;t | 팀원과 레포 하나에서 push, pull하고 충돌을 풀어요 | Collaborator 초대, `pull`, 충돌 해결, PR | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/06-team-repo/team-repo-slides.html) |
| [07 · 커밋 전 변경 취소하기와 잠깐 보관하기](./07-git-restore-stash) | G&#8288;i&#8288;t | 커밋 전 변경을 버리거나 잠깐 치워 둬요 | `restore` `restore --staged` `stash` `stash pop` | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/07-git-restore-stash/git-restore-stash-slides.html) |
| [08 · 갈라진 기록 합치는 방법 비교하기](./08-git-merge-ways) | G&#8288;i&#8288;t | merge, rebase, squash 결과를 나란히 비교해요 | `merge --no-ff` `rebase` `merge --squash` pull 설정 | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/08-git-merge-ways/git-merge-ways-slides.html) |
| [09 · uv로 파이썬 시작하기](./09-python-uv) | 파&#8288;이&#8288;썬 | uv로 파이썬 프로젝트를 만들고 패키지를 넣어요 | `uv init` `uv run` `uv add` `uv remove` `uv sync` | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/09-python-uv/python-uv-slides.html) |
| [10 · VS Code에서 Jupyter 노트북 쓰기](./10-vscode-jupyter) | 파&#8288;이&#8288;썬 | 노트북 셀을 실행하고 마크다운으로 정리해요 | `Shift+Enter`, 마크다운 셀, Restart, `type()` | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/10-vscode-jupyter/vscode-jupyter-slides.html) |
| [11 · 터미널에서 GitHub 다루기 (gh)](./11-gh-cli) | G&#8288;i&#8288;t&#8288;H&#8288;u&#8288;b | 레포 만들기와 PR을 터미널에서 해요 | `gh auth login` `gh repo create` `gh repo clone` `gh pr create` | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/11-gh-cli/gh-cli-slides.html) |
| [12 · 파이썬 기초 1 (변수, 타입, 연산)](./12-python-basics) | 파&#8288;이&#8288;썬 | 변수에 값을 담아 계산하고 비교해요 | `=` `type()` `//` `%` `and` | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/12-python-basics/python-basics-slides.html) |
| [13 · 파이썬 기초 2 (문자열, 리스트, for)](./13-python-strings-lists) | 파&#8288;이&#8288;썬 | 문자열과 리스트로 영수증을 찍어요 | `word[0:2]` f-string `[ ]` `append` `for` | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/13-python-strings-lists/python-strings-lists-slides.html) |
| [14 · 파이썬 기초 3 (in, 2차원 리스트)](./14-python-2d-lists) | 파&#8288;이&#8288;썬 | 값이 들어 있는지 묻고 표 모양 데이터를 다뤄요 | `in` `not in` `scores[1][2]` `len(scores[0])` | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/14-python-2d-lists/python-2d-lists-slides.html) |
| [15 · 파이썬 기초 4 (딕셔너리)](./15-python-dict) | 파&#8288;이&#8288;썬 | 키로 값을 찾고 바꾸는 딕셔너리를 다뤄요 | `{키: 값}` `menu["latte"]` `get` `del` `items()` | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/15-python-dict/python-dict-slides.html) |
| [16 · 파이썬 기초 5 (집합)](./16-python-sets) | 파&#8288;이&#8288;썬 | 중복을 없애고 두 목록에서 겹치는 값을 찾아요 | `set()` `add` `discard` `\|` `&` `-` | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/16-python-sets/python-sets-slides.html) |
| [17 · 제어문 1 (조건문 if)](./17-python-if) | 파&#8288;이&#8288;썬 | 조건에 따라 실행할 줄을 골라요 | `if` `elif` `else` `and` `not in` | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/17-python-if/python-if-slides.html) |
| [18 · 제어문 2 (반복 제어 while, break)](./18-python-while) | 파&#8288;이&#8288;썬 | 조건이 맞는 동안 반복하고 필요하면 멈춰요 | `range()` `enumerate()` `while` `break` `continue` | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/18-python-while/python-while-slides.html) |
| [19 · 함수 1 (정의, 매개변수, return)](./19-python-functions) | 파&#8288;이&#8288;썬 | 자주 쓰는 코드를 함수로 묶고 결과를 돌려받아요 | `def` `이름()` 매개변수 `return` `None` | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/19-python-functions/python-functions-slides.html) |
| [20 · 함수 2 (기본값, 지역 변수와 전역 변수)](./20-python-scope) | 파&#8288;이&#8288;썬 | 기본값을 쓰고 함수 안과 밖의 변수를 구분해요 | `size="M"` 키워드 인자 지역 변수 `global` `x = f(x)` | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/20-python-scope/python-scope-slides.html) |
| [21 · 함수 3 (lambda, map, filter)](./21-python-lambda) | 파&#8288;이&#8288;썬 | 짧은 함수를 lambda로 만들고 map, filter로 리스트 전체에 써요 | `lambda x: x + 10` `map` `filter` `list(map(...))` | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/21-python-lambda/python-lambda-slides.html) |
| [22 · 정렬과 sorted, max, min 제대로 쓰기](./22-python-sorting) | 파&#8288;이&#8288;썬 | key로 비교 기준을 정해 줄 세우고 가장 큰 값을 골라요 | `sorted(key=)` `sort()` `reverse=True` `max(d, key=d.get)` `default=` | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/22-python-sorting/python-sorting-slides.html) |
| [23 · 리스트 컴프리헨션](./23-python-comprehension) | 파&#8288;이&#8288;썬 | 바꾸고 고르는 for를 대괄호 한 줄로 써요 | `[x for x in xs]` `if` `if else` `{k: v for ...}` `{x for ...}` | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/23-python-comprehension/python-comprehension-slides.html) |
| [24 · 클래스 1 (붕어빵 틀과 붕어빵)](./24-python-class) | 파&#8288;이&#8288;썬 | class로 틀을 만들고 __init__과 self로 붕어빵마다 값을 담아요 | `class Bread:` `__init__` `self.flavor` `def intro(self):` | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/24-python-class/python-class-slides.html) |
| [25 · 클래스 2 (`__str__`과 `__repr__`)](./25-python-str-repr) | 파&#8288;이&#8288;썬 | print와 리스트에서 붕어빵이 알아보기 쉽게 보이게 만들어요 | `__str__` `__repr__` `str()` `repr()` `sorted(key=lambda b: b.price)` | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/25-python-str-repr/python-str-repr-slides.html) |
| [26 · 클래스 3 (상속과 클래스 변수)](./26-python-inheritance) | 파&#8288;이&#8288;썬 | 틀을 물려받아 다른 점만 적고, 모두 같이 쓰는 값은 틀에 둬요 | `Bread.shop` `class Dog(Animal):` `super().__init__()` `isinstance()` | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/26-python-inheritance/python-inheritance-slides.html) |
| [27 · 클래스 4 (캡슐화)](./27-python-encapsulation) | 파&#8288;이&#8288;썬 | 칸은 안에 감추고, 메서드와 property라는 문으로만 꺼내고 바꾸게 해요 | `self._stamps` `self.__password` `get_password()` `@property` `@password.setter` | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/27-python-encapsulation/python-encapsulation-slides.html) |
| [28 · 미니 프로젝트: 장바구니 (들여쓰기, items, 모듈)](./28-python-modules) | 파&#8288;이&#8288;썬 | 장바구니 프로젝트로 들여쓰기 상자, items() 꺼내 담기, 파일을 나누는 import를 읽고 써요 | `for p, q in d.items():` `import product` `from product import Product` `import coupon as cp` `if __name__ == "__main__":` | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/28-python-modules/python-modules-slides.html) |
| [29 · Docker 1 (컨테이너 실행하기)](./29-docker-basics) | D&#8288;o&#8288;c&#8288;k&#8288;e&#8288;r | Docker Desktop을 설치하고 Docker Hub의 공식 이미지를 받아서 컨테이너를 켜고 끄고 지워요 | `docker pull nginx` `docker run -d --name web -p 8080:80 nginx` `docker ps -a` `docker stop web` `docker rm web` | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/29-docker-basics/docker-basics-slides.html) |
| [30 · Docker 2 (내 프로그램을 이미지로 만들기)](./30-docker-image) | D&#8288;o&#8288;c&#8288;k&#8288;e&#8288;r | 장바구니를 Dockerfile로 내 이미지로 만들고, 볼륨과 compose로 컨테이너를 실행해요 | `docker exec -it web bash` `-v ./site:/usr/share/nginx/html` `docker build -t cart .` `.dockerignore` `docker compose up -d` | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/30-docker-image/docker-image-slides.html) |
| [31 · nginx 기초 (웹 서버와 리버스 프록시)](./31-nginx-basics) | D&#8288;o&#8288;c&#8288;k&#8288;e&#8288;r | nginx로 파일을 내주고, 리버스 프록시로 앱 여러 개를 80번 포트 하나로 묶어요 | `curl localhost/menu/` `location / { root ...; }` `proxy_pass http://menu/;` `docker exec cafe-web-1 nginx -t` `docker exec cafe-web-1 nginx -s reload` | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/31-nginx-basics/nginx-basics-slides.html) |

<!-- /curriculum:chapters -->

챕터는 번호 순서대로 이어져요. 앞 챕터에서 만든 폴더와 저장소를 다음 챕터에서 그대로 써요.

## 번외

정규 챕터와 따로 보는 보충 자료예요. 순서 없이 필요한 것만 골라 봐요. 목록은 [extras](./extras)에도 있어요.

<!-- curriculum:extras -->

| 제&#8288;목 | 다루는 내용 | 슬&#8288;라&#8288;이&#8288;드 |
| --- | --- | --- |
| [터미널 환경에 적응하기](./extras/terminal-path-help) | 탐색기와 터미널 맞춰 보기(`cd ..` `cd -` `cd ~`), 위치에 따라 달라지는 명령, `-h`와 `--help`, origin과 main 이름의 관례, git과 uv 도움말 읽기 | [열&#8288;기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/extras/terminal-path-help/terminal-path-help-slides.html) |

<!-- /curriculum:extras -->

## 학습 방법

1. 커리큘럼 표의 **열기**를 눌러 슬라이드를 브라우저에서 봐요.
2. 챕터 폴더의 `README.md`를 열고 실습 명령을 터미널에서 한 줄씩 따라 쳐요.
3. 막히면 챕터 README의 문제 해결 표에서 같은 메시지를 찾아요.

| 키 | 동작 |
| --- | --- |
| `→` `Space` | 다음 (애니메이션을 하나씩) |
| `←` | 이전 |
| 숫자 뒤 `Enter` | 그 장으로 가기 (`12` `Enter`면 12장) |
| `R` | 지금 장 애니메이션 다시 보기 |
| `A` | 애니메이션 끄고 켜기 |
| `N` | 발표자 노트 열고 닫기 |
| `F` | 전체 화면 |
| `?` | 단축키 안내 열고 닫기 |

마우스를 화면에 올리면 아래 가운데에 작은 막대가 나타나요. 아이콘에 마우스를 올리면 이름과 단축키가 보이고, `?` 버튼을 누르면 위 키 표가 열려요. 발표자 노트(`N`)는 오른쪽 아래에 카드로 떠요. 첫 줄에 그 장의 요점이 나오고, 아래 칸에 애니메이션이 몇 번째인지와 다음 장 제목이 보여요. 노트 카드는 창처럼 다뤄요. 위쪽을 잡고 끌면 옮겨지고, 가장자리나 오른쪽 아래 모서리를 끌면 크기가 바뀌어요. 옮긴 자리와 크기는 브라우저가 기억해요. 위쪽을 두 번 누르면 처음 자리로 돌아가요.

마우스로는 화면 양옆의 화살표 버튼을 눌러서 넘겨요. 버튼을 누르면 남은 애니메이션을 건너뛰고 바로 장이 넘어가요. 슬라이드를 클릭하거나 글자를 드래그해서 선택해도 장이 넘어가지 않아서 편하게 복사할 수 있어요. 코드 칸에 마우스를 올리면 오른쪽 위에 복사 버튼이 떠요. 터미널 칸은 `$` 뒤의 명령만 복사해요.

앞 장으로 돌아가면 애니메이션이 끝난 완성된 화면이 나와요. 다시 앞으로 가도 이미 본 애니메이션은 다시 나오지 않아요. 애니메이션을 처음부터 다시 보고 싶으면 `R`이나 아래 막대의 다시 보기 버튼(↻)을 눌러요. 복습할 때 `A`로 애니메이션을 끄면 한 번 누를 때마다 한 장씩 넘어가요. 끈 상태는 브라우저가 기억해요.

주소 끝에 `#12`처럼 번호를 붙이면 그 장부터 열려요. 아래 막대의 쪽 번호(`22 / 45`)를 누르고 숫자를 쳐도 돼요.

## 릴리스 노트

슬라이드와 자료에서 개선된 점을 스크린샷과 함께 알려 드려요.

<!-- curriculum:updates -->

| 날&#8288;짜 | 릴리스 노트 | 바뀐 점 |
| --- | --- | --- |
| 2026-11-09 | [발표자 노트를 원하는 자리로 옮기고 크기를 바꿀 수 있어요](./updates/2026-11-09-notes-window) | 노트 카드 위쪽을 끌면 옮겨지고, 가장자리나 모서리를 끌면 크기가 바뀌어요. 자리와 크기는 브라우저가 기억하고, 위쪽을 두 번 누르면 처음 자리로 돌아가요 |
| 2026-11-08 | [애니메이션 다시 보기가 추가되고 아래 막대와 발표자 노트가 보기 좋아졌어요](./updates/2026-11-08-slide-replay) | `R` 키나 ↻ 버튼으로 지금 장의 애니메이션을 처음부터 다시 봐요. 아래 막대는 아이콘만 남겨 간단해졌고, 단축키는 `?`로 열어 봐요. 발표자 노트는 요점이 먼저 보이는 카드로 바뀌었어요 |
| 2026-11-05 | [클래스 슬라이드에 직접 눌러 보는 장이 추가되었어요](./updates/2026-11-05-class-labs) | 24 붕어빵 기계, 25 누가 불릴까, 26 어디서부터 찾을까. 버튼을 누르면 코드가 한 줄씩 실행되고 메서드를 찾는 순서가 그림으로 보여요 |

지난 릴리스 노트는 [전체 목록](./updates)에서 봐요.

<!-- /curriculum:updates -->

## 실습 환경

| 운영체제 | 터미널 | 비고 |
| --- | --- | --- |
| macOS | 터미널 앱 | 기본 설치 |
| Windows | Git Bash | [Git for Windows](https://git-scm.com/download/win)를 설치하면 함께 설치 |
| Linux | 기본 터미널 | 기본 설치 |

슬라이드의 출력은 bash 5.2, GNU coreutils 9.4, git 2.43, uv 0.11.32(Python 3.14), gh 2.89.0에서 실제로 실행한 결과예요. 커밋 해시와 집합(set)을 찍은 순서는 실행할 때마다 달라요.

## 과정 규칙

모든 챕터가 같은 규칙을 따라요.

| 항목 | 규칙 |
| --- | --- |
| push, pull | `git push origin main`, `git pull origin main`처럼 원격과 브랜치를 끝까지 적어요. `-u`는 쓰지 않아요 |
| pull 설정 | 처음 한 번 `git config --global pull.rebase false`. pull은 merge로 합쳐요. `pull.rebase true`, `pull.ff only`는 08에서 비교로만 봐요 |
| 원격과 비교 | `git fetch origin` 뒤에 `git log --oneline`, `git log --oneline origin/main`. `--graph`, `--all`은 쓰지 않아요 |
| 그림으로 보기 | VS Code의 Git Graph로 결과만 확인해요. checkout, merge, reset은 Git Graph 메뉴 대신 터미널에서 쳐요 |
| 커밋 | `git add 파일` 뒤 `git commit -m "..."`. `-am`은 쓰지 않아요 |
| 커밋 전 되돌리기 | `git restore`, `git stash`는 07에서 배워요. 01~06 자료에는 나오지 않아요 |
| 합치는 방법 | `rebase`, `merge --squash`, `--no-ff`는 08에서 배워요. rebase는 push 전 내 브랜치에만 쓰고, push한 브랜치와 main에서는 쓰지 않아요 |
| 커밋 메시지 | [Conventional Commits](https://www.conventionalcommits.org/ko/v1.0.0/) 형식: `feat:` `fix:` `docs:` … |
| 브랜치 이동 | 슬라이드는 `git checkout`으로 보여 줘요. 같은 일을 하는 `git switch`도 03에서 소개해요 |
| 파이썬 프로젝트 | `uv init`으로 만들고 `uv run`으로 실행해요. 패키지는 `uv add`, `uv remove`. 가상환경을 직접 켤 땐 `source .venv/bin/activate`(Windows Git Bash는 `.venv/Scripts/activate`). uv 설치는 Mac `brew install uv`, Windows `winget install --id=astral-sh.uv -e`. `pip install`은 09에서 예전 방식 비교로만 봐요 |
| GitHub CLI (gh) | 11에서 배워요. 로그인은 `gh auth login`(HTTPS, 브라우저). `gh repo create`에는 `--push`를 붙이지 않고 `git push origin main`을 직접 쳐요. 레포 지우기 권한은 `gh auth refresh -h github.com -s delete_repo`로 더해요 |
| 문자열 포맷팅 | 13의 1파트에서 `%`, `format()`, f-string을 나란히 봐요. 새 코드는 f-string으로 적고, 그 앞 자료에는 f-string을 쓰지 않아요 |
| 제어문 | `if`, `elif`, `else`는 17, `range()`, `enumerate()`, `while`, `break`, `continue`는 18에서 배워요. 그 앞 자료는 `if`가 들어간 코드를 "참고, 읽기만"으로만 보여 줘요 |
| 함수 | `def`, 매개변수와 인자, `return`, `None`은 19, 기본값, 키워드 인자, 지역 변수와 전역 변수, `global`은 20에서 배워요. 바깥 값을 바꿀 땐 `global`보다 인자로 넣고 `return`으로 돌려받는 쪽을 권해요 |
| 함수 넘기기, 정렬, 컴프리헨션 | `lambda`, `map`, `filter`는 21, `sorted`·`max`·`min`의 `key=`와 `default=`는 22, 리스트·딕셔너리·집합 컴프리헨션은 23에서 배워요. `reduce`, `zip()`, `*args`는 다루지 않아요 |
| 클래스 | `class`, `__init__`, `self`, 메서드는 24, `__str__`, `__repr__`은 25, 클래스 변수, 상속, `super()`, `isinstance()`는 26, `_`, `__`, getter와 setter, `@property`는 27에서 붕어빵 틀과 붕어빵으로 배워요. `classmethod`, 다중 상속, `dataclass`는 다루지 않아요 |
| Docker | 29에서 Docker Desktop 설치, Docker Hub 공식 마크, `docker run`, `ps`, `stop`, `start`, `restart`, `rm`, `rmi`, `logs`, `-p 8080:80`, `-it`로 우분투 컨테이너 안에 들어가기를 배워요. 이미지는 Docker Official Image 마크부터 골라요. 명령은 Windows Git Bash, Mac 터미널에서 쳐요. 30에서 `docker exec -it`, 볼륨 `-v`, Dockerfile 다섯 줄(`astral/uv` 이미지)로 장바구니를 이미지로 만들기, `.dockerignore`, `docker compose up -d`를 배워요. Git Bash에서는 `export MSYS_NO_PATHCONV=1`을 먼저 쳐요. 31에서 nginx로 파일 내주기와 리버스 프록시(`proxy_pass`)를 배우고, 앱 서버 자리에는 연습용 이미지 `traefik/whoami`를 써요. |
| 브랜치 이름 | `feature/login`, `fix/12-login-error`, `docs/login-guide`처럼 `타입/하는-일` |

## 저장소 구조

```
.
├── 01-linux-terminal/
├── 02-git-basics/
├── 03-git-branch/
│   ├── README.md                 챕터 안내 (학습 목표, 실습, 문제 해결)
│   ├── git-branch-slides.html    슬라이드 (브라우저용)
│   ├── git-branch-slides.pdf     슬라이드 (강사용 인쇄본)
│   ├── slides/                   슬라이드 원본 (한 장에 한 파일)
│   └── tools/                    이 챕터만 쓰는 생성 스크립트
├── …                             04부터 마지막 챕터까지 같은 모양
├── extras/                       번외 자료 (주제마다 폴더 하나)
│   └── terminal-path-help/
├── updates/                      릴리스 노트 (날짜마다 폴더 하나, 스크린샷 포함)
├── tools/                        모든 챕터가 같이 쓰는 검사, HTML, PDF 도구와 README 표 만들기
├── templates/                    새 챕터 README 틀
├── curriculum.json               챕터, 번외, 릴리스 노트 목록 (README 표의 원본)
└── CLAUDE.md                     자료 작성 규칙
```

## 자료를 고칠 때

- 슬라이드를 고치면 챕터 폴더에서 HTML과 PDF를 다시 만들어요. 명령은 챕터 README의 강사용 절에 있어요.
- 커리큘럼 표, 번외 표, 챕터 README 맨 위 표와 맨 아래 이동 링크는 `curriculum.json`에서 만들어요. 목록을 고친 뒤 `python3 tools/build_readme.py`를 쳐요. 표를 README에서 직접 고치면 다음에 다시 만들 때 사라져요.
- 새 챕터는 맨 뒤 번호로 만들고 `templates/chapter-README.md`를 복사해서 시작해요. 덱은 [CLAUDE.md](./CLAUDE.md)의 "덱 만들기 흐름" 다섯 단계(준비, 내용 틀, 덱 만들기, 배포 전 점검, 배포)를 차례대로 따라요. 장 순서는 그 안의 "챕터 설계 틀"(왜 필요한가부터 실제 상황 예제까지)이에요. 이미 올린 챕터의 번호와 폴더 이름은 바꾸지 않아요.
- 번외는 `extras/주제` 폴더에 번호 없이 만들고 `curriculum.json`의 `extras`에 한 줄 더해요.
- 글쓰기와 폴더 규칙은 [CLAUDE.md](./CLAUDE.md)를 따라요.
