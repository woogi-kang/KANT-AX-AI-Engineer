"""Generates every slide of the first machine learning model deck (48, linear regression) and slides/deck.json.

Story: class notebook 02_ml.ipynb, second half (the first half, graphs and practice data, is chapter 47). A new notebook
model.ipynb reads the office.csv that 47 saved, whose rule we know (price = area x 450 + 5000 plus noise and 5 special
listings). Part 1: a hand-drawn line differs per person, the five-step map, a line is two numbers (w and b), and what
scikit-learn is. Part 2 takes the class cell apart one call at a time, each with why its arguments look that way:
the import path, an empty model object, X as a two-dimensional table and y as one column, fit(X, y), the line with the
smallest squared error, coef_ and intercept_ against 450 and 5000, predict with a DataFrame of the same column name,
y_pred for all 200 rows, and drawing the line after sort_values. Part 3 scores it: errors cancel out, MAE, MSE, RMSE,
R2 against guessing the mean, and the metric functions' (answer, prediction) order. Part 4: the special listings mask
(np.ones, dtype=bool, normal[special] = False), scores without them, and R2 as 47's correlation squared. Part 5: a 1-D
X, predict(33), a different column name, predict before fit, and the class's mask cell that passed special instead of
normal (R2 -2.55). Part 6: a quote table with a range of plus or minus MAE, finding the special listings from the
errors and learning again without them, and the usa_housing data where area explains almost nothing.
Every cell and output comes from tools/demo.sh (tools/run_nb.py runs the cells with the project kernel), kept in
tools/demo.log. Charts are the kernel's own PNGs in tools/img (NanumGothic stands in for Malgun Gothic on Linux).
Drawn diagrams (hand lines, residual squares, error bars) are computed here from datasets/office.csv with NumPy.

Layout rules (Stageshow skill, github.com/benjitaylor/skills, read in full for this deck):
1. one focal object per slide (a notebook cell, a chart from the kernel, one code line taken apart, or one diagram)
2. terms are labelled on the code token or the chart part with leader tags and tints, not in separate cards (annotations.md)
3. say it once: what the speaker notes say does not repeat in cards; one caption at most
4. no empty bands: the chart or the code grows to fill; the payoff gets the room (craft.md, Restraint)
5. values move instead of swapping: X and y fly into fit, w and b fill the empty model, True turns False in place
6. one number gets to be big (R2 0.80 to 0.92, MAE 2,510), the rest are lines (craft.md, Restraint)
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


# ---------- this deck ----------
NB = "model.ipynb"
NEW1 = " 이 셀만 새 노트북에서 실행해서 셀 번호가 [1]부터예요."
import numpy as np

EB1, EB2, EB3, EB4, EB5, EB6 = "1. 왜 필요한가", "2. 학습하고 예측하기", "3. 채점하기", "4. 특이 매물과 47 비교", "5. 오류와 함정", "6. 실제 상황"
IMPORTS = ["import numpy as np", "import pandas as pd", "import matplotlib.pyplot as plt"]
FITC = ["from sklearn.linear_model import LinearRegression", "", "model = LinearRegression()", "", 'X = office[["area"]]', 'y = office["price"]', "model.fit(X, y)", "",
        'print("기울기 w:", model.coef_[0], "정답: 450")', 'print("절편 b:", model.intercept_, "정답: 5000")']
FITO = ["기울기 w: 465.6735571178265 정답: 450", "절편 b: 4727.983834181516 정답: 5000"]
DRAWC = ["y_pred = model.predict(X)", "", 'line = X.sort_values("area")', "line_pred = model.predict(line)", "", "plt.figure(figsize=(8, 5))",
         'plt.scatter(office["area"], office["price"], alpha=0.6, label="실제 시세")', 'plt.plot(line["area"], line_pred, color="red", label="모델의 직선")',
         'plt.title("오피스텔 시세 200건")', 'plt.xlabel("면적")', 'plt.ylabel("가격")', "plt.legend()", "plt.show()"]
METC = ["from sklearn.metrics import mean_absolute_error, mean_squared_error, root_mean_squared_error, r2_score", "",
        'print(f"MAE = {mean_absolute_error(y, y_pred):,.0f}")', 'print(f"MSE = {mean_squared_error(y, y_pred):,.0f}")',
        'print(f"RMSE = {root_mean_squared_error(y, y_pred):,.0f}")', 'print(f"R2 = {r2_score(y, y_pred)}")']
METO = ["MAE = 2,510", "MSE = 17,697,259", "RMSE = 4,207", "R2 = 0.8041321769128468"]
NORMC = ["special = [17, 134, 178, 172, 122]", "", "normal = np.ones(len(office), dtype=bool)", "normal[special] = False", 'print("특이 매물:", special)', 'print("정상 매물:", normal.sum())']
CASEC = ["all_rows = np.ones(len(office), dtype=bool)", 'cases = [("전체 200건", all_rows), ("특이 매물 뺀 195건", normal)]', "",
         "for name, mask in cases:", "    y_true = y[mask]", "    y_hat = y_pred[mask]", "    mae = mean_absolute_error(y_true, y_hat)",
         "    rmse = root_mean_squared_error(y_true, y_hat)", "    r2 = r2_score(y_true, y_hat)", '    print(f"{name} MAE {mae:,.0f} | RMSE {rmse:,.0f} | R2 {r2:.2f}")']
CASEO = ["전체 200건 MAE 2,510 | RMSE 4,207 | R2 0.80", "특이 매물 뺀 195건 MAE 2,033 | RMSE 2,567 | R2 0.92"]

# the deck's own copy of office.csv, for drawn diagrams (the slide numbers that students see come from demo.log)
_d = np.loadtxt(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "datasets", "office.csv"), delimiter=",", skiprows=1)
AREA, PRICE = _d[:, 0], _d[:, 1]
WFIT, BFIT = np.polyfit(AREA, PRICE, 1)
assert abs(WFIT - 465.6736) < 0.01 and abs(BFIT - 4727.98) < 0.1
PRED = AREA * WFIT + BFIT
ERR = PRICE - PRED
SPECIAL = [17, 134, 178, 172, 122]
assert sorted(np.argsort(-np.abs(ERR))[:5]) == sorted(SPECIAL)


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


def cap_note():
    return ""


# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#F2B27A;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
       f'<h1{SLAM(1)} style="font-size:92px;font-weight:900;line-height:1.12;color:#F6F5F1">첫 머신러닝 모델<br>(선형 회귀)</h1>',
       '<p style="font-size:38px;line-height:1.45;color:#BFC6D4">scikit-learn으로 직선을 학습하고,<br>예측하고, 채점해요</p>']
cov.append(f'<div id="cov-card" style="position:absolute;left:1080px;top:200px;width:720px;height:540px;background:#FFFFFF;border-radius:24px;overflow:hidden">'
           + f'<img id="cov-img" src="data:image/png;base64,{png_b64("main-1.png")}" style="position:absolute;left:40px;top:58px;width:640px">'
           + '</div>')
cov.append(p(f"position:absolute;left:1080px;top:770px;width:720px;font-size:26px;line-height:1.5;color:#BFC6D4", "47에서 만든 오피스텔 시세 200건에 모델이 그은 직선이에요."))
cov.append(kenburns(2, "cov-img", 1.08, 6000, "55% 45%"))
W("cover", cov, "오늘은 첫 머신러닝 모델을 만들어요. 47에서 정답을 알고 만든 오피스텔 시세 데이터로 선형 회귀 모델을 학습해요. 모델이 찾은 직선으로 처음 보는 면적의 가격을 예측하고, 얼마나 잘 맞혔는지 점수를 매겨요. 오른쪽 빨간 선이 오늘 모델이 찾을 직선이에요. 처음 쓰는 도구라서 함수마다 괄호 안에 왜 그 값이 들어가는지 하나씩 풀어 볼게요." + IMGN, ("intro", "들어가기"))
ORDER.append("toc")

# ---------- setup ----------
o = [sec("setup")] + head("들어가기", "ml-basics에 scikit-learn을 넣고 새 노트북을 열어요", JP)
TL = [("$", "cd ml-basics"), ("$", "uv add scikit-learn"), ("o", " + cloudpickle==3.1.3"), ("o", " + joblib==1.6.0"), ("o", " + narwhals==2.29.0"), ("o", " + scikit-learn==1.9.1"), ("o", " + scipy==1.18.1"), ("o", " + threadpoolctl==3.8.0"), ("o", ""), ("$", "ls datasets"), ("o", "office.csv  usa_housing.csv")]
o.append(term(96, 214, 900, TL, 26, tid="t-setup"))
LHt = 26 * 1.55
o.append(box(1, 96 + 34 - 10, 214 + 26 + 1 * LHt - 4, 26 * 0.6 * 21 + 20, LHt + 8, "#F2C46D", 4, 10))
o.append(note(96, 214 + 52 + len(TL) * LHt + 24, 900, "scikit-learn 말고 다섯 개는 scikit-learn이 안에서 쓰는 패키지라 같이 들어와요. 버전 숫자는 받는 날에 따라 달라요.", SUB, 26, fade(1)))
o.append(note(96, 214 + 52 + len(TL) * LHt + 124, 900, "office.csv가 없으면 47의 저장 셀을 실행하거나 이 폴더의 datasets에서 받아요.", SUB, 26, fade(2)))
TX = 1140
tree = [("ml-basics/", INK, 0, True), ("datasets/", K1, 1, True), ("office.csv", K4, 2, False), ("usa_housing.csv", INK, 2, False), ("house.ipynb", GRAY, 1, False), (NB, JP, 1, False), ("pyproject.toml", GRAY, 1, False)]
o.append(label(TX, 214, "폴더 모양", INK, 30))
for i, (n_, c_, d, folder) in enumerate(tree):
    y = 290 + i * 80
    at = rise(2) + DELAY(i * 60) if i else ""
    o.append(p(f"position:absolute;left:{TX + d * 56}px;top:{y}px;font-family:{MONO};font-size:32px;font-weight:700;line-height:64px;color:{c_};white-space:nowrap", ("▸ " if folder else "") + e(n_), at))
o.append(tag(TX + 2 * 56 + 32 * 0.6 * 12 + 50, 290 + 2 * 80 + 32, "47에서 저장", K4, 2, 26))
o.append(tag(TX + 56 + 32 * 0.6 * 11 + 50, 290 + 4 * 80 + 32, "47 노트북", GRAY, 2, 26))
o.append(tag(TX + 56 + 32 * 0.6 * 11 + 50, 290 + 5 * 80 + 32, "오늘 노트북", JP, 2, 26))
o.append(caption("노트북 커널은 .venv를 골라요(10). 패키지는 uv add로만 넣어요.", 930, 3))
W("setup", o, "45부터 쓰는 ml-basics 프로젝트를 이어서 써요. 터미널에서 uv add scikit-learn을 쳐서 머신러닝 도구를 넣어요. scikit-learn이 안에서 쓰는 패키지 다섯 개가 같이 설치돼요. datasets 폴더에는 47에서 저장한 office.csv가 있어야 해요. 없으면 47의 저장 셀을 다시 실행하거나 이 챕터 폴더의 datasets에서 받아 넣어요. VS Code에서 model.ipynb를 새로 만들고 커널은 .venv로 골라요." + REAL)

# ---------- part 1 ----------
o = [sec("why")] + head(EB1, "자를 대고 그은 직선은 사람마다 달라요", K1)
PL = Plot(300, 230, 1000, 620, (18, 88), (5000, 70000))
o += PL.axes("면적(㎡)", "가격(만 원)", (20, 40, 60, 80), (10000, 30000, 50000, 70000))
o.append(PL.svg(PL.dots(AREA, PRICE)))
HAND = [(340, 12000, "#9AA0AB", "가"), (600, 1500, "#9AA0AB", "나"), (250, 14000, "#9AA0AB", "다")]
for k, (w_, b_, c_, nm) in enumerate(HAND):
    o.append(PL.svg(PL.line(w_, b_, c_, 5, "14 10"), WIPE(1) + DELAY(k * 250)))
    o.append(label(PL.X(88) + 18, PL.Y(w_ * 88 + b_) - 18 + (12 if nm == "가" else 0), f"{nm}의 선", GRAY, 26, fade(1) + DELAY(k * 250)))
o.append(PL.svg(PL.line(WFIT, BFIT, RED, 7), WIPE(2)))
o.append(label(PL.X(88) + 18, PL.Y(WFIT * 88 + BFIT) - 34, "모델의 선", RED, 30, fade(2)))
o.append(caption("어느 선이 가장 잘 맞는지 계산해서 하나로 정하는 프로그램이 오늘의 모델이에요.", 950, 3))
W("why", o, "47에서 만든 오피스텔 시세 200건이에요. 이 점들 위에 자를 대고 직선을 그어 보라고 하면 사람마다 조금씩 다른 선을 그어요. 가, 나, 다 세 사람의 선처럼요. 어느 선이 가장 잘 맞는지 말로는 정하기 어려워요. 머신러닝 모델은 가장 잘 맞는다는 기준을 숫자로 정해 두고, 계산해서 선 하나를 골라요. 빨간 선이 오늘 모델이 고를 선이에요. 이 선이 있으면 처음 보는 면적의 가격도 읽을 수 있어요. 점과 빨간 선은 office.csv로 그렸어요.", ("p1", "왜 필요한가"))

o = [sec("big")] + head(EB1, "47은 그래프와 연습 데이터, 48은 학습과 채점이에요", K1)
ST5 = [("표 준비", "pandas", "45, 46", GRAY, False), ("그래프로 보기", "matplotlib", "47", GRAY, False), ("연습 데이터", "NumPy 난수", "47", GRAY, False), ("학습하고 예측", "scikit-learn", "48", K2, True), ("채점", "scikit-learn", "48", K3, True)]
BW, GAP_, Y0 = 280, 77, 300
BH5 = 430
for i, (h_, lib, ch, c_, on) in enumerate(ST5):
    x = 96 + i * (BW + GAP_)
    bg = "#FFFFFF" if on else "#F1F0EC"
    bd = f"3px solid {c_}" if on else "3px solid #DAD7CF"
    o.append(f'<div data-build-in="rise order {1 if i < 3 else 2}"{DELAY((i % 3) * 120)} style="position:absolute;left:{x}px;top:{Y0}px;width:{BW}px;height:{BH5}px;border-radius:18px;border:{bd};background:{bg};display:flex;flex-direction:column;align-items:center;justify-content:center;gap:26px">'
             + num(i + 1, c_ if on else "#9AA0AB", 48) + p(f"font-size:36px;font-weight:700;color:{INK if on else GRAY}", e(h_))
             + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{c_ if on else GRAY}", e(lib)) + '</div>')
    o.append(p(f"position:absolute;left:{x}px;top:{Y0 + BH5 + 24}px;width:{BW}px;text-align:center;font-size:28px;font-weight:700;color:{c_ if on else GRAY}", f"{ch}", fade(1 if i < 3 else 2)))
    if i < 4:
        o.append(arrow(GAP_ - 24, "#C9CED8", WIPE(1 if i < 3 else 2), f"position:absolute;left:{x + BW + 12}px;top:{Y0 + BH5 / 2 - 15:.0f}px"))
o.append(f'<div data-build-in="fade order 3" style="position:absolute;left:{96 + 3 * (BW + GAP_) - 20}px;top:{Y0 - 30}px;width:{2 * BW + GAP_ + 40}px;height:{BH5 + 110}px;border-radius:26px;border:4px solid {K2};"></div>')
o.append(label(96 + 3 * (BW + GAP_) - 20, Y0 - 76, "오늘", K2, 30, fade(3)))
o.append(caption("정답(450, 5000)을 알고 만든 데이터라서 모델이 얼마나 가깝게 찾았는지 바로 맞춰 볼 수 있어요.", 920, 4))
W("big", o, "머신러닝 기초 수업의 다섯 단계를 다시 봐요. 45와 46에서 표를 준비했고, 47에서 그래프를 그리고 연습 데이터를 만들었어요. 오늘 48은 마지막 두 단계예요. scikit-learn으로 모델을 학습해서 예측하고, 그 예측이 얼마나 맞는지 채점해요. 47에서 가격을 면적 곱하기 450 더하기 5000으로 만들었으니, 모델이 찾은 숫자를 정답과 바로 비교할 수 있어요.")

o = [sec("wxb")] + head(EB1, "직선 하나는 숫자 두 개, 기울기 w와 절편 b로 정해져요", K1)
o.append(strip_code(96, 200, 1728, 130, [("가격 = ", W_, None), ("w", "#F2C46D", "f-w"), (" × 면적 + ", W_, None), ("b", "#8FD8DE", "f-b")], 52))
PW = Plot(250, 420, 760, 470, (0, 90), (0, 50000))
o += PW.axes("면적", "가격", (0, 20, 40, 60, 80), (0, 25000, 50000))
o.append(PW.svg(PW.line(450, 5000, INK, 5)))
xa, xb = 40, 60
o.append(PW.svg(f'<path d="M{PW.X(xa):.0f},{PW.Y(450 * xa + 5000):.0f} H{PW.X(xb):.0f} V{PW.Y(450 * xb + 5000):.0f}" fill="none" stroke="{K2}" stroke-width="5"/>', fade(1)))
o.append(label(PW.X(xa) + 30, PW.Y(450 * xa + 5000) + 10, "면적 +20", K2, 24, fade(1)))
o.append(label(PW.X(xb) + 16, PW.Y(450 * 50 + 5000) - 30, "가격 +9,000", K2, 24, fade(1)))
o.append(PW.svg(f'<circle cx="{PW.X(0):.0f}" cy="{PW.Y(5000):.0f}" r="12" fill="{K3}"/>', fade(2)))
o.append(label(PW.X(0) + 26, PW.Y(5000) - 4, "면적 0일 때 5,000", K3, 24, fade(2)))
RX = 1150
o.append(p(f"position:absolute;left:{RX}px;top:430px;width:670px;font-size:34px;font-weight:700;line-height:1.5;color:{INK}", f'<span{MARK(1)} style="color:{K2};background:{K2BG};border-radius:8px;padding:0 8px">w 기울기</span> <br>면적이 1 늘 때 가격이 오르는 양'))
o.append(p(f"position:absolute;left:{RX}px;top:590px;width:670px;font-size:34px;font-weight:700;line-height:1.5;color:{INK}", f'<span{MARK(2)} style="color:{K3};background:{K3BG};border-radius:8px;padding:0 8px">b 절편</span> <br>면적이 0일 때의 가격'))
o.append(note(RX, 760, 670, "47의 정답은 w = 450, b = 5000이에요.<br>모델은 이 두 숫자를 모른 채 점만 보고 찾아요.", SUB, 28, fade(3)))
W("wxb", o, "직선은 숫자 두 개만 알면 그릴 수 있어요. 기울기 w는 면적이 1 늘어날 때 가격이 얼마나 늘어나는지예요. 왼쪽 그림에서 면적이 20 늘면 가격은 9,000 늘어요. 20 곱하기 450이에요. 절편 b는 면적이 0일 때의 가격이에요. 선이 세로축과 만나는 높이라서 5,000이에요. 모델이 학습한다는 말은 점들을 보고 이 w와 b를 찾는다는 뜻이에요. 47에서 정답을 450과 5000으로 정해 두었으니 모델이 찾은 값과 비교해 볼 수 있어요.")

o = [sec("sklearn")] + head(EB1, "scikit-learn은 머신러닝 모델을 모아 둔 패키지예요", K1)
o += plain_rows(96, 210, 1728, [("설치할 때", "uv add scikit-learn", "패키지 이름 그대로"), ("불러올 때", "import sklearn", "줄여 쓴 이름. 짧게 sklearn으로 불러요")], [300, 620, 760], 1, 100, ["", "적는 이름", "메모"], 34, mono_cols=(1,))
DRW = [("linear_model", "직선 모델", "LinearRegression", K2, True), ("metrics", "채점 함수", "mean_absolute_error ...", K3, True), ("tree", "나무 모델", "다음 수업", GRAY, False), ("neighbors", "이웃 모델", "다음 수업", GRAY, False)]
BX0, BY0 = 96, 520
o.append(f'<div data-build-in="rise order 2" style="position:absolute;left:{BX0}px;top:{BY0}px;width:1728px;height:360px;border-radius:22px;border:3px solid {INK};background:#FFFFFF"></div>')
o.append(label(BX0 + 30, BY0 + 20, "sklearn", INK, 32, rise(2), True))
for i, (m, k, c, col, on) in enumerate(DRW):
    x = BX0 + 30 + i * 420
    o.append(f'<div data-build-in="rise order {2 if on else 3}"{DELAY(i * 80)} style="position:absolute;left:{x}px;top:{BY0 + 90}px;width:390px;height:240px;border-radius:16px;border:3px {"solid" if on else "dashed"} {col};background:{K2BG if i == 0 else (K3BG if i == 1 else "#F6F5F1")};display:flex;flex-direction:column;justify-content:center;gap:12px;padding:0 24px">'
             + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{col}", e(m)) + p(f"font-size:28px;font-weight:700;color:{INK if on else GRAY}", e(k))
             + p(f"font-family:{MONO};font-size:{22 if on else 24}px;color:{SUB if on else GRAY};white-space:nowrap", e(c)) + '</div>')
o.append(caption("오늘은 linear_model과 metrics 두 서랍만 열어요.", 930, 4))
W("sklearn", o, "scikit-learn은 머신러닝 모델과 채점 함수를 모아 둔 파이썬 패키지예요. 설치할 때는 scikit-learn이라고 적고, 코드에서 불러올 때는 줄인 이름 sklearn으로 적어요. 이름이 달라서 처음에 많이 헷갈려요. 패키지 안에는 모듈이 서랍처럼 나뉘어 있어요. 직선 모델은 linear_model 서랍에, 채점 함수는 metrics 서랍에 있어요. 나무 모델이나 이웃 모델 같은 다른 서랍도 있지만 다음 수업에서 봐요. 어느 서랍의 모델이든 만들기, fit, predict 세 줄로 쓰는 방법이 같아서 오늘 익힌 모양을 그대로 써요.")

# ---------- minimal example ----------
o = [sec("min")] + head(EB1, "가장 짧은 학습: 만들고, 문제와 정답을 넣고, fit", K1)
CFS[0] = 30
MT = 196
o += cell({"id": "c-min", "lines": FITC, "n": 4, "out": FITO}, 96, MT, 1240, sel="c-min")
TGS = [(0, "① 모델 설계도 불러오기", K2), (2, "② 빈 모델 하나 만들기", K2), (4, "③ 문제: 면적 (표)", K1), (5, "④ 정답: 가격 (한 줄)", K4), (6, "⑤ 학습", GR), (8, "⑥ 찾은 숫자 보기", GRAY)]
for k, (i, t_, c_) in enumerate(TGS):
    o.append(tag(1366, ly(MT, i), t_, c_, k // 2 + 1 if k < 4 else (3 if k == 4 else 4), 28, lead=False))
o.append(lspot(1, 96 + 87, MT, 1240 - 87, 10 + 10 * LH() + 8, MT + 10 + 0 * LH(), 3 * LH(), bar=K2))
o.append(lspot(2, 96 + 87, MT, 1240 - 87, 10 + 10 * LH() + 8, MT + 10 + 4 * LH(), 2 * LH(), bar=K1))
o.append(lspot(3, 96 + 87, MT, 1240 - 87, 10 + 10 * LH() + 8, MT + 10 + 6 * LH(), LH(), bar=GR))
o.append(lspot_off(4))
o.append(underline(4, cx(96, "기울기 w: ", True), cx(96, "기울기 w: 465.6735571178265", True), oy(MT, 10, 0) + LH() / 2, K2, 5))
o.append(underline(4, cx(96, "절편 b: ", True), cx(96, "절편 b: 4727.983834181516", True), oy(MT, 10, 1) + LH() / 2, K3, 5))
o.append(caption("정답 450, 5000과 가깝지만 똑같지는 않아요. 왜 그런지는 2파트에서 봐요.", 950, 5))
W("min", o, "수업 셀 하나로 첫 모델을 학습해요. 다섯 부분으로 읽어요. 첫 줄은 scikit-learn에서 선형 회귀 모델의 설계도를 불러와요. 둘째 줄은 그 설계도로 빈 모델을 하나 만들어요. X에는 문제인 면적을, y에는 정답인 가격을 담아요. model.fit이 학습하는 줄이에요. 마지막 두 줄은 학습으로 찾은 기울기와 절편을 정답 옆에 찍어요. 465.67과 4727.98이 나왔어요. 정답 450, 5000과 가깝지만 똑같지는 않아요. 다음 파트에서 한 줄씩 왜 이렇게 쓰는지 봐요. 앞에는 import 셀과 office.csv를 읽는 셀이 먼저 있어요." + REAL)

# ---------- read (after setup, before part 1 in ORDER) ----------
o = [sec("read")] + head("들어가기", "맨 위 세 셀: 불러오기, 한글 글꼴, office.csv 읽기", JP)
CFS[0] = 26
o += cell({"id": "c-imp", "lines": IMPORTS, "n": 1}, 96, 196, 900)
o.append(note(96 + 105, cbot(196, 3) + 24, 790, "[2]는 47과 같은 한글 글꼴 셀이에요(platform.system).", GRAY, 24))
RT = cbot(196, 3) + 90
RC = ['office = pd.read_csv("datasets/office.csv")', "print(office.shape)", "office.head()"]
o += cell({"id": "c-read", "lines": RC, "n": 3, "out": ["(200, 2)"]}, 96, RT, 900, sel="c-read")
o.append(tint(1, cx(96, "office = pd.read_csv(") - 4, ly(RT, 0) - LH() / 2, tw('"datasets/office.csv"') + 8, LH(), K4))
o.append(tag(96 + 900 + 24, ly(RT, 0), "노트북 옆 datasets 폴더", K4, 1, 24))
OH = [("70.307143", "38248.214420"), ("48.527099", "25847.194363"), ("75.808865", "39103.989157"), ("65.328922", "33988.014850"), ("26.121528", "17594.687426")]
o.append(df("rd-df", 96 + 105, oy(RT, 3, 0) + 40, ["area", "price"], OH, [200, 260], fs=28, rh=58, iw=50, attrs=rise(2)))
RX = 1100
o.append(label(RX, 560, "area  면적(㎡)", K1, 32, rise(2), True))
o.append(label(RX, 630, "price  가격(만 원)", K4, 32, rise(2), True))
o.append(note(RX, 720, 720, "200줄, 2열이에요. 47에서 저장한 숫자 그대로라<br>첫 줄 면적 70.3㎡, 가격 38,248만 원이 같아요.", SUB, 28, fade(3)))
W("read", o, "새 노트북 맨 위에는 셀 세 개를 먼저 둬요. 첫 셀은 NumPy, pandas, matplotlib을 불러와요. 둘째 셀은 47과 같은 한글 글꼴 설정이에요. 셋째 셀에서 47이 저장한 office.csv를 읽어요. 경로의 datasets는 노트북 옆에 있는 폴더 이름이에요. 200줄, 2열이 나오고, 첫 줄은 면적 70.3, 가격 38,248이에요. 47에서 본 숫자와 같아요. 면적 단위는 제곱미터, 가격 단위는 만 원이에요." + REAL)

# ---------- part 2 ----------
o = [sec("import")] + head(EB2, "from 패키지.모듈 import 클래스: 서랍에서 설계도를 꺼내요", K2)
o.append(strip_code(96, 200, 1728, 140, [("from ", "#9AA0AB", None), ("sklearn", "#9DC3F2", "im-a"), (".", W_, None), ("linear_model", "#F2C46D", "im-b"), (" import ", "#9AA0AB", None), ("LinearRegression", "#B8E8BE", "im-c")], 50))
IMP = [("sklearn", "패키지", "scikit-learn을 코드에서 부르는 이름", K1), ("linear_model", "모듈 (서랍)", "직선으로 예측하는 모델을 모아 둔 파일", K2), ("LinearRegression", "클래스 (설계도)", "선형 회귀 모델을 만드는 틀. 대문자로 시작해요(24)", GR)]
for i, (a, b, c, col) in enumerate(IMP):
    y = 400 + i * 120
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:96px;top:{y}px;width:1728px;height:104px;display:flex;flex-direction:row;align-items:center;gap:30px;border-bottom:2px solid {LINE}">'
             + p(f"width:420px;flex:none;font-family:{MONO};font-size:34px;font-weight:700;color:{col}", e(a)) + p(f"width:300px;flex:none;font-size:32px;font-weight:700;color:{INK}", e(b))
             + p(f"font-size:28px;color:{SUB}", e(c)) + '</div>')
o.append(f'<div data-build-in="fade order 4" style="position:absolute;left:96px;top:810px;width:1728px;display:flex;flex-direction:row;align-items:center;gap:30px">'
         + p(f"font-size:30px;font-weight:700;color:{GRAY}", "28에서 배운 모양")
         + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:{INK};background:#FFFFFF;border:2px solid {LINE};border-radius:12px;padding:8px 20px", "from cart import Cart")
         + p(f"font-size:30px;color:{SUB}", "점 하나만 더 붙었어요. 패키지 안 모듈이라서예요.") + '</div>')
W("import", o, "첫 줄을 조각으로 나눠 봐요. sklearn은 패키지 이름이에요. 점 뒤의 linear_model은 그 안의 모듈로, 직선으로 예측하는 모델을 모아 둔 서랍이에요. import 뒤의 LinearRegression이 실제로 쓸 클래스, 곧 모델의 설계도예요. 24에서 클래스 이름은 대문자로 시작한다고 배웠죠. 28의 from 모듈 import 이름과 같은 모양이고, 패키지 안의 모듈이라 점이 하나 더 붙었어요. 영어 뜻 그대로 Linear는 직선, Regression은 숫자를 예측하는 일이에요.")

o = [sec("model")] + head(EB2, "model = LinearRegression(): 설계도로 빈 모델 하나를 만들어요", K2)
o.append(strip_code(96, 200, 1728, 130, [("model", "#F2C46D", None), (" = ", W_, None), ("LinearRegression", "#B8E8BE", None), ("()", "#F2A0A0", None)], 50))
o.append(tag(160, 375, "붕어빵 하나 (객체)", "#B26A00", 1, 28, lead=False))
o.append(tag(560, 375, "붕어빵 틀 (클래스)", GR, 1, 28, lead=False))
o.append(tag(868, 420, "괄호 비움 = 기본 설정 그대로", RED, 2, 28, lead=False))
CFS[0] = 28
o += cell({"id": "c-model", "lines": ["model"], "n": 10, "out": ["LinearRegression()"]}, 96, 470, 760, attrs=rise(3))
o.append(note(96 + 105, cbot(470, 1) + 110, 700, "셀 마지막 줄에 객체를 적으면 25의 __repr__ 모양으로 보여요.", GRAY, 24, rise(3)))
MX = 1000
o.append(f'<div id="mdl" data-build-in="rise order 4" style="position:absolute;left:{MX}px;top:470px;width:820px;height:400px;border-radius:24px;border:4px solid {K2};background:#FFFFFF"></div>')
o.append(label(MX + 36, 496, "model 안", K2, 30, rise(4)))
o.append(vbox(MX + 60, 590, 330, 110, "coef_ = ?", "#C9CED8", "#F6F5F1", 34, rise(4), True))
o.append(vbox(MX + 430, 590, 330, 110, "intercept_ = ?", "#C9CED8", "#F6F5F1", 34, rise(4), True))
o.append(note(MX + 60, 740, 700, "아직 아무것도 배우지 않았어요. w와 b 자리가 비어 있어요.", SUB, 28, rise(4)))
W("model", o, "둘째 줄은 설계도로 모델 하나를 만들어요. 24의 붕어빵 비유로 보면 LinearRegression은 틀, model은 그 틀로 찍은 붕어빵이에요. 괄호를 비워 두면 기본 설정 그대로 만들어요. 오늘은 괄호 안에 아무것도 넣지 않아요. 셀 마지막 줄에 model을 적으면 LinearRegression()이라고만 나와요. 25에서 본 __repr__ 모양이에요. 이 순간의 모델은 아직 데이터를 본 적이 없어서 기울기와 절편 자리가 비어 있어요. 이름 끝의 밑줄은 다음 장에서 봐요." + REAL)

o = [sec("xy")] + head(EB2, "X는 대괄호 두 겹으로 표, y는 한 겹으로 한 줄이에요", K2)
CFS[0] = 30
XC = ['X = office[["area"]]', 'y = office["price"]', "print(X.shape, y.shape)"]
o += cell({"id": "c-xy", "lines": XC, "n": 11, "out": ["(200, 1) (200,)"]}, 96, 196, 1100, sel="c-xy")
o.append(tint(1, cx(96, "X = office") - 4, ly(196, 0) - LH() / 2, tw('[["area"]]') + 8, LH(), K1))
o.append(tint(2, cx(96, "y = office") - 4, ly(196, 1) - LH() / 2, tw('["price"]') + 8, LH(), K4))
o.append(tag(cx(96, XC[0]) + 30, ly(196, 0), "열 이름 리스트 → DataFrame", K1, 1, 26))
o.append(tag(cx(96, XC[1]) + 30, ly(196, 1), "열 이름 하나 → Series", K4, 2, 26))
TY = 470
o.append(df("xy-x", 150, TY, ["area"], [("70.307143",), ("48.527099",), ("75.808865",)], [200], fs=30, rh=60, iw=50, attrs=rise(1)))
o.append(p(f"position:absolute;left:150px;top:{TY + 60 * 4 + 10}px;font-family:{MONO};font-size:30px;color:{GRAY}", "⋮", rise(1)))
o.append(label(150, TY + 60 * 4 + 70, "X  (200, 1)  200행 1열 표", K1, 30, rise(1), True))
o.append(mono(760, TY + 10, ["0    38248.214420", "1    25847.194363", "2    39103.989157", "⋮", "Name: price, dtype: float64"], 28, 1.6, INK, rise(2)))
o.append(label(760, TY + 60 * 4 + 70, "y  (200,)  값 200개 한 줄", K4, 30, rise(2), True))
o.append(note(1360, 470, 460, "입력은 열이 여러 개가 될 수 있어서 늘 표로 받아요. 면적, 층수, 역까지 거리처럼요.", INK, 30, fade(3)))
o.append(note(1360, 700, 460, "정답은 언제나 열 하나라 한 줄이에요. 표는 대문자 X, 한 줄은 소문자 y로 쓰는 약속이에요.", SUB, 28, fade(3)))
W("xy", o, "X와 y의 대괄호 개수가 달라요. 45에서 spend 대괄호 안에 열 이름 리스트를 넣으면 표가 나온다고 배웠어요. X는 열 이름 하나짜리 리스트를 넣어서 200행 1열짜리 표, DataFrame이에요. y는 열 이름만 넣어서 값 200개가 한 줄로 늘어선 Series예요. shape로 보면 X는 (200, 1), y는 (200,)이에요. scikit-learn은 입력을 언제나 표로 받아요. 지금은 면적 하나지만 층수나 역까지 거리 같은 열이 늘어날 수 있기 때문이에요. 정답은 늘 하나라 한 줄이에요. 표는 대문자, 한 줄은 소문자로 이름 붙이는 게 머신러닝 코드의 약속이에요." + REAL)

o = [sec("fit")] + head(EB2, "model.fit(X, y): 문제를 먼저, 정답을 나중에 넣어요", K2)
o.append(strip_code(96, 200, 1728, 130, [("model.fit(", W_, None), ("X", "#9DC3F2", None), (", ", W_, None), ("y", "#F2A7CF", None), (")", W_, None)], 54))
o.append(tag(470, 375, "첫째 자리: 문제 (면적 표)", K1, 1, 28, lead=False))
o.append(tag(565, 420, "둘째 자리: 정답 (가격)", K4, 1, 28, lead=False))
FY = 480
o.append(df("fit-x", 110, FY, ["area"], [("70.3",), ("48.5",), ("75.8",), ("⋮",)], [130], fs=30, rh=58, iw=56))
o.append(df("fit-y", 380, FY, ["price"], [("38248",), ("25847",), ("39104",), ("⋮",)], [150], fs=30, rh=58, iw=56))
o.append(label(166, FY + 58 * 5 + 20, "X", K1, 34, "", True))
o.append(label(436, FY + 58 * 5 + 20, "y", K4, 34, "", True))
o.append(arrow(140, K2, WIPE(2), f"position:absolute;left:640px;top:{FY + 130}px"))
MX = 830
o.append(f'<div style="position:absolute;left:{MX}px;top:{FY - 20}px;width:520px;height:340px;border-radius:24px;border:4px solid {K2};background:#FFFFFF"></div>')
o.append(label(MX + 30, FY + 4, "model", K2, 30, "", True))
o.append(p(f"position:absolute;left:{MX + 30}px;top:{FY + 70}px;width:460px;font-size:28px;line-height:1.5;color:{SUB}", "선을 조금씩 바꿔 보며 오차가 가장 작은 w와 b를 계산해요", rise(2)))
o.append(vbox(MX + 30, FY + 190, 220, 100, "w = ?", "#C9CED8", "#F6F5F1", 32, "", True))
o.append(vbox(MX + 270, FY + 190, 220, 100, "b = ?", "#C9CED8", "#F6F5F1", 32, "", True))
o.append(vbox(MX + 30, FY + 190, 220, 100, "465.67", K2, K2BG, 34, rise(3)))
o.append(vbox(MX + 270, FY + 190, 220, 100, "4727.98", K3, K3BG, 34, rise(3) + DELAY(150)))
o.append(note(1420, FY - 10, 400, "fit은 '맞추다'예요. 점들에 선을 맞춰요.", INK, 30, fade(4)))
o.append(note(1420, FY + 150, 400, "순서를 바꿔 fit(y, X)로 쓰면 오류가 나요. 정답이 한 줄이어야 해서예요.", SUB, 26, fade(4)))
W("fit", o, "fit이 학습하는 함수예요. 영어로 맞추다라는 뜻이라 점들에 직선을 맞춘다고 기억해요. 괄호 안 순서가 정해져 있어요. 첫째 자리에 문제 X, 둘째 자리에 정답 y를 넣어요. 20에서 배운 위치 인자라서 이름 없이 순서로 짝이 정해져요. 바꿔 적으면 첫째 자리에 한 줄이 들어가서 오류가 나요. 5파트에서 그 오류 메시지를 봐요. fit을 실행하면 모델이 안에서 직선을 조금씩 바꿔 보며 오차가 가장 작은 w와 b를 계산해서 자기 안에 저장해요. 빈칸이었던 자리에 465.67과 4727.98이 들어가요. 표의 숫자는 office.head()의 앞 세 줄을 줄여 적었어요.")

o = [sec("best")] + head(EB2, "가장 잘 맞는 직선은 오차를 제곱해서 더한 값이 가장 작은 선이에요", K2)
idx = [51, 31, 4, 99, 1, 64, 2, 120, 60, 7]
pts = [(AREA[i], PRICE[i]) for i in idx if i not in SPECIAL][:8]
def resid_plot(left, title, w_, b_, color, order0):
    P = Plot(left, 300, 720, 500, (15, 90), (5000, 50000))
    out = P.axes("면적", "가격", (), (), 22)
    sq = ""
    tot = 0
    for x, y in pts:
        yp = w_ * x + b_
        d = abs(P.Y(y) - P.Y(yp))
        tot += (y - yp) ** 2
        top = min(P.Y(y), P.Y(yp))
        sq += f'<rect x="{P.X(x):.1f}" y="{top:.1f}" width="{d:.1f}" height="{d:.1f}" fill="{color}" fill-opacity="0.16" stroke="{color}" stroke-width="2"/>'
    out.append(P.svg(P.line(w_, b_, color, 5)))
    out.append(P.svg(sq, fade(order0)))
    out.append(P.svg("".join(f'<line x1="{P.X(x):.1f}" y1="{P.Y(y):.1f}" x2="{P.X(x):.1f}" y2="{P.Y(w_ * x + b_):.1f}" stroke="{color}" stroke-width="3"/>' for x, y in pts), WIPE(order0)))
    out.append(P.svg(P.dots([x for x, _ in pts], [y for _, y in pts], INK, 9, 0.85)))
    out.append(label(left, 230, title, color, 32))
    return out, tot
a1, t1 = resid_plot(150, "손으로 그은 선 (가)", 340, 12000, GRAY, 1)
a2, t2 = resid_plot(1050, "모델의 선", WFIT, BFIT, RED, 2)
o += a1 + a2
o.append(label(150, 870, f"네모 넓이 합 {t1 / 1e4:,.0f}만", GRAY, 30, fade(1)))
o.append(label(1050, 870, f"네모 넓이 합 {t2 / 1e4:,.0f}만", RED, 30, fade(2)))
o.append(caption("점과 선의 거리(오차)로 그린 네모의 넓이 합이 가장 작은 w와 b를 fit이 찾아요.", 950, 3))
W("best", o, "가장 잘 맞는다는 기준을 그림으로 봐요. 점마다 직선까지 세로로 잰 거리가 오차예요. 오차를 한 변으로 하는 네모를 그리면 그 넓이가 오차의 제곱이에요. 왼쪽은 1파트의 가 선이고, 오른쪽은 모델의 선이에요. 같은 점 8개에서 네모 넓이를 모두 더하면 모델의 선이 훨씬 작아요. 선형 회귀의 fit은 이 넓이 합이 가장 작아지는 w와 b를 계산해요. 제곱을 쓰는 이유는 위로 틀린 것과 아래로 틀린 것이 서로 지워지지 않게 하려는 거예요. 점 8개는 office.csv에서 골랐고 넓이 합은 이 그림을 그리면서 계산한 값이에요.")

o = [sec("coef")] + head(EB2, "coef_와 intercept_: 끝에 밑줄이 붙은 이름은 fit으로 배운 값이에요", K2)
CFS[0] = 30
o += cell({"id": "c-coef", "lines": ["model.coef_"], "n": 15, "out": ["array([465.67355712])"]}, 96, 200, 820, sel="c-coef")
o += cell({"id": "c-int", "lines": ["model.intercept_"], "n": 16, "out": ["np.float64(4727.983834181516)"]}, 96, 420, 820)
o.append(tag(cx(96, "array([465.67355712])", True) + 30, oy(200, 1, 0), "배열 (열마다 하나)", K2, 1, 26))
o.append(tag(cx(96, "np.float64(4727.983834181516)", True) + 20, oy(420, 1, 0), "숫자 하나", K3, 2, 26))
o.append(note(96 + 105, 640, 760, "열이 area 하나라 coef_도 하나예요. 그래서 수업 셀은 [0]을 붙여 숫자만 꺼냈어요.", INK, 28, fade(3)))
CX = 1000
o += plain_rows(CX, 210, 824, [("기울기 w", "465.67", "450"), ("절편 b", "4,727.98", "5,000")], [260, 260, 220], 4, 110, ["", "모델이 찾음", "47의 정답"], 36, mono_cols=(1, 2))
o.append(note(CX, 500, 824, "가깝지만 똑같지 않은 까닭", INK, 32, fade(5)))
o.append(note(CX, 560, 824, "47에서 가격에 ±2,500쯤 흔들림을 더했고, 특이 매물 5건은 1만 5천~2만 5천을 더 올렸어요. 모델은 흔들린 점들만 보고 선을 그어요.", SUB, 28, fade(5)))
o.append(note(CX, 760, 824, "특이 매물을 빼고 다시 학습하면 어떻게 될지는 6파트에서 봐요.", GRAY, 26, fade(5)))
W("coef", o, "fit이 끝나면 모델 안에 배운 값이 생겨요. coef_가 기울기, intercept_가 절편이에요. 이름 끝의 밑줄은 scikit-learn의 약속으로, fit을 한 뒤에 생기는 값이라는 표시예요. coef_는 배열로 나와요. 입력 열마다 기울기가 하나씩 있어서 열이 여러 개면 숫자도 여러 개가 돼요. 오늘은 열이 area 하나라 하나뿐이고, 그래서 수업 셀에서 [0]으로 꺼냈어요. intercept_는 숫자 하나예요. 찾은 값은 465.67과 4727.98로 정답 450, 5000과 조금 달라요. 47에서 가격에 흔들림과 특이 매물을 섞었기 때문이에요." + REAL)

o = [sec("predict")] + head(EB2, "model.predict(new): 학습 때와 같은 열 이름의 표를 넣어요", K2)
CFS[0] = 30
PC = ['new = pd.DataFrame({"area": [33, 59]})', "model.predict(new).round(-1)"]
o += cell({"id": "c-pred", "lines": PC, "n": 5, "out": ["array([20100., 32200.])"]}, 96, 196, 860, sel="c-pred")
o.append(tint(1, cx(96, 'new = pd.DataFrame({') - 4, ly(196, 0) - LH() / 2, tw('"area"') + 8, LH(), K1))
o.append(tag(96 + 860 + 24, ly(196, 0), "X와 같은 열 이름 area", K1, 1, 26))
o.append(tag(96 + 860 + 24, ly(196, 1), "47의 round(-1): 십의 자리까지", GRAY, 2, 24))
o.append(df("pr-new", 96 + 105, 420, ["area"], [("33",), ("59",)], [140], fs=30, rh=60, iw=40, attrs=rise(1)))
o.append(label(96 + 105, 620, "new  (2, 1)", K1, 28, rise(1), True))
# the calculation, left to right
CY = 720
STEPS = [("33", INK), ("× 465.67", K2), ("+ 4727.98", K3), ("= 20,095.2", INK), ("→ 20,100", GR)]
xx = 96
for k, (t_, c_) in enumerate(STEPS):
    wbox = int(tw(t_, 36) + 50)
    o.append(p(f"position:absolute;left:{xx}px;top:{CY}px;height:84px;padding:0 24px;border-radius:14px;border:3px solid {c_};background:#FFFFFF;font-family:{MONO};font-size:36px;font-weight:700;line-height:78px;color:{c_};white-space:pre", e(t_), rise(3) + DELAY(k * 140)))
    xx += wbox + 30
o.append(note(96, CY + 110, 1728, "predict는 넣은 행마다 w × 면적 + b를 계산해요. 59㎡는 32,202.7이고 반올림해서 32,200이에요.", SUB, 28, fade(4)))
RX = 1180
o.append(note(RX, 420, 640, "왜 숫자 33이 아니라 표일까요?", INK, 32, fade(2)))
o.append(note(RX, 480, 640, "fit에 표 X를 넣었으니 predict에도 같은 모양의 표를 넣어요. 열 이름도 같아야 모델이 어느 열인지 알아봐요.", SUB, 28, fade(2)))
W("predict", o, "학습한 모델로 처음 보는 면적의 가격을 예측해요. 33제곱미터와 59제곱미터예요. predict에는 숫자를 바로 넣지 않고 표를 넣어요. fit에 X라는 표를 넣었으니 같은 모양으로 넣어야 해요. 열 이름도 학습 때와 같은 area로 맞춰요. 딕셔너리 키가 열 이름이 된다는 건 45에서 배웠어요. predict는 행마다 기울기 곱하기 면적 더하기 절편을 계산해서 돌려줘요. 33은 20,095.2가 나오고 47의 round(-1)로 십의 자리까지 반올림하면 20,100이에요. 계산 줄의 소수 값은 model.predict(new)를 반올림 없이 찍은 결과로 맞췄어요." + REAL)

o = [sec("ypred")] + head(EB2, "predict(X)로 예측한 200건을 정답 옆에 놓아 봐요", K2)
CFS[0] = 26
YC = ["errors = y - y_pred", 'table = pd.DataFrame({"정답": y, "예측": y_pred, "오차": errors}).round(0)', "table.head()"]
o += cell({"id": "c-len", "lines": ["print(len(y_pred))", "print(y_pred[:3])"], "n": 20, "out": ["200", "[37468.16127849 27325.77044835 40030.16756398]"]}, 96, 196, 1000)
o.append(tag(cx(96, "[37468.16127849 27325.77044835 40030.16756398]", True) + 30, oy(196, 2, 1), "예측 200개 (NumPy 배열)", K2, 1, 24))
YT = cbot(196, 2) + 2 * (LH() + 10) + 40
o += cell({"id": "c-yp", "lines": YC, "n": 22, "out": []}, 96, YT, 1300, sel="c-yp")
o.append(tag(cx(96, YC[0]) + 30, ly(YT, 0), "정답 - 예측, 줄마다 빼기", K4, 2, 24))
TV = [("38248.0", "37468.0", "780.0"), ("25847.0", "27326.0", "-1479.0"), ("39104.0", "40030.0", "-926.0"), ("33988.0", "35150.0", "-1162.0"), ("17595.0", "16892.0", "703.0")]
TT = cbot(YT, 3) + 30
o.append(df("yp-t", 96 + 105, TT, ["정답", "예측", "오차"], TV, [210, 210, 210], fs=30, rh=62, iw=50, attrs=rise(3),
            cs={(i, 2): f"color:{GR if float(r[2]) > 0 else RED};font-weight:700" for i, r in enumerate(TV)}))
RX = 1060
o.append(note(RX, TT + 10, 760, "오차가 +면 실제가 예측보다 비싸요(선 위의 점).", GR, 28, fade(4)))
o.append(note(RX, TT + 100, 760, "오차가 -면 실제가 예측보다 싸요(선 아래의 점).", RED, 28, fade(4)))
o.append(note(RX, TT + 210, 760, "y_pred는 3파트 채점에서 계속 써요.", SUB, 28, fade(5)))
W("ypred", o, "앞 장 그래프 셀의 첫 줄에서 학습에 쓴 면적 200개를 모두 predict에 넣었어요. X가 표라서 그대로 넣으면 돼요. 결과 y_pred는 예측 가격 200개가 든 NumPy 배열이에요. 정답 y에서 y_pred를 빼면 줄마다 오차가 나와요. 45에서 배운 칸마다 계산이에요. 셋을 한 표로 보면 첫 줄은 실제 38,248, 예측 37,468이라 780만 원 더 비싸요. 오차가 플러스면 점이 선 위에, 마이너스면 선 아래에 있어요. 수업 노트북에는 오차 표가 없어요. 이해를 도우려고 더한 셀이에요." + REAL)

o = [sec("draw")] + head(EB2, "직선 그리기: 면적 순서로 정렬한 뒤 plot으로 이어요", K2)
CFS[0] = 20
o += cell({"id": "c-draw", "lines": DRAWC, "n": 6}, 96, 190, 1060, sel="c-draw")
o.append(lspot(1, 96 + 87, 190, 1060 - 87, 10 + 13 * LH() + 8, 190 + 10 + 2 * LH(), 2 * LH(), bar=K2))
o.append(lspot(2, 96 + 87, 190, 1060 - 87, 10 + 13 * LH() + 8, 190 + 10 + 7 * LH(), LH(), bar=RED))
o.append(lspot_off(3))
o.append(mono(96 + 105, cbot(190, 13) + 30, ["line.head(3)", "          area", "51   20.478548", "149  21.404785", "84   21.476285"], 24, 1.45, INK, rise(1)))
o.append(tag(96 + 105 + 24 * 0.6 * 16 + 30, cbot(190, 13) + 30 + 24 * 1.45 * 3.5, "작은 면적부터 줄 세웠어요", K2, 1, 24))
o.append(img(1190, 196, 634, "main-1.png", rise(2), "dr-img"))
o.append(note(1190, 196 + 634 * 939 / 1423 + 30, 634, "plot은 넣은 순서대로 점을 이어요. 그래서 왼쪽에서 오른쪽으로 줄을 세워 넣어요.", INK, 28, fade(3)))
W("draw", o, "모델의 직선을 산점도 위에 그려요. plot은 넣은 순서대로 점을 이어서 선을 그려요. 그래서 sort_values로 면적이 작은 것부터 줄을 세운 line을 만들고, 그 순서대로 예측한 line_pred를 이어요. line.head로 보면 번호가 51, 149, 84처럼 섞여 있어도 면적은 작은 것부터예요. 예측값은 모두 한 직선 위에 있어서 정렬하지 않아도 같은 선이 그려지긴 해요. 그래도 47의 오류 장처럼 점을 순서 없이 이으면 엉키는 경우가 많아서, 선을 그릴 때는 정렬하는 습관을 들여요. scatter의 alpha와 label, legend는 47에서 배웠어요." + REAL + IMGN)

# ---------- part 3 ----------
o = [sec("errors")] + head(EB3, "오차를 그냥 더하면 0이 돼요. +와 -가 서로 지워져서예요", K3)
EI = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
EV = [ERR[i] for i in EI]
BX, BY, BH, BWID = 200, 480, 520, 90
SCL = 0.05
o.append(f'<div style="position:absolute;left:{BX - 20}px;top:{BY}px;width:{len(EI) * (BWID + 18) + 20}px;height:3px;background:{INK}"></div>')
for k, v in enumerate(EV):
    hgt = abs(v) * SCL
    x = BX + k * (BWID + 18)
    y = BY - hgt if v > 0 else BY + 3
    o.append(bar(x, y, BWID, hgt, GR if v > 0 else RED, WIPE(1) + DELAY(k * 60), 6))
    o.append(p(f"position:absolute;left:{x - 20}px;top:{(y - 40) if v > 0 else (y + hgt + 6):.0f}px;width:{BWID + 40}px;text-align:center;font-family:{MONO};font-size:22px;font-weight:700;color:{GR if v > 0 else RED}", f"{v:+,.0f}", fade(1) + DELAY(k * 60)))
o.append(label(BX - 20, 230, "앞 10줄의 오차 (만 원)", SUB, 26))
o.append(label(BX + 10 * (BWID + 18) + 10, BY - 20, "0", INK, 28))
CFS[0] = 26
o += cell({"id": "c-esum", "lines": ['print("오차 합:", errors.sum().round(6))'], "n": 23, "out": ["오차 합: 0.0"]}, 96, 850, 1000, attrs=rise(2))
o.append(note(1330, 400, 494, "그래서 오차를 숫자 하나로 줄일 때는 부호를 없애요. 절댓값으로 없애면 MAE, 제곱으로 없애면 MSE예요.", INK, 30, fade(3)))
W("errors", o, "모델이 얼마나 잘 맞혔는지 점수 하나로 말하고 싶어요. 오차 200개를 그냥 더하면 어떨까요? 초록 막대처럼 실제가 더 비싼 줄은 플러스, 빨간 막대처럼 싼 줄은 마이너스라 서로 지워져요. 200개를 다 더하면 0이 나와요. 선형 회귀는 오차 합이 0이 되도록 선을 그어서 늘 그래요. 그래서 점수를 낼 때는 먼저 부호를 없애요. 절댓값으로 없애는 방법이 MAE, 제곱으로 없애는 방법이 MSE예요. 막대는 office.csv에서 계산한 앞 10줄의 오차예요." + REAL)

o = [sec("mae")] + head(EB3, "MAE: 오차의 절댓값을 평균 내요. 평균 2,510만 원쯤 틀려요", K3)
o.append(strip_code(96, 200, 1728, 120, [("MAE", "#8FD8DE", None), (" = 평균( ", W_, None), ("|정답 - 예측|", "#F2C46D", None), (" )", W_, None)], 46))
AB = [abs(v) for v in EV]
BY2 = 700
SC3 = 0.055
for k, v in enumerate(EV):
    hgt = abs(v) * SC3
    x = 220 + k * (BWID + 18)
    o.append(bar(x, BY2 - hgt, BWID, hgt, K3, "", 6))
    o.append(p(f"position:absolute;left:{x - 20}px;top:{BY2 - hgt - 40:.0f}px;width:{BWID + 40}px;text-align:center;font-family:{MONO};font-size:22px;font-weight:700;color:{K3}", f"{abs(v):,.0f}"))
o.append(f'<div style="position:absolute;left:200px;top:{BY2}px;width:{10 * (BWID + 18) + 20}px;height:3px;background:{INK}"></div>')
o.append(f'<div{WIPE(1)} style="position:absolute;left:200px;top:{BY2 - 2510 * SC3:.0f}px;width:{10 * (BWID + 18) + 20}px;height:0;border-top:4px dashed {INK}"></div>')
o.append(label(200 + 10 * (BWID + 18) + 20, BY2 - 2510 * SC3 - 20, "평균", INK, 28, fade(1)))
CFS[0] = 26
MC = ['print("오차 절댓값 평균:", errors.abs().mean())']
o += cell({"id": "c-mae", "lines": MC, "n": 24, "out": ["오차 절댓값 평균: 2510.4045478767703"]}, 96, 760, 1100, attrs=rise(2))
o.append(note(96 + 105, 930, 1000, "채점 셀의 mean_absolute_error(y, y_pred)도 2,510이에요.", SUB, 26, rise(2)))
o.append(p(f"position:absolute;left:1460px;top:440px;font-family:{MONO};font-size:110px;font-weight:900;line-height:1.2;color:{K3}", "2,510", ' id="mae-big"' + COUNT(3)))
o.append(label(1460, 590, "만 원 (가격과 같은 단위)", K3, 30, fade(3)))
W("mae", o, "MAE는 오차에서 부호를 떼고 평균을 낸 값이에요. 영어 Mean Absolute Error의 첫 글자예요. 막대를 모두 위로 세운 뒤 높이의 평균을 구한다고 생각하면 돼요. 200건의 평균은 2,510이에요. 가격 단위가 만 원이니 이 모델은 평균 2,510만 원쯤 틀린다고 읽어요. 단위가 가격과 같아서 넷 중 가장 읽기 쉬워요. mean_absolute_error 함수의 값과, abs로 부호를 떼고 mean으로 평균을 내서 직접 계산한 값이 같아요. 직접 계산한 셀은 이해를 도우려고 따로 실행했어요." + REAL)

o = [sec("rmse")] + head(EB3, "MSE는 제곱의 평균, RMSE는 그 제곱근이에요. 큰 오차가 크게 보여요", K3)
o += plain_rows(96, 210, 1728, [("MSE", "평균( (정답 - 예측)² )", "17,697,259", "만 원² (읽기 어려워요)"), ("RMSE", "√ MSE", "4,207", "만 원")], [200, 560, 400, 500], 1, 100, ["", "계산", "오늘 값", "단위"], 34, mono_cols=(0, 1, 2))
SQ = sorted([(abs(ERR[i]), i) for i in range(200)], reverse=True)
o.append(label(96, 470, "오차 제곱이 큰 순서로 30줄", SUB, 26, fade(2)))
BX3, BY3 = 96, 900
mx = SQ[0][0] ** 2
for k, (v, i) in enumerate(SQ[:30]):
    hgt = v ** 2 / mx * 380
    col = "#E08A00" if i in SPECIAL else "#9AA0AB"
    o.append(bar(BX3 + k * 44, BY3 - hgt, 34, hgt, col, WIPE(2) + DELAY(k * 25), 4))
o.append(f'<div style="position:absolute;left:{BX3}px;top:{BY3}px;width:{30 * 44}px;height:3px;background:{INK}"></div>')
o.append(tag(BX3 + 5 * 44 + 10, BY3 - 200, "특이 매물 5건", "#B26A00", 3, 28, lead=False))
o.append(note(1500, 520, 330, "제곱하면 2만은 4억, 2천은 4백만이에요. 큰 오차가 100배로 커져요.", INK, 28, fade(3)))
o.append(note(1500, 740, 330, "그래서 RMSE(4,207)가 MAE(2,510)보다 커요.", K3, 28, fade(4)))
W("rmse", o, "MSE는 오차를 제곱해서 평균 낸 값이에요. 17,697,259가 나왔는데 단위가 만 원의 제곱이라 그대로는 읽기 어려워요. 그래서 제곱근을 씌워 단위를 가격으로 되돌린 값이 RMSE이고, 4,207이에요. 제곱하면 큰 오차가 훨씬 커져요. 오차 2만은 제곱하면 4억이고, 2천은 4백만이라 100배 차이가 나요. 아래 막대는 오차 제곱이 큰 줄부터 30개를 세운 그림이에요. 앞의 주황 막대 다섯 개가 47에서 넣은 특이 매물이에요. 이 다섯 줄이 RMSE를 MAE보다 크게 끌어올려요. 막대는 office.csv에서 계산했어요." + REAL)

o = [sec("r2")] + head(EB3, "R²: 평균 하나만 찍을 때보다 오차를 얼마나 줄였나예요", K3)
PA = Plot(170, 300, 680, 430, (15, 90), (5000, 70000))
PB = Plot(1070, 300, 680, 430, (15, 90), (5000, 70000))
for P, tl, c in ((PA, "평균만 찍기: 모든 매물을 28,990으로", GRAY), (PB, "모델의 직선", RED)):
    o += P.axes("면적", "가격", (), (), 22)
    o.append(P.svg(P.dots(AREA, PRICE, K1, 5, 0.35)))
    o.append(label(P.l, 230, tl, c, 30))
o.append(PA.svg(PA.line(0, PRICE.mean(), GRAY, 5)))
o.append(PB.svg(PB.line(WFIT, BFIT, RED, 5)))
o.append(label(PA.l, 790, "R² = 0", GRAY, 40, rise(1), True))
o.append(label(PB.l, 790, "R² = 0.80", RED, 40, rise(2), True))
o.append(note(PB.l + 300, 798, 440, "평균만 찍을 때 오차(제곱 합)의 80%를 줄였어요", SUB, 26, rise(2)))
o.append(caption("1이면 모든 점이 선 위, 0이면 평균만 찍은 것과 같아요. 평균보다 못하면 마이너스도 나와요.", 940, 3))
W("r2", o, "R제곱은 기준과 비교한 점수예요. 기준은 면적을 아예 안 보고 모든 매물을 평균 가격 28,990으로 찍는 방법이에요. 왼쪽 회색 선이에요. 이 방법의 R제곱이 0이에요. 모델의 직선은 그 기준의 오차 제곱 합을 80퍼센트 줄여서 0.80이에요. 모든 점이 선 위에 있으면 1이에요. 거꾸로 평균만 찍는 것보다 못하면 마이너스가 나와요. 5파트에서 실제로 마이너스가 나오는 장면을 봐요. 단위가 없는 점수라 다른 데이터의 모델과도 비교할 수 있어요. 평균만 찍은 R제곱 0과 0.804는 따로 셀을 실행해서 확인했어요." + REAL)

o = [sec("metrics")] + head(EB3, "채점 함수는 모두 (정답, 예측) 순서로 넣어요", K3)
o.append(strip_code(96, 200, 1728, 130, [("mean_absolute_error(", W_, None), ("y", "#F2A7CF", None), (", ", W_, None), ("y_pred", "#F2C46D", None), (")", W_, None)], 50))
o.append(tag(745, 375, "첫째: 정답 (y_true)", K4, 1, 28, lead=False))
o.append(tag(838, 420, "둘째: 예측 (y_pred)", OR, 1, 28, lead=False))
CFS[0] = 26
OC = ['print("MAE", mean_absolute_error(y, y_pred), mean_absolute_error(y_pred, y))', 'print("R2 ", r2_score(y, y_pred), r2_score(y_pred, y))']
o += cell({"id": "c-ord", "lines": OC, "n": 7, "out": ["MAE 2510.4045478767703 2510.4045478767703", "R2  0.8041321769128468 0.7564233484113125"]}, 96, 500, 1400, attrs=rise(2))
o.append(box(3, cx(96, "R2  0.8041321769128468 ", True) - 8, oy(500, 2, 1) - LH() / 2 - 4, tw("0.7564233484113125") + 16, LH() + 8, RED, 4))
o.append(note(96 + 105, 760, 1600, "MAE, MSE, RMSE는 순서를 바꿔도 같지만 R²는 달라져요. 오류가 안 나서 틀린 줄 모르니 늘 정답부터 적어요.", INK, 30, fade(3)))
o.append(note(96 + 105, 860, 1600, "import 줄 하나에 쉼표로 넷을 불러와요(28). 수업 셀의 :,.0f는 13에서 배운 천 단위 쉼표와 소수 0자리예요.", SUB, 26, fade(4)))
W("metrics", o, "채점 함수 넷은 괄호 안 순서가 같아요. 첫째 자리에 정답 y, 둘째 자리에 예측 y_pred를 넣어요. scikit-learn 설명서에도 y_true, y_pred 순서로 적혀 있어요. 순서를 바꾸면 어떻게 될까요? 이 셀은 일부러 바꿔서 둘을 나란히 찍었어요. MAE는 절댓값이라 같지만, R제곱은 0.804가 0.756으로 바뀌어요. 오류 메시지가 없어서 틀린 줄도 모르게 돼요. 그러니 늘 정답부터 적어요. 수업 셀의 콜론 쉼표 점 0 f는 13에서 배운 천 단위 쉼표와 소수점 아래 0자리 포맷이에요." + REAL)

o = [sec("compare4")] + head(EB3, "점수 넷 한눈에: 작을수록 좋은 셋과 클수록 좋은 하나", K3)
C4 = [("MAE", "|오차|의 평균", "2,510", "만 원", "작을수록 좋아요", "평균 얼마나 틀리나"), ("MSE", "오차²의 평균", "17,697,259", "만 원²", "작을수록 좋아요", "모델끼리 비교할 때"),
      ("RMSE", "√MSE", "4,207", "만 원", "작을수록 좋아요", "큰 실수를 더 크게 볼 때"), ("R²", "1 - 모델 오차 / 평균 오차", "0.80", "없음", "1에 가까울수록 좋아요", "데이터가 달라도 비교")]
o += plain_rows(96, 220, 1728, C4, [150, 440, 270, 140, 330, 300], 1, 118, ["점수", "계산", "오늘 값", "단위", "좋은 방향", "언제 봐요"], 30, mono_cols=(0, 2))
o.append(caption("보통 MAE로 '얼마나 틀리나'를 말하고, R²로 '얼마나 설명하나'를 함께 적어요.", 900, 5))
W("compare4", o, "오늘 본 점수 넷을 한 표로 모았어요. MAE, MSE, RMSE는 오차를 재는 점수라 작을수록 좋아요. R제곱만 클수록 좋고 1이 가장 좋아요. 단위도 달라요. MAE와 RMSE는 가격과 같은 만 원이고, MSE는 만 원의 제곱, R제곱은 단위가 없어요. 사람에게 설명할 때는 MAE가 편해요. 평균 2,510만 원쯤 틀린다고 말할 수 있으니까요. RMSE가 MAE보다 많이 크면 크게 틀린 줄이 섞여 있다는 신호예요. 오늘도 4,207과 2,510으로 차이가 커요.")

# ---------- part 4 ----------
o = [sec("mask")] + head(EB4, "np.ones로 True 200개를 만들고 특이 매물만 False로", K4)
CFS[0] = 26
o += cell({"id": "c-norm", "lines": NORMC, "n": 8, "out": ["특이 매물: [17, 134, 178, 172, 122]", "정상 매물: 195"]}, 96, 196, 1000, sel="c-norm")
o.append(tag(cx(96, NORMC[0]) + 30, ly(196, 0), "47에서 뽑힌 번호", K4, 1, 24))
o.append(lspot(1, 96 + 87, 196, 1000 - 87, 10 + 6 * LH() + 8, 196 + 10 + 2 * LH(), LH(), bar=K4))
o.append(lspot(3, 96 + 87, 196, 1000 - 87, 10 + 6 * LH() + 8, 196 + 10 + 3 * LH(), LH(), bar=K4))
o.append(lspot_off(4))
AX = 1150
ARGS = [("len(office)", "몇 개: 행 수 200", K1), ("dtype=bool", "1.0 대신 True로 채워요", K4)]
for k, (a, b) in enumerate([(x[0], x[1]) for x in ARGS]):
    o.append(p(f"position:absolute;left:{AX}px;top:{210 + k * 80}px;font-family:{MONO};font-size:30px;font-weight:700;color:{ARGS[k][2]}", e(a), rise(2)))
    o.append(p(f"position:absolute;left:{AX + 260}px;top:{214 + k * 80}px;font-size:26px;color:{SUB}", e(b), rise(2)))
# boxes 14..19
BXS = 1150
for k, i in enumerate(range(14, 20)):
    x = BXS + k * 110
    val = "False" if i == 17 else "True"
    o.append(p(f"position:absolute;left:{x}px;top:430px;width:96px;text-align:center;font-family:{MONO};font-size:22px;color:{GRAY}", f"[{i}]"))
    if i == 17:
        o.append(p(f"position:absolute;left:{x}px;top:470px;width:96px;height:72px;border-radius:12px;border:3px solid {RED};background:{K5BG};font-family:{MONO};font-size:22px;font-weight:700;line-height:66px;text-align:center;color:{RED}", "False", ' id="m17" data-start="True"'))
    else:
        o.append(p(f"position:absolute;left:{x}px;top:470px;width:96px;height:72px;border-radius:12px;border:3px solid {GR};background:{GRBG};font-family:{MONO};font-size:22px;font-weight:700;line-height:66px;text-align:center;color:{GR}", "True"))
o.append(text(3, "m17", "False"))
o.append(label(BXS, 570, "normal의 14~19번 칸", SUB, 24))
CFS[0] = 26
o += cell({"id": "c-n1420", "lines": ["print(normal[14:20])"], "n": 28, "out": ["[ True  True  True False  True  True]"]}, 1060, 650, 760, attrs=rise(4))
o.append(note(96 + 105, cbot(196, 6) + 2 * (LH() + 10) + 50, 860, "대괄호에 번호 리스트를 넣으면 그 칸들을 한 번에 바꿔요. 17, 134, 178, 172, 122번 다섯 칸이 False가 돼요.", INK, 28, fade(4)))
o.append(note(96 + 105, cbot(196, 6) + 2 * (LH() + 10) + 190, 860, "sum()은 True를 1로 세서 195가 나와요.", GRAY, 26, fade(4)))
W("mask", o, "특이 매물을 뺀 성적도 보고 싶어요. 먼저 47에서 뽑힌 특이 매물 번호 다섯 개를 리스트로 적어요. np.ones는 1로 채운 배열을 만드는 함수예요. 첫째 자리는 개수로, len(office)라서 200이에요. dtype은 칸에 담을 값의 종류인데 bool로 정하면 1 대신 True로 채워요. 그러면 True 200개짜리 배열이 돼요. 다음 줄에서 normal 대괄호 안에 번호 리스트를 넣고 False를 넣으면 그 다섯 칸만 False로 바뀌어요. 오른쪽은 14번부터 19번 칸이에요. 17번만 False예요. sum은 True를 1, False를 0으로 세서 195가 나와요." + REAL)

o = [sec("cases")] + head(EB4, "특이 매물 5건을 빼고 채점하면 R²가 0.80에서 0.92로 올라요", K4)
CFS[0] = 22
o += cell({"id": "c-case", "lines": CASEC, "n": 9, "out": CASEO}, 96, 190, 1180, sel="c-case")
o.append(run(1, 96 + 87, 190 + 10 + 3 * LH(), 1180 - 89, LH()))
o.append(run(2, 96 + 87, 190 + 10 + 4 * LH(), 1180 - 89, 2 * LH()))
o.append(run_off(3))
o.append(tag(cx(96, CASEC[4]) + 30, ly(190, 4), "mask가 True인 줄만 남겨요 (45의 arr[조건])", K4, 2, 22))
o.append(tag(cx(96, CASEC[3]) + 30, ly(190, 3), "두 번 돌아요: 전체, 그다음 195건", GR, 1, 22))
RX = 1380
SC2 = [("MAE", "2,510", "2,033"), ("RMSE", "4,207", "2,567"), ("R²", "0.80", "0.92")]
for k, (nm, a, b) in enumerate(SC2):
    y = 230 + k * 190
    o.append(label(RX, y, nm, K3, 30, rise(3), True))
    o.append(p(f"position:absolute;left:{RX}px;top:{y + 50}px;font-family:{MONO};font-size:{60 if nm == 'R²' else 44}px;font-weight:900;color:{GRAY}", e(a), rise(3)))
    o.append(p(f"position:absolute;left:{RX + 200}px;top:{y + 50}px;font-family:{MONO};font-size:{60 if nm == 'R²' else 44}px;font-weight:900;color:{K4 if nm == 'R²' else INK}", "→ " + e(b), rise(3) + DELAY(150), ))
o.append(note(RX, 820, 440, "RMSE가 가장 많이 줄었어요. 큰 오차 5개가 빠져서예요.", SUB, 26, fade(4)))
W("cases", o, "수업 셀은 같은 채점을 두 번 해요. cases는 이름과 마스크를 묶은 튜플 두 개의 리스트예요. for 문이 한 번은 전체 200건, 한 번은 특이 매물을 뺀 195건으로 돌아요. y 대괄호 마스크는 45에서 배운 조건으로 고르기와 같아서 True인 줄만 남겨요. 결과를 보면 특이 매물 다섯 건만 빼도 MAE는 2,510에서 2,033으로, RMSE는 4,207에서 2,567로 줄고, R제곱은 0.80에서 0.92로 올라요. 큰 오차에 민감한 RMSE가 가장 많이 줄었어요. 단, 이 모델은 특이 매물까지 넣고 배운 모델이에요. 빼고 다시 배우는 건 6파트에서 해요. 수업 셀은 둘째 줄에 special을 적었는데 normal이 맞아요. 5파트에서 다뤄요." + REAL)

o = [sec("corr")] + head(EB4, "47의 상관계수를 제곱하면 오늘의 R²와 같아요", K4)
CFS[0] = 28
CC = ['print("상관계수:", office["area"].corr(office["price"]))', 'print("상관계수 제곱:", office["area"].corr(office["price"]) ** 2)']
o += cell({"id": "c-corr", "lines": CC, "n": 27, "out": ["상관계수: 0.8967341729369117", "상관계수 제곱: 0.8041321769128471"]}, 96, 196, 1300, sel="c-corr")
o.append(underline(1, cx(96, "상관계수 제곱: ", True), cx(96, "상관계수 제곱: 0.8041321", True), oy(196, 2, 1) + LH() / 2 + 2, K4, 5))
o += plain_rows(96, 520, 1728, [("상관계수 (47)", "두 열이 같이 오르내리는 정도", "-1 ~ 1", "0.90"), ("R² (48)", "모델이 정답을 설명하는 정도", "0 ~ 1 (못하면 마이너스)", "0.80")], [330, 560, 470, 200], 2, 110, ["", "무엇을 재요", "범위", "오늘"], 32, mono_cols=(3,))
o.append(caption("열 하나로 그은 직선일 때만 이렇게 같아요. 상관계수가 0에 가까우면 R²도 0에 가까워요.", 900, 3))
W("corr", o, "47에서 office의 상관계수가 0.90이라고 봤어요. 그 값을 제곱하면 0.804로 오늘 R제곱과 같아요. 입력 열이 하나뿐인 직선 모델에서는 늘 이렇게 같아요. 그래서 47의 상관계수만 보고도 직선 모델이 얼마나 맞을지 짐작할 수 있어요. 둘이 재는 것은 달라요. 상관계수는 두 열이 같이 오르내리는 정도라 방향이 있어 마이너스도 나와요. R제곱은 모델의 예측이 정답을 얼마나 설명하는지라 보통 0에서 1 사이예요. 6파트에서 상관계수가 0.08이었던 미국 집값으로 확인해요." + REAL)

# ---------- part 5 ----------
o = [sec("e-1d")] + head(EB5, "fit에 X를 한 줄로 넣으면: Expected a 2-dimensional container", K5)
CFS[0] = 26
EC = ['model.fit(office["area"], office["price"])']
EO = ["ValueError: Expected a 2-dimensional container but got <class 'pandas.Series'>", "instead. Pass a DataFrame containing a single row (i.e. single sample) or a", "single column (i.e. single feature) instead."]
o += cell({"id": "c-e1", "lines": EC, "n": 5, "out": EO, "err": True}, 96, 210, 1700, sel="c-e1")
o.append(underline(1, cx(96, "ValueError: ", True), cx(96, "ValueError: Expected a 2-dimensional container", True), oy(210, 1, 0) + LH() / 2 + 2, RED, 5))
o.append(reading(96, 560, "2차원(표)이 와야 하는데 Series(한 줄)가 왔다는 뜻이에요. 열 하나짜리 DataFrame을 넣으래요.", INK, 2))
o.append(fix(96, 680, 'model.fit(office["area"], ...)', 'model.fit(office[["area"]], ...)', 3, 32))
o.append(note(96, 810, 1728, "fit(y, X)처럼 순서를 바꿔도 첫째 자리에 한 줄이 들어가서 같은 오류가 나요.", SUB, 28, fade(4)))
W("e-1d", o, "가장 자주 나는 오류예요. fit 첫째 자리에 대괄호 한 겹으로 꺼낸 Series를 넣었어요. 메시지의 첫 줄을 읽으면 2차원 컨테이너, 곧 표가 와야 하는데 pandas Series가 왔다고 해요. 뒤에는 열 하나짜리 DataFrame을 넣으라고 알려 줘요. 고치는 법은 대괄호를 두 겹으로 바꾸는 거예요. fit의 X와 y 순서를 바꿔 적어도 첫째 자리에 한 줄이 들어가서 같은 오류가 나요. 메시지가 길면 첫 줄의 Expected 뒤만 읽어도 돼요. 오류 메시지는 화면 폭에 맞춰 세 줄로 나눠 적었어요." + REAL)

o = [sec("e-pred")] + head(EB5, "predict(33)처럼 숫자만 넣으면: Expected 2D array, got scalar", K5)
CFS[0] = 24
PO = ["UserWarning: X does not have valid feature names, but LinearRegression was fitted with", "feature names", "ValueError: Expected 2D array, got scalar array instead:", "array=33.", "Reshape your data either using array.reshape(-1, 1) ..."]
o += cell({"id": "c-e2", "lines": ["model.predict(33)"], "n": 5, "out": PO, "err": True, "red": (0, 1)}, 96, 200, 1700, sel="c-e2")
o.append(underline(1, cx(96, "ValueError: ", True), cx(96, "ValueError: Expected 2D array, got scalar array", True), oy(200, 1, 2) + LH() / 2 + 2, RED, 5))
o.append(reading(96, 570, "표(2차원)가 와야 하는데 숫자 하나가 왔어요. reshape는 아직 안 배웠으니 표를 만들어 넣어요.", INK, 2))
o.append(fix(96, 670, "model.predict(33)", 'model.predict(pd.DataFrame({"area": [33]}))', 3, 30))
o.append(note(96, 790, 1728, "위 UserWarning은 '학습 때는 열 이름 area가 있었는데 지금은 이름이 없다'는 경고예요. 표에 열 이름을 붙이면 함께 사라져요.", SUB, 28, fade(4)))
W("e-pred", o, "predict에 숫자 33을 바로 넣으면 두 가지가 나와요. 먼저 경고(UserWarning)예요. 학습할 때는 area라는 열 이름이 있었는데 지금 넣은 값에는 이름이 없다는 뜻이에요. 그다음이 진짜 오류예요. 2차원 배열이 와야 하는데 숫자 하나가 왔대요. 메시지는 reshape로 고치라고 하지만 아직 배우지 않았으니 수업 셀처럼 area 열이 있는 DataFrame을 만들어 넣어요. 그러면 경고와 오류가 둘 다 사라져요. 경고는 VS Code 셀 출력에서 오류처럼 눈에 띄지만 실행을 멈추지는 않아요. 경고 앞의 파일 경로와 뒷부분은 줄여 적었어요." + REAL)

o = [sec("e-name")] + head(EB5, "열 이름이 다르면: The feature names should match", K5)
CFS[0] = 24
NO = ["ValueError: The feature names should match those that were passed during fit.", "Feature names unseen at fit time:", "- size", "Feature names seen at fit time, yet now missing:", "- area"]
o += cell({"id": "c-e3", "lines": ['model.predict(pd.DataFrame({"size": [33, 59]}))'], "n": 7, "out": NO, "err": True}, 96, 200, 1500, sel="c-e3")
o.append(box(1, cx(96, "- ", True) - 8, oy(200, 1, 2) - LH() / 2 - 2, tw("size") + 16, LH() + 4, RED, 4))
o.append(box(1, cx(96, "- ", True) - 8, oy(200, 1, 4) - LH() / 2 - 2, tw("area") + 16, LH() + 4, GR, 4))
o.append(reading(96, 590, "fit 때 못 본 이름 size가 있고, fit 때 본 이름 area가 없다고 알려 줘요.", INK, 2))
CFS[0] = 24
o += cell({"id": "c-e4", "lines": ["model.predict([[33], [59]])"], "n": 6, "out": ["UserWarning: X does not have valid feature names, ...", "array([20095.21121907, 32202.72370413])"], "red": (0,)}, 96, 680, 1500, attrs=rise(3))
o.append(note(96 + 105, 900, 1600, "리스트를 두 겹으로 넣으면 계산은 되지만 경고가 나와요. 수업처럼 열 이름이 같은 DataFrame으로 넣어요.", SUB, 26, fade(4)))
W("e-name", o, "표를 넣었는데 열 이름을 area가 아닌 size로 적으면 또 오류가 나요. 메시지가 친절해요. fit 때 못 본 이름 size가 있고, fit 때 본 이름 area가 없다고 나란히 알려 줘요. 모델은 열 이름으로 어느 값이 면적인지 알아보기 때문이에요. 아래 셀처럼 리스트를 두 겹으로 감싸 넣으면 표 모양이라 계산은 돼요. 그래도 이름이 없다는 경고가 나와요. 열이 여러 개가 되면 순서가 섞여도 모르니, 수업처럼 같은 열 이름의 DataFrame으로 넣는 습관을 들여요. 경고 줄은 줄여 적었어요." + REAL)

o = [sec("e-notfit")] + head(EB5, "fit 전에 predict하면: is not fitted yet", K5)
CFS[0] = 26
NFC = ["from sklearn.linear_model import LinearRegression", "", "model = LinearRegression()", 'new = pd.DataFrame({"area": [33, 59]})', "model.predict(new)"]
NFO = ["NotFittedError: This LinearRegression instance is not fitted yet. Call 'fit' with", "appropriate arguments before using this estimator."]
o += cell({"id": "c-e5", "lines": NFC, "n": 3, "out": NFO, "err": True}, 96, 200, 1700, sel="c-e5")
o.append(underline(1, cx(96, "NotFittedError: This LinearRegression instance ", True), cx(96, "NotFittedError: This LinearRegression instance is not fitted yet", True), oy(200, 5, 0) + LH() / 2 + 2, RED, 5))
o.append(reading(96, 610, "아직 학습(fit)하지 않은 모델이에요. 빈 모델에는 w와 b가 없어서 예측할 수 없어요.", INK, 2))
o.append(fix(96, 710, "model.predict(new)", "model.fit(X, y)  # 먼저", 3, 32))
o.append(note(96, 830, 1728, "노트북을 다시 열면 모델도 처음부터예요. 맨 위 셀부터 차례로 실행해요.", SUB, 28, fade(4)))
W("e-notfit", o, "모델을 만들자마자 predict하면 NotFittedError가 나요. 이 LinearRegression 객체는 아직 학습되지 않았으니 fit을 먼저 부르라는 뜻이에요. 2파트에서 본 빈 모델 그림처럼 기울기와 절편 자리가 비어 있어서 계산할 수 없어요. 노트북을 껐다 켜거나 커널을 다시 시작하면 변수가 모두 사라지니 모델도 다시 학습해야 해요. 맨 위 셀부터 차례로 실행하면 돼요." + NEW1 + REAL)

o = [sec("e-mask")] + head(EB5, "수업 코드의 함정: normal 자리에 special을 넣으면 R²가 -2.55", K5)
CFS[0] = 24
BC = ["all_rows = np.ones(len(office), dtype=bool)", 'cases = [("전체 200건", all_rows), ("특이 매물 뺀 195건", special)]']
BO = ["전체 200건 MAE 2,510 | RMSE 4,207 | R2 0.80", "특이 매물 뺀 195건 MAE 21,118 | RMSE 21,236 | R2 -2.55"]
o += cell({"id": "c-e6", "lines": BC + ["", "for name, mask in cases:", "    ...  # 4파트 셀과 같아요"], "n": 8, "out": BO, "red": (1,)}, 96, 196, 1300, sel="c-e6")
o.append(tint(1, cx(96, 'cases = [("전체 200건", all_rows), ("특이 매물 뺀 195건", ') - 4, ly(196, 1) - LH() / 2, tw("special") + 8, LH(), RED))
o.append(box(2, cx(96, "특이 매물 뺀 195건 MAE 21,118 | RMSE 21,236 | R2 ", True) - 16, oy(196, 5, 1) - LH() / 2 - 2, tw("-2.55") + 24, LH() + 4, RED, 4))
CFS[0] = 24
o += cell({"id": "c-e7", "lines": ["print(y[special].shape, y[normal].shape)"], "n": 9, "out": ["(5,) (195,)"]}, 96, 560, 1000, attrs=rise(3))
o.append(note(1180, 560, 640, "special은 번호 5개라 y[special]은 특이 매물 5건만 골라요. 195건이 아니라 5건을 채점한 거예요.", INK, 28, fade(3)))
o.append(fix(96, 800, '("특이 매물 뺀 195건", special)', '("특이 매물 뺀 195건", normal)', 4, 28))
o.append(note(96, 900, 1728, "오류 없이 숫자만 이상하게 나와요. 결과 줄 수(shape)를 찍어 보면 바로 보여요.", SUB, 26, fade(4)))
W("e-mask", o, "수업 노트북의 마지막 셀에는 special이 들어가 있었어요. 결과를 보면 R제곱이 마이너스 2.55예요. 오류는 안 났지만 숫자가 이상해요. special은 번호 다섯 개짜리 리스트라서 y 대괄호 special은 특이 매물 다섯 건만 골라요. 그러니까 195건이 아니라 모델이 가장 크게 틀린 다섯 건만 채점한 거예요. R제곱이 마이너스라는 건 그 다섯 건의 평균만 찍는 것보다도 못하다는 뜻이에요. normal로 바꾸면 4파트의 0.92가 나와요. 줄 수를 찍어 보면 5와 195로 바로 구별돼요. 셀 둘째 줄 아래 for 문은 4파트와 같아서 줄여 적었어요." + REAL)

# ---------- part 6 ----------
o = [sec("x-quote")] + head(EB6, "오피스텔 견적표: 예상 가격과 ±MAE 범위를 같이 적어요", K6)
CFS[0] = 24
QC1 = ['quote = pd.DataFrame({"area": [25, 40, 60, 80]})', 'quote["예상 가격"] = model.predict(quote).round(-1)', "quote"]
QC2 = ["from sklearn.metrics import mean_absolute_error", "mae = mean_absolute_error(y, model.predict(X))", 'quote["아래"] = (quote["예상 가격"] - mae).round(-1)', 'quote["위"] = (quote["예상 가격"] + mae).round(-1)', "quote"]
o += cell({"id": "c-q1", "lines": QC1, "n": 5}, 96, 196, 1100)
o.append(tag(cx(96, QC1[1]) + 30, ly(196, 1), "새 열에 예측 넣기 (45)", K6, 1, 22))
Q2T = cbot(196, 3) + 30
o += cell({"id": "c-q", "lines": QC2, "n": 6}, 96, Q2T, 1100, sel="c-q")
o.append(tag(cx(96, QC2[1]) + 30, ly(Q2T, 1), "평균 오차 2,510", K3, 2, 22))
QV = [("25", "16370.0", "13860.0", "18880.0"), ("40", "23350.0", "20840.0", "25860.0"), ("60", "32670.0", "30160.0", "35180.0"), ("80", "41980.0", "39470.0", "44490.0")]
o.append(df("q-t", 96 + 105, cbot(Q2T, 5) + 30, ["area", "예상 가격", "아래", "위"], QV, [120, 200, 200, 200], fs=30, rh=62, iw=40, attrs=rise(3),
            cs={(i, 1): f"font-weight:700;color:{K6}" for i in range(4)}))
RX = 1280
QS = Plot(RX + 40, 260, 480, 520, (20, 85), (10000, 50000))
o += QS.axes("면적", "가격", (25, 40, 60, 80), (), 20)
for a, pv, lo, hi in [(25, 16370, 13860, 18880), (40, 23350, 20840, 25860), (60, 32670, 30160, 35180), (80, 41980, 39470, 44490)]:
    o.append(QS.svg(f'<line x1="{QS.X(a):.0f}" y1="{QS.Y(lo):.0f}" x2="{QS.X(a):.0f}" y2="{QS.Y(hi):.0f}" stroke="{K6}" stroke-width="10" stroke-linecap="round" stroke-opacity="0.35"/><circle cx="{QS.X(a):.0f}" cy="{QS.Y(pv):.0f}" r="10" fill="{K6}"/>', rise(4)))
o.append(QS.svg(QS.line(WFIT, BFIT, RED, 3, "10 8"), fade(4)))
o.append(note(RX, 860, 560, "점이 예상 가격, 막대가 ±2,510 범위예요.", SUB, 26, fade(4)))
W("x-quote", o, "부동산 중개소에서 면적별 견적표를 만든다고 해 봐요. 25, 40, 60, 80제곱미터를 표로 만들어 predict에 넣고, 결과를 새 열 예상 가격에 담아요. 숫자 하나만 주면 그대로 믿기 쉬우니 MAE만큼 아래와 위 범위도 같이 적어요. 평균 2,510만 원쯤 틀리는 모델이니까요. 40제곱미터는 23,350만 원이고 대략 20,840에서 25,860 사이예요. 오른쪽 그림은 표를 점과 막대로 그린 거예요. 범위 계산은 평균 오차를 쓴 간단한 방법이고, 정확한 예측 구간은 이 수업에서 다루지 않아요." + REAL, None)

o = [sec("x-find")] + head(EB6, "오차가 1만이 넘는 줄을 고르면 47의 특이 매물 5건이 나와요", K6)
CFS[0] = 26
o += cell({"id": "c-big", "lines": ['big = table[table["오차"] > 10000]', "big"], "n": 30, "out": []}, 96, 196, 820, sel="c-big")
BV = [("37427.0", "15973.0", "21454.0"), ("34300.0", "16597.0", "17703.0"), ("52044.0", "31928.0", "20117.0"), ("43557.0", "21789.0", "21768.0"), ("65582.0", "41031.0", "24550.0")]
o.append(df("big-t", 96 + 105, cbot(196, 2) + 30, ["정답", "예측", "오차"], BV, [180, 180, 180], fs=28, rh=58, iw=70, idx=[17, 122, 134, 172, 178], attrs=rise(1),
            cs={(i, -1): "" for i in range(5)}))
o.append(f'<div data-build-in="fade order 2" style="position:absolute;left:{96 + 105}px;top:{cbot(196, 2) + 30 + 58 + 2}px;width:70px;height:{58 * 5}px;border-radius:10px;border:4px solid #E08A00"></div>')
o.append(label(96 + 105, cbot(196, 2) + 30 + 58 * 6 + 26, "번호 17, 122, 134, 172, 178: 4파트의 special과 같아요", "#B26A00", 26, fade(2)))
o.append(img(1000, 196, 824, "main-2.png", rise(3), "fd-img"))
o.append(note(1000, 196 + 824 * 896 / 1423 + 26, 824, "주황 점 다섯 개가 모두 직선에서 위로 멀리 떨어져 있어요. 실제 데이터라면 잘못 적은 값인지, 정말 특별한 매물인지 먼저 확인해요.", SUB, 26, fade(4)))
o.append(note(96 + 105, cbot(196, 2) + 30 + 58 * 6 + 90, 760, "45의 조건으로 고르기 그대로예요. 오차가 큰 순서로 6번째는 6,551이라 1만에서 깔끔하게 갈려요.", GRAY, 24, fade(4)))
W("x-find", o, "이번에는 특이 매물 번호를 모른다고 생각해 봐요. 2파트에서 만든 오차 표에서 오차가 1만이 넘는 줄만 고르면 다섯 줄이 나와요. 번호가 17, 122, 134, 172, 178로 47에서 뽑은 특이 매물과 똑같아요. 모델이 크게 틀린 줄을 보면 데이터에서 튀는 값을 찾을 수 있어요. 오른쪽 그림에서 주황 점 다섯 개가 직선 위로 멀리 떨어져 있어요. 46에서 튀는 값은 누구인지 보고 지운다고 배웠어요. 여기서도 잘못 적은 값인지 진짜 특별한 매물인지 확인한 뒤에 뺄지 정해요. 오차 큰 순서의 6번째가 6,551이라는 건 따로 셀을 실행해서 확인했어요." + REAL + IMGN)

o = [sec("x-refit")] + head(EB6, "특이 매물을 빼고 다시 학습하면 기울기가 476으로 바뀌어요", K6)
CFS[0] = 24
RFC = ["clean = office[normal]", "model2 = LinearRegression()", 'model2.fit(clean[["area"]], clean["price"])', 'print("기울기:", model.coef_[0].round(1), "=>", model2.coef_[0].round(1))', 'print("절편:", model.intercept_.round(0), "=>", model2.intercept_.round(0))']
o += cell({"id": "c-rf", "lines": RFC, "n": 6, "out": ["기울기: 465.7 => 476.0", "절편: 4728.0 => 3647.0"]}, 96, 196, 1300, sel="c-rf")
o.append(tag(cx(96, RFC[1]) + 30, ly(196, 1), "새 붕어빵 하나 더", K2, 1, 22))
o.append(tag(cx(96, RFC[2]) + 30, ly(196, 2), "195건으로 학습", K4, 1, 22))
o += cell({"id": "c-rf2", "lines": ['new = pd.DataFrame({"area": [33, 59]})', "print(model.predict(new).round(-1))", "print(model2.predict(new).round(-1))"], "n": 7, "out": ["[20100. 32200.]", "[19350. 31730.]"]}, 96, 540, 1000, attrs=rise(2))
o += plain_rows(1180, 560, 640, [("33㎡", "20,100", "19,350"), ("59㎡", "32,200", "31,730")], [140, 230, 230], 3, 90, ["", "200건 모델", "195건 모델"], 32, mono_cols=(1, 2))
o.append(note(1180, 830, 640, "튀는 5건이 위로 끌어당기던 직선이 내려왔어요. 기울기는 오히려 정답 450에서 더 멀어졌어요.", SUB, 26, fade(4)))
W("x-refit", o, "이번에는 특이 매물을 아예 빼고 처음부터 다시 학습해요. normal 마스크로 195줄만 고른 clean을 만들고, 새 모델 model2를 만들어 학습해요. 같은 틀로 붕어빵을 하나 더 찍는 거예요. 절편은 4,728에서 3,647로 내려가고 기울기는 465.7에서 476.0이 됐어요. 33제곱미터 예측도 20,100에서 19,350으로 내려왔어요. 위로 튄 다섯 건이 직선을 끌어올리고 있었다는 뜻이에요. 기울기는 정답 450에서 오히려 멀어졌어요. 흔들림 2,500이 섞인 200건만으로는 정답을 딱 맞히기 어려워요. 데이터가 많을수록 정답에 가까워져요." + REAL)

o = [sec("x-house")] + head(EB6, "미국 집값 300채는 면적만으로 R²가 0.007, 거의 설명하지 못해요", K6)
CFS[0] = 19
HC1 = ["from sklearn.linear_model import LinearRegression", "from sklearn.metrics import r2_score", "", "hm = LinearRegression()", 'hm.fit(house[["SquareFeet"]], house["Price"])',
       'p300 = hm.predict(house[["SquareFeet"]])', 'print("300채 R2:", round(r2_score(house["Price"], p300), 3))']
HC2 = ["sm = LinearRegression()", 'sm.fit(small[["SquareFeet"]], small["Price"])', 'p10 = sm.predict(small[["SquareFeet"]])', 'print("10채 R2:", round(r2_score(small["Price"], p10), 2))',
       'p_all = sm.predict(house[["SquareFeet"]])', 'print("10채 직선으로 300채:", round(r2_score(house["Price"], p_all), 2))']
o += cell({"id": "c-h1", "lines": HC1, "n": 4, "out": ["300채 R2: 0.007"]}, 96, 186, 1020)
H2T = cbot(186, 7) + 1 * (LH() + 10) + 24
o += cell({"id": "c-h", "lines": HC2, "n": 5, "out": ["10채 R2: 0.8", "10채 직선으로 300채: -0.85"]}, 96, H2T, 1020, sel="c-h")
o.append(img(1150, 196, 674, "xhouse-1.png", rise(1), "hs-img"))
o.append(note(1150, 196 + 674 * 926 / 1380 + 20, 674, "세로축 1e6은 ×1,000,000이에요. 1.0이 100만 달러예요.", GRAY, 22, rise(1)))
o.append(box(2, cx(96, "300채 R2: ", True) - 8, oy(186, 7, 0) - LH() / 2 - 2, tw("0.007") + 16, LH() + 4, RED, 4))
o.append(box(3, cx(96, "10채 직선으로 300채: ", True) - 16, oy(H2T, 6, 1) - LH() / 2 - 2, tw("-0.85") + 24, LH() + 4, RED, 4))
o.append(note(1150, 196 + 674 * 926 / 1380 + 80, 674, "47의 상관계수 0.08과 0.89를 제곱한 것과 같은 이야기예요. 골라낸 10채로 배운 빨간 직선은 300채에서 평균보다도 못해요.", INK, 26, fade(3)))
W("x-house", o, "47에서 본 미국 집값 300채로도 학습해 봐요. 면적으로 가격을 예측하면 R제곱이 0.007이에요. 47에서 상관계수가 0.08이었으니 제곱하면 거의 0이죠. 파란 직선이 거의 누워 있어요. 이 데이터는 면적만으로는 가격을 설명할 수 없어요. 2015년 이후에 지은 10채만 골라서 학습하면 R제곱이 0.8로 좋아 보여요. 그런데 그 빨간 직선으로 300채 전체를 예측하면 마이너스 0.85, 평균만 찍는 것보다 못해요. 일부만 골라서 배운 모델은 전체에서 맞지 않을 수 있어요. 그래서 다음 수업에서는 학습용과 채점용 데이터를 나눠요. 이 노트북은 house와 small을 47처럼 먼저 만들었어요." + REAL + IMGN)

# ---------- wrap up ----------
o = [sec("trouble")] + head("정리", "막히면 출력의 마지막 줄을 봐요", RED)
TR = [("ModuleNotFoundError: No module named 'sklearn'", "scikit-learn을 안 넣었어요", "uv add scikit-learn"),
      ("ValueError: Expected a 2-dimensional container", "X를 대괄호 한 겹으로 넣었어요", 'office[["area"]]'),
      ("ValueError: Expected 2D array, got scalar array", "predict에 숫자만 넣었어요", 'pd.DataFrame({"area": [33]})'),
      ("ValueError: The feature names should match", "학습 때와 열 이름이 달라요", "같은 열 이름 area"),
      ("NotFittedError: ... is not fitted yet", "fit 전에 predict했어요", "model.fit(X, y) 먼저"),
      ("R²가 이상하게 낮거나 마이너스예요", "고른 줄이 다르거나 순서가 바뀌었어요", "shape, (정답, 예측) 확인")]
for i, (q, a_, cmd) in enumerate(TR):
    o.append(f'<div data-build-in="rise order {min(i + 1, 5)}" style="position:absolute;left:96px;top:{196 + i * 112}px;width:1728px;height:112px;display:flex;flex-direction:row;align-items:center;gap:26px;border-bottom:2px solid {LINE}">'
             + '<div style="flex:1;display:flex;flex-direction:column;gap:4px">' + p(f"{'font-family:' + MONO + ';' if q.isascii() else ''}font-size:25px;font-weight:700;color:{RED};white-space:nowrap", e(q)) + p(f"font-size:25px;color:{INK}", e(a_)) + '</div>'
             + p(f"width:560px;flex:none;font-size:27px;font-weight:700;color:{GR};white-space:pre", '✓ ' + e(cmd)) + '</div>')
o.append(caption("오류 메시지는 첫 줄의 Expected나 should 뒤를 읽으면 대부분 풀려요.", 900))
W("trouble", o, "막히면 셀 출력의 마지막 줄부터 읽어요. 위 다섯은 오류 메시지가 나오는 경우예요. 셋은 모두 모양 문제라 대괄호 두 겹과 같은 열 이름의 DataFrame으로 풀려요. 맨 아래는 메시지 없이 숫자만 이상한 경우예요. 마스크로 고른 줄 수를 shape로 찍어 보고, 채점 함수에 정답을 먼저 넣었는지 확인해요.", ("trouble", "정리"))

o = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장으로 보는 오늘의 코드</h2>']
CH = [("불러오기", "from sklearn.linear_model import LinearRegression", K2), ("빈 모델", "model = LinearRegression()", K2), ("문제와 정답", 'X = df[["열"]]   y = df["정답 열"]', K2),
      ("학습", "model.fit(X, y)", K2), ("배운 값", "model.coef_[0]   model.intercept_", K2),
      ("예측", 'model.predict(pd.DataFrame({"열": [값]}))', K3), ("채점 불러오기", "from sklearn.metrics import mean_absolute_error, ...", K3), ("평균 오차", "mean_absolute_error(y, y_pred)", K3),
      ("설명 정도", "r2_score(y, y_pred)   0 ~ 1", K3), ("줄 고르기", "mask = np.ones(n, dtype=bool)", K4)]
for i, (k, d, c) in enumerate(CH):
    x, y = 96 + (i // 5) * 884, 190 + (i % 5) * 124
    o.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:844px;height:110px;display:flex;flex-direction:column;justify-content:center;gap:4px;border-bottom:2px solid {LINE}">'
             + p(f"font-size:26px;font-weight:700;color:{c}", e(k)) + p(f"font-family:{MONO};font-size:{24 if len(d) > 42 else 28}px;font-weight:700;color:{INK};white-space:pre", e(d)) + '</div>')
o.append(p(f"position:absolute;left:96px;top:850px;width:1728px;font-size:32px;font-weight:700;line-height:1.5;color:{INK}", "만들고, fit(문제, 정답), predict(같은 모양 표), 채점(정답, 예측).<br>" + f'<span style="color:{GRAY}">다음: 학습용과 채점용 데이터를 나누고, 입력 열을 늘려 봐요.</span>'))
W("cheatsheet", o, "오늘 쓴 코드를 한 장에 모았어요. 왼쪽은 학습과 예측, 오른쪽은 채점이에요. 순서는 네 박자예요. 모델을 만들고, fit에 문제와 정답을 넣고, predict에 학습 때와 같은 모양의 표를 넣고, 채점 함수에 정답과 예측을 넣어요. 다음 수업에서는 학습에 쓴 데이터와 채점에 쓰는 데이터를 나누고, 면적 말고 다른 열도 입력으로 넣어 봐요.")

# ---------- order and toc ----------
want = ["cover", "toc", "setup", "read", "why", "big", "wxb", "sklearn", "min", "import", "model", "xy", "fit", "best", "coef", "predict", "draw", "ypred",
        "errors", "mae", "rmse", "r2", "metrics", "compare4", "mask", "cases", "corr", "e-1d", "e-pred", "e-name", "e-notfit", "e-mask",
        "x-quote", "x-find", "x-refit", "x-house", "trouble", "cheatsheet"]
assert sorted(want) == sorted(ORDER), (set(want) ^ set(ORDER))
ORDER[:] = want
SECTIONS.update({"p2": {"description": "학습하고 예측하기", "start": "import"}, "p3": {"description": "채점하기", "start": "errors"},
                 "p4": {"description": "특이 매물과 47 비교", "start": "mask"}, "p5": {"description": "오류와 함정", "start": "e-1d"}, "p6": {"description": "실제 상황", "start": "x-quote"}})
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
parts_ = [("Lightbulb", K1, "왜 필요한가", "why", "min"), ("Tool", K2, "학습하고 예측하기", "import", "ypred"), ("Activity", K3, "채점하기", "errors", "compare4"),
          ("Settings", K4, "특이 매물과 47 비교", "mask", "corr"), ("Warning", K5, "오류와 함정", "e-1d", "e-mask"), ("Star", K6, "실제 상황", "x-quote", "x-house")]
t = [f'<section id="toc" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>']
for i, (ic, c, h, a, b) in enumerate(parts_):
    x, y = 96 + (i // 3) * 884, 230 + (i % 3) * 190
    t.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:844px;height:160px;display:flex;flex-direction:row;align-items:center;gap:28px;border-bottom:2px solid {LINE}">'
             f'<p style="width:70px;font-size:72px;font-weight:900;color:{c}">{i + 1}</p><x-icon name="{ic}" style="width:52px;height:52px;color:{c}"></x-icon>'
             f'<p style="flex:1;font-size:44px;font-weight:700;color:{INK}">{e(h)}</p><p style="font-size:28px;color:{GRAY}">{page[a]}–{page[b]}쪽</p></div>')
t.append(f'<p style="position:absolute;left:96px;top:880px;font-size:30px;color:{SUB}">{page["setup"]}–{page["read"]}쪽은 프로젝트 준비, {page["trouble"]}–{page["cheatsheet"]}쪽은 막힐 때와 한 장 요약이에요.</p>')
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(t) + "\n<aside>" + e("1파트에서 모델이 왜 필요한지와 직선의 두 숫자, scikit-learn이 무엇인지 봐요. 2파트는 학습하고 예측하는 코드를 한 줄씩, 3파트는 예측을 채점하는 점수 넷이에요. 4파트는 특이 매물을 뺀 성적과 47 상관계수와의 관계, 5파트는 자주 나는 오류, 6파트는 배운 것을 섞은 실제 상황이에요.") + "</aside>\n</section>\n")
deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-24T07:00:00Z"}, "lists": "css", "title": "첫 머신러닝 모델 (선형 회귀)", "order": ORDER, "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
print(len(ORDER), "slides")
