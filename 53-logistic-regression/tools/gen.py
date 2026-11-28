"""Generates every slide of the logistic regression deck (53) and slides/deck.json.

Story: class notebook 05_ml.ipynb. The answer is no longer a score but pass or fail (y = score >= 60, 6 pass and 4 fail).
Part 1: a straight line (LinearRegression) fitted on True/False gives -0.16 and 1.19, so it can't be read as a chance;
the big picture of the chapter (three columns, weighted sum, S curve, probability, the 0.5 line). Part 2: y as True and
False, assign and shape[1] in the output of cell 1, chapter 51's split and scaling in one slide, stratify=y (test set
[False, True, True] with it, [True, False, False] without), iloc against loc (4 and 1), 1.21 as standard deviations.
Part 3: LogisticRegression from linear_model (a classifier despite the name), max_iter=1000 (it stops after 6 steps),
classes_ in sorted order, coef_ (shape (1, 3)) and intercept_. Part 4: class cell 6 (the new student [[4, 7, 5]]),
the weighted sum -0.065 by hand and decision_function, the S curve as a picture and a table (formula only as 참고),
predict and [0], predict_proba's two columns and [0, 1], score on the three test students (1.0), a table against
50 and 52. Part 5: scores as y (a 7-class classifier, no error), [0] alone (TypeError), no transform (warning and
99.68%), test_size=0.1 with stratify (ValueError), reading the sleep weight -0.37. Part 6: the empty class cell 7
filled with five students' chances (marked 수업 노트북 다음 단계), how much more practice turns 불합격 into 합격,
values outside the training range. Then trouble, recap, cheat sheet.
Class code fixes shown in the deck (and said in the notes): the unit "시간" after the standardized value dropped,
the comment "테스트용" written as "채점용". Every cell and output comes from tools/demo.sh (tools/run_nb.py runs the
cells with the project kernel), kept in tools/demo.log. This deck has no kernel charts; the S curve and the number
lines are drawn from the real outputs.

Layout rules (Stageshow skill, github.com/benjitaylor/skills, SKILL.md and every file in references/ read for this deck):
1. one focal object per slide: a notebook cell, one code line taken apart, one number line or one diagram (framing.md 1)
2. terms are labelled on the code token with leader lines and tints, not in cards (annotations.md)
3. say it once: the speaker notes carry the explanation, the slide keeps one caption at most (craft.md, Restraint)
4. no empty bands: the diagram or the code grows to fill; the payoff gets the room (craft.md, Restraint)
5. values move instead of swapping: scores turn into True/False chips, students fly into their sets, the
   standardized value slides down to its own ruler, [False] drops into False (motion.md, Changing text and values)
6. one number gets to be big (48.37% on the new student, 1.0 on the test students), the rest are lines (craft.md)
7. a comparison changes one thing (teaching.md, Making a comparison): with and without stratify, iloc and loc,
   transform and no transform
8. one color per role on every slide: pass green, fail red, training students teal, test students magenta,
   the weighted sum orange, the probability blue (craft.md, Color and looks)
Highlights come from tools/HIGHLIGHT.md, as many kinds as fit. No typing effect.
Usage: python3 tools/gen.py slides
"""


import base64, math
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


def flowbox(x, y, w, h, text, color, bg, fs=30, attrs="", mono_=True, tid=None):
    idt = f' id="{tid}"' if tid else ""
    return p(f"position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;border-radius:14px;border:3px solid {color};background:{bg};font-family:{MONO if mono_ else SANS};font-size:{fs}px;font-weight:700;line-height:{h - 6}px;text-align:center;color:{INK};white-space:nowrap", e(text), idt + attrs)


# ---------- this deck (53) ----------
NB = "logistic.ipynb"
EB1, EB2, EB3, EB4, EB5, EB6 = "1. 왜 필요한가", "2. 정답 만들고 나누기", "3. 모델 학습하기", "4. 확률 구하기", "5. 오류와 함정", "6. 실제 상황"
PS, PSB = GR, GRBG            # pass (True): green on every slide
FA, FAB = RED, K5BG           # fail (False): red on every slide
TR, TRB = TEAL, K3BG          # training students: teal
TE, TEB = K4, K4BG            # test students: magenta
ZC, ZCB = K2, K2BG            # weighted sum: orange
PC, PCB = K1, K1BG            # probability: blue
ROWS = [(1, 6, 10, 47), (2, 8, 15, 58), (3, 5, 20, 60), (4, 7, 25, 76), (5, 8, 30, 87), (2, 5, 12, 49), (3, 8, 28, 73), (5, 6, 22, 77), (4, 6, 32, 79), (1, 8, 8, 52)]
YS = [r[3] >= 60 for r in ROWS]
TRAIN_I, TEST_I = [3, 9, 1, 6, 8, 2, 0], [5, 7, 4]
TRAIN2_I, TEST2_I = [0, 7, 2, 9, 4, 3, 6], [8, 1, 5]     # without stratify (same split as 51)
CN3 = ["study_hours", "sleep_hours", "practice_count"]
DATAC = ['import pandas as pd', '', 'df = pd.DataFrame({', '    "study_hours":    [1, 2, 3, 4, 5, 2, 3, 5, 4, 1],', '    "sleep_hours":    [6, 8, 5, 7, 8, 5, 8, 6, 6, 8],',
         '    "practice_count": [10, 15, 20, 25, 30, 12, 28, 22, 32, 8],', '    "score":          [47, 58, 60, 76, 87, 49, 73, 77, 79, 52],', '})', '',
         'X = df[["study_hours", "sleep_hours", "practice_count"]]', 'y = df["score"] >= 60', '', 'print(f"학생 {len(X)} 명, X : {X.shape[1]}개")',
         'print(df[["score"]].assign(passed=y).head())']
DATAO = ["학생 10 명, X : 3개", "   score  passed", "0     47   False", "1     58   False", "2     60    True", "3     76    True", "4     87    True"]
SPLITC = ["from sklearn.model_selection import train_test_split", "from sklearn.preprocessing import StandardScaler", "", "# 학습용 vs 채점용 데이터 나누기",
          "X_train, X_test, y_train, y_test = train_test_split(", "    X, y, test_size=0.3, random_state=42, stratify=y", ")", "", "# 표준화", "scaler = StandardScaler()",
          "X_train_scaled = scaler.fit_transform(X_train)", "X_test_scaled = scaler.transform(X_test)", "", 'print(f"학습 {len(X_train)}명, 채점 {len(X_test)}명")', "",
          "# iloc[행 번호, 열 번호]", 'print(f"첫 학습 학생의 공부시간: {X_train.iloc[0, 0]} 시간")', 'print(f"표준화 값: {X_train_scaled[0, 0]:.2f}")']
SPLITO = ["학습 7명, 채점 3명", "첫 학습 학생의 공부시간: 4 시간", "표준화 값: 1.21"]
MODELC = ["from sklearn.linear_model import LogisticRegression", "", "# 표준화된 학습 데이터 + 정답", "model = LogisticRegression(max_iter=1000)", "model.fit(X_train_scaled, y_train)", "",
          'print("클래스 :", model.classes_.tolist())', 'print("가중치 :", model.coef_[0].round(3))']
MODELO = ["클래스 : [False, True]", "가중치 : [ 0.873 -0.37   0.877]"]
NEWC = ["new = pd.DataFrame(", "    [[4, 7, 5]],", "    columns=X.columns", ")", "new_scaled = scaler.transform(new)", "", "predict = model.predict(new_scaled)[0]", "",
        "pass_proba = model.predict_proba(new_scaled)[0, 1]", "", 'print("예측 결과:", "합격" if predict else "불합격")', 'print(f"합격 확률: {pass_proba:.2%}")']
NEWO = ["예측 결과: 불합격", "합격 확률: 48.37%"]
STUC = ["students = pd.DataFrame({", '    "study_hours":    [4, 2, 5, 3, 1],', '    "sleep_hours":    [7, 7, 6, 8, 6],', '    "practice_count": [5, 20, 25, 15, 30],', "})",
        "students_scaled = scaler.transform(students)", "", 'students["pass_proba"] = model.predict_proba(students_scaled)[:, 1].round(3)',
        'students["passed"] = model.predict(students_scaled)', 'students.sort_values("pass_proba", ascending=False)']
WGT = [0.873, -0.37, 0.877]
B0 = 0.447
FIXN = " 수업 셀 2의 마지막 줄은 '표준화 값: 1.21 시간'으로 찍었는데, 1.21은 시간이 아니라서 단위를 뺐어요. 주석의 '테스트용'은 이 덱의 말로 '채점용'이라고 적었어요."
EXTRA = " 이 셀은 이해를 도우려고 더했어요."


def sig(z):
    return 1 / (1 + math.exp(-z))


def logit(pv):
    return math.log(pv / (1 - pv))


def curve(P, color, width=6, z0=None, z1=None, attrs="", n=120):
    """The S curve drawn as one SVG path in Plot P (x is the weighted sum, y the probability)."""
    z0 = P.xr[0] if z0 is None else z0
    z1 = P.xr[1] if z1 is None else z1
    pts = [z0 + (z1 - z0) * k / n for k in range(n + 1)]
    d = "M" + " L".join(f"{P.X(z):.1f},{P.Y(sig(z)):.1f}" for z in pts)
    return f'<path{attrs} d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round"/>'


def pf(v):
    """A pass/fail chip (True or False) at its own size."""
    return tf("True" if v else "False")


def disc(i, x, y, passed, size=64, attrs="", tid=None, ring_=None):
    """One student as a numbered disc, colored by the answer (green pass, red fail). ring_: a set color around it."""
    c, bg = (PS, PSB) if passed else (FA, FAB)
    idt = f' id="{tid}"' if tid else ""
    sh = f"box-shadow:0 0 0 5px {ring_};" if ring_ else ""
    return p(f"position:absolute;left:{x:.0f}px;top:{y:.0f}px;width:{size}px;height:{size}px;border-radius:50%;border:3px solid {c};background:{bg};{sh}"
             f"font-family:{MONO};font-size:{size * 0.42:.0f}px;font-weight:700;line-height:{size - 6}px;text-align:center;color:{INK}", str(i), idt + attrs)


def setbox(x, y, w, h, color, attrs=""):
    return f'<div{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;border:4px solid {color};border-radius:22px"></div>'


def hbar_pf(x, y, w, h, ratio, attrs=""):
    """A stacked bar: pass share green from the left, fail share red after it."""
    gw = w * ratio
    return (f'<div{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;display:flex;flex-direction:row;border-radius:10px;overflow:hidden">'
            f'<div style="width:{gw:.0f}px;height:{h}px;background:{PS}"></div><div style="flex:1;height:{h}px;background:{FA};opacity:0.85"></div></div>')


def vline(x, y1, y2, color, width=3, dash="10 8", attrs=""):
    return (f'<svg{attrs} style="position:absolute;left:0;top:0;width:1920px;height:1080px;overflow:visible;pointer-events:none" viewBox="0 0 1920 1080">'
            f'<line x1="{x:.0f}" y1="{y1:.0f}" x2="{x:.0f}" y2="{y2:.0f}" stroke="{color}" stroke-width="{width}" stroke-dasharray="{dash}"/></svg>')


def hline(x1, x2, y, color, width=3, dash="10 8", attrs=""):
    return (f'<svg{attrs} style="position:absolute;left:0;top:0;width:1920px;height:1080px;overflow:visible;pointer-events:none" viewBox="0 0 1920 1080">'
            f'<line x1="{x1:.0f}" y1="{y:.0f}" x2="{x2:.0f}" y2="{y:.0f}" stroke="{color}" stroke-width="{width}" stroke-dasharray="{dash}"/></svg>')


def down(x, y, h=56, attrs=""):
    return f'<svg{attrs} style="position:absolute;left:{x - 20:.0f}px;top:{y:.0f}px;width:40px;height:{h}px" viewBox="0 0 40 {h}"><rect x="13" y="0" width="14" height="{h - 22}" fill="#9AA0AB"/><polygon points="2,{h - 24} 38,{h - 24} 20,{h - 2}" fill="#9AA0AB"/></svg>'


# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#F2B27A;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
       f'<h1 id="cov-h1"{SLAM(1)} style="font-size:88px;font-weight:900;line-height:1.14;color:#F6F5F1">합격할 확률<br>구하기</h1>',
       '<p style="font-size:38px;line-height:1.45;color:#BFC6D4">점수 대신 합격과 불합격을 맞히고,<br>그 확률까지 구해요</p>']
CP_ = Plot(70, 60, 620, 380, (-5, 5), (0, 1))
inner = [f'<line x1="{CP_.X(-5):.0f}" y1="{CP_.Y(0.5):.0f}" x2="{CP_.X(5):.0f}" y2="{CP_.Y(0.5):.0f}" stroke="#C9CED8" stroke-width="3" stroke-dasharray="10 8"/>',
         f'<line x1="{CP_.X(-5):.0f}" y1="{CP_.Y(0):.0f}" x2="{CP_.X(5):.0f}" y2="{CP_.Y(0):.0f}" stroke="#9AA0AB" stroke-width="3"/>',
         curve(CP_, PC, 7)]
for pv, ok in [(0.459, False), (0.941, True), (0.95, True)]:
    z = logit(pv)
    c = PS if ok else FA
    inner.append(f'<circle cx="{CP_.X(z):.1f}" cy="{CP_.Y(pv):.1f}" r="15" fill="#FFFFFF" stroke="{c}" stroke-width="6"/>')
cov.append(f'<div id="cov-card" style="position:absolute;left:1060px;top:220px;width:740px;height:520px;background:#FFFFFF;border-radius:24px;overflow:hidden">'
           f'<svg style="position:absolute;left:0;top:0;width:740px;height:520px" viewBox="0 0 740 520">{"".join(inner)}</svg>'
           + p(f"position:absolute;left:{CP_.X(-5) + 8:.0f}px;top:{CP_.Y(0.5) - 40:.0f}px;font-size:24px;font-weight:700;color:{GRAY}", "0.5")
           + p(f"position:absolute;left:{CP_.X(-5) + 8:.0f}px;top:{CP_.Y(1) - 20:.0f}px;font-size:24px;font-weight:700;color:{PC}", "합격 확률")
           + p(f"position:absolute;right:46px;top:{CP_.Y(0) + 14:.0f}px;font-size:24px;font-weight:700;color:{ZC}", "가중치를 곱해 더한 합계 →")
           + '</div>')
cov.append(p(f"position:absolute;left:1060px;top:770px;width:740px;font-size:26px;line-height:1.5;color:#BFC6D4", "채점용 학생 세 명의 합격 확률을 S자 곡선 위에 찍었어요."))
cov.append(shine(2, "cov-h1"))
W("cover", cov, "50과 51에서는 학생의 점수를 숫자로 맞혔어요. 오늘은 점수 대신 60점을 넘어 합격할지, 못 넘어 불합격할지를 맞혀요. 정답이 두 보기 중 하나인 문제예요. 로지스틱 회귀는 답만 말하지 않고, 합격할 확률이 몇 퍼센트인지까지 알려 줘요. 오른쪽 그림의 S자 곡선이 그 확률을 만드는 곡선이에요. 수업 노트북 05의 내용이에요.", ("intro", "들어가기"))
ORDER.append("toc")

# ---------- setup ----------
o = [sec("setup")] + head("들어가기", f"ml-basics에 새 노트북 {NB}을 열어요. 새로 설치할 건 없어요", JP)
TL = [("$", "cd ml-basics"), ("$", "cat pyproject.toml"), ("o", "dependencies = ["), ("o", '    "matplotlib>=3.11.2",'), ("o", '    "numpy>=2.5.5",'), ("o", '    "pandas>=3.1.1",'),
      ("o", '    "scikit-learn>=1.9.1",'), ("o", '    "seaborn>=0.13.2",'), ("o", "]")]
o.append(term(96, 214, 900, TL, 28, tid="t-setup"))
LHt = 28 * 1.55
o.append(box(1, 96 + 34 - 10, 214 + 26 + 6 * LHt - 4, 28 * 0.6 * 26 + 24, LHt + 8, "#F2C46D", 4, 10))
o.append(tag(96 + 34 + 28 * 0.6 * 26 + 40, 214 + 26 + 6.5 * LHt, "48에서 넣었어요", "#B26A00", 1, 26))
o.append(note(96, 214 + 52 + len(TL) * LHt + 30, 900, "dependencies 위아래 줄은 줄여 적었어요. 버전 숫자는 받는 날에 따라 달라요.", SUB, 26, fade(1)))
TX = 1240
tree = [("ml-basics/", INK, 0, True, None), (".venv/", GRAY, 1, True, None), ("datasets/", GRAY, 1, True, None), ("multi.ipynb", GRAY, 1, False, "50 노트북"),
        ("split.ipynb", GRAY, 1, False, "51 노트북"), (NB, JP, 1, False, "오늘 노트북"), ("pyproject.toml", GRAY, 1, False, None)]
