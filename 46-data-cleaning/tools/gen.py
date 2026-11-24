"""Generates every slide of the data cleaning deck (46) and slides/deck.json.

Story: today's class notebook on seaborn's titanic data (891 passengers, 15 columns) in the ml-basics project from 45.
Starts from df.head() with NaN in it, then the five-step map (look, blanks, outliers, duplicates, chart). Part 2 reads
info, describe and isnull().sum() and shows the blank rows with loc. Part 3 fills blanks: mean or median for age, the
mode for embark_town, the first letter for embarked, a new category for deck. Part 4 finds outliers with quantile and
the 1.5 x IQR fence, keeps them (104 of the 116 are first class) and drops only the 512 fares, then counts duplicate rows
and checks that they are different passengers (no name column). Part 5 draws the age histogram (Korean font by OS),
lines pandas up with the SQL of 36-43 and collects the pitfalls (category fillna, fillna without =, inplace on a column,
mode() without [0], median filling that adds duplicates). Part 6: who the outliers are, what mean filling did to the
histogram, and the whole cleaning in one cell.
Content checked against pandas 3.1.1: duplicated() already counts 107 before filling (NaN equals NaN there), filling
with the median makes 110, and .copy() is no longer needed for a warning (Copy-on-Write).
Every cell and output comes from tools/demo.sh (tools/run_nb.py runs the cells with the project kernel), kept in
tools/demo.log. Charts are the kernel's own PNGs in tools/img.

Layout rules (Stageshow skill, github.com/benjitaylor/skills, read in full for this deck):
1. one focal object per slide (a notebook cell, a DataFrame drawn as VS Code shows it, a chart, or one diagram)
2. terms are labelled on the code line or on the table with leader tags, not in separate cards (annotations.md)
3. say it once: what the speaker notes say does not repeat in cards; one caption at most
4. no empty bands: the table or the picture grows to fill; the payoff gets the room (craft.md, Restraint)
5. values move instead of swapping: a fill value flies into the blanks, the IQR fence slides out, counts roll up
6. one number gets to be big (177, 116, 107), the rest are lines (craft.md, Restraint)
Highlights come from tools/HIGHLIGHT.md, as many kinds as fit. No typing effect.
Usage: python3 tools/gen.py slides
"""

import base64
import html, json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from highlight import (spot, spot_off, cursor, cursor_off, ring, box, underline, lspot, lspot_off, run, run_off, zoom, zoom_off,
                       shine, shake, pulse, grow, link, keys, compare, SLAM, COUNT, MARK, DELAY, WIPE, STAGGER, MORPH, MORPH_FROM, tok)

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
NB = "titanic.ipynb"
TB = "#F4F5F7"   # striped row, like VS Code's notebook table
EB1, EB2, EB3, EB4, EB5, EB6 = "1. 왜 필요한가", "2. 훑어보고 빈칸 찾기", "3. 빈칸 채우기", "4. 튀는 값과 중복", "5. 그래프와 오류", "6. 실제 상황"
IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
LOAD = ["import pandas as pd", "import seaborn as sns", "", 'df = sns.load_dataset("titanic")', "df.shape"]
FONTC = ["import platform", "import matplotlib.pyplot as plt", "", "os_name = platform.system()", 'if os_name == "Windows":', '    plt.rcParams["font.family"] = "Malgun Gothic"',
         'elif os_name == "Darwin":', '    plt.rcParams["font.family"] = "AppleGothic"']
HIST = ["fig, ax = plt.subplots(figsize=(6, 4))", 'ax.hist(df["age"], bins=20, color="blue", edgecolor="black")', 'ax.set_title("나이 분포")', 'ax.set_xlabel("나이(세)")']
NEW1 = " 이 셀만 새 노트북에서 실행해서 셀 번호가 [1]부터예요."


def mono(left, top, lines, fs=24, lh=1.4, color=INK, attrs="", w=None, tid=None, weight=400):
    """Plain output text (VS Code prints it under the cell). Line i is centred at top + fs*lh*(i + 0.5)."""
    idt = f' id="{tid}"' if tid else ""
    ws = f"width:{w}px;" if w else ""
    body = "<br>".join(e(l) if l else "&#160;" for l in lines)
    return f'<p{idt}{attrs} style="position:absolute;left:{left}px;top:{top}px;{ws}font-family:{MONO};font-size:{fs}px;font-weight:{weight};line-height:{lh};white-space:pre;color:{color}">{body}</p>'


def my(top, i, fs=24, lh=1.4):
    return top + fs * lh * (i + 0.5)


def img(left, top, w, name, attrs="", tid=None, border=True):
    with open(os.path.join(IMG, name), "rb") as f:
        b = base64.b64encode(f.read()).decode()
    idt = f' id="{tid}"' if tid else ""
    bd = f"border:2px solid {LINE};border-radius:12px;" if border else ""
    return f'<img{idt}{attrs} src="data:image/png;base64,{b}" style="position:absolute;left:{left}px;top:{top}px;width:{w}px;{bd}background:#FFFFFF">'


def bar(x, y, w, h, color, attrs="", r=8):
    return f'<div{attrs} style="position:absolute;left:{x:.0f}px;top:{y:.0f}px;width:{max(w, 0):.0f}px;height:{h:.0f}px;border-radius:{r}px;background:{color}"></div>'


def nan_style():
    return f"color:{RED};font-weight:700;background:{K5BG};border-radius:6px"


# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#F2B27A;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
       f'<h1{SLAM(1)} style="font-size:96px;font-weight:900;line-height:1.1;color:#F6F5F1">데이터<br>정리하기</h1>',
       '<p style="font-size:40px;line-height:1.4;color:#BFC6D4">타이타닉 승객 891명의<br>빈칸, 튀는 값, 겹친 행 다듬기</p>']
cov.append(f'<div id="cov-card" style="position:absolute;left:1010px;top:250px;width:770px;height:580px;background:#FFFFFF;border-radius:24px;padding:44px 48px;display:flex;flex-direction:column;gap:18px">'
           + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{INK};white-space:pre", "df.isnull().sum()") + '</div>')
CVR = [("age", "177", "0"), ("embarked", "2", "0"), ("deck", "688", "0"), ("embark_town", "2", "0")]
for i, (c, a, b) in enumerate(CVR):
    y = 360 + i * 96
    cov.append(p(f"position:absolute;left:1058px;top:{y}px;width:240px;font-family:{MONO};font-size:32px;font-weight:700;line-height:72px;color:{INK}", c))
    cov.append(p(f"position:absolute;left:1330px;top:{y}px;width:130px;text-align:right;font-family:{MONO};font-size:34px;font-weight:700;line-height:72px;color:{RED}", a))
    cov.append(arrow(70, "#C9CED8", "", f"position:absolute;left:1490px;top:{y + 21}px"))
    cov.append(p(f"position:absolute;left:1590px;top:{y}px;width:120px;text-align:right;font-family:{MONO};font-size:34px;font-weight:700;line-height:72px;color:{GR}", b))
    cov.append(f'<div style="position:absolute;left:1058px;top:{y + 80}px;width:674px;height:2px;background:{LINE}"></div>')
cov.append(p(f"position:absolute;left:1058px;top:752px;width:680px;font-size:26px;line-height:1.5;color:{SUB}", "열마다 남은 빈칸 수예요. 정리한 뒤에는 모두 0이에요."))
cov.append(shine(2, "cov-card"))
W("cover", cov, "오늘은 머신러닝에 넣기 전에 데이터를 다듬는 법을 배워요. seaborn에 들어 있는 타이타닉 승객 891명의 표로 연습해요. 빈칸을 찾아 채우고, 튀는 값을 골라내고, 겹친 행을 세고, 그래프로 확인해요. 오른쪽 카드는 열마다 빈칸 수를 센 결과예요. 정리를 마치면 네 열 모두 0이 돼요.", ("intro", "들어가기"))
ORDER.append("toc")

# ---------- setup ----------
o = [sec("setup")] + head("들어가기", "45의 ml-basics에 seaborn과 matplotlib을 더해요", JP)
TL = [("$", "cd ml-basics"), ("$", "uv add seaborn matplotlib"), ("o", "Resolved 44 packages in 15ms"), ("o", "Installed 8 packages in 7ms"),
      ("o", " + contourpy==1.4.0"), ("o", "…"), ("o", " + matplotlib==3.11.2"), ("o", " + pillow==13.0.0"), ("o", " + pyparsing==3.3.3"), ("o", " + seaborn==0.13.2")]
TT_, TW_, FT = 214, 1000, 29
o.append(term(96, TT_, TW_, TL, FT, tid="t-setup"))
LHt = FT * 1.55
o.append(box(1, 96 + 34 - 10, TT_ + 26 + 9 * LHt - 4, FT * 0.6 * 19 + 20, LHt + 8, "#F2C46D", 4, 10))
o.append(tag(96 + 34 + FT * 0.6 * 19 + 40, TT_ + 26 + 9.5 * LHt, "연습용 데이터가 들어 있어요", "#B26A00", 1, 26))
o.append(box(2, 96 + 34 - 10, TT_ + 26 + 6 * LHt - 4, FT * 0.6 * 22 + 20, LHt + 8, "#9FD6F2", 4, 10))
o.append(tag(96 + 34 + FT * 0.6 * 22 + 40, TT_ + 26 + 6.5 * LHt, "그래프를 그려요", BL, 2, 26))
o.append(p(f"position:absolute;left:96px;top:{TT_ + 26 + 10 * LHt + 60:.0f}px;width:1000px;font-size:24px;line-height:1.6;color:{GRAY}",
           "45를 안 했다면 먼저 아래 세 명령을 쳐요.<br>" + f'<span style="font-family:{MONO};font-size:22px">uv init ml-basics, uv add numpy pandas, uv add --dev ipykernel</span>'))
steps_ = [p(f"font-size:30px;color:{INK}", "VS Code로 ml-basics 폴더 열기"),
          p(f"font-size:30px;color:{INK}", "새 파일") + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{JP}", NB) + p(f"font-size:30px;color:{INK}", "만들기"),
          p(f"font-size:30px;color:{INK}", "오른쪽 위 커널에서 .venv 고르기"),
          p(f"font-size:30px;color:{INK}", "첫 셀은 인터넷이 연결된 채로 실행")]
o.append(p(f"position:absolute;left:1180px;top:226px;font-size:32px;font-weight:700;color:{JP}", "노트북 열기 (10)", rise(3)))
for i, inner in enumerate(steps_):
    o.append(f'<div data-build-in="rise order 3"{DELAY(90 + i * 90)} style="position:absolute;left:1180px;top:{300 + i * 128}px;width:660px;height:110px;display:flex;flex-direction:row;flex-wrap:wrap;align-items:center;gap:14px;border-bottom:2px solid {LINE}">' + num(i + 1, JP, 34) + inner + '</div>')
o.append(caption("패키지는 늘 uv add로 넣어요. VS Code 알림의 Install 버튼은 누르지 않아요.", 900, 4))
W("setup", o, "45에서 만든 ml-basics 프로젝트를 그대로 써요. 터미널에서 uv add seaborn matplotlib을 치면 두 패키지와 그림 저장용 pillow 같은 도우미가 같이 들어와요. seaborn은 그래프 도구인데 연습용 데이터를 내려받는 load_dataset도 있어요. matplotlib은 6파트에서 나이 그래프를 그려요. VS Code에서 titanic.ipynb를 만들고 커널은 .venv로 골라요. 첫 셀이 데이터를 인터넷에서 받아 오니 연결된 채로 실행해요. 출력 가운데 줄은 줄였어요. 버전 숫자는 실행한 날에 따라 달라요." + REAL)

# ---------- part 1 ----------
o = [sec("why")] + head(EB1, "실제 데이터에는 빈칸, 튀는 값, 겹친 행이 섞여 있어요", K1)
T = 200
CFS[0] = 26
o += cell({"id": "c-why", "lines": ["df.head()"], "n": 2}, 96, T, 1000, sel="c-why")
HC = ["survived", "pclass", "sex", "age", "fare", "class", "deck", "embark_town"]
HR = [(0, 3, "male", "22.0", "7.2500", "Third", "NaN", "Southampton"), (1, 1, "female", "38.0", "71.2833", "First", "C", "Cherbourg"),
      (1, 3, "female", "26.0", "7.9250", "Third", "NaN", "Southampton"), (1, 1, "female", "35.0", "53.1000", "First", "C", "Southampton"),
      (0, 3, "male", "35.0", "8.0500", "Third", "NaN", "Southampton")]
HW = [136, 116, 116, 92, 130, 104, 90, 196]
TY = cbot(T, 1) + 20
cs = {(i, 6): nan_style() for i in (0, 2, 4)}
o.append(df("why-df", 96 + 85, TY, HC, HR, HW, fs=27, rh=74, iw=40, cs=cs))
o.append(p(f"position:absolute;left:{96 + 85}px;top:{TY + 74 * 6 + 20}px;width:900px;font-size:24px;color:{GRAY}", "열 15개 중 8개만 옮겼어요. NaN은 값이 비어 있다는 표시예요."))
DX = dfx(96 + 85, 40, HW, 6)
o.append(spot(1, DX - 4, TY - 4, HW[6] + 16, 74 * 6 + 8, pad=8))
o.append(spot_off(2))
PX = 1230
PR = [("빈칸", "177", "명", "나이(age)를 모르는 승객", K3), ("튀는 값", "512", "", "요금(fare) 최대. 가운데 값은 14.45", K4), ("겹친 행", "107", "줄", "15칸이 모두 같은 행", K5)]
for i, (h_, n_, u_, d_, c_) in enumerate(PR):
    y = 220 + i * 230
    at = rise(2) + DELAY(i * 120)
    o.append(f'<div{at} style="position:absolute;left:{PX}px;top:{y}px;width:600px;height:210px;display:flex;flex-direction:column;justify-content:center;gap:6px;border-bottom:2px solid {LINE}">'
             + p(f"font-size:28px;font-weight:700;color:{c_}", e(h_))
             + p(f"font-family:{MONO};font-size:84px;font-weight:700;line-height:1.05;color:{INK}", e(n_) + (f'<span style="font-family:{SANS};font-size:34px;color:{SUB}"> {e(u_)}</span>' if u_ else ""))
             + p(f"font-size:26px;color:{SUB}", e(d_)) + '</div>')
o.append(caption("이대로 머신러닝 모델에 넣으면 빈칸에서 멈추거나 튀는 값에 끌려가요.", 930, 3))
W("why", o, "실제 데이터는 처음부터 깨끗하지 않아요. df.head()로 앞 다섯 줄만 봐도 deck 열에 NaN이 세 개 보여요. NaN은 값이 비어 있다는 표시예요. 표 전체로 넓히면 나이를 모르는 승객이 177명, 혼자 512를 낸 요금, 15칸이 모두 같은 행 107줄이 있어요. 다음 강의의 머신러닝 모델은 대부분 빈칸이 있으면 학습을 못 하고, 튀는 값이 있으면 그쪽으로 끌려가요. 그래서 넣기 전에 정리해요." + REAL, ("p1", "왜 필요한가"))

o = [sec("big")] + head(EB1, "훑기, 빈칸, 튀는 값, 중복, 그래프 순서로 정리해요", K1)
ST5 = [("훑어보기", "info()\ndescribe()", K2, "2"), ("빈칸 채우기", "isnull()\nfillna()", K3, "2, 3"), ("튀는 값", "quantile()\nIQR", K4, "4"), ("중복 찾기", "duplicated()", K5, "4"), ("그래프", "ax.hist()", K6, "5")]
BW, GAP_, Y0 = 280, 77, 320
for i, (h_, code, c_, part) in enumerate(ST5):
    x = 96 + i * (BW + GAP_)
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:{x}px;top:{Y0}px;width:{BW}px;height:390px;border-radius:18px;border:3px solid {c_};background:#FFFFFF;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:30px">'
             + num(i + 1, c_, 48) + p(f"font-size:38px;font-weight:700;color:{INK}", e(h_))
             + p(f"font-family:{MONO};font-size:29px;font-weight:700;line-height:1.5;text-align:center;white-space:pre;color:{c_}", e(code)) + '</div>')
    o.append(p(f"position:absolute;left:{x}px;top:{Y0 + 412}px;width:{BW}px;text-align:center;font-size:26px;color:{GRAY}", f"{part}파트", fade(i + 1)))
    if i < 4:
        o.append(arrow(GAP_ - 24, "#C9CED8", WIPE(i + 2), f"position:absolute;left:{x + BW + 12}px;top:{Y0 + 180}px"))
