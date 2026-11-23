# 45 · NumPy와 pandas 맛보기

> 머신러닝 기초 수업 전에 한 실습을 한 챕터로 정리했어요. 한 달 지출 12건을 리스트, NumPy 배열, pandas 표로 차례로 옮기면서 합계, 평균, 고르기, 정렬, 분류별 합계를 구해요. 9의 uv, 10의 VS Code 노트북, 13~23의 파이썬, 36~39의 SQL을 이어서 써요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/45-numpy-pandas/numpy-pandas-slides.html) | [44 · 파이썬에서 PostgreSQL 쓰기 (psycopg)](../44-python-postgres) | [46 · 데이터 정리하기 (타이타닉 전처리)](../46-data-cleaning) |

<!-- /curriculum:top -->

## 학습 목표

- `uv add numpy pandas`로 패키지를 넣고 VS Code 노트북에서 `import numpy as np`, `import pandas as pd`로 불러요.
- 리스트 `* 2`와 배열 `* 2`가 어떻게 다른지 설명하고, 배열에 `sum` `mean` `min` `max`를 물어요.
- `arr >= 10000`이 칸마다 True, False를 낸다는 것과 `arr[조건]`으로 값을 고르는 법을 알아요.
- 딕셔너리로 DataFrame을 만들고, `spend["열"]`, `spend[["열", "열"]]`, `spend[조건]`으로 열과 행을 골라요.
- 조건 두 개를 `(조건1) & (조건2)`로 잇고, `sort_values`로 큰 순서로 세워요.
- 새 열을 계산해서 더하고, `loc[행 번호, 열 이름]`으로 칸 하나를 고쳐요.
- `groupby`로 분류마다 합계를 내고, `value_counts`로 값마다 횟수를 세요.

## 시작하기 전에

| 할 일 | 챕터 |
| --- | :---: |
| `uv init`, `uv add`, `uv add --dev` | 09 |
| VS Code 노트북, 커널 고르기, `Shift+Enter` | 10 |
| 리스트, `for`, f-string | 13 |
| 딕셔너리(`{키: 값}`, `d["키"]`) | 15 |
| `range(len())`, `if` | 17, 18 |
| `sorted(..., reverse=True)`, 컴프리헨션 | 22, 23 |
| `import 모듈 as 별명` | 28 |
| `WHERE`, `ORDER BY`, `GROUP BY` (비교용) | 36~39 |

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 3 | `ml-basics` 프로젝트 만들고 numpy, pandas 넣기 |
| 1 · 왜 필요한가 | 4~6 | 리스트로 식비 합계 구하기, 리스트에서 배열과 표로, 가장 짧은 NumPy |
| 2 · NumPy 배열 | 7~12 | 리스트와 배열의 `* 2`와 `+ 500`, `sum` `mean` `min` `max`, `shape` `dtype`, True/False 배열, `arr[조건]` |
| 3 · pandas 표 고르기 | 13~20 | DataFrame 만들기, `shape` `head`, 열 하나와 여러 개, 조건 필터, `&`, `sort_values` |
| 4 · 열 더하고 묶기 | 21~25 | `/`와 `//`, 새 열, `loc`로 고치기, `groupby`, `value_counts` |
| 5 · 비교와 오류 | 26~30 | 리스트, 배열, 표 비교표, SQL 비교표, `and`와 괄호 오류, `KeyError`, `ModuleNotFoundError` |
| 6 · 실제 상황 | 31~33 | 가장 많이 쓴 곳 세 군데, 식비 예산 비교, 1만 원 넘는 지출 세기 |
| 정리 | 34~35 | 막힐 때 보는 표, 한 장 요약 |

## 핵심 개념

```
파이썬 리스트        NumPy 배열              pandas DataFrame
[3200, 1500]   ──▶  [3200 1500]       ──▶   열 이름이 붙은 표
아무 값이나          숫자 칸을 한 번에 계산    숫자 열 하나하나가 배열
```

- 리스트 `* 2`는 같은 리스트를 이어 붙이고, 배열 `* 2`는 칸마다 2를 곱해요. 배열은 `+`, `-`, `/`, `//`도 칸마다 해요.
- 배열에 비교를 하면 칸마다 True, False가 담긴 배열이 나와요. 그 배열을 대괄호에 넣으면 True 자리만 남아요.
- DataFrame은 딕셔너리로 만들어요. 키가 열 이름, 값 리스트가 그 열의 칸이에요. 왼쪽 0부터 11은 pandas가 붙인 행 번호(index)예요.
- `spend["열"]`은 행 번호가 붙은 한 줄짜리(Series), `spend[["열", "열"]]`은 고른 열만 남은 표예요.
- 조건 두 개는 `and` 대신 `&`로 잇고, 조건마다 괄호로 감싸요.
- 계산해서 만든 열은 원래 열을 고쳐도 저절로 바뀌지 않아요. 계산 줄을 다시 실행해요.

