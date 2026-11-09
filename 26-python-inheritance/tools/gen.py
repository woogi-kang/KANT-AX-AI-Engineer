"""Generates every slide of the inheritance and class variable deck (26) and slides/deck.json.

Story: picks up the Bread class from chapters 24 and 25 for class variables, and uses the classic Animal, Dog and Cat
classes for inheritance (2026-11-09, Memoriz: the 붕어빵 inheritance examples were too hard). Part 1 shows Dog and Cat
written by copying. Part 2 puts shop and count on the Bread class (class variables). Part 3 inherits Animal with pass,
adds fetch, overrides speak, calls super().eat(), adds breed with super().__init__ and mixes animals in one list
(isinstance). Part 4 compares copying with inheriting and the "is a kind of" test. Part 5 collects the usual errors, and
part 6 is a stamp card with a VIP card and a 붕어빵 menu with mini 붕어빵.
Every cell and output comes from tools/demo.sh (tools/run_nb.py runs the cells with the project kernel).

Layout rules (2026-11-08 remake, from the Stageshow skill and tools/DESIGN.md):
- one focal object per slide, usually the code cell drawn at 30px; pictures beside it stay smaller
- terms sit on the picture or beside the code line as leader tags (tag()), not in separate cards
- say it once: what the speaker note already says is not repeated on the slide
- no empty bands: the focal object grows to fill the slide
- a fix is drawn as the wrong line struck through and the right line under it (fix())
- changing values move: fly() from the code line, stacked counters that roll up
Highlights vary by slide (tools/HIGHLIGHT.md, 2026-11-09 player): line tints, leader tags with DELAY, fly, spot, line spotlight,
run band with changing values (text), code-output links, color pairs and changed letters (MARK), code morph for fixes,
STAGGER and DIM for lists, WIPE for arrows, pen box, cursor, pulse, one shake (the AttributeError), SLAM and shine on the cover.
Usage: python3 tools/gen.py slides
"""

import html, json, os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from highlight import (spot, spot_off, cursor, cursor_off, ring, box, underline, lspot, lspot_off, run, run_off, text,  # noqa: E402
                       link, _svg, pulse, shake, shine, SLAM, STAGGER, DIM, DELAY, WIPE, MARK, MORPH, MORPH_FROM, tok)

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
INK, SUB, LINE, CARD = "#1D2330", "#4A5262", "#E1DED6", "#FFFFFF"
BL, GR, OR, PUR, RED, TEAL, GRAY = "#2459C9", "#1F8A4C", "#B26A00", "#5A3BB8", "#A33131", "#0F7C86", "#6A7180"
JP = "#B8560F"          # Jupyter, same as chapters 09 and 10
SEL = "#2F7DE1"         # selected cell bar, like VS Code's focus color
NB = "basics.ipynb"
K1, K1BG = "#1E5FA8", "#E5EEF8"
K2, K2BG = "#A0620A", "#F7EEDD"
K3, K3BG = TEAL, "#E2F2F3"
K4, K4BG = "#A23B72", "#F6E7EF"
K5, K5BG = RED, "#F8E6E6"
K6, K6BG = PUR, "#ECE7F8"
BR, BRBG = "#9A5B13", "#FBF0E0"      # 붕어빵 (an object)
MD, MDBG = "#5B4636", "#EFE8DF"      # 틀 (the class)
CR, CRBG = "#2F7D6B", "#E3F2EE"      # child class (Dog)
W_ = "#E6E9EF"
REAL = " 출력은 실제로 실행한 결과예요."


def e(s):
    return html.escape(s, quote=False)


def p(style, text, attrs=""):
    return f'<p{attrs} style="{style}">{text}</p>'


ORDER, SECTIONS = [], {}


def W(sid, parts, notes, section=None):
    if section:
        SECTIONS[section[0]] = {"description": section[1], "start": sid}
    ORDER.append(sid)
    with open(os.path.join(OUT, sid + ".html"), "w") as f:
        f.write("\n".join(parts) + f"\n<aside>{e(notes)}</aside>\n</section>\n")


def sec(sid, transition="fade", bg="#F6F5F1"):
    return f'<section id="{sid}" data-transition="{transition}" style="background:{bg};color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">'


def head(eyebrow, title, color):
    return [p(f"position:absolute;left:96px;top:48px;width:1728px;font-size:26px;font-weight:700;color:{color}", e(eyebrow), ' id="eyebrow"'),
            f'<h2 id="title" style="position:absolute;left:96px;top:92px;width:1728px;font-size:56px;font-weight:700;line-height:1.2;color:{INK}">{title}</h2>']


def at(order, anim="rise"):
    return f' data-build-in="{anim} order {order}"' if order else ""


def caption(text, top=944, order=None):
    a = at(order) if order else ' data-build-in="rise"'
    return p(f"position:absolute;left:96px;top:{top}px;width:1728px;font-size:34px;font-weight:700;line-height:1.4;color:{INK}", text, ' id="caption"' + a)


def num(i, color, size=56, extra=""):
    return p(f"width:{size + 16}px;height:{size + 16}px;flex:none;border-radius:50%;background:{color};color:#FFFFFF;font-size:{size * 0.6:.0f}px;font-weight:900;line-height:{size + 16}px;text-align:center;{extra}", str(i))


def kbd(text, size=30, color=INK):
    caps = [p(f"font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.2;white-space:nowrap;color:{color};background:#FFFFFF;border:2px solid #C9CED8;border-bottom-width:5px;border-radius:10px;padding:6px 14px", e(k)) for k in text.split("+")]
    plus = p(f"font-size:{size * 0.8:.0f}px;font-weight:700;color:{GRAY}", "+")
    return '<div style="display:flex;flex-direction:row;align-items:center;gap:8px">' + plus.join(caps) + '</div>'


# ---------- notebook cell, drawn at CFS[0] px ----------
CFS = [30]
HL = {"run": "rgba(31,138,76,0.16)", "skip": "rgba(106,113,128,0.18)", "err": "rgba(163,49,49,0.14)", "mark": "rgba(36,89,201,0.14)"}
HLT = {"run": GR, "skip": GRAY, "err": RED, "mark": BL}


def LHf():
    return CFS[0] * 1.45


def cell(c, left, top, w, attrs="", gut=True):
    """A Jupyter cell: [n] gutter, the code in a white box, then the output lines. Text starts at left+105."""
    fs, lines, n = CFS[0], c.get("lines", [""]), c.get("n")
    o = [f'<div id="{c["id"]}"{attrs or c.get("attrs", "")} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;display:flex;flex-direction:column;gap:10px">']
    bar = f'<div style="width:7px;flex:none;border-radius:4px;background:{SEL}"></div>'
    gutter = p(f"width:58px;flex:none;font-family:{MONO};font-size:22px;color:{GRAY};text-align:right;padding-top:12px", (f"[{n}]" if n else "") if gut else "")
    txt = "".join(p(f"font-family:{MONO};font-size:{fs}px;line-height:1.45;white-space:pre;color:{INK}", e(l) if l else "&#160;") for l in lines)
    box_ = f'<div style="flex:1;position:relative;background:#FFFFFF;border:2px solid {LINE};border-radius:10px;padding:8px 18px 8px;display:flex;flex-direction:column">{txt}</div>'
    o.append(f'<div style="display:flex;flex-direction:row;gap:10px;align-items:stretch">{bar}{gutter}{box_}</div>')
    if c.get("out"):
        col = lambda l: RED if c.get("err") and re.match(r"[A-Za-z]+(Error|Interrupt)", l) else INK
        oid = lambda j: f' id="{c["oid"]}"' if c.get("oid") and j == 0 else ""
        o.append(''.join(p(f"margin-left:85px;padding:0 20px;font-family:{MONO};font-size:{fs}px;line-height:1.45;white-space:pre;color:{col(l)}", e(l) if l else "&#160;", oid(j)) for j, l in enumerate(c["out"])))
    o.append('</div>')
    return o


def cell_h(c):
    return 20 + len(c.get("lines", [""])) * LHf() + len(c.get("out", [])) * (LHf() + 10)


def hl(left, top, w, i, n=1, kind="run", order=1, anim="fade"):
    """Tints code lines i..i+n-1 of a cell drawn at (left, top) with width w."""
    y = top + 10 + i * LHf()
    return f'<div{at(order, anim)} style="position:absolute;left:{left + 87}px;top:{y:.2f}px;width:{w - 89}px;height:{n * LHf():.2f}px;background:{HL[kind]};border-radius:6px"></div>'


def ly(top, i):
    """Center y of code line i in a cell drawn at top."""
    return top + 10 + i * LHf() + LHf() / 2


def oy(top, n, j):
    """Center y of output line j of a cell with n code lines."""
    return top + 20 + n * LHf() + 10 + j * (LHf() + 10) + LHf() / 2


def tw(s, fs=None):
    """Rendered width of a code string: Hangul is about one em, the rest 0.6 em."""
    f = fs or CFS[0]
    return sum(f * (1.0 if '가' <= ch <= '힣' else 0.6) for ch in s)


def tx(left, lines, gap=36):
    """x just right of the longest of the given lines (code or output) of a cell at left."""
    return int(left + 105 + max(tw(l) for l in lines) + gap)


def tag(x, y, text, color, order=None, size=28, lead=True, anim="fade", w=None, ex=""):
    """A leader label '← text' centred on y. No box."""
    ws = f"width:{w}px;white-space:pre-line;" if w else "white-space:nowrap;"
    return p(f"position:absolute;left:{x}px;top:{y - size * 0.725:.0f}px;{ws}font-size:{size}px;font-weight:700;line-height:1.45;color:{color}", ("← " if lead else "") + e(text), at(order, anim) + ex)


def bracket(x, y1, y2, color, order=None):
    """A thin ] bracket from y1 to y2, for a tag that covers several lines."""
    return f'<div{at(order, "fade")} style="position:absolute;left:{x}px;top:{y1:.0f}px;width:14px;height:{y2 - y1:.0f}px;border:4px solid {color};border-left:none;border-radius:0 8px 8px 0"></div>'


def src(sid, x, y, w, h):
    """An invisible box that a fly build starts from (usually a spot on a code line)."""
    return f'<div id="{sid}" style="position:absolute;left:{x:.0f}px;top:{y:.0f}px;width:{w:.0f}px;height:{h:.0f}px"></div>'


def arrow(w=60, color="#C9CED8"):
    return f'<x-shape kind="arrow-right" style="width:{w}px;height:30px;flex:none;background:{color}"></x-shape>'


def harrow(left, top, w, color="#C9CED8", attrs="", rot=0):
    r = f"transform:rotate({rot}deg);" if rot else ""
    return f'<x-shape{attrs} kind="arrow-right" style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:30px;{r}background:{color}"></x-shape>'


def fix(left, top, bad, good, order, size=30, w=1728, mark=None):
    """The wrong line struck through, an arrow, the right line, on one row.
    mark=(start, end, order): those characters of the right line get a tint that fades in (MARK) on that step."""
    gd = e(good)
    if mark:
        a0, a1, mo = mark
        gd = e(good[:a0]) + f'<span{MARK(mo)} style="background:#FFE08A;border-radius:6px">{e(good[a0:a1])}</span>' + e(good[a1:])
    return (f'<div{at(order)} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;display:flex;flex-direction:row;align-items:center;gap:22px">'
            + p(f"font-size:{size}px;font-weight:900;color:{RED}", "✕")
            + p(f"font-family:{MONO};font-size:{size}px;font-weight:700;color:{RED};text-decoration:line-through;text-decoration-thickness:3px;white-space:pre", e(bad))
            + arrow(70)
            + p(f"font-size:{size}px;font-weight:900;color:{GR}", "✓")
            + p(f"font-family:{MONO};font-size:{size}px;font-weight:700;color:{INK};background:#E6F4EC;border:3px solid {GR};border-radius:14px;padding:6px 20px;white-space:pre", gd) + '</div>')


def fixv(left, top, w, bad, good, order, size=26, label=None):
    """The same fix stacked: the wrong line struck through, the right line under it."""
    lab = p(f"font-size:26px;font-weight:700;color:{GR}", e(label)) if label else ""
    badrow = (f'<div style="display:flex;flex-direction:row;align-items:center;gap:16px">' + p(f"width:30px;flex:none;font-size:{size}px;font-weight:900;color:{RED}", "✕")
              + p(f"font-family:{MONO};font-size:{size}px;font-weight:700;color:{RED};text-decoration:line-through;text-decoration-thickness:3px;white-space:pre", e(bad)) + '</div>') if bad else ""
    return (f'<div{at(order)} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;display:flex;flex-direction:column;gap:14px">' + lab + badrow
            + '<div style="display:flex;flex-direction:row;align-items:center;gap:16px">' + p(f"width:30px;flex:none;font-size:{size}px;font-weight:900;color:{GR}", "✓")
            + p(f"font-family:{MONO};font-size:{size}px;font-weight:700;color:{INK};background:#E6F4EC;border:3px solid {GR};border-radius:14px;padding:6px 18px;white-space:pre", e(good)) + '</div></div>')


# ---------- class pictures (shared look with chapters 24 and 25) ----------
def over(left, top, i, pre, txt, color, order, fs=None):
    """Code text drawn exactly over line i of a cell at (left, top), starting after the characters pre.
    With MARK the color fades in on its step; before that it reads as the plain line under it."""
    f = fs or CFS[0]
    return p(f"position:absolute;left:{left + 105 + tw(pre, f):.1f}px;top:{top + 10 + i * LHf():.1f}px;font-family:{MONO};font-size:{f}px;line-height:1.45;white-space:pre;color:{color}",
             e(txt), MARK(order))


def clink(order, left, top, n, i, j, code, out, X, color=BL):
    """A pen curve from the end of code line i to the end of output line j of a cell with n code lines.
    It bows out to x = X, right of every line it passes, so it never crosses text."""
    x1, y1 = left + 105 + tw(code) + 14, ly(top, i)
    x2, y2 = left + 105 + tw(out) + 14, oy(top, n, j)
    return _svg(order, f'<path d="M{x1:.0f},{y1:.0f} C{X:.0f},{y1:.0f} {X:.0f},{y2:.0f} {x2:.0f},{y2:.0f}"/>', color, 4)


