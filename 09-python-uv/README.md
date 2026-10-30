# 09 · uv로 파이썬 시작하기

> 파이썬 프로젝트를 uv 하나로 만들고 실행해요. 먼저 예전 방식(venv, pip, requirements.txt)과 uv를 한 장에 나란히 놓고 비교해요. 그다음 `uv init`, `uv run`, `uv add`, `uv remove`, `uv sync`를 직접 쳐요. 예제 패키지는 웹 서버를 만드는 fastapi예요. uv가 만든 가상환경을 Mac과 Windows에서 직접 켜는 방법도 봐요. 마지막으로 머신러닝 수업에서 쓸 Jupyter 노트북을 VS Code에서 여는 준비까지 해요. 터미널 명령은 01, GitHub에 올리고 받는 명령은 02, 06과 같아요.

| 슬라이드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/09-python-uv/python-uv-slides.html) | [08 · 갈라진 기록 합치는 방법 비교하기](../08-git-merge-ways) | [10 · VS Code에서 Jupyter 노트북 쓰기](../10-vscode-jupyter) |

## 학습 목표

이 챕터를 마치면 다음을 할 수 있어요.

- python이 `.py` 파일을 읽어 실행한다는 것과 패키지가 무엇인지 말해요.
- 예전 방식의 여섯 단계가 uv 명령 세 개(`uv init`, `uv add`, `uv run`)로 줄어드는 것을 설명해요.
- Mac은 `brew`, Windows는 `winget`으로 uv를 설치해요.
- `uv init`으로 프로젝트를 만들고 `uv run`으로 실행해요.
- uv가 만든 가상환경을 Mac과 Windows에서 직접 켜고 꺼요.
- `uv add`, `uv remove`가 pyproject.toml, uv.lock, .venv 세 곳을 함께 바꾼다는 걸 알아요.
- GitHub에 올릴 파일과 올리지 않을 파일(.venv)을 구분하고, 받은 프로젝트를 `uv sync`로 똑같이 맞춰요.
- VS Code에 Python, Jupyter 확장을 설치하고, `uv add --dev ipykernel` 뒤 노트북 커널로 `.venv`를 골라 셀을 실행해요.

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1–2 | 표지, 오늘의 순서 |
| 1. 파이썬은 어떻게 실행되나 | 3–4 | python이 `.py`를 읽어 실행, 패키지와 PyPI |
| 2. 예전 방식과 비교 | 5–7 | 가상환경(.venv), 예전 6단계와 uv 3개 나란히 보기, uv가 대신 해 주는 세 가지 |
| 3. uv 설치하기 | 8 | Mac `brew install uv`, Windows `winget install --id=astral-sh.uv -e` |
| 4. 프로젝트 만들고 실행하기 | 9–14 | `uv init`, pyproject.toml 읽기, 첫 `uv run`, 두 번째 `uv run`, 가상환경 직접 켜기(Mac, Windows), 파이썬 버전 |
| 5. 패키지 넣고 빼기 | 15–19 | `uv add "fastapi[standard]"`, `uv tree`, `uv run fastapi dev main.py`로 웹 서버 켜기, `uv remove`, 캐시 |
| 6. 다른 컴퓨터에서 그대로 | 20–23 | 올릴 파일과 .gitignore, kim에서 lee로, `uv sync` 실제 출력, sync를 치는 때 |
| 7. VS Code에서 Jupyter 쓰기 | 24–29 | 노트북과 셀, Python과 Jupyter 확장 설치, `uv add --dev ipykernel`, 커널로 .venv 고르기, 셀 실행, 막힐 때 |
| 정리 | 30–32 | 예전 명령 바꿔 치기, 자주 나오는 메시지, 한 장 요약 |

## 핵심 개념

### 예전 방식과 uv

