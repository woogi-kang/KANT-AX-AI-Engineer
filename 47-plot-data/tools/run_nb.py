"""Runs the notebook cells shown in the deck with the project's own kernel and prints each output.
Used by tools/demo.sh. Each run() is one fresh kernel, like opening the notebook and pressing Run All.
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
LINE = '''fig, ax = plt.subplots(figsize=(6, 5))

months = ["1월", "2월", "3월", "4월", "5월", "6월"]
sales = [120, 135, 120, 160, 170, 190]

ax.plot(months, sales, marker="o", label="매출")
ax.set_title("My Mall 월 매출")
ax.set_xlabel("월")
ax.set_ylabel("매출(만원)")
ax.legend()
plt.show()'''
HOUSE = '''house = pd.read_csv("datasets/usa_housing.csv")
print(house.shape)
house.head()'''
SMALL = '''small = house[(house["YearBuilt"] > 2015) & (house["CrimeRate"] < 45)]
small.shape'''
SCAT = '''plt.figure(figsize=(6, 3))
plt.scatter(house["SquareFeet"], house["Price"], alpha=0.4, label="전체 300채")
plt.scatter(small["SquareFeet"], small["Price"], alpha=0.4, color="red", s=50, label="2015 이후 건축")
plt.xlabel("면적")
plt.ylabel("가격")
plt.legend()
plt.show()

print("전체 300채의 상관계수:", round(house["SquareFeet"].corr(house["Price"]), 2))
print("2015 이후 건축 상관계수:", round(small["SquareFeet"].corr(small["Price"]), 2))'''
MAKE = '''rng = np.random.default_rng(42)

n = 200
area = rng.uniform(20, 85, n)
price = area * 450 + 5000 + rng.normal(0, 2500, n).round(-1)

special = rng.choice(n, 5, replace=False)
price[special] += rng.uniform(15000, 25000, 5).round(-1)

office = pd.DataFrame({"area": area, "price": price})
office.describe().round(1)'''
SAVE = '''office.to_csv("datasets/office.csv", index=False)'''
OSCAT = '''plt.figure(figsize=(8, 5))
plt.scatter(office["area"], office["price"], alpha=0.6)
plt.title("오피스텔 시세 200건")
plt.xlabel("면적")
plt.ylabel("가격")
plt.show()

print("상관계수:", office["area"].corr(office["price"]))'''
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
NORMAL = '''normal = np.ones(len(office), dtype=bool)
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
CORE = [IMPORTS, FONTCELL, 'house = pd.read_csv("datasets/usa_housing.csv")', SMALL.replace("\nsmall.shape", ""),
        MAKE.replace("\noffice.describe().round(1)", ""), FIT.split("\n\nprint")[0]]   # what later notebooks need before their own cells

print("=== main: 수업 순서 그대로 한 노트북")
run([IMPORTS, FONTCELL, LINE, HOUSE, SMALL, SCAT, MAKE, SAVE, OSCAT, FIT, PRED, DRAW, METRIC, NORMAL, CASES,
     # extra looks used on slides, same kernel
     'office.head()',
     'print(X.shape, y.shape)',
     'X.head(3)',
     'y.head(3)',
     '''errors = y - y_pred
table = pd.DataFrame({"정답": y, "예측": y_pred, "오차": errors}).round(0)
table.head()''',
     '''print("MAE 직접:", errors.abs().mean())
print("MSE 직접:", (errors ** 2).mean())
print("RMSE 직접:", ((errors ** 2).mean()) ** 0.5)''',
     '''base = np.full(len(y), y.mean())
print("평균만 찍은 R2:", r2_score(y, base))
print("1 - 모델 오차 / 평균 오차:", 1 - (errors ** 2).sum() / ((y - y.mean()) ** 2).sum())''',
     'office.loc[special]',
     '''base_ = office["area"] * 450 + 5000
print((office["area"].head(3)).round(1).tolist())
print((base_.head(3)).round(0).tolist())
print((office["price"] - base_).head(3).round(0).tolist())
print(office["price"].head(3).round(0).tolist())''',
     'print(model.predict(pd.DataFrame({"area": [0]})))',
     ], "main")

print("=== min: 가장 짧은 그래프")
run([IMPORTS, FONTCELL, '''months = ["1월", "2월", "3월", "4월", "5월", "6월"]
sales = [120, 135, 120, 160, 170, 190]

plt.plot(months, sales)
plt.show()'''], "min")

print("=== two: 두 줄을 한 그래프에")
run([IMPORTS, FONTCELL, '''fig, ax = plt.subplots(figsize=(6, 5))

months = ["1월", "2월", "3월", "4월", "5월", "6월"]
sales = [120, 135, 120, 160, 170, 190]
goal = [130, 130, 140, 150, 160, 170]

ax.plot(months, sales, marker="o", label="매출")
ax.plot(months, goal, marker="s", label="목표")
ax.set_title("My Mall 월 매출과 목표")
ax.set_xlabel("월")
ax.set_ylabel("매출(만원)")
ax.legend()
plt.show()'''], "two")

print("=== nolegend: label만 적고 legend를 빼면")
run([IMPORTS, FONTCELL, LINE.replace("ax.legend()\n", "")], "nolegend")

print("=== e-len: x와 y 개수가 다르면")
run([IMPORTS, '''months = ["1월", "2월", "3월", "4월", "5월", "6월"]
sales = [120, 135, 120, 160, 170]

plt.plot(months, sales)'''])

print("=== e-file: 경로를 틀리면")
run([IMPORTS, 'house = pd.read_csv("usa_housing.csv")'])

print("=== csv: index=False가 없으면")
run(CORE + [SAVE, '''with open("datasets/office.csv") as f:
    print(f.read()[:120])''',
            '''office.to_csv("datasets/office_index.csv")
with open("datasets/office_index.csv") as f:
    print(f.read()[:120])''',
            'pd.read_csv("datasets/office_index.csv").head(3)',
            'pd.read_csv("datasets/office.csv").head(3)'])

print("=== rng: 시드와 난수")
run(["import numpy as np",
     '''a = np.random.default_rng(42)
b = np.random.default_rng(42)
print(a.uniform(20, 85, 3))
print(b.uniform(20, 85, 3))''',
     '''c = np.random.default_rng()
print(c.uniform(20, 85, 3))''',
     '''c = np.random.default_rng()
print(c.uniform(20, 85, 3))''',
     '''rng = np.random.default_rng(42)
print(rng.uniform(20, 85, 3))
print(rng.uniform(20, 85, 3))''',
     '''rng = np.random.default_rng(7)
print(rng.normal(0, 2500, 5).round(0))''',
     '''print(np.round(1234.5678, -1), np.round(1234.5678, 0), np.round(1234.5678, 1))''',
     '''rng = np.random.default_rng(1)
print(rng.choice(10, 5, replace=False))
print(rng.choice(10, 5, replace=True))''',
     '''rng = np.random.default_rng(42)
area = rng.uniform(20, 85, 200)
print(area[:3])''',
     '''rng = np.random.default_rng(42)
area = rng.uniform(20, 85, 200)
noise = rng.normal(0, 2500, 200)
print("면적 최소, 최대:", area.min().round(1), area.max().round(1))
print("잡음 평균, 표준편차:", noise.mean().round(0), noise.std().round(0))
print("잡음이 ±5000 안:", (abs(noise) <= 5000).mean())''',
     ])

print("=== e-1d: X를 1차원으로")
run(CORE + ['model.fit(office["area"], office["price"])'])

print("=== e-pred: predict에 숫자만")
run(CORE + ['model.predict(33)', 'model.predict([[33], [59]])'])

print("=== e-mask: special을 넣은 원래 셀")
run(CORE + ['y_pred = model.predict(X)', METRIC.split("\n")[0], NORMAL, CASES_BUG])

print("=== e-order: 인자 순서를 바꾸면")
run(CORE + ['y_pred = model.predict(X)', METRIC.split("\n")[0],
            '''print("MAE", mean_absolute_error(y, y_pred), mean_absolute_error(y_pred, y))
print("R2 ", r2_score(y, y_pred), r2_score(y_pred, y))'''])

print("=== e-plot: 정렬 없이 선으로")
run(CORE + ['''plt.figure(figsize=(8, 5))
plt.plot(office["area"], office["price"])
plt.show()'''], "eplot")

print("=== e-font: 글꼴 없이", flush=True)
run([IMPORTS, LINE], "efont", "plain")

print("=== x-normal: 특이 매물 빼고 다시 학습")
run(CORE + [NORMAL,
            '''clean = office[normal]
model2 = LinearRegression()
model2.fit(clean[["area"]], clean["price"])
print("기울기:", model.coef_[0].round(1), "=>", model2.coef_[0].round(1))
print("절편:", model.intercept_.round(0), "=>", model2.intercept_.round(0))''',
            '''p = model2.predict(clean[["area"]])
print("MAE", round(mean_absolute_error(clean["price"], p)), "RMSE", round(root_mean_squared_error(clean["price"], p)), "R2", round(r2_score(clean["price"], p), 2))'''.replace("print(", "from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score\nprint(", 1),
            ])

print("=== x-house: 미국 집값을 면적으로")
run(CORE + ['''from sklearn.metrics import r2_score

hm = LinearRegression()
hm.fit(house[["SquareFeet"]], house["Price"])
print("기울기:", hm.coef_[0].round(1))
print("R2:", round(r2_score(house["Price"], hm.predict(house[["SquareFeet"]])), 3))''',
            '''for col in ["Bedrooms", "Bathrooms", "SquareFeet", "YearBuilt", "CrimeRate", "SchoolRating"]:
    print(col, round(house[col].corr(house["Price"]), 2))''',
            '''sm = LinearRegression()
sm.fit(small[["SquareFeet"]], small["Price"])
print("10채 R2:", round(r2_score(small["Price"], sm.predict(small[["SquareFeet"]])), 2))
print("10채 직선으로 300채:", round(r2_score(house["Price"], sm.predict(house[["SquareFeet"]])), 2))''',
            ], "xhouse")

print("=== x-quote: 오피스텔 견적표")
run(CORE + ['''quote = pd.DataFrame({"area": [25, 40, 60, 80]})
quote["예상 가격"] = model.predict(quote).round(-1)
quote''',
            '''from sklearn.metrics import mean_absolute_error
mae = mean_absolute_error(y, model.predict(X))
quote["아래"] = (quote["예상 가격"] - mae).round(-1)
quote["위"] = (quote["예상 가격"] + mae).round(-1)
quote'''])
