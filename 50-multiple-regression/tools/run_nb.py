"""Runs the notebook cells shown in the deck with the project's own kernel and prints each output.
Used by tools/demo.sh (chapter 50, the multiple regression part of the class notebook 03_ml.ipynb and the steps after it). Each run() is one fresh kernel, like opening the notebook and pressing Run All.
Error lines keep only the last line of the traceback. Charts are saved as PNG files in $SHOTS."""
import base64
import os

import nbclient
import nbformat

SHOTS = os.environ.get("SHOTS", "shots")
FONT = os.environ.get("FONT", "")
os.makedirs(SHOTS, exist_ok=True)


def mpl(kind):
    """Each kernel reads matplotlib settings from its own folder. "plain" is matplotlib as installed (charts at 200 dpi).
    "ko" adds the Korean font that stands in for Malgun Gothic or AppleGothic, so the class's font cell (which sets
    nothing on Linux) draws the same chart students see on Windows or Mac."""
    d = os.path.abspath(".mpl-" + kind)   # inside the demo folder, not the repo
    os.makedirs(d, exist_ok=True)
    rc = "figure.dpi: 200\n"
    if kind == "ko" and FONT:
        rc += "font.family: NanumGothic\n"
    with open(os.path.join(d, "matplotlibrc"), "w") as f:
        f.write(rc)
    os.environ["MPLCONFIGDIR"] = d
    os.environ.pop("MATPLOTLIBRC", None)   # a machine-wide rc would win over the folder above


def run(cells, name=None, kind="ko"):
    mpl(kind)
    nb = nbformat.v4.new_notebook()
    nb.cells = [nbformat.v4.new_code_cell(c) for c in cells]
    nbclient.NotebookClient(nb, kernel_name="python3", allow_errors=True, timeout=300).execute()
    k = 0
    for c in nb.cells:
        print(f"--- [{c.execution_count}] {c.source!r}")
        for o in c.outputs:
            if o.output_type == "error":
                print(f"{o.ename}: {o.evalue}")
            elif o.output_type == "stream":
                print(f"<{o.name}>" if o.name == "stderr" else "", o.text, sep="")
            else:
                d = o.get("data", {})
                if "image/png" in d and name:
                    k += 1
                    fn = os.path.join(SHOTS, f"{name}-{k}.png")
                    with open(fn, "wb") as f:
                        f.write(base64.b64decode(d["image/png"]))
                    print(f"<image saved {fn}>")
                if "text/plain" in d:
                    print(d["text/plain"])






IMPORTS = '''import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns'''
FONTCELL = '''import platform

os_name = platform.system()
if os_name == "Windows":
    plt.rcParams["font.family"] = "Malgun Gothic"
elif os_name == "Darwin":
    plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False'''
FONT_NOMINUS = FONTCELL.rsplit("\n", 1)[0]
DATA = '''df = pd.DataFrame({
    "study_hours":    [1, 2, 3, 4, 5, 2, 3, 5, 4, 1],
    "sleep_hours":    [6, 8, 5, 7, 8, 5, 8, 6, 6, 8],
    "practice_count": [10, 15, 20, 25, 30, 12, 28, 22, 32, 8],
    "score":          [47, 58, 60, 76, 87, 49, 73, 77, 79, 52]
})
df'''
ONE = '''from sklearn.linear_model import LinearRegression

one = LinearRegression()
one.fit(df[["study_hours"]], df["score"])
print("기울기:", one.coef_[0], "절편:", one.intercept_)
two = df.loc[[1, 5]]
print(two)
print("예측:", one.predict(two[["study_hours"]]))'''
SCATTER = '''fig, axes = plt.subplots(1, 3, figsize=(16, 5))

sns.scatterplot(data=df, x="study_hours", y="score", ax=axes[0])
sns.scatterplot(data=df, x="sleep_hours", y="score", ax=axes[1])
sns.scatterplot(data=df, x="practice_count", y="score", ax=axes[2])

plt.show()'''
CORR = '''corr = df.corr()
corr.round(2)'''
HEAT = '''plt.figure(figsize=(7, 5))

sns.heatmap(
    corr,
    annot=True,
    vmin=-1,
    vmax=1,
    fmt=".2f"
)

plt.show()'''
XY = '''X = df[["study_hours", "sleep_hours", "practice_count"]]
y = df["score"]
print(X.shape, y.shape)'''
FIT = '''model = LinearRegression()
model.fit(X, y)

print("기울기 w:", model.coef_)
print("절편 b:", model.intercept_)'''
COEF = '''print("공부 1시간:", model.coef_[0].round(2))
print("수면 1시간:", model.coef_[1].round(2))
print("문제 1개:", model.coef_[2].round(2))'''
PRED = '''new = pd.DataFrame({"study_hours": [3], "sleep_hours": [7], "practice_count": [20]})
model.predict(new)'''
HAND = '''w = model.coef_
b = model.intercept_
print(3 * w[0] + 7 * w[1] + 20 * w[2] + b)'''
SCORE = '''from sklearn.metrics import mean_absolute_error, r2_score

y_pred = model.predict(X)
print(f"세 열 MAE {mean_absolute_error(y, y_pred):.2f} | R2 {r2_score(y, y_pred):.2f}")

p1 = one.predict(df[["study_hours"]])
print(f"공부 열 MAE {mean_absolute_error(y, p1):.2f} | R2 {r2_score(y, p1):.2f}")'''
TRUEPRED = '''plt.figure(figsize=(6, 5))
plt.scatter(y, y_pred, s=60, label="학생 10명")
plt.plot([40, 90], [40, 90], color="red", label="정답 = 예측")
plt.xlabel("정답 점수")
plt.ylabel("예측 점수")
plt.legend()
plt.show()'''
EACH = '''cols = ["study_hours", "sleep_hours", "practice_count"]
for col in cols:
    m = LinearRegression()
    m.fit(df[[col]], y)
    r2 = r2_score(y, m.predict(df[[col]]))
    print(f"{col:15} 혼자 기울기 {m.coef_[0]:5.2f} | R2 {r2:.2f}")'''
