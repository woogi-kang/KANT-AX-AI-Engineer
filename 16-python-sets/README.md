# 16 · 파이썬 기초 5 (집합)

> 13에서 리스트와 튜플, 15에서 딕셔너리를 배웠어요. 이번에는 같은 값을 하나만 담는 집합을 배워요. 먼저 집합이 어떤 그릇인지 그림으로 잡고, 값을 넣고 빼고 확인해요. 원 두 개로 합집합, 교집합, 차집합을 그려 본 뒤, 하루 주문과 두 반 명단, 15의 메뉴판에 써 봐요. 모든 예제는 12~15에서 쓰던 노트북에 이어서 적고 실행해요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/16-python-sets/python-sets-slides.html) | [15 · 파이썬 기초 4 (딕셔너리)](../15-python-dict) | 준비 중 |

<!-- /curriculum:top -->

## 학습 목표

이 챕터를 마치면 다음을 할 수 있어요.

- 집합이 중복 없고 순서 없는 주머니라는 것을 리스트, 튜플, 딕셔너리와 비교해 설명해요.
- `{1, 2, 3}`으로 집합을 만들고, `set(orders)`로 리스트의 중복을 없애요.
- 빈 집합은 `{}`가 아니라 `set()`으로 만들어요.
- `print`한 순서가 실행할 때마다 다를 수 있다는 걸 알고, 순서가 필요하면 `sorted()`를 써요.
- `set("banana")`가 글자로 쪼개진다는 것과 리스트는 집합에 못 담는다는 것을 알아요.
- `add`, `remove`, `discard`, `update`, `pop`, `clear`로 값을 넣고 빼요.
- `in`과 `not in`으로 값이 들어 있는지 묻고, 번호로는 꺼낼 수 없다는 걸 알아요.
- 합집합 `|`, 교집합 `&`, 차집합 `-`를 벤 다이어그램으로 읽고, `union()`, `intersection()`, `difference()`로도 써요.
- 주문 목록, 수강생 명단, 메뉴판처럼 두 목록을 비교하는 문제를 집합으로 풀어요.

## 시작하기 전에

12~15에서 쓰던 `hello-uv`의 `basics.ipynb`와 그때 배운 내용을 그대로 써요.

| 할 일 | 슬라이드 |
| --- | :---: |
| VS Code에 Python, Jupyter 확장 설치, `uv add --dev ipykernel`, 커널로 `.venv` 고르기 | 09 · 25–27쪽 |
| f-string과 칸 수, 천 단위 콤마 맞추기 | 13 · 1파트 |
| 리스트와 튜플, `sorted` `count` `list()`, `for` | 13 · 2파트 |
| `in`과 `not in` | 14 |
| 딕셔너리, `KeyError`, `sorted(menu)` | 15 |

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1–3 | 표지, 오늘의 순서, `basics.ipynb` 다시 열기 |
| 1. 집합이 뭔가요 | 4–11 | 같은 값은 한 번만 담는 주머니, 리스트·튜플·딕셔너리·집합 비교, `{3, 1, 2, 3}`과 `type` `len`, 순서가 없어서 커널마다 다르게 찍히는 `print`와 `sorted()`, `set(리스트)`로 중복 없애기, `set("banana")` 함정, 빈 집합 `set()`, 담을 수 있는 값과 `unhashable type: 'list'` |
| 2. 바꾸고 확인하기 | 12–18 | `add`, `remove`와 `discard`, `update`, 아무거나 빼는 `pop`과 `clear`, `in`과 `not in`, 번호로 못 꺼내기(`TypeError`)와 `sorted(menus)[0]`, `for m in menus:`와 `for m in sorted(menus):` |
| 3. 집합 연산 | 19–23 | 벤 다이어그램, 합집합 `a \| b`, 교집합 `a & b`, 차집합 `a - b`와 `b - a`, `union` `intersection` `difference`, 연산 뒤에도 그대로인 `a`와 `b` |
| 4. 실습 | 24–29 | 하루 주문에서 팔린 메뉴 종류와 잔 수, 두 반을 다 듣는 사람과 한쪽만 듣는 사람, 메뉴판에 없는 주문 찾기, 팔 수 있는 주문만 계산하기, 무엇에 담을지 고르기, 자주 나는 오류 |
| 정리 | 30–31 | 막힐 때, 한 장 요약 |

## 핵심 개념

### 집합은 주머니예요

집합(set)은 같은 값을 하나만 담는 주머니예요. 칸 번호가 없어서 순서도 없어요.

| 그릇 | 모양 | 순서 | 중복 | 꺼내기 |
| --- | --- | --- | --- | --- |
| 리스트 | `[1, 2]` | 있어요 | 돼요 | `[번호]` |
| 튜플 | `(1, 2)` | 있어요 | 돼요 | `[번호]` |
| 딕셔너리 | `{"a": 1}` | 넣은 순서 | 키는 안 돼요 | `[키]` |
| 집합 | `{1, 2}` | 없어요 | 안 돼요 | 못 꺼내요 |

