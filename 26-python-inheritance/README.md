# 26 · 클래스 3 (상속과 클래스 변수)

> 클래스 마지막 챕터예요. 붕어빵마다 따로 들지 않고 틀에 새겨서 모두 같이 쓰는 값(클래스 변수)과, 붕어빵 틀을 물려받아 슈크림 붕어빵 틀을 만드는 상속을 배워요. 같은 코드를 복사하지 않고 다른 점만 적는 방법이에요. 24의 `Bread` 틀과 25의 `__str__`을 그대로 이어서 써요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/26-python-inheritance/python-inheritance-slides.html) | [25 · 클래스 2 (`__str__`과 `__repr__`)](../25-python-str-repr) | 준비 중 |

<!-- /curriculum:top -->

## 학습 목표

이 챕터를 마치면 다음을 할 수 있어요.

- 틀에 적은 클래스 변수(`shop`, `count`)와 `self.`로 붙인 인스턴스 변수의 차이를 말해요.
- 클래스 변수는 `Bread.shop =`처럼 틀 이름으로 바꾸고 세요.
- `class CreamBread(Bread):`로 틀을 물려받고, 자식 틀에 메서드를 더해요.
- 칸을 더할 때 `super().__init__(flavor, price)`로 부모에게 맡겨요.
- 같은 이름의 메서드로 덮어쓰고, `super().intro()`로 부모 것을 불러요.
- "~는 ~의 한 종류"일 때만 상속한다는 기준으로 상속할지 골라요.

## 시작하기 전에

| 할 일 | 챕터 |
| --- | :---: |
| `class`, `__init__`, `self`, 메서드 | 24 |
| `__str__`, `__repr__` | 25 |
| 기본값, 지역 변수와 전역 변수 | 20 |
| `for`, 컴프리헨션 | 13, 23 |

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1–3 | 표지, 오늘의 순서, `basics.ipynb` 다시 열기 |
| 1. 왜 필요한가 | 4–5 | 복사해서 만든 슈크림 붕어빵 틀(왜 필요한가), 틀에 새긴 값과 물려받는 틀 그림(큰 그림) |
| 2. 클래스 변수 | 6–9 | 틀에 적은 값, 한 번에 바꾸기, 찍을 때마다 개수 세기, 인스턴스 변수와 비교 |
| 3. 상속 | 10–17 | `pass`로 전부 물려받기, 자식에 메서드 더하기, `super().__init__`, 한 줄에서 일어나는 다섯 단계, 덮어쓰기, `super().intro()`, 섞어 담기와 `isinstance`, 눌러 보기(어디서부터 찾을까) |
| 4. 복사와 상속 비교 | 18–19 | 고칠 곳이 한 군데, "~는 ~의 한 종류"일 때만 |
| 5. 오류와 함정 | 20–24 | `super().__init__` 빠짐, `self` 두 번, 자식 재료 수, `a.shop =`, `self.count` |
| 6. 실습 | 25–28 | 도장 카드와 VIP 카드 두 장, 붕어빵과 미니 붕어빵 메뉴판 두 장 |
| 정리 | 29–30 | 막힐 때, 한 장 요약 |

## 핵심 개념

### 클래스 변수와 인스턴스 변수

| | 인스턴스 변수 | 클래스 변수 |
| --- | --- | --- |
| 어디에 적나요 | `__init__` 안, `self.flavor = ...` | `class` 바로 아래, `shop = ...` |
| 누구 것인가요 | 붕어빵 하나하나 | 틀 하나 |
| 바꾸기 | `a.flavor = ...` | `Bread.shop = ...` |
| 예 | 맛, 가격, 도장 수 | 가게 이름, 전체 개수 |

`a.shop`을 꺼내면 파이썬은 붕어빵 `a`에서 먼저 찾고, 없으면 틀 `Bread`에서 찾아요.

### `CreamBread("슈크림", 1200, "많이")` 한 줄에서

1. 자식의 `__init__`이 불려요. `self`는 새 붕어빵이에요.
2. `super().__init__(flavor, price)`로 부모의 `__init__`에 가요. 같은 `self`예요.
3. 부모가 `self.flavor`, `self.price`를 붙여요.
4. 자식으로 돌아와 `self.cream`을 붙여요.
5. 세 칸이 다 붙은 붕어빵이 `c`에 담겨요.

메서드는 자식 틀부터 찾고, 없으면 부모 틀로 올라가요.

## 실습

VS Code에서 `hello-uv` 폴더를 열고 `basics.ipynb`를 열어요. 아래 코드를 셀 하나에 한 덩어리씩 적고 `Shift+Enter`로 실행해요. 주석(`#` 뒤)은 실제 출력이에요.

