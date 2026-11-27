"""Runs the notebook cells shown in the deck with the project's own kernel and prints each output.
Used by tools/demo.sh (chapter 52, the class notebook 04_ml.ipynb: Olivetti faces, distance, KNeighborsClassifier,
train_test_split with stratify, score). Each run() is one fresh kernel, like opening the notebook and
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


IMPORTS = '''import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import fetch_olivetti_faces'''
FONTCELL = '''import platform

os_name = platform.system()
if os_name == "Windows":
    plt.rcParams["font.family"] = "Malgun Gothic"
elif os_name == "Darwin":
    plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False'''
LOAD = '''faces = fetch_olivetti_faces(data_home="./datasets")'''
SHAPES = '''print("사진 묶음 크기:", faces.images.shape)
print("정답 묶음 크기:", faces.target.shape)
print("사람 번호:", np.unique(faces.target))'''
ROW = '''print("첫 사진 맨 윗줄 앞 5칸:", faces.images[0][0][:5].round(2))
print("가장 어두운 값:", faces.images.min())
print("가장 밝은 값:", faces.images.max())'''
ONE = '''plt.figure(figsize=(3, 3))
plt.imshow(faces.images[0], cmap="gray", vmin=0, vmax=1)
plt.title(f"Person {faces.target[0]}")
plt.axis("off")
plt.show()'''
NOVMIN = '''fig, axes = plt.subplots(1, 2, figsize=(6, 3))
axes[0].imshow(faces.images[0], cmap="gray", vmin=0, vmax=1)
axes[0].set_title("vmin=0, vmax=1")
axes[1].imshow(faces.images[0])
axes[1].set_title("아무것도 안 적으면")
axes[0].axis("off")
axes[1].axis("off")
plt.show()'''
CORNER = '''corner = faces.images[0][20:28, 20:28]

fig, ax = plt.subplots(figsize=(5, 5))
ax.imshow(corner, cmap="gray", vmin=0, vmax=1)

for r in range(8):
    for c in range(8):
        v = corner[r, c]
        ax.text(c, r, f"{v:.1f}", ha="center", va="center", color="red")

plt.show()'''
PERSON = '''def show_person(person):
    pics = faces.images[faces.target == person]
    fig, axes = plt.subplots(1, 10, figsize=(15, 2))
    for i in range(10):
        axes[i].imshow(pics[i], cmap="gray", vmin=0, vmax=1)
        axes[i].axis("off")
    plt.show()

show_person(39)'''
GRID = '''fig, axes = plt.subplots(4, 10, figsize=(15, 8))

for person, ax in enumerate(axes.flat):
    first = faces.images[faces.target == person][0]
    ax.imshow(first, cmap="gray", vmin=0, vmax=1)
    ax.set_title(person, fontsize=10)
    ax.axis("off")

plt.show()'''
TINY = '''new = np.array([0.2, 0.8, 0.5])
a = np.array([0.3, 0.6, 0.5])
b = np.array([0.9, 0.1, 0.4])

print("new - a:", (new - a).round(2))
print("제곱:", ((new - a) ** 2).round(2))
print("더하기:", ((new - a) ** 2).sum().round(2))
print("거리 a:", np.sqrt(((new - a) ** 2).sum()).round(2))
print("거리 b:", np.sqrt(((new - b) ** 2).sum()).round(2))'''
FLAT = '''X = faces.data
y = faces.target

print("X:", X.shape)
print("y:", y.shape)
print("같은 사진인가요?", np.array_equal(X[0].reshape(64, 64), faces.images[0]))'''
REALD = '''print("229번 사람:", y[229], " 228번 사람:", y[228], " 0번 사람:", y[0])
print("229번과 228번 거리:", np.sqrt(((X[229] - X[228]) ** 2).sum()).round(2))
print("229번과 0번 거리:", np.sqrt(((X[229] - X[0]) ** 2).sum()).round(2))'''
KNNIMP = '''from sklearn.neighbors import KNeighborsClassifier'''
KNOWN = '''new_index = 229
new_photo = X[new_index]

known = np.arange(400) != new_index
print(known[227:232])

X_known, y_known = X[known], y[known]
print("X_known:", X_known.shape)'''
MODEL = '''K = 3

model = KNeighborsClassifier(n_neighbors=K)
model.fit(X_known, y_known)'''
NEIGH = '''dist, idx = model.kneighbors([new_photo], n_neighbors=K)
print("idx:", idx)
print("가장 가까운 이웃:", y_known[idx[0]])
print("이웃과의 거리:", dist[0].round(2))'''
PRED = '''pred = model.predict([new_photo])
print("pred:", pred)
print("예측한 사람:", pred[0])
print("실제 정답:", y[new_index])'''
PICS = '''fig, axes = plt.subplots(1, K + 1, figsize=(8, 2.4))
axes[0].imshow(new_photo.reshape(64, 64), cmap="gray", vmin=0, vmax=1)
axes[0].set_title(f"새 사진: {y[new_index]}")
axes[0].axis("off")

for i in range(K):
    j = idx[0][i]
    axes[i + 1].imshow(X_known[j].reshape(64, 64), cmap="gray", vmin=0, vmax=1)
    axes[i + 1].set_title(f"Person {y_known[j]}")
    axes[i + 1].axis("off")

plt.show()'''
PICSBAD = PICS.replace('axes[i + 1].set_title(f"Person {y_known[j]}")', 'axes[i + 1].set_title(f"Person {y[new_index]}")')
KLOOP = '''for k in [1, 3, 5, 7]:
    m = KNeighborsClassifier(n_neighbors=k)
    m.fit(X_known, y_known)
    d, i = m.kneighbors([new_photo], n_neighbors=k)
    print(f"K={k} 이웃 {y_known[i[0]]} 예측 {m.predict([new_photo])[0]}")'''
SPLIT = '''from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    faces.data,
    faces.target,
    test_size=0.25,
    random_state=42,
    stratify=faces.target
)

print("학습용:", X_train.shape, " 채점용:", X_test.shape)
print("사람마다 채점용 장수:", np.bincount(y_test))'''
NOSTRAT = '''Xa, Xb, ya, yb = train_test_split(faces.data, faces.target, test_size=0.25, random_state=42)
print("사람마다 채점용 장수:", np.bincount(yb, minlength=40))'''
SCORE = '''K = 5
model = KNeighborsClassifier(n_neighbors=K)
model.fit(X_train, y_train)

accuracy = model.score(X_test, y_test)
print(f"예측 정확도: {accuracy:.2%}")'''
BYHAND = '''pred = model.predict(X_test)
print("정답:", y_test[:8])
print("예측:", pred[:8])
print("맞았나:", (pred == y_test)[:8])
print("맞힌 장수:", (pred == y_test).sum(), "/", len(y_test))
print("비율:", (pred == y_test).mean())'''
NOSTRATSCORE = '''mb = KNeighborsClassifier(n_neighbors=5)
mb.fit(Xa, ya)
print(f"stratify 없이: {mb.score(Xb, yb):.2%}")'''
E1D = '''model.predict(new_photo)'''
EBIG = '''big = KNeighborsClassifier(n_neighbors=500)
big.fit(X_train, y_train)
big.predict(X_test)'''
ESMALL = '''train_test_split(faces.data, faces.target, test_size=0.05, random_state=42, stratify=faces.target)'''
TRAP = '''print("0번, 1번, 10번 사람:", y[0], y[1], y[10])
print("0번과 1번 거리 (같은 사람):", np.sqrt(((X[0] - X[1]) ** 2).sum()).round(2))
print("0번과 10번 거리 (다른 사람):", np.sqrt(((X[0] - X[10]) ** 2).sum()).round(2))'''
TRAPPIC = '''fig, axes = plt.subplots(1, 3, figsize=(6, 2.4))
for k, n in enumerate([0, 1, 10]):
    axes[k].imshow(faces.images[n], cmap="gray", vmin=0, vmax=1)
    axes[k].set_title(f"{n}번: Person {y[n]}")
    axes[k].axis("off")
plt.show()'''
KTABLE = '''for k in [1, 3, 5, 7, 9]:
    m = KNeighborsClassifier(n_neighbors=k)
    m.fit(X_train, y_train)
    print(f"K={k}: {m.score(X_test, y_test):.2%}")'''
WRONG = '''wrong = pred != y_test
print("틀린 장수:", wrong.sum())
print("정답:", y_test[wrong])
print("예측:", pred[wrong])'''
CONFUSE = '''show_person(0)
show_person(15)'''

BASE = [IMPORTS, FONTCELL, LOAD]
print("=== load: first time downloads, second time reads the folder", flush=True)
run([IMPORTS, LOAD, LOAD, SHAPES, ROW], kind="plain")

print("=== pictures", flush=True)
run(BASE + [ONE, NOVMIN, CORNER, PERSON, GRID], "pic")

print("=== distance", flush=True)
run(BASE + [TINY, FLAT, REALD, TRAP, TRAPPIC], "dist")

print("=== knn one photo", flush=True)
run(BASE + [FLAT, KNNIMP, KNOWN, MODEL, NEIGH, PRED, PICS, PICSBAD, KLOOP, E1D], "one")

print("=== split and score", flush=True)
run(BASE + [FLAT, KNNIMP, SPLIT, NOSTRAT, SCORE, BYHAND, NOSTRATSCORE, EBIG, ESMALL, KTABLE, WRONG, PERSON, CONFUSE], "score")
