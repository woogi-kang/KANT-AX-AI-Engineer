# 17 · 제어문 1 (조건문 if)

> 지금까지 셀은 적은 줄을 위에서부터 모두 실행했어요. 이번에는 `if`로 조건에 따라 실행할 줄을 골라요. 12의 비교와 `and`, `or`, `not`, 14의 `in`을 조건으로 쓰고, 13의 `for` 안에 `if`를 넣어 골라 담아요. 15, 16에서 "참고, 읽기만"으로 둔 코드도 이번에 직접 쳐요. 같은 카페 예제를 18까지 이어서 써요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/17-python-if/python-if-slides.html) | [16 · 파이썬 기초 5 (집합)](../16-python-sets) | [18 · 제어문 2 (반복 제어 while, break)](../18-python-while) |

<!-- /curriculum:top -->

## 학습 목표

이 챕터를 마치면 다음을 할 수 있어요.

- `if 조건:`과 4칸 들여쓰기로 조건이 True일 때만 실행할 줄을 정해요.
- `else`로 False일 때 갈 길을, `elif`로 셋 이상의 갈림길을 만들어요.
- `elif`는 위에서부터 처음 True인 하나만 실행해서 조건 순서가 중요하다는 걸 알아요.
- `and`, `or`, `not`, `not in`, `9 <= hour < 18`로 조건을 합쳐요.
- `0`, `""`, `[]`, `{}`, `set()`, `None`은 False로 친다는 걸 `bool()`로 확인해요.
- `for` 안에 `if`를 넣어 조건에 맞는 값을 골라 담고 세요.
- 한 줄 `값1 if 조건 else 값2`, 15의 `get`, 16의 `discard`를 원래 `if` 코드와 나란히 읽어요.
- `=`와 `==`, 콜론, 들여쓰기, `or` 함정, 글자와 숫자 비교 오류를 고쳐요.

## 시작하기 전에

12~16에서 쓰던 `hello-uv`의 `basics.ipynb`와 그때 배운 내용을 그대로 써요.

| 할 일 | 슬라이드 |
| --- | :---: |
| VS Code에 Python, Jupyter 확장 설치, `uv add --dev ipykernel`, 커널로 `.venv` 고르기 | 09 · 25–27쪽 |
| 비교 `==` `>=`, `and` `or` `not`, `int()` | 12 · 3파트 |
| 리스트, `for`, f-string과 칸 맞추기 | 13 |
| `in`과 `not in` | 14 |
| 딕셔너리 `menu`, `get`, `items()` | 15 |
| 집합, `discard` | 16 |

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1–3 | 표지, 오늘의 순서, `basics.ipynb` 다시 열기 |
| 1. 참과 거짓으로 길 고르기 | 4–7 | 메뉴판에 없는 주문에서 나는 `KeyError`(왜 필요한가), 갈림길 그림(큰 그림), 가장 짧은 `if`와 콜론, 들여쓰기, 조건은 True나 False가 나오는 식 |
| 2. if, else, elif | 8–13 | False면 건너뛰기, 들여쓴 줄까지가 if, `else`, `elif`와 할인율, 조건 순서를 바꾸면 달라지는 결과, `if` 여러 개와 `elif` 비교 |
| 3. 조건 합치기 | 14–20 | 12의 놀이기구 조건을 `and`로, if 안의 if를 `and`로 줄이기, `or`, `not`과 `not in`, 범위 `9 <= hour < 18`, 비어 있으면 False(`bool()`), `if orders:`와 `if len(orders) > 0:` |
| 4. for와 함께, 줄여 쓰기 | 21–26 | for 안의 if로 골라 담기, 조건에 맞는 것 세기와 `count`, `items()`에서 찾기, 한 줄 `if else`, 15의 `get` 풀어 읽기, 16의 `discard`와 중복 없애기 긴 코드 직접 치기 |
| 5. 자주 나는 오류 | 27–30 | `=`와 `==`(`SyntaxError`), 콜론과 들여쓰기(`IndentationError`), `or "latte"` 함정, `"4500" >= 4000`(`TypeError`) |
| 6. 실습 | 31–34 | 장바구니 금액별 할인, 점수로 등급 매기기, 메뉴판에 없는 주문 빼고 계산하기, 어떤 모양을 쓸지 고르기 |
| 정리 | 35–36 | 막힐 때, 한 장 요약 |

## 핵심 개념

### if는 갈림길이에요

```python
if money >= price:
    print("주문할 수 있어요")   # 조건이 True일 때만
print("다음 손님")              # if 밖이라 늘 실행
```

