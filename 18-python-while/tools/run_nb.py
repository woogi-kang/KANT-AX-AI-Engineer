"""Runs the notebook cells shown in the deck with the project's own kernel and prints each output.
Used by tools/demo.sh. Each run() is one fresh kernel, like opening the notebook and pressing Run All.
The infinite loop cell is stopped after one second, like pressing the stop button in VS Code."""
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


MENUS = 'menus = ["coffee", "latte", "cake"]'
STOCK = 'stock = {"coffee": 3, "latte": 0, "cake": 2, "tea": 0}'

print("=== 1. 왜 필요한가")
run(['money = 10000\nfor cup in [1, 2, 3]:\n    money -= 4500\n    print(f"{cup}잔째, 남은 돈 {money}원")',
     'money = 10000\ncups = 0\nwhile money >= 4500:\n    money -= 4500\n    cups += 1\nprint(f"{cups}잔, 남은 돈 {money}원")'])

print("=== 2. range와 번호")
run(['print(range(5))\nprint(list(range(5)))\nprint(len(range(5)))',
     'print(list(range(1, 6)))\nprint(list(range(0, 10, 2)))\nprint(list(range(5, 0, -1)))\nprint(list(range(3, 3)))',
     'for i in range(3):\n    print("주문", i)\nfor i in range(1, 4):\n    print(f"{i}번 손님")',
     MENUS + '\nfor i in range(len(menus)):\n    print(i, menus[i])',
     'i = 0\nfor m in menus:\n    print(i, m)\n    i += 1',
     'for i, m in enumerate(menus):\n    print(i, m)\nfor i, m in enumerate(menus, 1):\n    print(f"{i}. {m}")',
     'print(list(enumerate(menus)))'])

print("=== 3. while")
run(['count = 1\nwhile count <= 3:\n    print(f"{count}번째")\n    count += 1\nprint("끝, count는", count)',
     'stock = 3\nwhile stock > 0:\n    stock -= 1\n    print(f"주문 받았어요. 남은 재고 {stock}")\nprint("품절이에요")',
     'stock = 0\nwhile stock > 0:\n    stock -= 1\n    print("주문 받았어요")\nprint("품절이에요")',
     'for i in range(1, 4):\n    print(i)\ni = 1\nwhile i <= 3:\n    print(i)\n    i += 1'])
run(['count = 1\nwhile count <= 3:\n    print(count)'], timeout=1)

print("=== 4. break와 continue")
ORD = 'orders = ["coffee", "cake", "latte", "tea", "cake"]\nsoldout = ["latte"]'
run([ORD + '\nfor o in orders:\n    if o in soldout:\n        print(f"{o} 품절, 주문을 멈춰요")\n        break\n    print(f"{o} 주문 받았어요")\nprint("끝")',
     'for o in orders:\n    if o in soldout:\n        print(f"{o} 품절, 건너뛰어요")\n        continue\n    print(f"{o} 주문 받았어요")\nprint("끝")',
     'for i in range(1, 6):\n    if i == 3:\n        break\n    print(i)\nprint("---")\nfor i in range(1, 6):\n    if i == 3:\n        continue\n    print(i)',
     'for o in orders:\n    if o in soldout:\n        print(f"{o} 품절, 건너뛰어요")\n    else:\n        print(f"{o} 주문 받았어요")\nprint("끝")',
     'left = 3\nn = 0\nwhile True:\n    if left == 0:\n        print("재고가 떨어졌어요")\n        break\n    left -= 1\n    n += 1\n    print(f"{n}번째 주문, 남은 재고 {left}")'])

print("=== 5. 누적과 중첩")
run(['prices = [4500, 5000, 6500, 4500]\ntotal = 0\nfor p in prices:\n    total += p\nprint(total)\nprint(sum(prices))',
     'n = 0\nfor p in prices:\n    if p >= 5000:\n        n += 1\nprint(n)\nprint(prices.count(4500))',
     'big = prices[0]\nfor p in prices:\n    if p > big:\n        big = p\nprint(big)\nprint(max(prices), min(prices))',
     'big = []\nfor p in prices:\n    if p >= 5000:\n        big.append(p)\nprint(big)\nprint(len(big))',
     'for dan in range(2, 4):\n    for i in range(1, 4):\n        print(f"{dan} x {i} = {dan * i}")\n    print("---")',
     'scores = [[90, 85, 77],\n          [70, 95, 88],\n          [60, 75, 99]]\nfor i in range(len(scores)):\n    for j in range(len(scores[i])):\n        if scores[i][j] < 70:\n            print(f"{i}행 {j}열: {scores[i][j]}점")',
     'for row in scores:\n    for s in row:\n        if s < 80:\n            print("80점 아래", s, "찾음")\n            break\n    print("이 행 확인 끝", row)'])

print("=== 6. 함정과 실습")
run(['orders = ["tea", "tea", "coffee", "tea", "cake"]\nfor o in orders:\n    if o == "tea":\n        orders.remove(o)\nprint(orders)',
     'orders = ["tea", "tea", "coffee", "tea", "cake"]\nkeep = []\nfor o in orders:\n    if o != "tea":\n        keep.append(o)\nprint(keep)',
     'total = 0\nfor p in [4500, 5000, 6500]:\n    total += p\n    print(total)',
     'total = 0\nfor p in [4500, 5000, 6500]:\n    total += p\nprint(total)',
     'for p in [4500, 5000, 6500]:\n    total = 0\n    total += p\nprint(total)',
     MENUS + '\nfor i in range(len(menus) + 1):\n    print(menus[i])',
     'print(list(range(1, 5)))\nprint(list(range(len(menus))))'])
run(['stock = 5\norders = [2, 1, 3, 1]\nsold = 0\ni = 0\nwhile i < len(orders):\n    want = orders[i]\n    if want > stock:\n        print(f"{i + 1}번 손님 {want}잔: 재고가 {stock}잔뿐이에요")\n        break\n    stock -= want\n    sold += want\n    print(f"{i + 1}번 손님 {want}잔, 남은 재고 {stock}")\n    i += 1\nprint(f"판매 {sold}잔, 남은 재고 {stock}")',
     'stock = {"coffee": 2, "latte": 1, "cake": 3}\norders = ["coffee", "latte", "coffee", "latte", "cake"]\nfor o in orders:\n    if stock[o] == 0:\n        print(f"{o} 품절이에요. 주문을 멈춰요")\n        break\n    stock[o] -= 1\n    print(f"{o} 나갔어요. 남은 수 {stock[o]}")\nprint(stock)',
     'for dan in range(2, 10):\n    print(f"{dan}단", end=" ")\n    for i in range(1, 10):\n        print(f"{dan * i:>3}", end="")\n    print()',
     'answer = 37\nguesses = [50, 25, 37, 40]\ntries = 0\nfor g in guesses:\n    tries += 1\n    if g == answer:\n        print(f"{g}: 정답이에요. {tries}번 만에 맞혔어요")\n        break\n    elif g > answer:\n        print(f"{g}: 더 작아요")\n    else:\n        print(f"{g}: 더 커요")'])
