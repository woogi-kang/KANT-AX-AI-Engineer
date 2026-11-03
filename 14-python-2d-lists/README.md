# 14 · 파이썬 기초 3 (in, 2차원 리스트)

> 13에서 리스트와 튜플에 값을 담고 `for`로 하나씩 꺼냈어요. 이번에는 `in`과 `not in`으로 값이 들어 있는지 True, False로 물어요. 그다음 리스트 안에 리스트를 넣은 2차원 리스트로 성적표와 좌석표 같은 표 모양 데이터를 다뤄요. 모든 예제는 12, 13에서 쓰던 노트북에 이어서 적고 실행해요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/14-python-2d-lists/python-2d-lists-slides.html) | [13 · 파이썬 기초 2 (문자열, 리스트, for)](../13-python-strings-lists) | [15 · 파이썬 기초 4 (딕셔너리)](../15-python-dict) |

<!-- /curriculum:top -->

## 학습 목표

이 챕터를 마치면 다음을 할 수 있어요.

- 리스트, 튜플, 문자열에서 `in`과 `not in`으로 값이 들어 있는지 True, False로 물어요.
- `in`의 결과를 `and`, `or`와 섞어 쓰고, 변수에 담아 둬요.
- `in`은 바깥 한 겹만 본다는 걸 알고, 안쪽은 `orders[2]`처럼 꺼낸 뒤 물어요.
- 2차원 리스트를 만들고 `scores[1]`(행), `scores[1][2]`(칸)로 꺼내요.
- `len(scores)`로 행 수, `len(scores[0])`로 열 수를 세요.
- `for row in scores:`로 행마다 `sum`, `max`를 구하고, `append`로 열 하나를 모아요.
- 행을 더하고(`scores.append([...])`) 열을 더해요(`for` 안에서 `row.append(0)`).
- `for name, kor, eng, math in students:`로 성적표를 찍어요.
- `[[0] * 3] * 3` 함정을 알고, `IndexError`, `ValueError`의 마지막 줄을 읽고 고쳐요.

## 시작하기 전에

12, 13에서 쓰던 `hello-uv`의 `basics.ipynb`와 그때 배운 내용을 그대로 써요.

| 할 일 | 슬라이드 |
| --- | :---: |
| VS Code에 Python, Jupyter 확장 설치, `uv add --dev ipykernel`, 커널로 `.venv` 고르기 | 09 · 25–27쪽 |
| 비교와 `True`·`False`, `and` `or` `not` | 12 · 4파트 |
| f-string과 칸 수, 소수점 맞추기 | 13 · 1파트 |
| 리스트와 튜플, `orders[1][0]`, `append` `join` `count`, `for`와 `+=` | 13 · 2파트 |

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1–3 | 표지, 오늘의 순서, `basics.ipynb` 다시 열기 |
| 1. in과 not in | 4–7 | 리스트에서 `in`과 `not in`, 튜플과 문자열의 `in`(숫자와 글자, 붙어 있는 글자 조각, 대소문자), `and` `or`와 섞기, 한 겹만 보는 `in` |
| 2. 2차원 리스트 | 8–20 | 리스트 안의 리스트와 `len`, `[행][열]`로 꺼내기, 칸과 행 바꾸기, `for`로 행마다 `sum` `max`, 열 하나 모으기, 전체 합계와 평균, 이름이 들어간 성적표, 2차원 리스트의 `in`, 행과 칸 자르기, 행과 열 더하기, 좌석표, `[[0] * 3] * 3` 함정, 자주 나는 오류 |
| 정리 | 21–22 | 막힐 때, 한 장 요약 |

## 핵심 개념

### in과 not in

`in`은 왼쪽 값이 오른쪽에 들어 있는지 물어요. 답은 `True`나 `False`예요. `not in`은 반대예요.