o.append(label(TX, 214, "폴더 모양", INK, 30))
for i, (n_, c_, d, folder, t_) in enumerate(tree):
    y = 290 + i * 76
    at = rise(2) + DELAY(i * 60) if i else ""
    s_ = ("▸ " if folder else "") + n_
    o.append(p(f"position:absolute;left:{TX + d * 56}px;top:{y}px;font-family:{MONO};font-size:32px;font-weight:700;line-height:64px;color:{c_};white-space:nowrap", e(s_), at))
    if t_:
        o.append(tag(TX + d * 56 + tw(s_, 32) + 30, y + 32, t_, JP if c_ == JP else GRAY, 2, 26))
o.append(caption("scikit-learn이 dependencies에 있으면 준비 끝이에요. 커널은 .venv를 골라요(10).", 930, 3))
W("setup", o, f"45부터 쓰는 ml-basics 프로젝트를 그대로 써요. 오늘 쓰는 LogisticRegression은 48에서 넣은 scikit-learn 안에 들어 있어요. 51의 train_test_split과 StandardScaler도 같은 패키지예요. 그래서 새로 설치할 건 없어요. pyproject.toml에 scikit-learn이 없으면 uv add scikit-learn으로 넣어요. VS Code에서 {NB}을 새로 만들고 커널은 .venv로 골라요. 오늘은 그래프를 그리지 않아서 글꼴 셀도 필요 없어요." + REAL)

# ---------- start ----------
o = [sec("start")] + head("들어가기", "맨 위 셀은 50, 51과 같은 학생 10명이에요. 정답 y만 달라요", JP)
CFS[0] = 26
o += cell({"id": "c-data", "lines": DATAC, "n": 1}, 96, 196, 1250, sel="c-data")
o.append(hl(96, 196, 1250, 3, 4, "skip", 1))
o.append(tag(1380, ly(196, 4.5) - 0, "50, 51과 같은 학생 10명", GRAY, 1, 28))
o.append(tag(1380, ly(196, 9), "문제 X: 열 셋은 그대로", INK, 2, 28))
o.append(hl(96, 196, 1250, 10, 1, "run", 3))
o.append(tag(1380, ly(196, 10), "정답 y: 점수 대신 합격, 불합격", PS, 3, 28))
o.append(tag(1380, ly(196, 12.5), "출력은 2파트에서 읽어요", GRAY, 4, 26))
o.append(caption("50의 y는 점수였어요. 오늘의 y는 60점을 넘었는지예요.", 930, 5))
W("start", o, "새 노트북 맨 위 셀은 수업 노트북 05의 셀 1이에요. 덱에서 수업 셀 몇이라고 부르면 수업 노트북의 셀 번호예요. 셀 왼쪽 대괄호 숫자는 이 덱의 셀을 위에서부터 차례로 실행했을 때의 번호예요. 학생 10명의 공부 시간, 수면 시간, 연습 횟수, 점수 표는 50, 51과 똑같아요. 문제 X도 같은 세 열이에요. 달라진 곳은 정답 y 한 줄이에요. 50에서는 y가 점수 그 자체였는데, 오늘은 점수가 60점 이상인지를 담아요. 출력 두 줄은 2파트에서 하나씩 읽어요.")

# ---------- part 1 ----------
o = [sec("why")] + head(EB1, "직선으로 합격을 맞히면 0과 1 밖으로 나가요", K1)
CFS[0] = 26
WHYC = ["from sklearn.linear_model import LinearRegression", "", "line = LinearRegression()", "line.fit(X, y)", "print(line.predict(X).round(2))"]
o += cell({"id": "c-why", "lines": WHYC, "n": 2, "out": ["[ 0.02  0.22  0.68  0.88  1.13  0.26  0.83  0.94  1.19 -0.16]"]}, 96, 196, 1240, sel="c-why")
o.append(tint(1, cx(96, "line.fit(X, ") - 2, ly(196, 3) - LH() / 2, tw("y") + 4, LH(), PS))
o.append(tag(cx(96, "line.fit(X, y)") + 30, ly(196, 3), "True는 1, False는 0으로 배워요", PS, 1, 28))
PRED = [0.02, 0.22, 0.68, 0.88, 1.13, 0.26, 0.83, 0.94, 1.19, -0.16]
NL = Plot(220, 660, 1480, 10, (-0.4, 1.4), (0, 1))
AY = 760
o.append(f'<div{fade(2)} style="position:absolute;left:{NL.X(0):.0f}px;top:{AY - 170}px;width:{NL.X(1) - NL.X(0):.0f}px;height:196px;background:{PCB};border-radius:14px"></div>')
o.append(label(NL.X(0) + 16, AY - 160, "확률이라면 0과 1 사이", PC, 26, fade(2)))
o.append(f'<div style="position:absolute;left:{NL.X(-0.4):.0f}px;top:{AY}px;width:{NL.X(1.4) - NL.X(-0.4):.0f}px;height:4px;background:#9AA0AB"></div>')
for v in [0, 0.5, 1]:
    o.append(p(f"position:absolute;left:{NL.X(v) - 40:.0f}px;top:{AY + 80}px;width:80px;text-align:center;font-family:{MONO};font-size:26px;font-weight:700;color:{GRAY}", str(v)))
    o.append(f'<div style="position:absolute;left:{NL.X(v) - 2:.0f}px;top:{AY - 10}px;width:4px;height:24px;background:#9AA0AB"></div>')
srt = sorted(range(10), key=lambda k: PRED[k])
for r_, k in enumerate(srt):
    x = NL.X(PRED[k])
    up = r_ % 2 == 0
    o.append(disc(k, x - 24, AY - 22, YS[k], 48, rise(1) + DELAY(r_ * 50), tid=f"d{k}"))
    o.append(p(f"position:absolute;left:{x - 40:.0f}px;top:{AY - 82 if up else AY + 34:.0f}px;width:80px;text-align:center;font-family:{MONO};font-size:24px;font-weight:700;color:{INK}", f"{PRED[k]:.2f}", rise(1) + DELAY(r_ * 50)))
o.append(box(3, NL.X(-0.16) - 46, AY - 86, 92, 42, RED, 4, 8))
o.append(box(3, NL.X(1.19) - 46, AY + 30, 92, 42, RED, 4, 8))
o.append(label(NL.X(-0.16) - 60, AY - 136, "0보다 작아요", RED, 24, fade(3)))
o.append(label(NL.X(1.19) - 50, AY + 84, "1보다 커요", RED, 24, fade(3)))
o.append(caption("직선은 끝없이 뻗어서 -0.16, 1.19가 나와요. 확률로 읽을 수 없어요.", 950, 4))
W("why", o, "48에서 배운 LinearRegression으로 먼저 해 봐요. y에 True와 False를 넣으면 True는 1, False는 0으로 보고 직선을 맞춰요. 예측을 찍으면 0.68처럼 합격 확률 같은 숫자가 나오기도 해요. 그런데 9번 학생은 -0.16, 8번 학생은 1.19예요. 확률은 0보다 작거나 1보다 클 수 없어요. 직선은 양쪽으로 끝없이 뻗어서 이런 숫자가 나와요. 그래서 0과 1 사이에만 머무는 곡선이 필요해요. 그림의 원 색은 정답이에요. 초록은 합격, 빨강은 불합격이에요." + EXTRA + REAL, ("p1", "왜 필요한가"))

o = [sec("big")] + head(EB1, "로지스틱 회귀는 합계를 S자 곡선에 넣어 확률로 바꿔요", K1)
NODES = [("세 열", "4, 7, 5", INK, "#FFFFFF"), ("합계", "-0.065", ZC, ZCB), ("합격 확률", "48.37%", PC, PCB), ("결과", "불합격", FA, FAB)]
STEPS_ = ["가중치를<br>곱해 더하기", "S자 곡선에<br>넣기", "0.5와<br>비교하기"]
FNS = ["new", "decision_function", "predict_proba", "predict"]
NX = [96, 572, 1048, 1524]
for k, (h_, v_, c_, bg) in enumerate(NODES):
    at = rise(2 * k) if k else ""
    o.append(flowbox(NX[k], 380, 300, 130, h_, c_, bg, 40, at, mono_=False))
    o.append(p(f"position:absolute;left:{NX[k]}px;top:560px;width:300px;text-align:center;font-family:{MONO if k < 3 else SANS};font-size:40px;font-weight:700;color:{c_}", e(v_), fade(7) + DELAY(k * 200) + f' id="bv{k}"'))
    o.append(p(f"position:absolute;left:{NX[k]}px;top:650px;width:300px;text-align:center;font-family:{MONO};font-size:24px;color:{GRAY}", e(FNS[k]), fade(8)))
for k, s_ in enumerate(STEPS_):
    x = NX[k] + 300
    o.append(arrow(110, "#9AA0AB", WIPE(2 * k + 1), f"position:absolute;left:{x + 33}px;top:430px"))
    o.append(p(f"position:absolute;left:{x - 10}px;top:290px;width:196px;text-align:center;font-size:26px;font-weight:700;line-height:1.35;color:{SUB}", s_, fade(2 * k + 1)))
o.append(label(96, 236, "새 학생 한 명이 지나가는 길", SUB, 28))
o.append(label(96, 760, "아래 회색 글씨는 그 값을 꺼내는 이름이에요. 4파트에서 하나씩 써 봐요.", GRAY, 26, fade(8)))
o.append(caption("앞 두 칸은 50의 다중 회귀와 같고, 뒤 두 칸이 새로 생겼어요.", 930, 9))
W("big", o, "오늘 배울 모델이 하는 일을 한 그림으로 봐요. 학생의 세 열 값에 열마다 가중치를 곱해 더해요. 여기까지는 50의 다중 회귀가 하던 덧셈과 같아요. 로지스틱 회귀는 이 합계를 S자 모양 곡선에 넣어서 0과 1 사이의 확률로 바꿔요. 마지막으로 확률이 0.5 이상이면 합격, 아니면 불합격이라고 답해요. 아래 숫자는 4파트에서 볼 새 학생의 실제 값이에요. 공부 4시간, 수면 7시간, 연습 5번인 학생은 합계 -0.065, 합격 확률 48.37%, 결과는 불합격이에요.")

# ---------- part 2 ----------
o = [sec("target")] + head(EB2, "y = df[\"score\"] >= 60은 학생마다 60점을 넘었는지 물어요", K2)
TP = [("y", "#B8E8BE"), (" = ", W_), ('df["score"]', "#9CC2F5"), (" >= 60", "#F2C46D")]
o.append(strip_parts(96, 200, 1728, 120, TP, 46))
xs, _ = sline(96, 200, TP, 46)
for k, (i, t_, c_) in enumerate([(2, "점수 열 하나 (45의 Series)", K1), (3, "칸마다 60 이상인지 비교 (12)", OR), (0, "정답 y: True, False 10개", PS)]):
    o.append(lead_down(1 + k, xs[i] + tw(TP[i][0], 46) / 2, 300, 350 + k * 56, c_, t_, 26))
SX, SG = 96, 172
for k in range(10):
    o.append(vbox(SX + k * SG, 560, 150, 80, str(ROWS[k][3]), K1, K1BG, 34, rise(1) + DELAY(k * 40) + f' id="sc{k}"'))
    o.append(p(f"position:absolute;left:{SX + k * SG}px;top:520px;width:150px;text-align:center;font-size:22px;color:{GRAY}", str(k), rise(1)))
    c_, bg = (PS, PSB) if YS[k] else (FA, FAB)
    o.append(p(f"position:absolute;left:{SX + k * SG}px;top:720px;width:150px;height:70px;border-radius:12px;background:{bg};font-family:{MONO};font-size:28px;font-weight:700;line-height:70px;text-align:center;color:{c_}",
               "True" if YS[k] else "False", fly(4, f"sc{k}") + DELAY(k * 60)))
o.append(label(96, 830, "True 6명 (합격)", PS, 30, fade(5)))
o.append(label(420, 830, "False 4명 (불합격)", FA, 30, fade(5)))
o.append(caption("정답이 두 보기 중 하나면 분류예요. 50처럼 숫자를 맞히는 건 회귀예요.", 930, 6))
W("target", o, "y 한 줄을 뜯어 봐요. df 대괄호 score는 45에서 본 열 하나, Series예요. 여기에 >= 60을 붙이면 12에서 배운 비교를 열의 칸마다 한 번씩 해요. 그래서 점수 10개가 True, False 10개로 바뀌어요. 60점인 2번 학생도 이상이라 True예요. 합격이 6명, 불합격이 4명이에요. 이렇게 정답이 정해진 보기 중 하나인 문제를 분류라고 해요. 50, 51처럼 점수 같은 숫자를 맞히는 문제는 회귀라고 해요.")

o = [sec("assign")] + head(EB2, "셀 1의 출력: 학생 수, 열 수, 그리고 passed 열을 붙인 표", K2)
OUTF = 34
o.append(mono(96, 230, DATAO, OUTF, 1.45, INK, tid="o-data"))
def oyl(i):
    return 230 + OUTF * 1.45 * (i + 0.5)
o.append(tint(1, 96 + tw("학생 ", OUTF) - 2, oyl(0) - OUTF * 0.72, tw("10", OUTF) + 4, OUTF * 1.45, K1))
o.append(tint(1, 96 + tw("학생 10 명, X : ", OUTF) - 10, oyl(0) - OUTF * 0.72, tw("3", OUTF) + 4, OUTF * 1.45, OR))
o.append(box(3, 96 + tw("   score ", OUTF) - 6, oyl(1) - OUTF * 0.72 - 4, tw(" passed", OUTF) + 16, OUTF * 1.45 * 6 + 8, PS, 4, 10))
o.append(tag(96 + tw("4     87    True", OUTF) + 50, oyl(4), "assign으로 붙인 열", PS, 3, 28))
o.append(tag(96 + tw("4     87    True", OUTF) + 50, oyl(5.2), "head()라서 앞 5명만", GRAY, 3, 24))
RX = 1060
o.append(label(RX, 222, "f-string 안의 두 값", SUB, 26, fade(1)))
o.append(p(f"position:absolute;left:{RX}px;top:270px;font-family:{MONO};font-size:30px;font-weight:700;line-height:1.6;color:{INK};white-space:pre",
           f'<span style="color:{K1}">len(X)</span>  → 10 (줄 수)<br>X.shape → (10, 3)<br><span style="color:{OR}">X.shape[1]</span> → 3 (열 수)', fade(2)))
AP_ = [("df[[\"score\"]]", "#9CC2F5"), (".assign(passed=y)", "#B8E8BE"), (".head()", "#C7B5F5")]
o.append(strip_parts(96, 640, 1728, 110, AP_, 40))
xs, _ = sline(96, 640, AP_, 40)
for k, (t_, c_) in enumerate([("score 열 하나짜리 표 (두 겹, 45)", K1), ("passed 열을 붙인 새 표 (df는 그대로)", PS), ("앞 5줄", PUR)]):
    o.append(lead_down(3 + k, xs[k] + tw(AP_[k][0], 40) / 2, 730, [800, 860, 800][k], c_, t_, 28, w=(420 if k == 0 else None), anchor=("center" if k == 0 else "left")))
W("assign", o, "셀 1의 출력을 읽어요. 첫 줄은 f-string 안에 넣은 두 값이에요. len(X)는 줄 수라서 10이에요. X.shape는 (10, 3)이고, 대괄호 1은 그 튜플의 1번 칸, 곧 열 수 3이에요. 13에서 배운 튜플 꺼내기와 같아요. 그 아래 표는 점수 열 하나짜리 표에 assign으로 passed 열을 붙인 거예요. assign은 열을 붙인 새 표를 돌려줘요. df에는 passed 열이 생기지 않아요. 정답을 점수 옆에 나란히 놓고 확인만 하려고 쓴 거예요. head()라서 앞 5명만 보여요." + REAL)

o = [sec("review51")] + head(EB2, "셀 2는 51에서 배운 나누기와 크기 맞추기예요. stratify만 새로 나왔어요", K2)
CFS[0] = 21
o += cell({"id": "c-split", "lines": SPLITC, "n": 3, "out": SPLITO}, 96, 190, 1180, sel="c-split")
o.append(hl(96, 190, 1180, 4, 3, "mark", 1))
o.append(tag(1320, ly(190, 5), "51: 학습용 7명, 채점용 3명", TR, 1, 26))
o.append(tint(2, cx(96, "    X, y, test_size=0.3, random_state=42, ") - 2, ly(190, 5) - LH() / 2, tw("stratify=y") + 4, LH(), OR))
o.append(tag(1320, ly(190, 6.2), "새로 나왔어요: 다음 장", OR, 2, 26))
o.append(hl(96, 190, 1180, 9, 3, "run", 3))
o.append(tag(1320, ly(190, 10), "51: 학습용으로 자를 만들고 같은 자로", TR, 3, 26, w=500))
o.append(hl(96, 190, 1180, 15, 3, "skip", 4))
o.append(tag(1320, ly(190, 16), "iloc과 1.21은 이 파트 끝에서", GRAY, 4, 26))
W("review51", o, "셀 2예요. 위쪽 다섯 줄은 51에서 배운 train_test_split이에요. 학생 10명을 학습용 7명과 채점용 3명으로 나눠요. 괄호 끝의 stratify=y만 새로 나왔어요. 다음 장에서 봐요. 가운데 세 줄은 51의 StandardScaler예요. 학습용으로 fit_transform해서 자를 만들고, 채점용은 같은 자로 transform만 해요. 아래 세 줄의 iloc과 표준화 값 1.21은 이 파트 끝에서 읽어요." + FIXN + REAL)

