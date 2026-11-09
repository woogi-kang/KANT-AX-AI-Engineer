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


print("=== 1. in과 not in")
P1 = ['menu = ["coffee", "latte", "cake"]\nprint(menu.count("juice"))\nmenu.index("juice")',
 'print("latte" in menu)\nprint("juice" in menu)\nprint("juice" not in menu)\nprint("latte" not in menu)',
 'order = ("coffee", 4500, 2)\nprint(4500 in order)\nprint("4500" in order)',
 'word = "python"\nprint("th" in word)\nprint("pt" in word)\nprint("P" in word)',
 'has_both = "latte" in menu and "cake" in menu\nprint(has_both)\nprint("juice" in menu or "tea" in menu)\nprint(not "juice" in menu)',
 'orders = [("coffee", 4500, 2), ("latte", 5000, 1), ("cake", 6500, 3)]\nprint(("cake", 6500, 3) in orders)\nprint("cake" in orders)\nprint("cake" in orders[2])',
 '3 in word']
P2 = ['kim = [90, 85, 77]\nlee = [70, 95, 88]\npark = [60, 75, 99]\nprint(sum(kim) + sum(lee) + sum(park))',
 'scores = [[90, 85, 77],\n          [70, 95, 88],\n          [60, 75, 99]]\nprint(scores)\nprint(len(scores))\nprint(len(scores[0]))',
 'print(scores[1])\nprint(scores[1][2])\nprint(scores[0][0])\nprint(scores[-1][-1])',
 'scores[0][1] = 100\nprint(scores[0])\nscores[2] = [65, 80, 90]\nprint(scores)',
 'for row in scores:\n    print(row, "합계:", sum(row), "최고:", max(row))',
 'eng = []\nfor row in scores:\n    eng.append(row[1])\nprint(eng)\nprint("영어 합계:", sum(eng))',
 'total = 0\ncount = 0\nfor row in scores:\n    total += sum(row)\n    count += len(row)\nprint("전체 합계:", total)\nprint("칸 수:", count)\nprint(f"평균: {total / count:.1f}")',
 'print(scores[:2])\nprint(scores[1][:2])\nprint(scores[0][::-1])',
 'print(95 in scores)\nprint(95 in scores[1])\nprint([70, 95, 88] in scores)\nfor row in scores:\n    print(row, 100 in row)',
 'scores.append([80, 70, 60])\nprint(len(scores))\nfor row in scores:\n    row.append(0)\nfor row in scores:\n    print(row)',
 'board = [[0] * 3] * 3\nboard[0][0] = 9\nprint(board)',
 'board = [[0, 0, 0],\n         [0, 0, 0],\n         [0, 0, 0]]\nboard[0][0] = 9\nprint(board)',
 'scores[5][0]', 'scores[0][9]', 'kor, eng, math = scores[0]']
P3 = ['students = [["kim", 90, 85, 77],\n            ["lee", 70, 95, 88],\n            ["park", 60, 75, 99]]\nprint(f"{\'name\':<6}{\'kor\':>5}{\'eng\':>5}{\'math\':>5}")\nprint("-" * 21)\nfor name, kor, eng, math in students:\n    print(f"{name:<6}{kor:>5}{eng:>5}{math:>5}")',
 'seats = [["O", "O", "X", "O"],\n         ["X", "O", "O", "O"],\n         ["O", "X", "X", "O"]]\nseats[0][1] = "X"\nfor row in seats:\n    print(" ".join(row))\nprint(seats[2].count("X"))\nprint(len(seats) * len(seats[0]))',
 'menu = ["coffee", "latte", "cake"]\nsales = [[12, 8, 5],\n         [10, 9, 7],\n         [15, 11, 4]]\nfor row in sales:\n    print(row, "하루 합계:", sum(row))\ncol = menu.index("latte")\nlatte = []\nfor row in sales:\n    latte.append(row[col])\nprint("latte:", latte, "합계:", sum(latte))']
run(P1)
print("=== 2. 2차원 리스트")
run(P2)
print("=== 3. 실제로 써 보기")
run(P3)
