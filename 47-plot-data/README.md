# 47 · 그래프 그리기와 연습 데이터 만들기

> 머신러닝 기초 수업의 두 번째 노트북 앞부분을 한 챕터로 정리했어요. matplotlib으로 선 그래프와 산점도를 그려 데이터를 눈으로 보고, NumPy 난수로 정답 규칙을 아는 오피스텔 시세 200건을 만들어 파일로 저장해요. 45, 46의 `ml-basics` 프로젝트와 pandas를 이어서 쓰고, 여기서 만든 `office.csv`로 다음 챕터에서 첫 머신러닝 모델을 만들어요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/47-plot-data/plot-data-slides.html) · [PDF 받기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/47-plot-data/plot-data-slides.pdf) | [46 · 데이터 정리하기 (타이타닉 전처리)](../46-data-cleaning) | [48 · 첫 머신러닝 모델 (선형 회귀)](../48-linear-regression) |

<!-- /curriculum:top -->

## 학습 목표

- matplotlib, NumPy 난수가 각각 무엇을 하는 도구인지 알고 `import ... as ...`로 불러와요.
- `fig, ax = plt.subplots(figsize=(6, 5))`로 그림판과 그래프 칸을 받고, `ax.plot(x, y, marker="o", label="매출")`의 자리마다 무엇이 들어가는지 말해요.
- `set_title`, `set_xlabel`, `set_ylabel`, `legend`로 그래프에 이름을 붙여요. `label`만 적고 `legend()`를 빼면 범례가 안 나와요.
- `pd.read_csv("datasets/파일.csv")`로 표를 불러오고 `plt.scatter`의 `alpha`, `color`, `s`로 점을 그려요.
- `corr()`로 두 열이 같이 움직이는 정도를 -1부터 1 사이 숫자로 보고, 점이 적으면 우연히 높게 나올 수 있다는 것을 알아요.
- `np.random.default_rng(42)`의 시드가 왜 필요한지 알고, `uniform`, `normal`, `choice`의 괄호 안 숫자가 각각 무엇인지 말해요.
- `round(-1)`로 10의 자리까지 반올림하고, `price[special] += 값`으로 고른 칸만 바꿔요.
- 만든 표를 `to_csv("경로", index=False)`로 저장하고, `index=False`가 없으면 생기는 `Unnamed: 0` 열을 알아봐요.

## 시작하기 전에

| 할 일 | 챕터 |
| --- | :---: |
| `uv add`, `uv add --dev` | 09 |
| VS Code 노트북, 커널 고르기 | 10 |
| 리스트, `len()`, `for` | 13 |
| `if`, `elif` | 17 |
| `+=`로 더해서 다시 담기 | 18 |
| `x, y = 함수()` | 19 |
| `import 모듈 as 별명` | 28 |
| `ml-basics` 프로젝트, 배열 계산, DataFrame, `df[(조건1) & (조건2)]` | 45 |
| `describe()`, 한글 글꼴 셀, `ax.hist` | 46 |

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1~3 | 표지, 목차, `datasets` 폴더와 `house.ipynb` 만들기 |
| 1 · 왜 필요한가 | 4~7 | 숫자만 봐서는 안 보이는 규칙, 머신러닝 다섯 단계 중 오늘의 자리, 도구 세 개, 가장 짧은 그래프 |
| 2 · matplotlib 그림판 | 8~13 | 첫 두 셀(불러오기, 글꼴), 그래프 각 부분의 이름, `plt.subplots`와 `figsize`, `ax.plot`의 네 자리, 이름 붙이기와 `legend`, `ax.`와 `plt.` 두 방식 |
| 3 · 산점도와 상관계수 | 14~18 | `pd.read_csv`와 경로, `plt.scatter`와 `alpha`, 두 번 찍기와 `color` `s` `label`, `corr()`, 점이 적을 때의 함정 |
| 4 · 연습 데이터 만들기 | 19~30 | 왜 직접 만드는지, 만드는 셀 전체, 시드, 부르는 순서, `uniform`, `normal`, `round(-1)`, 가격 공식, `choice`와 `replace`, `price[special] +=`, `describe()`로 확인, `to_csv`와 `index=False` |
| 5 · 오류와 함정 | 31~34 | 한글 글꼴 경고, `plot`으로 이은 실타래, x와 y 개수가 다를 때, 경로를 틀렸을 때 |
| 6 · 실제 상황 | 35~37 | 매출과 목표 두 줄 그래프, 만든 오피스텔 200건 그려 보기, 미국 집값은 어느 열이 가격과 관계있는지 |
| 정리 | 38~39 | 막힐 때 보는 표, 한 장으로 보는 오늘의 코드 |

