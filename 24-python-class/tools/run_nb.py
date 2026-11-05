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




print("=== 1. 왜 필요한가")
run(['''b1 = {"flavor": "팥", "price": 1000}
b2 = {"flavor": "슈크림", "price": 1200}

def intro(bread):
    print(bread["flavor"], "붕어빵", bread["price"], "원")

intro(b1)
intro(b2)''',
     '''b3 = {"flavr": "피자", "price": 1500}
intro(b3)''',
     '''print(type(3))
print(type("팥"))
print(type([1, 2]))''',
     '''xs = [1, 2]
xs.append(3)
print(xs)
print("Pat".lower())'''])

print("=== 2. 가장 작은 틀")
run(['''class Bread:
    pass

a = Bread()
b = Bread()
print(type(a))''',
     '''a.flavor = "팥"
a.price = 1000
b.flavor = "슈크림"
b.price = 1200
print(a.flavor, a.price)
print(b.flavor, b.price)''',
     '''c = Bread()
c.flavor = "피자"
print(c.price)'''])

print("=== 3. self와 __init__")
run(['''class Bread:
    pass

def setup(bread, flavor, price):
    bread.flavor = flavor
    bread.price = price

a = Bread()
setup(a, "팥", 1000)
print(a.flavor, a.price)''',
     '''class Bread:
    def __init__(self, flavor, price):
        self.flavor = flavor
        self.price = price

a = Bread("팥", 1000)
print(a.flavor, a.price)''',
     '''class Bread:
    def __init__(self, flavor, price):
        print("반죽 붓는 중:", flavor)
        self.flavor = flavor
        self.price = price

a = Bread("팥", 1000)
b = Bread("슈크림", 1200)
print(a.flavor, b.flavor)''',
     '''class Bread:
    def __init__(self, flavor, price):
        flavor = flavor
        price = price

a = Bread("팥", 1000)
print(a.flavor)''',
     '''class Bread:
    def __init__(self, flavor, price):
        self.flavor = flavor
        self.price = price
        self.baked = False

a = Bread("팥", 1000)
print(a.flavor, a.price, a.baked)'''])

print("=== 4. 메서드")
run(['''class Bread:
    def __init__(self, flavor, price):
        self.flavor = flavor
        self.price = price

    def intro(self):
        print(self.flavor, "붕어빵", self.price, "원")

a = Bread("팥", 1000)
b = Bread("슈크림", 1200)
a.intro()
b.intro()''',
     '''Bread.intro(a)
Bread.intro(b)''',
     '''class Bread:
    def __init__(self, flavor, price):
        self.flavor = flavor
        self.price = price

    def discount(self, won):
        self.price = self.price - won

    def total(self, qty):
        return self.price * qty

a = Bread("팥", 1000)
b = Bread("슈크림", 1200)
a.discount(200)
print(a.price, b.price)
print(a.total(3))'''])

print("=== 5. 오류와 함정")
run(['''class Bread:
    def __init__(self, flavor, price):
        self.flavor = flavor
        self.price = price

    def intro():
        print("붕어빵")

a = Bread("팥")''',
     '''a = Bread("팥", 1000)
a.intro()''',
     '''class Bread:
    def _init_(self, flavor, price):
        self.flavor = flavor
        self.price = price

a = Bread("팥", 1000)''',
     '''class Bread:
    def __init__(self, flavor, price):
        self.flavor = flavor
        self.price = price

a = Bread("팥", 1000)
print(a)''',
     '''class Bread:
    def __init__(self, flavor, price):
        self.flavor = flavor
        self.price = price

    def intro(self):
        print(flavor, "붕어빵")

a = Bread("팥", 1000)
a.intro()''',
     '''a = Bread
a.intro()''',
     '''a = Bread("팥", 1000)
print(a.flavr)'''])

print("=== 6. 실습")
run(['''class Bread:
    def __init__(self, flavor, price):
        self.flavor = flavor
        self.price = price

    def intro(self):
        print(self.flavor, "붕어빵", self.price, "원")

order = [Bread("팥", 1000), Bread("슈크림", 1200), Bread("팥", 1000)]
for b in order:
    b.intro()
total = sum([b.price for b in order])
print("합계", total, "원")''',
     '''class Drink:
    def __init__(self, name, price, size="M"):
        self.name = name
        self.price = price
        self.size = size

    def label(self):
        return f"{self.name}({self.size}) {self.price:,}원"

d1 = Drink("latte", 5000)
d2 = Drink("tea", 4000, "L")
print(d1.label())
print(d2.label())''',
     '''class Card:
    def __init__(self, name):
        self.name = name
        self.stamps = 0

    def add(self):
        self.stamps = self.stamps + 1

kim = Card("kim")
lee = Card("lee")
kim.add()
kim.add()
kim.add()
lee.add()
print(kim.name, kim.stamps)
print(lee.name, lee.stamps)'''])
