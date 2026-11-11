"""Generates every slide of the shopping-cart deck (28) and slides/deck.json.

Story: the class's mini project (product.py, cart.py) holds three things students mix up. Part 2 reads indentation
as boxes inside boxes (class, def, if/for) on cart.py itself. Part 3 starts from a, b = (1, 2) and walks to
for p, q in self.items.items(). Part 4 asks why the code is split into files and shows import, from x import y, z,
as, and their errors. Part 5 finds cart.py's unguarded test code printing inside main.py and fixes it with
if __name__ == "__main__":. Part 6 runs a whole order from main.py and adds a coupon.py module.
Every file and output comes from tools/scenes.py run by tools/demo.sh (tools/out.json).

Layout rules (Stageshow skill and tools/DESIGN.md): one focal object per slide (the file at 28px, the terminal beside or
under it), terms beside the code line as leader tags, said once, no empty bands, fixes drawn in place, values that move.
Highlights (tools/HIGHLIGHT.md): SLAM and shine on the cover, nested box reveal, pen box and ring, MARK color pairs,
run band, code morph, keycaps, fly, value change, line spotlight, WIPE arrows with DELAY labels, DIM steps,
code-output links, spotlight rows, pan, one shake, one zoom, COUNT, STAGGER lists. No typing effect.
Usage: python3 tools/gen.py slides
"""

import html, json, os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from highlight import (spot, spot_off, cursor, cursor_off, ring, box, underline, lspot, lspot_off, run, run_off, text,  # noqa: E402
                       link, _svg, pulse, shake, shine, grow, zoom, zoom_off, pan, keys, COUNT, SLAM, STAGGER, DIM, DELAY, WIPE, MARK, MORPH, MORPH_FROM, tok)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scenes import SCENES, PRODUCT, CART, CART_GUARDED, CART_BODY, COUPON, SHOW_IN, RET_OUT, MAIN_SHOP, MAIN_COUPON  # noqa: E402

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
INK, SUB, LINE, CARD = "#1D2330", "#4A5262", "#E1DED6", "#FFFFFF"
BL, GR, OR, PUR, RED, TEAL, GRAY = "#2459C9", "#1F8A4C", "#B26A00", "#5A3BB8", "#A33131", "#0F7C86", "#6A7180"
JP = "#B8560F"          # Jupyter, same as chapters 09 and 10
SEL = "#2F7DE1"         # selected cell bar, like VS Code's focus color
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
KO = lambda s: any('가' <= ch <= '힣' for ch in s)
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
    return f'<section id="{sid}" data-transition="{transition}" style="background:{bg};color:{INK};font-family:{SANS};font-variant-ligatures:none;word-break:keep-all;padding:96px;display:flex;flex-direction:column">'


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
    t.append(p(f"position:absolute;left:96px;top:944px;width:1728px;font-size:28px;color:{SUB}", f"{page['ready']}쪽은 프로젝트 준비, {page['trouble']}–{page['cheatsheet']}쪽은 막힐 때와 한 장 요약이에요."))
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
            cs += p(f"width:{cw}px;flex:none;font-family:{MONO if (k in mono and not KO(c)) else SANS};font-size:{fs}px;font-weight:{700 if (k == 0 or k in mono) else 500};color:{col};white-space:pre", e(c))
        o.append(f'<div{at(order0 + i if order0 else None, anim)} style="position:absolute;left:{left}px;top:{y + i * rh}px;width:{w}px;height:{rh}px;display:flex;flex-direction:row;align-items:center;gap:24px;border-bottom:2px solid {LINE}">{cs}</div>')
    return o


def code_big(left, top, s, size=40, color=INK, attrs=""):
    return p(f"position:absolute;left:{left}px;top:{top}px;font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.3;white-space:pre;color:{color}", e(s), attrs)


def cell_bottom(top, c):
    return int(top + cell_h(c))


def spot_block(order, left, top, i, n, w=1728):
    return spot(order, left + 87, top + 10 + i * LHf() - 4, w - 89, n * LHf() + 8, pad=6, r=12, dim=0.55)




# ================= chapter 28 =================
HERE = os.path.dirname(os.path.abspath(__file__))
OUTS = json.load(open(os.path.join(HERE, "out.json")))
REAL = " 출력은 tools/demo.sh로 실제로 실행한 결과예요."


def out(scene, k=0):
    return OUTS[scene][k]["out"]


def cmd(scene, k=0):
    return OUTS[scene][k]["cmd"]


def L(text):
    return text.rstrip("\n").split("\n")


PL, CL, GL = L(PRODUCT), L(CART), L(CART_GUARDED)


def rng(lines, a, b):
    """Lines a..b of a file, counted from 1 like the editor's line numbers."""
    return lines[a - 1:b]


def ded(lines, n):
    """The same lines with n leading spaces taken off (to show a method's inside at a readable size)."""
    return [l[n:] if l.startswith(" " * n) else l for l in lines]


def etw(s, fs):
    return sum(fs * (1.0 if '가' <= ch <= '힣' else 0.6) for ch in s)


TABH = 56
KO = lambda s: any('가' <= ch <= '힣' for ch in s)


def editor(eid, name, lines, left, top, w, fs=26, nums=None, attrs="", color=BL, h=None, start=1):
    """A VS Code-like file: a tab with the file name, gray line numbers, the code. Returns (html, geometry).
    nums: list of line labels, False for none, None for start, start+1, ... A line "⋮" draws a gray gap."""
    lh = fs * 1.45
    gw = 0 if nums is False else 70
    labels = [] if nums is False else (nums or [str(start + i) for i in range(len(lines))])
    hh = h or (TABH + 36 + len(lines) * lh)
    o = [f'<div id="{eid}"{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{hh:.0f}px;background:{CARD};border:2px solid {LINE};border-radius:16px;overflow:hidden">',
         f'<div style="position:absolute;left:0;top:0;width:{w}px;height:{TABH}px;background:#EEF0F3;border-bottom:2px solid {LINE}"></div>',
         p(f"position:absolute;left:0;top:0;height:{TABH}px;padding:0 26px;background:{CARD};border-right:2px solid {LINE};border-top:4px solid {color};font-family:{MONO};font-size:24px;font-weight:700;line-height:{TABH - 6}px;color:{INK};white-space:nowrap", e(name))]
    if gw:
        o.append(f'<div style="position:absolute;left:0;top:{TABH + 16}px;width:{gw}px">' + "".join(
            p(f"height:{lh:.2f}px;font-family:{MONO};font-size:{fs * 0.8:.0f}px;line-height:{lh:.2f}px;text-align:right;padding-right:6px;color:#A3A9B4", "" if l == "⋮" else e(n))
            for n, l in zip(labels, lines)) + '</div>')
    body = "".join(p(f"height:{lh:.2f}px;font-family:{SANS if l == '⋮' else MONO};font-size:{fs}px;line-height:{lh:.2f}px;white-space:pre;color:{GRAY if l == '⋮' else INK}", e(l) if l else "&#160;") for l in lines)
    o.append(f'<div style="position:absolute;left:{gw}px;top:{TABH}px;right:0;padding:16px 24px;background:{CARD};display:flex;flex-direction:column">{body}</div>')
    o.append('</div>')
    g = {"left": left, "top": top, "w": w, "fs": fs, "lh": lh, "tx": left + 2 + gw + 24, "y0": top + 2 + TABH + 16, "h": hh, "n": len(lines)}
    return "".join(o), g


def gly(g, i):
    """Center y of line i (from 0) of an editor or terminal."""
    return g["y0"] + i * g["lh"] + g["lh"] / 2


def gtop(g, i):
    return g["y0"] + i * g["lh"]


def gx(g, s):
    """x right after the text s drawn from the start of a line."""
    return g["tx"] + etw(s, g["fs"])


def gend(g, lines, gap=30):
    return int(max(gx(g, l) for l in lines) + gap)


def ibox(order, g, col, i0, i1, color, right=None, anim="fade", extra=""):
    """A tinted box behind lines i0..i1 that starts at indent column col: one level of indentation."""
    x = g["tx"] + col * 0.6 * g["fs"] - 10
    y = gtop(g, i0) - 2
    r = right if right is not None else g["left"] + g["w"] - 14
    return f'<div{at(order, anim)}{extra} style="position:absolute;left:{x:.0f}px;top:{y:.0f}px;width:{r - x:.0f}px;height:{(i1 - i0 + 1) * g["lh"] + 4:.0f}px;background:{color}1A;border-left:6px solid {color};border-radius:8px"></div>'


def lband(order, g, i, n=1, kind="err", anim="fade"):
    """Tints editor lines i..i+n-1 (run, skip, err, mark)."""
    x = g["left"] + 2 + (70 if g["tx"] - g["left"] > 30 else 0)
    return f'<div{at(order, anim)} style="position:absolute;left:{x}px;top:{gtop(g, i):.1f}px;width:{g["left"] + g["w"] - 2 - x}px;height:{n * g["lh"]:.1f}px;background:{HL[kind]}"></div>'


TERM_BG = "#1D2330"


def tint(order, g, i, n, color, dark=False, anim="fade"):
    """A colored band with a bar on the left behind lines i..i+n-1 of an editor (or a terminal with dark=True)."""
    if dark:
        x, w, a = g["left"] + 8, g["w"] - 16, "55"
    else:
        x = g["left"] + 2 + (70 if g["tx"] - g["left"] > 30 else 0)
        w, a = g["left"] + g["w"] - 2 - x, "1F"
    return f'<div{at(order, anim)} style="position:absolute;left:{x}px;top:{gtop(g, i):.1f}px;width:{w}px;height:{n * g["lh"]:.1f}px;background:{color}{a};border-left:6px solid {color};border-radius:4px"></div>'


def tcolor(l):
    if re.match(r"[A-Za-z]+(Error|Exception)\b", l):
        return "#FF8A80"
    if l.startswith("Traceback") or l.startswith("  File"):
        return "#9AA3B2"
    if l.strip() and set(l.strip()) <= set("^~"):
        return "#FF8A80"
    return "#E6E9EF"


def term(tid, runs, left, top, w, fs=22, h=None, attrs="", inner=None, prompt=True):
    """A dark terminal. runs: [(command, output lines)]. Returns (html, geometry). inner: id of a wrapper for pan()."""
    lh = fs * 1.45
    rows = []
    for c, outl in runs:
        if prompt:
            rows.append(p(f"font-family:{MONO};font-size:{fs}px;line-height:1.45;white-space:pre;color:#FFFFFF", f'<span style="color:#7DD3A0">$ </span>{e(c)}'))
        rows += [p(f"font-family:{MONO};font-size:{fs}px;line-height:1.45;white-space:pre;color:{tcolor(l)}", e(l) if l else "&#160;") for l in outl]
    n = len(rows)
    hh = h or (44 + 28 + n * lh)
    wrap = f'<div id="{inner}" style="display:flex;flex-direction:column">' + "".join(rows) + '</div>' if inner else "".join(rows)
    o = [f'<div id="{tid}"{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{hh:.0f}px;background:{TERM_BG};border-radius:16px;overflow:hidden">',
         p(f"position:absolute;left:22px;top:0;height:44px;font-size:20px;font-weight:700;line-height:44px;color:#9AA3B2", "터미널"),
         f'<div style="position:absolute;left:0;top:44px;right:0;bottom:0;padding:14px 22px;background:{TERM_BG};overflow:hidden;display:flex;flex-direction:column">{wrap}</div></div>']
    g = {"left": left, "top": top, "w": w, "fs": fs, "lh": lh, "tx": left + 22, "y0": top + 44 + 14, "h": hh, "n": n}
    return "".join(o), g


def qnum(i, color, size=44):
    return num(i, color, size)


EB1 = "1. 왜 필요한가"
EB2 = "2. 들여쓰기는 상자"
EB3 = "3. for p, q in items()"
EB4 = "4. 모듈과 import"
EB5 = '5. if __name__ == "__main__"'
EB6 = "6. 실습"
CP, CPBG = "#2459C9", "#E5EEF8"     # product.py
CC, CCBG = "#1F8A4C", "#E4F3EA"     # cart.py
CM, CMBG = "#B26A00", "#F7EEDD"     # main.py
CU, CUBG = "#5A3BB8", "#ECE7F8"     # coupon.py
LV = ["#2459C9", "#1F8A4C", "#B26A00", "#A23B72"]   # indentation levels 1-4


# ---------- cover ----------
cover([("from product import Product", "#C7B8F2"), ("", W_), ("class Cart:", W_), ("    def show(self):", W_),
       ("        for p, q in self.items.items():", "#8FD8DE"), ("            print(p.name, q)", W_), ("", W_), ('if __name__ == "__main__":', "#F2C48D"), ("    cart.show()", W_)],
      "장바구니<br>미니 프로젝트", "들여쓰기, items(),<br>모듈과 import",
      "오늘 수업에서 만든 장바구니 프로젝트 코드로 세 가지를 다시 봐요. 줄마다 들여쓰기가 무슨 뜻인지, for p, q in self.items.items()에 무엇이 담기는지, 파일을 나누고 import하는 이유예요. 예제는 모두 수업 레포의 product.py와 cart.py에서 가져왔어요. 오른쪽 코드의 색칠한 세 줄이 오늘 풀 세 가지예요.", h1size=92)

