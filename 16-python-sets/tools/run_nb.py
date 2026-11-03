"""Runs the notebook cells shown in the deck with the project's own kernel and prints each output.
Used by tools/demo.sh. Each run() is one fresh kernel, like opening the notebook and pressing Run All.
A set of strings prints in a different order on every new kernel. run() fixes PYTHONHASHSEED per kernel
so the deck can be regenerated with the same output; students will often see another order."""
import os
import nbclient
import nbformat


def run(cells, seed=0):
    os.environ["PYTHONHASHSEED"] = str(seed)
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


MENUS = 'menus = {"coffee", "latte", "cake"}'
print("=== 1. 집합이 뭔가요")
run(['nums = [3, 1, 3, 2, 1]\nprint(nums)\nprint(set(nums))',
     'nums = {3, 1, 2, 3}\nprint(nums)\nprint(type(nums))\nprint(len(nums))',
     MENUS + '\nprint(menus)\nprint(sorted(menus))',
     'orders = ["coffee", "latte", "coffee", "cake", "latte"]\nkinds = set(orders)\nprint(kinds)\nprint(len(orders), len(kinds))\nprint(sorted(kinds))',
     'print(set("banana"))\nprint(len(set("banana")))\nprint(set(["banana"]))\nprint({"banana"})',
     'a = {}\nprint(type(a))\nb = set()\nprint(type(b))\nprint(b)\nprint(len(b))',
     'ok = {1, "kim", (2, 3)}\nprint(len(ok))',
     'bad = {[1, 2], 3}',
     'd = {[1, 2]: "a"}'], seed=22)
print("=== 1b. 같은 셀을 새 커널에서")
run([MENUS + '\nprint(menus)\nprint(sorted(menus))'], seed=22)
run([MENUS + '\nprint(menus)\nprint(sorted(menus))'], seed=13)
print("=== 2. 바꾸고 확인하기")
run([MENUS + '\nmenus.add("tea")\nprint(menus)\nmenus.add("coffee")\nprint(menus)\nprint(len(menus))',
     'menus.remove("latte")\nprint(menus)',
     'menus.remove("juice")',
     'menus.discard("juice")\nmenus.discard("tea")\nprint(menus)',
     'menus.update(["juice", "tea", "coffee"])\nprint(menus)\nprint(len(menus))',
     'one = menus.pop()\nprint(one)\nprint(menus)\nnums = [10, 20, 30]\nprint(nums.pop())',
     'menus.clear()\nprint(menus)\nprint(len(menus))',
     MENUS + '\nprint("latte" in menus)\nprint("tea" in menus)\nprint("tea" not in menus)',
     'menus[0]',
     'print(sorted(menus))\nprint(sorted(menus)[0])\nprint(list(menus))',
     'for m in menus:\n    print(m)',
     'for m in sorted(menus):\n    print(m)'], seed=22)
print("=== 3. 집합 연산")
run(['a = {1, 2, 3, 4}\nb = {3, 4, 5, 6}\nprint(a | b)\nprint(a.union(b))',
     'print(a & b)\nprint(a.intersection(b))',
     'print(a - b)\nprint(b - a)\nprint(a.difference(b))',
     'c = a | b\nprint(a, b)\nprint(len(c), len(a & b))'], seed=22)
print("=== 4. 실습")
run(['orders = ["coffee", "latte", "coffee", "cake",\n          "coffee", "latte", "tea"]\nkinds = set(orders)\nprint(f"주문 {len(orders)}잔, 메뉴 {len(kinds)}가지")\nfor m in sorted(kinds):\n    print(m, orders.count(m))',
     'python_class = {"kim", "lee", "park", "choi"}\ndata_class = {"park", "choi", "jung", "kang"}\nboth = python_class & data_class\nprint(sorted(both))\nprint(sorted(python_class - data_class))\nprint(sorted(data_class - python_class))\nprint(f"모두 {len(python_class | data_class)}명")',
     'menu = {"coffee": 4500, "latte": 5000, "cake": 6500}\norders = ["coffee", "tea", "cake", "juice", "coffee"]\nprint(set(menu))\nprint(sorted(set(orders) - set(menu)))\nprint(sorted(set(orders) & set(menu)))',
     'total = 0\nfor m in sorted(set(orders) & set(menu)):\n    qty = orders.count(m)\n    print(f"{m:<8}{qty}개 {menu[m] * qty:>7,}원")\n    total += menu[m] * qty\nprint(f"합계 {total:,}원")',
     'cart = {}\ncart.add("coffee")',
     'menus = {"coffee", "latte"}\nmenus[0]',
     'menus.remove("tea")',
     'print(set("latte"))\nprint({"latte"})'], seed=22)