o = [sec("stratify")] + head(EB2, "stratify=y는 합격과 불합격 비율을 학습용과 채점용에 똑같이 나눠요", K2)
o.append(label(96, 214, "전체 10명: 합격 6명, 불합격 4명", INK, 30))
for k in range(10):
    o.append(disc(k, 96 + k * 98, 270, YS[k], 72, tid=f"st{k}"))
o.append(setbox(80, 470, 7 * 98 + 30, 110, TR, fade(1)))
o.append(label(96, 600, "학습용 7명: 합격 4, 불합격 3", TR, 30, fade(1)))
for j, k in enumerate(TRAIN_I):
    o.append(disc(k, 96 + j * 98, 490, YS[k], 72, fly(1, f"st{k}") + DELAY(j * 60)))
o.append(setbox(860, 470, 3 * 98 + 30, 110, TE, fade(2)))
o.append(label(876, 600, "채점용 3명: 합격 2, 불합격 1", TE, 30, fade(2)))
for j, k in enumerate(TEST_I):
    o.append(disc(k, 876 + j * 98, 490, YS[k], 72, fly(2, f"st{k}") + DELAY(j * 60)))
CFS[0] = 22
o += cell({"id": "c-st", "lines": ['print("학습용:", list(y_train))', 'print("채점용:", list(y_test))'], "n": 4,
           "out": ["학습용: [True, False, False, True, True, True, False]", "채점용: [False, True, True]"]}, 96, 690, 1100, attrs=rise(3))
RX = 1300
o.append(label(RX, 214, "합격 비율", SUB, 28, fade(3)))
for k, (t_, r_, c_) in enumerate([("전체", 6 / 10, INK), ("학습용", 4 / 7, TR), ("채점용", 2 / 3, TE)]):
    y = 270 + k * 110
    o.append(label(RX, y + 8, t_, c_, 28, fade(3) + DELAY(k * 100)))
    o.append(hbar_pf(RX + 130, y, 300, 50, r_, WIPE(3) + DELAY(k * 100)))
    o.append(label(RX + 450, y + 8, f"{r_:.0%}", c_, 28, fade(3) + DELAY(k * 100)))
o.append(note(RX, 620, 520, "3명은 6 대 4로 나눌 수 없어서, 가장 가까운 2 대 1이 돼요.", SUB, 26, fade(4)))
W("stratify", o, "stratify는 층을 나눈다는 뜻이에요. stratify=y라고 적으면 y의 True와 False를 따로 모아 두고, 양쪽에서 같은 비율로 학습용과 채점용에 나눠 담아요. 전체 10명은 합격 6명, 불합격 4명이에요. 학습용 7명에는 합격 4명과 불합격 3명이, 채점용 3명에는 합격 2명과 불합격 1명이 들어갔어요. 3명은 6 대 4로 정확히 나눌 수 없어서 가장 가까운 2 대 1이 됐어요. 분류에서는 정답 보기마다 학생 수가 다를 때가 많아서, 채점용에 한쪽 보기만 몰리지 않게 이 옵션을 자주 붙여요. 원 안의 숫자는 df의 줄 번호예요." + EXTRA + REAL)

o = [sec("stratify-cmp")] + head(EB2, "stratify를 빼면 채점용이 [True, False, False]로 바뀌어요", K2)
CFS[0] = 22
NOSC = ["X_train2, X_test2, y_train2, y_test2 = train_test_split(", "    X, y, test_size=0.3, random_state=42", ")", 'print("학습용:", list(y_train2))', 'print("채점용:", list(y_test2))']
o += cell({"id": "c-nost", "lines": NOSC, "n": 5, "out": ["학습용: [False, True, True, False, True, True, True]", "채점용: [True, False, False]"]}, 96, 190, 1300, sel="c-nost")
o.append(tag(cx(96, NOSC[1]) + 30, ly(190, 1), "stratify만 뺐어요", OR, 1, 26))
CY0 = 570
o.append(label(96, CY0 - 60, "합격 비율 (초록이 합격, 빨강이 불합격)", SUB, 26, fade(2)))
RW = [("전체 10명", 6 / 10, INK, None), ("stratify=y   학습용", 4 / 7, TR, "a"), ("채점용", 2 / 3, TE, "a"), ("stratify 없음 학습용", 5 / 7, TR, "b"), ("채점용", 1 / 3, TE, "b")]
for k, (t_, r_, c_, g) in enumerate(RW):
    y = CY0 + k * 74 + (24 if k >= 1 else 0) + (24 if k >= 3 else 0)
    od = 2 if g != "b" else 3
    o.append(p(f"position:absolute;left:96px;top:{y + 6}px;width:420px;text-align:right;font-size:28px;font-weight:700;color:{c_};white-space:pre", e(t_), fade(od)))
    o.append(hbar_pf(560, y, 900, 50, r_, WIPE(od)))
    o.append(label(1490, y + 6, f"{r_:.0%}", c_, 28, fade(od)))
o.append(vline(560 + 900 * 0.6, CY0 - 10, CY0 + 5 * 74 + 60, INK, 3, "8 8", fade(2)))
o.append(ring(4, 1470, CY0 + 4 * 74 + 48 - 8, 110, 50, RED, 5))
o.append(note(1630, CY0 + 4 * 74 + 48 + 2, 200, "불합격이 더 많아요", RED, 26, fade(4)))
W("stratify-cmp", o, "같은 random_state 42로 stratify만 빼고 나눴어요. 51과 같은 나누기예요. 이번에는 채점용 3명이 합격 1명, 불합격 2명이에요. 전체는 합격이 60%인데 채점용은 33%예요. 반대로 학습용에는 합격이 71%로 몰렸어요. 한 가지만 바꿨는데 양쪽 비율이 크게 달라졌어요. 학생이 적을수록 이렇게 쏠리기 쉬워요. stratify=y를 붙이면 양쪽 모두 전체 60%에 가깝게 맞춰져요. 점선이 전체 비율 60%예요." + EXTRA + REAL)

o = [sec("iloc")] + head(EB2, "iloc은 몇 번째 줄, loc은 이름표가 몇인 줄이에요", K2)
CFS[0] = 24
ILC = ["print(list(X_train.index))", "print(X_train.iloc[0, 0])", 'print(X_train.loc[0, "study_hours"])']
o += cell({"id": "c-iloc", "lines": ILC, "n": 6, "out": ["[3, 9, 1, 6, 8, 2, 0]", "4", "1"]}, 96, 196, 880, sel="c-iloc")
o.append(tint(1, cx(96, "print(X_train.") - 2, ly(196, 1) - LH() / 2, tw("iloc[0, 0]") + 4, LH(), K1))
o.append(tint(2, cx(96, "print(X_train.") - 2, ly(196, 2) - LH() / 2, tw('loc[0, "study_hours"]') + 4, LH(), OR))
TL0, IW, WD, RH, TT0 = 1150, 64, [190, 190, 230], 60, 250
XTR = [(ROWS[k][0], ROWS[k][1], ROWS[k][2]) for k in TRAIN_I]
o.append(df("t-xtr", TL0, TT0, CN3, XTR, WD, 26, RH, idx=TRAIN_I, iw=IW))
o.append(p(f"position:absolute;left:{TL0 - 110}px;top:{TT0}px;width:90px;height:{RH}px;text-align:center;font-size:22px;font-weight:700;line-height:{RH}px;color:{K1}", "번호", fade(1)))
for j in range(7):
    o.append(p(f"position:absolute;left:{TL0 - 110}px;top:{dfy(TT0, RH, j)}px;width:90px;height:{RH}px;text-align:center;font-family:{MONO};font-size:26px;font-weight:700;line-height:{RH}px;color:{K1}", str(j), fade(1)))
o.append(p(f"position:absolute;left:{TL0}px;top:{TT0 - 40}px;width:{IW + 10}px;text-align:right;font-size:22px;font-weight:700;color:{OR}", "이름표", fade(2)))
o.append(box(1, dfx(TL0, IW, WD, 0) - 4, dfy(TT0, RH, 0) - 2, WD[0] + 8, RH + 2, K1, 5, 10))
o.append(box(2, TL0 - 4, dfy(TT0, RH, 6) - 2, IW + WD[0] + 12, RH + 2, OR, 5, 10))
o.append(link(1, cx(96, "4", True) + 10, oy(196, 3, 1), TL0 - 120, dfy(TT0, RH, 0) + RH / 2, K1, 4))
o.append(link(2, cx(96, "1", True) + 10, oy(196, 3, 2), TL0 - 120, dfy(TT0, RH, 6) + RH / 2, OR, 4))
RY = 760
o.append(p(f"position:absolute;left:96px;top:{RY}px;font-family:{MONO};font-size:32px;font-weight:700;color:{K1};white-space:pre", "iloc[0, 0]", fade(3)))
o.append(p(f"position:absolute;left:520px;top:{RY}px;font-size:32px;font-weight:700;color:{INK}", "0번째 줄, 0번째 열 (번호는 0부터, 13의 인덱스처럼)", fade(3)))
o.append(p(f"position:absolute;left:96px;top:{RY + 80}px;font-family:{MONO};font-size:32px;font-weight:700;color:{OR};white-space:pre", 'loc[0, "study_hours"]', fade(3)))
o.append(p(f"position:absolute;left:520px;top:{RY + 80}px;font-size:32px;font-weight:700;color:{INK}", "이름표가 0인 줄, 이름이 study_hours인 열 (46)", fade(3)))
o.append(caption("섞어서 나눈 표는 번호와 이름표가 달라요. 첫 학생은 iloc으로 꺼내요.", 950, 4))
W("iloc", o, "셀 2의 iloc을 따로 찍어 봤어요. X_train은 섞어서 나눈 표라 왼쪽 이름표가 3, 9, 1처럼 뒤섞여 있어요. iloc은 이름표를 보지 않고 위에서부터 몇 번째 줄인지, 왼쪽부터 몇 번째 열인지를 번호로 받아요. 번호는 13의 리스트 인덱스처럼 0부터예요. 그래서 iloc 0, 0은 맨 위 3번 학생의 공부 시간 4예요. loc은 46에서 배운 대로 이름표와 열 이름을 받아요. loc 0은 이름표가 0인 줄이라 맨 아래 0번 학생의 공부 시간 1이 나와요. 섞인 표에서 맨 앞 학생을 꺼낼 때는 iloc을 써요." + EXTRA + REAL)

o = [sec("scaled")] + head(EB2, "표준화 값 1.21은 1.21시간이 아니라 표준편차 1.21개예요", K2)
CFS[0] = 24
SCC = ['print("평균:", scaler.mean_[0].round(2))', 'print("표준편차:", scaler.scale_[0].round(2))', "print((4 - 2.57) / 1.18)"]
o += cell({"id": "c-sc", "lines": SCC, "n": 7, "out": ["평균: 2.57", "표준편차: 1.18", "1.2118644067796611"]}, 96, 196, 900, sel="c-sc")
o.append(tag(1020, ly(196, 0), "학습용 7명의 공부 시간 평균 (51)", GRAY, None, 24))
HP = Plot(260, 600, 1400, 10, (0, 6), (0, 1))
HY = 640
o.append(label(96, HY - 20, "공부 시간", INK, 28))
o.append(f'<div style="position:absolute;left:{HP.X(0):.0f}px;top:{HY}px;width:{HP.X(6) - HP.X(0):.0f}px;height:4px;background:#9AA0AB"></div>')
for v in range(7):
    o.append(p(f"position:absolute;left:{HP.X(v) - 40:.0f}px;top:{HY + 18}px;width:80px;text-align:center;font-family:{MONO};font-size:24px;color:{GRAY}", f"{v}시간"))
seen = {}
for k in TRAIN_I:
    h = ROWS[k][0]
    n_ = seen.get(h, 0)
    seen[h] = n_ + 1
    o.append(disc(k, HP.X(h) - 26, HY - 66 - n_ * 60, YS[k], 52, ring_=(TR if k == 3 else None), tid=("s3" if k == 3 else None)))
M_, S_ = 2.57, 1.18
o.append(vline(HP.X(M_), HY - 200, HY + 10, ZC, 4, "10 8", fade(1)))
o.append(label(HP.X(M_) - 60, HY - 250, "평균 2.57", ZC, 26, fade(1)))
o.append(f'<div{WIPE(2)} style="position:absolute;left:{HP.X(M_):.0f}px;top:{HY + 70}px;width:{HP.X(M_ + S_) - HP.X(M_):.0f}px;height:14px;background:{TR};border-radius:7px"></div>')
o.append(label(HP.X(M_), HY + 92, "표준편차 1개 = 1.18시간", TR, 24, fade(2)))
ZY = 900
o.append(label(96, ZY - 20, "표준화 값", TR, 28, fade(3)))
o.append(f'<div{fade(3)} style="position:absolute;left:{HP.X(0):.0f}px;top:{ZY}px;width:{HP.X(6) - HP.X(0):.0f}px;height:4px;background:#9AA0AB"></div>')
for v in [-2, -1, 0, 1, 2]:
    x = HP.X(M_ + v * S_)
    if HP.X(0) <= x <= HP.X(6):
        o.append(p(f"position:absolute;left:{x - 40:.0f}px;top:{ZY + 18}px;width:80px;text-align:center;font-family:{MONO};font-size:24px;color:{GRAY}", str(v), fade(3)))
o.append(disc(3, HP.X(4) - 26, ZY - 66, True, 52, fly(4, "s3"), ring_=TR))
o.append(label(HP.X(4) + 40, ZY - 58, "1.21", TR, 34, fade(4)))
W("scaled", o, "셀 2의 마지막 줄이 찍은 1.21을 읽어 봐요. 51에서 배운 표준화는 평균을 빼고 표준편차로 나눠요. 학습용 7명의 공부 시간 평균은 2.57시간, 표준편차는 1.18시간이에요. 첫 학습 학생인 3번은 4시간을 공부했어요. 4에서 2.57을 빼고 1.18로 나누면 1.21이에요. 평균보다 표준편차 1.21개만큼 위에 있다는 뜻이에요. 그래서 단위가 시간이 아니에요. 수업 코드는 이 값 뒤에 '시간'을 붙였는데, 덱에서는 뺐어요. 손 계산은 반올림한 2.57과 1.18로 해서 끝자리가 조금 달라요." + EXTRA + REAL)

# ---------- part 3 ----------
o = [sec("import")] + head(EB3, "LogisticRegression은 이름은 회귀지만 분류 모델이에요", K3)
IP = [("from ", "#9AA0AB"), ("sklearn", "#9CC2F5"), (".", W_), ("linear_model", "#F2C46D"), (" import ", "#9AA0AB"), ("LogisticRegression", "#B8E8BE")]
o.append(strip_parts(96, 200, 1728, 130, IP, 46))
xs, _ = sline(96, 200, IP, 46)
for k, (i, t_, c_, lv) in enumerate([(1, "패키지 (48)", K1, 0), (3, "모듈: 선형 모델 서랍", OR, 1), (5, "클래스: 대문자로 시작 (51)", GR, 0)]):
    o.append(lead_down(1 + k, xs[i] + tw(IP[i][0], 46) / 2, 310, 370 + lv * 60, c_, t_, 26))
DR = [("LinearRegression", "48, 50", "점수 같은 숫자", GRAY, False), ("SGDRegressor", "49, 51", "숫자, 조금씩 고쳐 가며", GRAY, False), ("LogisticRegression", "오늘", "True, False와 그 확률", GR, True)]
o.append(label(96, 520, "linear_model 서랍 안", SUB, 26, fade(4)))
for i, (m, ch, d, c_, new) in enumerate(DR):
    x = 96 + i * 588
    o.append(f'<div{rise(4) + DELAY(i * 90)} style="position:absolute;left:{x}px;top:570px;width:552px;height:250px;border-radius:18px;border:3px solid {c_ if new else LINE};background:{"#FFFFFF" if new else "#F1F0EC"};padding:26px 30px;display:flex;flex-direction:column;gap:14px">'
             + p(f"font-family:{MONO};font-size:34px;font-weight:700;color:{INK}", e(m)) + p(f"font-size:28px;color:{SUB}", "맞히는 것: " + e(d))
             + p(f"margin-top:auto;font-size:26px;font-weight:700;color:{c_ if new else GRAY}", e(ch)) + '</div>')
