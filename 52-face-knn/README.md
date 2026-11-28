# 52 · 사진으로 사람 맞히기 (얼굴 데이터와 KNN)

> 머신러닝 기초 수업 노트북(`04_ml.ipynb`)을 한 챕터로 정리했어요. 48~51에서는 숫자(집값, 점수)를 맞혔어요. 이번에는 얼굴 사진 400장(40명이 10장씩)을 보고 "몇 번 사람인지"를 맞혀요. 사진이 숫자 표라는 것부터 시작해서, 거리를 손으로 재 보고, 가장 가까운 사진 몇 장의 다수결로 사람을 맞히는 KNN(`KNeighborsClassifier`)까지 하나씩 쌓아요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/52-face-knn/face-knn-slides.html) · [PDF 받기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/52-face-knn/face-knn-slides.pdf) | [51 · 처음 보는 데이터로 채점하기 (나누기와 스케일링)](../51-train-test-split) | 준비 중 |

<!-- /curriculum:top -->

## 학습 목표

- 흑백 사진 한 장이 0(검정)~1(흰색) 숫자가 담긴 64×64 표라는 것을 실제 값으로 확인해요.
- `fetch_olivetti_faces`가 돌려주는 꾸러미의 `images`, `data`, `target`이 각각 무엇인지 말할 수 있어요.
- `plt.imshow(사진, cmap="gray", vmin=0, vmax=1)`의 칸마다 왜 그 값이 들어가는지 말할 수 있어요.
- 칸 세 개짜리 사진으로 거리(빼기, 제곱, 더하기, 제곱근)를 손으로 계산하고, 같은 계산을 NumPy로 해요.
- KNN이 "가장 가까운 K장의 다수결"이라는 것과 K에 따라 답이 바뀌는 것을 실제 결과로 봐요.
- `kneighbors`와 `predict`에 사진을 대괄호로 한 번 더 감싸서 넣는 이유를 말할 수 있어요.
- `train_test_split`에 `stratify`를 붙여 사람마다 채점용 장수를 고르게 나누고, `score`로 정확도를 재요.
- 회귀(숫자 맞히기)와 분류(무엇인지 맞히기)의 차이를 말할 수 있어요.

## 시작하기 전에

| 할 일 | 챕터 |
| --- | :---: |
| VS Code 노트북과 커널 고르기 | 10 |
| f-string과 소수점, 리스트 번호와 자르기 | 13 |
| `range`, `enumerate`, `for` 안의 `for` | 18 |
| `def`로 함수 만들기 | 19 |
| `from 모듈 import 이름` | 28 |
| `ml-basics` 프로젝트, 배열 계산, `arr[조건]` | 45 |
| 한글 글꼴 셀 | 46 |
| `fig, axes = plt.subplots()`, `axes[0]` | 47, 50 |
| `fit`, `predict`, 붕어빵 틀로 모델 만들기 | 48 |
| `train_test_split`, 학습용과 채점용 | 51 |

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 3~4 | 새 노트북 `face.ipynb`, 맨 위 셀과 사진 400장 받기 |
| 1 · 왜 필요한가 | 5~6 | 48~51은 숫자를 맞혔고 이번에는 사람을 맞혀요(분류), KNN 다섯 단계 그림 |
| 2 · 사진은 숫자 표 | 7~12 | 꾸러미(`images`, `data`, `target`), 칸 하나는 0~1 숫자, `imshow`와 `cmap` `vmin` `vmax`, 한 사람의 10장, 40명을 한 그림에 |
| 3 · 거리와 이웃 | 13~17 | 칸 세 개 사진으로 거리 손 계산, 같은 계산을 NumPy로, 64×64를 4096칸 한 줄로, 실제 얼굴 거리(같은 사람 6.26, 다른 사람 9.76), 가까운 3장의 다수결 |
| 4 · KNN 학습하고 채점하기 | 18~28 | `KNeighborsClassifier` 이름 풀기, 229번 사진 따로 두기, `fit`은 외우기만, `kneighbors`와 `predict`(대괄호 두 겹), K마다 바뀌는 답, `stratify`로 나누기, 정확도 87.00%와 손으로 세기, 회귀와 분류 비교 |
| 5 · 오류와 함정 | 29~33 | 대괄호 한 겹, 수업 코드의 이웃 제목, 사진보다 큰 K, 사람 수보다 작은 채점용, 다른 사람이 더 가까운 경우 |
| 6 · 실제 상황 | 34~35 | 이 데이터에 맞는 K 고르기(K=1 95%), 틀린 13장과 자주 헷갈리는 두 사람 |
| 정리 | 36~38 | 막힐 때 보는 표, 네 단계 정리, 한 장으로 보는 코드 |

## 핵심 개념

