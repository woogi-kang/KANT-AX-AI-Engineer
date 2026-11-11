"""Every file and command the deck shows, as scenes. tools/demo.sh runs them with uv and writes tools/out.json.
tools/gen.py reads the same scenes, so the code on a slide and the code that produced its output are one text.

Each scene starts from a fresh copy of the class project (tools/src/product.py and cart.py, as written in class,
with the test code at the bottom of cart.py) plus uv init's main.py, then applies its own files and runs its commands.
"""
import os

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
PRODUCT = open(os.path.join(SRC, "product.py")).read()
CART = open(os.path.join(SRC, "cart.py")).read()

# cart.py's test code at the bottom, as written in class (no if __name__ guard)
CART_BODY, CART_TEST = CART.split("\n\n# -------------------------------------------\n# 테스트 코드\n", 1)
CART_TEST = "# 테스트 코드\n" + CART_TEST
GUARD_TEST = '''# 테스트 코드
if __name__ == "__main__":
    tumbler = Product("텀블러", 15_000, 10)
    earphone = Product("무선 이어폰", 89_000, 3)

    cart = Cart()
    cart.add(tumbler, 1)
    cart.add(earphone, 2)
    cart.show()
'''
CART_GUARDED = CART_BODY + "\n\n" + GUARD_TEST

COUPON = '''COUPONS = {"WELCOME": 3_000, "VIP": 5_000}


def discount(code):
    return COUPONS.get(code, 0)
'''


def swap(text, old, new):
    assert old in text, old
    return text.replace(old, new, 1)


SCENES = {}


def S(name, files, cmds):
    SCENES[name] = {"files": files, "cmds": cmds}


# ---------- 1. why ----------
S("class-run", {}, ["uv run cart.py"])

# ---------- 2. indentation ----------
SHOW_IN = swap(CART_GUARDED, '''            print(f"{p.name:<10} x {q:<3} = {p.price * q:>12,}원")

        print(line)''', '''            print(f"{p.name:<10} x {q:<3} = {p.price * q:>12,}원")
            print(line)''')
S("show-ok", {"cart.py": CART_GUARDED}, ["uv run cart.py"])
S("show-in", {"cart.py": SHOW_IN}, ["uv run cart.py"])

RET_OUT = swap(CART_GUARDED, '''            print("품절된 상품입니다.")
            return
''', '''            print("품절된 상품입니다.")
        return
''')
S("ret-out", {"cart.py": RET_OUT}, ["uv run cart.py"])

ERR_NOINDENT = swap(CART_GUARDED, '''    def is_empty(self):
        return len(self.items) == 0''', '''    def is_empty(self):
    return len(self.items) == 0''')
ERR_UNINDENT = swap(CART_GUARDED, '''            self.items[product] -= qty
            print(f"{product.name} {qty}개를 뺐습니다.")''', '''            self.items[product] -= qty
          print(f"{product.name} {qty}개를 뺐습니다.")''')
S("err-noindent", {"cart.py": ERR_NOINDENT}, ["uv run cart.py"])
S("err-unindent", {"cart.py": ERR_UNINDENT}, ["uv run cart.py"])

