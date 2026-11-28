"""Generates every slide of the gradient descent deck (49) and slides/deck.json.

Story: class notebook 03_ml.ipynb, part 2 (gradient descent), on the class's five students (hours 1-5, scores 47 53 65
73 87). Students mixed up the quadratic curve and derivatives, so neither appears as a formula: the U shape is the MSE
table for b = 35 and w = 8..12, and a slope is "move w by 0.001 and see how much the MSE changes". Part 1 recaps 48
(LinearRegression computes w 10, b 35 at once) and asks how to find w and b without a formula (walking down a foggy hill).
Part 2: the loss function, the U shape, the two meanings of "기울기" (the line's slope w in blue, the loss slope in orange),
tangent lines, one step against the slope, and five steps by hand with def loss(w). Part 3: the learning rate (step size),
by hand and with SGDRegressor (eta0 0.001, 0.01, 0.1, 0.5). Part 4 takes the class cells apart: SGDRegressor and each
argument, partial_fit and epochs, the history loop, the learning curve, w and b over epochs, the final prediction,
and a LinearRegression comparison. Part 5: real errors and traps. Part 6: when to stop, two new students, and 47's office
data. Class-code bugs are shown fixed and named in the notes.
Every cell and output comes from tools/demo.sh (tools/run_nb.py runs the cells with the project kernel), kept in
tools/demo.log. Charts are the kernel's own PNGs in tools/img (NanumGothic stands in for Malgun Gothic on Linux).
Drawn diagrams (U curves, tangents, steps) are computed here from the same five students with NumPy.

Layout rules (Stageshow skill, github.com/benjitaylor/skills, SKILL.md and references/ read in full for this deck):
1. one focal object per slide (a notebook cell, a kernel chart, or one drawn diagram), the rest quiet (framing.md rule 1)
2. terms sit on the code token or the curve as leader tags, not in cards (annotations.md: a leader explains one object)
3. one color per meaning across the deck: line slope w blue, loss slope orange, loss (MSE) red, b teal (craft.md, Color)
4. no empty bands; the payoff gets the room (craft.md, Restraint: space follows the story)
5. values move instead of swapping: the ball rolls down the U, w and b fly in (motion.md: every change moves)
6. one number gets to be big (3.2, 95.52, 504), the rest are lines (craft.md, Restraint)
Highlights come from tools/HIGHLIGHT.md, as many kinds as fit. No typing effect.
Usage: python3 tools/gen.py slides
"""


import base64
import html, json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from highlight import *

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
IMGN = " 그래프는 리눅스 커널이 그려서 맑은 고딕 대신 나눔고딕으로 나왔어요."
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
TB = "#F4F5F7"   # striped row, like VS Code's notebook table
IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
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

class Plot:
    """A drawn chart: data (x, y) to slide pixels inside a box. Axes are a thin left and bottom line."""
    def __init__(self, left, top, w, h, xr, yr):
        self.l, self.t, self.w, self.h, self.xr, self.yr = left, top, w, h, xr, yr

    def X(self, x):
        return self.l + (x - self.xr[0]) / (self.xr[1] - self.xr[0]) * self.w

    def Y(self, y):
        return self.t + self.h - (y - self.yr[0]) / (self.yr[1] - self.yr[0]) * self.h

    def svg(self, inner, attrs="", tid=None):
        idt = f' id="{tid}"' if tid else ""
        return f'<svg{idt}{attrs} style="position:absolute;left:0;top:0;width:1920px;height:1080px;overflow:visible;pointer-events:none" viewBox="0 0 1920 1080">{inner}</svg>'

    def axes(self, xlabel, ylabel, ticks_x=(), ticks_y=(), fs=22):
        o = [frame(self.l, self.t, self.w, self.h)]
        for v in ticks_x:
            o.append(p(f"position:absolute;left:{self.X(v) - 40:.0f}px;top:{self.t + self.h + 10}px;width:80px;text-align:center;font-size:{fs}px;color:{GRAY}", e(str(v))))
        for v in ticks_y:
            o.append(p(f"position:absolute;left:{self.l - 130}px;top:{self.Y(v) - fs * 0.7:.0f}px;width:116px;text-align:right;font-size:{fs}px;color:{GRAY}", e(f"{v:,}")))
        o.append(p(f"position:absolute;left:{self.l + self.w - 300}px;top:{self.t + self.h + 10 + (fs + 14 if ticks_x else 0)}px;width:300px;text-align:right;font-size:{fs + 2}px;font-weight:700;color:{SUB}", e(xlabel)))
        o.append(p(f"position:absolute;left:{self.l + 14}px;top:{self.t - 8}px;font-size:{fs + 2}px;font-weight:700;color:{SUB}", e(ylabel)))
        return o

    def dots(self, xs, ys, color=K1, r=7, op=0.5):
        return "".join(f'<circle cx="{self.X(x):.1f}" cy="{self.Y(y):.1f}" r="{r}" fill="{color}" fill-opacity="{op}"/>' for x, y in zip(xs, ys))

    def line(self, w, b, color, width=5, dash=""):
        x0, x1 = self.xr
        d = f' stroke-dasharray="{dash}"' if dash else ""
        return f'<line x1="{self.X(x0):.1f}" y1="{self.Y(w * x0 + b):.1f}" x2="{self.X(x1):.1f}" y2="{self.Y(w * x1 + b):.1f}" stroke="{color}" stroke-width="{width}" stroke-linecap="round"{d}/>'



    def path(self, fn, x0, x1, n=120):
        pts = [(x0 + (x1 - x0) * i / n) for i in range(n + 1)]
        return "M " + " L ".join(f"{self.X(x):.1f} {self.Y(fn(x)):.1f}" for x in pts)

    def curve(self, fn, x0, x1, color, width=5, attrs="", n=120):
        return f'<path{attrs} d="{self.path(fn, x0, x1, n)}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>'

    def tangent(self, fn, x, half, color, width=5, k=None):
        """A short straight ruler touching the curve at x (slope k in data units)."""
        k = k if k is not None else (fn(x + 1e-4) - fn(x - 1e-4)) / 2e-4
        x0, x1 = x - half, x + half
        return f'<line x1="{self.X(x0):.1f}" y1="{self.Y(fn(x) + k * (x0 - x)):.1f}" x2="{self.X(x1):.1f}" y2="{self.Y(fn(x) + k * (x1 - x)):.1f}" stroke="{color}" stroke-width="{width}" stroke-linecap="round"/>'


# ---------- this deck ----------
import numpy as np
NB = "gd.ipynb"
REAL_D = " 그림의 점과 선은 같은 5명 데이터로 계산해서 그렸어요."
EB1, EB2, EB3, EB4, EB5, EB6 = "1. 왜 필요한가", "2. 손실과 경사", "3. 학습률", "4. SGDRegressor로 학습하기", "5. 오류와 함정", "6. 실제 상황"
WC, WCBG = K1, K1BG          # the line's slope w: blue everywhere
GC, GCBG = OR, "#F7EEDD"     # the loss slope (경사): orange everywhere
LC, LCBG = RED, K5BG         # loss (MSE): red
BC, BCBG = TEAL, K3BG        # intercept b: teal
HRS = np.array([1, 2, 3, 4, 5.])
SCS = np.array([47, 53, 65, 73, 87.])


def mse(w, b=35):
    return float(np.mean((SCS - (w * HRS + b)) ** 2))


def slope(w, b=35):
    return float(-2 * np.mean(HRS * (SCS - w * HRS - b)))


assert [round(mse(w), 1) for w in (8, 9, 10, 11, 12)] == [47.2, 14.2, 3.2, 14.2, 47.2]
assert [round(slope(w), 1) for w in (8, 10, 12)] == [-44.0, 0.0, 44.0]
assert round(mse(0, 0), 1) == 4428.2


def walk(lr, w=8.0, n=5):
    out = [w]
    for _ in range(n):
        w = w - lr * (mse(w + 0.001) - mse(w)) / 0.001   # same as the notebook cell
        out.append(w)
    return out


assert [round(v, 2) for v in walk(0.01)] == [8, 8.44, 8.78, 9.05, 9.26, 9.42]
assert [round(v, 2) for v in walk(0.1)] == [8, 12.4, 7.12, 13.45, 5.85, 14.97]

IMPORTS = ["import pandas as pd", "import matplotlib.pyplot as plt", "", "from sklearn.linear_model import LinearRegression",
           "from sklearn.linear_model import SGDRegressor", "from sklearn.metrics import mean_squared_error"]
FONTC = ["import platform", "", "os_name = platform.system()", 'if os_name == "Windows":', '    plt.rcParams["font.family"] = "Malgun Gothic"',
         'elif os_name == "Darwin":', '    plt.rcParams["font.family"] = "AppleGothic"', "", 'plt.rcParams["axes.unicode_minus"] = False']
DATAC = ["df = pd.DataFrame({", '    "hours": [1, 2, 3, 4, 5],', '    "scores": [47, 53, 65, 73, 87]', "})", "", 'X = df[["hours"]]', 'y = df["scores"]', "df"]
LRC = ["model = LinearRegression()", "model.fit(X, y)", "y_pred = model.predict(X)", "", 'print(f"Weight: {model.coef_[0]:.2f}")',
       'print(f"Bias: {model.intercept_:.2f}")', 'print(f"MSE: {mean_squared_error(y, y_pred):.4f}")']
LRO = ["Weight: 10.00", "Bias: 35.00", "MSE: 3.2000"]
TABC = ["for w in [8, 9, 10, 11, 12]:", '    pred = w * df["hours"] + 35', "    mse = mean_squared_error(y, pred)", '    print("w =", w, "MSE =", round(mse, 1))']
TABO = ["w = 8 MSE = 47.2", "w = 9 MSE = 14.2", "w = 10 MSE = 3.2", "w = 11 MSE = 14.2", "w = 12 MSE = 47.2"]
UC = ["ws = [w / 2 for w in range(12, 29)]", 'losses = [mean_squared_error(y, w * df["hours"] + 35) for w in ws]', "",
      "fig, ax = plt.subplots(figsize=(7, 4))", 'ax.plot(ws, losses, marker="o")', 'ax.set_title("b = 35일 때 기울기 w에 따른 MSE")',
      'ax.set_xlabel("기울기 w")', 'ax.set_ylabel("MSE")', "plt.show()"]
LOSSC = ["def loss(w):", '    pred = w * df["hours"] + 35', "    return mean_squared_error(y, pred)", "", "print(loss(8), loss(10), loss(12))"]
SLOPEC = ["for w in [8, 10, 12]:", "    slope = (loss(w + 0.001) - loss(w)) / 0.001", '    print("w =", w, "| 손실의 기울기 =", round(slope, 1))']
SLOPEO = ["w = 8 | 손실의 기울기 = -44.0", "w = 10 | 손실의 기울기 = 0.0", "w = 12 | 손실의 기울기 = 44.0"]
STEPC = ["w = 8", "for step in range(1, 6):", "    slope = (loss(w + 0.001) - loss(w)) / 0.001", "    w = w - 0.01 * slope",
         '    print("걸음", step, "| 경사 =", round(slope, 1), "| 새 w =", round(w, 2), "| MSE =", round(loss(w), 2))']
STEPO = ["걸음 1 | 경사 = -44.0 | 새 w = 8.44 | MSE = 29.97", "걸음 2 | 경사 = -34.3 | 새 w = 8.78 | MSE = 19.49", "걸음 3 | 경사 = -26.8 | 새 w = 9.05 | MSE = 13.11",
         "걸음 4 | 경사 = -20.9 | 새 w = 9.26 | MSE = 9.23", "걸음 5 | 경사 = -16.3 | 새 w = 9.42 | MSE = 6.87"]
LRSC = ["for lr in [0.002, 0.01, 0.1]:", "    w = 8", "    path = [w]", "    for step in range(5):", "        slope = (loss(w + 0.001) - loss(w)) / 0.001",
        "        w = w - lr * slope", "        path.append(round(w, 2))", '    print("학습률", lr, ":", path)']
LRSO = ["학습률 0.002 : [8, 8.09, 8.17, 8.25, 8.33, 8.4]", "학습률 0.01 : [8, 8.44, 8.78, 9.05, 9.26, 9.42]", "학습률 0.1 : [8, 12.4, 7.12, 13.45, 5.85, 14.97]"]
SGDC = ["sgd = SGDRegressor(", '    loss="squared_error",      # 손실 함수: 오차 제곱 평균(MSE)', '    learning_rate="constant",  # 학습률을 처음 값 그대로',
        "    eta0=0.01,                 # 학습률: 한 번에 고치는 보폭", "    shuffle=False,             # 데이터 순서를 섞지 않음", "    random_state=42            # 난수 시드", ")", "sgd"]
SGDO = ["SGDRegressor(learning_rate='constant', random_state=42, shuffle=False)"]
LOOPC = ["epochs = 1000", "history = []", "", "for epoch in range(epochs):", "    sgd.partial_fit(X, y)", "", "    y_pred = sgd.predict(X)", "    mse = mean_squared_error(y, y_pred)", "",
         "    history.append({", '        "epoch": epoch + 1,', '        "weight": sgd.coef_[0],', '        "bias": sgd.intercept_[0],', '        "mse": mse', "    })", "",
         "history_df = pd.DataFrame(history)", "history_df"]
PICKC = ['history_df[history_df["epoch"].isin([1, 5, 10, 50, 100, 300, 500, 1000])]']
PICKR = [(1, "8.455225", "2.731163", "1369.816039"), (5, "16.728403", "6.216494", "167.673523"), (10, "17.060518", "7.615610", "141.377004"), (50, "15.031795", "15.629821", "72.111791"),
         (100, "13.294764", "22.401342", "32.278720"), (300, "10.678818", "32.599172", "4.254356"), (500, "10.223895", "34.372614", "3.302220"), (1000, "10.129335", "34.741238", "3.250159")]
CURVEC = ["plt.figure(figsize=(10, 5))", 'plt.plot(history_df["epoch"], history_df["mse"], color="blue", label="학습 손실(Training Loss)")',
          'plt.title("epoch마다 MSE가 줄어요")', 'plt.xlabel("Epoch")', 'plt.ylabel("MSE")', "plt.grid(alpha=0.3)", "plt.legend()", "plt.show()"]
WBC = ["fig, axes = plt.subplots(1, 2, figsize=(12, 5))", "", 'axes[0].plot(history_df["epoch"], history_df["weight"], color="blue")', 'axes[0].set_title("기울기 w")',
       'axes[0].set_xlabel("Epoch")', "axes[0].grid(alpha=0.3)", "", 'axes[1].plot(history_df["epoch"], history_df["bias"], color="blue")', 'axes[1].set_title("절편 b")',
       'axes[1].set_xlabel("Epoch")', "axes[1].grid(alpha=0.3)", "", "plt.show()"]
PREDC = ['print(f"기울기(w): {sgd.coef_[0]:.2f}")', 'print(f"절편(b): {sgd.intercept_[0]:.2f}")', "", 'new_data = pd.DataFrame({"hours": [6]})',
         "prediction = sgd.predict(new_data)", 'print(f"예측 성적: {prediction[0]:.2f}점")']
PREDO = ["기울기(w): 10.13", "절편(b): 34.74", "예측 성적: 95.52점"]
TRAINC = ["def train(eta, epochs=1000):", '    model = SGDRegressor(loss="squared_error", learning_rate="constant",', "                         eta0=eta, shuffle=False, random_state=42)",
          "    losses = []", "    for epoch in range(epochs):", "        model.partial_fit(X, y)", "        losses.append(mean_squared_error(y, model.predict(X)))", "    return model, losses"]
