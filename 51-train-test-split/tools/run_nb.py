"""Runs the notebook cells shown in the deck with the project's own kernel and prints each output.
Used by tools/demo.sh (chapter 51, cells 48 to 58 of the class notebook 03_ml.ipynb: train_test_split, StandardScaler,
SGDRegressor on three scaled columns, the w curves). Each run() is one fresh kernel, like opening the notebook and
pressing Run All. Error lines keep only the last line of the traceback. Charts are saved as PNG files in $SHOTS."""
import base64
import os

import nbclient
import nbformat

SHOTS = os.environ.get("SHOTS", "shots")
FONT = os.environ.get("FONT", "")
os.makedirs(SHOTS, exist_ok=True)


def mpl(kind):
    """Each kernel reads matplotlib settings from its own folder. "ko" adds the Korean font that stands in for
    Malgun Gothic or AppleGothic, so the font cell (which sets nothing on Linux) draws what students see."""
    d = os.path.abspath(".mpl-" + kind)
    os.makedirs(d, exist_ok=True)
    rc = "figure.dpi: 200\n"
    if kind == "ko" and FONT:
        rc += "font.family: NanumGothic\n"
    with open(os.path.join(d, "matplotlibrc"), "w") as f:
        f.write(rc)
    os.environ["MPLCONFIGDIR"] = d
    os.environ.pop("MATPLOTLIBRC", None)


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
from sklearn.linear_model import LinearRegression, SGDRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score'''
FONTCELL = '''import platform

os_name = platform.system()
if os_name == "Windows":
    plt.rcParams["font.family"] = "Malgun Gothic"
elif os_name == "Darwin":
    plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False'''
DATA = '''df = pd.DataFrame({
    "study_hours":    [1, 2, 3, 4, 5, 2, 3, 5, 4, 1],
    "sleep_hours":    [6, 8, 5, 7, 8, 5, 8, 6, 6, 8],
    "practice_count": [10, 15, 20, 25, 30, 12, 28, 22, 32, 8],
    "score":          [47, 58, 60, 76, 87, 49, 73, 77, 79, 52]
})
features = ["study_hours", "sleep_hours", "practice_count"]
X = df[features]
y = df["score"]'''
ALL = '''model = LinearRegression()
model.fit(X, y)
y_pred = model.predict(X)
print(f"MAE: {mean_absolute_error(y, y_pred):.4f}")
print(f"R2: {r2_score(y, y_pred):.4f}")'''
SPLIT = '''from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.3,
    random_state=42
)

print("X_train:", X_train.shape)
print("X_test:", X_test.shape)
print("y_train:", y_train.shape)
print("y_test:", y_test.shape)'''
SHOWTEST = '''print("학습용 학생:", list(X_train.index))
print("채점용 학생:", list(X_test.index))'''
TESTTBL = '''X_test'''
YTEST = '''y_test'''
LRTEST = '''test_model = LinearRegression()
test_model.fit(X_train, y_train)

test_pred = test_model.predict(X_test)

print(f"MAE: {mean_absolute_error(y_test, test_pred):.4f}")
print(f"MSE: {mean_squared_error(y_test, test_pred):.4f}")
print(f"R2: {r2_score(y_test, test_pred):.4f}")'''
TESTPREDS = '''print("정답:", list(y_test))
print("예측:", test_pred.round(1))'''
TRAINSCORE = '''train_pred = test_model.predict(X_train)
print(f"학습용 7명 R2: {r2_score(y_train, train_pred):.4f}")
print(f"채점용 3명 R2: {r2_score(y_test, test_pred):.4f}")'''
DESCRIBE = '''X.describe().round(2)'''
SCALE = '''from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

