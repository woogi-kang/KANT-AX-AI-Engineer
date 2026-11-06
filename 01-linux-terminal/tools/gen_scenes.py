"""Generates the terminal + folder-map slides for the Linux terminal deck.

Layout (2026-11-06, after the Stageshow skill): the folder map is the hero and sits on the page without a
panel. What changed is named by a short label beside its node, not by a badge box. The terminal is only as
tall as its lines, and the one-sentence takeaway sits under it as plain text, not in a card.
Clicks on every scene: each command is typed, its output comes in, the changed rows light up with their
labels, and last the takeaway comes in."""
import html, math, os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from highlight import spot, spot_off, underline, TYPE  # noqa: E402

OUT = sys.argv[1]
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"

# part colors (eyebrow)
PART = {
    "concept": "#3A4150", "look": "#1A7340", "make": "#1E3F8F", "path": "#5A3BB8",
    "move": "#8A5200", "extra": "#1D6B70", "help": "#A33131",
}
BLUE = "#2459C9"

# terminal geometry
TL, TT, TWD = 96, 196, 920
# folder map geometry: no panel, nodes start at MX
MX = 1112
PITCH, NODE_H, INDENT = 80, 62, 60
NFS = 32
CTOP, CBOT = 196, 1030          # content area under the title; the map and the left group are placed a third of the way down it


