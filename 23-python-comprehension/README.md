# 23 · 리스트 컴프리헨션

> 21에서 `map`과 `filter`로 리스트 전체를 바꾸고 골랐어요. 한 줄이지만 `list`, `map`, `lambda`를 풀어 가며 읽어야 했어요. 이번에는 같은 일을 대괄호 안에 `for`를 넣어 `[p + 500 for p in prices]`처럼 적어요. 이 모양을 리스트 컴프리헨션이라고 불러요. 같은 모양으로 딕셔너리와 집합도 만들고, 22의 `sorted`, `max`와 함께 써요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/23-python-comprehension/python-comprehension-slides.html) | [22 · 정렬과 sorted, max, min 제대로 쓰기](../22-python-sorting) | [24 · 클래스 1 (붕어빵 틀과 붕어빵)](../24-python-class) |

<!-- /curriculum:top -->

## 학습 목표

이 챕터를 마치면 다음을 할 수 있어요.

- `for`와 `append`로 새 리스트를 만드는 코드를 `[넣을 값 for 이름 in 리스트]`로 옮겨 적어요.
- 같은 일을 `for`, `map`/`filter`, 컴프리헨션 세 가지로 쓰고 비교해요.
- `for` 뒤에 `if`를 붙여 골라 담고, 앞에 한 줄 `if else`를 넣어 값을 바꿔 적어요. 두 자리의 차이를 말해요.
- 튜플 리스트를 `for name, menu_name, qty in orders`처럼 꺼내 담고, `range()`, 문자열에도 써요.
- `{키: 값 for ...}`로 딕셔너리를, `{값 for ...}`로 집합을 만들어요.
- 만든 리스트를 `sum`, `max`, `sorted`에 바로 넘겨요.
- 찍기만 하거나 여러 줄을 하거나 `break`가 필요하면 `for`가 더 낫다는 걸 알아요.

## 시작하기 전에

12~22에서 쓰던 `hello-uv`의 `basics.ipynb`와 그때 배운 내용을 그대로 써요.

| 할 일 | 슬라이드 |
| --- | :---: |
| VS Code에 Python, Jupyter 확장 설치, `uv add --dev ipykernel`, 커널로 `.venv` 고르기 | 09 · 25–27쪽 |
| 리스트, 튜플, `for`, `append`, `join`, f-string | 13 |
| 2차원 리스트 | 14 |
| 딕셔너리 `items()`, 집합 | 15, 16 |
| `if`, 한 줄 `값1 if 조건 else 값2` | 17 |
| `range()` | 18 |
| `lambda`, `map`, `filter`, `sorted`의 `key` | 21, 22 |

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1–3 | 표지, 오늘의 순서, `basics.ipynb` 다시 열기 |
| 1. 왜 필요한가 | 4–6 | 길어지는 `for`와 읽기 어려운 `map`(왜 필요한가), `for`의 세 조각을 대괄호 안에 옮기는 그림(큰 그림), 가장 짧은 컴프리헨션 |
| 2. 만들기와 고르기 | 7–12 | 세 방법 비교, 읽는 순서, 뒤의 `if`로 고르기, 고르고 바꾸기, 앞의 `if else`로 바꾸기, `if` 자리 비교 |
| 3. 여러 데이터에 쓰기 | 13–16 | `len`, 글자, `range`, 튜플 꺼내 담기, 딕셔너리 컴프리헨션, 집합 컴프리헨션 |
| 4. 함수와 함께 쓰기 | 17–19 | `sum`, `max`에 넘기기, `sorted`와 `min`으로 잇기, `for`가 더 나을 때 (겹친 컴프리헨션은 읽기만) |
| 5. 오류와 함정 | 20–23 | 뒤의 `if`에 `else`, 대괄호 안의 `print`, 소괄호로 감싸기, 앞뒤 이름 어긋남 |
| 6. 실습 | 24–26 | 장바구니 영수증, 품절 목록과 주문 가능 메뉴판, 성적표 |
| 정리 | 27–28 | 막힐 때, 한 장 요약 |

## 핵심 개념

### for의 세 조각을 옮겨요

```
up = []                          up = [p + 500          ① 넣을 값
for p in prices:                       for p in prices  ② 하나씩 꺼내기 (콜론은 빼요)
    if p >= 5000:                      if p >= 5000]    ③ 고르기 (필요할 때만)
        up.append(p + 500)
```

