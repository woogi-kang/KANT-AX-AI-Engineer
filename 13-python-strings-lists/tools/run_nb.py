"""Runs every notebook cell in tools/cells.py with the project's own kernel and saves the outputs.
Used by tools/demo.sh. Each part is one fresh kernel, like opening the notebook and pressing Run All.
Writes tools/outputs.json: {cell id: {"n": execution count, "out": [lines], "err": bool}}."""
import json
import os
import re
import sys

import nbclient
import nbformat

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cells import PARTS

result = {}
for part, cells in PARTS.items():
    nb = nbformat.v4.new_notebook()
    nb.cells = [nbformat.v4.new_code_cell(src) for _, src in cells]
    nbclient.NotebookClient(nb, kernel_name="python3", allow_errors=True).execute()
    print(f"=== {part}")
    for (cid, src), c in zip(cells, nb.cells):
        out, err = [], False
        for o in c.outputs:
            if o.output_type == "error":
                # Only the last line of the Traceback, without the "(file, line N)" position note.
                out.append(f"{o.ename}: {re.sub(r' [(]<?[^)]*line \d+[)]$', '', o.evalue)}")
                err = True
            else:
                text = o.get("text") or o.get("data", {}).get("text/plain", "")
                out += text.rstrip("\n").split("\n")
        result[cid] = {"n": c.execution_count, "out": out, "err": err}
        print(f"--- [{c.execution_count}] {cid}")
        print("\n".join(out))

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs.json"), "w") as f:
    json.dump(result, f, ensure_ascii=False, indent=1)
