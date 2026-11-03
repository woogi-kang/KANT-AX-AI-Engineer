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
BUY = 'if money >= price:\n    print("주문할 수 있어요")\nprint("다음 손님")'
SALE = 'if total >= 20000:\n    print("10% 할인")\nelif total >= 10000:\n    print("5% 할인")\nelse:\n    print("할인 없음")'

print("=== 1. 왜 필요한가와 참, 거짓")
run([MENU + '\norder = "tea"\nprint(menu[order])',
     'money = 5000\nprice = 4500\n' + BUY,
     'print(money >= price)\nprint(money == price)\nprint("tea" in menu)\nprint("tea" not in menu)\nprint(type(money >= price))'])

print("=== 2. if, else, elif")
run(['price = 4500\nmoney = 5000\n' + BUY,
     'money = 3000\n' + BUY,
     'money = 3000\nif money >= price:\n    print("주문할 수 있어요")\n    print("커피 나왔어요")\nprint("다음 손님")',
     'money = 3000\nif money >= price:\n    print("주문할 수 있어요")\nprint("커피 나왔어요")\nprint("다음 손님")',
     'money = 3000\nif money >= price:\n    print("주문할 수 있어요")\nelse:\n    print(f"{price - money}원 더 필요해요")',
     'total = 12000\n' + SALE,
     'total = 25000\n' + SALE,
     'total = 3000\n' + SALE,
     'total = 25000\nif total >= 10000:\n    print("5% 할인")\nelif total >= 20000:\n    print("10% 할인")\nelse:\n    print("할인 없음")',
     'total = 25000\nif total >= 20000:\n    print("10% 할인")\nif total >= 10000:\n    print("5% 할인")'])

print("=== 3. 조건 합치기")
run(['height = 130\nage = 9\nif height >= 120 and age >= 7:\n    print("탈 수 있어요")\nelse:\n    print("다음에 타요")',
     'height = 110\nif height >= 120 and age >= 7:\n    print("탈 수 있어요")\nelse:\n    print("다음에 타요")',
     'height = 130\nif height >= 120:\n    if age >= 7:\n        print("탈 수 있어요")',
     'is_member = False\ntotal = 60000\nif is_member or total >= 50000:\n    print("할인해 드려요")',
     MENU + '\norder = "tea"\nif not order in menu:\n    print("메뉴판에 없어요")\nif order not in menu:\n    print("메뉴판에 없어요")',
     'hour = 14\nif 9 <= hour < 18:\n    print("영업 중이에요")\nif hour >= 9 and hour < 18:\n    print("영업 중이에요")',
     'hour = 20\nif 9 <= hour < 18:\n    print("영업 중이에요")\nelse:\n    print("문 닫았어요")',
     'print(bool(0), bool(4500))\nprint(bool(""), bool("tea"))\nprint(bool([]), bool(["tea"]))\nprint(bool({}), bool(set()))\nprint(bool(None))',
     'orders = []\nif orders:\n    print(len(orders), "잔 주문")\nelse:\n    print("아직 주문이 없어요")\nif len(orders) > 0:\n    print(len(orders), "잔 주문")\nelse:\n    print("아직 주문이 없어요")'])

print("=== 4. for와 함께, 줄여 쓰기")
run([MENU + '\nprices = [4500, 5000, 6500, 4000]\ncheap = []\nfor p in prices:\n    if p <= 5000:\n        cheap.append(p)\nprint(cheap)',
     'orders = ["coffee", "latte", "coffee", "cake", "tea", "coffee"]\nn = 0\nfor o in orders:\n    if o == "coffee":\n        n += 1\nprint(n)\nprint(orders.count("coffee"))',
     'for name, price in menu.items():\n    if price <= 5000:\n        print(name, price)',
     'total = 12000\nif total >= 10000:\n    msg = "5% 할인"\nelse:\n    msg = "할인 없음"\nprint(msg)\nmsg = "5% 할인" if total >= 10000 else "할인 없음"\nprint(msg)',
     'if "cakee" in menu:\n    price = menu["cakee"]\nelse:\n    price = 5000\nprint(price)\nprint(menu["cakee"] if "cakee" in menu else 5000)\nprint(menu.get("cakee", 5000))',
     'menus = {"coffee", "cake"}\nif "juice" in menus:\n    menus.remove("juice")\nprint(sorted(menus))\nmenus.discard("juice")\nprint(sorted(menus))',
     'kinds = []\nfor o in orders:\n    if o not in kinds:\n        kinds.append(o)\nprint(kinds)\nprint(sorted(set(orders)))'])

print("=== 5. 자주 나는 오류")
run(['order = "coffee"\nif order = "coffee":\n    print("커피예요")',
     'if order == "coffee"\n    print("커피예요")',
     'if order == "coffee":\nprint("커피예요")',
     'if order == "coffee":\n    print("커피예요")\n      print("나왔어요")',
     'order = "cake"\nif order == "coffee" or "latte":\n    print("커피 종류예요")\nprint(order == "coffee" or "latte")',
     'if order == "coffee" or order == "latte":\n    print("커피 종류예요")\nelse:\n    print("커피 종류가 아니에요")\nprint(order in ["coffee", "latte"])',
     'price = "4500"\nif price >= 4000:\n    print("4000원 넘어요")',
     'if int(price) >= 4000:\n    print("4000원 넘어요")'])

print("=== 6. 실습")
run([MENU + '\ncart = {"coffee": 2, "cake": 1}\ntotal = 0\nfor name, qty in cart.items():\n    total += menu[name] * qty\nif total >= 20000:\n    rate = 10\nelif total >= 10000:\n    rate = 5\nelse:\n    rate = 0\nsale = total * rate // 100\nprint(f"합계 {total:>7,}원")\nprint(f"할인 {sale:>7,}원 ({rate}%)")\nprint(f"결제 {total - sale:>7,}원")',
     'scores = [["kim", 92], ["lee", 78], ["park", 85], ["choi", 59]]\nfor name, score in scores:\n    if score >= 90:\n        grade = "A"\n    elif score >= 80:\n        grade = "B"\n    elif score >= 70:\n        grade = "C"\n    else:\n        grade = "F"\n    print(f"{name:<5}{score:>3}  {grade}")',
     'orders = ["coffee", "tea", "cake", "coffee", "juice"]\ntotal = 0\nskipped = []\nfor o in orders:\n    if o in menu:\n        print(f"{o:<8}{menu[o]:>6,}원")\n        total += menu[o]\n    else:\n        skipped.append(o)\nprint(f"합계 {total:,}원")\nif skipped:\n    print("준비 중:", skipped)'])