o.append(f'<div data-build-in="fade order 6" style="position:absolute;left:96px;top:250px;width:1728px;height:8px;border-radius:4px;background:linear-gradient(90deg,{K2},{K6})"></div>')
o.append(label(96, 196, "891행 × 15열", INK, 30, fade(6), True))
o.append(p(f"position:absolute;left:1424px;top:196px;width:400px;text-align:right;font-family:{MONO};font-size:30px;font-weight:700;color:{INK}", "888행 × 15열", fade(6)))
o.append(caption("정리한 표는 다음 강의에서 머신러닝 모델에 넣어요.", 900, 7))
W("big", o, "데이터 정리는 다섯 단계로 해요. 먼저 info와 describe로 표를 훑어요. isnull로 빈칸을 세고 fillna로 채워요. quantile과 IQR로 튀는 값을 찾아요. duplicated로 겹친 행을 세요. 마지막으로 그래프를 그려 눈으로 확인해요. 수업에서는 이 순서로 891행을 888행으로 다듬었어요. 줄어든 세 줄은 4파트에서 지운 요금 512인 승객이에요.")

o = [sec("min")] + head(EB1, "가장 짧은 시작: 타이타닉 표를 불러와 크기를 봐요", K1)
T = 200
CFS[0] = 32
o += cell({"id": "c-min", "lines": LOAD, "n": 1, "out": ["(891, 15)"]}, 96, T, 1728, sel="c-min")
o.append(tag(cx(96, LOAD[1]) + 40, ly(T, 1), "import 모듈 as 별명 (28). 다들 sns로 불러요", GRAY, 1, 26))
o.append(underline(2, cx(96, "df = "), cx(96, LOAD[3]), ly(T, 3) + LH() / 2 - 4, BL, 5))
o.append(tag(cx(96, LOAD[3]) + 40, ly(T, 3), "연습용 데이터를 내려받아 표로 만들어요", BL, 2, 26))
o.append(tag(cx(96, "(891, 15)", True) + 40, oy(T, 5, 0), "(행, 열). 45의 shape예요", GR, 3, 26))
COLS = [("survived", "살았으면 1"), ("pclass", "객실 등급 1, 2, 3"), ("sex", "성별"), ("age", "나이"), ("sibsp", "형제, 배우자 수"),
        ("parch", "부모, 자식 수"), ("fare", "요금"), ("embarked", "탄 항구 첫 글자"), ("class", "등급 글자"), ("who", "man, woman, child"),
        ("adult_male", "성인 남자인지"), ("deck", "갑판 A~G"), ("embark_town", "탄 항구 이름"), ("alive", "살았는지 글자"), ("alone", "혼자 탔는지")]
GY0 = 640
o.append(label(96, GY0 - 54, "한 행이 승객 한 명, 열 15개는 이런 뜻이에요", INK, 28, rise(4)))
o.append(f'<div{STAGGER(4, 40)} style="position:absolute;left:96px;top:{GY0}px;width:1728px;display:flex;flex-direction:row;flex-wrap:wrap;gap:10px 16px">'
         + "".join(f'<div style="width:330px;height:72px;flex:none;display:flex;flex-direction:row;align-items:center;gap:12px;border-bottom:2px solid {LINE}">'
                   + p(f"font-family:{MONO};font-size:22px;font-weight:700;color:{K1 if c in ('age', 'deck', 'embark_town', 'embarked', 'fare') else INK};white-space:nowrap", e(c))
                   + p(f"font-size:21px;color:{SUB};white-space:nowrap", e(d)) + '</div>' for c, d in COLS) + '</div>')
W("min", o, "seaborn의 load_dataset에 데이터 이름을 넣으면 인터넷에서 연습용 데이터를 받아 pandas 표로 돌려줘요. 28에서 배운 import 모듈 as 별명으로 seaborn을 sns라고 불러요. 표 이름은 df로 짓는 게 관례예요. DataFrame의 앞 글자예요. shape는 45에서 본 것처럼 (행, 열)이에요. 승객 891명, 열 15개예요. 아래는 열 이름과 뜻이에요. 파랗게 칠한 다섯 열을 오늘 주로 다뤄요." + REAL)

# ---------- part 2 ----------
o = [sec("info")] + head(EB2, "info()는 열마다 빈칸이 아닌 칸 수와 타입을 알려 줘요", K2)
T = 196
CFS[0] = 26
o += cell({"id": "c-info", "lines": ["df.info()"], "n": 3}, 96, T, 1000, sel="c-info")
INFO = ["<class 'pandas.DataFrame'>", "RangeIndex: 891 entries, 0 to 890", "Data columns (total 15 columns):", " #   Column       Non-Null Count  Dtype   ",
        "---  ------       --------------  -----   ", " 0   survived     891 non-null    int64   ", " 1   pclass       891 non-null    int64   ", " 2   sex          891 non-null    str     ",
        " 3   age          714 non-null    float64 ", " 4   sibsp        891 non-null    int64   ", " 5   parch        891 non-null    int64   ", " 6   fare         891 non-null    float64 ",
        " 7   embarked     889 non-null    str     ", " 8   class        891 non-null    category", " 9   who          891 non-null    str     ", " 10  adult_male   891 non-null    bool    ",
        " 11  deck         203 non-null    category", " 12  embark_town  889 non-null    str     ", " 13  alive        891 non-null    str     ", " 14  alone        891 non-null    bool    ",
        "dtypes: bool(2), category(2), float64(2), int64(4), str(5)", "memory usage: 80.7 KB"]
IT, IFS, ILH = 262, 22, 1.5
IL = 96 + 105
o.append(mono(IL, IT, INFO, IFS, ILH))
CW = IFS * 0.6
for k, (row, order, col) in enumerate([(8, 1, RED), (12, 2, RED), (16, 2, RED), (17, 2, RED)]):
    o.append(box(order, IL + CW * 17 - 8, my(IT, row, IFS, ILH) - IFS * ILH / 2 - 1, CW * 13 + 16, IFS * ILH + 2, col, 3, 6))
o.append(tag(IL + CW * 58 + 20, my(IT, 8, IFS, ILH), "891보다 적으면 빈칸이 있어요. 177칸", RED, 1, 23))
o.append(tag(IL + CW * 58 + 20, my(IT, 12, IFS, ILH), "2칸 비어요", RED, 2, 23))
o.append(tag(IL + CW * 58 + 20, my(IT, 16, IFS, ILH), "688칸 비어요. 4명 중 3명", RED, 2, 23))
o.append(tag(IL + CW * 58 + 20, my(IT, 17, IFS, ILH), "2칸 비어요", RED, 2, 23))
o.append(underline(3, IL + CW * 34, IL + CW * 37, my(IT, 7, IFS, ILH) + IFS * 0.6, BL, 4))
o.append(tag(IL + CW * 58 + 20, my(IT, 7, IFS, ILH), "str: 글자 열 (pandas 3부터 이 이름)", BL, 3, 23))
o.append(underline(4, IL + CW * 34, IL + CW * 42, my(IT, 13, IFS, ILH) + IFS * 0.6, K4, 4))
o.append(tag(IL + CW * 58 + 20, my(IT, 13, IFS, ILH), "category: 정해진 값 몇 개만 (3파트)", K4, 4, 23))
W("info", o, "info는 표의 목차예요. 맨 위 RangeIndex는 행이 891개라는 뜻이에요. 열마다 Non-Null Count는 비어 있지 않은 칸 수예요. 891보다 적은 열에 빈칸이 있어요. age는 714라서 177칸이 비었고, deck은 203이라 688칸이 비었어요. Dtype은 칸에 든 값의 종류예요. 45의 int64와 float64 말고 str과 category가 보여요. str은 글자 열이고 pandas 3부터 이 이름으로 나와요. 예전 자료에는 object로 나와요. category는 정해진 값 몇 개만 들어가는 열이고 3파트에서 다시 만나요." + REAL, ("p2", "훑어보고 빈칸 찾기"))

o = [sec("describe")] + head(EB2, "describe()는 숫자 열의 개수, 평균, 사분위수를 보여 줘요", K2)
T = 196
CFS[0] = 26
o += cell({"id": "c-desc", "lines": ["df.describe()"], "n": 4}, 96, T, 1000, sel="c-desc")
DC = ["survived", "pclass", "age", "sibsp", "parch", "fare"]
DI = ["count", "mean", "std", "min", "25%", "50%", "75%", "max"]
DV = [("891.000000", "891.000000", "714.000000", "891.000000", "891.000000", "891.000000"), ("0.383838", "2.308642", "29.699118", "0.523008", "0.381594", "32.204208"),
      ("0.486592", "0.836071", "14.526497", "1.102743", "0.806057", "49.693429"), ("0.000000", "1.000000", "0.420000", "0.000000", "0.000000", "0.000000"),
      ("0.000000", "2.000000", "20.125000", "0.000000", "0.000000", "7.910400"), ("0.000000", "3.000000", "28.000000", "0.000000", "0.000000", "14.454200"),
      ("1.000000", "3.000000", "38.000000", "1.000000", "0.000000", "31.000000"), ("1.000000", "3.000000", "80.000000", "8.000000", "6.000000", "512.329200")]
DW = [170, 170, 170, 170, 170, 180]
DT = cbot(T, 1) + 20
cs = {}
for i in range(8):
    for j in (0, 1, 3, 4):
        cs[(i, j)] = "color:#A9AEB8"
o.append(df("d-df", 96 + 85, DT, DC, DV, DW, fs=26, rh=62, idx=DI, iw=100, cs=cs))
RX = 96 + 85 + 100 + sum(DW) + 50
def dcell(i, j):
    return dfx(96 + 85, 100, DW, j), dfy(DT, 62, i)