```
사진 400장 (40명 × 10장)
 └─ faces.data  (400, 4096)   사진 한 장을 4096칸 한 줄로 편 것   ──▶ X
 └─ faces.target (400,)       사진마다 몇 번 사람인지 (0~39)       ──▶ y

새 사진 ──▶ 400장 모두와 거리 재기 ──▶ 가까운 K장 고르기 ──▶ 그 K장의 사람 번호로 다수결 ──▶ 예측
```

- 흑백 사진은 칸마다 밝기 숫자가 담긴 표예요. 이 데이터는 0이 검정, 1이 흰색이에요.
- 거리는 칸마다 빼고, 제곱하고, 모두 더한 뒤 제곱근을 씌운 값이에요. 작을수록 비슷한 사진이에요.
- KNN(K-Nearest Neighbors)은 "가장 가까운 이웃 K명"이에요. 새 사진과 가까운 K장을 고르고 그 사진들의 사람 번호 중 가장 많은 쪽을 답해요.
- `fit`은 사진과 정답을 외워 두기만 해요. 거리 계산은 `predict`할 때 해요.
- K가 바뀌면 답이 바뀔 수 있어요. 229번 사진은 K=1이면 17번, K=3이면 22번(정답)이에요.
- 회귀는 숫자(점수, 집값)를 맞히고 R²로 채점해요. 분류는 무엇인지(사람 번호)를 맞히고 정확도(맞힌 비율)로 채점해요.

## 실습

### 1. 노트북 열기

48의 `ml-basics` 폴더를 그대로 써요. 얼굴 데이터를 받는 함수와 KNN은 48에서 넣은 scikit-learn 안에 있어서 새로 넣을 패키지는 없어요. VS Code에서 `face.ipynb`를 만들고 커널은 `.venv`를 골라요(10). 첫 실행에 인터넷에서 사진 파일을 받아요.

### 2. 불러오기와 사진 받기

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import fetch_olivetti_faces
```

글꼴 셀은 51과 같아요(46의 셀에 `plt.rcParams["axes.unicode_minus"] = False`를 더한 셀).

```python
faces = fetch_olivetti_faces(data_home="./datasets")
```

```
downloading Olivetti faces from https://ndownloader.figshare.com/files/5976027 to ./datasets
```

두 번째 실행부터는 출력 없이 `datasets` 폴더에서 바로 읽어요.

```python
print("사진 묶음 크기:", faces.images.shape)
print("정답 묶음 크기:", faces.target.shape)
print("사람 번호:", np.unique(faces.target))
```

```
사진 묶음 크기: (400, 64, 64)
정답 묶음 크기: (400,)
사람 번호: [ 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23
 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39]
```

### 3. 사진 한 장 보기

```python
plt.figure(figsize=(3, 3))
plt.imshow(faces.images[0], cmap="gray", vmin=0, vmax=1)
plt.title(f"Person {faces.target[0]}")
plt.axis("off")
plt.show()
```

`cmap="gray"`는 흑백으로, `vmin=0, vmax=1`은 0을 검정 1을 흰색으로 칠하라는 뜻이에요. 빼면 노랑과 보라로 칠해져요(10쪽).

### 4. 거리를 손으로, 그리고 NumPy로

```python
new = np.array([0.2, 0.8, 0.5])
a = np.array([0.3, 0.6, 0.5])
b = np.array([0.9, 0.1, 0.4])

print("new - a:", (new - a).round(2))
print("제곱:", ((new - a) ** 2).round(2))
print("더하기:", ((new - a) ** 2).sum().round(2))
print("거리 a:", np.sqrt(((new - a) ** 2).sum()).round(2))
print("거리 b:", np.sqrt(((new - b) ** 2).sum()).round(2))
```

```
new - a: [-0.1  0.2  0. ]
제곱: [0.01 0.04 0.  ]
더하기: 0.05
거리 a: 0.22
거리 b: 0.99
```

### 5. 사진 229번의 사람 맞히기

```python
from sklearn.neighbors import KNeighborsClassifier

X = faces.data
y = faces.target

new_index = 229
new_photo = X[new_index]

known = np.arange(400) != new_index
X_known, y_known = X[known], y[known]

K = 3
model = KNeighborsClassifier(n_neighbors=K)
model.fit(X_known, y_known)

dist, idx = model.kneighbors([new_photo], n_neighbors=K)
print("가장 가까운 이웃:", y_known[idx[0]])
print("이웃과의 거리:", dist[0].round(2))

pred = model.predict([new_photo])
print("예측한 사람:", pred[0])
print("실제 정답:", y[new_index])
```

```
가장 가까운 이웃: [17 22 22]
이웃과의 거리: [6.07 6.26 6.44]
예측한 사람: 22
실제 정답: 22
```

### 6. 나눠서 채점하기

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    faces.data,
    faces.target,
    test_size=0.25,
    random_state=42,
    stratify=faces.target
)

K = 5
model = KNeighborsClassifier(n_neighbors=K)
model.fit(X_train, y_train)

accuracy = model.score(X_test, y_test)
print(f"예측 정확도: {accuracy:.2%}")
```