def pitch(nodes):
    """Row pitch: 80px, closer only when a long map would not fit the content area."""
    return min(80, (CBOT - CTOP - 46 - NODE_H) // (len(nodes) - 1))


def map_row0(nodes):
    """Top of the first map row with a third of the free space above the map and two thirds below."""
    h = 46 + (len(nodes) - 1) * pitch(nodes) + NODE_H
    return CTOP + max(0, (CBOT - CTOP - h) // 3) + 46
CH = NFS * 0.6                 # JetBrains Mono advance

NODE_STYLE = {
    #          bg         border                 text       glyph
    "dir":    ("#FDF1DC", "2px solid #E0A84A",   "#5C3A00", "#E0A84A"),
    "file":   ("#FFFFFF", "2px solid #B4B9C3",   "#1D2330", "#B4B9C3"),
    "hidden": ("#F6F5F1", "2px dashed #9AA0AB",  "#6A7180", "#C9CDD4"),
    "ghost":  ("#FBF1F0", "2px dashed #E07A7A",  "#C26A6A", "#F0B4B4"),
}
# what changed: a colored label after the node. text = file content chip, sym = path symbol chip, num = step dot
LABEL = {"new": "#1A7340", "green": "#1A7340", "move": "#8A5200", "del": "#A33131", "info": "#1E3F8F", "hide": "#3A4150"}
NOTE = {"root": "맨 위 폴더", "kim": "~ 내 홈 폴더"}


def e(s):
    return html.escape(s, quote=False)


def p(style, text, attrs=""):
    return f'<p{attrs} style="{style}">{text}</p>'


def sw(s, size):
    """Rough rendered width of sans text: Hangul one em, the rest about 0.56 em."""
    return round(sum(size * (1.0 if '가' <= c <= '힣' else 0.56) for c in s))


def label(n):
    name, kind = n[1], n[2]
    return name + ("/" if kind in ("dir", "hidden") and name != "/" and not name.endswith("/") else "")


def node_w(n):
    return 64 + round(len(label(n)) * CH) + 20


def node_left(depth):
    return MX + depth * INDENT


def tag(x, top, text, kind, attrs=""):
    """One change label beside a node. Returns (html, width)."""
    y = top + NODE_H // 2
    if kind == "text":
        w = 32 + round(len(text) * 24 * 0.6)
        return p(f"position:absolute;left:{x}px;top:{y-20}px;width:{w}px;height:40px;font-family:{MONO};font-size:24px;font-weight:700;line-height:40px;text-align:center;border-radius:8px;background:#1B2029;color:#F2C46D;white-space:nowrap", e(text), attrs), w
    if kind == "sym":
        w = 40 + round(len(text) * 30 * 0.6)
        return p(f"position:absolute;left:{x}px;top:{y-22}px;width:{max(w, 60)}px;height:44px;font-family:{MONO};font-size:30px;font-weight:700;line-height:44px;text-align:center;border-radius:10px;background:#5A3BB8;color:#FFFFFF", e(text), attrs), max(w, 60)
    if kind == "num":
        return p(f"position:absolute;left:{x}px;top:{y-18}px;width:36px;height:36px;font-size:22px;font-weight:700;line-height:36px;text-align:center;border-radius:18px;background:#E3ECFD;color:#1E3F8F", e(text), attrs), 36
    t = "← " + text
    return p(f"position:absolute;left:{x}px;top:{y-19}px;font-size:26px;font-weight:700;line-height:38px;white-space:nowrap;color:{LABEL[kind]}", e(t), attrs), sw(t, 26)


def tree(nodes, cwd=None, badges=None, notes=True, pin_label="현재 위치", hot=None, title=True):
    """nodes: list of (id, name, kind, depth) in display order.
    hot: rows to light up after the terminal finishes. None = the rows with labels, "cwd" = the current row,
    False = none. The labels come in with the spotlight; the takeaway comes on the next click."""
    badges = badges or {}
    rows = {n[0]: i for i, n in enumerate(nodes)}
    if hot is None:
        hot = [k for k, v in badges.items() if v and all(len(b) == 2 for b in v)]
    elif hot == "cwd":
        hot = [cwd]
    hot = hot or []
    ROW0, PITCH = map_row0(nodes), pitch(nodes)
    t0 = STATE["n"] + 1
    fresh = {k for k in hot if any(b[1] == "new" for b in badges.get(k, []))}
    pop = lambda k: f' data-build-in="pop order {t0}"' if k in fresh else ""
    o = []
    if title:
        o.append(p(f"position:absolute;left:{MX}px;top:{ROW0-46}px;width:400px;font-size:24px;font-weight:700;line-height:1.2;color:#6A7180", "폴더 지도", ' id="tree-title"'))
    # connector lines
    for i, n in enumerate(nodes):
        nid, _, _, d = n
        if d == 0:
            continue
        j = max(k for k in range(i) if nodes[k][3] == d - 1)
        x = node_left(d - 1) + 27
        y0 = ROW0 + j * PITCH + NODE_H
        y1 = ROW0 + i * PITCH + NODE_H // 2
        o.append(f'<div id="lv-{nid}"{pop(nid)} style="position:absolute;left:{x}px;top:{y0}px;width:2px;height:{y1-y0+1}px;background:#CFCABF"></div>')
        o.append(f'<div id="lh-{nid}"{pop(nid)} style="position:absolute;left:{x}px;top:{y1-1}px;width:{node_left(d)-x}px;height:2px;background:#CFCABF"></div>')
    right = 0
    for i, n in enumerate(nodes):
        nid, name, kind, d = n
        bg, bd, col, gl = NODE_STYLE[kind]
        top = ROW0 + i * PITCH
        left, w = node_left(d), node_w(n)
        glyph = (f'<div style="width:28px;height:22px;background:{gl};border-radius:4px"></div>' if kind != "file" and not (kind == "ghost" and "." in name)
                 else f'<div style="width:22px;height:26px;background:{gl};border-radius:3px"></div>')
        box = lambda at, bg, bd, col, glyph, i="": (f'<div{i}{at} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{NODE_H}px;background:{bg};border:{bd};border-radius:12px;padding:0 16px;display:flex;flex-direction:row;gap:14px;align-items:center">'
                                                    + glyph + p(f"font-family:{MONO};font-size:{NFS}px;font-weight:700;white-space:nowrap;color:{col}", e(label(n))) + '</div>')
        if kind == "ghost" and nid in hot:
            # deleted on this slide: the folder or file is drawn whole first, and the dashed ghost fades in over it
            k2 = "file" if "." in name else "dir"
            bg2, bd2, col2, gl2 = NODE_STYLE[k2]
            g2 = (f'<div style="width:22px;height:26px;background:{gl2};border-radius:3px"></div>' if k2 == "file"
                  else f'<div style="width:28px;height:22px;background:{gl2};border-radius:4px"></div>')
            o.append(box("", bg2, bd2, col2, g2))
            o.append(box(f' data-build-in="fade order {t0}"', bg, bd, col, glyph, f' id="n-{nid}"'))
        else:
            o.append(box(pop(nid), bg, bd, col, glyph, f' id="n-{nid}"'))
        x = left + w + 20
        if notes and nid in NOTE:
            o.append(p(f"position:absolute;left:{x}px;top:{top + NODE_H // 2 - 17}px;font-size:24px;font-weight:700;line-height:34px;white-space:nowrap;color:#8A909C", e(NOTE[nid]), f' id="note-{nid}"'))
            x += sw(NOTE[nid], 24) + 20
        if nid == cwd:
            o.append(f'<div id="pin" style="position:absolute;left:{left-7}px;top:{top-7}px;width:{w+14}px;height:{NODE_H+14}px;border:3px solid {BLUE};border-radius:17px"></div>')
            pw = sw(pin_label, 22) + 28
            o.append(p(f"position:absolute;left:{x}px;top:{top + NODE_H // 2 - 18}px;width:{pw}px;height:36px;font-size:22px;font-weight:700;line-height:36px;text-align:center;color:#FFFFFF;background:{BLUE};border-radius:8px", e(pin_label), ' id="pin-tag"'))
            x += pw + 20
        for text, kind_b, *rest in badges.get(nid, []):
            order = f" order {rest[0]}" if rest else (f" order {t0}" if hot else "")
            h, bw = tag(x, top, text, kind_b, f' data-build-in="fade{order}"')
            o.append(h)
            x += bw + 14
        right = max(right, x)
    if hot:
        ii = sorted(rows[h] for h in hot)
        y0, y1 = ROW0 + ii[0] * PITCH - 14, ROW0 + ii[-1] * PITCH + NODE_H + 14
        o.append(spot(t0, MX - 20, y0, 1840 - MX, y1 - y0, pad=0, r=16, dim=0.55))
        o.append(spot_off(t0 + 1))
    assert right < 1840, ("tree too wide", right)
    return o


def head(sec_id, part, eyebrow, title, mono=True, transition="magic"):
    STATE["n"], STATE["dy"] = 0, 0
    o = [f'<section id="{sec_id}" data-transition="{transition}" style="background:#F6F5F1;color:#1D2330;font-family:{SANS};word-break:keep-all;padding:96px;display:flex;flex-direction:column">']
    o.append(p(f"position:absolute;left:96px;top:40px;width:1728px;font-size:24px;font-weight:700;color:{PART[part]}", e(eyebrow), ' id="eyebrow"'))
    fam = f"font-family:{MONO};" if mono else ""
    o.append(f'<h2 id="cmd" style="position:absolute;left:96px;top:86px;width:1728px;{fam}font-size:52px;font-weight:700;line-height:1.15;color:#1D2330">{title}</h2>')
    return o


STATE = {"n": 0, "tb": TT}
PT, PB, DOTS = 24, 30, 34      # terminal padding top/bottom, dot row + its gap


def terminal(lines, size=None):
    """lines: (kind, text). kind: $ prompt line 'path|command', o output, r error, l ls -l line, # comment.
    The window is as tall as its lines. Each command is typed on its own click and its output lines come in
    together on the next click. An error line gets a red pen underline as it appears."""
    if size is None:
        longest = max(len(t.replace("|", " $ ")) for _, t in lines)
        size = next(z for z in (34, 30, 28, 26, 24) if longest * z * 0.6 <= TWD - 56)
    lh = round(size * 1.45)
    cur, prev, marks = 0, None, []
    height = PT + DOTS + len(lines) * lh + (len(lines) - 1) * 4 + PB
    o = [f'<div id="term" style="position:absolute;left:{TL}px;top:__Y{TT}__px;width:{TWD}px;height:{height}px;background:#1B2029;border-radius:20px;padding:{PT}px 28px {PB}px;display:flex;flex-direction:column;gap:4px;font-family:{MONO}">']
    o.append('<div style="display:flex;flex-direction:row;gap:10px;height:16px;margin-bottom:14px">'
             + "".join(f'<div style="width:16px;height:16px;border-radius:8px;background:{c}"></div>' for c in ("#F28B82", "#F2C46D", "#7FD18B"))
             + '</div>')
    col = {"o": "#D8DEE9", "r": "#F28B82", "#": "#9AA3B5"}
    for k, (kind, text) in enumerate(lines):
        if kind == "$":
            cur += 1
        elif prev == "$":
            cur += 1
        at = f' data-build-in="fade order {cur}"' if cur else ""
        prev = kind
        st = f"font-size:{size}px;line-height:{lh}px;height:{lh}px;white-space:nowrap;"
        if kind == "$":
            where, cmd = text.split("|", 1)
            t = f'<span style="color:#8FB3FF">{e(where)} $</span> <span{TYPE(cur)}>{e(cmd)}</span>'
            o.append(p(st + "color:#F2C46D", t, at))
        elif kind == "l":
            t = f'<span style="color:#7FD18B">{e(text[0])}</span>' + e(text[1:]).replace("  ", "&#160;&#160;")
            o.append(p(st + "color:#D8DEE9", t, at))
        else:
            t = e(text).replace("  ", "&#160;&#160;") if text else "&#160;"
            o.append(p(st + f"color:{col[kind]}", t, at))
        if kind == "r":
            y = TT + PT + DOTS + k * (lh + 4) + lh - 2
            u = underline(cur, TL + 28, round(TL + 28 + len(text) * size * 0.6), y, color="#E5534B")
            marks.append(u.replace("position:absolute;left:0;top:0;", "position:absolute;left:0;top:__Y0__px;", 1))
    o.append('</div>')
    STATE["n"] = cur
    STATE["tb"] = TT + height
    return o + marks


def explain(title, sub=None):
    """The takeaway under the terminal: one bold sentence and at most one plain line. No card."""
    top = STATE["tb"] + 56
    plain = lambda t: re.sub(r"<[^>]+>", "", t)
    h = math.ceil(sw(plain(title), 44) / TWD) * 59 + (14 + math.ceil(sw(plain(sub), 30) / TWD) * 45 if sub else 0)
    STATE["dy"] = max(0, (CBOT - CTOP - (top + h - TT)) // 3)
    o = [f'<div id="explain" data-build-in="rise order {STATE["n"] + 2}" style="position:absolute;left:{TL}px;top:__Y{top}__px;width:{TWD}px;display:flex;flex-direction:column;gap:14px">']
    o.append(p("font-size:44px;font-weight:700;line-height:1.35;color:#1D2330", title))
    if sub:
        o.append(p("font-size:30px;line-height:1.5;color:#4A5262", sub))
    o.append('</div>')
    return o


def write(sec_id, parts, notes):
    body = "\n".join(parts) + f"\n<aside>{e(notes)}</aside>\n</section>\n"
    body = re.sub(r"__Y(\d+)__", lambda m: str(int(m.group(1)) + STATE.get("dy", 0)), body)
    with open(os.path.join(OUT, f"{sec_id}.html"), "w") as f:
        f.write(body)


def code(s):
    return f'<span style="font-family:{MONO};color:{BLUE}">{e(s)}</span>'


# ---------- tree states ----------
BASE = [("root", "/", "dir", 0), ("home", "home", "dir", 1), ("kim", "kim", "dir", 2),
        ("desk", "Desktop", "dir", 3), ("docs", "Documents", "dir", 3)]
KANT = BASE + [("kant", "kant", "dir", 3)]
MEMO = KANT + [("memo", "memo.md", "file", 4)]
NOTES = KANT + [("memo", "memo.md", "file", 4), ("notes", "notes", "dir", 4)]
MOVED = KANT + [("notes", "notes", "dir", 4), ("memo", "memo.md", "file", 5)]
COPY = MOVED + [("plan", "plan.md", "file", 4)]
RENAMED = MOVED + [("plan", "todo.md", "file", 4)]

# ---------- 개념 ----------
o = head("tree-map", "concept", "개념 3 · 폴더 트리", "폴더 안에 폴더, 거꾸로 선 나무", mono=False, transition="fade")
# each meaning sits on the same height as its node on the map, and a band spotlight joins the two
for i, (row, sym, t, sub, c) in enumerate([(0, "/", "맨 위 폴더 (루트)", "모든 폴더가 여기서 시작해요.", "#5A3BB8"),
                                          (2, "~", "내 홈 폴더", "터미널을 열면 여기서 시작해요.", "#1E3F8F")]):
    cy = map_row0(BASE) + row * PITCH + NODE_H // 2
    o.append(f'<div data-build-in="rise order {i+1}" style="position:absolute;left:96px;top:{cy-40}px;width:880px;height:80px;display:flex;flex-direction:row;gap:28px;align-items:center">'
             + p(f"font-family:{MONO};font-size:64px;font-weight:700;line-height:68px;width:72px;text-align:center;color:{c}", e(sym))
             + p(f"font-size:36px;font-weight:700;white-space:nowrap;color:{c}", e(t))
             + p("font-size:28px;white-space:nowrap;color:#4A5262", e(sub)) + '</div>')
    o.append(spot(i + 1, 76, cy - 36, 1764, 72, pad=0, r=16, dim=0.55))
o.append(spot_off(3))
o.append(p("position:absolute;left:96px;top:724px;width:880px;font-size:32px;font-weight:700;color:#1D2330", "홈 폴더 주소는 컴퓨터마다 달라요", ' data-build-in="rise order 3"'))
for i, (k, v) in enumerate([("Linux", "/home/kim"), ("Mac", "/Users/kim"), ("Windows Git Bash", "/c/Users/kim")]):
    o.append(f'<div data-build-in="rise order 3" style="position:absolute;left:96px;top:{786 + i * 72}px;width:880px;height:72px;border-top:2px solid #E1DED6;display:flex;flex-direction:row;align-items:center">'
             + p("font-size:28px;font-weight:700;width:320px;color:#4A5262", e(k))
             + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:#1D2330", e(v)) + '</div>')
o += tree(BASE, cwd="kim")
write("tree-map", o, "폴더는 나무를 거꾸로 세운 모양이에요. 맨 위 / 에서 가지가 아래로 뻗어요. 이 자료는 Linux 기준이라 홈 폴더가 /home/kim이에요. Mac이나 Windows에서는 주소만 다르고 명령은 똑같이 동작해요. 오른쪽 폴더 지도와 파란 현재 위치 표시는 뒤의 모든 실습 장면에 계속 나와요.")

# ---------- 둘러보기 ----------
o = head("s1-pwd", "look", "실습 1 · 둘러보기", "pwd")
o += terminal([("$", "~|pwd"), ("o", "/home/kim")])
o += explain("지금 있는 폴더의 주소를 알려 줘요", "pwd는 print working directory의 줄임말이에요.")
o += tree(BASE, cwd="kim", hot="cwd")
write("s1-pwd", o, "터미널을 처음 열면 홈 폴더에서 시작해요. 프롬프트의 ~ 와 pwd가 알려 준 /home/kim은 같은 곳이에요. 길을 잃은 것 같으면 언제든 pwd부터 쳐요.")

o = head("s2-ls", "look", "실습 2 · 둘러보기", "ls")
o += terminal([("$", "~|pwd"), ("o", "/home/kim"), ("$", "~|ls"), ("o", "Desktop  Documents")])
o += explain("지금 폴더 안에 든 것을 보여 줘요", "ls는 list의 줄임말이에요. 한 칸 아래에 있는 것만 보여요.")
o += tree(BASE, cwd="kim", badges={"desk": [("ls에 보임", "info")], "docs": [("ls에 보임", "info")]})
write("s2-ls", o, "ls는 현재 위치 바로 아래 칸만 보여 줘요. 그래서 지도에서 kim 밑의 Desktop과 Documents만 나와요. 영어 소문자 L과 S예요. 숫자 1이나 대문자 I와 헷갈리지 않게 짚어 주세요.")

o = head("s3-mkdir", "look", "실습 3 · 둘러보기", "mkdir kant")
o += terminal([("$", "~|mkdir kant"), ("$", "~|ls"), ("o", "Desktop  Documents  kant")])
o += explain("새 폴더를 만들어요", "만들기만 하고 안으로 들어가지는 않아요.")
o += tree(KANT, cwd="kim", badges={"kant": [("새로 생김", "new")]})
write("s3-mkdir", o, "mkdir은 make directory의 줄임말이에요. 디렉터리는 폴더와 같은 말이에요. 아무 출력이 없으면 성공이에요. 리눅스 명령은 대부분 성공하면 조용해요.")

o = head("s4-cd", "look", "실습 4 · 둘러보기", "cd kant")
o += terminal([("$", "~|cd kant"), ("$", "~/kant|pwd"), ("o", "/home/kim/kant")])
o += explain("폴더 안으로 들어가요", f"프롬프트 앞의 위치도 {code('~')} 에서 {code('~/kant')}로 바뀌어요.")
o += tree(KANT, cwd="kant", hot="cwd")
write("s4-cd", o, "cd는 change directory예요. 파란 현재 위치 표시가 kant로 내려가는 걸 보여 주세요. 프롬프트 앞부분이 바뀐 것도 함께 짚어요. 명령을 치기 전에 프롬프트로 지금 위치를 확인하는 습관을 들이면 실수가 줄어요.")

# ---------- 만들기 ----------
o = head("s5-touch", "make", "실습 5 · 파일 만들기", "touch memo.md")
o += terminal([("$", "~/kant|touch memo.md"), ("$", "~/kant|ls"), ("o", "memo.md")])
o += explain("내용이 없는 빈 파일을 만들어요")
o += tree(MEMO, cwd="kant", badges={"memo": [("새로 생김", "new")]})
write("s5-touch", o, "touch는 현재 위치에 파일을 만들어요. 그래서 memo.md는 kant 안에 생겨요. 이미 있는 파일에 touch를 쳐도 내용은 지워지지 않아요.")

o = head("s6-echo", "make", "실습 6 · 파일 만들기", 'echo "# hello" &gt; memo.md')
o += terminal([("$", '~/kant|echo "# hello" > memo.md'), ("$", "~/kant|cat memo.md"), ("o", "# hello")])
o += explain("파일에 글자를 쓰고 읽어요", f"{code('>')} 는 파일 내용을 지우고 새로 써요. {code('cat')}은 내용을 화면에 보여 줘요.")
o += tree(MEMO, cwd="kant", badges={"memo": [("# hello", "text")]})
write("s6-echo", o, "echo는 글자를 화면에 그대로 출력하는 명령이에요. 뒤에 > 파일이름을 붙이면 화면 대신 파일로 보내요. > 는 기존 내용을 덮어쓰니 중요한 파일에는 쓰지 않아요. # 은 마크다운에서 제목을 뜻하는 기호예요. 다음 장에서 봐요. 실제 수업에서는 파일 내용을 VS Code 같은 에디터로 고치는 일이 더 많아요.")

o = head("s7-mkdir2", "make", "실습 7 · 파일 만들기", "mkdir notes")
o += terminal([("$", "~/kant|mkdir notes"), ("$", "~/kant|ls"), ("o", "memo.md  notes")])
o += explain("폴더 안에 폴더를 또 만들어요", "ls에는 파일과 폴더가 함께 보여요.")
o += tree(NOTES, cwd="kant", badges={"notes": [("새로 생김", "new")]})
write("s7-mkdir2", o, "ls 출력만으로는 무엇이 파일이고 무엇이 폴더인지 구분하기 어려워요. 터미널에 따라 폴더를 다른 색으로 보여 주기도 해요. 이름에 .md 같은 확장자가 있으면 대개 파일이에요.")

# ---------- 경로 ----------
o = head("paths", "path", "경로 1", "절대 경로와 상대 경로", mono=False, transition="fade")
for i, (top, name, path_, sub, c) in enumerate([
        (236, "절대 경로", "/home/kim/kant/notes", "맨 위 / 부터 끝까지 적어요. 어디서 쳐도 같은 곳이에요.", "#1E3F8F"),
        (636, "상대 경로", "notes", "현재 위치 kant에서 출발해요. 위치가 바뀌면 가리키는 곳도 바뀌어요.", "#1A7340")]):
    o.append(f'<div data-build-in="rise order {i+1}" style="position:absolute;left:96px;top:{top}px;width:880px;display:flex;flex-direction:column;gap:20px">'
             + p(f"font-size:34px;font-weight:700;color:{c}", e(name))
             + p(f"font-family:{MONO};font-size:56px;font-weight:700;line-height:1.2;color:#1D2330", e(path_))
             + p("font-size:28px;line-height:1.5;color:#4A5262", e(sub)) + '</div>')
o += tree(NOTES, cwd="kant", notes=False, badges={
    "root": [("1", "num", 1)], "home": [("2", "num", 1)], "kim": [("3", "num", 1)],
    "kant": [("4", "num", 1)], "notes": [("5", "num", 1), ("한 칸 아래", "green", 2)]})
write("paths", o, "주소를 쓰는 방법이 두 가지예요. 절대 경로는 집 주소처럼 맨 위부터 다 적는 방식이에요. 상대 경로는 여기서 오른쪽 두 번째 집처럼 지금 위치를 기준으로 말하는 방식이에요. 평소에는 짧은 상대 경로를 많이 써요. 헷갈릴 때는 절대 경로가 확실해요.")

o = head("special", "path", "경로 2", "기호 네 개만 기억해요", mono=False, transition="fade")
# each symbol sits on the same height as the folder it points to (current position: notes)
SYM = [(".", "지금 폴더", 7, 1), ("..", "한 칸 위 폴더", 5, 2), ("~", "내 홈 폴더", 2, 3), ("/", "맨 위 폴더", 0, 4)]
for s_, t, row, k in SYM:
    cy = map_row0(NOTES) + row * PITCH + NODE_H // 2
    o.append(f'<div data-build-in="rise order {k}" style="position:absolute;left:96px;top:{cy-40}px;width:880px;height:80px;display:flex;flex-direction:row;gap:32px;align-items:center">'
             + p(f"font-family:{MONO};font-size:60px;font-weight:700;line-height:72px;width:100px;text-align:center;color:#5A3BB8", e(s_))
             + p("font-size:38px;font-weight:700;white-space:nowrap;color:#1D2330", e(t)) + '</div>')
o += tree(NOTES, cwd="notes", notes=False, badges={
    "notes": [(".", "sym", 1)], "kant": [("..", "sym", 2)], "kim": [("~", "sym", 3)], "root": [("/", "sym", 4)]})
write("special", o, "현재 위치가 notes일 때 기준이에요. . 은 지금 폴더, .. 은 바로 위 kant예요. ~ 와 / 는 어디에 있든 늘 같은 곳을 가리켜요. 이 네 기호는 cd뿐 아니라 mv, cp, ls 같은 모든 명령에서 똑같이 써요.")

o = head("s8-cd-rel", "path", "실습 8 · 경로", "cd notes")
o += terminal([("$", "~/kant|cd notes"), ("$", "~/kant/notes|pwd"), ("o", "/home/kim/kant/notes")])
o += explain("지금 위치에서 notes로 들어가요", "kant 안에 notes가 있어서 이름만 적어도 돼요. 이렇게 적는 게 상대 경로예요.")
o += tree(NOTES, cwd="notes", hot="cwd")
write("s8-cd-rel", o, "notes만 적어도 되는 건 지금 kant 안에 있어서예요. 홈 폴더에서 cd notes를 치면 에러가 나요. 그 경우는 뒤의 막힐 때 파트에서 다시 봐요.")

o = head("s9-cd-up", "path", "실습 9 · 경로", "cd ..")
o += terminal([("$", "~/kant/notes|cd .."), ("$", "~/kant|pwd"), ("o", "/home/kim/kant")])
o += explain("한 칸 위 폴더로 올라가요", f"{code('..')} 은 바로 위 폴더예요. {code('cd ../..')} 처럼 두 칸도 한 번에 가요.")
o += tree(NOTES, cwd="kant", hot="cwd")
write("s9-cd-up", o, "cd와 .. 사이에 띄어쓰기를 꼭 넣어요. cd.. 로 붙여 치면 에러가 나는 터미널이 있어요. 두 칸 위로 가려면 ../.. 처럼 / 로 이어요.")

o = head("s10-cd-abs", "path", "실습 10 · 경로", "cd /home/kim/kant/notes")
o += terminal([("$", "~/kant|cd /home/kim/kant/notes"), ("$", "~/kant/notes|pwd"), ("o", "/home/kim/kant/notes")])
o += explain("맨 위부터 적은 주소로 바로 가요", "절대 경로는 지금 어디에 있든 같은 곳으로 가요.")
o += tree(NOTES, cwd="notes", hot="cwd")
write("s10-cd-abs", o, "/ 로 시작하면 절대 경로예요. 지금 위치와 상관없이 늘 같은 곳으로 가요. 경로가 길어서 직접 치기보다는 Tab 자동 완성을 같이 써요.")

o = head("s11-cd-home", "path", "실습 11 · 경로", "cd ~")
o += terminal([("$", "~/kant/notes|cd ~"), ("$", "~|pwd"), ("o", "/home/kim")])
o += explain("어디서든 홈 폴더로 돌아가요", f"길을 잃으면 {code('cd ~')} 하고 다시 시작해요.")
o += tree(NOTES, cwd="kim", hot="cwd")
write("s11-cd-home", o, "cd 뒤에 아무것도 적지 않아도 홈 폴더로 가요. 두 방법 모두 결과가 같아요. 다음 장면은 cd kant로 다시 들어간 뒤 이어져요.")

# ---------- 옮기고 지우기 ----------
o = head("s12-mv", "move", "실습 12 · 옮기고 지우기", "mv memo.md notes/")
o += terminal([("$", "~|cd kant"), ("$", "~/kant|mv memo.md notes/"), ("$", "~/kant|ls"), ("o", "notes"),
               ("$", "~/kant|ls notes"), ("o", "memo.md")])
o += explain("파일을 다른 폴더로 옮겨요", f"원래 자리에는 남지 않아요. {code('mv 옮길것 도착할곳')} 순서로 적어요.")
o += tree(MOVED, cwd="kant", badges={"memo": [("옮겨짐", "move")]})
write("s12-mv", o, "mv는 move예요. 첫 번째가 옮길 것, 두 번째가 도착할 곳이에요. ls notes처럼 ls 뒤에 폴더 이름을 주면 들어가지 않고도 그 안을 볼 수 있어요.")

o = head("s13-cp", "move", "실습 13 · 옮기고 지우기", "cp notes/memo.md plan.md")
o += terminal([("$", "~/kant|cp notes/memo.md plan.md"), ("$", "~/kant|ls"), ("o", "notes  plan.md"),
               ("$", "~/kant|cat plan.md"), ("o", "# hello")])
o += explain("파일을 하나 더 복사해요", "원본 notes/memo.md는 그대로 있어요.")
o += tree(COPY, cwd="kant", badges={"plan": [("복사본", "move")], "memo": [("원본", "info")]})
write("s13-cp", o, "cp는 copy예요. 순서는 mv와 같아요. notes/memo.md는 notes 폴더 안의 memo.md라는 상대 경로예요. 폴더를 통째로 복사할 땐 cp -r을 써요.")

o = head("s14-rename", "move", "실습 14 · 옮기고 지우기", "mv plan.md todo.md")
o += terminal([("$", "~/kant|mv plan.md todo.md"), ("$", "~/kant|ls"), ("o", "notes  todo.md")])
o += explain("같은 자리에서 mv 하면 이름이 바뀌어요", f"이름 바꾸는 명령은 따로 없어요. {code('mv 원래이름 새이름')}으로 해요.")
o += tree(RENAMED, cwd="kant", badges={"plan": [("이름 바뀜", "move")]})
write("s14-rename", o, "두 번째 자리에 폴더가 아니라 새 파일 이름을 주면 그 이름으로 옮겨져요. 결국 이름이 바뀐 것과 같아요. 같은 이름의 파일이 이미 있으면 묻지 않고 덮어쓰니 주의해요.")

GH_TODO = MOVED + [("plan", "todo.md", "ghost", 4)]
o = head("s15-rm", "move", "실습 15 · 옮기고 지우기", "rm todo.md")
o += terminal([("$", "~/kant|rm todo.md"), ("$", "~/kant|ls"), ("o", "notes")])
o += explain("파일을 지워요", "휴지통에 가지 않고 바로 사라져요.")
o += tree(GH_TODO, cwd="kant", badges={"plan": [("사라짐", "del")]})
write("s15-rm", o, "rm은 remove예요. 지웠다고 아무 말도 하지 않아요. 지운 뒤에는 ls로 확인해요.")

GH_NOTES = KANT + [("notes", "notes", "ghost", 4), ("memo", "memo.md", "ghost", 5)]
o = head("s16-rm-r", "move", "실습 16 · 옮기고 지우기", "rm -r notes")
o += terminal([("$", "~/kant|rm notes"), ("r", "rm: cannot remove 'notes': Is a directory"),
               ("$", "~/kant|rm -r notes"), ("$", "~/kant|ls"), ("#", "# 아무것도 없어요")])
o += explain("폴더는 rm -r로 지워요", "안에 든 파일까지 한꺼번에 사라져요.")
o += tree(GH_NOTES, cwd="kant", badges={"notes": [("사라짐", "del")], "memo": [("같이 사라짐", "del")]})
write("s16-rm-r", o, "폴더에 rm만 치면 Is a directory 에러로 막아 줘요. -r은 recursive, 안쪽까지 전부라는 뜻이에요. rm -rf는 다음 장에서 봐요.")

GH_OLD = KANT + [("old", "old", "ghost", 4), ("a", "a.md", "ghost", 5), ("b", "b.md", "ghost", 5)]
o = head("s16b-rm-rf", "move", "실습 16-2 · 옮기고 지우기", "rm -rf old")
o += terminal([("$", "~/kant|mkdir old"), ("$", "~/kant|touch old/a.md old/b.md"), ("$", "~/kant|ls old"), ("o", "a.md  b.md"),
               ("$", "~/kant|rm -rf old"), ("$", "~/kant|ls"), ("#", "# 아무것도 없어요"),
               ("$", "~/kant|rm -r old"), ("r", "rm: cannot remove 'old': No such file or directory"),
               ("$", "~/kant|rm -rf old"), ("#", "# 없어도 아무 말 없어요")], size=24)
o += explain("묻지도 알리지도 않고 지워요", f"{code('-r')}은 폴더 안까지 전부, {code('-f')}는 force, 강제로예요. 경고와 에러를 모두 건너뛰어요.")
o += tree(GH_OLD, cwd="kant", badges={"old": [("사라짐", "del")], "a": [("같이 사라짐", "del")], "b": [("같이 사라짐", "del")]})
write("s16b-rm-rf", o, "rm -rf는 -r과 -f를 합친 거예요. -f가 붙으면 없는 파일을 지워도 에러가 나지 않고, 지우기 어려운 파일도 묻지 않고 지워요. 그래서 실수해도 아무 신호가 없어요. 개발하다 보면 node_modules 같은 큰 폴더를 지울 때 자주 써요. 쓰기 전에 pwd와 ls로 위치와 이름을 꼭 확인해요.")

# ---------- 더 편하게 ----------
o = head("s17-ls-a", "extra", "실습 17 · 숨김 파일", "ls -a")
o += terminal([("$", "~/kant|git init"), ("o", "Initialized empty Git repository in /home/kim/kant/.git/"),
               ("$", "~/kant|ls"), ("#", "# 아무것도 안 보여요"), ("$", "~/kant|ls -a"), ("o", ".  ..  .git")], size=24)
o += explain("점(.)으로 시작하는 이름은 숨겨져요", "ls -a를 쳐야 보여요. Git의 .git 폴더도 숨김이에요.")
o += tree(KANT + [("git", ".git", "hidden", 4)], cwd="kant", badges={"git": [("숨김 폴더", "hide")]})
write("s17-ls-a", o, "-a는 all이에요. 맨 앞의 . 과 .. 은 지금 폴더와 한 칸 위 폴더를 뜻하는 기호예요. git init은 다음 단원에서 배울 Git 명령이에요. 여기서는 숨김 폴더를 하나 만드는 데만 써요. git init이 만든 .git 폴더는 숨김이라 그냥 ls로는 안 보여요.")

o = head("s18-ls-al", "extra", "실습 18 · 숨김 파일", "ls -al")
o += terminal([("$", "~/kant|touch README.md"), ("$", "~/kant|ls"), ("o", "README.md"), ("$", "~/kant|ls -al"),
               ("o", "total 12"), ("l", "drwxr-xr-x 3 kim kim 4096 Oct 28 04:28 ."), ("l", "drwxr-xr-x 5 kim kim 4096 Oct 28 04:28 .."),
               ("l", "drwxr-xr-x 7 kim kim 4096 Oct 28 04:28 .git"), ("l", "-rw-r--r-- 1 kim kim    0 Oct 28 04:28 README.md")], size=26)
o += explain("숨김까지 자세히 보여 줘요", f"{code('-a')}는 숨김까지, {code('-l')}은 자세히예요. 맨 앞이 {code('d')}면 폴더, {code('-')}면 파일이에요.")
o += tree(KANT + [("git", ".git", "hidden", 4), ("readme", "README.md", "file", 4)], cwd="kant",
          badges={"git": [("d · 폴더", "hide")], "readme": [("- · 파일", "new")]})
write("s18-ls-al", o, "ls -al은 ls -a -l을 합친 거예요. 순서를 바꿔 ls -la로 쳐도 같아요. 한 줄에 권한, 주인, 크기, 고친 시각, 이름이 나와요. 지금은 맨 앞 글자로 폴더와 파일을 구분하는 것만 알면 돼요. 빈 파일인 README.md는 크기가 0이에요. 날짜와 시각은 실행한 때에 따라 달라요.")

# ---------- 막힐 때 ----------
o = head("err-cd", "help", "막힐 때 1", "No such file or directory")
o += terminal([("$", "~/kant|cd notse"), ("r", "bash: cd: notse: No such file or directory"), ("$", "~/kant|ls"), ("o", "notes  todo.md")])
o += explain("그 이름이 지금 위치에 없어요", "오타인지, 다른 폴더에 있는지 ls로 확인해요.")
o += tree(RENAMED, cwd="kant", badges={"notes": [("진짜 이름", "info")]})
write("err-cd", o, "가장 많이 보는 에러예요. 원인은 둘 중 하나예요. 이름 오타이거나, 지금 위치가 생각과 달라요. pwd와 ls로 위치와 이름을 확인하고, 이름은 Tab으로 자동 완성해요.")

o = head("err-cmd", "help", "막힐 때 2", "command not found")
o += terminal([("$", "~/kant|sl"), ("r", "bash: sl: command not found"), ("$", "~/kant|ls"), ("o", "notes  todo.md")])
o += explain("명령 이름이 틀렸어요", "ls를 sl로 치는 오타가 흔해요. 설치하지 않은 프로그램을 불러도 같은 메시지가 나와요.")
o += tree(RENAMED, cwd="kant")
write("err-cmd", o, "명령 이름 자체를 못 찾았다는 뜻이에요. 철자를 먼저 확인해요. 철자가 맞는데도 나오면 그 프로그램이 설치되지 않은 거예요. 예를 들어 Python을 설치하기 전에 python3을 치면 이 메시지가 나와요.")

SPACE = KANT + [("folder", "folder", "dir", 4), ("my", "my", "dir", 4), ("notes", "notes", "dir", 4),
                ("memo", "memo.md", "file", 5), ("plan", "todo.md", "file", 4)]
o = head("err-space", "help", "막힐 때 3", "mkdir my folder")
o += terminal([("$", "~/kant|mkdir my folder"), ("$", "~/kant|ls"), ("o", "folder  my  notes  todo.md"),
               ("#", ""), ("#", "# 이렇게 고쳐요"), ("$", '~/kant|mkdir "my folder"'), ("$", "~/kant|ls"), ("o", "'my folder'")])
o += explain("띄어쓰기는 이름을 둘로 나눠요", "따옴표로 묶거나, 처음부터 my-folder처럼 띄어쓰기 없이 지어요.")
o += tree(SPACE, cwd="kant", badges={"folder": [("따로 생김", "del")], "my": [("따로 생김", "del")]})
write("err-space", o, "터미널은 띄어쓰기를 기준으로 단어를 나눠요. 그래서 my와 folder 두 폴더가 생겨요. 아래 고친 예시는 잘못 만든 두 폴더를 지운 뒤 실행한 결과예요. 이름에 띄어쓰기를 넣지 않는 게 가장 편해요. 하이픈이나 밑줄을 써요.")
