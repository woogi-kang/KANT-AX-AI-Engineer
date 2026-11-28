"""Generates every slide of the plotting and practice-data deck (47) and slides/deck.json.

Story: class notebook 02_ml.ipynb, first half (the second half, linear regression, is chapter 48). Starts from office.head()
next to its scatter (a table hides the rule, dots show it), the five-step machine learning map (47 draws and makes data,
48 learns and scores) and the three libraries (pandas, matplotlib.pyplot, NumPy random). Part 2 builds the class's line
chart one call at a time (fig and ax, figsize, plot's x/y/marker/label, set_ names, legend, plt. vs ax. styles). Part 3
reads usa_housing.csv, explains scatter, alpha, color and s, and the correlation trap (0.08 for 300 houses, 0.89 for the 10
picked ones). Part 4 makes the office data whose rule we know (price = area x 450 + 5000): seed, rng order, uniform,
normal, round(-1), array math, choice without replacement, price[special] +=, describe and to_csv(index=False).
Part 5: missing font, plot instead of scatter, x and y of different length, a wrong path. Part 6: two lines with a legend,
the office scatter (corr 0.90) and the usa_housing columns that all sit near 0.
Every cell and output comes from tools/demo.sh (tools/run_nb.py runs the cells with the project kernel), kept in
tools/demo.log. Charts are the kernel's own PNGs in tools/img (NanumGothic stands in for Malgun Gothic on Linux).

Layout rules (Stageshow skill, github.com/benjitaylor/skills, read in full for this deck):
1. one focal object per slide (a notebook cell, a chart from the kernel, one code line taken apart, or one diagram)
2. terms are labelled on the code token or the chart part with leader tags and tints, not in separate cards (annotations.md)
3. say it once: what the speaker notes say does not repeat in cards; one caption at most
4. no empty bands: the chart or the code grows to fill; the payoff gets the room (craft.md, Restraint)
5. values move instead of swapping: the formula columns build left to right, the rng order links each print to its numbers
6. one number gets to be big (0.08 against 0.89), the rest are lines (craft.md, Restraint)
Highlights come from tools/HIGHLIGHT.md, as many kinds as fit. No typing effect.
Usage: python3 tools/gen.py slides
"""


import base64
import html, json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from highlight import (spot, spot_off, cursor, cursor_off, ring, box, underline, lspot, lspot_off, run, run_off, zoom, zoom_off,
                       shine, shake, pulse, grow, link, keys, compare, kenburns, SLAM, COUNT, MARK, DELAY, WIPE, STAGGER, MORPH, MORPH_FROM, tok)

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
GRBG = "#E6F4EC"
REAL = " 출력은 실제로 실행한 결과예요."
CV, CF, CI, CK = "#B8E8BE", "#8FD8DE", "#F2A0A0", "#E3B877"   # value, for, if, key colors on dark strips
LV, LF, LI = GR, TEAL, RED                                     # same parts on light ground
W_ = "#E6E9EF"
DARK = "#252B36"


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


def caption(text, top=950, order=None):
    at = f' data-build-in="rise order {order}"' if order else ' data-build-in="rise"'
    return p(f"position:absolute;left:96px;top:{top}px;width:1728px;font-size:34px;font-weight:700;line-height:1.4;color:{INK}", text, ' id="caption"' + at)


def num(i, color, size=40):
    return p(f"width:{size + 16}px;height:{size + 16}px;flex:none;border-radius:50%;background:{color};color:#FFFFFF;font-size:{size * 0.6:.0f}px;font-weight:900;line-height:{size + 16}px;text-align:center", str(i))


def kbd(text, size=30):
    caps = [p(f"font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.2;white-space:nowrap;color:{INK};background:#FFFFFF;border:2px solid #C9CED8;border-bottom-width:5px;border-radius:10px;padding:6px 14px", e(k)) for k in text.split("+")]
    plus = p(f"font-size:{size * 0.8:.0f}px;font-weight:700;color:{GRAY}", "+")
    return '<div style="display:flex;flex-direction:row;align-items:center;gap:8px">' + plus.join(caps) + '</div>'


def arrow(w=60, color="#C9CED8", attrs="", style=""):
    return f'<x-shape{attrs} kind="arrow-right" style="width:{w}px;height:30px;flex:none;background:{color};{style}"></x-shape>'


def tf(v, size=28):
    c, bg = (GR, GRBG) if v == "True" else (RED, K5BG)
    return p(f"display:inline-block;font-family:{MONO};font-size:{size}px;font-weight:700;color:{c};background:{bg};border-radius:10px;padding:2px 14px;white-space:nowrap", v)


# ---------- notebook cell, drawn at CFS[0] px ----------
CFS = [30]
HL = {"run": "rgba(31,138,76,0.16)", "skip": "rgba(106,113,128,0.20)", "err": "rgba(163,49,49,0.14)", "mark": "rgba(36,89,201,0.14)"}
HLT = {"run": GR, "skip": GRAY, "err": RED, "mark": BL}


def LH():
    return CFS[0] * 1.45


def cell(c, left, top, w, sel=None, attrs=""):
    """c: dict(id, lines, n, out, err). Same look as chapters 12-22, code at CFS[0] px."""
    fs, lines, n = CFS[0], c.get("lines", [""]), c.get("n")
    chosen = sel == c["id"]
    o = [f'<div id="{c["id"]}"{attrs or c.get("attrs", "")} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;display:flex;flex-direction:column;gap:10px">']
    bar = f'<div style="width:7px;flex:none;border-radius:4px;background:{SEL if chosen else "transparent"}"></div>'
    gutter = p(f"width:58px;flex:none;font-family:{MONO};font-size:22px;color:{GRAY};text-align:right;padding-top:12px", f"[{n}]" if n else "[ ]")
    txt = "".join(p(f"font-family:{MONO};font-size:{fs}px;line-height:1.45;white-space:pre;color:{INK}", e(l) if l else "&#160;") for l in lines)
    tg = p(f"position:absolute;right:14px;bottom:8px;font-size:18px;color:{GRAY}", "Python")
    bx = f'<div style="flex:1;position:relative;background:#FFFFFF;border:2px solid {LINE};border-radius:10px;padding:8px 18px 8px;display:flex;flex-direction:column">{txt}{tg}</div>'
    o.append(f'<div style="display:flex;flex-direction:row;gap:10px;align-items:stretch">{bar}{gutter}{bx}</div>')
    if c.get("out"):
        col = lambda i, l: RED if (c.get("err") and re.match(r"[A-Za-z]+(Error|Interrupt)", l)) or i in c.get("red", ()) else INK
        o.append("".join(p(f"margin-left:85px;padding:0 20px;font-family:{MONO};font-size:{fs}px;line-height:1.45;white-space:pre;color:{col(i, l)}", e(l) if l else "&#160;") for i, l in enumerate(c["out"])))
    o.append('</div>')
    return o


def hl(left, top, w, i, n=1, kind="run", order=1, tag=None):
    """Tints code lines i..i+n-1 of a cell drawn by cell(c, left, top, w). tag: a word at the right end of the tint."""
    y = top + 10 + i * LH()
    at = f' data-build-in="fade order {order}"' if order else ""
    t = p(f"position:absolute;right:110px;top:0;font-size:22px;font-weight:700;line-height:{LH():.0f}px;color:{HLT[kind]}", e(tag)) if tag else ""
    return f'<div{at} style="position:absolute;left:{left + 87}px;top:{y:.0f}px;width:{w - 89}px;height:{n * LH():.0f}px;background:{HL[kind]};border-radius:6px">{t}</div>'


def ly(top, i):
    """Centre y of code line i in a cell drawn at top."""
    return top + 10 + i * LH() + LH() / 2


def oy(top, n, j):
    """Centre y of output line j in a cell with n code lines."""
    return top + 20 + n * LH() + 10 + j * (LH() + 10) + LH() / 2


def tw(s, fs=None):
    """Rendered width of a code string: Hangul is about one em, the rest 0.6 em."""
    fs = fs or CFS[0]
    return sum(fs * (1.0 if '가' <= ch <= '힣' else 0.6) for ch in s)


def cx(left, s, out=False):
    """x where character s starts in a cell at left (code or output line)."""
    return left + (87 + 18 if not out else 85 + 20) + tw(s)


def tx(left, lines, gap=36, out=False):
    """x just right of the longest of the given lines inside a cell at left."""
    return int(max(cx(left, l, out) for l in lines) + gap)


def tag(x, y, text, color, order=None, size=30, lead=True, anim="fade", w=None):
    """A leader label: '← text' centred on y. No box."""
    at = f' data-build-in="{anim} order {order}"' if order else ""
    ws = f"width:{w}px;white-space:normal;" if w else "white-space:nowrap;"
    return p(f"position:absolute;left:{x:.0f}px;top:{y - size * 0.725:.0f}px;{ws}font-size:{size}px;font-weight:700;line-height:1.45;color:{color}", ("← " if lead else "") + e(text), at)


def fix(left, top, bad, good, order, size=32, w=1728):
    """The wrong line struck through, an arrow, the right line."""
    return (f'<div data-build-in="rise order {order}" style="position:absolute;left:{left}px;top:{top}px;width:{w}px;display:flex;flex-direction:row;align-items:center;gap:22px">'
            + p(f"font-size:{size}px;font-weight:900;color:{RED}", "✕")
            + p(f"font-family:{MONO};font-size:{size}px;font-weight:700;color:{RED};text-decoration:line-through;text-decoration-thickness:3px;white-space:pre", e(bad))
            + arrow(70)
            + p(f"font-size:{size}px;font-weight:900;color:{GR}", "✓")
            + p(f"font-family:{MONO};font-size:{size}px;font-weight:700;color:{INK};background:{GRBG};border:3px solid {GR};border-radius:14px;padding:6px 20px;white-space:pre", e(good)) + '</div>')


def plain_rows(left, top, w, rows, widths, order0=1, rh=76, head_=None, fs=30, mono_cols=(), hi=None, ids=None):
    """A light table: gray header over a dark rule, rows split by thin rules, no boxes.
    hi: (row, color) to give one row a tinted fill. ids: element id per row."""
    o = []
    y = top
    if head_:
        o.append(f'<div data-build-in="fade order {order0}" style="position:absolute;left:{left}px;top:{y}px;width:{w}px;height:50px;display:flex;flex-direction:row;gap:20px;border-bottom:3px solid {INK}">'
                 + "".join(p(f"width:{cw}px;flex:none;font-family:{MONO if (k in mono_cols and c.isascii()) else SANS};font-size:24px;font-weight:700;color:{GRAY};white-space:nowrap", e(c)) for k, (c, cw) in enumerate(zip(head_, widths))) + '</div>')
        y += 58
    for i, r in enumerate(rows):
        cells_ = ""
        for k, (c, cw) in enumerate(zip(r, widths)):
            if c in ("True", "False"):
                cells_ += f'<div style="width:{cw}px;flex:none">{tf(c, fs - 2)}</div>'
            else:
                cells_ += p(f"width:{cw}px;flex:none;font-family:{MONO if k in mono_cols else SANS};font-size:{fs}px;font-weight:700;color:{INK};white-space:pre", e(c))
        idt = f' id="{ids[i]}"' if ids else ""
        o.append(f'<div{idt} data-build-in="rise order {order0 + i}" style="position:absolute;left:{left}px;top:{y + i * rh}px;width:{w}px;height:{rh}px;display:flex;flex-direction:row;align-items:center;gap:20px;border-bottom:2px solid {LINE}">{cells_}</div>')
    return o


# ---------- dark code strips ----------
def seg(parts, size=40):
    """Spans in one line: parts = [(text, color), ...] or (text, color, attrs) for a piece that animates on its own."""
    sp = []
    for pt in parts:
        t, c = pt[0], pt[1]
        a = pt[2] if len(pt) > 2 else ""
        sp.append(f'<span{a} style="display:inline-block;color:{c}">{e(t).replace(" ", "&#160;")}</span>')
    return p(f"font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.5;color:{W_};white-space:pre", "".join(sp))


def strip(left, top, w, h, lines, attrs="", pad=48, center=False):
    jc = "center" if center else "flex-start"
    return (f'<div{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:{DARK};border-radius:22px;padding:0 {pad}px;display:flex;flex-direction:column;justify-content:center;align-items:{jc}">'
            + "".join(lines) + '</div>')


def boxes(items, left, top, w=170, h=90, color=GRAY, bg="#F1F0EC", on=True, fs=32, gap=12, ids=None, attrs=None, struck=()):
    """Values in a row of boxes. ids and attrs: one per box (for fly)."""
    o = []
    for i, it in enumerate(items):
        idt = f' id="{ids[i]}"' if ids else ""
        at = attrs[i] if attrs else ""
        st = i in struck
        o.append(p(f"position:absolute;left:{left + i * (w + gap)}px;top:{top}px;width:{w}px;height:{h}px;border-radius:14px;border:3px {'dashed' if st else 'solid'} {('#C9CED8' if st else color) if on else LINE};"
                   f"background:{CARD if st else (bg if on else CARD)};font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:{h - 6}px;text-align:center;color:{'#B4B9C3' if st else INK};white-space:pre{';text-decoration:line-through' if st else ''}", e(it), idt + at))
    return o


def chip(text, color, bg, fs=32, attrs=""):
    return p(f"display:inline-block;font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:1.2;color:{INK};background:{bg};border:3px solid {color};border-radius:999px;padding:6px 22px;white-space:pre", e(text), attrs)


def lockers(pairs, left, top, w=260, h=170, color=K1, bg=K1BG, attrs="", fs=36, kfs=26, gap=14):
    """A dictionary as lockers: key on the door band, value inside (same picture as chapter 15)."""
    o = [f'<div{attrs} style="position:absolute;left:{left}px;top:{top}px;display:flex;flex-direction:row;gap:{gap}px">']
    for k, v in pairs:
        o.append(f'<div style="width:{w}px;height:{h}px;flex:none;border-radius:14px;border:3px solid {color};background:{bg};display:flex;flex-direction:column;overflow:hidden">'
                 + p(f"height:{kfs + 26}px;flex:none;background:{color};color:#FFFFFF;font-family:{MONO};font-size:{kfs}px;font-weight:700;line-height:{kfs + 26}px;text-align:center;white-space:pre", e(k))
                 + '<div style="flex:1;display:flex;align-items:center;justify-content:center">' + p(f"font-family:{MONO};font-size:{fs}px;font-weight:700;color:{INK};white-space:pre", e(v)) + '</div></div>')
    o.append('</div>')
    return "".join(o)




def fly(order, src, extra=""):
    return f' data-build-in="fly order {order}" data-from="{src}"{extra}'


def fade(order):
    return f' data-build-in="fade order {order}"'


def rise(order):
    return f' data-build-in="rise order {order}"'


def label(x, y, text, color, size=28, attrs="", mono=False):
    return p(f"position:absolute;left:{x:.0f}px;top:{y:.0f}px;font-family:{MONO if mono else SANS};font-size:{size}px;font-weight:700;line-height:1.3;color:{color};white-space:nowrap", e(text), attrs)


def reading(x, y, text, color, order, size=32):
    """One plain line that says how to read an error. No box."""
    return p(f"position:absolute;left:{x}px;top:{y}px;width:1728px;font-size:{size}px;font-weight:700;line-height:1.4;color:{color}", e(text), rise(order))





def cbot(top, n):
    """y just under the code box of a cell with n code lines drawn at top."""
    return top + 20 + n * LH()


