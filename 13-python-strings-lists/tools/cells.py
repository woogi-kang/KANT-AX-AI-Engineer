"""Every notebook cell shown in the deck, in slide order. One list per part: each part runs in a fresh kernel.
tools/run_nb.py runs them with the hello-uv kernel and writes tools/outputs.json; tools/gen.py reads both."""

ORDERS = 'orders = [("coffee", 4500, 2), ("latte", 5000, 1), ("cake", 6500, 3)]'

PARTS = {
    # 들어가기: 12에서 배운 것만으로 주문 세 건을 찍어 봐요.
    "intro": [
        ("why", 'print("coffee", 4500, 2, 4500 * 2)\nprint("latte", 5000, 1, 5000 * 1)\nprint("cake", 6500, 3, 6500 * 3)\nprint("합계", 4500 * 2 + 5000 * 1 + 6500 * 3)'),
    ],
    "strings": [
        ("str-make", 'a = \'kim\'\nb = "kim"\nprint(a == b)\nprint(len("hello"))\nprint("It\'s me")'),
        ("str-index", 'word = "python"\nprint(word[0])\nprint(word[1])\nprint(word[-1])'),
        ("str-index-err", 'word[6]'),
        ("str-slice", 'print(word[0:2])\nprint(word[2:5])\nprint(word[:2])\nprint(word[2:])'),
        ("print-sep", 'print("kim", "lee")\nprint("kim", "lee", sep="-")\nprint("2026", "11", "02", sep=".")\nprint("hello", end=" ")\nprint("world")\nprint("첫째 줄\\n둘째 줄")\nprint("이름\\tkim")'),
        ("fmt-ways", 'cake = "치즈케이크"\nprice = 5000\nqty = 2\nprint("주문: %s %d개" % (cake, qty))\nprint("주문: {} {}개".format(cake, qty))\nprint(f"주문: {cake} {qty}개")'),
        ("fmt-sd", 'print("%s %d개" % (cake, qty))\nprint(f"{cake} {qty}개")\nprint(f"{cake} {qty + 1}개")'),
        ("fmt-format", 'print("{0} {1}원 {2}개".format(cake, price, qty))\nprint("{0} {2}개, 하나에 {1}원".format(cake, price, qty))\nprint("{0}, {0}".format(cake))'),
        ("fmt-width", 'print("[%5d]" % 42)\nprint(f"[{42:5d}]")\nprint(f"[{42:<5d}]")\nprint(f"[{42:05d}]")\nprint(f"[{\'kim\':5}]")\nprint(f"[{\'kim\':>5}]")'),
        ("fmt-float", 'pi = 3.141592\nprint("%.2f" % pi)\nprint(f"{pi:.2f}")\nprint(f"{pi:.4f}")\nprint(f"[{pi:8.2f}]")'),
        ("fmt-comma", 'price = 1234567\nprint(f"{price:,}원")\nprint(f"{1234567.891:,.2f}")\nfee = 35000\nprint(f"[{fee:8,}]")\nprint(f"{cake} {qty}개, 합계 {5000 * qty:,}원")'),
        ("fmt-align", 'print(f"{\'kim\':<6}{90:>5}")\nprint(f"{\'lee\':<6}{100:>5}")\nprint(f"{\'park\':<6}{7:>5}")\nprint("%-6s%5d" % ("park", 7))'),
        ("fmt-compare", 'print("[{0:5d}]".format(42))\nprint("{0:.2f}".format(pi))\nprint("{0:,}원".format(price))'),
        ("fmt-err1", '"%d개" % "kim"'),
        ("fmt-err2", '"%s %d개" % cake'),
        ("fmt-err3", 'f"{cake:d}"'),
        ("fmt-err4", '"%,d" % price'),
    ],
    "lists": [
        ("list-make", 'prices = [4500, 5000, 6500]\nprint(prices)\nprint(len(prices))\nprint(type(prices))'),
        ("list-index", 'menus = ["coffee", "latte", "cake"]\nprint(menus[0])\nprint(menus[-1])\nprint(menus[0:2])'),
        ("list-change", 'prices[0] = 4800\nprices.append(3000)\nprint(prices)\nprint(sum(prices))\nprint(max(prices))\nprint(min(prices))'),
        ("list-methods", 'cart = ["coffee", "latte"]\ncart.append("cake")\ncart.insert(0, "tea")\ncart.remove("latte")\nlast = cart.pop()\nfirst = cart.pop(0)\nprint(cart, last, first)'),
        ("list-find", 'scores = [70, 95, 80, 95]\nprint(scores.count(95))\nprint(scores.index(80))\nprint(95 in scores)\nscores.sort()\nprint(scores)\nscores.sort(reverse=True)\nprint(scores)'),
        ("list-slice", 'nums = [10, 20, 30, 40, 50, 60]\nprint(nums[1:4])\nprint(nums[:3])\nprint(nums[-2:])\nprint(nums[::2])\nprint(nums[::-1])'),
        ("list-nested", 'table = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]\nprint(table[1])\nprint(table[1][2])\nprint(table[-1][-1])\nprint(menus[0][0])\nmixed = ["coffee", 4500, True]\nprint(mixed)'),
        ("list-more", 'a = [3, 1, 2]\nb = [5, 4]\nprint(a + b, a * 2)\nprint(sorted(a), a)\na.extend(b)\na.reverse()\nc = a.copy()\nc.clear()\nprint(a, c)'),
        ("list-str", 'text = "coffee,latte,cake"\nwords = text.split(",")\nprint(words)\nprint(" / ".join(words))\nprint("hello world".split())\nprint(list("abc"))'),
        ("list-compare", 'names = ["kim", "lee"]\nnames[0] = "park"\nprint(names)\nword = "python"\nword[0] = "P"'),
        ("tuple", 'order = ("coffee", 4500, 2)\nprint(order[0])\nprint(order[1] * order[2])\nprint(order[1:])\nprint(type(order))'),
        ("tuple-err", 'order[1] = 5000'),
        ("orders", ORDERS + '\nprint(len(orders))\nprint(orders[1])\nprint(orders[1][0])\nprint(orders[2][1] * orders[2][2])'),
        ("tuple-more", 'menu, price, qty = orders[2]\nprint(menu, price, qty)\na, b = "kim", "lee"\na, b = b, a\nprint(a, b)\nprint(order.count(4500), order.index(2))\nprint(list(order))'),
        ("for-intro", 'for menu in menus:\n    print(menu)'),
        ("for-orders", 'for menu, price, qty in orders:\n    print(menu, price, qty)'),
        ("for-total", 'total = 0\nfor menu, price, qty in orders:\n    total += price * qty\n    print(menu, total)\nprint("합계:", total)'),
        ("list-err1", 'menus[3]'),
        ("list-err2", 'orders[0][3]'),
        ("list-err3", 'cart.remove("juice")'),
        ("for-err1", 'for menu in menus\n    print(menu)'),
        ("for-err2", 'for menu in menus:\nprint(menu)'),
    ],
    "examples": [
        ("ex-line", ORDERS + '\nmenu, price, qty = orders[0]\nprint(f"{\'menu\':<10}{\'price\':>8}{\'qty\':>5}{\'amount\':>10}")\nprint(f"{\'메뉴명\':<10}{\'단가\':>8}{\'수량\':>5}{\'금액\':>10}")\nprint(f"{\'메뉴명\':<7}{\'단가\':>6}{\'수량\':>3}{\'금액\':>8}")\nprint(f"{menu:<10}{price:>8,}{qty:>5}{price * qty:>10,}")'),
        ("ex-receipt", 'print("=" * 33)\nprint(f"{\'KANT 카페\':^31}")\nprint("=" * 33)\nprint(f"{\'메뉴명\':<7}{\'단가\':>6}{\'수량\':>3}{\'금액\':>8}")\nprint("-" * 33)\ntotal = 0\nfor menu, price, qty in orders:\n    print(f"{menu:<10}{price:>8,}{qty:>5}{price * qty:>10,}")\n    total += price * qty\nprint("-" * 33)\nprint(f"{\'합계\':<6}{total:>25,}")\nprint("=" * 33)'),
        ("ex-memo", 'memo = "latte,cake,latte,coffee,latte"\nitems = memo.split(",")\nitems.remove("coffee")\nitems.append("tea")\nprint(f"주문 {len(items)}건, latte {items.count(\'latte\')}잔")\nitems.sort()\nprint(" / ".join(items))'),
    ],
}
