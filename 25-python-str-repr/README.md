# 25 · 클래스 2 (`__str__`과 `__repr__`)

> 24에서 만든 붕어빵을 통째로 print하면 `<__main__.Bread object at 0x...>`가 나왔어요. 이번 챕터는 파이썬이 정해진 순간에 알아서 부르는 메서드 `__str__`과 `__repr__`으로 그 글자를 바꿔요. 왜 필요한지, 언제 불리는지, 둘이 어떻게 다른지를 차례로 보고, 붕어빵 여러 개를 정렬하고 재고가 줄어드는 노점을 만들어요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/25-python-str-repr/python-str-repr-slides.html) | [24 · 클래스 1 (붕어빵 틀과 붕어빵)](../24-python-class) | [26 · 클래스 3 (상속과 클래스 변수)](../26-python-inheritance) |

<!-- /curriculum:top -->

## 학습 목표

이 챕터를 마치면 다음을 할 수 있어요.

- 앞뒤 밑줄 두 개짜리 메서드는 직접 부르지 않고, 정해진 순간에 파이썬이 찾아 부른다는 걸 설명해요.
- `__str__`을 만들어 `print(a)`, `str(a)`, f-string에서 붕어빵이 보기 좋게 나오게 해요.
- `__repr__`을 만들어 셀 마지막 줄과 리스트 안에서도 붕어빵이 보이게 해요.
- 셀의 `'팥'`과 `print`의 `팥`이 repr과 str의 차이라는 걸 알고, 하나만 만든다면 `__repr__`이라는 걸 알아요.
- 붕어빵 리스트를 컴프리헨션과 `sorted(key=lambda ...)`로 다뤄요.
- 메서드로 재고 같은 상태를 바꾸고 `if`와 `return`으로 막아요.

## 시작하기 전에

24의 `Bread` 틀과 `basics.ipynb`에서 이어서 해요.

| 할 일 | 챕터 |
| --- | :---: |
| `class`, `__init__`, `self`, 메서드 | 24 |
| f-string, 칸 맞추기, 천 단위 콤마 | 13 |
| `if`와 `return` | 17, 19 |
| `sorted`, `max`의 `key=lambda` | 22 |
| 컴프리헨션 | 23 |

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1–3 | 표지, 오늘의 순서, `basics.ipynb` 다시 열기 |
| 1. 왜 필요한가 | 4–6 | 숫자와 리스트는 보이는데 붕어빵은 안 보이는 장면(왜 필요한가), 파이썬이 정해진 순간에 찾아 부르는 메서드 그림(큰 그림), 가장 짧은 `__str__` |
| 2. `__str__` | 7–9 | `self`의 값으로 붕어빵마다 다르게, `str()`과 f-string에서도 불리기, 24의 `intro()`와 비교 |
| 3. `__repr__` | 10–16 | `__str__`이 못 바꾸는 곳(셀 마지막 줄, 리스트 안), `'팥'`과 `팥`, `__repr__` 만들기, 언제 어느 쪽이 불리는지 표, 눌러 보기(누가 불릴까), 하나만 만든다면 `__repr__`, 참고로 읽기만 하는 `len`과 `+` |
| 4. 붕어빵 여러 개 다루기 | 17–21 | 리스트와 `for`, 컴프리헨션, `key=lambda` 정렬과 `max`, 재고 바꾸는 메서드, `if`로 막기 |
| 5. 오류와 함정 | 22–25 | `__str__` 안의 print, 숫자 돌려주기, 밑줄 하나, 글자에 붕어빵 더하기 |
| 6. 실습 | 26–28 | 붕어빵 노점의 하루 두 장, 카페 메뉴판 |
| 정리 | 29–30 | 막힐 때, 한 장 요약 |

## 핵심 개념

### 파이썬이 알아서 부르는 메서드

| 이렇게 쓰면 | 파이썬이 찾는 메서드 | 없으면 |
| --- | --- | --- |
| `Bread("팥", 1000)` | `__init__` | 재료 없이 찍기 |
| `print(a)`, `str(a)`, `f"{a}"` | `__str__` (없으면 `__repr__`을 빌려 써요) | `<__main__.Bread object at 0x...>` |
| 셀 마지막 줄의 `a` | `__repr__` | `<__main__.Bread at 0x...>` |
| `print([a, b])` | 안의 값은 `__repr__` | `[<__main__.Bread object at 0x...>, ...]` |

### 손님용과 만든 사람용

| | `__str__` | `__repr__` |
| --- | --- | --- |
| 비유 | 손님에게 보여 주는 메뉴판 글씨 | 만든 사람이 보는 주문표 |
| 예 | `팥 붕어빵 1,000원` | `Bread('팥', 1000)` |
| 이미 본 모양 | `print("팥")`의 `팥` | 셀 마지막 줄 `"팥"`의 `'팥'` |

