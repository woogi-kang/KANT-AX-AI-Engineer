# 09 · uv로 파이썬 시작하기

> 파이썬 프로젝트를 uv 하나로 만들고 실행해요. 먼저 예전 방식(venv, pip, requirements.txt)을 눈으로 보고, uv로 바꾸면 무엇이 줄어드는지 비교해요. 그다음 `uv init`, `uv run`, `uv add`, `uv remove`, `uv sync`를 직접 쳐요. 예제 패키지는 웹 서버를 만드는 fastapi예요. uv가 만든 가상환경을 Mac과 Windows에서 직접 켜는 방법도 봐요. 터미널 명령은 01, GitHub에 올리고 받는 명령은 02, 06과 같아요.

| 슬라이드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/09-python-uv/python-uv-slides.html) | [08 · 갈라진 기록 합치는 방법 비교하기](../08-git-merge-ways) | 준비 중 |

## 학습 목표

이 챕터를 마치면 다음을 할 수 있어요.

- python이 `.py` 파일을 읽어 실행한다는 것과 패키지가 무엇인지 말해요.
- 예전 방식의 순서(파이썬 설치, venv, activate, pip, requirements.txt)를 읽고, 같은 일을 하는 uv 명령으로 바꿔 쳐요.
- `uv init`으로 프로젝트를 만들고 `uv run`으로 실행해요.
- uv가 만든 가상환경을 Mac과 Windows에서 직접 켜고 꺼요.
- `uv add`, `uv remove`가 pyproject.toml, uv.lock, .venv 세 곳을 함께 바꾼다는 걸 알아요.
- GitHub에 올릴 파일과 올리지 않을 파일(.venv)을 구분하고, 받은 프로젝트를 `uv sync`로 똑같이 맞춰요.

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1–2 | 표지, 오늘의 순서 |
| 1. 파이썬은 어떻게 실행되나 | 3–4 | python이 `.py`를 읽어 실행, 패키지와 PyPI |
| 2. 예전 방식 | 5–8 | 여섯 단계, 가상환경(.venv), 실제 터미널, 자주 막히는 곳 네 가지 |
| 3. uv는 무엇이 다른가 | 9–12 | 도구 네 개를 uv 하나로, 할 일별 비교 표, 설치 |
| 4. 프로젝트 만들고 실행하기 | 13–18 | `uv init`, pyproject.toml 읽기, 첫 `uv run`, 두 번째 `uv run`, 가상환경 직접 켜기(Mac, Windows), 파이썬 버전 |
| 5. 패키지 넣고 빼기 | 19–23 | `uv add fastapi uvicorn`, `uv tree`, 웹 서버 켜기, `uv remove`, 캐시 |
| 6. 다른 컴퓨터에서 그대로 | 24–27 | 올릴 파일과 .gitignore, kim에서 lee로, `uv sync` 실제 출력, sync를 치는 때 |
| 정리 | 28–30 | 예전 명령 바꿔 치기, 자주 나오는 메시지, 한 장 요약 |

## 핵심 개념

### 예전 방식과 uv

| 할 일 | 예전 | uv |
| --- | --- | --- |
| 파이썬 설치 | python.org에서 받아 직접 설치 | 없으면 uv가 받아요 |
| 가상환경 | `python3 -m venv .venv` 뒤 `source .venv/bin/activate` | `uv run`, `uv sync`가 알아서 만들고 켜요. 직접 켜도 돼요 |
| 패키지 넣기 | `pip install fastapi uvicorn` 뒤 `pip freeze > requirements.txt` | `uv add fastapi uvicorn` |
| 패키지 빼기 | `pip uninstall fastapi uvicorn` (딸려 온 12개는 남아요) | `uv remove fastapi uvicorn` |
| 다른 컴퓨터 | `pip install -r requirements.txt` | `uv sync` |
| 실행 | 가상환경을 켠 상태에서 `python main.py` | `uv run main.py` |

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

macOS, Linux는 터미널에 붙여 넣어요.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows는 시작 메뉴에서 PowerShell을 열고 붙여 넣어요.

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
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

웹 서버를 만드는 fastapi와 서버를 켜 주는 uvicorn을 넣어요.

```bash
uv add fastapi uvicorn
cat pyproject.toml        # dependencies에 fastapi, uvicorn
uv tree --depth 2         # 두 개와 따라온 패키지
```

VS Code에서 `main.py`를 아래처럼 고쳐 저장해요.

```python
from fastapi import FastAPI
import uvicorn

app = FastAPI()


@app.get("/")
def home():
    return {"message": "안녕하세요"}


if __name__ == "__main__":
    uvicorn.run(app)
```

```bash
uv run main.py            # Uvicorn running on http://127.0.0.1:8000
```

브라우저로 `http://127.0.0.1:8000`을 열면 `{"message":"안녕하세요"}`가 보여요. 터미널로 돌아와 `Ctrl+C`로 서버를 꺼요.

