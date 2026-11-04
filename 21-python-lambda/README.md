# 21 · 함수 3 (lambda, map, filter)

> 리스트의 모든 가격을 바꾸거나 일부만 고를 때마다 빈 리스트, `for`, `append`를 다시 적었어요. 이번에는 함수도 값이라서 변수에 담고 다른 함수에 넘길 수 있다는 걸 봐요. 한 줄짜리 함수 `lambda`를 만들고, 리스트 전체에 함수를 쓰는 `map`과 골라내는 `filter`에 넘겨요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/21-python-lambda/python-lambda-slides.html) | [20 · 함수 2 (기본값, 지역 변수와 전역 변수)](../20-python-scope) | [22 · 정렬과 sorted, max, min 제대로 쓰기](../22-python-sorting) |

<!-- /curriculum:top -->

## 학습 목표

이 챕터를 마치면 다음을 할 수 있어요.

- 함수를 괄호 없이 이름만 적어 변수에 담고, 다른 함수의 인자로 넘겨요.
- `lambda x: x + 10`처럼 한 줄 함수를 만들고, `def`와 무엇이 같고 다른지 말해요.
- `list(map(함수, 리스트))`로 값마다 함수를 쓴 새 리스트를 만들어요. `map(str, xs)`, `map(len, xs)`처럼 이미 있는 함수도 넘겨요.
- `list(filter(함수, 리스트))`로 함수가 `True`를 돌려준 값만 남겨요. 딕셔너리를 넘기면 키가 하나씩 들어간다는 걸 알아요.
- `map` 결과에 번호와 `len`을 못 쓰고, 한 번 꺼내면 비어서 `list()`로 담아 둬야 한다는 걸 알아요.
- `lambda`가 길어지면 `def`로 만들어 넘겨요.

## 시작하기 전에

12~20에서 쓰던 `hello-uv`의 `basics.ipynb`와 그때 배운 내용을 그대로 써요.

| 할 일 | 슬라이드 |
| --- | :---: |
| VS Code에 Python, Jupyter 확장 설치, `uv add --dev ipykernel`, 커널로 `.venv` 고르기 | 09 · 25–27쪽 |
| 리스트, 튜플, `for`, `append`, `join`, f-string | 13 |
| 딕셔너리 | 15 |
| `if`, 한 줄 `값1 if 조건 else 값2` | 17 |
| `def`, 매개변수, `return` | 19, 20 |

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1–3 | 표지, 오늘의 순서, `basics.ipynb` 다시 열기 |
| 1. 왜 필요한가 | 4–6 | 가격을 바꿀 때마다 다시 적는 `for` 네 줄(왜 필요한가), `map`과 `filter` 그림(큰 그림), 가장 짧은 `map` |
| 2. 함수를 값처럼, lambda | 7–11 | 함수를 변수에 담기, 다른 함수에 넘기기, `def`와 `lambda` 비교, 바로 넘기기, 매개변수 여러 개와 한 줄 if else |
| 3. map | 12–15 | `for` 네 줄이 `map` 한 줄로, 값을 하나씩 넣는 그림, `<map object>`, `str` `int` `len` 넘기기 |
| 4. filter | 16–19 | `for`와 `if`로 골라 담기를 한 줄로, `True`만 남는 그림, 딕셔너리 키 고르기, 고른 다음 `map`으로 바꾸기 |
| 5. 오류와 함정 | 20–24 | 번호와 `len`을 못 쓰는 `map`, 한 번 꺼내면 비는 `map`, 넘길 함수에 괄호, `lambda` 안의 `return`, 긴 `lambda` |
| 6. 실습 | 25–27 | 10% 올린 가격표, 품절이 아니고 싼 메뉴, 튜플 주문 기록 |
| 정리 | 28–29 | 막힐 때, 한 장 요약 |

## 핵심 개념

### def와 lambda

| | `def` | `lambda` |
| --- | --- | --- |
| 모양 | `def add10(x):` 다음 줄에 `return x + 10` | `lambda x: x + 10` |
| 이름 | 있어요 | 없어요. 필요하면 변수에 담아요 |
| 길이 | 여러 줄, `if` `elif` 가능 | 값 하나를 계산하는 한 줄. `return`은 안 적어요 |
| 언제 | 여러 번 쓰거나 길 때 | 다른 함수에 바로 넘길 때 |

