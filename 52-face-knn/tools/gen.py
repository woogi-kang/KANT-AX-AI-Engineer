"""Generates every slide of the face photos and KNN deck (52) and slides/deck.json.

Story: class notebook 04_ml.ipynb (Olivetti faces and KNeighborsClassifier). Students found it hard, so the deck starts
from the ground: a photo is a table of numbers, what a distance is (a three-cell photo worked by hand), neighbours and a
majority vote, what K means. Part 1: chapters 48-51 guessed a number, today we guess who (classification), and the five
steps of KNN in one picture. Part 2: fetch_olivetti_faces and its bundle (images, data, target), one pixel is a number
from 0 (black) to 1 (white), imshow with cmap, vmin and vmax, one person's 10 photos, the 40 people in one grid.
Part 3: distance by hand on three cells, the same in NumPy, 64 x 64 laid flat into 4096 numbers, real distances
between faces (6.26 same person, 9.76 another), the majority vote of the 3 nearest. Part 4: KNeighborsClassifier
(name taken apart), photo 229 set aside, fit only memorises, kneighbors and predict (two brackets), K changes the
answer (K=7 ties and takes the smaller number), train_test_split with stratify, score 87.00% and the same by hand,
regression vs classification. Part 5: one bracket, the class code's wrong titles, K bigger than the photos, a test
size smaller than the people, the same person further away than another person. Part 6: which K for this data
(95% at K=1), the 13 wrong photos and the two people the model mixes up. Then trouble, recap, cheat sheet.
Class code fixes shown in the deck (and said in the notes): the neighbour titles used y[new_index] so every one read
"Person 22" (now y_known[j]), the "339장" comment is 399, the stale neighbour comments dropped, the third print label
says 사람 번호, grey and gray unified to gray, axex typo fixed and zip replaced by range(10) (zip is not taught), the
second reload of the data in cell 15 dropped, the separate neighbour figures put in one figure.
Every cell and output comes from tools/demo.sh (tools/run_nb.py runs the cells with the project kernel), kept in
tools/demo.log. Pictures are the kernel's own PNGs in tools/img (NanumGothic stands in for Malgun Gothic on Linux).

Layout rules (Stageshow skill, github.com/benjitaylor/skills, SKILL.md and every file in references/ read for this deck):
1. one focal object per slide: a notebook cell, a kernel picture, one code line taken apart, or one diagram (framing.md)
2. terms are labelled on the code token with leader lines and tints, not in cards (annotations.md)
3. say it once: the speaker notes carry the explanation, the slide keeps one caption at most (craft.md, Restraint)
4. no empty bands: the picture or the code grows to fill (craft.md, Restraint)
5. values move instead of swapping: votes fly into the tally, photo 229 flies out of the 400 (motion.md)
6. one number gets to be big (87.00%), the rest are lines (craft.md, Restraint)
7. a comparison changes one thing (teaching.md): vmin/vmax and nothing, stratify and none, y_known[j] and y[new_index]
8. one color per role on every slide: person 22 blue, person 17 brown, training teal, test magenta (craft.md)
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
    return sum(fs * (0.92 if '가' <= ch <= '힣' else 0.6) for ch in s)


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




from PIL import Image
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
    lx = x - 4 if anchor == "left" else (x - (w or 0) + 4 if anchor == "right" else x - (w or 0) / 2)
    lab = p(f"position:absolute;left:{lx:.0f}px;top:{y2:.0f}px;{ws}{'text-align:right;' if anchor == 'right' else ''}font-size:{size}px;font-weight:700;line-height:1.35;color:{color}", e(text), fade(order) + DELAY(150))
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




# ---------- this deck (52) ----------
NB = "face.ipynb"
EB1, EB2, EB3, EB4, EB5, EB6 = "1. 왜 필요한가", "2. 사진은 숫자 표", "3. 거리와 이웃", "4. KNN 학습하고 채점하기", "5. 오류와 함정", "6. 실제 상황"
TR, TRB = TEAL, K3BG          # training photos: teal
TE, TEB = K4, K4BG            # test photos: magenta
P22, P22B = K1, K1BG          # person 22: blue on every slide
P17, P17B = K2, K2BG          # person 17: brown on every slide
P3, P3B = PUR, K6BG           # person 3
PC = {22: (P22, P22B), 17: (P17, P17B), 3: (P3, P3B)}
NEW, NEWB = INK, "#FFFFFF"     # the new photo


def cropx(name, out, b):
    """Saves a pixel box of a kernel picture as its own file."""
    im = Image.open(os.path.join(IMG, name))
    im.crop(b).save(os.path.join(IMG, out))
    return out


for k_, x_ in enumerate([(20, 290), (343, 613), (667, 937), (990, 1260)]):
    cropx("one-1.png", ["f229.png", "f17.png", "f228.png", "f225.png"][k_], (x_[0], 64, x_[1], 333))
for k_, x_ in enumerate([(20, 294), (348, 622), (676, 950)]):
    cropx("dist-1.png", ["d0.png", "d1.png", "d10.png"][k_], (x_[0], 64, x_[1], 337))
cropx("pic-1.png", "f0.png", (20, 65, 482, 526))


def face(x, y, w, name, attrs="", tid=None, color=None):
    b = png_b64(name)
    idt = f' id="{tid}"' if tid else ""
    bd = f"border:4px solid {color};" if color else f"border:2px solid {LINE};"
    return f'<img{idt}{attrs} src="data:image/png;base64,{b}" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{w}px;{bd}border-radius:10px;background:#FFFFFF">'


def pdisc(n, x, y, size=64, attrs="", tid=None, fs=None):
    c, bg = PC.get(n, (GRAY, "#F1F0EC"))
    return stu(n, x, y, c, bg, size, attrs, tid, fs)


def vline(x, y1, y2, color, order, w=3):
    return f'<svg{fade(order)} style="position:absolute;left:0;top:0;width:1920px;height:1080px;overflow:visible;pointer-events:none" viewBox="0 0 1920 1080"><line x1="{x:.0f}" y1="{y1:.0f}" x2="{x:.0f}" y2="{y2:.0f}" stroke="{color}" stroke-width="{w}"/></svg>'


def gray_cell(x, y, s, v, attrs="", fs=None, tid=None):
    """One pixel drawn with its own gray, its value written on it."""
    g = int(v * 255)
    tc = "#FFFFFF" if v < 0.5 else INK
    idt = f' id="{tid}"' if tid else ""
    return p(f"position:absolute;left:{x}px;top:{y}px;width:{s}px;height:{s}px;background:rgb({g},{g},{g});border:2px solid #9AA0AB;font-family:{MONO};font-size:{fs or s * 0.3:.0f}px;font-weight:700;line-height:{s - 4}px;text-align:center;color:{tc}", f"{v:.1f}", idt + attrs)


def legend(x, y, items, gap=72, fs=28, tw_=None):
    """Tinted code chips with their meaning, one row each, under a cell (no leader lines crossing code)."""
    out = []
    cw = tw_ or max(tw(t, fs) for t, _, _, _ in items) + 40
    for k, (t, c, txt, od) in enumerate(items):
        cc = c.lstrip("#")
        r_, g_, b_ = int(cc[0:2], 16), int(cc[2:4], 16), int(cc[4:6], 16)
        out.append(f'<div{fade(od)} style="position:absolute;left:{x}px;top:{y + k * gap}px;display:flex;flex-direction:row;align-items:center;gap:24px">'
                   + p(f"width:{cw:.0f}px;flex:none;font-family:{MONO};font-size:{fs}px;line-height:1.4;white-space:pre;color:{INK}", f'<span style="background:rgba({r_},{g_},{b_},0.18);border-bottom:4px solid {c};border-radius:6px;padding:0 4px">{e(t)}</span>')
                   + p(f"font-size:{fs}px;font-weight:700;line-height:1.4;color:{c};white-space:nowrap", e(txt)) + '</div>')
    return out


def errline(x, y, text, order, size=26, w=1728):
    return p(f"position:absolute;left:{x}px;top:{y}px;width:{w}px;font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.45;color:{RED};white-space:pre-wrap;word-break:break-all", e(text), rise(order))


# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#F2B27A;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
       f'<h1{SLAM(1)} style="font-size:88px;font-weight:900;line-height:1.14;color:#F6F5F1">사진으로<br>사람 맞히기</h1>',
       '<p style="font-size:38px;line-height:1.45;color:#BFC6D4">얼굴 사진을 숫자로 읽고,<br>가장 가까운 사진 K장에게 물어봐요</p>']
cov.append(f'<div id="cov-card" style="position:absolute;left:1000px;top:250px;width:800px;height:460px;background:#FFFFFF;border-radius:24px;overflow:hidden">'
           + f'<img id="cov-img" src="data:image/png;base64,{png_b64("pic-5.png")}" style="position:absolute;left:20px;top:20px;width:760px">'
           + '</div>')
cov.append(p(f"position:absolute;left:1000px;top:740px;width:800px;font-size:26px;line-height:1.5;color:#BFC6D4", "40명이 10장씩 찍은 얼굴 사진 400장으로 연습해요."))
cov.append(kenburns(2, "cov-img", 1.08, 6000, "40% 40%"))
W("cover", cov, "48부터 51까지는 점수나 집값처럼 숫자를 맞혔어요. 오늘은 사진 한 장을 보고 이 사람이 누구인지 맞혀요. 컴퓨터는 사진을 어떻게 읽는지, 두 사진이 얼마나 닮았는지를 어떻게 재는지부터 천천히 봐요. 그다음 가장 가까운 사진 몇 장에게 물어보는 KNN으로 사람을 맞히고 채점해요. 수업 노트북 04를 정리했어요." + IMGN, ("intro", "들어가기"))
ORDER.append("toc")

# ---------- setup ----------
o = [sec("setup")] + head("들어가기", "ml-basics에 새 노트북 face.ipynb를 열어요", JP)
TL = [("$", "cd ml-basics"), ("$", "cat pyproject.toml"), ("o", "dependencies = ["), ("o", '    "matplotlib>=3.11.2",'), ("o", '    "numpy>=2.5.5",'), ("o", '    "pandas>=3.1.1",'),
      ("o", '    "scikit-learn>=1.9.1",'), ("o", '    "seaborn>=0.13.2",'), ("o", "]")]
o.append(term(96, 214, 900, TL, 28, tid="t-setup"))
LHt = 28 * 1.55
o.append(box(1, 96 + 34 - 10, 214 + 26 + 6 * LHt - 4, 28 * 0.6 * 26 + 24, LHt + 8, "#F2C46D", 4, 10))
o.append(tag(96 + 34 + 28 * 0.6 * 26 + 40, 214 + 26 + 6.5 * LHt, "48에서 넣었어요", OR, 1, 26))
o.append(note(96, 214 + 52 + len(TL) * LHt + 30, 900, "새로 설치할 건 없어요. 버전 숫자는 받는 날에 따라 달라요.", SUB, 26, fade(1)))
TX = 1080
tree = [("ml-basics/", INK, 0, True), (".venv/", GRAY, 1, True), ("datasets/", GRAY, 1, True), ("olivetti_py3.pkz", JP, 2, False), ("split.ipynb", GRAY, 1, False), (NB, JP, 1, False), ("pyproject.toml", GRAY, 1, False)]
o.append(label(TX, 214, "폴더 모양", INK, 30))
for i, (n_, c_, d, folder) in enumerate(tree):
    y = 290 + i * 76
    at = rise(2) + DELAY(i * 60) if i else ""
    o.append(p(f"position:absolute;left:{TX + d * 56}px;top:{y}px;font-family:{MONO};font-size:32px;font-weight:700;line-height:64px;color:{c_};white-space:nowrap", ("▸ " if folder else "") + e(n_), at))
o.append(tag(TX + 112 + 32 * 0.6 * 16 + 30, 290 + 3 * 76 + 32, "처음 실행할 때 받아요", JP, 3, 26))
o.append(tag(TX + 56 + 32 * 0.6 * 11 + 40, 290 + 4 * 76 + 32, "51 노트북", GRAY, 2, 26))
o.append(tag(TX + 56 + 32 * 0.6 * 10 + 40, 290 + 5 * 76 + 32, "오늘 노트북", JP, 2, 26))
o.append(caption("사진 데이터는 처음 한 번만 인터넷에서 받아요. 그 뒤로는 datasets 폴더에서 읽어요.", 930, 4))
W("setup", o, "45부터 쓰는 ml-basics 프로젝트를 그대로 써요. 오늘 쓰는 KNN과 얼굴 사진 데이터는 48에서 넣은 scikit-learn 안에 들어 있어요. 그래서 새로 설치할 건 없어요. VS Code에서 face.ipynb를 새로 만들고 커널은 .venv로 골라요. 얼굴 사진 파일은 처음 실행할 때 인터넷에서 받아서 datasets 폴더에 olivetti_py3.pkz로 저장돼요. 그래서 처음 한 번은 인터넷이 연결되어 있어야 해요." + REAL)

# ---------- start ----------
o = [sec("start")] + head("들어가기", "맨 위 셀에서 불러오고, 사진 400장을 받아요", JP)
CFS[0] = 30
IMPORTS = ["import numpy as np", "import matplotlib.pyplot as plt", "from sklearn.datasets import fetch_olivetti_faces"]
o += cell({"id": "c-imp", "lines": IMPORTS, "n": 1}, 96, 196, 1220, sel="c-imp")
o.append(tag(cx(96, IMPORTS[0]) + 30, ly(196, 0), "45", GRAY, 1, 26))
o.append(tag(cx(96, IMPORTS[1]) + 30, ly(196, 1), "47", GRAY, 1, 26))
o.append(tint(1, cx(96, "from ") - 2, ly(196, 2) - LH() / 2, tw("sklearn.datasets") + 4, LH(), K1))
o.append(tint(1, cx(96, "from sklearn.datasets import ") - 2, ly(196, 2) - LH() / 2, tw("fetch_olivetti_faces") + 4, LH(), OR))
o.append(tag(1360, ly(196, 2) - 20, "datasets 서랍: 연습용 데이터를 받아 오는 함수가 모여 있어요", K1, 1, 26, lead=False, w=480))
FT = 196 + chight(3) + 24
o.append(p(f"position:absolute;left:{96 + 87}px;top:{FT}px;font-family:{MONO};font-size:22px;color:{GRAY}", "[2]  글꼴 셀: 51과 같아요 (46의 셀 + axes.unicode_minus)"))
LT = FT + 60
LOAD = ['faces = fetch_olivetti_faces(data_home="./datasets")']
CFS[0] = 26
o += cell({"id": "c-load", "lines": LOAD, "n": 3, "out": ["downloading Olivetti faces from https://ndownloader.figshare.com/files/5976027 to ./datasets"]}, 96, LT, 1728, attrs=rise(2))
o.append(tag(cx(96, LOAD[0]) + 30, ly(LT, 0), "처음 실행: 인터넷에서 받아요", JP, 2, 26))
o.append(tint(3, cx(96, "faces = fetch_olivetti_faces(") - 2, ly(LT, 0) - LH() / 2, tw('data_home="./datasets"') + 4, LH(), OR))
o += legend(96 + 87, LT + chight(1, 1) + 26, [('data_home="./datasets"', OR, "받은 파일을 둘 폴더. 안 적으면 집 폴더 안 scikit_learn_data", 3)], fs=26)
L2 = LT + chight(1, 1) + 120
o += cell({"id": "c-load2", "lines": LOAD, "n": 4}, 96, L2, 1728, attrs=rise(4))
o.append(tag(cx(96, LOAD[0]) + 30, ly(L2, 0), "다시 실행: 출력 없이 폴더에서 바로 읽어요", GR, 4, 26))
o.append(caption("받는 건 처음 한 번뿐이에요. 인터넷이 없으면 첫 실행에서 오류가 나요.", 950, 5))
W("start", o, "새 노트북 맨 위 셀이에요. numpy는 45, matplotlib은 47에서 쓴 라이브러리예요. 셋째 줄은 scikit-learn의 datasets 서랍에서 fetch_olivetti_faces 함수를 불러와요. fetch는 가져온다는 뜻이고, Olivetti는 이 사진을 찍은 연구소 이름이에요. 둘째 셀은 51과 같은 글꼴 셀이라 줄여 적었어요. 셋째 셀에서 함수를 부르면 사진 파일을 인터넷에서 받아요. data_home은 받은 파일을 둘 폴더예요. 47에서 만든 datasets 폴더를 적었어요. 같은 셀을 다시 실행하면 폴더에 있는 파일을 읽어서 받는다는 줄이 안 나와요." + REAL)

# ---------- part 1 ----------
o = [sec("why")] + head(EB1, "지금까지는 숫자를 맞혔고, 오늘은 누구인지 맞혀요", K1)
o.append(label(96, 220, "48~51: 숫자 맞히기 (회귀)", K1, 34))
o.append(stu(7, 120, 320, K3, K3BG, 110))
o.append(note(96, 450, 300, "공부 4시간\n수면 7시간\n문제 30개".replace("\n", "<br>"), SUB, 26))
o.append(arrow(80, "#9AA0AB", "", "position:absolute;left:300px;top:360px"))
o.append(bigval(410, 330, "77.73점", K1, 96))
NL = 600
o.append(f'<div style="position:absolute;left:120px;top:{NL}px;width:680px;height:4px;background:#9AA0AB"></div>')
for v_ in [0, 25, 50, 75, 100]:
    x_ = 120 + v_ * 6.8
    o.append(f'<div style="position:absolute;left:{x_ - 1:.0f}px;top:{NL - 10}px;width:3px;height:24px;background:#9AA0AB"></div>')
    o.append(label(x_ - 20, NL + 22, str(v_), GRAY, 22))
o.append(f'<div style="position:absolute;left:{120 + 77.73 * 6.8 - 12:.0f}px;top:{NL - 12}px;width:24px;height:24px;border-radius:50%;background:{K1}"></div>')
o.append(note(96, 700, 820, "정답이 숫자 줄 위 어디든 될 수 있어요. 77.73점처럼 소수도 돼요.", INK, 30))
o.append(f'<div style="position:absolute;left:940px;top:220px;width:3px;height:680px;background:{LINE}"></div>')
R0 = 1010
o.append(label(R0, 220, "52: 누구인지 맞히기 (분류)", K4, 34, rise(1)))
o.append(face(R0, 300, 230, "f229.png", rise(1)))
o.append(arrow(80, "#9AA0AB", rise(1), f"position:absolute;left:{R0 + 260}px;top:400px"))
o.append(bigval(R0 + 370, 370, "22번", K4, 96, rise(1) + ' id="ans22"'))
for k in range(40):
    x_, y_ = R0 + (k % 10) * 80, 570 + (k // 10) * 60
    hi = k == 22
    o.append(p(f"position:absolute;left:{x_}px;top:{y_}px;width:66px;height:48px;border-radius:10px;border:3px solid {K4 if hi else LINE};background:{K4BG if hi else CARD};font-family:{MONO};font-size:24px;font-weight:700;line-height:42px;text-align:center;color:{INK}", str(k), rise(2) + DELAY(k * 15)))
o.append(note(R0, 820, 800, "정답이 정해진 40개 번호 중 하나예요. 22.5번 사람은 없어요.", INK, 30, fade(2)))
o.append(caption("정답이 정해진 몇 가지 중 하나일 때, 고르는 일을 분류라고 해요.", 950, 3))
W("why", o, "48부터 51까지 모델이 맞힌 정답은 점수나 집값 같은 숫자였어요. 51의 새 학생은 77.73점이 나왔죠. 정답이 숫자 줄 위 어디에나 있을 수 있는 문제를 회귀라고 해요. 오늘은 얼굴 사진을 보고 이 사람이 몇 번 사람인지 맞혀요. 이 데이터에는 0번부터 39번까지 40명이 있어서, 정답은 이 40개 중 하나예요. 22.5번 사람은 없어요. 이렇게 정해진 몇 가지 중 하나를 고르는 문제를 분류라고 해요. 메일이 스팸인지 아닌지, 사진이 고양이인지 개인지도 분류예요.", ("p1", "왜 필요한가"))

o = [sec("big")] + head(EB1, "KNN은 가장 닮은 사진 몇 장에게 물어봐요", K1)
BX = [96, 446, 796, 1146, 1496]
STEP = ["새 사진", "숫자 4096개", "399장과 거리 재기", "가장 가까운 3장", "다수결"]
for k, (x_, s_) in enumerate(zip(BX, STEP)):
    o.append(num(k + 1, K1, 30) .replace('<p style="', f'<p{rise(k) if k else ""} style="position:absolute;left:{x_}px;top:230px;', 1))
    o.append(label(x_ + 60, 236, s_, INK, 28, rise(k) if k else ""))
    if k:
        o.append(arrow(56, "#9AA0AB", WIPE(k), f"position:absolute;left:{x_ - 66}px;top:500px"))
o.append(face(96, 330, 270, "f229.png", tid="b-new"))
VAL = ["0.17", "0.13", "0.11", "...", "0.33", "0.30", "0.24"]
for k, v_ in enumerate(VAL):
    o.append(p(f"position:absolute;left:446px;top:{320 + k * 56}px;width:270px;height:48px;border-radius:8px;border:2px solid #C9CED8;background:{CARD};font-family:{MONO};font-size:26px;font-weight:700;line-height:44px;text-align:center;color:{INK}", v_, rise(1) + DELAY(k * 40)))
DL = [("6.07", 17), ("6.26", 22), ("6.44", 22), ("6.63", 22), ("...", None), ("9.76", 0)]
for k, (d_, n_) in enumerate(DL):
    o.append(p(f"position:absolute;left:796px;top:{320 + k * 64}px;width:270px;font-family:{MONO};font-size:28px;font-weight:700;line-height:56px;color:{INK};border-bottom:2px solid {LINE};white-space:pre", e(f"{d_:>5}" + (f"   {n_}번" if n_ is not None else "")), rise(2) + DELAY(k * 50)))
for k, (nm, n_) in enumerate([("f17.png", 17), ("f228.png", 22), ("f225.png", 22)]):
    o.append(face(1146, 320 + k * 165, 140, nm, rise(3) + DELAY(k * 80), color=PC[n_][0]))
    o.append(label(1300, 320 + k * 165 + 50, f"{n_}번", PC[n_][0], 32, rise(3) + DELAY(k * 80)))
o.append(label(1496, 330, "22번 2장, 17번 1장", INK, 30, rise(4)))
o.append(bigval(1496, 420, "22번", P22, 120, rise(4) + ' id="b-ans"'))
o.append(ring(5, 1496, 420, 260, 120, P22, 6))
o.append(caption("K Nearest Neighbors: 가장 가까운(Nearest) 이웃(Neighbors) K개. 이 다섯 단계를 2~4파트에서 하나씩 해요.", 930, 6))
W("big", o, "오늘 배울 KNN이 하는 일을 한 장으로 봐요. 첫째, 누구인지 모르는 새 사진이 있어요. 둘째, 컴퓨터는 이 사진을 0과 1 사이 숫자 4096개로 읽어요. 셋째, 이미 정답을 아는 사진 399장과 하나씩 거리를 재요. 거리가 작을수록 닮은 사진이에요. 넷째, 가장 가까운 사진 3장을 골라요. 다섯째, 그 3장이 몇 번 사람인지 세서 가장 많은 쪽으로 답해요. 22번이 2장, 17번이 1장이라 22번이에요. KNN은 K Nearest Neighbors, 가장 가까운 이웃 K개라는 뜻이에요. 여기서는 K가 3이에요. 숫자는 모두 4파트에서 실제로 실행한 값이에요." + REAL)

# ---------- part 2 ----------
o = [sec("bundle")] + head(EB2, "faces 꾸러미에는 사진 400장과 정답 400개가 있어요", K2)
CFS[0] = 26
SH = ['print("사진 묶음 크기:", faces.images.shape)', 'print("정답 묶음 크기:", faces.target.shape)', 'print("사람 번호:", np.unique(faces.target))']
SHO = ["사진 묶음 크기: (400, 64, 64)", "정답 묶음 크기: (400,)", "사람 번호: [ 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23", " 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39]"]
o += cell({"id": "c-sh", "lines": SH, "n": 4, "out": SHO}, 96, 196, 1728, sel="c-sh")
o.append(tint(1, cx(96, "사진 묶음 크기: (", True) - 2, oy(196, 3, 0) - LH() / 2, tw("400") + 4, LH(), K2))
o.append(tint(2, cx(96, "사진 묶음 크기: (400, ", True) - 2, oy(196, 3, 0) - LH() / 2, tw("64, 64") + 4, LH(), K1))
o.append(tint(3, cx(96, "정답 묶음 크기: (", True) - 2, oy(196, 3, 1) - LH() / 2, tw("400") + 4, LH(), GR))
TY = 196 + chight(3, 4) + 50
TILES = [("faces.images", "사진 400장", "한 장은 세로 64칸, 가로 64칸 표", K1, K1BG, 2), ("faces.target", "정답 400개", "사진마다 몇 번 사람인지 (0~39)", GR, GRBG, 3), ("faces.data", "같은 사진을 한 줄로 편 것", "3파트에서 써요", GRAY, "#F1F0EC", 4)]
for k, (nm, a_, b_, c_, bg, od) in enumerate(TILES):
    x_ = 96 + k * 590
    o.append(f'<div{rise(od)} style="position:absolute;left:{x_}px;top:{TY}px;width:560px;height:270px;border-top:6px solid {c_};background:{bg};border-radius:4px 4px 14px 14px;padding:22px 28px;display:flex;flex-direction:column;gap:10px">'
             + p(f"font-family:{MONO};font-size:36px;font-weight:700;color:{c_}", e(nm)) + p(f"font-size:36px;font-weight:700;color:{INK}", e(a_)) + p(f"font-size:28px;line-height:1.4;color:{SUB}", e(b_)) + '</div>')
o.append(caption("40명이 10장씩 찍어서 400장이에요. 사람 번호가 바로 맞힐 정답이에요.", 950, 5))
W("bundle", o, "fetch_olivetti_faces가 돌려준 faces는 여러 값을 담은 꾸러미예요. 점 뒤에 이름을 붙여 하나씩 꺼내요. faces.images는 사진 묶음이에요. shape이 400, 64, 64라서 사진이 400장이고, 한 장은 세로 64칸, 가로 64칸 표예요. faces.target은 정답 묶음이에요. 사진마다 그 사진이 몇 번 사람인지 적혀 있어요. np.unique는 겹치는 값을 하나만 남겨 줘요. 16의 set처럼요. 0번부터 39번까지 40명이에요. 400장을 40명으로 나누면 한 사람에 10장씩이에요. faces.data는 같은 사진을 한 줄로 편 것인데 3파트에서 써요." + REAL)

o = [sec("pixel")] + head(EB2, "사진 한 칸은 0(검정)부터 1(흰색) 사이 숫자예요", K2)
o.append(img(96, 196, 690, "pic-3.png", tid="i-corner"))
PX, PY, PW_ = 900, 200, 300
o.append(face(PX, PY, PW_, "f0.png", tid="i-f0"))
sc = PW_ / 462
o.append(box(1, PX + 20 * 7.22 * sc - 3, PY + 20 * 7.2 * sc - 3, 8 * 7.22 * sc + 6, 8 * 7.2 * sc + 6, RED, 4, 4))
o.append(link(1, PX + 20 * 7.22 * sc - 4, PY + 24 * 7.2 * sc, 786, 400, RED, 3))
o.append(note(PX + PW_ + 40, PY + 10, 580, "0번 사진에서 빨간 네모 8칸 × 8칸을 크게 그리고 칸마다 값을 적었어요.", SUB, 26, fade(1)))
GBY = PY + 150
o.append(f'<div{fade(2)} style="position:absolute;left:{PX + PW_ + 40}px;top:{GBY}px;width:520px;height:44px;border-radius:8px;border:2px solid #9AA0AB;background:linear-gradient(90deg,#000000,#FFFFFF)"></div>')
o.append(label(PX + PW_ + 40, GBY + 54, "0  검정", INK, 26, fade(2), mono=True))
o.append(label(PX + PW_ + 40 + 520 - 120, GBY + 54, "흰색  1", INK, 26, fade(2), mono=True))
CFS[0] = 22
RW = ['print("첫 사진 맨 윗줄 앞 5칸:", faces.images[0][0][:5].round(2))', 'print("가장 어두운 값:", faces.images.min())', 'print("가장 밝은 값:", faces.images.max())']
RT = 560
o += cell({"id": "c-row", "lines": RW, "n": 5, "out": ["첫 사진 맨 윗줄 앞 5칸: [0.31 0.37 0.42 0.44 0.53]", "가장 어두운 값: 0.0", "가장 밝은 값: 1.0"]}, PX - 100, RT, 1024, sel="c-row", attrs=rise(3))
o.append(tint(4, cx(PX - 100, 'print("첫 사진 맨 윗줄 앞 5칸:", faces.images') - 2, ly(RT, 0) - LH() / 2, tw("[0][0][:5]") + 4, LH(), OR))
o.append(lead_down(4, cx(PX - 100, 'print("첫 사진 맨 윗줄 앞 5칸:", faces.images') + tw("[0][0][:5]") / 2, ly(RT, 0) + LH() / 2, oy(RT, 3, 2) + 40, OR, "0번 사진, 0번 줄, 앞 5칸 (14의 2차원 리스트)", 24, w=600, anchor="right"))
o.append(caption("컴퓨터에게 사진은 64 × 64칸짜리 숫자 표예요.", 950, 5))
W("pixel", o, "사진을 아주 크게 키우면 작은 네모 칸이 보여요. 이 칸 하나를 픽셀이라고 해요. 이 데이터에서는 픽셀 하나가 0부터 1 사이 숫자 하나예요. 0은 검정, 1은 흰색이고, 그 사이는 회색이에요. 왼쪽 그림은 0번 사진의 이마와 눈 근처 8칸 × 8칸을 크게 그리고 칸마다 값을 적은 거예요. 0.6, 0.7 같은 밝은 회색이 많죠. 아래 셀에서 faces.images[0][0][:5]는 0번 사진의 0번 줄에서 앞 5칸이에요. 14에서 배운 scores[1][2]처럼 번호를 두 번 써서 꺼내요. 전체에서 가장 어두운 값은 0.0, 가장 밝은 값은 1.0이에요. 값을 적어 넣는 그림 셀은 이해를 도우려고 더했어요." + REAL + IMGN)

o = [sec("imshow")] + head(EB2, "imshow는 숫자 표를 받아서 칸마다 색을 칠해요", K2)
CFS[0] = 28
ON = ["plt.figure(figsize=(3, 3))", 'plt.imshow(faces.images[0], cmap="gray", vmin=0, vmax=1)', 'plt.title(f"Person {faces.target[0]}")', 'plt.axis("off")', "plt.show()"]
o += cell({"id": "c-one", "lines": ON, "n": 6}, 96, 196, 1150, sel="c-one")
o.append(tint(1, cx(96, "plt.imshow(") - 2, ly(196, 1) - LH() / 2, tw("faces.images[0]") + 4, LH(), K2))
o.append(tint(2, cx(96, 'plt.imshow(faces.images[0], cmap=') - 2, ly(196, 1) - LH() / 2, tw('"gray"') + 4, LH(), K1))
o.append(tint(3, cx(96, 'plt.imshow(faces.images[0], cmap="gray", ') - 2, ly(196, 1) - LH() / 2, tw("vmin=0") + 4, LH(), GR))
o.append(tint(3, cx(96, 'plt.imshow(faces.images[0], cmap="gray", vmin=0, ') - 2, ly(196, 1) - LH() / 2, tw("vmax=1") + 4, LH(), GR))
LB = 196 + chight(5) + 50
o += legend(96 + 87, LB, [("faces.images[0]", K2, "칠할 숫자 표 (64 × 64)", 1), ('cmap="gray"', K1, "색 이름: 회색으로 칠해요", 2), ("vmin=0, vmax=1", GR, "0을 검정, 1을 흰색으로 정해요", 3)], gap=90, fs=30)
o.append(tag(cx(96, ON[2]) + 30, ly(196, 2), "그림 위 제목 (13의 f-string)", SUB, 4, 24))
o.append(tag(cx(96, ON[3]) + 30, ly(196, 3), "눈금 숨기기", SUB, 4, 24))
o.append(img(1330, 196, 494, "pic-1.png", rise(5)))
o.append(caption("cmap을 안 적으면 보라와 노랑으로 칠해요. 사진은 늘 cmap=\"gray\", vmin=0, vmax=1로 그려요.", 950, 6))
W("imshow", o, "사진을 화면에 그리는 셀이에요. figsize는 47처럼 그림판 크기예요. imshow는 image show의 줄임말이에요. 첫 칸에 숫자 표를 넣으면 칸마다 색을 칠해요. cmap은 color map, 숫자를 어떤 색으로 바꿀지 정하는 이름이에요. gray를 적으면 회색으로 칠해요. vmin과 vmax는 가장 어두운 색과 가장 밝은 색에 맞출 숫자예요. 0을 검정, 1을 흰색으로 정했어요. title은 그림 위 제목이에요. faces.target[0]이 0이라서 Person 0이 나와요. axis off는 가장자리 눈금을 숨겨요. 수업 코드는 grey와 gray를 섞어 썼는데, 둘 다 되지만 gray로 맞췄어요." + IMGN)

o = [sec("cmap")] + head(EB2, "같은 숫자 표라도 cmap에 따라 색이 달라져요", K2)
o.append(img(96, 200, 1180, "pic-2.png", tid="i-cmp"))
o.append(spot(1, 96 + 1180 * 0.52, 200, 1180 * 0.48, 1180 * 507 / 970, pad=10))
o.append(spot_off(2))
CFS[0] = 22
NV = ["axes[0].imshow(faces.images[0], cmap=\"gray\", vmin=0, vmax=1)", "axes[1].imshow(faces.images[0])"]
o.append(mono(1320, 220, ["axes[0]  왼쪽 칸", "axes[1]  오른쪽 칸"], 26, 1.6, SUB))
o.append(note(1320, 340, 504, "오른쪽은 cmap을 안 적어서 matplotlib 기본 색(viridis)으로 칠했어요. 어두운 곳은 보라, 밝은 곳은 노랑이에요.", INK, 30, fade(1)))
o.append(note(1320, 580, 504, "vmin, vmax를 안 적으면 그 사진의 가장 작은 값과 큰 값에 맞춰요. 사진마다 기준이 달라져요.", INK, 30, fade(2)))
o.append(caption("숫자는 그대로예요. 색을 칠하는 규칙만 바뀌었어요.", 950, 3))
W("cmap", o, "같은 0번 사진을 두 칸에 그렸어요. 50의 plt.subplots(1, 2)처럼 그림판을 두 칸으로 나눴어요. 왼쪽은 cmap gray와 vmin, vmax를 적었고, 오른쪽은 아무것도 안 적었어요. 오른쪽은 matplotlib의 기본 색표인 viridis로 칠해서 보라와 노랑이 나와요. 숫자 표는 똑같고 색을 칠하는 규칙만 달라요. vmin과 vmax를 안 적으면 사진마다 그 사진의 가장 작은 값을 가장 어둡게, 가장 큰 값을 가장 밝게 칠해요. 사진끼리 밝기를 비교하려면 0과 1로 기준을 고정하는 게 좋아요." + IMGN)

o = [sec("person")] + head(EB2, "한 사람의 사진 10장만 골라서 그려요", K2)
CFS[0] = 28
PS = ["def show_person(person):", "    pics = faces.images[faces.target == person]", "    fig, axes = plt.subplots(1, 10, figsize=(15, 2))", "    for i in range(10):",
      '        axes[i].imshow(pics[i], cmap="gray", vmin=0, vmax=1)', '        axes[i].axis("off")', "    plt.show()", "", "show_person(39)"]
o += cell({"id": "c-ps", "lines": PS, "n": 7}, 96, 196, 1728, sel="c-ps")
o.append(tint(1, cx(96, "    pics = faces.images[") - 2, ly(196, 1) - LH() / 2, tw("faces.target == person") + 4, LH(), K1))
o.append(tag(cx(96, PS[1]) + 30, ly(196, 1), "그 사람 사진만 (45의 arr[조건])", K1, 1, 26))
o.append(tag(cx(96, PS[3]) + 30, ly(196, 3), "칸 10개를 차례로 (18의 range)", SUB, 2, 26))
o.append(hl(96, 196, 1728, 8, 1, "run", 3))
o.append(img(96, 196 + chight(9) + 40, 1728, "pic-4.png", rise(3)))
o.append(caption("39번 사람 10장이에요. 고개 방향과 표정이 조금씩 달라요.", 950, 4))
W("person", o, "한 사람의 사진만 골라 그리는 함수를 만들어요. faces.target == person은 45에서 배운 배열 비교예요. 400개 칸마다 True나 False가 나와요. 그걸 대괄호에 넣으면 True인 사진만 남아요. 한 사람에 10장씩이라 pics에는 사진 10장이 담겨요. 그다음 그림판을 가로 10칸으로 나누고, range(10)으로 칸 번호 0부터 9까지 돌면서 사진을 한 장씩 그려요. show_person(39)를 부르면 39번 사람 10장이 나와요. 수업 코드는 zip으로 두 묶음을 같이 돌았는데, zip은 아직 안 배워서 range로 바꿨어요. axex라는 오타도 고쳤어요." + IMGN)

o = [sec("grid")] + head(EB2, "40명의 첫 사진을 4줄 × 10칸에 그려요", K2)
CFS[0] = 24
GD = ["fig, axes = plt.subplots(4, 10, figsize=(15, 8))", "", "for person, ax in enumerate(axes.flat):", "    first = faces.images[faces.target == person][0]",
      '    ax.imshow(first, cmap="gray", vmin=0, vmax=1)', "    ax.set_title(person, fontsize=10)", '    ax.axis("off")', "", "plt.show()"]
o += cell({"id": "c-gd", "lines": GD, "n": 8}, 96, 196, 880, sel="c-gd")
o.append(tint(1, cx(96, "for person, ax in enumerate(") - 2, ly(196, 2) - LH() / 2, tw("axes.flat") + 4, LH(), K1))
o.append(tint(2, cx(96, "for person, ax in ") - 2, ly(196, 2) - LH() / 2, tw("enumerate") + 4, LH(), OR))
o += legend(96 + 87, 196 + chight(9) + 40, [("axes.flat", K1, "4줄 × 10칸을 한 줄로 펴서 칸 40개", 1), ("enumerate", OR, "칸 번호도 같이: 0번 칸에 0번 사람 (18)", 2)], gap=80, fs=28)
o.append(img(1010, 196, 814, "pic-5.png", rise(3)))
o.append(caption("사람마다 얼굴, 안경, 머리 모양이 달라요. 이 차이를 숫자로 재는 게 3파트예요.", 950, 4))
W("grid", o, "40명을 한눈에 보는 셀이에요. subplots(4, 10)은 4줄 10칸, 모두 40칸이에요. axes는 4줄 10칸짜리 2차원 묶음이라 for에 그대로 넣기 어려워요. axes.flat은 이걸 한 줄로 펴서 칸 40개를 차례로 꺼내 줘요. 18의 enumerate로 번호도 같이 받아서, 0번 칸에는 0번 사람, 1번 칸에는 1번 사람을 그려요. faces.target == person으로 그 사람 사진만 고르고 [0]으로 첫 장을 꺼내요. set_title에 사람 번호를 적었어요." + IMGN)

# ---------- part 3 ----------
o = [sec("tiny")] + head(EB3, "칸 3개짜리 사진으로 거리를 손으로 재 봐요", K3)
TV = {"new": [0.2, 0.8, 0.5], "a": [0.3, 0.6, 0.5], "b": [0.9, 0.1, 0.4]}
for k, (nm, vs) in enumerate(TV.items()):
    y_ = 220 + k * 150
    o.append(label(96, y_ + 34, nm, INK if nm == "new" else (P22 if nm == "a" else P17), 36, mono=True))
    for j, v_ in enumerate(vs):
        o.append(gray_cell(220 + j * 120, y_, 110, v_, fs=30))
o.append(note(96, 700, 560, "new와 a, new와 b 중 어느 쪽이 더 닮았을까요?", INK, 30))
TX0 = 720
o.append(label(TX0, 214, "new와 a", P22, 30, fade(1)))
o.append(label(TX0 + 560, 214, "new와 b", P17, 30, fade(5)))
RWS = [("1. 칸끼리 빼기", "-0.1   0.2   0.0", "-0.7   0.7   0.1"), ("2. 제곱하기", "0.01  0.04  0.00", "0.49  0.49  0.01"), ("3. 모두 더하기", "0.05", "0.99"), ("4. 루트 씌우기", "0.22", "0.99")]
for k, (h_, a_, b_) in enumerate(RWS):
    y_ = 280 + k * 120
    o.append(p(f"position:absolute;left:{TX0}px;top:{y_}px;width:1100px;height:110px;border-bottom:2px solid {LINE}", "", ""))
    o.append(label(TX0, y_ + 4, h_, SUB, 24, fade(k + 1)))
    o.append(label(TX0, y_ + 44, a_, INK, 34, fade(k + 1) + (' id="ta"' if k == 3 else ""), mono=True))
    o.append(label(TX0 + 560, y_ + 44, b_, INK, 34, fade(5) + (' id="tb"' if k == 3 else ""), mono=True))
o.append(box(6, TX0 - 12, 280 + 3 * 120 + 42, 104, 52, P22, 4))
o.append(note(TX0, 790, 1100, "빼기만 하면 -0.1과 0.2가 서로 지워져요. 제곱하면 모두 0 이상이 돼요.", SUB, 26, fade(2)))
o.append(caption("거리가 작을수록 닮은 사진이에요. new는 a와 더 닮았어요.", 950, 6))
W("tiny", o, "64 × 64는 너무 크니까 칸이 3개뿐인 사진으로 연습해요. new, a, b 세 사진이 있고 칸마다 0과 1 사이 숫자가 있어요. 두 사진이 얼마나 다른지는 네 단계로 재요. 첫째, 같은 자리 칸끼리 빼요. 둘째, 뺀 값을 제곱해요. 빼기만 하고 더하면 마이너스와 플러스가 서로 지워지니까, 제곱해서 모두 0 이상으로 만들어요. 셋째, 모두 더해요. 넷째, 루트를 씌워요. 루트는 제곱하기 전 크기로 되돌려 줘요. new와 a는 0.22, new와 b는 0.99예요. 거리가 작은 a가 new와 더 닮았어요. 이 거리를 유클리드 거리라고 해요. 48의 MSE처럼 빼고 제곱하고 더하는 계산이에요." + REAL)

o = [sec("tinycode")] + head(EB3, "NumPy 배열이면 네 단계가 한 줄씩이에요", K3)
CFS[0] = 28
TC = ["new = np.array([0.2, 0.8, 0.5])", "a = np.array([0.3, 0.6, 0.5])", "b = np.array([0.9, 0.1, 0.4])", "", 'print("new - a:", (new - a).round(2))', 'print("제곱:", ((new - a) ** 2).round(2))',
      'print("더하기:", ((new - a) ** 2).sum().round(2))', 'print("거리 a:", np.sqrt(((new - a) ** 2).sum()).round(2))', 'print("거리 b:", np.sqrt(((new - b) ** 2).sum()).round(2))']
TCO = ["new - a: [-0.1  0.2  0. ]", "제곱: [0.01 0.04 0.  ]", "더하기: 0.05", "거리 a: 0.22", "거리 b: 0.99"]
o += cell({"id": "c-tc", "lines": TC, "n": 9, "out": TCO}, 96, 196, 1320, sel="c-tc")
for k, (tok_, lab_) in enumerate([("(new - a)", "칸끼리 빼기 (45의 배열 계산)"), ("** 2", "제곱"), (".sum()", "모두 더하기"), ("np.sqrt", "루트")]):
    line_ = TC[4 + k]
    st = line_.find(tok_)
    o.append(tint(k + 1, cx(96, line_[:st]) - 2, ly(196, 4 + k) - LH() / 2, tw(tok_) + 4, LH(), [K1, OR, GR, PUR][k]))
    o.append(tag(1440, ly(196, 4 + k), lab_, [K1, OR, GR, PUR][k], k + 1, 26))
o.append(caption("손으로 잰 0.22, 0.99와 같아요. 사진이 커져도 이 한 줄이 그대로예요.", 950, 5))
W("tinycode", o, "같은 계산을 NumPy로 해요. 45에서 배운 것처럼 배열끼리 빼면 같은 자리 칸끼리 빼요. ** 2는 칸마다 제곱이에요. sum은 모두 더하고, np.sqrt는 루트를 씌워요. round(2)는 소수 둘째 자리까지 보여 줘요. 0.과 0.처럼 점만 찍힌 칸은 0.0이라는 뜻이에요. 결과는 손으로 잰 값과 같아요. 칸이 3개든 4096개든 이 한 줄은 그대로라서, 다음 장에서 진짜 사진 거리도 이렇게 재요." + REAL)

o = [sec("flat")] + head(EB3, "64 × 64 표를 한 줄로 펴면 숫자 4096개예요", K3)
RC = [K1, OR, GR, PUR]
for r in range(4):
    for c in range(4):
        o.append(p(f"position:absolute;left:{120 + c * 52}px;top:{220 + r * 52}px;width:46px;height:46px;border-radius:6px;background:{RC[r]};opacity:0.75", ""))
o.append(label(120, 434, "64줄 × 64칸", SUB, 24))
o.append(arrow(70, "#9AA0AB", WIPE(1), "position:absolute;left:360px;top:300px"))
for r in range(4):
    for c in range(4):
        o.append(p(f"position:absolute;left:{470 + (r * 4 + c) * 62}px;top:290px;width:56px;height:46px;border-radius:6px;background:{RC[r]};opacity:0.75", "", rise(1) + DELAY(r * 120)))
o.append(label(1480, 296, "… 4096칸", SUB, 26, fade(1)))
o.append(label(470, 360, "줄 0 뒤에 줄 1, 그 뒤에 줄 2 … 차례로 이어 붙여요", SUB, 26, fade(1)))
CFS[0] = 26
FL = ["X = faces.data", "y = faces.target", "", 'print("X:", X.shape)', 'print("y:", y.shape)', 'print("같은 사진인가요?", np.array_equal(X[0].reshape(64, 64), faces.images[0]))']
FLY0 = 490
o += cell({"id": "c-fl", "lines": FL, "n": 10, "out": ["X: (400, 4096)", "y: (400,)", "같은 사진인가요? True"]}, 96, FLY0, 1728, sel="c-fl", attrs=rise(2))
o.append(tag(cx(96, FL[0]) + 30, ly(FLY0, 0), "사진 400장, 한 장이 4096칸 (64 × 64)", K1, 3, 26))
o.append(tag(cx(96, FL[1]) + 30, ly(FLY0, 1), "정답 400개", GR, 3, 26))
o.append(tint(4, cx(96, 'print("같은 사진인가요?", np.array_equal(X[0]') - 2, ly(FLY0, 5) - LH() / 2, tw(".reshape(64, 64)") + 4, LH(), OR))
o.append(tag(cx(96, "같은 사진인가요? True", True) + 30, oy(FLY0, 6, 2), "reshape(64, 64)로 다시 접으면 원래 사진과 같아요", OR, 4, 26))
o.append(caption("모델에는 사진 한 장을 숫자 한 줄로 넣어요. 51의 학생 한 명이 한 줄이었던 것처럼요.", 950, 5))
W("flat", o, "모델에 넣으려면 사진 한 장이 한 줄이어야 해요. 51의 표에서 학생 한 명이 한 줄이었던 것과 같아요. 그래서 64 × 64 표의 줄을 차례로 이어 붙여 숫자 4096개짜리 한 줄로 펴요. faces.data에는 이렇게 편 사진이 이미 들어 있어요. 그래서 X는 400줄, 4096칸이에요. 51처럼 문제는 대문자 X, 정답은 소문자 y로 담아요. reshape(64, 64)는 한 줄을 다시 64줄로 접어요. np.array_equal은 두 배열이 칸마다 모두 같은지 물어서, True가 나왔으니 faces.data는 faces.images를 편 것과 같아요." + REAL)

o = [sec("realdist")] + head(EB3, "같은 사람 사진이 다른 사람 사진보다 가까워요", K3)
CFS[0] = 22
RD = ['print("229번 사람:", y[229], " 228번 사람:", y[228], " 0번 사람:", y[0])', 'print("229번과 228번 거리:", np.sqrt(((X[229] - X[228]) ** 2).sum()).round(2))', 'print("229번과 0번 거리:", np.sqrt(((X[229] - X[0]) ** 2).sum()).round(2))']
o += cell({"id": "c-rd", "lines": RD, "n": 11, "out": ["229번 사람: 22  228번 사람: 22  0번 사람: 0", "229번과 228번 거리: 6.26", "229번과 0번 거리: 9.76"]}, 96, 196, 1240, sel="c-rd")
FY = 560
o.append(face(810, FY, 300, "f229.png", tid="r229", color=NEW))
o.append(label(870, FY + 316, "229번 (22번 사람)", INK, 26))
o.append(face(250, FY, 300, "f228.png", rise(1), color=P22))
o.append(label(300, FY + 316, "228번 (22번 사람)", P22, 26, rise(1)))
o.append(face(1370, FY, 300, "f0.png", rise(2), color=GRAY))
o.append(label(1440, FY + 316, "0번 (0번 사람)", GRAY, 26, rise(2)))
o.append(f'<div{WIPE(1)} style="position:absolute;left:560px;top:{FY + 150}px;width:240px;height:5px;background:{P22}"></div>')
o.append(label(610, FY + 90, "6.26", P22, 44, rise(1), mono=True))
o.append(f'<div{WIPE(2)} style="position:absolute;left:1120px;top:{FY + 150}px;width:240px;height:5px;background:{GRAY}"></div>')
o.append(label(1170, FY + 90, "9.76", GRAY, 44, rise(2), mono=True))
o.append(caption("숫자 4096개로 잰 거리도 닮을수록 작아요.", 960, 3))
W("realdist", o, "이제 진짜 사진으로 재요. 229번 사진은 22번 사람이에요. 바로 앞 228번 사진도 22번 사람이고, 0번 사진은 0번 사람이에요. 앞 장의 한 줄 계산에 X[229]와 X[228]을 넣으면 6.26, X[229]와 X[0]을 넣으면 9.76이 나와요. 같은 사람끼리 거리가 더 작아요. 사진이 숫자 4096개여도 거리를 재는 방법은 칸 3개일 때와 똑같아요. 이 229번 사진을 4파트에서 누구인지 모르는 새 사진으로 써요." + REAL)

o = [sec("vote")] + head(EB3, "가장 가까운 K장이 투표해서 정해요", K3)
CX0, CY0 = 560, 570
NB7 = [(6.07, 17, 200), (6.26, 22, 320), (6.44, 22, 95), (6.63, 22, 35), (6.68, 17, 240), (6.93, 17, 160), (7.02, 3, -12)]
import math
def rr(d):
    return (d - 5.6) * 255
o.append(f'<svg{fade(2)} style="position:absolute;left:0;top:0;width:1920px;height:1080px;overflow:visible" viewBox="0 0 1920 1080"><circle cx="{CX0}" cy="{CY0}" r="{rr(6.50):.0f}" fill="{P22B}" fill-opacity="0.45" stroke="{P22}" stroke-width="4" stroke-dasharray="12 8"/></svg>')
o.append(face(CX0 - 60, CY0 - 60, 120, "f229.png", color=NEW))
for k, (d_, n_, ang) in enumerate(NB7):
    x_ = CX0 + rr(d_) * math.cos(math.radians(ang)) - 32
    y_ = CY0 - rr(d_) * math.sin(math.radians(ang)) - 32
    o.append(pdisc(n_, x_, y_, 64, rise(1) + DELAY(k * 60)))
o.append(label(CX0 + 130, CY0 + rr(6.5) + 10, "K = 3: 안에 든 3장", P22, 28, fade(2)))
VX = 1160
o.append(label(VX, 230, "가까운 순서", SUB, 26))
for k, (d_, n_, _) in enumerate(NB7[:3]):
    o.append(pdisc(n_, VX, 280 + k * 90, 64, rise(1)))
    o.append(label(VX + 90, 290 + k * 90, f"거리 {d_:.2f}", INK, 30, rise(1), mono=True))
o.append(label(VX, 580, "투표", SUB, 26, fade(3)))
o.append(p(f"position:absolute;left:{VX}px;top:630px;font-size:40px;font-weight:700;color:{P22}", "22번  2표", fade(3)))
o.append(p(f"position:absolute;left:{VX}px;top:700px;font-size:40px;font-weight:700;color:{P17}", "17번  1표", fade(3)))
o.append(p(f"position:absolute;left:{VX + 320}px;top:640px;font-size:72px;font-weight:900;color:{P22}", "→ 22번", fade(4) + ' id="v-ans"'))
o.append(note(1160, 800, 680, "새 사진 둘레에 이웃 7장을 놓은 상상도예요. 가운데에서 떨어진 정도만 실제 거리 순서를 따라요.", SUB, 24))
o.append(caption("가장 가까운 1장(17번)만 보면 틀려요. 3장에게 물으면 22번으로 맞아요.", 950, 5))
W("vote", o, "사진 399장과 거리를 다 재면 가까운 순서로 줄을 세울 수 있어요. 왼쪽 그림은 새 사진을 가운데 두고 가까운 이웃 7장을 놓은 상상도예요. 4096칸짜리 거리를 종이에 그릴 수는 없어서, 가운데에서 떨어진 정도만 실제 거리 순서대로 놓았어요. 차이가 잘 보이게 늘려 그렸고, 방향은 뜻이 없어요. 가장 가까운 사진은 17번 사람이에요. 1장만 보면 17번이라고 틀리게 답해요. K를 3으로 정하면 가까운 3장이 투표해요. 22번이 2표, 17번이 1표라서 22번이 이겨요. 이렇게 가까운 K장의 다수결로 정하는 방법이 KNN이에요. 거리와 사람 번호는 4파트의 실제 실행 결과예요." + REAL)

# ---------- part 4 ----------
o = [sec("knnname")] + head(EB4, "KNeighborsClassifier는 이름이 하는 일을 말해요", K4)
CFS[0] = 30
o += cell({"id": "c-ki", "lines": ["from sklearn.neighbors import KNeighborsClassifier"], "n": 12}, 96, 196, 1300, sel="c-ki")
o.append(tint(1, cx(96, "from ") - 2, ly(196, 0) - LH() / 2, tw("sklearn.neighbors") + 4, LH(), K1))
o.append(tag(1430, ly(196, 0), "neighbors 서랍: 이웃 모델", K1, 1, 26))
PARTS = [("K", "K장", "몇 장에게 물을지", K2), ("Neighbors", "이웃", "가까운 사진", P22), ("Classifier", "분류기", "정해진 번호 중 하나를 골라요", K4)]
x_ = 200
for k, (en, ko, d_, c_) in enumerate(PARTS):
    w_ = tw(en, 110)
    o.append(p(f"position:absolute;left:{x_}px;top:340px;font-family:{MONO};font-size:110px;font-weight:700;line-height:1.2;color:{c_};white-space:nowrap", e(en), rise(2 + k)))
    o.append(f'<div{fade(2 + k)} style="position:absolute;left:{x_}px;top:488px;width:{w_:.0f}px;height:6px;border-radius:3px;background:{c_}"></div>')
    cxk = x_ + w_ / 2
    o.append(p(f"position:absolute;left:{cxk - 200:.0f}px;top:520px;width:400px;text-align:center;font-size:44px;font-weight:700;color:{c_}", e(ko), fade(2 + k) + DELAY(120)))
    o.append(p(f"position:absolute;left:{cxk - 200:.0f}px;top:590px;width:400px;text-align:center;font-size:28px;line-height:1.4;color:{SUB};word-break:keep-all", e(d_), fade(2 + k) + DELAY(200)))
    x_ += w_ + 110
o.append(note(96, 780, 1728, "48의 LinearRegression은 Regression(회귀)으로 끝나서 숫자를 맞혀요. 이름 끝을 보면 회귀 모델인지 분류 모델인지 알 수 있어요.", INK, 30, fade(5)))
o.append(caption("이웃 K장에게 물어서 고르는 분류기, 줄여서 KNN이에요.", 950, 6))
W("knnname", o, "KNN 모델을 불러와요. scikit-learn의 neighbors 서랍에 있어요. 이름을 쪼개 읽으면 하는 일이 보여요. K는 몇 장에게 물을지 정하는 숫자, Neighbors는 이웃, Classifier는 분류기예요. 대문자로 시작하니 28에서 배운 클래스이고, 48의 LinearRegression처럼 괄호를 붙여 모델을 만들어요. LinearRegression은 끝이 Regression이라 숫자를 맞히는 회귀 모델이고, 이 모델은 끝이 Classifier라 번호를 고르는 분류 모델이에요.")

o = [sec("known")] + head(EB4, "229번 사진을 빼 두고, 나머지 399장만 보여 줘요", K4)
CFS[0] = 26
KN = ["new_index = 229", "new_photo = X[new_index]", "", "known = np.arange(400) != new_index", "print(known[227:232])", "", "X_known, y_known = X[known], y[known]", 'print("X_known:", X_known.shape)']
o += cell({"id": "c-kn", "lines": KN, "n": 13, "out": ["[ True  True False  True  True]", "X_known: (399, 4096)"]}, 96, 196, 1150, sel="c-kn")
o.append(tag(cx(96, KN[1]) + 30, ly(196, 1), "누구인지 모르는 척할 사진", INK, 1, 26))
o.append(tint(2, cx(96, "known = ") - 2, ly(196, 3) - LH() / 2, tw("np.arange(400)") + 4, LH(), K1))
o.append(tag(cx(96, KN[3]) + 30, ly(196, 3), "0~399 중 229만 False", K1, 2, 26))
o.append(tag(cx(96, KN[6]) + 30, ly(196, 6), "True인 399장만", GR, 3, 26))
BY = 760
for k in range(10):
    n_ = 225 + k
    o.append(p(f"position:absolute;left:{96 + k * 140}px;top:{BY}px;width:124px;height:80px;border-radius:12px;border:3px solid {INK if n_ == 229 else LINE};background:{CARD};font-family:{MONO};font-size:30px;font-weight:700;line-height:74px;text-align:center;color:{INK}", str(n_), f' id="kb{n_}"'))
o.append(p(f"position:absolute;left:1560px;top:{BY - 130}px;width:160px;height:96px;border-radius:12px;border:4px solid {INK};background:#FFFFFF;font-family:{MONO};font-size:36px;font-weight:700;line-height:88px;text-align:center;color:{INK}", "229", fly(4, "kb229")))
o.append(label(1540, BY - 180, "new_photo", INK, 28, fade(4), mono=True))
o.append(f'<div{fade(4)} style="position:absolute;left:{96 + 4 * 140}px;top:{BY}px;width:124px;height:80px;border-radius:12px;border:3px dashed #C9CED8;background:#F6F5F1"></div>')
o.append(label(96, BY + 100, "… 모두 400장, 229번 자리만 비워요", SUB, 26, fade(4)))
o.append(caption("시험 문제를 미리 보여 주면 안 되니까, 새 사진은 학습에서 빼요.", 960, 5))
W("known", o, "모델이 처음 보는 사진으로 맞히는지 보려고, 229번 사진 한 장을 따로 빼 둬요. new_photo가 누구인지 모르는 척할 사진이에요. np.arange(400)은 0부터 399까지 번호 배열이에요. 18의 range와 같은 일을 배열로 해요. != new_index로 비교하면 229번만 False, 나머지는 True예요. 출력은 227번부터 231번까지 다섯 칸만 보여 준 거예요. 이 True/False 배열을 X와 y에 넣으면 229번만 빠진 399장이 남아요. 51의 채점용을 떼어 두는 것과 같은 생각이에요. 수업 코드 주석에는 339장이라고 적혀 있었는데, 399장이 맞아요." + REAL)

o = [sec("fit")] + head(EB4, "KNN의 fit은 계산 없이 399장을 외워 두기만 해요", K4)
CFS[0] = 30
MD = ["K = 3", "", "model = KNeighborsClassifier(n_neighbors=K)", "model.fit(X_known, y_known)"]
o += cell({"id": "c-md", "lines": MD, "n": 14, "out": ["KNeighborsClassifier(n_neighbors=3)"]}, 96, 196, 1200, sel="c-md")
o.append(tint(1, cx(96, "model = KNeighborsClassifier(") - 2, ly(196, 2) - LH() / 2, tw("n_neighbors=K") + 4, LH(), K2))
o += legend(96 + 87, 196 + chight(4, 1) + 30, [("n_neighbors=K", K2, "물어볼 이웃 수 K. 안 적으면 5예요", 1)], fs=28)
o.append(tag(cx(96, MD[3]) + 30, ly(196, 3), "문제 먼저, 정답 나중 (48)", SUB, 2, 26))
CY_ = 660
o.append(label(96, CY_, "48 LinearRegression의 fit", SUB, 28, fade(3)))
o.append(p(f"position:absolute;left:96px;top:{CY_ + 50}px;font-family:{MONO};font-size:36px;font-weight:700;color:{INK}", "w = 10, b = 35 계산", fade(3)))
o.append(note(96, CY_ + 120, 800, "다 배우면 데이터 없이 직선만 있으면 돼요.", SUB, 26, fade(3)))
o.append(label(1000, CY_, "52 KNeighborsClassifier의 fit", K4, 28, fade(4)))
for k in range(6):
    o.append(p(f"position:absolute;left:{1000 + k * 92}px;top:{CY_ + 50}px;width:80px;height:80px;border-radius:8px;border:2px solid #C9CED8;background:#E9EAEE", "", rise(4) + DELAY(k * 60)))
o.append(label(1000 + 6 * 92, CY_ + 66, "… 399장", INK, 30, rise(4)))
o.append(note(1000, CY_ + 150, 820, "물어볼 때마다 399장과 거리를 다시 재요.", SUB, 26, fade(4)))
o.append(caption("그래서 KNN은 fit이 빠르고, 맞힐 때(predict) 시간이 걸려요.", 950, 5))
W("fit", o, "모델을 만들 때 n_neighbors에 K를 넣어요. 몇 장에게 물을지 정하는 값이에요. 안 적으면 기본값 5예요. 출력은 25에서 본 __repr__이에요. fit에는 48처럼 문제 X_known을 먼저, 정답 y_known을 나중에 넣어요. 48의 LinearRegression은 fit에서 기울기와 절편을 계산했어요. 다 배우고 나면 데이터 없이 직선만으로 예측해요. KNN의 fit은 계산하지 않고 399장을 그대로 외워 둬요. 새 사진이 오면 그때 399장과 거리를 재요. 그래서 fit은 빠르고 predict가 오래 걸려요." + REAL)

o = [sec("neigh")] + head(EB4, "kneighbors로 가장 가까운 이웃 3장을 직접 봐요", K4)
CFS[0] = 26
NG = ["dist, idx = model.kneighbors([new_photo], n_neighbors=K)", 'print("idx:", idx)', 'print("가장 가까운 이웃:", y_known[idx[0]])', 'print("이웃과의 거리:", dist[0].round(2))']
NGO = ["idx: [[179 228 225]]", "가장 가까운 이웃: [17 22 22]", "이웃과의 거리: [6.07 6.26 6.44]"]
o += cell({"id": "c-ng", "lines": NG, "n": 15, "out": NGO}, 96, 196, 1500, sel="c-ng")
o.append(tint(1, cx(96, "dist, idx = model.kneighbors(") - 2, ly(196, 0) - LH() / 2, tw("[new_photo]") + 4, LH(), OR))
o += legend(96 + 87, 196 + chight(4, 3) + 30, [("[new_photo]", OR, "대괄호 한 겹 더: 사진 여러 장 자리에 1장", 1)], fs=28)
o.append(tint(2, cx(96, "") - 2, ly(196, 0) - LH() / 2, tw("dist, idx") + 4, LH(), K1))
o.append(tag(cx(96, NG[0]) + 30, ly(196, 0), "거리와 번호를 한 번에 (19)", K1, 2, 24))
o.append(tint(3, cx(96, "idx: [[", True) - 2, oy(196, 4, 0) - LH() / 2, tw("179 228 225") + 4, LH(), GRAY))
o.append(tag(cx(96, NGO[0], True) + 30, oy(196, 4, 0), "X_known에서 몇 번째 사진인지", GRAY, 3, 24))
o.append(tint(4, cx(96, "가장 가까운 이웃: [", True) - 2, oy(196, 4, 1) - LH() / 2, tw("17 22 22") + 4, LH(), P22))
o.append(tag(cx(96, NGO[1], True) + 30, oy(196, 4, 1), "y_known으로 바꾸면 사람 번호", P22, 4, 24))
FY2 = 610
for k, (nm, n_, d_) in enumerate([("f17.png", 17, "6.07"), ("f228.png", 22, "6.26"), ("f225.png", 22, "6.44")]):
    x_ = 1004 + k * 280
    o.append(face(x_, FY2, 250, nm, rise(5) + DELAY(k * 80), color=PC[n_][0]))
    o.append(label(x_, FY2 + 262, f"{n_}번 · {d_}", PC[n_][0], 28, rise(5) + DELAY(k * 80)))
o.append(caption("idx는 줄 번호, 사람 번호는 y_known[idx[0]]으로 꺼내요.", 950, 6))
W("neigh", o, "predict 전에 모델이 고른 이웃을 직접 봐요. kneighbors는 가장 가까운 사진들의 거리와 번호를 돌려줘요. 19의 return a, b처럼 dist와 idx로 나눠 받아요. 모델은 사진 여러 장을 한꺼번에 받게 만들어져 있어서, 한 장이라도 대괄호로 한 겹 더 감싸 넣어요. 48에서 predict에 표를 넣은 것과 같은 이유예요. 그래서 결과도 두 겹이고, idx[0]으로 첫 사진의 결과를 꺼내요. idx의 179, 228, 225는 X_known 안에서 몇 번째 사진인지예요. 사람 번호가 아니에요. y_known[idx[0]]으로 바꾸면 17, 22, 22번 사람이에요. 거리는 6.07, 6.26, 6.44예요." + REAL + IMGN)

o = [sec("pred")] + head(EB4, "predict는 이웃 3장의 다수결을 돌려줘요", K4)
CFS[0] = 28
PR = ["pred = model.predict([new_photo])", 'print("pred:", pred)', 'print("예측한 사람:", pred[0])', 'print("실제 정답:", y[new_index])']
o += cell({"id": "c-pr", "lines": PR, "n": 16, "out": ["pred: [22]", "예측한 사람: 22", "실제 정답: 22"]}, 96, 196, 900, sel="c-pr")
o.append(label(1040, 196 + 784 * 354 / 1280 + 120, "이웃 3장의 사람 번호", SUB, 26))
o.append(img(1040, 196, 784, "one-1.png", tid="i-one"))
IH = 784 * 354 / 1280
VY = 196 + IH + 24
for k, n_ in enumerate([17, 22, 22]):
    pc = 1040 + (478 + k * 323.5) / 1280 * 784
    o.append(pdisc(n_, pc - 36, VY, 72, "", f"vs{k}"))
TY2 = 196 + chight(4, 3) + 60
o.append(label(96, TY2 - 56, "투표", SUB, 26, fade(1)))
o.append(label(96, TY2 + 10, "22번", P22, 44, fade(1)))
o.append(label(96, TY2 + 110, "17번", P17, 44, fade(1)))
o.append(pdisc(22, 260, TY2 + 6, 72, fly(2, "vs1")))
o.append(pdisc(22, 350, TY2 + 6, 72, fly(2, "vs2")))
o.append(pdisc(17, 260, TY2 + 106, 72, fly(2, "vs0")))
o.append(ring(3, 96, TY2 + 6, 330, 72, P22, 5))
o.append(p(f"position:absolute;left:560px;top:{TY2 + 20}px;font-size:72px;font-weight:900;color:{P22}", "→ 22번", fade(3)))
o.append(caption("이웃 3장 중 22번이 2장이라 22번으로 예측했고, 정답도 22번이에요.", 950, 4))
W("pred", o, "predict에 새 사진을 넣으면 답이 나와요. kneighbors와 같은 이유로 대괄호를 한 겹 더 감싸요. 결과도 배열이라 pred[0]으로 꺼내요. 오른쪽 그림은 새 사진과 이웃 3장을 그린 거예요. 이웃이 17번, 22번, 22번이라 22번이 2표로 이겨요. 실제 정답도 22번이니 맞혔어요. 그림 셀 코드는 길어서 덱에서 뺐어요. 노트북 tools/run_nb.py의 PICS 셀에 있어요. 수업 코드는 이웃마다 그림판을 따로 만들었는데, 한 그림판에 4칸으로 모았어요." + REAL + IMGN)

o = [sec("kchange")] + head(EB4, "K를 바꾸면 같은 사진도 답이 달라져요", K4)
CFS[0] = 26
KL = ["for k in [1, 3, 5, 7]:", "    m = KNeighborsClassifier(n_neighbors=k)", "    m.fit(X_known, y_known)", "    d, i = m.kneighbors([new_photo], n_neighbors=k)", '    print(f"K={k} 이웃 {y_known[i[0]]} 예측 {m.predict([new_photo])[0]}")']
KLO = ["K=1 이웃 [17] 예측 17", "K=3 이웃 [17 22 22] 예측 22", "K=5 이웃 [17 22 22 22 17] 예측 22", "K=7 이웃 [17 22 22 22 17 17  3] 예측 17"]
o += cell({"id": "c-kl", "lines": KL, "n": 17, "out": KLO}, 96, 196, 1500, sel="c-kl")
TB_ = [("K=1", "17번 1표", "17", RED), ("K=3", "22번 2표, 17번 1표", "22", GR), ("K=5", "22번 3표, 17번 2표", "22", GR), ("K=7", "22번 3표, 17번 3표, 3번 1표 (동점이면 작은 번호)", "17", RED)]
TT = 196 + chight(5, 4) + 30
for k, (a_, b_, c_, col) in enumerate(TB_):
    y_ = TT + k * 64
    o.append(f'<div{rise(1 + k)} style="position:absolute;left:96px;top:{y_}px;width:1500px;height:60px;display:flex;flex-direction:row;align-items:center;gap:30px;border-bottom:2px solid {LINE}">'
             + p(f"width:140px;font-family:{MONO};font-size:30px;font-weight:700;color:{INK}", a_) + p(f"width:820px;font-size:30px;font-weight:700;color:{SUB}", e(b_))
             + p(f"width:200px;font-family:{MONO};font-size:30px;font-weight:700;color:{col}", f"→ {c_}번") + p(f"font-size:26px;font-weight:700;color:{col}", "맞아요" if col == GR else "틀려요") + '</div>')
o.append(box(5, 90, TT + 3 * 64 - 4, 1512, 64, RED, 4))
o.append(caption("K는 직접 정하는 값이에요. 어떤 K가 좋은지는 6파트에서 채점해서 골라요.", 950, 6))
W("kchange", o, "K를 1, 3, 5, 7로 바꿔 가며 같은 229번 사진을 맞혔어요. K가 1이면 가장 가까운 17번 한 장만 보고 틀려요. K가 3과 5면 22번이 더 많아서 맞아요. K가 7이면 22번 3장, 17번 3장, 3번 1장으로 22번과 17번이 동점이에요. scikit-learn은 동점이면 번호가 작은 쪽을 골라서 17번으로 틀려요. 이렇게 K는 모델이 배우는 값이 아니라 우리가 정하는 값이에요. 수업 코드에 남아 있던 옛 이웃 번호 주석은 실제 결과와 달라서 뺐어요." + REAL)

o = [sec("split")] + head(EB4, "51처럼 나누고, 사람마다 같은 비율로 채점용을 떼요", K4)
CFS[0] = 26
SP = ["from sklearn.model_selection import train_test_split", "", "X_train, X_test, y_train, y_test = train_test_split(", "    faces.data,", "    faces.target,", "    test_size=0.25,",
      "    random_state=42,", "    stratify=faces.target", ")", "", 'print("학습용:", X_train.shape, " 채점용:", X_test.shape)', 'print("사람마다 채점용 장수:", np.bincount(y_test))']
SPO = ["학습용: (300, 4096)  채점용: (100, 4096)", "사람마다 채점용 장수: [2 3 3 3 2 3 2 3 2 2 3 3 2 2 3 2 2 2 3 2 3 3 3 3 2 2 2 2 3 3 3 2 3 2 2 3 3", " 2 3 2]"]
o += cell({"id": "c-sp", "lines": SP, "n": 18, "out": SPO}, 96, 196, 1728, sel="c-sp")
LX = 700
for k, (i_, t_, c_) in enumerate([(3, "문제 X: 사진 400장", K1), (4, "정답 y: 사람 번호 400개", GR), (5, "4분의 1 = 100장을 채점용으로", TE), (6, "51처럼 매번 같게 나눠요", SUB), (7, "사람마다 같은 비율로 (다음 장)", OR)]):
    o.append(tag(LX, ly(196, i_), t_, c_, k + 1, 26))
o.append(tint(6, cx(96, "    ") - 2, ly(196, 7) - LH() / 2, tw("stratify=faces.target") + 4, LH(), OR))
o.append(tag(cx(96, SPO[0], True) + 30, oy(196, 12, 0), "300장으로 배우고 100장으로 채점", TE, 6, 24))
o.append(caption("한 사람 10장 중 2~3장이 채점용, 7~8장이 학습용이에요.", 950, 7))
W("split", o, "51에서 배운 train_test_split으로 나눠요. 문제는 faces.data, 정답은 faces.target이에요. test_size 0.25는 4분의 1을 채점용으로 떼라는 뜻이라 400장 중 100장이에요. random_state 42는 51처럼 실행할 때마다 같은 사진이 채점용이 되게 해요. 새로 나온 칸은 stratify예요. 정답 열을 넣으면 사람마다 같은 비율로 채점용을 떼요. 한 사람에 10장이니 2장이나 3장씩 떼어져요. np.bincount는 0번부터 번호마다 몇 개 있는지 세요. 15에서 딕셔너리로 세던 일을 한 줄로 해요." + REAL, ("p4b", "나눠서 채점하기"))

o = [sec("strat")] + head(EB4, "stratify가 없으면 채점용이 0장인 사람이 생겨요", K4)
SX, SWb = 120, 42
def sbars(top, counts, color, order, title):
    out = [label(96, top - max(counts) * 30 - 100, title, color, 30, fade(order))]
    base = top
    for k, c_ in enumerate(counts):
        h_ = c_ * 30
        col = RED if c_ == 0 or c_ >= 7 else color
        out.append(bar(SX + k * SWb, base - h_, SWb - 8, h_, col, WIPE(order) + DELAY(k * 15), 4))
        out.append(label(SX + k * SWb + 8, base - h_ - 34, str(c_), col if col == RED else SUB, 22, fade(order)))
    out.append(f'<div{fade(order)} style="position:absolute;left:{SX - 10}px;top:{base}px;width:{40 * SWb + 10}px;height:3px;background:#9AA0AB"></div>')
    return out
WS = [2, 3, 3, 3, 2, 3, 2, 3, 2, 2, 3, 3, 2, 2, 3, 2, 2, 2, 3, 2, 3, 3, 3, 3, 2, 2, 2, 2, 3, 3, 3, 2, 3, 2, 2, 3, 3, 2, 3, 2]
NS = [4, 2, 2, 4, 3, 3, 1, 7, 2, 3, 3, 4, 2, 1, 3, 2, 0, 3, 2, 1, 2, 1, 4, 4, 2, 2, 4, 3, 2, 1, 1, 1, 3, 2, 1, 1, 2, 3, 5, 4]
o += sbars(470, WS, OR, 0, "stratify=faces.target: 모두 2장이나 3장")
o += sbars(860, NS, GRAY, 1, "stratify 없이: 0장부터 7장까지")
for k in [0, 10, 16, 20, 30, 39]:
    o.append(label(SX + k * SWb + (4 if k < 10 else -2), 872, str(k), GRAY, 20, fade(1)))
o.append(p(f"position:absolute;left:{SX + 16 * SWb - 90:.0f}px;top:610px;width:220px;text-align:center;font-size:26px;font-weight:700;line-height:1.3;color:{RED}", "16번 사람<br>채점용 0장 ↓", fade(2)))
o.append(note(1100, 280, 724, "막대 하나가 한 사람, 높이는 채점용 장수예요.", SUB, 24))
o.append(caption("stratify 없이 나누면 정확도 83.00%, stratify로 나누면 87.00%예요(다음 장).", 960, 3))
W("strat", o, "stratify를 넣은 경우와 뺀 경우를 사람마다 채점용 장수로 비교했어요. 위는 stratify를 넣어서 모든 사람이 2장이나 3장씩 채점용이에요. 아래는 random_state 42만 주고 그냥 섞어서 나눈 결과예요. 16번 사람은 채점용이 0장이라 채점에서 빠지고, 7번 사람은 7장이 채점용이라 학습용에 3장만 남아요. 학습용 사진이 적은 사람은 맞히기도 어려워요. 같은 K=5 모델로 채점하면 stratify 없이는 83.00%, stratify로 나누면 87.00%예요. 분류에서는 정답 종류마다 고르게 나누려고 stratify를 붙여요. 이 비교 셀은 이해를 도우려고 더했어요." + REAL)

o = [sec("score")] + head(EB4, "score는 채점용 100장 중 맞힌 비율이에요", K4)
CFS[0] = 32
SC = ["K = 5", "model = KNeighborsClassifier(n_neighbors=K)", "model.fit(X_train, y_train)", "", "accuracy = model.score(X_test, y_test)", 'print(f"예측 정확도: {accuracy:.2%}")']
o += cell({"id": "c-sc", "lines": SC, "n": 19, "out": ["예측 정확도: 87.00%"]}, 96, 196, 1100, sel="c-sc")
o.append(tint(1, cx(96, "model.fit(") - 2, ly(196, 2) - LH() / 2, tw("X_train, y_train") + 4, LH(), TR))
o.append(tint(2, cx(96, "accuracy = model.score(") - 2, ly(196, 4) - LH() / 2, tw("X_test, y_test") + 4, LH(), TE))
o.append(tag(cx(96, SC[2]) + 30, ly(196, 2), "학습용 300장 외우기", TR, 1, 26))
o.append(tag(cx(96, SC[4]) + 24, ly(196, 4), "채점용 100장", TE, 2, 26))
o.append(tint(3, cx(96, 'print(f"예측 정확도: {accuracy') - 2, ly(196, 5) - LH() / 2, tw(":.2%") + 4, LH(), OR))
o.append(lead_down(3, cx(96, 'print(f"예측 정확도: {accuracy') + tw(":.2%") / 2, ly(196, 5) + LH() / 2, oy(196, 6, 0) + 50, OR, "0.87을 100 곱하고 % 붙여 소수 둘째 자리까지", 26, w=620, anchor="right"))
o.append(label(1270, 300, "정확도 (accuracy)", SUB, 34, fade(4)))
o.append(bigval(1260, 370, "87.00%", TE, 140, fade(4) + COUNT(4)))
o.append(note(1270, 560, 560, "회귀의 R²(48) 대신, 분류는 맞힌 비율로 채점해요.", INK, 30, fade(4)))
o.append(caption("처음 보는 사진 100장 중 87장의 사람을 맞혔어요.", 950, 5))
W("score", o, "이번에는 K를 5로 정하고 학습용 300장으로 fit해요. score에 채점용 사진과 정답을 넣으면 100장을 모두 predict해서 정답과 비교하고, 맞힌 비율을 돌려줘요. 이 비율을 정확도, accuracy라고 해요. 48의 회귀 모델 score는 R제곱이었는데, 분류 모델 score는 정확도예요. f-string의 :.2%는 13의 :.2f처럼 소수 자리를 정하는데, 100을 곱하고 % 기호를 붙여 줘요. 0.87이 87.00%가 돼요." + REAL)

o = [sec("byhand")] + head(EB4, "87.00%는 맞힌 장수를 세서 나눈 값이에요", K4)
CFS[0] = 28
BH = ["pred = model.predict(X_test)", 'print("정답:", y_test[:8])', 'print("예측:", pred[:8])', 'print("맞았나:", (pred == y_test)[:8])', 'print("맞힌 장수:", (pred == y_test).sum(), "/", len(y_test))', 'print("비율:", (pred == y_test).mean())']
BHO = ["정답: [24  5 15 30 37 15 36  4]", "예측: [24  5  0 30 37  0 36  4]", "맞았나: [ True  True False  True  True False  True  True]", "맞힌 장수: 87 / 100", "비율: 0.87"]
o += cell({"id": "c-bh", "lines": BH, "n": 20, "out": BHO}, 96, 196, 1728, sel="c-bh")
o.append(tint(1, cx(96, "정답: [24  5 ", True) - 2, oy(196, 6, 0) - LH() / 2, tw("15") + 4, LH(), RED))
o.append(tint(1, cx(96, "예측: [24  5  ", True) - 2, oy(196, 6, 1) - LH() / 2, tw("0") + 4, LH(), RED))
o.append(tint(1, cx(96, "정답: [24  5 15 30 37 ", True) - 2, oy(196, 6, 0) - LH() / 2, tw("15") + 4, LH(), RED))
o.append(tint(1, cx(96, "예측: [24  5  0 30 37  ", True) - 2, oy(196, 6, 1) - LH() / 2, tw("0") + 4, LH(), RED))
o.append(tag(cx(96, BHO[1], True) + 30, oy(196, 6, 1) - 20, "15번 사람을 0번으로 두 번 (6파트)", RED, 1, 26))
o.append(tag(cx(96, BHO[2], True) + 30, oy(196, 6, 2), "True는 1, False는 0으로 세요", GR, 2, 26))
o.append(tag(cx(96, BHO[3], True) + 30, oy(196, 6, 3), "sum: True 개수", GR, 3, 26))
o.append(tag(cx(96, BHO[4], True) + 30, oy(196, 6, 4), "mean: 87 ÷ 100", GR, 4, 26))
o.append(caption("score 한 줄이 이 계산을 대신해요.", 950, 5))
W("byhand", o, "score가 하는 일을 직접 따라가요. predict로 채점용 100장을 모두 맞히고, 앞 8장만 정답과 나란히 찍었어요. 셋째와 여섯째 사진은 15번 사람인데 0번으로 틀렸어요. pred == y_test는 칸마다 같은지 물어서 True, False 100개를 만들어요. 파이썬은 True를 1, False를 0으로 세서 sum은 맞힌 장수 87이 되고, mean은 87을 100으로 나눈 0.87이 돼요. score가 돌려준 87.00%와 같아요." + REAL)

o = [sec("vs")] + head(EB4, "48~51의 회귀와 52의 분류를 나란히 봐요", K4)
VR = [("맞히는 것", "점수, 집값 같은 숫자", "몇 번 사람 같은 종류"), ("모델", "LinearRegression, SGDRegressor", "KNeighborsClassifier"), ("fit이 하는 일", "기울기 w, 절편 b 계산", "학습용 사진 외워 두기"),
      ("predict가 하는 일", "w × x + b", "가까운 K장의 다수결"), ("score", "R² (48)", "정확도 (맞힌 비율)"), ("직접 정하는 값", "eta0 (49)", "n_neighbors (K)")]
o += plain_rows(96, 210, 1728, VR, [380, 640, 640], 1, 100, ("", "회귀 (48~51)", "분류 (52)"), 30)
o.append(caption("나누기(train_test_split), fit, predict, score 순서는 그대로예요.", 950, 8))
W("vs", o, "51까지 배운 회귀와 오늘 배운 분류를 나란히 놓았어요. 회귀는 숫자를, 분류는 정해진 종류 중 하나를 맞혀요. 모델 이름 끝이 Regressor, Regression이면 회귀, Classifier면 분류예요. fit이 하는 일은 많이 달라요. 회귀는 기울기와 절편을 계산하고, KNN은 사진을 외워 두기만 해요. score는 회귀가 R제곱, 분류가 정확도예요. 직접 정하는 값으로 49는 학습률 eta0, 오늘은 K가 있었어요. 그래도 나누고, fit하고, predict하고, score로 채점하는 순서는 같아요. 51의 스케일링은 오늘 하지 않았어요. 사진은 모든 칸이 0과 1 사이라 이미 크기가 같아요.")

# ---------- part 5 ----------
o = [sec("e-1d")] + head(EB5, "사진 한 장을 대괄호 없이 넣으면 2D를 달라고 해요", K5)
CFS[0] = 28
o += cell({"id": "c-e1", "lines": ["model.predict(new_photo)"], "n": 21, "out": ["ValueError: Expected 2D array, got 1D array instead:", "array=[0.17355372 0.1322314  0.11157025 ... 0.3264463  0.30165288 0.24380165].",
                                                                             "Reshape your data either using array.reshape(-1, 1) if your data", "has a single feature or array.reshape(1, -1) if it contains a single sample."], "err": True}, 96, 196, 1728, sel="c-e1")
o.append(shake(1, "c-e1"))
o.append(reading(96, 520, "2D(두 겹)를 달라는데 1D(한 겹)가 들어왔어요. 모델은 사진 여러 장을 받는 자리라 사진 1장도 한 겹 더 감싸요.", INK, 2, 30))
o.append(fix(96, 640, "model.predict(new_photo)", "model.predict([new_photo])", 3, 34))
for k, (lab_, two) in enumerate([("new_photo  (1D, 한 겹)", False), ("[new_photo]  (2D, 사진 1장짜리 묶음)", True)]):
    x0 = 96 + k * 880
    o.append(label(x0, 760, lab_, RED if not two else GR, 26, fade(4), mono=True))
    inner = "".join(p(f"width:64px;height:40px;border-radius:6px;border:2px solid #C9CED8;background:{CARD};font-family:{MONO};font-size:18px;line-height:36px;text-align:center;color:{INK}", v) for v in ["0.17", "0.13", "…", "0.24"])
    row = f'<div style="display:flex;flex-direction:row;gap:6px">{inner}</div>'
    if two:
        row = f'<div style="padding:8px 12px;border:3px solid {GR};border-radius:12px;display:flex">{row}</div>'
    o.append(f'<div{fade(4)} style="position:absolute;left:{x0}px;top:810px;display:flex">{row}</div>')
o.append(caption("오류 아래 HINT의 reshape(1, -1)도 같은 일을 해요. 수업에서는 대괄호로 써요.", 950, 5))
W("e-1d", o, "가장 자주 나는 오류예요. 사진 한 장 new_photo는 숫자 4096개짜리 한 겹 배열이에요. 모델은 사진 여러 장, 곧 두 겹을 받게 만들어져 있어서 Expected 2D array, got 1D array라고 해요. 48에서 predict(33)을 넣었을 때와 같은 오류예요. 대괄호로 한 겹 더 감싸서 사진 1장짜리 묶음으로 넣으면 돼요. 오류 메시지가 알려 주는 reshape(1, -1)도 같은 일을 하지만, 수업에서는 대괄호로 써요." + REAL, ("p5", "오류와 함정"))

o = [sec("e-title")] + head(EB5, "그림 제목이 모두 Person 22면 제목 코드를 봐요", K5)
o.append(label(96, 200, "수업 코드", RED, 30))
o.append(img(96, 250, 840, "one-2.png"))
o.append(label(984, 200, "고친 코드", GR, 30, fade(2)))
o.append(img(984, 250, 840, "one-1.png", fade(2)))
o.append(box(1, 96 + 840 * 343 / 1280, 250, 840 * 270 / 1280, 840 * 60 / 1280, RED, 4))
o.append(fix(96, 620, 'set_title(f"Person {y[new_index]}")', 'set_title(f"Person {y_known[j]}")', 2, 28))
o.append(reading(96, 780, "y[new_index]는 새 사진의 정답이라 늘 22예요. 이웃 j번의 사람 번호는 y_known[j]예요.", INK, 3, 30))
o.append(caption("오류 없이 그림만 틀려요. 첫 이웃은 17번인데 22번으로 보여요.", 950, 4))
W("e-title", o, "수업 코드에서 실제로 있던 실수예요. 이웃 사진을 그리면서 제목에 y[new_index]를 적었어요. new_index는 229라서 y[new_index]는 새 사진의 정답 22예요. 그래서 이웃이 누구든 제목이 모두 Person 22로 나와요. 첫 이웃은 17번 사람인데도요. 오류가 나지 않아서 알아채기 어려워요. 이웃 j번의 사람 번호는 y_known[j]로 꺼내야 해요. 같은 셀에 잘못된 결과와 고친 결과를 나란히 그렸어요." + IMGN)

o = [sec("e-big")] + head(EB5, "K가 학습용 장수보다 크면 이웃을 못 찾아요", K5)
CFS[0] = 28
o += cell({"id": "c-eb", "lines": ["big = KNeighborsClassifier(n_neighbors=500)", "big.fit(X_train, y_train)", "big.predict(X_test)"], "n": 22,
           "out": ["ValueError: Expected n_neighbors <= n_samples_fit, but n_neighbors = 500,", "n_samples_fit = 300, n_samples = 100"], "err": True}, 96, 196, 1728, sel="c-eb")
o.append(tint(1, cx(96, "ValueError: Expected n_neighbors <= n_samples_fit, but ", True) - 2, oy(196, 3, 0) - LH() / 2, tw("n_neighbors = 500") + 4, LH(), RED))
o.append(tint(1, cx(96, "", True) - 2, oy(196, 3, 1) - LH() / 2, tw("n_samples_fit = 300") + 4, LH(), TR))
o.append(reading(96, 580, "이웃 500장을 찾으라는데 외운 사진(n_samples_fit)이 300장뿐이에요.", INK, 2, 32))
o.append(note(96, 680, 1728, "fit은 오류 없이 지나가요(외우기만 하니까요). 이웃을 찾는 predict에서 오류가 나요.", SUB, 28, fade(3)))
o.append(fix(96, 790, "n_neighbors=500", "n_neighbors=5", 4, 34))
o.append(caption("K는 학습용 장수보다 훨씬 작게 정해요. 이 데이터에서는 한 사람 장수(7~8장)보다도 작게요.", 950, 5))
W("e-big", o, "K를 500으로 정한 모델이에요. fit은 외우기만 해서 오류 없이 지나가요. predict에서 이웃 500장을 찾으려는데, 외운 사진은 학습용 300장뿐이라 오류가 나요. n_samples_fit은 fit에 넣은 사진 수, n_samples는 predict에 넣은 사진 수예요. K는 학습용 장수보다 훨씬 작아야 해요. 이 데이터는 한 사람의 학습용 사진이 7장이나 8장이라, K가 그보다 크면 다른 사람 사진이 꼭 섞여요." + REAL)

o = [sec("e-small")] + head(EB5, "stratify로 나눌 때 채점용이 사람 수보다 적으면 안 돼요", K5)
CFS[0] = 24
o += cell({"id": "c-es", "lines": ["train_test_split(faces.data, faces.target, test_size=0.05, random_state=42, stratify=faces.target)"], "n": 23,
           "out": ["ValueError: The test_size = 20 should be greater or equal to the number of classes = 40"], "err": True}, 96, 196, 1728, sel="c-es")
o.append(tint(1, cx(96, "train_test_split(faces.data, faces.target, ") - 2, ly(196, 0) - LH() / 2, tw("test_size=0.05") + 4, LH(), RED))
o.append(label(cx(96, "train_test_split(faces.data, faces.target, "), oy(196, 1, 0) + 40, "400장 × 0.05 = 20장", RED, 28, fade(1)))
for k in range(40):
    x_ = 96 + (k % 20) * 86
    y_ = 440 + (k // 20) * 96
    filled = k < 20
    o.append(p(f"position:absolute;left:{x_}px;top:{y_}px;width:72px;height:72px;border-radius:50%;border:3px {'solid' if filled else 'dashed'} {TE if filled else '#C9CED8'};background:{TEB if filled else CARD};font-family:{MONO};font-size:24px;font-weight:700;line-height:66px;text-align:center;color:{INK if filled else '#B4B9C3'}", str(k), rise(2) + DELAY(k * 15)))
o.append(note(96, 660, 1728, "사람마다 1장 이상 떼려면 40장은 있어야 해요. 20장으로는 20명이 채점용 0장이에요.", INK, 30, fade(3)))
o.append(fix(96, 780, "test_size=0.05", "test_size=0.25", 4, 32))
o.append(caption("classes는 정답 종류, 여기서는 사람 40명이에요.", 960, 5))
W("e-small", o, "stratify로 나눌 때 채점용을 너무 적게 잡으면 나는 오류예요. test_size 0.05는 400장의 5%, 20장이에요. stratify는 사람마다 같은 비율로 떼야 하는데, 사람이 40명이라 한 명에 1장씩만 떼도 40장이 필요해요. 20장으로는 20명이 채점용에 하나도 안 들어가요. 그래서 test_size는 classes 수인 40보다 크거나 같아야 한다고 알려 줘요. classes는 정답 종류, 여기서는 사람 수예요. 수업처럼 0.25로 100장을 떼면 돼요." + REAL)

o = [sec("e-trap")] + head(EB5, "같은 사람인데 다른 사람보다 멀 때도 있어요", K5)
CFS[0] = 24
TP = ['print("0번, 1번, 10번 사람:", y[0], y[1], y[10])', 'print("0번과 1번 거리 (같은 사람):", np.sqrt(((X[0] - X[1]) ** 2).sum()).round(2))', 'print("0번과 10번 거리 (다른 사람):", np.sqrt(((X[0] - X[10]) ** 2).sum()).round(2))']
o += cell({"id": "c-tp", "lines": TP, "n": 24, "out": ["0번, 1번, 10번 사람: 0 0 1", "0번과 1번 거리 (같은 사람): 12.7", "0번과 10번 거리 (다른 사람): 10.36"]}, 96, 196, 1500, sel="c-tp")
FY3 = 580
o.append(face(760, FY3, 280, "d0.png", color=NEW))
o.append(label(800, FY3 + 290, "0번 (0번 사람)", INK, 26))
o.append(face(240, FY3, 280, "d1.png", rise(1), color=GR))
o.append(label(270, FY3 + 290, "1번 (0번 사람)", GR, 26, rise(1)))
o.append(face(1280, FY3, 280, "d10.png", rise(2), color=GRAY))
o.append(label(1310, FY3 + 290, "10번 (1번 사람)", GRAY, 26, rise(2)))
o.append(label(560, FY3 + 80, "12.70", RED, 44, rise(1), mono=True))
o.append(f'<div{WIPE(1)} style="position:absolute;left:530px;top:{FY3 + 150}px;width:220px;height:5px;background:{RED}"></div>')
o.append(label(1100, FY3 + 80, "10.36", GRAY, 44, rise(2), mono=True))
o.append(f'<div{WIPE(2)} style="position:absolute;left:1050px;top:{FY3 + 150}px;width:220px;height:5px;background:{GRAY}"></div>')
o.append(caption("고개가 돌아가고 배경이 어두워지면 칸 값이 많이 바뀌어요. KNN은 칸 값만 비교해요.", 960, 3))
W("e-trap", o, "오류는 아니지만 꼭 알아 둘 함정이에요. 0번과 1번 사진은 같은 0번 사람이고, 10번 사진은 안경 쓴 1번 사람이에요. 그런데 거리를 재면 같은 사람끼리 12.70, 다른 사람과 10.36으로 다른 사람이 더 가까워요. 1번 사진은 고개를 돌려서 얼굴 자리가 옮겨 갔고 오른쪽 배경이 어두워요. KNN은 같은 자리 칸끼리 값만 비교해서, 얼굴이 조금 옮겨 가거나 밝기가 달라지면 거리가 크게 늘어요. 그래서 KNN이 틀리는 사진이 생겨요. 이 셀은 이해를 도우려고 더했어요." + REAL + IMGN)

# ---------- part 6 ----------
o = [sec("x-k")] + head(EB6, "K를 몇으로 할까요? 채점해 보고 골라요", K6)
CFS[0] = 26
KT = ["for k in [1, 3, 5, 7, 9]:", "    m = KNeighborsClassifier(n_neighbors=k)", "    m.fit(X_train, y_train)", '    print(f"K={k}: {m.score(X_test, y_test):.2%}")']
o += cell({"id": "c-kt", "lines": KT, "n": 25, "out": ["K=1: 95.00%", "K=3: 92.00%", "K=5: 87.00%", "K=7: 79.00%", "K=9: 76.00%"]}, 96, 196, 1000, sel="c-kt")
KV = [(1, 95), (3, 92), (5, 87), (7, 79), (9, 76)]
for k, (kk, v_) in enumerate(KV):
    y_ = 230 + k * 120
    w_ = (v_ - 50) * 10.5
    o.append(label(1160, y_ + 18, f"K={kk}", INK, 30, "", mono=True))
    o.append(bar(1290, y_, w_, 70, TE if kk != 1 else GR, WIPE(1) + DELAY(k * 100)))
    o.append(label(1290 + w_ + 16, y_ + 16, f"{v_}%", TE if kk != 1 else GR, 32, fade(1) + DELAY(k * 100)))
o.append(label(1160, 850, "막대는 50%부터 그렸어요", SUB, 22))
o.append(note(96, 196 + chight(4, 5) + 40, 1000, "한 사람의 학습용 사진이 7~8장뿐이라, K가 커질수록 다른 사람 사진이 투표에 섞여요.", INK, 30, fade(2)))
o.append(caption("이 데이터에서는 K=1이 가장 잘 맞혔어요. 데이터마다 다르니 꼭 채점해서 골라요.", 950, 3))
W("x-k", o, "어떤 K가 좋은지는 채점해서 정해요. K를 1, 3, 5, 7, 9로 바꿔 가며 같은 학습용으로 fit하고 채점용으로 채점했어요. 이 데이터에서는 K=1이 95%로 가장 높고 K가 커질수록 떨어져요. 한 사람의 학습용 사진이 7장이나 8장뿐이라, K가 커지면 다른 사람 사진이 투표에 섞이기 때문이에요. 229번 사진 한 장에서는 K=1이 틀렸지만, 100장을 채점하면 K=1이 가장 잘 맞아요. 한 장만 보고 K를 정하면 안 되는 이유예요. 51에서 본 것처럼 채점용이 100장뿐이라 나누는 방법에 따라 순위가 조금 바뀔 수 있어요. 이 셀은 이해를 도우려고 더했어요." + REAL, ("p6", "실제 상황"))

o = [sec("x-wrong")] + head(EB6, "틀린 13장을 모아 보면 헷갈린 사람이 보여요", K6)
CFS[0] = 24
WR = ["wrong = pred != y_test", 'print("틀린 장수:", wrong.sum())', 'print("정답:", y_test[wrong])', 'print("예측:", pred[wrong])', "", "show_person(0)", "show_person(15)"]
WRO = ["틀린 장수: 13", "정답: [15 15  2  0 21  3 28 34  0 16 23  2  9]", "예측: [ 0  0 39 17 38 39 20  4 15 24 20 24  7]"]
o += cell({"id": "c-wr", "lines": WR, "n": 26, "out": WRO}, 96, 196, 1000, sel="c-wr")
for (a_, b_) in [("정답: [", "15 15"), ("예측: [ ", "0  0")]:
    j = 1 if a_.startswith("정답") else 2
    o.append(tint(1, cx(96, a_, True) - 2, oy(196, 7, j) - LH() / 2, tw(b_) + 4, LH(), RED))
o.append(tint(2, cx(96, "정답: [15 15  2  ", True) - 2, oy(196, 7, 1) - LH() / 2, tw("0") + 4, LH(), OR))
o.append(tint(2, cx(96, "정답: [15 15  2  0 21  3 28 34  ", True) - 2, oy(196, 7, 1) - LH() / 2, tw("0") + 4, LH(), OR))
o.append(tint(2, cx(96, "예측: [ 0  0 39 17 38 39 20  4 ", True) - 2, oy(196, 7, 2) - LH() / 2, tw("15") + 4, LH(), OR))
o.append(note(1140, 220, 680, "15번을 0번으로 2번 틀렸어요.", RED, 30, fade(1)))
o.append(note(1140, 300, 680, "0번을 15번으로 1번, 17번으로 1번 틀렸어요.", OR, 30, fade(2)))
IY = 196 + chight(7, 3) + 30
o.append(label(96, IY, "0번 사람", INK, 26, rise(3)))
o.append(img(260, IY - 10, 1564, "score-2.png", rise(3), border=False))
o.append(label(96, IY + 170, "15번 사람", INK, 26, rise(3)))
o.append(img(260, IY + 160, 1564, "score-3.png", rise(3), border=False))
W("x-wrong", o, "틀린 사진만 모아 봐요. pred != y_test는 틀린 칸만 True예요. 이걸 대괄호에 넣으면 틀린 사진의 정답과 예측만 남아요. 13장이 틀렸어요. 87장을 맞혔으니 100에서 87을 뺀 13과 같아요. 15번 사람을 0번으로 두 번, 0번 사람을 15번으로 한 번 틀렸어요. 두 사람 사진을 앞에서 만든 show_person으로 그려 보면, 둘 다 짧은 머리에 정면을 보고 밝기도 비슷해요. 칸 값만 비교하는 KNN에게는 헷갈리기 쉬운 두 사람이에요. 이 셀은 이해를 도우려고 더했어요." + REAL + IMGN)

# ---------- closing ----------
o = [sec("trouble")] + head("정리", "막히면 출력의 마지막 줄과 대괄호부터 봐요", RED)
TBL = [("ValueError: Expected 2D array, got 1D array instead", "사진 1장을 대괄호 없이 넣었어요", "model.predict([new_photo])"),
       ("ValueError: Expected n_neighbors <= n_samples_fit", "K가 학습용 장수보다 커요", "n_neighbors=5"),
       ("ValueError: The test_size = 20 should be greater or equal to ...", "stratify인데 채점용이 사람 수보다 적어요", "test_size=0.25"),
       ("사진이 보라와 노랑으로 나와요", "imshow에 cmap을 안 적었어요", 'cmap="gray", vmin=0, vmax=1'),
       ("이웃 제목이 모두 같은 번호예요", "새 사진의 정답 y[new_index]를 적었어요", "y_known[j]")]
for i, (q, a_, cmd) in enumerate(TBL):
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:96px;top:{196 + i * 128}px;width:1728px;height:128px;display:flex;flex-direction:row;align-items:center;gap:26px;border-bottom:2px solid {LINE}">'
             + '<div style="flex:1;display:flex;flex-direction:column;gap:4px">' + p(f"{'font-family:' + MONO + ';' if q.isascii() else ''}font-size:24px;font-weight:700;color:{RED};white-space:nowrap", e(q)) + p(f"font-size:26px;color:{INK}", e(a_)) + '</div>'
             + p(f"width:560px;flex:none;font-family:{MONO};font-size:24px;font-weight:700;color:{GR};white-space:pre", '✓ ' + e(cmd)) + '</div>')
o.append(caption("새 사진은 늘 [사진]으로 감싸고, 나눈 뒤에는 shape를 한 번 찍어 봐요.", 900))
W("trouble", o, "막히면 출력의 마지막 줄부터 읽어요. 앞의 셋은 ValueError로 바로 알려 줘요. 첫째는 대괄호, 둘째는 K, 셋째는 test_size예요. 넷째와 다섯째는 오류 없이 그림만 이상한 경우예요. 사진 색이 이상하면 cmap, 제목이 이상하면 제목에 넣은 변수를 봐요.", ("trouble", "정리"))

o = [sec("recap")] + head("정리", "사진으로 사람을 맞히는 네 단계", K1)
STEPS = [("사진을 숫자로", "X = faces.data", "한 장이 0~1 숫자 4096개", K2),
         ("나누기", "train_test_split(..., test_size=0.25, stratify=faces.target)", "사람마다 같은 비율로", K3),
         ("외우기", "KNeighborsClassifier(n_neighbors=K).fit(X_train, y_train)", "fit은 계산 없이 저장", K4),
         ("맞히고 채점", "model.predict([new_photo])\nmodel.score(X_test, y_test)", "가까운 K장 다수결, 맞힌 비율", TE)]
for i, (h_, code, d, c_) in enumerate(STEPS):
    y = 200 + i * 150
    o.append(f'<div{rise(1 + i)} style="position:absolute;left:96px;top:{y}px;width:1728px;height:130px;display:flex;flex-direction:row;align-items:center;gap:30px;border-bottom:2px solid {LINE}">'
             + num(i + 1, c_, 40) + p(f"width:240px;flex:none;font-size:34px;font-weight:700;color:{INK}", e(h_))
             + p(f"flex:1;font-family:{MONO};font-size:24px;font-weight:700;line-height:1.5;color:{INK};white-space:pre", e(code))
             + p(f"width:380px;flex:none;font-size:26px;color:{SUB}", e(d)) + '</div>')
o.append(note(96, 830, 1728, "거리는 칸끼리 빼고, 제곱하고, 더하고, 루트를 씌운 값이에요. 작을수록 닮았어요.", INK, 30, fade(5)))
o.append(caption("다음에 배울 것: 합격, 불합격처럼 둘 중 하나를 확률로 맞히는 로지스틱 회귀", 950, 6))
W("recap", o, "오늘 배운 순서를 정리해요. 먼저 사진을 숫자 4096개짜리 한 줄로 읽어요. 그다음 51처럼 학습용과 채점용으로 나누는데, 분류에서는 stratify로 사람마다 같은 비율로 떼요. KNN의 fit은 학습용 사진을 외워 두기만 해요. predict는 새 사진과 가장 가까운 K장을 찾아 다수결로 답하고, score는 맞힌 비율을 돌려줘요. K는 우리가 정하는 값이라 채점해서 골라요. 다음 챕터에서는 합격과 불합격처럼 둘 중 하나를 고르면서 그 확률까지 알려 주는 로지스틱 회귀를 배워요.", ("recap", "정리"))

o = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장으로 보는 오늘의 코드</h2>']
CHS = [("데이터 받기", 'from sklearn.datasets import fetch_olivetti_faces\nfaces = fetch_olivetti_faces(data_home="./datasets")', K1),
       ("사진 그리기", 'plt.imshow(faces.images[0], cmap="gray", vmin=0, vmax=1)', K2),
       ("나누기", "X_train, X_test, y_train, y_test = train_test_split(\n    faces.data, faces.target, test_size=0.25, random_state=42, stratify=faces.target)", K3),
       ("KNN 학습과 채점", "from sklearn.neighbors import KNeighborsClassifier\nmodel = KNeighborsClassifier(n_neighbors=5)\nmodel.fit(X_train, y_train)\nmodel.score(X_test, y_test)", K4),
       ("사진 한 장 맞히기", "model.kneighbors([new_photo])\nmodel.predict([new_photo])", K6)]
y = 180
for k, d, c in CHS:
    n_ = d.count("\n") + 1
    h = 52 + n_ * 36
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:{h}px;display:flex;flex-direction:column;justify-content:center;gap:4px;border-bottom:2px solid {LINE}">'
             + p(f"font-size:26px;font-weight:700;color:{c}", e(k)) + p(f"font-family:{MONO};font-size:24px;font-weight:700;line-height:1.5;color:{INK};white-space:pre", e(d)) + '</div>')
    y += h + 14
o.append(p(f"position:absolute;left:96px;top:{y + 16}px;width:1728px;font-size:30px;font-weight:700;line-height:1.5;color:{INK}", "사진 한 장을 넣을 때는 늘 대괄호로 한 겹 더 감싸요."))
W("cheatsheet", o, "오늘 쓴 코드를 한 장에 모았어요. 데이터를 받고, 사진을 그려 보고, 나누고, KNN으로 학습하고 채점해요. 사진 한 장을 넣을 때는 늘 대괄호로 감싸요.")

# ---------- order and toc ----------
want = ["cover", "toc", "setup", "start", "why", "big", "bundle", "pixel", "imshow", "cmap", "person", "grid",
        "tiny", "tinycode", "flat", "realdist", "vote", "knnname", "known", "fit", "neigh", "pred", "kchange", "split", "strat", "score", "byhand", "vs",
        "e-1d", "e-title", "e-big", "e-small", "e-trap", "x-k", "x-wrong", "trouble", "recap", "cheatsheet"]
assert sorted(want) == sorted(ORDER), (set(want) ^ set(ORDER))
ORDER[:] = want
SECTIONS.pop("p4b", None)
SECTIONS.update({"p2": {"description": "사진은 숫자 표", "start": "bundle"}, "p3": {"description": "거리와 이웃", "start": "tiny"}, "p4": {"description": "KNN 학습하고 채점하기", "start": "knnname"}})
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
parts_ = [("Lightbulb", K1, "왜 필요한가", "why", "big"), ("Book", K2, "사진은 숫자 표", "bundle", "grid"), ("Search", K3, "거리와 이웃", "tiny", "vote"),
          ("Settings", K4, "KNN 학습하고 채점하기", "knnname", "vs"), ("Warning", K5, "오류와 함정", "e-1d", "e-trap"), ("Star", K6, "실제 상황", "x-k", "x-wrong")]
t = [f'<section id="toc" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>']
for i, (ic, c, h, a, b) in enumerate(parts_):
    x, y = 96 + (i // 3) * 884, 230 + (i % 3) * 190
    t.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:844px;height:160px;display:flex;flex-direction:row;align-items:center;gap:28px;border-bottom:2px solid {LINE}">'
             f'<p style="width:70px;font-size:72px;font-weight:900;color:{c}">{i + 1}</p><x-icon name="{ic}" style="width:52px;height:52px;color:{c}"></x-icon>'
             f'<p style="flex:1;font-size:40px;font-weight:700;color:{INK}">{e(h)}</p><p style="font-size:28px;color:{GRAY}">{page[a]}–{page[b]}쪽</p></div>')
t.append(f'<p style="position:absolute;left:96px;top:880px;font-size:30px;color:{SUB}">{page["setup"]}–{page["start"]}쪽은 노트북 준비, {page["trouble"]}–{page["cheatsheet"]}쪽은 막힐 때와 정리, 한 장 요약이에요.</p>')
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(t) + "\n<aside>" + e("1파트에서 회귀와 분류의 차이와 KNN의 큰 그림을 보고, 2파트에서 사진이 숫자 표라는 걸 확인해요. 3파트는 두 사진의 거리를 손으로 재 보고 이웃의 다수결을 봐요. 4파트에서 KNeighborsClassifier로 맞히고 채점해요. 수업 노트북 04가 여기까지예요. 5파트는 자주 나는 오류와 함정, 6파트는 K 고르기와 틀린 사진 살펴보기예요.") + "</aside>\n</section>\n")
deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-27T09:00:00Z"}, "lists": "css", "title": "사진으로 사람 맞히기 (얼굴 데이터와 KNN)", "order": ORDER, "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
print(len(ORDER), "slides")