o.append(caption("세 모델 모두 가중치를 곱해 더해요. 그래서 같은 서랍에 있어요.", 900, 5))
W("import", o, "오늘 모델은 48에서 LinearRegression을 꺼낸 linear_model 서랍에 함께 들어 있어요. 이름은 LogisticRegression, 로지스틱 회귀예요. Regression, 회귀라는 말이 붙어 있지만 점수 같은 숫자를 맞히지 않아요. True와 False 중 하나를 고르는 분류 모델이에요. 앞의 Logistic은 S자 곡선의 이름인 로지스틱 함수에서 왔어요. 세 모델 모두 열마다 가중치를 곱해 더하는 계산을 해서 같은 서랍에 있어요. 51에서 본 것처럼 대문자로 시작하니 클래스예요. 괄호로 모델 객체를 만들어 써요.", ("p3", "모델 학습하기"))

o = [sec("model")] + head(EB3, "수업 셀 4: 표준화한 학습용 7명과 정답으로 fit해요", K3)
CFS[0] = 26
o += cell({"id": "c-model", "lines": MODELC, "n": 8, "out": MODELO}, 96, 196, 1180, sel="c-model")
o.append(tint(1, cx(96, "model = LogisticRegression(") - 2, ly(196, 3) - LH() / 2, tw("max_iter=1000") + 4, LH(), OR))
o.append(tag(cx(96, MODELC[3]) + 30, ly(196, 3), "걸음 수 한도 (49의 반복)", OR, 1, 26))
o.append(tint(2, cx(96, "model.fit(") - 2, ly(196, 4) - LH() / 2, tw("X_train_scaled") + 4, LH(), TR))
o.append(tint(2, cx(96, "model.fit(X_train_scaled, ") - 2, ly(196, 4) - LH() / 2, tw("y_train") + 4, LH(), PS))
o.append(tag(cx(96, MODELC[4]) + 30, ly(196, 4), "문제 먼저, 정답 나중 (48)", TR, 2, 26))
M2Y = 196 + chight(8, 2) + 40
CFS[0] = 24
M100 = ["m100 = LogisticRegression()", "m100.fit(X_train_scaled, y_train)", 'print("기본값 100:", m100.coef_[0].round(3), m100.n_iter_)']
o += cell({"id": "c-m100", "lines": M100, "n": 9, "out": ["기본값 100: [ 0.873 -0.37   0.877] [6]"]}, 96, M2Y, 1180, attrs=rise(3))
o.append(box(4, cx(96, "기본값 100: [ 0.873 -0.37   0.877] ", True) - 8, oy(M2Y, 3, 0) - LH() / 2 - 4, tw("[6]") + 16, LH() + 8, RED, 4))
o.append(label(1400, 610, "실제로 걸은 횟수", SUB, 28, fade(4)))
o.append(bigval(1400, 680, "6번", INK, 150, fade(4)))
o.append(note(1400, 880, 420, "한도 1000이든 기본값 100이든 6번에 멈춰서 결과가 같아요.", INK, 26, fade(4)))
W("model", o, "수업 노트북의 셀 4예요. LogisticRegression 괄호 안의 max_iter는 최대 반복 횟수예요. 49에서 경사 하강법이 조금씩 고쳐 가며 걸었던 걸음 수의 한도예요. 1000이라고 적으면 1000번까지 걸어도 된다는 뜻이에요. fit에는 51처럼 표준화한 학습용 표를 먼저, 정답 y_train을 나중에 넣어요. 아래 셀은 max_iter를 빼고 기본값 100으로 학습한 거예요. n_iter_는 실제로 걸은 횟수인데 6번이에요. 6번 만에 더 고칠 곳이 없어서 멈췄어요. 그래서 가중치가 똑같아요. 학생이 7명뿐이라 금방 끝나요. 데이터가 크면 100번으로 모자랄 때가 있어서 수업처럼 넉넉히 적어 둬요." + REAL)

o = [sec("classes")] + head(EB3, "classes_는 보기 두 개를 정렬한 순서예요. False가 0번, True가 1번", K3)
CL_ = [("model.classes_.tolist()", "#9CC2F5"), ("  →  ", "#9AA0AB"), ("[False, True]", "#F2C46D")]
o.append(strip_parts(96, 200, 1728, 120, CL_, 46))
xs, _ = sline(96, 200, CL_, 46)
o.append(p(f"position:absolute;left:{xs[2] + tw('[', 46):.0f}px;top:{260 - 33:.0f}px;font-family:{MONO};font-size:46px;font-weight:700;line-height:69px;color:transparent;white-space:pre", "False", ' id="cf"'))
o.append(p(f"position:absolute;left:{xs[2] + tw('[False, ', 46):.0f}px;top:{260 - 33:.0f}px;font-family:{MONO};font-size:46px;font-weight:700;line-height:69px;color:transparent;white-space:pre", "True", ' id="ct"'))
for k, (v, t_, c_, bg, src) in enumerate([("False", "불합격", FA, FAB, "cf"), ("True", "합격", PS, PSB, "ct")]):
    x = 300 + k * 700
    o.append(p(f"position:absolute;left:{x}px;top:420px;width:520px;text-align:center;font-size:30px;font-weight:700;color:{GRAY}", f"{k}번 칸", fade(1)))
    o.append(f'<div{fly(1, src)} style="position:absolute;left:{x}px;top:470px;width:520px;height:220px;border-radius:22px;border:4px solid {c_};background:{bg};display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px">'
             + p(f"font-family:{MONO};font-size:64px;font-weight:700;color:{c_}", v) + p(f"font-size:34px;font-weight:700;color:{INK}", t_) + '</div>')
o.append(note(300, 740, 1220, "False는 0, True는 1이라서(12) 작은 쪽인 False가 먼저 서요.", INK, 30, fade(2)))
o.append(caption("4파트의 predict_proba가 이 순서로 두 칸을 줘요. 1번 칸이 합격 확률이에요.", 900, 3))
W("classes", o, "수업 셀 4의 첫 출력은 classes_예요. 모델이 y_train에서 본 보기를 정렬해서 담아요. 우리 y는 True와 False 두 가지라서 False, True 순서예요. 12에서 True는 1, False는 0으로 계산된다고 배웠죠. 작은 False가 0번 칸, True가 1번 칸이에요. tolist()는 배열을 리스트로 바꿔 찍으려고 붙였어요. 이 순서가 왜 중요한지는 4파트에서 봐요. predict_proba가 확률 두 개를 이 순서대로 줘서, 1번 칸이 합격 확률이 돼요." + REAL)

o = [sec("coef")] + head(EB3, "coef_는 열마다 가중치, intercept_는 모두에게 더하는 값이에요", K3)
CFS[0] = 24
CFC = ['print("절편 :", model.intercept_.round(3))', 'print("반복 횟수:", model.n_iter_)', "print(model.coef_.shape)"]
o += cell({"id": "c-coef", "lines": CFC, "n": 10, "out": ["절편 : [0.447]", "반복 횟수: [6]", "(1, 3)"]}, 96, 196, 900, sel="c-coef")
o.append(box(1, cx(96, "", True) - 8, oy(196, 3, 2) - LH() / 2 - 4, tw("(1, 3)") + 16, LH() + 8, OR, 4))
o.append(tag(cx(96, "(1, 3)", True) + 30, oy(196, 3, 2), "1줄, 3칸이라서 coef_[0]으로 줄을 꺼내요", OR, 1, 24))
BX0, BW = 1080, 240
o.append(label(BX0 - 40, 214, "coef_  (1, 3)", OR, 28, fade(2)))
o.append(f'<div{fade(2)} style="position:absolute;left:{BX0 - 40}px;top:260px;width:{3 * BW + 40}px;height:150px;border:3px dashed {OR};border-radius:20px"></div>')
for k, (c, w) in enumerate(zip(CN3, WGT)):
    o.append(p(f"position:absolute;left:{BX0 - 20 + k * BW}px;top:276px;width:{BW - 20}px;text-align:center;font-family:{MONO};font-size:22px;color:{GRAY}", e(c), fade(2)))
    o.append(vbox(BX0 - 20 + k * BW, 316, BW - 20, 74, f"{w}", ZC, ZCB, 32, fade(2)))
GX0, GS = 1100, 520
GY0 = 560
o.append(label(96, GY0 - 70, "가중치가 미는 방향 (표준화한 값 1개마다)", SUB, 26, fade(3)))
o.append(f'<div{fade(3)} style="position:absolute;left:{GX0}px;top:{GY0 - 20}px;width:4px;height:{3 * 100 + 10}px;background:#9AA0AB"></div>')
o.append(label(GX0 + 20, GY0 - 64, "합격 쪽 →", PS, 24, fade(3)))
o.append(label(GX0 - 160, GY0 - 64, "← 불합격 쪽", FA, 24, fade(3)))
for k, (c, w) in enumerate(zip(["공부 시간", "수면 시간", "연습 횟수"], WGT)):
    y = GY0 + k * 100
    o.append(p(f"position:absolute;left:96px;top:{y + 4}px;width:420px;font-size:30px;font-weight:700;color:{INK}", f'{c} <span style="font-family:{MONO};font-size:24px;color:{GRAY}">{CN3[k]}</span>', fade(3)))
    if w > 0:
        o.append(bar(GX0 + 4, y, w * GS, 52, PS, WIPE(3) + DELAY(k * 120)))
        o.append(label(GX0 + 16 + w * GS, y + 8, f"+{w}", PS, 30, fade(3) + DELAY(k * 120)))
    else:
        o.append(bar(GX0 + w * GS, y, -w * GS, 52, FA, WIPE(3) + DELAY(k * 120)))
        o.append(label(GX0 + w * GS - 110, y + 8, f"{w}", FA, 30, fade(3) + DELAY(k * 120)))
o.append(caption("절편 0.447은 세 열을 곱해 더한 뒤 누구에게나 똑같이 더해요.", 930, 4))
W("coef", o, "가중치를 더 들여다봐요. coef_의 모양은 (1, 3)이에요. 한 줄에 세 칸이 든 2차원 배열이라서, 수업 코드는 coef_ 대괄호 0으로 그 줄을 꺼냈어요. 14의 2차원 리스트에서 첫 줄을 꺼내던 것과 같아요. 세 칸은 X의 열 순서대로 공부 시간, 수면 시간, 연습 횟수의 가중치예요. 플러스면 그 값이 클수록 합격 쪽으로 밀고, 마이너스면 불합격 쪽으로 밀어요. 표준화한 값에 곱하는 가중치라서 1시간마다가 아니라 표준편차 하나마다의 크기예요. intercept_는 50의 절편처럼 모든 학생에게 똑같이 더하는 값 0.447이에요. 수면의 마이너스는 5파트에서 조심해서 읽어요." + EXTRA + REAL)


# ---------- part 1: the basic ideas ----------
o = [sec("kinds")] + head(EB1, "회귀는 '얼마'를, 분류는 '어느 쪽'을 맞혀요", K1)
KC = [("회귀", "답이 숫자예요. 사이 값도 다 답이 돼요", K1, K1BG, [("공부 시간으로 점수 맞히기", "76점, 76.5점 …", "50, 51"), ("면적으로 오피스텔 가격 맞히기", "3만 1천, 3만 2천 …", "48")]),
      ("분류", "답이 정해진 보기 중 하나예요", PS, PSB, [("점수가 60점을 넘을지 맞히기", "합격 또는 불합격", "오늘"), ("사진 속 사람이 누구인지 맞히기", "40명 중 한 명", "52")])]
for k, (h_, d_, c_, bg, ex) in enumerate(KC):
    x = 96 + k * 884
    o.append(f'<div{rise(1 + 2 * k)} style="position:absolute;left:{x}px;top:210px;width:844px;height:150px;border-radius:22px;background:{bg};border:4px solid {c_};display:flex;flex-direction:column;justify-content:center;padding:0 40px;gap:8px">'
             + p(f"font-size:56px;font-weight:900;color:{c_}", e(h_)) + p(f"font-size:30px;font-weight:700;color:{INK}", e(d_)) + '</div>')
    for j, (q_, a_, ch) in enumerate(ex):
        y = 400 + j * 130
        o.append(f'<div{rise(2 + 2 * k) + DELAY(j * 120)} style="position:absolute;left:{x}px;top:{y}px;width:844px;height:110px;border-bottom:2px solid {LINE};display:flex;flex-direction:row;align-items:center;gap:24px">'
                 + '<div style="flex:1;display:flex;flex-direction:column;gap:6px">' + p(f"font-size:30px;font-weight:700;color:{INK}", e(q_)) + p(f"font-size:26px;color:{c_};font-weight:700", "답: " + e(a_)) + '</div>'
                 + p(f"font-size:24px;font-weight:700;color:{GRAY}", e(ch)) + '</div>')
NLY = 760
o.append(f'<div{fade(5)} style="position:absolute;left:96px;top:{NLY + 40}px;width:744px;height:6px;border-radius:3px;background:{K1}"></div>')
for v in [0, 25, 50, 75, 100]:
    o.append(p(f"position:absolute;left:{96 + v * 7.44 - 30:.0f}px;top:{NLY + 60}px;width:60px;text-align:center;font-family:{MONO};font-size:22px;color:{GRAY}", str(v), fade(5)))
o.append(label(96, NLY - 40, "답이 줄 위 어디든 될 수 있어요", K1, 26, fade(5)))
for k, (t_, c_, bg) in enumerate([("False", FA, FAB), ("True", PS, PSB)]):
    o.append(p(f"position:absolute;left:{980 + k * 300}px;top:{NLY + 20}px;width:240px;height:80px;border-radius:16px;background:{bg};border:3px solid {c_};font-family:{MONO};font-size:34px;font-weight:700;line-height:74px;text-align:center;color:{c_}", t_, fade(6)))
o.append(label(980, NLY - 40, "답은 두 칸 중 하나예요", PS, 26, fade(6)))
o.append(caption("로지스틱 회귀는 이름에 '회귀'가 있어도 분류를 해요.", 930, 7))
W("kinds", o, "머신러닝 문제는 정답의 모양에 따라 크게 둘로 나눠요. 정답이 76점, 76.5점처럼 숫자이고 그 사이 값도 모두 답이 될 수 있으면 회귀예요. 50과 51의 점수 맞히기, 48의 오피스텔 가격이 회귀였어요. 정답이 정해진 보기 중 하나이면 분류예요. 오늘의 합격과 불합격이 분류예요. 52에서 사진 속 사람이 누구인지 맞힌 것도 분류예요. 헷갈리면 이렇게 물어봐요. 답을 '얼마'로 물으면 회귀, '어느 쪽'으로 물으면 분류예요. 오늘 배우는 로지스틱 회귀는 이름과 달리 분류 모델이에요.")

o = [sec("prob")] + head(EB1, "확률은 0과 1 사이의 숫자예요. 0.48은 100번 중 48번꼴이에요", K1)
GX, GY, GC = 96, 220, 52
for k in range(100):
    r_, c_ = divmod(k, 10)
    on = k < 48
    o.append(f'<div{fade(1) + DELAY(r_ * 60) if on else ""} style="position:absolute;left:{GX + c_ * GC}px;top:{GY + r_ * GC}px;width:{GC - 8}px;height:{GC - 8}px;border-radius:8px;background:{PC if on else "#E4E2DC"}"></div>')
o.append(label(GX, GY + 10 * GC + 12, "똑같은 학생 100명이라면 48명쯤 합격", PC, 28, fade(1)))
SX0, SW, SY = 760, 1000, 330
o.append(f'<div style="position:absolute;left:{SX0}px;top:{SY}px;width:{SW}px;height:16px;border-radius:8px;background:linear-gradient(90deg,#E4E2DC,{PC})"></div>')
for v, t_ in [(0, "절대 안 일어나요"), (0.5, "반반이에요"), (1, "꼭 일어나요")]:
    x = SX0 + v * SW
    o.append(f'<div style="position:absolute;left:{x - 3:.0f}px;top:{SY - 14}px;width:6px;height:44px;background:{INK}"></div>')
    o.append(p(f"position:absolute;left:{x - 140:.0f}px;top:{SY + 44}px;width:280px;text-align:center;font-family:{MONO};font-size:34px;font-weight:700;color:{INK}", f"{v:g}"))
    o.append(p(f"position:absolute;left:{x - 140:.0f}px;top:{SY + 94}px;width:280px;text-align:center;font-size:26px;color:{SUB}", e(t_)))
