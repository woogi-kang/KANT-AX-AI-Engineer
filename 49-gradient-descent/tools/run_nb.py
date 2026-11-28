"""Runs the notebook cells shown in the deck with the project's own kernel and prints each output.
Used by tools/demo.sh (chapter 49, part 2 of the class notebook 03_ml.ipynb, gradient descent). Each run() is one fresh kernel, like opening the notebook and pressing Run All.
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

from sklearn.linear_model import LinearRegression
from sklearn.linear_model import SGDRegressor
from sklearn.metrics import mean_squared_error'''
FONTCELL = '''import platform

os_name = platform.system()
if os_name == "Windows":
    plt.rcParams["font.family"] = "Malgun Gothic"
elif os_name == "Darwin":
    plt.rcParams["font.family"] = "AppleGothic"

plt.rcParams["axes.unicode_minus"] = False'''
DATA = '''df = pd.DataFrame({
    "hours": [1, 2, 3, 4, 5],
    "scores": [47, 53, 65, 73, 87]
})

X = df[["hours"]]
y = df["scores"]
df'''
LR = '''model = LinearRegression()
model.fit(X, y)
y_pred = model.predict(X)

print(f"Weight: {model.coef_[0]:.2f}")
print(f"Bias: {model.intercept_:.2f}")
print(f"MSE: {mean_squared_error(y, y_pred):.4f}")'''
LR6 = '''new_data = pd.DataFrame({"hours": [6]})
model.predict(new_data)'''
TABLE = '''for w in [8, 9, 10, 11, 12]:
    pred = w * df["hours"] + 35
    mse = mean_squared_error(y, pred)
    print("w =", w, "MSE =", round(mse, 1))'''
UCURVE = '''ws = [w / 2 for w in range(12, 29)]
losses = [mean_squared_error(y, w * df["hours"] + 35) for w in ws]

fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(ws, losses, marker="o")
ax.set_title("b = 35일 때 기울기 w에 따른 MSE")
ax.set_xlabel("기울기 w")
ax.set_ylabel("MSE")
plt.show()'''
ZERO = '''pred = 0 * df["hours"] + 0
print("w = 0, b = 0 일 때 MSE =", round(mean_squared_error(y, pred), 1))'''
LOSSF = '''def loss(w):
    pred = w * df["hours"] + 35
    return mean_squared_error(y, pred)

print(loss(8), loss(10), loss(12))'''
SLOPE = '''for w in [8, 10, 12]:
    slope = (loss(w + 0.001) - loss(w)) / 0.001
    print("w =", w, "| 손실의 기울기 =", round(slope, 1))'''
STEPS = '''w = 8
for step in range(1, 6):
    slope = (loss(w + 0.001) - loss(w)) / 0.001
    w = w - 0.01 * slope
    print("걸음", step, "| 경사 =", round(slope, 1), "| 새 w =", round(w, 2), "| MSE =", round(loss(w), 2))'''
LRSTEPS = '''for lr in [0.002, 0.01, 0.1]:
    w = 8
    path = [w]
    for step in range(5):
        slope = (loss(w + 0.001) - loss(w)) / 0.001
        w = w - lr * slope
        path.append(round(w, 2))
    print("학습률", lr, ":", path)'''
SGD = '''sgd = SGDRegressor(
    loss="squared_error",      # 손실 함수: 오차 제곱 평균(MSE)
    learning_rate="constant",  # 학습률을 처음 값 그대로
    eta0=0.01,                 # 학습률: 한 번에 고치는 보폭
    shuffle=False,             # 데이터 순서를 섞지 않음
    random_state=42            # 난수 시드
)
sgd'''
LOOP = '''epochs = 1000
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
history_df'''
PICK = '''history_df[history_df["epoch"].isin([1, 5, 10, 50, 100, 300, 500, 1000])]'''
CURVE = '''plt.figure(figsize=(10, 5))
plt.plot(history_df["epoch"], history_df["mse"], color="blue", label="학습 손실(Training Loss)")
plt.title("epoch마다 MSE가 줄어요")
plt.xlabel("Epoch")
plt.ylabel("MSE")
plt.grid(alpha=0.3)
plt.legend()
plt.show()'''
WB = '''fig, axes = plt.subplots(1, 2, figsize=(12, 5))

axes[0].plot(history_df["epoch"], history_df["weight"], color="blue")
axes[0].set_title("기울기 w")
axes[0].set_xlabel("Epoch")
axes[0].grid(alpha=0.3)

axes[1].plot(history_df["epoch"], history_df["bias"], color="blue")
axes[1].set_title("절편 b")
axes[1].set_xlabel("Epoch")
axes[1].grid(alpha=0.3)

plt.show()'''
PRED = '''print(f"기울기(w): {sgd.coef_[0]:.2f}")
print(f"절편(b): {sgd.intercept_[0]:.2f}")

new_data = pd.DataFrame({"hours": [6]})
prediction = sgd.predict(new_data)
print(f"예측 성적: {prediction[0]:.2f}점")'''
TRAIN = '''def train(eta, epochs=1000):
    model = SGDRegressor(loss="squared_error", learning_rate="constant",
                         eta0=eta, shuffle=False, random_state=42)
    losses = []
    for epoch in range(epochs):
        model.partial_fit(X, y)
        losses.append(mean_squared_error(y, model.predict(X)))
    return model, losses'''
ETAS = '''for eta in [0.001, 0.01, 0.1, 0.5]:
    m, losses = train(eta)
    print("eta0 =", eta, "| w =", round(m.coef_[0], 2), "| b =", round(m.intercept_[0], 2), "| MSE =", round(losses[-1], 2))'''
ETACHART = '''fig, ax = plt.subplots(figsize=(10, 5))
for eta in [0.001, 0.01, 0.1]:
    m, losses = train(eta)
    ax.plot(range(1, 1001), losses, label="eta0 = " + str(eta))
ax.set_ylim(0, 200)
ax.set_title("학습률마다 MSE가 줄어드는 모습")
ax.set_xlabel("Epoch")
ax.set_ylabel("MSE")
ax.legend()
plt.show()'''
BIG = '''m, losses = train(0.5)
print(losses[:5])'''

print("=== main: gd.ipynb, 수업 순서 그대로", flush=True)
run([IMPORTS, FONTCELL, DATA, LR, LR6, ZERO, TABLE, UCURVE, LOSSF, SLOPE, STEPS, LRSTEPS, SGD, LOOP, PICK, CURVE, WB, PRED,
     'print(type(sgd))',
     'history[:2]',
     'history_df.shape',
     'history_df[history_df["mse"] < 3.3].head(1)',
     'history_df[history_df["mse"] < 3.5].head(1)',
     '[round(v, 2) for v in [history_df["mse"].min(), history_df["mse"].iloc[-1]]]',
     ], "main")

print("=== train: 학습률 비교", flush=True)
run([IMPORTS, FONTCELL, DATA, TRAIN, ETAS, ETACHART, BIG], "eta")

print("=== err-loss", flush=True)
run([IMPORTS, DATA, 'sgd = SGDRegressor(loss="mse")\nsgd.partial_fit(X, y)'], "eloss")

print("=== err-default: learning_rate를 빼면", flush=True)
run([IMPORTS, DATA, '''sgd = SGDRegressor(loss="squared_error", eta0=0.01, shuffle=False, random_state=42)
for epoch in range(1000):
    sgd.partial_fit(X, y)
print(sgd.learning_rate)
print("w =", round(sgd.coef_[0], 2), "| b =", round(sgd.intercept_[0], 2))
print("MSE =", round(mean_squared_error(y, sgd.predict(X)), 2))'''], "edef")

print("=== err-fit: partial_fit 대신 fit", flush=True)
run([IMPORTS, DATA, '''sgd = SGDRegressor(loss="squared_error", learning_rate="constant", eta0=0.01,
                   max_iter=1000, shuffle=False, random_state=42)
for epoch in range(3):
    sgd.fit(X, y)
    print(epoch + 1, "| w =", round(sgd.coef_[0], 2), "| b =", round(sgd.intercept_[0], 2), "| n_iter_ =", sgd.n_iter_)''',
     '''sgd = SGDRegressor(loss="squared_error", learning_rate="constant", eta0=0.01,
                   max_iter=1, shuffle=False, random_state=42)
for epoch in range(3):
    sgd.fit(X, y)
    print(epoch + 1, "| w =", round(sgd.coef_[0], 2), "| b =", round(sgd.intercept_[0], 2))'''], "efit")

print("=== err-twice: 반복 셀을 두 번 실행", flush=True)
run([IMPORTS, FONTCELL, DATA, SGD, LOOP, LOOP, 'history_df.head(3)', CURVE], "etwice")

print("=== x-new: 학생 두 명 더", flush=True)
run([IMPORTS, DATA, SGD, LOOP.replace("history_df", "history_df"), '''df7 = pd.DataFrame({
    "hours": [1, 2, 3, 4, 5, 6, 7],
    "scores": [47, 53, 65, 73, 87, 94, 106]
})
X7 = df7[["hours"]]
y7 = df7["scores"]

for epoch in range(300):
    sgd.partial_fit(X7, y7)

print("SGD   w =", round(sgd.coef_[0], 2), "| b =", round(sgd.intercept_[0], 2))
lr7 = LinearRegression().fit(X7, y7)
print("정답  w =", round(lr7.coef_[0], 2), "| b =", round(lr7.intercept_, 2))''',
     'print(sgd.predict(pd.DataFrame({"hours": [8]})).round(1), lr7.predict(pd.DataFrame({"hours": [8]})).round(1))'], "xnew")

print("=== x-office: 47 오피스텔에 SGD", flush=True)
run([IMPORTS, '''from sklearn.metrics import r2_score

office = pd.read_csv("datasets/office.csv")
Xo = office[["area"]]
yo = office["price"]

for eta in [0.01, 0.0001]:
    sgd_o = SGDRegressor(loss="squared_error", learning_rate="constant",
                         eta0=eta, shuffle=False, random_state=42)
    for epoch in range(1000):
        sgd_o.partial_fit(Xo, yo)
    r2 = r2_score(yo, sgd_o.predict(Xo))
    print("eta0 =", eta, "| w =", round(sgd_o.coef_[0], 2), "| b =", round(sgd_o.intercept_[0], 2), "| R2 =", round(r2, 3))''',
     '''lr_o = LinearRegression().fit(Xo, yo)
print("LinearRegression w =", round(lr_o.coef_[0], 2), "| b =", round(lr_o.intercept_, 2), "| R2 =", round(r2_score(yo, lr_o.predict(Xo)), 3))'''], "xoffice")