| 코드 | 결과 | 뜻 |
| --- | --- | --- |
| `"latte" in menu` | `True` | menu에 latte가 있어요 |
| `"juice" not in menu` | `True` | menu에 juice가 없어요 |
| `"4500" in ("coffee", 4500, 2)` | `False` | 글자 `"4500"`과 숫자 `4500`은 달라요 |
| `"th" in "python"` | `True` | 문자열에서는 붙어 있는 글자 조각을 찾아요 |
| `"P" in "python"` | `False` | 대문자와 소문자를 구분해요 |
| `"cake" in orders` | `False` | 바깥에는 튜플만 있어요. 한 겹만 봐요 |
| `"cake" in orders[2]` | `True` | 한 겹 꺼낸 뒤 물으면 찾아요 |

`not "juice" in menu`도 결과는 같지만 `"juice" not in menu`가 읽기 쉬워요.

### 2차원 리스트

```python
scores = [[90, 85, 77],
          [70, 95, 88],
          [60, 75, 99]]
```

| 코드 | 결과 | 뜻 |
| --- | --- | --- |
| `scores[1]` | `[70, 95, 88]` | 1행 통째로 |
| `scores[1][2]` | `88` | 1행의 2열. 앞 번호가 행, 뒤 번호가 열 |
| `scores[-1][-1]` | `99` | 마지막 행의 마지막 열 |
| `len(scores)` | `3` | 행 수 |
| `len(scores[0])` | `3` | 열 수 |
| `scores[:2]` | 0행, 1행 | 바깥을 자르면 행 |
| `scores[1][:2]` | `[70, 95]` | 한 행을 꺼낸 뒤 칸을 잘라요 |

열 하나는 바로 꺼내는 문법이 없어서 `for`로 행마다 같은 번호를 모아요. 빈 표는 `[[0] * 3] * 3` 대신 행을 하나씩 직접 적어요. `* 3`으로 만들면 세 행이 같은 리스트라서 한 칸만 바꿔도 모든 행이 바뀌어요.

## 실습

VS Code에서 `hello-uv` 폴더를 열고 `basics.ipynb`를 열어요. 오른쪽 위 커널이 `.venv`인지 본 뒤, 아래 코드를 셀 하나에 한 덩어리씩 적고 `Shift+Enter`로 실행해요. 주석(`#` 뒤)은 실제 출력이에요.

### 1. in과 not in

```python
menu = ["coffee", "latte", "cake"]
print("latte" in menu)          # True
print("juice" in menu)          # False
print("juice" not in menu)      # True
print("latte" not in menu)      # False
```

```python
word = "python"
print("th" in word)      # True
print("pt" in word)      # False
print("P" in word)       # False
print("z" not in word)   # True
```

```python
has_both = "latte" in menu and "cake" in menu
print(has_both)                             # True
print("juice" in menu or "tea" in menu)     # False
```

```python
orders = [("coffee", 4500, 2), ("latte", 5000, 1), ("cake", 6500, 3)]
print(("cake", 6500, 3) in orders)   # True
print("cake" in orders)              # False
print("cake" in orders[2])           # True
```

### 2. 2차원 리스트

```python
scores = [[90, 85, 77],
          [70, 95, 88],
          [60, 75, 99]]
print(len(scores))       # 3
print(len(scores[0]))    # 3
print(scores[1][2])      # 88
scores[0][1] = 100
scores[2] = [65, 80, 90]
print(scores)            # [[90, 100, 77], [70, 95, 88], [65, 80, 90]]
```

```python
for row in scores:
    print(row, "합계:", sum(row), "최고:", max(row))
# [90, 100, 77] 합계: 267 최고: 100
# [70, 95, 88] 합계: 253 최고: 95
# [65, 80, 90] 합계: 235 최고: 90
```

```python
eng = []
for row in scores:
    eng.append(row[1])
print(eng)          # [100, 95, 80]

total = 0
count = 0
for row in scores:
    total += sum(row)
    count += len(row)
print("전체 합계:", total)          # 전체 합계: 755
print(f"평균: {total / count:.1f}")  # 평균: 83.9
```