### 1. 클래스 변수

```python
class Bread:
    shop = "붕어빵 1호점"
    count = 0

    def __init__(self, flavor, price):
        self.flavor = flavor
        self.price = price
        Bread.count = Bread.count + 1

a = Bread("팥", 1000)
b = Bread("슈크림", 1200)
print(a.shop, b.shop)
Bread.shop = "붕어빵 2호점"
print(a.shop, b.shop)
print(Bread.count)
# 붕어빵 1호점 붕어빵 1호점
# 붕어빵 2호점 붕어빵 2호점
# 2
```

### 2. 상속과 `super().__init__`

```python
class Bread:
    def __init__(self, flavor, price):
        self.flavor = flavor
        self.price = price

    def intro(self):
        print(self.flavor, "붕어빵", self.price, "원")

class CreamBread(Bread):
    def __init__(self, flavor, price, cream):
        super().__init__(flavor, price)
        self.cream = cream

    def intro(self):
        super().intro()
        print("  크림:", self.cream)

order = [Bread("팥", 1000), CreamBread("슈크림", 1200, "보통"), Bread("피자", 1500)]
for b in order:
    b.intro()
# 팥 붕어빵 1000 원
# 슈크림 붕어빵 1200 원
#   크림: 보통
# 피자 붕어빵 1500 원
```

### 3. `isinstance`

```python
c = CreamBread("슈크림", 1200, "많이")
print(isinstance(c, CreamBread))
print(isinstance(c, Bread))
print(isinstance(order[0], CreamBread))
# True
# True
# False
```

### 4. 실습: 도장 카드와 VIP 카드

```python
class Card:
    shop = "KANT 카페"
    goal = 10

    def __init__(self, name):
        self.name = name
        self.stamps = 0

    def add(self):
        self.stamps = self.stamps + 1

    def __str__(self):
        left = Card.goal - self.stamps
        return f"[{Card.shop}] {self.name}: 도장 {self.stamps}개, {left}개 남음"

class VipCard(Card):
    def add(self):
        self.stamps = self.stamps + 2

kim = Card("kim")
lee = VipCard("lee")
kim.add()
kim.add()
lee.add()
lee.add()
print(kim)
print(lee)
# [KANT 카페] kim: 도장 2개, 8개 남음
# [KANT 카페] lee: 도장 4개, 6개 남음
```

### 5. 실습: 붕어빵과 미니 붕어빵 메뉴판

```python
class Bread:
    count = 0

    def __init__(self, flavor, price):
        self.flavor = flavor
        self.price = price
        Bread.count = Bread.count + 1

    def __str__(self):
        return f"{self.flavor} 붕어빵 {self.price:,}원"

class MiniBread(Bread):
    def __init__(self, flavor, price, qty):
        super().__init__(flavor, price)
        self.qty = qty

    def __str__(self):
        return f"미니 {self.flavor} {self.qty}개 {self.price * self.qty:,}원"

menu = [Bread("팥", 1000), MiniBread("팥", 300, 5), Bread("슈크림", 1200), MiniBread("슈크림", 400, 5)]
for m in menu:
    print(m)
print("찍은 붕어빵:", Bread.count)
print([m.flavor for m in menu if isinstance(m, MiniBread)])
# 팥 붕어빵 1,000원
# 미니 팥 5개 1,500원
# 슈크림 붕어빵 1,200원
# 미니 슈크림 5개 2,000원
# 찍은 붕어빵: 4
# ['팥', '슈크림']
```

다 했으면 `Ctrl+S`(Mac `Cmd+S`)로 저장해요.

## 명령어 요약

| 코드 | 하는 일 |
| --- | --- |
| `shop = "붕어빵 1호점"` (class 바로 아래) | 클래스 변수. 모든 붕어빵이 같이 봐요 |
| `Bread.shop = ...` | 클래스 변수 바꾸기. 틀 이름으로 |
| `class CreamBread(Bread):` | 부모 틀 물려받기 |
| `super().__init__(flavor, price)` | 부모의 `__init__`에 맡기기. `self`는 안 적어요 |
| 같은 이름 `def intro(self):` | 부모 메서드 덮어쓰기 |
| `super().intro()` | 부모 메서드 부르기 |
| `isinstance(c, Bread)` | 그 틀(또는 그 자식)로 찍었는지 True, False |

## 문제 해결

