# 12 · 파이썬 기초 (변수, 타입, 연산, 문자열, 리스트)

> 10에서 노트북을 손에 익혔으니 이번에는 파이썬 코드를 직접 적어요. 값에 이름을 붙이는 변수 할당, 값의 종류인 변수 타입과 타입 바꾸기, 숫자를 계산하는 사칙연산, True와 False로 답하는 비교와 논리연산(`and`, `or`, `not`)을 차례로 봐요. 그다음 문자열을 자르고, 변수 값을 문장 안에 끼워 넣어 보기 좋게 출력해요. 마지막에는 주문 데이터를 리스트와 튜플에 담아 영수증 모양으로 찍어요. 모든 예제는 Jupyter 노트북 셀에 적고 실행해요.

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/12-python-basics/python-basics-slides.html) | [11 · 터미널에서 GitHub 다루기 (gh)](../11-gh-cli) | 준비 중 |

## 학습 목표

이 챕터를 마치면 다음을 할 수 있어요.

- `=`가 오른쪽 값을 왼쪽 이름에 넣는 명령이라는 것을 알고, 같은 이름에 다시 넣으면 값이 바뀌는 것을 확인해요.
- 셀 마지막 줄의 이름, `print(값)`, `print("설명", 값)`으로 값을 봐요.
- 값의 타입(`int`, `float`, `str`, `bool`)을 `type()`으로 확인하고, `int()`, `float()`, `str()`로 바꿔요.
- `+` `-` `*` `/`와 `//` `%` `**`로 계산하고, 계산 순서를 괄호로 정해요.
- `+=`로 지금 값에 더해서 다시 넣어요.
- `==` `!=` `>` `<` `>=` `<=`로 비교하고, 결과가 `True` 또는 `False`라는 것을 알아요.
- `and`, `or`, `not`으로 조건을 이어서 True, False를 구해요.
- 문자열에서 `word[0]`, `word[0:2]`로 글자를 꺼내고, `print()`의 `sep`, `end`와 `\n`, `\t`를 써요.
- 변수 값을 문자열에 끼워 넣는 세 방식(`%`, `format()`, f-string)을 읽고, 새 코드는 f-string으로 적어요.
- 칸 수(`{42:5d}`), 소수점 자리(`{pi:.2f}`), 천 단위 콤마(`{price:,}`)를 정해 출력해요.
- 값 여러 개를 리스트 `[ ]`와 튜플 `( )`에 담고, `orders[1][0]`처럼 번호 두 개로 꺼내요.
- 리스트 메서드 `append` `insert` `remove` `pop` `count` `index` `sort`와 튜플 메서드 `count` `index`를 써요.
- `menu, price, qty = orders[2]`로 튜플 값을 변수 여러 개에 한 번에 꺼내 담아요.
- `"=" * 33`, 머리글 맞춤, 콤마로 영수증 모양 출력을 만들어요.
- `for menu, price, qty in orders:`로 주문을 하나씩 꺼내 되풀이하고, 합계를 쌓아요.
- `NameError`, `TypeError`, `ValueError`, `IndexError`, `ZeroDivisionError`의 마지막 줄을 읽고 고쳐요.

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
| 들어가기 | 1–3 | 표지, 오늘의 순서, 10에서 이어서 새 노트북 `basics.ipynb` 만들기 |
| 1. 변수에 값 넣기 | 4–9 | `=`로 넣기, 값 보는 두 가지 방법, 다시 넣기, `age = age + 1`, 마지막 줄만 보이는 이유, `NameError` |
| 2. 변수 타입 | 10–14 | `int` `float` `str` `bool`과 `type()`, 타입은 값을 따라간다, `25`와 `"25"`, `int()` `float()` `str()`로 바꾸기, `ValueError` |
| 3. 사칙연산 | 15–28 | `+` `-` `*` `/`, `/`의 결과는 실수, 몫 `//`·나머지 `%`·거듭제곱 `**`, 계산 순서 네 계단, `**`가 먼저(`-2 ** 2`), 같은 순위는 왼쪽부터, 섞인 식 한 계단씩 풀기, 괄호 있고 없고 비교 예제 여덟 쌍, 직접 풀어 보기 네 문제, 변수로 계산, `+=`, 글자의 `+`와 `*` |
| 4. 비교와 논리연산 | 29–37 | 비교 연산자 여섯 가지, `=`와 `==`, 비교 결과를 변수에, `and` `or` `not` 표, 놀이기구 조건(`and`), 할인 조건(`or`), 푸는 순서 |
| 5. 문자열과 출력 | 38–52 | 따옴표와 `len()`, 인덱스와 `IndexError`, 슬라이싱, `print()`의 `sep` `end`, `\n` `\t`, 끼워 넣는 세 방식, `%s` `%d`와 f-string, `format()`의 `{0}` `{1}` `{2}`, 같은 주문내역을 세 방식으로, 칸 수 `%5d` `{42:5d}`, 소수점 `%0.2f` `{pi:.2f}`, 천 단위 콤마 `{price:,}`, `format()`의 모양, 표처럼 맞추기, 포맷팅 오류 |
| 6. 리스트와 튜플 | 53–72 | `[ ]`로 담기와 `len()`, 꺼내기와 자르기, 값 바꾸기와 `append`, `sum` `max` `min`, 넣고 빼는 메서드(`append` `insert` `remove` `pop`), 찾고 세고 정렬하는 메서드(`count` `index` `in` `sort`), 메서드와 함수 한눈에, 바꿀 수 없는 튜플, 튜플의 `count` `index`와 꺼내 담기, `a, b = b, a`, `list()` `tuple()`, 주문 데이터 `orders`, 번호 두 개로 꺼내기, 한 번에 꺼내 담기, 주문 줄 맞추기, 한글 머리글이 두 칸인 이유, 메뉴표 영수증, `for`로 하나씩 꺼내 되풀이하기, `for`로 합계 쌓기, 가게 이름과 날짜가 들어간 영수증 한 장, 콜론과 들여쓰기 오류, 여러 모양의 리스트, `IndexError` |
| 정리 | 73–74 | 막힐 때, 한 장 요약 |

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