`if` 뒤에 조건을 적고 콜론(`:`)으로 끝내요. 다음 줄을 4칸 들여쓰면 그 줄은 조건이 True일 때만 실행해요. 들여쓴 줄까지가 `if` 안이에요. VS Code에서 콜론 뒤 `Enter`를 치면 4칸이 저절로 들어가요.

| 모양 | 언제 |
| --- | --- |
| `if` | 조건이 맞을 때만 할 일이 있을 때 |
| `if` … `else` | 둘 중 하나는 꼭 할 때 |
| `if` … `elif` … `else` | 셋 이상 중 하나만 고를 때. 위에서부터 처음 True 하나만 실행해요 |
| `if` 여러 개 | 각각 따로 확인할 때. 여러 개가 실행될 수 있어요 |

### 조건 합치기

| 조건 | 뜻 |
| --- | --- |
| `a and b` | 둘 다 True |
| `a or b` | 하나라도 True |
| `not a`, `x not in menu` | 반대로 묻기 |
| `9 <= hour < 18` | 범위. `hour >= 9 and hour < 18`과 같아요 |

`0`, `""`, `[]`, `{}`, `set()`, `None`은 False로 보고, 나머지는 True로 봐요. 그래서 `if orders:`는 "주문이 하나라도 있으면"이에요.

### 줄여 쓴 것과 원래 모양

| 줄인 방법 | 원래 모양 |
| --- | --- |
| `msg = "5% 할인" if total >= 10000 else "할인 없음"` | `if`, `else` 4줄로 `msg`에 넣기 |
| `menu.get("cakee", 5000)` | `if "cakee" in menu:` 있으면 꺼내고, 없으면 5000 |
| `menus.discard("juice")` | `if "juice" in menus:` 있으면 `remove` |
| `orders.count("coffee")` | `for`와 `if o == "coffee":` 안에서 `n += 1` |

## 실습

VS Code에서 `hello-uv` 폴더를 열고 `basics.ipynb`를 열어요. 오른쪽 위 커널이 `.venv`인지 본 뒤, 아래 코드를 셀 하나에 한 덩어리씩 적고 `Shift+Enter`로 실행해요. 주석(`#` 뒤)은 실제 출력이에요.

### 1. if, else, elif

```python
price = 4500
money = 3000
if money >= price:
    print("주문할 수 있어요")
else:
    print(f"{price - money}원 더 필요해요")
# 1500원 더 필요해요
```

```python
total = 12000
if total >= 20000:
    print("10% 할인")
elif total >= 10000:
    print("5% 할인")
else:
    print("할인 없음")
# 5% 할인
```

`total`을 25000, 3000으로 바꿔 실행하면 `10% 할인`, `할인 없음`이 나와요. 두 조건의 순서를 바꾸면 25000에서도 `5% 할인`이 나와요.

### 2. 조건 합치기

```python
height = 130
age = 9
if height >= 120 and age >= 7:
    print("탈 수 있어요")       # 탈 수 있어요
hour = 14
if 9 <= hour < 18:
    print("영업 중이에요")      # 영업 중이에요
print(bool(0), bool(4500))     # False True
print(bool([]), bool(["tea"])) # False True
```

### 3. for와 함께

```python
menu = {"coffee": 4500, "latte": 5000, "cake": 6500}
prices = [4500, 5000, 6500, 4000]
cheap = []
for p in prices:
    if p <= 5000:
        cheap.append(p)
print(cheap)                   # [4500, 5000, 4000]
for name, price in menu.items():
    if price <= 5000:
        print(name, price)
# coffee 4500
# latte 5000
```

```python
if "cakee" in menu:
    price = menu["cakee"]
else:
    price = 5000
print(price)                   # 5000
print(menu.get("cakee", 5000)) # 5000
```

### 4. 실습: 메뉴판에 없는 주문 빼고 계산하기

```python
orders = ["coffee", "tea", "cake", "coffee", "juice"]
total = 0
skipped = []
for o in orders:
    if o in menu:
        print(f"{o:<8}{menu[o]:>6,}원")
        total += menu[o]
    else:
        skipped.append(o)
print(f"합계 {total:,}원")
if skipped:
    print("준비 중:", skipped)
# coffee   4,500원
# cake     6,500원
# coffee   4,500원
# 합계 15,500원
# 준비 중: ['tea', 'juice']
```

다 했으면 `Ctrl+S`(Mac `Cmd+S`)로 저장해요.

## 명령어 요약

