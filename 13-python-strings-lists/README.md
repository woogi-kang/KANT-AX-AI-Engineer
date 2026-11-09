# 13 · 파이썬 기초 2 (문자열, 리스트, for)

> 12에서 변수, 타입, 계산, 비교를 봤어요. 이번에는 문자열을 자르고, 변수 값을 문장 안에 끼워 넣어 보기 좋게 출력해요. 그다음 주문 데이터를 리스트와 튜플에 담아 영수증 모양으로 찍고, `for`로 되풀이를 줄여요. 모든 예제는 12에서 쓰던 노트북에 이어서 적고 실행해요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/13-python-strings-lists/python-strings-lists-slides.html) | [12 · 파이썬 기초 1 (변수, 타입, 연산)](../12-python-basics) | [14 · 파이썬 기초 3 (in, 2차원 리스트)](../14-python-2d-lists) |

<!-- /curriculum:top -->

## 학습 목표

이 챕터를 마치면 다음을 할 수 있어요.

- 문자열에서 `word[0]`, `word[0:2]`로 글자를 꺼내고, `print()`의 `sep`, `end`와 `\n`, `\t`를 써요.
- 변수 값을 문자열에 끼워 넣는 세 방식(`%`, `format()`, f-string)을 읽고, 새 코드는 f-string으로 적어요.
- 칸 수(`{42:5d}`), 소수점 자리(`{pi:.2f}`), 천 단위 콤마(`{price:,}`)를 정해 출력해요.
- 값 여러 개를 리스트 `[ ]`와 튜플 `( )`에 담고, `orders[1][0]`처럼 번호 두 개로 꺼내요.
- 리스트 메서드 `append` `insert` `remove` `pop` `count` `index` `sort` `extend` `reverse` `copy` `clear`와 튜플 메서드 `count` `index`를 써요.
- `[시작:끝:간격]`으로 자르고(`[::2]`, `[::-1]`), `table[1][2]`처럼 안쪽 값을 꺼내요.
- `split`으로 글자를 리스트로, `join`으로 리스트를 글자로 바꿔요.
- `menu, price, qty = orders[2]`로 튜플 값을 변수 여러 개에 한 번에 꺼내 담아요.
- `"=" * 33`, 머리글 맞춤, 콤마로 영수증 모양 출력을 만들어요.
- `for menu, price, qty in orders:`로 주문을 하나씩 꺼내 되풀이하고, 합계를 쌓아요.
- `IndexError`, `TypeError`, `ValueError`, `SyntaxError`, `IndentationError`의 마지막 줄을 읽고 고쳐요.

## 시작하기 전에

12에서 쓰던 `hello-uv`의 `basics.ipynb`와 12에서 배운 내용을 그대로 써요.

| 할 일 | 슬라이드 |
| --- | :---: |
| VS Code에 Python, Jupyter 확장 설치, `uv add --dev ipykernel`, 커널로 `.venv` 고르기 | 09 · 25–27쪽 |
| 변수 할당, `print("설명", 값)`, 타입과 `type()`, `int()` `str()` | 12 · 1–2파트 |
| 사칙연산과 `+=`, 글자의 `+`와 `*`, 비교와 `True`·`False` | 12 · 3–4파트 |

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1–4 | 표지, 오늘의 순서와 준비, 12에서 배운 것만으로 찍은 주문 세 줄, 이번 챕터의 큰 그림 |
| 1. 문자열과 출력 | 5–17 | 따옴표와 `len()`, 인덱스와 `IndexError`, 슬라이싱, `print()`의 `sep` `end`와 `\n` `\t`, 끼워 넣는 세 방식, `%s` `%d`와 f-string, `format()`의 `{0}` `{1}` `{2}`, 칸 수, 소수점, 천 단위 콤마, 표처럼 맞추기, 세 방식 한눈에, 포맷팅 오류 |
| 2. 리스트, 튜플, for | 18–35 | `[ ]`로 담기, 꺼내기와 자르기, 값 바꾸기와 `sum` `max` `min`, 넣고 빼는 메서드, 찾고 세고 정렬하는 메서드, `[시작:끝:간격]`, 안쪽 리스트, `+` `*` `extend` `sorted` `reverse` `copy` `clear`, `split`과 `join`, 문자열과 리스트 비교, 튜플, 주문 데이터 `orders`, 꺼내 담기와 `a, b = b, a`, `for`로 하나씩 꺼내기, `for`로 합계 쌓기, 리스트 오류, 콜론과 들여쓰기 오류 |
| 3. 영수증 만들기 | 36–38 | 주문 한 줄 칸 맞추기와 한글 머리글, `for`로 영수증 한 장, 주문 메모 정리하기 |
| 정리 | 39–40 | 막힐 때, 한 장 요약 |

