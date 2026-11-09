"""Generates every slide of the encapsulation deck (27) and slides/deck.json.

Story: the 도장 카드 from chapters 24 to 26 lets anyone write kim.stamps = 100. Part 2 puts one underscore on the slot
(_stamps): a promise, not a lock. Part 3 uses two underscores on a Secret's password: Python renames it to
_Secret__password, so mypass.__password fails but mypass._Secret__password still reads it. Part 4 opens a door with a
getter and a setter that checks the value, then writes the same with @property and @password.setter. Part 5 collects the
usual traps, part 6 is a stamp card that stops at 10 and a kiosk password that changes only with the old one.
Every cell and output comes from tools/demo.sh (tools/run_nb.py runs the cells with the project kernel).

Layout rules (Stageshow skill and tools/DESIGN.md): one focal object per slide (the code cell at 30px, pictures smaller),
terms beside the code line as leader tags, said once, no empty bands, fixes drawn in place, values that change move.
Highlights (tools/HIGHLIGHT.md): SLAM and shine on the cover, value change, WIPE arrows with DELAY labels, line spotlight,
DIM steps, pen ring, one shake, code-output links, code morph (name mangling, getter to property, fix), fly, cursor on the
lab, run band, spotlight rows, MARK color pairs, pen box, pulse, COUNT, STAGGER lists. No typing effect.
Usage: python3 tools/gen.py slides
"""

import html, json, os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from highlight import (spot, spot_off, cursor, cursor_off, ring, box, underline, lspot, lspot_off, run, run_off, text,  # noqa: E402
                       link, _svg, pulse, shake, shine, grow, COUNT, SLAM, STAGGER, DIM, DELAY, WIPE, MARK, MORPH, MORPH_FROM, tok)

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
CR, CRBG = "#2F7D6B", "#E3F2EE"      # 슈크림 붕어빵 (child class)
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


def obj(name, rows, left, top, w=440, color=BR, bg=BRBG, cls="Bread", attrs="", sid=None, rh=60, empty=None, fs=28, vid=None, kw="44%"):
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
                 + p(f"width:{kw};flex:none;font-family:{MONO};font-size:{fs - 4}px;font-weight:700;color:{RED if miss else SUB};white-space:nowrap", e(k))
                 + p(f"flex:1;font-family:{MONO};font-size:{fs}px;font-weight:700;color:{RED if miss else INK};white-space:nowrap", e("없음" if miss else v), vid.get(k, "")) + '</div>')
    o.append('</div></div>')
    return "".join(o)


def obj_h(n, rh=60):
    return 66 + 28 + max(n, 1) * rh + (max(n, 1) - 1) * 8 + 6