# ---------- ready ----------
o = [sec("ready")] + head("들어가기", "수업에서 만든 shopping-cart 폴더에서 해요", CM)
o.append(f'<div{STAGGER(1)} style="position:absolute;left:0;top:0;width:1920px;height:1080px">')
for i, (a_, b_) in enumerate([("a, b, c = 튜플로 꺼내 담기", "13"), ("딕셔너리 items(), for k, v", "15"), ("if와 4칸 들여쓰기", "17"), ("def, return", "19"), ("class, __init__, 메서드, __str__", "24·25"), ("클래스 변수 Product.next_id", "26")]):
    o.append(f'<div style="position:absolute;left:96px;top:{220 + i * 110}px;width:780px;height:96px;display:flex;flex-direction:row;gap:24px;align-items:center;border-bottom:2px solid {LINE}">'
             + f'<x-icon name="CheckCircle" style="width:44px;height:44px;color:{GR}"></x-icon>'
             + p(f"flex:1;font-size:32px;font-weight:700;color:{INK}", e(a_))
             + p(f"font-size:28px;font-weight:700;color:{GRAY};white-space:nowrap", e(b_)) + '</div>')
o.append('</div>')
FX, FY, FWD = 1000, 220, 824
o.append(p(f"position:absolute;left:{FX}px;top:{FY}px;font-family:{MONO};font-size:30px;font-weight:700;color:{GRAY}", "shopping-cart/", at(2, "fade")))
FILES = [("product.py", "상품 틀 Product", CP), ("cart.py", "장바구니 틀 Cart", CC), ("main.py", "uv init이 만든 파일", CM), ("pyproject.toml", "uv 프로젝트 설정", GRAY)]
o.append(f'<div{STAGGER(2, 90)} style="position:absolute;left:0;top:0;width:1920px;height:1080px">')
for i, (f_, d_, c_) in enumerate(FILES):
    o.append(f'<div style="position:absolute;left:{FX}px;top:{FY + 64 + i * 92}px;width:{FWD}px;height:80px;display:flex;flex-direction:row;align-items:center;gap:22px;border-bottom:2px solid {LINE}">'
             + f'<div style="width:14px;height:44px;flex:none;border-radius:6px;background:{c_}"></div>'
             + p(f"width:300px;flex:none;font-family:{MONO};font-size:30px;font-weight:700;color:{INK}", e(f_))
             + p(f"font-size:28px;color:{SUB}", e(d_)) + '</div>')
o.append('</div>')
t_, g_ = term("rd-term", [("uv run cart.py", [])], FX, 720, FWD, fs=30, attrs=at(3))
o.append(t_)
o.append(p(f"position:absolute;left:{FX}px;top:{720 + g_['h'] + 20:.0f}px;width:{FWD}px;font-size:28px;color:{SUB}", "VS Code로 폴더를 열고 터미널에서 쳐요.", at(3, "fade")))
W("ready", o, "수업에서 만든 shopping-cart 폴더를 VS Code로 열어요. product.py에는 상품 틀 Product, cart.py에는 장바구니 틀 Cart가 있어요. main.py는 uv init이 처음 만들어 준 파일이에요. 파일을 실행할 때는 터미널에서 uv run 파일이름을 쳐요. 왼쪽 목록은 오늘 다시 꺼내 쓸 내용이고, 옆 숫자가 배운 챕터예요. 슬라이드의 코드는 수업 레포의 코드 그대로이고, 출력은 tools/demo.sh가 같은 파일을 uv로 실제로 실행한 결과예요.")

# ---------- part 1 ----------
o = [sec("w-why")] + head(EB1, "장바구니 코드에서 자주 막히는 세 곳이에요", K1)
WL = rng(CL, 1, 1) + [""] + rng(CL, 3, 6) + ["⋮"] + rng(CL, 9, 13) + ["⋮"] + rng(CL, 59, 59) + ["⋮"] + rng(CL, 66, 68)
WN = ["1", "2"] + [str(i) for i in range(3, 7)] + [""] + [str(i) for i in range(9, 14)] + [""] + ["59"] + [""] + ["66", "67", "68"]
ed, g = editor("ww-ed", "cart.py", WL, 96, T, 1110, fs=25, nums=WN, color=CC)
o.append(ed)
QX = 1260
QS = [(WL.index(rng(CL, 13, 13)[0]), "이 return은 어느 줄 소속일까요?", "2파트 들여쓰기", K2, rng(CL, 11, 13), 11, 13),
      (WL.index(rng(CL, 66, 66)[0]), "p와 q에는 무엇이 들어갈까요?", "3파트 items()", K3, rng(CL, 66, 66), 66, 66),
      (0, "이 줄은 왜 맨 위에 있을까요?", "4파트 import", K4, rng(CL, 1, 1), 1, 1)]
for k, (i, q, part, col, src_, a_, b_) in enumerate(QS):
    i0 = WL.index(src_[0])
    n = len(src_)
    o.append(box(k + 1, g["tx"] - 12, int(gtop(g, i0) - 4), int(max(etw(s, 25) for s in src_)) + 24, int(n * g["lh"] + 8), col))
    yq = gly(g, i0 + (n - 1) / 2)
    o.append(f'<div{at(k + 1, "fade")}{DIM("wq")} style="position:absolute;left:{QX}px;top:{yq - 60:.0f}px;width:564px;height:120px;display:flex;flex-direction:row;align-items:center;gap:20px">'
             + qnum(k + 1, col, 40) + '<div style="display:flex;flex-direction:column;gap:4px">' + p(f"font-size:30px;font-weight:700;line-height:1.35;color:{INK}", e(q)) + p(f"font-size:24px;font-weight:700;color:{col}", e(part)) + '</div></div>')
o.append(caption("파트마다 한 곳씩 풀어요.", 972, 4))
W("w-why", o, "오늘 만든 cart.py에서 질문이 가장 많이 나온 세 곳이에요. 첫째, add 안의 return이 if 안에 있는지 밖에 있는지는 들여쓰기만 보고 알아야 해요. 둘째, show 안의 for p, q in self.items.items()에서 p와 q에 무엇이 담기는지예요. 셋째, 맨 위의 from product import Product가 왜 필요한지예요. 세 가지는 주제가 달라 보여도 모두 이 프로젝트를 읽는 데 필요해요. 파트마다 하나씩 풀어요.", ("p1", "왜 필요한가"))

o = [sec("w-big")] + head(EB1, "세 가지는 모두 장바구니 프로젝트 안에 있어요", K1)
BY = 250
cards = [("product.py", CP, CPBG, ["class Product:", "    def __init__(...):", "    def is_sold_out(self):", "    def __str__(self):"], 96),
         ("cart.py", CC, CCBG, ["class Cart:", "    def add(...):", "        if ...:", "            return", "    def show(self):", "        for p, q in ..."], 716),
         ("main.py", CM, CMBG, ["from cart import Cart", "", "cart = Cart()", "cart.add(...)"], 1336)]
CWD = 488
o.append(f'<div{STAGGER(1, 120)} style="position:absolute;left:0;top:0;width:1920px;height:1080px">')
for name, col, bg, ls, x in cards:
    body = "".join(p(f"font-family:{MONO};font-size:22px;line-height:1.5;white-space:pre;color:{INK}", e(l) if l else "&#160;") for l in ls)
    o.append(f'<div id="wb-{name[:-3]}" style="position:absolute;left:{x}px;top:{BY}px;width:{CWD}px;height:310px;background:{CARD};border:3px solid {col};border-radius:22px;overflow:hidden">'
             + f'<div style="height:60px;background:{bg};border-bottom:2px solid {col};display:flex;align-items:center;padding:0 24px">' + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{col}", e(name)) + '</div>'
             + f'<div style="padding:18px 24px;display:flex;flex-direction:column">{body}</div></div>')
o.append('</div>')
# 2: indentation boxes on cart.py
cx0 = 716 + 3 + 24
for lv, (c0, i0, i1) in enumerate([(4, 1, 5), (8, 2, 3), (12, 3, 3)]):
    x = cx0 + c0 * 13.2 - 8
    o.append(f'<div{at(2, "fade")} style="position:absolute;left:{x:.0f}px;top:{BY + 60 + 18 + i0 * 33 - 2:.0f}px;width:{716 + CWD - 14 - x:.0f}px;height:{(i1 - i0 + 1) * 33 + 4}px;background:{LV[lv]}1A;border-left:5px solid {LV[lv]};border-radius:6px"></div>')
# 3: ring on for p, q
o.append(underline(3, cx0 + 8 * 13.2, cx0 + 24 * 13.2, BY + 60 + 18 + 6 * 33 + 2, K3, 5))
# 4: import arrows between files
AY = BY + 180
o.append(harrow(96 + CWD + 12, AY, 716 - 96 - CWD - 24, K4, WIPE(4)))
o.append(harrow(716 + CWD + 12, AY, 1336 - 716 - CWD - 24, K4, WIPE(4)))
o.append(p(f"position:absolute;left:{96 + CWD - 40}px;top:{AY - 66}px;width:220px;text-align:center;font-size:24px;font-weight:700;color:{K4}", "import", at(4, "fade") + DELAY(250)))
o.append(p(f"position:absolute;left:{716 + CWD - 40}px;top:{AY - 66}px;width:220px;text-align:center;font-size:24px;font-weight:700;color:{K4}", "import", at(4, "fade") + DELAY(250)))
LG = [("2파트 들여쓰기", "파일 안에서 줄이 어느 상자 소속인지", K2), ("3파트 items()", "장바구니 딕셔너리를 한 쌍씩 꺼내기", K3), ("4·5파트 import", "파일과 파일을 잇기, 테스트 코드 막기", K4)]
for i, (k, d, c) in enumerate(LG):
    o.append(f'<div{at(2 + i)}{DIM("lg")} style="position:absolute;left:96px;top:{640 + i * 100}px;width:1728px;height:100px;display:flex;flex-direction:row;align-items:center;gap:30px;border-bottom:2px solid {LINE}">'
             + p(f"width:340px;flex:none;font-size:32px;font-weight:700;color:{c}", e(k)) + p(f"font-size:32px;font-weight:700;color:{INK}", e(d)) + '</div>')
W("w-big", o, "세 가지가 프로젝트의 어디에 있는지 그림으로 먼저 봐요. 들여쓰기는 파일 하나 안에서 줄이 어느 상자 소속인지 정해요. items()는 cart.py 안의 장바구니 딕셔너리를 한 쌍씩 꺼낼 때 써요. import는 파일과 파일 사이를 이어서 product.py의 Product를 cart.py에서, cart.py의 Cart를 main.py에서 쓰게 해 줘요. 파트 순서도 이 그림처럼 파일 안에서 파일 밖으로 넓혀 가요.")


# ---------- part 2: indentation ----------
o = [sec("i-box")] + head(EB2, "4칸 들어간 줄은 바로 위 상자 안에 있어요", K2)
IB = rng(CL, 3, 13)
ed, g = editor("ib-ed", "cart.py", IB, 96, T, 1100, fs=32, start=3, color=CC)
o.append(ed)
BOXES = [(1, 4, 1, 10, "class Cart 안", 0), (2, 8, 2, 3, "__init__ 안", 1), (2, 8, 7, 10, "add 안", 1), (3, 12, 9, 10, "if 안", 2)]
for order, col, i0, i1, lab, lv in BOXES:
    o.append(ibox(order, g, col, i0, i1, LV[lv]))
    o.append(p(f"position:absolute;left:{96 + 1100 - 300}px;top:{gtop(g, i0) + 2:.0f}px;width:270px;text-align:right;font-size:26px;font-weight:700;line-height:{g['lh'] - 4:.0f}px;color:{LV[lv]}", e(lab), at(order, "fade") + DELAY(150)))
RX = 1250
RULES = [("콜론(:) 다음 줄은", "4칸 더 들어가요"), ("같은 칸에서 시작하는 줄은", "같은 상자예요"), ("왼쪽으로 나오면", "그 상자가 끝나요")]
o.append(f'<div{STAGGER(4, 120)} style="position:absolute;left:0;top:0;width:1920px;height:1080px">')
for i, (a_, b_) in enumerate(RULES):
    o.append(f'<div style="position:absolute;left:{RX}px;top:{T + i * 170}px;width:574px;height:150px;display:flex;flex-direction:row;align-items:center;gap:22px;border-bottom:2px solid {LINE}">'
             + num(i + 1, K2, 40) + '<div style="display:flex;flex-direction:column;gap:4px">' + p(f"font-size:28px;color:{SUB}", e(a_)) + p(f"font-size:32px;font-weight:700;color:{INK}", e(b_)) + '</div></div>')
o.append('</div>')
o.append(caption("파이썬은 중괄호 대신 칸 수로 상자를 나눠요.", 900, 4))
W("i-box", o, "들여쓰기는 상자 안의 상자예요. class Cart: 아래 4칸 들어간 줄은 모두 Cart 상자 안이에요. def add 아래 8칸 들어간 줄은 add 상자 안이고, if 아래 12칸 들어간 두 줄은 if 상자 안이에요. 규칙은 오른쪽 세 줄이 전부예요. 콜론으로 끝난 줄 다음은 4칸 더 들어가고, 같은 칸에서 시작하면 같은 상자예요. 왼쪽으로 나오면 그 상자가 끝나요. 17에서 if의 범위를 들여쓰기로 정한 것과 같은 규칙이 class와 def에도 그대로 쓰여요.", ("p2", "들여쓰기는 상자"))

