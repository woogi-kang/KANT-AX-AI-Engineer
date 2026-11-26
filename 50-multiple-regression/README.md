# 50 · 다중 선형 회귀와 ML 기초 정리

> 머신러닝 기초 수업 노트북(`03_ml.ipynb`)의 다중 회귀 부분을 한 챕터로 정리했어요. 학생 10명의 공부 시간, 수면 시간, 푼 문제 수로 점수를 예측해요. 수업에서는 seaborn 산점도와 상관계수 히트맵까지 그렸고, 이 챕터는 그 뒤 단계(세 열로 학습, 기울기 읽기, 예측, 채점)를 이어서 보여 줘요. 마지막 장에서 45부터 50까지 배운 머신러닝 기초를 한 장으로 묶어요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/50-multiple-regression/multiple-regression-slides.html) · [PDF 받기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/50-multiple-regression/multiple-regression-slides.pdf) | [49 · 경사 하강법 (조금씩 고쳐 가며 직선 찾기)](../49-gradient-descent) | 준비 중 |

<!-- /curriculum:top -->

## 학습 목표

- seaborn이 무엇인지 알고, `sns.scatterplot(data=, x=, y=, ax=)`의 네 칸에 왜 그 값이 들어가는지 말할 수 있어요.
- `plt.subplots(1, 3)`으로 그림판을 칸 셋으로 나누고 `axes[0]`처럼 번호로 칸을 골라요.
- `df.corr()`로 모든 열 짝의 상관계수를 구하고 `sns.heatmap`의 `annot`, `vmin`, `vmax`, `fmt`를 읽어요.
- 한글 글꼴에서 마이너스가 네모로 나올 때 `axes.unicode_minus`를 꺼요.
- `X = df[["a", "b", "c"]]`로 입력 열 셋을 넣어 학습하고, `coef_`의 세 기울기를 "나머지는 그대로, 이 열만 1 늘리면"으로 읽어요.
- `predict`에는 학습 때와 같은 열, 같은 순서의 표를 넣어요.
- 한 열 모델과 세 열 모델의 MAE, R²를 비교하고 정답과 예측 점 그림으로 확인해요.

## 시작하기 전에

| 할 일 | 챕터 |
| --- | :---: |
| VS Code 노트북과 커널 고르기 | 10 |
| f-string 소수점 `:.2f`, `for` | 13 |
| `if` `elif`로 고르기 | 17 |
| `import 모듈 as 별명`, `from 모듈 import 이름` | 28 |
| `ml-basics` 프로젝트, DataFrame, `sort_values`, `head` | 45 |
| seaborn 설치, 한글 글꼴 셀 | 46 |
| `fig, ax = plt.subplots()`, 산점도, 상관계수 | 47 |
| `LinearRegression`, `fit`, `predict`, `coef_`, MAE, R² | 48 |
| 경사 하강법으로 기울기 찾기 | 49 |

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 3~4 | 새 노트북 `multi.ipynb`, 불러오기와 글꼴 셀(마이너스 한 줄 더하기) |
| 1 · 왜 필요한가 | 5~8 | 공부 열 하나로는 같은 점수, 입력 열 셋 그림, 열마다 붙는 기울기, 수업 주석의 낯선 말 |
| 2 · 그래프로 먼저 보기 | 9~17 | 데이터, seaborn, `plt.subplots(1, 3)`, scatterplot 네 칸, 산점도 읽기, `df.corr()`, 히트맵, `vmin` `vmax`, 마이너스 깨짐 |
| 3 · 세 열로 학습하기 | 18~23 | 대괄호 두 겹 X, `fit`과 `coef_`, 기울기 읽기, `predict` 계산, MAE와 R², 정답과 예측 점 그림 |
| 4 · 한 열 모델과 비교 | 24~26 | 혼자 배운 기울기와 같이 배운 기울기, 수면 열을 넣었을 때, 48과 비교표 |
| 5 · 오류와 함정 | 27~30 | `predict` 표의 열 순서와 빠진 열, 대괄호 한 겹 `KeyError`, `ax=`를 뺀 그래프, AppleGothic만 적은 글꼴 |
| 6 · 실제 상황 | 31~32 | 다음 시험 계획 비교, 가장 크게 틀린 학생 찾기 |
| 정리 | 33~35 | 막힐 때 보는 표, 머신러닝 기초 한 장 정리(45~50), 한 장으로 보는 코드 |

3파트부터는 수업 노트북 다음 단계예요. 덱의 해당 장 오른쪽 위에 "수업 노트북 다음 단계" 표시가 있어요.

## 핵심 개념

```
df (학생 10명)
 ├─ 그래프로 보기   sns.scatterplot × 3  (plt.subplots(1, 3)의 axes[0], axes[1], axes[2])
 │                  df.corr() ──▶ sns.heatmap(corr, annot=True, vmin=-1, vmax=1, fmt=".2f")
 │
 └─ 학습하기        X = df[["study_hours", "sleep_hours", "practice_count"]]   (10, 3)
                    y = df["score"]                                             (10,)
                    model.fit(X, y)
                    coef_ [5.80, 2.68, 0.63]   intercept_ 17.66
                    점수 = 5.80 × 공부 + 2.68 × 수면 + 0.63 × 문제 + 17.66
```

