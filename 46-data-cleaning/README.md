# 46 · 데이터 정리하기 (타이타닉 전처리)

> 머신러닝 기초 수업에서 한 실습을 한 챕터로 정리했어요. seaborn에 들어 있는 타이타닉 승객 891명의 표에서 빈칸을 찾아 채우고, 튀는 값과 겹친 행을 찾고, 나이 그래프로 확인해요. 45의 `ml-basics` 프로젝트와 pandas, 13의 문자열 인덱스, 17의 `if`, 36~39의 SQL을 이어서 써요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/46-data-cleaning/data-cleaning-slides.html) · [PDF 받기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/46-data-cleaning/data-cleaning-slides.pdf) | [45 · NumPy와 pandas 맛보기](../45-numpy-pandas) | [47 · 그래프 그리기와 연습 데이터 만들기](../47-plot-data) |

<!-- /curriculum:top -->

## 학습 목표

- `sns.load_dataset("titanic")`으로 연습용 표를 불러오고 `info()`, `describe()`로 훑어봐요.
- `isnull().sum()`으로 열마다 빈칸 수를 세고, `df.loc[조건, 열 리스트]`로 빈칸인 행을 직접 봐요.
- 숫자 빈칸은 평균이나 중앙값, 글자 빈칸은 최빈값 `mode()[0]`으로 `fillna`하고 결과를 다시 담아요.
- 같은 정보가 든 다른 열에서 `.str[0]`으로 값을 가져오고, category 열은 `cat.add_categories`로 칸을 먼저 늘려요.
- `quantile`로 Q1, Q3를 구하고 IQR의 1.5배 울타리 밖 행을 `|`로 골라요. 튀는 값은 누구인지 보고 지울지 정해요.
- `duplicated()`로 겹친 행을 세고, 같은 기록인지 확인한 뒤에 지워요.
- 운영체제에 맞는 한글 글꼴을 정하고 `ax.hist`로 나이 분포를 그려요.

## 시작하기 전에

| 할 일 | 챕터 |
| --- | :---: |
| `uv add`, `uv add --dev` | 09 |
| VS Code 노트북, 커널 고르기 | 10 |
| 문자열 인덱스 `s[0]`, 슬라이싱 `[:]` | 13 |
| `if`, `elif` | 17 |
| `x, y = 함수()` | 19 |
| `import 모듈 as 별명` | 28 |
| `IS NULL`, `UPDATE`, `DELETE`, `GROUP BY` (비교용) | 36~39 |
| `ml-basics` 프로젝트, DataFrame, `df[조건]`, `&`, `loc`, `value_counts` | 45 |

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 3 | `uv add seaborn matplotlib`, `titanic.ipynb` 만들기 |
| 1 · 왜 필요한가 | 4~6 | 빈칸, 튀는 값, 겹친 행이 섞인 표, 정리 다섯 단계, 표 불러와 크기 보기 |
| 2 · 훑어보고 빈칸 찾기 | 7~10 | `info()`, `describe()`, `isnull().sum()`, `loc[조건, 열]` |
| 3 · 빈칸 채우기 | 11~16 | 평균과 중앙값, `fillna`와 다시 담기, `value_counts(dropna=False)`, `mode()[0]`, `.str[0]`, category |
| 4 · 튀는 값과 중복 | 17~22 | `quantile`, IQR 울타리, `|`로 고르기, 512만 지우기, `duplicated()`, 지우기 전에 확인 |
| 5 · 그래프와 오류 | 23~29 | 한글 글꼴, `ax.hist`, SQL 비교표, category 오류, 다시 담지 않은 `fillna`, `[0]` 빠진 `mode()`, 채우면 느는 중복 |
| 6 · 실제 상황 | 30~32 | 튀는 요금 116명은 누구인지, 평균으로 채운 뒤의 그래프, 정리를 한 셀로 모으기 |
| 정리 | 33~34 | 막힐 때 보는 표, 상황별로 고르는 방법 |

## 핵심 개념

```
훑어보기 ──▶ 빈칸 채우기 ──▶ 튀는 값 ──▶ 중복 찾기 ──▶ 그래프
info()       isnull()        quantile()    duplicated()   ax.hist()
describe()   fillna()        IQR × 1.5
891행 × 15열                                              888행 × 15열
```

- `isnull()`은 칸마다 비었으면 True예요. `sum()`을 붙이면 True를 1로 세서 열마다 빈칸 수가 나와요.
- `fillna`는 채운 새 열을 돌려줘요. `df["age"] = df["age"].fillna(값)`처럼 다시 담아야 바뀌어요.
- 평균은 큰 값에 끌려가고 중앙값은 가운데 값이에요. 요금처럼 큰 값이 섞인 열은 중앙값이 안전해요.
- 글자 열은 가장 많이 나온 값(최빈값)으로 채워요. `mode()`는 Series라서 `[0]`으로 값 하나를 꺼내요.
- category 열은 들어갈 값을 칸 목록으로 정해 둔 열이에요. 새 값은 `cat.add_categories`로 칸부터 늘려요.
- IQR은 Q3 − Q1이에요. Q3 + 1.5 × IQR보다 크거나 Q1 − 1.5 × IQR보다 작으면 튀는 값으로 봐요. 튀는 값이 틀린 값은 아닐 수 있어요.
- `duplicated()`는 앞에 나온 행과 모든 칸이 같은 행을 찾아요. 이 표에는 이름 열이 없어서 다른 승객도 같은 행처럼 보여요.