def mold(left, top, w, title, lines, attrs="", color=MD, bg=MDBG, fs=30, tfs=34, sid=None, h=None):
    """A 붕어빵 틀 (class): a thick dashed frame, the class line on top, what it holds inside."""
    idp = f' id="{sid}"' if sid else ""
    hh = f"height:{h}px;" if h else ""
    body = "".join(p(f"font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:1.5;color:{INK};white-space:pre", e(l) if l else "&#160;") for l in lines)
    return (f'<div{idp}{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;{hh}background:{bg};border:6px dashed {color};border-radius:30px;padding:24px 34px;display:flex;flex-direction:column;gap:10px">'
            + '<div style="display:flex;flex-direction:row;align-items:center;gap:14px">' + p(f"font-size:22px;font-weight:700;color:#FFFFFF;background:{color};border-radius:10px;padding:4px 14px", "틀")
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
    deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-09T06:00:00Z"}, "lists": "css", "title": title, "order": ORDER,
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



CD, CDBG = "#1E5FA8", "#E5EEF8"      # 도장 카드 (Card)
SC, SCBG = "#3F4A63", "#E7EAF0"      # 비밀 금고 (Secret)
EB1 = "1. 왜 필요한가"
EB2 = "2. 밑줄 하나 _"
EB3 = "3. 밑줄 두 개 __"
EB4 = "4. getter와 setter"
EB5 = "5. 오류와 함정"
EB6 = "6. 실습"


def table(left, top, w, rows, widths, mono=(0,), order0=None, rh=90, head_=None, fs=30, colors=None, anim="rise"):
    """A light table like rows_list, but the columns in mono are drawn in the code font."""
    o, y = [], top
    if head_:
        o.append(f'<div style="position:absolute;left:{left}px;top:{y}px;width:{w}px;height:52px;display:flex;flex-direction:row;align-items:center;gap:24px;border-bottom:3px solid {INK}">'
                 + "".join(p(f"width:{cw}px;flex:none;font-size:26px;font-weight:700;color:{GRAY};white-space:nowrap", e(c)) for c, cw in zip(head_, widths)) + '</div>')
        y += 52
    for i, r in enumerate(rows):
        cs = ""
        for k, (c, cw) in enumerate(zip(r, widths)):
            col = colors[k] if colors and colors[k] else (SUB if k == 0 and k not in mono else INK)
            cs += p(f"width:{cw}px;flex:none;font-family:{MONO if k in mono else SANS};font-size:{fs}px;font-weight:{700 if (k == 0 or k in mono) else 500};color:{col};white-space:pre", e(c))
        o.append(f'<div{at(order0 + i if order0 else None, anim)} style="position:absolute;left:{left}px;top:{y + i * rh}px;width:{w}px;height:{rh}px;display:flex;flex-direction:row;align-items:center;gap:24px;border-bottom:2px solid {LINE}">{cs}</div>')
    return o


def code_big(left, top, s, size=40, color=INK, attrs=""):
    return p(f"position:absolute;left:{left}px;top:{top}px;font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.3;white-space:pre;color:{color}", e(s), attrs)


def cell_bottom(top, c):
    return int(top + cell_h(c))


def spot_block(order, left, top, i, n, w=1728):
    return spot(order, left + 87, top + 10 + i * LHf() - 4, w - 89, n * LHf() + 8, pad=6, r=12, dim=0.55)


# ---------- cover ----------
cover([("class Secret:", "#C7B8F2"), ("    def __init__(self):", W_), ("        self.__password = 1234", "#F2C48D"), ("", W_),
       ("mypass = Secret()", W_), ("print(mypass._Secret__password)", "#8FD8DE"), ("# 1234", "#B8E8BE")],
      "클래스 4<br>캡슐화", "칸은 안에 두고<br>문으로만 드나들기",
      "클래스 네 번째 챕터예요. 24부터 26까지 만든 붕어빵 틀과 도장 카드는 밖에서 아무 칸이나 바로 바꿀 수 있었어요. 이번에는 칸을 안에 감춰 두고, 메서드라는 문으로만 꺼내고 바꾸게 만들어요. 이걸 캡슐화라고 불러요. 밑줄 하나, 밑줄 두 개, getter와 setter, property를 차례로 봐요. 오른쪽 코드처럼 밑줄 두 개로 숨겨도 우회하는 길이 있다는 것까지 봐요.", h1size=96)

# ---------- ready ----------
o = [sec("ready")] + head("들어가기", "26에서 이어서 해요", JP)
o.append(f'<div{STAGGER(1)} style="position:absolute;left:0;top:0;width:1920px;height:1080px">')
for i, (a_, b_) in enumerate([("class, __init__, self, 메서드", "24"), ("메서드로 상태 바꾸기와 if로 막기", "25"), ("상속, super()", "26"), ("if, else", "17"), ("딕셔너리 {키: 값}", "15")]):
    o.append(f'<div style="position:absolute;left:96px;top:{230 + i * 120}px;width:760px;height:104px;display:flex;flex-direction:row;gap:24px;align-items:center;border-bottom:2px solid {LINE}">'
             + f'<x-icon name="CheckCircle" style="width:48px;height:48px;color:{GR}"></x-icon>'
             + p(f"flex:1;font-size:34px;font-weight:700;color:{INK}", e(a_))
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
W("ready", o, "09에서 만든 hello-uv 폴더를 VS Code로 열고 basics.ipynb를 다시 열어요. 24의 도장 카드에서 이어서 해요. 메서드 안에서 if로 값을 막는 건 25에서, 상속과 super는 26에서 배웠어요. 3파트에서 객체 속을 딕셔너리로 들여다보니 15의 딕셔너리 모양도 떠올려 두세요. 슬라이드의 출력은 tools/demo.sh가 hello-uv 커널에서 같은 셀을 실제로 실행한 결과예요.")

# ---------- part 1 ----------
o = [sec("w-why")] + head(EB1, "도장 수를 밖에서 아무 값으로나 바꿀 수 있어요", K1)
WY = ["class Card:", "    def __init__(self, name):", "        self.name = name", "        self.stamps = 0", "", "    def add(self):", "        self.stamps = self.stamps + 1", "",
      'kim = Card("kim")', "kim.add()", "kim.stamps = 100", "print(kim.name, kim.stamps)"]
FW = 1170
o += cell({"id": "c-w1", "lines": WY, "n": 1, "out": ["kim 100"]}, 96, T, FW)
T2 = cell_bottom(T, {"lines": WY, "out": [1]}) + 30
o += cell({"id": "c-w2", "lines": ["kim.stamps = -5", "print(kim.name, kim.stamps)"], "n": 2, "out": ["kim -5"], "attrs": at(3)}, 96, T2, FW)
o.append(hl(96, T, FW, 5, 2, "run", 1))
o.append(tag(tx(96, [WY[6]], 30), ly(T, 5.5), "도장은 add()로 한 개씩", GR, 1))
o.append(hl(96, T, FW, 10, 1, "err", 2))
o.append(tag(tx(96, [WY[10]], 30), ly(T, 10), "직접 100을 넣었어요", RED, 2))
o.append(hl(96, T2, FW, 0, 1, "err", 3))
o.append(tag(tx(96, ["kim.stamps = -5"], 30), ly(T2, 0), "음수도 들어가요", RED, 3))
RX, RW = 1290, 534
o.append(obj("kim", [("name", '"kim"'), ("stamps", "-5")], RX, T, RW, cls="Card", color=CD, bg=CDBG, vid={"stamps": ' id="w-st" data-start="1"'}))
o.append(text(2, "w-st", "100"))
o.append(text(3, "w-st", "-5"))
o.append(tag(RX, T + obj_h(2) + 80, "카드에는 오류도 경고도 없어요", RED, 4, lead=False, w=RW, size=32))
o.append(tag(RX, T + obj_h(2) + 170, "도장 열 개를 모으지 않고도\n다 채울 수 있어요", INK, 4, lead=False, w=RW, size=32, ex=DELAY(200)))
W("w-why", o, "24에서 만든 도장 카드예요. 도장은 add()로 한 개씩 찍기로 했어요. 그런데 kim.stamps = 100처럼 밖에서 칸에 바로 넣어도 아무 말이 없어요. 음수를 넣어도 그대로 들어가요. 오른쪽 kim 카드의 stamps 칸이 1에서 100, -5로 바뀌는 걸 보세요. 카드를 만든 사람은 add()로만 바꾸라고 생각했지만, 코드에는 그 약속이 어디에도 없어요. 이번 챕터는 이 칸을 안으로 감추는 방법을 배워요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p1", "왜 필요한가"))

o = [sec("w-big")] + head(EB1, "칸은 안에 감추고, 메서드라는 문으로만 드나들어요", K1)
BX, BY, BW, BH = 1000, 230, 824, 560
o.append(f'<div id="wb-obj" style="position:absolute;left:{BX}px;top:{BY}px;width:{BW}px;height:{BH}px;background:{CDBG};border:6px dashed {CD};border-radius:36px"></div>')
o.append(p(f"position:absolute;left:{BX + 40}px;top:{BY + 30}px;font-family:{MONO};font-size:34px;font-weight:700;color:{CD}", "kim (Card)"))
o.append(p(f"position:absolute;left:{BX + 250}px;top:{BY + 220}px;width:480px;height:120px;background:{CARD};border:3px solid {LINE};border-radius:18px;font-family:{MONO};font-size:44px;font-weight:700;line-height:114px;text-align:center;color:{INK}", "__stamps  2", ' id="wb-slot"'))
o.append(p(f"position:absolute;left:{BX + 250}px;top:{BY + 360}px;width:480px;text-align:center;font-size:26px;font-weight:700;color:{SUB}", "속 칸: 밖에서 안 보여요", at(1, "fade")))
# the door on the left wall
DY = BY + 230
o.append(f'<div{at(2)} style="position:absolute;left:{BX - 26}px;top:{DY}px;width:52px;height:140px;background:{GR};border-radius:14px"></div>')
o.append(p(f"position:absolute;left:{BX + 40}px;top:{DY + 40}px;font-size:28px;font-weight:700;color:{GR};white-space:nowrap", "문 = 메서드", at(2, "fade") + DELAY(150)))
# outside code
o.append(p(f"position:absolute;left:96px;top:{BY + 20}px;font-size:30px;font-weight:700;color:{SUB}", "밖의 코드"))
o.append(code_big(96, DY - 110, "kim.stamps = 100", 36, RED, at(3)))
o.append(harrow(560, DY - 100, 400, RED, WIPE(3)))
o.append(p(f"position:absolute;left:{BX - 60}px;top:{DY - 128}px;font-size:56px;font-weight:900;color:{RED}", "✕", at(3, "fade") + DELAY(400)))
o.append(code_big(96, DY + 50, "kim.add()", 36, GR, at(4)))
o.append(harrow(340, DY + 60, 600, GR, WIPE(4)))
o.append(pulse(4, "wb-slot"))
o.append(tag(96, DY + 170, "문 안에서 검사한 뒤에 칸을 바꿔요", GR, 4, lead=False, ex=DELAY(400)))
# three tools, one line each
LG = [("_stamps", "2파트: 밑줄 하나, 손대지 말자는 약속"), ("__stamps", "3파트: 밑줄 두 개, 이름이 바뀌어 숨어요"), ("get_, set_, property", "4파트: 꺼내고 넣는 문 만들기")]
for i, (k, d) in enumerate(LG):
    o.append(f'<div{at(5 + i)}{DIM("lg")} style="position:absolute;left:96px;top:{830 + i * 70}px;width:1728px;height:70px;display:flex;flex-direction:row;align-items:center;gap:30px;border-bottom:2px solid {LINE}">'
             + p(f"width:400px;flex:none;font-family:{MONO};font-size:30px;font-weight:700;color:{CD}", e(k)) + p(f"font-size:30px;font-weight:700;color:{INK}", e(d)) + '</div>')
W("w-big", o, "그림으로 먼저 봐요. 카드의 도장 칸을 안에 감춰서 밖에서 바로 손대지 못하게 하고, 메서드라는 문을 하나 열어 둬요. 밖의 코드는 kim.stamps = 100처럼 칸을 바로 바꾸지 않고 kim.add()처럼 문으로 들어와요. 문 안에서는 값이 맞는지 검사한 뒤에 칸을 바꿀 수 있어요. 이렇게 칸과 그 칸을 다루는 메서드를 한 덩어리로 묶고, 밖에는 문만 보여 주는 걸 캡슐화라고 해요. 아래 세 가지를 차례로 배워요.")

# ---------- part 2 ----------
o = [sec("u-basic")] + head(EB2, "밑줄 하나로 시작하는 칸은 안에서만 써요", K2)
UB = ["class Card:", "    def __init__(self, name):", "        self.name = name", "        self._stamps = 0", "", "    def add(self):", "        self._stamps = self._stamps + 1", "",
      "    def count(self):", "        return self._stamps", "", 'kim = Card("kim")', "kim.add()", "kim.add()", "print(kim.count())"]
FW = 1100
CB = cell_h({"lines": UB})
o += cell({"id": "c-u1", "lines": UB, "n": 1, "out": ["2"]}, 96, T, FW)
for k, (i, n, t_, col) in enumerate([(3, 1, "칸 이름 앞에 _ 하나", K2), (5, 2, "도장 찍는 문", GR), (8, 2, "도장 수를 꺼내 주는 문", GR), (12, 3, "밖에서는 문만 써요", BL)]):
    o.append(lspot(k + 1, 96 + 87, T, FW - 87, CB, T + 10 + i * LHf(), n * LHf(), bar=col))
    o.append(tag(tx(96, [UB[j] for j in range(i, i + n)], 30), ly(T, i + (n - 1) / 2), t_, col, k + 1))
o.append(lspot_off(5))
for i in (3, 6, 9):
    pre = UB[i][:UB[i].index("_stamps")]
    o.append(over(96, T, i, pre, "_stamps", K2, 5))
    if i == 6:
        pre2 = UB[i][:UB[i].index("_stamps", len(pre) + 3)]
        o.append(over(96, T, i, pre2, "_stamps", K2, 5))
o.append(obj("kim", [("name", '"kim"'), ("_stamps", "2")], 1260, T, 564, cls="Card", color=CD, bg=CDBG, attrs=at(4), vid={"_stamps": ' id="ub-st" data-start="0"'}))
o.append(text(5, "ub-st", "2"))
o.append(tag(1260, T + obj_h(2) + 60, "밖의 코드는 _stamps를 직접 적지 않았어요", K2, 5, lead=False, w=564))
W("u-basic", o, "칸 이름 앞에 밑줄을 하나 붙였어요. 파이썬에서 밑줄 하나로 시작하는 이름은 클래스 안에서만 쓰겠다는 표시예요. 카드 안의 메서드는 self._stamps를 평소처럼 읽고 바꿔요. 밖에서 쓸 수 있게 add와 count 두 메서드를 문으로 열어 뒀어요. 밖의 코드는 kim.add()와 kim.count()만 써서 도장 수 2를 꺼냈어요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p2", "밑줄 하나 _"))

o = [sec("u-sign")] + head(EB2, "밑줄 하나는 '직원만 들어와요' 표지판이에요", K2)
OX0, OY0, OW, OH = 96, 230, 1060, 640
o.append(f'<div style="position:absolute;left:{OX0}px;top:{OY0}px;width:{OW}px;height:{OH}px;background:{CARD};border:3px solid {CD};border-radius:30px;overflow:hidden">'
         + f'<div style="height:72px;background:{CD};display:flex;align-items:center;padding:0 30px">' + p(f"font-family:{MONO};font-size:34px;font-weight:700;color:#FFFFFF", "kim") + '<div style="flex:1"></div>' + p("font-size:24px;font-weight:700;color:#FFFFFF", "Card") + '</div></div>')
# outside zone (public) on the left, staff zone on the right
ZX = OX0 + 40
o.append(p(f"position:absolute;left:{ZX}px;top:{OY0 + 110}px;font-size:28px;font-weight:700;color:{GR}", "밖에서 써요", at(1, "fade")))
for i, s_ in enumerate(["name", "add()", "count()"]):
    o.append(p(f"position:absolute;left:{ZX}px;top:{OY0 + 170 + i * 110}px;width:400px;height:88px;background:#E6F4EC;border:3px solid {GR};border-radius:16px;font-family:{MONO};font-size:34px;font-weight:700;line-height:82px;padding-left:28px;color:{INK}", e(s_), at(1)))
