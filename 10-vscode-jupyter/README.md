# 10 · VS Code에서 Jupyter 노트북 쓰기

> 09에서 VS Code에 Jupyter를 연결하고 첫 셀을 실행했어요. 이번 챕터는 노트북을 손에 익혀요. 셀을 실행하는 키 세 가지, 실행 번호 읽는 법, Restart와 Run All, 명령 모드와 편집 모드를 차례로 봐요. 수업에서 정한 변수 이름 규칙과 컨벤션(표기법)은 마크다운 셀에 정리해요. 마지막에 Windows와 Mac 단축키를 한 표로 모았어요.

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/10-vscode-jupyter/vscode-jupyter-slides.html) | [09 · uv로 파이썬 시작하기](../09-python-uv) | 준비 중 |

## 학습 목표

이 챕터를 마치면 다음을 할 수 있어요.

- 노트북 화면에서 커널, 위쪽 버튼, 선택 막대, 실행 번호, 출력을 찾아요.
- 코드 셀과 마크다운 셀을 구분하고 서로 바꿔요.
- `Ctrl+Enter`, `Shift+Enter`, `Alt+Enter`의 차이를 말해요. Mac은 `control+Enter`, `option+Enter`예요.
- 대괄호 숫자가 실행한 순서라는 것을 알고, 꼬였을 때 Restart 뒤 Run All로 다시 실행해요.
- 명령 모드와 편집 모드를 `Esc`, `Enter`로 오가고, 명령 모드 글자 키(A, B, D D, Z, M, Y, L)를 써요.
- 마크다운 셀에 `---`, `###`, `-`로 규칙을 정리하고, 변수 이름 규칙과 세 가지 표기법을 구분해요.

## 시작하기 전에

09의 7파트를 먼저 끝내요. 이 챕터는 그 위에서 시작해요.

| 할 일 | 09 슬라이드 |
| --- | :---: |
| VS Code에 Python, Jupyter 확장(Microsoft) 설치 | 25쪽 |
| `uv add --dev ipykernel`로 커널 넣기 | 26쪽 |
| 노트북 커널로 `.venv` 고르기 | 27쪽 |

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1–3 | 표지, 오늘의 순서, 09에서 한 준비와 새 노트북 만들기 |
| 1. 노트북 화면 읽기 | 4–5 | 화면의 다섯 곳, 코드 셀과 마크다운 셀 |
| 2. 셀 실행하기 | 6–12 | `Ctrl+Enter`, `Shift+Enter`, `Alt+Enter`, 실행 번호와 커널이 기억하는 값, 같은 셀 다시 실행, Restart와 Run All, 위쪽 버튼 |
| 3. 명령 모드와 편집 모드 | 13–18 | 두 모드와 `Esc`·`Enter`, 키로만 셀 만들기(네 장), 명령 모드 글자 키 |
| 4. 마크다운 셀로 규칙 정리하기 | 19–21 | 마크다운 셀에 변수 이름 규칙 적기, 규칙을 어긴 이름의 SyntaxError, 컨벤션(스네이크, 파스칼, 카멜 표기법) |
| 5. 단축키 모음 | 22–23 | 실행하고 셀 다루는 키, 글 고치는 키와 파일 키 (Windows, Mac 나란히) |
| 정리 | 24–25 | 막힐 때, 한 장 요약 |

## 핵심 개념

### 셀 실행하는 세 가지 키

| 하는 일 | Windows | Mac |
| --- | --- | --- |
| 실행하고 그 셀에 머물기 | `Ctrl+Enter` | `control+Enter` |
| 실행하고 다음 셀로 (마지막 셀이면 새 셀) | `Shift+Enter` | `Shift+Enter` |
| 실행하고 바로 아래에 새 셀 | `Alt+Enter` | `option+Enter` |

Mac의 실행 키는 Cmd가 아니라 control이에요. VS Code 기본 설정이 그래요. 처음에는 `Shift+Enter` 하나만 써도 충분해요.

### 실행 번호와 커널

셀 왼쪽 `[1]`, `[2]`는 실행한 순서예요. 화면 위아래 순서가 아니에요. 값은 커널 하나가 계속 기억해서 앞 셀에서 만든 `x`를 뒤 셀이 그대로 써요.

같은 셀을 다시 실행하면 번호가 새로 붙고 값도 다시 바뀌어요. Restart는 커널이 기억한 값을 모두 지워요. 그 뒤 아래 셀만 실행하면 `NameError`가 나요. 꼬였다 싶으면 Restart 뒤 Run All로 맨 위부터 다시 실행해요.

| 위쪽 버튼 | 하는 일 |
| --- | --- |
| Run All | 맨 위부터 끝까지 실행 |
| Restart | 커널이 기억한 값 지우기 |
| Interrupt | 실행 중인 셀 멈추기 (실행 중에만 보여요) |
| Clear All Outputs | 화면의 출력만 지우기. 값은 남아요 |
| Variables | 커널이 기억하는 값을 표로 보기 |

### 명령 모드와 편집 모드

