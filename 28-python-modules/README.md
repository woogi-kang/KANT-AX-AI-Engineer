# 28 · 미니 프로젝트: 장바구니 (들여쓰기, items, 모듈)

> 수업에서 만든 장바구니 프로젝트(`product.py`, `cart.py`, `main.py`)를 다시 읽으면서 자주 막히는 세 가지를 풀어요. 들여쓰기가 어느 상자 소속인지 정하는 규칙, `for p, q in self.items.items()`에 무엇이 담기는지, 파일을 나누고 `import`하는 이유예요. 13의 꺼내 담기, 15의 `items()`, 17의 들여쓰기, 24~26의 클래스를 그대로 이어서 써요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/28-python-modules/python-modules-slides.html) | [27 · 클래스 4 (캡슐화)](../27-python-encapsulation) | [30 · Docker 2 (내 프로그램을 이미지로 만들기)](../30-docker-image) |

<!-- /curriculum:top -->

## 학습 목표

이 챕터를 마치면 다음을 할 수 있어요.

- 줄의 칸 수를 보고 그 줄이 `class`, `def`, `if`, `for` 중 어느 상자 안에 있는지 말해요.
- VS Code에서 `Tab`과 `Shift+Tab`으로 여러 줄의 칸을 한꺼번에 맞춰요.
- `a, b = (1, 2)`에서 출발해 `for p, q in cart.items.items():`에 무엇이 담기는지 설명해요.
- `cart.items`(Cart 안의 칸)와 `.items()`(딕셔너리 메서드)를 구별해요.
- 파일을 나누는 이유 세 가지(찾기, 같이 쓰기, 나눠 일하기)를 말해요.
- `import 모듈`, `from 모듈 import 이름`, `from 모듈 import 이름1, 이름2`, `import 모듈 as 별명`을 골라 써요.
- 테스트 코드를 `if __name__ == "__main__":` 안에 넣어서 import할 때 실행되지 않게 해요.

## 시작하기 전에

| 할 일 | 챕터 |
| --- | :---: |
| `a, b, c = 튜플`로 꺼내 담기 | 13 |
| 딕셔너리 `items()`, `for k, v in d.items():`, `get()` | 15 |
| `if`와 4칸 들여쓰기, 한 줄 `if else` | 17 |
| `def`, `return` | 19 |
| `class`, `__init__`, 메서드, `__str__` | 24, 25 |
| 클래스 변수 | 26 |

