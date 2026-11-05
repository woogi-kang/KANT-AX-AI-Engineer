# 24 · 클래스 1 (붕어빵 틀과 붕어빵)

> 클래스는 붕어빵 틀이고, 그 틀로 찍어 낸 붕어빵 하나하나가 객체예요. 이번 챕터는 틀을 만들고, 찍을 때 재료를 넣는 `__init__`과 `self`를 19의 함수에서 출발해 한 걸음씩 봐요. 그다음 붕어빵이 할 일을 메서드로 붙여요. 25에서는 print로 보기 좋게 찍는 법, 26에서는 틀을 물려받는 상속을 배워요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/24-python-class/python-class-slides.html) | [23 · 리스트 컴프리헨션](../23-python-comprehension) | [25 · 클래스 2 (`__str__`과 `__repr__`)](../25-python-str-repr) |

<!-- /curriculum:top -->

## 학습 목표

이 챕터를 마치면 다음을 할 수 있어요.

- 틀(클래스), 붕어빵(객체), 속성, 메서드가 무엇인지 그림으로 말해요.
- `class Bread:`로 틀을 만들고 `Bread("팥", 1000)`으로 붕어빵을 찍어요.
- `__init__`이 찍는 순간 저절로 불리고, 괄호 안의 재료가 `self` 뒤 칸에 순서대로 들어간다는 걸 설명해요.
- `self`가 "방금 찍은 붕어빵", "메서드를 부른 붕어빵"이라는 걸 알고 `self.flavor = flavor`를 읽어요.
- `def intro(self):`로 메서드를 만들고 `a.intro()`로 불러요. `a.intro()`가 `Bread.intro(a)`와 같다는 걸 알아요.
- 재료 수, `self` 빠짐, `__init__` 이름 오타로 나는 오류를 읽고 고쳐요.

## 시작하기 전에

12~23에서 쓰던 `hello-uv`의 `basics.ipynb`와 그때 배운 내용을 그대로 써요. 특히 19, 20의 함수를 많이 써요.

| 할 일 | 챕터 |
| --- | :---: |
| VS Code에 Python, Jupyter 확장 설치, `uv add --dev ipykernel`, 커널로 `.venv` 고르기 | 09, 10 |
| 변수, 타입, `type()` | 12 |
| 리스트, f-string, `for` | 13 |
| 딕셔너리 | 15 |
| `def`, 매개변수, `return` | 19 |
| 기본값, 지역 변수 | 20 |
| 컴프리헨션 | 23 |

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1–3 | 표지, 오늘의 순서, `basics.ipynb` 다시 열기 |
| 1. 왜 필요한가 | 4–6 | 딕셔너리와 함수로 만든 붕어빵의 불편함(왜 필요한가), 틀과 붕어빵 그림(큰 그림), `type()`으로 본 int, str, list 틀 |
| 2. 가장 작은 틀 | 7–9 | `class`와 `pass`, 점으로 값 붙이기, 손으로 붙일 때 빠뜨리는 문제 |
| 3. self와 `__init__` | 10–20 | 19의 함수 `setup(bread, ...)`로 붙이기, 틀 안으로 옮겨 `__init__`, 괄호 안 재료가 칸으로 날아가는 그림, 찍을 때 저절로 불리는지 확인, `self` 따라가기 두 장, 한 줄에서 일어나는 다섯 단계, 눌러 보기(붕어빵 기계), `self.flavor = flavor` 왼쪽과 오른쪽, `self.`를 빼면, 재료로 받지 않는 칸 |
| 4. 메서드 | 21–24 | `intro` 만들기, `a.intro()`는 `Bread.intro(a)`, 값 바꾸기와 `return`, 딕셔너리와 비교 |
| 5. 오류와 함정 | 25–28 | 재료 수, 메서드의 `self` 빠짐, `_init_` 밑줄, 붕어빵을 print하면 |
| 6. 실습 | 29–31 | 붕어빵 주문과 합계, 카페 음료 이름표, 도장 카드 |
| 정리 | 32–33 | 막힐 때, 한 장 요약 |

## 핵심 개념

### 틀과 붕어빵

| 말 | 뜻 | 코드 |
| --- | --- | --- |
| 틀 = 클래스 | 붕어빵을 찍는 모양 | `class Bread:` |
| 붕어빵 = 객체 | 틀로 찍어 낸 것 하나 | `a = Bread("팥", 1000)` |
| 속성 | 붕어빵에 든 값 | `a.flavor`, `a.price` |
| 메서드 | 붕어빵이 하는 일 (틀 안의 함수) | `a.intro()` |

### 함수에서 `__init__`으로