## 실습

### 1. 프로젝트 만들기

```bash
uv init ml-basics
cd ml-basics
uv add numpy pandas
uv add --dev ipykernel
```

```
Initialized project `ml-basics` at `/home/kim/ml-basics`
Using CPython 3.13.18 interpreter at: /usr/local/bin/python3.13
Creating virtual environment at: .venv
Resolved 5 packages in 7ms
Installed 4 packages in 16ms
 + numpy==2.5.5
 + pandas==3.1.1
 + python-dateutil==4.0.0
 + tzdata==2026.6
```

`uv add --dev ipykernel`의 출력은 길어서 줄였어요. 경로, 시간, 버전 숫자는 컴퓨터마다 달라요. VS Code로 `ml-basics` 폴더를 열고 `pandas.ipynb`를 만든 뒤, 오른쪽 위 커널에서 `.venv`를 골라요(10).

### 2. 지출 데이터 넣기

첫 셀에 리스트 세 개를 적고 실행해요. 같은 번호끼리 한 번의 지출이에요.

```python
shops = ["편의점", "버스", "영화관", "분식집", "온라인쇼핑", "카페",
         "음원앱", "버스", "편의점", "웹툰", "온라인쇼핑", "분식집"]
categories = ["식비", "교통", "문화", "식비", "쇼핑", "식비",
              "문화", "교통", "식비", "문화", "쇼핑", "식비"]
amounts = [3200, 1500, 15000, 6500, 32000, 4800,
           10900, 1500, 2700, 3000, 18500, 7000]
```

### 3. NumPy 배열

```python
import numpy as np

arr = np.array(amounts)
print("합계:", arr.sum())
print("평균:", round(arr.mean()))
print(arr[arr >= 10000])
```

```
합계: 106600
평균: 8883
[15000 32000 10900 18500]
```

### 4. pandas 표 만들고 고르기

```python
import pandas as pd

spend = pd.DataFrame({
    "day": [2, 3, 4, 5, 7, 9, 12, 14, 16, 19, 20, 25],
    "shop": shops,
    "category": categories,
    "amount": amounts
})
spend[spend["amount"] >= 10000]
```

```
    day   shop category  amount
2     4    영화관       문화   15000
4     7  온라인쇼핑       쇼핑   32000
6    12    음원앱       문화   10900
10   20  온라인쇼핑       쇼핑   18500
```

VS Code는 이 결과를 줄무늬 표로 그려요. 위 글자는 같은 결과를 글자로 옮긴 거예요.

```python
spend[(spend["category"] == "식비") & (spend["amount"] >= 5000)]
```

```
    day shop category  amount
3     5  분식집       식비    6500
11   25  분식집       식비    7000
```

### 5. 열 더하고 묶기

```python
spend["point"] = spend["amount"] // 100
spend.groupby("category")["amount"].sum().sort_values(ascending=False)
```

```
category
쇼핑    50500
문화    28900
식비    24200
교통     3000
Name: amount, dtype: int64
```

```python
spend["category"].value_counts()
```

```
category
식비    5
문화    3
교통    2
쇼핑    2
Name: count, dtype: int64
```

`value_counts()`는 처음부터 많은 순서로 나와요. 수업 코드처럼 뒤에 `sort_values(ascending=False)`를 붙이지 않아도 돼요.

## 명령어 요약

| 명령 | 하는 일 |
| --- | --- |
| `uv add numpy pandas` | 두 패키지를 프로젝트에 넣기 |
| `np.array(리스트)` | 리스트를 배열로 바꾸기 |
| `arr.sum()` `arr.mean()` `arr.min()` `arr.max()` | 합계, 평균, 최소, 최대 |
| `arr.shape` `arr.dtype` | 칸 수, 칸에 든 값의 종류 |
| `arr[arr >= 10000]` | 조건에 맞는 칸만 고르기 |
| `pd.DataFrame({열: 리스트})` | 딕셔너리로 표 만들기 |
| `spend.shape` `spend.head(3)` | 행과 열 수, 앞 세 줄 |
| `spend["열"]` | 열 하나(Series) |
| `spend[["열", "열"]]` | 열 여러 개(표) |
| `spend[조건]` | 조건이 True인 행만 |
| `spend[(조건1) & (조건2)]` | 두 조건을 모두 만족하는 행 |
| `spend.sort_values(by="열", ascending=False)` | 큰 순서로 세우기 |
| `spend["새 열"] = 계산` | 새 열 더하기 |
| `spend.loc[행 번호, "열"] = 값` | 칸 하나 고치기 |
| `spend.groupby("열")["값 열"].sum()` | 분류마다 합계 |
| `spend["열"].value_counts()` | 값마다 횟수, 많은 순 |

