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


print("=== 1. 문자열과 출력")
run(['a = \'kim\'\nb = "kim"\nprint(a == b)\nprint(len("hello"))\nprint("It\'s me")',
     'word = "python"\nprint(word[0])\nprint(word[1])\nprint(word[-1])', 'word[0:2]', 'print(word[2:5])\nprint(word[:2])\nprint(word[2:])', 'word[6]',
     'print("kim", "lee")\nprint("kim", "lee", sep="-")\nprint("2026", "11", "02", sep=".")\nprint("hello", end=" ")\nprint("world")',
     'print("첫째 줄\\n둘째 줄")\nprint("이름\\tkim")\nprint("경로: C:\\\\Users")',
     'name = "kim"\nage = 25\nprint("%s 님은 %d살이에요" % (name, age))\nprint("{} 님은 {}살이에요".format(name, age))\nprint(f"{name} 님은 {age}살이에요")',
     'print("이름: %s" % name)\nprint("나이: %d살" % age)', 'print(f"이름: {name}")\nprint(f"나이: {age}살")\nprint(f"내년: {age + 1}살")',
     'cake = "치즈케이크"\nprice = 5000\nqty = 2\nprint("주문내역은 : {0}, {1}, {2}".format(cake, price, qty))\nprint("주문내역은 : {}, {}, {}".format(cake, price, qty))\nprint("{0} {2}개, 하나에 {1}원".format(cake, price, qty))\nprint("{0}, {0}, {0}".format(cake))',
     'print("주문내역은 : %s, %d, %d" % (cake, price, qty))\nprint("주문내역은 : {0}, {1}, {2}".format(cake, price, qty))\nprint(f"주문내역은 : {cake}, {price}, {qty}")\nprint(f"{cake} {qty}개, 하나에 {price}원")\nprint(f"{cake} {qty}개, 합계 {price * qty:,}원")',
     'print("[%5d]" % 42)\nprint("[%-5d]" % 42)\nprint("[%05d]" % 42)\nprint("[%5s]" % "kim")',
     'print(f"[{42:5d}]")\nprint(f"[{42:<5d}]")\nprint(f"[{42:05d}]")\nprint(f"[{\'kim\':>5}]")\nprint(f"[{\'kim\':5}]")',
     'pi = 3.141592\nprint("%f" % pi)\nprint("%.2f" % pi)\nprint("%0.2f" % pi)\nprint("%.4f" % pi)\nprint("[%8.2f]" % pi)',
     'print(f"{pi}")\nprint(f"{pi:.2f}")\nprint(f"{pi:0.2f}")\nprint(f"{pi:.4f}")\nprint(f"[{pi:8.2f}]")',
     'price = 1234567\nprint(f"{price:,}")\nprint(f"{price:,}원")\nprint(f"{1234567.891:,.2f}")\nfee = 35000\nprint(f"[{fee:8,}]")',
     'print("%,d" % price)',
     'price = 5000\nprint("[{0:5d}]".format(qty))\nprint("{0:.2f}".format(3.141592))\nprint("{0:,}원".format(1234567))\nprint("{0}: {1:,}원 x {2}개".format(cake, price, qty))',
     'print("%-6s %5d" % ("kim", 90))\nprint("%-6s %5d" % ("lee", 100))\nprint("%-6s %5d" % ("park", 7))\nprint("할인 %d%%" % 30)',
     'print(f"{\'kim\':<6} {90:5d}")\nprint(f"{\'lee\':<6} {100:5d}")\nprint(f"{\'park\':<6} {7:5d}")\nprint(f"할인 {30}%")',
     '"%d살" % "kim"', '"%s 님은 %d살" % name', '"%s" % (name, age)', 'f"{name:d}"'])

