# 53 · 합격할 확률 구하기 (로지스틱 회귀)

> 머신러닝 기초 수업 노트북(`05_ml.ipynb`)을 한 챕터로 정리했어요. 50, 51에서는 점수(숫자)를 맞혔어요. 이번에는 같은 학생 10명으로 "60점을 넘었나(합격, 불합격)"를 맞히고, 합격할 확률이 몇 %인지 구해요. 분류와 회귀의 차이, 확률, S자 곡선이 0과 1 사이에 머무는 이유, 0.5 기준을 그림과 실제 숫자로 먼저 풀어요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/53-logistic-regression/logistic-regression-slides.html) · [PDF 받기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/53-logistic-regression/logistic-regression-slides.pdf) | [52 · 사진으로 사람 맞히기 (얼굴 데이터와 KNN)](../52-face-knn) | 준비 중 |

<!-- /curriculum:top -->

## 학습 목표

- 숫자를 맞히는 회귀와 보기 중에 고르는 분류의 차이를 말할 수 있어요.
- 직선(`LinearRegression`)으로 합격을 맞히면 0과 1 밖의 값이 나와서 확률로 못 읽는다는 것을 실제 결과로 확인해요.
- `y = df["score"] >= 60`으로 합격, 불합격 정답을 만들고, `stratify=y`로 학습용과 채점용의 합격 비율을 맞춰요.
- `iloc[행 번호, 열 번호]`와 `loc[이름표, 열 이름]`의 차이를 말할 수 있어요.
- `LogisticRegression`으로 학습하고 `classes_`, `coef_`, `intercept_`를 읽어요.
- 가중치를 곱해 더한 합계를 손으로 계산하고, S자 곡선이 그 합계를 0~1 확률로 바꾼다는 것을 숫자 표로 확인해요.
- `predict`와 `predict_proba`의 차이, 두 칸의 순서, `[0, 1]`과 `[:, 1]`로 합격 확률을 꺼내요.
- 가중치의 부호(+면 합격 쪽, -면 불합격 쪽)를 읽고, 적은 데이터로 배운 값을 조심해서 읽어요.

## 시작하기 전에

| 할 일 | 챕터 |
| --- | :---: |
| VS Code 노트북과 커널 고르기 | 10 |
| f-string 소수점 `:.2f`와 `:.2%`, `for` | 13 |
| 한 줄 `값1 if 조건 else 값2` | 17 |
| `range()` | 18 |
| `from 모듈 import 이름` | 28 |
| `ml-basics` 프로젝트, DataFrame, 열 비교의 True/False | 45 |
| `loc[이름표, 열 이름]` | 46 |
| `LinearRegression`, `fit`, `predict`, `coef_`, `intercept_` | 48 |
| 반복해서 조금씩 고치기(경사 하강법) | 49 |
| 학생 10명 표와 세 열 `X` | 50 |
| `train_test_split`, `StandardScaler`, `fit_transform`과 `transform` | 51 |

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 3~4 | 새 노트북 `logistic.ipynb`, 수업 셀 1(학생 10명과 `score >= 60`) |
| 1 · 왜 필요한가 | 5~8 | 직선으로 합격을 맞히면 -0.16과 1.19, 회귀와 분류, 확률은 0과 1 사이, 큰 그림(세 열, 합계, S자 곡선, 확률, 0.5 기준) |
| 2 · 정답 만들고 나누기 | 9~15 | `score >= 60`, `assign(passed=y)`, 51 다시 보기, `stratify=y`, 있을 때와 없을 때, `iloc`와 `loc`, 표준화 값 1.21 |
| 3 · 모델 만들기 | 16~19 | `LogisticRegression` 불러오기, 수업 셀 4와 `max_iter`, `classes_`, `coef_`와 `intercept_`, 가중치 부호 |
| 4 · 확률 구하기 | 20~28 | 수업 셀 6의 새 학생, 합계 -0.065 손 계산, S자 곡선, 0과 1 사이에 머무는 이유, `predict`, `predict_proba` 두 칸, 0.5 기준, `score`, 회귀와 KNN과 비교 |
| 5 · 오류와 함정 | 29~33 | 점수를 그대로 y에, `[0]`만 적기, `transform` 빼먹기, 너무 작은 `test_size`, 수면 가중치 -0.37 읽기 |
| 6 · 실제 상황 | 34~36 | 비어 있던 수업 셀 7(학생 다섯 명의 확률 표), 연습을 몇 번 더 하면 합격일까, 데이터 범위 밖 값 |
| 정리 | 37~39 | 막힐 때 보는 표, 단계 정리, 한 장으로 보는 코드 |