# ---------- 3. items() ----------
S("tuple", {"play.py": '''a, b = (1, 2)
print(a)
print(b)

name, qty = ("텀블러", 1)
print(name, qty)
'''}, ["uv run play.py"])
S("pairs", {"play.py": '''cart_items = {"텀블러": 1, "무선 이어폰": 2}

print(cart_items.items())
print(list(cart_items.items()))
'''}, ["uv run play.py"])
S("for", {"play.py": '''cart_items = {"텀블러": 1, "무선 이어폰": 2}

for name, qty in cart_items.items():
    print(name, qty)
'''}, ["uv run play.py"])
S("long", {"play.py": '''cart_items = {"텀블러": 1, "무선 이어폰": 2}

for pair in cart_items.items():
    name = pair[0]
    qty = pair[1]
    print(name, qty)
'''}, ["uv run play.py"])
S("twoitems", {"play.py": '''from product import Product
from cart import Cart

tumbler = Product("텀블러", 15_000, 10)
earphone = Product("무선 이어폰", 89_000, 3)

cart = Cart()
cart.add(tumbler, 1)
cart.add(earphone, 2)

for p, q in cart.items.items():
    print(p.name, p.price, q)
''', "cart.py": CART_GUARDED}, ["uv run play.py"])
S("subtotal", {"play.py": '''from product import Product
from cart import Cart

tumbler = Product("텀블러", 15_000, 10)
earphone = Product("무선 이어폰", 89_000, 3)
cart = Cart()
cart.add(tumbler, 1)
cart.add(earphone, 2)

total = 0
for p, q in cart.items.items():
    total = total + p.price * q
print(total)

print(sum([p.price * q for p, q in cart.items.items()]))
print(cart.subtotal())
''', "cart.py": CART_GUARDED}, ["uv run play.py"])
S("err-noitems", {"play.py": '''from product import Product
from cart import Cart

tumbler = Product("텀블러", 15_000, 10)
cart = Cart()
cart.add(tumbler, 1)

for p, q in cart.items:
    print(p.name, q)
''', "cart.py": CART_GUARDED}, ["uv run play.py"])
S("err-str", {"play.py": '''cart_items = {"텀블러": 1, "무선 이어폰": 2}

for name, qty in cart_items:
    print(name, qty)
'''}, ["uv run play.py"])

# ---------- 4. modules ----------
S("import", {"main.py": '''import product

tumbler = product.Product("텀블러", 15_000, 10)
print(tumbler)
''', "cart.py": CART_GUARDED}, ["uv run main.py"])
S("from", {"main.py": '''from product import Product

tumbler = Product("텀블러", 15_000, 10)
print(tumbler)
''', "cart.py": CART_GUARDED}, ["uv run main.py"])
S("from-many", {"coupon.py": COUPON, "main.py": '''from coupon import COUPONS, discount

print(COUPONS)
print(discount("VIP"))
print(discount("HELLO"))
''', "cart.py": CART_GUARDED}, ["uv run main.py"])
S("as", {"coupon.py": COUPON, "main.py": '''import coupon as cp

print(cp.discount("VIP"))
''', "cart.py": CART_GUARDED}, ["uv run main.py"])
S("err-typo", {"main.py": '''import prodcut
''', "cart.py": CART_GUARDED}, ["uv run main.py"])
S("err-name", {"main.py": '''from product import product
''', "cart.py": CART_GUARDED}, ["uv run main.py"])
S("err-noname", {"main.py": '''import product

tumbler = Product("텀블러", 15_000, 10)
''', "cart.py": CART_GUARDED}, ["uv run main.py"])

# ---------- 5. __name__ ----------
S("leak", {"main.py": '''from cart import Cart

print("main.py 시작")
cart = Cart()
'''}, ["uv run main.py"])
NAME_PRINT = 'print("cart.py의 __name__:", __name__)\n'
S("name", {"cart.py": CART_BODY + "\n\n" + NAME_PRINT, "main.py": '''from cart import Cart

print("main.py의 __name__:", __name__)
'''}, ["uv run cart.py", "uv run main.py"])
S("guarded", {"cart.py": CART_GUARDED, "main.py": '''from cart import Cart

print("main.py 시작")
cart = Cart()
'''}, ["uv run main.py", "uv run cart.py"])

# ---------- 6. practice ----------
MAIN_SHOP = '''from product import Product
from cart import Cart

tumbler = Product("텀블러", 15_000, 10)
earphone = Product("무선 이어폰", 89_000, 3)
pad = Product("마우스패드", 9_000, 0)

cart = Cart()
cart.add(tumbler, 2)
cart.add(earphone, 1)
cart.add(pad, 1)
cart.checkout()

print(tumbler)
print(earphone)
'''
S("shop", {"cart.py": CART_GUARDED, "main.py": MAIN_SHOP}, ["uv run main.py"])
MAIN_COUPON = '''from product import Product
from cart import Cart
from coupon import COUPONS, discount

for code, amount in COUPONS.items():
    print(f"{code:<8} {amount:>6,}원 할인")

tumbler = Product("텀블러", 15_000, 10)
cart = Cart()
cart.add(tumbler, 3)

pay = cart.total() - discount("VIP")
print(f"결제할 금액: {pay:,}원")
'''
S("coupon", {"cart.py": CART_GUARDED, "coupon.py": COUPON, "main.py": MAIN_COUPON}, ["uv run main.py"])
