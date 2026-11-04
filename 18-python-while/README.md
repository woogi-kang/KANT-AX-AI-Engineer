# 18 · 제어문 2 (반복 제어 while, break)

> 13의 `for`는 리스트를 처음부터 끝까지 돌았어요. 이번에는 `range()`로 정한 횟수만큼 돌고, `while`로 조건이 True인 동안 돌아요. `break`와 `continue`로 도중에 멈추거나 한 차례를 건너뛰어요. 합계, 개수, 최댓값을 반복으로 직접 쌓아 `sum()`, `max()`와 비교하고, 반복을 겹쳐 구구단과 14의 성적표를 돌아요. 17과 같은 카페 예제를 이어서 써요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/18-python-while/python-while-slides.html) | [17 · 제어문 1 (조건문 if)](../17-python-if) | [19 · 함수 1 (정의, 매개변수, return)](../19-python-functions) |

<!-- /curriculum:top -->

## 학습 목표

이 챕터를 마치면 다음을 할 수 있어요.

- 몇 번 돌지 모를 때 `for`로는 쓰기 어렵다는 걸 알고, `while`이 필요한 장면을 말해요.
- `range(5)`, `range(1, 6)`, `range(0, 10, 2)`, `range(5, 0, -1)`을 `list()`로 확인하고, 끝 숫자가 빠진다는 걸 알아요.
- `for i in range(len(xs))`와 `enumerate(xs)`로 번호와 값을 같이 써요.
- `while`의 시작값, 조건, 값 바꾸기를 찾고, 무한 반복을 멈춰요.
- `break`로 반복을 끝내고, `continue`로 이번 차례만 넘겨요. `while True`와 `break`를 같이 써요.
- 합계, 개수 세기, 조건 맞는 값 모으기, 최댓값 찾기를 반복으로 직접 쓰고 `sum()`, `count()`, `max()`와 비교해요.
- 반복 안에 반복을 넣어 표를 만들고, 안쪽 `break`는 안쪽만 멈춘다는 걸 알아요.
- 돌면서 리스트 지우기, 들여쓰기 한 단계 차이, `range(len()) + 1` 같은 함정을 피해요.

## 시작하기 전에

12~17에서 쓰던 `hello-uv`의 `basics.ipynb`와 그때 배운 내용을 그대로 써요.

| 할 일 | 슬라이드 |
| --- | :---: |
| VS Code에 Python, Jupyter 확장 설치, `uv add --dev ipykernel`, 커널로 `.venv` 고르기 | 09 · 25–27쪽 |
| `+=`, `-=`, `//` | 12 |
| 리스트, `for`, f-string 칸 맞추기, `print`의 `end`, `sum` `max` `min` `count` | 13 |
| 2차원 리스트 `scores[i][j]` | 14 |
| 딕셔너리 `items()`, `stock[o] -= 1` | 15 |
| `if`, `elif`, `else`, `and`, `or` | 17 |

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1–3 | 표지, 오늘의 순서, `basics.ipynb` 다시 열기 |
| 1. 왜 필요한가 | 4–6 | 10000원으로 커피를 세 잔 사서 돈이 마이너스가 되는 for(왜 필요한가), for와 while 그림(큰 그림), 가장 짧은 while로 몇 잔인지 세기 |
| 2. range와 번호 | 7–11 | `range(5)`와 `list()`, 시작과 끝과 간격, 거꾸로 세기, `for i in range(3):`, `range(len(menus))`와 직접 번호 세기, `enumerate(menus, 1)` |
| 3. while | 12–15 | 시작값, 묻기, 실행, 값 바꾸기, 재고가 0이 될 때까지와 0번 도는 while, 무한 반복과 멈추는 법(■, Interrupt, `Ctrl+C`), for와 while 고르기 |
| 4. break와 continue | 16–20 | 같은 주문 리스트에서 품절을 만나면 멈추기(`break`)와 품절만 건너뛰기(`continue`), 결과 나란히 비교, 1부터 5까지 점프 화살표, `continue`를 `if`, `else`로 길게 쓰기, `while True`와 `break` |
| 5. 쌓기와 겹친 반복 | 21–26 | 합계와 `sum()`, 세기와 모으기, 최댓값과 `max()` `min()`, 구구단 2·3단, 14의 성적표를 행과 열 번호로, 안쪽 `break` |
| 6. 함정과 실습 | 27–33 | 돌면서 `remove`, 들여쓰기 한 단계 차이 세 가지, `range(len(menus) + 1)`의 `IndexError`, 재고가 모자랄 때까지 주문 받기, 처음 품절에서 주문 멈추기, 구구단 표, 숫자 맞히기 |
| 정리 | 34–35 | 막힐 때, 한 장 요약 |

## 핵심 개념

### for와 while

