# 51 · 처음 보는 데이터로 채점하기 (나누기와 스케일링)

> 머신러닝 기초 수업 노트북(`03_ml.ipynb`)의 마지막 부분(셀 48~58)을 한 챕터로 정리했어요. 50에서는 학습한 학생 10명으로 다시 채점해서 R²가 0.99로 후하게 나왔어요. 이번에는 학생을 학습용 7명과 채점용 3명으로 나눠 채점하고, 열마다 다른 숫자 크기를 `StandardScaler`로 맞춘 뒤 49의 경사 하강법(`SGDRegressor`)으로 세 열을 학습해요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/51-train-test-split/train-test-split-slides.html) · [PDF 받기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/51-train-test-split/train-test-split-slides.pdf) | [50 · 다중 선형 회귀와 ML 기초 정리](../50-multiple-regression) | [52 · 사진으로 사람 맞히기 (얼굴 데이터와 KNN)](../52-face-knn) |

<!-- /curriculum:top -->

## 학습 목표

- 학습한 데이터로 채점하면 점수가 후하게 나오는 이유를 말하고, 처음 보는 데이터로 채점해요.
- `train_test_split(X, y, test_size=0.3, random_state=42)`의 칸마다 왜 그 값이 들어가는지, 돌려주는 네 개의 순서를 말할 수 있어요.
- `random_state`를 빼면 채점용 학생이 매번 바뀐다는 것을 실제 결과로 확인해요.
- `describe()`로 열마다 숫자 크기가 다른 것을 보고, 표준화(평균 빼고 표준편차로 나누기)를 손으로 계산해요.
- `StandardScaler`로 학습용은 `fit_transform`, 채점용과 새 학생은 `transform`을 써요.
- 크기를 맞춘 표로 `SGDRegressor`를 학습하고, 기울기 셋의 변화를 한 그래프에 그려요.
- 크기를 맞춘 열의 기울기를 "표준편차 1개만큼"으로 읽어요.

## 시작하기 전에

| 할 일 | 챕터 |
| --- | :---: |
| VS Code 노트북과 커널 고르기 | 10 |
| f-string 소수점 `:.4f`, 칸 수 맞추기, `for` | 13 |
| `return a, b`와 `x, y = 함수()` | 19 |
| `import 모듈 as 별명`, `from 모듈 import 이름` | 28 |
| `ml-basics` 프로젝트, DataFrame, index, 배열 `mean` | 45 |
| `describe()`, 한글 글꼴 셀 | 46 |
| `fig, ax = plt.subplots()`, `label`과 `legend`, `default_rng(42)` | 47 |
| `LinearRegression`, `fit`, `predict`, `coef_`, MAE, MSE, R² | 48 |
| `SGDRegressor`, `eta0`, `partial_fit`, epoch, 학습 곡선 | 49 |
| 학생 10명 표와 세 열 `X` | 50 |

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 3~4 | 새 노트북 `split.ipynb`, 50과 같은 데이터와 `features` 리스트 |
| 1 · 왜 필요한가 | 5~7 | 50의 R² 0.99는 공부한 문제로 본 시험, 기출문제 덮어 두기, 나누기가 들어가는 자리 |
| 2 · 나눠서 채점하기 | 8~14 | `model_selection` 서랍, 네 결과와 순서, `test_size`와 `random_state`, 누가 채점용인지, 7명으로 학습하고 3명으로 채점(R² 0.93), 학습용 0.9992와 비교 |
| 3 · 열의 크기 맞추기 | 15~20 | 크기를 안 맞춘 SGD가 터지는 장면, `describe()`, 표준화 손 계산, `StandardScaler`, `mean_`과 `scale_`, 평균 0 표준편차 1 확인 |
| 4 · SGD로 세 열 배우기 | 21~25 | 크기를 맞춘 SGD(R² 0.95, 197 epoch에서 멈춤), `partial_fit` 반복, 기울기 셋 그래프, 가로 막대 비교, `LinearRegression`과 비교표 |
| 5 · 오류와 함정 | 26~29 | 네 칸 순서를 바꿔 적기, 채점용에 `fit_transform`, 바꾸지 않은 표로 `predict`, 바꾼 열의 기울기 읽기 |
| 6 · 실제 상황 | 30~32 | 새 학생 예측, `random_state`마다 흔들리는 채점 점수, 47의 오피스텔 200건과 49에서 터진 SGD 살리기 |
| 정리 | 33~35 | 막힐 때 보는 표, 네 단계 정리, 한 장으로 보는 코드 |

## 핵심 개념

```
X, y (학생 10명)
 └─ train_test_split(X, y, test_size=0.3, random_state=42)
     ├─ X_train, y_train  학습용 7명  ──▶ scaler.fit_transform(X_train) ──▶ sgd.fit(X_train_scaled, y_train)
     └─ X_test,  y_test   채점용 3명  ──▶ scaler.transform(X_test)      ──▶ sgd.predict(X_test_scaled)
                                                                              └─ r2_score(y_test, 예측)
```