### map과 filter

```
map(lambda p: p + 500, prices)      filter(lambda p: p >= 5000, prices)

4500  5000  6500                     4500   5000   6500
  ↓     ↓     ↓    p + 500             ↓      ↓      ↓    p >= 5000
5000  5500  7000                    False  True   True
                                            5000   6500  (True인 원래 값)
```

- `map`은 함수가 돌려준 값을 모아요. 개수가 그대로예요.
- `filter`는 함수가 `True`를 돌려준 원래 값만 모아요. 개수가 줄 수 있어요.
- 둘 다 결과가 리스트가 아니에요. 찍거나 번호로 꺼내려면 `list()`로 감싸요.
- 함수를 넘길 땐 `map(add10, xs)`처럼 괄호 없이 이름만 적어요.

## 실습

VS Code에서 `hello-uv` 폴더를 열고 `basics.ipynb`를 열어요. 오른쪽 위 커널이 `.venv`인지 본 뒤, 아래 코드를 셀 하나에 한 덩어리씩 적고 `Shift+Enter`로 실행해요. 주석(`#` 뒤)은 실제 출력이에요. `0x`로 시작하는 숫자는 실행할 때마다 달라요.

### 1. 함수를 담고 넘기기

```python
def add10(x):
    return x + 10

plus = add10
print(plus(5))
print(add10)
# 15
# <function add10 at 0x7fdb817ce4b0>
```

```python
def double(x):
    return x * 2

def apply(f, x):
    return f(x)

print(apply(add10, 5))
print(apply(double, 5))
print(apply(lambda x: x * 3, 5))
# 15
# 10
# 15
```

### 2. lambda

```python
price_of = lambda price, qty: price * qty
print(price_of(4500, 2))
label = lambda p: "비쌈" if p >= 5000 else "보통"
print(label(6500), label(4500))
# 9000
# 비쌈 보통
```

### 3. map

```python
prices = [4500, 5000, 6500]
print(list(map(lambda p: p + 500, prices)))
print(prices)
m = map(lambda p: p + 500, prices)
print(m)
print(list(map(str, prices)))
print(", ".join(map(str, prices)))
# [5000, 5500, 7000]
# [4500, 5000, 6500]
# <map object at 0x7fe9b3214840>
# ['4500', '5000', '6500']
# 4500, 5000, 6500
```

### 4. filter

```python
prices = [4500, 5000, 6500, 3000]
print(list(filter(lambda p: p >= 5000, prices)))
stock = {"coffee": 3, "latte": 0, "cake": 2, "tea": 0}
print(list(filter(lambda m: stock[m] > 0, stock)))
print(list(map(lambda p: p * 9 // 10, filter(lambda p: p >= 5000, prices))))
# [5000, 6500]
# ['coffee', 'cake']
# [4500, 5850]
```

### 5. map은 한 번만 꺼내져요

```python
m = map(lambda p: p + 500, [4500, 5000])
print(list(m))
print(list(m))
# [5000, 5500]
# []
```

```python
m = map(lambda p: p + 500, [4500, 5000])
ups = list(m)
print(ups)
print(ups)
# [5000, 5500]
# [5000, 5500]
```

### 6. 실습: 주문 기록 고르고 꺼내기

```python
orders = [("kim", "latte", 2), ("lee", "cake", 1), ("park", "coffee", 3), ("kim", "tea", 1)]
many = list(filter(lambda o: o[2] >= 2, orders))
print(many)
print(list(map(lambda o: o[0], many)))
print(sum(map(lambda o: o[2], orders)))
# [('kim', 'latte', 2), ('park', 'coffee', 3)]
# ['kim', 'park']
# 7
```

다 했으면 `Ctrl+S`(Mac `Cmd+S`)로 저장해요.

## 명령어 요약