## 핵심 개념

```
그래프로 보기 ─────────────▶ 연습 데이터 만들기 ──────────────▶ 저장
fig, ax = plt.subplots()       rng = np.random.default_rng(42)     office.to_csv(..., index=False)
ax.plot(x, y)  선               area  = rng.uniform(20, 85, 200)
plt.scatter(x, y)  점           price = area * 450 + 5000 + 잡음
df["a"].corr(df["b"])           special = rng.choice(200, 5, ...)
```

- 그림판(`fig`)은 바깥 종이 전체, 그래프 칸(`ax`)은 그 안에 선과 점을 그리는 칸이에요. 이름을 붙이는 명령은 `ax.set_`으로 시작해요.
- `plot`과 `scatter`는 둘 다 첫째 자리가 가로 x, 둘째 자리가 세로 y예요. 두 리스트는 같은 자리끼리 짝이라 개수가 같아야 해요.
- `plot`은 행 순서대로 점을 이어요. 월처럼 순서가 있는 데이터에 쓰고, 행마다 따로인 데이터는 `scatter`로 찍어요.
- 상관계수는 1에 가까우면 오른쪽 위로, -1에 가까우면 오른쪽 아래로 줄을 서고, 0 근처면 흩어져 있다는 뜻이에요.
- 컴퓨터 난수는 시작 번호(시드)로 정해지는 계산이에요. 시드가 같으면 같은 순서로 같은 숫자가 나와서 친구와 결과를 맞춰 볼 수 있어요.
- 실제 데이터는 정답 규칙을 아무도 몰라요. 규칙(가격 = 면적 × 450 + 5000)을 정해 두고 만든 데이터라야 모델이 규칙을 잘 찾았는지 확인할 수 있어요.

## 실습

### 1. 데이터 폴더 준비

45, 46의 `ml-basics` 폴더에서 쳐요. 수업에서 받은 `usa_housing.csv`를 `datasets` 폴더에 넣어요. 파일은 이 챕터의 [datasets](datasets) 폴더에도 있어요.

```bash
cd ml-basics
mkdir datasets
```

```
ml-basics/
├── datasets/
│   └── usa_housing.csv
├── house.ipynb
└── pyproject.toml
```

45, 46을 안 했다면 먼저 `uv init ml-basics`, `cd ml-basics`, `uv add numpy pandas`, `uv add --dev ipykernel`, `uv add seaborn matplotlib`을 쳐요. VS Code로 `ml-basics` 폴더를 열고 `house.ipynb`를 만든 뒤, 오른쪽 위 커널에서 `.venv`를 골라요(10).

### 2. 첫 두 셀

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
```

```python
import platform

os_name = platform.system()
if os_name == "Windows":
    plt.rcParams["font.family"] = "Malgun Gothic"
elif os_name == "Darwin":
    plt.rcParams["font.family"] = "AppleGothic"
```

### 3. 선 그래프

```python
fig, ax = plt.subplots(figsize=(6, 5))

months = ["1월", "2월", "3월", "4월", "5월", "6월"]
sales = [120, 135, 120, 160, 170, 190]

ax.plot(months, sales, marker="o", label="매출")
ax.set_title("My Mall 월 매출")
ax.set_xlabel("월")
ax.set_ylabel("매출(만원)")
ax.legend()
plt.show()
```

`figsize=(6, 5)`는 가로 6인치, 세로 5인치예요. 노트북에서는 가로 600, 세로 500픽셀쯤으로 보여요.

### 4. 산점도와 상관계수

```python
house = pd.read_csv("datasets/usa_housing.csv")
print(house.shape)
```

```
(300, 10)
```

```python
small = house[(house["YearBuilt"] > 2015) & (house["CrimeRate"] < 45)]