## 실습

### 1. 패키지 더하기

45의 `ml-basics` 폴더에서 쳐요.

```bash
cd ml-basics
uv add seaborn matplotlib
```

```
Resolved 44 packages in 15ms
Installed 8 packages in 7ms
 + contourpy==1.4.0
 + cycler==0.12.1
 + fonttools==4.68.0
 + kiwisolver==1.5.1
 + matplotlib==3.11.2
 + pillow==13.0.0
 + pyparsing==3.3.3
 + seaborn==0.13.2
```

45를 안 했다면 먼저 `uv init ml-basics`, `cd ml-basics`, `uv add numpy pandas`, `uv add --dev ipykernel`을 쳐요. 시간과 버전 숫자는 컴퓨터마다 달라요. VS Code로 `ml-basics` 폴더를 열고 `titanic.ipynb`를 만든 뒤, 오른쪽 위 커널에서 `.venv`를 골라요(10).

### 2. 불러와서 훑어보기

첫 셀은 데이터를 인터넷에서 받아 오니 연결된 채로 실행해요.

```python
import pandas as pd
import seaborn as sns

df = sns.load_dataset("titanic")
df.shape
```

```
(891, 15)
```

```python
df.isnull().sum()
```

```
survived         0
pclass           0
sex              0
age            177
sibsp            0
parch            0
fare             0
embarked         2
class            0
who              0
adult_male       0
deck           688
embark_town      2
alive            0
alone            0
dtype: int64
```

`df.info()`와 `df.describe()`도 셀마다 하나씩 실행해 봐요.

### 3. 빈칸 채우기

```python
mean_age = df["age"].mean()
df.loc[:, "age"] = df["age"].fillna(mean_age)

mode_town = df["embark_town"].mode()[0]
df.loc[:, "embark_town"] = df["embark_town"].fillna(mode_town)
df.loc[:, "embarked"] = df["embark_town"].str[0]

df["deck"] = df["deck"].cat.add_categories("Unknown").fillna("Unknown")
df.isnull().sum().sum()
```

```
np.int64(0)
```

`isnull().sum()`에 `sum()`을 한 번 더 붙이면 표 전체의 빈칸 수예요.

### 4. 튀는 값 찾기

```python
q1 = df["fare"].quantile(0.25)
q3 = df["fare"].quantile(0.75)
iqr = q3 - q1
upper = q3 + 1.5 * iqr
lower = q1 - 1.5 * iqr

outliers = df[(df["fare"] < lower) | (df["fare"] > upper)]
print("튀는 요금:", len(outliers), "명")
outliers["pclass"].value_counts()
```

```
튀는 요금: 116 명
pclass
1    104
3      7
2      5
Name: count, dtype: int64
```

116명 중 104명이 1등석이라 다 지우지 않아요. 혼자 동떨어진 512만 지워요.

```python
before = len(df)
df = df[df["fare"] < 512].copy()
print(before, "=>", len(df))
print("중복 행:", df.duplicated().sum())
```

```
891 => 888
중복 행: 107
```

중복 107줄은 이름 열이 없어서 같아 보이는 다른 승객이 대부분이에요. 세기만 하고 지우지 않아요.

### 5. 나이 그래프

```python
import platform
import matplotlib.pyplot as plt

os_name = platform.system()
if os_name == "Windows":
    plt.rcParams["font.family"] = "Malgun Gothic"
elif os_name == "Darwin":
    plt.rcParams["font.family"] = "AppleGothic"
```

```python
fig, ax = plt.subplots(figsize=(6, 4))
ax.hist(df["age"], bins=20, color="blue", edgecolor="black")
ax.set_title("나이 분포")
ax.set_xlabel("나이(세)")
```

30살 근처 막대가 유난히 높아요. 나이가 비어 있던 177명을 모두 평균 29.7로 채웠기 때문이에요.

## 명령어 요약