| 코드 | 하는 일 |
| --- | --- |
| `plus = add10` | 괄호 없이 함수를 변수에 담기 |
| `apply(add10, 5)` | 함수를 다른 함수의 인자로 넘기기 |
| `lambda x: x + 10` | 이름 없는 한 줄 함수. 값 하나를 돌려줘요 |
| `lambda p, q: p * q` | 매개변수 여러 개 |
| `list(map(f, xs))` | 값마다 `f`를 쓴 새 리스트 |
| `map(str, xs)` `map(len, xs)` | 이미 있는 함수는 이름만 넘기기 |
| `list(filter(f, xs))` | `f`가 `True`인 값만 남긴 새 리스트 |
| `filter(f, d)` | 딕셔너리는 키가 하나씩 들어가요 |
| `", ".join(map(str, xs))` | 숫자 리스트를 글자로 이어 찍기 |

## 문제 해결

| 증상 | 원인과 해결 |
| --- | --- |
| `<map object at 0x...>`가 나와요 | `map` 결과를 그대로 찍었어요. `list(map(...))`로 감싸요 |
| `TypeError: 'map' object is not subscriptable` | `map` 결과에 번호를 붙였어요. `list()`로 바꿔 담아요 |
| `TypeError: object of type 'map' has no len()` | `map` 결과에 `len`을 썼어요. `list()`로 바꿔 담아요 |
| 두 번째 `list(m)`이 `[]`예요 | `map`은 한 번 꺼내면 비어요. `ups = list(m)`처럼 리스트로 담아 두고 써요 |
| `TypeError: add10() missing 1 required positional argument: 'x'` | 넘길 함수에 괄호를 붙였어요. `map(add10, xs)`처럼 이름만 적어요 |
| `SyntaxError: invalid syntax` | `lambda` 안에 `return`을 적었어요. `lambda x: x + 10`처럼 값만 적어요 |
| `lambda`가 한눈에 안 읽혀요 | 조건이 여러 개예요. `def`로 만들고 이름만 넘겨요 |

`SyntaxError` 메시지 끝에는 셀마다 다른 파일 이름과 줄 번호가 괄호로 붙어요. 슬라이드에서는 그 부분을 빼고 옮겼어요.

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분 (gen.py가 만들어요)
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py           모든 장과 deck.json 생성 (노트북 셀, map과 filter 파이프 그림, 값 상자)
  demo.sh          hello-uv를 새로 만들고 노트북 셀을 실제로 실행해 출력 확인
  run_nb.py        셀을 프로젝트 커널로 실행 (demo.sh가 불러요)
python-lambda-slides.html  배포용 HTML
python-lambda-slides.pdf   강사용 PDF
```

검사, HTML, PDF를 만드는 공용 도구(`check.js`, `build_player.js`, `export.js`)는 맨 위 [tools/](../tools)에 한 벌만 있어요. 명령은 이 폴더에서 쳐요.

슬라이드 HTML을 직접 고치지 말고 스크립트를 고친 뒤 다시 만들어요.

```bash
bash tools/demo.sh /tmp/lambda-demo > /tmp/lambda-demo.log 2>&1
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/build_player.js slides python-lambda-slides.html
node ../tools/export.js slides python-lambda-slides.pdf
```

셀 출력은 `tools/demo.sh`가 hello-uv(Python 3.14.6)를 만들고 `tools/run_nb.py`로 그 커널에서 실제로 실행한 결과예요. 파트마다 새 커널에서 위에서부터 차례로 실행해서, 셀 번호가 파트마다 [1]부터 시작해요. 오류는 Traceback 위쪽 줄을 빼고 마지막 줄만 옮겼어요. `0x` 주소는 다시 실행하면 바뀌니, 출력을 다시 받으면 gen.py의 주소도 같이 바꿔요.

범위: `lambda`, `map`, `filter`까지만 다뤄요. `reduce`, `zip()`, `*args`, `**kwargs`, `sorted`의 `key`(22), 리스트 컴프리헨션(23)은 다루지 않아요.

</details>

---

<!-- curriculum:nav -->

[← 이전: 20 · 함수 2 (기본값, 지역 변수와 전역 변수)](../20-python-scope) · [커리큘럼](../README.md) · [다음: 22 · 정렬과 sorted, max, min 제대로 쓰기 →](../22-python-sorting)

<!-- /curriculum:nav -->
