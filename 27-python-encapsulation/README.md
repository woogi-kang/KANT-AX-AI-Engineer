# 27 · 클래스 4 (캡슐화)

> 객체의 칸은 안에 감추고, 밖에서는 메서드라는 문으로만 꺼내고 바꾸게 하는 방법을 배워요. 밑줄 하나 `_`와 밑줄 두 개 `__`가 무엇이 다른지 보고, getter와 setter, `@property`로 값을 넣을 때 검사해요. 24~26의 도장 카드(`Card`)를 그대로 이어서 써요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/27-python-encapsulation/python-encapsulation-slides.html) | [26 · 클래스 3 (상속과 클래스 변수)](../26-python-inheritance) | [28 · 미니 프로젝트: 장바구니 (들여쓰기, items, 모듈)](../28-python-modules) |

<!-- /curriculum:top -->

## 학습 목표

이 챕터를 마치면 다음을 할 수 있어요.

- `self._stamps`처럼 밑줄 하나로 "안에서만 쓰는 칸"이라는 약속을 표시해요.
- `self.__password`가 `_Secret__password`로 이름이 바뀌어 저장된다는 걸 `__dict__`로 확인해요.
- `mypass._Secret__password`로 우회할 수 있으니, 밑줄은 자물쇠가 아니라 실수를 막는 표시라고 말해요.
- `get_password()`, `set_password(new)`로 꺼내고, 넣을 때 값을 검사해요.
- `@property`와 `@password.setter`로 괄호 없이 칸처럼 꺼내고 넣어요.
- `__` 칸을 자식 틀에서 못 찾는 오류, property에 괄호를 붙인 오류를 읽고 고쳐요.

## 시작하기 전에

| 할 일 | 챕터 |
| --- | :---: |
| `class`, `__init__`, `self`, 메서드 | 24 |
| `__str__`, 메서드로 상태 바꾸기와 `if`로 막기 | 25 |
| 상속, 클래스 변수 | 26 |
| 딕셔너리 `{키: 값}` | 15 |
| `if`, `else`, 범위 `1000 <= new <= 9999` | 17 |

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1–3 | 표지, 오늘의 순서, `basics.ipynb` 다시 열기 |
| 1. 왜 필요한가 | 4–5 | 도장 수를 밖에서 100, -5로 바꾸기(왜 필요한가), 칸은 안에 두고 메서드라는 문으로 드나드는 그림(큰 그림) |
| 2. 밑줄 하나 `_` | 6–8 | `_stamps`와 `count()`, "직원만 들어와요" 표지판, 밖에서 넣어도 오류가 안 나요 |
| 3. 밑줄 두 개 `__` | 9–13 | 밖에서 `AttributeError`, 안의 메서드에서는 그대로, `__dict__`로 본 바뀐 이름, `_Secret__password`로 우회, 눌러 보기(어떤 이름으로 저장되고 찾힐까) |
| 4. getter와 setter | 14–18 | getter, 검사하는 setter, `@property`, `@password.setter`, 다섯 가지 비교표 |
| 5. 오류와 함정 | 19–22 | 밖에서 `__password = 0`, 자식 틀의 `__stamps`, property에 괄호, setter 없는 property |
| 6. 실습 | 23–26 | 열 개에서 멈추는 도장 카드 두 장, 키오스크 비밀번호 두 장 |
| 정리 | 27–28 | 막힐 때, 한 장 요약 |

## 핵심 개념

### 이름 세 가지

| 클래스 안에 적은 이름 | 실제로 저장된 이름 | 밖에서 `mypass.이름`으로 |
| --- | --- | --- |
| `self.password` | `password` | 읽고 바꿀 수 있어요 |
| `self._password` | `_password` | 읽고 바꿀 수 있어요. 밑줄은 손대지 말자는 약속이에요 |
| `self.__password` | `_Secret__password` | `mypass.__password`는 `AttributeError`, `mypass._Secret__password`는 돼요 |

밑줄 두 개는 파이썬이 앞에 `_클래스이름`을 붙여 이름을 바꿔 두는 거예요. 자물쇠가 아니라서 우회할 수 있어요. 우회하는 코드는 만들지 않아요.

### 문 만들기

| 모양 | 꺼내기 | 넣기 |
| --- | --- | --- |
| getter, setter | `mypass.get_password()` | `mypass.set_password(5678)` |
| `@property`, `@password.setter` | `mypass.password` | `mypass.password = 5678` |

두 방법 모두 넣을 때 setter 안에서 값을 검사해요. 검사 규칙이 바뀌면 setter 한 곳만 고쳐요.

## 실습

VS Code에서 `hello-uv` 폴더를 열고 `basics.ipynb`를 열어요. 아래 코드를 셀 하나에 한 덩어리씩 적고 `Shift+Enter`로 실행해요. 주석(`#` 뒤)은 실제 출력이에요.