def mfix(left, top, sid, bad, good, order, size=30, label=None):
    """A fix drawn as a code morph: the wrong line (pieces from tok()) changes into the right one in place.
    bad and good are lists of (key or None, text). The PDF shows only the right line."""
    def body(parts, col):
        return "".join(tok(k, e(t)) if k else f'<span style="display:inline-block">{e(t)}</span>' for k, t in parts)
    st = f"position:absolute;left:{left + 60}px;top:{top}px;font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.5;white-space:pre;padding:6px 20px;border-radius:14px;border:3px solid"
    o = [p(f"position:absolute;left:{left}px;top:{top + 10}px;font-size:{size}px;font-weight:900;color:{RED}", "✕", at(order - 1, "fade")),
         p(f"{st} transparent;color:{RED}", body(bad, RED), f' id="{sid}"' + at(order - 1, "fade") + MORPH_FROM()),
         p(f"position:absolute;left:{left}px;top:{top + 10}px;font-size:{size}px;font-weight:900;color:{GR};background:#F6F5F1", "✓", at(order, "fade")),
         p(f"{st} {GR};color:{INK};background:#E6F4EC", body(good, INK), MORPH(order, sid))]
    if label:
        o.insert(0, p(f"position:absolute;left:{left}px;top:{top - 46}px;font-size:26px;font-weight:700;color:{GR}", e(label), at(order, "fade")))
    return "".join(o)


def obj(name, rows, left, top, w=440, color=BR, bg=BRBG, cls="Bread", attrs="", sid=None, rh=60, empty=None, fs=28, vid=None):
    """A 붕어빵 (object) as a card: its name on a band, one line per attribute.
    rows: (attribute, value) or (attribute, value, row background). value None draws an empty dashed slot."""
    idp = f' id="{sid}"' if sid else ""
    vid = vid or {}
    o = [f'<div{idp}{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;background:{CARD};border:3px solid {color};border-radius:26px;display:flex;flex-direction:column;overflow:hidden">'
         + f'<div style="height:66px;flex:none;background:{color};display:flex;flex-direction:row;align-items:center;padding:0 24px;gap:14px">'
         + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:#FFFFFF", e(name))
         + '<div style="flex:1"></div>' + p(f"font-size:22px;font-weight:700;color:#FFFFFF;opacity:.9;white-space:nowrap", e(cls)) + '</div>'
         + '<div style="padding:14px 20px;display:flex;flex-direction:column;gap:8px">']
    if not rows:
        o.append(p(f"height:{rh}px;font-size:26px;color:{GRAY};line-height:{rh}px;text-align:center", e(empty or "아직 아무것도 없어요")))
    for r in rows:
        k, v = r[0], r[1]
        rb = r[2] if len(r) > 2 else bg
        miss = v is None
        o.append(f'<div style="height:{rh}px;display:flex;flex-direction:row;align-items:center;gap:14px;border-radius:12px;background:{"#FFFFFF" if miss else rb};border:2px {"dashed" if miss else "solid"} {RED if miss else LINE};padding:0 18px">'
                 + p(f"width:44%;flex:none;font-family:{MONO};font-size:{fs - 4}px;font-weight:700;color:{RED if miss else SUB};white-space:nowrap", e(k))
                 + p(f"flex:1;font-family:{MONO};font-size:{fs}px;font-weight:700;color:{RED if miss else INK};white-space:nowrap", e("없음" if miss else v), vid.get(k, "")) + '</div>')
    o.append('</div></div>')
    return "".join(o)


def obj_h(n, rh=60):
    return 66 + 28 + max(n, 1) * rh + (max(n, 1) - 1) * 8 + 6


def mold(left, top, w, title, lines, attrs="", color=MD, bg=MDBG, fs=30, tfs=34, sid=None, h=None, chip_txt="틀"):
    """A 붕어빵 틀 (class): a thick dashed frame, the class line on top, what it holds inside."""
    idp = f' id="{sid}"' if sid else ""
    hh = f"height:{h}px;" if h else ""
    body = "".join(p(f"font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:1.5;color:{INK};white-space:pre", e(l) if l else "&#160;") for l in lines)
    return (f'<div{idp}{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;{hh}background:{bg};border:6px dashed {color};border-radius:30px;padding:24px 34px;display:flex;flex-direction:column;gap:10px">'
            + '<div style="display:flex;flex-direction:row;align-items:center;gap:14px">' + p(f"font-size:22px;font-weight:700;color:#FFFFFF;background:{color};border-radius:10px;padding:4px 14px;white-space:nowrap", chip_txt)
            + p(f"font-family:{MONO};font-size:{tfs}px;font-weight:700;color:{color};white-space:pre", e(title)) + '</div>'
            + f'<div style="display:flex;flex-direction:column">{body}</div></div>')


def mold_h(n, fs=30, tfs=34):
    """Height of mold() with n body lines (6px border twice, 24px padding twice, title row, gap)."""
    return 12 + 48 + max(tfs * 1.4, 40) + 10 + n * fs * 1.5


def seg(parts, size=40):
    return p(f"font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.5;color:#E6E9EF;white-space:pre",
             "".join(f'<span style="color:{c}">{e(t)}</span>' for t, c in parts))


def rows_list(left, top, w, rows, widths, order0=1, rh=78, head_=None, fs=28, colors=None, anim="rise"):
    """A light table: gray header over a dark rule, rows split by thin rules, no boxes.
    Cells that look like code use the mono font. colors: optional color per column."""
    o = []
    y = top
    if head_:
        o.append(f'<div style="position:absolute;left:{left}px;top:{y}px;width:{w}px;height:52px;display:flex;flex-direction:row;align-items:center;gap:24px;border-bottom:3px solid {INK}">'
                 + "".join(p(f"width:{cw}px;flex:none;font-size:26px;font-weight:700;color:{(colors[k] if colors and colors[k] else GRAY)};white-space:nowrap", e(c)) for k, (c, cw) in enumerate(zip(head_, widths))) + '</div>')
        y += 52
    for i, r in enumerate(rows):
        cells_ = ""
        for k, (c, cw) in enumerate(zip(r, widths)):
            code = k > 0 and (re.fullmatch(r"[ -~]+", c) is not None or re.search(r'[A-Za-z_]\.|[\[\]"=(]', c) is not None)
            cells_ += p(f"width:{cw}px;flex:none;font-family:{MONO if code else SANS};font-size:{fs}px;font-weight:{700 if (k == 0 or code) else 500};color:{SUB if k == 0 else INK};white-space:pre", e(c))
        o.append(f'<div id="row-{top}-{i}"{at(order0 + i if order0 else None, anim)} style="position:absolute;left:{left}px;top:{y + i * rh}px;width:{w}px;height:{rh}px;display:flex;flex-direction:row;align-items:center;gap:24px;border-bottom:2px solid {LINE}">{cells_}</div>')
    return o


def finish(parts, toc_note, title):
    page = {sid: i + 1 for i, sid in enumerate(ORDER)}
    t = [f'<section id="toc" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
         f'<h2 style="position:absolute;left:96px;top:80px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>']
    t.append(f'<div{STAGGER(1, 90)} style="position:absolute;left:0;top:0;width:1920px;height:1080px">')
    for i, (c, h, s, a, b) in enumerate(parts):
        y = 212 + i * 118
        t.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:118px;display:flex;flex-direction:row;align-items:center;gap:36px;border-bottom:2px solid {LINE}">'
                 + p(f"width:60px;flex:none;font-size:56px;font-weight:900;color:{c}", str(i + 1))
                 + p(f"width:400px;flex:none;font-size:38px;font-weight:700;color:{INK}", e(h))
                 + p(f"flex:1;font-size:28px;color:{SUB}", e(s))
                 + p(f"width:130px;flex:none;text-align:right;font-size:28px;font-weight:700;color:{GRAY}", f"{page[a]}–{page[b]}쪽") + '</div>')
    t.append('</div>')
    t.append(p(f"position:absolute;left:96px;top:944px;width:1728px;font-size:28px;color:{SUB}", f"{page['ready']}쪽은 노트북 준비, {page['trouble']}–{page['cheatsheet']}쪽은 막힐 때와 한 장 요약이에요."))
    with open(os.path.join(OUT, "toc.html"), "w") as f:
        f.write("\n".join(t) + f"\n<aside>{e(toc_note)}</aside>\n</section>\n")
    deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-05T06:00:00Z"}, "lists": "css", "title": title, "order": ORDER,
            "sections": SECTIONS,
            "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                      "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
            "designSystems": []}
    with open(os.path.join(OUT, "deck.json"), "w") as f:
        json.dump(deck, f, ensure_ascii=False, indent=2)
    print(len(ORDER), "slides")


def cover(lines, h1, sub, note, accent="#F2B27A", h1size=92):
    cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
           f'<p style="font-size:28px;font-weight:700;color:{accent};letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
           f'<h1{SLAM(1)} style="font-size:{h1size}px;font-weight:900;line-height:1.1;color:#F6F5F1">{h1}</h1>',
           f'<p style="font-size:40px;line-height:1.4;color:#BFC6D4">{sub}</p>']
    cov.append('<div id="cov-code" style="position:absolute;left:880px;top:290px;width:920px;height:500px;background:#252B36;border-radius:24px;padding:44px 52px;display:flex;flex-direction:column;justify-content:center;gap:16px">')
    for line, c in lines:
        cov.append(p(f"font-family:{MONO};font-size:32px;font-weight:700;line-height:1.45;color:{c};white-space:pre", e(line) if line else "&#160;"))
    cov.append('</div>')
    cov.append(shine(1, "cov-code"))
    W("cover", cov, note, ("intro", "들어가기"))
    ORDER.append("toc")


EB1 = "1. 왜 필요한가"
EB2 = "2. 클래스 변수"
EB3 = "3. 상속"
EB4 = "4. 복사와 상속 비교"
EB5 = "5. 오류와 함정"
EB6 = "6. 실습"
B = ["class Bread:", "    def __init__(self, flavor, price):", "        self.flavor = flavor", "        self.price = price", "",
     "    def intro(self):", '        print(self.flavor, "붕어빵", self.price, "원")']
T = 210          # top of the content under the title


def lines_y(top, n):
    """Top and bottom y of n code lines starting at line i, for brackets: returns function i -> (y1, y2)."""
    return lambda i, k=1: (top + 10 + i * LHf() + 4, top + 10 + (i + k) * LHf() - 4)


def out_span(top, n, j, k=1):
    return (oy(top, n, j) - LHf() / 2 + 2, oy(top, n, j + k - 1) + LHf() / 2 - 2)


def chip(text, color, bg, fs=28, dashed=False, extra=""):
    bd = f"3px {'dashed' if dashed else 'solid'} {color}"
    return p(f"font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:1.3;color:{INK};background:{bg};border:{bd};border-radius:14px;padding:8px 20px;white-space:pre;{extra}", e(text))


def slot_row(left, top, label, items, order, lw=360, w=200, h=72, fs=26):
    """A row of parameter slots: items are (text, kind) with kind slot|auto|extra|value|missing."""
    sty = {"slot": (MD, MDBG, "solid", INK), "auto": (GR, "#E6F4EC", "solid", INK), "extra": (RED, K5BG, "solid", RED),
           "value": (BR, BRBG, "solid", INK), "missing": (RED, CARD, "dashed", RED)}
    o = [f'<div{at(order)} style="position:absolute;left:{left}px;top:{top}px;display:flex;flex-direction:row;align-items:center;gap:16px">'
         + p(f"width:{lw}px;flex:none;font-size:28px;font-weight:700;color:{SUB};white-space:nowrap", e(label))]
    for text, kind in items:
        c, b, ds, tc = sty[kind]
        o.append(p(f"width:{w}px;height:{h}px;flex:none;border:3px {ds} {c};background:{b};border-radius:14px;font-family:{MONO if text.isascii() else SANS};font-size:{fs}px;font-weight:700;line-height:{h - 6}px;text-align:center;color:{tc};white-space:nowrap", e(text)))
    o.append('</div>')
    return "".join(o)


def mini(left, top, name, order_new=None):
    """A small 붕어빵 for the 'every object sees the class' picture, with its shop label under it."""
    o = [f'<div style="position:absolute;left:{left}px;top:{top}px;width:150px;background:{CARD};border:3px solid {BR};border-radius:18px;overflow:hidden">'
         + p(f"height:40px;background:{BR};color:#FFFFFF;font-family:{MONO};font-size:24px;font-weight:700;line-height:40px;padding-left:16px", e(name))
         + f'<div style="padding:10px 12px;display:flex;flex-direction:column;gap:8px"><div style="height:20px;border-radius:6px;background:{BRBG}"></div><div style="height:20px;width:70%;border-radius:6px;background:{BRBG}"></div></div></div>']
    o.append(p(f"position:absolute;left:{left - 20}px;top:{top + 124}px;width:190px;text-align:center;font-size:26px;font-weight:700;color:{K2};background:#F6F5F1",
               "2호점" if order_new else "1호점", f' id="mini-{name}" data-start="1호점"' if order_new else ""))
    if order_new:
        o.append(text(order_new, f"mini-{name}", "2호점"))
    return "".join(o)


# ---------- cover ----------
cover([("class Bread:", "#C7B8F2"), ('    shop = "붕어빵 1호점"', "#F2C48D"), ("", W_), ("class Dog(Animal):", "#8FD8DE"), ("    def __init__(self, name, breed):", W_), ("        super().__init__(name)", "#B8E8BE"), ("        self.breed = breed", W_)],
      "클래스 3<br>상속과<br>클래스 변수", "틀에 새긴 값과<br>물려받는 클래스",
      "클래스 세 번째 챕터예요. 24에서 붕어빵 틀을 만들고, 25에서 print했을 때 보기 좋게 바꿨어요. 이번에는 두 가지를 배워요. 하나는 붕어빵마다 따로 들지 않고 틀 하나에 새겨서 모두 같이 쓰는 값, 클래스 변수예요. 다른 하나는 동물(Animal) 클래스를 물려받아 개(Dog)와 고양이(Cat) 클래스를 만드는 상속이에요. 같은 코드를 복사하지 않고 다른 점만 적는 방법이에요.", h1size=76)