x, y = dcell(0, 2)
o.append(box(1, x + 4, y + 4, DW[2] - 4, 54, RED, 4, 8))
o.append(tag(RX, y + 31, "age만 714개: 빈칸은 안 세요", RED, 1, 26))
x1, y1 = dcell(1, 5)
x2, y2 = dcell(5, 5)
o.append(box(2, x1 + 4, y1 + 4, DW[5] - 4, 54, OR, 4, 8))
o.append(box(2, x2 + 4, y2 + 4, DW[5] - 4, 54, OR, 4, 8))
o.append(tag(RX, y1 + 31, "fare 평균 32.20", OR, 2, 26))
o.append(tag(RX, y2 + 31, "가운데 값 14.45 (50%)", OR, 2, 26))
x3, y3 = dcell(7, 5)
o.append(box(3, x3 + 4, y3 + 4, DW[5] - 4, 54, K4, 4, 8))
o.append(tag(RX, y3 + 31, "최대 512: 튀는 값이 있어요", K4, 3, 26))
o.append(caption("평균이 가운데 값보다 훨씬 크면 아주 큰 값이 섞여 있다는 신호예요.", 930, 4))
W("describe", o, "describe는 숫자 열마다 통계 여덟 줄을 한 표로 보여 줘요. count는 빈칸을 뺀 개수라서 age만 714예요. mean은 평균, std는 값이 퍼진 정도예요. 25%, 50%, 75%는 값을 작은 순서로 줄 세웠을 때 4분의 1, 가운데, 4분의 3 자리의 값이에요. 4파트에서 다시 써요. fare를 보면 평균은 32.20인데 가운데 값은 14.45예요. 최대 512 같은 큰 값이 평균만 끌어올린 거예요. 0과 1뿐인 survived처럼 오늘 안 쓰는 열은 흐리게 그렸어요." + REAL)

o = [sec("isnull")] + head(EB2, "isnull().sum()으로 열마다 빈칸 수를 세요", K2)
T = 196
CFS[0] = 28
o += cell({"id": "c-isn", "lines": ["df.isnull().sum()"], "n": 5}, 96, T, 860, sel="c-isn")
NUL = [("survived", 0), ("pclass", 0), ("sex", 0), ("age", 177), ("sibsp", 0), ("parch", 0), ("fare", 0), ("embarked", 2), ("class", 0), ("who", 0),
       ("adult_male", 0), ("deck", 688), ("embark_town", 2), ("alive", 0), ("alone", 0)]
NT, NFS, NLH = cbot(T, 1) + 14, 24, 1.36
NL = 96 + 105
o.append(mono(NL, NT, [f"{c:<15}{v:>4}" for c, v in NUL] + ["dtype: int64"], NFS, NLH))
BX0 = NL + NFS * 0.6 * 19 + 30
for i, (c, v) in enumerate(NUL):
    if v:
        o.append(bar(BX0, my(NT, i, NFS, NLH) - 12, max(v / 891 * 420, 10), 24, RED, WIPE(1) + DELAY(i * 30), 6))
o.append(tag(BX0 + 688 / 891 * 420 + 20, my(NT, 11, NFS, NLH), "688", RED, 1, 26, lead=False))
o.append(tag(BX0 + 177 / 891 * 420 + 20, my(NT, 3, NFS, NLH), "177", RED, 1, 26, lead=False))
# how it works: one column, True/False, sum
MX = 1130
o.append(label(MX, 210, "age 열에서 일어나는 일", INK, 30, rise(2)))
AGEV = ["22.0", "38.0", "26.0", "35.0", "35.0", "NaN"]
for i, v in enumerate(AGEV):
    y = 280 + i * 82
    nan = v == "NaN"
    o.append(vbox(MX, y, 170, 66, v, RED if nan else "#C9CED8", K5BG if nan else CARD, 28, rise(2) + DELAY(i * 50), dashed=nan))
    o.append(arrow(50, "#C9CED8", fade(3), f"position:absolute;left:{MX + 190}px;top:{y + 18}px"))
    o.append(f'<div data-build-in="rise order 3"{DELAY(i * 50)} style="position:absolute;left:{MX + 262}px;top:{y + 12}px">{tf("True" if nan else "False", 26)}</div>')
o.append(p(f"position:absolute;left:{MX}px;top:{280 + 6 * 82}px;width:320px;text-align:center;font-family:{MONO};font-size:28px;color:{GRAY}", "⋮"))
o.append(label(MX, 330 + 6 * 82, "isnull(): 비었으면 True", GRAY, 26, fade(3)))
o.append(p(f"position:absolute;left:{MX}px;top:{378 + 6 * 82}px;width:700px;font-size:26px;font-weight:700;line-height:1.4;color:{RED}", "sum(): True를 1로 세서 177", fade(4)))
W("isnull", o, "isnull은 칸마다 비었으면 True, 아니면 False를 돌려줘요. 45에서 배열에 비교를 하면 칸마다 True, False가 나왔던 것과 같아요. 그 표에 sum을 붙이면 True를 1, False를 0으로 세서 열마다 빈칸 수가 나와요. 오른쪽 그림은 age 열의 앞 여섯 칸이에요. 5번 승객의 나이가 비어서 True예요. 빨간 막대 넷이 오늘 채울 열이에요. deck은 891칸 중 688칸이 비었어요." + REAL)

o = [sec("loc-null")] + head(EB2, "loc[조건, 열]로 빈칸인 행만 골라 봐요", K2)
T = 196
CFS[0] = 30
LC = ['empty_age = df["age"].isnull()', 'print("나이 빈칸:", empty_age.sum(), "명")', 'df.loc[empty_age, ["sex", "age", "class"]].head()']
o += cell({"id": "c-loc", "lines": LC, "n": 6, "out": ["나이 빈칸: 177 명"]}, 96, T, 1728, sel="c-loc")
pre = "df.loc["
o.append(f'<div{fade(1)} style="position:absolute;left:{cx(96, pre) - 4:.0f}px;top:{ly(T, 2) - LH() / 2:.0f}px;width:{tw("empty_age") + 8:.0f}px;height:{LH():.0f}px;border-radius:6px;background:rgba(36,89,201,0.16);border-bottom:4px solid {BL}"></div>')
pre2 = "df.loc[empty_age, "
o.append(f'<div{fade(2)} style="position:absolute;left:{cx(96, pre2) - 4:.0f}px;top:{ly(T, 2) - LH() / 2:.0f}px;width:{tw(chr(91) + chr(34) + "sex" + chr(34) + ", " + chr(34) + "age" + chr(34) + ", " + chr(34) + "class" + chr(34) + chr(93)) + 8:.0f}px;height:{LH():.0f}px;border-radius:6px;background:rgba(15,124,134,0.16);border-bottom:4px solid {TEAL}"></div>')
o.append(tag(cx(96, LC[0]) + 40, ly(T, 0), "행마다 True, False (앞 장)", GRAY, None, 26))
LT = oy(T, 3, 0) + 50
LW = [130, 110, 140]
o.append(df("loc-df", 96 + 85, LT, ["sex", "age", "class"], [("male", "NaN", "Third"), ("male", "NaN", "Second"), ("female", "NaN", "Third"), ("male", "NaN", "Third"), ("female", "NaN", "Third")],
            LW, fs=30, rh=62, idx=[5, 17, 19, 26, 28], iw=70, cs={(i, 1): nan_style() for i in range(5)}, head_attrs=""))
o.append(f'<div{fade(1)} style="position:absolute;left:{96 + 85}px;top:{LT + 62}px;width:70px;height:{62 * 5}px;border-radius:8px;background:rgba(36,89,201,0.16);border-left:5px solid {BL}"></div>')
o.append(f'<div{fade(2)} style="position:absolute;left:{96 + 85 + 70}px;top:{LT}px;width:{sum(LW)}px;height:62px;border-radius:8px;background:rgba(15,124,134,0.16);border-bottom:4px solid {TEAL}"></div>')
o.append(tag(96 + 85 + 70 + sum(LW) + 60, LT + 31, "고른 열 세 개", TEAL, 2, 30))
o.append(tag(96 + 85 + 70 + sum(LW) + 60, LT + 62 * 3.5, "나이가 빈 행만 남았어요. 번호는 원래 번호", BL, 1, 30))
o.append(caption("빈칸 승객이 3등석에 많아 보여요. 고르기 전에 이렇게 직접 봐요.", 930, 3))
W("loc-null", o, "빈칸이 어떤 행인지 눈으로 보려면 loc을 써요. 45에서 loc[행 번호, 열 이름]으로 칸 하나를 골랐는데, 행 자리에 True, False Series를 넣으면 True인 행만 골라요. 열 자리에 열 이름 리스트를 넣으면 그 열만 남아요. 파란 칸이 행, 청록 칸이 열이에요. 왼쪽 번호 5, 17, 19는 원래 행 번호를 그대로 들고 와요. head를 붙여서 앞 다섯 줄만 봤어요." + REAL)

# ---------- part 3 ----------
o = [sec("mean-median")] + head(EB3, "평균은 큰 값에 끌려가고, 중앙값은 가운데 줄 선 값이에요", K3)
T = 196
CFS[0] = 30
MM = ['print("평균:", round(df["age"].mean(), 2))', 'print("중앙값:", round(df["age"].median(), 2))']
o += cell({"id": "c-mm", "lines": MM, "n": 7, "out": ["평균: 29.7", "중앙값: 28.0"]}, 96, T, 1728, sel="c-mm")
o.append(tag(cx(96, MM[1]) + 40, ly(T, 1), "median(): 작은 순서로 세운 가운데 값", K3, 1, 26))


def numline(y, lo, hi, ticks, marks, unit, order, name, width=1500, x0=260):
    """A number line with mean and median pins. marks: (value, text, color, above)."""
    sc = width / (hi - lo)
    out = [label(96, y - 22, name, INK, 30, rise(order)),
           f'<div{rise(order)} style="position:absolute;left:{x0}px;top:{y}px;width:{width}px;height:6px;border-radius:3px;background:#C9CED8"></div>']
    for t in ticks:
        tx_ = x0 + (t - lo) * sc
        out.append(p(f"position:absolute;left:{tx_ - 40:.0f}px;top:{y + 20}px;width:80px;text-align:center;font-family:{MONO};font-size:22px;color:{GRAY}", str(t), fade(order)))
        out.append(bar(tx_ - 1, y - 6, 3, 18, "#C9CED8", fade(order), 1))
    for k, (v, t, c, up) in enumerate(marks):
        mx_ = x0 + (v - lo) * sc
        ty = y - 92 if up else y + 56
        out.append(f'<div data-build-in="rise order {order + 1}"{DELAY(k * 160)} style="position:absolute;left:{mx_ - 10:.0f}px;top:{y - 7}px;width:20px;height:20px;border-radius:50%;background:{c};border:3px solid #FFFFFF"></div>')
        out.append(p(f"position:absolute;left:{mx_ - 160:.0f}px;top:{ty}px;width:320px;text-align:center;font-size:26px;font-weight:700;line-height:1.3;color:{c}", e(t), rise(order + 1) + DELAY(k * 160)))
    return out


o += numline(560, 0, 80, [0, 20, 40, 60, 80], [(29.7, "평균 29.7", K3, True), (28.0, "중앙값 28.0", GR, False)], "세", 1, "age")
o += numline(800, 0, 520, [0, 100, 200, 300, 400, 500], [(32.2, "평균 32.20", K4, True), (14.45, "중앙값 14.45", GR, False), (512.33, "최대 512.33", RED, True)], "", 3, "fare")
o.append(caption("나이는 둘이 비슷해요. 요금처럼 큰 값이 섞인 열은 중앙값이 가운데를 더 잘 보여 줘요.", 950, 5))
W("mean-median", o, "빈칸을 채울 숫자로 평균과 중앙값을 먼저 비교해요. 평균은 모두 더해 개수로 나눈 값이고, 중앙값은 작은 순서로 줄 세웠을 때 가운데 선 값이에요. 나이는 29.7과 28.0으로 비슷해서 어느 쪽을 써도 크게 다르지 않아요. 요금은 512 같은 큰 값 몇 개가 평균을 32.20까지 끌어올렸지만 중앙값은 14.45 그대로예요. 그래서 큰 값이 섞인 열은 중앙값으로 채우는 게 안전해요. 수업에서는 나이를 평균으로 채웠어요. 요금 숫자는 2파트 describe의 결과예요." + REAL)