```bash
uv remove fastapi uvicorn # 14개가 함께 빠져요
uv run main.py            # ModuleNotFoundError: No module named 'fastapi'
uv add fastapi uvicorn    # 캐시에 있어서 바로 들어가요
uv run main.py            # 다시 서버가 켜져요. Ctrl+C로 끄기
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
uv run main.py        # 서버가 켜져요. Ctrl+C로 끄기
```

팀원이 패키지를 넣고 push했으면 `git pull origin main` 뒤 `uv sync`로 내 `.venv`를 맞춰요.

## 명령어 요약

| 명령 | 하는 일 |
| --- | --- |
| `uv --version` | uv가 설치됐는지 확인 |
| `uv init 이름` | 프로젝트 폴더 만들기 (pyproject.toml, .python-version, main.py, git init) |
| `uv init --python 3.13 이름` | 파이썬 버전을 정해서 만들기 |
| `uv run main.py` | 프로젝트 가상환경에서 실행. 처음엔 .venv와 uv.lock을 만들어요 |
| `uv run python --version` | 이 프로젝트의 파이썬 버전 보기 |
| `uv add 패키지` | 패키지 넣기 (pyproject.toml, uv.lock, .venv) |
| `uv remove 패키지` | 패키지 빼기 (딸려 온 패키지까지) |
| `uv tree --depth 2` | 패키지가 어떤 패키지 때문에 들어왔는지 두 단계까지 보기 |
| `uv sync` | uv.lock대로 .venv 맞추기 (clone 직후, pull 뒤) |
| `source .venv/bin/activate` | 가상환경 직접 켜기 (Windows Git Bash는 `.venv/Scripts/activate`) |
| `deactivate` | 켠 가상환경 끄기 |

## 문제 해결

| 증상 | 원인과 해결 |
| --- | --- |
| `bash: uv: command not found` (Mac은 `zsh: command not found: uv`) | 설치 뒤 터미널을 새로 열지 않았어요. 터미널을 닫고 다시 열어요 |
| ``error: No `pyproject.toml` found in current directory or any parent directory`` | 프로젝트 폴더 밖이에요. `pwd`로 위치를 보고 `cd hello-uv` |
| `ModuleNotFoundError: No module named 'fastapi'` | 패키지를 넣지 않았거나 가상환경을 켜지 않고 `python3 main.py`로 실행했어요. `uv add fastapi uvicorn` 뒤 `uv run main.py` |
| `uv run main.py` 뒤 프롬프트가 돌아오지 않아요 | 서버가 켜져 기다리는 중이에요. `Ctrl+C`로 꺼요 |
| `ERROR: [Errno 98] error while attempting to bind on address ('127.0.0.1', 8000): [errno 98] address already in use` (번호는 운영체제마다 달라요) | 다른 터미널에 서버가 이미 켜져 있어요. 그 터미널에서 `Ctrl+C` |
| `error: Project is already initialized in ...` | 이미 만든 프로젝트 안이에요. `uv init`은 처음 한 번만 쳐요 |
| 자료에 `pip install 패키지`가 나와요 | 우리 프로젝트에서는 `uv add 패키지`로 바꿔 쳐요 |
| `.python-version` 숫자가 슬라이드와 달라요 | 컴퓨터에 이미 있던 파이썬을 썼어요. 그대로 써도 돼요 |

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분 (gen.py가 만들어요)
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py           모든 장과 deck.json 생성 (폴더 그림, 세 곳 카드, 비교 표)
  demo.sh          모든 명령을 새 폴더에서 다시 실행해 실제 출력 확인
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

터미널 출력은 `tools/demo.sh`로 uv 0.11.32, Python 3.14.6에서 실제로 실행해 옮겼어요. uv 캐시와 파이썬 설치 폴더를 실습 폴더 안에 새로 만들어서, 파이썬이 없는 컴퓨터처럼 첫 실행에 파이썬을 받아요. lee 컴퓨터는 캐시와 파이썬 폴더를 따로 둬서 처음 받는 모습을 재현했어요. 예전 방식은 uv가 받은 Python 3.14.6을 `python3`로 써서 실행했어요. 웹 서버는 백그라운드로 켜고 `curl`로 브라우저처럼 한 번 열어 본 뒤 Ctrl+C 신호로 껐어요. 이 확인 요청 때문에 실제 출력에는 GET 줄이 두 번 나와서 슬라이드에는 한 줄만 남겼어요. GitHub 자리는 내 컴퓨터의 빈 저장소로 대신하고 주소만 `https://github.com/kim/hello-uv.git`으로 보이게 했어요. 출력의 폴더 주소는 01처럼 `/home/kim`으로 바꿨어요. 설치 스크립트 출력은 버전마다 달라서 옮기지 않았어요. 화면 폭 때문에 뺀 줄은 발표자 노트에 적어 두었어요. 패키지 버전과 걸린 시간(ms)은 실행한 날에 따라 달라요.

</details>

---

[← 이전: 08 · 갈라진 기록 합치는 방법 비교하기](../08-git-merge-ways) · [커리큘럼](../README.md)