- 학습에 쓴 데이터로 채점하면 답을 본 시험이라 점수가 후해요(학습용 7명 R² 0.9992). 처음 보는 3명으로 채점한 점수(0.93)가 새 학생에게 기대할 점수에 가까워요.
- `train_test_split`은 줄을 섞은 다음 나눠요. 돌려주는 순서는 X 학습, X 채점, y 학습, y 채점이에요.
- `random_state`는 섞는 순서 번호예요. 빼면 실행할 때마다 채점용 학생이 바뀌어요.
- 표준화는 열마다 평균을 빼고 표준편차로 나눠요. 점의 순서와 간격은 그대로이고 눈금만 "표준편차 몇 개"로 바뀌어요.
- `fit`은 학습용으로 자(평균과 표준편차)를 만드는 일이에요. 채점용과 새 학생은 그 자로 `transform`만 해요.
- 경사 하강법은 열 크기가 다르면 같은 보폭이 큰 열에 너무 커서 숫자가 터져요. `LinearRegression`은 공식으로 한 번에 계산해서 크기를 안 맞춰도 돼요.
- 크기를 맞춘 열의 기울기 9.37은 "표준편차 하나(1.55시간)만큼 늘면 9.37점"이에요. 1시간으로는 6.04점이에요.

## 실습

### 1. 노트북 열기

48의 `ml-basics` 폴더를 그대로 써요. `train_test_split`과 `StandardScaler`는 48에서 넣은 scikit-learn 안에 있어서 새로 넣을 패키지는 없어요. VS Code에서 `split.ipynb`를 만들고 커널은 `.venv`를 골라요(10).

### 2. 불러오기와 데이터

```python
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression, SGDRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
```

글꼴 셀은 50과 같아요(46의 셀에 `plt.rcParams["axes.unicode_minus"] = False`를 더한 셀).

```python
df = pd.DataFrame({
    "study_hours":    [1, 2, 3, 4, 5, 2, 3, 5, 4, 1],
    "sleep_hours":    [6, 8, 5, 7, 8, 5, 8, 6, 6, 8],
    "practice_count": [10, 15, 20, 25, 30, 12, 28, 22, 32, 8],
    "score":          [47, 58, 60, 76, 87, 49, 73, 77, 79, 52]
})
features = ["study_hours", "sleep_hours", "practice_count"]
X = df[features]
y = df["score"]
```

### 3. 학습용과 채점용으로 나누기

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.3,
    random_state=42
)

print("X_train:", X_train.shape)
print("X_test:", X_test.shape)
print("y_train:", y_train.shape)
print("y_test:", y_test.shape)
```

```
X_train: (7, 3)
X_test: (3, 3)
y_train: (7,)
y_test: (3,)
```

### 4. 학습용으로 배우고 채점용으로 채점하기

```python
test_model = LinearRegression()
test_model.fit(X_train, y_train)

test_pred = test_model.predict(X_test)

print(f"MAE: {mean_absolute_error(y_test, test_pred):.4f}")
print(f"MSE: {mean_squared_error(y_test, test_pred):.4f}")
print(f"R2: {r2_score(y_test, test_pred):.4f}")
```

```
MAE: 3.0870
MSE: 10.6380
R2: 0.9327
```

### 5. 열의 크기 맞추기

```python
X.describe().round(2)
```

```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

scaled_df = pd.DataFrame(X_train_scaled, columns=features)
scaled_df.round(2)
```

```
   study_hours  sleep_hours  practice_count
0        -1.38        -0.76           -1.32
1         1.20        -0.76            0.20
2        -0.09        -1.65           -0.05
3        -1.38         1.02           -1.58
4         1.20         1.02            1.21
5         0.55         0.13            0.58
6        -0.09         1.02            0.96
```

### 6. SGD로 세 열 학습하기

```python
sgd = SGDRegressor(
    loss="squared_error",
    learning_rate="constant",
    eta0=0.01,
    max_iter=3000,
    random_state=42
)

sgd.fit(X_train_scaled, y_train)

sgd_pred = sgd.predict(X_test_scaled)