ETAC = ["for eta in [0.001, 0.01, 0.1, 0.5]:", "    m, losses = train(eta)",
        '    print("eta0 =", eta, "| w =", round(m.coef_[0], 2), "| b =", round(m.intercept_[0], 2), "| MSE =", round(losses[-1], 2))']
ETAO = ["eta0 = 0.001 | w = 13.53 | b = 22.17 | MSE = 33.13", "eta0 = 0.01 | w = 10.13 | b = 34.74 | MSE = 3.25", "eta0 = 0.1 | w = 14.1 | b = 26.87 | MSE = 54.15",
        "eta0 = 0.5 | w = 122243204786.88 | b = 2622426923558.02 | MSE = 8.964943610021554e+24"]
ETACH = ["fig, ax = plt.subplots(figsize=(10, 5))", "for eta in [0.001, 0.01, 0.1]:", "    m, losses = train(eta)", '    ax.plot(range(1, 1001), losses, label="eta0 = " + str(eta))',
         "ax.set_ylim(0, 200)", 'ax.set_title("학습률마다 MSE가 줄어드는 모습")', 'ax.set_xlabel("Epoch")', 'ax.set_ylabel("MSE")', "ax.legend()", "plt.show()"]


def ball(x, y, color=GC, r=16, attrs="", tid=None):
    idt = f' id="{tid}"' if tid else ""
    return f'<div{idt}{attrs} style="position:absolute;left:{x - r:.0f}px;top:{y - r:.0f}px;width:{2 * r}px;height:{2 * r}px;border-radius:50%;background:{color};border:4px solid #FFFFFF;box-shadow:0 2px 6px rgba(0,0,0,0.25)"></div>'


def pill(x, y, text, color, bg, fs=26, attrs="", mono_=True):
    return p(f"position:absolute;left:{x:.0f}px;top:{y:.0f}px;font-family:{MONO if mono_ else SANS};font-size:{fs}px;font-weight:700;line-height:1.3;color:{color};background:{bg};border-radius:10px;padding:4px 14px;white-space:nowrap", e(text), attrs)


def scatter_plot(P, line=None, color=RED, dots_attrs=""):
    o = P.axes("공부 시간", "점수", (1, 2, 3, 4, 5, 6), (40, 60, 80, 100))
    o.append(P.svg(P.dots(HRS, SCS, K1, 11, 0.85), dots_attrs))
    return o


# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#F2B27A;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
       f'<h1{SLAM(1)} style="font-size:100px;font-weight:900;line-height:1.12;color:#F6F5F1">경사 하강법</h1>',
       '<p style="font-size:40px;line-height:1.45;color:#BFC6D4">조금씩 고쳐 가며<br>가장 잘 맞는 직선을 찾아요</p>']
cov.append(f'<div style="position:absolute;left:1000px;top:190px;width:800px;height:620px;background:#FFFFFF;border-radius:24px"></div>')
CP = Plot(1110, 260, 620, 440, (6, 14), (0, 190))
cov.append(CP.svg(CP.curve(mse, 6.3, 13.7, LC, 6)))
cov.append(p(f"position:absolute;left:1110px;top:216px;font-size:24px;font-weight:700;color:{LC}", "MSE (틀린 정도)"))
cov.append(p(f"position:absolute;left:1430px;top:716px;width:300px;text-align:right;font-size:24px;font-weight:700;color:{WC}", "기울기 w →"))
CW = walk(0.01, 6.6, 12)
cov.append(CP.svg("".join(f'<circle cx="{CP.X(v):.1f}" cy="{CP.Y(mse(v)):.1f}" r="7" fill="{GC}" fill-opacity="0.45"/>' for v in CW[:-1])))
cov.append(CP.svg(f'<path id="cov-path" d="M ' + " L ".join(f"{CP.X(v):.1f} {CP.Y(mse(v)):.1f}" for v in CW) + '" fill="none" stroke="none"/>'))
cov.append(ball(CP.X(CW[-1]), CP.Y(mse(CW[-1])), GC, 18, PATH(2, "cov-path", 2600)))
cov.append(p(f"position:absolute;left:1000px;top:836px;width:800px;font-size:26px;line-height:1.5;color:#BFC6D4", "공 하나가 MSE 그래프의 골짜기 바닥으로 한 걸음씩 내려가요."))
W("cover", cov, "오늘은 경사 하강법을 배워요. 48에서는 LinearRegression이 기울기와 절편을 한 번에 계산해 줬어요. 오늘은 그 값을 처음엔 대충 정해 놓고, 틀린 정도를 보면서 조금씩 고쳐 가는 방법을 봐요. 오른쪽 빨간 U자 선이 틀린 정도를 나타내는 그래프이고, 주황 공이 한 걸음씩 바닥으로 내려가요. 2차함수나 미분이라는 말이 나오지만 식은 쓰지 않고 그림과 숫자로만 풀어요.", ("intro", "들어가기"))
ORDER.append("toc")

# ---------- setup ----------
o = [sec("setup")] + head("들어가기", "48의 ml-basics에 새 노트북 gd.ipynb를 만들어요", JP)
CFS[0] = 26
o += cell({"id": "c-imp", "lines": IMPORTS, "n": 1}, 96, 210, 1080, sel="c-imp")
o.append(hl(96, 210, 1080, 4, 1, "mark", 1, "오늘 새 모델"))
o.append(hl(96, 210, 1080, 5, 1, "skip", 1, "48의 MSE"))
o += cell({"id": "c-font", "lines": FONTC, "n": 2}, 96, 500, 1080)
o.append(hl(96, 500, 1080, 8, 1, "mark", 2, "새 줄"))
o.append(note(1240, 230, 600, "설치할 것은 없어요. 48에서 넣은 scikit-learn에 SGDRegressor도 들어 있어요.", INK, 30, fade(1)))
o.append(note(1240, 520, 600, "맨 아래 줄은 그래프 눈금의 마이너스(-)가 네모로 깨지지 않게 하는 설정이에요.", INK, 30, fade(2)))
o.append(note(1240, 700, 600, "AppleGothic처럼 마이너스 기호가 없는 글꼴에서 깨져요. 46, 47의 글꼴 셀에 이 한 줄만 더했어요.", SUB, 26, fade(2)))
W("setup", o, "45부터 쓰는 ml-basics 프로젝트에 새 노트북 gd.ipynb를 만들어요. 48에서 scikit-learn을 넣었으니 새로 설치할 것은 없어요. 첫 셀은 수업과 같은 import예요. LinearRegression은 48에서 쓴 모델이고, SGDRegressor가 오늘 새로 쓰는 모델이에요. 둘째 셀은 46과 47의 한글 글꼴 셀에 한 줄을 더했어요. axes.unicode_minus를 False로 두면 그래프 눈금의 마이너스 기호가 깨지지 않아요. 수업 노트북은 AppleGothic만 적어서 윈도우에서는 한글이 깨지고, 실제로 마이너스 기호가 깨졌다는 경고가 나왔어요. 그래서 고친 모양으로 보여 드려요." + REAL)

# ---------- part 1 ----------
o = [sec("recap")] + head(EB1, "48처럼 LinearRegression은 w 10, b 35를 한 번에 계산해요", K1)
CFS[0] = 24
o += cell({"id": "c-data", "lines": DATAC, "n": 3}, 96, 200, 960, sel="c-data")
o += cell({"id": "c-lr", "lines": LRC, "n": 4, "out": LRO}, 96, 520, 960)
P = Plot(1230, 240, 560, 520, (0, 6.6), (30, 105))
o += scatter_plot(P)
o.append(P.svg(P.line(10, 35, RED, 6), WIPE(1)))
o.append(label(P.X(2.6), P.Y(10 * 2.6 + 35) + 30, "10 × 시간 + 35", RED, 28, fade(1)))
o.append(ball(P.X(6), P.Y(95), GR, 13, fade(2)))
o.append(label(P.X(6) - 200, P.Y(95) - 18, "6시간 → 95점", GR, 30, fade(2)))
o.append(note(1230, 850, 600, "수업 메모의 '6시간 96점'은 오타예요. predict 결과는 95.0이에요.", GRAY, 24, fade(3)))
W("recap", o, "먼저 48을 짧게 다시 봐요. 수업 데이터는 학생 5명의 공부 시간과 점수예요. X는 대괄호 두 겹으로 꺼낸 표, y는 한 겹으로 꺼낸 한 줄이에요. LinearRegression으로 fit하면 기울기 w는 10, 절편 b는 35가 나와요. 공부를 한 시간 더 하면 점수가 10점 오르고, 0시간이면 35점이라는 직선이에요. 6시간이면 10 곱하기 6 더하기 35로 95점이에요. 수업 메모에는 96점이라고 적혀 있었는데 predict 결과는 95.0이라 95점이 맞아요. 셀 출력은 수업처럼 f-string으로 소수 둘째 자리까지 찍었어요." + REAL + REAL_D)

o = [sec("recap-mse")] + head(EB1, "틀린 정도는 48의 MSE로 재요: 오차를 제곱해서 평균", K1)
P = Plot(200, 230, 760, 600, (0.4, 5.6), (40, 92))
o += P.axes("공부 시간", "점수", (1, 2, 3, 4, 5), (40, 60, 80))
o.append(P.svg(P.line(10, 35, RED, 5)))
sq = ""
for k, (x_, y_) in enumerate(zip(HRS, SCS)):
    yp = 10 * x_ + 35
    d = abs(P.Y(y_) - P.Y(yp))
    if d:
        sq += f'<rect x="{P.X(x_):.1f}" y="{min(P.Y(y_), P.Y(yp)):.1f}" width="{d:.1f}" height="{d:.1f}" fill="{LC}" fill-opacity="0.16" stroke="{LC}" stroke-width="2"/>'
o.append(P.svg(sq, fade(1)))
o.append(P.svg(P.dots(HRS, SCS, K1, 11, 0.9)))
for k, (x_, y_) in enumerate(zip(HRS, SCS)):
    err = int(y_ - (10 * x_ + 35))
    o.append(label(P.X(x_) - 30, P.Y(y_) + (-58 if err > 0 else 18), f"{err:+d}" if err else "0", LC, 26, fade(1)))
CXR = 1120
rows = [("오차", "+2   -2   0   -2   +2"), ("제곱", "4    4    0    4    4"), ("평균", "(4 + 4 + 0 + 4 + 4) ÷ 5")]
for i, (a, b_) in enumerate(rows):
    o.append(label(CXR, 270 + i * 110, a, GRAY, 30, rise(2 + i)))
    o.append(label(CXR + 120, 270 + i * 110, b_, INK, 32, rise(2 + i), mono=True))
o.append(p(f"position:absolute;left:{CXR}px;top:620px;font-family:{MONO};font-size:120px;font-weight:900;line-height:1;color:{LC}", "3.2", COUNT(5)))
o.append(label(CXR + 260, 670, "= MSE", LC, 40, fade(5)))
o.append(caption("MSE가 작을수록 직선이 점에 잘 맞아요. 오늘은 이 숫자를 줄여 가는 방법을 봐요.", 950, 6))
W("recap-mse", o, "직선이 얼마나 틀렸는지는 48에서 배운 MSE로 재요. 점마다 직선과의 세로 거리가 오차예요. 5명의 오차는 플러스 2, 마이너스 2, 0, 마이너스 2, 플러스 2예요. 오차를 제곱하면 4, 4, 0, 4, 4이고, 그림의 빨간 네모 넓이예요. 이 다섯 개의 평균이 3.2이고, 앞 장 셀 출력의 MSE 3.2000과 같아요. 제곱하는 이유는 위로 틀린 것과 아래로 틀린 것이 서로 지워지지 않게 하려는 거예요. MSE가 작을수록 직선이 점에 잘 맞아요." + REAL_D)

o = [sec("why")] + head(EB1, "공식이 없을 때는 발밑 경사만 보고 한 걸음씩 내려가요", K1)
# left: map, right: fog walk
o.append(f'<div style="position:absolute;left:96px;top:220px;width:820px;height:640px;border-radius:20px;background:#FFFFFF;border:2px solid {LINE}"></div>')
o.append(f'<div style="position:absolute;left:1004px;top:220px;width:820px;height:640px;border-radius:20px;background:#ECEEF2;border:2px solid {LINE}"></div>')
o.append(label(136, 250, "LinearRegression (48)", INK, 34))
o.append(label(136, 300, "지도를 펴고 골짜기 위치를 바로 계산", SUB, 28))
o.append(label(1044, 250, "경사 하강법 (49)", INK, 34))
o.append(label(1044, 300, "안개 속에서 발밑 경사만 보고 한 걸음씩", SUB, 28))
PA = Plot(176, 380, 660, 380, (6, 14), (0, 190))
PB = Plot(1084, 380, 660, 380, (6, 14), (0, 190))
o.append(PA.svg(PA.curve(mse, 6.3, 13.7, "#C9CED8", 5)))
o.append(PA.svg(f'<line x1="{PA.X(10):.1f}" y1="{PA.Y(185):.1f}" x2="{PA.X(10):.1f}" y2="{PA.Y(8):.1f}" stroke="{RED}" stroke-width="4" stroke-dasharray="10 8"/>', WIPE(1)))
o.append(ball(PA.X(10), PA.Y(mse(10)), RED, 16, fade(1)))
o.append(label(PA.X(10) + 26, PA.Y(60), "한 번에 w = 10", RED, 28, fade(1)))
o.append(PB.svg(PB.curve(mse, 6.3, 13.7, "#9AA0AB", 5)))
o.append(f'<div style="position:absolute;left:1004px;top:360px;width:820px;height:420px;background:linear-gradient(90deg, rgba(236,238,242,0.0) 0%, rgba(236,238,242,0.0) 18%, rgba(236,238,242,0.85) 32%, rgba(236,238,242,0.85) 100%)"></div>')
BW_ = walk(0.01, 6.6, 12)
o.append(PB.svg(f'<path id="why-path" d="M ' + " L ".join(f"{PB.X(v):.1f} {PB.Y(mse(v)):.1f}" for v in BW_) + '" fill="none" stroke="none"/>'))
o.append(PB.svg("".join(f'<circle cx="{PB.X(v):.1f}" cy="{PB.Y(mse(v)):.1f}" r="7" fill="{GC}" fill-opacity="0.5"/>' for v in BW_[:-1]), fade(3)))
o.append(ball(PB.X(BW_[-1]), PB.Y(mse(BW_[-1])), GC, 16, PATH(3, "why-path", 2600)))
o.append(label(1044, 790, "직선 모델 말고는 공식이 없는 모델이 대부분이에요", SUB, 26, fade(2)))
o.append(label(136, 790, "직선 모델이라 계산식이 있어요", SUB, 26, fade(1)))
o.append(caption("경사 하강법: 틀린 정도가 줄어드는 쪽으로 w와 b를 조금씩 고치기를 되풀이해요.", 950, 4))
W("why", o, "LinearRegression은 직선 모델이라 가장 잘 맞는 w와 b를 바로 계산하는 공식이 있어요. 지도를 펴고 골짜기 위치를 찾는 것과 같아요. 그런데 뒤에서 배울 많은 모델은 이런 공식이 없어요. 그때는 안개 낀 산에서 내려오는 사람처럼 해요. 멀리는 안 보여도 발밑이 어느 쪽으로 기울었는지는 알 수 있어요. 내리막 쪽으로 한 걸음 가고, 다시 발밑을 보고 또 한 걸음 가요. 이렇게 틀린 정도가 줄어드는 쪽으로 조금씩 고치는 방법이 경사 하강법이에요. 경사는 기울어진 정도, 하강은 내려간다는 뜻이에요." + REAL_D, ("p1", "왜 필요한가"))