- 다중 선형 회귀는 48의 선형 회귀에서 입력 열만 늘린 거예요. `LinearRegression()`, `fit(X, y)`, `predict(표)` 세 줄은 그대로예요.
- 기울기는 열마다 하나, 절편은 하나예요. `coef_`의 칸 순서는 X에 적은 열 순서예요.
- 기울기 하나는 "나머지 열은 그대로 두고 그 열만 1 늘리면 오르는 점수"로 읽어요. 같이 넣은 열이 바뀌면 기울기도 바뀌어요(공부 혼자 8.90, 세 열에서는 5.80).
- 상관계수는 두 열이 같이 오르내리는 정도예요(-1~1). 히트맵은 그 표를 색으로 칠한 그림이고, `vmin=-1, vmax=1`로 범위를 고정해야 0이 가운데 색이 돼요.
- 열이 셋이면 직선 그림을 그릴 수 없어서 가로 정답, 세로 예측으로 점을 찍어 비교해요.
- 학습에 쓴 10명으로 채점해서 점수(R² 0.99)가 실제보다 좋게 나와요. 처음 보는 학생으로 채점하는 방법은 다음에 배워요.

## 실습

### 1. 노트북 열기

48의 `ml-basics` 폴더를 그대로 써요. seaborn(46)과 scikit-learn(48)이 이미 들어 있어서 새로 넣을 패키지는 없어요.

```bash
cd ml-basics
cat pyproject.toml
```

```
dependencies = [
    "matplotlib>=3.11.2",
    "numpy>=2.5.5",
    "pandas>=3.1.1",
    "scikit-learn>=1.9.1",
    "seaborn>=0.13.2",
]
```

`dependencies`만 옮겼어요. 버전 숫자는 받은 날에 따라 달라요. seaborn이나 scikit-learn이 없으면 `uv add seaborn matplotlib`, `uv add scikit-learn`을 쳐요. VS Code에서 `multi.ipynb`를 만들고 커널은 `.venv`를 골라요(10).

### 2. 불러오기와 글꼴

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
```

```python
import platform

os_name = platform.system()
if os_name == "Windows":
    plt.rcParams["font.family"] = "Malgun Gothic"
elif os_name == "Darwin":
    plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False
```

### 3. 데이터와 그래프

```python
df = pd.DataFrame({
    "study_hours":    [1, 2, 3, 4, 5, 2, 3, 5, 4, 1],
    "sleep_hours":    [6, 8, 5, 7, 8, 5, 8, 6, 6, 8],
    "practice_count": [10, 15, 20, 25, 30, 12, 28, 22, 32, 8],
    "score":          [47, 58, 60, 76, 87, 49, 73, 77, 79, 52]
})
df
```

```python
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

sns.scatterplot(data=df, x="study_hours", y="score", ax=axes[0])
sns.scatterplot(data=df, x="sleep_hours", y="score", ax=axes[1])
sns.scatterplot(data=df, x="practice_count", y="score", ax=axes[2])

plt.show()
```

```python
corr = df.corr()
corr.round(2)
```

```
                study_hours  sleep_hours  practice_count  score
study_hours            1.00         0.00            0.85   0.93
sleep_hours            0.00         1.00            0.14   0.29
practice_count         0.85         0.14            1.00   0.93
score                  0.93         0.29            0.93   1.00
```

```python
plt.figure(figsize=(7, 5))

sns.heatmap(
    corr,
    annot=True,
    vmin=-1,
    vmax=1,
    fmt=".2f"
)

plt.show()
```

그래프는 슬라이드 13쪽과 15쪽에서 봐요.

### 4. 세 열로 학습하기

```python
from sklearn.linear_model import LinearRegression

X = df[["study_hours", "sleep_hours", "practice_count"]]
y = df["score"]
print(X.shape, y.shape)
```

```
(10, 3) (10,)
```

```python
model = LinearRegression()
model.fit(X, y)

print("기울기 w:", model.coef_)
print("절편 b:", model.intercept_)
```

```
기울기 w: [5.80222725 2.68100001 0.63219852]
절편 b: 17.660208080206637
```

### 5. 예측하고 채점하기

```python
new = pd.DataFrame({"study_hours": [3], "sleep_hours": [7], "practice_count": [20]})
model.predict(new)
```

```
array([66.4778603])
```

```python
from sklearn.metrics import mean_absolute_error, r2_score