두 메서드 모두 꼭 글자를 `return`해요. 하나만 만든다면 더 많은 곳을 해결하는 `__repr__`이에요.

## 실습

VS Code에서 `hello-uv` 폴더를 열고 `basics.ipynb`를 열어요. 아래 코드를 셀 하나에 한 덩어리씩 적고 `Shift+Enter`로 실행해요. 주석(`#` 뒤)은 실제 출력이에요. `0x`로 시작하는 주소는 실행할 때마다 달라요.

### 1. 붕어빵을 print하면

```python
class Bread:
    def __init__(self, flavor, price):
        self.flavor = flavor
        self.price = price

a = Bread("팥", 1000)
print(a)
# <__main__.Bread object at 0x7f6735bb38c0>
```

### 2. `__str__`

```python
class Bread:
    def __init__(self, flavor, price):
        self.flavor = flavor
        self.price = price

    def __str__(self):
        return f"{self.flavor} 붕어빵 {self.price:,}원"

a = Bread("팥", 1000)
b = Bread("슈크림", 1200)
print(a)
print(f"주문: {a}")
print("오늘의 빵:", b)
print([a, b])
# 팥 붕어빵 1,000원
# 주문: 팥 붕어빵 1,000원
# 오늘의 빵: 슈크림 붕어빵 1,200원
# [<__main__.Bread object at 0x7febaa53c6e0>, <__main__.Bread object at 0x7febaa7fb890>]
```

### 3. `__repr__`까지

```python
class Bread:
    def __init__(self, flavor, price):
        self.flavor = flavor
        self.price = price

    def __str__(self):
        return f"{self.flavor} 붕어빵 {self.price:,}원"

    def __repr__(self):
        return f"Bread('{self.flavor}', {self.price})"

a = Bread("팥", 1000)
b = Bread("슈크림", 1200)
print(a)
print([a, b])
# 팥 붕어빵 1,000원
# [Bread('팥', 1000), Bread('슈크림', 1200)]
```

셀 마지막 줄에 `a`만 적으면 `Bread('팥', 1000)`이 보여요.

### 4. 붕어빵 여러 개

```python
breads = [Bread("팥", 1000), Bread("슈크림", 1200), Bread("피자", 1500)]
for b in breads:
    print(b)
print([b for b in breads if b.price >= 1200])
print(sorted(breads, key=lambda b: b.price, reverse=True))
print(max(breads, key=lambda b: b.price))
# 팥 붕어빵 1,000원
# 슈크림 붕어빵 1,200원
# 피자 붕어빵 1,500원
# [Bread('슈크림', 1200), Bread('피자', 1500)]
# [Bread('피자', 1500), Bread('슈크림', 1200), Bread('팥', 1000)]
# 피자 붕어빵 1,500원
```

### 5. 실습: 붕어빵 노점의 하루

```python
class Stall:
    def __init__(self, flavor, price, stock):
        self.flavor = flavor
        self.price = price
        self.stock = stock
        self.sold = 0

    def sell(self, qty):
        if qty > self.stock:
            return f"{self.flavor} 재고가 모자라요"
        self.stock = self.stock - qty
        self.sold = self.sold + qty
        return f"{self.flavor} {qty}개 판매"

    def __str__(self):
        return f"{self.flavor}: 판매 {self.sold}개, 매출 {self.sold * self.price:,}원"
```

```python
pat = Stall("팥", 1000, 20)
cream = Stall("슈크림", 1200, 10)
print(pat.sell(5))
print(cream.sell(12))
print(cream.sell(4))
print(pat)
print(cream)
# 팥 5개 판매
# 슈크림 재고가 모자라요
# 슈크림 4개 판매
# 팥: 판매 5개, 매출 5,000원
# 슈크림: 판매 4개, 매출 4,800원
```

### 6. 실습: 카페 메뉴판

```python
class Drink:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def __str__(self):
        return f"{self.name:<7}{self.price:>6,}원"

    def __repr__(self):
        return f"Drink('{self.name}', {self.price})"

menu = [Drink("latte", 5000), Drink("tea", 4000), Drink("coffee", 4500)]
for d in sorted(menu, key=lambda d: d.price):
    print(d)
print([d for d in menu if d.price < 5000])
# tea     4,000원
# coffee  4,500원
# latte   5,000원
# [Drink('tea', 4000), Drink('coffee', 4500)]
```

다 했으면 `Ctrl+S`(Mac `Cmd+S`)로 저장해요.

## 명령어 요약

