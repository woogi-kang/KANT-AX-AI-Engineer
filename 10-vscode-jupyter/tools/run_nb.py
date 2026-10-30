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
run(['x = 10', 'print(x * 2)', 'name = "kim"\nf"안녕하세요, {name}"', 'x = x + 1\nx', 'x = x + 1\nx'])
print("=== Restart 뒤 2번 셀만 실행")
run(['print(x * 2)'])
print("=== 마크다운 글을 코드 셀에 적었을 때")
run(['오늘 배운 것'])
print("=== 변수 이름 규칙을 어긴 셀")
run(['1st_name = "kim"', 'my name = "kim"', 'my-name = "kim"', 'class = "kim"'])