# ---------- ready ----------
o = [sec("ready")] + head("들어가기", "25에서 이어서 해요", JP)
o.append(f'<div{STAGGER(1)} style="position:absolute;left:0;top:0;width:1920px;height:1080px">')
for i, (a_, b_) in enumerate([("class, __init__, self", "24"), ("메서드, a.intro()", "24"), ("__str__, __repr__", "25"), ("지역 변수와 전역 변수", "20"), ("for, 컴프리헨션", "13, 23")]):
    o.append(f'<div style="position:absolute;left:96px;top:{230 + i * 120}px;width:760px;height:104px;display:flex;flex-direction:row;gap:24px;align-items:center;border-bottom:2px solid {LINE}">'
             + f'<x-icon name="CheckCircle" style="width:48px;height:48px;color:{GR}"></x-icon>'
             + p(f"flex:1;font-family:{MONO if a_.isascii() else SANS};font-size:34px;font-weight:700;color:{INK}", e(a_))
             + p(f"font-size:30px;font-weight:700;color:{GRAY};white-space:nowrap", e(b_)) + '</div>')
o.append('</div>')
o.append(f'<div{STAGGER(2, 110)} style="position:absolute;left:0;top:0;width:1920px;height:1080px">')
o.append(p(f"position:absolute;left:1000px;top:256px;font-size:36px;font-weight:700;color:{JP}", "노트북 다시 열기"))
steps_ = [p(f"font-size:32px;color:{INK}", "VS Code로 hello-uv 폴더 열기"),
          p(f"font-size:32px;color:{INK}", "탐색기에서") + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{JP}", NB) + p(f"font-size:32px;color:{INK}", "열기"),
          p(f"font-size:32px;color:{INK}", "오른쪽 위 커널이 .venv인지 보기"),
          p(f"font-size:32px;color:{INK}", "셀에 적고") + kbd("Shift+Enter", 26) + p(f"font-size:32px;color:{INK}", "로 실행")]
for i, inner in enumerate(steps_):
    o.append(f'<div style="position:absolute;left:1000px;top:{352 + i * 120}px;width:824px;height:104px;display:flex;flex-direction:row;align-items:center;gap:18px">' + num(i + 1, JP, 40) + inner + '</div>')
o.append('</div>')
o.append(caption("기억이 안 나면 왼쪽에 적힌 챕터를 먼저 다시 봐요.", 900, 3))
W("ready", o, "09에서 만든 hello-uv 폴더를 VS Code로 열고, basics.ipynb를 다시 열어요. 24의 Bread 틀에서 이어서 해요. self와 __init__이 헷갈리면 24의 3파트를, __str__이 헷갈리면 25를 먼저 봐요. 클래스 변수를 볼 때 20의 전역 변수가 떠오를 거예요. 슬라이드의 출력은 tools/demo.sh가 hello-uv 커널에서 같은 셀을 실제로 실행한 결과예요.")

# ---------- part 1 ----------
o = [sec("w-why")] + head(EB1, "개와 고양이 클래스를 따로 만들면 같은 코드를 두 번 적어요", K1)
CFS[0] = 26
WD = ["class Dog:", "    def __init__(self, name):", "        self.name = name", "", "    def eat(self):", '        print(f"{self.name}가 밥을 먹어요")', "", "    def speak(self):", '        print(f"{self.name}가 멍멍 짖어요")', "", 'd = Dog("초코")', "d.speak()"]
WC = ["class Cat:", "    def __init__(self, name):", "        self.name = name", "", "    def eat(self):", '        print(f"{self.name}가 밥을 먹어요")', "", "    def speak(self):", '        print(f"{self.name}가 야옹 울어요")', "", 'c = Cat("나비")', "c.speak()"]
FW = 846
for k, (left, L_, out_) in enumerate([(96, WD, "초코가 멍멍 짖어요"), (978, WC, "나비가 야옹 울어요")]):
    o += cell({"id": f"c-w{k + 1}", "lines": L_, "n": k + 1, "out": [out_]}, left, T, FW)
    o.append(hl(left, T, FW, 1, 5, "skip", 1))
    o.append(tag(tx(left, [L_[2]], 30), ly(T, 3), "두 클래스가 똑같아요", GRAY, 1, size=26, ex=DELAY(150 * k)))
    o.append(hl(left, T, FW, 7, 2, "mark", 2))
    o.append(tag(tx(left, ["    def speak(self):"], 30), ly(T, 7), "다른 건 여기뿐", BL, 2, size=26, ex=DELAY(150 * k)))
CFS[0] = 30
RY = 760
o.append(p(f"position:absolute;left:96px;top:{RY}px;font-size:30px;font-weight:700;color:{RED}", "동물이 늘수록 같은 코드도 늘어나요", at(3, "fade")))
o.append(f'<div{STAGGER(3, 110)} style="position:absolute;left:0;top:0;width:1920px;height:1080px">')
for i, nm in enumerate(["class Dog", "class Cat", "class Rabbit", "class Duck", "class Cow"]):
    o.append(f'<div style="position:absolute;left:{96 + i * 352}px;top:{RY + 60}px;width:320px;height:92px;border:3px dashed {GRAY};border-radius:18px;background:{CARD};display:flex;flex-direction:column;justify-content:center;padding:0 22px">'
             + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{INK}", e(nm)) + p(f"font-size:22px;color:{RED}", "__init__, eat 또 적기") + '</div>')
o.append('</div>')
W("w-why", o, "지금까지 배운 방법만으로 개와 고양이 클래스를 만들면 같은 코드를 두 번 적게 돼요. 이름을 붙이는 __init__과 밥 먹는 eat는 두 클래스가 한 글자도 다르지 않아요. 다른 건 우는 소리를 내는 speak뿐이에요. 밥 먹는 문구를 고치려면 두 클래스를 다 고쳐야 하고, 하나를 빼먹으면 서로 달라져요. 토끼, 오리, 소를 더하면 같은 코드를 그만큼 또 복사해요. 3파트의 상속이 이 문제를 풀어요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p1", "왜 필요한가"))

o = [sec("w-big")] + head(EB1, "틀에 새기는 값, 그리고 물려받는 클래스", K1)
M1 = mold_h(3)
o.append(mold(96, T, 760, "class Bread", ['shop = "붕어빵 1호점"', "__init__(flavor, price)", "intro()"], at(1)))
o.append(tag(96 + 40 + int(tw('shop = "붕어빵 1호점"')) + 30, T + 6 + 24 + 48 + 10 + 22, "클래스 변수", K2, 3))
o.append(harrow(880, T + int(M1 / 2) - 15, 100, BR, WIPE(2)))
o.append(obj("a", [("flavor", '"팥"'), ("price", "1000")], 1004, T, 390, attrs=at(2)))
o.append(obj("b", [("flavor", '"피자"'), ("price", "1500")], 1434, T, 390, attrs=at(2)))
o.append(tag(1004, T + obj_h(2) + 40, "a도 b도 틀의 shop을 같이 봐요", K2, 3, lead=False))
YA = 570
MA = mold_h(1, 28, 30)
o.append(mold(96, YA, 900, "class Animal", ["__init__(name), eat(), speak()"], at(4), fs=28, tfs=30, chip_txt="클래스"))
YK = int(YA + MA) + 80
for k, (x_, nm, ln, col, bg) in enumerate([(96, "class Dog(Animal)", "speak()  멍멍", CR, CRBG), (556, "class Cat(Animal)", "speak()  야옹", K1, K1BG)]):
    o.append(mold(x_, YK, 440, nm, [ln], at(5), color=col, bg=bg, fs=26, tfs=26, chip_txt="클래스"))
    o.append(harrow(x_ + 220 - 35, int(YA + MA + 45) - 15, 70, col, WIPE(5), rot=-90))
o.append(p(f"position:absolute;left:1100px;top:{YA + 40}px;font-size:34px;font-weight:700;color:{CR}", "물려받기 = 상속", at(5, "fade") + DELAY(250)))
o.append(tag(1100, YK + 40, "Dog와 Cat에는 speak만 적어요.\n__init__과 eat는 Animal에게서\n물려받아요.", INK, 6, lead=False, w=724, size=30))
W("w-big", o, "그림으로 먼저 봐요. 위는 2파트의 클래스 변수예요. 붕어빵 틀에 가게 이름을 새겨 두면, 찍은 붕어빵마다 따로 들고 있지 않아도 모두 틀에서 같이 봐요. 아래는 3파트의 상속이에요. Animal 클래스에 모든 동물이 같이 쓰는 __init__과 eat를 한 번만 적어요. Dog와 Cat은 Animal을 물려받아서, 다른 점인 speak만 적어요. 이렇게 물려받는 걸 상속이라고 해요. 화살표는 자식에서 부모 쪽을 가리켜요.")

# ---------- part 2 ----------
o = [sec("cv-basic")] + head(EB2, "틀에 바로 적은 값은 모든 붕어빵이 같이 봐요", K2)
CV1 = ["class Bread:", '    shop = "붕어빵 1호점"', "", "    def __init__(self, flavor, price):", "        self.flavor = flavor", "        self.price = price", "", 'a = Bread("팥", 1000)', 'b = Bread("슈크림", 1200)', "print(a.shop)", "print(b.shop)", "print(Bread.shop)"]
CW = 860
o += cell({"id": "c-cv1", "lines": CV1, "n": 1, "out": ["붕어빵 1호점", "붕어빵 1호점", "붕어빵 1호점"]}, 96, T, CW)
o.append(hl(96, T, CW, 1, 1, "mark", 1))
o.append(tag(tx(96, [CV1[1]], 30), ly(T, 1), "틀에 바로 적기", K2, 1, size=26))
y1, y2 = out_span(T, len(CV1), 0, 3)
OX = tx(96, ["붕어빵 1호점"], 24)
o.append(bracket(OX, y1, y2, K2, 4))
o.append(tag(OX + 30, (y1 + y2) / 2, "셋 다 틀의 값", K2, 4, lead=False))
RX, RW = 1010, 814
MH = mold_h(1)
o.append(mold(RX, T, RW, "class Bread", ['shop = "붕어빵 1호점"'], at(2)))
OY = 470
o.append(obj("a", [("flavor", '"팥"'), ("price", "1000")], RX, OY, 390, rh=56, fs=26, attrs=at(3)))
o.append(obj("b", [("flavor", '"슈크림"'), ("price", "1200")], RX + 424, OY, 390, rh=56, fs=26, attrs=at(3)))
for cx in (RX + 195, RX + 424 + 195):
    o.append(harrow(cx - 36, int((T + MH + OY) / 2) - 15, 72, K2, at(4, "fade"), rot=-90))
o.append(p(f"position:absolute;left:{RX + 245}px;top:{int((T + MH + OY) / 2) - 20}px;width:330px;text-align:center;font-size:26px;font-weight:700;color:{K2}", "shop은 틀에서 찾아요", at(4, "fade")))
SY = OY + obj_h(2, 56) + 40
for i, (n_, t_, r_, ok) in enumerate([("①", "a 안에서 shop 찾기", "없어요", False), ("②", "a를 찍은 틀 Bread에서 찾기", "붕어빵 1호점", True)]):
    o.append(f'<div{at(5 + i)}{DIM("look")} style="position:absolute;left:{RX}px;top:{SY + i * 80}px;width:{RW}px;height:80px;display:flex;flex-direction:row;align-items:center;gap:16px;border-bottom:2px solid {LINE}">'
             + p(f"width:40px;flex:none;font-size:30px;font-weight:900;color:{K2}", n_) + p(f"flex:1;font-size:28px;font-weight:700;color:{INK}", e(t_))
             + p(f"font-size:28px;font-weight:700;color:{GR if ok else RED};white-space:nowrap", ("✓ " if ok else "✕ ") + e(r_)) + '</div>')
W("cv-basic", o, "class 바로 아래, def 밖에 shop을 적었어요. self.이 없어요. 이렇게 틀에 적은 값을 클래스 변수라고 해요. 붕어빵 a와 b에는 shop 칸이 없지만 a.shop을 꺼내면 붕어빵 1호점이 나와요. 파이썬은 붕어빵에서 먼저 찾고, 없으면 그 붕어빵을 찍은 틀에서 찾아요. 틀 이름으로 Bread.shop이라고 꺼내도 같은 값이에요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p2", "클래스 변수"))

o = [sec("cv-change")] + head(EB2, "틀의 값을 바꾸면 모든 붕어빵에 한 번에 바뀌어요", K2)
CC = ['Bread.shop = "붕어빵 2호점"', "print(a.shop)", "print(b.shop)"]
o += cell({"id": "c-cv2", "lines": CC, "n": 2, "out": ["붕어빵 2호점", "붕어빵 2호점"]}, 96, T, 880)
o.append(hl(96, T, 880, 0, 1, "mark", 1))
o.append(tag(tx(96, [CC[0]], 30), ly(T, 0), "틀 이름으로 바꿔요", K2, 1, size=26))
VX = 96 + 105 + tw('Bread.shop = ')
o.append(src("cv2-src", VX, ly(T, 0) - 22, tw('"붕어빵 2호점"'), 44))
MX, MW = 1040, 784
o.append(mold(MX, T, MW, "class Bread", ['shop = "붕어빵 1호점"']))
MVX = MX + 40 + tw("shop = ")
o.append(p(f"position:absolute;left:{MVX - 6:.0f}px;top:{T + 6 + 24 + 48 + 10:.0f}px;font-family:{MONO};font-size:30px;font-weight:700;line-height:1.5;color:{K2};background:{MDBG};padding:0 6px;white-space:pre", e('"붕어빵 2호점"'), ' data-build-in="fly order 2" data-from="cv2-src"'))
MB = T + mold_h(1)
xs = [96 + 20 + round(i * (1728 - 190) / 7) for i in range(8)]
lines_svg = "".join(f'<line x1="{MX + MW / 2:.0f}" y1="{MB:.0f}" x2="{x + 75}" y2="690" stroke="#C9CED8" stroke-width="3" stroke-dasharray="8 8"/>' for x in xs)
o.append(f'<svg style="position:absolute;left:0;top:0;width:1920px;height:1080px" viewBox="0 0 1920 1080">{lines_svg}</svg>')
for i, x in enumerate(xs):
    o.append(mini(x, 690, "abcdefgh"[i], 3))