```python
students = [["kim", 90, 85, 77],
            ["lee", 70, 95, 88],
            ["park", 60, 75, 99]]
print(f"{'name':<6}{'kor':>5}{'eng':>5}{'math':>5}")
print("-" * 21)
for name, kor, eng, math in students:
    print(f"{name:<6}{kor:>5}{eng:>5}{math:>5}")
# name    kor  eng math
# ---------------------
# kim      90   85   77
# lee      70   95   88
# park     60   75   99
```

```python
seats = [["O", "O", "X", "O"],
         ["X", "O", "O", "O"],
         ["O", "X", "X", "O"]]
seats[0][1] = "X"
for row in seats:
    print(" ".join(row))
# O X X O
# X O O O
# O X X O
print(seats[2].count("X"))          # 2
print(len(seats) * len(seats[0]))   # 12
```

다 했으면 `Ctrl+S`(Mac `Cmd+S`)로 저장해요.

## 문제 해결

| 증상 | 원인과 해결 |
| --- | --- |
| `TypeError: 'in <string>' requires string as left operand, not int` | 문자열 안에 숫자가 있는지 물었어요. `"3" in word`처럼 글자로 물어요 |
| `IndexError: list index out of range` | 행이나 열 번호가 넘쳤어요. 행 수는 `len(scores)`, 열 수는 `len(scores[0])`로 확인해요 |
| `ValueError: too many values to unpack (expected 3)` | 행의 값 개수보다 변수가 적어요. 변수 개수를 값 개수에 맞춰요 |
| 한 칸만 바꿨는데 모든 행이 바뀌어요 | `[[0] * 3] * 3`으로 만들었어요. 행을 하나씩 직접 적어요 |
| `90 in students`가 `False`예요 | `in`은 바깥 한 겹만 봐요. `90 in students[0]`처럼 행을 꺼낸 뒤 물어요 |
| `"P" in word`가 `False`예요 | 대문자와 소문자가 달라요 |

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분 (gen.py가 만들어요)
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py           모든 장과 deck.json 생성 (노트북 셀, 리스트 칸, 2차원 표 그림)
  demo.sh          hello-uv를 새로 만들고 노트북 셀을 실제로 실행해 출력 확인
  run_nb.py        셀을 프로젝트 커널로 실행 (demo.sh가 불러요)
python-2d-lists-slides.html  배포용 HTML
python-2d-lists-slides.pdf   강사용 PDF
```

검사, HTML, PDF를 만드는 공용 도구(`check.js`, `build_player.js`, `export.js`)는 맨 위 [tools/](../tools)에 한 벌만 있어요. 명령은 이 폴더에서 쳐요.

슬라이드 HTML을 직접 고치지 말고 스크립트를 고친 뒤 다시 만들어요.

```bash
bash tools/demo.sh /tmp/2d-lists-demo > /tmp/2d-lists-demo.log 2>&1
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/build_player.js slides python-2d-lists-slides.html
node ../tools/export.js slides python-2d-lists-slides.pdf
```

셀 출력은 `tools/demo.sh`가 hello-uv를 만들고 `tools/run_nb.py`로 그 커널에서 실제로 실행한 결과예요. 파트마다 새 커널에서 위에서부터 차례로 실행해서, 셀 번호가 파트마다 [1]부터 시작해요. 2파트는 앞 셀에서 바꾼 `scores`를 계속 써요. 오류는 Traceback 위쪽 줄을 빼고 마지막 줄만 옮겼어요. `if`는 아직 배우지 않아서 쓰지 않았고, `zip`과 `range`도 쓰지 않았어요. 13의 2파트 찾기 장에 나온 `in`을 이 챕터 1파트에서 `not in`과 함께 정리해요.

</details>

---

<!-- curriculum:nav -->

[← 이전: 13 · 파이썬 기초 2 (문자열, 리스트, for)](../13-python-strings-lists) · [커리큘럼](../README.md) · [다음: 15 · 파이썬 기초 4 (딕셔너리) →](../15-python-dict)

<!-- /curriculum:nav -->