o = [sec("fill-age")] + head(EB3, "fillna는 빈칸만 골라 정한 값으로 채워요", K3)
T = 196
CFS[0] = 32
FA = ['mean_age = df["age"].mean()', 'df.loc[:, "age"] = df["age"].fillna(mean_age)', 'df["age"].isnull().sum()']
o += cell({"id": "c-fa", "lines": FA, "n": 8, "out": ["np.int64(0)"]}, 96, T, 1728, sel="c-fa")
o.append(underline(1, cx(96, 'df.loc[:, "age"] = '), cx(96, FA[1]), ly(T, 1) + LH() / 2 - 4, K3, 5))
o.append(tag(cx(96, FA[1]) + 40, ly(T, 1), "새 열을 돌려줘요", K3, 1, 26))
o.append(underline(2, cx(96, "df.loc["), cx(96, "df.loc[:"), ly(T, 1) + LH() / 2 - 4, BL, 5))
o.append(label(96 + 105, oy(T, 3, 0) + 44, 'df.loc[:, "age"]의 콜론(:)은 모든 행이에요 (13의 [:])', BL, 26, fade(2)))
o.append(tag(cx(96, "np.int64(0)", True) + 40, oy(T, 3, 0), "남은 빈칸 0", GR, 4, 26))
AY = 640
AV = ["22.0", "38.0", "26.0", "35.0", "35.0", "NaN", "54.0", "2.0", "27.0", "14.0", "4.0", "58.0", "20.0", "39.0", "14.0", "55.0", "2.0", "NaN"]
o.append(label(96, AY - 50, "age 열 앞 18칸", GRAY, 26))
o.append(vbox(1620, AY - 150, 200, 76, "29.699…", K3, K3BG, 30, ' id="fa-src"'))
o.append(label(1620, AY - 196, "mean_age", K3, 26, "", True))
for i, v in enumerate(AV):
    x = 96 + (i % 9) * 168
    y = AY + (i // 9) * 120
    if v == "NaN":
        o.append(vbox(x, y, 150, 90, "NaN", RED, K5BG, 28, "", dashed=True))
        o.append(vbox(x, y, 150, 90, "29.7", K3, K3BG, 28, fly(3, "fa-src", DELAY(0 if i < 9 else 140))))
    else:
        o.append(vbox(x, y, 150, 90, v, "#C9CED8", CARD, 28))
o.append(caption("df[\"age\"] = df[\"age\"].fillna(mean_age)로 써도 같아요.", 950, 4))
W("fill-age", o, "fillna는 빈칸인 칸만 골라 괄호 안의 값을 넣은 새 열을 돌려줘요. 원래 열은 그대로라서 왼쪽에 다시 넣어야 바뀌어요. 수업 코드는 df.loc[:, \"age\"]에 넣었어요. 콜론 하나는 13의 슬라이싱 [:]처럼 처음부터 끝까지라는 뜻이라 모든 행의 age 칸이에요. df[\"age\"] =로 써도 결과가 같아요. 마지막 줄로 다시 세어 보면 빈칸이 0이에요. np.int64(0)은 NumPy가 센 정수 0이라는 표시예요." + REAL)

o = [sec("embark-count")] + head(EB3, "value_counts(dropna=False)로 빈칸까지 같이 세요", K3)
T = 196
CFS[0] = 30
CFS[0] = 26
o += cell({"id": "c-vc1", "lines": ['df["embark_town"].value_counts()'], "n": 9, "out": ["embark_town", "Southampton    644", "Cherbourg      168", "Queenstown      77", "Name: count, dtype: int64"]}, 96, T, 760)
o += cell({"id": "c-vc2", "lines": ['df["embark_town"].value_counts(dropna=False)'], "n": 10, "out": ["embark_town", "Southampton    644", "Cherbourg      168", "Queenstown      77", "NaN              2", "Name: count, dtype: int64"]}, 900, T, 924, sel="c-vc2")
o.append(underline(1, cx(900, 'df["embark_town"].value_counts('), cx(900, 'df["embark_town"].value_counts(dropna=False'), ly(T, 0) + LH() / 2 - 4, K3, 5))
o.append(box(2, cx(900, "", True) - 10, oy(T, 1, 4) - LH() / 2 - 2, tw("NaN              2") + 20, LH() + 4, RED, 4, 8))
o.append(tag(cx(900, "NaN              2", True) + 30, oy(T, 1, 4), "빈칸 2", RED, 2, 28))
o.append(tag(cx(96, "Queenstown      77", True) + 30, oy(T, 1, 3), "빈칸은 안 보여요", GRAY, 1, 26))
VY = 700
for k, (n_, v) in enumerate([("Southampton", 644), ("Cherbourg", 168), ("Queenstown", 77)]):
    y = VY + k * 84
    o.append(p(f"position:absolute;left:96px;top:{y}px;width:250px;font-family:{MONO};font-size:30px;font-weight:700;line-height:64px;color:{INK}", n_, rise(3)))
    o.append(bar(360, y + 10, v / 644 * 1100, 44, K3 if k == 0 else "#9CC9CD", WIPE(3) + DELAY(k * 120)))
o.append(tag(360 + 1100 + 30, VY + 32, "가장 많아요: 최빈값", K3, 4, 28))
W("embark-count", o, "글자 열은 평균을 낼 수 없어서 가장 많이 나온 값으로 채워요. 먼저 값마다 몇 번 나왔는지 세요. 45의 value_counts는 빈칸을 빼고 세서 왼쪽처럼 NaN이 안 보여요. dropna=False를 넣으면 빈칸도 한 줄로 세어 줘요. dropna는 빈칸을 뺀다는 뜻이고 False로 끄는 거예요. 탑승 항구는 Southampton이 644번으로 가장 많고 빈칸은 2개예요. 가장 많이 나온 값을 최빈값이라고 해요." + REAL)

o = [sec("mode")] + head(EB3, "최빈값은 mode()[0]으로 꺼내서 채워요", K3)
T = 196
CFS[0] = 28
MD = ['mode_town = df["embark_town"].mode()[0]', 'print("최빈값:", mode_town)', "", 'df.loc[:, "embark_town"] = df["embark_town"].fillna(mode_town)', 'df["embark_town"].value_counts(dropna=False)']
MO = ["최빈값: Southampton", "", "embark_town", "Southampton    646", "Cherbourg      168", "Queenstown      77", "Name: count, dtype: int64"]
o += cell({"id": "c-md", "lines": MD, "n": 12, "out": MO}, 96, T, 1100, sel="c-md")
o.append(underline(1, cx(96, 'mode_town = df["embark_town"].'), cx(96, MD[0]), ly(T, 0) + LH() / 2 - 4, K3, 5))
o.append(p(f"position:absolute;left:{cx(96, 'Southampton    ', True):.0f}px;top:{oy(T, 5, 3) - LH() / 2:.0f}px;font-family:{MONO};font-size:{CFS[0]}px;line-height:1.45;color:{INK};background:{K3BG};border-radius:6px;white-space:pre", "646", COUNT(3)))
o.append(tag(cx(96, "Southampton    646", True) + 30, oy(T, 5, 3), "644 + 빈칸 2", K3, 3, 26))
SX0 = 1290
o.append(label(SX0, 210, "mode()가 돌려주는 것", INK, 28, rise(2)))
o.append(mono(SX0, 270, ['df["embark_town"].mode()'], 24, 1.4, GRAY, rise(2)))
o.append(f'<div data-build-in="rise order 2" style="position:absolute;left:{SX0}px;top:330px;width:500px;height:96px;border-radius:12px;border:3px solid {K3};background:{K3BG};display:flex;flex-direction:row;align-items:center">'
         + p(f"width:70px;flex:none;text-align:center;font-family:{MONO};font-size:28px;font-weight:700;color:{K3};border-right:2px solid {K3}", "0") + p(f"padding-left:20px;font-family:{MONO};font-size:30px;font-weight:700;color:{INK}", "Southampton") + '</div>')
o.append(p(f"position:absolute;left:{SX0}px;top:446px;width:520px;font-size:26px;line-height:1.5;color:{SUB}", "값이 하나여도 Series예요.<br>같이 1등인 값이 있으면 줄이 늘어요.", rise(2)))
o.append(arrow(70, K3, fade(2), f"position:absolute;left:{SX0 + 215}px;top:590px;transform:rotate(90deg)"))
o.append(label(SX0 + 270, 585, "[0]", K3, 32, fade(2), True))
o.append(vbox(SX0, 690, 500, 100, "Southampton", K3, "#FFFFFF", 32, fade(2)))
o.append(p(f"position:absolute;left:{SX0}px;top:806px;width:500px;font-size:26px;line-height:1.4;color:{SUB}", "첫 번째 값 하나만 꺼내요.", fade(2)))
W("mode", o, "mode는 가장 많이 나온 값을 돌려주는데, 값이 하나뿐이어도 0번 칸에 담긴 Series로 줘요. 같이 1등인 값이 여럿이면 줄이 늘어나기 때문이에요. 그래서 뒤에 [0]을 붙여 첫 번째 값 하나만 꺼내요. 13에서 리스트[0]으로 첫 칸을 꺼내던 것과 같아요. Southampton을 fillna에 넣으면 빈칸 두 개가 채워져서 644가 646이 돼요. [0]을 빠뜨리면 생기는 일은 5파트에서 봐요." + REAL)

o = [sec("embarked")] + head(EB3, "embarked는 embark_town의 첫 글자로 채워요", K3)
T = 196
CFS[0] = 28
o += cell({"id": "c-emb0", "lines": ['df.loc[df["embark_town"].isnull(), ["embarked", "embark_town"]]'], "n": 11}, 96, T, 1728)
ET = cbot(T, 1) + 16
o.append(df("emb-df", 96 + 85, ET, ["embarked", "embark_town"], [("NaN", "NaN"), ("NaN", "NaN")], [170, 210], fs=28, rh=56, idx=[61, 829], iw=80, cs={(i, j): nan_style() for i in range(2) for j in range(2)}))
o.append(tag(96 + 85 + 80 + 380 + 40, ET + 56 * 2, "빈칸이 같은 두 행이에요 (채우기 전)", GRAY, None, 26))
T2 = 520
EM = ['df.loc[:, "embarked"] = df["embark_town"].str[0]', 'df[["embarked", "embark_town"]].isnull().sum()']
o += cell({"id": "c-emb", "lines": EM, "n": 14, "out": ["embarked       0", "embark_town    0", "dtype: int64"]}, 96, T2, 1000, sel="c-emb")
o.append(underline(1, cx(96, 'df.loc[:, "embarked"] = df["embark_town"]'), cx(96, EM[0]), ly(T2, 0) + LH() / 2 - 4, K3, 5))
o.append(tag(cx(96, "embark_town    0", True) + 30, oy(T2, 2, 1), "둘 다 0", GR, 3, 26))
LX = 1200
for k, (town, ch) in enumerate([("Southampton", "S"), ("Cherbourg", "C"), ("Queenstown", "Q")]):
    y = 560 + k * 130
    o.append(p(f"position:absolute;left:{LX}px;top:{y}px;height:90px;font-family:{MONO};font-size:34px;font-weight:700;line-height:90px;color:{INK};white-space:pre", f'<span id="ch-{k}" style="color:{K3};background:{K3BG};border-radius:6px">{ch}</span>{e(town[1:])}', rise(2) + DELAY(k * 100)))
    o.append(arrow(60, "#C9CED8", fade(2), f"position:absolute;left:{LX + 300}px;top:{y + 30}px"))
    o.append(vbox(LX + 400, y, 90, 90, ch, K3, K3BG, 38, fly(2, f"ch-{k}", DELAY(k * 120))))
o.append(label(LX, 500, ".str[0]: 글자마다 0번 칸", K3, 28, rise(2)))
W("embarked", o, "embarked와 embark_town은 같은 정보를 다르게 적은 열이에요. 위 셀처럼 두 열은 61번과 829번 행이 똑같이 비어 있었어요. embark_town은 앞 장에서 채웠으니 그 첫 글자를 따오면 embarked도 채워져요. .str은 글자 열의 값마다 글자 기능을 쓰게 해 주고, [0]은 13의 문자열 인덱스처럼 0번 글자예요. Southampton은 S, Cherbourg는 C, Queenstown은 Q가 돼요. 다시 세어 보면 두 열 모두 빈칸이 0이에요." + REAL)

o = [sec("deck")] + head(EB3, "category 열은 칸을 먼저 늘리고 채워요", K3)
T = 196
CFS[0] = 28
o += cell({"id": "c-dk1", "lines": ['print(df["deck"].dtype)', 'print(df["deck"].cat.categories.tolist())'], "n": 15, "out": ["category", "['A', 'B', 'C', 'D', 'E', 'F', 'G']"]}, 96, T, 1000)
T2 = 470
DK = ['df["deck"] = df["deck"].cat.add_categories("Unknown").fillna("Unknown")', 'print(df["deck"].cat.categories.tolist())', 'df["deck"].value_counts()']
o += cell({"id": "c-dk2", "lines": DK, "n": 16, "out": ["['A', 'B', 'C', 'D', 'E', 'F', 'G', 'Unknown']"]}, 96, T2, 1728, sel="c-dk2")
o.append(underline(2, cx(96, 'df["deck"] = df["deck"].'), cx(96, 'df["deck"] = df["deck"].cat.add_categories("Unknown")'), ly(T2, 0) + LH() / 2 - 4, K4, 5))
o.append(underline(3, cx(96, 'df["deck"] = df["deck"].cat.add_categories("Unknown")'), cx(96, DK[0]), ly(T2, 0) + LH() / 2 - 4, K3, 5))
# drawer picture
DX0, DY0 = 1110, 220
DP = 80
o.append(label(DX0, DY0 - 10, "정해진 칸 7개", K4, 28, rise(1)))
for k, c in enumerate("ABCDEFG"):
    o.append(vbox(DX0 + k * DP, DY0 + 40, 68, 80, c, K4, K4BG, 30, rise(1) + DELAY(k * 40)))
o.append(vbox(DX0 + 7 * DP, DY0 + 40, 128, 80, "Unknown", K4, "#FFFFFF", 22, rise(2), dashed=True))
o.append(tag(DX0, DY0 + 160, "칸에 없는 값은 못 넣어요", RED, 1, 26, lead=False))
VC = [("Unknown", 688), ("C", 59), ("B", 47), ("D", 33), ("E", 32), ("A", 15), ("F", 13), ("G", 4)]
BY0 = oy(T2, 3, 0) + 60
for k, (c, v) in enumerate(VC):
    y = BY0 + k * 44
    o.append(p(f"position:absolute;left:{96 + 105}px;top:{y}px;width:150px;font-family:{MONO};font-size:24px;font-weight:700;line-height:36px;color:{INK}", c, rise(4)))
    o.append(bar(96 + 260, y + 6, v / 688 * 900, 24, K4 if c == "Unknown" else "#D9B3C7", WIPE(4) + DELAY(k * 50), 6))
    o.append(p(f"position:absolute;left:{96 + 260 + v / 688 * 900 + 16:.0f}px;top:{y}px;font-family:{MONO};font-size:24px;line-height:36px;color:{SUB}", str(v), fade(4)))
W("deck", o, "deck은 갑판 이름 A부터 G만 들어가는 category 열이에요. category는 들어갈 수 있는 값을 칸 목록으로 정해 둔 열이에요. 서랍 칸이 일곱 개뿐이라 목록에 없는 Unknown은 바로 넣을 수 없어요. 그래서 cat.add_categories로 Unknown 칸을 먼저 하나 늘리고, 이어서 fillna로 빈칸을 채워요. 점으로 이어 쓰면 왼쪽부터 차례로 실행돼요. 688칸이 Unknown이 됐어요. 순서를 바꾸면 나는 오류는 5파트에서 봐요." + REAL)

# ---------- part 4 ----------
FARES = None
o = [sec("quantile")] + head(EB4, "quantile은 줄 세운 값의 25%, 50%, 75% 자리를 알려 줘요", K4)
T = 196
CFS[0] = 30
o += cell({"id": "c-q", "lines": ['df["fare"].quantile([0.25, 0.5, 0.75])'], "n": 17, "out": ["0.25     7.9104", "0.50    14.4542", "0.75    31.0000", "Name: fare, dtype: float64"]}, 96, T, 1000, sel="c-q")
o.append(tag(cx(96, "0.75    31.0000", True) + 40, oy(T, 1, 1), "describe의 25%, 50%, 75%와 같아요", GRAY, 1, 26))
# 891 sorted fares drawn as a strip of thin bars (real data from the demo: quartiles), heights capped
QY, QX, QW = 560, 96, 1728
o.append(label(QX, QY - 50, "요금 891개를 작은 순서로 세웠어요", INK, 28, rise(2)))
o.append(f'<div{WIPE(2)} style="position:absolute;left:{QX}px;top:{QY}px;width:{QW}px;height:200px;border-radius:12px;background:linear-gradient(90deg,#E8E3D6 0%,#D9CFB8 70%,#B26A00 100%)"></div>')
for k, (pct, v, t) in enumerate([(25, "7.91", "Q1 (25%)"), (50, "14.45", "가운데 (50%)"), (75, "31.00", "Q3 (75%)")]):
    x = QX + QW * pct / 100
    o.append(bar(x - 3, QY - 14, 6, 228, K4, rise(3) + DELAY(k * 150), 3))
    o.append(p(f"position:absolute;left:{x - 150:.0f}px;top:{QY + 230}px;width:300px;text-align:center;font-size:26px;font-weight:700;line-height:1.35;color:{K4}", f'{e(t)}<br><span style="font-family:{MONO};font-size:30px;color:{INK}">{v}</span>', rise(3) + DELAY(k * 150)))
o.append(p(f"position:absolute;left:{QX}px;top:{QY + 230}px;width:120px;font-family:{MONO};font-size:24px;color:{GRAY}", "0", fade(2)))
o.append(p(f"position:absolute;left:{QX + QW - 160}px;top:{QY + 230}px;width:160px;text-align:right;font-family:{MONO};font-size:24px;color:{GRAY}", "512.33", fade(2)))
W("quantile", o, "튀는 값을 찾으려면 먼저 값이 어디에 몰려 있는지 봐요. quantile에 0.25를 넣으면 작은 순서로 줄 세웠을 때 4분의 1 자리 값을 줘요. 리스트로 세 개를 넣으면 세 자리를 한 번에 줘요. 25% 자리를 Q1, 75% 자리를 Q3라고 불러요. 2파트 describe의 25%, 50%, 75% 줄과 같은 숫자예요. 승객 넷 중 셋은 31 이하를 냈는데 맨 끝은 512까지 가요. 띠 그림은 줄 세운 순서만 나타낸 그림이에요." + REAL, ("p4", "튀는 값과 중복"))

o = [sec("iqr")] + head(EB4, "Q1~Q3 폭(IQR)의 1.5배 밖이면 튀는 값으로 봐요", K4)
T = 196
CFS[0] = 26
IQ = ['q1 = df["fare"].quantile(0.25)', 'q3 = df["fare"].quantile(0.75)', "iqr = q3 - q1", "upper = q3 + 1.5 * iqr", "lower = q1 - 1.5 * iqr",
      'print("IQR:", iqr)', 'print("위 기준:", upper)', 'print("아래 기준:", lower)']
IO = ["IQR: 23.0896", "위 기준: 65.6344", "아래 기준: -26.724"]
o += cell({"id": "c-iqr", "lines": IQ, "n": 18, "out": IO}, 96, T, 760, sel="c-iqr")
# fence diagram, x from -40 to 120
FX0, FW = 960, 860
lo_, hi_ = -40, 120
sc = FW / (hi_ - lo_)
X = lambda v: FX0 + (v - lo_) * sc
FY = 520
o.append(f'<div style="position:absolute;left:{FX0}px;top:{FY + 120}px;width:{FW}px;height:4px;background:#C9CED8"></div>')
for t in (-40, -20, 0, 20, 40, 60, 80, 100, 120):
    o.append(p(f"position:absolute;left:{X(t) - 40:.0f}px;top:{FY + 136}px;width:80px;text-align:center;font-family:{MONO};font-size:20px;color:{GRAY}", str(t)))
o.append(f'<div{rise(1)} style="position:absolute;left:{X(7.9104):.0f}px;top:{FY + 60}px;width:{(31 - 7.9104) * sc:.0f}px;height:120px;border-radius:8px;border:4px solid {K4};background:{K4BG}"></div>')
o.append(bar(X(14.4542) - 2, FY + 60, 4, 120, K4, rise(1), 2))
o.append(p(f"position:absolute;left:{X(7.9104) - 70:.0f}px;top:{FY + 196}px;width:140px;text-align:center;font-size:22px;font-weight:700;color:{K4}", "Q1 7.91", rise(1)))
o.append(p(f"position:absolute;left:{X(31) - 70:.0f}px;top:{FY + 196}px;width:140px;text-align:center;font-size:22px;font-weight:700;color:{K4}", "Q3 31.0", rise(1)))
o.append(f'<div{WIPE(2)} style="position:absolute;left:{X(7.9104):.0f}px;top:{FY + 20}px;width:{(31 - 7.9104) * sc:.0f}px;height:24px;border:3px solid {INK};border-bottom:none;border-radius:6px 6px 0 0"></div>')
o.append(p(f"position:absolute;left:{X(7.9104) - 40:.0f}px;top:{FY - 22}px;width:{(31 - 7.9104) * sc + 80:.0f}px;text-align:center;font-size:24px;font-weight:700;color:{INK}", "IQR 23.09", rise(2)))
o.append(f'<div{WIPE(3)} style="position:absolute;left:{X(31):.0f}px;top:{FY + 110}px;width:{1.5 * 23.0896 * sc:.0f}px;height:24px;border-top:4px dashed {OR}"></div>')
o.append(f'<div{WIPE(3)} style="position:absolute;left:{X(-26.724):.0f}px;top:{FY + 110}px;width:{1.5 * 23.0896 * sc:.0f}px;height:24px;border-top:4px dashed {OR}"></div>')
o.append(p(f"position:absolute;left:{X(31):.0f}px;top:{FY + 70}px;width:{1.5 * 23.0896 * sc:.0f}px;text-align:center;font-size:22px;font-weight:700;color:{OR}", "× 1.5", rise(3)))
for v, t, c in [(65.6344, "위 기준 65.63", RED), (-26.724, "아래 기준 -26.72", GRAY)]:
    o.append(bar(X(v) - 3, FY - 30, 6, 240, c, rise(4), 3))
    o.append(p(f"position:absolute;left:{X(v) - 120:.0f}px;top:{FY - 74}px;width:240px;text-align:center;font-size:24px;font-weight:700;color:{c}", t, rise(4)))
for k, v in enumerate([71.3, 76.7, 82.2, 90.0, 110.9, 120]):
    o.append(f'<div data-build-in="rise order 5"{DELAY(k * 60)} style="position:absolute;left:{X(min(v, 117)) - 10:.0f}px;top:{FY + 108}px;width:20px;height:20px;border-radius:50%;background:{RED}"></div>')
o.append(p(f"position:absolute;left:{X(70):.0f}px;top:{FY + 196}px;width:{X(120) - X(70) + 40:.0f}px;text-align:center;font-size:24px;font-weight:700;color:{RED}", "→ 512까지 116명", rise(5)))
o.append(caption("요금은 0보다 작을 수 없어서 아래 기준 밖은 아무도 없어요. 위쪽만 봐요.", 940, 6))
W("iqr", o, "Q3에서 Q1을 뺀 폭을 IQR이라고 불러요. 가운데 절반이 퍼진 폭이에요. 요금은 31.0에서 7.91을 빼서 23.09예요. 이 폭의 1.5배만큼 Q3 위와 Q1 아래로 울타리를 쳐요. 위 기준은 31 + 1.5 × 23.09로 65.63, 아래 기준은 7.91 − 1.5 × 23.09로 -26.72예요. 울타리 밖의 값을 튀는 값, 이상치라고 불러요. 요금은 음수가 없어서 위쪽 울타리 밖의 116명만 걸려요. 1.5배는 많이 쓰는 약속이에요." + REAL)

o = [sec("outliers")] + head(EB4, "| (또는)로 위쪽이나 아래쪽 울타리 밖의 행을 골라요", K4)
T = 196
CFS[0] = 30
OL = ['outliers = df[(df["fare"] < lower) | (df["fare"] > upper)]', 'print("튀는 요금:", len(outliers), "명")', 'outliers[["pclass", "age", "fare"]].head()']
o += cell({"id": "c-ol", "lines": OL, "n": 19, "out": ["튀는 요금: 116 명"]}, 96, T, 1728, sel="c-ol")
bx = cx(96, 'outliers = df[(df["fare"] < lower) ')
o.append(box(1, bx - 8, ly(T, 0) - LH() / 2 - 2, tw("|") + 16, LH() + 4, K4, 4, 6))
o.append(tag(cx(96, OL[0]) + 40, ly(T, 0), "둘 중 하나만 맞아도 골라요 (45는 &)", K4, 1, 26))
OT = oy(T, 3, 0) + 60
OW = [130, 230, 170]
o.append(df("ol-df", 96 + 85, OT, ["pclass", "age", "fare"], [(1, "38.000000", "71.2833"), (1, "19.000000", "263.0000"), (1, "29.699118", "146.5208"), (1, "28.000000", "82.1708"), (1, "49.000000", "76.7292")],
            OW, fs=30, rh=66, idx=[1, 27, 31, 34, 52], iw=70))
o.append(tag(96 + 85 + 70 + sum(OW) + 50, OT + 66 * 2, "모두 65.63보다 비싸요", GRAY, 2, 26))
o.append(cell({"id": "c-ol2", "lines": ['df[(df["fare"] < lower) & (df["fare"] > upper)].shape'], "n": 20, "out": ["(0, 15)"]}, 980, OT + 20, 844)[0] if False else "")
CFS[0] = 22
o += cell({"id": "c-ol2", "lines": ['df[(df["fare"] < lower) & (df["fare"] > upper)].shape'], "n": 20, "out": ["(0, 15)"]}, 880, OT + 66 * 4, 944, attrs=rise(3))
o.append(tag(cx(880, "(0, 15)", True) + 30, oy(OT + 66 * 4, 1, 0), "&로 바꾸면 0행: 둘 다 맞는 요금은 없어요", RED, 3, 24))
CFS[0] = 30
W("outliers", o, "울타리 밖은 아래 기준보다 작거나 위 기준보다 큰 행이에요. 두 조건 중 하나만 맞아도 고르니까 45의 & 대신 |를 써요. |는 또는이라는 뜻이고 조건마다 괄호로 감싸는 것도 &와 같아요. 116명이 걸렸고 앞 다섯 명은 모두 1등석이에요. 오른쪽 아래처럼 &로 바꾸면 65.63보다 크면서 -26.72보다 작은 값은 없어서 0행이 나와요. 오류 없이 조용히 틀리니 조심해요." + REAL)

o = [sec("drop")] + head(EB4, "튀는 값 중 512만 지우고, 표[조건]을 다시 담아요", K4)
T = 196
CFS[0] = 30
o += cell({"id": "c-top5", "lines": ['df["fare"].sort_values(ascending=False).head(5)'], "n": 21, "out": ["737    512.3292", "679    512.3292", "258    512.3292", "438    263.0000", "88     263.0000", "Name: fare, dtype: float64"]}, 96, T, 1060)
o.append(box(1, cx(96, "", True) - 10, oy(T, 1, 0) - LH() / 2 - 2, tw("737    512.3292") + 20, oy(T, 1, 2) - oy(T, 1, 0) + LH() + 4, RED, 4, 8))
o.append(tag(cx(96, "737    512.3292", True) + 40, oy(T, 1, 1), "세 명이 똑같이 512", RED, 1, 26))
T2 = 640
DR = ["before = len(df)", 'df = df[df["fare"] < 512].copy()', 'print(before, "=>", len(df))']
o += cell({"id": "c-drop", "lines": DR, "n": 22, "out": ["891 => 888"]}, 96, T2, 1728, sel="c-drop")
o.append(underline(2, cx(96, "df = "), cx(96, 'df = df[df["fare"] < 512]'), ly(T2, 1) + LH() / 2 - 4, K4, 5))
o.append(tag(cx(96, DR[1]) + 40, ly(T2, 1), "512 미만만 남겨서 df에 다시 담아요", K4, 2, 26))
o.append(tag(cx(96, "891 => 888", True) + 40, oy(T2, 3, 0), "세 줄이 빠졌어요", GR, 3, 26))
o.append(p(f"position:absolute;left:1220px;top:290px;width:604px;font-size:28px;line-height:1.6;color:{INK}", "튀는 116명을 다 지우면<br>1등석 승객이 거의 사라져요.<br>수업에서는 혼자 동떨어진<br>512만 지웠어요.", rise(1)))
W("drop", o, "튀는 값이라고 다 지우지는 않아요. 116명 중 104명이 1등석이라 비싼 요금이 틀린 값이 아니에요. 6파트에서 다시 봐요. 요금을 큰 순서로 보면 512.33이 세 명이고 그다음은 263이라 512만 동떨어져 있어요. 그래서 수업에서는 512 미만인 행만 남겨서 df에 다시 담았어요. 지운다는 건 남길 행을 골라 다시 담는 거예요. 891행이 888행이 됐어요. 뒤의 .copy()는 고른 표를 새 표로 떼어 두는 메서드예요. pandas 3부터는 빼도 경고가 나지 않지만, 수업 코드처럼 붙여 두면 예전 버전에서도 안전해요." + REAL)

o = [sec("dup")] + head(EB4, "duplicated()는 앞에 나온 행과 15칸이 모두 같은 행을 찾아요", K4)
T = 196
CFS[0] = 28
DU = ['print("중복 행:", df.duplicated().sum())', 'df[df.duplicated(keep=False)].sort_values(["fare", "age"]).head()']
o += cell({"id": "c-dup", "lines": DU, "n": 23, "out": ["중복 행: 107"]}, 96, T, 1728, sel="c-dup")
o.append(tag(cx(96, "중복 행: 107", True) + 40, oy(T, 2, 0), "처음 나온 행은 빼고 센 수", K5, 1, 26))
o.append(underline(2, cx(96, "df[df.duplicated("), cx(96, "df[df.duplicated(keep=False"), ly(T, 1) + LH() / 2 - 4, K5, 5))
o.append(tag(cx(96, DU[1]) + 30, ly(T, 1), "처음 것도 같이 표시", K5, 2, 24))
DUC = ["pclass", "sex", "age", "fare", "deck", "embark_town", "alone"]
DUR = [(2, "male", "29.699118", "0.0", "Unknown", "Southampton", "True")] * 5
DUW = [110, 100, 170, 90, 150, 200, 110]
DT2 = oy(T, 2, 0) + 70
o.append(df("dup-df", 96 + 85, DT2, DUC, DUR, DUW, fs=28, rh=60, idx=[277, 413, 466, 481, 674], iw=80, attrs=STAGGER(3, 120)))
o.append(p(f"position:absolute;left:{96 + 85}px;top:{DT2 + 60 * 6 + 16}px;width:1100px;font-size:24px;color:{GRAY}", "열 15개 중 7개만 옮겼어요. 나머지 열도 모두 같아요."))
o.append(tag(96 + 85 + 80 + sum(DUW) + 60, DT2 + 60 * 3, "다섯 줄이 똑같아요", K5, 3, 30))
W("dup", o, "duplicated는 위에서부터 보면서 앞에 나온 행과 모든 칸이 같은 행에 True를 붙여요. sum으로 세면 107줄이에요. 처음 나온 행은 False라서 빠져요. keep=False를 넣으면 처음 것까지 모두 True가 돼서 같은 행끼리 다 볼 수 있어요. 요금과 나이 순서로 세우면 같은 행이 붙어서 나와요. 2등석 남자, 요금 0, 나이 29.699…, 혼자 탄 다섯 줄이 똑같아요." + REAL)

o = [sec("dup-check")] + head(EB4, "같아 보여도 다른 승객이에요. 지우기 전에 확인해요", K4)
T = 196
CFS[0] = 24
DG = ['df[df.duplicated(keep=False)][["pclass", "sex", "age", "fare", "embark_town"]].value_counts().head(3)']
DGO = ["pclass  sex   age        fare    embark_town", "3       male  29.699118  7.8958  Southampton    13", "                         8.0500  Southampton    12", "                         7.7500  Queenstown      8", "Name: count, dtype: int64"]
o += cell({"id": "c-dg", "lines": DG, "n": 24, "out": DGO}, 96, T, 1728, sel="c-dg")
o.append(tag(cx(96, DGO[1], True) + 30, oy(T, 1, 1), "똑같은 행이 13줄", K5, 1, 26))
PY = 600
for k in range(13):
    x = 96 + k * 128
    o.append(f'<div data-build-in="rise order 2"{DELAY(k * 40)} style="position:absolute;left:{x}px;top:{PY}px;width:108px;height:150px;border-radius:14px;border:3px solid #C9CED8;background:#FFFFFF;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px">'
             f'<x-icon name="Users" style="width:44px;height:44px;color:{GRAY}"></x-icon>' + p(f"font-family:{MONO};font-size:18px;color:{GRAY}", "3 male") + p(f"font-family:{MONO};font-size:18px;color:{GRAY}", "7.8958") + '</div>')
o.append(p(f"position:absolute;left:96px;top:{PY + 175}px;width:1728px;font-size:30px;font-weight:700;line-height:1.5;color:{INK}", "13명 모두 나이를 몰라서 평균 29.699…로 채운 3등석 남자예요. 이 표에는 이름과 표 번호 열이 없어요.", rise(3)))
o.append(caption("그래서 수업에서는 중복을 세기만 하고 지우지 않았어요.", 940, 4))
W("dup-check", o, "같은 행이 왜 이렇게 많은지 묶어서 세어 봐요. 중복 행만 고른 뒤 다섯 열로 value_counts를 하면 같은 조합이 몇 줄인지 나와요. 3등석 남자, 나이 29.699…, 요금 7.8958, Southampton이 13줄이에요. 이 13명은 원래 나이가 비어 있어서 평균으로 채운 사람들이에요. seaborn 타이타닉에는 이름과 표 번호 열이 없어서 다른 승객도 같은 행처럼 보여요. 진짜 겹친 기록인지 확인할 열이 없으면 지우지 않아요. 지울 때는 4파트처럼 남길 행을 골라 다시 담아요." + REAL)

# ---------- part 5 ----------
o = [sec("font")] + head(EB5, "그래프의 한글은 운영체제에 맞는 글꼴을 정해야 보여요", K6)
T = 196
CFS[0] = 24
o += cell({"id": "c-font", "lines": FONTC, "n": 26}, 96, T, 900, sel="c-font")
o.append(hl(96, T, 900, 4, 2, "mark", 1, "Windows"))
o.append(hl(96, T, 900, 6, 2, "run", 2, "Mac"))
o.append(tag(cx(96, FONTC[3]) + 30, ly(T, 3), "17의 if, elif", GRAY, None, 24))
IW, IX = 440, 1100
IH = IW * 787 / 1040
o.append(img(IX, 200, IW, "broken-1.png", rise(3), "img-broken"))
o.append(img(IX, 200 + IH + 40, IW, "main-1.png", rise(4), "img-fixed"))
o.append(p(f"position:absolute;left:{IX + IW + 30}px;top:{200 + IH / 2 - 40:.0f}px;font-size:28px;font-weight:700;line-height:1.4;color:{RED}", "글꼴을<br>안 정했을 때", rise(3)))
o.append(p(f"position:absolute;left:{IX + IW + 30}px;top:{240 + IH * 1.5 - 40:.0f}px;font-size:28px;font-weight:700;line-height:1.4;color:{GR}", "글꼴을<br>정한 뒤", rise(4)))
o.append(mono(96 + 105, 560, ["UserWarning: Glyph 45208 (\\N{HANGUL SYLLABLE NA})", "missing from font(s) DejaVu Sans."], 22, 1.45, RED, rise(3)))
o.append(p(f"position:absolute;left:{96 + 105}px;top:650px;width:820px;font-size:26px;line-height:1.5;color:{SUB}", "기본 글꼴 DejaVu Sans에 한글이 없어서 네모로 나와요.", rise(3)))
o.append(caption("Windows는 맑은 고딕, Mac은 AppleGothic을 골라요.", 900, 5))
W("font", o, "matplotlib의 기본 글꼴에는 한글이 없어서 제목과 축 이름이 네모로 깨져요. 셀 아래에는 글자를 못 찾았다는 UserWarning이 글자마다 나와요. platform.system은 지금 컴퓨터가 Windows인지 Mac인지 이름을 돌려줘요. Mac은 Darwin이라고 나와요. 17의 if와 elif로 Windows면 맑은 고딕, Mac이면 AppleGothic을 rcParams에 정해요. 한 번 실행하면 그 노트북의 그래프에 계속 적용돼요. 오른쪽 그림은 리눅스에서 만들어서 맑은 고딕 대신 나눔고딕으로 그렸어요. 왼쪽은 글꼴을 정하지 않은 같은 그래프예요." + REAL, ("p5", "그래프와 오류"))

o = [sec("hist")] + head(EB5, "ax.hist는 값을 구간 20개로 나눠 사람 수를 막대로 그려요", K6)
T = 196
CFS[0] = 26
CFS[0] = 22
o += cell({"id": "c-hist", "lines": HIST, "n": 27, "out": ["Text(0.5, 0, '나이(세)')"]}, 96, T, 960, sel="c-hist")
o.append(tag(cx(96, HIST[0]) - 210, ly(T, 0) + 70, "", GRAY, None, 24) if False else "")
HL_ = [(0, "그림판 fig와 그래프 칸 ax", GRAY, 1), (1, "bins=20: 구간 20개", K6, 2), (2, "위 제목", GRAY, 3), (3, "x축 이름", GRAY, 3)]
o.append(lspot(1, 96 + 87, T, 960 - 87, 10 + 4 * LH() + 8, T + 10 + 0 * LH(), LH(), bar=GRAY))
o.append(lspot(2, 96 + 87, T, 960 - 87, 10 + 4 * LH() + 8, T + 10 + 1 * LH(), LH(), bar=K6))
o.append(lspot_off(3))
o.append(p(f"position:absolute;left:{96 + 105}px;top:{oy(T, 4, 0) + 40:.0f}px;width:840px;font-size:24px;line-height:1.55;color:{SUB}",
           "fig는 그림 전체, ax는 그 안의 그래프 한 칸이에요.<br>figsize=(6, 4)는 가로 6, 세로 4 크기예요.<br>Text(...) 줄은 마지막 줄의 결과라 신경 쓰지 않아도 돼요.", fade(1)))
o.append(img(1110, 200, 714, "main-1.png", "", "img-hist"))
o.append(zoom(3, 1110 + 714 * 0.42, 200 + 30, 714 * 0.2, 714 * 0.7, 30, 1.8))
o.append(zoom_off(4))
o.append(p(f"position:absolute;left:1110px;top:{200 + 714 * 787 / 1040 + 20:.0f}px;width:714px;font-size:26px;font-weight:700;line-height:1.45;color:{K6}", "30살 근처 막대만 250명이 넘어요. 6파트에서 이유를 봐요.", rise(3)))
W("hist", o, "히스토그램은 나이를 일정한 구간으로 나눠 구간마다 몇 명인지 막대로 그려요. plt.subplots는 그림판 fig와 그 안의 그래프 칸 ax를 같이 돌려줘요. 19에서 배운 x, y = 함수()처럼 두 개를 받아요. ax.hist에 나이 열을 넣고 bins=20으로 0살부터 80살까지를 20칸으로 나눴어요. 한 칸이 4살쯤이에요. color는 막대 색, edgecolor는 테두리 색이에요. 30살 근처 막대 하나가 유난히 높아요. 6파트에서 이유를 봐요." + REAL)

o = [sec("c-sql")] + head(EB5, "SQL로 하던 정리를 pandas 한 줄로 해요", K6)
CMP = [("빈칸 세기", 'df["age"].isnull().sum()', "SELECT COUNT(*) FROM t WHERE age IS NULL", "36"),
       ("빈칸 행 보기", 'df.loc[df["age"].isnull(), 열]', "SELECT 열 FROM t WHERE age IS NULL", "36"),
       ("빈칸 채우기", 'df["age"] = df["age"].fillna(29.7)', "UPDATE t SET age = 29.7 WHERE age IS NULL", "36"),
       ("값마다 세기", 'df["town"].value_counts()', "SELECT town, COUNT(*) FROM t GROUP BY town", "39"),
       ("행 지우기", 'df = df[df["fare"] < 512]', "DELETE FROM t WHERE fare >= 512", "36"),
       ("가운데 값", 'df["fare"].quantile(0.5)', "다루지 않았어요", "")]
o += plain_rows(96, 210, 1728, [(a, b, c) for a, b, c, d in CMP], [230, 690, 760], 1, 104, ["할 일", "pandas (오늘)", "SQL (36~43)"], 26, mono_cols=(1, 2))
o.append(caption("SQL은 서버의 표를 바꾸고, pandas는 메모리의 표를 다시 담아요.", 930, 8))
W("c-sql", o, "오늘 한 정리는 SQL에서도 해 본 일이에요. 빈칸 세기는 36의 IS NULL과 COUNT, 채우기는 36의 UPDATE와 WHERE, 값마다 세기는 39의 GROUP BY, 행 지우기는 36의 DELETE예요. 차이는 결과를 다루는 방식이에요. SQL은 데이터베이스의 표를 바로 바꾸고, pandas는 새 열이나 새 표를 돌려줘서 df에 다시 담아야 바뀌어요. 표에서 t와 town은 줄여 적은 이름이에요.")

o = [sec("e-cat")] + head(EB5, "category 열에 없는 값을 바로 넣으면 TypeError", K5)
T = 210
CFS[0] = 30
o += cell({"id": "c-ec", "lines": ['df["deck"] = df["deck"].fillna("Unknown")'], "n": 2, "out": ["TypeError: Cannot setitem on a Categorical with a new category (Unknown),", "set the categories first"], "err": True, "red": (1,)}, 96, T, 1728)
o.append(underline(1, cx(96, "", True), cx(96, "TypeError: Cannot setitem on a Categorical with a new category (Unknown)", True), oy(T, 1, 0) + LH() / 2 - 2, RED, 5))
o.append(reading(96 + 105, oy(T, 1, 1) + 56, "new category (Unknown): 칸 목록에 없는 값이에요. set the categories first: 칸부터 정하래요.", RED, 2, 28))
o.append(fix(96, 560, '.fillna("Unknown")', '.cat.add_categories("Unknown").fillna("Unknown")', 3, 30))
for k, c in enumerate("ABCDEFG"):
    o.append(vbox(96 + k * 92, 720, 80, 80, c, K4, K4BG, 30, rise(4)))
o.append(vbox(96 + 7 * 92, 720, 130, 80, "Unknown", K4, "#FFFFFF", 24, rise(4) + DELAY(200)))
o.append(tag(96 + 7 * 92 + 160, 760, "칸을 먼저 늘리고 채워요 (3파트)", K4, 4, 28))
W("e-cat", o, "category 열에 칸 목록에 없는 값을 바로 넣으면 TypeError가 나요. 오류 메시지는 Unknown이 새 카테고리라서 넣을 수 없으니 카테고리부터 정하라는 뜻이에요. 3파트처럼 cat.add_categories로 Unknown 칸을 먼저 늘리고 fillna를 붙여요. 문자열 열이나 숫자 열은 이 단계가 없어서 category 열에서만 만나요. 어떤 열이 category인지는 2파트 info의 Dtype에서 봐요." + NEW1 + REAL)

o = [sec("e-assign")] + head(EB5, "fillna 결과를 다시 담지 않으면 빈칸이 그대로예요", K5)
T = 200
CFS[0] = 28
CFS[0] = 26
o += cell({"id": "c-ea1", "lines": ['df["age"].fillna(29.7)', 'df["age"].isnull().sum()'], "n": 2, "out": ["np.int64(177)"]}, 96, T, 820)
o.append(tag(cx(96, "np.int64(177)", True) + 30, oy(T, 2, 0), "그대로 177", RED, 1, 26))
o += cell({"id": "c-ea2", "lines": ['df["age"].fillna(29.7, inplace=True)', 'df["age"].isnull().sum()'], "n": 3, "out": ["ChainedAssignmentError: A value is being set", "on a copy of a DataFrame or Series through", "chained assignment using an inplace method.", "np.int64(177)"], "err": True, "red": (1, 2)}, 1004, T, 820)
o.append(tag(cx(1004, "np.int64(177)", True) + 30, oy(T, 2, 3), "여전히 177", RED, 2, 26))
o.append(reading(96, 640, "fillna는 새 열을 돌려줄 뿐이에요. inplace=True도 열 하나에 쓰면 원본을 못 바꿔요 (pandas 3).", RED, 2, 28))
o.append(fix(96, 740, 'df["age"].fillna(29.7)', 'df["age"] = df["age"].fillna(29.7)', 3, 32))
o.append(caption("고친 셀은 np.int64(0)이 나와요. 다시 세어서 확인해요.", 900, 4))
W("e-assign", o, "가장 흔한 실수는 fillna만 치고 다시 담지 않는 거예요. fillna는 채운 새 열을 돌려줄 뿐이라 df는 그대로라서 빈칸이 177로 남아요. 인터넷 예제에 자주 나오는 inplace=True도 pandas 3에서는 열 하나에 쓰면 원본을 못 바꿔요. 셀 아래에 ChainedAssignmentError 경고가 나고 여전히 177이에요. 실제 경고는 더 길어서 첫 문장만 옮겼어요. 경고는 오류와 달리 셀이 멈추지 않아요. 왼쪽에 df[\"age\"] =를 붙여 다시 담으면 0이 돼요." + NEW1 + REAL)

o = [sec("e-mode")] + head(EB5, "mode()에 [0]을 빼면 오류 없이 빈칸이 남아요", K5)
T = 200
CFS[0] = 28
EMD = ['df.loc[:, "embark_town"] = df["embark_town"].fillna(df["embark_town"].mode())', 'df["embark_town"].value_counts(dropna=False)']
o += cell({"id": "c-emd", "lines": EMD, "n": 2, "out": ["embark_town", "Southampton    644", "Cherbourg      168", "Queenstown      77", "NaN              2", "Name: count, dtype: int64"]}, 96, T, 1728)
o.append(tint(1, cx(96, 'df.loc[:, "embark_town"] = df["embark_town"].fillna(') - 4, ly(T, 0) - LH() / 2, tw('df["embark_town"].mode()') + 8, LH(), RED))
o.append(box(2, cx(96, "", True) - 10, oy(T, 2, 4) - LH() / 2 - 2, tw("NaN              2") + 20, LH() + 4, RED, 4, 8))
o.append(tag(cx(96, "NaN              2", True) + 30, oy(T, 2, 4), "빈칸 2개가 그대로", RED, 2, 26))
o.append(reading(1000, oy(T, 2, 1) - 20, "mode()는 0번 칸 하나짜리 Series예요.", INK, 3, 28))
o.append(reading(1000, oy(T, 2, 1) + 34, "fillna는 Series를 받으면 같은 번호 칸끼리 채워요.", INK, 3, 28))
o.append(reading(1000, oy(T, 2, 1) + 88, "0번 행만 채우는데 0번은 비어 있지 않아요.", INK, 3, 28))
o.append(fix(96, 820, '.fillna(df["embark_town"].mode())', ".fillna(df[\"embark_town\"].mode()[0])", 4, 28))
W("e-mode", o, "mode 뒤에 [0]을 빼면 오류도 경고도 없이 빈칸이 그대로 남아요. mode는 0번 칸에 Southampton이 든 Series를 돌려줘요. fillna에 값 대신 Series를 넣으면 행 번호가 같은 칸끼리 짝지어 채워요. 그래서 0번 행만 채우려고 하는데 0번 승객은 원래 Southampton이라 비어 있지 않아요. 비어 있는 61번과 829번은 짝이 없어서 그대로예요. 채운 뒤에는 꼭 value_counts(dropna=False)나 isnull().sum()으로 다시 세어요." + NEW1 + REAL)

o = [sec("e-dup")] + head(EB5, "있는 값으로 채우면 중복이 늘 수 있어요", K5)
T = 196
CFS[0] = 26
ED = ['print("채우기 전:", df.duplicated().sum())', "", "a = df.copy()", 'a["age"] = a["age"].fillna(a["age"].mean())', 'print("평균으로:", a.duplicated().sum())', "",
      "b = df.copy()", 'b["age"] = b["age"].fillna(b["age"].median())', 'print("중앙값으로:", b.duplicated().sum())']
o += cell({"id": "c-ed", "lines": ED, "n": 2, "out": ["채우기 전: 107", "평균으로: 107", "중앙값으로: 110"]}, 96, T, 1000, sel="c-ed")
o.append(tag(cx(96, "중앙값으로: 110", True) + 30, oy(T, 9, 2), "3줄 늘었어요", RED, 1, 26))
o.append(tag(cx(96, "채우기 전: 107", True) + 30, oy(T, 9, 0), "빈칸끼리도 같은 값으로 봐요", GRAY, 1, 24))
o.append(label(1180, 220, "새로 생긴 중복 3줄", RED, 28, rise(2)))
o.append(df("ed-df", 1180, 270, ["pclass", "sex", "age", "fare"], [(3, "male", "28.0", "7.8958"), (3, "male", "28.0", "56.4958"), (3, "male", "28.0", "9.5000")], [110, 100, 90, 140], fs=28, rh=58, idx=[105, 826, 868], iw=80, attrs=rise(2), cs={(i, 2): f"color:{RED};font-weight:700" for i in range(3)}))
o.append(p(f"position:absolute;left:1180px;top:540px;width:640px;font-size:26px;line-height:1.5;color:{INK}", "원래 28살인 승객과 15칸이 모두 같아졌어요.<br>평균 29.699…는 원래 없던 나이라서<br>중복이 늘지 않았어요.", rise(3)))
o.append(caption("빈칸을 채운 뒤에는 duplicated()를 다시 세어요.", 940, 4))
W("e-dup", o, "채우는 값에 따라 중복 수가 달라져요. duplicated는 빈칸끼리도 같은 값으로 봐서 채우기 전에도 107이에요. 평균 29.699…는 원래 데이터에 없는 나이라서 채워도 107 그대로예요. 중앙값 28은 원래 28살인 승객이 있어서, 나이만 비어 있던 승객 세 명이 그 사람들과 15칸이 모두 같아졌어요. 그래서 110이 됐어요. copy로 원본 df를 남겨 두고 a와 b에 따로 채워 비교했어요. 채운 뒤에는 중복을 다시 세어 봐요." + NEW1 + REAL)

# ---------- part 6 ----------
o = [sec("x-fare")] + head(EB6, "튀는 요금 116명은 누구일까요", K6)
T = 196
CFS[0] = 30
o += cell({"id": "c-xf", "lines": ['outliers["pclass"].value_counts()'], "n": 25, "out": ["pclass", "1    104", "3      7", "2      5", "Name: count, dtype: int64"]}, 96, T, 900, sel="c-xf")
BY_ = 560
for k, (c, v, col) in enumerate([("1등석", 104, K4), ("3등석", 7, "#D9B3C7"), ("2등석", 5, "#D9B3C7")]):
    y = BY_ + k * 110
    o.append(p(f"position:absolute;left:96px;top:{y}px;width:150px;font-size:32px;font-weight:700;line-height:80px;color:{INK}", c, rise(1)))
    o.append(bar(260, y + 10, v / 104 * 1300, 60, col, WIPE(1) + DELAY(k * 120), 10))
    o.append(p(f"position:absolute;left:{260 + v / 104 * 1300 + 20:.0f}px;top:{y}px;font-family:{MONO};font-size:34px;font-weight:700;line-height:80px;color:{INK}", f'<span{COUNT(1) if k == 0 else ""}>{v}</span>명', fade(1)))
o.append(p(f"position:absolute;left:1080px;top:230px;width:744px;font-size:30px;line-height:1.6;color:{INK}", "4파트의 outliers에서 객실 등급을 세었어요.<br>비싼 1등석 표가 대부분이에요.", rise(2)))
o.append(caption("튀는 값은 틀린 값이 아닐 수 있어요. 누구인지 보고 지울지 정해요.", 940, 3))
W("x-fare", o, "4파트에서 고른 튀는 요금 116명을 객실 등급별로 세어 봐요. 45의 value_counts를 outliers 표의 pclass 열에 썼어요. 104명이 1등석이에요. 1등석은 원래 비싸서 요금이 높은 게 자연스러워요. 이 사람들을 다 지우면 1등석 승객이 거의 사라져서 데이터가 한쪽으로 쏠려요. 그래서 수업에서는 혼자 동떨어진 512만 지웠어요. IQR은 살펴볼 후보를 알려 줄 뿐이고, 지울지는 사람이 정해요." + REAL, ("p6", "실제 상황"))

o = [sec("x-hist")] + head(EB6, "평균으로 채우면 29.7살에 177명이 몰려요", K6)
T = 196
CFS[0] = 26
o += cell({"id": "c-xh", "lines": ['(df["age"].round(1) == 29.7).sum()'], "n": 4, "out": ["np.int64(0)"]}, 96, T, 820)
o += cell({"id": "c-xh2", "lines": ['(df["age"].round(1) == 29.7).sum()'], "n": 6, "out": ["np.int64(177)"]}, 1004, T, 820, sel="c-xh2")
o.append(label(96 + 105, oy(T, 1, 0) + 34, "채우기 전", GRAY, 24))
o.append(label(1004 + 105, oy(T, 1, 0) + 34, "평균으로 채운 뒤", K6, 24))
IWX = 760
IHX = IWX * 787 / 1040
SCX = IWX / 1040
IY = 420
for k, (name, x0, h, ymax, c_, t_) in enumerate([("xhist-1.png", 150, 84, 103.0, GRAY, "84명"), ("xhist-2.png", 1004, 261, 274.0, K6, "261명")]):
    o.append(img(x0, IY, IWX, name, rise(k + 1) if k else "", f"img-xh{k}"))
    # 28.3-32.3 bin in the kernel PNG: x 429-471 px, axis 0 at y 680 px, top at y 64 px = ymax
    top = 680 - h / ymax * (680 - 64)
    bx_, by_ = x0 + 429 * SCX - 2, IY + top * SCX - 8
    o.append(box(k + 1, bx_, by_, 42 * SCX + 12, (680 - top) * SCX + 16, RED if k else K6, 4, 6))
    o.append(tag(bx_ + 42 * SCX + 30, by_ + 30, t_, RED if k else K6, k + 1, 30, lead=True))
W("x-hist", o, "5파트 그래프에서 30살 근처 막대가 유난히 높았던 이유를 봐요. 나이가 비어 있던 177명을 모두 평균 29.699…로 채웠기 때문이에요. 셀로 세어 보면 채우기 전에는 29.7살인 사람이 0명, 채운 뒤에는 177명이에요. round(1)은 소수 첫째 자리까지 반올림이에요. 왼쪽과 오른쪽 그래프에서 같은 구간을 표시했어요. 세로축 눈금이 달라서 높이 대신 숫자를 비교해요. 평균으로 채우면 빈칸은 없어지지만 분포가 가운데로 쏠려요. 그래서 채운 뒤에는 그래프로 다시 확인해요. 이 셀은 새 노트북에서 차례로 실행했어요. 셀 번호 사이의 [5]는 평균으로 채우고 그래프를 다시 그린 셀이에요. 막대 높이 84와 261은 그래프와 같은 구간으로 따로 세어 확인했어요." + REAL)

o = [sec("x-pipe")] + head(EB6, "정리 순서를 한 셀에 모아 처음부터 다시 돌려요", K6)
T = 196
CFS[0] = 26
XP = ["import pandas as pd", "import seaborn as sns", "", 'df = sns.load_dataset("titanic")', "", 'df.loc[:, "age"] = df["age"].fillna(df["age"].mean())', 'town = df["embark_town"].mode()[0]',
      'df.loc[:, "embark_town"] = df["embark_town"].fillna(town)', 'df.loc[:, "embarked"] = df["embark_town"].str[0]', 'df["deck"] = df["deck"].cat.add_categories("Unknown").fillna("Unknown")',
      'df = df[df["fare"] < 512].copy()', "", 'print("남은 빈칸:", df.isnull().sum().sum())', 'print("크기:", df.shape)']
o += cell({"id": "c-xp", "lines": XP, "n": 1, "out": ["남은 빈칸: 0", "크기: (888, 15)"]}, 96, T, 1300, sel="c-xp")
for k, (i, t) in enumerate([(5, "숫자 빈칸: 평균"), (6, "글자 빈칸: 최빈값"), (8, "다른 열에서: 첫 글자"), (9, "category: 칸 늘리고"), (10, "튀는 값: 512만 지우기")]):
    o.append(run(k + 1, 96 + 89, T + 10 + i * LH(), 1300 - 93, LH() if i != 6 else 2 * LH()))
    o.append(tag(96 + 1300 + 30, ly(T, i) if i != 6 else ly(T, 6) + LH() / 2, t, GR, k + 1, 26))
o.append(run_off(6))
o.append(tag(cx(96, "크기: (888, 15)", True) + 30, oy(T, 14, 1), "빈칸 0, 891행에서 888행", GR, 6, 26))
W("x-pipe", o, "수업에서 셀마다 나눠 한 정리를 한 셀에 모았어요. 노트북을 새로 열어도 이 셀 하나로 같은 표를 다시 만들 수 있어요. 순서는 숫자 빈칸, 글자 빈칸, 다른 열에서 채우기, category, 튀는 값 지우기예요. 마지막 두 줄로 확인해요. isnull().sum()은 열마다 빈칸 수이고, 한 번 더 sum을 붙이면 표 전체의 빈칸 수예요. 0이고 크기는 888행 15열이에요. 다음 강의에서는 이 표를 모델에 넣어요." + NEW1 + REAL)

# ---------- wrap up ----------
o = [sec("trouble")] + head("정리", "막히면 출력의 마지막 줄을 봐요", RED)
TR = [("ModuleNotFoundError: No module named 'seaborn'", "프로젝트에 안 넣었어요", "uv add seaborn matplotlib"),
      ("URLError 같은 연결 오류", "load_dataset이 인터넷에서 못 받았어요", "연결 확인 뒤 다시 실행"),
      ("TypeError: Cannot setitem on a Categorical ...", "category 칸에 없는 값이에요", "add_categories 먼저"),
      ("ChainedAssignmentError", "열 하나에 inplace=True를 썼어요", 'df["열"] = ... 로 다시 담기'),
      ("채웠는데 isnull().sum()이 그대로예요", "결과를 다시 안 담았거나 mode()에 [0]이 없어요", "= 와 [0] 확인"),
      ("Glyph ... missing from font(s)", "한글 글꼴을 안 정했어요", "운영체제 글꼴 셀 실행"),
      ("고르기 결과가 0행이에요", "또는 자리에 &를 썼어요", "(조건1) | (조건2)")]
for i, (q, a_, cmd) in enumerate(TR):
    o.append(f'<div data-build-in="rise order {min(i + 1, 5)}" style="position:absolute;left:96px;top:{200 + i * 100}px;width:1728px;height:100px;display:flex;flex-direction:row;align-items:center;gap:26px;border-bottom:2px solid {LINE}">'
             + '<div style="flex:1;display:flex;flex-direction:column;gap:4px">' + p(f"{'font-family:' + MONO + ';' if q.isascii() else ''}font-size:25px;font-weight:700;color:{RED};white-space:nowrap", e(q)) + p(f"font-size:25px;color:{INK}", e(a_)) + '</div>'
             + p(f"width:520px;flex:none;font-size:27px;font-weight:700;color:{GR};white-space:pre", '✓ ' + e(cmd)) + '</div>')
o.append(caption("셀은 위에서부터 차례로 실행해요. 다시 열었다면 첫 셀부터 실행해요.", 950))
W("trouble", o, "막히면 셀 출력의 마지막 줄부터 읽어요. 위 두 줄은 준비할 때, 가운데 셋은 빈칸을 채울 때, 아래 둘은 그래프와 고르기에서 생겨요. 경고는 셀이 멈추지 않아서 지나치기 쉬워요. 빨간 글자가 보이면 결과를 다시 세어 봐요. 연결 오류의 실제 이름은 환경마다 달라요.", ("trouble", "정리"))

o = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">상황별로 고르는 방법</h2>']
CH = [("빈칸 세기", "df.isnull().sum()", K2), ("숫자 빈칸", 'fillna(df["열"].mean()) 큰 값이 섞이면 median()', K3), ("글자 빈칸", 'fillna(df["열"].mode()[0])', K3),
      ("다른 열에서", 'df["embark_town"].str[0]', K3), ("category 빈칸", 'cat.add_categories("Unknown").fillna("Unknown")', K3),
      ("튀는 값 찾기", "q3 + 1.5 * iqr 밖, | 로 고르기", K4), ("행 지우기", "df = df[남길 조건].copy()", K4), ("중복 세기", "df.duplicated().sum(), keep=False", K4),
      ("한글 그래프", 'plt.rcParams["font.family"] = 글꼴', K6), ("분포 보기", 'ax.hist(df["열"], bins=20)', K6)]
for i, (k, d, c) in enumerate(CH):
    x, y = 96 + (i // 5) * 884, 190 + (i % 5) * 124
    o.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:844px;height:110px;display:flex;flex-direction:column;justify-content:center;gap:4px;border-bottom:2px solid {LINE}">'
             + p(f"font-size:26px;font-weight:700;color:{c}", e(k)) + p(f"font-family:{MONO};font-size:{24 if len(d) > 40 else 28}px;font-weight:700;color:{INK};white-space:pre", e(d)) + '</div>')
o.append(p(f"position:absolute;left:96px;top:850px;width:1728px;font-size:32px;font-weight:700;line-height:1.5;color:{INK}", "채운 뒤에는 다시 세고, 지우기 전에는 누구인지 봐요.<br>" + f'<span style="color:{GRAY}">다음: 머신러닝 기초에서 정리한 표를 모델에 넣어요.</span>'))
W("cheatsheet", o, "빈칸은 isnull().sum()으로 세고, 숫자는 평균이나 중앙값, 글자는 최빈값으로 채워요. 같은 정보가 다른 열에 있으면 거기서 가져오고, category 열은 칸을 먼저 늘려요. 튀는 값은 IQR 울타리로 후보를 찾은 뒤 누구인지 보고 정해요. 중복은 세어 보고 같은 기록인지 확인한 뒤 지워요. 마지막으로 그래프로 분포를 확인해요. 다음 머신러닝 수업에서 이 표를 모델에 넣어요.")

# ---------- toc ----------
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
parts_ = [("Lightbulb", K1, "왜 필요한가", "why", "min"), ("Search", K2, "훑어보고 빈칸 찾기", "info", "loc-null"), ("Wrench", K3, "빈칸 채우기", "mean-median", "deck"),
          ("Activity", K4, "튀는 값과 중복", "quantile", "dup-check"), ("Warning", K6, "그래프와 오류", "font", "e-dup"), ("Star", K5, "실제 상황", "x-fare", "x-pipe")]
t = [f'<section id="toc" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>']
for i, (ic, c, h, a, b) in enumerate(parts_):
    x, y = 96 + (i // 3) * 884, 230 + (i % 3) * 190
    t.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:844px;height:160px;display:flex;flex-direction:row;align-items:center;gap:28px;border-bottom:2px solid {LINE}">'
             f'<p style="width:70px;font-size:72px;font-weight:900;color:{c}">{i + 1}</p><x-icon name="{ic}" style="width:52px;height:52px;color:{c}"></x-icon>'
             f'<p style="flex:1;font-size:44px;font-weight:700;color:{INK}">{e(h)}</p><p style="font-size:28px;color:{GRAY}">{page[a]}–{page[b]}쪽</p></div>')
t.append(f'<p style="position:absolute;left:96px;top:880px;font-size:30px;color:{SUB}">{page["setup"]}쪽은 프로젝트 준비, {page["trouble"]}–{page["cheatsheet"]}쪽은 막힐 때와 한 장 요약이에요.</p>')
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(t) + "\n<aside>" + e("2파트에서 표를 훑어 빈칸을 찾고, 3파트에서 채우고, 4파트에서 튀는 값과 중복을 다뤄요. 1파트는 왜 정리해야 하는지와 전체 순서예요. 5파트는 그래프를 그리고 SQL과 비교한 뒤 자주 하는 실수를 모았어요. 6파트는 튀는 요금이 누구인지, 평균으로 채우면 그래프가 어떻게 바뀌는지, 정리 전체를 한 셀로 모으는 법이에요.") + "</aside>\n</section>\n")
deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-23T10:00:00Z"}, "lists": "css", "title": "데이터 정리하기 (타이타닉 전처리)", "order": ORDER, "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
print(len(ORDER), "slides")