o.append(caption("붕어빵이 100개여도 Bread.shop 한 줄이면 돼요.", 900, 4))
W("cv-change", o, "가게를 옮겼어요. Bread.shop 한 줄만 바꿨는데 a와 b 모두 2호점이 나와요. 붕어빵들이 각자 들고 있는 게 아니라 틀 하나를 같이 보고 있기 때문이에요. 1파트의 복사한 코드처럼 붕어빵마다 self.shop을 따로 넣었다면 붕어빵 수만큼 바꿔야 했어요. 클래스 변수를 바꿀 땐 꼭 틀 이름으로 바꿔요. 붕어빵 이름으로 바꾸면 어떻게 되는지는 5파트에서 봐요." + REAL)

o = [sec("cv-count")] + head(EB2, "찍을 때마다 틀에 개수를 세요", K2)
CV3 = ["class Bread:", "    count = 0", "", "    def __init__(self, flavor, price):", "        self.flavor = flavor", "        self.price = price", "        Bread.count = Bread.count + 1", "", 'a = Bread("팥", 1000)', 'b = Bread("슈크림", 1200)', 'c = Bread("피자", 1500)', "print(Bread.count)"]
CW = 960
o += cell({"id": "c-cv3", "lines": CV3, "n": 3, "out": ["3"]}, 96, T, CW)
o.append(hl(96, T, CW, 6, 1, "mark", 1))
o.append(tag(tx(96, [CV3[6]], 20), ly(T, 6), "틀에 +1", K2, 1, size=26))
RX, RW = 1100, 724
o.append(f'<div style="position:absolute;left:{RX}px;top:{T}px;width:{RW}px;height:250px;background:{CARD};border:3px solid {K2};border-radius:26px;overflow:hidden">'
         + p(f"position:absolute;left:32px;top:22px;font-family:{MONO};font-size:30px;font-weight:700;color:{K2}", "Bread.count")
         + p(f"position:absolute;left:0;top:70px;width:{RW - 6}px;height:170px;text-align:center;font-family:{MONO};font-size:136px;font-weight:700;line-height:170px;color:{INK}", "3", ' id="cnt" data-start="0"')
         + '</div>')
for k, ln in enumerate([8, 9, 10]):
    o.append(run(k + 2, 96 + 87, T + 10 + ln * LHf(), CW - 89, LHf()))
    o.append(text(k + 2, "cnt", str(k + 1)))
    o.append(f'<div{at(k + 2)} style="position:absolute;left:{RX}px;top:{T + 290 + k * 84}px;width:{RW}px;height:84px;display:flex;flex-direction:row;align-items:center;gap:20px;border-bottom:2px solid {LINE}">'
             + p(f"flex:1;font-family:{MONO};font-size:28px;font-weight:700;color:{INK};white-space:pre", e(CV3[ln]))
             + p(f"font-size:28px;font-weight:700;color:{K2};white-space:nowrap", f"+1 → {k + 1}") + '</div>')
o.append(run_off(5))
o.append(caption("가게 이름, 전체 개수처럼 틀 전체에 하나만 있으면 되는 값에 써요.", 900, 5))
W("cv-count", o, "클래스 변수로 지금까지 찍은 붕어빵 수를 세요. count는 틀에 0으로 시작하고, __init__ 안에서 Bread.count에 1을 더해요. 24에서 본 것처럼 __init__은 찍을 때마다 불리니까, 세 번 찍으면 3이 돼요. 붕어빵 하나하나가 아니라 틀 전체에 하나만 있으면 되는 값에 클래스 변수를 써요. 더할 때도 self.count가 아니라 Bread.count로 적은 걸 보세요. 이유는 5파트에서 봐요." + REAL)

o = [sec("cv-table")] + head(EB2, "클래스 변수와 인스턴스 변수", K2)
CWS = [300, 680, 676]
TR = [["어디에 적나요", "__init__ 안, self.flavor = ...", 'class 바로 아래, shop = ...'],
      ["누구 것인가요", "붕어빵 하나하나 (객체)", "틀 하나 (클래스)"],
      ["몇 개 있나요", "붕어빵 수만큼", "틀에 하나"],
      ["꺼내기", "a.flavor", "a.shop, Bread.shop"],
      ["바꾸기", "a.flavor = ...", "Bread.shop = ..."],
      ["예", "맛, 가격, 도장 수", "가게 이름, 전체 개수"]]
o += rows_list(96, T, 1728, TR, CWS, order0=None, rh=96, head_=["", "인스턴스 변수", "클래스 변수"], fs=30, colors=[None, BR, MD])
for i in range(len(TR)):
    o.append(spot(i + 1, 96, T + 52 + i * 96, 1728, 96, pad=6, r=12))
o.append(spot_off(len(TR) + 1))
o.append(caption("인스턴스는 객체와 같은 말이에요. 붕어빵마다 다르면 self.이름, 모두 같으면 틀에 적어요.", 880, len(TR) + 1))
W("cv-table", o, "두 가지 변수를 표로 비교해요. 한 줄씩 비춰 가며 읽어요. 24에서 self.flavor처럼 붕어빵에 붙인 값은 인스턴스 변수예요. 인스턴스는 객체와 같은 말로, 틀로 찍은 붕어빵 하나를 뜻해요. 붕어빵 수만큼 따로 있어요. 틀에 바로 적은 shop은 클래스 변수예요. 틀에 하나만 있고 모두가 같이 봐요. 20의 지역 변수, 전역 변수와 비슷하게 보이지만, 클래스 변수는 틀 안에 묶여 있어요. 붕어빵마다 다른 값이면 self.이름으로, 모두 같은 값이면 틀에 적어요.")


# ---------- part 3 ----------
AN = ["class Animal:", "    def __init__(self, name):", "        self.name = name", "", "    def eat(self):", '        print(f"{self.name}가 밥을 먹어요")', "",
      "    def speak(self):", '        print(f"{self.name}가 소리를 내요")']
o = [sec("in-pass")] + head(EB3, "괄호에 부모 클래스를 적으면 전부 물려받아요", K3)
o += cell({"id": "c-i0", "lines": AN, "n": 1}, 96, T, 900)
o.append(tag(tx(96, [AN[2]], 30), ly(T, 3), "모두 같이 쓰는 것", MD, 1))
IP = ["class Dog(Animal):", "    pass", "", 'd = Dog("초코")', "d.eat()", "d.speak()"]
OP = ["초코가 밥을 먹어요", "초코가 소리를 내요"]
RX0, RW0 = 1040, 784
o += cell({"id": "c-i1", "lines": IP, "n": 2, "out": OP}, RX0, T, RW0)
o.append(hl(RX0, T, RW0, 0, 2, "run", 1))
o.append(tag(tx(RX0, [IP[0]], 30), ly(T, 0), "괄호에 부모 클래스", K3, 1))
o.append(over(RX0, T, 0, "class Dog(", "Animal", MD, 2))
o.append(over(RX0, T, 0, "class ", "Dog", CR, 2))
y1, y2 = out_span(T, len(IP), 0, 2)
OX = tx(RX0, OP, 24)
o.append(bracket(OX, y1, y2, CR, 4))
o.append(tag(OX + 30, (y1 + y2) / 2, "pass뿐인데\n둘 다 돼요", CR, 4, lead=False, w=220))


def role_mold(left, top, w, title, lines, role, color, bg, attrs, fs=28):
    return (mold(left, top, w, title, lines, attrs, color=color, bg=bg, fs=fs, tfs=30, chip_txt="클래스")
            + p(f"position:absolute;left:{left + w - 150}px;top:{top - 40}px;width:120px;text-align:right;font-size:24px;font-weight:700;color:{color}", e(role), attrs))


PY = 690
MP = mold_h(2, 28, 30)
o.append(role_mold(96, PY, 560, "Animal", ["__init__(name)", "eat(), speak()"], "부모", MD, MDBG, at(2)))
o.append(harrow(676, int(PY + MP / 2) - 15, 90, CR, WIPE(2), rot=180))
o.append(p(f"position:absolute;left:668px;top:{int(PY + MP / 2) + 26}px;width:110px;text-align:center;font-size:24px;font-weight:700;color:{CR}", "물려받기", at(2, "fade")))
o.append(role_mold(786, PY, 420, "Dog(Animal)", ["pass"], "자식", CR, CRBG, at(2)))
o.append(harrow(1226, int(PY + MP / 2) - 15, 90, CR, WIPE(3)))
o.append(obj("d", [("name", '"초코"')], 1336, PY, 488, cls="Dog", color=CR, bg=CRBG, attrs=at(3)))
W("in-pass", o, "상속은 class 이름 뒤 괄호에 물려받을 클래스를 적으면 돼요. 먼저 모든 동물이 같이 쓰는 Animal 클래스를 만들었어요. Dog 안에는 pass만 있어서 아무것도 적지 않았어요. 그런데도 이름을 넣어 만들 수 있고, eat와 speak도 불러져요. 부모 클래스 Animal의 __init__, eat, speak를 그대로 물려받았기 때문이에요. 물려주는 클래스를 부모 클래스, 물려받는 클래스를 자식 클래스라고 불러요. 개가 \"소리를 내요\"라고 하는 건 어색하죠. 두 장 뒤에서 멍멍으로 바꿔요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p3", "상속"))

o = [sec("in-add")] + head(EB3, "자식 클래스에는 더 할 일을 적어요", K3)
IA = ["class Dog(Animal):", "    def fetch(self):", '        print(f"{self.name}가 공을 물어 와요")', "", 'a = Animal("하마")', 'd = Dog("초코")', "d.eat()", "d.fetch()"]
OA = ["초코가 밥을 먹어요", "초코가 공을 물어 와요"]
FW = 1150
o += cell({"id": "c-i2", "lines": IA, "n": 3, "out": OA}, 96, T, FW)
o.append(hl(96, T, FW, 1, 2, "mark", 1))
o.append(bracket(96 + FW + 18, *lines_y(T, 8)(1, 2), BL, 1))
o.append(tag(96 + FW + 46, ly(T, 1.5), "Dog에만 있는 메서드", BL, 1, lead=False))
LX = tx(96, OA, 50)
o.append(clink(2, 96, T, 8, 6, 0, IA[6], OA[0], LX, MD))
o.append(clink(2, 96, T, 8, 7, 1, IA[7], OA[1], LX + 30, BL))
o.append(tag(LX + 60, oy(T, 8, 0.5), "eat는 부모에게서, fetch는 자기 클래스에서", CR, 2, ex=DELAY(400)))
T2 = int(T + cell_h({"lines": IA, "out": OA})) + 50
ERR = "AttributeError: 'Animal' object has no attribute 'fetch'"
o += cell({"id": "c-i3", "lines": ["a.fetch()"], "n": 4, "out": [ERR], "err": True, "attrs": at(3)}, 96, T2, FW)
o.append(box(3, 186, int(oy(T2, 1, 0) - 28), int(tw(ERR)) + 30, 56, RED))
o.append(tag(201 + int(tw(ERR)) + 44, oy(T2, 1, 0), "a는 Animal로 만들었어요", RED, 3))
o.append(caption("물려받기는 부모에서 자식 쪽으로만 일어나요. 모든 동물이 공을 물어 오지는 않아요.", 920, 4))
W("in-add", o, "자식 클래스에 새 메서드를 더해요. 공을 물어 오는 건 개만 하니까 Dog에 fetch를 적었어요. d는 부모에게서 물려받은 eat와 자기 클래스의 fetch를 둘 다 쓸 수 있어요. 앞 셀의 Animal을 그대로 쓰고 있어요. 반대로 하마 a는 부모 클래스 Animal로 만들어서 fetch가 없어요. 물려받기는 부모에서 자식 쪽으로만 일어나요." + REAL)

o = [sec("in-over")] + head(EB3, "같은 이름의 메서드를 다시 적으면 자식 것이 쓰여요", K3)
CFS[0] = 28
OD = ["class Dog(Animal):", "    def speak(self):", '        print(f"{self.name}가 멍멍 짖어요")', "", 'd = Dog("초코")', "d.speak()"]
OC = ["class Cat(Animal):", "    def speak(self):", '        print(f"{self.name}가 야옹 울어요")', "", 'c = Cat("나비")', "c.speak()"]
FW = 846
for k, (left, L_, out_, col, nm) in enumerate([(96, OD, "초코가 멍멍 짖어요", CR, "Dog"), (978, OC, "나비가 야옹 울어요", K1, "Cat")]):
    o += cell({"id": f"c-i4{k}", "lines": L_, "n": 5 + k, "out": [out_]}, left, T, FW)
    o.append(hl(left, T, FW, 1, 2, "run", 1))
    o.append(tag(tx(left, [L_[1]], 30), ly(T, 1), "부모에도 있는 이름", GR, 1, size=26, ex=DELAY(150 * k)))
    o.append(underline(2 + k, left + 105, left + 105 + int(tw(out_)), int(oy(T, 6, 0) + 22), col))
    o.append(tag(tx(left, [out_], 30), oy(T, 6, 0), f"{nm}의 speak", col, 2 + k, size=26))
