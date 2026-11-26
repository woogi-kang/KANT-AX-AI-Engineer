"""SQL 챕터의 practice.json을 만들어요.
    python3 build_sql.py 36-sql-basics
챕터의 tools/out.json(tools/demo.py가 실제 postgres:18 psql 화면을 그대로 담은 것)을 읽어요.
psql 한 번(장면 하나)이 실습 칸 하나예요. 칸을 실행하면 앞 장면의 문장을 먼저 조용히 넣어서 수업과 같은 표 상태를 만들어요.
\\d 같은 psql 백슬래시 명령은 브라우저 안 PostgreSQL에 없어서 빼요."""
import ast
import json
import os
import re
import sys

from deck import ROOT, Deck, write

PROMPT = re.compile(r"^(\w+)([=\-'\"(])([*!]?)# ?(.*)$")
HEAD = re.compile(r"^(psql \(|Type \"help\" for help\.)")


def parse(lines):
    """psql 화면 줄 → (입력 줄들, 화면 줄들). 백슬래시 명령과 그 출력은 빼요."""
    code, shown = [], []
    i = 0
    while i < len(lines) and not PROMPT.match(lines[i]):
        i += 1
    skip = False
    for line in lines[i:]:
        m = PROMPT.match(line)
        if m:
            text = m.group(4)
            if text.startswith("\\"):
                skip = True
                continue
            if m.group(2) == "=" and text == "":
                # 끝에 남은 빈 프롬프트
                skip = True
                continue
            skip = False
            code.append(text)
            shown.append(line)
        elif not skip:
            shown.append(line)
    while shown and shown[-1] == "":
        shown.pop()
    return code, shown


def find_file(chapter, name):
    for p in [os.path.join(ROOT, chapter, name), os.path.join(ROOT, chapter, "tools", name), os.path.join(ROOT, "38-sql-case", name)]:
        if os.path.exists(p):
            return p
    raise SystemExit(f"{name}을 찾지 못했어요")


def scene_opts(chapter):
    """demo.py의 scene(이름, 입력, setup=/pre=/seed=/keep=) 호출을 읽어 장면마다 숨은 준비를 알아내요.
    fresh()가 있는 demo.py는 장면마다 kant_shop을 새로 만들어요(keep=True면 앞 장면에 이어서)."""
    path = os.path.join(ROOT, chapter, "tools", "demo.py")
    src = open(path, encoding="utf8").read()
    tree = ast.parse(src)
    ns = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            try:
                exec(compile(ast.Module([node], []), path, "exec"), ns)
            except Exception:
                pass
    fresh = "def fresh(" in src
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "scene" and node.args:
            try:
                name = eval(compile(ast.Expression(node.args[0]), path, "eval"), ns)
            except Exception:
                continue
            kw = {}
            for k in node.keywords:
                try:
                    kw[k.arg] = eval(compile(ast.Expression(k.value), path, "eval"), ns)
                except Exception:
                    pass
            pre = kw.get("pre") or kw.get("setup") or ""
            if isinstance(pre, (list, tuple)):
                pre = "\n".join(pre)
            out[name] = {"fresh": fresh and not kw.get("keep"), "pre": pre, "seed": kw.get("seed", True)}
    return out


def main():
    chapter = sys.argv[1]
    deck = Deck(chapter)
    scenes = json.load(open(os.path.join(ROOT, chapter, "tools", "out.json"), encoding="utf8"))
    cells, setup, last = [], None, 1
    opts = scene_opts(chapter)
    chain = "psql"
    for name, runs in scenes.items():
        for k, r in enumerate(runs):
            cmd = r.get("cmd", "")
            if "out" not in r:
                continue  # 두 창 장면(43)은 재생형으로만 보여 줘요
            fm = re.search(r"(?:-f /tmp/|< )(\S+\.sql)", cmd)
            if fm and "psql" in cmd:
                setup = open(find_file(chapter, os.path.basename(fm.group(1))), encoding="utf8").read()
                continue
            if "psql" not in cmd or " -c " in cmd:
                continue
            code, shown = parse(r["out"])
            if not code or any(PROMPT.match(l) and PROMPT.match(l).group(1) != "kant_shop" for l in shown):
                continue
            o = opts.get(name, {})
            if o.get("fresh"):
                chain = name
                if o.get("pre"):
                    cells.append({"id": name + "-pre", "chain": chain, "code": o["pre"], "hidden": True})
            src = "\n".join(code)
            first = next((l for l in code if l.strip()), "")
            p = deck.find(first, last) or deck.find(first)
            if p:
                last = p["no"]
            cell = {"id": name + (f"-{k + 1}" if len(runs) > 1 else ""), "chain": chain, "code": src, "expect": shown}
            if o.get("seed") is False:
                cell["noseed"] = True
            if p:
                cell.update(page=p["no"], title=p["title"], part=deck.part(p["no"]))
            else:
                cell["hidden"] = True
            cells.append(cell)
    if setup is None and int(chapter[:2]) >= 38:
        setup = open(find_file(chapter, "sports.sql"), encoding="utf8").read()
    data = {
        "v": 1,
        "kind": "sql",
        "source": f"{chapter}/tools/demo.py가 실제 postgres:18 psql에서 실행한 화면",
        "prompt": "kant_shop",
        "cells": cells,
    }
    if setup:
        data["setup"] = setup
    shown = sum(1 for c in cells if not c.get("hidden"))
    print(f"{chapter}: 칸 {shown}개, 앞 장면만 {len(cells) - shown}개 -> {write(chapter, data)}")


main()
