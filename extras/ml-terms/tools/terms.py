"""Runs every code snippet the ML terms deck shows, like notebook cells, and keeps their real output.

Each CELL below is executed in one shared namespace (the way a notebook keeps variables between cells) and its printed
output (or the value of its last line) is stored. tools/gen.py reads tools/data.json, so every number on the slides
comes from this run. The drawings (U-shaped loss curve, gradient descent steps, histograms, learning curves) use the
numbers in the DRAW part at the bottom, which are computed the same way but not shown as code.
Usage (from the ml-basics project that demo.sh makes): .venv/bin/python terms.py OUT_JSON
"""
import ast
import contextlib
import io
import json
import sys
import warnings

warnings.filterwarnings("ignore")
NS = {}
CELLS = {}


def cell(name, src):
    """Run src like a notebook cell: prints are kept, and a bare last expression is shown with repr()."""
    src = src.strip("\n")
    tree = ast.parse(src)
    last = tree.body[-1] if tree.body and isinstance(tree.body[-1], ast.Expr) else None
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        if last is not None:
            exec(compile(ast.Module(tree.body[:-1], []), name, "exec"), NS)
            v = eval(compile(ast.Expression(last.value), name, "eval"), NS)
            if v is not None:
                print(repr(v))
        else:
            exec(compile(tree, name, "exec"), NS)
    out = buf.getvalue().rstrip("\n")
    CELLS[name] = {"code": src.split("\n"), "out": out.split("\n") if out else []}
    print(f"### {name}")
    print(src)
    print("--- output")
    print(out)
    print()


# ---------- setup, same as chapters 45 to 49 ----------
cell("import", """
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.linear_model import LinearRegression, SGDRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
""")

# ---------- 46: mean, median, quartiles ----------
cell("mean", """
titanic = sns.load_dataset("titanic")
print("평균:", round(titanic["fare"].mean(), 2))
print("중앙값:", titanic["fare"].median())
print("가장 큰 값:", titanic["fare"].max())
""")
cell("iqr", """
q1 = titanic["fare"].quantile(0.25)
q3 = titanic["fare"].quantile(0.75)
iqr = q3 - q1
upper = q3 + 1.5 * iqr
print("Q1:", q1, " Q3:", q3)
print("IQR:", round(iqr, 2), " 울타리:", round(upper, 2))
print("울타리 밖:", (titanic["fare"] > upper).sum(), "명")
""")

# ---------- the five students (03_ml) ----------
cell("five", """
df = pd.DataFrame({
    "hours": [1, 2, 3, 4, 5],
    "scores": [47, 53, 65, 73, 87]
})
df
""")
cell("corr", """
print(round(df["hours"].corr(df["scores"]), 2))
""")
cell("corr3", """
house = pd.read_csv("datasets/usa_housing.csv")
print("공부 시간과 점수:", round(df["hours"].corr(df["scores"]), 2))
print("집 면적과 가격:", round(house["SquareFeet"].corr(house["Price"]), 2))
print("객실 등급과 요금:", round(titanic["pclass"].corr(titanic["fare"]), 2))
""")

# ---------- 47: random numbers ----------
cell("seed", """
rng = np.random.default_rng(42)
print(rng.normal(0, 2500, 5).round())
rng = np.random.default_rng(42)
print(rng.normal(0, 2500, 5).round())
""")

# ---------- 48: X, y, fit, predict ----------
cell("xy", """
X = df[["hours"]]
y = df["scores"]
print(X.shape, y.shape)
""")
cell("fit", """
model = LinearRegression()
model.fit(X, y)
print("기울기 w:", round(model.coef_[0], 2))
print("절편 b:", round(model.intercept_, 2))
""")
cell("predict", """
new = pd.DataFrame({"hours": [6]})
print(model.predict(new))
""")
cell("ypred", """
y_pred = model.predict(X)
print("예측:", y_pred)
print("오차:", (y - y_pred).round(2).tolist())
""")
cell("metrics", """
print("MAE:", round(mean_absolute_error(y, y_pred), 2))
print("MSE:", round(mean_squared_error(y, y_pred), 2))
print("RMSE:", round(mean_squared_error(y, y_pred) ** 0.5, 2))
print("R²:", round(r2_score(y, y_pred), 2))
""")
cell("r2base", """
mean_line = [y.mean()] * 5
print("평균만 찍기 MSE:", round(mean_squared_error(y, mean_line), 2))
print("평균만 찍기 R²:", r2_score(y, mean_line))
""")
cell("r2neg", """
bad = 20 * df["hours"]
print("20 × 공부 시간 R²:", round(r2_score(y, bad), 2))
""")
cell("r2corr", """
r = df["hours"].corr(df["scores"])
print("상관계수:", round(r, 4))
print("상관계수 제곱:", round(r ** 2, 4))
print("R²:", round(r2_score(y, y_pred), 4))
""")
cell("double", """
m2 = LinearRegression()
m2.fit(X, y * 2)
print("기울기 w:", round(m2.coef_[0], 2))
print("상관계수:", round(df["hours"].corr(y * 2), 2))
""")

