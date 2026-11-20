"""Generates every slide of the NumPy and pandas deck (45) and slides/deck.json.

Story: the class's spending notebook (pandas.ipynb in a new uv project ml-basics). Starts from a five-line for loop that
adds up one category, places the list, the NumPy array and the pandas DataFrame on one picture, then NumPy (* 2, + 500,
sum mean min max, shape dtype, a True/False mask and arr[mask]), pandas (making a DataFrame from a dictionary, shape and
head, one column, a list of columns, a condition per row, table[condition], & with brackets, sort_values), a new column
with //, loc, groupby and value_counts. Part 5 lines the three up with lists and SQL (36-41) and collects the errors,
part 6 answers three questions about the month. The class code is fixed where it was off (the mean was labelled
"합계", shops and categories were defined twice, the first list had 13 values and the rest 12, an unused arr * 2,
a value_counts().sort_values() that was already sorted); zip is shown for reading only (not learned yet).
Every cell and output comes from tools/demo.sh (tools/run_nb.py runs the cells with the project kernel), kept in tools/demo.log.

Layout rules (Stageshow skill, github.com/benjitaylor/skills, read in full for this deck):
1. one focal object per slide (a notebook cell, a DataFrame drawn as VS Code shows it, or one dark code strip)
2. terms are labelled on the code line or on the table with leader tags, not in separate cards (annotations.md)
3. say it once: what the speaker notes say does not repeat in cards; one caption at most
4. no empty bands: the table or the picture grows to fill; the payoff gets the room (craft.md, Restraint)
5. values move instead of swapping: boxes fly from the array into the result, a stale cell gets a ring, numbers count up
Highlights come from tools/HIGHLIGHT.md, as many kinds as fit. No typing effect.
Usage: python3 tools/gen.py slides
"""

import html, json, os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from highlight import (spot, spot_off, cursor, cursor_off, ring, box, underline, lspot, lspot_off, run, run_off, zoom, zoom_off,
                       shine, shake, pulse, grow, link, keys, SLAM, COUNT, MARK, DELAY, WIPE, STAGGER, MORPH, MORPH_FROM, tok)

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
INK, SUB, LINE, CARD = "#1D2330", "#4A5262", "#E1DED6", "#FFFFFF"
BL, GR, OR, PUR, RED, TEAL, GRAY = "#2459C9", "#1F8A4C", "#B26A00", "#5A3BB8", "#A33131", "#0F7C86", "#6A7180"
JP = "#B8560F"          # Jupyter, same as chapters 09 and 10
SEL = "#2F7DE1"         # selected cell bar, like VS Code's focus color
NB = "pandas.ipynb"
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
        col = lambda l: RED if c.get("err") and re.match(r"[A-Za-z]+(Error|Interrupt)", l) else INK
        o.append("".join(p(f"margin-left:85px;padding:0 20px;font-family:{MONO};font-size:{fs}px;line-height:1.45;white-space:pre;color:{col(l)}", e(l) if l else "&#160;") for l in c["out"]))
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



# ---------- this deck ----------
EB1, EB2, EB3, EB4, EB5, EB6 = "1. 왜 필요한가", "2. NumPy 배열", "3. pandas 표 고르기", "4. 열 더하고 묶기", "5. 비교와 오류", "6. 실제 상황"
NEWK = " 6파트는 새 노트북이라 셀 번호가 [1]부터예요."
SH = ["편의점", "버스", "영화관", "분식집", "온라인쇼핑", "카페", "음원앱", "버스", "편의점", "웹툰", "온라인쇼핑", "분식집"]
CA = ["식비", "교통", "문화", "식비", "쇼핑", "식비", "문화", "교통", "식비", "문화", "쇼핑", "식비"]
AM = [3200, 1500, 15000, 6500, 32000, 4800, 10900, 1500, 2700, 3000, 18500, 7000]
DAY = [2, 3, 4, 5, 7, 9, 12, 14, 16, 19, 20, 25]
CATC = {"식비": (OR, K2BG), "교통": (BL, K1BG), "문화": (K4, K4BG), "쇼핑": (TEAL, K3BG)}
DATA = ['shops = ["편의점", "버스", "영화관", "분식집", "온라인쇼핑", "카페",', '         "음원앱", "버스", "편의점", "웹툰", "온라인쇼핑", "분식집"]',
        'categories = ["식비", "교통", "문화", "식비", "쇼핑", "식비",', '              "문화", "교통", "식비", "문화", "쇼핑", "식비"]',
        'amounts = [3200, 1500, 15000, 6500, 32000, 4800,', '           10900, 1500, 2700, 3000, 18500, 7000]']
FRAME = ["import pandas as pd", "", "spend = pd.DataFrame({", '    "day": [2, 3, 4, 5, 7, 9, 12, 14, 16, 19, 20, 25],', '    "shop": shops,', '    "category": categories,', '    "amount": amounts', "})", "spend"]
TB = "#F4F5F7"   # striped row, like VS Code's notebook table


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


SPEND_ROWS = [(DAY[i], SH[i], CA[i], AM[i]) for i in range(12)]
SW = [70, 170, 130, 120]   # day, shop, category, amount at fs 24


# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#F2B27A;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
       f'<h1{SLAM(1)} style="font-size:92px;font-weight:900;line-height:1.1;color:#F6F5F1">NumPy와<br>pandas 맛보기</h1>',
       '<p style="font-size:40px;line-height:1.4;color:#BFC6D4">숫자는 배열로,<br>가계부는 표로 한 번에 계산하기</p>']