def df(tid, left, top, cols, rows, widths, fs=26, rh=46, idx=None, iw=64, attrs="", row_attrs=None, cs=None, head_attrs=""):
    """A DataFrame as VS Code's notebook shows it: bold header and index, right aligned cells, striped rows.
    rows: list of tuples. idx: row labels (default 0..). cs: {(i, j): extra style}. row_attrs: {i: attrs}."""
    idx = idx if idx is not None else list(range(len(rows)))
    W_t = iw + sum(widths) + 24
    o = [f'<div id="{tid}"{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{W_t}px;display:flex;flex-direction:column">']
    hd_ = p(f"width:{iw}px;flex:none", "&#160;") + "".join(p(f"width:{w}px;flex:none;padding-right:12px;text-align:right;font-size:{fs}px;font-weight:700;color:{INK};white-space:nowrap", e(c)) for c, w in zip(cols, widths))
    o.append(f'<div{head_attrs} style="height:{rh}px;display:flex;flex-direction:row;align-items:center;border-bottom:2px solid #BFC4CE">{hd_}</div>')
    for i, r in enumerate(rows):
        bg = TB if i % 2 == 0 else "transparent"
        cells_ = p(f"width:{iw}px;flex:none;padding-right:12px;text-align:right;font-size:{fs}px;font-weight:700;color:{INK}", e(str(idx[i])))
        for j, (v, w) in enumerate(zip(r, widths)):
            extra = (cs or {}).get((i, j), "")
            cells_ += p(f"width:{w}px;flex:none;padding-right:12px;text-align:right;font-size:{fs}px;font-variant-numeric:tabular-nums;color:{INK};white-space:nowrap;{extra}", e(str(v)))
        ra = (row_attrs or {}).get(i, "")
        o.append(f'<div id="{tid}-r{i}"{ra} style="height:{rh}px;display:flex;flex-direction:row;align-items:center;background:{bg}">{cells_}</div>')
    o.append('</div>')
    return "".join(o)


def dfx(left, iw, widths, j):
    """Left x of column j (0 = first data column, -1 = index) in a table drawn at left."""
    return left + (0 if j < 0 else iw + sum(widths[:j]))


def dfy(top, rh, i):
    """Top y of data row i (header is row -1)."""
    return top + rh * (i + 1) + 2


def term(left, top, w, lines, fs=24, attrs="", tid=None):
    """A terminal: ('$', cmd) lines in white after a green $, ('o', text) output lines in gray."""
    idt = f' id="{tid}"' if tid else ""
    o = [f'<div{idt}{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;background:#1E222A;border-radius:18px;padding:26px 34px;display:flex;flex-direction:column">']
    for k, t in lines:
        if k == "$":
            o.append(p(f"font-family:{MONO};font-size:{fs}px;line-height:1.55;white-space:pre;color:#F2F4F8;font-weight:700", f'<span style="color:#7EE2A0">$ </span>{e(t)}'))
        else:
            o.append(p(f"font-family:{MONO};font-size:{fs}px;line-height:1.55;white-space:pre;color:#A7AEBB", e(t) if t else "&#160;"))
    o.append('</div>')
    return "".join(o)


def tline(top, i, fs=24):
    """Centre y of line i in term() drawn at top."""
    return top + 26 + fs * 1.55 * (i + 0.5)


def catchip(c, fs=24, attrs=""):
    col, bg = CATC[c]
    return p(f"display:inline-block;font-size:{fs}px;font-weight:700;color:{col};background:{bg};border-radius:8px;padding:0 10px;white-space:nowrap", e(c), attrs)


def vbox(x, y, w, h, text, color, bg, fs=30, attrs="", dashed=False):
    return p(f"position:absolute;left:{x:.0f}px;top:{y:.0f}px;width:{w}px;height:{h}px;border-radius:12px;border:3px {'dashed' if dashed else 'solid'} {color};background:{bg};"
             f"font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:{h - 6}px;text-align:center;color:{INK};white-space:pre", e(text), attrs)


def tint(order, x, y, w, h, color):
    """A see-through color band over a code token (no border, so it never covers neighbor characters)."""
    c = color.lstrip("#")
    r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
    at = f' data-build-in="fade order {order}"' if order else ""
    return f'<div{at} style="position:absolute;left:{x:.0f}px;top:{y:.0f}px;width:{w:.0f}px;height:{h:.0f}px;border-radius:6px;background:rgba({r},{g},{b},0.18);border-bottom:4px solid {color}"></div>'



# ---------- this deck ----------
NB = "house.ipynb"
TB = "#F4F5F7"   # striped row, like VS Code's notebook table
IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
NEW1 = " 이 셀만 새 노트북에서 실행해서 셀 번호가 [1]부터예요."


def mono(left, top, lines, fs=24, lh=1.4, color=INK, attrs="", w=None, tid=None, weight=400):
    """Plain output text (VS Code prints it under the cell). Line i is centred at top + fs*lh*(i + 0.5)."""
    idt = f' id="{tid}"' if tid else ""
    ws = f"width:{w}px;" if w else ""
    body = "<br>".join(e(l) if l else "&#160;" for l in lines)
    return f'<p{idt}{attrs} style="position:absolute;left:{left}px;top:{top}px;{ws}font-family:{MONO};font-size:{fs}px;font-weight:{weight};line-height:{lh};white-space:pre;color:{color}">{body}</p>'


def my(top, i, fs=24, lh=1.4):
    return top + fs * lh * (i + 0.5)


def png_b64(name):
    """Kernel figures as 256-colour PNGs: the slides look the same and the HTML gets much smaller."""
    import io
    from PIL import Image
    im = Image.open(os.path.join(IMG, name)).convert("RGB").quantize(256, dither=Image.Dither.NONE)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


def img(left, top, w, name, attrs="", tid=None, border=True):
    b = png_b64(name)
    idt = f' id="{tid}"' if tid else ""
    bd = f"border:2px solid {LINE};border-radius:12px;" if border else ""
    return f'<img{idt}{attrs} src="data:image/png;base64,{b}" style="position:absolute;left:{left}px;top:{top}px;width:{w}px;{bd}background:#FFFFFF">'


def bar(x, y, w, h, color, attrs="", r=8):
    return f'<div{attrs} style="position:absolute;left:{x:.0f}px;top:{y:.0f}px;width:{max(w, 0):.0f}px;height:{h:.0f}px;border-radius:{r}px;background:{color}"></div>'


def nan_style():
    return f"color:{RED};font-weight:700;background:{K5BG};border-radius:6px"


import numpy as np

EB1, EB2, EB3, EB4, EB5, EB6 = "1. 왜 필요한가", "2. matplotlib 그림판", "3. 산점도와 상관계수", "4. 연습 데이터 만들기", "5. 오류와 함정", "6. 실제 상황"
IMPORTS = ["import numpy as np", "import pandas as pd", "import matplotlib.pyplot as plt"]
FONTC = ["import platform", "", "os_name = platform.system()", 'if os_name == "Windows":', '    plt.rcParams["font.family"] = "Malgun Gothic"',
         'elif os_name == "Darwin":', '    plt.rcParams["font.family"] = "AppleGothic"']
LINEC = ["fig, ax = plt.subplots(figsize=(6, 5))", "", 'months = ["1월", "2월", "3월", "4월", "5월", "6월"]', "sales = [120, 135, 120, 160, 170, 190]", "",
         'ax.plot(months, sales, marker="o", label="매출")', 'ax.set_title("My Mall 월 매출")', 'ax.set_xlabel("월")', 'ax.set_ylabel("매출(만원)")', "ax.legend()", "plt.show()"]
MAKEC = ["rng = np.random.default_rng(42)", "", "n = 200", "area = rng.uniform(20, 85, n)", "price = area * 450 + 5000 + rng.normal(0, 2500, n).round(-1)", "",
         "special = rng.choice(n, 5, replace=False)", "price[special] += rng.uniform(15000, 25000, 5).round(-1)", "",
         'office = pd.DataFrame({"area": area, "price": price})', "office.describe().round(1)"]
DESC = ["        area    price", "count  200.0    200.0", "mean    52.1  28990.3", "std     18.4   9529.3", "min     20.5   9472.2",
        "25%     36.4  21093.2", "50%     51.1  29281.8", "75%     68.6  36729.6", "max     84.5  65581.6"]
# the deck's own data, made the same way as the notebook (PCG64 gives the same numbers on every machine)
_r = np.random.default_rng(42)
AREA = _r.uniform(20, 85, 200)
NOISE = _r.normal(0, 2500, 200).round(-1)
PRICE = AREA * 450 + 5000 + NOISE
SPECIAL = _r.choice(200, 5, replace=False)
PRICE[SPECIAL] += _r.uniform(15000, 25000, 5).round(-1)
assert list(SPECIAL) == [17, 134, 178, 172, 122]


def strip_code(left, top, w, h, parts, size=40, attrs=""):
    """One dark code line made of pieces: parts = [(text, color, id or None), ...]."""
    sp = []
    for t, c, i in parts:
        idt = f' id="{i}"' if i else ""
        sp.append(f'<span{idt} style="display:inline-block;color:{c}">{e(t).replace(" ", "&#160;")}</span>')
    line = p(f"font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.5;color:{W_};white-space:pre", "".join(sp))
    return strip(left, top, w, h, [line], attrs)


def dots_svg(left, top, w, h, pts, color, r=6, attrs="", opacity=0.55, tid=None):
    """Points in a box: pts are (x, y) between 0 and 1, y up."""
    idt = f' id="{tid}"' if tid else ""
    c = "".join(f'<circle cx="{x * w:.1f}" cy="{(1 - y) * h:.1f}" r="{r}" fill="{color}" fill-opacity="{opacity}"/>' for x, y in pts)
    return f'<svg{idt}{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;overflow:visible" viewBox="0 0 {w} {h}">{c}</svg>'


def frame(left, top, w, h, attrs=""):
    """Thin axes lines (left and bottom) for small drawn charts."""
    return (f'<div{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;border-left:3px solid #9AA0AB;border-bottom:3px solid #9AA0AB"></div>')


def note(x, y, w, text, color=SUB, size=26, attrs=""):
    return p(f"position:absolute;left:{x}px;top:{y}px;width:{w}px;font-size:{size}px;line-height:1.5;color:{color};word-break:keep-all", text, attrs)


# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#F2B27A;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
       f'<h1{SLAM(1)} style="font-size:92px;font-weight:900;line-height:1.12;color:#F6F5F1">그래프 그리기와<br>연습 데이터 만들기</h1>',
       '<p style="font-size:38px;line-height:1.45;color:#BFC6D4">matplotlib으로 그리고,<br>NumPy로 정답을 숨긴 데이터를 만들어요</p>']
cov.append(f'<div id="cov-card" style="position:absolute;left:1080px;top:200px;width:720px;height:540px;background:#FFFFFF;border-radius:24px;overflow:hidden">'
           + f'<img id="cov-img" src="data:image/png;base64,{png_b64("main-3.png")}" style="position:absolute;left:40px;top:58px;width:640px">'
           + '</div>')
cov.append(p(f"position:absolute;left:1080px;top:770px;width:720px;font-size:26px;line-height:1.5;color:#BFC6D4", "오피스텔 시세 200건. 오늘 직접 만드는 데이터예요."))
cov.append(kenburns(2, "cov-img", 1.08, 6000, "60% 40%"))
W("cover", cov, "오늘은 머신러닝 모델을 만들기 전에 꼭 하는 두 가지를 배워요. 데이터를 그래프로 그려서 눈으로 보는 것, 그리고 정답을 알고 있는 연습 데이터를 직접 만드는 것이에요. 그래프는 matplotlib, 연습 데이터는 NumPy의 난수로 만들어요. 오른쪽 그림이 오늘 만들 오피스텔 시세 200건이에요. 이 데이터로 다음 챕터에서 첫 머신러닝 모델을 학습해요.", ("intro", "들어가기"))
ORDER.append("toc")

# ---------- setup ----------
o = [sec("setup")] + head("들어가기", "ml-basics 프로젝트에 datasets 폴더를 만들어요", JP)
TL = [("$", "cd ml-basics"), ("$", "mkdir datasets"), ("o", ""), ("$", "ls datasets"), ("o", "usa_housing.csv")]
o.append(term(96, 214, 860, TL, 32, tid="t-setup"))
LHt = 32 * 1.55
o.append(box(1, 96 + 34 - 10, 214 + 26 + 4 * LHt - 4, 32 * 0.6 * 15 + 20, LHt + 8, "#F2C46D", 4, 10))
o.append(note(96, 214 + 52 + 5 * LHt + 30, 860, "usa_housing.csv는 이 챕터 폴더의 datasets에서 받아<br>ml-basics/datasets에 넣어요. 수업 데이터 300채예요.", SUB, 26, fade(1)))
o.append(note(96, 214 + 52 + 5 * LHt + 150, 860, "matplotlib은 46에서 넣었어요. 46을 건너뛰었다면 먼저<br>" + f'<span style="font-family:{MONO};font-size:24px;font-weight:700;color:{INK}">uv add matplotlib</span>', SUB, 26))
TX = 1110
tree = [("ml-basics/", INK, 0, True), ("datasets/", K1, 1, True), ("usa_housing.csv", INK, 2, False), ("office.csv", GRAY, 2, False), (NB, JP, 1, False), ("pyproject.toml", GRAY, 1, False), (".venv/", GRAY, 1, True)]
o.append(label(TX, 214, "폴더 모양", INK, 30))
for i, (n_, c_, d, folder) in enumerate(tree):
    y = 290 + i * 80
    at = rise(2) + DELAY(i * 60) if i else ""
    o.append(p(f"position:absolute;left:{TX + d * 56}px;top:{y}px;font-family:{MONO};font-size:32px;font-weight:700;line-height:64px;color:{c_};white-space:nowrap", ("▸ " if folder else "") + e(n_), at))
o.append(tag(TX + 2 * 56 + 32 * 0.6 * 10 + 60, 290 + 3 * 80 + 32, "4파트에서 만들어요", GRAY, 2, 26))
o.append(tag(TX + 56 + 32 * 0.6 * 11 + 50, 290 + 4 * 80 + 32, "오늘 노트북", JP, 2, 26))
o.append(caption("노트북 커널은 .venv를 골라요(10). 패키지는 uv add로만 넣어요.", 920, 3))
W("setup", o, "45와 46에서 쓴 ml-basics 프로젝트를 이어서 써요. 터미널에서 ml-basics 폴더로 들어가 datasets 폴더를 만들어요. 수업에서 받은 usa_housing.csv를 이 폴더에 넣어요. 파일은 이 챕터 폴더의 datasets에도 있어요. 오른쪽은 폴더 모양이에요. VS Code에서 ml-basics 폴더를 열고 house.ipynb를 만든 뒤 커널은 .venv로 골라요. office.csv는 4파트에서 노트북이 직접 만들어요." + REAL)

# ---------- part 1 ----------
o = [sec("why")] + head(EB1, "표 200줄로는 안 보이던 규칙이 점으로 찍으면 보여요", K1)
CFS[0] = 26
OH = [("70.307143", "38248.214420"), ("48.527099", "25847.194363"), ("75.808865", "39103.989157"), ("65.328922", "33988.014850"), ("26.121528", "17594.687426")]
o.append(label(96, 210, "office.head()", GRAY, 26, "", True))
o.append(df("why-df", 96, 260, ["area", "price"], OH, [200, 260], fs=30, rh=70, iw=50))
o.append(p(f"position:absolute;left:96px;top:{260 + 70 * 6 + 10}px;width:560px;font-family:{MONO};font-size:30px;color:{GRAY}", "⋮  (200줄)"))
o.append(note(96, 820, 700, "면적(㎡)과 가격(만 원)이에요.<br>숫자만 보면 규칙이 잘 안 보여요.", SUB, 26))
IW = 1000
o.append(img(824, 196, IW, "main-3.png", rise(1), "why-img"))
SC = IW / 1423
o.append(f'<x-shape{WIPE(2)} kind="arrow-right" style="position:absolute;left:{824 + 330 * SC:.0f}px;top:{196 + 840 * SC:.0f}px;width:{1000 * SC:.0f}px;height:30px;background:{K1};transform:rotate(-17.5deg);transform-origin:left center"></x-shape>')
o.append(tag(824 + 900 * SC, 196 + 760 * SC, "넓을수록 비싸요", K1, 2, 30, lead=False))
o.append(caption("머신러닝은 먼저 그려 보고 규칙이 있는지 확인하는 데서 시작해요.", 930, 3))
W("why", o, "왼쪽은 오늘 만들 오피스텔 데이터의 앞 다섯 줄이에요. 면적과 가격이 200줄 있어요. 숫자만 봐서는 넓을수록 비싼지 한눈에 알기 어려워요. 같은 200줄을 점으로 찍으면 오른쪽처럼 점들이 오른쪽 위로 올라가요. 머신러닝 모델은 이런 규칙을 찾는 프로그램이에요. 그래서 모델에 넣기 전에 먼저 그려서 규칙이 있는지 봐요." + REAL, ("p1", "왜 필요한가"))