T2 = int(T + cell_h({"lines": OD, "out": [1]})) + 40
o += cell({"id": "c-i46", "lines": ["a.speak()"], "n": 7, "out": ["하마가 소리를 내요"], "attrs": at(4)}, 96, T2, FW)
o.append(tag(tx(96, ["하마가 소리를 내요"], 30), oy(T2, 1, 0), "Animal의 speak 그대로", MD, 4, size=26))
CFS[0] = 30
LY = 760
o.append(f'<div{STAGGER(5, 160)} style="position:absolute;left:0;top:0;width:1920px;height:1080px">')
for i, (call, steps) in enumerate([("d.speak()", [("Dog에서 찾았어요", CR, CRBG, False), ("Animal은 안 봐요", GRAY, CARD, True)]),
                                   ("a.speak()", [("Animal에서 찾았어요", MD, MDBG, False)])]):
    row = p(f"width:200px;flex:none;font-family:{MONO};font-size:30px;font-weight:700;color:{INK}", e(call))
    for t_, c_, b_, dash in steps:
        row += arrow(50) + p(f"font-size:28px;font-weight:700;color:{c_};background:{b_};border:3px {'dashed' if dash else 'solid'} {c_};border-radius:14px;padding:6px 20px;white-space:nowrap", e(t_))
    o.append(f'<div style="position:absolute;left:96px;top:{T2 + 170 + i * 84}px;height:64px;display:flex;flex-direction:row;align-items:center;gap:16px">{row}</div>')
o.append('</div>')
o.append(caption("메서드는 자식 클래스에서 먼저 찾고, 없으면 부모 클래스로 올라가요.", 940, 5))
W("in-over", o, "부모에게 물려받은 메서드와 같은 이름으로 자식 클래스에 다시 적으면, 자식 것이 쓰여요. 이걸 덮어쓰기라고 해요. 개는 멍멍, 고양이는 야옹으로 speak를 다시 적었어요. 파이썬은 메서드를 찾을 때 자식 클래스부터 보고, 없으면 부모 클래스로 올라가요. d는 Dog에 speak가 있어서 그걸 쓰고 Animal까지 가지 않아요. 하마 a는 Animal로 만들었으니 원래 speak를 써요." + REAL)

o = [sec("in-supm")] + head(EB3, "super()로 부모 것을 부르고 조금만 더할 수도 있어요", K3)
IS3 = ["class Dog(Animal):", "    def eat(self):", "        super().eat()", '        print(f"{self.name}가 꼬리를 흔들어요")', "", 'd = Dog("초코")', "d.eat()"]
FW = 1728
OUTS = ["초코가 밥을 먹어요", "초코가 꼬리를 흔들어요"]
o += cell({"id": "c-i6", "lines": IS3, "n": 8, "out": OUTS}, 96, T, FW)
o.append(hl(96, T, FW, 2, 1, "run", 1))
o.append(tag(tx(96, [IS3[3]], 40), ly(T, 2), "super()는 부모 클래스. 부모의 eat를 그대로 불러요", GR, 1))
o.append(hl(96, T, FW, 3, 1, "mark", 2))
o.append(tag(tx(96, [IS3[3]], 40), ly(T, 3), "한 줄만 더해요", BL, 2))
OX = tx(96, OUTS, 40)
o.append(tag(OX, oy(T, 7, 0), "Animal의 eat가 찍은 줄", GR, 3, ex=DELAY(200)))
o.append(tag(OX, oy(T, 7, 1), "Dog가 더한 줄", BL, 3, ex=DELAY(200)))
RY = int(T + cell_h({"lines": IS3, "out": OUTS})) + 50
o += rows_list(96, RY, 1728, [["eat", "super().eat()", "부모의 eat 부르기"], ["__init__", "super().__init__(name)", "부모의 __init__ 부르기 (다음 장)"]], [200, 760, 700], order0=4, rh=72, fs=28)
W("in-supm", o, "앞 장처럼 메서드를 통째로 다시 적으면 부모 것은 안 쓰여요. 부모의 eat를 그대로 쓰고 한 줄만 더하고 싶을 땐 super().eat()를 써요. super()는 부모 클래스를 가리켜요. 이렇게 하면 밥 먹는 문구는 Animal에만 있어서, Animal을 고치면 Dog도 같이 바뀌어요. 1파트에서 본 두 군데 고치기 문제가 풀려요. 같은 모양으로 __init__도 부를 수 있어요. 다음 장에서 봐요." + REAL)

o = [sec("in-super")] + head(EB3, "칸을 더할 땐 super().__init__으로 부모에게 맡겨요", K3)
IS = ["class Dog(Animal):", "    def __init__(self, name, breed):", "        super().__init__(name)", "        self.breed = breed", "", "    def speak(self):", '        print(f"{self.name}가 멍멍 짖어요")', "",
      'd = Dog("초코", "푸들")', "print(d.name, d.breed)", "d.speak()"]
FW = 1100
o += cell({"id": "c-i4", "lines": IS, "n": 9, "out": ["초코 푸들", "초코가 멍멍 짖어요"]}, 96, T, FW)
o.append(hl(96, T, FW, 5, 2, "skip", 1))
o.append(tag(tx(96, [IS[5]], 30), ly(T, 5), "앞에서 본 멍멍", GRAY, 1, size=26))
o.append(hl(96, T, FW, 2, 1, "run", 2))
o.append(hl(96, T, FW, 3, 1, "mark", 3))
o.append(tag(tx(96, [IS[3]], 30), ly(T, 3), "개만 가진 칸은 직접 붙여요", BL, 3))
RX, RW = 1250, 574
BY, BF = T + 20, 40
s1, s2 = "super()", ".__init__(name)"
w1, w2 = tw(s1, BF), tw(s2, BF)
o.append(p(f"position:absolute;left:{RX}px;top:{BY}px;font-family:{MONO};font-size:{BF}px;font-weight:700;line-height:1.3;white-space:pre;color:{INK}",
           f'<span style="color:{MD}">{e(s1)}</span>{e(s2)}', at(2)))
for x0, ww, col, txt in [(RX, w1, MD, "부모\n클래스"), (RX + w1, w2, K3, "부모의 __init__에\nname을 넣어요.\nself는 안 적어요")]:
    o.append(f'<div{at(2, "fade")} style="position:absolute;left:{x0 + 6:.0f}px;top:{BY + 58}px;width:{ww - 12:.0f}px;height:16px;border:4px solid {col};border-top:none;border-radius:0 0 8px 8px"></div>')
    o.append(p(f"position:absolute;left:{x0 + 6:.0f}px;top:{BY + 88}px;font-size:26px;font-weight:700;line-height:1.4;color:{col};white-space:pre", e(txt), at(2, "fade")))
RY = 560
o.append(obj("d", [("name", '"초코"', MDBG)], RX, RY, RW, cls="Dog", color=CR, bg=CRBG, attrs=at(2)))
o.append(obj("d", [("name", '"초코"', MDBG), ("breed", '"푸들"', K1BG)], RX, RY, RW, cls="Dog", color=CR, bg=CRBG, attrs=at(3)))
o.append(caption("name은 부모가, breed는 자식이 붙여요.", 916, 4))
W("in-super", o, "개는 견종(breed) 칸이 하나 더 있어요. 그래서 Dog에 __init__을 새로 적어야 해요. 이름을 붙이는 일은 부모의 __init__이 이미 하고 있으니 다시 적지 않고 맡겨요. 앞 장의 super().eat()처럼, super().__init__(name)은 부모의 __init__에 이름을 넣어 부르는 줄이에요. self는 적지 않아요. 부모가 name을 붙인 뒤, 자식은 breed만 직접 붙여요. speak는 앞에서 본 멍멍을 그대로 다시 적었어요." + REAL)

o = [sec("in-super2")] + head(EB3, "Dog(\"초코\", \"푸들\") 한 줄에서 일어나는 일", K3)
ST5 = [("①", "Dog.__init__", "자식의 __init__이 불려요. self는 새 객체", CR),
       ("②", "super().__init__(name)", "부모의 __init__으로 가요. 같은 self예요", MD),
       ("③", "self.name = name", "부모가 name 칸을 붙여요", MD),
       ("④", "self.breed = breed", "자식으로 돌아와 breed 칸을 붙여요", CR),
       ("⑤", "d = 다 만든 객체", "두 칸이 다 붙은 객체가 d에 담겨요", CR)]
for i, (n_, code, what, col) in enumerate(ST5):
    o.append(f'<div id="stp-{i + 1}"{at(i + 1)}{DIM("st")} style="position:absolute;left:96px;top:{T + i * 136}px;width:1080px;height:136px;display:flex;flex-direction:row;align-items:center;gap:24px;border-bottom:2px solid {LINE}">'
             + p(f"width:48px;flex:none;font-size:40px;font-weight:900;color:{col}", e(n_))
             + '<div style="display:flex;flex-direction:column;gap:6px">' + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:{INK};white-space:pre", e(code))
             + p(f"font-size:28px;color:{SUB}", e(what)) + '</div></div>')
RX, RW = 1250, 574
o.append(obj("self", [], RX, T, RW, cls="Dog", color=CR, bg=CRBG, empty="아직 칸이 없어요", rh=72, attrs=at(1)))
o.append(obj("self", [("name", '"초코"', MDBG)], RX, T, RW, cls="Dog", color=CR, bg=CRBG, rh=72, attrs=' data-build-in="fly order 3" data-from="stp-3"'))
o.append(obj("self", [("name", '"초코"', MDBG), ("breed", '"푸들"', K1BG)], RX, T, RW, cls="Dog", color=CR, bg=CRBG, rh=72, attrs=' data-build-in="fly order 4" data-from="stp-4"'))
o.append(obj("d", [("name", '"초코"', MDBG), ("breed", '"푸들"', K1BG)], RX, T, RW, cls="Dog", color=CR, bg=CRBG, rh=72, attrs=' data-build-in="fly order 5" data-from="stp-5"'))
o.append(tag(RX, T + obj_h(2, 72) + 56, "부모의 __init__에서도 자식의 __init__에서도 같은 self예요", MD, 2, lead=False, w=RW))
W("in-super2", o, "24의 다섯 단계 그림처럼 이 줄을 나눠 봐요. 만들면 자식의 __init__이 먼저 불려요. 첫 줄에서 super().__init__을 만나 부모의 __init__으로 가요. 부모가 같은 self에 name 칸을 붙이고 돌아오면, 자식이 breed 칸을 붙여요. 오른쪽 그림에서 칸이 늘어나는 걸 보세요. 부모의 __init__과 자식의 __init__에서 self는 같은 객체 하나예요.")

o = [sec("in-list")] + head(EB3, "섞어 담아도 동물마다 자기 speak를 불러요", K3)
L1 = ['animals = [Dog("초코", "푸들"), Cat("나비"), Animal("하마")]', "for x in animals:", "    x.speak()"]
O1 = ["초코가 멍멍 짖어요", "나비가 야옹 울어요", "하마가 소리를 내요"]
o += cell({"id": "c-i7", "lines": L1, "n": 10, "out": O1}, 96, T, 1728)
o.append(hl(96, T, 1728, 2, 1, "mark", 1))
o.append(tag(tx(96, [L1[2]], 30), ly(T, 2), "부르는 줄은 하나", BL, 1))
OX = tx(96, O1, 40)
o.append(f'<div{STAGGER(2, 140)} style="position:absolute;left:0;top:0;width:1920px;height:1080px">')
for j, (t_, col) in enumerate([("Dog의 speak", CR), ("Cat의 speak", K1), ("Animal의 speak", MD)]):
    o.append(tag(OX, oy(T, 3, j), t_, col))
o.append('</div>')
T2 = int(T + cell_h({"lines": L1, "out": O1})) + 46
L2 = ["print(isinstance(d, Dog))", "print(isinstance(d, Animal))", "print(isinstance(a, Dog))"]
o += cell({"id": "c-i8", "lines": L2, "n": 11, "out": ["True", "True", "False"], "attrs": at(3)}, 96, T2, 1728)
o.append(tag(tx(96, L2, 40), ly(T2, 0), "isinstance(값, 클래스): 그 클래스로 만들었나요?", CR, 3))
OX = tx(96, ["False"], 40)
for j, (t_, col) in enumerate([("d는 Dog로 만들었어요", GR), ("개도 동물이에요", GR), ("하마는 개가 아니에요", RED)]):
    o.append(tag(OX, oy(T2, 3, j), t_, col, 4 + j))
W("in-list", o, "개, 고양이, 하마를 한 리스트에 섞어 담았어요. for로 하나씩 x.speak()를 부르면 동물마다 자기 클래스의 speak가 불려요. 부르는 쪽은 어떤 동물인지 몰라도 돼요. 어떤 클래스로 만들었는지 알고 싶으면 isinstance를 써요. 그 클래스나 그 클래스의 자식으로 만들었으면 True예요. d는 Dog이면서 Animal이기도 해서 둘 다 True예요. 하마 a는 Dog가 아니라서 False예요." + REAL)

# ---------- 메서드 찾기: a slide students press in the browser (tools/lab_find.js) ----------
LF_CSS = ("<style>"
          "#in-lab button{font-family:" + MONO.replace("'", '"') + ";font-size:25px;font-weight:700;border-radius:14px;padding:8px 18px;cursor:pointer;border:3px solid #C9CED8;background:#FFFFFF;color:#1D2330}"
          "#in-lab button:disabled{opacity:.5;cursor:default}"
          "#in-lab button.lf-on{border-color:#2F7D6B;background:#E3F2EE}"
          "#in-lab #lf-go{font-family:" + SANS.replace("'", '"') + ";background:#2F7D6B;border-color:#2F7D6B;color:#FFFFFF}"
          "#in-lab code{font-family:" + MONO.replace("'", '"') + ";font-size:24px;background:#F1F0EC;border-radius:8px;padding:1px 8px}"
          "#in-lab .lf-box{transition:box-shadow .3s,opacity .3s}"
          "#in-lab .lf-look{box-shadow:0 0 0 8px rgba(178,106,0,.45)}"
          "#in-lab .lf-box.lf-yes{box-shadow:0 0 0 8px rgba(31,138,76,.40)}"
          "#in-lab .lf-box.lf-no{opacity:.55}"
          "#in-lab .lf-row{transition:all .3s;border:2px solid transparent}"
          "#in-lab .lf-row.lf-yes{background:#D7F0DF!important;border-color:#1F8A4C}"
          "@keyframes lfIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}"
          "</style>")