o = [sec("i-show")] + head(EB2, "print(line) 한 줄의 칸 수만 다른데 출력이 달라요", K2)
SA = ded(rng(GL, 66, 70), 8)
SB = ded(rng(L(SHOW_IN), 66, 69), 8)
CW_ = 846
for k, (code, nm, sc, x, title_, col) in enumerate([(SA, "for 밖", "show-ok", 96, "for 밖에 둔 print(line)", GR), (SB, "for 안", "show-in", 96 + CW_ + 36, "for 안에 넣은 print(line)", RED)]):
    o.append(p(f"position:absolute;left:{x}px;top:{T - 6}px;font-size:28px;font-weight:700;color:{col}", e(title_)))
    ed, g = editor(f"is-ed{k}", "cart.py  show()", code, x, T + 44, CW_, fs=21, start=66, color=CC)
    o.append(ed)
    o.append(ibox(k + 1, g, 0, 1, 2 if k == 0 else 3, K2, anim="fade"))
    li = len(code) - 1
    o.append(box(k + 1, g["tx"] + etw(code[li][:len(code[li]) - len(code[li].lstrip())], 21) - 10, int(gtop(g, li) - 3), int(etw("print(line)", 21)) + 20, int(g["lh"] + 6), col))
    tt, tg = term(f"is-t{k}", [(cmd(sc), out(sc))], x, int(T + 44 + g["h"] + 24), CW_, fs=21)
    o.append(tt)
    if k == 1:
        for j in (4, 6):
            o.append(f'<div{at(3, "fade")} style="position:absolute;left:{x + 8}px;top:{gtop(tg, j + 1):.0f}px;width:{CW_ - 16}px;height:{tg["lh"]:.0f}px;background:{OR}55;border-radius:6px"></div>')
        o.append(tag(x + 22 + etw("-" * 40, 21) + 24, gly(tg, 6), "상품마다 한 줄씩", OR, 3, size=26))
W("i-show", o, "show()의 print(line)은 칸 수에 따라 for 상자 안에도, 밖에도 들어갈 수 있어요. 왼쪽은 수업 코드처럼 for와 같은 칸에 둬서 for가 다 끝난 뒤 한 번만 실행돼요. 오른쪽은 4칸 더 넣어서 for 상자 안으로 들어갔어요. 그래서 상품을 한 줄 찍을 때마다 줄도 한 번씩 찍혀요. 오류는 나지 않으니 출력을 보고서야 알아채요. 슬라이드에서는 show() 안쪽만 보이게 앞의 8칸을 덜어 냈어요. 테스트 코드는 if __name__ 안으로 옮긴 판이라, 5파트에서 왜 그렇게 했는지 봐요." + REAL)

o = [sec("i-return")] + head(EB2, "return이 if 밖으로 나오면 아무것도 담기지 않아요", K2)
RL = ded(rng(L(RET_OUT), 9, 24), 4)
ed, g = editor("ir-ed", "cart.py  add()", RL, 96, T, 1060, fs=24, start=9, color=CC)
o.append(ed)
RW_ = g["w"] - 74 - 4
o.append(run(1, g["left"] + 72, gtop(g, 2), RW_, g["lh"]))
o.append(lband(1, g, 3, 1, "skip"))
o.append(tag(gend(g, [RL[2]]), gly(g, 2), "텀블러는 품절이 아니라 False", GR, 1, size=26))
o.append(run(2, g["left"] + 72, gtop(g, 4), RW_, g["lh"]))
o.append(lband(2, g, 4, 1, "err"))
o.append(tag(gend(g, [RL[4]]), gly(g, 4), "if 밖이라 언제나 실행돼요", RED, 2, size=26))
o.append(run_off(3))
o.append(lband(3, g, 6, 10, "skip"))
o.append(tag(gend(g, [RL[6]], 30), gly(g, 6), "여기까지 못 와요", GRAY, 3, size=26))
tt, tg = term("ir-t", [(cmd("ret-out"), out("ret-out"))], 1196, T, 628, fs=20, attrs=at(3))
o.append(tt)
o.append(fixv(1196, 620, 628, "····return", "········return", 4, size=28, label="if 안으로 4칸 더 (· 하나가 빈칸 하나)"))
W("i-return", o, "add()의 return을 한 칸 단계 밖으로 꺼낸 코드예요. 이제 return은 if 상자 밖, add 상자 바로 안에 있어요. 텀블러는 품절이 아니라서 if 안의 print는 건너뛰어요. 그런데 return은 if와 상관없이 언제나 실행돼서 add()가 바로 끝나요. 그 아래 담는 코드까지 가지 못하니 장바구니가 비어 있다고 나와요. return을 if 안으로 4칸 넣으면, 품절일 때만 멈춰요. 19에서 return을 만나면 함수가 바로 끝난다고 배웠던 그 규칙이에요." + REAL)

o = [sec("i-oneline")] + head(EB2, "콜론 뒤를 한 줄에 붙인 if도 같은 상자예요", K2)
QS1 = f"font-family:{MONO};font-size:44px;font-weight:700;line-height:1.45;white-space:pre;color:{INK}"
o.append(p(f"position:absolute;left:96px;top:{T}px;font-size:28px;font-weight:700;color:{SUB}", "cart.py 51번 줄"))
o.append(p(f"position:absolute;left:96px;top:{T + 60}px;{QS1}", tok("i", "if self.is_empty():") + " " + tok("r", "return 0"), ' id="io-a"' + at(0, "fade") + MORPH_FROM()))
o.append(p(f"position:absolute;left:96px;top:{T + 60}px;{QS1}", tok("i", "if self.is_empty():") + "\n    " + tok("r", "return 0", f"color:{K2}"), MORPH(1, "io-a")))
o.append(tag(980, T + 60 + 32, "콜론 뒤 한 줄을 붙여 썼을 뿐이에요", K2, 1))
o.append(tag(980, T + 60 + 96, "두 줄로 풀면 4칸 들어간 if 상자예요", K2, 1, ex=DELAY(200)))
YB = T + 240
o.append(p(f"position:absolute;left:96px;top:{YB}px;font-size:28px;font-weight:700;color:{SUB}", "cart.py 52번 줄", at(2, "fade")))
o.append(p(f"position:absolute;left:96px;top:{YB + 60}px;{QS1}", "return " + f'<span{MARK(2)} style="color:{GR}">0</span>' + " if self.subtotal() >= 30_000 else " + f'<span{MARK(2)} style="color:{OR}">3_000</span>', at(2, "fade")))
o.append(tag(96, YB + 170, "이건 17의 한 줄 if else예요. 둘 중 값 하나를 골라 돌려줘요", INK, 2, lead=False, size=30))
o += table(96, YB + 240, 1100, [["15,000원", "3,000원"], ["193,000원", "0원"]], [500, 500], mono=(0, 1), order0=3, rh=70, head_=["상품 합계 (uv run cart.py)", "배송비"], fs=32, colors=[INK, None])
o.append(caption("수업 예제는 두 줄로 적어요. 붙여 쓴 코드를 만나면 두 줄로 풀어 읽어요.", 960, 4))
W("i-oneline", o, "cart.py 51번 줄의 if self.is_empty(): return 0은 두 줄 if를 한 줄에 붙인 모양이에요. 콜론 뒤에 실행할 줄이 하나뿐이면 이렇게 붙여 쓸 수 있어요. 두 줄로 풀면 return 0이 if 상자 안에 4칸 들어간 모양이에요. 52번 줄은 다르게 생겼어요. 17에서 배운 한 줄 if else라서, 조건에 따라 0과 3_000 중 하나를 골라 돌려줘요. 아래 표는 1파트의 uv run cart.py 출력에서 가져온 배송비예요. 상품 합계가 3만 원보다 적으면 3,000원, 많으면 0원이에요.")

o = [sec("i-error")] + head(EB2, "칸이 안 맞으면 IndentationError가 나요", K2)
for k, (sc, lnum, why, fixs, col) in enumerate([("err-noindent", "43", "42번 줄 def 다음 줄이 안으로 안 들어갔어요", "43번 줄 앞에 4칸 더 넣어요", RED),
                                              ("err-unindent", "39", "39번 줄만 10칸이라 맞는 상자가 없어요", "위 줄과 같은 12칸으로 맞춰요", RED)]):
    y0 = T + k * 360
    tt, tg = term(f"ie-t{k}", [(cmd(sc), out(sc))], 96, y0, 1160, fs=22, attrs=at(1 + 2 * k) if k else "")
    o.append(tt)
    last = out(sc)[-1]
    o.append(underline(1 + 2 * k, tg["tx"], tg["tx"] + etw(last.split(":")[0], 22), gly(tg, len(out(sc))) + 16, RED))
    lx = tg["tx"] + etw(out(sc)[0][:out(sc)[0].index("line")], 22)
    o.append(box(2 + 2 * k, int(lx) - 6, int(gtop(tg, 1)) - 2, int(etw("line " + lnum, 22)) + 12, int(tg["lh"]) + 4, OR))
    o.append(f'<div{at(2 + 2 * k)} style="position:absolute;left:1296px;top:{y0 + 20}px;width:528px;display:flex;flex-direction:column;gap:16px">'
             + p(f"font-size:28px;font-weight:700;line-height:1.4;color:{INK}", e(why))
             + p(f"font-size:28px;font-weight:700;line-height:1.4;color:{GR};background:#E6F4EC;border-radius:12px;padding:10px 18px", e(fixs)) + '</div>')
o.append(caption("오류 줄에 적힌 줄 번호부터 가서 위 줄과 칸을 비교해요.", 950, 4))
W("i-error", o, "칸이 맞지 않으면 파이썬은 실행하기 전에 IndentationError를 내요. 위는 def is_empty 다음 줄을 안으로 넣지 않았을 때예요. 콜론 다음에는 안으로 들어간 줄이 있어야 한다고 알려 줘요. 아래는 12칸이어야 할 줄을 10칸으로 적었을 때예요. 10칸에서 시작하는 상자가 없어서 어디에 붙일지 모른다는 뜻이에요. 두 오류 모두 메시지에 줄 번호가 있으니 그 줄로 가서 위 줄과 칸을 비교해요." + REAL)

o = [sec("i-keys")] + head(EB2, "VS Code에서는 Tab과 Shift+Tab으로 칸을 맞춰요", K2)
KL = rng(CL, 9, 13)
KA = KL[:3] + [l[4:] for l in KL[3:]]


def guides(g, lines):
    o = []
    for col in (4, 8, 12):
        idx = [i for i, l in enumerate(lines) if len(l) - len(l.lstrip()) > col]
        if idx:
            x = g["tx"] + col * 0.6 * g["fs"] - 2
            o.append(f'<div style="position:absolute;left:{x:.0f}px;top:{gtop(g, idx[0]):.0f}px;width:2px;height:{(idx[-1] - idx[0] + 1) * g["lh"]:.0f}px;background:#D3D7DE"></div>')
    return o


ed, g = editor("ik-ed", "cart.py", KL, 1010, T, 814, fs=26, start=9, color=CC)
o.append(ed)
o += guides(g, KL)
o.append(f'<div{at(1, "fade")} style="position:absolute;left:{g["left"] + 72}px;top:{gtop(g, 3):.0f}px;width:{g["w"] - 74}px;height:{2 * g["lh"]:.0f}px;background:#2F7DE133"></div>')
o.append(tag(1010, int(g["top"] + g["h"] + 34), "12, 13번 줄을 고르고 Shift+Tab 한 번", BL, 3, lead=False, size=26))
ed2, g2 = editor("ik-ed2", "cart.py", KA, 1010, int(g["top"] + g["h"] + 76), 814, fs=26, start=9, color=CC, attrs=at(3))
o.append(ed2)
o += [x.replace('<div style', f'<div{at(3)} style', 1) for x in guides(g2, KA)]
o.append(lband(3, g2, 3, 2, "err"))
o.append(tag(1010, int(g2["top"] + g2["h"] + 34), "두 줄이 if 상자 밖으로 나왔어요", RED, 3, lead=False, size=26))
KR = [("Tab", "고른 줄을 4칸 안으로"), ("Shift+Tab", "고른 줄을 4칸 밖으로")]
for i, (k_, d_) in enumerate(KR):
    y = T + i * 190
    o.append(keys(2 + i, 96, y + 10, k_, 34))
    o.append(p(f"position:absolute;left:96px;top:{y + 100}px;font-size:32px;font-weight:700;color:{INK}", e(d_), at(2 + i, "fade") + DELAY(250)))