읽을 땐 뒤의 `for`부터 읽고, 앞으로 돌아와 무엇을 모으는지 봐요.

### if 자리

| 모양 | 하는 일 | 개수 | `else` |
| --- | --- | --- | --- |
| `[p for p in prices if p >= 5000]` | 고르기 | 줄어요 | 쓰지 않아요 |
| `[p if p >= 5000 else 0 for p in prices]` | 바꾸기 | 그대로 | 꼭 있어야 해요 |

### 괄호 모양

| 모양 | 만드는 것 |
| --- | --- |
| `[값 for ...]` | 리스트 |
| `{키: 값 for ...}` | 딕셔너리 |
| `{값 for ...}` | 집합 |
| `(값 for ...)` | 리스트가 아니에요. `list()`로 감싸야 보여요 |

## 실습

VS Code에서 `hello-uv` 폴더를 열고 `basics.ipynb`를 열어요. 오른쪽 위 커널이 `.venv`인지 본 뒤, 아래 코드를 셀 하나에 한 덩어리씩 적고 `Shift+Enter`로 실행해요. 주석(`#` 뒤)은 실제 출력이에요.

### 1. 세 방법 비교

```python
prices = [4500, 5000, 6500, 3000]
up = []
for p in prices:
    up.append(p + 500)
print(up)
print(list(map(lambda p: p + 500, prices)))
print([p + 500 for p in prices])
# [5000, 5500, 7000, 3500]
# [5000, 5500, 7000, 3500]
# [5000, 5500, 7000, 3500]
```

### 2. 고르기와 바꾸기

```python
print([p for p in prices if p >= 5000])
print([p * 9 // 10 for p in prices if p >= 5000])
print(["비쌈" if p >= 5000 else "보통" for p in prices])
print([p if p >= 5000 else 0 for p in prices])
# [5000, 6500]
# [4500, 5850]
# ['보통', '비쌈', '비쌈', '보통']
# [0, 5000, 6500, 0]
```

### 3. 튜플, 딕셔너리, 집합

```python
orders = [("kim", "latte", 2), ("lee", "cake", 1), ("park", "coffee", 3), ("kim", "tea", 1)]
print([menu_name for name, menu_name, qty in orders if qty >= 2])
menu = {"coffee": 4500, "latte": 5000, "cake": 6500}
print({m: p * 11 // 10 for m, p in menu.items()})
buyers = {o[0] for o in orders}
print(sorted(buyers))
# ['latte', 'coffee']
# {'coffee': 4950, 'latte': 5500, 'cake': 7150}
# ['kim', 'lee', 'park']
```

집합은 순서가 없어서 `sorted()`로 줄 세워 찍었어요.

### 4. 함수와 함께 쓰기

```python
menu = {"coffee": 4500, "latte": 5000, "cake": 6500, "tea": 4000}
cart = ["coffee", "cake", "latte", "latte"]
print(sum([menu[m] for m in cart]))
stock = {"coffee": 3, "latte": 0, "cake": 2, "tea": 5}
ok = [m for m in menu if stock[m] > 0]
print(sorted(ok, key=menu.get))
print(min(ok, key=menu.get))
# 21000
# ['tea', 'coffee', 'cake']
# tea
```

### 5. 실습: 품절 목록과 주문 가능 메뉴판

```python
menu = {"coffee": 4500, "latte": 5000, "cake": 6500, "tea": 4000}
stock = {"coffee": 3, "latte": 0, "cake": 2, "tea": 0}
soldout = [m for m in stock if stock[m] == 0]
print("품절:", ", ".join(soldout))
board = {m: menu[m] * 11 // 10 for m in menu if stock[m] > 0}
print(board)
# 품절: latte, tea
# {'coffee': 4950, 'cake': 7150}
```

### 6. 실습: 성적표

```python
scores = [["kim", 92], ["lee", 78], ["park", 85], ["choi", 59]]
print([name for name, score in scores if score >= 80])
print(["합격" if score >= 60 else "재시험" for name, score in scores])
print(sum([score for name, score in scores]) / len(scores))
print(max(scores, key=lambda s: s[1])[0])
# ['kim', 'park']
# ['합격', '합격', '합격', '재시험']
# 78.5
# kim
```

다 했으면 `Ctrl+S`(Mac `Cmd+S`)로 저장해요.

## 명령어 요약