| 코드 | 하는 일 |
| --- | --- |
| `def __str__(self):` | print, `str()`, f-string에서 보일 글자 |
| `def __repr__(self):` | 셀 마지막 줄, 리스트 안에서 보일 글자 |
| `return f"..."` | 두 메서드 모두 꼭 글자를 돌려줘요 |
| `str(a)` `repr(a)` | 글자로 바꾸기. 각각 `__str__`, `__repr__`을 불러요 |
| `sorted(xs, key=lambda b: b.price)` | 붕어빵을 가격으로 줄 세우기 |
| `self.stock = self.stock - qty` | 메서드로 상태 바꾸기 |

## 문제 해결

| 메시지 | 원인 | 해결 |
| --- | --- | --- |
| `<__main__.Bread object at 0x...>` | `__str__`, `__repr__`이 없거나 밑줄이 하나예요 | 앞뒤 밑줄 두 개로 `__repr__` 만들기 |
| 리스트 안만 `<... object ...>` | `__str__`만 만들었어요 | `__repr__`도 만들어요 |
| `TypeError: __str__ returned non-string (type NoneType)` | 안에서 print했어요 | `return`으로 글자를 돌려줘요 |
| `TypeError: __str__ returned non-string (type int)` | 숫자를 돌려줬어요 | `str()`이나 f-string으로 감싸요 |
| `TypeError: can only concatenate str (not "Bread") to str` | 글자에 붕어빵을 바로 더했어요 | `str(a)`, `f"{a}"`, `print("주문:", a)` |
| `TypeError: '<' not supported between instances of 'Bread' and 'Bread'` | 붕어빵끼리 비교할 기준이 없어요 | `key=lambda b: b.price` |
| 재고가 마이너스가 돼요 | 메서드에서 값을 확인하지 않았어요 | `if`와 `return`으로 막아요 |

낯선 글자가 나오면 "지금 파이썬이 어느 메서드를 찾았을까"부터 생각해요.

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분 (gen.py가 만들어요)
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py           모든 장과 deck.json 생성 (노트북 셀, 파이썬이 찾는 메서드 그림, 불리는 곳 표)
  demo.sh          hello-uv를 새로 만들고 노트북 셀을 실제로 실행해 출력 확인
  run_nb.py        셀을 프로젝트 커널로 실행 (demo.sh가 불러요)
  lab_who.js       14쪽 누가 불릴까의 버튼 동작 (gen.py가 그 장에 넣어요)
python-str-repr-slides.html  배포용 HTML
python-str-repr-slides.pdf   강사용 PDF
```

검사, HTML, PDF를 만드는 공용 도구는 맨 위 [tools/](../tools)에 한 벌만 있어요. 명령은 이 폴더에서 쳐요.

```bash
bash tools/demo.sh /tmp/str-repr-demo > /tmp/str-repr-demo.log 2>&1
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/build_player.js slides python-str-repr-slides.html
node ../tools/export.js slides python-str-repr-slides.pdf
```

셀 출력은 `tools/demo.sh`가 hello-uv(Python 3.14.6)를 만들고 `tools/run_nb.py`로 그 커널에서 실제로 실행한 결과예요. 파트마다 새 커널에서 차례로 실행해서 셀 번호가 파트마다 [1]부터 시작해요. 오류는 Traceback 마지막 줄만 옮겼어요. `0x` 주소는 다시 실행하면 바뀌니, 출력을 다시 받으면 gen.py의 주소도 같이 바꿔요. 노트북은 셀 마지막 줄의 객체를 `<__main__.Bread at 0x...>`처럼 `object` 없이 보여 줘요(10쪽).

눌러 보기 장은 장 안의 `<script type="text/slide-js">`를 `build_player.js`가 실행해서 움직여요. 그래서 버튼은 배포용 HTML에서만 눌러지고, PDF에는 처음 화면이 들어가요. 눌러 보기에 나오는 출력도 `tools/run_nb.py`로 실제로 실행한 결과예요.

장 디자인은 `tools/DESIGN.md`(Stageshow 원칙)와 `tools/HIGHLIGHT.md`를 따라요. 장마다 노트북 셀 하나를 크게 두고, 설명은 셀 옆 "← 짧은 글"로 달아요. 긴 설명은 발표자 노트에 둬요. 오류 장은 틀린 줄에 줄을 긋고 고친 줄을 옆에 둬요. 14쪽 눌러 보기의 출력은 글자를 하나씩 찍지 않고 한 줄이 한 번에 나타나요.

범위: `__str__`, `__repr__`, `repr()`, 메서드로 상태 바꾸기를 처음 다뤄요. `__len__`, `__add__`는 16쪽에서 읽기만 보여 줘요. 그 밖의 매직 메서드, `__eq__`, `!r` 포맷, `@property`는 다루지 않아요.

</details>

---

<!-- curriculum:nav -->

[← 이전: 24 · 클래스 1 (붕어빵 틀과 붕어빵)](../24-python-class) · [커리큘럼](../README.md) · [다음: 26 · 클래스 3 (상속과 클래스 변수) →](../26-python-inheritance)

<!-- /curriculum:nav -->