# ---------- 49: loss as a function of w (b fixed at 35) ----------
cell("ucurve", """
for w in [8, 9, 10, 11, 12]:
    pred = w * df["hours"] + 35
    print(w, round(mean_squared_error(y, pred), 2))
""")
cell("slope", """
hours = df["hours"]
before = mean_squared_error(y, 8 * hours + 35)
after = mean_squared_error(y, 8.001 * hours + 35)
change = after - before
print("MSE 변화:", round(change, 4))
print("변화 ÷ 0.001:", round(change / 0.001, 1))
""")
cell("sgd", """
sgd = SGDRegressor(
    loss="squared_error",
    learning_rate="constant",
    eta0=0.01,
    max_iter=1000,
    shuffle=False,
    random_state=42
)
""")
cell("loop", """
history = []
for epoch in range(1000):
    sgd.partial_fit(X, y)
    y_pred = sgd.predict(X)
    history.append({
        "epoch": epoch + 1,
        "weight": sgd.coef_[0],
        "bias": sgd.intercept_[0],
        "mse": mean_squared_error(y, y_pred)
    })
history_df = pd.DataFrame(history)
history_df[history_df["epoch"].isin([1, 5, 10, 100, 500, 1000])]
""")
cell("sgdres", """
print("기울기 w:", round(sgd.coef_[0], 2))
print("절편 b:", round(sgd.intercept_[0], 2))
print("6시간:", round(sgd.predict(pd.DataFrame({"hours": [6]}))[0], 2), "점")
""")
cell("eta", """
for eta in [0.001, 0.01, 0.3]:
    s = SGDRegressor(learning_rate="constant", eta0=eta,
                     shuffle=False, random_state=42)
    for epoch in range(1000):
        s.partial_fit(X, y)
    print(eta, mean_squared_error(y, s.predict(X)))
""")

# ---------- 50: three columns ----------
cell("multi", """
study = pd.DataFrame({
    "study_hours":    [1, 2, 3, 4, 5, 2, 3, 5, 4, 1],
    "sleep_hours":    [6, 8, 5, 7, 8, 5, 8, 6, 6, 8],
    "practice_count": [10, 15, 20, 25, 30, 12, 28, 22, 32, 8],
    "score":          [47, 58, 60, 76, 87, 49, 73, 77, 79, 52]
})
X3 = study[["study_hours", "sleep_hours", "practice_count"]]
m3 = LinearRegression()
m3.fit(X3, study["score"])
print("coef_:", m3.coef_.round(2))
print("intercept_:", round(m3.intercept_, 2))
""")
cell("multipred", """
a = pd.DataFrame({"study_hours": [3, 4], "sleep_hours": [7, 7], "practice_count": [20, 20]})
print(m3.predict(a).round(2))
""")
cell("heat", """
study.corr().round(2)
""")

# ---------- DRAW: numbers for the drawings, not shown as code ----------
D = NS
draw = {}
fare = D["titanic"]["fare"]
counts, edges = __import__("numpy").histogram(fare, bins=list(range(0, 105, 5)) + [600])
draw["fare_hist"] = {"counts": counts.tolist(), "edges": edges.tolist(), "mean": float(fare.mean()), "median": float(fare.median()),
                     "q1": float(D["q1"]), "q3": float(D["q3"]), "upper": float(D["upper"]), "over": int((fare > D["upper"]).sum()), "n": int(len(fare))}
np_ = D["np"]
r = np_.random.default_rng(42).normal(0, 2500, 10000)
c, ed = np_.histogram(r, bins=40, range=(-10000, 10000))
draw["normal"] = {"counts": c.tolist(), "edges": ed.tolist(), "in1": float(((r > -2500) & (r < 2500)).mean())}
# loss curve with b = 35 and its slope (central difference, the same as the slope cell)
y, h = D["y"], D["df"]["hours"]
mse = lambda w, b=35: float(D["mean_squared_error"](y, w * h + b))
grad = lambda w: (mse(w + 1e-4) - mse(w - 1e-4)) / 2e-4
draw["u"] = [[round(w, 2), mse(w)] for w in np_.arange(6.5, 13.51, 0.05)]
draw["grad"] = {str(w): round(grad(w), 2) for w in [8, 9, 10, 11, 12]}
paths = {}
for eta in [0.004, 0.02, 0.1]:
    w, ps = 8.0, []
    for _ in range(8):
        ps.append([round(w, 3), round(mse(w), 3), round(grad(w), 3)])
        w = w - eta * grad(w)
    paths[str(eta)] = ps
draw["gd"] = paths
hd = D["history_df"]
draw["history"] = {"epoch": hd["epoch"].tolist(), "mse": hd["mse"].round(4).tolist(), "w": hd["weight"].round(4).tolist(), "b": hd["bias"].round(4).tolist()}
eh = {}
for eta in [0.001, 0.01, 0.3]:
    s = D["SGDRegressor"](learning_rate="constant", eta0=eta, shuffle=False, random_state=42)
    ms = []
    for _ in range(1000):
        s.partial_fit(D["X"], y)
        ms.append(float(D["mean_squared_error"](y, s.predict(D["X"]))))
    eh[str(eta)] = ms
draw["eta_hist"] = eh
# each student's own loss slope at w = 8 (b = 35): SGD steps by one of them, batch by their average
pred8 = 8 * h + 35
draw["per_student"] = [round(float(-2 * xi * (yi - pi)), 2) for xi, yi, pi in zip(h, y, pred8)]
draw["corr_house"] = D["house"][["SquareFeet", "Price"]].sample(60, random_state=1).values.tolist()
draw["corr_titanic"] = D["titanic"][["pclass", "fare"]].dropna().sample(80, random_state=1).values.tolist()
draw["heat"] = D["study"].corr().round(2).values.tolist()
draw["heat_cols"] = D["study"].columns.tolist()
draw["study"] = D["study"].values.tolist()
draw["coef3"] = D["m3"].coef_.tolist() + [float(D["m3"].intercept_)]

with open(sys.argv[1], "w") as f:
    json.dump({"cells": CELLS, "draw": draw}, f, ensure_ascii=False)
print("saved", sys.argv[1])