o.append(p(f"position:absolute;left:{SX0 + 0.48 * SW - 20:.0f}px;top:{SY - 76}px;width:40px;height:40px;border-radius:50%;background:{PC};border:4px solid #FFFFFF;box-shadow:0 0 0 3px {PC}", "", rise(2)))
o.append(label(SX0 + 0.48 * SW - 60, SY - 126, "0.48 = 48%", PC, 30, rise(2)))
RW_ = [("0.48", "48%", "100을 곱하면 퍼센트"), ("합격 0.48 + 불합격 0.52", "1", "둘 중 하나는 꼭 일어나요")]
for k, (a_, b_, c_) in enumerate(RW_):
    y = 600 + k * 120
    o.append(f'<div{rise(3 + k)} style="position:absolute;left:{SX0}px;top:{y}px;width:{SW}px;height:100px;display:flex;flex-direction:row;align-items:center;gap:26px;border-bottom:2px solid {LINE}">'
             + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:{INK};white-space:nowrap", e(a_)) + p(f"font-size:30px;font-weight:700;color:{GRAY}", "=")
             + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:{PC}", e(b_)) + p(f"margin-left:auto;font-size:26px;color:{SUB}", e(c_)) + '</div>')
o.append(caption("모델이 '불합격'이라고 답해도, 48%면 거의 반반이라는 뜻이에요.", 930, 5))
W("prob", o, "확률은 어떤 일이 얼마나 일어날 것 같은지를 0과 1 사이의 숫자로 적은 거예요. 0이면 절대 안 일어나고, 1이면 꼭 일어나고, 0.5면 반반이에요. 100을 곱하면 퍼센트가 돼서 0.48은 48%예요. 똑같은 조건의 학생이 100명 있다면 그중 48명쯤 합격한다는 느낌으로 읽어요. 보기가 합격과 불합격 둘뿐이면 두 확률을 더해 1이 돼요. 합격이 0.48이면 불합격은 0.52예요. 오늘 모델은 이 확률을 알려 줘서, 답이 불합격이어도 48%처럼 아슬아슬한지, 5%처럼 확실한지 구별할 수 있어요. 0.48은 4파트의 새 학생 값을 반올림한 거예요.")

# ---------- part 4 ----------
o = [sec("new")] + head(EB4, "수업 셀 6: 새 학생을 학습 때와 같은 모양의 표로 만들어요", K4)
CFS[0] = 22
o += cell({"id": "c-new", "lines": NEWC, "n": 11, "out": NEWO}, 96, 196, 1060, sel="c-new")
o.append(lspot(1, 96 + 87, 196, 1060 - 87, 12 * LH() + 20, 196 + 10, 5 * LH(), "#FFFFFF", PC))
RX = 1240
o.append(p(f"position:absolute;left:{RX}px;top:230px;font-family:{MONO};font-size:56px;font-weight:700;color:{INK};white-space:pre",
           f'<span style="color:{K1}">[</span><span style="color:{OR}">[4, 7, 5]</span><span style="color:{K1}">]</span>', fade(2)))
o.append(label(RX, 330, "바깥 [ ]: 줄들을 담는 리스트", K1, 26, fade(2)))
o.append(label(RX, 376, "안쪽 [ ]: 학생 한 명 = 한 줄", OR, 26, fade(2)))
o.append(label(RX, 450, "columns=X.columns: 열 이름 셋을 그대로", SUB, 26, fade(3)))
o.append(label(RX, 496, "transform: 학습용 자로 바꿔요 (51)", TR, 26, fade(3)))
o.append(lspot_off(4))
o.append(df("t-new", 96, 790, CN3, [(4, 7, 5)], [210, 210, 250], 28, 56, iw=60, attrs=rise(2)))
o.append(label(96, 740, "new 표 (1줄, 3열)", INK, 26, rise(2)))
o.append(tag(96 + 60 + 670 + 60, 790 + 56 + 28, "공부 4시간, 수면 7시간, 연습 5번", OR, 2, 28))
W("new", o, "수업 노트북의 셀 6이에요. 새 학생 한 명을 예측하려면 학습할 때와 같은 모양의 표가 필요해요. 대괄호가 두 겹인 이유가 여기 있어요. 바깥 대괄호는 줄들을 담는 리스트이고, 안쪽 대괄호 하나가 학생 한 명, 표의 한 줄이에요. 한 명뿐이라도 표는 줄의 목록이라서 두 겹으로 적어요. columns=X.columns로 열 이름을 X와 똑같이 붙여요. 50에서 본 것처럼 열 이름과 순서가 달라지면 안 돼요. 그다음 51처럼 학습용으로 만든 자로 transform해요. 아래 세 줄의 predict와 predict_proba는 다음 장부터 하나씩 봐요." + REAL)

o = [sec("zsum")] + head(EB4, "합계 -0.065: 표준화한 값에 가중치를 곱해 더하고, 절편을 더해요", K4)
CFS[0] = 22
ZSC = ["print(new_scaled.round(2))", "print((model.coef_[0] * new_scaled[0]).round(3))", "z = (model.coef_[0] * new_scaled[0]).sum() + model.intercept_[0]", "print(z.round(3))",
       "print(model.decision_function(new_scaled).round(3))"]
o += cell({"id": "c-zs", "lines": ZSC, "n": 12, "out": ["[[ 1.21  0.13 -1.74]]", "[ 1.059 -0.047 -1.524]", "-0.065", "[-0.065]"]}, 96, 190, 1300, sel="c-zs")
o.append(tag(1430, ly(190, 2), "45의 배열 곱하기: 칸끼리", GRAY, 1, 24))
o.append(tag(1430, ly(190, 4), "모델이 계산한 합계", ZC, 1, 24))
TY0, CW_ = 590, [330, 230, 80, 230, 80, 260]
HDR = ["", "표준화 값", "", "가중치", "", "곱한 값"]
o.append(f'<div{fade(2)} style="position:absolute;left:96px;top:{TY0}px;width:1300px;height:44px;display:flex;flex-direction:row;border-bottom:3px solid {INK}">'
         + "".join(p(f"width:{w}px;flex:none;text-align:right;font-size:24px;font-weight:700;color:{GRAY}", e(h)) for h, w in zip(HDR, CW_)) + '</div>')
ZR = [("공부 시간", "1.21", "×", "0.873", "=", "1.059"), ("수면 시간", "0.13", "×", "-0.37", "=", "-0.047"), ("연습 횟수", "-1.74", "×", "0.877", "=", "-1.524"), ("절편", "", "", "", "+", "0.447")]
for k, r in enumerate(ZR):
    y = TY0 + 52 + k * 58
    cells_ = "".join(p(f"width:{w}px;flex:none;text-align:right;font-family:{SANS if j == 0 else MONO};font-size:30px;font-weight:700;color:{ZC if j == 5 else (GRAY if j in (2, 4) else INK)}", e(c))
                     for j, (c, w) in enumerate(zip(r, CW_)))
    o.append(f'<div{rise(2 + k)} style="position:absolute;left:96px;top:{y}px;width:1300px;height:58px;display:flex;flex-direction:row;align-items:center;border-bottom:2px solid {LINE}">{cells_}</div>')
SY_ = TY0 + 52 + 4 * 58 + 14
o.append(f'<div{rise(6)} style="position:absolute;left:96px;top:{SY_}px;width:1300px;height:76px;display:flex;flex-direction:row;align-items:center;border-top:4px solid {ZC};background:{ZCB}">'
         + p(f"width:{sum(CW_[:5])}px;flex:none;text-align:right;font-size:32px;font-weight:900;color:{ZC}", "합계") + p(f"width:{CW_[5]}px;flex:none;text-align:right;font-family:{MONO};font-size:40px;font-weight:900;color:{ZC}", "-0.065") + '</div>')
o.append(note(1460, 640, 370, "연습 5번은 학습용 평균보다 훨씬 적어서 -1.74가 됐고, 여기서 합계가 크게 깎였어요.", INK, 26, fade(5)))
W("zsum", o, "모델 안에서 일어나는 계산을 손으로 따라가 봐요. 새 학생을 표준화하면 1.21, 0.13, -1.74예요. 공부 시간은 평균보다 많고, 연습 5번은 학습용 평균보다 한참 적어서 크게 마이너스예요. 열마다 가중치를 곱하면 1.059, -0.047, -1.524예요. 45에서 배운 것처럼 배열끼리 곱하면 같은 칸끼리 곱해져요. 셋을 더하고 절편 0.447을 더하면 -0.065예요. 50의 predict가 하던 덧셈과 똑같아요. 모델의 decision_function을 부르면 같은 -0.065가 나와요. 차이는 다음이에요. 50은 이 합계를 그대로 답으로 냈지만, 로지스틱 회귀는 합계를 S자 곡선에 넣어요." + EXTRA + REAL)

o = [sec("sigmoid")] + head(EB4, "S자 곡선은 합계를 0과 1 사이의 확률로 바꿔요", K4)
SP = Plot(200, 240, 700, 550, (-5, 5), (0, 1))
o += SP.axes("가중치를 곱해 더한 합계", "합격 확률", ticks_x=(-4, -2, 0, 2, 4), ticks_y=(0, 0.5, 1), fs=24)
inner = [f'<line x1="{SP.X(-5):.0f}" y1="{SP.Y(0.5):.0f}" x2="{SP.X(5):.0f}" y2="{SP.Y(0.5):.0f}" stroke="#C9CED8" stroke-width="3" stroke-dasharray="10 8"/>',
         f'<line x1="{SP.X(-5):.0f}" y1="{SP.Y(1):.0f}" x2="{SP.X(5):.0f}" y2="{SP.Y(1):.0f}" stroke="#E4E2DC" stroke-width="3"/>', curve(SP, PC, 7)]
o.append(SP.svg("".join(inner), WIPE(1)))
pts = "".join(f'<circle cx="{SP.X(z):.1f}" cy="{SP.Y(sig(z)):.1f}" r="13" fill="{PC}"/>' for z in (-2, 0, 2))
o.append(SP.svg(pts, fade(2)))
o.append(SP.svg(f'<circle cx="{SP.X(-0.065):.1f}" cy="{SP.Y(sig(-0.065)):.1f}" r="17" fill="#FFFFFF" stroke="{ZC}" stroke-width="7"/>', fade(3)))
o.append(label(SP.X(-0.065) + 26, SP.Y(sig(-0.065)) + 10, "새 학생 -0.065 → 0.4838", ZC, 26, fade(3)))
o.append(label(SP.X(2) + 20, SP.Y(sig(2)) + 10, "2 → 0.88", PC, 24, fade(2)))
o.append(label(SP.X(-2) + 20, SP.Y(sig(-2)) + 4, "-2 → 0.12", PC, 24, fade(2)))
CFS[0] = 22
SGC = ["import numpy as np", "", "for z in [-2, -0.065, 0, 2]:", "    print(z, (1 / (1 + np.exp(-z))).round(4))"]
o += cell({"id": "c-sig", "lines": SGC, "n": 13, "out": ["-2 0.1192", "-0.065 0.4838", "0 0.5", "2 0.8808"]}, 1010, 250, 820, attrs=rise(4))
o.append(hl(1010, 250, 820, 3, 1, "skip", 4))
o.append(label(1010 + 87, 250 + chight(4, 4) + 20, "회색 줄은 곡선의 식이에요. 참고, 읽기만 해요.", GRAY, 24, fade(4)))
o.append(caption("합계가 0이면 딱 0.5, 클수록 1에, 작을수록 0에 가까워져요.", 930, 5))
W("sigmoid", o, "S자 곡선은 시그모이드 곡선이라고도 불러요. 가로축은 앞 장의 합계, 세로축은 합격 확률이에요. 합계가 0이면 확률은 딱 0.5예요. 합계가 2면 0.88, -2면 0.12예요. 합계가 클수록 1에, 작을수록 0에 가까워지지만 둘 다 넘지는 않아요. 새 학생은 합계가 -0.065로 0보다 조금 작아서 0.5보다 조금 아래인 0.4838이에요. 오른쪽 셀은 곡선의 계산을 파이썬으로 적은 거예요. 식을 외울 필요는 없어서 참고로 읽기만 해요. 모델은 이 계산을 알아서 해요. 0.4838은 반올림한 -0.065로 계산해서, 모델이 낸 0.4837과 끝자리가 조금 달라요." + EXTRA + REAL)

o = [sec("sigwhy")] + head(EB4, "합계가 아무리 커도 1을, 아무리 작아도 0을 넘지 않아요", K4)
CFS[0] = 22
SWC = ["import numpy as np", "", "for z in [-10, -5, -2, 0, 2, 5, 10]:", "    e = np.exp(-z)", '    print(f"합계 {z:3}: np.exp(-z) = {e:10.4f}, 확률 = {1 / (1 + e):.4f}")']
SWO = ["합계 -10: np.exp(-z) = 22026.4658, 확률 = 0.0000", "합계  -5: np.exp(-z) =   148.4132, 확률 = 0.0067", "합계  -2: np.exp(-z) =     7.3891, 확률 = 0.1192",
       "합계   0: np.exp(-z) =     1.0000, 확률 = 0.5000", "합계   2: np.exp(-z) =     0.1353, 확률 = 0.8808", "합계   5: np.exp(-z) =     0.0067, 확률 = 0.9933", "합계  10: np.exp(-z) =     0.0000, 확률 = 1.0000"]
o += cell({"id": "c-sw", "lines": SWC, "n": 14, "out": SWO}, 96, 190, 1200, sel="c-sw")
o.append(hl(96, 190, 1200, 3, 2, "skip", None))
o.append(label(96 + 87, 190 + chight(5, 7) + 20, "회색 두 줄은 곡선의 식이에요. 참고, 읽기만 해요.", GRAY, 24))
o.append(box(1, cx(96, "합계 -10: np.exp(-z) = ", True) - 8, oy(190, 5, 0) - LH() / 2 - 4, tw("22026.4658") + 16, LH() + 8, FA, 4))
o.append(box(2, cx(96, "합계  10: np.exp(-z) = ", True) - 8, oy(190, 5, 6) - LH() / 2 - 4, tw("    0.0000") + 16, LH() + 8, PS, 4))
RX = 1360
RS = [(1, "합계가 아주 작으면", "np.exp(-z)는 아주 큰 수", "1 ÷ (1 + 아주 큰 수)", "0에 가까워요", FA), (2, "합계가 아주 크면", "np.exp(-z)는 0에 가까운 수", "1 ÷ (1 + 0에 가까운 수)", "1에 가까워요", PS),
      (3, "합계가 0이면", "np.exp(-z)는 1", "1 ÷ (1 + 1)", "딱 0.5", PC)]
for k, (od, a_, b_, c_, d_, col) in enumerate(RS):
    y = 200 + k * 250
    o.append(f'<div{rise(od)} style="position:absolute;left:{RX}px;top:{y}px;width:470px;height:226px;border-left:6px solid {col};padding:6px 0 6px 24px;display:flex;flex-direction:column;gap:8px">'
             + p(f"font-size:28px;font-weight:700;color:{INK}", e(a_)) + p(f"font-size:24px;color:{SUB}", e(b_)) + p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{INK}", e(c_))
             + p(f"font-size:30px;font-weight:900;color:{col}", e(d_)) + '</div>')
o.append(caption("1을 늘 1보다 큰 수로 나누니 1을 못 넘고, 양수끼리 나누니 0 밑으로 안 가요.", 950, 4))
W("sigwhy", o, "S자 곡선이 왜 0과 1 밖으로 못 나가는지 숫자로 확인해 봐요. 곡선은 1을 '1 더하기 np.exp(-z)'로 나눠요. np.exp(-z)는 합계가 클수록 작아지고, 작을수록 커지는 수예요. 0보다 작아지지는 않아요. 합계가 -10처럼 아주 작으면 np.exp(-z)가 2만이 넘어서, 1을 아주 큰 수로 나눈 확률은 0에 가까워요. 합계가 10처럼 아주 크면 np.exp(-z)가 0에 가까워서, 1을 1보다 아주 조금 큰 수로 나눈 확률은 1에 가까워요. 나누는 수가 늘 1보다 크니 1을 넘지 못하고, 결과가 마이너스가 될 일도 없어요. 출력의 0.0000과 1.0000은 소수 넷째 자리에서 반올림해서 그렇게 보일 뿐, 실제로 0이나 1이 되지는 않아요. 직선과 달리 이 곡선은 확률로 읽을 수 있어요. 식은 참고로만 읽어요." + EXTRA + REAL)

o = [sec("predict")] + head(EB4, "predict는 답을 배열로 줘요. 한 명이라 [0]으로 꺼내요", K4)
PP = [("predict", "#B8E8BE"), (" = ", W_), ("model.predict(new_scaled)", "#9CC2F5"), ("[0]", "#F2C46D")]
o.append(strip_parts(96, 200, 1728, 120, PP, 46))
xs, _ = sline(96, 200, PP, 46)
o.append(lead_down(1, xs[2] + tw(PP[2][0], 46) / 2, 300, 416, K1, "학생 여러 명을 받아 답도 여러 개", 26))
o.append(lead_down(2, xs[3] + tw(PP[3][0], 46) / 2, 300, 356, OR, "0번 칸 하나", 26))
CHY = 580
o.append(flowbox(96, CHY, 330, 110, "[False]", K1, K1BG, 40, fade(1), tid="pa"))
o.append(label(96, CHY + 130, "배열 (답 1개)", K1, 26, fade(1)))
o.append(arrow(90, "#9AA0AB", WIPE(2), f"position:absolute;left:450px;top:{CHY + 40}px"))
o.append(label(452, CHY - 46, "[0]", OR, 30, fade(2), True))
o.append(p(f"position:absolute;left:570px;top:{CHY}px;width:300px;height:110px;border-radius:14px;border:3px solid {FA};background:{FAB};font-family:{MONO};font-size:44px;font-weight:700;line-height:104px;text-align:center;color:{FA}", "False", fly(2, "pa")))
o.append(label(570, CHY + 130, "값 하나", FA, 26, fade(2)))
o.append(arrow(90, "#9AA0AB", WIPE(3), f"position:absolute;left:894px;top:{CHY + 40}px"))
o.append(p(f"position:absolute;left:1010px;top:{CHY - 56}px;font-family:{MONO};font-size:28px;font-weight:700;color:{INK};white-space:pre", e('"합격" if predict else "불합격"'), fade(3)))
o.append(flowbox(1010, CHY, 360, 110, "불합격", FA, FAB, 44, fade(3), mono_=False))
o.append(label(1010, CHY + 130, "17의 한 줄 if: False라서 else 쪽", SUB, 26, fade(3)))
o.append(caption("모델은 합격 확률 48.37%가 0.5보다 작아서 False라고 답했어요.", 930, 4))
W("predict", o, "predict는 학생 여러 명을 한꺼번에 받을 수 있어서 답도 배열로 돌려줘요. 오늘은 한 명만 넣었으니 칸이 하나인 배열 [False]가 나와요. 뒤에 대괄호 0을 붙이면 그 칸의 값 False 하나가 꺼내져요. 수업 코드는 이 값을 predict라는 변수에 담고, 17에서 배운 한 줄 if로 글자를 골랐어요. predict가 True면 '합격', 아니면 '불합격'이에요. False라서 불합격이 찍혔어요. 모델이 False라고 답한 이유는 합격 확률 48.37%가 기준 0.5보다 작기 때문이에요. 확률은 다음 장에서 꺼내요." + REAL)

o = [sec("proba")] + head(EB4, "predict_proba는 두 칸을 줘요. classes_ 순서대로 불합격, 합격", K4)
CFS[0] = 28
PBC1 = ["print(model.predict(new_scaled))", "print(model.predict_proba(new_scaled))"]
o += cell({"id": "c-pb1", "lines": PBC1, "n": 15, "out": ["[False]", "[[0.51633177 0.48366823]]"]}, 96, 196, 940, sel="c-pb1")
PB2Y = 196 + chight(2, 2) + 30
PBC2 = ["print(model.predict_proba(new_scaled)[0])", "print(model.predict_proba(new_scaled)[0, 1])"]
o += cell({"id": "c-pb2", "lines": PBC2, "n": 16, "out": ["[0.51633177 0.48366823]", "0.48366823060259606"]}, 96, PB2Y, 940, attrs=rise(3))
o.append(tag(cx(96, "[0.51633177 0.48366823]", True) + 24, oy(PB2Y, 2, 0), "[0]: 0번 줄", GRAY, 3, 26))
o.append(tag(96 + 85, oy(PB2Y, 2, 1) + 70, "[0, 1]: 0번 줄의 1번 칸 (iloc처럼 줄 번호, 칸 번호)", PC, 3, 28, lead=False))
GX0 = 1100
o.append(label(GX0, 212, "predict_proba 결과 (1줄, 2칸)", SUB, 26, fade(1)))
for k, (hd, v, t_, c_, bg) in enumerate([("0번 칸: False", "0.5163", "불합격 확률", FA, FAB), ("1번 칸: True", "0.4837", "합격 확률", PC, PCB)]):
    x = GX0 + k * 370
    o.append(p(f"position:absolute;left:{x}px;top:262px;width:340px;text-align:center;font-family:{MONO};font-size:24px;font-weight:700;color:{GRAY}", e(hd), fade(2)))
    o.append(f'<div{fade(1)} id="pb{k}" style="position:absolute;left:{x}px;top:306px;width:340px;height:170px;border-radius:18px;border:4px solid {c_};background:{bg};display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px">'
             + p(f"font-family:{MONO};font-size:48px;font-weight:700;color:{INK}", v) + p(f"font-size:28px;font-weight:700;color:{c_}", e(t_)) + '</div>')
o.append(label(GX0, 500, "classes_가 [False, True]라서 이 순서예요 (3파트)", SUB, 24, fade(2)))
o.append(box(3, GX0 + 370 - 10, 296, 360, 190, PC, 6, 22))
o.append(p(f"position:absolute;left:{GX0}px;top:620px;font-family:{MONO};font-size:34px;font-weight:700;color:{INK};white-space:pre", e('f"{pass_proba:.2%}"'), fade(4)))
o.append(label(GX0, 680, "100을 곱해 소수 둘째 자리까지, 끝에 % (13의 :.2f와 비슷해요)", SUB, 24, fade(4)))
o.append(bigval(GX0, 760, "48.37%", PC, 150, fade(4)))
o.append(caption("두 칸을 더하면 1이에요. 합격 확률은 1번 칸이라 [0, 1]로 꺼내요.", 950, 5))
W("proba", o, "predict_proba는 확률을 꺼내요. proba는 probability, 확률의 줄임말이에요. 결과는 대괄호가 두 겹인 표 모양이에요. 학생 한 명이라 줄은 하나, 보기가 둘이라 칸은 둘이에요. 칸 순서는 3파트에서 본 classes_ 순서라서 0번 칸이 False, 곧 불합격 확률 0.5163이고 1번 칸이 True, 합격 확률 0.4837이에요. 대괄호 0만 쓰면 줄 하나가 통째로 나와요. 대괄호 안에 0, 1을 쓰면 0번 줄의 1번 칸, 합격 확률 하나가 나와요. 셀 2의 iloc처럼 줄 번호, 칸 번호 순서예요. 이 값을 f-string에서 :.2%로 찍으면 100을 곱해 소수 둘째 자리까지 퍼센트로 보여 줘서 48.37%가 돼요." + REAL)

o = [sec("threshold")] + head(EB4, "기준 0.5는 '두 확률 중 더 큰 쪽'으로 답한다는 뜻이에요", K4)
CFS[0] = 22
PSC = ["two = model.predict_proba(new_scaled)[0]", 'print("불합격 확률:", two[0].round(4))', 'print("합격 확률:", two[1].round(4))', 'print("더하면:", two.sum().round(4))']
o += cell({"id": "c-ps", "lines": PSC, "n": 17, "out": ["불합격 확률: 0.5163", "합격 확률: 0.4837", "더하면: 1.0"]}, 96, 196, 900, sel="c-ps")
BX, BWW = 1080, 740
o.append(label(BX, 210, "새 학생의 두 확률", SUB, 26))
o.append(f'<div style="position:absolute;left:{BX}px;top:260px;width:{BWW}px;height:80px;display:flex;flex-direction:row;border-radius:14px;overflow:hidden">'
         f'<div style="width:{BWW * 0.5163:.0f}px;background:{FA};display:flex;align-items:center;padding-left:20px"><p style="font-size:28px;font-weight:700;color:#FFFFFF">불합격 51.63%</p></div>'
         f'<div style="flex:1;background:{PC};display:flex;align-items:center;justify-content:flex-end;padding-right:20px"><p style="font-size:28px;font-weight:700;color:#FFFFFF">합격 48.37%</p></div></div>')
o.append(vline(BX + BWW / 2, 240, 360, INK, 4, "8 6", fade(1)))
o.append(label(BX + BWW / 2 - 60, 370, "가운데 0.5", INK, 24, fade(1)))
o.append(note(BX, 420, BWW, "두 칸의 합이 1이라서, 합격 확률이 0.5보다 크면 합격 쪽이 더 커요. 작으면 불합격 쪽이 커요.", INK, 28, fade(2)))
TP_ = Plot(160, 720, 1600, 10, (0.4, 1), (0, 1))
TY = 740
o.append(f'<div{fade(3)} style="position:absolute;left:{TP_.X(0.4):.0f}px;top:{TY - 110}px;width:{TP_.X(0.5) - TP_.X(0.4):.0f}px;height:136px;background:{FAB}"></div>')
o.append(f'<div{fade(3)} style="position:absolute;left:{TP_.X(0.5):.0f}px;top:{TY - 110}px;width:{TP_.X(1) - TP_.X(0.5):.0f}px;height:136px;background:{PSB}"></div>')
o.append(label(TP_.X(0.4) + 14, TY - 104, "False로 답해요", FA, 24, fade(3)))
o.append(label(TP_.X(1) - 190, TY - 104, "True로 답해요", PS, 24, fade(3)))
o.append(f'<div{fade(3)} style="position:absolute;left:{TP_.X(0.4):.0f}px;top:{TY}px;width:{TP_.X(1) - TP_.X(0.4):.0f}px;height:4px;background:#9AA0AB"></div>')
for v in [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]:
    o.append(p(f"position:absolute;left:{TP_.X(v) - 40:.0f}px;top:{TY + 70}px;width:80px;text-align:center;font-family:{MONO};font-size:24px;font-weight:700;color:{GRAY}", f"{v:g}", fade(3)))
for k, (v, t_, up) in enumerate([(0.459, "0.459", False), (0.4837, "새 학생 0.4837", True), (0.502, "0.502", False), (0.941, "0.941", True), (0.95, "0.95", False)]):
    c_ = PS if v >= 0.5 else FA
    o.append(p(f"position:absolute;left:{TP_.X(v) - 16:.0f}px;top:{TY - 14}px;width:32px;height:32px;border-radius:50%;background:{c_};border:3px solid #FFFFFF", "", rise(4) + DELAY(k * 80)))
    o.append(p(f"position:absolute;left:{TP_.X(v) - 230 if (v < 0.5 or v > 0.9) else TP_.X(v) - 10:.0f}px;top:{TY - 58 if up else TY + 28}px;width:240px;text-align:{'right' if (v < 0.5 or v > 0.9) else 'left'};font-family:{MONO};font-size:24px;font-weight:700;color:{c_}", e(t_), rise(4) + DELAY(k * 80)))
o.append(caption("0.502처럼 0.5를 조금만 넘어도 True예요. 확률을 같이 보면 아슬아슬한지 알 수 있어요.", 950, 5))
W("threshold", o, "모델은 왜 0.5를 기준으로 답할까요. 보기가 둘이면 두 확률을 더해 1이에요. 셀에서도 0.5163과 0.4837을 더하면 1.0이에요. 그래서 합격 확률이 0.5보다 크면 합격 쪽 확률이 불합격 쪽보다 커지고, 모델은 더 그럴듯한 쪽인 True로 답해요. 0.5보다 작으면 False예요. 아래 줄에는 이 덱에 나오는 학생들의 합격 확률을 찍었어요. 점이 몰려 있어서 줄은 0.4부터 그렸어요. 0.459, 0.941, 0.95는 다음 장의 채점용 3명이고, 0.502는 6파트에서 만날 학생이에요. 0.502는 0.5를 아주 조금 넘었을 뿐인데 True예요. 그래서 답만 보지 말고 확률도 같이 봐야 해요. 0.5 말고 다른 기준을 쓰는 방법도 있지만 오늘은 다루지 않아요." + EXTRA + REAL)

o = [sec("score")] + head(EB4, "채점용 3명: 모두 맞혀서 score는 1.0이에요", K4)
CFS[0] = 22
SCO = ['print("정답:", list(y_test))', 'print("예측:", model.predict(X_test_scaled))', 'print("합격 확률:", model.predict_proba(X_test_scaled)[:, 1].round(3))', 'print("정확도:", model.score(X_test_scaled, y_test))']
o += cell({"id": "c-score", "lines": SCO, "n": 18, "out": ["정답: [False, True, True]", "예측: [False  True  True]", "합격 확률: [0.459 0.941 0.95 ]", "정확도: 1.0"]}, 96, 190, 1300, sel="c-score")
o.append(tint(1, cx(96, 'print("합격 확률:", model.predict_proba(X_test_scaled)') - 2, ly(190, 2) - LH() / 2, tw("[:, 1]") + 4, LH(), PC))
o.append(tag(1420, ly(190, 2), "[:, 1]: 모든 줄(:)의 1번 칸", PC, 1, 24))
SR = [(5, 49, False, 0.459), (7, 77, True, 0.941), (4, 87, True, 0.95)]
RY0, BX0, BW0 = 600, 520, 760
o.append(vline(BX0 + BW0 * 0.5, RY0 - 20, RY0 + 3 * 100 - 10, INK, 3, "8 6", fade(3)))
o.append(label(BX0 + BW0 * 0.5 - 30, RY0 - 56, "0.5", INK, 24, fade(3)))
for k, (i, sc, ok, pv) in enumerate(SR):
    y = RY0 + k * 100
    o.append(disc(i, 96, y, ok, 64, rise(3) + DELAY(k * 100), ring_=TE))
    o.append(label(186, y + 14, f"{sc}점, 정답 {ok}", PS if ok else FA, 28, rise(3) + DELAY(k * 100)))
    o.append(bar(BX0, y + 12, BW0 * pv, 40, PC, WIPE(3) + DELAY(k * 100)))
    o.append(label(BX0 + BW0 * pv + 14, y + 14, f"{pv:.1%}", PC, 28, fade(3) + DELAY(k * 100)))
    o.append(label(BX0 + BW0 + 140, y + 12, "✓", GR, 36, fade(4) + DELAY(k * 100)))
o.append(label(1530, 420, "score", SUB, 28, fade(5)))
o.append(bigval(1530, 490, "1.0", INK, 150, fade(5)))
o.append(label(1530, 680, "3명 중 3명", SUB, 28, fade(5)))
o.append(caption("49점 학생은 45.9%로 아슬아슬하게 맞혔어요. 3명뿐이라 점수는 운도 섞여요.", 950, 6))
W("score", o, "채점용 3명으로 채점해요. 51처럼 predict에 X_test_scaled를 넣어요. 정답은 False, True, True이고 예측도 똑같아요. predict_proba 뒤의 대괄호 :, 1은 모든 줄의 1번 칸이라는 뜻이에요. 46의 loc에서 콜론이 모든 행이었던 것과 같아요. 학생 세 명의 합격 확률만 쏙 뽑혀요. model.score는 분류 모델에서 맞힌 비율을 줘요. 3명 중 3명을 맞혀 1.0이에요. 회귀 모델의 score가 R제곱이었던 것과 달라요. 49점인 5번 학생은 합격 확률이 45.9%라서 0.5에 아주 가까웠어요. 채점용이 3명뿐이라 1.0이 실력의 전부라고 보기는 어려워요. 51에서 본 것처럼 누가 채점용이 되느냐에 따라 점수가 흔들려요." + REAL)

o = [sec("vs")] + head(EB4, "50의 선형 회귀, 52의 KNN과 나란히 보기", K4)
VH = ["", "50 선형 회귀", "52 KNN", "53 로지스틱 회귀"]
VR = [("맞히는 것", "점수 (숫자)", "사진 속 사람 (보기)", "합격, 불합격 (보기)"), ("종류", "회귀", "분류", "분류"),
      ("답을 내는 방법", "곱해 더한 합계", "가까운 이웃의 투표", "합계를 S자 곡선에 넣기"), ("predict", "점수", "보기 하나", "True 또는 False"),
      ("predict_proba", "없어요", "있어요", "있어요"), ("score", "R²", "맞힌 비율", "맞힌 비율")]
WD_ = [330, 440, 440, 440]
o += plain_rows(96, 210, 1728, VR, WD_, 1, 100, VH, 30)
o.append(box(len(VR) + 1, 96 + 330 + 440 * 2 + 60 - 10, 200, 440 + 20, 58 + len(VR) * 100 + 14, PS, 5, 14))
o.append(caption("모델은 달라도 fit, predict, score 쓰는 법은 같아요.", 950, len(VR) + 2))
W("vs", o, "지금까지 배운 모델과 나란히 놓아 봐요. 50의 선형 회귀는 점수 같은 숫자를 맞히는 회귀였고, 52의 KNN과 오늘의 로지스틱 회귀는 보기 중 하나를 고르는 분류예요. 선형 회귀와 로지스틱 회귀는 둘 다 열마다 가중치를 곱해 더해요. 로지스틱 회귀는 그 합계를 S자 곡선에 넣어 확률로 바꾸는 점이 달라요. KNN은 가중치 없이 가까운 이웃이 어느 쪽이 많은지로 답해요. 분류 모델은 predict_proba로 확률을 꺼낼 수 있고, score는 맞힌 비율이에요. 선형 회귀의 score는 R제곱이에요. 세 모델 모두 fit, predict, score를 같은 방법으로 써요.")

# ---------- part 5 ----------
o = [sec("e-cont")] + head(EB5, "점수를 그대로 y에 넣으면 오류 없이 점수 7개 중 하나를 골라요", K5)
CFS[0] = 24
ECC = ["from sklearn.linear_model import LogisticRegression", "", 'y_score = df["score"]', "X_train, X_test, s_train, s_test = train_test_split(X, y_score, test_size=0.3, random_state=42)",
       "X_train_scaled = scaler.fit_transform(X_train)", "", "wrong = LogisticRegression(max_iter=1000)", "wrong.fit(X_train_scaled, s_train)", 'print("클래스 :", wrong.classes_)']
o += cell({"id": "c-ec", "lines": ECC, "n": 19, "out": ["클래스 : [47 52 60 73 76 77 87]"]}, 96, 190, 1728, sel="c-ec")
o.append(tint(1, cx(96, "y_score = ") - 2, ly(190, 2) - LH() / 2, tw('df["score"]') + 4, LH(), RED))
o.append(tag(cx(96, ECC[2]) + 30, ly(190, 2), "점수 그대로 (>= 60이 없어요)", RED, 1, 26))
o.append(box(2, cx(96, "클래스 : ", True) - 8, oy(190, 9, 0) - LH() / 2 - 4, tw("[47 52 60 73 76 77 87]") + 16, LH() + 8, RED, 4))
o.append(tag(cx(96, "클래스 : [47 52 60 73 76 77 87]", True) + 30, oy(190, 9, 0), "학습용 7명의 점수가 보기 7개가 됐어요", RED, 2, 26))
E2Y = 190 + chight(9, 1) + 24
o += cell({"id": "c-ec2", "lines": ["new = pd.DataFrame([[4, 7, 5]], columns=X.columns)", "print(wrong.predict(scaler.transform(new)))"], "n": 20, "out": ["[52]"]}, 96, E2Y, 1100, attrs=rise(3))
o.append(note(1260, E2Y + 10, 560, "52점은 보기 7개 중 하나일 뿐이에요. 50점이나 65점은 절대 나오지 않아요.", INK, 28, fade(3)))
o.append(fix(96, 920, 'y_score = df["score"]', 'y = df["score"] >= 60', 4, 32))
W("e-cont", o, "y에 60 이상 비교를 빼고 점수를 그대로 넣으면 어떻게 될까요. 오류가 나지 않아요. 대신 LogisticRegression은 점수 하나하나를 보기로 여겨요. 학습용 7명의 점수 47, 52, 60, 73, 76, 77, 87이 보기 7개가 됐어요. 새 학생을 넣으면 52처럼 그중 하나를 골라요. 숫자를 맞히는 회귀가 아니라 7개 중 하나를 고르는 분류라서, 학습용에 없던 50점이나 65점은 절대 나오지 않아요. 점수를 맞히고 싶으면 50의 LinearRegression을 쓰고, 합격을 맞히고 싶으면 y를 True와 False로 만들어요. 이 셀은 X_train과 scaler를 덮어써요. 따라 해 봤다면 셀 2부터 다시 실행해요. 비교하려고 stratify 없이 나눴어요." + EXTRA + REAL, ("p5", "오류와 함정"))

o = [sec("e-two")] + head(EB5, "[0]만 적으면 두 칸이 남아서 %로 못 찍어요", K5)
CFS[0] = 24
ETC = ["new = pd.DataFrame([[4, 7, 5]], columns=X.columns)", "new_scaled = scaler.transform(new)", "pass_proba = model.predict_proba(new_scaled)[0]", 'print(f"합격 확률: {pass_proba:.2%}")']
o += cell({"id": "c-et", "lines": ETC, "n": 21, "out": ["TypeError: unsupported format string passed to numpy.ndarray.__format__"], "err": True}, 96, 196, 1500, sel="c-et")
o.append(tint(1, cx(96, "pass_proba = model.predict_proba(new_scaled)") - 2, ly(196, 2) - LH() / 2, tw("[0]") + 4, LH(), RED))
o.append(reading(96, 196 + chight(4, 1) + 30, "읽는 법: 배열(numpy.ndarray)에는 :.2% 같은 모양을 붙일 수 없다는 뜻이에요.", INK, 2, 30))
TY2 = 600
o.append(label(96, TY2, "[0]", RED, 34, fade(3), True))
for k, (v, c_, bg) in enumerate([("0.5163", FA, FAB), ("0.4837", PC, PCB)]):
    o.append(vbox(260 + k * 250, TY2 - 10, 230, 80, v, c_, bg, 32, fade(3)))
o.append(label(800, TY2 + 4, "두 칸이 남아요. 어느 칸을 %로 찍을지 몰라요", RED, 28, fade(3)))
o.append(label(96, TY2 + 120, "[0, 1]", GR, 34, fade(4), True))
o.append(vbox(260 + 250, TY2 + 110, 230, 80, "0.4837", PC, PCB, 32, fade(4)))
o.append(label(800, TY2 + 124, "합격 확률 하나 → 48.37%", GR, 28, fade(4)))
o.append(fix(96, 900, "predict_proba(new_scaled)[0]", "predict_proba(new_scaled)[0, 1]", 5, 32))
W("e-two", o, "수업 셀의 대괄호 0, 1을 0만 적으면 TypeError가 나요. 대괄호 0은 0번 줄을 통째로 꺼내서 불합격과 합격 확률 두 칸이 든 배열이 남아요. f-string의 :.2%는 숫자 하나에만 붙일 수 있어요. 오류 메시지의 numpy.ndarray가 배열이라는 뜻이에요. 대괄호 0, 1로 0번 줄의 1번 칸, 합격 확률 하나를 꺼내면 48.37%로 찍혀요." + EXTRA + REAL)

o = [sec("e-raw")] + head(EB5, "transform을 빼먹으면 경고 한 줄과 함께 99.68%가 나와요", K5)
CFS[0] = 22
ERC = ["new = pd.DataFrame([[4, 7, 5]], columns=X.columns)", "print(model.predict(new))", "print(model.predict_proba(new).round(4))"]
WARN = "UserWarning: X has feature names, but LogisticRegression was fitted without feature names"
o += cell({"id": "c-er", "lines": ERC, "n": 22, "out": [WARN, "[ True]", WARN, "[[0.0032 0.9968]]"], "red": (0, 2)}, 96, 190, 1728, sel="c-er")
o.append(tint(1, cx(96, "print(model.predict(") - 2, ly(190, 1) - LH() / 2, tw("new") + 4, LH(), RED))
o.append(tag(cx(96, ERC[1]) + 30, ly(190, 1), "바꾸지 않은 표 그대로", RED, 1, 26))
o.append(reading(96, 190 + chight(3, 4) + 26, "경고: 열 이름이 있는 표를 넣었는데, 학습할 때는 열 이름 없는 배열이었다는 뜻이에요.", INK, 2, 28))
o.append(label(96, 630, "transform 했을 때", SUB, 28, fade(3)))
o.append(bigval(96, 700, "48.37%", PC, 120, fade(3)))
o.append(label(800, 630, "transform 안 했을 때", RED, 28, fade(3)))
o.append(bigval(800, 700, "99.68%", RED, 120, fade(3) + ' id="b99"'))
o.append(shake(4, "b99"))
o.append(note(1460, 660, 370, "연습 5번을 표준편차 5개로 읽어서 연습을 아주 많이 한 학생이 됐어요.", INK, 26, fade(4)))
o.append(fix(96, 900, "model.predict_proba(new)", "model.predict_proba(scaler.transform(new))", 5, 30))
W("e-raw", o, "새 학생 표를 transform하지 않고 바로 넣으면 경고가 나와요. 경고는 빨간 상자로 보이지만 오류와 달리 셀이 멈추지 않아요. 그래서 결과가 그대로 찍혀요. 모델은 표준화한 값으로 배웠으니 4, 7, 5를 표준편차 4개, 7개, 5개로 읽어요. 특히 연습 5번은 원래 평균보다 적은데, 평균보다 표준편차 5개나 많은 학생으로 읽혀요. 그래서 48.37%였던 확률이 99.68%로 뛰고 답도 True로 바뀌어요. 51의 SGD에서 본 것과 같은 실수예요. predict와 predict_proba 앞에는 늘 scaler.transform을 거쳐요. 실제 화면에는 경고 앞에 파일 경로가 길게 붙어요." + EXTRA + REAL)

o = [sec("e-small")] + head(EB5, "10명에서 test_size=0.1과 stratify를 같이 주면 ValueError가 나요", K5)
CFS[0] = 24
ESC = ["from sklearn.model_selection import train_test_split", "", "X_train, X_test, y_train, y_test = train_test_split(", "    X, y, test_size=0.1, random_state=42, stratify=y", ")"]
o += cell({"id": "c-es", "lines": ESC, "n": 23, "out": ["ValueError: The test_size = 1 should be greater or equal to the number of classes = 2"], "err": True}, 96, 196, 1500, sel="c-es")
o.append(tint(1, cx(96, "    X, y, ") - 2, ly(196, 3) - LH() / 2, tw("test_size=0.1") + 4, LH(), RED))
o.append(reading(96, 196 + chight(5, 1) + 30, "읽는 법: 채점용 1명(test_size = 1)은 보기 수 2보다 크거나 같아야 해요.", INK, 2, 30))
SY2 = 680
o.append(label(96, SY2 - 50, "10명 × 0.1 = 채점용 1명", INK, 28, fade(3)))
o.append(setbox(96, SY2, 130, 120, TE, fade(3)))
o.append(p(f"position:absolute;left:128px;top:{SY2 + 26}px;width:64px;height:64px;border-radius:50%;border:3px dashed {GRAY};font-size:30px;font-weight:700;line-height:58px;text-align:center;color:{GRAY}", "?", fade(3)))
o.append(label(260, SY2 + 40, "합격과 불합격을 한 명씩 담을 자리가 없어요", RED, 28, fade(3)))
o.append(fix(96, 900, "test_size=0.1", "test_size=0.3", 4, 32))
W("e-small", o, "학생이 10명뿐인데 test_size를 0.1로 주면 채점용은 1명이에요. stratify=y는 합격과 불합격 비율을 채점용에도 맞추려고, 보기마다 적어도 한 명씩은 담으려 해요. 그런데 자리가 1명뿐이라 보기 두 개를 다 담을 수 없어요. 오류 메시지의 test_size = 1은 채점용 인원, number of classes = 2는 보기 수예요. 데이터가 적을 때는 test_size를 넉넉히 주거나 stratify를 빼요. 수업처럼 0.3이면 3명이라 괜찮아요." + EXTRA + REAL)

o = [sec("e-sleep")] + head(EB5, "수면 가중치 -0.37을 '잠을 자면 떨어진다'로 읽으면 안 돼요", K5)
CFS[0] = 25
o += cell({"id": "c-sl1", "lines": ['print(df[["sleep_hours", "score"]].corr().round(2))'], "n": 24,
           "out": ["             sleep_hours  score", "sleep_hours         1.00   0.29", "score               0.29   1.00"]}, 96, 190, 1000, sel="c-sl1")
o.append(box(1, cx(96, "sleep_hours         1.00   ", True) - 8, oy(190, 1, 1) - LH() / 2 - 4, tw("0.29") + 16, LH() + 8, PS, 4))
o.append(tag(cx(96, "sleep_hours         1.00   0.29", True) + 24, oy(190, 1, 1), "10명 전체로는 플러스", PS, 1, 24))
SLC = ["for sleep in [5, 6, 7, 8]:", "    one = pd.DataFrame([[4, sleep, 20]], columns=X.columns)", "    p = model.predict_proba(scaler.transform(one))[0, 1]", '    print(f"수면 {sleep}시간: {p:.2%}")']
S2Y = 190 + chight(1, 3) + 30
o += cell({"id": "c-sl2", "lines": SLC, "n": 25, "out": ["수면 5시간: 89.54%", "수면 6시간: 86.03%", "수면 7시간: 81.59%", "수면 8시간: 76.12%"]}, 96, S2Y, 1000, attrs=rise(2))
RX = 1180
o.append(label(RX, 214, "학습용 7명의 수면 시간", SUB, 26, fade(3)))
for k, (t_, ks, ok) in enumerate([("불합격 3명", [9, 1, 0], False), ("합격 4명", [3, 6, 8, 2], True)]):
    y = 270 + k * 120
    o.append(label(RX, y + 14, t_, PS if ok else FA, 28, fade(3)))
    for j, i in enumerate(ks):
        o.append(disc(i, RX + 170 + j * 80, y, ok, 60, fade(3) + DELAY(j * 60)))
        o.append(p(f"position:absolute;left:{RX + 170 + j * 80}px;top:{y + 64}px;width:60px;text-align:center;font-family:{MONO};font-size:22px;color:{INK}", f"{ROWS[i][1]}h", fade(3) + DELAY(j * 60)))
o.append(note(RX, 530, 640, "이 7명 안에서는 불합격 학생이 잠을 더 잤어요(평균 7.3시간과 6.5시간). 모델은 이 7명만 보고 배웠어요.", INK, 28, fade(4)))
o.append(note(RX, 720, 640, "-0.37은 '이 7명에서, 공부와 연습이 같을 때' 수면이 길수록 확률이 조금 내려갔다는 뜻이에요. 잠이 점수를 떨어뜨린다는 증거는 아니에요.", INK, 28, fade(5)))
W("e-sleep", o, "수면 가중치가 마이너스라서 잠을 많이 자면 떨어진다고 읽기 쉬워요. 공부 4시간, 연습 20번으로 두고 수면만 바꾸면 실제로 89.54%에서 76.12%로 내려가요. 하지만 10명 전체의 수면과 점수 상관계수는 0.29로 오히려 플러스예요. 모델은 학습용 7명만 보고 배웠는데, 이 7명 안에서는 불합격 3명이 평균 7.3시간, 합격 4명이 평균 6.5시간을 잤어요. 학생이 적으면 이런 우연이 가중치에 그대로 들어가요. 가중치는 다른 열을 그대로 둘 때 그 열이 확률을 어느 쪽으로 미는지일 뿐, 원인을 말해 주지 않아요. 50에서 혼자 배운 기울기와 같이 배운 기울기가 달랐던 것과 같은 이야기예요." + EXTRA + REAL)

# ---------- part 6 ----------
o = [sec("x-table"), NEXT()] + head(EB6, "비어 있던 수업 셀 7: 학생 다섯 명의 합격 확률을 표로 만들어요", K6)
CFS[0] = 24
o += cell({"id": "c-xt", "lines": STUC, "n": 26}, 96, 190, 1520, sel="c-xt")
o.append(tint(1, cx(96, 'students["pass_proba"] = model.predict_proba(students_scaled)') - 2, ly(190, 7) - LH() / 2, tw("[:, 1]") + 4, LH(), PC))
o.append(tag(cx(96, STUC[7]) + 20, ly(190, 7), "모두의 합격 확률", PC, 1, 22))
o.append(tag(cx(96, STUC[9]) + 30, ly(190, 9), "확률이 높은 순서로", INK, 1, 22))
XT = [(5, 6, 25, "0.956", "True"), (1, 6, 30, "0.653", "True"), (2, 7, 20, "0.502", "True"), (4, 7, 5, "0.484", "False"), (3, 8, 15, "0.475", "False")]
TT = 190 + chight(10) + 30
cs = {}
for i, r in enumerate(XT):
    cs[(i, 4)] = f"color:{PS if r[4] == 'True' else FA};font-weight:700"
    cs[(i, 3)] = f"color:{PC};font-weight:700"
o.append(df("t-xt", 96, TT, CN3 + ["pass_proba", "passed"], XT, [190, 190, 230, 170, 130], 28, 56, idx=[2, 4, 1, 0, 3], iw=60, attrs=rise(2),
            row_attrs={i: rise(2) + DELAY(i * 80) for i in range(5)}, cs=cs))
o.append(box(3, 96 - 6, dfy(TT, 56, 2) - 2, 60 + 910 + 36, 56 + 4, OR, 4, 8))
o.append(tag(96 + 60 + 910 + 50, dfy(TT, 56, 2) + 28, "0.502: 반반에 가까워요", OR, 3, 26))
o.append(tag(96 + 60 + 910 + 50, dfy(TT, 56, 3) + 28, "0번은 오늘의 새 학생", GRAY, 3, 24))
W("x-table", o, "수업 노트북의 마지막 셀은 students = pd.DataFrame( 까지만 적혀 있고 비어 있었어요. 학생 여러 명의 합격 확률을 한 표로 보는 셀로 채웠어요. 세 열로 학생 다섯 명의 표를 만들고, 학습용 자로 transform해요. predict_proba 뒤에 :, 1을 붙여 모든 학생의 합격 확률을 꺼내고 pass_proba 열에 담아요. 45에서 배운 새 열 만들기예요. passed 열에는 predict의 True, False를 담아요. 마지막 줄의 sort_values로 확률이 높은 학생부터 세웠어요. 1번 학생은 0.502로 True지만 거의 반반이에요. 0번 학생은 오늘의 새 학생과 같은 값이에요." + REAL, ("p6", "실제 상황"))

o = [sec("x-practice"), NEXT()] + head(EB6, "연습을 몇 번 더 하면 합격일까요? 6번부터 0.5를 넘어요", K6)
CFS[0] = 22
XPC = ["for practice in range(5, 11):", "    one = pd.DataFrame([[4, 7, practice]], columns=X.columns)", "    p = model.predict_proba(scaler.transform(one))[0, 1]", '    print(f"연습 {practice:2}번: {p:.2%}", "합격" if p >= 0.5 else "불합격")']
XPO = ["연습  5번: 48.37% 불합격", "연습  6번: 50.96% 합격", "연습  7번: 53.54% 합격", "연습  8번: 56.11% 합격", "연습  9번: 58.64% 합격", "연습 10번: 61.13% 합격"]
o += cell({"id": "c-xp", "lines": XPC, "n": 27, "out": XPO}, 96, 190, 1190, sel="c-xp")
o.append(tag(cx(96, XPC[0]) + 30, ly(190, 0), "18의 range: 5부터 10까지", GRAY, None, 22))
VALS = [48.37, 50.96, 53.54, 56.11, 58.64, 61.13]
BX1, BB, BH0 = 1350, 1000, 0
o.append(label(BX1, 214, "합격 확률 (막대는 40%부터)", SUB, 24))
for k, v in enumerate(VALS):
    x = BX1 + k * 76
    h = (v - 40) * 24
    c_ = PS if v >= 50 else FA
    o.append(bar(x, 760 - h, 60, h, c_, WIPE(1) + DELAY(k * 90)))
    o.append(label(x - 6, 760 - h - 40, f"{v:.1f}", c_, 24, fade(1) + DELAY(k * 90)))
    o.append(label(x + 4, 776, f"{k + 5}번", GRAY, 22, fade(1)))
o.append(hline(BX1 - 20, BX1 + 6 * 76, 760 - 10 * 24, INK, 3, "8 6", fade(2)))
o.append(label(BX1 + 6 * 76 + 6, 760 - 10 * 24 - 18, "50%", INK, 24, fade(2)))
o.append(f'<div style="position:absolute;left:{BX1 - 20}px;top:760px;width:{6 * 76 + 20}px;height:3px;background:#9AA0AB"></div>')
o.append(caption("연습 한 번에 2.5%쯤 올라서, 한 번만 더 하면 0.5를 넘어요.", 930, 3))
W("x-practice", o, "새 학생은 48.37%로 아슬아슬하게 불합격이었어요. 공부와 수면은 그대로 두고 연습 횟수만 5번부터 10번까지 바꿔 봤어요. 18의 range로 숫자를 만들고, 17의 한 줄 if로 0.5 이상이면 합격이라고 찍었어요. 연습 6번부터 50.96%로 0.5를 넘어서 합격이에요. 한 번에 2.5%쯤씩 올라가요. 이렇게 한 열만 바꿔 보면 무엇을 얼마나 바꿔야 결과가 달라지는지 감을 잡을 수 있어요. 다만 모델은 학생 7명으로 배운 거라, 실제 시험 결과를 약속하지는 않아요. 막대는 40%부터 그렸어요." + EXTRA + REAL)

o = [sec("x-range"), NEXT()] + head(EB6, "배운 범위 밖의 값은 확률이 1에 가까워져도 믿기 어려워요", K6)
CFS[0] = 22
o += cell({"id": "c-xr1", "lines": ['X.describe().loc[["min", "max"]]'], "n": 28}, 96, 190, 800, sel="c-xr1")
o.append(df("t-xr", 96 + 87, 190 + chight(1) + 14, CN3, [("1.0", "5.0", "8.0"), ("5.0", "8.0", "32.0")], [190, 190, 230], 24, 46, idx=["min", "max"], iw=70))
o.append(box(1, 96 + 87 + 70 + 380 - 4, 190 + chight(1) + 14 + 46, 230 + 8, 92 + 4, OR, 4, 8))
XRC = ["for practice in [8, 32, 60, 100]:", "    one = pd.DataFrame([[4, 7, practice]], columns=X.columns)", "    p = model.predict_proba(scaler.transform(one))[0, 1]", '    print(f"연습 {practice:3}번: {p:.2%}")']
R2Y = 190 + chight(1) + 14 + 46 * 3 + 30
o += cell({"id": "c-xr2", "lines": XRC, "n": 29, "out": ["연습   8번: 56.11%", "연습  32번: 93.89%", "연습  60번: 99.64%", "연습 100번: 99.99%"]}, 96, R2Y, 1000, attrs=rise(2))
NX0, NW_ = 1180, 640
NY0 = 520
o.append(f'<div{fade(3)} style="position:absolute;left:{NX0 + 8 * NW_ / 100:.0f}px;top:{NY0 - 20}px;width:{24 * NW_ / 100:.0f}px;height:44px;background:{K3BG};border-radius:10px"></div>')
o.append(label(NX0 + 8 * NW_ / 100, NY0 - 120, "배운 범위 8~32번", TR, 24, fade(3)))
o.append(f'<div{fade(3)} style="position:absolute;left:{NX0}px;top:{NY0}px;width:{NW_}px;height:4px;background:#9AA0AB"></div>')
for v in [0, 50, 100]:
    o.append(p(f"position:absolute;left:{NX0 + v * NW_ / 100 - 40:.0f}px;top:{NY0 + 80}px;width:80px;text-align:center;font-family:{MONO};font-size:22px;color:{GRAY}", f"{v}번", fade(3)))
for k, (v, pv, inr) in enumerate([(8, "56.11%", True), (32, "93.89%", True), (60, "99.64%", False), (100, "99.99%", False)]):
    x = NX0 + v * NW_ / 100
    c_ = TR if inr else RED
    o.append(p(f"position:absolute;left:{x - 14:.0f}px;top:{NY0 - 12}px;width:28px;height:28px;border-radius:50%;background:{c_};border:3px solid #FFFFFF", "", rise(4) + DELAY(k * 100)))
    o.append(p(f"position:absolute;left:{x - 70:.0f}px;top:{NY0 + (-62 if k % 2 else 32)}px;width:140px;text-align:center;font-family:{MONO};font-size:22px;font-weight:700;color:{c_}", pv, rise(4) + DELAY(k * 100)))
o.append(note(NX0, 680, 640, "모델은 연습 32번보다 많은 학생을 한 번도 보지 못했어요. 곡선을 그대로 늘린 값일 뿐이에요.", INK, 28, fade(5)))
W("x-range", o, "연습을 더 늘리면 확률이 어디까지 갈까요. 먼저 describe로 학생 10명의 가장 작은 값과 가장 큰 값을 봤어요. 연습 횟수는 8번부터 32번까지예요. 이 범위 안인 8번과 32번은 56.11%, 93.89%예요. 범위 밖인 60번은 99.64%, 100번은 99.99%로 거의 확실하다고 나와요. 하지만 모델은 연습 32번보다 많이 한 학생을 본 적이 없어요. S자 곡선을 그대로 늘린 값이라, 숫자가 확실해 보여도 믿기 어려워요. 배운 범위 안의 학생에게 쓸 때 가장 믿을 만해요. describe의 loc은 46에서 배운 이름표로 꺼내기예요." + EXTRA + REAL)

# ---------- closing ----------
o = [sec("trouble")] + head("정리", "막히면 y의 모양, transform, 대괄호 순서부터 봐요", RED)
TBL = [("classes_에 점수가 줄줄이 나와요", "y에 점수를 그대로 넣었어요", 'y = df["score"] >= 60'),
       ("TypeError: unsupported format string passed to numpy.ndarray.__format__", "[0]만 적어서 두 칸이 남았어요", "predict_proba(...)[0, 1]"),
       ("UserWarning: X has feature names, but LogisticRegression was fitted ...", "새 학생 표를 바꾸지 않았어요", "scaler.transform(new)"),
       ("ValueError: The test_size = 1 should be greater or equal to ...", "채점용이 보기 수보다 적어요", "test_size=0.3"),
       ("0.502인데 True라서 어색해 보여요", "0.5를 조금이라도 넘으면 True예요", "predict_proba도 같이 보기")]
for i, (q, a_, cmd) in enumerate(TBL):
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:96px;top:{196 + i * 128}px;width:1728px;height:128px;display:flex;flex-direction:row;align-items:center;gap:26px;border-bottom:2px solid {LINE}">'
             + '<div style="flex:1;display:flex;flex-direction:column;gap:4px">' + p(f"{'font-family:' + MONO + ';' if q.isascii() else ''}font-size:24px;font-weight:700;color:{RED};white-space:nowrap", e(q)) + p(f"font-size:26px;color:{INK}", e(a_)) + '</div>'
             + p(f"width:520px;flex:none;font-family:{MONO};font-size:24px;font-weight:700;color:{GR};white-space:pre", '✓ ' + e(cmd)) + '</div>')