수업에서 만든 `shopping-cart` 폴더를 VS Code로 열고 터미널에서 따라 쳐요. 코드는 수업 레포 [IndieGameMaker/kant_shopping_cart](https://github.com/IndieGameMaker/kant_shopping_cart)와 같아요.

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1–3 | 표지, 오늘의 순서, `shopping-cart` 폴더 준비 |
| 1. 왜 필요한가 | 4–5 | `cart.py`에서 자주 막히는 세 곳, 세 가지가 프로젝트 어디에 있는지 |
| 2. 들여쓰기는 상자 | 6–11 | 상자 안의 상자, `print(line)`이 `for` 안과 밖일 때, `if` 밖으로 나온 `return`, 한 줄 `if`, `IndentationError` 두 가지, `Tab`과 `Shift+Tab` |
| 3. `for p, q in items()` | 12–18 | `a, b = (1, 2)`, `items()`가 주는 튜플 쌍, `for`로 한 쌍씩, `pair[0]` 긴 방법, `cart.items.items()`, 합계 세 가지, `.items()`를 빠뜨린 오류 |
| 4. 모듈과 `import` | 19–27 | 파일을 나누는 이유, 파일 하나가 모듈 하나, `import`, `from`, 여러 개 꺼내기, `as`, 다섯 가지 비교표, `ModuleNotFoundError`, `ImportError`, `NameError` |
| 5. `if __name__ == "__main__"` | 28–30 | import했더니 섞여 나오는 테스트 출력, `__name__` 값, 고치기 |
| 6. 실습 | 31–32 | `main.py`에서 주문하기, `coupon.py` 모듈 더하기 |
| 정리 | 33–34 | 막힐 때, 한 장 요약 |

## 핵심 개념

### 들여쓰기는 상자

콜론(`:`)으로 끝난 줄 다음은 4칸 더 들어가서 그 상자 안이 돼요. 같은 칸에서 시작하는 줄은 같은 상자이고, 왼쪽으로 나오면 그 상자가 끝나요.

```python
class Cart:                                  # 0칸
    def add(self, product, qty):             # 4칸: Cart 상자 안
        if product.is_sold_out():            # 8칸: add 상자 안
            print("품절된 상품입니다.")         # 12칸: if 상자 안
            return                           # 12칸: 품절일 때만 멈춰요
```

`return`을 8칸으로 꺼내면 `if` 밖이라 언제나 실행돼서, 아무것도 담기지 않아요.

### `for p, q in 딕셔너리.items()`

| 코드 | 담기는 것 |
| --- | --- |
| `a, b = (1, 2)` | `a`에 1, `b`에 2 |
| `cart_items.items()` | `("텀블러", 1)`, `("무선 이어폰", 2)` 같은 튜플 쌍 |
| `for name, qty in cart_items.items():` | 바퀴마다 한 쌍을 `name`, `qty`에 나눠 담아요 |
| `for p, q in self.items.items():` | `p`에 `Product` 객체, `q`에 수량 |

앞의 `self.items`는 `__init__`에서 만든 칸 이름이고, 뒤의 `.items()`는 딕셔너리 메서드예요.

### import 모양

| 모양 | 쓰는 법 | 고르는 때 |
| --- | --- | --- |
| `import product` | `product.Product(...)` | 어느 모듈 것인지 보이게 |
| `from product import Product` | `Product(...)` | 하나를 여러 번 쓸 때 |
| `from coupon import COUPONS, discount` | `discount("VIP")` | 몇 개만 골라 쓸 때 |
| `import coupon as cp` | `cp.discount("VIP")` | 모듈 이름이 길 때 |
| `from coupon import *` | 쓰지 않아요 | 무엇이 왔는지 안 보여요 |

모듈 이름은 파일 이름에서 `.py`를 뺀 부분이에요. 파일 이름은 영문 소문자와 밑줄로 지어요(`shop_cart.py`).

## 실습

### 1. 지금 코드 실행하기

```bash
uv run cart.py
```

`cart.py` 맨 아래의 테스트 코드가 실행돼서 장바구니가 세 번 찍혀요.

### 2. `items()`로 한 쌍씩 꺼내기

`play.py`를 새로 만들어요.

```python
cart_items = {"텀블러": 1, "무선 이어폰": 2}

for name, qty in cart_items.items():
    print(name, qty)
```

```bash
uv run play.py
```

```
텀블러 1
무선 이어폰 2
```

`for name, qty in cart_items:`처럼 `.items()`를 빼면 `ValueError: too many values to unpack (expected 2)`가 나요.

### 3. import하면 테스트 코드가 같이 실행돼요

`main.py`를 이렇게 바꿔요.

```python
from cart import Cart

print("main.py 시작")
cart = Cart()
```

```bash
uv run main.py
```

`cart.py`의 테스트 출력이 먼저 줄줄이 나오고, `main.py 시작`은 맨 끝에 나와요.

### 4. 테스트 코드를 `if __name__ == "__main__":` 안에 넣기

`cart.py` 맨 아래 테스트 코드를 이렇게 바꿔요.

```python
# 테스트 코드
if __name__ == "__main__":
    tumbler = Product("텀블러", 15_000, 10)
    earphone = Product("무선 이어폰", 89_000, 3)

    cart = Cart()
    cart.add(tumbler, 1)
    cart.add(earphone, 2)
    cart.show()
```

```bash
uv run main.py
```

```
main.py 시작
```

`uv run cart.py`로 직접 실행하면 테스트는 그대로 돌아요.

### 5. 쿠폰 모듈 더하기

`coupon.py`를 새로 만들어요.

```python
COUPONS = {"WELCOME": 3_000, "VIP": 5_000}


def discount(code):
    return COUPONS.get(code, 0)
```

`main.py`를 이렇게 바꿔요.

```python
from product import Product
from cart import Cart
from coupon import COUPONS, discount

for code, amount in COUPONS.items():
    print(f"{code:<8} {amount:>6,}원 할인")

tumbler = Product("텀블러", 15_000, 10)
cart = Cart()
cart.add(tumbler, 3)

pay = cart.total() - discount("VIP")
print(f"결제할 금액: {pay:,}원")
```

```bash
uv run main.py
```

```
WELCOME   3,000원 할인
VIP       5,000원 할인
텀블러 3개를 담았습니다.
결제할 금액: 40,000원
```

쿠폰을 하나 더 넣고 `discount`에 그 코드를 넘겨 보세요.

## 명령어 요약

| 코드 | 하는 일 |
| --- | --- |
| `Tab` / `Shift+Tab` | 고른 줄을 4칸 안으로, 밖으로 (VS Code) |
| `a, b = (1, 2)` | 튜플을 두 칸에 나눠 담기 |
| `for p, q in d.items():` | 키와 값을 한 쌍씩 꺼내기 |
| `import product` | 모듈을 통째로 불러와서 `product.Product`로 쓰기 |
| `from product import Product` | 이름 하나를 꺼내 와서 `Product`로 바로 쓰기 |
| `from coupon import COUPONS, discount` | 쉼표로 여러 개 꺼내기 |
| `import coupon as cp` | 모듈에 별명 붙이기 |
| `if __name__ == "__main__":` | 직접 실행할 때만 아래 코드 실행 |
| `uv run 파일.py` | 프로젝트 폴더에서 파일 실행 |

## 문제 해결

| 메시지 | 원인 | 해결 |
| --- | --- | --- |
| `IndentationError: expected an indented block after function definition on line 42` | 콜론 다음 줄이 안으로 안 들어갔어요 | 그 줄 앞에 4칸 더 넣어요 |
| `IndentationError: unindent does not match any outer indentation level` | 위 줄들과 칸 수가 안 맞아요 | `Tab`, `Shift+Tab`으로 위 줄과 같은 칸에 맞춰요 |
| 오류는 없는데 줄(`-----`)이 상품마다 찍혀요 | `print(line)`이 `for` 상자 안에 들어갔어요 | `for`와 같은 칸으로 꺼내요 |
| `TypeError: cannot unpack non-iterable Product object` | 딕셔너리를 `.items()` 없이 돌아서 키 하나만 나왔어요 | `for p, q in cart.items.items():` |
| `ValueError: too many values to unpack (expected 2)` | 글자 키를 `.items()` 없이 돌아서 글자로 쪼개졌어요 | `.items()`를 붙여요 |
| `ModuleNotFoundError: No module named 'prodcut'` | 파일 이름 오타, 또는 다른 폴더에서 실행했어요 | 파일 이름을 확인하고 프로젝트 폴더에서 `uv run`해요 |
| `ImportError: cannot import name 'product' from 'product'` | 모듈 안에 그 이름이 없어요. 대소문자가 달라요 | `Did you mean`에 나온 이름(`Product`)으로 고쳐요 |
| `NameError: name 'Product' is not defined. Did you mean: 'product'?` | `import product`만 하고 `Product`라고 썼어요 | `product.Product(...)`로 쓰거나 `from product import Product`로 바꿔요 |
| import했더니 테스트 출력이 먼저 나와요 | 테스트 코드가 `if __name__ == "__main__":` 밖에 있어요 | 테스트 코드를 그 안에 4칸 들여 넣어요 |

오류에 적힌 경로(`/home/kim/shopping-cart`)는 실습 폴더라서 내 화면에서는 다르게 보여요.

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분 (gen.py가 만들어요)
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  src/             수업 레포의 product.py, cart.py (수업 때 쓴 그대로)
  scenes.py        장마다 보여 줄 파일과 명령 (gen.py와 demo.sh가 같이 읽어요)
  run_scenes.py    장마다 새 프로젝트를 복사해 파일을 쓰고 명령을 실행 (demo.sh가 불러요)
  demo.sh          uv 프로젝트를 만들고 모든 장면을 실제로 실행해서 tools/out.json에 저장
  out.json         실제 실행 출력
  gen.py           모든 장과 deck.json 생성 (에디터, 터미널, 들여쓰기 상자 그림)
python-modules-slides.html  배포용 HTML
python-modules-slides.pdf   강사용 PDF
```

검사, HTML, PDF를 만드는 공용 도구는 맨 위 [tools/](../tools)에 한 벌만 있어요. 명령은 이 폴더에서 쳐요.

```bash
bash tools/demo.sh
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/build_player.js slides python-modules-slides.html
node ../tools/export.js slides python-modules-slides.pdf
```

출력은 `tools/demo.sh`가 `/home/kim/shopping-cart`에 uv 프로젝트(Python 3.14.6)를 만들고 `tools/scenes.py`의 장면마다 실제로 실행한 결과예요. 슬라이드의 코드와 실행한 코드는 `scenes.py` 한 곳에서 나와서 서로 어긋나지 않아요. 2파트부터는 테스트 코드를 `if __name__ == "__main__":` 안에 넣은 `cart.py`를 써요. 5파트에서 그 이유를 보여 줘요.

장마다 강조는 `tools/HIGHLIGHT.md`에서 골랐어요. 표지는 제목이 크게 들어오고 코드 칸에 빛이 지나가요. 4쪽은 질문 세 개를 펜 상자로 두르고 지난 질문이 흐려져요. 6쪽은 들여쓰기 상자가 바깥부터 차례로 켜져요. 8쪽은 실행 막대가 줄을 따라 내려가요. 9, 15쪽은 코드가 그 자리에서 바뀌어요(코드 모핑). 11쪽은 키캡이 눌려요. 12, 22쪽은 값이 제자리로 날아와요. 14쪽은 바퀴마다 name, qty 값이 바뀌어요. 16, 23, 24, 32쪽은 코드와 그림을 같은 색으로 짝지어요. 17, 31쪽은 코드 줄과 출력 줄을 같은 색 띠로 짝지어요. 19, 20쪽 화살표는 왼쪽부터 그려져요. 25쪽 표는 한 줄씩 스포트라이트로 비춰요. 28쪽 터미널은 한 번 흔들리고 아래로 밀려 올라가요. 29쪽은 터미널 하나를 확대해요.

범위: 들여쓰기 상자 읽기, `Tab`과 `Shift+Tab`, `items()`와 꺼내 담기, 모듈과 `import`, `from ... import`, 쉼표로 여러 개, `as`, `if __name__ == "__main__":`을 다뤄요. 패키지(폴더와 `__init__.py`), 상대 import, `sys.path`, 제너레이터 문법은 다루지 않아요. 수업 코드의 `sum(p.price * q for p, q in ...)`은 대괄호를 넣은 리스트 컴프리헨션과 결과가 같다고만 보여 줘요.

</details>

---

<!-- curriculum:nav -->

[← 이전: 27 · 클래스 4 (캡슐화)](../27-python-encapsulation) · [커리큘럼](../README.md) · [다음: 30 · Docker 2 (내 프로그램을 이미지로 만들기) →](../30-docker-image)

<!-- /curriculum:nav -->