o = [sec("big")] + head(EB1, "학습은 네 박자를 1000번 되풀이하는 일이에요", K1)
STEPS4 = [("예측", "지금 w, b로 5명 점수 계산", WC, WCBG), ("손실", "MSE로 틀린 정도 재기", LC, LCBG), ("경사 보기", "어느 쪽이 내리막인지", GC, GCBG), ("고치기", "w, b를 조금 옮기기", BC, BCBG)]
CXc, CYc, R = 960, 560, 270
pos = [(CXc, CYc - R), (CXc + R + 140, CYc), (CXc, CYc + R), (CXc - R - 140, CYc)]
o.append(f'<svg style="position:absolute;left:0;top:0;width:1920px;height:1080px;overflow:visible" viewBox="0 0 1920 1080"><ellipse cx="{CXc}" cy="{CYc}" rx="{R + 10}" ry="{R - 40}" fill="none" stroke="#C9CED8" stroke-width="4" stroke-dasharray="14 10"/></svg>')
for i, ((t, d, c, bg), (x, y)) in enumerate(zip(STEPS4, pos)):
    o.append(f'<div id="b4-{i}"{rise(1)}{DELAY(i * 120)} style="position:absolute;left:{x - 200}px;top:{y - 70}px;width:400px;height:140px;border-radius:18px;background:{bg};border:3px solid {c};display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px">'
             + p(f"font-size:38px;font-weight:900;color:{c}", f"{i + 1}. {e(t)}") + p(f"font-size:24px;color:{INK}", e(d)) + '</div>')
o.append(p(f"position:absolute;left:{CXc - 160}px;top:{CYc - 54}px;width:320px;text-align:center;font-size:30px;font-weight:700;line-height:1.4;color:{INK}", "한 바퀴 = 1 epoch<br><span style='color:#6A7180;font-size:26px'>수업은 1000 바퀴</span>", fade(2)))
o.append(pulse(3, "b4-2"))
o.append(caption("48의 fit은 이 반복을 한 번에 계산으로 끝냈고, 오늘은 반복을 눈으로 따라가요.", 950, 3))
W("big", o, "경사 하강법의 학습은 네 박자예요. 첫째, 지금의 w와 b로 5명의 점수를 예측해요. 둘째, 예측과 정답을 비교해서 MSE로 틀린 정도를 재요. 이 틀린 정도를 손실이라고 불러요. 셋째, w를 어느 쪽으로 옮겨야 손실이 줄어드는지, 곧 경사를 봐요. 넷째, 그쪽으로 w와 b를 조금 옮겨요. 이 한 바퀴를 epoch라고 부르고, 수업 코드는 1000바퀴를 돌아요. 2파트는 셋째 박자인 경사가 무엇인지, 3파트는 넷째 박자에서 얼마나 옮길지를 봐요.")

# ---------- part 2: loss and slope ----------
o = [sec("loss")] + head(EB2, "손실 함수: w와 b를 넣으면 틀린 정도 하나가 나와요", LC)
MX, MY, MW, MH = 700, 300, 520, 330
o.append(f'<div style="position:absolute;left:{MX}px;top:{MY}px;width:{MW}px;height:{MH}px;border-radius:24px;background:{LCBG};border:4px solid {LC};display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px">'
         + p(f"font-size:40px;font-weight:900;color:{LC}", "손실 함수 (MSE)")
         + p(f"font-size:26px;color:{INK};text-align:center;line-height:1.6", "5명 점수를 w × 시간 + b로 예측<br>오차를 제곱해서 평균") + '</div>')
o.append(arrow(110, "#C9CED8", "", f"position:absolute;left:{MX - 150}px;top:{MY + MH / 2 - 15:.0f}px"))
o.append(arrow(110, "#C9CED8", "", f"position:absolute;left:{MX + MW + 40}px;top:{MY + MH / 2 - 15:.0f}px"))
o.append(label(MX - 520, MY - 70, "넣는 값", GRAY, 28))
o.append(label(MX + MW + 190, MY - 70, "나오는 값", GRAY, 28))
EX = [("w = 0", "b = 0", "4428.2", "SGDRegressor가 출발하는 자리"), ("w = 8", "b = 35", "47.2", ""), ("w = 10", "b = 35", "3.2", "LinearRegression이 찾은 자리")]
for i, (a, b_, v, d) in enumerate(EX):
    y = MY + 10 + i * 125
    o.append(f'<div{rise(1 + i)}{DIM("lossrows")} style="position:absolute;left:{MX - 560}px;top:{y}px;width:400px;display:flex;flex-direction:row;gap:14px">'
             + chip(a, WC, WCBG, 28) + chip(b_, BC, BCBG, 28) + '</div>')
    o.append(p(f"position:absolute;left:{MX + MW + 190}px;top:{y - 6}px;font-family:{MONO};font-size:{52 if i == 2 else 40}px;font-weight:900;line-height:1.2;color:{LC}", v, rise(1 + i) + DIM("lossrowsv")))
    if d:
        o.append(p(f"position:absolute;left:{MX + MW + 190}px;top:{y + (70 if i == 2 else 56)}px;font-size:22px;color:{GRAY};white-space:nowrap", e(d), rise(1 + i) + DIM("lossrowsd")))
CFS[0] = 24
o += cell({"id": "c-zero", "lines": ['pred = 0 * df["hours"] + 0', 'print("w = 0, b = 0 일 때 MSE =", round(mean_squared_error(y, pred), 1))'], "n": 6,
           "out": ["w = 0, b = 0 일 때 MSE = 4428.2"]}, 96, 720, 1240, attrs=fade(4))
o.append(caption("손실이 작을수록 좋은 w와 b예요. 학습은 손실을 줄이는 w와 b를 찾는 일이에요.", 950, 5))
W("loss", o, "손실 함수는 w와 b를 넣으면 틀린 정도를 숫자 하나로 돌려주는 계산이에요. 오늘은 48에서 배운 MSE를 손실 함수로 써요. 손실은 잃어버린 정도라는 뜻이라, 작을수록 좋아요. w 0, b 0을 넣으면 모든 학생을 0점으로 예측하니 MSE가 4428.2로 아주 커요. 뒤에서 볼 SGDRegressor가 바로 이 자리에서 출발해요. w 8, b 35는 47.2이고, LinearRegression이 찾은 w 10, b 35는 3.2예요. 학습이란 이 손실을 가장 작게 만드는 w와 b를 찾는 일이에요. 아래 셀은 w 0, b 0일 때를 직접 계산한 결과예요." + REAL, ("p2", "손실과 경사"))

o = [sec("table")] + head(EB2, "b를 35로 두고 w만 바꾸면 MSE가 47.2, 14.2, 3.2, 14.2, 47.2", LC)
CFS[0] = 28
o += cell({"id": "c-tab", "lines": TABC, "n": 7, "out": TABO}, 96, 210, 960, sel="c-tab")
o.append(f'<div{fade(2)} style="position:absolute;left:{96 + 85}px;top:{oy(210, 4, 2) - LH() / 2 - 4:.0f}px;width:520px;height:{LH() + 8:.0f}px;border-radius:8px;background:rgba(163,49,49,0.12)"></div>')
o.append(tag(96 + 85 + 520 + 24, oy(210, 4, 2), "가장 작아요", LC, 2, 28))
o.append(tag(96 + 85 + 520 + 24, oy(210, 4, 0), "w가 2 작아도", GRAY, 3, 26))
o.append(tag(96 + 85 + 520 + 24, oy(210, 4, 4), "2 커도 똑같이 47.2", GRAY, 3, 26))
P = Plot(1180, 250, 620, 560, (0, 5.8), (30, 105))
o += P.axes("공부 시간", "점수", (1, 2, 3, 4, 5), (40, 60, 80, 100))
o.append(P.svg(P.line(8, 35, "#9AA0AB", 4, "12 9"), fade(1)))
o.append(P.svg(P.line(12, 35, "#9AA0AB", 4, "12 9"), fade(1)))
o.append(P.svg(P.line(10, 35, RED, 6), WIPE(2)))
o.append(P.svg(P.dots(HRS, SCS, K1, 11, 0.9)))
o.append(label(P.X(5.8) + 12, P.Y(12 * 5.8 + 35) - 18, "w = 12", GRAY, 26, fade(1)))
o.append(label(P.X(5.8) + 12, P.Y(8 * 5.8 + 35) - 18, "w = 8", GRAY, 26, fade(1)))
o.append(label(P.X(5.8) + 12, P.Y(10 * 5.8 + 35) - 18, "w = 10", RED, 26, fade(2)))
o.append(caption("절편은 그대로 두고 기울기만 돌려 보면 손실이 줄었다가 다시 늘어요.", 950, 4))
W("table", o, "손실이 w에 따라 어떻게 바뀌는지 직접 계산해 봐요. 절편 b는 35로 고정하고 기울기 w만 8부터 12까지 바꿨어요. 반복문 안에서 w 곱하기 공부 시간 더하기 35로 예측하고, 48의 mean_squared_error로 MSE를 구해요. w가 10일 때 3.2로 가장 작고, 8이나 12처럼 2만큼 벗어나면 똑같이 47.2예요. 오른쪽 그림처럼 w 8과 12의 직선은 점에서 멀어지고, 10의 직선이 점 사이를 지나가요. 점에서 멀어질수록 오차가 커지고, 제곱하면 더 빨리 커져요." + REAL + REAL_D)

o = [sec("ushape")] + head(EB2, "w와 MSE를 그래프로 그리면 바닥이 하나인 U자가 나와요", LC)
CFS[0] = 20
o += cell({"id": "c-u", "lines": UC, "n": 8}, 96, 200, 960, sel="c-u")
o.append(tag(tx(96, UC[0:1]) - 10, ly(200, 0), "6.0, 6.5, ... 14.0", GRAY, 1, 24))
IX, IWD = 1090, 740
o.append(img(IX, 196, IWD, "main-1.png", fade(2), "u-img"))
UIW = IWD / 1240
o.append(ring(3, IX + 600 * UIW, 196 + 610 * UIW, 140 * UIW, 90 * UIW, LC, 6))
o.append(label(IX + 560 * UIW, 196 + 520 * UIW - 30, "w 10, MSE 3.2", LC, 26, fade(3)))
QX, QY = 136, 640
o.append(label(QX, QY, "2차함수는 '제곱이 들어간 계산'의 그래프예요", INK, 30, rise(4)))
SQ = [(-2, 4), (-1, 1), (0, 0), (1, 1), (2, 4)]
for i, (x_, y_) in enumerate(SQ):
    bx = QX + i * 150
    o.append(bar(bx + 40, QY + 250 - y_ * 40, 60, y_ * 40 + 4, "#E7B3B3" if y_ else LC, rise(5) + DELAY(i * 70), 6))
    o.append(p(f"position:absolute;left:{bx}px;top:{QY + 262}px;width:140px;text-align:center;font-family:{MONO};font-size:24px;color:{INK}", f"({x_})²={y_}" if x_ < 0 else f"{x_}²={y_}", rise(5) + DELAY(i * 70)))
o.append(caption("오차를 제곱해서 평균 내니까, 손실 그래프는 가운데가 가장 낮은 U자 모양이에요.", 950, 6))
W("ushape", o, "w를 6부터 14까지 0.5씩 바꿔 가며 MSE를 계산하고 그래프로 그렸어요. 첫 줄은 23에서 배운 컴프리헨션이에요. range로 12부터 28까지 세고 2로 나눠서 6.0, 6.5처럼 0.5 간격을 만들어요. 둘째 줄은 w마다 MSE를 하나씩 계산해 리스트에 담아요. 그래프는 바닥이 하나인 U자 모양이고, 바닥이 w 10, MSE 3.2예요. 수학에서는 이런 그래프를 2차함수라고 불러요. 어려운 말 같지만 제곱이 들어간 계산의 그래프라는 뜻이에요. 아래 막대처럼 마이너스 2부터 2까지 제곱하면 4, 1, 0, 1, 4로 가운데가 가장 낮아요. MSE도 오차를 제곱하니까 같은 모양이에요. 손실 그래프를 산, 바닥을 골짜기라고 부르기도 해요." + REAL + IMGN)

o = [sec("two")] + head(EB2, "'기울기'가 두 번 나와요: 직선의 기울기 w와 손실의 기울기", INK)
o.append(f'<div style="position:absolute;left:96px;top:200px;width:840px;height:8px;border-radius:4px;background:{WC}"></div>')
o.append(f'<div style="position:absolute;left:984px;top:200px;width:840px;height:8px;border-radius:4px;background:{GC}"></div>')
o.append(label(96, 226, "기울기 w (직선의 기울기)", WC, 36))
o.append(label(984, 226, "손실의 기울기 (경사)", GC, 36, fade(2)))
P = Plot(196, 330, 660, 400, (0, 5.8), (30, 105))
o += P.axes("공부 시간", "점수", (1, 2, 3, 4, 5), (40, 60, 80, 100), 20)
o.append(P.svg(P.line(10, 35, WC, 5)))
o.append(P.svg(P.dots(HRS, SCS, "#9AA0AB", 9, 0.8)))
o.append(P.svg(f'<path d="M {P.X(2):.1f} {P.Y(55):.1f} L {P.X(3):.1f} {P.Y(55):.1f} L {P.X(3):.1f} {P.Y(65):.1f}" fill="none" stroke="{WC}" stroke-width="4"/>', WIPE(1)))
o.append(label(P.X(2.15), P.Y(55) + 8, "1시간", WC, 24, fade(1)))
o.append(label(P.X(3) + 14, P.Y(60) - 16, "+10점", WC, 24, fade(1)))
U = Plot(1084, 330, 660, 400, (6, 14), (0, 190))
o += U.axes("기울기 w", "MSE", (6, 8, 10, 12, 14), (0, 50, 100, 150), 20)
o.append(U.svg(U.curve(mse, 6.2, 13.8, LC, 5), fade(2)))
o.append(U.svg(U.tangent(mse, 8, 1.4, GC, 6), fade(3)))
o.append(ball(U.X(8), U.Y(mse(8)), GC, 12, fade(3)))
o.append(label(U.X(8) + 40, U.Y(mse(8)) - 10, "w = 8에서 -44", GC, 26, fade(3)))
rows2 = [(WC, ["점수 그래프의 직선", "공부 1시간에 점수가 몇 점 오르나", "model.coef_ 로 꺼내요"]),
         (GC, ["손실(MSE) 그래프의 접선", "w를 1 늘리면 손실이 얼마나 바뀌나", "모델이 안에서 계산해요"])]
for k, (c, lines_) in enumerate(rows2):
    for j, t in enumerate(lines_):
        o.append(p(f"position:absolute;left:{96 + k * 888}px;top:{790 + j * 46}px;width:840px;font-size:28px;font-weight:{700 if j == 0 else 400};color:{c if j == 0 else INK};font-family:{SANS}", e(t).replace("model.coef_ ", f"<span style='font-family:{MONO}'>model.coef_</span>"), fade(1 if k == 0 else 3)))
