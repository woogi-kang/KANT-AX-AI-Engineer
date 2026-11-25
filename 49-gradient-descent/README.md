# 49 · 경사 하강법 (조금씩 고쳐 가며 직선 찾기)

> 머신러닝 기초 수업 노트북(`03_ml.ipynb`)의 경사 하강법 부분을 한 챕터로 정리했어요. 48에서 `LinearRegression`이 한 번에 계산한 직선을, 이번에는 틀린 정도(손실)를 보면서 조금씩 고쳐 가며 찾아요. 2차함수와 미분은 식 없이 그림과 실제 숫자로만 풀어요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/49-gradient-descent/gradient-descent-slides.html) · [PDF 받기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/49-gradient-descent/gradient-descent-slides.pdf) | [48 · 첫 머신러닝 모델 (선형 회귀)](../48-linear-regression) | 준비 중 |

<!-- /curriculum:top -->

## 학습 목표

- 손실 함수가 w와 b를 넣으면 틀린 정도(MSE) 하나를 돌려주는 계산이라는 것을 말할 수 있어요.
- b를 35로 두고 w를 바꾸면 MSE가 바닥이 하나인 U자로 바뀌는 것을 표와 그래프로 확인해요.
- "기울기 w"(직선이 얼마나 기울었나, `coef_`)와 "손실의 기울기"(경사, 손실 그래프에 댄 자가 얼마나 기울었나)를 구별해요.
- `새 w = w - 학습률 × 경사`로 한 걸음을 계산하고, 학습률이 너무 작거나 크면 어떻게 되는지 실제 결과로 봐요.
- `SGDRegressor`의 인자(`loss`, `learning_rate`, `eta0`, `shuffle`, `random_state`)가 왜 그 값인지 읽어요.
- `partial_fit`과 `fit`의 차이를 알고, 반복문으로 epoch마다 w, b, MSE를 기록해 학습 곡선을 그려요.

## 시작하기 전에

| 할 일 | 챕터 |
| --- | :---: |
| 반복문 `for`, `range` | 13, 18 |
| 딕셔너리, 딕셔너리 리스트 | 15 |
| 함수 `def`와 `return`, 키워드 인자 | 19, 20 |
| 리스트 컴프리헨션 | 23 |
| `__repr__`(셀 마지막 줄에 나오는 모양) | 25 |
| `ml-basics` 프로젝트, DataFrame, 조건으로 고르기 | 45 |
| `fig, ax = plt.subplots()`, `label`과 `legend`, 시드 | 47 |
| `LinearRegression`, `fit`, `predict`, MSE, R² | 48 |

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 3 | 새 노트북 `gd.ipynb`, import와 글꼴 셀(마이너스 기호 설정 한 줄 더하기) |
| 1 · 왜 필요한가 | 4~7 | 48 다시 보기(w 10, b 35, 6시간 95점), MSE 3.2, 안개 낀 산 내려가기, 학습의 네 박자 |
| 2 · 손실과 경사 | 8~14 | 손실 함수, w 8~12의 MSE 표, U자 그래프와 2차함수, 두 가지 기울기, 접선과 미분, 한 걸음, 손으로 다섯 걸음 |
| 3 · 학습률 | 15~17 | 보폭 0.002, 0.01, 0.1 비교, `eta0` 0.001~0.5, 학습률마다 MSE 그래프 |
| 4 · SGDRegressor로 학습하기 | 18~26 | S, G, D 뜻과 배치 비교, 인자 다섯 개, `partial_fit`과 epoch, 기록 반복문, `isin`, 학습 곡선, w와 b 그래프, 6시간 예측, `LinearRegression` 비교 |
| 5 · 오류와 함정 | 27~30 | `loss="mse"`, `learning_rate`를 뺀 경우, 반복문 안의 `fit`, 반복 셀을 두 번 실행 |
| 6 · 실제 상황 | 31~33 | MSE가 3.3 밑으로 내려간 epoch, 학생 두 명 더 이어서 학습하기, 47의 오피스텔 200건 |
| 정리 | 34~35 | 막힐 때 보는 표, 한 장으로 보는 코드 |

## 핵심 개념

```
지금 w, b ──▶ 1. 예측 ──▶ 2. 손실(MSE) ──▶ 3. 경사 보기 ──▶ 4. 고치기
    ▲                                                        │
    └──────────────── 한 바퀴 = 1 epoch, 수업은 1000번 ───────┘

새 w = w - 학습률 × 경사        w 8, 경사 -44, 학습률 0.01  →  8.44
```