### 문자열 꺼내기와 print

`word = "python"`일 때 결과예요. 번호(인덱스)는 0부터 세요.

| 코드 | 결과 | 뜻 |
| --- | --- | --- |
| `word[0]` | `'p'` | 첫 글자 |
| `word[-1]` | `'n'` | 뒤에서 첫 글자 |
| `word[0:2]` | `'py'` | 0번부터 2번 앞까지 |
| `word[2:]` | `'thon'` | 2번부터 끝까지 |
| `word[6]` | `IndexError` | 0~5번까지만 있어요 |

`print("kim", "lee", sep="-")`는 `kim-lee`, `print("hello", end=" ")`는 줄을 바꾸지 않고 한 칸 띄워요. 따옴표 안의 `\n`은 줄바꿈, `\t`는 탭이에요.

### 값을 끼워 넣는 세 방식

| 방식 | 예 | 언제 |
| --- | --- | --- |
| `%` 포맷팅 | `"%s 님은 %d살" % (name, age)` | 가장 옛 방식. 옛 코드와 책에서 봐요 |
| `format()` | `"{0} 님은 {1}살".format(name, age)` | 파이썬 3.0부터. 번호로 값을 골라요 |
| f-string | `f"{name} 님은 {age}살"` | 파이썬 3.6부터. 요즘 표준이라 새 코드는 이걸로 써요 |

`format()`은 중괄호 번호로 값을 골라요. 번호는 0부터 세요. `"주문내역은 : {0}, {1}, {2}".format(cake, price, qty)`에서 `{0}`은 cake, `{1}`은 price, `{2}`는 qty예요. 번호를 바꾸면 순서를 바꿀 수 있고, `{0}`을 여러 번 써도 돼요.

콜론 뒤에 모양을 적어요. `format()`은 콜론 앞에 번호를, f-string은 이름을 적고, 콜론 뒤는 같아요.

| `%` | f-string | 결과 | 뜻 |
| --- | --- | --- | --- |
| `"[%5d]" % 42` | `f"[{42:5d}]"` | `[   42]` | 다섯 칸 확보, 오른쪽 맞춤 |
| `"[%-5d]" % 42` | `f"[{42:<5d}]"` | `[42   ]` | 왼쪽 맞춤 |
| `"[%05d]" % 42` | `f"[{42:05d}]"` | `[00042]` | 빈칸을 0으로 |
| `"%0.2f" % pi` | `f"{pi:.2f}"` | `3.14` | 소수점 두 자리 (`pi = 3.141592`) |
| 없음 | `f"{price:,}"` | `1,234,567` | 천 단위 콤마 (`price = 1234567`) |
| 없음 | `f"[{fee:8,}]"` | `[  35,000]` | 여덟 칸 확보와 콤마 (`fee = 35000`) |

