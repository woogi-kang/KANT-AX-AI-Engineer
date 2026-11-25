# 48 · 첫 머신러닝 모델 (선형 회귀)

> 머신러닝 기초 수업 노트북(`02_ml.ipynb`)의 뒷부분을 한 챕터로 정리했어요. 47에서 정답(기울기 450, 절편 5000)을 알고 만든 오피스텔 시세 200건으로 scikit-learn의 선형 회귀 모델을 학습하고, 처음 보는 면적의 가격을 예측하고, 점수 넷으로 채점해요. 처음 쓰는 라이브러리라서 함수마다 괄호 안에 왜 그 값이 들어가는지 하나씩 풀어 봐요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/48-linear-regression/linear-regression-slides.html) · [PDF 받기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/48-linear-regression/linear-regression-slides.pdf) | [47 · 그래프 그리기와 연습 데이터 만들기](../47-plot-data) | 준비 중 |

<!-- /curriculum:top -->

## 학습 목표

- scikit-learn이 무엇인지 알고, 설치 이름(`scikit-learn`)과 불러오는 이름(`sklearn`)을 구별해요.
- `from sklearn.linear_model import LinearRegression`을 패키지, 모듈, 클래스로 나눠 읽어요.
- `model = LinearRegression()`으로 빈 모델을 만들고 `model.fit(X, y)`로 학습해요. X는 대괄호 두 겹(표), y는 한 겹(한 줄)인 이유를 말할 수 있어요.
- `coef_`, `intercept_`로 모델이 찾은 기울기와 절편을 꺼내 47의 정답과 비교해요.
- `model.predict(표)`로 새 면적의 가격을 예측하고, 정렬한 면적으로 직선을 그려요.
- MAE, MSE, RMSE, R²를 `(정답, 예측)` 순서로 구하고 무엇을 뜻하는지 읽어요.
- True/False 마스크로 특이 매물을 빼고 다시 채점해요.

## 시작하기 전에

| 할 일 | 챕터 |
| --- | :---: |
| `uv add`, VS Code 노트북과 커널 고르기 | 09, 10 |
| f-string 천 단위 쉼표 `:,.0f` | 13 |
| 위치 인자(순서대로 들어가기) | 19, 20 |
| 클래스와 객체(붕어빵 틀과 붕어빵), `__repr__` | 24, 25 |
| `from 모듈 import 이름` | 28 |
| `ml-basics` 프로젝트, DataFrame, Series, `arr[조건]` | 45 |
| 튀는 값은 누구인지 보고 지우기 | 46 |
| 산점도, 상관계수, 정답을 아는 연습 데이터 `office.csv` | 47 |

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 3~4 | `uv add scikit-learn`, 맨 위 세 셀과 `office.csv` 읽기 |
| 1 · 왜 필요한가 | 5~9 | 사람마다 다른 직선, 수업 다섯 단계, 기울기와 절편, scikit-learn 서랍, 가장 짧은 학습 셀 |
| 2 · 학습하고 예측하기 | 10~18 | import 읽기, 빈 모델, X와 y의 대괄호, `fit` 순서, 오차 제곱 합, `coef_`와 `intercept_`, `predict`, 직선 그리기, 예측과 오차 표 |
| 3 · 채점하기 | 19~24 | 오차 합은 0, MAE, MSE와 RMSE, R², `(정답, 예측)` 순서, 점수 넷 비교표 |
| 4 · 특이 매물과 47 비교 | 25~27 | `np.ones` 마스크, 특이 매물 뺀 채점, 상관계수 제곱과 R² |
| 5 · 오류와 함정 | 28~32 | 한 겹 X, 숫자만 넣은 `predict`, 다른 열 이름, fit 전 `predict`, `special`을 넣은 수업 셀 |
| 6 · 실제 상황 | 33~36 | 오피스텔 견적표, 오차로 특이 매물 찾기, 빼고 다시 학습하기, 미국 집값 300채 |
| 정리 | 37~38 | 막힐 때 보는 표, 한 장으로 보는 코드 |

## 핵심 개념

```
office.csv ──▶ X = office[["area"]]   (200, 1) 표
               y = office["price"]    (200,)   한 줄
                    │
model = LinearRegression()   빈 모델 (붕어빵 틀로 찍은 붕어빵)
model.fit(X, y)              오차 제곱 합이 가장 작은 직선 찾기
                    │
coef_ 465.67  intercept_ 4727.98     (47의 정답 450, 5000)
                    │
model.predict(표) ──▶ 예측 ──▶ 채점(정답, 예측): MAE 2,510  RMSE 4,207  R² 0.80
```