| 할 일 | 예전 | uv |
| --- | --- | --- |
| 파이썬 설치 | python.org에서 받아 설치 | 없으면 uv가 받아요 |
| 프로젝트 만들기 | `python3 -m venv .venv` | `uv init hello-uv` |
| 가상환경 켜기 | `source .venv/bin/activate` | `uv run`이 알아서 켜요. 직접 켜도 돼요 |
| 패키지 넣기 | `pip install "fastapi[standard]"` | `uv add "fastapi[standard]"` |
| 목록 적기 | `pip freeze > requirements.txt` | `uv add`가 알아서 적어요 |
| 실행 | 켠 상태에서 `fastapi dev main.py` | `uv run fastapi dev main.py` |

예전 여섯 단계 가운데 직접 치는 uv 명령은 세 개예요. 패키지를 뺄 때도 차이가 나요. `pip uninstall fastapi`는 fastapi 하나만 지우고 함께 들어온 58개를 남겨요. `uv remove fastapi`는 59개를 모두 빼요. 받은 프로젝트는 `pip install -r requirements.txt` 대신 `uv sync` 한 번이면 돼요.

예전 방식은 따라 치지 않아요. 인터넷 자료에 `pip install 패키지`가 나오면 우리 프로젝트에서는 `uv add 패키지`로 바꿔 쳐요. pip로 넣으면 pyproject.toml과 uv.lock에 적히지 않아서 다른 컴퓨터에서 `uv sync`로 받을 수 없어요.

### uv add가 바꾸는 세 곳

| 파일 | 하는 일 | GitHub에 |
| --- | --- | --- |
| `pyproject.toml` | 프로젝트 설명서. 내가 고른 패키지(`dependencies`)가 적혀요 | 올려요 |
| `uv.lock` | 따라온 패키지까지 정확한 버전이 적혀요 | 올려요 |
| `.venv/` | 패키지가 실제로 설치된 가상환경 | 올리지 않아요 (`.gitignore`에 있어요) |

`.python-version`은 이 폴더에서 쓸 파이썬 버전이에요. 이것도 올려요. 세 파일만 있으면 다른 컴퓨터에서 `uv sync` 한 번으로 같은 `.venv`를 만들어요.

> **주의** pyproject.toml과 uv.lock은 손으로 고치지 않아요. `uv add`, `uv remove`로만 바꿔요.

### 가상환경 직접 켜기

`uv run`이 실행할 때마다 `.venv`를 켜고 꺼요. 터미널에서 `python`을 여러 번 칠 때는 직접 켜도 돼요. 켜면 프롬프트 앞에 `(hello-uv)`가 붙어요.

| 터미널 | 켜기 | 끄기 |
| --- | --- | --- |
| macOS, Linux 터미널 | `source .venv/bin/activate` | `deactivate` |
| Windows Git Bash | `source .venv/Scripts/activate` | `deactivate` |
| Windows PowerShell | `.venv\Scripts\activate` | `deactivate` |

켠 상태에서는 `python main.py`로 실행해요. 켜는 걸 잊어도 `uv run main.py`는 늘 동작해서, 수업 실습은 `uv run`으로 적어요. PowerShell에서 스크립트 실행이 막혔다는 오류가 나면 Git Bash에서 켜요.

## 실습

### 0. uv 설치 (컴퓨터마다 한 번)

