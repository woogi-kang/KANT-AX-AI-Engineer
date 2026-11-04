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
down = []
for p in prices:
    down.append(p - 500)
print(down)''',
     '''print(list(map(lambda p: p + 500, prices)))
print(list(filter(lambda p: p >= 5000, prices)))''',
     '''numbers = [1, 2, 3]
print(list(map(lambda x: x + 10, numbers)))'''])

print("=== 2. 함수를 값처럼, lambda")
run(['''def add10(x):
    return x + 10

plus = add10
print(plus(5))
print(add10)''',
     '''def double(x):
    return x * 2

def apply(f, x):
    return f(x)

print(apply(add10, 5))
print(apply(double, 5))''',
     '''add10 = lambda x: x + 10
print(add10(5))
print(add10)''',
     '''print(apply(lambda x: x * 3, 5))''',
     '''price_of = lambda price, qty: price * qty
print(price_of(4500, 2))
label = lambda p: "비쌈" if p >= 5000 else "보통"
print(label(6500), label(4500))'''])

print("=== 3. map")
run(['''prices = [4500, 5000, 6500]

def add500(p):
    return p + 500

print(list(map(add500, prices)))
print(list(map(lambda p: p + 500, prices)))
print(prices)''',
     '''m = map(lambda p: p + 500, prices)
print(m)
print(list(m))''',
     '''for p in map(lambda p: p + 500, prices):
    print(p)''',
     '''print(list(map(str, prices)))
print(", ".join(map(str, prices)))
print(list(map(int, ["3", "1", "2"])))
print(list(map(len, ["coffee", "latte", "tea"])))'''])

print("=== 4. filter")
run(['''prices = [4500, 5000, 6500, 3000]
big = []
for p in prices:
    if p >= 5000:
        big.append(p)
print(big)
print(list(filter(lambda p: p >= 5000, prices)))''',
     '''check = lambda p: p >= 5000
print(check(4500), check(5000))
print(check(6500), check(3000))''',
     '''stock = {"coffee": 3, "latte": 0, "cake": 2, "tea": 0}
print(list(filter(lambda m: stock[m] > 0, stock)))''',
     '''big = list(filter(lambda p: p >= 5000, prices))
print(big)
print(list(map(lambda p: p * 9 // 10, big)))
print(list(map(lambda p: p * 9 // 10, filter(lambda p: p >= 5000, prices))))'''])

print("=== 5. 오류와 함정")
run(['''doubled = map(lambda x: x * 2, [1, 2, 3])
print(doubled[0])''',
     '''print(len(doubled))''',
     '''doubled = list(map(lambda x: x * 2, [1, 2, 3]))
print(doubled[0])
print(len(doubled))''',
     '''m = map(lambda p: p + 500, [4500, 5000])
print(list(m))
print(list(m))''',
     '''m = map(lambda p: p + 500, [4500, 5000])
ups = list(m)
print(ups)
print(ups)''',
     '''def add10(x):
    return x + 10

print(list(map(add10(), [1, 2, 3])))''',
     '''add10 = lambda x: return x + 10''',
     '''label = lambda p: "비쌈" if p >= 6000 else ("보통" if p >= 4500 else "쌈")
print(label(6500), label(5000), label(3000))''',
     '''def label(p):
    if p >= 6000:
        return "비쌈"
    elif p >= 4500:
        return "보통"
    return "쌈"

print(label(6500), label(5000), label(3000))'''])

print("=== 6. 실습")
run(['''menu = {"coffee": 4500, "latte": 5000, "cake": 6500}
print(list(map(lambda m: menu[m] * 11 // 10, menu)))

def line(m):
    new = menu[m] * 11 // 10
    return f"{m:<7}{menu[m]:>6,}원 → {new:>6,}원"

print("\\n".join(map(line, menu)))''',
     '''menu = {"coffee": 4500, "latte": 5000, "cake": 6500, "tea": 4000}
stock = {"coffee": 3, "latte": 0, "cake": 2, "tea": 5}
print(list(filter(lambda m: stock[m] > 0, menu)))
print(list(filter(lambda m: stock[m] > 0 and menu[m] < 5000, menu)))''',
     '''orders = [("kim", "latte", 2), ("lee", "cake", 1), ("park", "coffee", 3), ("kim", "tea", 1)]
many = list(filter(lambda o: o[2] >= 2, orders))
print(many)
print(list(map(lambda o: o[0], many)))
print(sum(map(lambda o: o[2], orders)))'''])