### 1. 밑줄 하나 `_`

```python
class Card:
    def __init__(self, name):
        self.name = name
        self._stamps = 0

    def add(self):
        self._stamps = self._stamps + 1

    def count(self):
        return self._stamps

kim = Card("kim")
kim.add()
kim.add()
print(kim.count())
# 2
```

```python
kim._stamps = 100
print(kim.count())
# 100
```

### 2. 밑줄 두 개 `__`와 우회

```python
class Secret:
    def __init__(self):
        self.__password = 1234

    def check(self, pw):
        return self.__password == pw

mypass = Secret()
print(mypass.check(1234))
print(mypass.check(1111))
# True
# False
```

```python
print(mypass.__password)
# AttributeError: 'Secret' object has no attribute '__password'
```

```python
print(mypass.__dict__)
print(mypass._Secret__password)
# {'_Secret__password': 1234}
# 1234
```

### 3. getter와 setter

```python
class Secret:
    def __init__(self):
        self.__password = 1234

    def get_password(self):
        return self.__password

    def set_password(self, new):
        if 1000 <= new <= 9999:
            self.__password = new
        else:
            print("비밀번호는 네 자리 숫자예요")

mypass = Secret()
mypass.set_password(12)
print(mypass.get_password())
mypass.set_password(5678)
print(mypass.get_password())
# 비밀번호는 네 자리 숫자예요
# 1234
# 5678
```

### 4. `@property`와 `@password.setter`

```python
class Secret:
    def __init__(self):
        self.__password = 1234

    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self, new):
        if 1000 <= new <= 9999:
            self.__password = new
        else:
            print("비밀번호는 네 자리 숫자예요")

mypass = Secret()
mypass.password = 12
print(mypass.password)
mypass.password = 5678
print(mypass.password)
# 비밀번호는 네 자리 숫자예요
# 1234
# 5678
```

### 5. 실습: 열 개에서 멈추는 도장 카드

```python
class Card:
    goal = 10

    def __init__(self, name):
        self.name = name
        self.__stamps = 0

    def add(self):
        if self.__stamps < Card.goal:
            self.__stamps = self.__stamps + 1

    @property
    def stamps(self):
        return self.__stamps

    def __str__(self):
        return f"{self.name}: 도장 {self.__stamps}/{Card.goal}"

kim = Card("kim")
for i in range(12):
    kim.add()
print(kim)
print(kim.stamps)
# kim: 도장 10/10
# 10
```

### 6. 실습: 키오스크 비밀번호

```python
class Kiosk:
    def __init__(self, password):
        self.__password = password

    def login(self, pw):
        if pw == self.__password:
            print("관리자 화면을 열어요")
        else:
            print("비밀번호가 틀렸어요")

    def change(self, old, new):
        if old == self.__password:
            self.__password = new
            print("비밀번호를 바꿨어요")
        else:
            print("지금 비밀번호가 틀려서 못 바꿔요")

k = Kiosk(1234)
k.login(1111)
k.change(1111, 5678)
k.change(1234, 5678)
k.login(5678)
# 비밀번호가 틀렸어요
# 지금 비밀번호가 틀려서 못 바꿔요
# 비밀번호를 바꿨어요
# 관리자 화면을 열어요
```

다 했으면 `Ctrl+S`(Mac `Cmd+S`)로 저장해요.

## 명령어 요약

| 코드 | 하는 일 |
| --- | --- |
| `self._stamps = 0` | 안에서만 쓰는 칸이라는 약속. 밖에서 바꿔도 오류는 안 나요 |
| `self.__password = 1234` | `_Secret__password`로 이름이 바뀌어 저장돼요 |
| `mypass.__dict__` | 객체에 실제로 저장된 칸 이름과 값 보기 (확인용) |
| `mypass._Secret__password` | 바뀐 이름으로 우회해서 읽기. 수업에서는 확인용으로만 |
| `def get_password(self):` | 꺼내는 문 (getter) |
| `def set_password(self, new):` | 검사하고 넣는 문 (setter) |
| `@property` | 메서드를 괄호 없이 칸처럼 꺼내요 |
| `@password.setter` | `mypass.password = 값`으로 넣을 때 검사해요 |

## 문제 해결