| 코드 | 하는 일 |
| --- | --- |
| `[x + 10 for x in xs]` | 값마다 바꾼 새 리스트 |
| `[x for x in xs if x > 0]` | 조건에 맞는 값만 고른 새 리스트 |
| `[x if x > 0 else 0 for x in xs]` | 모든 값을 조건에 따라 바꾼 새 리스트 |
| `[n for n, s in pairs]` | 튜플을 꺼내 담아 이름으로 쓰기 |
| `[n * n for n in range(1, 6)]` | `range`로 숫자를 만들며 계산 |
| `{k: v for k, v in d.items()}` | 딕셔너리 컴프리헨션 |
| `{x for x in xs}` | 집합 컴프리헨션 |
| `sum([...])` `max([...])` | 모은 값을 바로 넘기기 |

## 문제 해결

| 증상 | 원인과 해결 |
| --- | --- |
| `SyntaxError: invalid syntax` | 뒤의 `if`에 `else`를 붙였어요. 고르려면 `else`를 빼고, 바꾸려면 `if else`를 `for` 앞으로 옮겨요 |
| `NameError: name 'x' is not defined` | 앞의 값과 뒤의 `for`에서 이름이 달라요. `[p + 10 for p in prices]`처럼 맞춰요 |
| `[None, None]`이 같이 나와요 | 대괄호 안에서 `print`를 했어요. 찍기만 할 때는 `for`를 써요 |
| `<generator object <genexpr> at 0x...>`가 나와요 | 소괄호로 감쌌어요. 리스트가 필요하면 대괄호로 써요 |
| 개수가 줄었어요 | `for` 뒤에 `if`를 붙여 골랐어요. 모든 값을 바꾸려면 `if else`를 앞에 넣어요 |
| 한 줄이 너무 길어요 | 조건이나 할 일이 많아요. `for`나 `def`로 나눠 써요 |
| 집합 순서가 슬라이드와 달라요 | 집합은 순서가 없어요. `sorted()`로 줄 세워 찍어요 |

헷갈리면 같은 일을 `for` 문으로 먼저 써 보고 넣을 값, `for`, `if` 세 조각을 대괄호 안으로 옮겨요.

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분 (gen.py가 만들어요)
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py           모든 장과 deck.json 생성 (노트북 셀, 세 조각 색 구분, 고르기 파이프 그림)
  demo.sh          hello-uv를 새로 만들고 노트북 셀을 실제로 실행해 출력 확인
  run_nb.py        셀을 프로젝트 커널로 실행 (demo.sh가 불러요)
python-comprehension-slides.html  배포용 HTML
python-comprehension-slides.pdf   강사용 PDF
```

검사, HTML, PDF를 만드는 공용 도구(`check.js`, `build_player.js`, `export.js`)는 맨 위 [tools/](../tools)에 한 벌만 있어요. 명령은 이 폴더에서 쳐요.

슬라이드 HTML을 직접 고치지 말고 스크립트를 고친 뒤 다시 만들어요.

```bash
bash tools/demo.sh /tmp/comp-demo > /tmp/comp-demo.log 2>&1
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/build_player.js slides python-comprehension-slides.html
node ../tools/export.js slides python-comprehension-slides.pdf
```

셀 출력은 `tools/demo.sh`가 hello-uv(Python 3.14.6)를 만들고 `tools/run_nb.py`로 그 커널에서 실제로 실행한 결과예요. 파트마다 새 커널에서 위에서부터 차례로 실행해서, 셀 번호가 파트마다 [1]부터 시작해요. 오류는 Traceback 위쪽 줄을 빼고 마지막 줄만 옮겼어요. 22쪽의 `0x` 주소는 다시 실행하면 바뀌니, 출력을 다시 받으면 gen.py의 주소도 같이 바꿔요.

범위: 겹친 컴프리헨션(`for` 두 번)은 19쪽에서 읽기만 보여 줘요. 제너레이터는 22쪽에서 이름만 나오고 다루지 않아요. `reduce`, `zip()`, `*args`, `:=`는 다루지 않아요.

</details>

---

<!-- curriculum:nav -->

[← 이전: 22 · 정렬과 sorted, max, min 제대로 쓰기](../22-python-sorting) · [커리큘럼](../README.md) · [다음: 24 · 클래스 1 (붕어빵 틀과 붕어빵) →](../24-python-class)

<!-- /curriculum:nav -->
