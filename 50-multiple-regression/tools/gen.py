"""Generates every slide of the multiple linear regression deck (50, the last ML basics chapter) and slides/deck.json.

Story: class notebook 03_ml.ipynb, third part (multiple regression). The class stopped at the seaborn scatter plots and
the correlation heatmap; this deck finishes the same data with the steps after it (fit on three columns, three coef_
values, predict, R2), clearly marked as going past the class code. Part 1: a one-column model gives two students who
studied 2 hours the same 56.9, the 48-vs-50 picture, the formula with one w per column, and the class comments' words
(feature, target, weight, bias) mapped to the deck's words. Part 2: seaborn scatterplot and its four arguments, three
plots in one figure with plt.subplots(1, 3) and axes[0], df.corr(), sns.heatmap with annot, vmin, vmax and fmt (and
what changes without vmin and vmax), and the minus sign that turns into a box (axes.unicode_minus). Part 3: X with
three columns, fit, coef_ in column order, reading a coefficient ("keep the other two, add 1 to this one"), predict and
the same sum by hand, MAE and R2 against the one-column model, a true-vs-predicted chart instead of a line. Part 4: the
slopes alone vs together, sleep (R2 0.08 alone) still adds, and 48 vs 50. Part 5: predict with columns in another order
or missing, single brackets with two names (KeyError), scatterplot without ax=, the class's hard-coded AppleGothic.
Part 6: a study plan (which of the three to raise) and the students the model misses most. Then trouble, a one-slide
recap of ML basics 45 to 50, and the cheat sheet.
Class code fixes shown in the deck (and said in the notes): AppleGothic hard-coded (46's platform cell instead),
axes.unicode_minus added, the heatmap and scatter cells unchanged otherwise.
Every cell and output comes from tools/demo.sh (tools/run_nb.py runs the cells with the project kernel), kept in
tools/demo.log. Charts are the kernel's own PNGs in tools/img (NanumGothic stands in for Malgun Gothic on Linux).

Layout rules (Stageshow skill, github.com/benjitaylor/skills, SKILL.md and every file in references/ read for this deck):
1. one focal object per slide: a notebook cell, a kernel chart, one code line taken apart, or one diagram (framing.md 1)
2. terms are labelled on the code token or the chart part with leader tags and tints, not in cards (annotations.md)
3. say it once: the speaker notes carry the explanation, the slide keeps one caption at most (craft.md, Restraint)
4. no empty bands: the chart or the code grows to fill; the payoff gets the room (craft.md, Restraint)
5. values move instead of swapping: coef_ values fly into their columns, the plt line morphs into the seaborn line
6. one number gets to be big (R2 0.87 to 0.99), the rest are lines (craft.md, Restraint)
7. a comparison changes one thing (teaching.md, Making a comparison): heatmap with and without vmin/vmax, minus on/off
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


# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#F2B27A;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
       f'<h1{SLAM(1)} style="font-size:88px;font-weight:900;line-height:1.14;color:#F6F5F1">다중 선형 회귀와<br>ML 기초 정리</h1>',
       '<p style="font-size:38px;line-height:1.45;color:#BFC6D4">입력 열 셋으로 점수를 예측하고,<br>45~50을 한 장으로 묶어요</p>']
cov.append(f'<div id="cov-card" style="position:absolute;left:1080px;top:200px;width:720px;height:560px;background:#FFFFFF;border-radius:24px;overflow:hidden">'
           + f'<img id="cov-img" src="data:image/png;base64,{png_b64("main-2.png")}" style="position:absolute;left:44px;top:34px;width:632px">'
           + '</div>')
cov.append(p(f"position:absolute;left:1080px;top:790px;width:720px;font-size:26px;line-height:1.5;color:#BFC6D4", "학생 10명의 공부, 수면, 문제 풀이와 점수 사이의 상관계수를 색으로 칠한 그림이에요."))
cov.append(kenburns(2, "cov-img", 1.08, 6000, "40% 40%"))
W("cover", cov, "머신러닝 기초의 마지막 챕터예요. 48에서는 면적 한 열로 가격을 예측했어요. 오늘은 공부 시간, 수면 시간, 푼 문제 수 세 열로 시험 점수를 예측해요. 입력 열이 여러 개인 선형 회귀를 다중 선형 회귀라고 해요. 먼저 seaborn으로 열마다 점수와 어떤 관계인지 그래프로 보고, 수업에서 그린 히트맵까지 따라가요. 수업은 히트맵에서 끝났는데, 같은 데이터로 세 열을 학습하는 단계까지 이어서 해 봐요. 마지막에는 45부터 50까지 배운 머신러닝 기초를 한 장으로 정리해요." + IMGN, ("intro", "들어가기"))
ORDER.append("toc")

# ---------- setup ----------
o = [sec("setup")] + head("들어가기", "ml-basics에 새 노트북 multi.ipynb를 열어요. 새로 설치할 건 없어요", JP)
TL = [("$", "cd ml-basics"), ("$", "cat pyproject.toml"), ("o", "dependencies = ["), ("o", '    "matplotlib>=3.11.2",'), ("o", '    "numpy>=2.5.5",'), ("o", '    "pandas>=3.1.1",'),
      ("o", '    "scikit-learn>=1.9.1",'), ("o", '    "seaborn>=0.13.2",'), ("o", "]")]
o.append(term(96, 214, 900, TL, 28, tid="t-setup"))
LHt = 28 * 1.55
o.append(box(1, 96 + 34 - 10, 214 + 26 + 6 * LHt - 4, 28 * 0.6 * 25 + 20, LHt + 8, "#F2C46D", 4, 10))
o.append(box(2, 96 + 34 - 10, 214 + 26 + 7 * LHt - 4, 28 * 0.6 * 25 + 20, LHt + 8, "#8FD8DE", 4, 10))
o.append(tag(96 + 34 + 28 * 0.6 * 25 + 30, 214 + 26 + 6.5 * LHt, "48에서 넣었어요", "#B26A00", 1, 26))
o.append(tag(96 + 34 + 28 * 0.6 * 25 + 30, 214 + 26 + 7.5 * LHt, "46에서 넣었어요", TEAL, 2, 26))
o.append(note(96, 214 + 52 + len(TL) * LHt + 30, 900, "dependencies 위아래 줄은 줄여 적었어요. 버전 숫자는 받는 날에 따라 달라요.", SUB, 26, fade(2)))
TX = 1240
tree = [("ml-basics/", INK, 0, True), (".venv/", GRAY, 1, True), ("datasets/", GRAY, 1, True), ("model.ipynb", GRAY, 1, False), (NB, JP, 1, False), ("pyproject.toml", GRAY, 1, False)]
o.append(label(TX, 214, "폴더 모양", INK, 30))
for i, (n_, c_, d, folder) in enumerate(tree):
    y = 290 + i * 80
    at = rise(3) + DELAY(i * 60) if i else ""
    o.append(p(f"position:absolute;left:{TX + d * 56}px;top:{y}px;font-family:{MONO};font-size:32px;font-weight:700;line-height:64px;color:{c_};white-space:nowrap", ("▸ " if folder else "") + e(n_), at))
o.append(tag(TX + 56 + 32 * 0.6 * 11 + 40, 290 + 3 * 80 + 32, "48 노트북", GRAY, 3, 26))
o.append(tag(TX + 56 + 32 * 0.6 * 11 + 40, 290 + 4 * 80 + 32, "오늘 노트북", JP, 3, 26))
o.append(caption("seaborn과 scikit-learn이 dependencies에 있으면 준비 끝이에요. 커널은 .venv를 골라요(10).", 930, 4))
W("setup", o, "45부터 쓰는 ml-basics 프로젝트를 그대로 써요. 오늘 쓰는 seaborn은 46에서, scikit-learn은 48에서 이미 넣었어요. pyproject.toml의 dependencies에 둘이 보이면 새로 설치할 건 없어요. 없으면 uv add seaborn matplotlib, uv add scikit-learn으로 넣어요. VS Code에서 multi.ipynb를 새로 만들고 커널은 .venv로 골라요." + REAL)

# ---------- font ----------
o = [sec("font")] + head("들어가기", "맨 위 두 셀: 불러오기와 글꼴, 마이너스 한 줄을 더해요", JP)
CFS[0] = 28
o += cell({"id": "c-imp", "lines": IMPORTS, "n": 1}, 96, 200, 1080)
FT = 200 + chight(3) + 30
o += cell({"id": "c-font", "lines": FONTC, "n": 2}, 96, FT, 1080, sel="c-font")
o.append(tag(cx(96, IMPORTS[2]) + 30, ly(200, 2), "그래프 도구 seaborn, 줄여서 sns", CS, 1, 26))
o.append(hl(96, FT, 1080, 2, 5, "mark", 2))
o.append(tag(1210, ly(FT, 4.5), "46의 글꼴 셀: 운영체제를 보고 고르기", BL, 2, 26))
o.append(hl(96, FT, 1080, 7, 1, "run", 3))
o.append(tag(1210, ly(FT, 7), "새 줄: 마이너스 기호 깨짐 막기", GR, 3, 26))
o.append(note(1210, ly(FT, 7) + 40, 610, "왜 필요한지는 2파트 히트맵에서 봐요.", SUB, 24, fade(3)))
o.append(caption("수업 셀은 AppleGothic 한 줄만 적어서 Windows에서는 한글이 깨져요. 5파트에서 봐요.", 950, 4))
W("font", o, "새 노트북 맨 위에 셀 두 개를 먼저 둬요. 첫 셀은 pandas, matplotlib, seaborn을 불러와요. seaborn은 줄여서 sns라고 부르는 게 약속이에요. 둘째 셀은 46에서 쓴 글꼴 셀이에요. 운영체제가 Windows면 맑은 고딕, Mac이면 AppleGothic을 골라요. 오늘은 맨 아래에 axes.unicode_minus를 False로 두는 줄을 하나 더해요. 그래프의 마이너스 기호가 네모로 깨지는 걸 막는 줄이에요. 수업 노트북은 AppleGothic 한 줄만 적었는데, 그러면 Windows에서 한글이 깨져서 46의 셀로 바꿨어요.")

# ---------- part 1 ----------
o = [sec("why")] + head(EB1, "공부 시간만 보면, 2시간 공부한 두 학생이 둘 다 56.9점이에요", K1)
CFS[0] = 24
ONEC = ["from sklearn.linear_model import LinearRegression", "", "one = LinearRegression()", 'one.fit(df[["study_hours"]], df["score"])', 'print("기울기:", one.coef_[0], "절편:", one.intercept_)',
        "two = df.loc[[1, 5]]", "print(two)", 'print("예측:", one.predict(two[["study_hours"]]))']
ONEO = ["기울기: 8.899999999999997 절편: 39.10000000000001", "   study_hours  sleep_hours  practice_count  score", "1            2            8              15     58", "5            2            5              12     49", "예측: [56.9 56.9]"]
o += cell({"id": "c-one", "lines": ONEC, "n": 4, "out": ONEO}, 96, 196, 1010, sel="c-one")
o.append(hl(96, 196, 1010, 3, 1, "mark", 1, "공부 열 하나로 학습"))
o.append(underline(2, cx(96, "예측: ", True), cx(96, "예측: [56.9 56.9]", True), oyy(196, 8, 4) + LH() / 2, RED, 5))
STU = [("학생 1", 2, 8, 15, 58), ("학생 5", 2, 5, 12, 49)]
for k, (nm, s_, l_, pc, sc) in enumerate(STU):
    y = 210 + k * 330
    o.append(f'<div{rise(3) + DELAY(k * 150)} style="position:absolute;left:1180px;top:{y}px;width:640px;height:290px;background:#FFFFFF;border:2px solid {LINE};border-radius:20px;padding:26px 32px;display:flex;flex-direction:column;gap:18px">'
             + p(f"font-size:32px;font-weight:700;color:{INK}", e(nm))
             + '<div style="display:flex;flex-direction:row;gap:12px">' + colchip(f"공부 {s_}", CS, CSB, 26) + colchip(f"수면 {l_}", CL, CLB, 26) + colchip(f"문제 {pc}", CP, CPB, 26) + '</div>'
             + '<div style="display:flex;flex-direction:row;align-items:baseline;gap:40px;margin-top:10px">'
             + p(f"font-size:28px;color:{SUB}", f'실제 <b style="font-size:44px;color:{CY}">{sc}</b>')
             + p(f"font-size:28px;color:{SUB}", f'공부 열 모델 <b style="font-size:44px;color:{RED}">56.9</b>') + '</div></div>')
o.append(caption("두 학생을 가른 건 수면과 문제 풀이예요. 그 열도 같이 넣어야 모델이 차이를 봐요.", 940, 4))
W("why", o, "48처럼 열 하나로 학습하면 어떤 일이 생기는지 먼저 봐요. 공부 시간 한 열로 점수를 예측하는 모델을 만들었어요. 1번 학생과 5번 학생은 둘 다 2시간 공부했어요. 실제 점수는 58점과 49점으로 9점이나 차이가 나요. 그런데 모델은 공부 시간만 보니까 둘 다 56.9점이라고 예측해요. 두 학생은 수면 시간과 푼 문제 수가 달라요. 모델이 그 차이를 보려면 그 열도 입력으로 넣어야 해요. 이 셀은 수업 노트북에 없는 셀이에요. 이해를 도우려고 더했어요." + REAL, ("p1", "왜 필요한가"))

o = [sec("big")] + head(EB1, "48은 입력 열 하나, 오늘은 입력 열 셋이에요", K1)
def flowbox(x, y, w, h, text, color, bg, fs=30, attrs="", mono_=True):
    return p(f"position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;border-radius:14px;border:3px solid {color};background:{bg};font-family:{MONO if mono_ else SANS};font-size:{fs}px;font-weight:700;line-height:{h - 6}px;text-align:center;color:{INK};white-space:nowrap", e(text), attrs)
# 48, quiet
o.append(label(96, 220, "48 단순 선형 회귀", GRAY, 30))
o.append(flowbox(96, 300, 250, 80, "area", GRAY, "#F1F0EC", 30))
o.append(arrow(70, "#C9CED8", "", "position:absolute;left:366px;top:325px"))
o.append(flowbox(456, 300, 300, 80, "LinearRegression", GRAY, "#F1F0EC", 26))
o.append(arrow(70, "#C9CED8", "", "position:absolute;left:776px;top:325px"))
o.append(flowbox(866, 300, 200, 80, "price", GRAY, "#F1F0EC", 30))
# 50, the subject
o.append(label(96, 470, "50 다중 선형 회귀", K1, 34, fade(1)))
for i, (cn, kn, c_, bg) in enumerate(COLS):
    o.append(flowbox(96, 550 + i * 120, 340, 90, cn, c_, bg, 30, rise(1) + DELAY(i * 90)))
o.append(f'<svg{WIPE(2)} style="position:absolute;left:0;top:0;width:1920px;height:1080px;overflow:visible" viewBox="0 0 1920 1080">'
         + "".join(f'<path d="M446,{595 + i * 120} C560,{595 + i * 120} 560,715 660,715" fill="none" stroke="{c_}" stroke-width="5"/>' for i, (_, _, c_, _) in enumerate(COLS)) + '</svg>')
o.append(flowbox(670, 670, 360, 90, "LinearRegression", INK, "#FFFFFF", 28, rise(2)))
o.append(arrow(80, "#9AA0AB", WIPE(3), "position:absolute;left:1050px;top:700px"))
o.append(flowbox(1150, 670, 220, 90, "score", CY, CYB, 30, rise(3)))
o.append(note(1420, 560, 400, "식이 w × x + b 하나에서 열마다 w가 붙는 모양으로 바뀌어요.", INK, 30, fade(4)))
o.append(caption("만들기, fit, predict 세 줄은 48과 똑같아요. X에 넣는 열만 늘어요.", 950, 4))
W("big", o, "48과 오늘을 한 그림에 놓아 봐요. 위쪽 회색이 48이에요. 면적 한 열이 모델에 들어가서 가격 하나가 나왔어요. 입력 열이 하나인 선형 회귀를 단순 선형 회귀라고 해요. 아래쪽이 오늘이에요. 공부 시간, 수면 시간, 푼 문제 수 세 열이 같은 LinearRegression에 들어가서 점수 하나가 나와요. 입력 열이 여러 개면 다중 선형 회귀예요. 모델 이름도, fit과 predict를 쓰는 방법도 48과 같아요. 바뀌는 건 X에 넣는 열의 개수뿐이에요.")

o = [sec("formula")] + head(EB1, "열마다 기울기가 하나씩 붙어요", K1)
o.append(strip_parts(96, 200, 1728, 100, [("48   가격 = ", "#9AA0AB"), ("w", "#C9CED8"), (" × 면적 + ", "#9AA0AB"), ("b", "#C9CED8")], 36))
FP = [("점수 = ", W_), ("w1", "#9CC2F5"), (" × 공부 + ", W_), ("w2", "#C7B5F5"), (" × 수면 + ", W_), ("w3", "#F2C46D"), (" × 문제 + ", W_), ("b", "#8FD8DE")]
o.append(strip_parts(96, 340, 1728, 150, FP, 50, rise(1)))
xs, _ = sline(96, 340, FP, 50)
LBL = [(1, "공부 1시간 늘 때 오르는 점수", CS), (3, "수면 1시간", CL), (5, "문제 1개", CP), (7, "세 열이 모두 0일 때 점수", TEAL)]
for k, (i, t_, c_) in enumerate(LBL):
    xx = xs[i] + tw(FP[i][0], 50) / 2
    o.append(lead_down(2 + (k == 3), xx, 470, 560 + (k % 2) * 70, c_, t_, 26))
o.append(strip_parts(96, 760, 1728, 110, [("model.coef_", "#9CC2F5"), ("      = [w1, w2, w3]   ", W_), ("model.intercept_", "#8FD8DE"), (" = b", W_)], 38, fade(4)))
o.append(caption("열이 몇 개든 기울기는 열 수만큼, 절편은 하나예요.", 950, 4))
W("formula", o, "48의 직선은 가격 = w 곱하기 면적 더하기 b였어요. 오늘은 열이 셋이라 열마다 기울기가 하나씩 붙어요. w1은 공부 시간이 1시간 늘 때 점수가 얼마나 오르는지, w2는 수면 시간, w3는 푼 문제 1개에 대한 값이에요. 절편 b는 세 열이 모두 0일 때의 점수로 하나뿐이에요. fit을 하면 모델이 w1, w2, w3, b 네 숫자를 찾아요. 48에서 coef_가 배열이었던 이유가 여기 있어요. 열이 셋이면 coef_에 숫자 셋이 들어가요. 수업 주석의 Weight가 기울기, Bias가 절편이에요.")

o = [sec("terms")] + head(EB1, "수업 주석의 낯선 말은 48에서 쓴 말로 바꿔 읽어요", K1)
TRW = [("피처(Feature), 독립변수, 입력", "문제", "X"), ("타깃(Target), 종속변수", "정답", "y"), ("가중치(Weight), 계수", "기울기 w", "model.coef_"),
       ("편향(Bias)", "절편 b", "model.intercept_"), ("상관계수", "두 열이 같이 오르내리는 정도", "df.corr()"), ("다중 선형 회귀", "입력 열이 여러 개인 선형 회귀", "X에 열 셋")]
o += plain_rows(96, 210, 1728, TRW, [620, 600, 468], 1, 100, ("수업 주석에 나온 말", "이 덱에서 부르는 말", "코드"), 32, mono_cols=(2,))
o.append(caption("독립변수는 내가 정해 넣는 값, 종속변수는 그 값에 따라 정해지는 값이라는 뜻이에요.", 950, 7))
W("terms", o, "수업 노트북 주석에는 같은 것을 부르는 말이 여러 개 섞여 있어요. 피처, 독립변수, 입력은 모두 모델에 넣는 문제 쪽 열이에요. 코드에서는 X예요. 타깃과 종속변수는 맞혀야 하는 정답 열로 y예요. 가중치와 계수는 기울기, 편향은 절편이에요. 이 덱에서는 48처럼 문제, 정답, 기울기, 절편이라고 불러요. 처음 보는 말이 나오면 이 표에서 어느 칸인지 찾아보면 돼요. 독립변수는 내가 정해서 넣는 값이라 독립, 종속변수는 그 값에 따라 정해지는 값이라 종속이에요.")

# ---------- part 2 ----------
o = [sec("data")] + head(EB2, "학생 10명의 공부, 수면, 문제 풀이 수와 점수예요", K2)
CFS[0] = 24
o += cell({"id": "c-data", "lines": DATAC, "n": 3}, 96, 196, 1000, sel="c-data")
for i, (cn, kn, c_, bg) in enumerate(COLS):
    o.append(tint(1, cx(96, '    "') - 4, ly(196, i + 1) - LH() / 2, tw(cn) + 8, LH(), c_))
o.append(tint(1, cx(96, '    "') - 4, ly(196, 4) - LH() / 2, tw("score") + 8, LH(), CY))
LY = 196 + chight(7) + 40
for i, (cn, kn, c_, bg) in enumerate(COLS + [("score", "시험 점수", CY, CYB)]):
    o.append(f'<div{rise(1) + DELAY(i * 80)} style="position:absolute;left:96px;top:{LY + i * 62}px;display:flex;flex-direction:row;align-items:center;gap:18px;font-size:28px;font-weight:700;color:{INK}">' + colchip(cn, c_, bg, 26) + e(kn) + '</div>')
TX0, TY0, WD = 1120, 262, [165, 165, 200, 95]
o.append(df("t-data", TX0, TY0, CN, ROWS, WD, fs=24, rh=54, iw=40, attrs=fade(2)))
bx0, bx3 = dfx(TX0, 40, WD, 0), dfx(TX0, 40, WD, 3)
o.append(bar(bx0 + 6, TY0 - 26, bx3 - bx0 - 12, 8, CS, fade(3)))
o.append(label(bx0 + 6, TY0 - 70, "문제 X: 세 열", CS, 26, fade(3)))
o.append(bar(bx3 + 6, TY0 - 26, WD[3] - 12, 8, CY, fade(3)))
o.append(label(bx3 + 6, TY0 - 70, "정답 y", CY, 26, fade(3)))
W("data", o, "수업 노트북의 다중 회귀 데이터예요. 딕셔너리로 DataFrame을 만들었어요. 키가 열 이름이 된다는 건 45에서 배웠어요. 열은 넷이에요. study_hours는 공부 시간, sleep_hours는 잠잔 시간, practice_count는 푼 문제 수, score는 시험 점수예요. 앞의 세 열이 문제 X, score가 정답 y가 돼요. 학생은 10명뿐이라 표 전체가 화면에 들어와요. 리스트 안 숫자 앞의 띄어쓰기는 줄을 맞추려고 넣은 거라 빼도 결과가 같아요." + REAL)

o = [sec("seaborn")] + head(EB2, "seaborn은 표와 열 이름만 주면 matplotlib으로 그려 줘요", K2)
SA = [tok("f1", "plt.scatter(", f"color:#F2C46D"), tok("da", "df[", f"color:{W_}"), tok("sx", '"study_hours"', f"color:#9CC2F5"), tok("ba", "]", f"color:{W_}"), tok("cm", ",&#160;", f"color:{W_}"),
      tok("db", "df[", f"color:{W_}"), tok("sy", '"score"', f"color:#B8E8BE"), tok("bb", "]", f"color:{W_}"), tok("cl", ")", f"color:#F2C46D")]
SB = [tok("f2", "sns.scatterplot(", f"color:#8FD8DE"), tok("dd", "data=df,&#160;", f"color:{W_}"), tok("xk", "x=", f"color:{W_}"), tok("sx", '"study_hours"', f"color:#9CC2F5"),
      tok("yk", ",&#160;y=", f"color:{W_}"), tok("sy", '"score"', f"color:#B8E8BE"), tok("cl", ")", f"color:#8FD8DE")]
STY = f"position:absolute;left:96px;top:210px;width:1728px;height:130px;background:{DARK};border-radius:22px;padding:0 48px;display:flex;align-items:center;font-family:{MONO};font-size:40px;font-weight:700;line-height:1.5;white-space:pre"
o.append(f'<div id="sb-a"{MORPH_FROM()} style="{STY}">' + "".join(SA) + '</div>')
o.append(f'<div id="sb-b"{MORPH(1, "sb-a")} style="{STY}">' + "".join(SB) + '</div>')
c1 = crop("main-1.png", "crop-scatter1.png", (0, 0, 0.335, 1))
o.append(img(96, 400, 440, c1, rise(2)))
o.append(label(96, 400 + imh(c1, 440) + 12, "두 줄 모두 이 그림이 나와요", SUB, 24, rise(2)))
LAY = [("df", "pandas 표", "45", INK), ("seaborn", "표에서 열 이름으로 값을 골라요", "오늘", CS), ("matplotlib", "그림판과 칸에 점을 찍어요", "47", GRAY)]
for i, (nm, d_, ch, c_) in enumerate(LAY):
    y = 420 + i * 170
    o.append(f'<div{rise(3) + DELAY(i * 120)} style="position:absolute;left:760px;top:{y}px;width:1060px;height:120px;border-radius:18px;border:3px solid {c_ if i == 1 else LINE};background:{"#FFFFFF" if i == 1 else "#F1F0EC"};display:flex;flex-direction:row;align-items:center;gap:28px;padding:0 30px">'
             + p(f"width:240px;font-family:{MONO};font-size:34px;font-weight:700;color:{c_}", e(nm)) + p(f"flex:1;font-size:30px;font-weight:700;color:{INK}", e(d_)) + p(f"font-size:24px;color:{GRAY}", e(ch)) + '</div>')
    if i < 2:
        o.append(f'<x-shape{fade(3)} kind="arrow-down" style="position:absolute;left:1270px;top:{y + 124}px;width:40px;height:42px;background:#C9CED8"></x-shape>')
o.append(caption("sns는 seaborn을 줄여 부르는 이름이에요. 28의 import 모듈 as 별명이에요.", 950, 4))
W("seaborn", o, "seaborn은 matplotlib 위에서 돌아가는 그래프 패키지예요. 47에서는 plt.scatter 괄호 안에 df 대괄호로 꺼낸 열 두 개를 넣었어요. seaborn은 data에 표를 통째로 주고, x와 y에는 열 이름을 글자로 적어요. 그러면 seaborn이 표에서 열을 꺼내서 matplotlib에게 그리라고 넘겨요. 두 줄 다 같은 산점도가 나와요. 열 이름만 적으면 되니 그래프 여러 개를 그릴 때 코드가 짧아지고, 축 이름도 열 이름으로 자동으로 붙어요. seaborn은 46에서 데이터를 불러올 때 이미 썼고, 그래프 함수는 오늘 처음 써요." + IMGN)

o = [sec("subplots")] + head(EB2, "plt.subplots(1, 3): 그림판 하나를 그래프 칸 셋으로 나눠요", K2)
SP = [("fig, ", W_), ("axes", "#9CC2F5"), (" = plt.subplots(", W_), ("1", "#F2C46D"), (", ", W_), ("3", "#B8E8BE"), (", ", W_), ("figsize=(16, 5)", "#C9CED8"), (")", W_)]
o.append(strip_parts(96, 200, 1728, 120, SP, 44))
xs, _ = sline(96, 200, SP, 44)
LBS = [(1, "칸 셋을 담은 배열", CS, 0), (3, "행 1개", OR, 1), (5, "열 3개", GR, 0), (7, "그림판 크기: 가로 16, 세로 5인치", GRAY, 1)]
for k, (i, t_, c_, lv) in enumerate(LBS):
    o.append(lead_down(1, xs[i] + tw(SP[i][0], 44) / 2, 300, 360 + lv * 56, c_, t_, 26))
FY = 520
o.append(f'<div id="fig" style="position:absolute;left:96px;top:{FY}px;width:1200px;height:340px;border-radius:16px;border:3px dashed #9AA0AB;background:#FFFFFF"></div>')
o.append(label(110, FY - 44, "fig (그림판)", GRAY, 26))
for i in range(3):
    o.append(f'<div{rise(2) + DELAY(i * 120)} style="position:absolute;left:{130 + i * 384}px;top:{FY + 34}px;width:350px;height:272px;border-radius:12px;border:3px solid {COLS[i][2]};background:{COLS[i][3]};display:flex;align-items:center;justify-content:center">'
             + p(f"font-family:{MONO};font-size:38px;font-weight:700;color:{COLS[i][2]}", f"axes[{i}]") + '</div>')
CFS[0] = 26
o += cell({"id": "c-ax", "lines": ["print(type(axes))", "print(axes.shape)"], "n": 19, "out": ["<class 'numpy.ndarray'>", "(3,)"]}, 1340, FY, 480, attrs=rise(3))
o.append(caption("47은 칸이 하나라 ax 하나였어요. 칸이 셋이면 axes에서 번호로 꺼내요.", 950, 4))
W("subplots", o, "점 그래프 셋을 한 줄로 나란히 그리려고 그림판을 칸으로 나눠요. 47에서는 plt.subplots에 figsize만 넣어서 칸이 하나인 그림판을 만들었어요. 오늘은 앞에 숫자 둘을 넣어요. 첫째는 행, 곧 줄의 개수이고 둘째는 열, 곧 한 줄에 놓을 칸의 개수예요. 1, 3이면 한 줄에 칸 셋이에요. figsize는 47처럼 가로, 세로 인치이고, 칸이 셋이라 가로를 16으로 넓혔어요. 칸이 여럿이면 axes에 칸들이 배열로 담겨요. 13의 리스트처럼 axes[0], axes[1], axes[2]로 꺼내고, 0번이 왼쪽 칸이에요. type과 shape를 찍는 셀은 이해를 도우려고 더했어요." + REAL)

o = [sec("sargs")] + head(EB2, "scatterplot 괄호 네 칸: 어느 표, 가로 열, 세로 열, 몇 번째 칸", K2)
SG = [("sns.scatterplot(", "#8FD8DE"), ("data=df", "#E3B877"), (", ", W_), ('x="study_hours"', "#9CC2F5"), (", ", W_), ('y="score"', "#B8E8BE"), (", ", W_), ("ax=axes[0]", "#F2A0A0"), (")", "#8FD8DE")]
o.append(strip_parts(96, 210, 1728, 130, SG, 40))
xs, _ = sline(96, 210, SG, 40)
ARG = [(1, "그릴 표", OR, 0), (3, "가로축에 놓을 열 이름 (글자라 따옴표)", CS, 1), (5, "세로축 열 이름", GR, 0), (7, "그릴 칸, 0번이 왼쪽", RED, 1)]
for k, (i, t_, c_, lv) in enumerate(ARG):
    o.append(lead_down(k + 1, xs[i] + 30, 320, 390 + lv * 60, c_, t_, 26))
CFS[0] = 28
TOP = 580
o += cell({"id": "c-scat", "lines": SCAT, "n": 5}, 96, TOP, 1728, sel="c-scat")
for j, cn in enumerate(["study_hours", "sleep_hours", "practice_count"]):
    pre = 'sns.scatterplot(data=df, x="'
    o.append(tint(5, cx(96, pre) - 2, ly(TOP, 2 + j) - LH() / 2, tw(cn) + 4, LH(), COLS[j][2]))
    pre2 = SCAT[2 + j].split("ax=")[0] + "ax=axes["
    o.append(tint(5, cx(96, pre2) - 2, ly(TOP, 2 + j) - LH() / 2, tw(str(j)) + 4, LH(), RED))
o.append(tag(cx(96, SCAT[4]) + 30, ly(TOP, 3), "세 줄은 x와 칸 번호만 달라요", INK, 5, 26))
W("sargs", o, "scatterplot 괄호 안을 한 칸씩 봐요. data에는 그릴 표 df를 줘요. x에는 가로축에 놓을 열 이름을 적어요. 열 이름은 글자라서 따옴표로 감싸요. y에는 세로축 열 이름 score를 적어요. ax에는 앞 장에서 만든 칸 중 어디에 그릴지 적어요. axes[0]이 왼쪽 칸이에요. 모두 이름을 붙여 넣는 키워드 인자라서 순서를 바꿔 적어도 돼요. 수업 셀을 보면 세 줄이 거의 같고 x의 열 이름과 칸 번호만 달라요. ax를 빼먹으면 어떻게 되는지는 5파트에서 봐요.")

o = [sec("sread")] + head(EB2, "공부와 문제 풀이는 오른쪽 위로 올라가고, 수면은 흩어져 있어요", K2)
IW = 1728
o.append(img(96, 196, IW, "main-1.png", tid="i-sc"))
IH = imh("main-1.png", IW)
for i, (cn, t_, c_) in enumerate([("study_hours", "점수와 같이 올라가요", CS), ("sleep_hours", "위아래로 흩어져요", CL), ("practice_count", "점수와 같이 올라가요", CP)]):
    o.append(p(f"position:absolute;left:{96 + i * IW / 3 + 40:.0f}px;top:{196 + IH + 24:.0f}px;width:{IW / 3 - 80:.0f}px;text-align:center;font-size:30px;font-weight:700;color:{c_}", e(t_), rise(1) + DELAY(i * 150)))
o.append(spot(2, 96 + IW / 3 + 4, 200, IW / 3 - 8, IH - 8))
o.append(spot_off(3))
o.append(caption("눈으로 본 정도를 숫자 하나로 재는 게 다음 장의 상관계수예요.", 950, 3))
W("sread", o, "수업 셀을 실행하면 그래프 셋이 나란히 나와요. 왼쪽 공부 시간과 오른쪽 푼 문제 수는 점이 왼쪽 아래에서 오른쪽 위로 올라가요. 많이 할수록 점수가 높다는 뜻이에요. 가운데 수면 시간은 같은 8시간에서도 52점부터 87점까지 흩어져 있어서 한눈에 관계가 안 보여요. 축 이름 study_hours와 score는 seaborn이 열 이름으로 붙였어요. 이렇게 눈으로 본 관계를 숫자로 재는 게 47에서 배운 상관계수예요." + REAL + IMGN)

o = [sec("corr")] + head(EB2, "df.corr(): 모든 열 짝의 상관계수를 표 하나로 만들어요", K2)
CFS[0] = 28
o += cell({"id": "c-corr", "lines": ["corr = df.corr()", "corr.round(2)"], "n": 6}, 96, 196, 1100, sel="c-corr")
CT, CW, RH = 196 + chight(2) + 30, [200, 200, 240, 120], 64
o.append(df("t-corr", 96, CT, CN, CORRT, CW, fs=28, rh=RH, idx=CN, iw=250))
o.append(box(1, 96 - 4, dfy(CT, RH, 3) - 4, 250 + sum(CW) + 32, RH + 4, CY, 4, 10))
o.append(tag(96 + 250 + sum(CW) + 60, dfy(CT, RH, 3) + RH / 2, "score 줄: 점수와 각 열", CY, 1, 28))
for i in range(4):
    o.append(ring(2, dfx(96, 250, CW, i) + CW[i] - 80, dfy(CT, RH, i) + 8, 60, RH - 20, GRAY, 4))
o.append(tag(96 + 250 + sum(CW) + 60, dfy(CT, RH, 0) + RH / 2, "대각선 1.00: 자기 자신과는 늘 1", GRAY, 2, 28))
o.append(tag(96 + 250 + sum(CW) + 60, dfy(CT, RH, 2) + RH / 2, "0.85: 공부와 문제 풀이도 같이 올라가요", CP, 3, 28))
o.append(caption('47은 df["a"].corr(df["b"])로 두 열만, 오늘은 df.corr()로 모든 짝을 재요.', 950, 4))
W("corr", o, "47에서 열 두 개의 상관계수를 corr로 구했어요. 괄호를 비우고 표에 바로 corr를 부르면 모든 열 짝의 상관계수를 표로 만들어요. 열이 넷이라 4행 4열이에요. 맨 아래 score 줄을 보면 공부 0.93, 수면 0.29, 문제 풀이 0.93이에요. 앞 장 그래프에서 본 그대로예요. 대각선은 자기 자신과의 상관계수라 늘 1이에요. 대각선을 사이에 두고 위와 아래가 같아요. 공부와 문제 풀이 사이도 0.85로 높아요. 이 숫자는 4파트에서 다시 봐요. 수업 셀은 corr만 만들었고, 표를 찍는 round(2) 줄은 보기 좋게 더했어요." + REAL)

o = [sec("heat")] + head(EB2, "sns.heatmap: 상관계수 표를 색 칸으로 칠해요", K2)
CFS[0] = 28
o += cell({"id": "c-heat", "lines": HEATC, "n": 7}, 96, 196, 560, sel="c-heat")
HT = [(3, "칠할 표", INK), (4, "칸에 숫자 쓰기", OR), (5, "색의 가장 낮은 끝", BL), (6, "색의 가장 높은 끝", BL), (7, "소수 둘째 자리까지", GR)]
for k, (i, t_, c_) in enumerate(HT):
    o.append(tag(690, ly(196, i), t_, c_, [1, 1, 2, 2, 3][k], 26))
o.append(img(1060, 196, 760, "main-2.png", rise(1)))
o.append(note(96, 196 + chight(11) + 30, 900, 'fmt의 ".2f"는 13의 f-string에서 쓴 :.2f와 같은 뜻이에요. 빼면 0.849…처럼 길게 나와요.', SUB, 26, fade(3)))
o.append(caption("밝을수록 같이 올라가는 사이, 어두울수록 반대로 움직이는 사이예요.", 950, 4))
W("heat", o, "수업의 마지막 셀이에요. heatmap은 표의 숫자를 색으로 칠해서 한눈에 보게 해 주는 그래프예요. 첫째 자리에 앞 장의 corr 표를 넣어요. annot을 True로 하면 칸마다 숫자를 써 줘요. vmin과 vmax는 색 막대의 아래 끝과 위 끝이에요. 상관계수는 -1부터 1까지라 그 범위로 정했어요. fmt는 숫자 모양이에요. 점 2 f는 13의 f-string에서 쓴 소수 둘째 자리와 같은 뜻이에요. 그림에서 밝은 칸이 같이 올라가는 사이예요. 수면 줄은 붉은 색이라 다른 열과 관계가 약해요. 수업 셀처럼 인자마다 줄을 바꿔 적어도 한 줄로 적은 것과 같아요." + REAL + IMGN)

o = [sec("vmin")] + head(EB2, "vmin, vmax를 빼면 0.00이 가장 어두운 색이 돼요", K2)
o.append(img(96, 230, 820, "main-2.png", tid="i-v1"))
o.append(img(1004, 230, 820 * 1109 / 1136, "nov-1.png", rise(1), tid="i-v2"))
o.append(label(96, 180, "vmin=-1, vmax=1", BL, 30, mono=True))
o.append(label(1004, 180, "vmin, vmax 없이", RED, 30, fade(1)))
s1, s2 = 820 / 1136, 820 * 1109 / 1136 / 1109
o.append(ring(2, 96 + 330 * s1, 230 + 80 * s1, 120 * s1, 80 * s1, BL, 5))
o.append(ring(2, 1004 + 330 * s2, 230 + 80 * s2, 120 * s2, 80 * s2, RED, 5))
o.append(caption("범위를 -1~1로 고정하면 0.00이 '관계없음'인 가운데 색으로 칠해져요.", 950, 3))
W("vmin", o, "vmin과 vmax를 왜 적는지 빼고 그려서 비교해 봐요. 오른쪽이 뺀 그림이에요. 색 막대가 0부터 1까지로 바뀌었어요. seaborn이 표 안의 가장 작은 값과 가장 큰 값으로 범위를 정했기 때문이에요. 그래서 관계가 없다는 뜻인 0.00이 가장 어두운 색, 곧 가장 반대로 움직이는 것처럼 칠해졌어요. 왼쪽처럼 -1부터 1로 고정하면 0.00은 가운데 붉은 색이고, 반대로 움직이는 사이가 생기면 어두운 색으로 칠해져요. 다른 데이터의 히트맵과 색을 비교할 때도 범위가 같아야 해요." + REAL + IMGN)

o = [sec("minus")] + head(EB2, "색 막대의 마이너스가 네모로 나오면 axes.unicode_minus를 꺼요", K2)
cb1 = crop("minus-1.png", "crop-minus-bad.png", (0.85, 0.45, 1, 1))
cb2 = crop("main-2.png", "crop-minus-ok.png", (0.85, 0.45, 1, 1))
o.append(img(160, 200, 240, cb1))
o.append(label(160, 200 + imh(cb1, 240) + 14, "글꼴에 없는 기호", RED, 26))
o.append(img(1540, 200, 240, cb2, rise(3)))
o.append(label(1540, 200 + imh(cb2, 240) + 14, "보통 - 로 그려요", GR, 26, rise(3)))
CFS[0] = 24
WRN = ["UserWarning: Glyph 8722 (\\N{MINUS SIGN}) missing", "from font(s) AppleGothic."]
o.append(mono(500, 250, WRN, 26, 1.5, RED, fade(1)))
o.append(note(500, 360, 960, "수업 노트북(Mac)에 실제로 나온 경고예요. 그래프의 마이너스는 키보드의 - 대신 긴 마이너스 기호(8722번)로 그리는데, 한글 글꼴에는 그 기호가 없어요.", INK, 28, fade(1)))
o.append(strip_parts(500, 620, 960, 110, [('plt.rcParams["axes.unicode_minus"]', "#9CC2F5"), (" = ", W_), ("False", "#F2C46D")], 30, rise(2)))
o.append(note(500, 750, 960, "4쪽 글꼴 셀의 맨 아래 줄이에요. False면 키보드의 - 로 그려요.", SUB, 26, fade(2)))
o.append(arrow(70, "#C9CED8", fade(3), "position:absolute;left:1480px;top:665px"))
W("minus", o, "수업 노트북의 히트맵 셀 아래에 경고가 두 줄 나왔어요. 8722번 글자, 곧 마이너스 기호가 AppleGothic 글꼴에 없다는 뜻이에요. matplotlib은 마이너스를 키보드의 짧은 하이픈 대신 조금 긴 수학용 마이너스 기호로 그려요. 맑은 고딕이나 AppleGothic 같은 한글 글꼴에는 그 기호가 없어서 색 막대의 -0.25, -0.50 앞이 네모로 나와요. 글꼴 셀에 axes.unicode_minus를 False로 두는 줄을 더하면 키보드의 하이픈으로 그려서 깨지지 않아요. 왼쪽 네모 그림과 오른쪽 그림은 리눅스에서 나눔고딕으로 그렸고, 같은 경고가 나왔어요." + REAL)

# ---------- part 3 ----------
o = [sec("xy"), NEXT()] + head(EB3, "X에 열 셋: 대괄호 두 겹 안에 열 이름 리스트를 넣어요", K3)
CFS[0] = 28
o += cell({"id": "c-xy", "lines": XYC, "n": 8, "out": ["(10, 3) (10,)"]}, 96, 196, 1300, sel="c-xy")
for j, (cn, kn, c_, bg) in enumerate(COLS):
    pre = 'X = df[[' + ", ".join(f'"{c}"' for c in CN[:j]) + (", " if j else "")
    o.append(tint(1, cx(96, pre) - 2, ly(196, 0) - LH() / 2, tw(f'"{cn}"') + 4, LH(), c_))
o.append(tint(2, cx(96, "X = df[") - 2, ly(196, 0) - LH() / 2, tw("[") + 4, LH(), RED))
o.append(tint(2, cx(96, XYC[0][:-1]) - 2, ly(196, 0) - LH() / 2, tw("]") + 4, LH(), RED))
o.append(tag(cx(96, XYC[1]) + 40, ly(196, 1), "정답은 48처럼 한 겹, 한 줄", CY, 3, 26))
TY = 196 + chight(3, 1) + 50
o.append(df("t-x", 96, TY, CN[:3], [r[:3] for r in ROWS[:3]], [200, 200, 240], fs=28, rh=56, iw=40, attrs=rise(3)))
o.append(label(96, TY + 56 * 4 + 16, "X.head(3)  →  (10, 3)  10행 3열 표", CS, 28, rise(3), True))
o.append(note(1000, TY, 820, '48은 X = office[["area"]]로 (200, 1)이었어요. 리스트에 열 이름을 더 적으면 열이 늘어요.', INK, 30, fade(4)))
o.append(caption("fit에 넣을 문제는 언제나 표예요. 열이 하나든 셋이든 대괄호는 두 겹이에요.", 950, 4))
W("xy", o, "수업 노트북은 히트맵에서 끝났어요. 여기서부터는 같은 데이터로 학습까지 이어 가요. 먼저 문제 X와 정답 y를 나눠요. X는 df 대괄호 안에 열 이름 셋을 담은 리스트를 넣어요. 바깥 대괄호는 열을 고르는 괄호이고 안쪽은 리스트 괄호라 두 겹이에요. 45에서 열 두 개를 고를 때와 같은 모양이에요. shape를 찍으면 10행 3열이에요. 정답 y는 48처럼 열 이름 하나라 한 겹이고 값 10개짜리 한 줄이에요. X.head(3)은 이해를 도우려고 따로 실행한 셀이에요." + REAL, ("p3", "세 열로 학습하기"))

o = [sec("fit"), NEXT()] + head(EB3, "fit은 48과 똑같아요. coef_에 기울기 셋이 X 열 순서대로 들어가요", K3)
CFS[0] = 28
o += cell({"id": "c-fit", "lines": FITC, "n": 9, "out": FITO}, 96, 196, 1300, sel="c-fit")
o.append(hl(96, 196, 1300, 1, 1, "run", 1, "48과 같은 줄"))
o.append(underline(2, cx(96, "기울기 w: [", True), cx(96, "기울기 w: [5.80222725 2.68100001 0.63219852", True), oyy(196, 5, 0) + LH() / 2, CS, 5))
BY = 640
for i, (cn, kn, c_, bg) in enumerate(COLS):
    x = 96 + i * 440
    o.append(colchip(cn, c_, bg, 28).replace('<p style="', f'<p{rise(3)} style="position:absolute;left:{x}px;top:{BY}px;'))
    o.append(f'<x-shape{fade(3)} kind="arrow-down" style="position:absolute;left:{x + 100}px;top:{BY + 56}px;width:36px;height:40px;background:#C9CED8"></x-shape>')
    o.append(vbox(x, BY + 110, 400, 110, f"w{i + 1} = {W3[i]}", c_, bg, 40, rise(3) + DELAY(i * 120)))
o.append(vbox(1416, BY + 110, 400, 110, "b = 17.66", TEAL, K3BG, 40, rise(4)))
o.append(label(1416, BY + 30, "intercept_", TEAL, 28, rise(4), True))
o.append(caption("coef_의 첫째 칸은 X의 첫째 열 study_hours의 기울기예요.", 950, 5))
W("fit", o, "모델을 만들고 fit하는 두 줄은 48과 글자 하나 다르지 않아요. X에 열이 셋이라는 것만 달라요. coef_를 찍으면 숫자 셋이 든 배열이 나와요. 48에서는 하나라 [0]으로 꺼냈죠. 순서는 X를 만들 때 적은 열 순서와 같아요. 첫째 5.80은 study_hours, 둘째 2.68은 sleep_hours, 셋째 0.63은 practice_count의 기울기예요. intercept_는 숫자 하나로 17.66이에요. 아래 상자는 소수 둘째 자리로 줄여 적었어요." + REAL)

o = [sec("coefread"), NEXT()] + head(EB3, "기울기 읽기: 나머지 두 열은 그대로 두고, 그 열만 1 늘리면", K3)
CFS[0] = 24
MOREC = ["more = pd.DataFrame({", '    "study_hours":    [3, 4, 3, 3],', '    "sleep_hours":    [7, 7, 8, 7],', '    "practice_count": [20, 20, 20, 21]', "})", "model.predict(more).round(2)"]
o += cell({"id": "c-more", "lines": MOREC, "n": 23, "out": ["array([66.48, 72.28, 69.16, 67.11])"]}, 96, 196, 820, sel="c-more")
for j in range(3):
    pre = MOREC[1 + j].split("[")[0] + "[3, " if j == 0 else MOREC[1 + j].split("[")[0] + "[7, 7, " if j == 1 else MOREC[3].split("[")[0] + "[20, 20, 20, "
    o.append(tint(1, cx(96, pre) - 2, ly(196, 1 + j) - LH() / 2, tw("4" if j == 0 else "8" if j == 1 else "21") + 4, LH(), COLS[j][2]))
BARS = [("기준 학생 (3, 7, 20)", 66.48, None, GRAY, "#E1DED6"), ("공부 +1시간", 72.28, "+5.80", CS, CSB), ("수면 +1시간", 69.16, "+2.68", CL, CLB), ("문제 +1개", 67.11, "+0.63", CP, CPB)]
X0, SC = 1180, 30      # bar for 60..75 points
for i, (t_, v, d_, c_, bg) in enumerate(BARS):
    y = 220 + i * 150
    o.append(label(990, y + 14, t_, INK if i else GRAY, 28, rise(2 + (i > 0)) + DELAY(i * 120)))
    o.append(bar(X0, y + 64, (66.48 - 60) * SC, 46, "#C9CED8", WIPE(2 + (i > 0)) + DELAY(i * 120)))
    if d_:
        o.append(bar(X0 + (66.48 - 60) * SC, y + 64, (v - 66.48) * SC, 46, c_, WIPE(3) + DELAY(i * 120 + 200)))
    o.append(label(X0 + (v - 60) * SC + 16, y + 66, f"{v:.2f}" + (f"  {d_}" if d_ else ""), c_ if d_ else GRAY, 30, rise(2 + (i > 0)) + DELAY(i * 120 + 300)))
o.append(note(96, 196 + chight(6, 1) + 40, 820, "기준보다 오른 만큼이 그 열의 기울기예요. 문제 1개가 0.63점으로 작은 건 단위가 작아서예요. 10개면 6.3점이에요.", INK, 28, fade(4)))
W("coefread", o, "기울기 하나를 읽는 법이에요. 공부 3시간, 수면 7시간, 문제 20개인 학생을 기준으로 66.48점이에요. 다른 두 열은 그대로 두고 공부만 1시간 늘리면 72.28점으로 5.80점 올라요. 바로 공부의 기울기예요. 수면만 1시간 늘리면 2.68점, 문제만 1개 늘리면 0.63점 올라요. 그래서 기울기는 나머지 열은 그대로 두고 그 열만 1 늘렸을 때 바뀌는 점수라고 읽어요. 문제 풀이 기울기가 작아 보이는 건 1개라는 단위가 작아서예요. 10개를 더 풀면 6.3점이라 기울기 크기만 보고 어느 열이 더 중요하다고 말하면 안 돼요. 이 셀은 이해를 도우려고 더했고, 막대는 그 출력으로 그렸어요." + REAL)

o = [sec("predict"), NEXT()] + head(EB3, "predict는 열마다 기울기를 곱해서 더하고 b를 더해요", K3)
CFS[0] = 26
PREDC = ['new = pd.DataFrame({"study_hours": [3], "sleep_hours": [7], "practice_count": [20]})', "model.predict(new)"]
o += cell({"id": "c-pred", "lines": PREDC, "n": 11, "out": ["array([66.4778603])"]}, 96, 196, 1728, sel="c-pred")
HANDC = ["w = model.coef_", "b = model.intercept_", "print(3 * w[0] + 7 * w[1] + 20 * w[2] + b)"]
H2 = 196 + chight(2, 1) + 30
o += cell({"id": "c-hand", "lines": HANDC, "n": 12, "out": ["66.47786029820003"]}, 96, H2, 1100, attrs=rise(1))
EQ = [("3", "×", "5.80", CS, CSB), ("7", "×", "2.68", CL, CLB), ("20", "×", "0.63", CP, CPB)]
EY = 700
x = 96
for i, (a_, m_, w_, c_, bg) in enumerate(EQ):
    o.append(vbox(x, EY, 250, 110, f"{a_} × {w_}", c_, bg, 36, rise(2) + DELAY(i * 120)))
    o.append(p(f"position:absolute;left:{x + 258}px;top:{EY + 28}px;font-size:44px;font-weight:700;color:{GRAY}", "+", rise(2) + DELAY(i * 120)))
    x += 300
o.append(vbox(x, EY, 220, 110, "17.66", TEAL, K3BG, 36, rise(2) + DELAY(360)))
o.append(p(f"position:absolute;left:{x + 236}px;top:{EY + 28}px;font-size:44px;font-weight:700;color:{GRAY}", "=", rise(3)))
o.append(vbox(x + 300, EY, 240, 110, "66.48", INK, "#FFFFFF", 44, rise(3)))
o.append(caption("predict는 행마다 이 덧셈을 해요. 상자의 기울기는 소수 둘째 자리로 줄였어요.", 950, 4))
W("predict", o, "처음 보는 학생의 점수를 예측해요. 공부 3시간, 수면 7시간, 문제 20개예요. 48처럼 predict에는 학습 때와 같은 열 이름의 표를 넣어요. 열이 셋이니 딕셔너리 키도 셋이에요. 66.48점이 나왔어요. predict가 안에서 하는 계산을 직접 해 보면 3 곱하기 w1, 7 곱하기 w2, 20 곱하기 w3에 b를 더한 값과 똑같아요. 열 이름과 값의 짝을 같은 색으로 칠했어요. 손으로 계산하는 셀은 이해를 도우려고 더했어요." + REAL)

o = [sec("score"), NEXT()] + head(EB3, "세 열 모델은 R²가 0.87에서 0.99로, 평균 오차는 4.26점에서 1.17점으로", K3)
CFS[0] = 24
SCOREC = ["from sklearn.metrics import mean_absolute_error, r2_score", "", "y_pred = model.predict(X)", 'print(f"세 열 MAE {mean_absolute_error(y, y_pred):.2f} | R2 {r2_score(y, y_pred):.2f}")', "",
          'p1 = one.predict(df[["study_hours"]])', 'print(f"공부 열 MAE {mean_absolute_error(y, p1):.2f} | R2 {r2_score(y, p1):.2f}")']
o += cell({"id": "c-score", "lines": SCOREC, "n": 13, "out": ["세 열 MAE 1.17 | R2 0.99", "공부 열 MAE 4.26 | R2 0.87"]}, 96, 196, 1728, sel="c-score")
o.append(hl(96, 196, 1728, 5, 1, "mark", 1, "5쪽의 공부 열 모델"))
SY = 196 + chight(7, 2) + 60
o.append(p(f"position:absolute;left:96px;top:{SY}px;font-size:30px;font-weight:700;color:{SUB}", "R²", rise(2)))
o.append(p(f"position:absolute;left:96px;top:{SY + 40}px;font-size:120px;font-weight:900;line-height:1.1;color:#9AA0AB", "0.87", rise(2)))
o.append(arrow(110, "#C9CED8", WIPE(3), f"position:absolute;left:400px;top:{SY + 105}px"))
o.append(p(f"position:absolute;left:560px;top:{SY + 40}px;font-size:120px;font-weight:900;line-height:1.1;color:{CY}", "0.99", rise(3)))
o.append(note(1000, SY + 30, 820, "MAE 4.26 → 1.17점. 점수 단위라 '평균 1점쯤 틀린다'로 읽어요.", INK, 32, fade(4)))
o.append(note(1000, SY + 170, 820, "학습에 쓴 10명으로 채점한 점수라 실제보다 좋게 나와요.", SUB, 28, fade(4)))
W("score", o, "48에서 배운 채점 함수로 두 모델을 비교해요. 괄호 안 순서는 늘 정답, 예측이에요. 세 열 모델은 평균 1.17점쯤 틀리고 R제곱은 0.99예요. 5쪽의 공부 열 모델은 평균 4.26점 틀리고 R제곱이 0.87이에요. 열을 같이 넣으니 오차가 4분의 1 정도로 줄었어요. 다만 학생이 10명뿐이고, 학습에 쓴 그 10명으로 채점했어요. 처음 보는 학생에게도 이렇게 잘 맞을지는 알 수 없어요. 학습용과 채점용을 나누는 방법은 머신러닝 기초 다음에 배워요." + REAL)

o = [sec("truepred"), NEXT()] + head(EB3, "열이 셋이면 직선을 못 그려요. 정답과 예측을 점으로 비교해요", K3)
CFS[0] = 24
TPC = ["plt.figure(figsize=(6, 5))", 'plt.scatter(y, y_pred, s=60, label="학생 10명")', 'plt.plot([40, 90], [40, 90], color="red", label="정답 = 예측")',
       'plt.xlabel("정답 점수")', 'plt.ylabel("예측 점수")', "plt.legend()", "plt.show()"]
o += cell({"id": "c-tp", "lines": TPC, "n": 14}, 96, 196, 1000, sel="c-tp")
o.append(hl(96, 196, 1000, 2, 1, "mark", 2))
o.append(img(1150, 196, 670, "main-3.png", rise(1)))
o.append(note(96, 196 + chight(7) + 40, 1000, "빨간 선은 (40, 40)과 (90, 90)을 이은 선이에요. 가로가 정답, 세로가 예측이라 점이 선에 붙을수록 잘 맞힌 거예요.", INK, 30, fade(3)))
o.append(caption("입력 열이 셋이면 축이 넷 필요해서 48처럼 직선 그림을 못 그려요.", 950, 4))
W("truepred", o, "48에서는 산점도 위에 모델의 직선을 그렸어요. 오늘은 입력 열이 셋이라 점수까지 축이 네 개 필요해서 종이에 그릴 수 없어요. 그래서 가로에 정답, 세로에 예측을 놓고 학생마다 점을 찍어요. 빨간 선은 정답과 예측이 같은 자리예요. 40에서 90까지 두 점을 이은 선이에요. 점이 선에 붙어 있을수록 잘 맞힌 거예요. 거의 모든 점이 선 가까이 있어서 R제곱 0.99와 맞아요. 이 그래프 셀은 이해를 도우려고 더했어요." + REAL + IMGN)

# ---------- part 4 ----------
o = [sec("each")] + head(EB4, "혼자 배운 기울기와 같이 배운 기울기는 달라요", K4)
CFS[0] = 24
EACHC = ['cols = ["study_hours", "sleep_hours", "practice_count"]', "for col in cols:", "    m = LinearRegression()", "    m.fit(df[[col]], y)", "    r2 = r2_score(y, m.predict(df[[col]]))",
         '    print(f"{col:15} 혼자 기울기 {m.coef_[0]:5.2f} | R2 {r2:.2f}")']
EACHO = ["study_hours     혼자 기울기  8.90 | R2 0.87", "sleep_hours     혼자 기울기  3.29 | R2 0.08", "practice_count  혼자 기울기  1.54 | R2 0.87"]
o += cell({"id": "c-each", "lines": EACHC, "n": 15, "out": EACHO}, 96, 196, 1100, sel="c-each")
TRE = [("study_hours", "8.90", "5.80"), ("sleep_hours", "3.29", "2.68"), ("practice_count", "1.54", "0.63")]
o += plain_rows(1240, 220, 570, TRE, [290, 140, 140], 1, 80, ("열", "혼자", "같이"), 30, mono_cols=(0, 1, 2), ids=["re0", "re1", "re2"])
o.append(box(2, 1226, 220 + 58 - 6, 594, 80 + 12, CS, 4, 10))
o.append(note(1250, 560, 570, "공부와 문제 풀이는 같이 오르내려요(상관계수 0.85). 같이 넣으면 둘이 점수 몫을 나눠 가져요.", INK, 28, fade(3)))
o.append(caption("기울기는 같이 넣은 열에 따라 달라져요. 열을 바꾸면 기울기 읽기도 다시 해요.", 950, 4))
W("each", o, "열마다 따로 학습한 기울기와 세 열을 같이 학습한 기울기를 비교해요. for 문으로 열 하나씩 모델을 만들었어요. 공부 열만 넣으면 기울기가 8.90인데, 세 열을 같이 넣으면 5.80으로 줄어요. 문제 풀이도 1.54에서 0.63으로 줄어요. 공부를 많이 한 학생이 문제도 많이 풀어서 두 열이 같이 오르내리기 때문이에요. 혼자일 때는 공부 열이 문제 풀이 몫까지 가져갔어요. 같이 넣으면 모델이 몫을 나눠요. 그래서 기울기 하나는 함께 넣은 열이 무엇인지와 같이 읽어요. 이 셀은 이해를 도우려고 더했어요." + REAL, ("p4", "한 열 모델과 비교"))

o = [sec("sleep")] + head(EB4, "수면은 혼자 R² 0.08이지만, 세 열에 넣으면 0.94가 0.99로 올라요", K4)
CFS[0] = 24
NSC = ['two_cols = ["study_hours", "practice_count"]', "m2 = LinearRegression()", "m2.fit(df[two_cols], y)", 'print(f"수면 뺀 두 열 R2 {r2_score(y, m2.predict(df[two_cols])):.2f}")', 'print(f"세 열 R2 {r2_score(y, y_pred):.2f}")']
o += cell({"id": "c-ns", "lines": NSC, "n": 16, "out": ["수면 뺀 두 열 R2 0.94", "세 열 R2 0.99"]}, 96, 196, 1200, sel="c-ns")
RB = [("수면 혼자", 0.08, CL), ("공부 + 문제", 0.94, CP), ("공부 + 수면 + 문제", 0.99, CY)]
BY0 = 196 + chight(5, 2) + 70
for i, (t_, v, c_) in enumerate(RB):
    y = BY0 + i * 110
    o.append(label(96, y + 12, t_, INK, 30, rise(1 + i)))
    o.append(bar(520, y, v * 1100, 64, c_, WIPE(1 + i)))
    o.append(label(520 + v * 1100 + 18, y + 12, f"R² {v:.2f}", c_, 32, rise(1 + i)))
o.append(note(1340, 196, 480, "5쪽의 1번과 5번 학생은 공부가 같은데 점수가 9점 달랐어요. 그 차이를 수면이 설명해요.", INK, 28, fade(4)))
o.append(caption("상관계수가 낮은 열도 다른 열과 같이 넣으면 쓸모가 있을 수 있어요.", 950, 4))
W("sleep", o, "수면 열은 쓸모가 없을까요? 앞 장에서 수면 혼자로 학습한 R제곱은 0.08이었어요. 상관계수도 0.29로 낮았죠. 그런데 공부와 문제 풀이 두 열 모델에 수면을 더하면 R제곱이 0.94에서 0.99로 올라요. 공부와 문제 풀이로 설명하고 남은 차이를 수면이 설명하기 때문이에요. 5쪽의 1번과 5번 학생이 그 예예요. 공부 시간은 같은데 8시간 잔 학생이 9점 높았어요. 그러니 상관계수만 보고 열을 바로 빼지 말고 넣었을 때와 뺐을 때 점수를 비교해 봐요. 다만 10명 데이터라 우연일 수도 있어요. 이 셀은 이해를 도우려고 더했어요." + REAL)

o = [sec("vs48")] + head(EB4, "48과 50을 한 표로: 바뀐 건 X의 열 개수와 그 결과뿐이에요", K4)
TV = [("입력 열", "area 하나", "study_hours, sleep_hours, practice_count"), ("X 모양", "(200, 1)", "(10, 3)"), ("coef_", "숫자 하나, [0]으로 꺼내기", "숫자 셋, X 열 순서대로"),
      ("식", "w × 면적 + b", "w1×공부 + w2×수면 + w3×문제 + b"), ("그림", "산점도 위 직선", "정답과 예측 점 그림"), ("predict 표", 'pd.DataFrame({"area": [33]})', "세 열 모두, 같은 이름과 순서"),
      ("채점", "mean_absolute_error, r2_score (정답, 예측)", "똑같아요")]
o += plain_rows(96, 200, 1728, TV, [260, 640, 788], 1, 92, ("", "48 단순 선형 회귀", "50 다중 선형 회귀"), 28)
o.append(caption("LinearRegression(), fit(X, y), predict(표) 세 줄은 그대로예요.", 950, 6))
W("vs48", o, "48과 오늘을 표로 비교해요. 바뀐 건 입력 열의 개수와 거기서 따라오는 것들이에요. X가 1열에서 3열이 됐고, coef_에 숫자가 셋 들어가요. 식에는 열마다 기울기가 붙어요. 직선 그림 대신 정답과 예측을 비교하는 점 그림을 그려요. predict에 넣는 표에도 세 열이 모두 같은 이름과 순서로 있어야 해요. 모델을 만들고, fit하고, predict하고, 정답과 예측으로 채점하는 흐름은 똑같아요.")

# ---------- part 5 ----------
o = [sec("e-order")] + head(EB5, "predict 표의 열 순서가 다르거나 빠지면 ValueError가 나요", K5)
CFS[0] = 24
EO1 = ['model.predict(pd.DataFrame({"sleep_hours": [7], "study_hours": [3], "practice_count": [20]}))']
o += cell({"id": "c-eo1", "lines": EO1, "n": 7, "out": ["ValueError: The feature names should match those that were passed during fit.", "Feature names must be in the same order as they were in fit."], "err": True}, 96, 196, 1728, sel="c-eo1")
o.append(underline(1, cx(96, "Feature names ", True), cx(96, "Feature names must be in the same order", True), oyy(196, 1, 1) + LH() / 2, RED, 5))
E2 = 196 + chight(1, 2) + 40
EO2 = ['model.predict(pd.DataFrame({"study_hours": [3], "practice_count": [20]}))']
o += cell({"id": "c-eo2", "lines": EO2, "n": 8, "out": ["ValueError: The feature names should match those that were passed during fit.", "Feature names seen at fit time, yet now missing:", "- sleep_hours"], "err": True}, 96, E2, 1728, attrs=rise(2))
o.append(underline(3, cx(96, "Feature names seen at fit time, ", True), cx(96, "Feature names seen at fit time, yet now missing:", True), oyy(E2, 1, 1) + LH() / 2, RED, 5))
o.append(reading(96, E2 + chight(1, 3) + 40, "위는 순서가 다르고, 아래는 sleep_hours가 빠졌다는 뜻이에요. 학습 때 X와 같은 열을 같은 순서로 넣어요.", INK, 4))
o.append(fix(96, 700, '{"sleep_hours": [7], "study_hours": [3], ...}', '{"study_hours": [3], "sleep_hours": [7], ...}', 5, 26))
W("e-order", o, "열이 여러 개면 predict에서 오류가 자주 나요. 위 셀은 열 세 개를 다 적었지만 수면을 먼저 적었어요. 메시지 둘째 줄에 열 이름이 fit 때와 같은 순서여야 한다고 나와요. 아래 셀은 sleep_hours를 빼먹었어요. fit 때 본 열 이름 중 sleep_hours가 없다고 알려 줘요. 모델은 열 이름으로 어느 값이 어느 열인지 알아보고, 순서까지 맞춰야 해요. 학습 때 X와 같은 열을 같은 순서로 적으면 둘 다 풀려요. 48의 e-name 장에서 본 메시지와 첫 줄이 같아요." + REAL, ("p5", "오류와 함정"))

o = [sec("e-key")] + head(EB5, "열 둘을 대괄호 한 겹으로 고르면: KeyError", K5)
CFS[0] = 28
o += cell({"id": "c-ek", "lines": ['df["study_hours", "sleep_hours"]'], "n": 7, "out": ["KeyError: ('study_hours', 'sleep_hours')"], "err": True}, 96, 220, 1300, sel="c-ek")
o.append(underline(1, cx(96, "KeyError: ", True), cx(96, "KeyError: ('study_hours', 'sleep_hours')", True), oyy(220, 1, 0) + LH() / 2, RED, 5))
o.append(reading(96, 440, "쉼표로 이은 두 이름을 열 이름 하나로 읽어서, 그런 열이 없다는 뜻이에요.", INK, 2))
o.append(fix(96, 560, 'df["study_hours", "sleep_hours"]', 'df[["study_hours", "sleep_hours"]]', 3, 32))
o.append(note(96, 700, 1728, '열 하나를 한 겹으로 fit에 넣으면 48의 Expected a 2-dimensional container 오류예요. X는 열 수와 상관없이 두 겹이에요.', SUB, 28, fade(4)))
W("e-key", o, "열 여러 개를 고를 때 대괄호를 한 겹만 쓰면 KeyError가 나요. 파이썬은 쉼표로 이은 두 이름을 튜플 하나로 묶어서 열 이름 하나로 찾아요. 그런 이름의 열은 없으니 키 오류예요. 안쪽에 리스트 대괄호를 하나 더 넣어야 해요. 열 하나를 한 겹으로 꺼내서 fit에 넣으면 48에서 본 2차원 컨테이너 오류가 나요. X는 열이 하나든 셋이든 두 겹이라고 기억해요." + REAL)

o = [sec("e-ax")] + head(EB5, "ax=를 빼면 세 그래프가 마지막 칸 하나에 겹쳐요", K5)
CFS[0] = 22
EAX = ['sns.scatterplot(data=df, x="study_hours", y="score")', 'sns.scatterplot(data=df, x="sleep_hours", y="score")', 'sns.scatterplot(data=df, x="practice_count", y="score")']
o += cell({"id": "c-eax", "lines": ["fig, axes = plt.subplots(1, 3, figsize=(16, 5))", ""] + EAX, "n": 4}, 96, 196, 960, sel="c-eax")
o.append(img(96, 196 + chight(5) + 30, 1728, "eax-1.png", rise(1)))
EH = imh("eax-1.png", 1728)
o.append(box(2, 96 + 1728 * 2 / 3 + 8, 196 + chight(5) + 38, 1728 / 3 - 24, EH - 16, RED, 5, 12))
o.append(fix(1110, 250, 'y="score")', 'y="score", ax=axes[0])', 3, 22, 714))
W("e-ax", o, "scatterplot에서 ax를 빼먹으면 오류는 안 나요. 대신 seaborn이 지금 쓰고 있는 칸, 곧 subplots가 마지막으로 만든 오른쪽 칸에 세 번 다 그려요. 앞의 두 칸은 비어 있고, 오른쪽 칸에 세 색 점이 겹쳐요. 가로축 이름도 첫 열 이름만 붙어서 무엇을 그렸는지 헷갈려요. 줄마다 ax에 axes[0], axes[1], axes[2]를 적어 줘요." + REAL + IMGN)

o = [sec("e-font")] + head(EB5, "AppleGothic만 적으면 Windows에서 한글이 네모로 나와요", K5)
CFS[0] = 26
o += cell({"id": "c-ef", "lines": ['plt.rcParams["font.family"] = "AppleGothic"'], "n": 2, "out": ["findfont: Font family 'AppleGothic' not found."], "err": True}, 96, 196, 1000, sel="c-ef")
o.append(img(96, 196 + chight(1, 1) + 30, 760, "efont-1.png", rise(1)))
o.append(note(1000, 420, 820, "AppleGothic은 Mac에만 있는 글꼴이에요. 없으면 matplotlib 기본 글꼴로 그리는데, 기본 글꼴에는 한글이 없어요.", INK, 30, fade(2)))
o.append(note(1000, 640, 820, "46의 글꼴 셀처럼 platform.system()으로 운영체제를 보고 고르면 Windows, Mac 모두 돼요.", GR, 30, fade(3)))
W("e-font", o, "수업 노트북의 첫 셀은 AppleGothic을 바로 적고 Windows 줄은 주석으로 막아 뒀어요. Mac에서는 잘 되지만 Windows에서 그대로 실행하면 그런 글꼴이 없다는 메시지가 여러 번 나와요. 그러면 matplotlib이 기본 글꼴로 그리는데 기본 글꼴에는 한글이 없어서 제목과 축 이름이 네모로 나와요. 46에서 배운 글꼴 셀을 쓰면 운영체제를 보고 알맞은 글꼴을 골라요. 이 장의 그림은 리눅스에서 같은 셀을 실행한 결과예요. 메시지는 같은 줄이 여러 번 나와서 한 줄만 적었어요." + REAL)

# ---------- part 6 ----------
o = [sec("x-plan")] + head(EB6, "다음 시험 계획: 공부, 수면, 문제 중 무엇을 늘리면 좋을까요", K6)
CFS[0] = 24
PLANC = ["plan = pd.DataFrame({", '    "study_hours":    [2, 3, 2, 2],', '    "sleep_hours":    [6, 6, 7, 6],', '    "practice_count": [15, 15, 15, 25]', "})",
         "pred = model.predict(plan)", 'plan["예상 점수"] = pred.round(1)', "plan"]
o += cell({"id": "c-plan", "lines": PLANC, "n": 17}, 96, 196, 940, sel="c-plan")
o.append(hl(96, 196, 940, 5, 1, "mark", 1, "계획 넷을 한 번에 예측"))
PT = 196 + chight(8) + 20
o.append(df("t-plan", 96 + 85, PT, CN[:3] + ["예상 점수"], [(2, 6, 15, 54.8), (3, 6, 15, 60.6), (2, 7, 15, 57.5), (2, 6, 25, 61.2)], [170, 170, 200, 150], fs=24, rh=48, iw=40, attrs=fade(2)))
PB = [("지금", 54.8, GRAY), ("공부 +1시간", 60.6, CS), ("수면 +1시간", 57.5, CL), ("문제 +10개", 61.2, CP)]
for i, (t_, v, c_) in enumerate(PB):
    y = 230 + i * 150
    o.append(label(1120, y, t_, INK, 28, rise(3) + DELAY(i * 100)))
    o.append(bar(1120, y + 46, (v - 45) * 34, 50, c_, WIPE(3) + DELAY(i * 100)))
    o.append(label(1120 + (v - 45) * 34 + 16, y + 52, f"{v}", c_, 32, rise(3) + DELAY(i * 100)))
o.append(caption("이 데이터 범위(공부 1~5, 수면 5~8, 문제 8~32) 안의 계획만 믿을 만해요.", 950, 4))
W("x-plan", o, "공부 2시간, 수면 6시간, 문제 15개를 푸는 학생이 다음 시험을 준비해요. 하나만 늘린다면 무엇이 좋을지 모델로 비교해 봐요. 계획 넷을 표로 만들어 predict에 넣었어요. predict는 열을 더하기 전에 해요. 예상 점수 열을 먼저 넣으면 열이 넷이 돼서 앞에서 본 열 이름 오류가 나요. 지금은 54.8점이고, 공부를 1시간 늘리면 60.6점, 수면 1시간은 57.5점, 문제 10개는 61.2점이에요. 다만 모델은 학생 10명에게서 배웠고, 그 범위를 넘는 계획, 예를 들어 하루 12시간 자기 같은 값은 믿을 수 없어요." + REAL, ("p6", "실제 상황"))

o = [sec("x-err")] + head(EB6, "가장 크게 틀린 학생 셋: 최대 2.2점이에요", K6)
CFS[0] = 24
ERRC = ["table = df.copy()", 'table["예측"] = y_pred.round(1)', 'table["오차"] = (table["score"] - table["예측"]).round(1)', 'table["오차 크기"] = table["오차"].abs()',
        'table.sort_values(by="오차 크기", ascending=False).head(3)']
o += cell({"id": "c-err", "lines": ERRC, "n": 18}, 96, 196, 1300, sel="c-err")
ET = 196 + chight(5) + 20
o.append(df("t-err", 96 + 85, ET, CN + ["예측", "오차", "오차 크기"], [(2, 8, 15, 58, 60.2, -2.2, 2.2), (1, 8, 8, 52, 50.0, 2.0, 2.0), (4, 6, 32, 79, 77.2, 1.8, 1.8)],
              [160, 160, 200, 90, 100, 100, 140], fs=24, rh=50, idx=[1, 9, 8], iw=40, attrs=fade(1)))
o.append(box(2, 96 + 85 - 6, dfy(ET, 50, 0) - 4, 40 + 950 + 36, 58, RED, 4, 10))
o.append(tag(96 + 85 + 40 + 950 + 60, dfy(ET, 50, 0) + 25, "1번 학생: 실제보다 2.2점 높게", RED, 2, 26))
o.append(note(96, ET + 50 * 4 + 40, 1728, "오차 크기 열은 abs()로 부호를 뗀 값이에요(48). 마이너스는 모델이 실제보다 높게 예측했다는 뜻이에요.", SUB, 26, fade(3)))
o.append(caption("학습한 10명 안에서 본 오차예요. 새 학생이면 더 커질 수 있어요.", 950, 4))
W("x-err", o, "모델이 누구를 가장 크게 틀렸는지 찾아봐요. 표를 복사해서 예측과 오차 열을 더하고, 오차의 절댓값으로 줄을 세웠어요. 가장 크게 틀린 학생도 2.2점이에요. 1번 학생은 58점인데 60.2점으로 예측했어요. 8시간 잔 학생이라 수면 기울기만큼 점수를 더 받았는데, 실제로는 그만큼 오르지 않았어요. 오차가 마이너스면 모델이 실제보다 높게 예측한 거예요. 이 오차들은 학습에 쓴 학생으로 잰 거라서 처음 보는 학생이면 더 커질 수 있어요. copy는 원래 df를 건드리지 않으려고 썼어요." + REAL)

# ---------- wrap up ----------
o = [sec("trouble")] + head("정리", "막히면 출력의 마지막 줄을 봐요", RED)
TR = [("ValueError: Feature names must be in the same order", "predict 표의 열 순서가 학습 때와 달라요", "X와 같은 순서로"),
      ("ValueError: ... yet now missing: - sleep_hours", "predict 표에 열이 빠졌어요", "세 열 모두 적기"),
      ("KeyError: ('study_hours', 'sleep_hours')", "열 여러 개를 대괄호 한 겹으로 골랐어요", 'df[["a", "b"]]'),
      ("그래프가 마지막 칸 하나에 겹쳐요", "scatterplot에 ax=를 안 적었어요", "ax=axes[0]"),
      ("UserWarning: Glyph 8722 (\\N{MINUS SIGN}) missing", "마이너스 기호가 한글 글꼴에 없어요", "unicode_minus = False"),
      ("findfont: Font family 'AppleGothic' not found.", "Windows에서 Mac 글꼴을 골랐어요", "46의 글꼴 셀")]
for i, (q, a_, cmd) in enumerate(TR):
    o.append(f'<div data-build-in="rise order {min(i + 1, 5)}" style="position:absolute;left:96px;top:{196 + i * 112}px;width:1728px;height:112px;display:flex;flex-direction:row;align-items:center;gap:26px;border-bottom:2px solid {LINE}">'
             + '<div style="flex:1;display:flex;flex-direction:column;gap:4px">' + p(f"{'font-family:' + MONO + ';' if q.isascii() else ''}font-size:25px;font-weight:700;color:{RED};white-space:nowrap", e(q)) + p(f"font-size:25px;color:{INK}", e(a_)) + '</div>'
             + p(f"width:500px;flex:none;font-size:27px;font-weight:700;color:{GR};white-space:pre", '✓ ' + e(cmd)) + '</div>')
o.append(caption("열 이름과 순서, 대괄호 두 겹, ax 번호 세 가지를 먼저 확인해요.", 900))
W("trouble", o, "막히면 셀 출력의 마지막 줄부터 읽어요. 위 셋은 열과 관련된 오류예요. predict에 넣는 표는 학습 때 X와 같은 열을 같은 순서로, 여러 열을 고를 때는 대괄호 두 겹이에요. 넷째는 오류 없이 그림만 이상한 경우예요. 아래 둘은 글꼴 메시지예요. 46의 글꼴 셀에 unicode_minus 줄을 더해 두면 두 가지 다 막혀요.", ("trouble", "정리"))

o = [sec("recap")] + head("정리", "머신러닝 기초 한 장 정리 (45~50)", K1)
RC = [("45", "표 만들기", "pd.DataFrame(딕셔너리)   df[조건]", GRAY), ("46", "데이터 정리", "fillna()   mode()[0]   duplicated()", GRAY), ("47", "그래프와 연습 데이터", "plt.scatter()   rng.normal()", GRAY),
      ("48", "학습, 예측, 채점", "fit(X, y)   predict(표)   r2_score()", K2), ("49", "경사 하강법", "SGDRegressor   partial_fit()", K2), ("50", "입력 열 여러 개", 'df[["a", "b", "c"]]   sns.heatmap()', K1)]
for i, (ch, h_, code, c_) in enumerate(RC):
    x, y = 96 + (i % 3) * 584, 210 + (i // 3) * 290
    o.append(f'<div{rise(1 + i // 3)}{DELAY((i % 3) * 120)} style="position:absolute;left:{x}px;top:{y}px;width:560px;height:250px;border-radius:18px;border:3px solid {c_ if c_ != GRAY else LINE};background:#FFFFFF;padding:24px 28px;display:flex;flex-direction:column;gap:14px">'
             + '<div style="display:flex;flex-direction:row;align-items:baseline;gap:18px">' + p(f"font-size:56px;font-weight:900;color:{c_}", ch) + p(f"font-size:34px;font-weight:700;color:{INK}", e(h_)) + '</div>'
             + p(f"font-family:{MONO};font-size:24px;font-weight:700;line-height:1.5;color:{SUB};white-space:pre-wrap", e(code)) + '</div>')
STEP = [("준비", "45, 46"), ("보기", "47, 50"), ("학습", "48, 49, 50"), ("채점", "48")]
for i, (a_, b_) in enumerate(STEP):
    x = 96 + i * 440
    o.append(f'<div{rise(3) + DELAY(i * 100)} style="position:absolute;left:{x}px;top:830px">' + num(i + 1, K1, 30) + '</div>')
    o.append(p(f"position:absolute;left:{x + 66}px;top:836px;font-size:34px;font-weight:700;color:{INK}", f'{e(a_)} <span style="font-size:26px;color:{GRAY}">{e(b_)}</span>', rise(3) + DELAY(i * 100)))
o.append(caption("다음에 더 배울 것: 학습용과 채점용 데이터 나누기, 다른 모델", 960, 4))
W("recap", o, "45부터 오늘까지 배운 머신러닝 기초를 한 장에 모았어요. 45에서 pandas로 표를 만들고 조건으로 골랐어요. 46에서 빈칸을 채우고 튀는 값과 겹친 행을 찾았어요. 47에서 그래프를 그리고 정답을 아는 연습 데이터를 만들었어요. 48에서 선형 회귀로 학습하고, 예측하고, 채점했어요. 49에서는 모델이 손실을 조금씩 줄여 가며 기울기와 절편을 찾는 경사 하강법을 봤어요. 오늘 50에서 입력 열을 셋으로 늘렸어요. 순서로 보면 데이터를 준비하고, 그래프로 보고, 학습하고, 채점하는 네 박자예요. 다음에는 학습에 쓰지 않은 데이터로 채점하는 방법과 다른 모델을 배워요.")

o = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장으로 보는 오늘의 코드</h2>']
CH = [("그림판을 칸 셋으로", "fig, axes = plt.subplots(1, 3, figsize=(16, 5))", K2), ("열 이름으로 점 그래프", 'sns.scatterplot(data=df, x="열", y="열", ax=axes[0])', K2),
      ("모든 열 짝 상관계수", "corr = df.corr()", K2), ("색 칸 그림", 'sns.heatmap(corr, annot=True, vmin=-1, vmax=1, fmt=".2f")', K2), ("마이너스 깨짐 막기", 'plt.rcParams["axes.unicode_minus"] = False', K2),
      ("문제 열 셋", 'X = df[["a", "b", "c"]]', K3), ("학습", "model.fit(X, y)", K3), ("기울기 셋, 절편 하나", "model.coef_   model.intercept_", K3),
      ("예측", 'model.predict(pd.DataFrame({"a": [..], "b": [..], "c": [..]}))', K3), ("채점", "r2_score(y, y_pred)", K3)]
for i, (k, d, c) in enumerate(CH):
    x, y = 96 + (i // 5) * 884, 190 + (i % 5) * 124
    o.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:844px;height:110px;display:flex;flex-direction:column;justify-content:center;gap:4px;border-bottom:2px solid {LINE}">'
             + p(f"font-size:26px;font-weight:700;color:{c}", e(k)) + p(f"font-family:{MONO};font-size:{22 if len(d) > 50 else 24 if len(d) > 42 else 28}px;font-weight:700;color:{INK};white-space:pre", e(d)) + '</div>')
o.append(p(f"position:absolute;left:96px;top:850px;width:1728px;font-size:32px;font-weight:700;line-height:1.5;color:{INK}", "그래프로 열마다 보고, 세 열을 X에 넣고, 기울기는 '나머지는 그대로, 이 열만 1'로 읽어요.<br>" + f'<span style="color:{GRAY}">predict 표는 학습 때와 같은 열, 같은 순서예요.</span>'))
W("cheatsheet", o, "오늘 쓴 코드를 한 장에 모았어요. 왼쪽은 그래프, 오른쪽은 학습과 예측이에요. 열이 여러 개면 먼저 산점도와 히트맵으로 열마다 점수와 어떤 사이인지 봐요. 그다음 문제 열을 모두 X에 넣고 48과 같은 세 줄로 학습하고 예측해요. 기울기는 나머지 열은 그대로 두고 그 열만 1 늘렸을 때 바뀌는 점수로 읽어요.")

# ---------- order and toc ----------
want = ["cover", "toc", "setup", "font", "why", "big", "formula", "terms", "data", "seaborn", "subplots", "sargs", "sread", "corr", "heat", "vmin", "minus",
        "xy", "fit", "coefread", "predict", "score", "truepred", "each", "sleep", "vs48", "e-order", "e-key", "e-ax", "e-font", "x-plan", "x-err", "trouble", "recap", "cheatsheet"]
assert sorted(want) == sorted(ORDER), (set(want) ^ set(ORDER))
ORDER[:] = want
SECTIONS.update({"p2": {"description": "그래프로 먼저 보기", "start": "data"}})
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
parts_ = [("Lightbulb", K1, "왜 필요한가", "why", "terms"), ("Activity", K2, "그래프로 먼저 보기", "data", "minus"), ("Tool", K3, "세 열로 학습하기", "xy", "truepred"),
          ("Settings", K4, "한 열 모델과 비교", "each", "vs48"), ("Warning", K5, "오류와 함정", "e-order", "e-font"), ("Star", K6, "실제 상황", "x-plan", "x-err")]
t = [f'<section id="toc" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>']
for i, (ic, c, h, a, b) in enumerate(parts_):
    x, y = 96 + (i // 3) * 884, 230 + (i % 3) * 190
    t.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:844px;height:160px;display:flex;flex-direction:row;align-items:center;gap:28px;border-bottom:2px solid {LINE}">'
             f'<p style="width:70px;font-size:72px;font-weight:900;color:{c}">{i + 1}</p><x-icon name="{ic}" style="width:52px;height:52px;color:{c}"></x-icon>'
             f'<p style="flex:1;font-size:44px;font-weight:700;color:{INK}">{e(h)}</p><p style="font-size:28px;color:{GRAY}">{page[a]}–{page[b]}쪽</p></div>')
t.append(f'<p style="position:absolute;left:96px;top:880px;font-size:30px;color:{SUB}">{page["setup"]}–{page["font"]}쪽은 노트북 준비, {page["trouble"]}–{page["cheatsheet"]}쪽은 막힐 때와 ML 기초 정리, 한 장 요약이에요. 3파트부터는 수업 노트북 다음 단계예요.</p>')
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(t) + "\n<aside>" + e("1파트에서 열이 하나일 때 무엇이 부족한지와 다중 선형 회귀의 식, 수업 주석의 용어를 봐요. 2파트는 수업 노트북 그대로 seaborn 산점도와 상관계수 히트맵을 그려요. 3파트는 같은 데이터로 세 열을 학습하고 예측하고 채점해요. 수업 노트북은 히트맵에서 끝나서 3파트부터는 이어 가는 단계예요. 4파트는 한 열 모델과 비교, 5파트는 자주 나는 오류, 6파트는 배운 것을 섞은 실제 상황이에요. 마지막에 45부터 50까지 머신러닝 기초를 한 장으로 정리해요.") + "</aside>\n</section>\n")
deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-25T13:00:00Z"}, "lists": "css", "title": "다중 선형 회귀와 ML 기초 정리", "order": ORDER, "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
print(len(ORDER), "slides")