- 손실 함수는 w와 b를 넣으면 틀린 정도를 숫자 하나로 돌려줘요. 오늘은 48의 MSE를 써요.
- b를 35로 두고 w만 8, 9, 10, 11, 12로 바꾸면 MSE가 47.2, 14.2, 3.2, 14.2, 47.2예요. 제곱이 들어간 계산이라 그래프가 바닥이 하나인 U자예요. 이런 그래프를 2차함수라고 불러요.
- "기울기"가 두 번 나와요. 직선의 기울기 w는 공부 1시간에 오르는 점수(`coef_`)예요. 손실의 기울기(경사)는 손실 그래프의 한 점에 자를 댔을 때 얼마나 기울었는지예요.
- 그 자의 기울기를 구하는 일을 미분이라고 불러요. 컴퓨터는 w를 0.001만 움직여 보고 MSE가 얼마나 바뀌는지로 알 수 있어요. w 8에서 -44, 10에서 0, 12에서 +44예요.
- 경사의 반대쪽으로 가면 늘 내리막이에요. 학습률은 한 걸음의 크기예요. 너무 작으면 느리고, 너무 크면 바닥을 넘어가거나 숫자가 터져요. 오류 메시지는 안 나요.
- `SGDRegressor`는 데이터를 한 줄씩 보며 한 걸음씩 고쳐요. `partial_fit`은 한 바퀴(1 epoch)만 배우고 부를 때마다 이어서 배워요. `fit`은 부를 때마다 처음부터 다시 배워요.

## 실습

### 1. 노트북 만들기

45~48의 `ml-basics` 폴더에서 VS Code로 `gd.ipynb`를 만들고 커널은 `.venv`를 골라요(10). 48에서 `uv add scikit-learn`을 했으면 새로 설치할 것은 없어요.

```python
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression
from sklearn.linear_model import SGDRegressor
from sklearn.metrics import mean_squared_error
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

```python
df = pd.DataFrame({
    "hours": [1, 2, 3, 4, 5],
    "scores": [47, 53, 65, 73, 87]
})

X = df[["hours"]]
y = df["scores"]
```

### 2. 손실 표

```python
for w in [8, 9, 10, 11, 12]:
    pred = w * df["hours"] + 35
    mse = mean_squared_error(y, pred)
    print("w =", w, "MSE =", round(mse, 1))
```

```
w = 8 MSE = 47.2
w = 9 MSE = 14.2
w = 10 MSE = 3.2
w = 11 MSE = 14.2
w = 12 MSE = 47.2
```

### 3. 손으로 다섯 걸음

```python
def loss(w):
    pred = w * df["hours"] + 35
    return mean_squared_error(y, pred)

w = 8
for step in range(1, 6):
    slope = (loss(w + 0.001) - loss(w)) / 0.001
    w = w - 0.01 * slope
    print("걸음", step, "| 경사 =", round(slope, 1), "| 새 w =", round(w, 2), "| MSE =", round(loss(w), 2))
```

```
걸음 1 | 경사 = -44.0 | 새 w = 8.44 | MSE = 29.97
걸음 2 | 경사 = -34.3 | 새 w = 8.78 | MSE = 19.49
걸음 3 | 경사 = -26.8 | 새 w = 9.05 | MSE = 13.11
걸음 4 | 경사 = -20.9 | 새 w = 9.26 | MSE = 9.23
걸음 5 | 경사 = -16.3 | 새 w = 9.42 | MSE = 6.87
```

손실 표와 다섯 걸음은 이해를 돕는 연습 셀이에요. 수업 노트북에는 없어요.

### 4. SGDRegressor로 1000 epoch 학습

```python
sgd = SGDRegressor(
    loss="squared_error",      # 손실 함수: 오차 제곱 평균(MSE)
    learning_rate="constant",  # 학습률을 처음 값 그대로
    eta0=0.01,                 # 학습률: 한 번에 고치는 보폭
    shuffle=False,             # 데이터 순서를 섞지 않음
    random_state=42            # 난수 시드
)

epochs = 1000
history = []

for epoch in range(epochs):
    sgd.partial_fit(X, y)

    y_pred = sgd.predict(X)
    mse = mean_squared_error(y, y_pred)

    history.append({
        "epoch": epoch + 1,
        "weight": sgd.coef_[0],
        "bias": sgd.intercept_[0],
        "mse": mse
    })

history_df = pd.DataFrame(history)
```

```python
plt.figure(figsize=(10, 5))
plt.plot(history_df["epoch"], history_df["mse"], color="blue", label="학습 손실(Training Loss)")
plt.title("epoch마다 MSE가 줄어요")
plt.xlabel("Epoch")
plt.ylabel("MSE")
plt.grid(alpha=0.3)
plt.legend()
plt.show()
```

### 5. 예측하기

```python
print(f"기울기(w): {sgd.coef_[0]:.2f}")
print(f"절편(b): {sgd.intercept_[0]:.2f}")

