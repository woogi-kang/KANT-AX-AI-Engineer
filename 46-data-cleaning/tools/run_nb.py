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


LOAD = '''import pandas as pd
import seaborn as sns

df = sns.load_dataset("titanic")
df.shape'''
# The class cell, with Linux added only so this script can draw Korean here (students use Windows or Mac).
FONTCELL = '''import platform
import matplotlib.pyplot as plt

os_name = platform.system()
if os_name == "Windows":
    plt.rcParams["font.family"] = "Malgun Gothic"
elif os_name == "Darwin":
    plt.rcParams["font.family"] = "AppleGothic"'''
HIST = '''fig, ax = plt.subplots(figsize=(6, 4))
ax.hist(df["age"], bins=20, color="blue", edgecolor="black")
ax.set_title("나이 분포")
ax.set_xlabel("나이(세)")'''

print("=== main: 수업 순서 그대로 한 노트북")
run([LOAD,
     "df.head()",
     "df.info()",
     "df.describe()",
     "df.isnull().sum()",
     '''empty_age = df["age"].isnull()
print("나이 빈칸:", empty_age.sum(), "명")
df.loc[empty_age, ["sex", "age", "class"]].head()''',
     '''print("평균:", round(df["age"].mean(), 2))
print("중앙값:", round(df["age"].median(), 2))''',
     '''mean_age = df["age"].mean()
df.loc[:, "age"] = df["age"].fillna(mean_age)
df["age"].isnull().sum()''',
     'df["embark_town"].value_counts()',
     'df["embark_town"].value_counts(dropna=False)',
     'df.loc[df["embark_town"].isnull(), ["embarked", "embark_town"]]',
     '''mode_town = df["embark_town"].mode()[0]
print("최빈값:", mode_town)

df.loc[:, "embark_town"] = df["embark_town"].fillna(mode_town)
df["embark_town"].value_counts(dropna=False)''',
     'df["embark_town"].mode()',
     '''df.loc[:, "embarked"] = df["embark_town"].str[0]
df[["embarked", "embark_town"]].isnull().sum()''',
     '''print(df["deck"].dtype)
print(df["deck"].cat.categories.tolist())''',
     '''df["deck"] = df["deck"].cat.add_categories("Unknown").fillna("Unknown")
print(df["deck"].cat.categories.tolist())
df["deck"].value_counts()''',
     'df["fare"].quantile([0.25, 0.5, 0.75])',
     '''q1 = df["fare"].quantile(0.25)
q3 = df["fare"].quantile(0.75)
iqr = q3 - q1
upper = q3 + 1.5 * iqr
lower = q1 - 1.5 * iqr
print("IQR:", iqr)
print("위 기준:", upper)
print("아래 기준:", lower)''',
     '''outliers = df[(df["fare"] < lower) | (df["fare"] > upper)]
print("튀는 요금:", len(outliers), "명")
outliers[["pclass", "age", "fare"]].head()''',
     'df[(df["fare"] < lower) & (df["fare"] > upper)].shape',
     'df["fare"].sort_values(ascending=False).head(5)',
     '''before = len(df)
df = df[df["fare"] < 512].copy()
print(before, "=>", len(df))''',
     '''print("중복 행:", df.duplicated().sum())
df[df.duplicated(keep=False)].sort_values(["fare", "age"]).head()''',
     'df[df.duplicated(keep=False)][["pclass", "sex", "age", "fare", "embark_town"]].value_counts().head(3)',
     'outliers["pclass"].value_counts()',
     FONTCELL,
     HIST,
     ], "main")

print("=== e-dup: 채우는 값에 따라 중복이 달라져요")
run([LOAD,
     'print("채우기 전:", df.duplicated().sum())',
     '''a = df.copy()
a["age"] = a["age"].fillna(a["age"].mean())
print("평균으로:", a.duplicated().sum())''',
     '''b = df.copy()
b["age"] = b["age"].fillna(b["age"].median())
print("중앙값으로:", b.duplicated().sum())''',
     '''new = b.duplicated() & ~df.duplicated()
b[new][["pclass", "sex", "age", "fare"]]''',
     ])

