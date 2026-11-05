"""Runs the notebook cells shown in the deck with the project's own kernel and prints each output.
Used by tools/demo.sh. Each run() is one fresh kernel, like opening the notebook and pressing Run All.
Error lines keep only the last line of the traceback."""
import re

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
                last = re.sub(r"\x1b\[[0-9;]*m", "", "\n".join(o.traceback)).strip().splitlines()[-1]
                print(last)   # last traceback line, with hints like "Did you mean"
            else:
                t = o.get("text") or o.get("data", {}).get("text/plain")
                lines = t.splitlines()
                if len(lines) > 12:
                    t = "\n".join(lines[:5]) + f"\n... ({len(lines)} lines)"
                print(t)




B = '''class Bread:
    def __init__(self, flavor, price):
        self.flavor = flavor
        self.price = price
'''
STR = '''
    def __str__(self):
        return f"{self.flavor} 붕어빵 {self.price:,}원"
'''
REPR = '''
    def __repr__(self):
        return f"Bread('{self.flavor}', {self.price})"
'''
AB = '''
a = Bread("팥", 1000)
b = Bread("슈크림", 1200)'''

print("=== 1. 왜 필요한가")
run(['''print(3)
print("팥")
print([1, 2])''',
     B + AB + '''
print(a)
print([a, b])''',
     '''class Bread:
    def __init__(self, flavor, price):
        self.flavor = flavor
        self.price = price

    def __str__(self):
        return "붕어빵이에요"

a = Bread("팥", 1000)
print(a)'''])

print("=== 2. __str__")
run([B + STR + AB + '''
print(a)
print(b)''',
     '''print(str(a))
print(f"주문: {a}")
print("오늘의 빵:", b)''',
     '''msg = "포장할게요: " + str(a)
print(msg)
print(len(str(a)))'''])

print("=== 3. __repr__")
run([B + STR + AB + '''
a''',
     '''print([a, b])''',
     '''"팥"''',
     '''print("팥")
print(["팥", "슈크림"])
print(str("팥"))
print(repr("팥"))''',
     B + STR + REPR + AB + '''
a''',
     '''print(a)
print([a, b])''',
     B + REPR + AB + '''
print(a)
print([a, b])''',
     '''print(len([1, 2, 3]))
print([1, 2, 3].__len__())
print(3 + 4)
print((3).__add__(4))'''])

print("=== 4. 붕어빵 여러 개 다루기")
run([B + STR + REPR + '''
breads = [Bread("팥", 1000), Bread("슈크림", 1200), Bread("피자", 1500)]
for b in breads:
    print(b)''',
     '''print([b.flavor for b in breads])
print(sum([b.price for b in breads]))
print([b for b in breads if b.price >= 1200])''',
     '''print(sorted(breads, key=lambda b: b.price, reverse=True))
print(max(breads, key=lambda b: b.price))''',
     '''print(sorted(breads))''',
     '''class Stall:
    def __init__(self, name, stock):
        self.name = name
        self.stock = stock
        self.sold = 0

    def sell(self, qty):
        self.stock = self.stock - qty
        self.sold = self.sold + qty

    def __str__(self):
        return f"{self.name}: 남은 {self.stock}개, 판매 {self.sold}개"

s = Stall("팥", 10)
print(s)
s.sell(3)
print(s)''',
     '''class Stall:
    def __init__(self, name, stock):
        self.name = name
        self.stock = stock
        self.sold = 0

    def sell(self, qty):
        if qty > self.stock:
            return "재고가 모자라요"
        self.stock = self.stock - qty
        self.sold = self.sold + qty
        return "판매 완료"

s = Stall("팥", 5)
print(s.sell(3))
print(s.sell(4))
print(s.stock, s.sold)'''])

print("=== 5. 오류와 함정")
run([B + '''
    def __str__(self):
        print(self.flavor, "붕어빵")
''' + AB + '''
print(a)''',
     B + '''
    def __str__(self):
        return self.price
''' + AB + '''
print(a)''',
     B + '''
    def _str_(self):
        return f"{self.flavor} 붕어빵"
''' + AB + '''
print(a)''',
     B + STR + AB + '''
print("주문: " + a)'''])

print("=== 6. 실습")
run(['''class Stall:
    def __init__(self, flavor, price, stock):
        self.flavor = flavor
        self.price = price
        self.stock = stock
        self.sold = 0

    def sell(self, qty):
        if qty > self.stock:
            return f"{self.flavor} 재고가 모자라요"
        self.stock = self.stock - qty
        self.sold = self.sold + qty
        return f"{self.flavor} {qty}개 판매"

    def __str__(self):
        return f"{self.flavor}: 판매 {self.sold}개, 매출 {self.sold * self.price:,}원"''',
     '''pat = Stall("팥", 1000, 20)
cream = Stall("슈크림", 1200, 10)
print(pat.sell(5))
print(cream.sell(12))
print(cream.sell(4))
print(pat)
print(cream)''',
     '''class Drink:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def __str__(self):
        return f"{self.name:<7}{self.price:>6,}원"

    def __repr__(self):
        return f"Drink('{self.name}', {self.price})"

menu = [Drink("latte", 5000), Drink("tea", 4000), Drink("coffee", 4500)]
for d in sorted(menu, key=lambda d: d.price):
    print(d)
print([d for d in menu if d.price < 5000])'''])
