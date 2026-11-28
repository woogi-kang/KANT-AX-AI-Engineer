"""Runs the notebook cells shown in the deck with the project's own kernel and prints each output.
Used by tools/demo.sh (chapter 53, the class notebook 05_ml.ipynb: pass or fail from score >= 60, train_test_split with
stratify, StandardScaler, LogisticRegression, predict and predict_proba, and the empty last cell filled in).
Each run() is one fresh kernel, like opening the notebook and pressing Run All. Error lines keep only the last line of
the traceback. Warnings print as <stderr> lines."""
import nbclient
import nbformat


def run(cells):
    nb = nbformat.v4.new_notebook()
    nb.cells = [nbformat.v4.new_code_cell(c) for c in cells]
    nbclient.NotebookClient(nb, kernel_name="python3", allow_errors=True, timeout=300).execute()
    for c in nb.cells:
        print(f"--- [{c.execution_count}] {c.source!r}")
        for o in c.outputs:
            if o.output_type == "error":
                print(f"{o.ename}: {o.evalue}")
            elif o.output_type == "stream":
                print(f"<{o.name}>" if o.name == "stderr" else "", o.text, sep="")
            else:
                d = o.get("data", {})
                if "text/plain" in d:
                    print(d["text/plain"])


# class cell 1 (05_ml.ipynb), as in class
DATA = '''import pandas as pd

df = pd.DataFrame({
    "study_hours":    [1, 2, 3, 4, 5, 2, 3, 5, 4, 1],
    "sleep_hours":    [6, 8, 5, 7, 8, 5, 8, 6, 6, 8],
    "practice_count": [10, 15, 20, 25, 30, 12, 28, 22, 32, 8],
    "score":          [47, 58, 60, 76, 87, 49, 73, 77, 79, 52],
})

X = df[["study_hours", "sleep_hours", "practice_count"]]
y = df["score"] >= 60

print(f"학생 {len(X)} 명, X : {X.shape[1]}개")
print(df[["score"]].assign(passed=y).head())'''
# class cell 2, the last print without the wrong unit "시간"
SPLIT = '''from sklearn.model_selection import train_test_split
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
print(f"표준화 값: {X_train_scaled[0, 0]:.2f}")'''
# class cell 4
MODEL = '''from sklearn.linear_model import LogisticRegression

# 표준화된 학습 데이터 + 정답
model = LogisticRegression(max_iter=1000)
model.fit(X_train_scaled, y_train)

print("클래스 :", model.classes_.tolist())
print("가중치 :", model.coef_[0].round(3))'''
# class cell 6
NEW = '''new = pd.DataFrame(
    [[4, 7, 5]],
    columns=X.columns
)
new_scaled = scaler.transform(new)

predict = model.predict(new_scaled)[0]

pass_proba = model.predict_proba(new_scaled)[0, 1]

print("예측 결과:", "합격" if predict else "불합격")
print(f"합격 확률: {pass_proba:.2%}")'''
# class cell 7 was left empty: filled in for the deck
STUDENTS = '''students = pd.DataFrame({
    "study_hours":    [4, 2, 5, 3, 1],
    "sleep_hours":    [7, 7, 6, 8, 6],
    "practice_count": [5, 20, 25, 15, 30],
})
students_scaled = scaler.transform(students)

students["pass_proba"] = model.predict_proba(students_scaled)[:, 1].round(3)
students["passed"] = model.predict(students_scaled)
students.sort_values("pass_proba", ascending=False)'''
BASE = [DATA, SPLIT, MODEL]

print("=== start: 수업 셀 1", flush=True)
run([DATA, 'print(list(y))'])

print("=== why: 직선으로 합격 맞히기", flush=True)
run([DATA, '''from sklearn.linear_model import LinearRegression

line = LinearRegression()
line.fit(X, y)
print(line.predict(X).round(2))'''])

print("=== split: 수업 셀 2와 stratify", flush=True)
run([DATA, SPLIT, '''print("학습용:", list(y_train))
print("채점용:", list(y_test))''', '''X_train2, X_test2, y_train2, y_test2 = train_test_split(
    X, y, test_size=0.3, random_state=42
)
print("학습용:", list(y_train2))
print("채점용:", list(y_test2))''', '''print("학습용 학생:", list(X_train.index))
print("채점용 학생:", list(X_test.index))'''])

print("=== iloc: 번호로 꺼내기와 이름표로 꺼내기", flush=True)
run([DATA, SPLIT, '''print(list(X_train.index))
print(X_train.iloc[0, 0])
print(X_train.loc[0, "study_hours"])''', '''print("평균:", scaler.mean_[0].round(2))
print("표준편차:", scaler.scale_[0].round(2))
print((4 - 2.57) / 1.18)'''])

