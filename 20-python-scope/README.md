# 20 · 함수 2 (기본값, 지역 변수와 전역 변수)

> 19의 함수를 카페에서 써 보면 두 군데서 막혀요. 거의 늘 같은 값(사이즈 M)을 매번 적어야 하고, 함수 안에서 만든 값이 밖에서 안 보여요. 이번에는 기본값과 키워드 인자로 부르기 편한 함수를 만들고, 함수 안(지역)과 밖(전역)의 변수가 어디까지 보이는지 봐요. 바깥 값을 바꾸는 `global`과 `return`을 비교하고, 리스트와 딕셔너리를 넘겼을 때 원본이 바뀌는 경우를 봐요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/20-python-scope/python-scope-slides.html) | [19 · 함수 1 (정의, 매개변수, return)](../19-python-functions) | [21 · 함수 3 (lambda, map, filter)](../21-python-lambda) |

<!-- /curriculum:top -->

## 학습 목표

이 챕터를 마치면 다음을 할 수 있어요.

- `def order(menu_name, size="M"):`처럼 기본값을 정하고, 부를 때 빼거나 바꿔 넣어요.
- `order("latte", qty=3)`처럼 칸 이름을 붙인 키워드 인자를 쓰고, 위치 인자와 섞어 쓰는 순서를 지켜요.
- `print`의 `sep`, `end`와 `sorted`의 `reverse`가 기본값이 있는 키워드 인자라는 걸 알아요.
- 함수 안에서 만든 변수와 매개변수(지역 변수)는 밖에서 안 보이고, 부를 때마다 새로 생긴다는 걸 알아요.
- 함수 밖에서 만든 변수(전역 변수)를 안에서 읽고, 같은 이름에 값을 넣으면 새 지역 변수가 생긴다는 걸 알아요.
- `UnboundLocalError`가 나는 이유를 말하고, `global`과 `return` 두 방법으로 바깥 값을 바꿔요. `return` 쪽을 권하는 이유를 말해요.
- 리스트와 딕셔너리를 넘겨 안에서 고치면 원본이 바뀌고, 숫자는 그대로라는 걸 알아요. 원본을 지키려면 `copy()`를 써요.

## 시작하기 전에

12~19에서 쓰던 `hello-uv`의 `basics.ipynb`와 그때 배운 내용을 그대로 써요.

| 할 일 | 슬라이드 |
| --- | :---: |
| VS Code에 Python, Jupyter 확장 설치, `uv add --dev ipykernel`, 커널로 `.venv` 고르기 | 09 · 25–27쪽 |
| `print`의 `sep` `end`, `copy()`, `append` | 13 |
| 딕셔너리 `get(키, 기본값)`, `items()` | 15 |
| `sorted(..., reverse=True)` | 16 |
| `if`, `for` | 17, 18 |
| `def`, 매개변수, `return`, `None` | 19 |

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1–3 | 표지, 오늘의 순서, `basics.ipynb` 다시 열기 |
| 1. 왜 필요한가 | 4–6 | 매번 적는 사이즈 M과 사라진 `total`(왜 필요한가), 칸에 미리 채운 값과 함수 안팎 그림(큰 그림), 가장 짧은 기본값 |
| 2. 기본값과 키워드 인자 | 7–10 | 기본값이 여러 개일 때, 칸 이름을 붙여 순서 바꾸기, 기본값과 키워드 인자의 순서 규칙(`SyntaxError`), `print`와 `sorted`에서 본 키워드 인자 |
| 3. 지역 변수 | 11–13 | 함수 안에서 만든 변수는 밖에서 `NameError`, 매개변수도 지역 변수, 부를 때마다 새로 만들어서 쌓이지 않는 도장 |
| 4. 전역 변수 | 14–18 | 밖의 변수를 안에서 읽기, 같은 이름에 넣으면 상자 두 개, `UnboundLocalError`, `global`, `global`과 `return` 비교 |
| 5. 리스트와 딕셔너리 넘기기 | 19–22 | 넘긴 리스트에 `append`하면 원본이 바뀌기, 숫자는 그대로, 재고 딕셔너리 줄이기, `copy()`로 원본 지키기 |
| 6. 실습 | 23–25 | 기본값이 있는 주문 함수, 함수 안에서 함수를 부르는 영수증, `get`과 기본값으로 포인트 적립 |
| 정리 | 26–27 | 막힐 때, 한 장 요약 |

## 핵심 개념

### 기본값과 키워드 인자

| 코드 | size | qty |
| --- | --- | --- |
| `def order(menu_name, size="M", qty=1):` | 기본값 `"M"` | 기본값 `1` |
| `order("latte")` | `"M"` | `1` |
| `order("latte", "L", 2)` | `"L"` | `2` |
| `order("latte", qty=3)` | `"M"` | `3` |
| `order(size="L", menu_name="tea")` | `"L"` | `1` |