o.append(p(f"position:absolute;left:96px;top:{T + 400}px;font-family:{MONO};font-size:28px;font-weight:700;color:{INK};background:#E3E6EB;border:2px solid #C9CED8;border-radius:8px;padding:6px 16px", "Spaces: 4", at(4)))
o.append(p(f"position:absolute;left:96px;top:{T + 470}px;width:860px;font-size:28px;line-height:1.45;color:{INK}", "VS Code 맨 아래 막대 오른쪽에 보여요. Tab 한 번이 빈칸 4개예요.", at(4, "fade") + DELAY(200)))
o.append(caption("스페이스를 하나씩 세지 말고 Tab과 Shift+Tab을 써요.", 960, 5))
W("i-keys", o, "VS Code에서는 칸을 직접 세지 않아도 돼요. 줄을 고르고 Tab을 누르면 4칸 안으로, Shift+Tab을 누르면 4칸 밖으로 움직여요. 오른쪽처럼 12, 13번 줄을 골라 Shift+Tab을 한 번 누르면 두 줄이 한꺼번에 if 상자 밖으로 나와요. 앞에서 본 return 실수가 이렇게 생기니, 누른 뒤에는 상자를 다시 확인해요. 맥과 윈도우 모두 같은 키예요. 코드 왼쪽의 세로 안내선은 상자의 경계라서 칸을 비교할 때 도움이 돼요. 화면 맨 아래 막대 오른쪽에 Spaces: 4가 보이면 Tab 한 번이 빈칸 네 개로 들어가요. 다른 숫자가 보이면 눌러서 4로 바꿔요.")


# ---------- part 3: items() ----------
def code_lines(scene, f):
    return L(SCENES[scene]["files"][f])


def slot(sid, label, value, x, y, w, color, attrs="", vattrs="", fs=34, h=84):
    """A named box with a value inside, like the value boxes of chapter 12."""
    return (p(f"position:absolute;left:{x}px;top:{y - 44}px;font-family:{MONO};font-size:28px;font-weight:700;color:{color}", e(label), attrs)
            + f'<div{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{CARD};border:3px solid {color};border-radius:16px"></div>'
            + p(f"position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:{h}px;text-align:center;color:{INK};white-space:nowrap", e(value), f' id="{sid}"' + vattrs))


o = [sec("u-tuple")] + head(EB3, "a, b = (1, 2)는 두 값을 두 칸에 나눠 담아요", K3)
UT = code_lines("tuple", "play.py")
ed, g = editor("ut-ed", "play.py", UT, 96, T, 880, fs=30, color=GRAY)
o.append(ed)
tt, tg = term("ut-t", [(cmd("tuple"), out("tuple"))], 96, int(T + g["h"] + 28), 880, fs=28)
o.append(tt)
PX = 1080


def tuple_row(y, vals, pre, order, names, col):
    """( v1 , v2 ) drawn big, then two boxes below that the values fly into."""
    parts, x = [], PX
    pieces = ["("] + sum([[v, ","] for v in vals], [])[:-1] + [")"]
    for piece in pieces:
        w = etw(piece, 44) + 8
        sid = f' id="{pre}{vals.index(piece)}"' if piece in vals else ""
        parts.append(p(f"position:absolute;left:{x:.0f}px;top:{y}px;font-family:{MONO};font-size:44px;font-weight:700;line-height:60px;color:{SUB if piece in '(,)' else INK};white-space:pre", e(piece), sid))
        x += w + (6 if piece != "(" else 0)
    for k, (nm, v) in enumerate(zip(names, vals)):
        bx = PX + k * 370
        parts.append(slot(f"{pre}s{k}", nm, v, bx, y + 150, 320, col, vattrs=f' data-build-in="fly order {order}" data-from="{pre}{k}"'))
    return parts


o += tuple_row(T + 10, ["1", "2"], "ta", 1, ["a", "b"], K3)
o += tuple_row(T + 340, ['"텀블러"', "1"], "tb", 2, ["name", "qty"], K3)
o.append(caption("13에서 배운 꺼내 담기예요. 왼쪽 이름 수와 오른쪽 값 수가 같아야 해요.", 950, 3))
W("u-tuple", o, "for p, q를 이해하려면 이 한 줄부터 봐요. a, b = (1, 2)는 오른쪽 튜플의 첫 값을 a에, 두 번째 값을 b에 담아요. 13에서 a, b, c = 튜플로 꺼내 담기를 배웠어요. 오른쪽 그림처럼 값이 순서대로 칸에 들어가요. 두 번째 줄은 장바구니에 어울리게 상품 이름과 수량을 담았어요. 왼쪽 이름 수와 오른쪽 값 수가 같아야 한다는 것만 기억하면 돼요. play.py는 연습용으로 만든 새 파일이에요." + REAL, ("p3", "for p, q in items()"))

o = [sec("u-pairs")] + head(EB3, "items()는 키와 값을 튜플 한 쌍씩 묶어 줘요", K3)
UP = code_lines("pairs", "play.py")
ed, g = editor("up-ed", "play.py", UP, 96, T, 1000, fs=28, color=GRAY)
o.append(ed)
tt, tg = term("up-t", [(cmd("pairs"), out("pairs"))], 96, int(T + g["h"] + 28), 1000, fs=24)
o.append(tt)
lo = out("pairs")[1]
o.append(box(3, int(tg["tx"] + etw("[", 24)) - 6, int(gtop(tg, 2)) - 2, int(etw("('텀블러', 1)", 24)) + 12, int(tg["lh"]) + 4, K3))
DX = 1200
o += table(DX, T, 624, [['"텀블러"', "1"], ['"무선 이어폰"', "2"]], [330, 200], mono=(0, 1), rh=80, head_=["키", "값"], fs=32)
o.append(p(f"position:absolute;left:{DX}px;top:{T + 250}px;font-family:{MONO};font-size:34px;font-weight:700;color:{K3}", ".items()", at(1, "fade")))
o.append(f'<x-shape{at(1)} kind="arrow-right" style="position:absolute;left:{DX + 200}px;top:{T + 256}px;width:120px;height:30px;transform:rotate(90deg);background:{K3}"></x-shape>')
o.append(f'<div{STAGGER(2, 160)} style="position:absolute;left:0;top:0;width:1920px;height:1080px">')
for i, pr in enumerate(["('텀블러', 1)", "('무선 이어폰', 2)"]):
    o.append(p(f"position:absolute;left:{DX}px;top:{T + 360 + i * 110}px;font-family:{MONO};font-size:34px;font-weight:700;line-height:1.3;color:{INK};background:{K3BG};border:3px solid {K3};border-radius:16px;padding:10px 22px;white-space:pre", e(pr), f' id="up-p{i}"'))
o.append('</div>')
o.append(caption("한 쌍이 튜플이니, 앞 장의 a, b = 튜플처럼 두 칸에 나눠 담을 수 있어요.", 950, 4))
W("u-pairs", o, "딕셔너리의 items()는 키와 값을 튜플 한 쌍으로 묶어서 줘요. 15에서 본 dict_items 모양이에요. list()로 바꿔 보면 괄호로 묶인 쌍이 두 개 들어 있어요. ('텀블러', 1) 하나가 앞 장의 (1, 2)와 같은 튜플이에요. 그러니 이 한 쌍도 이름 두 개에 나눠 담을 수 있어요. 다음 장에서 for가 이 쌍을 하나씩 꺼내요." + REAL)

o = [sec("u-for")] + head(EB3, "for가 한 쌍씩 꺼내서 name과 qty에 나눠 담아요", K3)
UF = code_lines("for", "play.py")
ed, g = editor("uf-ed", "play.py", UF, 96, T, 1000, fs=32, color=GRAY)
o.append(ed)
FO = out("for")
TY = int(T + g["h"] + 40)
tt, tg = term("uf-t", [(cmd("for"), [])], 96, TY, 1000, fs=30, h=44 + 28 + 3 * 30 * 1.45 + 10)
o.append(tt)
for j, l in enumerate(FO):
    o.append(p(f"position:absolute;left:{tg['tx']}px;top:{gtop(tg, j + 1):.0f}px;font-family:{MONO};font-size:30px;line-height:1.45;white-space:pre;color:#E6E9EF", e(l), at(2 + 2 * j, "fade")))
RW2 = g["w"] - 74 - 4
for j in range(2):
    o.append(run(1 + 2 * j, g["left"] + 72, gtop(g, 2), RW2, g["lh"]))
    o.append(run(2 + 2 * j, g["left"] + 72, gtop(g, 3), RW2, g["lh"]))
o.append(run_off(5))
PX2 = 1200
for i, pr in enumerate(["('텀블러', 1)", "('무선 이어폰', 2)"]):
    o.append(p(f"position:absolute;left:{PX2}px;top:{T + i * 100}px;font-family:{MONO};font-size:32px;font-weight:700;line-height:1.3;color:{INK};background:{K3BG};border:3px solid {K3};border-radius:16px;padding:10px 22px;white-space:pre", e(pr), f' id="uf-p{i}"'))
o.append(pulse(1, "uf-p0"))
o.append(pulse(3, "uf-p1"))
o.append(slot("uf-n", "name", '"무선 이어폰"', PX2, T + 330, 520, K3, vattrs=' data-start=" "'))
o.append(slot("uf-q", "qty", "2", PX2, T + 520, 520, K3, vattrs=' data-start=" "'))
o.append(text(1, "uf-n", '"텀블러"'))
o.append(text(1, "uf-q", "1"))
o.append(text(3, "uf-n", '"무선 이어폰"'))
o.append(text(3, "uf-q", "2"))
o.append(tag(PX2, T + 700, "쌍이 두 개라 두 번 돌아요", INK, 5, lead=False, size=30))
W("u-for", o, "for name, qty in cart_items.items():는 앞 장의 쌍을 하나씩 꺼내서, 꺼낸 쌍을 name과 qty 두 칸에 나눠 담아요. 첫 바퀴에는 ('텀블러', 1)이 와서 name은 텀블러, qty는 1이 돼요. print가 한 줄을 찍고, 두 번째 바퀴에는 ('무선 이어폰', 2)가 와요. 쌍이 두 개라 두 번 돌고 끝나요. 매 바퀴마다 a, b = 튜플을 한 번씩 하는 것과 같아요." + REAL)

o = [sec("u-long")] + head(EB3, "for 옆에 이름 두 개는 pair[0], pair[1]을 줄인 모양이에요", K3)
QL = f"font-family:{MONO};font-size:38px;font-weight:700;line-height:1.5;white-space:pre;color:{INK}"
LX, LY = 96, T + 40
o.append(p(f"position:absolute;left:{LX}px;top:{LY - 50}px;font-size:28px;font-weight:700;color:{SUB}", "긴 방법"))
o.append(p(f"position:absolute;left:{LX}px;top:{LY}px;{QL}",
           tok("f", "for ") + tok("pair", "pair") + tok("in", " in cart_items.items():") + "\n" + tok("n", "    name = ", "") + f'<span{MARK(1)} style="color:{BL}">pair[0]</span>' + "\n" + tok("q", "    qty = ") + f'<span{MARK(1)} style="color:{OR}">pair[1]</span>' + "\n" + tok("pr", "    print(name, qty)"),
           ' id="ul-a"' + MORPH_FROM()))
o.append(p(f"position:absolute;left:{LX}px;top:{LY}px;{QL}",
           tok("f", "for ") + tok("nq", f'<span style="color:{BL}">name</span>, <span style="color:{OR}">qty</span>') + tok("in", " in cart_items.items():") + "\n" + tok("pr", "    print(name, qty)"),
           MORPH(2, "ul-a")))
o.append(tag(LX, LY + 360, "한 쌍을 pair 하나로 받고, 번호로 꺼내요", SUB, 1, lead=False, size=30))
o.append(tag(LX, LY + 420, "for에서 바로 두 칸에 나눠 담아요. 수업 코드는 이 모양이에요", K3, 2, lead=False, size=30))
RX3 = 1250
for k, (sc, nm, order) in enumerate([("long", "긴 방법", None), ("for", "짧은 방법", 2)]):
    y = T + k * 330
    o.append(p(f"position:absolute;left:{RX3}px;top:{y}px;font-size:26px;font-weight:700;color:{SUB}", e(nm), at(order, "fade") if order else ""))
    tt, tg = term(f"ul-t{k}", [(cmd(sc), out(sc))], RX3, y + 46, 574, fs=26, attrs=at(order) if order else "")
    o.append(tt)
o.append(caption("출력이 똑같아요. pair[0]이 name, pair[1]이 qty예요.", 950, 3))
W("u-long", o, "for 옆에 이름을 두 개 적는 건 긴 방법을 줄인 모양이에요. 긴 방법은 한 쌍을 pair라는 이름 하나로 받고, pair[0]과 pair[1]로 하나씩 꺼내요. 짧은 방법은 for에서 바로 두 칸에 나눠 담아요. 오른쪽 출력처럼 결과는 똑같아요. 수업 코드의 for p, q in self.items.items()도 이 짧은 방법이에요. 13에서 튜플을 번호 두 개로 꺼냈던 것과 a, b = 튜플로 꺼내 담았던 것을 떠올려요." + REAL)