W("two", o, "학생들이 가장 헷갈려하는 부분이에요. 기울기라는 말이 두 곳에서 나와요. 왼쪽 파란색은 직선의 기울기 w예요. 점수 그래프 위의 직선이 얼마나 기울었는지, 곧 공부 1시간에 점수가 10점 오른다는 뜻이고 48의 coef_로 꺼내요. 오른쪽 주황색은 손실의 기울기예요. 가로축이 w, 세로축이 MSE인 손실 그래프에서 지금 자리에 자를 댔을 때 얼마나 기울었는지예요. w가 8인 자리에서는 마이너스 44라서, w를 늘리면 손실이 줄어드는 내리막이에요. 경사 하강법의 경사가 바로 이 손실의 기울기예요. 이 덱에서는 직선 쪽은 늘 파란색 기울기 w, 손실 쪽은 늘 주황색 경사로 부를게요." + REAL_D)

o = [sec("tangent")] + head(EB2, "미분은 그 자리에 댄 자가 얼마나 기울었는지예요", GC)
U = Plot(200, 250, 740, 560, (6, 14), (0, 190))
o += U.axes("기울기 w", "MSE", (6, 8, 10, 12, 14), (0, 50, 100, 150))
o.append(U.svg(U.curve(mse, 6.2, 13.8, LC, 5)))
TG = [(8, "-44", "내리막: w를 늘려요"), (10, "0", "평평: 바닥이에요"), (12, "+44", "오르막: w를 줄여요")]
for i, (wv, sv, d) in enumerate(TG):
    o.append(U.svg(U.tangent(mse, wv, 1.3, GC, 7), WIPE(1 + i)))
    o.append(ball(U.X(wv), U.Y(mse(wv)), GC, 12, fade(1 + i)))
    lx = U.X({8: 7.25, 10: 9.2, 12: 11.0}[wv])
    ly_ = U.Y({8: 135, 10: 62, 12: 135}[wv])
    o.append(p(f"position:absolute;left:{lx:.0f}px;top:{ly_:.0f}px;font-size:30px;font-weight:900;line-height:1.3;color:{GC};white-space:nowrap", f"경사 {sv}<br><span style='font-size:22px;font-weight:700;color:{SUB}'>{e(d)}</span>", fade(1 + i) + DELAY(150)))
CFS[0] = 22
CFS[0] = 19
o += cell({"id": "c-slope", "lines": SLOPEC, "n": 10, "out": SLOPEO}, 1010, 250, 814, sel="c-slope", attrs=fade(4))
o.append(tag(1010 + 105, cbot(250, 3) + 180, "0.001만 움직여 보고 MSE 차이를 0.001로 나눴어요", GC, 4, 22, lead=False, w=640))
o.append(caption("경사가 마이너스면 오른쪽이 내리막, 플러스면 왼쪽이 내리막이에요.", 950, 5))
W("tangent", o, "미분이라는 말도 식 없이 그림으로 봐요. U자 그래프의 한 점에 자를 대면, 그 자가 얼마나 기울었는지가 그 자리의 경사예요. 이 경사를 구하는 일을 미분이라고 불러요. w 8에서는 자가 오른쪽 아래로 기울어서 마이너스 44예요. 오른쪽으로 가면 내려간다는 뜻이라 w를 늘려야 해요. w 10은 바닥이라 자가 평평하고 경사가 0이에요. w 12에서는 플러스 44라 왼쪽이 내리막이고 w를 줄여야 해요. 오른쪽 셀은 컴퓨터가 경사를 어떻게 알 수 있는지 보여 줘요. w를 0.001만 움직여 보고 MSE가 얼마나 바뀌었는지를 0.001로 나누면 그 자리의 경사가 나와요. 앞 장에서 만든 loss 함수를 썼고, 다음 장에서 그 함수를 봐요." + REAL + REAL_D)

o = [sec("step")] + head(EB2, "경사의 반대쪽으로 한 걸음: 새 w = w - 학습률 × 경사", GC)
o.append(strip_code(96, 220, 1728, 150, [("새 w", WC, None), (" = ", W_, None), ("w", WC, None), (" - ", W_, None), ("학습률", "#C9B6F2", None), (" × ", W_, None), ("경사", "#F2C46D", None)], 64))
o.append(strip_code(96, 400, 1728, 150, [("8.44", WC, "st-new"), (" = ", W_, None), ("8", WC, None), (" - ", W_, None), ("0.01", "#C9B6F2", None), (" × ", W_, None), ("(-44)", "#F2C46D", None)], 64, rise(1)))
o.append(label(1300, 448, "= 8 + 0.44", "#BFC6D4", 40, fade(2), mono=True))
U = Plot(220, 640, 640, 260, (7, 11), (0, 80))
o.append(U.svg(U.curve(mse, 7.4, 10.6, LC, 5), fade(3)))
o.append(U.svg(f'<line x1="{U.X(8):.1f}" y1="{U.Y(mse(8)) - 40:.1f}" x2="{U.X(8.44) - 6:.1f}" y2="{U.Y(mse(8)) - 40:.1f}" stroke="{GC}" stroke-width="5" marker-end="url(#ah)"/><defs><marker id="ah" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="{GC}"/></marker></defs>', fade(3)))
o.append(ball(U.X(8), U.Y(mse(8)), "#C9CED8", 11, fade(3)))
o.append(ball(U.X(8.44), U.Y(mse(8.44)), GC, 13, fade(3)))
o.append(label(U.X(8) - 40, U.Y(mse(8)) - 100, "8에서 8.44로", GC, 26, fade(3)))
o.append(p(f"position:absolute;left:980px;top:640px;width:840px;font-size:30px;line-height:1.7;color:{INK}", "경사가 <b style='color:#B26A00'>마이너스</b>면 빼기의 빼기라 w가 <b>커져요</b>.<br>경사가 <b style='color:#B26A00'>플러스</b>면 w가 <b>작아져요</b>.<br>바닥(경사 0)에서는 <b>멈춰요</b>.", rise(4)))
o.append(p(f"position:absolute;left:980px;top:850px;width:840px;font-size:26px;line-height:1.5;color:{SUB}", "학습률은 한 걸음의 크기예요. 3파트에서 자세히 봐요.", fade(4)))
W("step", o, "경사를 알았으니 한 걸음 옮겨 봐요. 규칙은 한 줄이에요. 새 w는 지금 w에서 학습률 곱하기 경사를 뺀 값이에요. w 8에서 경사는 마이너스 44였어요. 학습률을 0.01로 두면 0.01 곱하기 마이너스 44는 마이너스 0.44이고, 빼기의 빼기라서 8에 0.44를 더해 8.44가 돼요. 오른쪽, 곧 내리막으로 한 걸음 간 거예요. 경사가 플러스였다면 w가 줄어서 왼쪽으로 가요. 경사가 0인 바닥에서는 더 움직이지 않아요. 경사의 반대쪽으로 가니까 늘 내리막으로 가는 거예요. 학습률은 걸음의 크기인데 3파트에서 자세히 봐요. 수업 코드의 SGDRegressor도 안에서 이 규칙으로 w와 b를 같이 고쳐요." + REAL_D)

o = [sec("walk")] + head(EB2, "손으로 다섯 걸음: w가 8에서 9.42로, MSE가 47.2에서 6.87로", GC)
CFS[0] = 22
o += cell({"id": "c-lossf", "lines": LOSSC, "n": 9, "out": ["47.2 3.2 47.2"]}, 96, 196, 860)
o += cell({"id": "c-step", "lines": STEPC, "n": 11, "out": STEPO}, 96, 480, 1728, sel="c-step")
o.append(tag(tx(96, LOSSC[0:1]) - 10, ly(200, 0), "19의 함수: w를 넣으면 MSE를 돌려줘요", GRAY, 1, 20))
o.append(lspot(2, 96 + 87, 480, 1728 - 89, 20 + 5 * LH(), ly(480, 3) - LH() / 2, LH()))
o.append(lspot_off(3))
U = Plot(1160, 200, 640, 200, (7.6, 10.4), (0, 68))
o += U.axes("기울기 w", "MSE", (8, 9, 10), (0, 50), 18)
o.append(U.svg(U.curve(mse, 7.7, 10.3, LC, 5)))
WK = walk(0.01, 8.0, 5)
o.append(U.svg(f'<path id="walk-path" d="M ' + " L ".join(f"{U.X(v):.1f} {U.Y(mse(v)):.1f}" for v in WK) + '" fill="none" stroke="none"/>'))
o.append(U.svg("".join(f'<circle cx="{U.X(v):.1f}" cy="{U.Y(mse(v)):.1f}" r="8" fill="{GC}" fill-opacity="0.45"/>' for v in WK[:-1]), fade(3)))
o.append(ball(U.X(WK[-1]), U.Y(mse(WK[-1])), GC, 14, PATH(3, "walk-path", 2200)))
o.append(label(U.X(8) + 24, U.Y(mse(8)) - 20, "출발 8", GRAY, 22, fade(3)))
o.append(label(U.X(WK[-1]) + 16, U.Y(mse(WK[-1])) - 46, "9.42", GC, 24, fade(3)))
o.append(caption("바닥에 가까워질수록 경사가 작아져서 걸음도 짧아져요.", 960, 4))
W("walk", o, "경사 하강법을 직접 다섯 걸음 걸어 봐요. 먼저 19에서 배운 함수로 loss를 만들어요. w를 넣으면 b를 35로 두고 MSE를 돌려줘요. 아래 셀은 w 8에서 출발해서 반복할 때마다 앞 장의 방법으로 경사를 구하고, 새 w는 w 빼기 0.01 곱하기 경사로 바꿔요. 첫 걸음에 경사 마이너스 44로 8.44가 되고, 다섯 걸음 뒤에는 9.42, MSE는 6.87까지 줄었어요. 바닥에 가까워질수록 경사가 작아져서 걸음도 저절로 짧아져요. 계속 걸으면 10에 거의 닿아요. 실제 모델은 b도 같은 방법으로 함께 고쳐요. 손으로 쓴 이 셀은 이해를 돕는 연습이고 수업 노트북에는 없어요." + REAL + REAL_D)


# ---------- part 3: learning rate ----------
LRC_ = PUR
o = [sec("lr")] + head(EB3, "학습률은 한 걸음의 크기예요: 0.002, 0.01, 0.1로 다섯 걸음", LRC_)
CFS[0] = 22
o += cell({"id": "c-lrs", "lines": LRSC, "n": 12, "out": LRSO}, 96, 196, 1040, sel="c-lrs")
o.append(hl(96, 196, 1040, 5, 1, "mark", 1, "보폭"))
TX3 = tx(96, LRSO, out=True)
for j, (t, c) in enumerate([("너무 느려요: 다섯 걸음에 8.4", GRAY), ("알맞아요: 9.42까지", GR), ("바닥을 넘어 왔다 갔다 해요", RED)]):
    o.append(tag(TX3, oy(196, 8, j), t, c, 2, 26))
for k, (lr_, t, c) in enumerate([(0.002, "0.002: 너무 느려요", GRAY), (0.01, "0.01: 알맞아요", GR), (0.1, "0.1: 너무 커요", RED)]):
    MP = Plot(150 + k * 590, 690, 470, 190, (5.5, 15.5), (0, 300))
    pts = walk(lr_, 8.0, 5)
    o.append(f'<div{rise(3)}{DELAY(k * 150)} style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none">'
             + label(MP.l - 40, 650, t, c, 28)
             + MP.svg(MP.curve(mse, 5.6, 15.1, "#D9A9A9", 4)
                      + f'<path d="M ' + " L ".join(f"{MP.X(v):.1f} {MP.Y(mse(v)):.1f}" for v in pts) + f'" fill="none" stroke="{GC}" stroke-width="3"/>'
                      + "".join(f'<circle cx="{MP.X(v):.1f}" cy="{MP.Y(mse(v)):.1f}" r="{6 if i < 5 else 10}" fill="{GC}" fill-opacity="{0.5 if i < 5 else 1}"/>' for i, v in enumerate(pts)))
             + '</div>')
o.append(caption("보폭이 작으면 오래 걸리고, 크면 바닥을 넘어가요. 알맞은 크기를 골라야 해요.", 950, 4))
W("lr", o, "새 w는 w 빼기 학습률 곱하기 경사였어요. 학습률은 한 번에 얼마나 크게 걸을지 정하는 숫자, 곧 보폭이에요. 앞 장의 다섯 걸음을 학습률만 바꿔서 다시 걸어 봐요. 0.002는 다섯 걸음에 8.4까지밖에 못 가서 너무 느려요. 0.01은 9.42까지 차근차근 내려가요. 0.1은 첫 걸음에 바닥 10을 지나 12.4까지 가고, 다음에는 7.12로 돌아오며 왔다 갔다 해요. 아래 그림의 주황 선이 다섯 걸음의 길이에요. 보폭이 너무 작으면 오래 걸리고, 너무 크면 바닥을 넘어가서 오히려 멀어져요. 이 셀도 이해를 돕는 연습이에요." + REAL + REAL_D, ("p3", "학습률"))

o = [sec("lr-sgd")] + head(EB3, "SGDRegressor에서는 학습률을 eta0라고 불러요: 0.5면 숫자가 터져요", LRC_)
CFS[0] = 20
o.append(note(1260, 200, 560, "학습률만 바꿔서 1000 epoch 학습하는 함수예요. 안의 코드는 4파트에서 한 줄씩 봐요.", INK, 26, fade(1)))
o.append(note(1260, 340, 560, "eta는 그리스 문자 η(에타)예요. 학습률을 적을 때 자주 쓰는 글자이고, 0은 처음 값이라는 뜻이에요.", SUB, 24, fade(1)))
o += cell({"id": "c-train", "lines": TRAINC, "n": 4}, 96, 196, 1130)
o.append(tint(1, cx(96, "                         ") - 4, ly(196, 2) - LH() / 2, tw("eta0=eta") + 8, LH(), LRC_))
ET = cbot(196, 8) + 30
o += cell({"id": "c-eta", "lines": ETAC, "n": 5, "out": ETAO, "red": (3,)}, 96, ET, 1728, sel="c-eta")
TX4 = tx(96, ETAO[:3], out=True)
for j, (t, c) in enumerate([("너무 느려요: 1000번 해도 MSE 33", GRAY), ("알맞아요: LinearRegression의 3.2와 거의 같아요", GR), ("바닥을 못 찾고 MSE 54에서 멈춰요", "#B26A00")]):
    o.append(tag(TX4, oy(ET, 3, j), t, c, 2, 24))
o.append(box(3, 96 + 85 + 8, oy(ET, 3, 3) - LH() / 2 - 4, tw(ETAO[3]) + 28, LH() + 8, RED, 4))
o.append(tag(cx(96, ETAO[3], True) + 40, oy(ET, 3, 3) + 50, "w가 1222억: 오류 없이 터졌어요", RED, 3, 26, lead=False))
o.append(caption("오류가 안 나도 MSE가 줄지 않거나 터지면 eta0부터 바꿔 봐요.", 950, 4))
W("lr-sgd", o, "이번에는 진짜 SGDRegressor로 학습률을 바꿔 봐요. 위 셀은 19의 함수로, 학습률 eta를 받아 1000 epoch 학습한 모델과 epoch마다의 MSE 리스트를 돌려줘요. SGDRegressor에서는 학습률을 eta0라는 이름으로 넣어요. 0.001은 1000번을 돌아도 MSE가 33이라 아직 내려가는 중이에요. 0.01은 3.25로 LinearRegression의 3.2와 거의 같아요. 0.1은 54에서 멈춰서 더 줄지 않아요. 보폭이 커서 바닥 근처를 계속 넘나드는 거예요. 0.5는 w가 1222억, MSE가 e 플러스 24, 곧 0이 24개 붙은 숫자가 돼요. 오류 메시지는 하나도 안 나와요. 그래서 MSE를 꼭 찍어 봐야 해요. 이 비교는 수업 노트북에 없어서 새 노트북에서 import, 글꼴, 데이터 셀 다음에 실행했어요." + REAL)