new_data = pd.DataFrame({"hours": [6]})
prediction = sgd.predict(new_data)
print(f"예측 성적: {prediction[0]:.2f}점")
```

```
기울기(w): 10.13
절편(b): 34.74
예측 성적: 95.52점
```

48의 `LinearRegression`은 같은 데이터로 w 10.00, b 35.00, 6시간 95.00점이에요. 반복 셀을 다시 실행하면 이어서 배우니, 처음부터 하려면 `sgd`를 만드는 셀부터 다시 실행해요.

## 명령어 요약

| 명령 | 하는 일 |
| --- | --- |
| `from sklearn.linear_model import SGDRegressor` | 경사 하강법으로 배우는 회귀 모델 불러오기 |
| `SGDRegressor(loss="squared_error", learning_rate="constant", eta0=0.01)` | 손실은 MSE, 보폭 0.01 그대로 |
| `shuffle=False`, `random_state=42` | 순서 그대로, 늘 같은 결과 |
| `sgd.partial_fit(X, y)` | 한 바퀴(1 epoch)만 배우기, 부르면 이어서 |
| `sgd.coef_[0]` / `sgd.intercept_[0]` | 지금 기울기 w, 절편 b (둘 다 배열) |
| `history.append({...})` / `pd.DataFrame(history)` | epoch마다 기록하고 표로 |
| `df[df["열"].isin([값, ...])]` | 목록에 있는 값의 줄만 고르기 |
| `fig, axes = plt.subplots(1, 2)` | 그래프 칸 두 개, `axes[0]` `axes[1]` |
| `새 w = w - 학습률 × 경사` | 경사의 반대쪽으로 한 걸음 |

## 문제 해결

| 메시지 | 원인 | 해결 |
| --- | --- | --- |
| `InvalidParameterError: The 'loss' parameter of SGDRegressor must be a str among {...}. Got 'mse' instead.` | `loss="mse"`라고 적었어요 | `loss="squared_error"` |
| MSE가 `8.96e+24`처럼 엄청 커요 | 학습률이 너무 커서 숫자가 터졌어요 | `eta0`를 10배씩 작게 |
| MSE가 줄다가 큰 값에서 멈추거나 1000번 뒤에도 커요 | 학습률이 크거나 너무 작아요. `learning_rate`를 빼서 `invscaling`이 쓰였을 수도 있어요 | `learning_rate="constant"` 확인, `eta0` 바꾸며 학습 곡선 보기 |
| `ConvergenceWarning: Maximum number of iteration reached before convergence.` | 반복문 안에서 `fit(X, y)`를 불렀어요 | `partial_fit(X, y)` |
| 학습 곡선이 처음부터 평평해요 | 반복 셀을 두 번 실행해서 이어서 배웠어요 | `sgd`를 만드는 셀부터 다시 실행 |
| `Glyph 8722 (\N{MINUS SIGN}) missing from font(s)` | 글꼴에 마이너스 기호가 없어요 | `plt.rcParams["axes.unicode_minus"] = False` |

## 강사용

<details>
<summary>수업 코드와 다르게 보여 준 곳</summary>

- 수업 메모의 "6시간 학습 96점"은 `predict` 결과가 95.0이라 95점으로 적었어요.
- 학습 곡선 셀의 `plt.xlabel("Loss")`는 가로축이 epoch라 `"Epoch"`로, `Traing`은 `Training`으로 고치고 빠진 `plt.legend()`와 제목 줄을 더했어요.
- `eta0=0.01` 주석 "초기 학습률"은 `constant`라 바뀌지 않아서 "학습률"로 고쳤어요. `partial_fit`에서 쓰이지 않는 `max_iter=1000`은 지웠고, 나머지 주석도 쉬운 말로 바꿨어요.
- 마크다운 제목의 "시험 적적 예측하기"는 "성적"으로 고쳤어요.
- 글꼴 셀은 AppleGothic만 적혀 있어서 46, 47처럼 운영체제마다 고르게 하고 `axes.unicode_minus` 한 줄을 더했어요.
- 손실 표, U자 그래프, `def loss(w)`, 경사 계산, 다섯 걸음, 학습률 비교(`train` 함수), 오류 셀, 실제 상황 셀은 이해를 도우려고 더한 셀이에요. 학습률 비교와 오류 셀은 새 노트북에서 import와 데이터 셀 뒤에 실행해서 셀 번호가 다시 시작해요.
- 그래프 그림은 리눅스에서 만들어서 맑은 고딕 대신 나눔고딕으로 그렸어요.

</details>

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json                      슬라이드 순서와 파트 구분
  *.html                         한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
datasets/
  office.csv                     47에서 저장하는 연습 데이터 (6파트에서 써요)
tools/
  gen.py                         이 챕터의 장 생성
  demo.sh                        uv 프로젝트를 만들고 노트북 셀을 실제로 실행
  run_nb.py                      demo.sh가 부르는 셀 실행기 (nbclient)
  demo.log                       슬라이드에 옮긴 실제 출력
  img/                           커널이 그린 그래프 그림
gradient-descent-slides.html     배포용 HTML
gradient-descent-slides.pdf      슬라이드 PDF
```

출력은 `FONT=나눔고딕.ttf bash tools/demo.sh /tmp/새폴더 > tools/demo.log 2>&1`로 다시 만들어요. 공용 도구는 맨 위 [tools/](../tools)에 있어요. 명령은 이 폴더에서 쳐요.

```bash
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/boxcheck.js slides
node ../tools/build_player.js slides gradient-descent-slides.html
node ../tools/export.js slides gradient-descent-slides.pdf
```

</details>

---

<!-- curriculum:nav -->

[← 이전: 48 · 첫 머신러닝 모델 (선형 회귀)](../48-linear-regression) · [커리큘럼](../README.md)

<!-- /curriculum:nav -->
