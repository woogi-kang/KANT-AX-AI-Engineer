"""Runs the notebook cells shown in the deck with the project's own kernel and prints each output.
Used by tools/demo.sh. Each run() is one fresh kernel, like opening the notebook and pressing Run All."""
import nbclient
import nbformat


def run(cells):
    nb = nbformat.v4.new_notebook()
    nb.cells = [nbformat.v4.new_code_cell(c) for c in cells]
    nbclient.NotebookClient(nb, kernel_name="python3", allow_errors=True).execute()
    for c in nb.cells:
        print(f"--- [{c.execution_count}] {c.source!r}")
        for o in c.outputs:
            if o.output_type == "error":
                print(f"{o.ename}: {o.evalue}")
            else:
                print(o.get("text") or o.get("data", {}).get("text/plain"))


MENU = 'menu = {"coffee": 4500, "latte": 5000, "cake": 6500}'
print("=== 1. 만들고 꺼내기")
run(['student = ["kim", 90, 85, 77]\nprint(student[2])',
     'student = {"name": "kim", "kor": 90,\n           "eng": 85, "math": 77}\nprint(student["eng"])',
     MENU + '\nprint(menu)\nprint(type(menu))\nprint(len(menu))\ncart = {}\nprint(cart)\nprint(len(cart))',
     'print(menu["latte"])\nprice = menu["cake"]\nprint(price * 2)',
     'menu["tea"]',
     'print(menu.get("latte"))\nprint(menu.get("tea"))\nprint(menu.get("tea", 0))'])
print("=== 2. 바꾸기")
run([MENU + '\nmenu["tea"] = 4000\nprint(menu)\nmenu["latte"] = 5500\nprint(menu)\nprint(len(menu))',
     'dup = {"latte": 5000, "latte": 5500}\nprint(dup)\nprint(len(dup))\nscore = {"kim": 90, "lee": 90, "park": 90}\nprint(score)',
     'del menu["tea"]\nprint(menu)\nprice = menu.pop("cake")\nprint(price)\nprint(menu)',
     'del menu["tea"]',
     'print("latte" in menu)\nprint("tea" in menu)\nprint("tea" not in menu)\nprint(5500 in menu)\nprint(len(menu))'])
print("=== 3. 둘러보기")
run([MENU + '\nprint(menu.keys())\nprint(menu.values())\nprint(menu.items())\nprint(list(menu.keys()))',
     'keys = list(menu.keys())\nprint(keys)\nprint(keys[0])\nprint(list(menu.values())[-1])\npair = list(menu.items())[1]\nprint(pair)\nprint(pair[0], pair[1])',
     'menu.keys()[0]',
     'for name in menu:\n    print(name)',
     'for name, price in menu.items():\n    print(f"{name:<8}{price:>6,}원")',
     'print(sum(menu.values()))\nprint(max(menu.values()))\nprint(5000 in menu.values())\nprint(sorted(menu))',
     'settings = {"name": "kim"}\nprint(settings.get("name", "guest"))\nprint(settings.get("lang", "ko"))\nprint(settings.get("theme", "light"))\nprint(settings)',
     'cart = {"coffee": 2, "tea": 1}\ntotal = 0\nfor name, qty in cart.items():\n    price = menu.get(name, 0)\n    print(name, qty, price * qty)\n    total += price * qty\nprint("합계:", total)',
     'words = "coffee latte coffee cake coffee latte".split()\ncount = {}\nfor w in words:\n    count[w] = count.get(w, 0) + 1\nprint(count)\nprint(count["coffee"])',
     'votes = {}\nvotes["coffee"] = votes["coffee"] + 1'])
print("=== 4. 리스트와 섞기")
run(['scores = {"kim": [90, 85, 77],\n          "lee": [70, 95, 88],\n          "park": [60, 75, 99]}\nprint(scores["lee"])\nprint(scores["lee"][1])\nfor name, s in scores.items():\n    print(name, sum(s), max(s))',
     'orders = [{"menu": "coffee", "price": 4500, "qty": 2},\n          {"menu": "latte", "price": 5000, "qty": 1},\n          {"menu": "cake", "price": 6500, "qty": 3}]\nprint(len(orders))\nprint(orders[1])\nprint(orders[1]["menu"])\nprint(orders[2]["price"] * orders[2]["qty"])',
     'for order in orders:\n    print(order["menu"], order["price"] * order["qty"])',
     'print("=" * 33)\nprint(f"{\'KANT 카페\':^31}")\nprint(f"{\'2026-11-03  14:30\':^33}")\nprint("=" * 33)\nprint(f"{\'메뉴명\':<7}{\'단가\':>6}{\'수량\':>3}{\'금액\':>8}")\nprint("-" * 33)\ntotal = 0\ncount = 0\nfor order in orders:\n    amount = order["price"] * order["qty"]\n    print(f"{order[\'menu\']:<10}{order[\'price\']:>8,}{order[\'qty\']:>5}{amount:>10,}")\n    total += amount\n    count += order["qty"]\nprint("-" * 33)\nprint(f"{\'수량\':<6}{count:>15}")\nprint(f"{\'합계\':<6}{total:>25,}")\nprint("=" * 33)\nprint(f"{\'감사합니다\':^28}")',
     MENU + '\ncart = {"coffee": 2, "cake": 3}\ntotal = 0\nfor name, qty in cart.items():\n    price = menu[name]\n    print(f"{name} {qty}개 {price * qty:,}원")\n    total += price * qty\nprint(f"합계 {total:,}원")',
     'menu[0]', 'menu["Latte"]', 'orders["menu"]'])
