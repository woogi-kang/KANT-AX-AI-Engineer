# 19 · 함수 1 (정의, 매개변수, return)

> 손님마다 복사하던 장바구니 합계 계산을 함수 하나로 묶어요. `def`로 함수를 만들고, 괄호 안 칸(매개변수)으로 값을 받고, `return`으로 결과를 돌려받아요. 가장 많이 헷갈리는 `print`와 `return`의 차이를 나란히 보고, 15~17에서 만든 카페 코드를 함수로 바꿔요. 기본값과 지역 변수, 전역 변수는 20에서 이어서 배워요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/19-python-functions/python-functions-slides.html) | [18 · 제어문 2 (반복 제어 while, break)](../18-python-while) | [20 · 함수 2 (기본값, 지역 변수와 전역 변수)](../20-python-scope) |

<!-- /curriculum:top -->

## 학습 목표

이 챕터를 마치면 다음을 할 수 있어요.

- 같은 줄을 여러 번 복사하면 왜 불편한지 말하고, 함수가 재료를 받아 결과를 내놓는 상자라는 걸 알아요.
- `def 이름():`으로 함수를 만들고(정의), `이름()`으로 불러요(호출). 정의만 하면 실행되지 않는다는 걸 알아요.
- 괄호 안에 매개변수를 하나나 여러 개 만들고, 부를 때 인자를 순서대로 넣어요.
- `return`으로 값을 돌려받아 변수에 담거나 계산에 써요. `print`와 `return`의 차이를 설명해요.
- `return`이 없으면 `None`이 돌아오고, `return`을 만나면 함수가 바로 끝난다는 걸 알아요.
- `return a, b`로 값 두 개를 돌려주고 `x, y = 함수()`로 나눠 받아요.
- 괄호 빼기, 인자 수 `TypeError`, `return` 아래 줄, `None` 계산, 정의 전 호출 `NameError`를 고쳐요.

## 시작하기 전에

12~18에서 쓰던 `hello-uv`의 `basics.ipynb`와 그때 배운 내용을 그대로 써요.

| 할 일 | 슬라이드 |
| --- | :---: |
| VS Code에 Python, Jupyter 확장 설치, `uv add --dev ipykernel`, 커널로 `.venv` 고르기 | 09 · 25–27쪽 |
| 변수 이름 규칙, Restart | 10 |
| f-string과 천 단위 콤마, 리스트, `for`, `len` `sum` `sorted`, 튜플 꺼내 담기 | 13 |
| 딕셔너리 `menu["latte"]`, `None` | 15 |
| `if`, `elif`, `else` | 17 |

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1–3 | 표지, 오늘의 순서, `basics.ipynb` 다시 열기 |
| 1. 왜 필요한가 | 4–6 | 손님마다 복사한 합계 계산(왜 필요한가), `len` `sorted` `sum`을 재료와 결과 상자로 보기(큰 그림), 가장 짧은 `def hello():` |
| 2. 정의와 호출 | 7–9 | `def` 줄 다섯 조각, 정의만 하면 아무것도 안 찍히기, 부르면 몸통으로 갔다가 제자리로 돌아오기 |
| 3. 매개변수와 인자 | 10–12 | 재료 칸 하나 `greet(name)`, 여러 개 `order(menu_name, qty)`, 순서를 바꾸면 값도 바뀌어 들어가기 |
| 4. return | 13–17 | 부른 자리로 값 돌려주기, `print`와 `return` 나란히, `return`이 없으면 `None`, `return`을 만나면 바로 끝, `return a, b` |
| 5. 오류와 함정 | 18–22 | 괄호 빼기, 인자 수가 다른 `TypeError`, `return` 아래 줄, 찍기만 하는 함수로 계산하기, 정의 전에 부르는 `NameError` |
| 6. 실습 | 23–26 | 장바구니 총액, 주문할 수 있는지 True와 False로 돌려주기, 17의 성적 등급, 17의 할인 결제를 함수 두 개로 |
| 정리 | 27–28 | 막힐 때, 한 장 요약 |

## 핵심 개념

### 함수는 재료를 넣으면 결과가 나오는 상자