SX = OX0 + 540
o.append(f'<div{at(2)} style="position:absolute;left:{SX}px;top:{OY0 + 110}px;width:480px;height:490px;background:{K2BG};border:4px dashed {K2};border-radius:22px"></div>')
o.append(p(f"position:absolute;left:{SX + 30}px;top:{OY0 + 140}px;font-size:28px;font-weight:700;color:#FFFFFF;background:{K2};border-radius:10px;padding:6px 18px", "직원만 들어와요", at(2)))
o.append(p(f"position:absolute;left:{SX + 40}px;top:{OY0 + 280}px;width:400px;height:88px;background:{CARD};border:3px solid {K2};border-radius:16px;font-family:{MONO};font-size:34px;font-weight:700;line-height:82px;text-align:center;color:{INK}", "_stamps", at(2)))
o.append(p(f"position:absolute;left:{SX + 40}px;top:{OY0 + 400}px;width:400px;font-size:26px;line-height:1.45;color:{SUB};text-align:center", "add와 count가\n안에서 읽고 바꿔요".replace("\n", "<br>"), at(2, "fade") + DELAY(200)))
RX = 1220
for i, (t_, d_, col) in enumerate([("표지판", "_는 '안에서만 쓸게요'라는 표시예요", K2), ("문은 안 잠겨요", "밖에서 kim._stamps로 읽고 바꿀 수는 있어요", RED), ("약속을 지켜요", "밑줄 하나짜리 이름은 밖에서 안 써요", GR)]):
    o.append(f'<div{at(3 + i)}{DIM("sg")} style="position:absolute;left:{RX}px;top:{OY0 + i * 210}px;width:604px;height:190px;display:flex;flex-direction:column;justify-content:center;gap:10px;border-bottom:2px solid {LINE}">'
             + p(f"font-size:34px;font-weight:700;color:{col}", e(t_)) + p(f"font-size:28px;line-height:1.4;color:{INK}", e(d_)) + '</div>')
o.append(caption("파이썬은 잠그지 않아요. 밑줄은 사람끼리 지키는 약속이에요.", 920, 6))
W("u-sign", o, "밑줄 하나는 가게의 '직원만 들어와요' 표지판과 같아요. 카드의 name, add, count는 밖에서 쓰라고 열어 둔 것이고, _stamps는 카드 안의 메서드만 쓰는 칸이에요. 표지판이 붙은 문은 잠겨 있지 않아요. 밖에서 kim._stamps라고 적으면 읽을 수도, 바꿀 수도 있어요. 다만 밑줄을 본 사람은 '이건 안에서 쓰는 거구나' 하고 밖에서 쓰지 않아요. 파이썬은 이걸 사람끼리 지키는 약속으로 둬요.")

o = [sec("u-outside")] + head(EB2, "밖에서 _stamps에 넣어도 오류가 나지 않아요", K2)
UO = ["kim._stamps = 100", "print(kim.count())"]
FW = 1100
o += cell({"id": "c-u2", "lines": UO, "n": 2, "out": ["100"]}, 96, T, FW)
o.append(hl(96, T, FW, 0, 1, "err", 1))
o.append(tag(tx(96, UO, 40), ly(T, 0), "표지판을 무시하고 들어갔어요", RED, 1))
o.append(ring(2, 201, int(oy(T, 2, 0) - 24), int(tw("100")), 48, RED))
o.append(tag(tx(96, ["100"], 70), oy(T, 2, 0), "add를 안 거치고 100이 됐어요", RED, 2))
RX, RW = 1240, 584
o.append(obj("kim", [("name", '"kim"'), ("_stamps", "100", K5BG)], RX, T, RW, cls="Card", color=CD, bg=CDBG, vid={"_stamps": ' id="u-st" data-start="2"'}))
o.append(text(1, "u-st", "100"))
CY = T + 330
o += table(96, CY, 1728, [["kim.stamps = 100", "1파트: 누구나 바꿔도 되는 칸처럼 보여요"], ["kim._stamps = 100", "되긴 되지만, 밑줄을 보고도 약속을 어긴 코드예요"]], [520, 1160], order0=3, rh=120, head_=["밖의 코드", "읽는 사람에게는"], fs=32)
o.append(caption("밑줄 하나는 실수를 막아 주지, 일부러 하는 사람은 못 막아요.", 900, 5))
W("u-outside", o, "앞 셀의 kim 카드에서 밖의 코드가 kim._stamps에 100을 넣었어요. 오류 없이 들어가고, count()도 100을 돌려줘요. 밑줄 하나는 자물쇠가 아니라 표지판이라서 그래요. 그래도 밑줄이 있으면 코드를 읽는 사람이 '이건 밖에서 쓰면 안 되는 칸'이라는 걸 바로 알아요. 1파트처럼 이름만 있을 땐 그 차이가 보이지 않았어요." + REAL)

# ---------- part 3 ----------
o = [sec("d-basic")] + head(EB3, "밑줄 두 개로 시작하는 칸은 밖에서 이름으로 못 찾아요", K3)
DB = ["class Secret:", "    def __init__(self):", "        self.__password = 1234", "", "mypass = Secret()", "print(mypass.__password)"]
ERR = "AttributeError: 'Secret' object has no attribute '__password'"
o += cell({"id": "c-d1", "lines": DB, "n": 1, "out": [ERR], "err": True, "oid": "d1-err"}, 96, T, 1728)
o.append(hl(96, T, 1728, 2, 1, "mark", 1))
o.append(tag(tx(96, [DB[2]], 40), ly(T, 2), "칸 이름 앞에 _ 두 개", K3, 1))
o.append(hl(96, T, 1728, 5, 1, "err", 2))
o.append(box(2, 186, int(oy(T, 6, 0) - 28), int(tw(ERR)) + 30, 56, RED))
o.append(shake(2, "d1-err"))
k = ERR.index("'__password'")
SY = cell_bottom(T, {"lines": DB, "out": [1]}) + 70
RX = 96
o.append(obj("mypass", [("??", "1234")], RX, SY, 640, cls="Secret", color=SC, bg=SCBG, attrs=at(3), rh=80, fs=34))
o.append(tag(RX + 690, SY + 66 + 14 + 40, "칸은 분명히 있어요\n그런데 이름이 __password가 아니에요", SC, 3, lead=False, w=1000, size=32))
o.append(caption("안에 1234가 있는데 왜 못 찾을까요? 두 장 뒤에서 봐요.", 920, 4))
W("d-basic", o, "이번에는 금고 Secret을 만들어요. 비밀번호 칸 이름 앞에 밑줄을 두 개 붙였어요. 밖에서 mypass.__password로 꺼내려 하니 AttributeError가 나요. Secret 객체에 __password라는 이름이 없다는 뜻이에요. 분명히 __init__에서 1234를 넣었는데 말이에요. 칸은 있지만 이름이 바뀌어 있어서 그래요. 무슨 이름으로 바뀌었는지는 두 장 뒤에서 봐요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p3", "밑줄 두 개 __"))

o = [sec("d-inside")] + head(EB3, "클래스 안의 메서드는 self.__password를 그대로 써요", K3)
DI = ["class Secret:", "    def __init__(self):", "        self.__password = 1234", "", "    def check(self, pw):", "        return self.__password == pw", "", "mypass = Secret()", "print(mypass.check(1234))", "print(mypass.check(1111))"]
DO = ["True", "False"]
FW = 1728
o += cell({"id": "c-d2", "lines": DI, "n": 2, "out": DO}, 96, T, FW)
o.append(hl(96, T, FW, 4, 2, "run", 1))
o.append(tag(tx(96, [DI[5]], 40), ly(T, 4.5), "안에서는 이름 그대로 읽혀요", GR, 1))
LX = tx(96, [DI[9]], 60)
o.append(clink(2, 96, T, 10, 8, 0, DI[8], DO[0], LX, GR))
o.append(tag(LX + 90, oy(T, 10, 0), "1234가 맞아요", GR, 2, ex=DELAY(300)))
o.append(clink(3, 96, T, 10, 9, 1, DI[9], DO[1], LX + 40, RED))
o.append(tag(LX + 90, oy(T, 10, 1), "1111은 틀려요", RED, 3, ex=DELAY(300)))
o.append(caption("밖에는 맞는지 틀린지만 알려 주고, 비밀번호는 보여 주지 않아요.", 944, 4))
W("d-inside", o, "같은 클래스 안의 메서드에서는 self.__password가 문제없이 읽혀요. check는 넣은 번호가 비밀번호와 같은지 True나 False로 돌려줘요. 밖의 코드는 비밀번호를 직접 보지 않고, check라는 문으로 맞는지만 물어봐요. 이게 캡슐화의 모양이에요. 칸은 안에 있고, 밖에는 꼭 필요한 문만 열려 있어요." + REAL)

o = [sec("d-mangle")] + head(EB3, "파이썬이 __password를 _Secret__password로 바꿔 둬요", K3)
o += cell({"id": "c-d3", "lines": ["print(mypass.__dict__)"], "n": 3, "out": ["{'_Secret__password': 1234}"]}, 96, T, 1100)
o.append(tag(tx(96, ["print(mypass.__dict__)"], 40), ly(T, 0), "객체 속 칸을 딕셔너리로 보여 줘요", SUB, 1, size=26))
o.append(underline(2, 201 + int(tw("{")), 201 + int(tw("{'_Secret__password'")), int(oy(T, 1, 0) + 24), K3))
NY = 520
o.append(p(f"position:absolute;left:96px;top:{NY - 70}px;font-size:28px;font-weight:700;color:{SUB}", "클래스 안에 적은 이름"))
o.append(p(f"position:absolute;left:96px;top:{NY}px;font-family:{MONO};font-size:72px;font-weight:700;line-height:1.3;white-space:pre;color:{INK}",
           tok("s", "self.") + tok("pw", "__password", f"color:{K3}"), ' id="mg-a"' + MORPH_FROM()))
