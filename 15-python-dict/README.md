# 15 · 파이썬 기초 4 (딕셔너리)

> 13과 14에서는 리스트에 값을 담고 `orders[1][0]`처럼 번호로 꺼냈어요. 이번에는 번호 대신 이름(키)으로 값을 찾는 딕셔너리를 배워요. 만들고 꺼내고, 바꾸고 지우고, `for`로 둘러본 뒤, 리스트와 섞어서 13의 KANT 카페 영수증을 다시 찍어요. 모든 예제는 12~14에서 쓰던 노트북에 이어서 적고 실행해요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/15-python-dict/python-dict-slides.html) | [14 · 파이썬 기초 3 (in, 2차원 리스트)](../14-python-2d-lists) | 준비 중 |

<!-- /curriculum:top -->

## 학습 목표

이 챕터를 마치면 다음을 할 수 있어요.

- `{"coffee": 4500, "latte": 5000}`처럼 키: 값 쌍으로 딕셔너리를 만들고, `len()`으로 쌍의 개수를 세요.
- `menu["latte"]`로 값을 꺼내고, 없는 키를 꺼낼 때 나는 `KeyError`를 읽어요.
- `menu.get("tea", 0)`으로 없는 키에도 오류 없이 기본값을 받아요.
- 설정값의 기본값, 메뉴판에 없는 주문, `count[w] = count.get(w, 0) + 1` 개수 세기처럼 get을 쓰는 곳을 알아요.
- `menu["tea"] = 4000` 한 문법으로 없는 키는 추가하고, 있는 키는 수정해요.
- 키는 겹치지 않아서 같은 키에 다시 넣으면 값이 덮어써진다는 걸 알아요. 값은 겹쳐도 돼요.
- `del`과 `pop`으로 키와 값을 지워요.
- `in`과 `not in`이 키 쪽만 본다는 걸 알고, 값은 `menu.values()`에서 찾아요.
- `keys()`, `values()`, `items()`로 모으고, `for name, price in menu.items():`로 한 쌍씩 꺼내요.
- `list(menu.keys())[0]`처럼 `list()`로 바꾼 뒤 번호로 꺼내요.
- 값이 리스트인 딕셔너리와 딕셔너리를 담은 리스트를 만들고 `orders[1]["menu"]`처럼 꺼내요.

## 시작하기 전에

12~14에서 쓰던 `hello-uv`의 `basics.ipynb`와 그때 배운 내용을 그대로 써요.

| 할 일 | 슬라이드 |
| --- | :---: |
| VS Code에 Python, Jupyter 확장 설치, `uv add --dev ipykernel`, 커널로 `.venv` 고르기 | 09 · 25–27쪽 |
| f-string과 칸 수, 천 단위 콤마 맞추기 | 13 · 1파트 |
| 리스트와 튜플, `pop` `sum` `max` `sorted` `list()`, `for`와 꺼내 담기, KANT 카페 영수증 | 13 · 2파트 |
| `in`과 `not in`, 2차원 리스트 | 14 |

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1–3 | 표지, 오늘의 순서, `basics.ipynb` 다시 열기 |
| 1. 만들고 꺼내기 | 4–7 | 번호 대신 키로 찾기(사물함 그림), `{키: 값}`과 `type` `len`, 빈 딕셔너리 `{}`, `menu["latte"]`로 꺼내기와 `KeyError`, `get`과 기본값, `None` |
| 2. 바꾸고 지우기 | 8–11 | 없는 키면 추가, 있는 키면 수정, 키는 겹치지 않기(`{"latte": 5000, "latte": 5500}`), 값은 겹쳐도 되기, `del`과 `pop`, 키를 보는 `in`과 `not in` |
| 3. 둘러보기 | 12–17 | `keys()` `values()` `items()`와 `list()`, `list(menu.keys())[0]`처럼 리스트로 바꿔 번호로 꺼내기와 `TypeError`, `for name in menu:`, `for name, price in menu.items():`, `values()`의 `sum` `max` `in`, `sorted(menu)`, get을 쓰는 곳(설정 기본값, 메뉴판에 없는 주문은 0원, 개수 세기) |
| 4. 리스트와 섞기 | 18–23 | 값이 리스트인 딕셔너리, 딕셔너리 리스트 `orders[1]["menu"]`, `for order in orders:`, KANT 카페 영수증 다시 찍기, 메뉴판과 장바구니 딕셔너리, 자주 나는 오류 |
| 정리 | 24–25 | 막힐 때, 한 장 요약 |

## 핵심 개념

### 키와 값

딕셔너리는 사물함과 같아요. 문에 적힌 이름이 키(key), 안에 든 것이 값(value)이에요. 리스트는 칸마다 번호가 있고, 딕셔너리는 칸마다 키가 있어요.

```python
menu = {"coffee": 4500, "latte": 5000, "cake": 6500}
```

