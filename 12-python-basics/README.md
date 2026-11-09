# 12 · 파이썬 기초 1 (변수, 타입, 연산)

> 10에서 노트북을 손에 익혔으니 이번에는 파이썬 코드를 직접 적어요. 값에 이름을 붙이는 변수 할당, 값의 종류인 변수 타입과 타입 바꾸기, 숫자를 계산하는 사칙연산, True와 False로 답하는 비교와 논리연산(`and`, `or`, `not`)을 차례로 봐요. 마지막에는 카페 주문 계산을 이 네 가지로 풀어요. 문자열과 리스트는 [13 · 파이썬 기초 2](../13-python-strings-lists)에서 이어서 봐요. 모든 예제는 Jupyter 노트북 셀에 적고 실행해요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/12-python-basics/python-basics-slides.html) | [11 · 터미널에서 GitHub 다루기 (gh)](../11-gh-cli) | [13 · 파이썬 기초 2 (문자열, 리스트, for)](../13-python-strings-lists) |

<!-- /curriculum:top -->

## 학습 목표

이 챕터를 마치면 다음을 할 수 있어요.

- `=`가 오른쪽 값을 왼쪽 이름에 넣는 명령이라는 것을 알고, 같은 이름에 다시 넣으면 값이 바뀌는 것을 확인해요.
- 셀 마지막 줄의 이름, `print(값)`, `print("설명", 값)`으로 값을 봐요.
- 값의 타입(`int`, `float`, `str`, `bool`)을 `type()`으로 확인하고, `int()`, `float()`, `str()`로 바꿔요.
- `+` `-` `*` `/`와 `//` `%` `**`로 계산하고, 계산 순서를 괄호로 정해요.
- `+=`로 지금 값에 더해서 다시 넣어요.
- `==` `!=` `>` `<` `>=` `<=`로 비교하고, 결과가 `True` 또는 `False`라는 것을 알아요.
- `and`, `or`, `not`으로 조건을 이어서 True, False를 구해요.
- `NameError`, `TypeError`, `ValueError`, `ZeroDivisionError`의 마지막 줄을 읽고 고쳐요.

## 시작하기 전에

09에서 만든 `hello-uv`와 10에서 배운 내용을 그대로 써요. 11(gh)은 파이썬과 따로 보는 챕터라 이 챕터를 먼저 봐도 돼요.

| 할 일 | 슬라이드 |
| --- | :---: |
| VS Code에 Python, Jupyter 확장 설치, `uv add --dev ipykernel`, 커널로 `.venv` 고르기 | 09 · 25–27쪽 |
| 변수 이름 규칙과 스네이크 표기법(`user_name`) | 10 · 19–21쪽 |
| 자료형 다섯 가지와 `type()` | 10 · 22–23쪽 |

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1–5 | 표지, 오늘의 순서, 숫자만 적은 카페 계산이 불편한 이유, 큰 그림(변수, 타입, 계산, 비교), 새 노트북 `basics.ipynb` 만들기 |
| 1. 변수에 값 넣기 | 6–11 | `=`로 넣기, 값 보는 두 가지 방법, 다시 넣기, `age = age + 1`, 마지막 줄만 보이는 이유, `NameError` |
| 2. 변수 타입 | 12–16 | `int` `float` `str` `bool`과 `type()`, 타입은 값을 따라간다, `25`와 `"25"`, `int()` `float()` `str()`로 바꾸기, `ValueError` |
| 3. 사칙연산 | 17–27 | `+` `-` `*` `/`, `/`의 결과는 실수, 몫 `//`·나머지 `%`·거듭제곱 `**`, 계산 순서 네 계단, `**`가 먼저(`-2 ** 2`), 같은 순위는 왼쪽부터, 섞인 식 한 계단씩 풀기, 괄호 있고 없고 비교 예제 여덟 쌍, 직접 풀어 보기 네 문제, `+=`, 글자의 `+`와 `*` |
| 4. 비교와 논리연산 | 28–35 | 비교 연산자 여섯 가지, `=`와 `==`, 비교 결과를 변수에, `and` `or` `not` 표, 놀이기구 조건(`and`), 푸는 순서 |
| 5. 카페 주문으로 풀어 보기 | 36–38 | 가격 변수로 합계와 잔돈(가격이 오르면 한 줄만 고치기), 글자로 온 수량을 `int()`로 바꿔 나눠 내기(`//`, `%`), 사이즈 업과 할인 조건(`and`, `or`, `not`) |
| 정리 | 39–40 | 막힐 때, 한 장 요약 |

## 핵심 개념

### 변수 할당