## 핵심 개념

```
X (세 열) ──▶ 표준화 ──▶ 가중치를 곱해 더한 합계 z ──▶ S자 곡선 ──▶ 합격 확률 (0~1) ──▶ 0.5보다 크면 True
                          0.873×공부 - 0.37×수면                       predict_proba          predict
                          + 0.877×연습 + 0.447
```

- 회귀는 점수처럼 숫자를 맞히고, 분류는 합격과 불합격처럼 정해진 보기 중 하나를 골라요. `LogisticRegression`은 이름에 회귀가 들어 있지만 분류 모델이에요.
- 확률은 0(절대 안 돼요)과 1(꼭 돼요) 사이의 숫자예요. 직선은 끝없이 올라가고 내려가서 -0.16, 1.19가 나와요.
- S자 곡선은 합계가 아무리 커도 1을 못 넘고, 아무리 작아도 0 밑으로 안 가요. 합계 0이 확률 50%예요.
- 가중치가 +면 그 열이 클수록 합격 쪽, -면 불합격 쪽으로 밀어요. 적은 데이터로 배운 값이라 원인으로 읽지 않아요.
- `predict_proba`는 `classes_` 순서([False, True])대로 불합격 확률과 합격 확률 두 칸을 줘요. 두 칸을 더하면 1이에요.
- `predict`는 합격 확률이 0.5보다 크면 True예요.

## 실습

### 1. 노트북 열기

48의 `ml-basics` 폴더를 그대로 써요. `LogisticRegression`은 48에서 넣은 scikit-learn 안에 있어서 새로 넣을 패키지는 없어요. VS Code에서 `logistic.ipynb`를 만들고 커널은 `.venv`를 골라요(10).

### 2. 데이터와 정답 (수업 셀 1)

```python
import pandas as pd

df = pd.DataFrame({
    "study_hours":    [1, 2, 3, 4, 5, 2, 3, 5, 4, 1],
    "sleep_hours":    [6, 8, 5, 7, 8, 5, 8, 6, 6, 8],
    "practice_count": [10, 15, 20, 25, 30, 12, 28, 22, 32, 8],
    "score":          [47, 58, 60, 76, 87, 49, 73, 77, 79, 52],
})

X = df[["study_hours", "sleep_hours", "practice_count"]]
y = df["score"] >= 60

print(f"학생 {len(X)} 명, X : {X.shape[1]}개")
print(df[["score"]].assign(passed=y).head())
```

```
학생 10 명, X : 3개
   score  passed
0     47   False
1     58   False
2     60    True
3     76    True
4     87    True
```

### 3. 나누고 표준화하기 (수업 셀 2)

```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# 학습용 vs 채점용 데이터 나누기
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

# 표준화
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print(f"학습 {len(X_train)}명, 채점 {len(X_test)}명")

# iloc[행 번호, 열 번호]
print(f"첫 학습 학생의 공부시간: {X_train.iloc[0, 0]} 시간")
print(f"표준화 값: {X_train_scaled[0, 0]:.2f}")
```

```
학습 7명, 채점 3명
첫 학습 학생의 공부시간: 4 시간
표준화 값: 1.21
```

`stratify=y`가 있으면 채점용이 `[False, True, True]`, 없으면 `[True, False, False]`예요. 전체 합격 비율(6:4)을 채점용에도 맞추려고 넣어요.

### 4. 모델 만들기 (수업 셀 4)