macOS는 터미널에서 Homebrew로 설치해요. `brew --version`에 버전이 나오지 않으면 [brew.sh](https://brew.sh)의 설치 명령으로 Homebrew부터 설치해요.

```bash
brew install uv
```

Windows는 시작 메뉴에서 PowerShell을 열고 winget으로 설치해요. 약관 동의를 물으면 `Y`를 쳐요.

```powershell
winget install --id=astral-sh.uv -e
```

설치가 끝나면 터미널(Windows는 Git Bash)을 닫았다가 새로 열고 확인해요.

```bash
uv --version
```

### 1. 프로젝트 만들고 실행하기

수업 저장소 `hello-git` 안이 아니라 홈 폴더에서 시작해요.

```bash
cd ~
uv init hello-uv
cd hello-uv
ls -a                 # .git .gitignore .python-version README.md main.py pyproject.toml
uv run main.py        # 처음엔 .venv를 만들고 Hello from hello-uv!
ls -a                 # .venv, uv.lock이 생겼어요
uv run main.py        # 두 번째는 바로 Hello from hello-uv!
```

가상환경을 직접 켜 봐요. Windows Git Bash는 `source .venv/Scripts/activate`예요.

```bash
source .venv/bin/activate   # 프롬프트 앞에 (hello-uv)
which python                # .../hello-uv/.venv/bin/python
python main.py              # Hello from hello-uv!
deactivate                  # 끄기
```

### 2. 패키지 넣고, 쓰고, 빼기

웹 서버를 만드는 fastapi를 넣어요. `[standard]`는 서버를 켜는 도구까지 함께 넣으라는 뜻이에요. Mac 터미널(zsh)은 대괄호를 특별한 글자로 읽어서 큰따옴표까지 그대로 쳐요.

```bash
uv add "fastapi[standard]"
cat pyproject.toml        # dependencies에 "fastapi[standard]>=0.162.0"
uv tree --depth 2         # fastapi와 따라온 패키지
```

VS Code에서 `main.py`를 아래처럼 고쳐 저장해요.

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def home():
    return {"message": "안녕하세요"}
```

```bash
uv run fastapi dev main.py    # Server started at http://127.0.0.1:8000
```

브라우저로 `http://127.0.0.1:8000`을 열면 `{"message":"안녕하세요"}`가 보여요. 터미널로 돌아와 `Ctrl+C`로 서버를 꺼요.

```bash
uv remove fastapi             # 59개가 함께 빠져요
uv run fastapi dev main.py    # error: Failed to spawn: `fastapi`
uv add "fastapi[standard]"    # 캐시에 있어서 바로 들어가요
uv run fastapi dev main.py    # 다시 서버가 켜져요. Ctrl+C로 끄기
```

### 3. GitHub에 올리고 다른 컴퓨터에서 받기

GitHub에서 빈 저장소 `hello-uv`를 만든 뒤 02처럼 연결하고 올려요. `kim` 자리에 내 GitHub 아이디를 넣어요.

```bash
git status --short    # .venv가 목록에 없어요
git add .
git commit -m "feat: hello-uv 프로젝트 만들기"
git remote add origin https://github.com/kim/hello-uv.git
git push origin main
```

팀원(lee) 컴퓨터에서는 이렇게 받아요. 혼자라면 `mkdir ~/lee` 뒤 `cd ~/lee`에서 해 봐요.

```bash
git clone https://github.com/kim/hello-uv.git
cd hello-uv
uv sync               # 파이썬, .venv, 패키지를 uv.lock대로
uv run fastapi dev main.py   # 서버가 켜져요. Ctrl+C로 끄기
```

팀원이 패키지를 넣고 push했으면 `git pull origin main` 뒤 `uv sync`로 내 `.venv`를 맞춰요.

### 4. VS Code에서 Jupyter 노트북 쓰기

1. VS Code 왼쪽 확장 아이콘을 눌러요. 단축키는 Mac `Cmd+Shift+X`, Windows `Ctrl+Shift+X`예요.
2. `Python`을 검색해서 만든 곳이 Microsoft인 확장을 설치해요.
3. `Jupyter`를 검색해서 만든 곳이 Microsoft인 확장을 설치하고 VS Code를 다시 열어요.

터미널에서 노트북 커널을 넣어요.

```bash
cd ~/hello-uv
uv add --dev ipykernel    # pyproject.toml의 [dependency-groups] dev에 적혀요
```

1. VS Code에서 File > Open Folder로 `hello-uv` 폴더 자체를 열어요.
2. 왼쪽 탐색기에서 새 파일 `notebook.ipynb`를 만들어요.
3. 오른쪽 위 Select Kernel을 누르고 Python Environments를 골라요.
4. `.venv (Python 3.14.6)`를 골라요. 숫자는 컴퓨터마다 달라요.
5. 셀에 아래를 적고 `Shift+Enter`로 실행해요.

```python
import sys
print(sys.executable)     # .../hello-uv/.venv/bin/python 이면 맞게 고른 거예요
```

VS Code가 ipykernel을 설치하라는 알림을 띄우면 Install을 누르지 말고 위의 `uv add --dev ipykernel`을 쳐요. Install은 pip로 넣어서 pyproject.toml에 적히지 않아요.

## 명령어 요약

| 명령 | 하는 일 |
| --- | --- |
| `uv --version` | uv가 설치됐는지 확인 |
| `uv init 이름` | 프로젝트 폴더 만들기 (pyproject.toml, .python-version, main.py, git init) |
| `uv init --python 3.13 이름` | 파이썬 버전을 정해서 만들기 |
| `uv run main.py` | 프로젝트 가상환경에서 실행. 처음엔 .venv와 uv.lock을 만들어요 |
| `uv run python --version` | 이 프로젝트의 파이썬 버전 보기 |
| `uv add 패키지` | 패키지 넣기 (pyproject.toml, uv.lock, .venv) |
| `uv add "fastapi[standard]"` | fastapi와 서버를 켜는 도구 넣기 |
| `uv run fastapi dev main.py` | fastapi 서버 켜기. `Ctrl+C`로 꺼요 |
| `uv remove 패키지` | 패키지 빼기 (딸려 온 패키지까지) |
| `uv tree --depth 2` | 패키지가 어떤 패키지 때문에 들어왔는지 두 단계까지 보기 |
| `uv sync` | uv.lock대로 .venv 맞추기 (clone 직후, pull 뒤) |
| `uv add --dev ipykernel` | 노트북 커널 넣기. 개발용 칸(dev)에 적혀요 |
| `source .venv/bin/activate` | 가상환경 직접 켜기 (Windows Git Bash는 `.venv/Scripts/activate`) |
| `deactivate` | 켠 가상환경 끄기 |

## 문제 해결

| 증상 | 원인과 해결 |
| --- | --- |
| `bash: uv: command not found` (Mac은 `zsh: command not found: uv`) | 설치 뒤 터미널을 새로 열지 않았어요. 터미널을 닫고 다시 열어요 |
| ``error: No `pyproject.toml` found in current directory or any parent directory`` | 프로젝트 폴더 밖이에요. `pwd`로 위치를 보고 `cd hello-uv` |
| `ModuleNotFoundError: No module named 'fastapi'` | 패키지를 넣지 않았거나 가상환경을 켜지 않고 `python3 main.py`로 실행했어요. `uv add "fastapi[standard]"` 뒤 `uv run fastapi dev main.py` |
| ``error: Failed to spawn: `fastapi` `` | fastapi를 넣지 않았어요. `uv add "fastapi[standard]"` |
| `RuntimeError: To use the fastapi command, please install "fastapi[standard]"` | `[standard]` 없이 `uv add fastapi`로 넣었어요. 메시지의 pip install 대신 `uv add "fastapi[standard]"` |
| `uv run fastapi dev main.py` 뒤 프롬프트가 돌아오지 않아요 | 서버가 켜져 기다리는 중이에요. `Ctrl+C`로 꺼요 |
| `ERROR:    [Errno 98] Address already in use` (번호는 운영체제마다 달라요) | 다른 터미널에 서버가 이미 켜져 있어요. 그 터미널에서 `Ctrl+C` |
| `error: Project is already initialized in ...` | 이미 만든 프로젝트 안이에요. `uv init`은 처음 한 번만 쳐요 |
| 자료에 `pip install 패키지`가 나와요 | 우리 프로젝트에서는 `uv add 패키지`로 바꿔 쳐요 |
| `.python-version` 숫자가 슬라이드와 달라요 | 컴퓨터에 이미 있던 파이썬을 썼어요. 그대로 써도 돼요 |
| 노트북에서 ipykernel을 설치하라는 알림이 떠요 | Install 대신 터미널에서 `uv add --dev ipykernel`. 그다음 커널을 다시 골라요 |
| 커널 목록에 `.venv`가 없어요 | `hello-uv` 폴더 자체를 열었는지 봐요. `uv sync` 뒤 VS Code를 다시 열어요 |
| 노트북 셀에서 `ModuleNotFoundError` | 커널이 `.venv`가 아니에요. 오른쪽 위 커널 이름을 눌러 `.venv`로 바꿔요 |

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분 (gen.py가 만들어요)
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py           모든 장과 deck.json 생성 (폴더 그림, 세 곳 카드, 나란히 비교)
  demo.sh          모든 명령을 새 폴더에서 다시 실행해 실제 출력 확인
  run_nb.py        노트북 셀을 프로젝트 커널로 실행해 출력 확인 (demo.sh가 불러요)
  check.js         글자 넘침, 겹침, 여백 검사와 스크린샷
  deckrender.js    export.js와 build_player.js가 같이 쓰는 렌더링 코드
  export.js        PDF 내보내기
  build_player.js  애니메이션이 재생되는 HTML 한 파일 만들기
  icons/           아이콘 (Lucide, ISC 라이선스)
python-uv-slides.html  배포용 HTML
python-uv-slides.pdf   강사용 PDF
```

슬라이드 HTML을 직접 고치지 말고 스크립트를 고친 뒤 다시 만들어요.

```bash
bash tools/demo.sh /tmp/uv-demo > /tmp/uv-demo.log 2>&1
python3 tools/gen.py slides
node tools/check.js slides shots
node tools/build_player.js slides python-uv-slides.html
node tools/export.js slides python-uv-slides.pdf
```

터미널 출력은 `tools/demo.sh`로 uv 0.11.32, Python 3.14.6에서 실제로 실행해 옮겼어요. uv 캐시와 파이썬 설치 폴더를 실습 폴더 안에 새로 만들어서, 파이썬이 없는 컴퓨터처럼 첫 실행에 파이썬을 받아요. lee 컴퓨터는 캐시와 파이썬 폴더를 따로 둬서 처음 받는 모습을 재현했어요. 예전 방식은 uv가 받은 Python 3.14.6을 `python3`로 써서 실행했어요. 웹 서버는 백그라운드로 켜고 `curl`로 브라우저처럼 한 번 열어 본 뒤 Ctrl+C 신호로 껐어요. 이 확인 요청 때문에 실제 출력에는 GET 줄이 두 번 나와서 슬라이드에는 한 줄만 남겼어요. `fastapi dev`가 찍는 첫 줄들의 그림 문자(⚡️, 🌐)도 실제 출력 그대로예요. 예전 방식의 `pip uninstall fastapi` 뒤 남은 58개는 `pip freeze | wc -l`로 셌어요. 노트북 셀 출력은 `tools/run_nb.py`가 hello-uv 복사본의 커널(ipykernel)로 셀을 실행한 결과예요. VS Code 화면(확장, 커널 고르기)은 이 환경에서 띄울 수 없어서 단순하게 그렸어요. GitHub 자리는 내 컴퓨터의 빈 저장소로 대신하고 주소만 `https://github.com/kim/hello-uv.git`으로 보이게 했어요. 출력의 폴더 주소는 01처럼 `/home/kim`으로 바꿨어요. `brew install uv`, `winget install` 출력은 이 환경에서 칠 수 없고 버전마다 달라서 옮기지 않았어요. 화면 폭 때문에 뺀 줄은 발표자 노트에 적어 두었어요. 패키지 버전과 걸린 시간(ms)은 실행한 날에 따라 달라요.

</details>

---

[← 이전: 08 · 갈라진 기록 합치는 방법 비교하기](../08-git-merge-ways) · [커리큘럼](../README.md) · [다음: 10 · VS Code에서 Jupyter 노트북 쓰기 →](../10-vscode-jupyter)