def lf_row(sid, txt, fs=23):
    return (f'<div id="{sid}" class="lf-row" style="height:50px;border-radius:10px;background:#FFFFFF;padding:0 14px;display:flex;align-items:center">'
            + p(f"font-family:{MONO};font-size:{fs}px;font-weight:700;color:{INK};white-space:pre", e(txt)) + '</div>')


def lf_mold(sid, left, top, title, rows, color, bg):
    return (f'<div id="{sid}" class="lf-box" style="position:absolute;left:{left}px;top:{top}px;width:620px;background:{bg};border:5px dashed {color};border-radius:26px;padding:16px 22px;display:flex;flex-direction:column;gap:8px">'
            + '<div style="display:flex;flex-direction:row;align-items:center;gap:12px">' + p(f"font-size:20px;font-weight:700;color:#FFFFFF;background:{color};border-radius:10px;padding:3px 12px", "클래스") + p(f"font-family:{MONO};font-size:27px;font-weight:700;color:{color}", e(title)) + '</div>'
            + "".join(lf_row(f"{sid}-{k}", t) for k, t in rows) + '</div>')


def lf_obj(name, cls, rows, left, top, color):
    return (f'<div id="lf-o-{name}" class="lf-box" style="position:absolute;left:{left}px;top:{top}px;width:300px;background:{CARD};border:3px solid {color};border-radius:22px;overflow:hidden">'
            + f'<div style="height:56px;background:{color};display:flex;align-items:center;padding:0 18px;gap:10px">' + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:#FFFFFF", e(name)) + '<div style="flex:1"></div>' + p("font-size:18px;font-weight:700;color:#FFFFFF;opacity:.85", e(cls)) + '</div>'
            + '<div style="padding:10px 14px;display:flex;flex-direction:column;gap:6px">' + "".join(lf_row(f"lf-o-{name}-{k}", f"{k}  {v}", 21) for k, v in rows) + '</div></div>')


o = [sec("in-lab"), LF_CSS] + head(EB3, "눌러 보기: 파이썬은 어디서부터 찾을까요", K3)
o.append(lf_mold("lf-m-Animal", 96, 196, "class Animal", [("__init__", "__init__(self, name)"), ("eat", "eat(self)"), ("speak", "speak(self)  # 소리를 내요")], MD, MDBG))
o.append(f'<x-shape kind="arrow-right" style="position:absolute;left:366px;top:476px;width:80px;height:30px;transform:rotate(-90deg);background:{CR}"></x-shape>')
o.append(p(f"position:absolute;left:456px;top:472px;font-size:24px;font-weight:700;color:{CR}", "물려받기"))
o.append(lf_mold("lf-m-Dog", 96, 540, "class Dog(Animal)", [("__init__", "__init__(self, name, breed)"), ("speak", "speak(self)  # 멍멍"), ("fetch", "fetch(self)")], CR, CRBG))
o.append(lf_obj("a", "Animal", [("name", '"하마"')], 762, 256, MD))
o.append(lf_obj("d", "Dog", [("name", '"초코"'), ("breed", '"푸들"')], 762, 560, CR))
o.append(p(f"position:absolute;left:762px;top:396px;width:300px;font-size:22px;color:{SUB};text-align:center", "Animal로 만들었어요"))
o.append(p(f"position:absolute;left:762px;top:786px;width:300px;font-size:22px;color:{SUB};text-align:center", "Dog로 만들었어요"))
o.append(f'<div style="position:absolute;left:1100px;top:196px;width:724px;height:286px;background:{CARD};border:2px solid {LINE};border-radius:22px;padding:18px 24px;display:flex;flex-direction:column;gap:14px">'
         + f'<div id="lf-who" style="display:flex;flex-direction:row;gap:12px;align-items:center">{p(f"width:96px;font-size:24px;font-weight:700;color:{SUB}", "누구에게")}<button data-o="a">a</button><button id="lf-b-d" data-o="d">d</button></div>'
         + f'<div id="lf-what" style="display:flex;flex-direction:row;flex-wrap:wrap;gap:10px;align-items:center">{p(f"width:96px;font-size:24px;font-weight:700;color:{SUB}", "무엇을")}<button data-k="speak">.speak()</button><button id="lf-b-eat" data-k="eat">.eat()</button><button data-k="fetch">.fetch()</button><button data-k="breed">.breed</button><button data-k="name">.name</button></div>'
         + f'<div style="display:flex;flex-direction:row;gap:16px;align-items:center"><button id="lf-go">찾아보기 ▶</button>{p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{INK}", "d.eat()", " id=\"lf-code\"")}</div></div>')
o.append(f'<div id="lf-log" style="position:absolute;left:1100px;top:502px;width:724px;height:236px;background:{CARD};border:2px solid {LINE};border-radius:22px;padding:18px 24px;display:flex;flex-direction:column;gap:6px">'
         + p(f"font-size:25px;color:{GRAY}", "찾는 길이 여기에 한 줄씩 나와요.") + '</div>')
o.append(f'<div style="position:absolute;left:1100px;top:758px;width:724px;height:150px;background:{CARD};border:2px solid {LINE};border-left:10px solid {JP};border-radius:22px;padding:16px 24px;display:flex;flex-direction:column;gap:8px">'
         + p(f"font-size:24px;font-weight:700;color:{JP}", "출력") + p(f"font-family:{MONO};font-size:22px;font-weight:700;line-height:1.4;color:{INK};white-space:pre-wrap;overflow-wrap:break-word", "", ' id="lf-out"') + '</div>')
o.append(f'<div style="position:absolute;left:96px;top:930px;width:1728px;height:106px;background:{CARD};border:2px solid {LINE};border-left:10px solid {CR};border-radius:18px;padding:0 30px;display:flex;align-items:center">'
         + p(f"font-size:30px;font-weight:500;line-height:1.4;color:{INK}", "누구에게 무엇을 물을지 고르고 찾아보기를 눌러요. 브라우저로 슬라이드를 열면 눌러져요.", ' id="lf-msg"') + '</div>')
o += [cursor(1, target="lf-b-d"), cursor(2, target="lf-b-eat"), cursor(3, target="lf-go"), cursor_off(4)]
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lab_find.js")) as f:
    o.append('<script type="text/slide-js">\n' + f.read() + '</script>')
W("in-lab", o, "메서드와 값을 어디서 찾는지 직접 눌러 보는 장이에요. 브라우저로 슬라이드를 열면 버튼이 눌러져요. 객체와 물을 것을 고르고 찾아보기를 누르면 파이썬이 찾는 순서대로 불이 들어와요. 먼저 객체 자신, 다음은 그 객체를 만든 클래스, 그다음은 부모 클래스예요. d.speak()는 Dog에서 찾아서 멍멍이 나와요. d.eat()는 Dog에 없어서 Animal까지 올라가 찾아요. a.fetch()는 Animal에서 끝나서 AttributeError가 나요. 자식 클래스는 보지 않기 때문이에요. 처음 세 번 넘기면 커서가 누를 곳을 d, eat, 찾아보기 순서로 짚어 줘요. 누르기 전에 어디서 찾을지 수강생에게 먼저 물어보세요. 출력은 tools/demo.sh로 실제로 실행한 결과예요.")


# ---------- part 4 ----------
o = [sec("cmp-copy")] + head(EB4, "복사해서 만든 클래스와 물려받은 클래스", K4)
CFS[0] = 26
LC = ["class Cat:", "    def __init__(self, name):", "        self.name = name", "", "    def eat(self):", '        print(f"{self.name}가 밥을 먹어요")', "", "    def speak(self):", '        print(f"{self.name}가 야옹 울어요")']
LI = ["class Cat(Animal):", "    def speak(self):", '        print(f"{self.name}가 야옹 울어요")']
CT = 270
for x, title, col in [(96, "복사 (1파트)", GRAY), (978, "상속 (3파트)", CR)]:
    o.append(p(f"position:absolute;left:{x + 20}px;top:{T}px;font-size:32px;font-weight:700;color:{col}", e(title)))
o += cell({"id": "c-cp1", "lines": LC}, 96, CT, 846, gut=False)
o += cell({"id": "c-cp2", "lines": LI, "attrs": at(2)}, 978, CT, 846, gut=False)
o.append(hl(96, CT, 846, 1, 5, "err", 1))
o.append(tag(tx(96, [LC[2]], 20), ly(CT, 3), "Dog에도 똑같이 적음", RED, 1, size=24))
o.append(hl(978, CT, 846, 1, 2, "mark", 2))
o.append(tag(978 + 20, int(CT + cell_h({"lines": LI})) + 40, "__init__과 eat는 Animal에게 맡겼어요.\n다른 점인 speak만 적어요.", GR, 2, lead=False, w=820, size=26))
CFS[0] = 30
o += rows_list(96, 680, 1728, [["eat를 고치면", "Dog, Cat 다 고쳐야 해요", "Animal 한 곳만 고쳐요"], ["적는 것", "모든 줄", "다른 점만"]], [340, 664, 664], order0=3, rh=90,
               head_=["", "복사", "상속"], fs=30, colors=[None, GRAY, CR])
W("cmp-copy", o, "상속하면 다른 점만 적어서 코드가 짧고, 고칠 곳이 한 군데예요. 1파트에서 복사해 만든 Cat과 3파트에서 물려받은 Cat을 나란히 놓았어요. 복사한 Cat은 __init__과 eat를 Dog와 똑같이 다시 적었어요. 물려받은 Cat은 speak만 적고 나머지는 Animal에게 맡겼어요. 밥 먹는 문구를 바꾸면 Animal 한 곳만 고치면 돼요.")

o = [sec("cmp-when")] + head(EB4, "\"~는 ~의 한 종류\"일 때 상속해요", K4)
o.append(f'<div{STAGGER(1, 120)} style="position:absolute;left:0;top:0;width:1920px;height:1080px">')
for i, (q, ok, a_) in enumerate([("개는 동물의 한 종류예요", True, "Dog(Animal)"), ("고양이는 동물의 한 종류예요", True, "Cat(Animal)"), ("미니 붕어빵은 붕어빵의 한 종류예요", True, "MiniBread(Bread)"),
                                 ("동물원은 동물의 한 종류가 아니에요", False, "Zoo 클래스를 따로"), ("사료는 동물의 한 종류가 아니에요", False, "Food 클래스를 따로")]):
    if i == 3:
        o.append('</div>')
        o.append(f'<div{STAGGER(2, 120)} style="position:absolute;left:0;top:0;width:1920px;height:1080px">')
    o.append(f'<div style="position:absolute;left:96px;top:{T + i * 124}px;width:1728px;height:124px;display:flex;flex-direction:row;align-items:center;gap:32px;border-bottom:2px solid {LINE}">'
             + p(f"width:110px;flex:none;font-size:34px;font-weight:900;color:{GR if ok else RED}", ("✓ 상속" if ok else "✕ 따로"))
             + p(f"flex:1;font-size:34px;font-weight:700;color:{INK}", e(q))
             + p(f"font-family:{MONO if a_.isascii() else SANS};font-size:30px;font-weight:700;color:{CR if ok else SUB};white-space:nowrap", e(a_)) + '</div>')
o.append('</div>')
o.append(caption("코드가 비슷해 보여도 한 종류가 아니면 상속하지 않아요.", 880, 3))
W("cmp-when", o, "상속은 언제 쓸까요? 자식이 부모의 한 종류일 때예요. 개와 고양이는 동물의 한 종류라서 Animal을 물려받아요. 6파트에서 만들 미니 붕어빵도 붕어빵의 한 종류예요. 동물원은 동물이 아니에요. 동물을 담아 두는 곳이라서 Zoo 클래스를 따로 만들고 안에 동물 리스트를 두면 돼요. 사료도 동물의 한 종류가 아니니 따로 만들어요. 소리 내어 \"~는 ~의 한 종류예요\"가 자연스러운지 읽어 보세요.")

# ---------- part 5 ----------
o = [sec("t-nosuper")] + head(EB5, "super().__init__을 빼먹으면 부모 칸이 없어요", K5)
CFS[0] = 26
TN = AN + ["", "class Dog(Animal):", "    def __init__(self, name, breed):", "        self.breed = breed", "", 'd = Dog("초코", "푸들")', "d.eat()"]
ERR = "AttributeError: 'Dog' object has no attribute 'name'"
FW = 1090
o += cell({"id": "c-t1", "lines": TN, "n": 1, "out": [ERR], "err": True, "oid": "t1-err"}, 96, T, FW)
o.append(hl(96, T, FW, 11, 2, "err", 1))
o.append(tag(tx(96, [TN[12]], 30), ly(T, 12), "super().__init__ 줄이 없어요", RED, 1))
o.append(box(2, 186, int(oy(T, len(TN), 0) - 26), int(tw(ERR)) + 30, 52, RED))
o.append(shake(2, "t1-err"))
CFS[0] = 30
RX, RW = 1250, 574
o.append(obj("d", [("breed", '"푸들"'), ("name", None)], RX, T + 40, RW, cls="Dog", color=CR, bg=CRBG, attrs=at(3), rh=84, fs=32))
o.append(fixv(RX, T + 40 + obj_h(2, 84) + 120, RW, None, "super().__init__(name)", 4, size=30, label="자식 __init__ 첫 줄에 적어요"))
W("t-nosuper", o, "자식 클래스에 __init__을 새로 적으면 부모의 __init__은 저절로 불리지 않아요. 3파트의 덮어쓰기와 같아요. Dog의 __init__에서 breed만 붙이고 super().__init__을 빼먹어서, name 칸이 없는 객체가 만들어졌어요. 만들 때는 아무 말이 없다가 eat에서 self.name을 꺼낼 때 AttributeError가 나요. 자식 __init__의 첫 줄에 super().__init__을 적어요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p5", "오류와 함정"))