o.append(caption("경고와 오류는 마지막 줄부터 읽어요. 이상하면 classes_와 확률을 찍어 봐요.", 900))
W("trouble", o, "막히면 출력의 마지막 줄부터 읽어요. 첫째, classes_에 점수가 여러 개 나오면 y가 True, False가 아니에요. 둘째, TypeError는 대괄호 0만 적어서 두 칸이 남은 거예요. 셋째, feature names 경고는 새 학생 표를 transform하지 않은 거예요. 넷째, test_size ValueError는 채점용 인원이 보기 수보다 적은 거예요. 마지막으로 답이 이상해 보이면 predict_proba로 두 확률을 찍어 봐요.", ("trouble", "정리"))

o = [sec("recap")] + head("정리", "로지스틱 회귀로 합격 확률을 구하는 다섯 단계", K1)
STEPS = [("정답 만들기", 'y = df["score"] >= 60', "True와 False 두 보기", K2),
         ("나누고 크기 맞추기", "train_test_split(..., stratify=y)\nscaler.fit_transform(X_train)", "보기 비율을 맞춰서 (51)", TR),
         ("학습", "model = LogisticRegression(max_iter=1000)\nmodel.fit(X_train_scaled, y_train)", "가중치 셋과 절편", K3),
         ("확률과 답", "model.predict_proba(new_scaled)[0, 1]\nmodel.predict(new_scaled)[0]", "합계 → S자 곡선 → 0.5 기준", PC),
         ("채점", "model.score(X_test_scaled, y_test)", "맞힌 비율", TE)]