- 만들 때: 기본값이 없는 칸을 앞에, 기본값이 있는 칸을 뒤에 둬요.
- 부를 때: 이름 없는 값(위치 인자)을 앞에, 이름 붙인 값(키워드 인자)을 뒤에 적어요.

### 지역 변수와 전역 변수

```
┌ 밖: 노트북 전체 (전역) ──────────────┐
│ shop = "KANT 카페"   count = 0         │
│  ┌ 안: 함수 몸통 (지역) ─────────┐    │
│  │ total = 9000   매개변수도 여기 │    │
│  └────────────────────────────────┘    │
└────────────────────────────────────────┘
```

| | 안에서 | 밖에서 |
| --- | --- | --- |
| 전역 변수 읽기 | 돼요 | 돼요 |
| 지역 변수 읽기 | 돼요 | `NameError` |
| 함수 안에서 `=`로 값 넣기 | 같은 이름이라도 새 지역 변수가 생겨요 | |

함수 안에서 바깥 변수를 읽다가 바꾸면(`count = count + 1`) `UnboundLocalError`가 나요. 바깥 값을 바꿔야 하면 `global count`보다 `count = visit(count)`처럼 인자로 넣고 `return`으로 돌려받는 쪽을 권해요. 값이 바뀌는 줄이 밖에 보여서 찾기 쉬워요.

### 넘긴 값이 바뀌는지

| 함수 안에서 | 밖의 원본 |
| --- | --- |
| `n += 1`, `n = ...` 처럼 새 값 넣기 | 그대로 |
| `cart.append(...)` 처럼 받은 리스트 고치기 | 바뀌어요 |
| `stock[name] -= 1` 처럼 받은 딕셔너리 칸 고치기 | 바뀌어요 |
| `new_cart = cart.copy()` 뒤에 고치기 | 그대로 |

## 실습

VS Code에서 `hello-uv` 폴더를 열고 `basics.ipynb`를 열어요. 오른쪽 위 커널이 `.venv`인지 본 뒤, 아래 코드를 셀 하나에 한 덩어리씩 적고 `Shift+Enter`로 실행해요. 주석(`#` 뒤)은 실제 출력이에요.

### 1. 기본값과 키워드 인자

```python
def order(menu_name, size="M", qty=1):
    print(f"{menu_name} {size} {qty}잔")

order("latte")
order("latte", "L", 2)
order("latte", qty=3)
order(size="L", menu_name="tea")
# latte M 1잔
# latte L 2잔
# latte M 3잔
# tea L 1잔
```

### 2. 지역 변수는 밖에서 안 보여요

```python
def calc():
    total = 4500 * 2
    print("안:", total)

calc()
print("밖:", total)
# 안: 9000
# NameError: name 'total' is not defined
```

### 3. 같은 이름, 다른 상자

```python
price = 4500

def set_price():
    price = 5000
    print("안:", price)

set_price()
print("밖:", price)
# 안: 5000
# 밖: 4500
```

### 4. global과 return

```python
count = 0

def visit():
    count = count + 1

visit()
# UnboundLocalError: cannot access local variable 'count' where it is not associated with a value
```

```python
def visit(count):
    return count + 1

count = 0
count = visit(count)
count = visit(count)
count = visit(count)
print(count)
# 3
```

### 5. 넘긴 리스트와 딕셔너리

```python
def add_item(cart, name):
    cart.append(name)

def sell(stock, name):
    stock[name] -= 1

my_cart = ["coffee"]
add_item(my_cart, "cake")
print(my_cart)
stock = {"coffee": 3, "latte": 1}
sell(stock, "latte")
print(stock)
# ['coffee', 'cake']
# {'coffee': 3, 'latte': 0}
```

### 6. 실습: 주문 함수

```python
def take_order(stock, name, qty=1):
    if stock[name] < qty:
        print(f"{name} {qty}개: 재고가 {stock[name]}개뿐이에요")
        return False
    stock[name] -= qty
    print(f"{name} {qty}개 나갔어요")
    return True

stock = {"coffee": 3, "latte": 1, "cake": 2}
take_order(stock, "coffee", 2)
take_order(stock, "latte")
take_order(stock, "latte")
take_order(stock, "cake", qty=3)
print(stock)
# coffee 2개 나갔어요
# latte 1개 나갔어요
# latte 1개: 재고가 0개뿐이에요
# cake 3개: 재고가 2개뿐이에요
# {'coffee': 1, 'latte': 0, 'cake': 2}
```