| 코드 | 뜻 |
| --- | --- |
| `age = 25` | 25를 `age`라는 이름에 넣어요. 오른쪽에서 왼쪽으로 읽어요 |
| `age = 26` | 다시 넣으면 예전 값 25는 사라지고 26만 남아요 |
| `age = age + 1` | 오른쪽을 먼저 계산해요. 지금 값 26을 읽고, 1을 더해 27을 만들고, `age`에 다시 넣어요 |

값을 보는 방법은 두 가지예요. 셀 마지막 줄에 이름만 적으면 그 값이 보여요. 마지막 줄 하나만 보여서, 여러 값을 보려면 줄마다 `print()`를 써요. `print("나이:", age)`처럼 쉼표로 설명을 붙이면 한 칸 띄워서 이어 보여 줘요.

파이썬은 대문자와 소문자를 다른 이름으로 봐요. `age`에 값을 넣고 `Age`를 쓰면 `NameError`가 나요.

### 변수 타입

타입은 값의 종류예요. 10에서 본 자료형과 같은 말이에요.

| 값 | 타입 | `type()` 출력 | 뜻 |
| --- | --- | --- | --- |
| `25` | 정수 | `<class 'int'>` | 소수점 없는 숫자 |
| `172.5` | 실수 | `<class 'float'>` | 소수점 있는 숫자 |
| `"kim"` | 문자열 | `<class 'str'>` | 따옴표로 감싼 글자 |
| `False` | 불리언 | `<class 'bool'>` | `True` 또는 `False` |

타입은 이름이 아니라 넣은 값을 따라가요. `x = 10`이면 `int`, 다시 `x = "ten"`을 넣으면 `str`이에요. `25`와 `"25"`도 달라요. `25 + 1`은 26, `"25" + "1"`은 `251`이에요.

| 바꾸기 | 결과 | 설명 |
| --- | --- | --- |
| `int("3")` | `3` | 글자를 정수로 |
| `str(3)` | `'3'` | 숫자를 글자로 |
| `float("3.5")` | `3.5` | 글자를 실수로 |
| `int(3.9)` | `3` | 소수점 아래를 버려요 |

`int("삼")`, `int("3.5")`처럼 정수로 못 읽는 글자는 `ValueError`가 나요. 소수점 글자는 `float()`로 바꿔요.

### 사칙연산과 몫, 나머지, 거듭제곱

| 기호 | 뜻 | 예 | 결과 |
| --- | --- | --- | --- |
| `+` | 더하기 | `7 + 3` | `10` |
| `-` | 빼기 | `7 - 3` | `4` |
| `*` | 곱하기 | `7 * 3` | `21` |
| `/` | 나누기 (결과는 항상 실수) | `7 / 3`, `6 / 2` | `2.3333333333333335`, `3.0` |
| `//` | 몫 | `7 // 3` | `2` |
| `%` | 나머지 | `7 % 3` | `1` |
| `**` | 거듭제곱 | `2 ** 3` | `8` |

### 계산 순서

| 계단 | 연산 | 예 | 결과 |
| :---: | --- | --- | --- |
| 1 | `( )` 괄호 | `(2 + 3) * 4` | `20` |
| 2 | `**` 거듭제곱 | `2 ** 3 // 3`, `-2 ** 2` | `2`, `-4` |
| 3 | `*` `/` `//` `%` (넷은 같은 순위) | `2 + 3 * 4` | `14` |
| 4 | `+` `-` | `10 - 4 + 2` | `8` |

위 계단부터 풀고, 같은 계단끼리는 왼쪽부터 풀어요. `8 / 2 * 4`는 `4.0 * 4`라서 `16.0`, `7 // 2 * 2`는 `3 * 2`라서 `6`이에요. `-2 ** 2`는 `**`가 빼기 기호보다 먼저라서 `-4`예요. 음수를 거듭제곱할 땐 `(-2) ** 2`처럼 괄호로 묶어요.

`10 - 2 * 3 ** 2 // 4`는 한 계단씩 풀어요.

1. `3 ** 2`를 먼저 해서 `10 - 2 * 9 // 4`
2. 같은 계단의 `*`와 `//`는 왼쪽부터. `10 - 18 // 4`, 그다음 `10 - 4`
3. 마지막 빼기로 `6`

괄호를 치면 답이 달라지는 예예요. 모두 셀에서 실행한 결과예요.

| 괄호 없이 | 결과 | 괄호를 치면 | 결과 |
| --- | --- | --- | --- |
| `10 + 2 * 3` | `16` | `(10 + 2) * 3` | `36` |
| `20 - 10 / 2` | `15.0` | `(20 - 10) / 2` | `5.0` |
| `12 / 3 * 2` | `8.0` | `12 / (3 * 2)` | `2.0` |
| `100 - 30 - 20` | `50` | `100 - (30 - 20)` | `90` |
| `2 ** 2 * 3` | `12` | `2 ** (2 * 3)` | `64` |
| `17 % 5 * 2` | `4` | `17 % (5 * 2)` | `7` |
| `3 + 10 // 3` | `6` | `(3 + 10) // 3` | `4` |
| `-3 ** 2` | `-9` | `(-3) ** 2` | `9` |