| 메시지 | 원인 | 해결 |
| --- | --- | --- |
| `AttributeError: 'CreamBread' object has no attribute 'flavor'` | 자식 `__init__`에서 `super().__init__`을 안 불렀어요 | 자식 `__init__` 첫 줄에 `super().__init__(flavor, price)` |
| `TypeError: Bread.__init__() takes 3 positional arguments but 4 were given` | `super().__init__`에 `self`를 넣었어요 | `self`를 빼요 |
| `TypeError: CreamBread.__init__() missing 1 required positional argument: 'cream'` | 자식 틀의 재료가 모자라요 | 자식 `__init__`의 칸 수에 맞추거나 기본값을 둬요 |
| `NameError: name 'Bred' is not defined` | 괄호 안 부모 이름 오타이거나 부모 셀을 아직 안 실행했어요 | 이름을 고치고 부모 셀을 먼저 실행해요 |
| 한 붕어빵만 값이 달라요 | `a.shop =`으로 바꿔서 `a`에만 새 칸이 생겼어요 | `Bread.shop =` |
| 개수가 0에서 안 늘어요 | `self.count = self.count + 1`로 셌어요 | `Bread.count = Bread.count + 1` |
| 부모를 고쳤는데 자식은 그대로예요 | 자식이 같은 이름으로 덮어썼어요 | 자식에서 `super().메서드()`로 불러요 |

헷갈리면 "자식 틀에서 먼저 찾고, 없으면 부모 틀" 순서로 따라가 봐요.

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분 (gen.py가 만들어요)
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py           모든 장과 deck.json 생성 (노트북 셀, 부모와 자식 틀 그림, super 단계)
  demo.sh          hello-uv를 새로 만들고 노트북 셀을 실제로 실행해 출력 확인
  run_nb.py        셀을 프로젝트 커널로 실행 (demo.sh가 불러요)
  lab_find.js      17쪽 어디서부터 찾을까의 버튼 동작 (gen.py가 그 장에 넣어요)
python-inheritance-slides.html  배포용 HTML
python-inheritance-slides.pdf   강사용 PDF
```

검사, HTML, PDF를 만드는 공용 도구는 맨 위 [tools/](../tools)에 한 벌만 있어요. 명령은 이 폴더에서 쳐요.

```bash
bash tools/demo.sh /tmp/inheritance-demo > /tmp/inheritance-demo.log 2>&1
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/build_player.js slides python-inheritance-slides.html
node ../tools/export.js slides python-inheritance-slides.pdf
```

셀 출력은 `tools/demo.sh`가 hello-uv(Python 3.14.6)를 만들고 `tools/run_nb.py`로 그 커널에서 실제로 실행한 결과예요. 파트마다 새 커널에서 차례로 실행해서 셀 번호가 파트마다 [1]부터 시작해요. 4파트는 셀 없이 그림과 표만 있어요. 오류는 Traceback 마지막 줄만 옮겼어요.

장마다 강조는 `tools/HIGHLIGHT.md`에서 골랐어요. 표지는 제목이 크게 들어오고 코드 칸에 빛이 지나가요. 목차, 들어가기, 19, 29, 30쪽 목록은 한 번 누르면 차례로 나와요(시차). 5쪽 화살표는 왼쪽부터 그려지고, 6쪽과 13쪽은 지난 단계가 흐려져요. 7쪽 붕어빵 이름표와 8쪽 개수는 값이 바뀌고, 8쪽과 26쪽은 실행 막대가 줄을 따라 내려가요. 9쪽 표는 스포트라이트로, 25, 27쪽 코드는 줄 스포트라이트로 한 덩어리씩 비춰요. 10쪽은 코드의 틀 이름과 그림의 틀이 같은 색으로 짝지어지고, 11, 14쪽은 부른 줄과 출력을 선으로 이어요. 17쪽은 커서가 누를 곳을 짚어요. 20쪽 오류는 한 번 흔들리고, 21, 24쪽은 틀린 줄이 그 자리에서 고친 줄로 바뀌어요(코드 모핑). 22쪽은 더한 글자만 칠하고, 23, 24쪽은 그대로인 틀을 두 번 두드려요.

눌러 보기 장은 장 안의 `<script type="text/slide-js">`를 `build_player.js`가 실행해서 움직여요. 그래서 버튼은 배포용 HTML에서만 눌러지고, PDF에는 처음 화면이 들어가요. 눌러 보기에 나오는 출력도 `tools/run_nb.py`로 실제로 실행한 결과예요.

범위: 클래스 변수, 상속, `super()`, 덮어쓰기, `isinstance`를 처음 다뤄요. 다중 상속, `classmethod`, `staticmethod`, `@property`, 추상 클래스, `_`로 숨기기는 다루지 않아요.

</details>

---

<!-- curriculum:nav -->

[← 이전: 25 · 클래스 2 (`__str__`과 `__repr__`)](../25-python-str-repr) · [커리큘럼](../README.md)

<!-- /curriculum:nav -->