## 핵심 개념

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
| `cart.pop()` | `'cake'`를 돌려주고 `['tea', 'coffee']` | 맨 뒤를 빼서 돌려주기 |
| `cart.pop(0)` | `'tea'`를 돌려주고 `['coffee']` | 0번을 빼서 돌려주기 |
| `scores.count(95)` | `2` | 몇 개인지 |
| `scores.index(80)` | `2` | 몇 번 자리인지 |
| `95 in scores` | `True` | 들어 있는지 |
| `scores.sort()` | `[70, 80, 95, 95]` | 작은 수부터. `reverse=True`면 큰 수부터 |

자르기는 `[시작:끝:간격]`이에요. `nums = [10, 20, 30, 40, 50, 60]`이면 `nums[1:4]`는 `[20, 30, 40]`, `nums[-2:]`는 `[50, 60]`, `nums[::2]`는 `[10, 30, 50]`, `nums[::-1]`은 거꾸로 전부예요. 안쪽 리스트는 `table[1][2]`처럼 번호를 두 번 써요.

| 더 쓰는 것 | 뜻 |
| --- | --- |
| `a + b`, `a * 2` | 이어 붙인 새 리스트, 반복한 새 리스트 |
| `a.extend(b)` | a 뒤에 b를 이어 붙여요. a가 바뀌어요 |
| `sorted(a)` | 정렬한 새 리스트. a는 그대로 |
| `a.reverse()` | 순서만 거꾸로 |
| `a.copy()`, `a.clear()` | 복사본 만들기, 전부 비우기 |
| `"a,b".split(",")` | 글자를 잘라 리스트로 `['a', 'b']` |
| `" / ".join(words)` | 리스트를 사이에 글자를 넣어 하나로 |

문자열도 번호로 꺼내고 자르는 법은 리스트와 같지만, `word[0] = "P"`처럼 글자 하나를 바꾸면 `TypeError`가 나요.

튜플은 바꾸는 메서드가 없고 `count`, `index`만 있어요. `year, month, day = (2026, 11, 2)`처럼 한 번에 꺼내 담고, `a, b = b, a`로 두 값을 맞바꿔요. 고쳐야 하면 `list(튜플)`로 바꿔서 고쳐요.

주문 여러 건은 튜플을 리스트에 담아요. `orders = [("coffee", 4500, 2), ("latte", 5000, 1), ("cake", 6500, 3)]`에서 앞 번호는 몇째 주문, 뒤 번호는 그 안의 몇째 값이에요. `orders[1][0]`은 `'latte'`, `orders[2][1] * orders[2][2]`는 `19500`이에요. `menu, price, qty = orders[2]`처럼 쓰면 튜플 값이 순서대로 하나씩 들어가요.

글자도 `<` `>` `^`로 맞춰요. 파이썬은 한글 한 글자를 한 칸으로 세지만 화면에서는 두 칸 너비라서, 한글 머리글은 한글 글자 수만큼 칸 수를 빼요. 10칸짜리 `'메뉴명'`은 `{'메뉴명':<7}`이에요. 글꼴에 따라 조금 어긋나면 머리글을 영어로 써요.

`for 이름 in 리스트:`는 리스트에서 값을 하나씩 꺼내 이름에 넣고, 아래 네 칸 들여 쓴 줄을 되풀이해요. `for menu, price, qty in orders:`처럼 이름 세 개를 적으면 주문 튜플 하나가 세 이름에 나눠 들어가요. 합계는 for 앞에서 `total = 0`으로 시작하고, 안쪽에서 `total += price * qty`로 쌓아요. 줄 끝 콜론을 빠뜨리면 `SyntaxError`, 들여 쓰지 않으면 `IndentationError`가 나요.

