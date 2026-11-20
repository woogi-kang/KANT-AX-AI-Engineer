"""Runs the notebook cells shown in the deck with the project's own kernel and prints each output.
Used by tools/demo.sh. Each run() is one fresh kernel, like opening the notebook and pressing Run All.
Error lines keep only the last line of the traceback. DataFrames print as text; the deck draws them as VS Code's table."""
import sys

import nbclient
import nbformat


def run(cells, timeout=None):
    nb = nbformat.v4.new_notebook()
    nb.cells = [nbformat.v4.new_code_cell(c) for c in cells]
    kw = dict(timeout=timeout, interrupt_on_timeout=True) if timeout else {}
    nbclient.NotebookClient(nb, kernel_name="python3", allow_errors=True, **kw).execute()
    for c in nb.cells:
        print(f"--- [{c.execution_count}] {c.source!r}")
        for o in c.outputs:
            if o.output_type == "error":
                print(f"{o.ename}: {o.evalue}")
            else:
                print(o.get("text") or o.get("data", {}).get("text/plain"))


DATA = '''shops = ["편의점", "버스", "영화관", "분식집", "온라인쇼핑", "카페",
         "음원앱", "버스", "편의점", "웹툰", "온라인쇼핑", "분식집"]
categories = ["식비", "교통", "문화", "식비", "쇼핑", "식비",
              "문화", "교통", "식비", "문화", "쇼핑", "식비"]
amounts = [3200, 1500, 15000, 6500, 32000, 4800,
           10900, 1500, 2700, 3000, 18500, 7000]'''
FRAME = '''import pandas as pd

spend = pd.DataFrame({
    "day": [2, 3, 4, 5, 7, 9, 12, 14, 16, 19, 20, 25],
    "shop": shops,
    "category": categories,
    "amount": amounts
})
spend'''

if sys.argv[1:] == ["nopandas"]:
    print("=== e. 패키지를 안 넣은 프로젝트")
    run(["import pandas as pd"])
    sys.exit()

print("=== 1. 미리보기 (4파트의 groupby를 고치기 전 데이터로)")
run([DATA, FRAME, '''spend.groupby("category")["amount"].sum()'''])

print("=== 1~5. 이어서 한 노트북")
run([DATA,
     # 1. why
     '''food = 0
for i in range(len(amounts)):
    if categories[i] == "식비":
        food = food + amounts[i]
print(food)''',
     '''food = 0
for c, a in zip(categories, amounts):
    if c == "식비":
        food = food + a
print(food)''',
     '''import numpy as np

print(np.array([3200, 1500, 15000]) * 2)''',
     # 2. numpy
     '''prices = [3200, 1500, 15000]
print(prices * 2)
print(np.array(prices) * 2)''',
     '''print(prices + 500)''',
     '''print(np.array(prices) + 500)''',
     '''arr = np.array(amounts)
print(arr)''',
     '''print("합계:", arr.sum())
print("평균:", round(arr.mean()))
print("최소:", arr.min())
print("최대:", arr.max())''',
     '''print(sum(amounts) / len(amounts))
print(amounts.mean())''',
     '''print("모양:", arr.shape)
print("타입:", arr.dtype)''',
     '''print(arr >= 10000)''',
     '''print(arr[arr >= 10000])''',
     # 3. pandas
     FRAME,
     '''spend.shape''',
     '''spend.head(3)''',
     '''spend["amount"]''',
     '''print("합계:", spend["amount"].sum())
print("평균:", round(spend["amount"].mean(), 2))''',
     '''spend[["shop", "amount"]]''',
     '''spend["category"] == "문화"''',
     '''spend[spend["category"] == "문화"]''',
     '''spend[spend["amount"] >= 10000]''',
     '''spend[(spend["category"] == "식비") & (spend["amount"] >= 5000)]''',
     '''spend.sort_values(by="amount", ascending=False).head(3)''',
     # 4. new column, loc, groupby
     '''spend["amount"] / 100''',
     '''spend["amount"] // 100''',
     '''spend["point"] = spend["amount"] // 100
print(spend["point"].sum())
spend.head(3)''',
     '''spend.loc[2, "amount"] = 14000
spend.head(3)''',
     '''spend["point"] = spend["amount"] // 100
spend.head(3)''',
     '''spend.groupby("category")["amount"].sum()''',
     '''spend.groupby("category")["amount"].sum().sort_values(ascending=False)''',
     '''spend["category"].value_counts()''',
     # 5. errors
     '''spend[spend["category"] == "식비" and spend["amount"] >= 5000]''',
     '''spend[spend["category"] == "식비" & spend["amount"] >= 5000]''',
     '''spend["amout"]''',
     '''spend["shop", "amount"]''',
     ])

print("=== 6. 실습 (새 커널)")
run([DATA, FRAME,
     '''top = spend.sort_values(by="amount", ascending=False).head(3)
top[["shop", "amount"]]''',
     '''food = spend[spend["category"] == "식비"]["amount"].sum()
print(f"식비 {food}원, 예산 20000원보다 {food - 20000}원 더 썼어요")''',
     '''big = spend[spend["amount"] >= 10000]
total = big["amount"].sum()
print(f"1만 원 넘는 지출 {len(big)}번, 합계 {total}원")
big["category"].value_counts()''',
     ])
