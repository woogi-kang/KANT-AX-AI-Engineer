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



SALES = 'sales = {"coffee": 12, "latte": 30, "cake": 8, "tea": 15}'

print("=== 1. 왜 필요한가")
run([SALES + '''
print(sorted(sales))
print(max(sales))''',
     '''names = ["latte", "tea", "coffee"]
print(sorted(names))
print(sorted(names, key=len))
print(max(sales, key=sales.get))'''])

print("=== 2. sorted와 sort, key")
run(['''prices = [6500, 4500, 5000]
a = sorted(prices)
print(a)
print(prices)
prices.sort()
print(prices)''',
     '''prices = [6500, 4500, 5000]
prices = prices.sort()
print(prices)''',
     '''prices = [6500, 4500, 5000]
print(sorted(prices, reverse=True))
prices.sort(reverse=True)
print(prices)''',
     '''print(sorted(["Latte", "cake", "Tea", "coffee"]))
print(sorted(["라떼", "커피", "녹차"]))
print(sorted(["10", "9", "100"]))''',
     '''names = ["latte", "tea", "coffee", "mocha"]
print(list(map(len, names)))
print(sorted(names, key=len))
print(sorted(names, key=len, reverse=True))''',
     '''print("Latte".lower())
print(sorted(["Latte", "cake", "Tea", "coffee"], key=str.lower))
print(sorted(["10", "9", "100"], key=int))'''])

print("=== 3. 튜플과 딕셔너리 정렬")
run(['''items = [("latte", 5000), ("cake", 6500), ("coffee", 4500), ("cake", 6000)]
print(sorted(items))''',
     '''items = [("latte", 5000), ("cake", 6500), ("coffee", 4500)]
print(sorted(items, key=lambda m: m[1]))
print(sorted(items, key=lambda m: m[1], reverse=True))''',
     '''sales = [("latte", 30), ("cake", 8), ("coffee", 30), ("tea", 15)]
print(sorted(sales, key=lambda m: m[1], reverse=True))
print(list(map(lambda m: (-m[1], m[0]), sales)))
print(sorted(sales, key=lambda m: (-m[1], m[0])))''',
     SALES + '''
print(sorted(sales))
print(sorted(sales.values()))
print(sorted(sales.items()))''',
     '''rank = sorted(sales.items(), key=lambda kv: kv[1], reverse=True)
print(rank)
for name, n in rank:
    print(f"{name:<7}{n:>3}잔")''',
     '''print(sales.get("latte"))
print(sorted(sales, key=sales.get))
print(sorted(sales, key=sales.get, reverse=True))'''])

print("=== 4. max와 min")
run(['''prices = [4500, 5000, 6500, 3000]
print(max(prices), min(prices))
names = ["latte", "tea", "coffee"]
print(max(names), min(names))
print(max(names, key=len))''',
     SALES + '''
print(max(sales))
print(max(sales, key=sales.get))
print(min(sales, key=sales.get))
print(max(sales.items(), key=lambda kv: kv[1]))''',
     '''print(max([]))''',
     '''big = list(filter(lambda p: p > 10000, prices))
print(big)
print(max(big, default=0))''',
     '''print(sum(sales.values()), len(sales))
print(sum(sales.values()) / len(sales))
top3 = sorted(sales, key=sales.get, reverse=True)[:3]
print(top3)'''])

print("=== 5. 오류와 함정")
run(['''print(sorted([4500, "5000", 6500]))''',
     '''print(sorted([4500, "5000", 6500], key=int))''',
     '''print(sorted(["latte", "tea"], key=len()))''',
     SALES + '''
print(sorted(sales, key=sales.get()))''',
     '''print(sorted(sales.items(), key=kv[1]))''',
     '''print(sorted(sales, sales.get))'''])

print("=== 6. 실습")
run(['''sales = {"coffee": 12, "latte": 30, "cake": 8, "tea": 15, "juice": 15}
rank = sorted(sales.items(), key=lambda kv: (-kv[1], kv[0]))
for i, kv in enumerate(rank[:3], 1):
    print(f"{i}위 {kv[0]:<6}{kv[1]:>3}잔")''',
     '''menu = {"coffee": 4500, "latte": 5000, "cake": 6500, "tea": 4000}
hi = max(menu, key=menu.get)
lo = min(menu, key=menu.get)
print(f"가장 비싼 메뉴 {hi} {menu[hi]:,}원")
print(f"가장 싼 메뉴 {lo} {menu[lo]:,}원")
for m in sorted(menu, key=menu.get):
    print(f"{m:<7}{menu[m]:>6,}원")''',
     '''names = ["mocha", "tea", "latte", "americano", "cake"]
print(sorted(names, key=len))
print(sorted(names, key=lambda n: (len(n), n)))''',
     '''scores = [("kim", 92), ("lee", 78), ("park", 85), ("choi", 59)]
ranked = sorted(scores, key=lambda s: s[1], reverse=True)
for name, score in ranked:
    print(f"{name:<5}{score:>3}")
print("1등:", max(scores, key=lambda s: s[1])[0])
print("평균:", sum(map(lambda s: s[1], scores)) / len(scores))'''])