print("=== e-cat")
run([LOAD, 'df["deck"] = df["deck"].fillna("Unknown")'])

print("=== e-assign")
run([LOAD,
     '''df["age"].fillna(29.7)
df["age"].isnull().sum()''',
     '''df["age"].fillna(29.7, inplace=True)
df["age"].isnull().sum()''',
     '''df["age"] = df["age"].fillna(29.7)
df["age"].isnull().sum()''',
     ])

print("=== e-mode")
run([LOAD,
     '''df.loc[:, "embark_town"] = df["embark_town"].fillna(df["embark_town"].mode())
df["embark_town"].value_counts(dropna=False)''',
     'df["embark_town"].mode()',
     ])

print("=== e-copy: pandas 3에서는 .copy() 없이도 경고가 안 나요")
run([LOAD,
     '''small = df[df["fare"] < 512]
small.loc[:, "age"] = 0
print(df["age"].isnull().sum(), small["age"].sum())''',
     ])

print("=== font-broken: 글꼴 설정 없이 (리눅스 기본 글꼴)")
run([LOAD, '''mean_age = df["age"].mean()
df.loc[:, "age"] = df["age"].fillna(mean_age)''', "import matplotlib.pyplot as plt", HIST], "broken", "plain")

print("=== x-hist: 채우기 전과 후")
run([LOAD, FONTCELL, HIST,
     '''(df["age"].round(1) == 29.7).sum()''',
     '''df.loc[:, "age"] = df["age"].fillna(df["age"].mean())
fig, ax = plt.subplots(figsize=(6, 4))
ax.hist(df["age"], bins=20, color="blue", edgecolor="black")
ax.set_title("나이 분포 (평균으로 채운 뒤)")
ax.set_xlabel("나이(세)")''',
     '''(df["age"].round(1) == 29.7).sum()''',
     # Not on a slide: bar heights of the 28.3-32.3 bin before and after, same bins as ax.hist
     '''import numpy as np
raw = sns.load_dataset("titanic")["age"].dropna()
print(np.histogram(raw, bins=20)[0][7], np.histogram(df["age"], bins=20)[0][7])''',
     ], "xhist")

print("=== x-pipe: 한 셀로 다시 정리하기")
run(['''import pandas as pd
import seaborn as sns

df = sns.load_dataset("titanic")

df.loc[:, "age"] = df["age"].fillna(df["age"].mean())
town = df["embark_town"].mode()[0]
df.loc[:, "embark_town"] = df["embark_town"].fillna(town)
df.loc[:, "embarked"] = df["embark_town"].str[0]
df["deck"] = df["deck"].cat.add_categories("Unknown").fillna("Unknown")
df = df[df["fare"] < 512].copy()

print("남은 빈칸:", df.isnull().sum().sum())
print("크기:", df.shape)'''])

print("=== readme: README 실습을 순서대로")
run([LOAD,
     "df.isnull().sum()",
     '''mean_age = df["age"].mean()
df.loc[:, "age"] = df["age"].fillna(mean_age)

mode_town = df["embark_town"].mode()[0]
df.loc[:, "embark_town"] = df["embark_town"].fillna(mode_town)
df.loc[:, "embarked"] = df["embark_town"].str[0]

df["deck"] = df["deck"].cat.add_categories("Unknown").fillna("Unknown")
df.isnull().sum().sum()''',
     '''q1 = df["fare"].quantile(0.25)
q3 = df["fare"].quantile(0.75)
iqr = q3 - q1
upper = q3 + 1.5 * iqr
lower = q1 - 1.5 * iqr

outliers = df[(df["fare"] < lower) | (df["fare"] > upper)]
print("튀는 요금:", len(outliers), "명")
outliers["pclass"].value_counts()''',
     '''before = len(df)
df = df[df["fare"] < 512].copy()
print(before, "=>", len(df))
print("중복 행:", df.duplicated().sum())''',
     FONTCELL,
     HIST,
     ])