```
예측 정확도: 87.00%
```

이웃 사진을 한 그림에 그리는 코드와 K 비교, 틀린 사진 찾기 코드는 슬라이드 21~23쪽, 34~35쪽에 있어요.

## 명령어 요약

| 명령 | 하는 일 |
| --- | --- |
| `from sklearn.datasets import fetch_olivetti_faces` | 얼굴 데이터 받는 함수 불러오기 |
| `faces = fetch_olivetti_faces(data_home="./datasets")` | 사진 400장을 `datasets` 폴더에 받아 읽기 |
| `faces.images` / `faces.data` / `faces.target` | 64×64 사진 / 4096칸 한 줄 / 사람 번호 |
| `plt.imshow(사진, cmap="gray", vmin=0, vmax=1)` | 0은 검정, 1은 흰색으로 그리기 |
| `np.sqrt(((a - b) ** 2).sum())` | 두 사진의 거리 |
| `from sklearn.neighbors import KNeighborsClassifier` | KNN 분류 모델 불러오기 |
| `KNeighborsClassifier(n_neighbors=5)` | 가까운 5장으로 다수결하는 모델 |
| `model.kneighbors([사진], n_neighbors=K)` | 가까운 K장의 거리와 번호 |
| `model.predict([사진])` | 사람 번호 예측 |
| `train_test_split(..., stratify=faces.target)` | 사람마다 채점용 장수를 고르게 |
| `model.score(X_test, y_test)` | 정확도(맞힌 비율) |

## 문제 해결

| 메시지 | 원인 | 해결 |
| --- | --- | --- |
| `ValueError: Expected 2D array, got 1D array instead` | 사진 한 장을 대괄호 없이 `predict(new_photo)`에 넣었어요 | `predict([new_photo])` |
| 이웃 사진 제목이 모두 `Person 22`예요 | 제목에 `y[new_index]`를 적었어요 | `y_known[j]` |
| `ValueError: Expected n_neighbors <= n_samples_fit` | K가 학습용 사진 수(300)보다 커요 | K를 사진 수보다 작게 |
| `ValueError: The test_size = 20 should be greater or equal to the number of classes = 40` | `stratify`를 쓰는데 채점용이 사람 수보다 적어요 | `test_size`를 0.1 이상으로 |
| 처음 실행에서 다운로드 오류 | 인터넷이 없어요 | 인터넷에 연결하고 다시 실행 |
| 사진이 노랑과 보라로 나와요 | `cmap="gray"`를 안 적었어요 | `cmap="gray", vmin=0, vmax=1` |

## 강사용

<details>
<summary>수업 코드와 다르게 보여 준 곳</summary>

- 이웃 사진 제목이 `y[new_index]`라서 세 장 모두 "Person 22"로 나왔어요. 실제로는 17번 사람이 섞여 있어서 `y_known[j]`로 고치고, 두 그림을 나란히 보여 줘요(30쪽).
- 주석의 "339장"은 399장으로 고쳤어요. 이웃 번호와 맞지 않던 주석은 뺐어요.
- 세 번째 출력의 이름표를 "사람 번호"로 바꿨어요.
- `grey`와 `gray`가 섞여 있어서 `gray`로 맞췄어요.
- `axex` 오타를 고치고, 아직 배우지 않은 `zip`은 `range(10)`으로 바꿨어요.
- 셀 15에서 데이터를 한 번 더 받던 줄은 뺐어요.
- 이웃 사진을 따로 그리던 그림들은 한 그림에 모았어요.
- 칸 세 개 사진의 거리 손 계산, 실제 얼굴 거리, K 비교, `stratify` 비교, 손으로 세는 정확도, 5파트, 6파트는 이해를 도우려고 더한 셀이에요.
- 모든 출력은 같은 커널에서 실제로 실행했어요. 그림은 리눅스에서 만들어서 맑은 고딕 대신 나눔고딕으로 그렸어요.

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
  img/                           커널이 그린 그림
face-knn-slides.html             배포용 HTML
face-knn-slides.pdf              슬라이드 PDF
```

출력은 `FONT=나눔고딕.ttf bash tools/demo.sh /tmp/새폴더 > tools/demo.log 2>&1`로 다시 만들어요. 공용 도구는 맨 위 [tools/](../tools)에 있어요. 명령은 이 폴더에서 쳐요.

```bash
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/boxcheck.js slides
node ../tools/build_player.js slides face-knn-slides.html
node ../tools/export.js slides face-knn-slides.pdf
```

</details>

---

<!-- curriculum:nav -->

[← 이전: 51 · 처음 보는 데이터로 채점하기 (나누기와 스케일링)](../51-train-test-split) · [커리큘럼](../README.md)

<!-- /curriculum:nav -->