## 문제 해결

| 메시지 | 원인 | 해결 |
| --- | --- | --- |
| `ModuleNotFoundError: No module named 'pandas'` | 프로젝트에 pandas를 넣지 않았거나 커널이 다른 파이썬이에요 | `uv add numpy pandas` 뒤 노트북 Restart, 커널이 `.venv`인지 확인 |
| `AttributeError: 'list' object has no attribute 'mean'` | 리스트에 배열 메서드를 불렀어요 | `np.array(리스트)`로 바꾼 배열에 묻기 |
| `TypeError: can only concatenate list (not "int") to list` | 리스트에 숫자를 더했어요 | 배열로 바꾸면 칸마다 더해져요 |
| `ValueError: The truth value of a Series is ambiguous. ...` | 조건 두 개를 `and`로 이었어요 | `(조건1) & (조건2)` |
| `TypeError: Cannot perform 'rand_' with a dtyped [int64] array and scalar of type [bool]` | `&` 양쪽 조건에 괄호가 없어요 | 조건마다 괄호로 감싸기 |
| `KeyError: 'amout'` | 열 이름이 틀렸어요 | `spend.head()`로 머리글 확인 |
| `KeyError: ('shop', 'amount')` | 열 두 개를 대괄호 한 겹에 적었어요 | `spend[["shop", "amount"]]` |
| `NameError: name 'spend' is not defined` | 앞 셀을 실행하지 않았어요 | 리스트 셀과 DataFrame 셀부터 차례로 실행 |
| 금액을 고쳤는데 point가 그대로예요 | 계산한 열은 저절로 바뀌지 않아요 | point 계산 줄을 다시 실행 |

## 강사용

<details>
<summary>수업 코드에서 고친 곳</summary>

- 평균을 찍는 줄의 이름표가 "합계"로 적혀 있어서 "평균"으로 고쳤어요(2파트, 3파트).
- `shops`와 `categories`를 두 번 적은 셀은 한 번만 적었어요.
- 첫 `amounts`가 13개, `shops`가 12개로 어긋나 있어서 12개로 맞췄어요.
- 쓰이지 않던 `arr * 2` 줄은 리스트와 배열 비교 장으로 옮겼어요.
- `value_counts()` 뒤의 `sort_values(ascending=False)`는 결과가 같아서 뺐어요.
- 리스트 합계의 `zip()`은 아직 배우지 않아서 `range(len())`와 `if`로 바꾸고, `zip()`은 참고로 읽기만 해요.

</details>

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json                 슬라이드 순서와 파트 구분
  *.html                    한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py                    이 챕터의 장 생성
  demo.sh                   uv 프로젝트를 만들고 노트북 셀을 실제로 실행
  run_nb.py                 demo.sh가 부르는 셀 실행기 (nbclient)
  demo.log                  슬라이드에 옮긴 실제 출력
numpy-pandas-slides.html    배포용 HTML
numpy-pandas-slides.pdf     강사용 PDF
```

출력은 `bash tools/demo.sh /tmp/새폴더 > tools/demo.log`로 다시 만들어요. 실제 uv, numpy, pandas, ipykernel 커널에서 셀을 실행해요. 공용 도구는 맨 위 [tools/](../tools)에 있어요. 명령은 이 폴더에서 쳐요.

```bash
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/boxcheck.js slides
node ../tools/build_player.js slides numpy-pandas-slides.html
node ../tools/export.js slides numpy-pandas-slides.pdf
```

</details>

---

<!-- curriculum:nav -->

[← 이전: 44 · 파이썬에서 PostgreSQL 쓰기 (psycopg)](../44-python-postgres) · [커리큘럼](../README.md) · [다음: 46 · 데이터 정리하기 (타이타닉 전처리) →](../46-data-cleaning)

<!-- /curriculum:nav -->
