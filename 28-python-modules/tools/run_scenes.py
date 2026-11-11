"""Runs each scene of scenes.py in a fresh copy of the uv project at ROOT/shopping-cart and saves the outputs.
Usage (from demo.sh): python3 -I run_scenes.py ROOT OUT.json"""
import json, os, shutil, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scenes import SCENES, PRODUCT, CART  # noqa: E402

root, out_path = sys.argv[1], sys.argv[2]
base, proj = os.path.join(root, "base"), os.path.join(root, "shopping-cart")
out = {}
for name, sc in SCENES.items():
    shutil.rmtree(proj, ignore_errors=True)
    shutil.copytree(base, proj, symlinks=True)
    files = {"product.py": PRODUCT, "cart.py": CART, **sc["files"]}
    for f, text in files.items():
        with open(os.path.join(proj, f), "w") as fh:
            fh.write(text)
    runs = []
    for cmd in sc["cmds"]:
        r = subprocess.run(cmd, shell=True, cwd=proj, capture_output=True, text=True)
        text = (r.stdout + r.stderr).rstrip("\n")
        runs.append({"cmd": cmd, "out": text.split("\n") if text else []})
        print(f"=== {name}\n$ {cmd}\n{text}\n")
    out[name] = runs
with open(out_path, "w") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