o.append(p(f"position:absolute;left:96px;top:{NY}px;font-family:{MONO};font-size:72px;font-weight:700;line-height:1.3;white-space:pre;color:{INK}",
           tok("s", "self.") + tok("cls", "_Secret", f"color:{SC};background:#FFE08A;border-radius:10px") + tok("pw", "__password", f"color:{K3}"), MORPH(3, "mg-a")))
o.append(p(f"position:absolute;left:96px;top:{NY + 130}px;font-size:30px;font-weight:700;color:{SC}", "앞에 _클래스이름을 붙여서 저장해요", at(3, "fade") + DELAY(500)))
RY = 790
o += table(96, RY, 1728, [["mypass.__password", "그런 이름은 없어요", "AttributeError"], ["mypass._Secret__password", "바뀐 이름 그대로 적으면", "1234"]], [620, 640, 420], mono=(0, 2), order0=4, rh=90, fs=30, colors=[None, None, None])
W("d-mangle", o, "객체에 붙은 칸은 __dict__로 딕셔너리처럼 들여다볼 수 있어요. 키가 _Secret__password예요. 클래스 안에서 밑줄 두 개로 시작하는 이름을 적으면, 파이썬이 앞에 밑줄과 클래스 이름을 붙여서 저장해요. 이걸 이름 바꾸기, 영어로 name mangling이라고 해요. 그래서 밖에서 __password로 찾으면 없다고 하고, 안의 메서드에서는 파이썬이 같은 규칙으로 바꿔 읽어서 잘 찾아요. __dict__는 들여다볼 때만 쓰고 실습 코드에는 쓰지 않아요." + REAL)

o = [sec("d-bypass")] + head(EB3, "바뀐 이름을 알면 밖에서도 꺼내고 바꿀 수 있어요", K3)
B1 = ["print(mypass._Secret__password)"]
o += cell({"id": "c-d4", "lines": B1, "n": 4, "out": ["1234"]}, 96, T, 1100)
o.append(hl(96, T, 1100, 0, 1, "err", 1))
o.append(tag(tx(96, B1, 40), ly(T, 0), "바뀐 이름으로 돌아서 조회", RED, 1))
T2 = cell_bottom(T, {"lines": B1, "out": [1]}) + 40
B2 = ["mypass._Secret__password = 5678", "print(mypass.check(5678))"]
o += cell({"id": "c-d5", "lines": B2, "n": 5, "out": ["True"], "attrs": at(2)}, 96, T2, 1100)
o.append(hl(96, T2, 1100, 0, 1, "err", 2))
o.append(tag(tx(96, B2, 40), ly(T2, 0), "바꾸기까지 돼요", RED, 2))
RX, RW = 1290, 534
o.append(obj("mypass", [("_Secret__password", "5678", K5BG)], RX, T, RW, cls="Secret", color=SC, bg=SCBG, fs=28, kw="62%", vid={"_Secret__password": ' id="byp-v" data-start="1234"'}))
o.append(text(2, "byp-v", "5678"))
SY = 640
for i, (t_, d_, col) in enumerate([("자물쇠가 아니에요", "밑줄 두 개도 이름을 바꿔 둔 것뿐이에요", RED), ("그래서 쓰는 곳", "실수로 같은 이름을 쓰는 걸 막을 때 (5파트)", SC), ("우회는 하지 않아요", "_Secret__password를 밖에서 쓰는 코드는 만들지 않아요", GR)]):
    o.append(f'<div{at(3 + i)}{DIM("bp")} style="position:absolute;left:96px;top:{SY + i * 96}px;width:1728px;height:96px;display:flex;flex-direction:row;align-items:center;gap:30px;border-bottom:2px solid {LINE}">'
             + p(f"width:360px;flex:none;font-size:32px;font-weight:700;color:{col}", e(t_)) + p(f"font-size:30px;color:{INK}", e(d_)) + '</div>')
W("d-bypass", o, "앞 장에서 본 바뀐 이름 _Secret__password를 밖에서 그대로 적으면 1234가 나와요. 이렇게 돌아서 조회할 수 있어요. 값을 넣으면 비밀번호가 5678로 바뀌어서 check(5678)이 True예요. 밑줄 두 개도 자물쇠가 아니라 이름을 바꿔 둔 것뿐이에요. 파이썬에는 밖에서 절대 못 여는 칸이 없어요. 밑줄 두 개는 주로 상속한 자식 틀이 실수로 같은 이름을 덮어쓰지 않게 할 때 써요. 5파트에서 다시 봐요. 바뀐 이름을 밖에서 쓰는 건 표지판을 뜯고 들어가는 것과 같으니 실제 코드에서는 하지 않아요." + REAL)

# ---------- 이름 바꾸기: a slide students press in the browser (tools/lab_name.js) ----------
LN_CSS = ("<style>"
          "#d-lab button{font-family:" + MONO.replace("'", '"') + ";font-size:26px;font-weight:700;border-radius:14px;padding:10px 20px;cursor:pointer;border:3px solid #C9CED8;background:#FFFFFF;color:#1D2330;text-align:left}"
          "#d-lab button:disabled{opacity:.5;cursor:default}"
          "#d-lab button.ln-on{border-color:#0F7C86;background:#E2F2F3}"
          "#d-lab #ln-go{font-family:" + SANS.replace("'", '"') + ";background:#0F7C86;border-color:#0F7C86;color:#FFFFFF;text-align:center}"
          "#d-lab .ln-box{transition:box-shadow .35s,background .35s}"
          "#d-lab .ln-box.ln-show{box-shadow:0 0 0 8px rgba(15,124,134,.25)}"
          "#d-lab .ln-box.ln-ok{background:#E6F4EC}"
          "#d-lab .ln-box.ln-bad{background:#F8E6E6}"
          "#d-lab .ln-box.ln-bad p{color:#A33131!important}"
          "</style>")
o = [sec("d-lab"), LN_CSS] + head(EB3, "눌러 보기: 어떤 이름으로 저장되고, 어떤 이름으로 찾힐까요", K3)
o.append(p(f"position:absolute;left:96px;top:206px;font-size:28px;font-weight:700;color:{SUB}", "① 클래스 안에 적을 이름"))
o.append('<div id="ln-in" style="position:absolute;left:96px;top:256px;width:820px;display:flex;flex-direction:row;gap:14px">'
         + "".join(f'<button data-n="{n}"{" id=\"ln-b-in\"" if n == "__password" else ""}>self.{n}</button>' for n in ["password", "_password", "__password"]) + '</div>')
o.append(p(f"position:absolute;left:96px;top:356px;font-size:28px;font-weight:700;color:{SUB}", "② 밖에서 꺼낼 이름"))
o.append('<div id="ln-out" style="position:absolute;left:96px;top:406px;width:820px;display:flex;flex-direction:row;flex-wrap:wrap;gap:14px">'
         + "".join(f'<button data-n="{n}"{" id=\"ln-b-out\"" if n == "_Secret__password" else ""}>mypass.{n}</button>' for n in ["password", "_password", "__password", "_Secret__password"]) + '</div>')
o.append(f'<button id="ln-go" style="position:absolute;left:96px;top:600px;width:300px">③ 실행 ▶</button>')
o.append(f'<div style="position:absolute;left:980px;top:206px;width:844px;background:{CARD};border:2px solid {LINE};border-radius:20px;padding:22px 30px;display:flex;flex-direction:column">'
         + "".join(p(f"font-family:{MONO};font-size:28px;font-weight:700;line-height:1.5;white-space:pre;color:{INK}", e(l) if l else "&#160;", (' id="ln-code-in"' if "1234" in l else ' id="ln-code-out"' if l.startswith("print") else "")) for l in ["class Secret:", "    def __init__(self):", "        self.__password = 1234", "", "mypass = Secret()", "print(mypass.__password)"]) + '</div>')