| | `for` | `while` |
| --- | --- | --- |
| 언제 | 횟수나 묶음이 정해졌을 때 | 조건이 False가 될 때까지 |
| 예 | 메뉴 하나씩, 10번 반복 | 돈이 남는 동안, 재고가 있는 동안 |
| 멈춤 | 값이 떨어지면 저절로 | 값 바꾸기를 직접 적어야 해요 |

`while`에는 시작값, 조건, 값 바꾸기 세 가지가 꼭 있어야 해요. 값 바꾸기를 빠뜨리면 끝나지 않아요. 노트북에서는 셀 왼쪽의 ■ 버튼이나 위쪽의 Interrupt로, 터미널에서는 `Ctrl+C`(Mac `control+C`)로 멈춰요.

### range

| 코드 | 숫자 |
| --- | --- |
| `range(5)` | 0, 1, 2, 3, 4 |
| `range(1, 6)` | 1, 2, 3, 4, 5 |
| `range(0, 10, 2)` | 0, 2, 4, 6, 8 |
| `range(5, 0, -1)` | 5, 4, 3, 2, 1 |

끝 숫자는 늘 빠져요. 13의 자르기 `[시작:끝:간격]`과 같은 규칙이에요.

### break와 continue

| 코드 | 하는 일 |
| --- | --- |
| `break` | 반복을 바로 끝내요. 가장 가까운 반복 하나만 끝내요 |
| `continue` | 아래 줄을 건너뛰고 다음 차례로 가요. `if`, `else`로 길게 써도 결과가 같아요 |

### 반복으로 쌓기

| 하는 일 | 원래 모양 | 줄인 방법 |
| --- | --- | --- |
| 합계 | `total = 0`, 반복 안에서 `total += p` | `sum(prices)` |
| 같은 값 세기 | `n = 0`, `if p == 4500:` 안에서 `n += 1` | `prices.count(4500)` |
| 조건 맞는 값 세기 | `if p >= 5000:` 안에서 `n += 1` | 없어요 |
| 가장 큰 값 | `big = prices[0]`, 더 크면 바꾸기 | `max(prices)` |

## 실습

VS Code에서 `hello-uv` 폴더를 열고 `basics.ipynb`를 열어요. 오른쪽 위 커널이 `.venv`인지 본 뒤, 아래 코드를 셀 하나에 한 덩어리씩 적고 `Shift+Enter`로 실행해요. 주석(`#` 뒤)은 실제 출력이에요.

### 1. while로 몇 잔인지 세기

```python
money = 10000
cups = 0
while money >= 4500:
    money -= 4500
    cups += 1
print(f"{cups}잔, 남은 돈 {money}원")
# 2잔, 남은 돈 1000원
```

### 2. range와 enumerate

```python
print(list(range(5)))            # [0, 1, 2, 3, 4]
print(list(range(1, 6)))         # [1, 2, 3, 4, 5]
print(list(range(5, 0, -1)))     # [5, 4, 3, 2, 1]
menus = ["coffee", "latte", "cake"]
for i, m in enumerate(menus, 1):
    print(f"{i}. {m}")
# 1. coffee
# 2. latte
# 3. cake
```

### 3. break와 continue

```python
orders = ["coffee", "cake", "latte", "tea", "cake"]
soldout = ["latte"]
for o in orders:
    if o in soldout:
        print(f"{o} 품절, 주문을 멈춰요")
        break
    print(f"{o} 주문 받았어요")
print("끝")
# coffee 주문 받았어요
# cake 주문 받았어요
# latte 품절, 주문을 멈춰요
# 끝
```

같은 셀에서 `break`를 `continue`로, 메시지를 `건너뛰어요`로 바꾸면 latte만 빼고 tea와 cake까지 받아요.

```python
for o in orders:
    if o in soldout:
        print(f"{o} 품절, 건너뛰어요")
        continue
    print(f"{o} 주문 받았어요")
print("끝")
# coffee 주문 받았어요
# cake 주문 받았어요
# latte 품절, 건너뛰어요
# tea 주문 받았어요
# cake 주문 받았어요
# 끝
```

`break`는 반복 아래 줄로 나가고, `continue`는 반복 맨 위로 돌아가 다음 차례를 꺼내요.

### 4. 쌓기

```python
prices = [4500, 5000, 6500, 4500]
big = prices[0]
for p in prices:
    if p > big:
        big = p
print(big)                       # 6500
print(max(prices), min(prices))  # 6500 4500
```

### 5. 실습: 구구단 표

```python
for dan in range(2, 10):
    print(f"{dan}단", end=" ")
    for i in range(1, 10):
        print(f"{dan * i:>3}", end="")
    print()
# 2단   2  4  6  8 10 12 14 16 18
# 3단   3  6  9 12 15 18 21 24 27
# (9단까지 이어져요)
```

### 6. 실습: 숫자 맞히기

