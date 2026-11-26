"""파이썬 챕터의 practice.json을 만들어요.
    python3 build_python.py <harvest.json> [--packages numpy,pandas]
harvest.json은 harvest_nb.py가 챕터의 tools/run_nb.py를 실제 커널로 돌려 모은 셀과 출력이에요.
덱에 보이는 셀만 실습 칸이 되고, 덱에 없는 셀은 앞 셀(prelude)로만 써요."""
import json
import sys

from deck import Deck, write


def main():
    src = json.load(open(sys.argv[1]))
    packages = []
    if "--packages" in sys.argv:
        packages = sys.argv[sys.argv.index("--packages") + 1].split(",")
    chapter = src["chapter"]
    deck = Deck(chapter)
    cells = []
    last = 1
    for ri, run in enumerate(src["runs"]):
        for ci, c in enumerate(run["cells"]):
            p = deck.find(c["src"], last) or deck.find(c["src"])
            if p:
                last = p["no"]
            cell = {
                "id": f"r{ri + 1}c{ci + 1}",
                "chain": f"r{ri + 1}",
                "code": c["src"],
                "expect": c["out"],
            }
            if len(c["out"]) > 400:
                # 끝나지 않는 반복처럼 아주 긴 출력은 앞 400줄만 두고 원래 줄 수를 적어요.
                cell["expect"] = c["out"][:400]
                cell["cut"] = len(c["out"])
            if c["err"]:
                cell["err"] = True
            if p:
                cell["page"] = p["no"]
                cell["title"] = p["title"]
                cell["part"] = deck.part(p["no"])
            else:
                cell["hidden"] = True
            cells.append(cell)
    data = {
        "v": 1,
        "kind": "python",
        "source": f"{chapter}/tools/run_nb.py를 실제 Jupyter 커널(Python {src['python']})로 실행한 출력",
        "cells": cells,
    }
    if packages:
        data["packages"] = packages
    shown = sum(1 for c in cells if not c.get("hidden"))
    print(f"{chapter}: 칸 {shown}개, 앞 셀만 {len(cells) - shown}개 -> {write(chapter, data)}")


main()