o = [sec("t-superself")] + head(EB5, "super().__init__에 self를 넣으면 3 were given", K5)
L = ["class Dog(Animal):", "    def __init__(self, name, breed):", "        super().__init__(self, name)", "        self.breed = breed", "", 'd = Dog("초코", "푸들")']
ERR = "TypeError: Animal.__init__() takes 2 positional arguments but 3 were given"
o += cell({"id": "c-t2", "lines": L, "n": 2, "out": [ERR], "err": True}, 96, T, 1728)
o.append(hl(96, T, 1728, 2, 1, "err", 1))
o.append(tag(tx(96, [L[2]], 30), ly(T, 2), "self를 직접 넣었어요", RED, 1))
k = ERR.index("3 were given")
o.append(underline(2, int(201 + tw(ERR[:k])), int(201 + tw(ERR[:k + 12])), int(oy(T, 6, 0) + 24), RED))
SY = int(T + cell_h({"lines": L, "out": [ERR]})) + 70
o.append(slot_row(96, SY, "Animal.__init__의 칸", [("self", "slot"), ("name", "slot")], 3, lw=400))
o.append(slot_row(96, SY + 100, "들어온 값 3개", [("self (자동)", "auto"), ("self", "extra"), ("name", "value")], 3, lw=400))
o.append(mfix(96, SY + 222, "ss-bad", [("s", "super().__init__("), (None, "self, "), ("a", "name)")], [("s", "super().__init__("), ("a", "name)")], 4))
W("t-superself", o, "super().__init__ 괄호에 self를 같이 적었어요. 부모의 __init__은 self, name 두 칸인데 세 개가 들어왔다는 TypeError예요. super()로 부를 때도 d.speak()처럼 파이썬이 self를 알아서 넣어 줘요. 그래서 직접 적은 self까지 합쳐 세 개가 됐어요. 아래 그림처럼 한 칸이 남아요. super().__init__(name)처럼 self 없이 적어요." + REAL)

o = [sec("t-breed")] + head(EB5, "자식 클래스는 재료가 하나 더 필요해요", K5)
L = ["class Dog(Animal):", "    def __init__(self, name, breed):", "        super().__init__(name)", "        self.breed = breed", "", 'd = Dog("초코")']
ERR = "TypeError: Dog.__init__() missing 1 required positional argument: 'breed'"
o += cell({"id": "c-t3", "lines": L, "n": 3, "out": [ERR], "err": True}, 96, T, 1728)
o.append(hl(96, T, 1728, 5, 1, "err", 1))
o.append(tag(tx(96, [L[5]], 30), ly(T, 5), "이름만 넣었어요", RED, 1))
k = ERR.index("'breed'")
o.append(underline(2, int(201 + tw(ERR[:k])), int(201 + tw(ERR[:k + 7])), int(oy(T, 6, 0) + 24), RED))
SY = int(T + cell_h({"lines": L, "out": [ERR]})) + 70
o.append(slot_row(96, SY, "Dog.__init__의 칸", [("self", "slot"), ("name", "slot"), ("breed", "slot")], 3, lw=400))
o.append(slot_row(96, SY + 100, "들어온 값", [("self (자동)", "auto"), ('"초코"', "value"), ("없음", "missing")], 3, lw=400))
o.append(fix(96, SY + 222, 'Dog("초코")', 'Dog("초코", "푸들")', 4, mark=(8, 14, 5)))
o.append(p(f"position:absolute;left:96px;top:{SY + 316}px;font-size:28px;color:{SUB}", '견종을 자주 안 적으면 20에서 배운 기본값으로 breed="믹스"를 둘 수도 있어요.', at(5)))
W("t-breed", o, "Animal처럼 이름만 넣어 만들었더니 breed가 모자라다는 TypeError가 나요. Dog에 __init__을 새로 적었으니 만들 때 불리는 건 Dog의 __init__이에요. 아래 그림처럼 breed 칸이 비어요. 자식 __init__의 칸 수에 맞춰 재료를 넣어요. 견종을 자주 안 적는다면 20에서 배운 기본값으로 breed=\"믹스\"를 둘 수도 있어요." + REAL)

o = [sec("t-shop")] + head(EB5, "a.shop = 으로 바꾸면 a에만 새 칸이 생겨요", K5)
TS = ["class Bread:", '    shop = "붕어빵 1호점"', "", "    def __init__(self, flavor, price):", "        self.flavor = flavor", "        self.price = price", "", 'a = Bread("팥", 1000)', 'b = Bread("슈크림", 1200)', 'a.shop = "옆 가게"', "print(a.shop)", "print(b.shop)", "print(Bread.shop)"]
TO = ["옆 가게", "붕어빵 1호점", "붕어빵 1호점"]
FW = 860
o += cell({"id": "c-t4", "lines": TS, "n": 4, "out": TO}, 96, T, FW)
o.append(hl(96, T, FW, 9, 1, "err", 1))
o.append(tag(tx(96, [TS[9]], 30), ly(T, 9), "붕어빵 이름으로 바꾸기", RED, 1))
o.append(src("shop-src", 96 + 105, ly(T, 9) - 22, tw(TS[9]), 44))
RX, RW = 1000, 824
o.append(mold(RX, T, RW, "class Bread", ['shop = "붕어빵 1호점"'], sid="shop-mold"))
o.append(tag(RX + 40 + int(tw('shop = "붕어빵 1호점"')) + 30, T + 6 + 24 + 48 + 10 + 22, "그대로예요", MD, 3))
o.append(pulse(3, "shop-mold"))
OY = int(T + mold_h(1)) + 60
o.append(obj("a", [("flavor", '"팥"')], RX, OY, 400, rh=56, fs=26))
o.append(obj("a", [("flavor", '"팥"'), ("shop", '"옆 가게"', K5BG)], RX, OY, 400, rh=56, fs=26, attrs=' data-build-in="fly order 2" data-from="shop-src"'))
o.append(obj("b", [("flavor", '"슈크림"')], RX + 424, OY, 400, rh=56, fs=26))
OX = tx(96, TO, 40)
o.append(tag(OX, oy(T, 13, 0), "a에 붙은 칸이 먼저 보여요", RED, 3))
y1, y2 = out_span(T, 13, 1, 2)
o.append(bracket(OX - 4, y1, y2, MD, 3))
o.append(tag(OX + 26, (y1 + y2) / 2, "b와 틀은 그대로", MD, 3, lead=False))
o.append(fixv(RX, OY + obj_h(2, 56) + 50, RW, 'a.shop = "옆 가게"', 'Bread.shop = "옆 가게"', 4, size=28, label="모두 바꾸려면 틀 이름으로"))
W("t-shop", o, "클래스 변수를 붕어빵 이름으로 바꿨어요. 오류는 나지 않지만, 틀의 값이 바뀌는 게 아니라 a에만 shop이라는 새 칸이 붙어요. 24의 2파트에서 점으로 칸을 붙인 것과 같아요. 이제 a.shop을 꺼내면 a에 붙은 칸이 먼저 보여서 옆 가게가 나오고, b와 틀은 그대로 1호점이에요. 모두의 값을 바꾸려면 Bread.shop =처럼 틀 이름으로 바꿔요." + REAL)

o = [sec("t-count")] + head(EB5, "self.count로 세면 틀의 개수가 안 늘어요", K5)
TC = ["class Bread:", "    count = 0", "", "    def __init__(self, flavor, price):", "        self.flavor = flavor", "        self.price = price", "        self.count = self.count + 1", "", 'a = Bread("팥", 1000)', 'b = Bread("슈크림", 1200)', "print(a.count, b.count)", "print(Bread.count)"]
FW = 860
o += cell({"id": "c-t5", "lines": TC, "n": 5, "out": ["1 1", "0"]}, 96, T, FW)
o.append(hl(96, T, FW, 6, 1, "err", 1))
OX = tx(96, ["1 1"], 40)
o.append(tag(OX, oy(T, 12, 0), "a.count, b.count", SUB, 3, size=26))
o.append(tag(OX, oy(T, 12, 1), "Bread.count", SUB, 3, size=26))
RX = 1010
BF = 36
L6 = "self.count = self.count + 1"
o.append(p(f"position:absolute;left:{RX}px;top:{T + 10}px;font-family:{MONO};font-size:{BF}px;font-weight:700;line-height:1.3;white-space:pre;color:{INK}", e(L6), at(2)))
for a0, a1, col, txt in [(0, 10, RED, "왼쪽: 붕어빵에\n새 칸을 붙여요"), (13, 27, MD, "오른쪽: 붕어빵에 없으니\n틀의 0을 읽어요")]:
    x0, ww = RX + tw(L6[:a0], BF), tw(L6[a0:a1], BF)
    o.append(f'<div{at(2, "fade")} style="position:absolute;left:{x0 + 4:.0f}px;top:{T + 66}px;width:{ww - 8:.0f}px;height:14px;border:4px solid {col};border-top:none;border-radius:0 0 8px 8px"></div>')
    o.append(p(f"position:absolute;left:{x0 + 4:.0f}px;top:{T + 92}px;font-size:26px;font-weight:700;line-height:1.4;color:{col};white-space:pre", e(txt), at(2, "fade")))
MY = T + 210
o.append(mold(RX, MY, 814, "class Bread", ["count = 0"], at(3), fs=28, tfs=30, sid="cnt-mold"))
o.append(pulse(3, "cnt-mold"))
o.append(tag(RX + 40 + int(tw("count = 0", 28)) + 30, MY + 6 + 24 + 42 + 10 + 21, "한 번도 안 바뀌어요", MD, 3, size=26))
OY = int(MY + mold_h(1, 28, 30)) + 30
o.append(obj("a", [("flavor", '"팥"'), ("count", "1", K5BG)], RX, OY, 395, rh=52, fs=26, attrs=at(3)))
o.append(obj("b", [("flavor", '"슈크림"'), ("count", "1", K5BG)], RX + 419, OY, 395, rh=52, fs=26, attrs=at(3)))
o.append(mfix(96, 906, "cnt-bad", [(None, "self"), ("c1", ".count = "), (None, "self"), ("c2", ".count + 1")], [(None, "Bread"), ("c1", ".count = "), (None, "Bread"), ("c2", ".count + 1")], 4, size=28))
W("t-count", o, "2파트의 개수 세기를 self.count로 적었어요. 오류는 없는데 Bread.count는 0이고, 붕어빵마다 1이에요. 오른쪽 self.count는 붕어빵에 count 칸이 없으니 틀의 0을 읽어요. 왼쪽 self.count =은 앞 장처럼 붕어빵에 새 칸을 붙여요. 그래서 틀의 값은 한 번도 안 바뀌어요. 20의 전역 변수에서 같은 이름에 넣으면 새 지역 변수가 생기던 것과 비슷해요. 틀의 값을 바꿀 땐 Bread.count처럼 틀 이름으로 적어요." + REAL)

# ---------- part 6 ----------


def spot_block(order, left, top, i, n, w=1728):
    return spot(order, left + 87, top + 10 + i * LHf() - 4, w - 89, n * LHf() + 8, pad=6, r=12, dim=0.55)


o = [sec("x-card")] + head(EB6, "도장 카드 ①: 틀에 가게와 목표, VIP는 두 배로", K6)
CFS[0] = 28
XC = ["class Card:", '    shop = "KANT 카페"', "    goal = 10", "", "    def __init__(self, name):", "        self.name = name", "        self.stamps = 0", "", "    def add(self):", "        self.stamps = self.stamps + 1", "", "    def __str__(self):", "        left = Card.goal - self.stamps", '        return f"[{Card.shop}] {self.name}: 도장 {self.stamps}개, {left}개 남음"', "", "class VipCard(Card):", "    def add(self):", "        self.stamps = self.stamps + 2"]
XT = 200
o += cell({"id": "c-x1", "lines": XC, "n": 1}, 96, XT, 1728)
for k, (i, n, kind, ti, t_, col) in enumerate([(1, 2, "mark", 1, "모든 카드가 같은 값: 클래스 변수", BL), (11, 3, "run", 11, "남은 도장 수까지 글자로 (25)", GR), (15, 3, "err", 15, "도장 카드의 한 종류, add만 두 개씩", RED)]):
    o.append(hl(96, XT, 1728, i, n, kind, k + 1))
    o.append(lspot(k + 1, 96 + 87, XT, 1728 - 87, cell_h({"lines": XC}), XT + 10 + i * LHf(), n * LHf(), bar=col))
    o.append(tag(tx(96, [XC[ti]], 30), ly(XT, ti), t_, col, k + 1))
o.append(lspot_off(4))
o.append(p(f"position:absolute;left:201px;top:{XT + cell_h({'lines': XC}) + 14:.0f}px;font-size:24px;color:{GRAY}", "출력 없이 틀만 만드는 셀이에요"))
CFS[0] = 30
W("x-card", o, "24에서 만든 도장 카드를 이어서 만들어요. 가게 이름과 목표 도장 수는 모든 카드가 같아서 클래스 변수로 틀에 적었어요. __str__은 25에서 배운 대로 남은 도장 수까지 글자로 돌려줘요. VIP 카드는 도장 카드의 한 종류라서 Card를 물려받고, add만 두 개씩 찍도록 덮어썼어요. __init__과 __str__은 그대로 물려받아요. 이 셀은 틀만 만들어서 출력이 없어요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요.", ("p6", "실습"))

o = [sec("x-card2")] + head(EB6, "도장 카드 ②: 같은 add인데 카드마다 다르게", K6)
XC2 = ['kim = Card("kim")', 'lee = VipCard("lee")', "kim.add()", "kim.add()", "lee.add()", "lee.add()", "print(kim)", "print(lee)"]
o += cell({"id": "c-x2", "lines": XC2, "n": 2, "out": ["[KANT 카페] kim: 도장 2개, 8개 남음", "[KANT 카페] lee: 도장 4개, 6개 남음"]}, 96, T, 900)
RX, RW = 1040, 784
o.append(obj("kim", [("name", '"kim"'), ("stamps", "2")], RX, T, RW, cls="Card", color=BL, bg=K1BG, vid={"stamps": ' id="st-kim" data-start="0"'}))
o.append(obj("lee", [("name", '"lee"'), ("stamps", "4")], RX, T + obj_h(2) + 34, RW, cls="VipCard", color=CR, bg=CRBG, vid={"stamps": ' id="st-lee" data-start="0"'}))
for k, (ln, who, v) in enumerate([(2, "kim", "1"), (3, "kim", "2"), (4, "lee", "2"), (5, "lee", "4")]):
    o.append(run(k + 1, 96 + 87, T + 10 + ln * LHf(), 900 - 89, LHf()))
    o.append(text(k + 1, f"st-{who}", v))