글자를 담은 집합을 `print`하면 적은 순서와 다르게 나오고, 커널을 다시 켜면 또 달라질 수 있어요. 내 화면이 슬라이드와 달라도 틀린 게 아니에요. 순서가 필요하면 `sorted()`로 줄 세운 리스트를 써요.

### 넣고 빼기

| 코드 | 하는 일 |
| --- | --- |
| `menus.add("tea")` | 하나 넣어요. 이미 있으면 그대로예요 |
| `menus.remove("latte")` | 빼요. 없으면 `KeyError` |
| `menus.discard("juice")` | 있으면 빼고, 없으면 그냥 넘어가요 |
| `menus.update(["juice", "tea"])` | 리스트의 값을 모두 넣어요 |
| `menus.pop()` | 아무거나 하나 빼서 돌려줘요 |
| `menus.clear()` | 모두 비워요 |
| `"latte" in menus` | 들어 있으면 `True` |

### 집합 연산

`a = {1, 2, 3, 4}`, `b = {3, 4, 5, 6}`일 때 결과예요.

| 기호 | 이름 | 결과 | 뜻 |
| --- | --- | --- | --- |
| `a \| b` | `a.union(b)` | `{1, 2, 3, 4, 5, 6}` | 어느 쪽이든 있는 값 |
| `a & b` | `a.intersection(b)` | `{3, 4}` | 둘 다 있는 값 |
| `a - b` | `a.difference(b)` | `{1, 2}` | `a`에만 있는 값 |
| `b - a` | `b.difference(a)` | `{5, 6}` | `b`에만 있는 값. 앞뒤를 바꾸면 결과가 달라요 |

## 실습

VS Code에서 `hello-uv` 폴더를 열고 `basics.ipynb`를 열어요. 오른쪽 위 커널이 `.venv`인지 본 뒤, 아래 코드를 셀 하나에 한 덩어리씩 적고 `Shift+Enter`로 실행해요. 주석(`#` 뒤)은 실제 출력이에요. 집합을 그대로 찍은 줄은 순서가 다르게 나올 수 있어요.

### 1. 집합이 뭔가요

```python
nums = [3, 1, 3, 2, 1]
print(set(nums))         # {1, 2, 3}
nums = {3, 1, 2, 3}
print(type(nums))        # <class 'set'>
print(len(nums))         # 3
```

```python
orders = ["coffee", "latte", "coffee", "cake", "latte"]
kinds = set(orders)
print(kinds)                       # {'latte', 'cake', 'coffee'} (순서는 다를 수 있어요)
print(len(orders), len(kinds))     # 5 3
print(sorted(kinds))               # ['cake', 'coffee', 'latte']
```

```python
print(set("banana"))     # {'b', 'a', 'n'} (순서는 다를 수 있어요)
print({"banana"})        # {'banana'}
b = set()
print(type(b))           # <class 'set'>
print(type({}))          # <class 'dict'>
```

### 2. 바꾸고 확인하기

```python
menus = {"coffee", "latte", "cake"}
menus.add("tea")
menus.add("coffee")
print(len(menus))              # 4
menus.remove("latte")
menus.discard("juice")
print(sorted(menus))           # ['cake', 'coffee', 'tea']
menus.update(["juice", "tea", "coffee"])
print(len(menus))              # 4
print("cake" in menus)         # True
print("latte" not in menus)    # True
```

```python
for m in sorted(menus):
    print(m)
# cake
# coffee
# juice
# tea
```

### 3. 집합 연산

```python
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}
print(a | b)     # {1, 2, 3, 4, 5, 6}
print(a & b)     # {3, 4}
print(a - b)     # {1, 2}
print(b - a)     # {5, 6}
```

### 4. 실습

```python
orders = ["coffee", "latte", "coffee", "cake",
          "coffee", "latte", "tea"]
kinds = set(orders)
print(f"주문 {len(orders)}잔, 메뉴 {len(kinds)}가지")
for m in sorted(kinds):
    print(m, orders.count(m))
# 주문 7잔, 메뉴 4가지
# cake 1
# coffee 3
# latte 2
# tea 1
```

```python
python_class = {"kim", "lee", "park", "choi"}
data_class = {"park", "choi", "jung", "kang"}
print(sorted(python_class & data_class))     # ['choi', 'park']
print(sorted(python_class - data_class))     # ['kim', 'lee']
print(f"모두 {len(python_class | data_class)}명")   # 모두 6명
```

```python
menu = {"coffee": 4500, "latte": 5000, "cake": 6500}
orders = ["coffee", "tea", "cake", "juice", "coffee"]
print(sorted(set(orders) - set(menu)))     # ['juice', 'tea']
total = 0
for m in sorted(set(orders) & set(menu)):
    qty = orders.count(m)
    print(f"{m:<8}{qty}개 {menu[m] * qty:>7,}원")
    total += menu[m] * qty
print(f"합계 {total:,}원")
# cake    1개   6,500원
# coffee  2개   9,000원
# 합계 15,500원
```