| 메시지 | 원인 | 해결 |
| --- | --- | --- |
| `AttributeError: 'Secret' object has no attribute '__password'` | `__` 칸을 밖에서 그 이름으로 찾았어요 | 클래스에 getter나 `@property`를 만들어 꺼내요 |
| `AttributeError: 'VipCard' object has no attribute '_VipCard__stamps'` | 자식 틀에서 부모의 `__stamps`를 썼어요. 자식 안에서는 `_VipCard__stamps`로 바뀌어요 | 부모와 자식이 같이 쓰는 칸은 `self._stamps`로 둬요 |
| `TypeError: 'int' object is not callable` | property에 괄호를 붙였어요 (`kim.stamps()`) | 괄호를 빼요 (`kim.stamps`) |
| `AttributeError: property 'stamps' of 'Card' object has no setter` | setter 없는 property에 `=`로 넣었어요 | 바꿔야 하면 `@stamps.setter`나 `add()` 같은 메서드를 만들어요 |
| 밖에서 `mypass.__password = 0`을 했는데 비밀번호가 그대로예요 | 클래스 밖에서는 이름이 안 바뀌어서 새 칸 `__password`가 하나 더 생겼어요 | `print(mypass.__dict__)`로 칸 이름을 확인하고 setter로 바꿔요 |
| `_stamps`를 밖에서 바꿨는데 오류가 안 나요 | 밑줄 하나는 약속일 뿐이에요 | 밖에서는 메서드로만 바꿔요 |

헷갈리면 `print(객체.__dict__)`로 실제 저장된 이름을 들여다봐요.

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분 (gen.py가 만들어요)
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py           모든 장과 deck.json 생성 (노트북 셀, 객체 칸 그림, 이름 바뀜)
  demo.sh          hello-uv를 새로 만들고 노트북 셀을 실제로 실행해 출력 확인
  run_nb.py        셀을 프로젝트 커널로 실행 (demo.sh가 불러요)
  lab_name.js      13쪽 이름 바꾸기 눌러 보기의 버튼 동작 (gen.py가 그 장에 넣어요)
python-encapsulation-slides.html  배포용 HTML
python-encapsulation-slides.pdf   강사용 PDF
```

검사, HTML, PDF를 만드는 공용 도구는 맨 위 [tools/](../tools)에 한 벌만 있어요. 명령은 이 폴더에서 쳐요.

```bash
bash tools/demo.sh /tmp/encapsulation-demo > /tmp/encapsulation-demo.log 2>&1
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/build_player.js slides python-encapsulation-slides.html
node ../tools/export.js slides python-encapsulation-slides.pdf
```

셀 출력은 `tools/demo.sh`가 hello-uv(Python 3.14.6)를 만들고 `tools/run_nb.py`로 그 커널에서 실제로 실행한 결과예요. 파트마다 새 커널에서 차례로 실행해서 셀 번호가 파트마다 [1]부터 시작해요. 오류는 Traceback 마지막 줄만 옮겼어요.

장마다 강조는 `tools/HIGHLIGHT.md`에서 골랐어요. 표지는 제목이 크게 들어오고 코드 칸에 빛이 지나가요. 목차, 들어가기, 27, 28쪽 목록은 차례로 나와요(시차). 4쪽 도장 수 칸은 값이 1, 100, -5로 바뀌어요. 5쪽 화살표는 왼쪽부터 그려지고 문이 두 번 두드려지며, 아래 목록은 지난 항목이 흐려져요. 6, 14, 23쪽 코드는 줄 스포트라이트로 비춰요. 8쪽 출력은 펜 동그라미, 9, 21쪽 오류는 상자로 두르고 9쪽은 한 번 흔들려요. 10쪽은 부른 줄과 출력을 선으로 이어요. 11, 16, 20쪽은 이름이 그 자리에서 바뀌어요(코드 모핑). 13쪽은 커서가 누를 곳을 짚어요. 15, 26쪽은 실행 막대가 줄을 따라 내려가요. 18쪽 표와 25쪽 코드는 스포트라이트로 한 덩어리씩 비춰요. 19쪽은 코드와 저장된 칸을 같은 색으로 짝지어요. 24쪽 도장 수는 숫자가 올라가요.

눌러 보기 장은 장 안의 `<script type="text/slide-js">`를 `build_player.js`가 실행해서 움직여요. 그래서 버튼은 배포용 HTML에서만 눌러지고, PDF에는 처음 화면이 들어가요. 눌러 보기에 나오는 출력도 `tools/run_nb.py`로 실제로 실행한 결과예요.

범위: `_` 약속, `__` 이름 바꾸기와 `_Secret__password` 우회, `__dict__`로 들여다보기, getter와 setter, `@property`, `@password.setter`를 처음 다뤄요. 데코레이터가 동작하는 원리, `deleter`, `property()` 함수 모양, `__slots__`, `classmethod`, `staticmethod`, `dataclass`는 다루지 않아요.

</details>

---

<!-- curriculum:nav -->

[← 이전: 26 · 클래스 3 (상속과 클래스 변수)](../26-python-inheritance) · [커리큘럼](../README.md) · [다음: 28 · 미니 프로젝트: 장바구니 (들여쓰기, items, 모듈) →](../28-python-modules)

<!-- /curriculum:nav -->