- 선형 회귀는 `가격 = w × 면적 + b`의 직선을 찾아요. w는 면적이 1 늘 때 오르는 가격, b는 면적이 0일 때의 가격이에요.
- scikit-learn은 입력을 늘 표로 받아요. 열이 늘어날 수 있어서예요. 정답은 하나라 한 줄이에요. 그래서 `X`는 대괄호 두 겹, `y`는 한 겹이에요.
- `fit(X, y)`와 채점 함수는 자리 순서가 정해져 있어요. fit은 (문제, 정답), 채점은 (정답, 예측)이에요.
- 이름 끝에 밑줄이 붙은 `coef_`, `intercept_`는 fit을 한 뒤에 생기는 값이에요.
- `predict`에는 학습 때와 같은 열 이름의 표를 넣어요. 숫자 하나나 다른 열 이름은 오류가 나요.
- MAE는 오차 절댓값의 평균, MSE는 제곱의 평균, RMSE는 그 제곱근이에요. 셋은 작을수록 좋아요. R²는 평균만 찍을 때보다 오차를 얼마나 줄였는지라 1에 가까울수록 좋아요.
- 열 하나로 그은 직선에서는 상관계수의 제곱이 R²와 같아요(0.8967² = 0.8041).

## 실습

### 1. 패키지 더하기

47의 `ml-basics` 폴더에서 쳐요.

```bash
cd ml-basics
uv add scikit-learn
```

```
Resolved 50 packages in 114ms
Installed 6 packages in 17ms
 + cloudpickle==3.1.3
 + joblib==1.6.0
 + narwhals==2.29.0
 + scikit-learn==1.9.1
 + scipy==1.18.1
 + threadpoolctl==3.8.0
```

시간과 버전 숫자는 컴퓨터마다 달라요. `datasets/office.csv`가 없으면 47의 저장 셀을 실행하거나 이 폴더의 [datasets](datasets)에서 받아 넣어요. VS Code에서 `model.ipynb`를 만들고 커널은 `.venv`를 골라요(10).

### 2. 불러오기와 학습

맨 위에는 47과 같은 import 셀과 한글 글꼴 셀을 먼저 둬요.

```python
office = pd.read_csv("datasets/office.csv")
print(office.shape)
```

```
(200, 2)
```

```python
from sklearn.linear_model import LinearRegression

model = LinearRegression()

X = office[["area"]]
y = office["price"]
model.fit(X, y)

print("기울기 w:", model.coef_[0], "정답: 450")
print("절편 b:", model.intercept_, "정답: 5000")
```

```
기울기 w: 465.6735571178265 정답: 450
절편 b: 4727.983834181516 정답: 5000
```

정답과 가깝지만 똑같지 않아요. 47에서 가격에 흔들림과 특이 매물을 섞었기 때문이에요.

### 3. 예측하기

```python
new = pd.DataFrame({"area": [33, 59]})
model.predict(new).round(-1)
```

```
array([20100., 32200.])
```

### 4. 채점하기

```python
y_pred = model.predict(X)

from sklearn.metrics import mean_absolute_error, mean_squared_error, root_mean_squared_error, r2_score

print(f"MAE = {mean_absolute_error(y, y_pred):,.0f}")
print(f"MSE = {mean_squared_error(y, y_pred):,.0f}")
print(f"RMSE = {root_mean_squared_error(y, y_pred):,.0f}")
print(f"R2 = {r2_score(y, y_pred)}")
```

```
MAE = 2,510
MSE = 17,697,259
RMSE = 4,207
R2 = 0.8041321769128468
```

수업 노트북은 `y_pred = model.predict(X)`를 그래프 셀 첫 줄에 두었어요. 그래프는 슬라이드 17쪽에서 봐요.

### 5. 특이 매물 빼고 채점하기

```python
special = [17, 134, 178, 172, 122]

normal = np.ones(len(office), dtype=bool)
normal[special] = False
print("정상 매물:", normal.sum())
```

```
정상 매물: 195
```

```python
all_rows = np.ones(len(office), dtype=bool)
cases = [("전체 200건", all_rows), ("특이 매물 뺀 195건", normal)]

for name, mask in cases:
    y_true = y[mask]
    y_hat = y_pred[mask]
    mae = mean_absolute_error(y_true, y_hat)
    rmse = root_mean_squared_error(y_true, y_hat)
    r2 = r2_score(y_true, y_hat)
    print(f"{name} MAE {mae:,.0f} | RMSE {rmse:,.0f} | R2 {r2:.2f}")
```

```
전체 200건 MAE 2,510 | RMSE 4,207 | R2 0.80
특이 매물 뺀 195건 MAE 2,033 | RMSE 2,567 | R2 0.92
```

`cases` 둘째 칸에는 `normal`을 넣어요. `special`을 넣으면 특이 매물 다섯 건만 채점해서 R²가 -2.55로 나와요(32쪽).

## 명령어 요약