다 했으면 `Ctrl+S`(Mac `Cmd+S`)로 저장해요.

## 명령어 요약

| 코드 | 하는 일 |
| --- | --- |
| `{1, 2, 3}` | 집합 만들기 |
| `set(리스트)` | 리스트의 중복을 없앤 집합 |
| `set()` | 빈 집합. `{}`는 빈 딕셔너리 |
| `s.add(값)` | 하나 넣기 |
| `s.update(리스트)` | 여러 개 넣기 |
| `s.remove(값)` | 빼기. 없으면 `KeyError` |
| `s.discard(값)` | 있으면 빼기 |
| `s.pop()` `s.clear()` | 아무거나 하나 빼기, 모두 비우기 |
| `값 in s`, `값 not in s` | 들어 있는지 묻기 |
| `len(s)` | 값의 개수 |
| `sorted(s)` | abc 순서로 줄 세운 리스트 |
| `a \| b` `a & b` `a - b` | 합집합, 교집합, 차집합 |
| `a.union(b)` `a.intersection(b)` `a.difference(b)` | 위 세 연산의 이름 버전 |

## 문제 해결

| 증상 | 원인과 해결 |
| --- | --- |
| `AttributeError: 'dict' object has no attribute 'add'` | 빈 집합을 `{}`로 만들었어요. `{}`는 빈 딕셔너리예요. `set()`으로 만들어요 |
| `TypeError: 'set' object is not subscriptable` | 집합에 번호를 붙였어요. `sorted(menus)[0]`처럼 리스트로 바꾼 뒤 꺼내요 |
| `KeyError: 'juice'` | 없는 값을 `remove`했어요. 있는지 모르면 `discard`를 써요 |
| `TypeError: unhashable type: 'list'` | 집합이나 딕셔너리 키에 리스트를 넣었어요. 바뀌지 않는 튜플로 바꿔요 |
| `{'b', 'a', 'n'}`처럼 글자만 나와요 | `set()`에 문자열을 넣었어요. 단어 하나는 `{"banana"}`로 적어요 |
| `print` 순서가 슬라이드와 달라요 | 집합은 순서가 없어요. 틀린 게 아니에요. 순서가 필요하면 `sorted()`로 찍어요 |

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분 (gen.py가 만들어요)
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py           모든 장과 deck.json 생성 (노트북 셀, 주머니 그림, 벤 다이어그램)
  demo.sh          hello-uv를 새로 만들고 노트북 셀을 실제로 실행해 출력 확인
  run_nb.py        셀을 프로젝트 커널로 실행 (demo.sh가 불러요)
python-sets-slides.html  배포용 HTML
python-sets-slides.pdf   강사용 PDF
```

검사, HTML, PDF를 만드는 공용 도구(`check.js`, `build_player.js`, `export.js`)는 맨 위 [tools/](../tools)에 한 벌만 있어요. 명령은 이 폴더에서 쳐요.

슬라이드 HTML을 직접 고치지 말고 스크립트를 고친 뒤 다시 만들어요.

```bash
bash tools/demo.sh /tmp/sets-demo > /tmp/sets-demo.log 2>&1
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/build_player.js slides python-sets-slides.html
node ../tools/export.js slides python-sets-slides.pdf
```

셀 출력은 `tools/demo.sh`가 hello-uv를 만들고 `tools/run_nb.py`로 그 커널에서 실제로 실행한 결과예요. 파트마다 새 커널에서 위에서부터 차례로 실행해서, 셀 번호가 파트마다 [1]부터 시작해요. 오류는 Traceback 위쪽 줄을 빼고 마지막 줄만 옮겼어요.

글자를 담은 집합은 커널마다 찍히는 순서가 달라요. 다시 만들어도 같은 출력이 나오도록 `run_nb.py`가 커널마다 `PYTHONHASHSEED`를 고정해요(파트 실행은 22, 7쪽의 다시 실행 예시는 13). 22는 순서가 abc 순서나 적은 순서와 다르게 나오는 값으로 골랐어요. 수업에서는 수강생 화면의 순서가 다르다고 질문이 나오면 7쪽을 보여 줘요. 15쪽 `pop()`의 결과도 실행할 때마다 달라요.

범위는 처음 제안한 여섯 묶음에 for, `pop` `clear` `update`, 메서드 이름 버전, 문자열 함정, 담을 수 있는 값, 무엇에 담을지 고르기를 더했어요. 대칭차집합 `^`, `issubset`, frozenset은 다루지 않아요. `if`는 아직 배우지 않아서 실습도 `&`로 먼저 걸러서 풀었어요. 세 연산은 결과가 늘 작은 수부터 찍히는 숫자 집합으로 먼저 보여 주고, 4파트에서 메뉴와 이름으로 넘어가요.

</details>

---

<!-- curriculum:nav -->

[← 이전: 15 · 파이썬 기초 4 (딕셔너리)](../15-python-dict) · [커리큘럼](../README.md)

<!-- /curriculum:nav -->