for i, (h_, code, d, c_) in enumerate(STEPS):
    y = 196 + i * 136
    o.append(f'<div{rise(1 + i)} style="position:absolute;left:96px;top:{y}px;width:1728px;height:122px;display:flex;flex-direction:row;align-items:center;gap:30px;border-bottom:2px solid {LINE}">'
             + num(i + 1, c_, 40) + p(f"width:300px;flex:none;font-size:34px;font-weight:700;color:{INK}", e(h_))
             + p(f"flex:1;font-family:{MONO};font-size:24px;font-weight:700;line-height:1.5;color:{INK};white-space:pre", e(code))
             + p(f"width:400px;flex:none;font-size:26px;color:{SUB}", e(d)) + '</div>')
o.append(caption("다음에 배울 것: 맞힌 비율 말고 '어떻게 틀렸는지' 나눠 보는 채점 방법", 950, 6))
W("recap", o, "오늘 배운 순서를 정리해요. 정답을 True와 False로 만들고, stratify로 보기 비율을 맞춰 나눈 뒤 51처럼 크기를 맞춰요. LogisticRegression으로 학습하면 가중치 셋과 절편이 생겨요. 새 학생은 가중치를 곱해 더한 합계가 S자 곡선을 지나 확률이 되고, 0.5를 기준으로 답이 정해져요. 채점은 맞힌 비율이에요. 합격을 불합격으로 틀린 것과 불합격을 합격으로 틀린 것을 나눠 보는 채점 방법은 다음에 이어서 배워요.", ("recap", "정리"))

o = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장으로 보는 오늘의 코드</h2>']
CHS = [("정답을 True, False로", 'y = df["score"] >= 60', PS),
       ("보기 비율을 맞춰 나누고 크기 맞추기", "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)\nX_train_scaled = scaler.fit_transform(X_train)", TR),
       ("학습", "from sklearn.linear_model import LogisticRegression\nmodel = LogisticRegression(max_iter=1000)\nmodel.fit(X_train_scaled, y_train)", K3),
       ("새 학생의 답과 확률", "new_scaled = scaler.transform(pd.DataFrame([[4, 7, 5]], columns=X.columns))\nmodel.predict(new_scaled)[0]                 # False\nmodel.predict_proba(new_scaled)[0, 1]        # 0.4837", PC),
       ("채점", "model.score(X_test_scaled, y_test)           # 맞힌 비율", TE)]
y = 180
for k, d, c in CHS:
    n_ = d.count("\n") + 1
    h = 50 + n_ * 36
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:{h}px;display:flex;flex-direction:column;justify-content:center;gap:4px;border-bottom:2px solid {LINE}">'
             + p(f"font-size:26px;font-weight:700;color:{c}", e(k)) + p(f"font-family:{MONO};font-size:24px;font-weight:700;line-height:1.5;color:{INK};white-space:pre", e(d)) + '</div>')
    y += h + 16
o.append(p(f"position:absolute;left:96px;top:{y + 20}px;width:1728px;font-size:30px;font-weight:700;line-height:1.5;color:{INK}", "predict_proba의 두 칸은 classes_ 순서예요. 1번 칸이 합격 확률이에요."))
W("cheatsheet", o, "오늘 쓴 코드를 한 장에 모았어요. 정답을 True와 False로 만들고, 비율을 맞춰 나누고, 크기를 맞추고, 학습하고, 확률과 답을 꺼내고, 채점해요. 새 학생도 늘 scaler.transform을 거쳐요.")

# ---------- order and toc ----------
want = ["cover", "toc", "setup", "start", "why", "kinds", "prob", "big",
        "target", "assign", "review51", "stratify", "stratify-cmp", "iloc", "scaled",
        "import", "model", "classes", "coef",
        "new", "zsum", "sigmoid", "sigwhy", "predict", "proba", "threshold", "score", "vs",
        "e-cont", "e-two", "e-raw", "e-small", "e-sleep", "x-table", "x-practice", "x-range", "trouble", "recap", "cheatsheet"]
assert sorted(want) == sorted(ORDER), (set(want) ^ set(ORDER))
ORDER[:] = want
SECTIONS.update({"p2": {"description": "정답 만들고 나누기", "start": "target"}, "p4": {"description": "확률 구하기", "start": "new"}})
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
parts_ = [("Lightbulb", K1, "왜 필요한가", "why", "big"), ("Activity", K2, "정답 만들고 나누기", "target", "scaled"), ("Tool", K3, "모델 학습하기", "import", "coef"),
          ("Settings", K4, "확률 구하기", "new", "vs"), ("Warning", K5, "오류와 함정", "e-cont", "e-sleep"), ("Star", K6, "실제 상황", "x-table", "x-range")]
t = [f'<section id="toc" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>']
for i, (ic, c, h, a, b) in enumerate(parts_):
    x, y = 96 + (i // 3) * 884, 230 + (i % 3) * 190
    t.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:844px;height:160px;display:flex;flex-direction:row;align-items:center;gap:28px;border-bottom:2px solid {LINE}">'
             f'<p style="width:70px;font-size:72px;font-weight:900;color:{c}">{i + 1}</p><x-icon name="{ic}" style="width:52px;height:52px;color:{c}"></x-icon>'
             f'<p style="flex:1;font-size:44px;font-weight:700;color:{INK}">{e(h)}</p><p style="font-size:28px;color:{GRAY}">{page[a]}–{page[b]}쪽</p></div>')
t.append(f'<p style="position:absolute;left:96px;top:880px;font-size:30px;color:{SUB}">{page["setup"]}–{page["start"]}쪽은 노트북 준비, {page["trouble"]}–{page["cheatsheet"]}쪽은 막힐 때와 정리, 한 장 요약이에요.</p>')
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(t) + "\n<aside>" + e("1파트에서 직선으로는 합격 확률을 못 구하는 이유와 분류, 확률의 뜻을 보고, 2파트에서 정답을 True와 False로 만들어 비율을 맞춰 나눠요. 3파트는 LogisticRegression으로 학습하고 가중치를 읽어요. 4파트는 새 학생의 합계가 S자 곡선을 지나 확률이 되는 과정을 따라가고 채점해요. 5파트는 자주 나는 오류, 6파트는 비어 있던 수업 셀을 채우는 실제 상황이에요.") + "</aside>\n</section>\n")
deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-27T09:00:00Z"}, "lists": "css", "title": "합격할 확률 구하기 (로지스틱 회귀)", "order": ORDER, "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
print(len(ORDER), "slides")