```
재료 ──▶ [ 함수 ] ──▶ 결과
["coffee", "cake"] ──▶ [ len ] ──▶ 2
2 ──▶ [ price_of ] ──▶ 9000
```

13에서 쓴 `len`, `sum`, `sorted`도 함수예요. 이번에는 이런 상자를 `def`로 직접 만들어요.

### 정의와 호출

| | 모양 | 하는 일 |
| --- | --- | --- |
| 정의 | `def hello():` 다음 줄 4칸 들여쓰기 | 이름에 몸통을 기억해 두기만 해요 |
| 호출 | `hello()` | 몸통을 처음부터 끝까지 실행하고 제자리로 돌아와요 |

### 매개변수와 인자

| 말 | 어디에 | 예 |
| --- | --- | --- |
| 매개변수 | `def` 줄 괄호 안의 칸 이름 | `def order(menu_name, qty):`의 `menu_name`, `qty` |
| 인자 | 부를 때 괄호에 넣는 값 | `order("latte", 2)`의 `"latte"`, `2` |

인자는 적은 순서대로 칸에 들어가요. 순서를 바꾸면 오류 없이 값이 바뀌어 들어가요.

### print와 return

| | `print` | `return` |
| --- | --- | --- |
| 하는 일 | 화면에 찍어요 | 부른 자리로 값을 돌려줘요 |
| `a = 함수()`에 담기는 값 | `None` | 돌려준 값 |
| 다음 계산에 쓰기 | 안 돼요 | 돼요 |

`return`을 만나면 함수가 바로 끝나요. 몸통 끝까지 `return`이 없으면 `None`이 돌아와요.

## 실습

VS Code에서 `hello-uv` 폴더를 열고 `basics.ipynb`를 열어요. 오른쪽 위 커널이 `.venv`인지 본 뒤, 아래 코드를 셀 하나에 한 덩어리씩 적고 `Shift+Enter`로 실행해요. 주석(`#` 뒤)은 실제 출력이에요.

### 1. 만들고 부르기

```python
def hello():
    print("어서 오세요")

hello()
hello()
# 어서 오세요
# 어서 오세요
```

### 2. 매개변수와 인자

```python
def order(menu_name, qty):
    print(f"{menu_name} {qty}잔 주문 받았어요")

order("latte", 2)
order(2, "latte")
# latte 2잔 주문 받았어요
# 2 latte잔 주문 받았어요
```

### 3. print와 return

```python
def show(qty):
    print(4500 * qty)

def calc(qty):
    return 4500 * qty

a = show(2)
b = calc(2)
print("a:", a)
print("b:", b)
print(b + 1000)
# 9000
# a: None
# b: 9000
# 10000
```

### 4. return을 만나면 끝나요

```python
def check(stock):
    if stock == 0:
        return "품절"
    return "주문 가능"

print(check(0))
print(check(3))
# 품절
# 주문 가능
```

### 5. 실습: 장바구니 총액

```python
menu = {"coffee": 4500, "latte": 5000, "cake": 6500}

def calc_total(cart, menu):
    total = 0
    for m in cart:
        total += menu[m]
    return total

cart1 = ["coffee", "cake"]
cart2 = ["latte", "latte", "cake"]
print(f"합계 {calc_total(cart1, menu):,}원")
print(f"합계 {calc_total(cart2, menu):,}원")
# 합계 11,000원
# 합계 16,500원
```

### 6. 실습: 할인 결제

```python
def discount_rate(total):
    if total >= 20000:
        return 10
    elif total >= 10000:
        return 5
    return 0

def pay(total):
    rate = discount_rate(total)
    sale = total * rate // 100
    return total - sale

print(pay(8000))
print(pay(15500))
print(pay(22000))
# 8000
# 14725
# 19800
```

다 했으면 `Ctrl+S`(Mac `Cmd+S`)로 저장해요.

## 명령어 요약