o = [sec("u-two")] + head(EB3, "cart.items는 칸 이름, .items()는 딕셔너리 메서드예요", K3)
U2 = code_lines("twoitems", "play.py")
ed, g = editor("u2-ed", "play.py", U2, 96, T, 1000, fs=26, color=GRAY)
o.append(ed)
fi = U2.index("for p, q in cart.items.items():")
o.append(over(0, 0, 0, "", "", INK, 0) if False else "")
o.append(p(f"position:absolute;left:{gx(g, 'for p, q in '):.1f}px;top:{gtop(g, fi):.1f}px;font-family:{MONO};font-size:26px;line-height:{g['lh']:.2f}px;white-space:pre;color:{K1};background:{K1BG}", "cart.items", MARK(1)))
o.append(p(f"position:absolute;left:{gx(g, 'for p, q in cart.items'):.1f}px;top:{gtop(g, fi):.1f}px;font-family:{MONO};font-size:26px;line-height:{g['lh']:.2f}px;white-space:pre;color:{GR};background:#E6F4EC", ".items()", MARK(2)))
tt, tg = term("u2-t", [(cmd("twoitems"), out("twoitems"))], 96, int(T + g["h"] + 22), 1000, fs=22)
o.append(tt)
CX, CY2 = 1160, T
o.append(f'<div id="u2-cart" style="position:absolute;left:{CX}px;top:{CY2}px;width:664px;height:470px;background:{CARD};border:3px solid {CC};border-radius:26px;overflow:hidden">'
         + f'<div style="height:66px;background:{CC};display:flex;align-items:center;padding:0 24px">' + p("font-family:" + MONO + ";font-size:32px;font-weight:700;color:#FFFFFF", "cart") + '<div style="flex:1"></div>' + p("font-size:22px;font-weight:700;color:#FFFFFF", "Cart") + '</div></div>')
o.append(p(f"position:absolute;left:{CX + 30}px;top:{CY2 + 96}px;font-family:{MONO};font-size:28px;font-weight:700;color:{K1}", "items", at(1, "fade")))
o.append(f'<div{at(1)} style="position:absolute;left:{CX + 30}px;top:{CY2 + 146}px;width:604px;height:290px;background:{K1BG};border:3px solid {K1};border-radius:18px"></div>')
for i, (nm, pr, q) in enumerate([("텀블러", "15000", "1"), ("무선 이어폰", "89000", "2")]):
    y = CY2 + 170 + i * 128
    o.append(f'<div{at(1)} id="u2-k{i}" style="position:absolute;left:{CX + 54}px;top:{y}px;width:380px;height:106px;background:{CARD};border:3px solid {CP};border-radius:14px;display:flex;flex-direction:column;justify-content:center;padding:0 18px">'
             + p(f"font-size:22px;font-weight:700;color:{CP}", "Product") + p(f"font-size:28px;font-weight:700;color:{INK}", e(f"{nm}  {int(pr):,}원")) + '</div>')
    o.append(p(f"position:absolute;left:{CX + 450}px;top:{y + 26}px;font-family:{MONO};font-size:40px;font-weight:700;color:{INK}", ": " + q, at(1)))
o.append(tag(CX, CY2 + 510, "cart.items: Cart 안의 딕셔너리 칸", K1, 1, lead=False, size=28))
o.append(tag(CX, CY2 + 560, ".items(): 딕셔너리를 한 쌍씩 꺼내는 메서드", GR, 2, lead=False, size=28))
o.append(tag(CX, CY2 + 640, "키가 Product 객체라서 p.name, p.price를 써요", CP, 3, lead=False, size=28, w=664))
o.append(pulse(3, "u2-k0"))
W("u-two", o, "수업 코드에서 items가 두 번 나와서 헷갈렸을 거예요. 앞의 cart.items는 Cart의 __init__에서 self.items = {}로 만든 칸 이름이에요. 장바구니 딕셔너리가 이 칸에 들어 있어요. 뒤의 .items()는 그 딕셔너리의 메서드예요. 칸 이름을 basket처럼 지었다면 cart.basket.items()가 됐을 거예요. 또 하나, 이 딕셔너리의 키는 글자가 아니라 Product 객체예요. 그래서 p에는 상품 객체가 담기고 p.name, p.price로 꺼내요. q에는 수량이 담겨요." + REAL)

o = [sec("u-sum")] + head(EB3, "합계는 for로 쌓아도, sum에 넘겨도 같아요", K3)
US = code_lines("subtotal", "play.py")
ed, g = editor("us-ed", "play.py", US, 96, T, 1060, fs=23, color=GRAY)
o.append(ed)
tt, tg = term("us-t", [(cmd("subtotal"), out("subtotal"))], 1196, T, 628, fs=26)
o.append(tt)
for k, (ci, oj, col) in enumerate([(US.index("print(total)"), 2, BL), (US.index("print(sum([p.price * q for p, q in cart.items.items()]))"), 3, OR), (US.index("print(cart.subtotal())"), 4, GR)]):
    o.append(tint(1 + k, g, ci if k else ci - 3, 1 if k else 4, col))
    o.append(tint(1 + k, tg, oj + 1, 1, col, dark=True))
RB = [("for로 하나씩 더하기", "18", BL), ("컴프리헨션 리스트를 sum에", "23", OR), ("Cart의 subtotal() 메서드", "cart.py", GR)]
for i, (a_, b_, c_) in enumerate(RB):
    o.append(f'<div{at(1 + i)}{DIM("us")} style="position:absolute;left:1196px;top:{T + tg["h"] + 40 + i * 76:.0f}px;width:628px;height:76px;display:flex;flex-direction:row;align-items:center;gap:16px;border-bottom:2px solid {LINE}">'
             + f'<div style="width:12px;height:40px;flex:none;border-radius:6px;background:{c_}"></div>' + p(f"flex:1;font-size:26px;font-weight:700;color:{INK}", e(a_)) + p(f"font-size:24px;font-weight:700;color:{GRAY}", e(b_)) + '</div>')
SL = [rng(CL, 47, 47)[0]]
ed2, g2 = editor("us-ed2", "cart.py", SL, 96, 870, 1728, fs=26, start=47, color=CC, attrs=at(4))
o.append(ed2)
o.append(tag(gend(g2, SL, 20), gly(g2, 0), "[ ] 없는 모양은 제너레이터, 결과는 같아요", K3, 4, size=26))
W("u-sum", o, "장바구니 합계를 세 가지로 구해 봤어요. 첫째는 18에서 배운 대로 total = 0에서 시작해 for로 하나씩 더해요. 둘째는 23의 컴프리헨션으로 금액 리스트를 만들어 sum에 넘겨요. 셋째는 수업 코드의 subtotal() 메서드예요. 셋 다 193000이에요. 아래 cart.py 47번 줄은 sum 안에 대괄호가 없어요. 23에서 이름만 본 제너레이터라는 모양이고, 리스트를 만들지 않을 뿐 결과는 같아요. 수업 예제에서는 대괄호를 넣은 둘째 모양으로 읽어도 돼요." + REAL)

o = [sec("u-error")] + head(EB3, ".items()를 빠뜨리면 키만 나와서 둘로 못 나눠요", K3)
for k, (sc, why, fixs, y0) in enumerate([("err-noitems", "cart.items를 돌면 키인 Product 하나씩 나와요. 하나를 둘로 못 나눠요", "for p, q in cart.items.items():", T),
                                         ("err-str", "키 \"텀블러\"는 글자 셋으로 쪼개져서 두 칸에 안 맞아요", "for name, qty in cart_items.items():", T + 380)]):
    tt, tg = term(f"ue-t{k}", [(cmd(sc), out(sc))], 96, y0, 1060, fs=22, attrs=at(1 + 2 * k) if k else "")
    o.append(tt)
    last = out(sc)[-1]
    o.append(underline(1 + 2 * k, tg["tx"], tg["tx"] + etw(last, 22), gly(tg, len(out(sc))) + 16, RED))
    o.append(f'<div{at(2 + 2 * k)} style="position:absolute;left:1196px;top:{y0 + 20}px;width:628px;display:flex;flex-direction:column;gap:16px">'
             + p(f"font-size:28px;font-weight:700;line-height:1.4;color:{INK}", e(why))
             + p(f"font-family:{MONO};font-size:24px;font-weight:700;line-height:1.4;color:{INK};background:#E6F4EC;border:3px solid {GR};border-radius:12px;padding:10px 18px;white-space:pre", e(fixs)) + '</div>')
o.append(caption("딕셔너리를 for로 돌면 키만 나와요. 키와 값이 같이 필요하면 .items()를 붙여요.", 950, 4))
W("u-error", o, "items()를 빠뜨렸을 때 나는 오류 두 가지예요. 딕셔너리를 그냥 for로 돌면 키만 하나씩 나와요. 위는 키가 Product 객체라서 하나를 p와 q 둘로 나눌 수 없다는 TypeError예요. 아래는 키가 글자라서 \"텀블러\"가 글자 세 개로 쪼개졌어요. 칸은 두 개인데 값이 세 개라 ValueError가 나요. 키가 두 글자였다면 오류 없이 엉뚱한 값이 담겼을 거예요. 키와 값이 같이 필요하면 꼭 .items()를 붙여요." + REAL)