plt.figure(figsize=(6, 3))
plt.scatter(house["SquareFeet"], house["Price"], alpha=0.4, label="전체 300채")
plt.scatter(small["SquareFeet"], small["Price"], alpha=0.4, color="red", s=50, label="2015 이후 건축")
plt.xlabel("면적")
plt.ylabel("가격")
plt.legend()
plt.show()

print("전체 300채의 상관계수:", round(house["SquareFeet"].corr(house["Price"]), 2))
print("2015 이후 건축 상관계수:", round(small["SquareFeet"].corr(small["Price"]), 2))
```

```
전체 300채의 상관계수: 0.08
2015 이후 건축 상관계수: 0.89
```

300채 전체로는 관계가 거의 없는데, 고른 10채만 보면 높게 나와요. 점이 적으면 우연히 줄을 설 수 있어요.

### 5. 연습 데이터 만들기

```python
rng = np.random.default_rng(42)

n = 200
area = rng.uniform(20, 85, n)
price = area * 450 + 5000 + rng.normal(0, 2500, n).round(-1)

special = rng.choice(n, 5, replace=False)
price[special] += rng.uniform(15000, 25000, 5).round(-1)

office = pd.DataFrame({"area": area, "price": price})
office.describe().round(1)
```

```
        area    price
count  200.0    200.0
mean    52.1  28990.3
std     18.4   9529.3
min     20.5   9472.2
25%     36.4  21093.2
50%     51.1  29281.8
75%     68.6  36729.6
max     84.5  65581.6
```

| 코드 | 괄호 안 숫자 |
| --- | --- |
| `default_rng(42)` | 시드(시작 번호). 같으면 같은 난수가 나와요 |
| `uniform(20, 85, n)` | 가장 작은 값, 가장 큰 쪽 끝(85는 안 나와요), 개수 |
| `normal(0, 2500, n)` | 평균, 표준편차(퍼진 정도), 개수 |
| `.round(-1)` | 10의 자리까지 반올림 (`1234.5678` → `1230.0`) |
| `choice(n, 5, replace=False)` | 0부터 n-1번 중에서, 5개, 뽑은 번호는 다시 안 넣기 |

시드 42를 똑같이 쓰면 위 표와 같은 숫자가 나와요. 셀을 나눠 실행하거나 순서를 바꾸면 달라져요.

### 6. 저장하고 그려 보기

```python
office.to_csv("datasets/office.csv", index=False)
```

```python
plt.figure(figsize=(8, 5))
plt.scatter(office["area"], office["price"], alpha=0.6)
plt.title("오피스텔 시세 200건")
plt.xlabel("면적")
plt.ylabel("가격")
plt.show()