| 코드 | 하는 일 |
| --- | --- |
| `def 이름():` | 함수 만들기(정의). 다음 줄부터 4칸 들여써서 몸통을 적어요 |
| `이름()` | 함수 실행하기(호출) |
| `def 이름(a, b):` | 매개변수 칸 두 개 |
| `이름(1, 2)` | 인자를 순서대로 넣기 |
| `return 값` | 값을 돌려주고 함수 끝내기 |
| `None` | `return`이 없을 때 돌아오는 값 |
| `return a, b` | 값 두 개를 튜플로 돌려주기 |
| `x, y = 이름()` | 돌려받은 값을 나눠 담기 |

## 문제 해결

| 증상 | 원인과 해결 |
| --- | --- |
| `<function hello at 0x...>`가 나와요 | 괄호를 빼서 실행하지 않았어요. `hello()`처럼 괄호를 붙여요. `0x` 뒤 숫자는 실행할 때마다 달라요 |
| `TypeError: order() missing 1 required positional argument: 'qty'` | 인자를 덜 넣었어요. `def` 줄의 칸 수만큼 넣어요 |
| `TypeError: order() takes 2 positional arguments but 3 were given` | 인자를 더 넣었어요 |
| `NameError: name 'welcome' is not defined` | `def` 셀보다 먼저 불렀어요. `def` 셀을 먼저 실행해요 |
| 돌려받은 값이 `None`이에요 | 함수에 `return`이 없어요. `print` 대신 `return`을 써요 |
| `TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'` | `None`으로 계산했어요. 함수에 `return`을 넣어요 |
| `return` 아래 `print`가 안 찍혀요 | `return`에서 함수가 끝났어요. `print`를 `return` 위로 옮겨요 |
| 순서가 이상하게 찍혀요 | 인자 순서가 `def` 줄과 달라요 |

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분 (gen.py가 만들어요)
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py           모든 장과 deck.json 생성 (노트북 셀, 실행한 줄 표시, 함수 상자, 실행 순서 표)
  demo.sh          hello-uv를 새로 만들고 노트북 셀을 실제로 실행해 출력 확인
  run_nb.py        셀을 프로젝트 커널로 실행 (demo.sh가 불러요)
python-functions-slides.html  배포용 HTML
python-functions-slides.pdf   강사용 PDF
```

검사, HTML, PDF를 만드는 공용 도구(`check.js`, `build_player.js`, `export.js`)는 맨 위 [tools/](../tools)에 한 벌만 있어요. 명령은 이 폴더에서 쳐요.

슬라이드 HTML을 직접 고치지 말고 스크립트를 고친 뒤 다시 만들어요.

```bash
bash tools/demo.sh /tmp/func-demo > /tmp/func-demo.log 2>&1
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/build_player.js slides python-functions-slides.html
node ../tools/export.js slides python-functions-slides.pdf
```

셀 출력은 `tools/demo.sh`가 hello-uv(Python 3.14.6)를 만들고 `tools/run_nb.py`로 그 커널에서 실제로 실행한 결과예요. 파트마다 새 커널에서 위에서부터 차례로 실행해서, 셀 번호가 파트마다 [1]부터 시작해요. 오류는 Traceback 위쪽 줄을 빼고 마지막 줄만 옮겼어요. 22쪽의 `NameError` 두 셀은 따로 띄운 새 커널에서 실행했어요.

18쪽 `print(hello)`의 `0x` 뒤 숫자는 함수가 저장된 메모리 위치라서 실행할 때마다 달라요. 수강생 화면과 달라도 괜찮다고 알려 줘요.

범위: 기본값, 키워드 인자, 지역 변수와 전역 변수, `global`, 리스트를 넘겼을 때 원본이 바뀌는 일은 20에서 다뤄요. `*args`, `**kwargs`, `lambda`, 재귀, 데코레이터, 타입 힌트, docstring은 다루지 않아요. 6파트에서 `calc_total(cart, menu)`의 `menu` 칸은 바깥 `menu`와 이름이 같지만, 같은 이름이어도 괜찮은 이유는 20에서 설명해요.

</details>

---

<!-- curriculum:nav -->

[← 이전: 18 · 제어문 2 (반복 제어 while, break)](../18-python-while) · [커리큘럼](../README.md) · [다음: 20 · 함수 2 (기본값, 지역 변수와 전역 변수) →](../20-python-scope)

<!-- /curriculum:nav -->
