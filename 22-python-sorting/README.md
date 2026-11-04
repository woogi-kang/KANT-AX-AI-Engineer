# 22 · 정렬과 sorted, max, min 제대로 쓰기

> 판매량 딕셔너리에서 가장 많이 팔린 메뉴를 물었는데 `max(sales)`가 `tea`를 돌려줘요. 키끼리 abc 순으로 비교했기 때문이에요. 이번에는 `sorted`와 `sort`의 차이를 보고, `key=`로 무엇을 기준으로 비교할지 정해요. 튜플과 딕셔너리를 줄 세우고, `max`와 `min`으로 가장 큰 것과 작은 것을 골라요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/22-python-sorting/python-sorting-slides.html) | [21 · 함수 3 (lambda, map, filter)](../21-python-lambda) | [23 · 리스트 컴프리헨션](../23-python-comprehension) |

<!-- /curriculum:top -->

## 학습 목표

이 챕터를 마치면 다음을 할 수 있어요.

- `sorted(xs)`는 새 리스트를 주고 `xs.sort()`는 원본을 바꾸며 `None`을 돌려준다는 걸 알아요. `xs = xs.sort()`를 쓰지 않아요.
- `reverse=True`로 큰 것부터 세워요.
- 글자는 앞 글자부터 비교하고 대문자가 소문자보다 앞이라는 걸 알아요. `key=len`, `key=str.lower`, `key=int`로 비교 방법을 바꿔요.
- 튜플은 앞 칸부터 비교한다는 걸 알고, `key=lambda m: m[1]`로 둘째 칸 기준, `key=lambda m: (-m[1], m[0])`로 두 기준을 정해요.
- 딕셔너리에서 키, 값, 짝(`items()`) 중 무엇을 줄 세울지 고르고, `key=sales.get`으로 값 순서대로 키를 세워요.
- `max`, `min`에 `key=`와 `default=`를 넣고, `max(sales, key=sales.get)`으로 가장 많이 팔린 메뉴를 골라요.
- `sum`, `len`, `[:3]`과 같이 써서 평균과 상위 3개를 구해요.

## 시작하기 전에

12~21에서 쓰던 `hello-uv`의 `basics.ipynb`와 그때 배운 내용을 그대로 써요.

| 할 일 | 슬라이드 |
| --- | :---: |
| VS Code에 Python, Jupyter 확장 설치, `uv add --dev ipykernel`, 커널로 `.venv` 고르기 | 09 · 25–27쪽 |
| 리스트, 튜플, `sort`, `sorted`, `max`, `min`, `[:3]` 자르기 | 13 |
| 딕셔너리 `get`, `values`, `items` | 15 |
| `sorted(..., reverse=True)` | 16 |
| `enumerate()` | 18 |
| `lambda`, `map`, `filter` | 21 |

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1–3 | 표지, 오늘의 순서, `basics.ipynb` 다시 열기 |
| 1. 왜 필요한가 | 4–6 | `max(sales)`가 `tea`인 이유(왜 필요한가), 비교할 값을 따로 만드는 `key` 그림(큰 그림), 가장 짧은 `key` |
| 2. sorted, sort, key | 7–12 | 새 리스트와 원본, `prices = prices.sort()` 함정, `reverse=True`, 글자 비교, `key=len`, `key=str.lower`와 `key=int` |
| 3. 튜플과 딕셔너리 정렬 | 13–18 | 튜플은 앞 칸부터, `m[1]` 기준, 두 기준 `(-m[1], m[0])`, 딕셔너리의 키·값·짝, `items()` 판매 순위, `key=sales.get` |
| 4. max와 min | 19–22 | `max`, `min`의 `key`, 가장 많이 팔린 메뉴, 빈 리스트와 `default=`, `sum` `len` `[:3]`과 같이 쓰기 |
| 5. 오류와 함정 | 23–25 | 숫자와 글자 섞기, `key`에 괄호, `lambda`나 `key=` 빠뜨리기 |
| 6. 실습 | 26–29 | 판매 순위 3위까지, 가장 비싼 메뉴와 싼 메뉴, 이름 길이순 메뉴판, 성적표 |
| 정리 | 30–31 | 막힐 때, 한 장 요약 |

## 핵심 개념

### sorted와 sort

| | `sorted(xs)` | `xs.sort()` |
| --- | --- | --- |
| 원본 `xs` | 그대로 | 바뀌어요 |
| 돌려주는 값 | 새 리스트 | `None` |
| 쓰는 곳 | 리스트, 튜플, 딕셔너리, 집합 | 리스트만 |