직접 풀어 볼 문제예요. 답은 `7 // 2 ** 2`는 `1`, `10 % 3 ** 2`는 `1`, `2 + 3 * 4 ** 2 // 8`은 `8`, `50 - 5 * 2 ** 3 % 7`은 `45`예요.

헷갈리면 먼저 할 계산을 괄호로 묶어요.

`score += 10`은 `score = score + 10`을 줄여 쓴 거예요. `-=`, `*=`, `/=`도 같은 모양이에요.

문자열에 `+`를 쓰면 이어 붙이고(`"kim" + "lee"`는 `'kimlee'`), `*`를 쓰면 반복해요(`"ha" * 3`은 `'hahaha'`). 따옴표로 감싼 `"3"`은 글자라서 `"3" + 3`은 `TypeError`가 나요. `int("3") + 3`처럼 타입을 맞추면 6이에요.

### 비교 연산자

`age = 25`일 때 결과예요. 결과는 2파트에서 본 불리언(`bool`)이에요.

| 기호 | 뜻 | 예 | 결과 |
| --- | --- | --- | --- |
| `>` | 크다 | `age > 20` | `True` |
| `<` | 작다 | `age < 20` | `False` |
| `==` | 같다 | `age == 25` | `True` |
| `!=` | 다르다 | `age != 25` | `False` |
| `>=` | 크거나 같다 | `age >= 25` | `True` |
| `<=` | 작거나 같다 | `age <= 24` | `False` |

`=` 하나는 넣기, `==` 두 개는 묻기예요. 비교하려다 `=` 하나만 쓰면 오류 없이 값이 바뀌어요.

### 논리연산자

| 왼쪽 | 오른쪽 | `and` | `or` |
| --- | --- | --- | --- |
| `True` | `True` | `True` | `True` |
| `True` | `False` | `False` | `True` |
| `False` | `True` | `False` | `True` |
| `False` | `False` | `False` | `False` |

`and`는 둘 다 True일 때만 True, `or`는 하나만 True여도 True예요. `not`은 값 하나 앞에 붙여서 뒤집어요. `not True`는 `False`예요.

여러 연산이 섞이면 계산, 비교, `not`, `and`, `or` 순서로 풀어요. `2 + 3 > 4 and not False`는 `5 > 4 and not False`, `True and True`를 거쳐 `True`가 돼요.

## 실습

VS Code에서 `hello-uv` 폴더를 열고 새 파일 `basics.ipynb`를 만들어요. 오른쪽 위 커널로 `.venv`를 고른 뒤, 아래 코드를 셀 하나에 한 덩어리씩 적고 `Shift+Enter`로 실행해요. 주석(`#` 뒤)은 실제 출력이에요.

### 1. 변수에 값 넣기

```python
age = 25
print(age)          # 25
print("나이:", age)  # 나이: 25
```

```python
age = 26
age = age + 1
age                 # 27
```

```python
user_name = "kim"
age
user_name           # 'kim' (age는 보이지 않아요)
```

`Age`만 적은 셀을 실행해 `NameError: name 'Age' is not defined`를 직접 봐요.

### 2. 변수 타입

```python
x = 10
print(type(x))      # <class 'int'>
x = "ten"
print(type(x))      # <class 'str'>
```

```python
print(int("3") + 3)    # 6
print(str(3) + "3")    # 33
print(float("3.5"))    # 3.5
print(int(3.9))        # 3
```

`int("삼")`만 적은 셀을 실행해 `ValueError: invalid literal for int() with base 10: '삼'`을 직접 봐요.

### 3. 사칙연산

```python
print(7 + 3)    # 10
print(7 - 3)    # 4
print(7 * 3)    # 21
print(7 / 3)    # 2.3333333333333335
print(6 / 2)    # 3.0
print(7 // 3)   # 2
print(7 % 3)    # 1
print(2 ** 3)   # 8
```

```python
print(2 ** 3 // 3)              # 2
print(-2 ** 2)                  # -4
print((-2) ** 2)                # 4
print(8 / 2 * 4)                # 16.0
print(10 - 2 * 3 ** 2 // 4)     # 6
print(10 + 2 * 3)               # 16
print((10 + 2) * 3)             # 36
print(17 % 5 * 2)               # 4
print(17 % (5 * 2))             # 7
```

```python
score = 0
score += 10
score += 5
score           # 15
```

### 4. 비교와 논리연산

```python
age = 25
is_adult = age >= 20
print(is_adult)         # True
print(type(is_adult))   # <class 'bool'>
```

```python
print(not True)    # False
print(not False)   # True
```

```python
height = 130
age = 9
height >= 120 and age >= 7    # True
```