print("상관계수:", office["area"].corr(office["price"]))
```

```
상관계수: 0.8967341729369117
```

점이 오른쪽 위로 곧게 올라가고, 위로 뜬 점 다섯 개가 `special`로 값을 올린 특이 매물이에요.

## 명령어 요약

| 명령 | 하는 일 |
| --- | --- |
| `import matplotlib.pyplot as plt` | 그래프 도구 불러오기 |
| `fig, ax = plt.subplots(figsize=(가로, 세로))` | 그림판과 그래프 칸 받기 (인치) |
| `ax.plot(x, y, marker="o", label="이름")` | 선 그래프 |
| `ax.set_title()` `ax.set_xlabel()` `ax.set_ylabel()` | 제목, 가로축 이름, 세로축 이름 |
| `ax.legend()` | `label`을 모아 범례 그리기 |
| `plt.figure(figsize=(8, 5))` | 그림판만 만들기 (`plt.`로 바로 그릴 때) |
| `plt.scatter(x, y, alpha=0.4, color="red", s=50)` | 산점도 (투명도, 색, 점 넓이) |
| `plt.show()` | 그림을 셀 아래에 보여 주기 |
| `pd.read_csv("datasets/파일.csv")` | CSV 파일을 표로 불러오기 |
| `df["a"].corr(df["b"])` | 두 열의 상관계수 (-1 ~ 1) |
| `rng = np.random.default_rng(42)` | 시드를 정한 난수 기계 |
| `rng.uniform(작은 값, 큰 값, 개수)` | 범위 안에서 고르게 |
| `rng.normal(평균, 표준편차, 개수)` | 종 모양으로 퍼지게 |
| `rng.choice(n, 개수, replace=False)` | 번호 뽑기 (겹치지 않게) |
| `배열.round(-1)` | 10의 자리까지 반올림 |
| `배열[번호배열] += 값` | 고른 칸만 더해서 다시 담기 |
| `df.to_csv("경로", index=False)` | 행 번호 없이 CSV로 저장 |

## 문제 해결

| 메시지 | 원인 | 해결 |
| --- | --- | --- |
| `ModuleNotFoundError: No module named 'matplotlib'` | 프로젝트에 넣지 않았어요 | `uv add matplotlib` 뒤 노트북 Restart |
| `FileNotFoundError: [Errno 2] No such file or directory: 'usa_housing.csv'` | 경로에 폴더 이름이 빠졌거나 파일을 다른 폴더에 뒀어요 | `"datasets/usa_housing.csv"`, 파일 위치 확인 |
| `ValueError: x and y must have same first dimension, but have shapes (6,) and (5,)` | x와 y 리스트 개수가 달라요 | `len()`으로 세고 빠진 값 채우기 |
| `UserWarning: Glyph 47588 (\N{HANGUL SYLLABLE MAE}) missing from font(s) DejaVu Sans.` | 한글 글꼴을 정하지 않았어요 | 글꼴 셀을 먼저 실행 |
| 범례가 안 나와요 | `label`만 적고 `legend()`를 안 불렀어요 | `ax.legend()` 또는 `plt.legend()` |
| 선이 실타래처럼 엉켜요 | 순서 없는 데이터를 `plot`으로 이었어요 | `scatter`로 찍기 |
| 다시 불러온 표에 `Unnamed: 0` 열이 있어요 | `to_csv`에 `index=False`를 빼고 저장했어요 | `index=False`를 붙여 다시 저장 |
| 친구나 슬라이드와 난수가 달라요 | 시드를 안 정했거나 셀을 나눠, 또는 여러 번 실행했어요 | `default_rng(42)` 셀을 처음부터 한 번 실행 |

## 강사용

<details>
<summary>수업 코드와 다르게 보여 준 곳</summary>

- 수업 노트북(`02_ml.ipynb`)의 앞부분(그래프, 산점도, 연습 데이터)이 이 챕터예요. 모델 학습, 예측, 평가는 다음 챕터로 나눴어요.
- 노트북 맨 끝 평가 셀은 특이 매물(`special`) 대신 정상 매물(`normal`)로 고쳐야 맞아요. 다음 챕터에서 고친 코드와 실제 결과로 보여 줘요.
- 시드 없이 실행한 난수 두 줄은 실행할 때마다 달라요. 슬라이드에 그렇게 적어 뒀어요.
- 그래프 그림은 리눅스에서 만들어서 맑은 고딕 대신 나눔고딕으로 그렸어요.

</details>

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
datasets/
  usa_housing.csv            수업에서 받은 미국 집값 300채
slides/
  deck.json                  슬라이드 순서와 파트 구분
  *.html                     한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py                     이 챕터의 장 생성
  demo.sh                    uv 프로젝트를 만들고 노트북 셀을 실제로 실행
  run_nb.py                  demo.sh가 부르는 셀 실행기 (nbclient)
  demo.log                   슬라이드에 옮긴 실제 출력
  img/                       커널이 그린 그래프 그림
plot-data-slides.html        배포용 HTML
plot-data-slides.pdf         강사용 PDF
```

출력은 `FONT=나눔고딕.ttf bash tools/demo.sh /tmp/새폴더 > tools/demo.log 2>&1`로 다시 만들어요. `demo.sh`는 다음 챕터에서 쓸 학습, 평가 셀까지 같이 실행해서 `scikit-learn`도 넣어요. 공용 도구는 맨 위 [tools/](../tools)에 있어요. 명령은 이 폴더에서 쳐요.

```bash
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/boxcheck.js slides
node ../tools/build_player.js slides plot-data-slides.html
node ../tools/export.js slides plot-data-slides.pdf
```

</details>

---

<!-- curriculum:nav -->

[← 이전: 46 · 데이터 정리하기 (타이타닉 전처리)](../46-data-cleaning) · [커리큘럼](../README.md) · [다음: 48 · 첫 머신러닝 모델 (선형 회귀) →](../48-linear-regression)

<!-- /curriculum:nav -->