o = [sec("lr-chart")] + head(EB3, "그래프로 보면 0.01만 바닥까지 내려가요", LRC_)
CFS[0] = 18
o += cell({"id": "c-ech", "lines": ETACH, "n": 6}, 96, 196, 820, sel="c-ech")
o.append(tag(tx(96, ETACH[4:5]) - 10, ly(196, 4), "세로축 0~200만", GRAY, 1, 22))
IW3 = 880
o.append(img(944, 196, IW3, "eta-1.png", fade(1), "eta-img"))
IH3 = int(IW3 * 939 / 1699)
for k, (t, c) in enumerate([("0.01: 3.25까지 내려가요", "#D9620B"), ("0.1: 54에서 멈춰요", "#2E8B2E"), ("0.001: 아직 내려가는 중", "#1F77B4")]):
    o.append(label(944 + k * 300, 196 + IH3 + 10, t, c, 22, fade(2) + DELAY(k * 150)))
BT = 196 + IH3 + 66
CFS[0] = 22
o += cell({"id": "c-big", "lines": ["m, losses = train(0.5)", "print(losses[:5])"], "n": 7,
           "out": ["[172149912.2151003, 879515344619.9103, 4486687432513745.0, 2.288753442431855e+19, 1.1675408295109558e+23]"], "red": (0,)}, 96, BT, 1728, attrs=rise(3))
o.append(underline(4, cx(96, "[172149912.2151003, 879515344619.9103, 4486687432513745.0, 2.288753442431855e+19, ", True), cx(96, "[172149912.2151003, 879515344619.9103, 4486687432513745.0, 2.288753442431855e+19, 1.1675408295109558e+23", True), oy(BT, 2, 0) + 18, RED, 5))
o.append(tag(96 + 105, oy(BT, 2, 0) + 58, "0.5는 epoch마다 MSE가 수백 배씩 커져요. 다섯 번째에 e+23이에요.", RED, 4, 24, lead=False))
W("lr-chart", o, "세 학습률의 MSE를 epoch마다 그래프로 그렸어요. 반복문으로 train을 세 번 부르고, 같은 그래프 칸에 선 세 개를 그려요. label을 적고 legend를 부르면 47처럼 범례가 나와요. 처음 MSE가 아주 커서 세로축을 set_ylim으로 0부터 200까지만 보이게 했어요. 주황 0.01은 바닥까지 내려가요. 초록 0.1은 금방 내려오다가 54에서 평평해져요. 파랑 0.001은 1000번 끝까지 천천히 내려가는 중이에요. 0.5는 그래프에 넣지 않고 처음 다섯 epoch의 MSE만 찍었어요. 1억 7천만에서 시작해서 매번 수백 배씩 커져요. 학습률은 10배씩 바꿔 보는 게 보통이에요. 터지면 10배 작게, 너무 느리면 10배 크게 해 봐요." + REAL + IMGN)

# ---------- part 4: SGDRegressor ----------
o = [sec("sgd")] + head(EB4, "SGDRegressor: 경사 하강법으로 직선을 찾는 scikit-learn 모델", GR)
SGDW = [("S", "Stochastic", "확률적: 한 명씩 보고", BC), ("G", "Gradient", "경사: 손실의 기울기", GC), ("D", "Descent", "하강: 내려가기", LC)]
row = [f'<div{STAGGER(1, 160)} style="position:absolute;left:96px;top:200px;width:1728px;height:200px;display:flex;flex-direction:row;gap:40px">']
for L_, en, ko, c in SGDW:
    row.append(f'<div style="flex:1;display:flex;flex-direction:row;align-items:center;gap:26px;border-bottom:4px solid {c}">'
               + p(f"font-size:130px;font-weight:900;line-height:1;color:{c}", L_)
               + '<div style="display:flex;flex-direction:column;gap:6px">' + p(f"font-size:34px;font-weight:700;color:{INK}", en) + p(f"font-size:28px;color:{SUB}", e(ko)) + '</div></div>')
row.append('</div>')
o.append("".join(row))
o.append(label(96, 410, "Regressor: 점수처럼 숫자를 맞히는 모델 (회귀)", GRAY, 26, fade(1)))
STU = ["1h 47점", "2h 53점", "3h 65점", "4h 73점", "5h 87점"]
for k, (ttl, sub_, c) in enumerate([("배치 경사 하강법", "5명을 다 보고 경사 평균으로 한 걸음", GRAY), ("확률적 경사 하강법 (SGD)", "한 명 볼 때마다 한 걸음씩, 다섯 걸음", GR)]):
    X0 = 96 + k * 888
    blk = [f'<div{rise(2 + k)} style="position:absolute;left:{X0}px;top:480px;width:840px;height:420px;border-radius:20px;background:#FFFFFF;border:2px solid {LINE}">']
    blk.append(p(f"position:absolute;left:36px;top:26px;font-size:34px;font-weight:900;color:{c}", e(ttl)))
    blk.append(p(f"position:absolute;left:36px;top:80px;font-size:26px;color:{SUB}", e(sub_)))
    for i, s_ in enumerate(STU):
        blk.append(p(f"position:absolute;left:{36 + i * 156}px;top:150px;width:140px;height:60px;border-radius:12px;background:#F1F0EC;font-size:24px;font-weight:700;line-height:60px;text-align:center;color:{INK}", e(s_)))
    if k == 0:
        blk.append(f'<div style="position:absolute;left:36px;top:226px;width:764px;height:26px;border:3px solid {GRAY};border-top:none;border-radius:0 0 14px 14px"></div>')
        blk.append(p(f"position:absolute;left:0;top:270px;width:840px;text-align:center;font-size:28px;font-weight:700;color:{GC}", "경사 평균 1개"))
        blk.append(f'<div style="position:absolute;left:330px;top:330px;width:180px;height:56px;border-radius:28px;background:{GC};color:#FFFFFF;font-size:26px;font-weight:700;line-height:56px;text-align:center">한 걸음</div>')
    else:
        for i in range(5):
            blk.append(p(f"position:absolute;left:{36 + i * 156 + 58}px;top:222px;font-size:30px;color:{GRAY}", "↓"))
            blk.append(f'<div style="position:absolute;left:{36 + i * 156 + 20}px;top:270px;width:100px;height:46px;border-radius:23px;background:{GC};color:#FFFFFF;font-size:22px;font-weight:700;line-height:46px;text-align:center">걸음 {i + 1}</div>')
        blk.append(p(f"position:absolute;left:36px;top:340px;width:780px;font-size:24px;color:{SUB}", "shuffle=False라 1번부터 5번 순서 그대로예요."))
    blk.append('</div>')
    o.append("".join(blk))
o.append(caption("수업 데이터는 5명이라 1 epoch에 다섯 걸음을 걸어요.", 950, 4))
W("sgd", o, "오늘의 모델 SGDRegressor를 봐요. 이름이 길지만 앞 세 글자만 알면 돼요. S는 Stochastic, 확률적이라는 뜻으로 데이터를 한 줄씩 골라 본다는 말이에요. G는 Gradient, 2파트에서 본 손실의 기울기, 곧 경사예요. D는 Descent, 내려간다는 뜻이에요. Regressor는 48의 회귀처럼 숫자를 맞히는 모델이라는 뜻이에요. 왼쪽 배치 방식은 5명을 다 보고 경사를 평균 내서 한 걸음 가요. 오른쪽 SGD는 한 명 볼 때마다 그 학생만으로 경사를 구해 한 걸음씩 가요. 그래서 5명이면 한 epoch에 다섯 걸음이에요. 원래는 순서를 섞어서 뽑기 때문에 확률적이라고 부르는데, 수업 코드는 shuffle을 False로 둬서 1번부터 5번 순서대로 봐요. 데이터가 수백만 줄이어도 한 줄씩 보고 바로 고칠 수 있어서 큰 데이터에서 많이 써요.", ("p4", "SGDRegressor로 학습하기"))

o = [sec("args")] + head(EB4, "괄호 안의 값 다섯 개: 손실, 학습률 방식, 학습률, 순서, 시드", GR)
CFS[0] = 24
TXA = tx(96, SGDC[1:6], gap=40)
SGW = TXA - 20 - 96
o += cell({"id": "c-sgd", "lines": SGDC, "n": 13, "out": SGDO}, 96, 196, SGW, sel="c-sgd")
AT = [(1, "48의 MSE를 손실로 써요", LC, 1), (2, "보폭을 줄이지 않고 그대로", LRC_, 1), (3, "학습률(보폭) 0.01", LRC_, 2), (4, "1, 2, 3, 4, 5번 순서 그대로", BC, 3), (5, "47의 시드처럼 늘 같은 결과", GRAY, 3)]
for i, t, c, od in AT:
    o.append(tag(TXA, ly(196, i), t, c, od, 24))
BOXX, BOXW = 96 + 87, SGW - 89
o.append(lspot(1, BOXX, 196, BOXW, 20 + 8 * LH(), ly(196, 1) - LH() / 2, 2 * LH()))
o.append(lspot(2, BOXX, 196, BOXW, 20 + 8 * LH(), ly(196, 3) - LH() / 2, LH()))
o.append(lspot(3, BOXX, 196, BOXW, 20 + 8 * LH(), ly(196, 4) - LH() / 2, 2 * LH()))
o.append(lspot_off(4))
o.append(tag(96 + 105, oy(196, 8, 0) + 44, "기본값과 같은 loss와 eta0는 안 보여요 (25의 __repr__)", GRAY, 4, 22, lead=False))
o.append(fix(96, 680, "eta0=0.01,  # 초기 학습률", "eta0=0.01,  # 학습률", 5, 28))
o.append(note(96 + 60, 760, 1600, "constant라 처음 값이 끝까지 그대로라서 '초기'를 뺐어요. 수업 코드의 max_iter=1000은 partial_fit에서는 쓰이지 않아서 지웠어요.", SUB, 26, fade(5)))
o.append(caption("괄호 안은 모두 이름을 붙여 넣는 키워드 인자예요(20).", 950, 5))
W("args", o, "SGDRegressor의 괄호 안을 하나씩 봐요. 모두 이름을 붙여 넣는 20의 키워드 인자예요. loss는 손실 함수로, squared_error가 48의 MSE와 같은 오차 제곱 평균이에요. learning_rate는 학습률을 다루는 방식이에요. constant는 처음 정한 보폭을 끝까지 그대로 쓴다는 뜻이에요. eta0가 그 보폭, 곧 3파트의 학습률 0.01이에요. shuffle을 False로 두면 매 epoch 1번 학생부터 순서대로 봐요. random_state 42는 47의 시드처럼 처음 값을 정해서 몇 번을 실행해도 같은 결과가 나오게 해요. 마지막 줄 sgd를 실행하면 25에서 배운 repr이 나오는데, 기본값과 같은 loss와 eta0는 생략돼요. 수업 코드는 eta0 주석이 초기 학습률이었는데, constant라 학습률이 바뀌지 않으니 학습률로 고쳤어요. max_iter=1000도 있었는데 partial_fit은 이 값을 쓰지 않아서 지웠어요. 다른 주석도 뜻이 바로 보이게 쉬운 말로 바꿨어요." + REAL)

o = [sec("partial")] + head(EB4, "partial_fit은 딱 한 바퀴(1 epoch)만 배우고, 부르면 이어서 배워요", GR)
o.append(strip_code(96, 200, 1728, 120, [("epoch", "#F2C46D", None), (" = ", W_, None), ("5명을 한 번씩 다 보고 고치는 한 바퀴", W_, None)], 44))
RDX, RDY = 96, 380
o.append(f'<div style="position:absolute;left:{RDX}px;top:{RDY}px;width:1000px;height:420px;border-radius:22px;background:#FFFFFF;border:2px solid {LINE}"></div>')
o.append(label(RDX + 40, RDY + 30, "sgd.partial_fit(X, y)를 부를 때마다", INK, 30, mono=False))
RV = [("rd-ep", "epoch", "1000", "0", INK), ("rd-w", "기울기 w", "10.13", "0.00", WC), ("rd-b", "절편 b", "34.74", "0.00", BC)]
for i, (tid, k, v, v0, c) in enumerate(RV):
    o.append(label(RDX + 60 + i * 320, RDY + 120, k, GRAY, 28))
    o.append(p(f"position:absolute;left:{RDX + 60 + i * 320}px;top:{RDY + 170}px;font-family:{MONO};font-size:72px;font-weight:900;line-height:1.1;color:{c}", v, f' id="{tid}" data-start="{v0}"'))
for od, vals in [(1, ("1", "8.46", "2.73")), (2, ("2", "12.81", "4.27")), (3, ("1000", "10.13", "34.74"))]:
    for (tid, *_), v in zip(RV, vals):
        o.append(text(od, tid, v))
o.append(label(RDX + 60, RDY + 300, "처음에는 w 0, b 0에서 출발해요", SUB, 26))
o.append(p(f"position:absolute;left:1160px;top:{RDY}px;width:664px;font-size:30px;line-height:1.6;color:{INK}", "<b style='color:#1F8A4C'>partial_fit</b>: 한 바퀴만 돌고 멈춰요. 다시 부르면 지금 w, b에서 이어서 한 바퀴 더.<br><br><b>fit</b>: 처음 값부터 다시 시작해서 알아서 여러 바퀴를 돌고 멈춰요.", fade(4)))
o.append(p(f"position:absolute;left:1160px;top:{RDY + 330}px;width:664px;font-size:26px;line-height:1.5;color:{SUB}", "그래서 epoch마다 MSE를 기록하려면 반복문 안에 partial_fit을 써요. fit을 쓰면 5파트에서 볼 함정에 빠져요.", fade(4)))
o.append(caption("1번 부르면 1 epoch, 1000번 부르면 1000 epoch예요.", 950, 4))
W("partial", o, "SGDRegressor에는 학습 메서드가 두 개 있어요. fit은 48처럼 부르면 처음부터 시작해서 알아서 여러 바퀴를 돌고 멈춰요. partial_fit은 데이터 전체를 딱 한 바퀴만 보고 멈춰요. 이 한 바퀴를 epoch라고 불러요. 5명 데이터면 다섯 명을 한 번씩 다 보는 게 1 epoch예요. 다시 partial_fit을 부르면 지금까지 배운 w와 b에서 이어서 한 바퀴를 더 돌아요. 화면처럼 w 0, b 0에서 출발해서 한 번 부르면 w 8.46, b 2.73, 두 번이면 12.81, 4.27, 1000번이면 10.13, 34.74예요. partial은 일부라는 뜻이에요. 수업 코드는 반복문 안에서 partial_fit을 1000번 불러서 epoch마다 결과를 기록해요. 숫자는 다음 장의 history에서 꺼냈어요." + REAL)