f-string에서 글자는 기본이 왼쪽 맞춤이에요. `f"[{'kim':5}]"`는 `[kim  ]`이고, 오른쪽으로 보내려면 `{'kim':>5}`처럼 `>`를 붙여요. `%` 방식에는 콤마 옵션이 없어서 `"%,d" % price`는 `ValueError`가 나요.

### 리스트와 튜플

| 코드 | 결과 | 뜻 |
| --- | --- | --- |
| `prices = [4500, 5000, 6500]` | | 대괄호에 값 여러 개를 담은 리스트 |
| `len(prices)` | `3` | 담긴 개수 |
| `prices[0] = 4800` | | 0번 값을 바꿔요 |
| `prices.append(3000)` | | 맨 뒤에 하나 더해요 |
| `sum(prices)`, `max(prices)`, `min(prices)` | `19300`, `6500`, `3000` | 합계, 가장 큰 값, 가장 작은 값 |
| `order = ("coffee", 4500, 2)` | | 소괄호로 묶은 튜플. 만든 뒤 못 바꿔요 |

리스트 이름 뒤에 점을 찍고 쓰는 함수를 메서드라고 불러요. `cart = ["coffee", "latte"]`, `scores = [70, 95, 80, 95]`일 때 결과예요.

| 메서드 | 결과 | 뜻 |
| --- | --- | --- |
| `cart.append("cake")` | `['coffee', 'latte', 'cake']` | 맨 뒤에 더하기 |
| `cart.insert(0, "tea")` | `['tea', 'coffee', 'latte', 'cake']` | 그 자리에 끼우기 |
| `cart.remove("latte")` | `['tea', 'coffee', 'cake']` | 값을 찾아 지우기. 없으면 `ValueError` |
| `cart.pop()` | `'cake'`를 돌려주고 `['tea', 'coffee']` | 맨 뒤를 꺼내기 |
| `scores.count(95)` | `2` | 몇 개인지 |
| `scores.index(80)` | `2` | 몇 번 자리인지 |
| `95 in scores` | `True` | 들어 있는지 |
| `scores.sort()` | `[70, 80, 95, 95]` | 작은 수부터. `reverse=True`면 큰 수부터 |

튜플은 바꾸는 메서드가 없고 `count`, `index`만 있어요. `year, month, day = (2026, 11, 2)`처럼 한 번에 꺼내 담고, `a, b = b, a`로 두 값을 맞바꿔요. 고쳐야 하면 `list(튜플)`로 바꿔서 고쳐요.

주문 여러 건은 튜플을 리스트에 담아요. `orders = [("coffee", 4500, 2), ("latte", 5000, 1), ("cake", 6500, 3)]`에서 앞 번호는 몇째 주문, 뒤 번호는 그 안의 몇째 값이에요. `orders[1][0]`은 `'latte'`, `orders[2][1] * orders[2][2]`는 `19500`이에요. `menu, price, qty = orders[2]`처럼 쓰면 튜플 값이 순서대로 하나씩 들어가요.

글자도 `<` `>` `^`로 맞춰요. 파이썬은 한글 한 글자를 한 칸으로 세지만 화면에서는 두 칸 너비라서, 한글 머리글은 한글 글자 수만큼 칸 수를 빼요. 10칸짜리 `'메뉴명'`은 `{'메뉴명':<7}`이에요. 글꼴에 따라 조금 어긋나면 머리글을 영어로 써요.