print(f"MAE: {mean_absolute_error(y_test, sgd_pred):.4f}")
print(f"MSE: {mean_squared_error(y_test, sgd_pred):.4f}")
print(f"R2: {r2_score(y_test, sgd_pred):.4f}")
```

```
MAE: 2.8169
MSE: 8.5966
R2: 0.9456
```

`partial_fit` 반복, 기울기 셋 그래프, 가로 막대 코드는 슬라이드 22~24쪽에 있어요.

## 명령어 요약

| 명령 | 하는 일 |
| --- | --- |
| `from sklearn.model_selection import train_test_split` | 데이터 나누는 함수 불러오기 |
| `X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)` | 30%를 채점용으로, 섞는 순서 고정 |
| `list(X_test.index)` | 채점용으로 간 원래 행 번호 |
| `from sklearn.preprocessing import StandardScaler` | 표준화 도구 불러오기 |
| `scaler.fit_transform(X_train)` | 학습용으로 평균과 표준편차를 재고 바꾸기 |
| `scaler.transform(X_test)` | 학습용에서 잰 값으로 바꾸기만 |
| `scaler.mean_` / `scaler.scale_` | 열마다 평균, 표준편차 |
| `X_train_scaled.mean(axis=0)` | 열마다 평균 |
| `plt.barh(이름들, 길이들, color="blue")` | 가로 막대 그래프 |

## 문제 해결

| 메시지 | 원인 | 해결 |
| --- | --- | --- |
| `ValueError: Found input variables with inconsistent numbers of samples: [7, 3]` | 받는 이름 순서를 `X_train, y_train, X_test, y_test`로 적었어요 | `X_train, X_test, y_train, y_test` 순서로 받기 |
| 기울기가 `3.36938078e+10`처럼 터져요 | 크기를 안 맞춘 표로 SGD를 학습했어요 | `scaler.fit_transform(X_train)`으로 바꾼 표로 학습 |
| `UserWarning: X has feature names, but SGDRegressor was fitted without feature names` | 바꾸지 않은 표를 `predict`에 넣었어요 | `sgd.predict(scaler.transform(표))` |
| 오류 없이 채점 점수가 떨어져요 (R² 0.81) | 채점용에 `fit_transform`을 썼어요 | 채점용과 새 학생은 `transform`만 |
| 실행할 때마다 채점용 학생과 점수가 달라요 | `random_state`를 안 적었어요 | `random_state=42` |

## 강사용

<details>
<summary>수업 코드와 다르게 보여 준 곳</summary>

- 셀 48의 주석 `y_yrain`은 오타라서 뺐어요.
- 셀 53 주석의 "표준화 (-1 ~ +1)"는 실제 값에 -1.65가 있어서, "평균 0, 퍼진 정도 1"로 고쳐 설명했어요(18쪽).
- 셀 55의 주석 두 줄이 서로 바뀌어 있어서 주석은 빼고 장의 설명으로 대신했어요.
- 셀 57의 손실 곡선과 w1 그래프 중 w1 그래프는 셀 58의 세 기울기 그래프에 들어 있어서 손실 곡선만 보여 줘요. 손실 곡선에는 제목과 축 이름을 더했어요.
- 셀 58의 `axe`는 `ax`로, `plt.legend()`는 `ax.legend()`로 바꾸고 제목과 x축 이름을 더했어요.
- 24쪽의 가로 막대 두 개는 이해를 도우려고 더한 그래프예요. 오른쪽 그래프는 셀 56의 500 epoch를 마친 `sgd`로 그려서 21쪽(197 epoch)의 기울기와 조금 달라요.
- 1파트의 50 다시 보기, 누가 채점용인지, `random_state` 비교, 학습용 점수, 3파트의 크기 안 맞춘 SGD와 손 계산, 4파트의 `n_iter_`, 5파트, 6파트는 이해를 도우려고 더한 셀이에요.
- 6파트 오피스텔에서 학습용 R²(0.784)가 채점용(0.917)보다 낮은 건 47의 특이 매물 5건(122, 134, 17, 172, 178번)이 모두 학습용에 들어갔기 때문이에요. 같은 커널에서 확인했어요.
- 모든 출력은 같은 커널에서 실제로 실행했어요. 그래프는 리눅스에서 만들어서 맑은 고딕 대신 나눔고딕으로 그렸어요.

</details>

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json                      슬라이드 순서와 파트 구분
  *.html                         한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py                         이 챕터의 장 생성
  demo.sh                        uv 프로젝트를 만들고 노트북 셀을 실제로 실행
  run_nb.py                      demo.sh가 부르는 셀 실행기 (nbclient)
  demo.log                       슬라이드에 옮긴 실제 출력
  img/                           커널이 그린 그래프 그림
datasets/office.csv              6파트에서 쓰는 47의 오피스텔 데이터
train-test-split-slides.html     배포용 HTML
train-test-split-slides.pdf      슬라이드 PDF
```

출력은 `FONT=나눔고딕.ttf bash tools/demo.sh /tmp/새폴더 > tools/demo.log 2>&1`로 다시 만들어요. 공용 도구는 맨 위 [tools/](../tools)에 있어요. 명령은 이 폴더에서 쳐요.

```bash
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/boxcheck.js slides
node ../tools/build_player.js slides train-test-split-slides.html
node ../tools/export.js slides train-test-split-slides.pdf
```

</details>

---

<!-- curriculum:nav -->

[← 이전: 50 · 다중 선형 회귀와 ML 기초 정리](../50-multiple-regression) · [커리큘럼](../README.md) · [다음: 52 · 사진으로 사람 맞히기 (얼굴 데이터와 KNN) →](../52-face-knn)

<!-- /curriculum:nav -->