```python
answer = 37
guesses = [50, 25, 37, 40]
tries = 0
for g in guesses:
    tries += 1
    if g == answer:
        print(f"{g}: 정답이에요. {tries}번 만에 맞혔어요")
        break
    elif g > answer:
        print(f"{g}: 더 작아요")
    else:
        print(f"{g}: 더 커요")
# 50: 더 작아요
# 25: 더 커요
# 37: 정답이에요. 3번 만에 맞혔어요
```

다 했으면 `Ctrl+S`(Mac `Cmd+S`)로 저장해요.

## 명령어 요약

| 코드 | 하는 일 |
| --- | --- |
| `range(끝)` `range(시작, 끝)` `range(시작, 끝, 간격)` | 숫자 줄. 끝은 빠져요 |
| `list(range(5))` | range를 눈으로 확인 |
| `for i in range(n):` | n번 반복 |
| `for i in range(len(xs)):` | 번호로 돌고 `xs[i]`로 꺼내기 |
| `for i, x in enumerate(xs, 1):` | 번호(1부터)와 값을 같이 |
| `while 조건:` | 조건이 True인 동안 반복 |
| `while True:` | `break`를 만날 때까지 반복 |
| `break` | 반복 끝내기 |
| `continue` | 이번 차례만 넘기기 |
| `print()` | 줄만 바꾸기 |

## 문제 해결

| 증상 | 원인과 해결 |
| --- | --- |
| 셀이 끝나지 않고 출력이 계속 나와요 | `while` 조건이 늘 True예요. ■ 버튼이나 Interrupt로 멈추고 값 바꾸기 줄을 넣어요 |
| `KeyboardInterrupt` | 직접 멈췄다는 표시예요. 오류가 아니에요 |
| `IndexError: list index out of range` | `range(len(menus) + 1)`처럼 칸을 넘었어요. `range(len(menus))`가 딱 맞아요 |
| 1부터 5까지 도는데 4에서 끝나요 | `range`의 끝 숫자는 빠져요. `range(1, 6)` |
| 지웠는데 하나가 남아요 | 돌고 있는 리스트를 `remove`했어요. 남길 것만 새 리스트에 `append`해요 |
| 합계가 마지막 값만 나와요 | `total = 0`을 `for` 안에 넣었어요. `for` 위로 옮겨요 |
| 합계가 줄마다 찍혀요 | `print`가 `for` 안에 있어요. 들여쓰기를 빼요 |
| 바깥 반복이 멈추지 않아요 | `break`는 가장 가까운 반복 하나만 끝내요 |

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분 (gen.py가 만들어요)
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py           모든 장과 deck.json 생성 (노트북 셀, 실행한 줄 표시, 반복 그림, 값 바뀌는 표)
  demo.sh          hello-uv를 새로 만들고 노트북 셀을 실제로 실행해 출력 확인
  run_nb.py        셀을 프로젝트 커널로 실행 (demo.sh가 불러요)
python-while-slides.html  배포용 HTML
python-while-slides.pdf   강사용 PDF
```

검사, HTML, PDF를 만드는 공용 도구(`check.js`, `build_player.js`, `export.js`)는 맨 위 [tools/](../tools)에 한 벌만 있어요. 명령은 이 폴더에서 쳐요.

슬라이드 HTML을 직접 고치지 말고 스크립트를 고친 뒤 다시 만들어요.

```bash
bash tools/demo.sh /tmp/while-demo > /tmp/while-demo.log 2>&1
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/build_player.js slides python-while-slides.html
node ../tools/export.js slides python-while-slides.pdf
```

셀 출력은 `tools/demo.sh`가 hello-uv를 만들고 `tools/run_nb.py`로 그 커널에서 실제로 실행한 결과예요. 파트마다 새 커널에서 위에서부터 차례로 실행해서, 셀 번호가 파트마다 [1]부터 시작해요. 오류는 Traceback 위쪽 줄을 빼고 마지막 줄만 옮겼어요.

14쪽의 무한 반복은 따로 띄운 커널에서 1초 뒤 멈춰(`interrupt_on_timeout`) 실제로 받은 출력이에요. 1초 동안 `1`이 17만 줄 넘게 찍혀서 앞의 네 줄과 마지막 `KeyboardInterrupt`만 옮겼어요. 수강생이 따라 칠 땐 바로 멈추라고 알려 줘요. 6파트의 실습 셀 [8]~[11]도 따로 띄운 커널에서 실행했어요. 앞 셀의 값을 쓰지 않아서 결과는 같아요.

범위는 처음 제안한 아홉 묶음 그대로예요. `for ... else`, `zip()`, `input()`, 바깥 반복까지 한 번에 멈추는 방법은 다루지 않아요. `range()`와 `enumerate()`는 이 챕터에서 처음 배워요.

</details>

---

<!-- curriculum:nav -->

[← 이전: 17 · 제어문 1 (조건문 if)](../17-python-if) · [커리큘럼](../README.md) · [다음: 19 · 함수 1 (정의, 매개변수, return) →](../19-python-functions)

<!-- /curriculum:nav -->