`for 이름 in 리스트:`는 리스트에서 값을 하나씩 꺼내 이름에 넣고, 아래 네 칸 들여 쓴 줄을 되풀이해요. `for menu, price, qty in orders:`처럼 이름 세 개를 적으면 주문 튜플 하나가 세 이름에 나눠 들어가요. 합계는 for 앞에서 `total = 0`으로 시작하고, 안쪽에서 `total += price * qty`로 쌓아요. 줄 끝 콜론을 빠뜨리면 `SyntaxError`, 들여 쓰지 않으면 `IndentationError`가 나요.

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
total = 10000
people = 3
print("한 사람:", total // people)  # 한 사람: 3333
print("남는 돈:", total % people)   # 남는 돈: 1
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
height = 130
age = 9
height >= 120 and age >= 7    # True
```

```python
is_member = False
total = 60000
is_member or total >= 50000   # True
```

```python
not is_member                 # True
```

### 5. 문자열과 출력

```python
word = "python"
print(word[0])      # p
print(word[-1])     # n
print(word[0:2])    # py
print(word[2:])     # thon
```

```python
print("kim", "lee", sep="-")    # kim-lee
print("hello", end=" ")
print("world")                  # hello world
print("첫째 줄\n둘째 줄")
# 첫째 줄
# 둘째 줄
```

```python
cake = "치즈케이크"
price = 5000
qty = 2
print("주문내역은 : %s, %d, %d" % (cake, price, qty))          # 주문내역은 : 치즈케이크, 5000, 2
print("주문내역은 : {0}, {1}, {2}".format(cake, price, qty))   # 주문내역은 : 치즈케이크, 5000, 2
print(f"주문내역은 : {cake}, {price}, {qty}")                  # 주문내역은 : 치즈케이크, 5000, 2
print(f"{cake} {qty}개, 합계 {price * qty:,}원")               # 치즈케이크 2개, 합계 10,000원
```

```python
pi = 3.141592
print("%0.2f" % pi)       # 3.14
print(f"{pi:.2f}")        # 3.14
print("[%5d]" % 42)       # [   42]
print(f"[{42:5d}]")       # [   42]
```

```python
price = 1234567
print(f"{price:,}원")     # 1,234,567원
fee = 35000
print(f"[{fee:8,}]")      # [  35,000]
```

### 6. 리스트와 튜플

```python
cart = ["coffee", "latte"]
cart.append("cake")
cart.insert(0, "tea")
print(cart)          # ['tea', 'coffee', 'latte', 'cake']
cart.remove("latte")
last = cart.pop()
print(last, cart)    # cake ['tea', 'coffee']
```

```python
scores = [70, 95, 80, 95]
print(scores.count(95))   # 2
print(scores.index(80))   # 2
scores.sort(reverse=True)
print(scores)             # [95, 95, 80, 70]
```

```python
orders = [("coffee", 4500, 2), ("latte", 5000, 1), ("cake", 6500, 3)]
print(len(orders))                    # 3
print(orders[1][0])                   # latte
menu, price, qty = orders[2]
print(f"{menu} {qty}개, {price * qty:,}원")   # cake 3개, 19,500원
```

```python
total = orders[0][1] * orders[0][2]
total += orders[1][1] * orders[1][2]
total += orders[2][1] * orders[2][2]
print("=" * 33)
print(f"{'메뉴명':<7}{'단가':>6}{'수량':>3}{'금액':>8}")
print("-" * 33)
print(f"{orders[0][0]:<10}{orders[0][1]:>8,}{orders[0][2]:>5}{orders[0][1] * orders[0][2]:>10,}")
print(f"{orders[1][0]:<10}{orders[1][1]:>8,}{orders[1][2]:>5}{orders[1][1] * orders[1][2]:>10,}")
print(f"{orders[2][0]:<10}{orders[2][1]:>8,}{orders[2][2]:>5}{orders[2][1] * orders[2][2]:>10,}")
print("-" * 33)
print(f"{'합계':<6}{total:>25,}")
print("=" * 33)
# =================================
# 메뉴명        단가 수량      금액
# ---------------------------------
# coffee       4,500    2     9,000
# latte        5,000    1     5,000
# cake         6,500    3    19,500
# ---------------------------------
# 합계                       33,500
# =================================
```

같은 주문을 for로 찍어 영수증 한 장을 완성해요. 주문 줄 세 줄이 for 두 줄로 줄어요.

```python
print("=" * 33)
print(f"{'KANT 카페':^31}")
print(f"{'2026-11-02  14:30':^33}")
print("=" * 33)
print(f"{'메뉴명':<7}{'단가':>6}{'수량':>3}{'금액':>8}")
print("-" * 33)
total = 0
count = 0
for menu, price, qty in orders:
    print(f"{menu:<10}{price:>8,}{qty:>5}{price * qty:>10,}")
    total += price * qty
    count += qty
print("-" * 33)
print(f"{'수량':<6}{count:>15}")
print(f"{'합계':<6}{total:>25,}")
print("=" * 33)
print(f"{'감사합니다':^28}")
# =================================
#             KANT 카페
#         2026-11-02  14:30
# =================================
# 메뉴명        단가 수량      금액
# ---------------------------------
# coffee       4,500    2     9,000
# latte        5,000    1     5,000
# cake         6,500    3    19,500
# ---------------------------------
# 수량                  6
# 합계                       33,500
# =================================
#            감사합니다
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
| `IndexError: string index out of range` | 없는 번호예요. 번호는 0부터 `len(값) - 1`까지예요 |
| `TypeError: not enough arguments for format string` | `%` 자리 수와 값 수가 달라요. f-string으로 쓰면 이름을 바로 적어서 덜 틀려요 |
| `ValueError: unsupported format character ','` | `%`에는 콤마 옵션이 없어요. `f"{price:,}"`로 써요 |
| `ValueError: list.remove(x): x not in list` | 리스트에 없는 값을 지우려 했어요. `값 in 리스트`로 먼저 확인해요 |
| `IndexError: list index out of range` | 리스트에 없는 번호예요. 값이 세 개면 마지막 번호는 2 |
| `TypeError: 'tuple' object does not support item assignment` | 튜플은 바꿀 수 없어요. 바꿀 값은 리스트에 담아요 |
| `SyntaxError: expected ':'` | `for` 줄 끝에 콜론을 빠뜨렸어요 |
| `IndentationError: expected an indented block after 'for' statement on line 1` | 되풀이할 줄을 네 칸 들여 써요 |
| 합계가 쌓이지 않아요 | `total = 0`을 for 안에 넣었어요. for 앞으로 옮겨요 |
| 한글 머리글만 칸이 밀려요 | 한글은 화면에서 두 칸이에요. 한글 글자 수만큼 칸 수를 빼거나 머리글을 영어로 |
| `ValueError: Unknown format code 'd' for object of type 'str'` | 글자에 `d`(정수 모양)를 줬어요. 값의 타입을 확인해요 |
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
  gen.py           모든 장과 deck.json 생성 (노트북 셀, 변수 상자, 타입 카드, True·False 표, % 와 f-string 나란히, 리스트 칸)
  demo.sh          hello-uv를 새로 만들고 노트북 셀을 실제로 실행해 출력 확인
  run_nb.py        셀을 프로젝트 커널로 실행 (demo.sh가 불러요)
python-basics-slides.html  배포용 HTML
python-basics-slides.pdf   강사용 PDF
```

검사, HTML, PDF를 만드는 공용 도구(`check.js`, `build_player.js`, `export.js`)는 맨 위 [tools/](../tools)에 한 벌만 있어요. 명령은 이 폴더에서 쳐요.

슬라이드 HTML을 직접 고치지 말고 스크립트를 고친 뒤 다시 만들어요.

```bash
bash tools/demo.sh /tmp/basics-demo > /tmp/basics-demo.log 2>&1
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/build_player.js slides python-basics-slides.html
node ../tools/export.js slides python-basics-slides.pdf
```

셀 출력은 `tools/demo.sh`가 uv 0.11.32로 hello-uv를 만들고 `tools/run_nb.py`로 그 커널에서 실제로 실행한 결과예요. 파트마다 새 커널에서 위에서부터 차례로 실행해서, 슬라이드의 셀 번호가 파트마다 [1]부터 시작해요. 오류는 Traceback 위쪽 줄을 빼고 마지막 줄만 옮겼어요. demo.sh 환경의 커널은 Python 3.13이었고, 이 챕터의 출력과 메시지는 3.14와 같아요. f-string은 5파트에서 처음 배워서 1~4파트 예제에는 쓰지 않았어요. `input()`은 아직 배우지 않아서 쓰지 않았어요. 6파트는 주문 줄을 먼저 한 줄씩 적어 보고, 그 뒤에 for로 같은 영수증을 다시 찍어요. `if`는 아직 쓰지 않았어요. 오류 메시지 뒤 괄호 안의 위치 표시는 빼고 옮겼어요. 영수증 출력의 한글은 슬라이드에서 영어 두 칸 너비로 그렸어요.

</details>

---

[← 이전: 11 · 터미널에서 GitHub 다루기 (gh)](../11-gh-cli) · [커리큘럼](../README.md)