```python
from sklearn.linear_model import LogisticRegression

# 표준화된 학습 데이터 + 정답
model = LogisticRegression(max_iter=1000)
model.fit(X_train_scaled, y_train)

print("클래스 :", model.classes_.tolist())
print("가중치 :", model.coef_[0].round(3))
```

```
클래스 : [False, True]
가중치 : [ 0.873 -0.37   0.877]
```

### 5. 새 학생의 합격 확률 (수업 셀 6)

```python
new = pd.DataFrame(
    [[4, 7, 5]],
    columns=X.columns
)
new_scaled = scaler.transform(new)

predict = model.predict(new_scaled)[0]

pass_proba = model.predict_proba(new_scaled)[0, 1]

print("예측 결과:", "합격" if predict else "불합격")
print(f"합격 확률: {pass_proba:.2%}")
```

```
예측 결과: 불합격
합격 확률: 48.37%
```

`model.predict_proba(new_scaled)`는 `[[0.51633177 0.48366823]]`이에요. 0번 칸이 불합격 확률, 1번 칸이 합격 확률이고 더하면 1이에요.

### 6. 채점용 3명으로 채점하기

```python
print("정답:", list(y_test))
print("예측:", model.predict(X_test_scaled))
print("합격 확률:", model.predict_proba(X_test_scaled)[:, 1].round(3))
print("정확도:", model.score(X_test_scaled, y_test))
```

```
정답: [False, True, True]
예측: [False  True  True]
합격 확률: [0.459 0.941 0.95 ]
정확도: 1.0
```

### 7. 학생 여럿의 합격 확률 표 (수업 셀 7, 수업 노트북 다음 단계)

```python
students = pd.DataFrame({
    "study_hours":    [4, 2, 5, 3, 1],
    "sleep_hours":    [7, 7, 6, 8, 6],
    "practice_count": [5, 20, 25, 15, 30],
})
students_scaled = scaler.transform(students)

students["pass_proba"] = model.predict_proba(students_scaled)[:, 1].round(3)
students["passed"] = model.predict(students_scaled)
students.sort_values("pass_proba", ascending=False)
```

```
   study_hours  sleep_hours  practice_count  pass_proba  passed
2            5            6              25       0.956    True
4            1            6              30       0.653    True
1            2            7              20       0.502    True
0            4            7               5       0.484   False
3            3            8              15       0.475   False
```

## 명령어 요약

| 명령 | 하는 일 |
| --- | --- |
| `y = df["score"] >= 60` | 60점 이상이면 True인 정답 만들기 |
| `df[["score"]].assign(passed=y)` | 열을 붙인 사본 보기 (원래 표는 그대로) |
| `train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)` | 합격 비율을 맞춰 나누기 |
| `X_train.iloc[0, 0]` | 0번째 행, 0번째 열 (번호로 꺼내기) |
| `from sklearn.linear_model import LogisticRegression` | 로지스틱 회귀 불러오기 |
| `LogisticRegression(max_iter=1000)` | 반복 횟수 한도 1000으로 모델 만들기 |
| `model.classes_` | 보기 순서 (`[False, True]`) |
| `model.coef_[0]` / `model.intercept_` | 열마다 가중치 / 절편 |
| `model.decision_function(new_scaled)` | 가중치를 곱해 더한 합계 |
| `model.predict(new_scaled)` | True 또는 False |
| `model.predict_proba(new_scaled)[0, 1]` | 첫 학생의 합격 확률 |
| `model.predict_proba(X_test_scaled)[:, 1]` | 모든 학생의 합격 확률 |
| `model.score(X_test_scaled, y_test)` | 맞힌 비율 |
| `f"{p:.2%}"` | 100을 곱해 소수 둘째 자리까지, 끝에 % |

## 문제 해결