o = [sec("loop")] + head(EB4, "1000번 반복하며 epoch마다 w, b, MSE를 딕셔너리로 기록해요", GR)
CFS[0] = 20
o += cell({"id": "c-loop", "lines": LOOPC, "n": 14}, 96, 196, 900, sel="c-loop")
LBX, LBW = 96 + 87, 900 - 89
o.append(run(1, LBX, ly(196, 4) - LH() / 2, LBW, LH()))
o.append(run(2, LBX, ly(196, 6) - LH() / 2, LBW, 2 * LH()))
o.append(run(3, LBX, ly(196, 9) - LH() / 2, LBW, 6 * LH()))
o.append(run_off(4))
o.append(tag(tx(96, LOOPC[4:5]) - 10, ly(196, 4), "한 바퀴 배우기", GR, 1, 22))
o.append(tag(tx(96, LOOPC[6:8]) - 10, ly(196, 7) - LH() / 2, "지금 직선의 MSE", LC, 2, 22))
o.append(tag(tx(96, LOOPC[9:15]) - 10, ly(196, 11), "15의 딕셔너리 하나", BC, 3, 22))
o.append(tag(tx(96, LOOPC[16:17]) - 10, ly(196, 16), "45의 DataFrame으로", K6, 4, 22))
HX = 1060
o.append(mono(HX, 220, ["[{'epoch': 1, 'weight': 8.455..,", "  'bias': 2.731.., 'mse': 1369.8..},", " {'epoch': 2, 'weight': 12.81..,", "  'bias': 4.270.., 'mse': 515.8..},", " ... 1000개]"], 22, 1.5, SUB, rise(3)))
o.append(label(HX, 470, "history: 딕셔너리 1000개가 담긴 리스트", BC, 24, fade(3)))
HR = [("1", "8.455225", "2.731163", "1369.816039"), ("2", "12.813586", "4.270770", "515.808449"), ("3", "15.045308", "5.190714", "269.417813")]
o.append(df("hd", HX, 560, ["epoch", "weight", "bias", "mse"], HR, [90, 160, 150, 180], fs=24, rh=44, iw=40, attrs=rise(4)))
o.append(label(HX + 40, 560 + 44 * 4 + 14, "...  [1000 rows x 4 columns]", GRAY, 22, fade(4), mono=True))
o.append(note(HX, 840, 760, "딕셔너리의 키가 열 이름, 딕셔너리 하나가 한 줄이 돼요.", INK, 26, fade(4)))
W("loop", o, "수업의 반복 셀을 한 줄씩 따라가요. epochs는 1000이고, history는 기록을 모을 빈 리스트예요. 반복할 때마다 partial_fit으로 한 바퀴 배워요. 그다음 지금의 w와 b로 5명 점수를 predict하고, MSE를 구해요. 이 값들을 15에서 배운 딕셔너리 하나로 묶어서 history에 append해요. coef_와 intercept_는 48처럼 배열이라 [0]으로 꺼내요. epoch는 0부터 세니까 1을 더해 1번째부터 적어요. 반복이 끝나면 history에는 딕셔너리 1000개가 담겨요. 45처럼 pd.DataFrame에 넣으면 딕셔너리의 키가 열 이름, 딕셔너리 하나가 한 줄인 표가 돼요. 오른쪽 위 리스트는 history 앞 두 개를 줄여서 옮긴 거예요." + REAL)

o = [sec("history")] + head(EB4, "기록에서 epoch 8개만 골라 보면 MSE가 1369.8에서 3.25로 줄어요", GR)
CFS[0] = 24
o += cell({"id": "c-pick", "lines": PICKC, "n": 15}, 96, 196, 1728, sel="c-pick")
o.append(tint(1, cx(96, 'history_df[history_df["epoch"].'), ly(196, 0) - LH() / 2, tw("isin([1, 5, 10, 50, 100, 300, 500, 1000])"), LH(), BC))
PKT = cbot(196, 1) + 30
PWS = [120, 190, 190, 210]
csx = {}
for i in range(8):
    csx[(i, 1)] = f"color:{WC};font-weight:700"
    csx[(i, 2)] = f"color:{BC};font-weight:700"
    csx[(i, 3)] = f"color:{LC};font-weight:700"
o.append(df("pk", 96 + 105, PKT, ["epoch", "weight", "bias", "mse"], PICKR, PWS, fs=28, rh=64, iw=70, idx=[0, 4, 9, 49, 99, 299, 499, 999], attrs=rise(1), cs=csx))
o.append(box(2, 96 + 105 + 70 + 120 - 6, dfy(PKT, 64, 1) - 2, 190 + 12, 64 * 2 + 4, WC, 4))
o.append(tag(96 + 105 + 70 + sum(PWS) + 60, dfy(PKT, 64, 1) + 64, "w가 17까지 지나쳤다가 돌아와요", WC, 2, 26))
o.append(tag(96 + 105 + 70 + sum(PWS) + 60, dfy(PKT, 64, 7) + 32, "w 10.13, b 34.74, MSE 3.25", LC, 3, 26))
o.append(grow(3, "pk-r7"))
o.append(note(96 + 105, PKT + 64 * 9 + 24, 1600, "isin(목록): 목록 안에 있는 값이면 True예요. 45의 조건으로 고르기와 같아요. 왼쪽 번호는 원래 행 번호라 epoch보다 1 작아요.", SUB, 24, fade(1)))
W("history", o, "1000줄을 다 볼 수는 없으니 epoch 8개만 골라요. isin은 괄호 안 목록에 들어 있는 값이면 True를 돌려줘요. 45에서 배운 조건으로 고르기처럼 True인 줄만 남아요. 왼쪽 번호는 원래 행 번호라 epoch보다 하나 작아요. 처음 MSE는 1369.8로 아주 커요. w는 5 epoch 만에 16.7, 10 epoch에 17.06까지 올라가서 정답 10을 지나쳐요. 그동안 b가 아직 작아서, w를 키워서라도 점수를 맞추려는 거예요. b가 천천히 올라오면서 w는 다시 내려와요. 1000 epoch에는 w 10.13, b 34.74, MSE 3.25로 LinearRegression의 답에 거의 닿아요." + REAL)

o = [sec("curve")] + head(EB4, "학습 곡선: epoch마다 MSE가 줄어드는 그래프", GR)
CFS[0] = 20
o += cell({"id": "c-curve", "lines": CURVEC, "n": 16}, 96, 190, 1728, sel="c-curve")
o.append(tag(tx(96, CURVEC[1:2]) - 10, ly(190, 1), "가로 epoch, 세로 MSE", GRAY, 1, 22))
IW4, IX4, IY4 = 760, 96, 470
o.append(img(IX4, IY4, IW4, "main-2.png", fade(1), "cv-img"))
S4 = IW4 / 1716
o.append(ring(2, IX4 + 200 * S4, IY4 + 80 * S4, 120 * S4, 700 * S4, LC, 5))
o.append(label(IX4 + 340 * S4, IY4 + 300 * S4, "처음 몇 번에 크게 줄고", LC, 24, fade(2)))
o.append(label(IX4 + 900 * S4, IY4 + 700 * S4, "뒤로 갈수록 평평해져요", SUB, 24, fade(2)))
o.append(fix(920, 500, 'plt.xlabel("Loss")', 'plt.xlabel("Epoch")', 3, 26, 900))
o.append(fix(920, 600, '"(Traing Loss)"', '"(Training Loss)"', 4, 26, 900))
o.append(fix(920, 700, "(범례 없음)", "plt.legend()", 5, 26, 900))
o.append(caption("수업 코드의 세 군데를 고쳤어요. 가로축 이름, 오타, 범례예요.", 950, 5))
W("curve", o, "history_df로 그래프를 그려요. 가로축은 epoch, 세로축은 MSE예요. 이런 그래프를 학습 곡선이라고 불러요. 처음 몇 epoch에 1369에서 200 아래로 뚝 떨어지고, 그 뒤로는 천천히 줄다가 평평해져요. 바닥에 가까울수록 경사가 작아서 걸음도 짧아지기 때문이에요. 2파트에서 손으로 걸었을 때와 같은 모양이에요. 수업 코드에서 세 군데를 고쳤어요. 가로축 이름이 Loss로 적혀 있었는데 가로축은 epoch라 Epoch가 맞아요. label의 Traing은 Training의 오타예요. 47에서 배웠듯이 label만 적으면 범례가 안 나와서 plt.legend를 더했어요. 그래프 제목 줄도 하나 더했어요." + REAL + IMGN)

o = [sec("wb")] + head(EB4, "w는 지나쳤다 돌아오고, b는 천천히 올라와요", GR)
CFS[0] = 18
o += cell({"id": "c-wb", "lines": WBC, "n": 17}, 96, 196, 880, sel="c-wb")
o.append(tint(1, cx(96, "fig, axes = plt.subplots(") - 2, ly(196, 0) - LH() / 2, tw("1, 2") + 4, LH(), WC))
o.append(tag(tx(96, WBC[0:1]) - 10, ly(196, 0), "1행 2열", WC, 1, 22))
IW5 = 860
o.append(img(964, 196, IW5, "main-3.png", fade(2), "wb-img"))
S5 = IW5 / 1953
IB = 196 + IW5 * 939 / 1953
o.append(tint(2, cx(96, "") - 2, ly(196, 2) - LH() / 2, tw("axes[0]") + 4, LH(), WC))
o.append(tint(3, cx(96, "") - 2, ly(196, 7) - LH() / 2, tw("axes[1]") + 4, LH(), BC))
o.append(label(964 + 250 * S5, IB + 20, "axes[0]", WC, 24, fade(2), mono=True))
o.append(label(964 + 1450 * S5, IB + 20, "axes[1]", BC, 24, fade(3), mono=True))
o.append(ring(4, 964 + 100 * S5, 196 + 80 * S5, 60 * S5, 60 * S5, WC, 5))
o.append(note(964, IB + 80, 860, "w는 10 epoch쯤 17까지 지나쳤다가 10.13으로 돌아와요. b는 2.73에서 34.74까지 천천히 올라와요.", INK, 26, fade(4)))
W("wb", o, "w와 b가 epoch마다 어떻게 바뀌었는지도 그려요. plt.subplots에 1, 2를 넣으면 그림판 하나에 그래프 칸이 1행 2열로 두 개 생겨요. 47에서는 칸이 하나라 ax로 받았는데, 두 개면 axes라는 이름으로 받고 13의 리스트처럼 axes[0], axes[1]로 꺼내요. 왼쪽 칸에는 weight, 오른쪽 칸에는 bias를 그려요. 왼쪽을 보면 w가 처음에 17까지 확 올라갔다가 천천히 10.13으로 돌아와요. 오른쪽 b는 처음부터 천천히 올라와서 34.74에 닿아요. b가 늦게 올라오는 동안 w가 대신 점수를 맞추느라 지나쳤던 거예요." + REAL + IMGN)

o = [sec("pred")] + head(EB4, "1000 epoch 뒤 6시간 예측은 95.52점, LinearRegression은 95.00점", GR)
CFS[0] = 26
o += cell({"id": "c-pred", "lines": PREDC, "n": 18, "out": PREDO}, 96, 196, 1040, sel="c-pred")
o.append(tag(tx(96, PREDC[3:4]) - 10, ly(196, 3), "48처럼 같은 열 이름의 표", GRAY, 1, 24))
o.append(p(f"position:absolute;left:1220px;top:240px;font-family:{MONO};font-size:150px;font-weight:900;line-height:1;color:{GR}", "95.52", COUNT(2)))
o.append(label(1226, 420, "SGDRegressor, 6시간", GR, 30, fade(2)))
o.append(p(f"position:absolute;left:1226px;top:500px;font-family:{MONO};font-size:72px;font-weight:900;line-height:1;color:{GRAY}", "95.00", rise(3)))
o.append(label(1226, 590, "LinearRegression, 6시간 (1파트)", GRAY, 26, fade(3)))
o.append(note(1226, 660, 600, "차이는 0.52점이에요. w와 b가 공식의 답에 거의 닿았어요.", INK, 28, fade(3)))
o.append(fix(96, 790, "### 최종 모델로 시험 적적 예측하기", "### 최종 모델로 시험 성적 예측하기", 4, 28))
o.append(note(156, 870, 1600, "수업 노트북의 마크다운 제목에 있던 오타 '적적'을 '성적'으로 고쳤어요.", SUB, 24, fade(4)))
W("pred", o, "1000 epoch를 배운 sgd로 예측해요. coef_와 intercept_는 배열이라 [0]으로 꺼내요. 기울기는 10.13, 절편은 34.74예요. predict에는 48처럼 학습 때와 같은 열 이름 hours를 가진 표를 넣어요. 6시간 공부하면 95.52점으로 예측해요. 1파트의 LinearRegression은 95.00점이었으니 차이는 0.52점이에요. 1000 epoch를 배워도 공식의 답과 똑같지는 않지만 거의 닿았어요. 수업 노트북에서 이 셀 위의 마크다운 제목에 '시험 적적 예측하기'라는 오타가 있어서 '성적'으로 고쳤어요." + REAL)

o = [sec("compare")] + head(EB4, "LinearRegression과 SGDRegressor 비교", GR)
CMP = [("찾는 방법", "공식으로 한 번에 계산", "경사를 보고 조금씩 고치기"), ("학습 코드", "model.fit(X, y) 한 번", "partial_fit을 반복문에서"),
       ("정해 줄 값", "없어요", "학습률 eta0, epoch 수"), ("오늘 결과", "w 10.00  b 35.00", "w 10.13  b 34.74"), ("MSE", "3.20", "3.25"),
       ("언제 쓰나", "데이터가 적고 직선 모델일 때", "데이터가 아주 많거나 계속 들어올 때")]
rows_html = plain_rows(96, 210, 1728, CMP, [300, 680, 680], 1, 96, ["", "LinearRegression (48)", "SGDRegressor (49)"], 32)
grp = {1: 1, 2: 1, 3: 1, 4: 2, 5: 2, 6: 3, 7: 3}
rows_html = [re.sub(r"rise order (\d+)", lambda m: f"rise order {grp.get(int(m.group(1)), 3)}", h) for h in rows_html]
rows_html = [re.sub(r"fade order 1", "fade order 1", h) for h in rows_html]
o += rows_html
o.append(f'<div{fade(2)} style="position:absolute;left:{96 + 320}px;top:{210 + 58 + 3 * 96}px;width:1400px;height:{2 * 96}px;border-radius:12px;background:rgba(31,138,76,0.08)"></div>')
o.append(caption("결과는 거의 같아요. 다른 점은 찾아가는 과정이고, 많은 모델은 SGD처럼 배워요.", 950, 4))
W("compare", o, "두 모델을 나란히 봐요. LinearRegression은 공식으로 한 번에 계산해서 fit 한 번이면 끝나고, 정해 줄 값도 없어요. SGDRegressor는 경사를 보고 조금씩 고쳐서, 학습률과 몇 바퀴 돌지를 정해 줘야 해요. 오늘 결과는 w 10과 10.13, b 35와 34.74, MSE 3.2와 3.25로 거의 같아요. 직선 모델이고 데이터가 5명뿐이면 LinearRegression이 더 간단해요. 데이터가 수백만 줄이라 한 번에 계산하기 어렵거나, 새 데이터가 계속 들어와서 이어서 배워야 할 때는 SGD 방식을 써요. 앞으로 배울 많은 모델도 이렇게 손실을 줄이는 쪽으로 조금씩 고쳐 가며 배워요." + REAL)


# ---------- part 5: errors and traps ----------
o = [sec("e-loss")] + head(EB5, 'loss="mse"라고 쓰면 InvalidParameterError가 나요', RED)
CFS[0] = 28
ELO = ["InvalidParameterError: The 'loss' parameter of SGDRegressor must be a str among",
       "{'squared_epsilon_insensitive', 'huber', 'epsilon_insensitive', 'squared_error'}.", "Got 'mse' instead."]