| 명령 | 하는 일 |
| --- | --- |
| `uv add seaborn matplotlib` | 연습용 데이터와 그래프 도구 넣기 |
| `sns.load_dataset("titanic")` | 타이타닉 표 내려받기 |
| `df.info()` | 열마다 빈칸이 아닌 칸 수와 타입 |
| `df.describe()` | 숫자 열의 개수, 평균, 사분위수, 최대 |
| `df.isnull().sum()` | 열마다 빈칸 수 |
| `df.loc[조건, ["열", "열"]]` | 조건에 맞는 행의 고른 열 |
| `df["열"].mean()` `df["열"].median()` | 평균, 중앙값 |
| `df["열"] = df["열"].fillna(값)` | 빈칸 채우고 다시 담기 |
| `df["열"].value_counts(dropna=False)` | 빈칸까지 값마다 세기 |
| `df["열"].mode()[0]` | 최빈값 하나 |
| `df["열"].str[0]` | 글자마다 첫 글자 |
| `df["열"].cat.add_categories("새 값")` | category 칸 늘리기 |
| `df["열"].quantile(0.25)` | 줄 세운 값의 25% 자리 |
| `df[(조건1) \| (조건2)]` | 둘 중 하나라도 맞는 행 |
| `df = df[조건].copy()` | 남길 행만 골라 다시 담기 |
| `df.duplicated().sum()` | 겹친 행 수 |
| `df[df.duplicated(keep=False)]` | 겹친 행을 처음 것까지 모두 보기 |
| `fig, ax = plt.subplots(figsize=(6, 4))` | 그림판과 그래프 칸 |
| `ax.hist(df["열"], bins=20)` | 구간 20개 히스토그램 |

## 문제 해결

| 메시지 | 원인 | 해결 |
| --- | --- | --- |
| `ModuleNotFoundError: No module named 'seaborn'` | 프로젝트에 넣지 않았어요 | `uv add seaborn matplotlib` 뒤 노트북 Restart |
| `URLError` 같은 연결 오류 | `load_dataset`이 인터넷에서 데이터를 못 받았어요 | 연결을 확인하고 다시 실행 |
| `TypeError: Cannot setitem on a Categorical with a new category (Unknown), set the categories first` | category 칸 목록에 없는 값을 넣었어요 | `cat.add_categories("Unknown")` 뒤 `fillna` |
| `ChainedAssignmentError: A value is being set on a copy ...` | 열 하나에 `inplace=True`를 썼어요(pandas 3) | `df["열"] = df["열"].fillna(값)` |
| 채웠는데 빈칸 수가 그대로예요 | `fillna` 결과를 다시 담지 않았거나 `mode()`에 `[0]`이 없어요 | 왼쪽에 `df["열"] =`, `mode()[0]` |
| `UserWarning: Glyph ... missing from font(s) DejaVu Sans.` | 그래프 한글 글꼴을 정하지 않았어요 | 운영체제 글꼴 셀을 먼저 실행 |
| 고르기 결과가 0행이에요 | 또는 자리에 `&`를 썼어요 | `(조건1) \| (조건2)` |
| 채운 뒤 중복 수가 늘었어요 | 원래 있는 값(중앙값 등)으로 채워서 다른 행과 같아졌어요 | 채운 뒤 `duplicated()`를 다시 세고, 지우기 전에 같은 기록인지 확인 |

## 강사용

<details>
<summary>수업 코드와 다르게 보여 준 곳</summary>

- 쓰이지 않던 `import numpy as np`와 버전 출력은 뺐어요.
- `duplicated()`는 빈칸끼리도 같은 값으로 봐서 원본 그대로도 107이에요. 평균으로 채워도 107이고, 중앙값 28로 채우면 110이에요. 그래서 "채우면 중복이 늘 수 있다"는 중앙값으로 보여 줘요.
- pandas 3부터 Copy-on-Write가 기본이라 `.copy()`를 빼도 `SettingWithCopyWarning`이 나지 않아요. 수업 코드처럼 붙여 두되, 오류 장은 실제로 나는 `ChainedAssignmentError`로 보여 줘요.
- 그래프 그림은 리눅스에서 만들어서 맑은 고딕 대신 나눔고딕으로 그렸어요.

</details>

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json                  슬라이드 순서와 파트 구분
  *.html                     한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py                     이 챕터의 장 생성
  demo.sh                    uv 프로젝트를 만들고 노트북 셀을 실제로 실행
  run_nb.py                  demo.sh가 부르는 셀 실행기 (nbclient)
  demo.log                   슬라이드에 옮긴 실제 출력
  img/                       커널이 그린 그래프 그림
data-cleaning-slides.html    배포용 HTML
data-cleaning-slides.pdf     강사용 PDF
```

출력은 `FONT=나눔고딕.ttf bash tools/demo.sh /tmp/새폴더 > tools/demo.log 2>&1`로 다시 만들어요. 데이터를 내려받으니 인터넷이 필요해요. 공용 도구는 맨 위 [tools/](../tools)에 있어요. 명령은 이 폴더에서 쳐요.

```bash
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/boxcheck.js slides
node ../tools/build_player.js slides data-cleaning-slides.html
node ../tools/export.js slides data-cleaning-slides.pdf
```

</details>

---

<!-- curriculum:nav -->

[← 이전: 45 · NumPy와 pandas 맛보기](../45-numpy-pandas) · [커리큘럼](../README.md) · [다음: 47 · 그래프 그리기와 연습 데이터 만들기 →](../47-plot-data)

<!-- /curriculum:nav -->
