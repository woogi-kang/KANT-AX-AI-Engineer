"""Runs the notebook cells shown in the deck with the project's own kernel and prints each output.
Used by tools/demo.sh (chapter 48, the second half of the class notebook 02_ml.ipynb). Each run() is one fresh kernel, like opening the notebook and pressing Run All.
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




IMPORTS = '''import numpy as np
import pandas as pd
import matplotlib.pyplot as plt'''
FONTCELL = '''import platform

os_name = platform.system()
if os_name == "Windows":
    plt.rcParams["font.family"] = "Malgun Gothic"
elif os_name == "Darwin":
    plt.rcParams["font.family"] = "AppleGothic"'''
READ = '''office = pd.read_csv("datasets/office.csv")
print(office.shape)
office.head()'''
FIT = '''from sklearn.linear_model import LinearRegression

model = LinearRegression()

X = office[["area"]]
y = office["price"]
model.fit(X, y)

print("기울기 w:", model.coef_[0], "정답: 450")
print("절편 b:", model.intercept_, "정답: 5000")'''
PRED = '''new = pd.DataFrame({"area": [33, 59]})
model.predict(new).round(-1)'''
DRAW = '''y_pred = model.predict(X)

line = X.sort_values("area")
line_pred = model.predict(line)

plt.figure(figsize=(8, 5))
plt.scatter(office["area"], office["price"], alpha=0.6, label="실제 시세")
plt.plot(line["area"], line_pred, color="red", label="모델의 직선")
plt.title("오피스텔 시세 200건")
plt.xlabel("면적")
plt.ylabel("가격")
plt.legend()
plt.show()'''
METRIC = '''from sklearn.metrics import mean_absolute_error, mean_squared_error, root_mean_squared_error, r2_score

print(f"MAE = {mean_absolute_error(y, y_pred):,.0f}")
print(f"MSE = {mean_squared_error(y, y_pred):,.0f}")
print(f"RMSE = {root_mean_squared_error(y, y_pred):,.0f}")
print(f"R2 = {r2_score(y, y_pred)}")'''
NORMAL = '''special = [17, 134, 178, 172, 122]

normal = np.ones(len(office), dtype=bool)
normal[special] = False
print("특이 매물:", special)
print("정상 매물:", normal.sum())'''
CASES = '''all_rows = np.ones(len(office), dtype=bool)
cases = [("전체 200건", all_rows), ("특이 매물 뺀 195건", normal)]

for name, mask in cases:
    y_true = y[mask]
    y_hat = y_pred[mask]
    mae = mean_absolute_error(y_true, y_hat)
    rmse = root_mean_squared_error(y_true, y_hat)
    r2 = r2_score(y_true, y_hat)
    print(f"{name} MAE {mae:,.0f} | RMSE {rmse:,.0f} | R2 {r2:.2f}")'''
CASES_BUG = CASES.replace('("특이 매물 뺀 195건", normal)', '("특이 매물 뺀 195건", special)')
CORE = [IMPORTS, FONTCELL, 'office = pd.read_csv("datasets/office.csv")', FIT.split("\n\nprint")[0]]   # what later notebooks need first
print("=== main: model.ipynb, 수업 순서 그대로", flush=True)
run([IMPORTS, FONTCELL, READ, FIT, PRED, DRAW, METRIC, NORMAL, CASES,
     # extra looks used on slides, same kernel
     'model',
     'print(X.shape, y.shape)',
     'X.head(3)',
     'y.head(3)',
     'print(type(X))\nprint(type(y))',
     'model.coef_',
     'model.intercept_',
     'print(33 * model.coef_[0] + model.intercept_)\nprint(59 * model.coef_[0] + model.intercept_)',
     'model.predict(new)',
     'new',
     'print(len(y_pred))\nprint(y_pred[:3])',
     'line.head(3)',
     '''errors = y - y_pred
table = pd.DataFrame({"정답": y, "예측": y_pred, "오차": errors}).round(0)
table.head()''',
     'print("오차 합:", errors.sum().round(6))',
     'print("오차 절댓값 평균:", errors.abs().mean())',
     '''print("오차 제곱 평균:", (errors ** 2).mean())
print("그 제곱근:", ((errors ** 2).mean()) ** 0.5)''',
     '''base = np.full(len(y), y.mean())
print("평균만 찍은 R2:", r2_score(y, base))
print("1 - 모델 오차 / 평균 오차:", 1 - (errors ** 2).sum() / ((y - y.mean()) ** 2).sum())''',
     'print("상관계수:", office["area"].corr(office["price"]))\nprint("상관계수 제곱:", office["area"].corr(office["price"]) ** 2)',
     'print(normal[14:20])',
     'office.loc[special]',
     'big = table[table["오차"] > 10000]\nbig',
     'table["오차"].abs().sort_values(ascending=False).head(7)',
     '''plt.figure(figsize=(8, 5))
plt.scatter(office["area"], office["price"], alpha=0.6, label="정상 매물")
plt.scatter(office.loc[special, "area"], office.loc[special, "price"], color="orange", s=80, label="특이 매물 5건")
plt.plot(line["area"], line_pred, color="red", label="모델의 직선")
plt.xlabel("면적")
plt.ylabel("가격")
plt.legend()
plt.show()''',
     # the class's first drawing, without sorting (cell 7 of 02_ml.ipynb)
     '''plt.figure(figsize=(8, 5))
plt.scatter(office["area"], office["price"], alpha=0.6)
plt.plot(office["area"], y_pred, color="red")
plt.show()''',
     ], "main")

print("=== notfit: fit 전에 predict", flush=True)
run([IMPORTS, 'office = pd.read_csv("datasets/office.csv")', '''from sklearn.linear_model import LinearRegression

model = LinearRegression()
new = pd.DataFrame({"area": [33, 59]})
model.predict(new)'''])

print("=== e-1d: X를 1차원으로", flush=True)
run(CORE + ['model.fit(office["area"], office["price"])', 'model.fit(y, X)'])

print("=== e-pred: predict에 숫자만, 리스트로", flush=True)
run(CORE + ['model.predict(33)', 'model.predict([[33], [59]])', 'model.predict(pd.DataFrame({"size": [33, 59]}))'])

print("=== e-mask: special을 넣은 원래 셀", flush=True)
run(CORE + ['y_pred = model.predict(X)', METRIC.split("\n")[0], NORMAL, CASES_BUG, 'print(y[special].shape, y[normal].shape)'])

print("=== e-order: 인자 순서를 바꾸면", flush=True)
run(CORE + ['y_pred = model.predict(X)', METRIC.split("\n")[0],
            '''print("MAE", mean_absolute_error(y, y_pred), mean_absolute_error(y_pred, y))
print("R2 ", r2_score(y, y_pred), r2_score(y_pred, y))'''])

print("=== x-normal: 특이 매물 빼고 다시 학습", flush=True)
run(CORE + [NORMAL.replace('\nprint("특이 매물:", special)\nprint("정상 매물:", normal.sum())', ''),
            '''clean = office[normal]
model2 = LinearRegression()
model2.fit(clean[["area"]], clean["price"])
print("기울기:", model.coef_[0].round(1), "=>", model2.coef_[0].round(1))
print("절편:", model.intercept_.round(0), "=>", model2.intercept_.round(0))''',
            '''new = pd.DataFrame({"area": [33, 59]})
print(model.predict(new).round(-1))
print(model2.predict(new).round(-1))'''])

print("=== x-house: 미국 집값을 면적으로", flush=True)
run([IMPORTS, FONTCELL, '''house = pd.read_csv("datasets/usa_housing.csv")
small = house[(house["YearBuilt"] > 2015) & (house["CrimeRate"] < 45)]
print(house.shape, small.shape)''',
     '''from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

hm = LinearRegression()
hm.fit(house[["SquareFeet"]], house["Price"])
p300 = hm.predict(house[["SquareFeet"]])
print("300채 R2:", round(r2_score(house["Price"], p300), 3))''',
     '''sm = LinearRegression()
sm.fit(small[["SquareFeet"]], small["Price"])
p10 = sm.predict(small[["SquareFeet"]])
print("10채 R2:", round(r2_score(small["Price"], p10), 2))
p_all = sm.predict(house[["SquareFeet"]])
print("10채 직선으로 300채:", round(r2_score(house["Price"], p_all), 2))''',
     '''line = house[["SquareFeet"]].sort_values("SquareFeet")

plt.figure(figsize=(8, 5))
plt.scatter(house["SquareFeet"], house["Price"], alpha=0.4, label="전체 300채")
plt.scatter(small["SquareFeet"], small["Price"], color="red", s=50, label="2015 이후 건축 10채")
plt.plot(line["SquareFeet"], hm.predict(line), color="blue", label="300채로 배운 직선")
plt.plot(line["SquareFeet"], sm.predict(line), color="red", label="10채로 배운 직선")
plt.xlabel("면적")
plt.ylabel("가격")
plt.legend()
plt.show()'''], "xhouse")

print("=== x-quote: 오피스텔 견적표", flush=True)
run(CORE + ['''quote = pd.DataFrame({"area": [25, 40, 60, 80]})
quote["예상 가격"] = model.predict(quote).round(-1)
quote''',
            '''from sklearn.metrics import mean_absolute_error
mae = mean_absolute_error(y, model.predict(X))
quote["아래"] = (quote["예상 가격"] - mae).round(-1)
quote["위"] = (quote["예상 가격"] + mae).round(-1)
quote'''])