o = [sec("big")] + head(EB1, "47은 그래프와 연습 데이터, 48은 학습과 채점이에요", K1)
ST5 = [("표 준비", "pandas", "45, 46", K1, True), ("그래프로 보기", "matplotlib", "47", K2, True), ("연습 데이터", "NumPy 난수", "47", K4, True), ("학습하고 예측", "scikit-learn", "48", GRAY, False), ("채점", "scikit-learn", "48", GRAY, False)]
BW, GAP_, Y0 = 280, 77, 300
BH5 = 430
for i, (h_, lib, ch, c_, on) in enumerate(ST5):
    x = 96 + i * (BW + GAP_)
    bg = "#FFFFFF" if on else "#F1F0EC"
    bd = f"3px solid {c_}" if on else "3px dashed #C9CED8"
    o.append(f'<div data-build-in="rise order {1 if i < 3 else 2}"{DELAY((i % 3) * 120)} style="position:absolute;left:{x}px;top:{Y0}px;width:{BW}px;height:{BH5}px;border-radius:18px;border:{bd};background:{bg};display:flex;flex-direction:column;align-items:center;justify-content:center;gap:26px">'
             + num(i + 1, c_, 48) + p(f"font-size:36px;font-weight:700;color:{INK if on else GRAY}", e(h_))
             + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{c_}", e(lib)) + '</div>')
    o.append(p(f"position:absolute;left:{x}px;top:{Y0 + BH5 + 24}px;width:{BW}px;text-align:center;font-size:28px;font-weight:700;color:{c_ if on else GRAY}", f"{ch}", fade(1 if i < 3 else 2)))
    if i < 4:
        o.append(arrow(GAP_ - 24, "#C9CED8", WIPE(1 if i < 2 else 2), f"position:absolute;left:{x + BW + 12}px;top:{Y0 + BH5 / 2 - 15:.0f}px"))
o.append(f'<div data-build-in="fade order 3" style="position:absolute;left:{96 + BW + GAP_ - 20}px;top:{Y0 - 30}px;width:{2 * BW + GAP_ + 40}px;height:{BH5 + 110}px;border-radius:26px;border:4px solid {K2};"></div>')
o.append(label(96 + BW + GAP_ - 20, Y0 - 76, "오늘", K2, 30, fade(3)))
o.append(caption("4파트에서 만든 데이터가 48의 연습 문제가 돼요.", 920, 4))
W("big", o, "머신러닝 기초 수업은 다섯 단계로 흘러가요. 45와 46에서 pandas로 표를 준비했어요. 오늘 47에서는 그 표를 matplotlib으로 그려 보고, NumPy 난수로 연습 데이터를 만들어요. 48에서는 scikit-learn으로 모델을 학습하고 예측한 뒤 얼마나 맞혔는지 채점해요. 오늘 만드는 데이터는 정답을 알고 만들기 때문에 48에서 모델이 정답을 잘 찾았는지 확인할 수 있어요.")

o = [sec("libs")] + head(EB1, "오늘 쓰는 도구 셋: 표는 pandas, 그림은 matplotlib, 난수는 NumPy", K1)
LIB = [("import pandas as pd", "pd", "표를 읽고 쓰고 골라요", "엑셀 표", "45", K1),
       ("import matplotlib.pyplot as plt", "plt", "그래프를 그려요", "그림판", "새로", K2),
       ("import numpy as np", "np", "숫자 배열 계산, 난수 만들기", "주사위", "45", K4)]
o += plain_rows(96, 220, 1728, [(a, b, c, d) for a, b, c, d, _, _ in LIB], [700, 150, 560, 240], 1, 130, ["불러오는 줄", "별명", "하는 일", "비유"], 32, mono_cols=(0, 1))
o.append(f'<div data-build-in="rise order 4" style="position:absolute;left:96px;top:{220 + 58 + 3 * 130 + 50}px;width:1728px;height:230px;display:flex;flex-direction:row;align-items:center;gap:40px">'
         + f'<div style="width:560px;height:200px;flex:none;border-radius:18px;border:3px solid {K2};background:{K2BG};position:relative">'
         + p(f"position:absolute;left:24px;top:14px;font-family:{MONO};font-size:28px;font-weight:700;color:{K2}", "matplotlib")
         + p(f"position:absolute;left:24px;top:56px;font-size:22px;color:{SUB}", "패키지 (uv add 이름)")
         + f'<div style="position:absolute;left:250px;top:60px;width:270px;height:110px;border-radius:12px;border:3px solid {K2};background:#FFFFFF;display:flex;flex-direction:column;align-items:center;justify-content:center">'
         + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{INK}", "pyplot") + p(f"font-size:22px;color:{SUB}", "그리는 명령 모음") + '</div></div>'
         + p(f"flex:1;font-size:30px;line-height:1.55;color:{INK}", "matplotlib.pyplot은 matplotlib 안의 pyplot 모듈이에요.<br>28의 import 모듈 as 별명처럼 plt라고 줄여 불러요.<br>"
             + f'<span style="color:{GRAY}">np, pd, plt는 세계 어디서나 쓰는 약속이에요.</span>') + '</div>')
W("libs", o, "오늘은 도구 세 개를 같이 써요. pandas는 45에서 배운 표 도구예요. NumPy는 숫자 배열 도구인데, 오늘은 그 안의 난수 기능으로 연습 데이터를 만들어요. matplotlib은 그래프 도구예요. 정확히는 matplotlib 패키지 안의 pyplot 모듈을 불러와 plt라고 불러요. 점은 패키지 안의 모듈을 가리켜요. 28에서 배운 import 모듈 as 별명과 같아요. np, pd, plt는 다른 사람 코드에서도 똑같이 쓰는 별명이라 그대로 쓰는 게 좋아요.")

o = [sec("min")] + head(EB1, "가장 짧은 그래프: x 리스트와 y 리스트를 plt.plot에 넣어요", K1)
CFS[0] = 28
MN = ['months = ["1월", "2월", "3월", "4월", "5월", "6월"]', "sales = [120, 135, 120, 160, 170, 190]", "", "plt.plot(months, sales)", "plt.show()"]
o += cell({"id": "c-min", "lines": MN, "n": 3}, 96, 200, 950, sel="c-min")
o.append(tint(1, cx(96, "plt.plot(") - 4, ly(200, 3) - LH() / 2, tw("months") + 8, LH(), K1))
o.append(tint(1, cx(96, "plt.plot(months, ") - 4, ly(200, 3) - LH() / 2, tw("sales") + 8, LH(), K4))
o.append(tag(cx(96, MN[3]) + 40, ly(200, 3), "가로(x), 세로(y) 순서", INK, 1, 26))
o.append(tag(cx(96, MN[4]) + 40, ly(200, 4), "셀 아래에 그림을 보여 줘요", GRAY, 2, 26))
MW = 760
o.append(img(1080, 196, 744, "min-1.png", rise(2), "min-img"))
o.append(note(96 + 105, cbot(200, 5) + 50, 860, "months 6개와 sales 6개가 같은 자리끼리 짝이 돼요.<br>1월은 120, 2월은 135, … 6월은 190이에요.", INK, 28, fade(3)))
o.append(note(96 + 105, cbot(200, 5) + 170, 860, "plt는 다음 장 셀 [1]에서 불러오는 matplotlib.pyplot이에요.", GRAY, 24, fade(3)))
W("min", o, "가장 짧은 그래프부터 그려 봐요. 가로축에 놓을 값 리스트와 세로축에 놓을 값 리스트를 plt.plot에 차례로 넣어요. 순서가 중요해요. 앞이 가로 x, 뒤가 세로 y예요. 두 리스트는 같은 자리끼리 짝이 돼서 1월에 120, 2월에 135 자리에 점을 찍고 선으로 이어요. plt.show는 다 그린 그림을 셀 아래에 보여 줘요. 다음 파트에서 제목과 축 이름, 점 모양을 하나씩 붙여요." + NEW1 + REAL)

# ---------- part 2 ----------
o = [sec("cells12")] + head(EB2, "노트북 맨 위 두 셀: 불러오기와 한글 글꼴", K2)
CFS[0] = 26
o += cell({"id": "c-imp", "lines": IMPORTS, "n": 1}, 96, 200, 980)
o += cell({"id": "c-font", "lines": FONTC, "n": 2}, 96, cbot(200, 3) + 40, 980, sel="c-font")
FT = cbot(200, 3) + 40
o.append(tag(cx(96, FONTC[2]) + 30, ly(FT, 2), "운영체제 이름", K2, 1, 26))
RX = 1150
o.append(label(RX, 220, "platform.system()이 돌려주는 값", INK, 28, rise(1)))
for i, (a, b) in enumerate([('"Windows"', "Windows"), ('"Darwin"', "Mac"), ('"Linux"', "리눅스")]):
    o.append(p(f"position:absolute;left:{RX}px;top:{280 + i * 70}px;width:300px;font-family:{MONO};font-size:30px;font-weight:700;line-height:60px;color:{INK}", e(a), rise(1) + DELAY(i * 80)))
    o.append(p(f"position:absolute;left:{RX + 320}px;top:{280 + i * 70}px;font-size:28px;line-height:60px;color:{SUB}", e(b), rise(1) + DELAY(i * 80)))
o.append(label(RX, 540, 'plt.rcParams["font.family"]', K2, 28, rise(2), True))
o.append(note(RX, 590, 680, "rcParams는 그래프 설정이 든 딕셔너리예요(15).<br>font.family 키에 글꼴 이름을 넣으면<br>이 노트북의 모든 그래프에 한글이 나와요.", INK, 28, rise(2)))
o.append(note(RX, 790, 680, "Windows는 맑은 고딕, Mac은 AppleGothic이에요.", GRAY, 26, rise(2)))
o.append(lspot(1, 96 + 87, FT, 980 - 87, 10 + 7 * LH() + 8, FT + 10 + 2 * LH(), LH(), bar=K2))
o.append(lspot(2, 96 + 87, FT, 980 - 87, 10 + 7 * LH() + 8, FT + 10 + 3 * LH(), 4 * LH(), bar=K2))
o.append(lspot_off(3))
W("cells12", o, "노트북 맨 위에 두 셀을 먼저 실행해요. 첫 셀은 세 도구를 불러와요. 둘째 셀은 46에서 본 한글 글꼴 설정이에요. platform.system은 지금 컴퓨터의 운영체제 이름을 글자로 돌려줘요. Windows면 Windows, Mac이면 Darwin이에요. plt.rcParams는 matplotlib의 설정 딕셔너리라서 font.family 키에 글꼴 이름을 넣으면 그 뒤 그래프에 한글이 나와요. 이 셀을 빼면 한글이 네모로 깨져요. 5파트에서 그 화면을 봐요.")

o = [sec("anatomy")] + head(EB2, "그래프 한 장은 그림판 fig와 그래프 칸 ax로 되어 있어요", K2)
AW = 760
AS = AW / 1079
AL, AT = 96, 190
o.append(img(AL, AT, AW, "main-1.png", "", "an-img"))
PARTS = [("제목", "ax.set_title()", (470, 15, 250, 45), K2), ("범례", "ax.legend()", (140, 78, 160, 54), K4), ("y축 이름", "ax.set_ylabel()", (12, 380, 40, 140), K1),
         ("x축 이름", "ax.set_xlabel()", (565, 885, 60, 45), K1), ("점 (marker)", 'marker="o"', (995, 78, 44, 44), K3), ("ax: 그래프 칸", "plt.subplots()", (128, 63, 932, 770), GRAY)]
LX = 1000
for i, (nm, code, (x, y, w, h), c_) in enumerate(PARTS):
    order = i // 2 + 1
    o.append(box(order, AL + x * AS - 4, AT + y * AS - 4, w * AS + 8, h * AS + 8, c_, 4, 8))
    yy = 230 + i * 110
    o.append(f'<div data-build-in="rise order {order}" style="position:absolute;left:{LX}px;top:{yy}px;width:824px;height:90px;display:flex;flex-direction:row;align-items:center;gap:22px;border-bottom:2px solid {LINE}">'
             + f'<div style="width:20px;height:20px;flex:none;border-radius:4px;background:{c_}"></div>'
             + p(f"width:260px;flex:none;font-size:32px;font-weight:700;color:{INK}", e(nm))
             + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{c_}", e(code)) + '</div>')
o.append(note(LX, 230 + 6 * 110 + 10, 824, "fig는 바깥 그림 전체예요. 크기를 정하고 저장할 때 써요.", GRAY, 26, fade(3)))
W("anatomy", o, "앞 장 그래프에 이름을 다 붙이면 이 모양이 돼요. 바깥 흰 종이 전체가 그림판 fig이고, 테두리 안 칸이 그래프 칸 ax예요. 그래프 칸에 선과 점을 그리고, 위에 제목, 아래와 왼쪽에 축 이름, 구석에 범례를 붙여요. 오른쪽 표는 각 부분을 만드는 코드예요. ax로 시작하는 명령은 모두 그래프 칸에 그려요. 다음 장부터 코드 한 줄씩 봐요." + REAL)

o = [sec("subplots")] + head(EB2, "plt.subplots는 fig와 ax 두 개를 돌려줘요", K2)
o.append(strip_code(96, 200, 1728, 130, [("fig, ax", "#F2C46D", "sp-left"), (" = plt.subplots(", W_, None), ("figsize=(6, 5)", CV, "sp-size"), (")", W_, None)], 44))
o.append(tag(160, 380, "19의 x, y = 함수()처럼 두 개를 받아요", "#B26A00", 1, 28, lead=False))
o.append(tag(1020, 380, "(가로, 세로) 크기. 단위는 인치예요", GR, 2, 28, lead=False))
S_ = 64
for k, (w_, h_, t_, x0) in enumerate([(6, 5, "(6, 5) 선 그래프", 96), (8, 5, "(8, 5) 오피스텔 산점도", 620), (6, 3, "(6, 3) 미국 집값 산점도", 1300)]):
    y0 = 480
    o.append(f'<div data-build-in="rise order 3"{DELAY(k * 120)} style="position:absolute;left:{x0}px;top:{y0}px;width:{w_ * S_}px;height:{h_ * S_}px;border-radius:8px;border:3px solid {K2 if k == 0 else "#C9CED8"};background:#FFFFFF">'
             + f'<div style="position:absolute;left:12%;top:10%;width:80%;height:76%;border:2px dashed {"#9AA0AB"}"></div></div>')
    o.append(p(f"position:absolute;left:{x0}px;top:{y0 + h_ * S_ + 16}px;width:{w_ * S_ + 60}px;font-family:{MONO};font-size:26px;font-weight:700;color:{K2 if k == 0 else GRAY};white-space:nowrap", e(t_), rise(3) + DELAY(k * 120)))
o.append(note(96, 930, 1728, "바깥 실선이 fig, 안쪽 점선이 ax예요. 1인치가 100픽셀이라 (6, 5)는 600×500 그림이에요.", INK, 30, fade(4)))
W("subplots", o, "plt.subplots는 그림판 fig와 그래프 칸 ax를 한 번에 만들어 두 개를 돌려줘요. 19에서 배운 x, y = 함수()처럼 왼쪽에 이름 두 개를 적어 받아요. figsize는 그림 크기예요. 괄호 안 앞이 가로, 뒤가 세로이고 단위는 인치예요. 노트북은 1인치를 100픽셀로 그려서 (6, 5)는 가로 600, 세로 500 픽셀이에요. 수업 셀 출력의 Figure size 600x500이 이 숫자예요. 수업에서는 선 그래프에 (6, 5), 오피스텔 산점도에 (8, 5), 미국 집값에 (6, 3)을 썼어요. 크기는 보기 좋게 고르면 돼요.")

o = [sec("plot")] + head(EB2, "ax.plot(x, y, marker, label): 자리마다 하는 일이 달라요", K2)
o.append(strip_code(96, 200, 1728, 130, [("ax.plot(", W_, None), ("months", "#9DC3F2", None), (", ", W_, None), ("sales", "#F2A7CF", None), (", ", W_, None), ('marker="o"', CF, None), (", ", W_, None), ('label="매출"', "#F2C46D", None), (")", W_, None)], 44))
ARG = [("months", "가로 x에 놓을 값", K1, "1월 … 6월"), ("sales", "세로 y에 놓을 값", K4, "120 … 190"), ('marker="o"', "점 모양", K3, ""), ('label="매출"', "범례에 쓸 이름", K2, "legend()가 있어야 보여요")]
for i, (a, b, c_, d) in enumerate(ARG):
    y = 380 + i * 110
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:96px;top:{y}px;width:1000px;height:96px;display:flex;flex-direction:row;align-items:center;gap:24px;border-bottom:2px solid {LINE}">'
             + p(f"width:300px;flex:none;font-family:{MONO};font-size:32px;font-weight:700;color:{c_}", e(a)) + p(f"width:300px;flex:none;font-size:30px;font-weight:700;color:{INK}", e(b))
             + p(f"font-size:26px;color:{GRAY}", e(d)) + '</div>')
# marker samples
MKX = 1180
o.append(label(MKX, 380, "marker에 넣는 글자", K3, 28, rise(3)))
MK = [('"o"', "circle"), ('"s"', "square"), ('"^"', "tri"), ('"x"', "x")]
for k, (t_, kind) in enumerate(MK):
    x = MKX + k * 160
    shp = {"circle": f'<div style="width:40px;height:40px;border-radius:50%;background:{K3}"></div>',
           "square": f'<div style="width:38px;height:38px;background:{K3}"></div>',
           "tri": f'<div style="width:0;height:0;border-left:24px solid transparent;border-right:24px solid transparent;border-bottom:42px solid {K3}"></div>',
           "x": f'<p style="font-size:52px;font-weight:900;line-height:42px;color:{K3}">✕</p>'}[kind]
    o.append(f'<div data-build-in="rise order 3"{DELAY(k * 80)} style="position:absolute;left:{x}px;top:440px;width:130px;height:130px;border-radius:14px;border:2px solid {LINE};background:#FFFFFF;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px">{shp}'
             + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{INK}", e(t_)) + '</div>')
o.append(note(MKX, 600, 640, "marker를 안 적으면 점 없이 선만 그려요(앞 파트의 가장 짧은 그래프).", GRAY, 24, rise(3)))
o.append(note(96, 850, 1728, "앞 두 자리는 이름 없이 순서로, 뒤 두 자리는 이름=값으로 넣어요(20의 키워드 인자). 그래서 marker와 label은 순서를 바꿔 적어도 돼요.", INK, 28, fade(5)))
W("plot", o, "ax.plot의 괄호 안 네 자리를 하나씩 봐요. 첫째 자리는 가로축에 놓을 값, 둘째 자리는 세로축에 놓을 값이에요. 이 둘은 이름 없이 순서로 넣어서 바꾸면 그래프가 옆으로 눕어요. marker는 점 모양이에요. 동그라미 o, 네모 s, 세모 ^, 엑스 x 같은 글자를 넣어요. label은 이 선의 이름이에요. 범례에 쓰려고 미리 붙여 두는 이름이라 legend를 부르기 전에는 화면에 안 나와요. 뒤 두 자리는 20에서 배운 키워드 인자라서 서로 순서를 바꿔도 돼요.")

o = [sec("legend")] + head(EB2, "set_으로 이름을 붙이고, legend()로 범례를 켜요", K2)
CFS[0] = 28
LG = ['ax.set_title("My Mall 월 매출")', 'ax.set_xlabel("월")', 'ax.set_ylabel("매출(만원)")', "ax.legend()", "plt.show()"]
o += cell({"id": "c-lg", "lines": LG, "n": 3}, 96, 210, 860, sel="c-lg")
for i, (t_, c_) in enumerate([("그래프 위 제목", K2), ("가로축 아래 이름", K1), ("세로축 왼쪽 이름", K1), ("label을 모아 범례 상자로", K4)]):
    o.append(tag(cx(96, LG[i]) + 30, ly(210, i), t_, c_, 1 if i < 3 else 2, 24))
IW2, IY2 = 520, 480
o.append(img(96, IY2, IW2, "nolegend-1.png", rise(3), "lg-no"))
o.append(img(676, IY2, IW2, "main-1.png", rise(3), "lg-yes"))
o.append(p(f"position:absolute;left:96px;top:{IY2 + IW2 * 941 / 1079 + 14:.0f}px;width:{IW2}px;text-align:center;font-family:{MONO};font-size:26px;font-weight:700;color:{GRAY}", "legend() 없음", rise(3)))
o.append(p(f"position:absolute;left:676px;top:{IY2 + IW2 * 941 / 1079 + 14:.0f}px;width:{IW2}px;text-align:center;font-family:{MONO};font-size:26px;font-weight:700;color:{K4}", "legend() 있음", rise(3)))
LS = IW2 / 1079
o.append(ring(4, 676 + 135 * LS, IY2 + 70 * LS, 175 * LS, 70 * LS, K4, 5))
o.append(note(1270, IY2 + 20, 554, "label을 적었는데 범례가 없다면 legend()를 빠뜨린 거예요.", INK, 32, fade(5)))
o.append(note(1270, IY2 + 200, 554, "set_은 '정하다'라는 뜻이에요. 넣는 글자는 큰따옴표 안에 적어요.", GRAY, 26, fade(1)))
W("legend", o, "그래프 칸 ax에 이름을 붙이는 명령은 set_으로 시작해요. set_title은 위 제목, set_xlabel은 가로축 이름, set_ylabel은 세로축 이름이에요. 넣는 값은 화면에 보일 글자라서 큰따옴표로 감싸요. legend는 앞에서 붙인 label들을 모아 범례 상자를 그려요. 아래 두 그림은 legend 한 줄만 다른 셀의 결과예요. label을 적어도 legend를 부르지 않으면 범례가 안 나와요. 선이 하나일 때는 범례를 빼도 되지만, 6파트처럼 선이 둘 이상이면 꼭 켜요." + REAL)

o = [sec("styles")] + head(EB2, "plt.으로 바로 그리기와 ax.로 그리기, 두 방식은 결과가 같아요", K2)
STY = [("plt.figure(figsize=(8, 5))", "fig, ax = plt.subplots(figsize=(8, 5))"), ("plt.scatter(x, y)", "ax.scatter(x, y)"), ("plt.plot(x, y)", "ax.plot(x, y)"),
       ('plt.title("제목")', 'ax.set_title("제목")'), ('plt.xlabel("면적")', 'ax.set_xlabel("면적")'), ("plt.legend()", "ax.legend()"), ("plt.show()", "plt.show()")]
o += plain_rows(96, 210, 1728, STY, [760, 940], 1, 92, ["plt.로 바로 (3파트 산점도)", "ax.로 (2파트 선 그래프)"], 32, mono_cols=(0, 1))
for i in (3, 4):
    o.append(tint(2, 96 + 780 + tw("ax.", 32) - 2, 210 + 58 + i * 92 + 22, tw("set_", 32) + 4, 48, K2))
o.append(caption("이름이 달라지는 건 제목과 축 이름의 set_뿐이에요. 한 셀 안에서는 한 방식만 써요.", 940, 3))
W("styles", o, "수업에서는 두 방식을 섞어 썼어요. 선 그래프는 fig, ax = plt.subplots로 칸을 받아 ax.plot처럼 그렸고, 3파트 산점도는 plt.figure로 그림판만 만들고 plt.scatter처럼 바로 그렸어요. plt.으로 바로 그리면 matplotlib이 지금 그리고 있는 칸에 알아서 그려 줘요. 결과는 같아요. 다른 점은 제목과 축 이름이에요. plt.title, plt.xlabel이 ax에서는 set_title, set_xlabel이 돼요. 한 셀 안에서 두 방식을 섞으면 읽기 어려우니 하나로 맞춰요.")

# ---------- part 3 ----------
o = [sec("readcsv")] + head(EB3, "pd.read_csv로 미국 집값 300채를 불러와요", K3)
CFS[0] = 28
RC = ['house = pd.read_csv("datasets/usa_housing.csv")', "print(house.shape)", "house.head()"]
o += cell({"id": "c-rc", "lines": RC, "n": 4, "out": ["(300, 10)"]}, 96, 196, 1728, sel="c-rc")
o.append(underline(1, cx(96, "house = pd.read_csv(\""), cx(96, 'house = pd.read_csv("datasets/usa_housing.csv'), ly(196, 0) + LH() / 2 - 4, K3, 5))
o.append(tag(cx(96, RC[0]) + 30, ly(196, 0), "노트북 옆 datasets 폴더의 파일", K3, 1, 26))
o.append(tag(cx(96, "(300, 10)", True) + 30, oy(196, 3, 0), "300채, 열 10개", GR, 2, 26))
HT = oy(196, 3, 0) + 50
HC = ["Price", "Bedrooms", "Bathrooms", "SquareFeet", "YearBuilt", "CrimeRate", "SchoolRating"]
HR = [(221958, 1, 1.9, 4827, 1979, 48.60, 5), (771155, 2, 2.0, 1035, 1987, 92.03, 9), (231932, 1, 3.0, 2769, 1982, 52.08, 3), (465838, 3, 3.3, 2708, 1907, 61.65, 1), (359178, 4, 3.4, 1175, 1994, 15.66, 4)]
HW = [170, 170, 180, 190, 170, 170, 200]
cs = {(i, j): f"color:{K3};font-weight:700" for i in range(5) for j in (0, 3)}
o.append(df("rc-df", 96 + 85, HT, HC, [tuple(f"{v:.2f}" if j == 5 else str(v) for j, v in enumerate(r)) for r in HR], HW, fs=26, rh=54, iw=40, cs=cs, attrs=rise(3)))
MEAN = [("Price", "가격"), ("Bedrooms", "침실 수"), ("Bathrooms", "욕실 수"), ("SquareFeet", "면적"), ("YearBuilt", "지은 해"), ("CrimeRate", "범죄율"), ("SchoolRating", "학교 평점")]
o.append(note(96 + 85, HT + 54 * 6 + 20, 1640, "열 10개 중 7개만 옮겼어요.<br>" + ", ".join(f'<span style="font-family:{MONO};font-weight:700">{a}</span> {b}' for a, b in MEAN), SUB, 24, rise(3)))
W("readcsv", o, "산점도 연습에는 수업에서 받은 미국 집값 데이터를 써요. pd.read_csv에 파일 경로를 넣으면 표로 불러와요. 경로 datasets/usa_housing.csv는 노트북이 있는 폴더 안의 datasets 폴더 속 파일이라는 뜻이에요. shape를 찍어 보면 300채, 열 10개예요. 오늘은 가격 Price와 면적 SquareFeet 두 열을 주로 봐요. 면적 단위는 제곱피트예요. 경로를 틀리면 나는 오류는 5파트에서 봐요." + REAL)

o = [sec("scatter")] + head(EB3, "plt.scatter는 행마다 점 하나를 찍어요. alpha는 점의 투명도예요", K3)
o.append(strip_code(96, 196, 1728, 120, [("plt.scatter(", W_, None), ('house["SquareFeet"]', "#9DC3F2", None), (", ", W_, None), ('house["Price"]', "#F2A7CF", None), (", ", W_, None), ("alpha=0.4", CV, None), (", ", W_, None), ('label="전체 300채"', "#F2C46D", None), (")", W_, None)], 34))
o.append(label(96, 360, "0번 행 하나가 점 하나가 돼요", INK, 30, rise(1)))
o.append(df("sc-df", 96, 420, ["Price", "SquareFeet"], [("221958", "4827")], [200, 220], fs=30, rh=64, iw=40, cs={(0, 0): f"color:{K4};font-weight:700", (0, 1): f"color:{K1};font-weight:700"}, attrs=rise(1)))
o.append(frame(640, 380, 360, 230, rise(1)))
o.append(dots_svg(640, 380, 360, 230, [(0.92, 0.18)], K3, 12, rise(1), 0.9))
o.append(label(640 + 360 * 0.92 - 190, 380 + 230 * 0.82 - 56, "(4827, 221958)", K3, 22, rise(1), True))
o.append(label(640 + 130, 630, "x: SquareFeet", K1, 24, rise(1), True))
o.append(label(660, 384, "y: Price", K4, 24, rise(1), True))
o.append(label(1180, 360, "alpha: 0이면 투명, 1이면 진하게", INK, 30, rise(2)))
for k, (a_, x0) in enumerate([(1.0, 1180), (0.4, 1520)]):
    pts = [(0.3, 0.5), (0.45, 0.55), (0.55, 0.45), (0.5, 0.62), (0.4, 0.4)]
    o.append(f'<div data-build-in="rise order 2"{DELAY(k * 150)} style="position:absolute;left:{x0}px;top:420px;width:300px;height:230px;border-radius:14px;border:2px solid {LINE};background:#FFFFFF"></div>')
    o.append(dots_svg(x0, 420, 300, 230, pts, BL, 34, rise(2) + DELAY(k * 150), a_))
    o.append(p(f"position:absolute;left:{x0}px;top:664px;width:300px;text-align:center;font-family:{MONO};font-size:28px;font-weight:700;color:{INK}", f"alpha={a_:g}", rise(2) + DELAY(k * 150)))
o.append(note(96, 760, 1728, "점이 300개라 겹치는 곳이 많아요. alpha=0.4로 흐리게 하면 겹친 곳이 진해져서 몰린 곳이 보여요.<br>label은 앞 파트처럼 범례에 쓸 이름이에요.", INK, 30, fade(3)))
W("scatter", o, "산점도는 표의 한 행을 점 하나로 찍는 그래프예요. plt.scatter의 첫째 자리가 가로 x, 둘째 자리가 세로 y인 건 plot과 같아요. 0번 집은 면적 4827, 가격 221958이라서 그 자리에 점 하나가 찍혀요. 300행이면 점이 300개예요. alpha는 점의 투명도예요. 0이면 안 보이고 1이면 진해요. 점이 많이 겹칠 때 0.4쯤으로 흐리게 하면 겹친 곳이 진해져서 점이 몰린 곳을 알 수 있어요. plot과 달리 점을 선으로 잇지 않아요.")

o = [sec("scatter2")] + head(EB3, "같은 그림에 scatter를 두 번 부르면 위에 겹쳐 찍어요", K3)
CFS[0] = 24
S2 = ['small = house[(house["YearBuilt"] > 2015) & (house["CrimeRate"] < 45)]', "small.shape"]
o += cell({"id": "c-sm", "lines": S2, "n": 5, "out": ["(10, 10)"]}, 96, 196, 1040)
o.append(tag(cx(96, "(10, 10)", True) + 30, oy(196, 2, 0), "2015년 뒤에 짓고 범죄율 45 미만: 10채", GR, 1, 24))
SC2 = ["plt.figure(figsize=(6, 3))", 'plt.scatter(house["SquareFeet"], house["Price"],', '            alpha=0.4, label="전체 300채")',
       'plt.scatter(small["SquareFeet"], small["Price"],', '            alpha=0.4, color="red", s=50, label="2015 이후 건축")', 'plt.xlabel("면적")', 'plt.ylabel("가격")', "plt.legend()", "plt.show()"]
T2 = oy(196, 2, 0) + 60
o += cell({"id": "c-s2", "lines": SC2, "n": 6}, 96, T2, 1040, sel="c-s2")
o.append(tint(2, cx(96, '            alpha=0.4, ') - 4, ly(T2, 4) - LH() / 2, tw('color="red"') + 8, LH(), RED))
o.append(tint(3, cx(96, '            alpha=0.4, color="red", ') - 4, ly(T2, 4) - LH() / 2, tw("s=50") + 8, LH(), OR))
IW3 = 640
o.append(img(1184, 300, IW3, "main-2.png", rise(1), "s2-img"))
o.append(note(1184, 300 + IW3 * 620 / 1070 + 20, 640, 'color="red": 점 색. 안 적으면 순서대로 파랑, 주황 …', RED, 24, fade(2)))
o.append(note(1184, 300 + IW3 * 620 / 1070 + 90, 640, "s=50: 점 크기(넓이). 기본은 36이라 조금 크게 찍었어요.", OR, 24, fade(3)))
o.append(note(1184, 300 + IW3 * 620 / 1070 + 160, 640, "왼쪽 위 1e6은 세로 숫자가 100만 단위라는 뜻이에요. 0.8은 80만이에요.", GRAY, 24, fade(3)))
o.append(note(96 + 85, cbot(T2, 9) + 26, 960, "조건이 둘이면 (조건1) &amp; (조건2)처럼 괄호로 감싸요(45).", GRAY, 24, fade(1)))
W("scatter2", o, "300채 가운데 2015년 뒤에 짓고 범죄율이 45보다 낮은 집만 골랐어요. 45에서 배운 조건 두 개를 & 로 잇는 방법이에요. 10채가 남아요. 같은 그림판에 scatter를 두 번 부르면 두 번째 점이 첫 번째 위에 겹쳐 찍혀요. 두 번째 scatter에는 color로 빨간색, s로 점 크기 50을 줬어요. s는 점의 넓이라서 기본 36보다 조금 커져요. 색을 안 적으면 matplotlib이 순서대로 파랑, 주황 같은 색을 골라요. 둘 다 label을 붙였으니 legend가 범례 두 줄을 그려요." + REAL)

o = [sec("corr")] + head(EB3, "상관계수는 -1부터 1까지, 두 열이 같이 움직이는 정도예요", K3)
CW_ = 1360
CX0 = 280
o.append(f'<div data-build-in="wipe order 1" style="position:absolute;left:{CX0}px;top:640px;width:{CW_}px;height:16px;border-radius:8px;background:linear-gradient(90deg,{K4},#D7DAE0 50%,{K1})"></div>')
rng_ = np.random.default_rng(3)
xs = rng_.uniform(0.05, 0.95, 26)
for k, (v, t_, c_) in enumerate([(-1, "-1: 한쪽이 늘면 다른 쪽은 줄어요", K4), (0, "0: 관계가 없어요", GRAY), (1, "1: 같이 늘어요", K1)]):
    x = CX0 + (v + 1) / 2 * CW_
    o.append(p(f"position:absolute;left:{x - 60:.0f}px;top:676px;width:120px;text-align:center;font-family:{MONO};font-size:36px;font-weight:700;color:{c_}", f"{v:g}", rise(2) + DELAY(k * 120)))
    if v == 0:
        pts = list(zip(xs, rng_.uniform(0.05, 0.95, 26)))
    else:
        noise = rng_.normal(0, 0.06, 26)
        pts = [(a, min(max((a if v > 0 else 1 - a) + n_, 0.03), 0.97)) for a, n_ in zip(xs, noise)]
    bx = int(x - 170)
    o.append(frame(bx, 260, 340, 300, rise(2) + DELAY(k * 120)))
    o.append(dots_svg(bx, 260, 340, 300, pts, c_, 10, rise(2) + DELAY(k * 120), 0.7))
    o.append(p(f"position:absolute;left:{x - 220:.0f}px;top:744px;width:440px;text-align:center;font-size:26px;font-weight:700;line-height:1.4;color:{c_}", e(t_), rise(2) + DELAY(k * 120)))
o.append(strip_code(96, 850, 1728, 110, [('house["SquareFeet"]', "#9DC3F2", None), (".corr(", W_, None), ('house["Price"]', "#F2A7CF", None), (")", W_, None), ("   두 Series 사이의 상관계수", "#9AA0AB", None)], 34, rise(3)))
W("corr", o, "상관계수는 두 열이 얼마나 같이 움직이는지를 -1부터 1까지 숫자 하나로 알려 줘요. 1에 가까우면 한쪽이 늘 때 다른 쪽도 늘어서 점들이 오른쪽 위로 줄을 서요. -1에 가까우면 반대로 오른쪽 아래로 줄을 서요. 0 근처면 점이 흩어져 있어서 관계가 없다는 뜻이에요. pandas에서는 한 열에 .corr를 붙이고 괄호 안에 다른 열을 넣어요. 순서를 바꿔도 같은 값이에요. 그림의 점은 설명하려고 그린 예시예요.")

o = [sec("corr-trap")] + head(EB3, "10채만 보면 0.89, 300채 전체는 0.08이에요", K3)
CFS[0] = 26
CT = ['print("전체 300채의 상관계수:", round(house["SquareFeet"].corr(house["Price"]), 2))', 'print("2015 이후 건축 상관계수:", round(small["SquareFeet"].corr(small["Price"]), 2))']
o += cell({"id": "c-ct", "lines": CT, "n": 6, "out": ["전체 300채의 상관계수: 0.08", "2015 이후 건축 상관계수: 0.89"]}, 96, 196, 1728, sel="c-ct")
o.append(tag(cx(96, CT[0]) + 20, ly(196, 0), "앞 셀 아래쪽 두 줄", GRAY, None, 22))
o.append(tag(cx(96, "2015 이후 건축 상관계수: 0.89", True) + 30, oy(196, 2, 1), "round(값, 2): 소수 둘째 자리까지", GRAY, 1, 24))
IW4 = 860
IY4 = 420
o.append(img(96, IY4, IW4, "main-2.png", "", "ct-img"))
S4 = IW4 / 1070
o.append(f'<div data-build-in="fade order 2" style="position:absolute;left:{96 + 120 * S4:.0f}px;top:{IY4 + 50 * S4:.0f}px;width:{930 * S4:.0f}px;height:{462 * S4:.0f}px;background:rgba(246,245,241,0.55)"></div>')
o.append(f'<x-shape{WIPE(3)} kind="arrow-right" style="position:absolute;left:{96 + 190 * S4:.0f}px;top:{IY4 + 470 * S4:.0f}px;width:{720 * S4:.0f}px;height:26px;background:{RED};transform:rotate(-28deg);transform-origin:left center"></x-shape>')
RX = 1080
o.append(p(f"position:absolute;left:{RX}px;top:450px;font-family:{MONO};font-size:120px;font-weight:700;line-height:1;color:{GRAY}", "0.08", rise(1)))
o.append(p(f"position:absolute;left:{RX}px;top:590px;font-size:28px;color:{SUB}", "파란 점 300개: 흩어져 있어요", rise(1)))
o.append(p(f"position:absolute;left:{RX}px;top:670px;font-family:{MONO};font-size:120px;font-weight:700;line-height:1;color:{RED}", "0.89", rise(2)))
o.append(p(f"position:absolute;left:{RX}px;top:810px;width:660px;font-size:28px;color:{SUB}", "빨간 점 10개: 우연히 줄을 섰어요", rise(2)))
o.append(caption("골라낸 몇 개만 보면 없는 규칙이 보일 수 있어요. 전체로 판단해요.", 960, 4))
W("corr-trap", o, "앞 셀 아래쪽 두 줄의 결과예요. 300채 전체로 계산하면 면적과 가격의 상관계수가 0.08이라 관계가 거의 없어요. 그런데 고른 10채만 보면 0.89로 아주 높게 나와요. 빨간 점 10개만 따로 보면 오른쪽 위로 줄을 선 것처럼 보이기 때문이에요. 점이 적으면 우연히 줄을 설 수 있어요. 몇 개만 골라 보고 면적이 넓으면 비싸다고 판단하면 틀려요. 그래서 데이터 전체를 보고, 개수가 적은 결과는 의심해요." + REAL)

# ---------- part 4 ----------
o = [sec("whymake")] + head(EB4, "정답을 알고 만든 데이터라야 모델이 맞혔는지 채점할 수 있어요", K4)
FL = [("정답 규칙", "가격 =\n면적 × 450 + 5000", K4, "우리가 정해요"), ("흔들림 더하기", "잡음 ± 2500\n특이 매물 5건", K2, "실제 시세처럼"), ("데이터 200건", "area, price", K1, "office.csv"), ("48에서 모델이", "450과 5000을\n찾아낼까?", GRAY, "채점")]
for i, (h_, b_, c_, s_) in enumerate(FL):
    x = 96 + i * 440
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:{x}px;top:300px;width:380px;height:360px;border-radius:18px;border:3px {"dashed" if i == 3 else "solid"} {c_};background:#FFFFFF;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:24px">'
             + p(f"font-size:34px;font-weight:700;color:{c_}", e(h_)) + p(f"font-family:{MONO};font-size:28px;font-weight:700;line-height:1.5;text-align:center;white-space:pre;color:{INK}", e(b_))
             + p(f"font-size:24px;color:{GRAY}", e(s_)) + '</div>')
    if i < 3:
        o.append(arrow(44, "#C9CED8", WIPE(i + 2), f"position:absolute;left:{x + 388}px;top:465px"))
o.append(note(96, 740, 1728, "실제 데이터는 정답 규칙을 아무도 몰라요.<br>연습할 때는 규칙을 숨겨 둔 데이터를 직접 만들고, 모델이 그 규칙을 얼마나 가깝게 찾는지 봐요.", INK, 30, fade(4)))
W("whymake", o, "4파트에서는 데이터를 직접 만들어요. 실제 시세 데이터는 정답 규칙을 아무도 몰라서, 모델이 찾은 규칙이 맞는지 확인할 방법이 없어요. 그래서 연습할 때는 우리가 규칙을 정해 두고 데이터를 만들어요. 가격은 면적에 450을 곱하고 5000을 더한 값으로 정했어요. 그대로 두면 점이 자로 그은 듯 한 줄로 서니까 실제처럼 흔들림을 조금 더하고, 유난히 비싼 특이 매물도 다섯 건 넣어요. 48에서 모델이 450과 5000을 얼마나 가깝게 찾는지 채점해요.")

o = [sec("make")] + head(EB4, "연습 데이터를 만드는 셀 하나를 줄마다 봐요", K4)
CFS[0] = 26
o += cell({"id": "c-mk", "lines": MAKEC, "n": 7}, 96, 196, 1180, sel="c-mk")
o.append(mono(96 + 105, cbot(196, 11) + 18, DESC, 24, 1.3))
MKT = [(0, 1, "난수를 만드는 기계, 시드 42"), (3, 1, "20~85 사이 면적 200개"), (4, 1, "정답 규칙 + 흔들림"), (6, 2, "특이 매물 5건 값 올리기"), (9, 2, "표로 묶고 요약")]
for k, (i, n_, t_) in enumerate(MKT):
    o.append(lspot(k + 1, 96 + 87, 196, 1180 - 87, 10 + 11 * LH() + 8, 196 + 10 + i * LH(), n_ * LH(), bar=K4))
    o.append(tag(1300, ly(196, i) + (n_ - 1) * LH() / 2, t_, K4, k + 1, 26))
o.append(lspot_off(6))
o.append(note(760, cbot(196, 11) + 40, 1000, "같은 시드 42면 이 숫자가 그대로 나와요.<br>결과 표는 29쪽에서 읽어요. 다음 장부터 한 줄씩 봐요.", GRAY, 28, fade(6)))
W("make", o, "수업에서 연습 데이터를 만든 셀 전체예요. 다음 장부터 한 줄씩 자세히 보니까 여기서는 흐름만 봐요. 첫 줄은 난수를 만드는 기계를 시드 42로 만들어요. 면적 200개를 20부터 85 사이에서 뽑고, 가격은 정답 규칙에 흔들림을 더해 계산해요. 그다음 다섯 건을 골라 값을 크게 올려 특이 매물을 만들어요. 마지막으로 두 배열을 DataFrame으로 묶고 describe로 요약해요. 셀 번호 [7]은 앞의 산점도 셀 다음이라서예요." + REAL)

o = [sec("seed")] + head(EB4, "시드를 정하면 몇 번을 실행해도 같은 난수가 나와요", K4)
CFS[0] = 26
SD1 = ["a = np.random.default_rng(42)", "b = np.random.default_rng(42)", "print(a.uniform(20, 85, 3))", "print(b.uniform(20, 85, 3))"]
o += cell({"id": "c-sd1", "lines": SD1, "n": 2, "out": ["[70.30714316 48.52709858 75.80886479]", "[70.30714316 48.52709858 75.80886479]"]}, 96, 196, 860, sel="c-sd1")
SD2 = ["c = np.random.default_rng()", "print(c.uniform(20, 85, 3))"]
o += cell({"id": "c-sd2", "lines": SD2, "n": 3, "out": ["[54.37304406 25.20540904 34.6906226 ]"]}, 1000, 196, 824)
o += cell({"id": "c-sd3", "lines": SD2, "n": 4, "out": ["[35.8787782  31.6816176  36.54919986]"]}, 1000, 196 + 230, 824)
o.append(box(1, 96 + 105 - 8, oy(196, 4, 0) - LH() / 2 - 4, tw("[70.30714316 48.52709858 75.80886479]") + 16, 2 * LH() + 18, GR, 4, 8))
o.append(tag(96 + 105, oy(196, 4, 1) + 60, "시드 42: 둘이 똑같아요", GR, 1, 26, lead=False))
o.append(tag(1000 + 105, oy(196 + 230, 2, 0) + 60, "시드 없음: 실행할 때마다 달라요", RED, 2, 26, lead=False))
o.append(tint(2, cx(1000, "c = np.random.default_rng(") - 2, ly(196, 0) - LH() / 2, 18, LH(), RED))
DY = 690
o.append(f'<div data-build-in="rise order 3" style="position:absolute;left:96px;top:{DY}px;width:1728px;height:200px;display:flex;flex-direction:row;align-items:center;gap:30px">'
         + f'<div style="width:220px;height:160px;flex:none;border-radius:20px;border:4px solid {K4};background:{K4BG};display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px">'
         + p(f"font-size:24px;color:{SUB}", "rng") + p(f"font-family:{MONO};font-size:52px;font-weight:700;color:{K4}", "42") + '</div>'
         + arrow(60, K4) + "".join(p(f"width:150px;height:84px;flex:none;border-radius:12px;border:3px solid {K4};background:#FFFFFF;font-family:{MONO};font-size:30px;font-weight:700;line-height:78px;text-align:center;color:{INK}", v) for v in ["70.31", "48.53", "75.81", "65.33", "…"])
         + p(f"flex:1;font-size:28px;line-height:1.5;color:{INK}", "시드는 순서표 번호예요.<br>같은 번호면 같은 순서로 나와요.") + '</div>')
W("seed", o, "컴퓨터의 난수는 정해진 계산으로 만든 숫자예요. 그 계산의 시작 번호를 시드라고 해요. np.random.default_rng에 42를 넣어 두 개를 만들면 둘 다 똑같은 순서로 숫자를 내놓아요. 괄호를 비우면 실행할 때마다 시작 번호가 달라져서 결과도 달라요. 오른쪽 두 셀은 같은 코드를 두 번 실행한 결과예요. 수강생 모두 42를 넣으면 슬라이드와 같은 데이터를 얻어요. 42는 관례로 많이 쓰는 숫자일 뿐이고 다른 숫자를 넣어도 돼요. 시드 없는 두 셀의 숫자는 여러분 화면에서 또 달라요." + NEW1 + REAL)

o = [sec("seed-order")] + head(EB4, "같은 rng를 또 부르면 다음 순서의 숫자가 나와요", K4)
CFS[0] = 30
SO = ["rng = np.random.default_rng(42)", "print(rng.uniform(20, 85, 3))", "print(rng.uniform(20, 85, 3))"]
o += cell({"id": "c-so", "lines": SO, "n": 5, "out": ["[70.30714316 48.52709858 75.80886479]", "[65.32892189 26.12152761 83.41545286]"]}, 96, 196, 1728, sel="c-so")
o.append(link(1, cx(96, SO[1]) + 20, ly(196, 1), cx(96, "[70.30714316 48.52709858 75.80886479]", True) + 40, oy(196, 3, 0), K4))
o.append(link(2, cx(96, SO[2]) + 20, ly(196, 2), cx(96, "[65.32892189 26.12152761 83.41545286]", True) + 40, oy(196, 3, 1), K1))
o.append(tag(cx(96, "[70.30714316 48.52709858 75.80886479]", True) + 60, oy(196, 3, 0), "1~3번째 숫자", K4, 1, 26))
o.append(tag(cx(96, "[65.32892189 26.12152761 83.41545286]", True) + 60, oy(196, 3, 1), "4~6번째 숫자", K1, 2, 26))
SQ = ["70.31", "48.53", "75.81", "65.33", "26.12", "83.42", "…"]
for i, v in enumerate(SQ):
    c_ = K4 if i < 3 else (K1 if i < 6 else GRAY)
    o.append(vbox(96 + i * 200, 640, 180, 90, v, c_, "#FFFFFF", 30, rise(3) + DELAY(i * 60)))
o.append(note(96, 770, 1728, "셀을 다시 실행하면 첫 줄에서 rng를 새로 만들어서 70.31부터 다시 나와요.<br>그래서 시드는 데이터를 만드는 셀 맨 위에 한 번만 적어요.", INK, 30, fade(4)))
W("seed-order", o, "시드가 같다고 부를 때마다 같은 숫자가 나오는 건 아니에요. rng는 순서표를 따라 숫자를 하나씩 꺼내요. 첫 번째 uniform이 1번부터 3번 숫자를 가져가면 두 번째 uniform은 4번부터 6번 숫자를 받아요. 셀을 처음부터 다시 실행하면 첫 줄에서 rng를 새로 만들어서 다시 70.31부터 나와요. 그래서 데이터를 만드는 셀은 위에서부터 한 번에 실행하고, 시드는 맨 위에 한 번만 적어요. 4파트 셀도 이 순서라서 수강생 모두 같은 200건을 얻어요." + NEW1 + REAL)

o = [sec("uniform")] + head(EB4, "uniform(20, 85, n): 20부터 85 사이에서 고르게 n개", K4)
o.append(strip_code(96, 196, 1728, 120, [("area = rng.uniform(", W_, None), ("20", "#9DC3F2", None), (", ", W_, None), ("85", "#F2A7CF", None), (", ", W_, None), ("n", CV, None), (")", W_, None)], 44))
UA = [("20", "가장 작은 값 (low)", K1), ("85", "이 값 바로 아래까지 (high)", K4), ("n", "몇 개 뽑을지 (size). n = 200", GR)]
for i, (a, b, c_) in enumerate(UA):
    o.append(p(f"position:absolute;left:{96 + i * 580}px;top:350px;width:560px;font-size:30px;font-weight:700;color:{c_}", f'<span style="font-family:{MONO}">{e(a)}</span>  {e(b)}', rise(i + 1)))
NLX, NLW, NLY = 200, 1520, 640
o.append(f'<div{rise(4)} style="position:absolute;left:{NLX}px;top:{NLY}px;width:{NLW}px;height:6px;border-radius:3px;background:#9AA0AB"></div>')
for t in (20, 30, 40, 50, 60, 70, 80, 85):
    xx = NLX + (t - 20) / 65 * NLW
    o.append(p(f"position:absolute;left:{xx - 40:.0f}px;top:{NLY + 22}px;width:80px;text-align:center;font-family:{MONO};font-size:24px;color:{GRAY}", str(t), rise(4)))
pts = [((a - 20) / 65, 0.15 + 0.7 * ((k * 37) % 23) / 22) for k, a in enumerate(AREA)]
o.append(dots_svg(NLX, NLY - 190, NLW, 170, pts, K4, 8, rise(4), 0.6))
o.append(note(NLX, NLY + 80, NLW, "실제로 뽑은 면적 200개예요. 가장 작은 값 20.5, 가장 큰 값 84.5로 20~85 사이에 고르게 퍼졌어요.", INK, 28, fade(5)))
o.append(note(NLX, NLY + 150, NLW, "점의 높이는 겹치지 않게 흩어 놓은 것이고 뜻은 없어요.", GRAY, 24, fade(5)))
W("uniform", o, "uniform은 정해진 범위 안에서 어느 값이나 똑같은 확률로 뽑는 함수예요. 첫째 자리 20은 가장 작은 값, 둘째 자리 85는 가장 큰 쪽 끝이고, 85 자체는 나오지 않고 바로 아래까지예요. 셋째 자리는 몇 개를 뽑을지예요. 위에서 n = 200으로 정해 둬서 200개가 나와요. 개수를 변수로 두면 나중에 데이터 크기를 바꿀 때 한 곳만 고치면 돼요. 오피스텔 면적이 20제곱미터에서 85제곱미터 사이라고 보고 이 범위를 골랐어요. 아래 점은 실제로 뽑은 200개이고 고르게 퍼져 있어요.")

o = [sec("normal")] + head(EB4, "normal(0, 2500, n): 0 근처가 많고 멀수록 드문 흔들림", K4)
o.append(strip_code(96, 196, 1728, 120, [("rng.normal(", W_, None), ("0", "#9DC3F2", None), (", ", W_, None), ("2500", "#F2A7CF", None), (", ", W_, None), ("n", CV, None), (")", W_, None)], 44))
NA = [("0", "가운데 값, 평균 (loc)", K1), ("2500", "퍼진 정도, 표준편차 (scale)", K4), ("n", "몇 개 (size)", GR)]
for i, (a, b, c_) in enumerate(NA):
    o.append(p(f"position:absolute;left:{96 + i * 580}px;top:350px;width:560px;font-size:30px;font-weight:700;color:{c_}", f'<span style="font-family:{MONO}">{e(a)}</span>  {e(b)}', rise(i + 1)))
BX, BW_, BY, BH = 200, 1000, 470, 330
xs_ = np.linspace(-3.4, 3.4, 120)
ys_ = np.exp(-xs_ ** 2 / 2)
path = "M " + " L ".join(f"{(x + 3.4) / 6.8 * BW_:.1f} {BH - y * (BH - 20):.1f}" for x, y in zip(xs_, ys_))
fill2 = "M " + " L ".join(f"{(x + 3.4) / 6.8 * BW_:.1f} {BH - y * (BH - 20):.1f}" for x, y in zip(xs_, ys_) if abs(x) <= 2) + f" L {(2 + 3.4) / 6.8 * BW_:.1f} {BH} L {(-2 + 3.4) / 6.8 * BW_:.1f} {BH} Z"
o.append(f'<svg{rise(4)} style="position:absolute;left:{BX}px;top:{BY}px;width:{BW_}px;height:{BH}px;overflow:visible" viewBox="0 0 {BW_} {BH}"><path d="{fill2}" fill="{K4BG}"/><path d="{path}" fill="none" stroke="{K4}" stroke-width="5"/><line x1="0" y1="{BH}" x2="{BW_}" y2="{BH}" stroke="#9AA0AB" stroke-width="3"/></svg>')
for v in (-5000, -2500, 0, 2500, 5000):
    xx = BX + (v / 2500 + 3.4) / 6.8 * BW_
    o.append(p(f"position:absolute;left:{xx - 70:.0f}px;top:{BY + BH + 14}px;width:140px;text-align:center;font-family:{MONO};font-size:24px;color:{GRAY}", f"{v:+,}" if v else "0", rise(4)))
o.append(p(f"position:absolute;left:{BX + BW_ / 2 - 200:.0f}px;top:{BY + BH - 90}px;width:400px;text-align:center;font-size:26px;font-weight:700;color:{K4}", "±5000 안: 94%", rise(4)))
RX = 1260
o.append(label(RX, 470, "시드 7로 rng.normal(0, 2500, 5) 뽑기", GRAY, 24, fade(5)))
o.append(mono(RX, 512, ["[    3.   747.  -685. -2226. -1137.]"], 24, 1.4, INK, fade(5)))
o.append(note(RX, 580, 560, "+도 −도 나와요. 같은 면적이라도 시세가 위아래로 흔들리는 몫이에요.", INK, 28, fade(5)))
o.append(note(RX, 750, 560, "200개를 뽑으면 평균 41, 표준편차 2538로 정한 값과 거의 같아요.", GRAY, 24, fade(5)))
W("normal", o, "normal은 종 모양으로 퍼진 난수를 뽑아요. 가운데 값 근처가 가장 많이 나오고 멀어질수록 드물어요. 첫째 자리 0은 가운데 값, 즉 평균이에요. 둘째 자리 2500은 표준편차로 얼마나 넓게 퍼지는지예요. 셋째 자리는 개수예요. 평균이 0이라서 플러스도 마이너스도 나오고, 대부분 가운데 근처예요. 실제로 200개를 뽑아 보니 94%가 플러스마이너스 5000 안에 들었어요. 이 흔들림을 잡음이라고 불러요. 같은 면적이어도 층이나 위치에 따라 시세가 조금씩 다른 것을 흉내 낸 거예요. 오른쪽 위 줄은 시드 7로 다섯 개만 뽑아 본 예시예요." + NEW1 + REAL)

o = [sec("round")] + head(EB4, ".round(-1)은 10의 자리로 반올림해요", K4)
CFS[0] = 32
RD = ["print(np.round(1234.5678, -1), np.round(1234.5678, 0), np.round(1234.5678, 1))"]
o += cell({"id": "c-rd", "lines": RD, "n": 7, "out": ["1230.0 1235.0 1234.6"]}, 96, 196, 1728, sel="c-rd")
DG = list("1234.5678")
DX0, DY0 = 470, 420
for i, ch in enumerate(DG):
    o.append(p(f"position:absolute;left:{DX0 + i * 110}px;top:{DY0}px;width:100px;height:124px;border-radius:12px;border:3px solid #C9CED8;background:#FFFFFF;font-family:{MONO};font-size:64px;font-weight:700;line-height:118px;text-align:center;color:{INK}", ch))
for k, (pos, t_, res, c_) in enumerate([(2, "-1: 10의 자리까지", "1230", K4), (3, "0: 일의 자리까지", "1235", K1), (5, "1: 소수 첫째 자리까지", "1234.6", GR)]):
    xx = DX0 + pos * 110
    o.append(f'<div data-build-in="rise order {k + 1}" style="position:absolute;left:{xx - 6}px;top:{DY0 - 14}px;width:112px;height:152px;border-radius:14px;border:5px solid {c_}"></div>')
    o.append(p(f"position:absolute;left:{DX0}px;top:{DY0 + 190 + k * 74}px;width:1300px;font-size:34px;font-weight:700;color:{c_}", f'{e(t_)}  <span style="font-family:{MONO}">→ {res}</span>', rise(k + 1)))
o.append(note(96, 920, 1728, "수업 셀은 잡음에만 붙였어요: rng.normal(0, 2500, n).round(-1). 그래서 흔들림은 10 단위이고 면적 × 450은 소수가 남아요.", INK, 28, fade(4)))
W("round", o, "round에 넣는 숫자는 소수점에서 몇 자리까지 남길지예요. 1은 소수 첫째 자리, 0은 일의 자리까지 반올림해요. 음수를 넣으면 소수점 왼쪽으로 가요. -1은 10의 자리까지라서 1234.5678이 1230이 돼요. 수업 셀에서는 rng.normal(0, 2500, n) 바로 뒤에 붙였어요. 그래서 흔들림만 10 단위로 깔끔해지고, 면적에 450을 곱한 부분은 소수가 그대로 남아요. 가격 끝자리가 소수인 건 그 때문이에요. np.round와 배열 뒤에 붙이는 .round는 같은 일을 해요." + NEW1 + REAL)

o = [sec("formula")] + head(EB4, "배열 계산은 칸마다 따로 해요: 면적 × 450 + 5000 + 잡음", K4)
o.append(strip_code(96, 196, 1728, 110, [("price = ", W_, None), ("area", "#9DC3F2", None), (" * 450 + 5000 + ", W_, None), ("rng.normal(0, 2500, n).round(-1)", "#F2C46D", None)], 36))
COLS = [("area", [f"{v:.1f}" for v in AREA[:3]], K1, "fm-a"), ("× 450 + 5000", [f"{v:,.0f}" for v in (AREA[:3] * 450 + 5000)], GRAY, "fm-b"), ("+ 잡음", [f"{v:+,.0f}" for v in NOISE[:3]], K2, "fm-c"), ("= price", [f"{v:,.0f}" for v in PRICE[:3]], K4, "fm-d")]
for j, (h_, vals, c_, idp) in enumerate(COLS):
    x = 96 + j * 440
    o.append(p(f"position:absolute;left:{x}px;top:370px;width:380px;text-align:center;font-family:{MONO};font-size:32px;font-weight:700;color:{c_}", e(h_), rise(j + 1)))
    for i, v in enumerate(vals):
        o.append(vbox(x, 440 + i * 120, 380, 96, v, c_, "#FFFFFF", 36, rise(j + 1) + DELAY(i * 80), ))
    if j < 3:
        o.append(arrow(44, "#C9CED8", WIPE(j + 2), f"position:absolute;left:{x + 388}px;top:{440 + 120 + 33}px"))
o.append(p(f"position:absolute;left:96px;top:810px;width:1728px;font-family:{MONO};font-size:28px;color:{GRAY}", "0번, 1번, 2번 행  ⋯  199번 행까지 같은 계산", fade(4)))
o.append(note(96, 880, 1728, "45의 배열 * 2처럼 반복문 없이 200칸을 한 번에 계산해요. 소수는 보기 좋게 줄였어요.", INK, 28, fade(5)))
W("formula", o, "가격을 만드는 줄을 앞 세 행으로 따라가 봐요. area는 숫자 200개가 든 배열이라서 450을 곱하면 200칸이 각각 곱해져요. 45에서 배열에 2를 곱하면 칸마다 곱해졌던 것과 같아요. 0번 행은 면적 70.3에 450을 곱하고 5000을 더해 36638이 되고, 잡음 1610을 더해 38248이 돼요. 1번 행은 잡음이 마이너스라 정답 규칙보다 990 싸요. 반복문 없이 200행을 한 번에 계산해요. 숫자는 소수 첫째 자리나 정수로 줄여 적었어요." + REAL)

o = [sec("choice")] + head(EB4, "choice(n, 5, replace=False): 0~199 중 겹치지 않게 5개", K4)
o.append(strip_code(96, 196, 1728, 120, [("special = rng.choice(", W_, None), ("n", "#9DC3F2", None), (", ", W_, None), ("5", "#F2A7CF", None), (", ", W_, None), ("replace=False", CV, None), (")", W_, None)], 42))
CA = [("n", "0부터 n-1까지 번호 중에서 (0~199)", K1), ("5", "5개를 뽑아요", K4), ("replace=False", "뽑은 번호는 다시 안 넣어요", GR)]
for i, (a, b, c_) in enumerate(CA):
    o.append(p(f"position:absolute;left:96px;top:{350 + i * 64}px;width:1728px;font-size:30px;font-weight:700;color:{c_}", f'<span style="font-family:{MONO};display:inline-block;width:300px">{e(a)}</span>{e(b)}', rise(i + 1)))
CFS[0] = 28
CH1 = ["rng = np.random.default_rng(1)", "print(rng.choice(10, 5, replace=False))", "print(rng.choice(10, 5, replace=True))"]
o += cell({"id": "c-ch", "lines": CH1, "n": 8, "out": ["[3 0 6 8 2]", "[3 8 4 2 8]"]}, 96, 580, 1000, sel="c-ch")
o.append(box(4, cx(96, "[3 8 4 ", True) - 6, oy(580, 3, 1) - LH() / 2 - 2, tw("2") + 12, LH() + 4, RED, 4, 6) if False else "")
for pos in ("[3 ", "[3 8 4 2 "):
    o.append(box(4, cx(96, pos, True) - 6, oy(580, 3, 1) - LH() / 2 - 2, tw("8") + 12, LH() + 4, RED, 4, 6))
o.append(tag(cx(96, "[3 8 4 2 8]", True) + 30, oy(580, 3, 1), "True면 8이 두 번 나올 수 있어요", RED, 4, 24))
o.append(tag(cx(96, "[3 0 6 8 2]", True) + 30, oy(580, 3, 0), "False는 모두 달라요", GR, 4, 24))
o.append(label(1200, 600, "수업 셀의 결과", INK, 28, fade(5)))
o.append(p(f"position:absolute;left:1200px;top:650px;font-family:{MONO};font-size:44px;font-weight:700;color:{K4}", "[ 17 134 178 172 122]", fade(5)))
o.append(note(1200, 730, 620, "특이 매물이 될 행 번호 5개예요. 같은 집을 두 번 고르면 4건만 되니 False로 막았어요.", INK, 26, fade(5)))
W("choice", o, "choice는 번호 중에서 몇 개를 뽑아요. 첫째 자리에 숫자 n을 넣으면 0부터 n-1까지의 번호 중에서 뽑아요. n이 200이라 0번부터 199번 행 중에서예요. 둘째 자리는 뽑을 개수예요. replace는 뽑은 번호를 다시 넣을지예요. 공을 뽑고 다시 상자에 넣으면 같은 공이 또 나올 수 있어요. 왼쪽 아래 셀에서 True로 뽑으니 8이 두 번 나왔어요. 특이 매물은 서로 다른 집 다섯 채여야 해서 False로 뽑았어요. 수업 셀에서는 17, 134, 178, 172, 122번이 뽑혔어요." + REAL)

o = [sec("plus-eq")] + head(EB4, "price[special] += …: 고른 다섯 칸에만 값을 더해요", K4)
o.append(strip_code(96, 196, 1728, 110, [("price[", W_, None), ("special", "#9DC3F2", None), ("] += ", W_, None), ("rng.uniform(15000, 25000, 5)", "#F2A7CF", None), (".round(-1)", "#F2C46D", None)], 38))
o.append(note(96, 340, 1728, '대괄호 안에 번호 배열을 넣으면 그 칸들만 골라요. += 는 "지금 값에 더해서 다시 담기"예요(18). 다섯 칸에 15000~25000 사이 값을 하나씩 더해요.', INK, 28, rise(1)))
CFS[0] = 26
SPR = [(17, "24.148122", "37426.654741"), (134, "58.409507", "52044.278126"), (178, "77.959022", "65581.560038"), (172, "36.637731", "43556.978899"), (122, "25.488881", "34299.996393")]
o += cell({"id": "c-pe", "lines": ["office.loc[special]"], "n": 9}, 96, 470, 900)
o.append(df("pe-df", 96 + 85, cbot(470, 1) + 14, ["area", "price"], [(a, b) for _, a, b in SPR], [200, 240], fs=28, rh=58, idx=[i for i, _, _ in SPR], iw=80, cs={(i, 1): f"color:{K4};font-weight:700" for i in range(5)}, attrs=rise(2)))
IW5 = 820
o.append(img(1004, 430, IW5, "main-3.png", rise(3), "pe-img"))
S5 = IW5 / 1423
for (px_, py_) in [(284, 451), (505, 375), (888, 269), (1232, 100), (308, 490)]:
    o.append(ring(4, 1004 + px_ * S5 - 18, 430 + py_ * S5 - 18, 36, 36, RED, 4))
o.append(tag(1004 + 1232 * S5 - 110, 430 + 100 * S5, "178번", RED, 4, 24, lead=False))
W("plus-eq", o, "특이 매물 다섯 채의 가격을 올리는 줄이에요. 대괄호 안에 번호 하나 대신 번호 배열 special을 넣으면 그 다섯 칸만 한꺼번에 골라요. += 는 18에서 쓴 total += x처럼 지금 값에 더해서 다시 담는다는 뜻이에요. 더하는 값은 15000부터 25000 사이에서 다섯 개를 뽑아 10의 자리로 반올림했어요. 왼쪽 표는 만든 뒤에 그 다섯 행만 본 결과예요. 오른쪽 산점도에서 동그라미 친 점들이 직선 위로 붕 떠 있어요. 48에서 이 다섯 점이 채점 점수를 어떻게 흔드는지 봐요." + REAL)

o = [sec("describe")] + head(EB4, "딕셔너리로 DataFrame을 만들고 describe로 확인해요", K4)
CFS[0] = 28
DCL = ['office = pd.DataFrame({"area": area, "price": price})', "office.describe().round(1)"]
o += cell({"id": "c-dc", "lines": DCL, "n": 7}, 96, 196, 1728, sel="c-dc")
o.append(tint(1, cx(96, "office = pd.DataFrame({") - 4, ly(196, 0) - LH() / 2, tw('"area"') + 8, LH(), K1))
o.append(tint(1, cx(96, 'office = pd.DataFrame({"area": area, ') - 4, ly(196, 0) - LH() / 2, tw('"price"') + 8, LH(), K1))
o.append(tag(cx(96, DCL[0]) + 30, ly(196, 0), "키가 열 이름, 값이 열 내용 (45)", K1, 1, 26))
DT = cbot(196, 2) + 20
DV = [("200.0", "200.0"), ("52.1", "28990.3"), ("18.4", "9529.3"), ("20.5", "9472.2"), ("36.4", "21093.2"), ("51.1", "29281.8"), ("68.6", "36729.6"), ("84.5", "65581.6")]
o.append(df("dc-df", 96 + 85, DT, ["area", "price"], DV, [180, 220], fs=28, rh=62, idx=["count", "mean", "std", "min", "25%", "50%", "75%", "max"], iw=110))
RX = 96 + 85 + 110 + 400 + 70
for i, t_, c_, k in [(0, "200건", GR, 2), (3, "면적은 20~85 안이에요", K1, 3), (7, "65581.6: 178번 특이 매물", K4, 4)]:
    o.append(box(k, 96 + 85 - 6, dfy(DT, 62, i) - 2, 110 + 400 + 24, 60, c_, 4, 8))
    o.append(tag(RX, dfy(DT, 62, i) + 29, t_, c_, k, 28))
o.append(tag(RX, dfy(DT, 62, 1) + 29, "평균 면적 52.1, 평균 가격 28990", GRAY, 3, 26))
W("describe", o, "area와 price 두 배열을 딕셔너리에 담아 DataFrame으로 바꿔요. 45에서 본 것처럼 키가 열 이름, 값이 그 열의 내용이 돼요. describe로 만든 데이터를 확인해요. 개수가 200이고, 면적의 최솟값 20.5와 최댓값 84.5가 uniform에 준 범위 안이에요. 가격의 최댓값 65581.6은 특이 매물 178번이에요. round(1)은 표를 보기 좋게 소수 첫째 자리까지만 보여 줘요. 숫자가 예상한 범위에 있는지 이렇게 먼저 확인하는 습관을 들여요." + REAL)

o = [sec("tocsv")] + head(EB4, "to_csv(…, index=False)로 저장해야 다시 읽을 때 깔끔해요", K4)
CFS[0] = 28
o += cell({"id": "c-tc", "lines": ['office.to_csv("datasets/office.csv", index=False)'], "n": 8}, 96, 196, 1728, sel="c-tc")
o.append(tint(1, cx(96, 'office.to_csv("datasets/office.csv", ') - 4, ly(196, 0) - LH() / 2, tw("index=False") + 8, LH(), GR))
o.append(tag(cx(96, 'office.to_csv("datasets/office.csv", index=False)') + 30, ly(196, 0), "출력은 없어요. 파일이 생겨요", GRAY, None, 24))
FY = 380
for k, (ttl, lines, c_, rd, x0) in enumerate([("index=False (수업)", ["area,price", "70.30714315613761,38248.214420261924", "48.5270985838834,25847.19436274753", "⋮"], GR, ["        area         price", "0  70.307143  38248.214420", "1  48.527099  25847.194363"], 96),
                                               ("index를 빼먹으면", [",area,price", "0,70.30714315613761,38248.214420261924", "1,48.5270985838834,25847.19436274753", "⋮"], RED, ["   Unnamed: 0       area         price", "0           0  70.307143  38248.214420", "1           1  48.527099  25847.194363"], 984)]):
    o.append(label(x0, FY, ttl, c_, 30, rise(k + 2)))
    o.append(f'<div data-build-in="rise order {k + 2}" style="position:absolute;left:{x0}px;top:{FY + 56}px;width:840px;height:250px;border-radius:14px;border:2px solid {LINE};background:#FFFFFF;padding:20px 26px">'
             + p(f"font-size:22px;color:{GRAY}", "datasets/office.csv") + p(f"margin-top:10px;font-family:{MONO};font-size:22px;line-height:1.6;white-space:pre;color:{INK}", "<br>".join(e(l) for l in lines)) + '</div>')
    o.append(label(x0, FY + 340, "pd.read_csv로 다시 읽으면", GRAY, 24, rise(k + 2)))
    o.append(mono(x0, FY + 384, rd, 22, 1.5, INK, rise(k + 2)))
o.append(box(4, 1003, 500, 23, 132, RED, 4))
o.append(box(4, 1012, 762, 154, 38, RED, 4))
o.append(caption("index=False가 없으면 행 번호가 열로 저장돼서 Unnamed: 0 열이 생겨요.", 950, 5))
W("tocsv", o, "만든 표를 파일로 저장해야 48에서 다시 불러 쓸 수 있어요. to_csv의 첫째 자리는 저장할 경로, index=False는 왼쪽의 행 번호를 저장하지 말라는 뜻이에요. 왼쪽은 수업처럼 저장한 파일을 VS Code로 연 모습이에요. 첫 줄이 열 이름이고 그 아래가 값이에요. index=False를 빼면 오른쪽처럼 맨 앞에 번호 열이 같이 저장돼요. 이 파일을 다시 읽으면 이름 없는 번호 열이 Unnamed: 0이라는 열로 들어와요. 셀 출력은 없지만 왼쪽 탐색기의 datasets 폴더에 office.csv가 생겨요." + REAL)

# ---------- part 5 ----------
o = [sec("e-font")] + head(EB5, "글꼴 셀을 빼면 한글이 네모로 깨져요", K5)
CFS[0] = 22
o.append(img(96, 200, 700, "efont-1.png", "", "ef-img"))
o.append(ring(1, 96 + 410 * 700 / 1082, 200 + 10 * 700 / 1082, 260 * 700 / 1082, 50 * 700 / 1082, RED, 5))
o.append(ring(1, 96 + 2 * 700 / 1082, 200 + 380 * 700 / 1082, 50 * 700 / 1082, 160 * 700 / 1082, RED, 5))
o.append(label(900, 220, "셀 아래 경고", RED, 28, rise(2)))
o.append(mono(900, 270, ["UserWarning: Glyph 47588", "(\\N{HANGUL SYLLABLE MAE})", "missing from font(s) DejaVu Sans."], 28, 1.5, RED, rise(2)))
o.append(note(900, 430, 900, "'매' 글자 모양(Glyph)이 기본 글꼴 DejaVu Sans에 없다는 뜻이에요. 경고라서 그림은 나오지만 한글 자리가 네모예요.", INK, 28, rise(2)))
o.append(fix(900, 640, "글꼴 셀 없이 그리기", "셀 [2]를 먼저 실행", 3, 30, 920))
o.append(note(900, 760, 900, "노트북을 다시 열면 첫 셀부터 차례로 실행해요. 글꼴 설정도 다시 해야 해요.", GRAY, 26, fade(3)))
W("e-font", o, "글꼴 셀을 실행하지 않고 그래프를 그리면 제목과 축 이름의 한글이 네모로 나와요. 셀 아래에 UserWarning이 글자마다 하나씩 뜨는데, 매라는 글자의 모양이 기본 글꼴인 DejaVu Sans에 없다는 뜻이에요. 경고는 오류와 달리 셀이 멈추지 않아서 그림은 나와요. 고치는 법은 2파트의 글꼴 셀을 먼저 실행하는 거예요. VS Code를 껐다 켜면 설정이 사라지니 첫 셀부터 다시 실행해요." + NEW1 + REAL)

o = [sec("e-plot")] + head(EB5, "순서가 섞인 데이터를 plot으로 그리면 선이 엉켜요", K5)
CFS[0] = 26
EP = ["plt.figure(figsize=(8, 5))", 'plt.plot(office["area"], office["price"])', "plt.show()"]
o += cell({"id": "c-ep", "lines": EP, "n": 10}, 96, 196, 800, sel="c-ep")
o.append(tint(1, cx(96, "plt.") - 4, ly(196, 1) - LH() / 2, tw("plot") + 8, LH(), RED))
o.append(img(960, 196, 864, "eplot-1.png", rise(1), "ep-img"))
o.append(note(96 + 85, cbot(196, 3) + 40, 760, "plot은 표에 적힌 순서대로 점을 이어요. area는 무작위로 뽑아서 70.3 다음이 48.5, 그다음이 75.8이라 선이 왔다 갔다 해요.", INK, 28, rise(2)))
o.append(fix(96, 760, "plt.plot(...)", "plt.scatter(...)", 3, 32, 860))
o.append(note(96, 870, 860, "점끼리 이어야 할 때는 sort_values로 줄 세운 뒤에 plot해요(48).", GRAY, 26, fade(3)))
W("e-plot", o, "plot과 scatter를 헷갈리면 이런 그림이 나와요. plot은 표의 0번 행 점에서 1번 행 점, 2번 행 점 순서로 선을 이어요. 면적은 무작위로 뽑아서 70.3 다음이 48.5, 그다음이 75.8처럼 왔다 갔다 하니 선이 실타래처럼 엉켜요. 행 하나하나를 따로 보여 주려면 scatter를 써요. 월 매출처럼 순서가 있는 데이터만 plot으로 이어요. 48에서 모델의 직선을 그릴 때는 면적 순서로 줄을 세운 뒤에 plot해요." + NEW1 + REAL)

o = [sec("e-len")] + head(EB5, "x와 y의 개수가 다르면 ValueError가 나요", K5)
CFS[0] = 28
EL = ['months = ["1월", "2월", "3월", "4월", "5월", "6월"]', "sales = [120, 135, 120, 160, 170]", "", "plt.plot(months, sales)"]
o += cell({"id": "c-el", "lines": EL, "n": 2, "out": ["ValueError: x and y must have same first dimension, but have shapes (6,) and (5,)"], "err": True}, 96, 200, 1728)
o.append(underline(1, cx(96, "ValueError: x and y must have same first dimension, but have shapes ", True), cx(96, "ValueError: x and y must have same first dimension, but have shapes (6,) and (5,)", True), oy(200, 4, 0) + LH() / 2 - 2, RED, 5))
o.append(reading(96 + 105, oy(200, 4, 0) + 60, "same first dimension: 개수가 같아야 해요. (6,)과 (5,): x는 6개, y는 5개예요.", RED, 2, 30))
o.append(fix(96, 780, "sales = [120, 135, 120, 160, 170]", "sales = [120, 135, 120, 160, 170, 190]", 4, 30))
o.append(note(96, 940, 1728, "가로 6칸에 세로 값이 5개뿐이라 6월에 찍을 점이 없어요. len(months), len(sales)로 세어 봐요(13).", INK, 28, fade(4)))
o.append(label(96, 560, "months", K1, 26, rise(3), True))
o.append(label(96, 650, "sales", K4, 26, rise(3), True))
for i, (m_, v_) in enumerate(zip(["1월", "2월", "3월", "4월", "5월", "6월"], ["120", "135", "120", "160", "170", "?"])):
    o.append(vbox(260 + i * 150, 540, 130, 70, m_, K1, "#FFFFFF", 28, rise(3) + DELAY(i * 50)))
    o.append(vbox(260 + i * 150, 630, 130, 70, v_, RED if v_ == "?" else K4, K5BG if v_ == "?" else "#FFFFFF", 28, rise(3) + DELAY(i * 50), dashed=v_ == "?"))
o.append(tag(260 + 6 * 150 + 20, 665, "짝이 없어요", RED, 3, 28))
W("e-len", o, "x와 y는 같은 자리끼리 짝이 돼야 해서 개수가 같아야 해요. 월은 6개인데 매출을 5개만 적으면 ValueError가 나요. 메시지의 same first dimension은 첫 번째 크기가 같아야 한다는 뜻이고, shapes (6,) and (5,)가 각각 6개와 5개라는 뜻이에요. 빠진 6월 매출 190을 채우면 그려져요. 개수가 헷갈리면 13에서 배운 len으로 두 리스트를 세어 봐요." + NEW1 + REAL)

o = [sec("e-file")] + head(EB5, "경로를 틀리면 FileNotFoundError가 나요", K5)
CFS[0] = 28
o += cell({"id": "c-ef", "lines": ['house = pd.read_csv("usa_housing.csv")'], "n": 2, "out": ["FileNotFoundError: [Errno 2] No such file or directory: 'usa_housing.csv'"], "err": True}, 96, 200, 1728)
o.append(underline(1, cx(96, "FileNotFoundError: [Errno 2] ", True), cx(96, "FileNotFoundError: [Errno 2] No such file or directory", True), oy(200, 1, 0) + LH() / 2 - 2, RED, 5))
o.append(reading(96 + 105, oy(200, 1, 0) + 60, "No such file or directory: 그런 파일이나 폴더가 없대요. 노트북 옆에서 usa_housing.csv를 찾았어요.", RED, 2, 30))
TRX = 200
tree2 = [("ml-basics/", INK, 0), (NB, JP, 1), ("datasets/", K1, 1), ("usa_housing.csv", INK, 2)]
for i, (n_, c_, d) in enumerate(tree2):
    o.append(p(f"position:absolute;left:{TRX + d * 70}px;top:{480 + i * 90}px;font-family:{MONO};font-size:38px;font-weight:700;line-height:70px;color:{c_}", e(n_), rise(3)))
o.append(tag(TRX + 70 + 38 * 0.6 * 11 + 40, 480 + 90 + 35, "여기서 찾아요", JP, 3, 30))
o.append(tag(TRX + 140 + 38 * 0.6 * 15 + 40, 480 + 3 * 90 + 35, "파일은 한 칸 안쪽에 있어요", K1, 3, 30))
o.append(fix(96, 860, 'pd.read_csv("usa_housing.csv")', 'pd.read_csv("datasets/usa_housing.csv")', 4, 30))
W("e-file", o, "파일 경로를 틀리면 FileNotFoundError가 나요. 경로에 파일 이름만 적으면 노트북 파일이 있는 폴더에서 찾아요. 실제 파일은 그 안의 datasets 폴더에 있어서 못 찾은 거예요. 폴더 이름까지 datasets/usa_housing.csv로 적으면 돼요. 파일을 다운로드 폴더에 그대로 두었거나 폴더 이름의 철자가 다를 때도 같은 오류가 나요. VS Code 왼쪽 탐색기에서 파일 위치를 먼저 확인해요." + NEW1 + REAL)

# ---------- part 6 ----------
o = [sec("x-two")] + head(EB6, "매출과 목표를 한 그래프에: plot을 두 번, label은 각각", K6)
CFS[0] = 24
TWO = ["fig, ax = plt.subplots(figsize=(6, 5))", "", 'months = ["1월", "2월", "3월", "4월", "5월", "6월"]', "sales = [120, 135, 120, 160, 170, 190]", "goal = [130, 130, 140, 150, 160, 170]", "",
       'ax.plot(months, sales, marker="o", label="매출")', 'ax.plot(months, goal, marker="s", label="목표")', 'ax.set_title("My Mall 월 매출과 목표")', 'ax.set_xlabel("월")', 'ax.set_ylabel("매출(만원)")', "ax.legend()", "plt.show()"]
o += cell({"id": "c-two", "lines": TWO, "n": 1}, 96, 196, 980, sel="c-two")
o.append(hl(96, 196, 980, 6, 2, "mark", 1))
o.append(hl(96, 196, 980, 11, 1, "run", 2, "범례 두 줄"))
o.append(img(1130, 196, 694, "two-1.png", rise(1), "two-img"))
o.append(note(1130, 196 + 694 * 941 / 1079 + 20, 694, "3월에는 목표보다 20 모자라고, 6월에는 20 넘었어요.", INK, 26, fade(3)))
W("x-two", o, "실제로 자주 쓰는 모양이에요. 매출과 목표를 한 그래프에 그려서 어느 달이 모자랐는지 봐요. 같은 ax에 plot을 두 번 부르면 선이 두 개 그려져요. 색은 matplotlib이 파랑, 주황 순서로 알아서 골라요. 점 모양은 매출은 동그라미, 목표는 네모로 다르게 했어요. label을 하나씩 붙였으니 legend가 범례 두 줄을 그려요. 그래프를 보면 3월에 목표보다 20 모자라고 6월에는 20 넘었어요." + NEW1 + REAL)

o = [sec("x-office")] + head(EB6, "만든 오피스텔 200건을 그려서 직선이 보이는지 확인해요", K6)
CFS[0] = 22
OS = ["plt.figure(figsize=(8, 5))", 'plt.scatter(office["area"], office["price"], alpha=0.6)', 'plt.title("오피스텔 시세 200건")', 'plt.xlabel("면적")', 'plt.ylabel("가격")', "plt.show()", "",
      'print("상관계수:", office["area"].corr(office["price"]))']
o += cell({"id": "c-os", "lines": OS, "n": 9, "out": ["상관계수: 0.8967341729369117"]}, 96, 196, 920, sel="c-os")
o.append(box(1, cx(96, "", True) - 8, oy(196, 8, 0) - LH() / 2 - 4, tw("상관계수: 0.8967341729369117") + 16, LH() + 8, GR, 4, 8))
o.append(tag(cx(96, "상관계수: 0.8967341729369117", True) + 30, oy(196, 8, 0), "1에 가까워요", GR, 1, 26))
o.append(img(1060, 196, 764, "main-3.png", "", "os-img"))
S6 = 764 / 1423
o.append(f'<div data-build-in="fade order 2" style="position:absolute;left:{1060 + 215 * S6:.0f}px;top:{196 + 742 * S6:.0f}px;width:{1150 * S6:.0f}px;height:0;border-top:6px dashed {K6};transform:rotate(-17.5deg);transform-origin:left center"></div>')
o.append(note(1060, 196 + 764 * 941 / 1423 + 20, 764, "점선은 눈으로 그어 본 선이에요. 진짜 직선은 48에서 찾아요.", K6, 26, fade(2)))
o.append(caption("정답 규칙이 450, 5000이니 점이 직선 근처에 모이고 상관계수가 0.90이에요.", 940, 3))
W("x-office", o, "4파트에서 만든 데이터를 그려서 확인해요. 수업 셀 [9]예요. 점이 오른쪽 위로 곧게 올라가고 상관계수가 0.8967로 1에 가까워요. 정답 규칙대로 만들고 흔들림만 조금 더했으니 당연한 결과예요. 위로 붕 뜬 점 다섯 개가 특이 매물이에요. 점선은 설명하려고 손으로 그은 선이에요. 48에서는 scikit-learn이 이 점들에 가장 잘 맞는 직선을 찾고, 그 직선의 기울기가 정답 450에 얼마나 가까운지 봐요." + REAL)

o = [sec("x-cols")] + head(EB6, "미국 집값은 어느 열과도 상관계수가 0에 가까워요", K6)
CFS[0] = 26
XC = ['for col in ["Bedrooms", "Bathrooms", "SquareFeet", "YearBuilt", "CrimeRate", "SchoolRating"]:', '    print(col, round(house[col].corr(house["Price"]), 2))']
XO = [("Bedrooms", 0.02), ("Bathrooms", 0.06), ("SquareFeet", 0.08), ("YearBuilt", 0.0), ("CrimeRate", 0.01), ("SchoolRating", 0.03)]
o += cell({"id": "c-xc", "lines": XC, "n": 2, "out": [f"{a} {b}" for a, b in XO]}, 96, 196, 1728, sel="c-xc")
BXX, BY0, BWW, BLX = 1060, 400, 700, 760
o.append(label(BLX, BY0 - 64, "Price와의 상관계수 (0 ~ 1)", INK, 28, rise(1)))
for i, (a, b) in enumerate(XO + [("오피스텔", 0.90)]):
    y = BY0 + i * 58 + (20 if i == 6 else 0)
    c_ = GRAY if i == 6 else K6
    o.append(p(f"position:absolute;left:{BLX}px;top:{y}px;width:280px;font-family:{MONO};font-size:26px;font-weight:700;line-height:44px;color:{c_}", e(a), rise(1 if i < 6 else 2)))
    o.append(bar(BXX, y + 8, max(b * BWW, 6), 28, c_, WIPE(1 if i < 6 else 2) + DELAY(i * 60), 6))
    o.append(p(f"position:absolute;left:{BXX + max(b * BWW, 6) + 16:.0f}px;top:{y}px;font-family:{MONO};font-size:26px;font-weight:700;line-height:44px;color:{c_}", f"{b:.2f}", fade(1 if i < 6 else 2)))
o.append(note(96, 960, 1728, "어느 열 하나로도 가격을 줄 세울 수 없어요. 그래서 4파트에서 규칙이 확실한 연습 데이터를 직접 만들었어요.", INK, 30, fade(3)))
W("x-cols", o, "미국 집값 데이터에서 가격과 가장 관계가 깊은 열을 찾아봐요. 13에서 배운 for 반복문으로 여섯 열의 상관계수를 차례로 찍었어요. 모두 0.1보다 작아요. 맨 아래 회색 막대는 비교하려고 넣은 오피스텔 데이터의 0.90이에요. 이 데이터는 어느 열 하나만으로는 가격을 맞힐 수 없다는 뜻이에요. 수업 데이터가 연습용으로 만든 값이라서 그래요. 그래서 처음 배우는 모델에는 규칙을 알고 만든 오피스텔 데이터를 써요." + NEW1 + REAL)

# ---------- wrap up ----------
o = [sec("trouble")] + head("정리", "막히면 출력의 마지막 줄을 봐요", RED)
TR = [("ModuleNotFoundError: No module named 'matplotlib'", "프로젝트에 안 넣었어요", "uv add matplotlib"),
      ("FileNotFoundError: ... 'usa_housing.csv'", "경로에 폴더 이름이 빠졌어요", '"datasets/usa_housing.csv"'),
      ("ValueError: x and y must have same first dimension", "x와 y 개수가 달라요", "len()으로 세기"),
      ("UserWarning: Glyph ... missing from font(s)", "한글 글꼴을 안 정했어요", "글꼴 셀 먼저 실행"),
      ("범례가 안 나와요", "label만 적고 legend()를 안 불렀어요", "ax.legend()"),
      ("선이 실타래처럼 엉켜요", "순서 없는 데이터를 plot으로 이었어요", "scatter로"),
      ("친구와 난수가 달라요", "시드를 안 정했거나 셀을 나눠 실행했어요", "default_rng(42), 셀 처음부터")]
for i, (q, a_, cmd) in enumerate(TR):
    o.append(f'<div data-build-in="rise order {min(i + 1, 5)}" style="position:absolute;left:96px;top:{196 + i * 102}px;width:1728px;height:102px;display:flex;flex-direction:row;align-items:center;gap:26px;border-bottom:2px solid {LINE}">'
             + '<div style="flex:1;display:flex;flex-direction:column;gap:4px">' + p(f"{'font-family:' + MONO + ';' if q.isascii() else ''}font-size:25px;font-weight:700;color:{RED};white-space:nowrap", e(q)) + p(f"font-size:25px;color:{INK}", e(a_)) + '</div>'
             + p(f"width:560px;flex:none;font-size:27px;font-weight:700;color:{GR};white-space:pre", '✓ ' + e(cmd)) + '</div>')
o.append(caption("셀은 위에서부터 차례로 실행해요. 노트북을 다시 열었다면 첫 셀부터예요.", 950))
W("trouble", o, "막히면 셀 출력의 마지막 줄부터 읽어요. 위 넷은 오류나 경고 메시지가 나오는 경우이고, 아래 셋은 메시지 없이 그림이나 숫자가 이상한 경우예요. 메시지가 없는 경우가 더 찾기 어려워요. 범례가 없으면 legend, 선이 엉키면 plot과 scatter, 난수가 다르면 시드와 실행 순서를 확인해요.", ("trouble", "정리"))

o = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장으로 보는 오늘의 코드</h2>']
CH = [("그림판과 칸", "fig, ax = plt.subplots(figsize=(가로, 세로))", K2), ("선 그래프", 'ax.plot(x, y, marker="o", label="이름")', K2), ("이름 붙이기", 'ax.set_title(), set_xlabel(), set_ylabel(), ax.legend()', K2),
      ("산점도", 'plt.scatter(x, y, alpha=0.4, color="red", s=50)', K3), ("상관계수", 'df["a"].corr(df["b"])  -1 ~ 1', K3),
      ("난수 기계", "rng = np.random.default_rng(42)", K4), ("고르게", "rng.uniform(작은 값, 큰 값, 개수)", K4), ("종 모양", "rng.normal(평균, 표준편차, 개수)", K4),
      ("번호 뽑기", "rng.choice(n, 개수, replace=False)", K4), ("저장", 'df.to_csv("경로", index=False)', K4)]
for i, (k, d, c) in enumerate(CH):
    x, y = 96 + (i // 5) * 884, 190 + (i % 5) * 124
    o.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:844px;height:110px;display:flex;flex-direction:column;justify-content:center;gap:4px;border-bottom:2px solid {LINE}">'
             + p(f"font-size:26px;font-weight:700;color:{c}", e(k)) + p(f"font-family:{MONO};font-size:{24 if len(d) > 42 else 28}px;font-weight:700;color:{INK};white-space:pre", e(d)) + '</div>')
o.append(p(f"position:absolute;left:96px;top:850px;width:1728px;font-size:32px;font-weight:700;line-height:1.5;color:{INK}", "먼저 그려 보고, 정답을 아는 데이터로 연습해요.<br>" + f'<span style="color:{GRAY}">다음: 48에서 office.csv로 첫 머신러닝 모델(선형 회귀)을 학습해요.</span>'))
W("cheatsheet", o, "오늘 쓴 코드를 한 장에 모았어요. 왼쪽은 그래프, 오른쪽은 난수와 저장이에요. 그래프는 x, y 순서와 label, legend 짝을 기억해요. 난수는 시드를 먼저 정하고, uniform은 범위, normal은 평균과 표준편차, choice는 번호 뽑기예요. 저장할 때는 index=False를 붙여요. 다음 챕터에서는 오늘 저장한 office.csv로 첫 머신러닝 모델을 학습해요.")

# ---------- toc ----------
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
parts_ = [("Lightbulb", K1, "왜 필요한가", "why", "min"), ("Tool", K2, "matplotlib 그림판", "cells12", "styles"), ("Activity", K3, "산점도와 상관계수", "readcsv", "corr-trap"),
          ("Settings", K4, "연습 데이터 만들기", "whymake", "tocsv"), ("Warning", K5, "오류와 함정", "e-font", "e-file"), ("Star", K6, "실제 상황", "x-two", "x-cols")]
t = [f'<section id="toc" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>']
for i, (ic, c, h, a, b) in enumerate(parts_):
    x, y = 96 + (i // 3) * 884, 230 + (i % 3) * 190
    t.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:844px;height:160px;display:flex;flex-direction:row;align-items:center;gap:28px;border-bottom:2px solid {LINE}">'
             f'<p style="width:70px;font-size:72px;font-weight:900;color:{c}">{i + 1}</p><x-icon name="{ic}" style="width:52px;height:52px;color:{c}"></x-icon>'
             f'<p style="flex:1;font-size:44px;font-weight:700;color:{INK}">{e(h)}</p><p style="font-size:28px;color:{GRAY}">{page[a]}–{page[b]}쪽</p></div>')
t.append(f'<p style="position:absolute;left:96px;top:880px;font-size:30px;color:{SUB}">{page["setup"]}쪽은 프로젝트 준비, {page["trouble"]}–{page["cheatsheet"]}쪽은 막힐 때와 한 장 요약이에요.</p>')
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(t) + "\n<aside>" + e("1파트에서 왜 그래프부터 그리는지와 오늘 쓰는 도구를 보고, 2파트에서 matplotlib 그래프를 한 줄씩 만들어요. 3파트는 산점도와 상관계수, 4파트는 정답을 숨긴 연습 데이터 만들기예요. 5파트는 자주 하는 실수, 6파트는 배운 것을 섞은 실제 상황이에요.") + "</aside>\n</section>\n")
deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-24T06:00:00Z"}, "lists": "css", "title": "그래프 그리기와 연습 데이터 만들기", "order": ORDER, "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
print(len(ORDER), "slides")