# ---------- part 4: modules ----------
def fchip(fid, name, x, y, w, col, bg, attrs="", sub=None, h=96):
    s = p(f"font-size:24px;color:{SUB}", e(sub)) if sub else ""
    return (f'<div id="{fid}"{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{bg};border:3px solid {col};border-radius:18px;display:flex;flex-direction:column;justify-content:center;padding:0 24px;gap:2px">'
            + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{col}", e(name)) + s + '</div>')


def modbox(mid, name, x, y, w, h, col, bg, attrs="", nid=None):
    """A module drawn as a dashed box with its name on a tab."""
    nattr = f' id="{nid}"' if nid else ""
    return (f'<div id="{mid}"{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{bg};border:4px dashed {col};border-radius:24px"></div>'
            + p(f"position:absolute;left:{x + 24}px;top:{y - 22}px;font-family:{MONO};font-size:28px;font-weight:700;color:#FFFFFF;background:{col};border-radius:10px;padding:2px 16px", e(name), nattr + attrs))


o = [sec("m-why")] + head(EB4, "파일을 나누면 찾기, 같이 쓰기, 나눠 일하기가 쉬워요", K4)
BX0, BY0, BW0, BH0 = 96, 230, 520, 340
o.append(f'<div style="position:absolute;left:{BX0}px;top:{BY0}px;width:{BW0}px;height:{BH0}px;background:{CARD};border:3px solid {GRAY};border-radius:22px;overflow:hidden">'
         + f'<div style="height:58px;background:#EEF0F3;border-bottom:2px solid {LINE};display:flex;align-items:center;padding:0 22px">' + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{INK}", "shop.py") + '<div style="flex:1"></div>' + p(f"font-size:22px;font-weight:700;color:{GRAY}", "한 파일 139줄") + '</div>'
         + '<div style="padding:14px 18px;display:flex;flex-direction:column;gap:8px">'
         + "".join(f'<div style="height:{h}px;border-radius:10px;background:{bg};border-left:6px solid {c};display:flex;align-items:center;padding-left:16px">' + p(f"font-family:{MONO};font-size:22px;font-weight:700;color:{c}", e(t)) + '</div>'
                   for t, c, bg, h in [("class Product", CP, CPBG, 56), ("class Cart", CC, CCBG, 128), ("테스트 코드", GRAY, "#EEF0F3", 44)]) + '</div></div>')
o.append(harrow(BX0 + BW0 + 30, BY0 + 150, 140, K4, WIPE(1)))
FXX = BX0 + BW0 + 200
FILES2 = [("product.py", "35줄, 상품", CP, CPBG, "kim", "#2459C9"), ("cart.py", "104줄, 장바구니", CC, CCBG, "lee", "#1F8A4C"), ("main.py", "주문하는 코드", CM, CMBG, "park", "#B26A00")]
o.append(f'<div{STAGGER(1, 120)} style="position:absolute;left:0;top:0;width:1920px;height:1080px">')
for i, (f_, d_, c_, b_, who, wc) in enumerate(FILES2):
    o.append(fchip(f"mw-{i}", f_, FXX, BY0 + i * 116, 470, c_, b_, sub=d_, h=100))
o.append('</div>')
for i, (f_, d_, c_, b_, who, wc) in enumerate(FILES2):
    o.append(p(f"position:absolute;left:{FXX + 500}px;top:{BY0 + i * 116 + 28}px;font-family:{MONO};font-size:28px;font-weight:700;color:#FFFFFF;background:{wc};border-radius:22px;padding:4px 22px", who, at(4, "fade") + DELAY(i * 100)))
RS = [("찾기", "상품을 고칠 땐 product.py만 열어요. 139줄을 뒤지지 않아요", K4), ("같이 쓰기", "Product 하나를 cart.py와 main.py가 import해서 같이 써요. 복사하지 않아요", K4), ("나눠 일하기", "06처럼 여럿이 일할 때 각자 다른 파일을 고쳐서 충돌이 줄어요", K4)]
for i, (t_, d_, c_) in enumerate(RS):
    o.append(f'<div{at(2 + i)}{DIM("mw")} style="position:absolute;left:{96 + i * 592}px;top:640px;width:552px;height:300px;display:flex;flex-direction:column;gap:14px;border-top:4px solid {c_};padding-top:22px">'
             + '<div style="display:flex;flex-direction:row;align-items:center;gap:16px">' + num(i + 1, c_, 36) + p(f"font-size:34px;font-weight:700;color:{INK}", e(t_)) + '</div>'
             + p(f"font-size:28px;line-height:1.5;color:{INK}", e(d_)) + '</div>')
o.append(pulse(3, "mw-0"))
o.append(caption("나눈 파일은 import로 다시 이어서 써요.", 950, 5))
W("m-why", o, "파일을 나누는 이유는 세 가지예요. 첫째, 찾기 쉬워요. 상품 코드를 고칠 땐 product.py만 열면 되고, 139줄짜리 한 파일을 뒤지지 않아도 돼요. 둘째, 같이 쓸 수 있어요. Product는 cart.py에서도 main.py에서도 필요한데, 복사해 붙이지 않고 import로 불러 써요. 복사해 두면 고칠 때 두 곳을 다 고쳐야 해요. 셋째, 나눠 일하기 좋아요. 06의 팀 레포처럼 kim은 product.py, lee는 cart.py를 맡으면 같은 줄을 동시에 고칠 일이 줄어서 충돌이 덜 나요.", ("p4", "모듈과 import"))

o = [sec("m-file")] + head(EB4, "파일 하나가 모듈 하나예요. 이름은 .py를 뺀 부분이에요", K4)
for i, (f_, c_, b_) in enumerate([("product", CP, CPBG), ("cart", CC, CCBG), ("coupon", CU, CUBG)]):
    y = T + 20 + i * 140
    o.append(p(f"position:absolute;left:96px;top:{y}px;font-family:{MONO};font-size:48px;font-weight:700;line-height:1.4;color:{c_};white-space:pre", e(f_) + f'<span{MARK(1)} style="color:#B8BDC7;text-decoration:line-through;text-decoration-thickness:4px">.py</span>'))
    o.append(harrow(560, y + 22, 120, "#C9CED8", WIPE(2)))
    o.append(p(f"position:absolute;left:720px;top:{y}px;font-family:{MONO};font-size:48px;font-weight:700;line-height:1.4;color:{INK};white-space:pre", "import " + f'<span style="color:{c_}">{e(f_)}</span>', at(2, "fade") + DELAY(200)))
o.append(p(f"position:absolute;left:96px;top:{T + 470}px;font-size:28px;font-weight:700;color:{SUB}", "09에서 본 import도 같은 문법이에요", at(3, "fade")))
o.append(p(f"position:absolute;left:96px;top:{T + 520}px;font-family:{MONO};font-size:40px;font-weight:700;line-height:1.4;color:{INK};white-space:pre", "import fastapi", at(3)))
o.append(tag(520, T + 548, "uv add로 받아 온 남의 모듈", GRAY, 3, size=28))
o.append(f'<div{at(4)} style="position:absolute;left:1240px;top:{T + 20}px;width:584px;display:flex;flex-direction:column;gap:18px;border-left:4px solid {K4};padding-left:30px">'
         + p(f"font-size:32px;font-weight:700;color:{INK}", "모듈 이름 짓기")
         + p(f"font-size:28px;line-height:1.5;color:{INK}", "영문 소문자로 지어요. 두 단어면 밑줄로 이어요.")
         + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{GR}", "shop_cart.py")
         + p(f"font-size:28px;line-height:1.5;color:{INK}", "띄어쓰기와 -는 import 뒤에 적을 수 없어요.")
         + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{RED};text-decoration:line-through", "shop-cart.py") + '</div>')
o.append(caption("실행한 파일과 같은 폴더에 있는 모듈은 이름만 적으면 찾아요.", 950, 5))
W("m-file", o, "파이썬 파일 하나를 모듈이라고 불러요. 모듈 이름은 파일 이름에서 .py를 뺀 부분이에요. product.py는 product 모듈이라서 import product로 불러요. 09에서 uv add fastapi 뒤에 import fastapi를 쳤던 것도 같은 문법이에요. 그때는 남이 만든 모듈을 받아 왔고, 오늘은 내가 만든 파일을 불러요. import 뒤에는 변수 이름처럼 적어야 해서, 파일 이름은 영문 소문자와 밑줄로 지어요. 띄어쓰기나 -가 들어간 파일은 import할 수 없어요.")

o = [sec("m-import")] + head(EB4, "import product는 모듈을 통째로 불러와요", K4)
MI = code_lines("import", "main.py")
ed, g = editor("mi-ed", "main.py", MI, 96, T, 980, fs=32, color=CM)
o.append(ed)
o.append(p(f"position:absolute;left:{gx(g, 'tumbler = '):.1f}px;top:{gtop(g, 2):.1f}px;font-family:{MONO};font-size:32px;line-height:{g['lh']:.2f}px;white-space:pre;color:{CP};background:{CPBG}", "product.", MARK(2)))
tt, tg = term("mi-t", [(cmd("import"), out("import"))], 96, int(T + g["h"] + 30), 980, fs=30, attrs=at(3))
o.append(tt)
o.append(link(3, gend(g, [MI[3]], 10), gly(g, 3), gend(tg, [out("import")[0]], 10), gly(tg, 1), CM))
o.append(modbox("mi-mod", "product", 1200, T + 40, 624, 300, CP, CPBG, attrs=at(1)))
o.append(fchip("mi-cls", "Product", 1250, T + 110, 300, CP, CARD, attrs=at(1), sub="상품 틀", h=100))
o.append(p(f"position:absolute;left:1250px;top:{T + 240}px;font-size:26px;color:{SUB}", "product.py 안의 모든 이름", at(1, "fade")))
o.append(tag(1200, T + 400, "꺼낼 때는 모듈 이름.안의 이름", CP, 2, lead=False, size=30))
o.append(code_big(1200, T + 460, "product.Product(...)", 38, INK, at(2)))
o.append(tag(1200, T + 560, "어느 파일에서 온 이름인지 코드에 보여요", INK, 2, lead=False, size=28, ex=DELAY(200)))
o.append(caption("점(.)은 '그 안의'라는 뜻이에요. 객체의 메서드를 부를 때와 같아요.", 950, 4))
W("m-import", o, "import product는 product.py를 통째로 불러와서 product라는 이름으로 묶어 둬요. 안에 있는 Product를 쓰려면 product.Product처럼 모듈 이름 뒤에 점을 찍고 적어요. 19에서 함수를 부르고 24에서 객체의 메서드를 점으로 불렀던 것처럼, 모듈 안의 이름도 점으로 꺼내요. 코드를 읽는 사람은 Product가 product.py에서 왔다는 걸 바로 알 수 있어요. 출력은 Product의 __str__이 만든 한 줄이에요." + REAL)

o = [sec("m-from")] + head(EB4, "from product import Product는 하나만 꺼내 와요", K4)
MF = code_lines("from", "main.py")
ed, g = editor("mf-ed", "main.py", MF, 96, T, 980, fs=32, color=CM)
o.append(ed)
tt, tg = term("mf-t", [(cmd("from"), out("from"))], 96, int(T + g["h"] + 30), 980, fs=30)
o.append(tt)
o.append(modbox("mf-mod", "product", 1200, T + 40, 624, 220, CP, CPBG))
o.append(fchip("mf-src", "Product", 1250, T + 100, 300, CP, CARD, sub="상품 틀", h=100))
o.append(f'<div style="position:absolute;left:1200px;top:{T + 380}px;width:624px;height:250px;background:{CMBG};border:3px solid {CM};border-radius:24px"></div>')
o.append(p(f"position:absolute;left:1224px;top:{T + 358}px;font-family:{MONO};font-size:28px;font-weight:700;color:#FFFFFF;background:{CM};border-radius:10px;padding:2px 16px", "main.py"))
o.append(f'<div data-build-in="fly order 1" data-from="mf-src" style="position:absolute;left:1250px;top:{T + 450}px;width:300px;height:100px;background:{CARD};border:3px solid {CP};border-radius:18px;display:flex;flex-direction:column;justify-content:center;padding:0 24px">'
         + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{CP}", "Product") + p(f"font-size:24px;color:{SUB}", "이름만 써요") + '</div>')
o.append(lband(1, g, 0, 1, "mark"))
o.append(lband(2, g, 2, 1, "mark"))
o.append(tag(gend(g, [MF[2]], 20), gly(g, 2), "product. 없이", CM, 2, size=28))
o.append(caption("수업 코드 cart.py 1번 줄이 바로 이 모양이에요.", 950, 3))
W("m-from", o, "from product import Product는 product 모듈에서 Product 하나만 꺼내 와서 main.py에 놓아 둬요. 그래서 product.를 붙이지 않고 Product라고만 써요. 출력은 앞 장과 똑같아요. 수업 코드 cart.py 1번 줄이 바로 이 모양이에요. cart.py는 Product를 여러 번 쓰니까 짧게 부를 수 있는 쪽을 골랐어요." + REAL)

o = [sec("m-many")] + head(EB4, "from coupon import COUPONS, discount로 여러 개를 꺼내요", K4)
CPL = L(COUPON)
ed, g = editor("mm-ed1", "coupon.py", CPL, 96, T, 900, fs=26, color=CU)
o.append(ed)
MM = code_lines("from-many", "main.py")
ed2, g2 = editor("mm-ed2", "main.py", MM, 96, int(T + g["h"] + 26), 900, fs=26, color=CM)
o.append(ed2)


def paint(g_, i, pre, word, color, order, bg=None):
    b = f"background:{bg};" if bg else ""
    return p(f"position:absolute;left:{gx(g_, pre):.1f}px;top:{gtop(g_, i):.1f}px;font-family:{MONO};font-size:{g_['fs']}px;line-height:{g_['lh']:.2f}px;white-space:pre;color:{color};{b}", e(word), MARK(order))


o.append(paint(g, 0, "", "COUPONS", CU, 1, CUBG))
o.append(paint(g, 3, "def ", "discount", OR, 1, "#F7EEDD"))
o.append(paint(g2, 0, "from coupon import ", "COUPONS", CU, 1, CUBG))
o.append(paint(g2, 0, "from coupon import COUPONS, ", "discount", OR, 1, "#F7EEDD"))
tt, tg = term("mm-t", [(cmd("from-many"), out("from-many"))], 1060, T, 764, fs=26, attrs=at(3))
o.append(tt)
o.append(modbox("mm-mod", "coupon", 1060, T + 330, 764, 170, CU, CUBG, attrs=at(2)))
o.append(fchip("mm-c1", "COUPONS", 1100, T + 380, 300, CU, CARD, attrs=at(2), h=80))
o.append(fchip("mm-c2", "discount", 1440, T + 380, 300, OR, CARD, attrs=at(2), h=80))
o.append(tag(1060, T + 560, "쉼표로 이어서 필요한 것만 꺼내요", K4, 2, lead=False, size=30))
o.append(tag(1060, T + 620, "딕셔너리 칸도, 함수도 꺼낼 수 있어요", INK, 2, lead=False, size=28, ex=DELAY(200)))
o.append(caption("없는 쿠폰 HELLO는 get의 기본값 0이 나와요.", 950, 4))
W("m-many", o, "쿠폰 기능을 coupon.py라는 새 모듈로 만들었어요. 쿠폰 표 딕셔너리 COUPONS와 할인 금액을 돌려주는 함수 discount가 들어 있어요. main.py에서 둘 다 쓰고 싶으면 import 뒤에 쉼표로 이어서 적어요. 같은 색끼리 짝이에요. 꺼낸 이름은 main.py에서 바로 쓸 수 있어요. 없는 쿠폰은 15에서 배운 get의 기본값 0이 돌아와요." + REAL)

o = [sec("m-as")] + head(EB4, "as로 모듈에 짧은 별명을 붙여요", K4)
MA = code_lines("as", "main.py")
ed, g = editor("ma-ed", "main.py", MA, 96, T, 980, fs=34, color=CM)
o.append(ed)
o.append(paint(g, 0, "import coupon ", "as cp", K4, 1, K4BG))
o.append(paint(g, 2, "print(", "cp", K4, 1, K4BG))
tt, tg = term("ma-t", [(cmd("as"), out("as"))], 96, int(T + g["h"] + 30), 980, fs=30)
o.append(tt)
o.append(modbox("ma-mod", "cp", 1200, T + 40, 624, 200, CU, CUBG, nid="ma-name\" data-start=\"coupon"))
o.append(text(1, "ma-name", "cp"))
o.append(p(f"position:absolute;left:1240px;top:{T + 120}px;font-size:28px;color:{SUB}", "coupon.py를 cp라는 이름으로"))
o.append(tag(1200, T + 330, "이름이 길 때 줄여 불러요", K4, 2, lead=False, size=30))
o.append(code_big(1200, T + 390, "import pandas as pd", 34, GRAY, at(2)))
o.append(tag(1200, T + 460, "나중에 데이터 다룰 때 자주 보는 모양이에요", GRAY, 2, lead=False, size=26, ex=DELAY(200)))
o.append(f'<div{at(3)} style="position:absolute;left:96px;top:800px;width:1728px;display:flex;flex-direction:row;align-items:center;gap:28px;border-top:2px solid {LINE};padding-top:30px">'
         + p(f"font-family:{MONO};font-size:34px;font-weight:700;color:{RED};text-decoration:line-through;text-decoration-thickness:3px;white-space:pre", "from coupon import *")
         + p(f"font-size:30px;font-weight:700;line-height:1.4;color:{INK}", "*는 모든 이름을 가져와요. 무엇이 들어왔는지 안 보여서 쓰지 않아요.") + '</div>')
W("m-as", o, "import 뒤에 as를 붙이면 모듈에 별명을 지어 줄 수 있어요. import coupon as cp라고 쓰면 coupon 대신 cp로 불러요. 이름이 길 때 줄이려고 써요. 나중에 데이터를 다룰 때 import pandas as pd 같은 모양을 자주 볼 거예요. 아래 별표 모양은 모듈 안의 모든 이름을 한꺼번에 가져와요. 코드만 보고는 어떤 이름이 들어왔는지 알 수 없고, 내 변수와 이름이 겹치면 덮어써져서 쓰지 않아요." + REAL)

o = [sec("m-table")] + head(EB4, "모양마다 쓰는 법과 고르는 때가 달라요", K4)
MT = [["import product", "product.Product(...)", "어느 모듈 것인지 보이게"], ["from product import Product", "Product(...)", "하나를 여러 번 쓸 때"],
      ["from coupon import COUPONS, discount", "discount(\"VIP\")", "몇 개만 골라 쓸 때"], ["import coupon as cp", "cp.discount(\"VIP\")", "모듈 이름이 길 때"], ["from coupon import *", "쓰지 않아요", "무엇이 왔는지 안 보여요"]]
o += table(96, T + 10, 1728, MT, [700, 480, 500], mono=(0, 1), rh=118, head_=["모양", "쓰는 법", "고르는 때"], fs=30, colors=[INK, None, None])
for i in range(5):
    o.append(spot(1 + i, 96, T + 10 + 52 + i * 118, 1728, 118, pad=4, r=10, dim=0.45))
o.append(spot_off(6))
o.append(caption("헷갈리면 수업 코드처럼 from 파일 import 이름부터 써요.", 950, 6))
W("m-table", o, "import 모양 다섯 가지를 한 표로 모았어요. 어느 모듈 것인지 코드에 드러내고 싶으면 import product, 하나를 여러 번 쓰면 from product import Product예요. 몇 개만 골라 쓰면 쉼표로 이어요. 모듈 이름이 길면 as로 줄여요. 별표는 쓰지 않아요. 오늘 장바구니 프로젝트에서는 수업 코드처럼 from 파일 import 이름 모양을 기본으로 쓰면 돼요.")

o = [sec("m-error")] + head(EB4, "이름이 틀리면 ModuleNotFoundError, ImportError가 나요", K4)
for k, (sc, why, fixs, y0) in enumerate([("err-typo", "prodcut.py라는 파일이 없어요. 파일 이름의 오타예요", "import product", T),
                                         ("err-name", "product.py 안에 소문자 product가 없어요. 대소문자가 달라요", "from product import Product", T + 370)]):
    tt, tg = term(f"me-t{k}", [(cmd(sc), out(sc))], 96, y0, 1728, fs=22, attrs=at(1 + 2 * k) if k else "")
    o.append(tt)
    last = out(sc)[-1]
    o.append(underline(1 + 2 * k, tg["tx"], tg["tx"] + etw(last.split(":")[0], 22), gly(tg, len(out(sc))) + 16, RED))
    if "Did you mean" in last:
        o.append(underline(2 + 2 * k, tg["tx"] + etw(last[:last.index("Did")], 22), tg["tx"] + etw(last, 22), gly(tg, len(out(sc))) + 16, OR))
    o.append(f'<div{at(2 + 2 * k)} style="position:absolute;left:96px;top:{y0 + tg["h"] + 20:.0f}px;width:1728px;display:flex;flex-direction:row;align-items:center;gap:26px">'
             + p(f"font-size:28px;font-weight:700;color:{INK}", e(why))
             + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{INK};background:#E6F4EC;border:3px solid {GR};border-radius:12px;padding:6px 18px;white-space:pre", e(fixs)) + '</div>')
o.append(caption("파일 이름과 대소문자를 먼저 봐요. Did you mean이 보이면 그 이름이 정답 후보예요.", 950, 5))
W("m-error", o, "import에서 나는 오류 두 가지예요. 위는 모듈 이름에 오타가 있을 때예요. prodcut이라는 모듈을 못 찾았다는 ModuleNotFoundError가 나요. 아래는 모듈은 찾았는데 그 안에 그런 이름이 없을 때예요. 클래스 이름은 대문자 P로 시작하는데 소문자로 적었어요. 파이썬 3.14는 Did you mean으로 비슷한 이름을 알려 줘요. 오류에 적힌 경로는 실습 폴더라서 수강생 화면에서는 다르게 보여요." + REAL)

o = [sec("m-error2")] + head(EB4, "import product만 하고 Product라고 쓰면 NameError예요", K4)
sc = "err-noname"
NN = code_lines(sc, "main.py")
ed, g = editor("mn-ed", "main.py", NN, 96, T, 1000, fs=32, color=CM)
o.append(ed)
o.append(lband(1, g, 2, 1, "err"))
tt, tg = term("mn-t", [(cmd(sc), out(sc))], 96, int(T + g["h"] + 30), 1728, fs=24)
o.append(tt)
last = out(sc)[-1]
o.append(underline(1, tg["tx"], tg["tx"] + etw(last.split(":")[0], 24), gly(tg, len(out(sc))) + 18, RED))
o.append(underline(2, tg["tx"] + etw(last[:last.index("Did")], 24), tg["tx"] + etw(last, 24), gly(tg, len(out(sc))) + 18, OR))
FY2 = int(tg["top"] + tg["h"] + 44)
o.append(fixv(96, FY2, 820, "", "product.Product(...)", 3, size=30, label="고치기 1: 점을 찍어 써요"))
o.append(fixv(960, FY2, 864, "", "from product import Product", 4, size=30, label="고치기 2: 맨 위를 바꿔요"))
W("m-error2", o, "import product는 모듈을 product라는 이름으로 불러올 뿐, Product라는 이름을 main.py에 놓아 주지 않아요. 그래서 Product라고만 쓰면 그런 이름이 없다는 NameError가 나요. 파이썬이 Did you mean: 'product'?로 힌트를 줘요. 고치는 방법은 둘이에요. product.Product로 점을 찍어 쓰거나, 맨 위를 from product import Product로 바꿔요." + REAL)

# ---------- part 5: __name__ ----------
o = [sec("n-leak")] + head(EB5, "cart.py를 import했더니 테스트 출력이 먼저 나와요", K5)
NL = code_lines("leak", "main.py")
ed, g = editor("nl-ed", "main.py", NL, 96, T, 760, fs=28, color=CM)
o.append(ed)
TL = rng(CL, 94, 104)
ed2, g2 = editor("nl-ed2", "cart.py", TL, 96, int(T + g["h"] + 30), 760, fs=22, start=94, color=CC)
o.append(ed2)
o.append(ibox(2, g2, 0, 0, len(TL) - 1, RED))
o.append(tag(96, g2["top"] + g2["h"] + 34, "if 없이 파일 맨 아래에 그냥 있어요", RED, 2, lead=False, size=26))
LO = out("leak")
TH = 1000 - T
tt, tg = term("nl-t", [(cmd("leak"), LO)], 900, T, 924, fs=22, h=TH, inner="nl-in", attrs=at(1))
o.append(tt)
o.append(shake(1, "nl-t"))
vis = (TH - 44 - 28) / tg["lh"]
shift = int((len(LO) + 1 - vis) * tg["lh"]) + 8
o.append(f'<div{at(2, "fade")} style="position:absolute;left:908px;top:{gtop(tg, 1):.0f}px;width:908px;height:{(len(LO) - 1) * tg["lh"]:.0f}px;background:{RED}30;border-radius:8px"></div>' if False else "")
o.append(pan(3, "nl-in", -shift))
o.append(p(f"position:absolute;left:1440px;top:{T + TH - 80}px;font-size:26px;font-weight:700;color:#FFFFFF;background:{GR};border-radius:10px;padding:6px 16px", "main.py 시작은 맨 끝", at(3, "fade") + DELAY(1800)))
W("n-leak", o, "main.py에서 from cart import Cart 한 줄만 적고 실행했어요. 그런데 cart.py 맨 아래의 테스트 코드가 먼저 실행돼서 장바구니 출력이 줄줄이 나와요. import는 그 파일을 위에서부터 한 번 실행해서 이름을 만들어요. 그래서 파일 맨 아래에 그냥 적어 둔 코드도 같이 실행돼요. main.py의 첫 출력은 터미널 맨 끝에 가서야 보여요. 다음 장에서 파이썬이 '직접 실행'과 'import'를 어떻게 구별하는지 봐요." + REAL, ("p5", '__name__ == "__main__"'))

o = [sec("n-name")] + head(EB5, "직접 실행한 파일만 __name__이 \"__main__\"이에요", K5)
NM = code_lines("name", "main.py")
CBL = L(CART_BODY)
nline = len(CBL) + 2
ed, g = editor("nn-ed1", "cart.py", ["⋮", 'print("cart.py의 __name__:", __name__)'], 96, T, 900, fs=26, nums=["", str(nline)], color=CC)
o.append(ed)
ed2, g2 = editor("nn-ed2", "main.py", NM, 96, int(T + g["h"] + 26), 900, fs=26, color=CM)
o.append(ed2)
t1, tg1 = term("nn-t1", [(cmd("name", 0), out("name", 0))], 1060, T, 764, fs=26, attrs=at(1))
o.append(t1)
t2, tg2 = term("nn-t2", [(cmd("name", 1), out("name", 1))], 1060, int(T + tg1["h"] + 30), 764, fs=26, attrs=at(2))
o.append(t2)
v1 = out("name", 0)[0]
o.append(p(f"position:absolute;left:{tg1['tx'] + etw(v1[:v1.index('__main__')], 26):.1f}px;top:{gtop(tg1, 1):.1f}px;font-family:{MONO};font-size:26px;line-height:{tg1['lh']:.2f}px;white-space:pre;color:#7DD3A0;font-weight:700", "__main__", MARK(1)))
v2 = out("name", 1)[0]
o.append(p(f"position:absolute;left:{tg2['tx'] + etw(v2[:v2.rindex('cart')], 26):.1f}px;top:{gtop(tg2, 1):.1f}px;font-family:{MONO};font-size:26px;line-height:{tg2['lh']:.2f}px;white-space:pre;color:#FFC46B;font-weight:700", "cart", MARK(2)))
o.append(zoom(2, 1060, tg2["top"], 764, tg2["h"]))
o.append(zoom_off(3))
TY3 = int(tg2["top"] + tg2["h"] + 50)
o += table(96, max(TY3, int(g2["top"] + g2["h"] + 50)), 1728, [["uv run cart.py로 직접 실행", '"__main__"'], ["다른 파일이 import로 부름", '"cart" (모듈 이름)']], [900, 700], mono=(1,), order0=3, rh=84, head_=["cart.py가 실행된 방법", "cart.py의 __name__"], fs=30)
W("n-name", o, "파이썬은 파일마다 __name__이라는 이름을 하나씩 만들어 둬요. cart.py 맨 아래에 __name__을 찍는 줄을 넣고 두 번 실행해 봤어요. uv run cart.py로 직접 실행하면 __name__은 \"__main__\"이에요. uv run main.py로 실행하면 main.py가 \"__main__\"이 되고, import로 불려 온 cart.py는 자기 모듈 이름 \"cart\"가 돼요. 이 차이로 직접 실행한 건지, import로 불린 건지 구별할 수 있어요." + REAL)

o = [sec("n-fix")] + head(EB5, "테스트 코드는 if __name__ == \"__main__\": 안에 넣어요", K5)
GT = rng(GL, len(L(CART_BODY)) + 3, len(GL))
ed, g = editor("nf-ed", "cart.py", GT, 96, T, 900, fs=26, start=len(L(CART_BODY)) + 3, color=CC)
o.append(ed)
gi = GT.index('if __name__ == "__main__":')
o.append(lband(1, g, gi, 1, "mark"))
o.append(ibox(1, g, 4, gi + 1, len(GT) - 1, K5))
o.append(tag(gend(g, [GT[gi]], 24), gly(g, gi), "직접 실행할 때만 True", K5, 1, size=26))
t1, tg1 = term("nf-t1", [(cmd("guarded", 0), out("guarded", 0))], 1060, T, 764, fs=24, attrs=at(2))
o.append(t1)
o.append(tag(1060, int(tg1["top"] + tg1["h"] + 36), "import할 때는 테스트가 안 돌아요", GR, 2, lead=False, size=26))
t2, tg2 = term("nf-t2", [(cmd("guarded", 1), out("guarded", 1))], 1060, int(tg1["top"] + tg1["h"] + 80), 764, fs=19, attrs=at(3))
o.append(t2)
o.append(p(f"position:absolute;left:96px;top:{int(g['top'] + g['h'] + 40)}px;width:900px;font-size:28px;line-height:1.5;color:{INK}", "product.py 26번 줄에는 이미 이 줄이 있어요. 그래서 product.py를 import해도 상품 목록이 찍히지 않았어요.", at(4)))
ed3, g3 = editor("nf-ed3", "product.py", [PL[25]], 96, int(g['top'] + g['h'] + 150), 900, fs=26, start=26, color=CP, attrs=at(4))
o.append(ed3)
W("n-fix", o, "테스트 코드를 if __name__ == \"__main__\": 아래로 4칸 들여 넣었어요. cart.py를 직접 실행하면 __name__이 \"__main__\"이라 조건이 True가 되고 테스트가 돌아요. main.py가 import하면 __name__이 \"cart\"라서 False가 되고 건너뛰어요. 오른쪽 위 터미널처럼 main.py의 출력만 깔끔하게 나와요. product.py 26번 줄에는 수업에서 이미 이 줄을 넣어 뒀어요. 파일을 import할 일이 있으면 테스트 코드는 언제나 이 안에 둬요. 슬라이드의 테스트 코드는 담고 보여 주는 부분만 남겨 짧게 줄였어요." + REAL)


# ---------- part 6: practice ----------
o = [sec("x-shop")] + head(EB6, "main.py에서 상품과 장바구니를 불러 주문해요", K6)
XS = L(MAIN_SHOP)
ed, g = editor("xs-ed", "main.py", XS, 96, T, 920, fs=25, color=CM)
o.append(ed)
XO = out("shop")
tt, tg = term("xs-t", [(cmd("shop"), XO)], 1060, T, 764, fs=21)
o.append(tt)
o.append(lband(1, g, 0, 2, "mark"))
o.append(tag(gend(g, XS[0:2], 24), gly(g, 0.5), "두 파일에서 하나씩", CM, 1, size=26))
pi = XS.index("cart.add(pad, 1)")
o.append(tint(2, g, pi, 1, RED))
o.append(tint(2, tg, 3, 1, RED, dark=True))
o.append(tag(gend(g, [XS[pi]], 24), gly(g, pi), "재고 0이라 품절", RED, 2, size=26))
ci = XS.index("cart.checkout()")
o.append(tint(3, g, ci, 1, GR))
o.append(tint(3, tg, 4, 9, GR, dark=True))
o.append(tag(gend(g, [XS[ci]], 24), gly(g, ci), "영수증을 찍어요", GR, 3, size=26))
ti = XS.index("print(tumbler)")
o.append(tint(4, g, ti, 2, BL))
o.append(tint(4, tg, len(XO) - 1, 2, BL, dark=True))
o.append(tag(tg["left"], int(tg["top"] + tg["h"] + 36), "텀블러 재고가 10개에서 8개로 줄었어요", BL, 4, lead=False, size=26))
o.append(caption("상품은 product.py, 장바구니는 cart.py, 주문은 main.py가 맡아요.", 950, 5))
W("x-shop", o, "이제 main.py에서 두 모듈을 불러 실제로 주문해 봐요. 맨 위 두 줄로 Product와 Cart를 꺼내 와요. 텀블러 2개와 이어폰 1개는 담기고, 재고가 0인 마우스패드는 품절이라 안 담겨요. checkout()이 영수증을 찍고 재고를 줄여서, 마지막에 텀블러 재고가 10개에서 8개가 됐어요. cart.py는 테스트 코드를 if __name__ 안에 넣은 판이라 테스트 출력이 섞이지 않아요. 상품 번호 1, 2는 26에서 배운 클래스 변수 next_id가 매겨 줬어요." + REAL, ("p6", "실습"))

o = [sec("x-coupon")] + head(EB6, "coupon.py를 더해 세 가지를 한 번에 써요", K6)
XC = L(MAIN_COUPON)
ed, g = editor("xc-ed", "main.py", XC, 96, T, 950, fs=24, color=CM)
o.append(ed)
ed2, g2 = editor("xc-ed2", "coupon.py", CPL, 1080, T, 744, fs=22, color=CU)
o.append(ed2)
XCO = out("coupon")
tt, tg = term("xc-t", [(cmd("coupon"), XCO)], 1080, int(T + g2["h"] + 26), 744, fs=22)
o.append(tt)
o.append(paint(g, 2, "from coupon import ", "COUPONS", CU, 1, CUBG))
o.append(paint(g, 2, "from coupon import COUPONS, ", "discount", OR, 1, "#F7EEDD"))
o.append(paint(g2, 0, "", "COUPONS", CU, 1, CUBG))
o.append(paint(g2, 3, "def ", "discount", OR, 1, "#F7EEDD"))
fi2 = XC.index("for code, amount in COUPONS.items():")
o.append(lband(2, g, fi2, 2, "mark"))
o.append(f'<div{at(2, "fade")} style="position:absolute;left:{tg["left"] + 8}px;top:{gtop(tg, 1):.0f}px;width:{tg["w"] - 16}px;height:{2 * tg["lh"]:.0f}px;background:#2F7DE155;border-radius:6px"></div>')
pi2 = XC.index('pay = cart.total() - discount("VIP")')
o.append(lband(3, g, pi2, 2, "run"))
o.append(f'<div{at(3, "fade")} style="position:absolute;left:{tg["left"] + 8}px;top:{gtop(tg, len(XCO)):.0f}px;width:{tg["w"] - 16}px;height:{tg["lh"]:.0f}px;background:#1F8A4C77;border-radius:6px"></div>')
o.append(tag(tg["left"], int(tg["top"] + tg["h"] + 36), "45,000원 - VIP 5,000원", GR, 3, lead=False, size=26))
TP = [("들여쓰기", "def와 for 안은 4칸", K2), ("items()", "for code, amount in COUPONS.items()", K3), ("import", "from coupon import COUPONS, discount", K4)]
o.append(f'<div{STAGGER(4, 120)} style="position:absolute;left:0;top:0;width:1920px;height:1080px">')
for i, (a_, b_, c_) in enumerate(TP):
    o.append(f'<div style="position:absolute;left:{96 + i * 592}px;top:{int(g["top"] + g["h"] + 40)}px;width:552px;display:flex;flex-direction:column;gap:8px;border-top:4px solid {c_};padding-top:14px">'
             + p(f"font-size:28px;font-weight:700;color:{c_}", e(a_)) + p(f"font-family:{MONO if b_.isascii() else SANS};font-size:22px;font-weight:700;color:{INK};white-space:pre", e(b_)) + '</div>')
o.append('</div>')
W("x-coupon", o, "마지막으로 앞 장의 coupon.py를 더해 쿠폰을 써요. main.py 맨 위에서 세 모듈을 불러와요. 쿠폰 목록은 COUPONS.items()로 코드와 할인 금액을 한 쌍씩 꺼내서 찍어요. 텀블러 3개는 45,000원이라 배송비가 없고, VIP 쿠폰 5,000원을 빼서 40,000원이에요. 아래 세 칸처럼 오늘 본 세 가지가 이 짧은 파일에 다 들어 있어요. 직접 쿠폰을 하나 더 넣고, discount에 그 코드를 넘겨 보세요." + REAL)

# ---------- wrap up ----------
o = [sec("trouble")] + head("정리", "막히면 오류의 마지막 줄을 봐요", RED)
TR = [("IndentationError: expected an indented block", "콜론 다음 줄이 안으로 안 들어갔어요", "4칸 넣기"),
      ("IndentationError: unindent does not match ...", "위 줄들과 칸 수가 안 맞아요", "Tab, Shift+Tab"),
      ("TypeError: cannot unpack non-iterable Product object", "딕셔너리를 .items() 없이 돌았어요", ".items()"),
      ("ModuleNotFoundError: No module named ...", "파일 이름 오타, 다른 폴더에서 실행", "파일 이름 확인"),
      ("ImportError: cannot import name ...", "모듈 안에 그 이름이 없어요. 대소문자", "Did you mean"),
      ("import했더니 테스트 출력이 나와요", "테스트 코드가 if __name__ 밖에 있어요", 'if __name__ == "__main__":')]
o.append(f'<div{STAGGER(1, 90)} style="position:absolute;left:0;top:0;width:1920px;height:1080px">')
for i, (q, a_, c_) in enumerate(TR):
    o.append(f'<div style="position:absolute;left:96px;top:{T + i * 110}px;width:1728px;height:110px;display:flex;flex-direction:row;align-items:center;gap:28px;border-bottom:2px solid {LINE}">'
             + p(f"width:40px;flex:none;font-size:30px;font-weight:900;color:{RED}", str(i + 1))
             + '<div style="flex:1;display:flex;flex-direction:column;gap:2px">' + p(f"{'font-family:' + MONO + ';' if q.isascii() else ''}font-size:26px;font-weight:700;color:{INK};white-space:nowrap", e(q)) + p(f"font-size:24px;color:{SUB}", e(a_)) + '</div>'
             + p(f"{'font-family:' + MONO + ';font-size:24px;' if c_.replace(',', '').replace(' ', '').isascii() else 'font-size:25px;'}font-weight:700;line-height:1.4;color:{INK};background:#E6F4EC;padding:6px 18px;border-radius:12px;white-space:pre", e(c_)) + '</div>')
o.append('</div>')
o.append(caption("uv run은 프로젝트 폴더(shopping-cart) 안에서 쳐요.", 920, 2))
W("trouble", o, "이번 챕터에서 자주 만나는 일을 모았어요. 1번과 2번은 들여쓰기예요. 오류에 나온 줄 번호로 가서 위 줄과 칸을 맞춰요. 3번은 딕셔너리를 .items() 없이 돌았을 때예요. 4번과 5번은 import 이름이 틀렸을 때예요. ModuleNotFoundError가 나면 터미널이 프로젝트 폴더 안에 있는지도 봐요. 6번은 오류는 없지만 테스트 출력이 섞이는 경우예요.", ("trouble", "정리"))

o = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:80px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>']
CH = [[("콜론(:) 다음 줄", "4칸 더 들어가서 그 상자 안", K2), ("Tab / Shift+Tab", "고른 줄을 4칸 안으로, 밖으로", K2), ("a, b = (1, 2)", "튜플을 두 칸에 나눠 담기", K3), ("for p, q in d.items():", "키와 값을 한 쌍씩 꺼내기", K3)],
      [("import product", "product.Product(...)로 쓰기", K4), ("from product import Product", "Product(...)로 바로 쓰기", K4), ("from coupon import A, B", "쉼표로 여러 개, as로 별명", K4), ('if __name__ == "__main__":', "직접 실행할 때만 테스트", K5)]]
o.append(f'<div{STAGGER(1, 80)} style="position:absolute;left:0;top:0;width:1920px;height:1080px">')
for col, items in enumerate(CH):
    for i, (k, d, c) in enumerate(items):
        o.append(f'<div style="position:absolute;left:{96 + col * 888}px;top:{212 + i * 128}px;width:840px;height:128px;display:flex;flex-direction:column;justify-content:center;gap:8px;border-bottom:2px solid {LINE}">'
                 + p(f"{'font-family:' + MONO + ';' if k.isascii() else ''}font-size:32px;font-weight:700;color:{c};white-space:pre", e(k))
                 + p(f"font-size:28px;color:{INK}", e(d)) + '</div>')
o.append('</div>')
o.append(p(f"position:absolute;left:96px;top:780px;width:1728px;font-size:36px;font-weight:700;line-height:1.4;color:{INK}", "파일 안은 들여쓰기로, 파일 사이는 import로 나눠요.", at(2)))
o.append(p(f"position:absolute;left:96px;top:860px;width:1728px;font-size:30px;line-height:1.4;color:{SUB}", "다음 수업에서 장바구니에 기능을 더할 때도 새 파일을 만들고 import로 이어 붙여요.", at(2)))
W("cheatsheet", o, "이번 챕터를 한 장에 모았어요. 들여쓰기는 콜론 다음 줄을 4칸 넣어 상자를 만들고, VS Code에서는 Tab과 Shift+Tab으로 맞춰요. 딕셔너리는 .items()로 키와 값을 한 쌍씩 꺼내고, for 옆 이름 두 칸에 나눠 담아요. 파일은 역할마다 나누고 import로 이어요. import할 파일의 테스트 코드는 if __name__ == \"__main__\": 안에 둬요. 장바구니에 기능을 더할 때도 새 파일을 만들어 import로 붙여 보세요.")

finish([(K1, "왜 필요한가", "자주 막히는 세 곳, 프로젝트 안의 위치", "w-why", "w-big"),
        (K2, "들여쓰기는 상자", "상자 안의 상자, for 안과 밖, return, 오류, Tab", "i-box", "i-keys"),
        (K3, "for p, q in items()", "튜플 나눠 담기, 한 쌍씩, 긴 방법, 합계, 오류", "u-tuple", "u-error"),
        (K4, "모듈과 import", "나누는 이유, import 모양 다섯 가지, 오류", "m-why", "m-error2"),
        (K5, "if __name__", "섞여 나오는 테스트 출력, __name__, 고치기", "n-leak", "n-fix"),
        (K6, "실습", "main.py에서 주문하기, 쿠폰 모듈 더하기", "x-shop", "x-coupon")],
       "여섯 파트로 나눴어요. 1파트는 장바구니 코드에서 막히는 세 곳과 큰 그림이에요. 2파트는 들여쓰기, 3파트는 items()와 for p, q예요. 4파트는 파일을 나누는 이유와 import 쓰는 법, 5파트는 import할 때 섞여 나오는 테스트 출력을 막는 법이에요. 6파트에서 main.py로 주문하고 쿠폰 모듈을 더해요.",
       "미니 프로젝트: 장바구니 (들여쓰기, items, 모듈)")
