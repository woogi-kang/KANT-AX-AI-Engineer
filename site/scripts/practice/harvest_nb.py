"""챕터의 tools/run_nb.py를 그대로 실행하면서 노트북 셀과 실제 출력을 모아 JSON으로 내보내요.
run_nb.py가 nbclient로 실제 커널을 돌리는 그 순간을 가로채기만 해요(셀과 출력은 바꾸지 않아요).
    python harvest_nb.py <챕터 폴더> [run_nb.py 인자...] > out.json
run_nb.py와 같은 일을 하는 ipykernel, nbclient, nbformat이 든 파이썬으로 실행해요."""
import contextlib, io, json, os, re, runpy, sys

import nbclient

chapter = os.path.abspath(sys.argv[1])
tools = os.path.join(chapter, "tools")
runs = []
title = [""]


class Tee(io.TextIOBase):
    def __init__(self, real):
        self.real = real

    def write(self, s):
        for line in s.split("\n"):
            if line.startswith("=== "):
                title[0] = line[4:].strip()
        return len(s)


orig = nbclient.NotebookClient.execute


def execute(self, *a, **k):
    r = orig(self, *a, **k)
    cells = []
    for c in self.nb.cells:
        if c.cell_type != "code":
            continue
        out, err = [], False
        for o in c.outputs:
            if o.output_type == "error":
                out.append(f"{o.ename}: {re.sub(r' [(]<?[^)]*line \d+[)]$', '', o.evalue)}")
                err = True
            else:
                text = o.get("text") or o.get("data", {}).get("text/plain", "")
                if not text and "image/png" in o.get("data", {}):
                    text = "[그림]"
                out += text.rstrip("\n").split("\n")
        cells.append({"src": c.source, "out": out, "err": err, "n": c.execution_count})
    runs.append({"title": title[0], "seed": os.environ.get("PYTHONHASHSEED"), "cells": cells})
    return r


nbclient.NotebookClient.execute = execute
sys.argv = [os.path.join(tools, "run_nb.py")] + sys.argv[2:]
sys.path.insert(0, tools)
os.chdir(os.environ.get("HARVEST_CWD", os.getcwd()))
with contextlib.redirect_stdout(Tee(sys.stdout)):
    runpy.run_path(os.path.join(tools, "run_nb.py"), run_name="__main__")
json.dump({"chapter": os.path.basename(chapter), "python": sys.version.split()[0], "runs": runs}, sys.stdout, ensure_ascii=False, indent=1)
