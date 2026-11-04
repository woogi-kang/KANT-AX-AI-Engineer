"""Runs the notebook cells shown in the deck with the project's own kernel and prints each output.
Used by tools/demo.sh. Each run() is one fresh kernel, like opening the notebook and pressing Run All.
Error lines keep only the last line of the traceback."""
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
                t = o.get("text") or o.get("data", {}).get("text/plain")
                lines = t.splitlines()
                if len(lines) > 12:
                    t = "\n".join(lines[:5]) + f"\n... ({len(lines)} lines)"
                print(t)



print("=== 1. 왜 필요한가")
run(['''prices = [4500, 5000, 6500]
up = []
for p in prices:
    up.append(p + 500)
print(up)
print(list(map(lambda p: p + 500, prices)))''',
     '''numbers = [1, 2, 3]
print([x + 10 for x in numbers])'''])

print("=== 2. 만들기와 고르기")
run(['''prices = [4500, 5000, 6500, 3000]
up = []
for p in prices:
    up.append(p + 500)
print(up)
print(list(map(lambda p: p + 500, prices)))
print([p + 500 for p in prices])''',
     '''big = []
for p in prices:
    if p >= 5000:
        big.append(p)
print(big)
print(list(filter(lambda p: p >= 5000, prices)))
print([p for p in prices if p >= 5000])''',
     '''print([p * 9 // 10 for p in prices if p >= 5000])
print(list(map(lambda p: p * 9 // 10, filter(lambda p: p >= 5000, prices))))''',
     '''print(["비쌈" if p >= 5000 else "보통" for p in prices])''',
     '''print([p for p in prices if p >= 5000])
print([p if p >= 5000 else 0 for p in prices])'''])

print("=== 3. 여러 데이터에 쓰기")
run(['''names = ["latte", "tea", "coffee"]
print([len(m) for m in names])
print([m[0] for m in names])
print([n * n for n in range(1, 6)])''',
     '''orders = [("kim", "latte", 2), ("lee", "cake", 1), ("park", "coffee", 3), ("kim", "tea", 1)]
print([o[0] for o in orders])
print([menu_name for name, menu_name, qty in orders if qty >= 2])''',
     '''menu = {"coffee": 4500, "latte": 5000, "cake": 6500}
print({m: p * 11 // 10 for m, p in menu.items()})
stock = {"coffee": 3, "latte": 0, "cake": 2}
print({m: n for m, n in stock.items() if n > 0})
print([m for m in stock if stock[m] == 0])''',
     '''buyers = {o[0] for o in orders}
print(len(buyers))
print(sorted(buyers))'''])

print("=== 4. 함수와 함께 쓰기")
run(['''menu = {"coffee": 4500, "latte": 5000, "cake": 6500, "tea": 4000}
cart = ["coffee", "cake", "latte", "latte"]
print(sum([menu[m] for m in cart]))
print(max([len(m) for m in menu]))''',
     '''stock = {"coffee": 3, "latte": 0, "cake": 2, "tea": 5}
ok = [m for m in menu if stock[m] > 0]
print(ok)
print(sorted(ok, key=menu.get))
print(min(ok, key=menu.get))''',
     '''scores = [[90, 80], [70, 60]]
print([x for row in scores
       for x in row])'''])

print("=== 5. 오류와 함정")
run(['''prices = [4500, 5000, 6500, 3000]
print([p for p in prices if p >= 5000 else 0])''',
     '''[print(m) for m in ["latte", "tea"]]''',
     '''prices = [4500, 5000, 6500, 3000]
print((p + 500 for p in prices))
print(list(p + 500 for p in prices))''',
     '''print([x + 10 for p in prices])'''])

print("=== 6. 실습")
run(['''menu = {"coffee": 4500, "latte": 5000, "cake": 6500}
cart = ["latte", "cake", "coffee"]
lines = [f"{m:<7}{menu[m]:>6,}원" for m in cart]
print("\\n".join(lines))
print(f"합계   {sum([menu[m] for m in cart]):>6,}원")''',
     '''menu = {"coffee": 4500, "latte": 5000, "cake": 6500, "tea": 4000}
stock = {"coffee": 3, "latte": 0, "cake": 2, "tea": 0}
soldout = [m for m in stock if stock[m] == 0]
print("품절:", ", ".join(soldout))
board = {m: menu[m] * 11 // 10 for m in menu if stock[m] > 0}
print(board)''',
     '''scores = [["kim", 92], ["lee", 78], ["park", 85], ["choi", 59]]
print([name for name, score in scores if score >= 80])
print(["합격" if score >= 60 else "재시험" for name, score in scores])
print(sum([score for name, score in scores]) / len(scores))
print(max(scores, key=lambda s: s[1])[0])'''])