| 명령 | 하는 일 |
| --- | --- |
| `uv add scikit-learn` | 머신러닝 도구 넣기 (불러올 때는 `sklearn`) |
| `from sklearn.linear_model import LinearRegression` | 선형 회귀 설계도 불러오기 |
| `model = LinearRegression()` | 빈 모델 만들기 |
| `X = df[["열"]]` / `y = df["정답 열"]` | 문제는 표, 정답은 한 줄 |
| `model.fit(X, y)` | 학습 (문제 먼저, 정답 나중) |
| `model.coef_[0]` / `model.intercept_` | 찾은 기울기, 절편 |
| `model.predict(pd.DataFrame({"열": [값]}))` | 같은 열 이름의 표로 예측 |
| `df.sort_values("열")` | 직선을 그리기 전에 면적 순서로 정렬 |
| `mean_absolute_error(y, y_pred)` | MAE, 평균 몇만 원 틀리나 |
| `mean_squared_error(y, y_pred)` | MSE, 오차 제곱의 평균 |
| `root_mean_squared_error(y, y_pred)` | RMSE, MSE의 제곱근 |
| `r2_score(y, y_pred)` | R², 평균보다 얼마나 잘 맞나 |
| `np.ones(n, dtype=bool)` | True n개짜리 마스크 |
| `y[mask]` | True인 줄만 고르기 |

## 문제 해결

| 메시지 | 원인 | 해결 |
| --- | --- | --- |
| `ModuleNotFoundError: No module named 'sklearn'` | scikit-learn을 넣지 않았어요 | `uv add scikit-learn` 뒤 노트북 Restart |
| `ValueError: Expected a 2-dimensional container but got <class 'pandas.Series'> instead.` | X를 대괄호 한 겹으로 넣었거나 `fit(y, X)`로 순서를 바꿨어요 | `office[["area"]]`, `fit(X, y)` |
| `ValueError: Expected 2D array, got scalar array instead` | `predict(33)`처럼 숫자만 넣었어요 | `predict(pd.DataFrame({"area": [33]}))` |
| `ValueError: The feature names should match those that were passed during fit.` | 학습 때와 다른 열 이름의 표를 넣었어요 | 열 이름을 `area`로 맞추기 |
| `UserWarning: X does not have valid feature names` | 열 이름 없는 숫자나 리스트를 넣었어요 | 같은 열 이름의 DataFrame으로 넣기 |
| `NotFittedError: This LinearRegression instance is not fitted yet.` | fit 전에 predict했어요. 커널을 다시 켜도 모델이 비어요 | 맨 위 셀부터 차례로 실행 |
| 오류는 없는데 R²가 마이너스예요 | 마스크 자리에 번호 리스트(`special`)를 넣었어요 | `normal`을 넣고 `y[mask].shape`로 줄 수 확인 |
| R²가 조금 달라요 | 채점 함수에 (예측, 정답) 순서로 넣었어요 | 늘 (정답, 예측) 순서 |

## 강사용

<details>
<summary>수업 코드와 다르게 보여 준 곳</summary>

- 수업 노트북 마지막 셀의 `("특이 매물 뺀 195건", special)`은 `normal`이 맞아요. 덱은 고친 셀을 4파트에, 원래 셀과 그 결과(R² -2.55)를 5파트 함정 장에 보여 줘요.
- 오차 표(`errors`, `table`), 오차 절댓값 평균, 평균만 찍은 R², 상관계수 제곱, 오차 1만 넘는 줄 고르기, 다시 학습하기, 견적표는 이해를 도우려고 더한 셀이에요. 모두 같은 커널에서 실행한 출력이에요.
- 미국 집값 예제는 47의 `house`, `small`(2015년 이후 건축, 범죄율 45 미만 10채)을 먼저 만들고 실행했어요.
- 그래프 그림은 리눅스에서 만들어서 맑은 고딕 대신 나눔고딕으로 그렸어요.

</details>

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json                      슬라이드 순서와 파트 구분
  *.html                         한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
datasets/
  office.csv                     47에서 저장하는 연습 데이터 (수업 파일과 같아요)
  usa_housing.csv                47에서 쓴 미국 집값 300채
tools/
  gen.py                         이 챕터의 장 생성
  demo.sh                        uv 프로젝트를 만들고 노트북 셀을 실제로 실행
  run_nb.py                      demo.sh가 부르는 셀 실행기 (nbclient)
  demo.log                       슬라이드에 옮긴 실제 출력
  img/                           커널이 그린 그래프 그림
linear-regression-slides.html    배포용 HTML
linear-regression-slides.pdf     슬라이드 PDF
```

출력은 `FONT=나눔고딕.ttf bash tools/demo.sh /tmp/새폴더 > tools/demo.log 2>&1`로 다시 만들어요. 공용 도구는 맨 위 [tools/](../tools)에 있어요. 명령은 이 폴더에서 쳐요.

```bash
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/boxcheck.js slides
node ../tools/build_player.js slides linear-regression-slides.html
node ../tools/export.js slides linear-regression-slides.pdf
```

</details>

---

<!-- curriculum:nav -->

[← 이전: 47 · 그래프 그리기와 연습 데이터 만들기](../47-plot-data) · [커리큘럼](../README.md)

<!-- /curriculum:nav -->