y_pred = model.predict(X)
print(f"세 열 MAE {mean_absolute_error(y, y_pred):.2f} | R2 {r2_score(y, y_pred):.2f}")
```

```
세 열 MAE 1.17 | R2 0.99
```

같은 데이터로 공부 열 하나만 학습하면 MAE 4.26, R² 0.87이에요(슬라이드 22쪽).

## 명령어 요약

| 명령 | 하는 일 |
| --- | --- |
| `import seaborn as sns` | 표와 열 이름으로 그래프를 그리는 도구 불러오기 |
| `fig, axes = plt.subplots(1, 3, figsize=(16, 5))` | 그림판 하나를 가로로 칸 셋으로 나누기 |
| `sns.scatterplot(data=df, x="열", y="열", ax=axes[0])` | 열 이름으로 산점도, 0번 칸에 그리기 |
| `df.corr()` | 모든 열 짝의 상관계수 표 |
| `sns.heatmap(corr, annot=True, vmin=-1, vmax=1, fmt=".2f")` | 상관계수 표를 색 칸으로, 숫자는 소수 둘째 자리까지 |
| `plt.rcParams["axes.unicode_minus"] = False` | 한글 글꼴에서 마이너스가 네모로 나오지 않게 |
| `X = df[["a", "b", "c"]]` | 입력 열 셋을 표로 고르기 |
| `model.coef_` / `model.intercept_` | 기울기 셋(X 열 순서), 절편 하나 |
| `model.predict(pd.DataFrame({...}))` | 학습 때와 같은 열, 같은 순서의 표로 예측 |
| `r2_score(y, y_pred)` | R², 늘 (정답, 예측) 순서 |

## 문제 해결

| 메시지 | 원인 | 해결 |
| --- | --- | --- |
| `ValueError: ... Feature names must be in the same order as they were in fit.` | `predict` 표의 열 순서가 학습 때와 달라요 | X와 같은 순서로 열 적기 |
| `ValueError: ... Feature names seen at fit time, yet now missing:` | `predict` 표에 열이 빠졌어요 | 세 열을 모두 적기 |
| `KeyError: ('study_hours', 'sleep_hours')` | 열 둘을 대괄호 한 겹으로 골랐어요 | `df[["study_hours", "sleep_hours"]]` |
| 그래프 셋이 오른쪽 칸 하나에 겹쳐요 | `scatterplot`에 `ax=`를 안 적었어요 | `ax=axes[0]`, `ax=axes[1]`, `ax=axes[2]` |
| `UserWarning: Glyph 8722 (\N{MINUS SIGN}) missing from font(s) ...` | 한글 글꼴에 마이너스 기호가 없어요 | `plt.rcParams["axes.unicode_minus"] = False` |
| `findfont: Font family 'AppleGothic' not found.` | Windows에서 Mac 글꼴을 골랐어요 | 46의 글꼴 셀(`platform.system()`)로 고르기 |
| 히트맵에서 0.00이 가장 어두운 색이에요 | `vmin`, `vmax`를 빼서 범위가 표 안의 값으로 정해졌어요 | `vmin=-1, vmax=1` |

## 강사용

<details>
<summary>수업 코드와 다르게 보여 준 곳</summary>

- 수업 노트북의 글꼴 셀은 AppleGothic 한 줄만 적고 Windows 줄을 주석으로 막아 뒀어요. Windows에서는 한글이 깨져서 46의 `platform.system()` 셀로 바꾸고, 원래 셀은 5파트 함정 장에 보여 줘요.
- 수업 노트북에 마이너스 경고(`Glyph 8722`)가 나와서 글꼴 셀에 `axes.unicode_minus` 줄을 더했어요.
- 수업 셀은 `corr`만 만들었고, 표를 찍는 `corr.round(2)`는 보기 좋게 더했어요.
- 수업은 히트맵까지였어요. 1파트의 공부 열 모델, 3파트부터의 학습, 기울기 읽기, 예측, 채점, 정답과 예측 그림, 4파트 비교, 6파트 실제 상황은 이해를 도우려고 더한 셀이에요. 덱에 "수업 노트북 다음 단계"로 표시했어요.
- 모든 출력은 같은 커널에서 실제로 실행했어요. 그래프는 리눅스에서 만들어서 맑은 고딕 대신 나눔고딕으로 그렸어요.
- 수업 주석의 독립변수, 종속변수, 가중치, 편향은 48에서 쓴 말(문제, 정답, 기울기, 절편)로 바꿔 읽게 했어요(8쪽).

</details>

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json                        슬라이드 순서와 파트 구분
  *.html                           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py                           이 챕터의 장 생성
  demo.sh                          uv 프로젝트를 만들고 노트북 셀을 실제로 실행
  run_nb.py                        demo.sh가 부르는 셀 실행기 (nbclient)
  demo.log                         슬라이드에 옮긴 실제 출력
  img/                             커널이 그린 그래프 그림
multiple-regression-slides.html    배포용 HTML
multiple-regression-slides.pdf     슬라이드 PDF
```

출력은 `FONT=나눔고딕.ttf bash tools/demo.sh /tmp/새폴더 > tools/demo.log 2>&1`로 다시 만들어요. 공용 도구는 맨 위 [tools/](../tools)에 있어요. 명령은 이 폴더에서 쳐요.

```bash
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/boxcheck.js slides
node ../tools/build_player.js slides multiple-regression-slides.html
node ../tools/export.js slides multiple-regression-slides.pdf
```

</details>

---

<!-- curriculum:nav -->

[← 이전: 49 · 경사 하강법 (조금씩 고쳐 가며 직선 찾기)](../49-gradient-descent) · [커리큘럼](../README.md)

<!-- /curriculum:nav -->