o.append(run_off(5))
MYb = int(T + cell_h({"lines": XC2, "out": [1, 2]})) + 70
for i, (call, meth, plus, col, bg) in enumerate([("kim.add()", "Card.add", "+1씩", BL, K1BG), ("lee.add()", "VipCard.add", "+2씩", CR, CRBG)]):
    o.append(f'<div{at(2 + 2 * i)} style="position:absolute;left:96px;top:{MYb + i * 100}px;width:900px;height:84px;display:flex;flex-direction:row;align-items:center;gap:22px">'
             + f'<div style="width:240px;flex:none;display:flex">' + chip(call, GRAY, "#F1F0EC") + '</div>' + arrow(60)
             + f'<div style="width:300px;flex:none;display:flex">' + chip(meth, col, bg, dashed=True) + '</div>'
             + p(f"font-size:32px;font-weight:900;color:{col}", e(plus)) + '</div>')
o.append(tag(RX, T + 2 * obj_h(2) + 34 + 70, "print와 가게 이름은 둘 다 Card에서 물려받아요", K6, 5, lead=False, w=RW))
W("x-card2", o, "앞 셀의 틀로 일반 카드 kim과 VIP 카드 lee를 만들었어요. 둘 다 add를 두 번 불렀는데 kim은 2개, lee는 4개예요. lee는 VipCard 틀에 덮어쓴 add를 쓰기 때문이에요. print는 두 카드 모두 Card의 __str__을 쓰고, 가게 이름과 목표도 틀에서 같이 봐요. 부르는 쪽은 똑같이 add()라고만 적어도 카드마다 알맞게 동작해요." + REAL)

o = [sec("x-mini")] + head(EB6, "붕어빵 메뉴판 ①: 미니 붕어빵 틀을 물려받기", K6)
CFS[0] = 28
XM = ["class Bread:", "    count = 0", "", "    def __init__(self, flavor, price):", "        self.flavor = flavor", "        self.price = price", "        Bread.count = Bread.count + 1", "", "    def __str__(self):", '        return f"{self.flavor} 붕어빵 {self.price:,}원"', "", "class MiniBread(Bread):", "    def __init__(self, flavor, price, qty):", "        super().__init__(flavor, price)", "        self.qty = qty", "", "    def __str__(self):", '        return f"미니 {self.flavor} {self.qty}개 {self.price * self.qty:,}원"']
o += cell({"id": "c-x3", "lines": XM, "n": 3}, 96, XT, 1728)
for k, (i, n, kind, tags_) in enumerate([(6, 1, "mark", [(6, "찍을 때마다 개수 세기", BL)]), (11, 4, "run", [(11, "미니 붕어빵도 붕어빵의 한 종류", GR), (13, "맛과 가격은 부모에게 맡겨요", GR)]), (16, 2, "err", [(16, "묶음 가격이 보이게 덮어쓰기", RED)])]):
    o.append(hl(96, XT, 1728, i, n, kind, k + 1))
    o.append(lspot(k + 1, 96 + 87, XT, 1728 - 87, cell_h({"lines": XM}), XT + 10 + i * LHf(), n * LHf(), bar=tags_[0][2]))
    for ti, t_, col in tags_:
        o.append(tag(tx(96, [XM[ti]], 30), ly(XT, ti), t_, col, k + 1))
o.append(lspot_off(4))
o.append(p(f"position:absolute;left:201px;top:{XT + cell_h({'lines': XM}) + 14:.0f}px;font-size:24px;color:{GRAY}", "이 셀도 출력이 없어요"))
CFS[0] = 30
W("x-mini", o, "미니 붕어빵은 한 개 가격과 묶음 개수가 있어요. 미니 붕어빵도 붕어빵의 한 종류라서 Bread를 물려받았어요. 자식 __init__은 맛과 가격을 super().__init__에 맡기고 개수만 붙여요. 부모 __init__ 안에서 Bread.count가 늘어나니까 미니 붕어빵을 찍어도 개수가 세져요. __str__은 묶음 가격을 보여 주도록 덮어썼어요. 이 셀도 틀만 만들어서 출력이 없어요.")

o = [sec("x-mini2")] + head(EB6, "붕어빵 메뉴판 ②: 섞어 담고 찍고 세기", K6)
CFS[0] = 26
XM2 = ['menu = [Bread("팥", 1000), MiniBread("팥", 300, 5), Bread("슈크림", 1200), MiniBread("슈크림", 400, 5)]', "for m in menu:", "    print(m)", 'print("찍은 붕어빵:", Bread.count)', "print([m.flavor for m in menu if isinstance(m, MiniBread)])"]
XO = ["팥 붕어빵 1,000원", "미니 팥 5개 1,500원", "슈크림 붕어빵 1,200원", "미니 슈크림 5개 2,000원", "찍은 붕어빵: 4", "['팥', '슈크림']"]
o += cell({"id": "c-x4", "lines": XM2, "n": 4, "out": XO}, 96, T, 1728)
OX = tx(96, XO, 40)
o.append(hl(96, T, 1728, 2, 1, "run", 1))
y1, y2 = out_span(T, 5, 0, 4)
o.append(bracket(OX - 4, y1, y2, GR, 1))
o.append(tag(OX + 26, (y1 + y2) / 2, "붕어빵마다 자기 틀의 __str__ (25)", GR, 1, lead=False))
o.append(hl(96, T, 1728, 3, 1, "mark", 2))
o.append(tag(OX, oy(T, 5, 4), "미니도 부모 __init__을 거쳐서 4개", BL, 2, ex=DELAY(300)))
o.append(hl(96, T, 1728, 4, 1, "err", 3))
o.append(tag(OX, oy(T, 5, 5), "isinstance와 컴프리헨션(23)으로 미니만", RED, 3, ex=DELAY(300)))
CFS[0] = 30
o.append(caption("24부터 26까지 배운 클래스를 한 셀에서 다 썼어요.", 880, 4))
W("x-mini2", o, "보통 붕어빵과 미니 붕어빵을 섞어 메뉴판 리스트에 담았어요. for로 print하면 붕어빵마다 자기 틀의 __str__이 불려서 미니는 묶음 가격이 나와요. 찍은 붕어빵은 미니까지 4개로 세졌어요. 미니도 super().__init__으로 부모의 __init__을 거쳤기 때문이에요. 마지막 줄은 23의 컴프리헨션과 isinstance로 미니 붕어빵의 맛만 골랐어요. 24부터 26까지 배운 클래스를 한 셀에서 다 썼어요." + REAL)

# ---------- wrap up ----------
o = [sec("trouble")] + head("정리", "막히면 오류의 마지막 줄을 봐요", RED)
TR = [("AttributeError: 'Dog' object has no attribute 'name'", "자식 __init__에서 super().__init__을 안 불렀어요", "super().__init__(...)"),
      ("TypeError: ... takes 2 positional arguments but 3 were given", "super().__init__에 self를 넣었어요", "self 빼기"),
      ("TypeError: Dog.__init__() missing ... 'breed'", "자식 클래스의 재료가 모자라요", "칸 수 맞추기, 기본값"),
      ("NameError: name 'Anmal' is not defined", "괄호 안 부모 이름 오타이거나 부모를 아직 안 만들었어요", "부모 셀 먼저 실행"),
      ("한 붕어빵만 값이 달라요", "a.shop = 으로 바꿨어요", "Bread.shop ="),
      ("개수가 0에서 안 늘어요", "self.count로 셌어요", "Bread.count"),
      ("부모 메서드를 고쳤는데 자식은 그대로예요", "자식이 같은 이름으로 덮어썼어요", "super().메서드()")]
o.append(f'<div{STAGGER(1, 90)} style="position:absolute;left:0;top:0;width:1920px;height:1080px">')
for i, (q, a_, cmd) in enumerate(TR):
    o.append(f'<div style="position:absolute;left:96px;top:{T + i * 100}px;width:1728px;height:100px;display:flex;flex-direction:row;align-items:center;gap:28px;border-bottom:2px solid {LINE}">'
             + p(f"width:40px;flex:none;font-size:30px;font-weight:900;color:{RED}", str(i + 1))
             + '<div style="flex:1;display:flex;flex-direction:column;gap:2px">' + p(f"{'font-family:' + MONO + ';' if q.isascii() else ''}font-size:26px;font-weight:700;color:{INK};white-space:nowrap", e(q)) + p(f"font-size:24px;color:{SUB}", e(a_)) + '</div>'
             + p(f"{'font-family:' + MONO + ';font-size:24px;' if cmd.isascii() else 'font-size:25px;'}font-weight:700;line-height:1.4;color:{INK};background:#E6F4EC;padding:6px 18px;border-radius:12px;white-space:pre", e(cmd)) + '</div>')
o.append('</div>')
o.append(caption("헷갈리면 \"자식 클래스에서 먼저 찾고, 없으면 부모 클래스\" 순서로 따라가 봐요.", 940, 2))
W("trouble", o, "이번 챕터에서 자주 만나는 일을 모았어요. 1번부터 3번은 자식 __init__과 super에서 생겨요. 4번은 부모 틀 이름을 틀렸거나 부모 틀 셀을 아직 실행하지 않았을 때 나요. 5번과 6번은 오류가 없어서 더 찾기 어려워요. 클래스 변수는 틀 이름으로 바꾼다는 것만 기억하세요. 7번은 자식이 덮어쓴 메서드라서 부모를 고쳐도 안 바뀌는 경우예요. super로 부모 것을 부르면 같이 바뀌어요.", ("trouble", "정리"))

o = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:80px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>']
CH = [[('shop = "1호점"', "틀에 새긴 값 (클래스 변수)", K2), ("Bread.shop = ...", "모두 한 번에 바꾸기", K2), ("class Dog(Animal):", "클래스 물려받기", CR), ("super().__init__(name)", "칸을 더할 때 부모에게 맡기기", CR)],
      [("def speak(self):", "같은 이름이면 덮어쓰기", K3), ("super().eat()", "부모 것을 부르고 조금 더", K3), ("isinstance(d, Animal)", "어떤 클래스로 만들었나", K4), ("~는 ~의 한 종류", "상속할지 고르는 말", K4)]]
o.append(f'<div{STAGGER(1, 80)} style="position:absolute;left:0;top:0;width:1920px;height:1080px">')
for col, items in enumerate(CH):
    for i, (k, d, c) in enumerate(items):
        o.append(f'<div style="position:absolute;left:{96 + col * 888}px;top:{212 + i * 128}px;width:840px;height:128px;display:flex;flex-direction:column;justify-content:center;gap:8px;border-bottom:2px solid {LINE}">'
                 + p(f"{'font-family:' + MONO + ';' if k.isascii() else ''}font-size:32px;font-weight:700;color:{c};white-space:pre", e(k))
                 + p(f"font-size:28px;color:{INK}", e(d)) + '</div>')
o.append('</div>')
o.append(p(f"position:absolute;left:96px;top:780px;width:1728px;font-size:36px;font-weight:700;line-height:1.4;color:{INK}", "객체마다 다르면 self.이름, 모두 같으면 클래스에 적어요. 한 종류면 물려받아요.", at(2)))
o.append(p(f"position:absolute;left:96px;top:860px;width:1728px;font-size:30px;line-height:1.4;color:{SUB}", "다음 27에서는 감춰 둘 칸과 밖에서 쓸 문을 나눠요.", at(2)))
W("cheatsheet", o, "이번 챕터의 내용을 한 장에 모았어요. 모두 같은 값은 틀에 적는 클래스 변수로, 바꿀 땐 틀 이름으로 바꿔요. 자식 클래스는 괄호에 부모 클래스를 적어 물려받고, 칸을 더할 땐 super().__init__으로 부모에게 맡겨요. 같은 이름의 메서드를 다시 적으면 덮어쓰고, 부모 것도 쓰고 싶으면 super()로 불러요. 상속은 자식이 부모의 한 종류일 때만 써요. 다음 27에서는 칸을 안에 감추고 메서드라는 문으로만 드나드는 캡슐화를 배워요.")

finish([(K1, "왜 필요한가", "복사해서 만든 Dog와 Cat, 틀에 새긴 값과 물려받는 클래스", "w-why", "w-big"),
        (K2, "클래스 변수", "틀에 적은 값, 한 번에 바꾸기, 개수 세기, 두 변수 비교", "cv-basic", "cv-table"),
        (K3, "상속", "Animal, Dog, Cat으로 물려받기, 더하기, 덮어쓰기, super(), 눌러 보기", "in-pass", "in-lab"),
        (K4, "복사와 상속 비교", "고칠 곳 한 군데, 한 종류일 때만", "cmp-copy", "cmp-when"),
        (K5, "오류와 함정", "super 빠짐, self 두 번, 재료 수, a.shop, self.count", "t-nosuper", "t-count"),
        (K6, "실습", "도장 카드와 VIP 카드, 붕어빵과 미니 붕어빵 메뉴판", "x-card", "x-mini2")],
       "여섯 파트로 나눴어요. 1파트는 개와 고양이 클래스를 복사로 만들 때의 문제와 큰 그림이에요. 2파트는 틀에 새기는 클래스 변수, 3파트가 중심인 상속이에요. 상속은 Animal, Dog, Cat으로 봐요. 4파트는 복사와 상속을 비교하고 언제 상속하는지 정해요. 5파트는 자주 나는 오류, 6파트는 도장 카드와 붕어빵 메뉴판 실습이에요. 파트마다 새 커널에서 위에서부터 차례로 실행해요.",
       "클래스 3 (상속과 클래스 변수)")
