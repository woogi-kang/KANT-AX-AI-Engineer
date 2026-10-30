"""Runs the notebook cells of the Jupyter part with the project's own kernel and prints each output.
Used by tools/demo.sh. Needs nbclient and nbformat in the .venv (demo.sh installs them in a copy)."""
import nbclient
import nbformat

CELLS = ['print("안녕하세요")', "import sys\nprint(sys.executable)", "import fastapi\nprint(fastapi.__version__)", "1 + 2"]
nb = nbformat.v4.new_notebook()
nb.cells = [nbformat.v4.new_code_cell(c) for c in CELLS]
nbclient.NotebookClient(nb, kernel_name="python3").execute()
for i, c in enumerate(nb.cells, 1):
    print(f"--- [{i}] {c.source!r}")
    for o in c.outputs:
        print(o.get("text") or o.get("data", {}).get("text/plain"))