o.append(f'<div id="ln-dict-box" class="ln-box" style="position:absolute;left:980px;top:540px;width:844px;height:120px;background:{CARD};border:2px solid {LINE};border-left:10px solid {K3};border-radius:20px;padding:14px 28px;display:flex;flex-direction:column;gap:6px">'
         + p(f"font-size:24px;font-weight:700;color:{K3}", "저장된 이름 (mypass.__dict__)") + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{INK};white-space:pre", "실행을 누르면 나와요", ' id="ln-dict"') + '</div>')
o.append(f'<div id="ln-res-box" class="ln-box" style="position:absolute;left:980px;top:684px;width:844px;height:150px;background:{CARD};border:2px solid {LINE};border-left:10px solid {JP};border-radius:20px;padding:14px 28px;display:flex;flex-direction:column;gap:6px">'
         + p(f"font-size:24px;font-weight:700;color:{JP}", "출력") + p(f"font-family:{MONO};font-size:24px;font-weight:700;line-height:1.4;color:{INK};white-space:pre-wrap", "실행을 누르면 나와요", ' id="ln-res"') + '</div>')
o.append(f'<div style="position:absolute;left:96px;top:870px;width:1728px;height:120px;background:{CARD};border:2px solid {LINE};border-left:10px solid {K3};border-radius:18px;padding:0 30px;display:flex;align-items:center">'
         + p(f"font-size:30px;font-weight:500;line-height:1.4;color:{INK}", "안에 적을 이름과 밖에서 꺼낼 이름을 고르고 실행을 눌러요. 브라우저로 슬라이드를 열면 눌러져요.", ' id="ln-msg"') + '</div>')
o += [cursor(1, target="ln-b-in"), cursor(2, target="ln-b-out"), cursor(3, target="ln-go"), cursor_off(4)]
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lab_name.js")) as f:
    o.append('<script type="text/slide-js">\n' + f.read() + '</script>')
W("d-lab", o, "이름이 어떻게 저장되는지 직접 눌러 보는 장이에요. 브라우저로 슬라이드를 열면 버튼이 눌러져요. 위에서 클래스 안에 적을 이름을, 아래에서 밖에서 꺼낼 이름을 고르고 실행을 눌러요. 밑줄이 없거나 하나면 적은 이름 그대로 저장되고, 밑줄 두 개면 앞에 _Secret이 붙어요. 밖에서 꺼낼 이름이 저장된 이름과 똑같아야 1234가 나와요. 처음 세 번 넘기면 커서가 누를 곳을 짚어 줘요. 누르기 전에 결과가 어떻게 나올지 수강생에게 먼저 물어보세요. 출력은 tools/demo.sh로 실제로 실행한 결과예요.")

# ---------- part 4 ----------
o = [sec("g-get")] + head(EB4, "꺼내는 문은 getter, 넣는 문은 setter예요", K4)
GS = ["class Secret:", "    def __init__(self):", "        self.__password = 1234", "", "    def get_password(self):", "        return self.__password", "",
      "    def set_password(self, new):", "        if 1000 <= new <= 9999:", "            self.__password = new", "        else:", '            print("비밀번호는 네 자리 숫자예요")', "",
      "mypass = Secret()", "print(mypass.get_password())"]
CFS[0] = 28
FW = 1180
CB = cell_h({"lines": GS})
o += cell({"id": "c-g1", "lines": GS, "n": 1, "out": ["1234"]}, 96, T - 10, FW)
for k, (i, n, t_, col) in enumerate([(4, 2, "getter: 값을 꺼내 돌려줘요", GR), (7, 5, "setter: 검사하고 넣어요", BL), (13, 2, "밖에서는 문으로", K4)]):
    o.append(lspot(k + 1, 96 + 87, T - 10, FW - 87, CB, T + i * LHf(), n * LHf(), bar=col))
    o.append(bracket(96 + FW + 14, T + i * LHf() + 4, T + (i + n) * LHf() - 4, col, k + 1))
    o.append(tag(96 + FW + 42, T + (i + n / 2) * LHf(), t_, col, k + 1, lead=False, w=540))
o.append(lspot_off(4))
CFS[0] = 30
W("g-get", o, "칸을 감췄으니 밖에서 꺼내고 넣을 문이 필요해요. 꺼내 주는 메서드를 getter, 넣어 주는 메서드를 setter라고 불러요. 이름은 보통 get_칸이름, set_칸이름으로 지어요. get_password는 비밀번호를 돌려줘요. set_password는 새 번호가 네 자리 숫자인지 if로 검사하고, 맞을 때만 칸을 바꿔요. 밖의 코드는 mypass.get_password()로 1234를 꺼냈어요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p4", "getter와 setter"))

o = [sec("g-set")] + head(EB4, "setter가 검사해서 틀린 값은 안 넣어요", K4)
GSet = ["mypass.set_password(12)", "print(mypass.get_password())", "mypass.set_password(5678)", "print(mypass.get_password())"]
GO = ["비밀번호는 네 자리 숫자예요", "1234", "5678"]
FW = 1060
o += cell({"id": "c-g2", "lines": GSet, "n": 2, "out": GO}, 96, T, FW)
RX, RW = 1240, 584
o.append(obj("mypass", [("_Secret__password", "5678")], RX, T, RW, cls="Secret", color=SC, bg=SCBG, fs=28, kw="62%", vid={"_Secret__password": ' id="gs-v" data-start="1234"'}))
for k in range(4):
    o.append(run(k + 1, 96 + 87, T + 10 + k * LHf(), FW - 89, LHf()))
o.append(tag(tx(96, GSet, 30), ly(T, 0), "12는 네 자리가 아니에요", RED, 1, ex=DELAY(200)))
o.append(tag(tx(96, GSet, 30), ly(T, 1), "그대로 1234", GRAY, 2, ex=DELAY(200)))
o.append(tag(tx(96, GSet, 30), ly(T, 2), "검사를 통과해요", GR, 3, ex=DELAY(200)))
o.append(text(3, "gs-v", "5678"))
o.append(tag(tx(96, GSet, 30), ly(T, 3), "5678로 바뀌었어요", GR, 4, ex=DELAY(200)))
o.append(run_off(5))
OY = cell_bottom(T, {"lines": GSet, "out": GO}) + 60
o.append(p(f"position:absolute;left:96px;top:{OY}px;font-size:28px;font-weight:700;color:{SUB}", "검사 없이 칸을 그대로 열어 두면 (참고)", at(5)))
PB = ["class Secret:", "    def __init__(self):", "        self.password = 1234", "", "mypass = Secret()", "mypass.password = 12", "print(mypass.password)"]
CFS[0] = 26
o += cell({"id": "c-g3", "lines": PB[4:], "out": ["12"], "attrs": at(5)}, 96, OY + 50, FW, gut=False)
o.append(tag(tx(96, PB[4:], 30), ly(OY + 50, 1), "12가 그대로 들어가요", RED, 5))
CFS[0] = 30
W("g-set", o, "실행 막대를 따라 한 줄씩 봐요. set_password(12)는 네 자리가 아니라서 안내 문구만 찍고 칸을 그대로 둬요. 그래서 get_password()는 아직 1234예요. set_password(5678)은 검사를 통과해서 칸이 5678로 바뀌어요. 아래는 비밀번호를 그냥 self.password로 열어 둔 금고예요. 이때는 12도 검사 없이 들어가요. setter를 두는 이유가 이 검사예요. 비밀번호 규칙이 바뀌어도 setter 한 곳만 고치면 돼요." + REAL)

o = [sec("p-basic")] + head(EB4, "@property를 붙이면 괄호 없이 꺼내요", K4)
PP = ["class Secret:", "    def __init__(self):", "        self.__password = 1234", "", "    @property", "    def password(self):", "        return self.__password", "", "mypass = Secret()", "print(mypass.password)"]
FW = 1240
o += cell({"id": "c-p1", "lines": PP, "n": 3, "out": ["1234"]}, 96, T, FW)
o.append(hl(96, T, FW, 4, 1, "mark", 1))
o.append(tag(tx(96, [PP[6]], 30), ly(T, 4), "def 바로 위에 붙이는 표시", BL, 1))
o.append(hl(96, T, FW, 5, 2, "run", 1))
o.append(tag(tx(96, [PP[6]], 30), ly(T, 5.5), "getter와 같은 일, 이름은 칸 이름", GR, 1, ex=DELAY(200)))
o.append(hl(96, T, FW, 9, 1, "run", 2))
o.append(tag(tx(96, [PP[9]], 30), ly(T, 9), "괄호 없이 칸처럼 읽어요", GR, 2))
MY = 860
o.append(p(f"position:absolute;left:96px;top:{MY - 60}px;font-size:28px;font-weight:700;color:{SUB}", "꺼내는 코드가 이렇게 짧아져요", at(3)))
o.append(p(f"position:absolute;left:96px;top:{MY}px;font-family:{MONO};font-size:60px;font-weight:700;line-height:1.3;white-space:pre;color:{INK}",
           tok("m", "mypass.") + tok("g", "get_", f"color:{RED}") + tok("pw", "password") + tok("pa", "()", f"color:{RED}"), ' id="pm-a"' + at(3) + MORPH_FROM()))
o.append(p(f"position:absolute;left:96px;top:{MY}px;font-family:{MONO};font-size:60px;font-weight:700;line-height:1.3;white-space:pre;color:{INK}",
           tok("m", "mypass.") + tok("pw", "password", f"color:{GR}"), MORPH(4, "pm-a")))
W("p-basic", o, "getter를 더 짧게 쓰는 방법이에요. 메서드 이름을 칸 이름 password로 짓고, def 바로 위에 @property라는 표시를 붙여요. 그러면 밖에서 mypass.password처럼 괄호 없이 칸을 읽듯 꺼내요. 안에서는 getter와 같이 감춰 둔 __password를 돌려줘요. 아래 줄에서 get_와 괄호가 빠지는 걸 보세요. @ 표시가 어떻게 동작하는지는 이 과정에서 다루지 않고, 쓰는 모양만 기억해요." + REAL)

o = [sec("p-setter")] + head(EB4, "@password.setter를 붙이면 = 으로 넣어도 검사해요", K4)
PS = ["class Secret:", "    def __init__(self):", "        self.__password = 1234", "", "    @property", "    def password(self):", "        return self.__password", "",
      "    @password.setter", "    def password(self, new):", "        if 1000 <= new <= 9999:", "            self.__password = new", "        else:", '            print("비밀번호는 네 자리 숫자예요")', "",
      "mypass = Secret()", "mypass.password = 12", "print(mypass.password)", "mypass.password = 5678", "print(mypass.password)"]