```python
# 19의 함수로 붙이기              # 틀 안의 __init__
def setup(bread, flavor, price):    class Bread:
    bread.flavor = flavor               def __init__(self, flavor, price):
    bread.price = price                     self.flavor = flavor
                                            self.price = price
a = Bread()
setup(a, "팥", 1000)                a = Bread("팥", 1000)
```

함수를 틀 안에 넣고 이름을 `__init__`으로 바꾸면, 찍을 때 파이썬이 저절로 불러요. 첫 칸 `bread`는 이름만 `self`로 바뀌었고, 파이썬이 방금 찍은 붕어빵을 넣어 줘요.

### `a = Bread("팥", 1000)` 한 줄에서

1. 빈 붕어빵이 하나 생겨요.
2. 파이썬이 `__init__(빈 붕어빵, "팥", 1000)`을 불러요. 빈 붕어빵이 `self`예요.
3. `self.flavor = "팥"`으로 맛 칸을 붙여요.
4. `self.price = 1000`으로 가격 칸을 붙여요.
5. 다 된 붕어빵을 `a`에 담아요.

`self.flavor`는 붕어빵에 남는 칸이고, 오른쪽 `flavor`는 `__init__`이 끝나면 사라지는 재료(20의 지역 변수)예요.

## 실습

VS Code에서 `hello-uv` 폴더를 열고 `basics.ipynb`를 열어요. 오른쪽 위 커널이 `.venv`인지 본 뒤, 아래 코드를 셀 하나에 한 덩어리씩 적고 `Shift+Enter`로 실행해요. 주석(`#` 뒤)은 실제 출력이에요.

### 1. 빈 틀과 손으로 붙이기

```python
class Bread:
    pass

a = Bread()
a.flavor = "팥"
a.price = 1000
print(a.flavor, a.price)
# 팥 1000
```

### 2. `__init__`으로 찍을 때 재료 넣기

```python
class Bread:
    def __init__(self, flavor, price):
        print("반죽 붓는 중:", flavor)
        self.flavor = flavor
        self.price = price

a = Bread("팥", 1000)
b = Bread("슈크림", 1200)
print(a.flavor, b.flavor)
# 반죽 붓는 중: 팥
# 반죽 붓는 중: 슈크림
# 팥 슈크림
```

### 3. 메서드

```python
class Bread:
    def __init__(self, flavor, price):
        self.flavor = flavor
        self.price = price

    def intro(self):
        print(self.flavor, "붕어빵", self.price, "원")

    def discount(self, won):
        self.price = self.price - won

    def total(self, qty):
        return self.price * qty

a = Bread("팥", 1000)
b = Bread("슈크림", 1200)
a.discount(200)
a.intro()
b.intro()
print(a.total(3))
# 팥 붕어빵 800 원
# 슈크림 붕어빵 1200 원
# 2400
```

### 4. 실습: 붕어빵 주문과 합계

```python
order = [Bread("팥", 1000), Bread("슈크림", 1200), Bread("팥", 1000)]
for b in order:
    b.intro()
total = sum([b.price for b in order])
print("합계", total, "원")
# 팥 붕어빵 1000 원
# 슈크림 붕어빵 1200 원
# 팥 붕어빵 1000 원
# 합계 3200 원
```

3번 셀의 `Bread` 틀을 그대로 써요. `discount`로 바꾼 값은 `a`에만 들어 있어서 새로 찍은 붕어빵은 원래 가격이에요.

### 5. 실습: 카페 음료 이름표

```python
class Drink:
    def __init__(self, name, price, size="M"):
        self.name = name
        self.price = price
        self.size = size

    def label(self):
        return f"{self.name}({self.size}) {self.price:,}원"

d1 = Drink("latte", 5000)
d2 = Drink("tea", 4000, "L")
print(d1.label())
print(d2.label())
# latte(M) 5,000원
# tea(L) 4,000원
```

### 6. 실습: 도장 카드

```python
class Card:
    def __init__(self, name):
        self.name = name
        self.stamps = 0

    def add(self):
        self.stamps = self.stamps + 1

kim = Card("kim")
lee = Card("lee")
kim.add()
kim.add()
kim.add()
lee.add()
print(kim.name, kim.stamps)
print(lee.name, lee.stamps)
# kim 3
# lee 1
```

다 했으면 `Ctrl+S`(Mac `Cmd+S`)로 저장해요.

## 명령어 요약