NOSLEEP = '''two_cols = ["study_hours", "practice_count"]
m2 = LinearRegression()
m2.fit(df[two_cols], y)
print(f"수면 뺀 두 열 R2 {r2_score(y, m2.predict(df[two_cols])):.2f}")
print(f"세 열 R2 {r2_score(y, y_pred):.2f}")'''
PLAN = '''plan = pd.DataFrame({
    "study_hours":    [2, 3, 2, 2],
    "sleep_hours":    [6, 6, 7, 6],
    "practice_count": [15, 15, 15, 25]
})
pred = model.predict(plan)
plan["예상 점수"] = pred.round(1)
plan'''
ERRT = '''table = df.copy()
table["예측"] = y_pred.round(1)
table["오차"] = (table["score"] - table["예측"]).round(1)
table["오차 크기"] = table["오차"].abs()
table.sort_values(by="오차 크기", ascending=False).head(3)'''
CORE = [IMPORTS, FONTCELL, DATA.replace("\ndf", ""), ONE.split("\nprint")[0], XY, FIT.split("\n\nprint")[0]]

print("=== main: multi.ipynb, 수업 순서 그대로 뒤에 학습 단계", flush=True)
run([IMPORTS, FONTCELL, DATA, ONE, SCATTER, CORR, HEAT, XY, FIT, COEF, PRED, HAND, SCORE, TRUEPRED, EACH, NOSLEEP, PLAN, ERRT,
     'print(type(axes))\nprint(axes.shape)',
     'X.head(3)',
     'model.coef_.shape',
     'new',
     '''more = pd.DataFrame({
    "study_hours":    [3, 4, 3, 3],
    "sleep_hours":    [7, 7, 8, 7],
    "practice_count": [20, 20, 20, 21]
})
model.predict(more).round(2)''',
     ], "main")

print("=== heat-nov: vmin, vmax 없이", flush=True)
run([IMPORTS, FONTCELL, DATA.replace("\ndf", ""), 'corr = df.corr()', HEAT.replace("    vmin=-1,\n    vmax=1,\n", "")], "nov")

print("=== heat-nofmt: annot만", flush=True)
run([IMPORTS, FONTCELL, DATA.replace("\ndf", ""), 'corr = df.corr()', HEAT.replace(',\n    fmt=".2f"', '')], "nofmt")

print("=== minus: unicode_minus 없이", flush=True)
run([IMPORTS, FONT_NOMINUS, DATA.replace("\ndf", ""), 'corr = df.corr()', HEAT], "minus")

print("=== e-font: 수업 코드 AppleGothic 그대로", flush=True)
run([IMPORTS, 'plt.rcParams["font.family"] = "AppleGothic"', DATA.replace("\ndf", ""), '''plt.figure(figsize=(6, 4))
plt.scatter(df["study_hours"], df["score"])
plt.title("공부 시간과 점수")
plt.xlabel("공부 시간")
plt.ylabel("점수")
plt.show()'''], "efont", kind="plain")

print("=== e-ax: ax= 없이", flush=True)
run([IMPORTS, FONTCELL, DATA.replace("\ndf", ""), SCATTER.replace(", ax=axes[0]", "").replace(", ax=axes[1]", "").replace(", ax=axes[2]", "")], "eax")

print("=== e-order: predict 표의 열 순서와 빠진 열", flush=True)
run(CORE + ['model.predict(pd.DataFrame({"sleep_hours": [7], "study_hours": [3], "practice_count": [20]}))',
            'model.predict(pd.DataFrame({"study_hours": [3], "practice_count": [20]}))',
            'model.predict(pd.DataFrame({"study_hours": [3], "sleep_hours": [7], "practice_count": [20]}))'])

print("=== e-key: 대괄호 한 겹", flush=True)
run(CORE + ['df["study_hours", "sleep_hours"]', 'model.fit(df["study_hours"], y)'])