`prices = prices.sort()`처럼 받으면 `prices`에 `None`만 남아요. `prices.sort()`만 쓰거나 `prices = sorted(prices)`로 써요.

### key는 비교할 값을 따로 만들어요

```
sorted(names, key=len)

names      "latte"  "tea"  "coffee"
len()  →     5        3       6      ← 이 값으로 비교해요
결과       "tea"  "latte"  "coffee"  ← 줄 서는 건 원래 값이에요
```

| 줄 세울 것 | 코드 |
| --- | --- |
| 튜플 둘째 칸 기준 | `sorted(items, key=lambda m: m[1])` |
| 많은 순, 같으면 이름순 | `sorted(sales, key=lambda m: (-m[1], m[0]))` |
| 딕셔너리 키를 값 순서로 | `sorted(d, key=d.get)` |
| 딕셔너리 짝을 값 순서로 | `sorted(d.items(), key=lambda kv: kv[1])` |
| 값이 가장 큰 키 | `max(d, key=d.get)` |

`key`에는 괄호 없이 함수 이름이나 `lambda`를 넣어요.

## 실습

VS Code에서 `hello-uv` 폴더를 열고 `basics.ipynb`를 열어요. 오른쪽 위 커널이 `.venv`인지 본 뒤, 아래 코드를 셀 하나에 한 덩어리씩 적고 `Shift+Enter`로 실행해요. 주석(`#` 뒤)은 실제 출력이에요.

### 1. max(sales)가 tea인 이유

```python
sales = {"coffee": 12, "latte": 30, "cake": 8, "tea": 15}
print(sorted(sales))
print(max(sales))
print(max(sales, key=sales.get))
# ['cake', 'coffee', 'latte', 'tea']
# tea
# latte
```

### 2. sorted와 sort

```python
prices = [6500, 4500, 5000]
a = sorted(prices)
print(a)
print(prices)
prices.sort()
print(prices)
# [4500, 5000, 6500]
# [6500, 4500, 5000]
# [4500, 5000, 6500]
```

```python
prices = [6500, 4500, 5000]
prices = prices.sort()
print(prices)
# None
```

### 3. key로 비교 방법 바꾸기

```python
names = ["latte", "tea", "coffee", "mocha"]
print(sorted(names, key=len))
print(sorted(["Latte", "cake", "Tea", "coffee"]))
print(sorted(["Latte", "cake", "Tea", "coffee"], key=str.lower))
print(sorted(["10", "9", "100"], key=int))
# ['tea', 'latte', 'mocha', 'coffee']
# ['Latte', 'Tea', 'cake', 'coffee']
# ['cake', 'coffee', 'Latte', 'Tea']
# ['9', '10', '100']
```

### 4. 튜플 정렬과 두 기준

```python
sales = [("latte", 30), ("cake", 8), ("coffee", 30), ("tea", 15)]
print(sorted(sales, key=lambda m: m[1], reverse=True))
print(sorted(sales, key=lambda m: (-m[1], m[0])))
# [('latte', 30), ('coffee', 30), ('tea', 15), ('cake', 8)]
# [('coffee', 30), ('latte', 30), ('tea', 15), ('cake', 8)]
```

### 5. 딕셔너리 정렬과 max, min

```python
sales = {"coffee": 12, "latte": 30, "cake": 8, "tea": 15}
print(sorted(sales.items(), key=lambda kv: kv[1], reverse=True))
print(sorted(sales, key=sales.get, reverse=True))
print(min(sales, key=sales.get))
print(sum(sales.values()) / len(sales))
print(sorted(sales, key=sales.get, reverse=True)[:3])
# [('latte', 30), ('tea', 15), ('coffee', 12), ('cake', 8)]
# ['latte', 'tea', 'coffee', 'cake']
# cake
# 16.25
# ['latte', 'tea', 'coffee']
```

```python
prices = [4500, 5000, 6500, 3000]
big = list(filter(lambda p: p > 10000, prices))
print(big)
print(max(big, default=0))
# []
# 0
```

### 6. 실습: 판매 순위표

```python
sales = {"coffee": 12, "latte": 30, "cake": 8, "tea": 15, "juice": 15}
rank = sorted(sales.items(), key=lambda kv: (-kv[1], kv[0]))
for i, kv in enumerate(rank[:3], 1):
    print(f"{i}위 {kv[0]:<6}{kv[1]:>3}잔")
# 1위 latte  30잔
# 2위 juice  15잔
# 3위 tea    15잔
```

다 했으면 `Ctrl+S`(Mac `Cmd+S`)로 저장해요.