| 코드 | 결과 | 뜻 |
| --- | --- | --- |
| `menu["latte"]` | `5000` | latte 키의 값 |
| `menu["tea"]` | `KeyError: 'tea'` | 없는 키를 꺼냈어요 |
| `menu.get("tea")` | `None` | 없으면 None(값 없음) |
| `menu.get("tea", 0)` | `0` | 없으면 정해 둔 값 |
| `len(menu)` | `3` | 키: 값 쌍의 개수 |
| `type(menu)` | `<class 'dict'>` | dict는 dictionary(사전)의 줄임말 |

### 바꾸고 지우기

| 코드 | 하는 일 |
| --- | --- |
| `menu["tea"] = 4000` | tea 키가 없으니 새 칸을 추가해요 |
| `menu["latte"] = 5500` | latte 키가 있으니 값만 바꿔요 |
| `del menu["tea"]` | 키와 값을 같이 지워요 |
| `menu.pop("cake")` | 지우면서 값(`6500`)을 돌려줘요 |
| `"latte" in menu` | 키가 있으면 `True`. 값은 보지 않아요 |
| `5500 in menu.values()` | 값 쪽에서 찾아요 |

키는 겹치지 않아요. `{"latte": 5000, "latte": 5500}`처럼 같은 키를 두 번 적으면 마지막 값만 남아요. 값은 `{"kim": 90, "lee": 90}`처럼 겹쳐도 돼요.

### 둘러보기와 리스트와 섞기

| 코드 | 결과 |
| --- | --- |
| `menu.keys()` | `dict_keys(['coffee', 'latte', 'cake'])` |
| `menu.values()` | `dict_values([4500, 5000, 6500])` |
| `menu.items()` | `dict_items([('coffee', 4500), ('latte', 5000), ('cake', 6500)])` |
| `list(menu.keys())[0]` | `'coffee'` |
| `list(menu.items())[1]` | `('latte', 5000)` |
| `menu.keys()[0]` | `TypeError` (리스트로 바꾸지 않으면 번호로 못 꺼내요) |
| `sorted(menu)` | `['cake', 'coffee', 'latte']` |
| `scores["lee"][1]` | 값이 리스트면 키로 꺼낸 뒤 번호로 한 번 더 꺼내요 |
| `orders[1]["menu"]` | 리스트 안 딕셔너리는 번호로 꺼낸 뒤 키로 꺼내요 |

## 실습

VS Code에서 `hello-uv` 폴더를 열고 `basics.ipynb`를 열어요. 오른쪽 위 커널이 `.venv`인지 본 뒤, 아래 코드를 셀 하나에 한 덩어리씩 적고 `Shift+Enter`로 실행해요. 주석(`#` 뒤)은 실제 출력이에요.

### 1. 만들고 꺼내기

```python
menu = {"coffee": 4500, "latte": 5000, "cake": 6500}
print(menu)          # {'coffee': 4500, 'latte': 5000, 'cake': 6500}
print(type(menu))    # <class 'dict'>
print(len(menu))     # 3
```

```python
print(menu["latte"])         # 5000
price = menu["cake"]
print(price * 2)             # 13000
print(menu.get("tea"))       # None
print(menu.get("tea", 0))    # 0
```

### 2. 바꾸고 지우기

```python
menu["tea"] = 4000
menu["latte"] = 5500
print(menu)          # {'coffee': 4500, 'latte': 5500, 'cake': 6500, 'tea': 4000}
print(len(menu))     # 4
```

```python
dup = {"latte": 5000, "latte": 5500}
print(dup)           # {'latte': 5500}
```

```python
del menu["tea"]
price = menu.pop("cake")
print(price)                  # 6500
print(menu)                   # {'coffee': 4500, 'latte': 5500}
print("latte" in menu)        # True
print(5500 in menu)           # False
```

### 3. 둘러보기

```python
menu = {"coffee": 4500, "latte": 5000, "cake": 6500}
for name, price in menu.items():
    print(f"{name:<8}{price:>6,}원")
# coffee   4,500원
# latte    5,000원
# cake     6,500원
keys = list(menu.keys())
print(keys[0])                    # coffee
pair = list(menu.items())[1]
print(pair)                       # ('latte', 5000)
print(pair[0], pair[1])           # latte 5000
print(sum(menu.values()))         # 16000
print(sorted(menu))               # ['cake', 'coffee', 'latte']
```

get은 없을 수도 있는 키에 써요. 처음 나온 단어는 get이 0을 줘서 1부터 세요.

```python
settings = {"name": "kim"}
print(settings.get("lang", "ko"))     # ko
words = "coffee latte coffee cake coffee latte".split()
count = {}
for w in words:
    count[w] = count.get(w, 0) + 1
print(count)                          # {'coffee': 3, 'latte': 2, 'cake': 1}
```

### 4. 리스트와 섞기

```python
orders = [{"menu": "coffee", "price": 4500, "qty": 2},
          {"menu": "latte", "price": 5000, "qty": 1},
          {"menu": "cake", "price": 6500, "qty": 3}]
print(orders[1]["menu"])      # latte
for order in orders:
    print(order["menu"], order["price"] * order["qty"])
# coffee 9000
# latte 5000
# cake 19500
```

