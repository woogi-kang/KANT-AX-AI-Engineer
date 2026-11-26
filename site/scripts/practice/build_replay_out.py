"""챕터 도구가 실제로 실행해 남긴 출력 파일에서 재생형 practice.json을 만들어요.
    python3 build_replay_out.py 35-docker-cli
- tools/out.json (30~35, 44의 demo.py): 장면 이름 → [{cmd, cwd, out}]
- tools/demo-output.txt (11, 29의 demo.sh): "### 이름" 또는 "== 이름" 아래 "$ 명령"과 출력
덱에 나오는 명령이 있는 장면만 칸이 돼요. 칸의 쪽 번호와 제목은 그 명령이 처음 보이는 장이에요."""
import json
import os
import re
import sys

from deck import ROOT, Deck, write


def from_out_json(path):
    scenes = json.load(open(path, encoding="utf8"))
    for name, runs in scenes.items():
        steps = []
        for r in runs:
            if "out" not in r or not r.get("cmd"):
                continue
            cwd = r.get("cwd") or ""
            steps.append({"cmd": r["cmd"], "out": r["out"], **({"cwd": cwd} if cwd and cwd != "~" else {})})
        if steps:
            yield name, steps


def from_txt(path):
    name, steps, cur = None, [], None
    for raw in open(path, encoding="utf8").read().split("\n"):
        line = raw.rstrip()
        h = re.match(r"^(?:### |== )(.+)$", line)
        if h:
            if name and steps:
                yield name, steps
            name, steps, cur = h.group(1).strip(), [], None
            continue
        m = re.match(r"^\$ (?:\[([^\]]+)\] )?(.*)$", line)
        if m:
            cur = {"cmd": m.group(2).strip(), "out": []}
            if m.group(1) and m.group(1) != "~":
                cur["cwd"] = m.group(1)
            steps.append(cur)
        elif re.match(r"^\[(exit|rc)=?\s?-?\d+\]$", line):
            continue
        elif cur is not None:
            cur["out"].append(line)
    if name and steps:
        yield name, steps


def main():
    chapter = sys.argv[1]
    tools = os.path.join(ROOT, chapter, "tools")
    if os.path.exists(os.path.join(tools, "out.json")):
        src, it = "tools/out.json(tools/demo.py)", from_out_json(os.path.join(tools, "out.json"))
    else:
        src, it = "tools/demo-output.txt(tools/demo.sh)", from_txt(os.path.join(tools, "demo-output.txt"))
    deck = Deck(chapter)
    cells, last = [], 1
    for name, steps in it:
        for s in steps:
            while s["out"] and s["out"][-1] == "":
                s["out"].pop()
        p = None
        for s in steps:
            p = deck.find(s["cmd"], last) or deck.find(s["cmd"])
            if p:
                break
        if not p:
            continue
        last = p["no"]
        cells.append({"id": re.sub(r"[^\w-]+", "-", name).strip("-") or f"s{len(cells) + 1}", "page": p["no"], "title": p["title"], "part": deck.part(p["no"]), "steps": steps})
    cells.sort(key=lambda c: c["page"])
    ids = set()
    for c in cells:
        while c["id"] in ids:
            c["id"] += "-2"
        ids.add(c["id"])
    data = {"v": 1, "kind": "replay", "source": f"{chapter}/{src}로 실제 실행한 출력", "cells": cells}
    n = sum(len(c["steps"]) for c in cells)
    print(f"{chapter}: 칸 {len(cells)}개, 명령 {n}개 -> {write(chapter, data)}")


main()
