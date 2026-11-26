"""터미널, Git, Docker 챕터의 재생형 practice.json을 만들어요.
    python3 build_replay.py 02-git-basics [--force]
덱의 터미널 칸(어두운 상자 안의 "$ 명령"과 그 아래 출력 줄)을 장마다 읽어요. 덱의 터미널 화면은 챕터의
demo.sh, demo.py로 실제로 실행한 출력을 옮긴 것이라, 지어낸 출력 없이 수업 화면 그대로 보여 줘요.
수강생이 친 명령이 수업 명령과 같으면 그 출력을 보여 줘요(실제로 실행하지는 않아요)."""
import html
import os
import re
import sys
from html.parser import HTMLParser

from deck import ROOT, Deck, write

# 챕터 README가 밝힌 출력 출처가 따로 있으면 그대로 적어요
SOURCE = {
    "01-linux-terminal": "01 덱의 터미널 화면(bash 5.2, GNU coreutils 9.4에서 실제로 실행해 확인한 출력, 프롬프트는 위치만 남김)",
}
MONO = re.compile(r"mono|Mono|Consolas|Menlo", re.I)


class Term(HTMLParser):
    """장 하나에서 어두운 상자 안의 고정폭 글자 줄을 상자별로 모아요."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []  # [(tag, box_id or None, style)]
        self.boxes = {}
        self.order = []
        self.p = None
        self.n = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        st = a.get("style", "") or ""
        if tag in ("div", "section", "aside"):
            dark = re.search(r"background:\s*#(1[0-9A-F]|2[0-9A-F])[0-9A-F]{4}\b", st, re.I) is not None
            box = None
            if dark:
                self.n += 1
                box = self.n
            self.stack.append((tag, box, st))
        elif tag == "p" or tag == "span" and self.p is None and "white-space:pre" in st:
            inherited = any(MONO.search(s or "") for _, _, s in self.stack)
            if MONO.search(st) or inherited:
                box = next((b for _, b, _ in reversed(self.stack) if b), None)
                aside = any(t == "aside" for t, _, _ in self.stack)
                if box and not aside:
                    self.p = {"box": box, "text": "", "tag": tag}
        elif tag == "br" and self.p is not None:
            self.p["text"] += "\n"

    def handle_endtag(self, tag):
        if self.p is not None and tag == self.p["tag"]:
            b = self.p["box"]
            if b not in self.boxes:
                self.boxes[b] = []
                self.order.append(b)
            self.boxes[b].extend(self.p["text"].split("\n"))
            self.p = None
        elif tag in ("div", "section", "aside") and self.stack:
            self.stack.pop()

    def handle_data(self, data):
        if self.p is not None:
            self.p["text"] += data


def steps_of(lines):
    lines = [l.replace(" ", " ").rstrip() for l in lines]
    # 프롬프트는 "$ 명령"이거나 01처럼 위치를 앞에 둔 "~/kant $ 명령"이에요
    if not any(re.match(r"^(?:[~/]\S* )?\$ ", l) for l in lines):
        return None
    steps, cur = [], None
    # 명령 없이 프롬프트만 있는 마지막 줄("~ $")은 빼요
    lines = [l for l in lines if not re.match(r"^(?:[~/]\S* )?\$$", l)]
    for l in lines:
        m = re.match(r"^(?:(\S+) )?\$ (.*)$", l)
        if m and (m.group(1) is None or m.group(1).startswith(("~", "/"))):
            cur = {"cmd": m.group(2).strip(), "out": []}
            if m.group(1):
                cur["cwd"] = m.group(1)
            steps.append(cur)
        elif cur is None:
            steps.append(cur := {"cmd": "", "out": [l]})
        else:
            cur["out"].append(l)
    for s in steps:
        while s["out"] and s["out"][-1] == "":
            s["out"].pop()
    # 명령이 하나도 없는 상자는 뺴요
    return steps if any(s["cmd"] for s in steps) else None


def main():
    chapter = sys.argv[1]
    if os.path.exists(os.path.join(ROOT, chapter, "practice.json")) and "--force" not in sys.argv:
        import json

        if json.load(open(os.path.join(ROOT, chapter, "practice.json"))).get("kind") != "replay":
            raise SystemExit(f"{chapter}: 이미 실행형 practice.json이 있어요")
    deck = Deck(chapter)
    cells, seen = [], set()
    for pg in deck.pages:
        raw = open(os.path.join(ROOT, chapter, "slides", pg["id"] + ".html"), encoding="utf8").read()
        t = Term()
        t.feed(raw)
        for k, b in enumerate(t.order):
            st = steps_of(t.boxes[b])
            if not st:
                continue
            key = tuple((s["cmd"], tuple(s["out"])) for s in st)
            if key in seen:
                continue  # 같은 화면이 다음 장에 또 나오면 한 번만
            seen.add(key)
            cells.append({"id": f"{pg['id']}-{k + 1}", "page": pg["no"], "title": pg["title"], "part": deck.part(pg["no"]), "steps": st})
    data = {
        "v": 1,
        "kind": "replay",
        "source": SOURCE.get(chapter, f"{chapter} 덱의 터미널 화면(챕터 도구로 실제 실행한 출력)"),
        "cells": cells,
    }
    n = sum(len([s for s in c["steps"] if s["cmd"]]) for c in cells)
    print(f"{chapter}: 칸 {len(cells)}개, 명령 {n}개 -> {write(chapter, data)}")


main()
