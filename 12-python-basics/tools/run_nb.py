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


print("=== 0. 왜 필요한가")
run(['print(4500 * 2 + 5000)', 'print(20000 - (4500 * 2 + 5000))'])
print("=== 1. 변수 할당")
run(['age = 25', 'age', 'print(age)\nprint("나이:", age)', 'age = 26\nage', 'age = age + 1\nage',
     'user_name = "kim"\nage\nuser_name', 'print(age)\nprint(user_name)', 'Age'])
print("=== 2. 변수 타입")
run(['age = 25\nheight = 172.5\nuser_name = "kim"\nis_member = False\nprint(type(age))\nprint(type(height))\nprint(type(user_name))\nprint(type(is_member))',
     'x = 10\nprint(type(x))\nx = "ten"\nprint(type(x))',
     'print(type(25))\nprint(type("25"))\nprint(25 + 1)\nprint("25" + "1")',
     'print(int("3") + 3)\nprint(str(3) + "3")\nprint(float("3.5"))\nprint(int(3.9))',
     'int("삼")', 'int("3.5")', 'print(type(7 + 3))\nprint(type(7 + 0.5))\nprint(type(6 / 2))'])
print("=== 3. 사칙연산")
run(['print(7 + 3)\nprint(7 - 3)\nprint(7 * 3)\nprint(7 / 3)\nprint(6 / 2)',
     'print(7 // 3)\nprint(7 % 3)\nprint(2 ** 3)', '2 + 3 * 4', '(2 + 3) * 4',
     'print(2 ** 3 // 3)\nprint(2 * 3 ** 2)\nprint(-2 ** 2)\nprint((-2) ** 2)', 'print(10 - 4 + 2)\nprint(8 / 2 * 4)\nprint(7 // 2 * 2)',
     'print(10 - 2 * 3 ** 2 // 4)',
     'print(10 + 2 * 3)\nprint((10 + 2) * 3)\nprint(20 - 10 / 2)\nprint((20 - 10) / 2)\nprint(12 / 3 * 2)\nprint(12 / (3 * 2))\nprint(100 - 30 - 20)\nprint(100 - (30 - 20))', 'print(2 ** 2 * 3)\nprint(2 ** (2 * 3))\nprint(17 % 5 * 2)\nprint(17 % (5 * 2))\nprint(3 + 10 // 3)\nprint((3 + 10) // 3)\nprint(-3 ** 2)\nprint((-3) ** 2)', 'print(7 // 2 ** 2)\nprint(10 % 3 ** 2)\nprint(2 + 3 * 4 ** 2 // 8)\nprint(50 - 5 * 2 ** 3 % 7)',
     'score = 0\nscore += 10\nscore += 5\nscore',
     '"kim" + "lee"', '"ha" * 3', '"3" + "3"', '"3" + 3', '10 / 0'])
run(['2 ** 3 ** 2'])
print("=== 4. 비교와 논리연산")
run(['age = 25\nprint(age > 20)\nprint(age < 20)\nprint(age == 25)\nprint(age != 25)\nprint(age >= 25)\nprint(age <= 24)',
     'age == 30', 'age = 30\nage', 'age = 25\nis_adult = age >= 20\nprint(is_adult)\nprint(type(is_adult))',
     'print(True and True)\nprint(True and False)\nprint(False and True)\nprint(False and False)',
     'print(True or True)\nprint(True or False)\nprint(False or True)\nprint(False or False)',
     'print(not True)\nprint(not False)',
     'height = 130\nage = 9\nheight >= 120 and age >= 7', 'height = 110\nheight >= 120 and age >= 7',
     '2 + 3 > 4 and not False', 'age = 25\nage >= 20 and age < 30', 'is_member = true'])
print("=== 5. 실제 상황 예제")
run(['americano = 4500\nlatte = 5000\ntotal = americano * 2 + latte\npaid = 20000\nprint("합계:", total)\nprint("잔돈:", paid - total)',
     'americano = 4800\ntotal = americano * 2 + latte\nprint("합계:", total)\nprint("잔돈:", paid - total)',
     'qty = "3"\ntotal = 4500 * int(qty) + 5000\npeople = 3\nprint("합계:", total)\nprint("한 사람:", total // people)\nprint("남는 돈:", total % people)',
     'qty = "3"\nprint(5000 + qty)',
     'is_member = False\nhas_coupon = True\ntotal = 18500\nsize_up = total >= 15000 and has_coupon\ndiscount = is_member or total >= 50000\nprint("사이즈 업:", size_up)\nprint("할인:", discount)\nprint("비회원:", not is_member)'])