PO = ["비밀번호는 네 자리 숫자예요", "1234", "5678"]
CFS[0] = 22
FW = 1100
o += cell({"id": "c-p2", "lines": PS, "n": 4, "out": PO}, 96, 196, FW)
o.append(hl(96, 196, FW, 8, 6, "mark", 1))
o.append(tag(tx(96, [PS[13]], 24), ly(196, 10.5), "set_password와 같은 검사", BL, 1, size=26))
o.append(hl(96, 196, FW, 16, 1, "err", 2))
o.append(tag(tx(96, [PS[16]], 24), ly(196, 16), "= 으로 넣어도 setter가 불려요", RED, 2, size=26))
o.append(hl(96, 196, FW, 18, 1, "run", 3))
o.append(tag(tx(96, [PS[18]], 24), ly(196, 18), "통과", GR, 3, size=26))
CFS[0] = 30
RX = 1270
o.append(p(f"position:absolute;left:{RX}px;top:220px;font-size:28px;font-weight:700;color:{SUB}", "같은 일, 두 가지 모양", at(4)))
o += table(RX, 270, 554, [["꺼내기", "get_password()"], ["", "password"], ["넣기", "set_password(5678)"], ["", "password = 5678"]], [110, 440], mono=(1,), order0=4, rh=80, fs=28)
o.append(tag(RX, 650, "둘 다 같은 일을 해요\n밖에서 칸처럼 쓰고 싶으면 property를 골라요", K4, 5, lead=False, w=554, size=28))
W("p-setter", o, "넣는 문도 property로 만들 수 있어요. 같은 이름 password로 메서드를 하나 더 적고, 위에 @password.setter를 붙여요. 안의 검사는 set_password와 똑같아요. 이제 밖에서 mypass.password = 12처럼 칸에 넣듯 적어도 setter가 불려서 검사해요. 12는 막히고 5678은 들어가요. 오른쪽처럼 getter, setter 메서드와 property는 같은 일을 하는 두 가지 모양이에요. 밖에서 칸처럼 쓰고 싶으면 property를 골라요." + REAL)

o = [sec("cmp-table")] + head(EB4, "다섯 가지를 한 표로 비교해요", K4)
CWS = [380, 300, 330, 674]
TRo = [["self.stamps", "읽기, 바꾸기", "그대로 열림", "아무나 바꿔도 될 때 (보통은 이것)"],
       ["self._stamps", "되긴 해요", "약속", "안에서만 쓰는 칸, 자식 틀도 쓸 칸"],
       ["self.__stamps", "이름으로는 안 돼요", "이름이 바뀜", "자식 틀과 이름이 겹치면 안 될 때"],
       ["get_, set_", "메서드로", "문", "꺼내고 넣을 때 검사가 필요할 때"],
       ["@property", "칸처럼", "문", "getter, setter를 칸처럼 쓰고 싶을 때"]]
o += table(96, T, 1728, TRo, CWS, order0=None, rh=104, head_=["안에 적는 모양", "밖에서", "잠금", "언제"], fs=30, colors=[CD, None, None, None])
for i in range(len(TRo)):
    o.append(spot(i + 1, 96, T + 52 + i * 104, 1728, 104, pad=6, r=12))
o.append(spot_off(len(TRo) + 1))
o.append(caption("밑줄은 자물쇠가 아니에요. 밖에서 쓸 문을 정해 두는 게 캡슐화예요.", 870, len(TRo) + 1))
W("cmp-table", o, "지금까지 본 방법을 한 줄씩 비춰 가며 비교해요. 그냥 이름은 누구나 읽고 바꿔도 되는 칸이고, 대부분의 칸은 이렇게 둬요. 밑줄 하나는 안에서만 쓰자는 약속이에요. 자식 틀에서도 써야 하는 칸은 밑줄 하나로 둬요. 밑줄 두 개는 이름이 바뀌어서 밖에서도, 자식 틀에서도 그 이름으로는 못 찾아요. getter와 setter는 꺼내고 넣는 문이고, property는 그 문을 칸처럼 쓰게 해 줘요. 어느 것도 완전히 잠그지는 못해요. 밖에서 쓸 문을 정해 두는 방법이에요.")

# ---------- part 5 ----------
o = [sec("t-outset")] + head(EB5, "밖에서 mypass.__password = 0 이라고 적으면 새 칸이 생겨요", K5)
TO = ["class Secret:", "    def __init__(self):", "        self.__password = 1234", "", "    def check(self, pw):", "        return self.__password == pw", "",
      "mypass = Secret()", "mypass.__password = 0", "print(mypass.check(1234))", "print(mypass.__dict__)"]
TOO = ["True", "{'_Secret__password': 1234, '__password': 0}"]
FW = 1728
o += cell({"id": "c-t1", "lines": TO, "n": 1, "out": TOO}, 96, T, FW)
o.append(hl(96, T, FW, 8, 1, "err", 1))
o.append(tag(tx(96, [TO[8]], 40), ly(T, 8), "비밀번호를 0으로 바꾼 줄 알았어요", RED, 1))
o.append(tag(tx(96, ["True"], 40), oy(T, 11, 0), "1234가 아직 맞아요", GR, 2))
OO = TOO[1]
a0 = OO.index("'_Secret__password'"); a1 = OO.index("1234") + 4
b0 = OO.index("'__password'"); b1 = len(OO) - 1
yy = oy(T, 11, 1) - LHf() / 2
o.append(p(f"position:absolute;left:{201 + tw(OO[:a0]):.1f}px;top:{yy:.1f}px;font-family:{MONO};font-size:30px;line-height:1.45;white-space:pre;color:{SC};background:{SCBG};border-radius:6px", e(OO[a0:a1]), MARK(3)))
o.append(p(f"position:absolute;left:{201 + tw(OO[:b0]):.1f}px;top:{yy:.1f}px;font-family:{MONO};font-size:30px;line-height:1.45;white-space:pre;color:{RED};background:{K5BG};border-radius:6px", e(OO[b0:b1]), MARK(4)))
o.append(tag(201 + int(tw(OO[:a0])), yy + 90, "진짜 비밀번호 칸", SC, 3, lead=False, size=26))
o.append(tag(201 + int(tw(OO[:b0])), yy + 90, "밖에서 새로 붙은 칸", RED, 4, lead=False, size=26))
o.append(caption("이름 바꾸기는 클래스 안에서만 일어나요. 밖에서 적은 __password는 그냥 새 칸이에요.", 944, 5))
W("t-outset", o, "밖에서 mypass.__password = 0이라고 적었어요. 오류가 안 나니까 비밀번호가 바뀐 것 같지만, check(1234)는 여전히 True예요. __dict__를 보면 칸이 두 개예요. 이름 바꾸기는 클래스 안에 적은 이름에만 일어나요. 밖에서 적은 __password는 바뀌지 않고, 24에서 점으로 칸을 붙인 것처럼 새 칸이 하나 생겨요. 26의 a.shop = 함정과 비슷해요. 비밀번호를 바꾸려면 setter를 써요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p5", "오류와 함정"))

o = [sec("t-child")] + head(EB5, "자식 틀에서 부모의 __stamps를 쓰면 이름이 달라서 못 찾아요", K5)
TC = ["class Card:", "    def __init__(self, name):", "        self.name = name", "        self.__stamps = 0", "", "    def add(self):", "        self.__stamps = self.__stamps + 1", "",
      "class VipCard(Card):", "    def add(self):", "        self.__stamps = self.__stamps + 2", "", 'lee = VipCard("lee")', "lee.add()"]
ERR = "AttributeError: 'VipCard' object has no attribute '_VipCard__stamps'"
CFS[0] = 28
FW = 1728
o += cell({"id": "c-t2", "lines": TC, "n": 2, "out": [ERR], "err": True}, 96, 196, FW)
o.append(hl(96, 196, FW, 3, 1, "mark", 1))
o.append(tag(tx(96, [TC[6]], 30), ly(196, 3), "Card 안: _Card__stamps로 저장", SC, 1, size=26))
o.append(hl(96, 196, FW, 10, 1, "err", 2))
o.append(tag(tx(96, [TC[10]], 30), ly(196, 10), "VipCard 안: _VipCard__stamps를 찾아요", RED, 2, size=26))
k = ERR.index("'_VipCard__stamps'")
o.append(underline(3, int(201 + tw(ERR[:k])), int(201 + tw(ERR[:k + 18])), int(oy(196, 14, 0) + 22), RED))
CFS[0] = 30
FY = 950
o.append(mfix(96, FY, "tc-bad", [(None, "self."), (None, "__"), ("st", "stamps")], [(None, "self."), ("u", "_"), ("st", "stamps")], 5, size=30, label="부모와 자식이 같이 쓰는 칸은 밑줄 하나로"))
o.append(p(f"position:absolute;left:760px;top:{FY + 8}px;font-size:28px;color:{SUB}", "고친 뒤 lee.add() 하면 lee._stamps는 2 (실행 결과)", at(5, "fade")))
W("t-child", o, "26의 VIP 카드처럼 Card를 물려받아 add를 덮어썼어요. 부모 Card 안에 적은 __stamps는 _Card__stamps로 저장돼요. 자식 VipCard 안에 적은 __stamps는 _VipCard__stamps로 바뀌어서, 그런 칸이 없다는 AttributeError가 나요. 밑줄 두 개는 원래 자식 틀이 같은 이름을 써도 서로 부딪히지 않게 하려고 만든 거라서 그래요. 부모와 자식이 같이 쓰는 칸은 밑줄 하나로 적어요. 고치고 다시 실행하면 lee._stamps가 2예요." + REAL)

o = [sec("t-paren")] + head(EB5, "property에 괄호를 붙이면 'int' object is not callable", K5)
TP = ["class Card:", "    def __init__(self, name):", "        self.name = name", "        self.__stamps = 0", "", "    @property", "    def stamps(self):", "        return self.__stamps", "", 'kim = Card("kim")', "print(kim.stamps())"]
ERR = "TypeError: 'int' object is not callable"
FW = 1728
o += cell({"id": "c-t3", "lines": TP, "n": 3, "out": [ERR], "err": True}, 96, T, FW)
o.append(hl(96, T, FW, 10, 1, "err", 1))
o.append(tag(tx(96, [TP[10]], 40), ly(T, 10), "메서드처럼 괄호를 붙였어요", RED, 1))
o.append(box(2, 186, int(oy(T, 11, 0) - 28), int(tw(ERR)) + 30, 56, RED))
o.append(tag(tx(96, [ERR], 60), oy(T, 11, 0), "kim.stamps가 벌써 0이라서 0()이 돼요", RED, 2))
FY = cell_bottom(T, {"lines": TP, "out": [1]}) + 60
o.append(fix(96, FY, "print(kim.stamps())", "print(kim.stamps)", 3, w=1728))
W("t-paren", o, "property로 만든 stamps에 메서드처럼 괄호를 붙였어요. kim.stamps는 이미 메서드가 불려서 숫자 0이 돼요. 그 뒤에 괄호가 붙으니 0()처럼 숫자를 함수처럼 부른 셈이라 TypeError가 나요. callable은 괄호로 부를 수 있다는 뜻이에요. property는 괄호 없이 kim.stamps로 써요." + REAL)