| 코드 | 하는 일 |
| --- | --- |
| `class Bread:` | 틀 만들기. 첫 글자는 대문자 |
| `pass` | 아직 아무것도 안 넣었다는 표시 |
| `Bread("팥", 1000)` | 붕어빵 찍기 |
| `def __init__(self, flavor, price):` | 찍을 때 저절로 불리는 메서드 |
| `self.flavor = flavor` | 붕어빵에 칸 붙이기 |
| `self.stamps = 0` | 재료로 받지 않고 처음 값 정하기 |
| `def intro(self):` | 메서드 만들기. 첫 칸은 `self` |
| `a.intro()` | 메서드 부르기. `Bread.intro(a)`와 같아요 |
| `a.flavor` | 속성 꺼내기 |

## 문제 해결

| 메시지 | 원인 | 해결 |
| --- | --- | --- |
| `TypeError: Bread.__init__() missing 1 required positional argument: 'price'` | 찍을 때 재료가 모자라요 | `self` 뒤 칸 수만큼 재료를 넣어요 |
| `TypeError: Bread.intro() takes 0 positional arguments but 1 was given` | 메서드에 `self`를 안 적었어요 | `def intro(self):` |
| `TypeError: Bread() takes no arguments` | `_init_`, `__int__`처럼 이름이 틀렸어요 | 앞뒤 밑줄 두 개씩 `__init__` |
| `AttributeError: 'Bread' object has no attribute 'flavor'` | 칸 이름 오타이거나 `__init__`에서 `self.`를 뺐어요 | `self.flavor = flavor` |
| `NameError: name 'flavor' is not defined` | 메서드 안에서 `self.flavor` 대신 `flavor`를 썼어요 | `self.flavor` |
| `<__main__.Bread object at 0x...>` | 붕어빵을 통째로 print했어요. 오류는 아니에요 | 지금은 `a.flavor`로, 25에서 `__str__` |
| `TypeError: Bread.intro() missing 1 required positional argument: 'self'` | `a = Bread`처럼 괄호 없이 틀을 담았어요 | `Bread("팥", 1000)` |

헷갈리면 `self` 자리에 붕어빵 이름(`a`)을 넣어 `a.flavor = "팥"`처럼 소리 내어 읽어 봐요.

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분 (gen.py가 만들어요)
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py           모든 장과 deck.json 생성 (노트북 셀, 붕어빵 틀과 붕어빵 그림, self 따라가기)
  demo.sh          hello-uv를 새로 만들고 노트북 셀을 실제로 실행해 출력 확인
  run_nb.py        셀을 프로젝트 커널로 실행 (demo.sh가 불러요)
  lab_stamp.js     17쪽 붕어빵 기계의 버튼 동작 (gen.py가 그 장에 넣어요)
python-class-slides.html  배포용 HTML
python-class-slides.pdf   강사용 PDF
```

검사, HTML, PDF를 만드는 공용 도구(`check.js`, `build_player.js`, `export.js`)는 맨 위 [tools/](../tools)에 한 벌만 있어요. 명령은 이 폴더에서 쳐요.

슬라이드 HTML을 직접 고치지 말고 스크립트를 고친 뒤 다시 만들어요.

```bash
bash tools/demo.sh /tmp/class-demo > /tmp/class-demo.log 2>&1
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/build_player.js slides python-class-slides.html
node ../tools/export.js slides python-class-slides.pdf
```

셀 출력은 `tools/demo.sh`가 hello-uv(Python 3.14.6)를 만들고 `tools/run_nb.py`로 그 커널에서 실제로 실행한 결과예요. 파트마다 새 커널에서 위에서부터 차례로 실행해서, 셀 번호가 파트마다 [1]부터 시작해요. 오류는 Traceback 마지막 줄만 옮겼어요. 28쪽의 `0x` 주소는 다시 실행하면 바뀌니, 출력을 다시 받으면 gen.py의 주소도 같이 바꿔요.

눌러 보기 장은 장 안의 `<script type="text/slide-js">`를 `build_player.js`가 실행해서 움직여요. 그래서 버튼은 배포용 HTML에서만 눌러지고, PDF에는 처음 화면이 들어가요. 눌러 보기에 나오는 출력도 `tools/run_nb.py`로 실제로 실행한 결과예요.

범위: `pass`와 클래스, `__init__`, `self`, 메서드를 처음 다뤄요. `__str__`, `__repr__`은 25, 클래스 변수와 상속은 26에서 다뤄요. `@property`, `classmethod`, `staticmethod`, `_`로 숨기기, `dataclass`, 타입 힌트는 다루지 않아요. VS Code 디버거로 `self`가 생기는 과정을 따라가는 자료는 번외로 따로 만들 예정이에요.

</details>

---

<!-- curriculum:nav -->

[← 이전: 23 · 리스트 컴프리헨션](../23-python-comprehension) · [커리큘럼](../README.md) · [다음: 25 · 클래스 2 (`__str__`과 `__repr__`) →](../25-python-str-repr)

<!-- /curriculum:nav -->
