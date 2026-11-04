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
run(['def order(menu_name, size):\n    print(f"{menu_name} {size} 사이즈")\n\norder("latte", "M")\norder("coffee", "M")\norder("tea", "M")',
     'order("cake")',
     'def calc():\n    total = 4500 * 2\n\ncalc()\nprint(total)',
     'def order(menu_name, size="M"):\n    print(f"{menu_name} {size} 사이즈")\n\norder("latte")\norder("latte", "L")'])

print("=== 2. 기본값과 키워드 인자")
run(['def order(menu_name, size="M", qty=1):\n    print(f"{menu_name} {size} {qty}잔")\n\norder("latte")\norder("latte", "L")\norder("latte", "L", 2)\norder("latte", qty=3)',
     'order(size="L", menu_name="tea")\norder("tea", qty=2, size="S")',
     'def order(size="M", menu_name):\n    print(menu_name, size)',
     'order(size="L", "tea")',
     'print("coffee", "latte", sep=" / ")\nprint("coffee", end=" ")\nprint("latte")\nprint(sorted([5000, 4500, 6500], reverse=True))'])

print("=== 3. 지역 변수")
run(['def calc():\n    total = 4500 * 2\n    print("안:", total)\n\ncalc()\nprint("밖:", total)',
     'def greet(name):\n    print(f"{name}님, 어서 오세요")\n\ngreet("kim")\nprint(name)',
     'def add_stamp():\n    stamp = 0\n    stamp += 1\n    print("도장", stamp)\n\nadd_stamp()\nadd_stamp()\nadd_stamp()'])

print("=== 4. 전역 변수")
run(['shop = "KANT 카페"\n\ndef hello():\n    print(f"{shop}에 어서 오세요")\n\nhello()',
     'price = 4500\n\ndef set_price():\n    price = 5000\n    print("안:", price)\n\nset_price()\nprint("밖:", price)',
     'count = 0\n\ndef visit():\n    count = count + 1\n\nvisit()',
     'count = 0\n\ndef visit():\n    global count\n    count = count + 1\n\nvisit()\nvisit()\nvisit()\nprint(count)',
     'def visit(count):\n    return count + 1\n\ncount = 0\ncount = visit(count)\ncount = visit(count)\ncount = visit(count)\nprint(count)'])

print("=== 5. 리스트와 딕셔너리 넘기기")
run(['def add_item(cart, name):\n    cart.append(name)\n\nmy_cart = ["coffee"]\nadd_item(my_cart, "cake")\nadd_item(my_cart, "latte")\nprint(my_cart)',
     'def add_one(n):\n    n += 1\n    print("안:", n)\n\nx = 1\nadd_one(x)\nprint("밖:", x)',
     'def sell(stock, name):\n    stock[name] -= 1\n\nstock = {"coffee": 3, "latte": 1}\nsell(stock, "latte")\nsell(stock, "coffee")\nprint(stock)',
     'def with_item(cart, name):\n    new_cart = cart.copy()\n    new_cart.append(name)\n    return new_cart\n\nmy_cart = ["coffee"]\nbig_cart = with_item(my_cart, "cake")\nprint(my_cart)\nprint(big_cart)'])

print("=== 6. 실습")
run(['def take_order(stock, name, qty=1):\n    if stock[name] < qty:\n        print(f"{name} {qty}개: 재고가 {stock[name]}개뿐이에요")\n        return False\n    stock[name] -= qty\n    print(f"{name} {qty}개 나갔어요")\n    return True\n\nstock = {"coffee": 3, "latte": 1, "cake": 2}\ntake_order(stock, "coffee", 2)\ntake_order(stock, "latte")\ntake_order(stock, "latte")\ntake_order(stock, "cake", qty=3)\nprint(stock)',
     'menu = {"coffee": 4500, "latte": 5000, "cake": 6500}\n\ndef calc_total(cart, menu):\n    total = 0\n    for name, qty in cart.items():\n        total += menu[name] * qty\n    return total\n\ndef print_receipt(cart, menu, rate=0):\n    total = calc_total(cart, menu)\n    sale = total * rate // 100\n    for name, qty in cart.items():\n        print(f"{name:<7}{qty}개 {menu[name] * qty:>7,}원")\n    print(f"할인   {rate:>2}% {sale:>7,}원")\n    print(f"결제       {total - sale:>7,}원")',
     'cart1 = {"coffee": 2, "cake": 1}\ncart2 = {"latte": 3, "cake": 2}\nprint_receipt(cart1, menu)\nprint("---")\nprint_receipt(cart2, menu, rate=10)',
     'def add_point(points, name, amount, rate=5):\n    points[name] = points.get(name, 0) + amount * rate // 100\n\npoints = {"kim": 300}\nadd_point(points, "kim", 9000)\nadd_point(points, "lee", 6500)\nadd_point(points, "lee", 10000, rate=10)\nprint(points)'])