## 실습

VS Code에서 `hello-uv` 폴더를 열고 12에서 쓰던 `basics.ipynb`를 열어요. 오른쪽 위 커널이 `.venv`인지 본 뒤, 아래 코드를 셀 하나에 한 덩어리씩 적고 `Shift+Enter`로 실행해요. 주석(`#` 뒤)은 실제 출력이에요.

### 1. 문자열과 출력

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

### 2. 리스트, 튜플, for

```python
cart = ["coffee", "latte"]
cart.append("cake")
cart.insert(0, "tea")
cart.remove("latte")
print(cart)          # ['tea', 'coffee', 'cake']
last = cart.pop()
first = cart.pop(0)
print(last, first)   # cake tea
print(cart)          # ['coffee']
```

```python
nums = [10, 20, 30, 40, 50, 60]
print(nums[1:4])    # [20, 30, 40]
print(nums[::2])    # [10, 30, 50]
print(nums[::-1])   # [60, 50, 40, 30, 20, 10]
words = "coffee,latte,cake".split(",")
print(" / ".join(words))   # coffee / latte / cake
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

주문을 하나씩 꺼내 합계를 쌓아요. `total = 0`은 for 앞에 한 번만 적어요.

```python
total = 0
for menu, price, qty in orders:
    total += price * qty
    print(menu, total)
print("합계:", total)
# coffee 9000
# latte 14000
# cake 33500
# 합계: 33500
```

### 3. 영수증 만들기

주문 줄은 for 두 줄로 찍어요. 주문이 몇 건이든 셀은 그대로예요.

```python
print("=" * 33)
print(f"{'KANT 카페':^31}")
print("=" * 33)
print(f"{'메뉴명':<7}{'단가':>6}{'수량':>3}{'금액':>8}")
print("-" * 33)
total = 0
for menu, price, qty in orders:
    print(f"{menu:<10}{price:>8,}{qty:>5}{price * qty:>10,}")
    total += price * qty
print("-" * 33)
print(f"{'합계':<6}{total:>25,}")
print("=" * 33)
# =================================
#             KANT 카페
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

쉼표로 이어 적은 주문 메모를 리스트로 바꿔 고친 뒤 다시 글자로 합쳐요.

```python
memo = "latte,cake,latte,coffee,latte"
items = memo.split(",")
items.remove("coffee")
items.append("tea")
print(f"주문 {len(items)}건, latte {items.count('latte')}잔")   # 주문 5건, latte 3잔
items.sort()
print(" / ".join(items))   # cake / latte / latte / latte / tea
```

다 했으면 `Ctrl+S`(Mac `Cmd+S`)로 저장해요.

## 문제 해결