### 5. 카페 주문으로 풀어 보기

위에서부터 한 셀씩 실행해요.

```python
americano = 4500
latte = 5000
total = americano * 2 + latte
paid = 20000
print("합계:", total)          # 합계: 14000
print("잔돈:", paid - total)   # 잔돈: 6000
```

```python
americano = 4800
total = americano * 2 + latte
print("합계:", total)          # 합계: 14600
print("잔돈:", paid - total)   # 잔돈: 5400
```

```python
qty = "3"
total = 4500 * int(qty) + 5000
people = 3
print("합계:", total)                # 합계: 18500
print("한 사람:", total // people)   # 한 사람: 6166
print("남는 돈:", total % people)    # 남는 돈: 2
```

`int(qty)` 없이 `print(5000 + qty)`를 실행해 `TypeError: unsupported operand type(s) for +: 'int' and 'str'`를 직접 봐요.

```python
is_member = False
has_coupon = True
total = 18500
size_up = total >= 15000 and has_coupon
discount = is_member or total >= 50000
print("사이즈 업:", size_up)       # 사이즈 업: True
print("할인:", discount)           # 할인: False
print("비회원:", not is_member)    # 비회원: True
```

다 했으면 `Ctrl+S`(Mac `Cmd+S`)로 저장해요.

## 문제 해결

| 증상 | 원인과 해결 |
| --- | --- |
| `NameError: name 'Age' is not defined` | 대소문자나 철자가 달라요. 넣는 셀을 안 돌렸으면 Run All |
| `NameError: name 'true' is not defined` | `True`, `False`는 첫 글자가 대문자예요 |
| `TypeError: can only concatenate str (not "int") to str` | 따옴표 글자와 숫자를 더했어요. `int("3") + 3`처럼 타입을 맞춰요 |
| `ValueError: invalid literal for int() with base 10: '삼'` | `int()`가 숫자로 못 읽는 글자예요. 소수점 글자는 `float()` |
| `ZeroDivisionError: division by zero` | 0으로 나눴어요. 나누는 수를 확인해요 |
| 비교했는데 값이 바뀌었어요 | `=`를 하나만 썼어요. 비교는 `==` |
| `6 / 2`가 `3.0`으로 나와요 | `/`의 결과는 항상 실수예요. 몫만 필요하면 `//` |
| 셀에 적은 값 중 하나만 보여요 | 이름만 적으면 마지막 줄만 보여요. 줄마다 `print()` |

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분 (gen.py가 만들어요)
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py           모든 장과 deck.json 생성 (노트북 셀, 줄 옆 라벨, 변수 상자, 계산 계단, True·False 표, 강조)
  demo.sh          hello-uv를 새로 만들고 노트북 셀을 실제로 실행해 출력 확인
  run_nb.py        셀을 프로젝트 커널로 실행 (demo.sh가 불러요)
python-basics-slides.html  배포용 HTML
python-basics-slides.pdf   강사용 PDF
```

검사, HTML, PDF를 만드는 공용 도구(`check.js`, `build_player.js`, `export.js`)는 맨 위 [tools/](../tools)에 한 벌만 있어요. 명령은 이 폴더에서 쳐요.

슬라이드 HTML을 직접 고치지 말고 스크립트를 고친 뒤 다시 만들어요. 장 배치는 Stageshow 원칙(장마다 주인공 하나, 카드 대신 코드 줄 옆 라벨, 테두리 없는 표)을, 강조는 `tools/HIGHLIGHT.md`를 따랐어요.

```bash
bash tools/demo.sh /tmp/basics-demo > /tmp/basics-demo.log 2>&1
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/build_player.js slides python-basics-slides.html
node ../tools/export.js slides python-basics-slides.pdf
```

셀 출력은 `tools/demo.sh`가 uv 0.11.32로 hello-uv를 만들고 `tools/run_nb.py`로 그 커널에서 실제로 실행한 결과예요. 파트마다 새 커널에서 위에서부터 차례로 실행해서, 슬라이드의 셀 번호가 파트마다 [1]부터 시작해요. 오류는 Traceback 위쪽 줄을 빼고 마지막 줄만 옮겼어요. demo.sh 환경의 커널은 Python 3.13이었고, 이 챕터의 출력과 메시지는 3.14와 같아요. f-string은 13에서 처음 배워서 이 챕터 예제에는 쓰지 않았어요. `input()`과 `if`는 아직 배우지 않아서 쓰지 않았어요.

</details>

---

<!-- curriculum:nav -->

[← 이전: 11 · 터미널에서 GitHub 다루기 (gh)](../11-gh-cli) · [커리큘럼](../README.md) · [다음: 13 · 파이썬 기초 2 (문자열, 리스트, for) →](../13-python-strings-lists)

<!-- /curriculum:nav -->
