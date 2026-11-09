"""Runs one notebook cell with the project's kernel, then a shell command, then the same cell again in the
same kernel, like a student who sees ModuleNotFoundError, types the command in the terminal and re-runs.
Used by tools/demo.sh. Needs jupyter_client in the .venv (demo.sh installs it for the run, then removes it)."""
import subprocess, sys
from jupyter_client.manager import start_new_kernel

CELL = 'import requests\nprint("requests 버전:", requests.__version__)'
km, kc = start_new_kernel(kernel_name="python3")


def run(code):
    kc.execute(code)
    while True:
        m = kc.get_iopub_msg(timeout=60)
        t, c = m["msg_type"], m["content"]
        if t == "stream":
            print(c["text"], end="")
        elif t == "error":
            print(f'{c["ename"]}: {c["evalue"]}')
        elif t == "status" and c["execution_state"] == "idle":
            break


print("--- [1] before"); run(CELL)
print("--- $", sys.argv[1]); print(subprocess.run(sys.argv[1], shell=True, capture_output=True, text=True).stderr, end="")
print("--- [2] after"); run(CELL)
kc.stop_channels(); km.shutdown_kernel(now=True)