scaled_df = pd.DataFrame(X_train_scaled, columns=features)
scaled_df.round(2)'''
SCALERAW = '''X_train_scaled[:2]'''
MEANS = '''print("평균:", scaler.mean_.round(2))
print("표준편차:", scaler.scale_.round(2))'''
HAND = '''x = X_train["study_hours"]
print(list(x))
print("평균:", x.mean().round(2))
print("표준편차:", x.std(ddof=0).round(2))
print("첫 학생:", ((x.iloc[0] - x.mean()) / x.std(ddof=0)).round(2))'''
CHECK = '''scaled_df.describe().round(2)'''
NPCHECK = '''print("평균:", X_train_scaled.mean(axis=0).round(2))
print("표준편차:", X_train_scaled.std(axis=0).round(2))'''
LRCOEF = '''print("기울기 w:", test_model.coef_.round(2))
print("절편 b:", test_model.intercept_.round(2))'''
TESTSCALED = '''pd.DataFrame(X_test_scaled, columns=features, index=X_test.index).round(2)'''
SGD = '''sgd = SGDRegressor(
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
print(f"R2: {r2_score(y_test, sgd_pred):.4f}")'''
NITER = '''print("반복한 epoch:", sgd.n_iter_)
print("기울기 w:", sgd.coef_.round(2))
print("절편 b:", sgd.intercept_.round(2))'''
SGDRAW = '''raw = SGDRegressor(
    loss="squared_error",
    learning_rate="constant",
    eta0=0.01,
    max_iter=3000,
    random_state=42
)

raw.fit(X_train, y_train)
print("기울기 w:", raw.coef_)
print("예측:", raw.predict(X_test))'''
LOOP = '''sgd = SGDRegressor(
    loss="squared_error",
    learning_rate="constant",
    eta0=0.01,
    random_state=42
)

epochs = 500
history = []

for epoch in range(epochs):
    sgd.partial_fit(X_train_scaled, y_train)
    pred = sgd.predict(X_train_scaled)
    history.append({
        "epoch": epoch + 1,
        "w1": sgd.coef_[0],
        "w2": sgd.coef_[1],
        "w3": sgd.coef_[2],
        "bias": sgd.intercept_[0],
        "mse": mean_squared_error(y_train, pred),
    })

history_df = pd.DataFrame(history)
history_df.round(2).tail()'''
HEAD = '''history_df.round(2).head(3)'''
LOSS = '''plt.figure(figsize=(6, 4))
plt.plot(history_df["epoch"], history_df["mse"])
plt.title("학습 곡선")
plt.xlabel("epoch")
plt.ylabel("MSE")
plt.show()'''
WCURVE = '''fig, ax = plt.subplots(figsize=(10, 5))

ax.plot(history_df["epoch"], history_df["w1"], label="study")
ax.plot(history_df["epoch"], history_df["w2"], label="sleep")
ax.plot(history_df["epoch"], history_df["w3"], label="count")

ax.set_title("기울기 w1, w2, w3의 변화")
ax.set_xlabel("epoch")
ax.legend()
ax.grid(alpha=0.3)
plt.show()'''
BARH = '''coef_df = pd.DataFrame({
    "feature": features,
    "weight": sgd.coef_,
})

plt.figure(figsize=(6, 4))
plt.barh(coef_df["feature"], coef_df["weight"], color="blue")
plt.title("스케일링한 열의 기울기")
plt.show()'''
BARH_RAW = '''raw_coef = pd.DataFrame({
    "feature": features,
    "weight": test_model.coef_,
})

plt.figure(figsize=(6, 4))
plt.barh(raw_coef["feature"], raw_coef["weight"], color="gray")
plt.title("스케일링 안 한 열의 기울기")
plt.show()'''

BASE = [IMPORTS, FONTCELL, DATA]
SPLITC = BASE + [SPLIT]
SCALEC = SPLITC + [SCALE]

print("=== main: 수업 셀 48~58 순서", flush=True)
run(BASE + ["df", ALL, SPLIT, SHOWTEST, TESTTBL, YTEST, LRTEST, TESTPREDS, TRAINSCORE, LRCOEF, DESCRIBE, SCALE, SCALERAW, MEANS, HAND, CHECK, NPCHECK, TESTSCALED,
            SGD, NITER, LOOP, HEAD, LOSS, WCURVE, BARH, LRTEST, BARH_RAW], "main")

print("=== seed: random_state 없이 두 번", flush=True)
run(BASE + ['from sklearn.model_selection import train_test_split', '''X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
print("채점용 학생:", list(X_test.index))''', '''X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)
print("채점용 학생:", list(X_test.index))''', '''X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
print("채점용 학생:", list(X_test.index))''', '''X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
print("채점용 학생:", list(X_test.index))'''])

print("=== sizes: test_size 바꿔 보기", flush=True)
run(BASE + ['from sklearn.model_selection import train_test_split', '''for size in [0.2, 0.3, 0.5]:
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=size, random_state=42)
    print(size, "→ 학습용", len(X_train), "명, 채점용", len(X_test), "명")''', '''X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=3, random_state=42)
print(len(X_train), len(X_test))'''])

print("=== sgd-raw: 스케일링 없이 SGD", flush=True)
run(SPLITC + [SGDRAW])

print("=== e-order: 네 칸 순서를 바꿔 적기", flush=True)
run(BASE + ['''from sklearn.model_selection import train_test_split

