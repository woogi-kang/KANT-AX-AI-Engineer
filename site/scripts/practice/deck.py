"""덱(slides/*.html, deck.json)과 챕터 README에서 쪽 번호, 장 제목, 파트를 찾아 주는 도구예요.
build_python.py, build_sql.py, build_replay.py가 같이 써요."""
import html
import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def _text(s):
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"</p>|</div>|</li>|</tr>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(s)


class Deck:
    def __init__(self, chapter):
        self.chapter = chapter
        base = os.path.join(ROOT, chapter, "slides")
        order = json.load(open(os.path.join(base, "deck.json")))["order"]
        self.pages = []
        for i, sid in enumerate(order):
            raw = open(os.path.join(base, sid + ".html"), encoding="utf8").read()
            # 발표자 노트(aside)는 장 화면이 아니라서 빼요.
            body = re.sub(r"<aside[\s\S]*?</aside>", "", raw)
            m = re.search(r'<h[12][^>]*id="title"[^>]*>([\s\S]*?)</h[12]>', body) or re.search(r"<h[12][^>]*>([\s\S]*?)</h[12]>", body)
            title = re.sub(r"\s+", " ", _text(m.group(1))).strip() if m else ""
            lines = [re.sub(r"\s+", " ", l).strip() for l in _text(body).split("\n")]
            self.pages.append({"no": i + 1, "id": sid, "title": title, "lines": [l for l in lines if l], "flat": re.sub(r"\s+", "", _text(body))})
        self.parts = parts_of(chapter)

    def find(self, code, start=1):
        """코드 줄이 모두 보이는 첫 쪽(start쪽부터). 없으면 None"""
        want = [re.sub(r"\s+", "", l) for l in code.split("\n") if l.strip()]
        if not want:
            return None
        for p in self.pages:
            if p["no"] < start:
                continue
            if all(w in p["flat"] for w in want):
                return p
        return None

    def page(self, no):
        return self.pages[no - 1] if no and 0 < no <= len(self.pages) else None

    def part(self, no):
        for pt in self.parts:
            if pt["from"] <= no <= pt["to"]:
                return pt["name"]
        return ""


def parts_of(chapter):
    md = open(os.path.join(ROOT, chapter, "README.md"), encoding="utf8").read()
    sec = next((s for s in re.split(r"^## ", md, flags=re.M) if s.startswith("구성")), "")
    out = []
    for line in sec.split("\n"):
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or not re.search(r"\d", cells[1]) or set(cells[1]) <= set("-: "):
            continue
        nums = [int(x) for x in re.findall(r"\d+", cells[1])]
        out.append({"name": cells[0], "from": nums[0], "to": nums[-1] if len(nums) > 1 else nums[0]})
    return out


def write(chapter, data):
    """practice.json을 써요. 전에 적어 둔 diff 메모(같은 id, 같은 코드)는 그대로 옮겨요."""
    p = os.path.join(ROOT, chapter, "practice.json")
    if os.path.exists(p):
        old = {c["id"]: c for c in json.load(open(p, encoding="utf8")).get("cells", [])}
        for c in data["cells"]:
            o = old.get(c["id"])
            if o and o.get("diff") and o.get("code") == c.get("code"):
                c["diff"] = o["diff"]
    with open(p, "w", encoding="utf8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    return p