o = [sec("t-noset")] + head(EB5, "setter가 없는 property에 넣으면 has no setter", K5)
ERR = "AttributeError: property 'stamps' of 'Card' object has no setter"
o += cell({"id": "c-t4", "lines": ["kim.stamps = 100"], "n": 4, "out": [ERR], "err": True}, 96, T, 1728)
o.append(hl(96, T, 1728, 0, 1, "err", 1))
o.append(tag(tx(96, ["kim.stamps = 100"], 40), ly(T, 0), "앞 장의 kim, getter만 있어요", RED, 1))
k = ERR.index("has no setter")
o.append(underline(2, int(201 + tw(ERR[:k])), int(201 + tw(ERR)), int(oy(T, 1, 0) + 24), RED))
DY = 470
o.append(f'<div id="ns-door" style="position:absolute;left:96px;top:{DY}px;width:820px;height:300px;background:{CDBG};border:4px solid {CD};border-radius:28px"></div>')
o.append(p(f"position:absolute;left:136px;top:{DY + 30}px;font-family:{MONO};font-size:32px;font-weight:700;color:{CD}", "kim.stamps"))
o.append(p(f"position:absolute;left:136px;top:{DY + 110}px;width:740px;height:66px;background:#E6F4EC;border:3px solid {GR};border-radius:14px;font-size:30px;font-weight:700;line-height:60px;padding-left:24px;color:{INK}", "✓ 꺼내는 문 (@property)"))
o.append(p(f"position:absolute;left:136px;top:{DY + 196}px;width:740px;height:66px;background:{CARD};border:3px dashed {RED};border-radius:14px;font-size:30px;font-weight:700;line-height:60px;padding-left:24px;color:{RED}", "✕ 넣는 문 없음", ' id="ns-set"'))
o.append(pulse(3, "ns-set"))
o.append(tag(980, DY + 60, "읽기만 열어 둔 칸이에요", CD, 3, lead=False))
o.append(tag(980, DY + 140, "도장 수처럼 밖에서 바꾸면 안 되는 값은 일부러 이렇게 둬요", INK, 4, lead=False, w=844, size=28))
o.append(tag(980, DY + 250, "바꾸게 하려면 @stamps.setter나 add() 같은 메서드를 만들어요", GR, 5, lead=False, w=844, size=28))
o.append(caption("오류처럼 보여도, 읽기만 열어 둔 것도 캡슐화예요.", 900, 5))
W("t-noset", o, "앞 장의 Card는 @property로 꺼내는 문만 만들었어요. 밖에서 kim.stamps = 100이라고 넣으면 setter가 없다는 AttributeError가 나요. 이건 고장이 아니라 일부러 읽기만 열어 둔 거예요. 도장 수는 add()로만 늘어나야 하니 넣는 문을 만들지 않았어요. 밖에서 바꾸게 하고 싶으면 4파트처럼 @stamps.setter를 만들거나, add() 같은 메서드를 둬요." + REAL)

# ---------- part 6 ----------
o = [sec("x-card")] + head(EB6, "도장 카드 ①: 열 개에서 멈추고, 읽기만 열어 두기", K6)
XC = ["class Card:", "    goal = 10", "", "    def __init__(self, name):", "        self.name = name", "        self.__stamps = 0", "", "    def add(self):", "        if self.__stamps < Card.goal:", "            self.__stamps = self.__stamps + 1", "",
      "    @property", "    def stamps(self):", "        return self.__stamps", "", "    def __str__(self):", '        return f"{self.name}: 도장 {self.__stamps}/{Card.goal}"']
CFS[0] = 28
XT = 200
CB = cell_h({"lines": XC})
o += cell({"id": "c-x1", "lines": XC, "n": 1}, 96, XT, 1728)
for k, (i, n, kind, ti, t_, col) in enumerate([(5, 1, "mark", 5, "도장 칸은 밑줄 두 개로 감춰요", BL), (7, 3, "run", 8, "문 안에서 열 개를 넘지 않게 검사", GR), (11, 3, "err", 11, "읽기만: setter는 일부러 안 만들어요", RED)]):
    o.append(hl(96, XT, 1728, i, n, kind, k + 1))
    o.append(lspot(k + 1, 96 + 87, XT, 1728 - 87, CB, XT + 10 + i * LHf(), n * LHf(), bar=col))
    o.append(tag(tx(96, [XC[ti]], 30), ly(XT, ti), t_, col, k + 1))
o.append(lspot_off(4))
o.append(p(f"position:absolute;left:201px;top:{XT + CB + 14:.0f}px;font-size:24px;color:{GRAY}", "출력 없이 틀만 만드는 셀이에요"))
CFS[0] = 30
W("x-card", o, "도장 카드를 캡슐화해서 완성해요. 도장 칸은 밑줄 두 개로 감췄어요. add는 25에서 배운 것처럼 if로 막아서, 목표 열 개를 넘으면 더 찍지 않아요. 도장 수는 property로 읽기만 열어 두고 setter는 만들지 않았어요. __str__은 25처럼 카드를 글자로 보여 줘요. 이 셀은 틀만 만들어서 출력이 없어요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요.", ("p6", "실습"))

o = [sec("x-card2")] + head(EB6, "도장 카드 ②: 열두 번 찍어도 열 개", K6)
XC2 = ['kim = Card("kim")', "for i in range(12):", "    kim.add()", "print(kim)", "print(kim.stamps)"]
XO2 = ["kim: 도장 10/10", "10"]
FW = 1000
CFS[0] = 36
o += cell({"id": "c-x2", "lines": XC2, "n": 2, "out": XO2}, 96, T, FW)
o.append(hl(96, T, FW, 1, 2, "run", 1))
o.append(tag(tx(96, XC2, 30), ly(T, 1.5), "add를 열두 번", GR, 1))
RX, RW = 1180, 644
o.append(f'<div style="position:absolute;left:{RX}px;top:{T}px;width:{RW}px;height:300px;background:{CARD};border:3px solid {CD};border-radius:26px;overflow:hidden">'
         + p(f"position:absolute;left:32px;top:22px;font-family:{MONO};font-size:30px;font-weight:700;color:{CD}", "kim.stamps")
         + p(f"position:absolute;left:0;top:80px;width:{RW - 6}px;height:180px;text-align:center;font-family:{MONO};font-size:150px;font-weight:700;line-height:180px;color:{INK}", "10", COUNT(2, 1800)) + '</div>')
o.append(tag(RX, T + 350, "11번째, 12번째 add는 if에서 막혀요", RED, 3, lead=False, w=RW))
o.append(tag(tx(96, XO2, 40), oy(T, 5, 0), "__str__", SUB, 4, size=26))
o.append(tag(tx(96, XO2, 40), oy(T, 5, 1), "property로 꺼낸 값", SUB, 4, size=26))
CFS[0] = 30
o.append(caption("밖의 코드는 add()와 stamps만 알면 돼요. 칸이 어떻게 생겼는지는 몰라도 돼요.", 900, 5))
W("x-card2", o, "앞 셀의 틀로 kim 카드를 만들고 18에서 배운 range로 add를 열두 번 불렀어요. 열한 번째부터는 if에서 막혀서 도장은 열 개에서 멈춰요. print(kim)은 __str__을, kim.stamps는 property를 거쳐서 10을 보여 줘요. 밖의 코드는 add()와 stamps만 알면 돼요. 나중에 도장 칸 모양을 바꿔도 이 두 문만 그대로면 밖의 코드는 안 고쳐도 돼요." + REAL)

o = [sec("x-lock")] + head(EB6, "키오스크 비밀번호 ①: 옛 번호를 알아야 바꿔요", K6)
XK = ["class Kiosk:", "    def __init__(self, password):", "        self.__password = password", "", "    def login(self, pw):", "        if pw == self.__password:", '            print("관리자 화면을 열어요")', "        else:", '            print("비밀번호가 틀렸어요")', "",
      "    def change(self, old, new):", "        if old == self.__password:", "            self.__password = new", '            print("비밀번호를 바꿨어요")', "        else:", '            print("지금 비밀번호가 틀려서 못 바꿔요")']
CFS[0] = 28
CB = cell_h({"lines": XK})
o += cell({"id": "c-x3", "lines": XK, "n": 3}, 96, XT, 1728)
for k, (i, n, col, t_) in enumerate([(2, 1, BL, "재료로 받은 번호를 감춰요"), (4, 5, GR, "맞는지만 확인해요"), (10, 6, OR, "옛 번호가 맞을 때만 바꿔요")]):
    o.append(spot_block(k + 1, 96, XT, i, n))
    o.append(tag(tx(96, [XK[j] for j in range(i, i + n)], 30), ly(XT, i + (n - 1) / 2), t_, col, k + 1))
