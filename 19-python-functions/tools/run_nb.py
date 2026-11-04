"""Runs the notebook cells shown in the deck with the project's own kernel and prints each output.
Used by tools/demo.sh. Each run() is one fresh kernel, like opening the notebook and pressing Run All.
Error lines keep only the last line of the traceback. Function objects print with a memory address that changes on every run."""
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




MENU = 'menu = {"coffee": 4500, "latte": 5000, "cake": 6500}'

print("=== 1. 왜 필요한가")
run([MENU + '\ncart = ["coffee", "cake"]\ntotal = 0\nfor m in cart:\n    total += menu[m]\nprint(f"합계 {total:,}원")\ncart = ["latte", "latte", "cake"]\ntotal = 0\nfor m in cart:\n    total += menu[m]\nprint(f"합계 {total:,}원")',
     'cart = ["coffee", "cake"]\nprint(len(cart))\nprint(sorted([6500, 4500, 5000]))\nprint(sum([4500, 6500]))',
     'def hello():\n    print("어서 오세요")\n\nhello()\nhello()'])

print("=== 2. 정의와 호출")
run(['def hello():\n    print("어서 오세요")\n    print("주문하시겠어요?")',
     'hello()',
     'print("가게 문 열어요")\nhello()\nprint("다음 손님")\nhello()'])

print("=== 3. 매개변수와 인자")
run(['def greet(name):\n    print(f"{name}님, 어서 오세요")\n\ngreet("kim")\ngreet("lee")',
     'def order(menu_name, qty):\n    print(f"{menu_name} {qty}잔 주문 받았어요")\n\norder("latte", 2)\norder("coffee", 1)',
     'order(2, "latte")'])

print("=== 4. return")
run(['def price_of(qty):\n    return 4500 * qty\n\nx = price_of(2)\nprint(x)\nprint(price_of(3) + 1000)',
     'def show(qty):\n    print(4500 * qty)\n\na = show(2)\nprint("a:", a)',
     'def calc(qty):\n    return 4500 * qty\n\nb = calc(2)\nprint("b:", b)\nprint(b + 1000)',
     'result = print("안녕")\nprint(result)\nprint(type(result))',
     'def check(stock):\n    if stock == 0:\n        return "품절"\n    return "주문 가능"\n\nprint(check(0))\nprint(check(3))',
     'def summary(prices):\n    return sum(prices), len(prices)\n\nprint(summary([4500, 5000, 6500]))\ntotal, n = summary([4500, 5000, 6500])\nprint(total, n)'])

print("=== 5. 오류와 함정")
run(['def hello():\n    print("어서 오세요")\n\nhello',
     'print(hello)',
     'def order(menu_name, qty):\n    print(f"{menu_name} {qty}잔 주문 받았어요")\n\norder("latte")',
     'order("latte", 2, "L")',
     'def calc(qty):\n    total = 4500 * qty\n    return total\n    print("계산 끝")\n\nprint(calc(2))',
     'def show(qty):\n    print(4500 * qty)\n\nshow(2) + 1000'])
run(['welcome()\n\ndef welcome():\n    print("어서 오세요")',
     'welcome()'])

print("=== 6. 실습")
run([MENU + '\n\ndef calc_total(cart, menu):\n    total = 0\n    for m in cart:\n        total += menu[m]\n    return total\n\ncart1 = ["coffee", "cake"]\ncart2 = ["latte", "latte", "cake"]\nprint(f"합계 {calc_total(cart1, menu):,}원")\nprint(f"합계 {calc_total(cart2, menu):,}원")',
     'def can_order(stock, name):\n    if stock[name] > 0:\n        return True\n    return False\n\nstock = {"coffee": 3, "latte": 0, "cake": 2}\nfor o in ["coffee", "latte", "cake"]:\n    if can_order(stock, o):\n        print(o, "주문 받았어요")\n    else:\n        print(o, "품절이에요")',
     'def grade(score):\n    if score >= 90:\n        return "A"\n    elif score >= 80:\n        return "B"\n    elif score >= 70:\n        return "C"\n    return "F"\n\nscores = [["kim", 92], ["lee", 78], ["park", 85], ["choi", 59]]\nfor name, score in scores:\n    print(f"{name:<5}{score:>3}  {grade(score)}")',
     'def discount_rate(total):\n    if total >= 20000:\n        return 10\n    elif total >= 10000:\n        return 5\n    return 0\n\ndef pay(total):\n    rate = discount_rate(total)\n    sale = total * rate // 100\n    return total - sale\n\nprint(pay(8000))\nprint(pay(15500))\nprint(pay(22000))'])