print("=== 2. 리스트와 튜플")
run(['prices = [4500, 5000, 6500]\nprint(prices)\nprint(len(prices))\nprint(type(prices))',
     'menus = ["coffee", "latte", "cake"]\nprint(menus[0])\nprint(menus[-1])\nprint(menus[0:2])',
     'prices[0] = 4800\nprices.append(3000)\nprint(prices)\nprint(sum(prices))\nprint(max(prices))\nprint(min(prices))',
     'cart = ["coffee", "latte"]\ncart.append("cake")\ncart.insert(0, "tea")\ncart.remove("latte")\nprint(cart)\nlast = cart.pop()\nfirst = cart.pop(0)\nprint(last, first)\nprint(cart)',
     'cart.remove("juice")',
     'scores = [70, 95, 80, 95]\nprint(scores.count(95))\nprint(scores.index(80))\nprint(95 in scores)\nscores.sort()\nprint(scores)\nscores.sort(reverse=True)\nprint(scores)',
     'nums = [10, 20, 30, 40, 50, 60]\nprint(nums[1:4])\nprint(nums[:3])\nprint(nums[3:])\nprint(nums[-2:])\nprint(nums[::2])\nprint(nums[1::2])\nprint(nums[::-1])',
     'table = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]\nprint(table[1])\nprint(table[1][2])\nprint(table[-1][-1])\nprint(table[0][:2])\nprint(menus[0][0])\nprint(menus[1][-3:])',
     'a = [3, 1, 2]\nb = [5, 4]\nprint(a + b, a * 2)\na.extend(b)\nprint(a)\nprint(sorted(a), a)\na.reverse()\nprint(a)\nc = a.copy()\nc.clear()\nprint(a, c)',
     'text = "coffee,latte,cake"\nwords = text.split(",")\nprint(words)\nprint(len(words))\nprint(" / ".join(words))\nprint("hello world".split())\nprint(list("abc"))',
     'order = ("coffee", 4500, 2)\nprint(order[0])\nprint(order[1] * order[2])\nprint(type(order))',
     'order[1] = 5000',
     'date = (2026, 11, 2)\nprint(date.count(2))\nprint(date.index(11))\nyear, month, day = date\nprint(year, month, day)\na = "kim"\nb = "lee"\na, b = b, a\nprint(a, b)\nprint(list(date))\nprint(tuple(menus))',
     't = (10, 20, 30, 40)\nprint(t[1:3])\nprint(t[::-1])\nprint(t + (50,))\nprint(len(t), sum(t), max(t))\nprint(30 in t)\ninfo = ("kim", (2026, 11, 2))\nprint(info[1][0])',
     'orders = [("coffee", 4500, 2), ("latte", 5000, 1), ("cake", 6500, 3)]\nprint(len(orders))\nprint(orders[1])\nprint(orders[1][0])\nprint(orders[2][1] * orders[2][2])\nprint(orders[0:2])',
     'menu, price, qty = orders[2]\nprint(menu, price, qty)\nprint(f"{menu} {qty}개, {price * qty:,}원")',
     'print(f"{orders[0][0]:<7}{orders[0][1]:>6,}원 {orders[0][2]:>2}개")\nprint(f"{orders[1][0]:<7}{orders[1][1]:>6,}원 {orders[1][2]:>2}개")\nprint(f"{orders[2][0]:<7}{orders[2][1]:>6,}원 {orders[2][2]:>2}개")\ntotal = orders[0][1] * orders[0][2]\ntotal += orders[1][1] * orders[1][2]\ntotal += orders[2][1] * orders[2][2]\nprint(f"합계 {total:,}원")',
     'print(f"{\'메뉴명\':<10}{\'단가\':>8}{\'수량\':>5}{\'금액\':>10}")\nprint(f"{\'menu\':<10}{\'price\':>8}{\'qty\':>5}{\'amount\':>10}")\nprint(f"{orders[0][0]:<10}{orders[0][1]:>8,}{orders[0][2]:>5}{orders[0][1] * orders[0][2]:>10,}")',
     'print("=" * 33)\nprint(f"{\'메뉴명\':<7}{\'단가\':>6}{\'수량\':>3}{\'금액\':>8}")\nprint("-" * 33)\nprint(f"{orders[0][0]:<10}{orders[0][1]:>8,}{orders[0][2]:>5}{orders[0][1] * orders[0][2]:>10,}")\nprint(f"{orders[1][0]:<10}{orders[1][1]:>8,}{orders[1][2]:>5}{orders[1][1] * orders[1][2]:>10,}")\nprint(f"{orders[2][0]:<10}{orders[2][1]:>8,}{orders[2][2]:>5}{orders[2][1] * orders[2][2]:>10,}")\nprint("-" * 33)\nprint(f"{\'합계\':<6}{total:>25,}")\nprint("=" * 33)',
     'for menu in menus:\n    print(menu)',
     'for menu, price, qty in orders:\n    print(menu, price, qty)',
     'total = 0\nfor menu, price, qty in orders:\n    total += price * qty\n    print(menu, total)\nprint("합계:", total)',
     'print("=" * 33)\nprint(f"{\'KANT 카페\':^31}")\nprint(f"{\'2026-11-02  14:30\':^33}")\nprint("=" * 33)\nprint(f"{\'메뉴명\':<7}{\'단가\':>6}{\'수량\':>3}{\'금액\':>8}")\nprint("-" * 33)\ntotal = 0\ncount = 0\nfor menu, price, qty in orders:\n    print(f"{menu:<10}{price:>8,}{qty:>5}{price * qty:>10,}")\n    total += price * qty\n    count += qty\nprint("-" * 33)\nprint(f"{\'수량\':<6}{count:>15}")\nprint(f"{\'합계\':<6}{total:>25,}")\nprint("=" * 33)\nprint(f"{\'감사합니다\':^28}")',
     'for menu in menus\n    print(menu)', 'for menu in menus:\nprint(menu)',
     'names = ["kim", "lee", "park"]\nscores = [90, 100, 7]\nmixed = ["coffee", 4500, True]\ncarts = [["coffee", "cake"], ["latte"]]\nempty = []\nprint(scores[1])\nprint(mixed)\nprint(carts[0][1])\nprint(len(empty))',
     'menus[3]', 'orders[3]', 'orders[0][3]'])