o += cell({"id": "c-eloss", "lines": ['sgd = SGDRegressor(loss="mse")', "sgd.partial_fit(X, y)"], "n": 3, "out": ELO, "err": True, "red": (1, 2)}, 96, 210, 1728, sel="c-eloss")
o.append(underline(1, cx(96, 'sgd = SGDRegressor(loss='), cx(96, 'sgd = SGDRegressor(loss="mse"'), ly(210, 0) + 20, RED, 5))
o.append(box(2, cx(96, "", True) - 8, oy(210, 2, 2) - LH() / 2 - 4, tw("Got 'mse' instead.") + 16, LH() + 8, RED, 4))
o.append(tag(cx(96, "Got 'mse' instead.", True) + 30, oy(210, 2, 2), "mse를 받았다", RED, 2, 26))
o.append(box(3, cx(96, "{'squared_epsilon_insensitive', 'huber', 'epsilon_insensitive', ", True) - 6, oy(210, 2, 1) - LH() / 2 - 4, tw("'squared_error'") + 12, LH() + 8, GR, 4))
o.append(fix(96, 640, 'loss="mse"', 'loss="squared_error"', 4))
o.append(reading(96, 760, "MSE는 채점 함수 이름(mean_squared_error)이고, loss에는 손실 이름 squared_error를 적어요.", INK, 4, 30))
o.append(note(96, 840, 1728, "중괄호 안 네 이름은 집합이라 실행할 때마다 순서가 달라질 수 있어요. 16에서 본 집합 순서와 같아요.", GRAY, 24, fade(4)))
W("e-loss", o, "loss에 mse라고 적으면 InvalidParameterError가 나요. 메시지는 loss 값이 중괄호 안 네 개 중 하나여야 하는데 mse를 받았다는 뜻이에요. 목록에 squared_error가 있어요. MSE는 채점 함수 mean_squared_error의 줄임말이라 헷갈리기 쉬워요. loss에는 손실의 이름인 squared_error를 적어요. 오류는 SGDRegressor를 만들 때가 아니라 partial_fit을 부를 때 나요. 중괄호 목록은 16의 집합이라 수강생 화면에서는 순서가 다를 수 있어요." + REAL, ("p5", "오류와 함정"))

o = [sec("e-default")] + head(EB5, "learning_rate를 빼면 보폭이 점점 줄어서 1000번에도 MSE 14", RED)
CFS[0] = 24
EDC = ['sgd = SGDRegressor(loss="squared_error", eta0=0.01, shuffle=False, random_state=42)', "for epoch in range(1000):", "    sgd.partial_fit(X, y)", "print(sgd.learning_rate)",
       'print("w =", round(sgd.coef_[0], 2), "| b =", round(sgd.intercept_[0], 2))', 'print("MSE =", round(mean_squared_error(y, sgd.predict(X)), 2))']
o += cell({"id": "c-edef", "lines": EDC, "n": 3, "out": ["invscaling", "w = 12.13 | b = 27.26", "MSE = 14.09"], "red": (0, 2)}, 96, 196, 1600, sel="c-edef")
o.append(f'<div{fade(1)} style="position:absolute;left:{cx(96, "sgd = SGDRegressor(loss=" + chr(34) + "squared_error" + chr(34) + ",") + 2:.0f}px;top:{ly(196, 0) - LH() / 2 - 2:.0f}px;width:10px;height:{LH() + 4:.0f}px;border-radius:4px;background:{RED}"></div>')
o.append(tag(tx(96, EDC[0:1]) - 20, ly(196, 0) + 40, "learning_rate가 없어요", RED, 1, 24, lead=False))
EDT = cbot(196, 6) + 3 * (LH() + 10) + 50
DFT = [("learning_rate", "보폭", "w", "b", "MSE"), ('"constant"', "그대로", "10.13", "34.74", "3.25"), ("빼면 invscaling", "점점 줄어요", "12.13", "27.26", "14.09")]
o += plain_rows(96, EDT, 1100, DFT[1:], [300, 220, 160, 160, 160], 2, 76, list(DFT[0]), 30, mono_cols=(0, 2, 3, 4))
FP = [("constant", [1.0] * 6, GR), ("invscaling", [1.0, 0.71, 0.58, 0.5, 0.45, 0.41], RED)]
for k, (nm, ws_, c) in enumerate(FP):
    yy = EDT + 40 + k * 110
    o.append(label(1300, yy, nm, c, 26, fade(3), mono=True))
    xx = 1300
    for i, s_ in enumerate(ws_):
        o.append(bar(xx, yy + 44, 70 * s_, 18, c, fade(3) + DELAY(i * 80), 9))
        xx += 70 * s_ + 10
o.append(caption("수업처럼 learning_rate=\"constant\"를 꼭 적어요. 빼면 기본값 invscaling이 쓰여요.", 950, 4))
W("e-default", o, "수업 코드에서 learning_rate를 빼면 어떻게 될까요. 오류는 안 나요. 대신 기본값 invscaling이 쓰여요. invscaling은 epoch가 지날수록 보폭을 점점 줄이는 방식이에요. 오른쪽 아래 막대가 걸음 크기예요. 처음 몇 걸음 뒤로는 보폭이 작아져서 1000번을 돌아도 w 12.13, b 27.26, MSE 14.09로 아직 바닥에 못 가요. constant로 둔 수업 코드는 3.25까지 내려갔어요. 보폭을 줄이는 방법의 자세한 원리는 이 수업에서 다루지 않아요. 수업처럼 constant를 적고 eta0를 고르면 돼요. 막대 길이는 비교를 돕는 그림이에요." + REAL)

o = [sec("e-fit")] + head(EB5, "반복문 안에서 fit을 부르면 매번 처음부터 다시 배워요", RED)
CFS[0] = 20
EFC1 = ['sgd = SGDRegressor(loss="squared_error", learning_rate="constant", eta0=0.01,', "                   max_iter=1000, shuffle=False, random_state=42)", "for epoch in range(3):", "    sgd.fit(X, y)",
        '    print(epoch + 1, "| w =", round(sgd.coef_[0], 2), "| b =", round(sgd.intercept_[0], 2), "| n_iter_ =", sgd.n_iter_)']
EFO1 = ["1 | w = 10.31 | b = 34.04 | n_iter_ = 427", "2 | w = 10.31 | b = 34.04 | n_iter_ = 427", "3 | w = 10.31 | b = 34.04 | n_iter_ = 427"]
EFC2 = ['sgd = SGDRegressor(loss="squared_error", learning_rate="constant", eta0=0.01,', "                   max_iter=1, shuffle=False, random_state=42)", "for epoch in range(3):", "    sgd.fit(X, y)",
        '    print(epoch + 1, "| w =", round(sgd.coef_[0], 2), "| b =", round(sgd.intercept_[0], 2))']
EFO2 = ["1 | w = 8.46 | b = 2.73", "2 | w = 8.46 | b = 2.73", "3 | w = 8.46 | b = 2.73",
        "ConvergenceWarning: Maximum number of iteration reached before convergence. Consider increasing max_iter to improve the fit."]
o += cell({"id": "c-ef1", "lines": EFC1, "n": 3, "out": EFO1}, 96, 190, 1728)
F2T = cbot(190, 5) + 3 * (LH() + 10) + 34
o += cell({"id": "c-ef2", "lines": EFC2, "n": 4, "out": EFO2, "red": (3,)}, 96, F2T, 1728, sel="c-ef2")
o.append(box(1, 96 + 85 + 8, oy(190, 5, 0) - LH() / 2 - 4, tw(EFO1[0]) + 28, 3 * (LH() + 10) - 2, RED, 4))
o.append(tag(cx(96, EFO1[0], True) + 50, oy(190, 5, 1), "세 번 다 똑같아요: 427 epoch를 돌고 멈췄다가 다시 처음부터", RED, 1, 24))
o.append(box(2, 96 + 85 + 8, oy(F2T, 5, 0) - LH() / 2 - 4, tw(EFO2[0]) + 28, 3 * (LH() + 10) - 2, RED, 4))
o.append(tag(cx(96, EFO2[0], True) + 50, oy(F2T, 5, 1), "한 바퀴짜리를 세 번 해도 첫 바퀴 값 그대로", RED, 2, 24))
o.append(tag(96 + 105, oy(F2T, 5, 3) + 44, "더 돌아야 한다는 경고가 fit마다 나와요 (3번)", "#B26A00", 3, 22, lead=False))
o.append(caption("epoch마다 기록하려면 반복문 안에 partial_fit을 써요.", 960, 4))
W("e-fit", o, "partial_fit 자리에 fit을 쓰면 어떻게 될까요. 위 셀은 max_iter를 1000으로 두고 fit을 세 번 불렀어요. fit은 부를 때마다 w와 b를 처음 값으로 되돌리고 다시 배워요. 그래서 세 번 모두 427 epoch를 돌고 멈춘 같은 결과예요. n_iter_는 실제로 돈 바퀴 수예요. 427에서 멈춘 건 더 돌아도 손실이 거의 안 줄면 스스로 멈추는 기능 때문인데, 이 수업에서는 다루지 않아요. 아래 셀처럼 max_iter를 1로 두고 fit을 반복하면 한 바퀴짜리를 처음부터 세 번 하는 셈이라 첫 바퀴 값 8.46, 2.73에 머물러요. 바퀴가 모자란다는 ConvergenceWarning도 fit마다 나와요. 경고 앞의 파일 경로는 줄였어요." + REAL)

o = [sec("e-twice")] + head(EB5, "반복 셀을 두 번 실행하면 이어서 배워서 곡선이 처음부터 평평해요", RED)
CFS[0] = 24
o += cell({"id": "c-tw", "lines": ["history_df.head(3)"], "n": 7}, 96, 196, 800, sel="c-tw")
TWR = [("1", "10.129325", "34.741279", "3.250156"), ("2", "10.129314", "34.741320", "3.250153"), ("3", "10.129304", "34.741360", "3.250150")]
TWT = cbot(196, 1) + 30
o.append(df("tw", 96 + 105, TWT, ["epoch", "weight", "bias", "mse"], TWR, [100, 160, 160, 150], fs=26, rh=52, iw=40, attrs=rise(1), cs={(i, 3): f"color:{LC};font-weight:700" for i in range(3)}))
o.append(box(2, dfx(96 + 105, 40, [100, 160, 160, 150], 3) - 4, dfy(TWT, 52, 0) - 4, 150 + 12, 52 * 3 + 8, LC, 4))
o.append(note(96, TWT + 52 * 4 + 30, 800, "epoch는 1부터 다시 세지만, MSE가 처음부터 3.25예요. 처음 실행의 1369.8이 아니에요.", INK, 26, fade(2)))
IW6 = 900
o.append(img(924, 196, IW6, "etwice-1.png", fade(1), "tw-img"))
S6 = IW6 / 1768
o.append(ring(3, 924 + 195 * S6, 196 + 30 * S6, 90 * S6, 30 * S6, RED, 5))
o.append(note(924, 196 + IW6 * 939 / 1768 + 20, 900, "왼쪽 위 +3.25는 눈금에 3.25를 더해 읽으라는 뜻이에요. 0.0003만큼만 줄었어요.", SUB, 24, fade(3)))
o.append(reading(96, 820, "처음부터 다시 하려면 sgd를 만드는 셀부터 다시 실행해요.", GR, 4, 32))
W("e-twice", o, "수업 중에 반복 셀을 한 번 더 실행하면 이런 일이 생겨요. history는 빈 리스트로 다시 만들어지니 epoch는 1부터 다시 세요. 그런데 sgd는 이미 1000 epoch를 배운 상태라 거기서 이어서 1000번을 더 배워요. 그래서 첫 줄 MSE가 1369.8이 아니라 3.25예요. 학습 곡선도 처음부터 평평해요. 그래프 왼쪽 위의 플러스 3.25는 눈금 숫자에 3.25를 더해 읽으라는 뜻이에요. 변화가 너무 작아서 matplotlib이 이렇게 줄여서 적었어요. 1000번 동안 0.0003만큼만 줄었어요. 처음부터 다시 배우려면 SGDRegressor를 만드는 셀부터 다시 실행해요." + REAL + IMGN)

# ---------- part 6: real situations ----------
o = [sec("x-stop")] + head(EB6, "MSE가 3.3 밑으로 처음 내려간 epoch는 504예요", K6)
CFS[0] = 22
o += cell({"id": "c-st1", "lines": ['history_df[history_df["mse"] < 3.3].head(1)'], "n": 22}, 96, 196, 900, sel="c-st1")
STW = [100, 160, 160, 150]
S1T = cbot(196, 1) + 24
o.append(df("st1", 96 + 105, S1T, ["epoch", "weight", "bias", "mse"], [("504", "10.220602", "34.385449", "3.299564")], STW, fs=24, rh=46, iw=60, idx=[503], attrs=rise(1), cs={(0, 0): f"color:{K6};font-weight:900"}))
S2T = S1T + 46 * 2 + 40
o += cell({"id": "c-st2", "lines": ['history_df[history_df["mse"] < 3.5].head(1)'], "n": 23}, 96, S2T, 900, attrs=rise(2))
S2D = cbot(S2T, 1) + 24
o.append(df("st2", 96 + 105, S2D, ["epoch", "weight", "bias", "mse"], [("389", "10.380967", "33.760294", "3.499643")], STW, fs=24, rh=46, iw=60, idx=[388], attrs=rise(2)))
o.append(note(96, S2D + 46 * 2 + 30, 900, "head(1)은 조건에 맞는 첫 줄, 곧 처음 내려간 epoch예요.", SUB, 24, fade(2)))
IW7 = 780
o.append(img(1044, 196, IW7, "main-2.png", fade(1), "st-img"))
S7 = IW7 / 1716
EX504 = 1044 + (215 + 504 * 1.412) * S7
o.append(f'<div{fade(3)} style="position:absolute;left:{EX504 - 2:.0f}px;top:{196 + 62 * S7:.0f}px;width:0;height:{770 * S7:.0f}px;border-left:4px dashed {K6}"></div>')
o.append(label(EX504 + 12, 196 + 300 * S7, "504", K6, 40, fade(3)))
o.append(p(f"position:absolute;left:1044px;top:{196 + IW7 * 939 / 1716 + 30:.0f}px;width:780px;font-size:30px;line-height:1.5;color:{INK}", "504 epoch 뒤 496번은 MSE를 <b>0.05</b>만 줄였어요.<br>epochs를 600쯤으로 줄여도 결과가 거의 같아요.", fade(4)))
o.append(caption("학습 곡선이 평평해지면 그만 돌려도 돼요. 시간이 절약돼요.", 950, 5))
W("x-stop", o, "1000번을 다 돌아야 할까요. 45의 조건으로 MSE가 3.3보다 작은 줄을 고르고 head(1)로 첫 줄만 보면, 처음 3.3 밑으로 내려간 epoch가 나와요. 504예요. 3.5 밑은 389 epoch예요. 마지막 MSE가 3.25이니 504 epoch 뒤 496번은 0.05만 줄인 거예요. 학습 곡선에 504를 표시하면 이미 거의 평평한 곳이에요. 데이터가 많으면 1 epoch에도 시간이 오래 걸려서, 곡선이 평평해지면 멈추는 게 시간을 아껴요. 언제 멈출지 자동으로 정하는 기능도 있지만 이 수업에서는 다루지 않아요." + REAL + IMGN, ("p6", "실제 상황"))

