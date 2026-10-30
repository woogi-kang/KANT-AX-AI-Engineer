"""Runs the notebook cells shown in the deck with the project's own kernel and prints each output.
Used by tools/demo.sh. Restart is a new kernel, like the Restart button in VS Code."""
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


print("=== 처음 실행")
run(['x = 10', 'print(x * 2)', 'name = "kim"\nname', 'x = x + 1\nx', 'x = x + 1\nx'])
print("=== Restart 뒤 2번 셀만 실행")
run(['print(x * 2)'])
print("=== 마크다운 글을 코드 셀에 적었을 때")
run(['오늘 배운 것'])
print("=== 변수 이름 규칙을 어긴 셀")
run(['1st_name = "kim"', 'my name = "kim"', 'my-name = "kim"', 'class = "kim"'])
print("=== 자료형")
run(['# 정수형 자료형\nage = 25\n\n# 실수 자료형\npi = 3.14\n\n# 불리언 자료형(Boolean)\nis_alive = True\n\n# 문자열 자료형\nuser_name = "kim"\n\n# 리스트 (다른 언어의 배열과 비슷해요)\ngrade_type = [1, 2, 3, 4, 5]',
     'print(type(age))\nprint(type(pi))\nprint(type(is_alive))\nprint(type(user_name))\nprint(type(grade_type))'])