cw_ = [80, 190, 150, 140]
cov.append(f'<div id="cov-card" style="position:absolute;left:1000px;top:250px;width:780px;height:580px;background:#FFFFFF;border-radius:24px;padding:40px 44px;display:flex;flex-direction:column;gap:22px">'
           + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{INK};white-space:pre", 'spend[spend["amount"] >= 10000]') + '</div>')
cov.append(df("cov-df", 1044, 340, ["day", "shop", "category", "amount"], [SPEND_ROWS[i] for i in (2, 4, 6, 10)], cw_, fs=28, rh=58, idx=[2, 4, 6, 10], iw=70))
cov.append(p(f"position:absolute;left:1044px;top:680px;width:700px;font-size:26px;line-height:1.5;color:{SUB}", "1만 원 넘게 쓴 날만 골라낸 표예요.<br>다섯 줄 for 문이 한 줄이 돼요."))
cov.append(shine(2, "cov-card"))
W("cover", cov, "오늘은 머신러닝 기초를 배우기 전에 데이터를 다루는 두 도구를 맛봐요. NumPy는 숫자 묶음을 칸마다 한 번에 계산하고, pandas는 엑셀처럼 열 이름이 붙은 표를 만들어 고르고 묶어요. 한 달 지출 기록 12줄로 합계, 평균, 1만 원 넘는 지출, 분류별 합계를 구해요. 오른쪽 표처럼 for 문 다섯 줄이 한 줄로 바뀌는 장면을 계속 봐요.", ("intro", "들어가기"))
ORDER.append("toc")

# ---------- setup ----------
o = [sec("setup")] + head("들어가기", "ml-basics 프로젝트에 numpy와 pandas를 넣어요", JP)
TL = [("$", "uv init ml-basics"), ("o", "Initialized project `ml-basics` at `…/ml-basics`"), ("$", "cd ml-basics"), ("$", "uv add numpy pandas"),
      ("o", "…"), ("o", " + numpy==2.5.5"), ("o", " + pandas==3.1.1"), ("o", " + python-dateutil==4.0.0"), ("o", " + tzdata==2026.6"),
      ("$", "uv add --dev ipykernel"), ("o", "…"), ("o", " + ipykernel==7.4.0")]
TT_, TW_ = 214, 1040
FT = 29
o.append(term(96, TT_, TW_, TL, FT, tid="t-setup"))
LHt = FT * 1.55
o.append(box(1, 96 + 34 - 10, TT_ + 26 + 5 * LHt - 4, FT * 0.6 * 17 + 20, 2 * LHt + 8, "#F2C46D", 4, 10))
o.append(tag(96 + 34 + FT * 0.6 * 17 + 40, TT_ + 26 + 6 * LHt, "pandas 안에서 숫자 계산은 numpy가 맡아요", "#B26A00", 1, 26))
o.append(box(2, 96 + 34 - 10, TT_ + 26 + 11 * LHt - 4, FT * 0.6 * 20 + 20, LHt + 8, "#9FD6F2", 4, 10))
o.append(tag(96 + 34 + FT * 0.6 * 20 + 40, TT_ + 26 + 11.5 * LHt, "노트북 커널 (10)", BL, 2, 26))
steps_ = [p(f"font-size:30px;color:{INK}", "VS Code로 ml-basics 폴더 열기"),
          p(f"font-size:30px;color:{INK}", "새 파일") + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{JP}", NB) + p(f"font-size:30px;color:{INK}", "만들기"),
          p(f"font-size:30px;color:{INK}", "오른쪽 위 커널에서 .venv 고르기"),
          p(f"font-size:30px;color:{INK}", "셀에 적고") + kbd("Shift+Enter", 24) + p(f"font-size:30px;color:{INK}", "로 실행")]
o.append(p(f"position:absolute;left:1180px;top:226px;font-size:32px;font-weight:700;color:{JP}", "노트북 열기 (10)", rise(3)))
for i, inner in enumerate(steps_):
    o.append(f'<div data-build-in="rise order 3"{DELAY(90 + i * 90)} style="position:absolute;left:1180px;top:{300 + i * 128}px;width:660px;height:110px;display:flex;flex-direction:row;flex-wrap:wrap;align-items:center;gap:14px;border-bottom:2px solid {LINE}">' + num(i + 1, JP, 34) + inner + '</div>')
o.append(caption("pip install은 쓰지 않아요. 09처럼 uv add로 넣어요.", 880, 4))
W("setup", o, "09에서 배운 uv로 새 프로젝트 ml-basics를 만들고 numpy와 pandas를 넣어요. uv add 한 줄에 패키지 두 개를 띄어 적으면 같이 들어가요. pandas는 안에서 numpy로 숫자를 계산해서, pandas만 적어도 numpy가 따라 들어와요. 오늘은 numpy도 직접 쓰니까 이름을 같이 적었어요. 노트북을 쓰려고 10처럼 ipykernel을 dev로 넣고, VS Code에서 pandas.ipynb를 만든 뒤 커널을 .venv로 골라요. 출력 가운데 줄은 줄였어요. 버전 숫자는 실행한 날에 따라 달라요." + REAL)

# ---------- part 1 ----------
o = [sec("why")] + head(EB1, "리스트로는 식비 합계 하나에 다섯 줄을 써요", K1)
T1 = 200
CFS[0] = 22
o += cell({"id": "c-w1", "lines": DATA, "n": 1}, 96, T1, 990)
o.append(tag(1116, ly(T1, 2) + LH() / 2, "같은 번호끼리 한 번의 지출이에요", GRAY, None, 28))
CFS[0] = 30
T2 = int(cbot(T1, 6) - 7 * 0 + 24) if False else 438
CFS[0] = 22
T2 = int(T1 + 20 + 6 * LH() + 28)
CFS[0] = 30
LOOP = ["food = 0", "for i in range(len(amounts)):", '    if categories[i] == "식비":', "        food = food + amounts[i]", "print(food)"]
o += cell({"id": "c-w2", "lines": LOOP, "n": 2, "out": ["24200"]}, 96, T2, 1000, sel="c-w2")
o.append(hl(96, T2, 1000, 1, 3, "mark", 1))
o.append(tag(1126, ly(T2, 2), "i번째 분류와 i번째 금액을 맞춰 읽어요 (18)", BL, 1, 28))
o.append(p(f"position:absolute;left:1126px;top:{ly(T2, 3) + 34:.0f}px;width:700px;font-size:24px;line-height:1.5;color:{GRAY}", "수업 코드의 zip(categories, amounts)도<br>같은 일을 해요. zip은 안 배워서 읽기만 해요.", fade(2)))
SY = 830
o.append(label(96, SY - 52, "4파트에서 배울 pandas 한 줄", GRAY, 28, rise(3)))
o.append(strip(96, SY, 1728, 150, [seg([("spend.groupby(", W_), ('"category"', CK), (")[", W_), ('"amount"', CV), ("].sum()", W_)], 36)], rise(3), 48))
for k, (c, v) in enumerate([("교통", "3000"), ("문화", "28900"), ("쇼핑", "50500"), ("식비", "24200")]):
    o.append(p(f"position:absolute;left:{1130 + k * 172}px;top:{SY + 30}px;width:160px;height:90px;border-radius:12px;background:#323946;display:flex;flex-direction:column;align-items:center;justify-content:center;font-size:24px;font-weight:700;color:#BFC6D4;line-height:1.25;text-align:center",
               f'{e(c)}<br><span style="font-family:{MONO};font-size:28px;color:{"#B8E8BE" if c == "식비" else "#F2F4F8"}">{v}</span>', rise(4)))
W("why", o, "리스트로 식비만 더하려면 for, if, 번호까지 다섯 줄이 필요해요. 지출 12번을 가게, 분류, 금액 리스트 세 개에 나눠 담았어요. 같은 번호끼리 한 번의 지출이에요. 18의 range(len())로 번호 i를 돌면서 i번째 분류가 식비일 때만 i번째 금액을 더해요. 수업 코드는 zip으로 두 리스트를 짝지어 꺼냈는데, zip은 아직 배우지 않아서 참고로만 봐요. 아래 줄은 4파트에서 배울 pandas 한 줄이에요. 분류 네 개의 합계가 한 번에 나와요. 숫자 묶음은 NumPy, 표는 pandas로 이렇게 짧게 써요." + REAL, ("p1", "왜 필요한가"))

o = [sec("big")] + head(EB1, "리스트에서 배열로, 배열에서 표로 가요", K1)
SX = [96, 556, 1016, 1476]
YT = 300
o.append(label(SX[0], YT, "파이썬 리스트", INK, 34, rise(1)))
o.append(label(SX[0], YT + 50, "13에서 배운 그 리스트", GRAY, 26, rise(1)))
for k, v in enumerate(["3200", "1500", "15000"]):
    o.append(vbox(SX[0], YT + 120 + k * 100, 300, 84, v, GRAY, "#F1F0EC", 34, rise(1) + DELAY(k * 80)))
o.append(arrow(70, "#C9CED8", WIPE(2), f"position:absolute;left:{SX[0] + 360}px;top:{YT + 250}px"))
o.append(label(SX[1], YT, "NumPy 배열", BL, 34, rise(2)))
o.append(label(SX[1], YT + 50, "숫자 칸을 한 번에 계산", GRAY, 26, rise(2)))
o.append(f'<div data-build-in="rise order 2" style="position:absolute;left:{SX[1]}px;top:{YT + 120}px;width:300px;height:284px;border-radius:14px;border:3px solid {BL};background:{K1BG};display:flex;flex-direction:column">'
         + "".join(p(f"height:{94 if k < 2 else 90}px;flex:none;{'border-bottom:2px solid #9BB6E0;' if k < 2 else ''}font-family:{MONO};font-size:34px;font-weight:700;line-height:{94 if k < 2 else 90}px;text-align:center;color:{INK}", v) for k, v in enumerate(["3200", "1500", "15000"])) + '</div>')
o.append(p(f"position:absolute;left:{SX[1]}px;top:{YT + 420}px;width:300px;text-align:center;font-family:{MONO};font-size:30px;font-weight:700;color:{BL}", "* 2  .sum()", fade(2)))
o.append(arrow(70, "#C9CED8", WIPE(3), f"position:absolute;left:{SX[1] + 360}px;top:{YT + 250}px"))
o.append(label(SX[2], YT, "pandas DataFrame", K4, 34, rise(3)))
o.append(label(SX[2], YT + 50, "열 이름이 붙은 표", GRAY, 26, rise(3)))
o.append(df("big-df", SX[2] - 10, YT + 120, ["shop", "amount"], [(SH[i], AM[i]) for i in range(3)], [150, 120], fs=26, rh=64, iw=40, attrs=rise(3)))
o.append(p(f"position:absolute;left:{SX[2]}px;top:{YT + 420}px;width:340px;font-size:26px;line-height:1.45;color:{K4}", "숫자 열 하나하나는<br>NumPy 배열이에요", fade(3)))
o.append(arrow(70, "#C9CED8", WIPE(4), f"position:absolute;left:{SX[2] + 360}px;top:{YT + 250}px"))
o.append(label(SX[3], YT, "머신러닝", GRAY, 34, rise(4)))
o.append(label(SX[3], YT + 50, "다음 강의", GRAY, 26, rise(4)))
o.append(p(f"position:absolute;left:{SX[3]}px;top:{YT + 120}px;width:330px;height:284px;border-radius:14px;border:3px dashed #C9CED8;display:flex;align-items:center;justify-content:center;text-align:center;font-size:28px;line-height:1.5;color:{SUB}", "표를 넣으면<br>규칙을 배워서<br>값을 맞히는 모델", rise(4)))
o.append(caption("32~43의 SQL 표와 같은 모양이라, 고르고 묶는 생각도 같아요.", 900, 5))
W("big", o, "오늘 쓰는 세 가지는 한 줄로 이어져요. 13의 리스트는 아무 값이나 담는 상자예요. NumPy 배열은 숫자만 담는 대신 곱하기와 합계를 모든 칸에 한 번에 해요. pandas DataFrame은 배열 여러 개에 열 이름을 붙여 옆으로 세운 표예요. 숫자 열 하나하나가 NumPy 배열이라 pandas도 같은 계산을 해요. 머신러닝 수업에서는 이 표를 모델에 넣어요. 표 모양은 32부터 본 SQL 표와 같아서, WHERE로 고르고 GROUP BY로 묶던 생각을 그대로 써요.")

o = [sec("min")] + head(EB1, "가장 짧은 NumPy: 배열에 2를 곱하기", K1)
T = 210
CFS[0] = 34
MN = ["import numpy as np", "", "print(np.array([3200, 1500, 15000]) * 2)"]
o += cell({"id": "c-min", "lines": MN, "n": 4, "out": ["[ 6400  3000 30000]"]}, 96, T, 1728, sel="c-min")
o.append(tag(cx(96, MN[0]) + 40, ly(T, 0), "import 모듈 as 별명 (28). 다들 np로 불러요", GRAY, 1, 28))
o.append(underline(2, cx(96, "print("), cx(96, "print(np.array([3200, 1500, 15000])"), ly(T, 2) + LH() / 2 - 4, BL, 5))
o.append(tag(cx(96, MN[2]) + 40, ly(T, 2), "리스트를 배열로 바꿔요", BL, 2, 28))
BY = 540
o += boxes(["3200", "1500", "15000"], 96, BY, 220, 150, GRAY, "#F1F0EC", True, 52, 20, ids=["mn-a", "mn-b", "mn-c"])
o.append(p(f"position:absolute;left:836px;top:{BY + 30}px;width:248px;text-align:center;font-family:{MONO};font-size:40px;font-weight:700;color:{BL}", "* 2", fade(3)))
o.append(arrow(200, BL, fade(3), f"position:absolute;left:860px;top:{BY + 90}px"))
o += boxes(["6400", "3000", "30000"], 1124, BY, 220, 150, BL, K1BG, True, 52, 20, attrs=[fly(3, "mn-a"), fly(3, "mn-b", DELAY(120)), fly(3, "mn-c", DELAY(240))])
o.append(caption("for 없이 칸마다 2를 곱했어요. 출력에는 쉼표가 없어요.", 800, 4))
W("min", o, "np.array로 리스트를 배열로 바꾸면 곱하기 한 번이 모든 칸에 들어가요. 28에서 배운 import 모듈 as 별명으로 numpy를 np라고 불러요. np는 거의 모든 코드가 쓰는 별명이라 그대로 따라 써요. 3200, 1500, 15000이 6400, 3000, 30000이 됐어요. 배열을 print하면 쉼표 없이 띄어쓰기로 칸을 나눠요. 리스트와 구별하는 표시예요." + REAL)

# ---------- part 2 ----------
o = [sec("n-list")] + head(EB2, "리스트 * 2는 이어 붙이고, 배열 * 2는 칸마다 곱해요", K2)
T, FW = 206, 1728
CFS[0] = 34
NL = ["prices = [3200, 1500, 15000]", "print(prices * 2)", "print(np.array(prices) * 2)"]
o += cell({"id": "c-nl", "lines": NL, "n": 5, "out": ["[3200, 1500, 15000, 3200, 1500, 15000]", "[ 6400  3000 30000]"]}, 96, T, FW, sel="c-nl")
CB = (96 + 87, T, FW - 87, 10 + 3 * LH() + 8)
o.append(lspot(1, *CB, T + 10 + 1 * LH(), LH(), bar=GRAY))
o.append(tag(cx(96, "[3200, 1500, 15000, 3200, 1500, 15000]", True) + 30, oy(T, 3, 0), "리스트 * 2의 결과", GRAY, 1, 28))
o.append(tag(cx(96, "[3200, 1500, 15000, 3200, 1500, 15000]", True) + 30, oy(T, 3, 1), "배열 * 2의 결과", BL, 2, 28))
o.append(lspot(2, *CB, T + 10 + 2 * LH(), LH(), bar=BL))
o.append(lspot_off(3))
RY = 640
o.append(label(96, RY - 50, "리스트 * 2", GRAY, 30, rise(1)))
o += boxes(["3200", "1500", "15000", "3200", "1500", "15000"], 96, RY, 150, 90, GRAY, "#F1F0EC", True, 30, 10, attrs=[rise(1)] * 3 + [rise(1) + DELAY(200)] * 3)
o.append(tag(96 + 6 * 160 + 10, RY + 45, "개수가 두 배 (13)", GRAY, 1, 28))
o.append(label(96, RY + 140, "배열 * 2", BL, 30, rise(2)))
o += boxes(["6400", "3000", "30000"], 96, RY + 190, 150, 90, BL, K1BG, True, 30, 10, attrs=[rise(2)] * 3)
o.append(tag(96 + 3 * 160 + 10, RY + 235, "개수는 그대로, 값이 두 배", BL, 2, 28))
W("n-list", o, "같은 * 2인데 리스트는 이어 붙이고 배열은 칸마다 곱해요. 13에서 리스트에 * 2를 하면 같은 리스트를 두 번 이어 붙인다고 배웠어요. 그래서 값이 여섯 개가 돼요. 배열에 * 2를 하면 개수는 세 개 그대로이고 값마다 2를 곱해요. 금액을 한꺼번에 바꿀 때는 배열이 맞아요. 수업 코드 첫 셀의 amounts * 2가 바로 이 리스트 쪽 결과였어요." + REAL, ("p2", "NumPy 배열"))

o = [sec("n-plus")] + head(EB2, "리스트에 숫자를 더하면 오류, 배열은 칸마다 더해요", K2)
T = 206
CFS[0] = 32
o += cell({"id": "c-np1", "lines": ["print(prices + 500)"], "n": 6, "out": ['TypeError: can only concatenate list (not "int") to list'], "err": True}, 96, T, 1728)
o += cell({"id": "c-np2", "lines": ["print(np.array(prices) + 500)"], "n": 7, "out": ["[ 3700  2000 15500]"]}, 96, T + 160, 1728, sel="c-np2")
o.append(underline(1, cx(96, "", True), cx(96, "TypeError: can only concatenate list", True), oy(T, 1, 0) + LH() / 2 - 2, RED, 5))
o.append(tag(cx(96, 'TypeError: can only concatenate list (not "int") to list', True) + 30, oy(T, 1, 0), "리스트 +는 리스트끼리만", RED, 1, 26))
BY = 600
o += boxes(["3200", "1500", "15000"], 96, BY, 220, 130, GRAY, "#F1F0EC", True, 46, 20, ids=["np-a", "np-b", "np-c"], attrs=[fade(2)] * 3)
for k in range(3):
    o.append(p(f"position:absolute;left:{96 + k * 240}px;top:{BY + 150}px;width:220px;text-align:center;font-family:{MONO};font-size:32px;font-weight:700;color:{GR}", "+ 500", fade(3)))
o.append(arrow(160, GR, fade(3), f"position:absolute;left:{96 + 3 * 240 + 40}px;top:{BY + 50}px"))
o += boxes(["3700", "2000", "15500"], 1124, BY, 220, 130, GR, GRBG, True, 46, 20, attrs=[fly(4, "np-a"), fly(4, "np-b", DELAY(120)), fly(4, "np-c", DELAY(240))])
o.append(caption("배열은 +, -, *, /, //를 모두 칸마다 계산해요.", 900, 5))
W("n-plus", o, "리스트에 숫자를 더하면 TypeError, 배열에 더하면 칸마다 더해져요. 13에서 리스트의 +는 리스트끼리 이어 붙이는 기호라고 했어요. 그래서 리스트와 숫자 500은 이어 붙일 수 없다는 오류가 나요. 배열은 + 500을 모든 칸에 해서 3700, 2000, 15500이 나와요. 빼기, 나누기, 몫 나누기도 같아요. 리스트로 하려면 23의 컴프리헨션을 써야 했던 일이에요." + REAL)

o = [sec("n-stats")] + head(EB2, "합계, 평균, 최소, 최대를 배열에 바로 물어요", K2)
T = 200
CFS[0] = 28
o += cell({"id": "c-ns1", "lines": ["arr = np.array(amounts)", "print(arr)"], "n": 8, "out": ["[ 3200  1500 15000  6500 32000  4800 10900  1500  2700  3000 18500  7000]"]}, 96, T, 1728)
T2 = 430
CFS[0] = 32
ST = ['print("합계:", arr.sum())', 'print("평균:", round(arr.mean()))', 'print("최소:", arr.min())', 'print("최대:", arr.max())']
SO = ["합계: 106600", "평균: 8883", "최소: 1500", "최대: 32000"]
o += cell({"id": "c-ns2", "lines": ST, "n": 9, "out": SO}, 96, T2, 1728, sel="c-ns2")
o = [re.sub(r'<p( style="[^"]*">합계: 106600</p>)', lambda m: "<p" + COUNT(1) + m.group(1), x) for x in o]
o.append(tag(cx(96, ST[1]) + 40, ly(T2, 1), "round()로 반올림했어요", BL, 2, 28))
o.append(tag(cx(96, SO[0], True) + 40, oy(T2, 4, 0), "sum(amounts)와 같은 값", GR, 1, 28))
o.append(tag(cx(96, SO[1], True) + 40, oy(T2, 4, 1), "8883.33…을 반올림", BL, 2, 28))
o.append(tag(cx(96, SO[3], True) + 40, oy(T2, 4, 3), "13의 min(), max()처럼 물어요", K4, 3, 28))
W("n-stats", o, "배열 뒤에 점을 찍고 sum, mean, min, max를 부르면 합계, 평균, 최소, 최대가 나와요. 지출 12개를 배열 arr로 만들었어요. 13에서 리스트는 sum(amounts)처럼 함수에 넣었는데, 배열은 arr.sum()처럼 배열에게 물어요. 평균은 8883.33…이라 round로 반올림해서 8883이에요. 수업 코드에서는 평균 줄의 이름표가 합계로 적혀 있어서 평균으로 고쳤어요. 리스트에는 mean이 없어서 오류가 나요. 5파트에서 봐요." + REAL)

o = [sec("n-shape")] + head(EB2, "shape는 칸 수, dtype은 칸에 든 값의 종류예요", K2)
T = 206
CFS[0] = 34
o += cell({"id": "c-nsh", "lines": ['print("모양:", arr.shape)', 'print("타입:", arr.dtype)'], "n": 11, "out": ["모양: (12,)", "타입: int64"]}, 96, T, 1728, sel="c-nsh")
BY = 640
for k, v in enumerate(AM):
    o.append(vbox(96 + k * 144, BY, 132, 84, str(v), K2, K2BG, 26, rise(1) + DELAY(k * 40)))
    o.append(p(f"position:absolute;left:{96 + k * 144}px;top:{BY + 96}px;width:132px;text-align:center;font-family:{MONO};font-size:24px;color:{GRAY}", str(k), fade(1)))
o.append(f'<div data-build-in="fade order 2" style="position:absolute;left:96px;top:{BY - 40}px;width:{12 * 144 - 12}px;height:20px;border:3px solid {K2};border-bottom:none;border-radius:10px 10px 0 0"></div>')
o.append(p(f"position:absolute;left:96px;top:{BY - 100}px;width:{12 * 144 - 12}px;text-align:center;font-size:30px;font-weight:700;color:{K2}", "12칸이 한 줄 → (12,)", fade(2)))
o.append(tag(cx(96, "타입: int64", True) + 40, oy(T, 2, 1), "모든 칸이 정수(integer)예요", OR, 3, 28))
o.append(caption("배열은 한 가지 종류만 담아서 계산이 빨라요.", 900, 4))
W("n-shape", o, "shape는 배열이 몇 칸인지, dtype은 칸에 무엇이 들었는지 알려 줘요. (12,)는 한 줄에 12칸이라는 뜻이에요. 쉼표 하나짜리 튜플이라 괄호 안이 한 칸뿐이에요. int64는 64비트 정수라는 이름이에요. 배열은 모든 칸이 같은 종류여서 계산을 한꺼번에 빨리 해요. 3파트의 표에도 shape가 있어서 행과 열 수를 알려 줘요." + REAL)

o = [sec("n-mask")] + head(EB2, "배열에 비교를 하면 칸마다 True, False가 나와요", K2)
T = 206
CFS[0] = 30
o += cell({"id": "c-nm", "lines": ["print(arr >= 10000)"], "n": 12, "out": ["[False False  True False  True False  True False False False  True False]"]}, 96, T, 1728, sel="c-nm")
BY = 440
for k, v in enumerate(AM):
    big = v >= 10000
    o.append(vbox(96 + k * 144, BY, 132, 84, str(v), K2 if big else "#C9CED8", K2BG if big else CARD, 26, rise(1) + DELAY(k * 40)))
    o.append(f'<div data-build-in="rise order 2"{DELAY(k * 50)} style="position:absolute;left:{96 + k * 144}px;top:{BY + 120}px;width:132px;display:flex;justify-content:center">{tf("True" if big else "False", 22)}</div>')
o.append(label(96, BY - 50, "arr", GRAY, 28, fade(1), True))
o.append(label(96, BY + 190, ">= 10000 ?", GRAY, 28, fade(2), True))
o.append(caption("이 True, False 배열을 대괄호에 넣으면 고르기가 돼요.", 780, 3))
W("n-mask", o, "배열에 >= 10000 같은 비교를 하면 칸마다 True나 False가 담긴 배열이 나와요. 12의 비교 연산이 값 하나에 True, False를 냈다면, 배열은 12칸에 한 번씩 물어요. 15000, 32000, 10900, 18500 네 칸만 True예요. 출력의 True 앞 띄어쓰기는 False와 자리를 맞추려고 넣은 거예요. 다음 장에서 이 배열로 값을 골라요." + REAL)

o = [sec("n-filter")] + head(EB2, "배열[조건]은 True 자리의 값만 남겨요", K2)
T = 206
CFS[0] = 36
o += cell({"id": "c-nf", "lines": ["print(arr[arr >= 10000])"], "n": 13, "out": ["[15000 32000 10900 18500]"]}, 96, T, 1728, sel="c-nf")
o.append(underline(1, cx(96, "print(arr["), cx(96, "print(arr[arr >= 10000"), ly(T, 0) + LH() / 2 - 2, OR, 6))
o.append(tag(cx(96, "print(arr[arr >= 10000])") + 40, ly(T, 0), "대괄호 안에 조건", OR, 1, 28))
BY = 430
src = {}
for k, v in enumerate(AM):
    big = v >= 10000
    if big:
        src[v] = f"nf-{k}"
    o.append(vbox(96 + k * 144, BY, 132, 84, str(v), K2 if big else "#C9CED8", K2BG if big else CARD, 26, f' id="nf-{k}"'))
    o.append(f'<div style="position:absolute;left:{96 + k * 144}px;top:{BY + 104}px;width:132px;display:flex;justify-content:center">{tf("True" if big else "False", 22)}</div>')
picked = [v for v in AM if v >= 10000]
for k, v in enumerate(picked):
    o.append(vbox(96 + k * 220, BY + 260, 200, 110, str(v), GR, GRBG, 38, fly(2, src[v], DELAY(k * 120))))
o.append(tag(96 + 4 * 220 + 20, BY + 315, "False 자리는 빠져요", GR, 3, 30))
o.append(caption("23의 [a for a in amounts if a >= 10000]와 같은 값이에요.", 920, 3))
W("n-filter", o, "배열 대괄호 안에 조건을 넣으면 True 자리의 값만 남은 새 배열이 나와요. 안쪽 arr >= 10000이 먼저 True, False 배열이 되고, 바깥 arr가 그 배열로 칸을 골라요. 그래서 네 값만 아래로 내려왔어요. 23의 컴프리헨션에서 뒤에 if를 붙여 고르던 일과 결과가 같아요. 3파트의 pandas 표에서도 똑같이 표[조건]으로 행을 골라요." + REAL)

# ---------- part 3 ----------
o = [sec("d-make")] + head(EB3, "딕셔너리로 DataFrame을 만들면 키가 열 이름이 돼요", K3)
T = 200
CFS[0] = 28
o += cell({"id": "c-dm", "lines": FRAME, "n": 14}, 96, T, 1044, sel="c-dm")
TX0, TY0, RH = 1190, 200, 50
o.append(df("dm-df", TX0, TY0, ["day", "shop", "category", "amount"], SPEND_ROWS, SW, fs=24, rh=RH, iw=50, attrs=rise(1)))
o.append(tint(2, cx(96, "    ") - 4, ly(T, 3) - LH() / 2, tw('"day"') + 6, LH(), K3))
o.append(box(2, dfx(TX0, 50, SW, 0), TY0 - 2, sum(SW) + 24, RH + 2, K3, 4, 8))
o.append(tag(96 + 87 + 20, cbot(T, 9) + 50, "키 → 열 이름, 값 리스트 → 그 열의 12칸", K3, 2, 28, lead=False))
o.append(box(3, TX0 - 6, dfy(TY0, RH, 0), 64, 12 * RH, OR, 4, 8))
o.append(tag(96 + 87 + 20, cbot(T, 9) + 110, "왼쪽 0~11은 pandas가 붙인 행 번호(index)", OR, 3, 28, lead=False))
o.append(tag(cx(96, "spend") + 30, ly(T, 8), "마지막 줄 이름은 표로 보여 줘요 (10)", GRAY, 4, 26))
W("d-make", o, "pd.DataFrame에 딕셔너리를 넣으면 키가 열 이름, 값 리스트가 그 열의 칸이 돼요. 15에서 배운 딕셔너리 모양 그대로예요. day, shop, category, amount 네 키가 위쪽 머리글이 됐어요. 리스트 길이가 모두 12라서 행도 12개예요. 길이가 다르면 오류가 나요. 왼쪽 0부터 11은 pandas가 붙인 행 번호이고 index라고 불러요. 셀 마지막 줄에 spend만 적으면 VS Code가 표로 그려 줘요. 수업 코드는 shops와 categories를 두 번 적었는데 한 번만 적어도 돼요." + REAL, ("p3", "pandas 표 고르기"))

o = [sec("d-look")] + head(EB3, "shape로 크기를, head로 앞 몇 줄만 봐요", K3)
T = 210
CFS[0] = 36
o += cell({"id": "c-dl1", "lines": ["spend.shape"], "n": 15, "out": ["(12, 4)"]}, 96, T, 860)
o.append(tag(cx(96, "(12, 4)", True) + 40, oy(T, 1, 0), "행 12개, 열 4개", K3, 1, 30))
T2 = 470
o += cell({"id": "c-dl2", "lines": ["spend.head(3)"], "n": 16}, 96, T2, 860, sel="c-dl2")
o.append(df("dl-df", 96 + 85, cbot(T2, 1) + 16, ["day", "shop", "category", "amount"], SPEND_ROWS[:3], [90, 190, 170, 150], fs=32, rh=66, iw=60, attrs=rise(2)))
o.append(tag(cx(96, "spend.head(3)") + 40, ly(T2, 0), "괄호를 비우면 다섯 줄", GRAY, 2, 28))
o.append(p(f"position:absolute;left:1100px;top:226px;width:724px;font-size:30px;font-weight:700;color:{K3}", "수업 코드의 주석", fade(3)))
o.append(strip(1100, 290, 724, 300, [seg([("# spend.shape", "#9AA1AE")], 34), seg([("# spend.head(5)", "#9AA1AE")], 34), seg([("# spend.info()", "#9AA1AE")], 34)], fade(3), 48))
o.append(p(f"position:absolute;left:1100px;top:620px;width:724px;font-size:28px;line-height:1.55;color:{SUB}", "#를 지우고 한 줄씩 실행해 봐요.<br>info()는 열마다 이름, 빈칸 수, 타입을 보여 줘요.", fade(3)))
W("d-look", o, "표를 받으면 shape로 크기부터, head로 앞 몇 줄부터 봐요. shape는 괄호 없이 적고 (행, 열)이 나와요. 2파트 배열의 shape와 같은 이름이에요. head(3)는 위에서 세 줄만 보여 줘요. 데이터가 수천 줄이어도 앞만 보고 모양을 알 수 있어요. 수업 코드에 주석으로 남긴 info()는 열마다 타입을 줄글로 알려 줘요. 직접 지워 가며 실행해 봐요." + REAL)

o = [sec("d-col")] + head(EB3, "열 이름 하나를 대괄호에 넣으면 그 열만 나와요", K3)
T = 200
CFS[0] = 24
SER = ["0      3200", "1      1500", "2     15000", "3      6500", "4     32000", "5      4800", "6     10900", "7      1500", "8      2700", "9      3000", "10    18500", "11     7000", "Name: amount, dtype: int64"]
o += cell({"id": "c-dc1", "lines": ['spend["amount"]'], "n": 17, "out": SER}, 96, T, 640, sel="c-dc1")
o.append(box(1, cx(96, "", True) - 12, oy(T, 1, 0) - LH() / 2 - 4, tw("10   ") + 4, oy(T, 1, 11) - oy(T, 1, 0) + LH() + 8, OR, 4, 8))
o.append(tag(cx(96, "11     7000", True) + 40, oy(T, 1, 2), "왼쪽은 행 번호, 오른쪽은 값", OR, 1, 26, lead=False))
o.append(tag(cx(96, SER[-1], True) + 30, oy(T, 1, 12), "열 이름과 타입", GRAY, 2, 26))
o.append(p(f"position:absolute;left:440px;top:{oy(T, 1, 5) - 20:.0f}px;width:330px;font-size:28px;line-height:1.5;font-weight:700;color:{K3}", "번호가 붙은 한 줄짜리를<br>Series라고 불러요", fade(2)))
T2 = 260
CFS[0] = 22
o += cell({"id": "c-dc2", "lines": ['print("합계:", spend["amount"].sum())', 'print("평균:", round(spend["amount"].mean(), 2))'], "n": 18, "out": ["합계: 106600", "평균: 8883.33"]}, 950, T2, 874)
o.append(tag(950 + 105, cbot(T2, 2) + 150, "2파트 배열과 같은 sum, mean", BL, 3, 28, lead=False))
o.append(tag(950 + 105, cbot(T2, 2) + 200, "round(값, 2)는 소수 둘째 자리까지", GRAY, 3, 26, lead=False))
W("d-col", o, "spend 뒤 대괄호에 열 이름을 넣으면 그 열 하나만 꺼내요. 15에서 딕셔너리[키]로 값을 꺼내던 모양과 같아요. 나온 것은 왼쪽 행 번호와 오른쪽 값이 짝지어진 한 줄짜리이고, pandas는 이것을 Series라고 불러요. 맨 아래 Name과 dtype은 열 이름과 타입이에요. 열 안의 값은 NumPy 배열이라 sum과 mean을 그대로 써요. 평균은 round의 두 번째 칸에 2를 넣어 소수 둘째 자리까지 남겼어요. 수업 코드는 여기서도 평균 줄에 합계라고 적혀 있어서 고쳤어요." + REAL)

o = [sec("d-cols")] + head(EB3, "열 여러 개는 이름 리스트를 넣어서 대괄호가 두 겹이에요", K3)
T = 200
CFS[0] = 30
o += cell({"id": "c-dcs", "lines": ['spend[["shop", "amount"]]'], "n": 19}, 96, T, 860, sel="c-dcs")
o.append(df("dcs-df", 96 + 85, cbot(T, 1) + 12, ["shop", "amount"], [(SH[i], AM[i]) for i in range(12)], [200, 150], fs=24, rh=46, iw=50, attrs=rise(1)))
FS, X0 = 40, 1080 + 48
cw = FS * 0.6
o.append(strip(1080, 260, 744, 150, [seg([("spend", W_), ("[", "#F2C46D"), ('["shop", "amount"]', CF), ("]", "#F2C46D")], FS)], "", 48))
o.append(label(1080, 440, "바깥 [ ] : 열 고르기", OR, 30, fade(2)))
o.append(label(1080, 500, "안쪽 [ ] : 열 이름 리스트 (13)", TEAL, 30, fade(2)))
o.append(p(f"position:absolute;left:1080px;top:600px;width:744px;font-size:28px;line-height:1.6;color:{SUB}", f'한 겹 <span style="font-family:{MONO};font-weight:700;color:{INK}">spend["shop"]</span>은 Series,<br>두 겹 <span style="font-family:{MONO};font-weight:700;color:{INK}">spend[["shop"]]</span>은 열 하나짜리 표예요.', fade(3)))
o.append(p(f"position:absolute;left:1080px;top:760px;width:744px;font-size:28px;line-height:1.6;color:{RED}", "한 겹에 이름 두 개를 적으면 KeyError가 나요. 5파트에서 봐요.", fade(4)))
W("d-cols", o, "열을 여러 개 고르려면 열 이름 리스트를 대괄호에 넣어요. 안쪽 대괄호는 13의 리스트이고, 바깥 대괄호는 앞 장의 열 고르기예요. 그래서 대괄호가 두 겹이 돼요. 결과는 고른 열만 남은 표예요. 열 이름 하나라도 리스트로 넣으면 Series가 아니라 열 하나짜리 표가 나와요. 한 겹 안에 이름 두 개를 쉼표로 적으면 KeyError가 나요." + REAL)

o = [sec("d-cond")] + head(EB3, "열에 비교를 하면 행마다 True, False가 나와요", K3)
T = 200
CFS[0] = 24
CO = [f"{i:<2}    {'True' if CA[i] == '문화' else 'False':>5}" for i in range(12)] + ["Name: category, dtype: bool"]
CO = ["0     False", "1     False", "2      True", "3     False", "4     False", "5     False", "6      True", "7     False", "8     False", "9      True", "10    False", "11    False", "Name: category, dtype: bool"]
o += cell({"id": "c-dcd", "lines": ['spend["category"] == "문화"'], "n": 20, "out": CO}, 96, T, 700, sel="c-dcd")
XC = 900
o.append(label(XC, oy(T, 1, 0) - 70, "category 열과 나란히", GRAY, 26, fade(1)))
for i in range(12):
    y = oy(T, 1, i)
    hit = CA[i] == "문화"
    o.append(f'<div data-build-in="rise order 1"{DELAY(i * 40)} style="position:absolute;left:{XC}px;top:{y - 19:.0f}px;height:38px;display:flex;flex-direction:row;align-items:center;gap:18px">'
             + p(f"width:40px;text-align:right;font-family:{MONO};font-size:24px;color:{GRAY}", str(i)) + catchip(CA[i], 24) + '</div>')
    if hit:
        o.append(p(f"position:absolute;left:{XC + 170}px;top:{y - 19:.0f}px;height:38px;font-size:24px;font-weight:700;line-height:38px;color:{GR}", "← 문화라서 True", fade(2)))
o.append(box(2, cx(96, "", True) - 12, oy(T, 1, 2) - 21, tw("2      True") + 22, 42, GR, 4, 8))
o.append(box(2, cx(96, "", True) - 12, oy(T, 1, 6) - 21, tw("2      True") + 22, 42, GR, 4, 8))
o.append(box(2, cx(96, "", True) - 12, oy(T, 1, 9) - 21, tw("2      True") + 22, 42, GR, 4, 8))
o.append(p(f"position:absolute;left:1400px;top:{oy(T, 1, 3):.0f}px;width:424px;font-size:28px;line-height:1.55;color:{SUB}", "2파트 배열의 비교와 같아요. 이번엔 행 번호가 붙은 Series로 나와요.", fade(3)))
W("d-cond", o, "열에 == 같은 비교를 하면 행마다 True, False가 붙은 Series가 나와요. category 열을 문화와 하나씩 비교해서 2번, 6번, 9번 행만 True예요. 2파트의 arr >= 10000과 같은 일인데, 결과에 행 번호가 붙어 있다는 점만 달라요. 이 번호 덕분에 다음 장에서 표의 같은 번호 행을 골라요." + REAL)

o = [sec("d-filter")] + head(EB3, "표[조건]은 True인 행만 남겨요", K3)
T = 200
CFS[0] = 30
FL1 = 'spend[spend["category"] == "문화"]'
o += cell({"id": "c-df1", "lines": [FL1], "n": 21}, 96, T, 1728)
o.append(tint(1, cx(96, "spend[") - 3, ly(T, 0) - LH() / 2, tw('spend["category"] == "문화"') + 6, LH(), GR))
o.append(tag(cx(96, FL1) + 40, ly(T, 0), "앞 장의 True, False", GR, 1, 28))
DW = [80, 210, 150, 150]
o.append(df("df1-df", 96 + 85, cbot(T, 1) + 12, ["day", "shop", "category", "amount"], [SPEND_ROWS[i] for i in (2, 6, 9)], DW, fs=28, rh=54, idx=[2, 6, 9], iw=60, attrs=rise(1)))
T2 = 560
FL2 = 'spend[spend["amount"] >= 10000]'
o += cell({"id": "c-df2", "lines": [FL2], "n": 22}, 96, T2, 1728, sel="c-df2")
o.append(df("df2-df", 96 + 85, cbot(T2, 1) + 12, ["day", "shop", "category", "amount"], [SPEND_ROWS[i] for i in (2, 4, 6, 10)], DW, fs=28, rh=54, idx=[2, 4, 6, 10], iw=60, attrs=rise(2)))
o.append(box(3, 96 + 85 - 6, cbot(T2, 1) + 12 + 54, 72, 4 * 54 + 4, OR, 4, 8))
o.append(tag(96 + 85 + sum(DW) + 120, cbot(T2, 1) + 12 + 54 * 2.5, "행 번호는 원래 번호 그대로예요", OR, 3, 28))
W("d-filter", o, "표 대괄호 안에 True, False Series를 넣으면 True인 행만 남은 표가 나와요. 2파트 배열[조건]과 같은 모양이에요. 안쪽 비교가 먼저 행마다 True, False가 되고, 바깥 spend가 그 행만 골라요. 문화는 세 줄, 1만 원 이상은 네 줄이에요. 왼쪽 행 번호는 새로 매기지 않고 원래 번호를 그대로 들고 와요. 36의 WHERE와 같은 일이에요." + REAL)

o = [sec("d-and")] + head(EB3, "조건 두 개는 &로 잇고, 조건마다 괄호로 감싸요", K3)
T = 200
CFS[0] = 30
AN = 'spend[(spend["category"] == "식비") & (spend["amount"] >= 5000)]'
o += cell({"id": "c-da", "lines": [AN], "n": 23}, 96, T, 1728, sel="c-da")
p1s, p1e = "spend[", 'spend[(spend["category"] == "식비")'
p2s = 'spend[(spend["category"] == "식비") & '
o.append(tint(1, cx(96, p1s) - 3, ly(T, 0) - LH() / 2, tw('(spend["category"] == "식비")') + 6, LH(), OR))
o.append(tint(1, cx(96, p2s) - 3, ly(T, 0) - LH() / 2, tw('(spend["amount"] >= 5000)') + 6, LH(), BL))
o.append(underline(2, cx(96, p1e + " "), cx(96, p1e + " &"), ly(T, 0) + LH() / 2 + 6, GR, 6))
o.append(df("da-df", 96 + 85, cbot(T, 1) + 12, ["day", "shop", "category", "amount"], [SPEND_ROWS[i] for i in (3, 11)], [80, 190, 150, 150], fs=28, rh=54, idx=[3, 11], iw=60, attrs=rise(4)))
GY = 520
LBW = 250
o.append(label(96, GY + 64 - 18, "식비?", OR, 28, fade(3)))
o.append(label(96, GY + 128 - 18, "5000 이상?", BL, 28, fade(3)))
o.append(label(96, GY + 192 - 18, "& 둘 다", GR, 28, fade(3)))
for i in range(12):
    x = 96 + LBW + i * 122
    a, b = CA[i] == "식비", AM[i] >= 5000
    o.append(p(f"position:absolute;left:{x}px;top:{GY}px;width:110px;text-align:center;font-family:{MONO};font-size:24px;color:{GRAY}", str(i), fade(3)))
    for r, v in enumerate([a, b, a and b]):
        sty = f"position:absolute;left:{x}px;top:{GY + 64 * (r + 1) - 22}px;width:110px;display:flex;justify-content:center"
        o.append(f'<div data-build-in="fade order 3"{DELAY(i * 30)} style="{sty}">{tf("True" if v else "False", 20)}</div>')
o.append(box(4, 96 + LBW + 3 * 122 - 6, GY + 192 - 30, 122, 60, GR, 4, 10))
o.append(box(4, 96 + LBW + 11 * 122 - 6, GY + 192 - 30, 122, 60, GR, 4, 10))
o.append(caption("and를 쓰거나 괄호를 빼면 오류가 나요. 5파트에서 봐요.", 900, 5))
W("d-and", o, "조건이 두 개면 &로 잇고, 조건마다 괄호로 감싸요. 식비이면서 5000원 이상인 행을 골라요. 12의 and는 값 하나끼리만 비교해서 Series에는 쓸 수 없어요. 그래서 pandas는 행마다 둘 다 True인지 보는 &를 써요. 아래 그림처럼 같은 번호끼리 짝지어 둘 다 True인 3번, 11번만 남았어요. 괄호를 빼면 &가 먼저 계산돼서 오류가 나요. 또는은 |를 써요." + REAL)

o = [sec("d-sort")] + head(EB3, "sort_values로 금액이 큰 순서로 세워요", K3)
SO_ = 'spend.sort_values(by="amount", ascending=False).head(3)'
T = 200
CFS[0] = 36
o += cell({"id": "c-ds", "lines": [SO_], "n": 24}, 96, T, 1728, sel="c-ds")
UY = ly(T, 0) + LH() / 2 - 2
pre = "spend.sort_values("
for k, (sg, t, col, lc) in enumerate([('by="amount"', "기준 열", CF, LF), ("ascending=False", "큰 것부터", CK, OR), (".head(3)", "위에서 세 줄", CV, LV)]):
    x1 = cx(96, pre)
    o.append(underline(k + 1, x1, cx(96, pre + sg), UY, col, 6))
    o.append(label(x1, cbot(T, 1) + 18, t, lc, 30, fade(k + 1)))
    pre += sg + (", " if k == 0 else ")")
DT = cbot(T, 1) + 100
o.append(df("ds-df", 96 + 85, DT, ["day", "shop", "category", "amount"], [SPEND_ROWS[i] for i in (4, 10, 2)], [100, 260, 200, 200], fs=40, rh=92, idx=[4, 10, 2], iw=80, attrs=rise(4)))
o.append(p(f"position:absolute;left:1120px;top:{DT + 130}px;width:700px;font-size:30px;line-height:1.6;color:{SUB}", "22의 sorted(..., reverse=True)처럼<br>ascending=False가 큰 것부터 세워요.", fade(2)))
o.append(p(f"position:absolute;left:1120px;top:{DT + 270}px;width:700px;font-size:30px;font-weight:700;line-height:1.6;color:{GRAY}", "행 번호도 행을 따라 4, 10, 2 순서가 됐어요.", fade(4)))
W("d-sort", o, "sort_values의 by에 기준 열을 적으면 그 열 순서로 행을 세워요. ascending은 오름차순이라는 뜻이고, False를 넣으면 큰 것부터예요. 22에서 sorted에 reverse=True를 넣던 것과 같은 생각이에요. 뒤에 head(3)를 이어 붙여서 위에서 세 줄만 봤어요. 점으로 이어 쓰면 왼쪽부터 차례로 실행돼요. 행 번호가 행을 따라 움직여서 4, 10, 2 순서가 됐어요. 36의 ORDER BY amount DESC LIMIT 3과 같아요." + REAL)

# ---------- part 4 ----------
o = [sec("a-div")] + head(EB4, "/는 소수까지, //는 몫만 남겨요", K4)
T = 200
CFS[0] = 24
DV1 = ["0      32.0", "1      15.0", "2     150.0", "3      65.0", "4     320.0", "5      48.0", "6     109.0", "7      15.0", "8      27.0", "9      30.0", "10    185.0", "11     70.0", "Name: amount, dtype: float64"]
DV2 = ["0      32", "1      15", "2     150", "3      65", "4     320", "5      48", "6     109", "7      15", "8      27", "9      30", "10    185", "11     70", "Name: amount, dtype: int64"]
o += cell({"id": "c-dv1", "lines": ['spend["amount"] / 100'], "n": 25, "out": DV1}, 96, T, 820)
o += cell({"id": "c-dv2", "lines": ['spend["amount"] // 100'], "n": 26, "out": DV2}, 1004, T, 820, sel="c-dv2")
o.append(tint(1, cx(96, "Name: amount, dtype: ", True) - 3, oy(T, 1, 12) - 20, tw("float64") + 6, 40, GRAY))
o.append(tint(2, cx(1004, "Name: amount, dtype: ", True) - 3, oy(T, 1, 12) - 20, tw("int64") + 6, 40, K4))
o.append(tag(cx(96, "11     70.0", True) + 50, oy(T, 1, 1), "32.0처럼 소수점이 붙어요", GRAY, 1, 26))
o.append(tag(cx(1004, "11     70", True) + 50, oy(T, 1, 1), "정수 몫 (12)", K4, 2, 26))
o.append(caption("포인트는 정수라서 //로 100원마다 1점을 매겨요.", 950, 3))
W("a-div", o, "100원마다 1포인트를 주려고 금액을 100으로 나눠요. 12에서 배운 것처럼 /는 소수까지 계산해서 32.0처럼 점이 붙고 타입이 float64가 돼요. //는 몫만 남겨서 32이고 타입은 정수 int64예요. 3250원이었다면 /는 32.5, //는 32라서 차이가 더 잘 보여요. 포인트는 정수여야 하니 //를 써요. 열 전체에 나누기 한 번이 들어가는 건 2파트 배열과 같아요." + REAL, ("p4", "열 더하고 묶기"))

o = [sec("a-col")] + head(EB4, "없는 열 이름에 값을 넣으면 새 열이 생겨요", K4)
T = 200
CFS[0] = 32
AC = ['spend["point"] = spend["amount"] // 100', 'print(spend["point"].sum())', "spend.head(3)"]
o += cell({"id": "c-ac", "lines": AC, "n": 27, "out": ["1066"]}, 96, T, 1728, sel="c-ac")
o = [re.sub(r'<p( style="[^"]*">1066</p>)', lambda m: "<p" + COUNT(2) + m.group(1), x) for x in o]
o.append(hl(96, T, 1728, 0, 1, "mark", 1))
o.append(tag(cx(96, AC[0]) + 40, ly(T, 0), "15의 딕셔너리[새 키] = 값과 같은 모양", BL, 1, 28))
o.append(tag(cx(96, "1066", True) + 40, oy(T, 3, 0), "포인트 합계", GR, 2, 28))
AW = [100, 210, 180, 170, 150]
TY = oy(T, 3, 0) + 50
CSP = {(i, 4): f"color:{K4};font-weight:700" for i in range(3)}
o.append(df("ac-df", 96 + 85, TY, ["day", "shop", "category", "amount", "point"], [SPEND_ROWS[i] + (AM[i] // 100,) for i in range(3)], AW, fs=32, rh=68, iw=60, attrs=rise(3), cs=CSP))
o.append(box(3, dfx(96 + 85, 60, AW, 4) - 4, TY - 2, AW[4] + 20, 4 * 68 + 6, K4, 4, 10))
o.append(tag(dfx(96 + 85, 60, AW, 5) + 70, TY + 68 * 2.5, "맨 오른쪽에 point 열이 붙었어요", K4, 3, 28))
o.append(caption("이미 있는 열 이름에 넣으면 새로 만들지 않고 덮어써요.", 840, 4))
W("a-col", o, "spend[\"point\"]처럼 아직 없는 열 이름에 값을 넣으면 맨 오른쪽에 새 열이 생겨요. 15에서 딕셔너리[새 키] = 값으로 키를 더하던 모양과 같아요. 오른쪽 금액 // 100이 열 전체에 계산돼서 행마다 포인트가 들어가요. 새 열도 다른 열처럼 sum으로 합계를 내요. 이번 달 포인트는 1066점이에요. 이미 있는 이름에 넣으면 새로 만들지 않고 덮어써요." + REAL)

o = [sec("a-loc")] + head(EB4, "loc[행 번호, 열 이름]으로 칸 하나를 고쳐요", K4)
T = 200
CFS[0] = 30
LC1 = ['spend.loc[2, "amount"] = 14000', "spend.head(3)"]
LC2 = ['spend["point"] = spend["amount"] // 100', "spend.head(3)"]
o += cell({"id": "c-lc1", "lines": LC1, "n": 28}, 96, T, 860)
o += cell({"id": "c-lc2", "lines": LC2, "n": 29}, 984, T, 840, sel="c-lc2", attrs=rise(3))
LW = [76, 150, 140, 130, 100]
LR, LI = 64, 46
TY = cbot(T, 2) + 20
R2a = [SPEND_ROWS[0] + (32,), SPEND_ROWS[1] + (15,), (4, "영화관", "문화", 14000, 150)]
R2b = R2a[:2] + [(4, "영화관", "문화", 14000, 140)]
o.append(df("lc1-df", 96 + 85, TY, ["day", "shop", "category", "amount", "point"], R2a, LW, fs=30, rh=LR, iw=LI, attrs=rise(1), cs={(2, 3): f"color:{GR};font-weight:700", (2, 4): f"color:{RED};font-weight:700"}))
o.append(df("lc2-df", 984 + 85, TY, ["day", "shop", "category", "amount", "point"], R2b, LW, fs=30, rh=LR, iw=LI, attrs=rise(3), cs={(2, 3): f"color:{GR};font-weight:700", (2, 4): f"color:{GR};font-weight:700"}))
YR2 = dfy(TY, LR, 2)
o.append(box(1, dfx(96 + 85, LI, LW, 3) + 16, YR2 + 2, LW[3] - 6, LR - 4, GR, 4, 8))
o.append(box(2, dfx(96 + 85, LI, LW, 4) + 20, YR2 + 2, LW[4] - 12, LR - 4, RED, 4, 8))
o.append(p(f"position:absolute;left:{96 + 85}px;top:{YR2 + 110}px;width:760px;font-size:30px;line-height:1.55;font-weight:700;color:{RED}", "amount만 바뀌고 point는 150 그대로예요.", fade(2)))
o.append(p(f"position:absolute;left:{96 + 85}px;top:{YR2 + 160}px;width:760px;font-size:28px;line-height:1.55;color:{SUB}", "계산해서 만든 열은 저절로 바뀌지 않아요.", fade(2)))
o.append(box(4, dfx(984 + 85, LI, LW, 4) + 20, YR2 + 2, LW[4] - 12, LR - 4, GR, 4, 8))
o.append(p(f"position:absolute;left:{984 + 85}px;top:{YR2 + 110}px;width:740px;font-size:30px;line-height:1.55;font-weight:700;color:{GR}", "point 줄을 다시 실행하면 140이 돼요.", fade(4)))
o.append(caption("loc의 첫 칸은 왼쪽 행 번호, 둘째 칸은 열 이름이에요.", 860, 5))
W("a-loc", o, "loc 뒤 대괄호에 행 번호와 열 이름을 적고 값을 넣으면 그 칸 하나만 바뀌어요. 2번 행 영화관 금액을 15000에서 14000으로 고쳤어요. 그런데 point는 150 그대로예요. point는 만들 때 한 번 계산한 값이라 amount가 바뀌어도 따라 바뀌지 않아요. 수업 코드처럼 point 줄을 한 번 더 실행해야 140이 돼요. loc의 첫 칸은 0부터 센 순서가 아니라 왼쪽에 보이는 행 번호예요." + REAL)

o = [sec("a-group")] + head(EB4, "groupby로 분류마다 묶어서 합계를 내요", K4)
T = 256
CFS[0] = 30
GB = 'spend.groupby("category")["amount"].sum().sort_values(ascending=False)'
GO = ["category", "쇼핑    50500", "문화    27900", "식비    24200", "교통     3000", "Name: amount, dtype: int64"]
o += cell({"id": "c-gb", "lines": [GB], "n": 31, "out": GO}, 96, T, 1728, sel="c-gb")
segs_ = [("spend.groupby(", '"category"', ")", "① 묶고", K4), ('["amount"]', None, None, "② 열 고르고", TEAL), (".sum()", None, None, "③ 합계", GR), (".sort_values(ascending=False)", None, None, "④ 큰 순서로", OR)]
pre = ""
for k, (a, b, c, t, col) in enumerate(segs_):
    s = a + (b or "") + (c or "")
    o.append(underline(k + 1, cx(96, pre) + (tw("spend.") if k == 0 else 0), cx(96, pre + s), ly(T, 0) + LH() / 2 - 2, col, 5))
    o.append(label(cx(96, pre) + (tw("spend.") if k == 0 else 0), T - 44, t, col, 26, fade(k + 1)))
    pre += s
GBX, GBY = 730, 420
groups = [("쇼핑", [32000, 18500]), ("문화", [14000, 10900, 3000]), ("식비", [3200, 6500, 4800, 2700, 7000]), ("교통", [1500, 1500])]
for k, (c, vals) in enumerate(groups):
    col, bg = CATC[c]
    x = GBX + k * 274
    chips_ = "".join(p(f"font-family:{MONO};font-size:22px;font-weight:700;color:{INK};background:#FFFFFF;border-radius:8px;padding:2px 10px", str(v)) for v in vals)
    o.append(f'<div data-build-in="rise order 1"{DELAY(k * 90)} style="position:absolute;left:{x}px;top:{GBY}px;width:262px;height:300px;border-radius:16px;border:3px solid {col};background:{bg};display:flex;flex-direction:column;padding:14px 16px;gap:12px">'
             + p(f"font-size:28px;font-weight:700;color:{col}", e(c)) + f'<div style="display:flex;flex-direction:row;flex-wrap:wrap;gap:8px">{chips_}</div></div>')
    o.append(p(f"position:absolute;left:{x}px;top:{GBY + 236}px;width:262px;text-align:center;font-family:{MONO};font-size:34px;font-weight:700;color:{col}", f"{sum(vals)}", fade(3)))
o.append(caption("39의 GROUP BY category와 SUM(amount)를 한 줄로 쓴 거예요.", 900, 5))
W("a-group", o, "groupby에 열 이름을 넣으면 그 열 값이 같은 행끼리 바구니에 담아요. 39에서 GROUP BY로 묶던 것과 같아요. 바구니마다 amount 열을 고르고 sum으로 더하면 분류마다 합계가 하나씩 나와요. 그림의 문화 바구니에는 앞 장에서 고친 14000이 들어 있어서 27900이에요. groupby 결과는 분류 이름 순서라서, 마지막에 sort_values로 큰 순서로 세웠어요. 쇼핑에 가장 많이 썼어요." + REAL)

o = [sec("a-count")] + head(EB4, "value_counts는 값마다 몇 번 나왔는지 세요", K4)
T = 200
CFS[0] = 34
VC = ["category", "식비    5", "문화    3", "교통    2", "쇼핑    2", "Name: count, dtype: int64"]
o += cell({"id": "c-vc", "lines": ['spend["category"].value_counts()'], "n": 32, "out": VC}, 96, T, 1000, sel="c-vc")
BX0, BY0 = 1160, 300
for k, (c, n) in enumerate([("식비", 5), ("문화", 3), ("교통", 2), ("쇼핑", 2)]):
    col, bg = CATC[c]
    y = BY0 + k * 100
    o.append(p(f"position:absolute;left:{BX0}px;top:{y}px;width:90px;font-size:30px;font-weight:700;line-height:70px;color:{col}", e(c), fade(1)))
    o.append(f'<div{WIPE(1)}{DELAY(k * 120)} style="position:absolute;left:{BX0 + 100}px;top:{y}px;width:{n * 100}px;height:70px;border-radius:10px;background:{col};display:flex;flex-direction:row;gap:0">'
             + "".join(f'<div style="width:100px;height:70px;border-right:2px solid rgba(255,255,255,0.6)"></div>' for _ in range(n)) + '</div>')
    o.append(p(f"position:absolute;left:{BX0 + 100 + n * 100 + 16}px;top:{y}px;font-family:{MONO};font-size:32px;font-weight:700;line-height:70px;color:{col}", str(n), fade(1)))
o.append(fix(96, 760, ".value_counts().sort_values(ascending=False)", ".value_counts()", 2, 30))
o.append(caption("이미 많은 순서로 나와서 sort_values를 붙이지 않아도 돼요.", 900, 3))
W("a-count", o, "value_counts는 열 안의 값마다 몇 번 나왔는지 세요. 15에서 딕셔너리에 하나씩 더해 가며 세던 일을 한 줄로 해요. 식비가 다섯 번으로 가장 많아요. 결과는 처음부터 많은 순서로 세워져 나와요. 수업 코드는 뒤에 sort_values(ascending=False)를 붙였는데 결과가 같아서 빼도 돼요. 횟수가 같은 교통과 쇼핑은 순서가 바뀔 수 있어요. 39의 COUNT(*)와 GROUP BY로 세던 것과 같아요." + REAL)

# ---------- part 5 ----------
o = [sec("c-cmp")] + head(EB5, "리스트, 배열, 표에서 같은 일을 이렇게 써요", K5)
CMP = [("모두 2배", "[a * 2 for a in amounts]", "arr * 2", 'spend["amount"] * 2'),
       ("합계", "sum(amounts)", "arr.sum()", 'spend["amount"].sum()'),
       ("평균", "sum(amounts) / len(amounts)", "arr.mean()", 'spend["amount"].mean()'),
       ("1만 원 이상", "[a for a in amounts if a >= 10000]", "arr[arr >= 10000]", 'spend[spend["amount"] >= 10000]'),
       ("큰 순서", "sorted(amounts, reverse=True)", "", 'spend.sort_values(by="amount", ascending=False)')]
o += plain_rows(96, 220, 1728, CMP, [170, 500, 290, 708], 1, 116, ("할 일", "리스트 (13, 22, 23)", "NumPy 배열", "pandas DataFrame"), 24, (1, 2, 3))
o.append(caption("배열과 표는 for 없이 열 전체에 한 번에 해요. 리스트 쪽이 가장 길어요.", 900, 7))
W("c-cmp", o, "같은 일을 리스트, 배열, 표로 나란히 적었어요. 리스트는 13의 sum, 22의 sorted, 23의 컴프리헨션으로 했어요. 배열은 for 없이 연산과 점 메서드로 해요. 표는 열 이름을 대괄호로 꺼낸 뒤 배열처럼 쓰고, 고르기와 정렬은 행 전체를 같이 움직여요. 배열은 정렬도 되지만 오늘은 다루지 않았어요. 데이터가 표 모양이면 pandas가 가장 짧아요.")

o = [sec("c-sql")] + head(EB5, "pandas 한 줄과 SQL 한 문장을 맞춰 봐요", K5)
SQ = [('spend[["shop", "amount"]]', "SELECT shop, amount FROM spend;", "36"),
      ('spend[spend["amount"] >= 10000]', "SELECT * FROM spend WHERE amount >= 10000;", "36"),
      ("(조건1) & (조건2)", "WHERE 조건1 AND 조건2", "38"),
      ('.sort_values(by="amount", ascending=False).head(3)', "ORDER BY amount DESC LIMIT 3", "36"),
      ('.groupby("category")["amount"].sum()', "SELECT category, SUM(amount) ... GROUP BY category", "39"),
      ('["category"].value_counts()', "SELECT category, COUNT(*) ... GROUP BY category", "39"),
      ('spend.loc[2, "amount"] = 14000', "UPDATE spend SET amount = 14000 WHERE id = 2;", "36")]
o += plain_rows(96, 210, 1728, SQ, [770, 780, 98], 1, 84, ("pandas", "SQL (psql)", "챕터"), 24, (0, 1))
o.append(caption("SQL은 데이터베이스에 묻고, pandas는 노트북 안의 표에 바로 물어요.", 900, 8))
W("c-sql", o, "32부터 배운 SQL과 오늘의 pandas는 같은 일을 다른 말로 해요. 열 고르기는 SELECT, 표[조건]은 WHERE, &는 AND예요. sort_values와 head는 ORDER BY와 LIMIT, groupby와 sum은 GROUP BY와 SUM, value_counts는 GROUP BY와 COUNT예요. loc로 칸 고치기는 UPDATE예요. 차이는 데이터가 있는 곳이에요. SQL은 서버의 데이터베이스에 묻고, pandas는 파이썬 메모리에 올린 표를 바로 다뤄요. 44의 psycopg로 꺼낸 결과도 pandas 표로 옮길 수 있어요.")

o = [sec("e-and")] + head(EB5, "and를 쓰거나 괄호를 빼면 오류가 나요", K5)
T = 200
CFS[0] = 26
E1 = 'spend[spend["category"] == "식비" and spend["amount"] >= 5000]'
E2 = 'spend[spend["category"] == "식비" & spend["amount"] >= 5000]'
o += cell({"id": "c-ea1", "lines": [E1], "n": 33, "out": ["ValueError: The truth value of a Series is ambiguous. Use a.empty, a.item(), a.any() or a.all()."], "err": True}, 96, T, 1728)
o.append(tint(1, cx(96, 'spend[spend["category"] == "식비" ') - 4, ly(T, 0) - LH() / 2, tw("and") + 8, LH(), RED))
o.append(reading(96 + 105, oy(T, 1, 0) + 36, "True, False가 12개라서 and가 하나로 정하지 못해요.", RED, 1, 28))
T2 = 440
o += cell({"id": "c-ea2", "lines": [E2], "n": 34, "out": ["TypeError: Cannot perform 'rand_' with a dtyped [int64] array and scalar of type [bool]"], "err": True}, 96, T2, 1728)
o.append(tint(2, cx(96, 'spend[spend["category"] == "식비" ') - 4, ly(T2, 0) - LH() / 2, tw("&") + 8, LH(), RED))
o.append(reading(96 + 105, oy(T2, 1, 0) + 36, '&가 ==보다 먼저 묶여서 "식비" & spend["amount"]부터 계산해요.', RED, 2, 28))
o.append(fix(96, 720, "조건1 and 조건2", "(조건1) & (조건2)", 3, 34))
W("e-and", o, "조건 두 개를 and로 잇거나 괄호 없이 &로 이으면 오류가 나요. and는 왼쪽이 True인지 하나로 정해야 하는데, Series에는 True와 False가 12개라 정할 수 없다는 ValueError예요. 괄호를 빼면 파이썬은 &를 ==보다 먼저 계산해요. 그래서 \"식비\" & spend[\"amount\"]라는 엉뚱한 계산을 하다가 TypeError가 나요. 조건마다 괄호로 감싸고 &로 이어요. 괄호를 빠뜨리기 쉬운 곳이라 오류 메시지를 같이 기억해 둬요." + REAL)

o = [sec("e-key")] + head(EB5, "열 이름이 틀리거나 대괄호가 한 겹이면 KeyError", K5)
T = 200
CFS[0] = 32
o += cell({"id": "c-ek1", "lines": ['spend["amout"]'], "n": 35, "out": ["KeyError: 'amout'"], "err": True}, 96, T, 860)
o += cell({"id": "c-ek2", "lines": ['spend["shop", "amount"]'], "n": 36, "out": ["KeyError: ('shop', 'amount')"], "err": True}, 984, T, 840)
o.append(underline(1, cx(96, 'spend["amo'), cx(96, 'spend["amou'), ly(T, 0) + LH() / 2 - 4, RED, 5))
o.append(tint(2, cx(984, "spend[") - 6, ly(T, 0) - LH() / 2, tw('"shop", "amount"') + 12, LH(), RED))
o.append(reading(96, 470, "왼쪽: 열 이름 amount에서 n이 빠졌어요.", RED, 1, 30))
o.append(reading(96, 530, "오른쪽: 이름 두 개를 한 열 이름으로 찾았어요.", RED, 2, 30))
o.append(fix(96, 650, 'spend["amout"]', 'spend["amount"]', 3, 34))
o.append(fix(96, 770, 'spend["shop", "amount"]', 'spend[["shop", "amount"]]', 4, 34))
o.append(caption("열 이름이 헷갈리면 spend.head()로 머리글부터 봐요.", 900, 5))
W("e-key", o, "없는 열 이름을 찾으면 KeyError가 나요. 15에서 딕셔너리에 없는 키를 찾을 때와 같은 오류예요. 왼쪽은 amount를 amout으로 잘못 적었어요. 오른쪽은 대괄호를 한 겹만 써서, pandas가 shop과 amount 둘을 묶은 이름 하나를 찾았어요. 열 두 개를 고르려면 3파트처럼 이름 리스트를 넣어 대괄호를 두 겹으로 써요. 머리글은 spend.head()로 확인해요." + REAL)

o = [sec("e-mod")] + head(EB5, "패키지를 안 넣었거나 리스트에 mean을 부르면", K5)
T = 250
CFS[0] = 28
o.append(label(96, T - 50, "uv add를 안 한 프로젝트", GRAY, 26))
o += cell({"id": "c-em1", "lines": ["import pandas as pd"], "n": 1, "out": ["ModuleNotFoundError: No module named 'pandas'"], "err": True}, 96, T, 960)
o.append(term(1110, T, 714, [("$", "uv add numpy pandas")], 28, rise(1)))
o.append(p(f"position:absolute;left:1110px;top:{T + 110}px;width:714px;font-size:26px;line-height:1.5;color:{SUB}", "넣은 뒤 노트북 위쪽 Restart를 누르고 다시 실행해요.", rise(1)))
T2 = 520
o.append(label(96, T2 - 50, "2파트 노트북", GRAY, 26, rise(2)))
o += cell({"id": "c-em2", "lines": ["print(sum(amounts) / len(amounts))", "print(amounts.mean())"], "n": 10, "out": ["8883.333333333334", "AttributeError: 'list' object has no attribute 'mean'"], "err": True}, 96, T2, 1728, attrs=rise(2))
o.append(fix(96, 790, "amounts.mean()", "arr.mean()", 3, 30))
o.append(caption("리스트에는 mean, shape가 없어요. np.array로 바꾼 배열에 물어요.", 900, 4))
W("e-mod", o, "pandas를 넣지 않은 프로젝트에서 import하면 ModuleNotFoundError가 나요. 터미널에서 uv add numpy pandas를 치고, 노트북의 Restart를 눌러 다시 실행해요. 커널이 다른 폴더의 파이썬으로 골라져 있어도 같은 오류가 나요. 오른쪽은 2파트에서 리스트 amounts에 mean을 부른 경우예요. 리스트에는 그런 메서드가 없어서 AttributeError가 나요. 리스트는 sum을 len으로 나누고, 배열이면 arr.mean()으로 물어요. 왼쪽 출력은 pandas 없이 ipykernel만 넣은 프로젝트에서 실행했어요." + REAL)

# ---------- part 6 ----------
o = [sec("x-top")] + head(EB6, "이번 달 가장 많이 쓴 곳 세 군데를 뽑아요", K6)
T = 210
CFS[0] = 32
XT = ['top = spend.sort_values(by="amount", ascending=False).head(3)', 'top[["shop", "amount"]]']
o += cell({"id": "c-xt", "lines": XT, "n": 3}, 96, T, 1728, sel="c-xt")
o.append(hl(96, T, 1728, 0, 1, "mark", 1, "3파트 sort_values"))
o.append(hl(96, T, 1728, 1, 1, "run", 2, "3파트 열 두 개"))
TY = cbot(T, 2) + 16
XR = 96
o.append(df("xt-df", 96 + 85, TY, ["shop", "amount"], [("온라인쇼핑", 32000), ("온라인쇼핑", 18500), ("영화관", 15000)], [260, 190], fs=38, rh=XR, idx=[4, 10, 2], iw=80, attrs=rise(2)))
BX = 880
for k, (s_, v) in enumerate([("온라인쇼핑", 32000), ("온라인쇼핑", 18500), ("영화관", 15000)]):
    y = TY + XR * (k + 1) + 14
    o.append(f'<div{WIPE(3)}{DELAY(k * 150)} style="position:absolute;left:{BX}px;top:{y}px;width:{int(v / 32000 * 900)}px;height:{XR - 26}px;border-radius:10px;background:{[TEAL, TEAL, K4][k]}"></div>')
o.append(caption("세 곳 중 두 곳이 온라인쇼핑이에요.", 880, 4))
W("x-top", o, "새 노트북에서 1파트의 리스트 셀과 3파트의 DataFrame 셀을 먼저 실행해요. 지출이 큰 순서로 세운 뒤 위에서 세 줄을 top에 담고, 가게와 금액 열만 골라 봤어요. 3파트에서 배운 sort_values, head, 열 두 개 고르기를 이어 쓴 거예요. 막대는 32000원을 기준으로 길이를 맞춘 그림이에요. 온라인쇼핑이 두 번이나 들어 있어요." + NEWK + REAL, ("p6", "실제 상황"))

o = [sec("x-food")] + head(EB6, "식비가 예산 2만 원을 넘었는지 계산해요", K6)
T = 210
CFS[0] = 30
XF = ['food = spend[spend["category"] == "식비"]["amount"].sum()', 'print(f"식비 {food}원, 예산 20000원보다 {food - 20000}원 더 썼어요")']
o += cell({"id": "c-xf", "lines": XF, "n": 4, "out": ["식비 24200원, 예산 20000원보다 4200원 더 썼어요"]}, 96, T, 1728, sel="c-xf")
pre = "food = "
for k, (s, t, col) in enumerate([('spend[spend["category"] == "식비"]', "① 식비 행만", BL), ('["amount"]', "② 금액 열", TEAL), (".sum()", "③ 더하기", GR)]):
    o.append(underline(k + 1, cx(96, pre), cx(96, pre + s), ly(T, 0) + LH() / 2 - 2, col, 5))
    o.append(label(cx(96, pre), oy(T, 2, 0) + 50, t, col, 26, fade(k + 1)))
    pre += s
GY = 600
SC = 1500 / 30000
o.append(f'<div style="position:absolute;left:96px;top:{GY}px;width:1500px;height:90px;border-radius:12px;background:#ECEAE4"></div>')
o.append(f'<div{WIPE(4)} style="position:absolute;left:96px;top:{GY}px;width:{24200 * SC:.0f}px;height:90px;border-radius:12px;background:{OR}"></div>')
o.append(f'<div style="position:absolute;left:{96 + 20000 * SC:.0f}px;top:{GY - 30}px;width:4px;height:150px;background:{INK}"></div>')
o.append(label(96 + 20000 * SC - 120, GY - 76, "예산 20000", INK, 28))
o.append(label(96 + 24200 * SC + 20, GY + 22, "24200 (+4200)", RED, 32, fade(4)))
o.append(caption("13의 f-string으로 계산한 값을 문장 안에 넣었어요.", 840, 5))
W("x-food", o, "식비 행만 골라 금액 열을 더하고, 예산과 비교한 문장을 찍어요. 첫 줄은 왼쪽부터 읽어요. 식비인 행만 남긴 표에서 amount 열을 꺼내 sum으로 더해요. 둘째 줄은 13의 f-string으로 합계와 넘은 금액을 문장 안에 넣었어요. 1파트에서 for와 if로 다섯 줄을 쓴 24200을 한 줄로 구했어요." + REAL)

o = [sec("x-big")] + head(EB6, "1만 원 넘는 지출이 몇 번, 얼마인지 세요", K6)
T = 200
CFS[0] = 30
XB = ['big = spend[spend["amount"] >= 10000]', 'total = big["amount"].sum()', 'print(f"1만 원 넘는 지출 {len(big)}번, 합계 {total}원")', 'big["category"].value_counts()']
XBO = ["1만 원 넘는 지출 4번, 합계 76400원", "", "category", "문화    2", "쇼핑    2", "Name: count, dtype: int64"]
FW = 1240
o += cell({"id": "c-xb", "lines": XB, "n": 5, "out": XBO}, 96, T, FW, sel="c-xb")
TX = 96 + FW + 30
for k, t in enumerate(["3파트 표[조건]", "4파트의 합계", "len(표)는 행 수", "4파트 value_counts"]):
    o.append(run(k + 1, 96 + 89, T + 10 + k * LH(), FW - 93, LH()))
    o.append(tag(TX, ly(T, k), t, GR, k + 1, 28))
o.append(run_off(5))
o.append(caption("큰 지출 네 번이 문화와 쇼핑에 반씩 있어요.", 900, 5))
W("x-big", o, "1만 원 넘는 지출만 골라 횟수, 합계, 분류를 한 셀에서 봐요. 첫 줄은 3파트의 표[조건]으로 큰 지출 행만 big에 담아요. 둘째 줄은 그 표의 금액 합계예요. len에 표를 넣으면 행 수가 나와서 4번이에요. 마지막 줄은 4파트의 value_counts로 분류를 세요. print 뒤에 마지막 줄의 결과가 이어서 나와요." + REAL)

# ---------- wrap up ----------
o = [sec("trouble")] + head("정리", "막히면 오류의 마지막 줄을 봐요", RED)
TR = [("ModuleNotFoundError: No module named 'pandas'", "프로젝트에 안 넣었어요", "uv add numpy pandas 뒤 Restart"),
      ("AttributeError: 'list' object has no attribute 'mean'", "리스트에 배열 메서드를 불렀어요", "np.array()로 바꾸기"),
      ("ValueError: The truth value of a Series is ambiguous", "조건을 and로 이었어요", "(조건1) & (조건2)"),
      ("TypeError: Cannot perform 'rand_' ...", "조건에 괄호가 없어요", "조건마다 ( )"),
      ("KeyError: 'amout'", "열 이름이 틀렸어요", "spend.head()로 확인"),
      ("KeyError: ('shop', 'amount')", "대괄호가 한 겹이에요", "spend[[...]] 두 겹"),
      ("고쳤는데 point가 그대로예요", "계산한 열은 저절로 안 바뀌어요", "point 줄을 다시 실행")]
for i, (q, a_, cmd) in enumerate(TR):
    o.append(f'<div data-build-in="rise order {min(i + 1, 5)}" style="position:absolute;left:96px;top:{200 + i * 100}px;width:1728px;height:100px;display:flex;flex-direction:row;align-items:center;gap:26px;border-bottom:2px solid {LINE}">'
             + '<div style="flex:1;display:flex;flex-direction:column;gap:4px">' + p(f"{'font-family:' + MONO + ';' if q.isascii() else ''}font-size:25px;font-weight:700;color:{RED};white-space:nowrap", e(q)) + p(f"font-size:25px;color:{INK}", e(a_)) + '</div>'
             + p(f"width:520px;flex:none;font-size:27px;font-weight:700;color:{GR};white-space:pre", '✓ ' + e(cmd)) + '</div>')
o.append(caption("셀은 위에서부터 차례로 실행해요. 앞 셀을 건너뛰면 NameError가 나요.", 950))
W("trouble", o, "막히면 오류의 마지막 줄부터 읽어요. 이번 챕터에서 자주 만나는 일을 모았어요. 위 두 줄은 준비와 배열에서, 가운데 셋은 표를 고를 때, 마지막 줄은 열을 고칠 때 생겨요. 셀은 위에서부터 차례로 실행해야 해요. 노트북을 다시 열었다면 리스트 셀과 DataFrame 셀부터 실행해요.", ("trouble", "정리"))

o = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>']
CH = [("arr = np.array(리스트)", "칸마다 계산하는 배열", K2), ("arr.sum() .mean() .max()", "합계, 평균, 최대", K2), ("arr[arr >= 10000]", "조건에 맞는 칸만", K2),
      ("pd.DataFrame({열: 리스트})", "딕셔너리로 표 만들기", K3), ('spend[["shop", "amount"]]', "열 여러 개 고르기", K3), ('spend[(조건1) & (조건2)]', "행 고르기, 조건마다 괄호", K3),
      ('spend.sort_values(by="열", ascending=False)', "큰 순서로 세우기", K3), ('spend["새 열"] = 계산', "열 더하기, loc[번호, 열]로 고치기", K4),
      ('groupby("열")["값"].sum()', "분류마다 합계", K4), ('["열"].value_counts()', "값마다 횟수, 많은 순", K4)]
for i, (k, d, c) in enumerate(CH):
    x, y = 96 + (i // 5) * 884, 190 + (i % 5) * 124
    o.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:844px;height:110px;display:flex;flex-direction:column;justify-content:center;gap:4px;border-bottom:2px solid {LINE}">'
             + p(f"font-family:{MONO};font-size:{28 if len(k) > 34 else 32}px;font-weight:700;color:{c};white-space:pre", e(k)) + p(f"font-size:26px;color:{SUB}", e(d)) + '</div>')
o.append(p(f"position:absolute;left:96px;top:850px;width:1728px;font-size:32px;font-weight:700;line-height:1.5;color:{INK}", "숫자 묶음은 배열로, 열 이름이 있는 데이터는 표로 다뤄요.<br>" + f'<span style="color:{GRAY}">다음: 머신러닝 기초에서 이 표를 모델에 넣어요.</span>'))
W("cheatsheet", o, "숫자 묶음은 np.array로 배열을 만들어 칸마다 계산하고, 열 이름이 있는 데이터는 DataFrame으로 다뤄요. 표는 대괄호로 열과 행을 고르고, 조건 두 개는 괄호와 &로 이어요. sort_values로 세우고, 새 열은 대괄호에 넣어 만들고, loc로 칸을 고쳐요. groupby와 value_counts로 분류마다 합계와 횟수를 구해요. 다음 머신러닝 수업에서는 이렇게 다듬은 표를 모델에 넣어요.")

# ---------- toc ----------
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
parts_ = [("Lightbulb", K1, "왜 필요한가", "why", "min"), ("Code", K2, "NumPy 배열", "n-list", "n-filter"), ("Database", K3, "pandas 표 고르기", "d-make", "d-sort"),
          ("Tool", K4, "열 더하고 묶기", "a-div", "a-count"), ("Warning", K5, "비교와 오류", "c-cmp", "e-mod"), ("Star", K6, "실제 상황", "x-top", "x-big")]
t = [f'<section id="toc" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>']
for i, (ic, c, h, a, b) in enumerate(parts_):
    x, y = 96 + (i // 3) * 884, 230 + (i % 3) * 190
    t.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:844px;height:160px;display:flex;flex-direction:row;align-items:center;gap:28px;border-bottom:2px solid {LINE}">'
             f'<p style="width:70px;font-size:72px;font-weight:900;color:{c}">{i + 1}</p><x-icon name="{ic}" style="width:52px;height:52px;color:{c}"></x-icon>'
             f'<p style="flex:1;font-size:44px;font-weight:700;color:{INK}">{e(h)}</p><p style="font-size:28px;color:{GRAY}">{page[a]}–{page[b]}쪽</p></div>')
t.append(f'<p style="position:absolute;left:96px;top:880px;font-size:30px;color:{SUB}">{page["setup"]}쪽은 프로젝트 준비, {page["trouble"]}–{page["cheatsheet"]}쪽은 막힐 때와 한 장 요약이에요.</p>')
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(t) + "\n<aside>" + e("2파트 NumPy와 3, 4파트 pandas가 중심이에요. 1파트는 for 문의 불편함과 리스트, 배열, 표의 관계예요. 2파트는 배열을 칸마다 계산하고 조건으로 골라요. 3파트는 표를 만들고 열과 행을 골라 세워요. 4파트는 열을 더하고 고치고 분류마다 묶어요. 5파트는 리스트와 SQL과 비교하고 오류를 모았어요. 6파트는 이번 달 지출에 질문 세 개를 던져요. 노트북 셀은 위에서부터 차례로 실행해요.") + "</aside>\n</section>\n")
deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-20T03:00:00Z"}, "lists": "css", "title": "NumPy와 pandas 맛보기", "order": ORDER, "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
print(len(ORDER), "slides")