| 메시지 | 원인 | 해결 |
| --- | --- | --- |
| `classes_`가 `[47 52 60 73 76 77 87]`이에요 | y에 점수를 그대로 넣어서 점수 7개 중 하나를 고르는 분류가 됐어요 | `y = df["score"] >= 60`으로 True/False 정답 만들기 |
| `TypeError: unsupported format string passed to numpy.ndarray.__format__` | `predict_proba(...)[0]`만 적어서 두 칸이 남았어요 | `[0, 1]`로 합격 확률 한 칸만 꺼내기 |
| `UserWarning: X has feature names, but LogisticRegression was fitted without feature names`와 합격 확률 99.68% | 새 학생을 `scaler.transform` 없이 넣었어요 | `model.predict_proba(scaler.transform(new))` |
| `ValueError: The test_size = 1 should be greater or equal to the number of classes = 2` | 10명에 `test_size=0.1`이면 채점용이 1명이라 합격과 불합격을 다 못 담아요 | `test_size=0.3`처럼 보기 수 이상이 되게 하기 |
| 수면 가중치가 -0.37이라 잠을 자면 떨어진다고 읽었어요 | 7명으로 배운 값이고, 수면과 점수의 상관계수는 0.29예요 | 가중치는 원인이 아니라 이 데이터에서 배운 방향으로만 읽기 |
| 0.502인데 True라서 어색해 보여요 | 0.5를 조금이라도 넘으면 True예요 | `predict_proba`도 같이 보기 |

## 강사용

<details>
<summary>수업 코드와 다르게 보여 준 곳</summary>

- 수업 셀 2의 `print(f"표준화 값: {X_train_scaled[0, 0]:.2f} 시간")`은 표준화 값이 시간이 아니라 "표준편차 몇 개"라서 "시간"을 뺐어요(15쪽).
- 수업 주석의 "테스트용"은 51부터 쓰는 말에 맞춰 "채점용"으로 바꿨어요.
- 비어 있던 수업 셀 7은 학생 다섯 명의 합격 확률 표로 채우고 "수업 노트북 다음 단계"로 표시했어요(34쪽).
- 1파트의 직선으로 맞히기, 회귀와 분류, 확률, 2파트의 `stratify` 비교와 `loc` 비교, 3파트의 `n_iter_`와 기본값 100 비교, 4파트의 합계 손 계산, S자 곡선 숫자 표, 두 칸 더하기, `score`, 5파트, 6파트는 이해를 도우려고 더한 셀이에요.
- 강사 요청으로 기초 개념 장(6쪽 회귀와 분류, 7쪽 확률, 23쪽 S자 곡선이 0과 1 사이에 머무는 이유, 26쪽 0.5 기준, 19쪽 가중치 부호)을 더했어요. 시그모이드 식은 "참고, 읽기만"으로 한 줄만 보여 줘요.
- `max_iter=1000`이지만 실제로는 6번 만에 끝나서 기본값 100과 결과가 같아요(17쪽).
- 셀 번호는 덱 순서대로 다시 매겼어요. 장 제목의 "수업 셀 4, 6, 7"은 수업 노트북의 셀 번호예요.
- 모든 출력은 같은 커널에서 실제로 실행했어요.

</details>

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json                         슬라이드 순서와 파트 구분
  *.html                            한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py                            이 챕터의 장 생성
  demo.sh                           uv 프로젝트를 만들고 노트북 셀을 실제로 실행
  run_nb.py                         demo.sh가 부르는 셀 실행기 (nbclient)
  demo.log                          슬라이드에 옮긴 실제 출력
logistic-regression-slides.html     배포용 HTML
logistic-regression-slides.pdf      슬라이드 PDF
```

출력은 `bash tools/demo.sh /tmp/새폴더 > tools/demo.log 2>&1`로 다시 만들어요. 공용 도구는 맨 위 [tools/](../tools)에 있어요. 명령은 이 폴더에서 쳐요.

```bash
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/boxcheck.js slides
node ../tools/build_player.js slides logistic-regression-slides.html
node ../tools/export.js slides logistic-regression-slides.pdf
```

</details>

---

<!-- curriculum:nav -->

[← 이전: 52 · 사진으로 사람 맞히기 (얼굴 데이터와 KNN)](../52-face-knn) · [커리큘럼](../README.md)

<!-- /curriculum:nav -->
