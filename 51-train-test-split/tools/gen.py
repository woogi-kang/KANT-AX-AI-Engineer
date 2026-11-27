"""Generates every slide of the train/test split and scaling deck (51) and slides/deck.json.

Story: class notebook 03_ml.ipynb, cells 48 to 58. Chapter 50 scored the model on the same 10 students it learned
from (R2 0.99). Part 1: that is an exam made of the questions you studied; split off students the model never sees.
Part 2: train_test_split from sklearn.model_selection, its four results and their order, test_size and random_state
(with and without, real runs), which students went where, fit on 7, score on 3 (R2 0.93), 0.9992 vs 0.93.
Part 3: SGD on raw columns explodes (w 3.4e+10), describe() shows columns of different size, standardizing one
column by hand, StandardScaler with fit_transform on the training table and transform on the test table, the scaler's
mean_ and scale_, the scaled table's mean 0 and std 1 (and why describe() prints 1.08). Part 4: SGDRegressor on the
scaled table (R2 0.95, stopped by itself at epoch 197), the partial_fit loop and its history, the w1 w2 w3 curves
with label and legend, barh of raw and scaled slopes, LinearRegression vs SGDRegressor. Part 5: the four results in
the wrong order, fit_transform on the test table, predict with the raw table, reading a scaled slope as points per
hour. Part 6: a new student through scaler.transform, random_state changes the 3-student score (0.89 to 0.98), the
200 office listings of 47 split and the SGD that exploded in 49 working once scaled. Then trouble, recap, cheat sheet.
Class code fixes shown in the deck (and said in the notes): the y_yrain comment dropped, "(-1 ~ +1)" comment
corrected, the swapped comments of cell 55 put back, the loss chart of cell 57 given a title and axis names, axe
renamed ax with ax.legend(), labels kept as in class. The barh charts are added (not in the class notebook).
Every cell and output comes from tools/demo.sh (tools/run_nb.py runs the cells with the project kernel), kept in
tools/demo.log. Charts are the kernel's own PNGs in tools/img (NanumGothic stands in for Malgun Gothic on Linux).

Layout rules (Stageshow skill, github.com/benjitaylor/skills, SKILL.md and every file in references/ read for this deck):
1. one focal object per slide: a notebook cell, a kernel chart, one code line taken apart, or one diagram (framing.md 1)
2. terms are labelled on the code token with leader lines and tints, not in cards (annotations.md)
3. say it once: the speaker notes carry the explanation, the slide keeps one caption at most (craft.md, Restraint)
4. no empty bands: the chart or the code grows to fill; the payoff gets the room (craft.md, Restraint)
5. values move instead of swapping: the four results fly into their boxes, the test papers fly out, dots slide onto
   the scaled number line (motion.md, Changing text and values)
6. one number gets to be big (R2 0.93 on the test students), the rest are lines (craft.md, Restraint)
7. a comparison changes one thing (teaching.md, Making a comparison): with and without random_state, transform and
   fit_transform, raw and scaled slopes
8. one color per role on every slide: training students teal, test students magenta (craft.md, Color and looks)
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




# ---------- this deck ----------
from PIL import Image
NB = "multi.ipynb"
EB1, EB2, EB3, EB4, EB5, EB6 = "1. 왜 필요한가", "2. 그래프로 먼저 보기", "3. 세 열로 학습하기", "4. 한 열 모델과 비교", "5. 오류와 함정", "6. 실제 상황"
CS, CL, CP, CY = K1, PUR, K2, GR          # study, sleep, practice, score: the same color on every slide
CSB, CLB, CPB, CYB = K1BG, K6BG, K2BG, GRBG
COLS = [("study_hours", "공부 시간", CS, CSB), ("sleep_hours", "수면 시간", CL, CLB), ("practice_count", "푼 문제 수", CP, CPB)]
IMPORTS = ["import pandas as pd", "import matplotlib.pyplot as plt", "import seaborn as sns"]
FONTC = ["import platform", "", "os_name = platform.system()", 'if os_name == "Windows":', '    plt.rcParams["font.family"] = "Malgun Gothic"',
         'elif os_name == "Darwin":', '    plt.rcParams["font.family"] = "AppleGothic"', 'plt.rcParams["axes.unicode_minus"] = False']
DATAC = ['df = pd.DataFrame({', '    "study_hours":    [1, 2, 3, 4, 5, 2, 3, 5, 4, 1],', '    "sleep_hours":    [6, 8, 5, 7, 8, 5, 8, 6, 6, 8],',
         '    "practice_count": [10, 15, 20, 25, 30, 12, 28, 22, 32, 8],', '    "score":          [47, 58, 60, 76, 87, 49, 73, 77, 79, 52]', '})', 'df']
ROWS = [(1, 6, 10, 47), (2, 8, 15, 58), (3, 5, 20, 60), (4, 7, 25, 76), (5, 8, 30, 87), (2, 5, 12, 49), (3, 8, 28, 73), (5, 6, 22, 77), (4, 6, 32, 79), (1, 8, 8, 52)]
SCAT = ["fig, axes = plt.subplots(1, 3, figsize=(16, 5))", "", 'sns.scatterplot(data=df, x="study_hours", y="score", ax=axes[0])',
        'sns.scatterplot(data=df, x="sleep_hours", y="score", ax=axes[1])', 'sns.scatterplot(data=df, x="practice_count", y="score", ax=axes[2])', "", "plt.show()"]
HEATC = ["plt.figure(figsize=(7, 5))", "", "sns.heatmap(", "    corr,", "    annot=True,", "    vmin=-1,", "    vmax=1,", '    fmt=".2f"', ")", "", "plt.show()"]
CORRT = [("1.00", "0.00", "0.85", "0.93"), ("0.00", "1.00", "0.14", "0.29"), ("0.85", "0.14", "1.00", "0.93"), ("0.93", "0.29", "0.93", "1.00")]
CN = ["study_hours", "sleep_hours", "practice_count", "score"]
XYC = ['X = df[["study_hours", "sleep_hours", "practice_count"]]', 'y = df["score"]', "print(X.shape, y.shape)"]
FITC = ["model = LinearRegression()", "model.fit(X, y)", "", 'print("기울기 w:", model.coef_)', 'print("절편 b:", model.intercept_)']
FITO = ["기울기 w: [5.80222725 2.68100001 0.63219852]", "절편 b: 17.660208080206637"]
W3 = ["5.80", "2.68", "0.63"]


def oyy(top, n, j):
    """Centre y of output line j in a cell with n code lines drawn at top (output lines sit together, no gap)."""
    return top + n * LH() + 30 + j * LH() + LH() / 2


def chight(n, m=0):
    return n * LH() + 20 + (10 + m * LH() if m else 0)


def imh(name, w):
    W0, H0 = Image.open(os.path.join(IMG, name)).size
    return w * H0 / W0


def crop(name, out, box):
    """Saves part of a kernel chart as its own file (box in fractions of the image) so a slide can show it large."""
    im = Image.open(os.path.join(IMG, name))
    W0, H0 = im.size
    im.crop((int(box[0] * W0), int(box[1] * H0), int(box[2] * W0), int(box[3] * H0))).save(os.path.join(IMG, out))
    return out


def NEXT():
    """Marks the slides that go past the class notebook (it stopped at the heatmap)."""
    return p(f"position:absolute;right:96px;top:40px;font-size:24px;font-weight:700;line-height:1.3;color:{TEAL};background:{K3BG};border-radius:999px;padding:6px 20px;white-space:nowrap", "수업 노트북 다음 단계")


def sline(left, top, parts, size=40, attrs="", tid=None):
    """One code line on dark ground, pieces colored: parts = [(text, color), ...]. Returns html and x of each piece."""
    xs, x = [], left + 48
    for t_, c_ in parts:
        xs.append(x)
        x += tw(t_, size)
    return xs, x


def strip_parts(left, top, w, h, parts, size=40, attrs="", tid=None):
    idt = f' id="{tid}"' if tid else ""
    sp = "".join(f'<span style="display:inline-block;color:{c}">{e(t).replace(" ", "&#160;")}</span>' for t, c in parts)
    line = p(f"font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.5;color:{W_};white-space:pre", sp)
    return f'<div{idt}{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:{DARK};border-radius:22px;padding:0 48px;display:flex;flex-direction:column;justify-content:center">{line}</div>'


def lead_down(order, x, y1, y2, color, text, size=28, w=None, anchor="left"):
    """A fine leader from a code token (x, y1) down to its label at y2 (annotations.md: thin line, a dot at the end)."""
    svg = (f'<svg{fade(order)} style="position:absolute;left:0;top:0;width:1920px;height:1080px;overflow:visible;pointer-events:none" viewBox="0 0 1920 1080">'
           f'<line x1="{x:.0f}" y1="{y1:.0f}" x2="{x:.0f}" y2="{y2 - 8:.0f}" stroke="{color}" stroke-width="3"/><circle cx="{x:.0f}" cy="{y1:.0f}" r="6" fill="{color}"/></svg>')
    ws = f"width:{w}px;white-space:normal;" if w else "white-space:nowrap;"
    lx = x - 4 if anchor == "left" else x - (w or 0) / 2
    lab = p(f"position:absolute;left:{lx:.0f}px;top:{y2:.0f}px;{ws}font-size:{size}px;font-weight:700;line-height:1.35;color:{color}", e(text), fade(order) + DELAY(150))
    return svg + lab


def colchip(name, color, bg, fs=26):
    return p(f"display:inline-block;font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:1.3;color:{color};background:{bg};border-radius:10px;padding:4px 14px;white-space:nowrap", e(name))




# ---------- this deck (51) ----------
NB = "split.ipynb"
EB1, EB2, EB3, EB4, EB5, EB6 = "1. 왜 필요한가", "2. 나눠서 채점하기", "3. 열의 크기 맞추기", "4. SGD로 세 열 배우기", "5. 오류와 함정", "6. 실제 상황"
TR, TRB = TEAL, K3BG          # training students: teal on every slide
TE, TEB = K4, K4BG            # test students: magenta on every slide
CS, CL, CP, CY = K1, PUR, K2, GR
CSB, CLB, CPB, CYB = K1BG, K6BG, K2BG, GRBG
COLS = [("study_hours", "공부 시간", CS, CSB), ("sleep_hours", "수면 시간", CL, CLB), ("practice_count", "푼 문제 수", CP, CPB)]
CN = ["study_hours", "sleep_hours", "practice_count", "score"]
ROWS = [(1, 6, 10, 47), (2, 8, 15, 58), (3, 5, 20, 60), (4, 7, 25, 76), (5, 8, 30, 87), (2, 5, 12, 49), (3, 8, 28, 73), (5, 6, 22, 77), (4, 6, 32, 79), (1, 8, 8, 52)]
TRAIN_I, TEST_I = [0, 7, 2, 9, 4, 3, 6], [8, 1, 5]
IMPORTS = ["import pandas as pd", "import matplotlib.pyplot as plt", "from sklearn.linear_model import LinearRegression, SGDRegressor",
           "from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score"]
DATAC = ['df = pd.DataFrame({', '    "study_hours":    [1, 2, 3, 4, 5, 2, 3, 5, 4, 1],', '    "sleep_hours":    [6, 8, 5, 7, 8, 5, 8, 6, 6, 8],',
         '    "practice_count": [10, 15, 20, 25, 30, 12, 28, 22, 32, 8],', '    "score":          [47, 58, 60, 76, 87, 49, 73, 77, 79, 52]', '})',
         'features = ["study_hours", "sleep_hours", "practice_count"]', 'X = df[features]', 'y = df["score"]']
SPLITC = ["from sklearn.model_selection import train_test_split", "", "X_train, X_test, y_train, y_test = train_test_split(", "    X,", "    y,", "    test_size=0.3,",
          "    random_state=42", ")", "", 'print("X_train:", X_train.shape)', 'print("X_test:", X_test.shape)', 'print("y_train:", y_train.shape)', 'print("y_test:", y_test.shape)']
SPLITO = ["X_train: (7, 3)", "X_test: (3, 3)", "y_train: (7,)", "y_test: (3,)"]
LRC = ["test_model = LinearRegression()", "test_model.fit(X_train, y_train)", "", "test_pred = test_model.predict(X_test)", "",
       'print(f"MAE: {mean_absolute_error(y_test, test_pred):.4f}")', 'print(f"MSE: {mean_squared_error(y_test, test_pred):.4f}")', 'print(f"R2: {r2_score(y_test, test_pred):.4f}")']
SCALEC = ["from sklearn.preprocessing import StandardScaler", "", "scaler = StandardScaler()", "", "X_train_scaled = scaler.fit_transform(X_train)", "X_test_scaled = scaler.transform(X_test)", "",
          "scaled_df = pd.DataFrame(X_train_scaled, columns=features)", "scaled_df.round(2)"]
SCALED = [(-1.38, -0.76, -1.32), (1.20, -0.76, 0.20), (-0.09, -1.65, -0.05), (-1.38, 1.02, -1.58), (1.20, 1.02, 1.21), (0.55, 0.13, 0.58), (-0.09, 1.02, 0.96)]
SGDC = ["sgd = SGDRegressor(", '    loss="squared_error",', '    learning_rate="constant",', "    eta0=0.01,", "    max_iter=3000,", "    random_state=42", ")", "",
        "sgd.fit(X_train_scaled, y_train)", "", "sgd_pred = sgd.predict(X_test_scaled)", "",
        'print(f"MAE: {mean_absolute_error(y_test, sgd_pred):.4f}")', 'print(f"MSE: {mean_squared_error(y_test, sgd_pred):.4f}")', 'print(f"R2: {r2_score(y_test, sgd_pred):.4f}")']
SGDO = ["MAE: 2.8169", "MSE: 8.5966", "R2: 0.9456"]
SCALE_NOTE = " 수업 셀의 주석은 표준화를 '-1 ~ +1'로 적었는데, 실제 값에는 -1.65도 있어요. 범위가 정해지는 게 아니라 평균이 0, 퍼진 정도가 1이 돼요."


def oyy(top, n, j):
    return oy(top, n, j)


def chight(n, m=0):
    return n * LH() + 20 + (10 + m * (LH() + 10) if m else 0)


def stu(i, x, y, color, bg, size=64, attrs="", tid=None, fs=None):
    """One student as a numbered disc (row number of df)."""
    idt = f' id="{tid}"' if tid else ""
    return p(f"position:absolute;left:{x:.0f}px;top:{y:.0f}px;width:{size}px;height:{size}px;border-radius:50%;border:3px solid {color};background:{bg};"
             f"font-family:{MONO};font-size:{fs or size * 0.42:.0f}px;font-weight:700;line-height:{size - 6}px;text-align:center;color:{INK}", str(i), idt + attrs)


def bigval(x, y, text, color, size=120, attrs=""):
    return p(f"position:absolute;left:{x}px;top:{y}px;font-size:{size}px;font-weight:900;line-height:1;color:{color};font-variant-numeric:tabular-nums;white-space:nowrap", e(text), attrs)


# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#F2B27A;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
       f'<h1{SLAM(1)} style="font-size:88px;font-weight:900;line-height:1.14;color:#F6F5F1">처음 보는 데이터로<br>채점하기</h1>',
       '<p style="font-size:38px;line-height:1.45;color:#BFC6D4">학습용과 채점용으로 나누고,<br>열의 크기를 맞춰요</p>']
cov.append(f'<div id="cov-card" style="position:absolute;left:1060px;top:220px;width:740px;height:520px;background:#FFFFFF;border-radius:24px;overflow:hidden">'
           + f'<img id="cov-img" src="data:image/png;base64,{png_b64("main-2.png")}" style="position:absolute;left:30px;top:70px;width:680px">'
           + '</div>')
cov.append(p(f"position:absolute;left:1060px;top:770px;width:740px;font-size:26px;line-height:1.5;color:#BFC6D4", "크기를 맞춘 세 열로 기울기 셋을 찾아가는 모습이에요."))
cov.append(kenburns(2, "cov-img", 1.08, 6000, "30% 40%"))
W("cover", cov, "50에서는 학생 10명으로 학습하고, 같은 10명으로 채점해서 R제곱 0.99가 나왔어요. 오늘은 그 점수가 너무 후한 이유를 보고, 학생 일부를 떼어 두었다가 채점하는 방법을 배워요. 이어서 열마다 크기가 다른 숫자를 비슷한 크기로 맞추는 스케일링을 배우고, 49의 경사 하강법으로 세 열을 학습해요. 수업 노트북 03의 마지막 부분, 셀 48부터 58까지예요." + IMGN, ("intro", "들어가기"))
ORDER.append("toc")

# ---------- setup ----------
o = [sec("setup")] + head("들어가기", "ml-basics에 새 노트북 split.ipynb를 열어요. 새로 설치할 건 없어요", JP)
TL = [("$", "cd ml-basics"), ("$", "cat pyproject.toml"), ("o", "dependencies = ["), ("o", '    "matplotlib>=3.11.2",'), ("o", '    "numpy>=2.5.5",'), ("o", '    "pandas>=3.1.1",'),
      ("o", '    "scikit-learn>=1.9.1",'), ("o", '    "seaborn>=0.13.2",'), ("o", "]")]
o.append(term(96, 214, 900, TL, 28, tid="t-setup"))
LHt = 28 * 1.55
o.append(box(1, 96 + 34 - 10, 214 + 26 + 6 * LHt - 4, 28 * 0.6 * 26 + 24, LHt + 8, "#F2C46D", 4, 10))
o.append(tag(96 + 34 + 28 * 0.6 * 26 + 40, 214 + 26 + 6.5 * LHt, "48에서 넣었어요", "#B26A00", 1, 26))
o.append(note(96, 214 + 52 + len(TL) * LHt + 30, 900, "dependencies 위아래 줄은 줄여 적었어요. 버전 숫자는 받는 날에 따라 달라요.", SUB, 26, fade(1)))
TX = 1240
tree = [("ml-basics/", INK, 0, True), (".venv/", GRAY, 1, True), ("datasets/", GRAY, 1, True), ("office.csv", GRAY, 2, False), ("multi.ipynb", GRAY, 1, False), (NB, JP, 1, False), ("pyproject.toml", GRAY, 1, False)]
o.append(label(TX, 214, "폴더 모양", INK, 30))
for i, (n_, c_, d, folder) in enumerate(tree):
    y = 290 + i * 76
    at = rise(2) + DELAY(i * 60) if i else ""
    o.append(p(f"position:absolute;left:{TX + d * 56}px;top:{y}px;font-family:{MONO};font-size:32px;font-weight:700;line-height:64px;color:{c_};white-space:nowrap", ("▸ " if folder else "") + e(n_), at))
o.append(tag(TX + 112 + 32 * 0.6 * 10 + 40, 290 + 3 * 76 + 32, "47에서 저장, 6파트", GRAY, 2, 26))
o.append(tag(TX + 56 + 32 * 0.6 * 11 + 40, 290 + 4 * 76 + 32, "50 노트북", GRAY, 2, 26))
o.append(tag(TX + 56 + 32 * 0.6 * 11 + 40, 290 + 5 * 76 + 32, "오늘 노트북", JP, 2, 26))
o.append(caption("scikit-learn이 dependencies에 있으면 준비 끝이에요. 커널은 .venv를 골라요(10).", 930, 3))
W("setup", o, "45부터 쓰는 ml-basics 프로젝트를 그대로 써요. 오늘 쓰는 train_test_split과 StandardScaler는 48에서 넣은 scikit-learn 안에 들어 있어요. 그래서 새로 설치할 건 없어요. pyproject.toml에 scikit-learn이 없으면 uv add scikit-learn으로 넣어요. VS Code에서 split.ipynb를 새로 만들고 커널은 .venv로 골라요. datasets 폴더의 office.csv는 47에서 만든 오피스텔 데이터예요. 6파트에서 다시 꺼내 써요." + REAL)

# ---------- start ----------
o = [sec("start")] + head("들어가기", "맨 위 셀은 50과 같은 학생 10명, 같은 X와 y예요", JP)
CFS[0] = 24
o += cell({"id": "c-imp", "lines": IMPORTS, "n": 1}, 96, 196, 1330)
DT = 196 + chight(4) + 28
o.append(p(f"position:absolute;left:{96 + 87}px;top:{DT}px;font-family:{MONO};font-size:22px;color:{GRAY}", "[2]  글꼴 셀: 50과 같아요 (46의 셀 + axes.unicode_minus)"))
DT2 = DT + 52
o += cell({"id": "c-data", "lines": DATAC, "n": 3}, 96, DT2, 1180, sel="c-data")
o.append(tag(1450, ly(196, 2), "SGDRegressor는 49", OR, 1, 24))
o.append(tag(1450, ly(196, 3), "채점 함수 셋은 48", GR, 1, 24))
o.append(hl(96, DT2, 1180, 6, 3, "mark", 2))
o.append(tag(1310, ly(DT2, 7), "50과 같은 문제 X(10, 3)와 정답 y(10,)", BL, 2, 26, w=500))
o.append(caption("오늘은 이 X와 y를 학습용과 채점용으로 나누는 데서 시작해요.", 950, 3))
W("start", o, "새 노트북 맨 위 셀이에요. pandas와 matplotlib을 불러오고, 모델 둘과 채점 함수 셋을 불러와요. SGDRegressor는 49의 경사 하강법 모델, 채점 함수는 48에서 쓴 것들이에요. 둘째 셀은 50과 같은 글꼴 셀이라 줄여 적었어요. 셋째 셀은 50의 학생 10명 표예요. features에 열 이름 셋을 담아 두고 X와 y를 만들었어요. 수업 노트북도 features라는 이름을 써요. 뒤에서 열 이름을 다시 붙일 때 이 리스트를 또 써요." + REAL)

# ---------- part 1 ----------
o = [sec("why")] + head(EB1, "50의 R² 0.99는 학습한 10명으로 다시 친 시험이에요", K1)
CFS[0] = 26
ALLC = ["model = LinearRegression()", "model.fit(X, y)", "y_pred = model.predict(X)", 'print(f"MAE: {mean_absolute_error(y, y_pred):.4f}")', 'print(f"R2: {r2_score(y, y_pred):.4f}")']
o += cell({"id": "c-all", "lines": ALLC, "n": 4, "out": ["MAE: 1.1739", "R2: 0.9900"]}, 96, 200, 1000, sel="c-all")
o.append(tint(1, cx(96, "model.fit(") - 2, ly(200, 1) - LH() / 2, tw("X, y") + 4, LH(), TR))
o.append(tint(2, cx(96, "y_pred = model.predict(") - 2, ly(200, 2) - LH() / 2, tw("X") + 4, LH(), TE))
o.append(tag(cx(96, "model.fit(X, y)") + 30, ly(200, 1), "10명으로 배우고", TR, 1, 28))
o.append(tag(cx(96, "y_pred = model.predict(X)") + 30, ly(200, 2), "같은 10명을 다시 맞혀요", TE, 2, 28))
SY = 640
for k in range(10):
    o.append(stu(k, 96 + k * 98, SY, TR, TRB, 72, rise(1) + DELAY(k * 40)))
o.append(label(96, SY - 56, "학습에 쓴 학생", TR, 28, fade(1)))
o.append(f'<div{fade(2)} style="position:absolute;left:84px;top:{SY - 12}px;width:{98 * 10 + 2}px;height:96px;border:4px dashed {TE};border-radius:20px"></div>')
o.append(label(96, SY + 110, "채점에 쓴 학생: 똑같은 10명", TE, 28, fade(2)))
o.append(label(1260, 300, "R²", SUB, 40, fade(3)))
o.append(bigval(1260, 360, "0.99", INK, 200, fade(3)))
o.append(note(1260, 600, 560, "답을 본 문제로 시험을 보면 점수가 잘 나와요. 처음 보는 학생에게도 이만큼 맞힐지는 이 숫자로 알 수 없어요.", INK, 30, fade(3)))
o.append(caption("새 학생에게 얼마나 맞을지 알려면, 학습에 안 쓴 학생으로 채점해야 해요.", 940, 4))
W("why", o, "50의 마지막 채점을 다시 봐요. fit에 X와 y, 학생 10명을 넣어 배웠어요. 그리고 predict에도 같은 X를 넣어 같은 10명의 점수를 맞혔어요. 그래서 R제곱이 0.99로 거의 만점이에요. 하지만 이건 공부한 문제를 그대로 시험에 낸 것과 같아요. 우리가 모델을 쓰고 싶은 곳은 처음 보는 학생이에요. 처음 보는 학생에게 얼마나 맞을지 알려면 학습에 안 쓴 학생으로 채점해야 해요." + REAL, ("p1", "왜 필요한가"))

o = [sec("exam")] + head(EB1, "기출문제 10개 중 3개는 덮어 두고, 나머지 7개로만 공부해요", K1)
PW, PH, PG = 130, 160, 22
def paper(i, x, y, color, bg, attrs="", tid=None):
    idt = f' id="{tid}"' if tid else ""
    return (f'<div{idt}{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{PW}px;height:{PH}px;border-radius:10px;border:3px solid {color};background:{bg};display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px">'
            + p(f"font-size:22px;font-weight:700;color:{color}", "문제") + p(f"font-family:{MONO};font-size:44px;font-weight:700;color:{INK}", str(i + 1)) + '</div>')
o.append(label(96, 220, "공부한 10문제로 그대로 시험", GRAY, 30))
for k in range(10):
    o.append(paper(k, 96 + k * (PW + PG), 280, "#B4B9C3", "#F1F0EC", tid=f"pa{k}"))
o.append(p(f"position:absolute;left:{96 + 10 * (PW + PG) - PG + 24}px;top:316px;width:200px;font-size:30px;font-weight:700;line-height:1.4;color:{GRAY}", "답을 외워도<br>100점"))
o.append(label(96, 530, "7문제로 공부하고, 덮어 둔 3문제로 시험", INK, 30, fade(1)))
TESTP = [2, 5, 8]
j = 0
for k in range(10):
    if k in TESTP:
        continue
    o.append(paper(k, 96 + j * (PW + PG), 590, TR, TRB, rise(1) + DELAY(j * 50)))
    j += 1
for m, k in enumerate(TESTP):
    o.append(paper(k, 1300 + m * (PW + PG), 590, TE, TEB, fly(2, f"pa{k}")))
o.append(label(96, 774, "학습용", TR, 28, fade(1)))
o.append(label(1300, 774, "채점용 (공부할 땐 안 봐요)", TE, 28, fade(2)))
o.append(caption("모델도 같아요. 학생 일부를 떼어 두고, 배운 뒤에 그 학생들로 채점해요.", 940, 3))
W("exam", o, "시험공부로 바꿔 생각해 봐요. 기출문제 10개로 공부하고 같은 10개로 시험을 보면, 답을 외우기만 해도 100점이에요. 실력이 얼마인지는 알 수 없어요. 그래서 3개는 덮어 두고 7개로만 공부한 다음, 덮어 둔 3개로 모의고사를 봐요. 그 점수가 처음 보는 문제를 얼마나 풀지에 더 가까워요. 머신러닝에서는 공부하는 쪽을 학습용 데이터, 덮어 두는 쪽을 테스트 데이터라고 해요. 이 덱에서는 채점용이라고 불러요. 학습용은 청록, 채점용은 자주색으로 계속 칠해요.")

o = [sec("big")] + head(EB1, "나누기는 X와 y를 만든 뒤, fit 하기 전에 해요", K1)
def flowbox(x, y, w, h, text, color, bg, fs=30, attrs="", mono_=True, tid=None):
    idt = f' id="{tid}"' if tid else ""
    return p(f"position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;border-radius:14px;border:3px solid {color};background:{bg};font-family:{MONO if mono_ else SANS};font-size:{fs}px;font-weight:700;line-height:{h - 6}px;text-align:center;color:{INK};white-space:nowrap", e(text), idt + attrs)
o.append(flowbox(96, 470, 260, 100, "X, y", INK, "#FFFFFF", 36))
o.append(label(96, 590, "학생 10명", SUB, 26))
o.append(arrow(70, "#9AA0AB", WIPE(1), "position:absolute;left:376px;top:505px"))
o.append(flowbox(466, 470, 360, 100, "train_test_split", K1, K1BG, 30, rise(1)))
o.append(f'<svg{WIPE(2)} style="position:absolute;left:0;top:0;width:1920px;height:1080px;overflow:visible" viewBox="0 0 1920 1080">'
         f'<path d="M836,500 C900,500 900,330 966,330" fill="none" stroke="{TR}" stroke-width="5"/><path d="M836,540 C900,540 900,710 966,710" fill="none" stroke="{TE}" stroke-width="5"/></svg>')
o.append(flowbox(976, 280, 330, 100, "X_train, y_train", TR, TRB, 28, rise(2)))
o.append(label(976, 396, "학습용 7명", TR, 26, rise(2)))
o.append(flowbox(976, 660, 330, 100, "X_test", TE, TEB, 28, rise(2)))
o.append(label(976, 776, "채점용 3명 (y_test는 정답지)", TE, 26, rise(2)))
o.append(arrow(70, "#9AA0AB", WIPE(3), "position:absolute;left:1326px;top:315px"))
o.append(flowbox(1416, 280, 300, 100, "fit", TR, "#FFFFFF", 32, rise(3)))
o.append(arrow(70, "#9AA0AB", WIPE(4), "position:absolute;left:1326px;top:695px"))
o.append(flowbox(1416, 660, 300, 100, "predict", TE, "#FFFFFF", 32, rise(4)))
o.append(f'<svg{WIPE(4)} style="position:absolute;left:1536px;top:396px;width:60px;height:250px" viewBox="0 0 60 250"><rect x="22" y="0" width="16" height="210" fill="#9AA0AB"/><polygon points="4,206 56,206 30,248" fill="#9AA0AB"/></svg>')
o.append(label(1600, 500, "배운 모델로", SUB, 26, fade(4)))
o.append(label(1416, 790, "예측과 y_test로 r2_score", TE, 26, fade(4)))
o.append(caption("fit에는 학습용만, 채점에는 채점용만 들어가요.", 950, 5))
W("big", o, "오늘 할 일을 한 그림으로 봐요. 50처럼 X와 y를 만든 다음, fit 하기 전에 train_test_split으로 둘로 나눠요. 위쪽 학습용 7명은 fit에 들어가서 모델이 배워요. 아래쪽 채점용 3명은 학습하는 동안 모델이 보지 못해요. 다 배운 모델에 채점용 X_test를 넣어 예측하고, 그 예측을 채점용 정답 y_test와 비교해서 점수를 매겨요. 학습에 쓴 학생과 채점에 쓴 학생은 한 명도 겹치지 않아요.")

# ---------- part 2 ----------
o = [sec("import")] + head(EB2, "train_test_split은 scikit-learn의 model_selection 서랍에 있어요", K2)
IP = [("from ", "#9AA0AB"), ("sklearn", "#9CC2F5"), (".", W_), ("model_selection", "#F2C46D"), (" import ", "#9AA0AB"), ("train_test_split", "#B8E8BE")]
o.append(strip_parts(96, 210, 1728, 130, IP, 46))
xs, _ = sline(96, 210, IP, 46)
LB = [(1, "패키지 (48에서 설치)", CS, 0), (3, "모듈: 데이터 나누기, 모델 고르기 도구", OR, 1), (5, "함수: 소문자와 밑줄", GR, 0)]
for k, (i, t_, c_, lv) in enumerate(LB):
    o.append(lead_down(1 + k, xs[i] + tw(IP[i][0], 46) / 2, 320, 380 + lv * 60, c_, t_, 26))
DR = [("linear_model", "LinearRegression, SGDRegressor", "48, 49", GRAY, False), ("metrics", "mean_absolute_error, r2_score", "48", GRAY, False),
      ("model_selection", "train_test_split", "오늘 2파트", OR, True), ("preprocessing", "StandardScaler", "오늘 3파트", TEAL, True)]
for i, (m, f_, ch, c_, new) in enumerate(DR):
    x = 96 + i * 440
    o.append(f'<div{rise(4) + DELAY(i * 90)} style="position:absolute;left:{x}px;top:560px;width:410px;height:300px;border-radius:18px;border:3px solid {c_ if new else LINE};background:{"#FFFFFF" if new else "#F1F0EC"};padding:24px 26px;display:flex;flex-direction:column;gap:16px">'
             + p(f"font-size:24px;font-weight:700;color:{c_}", "sklearn." ) + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:{INK}", e(m))
             + p(f"font-family:{MONO};font-size:22px;line-height:1.5;color:{SUB};white-space:nowrap", e(f_).replace(", ", "<br>")) + p(f"margin-top:auto;font-size:24px;font-weight:700;color:{c_ if new else GRAY}", e(ch)) + '</div>')
o.append(caption("이름이 대문자로 시작하면 클래스(만들어 쓰기), 소문자면 함수(바로 부르기)예요.", 940, 5))
W("import", o, "train_test_split은 48에서 설치한 scikit-learn 안에 있어요. 불러오는 이름은 sklearn이에요. scikit-learn은 도구를 서랍처럼 모듈로 나눠 담아요. 48에서는 linear_model 서랍에서 모델을, metrics 서랍에서 채점 함수를 꺼냈어요. 오늘은 model_selection 서랍에서 train_test_split 함수를 꺼내요. 이 서랍에는 데이터를 나누고 모델을 고르는 도구가 들어 있어요. 3파트에서는 preprocessing, 곧 전처리 서랍에서 StandardScaler를 꺼내요. LinearRegression처럼 대문자로 시작하는 이름은 클래스라서 괄호로 객체를 만들어 쓰고, train_test_split처럼 소문자와 밑줄로 된 이름은 함수라서 바로 불러요.")

o = [sec("split")] + head(EB2, "train_test_split은 네 가지를 X 두 개, y 두 개 순서로 돌려줘요", K2)
CFS[0] = 24
o += cell({"id": "c-split", "lines": SPLITC, "n": 5, "out": SPLITO}, 96, 196, 1000, sel="c-split")
RL = "X_train, X_test, y_train, y_test = train_test_split("
pos = [0, len("X_train, "), len("X_train, X_test, "), len("X_train, X_test, y_train, ")]
nm = ["X_train", "X_test", "y_train", "y_test"]
rc = [TR, TE, TR, TE]
for k in range(4):
    o.append(tint(1, cx(96, RL[:pos[k]]) - 2, ly(196, 2) - LH() / 2, tw(nm[k]) + 4, LH(), rc[k]))
    o.append(p(f"position:absolute;left:{cx(96, RL[:pos[k]]) + tw(nm[k]) / 2 - 14:.0f}px;top:{ly(196, 2) - LH() / 2 - 34:.0f}px;width:28px;height:28px;border-radius:50%;background:{rc[k]};color:#FFFFFF;font-size:18px;font-weight:900;line-height:28px;text-align:center", str(k + 1), fade(1) + f' id="sn{k}"'))
DX = 1160
o.append(label(DX, 210, "들어간 것", SUB, 26))
o.append(flowbox(DX, 254, 300, 84, "X  (10, 3)", INK, "#FFFFFF", 28))
o.append(flowbox(DX + 360, 254, 300, 84, "y  (10,)", INK, "#FFFFFF", 28))
o.append(label(DX, 400, "나온 것 (이 순서로 받아요)", SUB, 26, fade(2)))
OUTB = [("X_train  (7, 3)", TR, TRB), ("X_test  (3, 3)", TE, TEB), ("y_train  (7,)", TR, TRB), ("y_test  (3,)", TE, TEB)]
for k, (t_, c_, bg) in enumerate(OUTB):
    y = 450 + k * 112
    o.append(p(f"position:absolute;left:{DX}px;top:{y + 24}px;width:40px;height:40px;border-radius:50%;background:{c_};color:#FFFFFF;font-size:24px;font-weight:900;line-height:40px;text-align:center", str(k + 1), fly(2, f"sn{k}")))
    o.append(flowbox(DX + 64, y, 596, 88, t_, c_, bg, 30, rise(2) + DELAY(k * 120)))
o.append(caption("받는 이름은 자유지만, 자리 순서는 X 학습, X 채점, y 학습, y 채점으로 정해져 있어요.", 950, 3))
W("split", o, "수업 셀 48이에요. train_test_split 괄호 안에 문제 X와 정답 y를 넣으면, 결과를 네 개 돌려줘요. 순서는 X의 학습용, X의 채점용, y의 학습용, y의 채점용이에요. 왼쪽에 이름 네 개를 쉼표로 적으면 19에서 배운 return a, b처럼 순서대로 하나씩 담겨요. 이름은 마음대로 지어도 되지만 순서는 바뀌지 않아요. 그래서 다들 X_train, X_test, y_train, y_test라는 이름을 써요. 출력을 보면 X는 10줄에서 7줄과 3줄로, y도 10개에서 7개와 3개로 나뉘었어요. 열 수 3은 그대로예요. 수업 주석의 y_yrain은 오타라서 뺐어요." + REAL)

o = [sec("args")] + head(EB2, "test_size는 채점용 비율, random_state는 섞는 순서 번호예요", K2)
AP = [("train_test_split(", W_), ("X, y", "#9CC2F5"), (", ", W_), ("test_size=0.3", "#F2C46D"), (", ", W_), ("random_state=42", "#C7B5F5"), (")", W_)]
o.append(strip_parts(96, 200, 1728, 120, AP, 42))
xs, _ = sline(96, 200, AP, 42)
for k, (i, t_, c_) in enumerate([(1, "문제와 정답, 이 순서로", CS), (3, "10명 × 0.3 = 3명을 채점용으로", OR), (5, "다음 장에서 봐요", PUR)]):
    o.append(lead_down(1 + k, xs[i] + tw(AP[i][0], 42) / 2, 300, 360 + (k % 2) * 56, c_, t_, 26))
CFS[0] = 24
SZC = ["for size in [0.2, 0.3, 0.5]:", "    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=size, random_state=42)", '    print(size, "→ 학습용", len(X_train), "명, 채점용", len(X_test), "명")']
SZO = ["0.2 → 학습용 8 명, 채점용 2 명", "0.3 → 학습용 7 명, 채점용 3 명", "0.5 → 학습용 5 명, 채점용 5 명"]
o += cell({"id": "c-sz", "lines": SZC, "n": 6, "out": SZO}, 96, 520, 1728, attrs=rise(3))
for k, (a, b) in enumerate([(8, 2), (7, 3), (5, 5)]):
    y0 = oyy(520, 3, k) - 16
    for m in range(10):
        c_ = TR if m < a else TE
        o.append(f'<div{rise(4)}{DELAY(k * 120 + m * 20)} style="position:absolute;left:{1200 + m * 40}px;top:{y0:.0f}px;width:30px;height:30px;border-radius:50%;background:{c_}"></div>')
o.append(note(96, 860, 1728, "보통 0.2~0.3을 써요. 채점용이 너무 적으면 점수가 운에 흔들리고, 너무 많으면 배울 학생이 줄어요. test_size=3처럼 정수로 주면 3명이에요.", SUB, 28, fade(5)))
W("args", o, "괄호 안을 하나씩 봐요. 첫째와 둘째 칸은 문제 X와 정답 y예요. 이름 없이 순서로 들어가는 위치 인자예요. test_size는 전체 중 몇 비율을 채점용으로 뗄지예요. 0.3이면 10명의 30퍼센트, 3명이에요. 0.2면 2명, 0.5면 5명이 채점용이 돼요. 보통 0.2에서 0.3을 써요. 채점용이 너무 적으면 점수가 우연에 흔들리고, 너무 많으면 배울 학생이 모자라요. 0.3 대신 정수 3을 주면 비율이 아니라 3명이라는 뜻이에요. 실행해 보면 7과 3이 나와요. random_state는 다음 장에서 봐요." + REAL)

o = [sec("which")] + head(EB2, "나누기 전에 섞어요. 채점용은 8번, 1번, 5번 학생이에요", K2)
CFS[0] = 26
WC = ['print("학습용 학생:", list(X_train.index))', 'print("채점용 학생:", list(X_test.index))']
o += cell({"id": "c-which", "lines": WC, "n": 7, "out": ["학습용 학생: [0, 7, 2, 9, 4, 3, 6]", "채점용 학생: [8, 1, 5]"]}, 96, 200, 980, sel="c-which")
o.append(tint(1, cx(96, "학습용 학생: ", True) - 2, oyy(200, 2, 0) - LH() / 2, tw("[0, 7, 2, 9, 4, 3, 6]") + 4, LH(), TR))
o.append(tint(1, cx(96, "채점용 학생: ", True) - 2, oyy(200, 2, 1) - LH() / 2, tw("[8, 1, 5]") + 4, LH(), TE))
o.append(note(96, 480, 980, "index는 표 왼쪽의 행 번호예요(45). 나눈 뒤에도 원래 번호를 그대로 들고 있어서, 누가 어디로 갔는지 알 수 있어요.", INK, 30, fade(2)))
o.append(note(96, 680, 980, "번호가 0, 1, 2 순서가 아니에요. train_test_split은 섞은 다음 나눠요(shuffle=True가 기본값).", SUB, 28, fade(3)))
TX0, TY0, WD = 1150, 210, [150, 150, 190, 90]
ra = {i: "" for i in range(10)}
cs = {}
for i in range(10):
    c_ = TE if i in TEST_I else TR
    cs[(i, 3)] = f"color:{c_};font-weight:700"
o.append(df("t-which", TX0, TY0, CN, ROWS, WD, fs=24, rh=60, iw=44, cs=cs))
for i in range(10):
    c_ = TE if i in TEST_I else TR
    o.append(f'<div{fade(1)} style="position:absolute;left:{TX0 - 20}px;top:{dfy(TY0, 60, i) + 6:.0f}px;width:10px;height:48px;border-radius:5px;background:{c_}"></div>')
for i in TEST_I:
    o.append(box(2, TX0 - 4, dfy(TY0, 60, i), 44 + sum(WD) + 32, 58, TE, 4, 10))
W("which", o, "누가 학습용이고 누가 채점용인지 확인해 봐요. X_train과 X_test는 DataFrame이라서 45에서 본 index, 곧 왼쪽 행 번호를 그대로 갖고 있어요. 채점용은 8번, 1번, 5번 학생이에요. 번호가 앞에서부터 차례대로가 아니죠. train_test_split은 기본으로 줄을 한 번 섞은 다음 나눠요. 표가 점수 순서나 날짜 순서로 놓여 있어도 한쪽에 몰리지 않게 하려는 거예요. 오른쪽 표에서 자주색 줄이 채점용, 청록 줄이 학습용이에요. 이 셀은 이해를 도우려고 더했어요." + REAL)

o = [sec("seed")] + head(EB2, "random_state를 빼면 실행할 때마다 다른 학생이 채점용이 돼요", K2)
CFS[0] = 22
SD1 = ["X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)", 'print("채점용 학생:", list(X_test.index))']
SD2 = ["X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)", 'print("채점용 학생:", list(X_test.index))']
YS = [196, 196 + chight(2, 1) + 22]
o.append(label(96, 196, "random_state 없이 두 번", RED, 28))
for k, out in enumerate(["채점용 학생: [4, 7, 5]", "채점용 학생: [1, 2, 3]"]):
    o += cell({"id": f"c-sa{k}", "lines": SD1, "n": 8 + k, "out": [out]}, 96, 246 + k * (chight(2, 1) + 18), 1290, attrs=rise(1 + k) if k else "")
o.append(underline(2, cx(96, "채점용 학생: ", True), cx(96, "채점용 학생: [1, 2, 3]", True), oyy(246 + chight(2, 1) + 18, 2, 0) + LH() / 2, RED, 5))
Y2 = 246 + 2 * (chight(2, 1) + 18) + 30
o.append(label(96, Y2, "random_state=42로 두 번", GR, 28, fade(3)))
for k in range(2):
    o += cell({"id": f"c-sb{k}", "lines": SD2, "n": 10 + k, "out": ["채점용 학생: [8, 1, 5]"]}, 96, Y2 + 50 + k * (chight(2, 1) + 18), 1290, attrs=rise(3))
o.append(note(1420, 300, 400, "섞는 순서가 매번 달라서 결과가 달라요. 여러분 화면의 위 두 줄은 이것과 다를 수 있어요.", INK, 28, fade(2)))
o.append(note(1420, Y2 + 60, 400, "번호를 정해 두면 몇 번을 실행해도 같은 3명이에요. 47의 default_rng(42)와 같은 생각이에요.", GR, 28, fade(4)))
o.append(caption("42는 약속일 뿐이에요. 0이든 7이든 같은 숫자를 쓰면 같은 결과가 나와요.", 960, 5))
W("seed", o, "random_state를 빼고 같은 셀을 두 번 실행했어요. 처음엔 4번, 7번, 5번이, 두 번째엔 1번, 2번, 3번이 채점용이 됐어요. 섞는 순서가 실행할 때마다 달라서예요. 채점용이 바뀌면 점수도 바뀌니까, 어제와 오늘 결과를 비교할 수가 없어요. random_state에 숫자를 주면 섞는 순서가 고정돼요. 47에서 난수를 만들 때 default_rng(42)로 시드를 정한 것과 같은 생각이에요. 42에 특별한 뜻은 없고 많이 쓰는 약속일 뿐이에요. 다른 숫자를 써도 같은 숫자면 같은 결과가 나와요. random_state가 없는 두 줄은 여러분 화면과 다를 수 있어요." + REAL)

o = [sec("fittest")] + head(EB2, "학습용 7명으로 fit, 채점용 3명으로 채점해요", K2)
CFS[0] = 25
o += cell({"id": "c-lr", "lines": LRC, "n": 12, "out": ["MAE: 3.0870", "MSE: 10.6380", "R2: 0.9327"]}, 96, 196, 1000, sel="c-lr")
o.append(tint(1, cx(96, "test_model.fit(") - 2, ly(196, 1) - LH() / 2, tw("X_train, y_train") + 4, LH(), TR))
o.append(tint(2, cx(96, "test_pred = test_model.predict(") - 2, ly(196, 3) - LH() / 2, tw("X_test") + 4, LH(), TE))
for j, ln in enumerate(LRC[5:8]):
    s0 = ln.index("(y_test") + 1
    o.append(tint(3, cx(96, ln[:s0]) - 2, ly(196, 5 + j) - LH() / 2, tw("y_test, test_pred") + 4, LH(), TE))
o.append(tag(cx(96, LRC[1]) + 30, ly(196, 1), "학습용만", TR, 1, 26))
o.append(tag(cx(96, LRC[3]) + 30, ly(196, 3), "처음 보는 3명", TE, 2, 26))
o.append(tag(1110, ly(196, 6), "정답도 채점용", TE, 3, 22))
BX = 1320
o.append(label(BX, 210, "채점용 3명: 정답과 예측", INK, 28, fade(4)))
for k, (i, t_, pr) in enumerate([(8, 79, 74.9), (1, 58, 61.5), (5, 49, 50.6)]):
    y = 280 + k * 200
    o.append(stu(i, BX, y + 22, TE, TEB, 60, rise(4) + DELAY(k * 120)))
    o.append(bar(BX + 90, y + 10, t_ * 3.6, 34, CY, WIPE(4) + DELAY(k * 120)))
    o.append(label(BX + 100 + t_ * 3.6, y + 10, f"정답 {t_}", CY, 26, rise(4) + DELAY(k * 120)))
    o.append(bar(BX + 90, y + 56, pr * 3.6, 34, "#9AA0AB", WIPE(4) + DELAY(k * 120 + 60)))
    o.append(label(BX + 100 + pr * 3.6, y + 56, f"예측 {pr}", SUB, 26, rise(4) + DELAY(k * 120 + 60)))
o.append(caption("모델 만들기와 채점 함수는 48과 같아요. 넣는 표만 학습용과 채점용으로 갈렸어요.", 950, 5))
W("fittest", o, "수업 셀 50이에요. 모델을 새로 만들고 fit에는 학습용 X_train과 y_train만 넣었어요. 그다음 처음 보는 X_test 3명을 predict에 넣었어요. 채점할 때 정답도 채점용 y_test를 써요. 학습용 정답과 짝을 지으면 줄 수부터 안 맞아요. 결과는 MAE 3.09, R제곱 0.93이에요. 오른쪽은 세 학생의 정답과 예측이에요. 8번 학생은 79점인데 74.9로, 4점쯤 낮게 예측했어요. 50에서는 가장 크게 틀린 학생도 2.2점이었는데, 처음 보는 학생에게는 더 크게 틀려요. 수업 노트북은 MAE, MSE, R제곱만 찍었고, 정답과 예측 그림은 이해를 도우려고 더했어요." + REAL)

o = [sec("compare")] + head(EB2, "학습한 7명으로 재면 0.9992, 처음 보는 3명은 0.93이에요", K2)
CFS[0] = 26
TSC = ["train_pred = test_model.predict(X_train)", 'print(f"학습용 7명 R2: {r2_score(y_train, train_pred):.4f}")', 'print(f"채점용 3명 R2: {r2_score(y_test, test_pred):.4f}")']
o += cell({"id": "c-ts", "lines": TSC, "n": 13, "out": ["학습용 7명 R2: 0.9992", "채점용 3명 R2: 0.9327"]}, 96, 196, 1100, sel="c-ts")
CB = [("50: 10명으로 배우고 같은 10명으로", 0.99, "#9AA0AB"), ("오늘: 학습용 7명으로 다시 재면", 0.9992, TR), ("오늘: 처음 보는 3명", 0.9327, TE)]
for k, (t_, v, c_) in enumerate(CB):
    y = 520 + k * 120
    o.append(label(96, y, t_, INK if k == 2 else SUB, 28, rise(1 + k)))
    o.append(bar(620, y - 6, v * 540, 56, c_, WIPE(1 + k)))
    o.append(label(620 + v * 540 + 18, y, f"{v:.4f}".rstrip("0") if k != 1 else "0.9992", c_, 30, rise(1 + k)))
o.append(bigval(1340, 240, "0.93", TE, 180, COUNT(4, 900)))
o.append(note(1340, 440, 480, "모델이 새 학생에게 낼 점수는 이쪽에 가까워요. 보고서에 적을 점수도 이 숫자예요.", INK, 30, fade(4)))
o.append(caption("학습용 점수만 높고 채점용 점수가 낮으면, 학습용을 외웠다는 신호예요.", 950, 5))
W("compare", o, "같은 모델을 학습용 7명과 채점용 3명으로 따로 채점해 봤어요. 학습한 7명으로 재면 R제곱이 0.9992로 거의 1이에요. 50의 0.99처럼 공부한 문제로 본 시험이라서예요. 처음 보는 3명으로 재면 0.93이에요. 새 학생에게 모델을 쓸 때 기대할 수 있는 점수는 0.93 쪽이에요. 두 점수 차이가 크면 모델이 학습용 데이터를 외웠다는 신호예요. 이런 상태를 과대적합이라고 부르는데, 이름만 알아 두면 돼요. 학습용 점수 셀은 이해를 도우려고 더했어요." + REAL)

# ---------- part 3 ----------
o = [sec("sgdraw")] + head(EB3, "크기를 안 맞추고 SGD로 배우면 기울기가 수백억으로 터져요", K3)
CFS[0] = 24
RAWC = ["raw = SGDRegressor(", '    loss="squared_error",', '    learning_rate="constant",', "    eta0=0.01,", "    max_iter=3000,", "    random_state=42", ")", "",
        "raw.fit(X_train, y_train)", 'print("기울기 w:", raw.coef_)', 'print("예측:", raw.predict(X_test))']
RAWO = ["기울기 w: [ 3.36938078e+10 -4.74775486e+10  1.16018067e+10]", "예측: [ 2.15788250e+11 -1.43785177e+11 -3.61579513e+10]"]
o += cell({"id": "c-raw", "lines": RAWC, "n": 14, "out": RAWO, "red": (0, 1)}, 96, 196, 1100, sel="c-raw")
o.append(tint(1, cx(96, "raw.fit(") - 2, ly(196, 8) - LH() / 2, tw("X_train, y_train") + 4, LH(), TR))
o.append(tag(cx(96, RAWC[8]) + 30, ly(196, 8), "크기를 안 맞춘 표 그대로", TR, 1, 26))
o.append(shake(2, "c-raw"))
o.append(underline(2, cx(96, "기울기 w: [ ", True), cx(96, "기울기 w: [ 3.36938078e+10", True), oyy(196, 11, 0) + LH() / 2 + 2, RED, 5))
RX = 1260
o.append(label(RX, 230, "3.36938078e+10 읽기", SUB, 28, fade(3)))
o.append(p(f"position:absolute;left:{RX}px;top:290px;width:560px;font-family:{MONO};font-size:40px;font-weight:700;line-height:1.5;color:{INK}", "3.37 × 10<sup>10</sup>", fade(3)))
o.append(p(f"position:absolute;left:{RX}px;top:360px;width:560px;font-size:30px;line-height:1.5;color:{SUB}", "e+10은 10을 열 번 곱한다는 뜻이에요.", fade(3)))
o.append(bigval(RX, 440, "337억", RED, 120, fade(4)))
o.append(note(RX, 600, 560, "기울기 w1이 337억이에요. 정답 점수는 49점에서 87점인데, 첫 학생 예측은 2천억이 넘어요.", INK, 30, fade(4)))
o.append(caption("49의 오피스텔에서 eta0 0.01이 터진 것과 같은 일이에요. 오류 없이 숫자만 터져요.", 950, 5))
W("sgdraw", o, "3파트를 시작하기 전에, 나눈 학습용 표를 49의 SGDRegressor에 그대로 넣어 봐요. 설정은 수업 셀 55와 같아요. 결과를 보면 기울기가 3.36938078e+10이에요. e+10은 10을 열 번 곱한다는 뜻이라서 약 337억이에요. 예측도 2천억이 넘어요. 점수는 49점에서 87점 사이인데 말이 안 되는 숫자예요. 오류는 나지 않고 숫자만 터져요. 49에서 오피스텔 200건에 eta0 0.01을 썼을 때와 같은 일이에요. 왜 이런 일이 생기는지 다음 장에서 열마다 숫자 크기를 비교해 봐요. 이 셀은 이해를 도우려고 더했어요." + REAL, ("p3", "열의 크기 맞추기"))

o = [sec("describe")] + head(EB3, "describe()로 보면 열마다 숫자가 퍼진 크기가 달라요", K3)
CFS[0] = 24
o += cell({"id": "c-desc", "lines": ["X.describe().round(2)"], "n": 15}, 96, 196, 900, sel="c-desc")
DESC = [("10.00", "10.00", "10.00"), ("3.00", "6.70", "20.20"), ("1.49", "1.25", "8.63"), ("1.00", "5.00", "8.00"), ("2.00", "6.00", "12.75"), ("3.00", "6.50", "21.00"), ("4.00", "8.00", "27.25"), ("5.00", "8.00", "32.00")]
DIDX = ["count", "mean", "std", "min", "25%", "50%", "75%", "max"]
DTOP = 196 + chight(1) + 24
o.append(df("t-desc", 96, DTOP, CN[:3], DESC, [190, 190, 230], fs=26, rh=60, idx=DIDX, iw=90))
o.append(spot(1, target="t-desc-r1"))
o.append(spot(2, target="t-desc-r2"))
o.append(spot_off(3))
RB = 1060
AX0, AXW = RB + 120, 560
sc_ = AXW / 32
o.append(label(RB, 220, "가장 작은 값부터 가장 큰 값까지", INK, 28, fade(3)))
for k, ((cn, kr, c_, bg), lo, hi) in enumerate(zip(COLS, [1, 5, 8], [5, 8, 32])):
    y = 300 + k * 120
    o.append(label(RB, y + 6, kr, c_, 26, fade(3)))
    o.append(bar(AX0 + lo * sc_, y, (hi - lo) * sc_, 44, c_, WIPE(3) + DELAY(k * 120)))
    o.append(label(AX0 + hi * sc_ + 14, y + 6, f"{lo}~{hi}", c_, 26, fade(3) + DELAY(k * 120)))
o.append(f'<div{fade(3)} style="position:absolute;left:{AX0}px;top:650px;width:{AXW}px;height:3px;background:#9AA0AB"></div>')
for v in [0, 8, 16, 24, 32]:
    o.append(label(AX0 + v * sc_ - 20, 664, str(v), GRAY, 24, fade(3)))
o.append(note(RB, 740, 760, "표준편차(std)는 공부 시간 1.49, 푼 문제 수 8.63이에요. 6배쯤 차이가 나요.", INK, 30, fade(4)))
o.append(caption("큰 숫자 열은 한 걸음만 고쳐도 예측이 크게 흔들려서, 경사 하강법의 걸음이 엉망이 돼요.", 950, 5))
W("describe", o, "수업 셀 52예요. 46에서 본 describe로 열마다 요약 숫자를 봐요. mean은 평균이에요. 공부 시간은 평균 3시간, 수면은 6.7시간, 푼 문제 수는 20.2개예요. std는 표준편차, 곧 평균에서 얼마나 퍼져 있는지예요. 공부 시간은 1.49, 푼 문제 수는 8.63으로 6배쯤 커요. 오른쪽 막대처럼 공부 시간은 1에서 5 사이에, 푼 문제 수는 8에서 32 사이에 퍼져 있어요. 경사 하강법은 모든 기울기를 같은 학습률로 고쳐요. 숫자가 큰 열은 기울기를 조금만 바꿔도 예측이 크게 바뀌어서, 같은 보폭이 그 열에는 너무 커요. 그래서 앞 장처럼 숫자가 터져요. 열마다 크기를 비슷하게 맞추는 일을 특성 스케일링이라고 불러요." + REAL)

o = [sec("standardize")] + head(EB3, "표준화: 평균을 빼고 표준편차로 나눠요. 점 모양은 그대로예요", K3)
CFS[0] = 20
HANDC = ['x = X_train["study_hours"]', "print(list(x))", 'print("평균:", x.mean().round(2))', 'print("표준편차:", x.std(ddof=0).round(2))', 'print("첫 학생:", ((x.iloc[0] - x.mean()) / x.std(ddof=0)).round(2))']
HANDO = ["[1, 5, 3, 1, 5, 4, 3]", "평균: 3.14", "표준편차: 1.55", "첫 학생: -1.38"]
o += cell({"id": "c-hand", "lines": HANDC, "n": 16, "out": HANDO}, 96, 196, 1060, sel="c-hand")
o.append(note(560, oy(196, 5, 1) - 16, 560, "ddof=0: StandardScaler와 같은 방법으로 표준편차 구하기<br>iloc[0]: 첫 줄 꺼내기", GRAY, 22, fade(1)))
FX = 1220
o.append(label(FX, 216, "첫 학생 (공부 1시간)", SUB, 26))
o.append(p(f"position:absolute;left:{FX}px;top:262px;font-family:{MONO};font-size:44px;font-weight:700;line-height:1.4;color:{INK};white-space:nowrap",
           f'(<span style="color:{CS}">1</span> − <span style="color:{OR}">3.14</span>) ÷ <span style="color:{PUR}">1.55</span>'))
o.append(p(f"position:absolute;left:{FX}px;top:336px;font-family:{MONO};font-size:44px;font-weight:700;line-height:1.4;color:{INK};white-space:nowrap", f'= <span style="color:{TR}">−1.38</span>', fade(1)))
o.append(note(FX, 420, 640, "평균보다 표준편차 1.38개만큼 작다는 뜻이에요.", INK, 28, fade(1)))
VALS = [1, 5, 3, 1, 5, 4, 3]
SCV = [-1.38, 1.20, -0.09, -1.38, 1.20, 0.55, -0.09]
MEANH, STDH, PX = 3.14, 1.55, 230
CX0 = 960
hx = lambda v: CX0 + (v - MEANH) * PX
L1, L2 = 650, 860
o.append(f'<div style="position:absolute;left:{hx(0)}px;top:{L1}px;width:{hx(6) - hx(0)}px;height:3px;background:#9AA0AB"></div>')
for v in range(7):
    o.append(label(hx(v) - 8, L1 + 14, str(v), GRAY, 24))
o.append(label(hx(6) + 20, L1 - 14, "시간", GRAY, 24))
seen = {}
for k, v in enumerate(VALS):
    s = seen.get(v, 0); seen[v] = s + 1
    o.append(p(f"position:absolute;left:{hx(v) - 16:.0f}px;top:{L1 - 40 - s * 38}px;width:32px;height:32px;border-radius:50%;background:{CS}", "", f' id="hd{k}"'))
o.append(f'<div{fade(2)} style="position:absolute;left:{hx(MEANH) - 2:.0f}px;top:{L1 - 130}px;width:4px;height:150px;background:{OR}"></div>')
o.append(label(hx(MEANH) + 12, L1 - 130, "평균 3.14", OR, 24, fade(2)))
o.append(f'<div{fade(3)} style="position:absolute;left:{CX0 - 2 * STDH * PX:.0f}px;top:{L2}px;width:{4 * STDH * PX:.0f}px;height:3px;background:{TR}"></div>')
for u in [-2, -1, 0, 1, 2]:
    o.append(label(CX0 + u * STDH * PX - 12, L2 + 14, str(u), TR, 24, fade(3)))
seen = {}
for k, v in enumerate(SCV):
    s = seen.get(v, 0); seen[v] = s + 1
    o.append(p(f"position:absolute;left:{CX0 + v * STDH * PX - 16:.0f}px;top:{L2 - 40 - s * 38}px;width:32px;height:32px;border-radius:50%;background:{TR}", "", fly(3, f"hd{k}")))
o.append(label(CX0 + 2 * STDH * PX + 20, L2 - 14, "표준편차 몇 개", TR, 24, fade(3)))
o.append(caption("점은 그대로 내려왔어요. 눈금만 '시간'에서 '평균에서 표준편차 몇 개'로 바뀌어요.", 960, 4))
W("standardize", o, "열의 크기를 맞추는 방법 중 수업에서 쓴 표준화를 손으로 해 봐요. 학습용 7명의 공부 시간은 1, 5, 3, 1, 5, 4, 3이에요. 평균은 3.14, 표준편차는 1.55예요. 첫 학생의 1시간에서 평균 3.14를 빼고 1.55로 나누면 -1.38이에요. 평균보다 표준편차 1.38개만큼 작다는 뜻이에요. 아래 그림에서 위 줄은 시간 눈금이고, 아래 줄은 바꾼 값의 눈금이에요. 점이 그대로 아래로 내려왔죠. 학생끼리의 순서와 간격은 그대로이고, 눈금만 시간에서 표준편차 몇 개로 바뀌어요. 다른 열도 똑같이 바꾸면 세 열 모두 0 근처, 비슷한 크기가 돼요. ddof=0은 StandardScaler와 같은 방법으로 표준편차를 구하라는 설정이고, iloc[0]은 첫 줄을 꺼내요. 둘 다 이 셀에서만 써요. 이 셀은 이해를 도우려고 더했어요." + REAL)

o = [sec("scaler")] + head(EB3, "StandardScaler: 학습용은 fit_transform, 채점용은 transform", K3)
CFS[0] = 24
o += cell({"id": "c-scale", "lines": SCALEC, "n": 17}, 96, 196, 1728, sel="c-scale")
BXL, BXT, BXW, BXH = 96 + 87, 196, 1728 - 87, len(SCALEC) * LH() + 20
SCT = [(2, "표준화 도구(객체)를 만들어요. 괄호를 비우면 기본 설정", K1), (4, "학습용으로 평균과 표준편차를 재고(fit), 바꿔요(transform)", TR),
       (5, "채점용은 학습용에서 잰 값으로 바꾸기만 해요", TE), (7, "결과는 열 이름 없는 배열이라 이름을 다시 붙여요", SUB)]
TGX = tx(96, SCALEC, 40)
for k, (i, t_, c_) in enumerate(SCT):
    o.append(lspot(1 + k, BXL, BXT, BXW, BXH, BXT + 8 + i * LH(), LH() + 4, "#FFFFFF", c_))
    o.append(tag(TGX, ly(196, i), t_, c_, 1 + k, 26))
o.append(lspot_off(5))
STOP = 196 + chight(len(SCALEC)) + 30
o.append(df("t-scaled", 96, STOP, CN[:3], [tuple(f"{v:.2f}" for v in r) for r in SCALED], [190, 190, 230], fs=24, rh=46, iw=50, attrs=WIPE(5)))
o.append(note(820, STOP + 20, 1000, "값이 모두 0 근처로 모였어요. 왼쪽 번호는 0~6으로 새로 붙었어요(배열에는 원래 번호가 없어요).", INK, 28, fade(6)))
o.append(note(820, STOP + 160, 1000, "-1.65도 있어요. 범위가 -1~+1로 정해지는 게 아니라, 평균이 0, 퍼진 정도가 1이 돼요.", SUB, 28, fade(6)))
W("scaler", o, "수업 셀 53이에요. StandardScaler는 scikit-learn의 preprocessing, 곧 전처리 서랍에 있는 클래스예요. 대문자로 시작하니 괄호로 객체를 만들어요. 24의 붕어빵 틀처럼요. fit_transform은 두 가지를 한 번에 해요. fit으로 학습용 7명의 열마다 평균과 표준편차를 재서 객체 안에 적어 두고, transform으로 앞 장의 계산을 해서 바꾼 표를 돌려줘요. 채점용은 transform만 써요. 학습용에서 잰 평균과 표준편차로 바꾸기만 해요. 결과는 열 이름이 없는 NumPy 배열이라서 pd.DataFrame에 columns=features를 넣어 열 이름을 다시 붙였어요." + SCALE_NOTE + REAL)

o = [sec("fitvt")] + head(EB3, "fit은 자를 만들고, transform은 그 자로 재요. 채점용도 같은 자예요", K3)
CFS[0] = 24
MC = ['print("평균:", scaler.mean_.round(2))', 'print("표준편차:", scaler.scale_.round(2))']
o += cell({"id": "c-mean", "lines": MC, "n": 18, "out": ["평균: [ 3.14  6.86 20.43]", "표준편차: [1.55 1.12 7.89]"]}, 96, 196, 780, sel="c-mean")
o.append(tag(900, ly(196, 0), "끝 밑줄: fit 뒤에 생기는 값 (48의 coef_)", GRAY, None, 24))
FY1, FY2 = 520, 780
o.append(flowbox(96, FY1, 260, 90, "X_train", TR, TRB, 30))
o.append(arrow(60, "#9AA0AB", WIPE(1), f"position:absolute;left:372px;top:{FY1 + 30}px"))
o.append(flowbox(450, FY1, 200, 90, "fit", K1, K1BG, 32, rise(1)))
o.append(arrow(60, "#9AA0AB", WIPE(1), f"position:absolute;left:666px;top:{FY1 + 30}px"))
o.append(f'<div id="ruler"{rise(1)} style="position:absolute;left:744px;top:{FY1 - 60}px;width:600px;height:210px;border-radius:18px;border:3px solid {K1};background:#FFFFFF;padding:20px 28px;display:flex;flex-direction:column;gap:10px">'
         + p(f"font-size:26px;font-weight:700;color:{K1}", "scaler 안에 적어 둔 자")
         + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{INK};white-space:pre", "mean_   3.14  6.86  20.43")
         + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{INK};white-space:pre", "scale_  1.55  1.12   7.89") + '</div>')
o.append(flowbox(96, FY2, 260, 90, "X_test", TE, TEB, 30, rise(2)))
o.append(arrow(60, "#9AA0AB", WIPE(2), f"position:absolute;left:372px;top:{FY2 + 30}px"))
o.append(flowbox(450, FY2, 260, 90, "transform", TE, "#FFFFFF", 30, rise(2), tid="fb-tr"))
o.append(link(3, 1044, FY1 + 152, 580, FY2 - 4, K1, 4))
o.append(label(1060, FY1 + 180, "같은 자로 재요", K1, 26, fade(3)))
o.append(cursor(3, 680, FY2 + 72))
o.append(arrow(60, "#9AA0AB", WIPE(4), f"position:absolute;left:726px;top:{FY2 + 30}px"))
o.append(mono(806, FY2 - 6, ["   study  sleep  practice", "8   0.55  -0.76   1.47", "1  -0.74   1.02  -0.69", "5  -0.74  -1.65  -1.07"], 24, 1.4, INK, rise(4)))
o.append(note(1440, FY2, 380, "채점용 3명의 평균은 0이 아니어도 괜찮아요.", SUB, 26, fade(4)))
o.append(caption("채점용으로 다시 fit 하지 않아요. 새 학생은 학습용 기준으로 재야 해요.", 950, 5))
W("fitvt", o, "scaler 객체 안에 무엇이 적혔는지 봐요. mean_은 열마다 평균, scale_은 열마다 표준편차예요. 학습용 7명으로 잰 값이라서 describe의 10명 평균과 조금 달라요. 48의 coef_처럼 끝에 밑줄이 붙은 이름은 fit을 한 뒤에 생기는 값이에요. 그림으로 보면 fit은 학습용 표로 자를 만드는 일이고, transform은 그 자로 재는 일이에요. 채점용 3명은 새로 자를 만들지 않고 학습용 자로 재요. 채점용은 새 학생 역할이라서, 모델이 배운 기준과 같은 기준으로 재야 해요. 채점용 3명만 보면 평균이 0이 아닌데 그래도 괜찮아요. 아래 숫자는 X_test_scaled에 원래 번호를 붙여 찍은 결과이고, 열 이름은 짧게 줄였어요. 이 셀들은 이해를 도우려고 더했어요." + REAL)

o = [sec("check")] + head(EB3, "바꾼 학습용 표는 열마다 평균 0, 표준편차 1이에요", K3)
CFS[0] = 24
CKC = ['print("평균:", X_train_scaled.mean(axis=0).round(2))', 'print("표준편차:", X_train_scaled.std(axis=0).round(2))']
o += cell({"id": "c-ck", "lines": CKC, "n": 19, "out": ["평균: [0. 0. 0.]", "표준편차: [1. 1. 1.]"]}, 96, 196, 1100, sel="c-ck")
o.append(tint(1, cx(96, 'print("평균:", X_train_scaled.mean(') - 2, ly(196, 0) - LH() / 2, tw("axis=0") + 4, LH(), OR))
o.append(tag(1220, ly(196, 0), "axis=0: 위아래로, 열마다", OR, 1, 26))
o.append(tag(cx(96, "표준편차: [1. 1. 1.]", True) + 24, oyy(196, 2, 1), "세 열 모두 1", GR, 2, 26))
RY = 470
o.append(label(96, RY, "바꾼 뒤 가장 작은 값부터 큰 값까지", INK, 28, fade(3)))
AX1, AXW1 = 400, 900
s1 = AXW1 / 4
for k, ((cn, kr, c_, bg), lo, hi) in enumerate(zip(COLS, [-1.38, -1.65, -1.58], [1.20, 1.02, 1.21])):
    y = RY + 70 + k * 90
    o.append(label(96, y + 6, kr, c_, 26, fade(3)))
    o.append(bar(AX1 + (lo + 2) * s1, y, (hi - lo) * s1, 40, c_, WIPE(3) + DELAY(k * 120)))
o.append(f'<div{fade(3)} style="position:absolute;left:{AX1}px;top:{RY + 345}px;width:{AXW1}px;height:3px;background:#9AA0AB"></div>')
for u in [-2, -1, 0, 1, 2]:
    o.append(label(AX1 + (u + 2) * s1 - 12, RY + 358, str(u), GRAY, 24, fade(3)))
o.append(note(1400, RY + 60, 420, "describe()로 보면 std가 1.08로 나와요. 7로 나누지 않고 6(7 - 1)으로 나누는 방법이라서예요. 둘 다 맞아요.", SUB, 26, fade(4)))
o.append(caption("세 열이 같은 자 위에 올라왔어요. 이제 같은 보폭으로 고쳐도 돼요.", 950, 5))
W("check", o, "바꾼 학습용 표가 정말 평균 0, 표준편차 1인지 확인해요. X_train_scaled는 NumPy 배열이라서 45에서 본 mean을 쓸 수 있어요. axis=0은 위아래 방향, 곧 열마다 계산하라는 뜻이에요. 빼면 9칸 전체의 평균 하나가 나와요. 세 열 모두 평균 0, 표준편차 1이에요. 아래 막대처럼 세 열이 비슷한 범위에 모였어요. scaled_df에 describe를 쓰면 std가 1.08로 나와요. pandas의 std는 개수에서 1을 뺀 6으로 나누고, StandardScaler는 7로 나눠서 생기는 차이예요. 둘 다 맞는 계산이니 신경 쓰지 않아도 돼요. 이 셀은 이해를 도우려고 더했어요." + REAL)

# ---------- part 4 ----------
o = [sec("sgd")] + head(EB4, "크기를 맞춘 표로 SGD를 학습하면 채점용 R²가 0.95예요", K4)
CFS[0] = 22
o += cell({"id": "c-sgd", "lines": SGDC, "n": 20, "out": SGDO}, 96, 196, 980, sel="c-sgd")
SGT = [(1, "손실은 MSE (49)", 1), (2, "보폭을 바꾸지 않아요 (49)", 1), (3, "보폭(학습률) 0.01", 1), (4, "최대 3000 epoch까지", 2), (5, "섞는 순서 고정", 2)]
TX4 = cx(96, '    learning_rate="constant",') + 40
for i, t_, od in SGT:
    o.append(tag(TX4, ly(196, i), t_, K4 if od == 1 else SUB, od, 22))
o.append(tint(3, cx(96, "sgd.fit(") - 2, ly(196, 8) - LH() / 2, tw("X_train_scaled, y_train") + 4, LH(), TR))
o.append(tint(3, cx(96, "sgd_pred = sgd.predict(") - 2, ly(196, 10) - LH() / 2, tw("X_test_scaled") + 4, LH(), TE))
o.append(tag(cx(96, SGDC[8]) + 24, ly(196, 8), "바꾼 학습용", TR, 3, 22))
o.append(tag(cx(96, SGDC[10]) + 24, ly(196, 10), "바꾼 채점용", TE, 3, 22))
NIC = ['print("반복한 epoch:", sgd.n_iter_)', 'print("기울기 w:", sgd.coef_.round(2))', 'print("절편 b:", sgd.intercept_.round(2))']
o += cell({"id": "c-nit", "lines": NIC, "n": 21, "out": ["반복한 epoch: 197", "기울기 w: [9.37 3.47 3.86]", "절편 b: [67.43]"]}, 1090, 196, 734, attrs=rise(4))
o.append(underline(5, 1090 + 85 + 20 + tw("반복한 epoch: ") - 4, 1090 + 85 + 20 + tw("반복한 epoch: 197") + 4, oyy(196, 3, 0) + LH() / 2 + 2, OR))
o.append(note(1090 + 85, 196 + chight(3, 3) + 30, 620, "3000까지 가지 않고 197번째에 멈췄어요. 손실이 거의 줄지 않으면 스스로 멈춰요.", INK, 26, fade(5)))
o.append(note(1090 + 85, 196 + chight(3, 3) + 170, 620, "절편 67.43은 학습용 7명의 평균 점수와 거의 같아요. 바꾼 값이 모두 0인 학생, 곧 평균 학생의 점수예요.", SUB, 26, fade(5)))
W("sgd", o, "수업 셀 55예요. 49에서 배운 SGDRegressor를 세 열에 써요. loss는 MSE, learning_rate는 constant로 보폭을 바꾸지 않고, eta0는 보폭 0.01이에요. max_iter는 epoch를 최대 몇 번까지 돌지예요. 이번에는 fit에 바꾼 학습용 표를, predict에 바꾼 채점용 표를 넣었어요. 채점용 R제곱은 0.9456이에요. 오른쪽 셀을 보면 3000번을 다 돌지 않고 197번째 epoch에서 멈췄어요. 손실이 더 줄지 않으면 스스로 멈추는 설정이 기본으로 켜져 있어서예요. 절편 67.43은 바꾼 값이 모두 0인 학생, 곧 세 열 모두 평균인 학생의 예측 점수예요. 수업 셀의 주석은 두 줄이 서로 바뀌어 있어서 빼고 이 장의 설명으로 대신했어요. 오른쪽 셀은 이해를 도우려고 더했어요." + REAL, ("p4", "SGD로 세 열 배우기"))

o = [sec("loop")] + head(EB4, "partial_fit 반복으로 epoch마다 기울기 셋과 MSE를 적어 둬요", K4)
CFS[0] = 20
LOOPC = ["sgd = SGDRegressor(", '    loss="squared_error",', '    learning_rate="constant",', "    eta0=0.01,", "    random_state=42", ")", "", "epochs = 500", "history = []", "",
         "for epoch in range(epochs):", "    sgd.partial_fit(X_train_scaled, y_train)", "    pred = sgd.predict(X_train_scaled)", "    history.append({", '        "epoch": epoch + 1,',
         '        "w1": sgd.coef_[0],', '        "w2": sgd.coef_[1],', '        "w3": sgd.coef_[2],', '        "bias": sgd.intercept_[0],', '        "mse": mean_squared_error(y_train, pred),', "    })", "",
         "history_df = pd.DataFrame(history)", "history_df.round(2).tail()"]
o += cell({"id": "c-loop", "lines": LOOPC, "n": 22}, 96, 196, 900, sel="c-loop")
LBX, LBW, LBH = 96 + 87, 900 - 87, len(LOOPC) * LH() + 20
o.append(lspot(1, LBX, 196, LBW, LBH, 196 + 8 + 11 * LH(), LH() + 4, "#FFFFFF", K4))
o.append(tag(cx(96, LOOPC[11]) + 20, ly(196, 11), "한 epoch씩 (49)", K4, 1, 22))
o.append(lspot(2, LBX, 196, LBW, LBH, 196 + 8 + 15 * LH(), 3 * LH() + 4, "#FFFFFF", K4))
o.append(tag(cx(96, LOOPC[15]) + 60, ly(196, 16), "기울기 셋: coef_[0], [1], [2]", K4, 2, 22))
o.append(lspot_off(3))
HC = ["epoch", "w1", "w2", "w3", "bias", "mse"]
HW = [90, 76, 76, 76, 96, 120]
o.append(label(1050, 200, "처음 3 epoch (head(3))", SUB, 24, fade(3)))
o.append(df("t-head", 1050, 236, HC, [(1, "0.81", "0.34", "0.82", "4.65", "4084.14"), (2, "1.52", "0.64", "1.53", "8.98", "3527.52"), (3, "2.14", "0.90", "2.15", "13.01", "3048.06")], HW, fs=22, rh=42, iw=56, attrs=rise(3)))
o.append(label(1050, 440, "마지막 5 epoch (tail())", SUB, 24, fade(4)))
TAIL = [(496, "9.92", "3.62", "3.29", "67.42", "0.14"), (497, "9.92", "3.62", "3.29", "67.42", "0.14"), (498, "9.92", "3.62", "3.29", "67.42", "0.14"), (499, "9.93", "3.62", "3.29", "67.42", "0.14"), (500, "9.93", "3.62", "3.29", "67.42", "0.14")]
o.append(df("t-tail", 1050, 476, HC, TAIL, HW, fs=22, rh=42, idx=[495, 496, 497, 498, 499], iw=56, attrs=rise(4)))
MX = 1050 + 56 + sum(HW[:5])
o.append(box(5, MX - 4, 236 + 42 + 2, HW[5] + 20, 42, RED, 4, 8))
o.append(box(5, MX - 4, 476 + 42 * 5 + 2, HW[5] + 20, 42, GR, 4, 8))
o.append(note(1050, 760, 770, "MSE가 4084에서 0.14로 줄었어요. 뒤쪽 epoch는 기울기가 거의 안 바뀌어요.", INK, 28, fade(5)))
W("loop", o, "수업 셀 56이에요. 49에서 본 partial_fit 반복과 같아요. partial_fit은 부를 때마다 학습용 7명을 한 번 훑는 한 epoch만 배워요. 500번 반복하면서 epoch마다 기울기, 절편, MSE를 딕셔너리로 만들어 history 리스트에 쌓았어요. 49와 다른 점은 기울기가 셋이라서 coef_의 0번, 1번, 2번 칸을 w1, w2, w3로 꺼낸 것뿐이에요. 오른쪽은 처음 세 줄과 마지막 다섯 줄이에요. MSE가 4084에서 0.14로 줄었고, 마지막 다섯 epoch에서는 기울기가 거의 바뀌지 않아요. MSE를 학습용으로 쟀으니 0.14는 학습용 점수예요. 처음 세 줄을 찍는 셀은 이해를 도우려고 더했어요." + REAL)

o = [sec("curve")] + head(EB4, "기울기 셋이 epoch마다 어떻게 바뀌는지 한 그래프에 그려요", K4)
CFS[0] = 20
WCC = ["fig, ax = plt.subplots(figsize=(10, 5))", "", 'ax.plot(history_df["epoch"], history_df["w1"], label="study")', 'ax.plot(history_df["epoch"], history_df["w2"], label="sleep")',
       'ax.plot(history_df["epoch"], history_df["w3"], label="count")', "", 'ax.set_title("기울기 w1, w2, w3의 변화")', 'ax.set_xlabel("epoch")', "ax.legend()", "ax.grid(alpha=0.3)", "plt.show()"]
o += cell({"id": "c-wc", "lines": WCC, "n": 24}, 96, 196, 900, sel="c-wc")
o.append(tint(1, cx(96, 'ax.plot(history_df["epoch"], history_df["w1"], ') - 2, ly(196, 2) - LH() / 2, tw('label="study"') + 4, LH(), K1))
o.append(tag(cx(96, WCC[8]) + 24, ly(196, 8), "label을 모아 범례 상자로 (47)", K1, 1, 22))
o.append(tag(cx(96, WCC[9]) + 24, ly(196, 9), "옅은 눈금선, 0.3은 진하기 (47의 alpha)", SUB, 2, 22))
o.append(img(1000, 196, 824, "main-2.png", tid="im-w"))
o.append(label(96, 196 + chight(11) + 40, "MSE 손실 곡선 (수업 셀 57)", SUB, 24, fade(3)))
o.append(img(96, 196 + chight(11) + 80, 400, "main-1.png", fade(3)))
o.append(note(540, 196 + chight(11) + 90, 420, "손실은 처음 몇십 epoch에 크게 줄고, 그 뒤로는 바닥에 붙어요(49).", SUB, 24, fade(3)))
WY = 196 + imh("main-2.png", 824) + 30
o.append(note(1000, WY, 824, "count(푼 문제 수)는 6 가까이 올랐다가 3.3으로 내려와요. 공부 시간과 같이 오르는 열이라, 점수를 올린 몫을 공부 시간에게 나눠 줬어요(50).", INK, 28, fade(4)))
W("curve", o, "수업 셀 58이에요. 그래프 칸 하나에 plot을 세 번 그려서 기울기 셋의 변화를 한꺼번에 봐요. label은 선마다 붙이는 이름이고, ax.legend가 그 이름을 모아 범례 상자를 그려요. 47에서 본 것처럼 label만 적으면 범례가 나오지 않아요. grid는 옅은 눈금선이고 alpha 0.3은 진하기예요. 공부 시간의 기울기 study는 10 가까이 올라가요. 푼 문제 수 count는 처음에 6 가까이 올랐다가 3.3으로 내려와요. 공부 시간과 푼 문제 수는 같이 오르는 열이라서, 처음에는 둘 다 점수를 올리다가 나중에 공부 시간이 몫을 더 가져가요. 50에서 본 혼자 배운 기울기와 같이 배운 기울기 이야기예요. 왼쪽 아래는 수업 셀 57의 손실 곡선이에요. 수업 코드의 axe는 ax로, plt.legend는 ax.legend로 바꿨고, 제목과 x축 이름을 더했어요. 셀 57의 둘째 그래프(w1 하나)는 이 그래프에 들어 있어서 뺐어요." + IMGN)

o = [sec("barh")] + head(EB4, "가로 막대로 기울기 비교: 크기를 맞춰야 나란히 볼 수 있어요", K4)
BP = [("plt.barh(", W_), ('coef_df["feature"]', "#9CC2F5"), (", ", W_), ('coef_df["weight"]', "#F2C46D"), (", ", W_), ('color="blue"', "#C7B5F5"), (")", W_)]
o.append(strip_parts(96, 196, 1728, 100, BP, 36))
xs, _ = sline(96, 196, BP, 36)
for k, (i, t_, c_) in enumerate([(1, "막대 이름 (세로로 늘어서요)", CS), (3, "막대 길이", OR), (5, "막대 색", PUR)]):
    o.append(lead_down(1 + k, xs[i] + tw(BP[i][0], 36) / 2, 280, 320, c_, t_, 24))
IW = 760
o.append(label(96, 400, "LinearRegression, 원래 단위", SUB, 26, fade(4)))
o.append(img(96, 444, IW, "main-4.png", fade(4), tid="im-raw"))
o.append(label(960, 400, "SGD 500 epoch, 크기를 맞춘 열", K4, 26, fade(5)))
o.append(img(960, 444, IW, "main-3.png", fade(5), tid="im-sc"))
o.append(grow(6, "im-sc"))
o.append(caption("푼 문제 수: 0.41(문제 1개에) → 3.29(표준편차 7.89개에). 같은 자로 재야 막대를 비교할 수 있어요.", 950, 6))
W("barh", o, "기울기를 가로 막대로 비교해 봐요. barh는 가로 막대 그래프를 그려요. 첫째 칸은 막대 이름, 둘째 칸은 막대 길이, color는 색이에요. coef_df는 열 이름과 기울기를 45처럼 딕셔너리로 묶은 표예요. 왼쪽은 크기를 안 맞춘 LinearRegression의 기울기예요. 푼 문제 수는 0.41로 아주 작아 보여요. 문제 1개당 0.41점이라서 그래요. 오른쪽은 크기를 맞춘 SGD의 기울기예요. 이번에는 문제 수가 3.29로 수면 시간과 비슷해요. 표준편차 하나, 곧 문제 7.89개만큼 늘 때 3.29점이라는 뜻이에요. 크기를 맞춰야 같은 자로 잰 기울기가 돼서 막대를 나란히 비교할 수 있어요. 오른쪽 그래프는 셀 56의 500 epoch를 마친 sgd로 그려서, 앞 장의 197 epoch 숫자와 조금 달라요. 이 장의 두 그래프는 이해를 도우려고 더했어요." + IMGN)

o = [sec("vs")] + head(EB4, "LinearRegression과 SGDRegressor 나란히 보기", K4)
VR = [("찾는 방법", "공식으로 한 번에 계산", "조금씩 고쳐 가며 (경사 하강법)"), ("스케일링", "없어도 돼요", "꼭 해요"), ("fit에 넣는 표", "X_train", "X_train_scaled"),
      ("predict에 넣는 표", "X_test", "X_test_scaled"), ("기울기 읽기", "원래 단위 1만큼", "표준편차 1개만큼"), ("채점용 R²", "0.9327", "0.9456"), ("채점용 MAE", "3.09점", "2.82점")]
o += plain_rows(96, 210, 1728, VR, [360, 620, 640], 1, 82, ("", "LinearRegression (48)", "SGDRegressor (49, 오늘)"), 30)
o.append(caption("채점용이 3명뿐이라 0.93과 0.95의 차이는 운일 수 있어요. 6파트에서 확인해요.", 950, 8))
W("vs", o, "두 모델을 나란히 봐요. LinearRegression은 오차 제곱 합이 가장 작은 기울기를 공식으로 한 번에 계산해요. 그래서 열 크기가 달라도 괜찮아요. SGDRegressor는 49처럼 조금씩 고쳐 가며 찾아서, 열 크기를 꼭 맞춰야 해요. 그래서 fit과 predict에 넣는 표도 바꾼 표예요. 기울기도 SGD 쪽은 표준편차 1개만큼으로 읽어요. 채점 점수는 SGD가 조금 높은데, 채점용이 3명뿐이라 이 차이로 어느 쪽이 낫다고 말하기는 어려워요. 6파트에서 random_state만 바꿔도 점수가 크게 바뀌는 것을 봐요." + REAL)

# ---------- part 5 ----------
o = [sec("e-order")] + head(EB5, "네 칸 순서를 바꿔 적으면 y_train에 X_test가 들어가요", K5)
CFS[0] = 24
EOC = ["X_train, y_train, X_test, y_test = train_test_split(", "    X, y, test_size=0.3, random_state=42", ")", 'print("y_train:", y_train.shape)']
o += cell({"id": "c-eo", "lines": EOC, "n": 25, "out": ["y_train: (3, 3)"]}, 96, 196, 1728)
o.append(tint(1, cx(96, "X_train, ") - 2, ly(196, 0) - LH() / 2, tw("y_train") + 4, LH(), RED))
o.append(tag(cx(96, EOC[0]) + 30, ly(196, 0), "둘째 자리는 X_test 자리예요", RED, 1, 26))
o.append(box(2, cx(96, "y_train: ", True) - 12, oyy(196, 4, 0) - LH() / 2 - 6, tw("(3, 3)") + 24, LH() + 12, RED, 4))
o.append(tag(cx(96, "y_train: (3, 3)", True) + 30, oyy(196, 4, 0), "정답이 아니라 채점용 문제 3줄 3열", RED, 2, 26))
EY = 196 + chight(4, 1) + 30
o += cell({"id": "c-eo2", "lines": ["m = LinearRegression()", "m.fit(X_train, y_train)"], "n": 26, "out": ["ValueError: Found input variables with inconsistent numbers of samples: [7, 3]"], "err": True}, 96, EY, 1728, attrs=rise(3))
o.append(reading(96, EY + chight(2, 1) + 30, "문제는 7줄인데 정답은 3줄이라서 짝이 안 맞는다는 뜻이에요.", INK, 4, 30))
o.append(fix(96, EY + chight(2, 1) + 120, "X_train, y_train, X_test, y_test", "X_train, X_test, y_train, y_test", 5, 28))
W("e-order", o, "자주 하는 실수예요. 받는 이름을 X_train, y_train, X_test, y_test 순서로 적었어요. train_test_split은 이름을 보지 않고 자리 순서대로 담아요. 그래서 둘째 자리의 y_train에는 X_test가, 셋째 자리의 X_test에는 y_train이 들어가요. y_train의 모양이 3줄 3열로 찍혀요. 이 상태로 fit을 하면 문제는 7줄인데 정답은 3줄이라 짝이 안 맞는다는 ValueError가 나요. 순서는 X 학습, X 채점, y 학습, y 채점이에요. 나눈 뒤에 shape부터 찍어 보면 바로 알 수 있어요." + REAL, ("p5", "오류와 함정"))

o = [sec("e-refit")] + head(EB5, "채점용에 fit_transform을 쓰면 오류 없이 점수가 떨어져요", K5)
CFS[0] = 22
ER1 = ["wrong = StandardScaler().fit_transform(X_test)", "print(pd.DataFrame(X_test_scaled, columns=features).round(2))", "print(pd.DataFrame(wrong, columns=features).round(2))"]
o += cell({"id": "c-er1", "lines": ER1, "n": 27}, 96, 196, 1000)
o.append(tint(1, cx(96, "wrong = StandardScaler().") - 2, ly(196, 0) - LH() / 2, tw("fit_transform(X_test)") + 4, LH(), RED))
o.append(tag(cx(96, ER1[0]) + 20, ly(196, 0), "채점용 3명으로 새 자", RED, 1, 22))
ER2 = ["wrong_pred = sgd.predict(wrong)", 'print("정답:", list(y_test))', 'print("transform:", sgd_pred.round(1))', 'print("fit_transform:", wrong_pred.round(1))', 'print(f"R2: {r2_score(y_test, wrong_pred):.4f}")']
E2Y = 196 + chight(3) + 24
o += cell({"id": "c-er2", "lines": ER2, "n": 28, "out": ["정답: [79, 58, 49]", "transform: [75.6 61.4 50.7]", "fit_transform: [85.2 63.4 53.7]", "R2: 0.8114"]}, 96, E2Y, 1000, attrs=rise(2))
o.append(underline(3, cx(96, "R2: ", True), cx(96, "R2: 0.8114", True), oyy(E2Y, 5, 3) + LH() / 2 + 2, RED, 5))
o.append(note(96 + 85, E2Y + chight(5, 4) + 20, 900, "transform으로 재면 R² 0.9456이었어요(4파트).", SUB, 26, fade(3)))
TX5 = 1160
o.append(label(TX5, 210, "transform: 학습용 자 (맞아요)", GR, 26))
TA = ["   study  sleep  practice", "0   0.55  -0.76   1.47", "1  -0.74   1.02  -0.69", "2  -0.74  -1.65  -1.07"]
TB_ = ["   study  sleep  practice", "0   1.41  -0.27   1.40", "1  -0.71   1.34  -0.53", "2  -0.71  -1.07  -0.87"]
o.append(mono(TX5, 256, TA, 26, 1.5, INK))
o.append(label(TX5, 500, "fit_transform: 채점용 3명으로 새 자", RED, 26, fade(1)))
o.append(mono(TX5, 546, TB_, 26, 1.5, INK, rise(1)))
VX = TX5 + 26 * 0.6 * 4
o.append(box(2, VX - 8, 256 + 26 * 1.5 - 2, 26 * 0.6 * 4 + 16, 26 * 1.5 + 4, GR, 4, 8))
o.append(box(2, VX - 8, 546 + 26 * 1.5 - 2, 26 * 0.6 * 4 + 16, 26 * 1.5 + 4, RED, 4, 8))
o.append(note(TX5, 780, 660, "8번 학생의 공부 시간이 0.55에서 1.41로 바뀌었어요. 모델은 공부를 훨씬 많이 한 학생으로 읽어요.", INK, 26, fade(3)))
W("e-refit", o, "채점용 표에 transform 대신 fit_transform을 쓰면 어떻게 될까요. 채점용 3명만으로 평균과 표준편차를 새로 재서 다른 자가 만들어져요. 오른쪽 두 표를 비교해 봐요. 8번 학생의 공부 시간이 학습용 자로는 0.55인데, 새 자로는 1.41이 됐어요. 모델은 학습용 자로 배웠으니 이 학생을 공부를 훨씬 많이 한 학생으로 읽어요. 예측이 85.2점으로 올라가고 R제곱이 0.9456에서 0.8114로 떨어졌어요. 오류는 나지 않아서 더 찾기 어려워요. 채점용과 새 학생은 늘 transform만 써요. 출력 표의 열 이름은 짧게 줄였어요." + REAL)

o = [sec("e-noscale")] + head(EB5, "바꾸지 않은 X_test를 predict에 넣으면 249점이 나와요", K5)
CFS[0] = 24
o += cell({"id": "c-en", "lines": ["bad = sgd.predict(X_test)", 'print("예측:", bad.round(1))'], "n": 29,
           "out": ["UserWarning: X has feature names, but SGDRegressor was fitted without feature names", "예측: [249.3 171.9 149.9]"], "red": (0,)}, 96, 196, 1728)
o.append(tint(1, cx(96, "bad = sgd.predict(") - 2, ly(196, 0) - LH() / 2, tw("X_test") + 4, LH(), RED))
o.append(tag(cx(96, "bad = sgd.predict(X_test)") + 30, ly(196, 0), "바꾸지 않은 원래 표", RED, 1, 26))
o.append(spot(2, 96 + 85, oyy(196, 2, 0) - LH() / 2, 1728 - 85, LH()))
o.append(reading(96, 196 + chight(2, 2) + 40, "경고: 열 이름이 있는 표를 넣었는데, 학습할 때는 열 이름 없는 배열이었다는 뜻이에요.", INK, 2, 30))
o.append(spot_off(3))
BY = 560
for k, (i, t_, pr) in enumerate([(8, 79, 249.3), (1, 58, 171.9), (5, 49, 149.9)]):
    y = BY + k * 90
    o.append(stu(i, 96, y, TE, TEB, 56, rise(3) + DELAY(k * 100)))
    o.append(bar(180, y + 4, t_ * 3.4, 22, CY, WIPE(3) + DELAY(k * 100)))
    o.append(bar(180, y + 30, pr * 3.4, 22, RED, WIPE(3) + DELAY(k * 100 + 60)))
    o.append(label(190 + pr * 3.4, y + 12, f"정답 {t_} · 예측 {pr}", INK, 26, rise(3) + DELAY(k * 100)))
o.append(fix(96, 860, "sgd.predict(X_test)", "sgd.predict(X_test_scaled)", 4, 30))
W("e-noscale", o, "SGD 모델은 바꾼 표로 배웠는데, predict에 바꾸지 않은 원래 X_test를 넣었어요. 경고가 하나 나와요. 열 이름이 있는 표를 넣었는데 학습할 때는 열 이름이 없는 배열이었다는 뜻이에요. 경고만 보면 별일 아닌 것 같지만 진짜 문제는 값이에요. 공부 시간 4시간을 표준편차 4개로 읽어서 예측이 249점처럼 터무니없이 커져요. 스케일링으로 학습한 모델에는 predict 전에 늘 scaler.transform을 거친 표를 넣어요. 실제 화면에는 경고 앞에 파일 경로가 길게 붙어요. 이 셀은 이해를 도우려고 더했어요." + REAL)

o = [sec("e-read")] + head(EB5, "바꾼 열의 기울기 9.37은 '1시간에 9.37점'이 아니에요", K5)
CFS[0] = 24
RDC1 = ['print("공부 시간 표준편차:", scaler.scale_[0].round(2), "시간")', 'print("기울기 w1:", sgd.coef_[0].round(2))']
o += cell({"id": "c-rd1", "lines": RDC1, "n": 30, "out": ["공부 시간 표준편차: 1.55 시간", "기울기 w1: 9.37"]}, 96, 196, 1100)
RDC2 = ['a = pd.DataFrame({"study_hours": [3, 4], "sleep_hours": [7, 7], "practice_count": [20, 20]})', "pa = sgd.predict(scaler.transform(a))",
        'print("3시간, 4시간:", pa.round(2), "차이:", (pa[1] - pa[0]).round(2))']
R2Y = 196 + chight(2, 2) + 24
o += cell({"id": "c-rd2", "lines": RDC2, "n": 31, "out": ["3시간, 4시간: [66.8  72.83] 차이: 6.04"]}, 96, R2Y, 1728, attrs=rise(1))
o.append(box(2, cx(96, "3시간, 4시간: [66.8  72.83] 차이: ", True) - 24, oyy(R2Y, 3, 0) - LH() / 2 - 6, tw("6.04") + 32, LH() + 12, RED, 4))
GY = R2Y + chight(3, 1) + 120
SX0, PXH = 300, 360
o.append(label(96, GY + 8, "공부 시간", CS, 28, fade(3)))
o.append(f'<div{fade(3)} style="position:absolute;left:{SX0}px;top:{GY + 24}px;width:{PXH * 3.6:.0f}px;height:3px;background:#9AA0AB"></div>')
for h_ in range(4):
    o.append(label(SX0 + h_ * PXH - 30, GY + 40, f"+{h_}시간", GRAY, 22, fade(3)))
o.append(bar(SX0, GY - 40, PXH, 30, K1, WIPE(3)))
o.append(label(SX0 + PXH + 14, GY - 42, "1시간 → +6.04점", K1, 26, fade(3)))
o.append(bar(SX0, GY + 90, PXH * 1.55, 30, TR, WIPE(4)))
o.append(label(SX0 + PXH * 1.55 + 14, GY + 88, "표준편차 1개 = 1.55시간 → +9.37점", TR, 26, fade(4)))
o.append(caption("시간 단위로 읽으려면 9.37 ÷ 1.55 = 6.04예요. LinearRegression의 6.43과 비슷해요.", 950, 5))
W("e-read", o, "바꾼 열로 배운 기울기를 원래 단위로 읽는 실수예요. 공부 시간의 기울기 9.37은 1시간 늘 때 9.37점이 아니라, 표준편차 하나만큼, 곧 1.55시간 늘 때 9.37점이에요. 확인하려고 다른 열은 그대로 두고 공부 시간만 3시간과 4시간인 학생을 예측했어요. 차이는 6.04점이에요. 9.37을 1.55로 나눈 값과 같아요. 크기를 안 맞춘 LinearRegression의 기울기 6.43과 비슷하죠. 두 모델이 배운 내용은 같고 단위만 달라요. 이 셀들은 이해를 도우려고 더했어요." + REAL)

# ---------- part 6 ----------
o = [sec("x-new")] + head(EB6, "새 학생 예측: 학습용 자로 바꾼 다음 predict에 넣어요", K6)
CFS[0] = 22
NWC = ["new = pd.DataFrame({", '    "study_hours": [4],', '    "sleep_hours": [7],', '    "practice_count": [30],', "})", "new_scaled = scaler.transform(new)", "print(new_scaled.round(2))",
       'print("SGD:", sgd.predict(new_scaled).round(2))', 'print("LinearRegression:", test_model.predict(new).round(2))']
o += cell({"id": "c-new", "lines": NWC, "n": 32, "out": ["[[0.55 0.13 1.21]]", "SGD: [77.73]", "LinearRegression: [77.32]"]}, 96, 196, 1100, sel="c-new")
o.append(hl(96, 196, 1100, 5, 1, "mark", 1))
NY, ST = 230, 150
FL = [("4시간, 7시간, 30문제", INK, "#FFFFFF", False), ("scaler.transform", TR, TRB, True), ("0.55   0.13   1.21", TR, "#FFFFFF", True), ("sgd.predict  →  77.73점", K4, K4BG, True)]
for k, (t_, c_, bg, m_) in enumerate(FL):
    o.append(flowbox(1240, NY + k * ST, 584, 84, t_, c_, bg, 30, rise(k) if k else "", mono_=m_))
    if k:
        o.append(f'<svg{WIPE(k)} style="position:absolute;left:1512px;top:{NY + k * ST - 62}px;width:40px;height:56px" viewBox="0 0 40 56"><rect x="13" y="0" width="14" height="32" fill="#9AA0AB"/><polygon points="2,30 38,30 20,54" fill="#9AA0AB"/></svg>')
o.append(note(1240, NY + 4 * ST, 584, "LinearRegression은 바꾸지 않은 표로 77.32점. 두 모델이 0.4점 차이예요.", SUB, 26, fade(4)))
o.append(caption("transform을 빼먹으면 245점이 나와요(5파트). 새 학생도 학습용 자로 재요.", 950, 5))
W("x-new", o, "실제로 써 봐요. 공부 4시간, 수면 7시간, 문제 30개를 푼 새 학생의 점수를 예측해요. 50처럼 열 이름이 같은 표를 만들고, SGD 모델에 넣기 전에 scaler.transform으로 바꿔요. fit_transform이 아니라 transform이에요. 학습용 7명으로 만든 자로 재야 해요. 바꾼 값은 0.55, 0.13, 1.21이고 예측은 77.73점이에요. LinearRegression은 스케일링이 필요 없어서 원래 표를 그대로 넣었고 77.32점이 나왔어요. transform을 빼먹고 sgd.predict(new)를 하면 경고와 함께 245점이 나와요." + REAL, ("p6", "실제 상황"))

o = [sec("x-seed")] + head(EB6, "random_state만 바꿔도 3명 채점 점수가 0.89에서 0.98까지 흔들려요", K6)
CFS[0] = 22
SEC = ["for seed in [0, 1, 2, 3, 42]:", "    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=seed)", "    m = LinearRegression()",
       "    m.fit(X_train, y_train)", "    r2 = r2_score(y_test, m.predict(X_test))", '    print(f"random_state={seed:2} 채점용 {list(X_test.index)} R2 {r2:.2f}")']
SEO = ["random_state= 0 채점용 [2, 8, 4] R2 0.97", "random_state= 1 채점용 [2, 9, 6] R2 0.89", "random_state= 2 채점용 [4, 1, 5] R2 0.98", "random_state= 3 채점용 [5, 4, 1] R2 0.98", "random_state=42 채점용 [8, 1, 5] R2 0.93"]
o += cell({"id": "c-seed", "lines": SEC, "n": 33, "out": SEO}, 96, 196, 1728, sel="c-seed")
SB0 = 870
for k, (sd, v) in enumerate([(0, 0.97), (1, 0.89), (2, 0.98), (3, 0.98), (42, 0.93)]):
    x = SB0 + k * 190
    hgt = (v - 0.8) * 1800
    c_ = RED if sd == 1 else TE
    o.append(bar(x, 860 - hgt, 110, hgt, c_, WIPE(1) + DELAY(k * 100)))
    o.append(label(x + 22, 860 - hgt - 40, f"{v:.2f}", c_, 28, fade(1) + DELAY(k * 100)))
    o.append(label(x + 30 if sd < 10 else x + 22, 874, str(sd), GRAY, 24, fade(1)))
o.append(f'<div{fade(1)} style="position:absolute;left:{SB0 - 20}px;top:860px;width:{5 * 190}px;height:3px;background:#9AA0AB"></div>')
o.append(label(SB0 - 20, 430, "random_state마다 채점용 R² (막대는 0.8부터)", SUB, 24, fade(1)))
o.append(caption("채점용이 몇 명뿐이면 점수가 운에 흔들려요. 데이터가 많을수록 점수를 믿을 수 있어요.", 950, 2))
W("x-seed", o, "random_state만 0, 1, 2, 3, 42로 바꿔 가며 나누고, 같은 LinearRegression으로 채점했어요. 13의 f-string 칸 수 맞추기로 줄을 맞췄어요. 채점용 학생이 바뀔 때마다 R제곱이 0.89에서 0.98까지 달라져요. 학생이 10명뿐이라 채점용 3명이 누구냐에 따라 점수가 크게 흔들려요. 그래서 4파트의 0.93과 0.95 차이로 어느 모델이 낫다고 말하기 어려워요. 데이터가 많으면 채점용도 많아져서 점수가 덜 흔들려요. 여러 번 나눠 평균을 내는 방법도 있는데 오늘은 다루지 않아요. 오른쪽 막대는 R제곱 0.8부터 그렸어요. 이 셀은 이해를 도우려고 더했어요." + REAL)

o = [sec("x-office")] + head(EB6, "47의 오피스텔 200건: 나눠서 채점하고, 49에서 터진 SGD 살리기", K6)
CFS[0] = 22
OFC = ['office = pd.read_csv("datasets/office.csv")', 'Xo = office[["area"]]', 'yo = office["price"]', "",
       "Xo_train, Xo_test, yo_train, yo_test = train_test_split(Xo, yo, test_size=0.2, random_state=42)", "print(Xo_train.shape, Xo_test.shape)"]
o += cell({"id": "c-of1", "lines": OFC, "n": 34, "out": ["(160, 1) (40, 1)"]}, 96, 196, 1728, sel="c-of1")
OF2 = ["sc = StandardScaler()", "Xo_train_s = sc.fit_transform(Xo_train)", "Xo_test_s = sc.transform(Xo_test)", "",
       'sg = SGDRegressor(loss="squared_error", learning_rate="constant", eta0=0.01, max_iter=3000, random_state=42)', "sg.fit(Xo_train_s, yo_train)",
       'print(f"스케일링하고: 채점용 R2 {r2_score(yo_test, sg.predict(Xo_test_s)):.3f}")', 'print(f"채점용 MAE: {mean_absolute_error(yo_test, sg.predict(Xo_test_s)):.0f}")']
O2Y = 196 + chight(6, 1) + 24
o += cell({"id": "c-of2", "lines": OF2, "n": 37, "out": ["스케일링하고: 채점용 R2 0.916", "채점용 MAE: 1904"]}, 96, O2Y, 1728, attrs=rise(1))
o.append(hl(96, O2Y, 1728, 1, 2, "run", 1, "크기 맞추기"))
o.append(zoom(2, 96 + 85, oyy(O2Y, 8, 0) - LH() / 2 - 10, 800, 2 * LH() + 20, 60, 2))
o.append(zoom_off(3))
TBY = O2Y + chight(8, 2) + 30
OR3 = [("스케일링 없이 SGD (셀 36)", "기울기 -4.296e+11", "터져요"), ("크기 맞추고 SGD", "R² 0.916, MAE 1904", "살았어요"), ("LinearRegression (셀 35)", "R² 0.917, MAE 1899", "기준")]
for k, (a_, b_, c_) in enumerate(OR3):
    y = TBY + k * 54
    col = RED if k == 0 else (GR if k == 1 else SUB)
    o.append(p(f"position:absolute;left:96px;top:{y}px;width:1728px;font-size:28px;font-weight:700;color:{col};white-space:pre", e(f"{a_:<0}") + f'<span style="position:absolute;left:520px;font-family:{MONO}">{e(b_)}</span><span style="position:absolute;left:1100px">{e(c_)}</span>', rise(3) + DELAY(k * 100)))
W("x-office", o, "47에서 만든 오피스텔 200건을 꺼내요. 49에서는 면적을 그대로 SGD에 넣었다가 eta0 0.01에서 숫자가 터졌어요. 이번에는 먼저 160건과 40건으로 나눠요. test_size 0.2라서 40건이 채점용이에요. 그다음 학습용 면적으로 StandardScaler를 fit_transform하고, 채점용은 transform해요. 같은 eta0 0.01로 SGD를 학습하면 채점용 R제곱이 0.916이에요. 스케일링 없이 같은 설정으로 돌린 셀 36은 기울기가 마이너스 4천억이 넘게 터졌어요. LinearRegression은 채점용 R제곱 0.917, MAE 1899로 거의 같아요. LinearRegression의 학습용 R제곱은 0.784로 채점용보다 낮은데, 47에서 넣은 특이 매물 5건이 모두 학습용에 들어갔기 때문이에요. 셀 35와 36은 이 장에서 결과만 옮겼어요. 이 셀들은 이해를 도우려고 더했어요." + REAL)

# ---------- closing ----------
o = [sec("trouble")] + head("정리", "막히면 출력의 마지막 줄과 shape부터 봐요", RED)
TBL = [("ValueError: Found input variables with inconsistent numbers of samples", "네 칸 이름 순서를 바꿔 적었어요", "X_train, X_test, y_train, y_test"),
       ("기울기 w: [ 3.36938078e+10 ...]", "크기를 안 맞춘 표로 SGD를 학습했어요", "scaler.fit_transform(X_train)"),
       ("UserWarning: X has feature names, but SGDRegressor was fitted ...", "바꾸지 않은 표를 predict에 넣었어요", "scaler.transform(X_test)"),
       ("채점 점수가 오류 없이 떨어져요 (R2 0.81)", "채점용에 fit_transform을 썼어요", "transform만"),
       ("실행할 때마다 채점용 학생이 달라요", "random_state를 안 적었어요", "random_state=42")]
for i, (q, a_, cmd) in enumerate(TBL):
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:96px;top:{196 + i * 128}px;width:1728px;height:128px;display:flex;flex-direction:row;align-items:center;gap:26px;border-bottom:2px solid {LINE}">'
             + '<div style="flex:1;display:flex;flex-direction:column;gap:4px">' + p(f"{'font-family:' + MONO + ';' if q.isascii() else ''}font-size:24px;font-weight:700;color:{RED};white-space:nowrap", e(q)) + p(f"font-size:26px;color:{INK}", e(a_)) + '</div>'
             + p(f"width:560px;flex:none;font-family:{MONO};font-size:24px;font-weight:700;color:{GR};white-space:pre", '✓ ' + e(cmd)) + '</div>')
o.append(caption("나눈 뒤 shape, 바꾼 뒤 평균과 표준편차를 한 번씩 찍어 보면 대부분 잡혀요.", 900))
W("trouble", o, "막히면 출력의 마지막 줄부터 읽어요. 첫째는 네 칸 순서 실수예요. 둘째와 셋째는 스케일링을 빼먹은 경우예요. SGD로 배울 때는 학습용을 fit_transform, predict에 넣는 표는 transform이에요. 넷째와 다섯째는 오류가 나지 않는 함정이에요. 채점 점수가 이상하게 낮거나 매번 다르면 fit_transform과 random_state를 확인해요.", ("trouble", "정리"))

o = [sec("recap")] + head("정리", "처음 보는 데이터로 채점하는 네 단계", K1)
STEPS = [("나누기", "train_test_split(X, y, test_size=0.3, random_state=42)", "학습용 7명, 채점용 3명", K2),
         ("크기 맞추기", "scaler.fit_transform(X_train)\nscaler.transform(X_test)", "학습용으로 자를 만들고, 같은 자로", K3),
         ("학습", "sgd.fit(X_train_scaled, y_train)", "학습용만 넣어요", K4),
         ("채점", "r2_score(y_test, sgd.predict(X_test_scaled))", "채점용 정답과 비교", TE)]
for i, (h_, code, d, c_) in enumerate(STEPS):
    y = 200 + i * 150
    o.append(f'<div{rise(1 + i)} style="position:absolute;left:96px;top:{y}px;width:1728px;height:130px;display:flex;flex-direction:row;align-items:center;gap:30px;border-bottom:2px solid {LINE}">'
             + num(i + 1, c_, 40) + p(f"width:260px;flex:none;font-size:36px;font-weight:700;color:{INK}", e(h_))
             + p(f"flex:1;font-family:{MONO};font-size:26px;font-weight:700;line-height:1.5;color:{INK};white-space:pre", e(code))
             + p(f"width:420px;flex:none;font-size:26px;color:{SUB}", e(d)) + '</div>')
o.append(note(96, 830, 1728, "LinearRegression만 쓸 때는 2단계를 빼도 돼요. SGD처럼 걸음으로 찾는 모델은 2단계가 꼭 있어야 해요.", INK, 30, fade(5)))
o.append(caption("다음에 배울 것: 점수 대신 종류를 맞히는 분류, 가까운 이웃으로 맞히는 KNN", 950, 6))
W("recap", o, "오늘 배운 순서를 정리해요. 먼저 train_test_split으로 학습용과 채점용을 나눠요. 그다음 StandardScaler로 학습용에서 자를 만들고, 학습용과 채점용을 같은 자로 바꿔요. 학습에는 학습용만 넣고, 채점은 채점용 정답과 비교해요. LinearRegression은 크기를 안 맞춰도 되지만, SGD처럼 조금씩 고쳐 가는 모델은 크기 맞추기가 꼭 필요해요. 다음 수업에서는 점수 같은 숫자 대신 종류를 맞히는 분류와, 가까운 이웃을 보고 맞히는 KNN을 배워요.", ("recap", "정리"))

o = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장으로 보는 오늘의 코드</h2>']
CHS = [("불러오기", "from sklearn.model_selection import train_test_split\nfrom sklearn.preprocessing import StandardScaler", K1),
       ("학습용과 채점용으로 나누기", "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)", K2),
       ("크기 맞추기", "scaler = StandardScaler()\nX_train_scaled = scaler.fit_transform(X_train)\nX_test_scaled = scaler.transform(X_test)", K3),
       ("SGD로 학습하고 채점", 'sgd = SGDRegressor(loss="squared_error", learning_rate="constant", eta0=0.01, max_iter=3000, random_state=42)\nsgd.fit(X_train_scaled, y_train)\nr2_score(y_test, sgd.predict(X_test_scaled))', K4),
       ("가로 막대", 'plt.barh(이름들, 길이들, color="blue")', K6)]
y = 180
for k, d, c in CHS:
    n_ = d.count("\n") + 1
    h = 50 + n_ * 36
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:{h}px;display:flex;flex-direction:column;justify-content:center;gap:4px;border-bottom:2px solid {LINE}">'
             + p(f"font-size:26px;font-weight:700;color:{c}", e(k)) + p(f"font-family:{MONO};font-size:24px;font-weight:700;line-height:1.5;color:{INK};white-space:pre", e(d)) + '</div>')
    y += h + 16
o.append(p(f"position:absolute;left:96px;top:{y + 20}px;width:1728px;font-size:30px;font-weight:700;line-height:1.5;color:{INK}", "fit은 학습용에만, 채점용과 새 학생은 transform만 써요."))
W("cheatsheet", o, "오늘 쓴 코드를 한 장에 모았어요. 나누고, 학습용으로 자를 만들어 크기를 맞추고, 학습하고, 채점용으로 채점해요. fit이 들어간 줄에는 늘 학습용만 들어가요.")

# ---------- order and toc ----------
want = ["cover", "toc", "setup", "start", "why", "exam", "big", "import", "split", "args", "which", "seed", "fittest", "compare",
        "sgdraw", "describe", "standardize", "scaler", "fitvt", "check", "sgd", "loop", "curve", "barh", "vs",
        "e-order", "e-refit", "e-noscale", "e-read", "x-new", "x-seed", "x-office", "trouble", "recap", "cheatsheet"]
assert sorted(want) == sorted(ORDER), (set(want) ^ set(ORDER))
ORDER[:] = want
SECTIONS.update({"p2": {"description": "나눠서 채점하기", "start": "import"}})
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
parts_ = [("Lightbulb", K1, "왜 필요한가", "why", "big"), ("Activity", K2, "나눠서 채점하기", "import", "compare"), ("Tool", K3, "열의 크기 맞추기", "sgdraw", "check"),
          ("Settings", K4, "SGD로 세 열 배우기", "sgd", "vs"), ("Warning", K5, "오류와 함정", "e-order", "e-read"), ("Star", K6, "실제 상황", "x-new", "x-office")]
t = [f'<section id="toc" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>']
for i, (ic, c, h, a, b) in enumerate(parts_):
    x, y = 96 + (i // 3) * 884, 230 + (i % 3) * 190
    t.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:844px;height:160px;display:flex;flex-direction:row;align-items:center;gap:28px;border-bottom:2px solid {LINE}">'
             f'<p style="width:70px;font-size:72px;font-weight:900;color:{c}">{i + 1}</p><x-icon name="{ic}" style="width:52px;height:52px;color:{c}"></x-icon>'
             f'<p style="flex:1;font-size:44px;font-weight:700;color:{INK}">{e(h)}</p><p style="font-size:28px;color:{GRAY}">{page[a]}–{page[b]}쪽</p></div>')
t.append(f'<p style="position:absolute;left:96px;top:880px;font-size:30px;color:{SUB}">{page["setup"]}–{page["start"]}쪽은 노트북 준비, {page["trouble"]}–{page["cheatsheet"]}쪽은 막힐 때와 정리, 한 장 요약이에요.</p>')
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(t) + "\n<aside>" + e("1파트에서 50의 채점이 왜 너무 후한지 보고, 2파트에서 train_test_split으로 학습용과 채점용을 나눠 채점해요. 3파트는 열마다 다른 숫자 크기를 StandardScaler로 맞추고, 4파트는 맞춘 표로 49의 SGD를 학습해요. 수업 노트북 03의 셀 48부터 58까지가 여기까지예요. 5파트는 자주 나는 오류, 6파트는 배운 것을 섞은 실제 상황이에요.") + "</aside>\n</section>\n")
deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-26T09:00:00Z"}, "lists": "css", "title": "처음 보는 데이터로 채점하기 (나누기와 스케일링)", "order": ORDER, "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
print(len(ORDER), "slides")