## 명령어 요약

| 코드 | 하는 일 |
| --- | --- |
| `sorted(xs)` | 줄 세운 새 리스트. 원본은 그대로 |
| `xs.sort()` | 원본을 줄 세우고 `None`을 돌려줘요 |
| `reverse=True` | 큰 것부터 |
| `key=len` `key=str.lower` `key=int` | 길이, 소문자로 바꾼 글자, 숫자로 바꾼 값으로 비교 |
| `"Latte".lower()` | 글자를 소문자로 바꾸기 |
| `key=lambda m: m[1]` | 튜플 둘째 칸으로 비교 |
| `key=lambda m: (-m[1], m[0])` | 숫자는 큰 순, 같으면 이름순 |
| `sorted(d, key=d.get)` | 딕셔너리 키를 값 순서로 |
| `sorted(d.items(), key=lambda kv: kv[1])` | 딕셔너리 짝을 값 순서로 |
| `max(d, key=d.get)` `min(d, key=d.get)` | 값이 가장 큰 키, 가장 작은 키 |
| `max(xs, default=0)` | 비어 있으면 0 |
| `sorted(...)[:3]` | 상위 3개 |

## 문제 해결

| 증상 | 원인과 해결 |
| --- | --- |
| `max(sales)`가 엉뚱한 이름이에요 | 딕셔너리는 키끼리 abc 순으로 비교해요. `max(sales, key=sales.get)`으로 써요 |
| `prices`를 찍으니 `None`이에요 | `prices = prices.sort()`로 받았어요. `prices.sort()`만 써요 |
| `['10', '100', '9']` 순서예요 | 글자는 앞 글자부터 비교해요. `key=int`를 넣어요 |
| `TypeError: '<' not supported between instances of 'str' and 'int'` | 숫자와 글자를 섞었어요. 타입을 맞추거나 `key=int`를 넣어요 |
| `TypeError: len() takes exactly one argument (0 given)` | `key`에 괄호를 붙였어요. `key=len`처럼 이름만 적어요 |
| `NameError: name 'kv' is not defined` | `lambda kv:`를 빠뜨렸어요. `key=lambda kv: kv[1]`로 써요 |
| `TypeError: sorted expected 1 argument, got 2` | `key=`를 빠뜨렸어요. `sorted(sales, key=sales.get)`으로 써요 |
| `ValueError: max() iterable argument is empty` | 빈 리스트에 `max`를 썼어요. `default=0`을 넣어요 |

순서가 기대와 다르면 `list(map(len, names))`처럼 key 함수의 결과를 먼저 찍어 봐요.

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분 (gen.py가 만들어요)
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py           모든 장과 deck.json 생성 (노트북 셀, key 파이프 그림, 튜플 칸)
  demo.sh          hello-uv를 새로 만들고 노트북 셀을 실제로 실행해 출력 확인
  run_nb.py        셀을 프로젝트 커널로 실행 (demo.sh가 불러요)
python-sorting-slides.html  배포용 HTML
python-sorting-slides.pdf   강사용 PDF
```

검사, HTML, PDF를 만드는 공용 도구(`check.js`, `build_player.js`, `export.js`)는 맨 위 [tools/](../tools)에 한 벌만 있어요. 명령은 이 폴더에서 쳐요.

슬라이드 HTML을 직접 고치지 말고 스크립트를 고친 뒤 다시 만들어요.

```bash
bash tools/demo.sh /tmp/sorting-demo > /tmp/sorting-demo.log 2>&1
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/build_player.js slides python-sorting-slides.html
node ../tools/export.js slides python-sorting-slides.pdf
```

셀 출력은 `tools/demo.sh`가 hello-uv(Python 3.14.6)를 만들고 `tools/run_nb.py`로 그 커널에서 실제로 실행한 결과예요. 파트마다 새 커널에서 위에서부터 차례로 실행해서, 셀 번호가 파트마다 [1]부터 시작해요. 오류는 Traceback 위쪽 줄을 빼고 마지막 줄만 옮겼어요.

범위: `.lower()`는 이 챕터에서 처음 보여 줘요. `operator.itemgetter`, `functools.cmp_to_key`, `zip()`, 딕셔너리 컴프리헨션(23)은 다루지 않아요.

</details>

---

<!-- curriculum:nav -->

[← 이전: 21 · 함수 3 (lambda, map, filter)](../21-python-lambda) · [커리큘럼](../README.md) · [다음: 23 · 리스트 컴프리헨션 →](../23-python-comprehension)

<!-- /curriculum:nav -->