다 했으면 `Ctrl+S`(Mac `Cmd+S`)로 저장해요.

## 명령어 요약

| 코드 | 하는 일 |
| --- | --- |
| `def f(a, b="M"):` | `b`에 기본값 정하기. 기본값 칸은 뒤에 |
| `f(1)` `f(1, "L")` | 기본값 칸은 빼면 기본값, 넣으면 넣은 값 |
| `f(1, b="L")` `f(b="L", a=1)` | 키워드 인자. 칸 이름으로 넣고 순서는 자유. 위치 인자 뒤에 |
| `print(..., sep=" / ", end=" ")` | `print`의 키워드 인자 (13) |
| `sorted(xs, reverse=True)` | `sorted`의 키워드 인자 (16) |
| `global x` | 함수 안에서 바깥 `x`를 바꾸기. 되도록 피해요 |
| `x = f(x)` | 인자로 넣고 `return`으로 돌려받아 바꾸기 |
| `cart.copy()` | 넘겨받은 리스트의 원본을 지키며 고치기 |

## 문제 해결

| 증상 | 원인과 해결 |
| --- | --- |
| `SyntaxError: parameter without a default follows parameter with a default` | `def` 줄에서 기본값 칸을 앞에 뒀어요. 기본값 칸을 뒤로 옮겨요 |
| `SyntaxError: positional argument follows keyword argument` | 부를 때 이름 없는 값을 키워드 인자 뒤에 적었어요. 앞으로 옮겨요 |
| `NameError: name 'total' is not defined` | 함수 안의 지역 변수를 밖에서 썼어요. `return`으로 돌려받아요 |
| `UnboundLocalError: cannot access local variable 'count' ...` | 함수 안에서 바깥 변수를 읽다가 바꿨어요. 인자로 받고 `return`해요 |
| 함수 안에서 바꿨는데 밖이 그대로예요 | 안에서 `=`로 새 지역 변수를 만들었어요. `x = f(x)`로 돌려받아요 |
| 함수에 넘긴 리스트가 바뀌었어요 | 받은 리스트를 `append`로 고쳤어요. 원본을 지키려면 `copy()`로 복사해 고쳐요 |
| 부를 때마다 값이 처음으로 돌아가요 | 지역 변수는 부를 때마다 새로 생겨요. 값을 밖에 두고 넘겨요 |

`SyntaxError` 메시지 끝에는 셀마다 다른 파일 이름과 줄 번호가 괄호로 붙어요. 슬라이드에서는 그 부분을 빼고 옮겼어요.

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분 (gen.py가 만들어요)
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py           모든 장과 deck.json 생성 (노트북 셀, 안팎 상자 그림, 변수 상자, 리스트를 가리키는 화살표)
  demo.sh          hello-uv를 새로 만들고 노트북 셀을 실제로 실행해 출력 확인
  run_nb.py        셀을 프로젝트 커널로 실행 (demo.sh가 불러요)
python-scope-slides.html  배포용 HTML
python-scope-slides.pdf   강사용 PDF
```

검사, HTML, PDF를 만드는 공용 도구(`check.js`, `build_player.js`, `export.js`)는 맨 위 [tools/](../tools)에 한 벌만 있어요. 명령은 이 폴더에서 쳐요.

슬라이드 HTML을 직접 고치지 말고 스크립트를 고친 뒤 다시 만들어요.

```bash
bash tools/demo.sh /tmp/scope-demo > /tmp/scope-demo.log 2>&1
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/build_player.js slides python-scope-slides.html
node ../tools/export.js slides python-scope-slides.pdf
```

셀 출력은 `tools/demo.sh`가 hello-uv(Python 3.14.6)를 만들고 `tools/run_nb.py`로 그 커널에서 실제로 실행한 결과예요. 파트마다 새 커널에서 위에서부터 차례로 실행해서, 셀 번호가 파트마다 [1]부터 시작해요. 오류는 Traceback 위쪽 줄을 빼고 마지막 줄만 옮겼어요. 18쪽 왼쪽 셀은 17쪽의 [4]를 다시 보여 준 거예요.

범위: `global`은 있다는 것과 쓰는 법만 보여 주고 `return` 쪽을 권해요. `nonlocal`(함수 안의 함수가 필요해요), `*args`, `**kwargs`, `lambda`, 재귀, 데코레이터, 타입 힌트, docstring, 기본값에 리스트를 넣을 때의 함정은 다루지 않아요.

</details>

---

<!-- curriculum:nav -->

[← 이전: 19 · 함수 1 (정의, 매개변수, return)](../19-python-functions) · [커리큘럼](../README.md) · [다음: 21 · 함수 3 (lambda, map, filter) →](../21-python-lambda)

<!-- /curriculum:nav -->