```python
cart = {"coffee": 2, "cake": 3}
total = 0
for name, qty in cart.items():
    price = menu[name]
    print(f"{name} {qty}개 {price * qty:,}원")
    total += price * qty
print(f"합계 {total:,}원")
# coffee 2개 9,000원
# cake 3개 19,500원
# 합계 28,500원
```

13의 KANT 카페 영수증을 딕셔너리 리스트로 다시 찍는 코드는 슬라이드 21쪽에 있어요. 다 했으면 `Ctrl+S`(Mac `Cmd+S`)로 저장해요.

## 명령어 요약

| 코드 | 하는 일 |
| --- | --- |
| `{}` | 빈 딕셔너리 |
| `d[키]` | 값 꺼내기. 없으면 `KeyError` |
| `d.get(키, 기본값)` | 값 꺼내기. 없으면 기본값(안 적으면 `None`) |
| `d[k] = d.get(k, 0) + 1` | 개수 세기. 처음 나온 키는 1부터 |
| `d[키] = 값` | 없으면 추가, 있으면 수정 |
| `del d[키]` | 키와 값 지우기 |
| `d.pop(키)` | 지우면서 값 돌려받기 |
| `키 in d`, `키 not in d` | 키가 있는지 묻기 |
| `len(d)` | 쌍의 개수 |
| `d.keys()` `d.values()` `d.items()` | 키만, 값만, (키, 값) 쌍 모으기 |
| `for k, v in d.items():` | 한 쌍씩 꺼내기 |
| `list(d.keys())[0]` | 리스트로 바꿔 번호로 꺼내기 |

## 문제 해결

| 증상 | 원인과 해결 |
| --- | --- |
| `KeyError: 'tea'` | 없는 키를 꺼냈어요. 키에 오타가 없는지 보고, 없을 수도 있는 키는 `menu.get("tea", 0)`으로 꺼내요 |
| `KeyError: 0` | 딕셔너리를 번호로 꺼냈어요. 딕셔너리는 `menu["coffee"]`처럼 키로 꺼내요 |
| `KeyError: 'Latte'` | 키는 대문자와 소문자를 구분해요. 만들 때 적은 그대로 적어요 |
| `TypeError: list indices must be integers or slices, not str` | 리스트에 키를 넣었어요. `orders[0]["menu"]`처럼 번호부터 적어요 |
| 넣은 값 하나가 사라졌어요 | 같은 키를 두 번 넣었어요. 키가 겹치면 마지막 값만 남아요 |
| `TypeError: 'dict_keys' object is not subscriptable` | `keys()`에 바로 번호를 붙였어요. `list(menu.keys())[0]`처럼 리스트로 바꾼 뒤 꺼내요 |
| `5500 in menu`가 `False`예요 | `in`은 키만 봐요. 값은 `5500 in menu.values()`로 물어요 |

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분 (gen.py가 만들어요)
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py           모든 장과 deck.json 생성 (노트북 셀, 사물함 그림, 영수증)
  demo.sh          hello-uv를 새로 만들고 노트북 셀을 실제로 실행해 출력 확인
  run_nb.py        셀을 프로젝트 커널로 실행 (demo.sh가 불러요)
python-dict-slides.html  배포용 HTML
python-dict-slides.pdf   강사용 PDF
```

검사, HTML, PDF를 만드는 공용 도구(`check.js`, `build_player.js`, `export.js`)는 맨 위 [tools/](../tools)에 한 벌만 있어요. 명령은 이 폴더에서 쳐요.

슬라이드 HTML을 직접 고치지 말고 스크립트를 고친 뒤 다시 만들어요.

```bash
bash tools/demo.sh /tmp/dict-demo > /tmp/dict-demo.log 2>&1
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/build_player.js slides python-dict-slides.html
node ../tools/export.js slides python-dict-slides.pdf
```

셀 출력은 `tools/demo.sh`가 hello-uv를 만들고 `tools/run_nb.py`로 그 커널에서 실제로 실행한 결과예요. 파트마다 새 커널에서 위에서부터 차례로 실행해서, 셀 번호가 파트마다 [1]부터 시작해요. 그래서 2, 3, 4파트의 첫 셀에서 `menu`나 `scores`를 다시 만들어요. 오류는 Traceback 위쪽 줄을 빼고 마지막 줄만 옮겼어요. 영수증 출력의 한글은 슬라이드에서 영어 두 칸 너비로 그렸어요.

범위는 가볍게 잡았어요. `setdefault`, `zip()`, 딕셔너리 컴프리헨션, JSON, 키에 리스트를 못 쓰는 이유는 다루지 않아요. `if`는 아직 배우지 않아서 쓰지 않았어요. 사물함 그림에서 키를 "이름"이라고도 불렀는데, Git 덱의 브랜치 "이름표"와 섞이지 않게 "이름표"라는 말은 쓰지 않았어요.

</details>

---

<!-- curriculum:nav -->

[← 이전: 14 · 파이썬 기초 3 (in, 2차원 리스트)](../14-python-2d-lists) · [커리큘럼](../README.md)

<!-- /curriculum:nav -->