print("=== model: 수업 셀 4와 더 찍어 보기", flush=True)
run(BASE + ['''print("절편 :", model.intercept_.round(3))
print("반복 횟수:", model.n_iter_)
print(model.coef_.shape)''', '''m100 = LogisticRegression()
m100.fit(X_train_scaled, y_train)
print("기본값 100:", m100.coef_[0].round(3), m100.n_iter_)'''])

print("=== predict: 수업 셀 6", flush=True)
run(BASE + [NEW])

print("=== zsum: 가중치를 곱해 더한 합계", flush=True)
run(BASE + [NEW, '''print(new_scaled.round(2))
print((model.coef_[0] * new_scaled[0]).round(3))
z = (model.coef_[0] * new_scaled[0]).sum() + model.intercept_[0]
print(z.round(3))
print(model.decision_function(new_scaled).round(3))''', '''import numpy as np

for z in [-2, -0.065, 0, 2]:
    print(z, (1 / (1 + np.exp(-z))).round(4))'''])

print("=== sigwhy: S자 곡선이 0과 1 사이에 머무는 이유", flush=True)
run(['''import numpy as np

for z in [-10, -5, -2, 0, 2, 5, 10]:
    e = np.exp(-z)
    print(f"합계 {z:3}: np.exp(-z) = {e:10.4f}, 확률 = {1 / (1 + e):.4f}")'''])

print("=== psum: 두 칸을 더하면 1", flush=True)
run(BASE + [NEW, '''two = model.predict_proba(new_scaled)[0]
print("불합격 확률:", two[0].round(4))
print("합격 확률:", two[1].round(4))
print("더하면:", two.sum().round(4))'''])

print("=== proba: predict와 predict_proba 펼쳐 보기", flush=True)
run(BASE + [NEW, '''print(model.predict(new_scaled))
print(model.predict_proba(new_scaled))''', '''print(model.predict_proba(new_scaled)[0])
print(model.predict_proba(new_scaled)[0, 1])'''])

print("=== score: 채점용 3명", flush=True)
run(BASE + ['''print("정답:", list(y_test))
print("예측:", model.predict(X_test_scaled))
print("합격 확률:", model.predict_proba(X_test_scaled)[:, 1].round(3))
print("정확도:", model.score(X_test_scaled, y_test))''', '''print(df.loc[list(X_test.index), ["score"]])'''])

print("=== e-cont: 점수를 그대로 y에", flush=True)
run([DATA, SPLIT, '''from sklearn.linear_model import LogisticRegression

y_score = df["score"]
X_train, X_test, s_train, s_test = train_test_split(X, y_score, test_size=0.3, random_state=42)
X_train_scaled = scaler.fit_transform(X_train)

wrong = LogisticRegression(max_iter=1000)
wrong.fit(X_train_scaled, s_train)
print("클래스 :", wrong.classes_)''', '''new = pd.DataFrame([[4, 7, 5]], columns=X.columns)
print(wrong.predict(scaler.transform(new)))'''])

print("=== e-two: [0]만 적기", flush=True)
run(BASE + ['''new = pd.DataFrame([[4, 7, 5]], columns=X.columns)
new_scaled = scaler.transform(new)
pass_proba = model.predict_proba(new_scaled)[0]
print(f"합격 확률: {pass_proba:.2%}")'''])

print("=== e-raw: transform 안 한 새 학생", flush=True)
run(BASE + ['''new = pd.DataFrame([[4, 7, 5]], columns=X.columns)
print(model.predict(new))
print(model.predict_proba(new).round(4))'''])

print("=== e-small: 너무 작은 test_size와 stratify", flush=True)
run([DATA, '''from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.1, random_state=42, stratify=y
)'''])

print("=== e-sleep: 수면 가중치 -0.37 읽기", flush=True)
run(BASE + ['''print(df[["sleep_hours", "score"]].corr().round(2))''', '''for sleep in [5, 6, 7, 8]:
    one = pd.DataFrame([[4, sleep, 20]], columns=X.columns)
    p = model.predict_proba(scaler.transform(one))[0, 1]
    print(f"수면 {sleep}시간: {p:.2%}")'''])

print("=== x-table: 비어 있던 셀 7", flush=True)
run(BASE + [STUDENTS])

print("=== x-practice: 연습을 몇 번 더 하면", flush=True)
run(BASE + ['''for practice in range(5, 11):
    one = pd.DataFrame([[4, 7, practice]], columns=X.columns)
    p = model.predict_proba(scaler.transform(one))[0, 1]
    print(f"연습 {practice:2}번: {p:.2%}", "합격" if p >= 0.5 else "불합격")'''])

print("=== x-range: 범위 밖 값", flush=True)
run(BASE + ['''X.describe().loc[["min", "max"]]''', '''for practice in [8, 32, 60, 100]:
    one = pd.DataFrame([[4, 7, practice]], columns=X.columns)
    p = model.predict_proba(scaler.transform(one))[0, 1]
    print(f"연습 {practice:3}번: {p:.2%}")'''])