o.append(spot_off(4))
o.append(p(f"position:absolute;left:201px;top:{XT + CB + 14:.0f}px;font-size:24px;color:{GRAY}", "이 셀도 출력이 없어요"))
CFS[0] = 30
W("x-lock", o, "카페 키오스크의 관리자 비밀번호를 금고처럼 만들어요. 만들 때 받은 번호를 밑줄 두 개로 감춰요. getter는 일부러 만들지 않았어요. 비밀번호는 밖에서 꺼내 볼 일이 없으니까요. login은 맞는지만 확인하고, change는 지금 번호를 맞혀야 새 번호로 바꿔요. setter에 검사를 넣은 것과 같은 생각이에요. 이 셀도 틀만 만들어서 출력이 없어요.")

o = [sec("x-lock2")] + head(EB6, "키오스크 비밀번호 ②: 틀리면 안 열리고 안 바뀌어요", K6)
XK2 = ["k = Kiosk(1234)", "k.login(1111)", "k.change(1111, 5678)", "k.change(1234, 5678)", "k.login(5678)"]
XKO = ["비밀번호가 틀렸어요", "지금 비밀번호가 틀려서 못 바꿔요", "비밀번호를 바꿨어요", "관리자 화면을 열어요"]
FW = 1040
CFS[0] = 34
o += cell({"id": "c-x4", "lines": XK2, "n": 4, "out": XKO}, 96, T, FW)
RX, RW = 1180, 644
o.append(obj("k", [("_Kiosk__password", "5678")], RX, T, RW, cls="Kiosk", color=SC, bg=SCBG, fs=28, kw="62%", vid={"_Kiosk__password": ' id="kk-v" data-start="1234"'}))
for k in range(4):
    o.append(run(k + 1, 96 + 87, T + 10 + (k + 1) * LHf(), FW - 89, LHf()))
o.append(text(3, "kk-v", "5678"))
OXk = tx(96, XKO, 30)
for j, (t_, col) in enumerate([("✕ 로그인", RED), ("✕ 변경", RED), ("✓ 변경", GR), ("✓ 로그인", GR)]):
    o.append(tag(OXk, oy(T, 5, j), t_, col, j + 1, lead=False, size=30, ex=DELAY(250)))
o.append(run_off(5))
CFS[0] = 30
o.append(tag(RX, T + obj_h(1) + 60, "칸이 바뀐 건 옛 번호를 맞힌 한 번뿐이에요", SC, 5, lead=False, w=RW))
o.append(caption("밖의 코드는 비밀번호를 한 번도 꺼내 보지 않았어요.", 900, 5))
W("x-lock2", o, "1234로 키오스크를 만들고 차례로 불러 봐요. 실행 막대를 따라가면, 1111로는 로그인도 안 되고 번호를 바꾸지도 못해요. 1234를 맞히자 5678로 바뀌고, 그 뒤로는 5678로 열려요. 오른쪽 칸이 바뀐 건 옛 번호를 맞힌 그 한 줄뿐이에요. 밖의 코드는 비밀번호를 한 번도 꺼내 보지 않고 login과 change라는 문만 썼어요." + REAL)

# ---------- wrap up ----------
o = [sec("trouble")] + head("정리", "막히면 오류의 마지막 줄을 봐요", RED)
TR = [("AttributeError: 'Secret' object has no attribute '__password'", "밑줄 두 개짜리 칸을 밖에서 이름으로 찾았어요", "getter, property"),
      ("AttributeError: ... no attribute '_VipCard__stamps'", "자식 틀에서 부모의 __칸을 썼어요", "밑줄 하나 _stamps"),
      ("TypeError: 'int' object is not callable", "property에 괄호를 붙였어요", "kim.stamps"),
      ("AttributeError: property 'stamps' of 'Card' object has no setter", "읽기만 연 property에 넣었어요", "@stamps.setter, 메서드"),
      ("밖에서 __password = 0 했는데 안 바뀌어요", "밖에서는 이름이 안 바뀌어서 새 칸이 생겼어요", "setter로 바꾸기"),
      ("_stamps를 밖에서 바꿨더니 값이 이상해요", "약속을 어기고 검사를 건너뛰었어요", "add() 같은 메서드로")]
o.append(f'<div{STAGGER(1, 90)} style="position:absolute;left:0;top:0;width:1920px;height:1080px">')
for i, (q, a_, cmd) in enumerate(TR):
    o.append(f'<div style="position:absolute;left:96px;top:{T + i * 110}px;width:1728px;height:110px;display:flex;flex-direction:row;align-items:center;gap:28px;border-bottom:2px solid {LINE}">'
             + p(f"width:40px;flex:none;font-size:30px;font-weight:900;color:{RED}", str(i + 1))
             + '<div style="flex:1;display:flex;flex-direction:column;gap:2px">' + p(f"{'font-family:' + MONO + ';' if q.isascii() else ''}font-size:26px;font-weight:700;color:{INK};white-space:nowrap", e(q)) + p(f"font-size:24px;color:{SUB}", e(a_)) + '</div>'
             + p(f"{'font-family:' + MONO + ';font-size:24px;' if cmd.replace(',', '').replace(' ', '').isascii() else 'font-size:25px;'}font-weight:700;line-height:1.4;color:{INK};background:#E6F4EC;padding:6px 18px;border-radius:12px;white-space:pre", e(cmd)) + '</div>')
o.append('</div>')
o.append(caption("헷갈리면 __dict__로 실제 저장된 이름을 들여다봐요.", 920, 2))
W("trouble", o, "이번 챕터에서 자주 만나는 일을 모았어요. 1번은 감춘 칸을 밖에서 찾을 때예요. getter나 property를 만들어 꺼내요. 2번은 자식 틀에서 부모의 밑줄 두 개짜리 칸을 쓸 때예요. 같이 쓰는 칸은 밑줄 하나로 둬요. 3번과 4번은 property에서 나요. 5번과 6번은 오류가 없어서 더 찾기 어려워요. 헷갈리면 __dict__로 실제로 어떤 이름이 저장됐는지 들여다봐요.", ("trouble", "정리"))

o = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:80px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>']
CH = [[("self._stamps", "안에서만 쓰자는 약속", K2), ("self.__password", "이름이 _Secret__password로 바뀌어요", K3), ("mypass._Secret__password", "알면 우회할 수 있어요. 쓰지는 않아요", RED), ("__dict__", "저장된 이름 들여다보기", SUB)],
      [("get_password(), set_password()", "꺼내는 문, 검사하고 넣는 문", K4), ("@property", "괄호 없이 칸처럼 꺼내기", K4), ("@password.setter", "= 으로 넣어도 검사하기", K4), ("setter 없는 property", "읽기만 열어 두기", K6)]]
o.append(f'<div{STAGGER(1, 80)} style="position:absolute;left:0;top:0;width:1920px;height:1080px">')
for col, items in enumerate(CH):
    for i, (k, d, c) in enumerate(items):
        o.append(f'<div style="position:absolute;left:{96 + col * 888}px;top:{212 + i * 128}px;width:840px;height:128px;display:flex;flex-direction:column;justify-content:center;gap:8px;border-bottom:2px solid {LINE}">'
                 + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:{c};white-space:pre", e(k))
                 + p(f"font-size:28px;color:{INK}", e(d)) + '</div>')
o.append('</div>')
o.append(p(f"position:absolute;left:96px;top:780px;width:1728px;font-size:36px;font-weight:700;line-height:1.4;color:{INK}", "칸은 안에 두고, 밖에는 문만 열어 둬요. 파이썬의 밑줄은 자물쇠가 아니라 약속이에요.", at(2)))
o.append(p(f"position:absolute;left:96px;top:860px;width:1728px;font-size:30px;line-height:1.4;color:{SUB}", "24부터 27까지 붕어빵 틀과 도장 카드로 클래스를 만들고, 꾸미고, 물려받고, 감췄어요.", at(2)))
W("cheatsheet", o, "이번 챕터를 한 장에 모았어요. 밑줄 하나는 안에서만 쓰자는 약속, 밑줄 두 개는 이름이 바뀌어 숨는 칸이에요. 바뀐 이름을 알면 밖에서도 꺼낼 수 있으니 자물쇠는 아니에요. 밖에서 꺼내고 넣을 일이 있으면 getter와 setter로 문을 만들고, setter에서 값을 검사해요. property를 쓰면 같은 문을 칸처럼 쓸 수 있고, setter를 안 만들면 읽기만 열려요. 24부터 27까지 클래스 네 챕터를 마쳤어요.")

finish([(K1, "왜 필요한가", "아무 값이나 들어가는 도장 칸, 칸과 문 그림", "w-why", "w-big"),
        (K2, "밑줄 하나 _", "안에서만 쓰는 칸, 표지판, 밖에서도 바뀌어요", "u-basic", "u-outside"),
        (K3, "밑줄 두 개 __", "못 찾는 이름, 바뀐 이름, 우회해서 조회, 눌러 보기", "d-basic", "d-lab"),
        (K4, "getter와 setter", "꺼내는 문과 검사하는 문, 괄호 없이, 한 표 비교", "g-get", "cmp-table"),
        (K5, "오류와 함정", "밖에서 붙은 새 칸, 자식 틀, 괄호, setter 없음", "t-outset", "t-noset"),
        (K6, "실습", "열 개에서 멈추는 도장 카드, 키오스크 비밀번호", "x-card", "x-lock2")],
       "여섯 파트로 나눴어요. 1파트는 밖에서 아무 값이나 넣을 수 있는 문제와 큰 그림이에요. 2파트는 밑줄 하나, 3파트는 밑줄 두 개와 우회하는 길이에요. 4파트는 getter, setter와 property로 문을 만들어요. 5파트는 자주 나는 오류, 6파트는 도장 카드와 키오스크 실습이에요. 파트마다 새 커널에서 위에서부터 차례로 실행해요.",
       "클래스 4 (캡슐화)")