| 모드 | 화면 | 하는 일 | 들어가는 키 |
| --- | --- | --- | --- |
| 명령 모드 | 셀 왼쪽 막대만 | 셀 추가, 삭제, 종류 바꾸기 | `Esc` |
| 편집 모드 | 막대와 셀 테두리, 커서 | 셀 안의 글자 고치기 | `Enter` 또는 셀 안 클릭 |

명령 모드 글자 키는 Windows와 Mac이 같아요. Shift 없이 그냥 눌러요.

| 키 | 하는 일 |
| --- | --- |
| `A` / `B` | 위 / 아래에 셀 추가 |
| `D` `D` | 셀 지우기 (D를 두 번) |
| `Z` | 지운 셀 되살리기 |
| `M` / `Y` | 마크다운 셀로 / 코드 셀로 |
| `L` | 줄 번호 켜고 끄기 |
| `Alt+↑` `Alt+↓` (Mac `option`) | 셀 위아래로 옮기기 |

한글 입력 상태에서는 글자 키가 먹지 않을 수 있어요. 한/영 키로 영문으로 바꿔요.

### 변수 이름 규칙과 컨벤션

| 규칙 | 틀린 예 | 실제 오류 | 이렇게 |
| --- | --- | --- | --- |
| 숫자로 시작 불가 | `1st_name` | `SyntaxError: invalid decimal literal` | `first_name` |
| 공백 불가 | `my name` | `SyntaxError: invalid syntax` | `my_name` |
| 하이픈(-) 불가 | `my-name` | `SyntaxError: cannot assign to expression here.` | `my_name` |
| 예약어 사용 불가 | `class` | `SyntaxError: invalid syntax` | `class_name` |

예약어는 `if`, `for`, `class`, `True`, `None`처럼 파이썬이 이미 쓰는 단어예요. 셀에서 `import keyword` 뒤 `keyword.kwlist`를 실행하면 전체 목록이 나와요.

| 컨벤션 | 예 | 파이썬에서 |
| --- | --- | --- |
| 스네이크 표기법 (snake_case) | `user_name` | 변수, 함수 이름. 우리는 이걸 써요 |
| 파스칼 표기법 (PascalCase) | `UserProfile` | 클래스 이름 |
| 카멜 표기법 (camelCase) | `userName` | 잘 안 써요. 자바스크립트에서 많이 써요 |

## 실습

### 1. 노트북 열기

VS Code에서 File > Open Folder로 09의 `hello-uv` 폴더 자체를 열어요. 09에서 만든 `notebook.ipynb`를 열고 오른쪽 위 커널이 `.venv`인지 봐요. 새로 만들 땐 명령 팔레트(`Ctrl+Shift+P`, Mac `Cmd+Shift+P`)에서 `Create: New Jupyter Notebook`을 골라요.

### 2. 실행 키 세 가지

셀 두 개에 아래를 적어요.

```python
x = 10
```

```python
print(x * 2)
```

1번 셀을 클릭하고 차례로 눌러 봐요. 누를 때마다 파란 막대가 어디로 가는지 봐요.

1. `Ctrl+Enter` (Mac `control+Enter`): 막대가 1번 셀에 그대로 있어요.
2. `Shift+Enter`: 막대가 2번 셀로 내려가요.
3. `Alt+Enter` (Mac `option+Enter`): 바로 아래에 빈 셀이 생겨요.

### 3. 실행 순서와 Restart

맨 아래 셀에 아래를 적고 두 번 실행해요. 출력이 11, 12로 바뀌고 번호도 새로 붙어요.

```python
x = x + 1
x
```

1. 위쪽 Restart를 눌러요.
2. `print(x * 2)` 셀만 실행해요. `NameError: name 'x' is not defined`가 나요.
3. Run All을 눌러요. 맨 위부터 다시 실행해서 오류가 사라져요.

### 4. 키로만 마크다운 셀 만들기

1. 아무 코드 셀 안을 클릭하고 `Esc`를 쳐요. 명령 모드가 돼요.
2. `B`를 쳐요. 아래에 새 셀이 생겨요.
3. `M`을 쳐요. 셀 오른쪽 아래 글자가 Markdown으로 바뀌어요.
4. `Enter`를 치고 `# 오늘 배운 것`을 적어요.
5. `Shift+Enter`로 실행해요. 꾸며진 제목이 돼요.

### 5. 마크다운 셀에 규칙 정리하기

명령 모드에서 `B`, `M`, `Enter` 순서로 마크다운 셀을 만들고 아래를 적어요. `Shift+Enter`로 실행하면 가로줄, 작은 제목, 목록으로 바뀌어요.

```markdown
---
### 변수 이름 규칙

- 숫자로 시작 불가
- 공백 불가
- 하이픈(-) 불가
- 예약어 사용 불가

### 컨벤션

- 스네이크 표기법: user_name
- 파스칼 표기법: UserProfile
- 카멜 표기법: userName
```

아래에 코드 셀을 만들고 `my-name = "kim"`을 실행해 SyntaxError를 직접 봐요. `my_name = "kim"`으로 고치면 오류 없이 실행돼요.