o = [sec("x-new")] + head(EB6, "학생 두 명이 늘면 partial_fit으로 이어서 300번만 더 배워요", K6)
CFS[0] = 19
XNC = ["df7 = pd.DataFrame({", '    "hours": [1, 2, 3, 4, 5, 6, 7],', '    "scores": [47, 53, 65, 73, 87, 94, 106]', "})", 'X7 = df7[["hours"]]', 'y7 = df7["scores"]', "",
       "for epoch in range(300):", "    sgd.partial_fit(X7, y7)", "", 'print("SGD   w =", round(sgd.coef_[0], 2), "| b =", round(sgd.intercept_[0], 2))',
       "lr7 = LinearRegression().fit(X7, y7)", 'print("정답  w =", round(lr7.coef_[0], 2), "| b =", round(lr7.intercept_, 2))']
o += cell({"id": "c-xn", "lines": XNC, "n": 5, "out": ["SGD   w = 10.11 | b = 34.72", "정답  w = 10.04 | b = 34.86"]}, 96, 190, 1070, sel="c-xn")
o.append(tint(1, cx(96, '    "hours": [1, 2, 3, 4, 5, ') - 2, ly(190, 1) - LH() / 2, tw("6, 7") + 4, LH(), K4))
o.append(tint(1, cx(96, '    "scores": [47, 53, 65, 73, 87, ') - 2, ly(190, 2) - LH() / 2, tw("94, 106") + 4, LH(), K4))
o.append(run(2, 96 + 87, ly(190, 7) - LH() / 2, 1070 - 89, 2 * LH()))
o.append(run_off(3))
o.append(tag(tx(96, XNC[7:9]) - 10, ly(190, 8) - LH() / 2, "이미 배운 sgd에서 이어서", GR, 2, 22))
XN2 = cbot(190, 13) + 2 * (LH() + 10) + 40
o += cell({"id": "c-xn2", "lines": ['print(sgd.predict(pd.DataFrame({"hours": [8]})).round(1), lr7.predict(pd.DataFrame({"hours": [8]})).round(1))'], "n": 6, "out": ["[115.6] [115.1]"]}, 96, XN2, 1728, attrs=rise(4))
P7 = Plot(1240, 220, 560, 360, (0, 8.5), (30, 125))
o += P7.axes("공부 시간", "점수", (2, 4, 6, 8), (40, 80, 120), 20)
o.append(P7.svg(P7.dots(HRS, SCS, K1, 10, 0.85)))
o.append(P7.svg(P7.dots([6, 7], [94, 106], K4, 11, 0.95), SLIDE(1, 160, 0)))
o.append(P7.svg(P7.line(10.04, 34.86, "#9AA0AB", 4, "10 8"), fade(3)))
o.append(P7.svg(P7.line(10.11, 34.72, RED, 4), WIPE(3)))
o.append(label(P7.X(6) - 10, P7.Y(94) + 16, "새 학생 2명", K4, 22, fade(1)))
o.append(label(P7.X(8.5) + 10, P7.Y(10.11 * 8.5 + 34.72) - 40, "SGD", RED, 22, fade(3)))
o.append(label(P7.X(8.5) + 10, P7.Y(10.04 * 8.5 + 34.86) + 0, "정답", GRAY, 22, fade(3)))
o.append(box(3, 96 + 85 + 8, oy(190, 13, 0) - LH() / 2 - 4, tw("SGD   w = 10.11 | b = 34.72") + 28, 2 * (LH() + 10) - 2, RED, 4))
W("x-new", o, "수업이 끝난 뒤 학생 두 명의 점수가 더 들어왔다고 해 봐요. 6시간 94점, 7시간 106점이에요. 7명 표를 만들고, 이미 1000 epoch를 배운 sgd에 partial_fit을 300번만 더 불러요. partial_fit은 지금 w와 b에서 이어서 배우니까 처음부터 다시 1000번 돌 필요가 없어요. 결과는 w 10.11, b 34.72예요. 7명으로 LinearRegression을 새로 학습하면 w 10.04, b 34.86이라 거의 같아요. 8시간 예측도 115.6점과 115.1점이에요. 새 데이터가 계속 들어오는 서비스에서 이렇게 이어서 배우는 방식을 써요. 이 노트북은 4파트의 SGD 셀과 반복 셀을 먼저 실행했어요." + REAL + REAL_D)

o = [sec("x-office")] + head(EB6, "47의 오피스텔 200건은 eta0 0.01이면 터지고, 0.0001이면 R² 0.802", K6)
CFS[0] = 18
XOC = ["from sklearn.metrics import r2_score", "", 'office = pd.read_csv("datasets/office.csv")', 'Xo = office[["area"]]', 'yo = office["price"]', "", "for eta in [0.01, 0.0001]:",
       '    sgd_o = SGDRegressor(loss="squared_error", learning_rate="constant",', "                         eta0=eta, shuffle=False, random_state=42)", "    for epoch in range(1000):", "        sgd_o.partial_fit(Xo, yo)",
       "    r2 = r2_score(yo, sgd_o.predict(Xo))", '    print("eta0 =", eta, "| w =", round(sgd_o.coef_[0], 2), "| b =", round(sgd_o.intercept_[0], 2), "| R2 =", round(r2, 3))']
XOO = ["eta0 = 0.01 | w = -303320086979.13 | b = 427074117107.3 | R2 = -2.9579296731822244e+18", "eta0 = 0.0001 | w = 458.45 | b = 4735.1 | R2 = 0.802"]
o += cell({"id": "c-xo", "lines": XOC, "n": 2, "out": XOO, "red": (0,)}, 96, 186, 1728, sel="c-xo")
o.append(f'<div id="xo-bad"{fade(1)} style="position:absolute;left:{96 + 85 + 10}px;top:{oy(186, 13, 0) - LH() / 2 - 2:.0f}px;width:{tw(XOO[0]) + 24:.0f}px;height:{LH() + 4:.0f}px;border-radius:6px;background:rgba(163,49,49,0.12)"></div>')
o.append(shake(1, "xo-bad"))
o.append(box(2, 96 + 85 + 8, oy(186, 13, 1) - LH() / 2 - 4, tw(XOO[1]) + 28, LH() + 8, GR, 4))
XO3 = cbot(186, 13) + 2 * (LH() + 10) + 30
o += cell({"id": "c-xo3", "lines": ["lr_o = LinearRegression().fit(Xo, yo)",
                                     'print("LinearRegression w =", round(lr_o.coef_[0], 2), "| b =", round(lr_o.intercept_, 2), "| R2 =", round(r2_score(yo, lr_o.predict(Xo)), 3))'],
           "n": 3, "out": ["LinearRegression w = 465.67 | b = 4727.98 | R2 = 0.804"]}, 96, XO3, 1728, attrs=rise(3))
o.append(note(96, 830, 1728, "면적이 20~85라 1~5시간보다 숫자가 커서 경사도 커요. 그래서 같은 보폭이 너무 커요. 100배 작은 0.0001이면 48의 R² 0.804와 거의 같아요.", INK, 26, fade(2)))
o.append(caption("숫자가 큰 데이터에는 학습률을 작게 잡아요. 터지면 10배씩 줄여 봐요.", 950, 4))
W("x-office", o, "47에서 만든 오피스텔 200건에도 SGD를 써 봐요. 48처럼 r2_score로 채점해요. 5명 데이터와 같은 eta0 0.01을 쓰면 w가 마이너스 3천억이 넘고 R제곱이 마이너스 e 플러스 18로 터져요. 면적이 20부터 85까지라 1부터 5시간보다 숫자가 크고, 그만큼 경사도 커서 같은 보폭이 너무 커진 거예요. 100배 작은 0.0001로 바꾸면 w 458.45, b 4735.1, R제곱 0.802예요. 48에서 LinearRegression으로 배운 465.67, 4727.98, 0.804와 거의 같아요. 데이터마다 알맞은 학습률이 달라요. 숫자 크기를 맞춰서 학습률을 덜 고민하게 하는 방법도 있지만 이 수업에서는 다루지 않아요. 이 노트북은 48처럼 datasets 폴더의 office.csv를 읽었어요." + REAL)

# ---------- wrap up ----------
o = [sec("trouble")] + head("정리", "막히면 MSE와 출력의 마지막 줄을 봐요", RED)
TR = [("InvalidParameterError: ... Got 'mse' instead.", "loss 이름을 잘못 적었어요", 'loss="squared_error"'),
      ("MSE가 e+24처럼 엄청 커요", "학습률이 너무 커서 터졌어요", "eta0를 10배씩 작게"),
      ("MSE가 줄다가 큰 값에서 멈춰요", "학습률이 크거나, 너무 작아서 아직 내려가는 중", "eta0 바꾸고 학습 곡선 보기"),
      ("ConvergenceWarning: Maximum number of iteration ...", "반복문 안에서 fit을 불렀어요", "partial_fit(X, y)"),
      ("학습 곡선이 처음부터 평평해요", "반복 셀을 두 번 실행해서 이어서 배웠어요", "sgd 만드는 셀부터 다시"),
      ("그래프의 마이너스(-)가 네모로 나와요", "글꼴에 마이너스 기호가 없어요", "axes.unicode_minus = False")]
for i, (q, a_, cmd) in enumerate(TR):
    o.append(f'<div data-build-in="rise order {min(i + 1, 5)}" style="position:absolute;left:96px;top:{196 + i * 112}px;width:1728px;height:112px;display:flex;flex-direction:row;align-items:center;gap:26px;border-bottom:2px solid {LINE}">'
             + '<div style="flex:1;display:flex;flex-direction:column;gap:4px">' + p(f"{'font-family:' + MONO + ';' if q.isascii() else ''}font-size:25px;font-weight:700;color:{RED};white-space:nowrap", e(q)) + p(f"font-size:25px;color:{INK}", e(a_)) + '</div>'
             + p(f"width:560px;flex:none;font-size:27px;font-weight:700;color:{GR};white-space:pre", '✓ ' + e(cmd)) + '</div>')
o.append(caption("경사 하강법은 오류 없이 틀리는 일이 많아요. MSE를 꼭 찍어 봐요.", 900))
W("trouble", o, "막히면 셀 출력의 마지막 줄을 먼저 읽어요. 오류 메시지가 나오는 건 첫째 줄과 넷째 줄뿐이에요. 나머지는 오류 없이 숫자나 그래프만 이상해요. 경사 하강법은 학습률이 안 맞아도 조용히 틀린 답을 내니까, MSE와 학습 곡선을 꼭 확인해요. 터지면 eta0를 10배 작게, 너무 느리면 10배 크게 해 봐요.", ("trouble", "정리"))

o = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장으로 보는 오늘의 코드</h2>']
CH = [("불러오기", "from sklearn.linear_model import SGDRegressor", GR), ("모델", 'SGDRegressor(loss="squared_error", learning_rate="constant", eta0=0.01)', GR),
      ("한 바퀴(1 epoch)", "sgd.partial_fit(X, y)", GR), ("반복하며 기록", 'history.append({"epoch": epoch + 1, "mse": mse})', GR), ("표로", "history_df = pd.DataFrame(history)", GR),
      ("한 걸음", "새 w = w - 학습률 × 경사", GC), ("학습 곡선", 'plt.plot(history_df["epoch"], history_df["mse"])', LC), ("배운 값", "sgd.coef_[0]   sgd.intercept_[0]", WC),
      ("예측", 'sgd.predict(pd.DataFrame({"hours": [6]}))', WC), ("학습률 고르기", "터지면 10배 작게, 느리면 10배 크게", LRC_)]
for i, (k, d, c) in enumerate(CH):
    x, y = 96 + (i // 5) * 884, 190 + (i % 5) * 124
    o.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:844px;height:110px;display:flex;flex-direction:column;justify-content:center;gap:4px;border-bottom:2px solid {LINE}">'
             + p(f"font-size:26px;font-weight:700;color:{c}", e(k)) + p(f"font-family:{MONO};font-size:{20 if len(d) > 56 else (24 if len(d) > 42 else 28)}px;font-weight:700;color:{INK};white-space:pre", e(d)) + '</div>')
o.append(p(f"position:absolute;left:96px;top:850px;width:1728px;font-size:32px;font-weight:700;line-height:1.5;color:{INK}", "예측하고, 손실 재고, 경사 보고, 고치기를 epoch마다 되풀이해요.<br>" + f'<span style="color:{GRAY}">다음: 입력 열이 여러 개인 다중 선형 회귀를 배워요.</span>'))
W("cheatsheet", o, "오늘 쓴 코드를 한 장에 모았어요. 왼쪽은 SGDRegressor로 학습하고 기록하는 순서, 오른쪽은 한 걸음의 규칙과 그래프, 예측이에요. 경사 하강법은 예측, 손실, 경사, 고치기의 네 박자를 epoch마다 되풀이해요. 학습률은 데이터마다 달라서 10배씩 바꿔 보며 학습 곡선으로 확인해요. 다음 챕터에서는 공부 시간 하나가 아니라 입력 열이 여러 개인 다중 선형 회귀를 배워요.")

# ---------- order and toc ----------
want = ["cover", "toc", "setup", "recap", "recap-mse", "why", "big", "loss", "table", "ushape", "two", "tangent", "step", "walk",
        "lr", "lr-sgd", "lr-chart", "sgd", "args", "partial", "loop", "history", "curve", "wb", "pred", "compare",
        "e-loss", "e-default", "e-fit", "e-twice", "x-stop", "x-new", "x-office", "trouble", "cheatsheet"]
assert sorted(want) == sorted(ORDER), (set(want) ^ set(ORDER))
ORDER[:] = want
SECTIONS["p1"]["start"] = "recap"
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
parts_ = [("Lightbulb", K1, "왜 필요한가", "recap", "big"), ("Activity", RED, "손실과 경사", "loss", "walk"), ("Settings", PUR, "학습률", "lr", "lr-chart"),
          ("Tool", GR, "SGDRegressor로 학습하기", "sgd", "compare"), ("Warning", RED, "오류와 함정", "e-loss", "e-twice"), ("Star", K6, "실제 상황", "x-stop", "x-office")]
t = [f'<section id="toc" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>']
for i, (ic, c, h, a, b) in enumerate(parts_):
    x, y = 96 + (i // 3) * 884, 230 + (i % 3) * 190
    t.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:844px;height:160px;display:flex;flex-direction:row;align-items:center;gap:28px;border-bottom:2px solid {LINE}">'
             f'<p style="width:70px;font-size:72px;font-weight:900;color:{c}">{i + 1}</p><x-icon name="{ic}" style="width:52px;height:52px;color:{c}"></x-icon>'
             f'<p style="flex:1;font-size:44px;font-weight:700;color:{INK}">{e(h)}</p><p style="font-size:28px;color:{GRAY}">{page[a]}–{page[b]}쪽</p></div>')
t.append(f'<p style="position:absolute;left:96px;top:880px;font-size:30px;color:{SUB}">{page["setup"]}쪽은 노트북 준비, {page["trouble"]}–{page["cheatsheet"]}쪽은 막힐 때와 한 장 요약이에요.</p>')
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(t) + "\n<aside>" + e("1파트는 48을 다시 보고 공식 없이 답을 찾는 방법이 왜 필요한지 봐요. 2파트는 손실 함수와 U자 그래프, 두 가지 기울기, 경사의 반대쪽으로 한 걸음이에요. 3파트는 걸음의 크기인 학습률, 4파트는 수업 코드의 SGDRegressor를 한 줄씩 봐요. 5파트는 자주 나는 오류와 함정, 6파트는 배운 것을 섞은 실제 상황이에요.") + "</aside>\n</section>\n")
deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-25T07:00:00Z"}, "lists": "css", "title": "경사 하강법 (조금씩 고쳐 가며 직선 찾기)", "order": ORDER, "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
print(len(ORDER), "slides")