| 코드 | 하는 일 |
| --- | --- |
| `if 조건:` | 조건이 True면 들여쓴 줄을 실행 |
| `else:` | 앞 조건이 모두 False일 때 |
| `elif 조건:` | 앞 조건이 False일 때 다음 조건 묻기 |
| `a and b`, `a or b`, `not a` | 둘 다, 하나라도, 반대로 |
| `x in d`, `x not in d` | 들어 있는지, 없는지 |
| `9 <= hour < 18` | 범위 묻기 |
| `bool(값)` | if에서 True로 볼지 False로 볼지 확인 |
| `값1 if 조건 else 값2` | 둘 중 하나를 고르는 한 줄 모양 |

## 문제 해결

| 증상 | 원인과 해결 |
| --- | --- |
| `SyntaxError: invalid syntax. Maybe you meant '==' or ':=' instead of '='?` | `if` 뒤에 `=` 하나를 썼어요. 묻기는 `==`예요 |
| `SyntaxError: expected ':'` | `if`, `elif`, `else` 줄 끝에 콜론이 없어요 |
| `IndentationError: expected an indented block after 'if' statement on line 1` | `if` 다음 줄을 들여쓰지 않았어요. 4칸 들여써요 |
| `IndentationError: unexpected indent` | 같은 `if` 안에서 칸 수가 달라요. 4칸에 맞춰요 |
| `TypeError: '>=' not supported between instances of 'str' and 'int'` | 따옴표 숫자(글자)와 숫자를 비교했어요. `int(price)`로 바꿔요 |
| 조건이 늘 True예요 | `order == "coffee" or "latte"`처럼 `or` 뒤에 비교를 빼먹었어요. `order == "coffee" or order == "latte"` 또는 `order in ["coffee", "latte"]` |
| 25000원인데 5% 할인이 나와요 | `elif` 순서가 바뀌었어요. 좁은 조건(큰 금액)을 위에 둬요 |
| 돈이 모자란데 커피가 나와요 | 그 줄이 `if` 밖에 있어요. 들여쓰기를 맞춰요 |

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분 (gen.py가 만들어요)
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py           모든 장과 deck.json 생성 (노트북 셀, 실행한 줄 표시, 갈림길 그림)
  demo.sh          hello-uv를 새로 만들고 노트북 셀을 실제로 실행해 출력 확인
  run_nb.py        셀을 프로젝트 커널로 실행 (demo.sh가 불러요)
python-if-slides.html  배포용 HTML
python-if-slides.pdf   강사용 PDF
```

검사, HTML, PDF를 만드는 공용 도구(`check.js`, `build_player.js`, `export.js`)는 맨 위 [tools/](../tools)에 한 벌만 있어요. 명령은 이 폴더에서 쳐요.

슬라이드 HTML을 직접 고치지 말고 스크립트를 고친 뒤 다시 만들어요.

```bash
bash tools/demo.sh /tmp/if-demo > /tmp/if-demo.log 2>&1
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/build_player.js slides python-if-slides.html
node ../tools/export.js slides python-if-slides.pdf
```

셀 출력은 `tools/demo.sh`가 hello-uv를 만들고 `tools/run_nb.py`로 그 커널에서 실제로 실행한 결과예요. 파트마다 새 커널에서 위에서부터 차례로 실행해서, 셀 번호가 파트마다 [1]부터 시작해요. 오류는 Traceback 위쪽 줄을 빼고 마지막 줄만 옮겼어요. 27쪽만 줄 번호를 읽는 법을 보여 주려고 `Cell In[1], line 2` 줄을 남겼어요. 11쪽 오른쪽 아래의 total 세 가지 결과와 13쪽 오른쪽 셀 [7]은 2파트 커널에서 같은 셀을 total만 바꿔 실행한 결과예요.

코드 칸 위의 색 띠는 그 줄이 실행됐는지(초록), 건너뛰었는지(회색), 문제인지(빨강), 눈여겨볼 줄인지(파랑) 표시해요. 클릭할 때마다 하나씩 나타나요.

범위는 처음 제안한 열 묶음 그대로예요. `match`, `input()`, 바다코끼리 연산자 `:=`는 다루지 않아요. 27쪽의 오류 메시지에 `:=`가 나오지만 배우지 않은 기호라 넘어가도 된다고 적었어요. 15, 16의 "참고, 읽기만" 코드는 4파트(25, 26쪽)에서 직접 치는 셀로 바꿨어요.

</details>

---

<!-- curriculum:nav -->

[← 이전: 16 · 파이썬 기초 5 (집합)](../16-python-sets) · [커리큘럼](../README.md) · [다음: 18 · 제어문 2 (반복 제어 while, break) →](../18-python-while)

<!-- /curriculum:nav -->