다 했으면 `Ctrl+S`(Mac `Cmd+S`)로 저장해요.

## 단축키 요약

| 하는 일 | Windows | Mac |
| --- | --- | --- |
| 실행하고 머물기 | `Ctrl+Enter` | `control+Enter` |
| 실행하고 다음 셀로 | `Shift+Enter` | `Shift+Enter` |
| 실행하고 아래에 새 셀 | `Alt+Enter` | `option+Enter` |
| 명령 모드로 / 편집 모드로 | `Esc` / `Enter` | `Esc` / `Enter` |
| 셀 추가, 지우기, 종류 (명령 모드) | `A` `B` `D D` `M` `Y` | `A` `B` `D D` `M` `Y` |
| 셀 옮기기 (명령 모드) | `Alt+↑` `Alt+↓` | `option+↑` `option+↓` |
| 주석 넣고 빼기 (편집 모드) | `Ctrl+/` | `Cmd+/` |
| 되돌리기 (편집 모드) | `Ctrl+Z` | `Cmd+Z` |
| 노트북에서 찾기 | `Ctrl+F` | `Cmd+F` |
| 저장 | `Ctrl+S` | `Cmd+S` |
| 명령 팔레트 | `Ctrl+Shift+P` | `Cmd+Shift+P` |

단축키가 안 먹으면 명령 팔레트에서 `Preferences: Open Keyboard Shortcuts`를 열고 `notebook`으로 검색해 지금 키를 확인해요.

## 문제 해결

| 증상 | 원인과 해결 |
| --- | --- |
| 글자를 쳤는데 셀이 생기거나 지워져요 | 명령 모드였어요. 셀 안을 클릭하거나 `Enter` |
| `A`, `B`, `M`을 눌러도 아무 일이 없어요 | 편집 모드거나 한글 입력 상태예요. `Esc`를 치고 한/영 키로 영문으로 |
| `NameError: name 'x' is not defined` | 앞 셀을 안 돌렸거나 Restart 뒤예요. Run All |
| `SyntaxError: invalid syntax` | 설명 글을 코드 셀에 적었어요. 명령 모드에서 `M` |
| 셀이 끝나지 않고 계속 돌아요 | 위쪽 Interrupt로 멈춰요 |
| Mac에서 `Cmd+Enter`로 실행이 안 돼요 | Mac 실행 키는 `control+Enter`예요 |
| 대괄호 숫자가 뒤죽박죽이에요 | 누른 순서대로 실행했어요. Restart 뒤 Run All |
| 셀에서 `ModuleNotFoundError` | 커널이 `.venv`가 아니에요. 09의 문제 해결 표를 봐요 |
| ipykernel을 설치하라는 알림이 떠요 | Install 대신 터미널에서 `uv add --dev ipykernel` (09) |

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분 (gen.py가 만들어요)
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py           모든 장과 deck.json 생성 (노트북 화면, 키 캡, 단축키 표)
  demo.sh          hello-uv를 새로 만들고 노트북 셀을 실제로 실행해 출력 확인
  run_nb.py        셀을 프로젝트 커널로 실행 (demo.sh가 불러요)
  check.js         글자 넘침, 겹침, 여백 검사와 스크린샷
  deckrender.js    export.js와 build_player.js가 같이 쓰는 렌더링 코드
  export.js        PDF 내보내기
  build_player.js  애니메이션이 재생되는 HTML 한 파일 만들기
  icons/           아이콘 (Lucide, ISC 라이선스)
vscode-jupyter-slides.html  배포용 HTML
vscode-jupyter-slides.pdf   강사용 PDF
```

슬라이드 HTML을 직접 고치지 말고 스크립트를 고친 뒤 다시 만들어요.

```bash
bash tools/demo.sh /tmp/nb-demo > /tmp/nb-demo.log 2>&1
python3 tools/gen.py slides
node tools/check.js slides shots
node tools/build_player.js slides vscode-jupyter-slides.html
node tools/export.js slides vscode-jupyter-slides.pdf
```

셀 출력(20, `'안녕하세요, kim'`, 11, 12, NameError, 이름 규칙 SyntaxError 네 가지)은 `tools/demo.sh`가 uv 0.11.32로 hello-uv를 만들고 `tools/run_nb.py`로 그 커널에서 실제로 실행한 결과예요. Restart는 새 커널을 띄워 재현했어요. 오류는 Traceback 위쪽 줄을 빼고 마지막 줄만 옮겼어요. SyntaxError 괄호 안의 임시 파일 이름과 줄 번호, 하이픈 오류 뒤의 `Maybe you meant '==' instead of '='?`도 뺐어요. demo.sh 환경의 커널은 Python 3.13이었고, 메시지는 3.14와 같아요. VS Code 화면은 이 환경에서 띄울 수 없어서 단순하게 그렸어요. 단축키는 VS Code 기본 설정 기준이에요. Mac 셀 실행이 `control+Enter`인 것은 VS Code 저장소 이슈 #221892, #213675에서 확인했어요.

</details>

---

[← 이전: 09 · uv로 파이썬 시작하기](../09-python-uv) · [커리큘럼](../README.md)