X_train, y_train, X_test, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42
)
print("y_train:", y_train.shape)''', '''m = LinearRegression()
m.fit(X_train, y_train)'''])

print("=== e-refit: 채점용에 fit_transform", flush=True)
run(SCALEC + [SGD.replace('print(f"MSE: {mean_squared_error(y_test, sgd_pred):.4f}")\n', ''), '''wrong = StandardScaler().fit_transform(X_test)
print(pd.DataFrame(X_test_scaled, columns=features).round(2))
print(pd.DataFrame(wrong, columns=features).round(2))''', '''wrong_pred = sgd.predict(wrong)
print("정답:", list(y_test))
print("transform:", sgd_pred.round(1))
print("fit_transform:", wrong_pred.round(1))
print(f"R2: {r2_score(y_test, wrong_pred):.4f}")'''])

print("=== e-noscale: 스케일링 안 한 표를 predict", flush=True)
run(SCALEC + [SGD.replace('print(f"MSE: {mean_squared_error(y_test, sgd_pred):.4f}")\n', ''), '''bad = sgd.predict(X_test)
print("예측:", bad.round(1))'''])

print("=== e-read: 스케일링한 기울기 읽기", flush=True)
run(SCALEC + [SGD, '''print("공부 시간 표준편차:", scaler.scale_[0].round(2), "시간")
print("기울기 w1:", sgd.coef_[0].round(2))''', '''a = pd.DataFrame({"study_hours": [3, 4], "sleep_hours": [7, 7], "practice_count": [20, 20]})
pa = sgd.predict(scaler.transform(a))
print("3시간, 4시간:", pa.round(2), "차이:", (pa[1] - pa[0]).round(2))'''])

print("=== x-new: 새 학생 예측", flush=True)
run(SCALEC + [SGD, LRTEST, '''new = pd.DataFrame({
    "study_hours": [4],
    "sleep_hours": [7],
    "practice_count": [30],
})
new_scaled = scaler.transform(new)
print(new_scaled.round(2))
print("SGD:", sgd.predict(new_scaled).round(2))
print("LinearRegression:", test_model.predict(new).round(2))''', '''sgd.predict(new)'''])

print("=== x-seed: random_state마다 채점 점수", flush=True)
run(BASE + ['from sklearn.model_selection import train_test_split', '''for seed in [0, 1, 2, 3, 42]:
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=seed)
    m = LinearRegression()
    m.fit(X_train, y_train)
    r2 = r2_score(y_test, m.predict(X_test))
    print(f"random_state={seed:2} 채점용 {list(X_test.index)} R2 {r2:.2f}")'''])

print("=== x-office: 오피스텔 200건 나눠 채점, 스케일링한 SGD", flush=True)
run(BASE + ['from sklearn.model_selection import train_test_split\nfrom sklearn.preprocessing import StandardScaler', '''office = pd.read_csv("datasets/office.csv")
Xo = office[["area"]]
yo = office["price"]

Xo_train, Xo_test, yo_train, yo_test = train_test_split(Xo, yo, test_size=0.2, random_state=42)
print(Xo_train.shape, Xo_test.shape)''', '''lr = LinearRegression()
lr.fit(Xo_train, yo_train)
print(f"학습용 R2: {r2_score(yo_train, lr.predict(Xo_train)):.3f}")
print(f"채점용 R2: {r2_score(yo_test, lr.predict(Xo_test)):.3f}")
print(f"채점용 MAE: {mean_absolute_error(yo_test, lr.predict(Xo_test)):.0f}")''', '''raw = SGDRegressor(loss="squared_error", learning_rate="constant", eta0=0.01, max_iter=3000, random_state=42)
raw.fit(Xo_train, yo_train)
print("스케일링 없이:", raw.coef_)''', '''sc = StandardScaler()
Xo_train_s = sc.fit_transform(Xo_train)
Xo_test_s = sc.transform(Xo_test)

sg = SGDRegressor(loss="squared_error", learning_rate="constant", eta0=0.01, max_iter=3000, random_state=42)
sg.fit(Xo_train_s, yo_train)
print(f"스케일링하고: 채점용 R2 {r2_score(yo_test, sg.predict(Xo_test_s)):.3f}")
print(f"채점용 MAE: {mean_absolute_error(yo_test, sg.predict(Xo_test_s)):.0f}")'''])