| 증상 | 원인과 해결 |
| --- | --- |
| `IndexError: string index out of range` | 없는 번호예요. 번호는 0부터 `len(값) - 1`까지예요 |
| `TypeError: not enough arguments for format string` | `%` 자리 수와 값 수가 달라요. f-string으로 쓰면 이름을 바로 적어서 덜 틀려요 |
| `ValueError: unsupported format character ','` | `%`에는 콤마 옵션이 없어요. `f"{price:,}"`로 써요 |
| `ValueError: list.remove(x): x not in list` | 리스트에 없는 값을 지우려 했어요. `값 in 리스트`로 먼저 확인해요 |
| `IndexError: list index out of range` | 리스트에 없는 번호예요. 값이 세 개면 마지막 번호는 2 |
| `TypeError: 'tuple' object does not support item assignment` | 튜플은 바꿀 수 없어요. 바꿀 값은 리스트에 담아요 |
| `TypeError: 'str' object does not support item assignment` | 문자열도 글자 하나를 바꿀 수 없어요. 새 문자열을 만들어 담아요 |
| `SyntaxError: expected ':'` | `for` 줄 끝에 콜론을 빠뜨렸어요 |
| `IndentationError: expected an indented block after 'for' statement on line 1` | 되풀이할 줄을 네 칸 들여 써요 |
| 합계가 쌓이지 않아요 | `total = 0`을 for 안에 넣었어요. for 앞으로 옮겨요 |
| 한글 머리글만 칸이 밀려요 | 한글은 화면에서 두 칸이에요. 한글 글자 수만큼 칸 수를 빼거나 머리글을 영어로 |
| `ValueError: Unknown format code 'd' for object of type 'str'` | 글자에 `d`(정수 모양)를 줬어요. 값의 타입을 확인해요 |

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분 (gen.py가 만들어요)
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  cells.py         슬라이드에 나오는 노트북 셀 전부 (파트마다 한 목록)
  run_nb.py        cells.py의 셀을 파트마다 새 커널로 실행하고 outputs.json에 저장
  outputs.json     실제 실행 결과 (gen.py가 읽어요)
  demo.sh          hello-uv를 새로 만들고 run_nb.py로 셀을 실행
  gen.py           모든 장과 deck.json 생성 (노트북 셀, 강조, 글자 칸, 리스트 칸, 영수증)
python-strings-lists-slides.html  배포용 HTML
python-strings-lists-slides.pdf   강사용 PDF
```

검사, HTML, PDF를 만드는 공용 도구(`check.js`, `build_player.js`, `export.js`)는 맨 위 [tools/](../tools)에 한 벌만 있어요. 명령은 이 폴더에서 쳐요.

슬라이드 HTML을 직접 고치지 말고 셀은 `cells.py`, 장은 `gen.py`를 고친 뒤 다시 만들어요. 셀을 고쳤으면 `demo.sh`부터 다시 돌려 `outputs.json`을 새로 만들어요.

```bash
bash tools/demo.sh /tmp/strings-lists-demo > /tmp/strings-lists-demo.log 2>&1
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/build_player.js slides python-strings-lists-slides.html
node ../tools/export.js slides python-strings-lists-slides.pdf
```

셀 출력은 `tools/demo.sh`가 uv 0.11.32로 hello-uv를 만들고 `tools/run_nb.py`로 그 커널에서 실제로 실행한 결과예요. 파트마다 새 커널에서 위에서부터 차례로 실행해서, 슬라이드의 셀 번호가 파트마다 [1]부터 시작해요. 오류는 Traceback 위쪽 줄과 괄호 안의 위치 표시를 빼고 마지막 줄만 옮겼어요. demo.sh 환경의 커널은 Python 3.13이었어요. f-string은 이 챕터 1파트에서 처음 배우고, `for`는 2파트에서 처음 배워요. `input()`, `if`, `range()`는 아직 배우지 않아서 쓰지 않았어요. 영수증 출력의 한글은 슬라이드에서 영어 두 칸 너비로 그렸어요.

2026-11-08에 덱을 다시 짰어요. 장 구성은 Stageshow 원칙(장마다 주인공 하나, 코드에 붙인 설명, 같은 색 짝, 값이 날아가는 움직임)을, 강조는 맨 위 `tools/HIGHLIGHT.md`를 따랐어요.

2026-11-09에 새 플레이어의 강조 기법으로 다시 입혔어요. 줄 스포트라이트(인덱스, 콤마), 실행 막대(for 되풀이), 값 바뀜(리스트 칸, total), 흐리게 하기(메서드, 메모 예제), 흔들기(튜플 자물쇠, 오류), 키 누름(for 오류), 숫자 올라가기(영수증 합계), 같은 색 짝(포맷 자리와 값), 차례로 나오기(목차, 문제 해결 표)를 장마다 골라 썼어요. 글자가 한 자씩 찍히는 효과는 쓰지 않았어요.

</details>

---

<!-- curriculum:nav -->

[← 이전: 12 · 파이썬 기초 1 (변수, 타입, 연산)](../12-python-basics) · [커리큘럼](../README.md) · [다음: 14 · 파이썬 기초 3 (in, 2차원 리스트) →](../14-python-2d-lists)

<!-- /curriculum:nav -->
