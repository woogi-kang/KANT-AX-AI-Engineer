"""Generates every slide of the sorting deck (22, sorted, sort, max, min and key) and slides/deck.json.

Story: keeps writing in basics.ipynb from chapters 12-21. Starts from max(sales) returning 'tea' instead of the best
seller, draws key as a function that makes the values to compare, then sorted next to sort (and the None trap), reverse,
how strings compare, key=len, str.lower and int, tuples compared slot by slot, lambda keys and two-part keys, sorting a
dictionary by key, value or item, max and min with key and default, and sum, len and slicing. Part 5 collects the usual
errors, and part 6 builds a sales ranking, price board, menu board and score sheet.

Layout rules (Stageshow, see tools/DESIGN.md): one focal object per slide (the notebook cell or one picture), terms
labelled beside the code line or picture with leader tags instead of cards, the speaker notes carry the explanation,
values that move are animated with fly, and a fix is the wrong line struck through next to the right one.
Every cell and output comes from tools/demo.sh (tools/run_nb.py runs the cells with the project kernel).
Usage: python3 tools/gen.py slides
"""

import html, json, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from highlight import spot, spot_off, ring, box, underline

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
INK, SUB, LINE, CARD = "#1D2330", "#4A5262", "#E1DED6", "#FFFFFF"
BL, GR, OR, PUR, RED, TEAL, GRAY = "#2459C9", "#1F8A4C", "#B26A00", "#5A3BB8", "#A33131", "#0F7C86", "#6A7180"
JP = "#B8560F"          # Jupyter, same as chapters 09 and 10
SEL = "#2F7DE1"         # selected cell bar, like VS Code's focus color
FAINT = "#F1F0EC"
NB = "basics.ipynb"
K1, K1BG = "#1E5FA8", "#E5EEF8"
K2, K2BG = "#A0620A", "#F7EEDD"
K3, K3BG = TEAL, "#E2F2F3"
K4, K4BG = "#A23B72", "#F6E7EF"
K5, K5BG = RED, "#F8E6E6"
K6, K6BG = PUR, "#ECE7F8"
GRBG = "#E6F4EC"
REAL = " 출력은 실제로 실행한 결과예요."


def e(s):
    return html.escape(s, quote=False)


def p(style, text, attrs=""):
    return f'<p{attrs} style="{style}">{text}</p>'


def at(kind, order):
    return f' data-build-in="{kind} order {order}"' if order else ""


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


def caption(text, top=960, order=None):
    return p(f"position:absolute;left:96px;top:{top}px;width:1728px;font-size:34px;font-weight:700;line-height:1.4;color:{INK}", text,
             ' id="caption"' + (at("rise", order) or ' data-build-in="rise"'))


def num(i, color, size=56):
    return p(f"width:{size + 16}px;height:{size + 16}px;flex:none;border-radius:50%;background:{color};color:#FFFFFF;font-size:{size * 0.6:.0f}px;font-weight:900;line-height:{size + 16}px;text-align:center", str(i))


def kbd(text, size=30):
    caps = [p(f"font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.2;white-space:nowrap;color:{INK};background:#FFFFFF;border:2px solid #C9CED8;border-bottom-width:5px;border-radius:10px;padding:6px 14px", e(k)) for k in text.split("+")]
    plus = p(f"font-size:{size * 0.8:.0f}px;font-weight:700;color:{GRAY}", "+")
    return '<div style="display:flex;flex-direction:row;align-items:center;gap:8px">' + plus.join(caps) + '</div>'


# ---------- notebook cell, drawn at FS px ----------
FS = 30
LH = FS * 1.45          # 43.5


def cell(c, left, top, w, sel=True, attrs=""):
    """A notebook cell: [n] gutter, the code box, then the output lines. c: dict(lines, n, out, err)."""
    lines, n = c.get("lines", [""]), c.get("n")
    o = [f'<div{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;display:flex;flex-direction:column;gap:10px">']
    bar = f'<div style="width:7px;flex:none;border-radius:4px;background:{SEL if sel else "transparent"}"></div>'
    gutter = p(f"width:58px;flex:none;font-family:{MONO};font-size:22px;color:{GRAY};text-align:right;padding-top:12px", f"[{n}]" if n else "[ ]")
    txt = "".join(p(f"font-family:{MONO};font-size:{FS}px;line-height:1.45;white-space:pre;color:{INK}", e(l) if l else "&#160;") for l in lines)
    tag_ = p(f"position:absolute;right:14px;bottom:8px;font-size:18px;color:{GRAY}", "Python")
    box_ = f'<div style="flex:1;position:relative;background:#FFFFFF;border:2px solid {LINE};border-radius:10px;padding:8px 18px 8px;display:flex;flex-direction:column">{txt}{tag_}</div>'
    o.append(f'<div style="display:flex;flex-direction:row;gap:10px;align-items:stretch">{bar}{gutter}{box_}</div>')
    if c.get("out"):
        import re
        col = lambda l: RED if c.get("err") and re.match(r"[A-Za-z]+(Error|Interrupt)", l) else INK
        o.append("".join(p(f"margin-left:85px;padding:0 20px;font-family:{MONO};font-size:{FS}px;line-height:1.45;white-space:pre;color:{col(l)}", e(l) if l else "&#160;") for l in c["out"]))
    o.append('</div>')
    return o


def cell_bottom(top, n, nout):
    """y just under the last output line of a cell."""
    return top + 20 + n * LH + (10 + nout * (LH + 10) - 10 if nout else 0)


HL = {"run": "rgba(31,138,76,0.16)", "skip": "rgba(106,113,128,0.20)", "err": "rgba(163,49,49,0.14)", "mark": "rgba(36,89,201,0.14)", "or": "rgba(178,106,0,0.14)"}


def hl(left, top, w, i, n=1, kind="run", order=1):
    """Tints code lines i..i+n-1 of a cell drawn by cell(c, left, top, w)."""
    y = top + 10 + i * LH
    return f'<div{at("fade", order)} style="position:absolute;left:{left + 87}px;top:{y:.0f}px;width:{w - 89}px;height:{n * LH:.0f}px;background:{HL[kind]};border-radius:6px"></div>'


def ly(top, i):
    """Center y of code line i in a cell drawn at top."""
    return top + 10 + i * LH + LH / 2


def oy(top, n, j):
    """Center y of output line j of a cell with n code lines (output lines sit 10px apart)."""
    return top + 20 + n * LH + 10 + j * (LH + 10) + LH / 2


def tw(s, size=FS):
    """Rendered width of a monospace string: Hangul is about one em, the rest 0.6 em."""
    return sum(size * (1.0 if '가' <= ch <= '힣' else 0.6) for ch in s)


def cx(left, prefix):
    """x where the text after `prefix` starts on a code or output line of a cell at left."""
    return left + 105 + tw(prefix)


def tag(x, y, text, color, order=None, size=28, lead=True):
    """A leader label: '← text' centred on y. No box."""
    t = ("← " if lead else "") + e(text)
    return p(f"position:absolute;left:{x:.0f}px;top:{y - size * 0.72:.0f}px;font-size:{size}px;font-weight:700;line-height:1.45;color:{color};white-space:nowrap", t, at("fade", order))


def lbl(x, y, text, color, order=None, size=28, w=None, mono=False):
    """A plain label whose top-left is (x, y)."""
    ws = f"width:{w}px;" if w else ""
    return p(f"position:absolute;left:{x:.0f}px;top:{y:.0f}px;{ws}font-family:{MONO if mono else SANS};font-size:{size}px;font-weight:700;line-height:1.4;color:{color};white-space:nowrap", e(text), at("fade", order))


def out_ring(order, left, top, n, j, text, color=RED, prefix=""):
    """Pen loop around (part of) output line j: the part after prefix."""
    x = cx(left, prefix) - 8
    return box(order, int(x), int(oy(top, n, j) - LH / 2 - 2), int(tw(text) + 16), int(LH + 4), color)


def code_line(order, left, top, i, prefix, text, color=OR):
    """Pen underline under `text`, which starts after `prefix` on code line i."""
    x1 = cx(left, prefix)
    return underline(order, int(x1), int(x1 + tw(text)), int(ly(top, i) + LH / 2 - 2), color)


def out_line(order, left, top, n, j, prefix, text, color=RED):
    x1 = cx(left, prefix)
    return underline(order, int(x1), int(x1 + tw(text)), int(oy(top, n, j) + LH / 2 - 2), color)


def vbox(sid, text, x, y, w, h, color=GRAY, bg=FAINT, attrs="", fs=34, faint=False, sub=None):
    """One value drawn as a box, absolutely placed. sub: a small second line under the value."""
    i = f' id="{sid}"' if sid else ""
    body = p(f"font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:1.2;color:{'#B4B9C3' if faint else INK};white-space:pre", e(text))
    if sub is not None:
        body += p(f"font-family:{MONO};font-size:{fs - 8}px;font-weight:700;line-height:1.2;color:{color};white-space:pre;margin-top:6px", e(sub))
    return (f'<div{i}{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;border-radius:14px;border:3px solid {color};background:{bg};'
            f'display:flex;flex-direction:column;align-items:center;justify-content:center">{body}</div>')


def harrow(x, y, w, color="#C9CED8", attrs="", rot=0):
    r = f"transform:rotate({rot}deg);transform-origin:center;" if rot else ""
    return f'<x-shape{attrs} kind="arrow-right" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:30px;{r}background:{color}"></x-shape>'


def arrow(w=60, color="#C9CED8"):
    return f'<x-shape kind="arrow-right" style="width:{w}px;height:30px;flex:none;background:{color}"></x-shape>'


def row(left, top, w, h, inner, order=None, gap=18):
    return f'<div{at("rise", order)} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;display:flex;flex-direction:row;align-items:center;gap:{gap}px">' + inner + '</div>'


def small(t, color=SUB, size=28, w=None, mono=False):
    ws = f"width:{w}px;flex:none;" if w else ""
    return p(f"{ws}font-family:{MONO if mono else SANS};font-size:{size}px;font-weight:700;color:{color};white-space:nowrap", e(t))


def tup(vals, hi=(), color=K3, bg=K3BG, w=170, h=80, fs=30, dim=()):
    """A tuple drawn as joined slots inside round brackets."""
    o = ['<div style="display:flex;flex-direction:row;align-items:center;gap:6px">' + p(f"font-family:{MONO};font-size:{fs + 14}px;font-weight:700;color:{GRAY}", "(")]
    for i, v in enumerate(vals):
        on, off = i in hi, i in dim
        o.append(p(f"width:{w}px;height:{h}px;flex:none;border-radius:12px;border:3px solid {color if on else LINE};background:{bg if on else CARD};font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:{h - 6}px;text-align:center;color:{'#B4B9C3' if off else INK};white-space:pre", e(v)))
    o.append(p(f"font-family:{MONO};font-size:{fs + 14}px;font-weight:700;color:{GRAY}", ")") + '</div>')
    return "".join(o)


def chip(text, color=K1, bg=K1BG, fs=30):
    return p(f"font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:1.2;color:{INK};background:{bg};border:3px solid {color};border-radius:999px;padding:6px 22px;white-space:pre", e(text))


def tf(v, size=28):
    c, bg = (GR, GRBG) if v == "True" else (RED, K5BG)
    return p(f"display:inline-block;font-family:{MONO};font-size:{size}px;font-weight:700;color:{c};background:{bg};border-radius:10px;padding:2px 14px;white-space:nowrap", v)


def lockers(pairs, left, top, w=200, h=170, color=K1, bg=K1BG, hi=(), attrs="", fs=34, kfs=24, gap=12, mode=None, ids=None):
    """A dictionary drawn as a row of lockers: the key is written on the door band, the value sits inside.
    mode "key" or "val" dims the other half (for keys() and values())."""
    o = [f'<div{attrs} style="position:absolute;left:{left}px;top:{top}px;display:flex;flex-direction:row;gap:{gap}px">']
    for i, (k, v) in enumerate(pairs):
        on = i in hi or mode is not None
        kc = color if (on and mode != "val") else "#ECEAE3"
        kt = "#FFFFFF" if (on and mode != "val") else (GRAY if mode == "val" else INK)
        vt = "#B4B9C3" if mode == "key" else INK
        sid = f' id="{ids[i]}"' if ids else ""
        o.append(f'<div{sid} style="width:{w}px;height:{h}px;flex:none;border-radius:14px;border:3px solid {color if on else "#C9CED8"};background:{bg if (on and mode != "key") else CARD};display:flex;flex-direction:column;overflow:hidden">'
                 + p(f"height:{kfs + 26}px;flex:none;background:{kc};color:{kt};font-family:{MONO};font-size:{kfs}px;font-weight:700;line-height:{kfs + 26}px;text-align:center;white-space:pre", e(k))
                 + '<div style="flex:1;display:flex;align-items:center;justify-content:center">'
                 + p(f"font-family:{MONO};font-size:{fs}px;font-weight:700;color:{vt};white-space:pre", e(v)) + '</div></div>')
    o.append('</div>')
    return "".join(o)


def fix(left, top, bad, good, order, size=32, w=1728, alt=None):
    """The wrong line struck through, an arrow, the right line. alt: a second right line in gray after it."""
    return (f'<div{at("rise", order)} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;display:flex;flex-direction:row;align-items:center;gap:22px">'
            + p(f"font-size:{size}px;font-weight:900;color:{RED}", "✕")
            + p(f"font-family:{MONO};font-size:{size}px;font-weight:700;color:{RED};text-decoration:line-through;text-decoration-thickness:3px;white-space:pre", e(bad))
            + arrow(70)
            + p(f"font-size:{size}px;font-weight:900;color:{GR}", "✓")
            + p(f"font-family:{MONO};font-size:{size}px;font-weight:700;color:{INK};background:{GRBG};border:3px solid {GR};border-radius:14px;padding:6px 20px;white-space:pre", e(good))
            + (p(f"font-size:{size - 4}px;font-weight:700;color:{GRAY};white-space:nowrap", "또는") + p(f"font-family:{MONO};font-size:{size}px;font-weight:700;color:{INK};background:{GRBG};border:3px solid {GR};border-radius:14px;padding:6px 20px;white-space:pre", e(alt)) if alt else "")
            + '</div>')


def plain_rows(left, top, w, rows, widths, order0=1, rh=84, head_=None, fs=30, hi=(), mono_cols=(), colors=None):
    """A light table: header in gray over a dark rule, rows split by thin rules, no boxes.
    rows: lists of cells; a cell "True"/"False" becomes a chip. hi: rows tinted orange."""
    o = []
    y = top
    if head_:
        o.append(f'<div style="position:absolute;left:{left}px;top:{y}px;width:{w}px;height:52px;display:flex;flex-direction:row;align-items:center;gap:24px;border-bottom:3px solid {INK}">'
                 + "".join(p(f"width:{cw}px;flex:none;font-size:24px;font-weight:700;color:{GRAY}", e(c)) for c, cw in zip(head_, widths)) + '</div>')
        y += 60
    for i, r in enumerate(rows):
        cells_ = ""
        for k, (c, cw) in enumerate(zip(r, widths)):
            if c in ("True", "False"):
                cells_ += f'<div style="width:{cw}px;flex:none">{tf(c)}</div>'
                continue
            mono = k in mono_cols
            col = (colors[k] if colors and colors[k] else (INK if mono or k == 0 else SUB))
            cells_ += p(f"width:{cw}px;flex:none;font-family:{MONO if mono else SANS};font-size:{fs}px;font-weight:{700 if mono or k == 0 else 500};color:{col};white-space:pre", e(c))
        bg = "background:rgba(178,106,0,0.10);" if i in hi else ""
        o.append(f'<div{at("rise", order0 + i if order0 else 0)} id="row{top}-{i}" style="position:absolute;left:{left}px;top:{y + i * rh}px;width:{w}px;height:{rh}px;{bg}display:flex;flex-direction:row;align-items:center;gap:24px;padding:0 12px;border-bottom:2px solid {LINE}">{cells_}</div>')
    return o


def pipe(left, top, items, fn, outs, color, bg, order=1, w=200, fs=30, ids=None):
    """key drawn as a pipe: input boxes on top, a function band in the middle, results below."""
    n = len(items)
    width = n * (w + 16) - 16
    o = []
    for i, it in enumerate(items):
        o.append(vbox(ids[i] if ids else None, it, left + i * (w + 16), top, w, 90, GRAY, FAINT, at("fade", order), fs))
    o.append(f'<div{at("fade", order + 1)} style="position:absolute;left:{left}px;top:{top + 130}px;width:{width}px;height:90px;border-radius:18px;background:{color};display:flex;align-items:center;justify-content:center">'
             + p(f"font-family:{MONO};font-size:{fs + 2}px;font-weight:700;color:#FFFFFF;white-space:pre", e(fn)) + '</div>')
    for i, v in enumerate(outs):
        x = left + i * (w + 16)
        o.append(harrow(x + w // 2 - 18, top + 96, 36, "#C9CED8", at("fade", order + 1), 90))
        o.append(harrow(x + w // 2 - 18, top + 226, 36, color, at("fade", order + 2), 90))
        o.append(vbox(None, v, x, top + 262, w, 90, color, bg, at("rise", order + 2), fs))
    return o


EB1 = "1. 왜 필요한가"
EB2 = "2. sorted, sort, key"
EB3 = "3. 튜플과 딕셔너리 정렬"
EB4 = "4. max와 min"
EB5 = "5. 오류와 함정"
EB6 = "6. 실습"
SALES = 'sales = {"coffee": 12, "latte": 30, "cake": 8, "tea": 15}'
SALES_P = [("coffee", "12"), ("latte", "30"), ("cake", "8"), ("tea", "15")]


# ---------- cover ----------
def cover(lines, h1, sub, note, accent="#F2B27A", h1size=76):
    cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
           f'<p style="font-size:28px;font-weight:700;color:{accent};letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
           f'<h1 style="font-size:{h1size}px;font-weight:900;line-height:1.1;color:#F6F5F1">{h1}</h1>',
           f'<p style="font-size:40px;line-height:1.4;color:#BFC6D4">{sub}</p>',
           '<div style="position:absolute;left:900px;top:280px;width:1020px;height:520px;background:#252B36;border-radius:24px 0 0 24px;padding:44px 56px;display:flex;flex-direction:column;justify-content:center;gap:16px">']
    for line, c in lines:
        cov.append(p(f"font-family:{MONO};font-size:32px;font-weight:700;line-height:1.45;color:{c};white-space:pre", e(line) if line else "&#160;"))
    cov.append('</div>')
    W("cover", cov, note, ("intro", "들어가기"))
    ORDER.append("toc")


cover([('sales = {"coffee": 12, "latte": 30,', "#E6E9EF"), ('         "cake": 8, "tea": 15}', "#E6E9EF"), ("", "#E6E9EF"),
       ("sorted(sales, key=sales.get, reverse=True)", "#8FD8DE"), ("# ['latte', 'tea', 'coffee', 'cake']", "#9AA1AE"), ("", "#E6E9EF"),
       ("max(sales, key=sales.get)", "#E3B877"), ("# 'latte'", "#9AA1AE")],
      "정렬과<br>sorted, max, min", "무엇을 기준으로 줄 세우고<br>가장 큰 값을 고를지 key로 정하기",
      "이번 챕터는 key로 줄 세우는 기준을 직접 정해요. 13에서 sorted와 sort, max와 min을 써 봤어요. 그때는 숫자는 작은 순, 글자는 abc 순으로만 줄 세웠어요. 이번에는 길이순, 가격순, 판매량 많은 순처럼 기준을 바꿔요. 21에서 배운 lambda를 key에 넣는 게 이번 챕터의 중심이에요. 튜플 리스트와 딕셔너리도 원하는 기준으로 줄 세워요.")

# ---------- ready ----------
o = [sec("ready")] + head("들어가기", "21에서 이어서 해요", JP)
for i, (a_, b_) in enumerate([("리스트, 튜플, sort, sorted, max, min", "13"), ("딕셔너리 get, items()", "15"), ("sorted(..., reverse=True)", "16, 20"), ("for, enumerate()", "13, 18"), ("lambda, map, filter", "21")]):
    o.append(f'<div{at("rise", min(i + 1, 4))} style="position:absolute;left:96px;top:{230 + i * 120}px;width:820px;height:104px;display:flex;flex-direction:row;gap:24px;align-items:center;border-bottom:2px solid {LINE}">'
             + f'<x-icon name="CheckCircle" style="width:48px;height:48px;color:{GR}"></x-icon>'
             + p(f"flex:1;font-size:32px;font-weight:700;color:{INK}", e(a_))
             + p(f"font-size:30px;font-weight:700;color:{GRAY};white-space:nowrap", e(b_)) + '</div>')
o.append(p(f"position:absolute;left:1020px;top:256px;font-size:36px;font-weight:700;color:{JP}", "노트북 다시 열기", at("rise", 5)))
steps_ = [p(f"font-size:32px;color:{INK}", "VS Code로 hello-uv 폴더 열기"),
          p(f"font-size:32px;color:{INK}", "탐색기에서") + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{JP}", NB) + p(f"font-size:32px;color:{INK}", "열기"),
          p(f"font-size:32px;color:{INK}", "오른쪽 위 커널이 .venv인지 보기"),
          p(f"font-size:32px;color:{INK}", "셀에 적고") + kbd("Shift+Enter", 26) + p(f"font-size:32px;color:{INK}", "로 실행")]
for i, inner in enumerate(steps_):
    o.append(row(1020, 352 + i * 120, 804, 104, num(i + 1, JP, 40) + inner, 5))
o.append(caption("기억이 안 나면 왼쪽에 적힌 챕터를 먼저 다시 봐요.", 900, 6))
W("ready", o, "hello-uv의 basics.ipynb를 다시 열고, 13, 15, 16, 20, 21에서 배운 것을 이어서 써요. 09에서 만든 hello-uv 폴더를 VS Code로 열어요. 13의 sorted, sort, max, min과 튜플, 15의 get과 items, 16과 20의 reverse=True를 다시 써요. 21의 lambda를 key에 넣는 게 이번 챕터의 중심이라 21을 먼저 보고 오면 좋아요. 슬라이드의 출력은 tools/demo.sh가 hello-uv 커널에서 같은 셀을 실제로 실행한 결과예요. 셀 번호는 파트마다 [1]부터 다시 셌어요.")

# ---------- part 1 ----------
o = [sec("s-why")] + head(EB1, "가장 많이 팔린 메뉴를 물었는데 tea가 나와요", K1)
T, FW = 220, 1180
TX = 96 + FW + 30
o += cell({"lines": [SALES, "print(sorted(sales))", "print(max(sales))"], "n": 1, "out": ["['cake', 'coffee', 'latte', 'tea']", "tea"]}, 96, T, FW)
o.append(hl(96, T, FW, 2, 1, "err", 1))
o.append(out_ring(1, 96, T, 3, 1, "tea"))
o.append(tag(TX, ly(T, 2), "기대한 건 latte", RED, 1))
o.append(tag(TX, oy(T, 3, 0), "키만 abc 순으로 줄 섰어요", K1, 2))
o.append(tag(TX, oy(T, 3, 1), "abc 순으로 가장 뒤라서 가장 커요", K1, 2))
LT = 620
o.append(lockers(SALES_P, 96, LT, 280, 200, K1, K1BG, hi=(1,), fs=44, kfs=28, gap=16, attrs=at("rise", 3)))
o.append(tag(96 + 4 * 296 + 20, LT + 120, "판매량은 latte가 30잔으로 가장 많아요", K1, 3))
o.append(caption("이름 말고 판매량으로 비교하라고 알려 주는 방법이 key예요.", 960, 4))
W("s-why", o, "max(sales)는 판매량이 아니라 이름끼리 비교해서 tea를 돌려줘요. 메뉴별 판매량을 딕셔너리에 담고 가장 많이 팔린 메뉴를 물었어요. 판매량은 latte가 30잔으로 가장 많은데 tea가 나와요. sorted와 max는 딕셔너리를 받으면 키만 봐요. 키가 글자라서 abc 순으로 비교했고, tea가 가장 뒤라서 가장 큰 값이 됐어요. 이름이 아니라 판매량으로 비교하라고 알려 줘야 해요. 그 방법이 key예요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p1", "왜 필요한가"))

# s-big: names -> key=len -> values to compare -> names in line. The result boxes fly from the names.
o = [sec("s-big")] + head(EB1, "key는 비교할 값을 따로 만들어 줘요", K1)
X0, BW, GAP = 420, 300, 50
cols = [X0 + i * (BW + GAP) for i in range(3)]
NAMES, LENS = ['"latte"', '"tea"', '"coffee"'], ["5", "3", "6"]
RA, RB, RC = 226, 520, 760
o.append(lbl(96, RA + 34, "원래 값", GRAY, None, 30))
for i, (x, n_) in enumerate(zip(cols, NAMES)):
    o.append(vbox(f"bn{i}", n_, x, RA, BW, 110, GRAY, FAINT, fs=36))
BAND_W = 3 * BW + 2 * GAP
o.append(f'<div{at("fade", 1)} style="position:absolute;left:{X0}px;top:{RA + 150}px;width:{BAND_W}px;height:84px;border-radius:18px;background:{K1};display:flex;align-items:center;justify-content:center">'
         + p(f"font-family:{MONO};font-size:36px;font-weight:700;color:#FFFFFF", "key=len") + '</div>')
for i, x in enumerate(cols):
    o.append(harrow(x + BW // 2 - 18, RA + 114, 36, "#C9CED8", at("fade", 1), 90))
    o.append(harrow(x + BW // 2 - 18, RA + 238, 36, K1, at("fade", 2), 90))
o.append(lbl(96, RB + 30, "비교할 값", K1, 2, 30))
for i, (x, v) in enumerate(zip(cols, LENS)):
    o.append(vbox(f"bl{i}", v, x, RB, BW, 100, K1, K1BG, at("rise", 2), 40))
o.append(tag(X0 + BAND_W + 40, RB + 50, "이 값으로 비교해요", K1, 2))
o.append(lbl(X0, RB + 112, "작은 것부터 줄 서요", GRAY, 3, 26))
o.append(lbl(96, RC + 40, "결과", GR, 3, 30))
for slot, src in enumerate([1, 0, 2]):          # 3, 5, 6 -> tea, latte, coffee
    o.append(vbox(None, NAMES[src], cols[slot], RC, BW, 130, GR, GRBG, f' data-build-in="fly order 3" data-from="bn{src}"', 36, sub=LENS[src]))
o.append(tag(X0 + BAND_W + 40, RC + 65, "줄 서는 건 원래 값이에요", GR, 4))
W("s-big", o, "key에 넣은 함수가 값마다 비교할 값을 만들고, 줄은 그 값으로 서요. 이름 세 개를 길이순으로 세우고 싶어요. key=len을 주면 sorted가 값마다 len을 써서 비교할 값 5, 3, 6을 만들어요. 21의 map이 값을 하나씩 함수에 넣던 것과 같아요. 그다음 비교할 값이 작은 것부터 줄을 세워요. 결과에는 숫자가 아니라 원래 이름이 들어가요. tea, latte, coffee 순이에요. max와 min도 key를 받아서 같은 방식으로 비교해요.")

o = [sec("s-min")] + head(EB1, "가장 짧은 key: 이름을 길이순으로", K1)
T, FW = 220, 1180
TX = 96 + FW + 30
MIN = ['names = ["latte", "tea", "coffee"]', "print(sorted(names))", "print(sorted(names, key=len))", "print(max(sales, key=sales.get))"]
o += cell({"lines": MIN, "n": 2, "out": ["['coffee', 'latte', 'tea']", "['tea', 'latte', 'coffee']", "latte"]}, 96, T, FW)
o.append(code_line(1, 96, T, 2, "print(sorted(names, ", "key=len", K1))
o.append(tag(TX, ly(T, 2), "길이로 비교", K1, 1))
o.append(tag(TX, oy(T, 4, 1), "길이 3, 5, 6 순", K1, 1))
o.append(code_line(2, 96, T, 3, "print(max(sales, ", "key=sales.get", GR))
o.append(tag(TX, ly(T, 3), "판매량으로 비교", GR, 2))
o.append(tag(TX, oy(T, 4, 2), "앞 장의 tea가 latte로", GR, 2))
o += plain_rows(96, 720, 1728, [["21", "map(len, names)", "len을 괄호 없이 넘겼어요"], ["22", "sorted(names, key=len)", "key에도 괄호 없이 넘겨요"]], [100, 640, 860], 3, 84, None, 32, mono_cols=(1,))
W("s-min", o, "key= 뒤에 함수 이름을 넣으면 무엇으로 비교할지 바뀌어요. 그냥 sorted는 abc 순이라 coffee가 먼저예요. key=len을 주면 길이 3인 tea, 5인 latte, 6인 coffee 순이 돼요. 마지막 줄은 앞 장의 문제를 푼 거예요. key=sales.get을 주면 키마다 sales.get으로 판매량을 꺼내 비교해서 latte를 골라요. key에는 21의 map처럼 괄호 없이 함수 이름만 넣어요. sales.get은 3파트에서 자세히 봐요. sales는 앞 셀에서 만들었어요." + REAL)

# ---------- part 2 ----------
o = [sec("o-two")] + head(EB2, "sorted는 새 리스트, sort는 원본을 바꿔요", K2)
T, FW = 220, 860
o += cell({"lines": ["prices = [6500, 4500, 5000]", "a = sorted(prices)", "print(a)", "print(prices)", "prices.sort()", "print(prices)"], "n": 1, "out": ["[4500, 5000, 6500]", "[6500, 4500, 5000]", "[4500, 5000, 6500]"]}, 96, T, FW)
o.append(hl(96, T, FW, 1, 1, "mark", 1))
o.append(hl(96, T, FW, 4, 1, "run", 2))
PX, SW = 1060, 236
VALS = ["6500", "4500", "5000"]
o.append(lbl(PX, 220, "prices", GRAY, None, 30, mono=True))
for i, v in enumerate(VALS):
    o.append(vbox(f"pv{i}", v, PX + i * (SW + 12), 270, SW, 96, GRAY, FAINT, fs=34))
o.append(lbl(PX, 430, "a = sorted(prices)", K2, 1, 30, mono=True))
for slot, src in enumerate([1, 2, 0]):
    o.append(vbox(None, VALS[src], PX + slot * (SW + 12), 480, SW, 96, K2, K2BG, f' data-build-in="fly order 1" data-from="pv{src}"', 34))
o.append(lbl(PX, 590, "새 리스트예요. prices는 그대로예요", K2, 1, 28))
o.append(lbl(PX, 690, "prices.sort() 다음의 prices", GR, 2, 30, mono=True))
for slot, src in enumerate([1, 2, 0]):
    o.append(vbox(None, VALS[src], PX + slot * (SW + 12), 740, SW, 96, GR, GRBG, f' data-build-in="fly order 2" data-from="pv{src}"', 34))
o.append(lbl(PX, 850, "prices 자체가 바뀌었어요", GR, 2, 28))
o.append(caption("원본을 지키려면 sorted, 원본을 바꿔도 되면 sort를 써요.", 960, 3))
W("o-two", o, "sorted는 줄 세운 새 리스트를 주고, sort는 원래 리스트를 바꿔요. 13에서 본 두 가지를 다시 짚어요. sorted(prices)는 함수예요. 줄 세운 새 리스트를 돌려주고 prices는 그대로 둬요. 그래서 a는 줄 섰지만 prices를 찍으면 원래 순서예요. prices.sort()는 리스트의 메서드예요. prices 자체를 줄 세워요. 다음 장에서 보겠지만 sort는 돌려주는 값이 없어요. 원래 순서가 나중에도 필요하면 sorted, 필요 없으면 sort를 써요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p2", "sorted, sort, key"))

o = [sec("o-none")] + head(EB2, "prices = prices.sort()를 하면 None만 남아요", K2)
T, FW = 220, 1000
TX = 96 + FW + 30
o += cell({"lines": ["prices = [6500, 4500, 5000]", "prices = prices.sort()", "print(prices)"], "n": 2, "out": ["None"]}, 96, T, FW)
o.append(hl(96, T, FW, 1, 1, "err", 1))
o.append(tag(TX, ly(T, 1), "sort가 돌려준 값을 prices에 넣었어요", RED, 1))
o.append(out_ring(2, 96, T, 3, 0, "None"))
o.append(tag(TX, oy(T, 3, 0), "줄 세운 리스트를 잃었어요", RED, 2))
o += plain_rows(96, 470, 1300, [["1", "prices.sort()", "prices를 줄 세워요"], ["2", "돌려준 값", "None"], ["3", "prices = None", "prices에 None이 들어가요"]], [80, 520, 600], 3, 80, None, 30, mono_cols=(1,), colors=(K5, None, None))
o.append(fix(96, 790, "prices = prices.sort()", "prices.sort()", 6, 32, alt="prices = sorted(prices)"))
W("o-none", o, "sort는 돌려주는 값이 없어서, 그 결과를 다시 담으면 None만 남아요. 자주 하는 실수예요. 줄 세운 결과를 다시 prices에 담으려고 prices = prices.sort()라고 적었어요. 찍어 보면 None이에요. sort는 prices를 줄 세우기만 하고 돌려주는 값이 없어요. 19에서 return이 없는 함수가 None을 돌려준 것과 같아요. 그 None을 prices에 넣어서 줄 세운 리스트를 잃었어요. sort는 prices.sort()처럼 한 줄로만 쓰고, 결과를 변수에 담고 싶으면 sorted를 써요." + REAL)

o = [sec("o-rev")] + head(EB2, "큰 것부터 세우려면 reverse=True", K2)
T, FW = 220, 1180
TX = 96 + FW + 30
o += cell({"lines": ["prices = [6500, 4500, 5000]", "print(sorted(prices, reverse=True))", "prices.sort(reverse=True)", "print(prices)"], "n": 3, "out": ["[6500, 5000, 4500]", "[6500, 5000, 4500]"]}, 96, T, FW)
o.append(code_line(1, 96, T, 1, "print(sorted(prices, ", "reverse=True", K2))
o.append(tag(TX, ly(T, 1), "20의 키워드 인자", K2, 1))
o.append(code_line(2, 96, T, 2, "prices.sort(", "reverse=True", GR))
o.append(tag(TX, ly(T, 2), "sort도 똑같이 받아요", GR, 2))
RX, RW = 420, 220
o.append(lbl(96, 640, "기본", GRAY, 3, 30))
for i, v in enumerate(["4500", "5000", "6500"]):
    o.append(vbox(f"rv{i}", v, RX + i * (RW + 16), 620, RW, 96, GRAY, FAINT, at("rise", 3), 34))
o.append(lbl(96, 800, "reverse=True", K2, 4, 30, mono=True))
for slot, src in enumerate([2, 1, 0]):
    o.append(vbox(None, ["4500", "5000", "6500"][src], RX + slot * (RW + 16), 780, RW, 96, K2, K2BG, f' data-build-in="fly order 4" data-from="rv{src}"', 34))
o.append(tag(RX + 3 * (RW + 16) + 24, 828, "큰 것부터, 글자라면 z부터", K2, 4))
W("o-rev", o, "reverse=True를 넣으면 큰 것부터 세워요. 16과 20에서 본 reverse=True예요. 기본값이 False라서 빼면 작은 것부터 세우고, True를 넣으면 거꾸로 큰 것부터 세워요. 글자라면 z 쪽부터예요. 20에서 배운 대로 칸 이름을 붙여 넣는 키워드 인자예요. sort도 같은 키워드 인자를 받아서 prices.sort(reverse=True)로 원본을 큰 것부터 세워요. 뒤에 나올 key도 sorted와 sort 둘 다 받아요." + REAL)

o = [sec("o-what")] + head(EB2, "글자는 앞 글자부터 하나씩 비교해요", K2)
T, FW = 220, 1180
TX = 96 + FW + 30
WHAT = ['print(sorted(["Latte", "cake", "Tea", "coffee"]))', 'print(sorted(["라떼", "커피", "녹차"]))', 'print(sorted(["10", "9", "100"]))']
o += cell({"lines": WHAT, "n": 4, "out": ["['Latte', 'Tea', 'cake', 'coffee']", "['녹차', '라떼', '커피']", "['10', '100', '9']"]}, 96, T, FW)
o.append(out_ring(3, 96, T, 3, 2, "['10', '100', '9']"))
o.append(tag(TX, oy(T, 3, 2), "크기순이 아니에요", RED, 3))
o += plain_rows(96, 640, 1728, [['"Tea" < "cake"', "True", "대문자 A~Z 뒤에 소문자 a~z가 와요"], ['"녹차" < "라떼"', "True", "한글은 가나다 순이에요"], ['"100" < "9"', "True", "첫 글자 1과 9를 먼저 비교해요"]],
                [420, 160, 1000], 1, 90, None, 32, mono_cols=(0,))
W("o-what", o, "글자는 사전처럼 첫 글자부터 하나씩 비교해요. 첫째 줄에서 Latte와 Tea가 cake보다 앞에 왔어요. 파이썬은 대문자를 소문자보다 앞에 둬요. 한글은 가나다 순이에요. 셋째 줄은 숫자를 글자로 담았어요. 첫 글자 1과 9를 비교해서 10과 100이 9보다 앞에 와요. 이렇게 크기순이 아닌 결과는 다음 두 장의 key로 고쳐요." + REAL)

o = [sec("k-len")] + head(EB2, "key=len: 길이를 재서 비교해요", K2)
T, FW = 220, 1180
TX = 96 + FW + 30
KL = ['names = ["latte", "tea", "coffee", "mocha"]', "print(list(map(len, names)))", "print(sorted(names, key=len))", "print(sorted(names, key=len, reverse=True))"]
o += cell({"lines": KL, "n": 5, "out": ["[5, 3, 6, 5]", "['tea', 'latte', 'mocha', 'coffee']", "['coffee', 'latte', 'mocha', 'tea']"]}, 96, T, FW)
o.append(tag(TX, oy(T, 4, 0), "21의 map(len, …)과 같은 값", K2, 1))
NX, NW, NG = 300, 220, 40
KN = ['"latte"', '"tea"', '"coffee"', '"mocha"']
o.append(lbl(96, 676, "names", GRAY, 1, 30, mono=True))
for i, v in enumerate(KN):
    o.append(vbox(f"kn{i}", v, NX + i * (NW + NG), 660, NW, 84, GRAY, FAINT, at("rise", 1), 30))
o.append(lbl(96, 808, "len", K2, 2, 30, mono=True))
for i, v in enumerate(["5", "3", "6", "5"]):
    o.append(vbox(None, v, NX + i * (NW + NG), 792, NW, 84, K2, K2BG, f' data-build-in="fly order 2" data-from="kn{i}"', 34))
o.append(box(3, NX - 12, 648, NW + 24, 240, OR))
o.append(box(3, NX + 3 * (NW + NG) - 12, 648, NW + 24, 240, OR))
o.append(tag(NX + 4 * (NW + NG) + 20, 768, "길이가 같으면 처음 적은 순서", OR, 3))
W("k-len", o, "key=len은 길이로 비교하고, 길이가 같으면 처음 적은 순서를 지켜요. 21에서 map(len, names)로 뽑은 길이 5, 3, 6, 5가 sorted가 안에서 쓰는 비교 값이에요. 작은 것부터 세우면 tea, latte와 mocha, coffee 순이에요. latte와 mocha는 길이가 같아요. 이럴 땐 처음 적은 순서를 그대로 지켜서 latte가 먼저 와요. reverse=True를 같이 주면 긴 이름부터 세워요. 길이가 같은 둘의 순서는 그대로예요." + REAL)

o = [sec("k-lower")] + head(EB2, "key=str.lower, key=int로 비교 방법을 바꿔요", K2)
T, FW = 220, 1728
KW = ['print("Latte".lower())', 'print(sorted(["Latte", "cake", "Tea", "coffee"], key=str.lower))', 'print(sorted(["10", "9", "100"], key=int))']
o += cell({"lines": KW, "n": 6, "out": ["latte", "['cake', 'coffee', 'Latte', 'Tea']", "['9', '10', '100']"]}, 96, T, FW)
o.append(code_line(1, 96, T, 0, 'print("Latte"', ".lower()", K2))
o.append(code_line(2, 96, T, 1, 'print(sorted(["Latte", "cake", "Tea", "coffee"], ', "key=str.lower", K2))
o.append(code_line(3, 96, T, 2, 'print(sorted(["10", "9", "100"], ', "key=int", GR))
o += plain_rows(96, 640, 1728, [['"Latte".lower()', "글자를 모두 소문자로 바꾼 새 글자를 줘요"], ["key=str.lower", "소문자로 바꿔서 비교해요. 결과는 원래 글자예요"], ["key=int", "숫자로 바꿔서 크기순으로 비교해요"]],
                [440, 1180], 1, 90, None, 32, mono_cols=(0,), colors=(K2, None))
W("k-lower", o, "비교할 때만 값을 바꾸고 싶으면 key에 바꾸는 함수를 넣어요. 앞 장에서 이상했던 두 결과를 key로 고쳐요. lower는 이번에 처음 보는 글자 메서드예요. 글자를 모두 소문자로 바꾼 새 글자를 줘요. key=str.lower를 주면 소문자로 바꾼 값끼리 비교해서 대소문자 상관없이 abc 순이 돼요. 결과에는 Latte, Tea처럼 원래 글자가 그대로 들어가요. 글자로 담긴 숫자는 12에서 배운 int를 key로 주면 숫자 크기순이 돼요. str.lower는 글자 메서드 lower를 함수로 넘기는 이름이에요. 괄호는 붙이지 않아요." + REAL)

# ---------- part 3 ----------
o = [sec("p-tuple")] + head(EB3, "튜플은 앞 칸부터 비교해요", K3)
T, FW = 220, 1728
o += cell({"lines": ['items = [("latte", 5000), ("cake", 6500), ("coffee", 4500), ("cake", 6000)]', "print(sorted(items))"], "n": 1, "out": ["[('cake', 6000), ('cake', 6500), ('coffee', 4500), ('latte', 5000)]"]}, 96, T, FW)
o.append(row(96, 470, 1180, 110, tup(['"cake"', "6000"], hi=(1,), w=210, h=90) + small("<", K3, 40) + tup(['"cake"', "6500"], hi=(1,), w=210, h=90), 1))
o.append(tag(1300, 525, "첫 칸이 같아서 둘째 칸으로", K3, 1))
o.append(row(96, 660, 1180, 110, tup(['"coffee"', "4500"], hi=(0,), w=210, h=90) + small("<", K3, 40) + tup(['"latte"', "5000"], hi=(0,), w=210, h=90), 2))
o.append(tag(1300, 715, "첫 칸이 다르면 거기서 끝", K3, 2))
o.append(caption("글자를 첫 글자부터 비교하듯, 튜플은 첫 칸부터 비교해요.", 900, 3))
W("p-tuple", o, "튜플 리스트를 그냥 줄 세우면 첫 칸 기준, 같으면 둘째 칸 기준이에요. 13에서 배운 튜플로 메뉴와 가격을 묶었어요. 그냥 sorted하면 첫 칸인 이름 순으로 서요. cake가 둘이라 첫 칸이 같아요. 그럴 때는 둘째 칸 6000과 6500을 비교해서 6000짜리가 먼저예요. coffee와 latte는 첫 칸이 달라서 둘째 칸은 보지 않아요. 앞 파트에서 글자를 첫 글자부터 비교한 것과 같은 방식이에요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p3", "튜플과 딕셔너리 정렬"))

o = [sec("p-index")] + head(EB3, "key=lambda m: m[1]로 둘째 칸 기준", K3)
T, FW = 220, 1180
TX = 96 + FW + 30
PI = ['items = [("latte", 5000), ("cake", 6500), ("coffee", 4500)]', "print(sorted(items, key=lambda m: m[1]))", "print(sorted(items, key=lambda m: m[1], reverse=True))"]
o += cell({"lines": PI, "n": 2, "out": ["[('coffee', 4500), ('latte', 5000), ('cake', 6500)]", "[('cake', 6500), ('latte', 5000), ('coffee', 4500)]"]}, 96, T, FW)
o.append(code_line(1, 96, T, 1, "print(sorted(items, key=lambda m: ", "m[1]", K3))
o.append(tag(TX, ly(T, 1), "m에 튜플이 하나씩", K3, 1))
for i, (n_, v) in enumerate([('"latte"', "5000"), ('"cake"', "6500"), ('"coffee"', "4500")]):
    o.append(row(96, 600 + i * 110, 1100, 96, small("m =", GRAY, 30, 90, True) + tup([n_, v], hi=(1,), dim=(0,), w=200) + arrow(60, K3) + small("m[1]", K3, 30, 100, True) + chip(v, K3, K3BG, 32), 2))
o.append(tag(1180, 710, "가격으로 비교하고, 결과는 튜플 그대로", K3, 3))
W("p-index", o, "원하는 칸으로 세우려면 그 칸을 꺼내는 lambda를 key에 넣어요. 가격순으로 세우고 싶은데 이미 있는 함수가 없어서 21의 lambda로 만들어요. key=lambda m: m[1]은 튜플 하나를 m으로 받아 둘째 칸, 곧 가격을 돌려줘요. sorted는 이 가격으로 비교해서 4500, 5000, 6500 순으로 세워요. 결과에는 튜플이 그대로 들어가요. reverse=True를 같이 주면 비싼 것부터예요. 이름은 m[0]이라 key=lambda m: m[0]이면 그냥 sorted와 같아요." + REAL)

o = [sec("p-multi")] + head(EB3, "판매량 많은 순, 같으면 이름순으로 세워요", K3)
T, FW = 210, 1728
MUL = ['sales = [("latte", 30), ("cake", 8), ("coffee", 30), ("tea", 15)]', "print(sorted(sales, key=lambda m: m[1], reverse=True))", "print(list(map(lambda m: (-m[1], m[0]), sales)))", "print(sorted(sales, key=lambda m: (-m[1], m[0])))"]
MO = ["[('latte', 30), ('coffee', 30), ('tea', 15), ('cake', 8)]", "[(-30, 'latte'), (-8, 'cake'), (-30, 'coffee'), (-15, 'tea')]", "[('coffee', 30), ('latte', 30), ('tea', 15), ('cake', 8)]"]
o += cell({"lines": MUL, "n": 3, "out": MO}, 96, T, FW)
OTX = 1440
o.append(hl(96, T, FW, 1, 1, "skip", 1))
o.append(tag(OTX, oy(T, 4, 0), "30끼리는 원래 순서", GRAY, 1))
o.append(hl(96, T, FW, 3, 1, "run", 2))
o.append(tag(OTX, oy(T, 4, 2), "같으면 이름순", GR, 2))
o += plain_rows(96, 640, 1728, [['("coffee", 30)', "(-30, 'coffee')", "-30이 가장 작고, 이름도 c가 먼저"], ['("latte", 30)', "(-30, 'latte')", "-30이 같아서 이름으로 비교해요"], ['("tea", 15)', "(-15, 'tea')", "다음은 -15"], ['("cake", 8)', "(-8, 'cake')", "-8이 가장 커서 맨 뒤"]],
                [380, 380, 880], 3, 68, ["튜플", "key 결과", "읽는 법"], 28, hi=(0, 1), mono_cols=(0, 1))
W("p-multi", o, "key가 (-판매량, 이름) 튜플을 돌려주면 많은 순으로 세우고, 같으면 이름순으로 세워요. reverse=True로 많은 순을 세우면 30잔인 latte와 coffee는 원래 순서대로 남아요. key가 튜플을 돌려주면 앞 장처럼 첫 칸부터 비교해요. 첫 칸에 -m[1], 둘째 칸에 m[0]을 넣었어요. 판매량에 -를 붙이면 30이 -30이 돼서 작은 것부터 세워도 많이 팔린 메뉴가 앞에 와요. 첫 칸이 -30으로 같으면 둘째 칸 이름으로 비교해서 coffee가 먼저예요. reverse는 쓰지 않았어요." + REAL)

o = [sec("p-dict")] + head(EB3, "딕셔너리는 키, 값, 짝 중 무엇을 줄 세울지 골라요", K3)
T, FW = 210, 1728
o += cell({"lines": [SALES, "print(sorted(sales))", "print(sorted(sales.values()))", "print(sorted(sales.items()))"], "n": 4, "out": ["['cake', 'coffee', 'latte', 'tea']", "[8, 12, 15, 30]", "[('cake', 8), ('coffee', 12), ('latte', 30), ('tea', 15)]"]}, 96, T, FW)
GW = 552
for g, (code, mode, said) in enumerate([("sorted(sales)", "key", "키만, 이름이 abc 순으로"), ("sorted(sales.values())", "val", "값만, 메뉴 이름은 빠져요"), ("sorted(sales.items())", None, "(키, 값) 튜플, 첫 칸 이름순")]):
    x = 96 + g * (GW + 36)
    o.append(lbl(x, 640, code, K3, g + 1, 28, mono=True))
    o.append(lockers(SALES_P, x, 690, 126, 150, K3, K3BG, hi=(0, 1, 2, 3) if mode is None else (), fs=32, kfs=22, gap=16, mode=mode, attrs=at("rise", g + 1)))
    o.append(lbl(x, 860, said, SUB if mode else K3, g + 1, 26))
W("p-dict", o, "딕셔너리는 sorted에 무엇을 넘기느냐에 따라 키, 값, 짝 중 하나가 줄 서요. 15의 판매량 딕셔너리로 돌아와요. 딕셔너리를 그대로 넘기면 키만 줄 세워요. values()를 넘기면 판매량만 줄 세우는데 어느 메뉴인지가 빠져요. items()를 넘기면 키와 값을 묶은 튜플 리스트가 돼요. 앞 장의 튜플 규칙대로 첫 칸인 이름 순이에요. 이름과 판매량을 같이 두고 판매량으로 세우려면 다음 장처럼 items()에 key를 줘요." + REAL)

o = [sec("p-items")] + head(EB3, "items()에 key=lambda kv: kv[1]로 판매 순위", K3)
T, FW = 210, 1360
TX = 96 + FW + 40
PIT = ["rank = sorted(sales.items(), key=lambda kv: kv[1], reverse=True)", "print(rank)", "for name, n in rank:", '    print(f"{name:<7}{n:>3}잔")']
PIO = ["[('latte', 30), ('tea', 15), ('coffee', 12), ('cake', 8)]", "latte   30잔", "tea     15잔", "coffee  12잔", "cake     8잔"]
o += cell({"lines": PIT, "n": 5, "out": PIO}, 96, T, FW)
o.append(code_line(1, 96, T, 0, "rank = sorted(sales.items(), key=lambda kv: ", "kv[1]", K3))
o.append(tag(TX, ly(T, 0), "판매량으로 비교", K3, 1))
o.append(f'<div{at("rise", 1)} style="position:absolute;left:820px;top:520px;display:flex;flex-direction:column;align-items:flex-start;gap:12px">'
         + '<div style="display:flex;flex-direction:row;align-items:center;gap:16px">' + small("kv =", GRAY, 30, None, True) + tup(['"latte"', "30"], hi=(1,), w=200, h=90, fs=32) + '</div>'
         + '<div style="display:flex;flex-direction:row;gap:6px;margin-left:118px">' + "".join(p(f"width:200px;text-align:center;font-family:{MONO};font-size:28px;font-weight:700;color:{c}", t) for t, c in (("kv[0]", GRAY), ("kv[1]", K3))) + '</div></div>')
o.append(tag(500, oy(T, 4, 2), "13의 꺼내 담기", GRAY, 2))
o.append(caption("이름과 값을 같이 두고 값으로 세우려면 items()에 key를 줘요.", 960, 3))
W("p-items", o, "이름과 판매량을 같이 두고 판매량으로 세우려면 items()에 key를 줘요. items()가 주는 튜플 하나를 kv로 받아요. key와 value의 첫 글자라서 kv라고 지었어요. kv[1]이 판매량이라 판매량으로 비교하고, reverse=True로 많은 순이에요. 결과는 튜플 리스트라서 for name, n in rank:처럼 13의 꺼내 담기로 두 변수에 나눠 찍어요. 칸 맞추기도 13에서 배운 그대로예요." + REAL)

o = [sec("p-get")] + head(EB3, "키만 필요하면 key=sales.get", K3)
T, FW = 210, 1180
TX = 96 + FW + 30
o += cell({"lines": ['print(sales.get("latte"))', "print(sorted(sales, key=sales.get))", "print(sorted(sales, key=sales.get, reverse=True))"], "n": 6, "out": ["30", "['cake', 'coffee', 'tea', 'latte']", "['latte', 'tea', 'coffee', 'cake']"]}, 96, T, FW)
o.append(tag(TX, oy(T, 3, 0), "15의 get, 키를 넣으면 값", K3, 1))
o += pipe(96, 600, ['"coffee"', '"latte"', '"cake"', '"tea"'], "sales.get", ["12", "30", "8", "15"], K3, K3BG, 2, 230)
o.append(tag(96 + 4 * 246 + 24, 775, "괄호 없이 이름만 넘겨요", K3, 3))
o.append(tag(96 + 4 * 246 + 24, 907, "lambda k: sales[k]와 같아요", GRAY, 4))
W("p-get", o, "결과에 키만 있으면 될 때는 key=sales.get으로 값 순서대로 키를 세워요. 15에서 배운 get은 키를 넣으면 값을 주는 메서드예요. 괄호 없이 sales.get만 key에 넘기면 sorted가 키마다 sales.get을 불러 판매량을 꺼내 비교해요. 결과는 키 리스트예요. 21에서 함수를 괄호 없이 넘긴 것과 같아요. lambda k: sales[k]로 적어도 결과는 같아요. 1파트의 max(sales, key=sales.get)도 이 방식이었어요." + REAL)

# ---------- part 4 ----------
o = [sec("m-basic")] + head(EB4, "max와 min도 key를 받아요", K4)
T, FW = 210, 1000
TX = 96 + FW + 40
o += cell({"lines": ["prices = [4500, 5000, 6500, 3000]", "print(max(prices), min(prices))", 'names = ["latte", "tea", "coffee"]', "print(max(names), min(names))", "print(max(names, key=len))"], "n": 1, "out": ["6500 3000", "tea coffee", "coffee"]}, 96, T, FW)
o.append(tag(TX, oy(T, 5, 1), "글자는 abc 순, sorted와 같은 규칙", K4, 1))
o.append(hl(96, T, FW, 4, 1, "mark", 2))
o.append(tag(TX, oy(T, 5, 2), "길이 6이 아니라 이름 coffee", GR, 2))
SX, SWD = 96, 300
o.append(lbl(96, 700, "sorted(names)", GRAY, 3, 30, mono=True))
for i, v in enumerate(['"coffee"', '"latte"', '"tea"']):
    o.append(vbox(f"ms{i}", v, SX + i * (SWD + 16), 752, SWD, 96, K4 if i in (0, 2) else GRAY, K4BG if i in (0, 2) else FAINT, at("rise", 3), 34))
for lx, lt in ((SX, "min"), (SX + 2 * (SWD + 16), "max")):
    o.append(p(f"position:absolute;left:{lx}px;top:864px;width:{SWD}px;text-align:center;font-family:{MONO};font-size:30px;font-weight:700;color:{K4}", lt, at("fade", 4)))
o.append(tag(SX + 3 * (SWD + 16) + 24, 800, "맨 앞이 min, 맨 뒤가 max", K4, 4))
W("m-basic", o, "max(xs, key=함수)는 함수 결과가 가장 큰 원래 값을 돌려줘요. 13에서 max와 min은 가장 큰 값과 가장 작은 값을 줬어요. 비교 규칙은 sorted와 같아서 글자는 abc 순이에요. tea가 가장 크고 coffee가 가장 작아요. max와 min도 key를 받아요. key=len을 주면 길이로 비교해서 가장 긴 coffee를 돌려줘요. 돌아오는 건 길이 6이 아니라 원래 값이에요. sorted로 줄 세운 맨 뒤가 max, 맨 앞이 min이라고 생각하면 돼요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p4", "max와 min"))

o = [sec("m-dict")] + head(EB4, "가장 많이 팔린 메뉴는 max(sales, key=sales.get)", K4)
T, FW = 210, 1100
TX = 96 + FW + 40
o += cell({"lines": [SALES, "print(max(sales))", "print(max(sales, key=sales.get))", "print(min(sales, key=sales.get))", "print(max(sales.items(), key=lambda kv: kv[1]))"], "n": 2, "out": ["tea", "latte", "cake", "('latte', 30)"]}, 96, T, FW)
o.append(hl(96, T, FW, 1, 1, "skip", 1))
o.append(tag(TX, oy(T, 5, 0), "1파트의 tea", GRAY, 1))
o.append(tag(TX, oy(T, 5, 1), "판매량이 가장 많은 키", K4, 2))
o.append(tag(TX, oy(T, 5, 2), "판매량이 가장 적은 키", K4, 3))
o.append(tag(TX, oy(T, 5, 3), "이름과 판매량을 같이", K3, 4))
o.append(lockers(SALES_P, 96, 760, 250, 160, K4, K4BG, hi=(1,), fs=40, kfs=26, gap=16, attrs=at("rise", 5), ids=["md0", "md1", "md2", "md3"]))
o.append(spot(6, target="md1", pad=14))
W("m-dict", o, "max(sales, key=sales.get)는 판매량으로 비교해서 가장 많이 팔린 메뉴 이름을 돌려줘요. 1파트의 문제를 다시 봐요. max(sales)는 키끼리 비교해서 tea였어요. key=sales.get을 주면 키마다 판매량을 꺼내 비교해서 latte를 돌려줘요. min도 같아서 가장 적게 팔린 cake이 나와요. 이름과 판매량이 같이 필요하면 items()를 넘기고 kv[1]로 비교해요. 결과가 ('latte', 30) 튜플이에요. 이름만 필요하면 get, 둘 다 필요하면 items()를 골라요." + REAL)

o = [sec("m-default")] + head(EB4, "빈 리스트에 max를 쓰면 ValueError가 나요", K4)
T1, T2, FW = 210, 400, 1180
TX = 96 + FW + 30
o += cell({"lines": ["print(max([]))"], "n": 3, "out": ["ValueError: max() iterable argument is empty"], "err": True}, 96, T1, FW)
o.append(out_line(1, 96, T1, 1, 0, "ValueError: max() ", "iterable argument is empty"))
o.append(tag(TX, oy(T1, 1, 0), "고를 값이 하나도 없어요", RED, 1))
o += cell({"lines": ["big = list(filter(lambda p: p > 10000, prices))", "print(big)", "print(max(big, default=0))"], "n": 4, "out": ["[]", "0"]}, 96, T2, FW, attrs=at("rise", 2))
o.append(tag(TX, oy(T2, 3, 0), "1만 원 넘는 메뉴가 없어요", OR, 2))
o.append(hl(96, T2, FW, 2, 1, "run", 3))
o.append(tag(TX, oy(T2, 3, 1), "비어 있으면 0", GR, 3))
o += plain_rows(96, 790, 1728, [["15", 'menu.get("cakee", 5000)', "키가 없을 때 대신 돌려줄 값"], ["22", "max(big, default=0)", "비어 있을 때 대신 돌려줄 값"]], [100, 640, 860], 4, 80, None, 30, mono_cols=(1,))
W("m-default", o, "빈 리스트에 max를 쓰면 ValueError가 나니, 비어 있을 수 있으면 default를 적어요. 오류 메시지는 iterable argument is empty예요. 가장 큰 값을 고르려는데 값이 하나도 없어서예요. 21의 filter로 고른 결과는 이렇게 비어 있을 수 있어요. 1만 원이 넘는 메뉴가 없어서 big이 빈 리스트예요. default=0처럼 적으면 비어 있을 때 오류 대신 0을 돌려줘요. 15의 get에 기본값을 준 것과 비슷해요. min도 똑같이 default를 받아요. Traceback 위쪽 줄은 빼고 마지막 줄만 옮겼어요. prices는 앞 셀에서 만들었어요." + REAL)

o = [sec("m-with")] + head(EB4, "sum, len, 자르기와 같이 써요", K4)
T, FW = 210, 1180
TX = 96 + FW + 30
o += cell({"lines": ["print(sum(sales.values()), len(sales))", "print(sum(sales.values()) / len(sales))", "top3 = sorted(sales, key=sales.get, reverse=True)[:3]", "print(top3)"], "n": 5, "out": ["65 4", "16.25", "['latte', 'tea', 'coffee']"]}, 96, T, FW)
o.append(tag(TX, oy(T, 4, 0), "모두 65잔, 메뉴 4개", K4, 1))
o.append(tag(TX, oy(T, 4, 1), "메뉴 하나당 평균 16.25잔", OR, 2))
o.append(code_line(3, 96, T, 2, "top3 = sorted(sales, key=sales.get, reverse=True)", "[:3]", K3))
o.append(tag(TX, oy(T, 4, 2), "줄 세운 리스트의 앞 3개", K3, 3))
SX, SWD = 96, 300
for i, v in enumerate(['"latte"', '"tea"', '"coffee"', '"cake"']):
    o.append(vbox(None, v, SX + i * (SWD + 16), 740, SWD, 96, K3 if i < 3 else GRAY, K3BG if i < 3 else FAINT, at("rise", 3), 34))
    o.append(p(f"position:absolute;left:{SX + i * (SWD + 16)}px;top:696px;width:{SWD}px;text-align:center;font-family:{MONO};font-size:26px;font-weight:700;color:{K3 if i < 3 else GRAY}", str(i), at("fade", 3)))
o.append(box(4, SX - 14, 684, 3 * SWD + 2 * 16 + 28, 168, K3))
o.append(tag(SX + 4 * (SWD + 16) + 10, 788, "[:3]", K3, 4))
W("m-with", o, "상위 몇 개는 sorted로 줄 세운 뒤 [:n]을 붙여서 뽑아요. 13의 sum, len과 자르기를 같이 써요. sales.values()를 sum하면 모두 65잔, len(sales)는 메뉴 4개예요. 나누면 메뉴 하나당 평균 16.25잔이에요. 많이 팔린 상위 3개는 sorted로 많은 순으로 세운 뒤 [:3]을 붙여요. sorted가 리스트를 주니까 바로 자를 수 있어요. 하나만 필요하면 max, 여러 개가 필요하면 sorted와 자르기예요." + REAL)

# ---------- part 5 ----------
o = [sec("t-mix")] + head(EB5, "숫자와 글자를 섞으면 비교할 수 없어요", K5)
T1, T2, FW = 210, 410, 1728
o += cell({"lines": ['print(sorted([4500, "5000", 6500]))'], "n": 1, "out": ["TypeError: '<' not supported between instances of 'str' and 'int'"], "err": True}, 96, T1, FW)
o.append(out_line(1, 96, T1, 1, 0, "TypeError: '<' not supported between instances of ", "'str' and 'int'"))
o.append(tag(cx(96, "TypeError: '<' not supported between instances of 'str' and 'int'") + 30, oy(T1, 1, 0), "글자와 숫자", RED, 1))
o += cell({"lines": ['print(sorted([4500, "5000", 6500], key=int))'], "n": 2, "out": ["[4500, '5000', 6500]"]}, 96, T2, 1180, attrs=at("rise", 2))
o.append(tag(96 + 1180 + 30, ly(T2, 0), "비교할 때만 숫자로", GR, 2))
o.append(tag(96 + 1180 + 30, oy(T2, 1, 0), "\"5000\"은 그대로 글자", OR, 3))
o.append(fix(96, 700, '[4500, "5000", 6500]', "[4500, 5000, 6500]", 4, 34))
o.append(caption("한 리스트에는 같은 타입을 담아요. 섞였으면 key로 맞춰 비교해요.", 900, 4))
W("t-mix", o, "숫자와 글자가 섞인 리스트는 크기를 비교할 수 없어서 TypeError가 나요. 가격 하나가 글자 \"5000\"으로 들어갔어요. sorted가 4500과 \"5000\"을 비교하려다 str과 int 사이에는 < 를 쓸 수 없다는 오류를 내요. max와 min도 똑같은 오류가 나요. key=int를 주면 비교할 때만 숫자로 바꿔서 줄 세워요. 결과에는 \"5000\"이 글자로 그대로 남아요. 처음부터 같은 타입으로 담는 게 가장 좋아요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p5", "오류와 함정"))

o = [sec("t-paren")] + head(EB5, "key에 괄호를 붙이면 TypeError가 나요", K5)
T1, T2, FW = 210, 400, 1728
o += cell({"lines": ['print(sorted(["latte", "tea"], key=len()))'], "n": 3, "out": ["TypeError: len() takes exactly one argument (0 given)"], "err": True}, 96, T1, FW)
o.append(code_line(1, 96, T1, 0, 'print(sorted(["latte", "tea"], key=len', "()", RED))
o.append(out_line(1, 96, T1, 1, 0, "TypeError: len() takes exactly one argument ", "(0 given)"))
o += cell({"lines": [SALES, "print(sorted(sales, key=sales.get()))"], "n": 4, "out": ["TypeError: get expected at least 1 argument, got 0"], "err": True}, 96, T2, FW, attrs=at("rise", 2))
o.append(code_line(2, 96, T2, 1, "print(sorted(sales, key=sales.get", "()", RED))
o.append(out_line(2, 96, T2, 2, 0, "TypeError: get expected at least 1 argument, ", "got 0"))
o.append(tag(cx(96, "TypeError: get expected at least 1 argument, got 0") + 30, oy(T2, 2, 0), "아무것도 안 넣고 먼저 불렸어요", RED, 3))
o.append(fix(96, 740, "key=len()", "key=len", 4, 34))
o.append(fix(96, 850, "key=sales.get()", "key=sales.get", 5, 34))
W("t-paren", o, "key에 괄호를 붙이면 함수가 그 자리에서 아무것도 받지 않고 먼저 실행돼요. len()은 재료 없이 불려서 하나를 받아야 하는데 0개를 받았다는 TypeError가 나요. sales.get()도 키 없이 불려서 got 0이라는 오류가 나요. 21에서 map에 add10()을 넘겼을 때와 같은 실수예요. key에는 괄호 없이 함수 이름만 적어요. 괄호는 sorted가 값을 하나씩 넣으면서 대신 붙여 줘요." + REAL)

o = [sec("t-lambda")] + head(EB5, "lambda나 key=를 빠뜨리면 생기는 오류", K5)
T1, T2, FW = 210, 400, 1180
TX = 96 + FW + 30
o += cell({"lines": ["print(sorted(sales.items(), key=kv[1]))"], "n": 5, "out": ["NameError: name 'kv' is not defined"], "err": True}, 96, T1, FW)
o.append(out_line(1, 96, T1, 1, 0, "NameError: name ", "'kv'"))
o.append(tag(TX, ly(T1, 0), "lambda kv: 가 빠졌어요", RED, 1))
o += cell({"lines": ["print(sorted(sales, sales.get))"], "n": 6, "out": ["TypeError: sorted expected 1 argument, got 2"], "err": True}, 96, T2, FW, attrs=at("rise", 2))
o.append(out_line(2, 96, T2, 1, 0, "TypeError: sorted expected 1 argument, ", "got 2"))
o.append(tag(TX, ly(T2, 0), "key= 이름이 빠졌어요", RED, 2))
o.append(fix(96, 640, "key=kv[1]", "key=lambda kv: kv[1]", 3, 34))
o.append(fix(96, 750, "sorted(sales, sales.get)", "sorted(sales, key=sales.get)", 4, 34))
o.append(caption("key는 꼭 key=로, lambda는 lambda 이름: 까지 적어요.", 900, 5))
W("t-lambda", o, "lambda kv: 를 빠뜨리면 NameError, key= 를 빠뜨리면 TypeError가 나요. 첫째는 lambda kv: 를 빼고 kv[1]만 적었어요. kv는 lambda가 만드는 매개변수 이름인데 lambda가 없으니 그런 변수가 없다는 오류가 나요. 둘째는 key= 없이 sales.get을 둘째 자리에 넣었어요. sorted는 줄 세울 값 하나만 위치로 받고, key와 reverse는 20에서 배운 키워드 인자로만 받아요. 그래서 1개를 받아야 하는데 2개를 받았다는 TypeError가 나요." + REAL)

# ---------- part 6 ----------
o = [sec("x-rank")] + head(EB6, "판매 순위표 3위까지 찍기", K6)
T, FW = 210, 1400
TX = 96 + FW + 30
RK = ['sales = {"coffee": 12, "latte": 30, "cake": 8, "tea": 15, "juice": 15}', "rank = sorted(sales.items(), key=lambda kv: (-kv[1], kv[0]))", "for i, kv in enumerate(rank[:3], 1):", '    print(f"{i}위 {kv[0]:<6}{kv[1]:>3}잔")']
o += cell({"lines": RK, "n": 1, "out": ["1위 latte  30잔", "2위 juice  15잔", "3위 tea    15잔"]}, 96, T, FW)
o.append(hl(96, T, FW, 1, 1, "mark", 1))
o.append(tag(TX, ly(T, 1), "두 기준 (3파트)", K3, 1))
o.append(hl(96, T, FW, 2, 1, "run", 2))
o.append(tag(TX, ly(T, 2), "1위부터 (18)", GR, 2))
o.append(row(96, 640, 1500, 110, small("key 결과", GRAY, 30, 180) + tup(["-15", "'juice'"], hi=(1,), w=180) + small("<", K6, 40) + tup(["-15", "'tea'"], hi=(1,), w=180), 3))
o.append(tag(1220, 695, "-15가 같아서 이름으로, juice가 먼저", K6, 3))
o.append(caption("줄 세우기, 자르기, 번호 붙이기를 이어서 순위표를 만들어요.", 900, 4))
W("x-rank", o, "줄 세우기, 자르기, 번호 붙이기를 이어서 판매 순위표를 만들어요. juice를 더해서 tea와 juice가 15잔으로 같아요. 3파트의 두 기준 key로 많은 순, 같으면 이름순으로 세워요. 앞 3개만 [:3]으로 자르고, 18에서 배운 enumerate에 시작 번호 1을 줘서 1위부터 번호를 붙였어요. kv는 튜플이라 kv[0]이 이름, kv[1]이 잔 수예요. 15잔끼리는 이름순이라 juice가 tea보다 앞이에요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p6", "실습"))

o = [sec("x-price")] + head(EB6, "가장 비싼 메뉴, 가장 싼 메뉴, 가격순 메뉴판", K6)
T, FW = 200, 1340
TX = 96 + FW + 30
PRC = ['menu = {"coffee": 4500, "latte": 5000, "cake": 6500, "tea": 4000}', "hi = max(menu, key=menu.get)", "lo = min(menu, key=menu.get)", 'print(f"가장 비싼 메뉴 {hi} {menu[hi]:,}원")', 'print(f"가장 싼 메뉴 {lo} {menu[lo]:,}원")', "for m in sorted(menu, key=menu.get):", '    print(f"{m:<7}{menu[m]:>6,}원")']
o += cell({"lines": PRC, "n": 2, "out": ["가장 비싼 메뉴 cake 6,500원", "가장 싼 메뉴 tea 4,000원", "tea     4,000원", "coffee  4,500원", "latte   5,000원", "cake    6,500원"]}, 96, T, FW)
o.append(hl(96, T, FW, 1, 2, "mark", 1))
o.append(tag(TX, ly(T, 1.5), "이름을 받아요", K6, 1))
o.append(hl(96, T, FW, 3, 2, "or", 2))
o.append(tag(TX, ly(T, 3.5), "menu[hi]로 가격 꺼내기", OR, 2))
o.append(hl(96, T, FW, 5, 1, "run", 3))
o.append(tag(TX, ly(T, 5), "가격순 키 리스트", GR, 3))
W("x-price", o, "max, min에 key=menu.get을 주면 가장 비싼 메뉴와 가장 싼 메뉴의 이름이 나와요. 4파트처럼 가격으로 비교해서 이름을 돌려줘요. 이름을 받았으니 menu[hi]로 가격도 꺼내서 같이 찍어요. 가격순 메뉴판은 sorted(menu, key=menu.get)이 준 키 리스트를 for로 돌면서 찍었어요. 칸 맞추기와 천 단위 콤마는 13에서 배운 그대로예요." + REAL)

o = [sec("x-board")] + head(EB6, "메뉴판을 이름 길이순, 같으면 abc 순으로", K6)
T, FW = 210, 1180
TX = 96 + FW + 30
o += cell({"lines": ['names = ["mocha", "tea", "latte", "americano", "cake"]', "print(sorted(names, key=len))", "print(sorted(names, key=lambda n: (len(n), n)))"], "n": 3, "out": ["['tea', 'cake', 'mocha', 'latte', 'americano']", "['tea', 'cake', 'latte', 'mocha', 'americano']"]}, 96, T, FW)
o.append(hl(96, T, FW, 1, 1, "skip", 1))
o.append(tag(TX, oy(T, 3, 0), "5끼리는 원래 순서", GRAY, 1))
o.append(hl(96, T, FW, 2, 1, "run", 2))
o.append(tag(TX, oy(T, 3, 1), "같으면 abc 순", GR, 2))
o.append(row(96, 560, 1500, 110, small("key 결과", GRAY, 30, 180) + tup(["5", '"latte"'], hi=(1,), w=180) + small("<", K6, 40) + tup(["5", '"mocha"'], hi=(1,), w=180), 3))
o.append(tag(1220, 615, "첫 칸 5가 같아서 이름으로", K6, 3))
o += plain_rows(96, 740, 1728, [["판매 순위 (3파트)", "(-m[1], m[0])", "많은 순, 같으면 이름순"], ["메뉴판 (지금)", "(len(n), n)", "짧은 순, 같으면 abc 순"]], [420, 480, 700], 4, 80, None, 30, mono_cols=(1,))
W("x-board", o, "기준이 둘이면 key가 (첫째 기준, 둘째 기준) 튜플을 돌려주게 해요. 메뉴판 이름을 짧은 것부터 적고 싶어요. key=len만 주면 길이 5인 mocha와 latte는 처음 적은 순서대로 mocha가 먼저예요. 같은 길이끼리 abc 순으로 세우려면 key가 길이와 이름을 묶은 튜플을 돌려주게 해요. 첫 칸 5가 같으니 둘째 칸 이름을 비교해서 latte가 앞으로 와요. 3파트의 판매량 순위와 같은 방법이에요. 이번에는 둘 다 작은 것부터라 -를 붙이지 않아요." + REAL)

o = [sec("x-score")] + head(EB6, "성적표를 점수순으로 세우고 1등과 평균 구하기", K6)
T, FW = 200, 1360
TX = 96 + FW + 30
SC = ['scores = [("kim", 92), ("lee", 78), ("park", 85), ("choi", 59)]', "ranked = sorted(scores, key=lambda s: s[1], reverse=True)", "for name, score in ranked:", '    print(f"{name:<5}{score:>3}")', 'print("1등:", max(scores, key=lambda s: s[1])[0])', 'print("평균:", sum(map(lambda s: s[1], scores)) / len(scores))']
o += cell({"lines": SC, "n": 4, "out": ["kim   92", "park  85", "lee   78", "choi  59", "1등: kim", "평균: 78.5"]}, 96, T, FW)
o.append(hl(96, T, FW, 1, 1, "mark", 1))
o.append(tag(TX, ly(T, 1), "점수 높은 순", K6, 1))
o.append(code_line(2, 96, T, 4, 'print("1등:", max(scores, key=lambda s: s[1])', "[0]", OR))
o.append(tag(TX, ly(T, 4), "튜플에서 이름만", OR, 2))
o.append(hl(96, T, FW, 5, 1, "run", 3))
o.append(tag(TX, ly(T, 5), "21의 map으로 점수만", GR, 3))
W("x-score", o, "정렬, max, map을 섞어서 성적표를 점수순으로 세우고 1등과 평균을 구해요. 17에서 만든 성적 데이터를 튜플 리스트로 적었어요. key=lambda s: s[1]과 reverse=True로 점수 높은 순으로 세워 찍어요. 1등은 max에 같은 key를 주면 돼요. max가 튜플을 통째로 주니까 [0]을 붙여 이름만 꺼냈어요. 평균은 21의 map으로 점수만 꺼내 sum에 넘기고 사람 수로 나눴어요." + REAL)

# ---------- wrap up ----------
o = [sec("trouble")] + head("정리", "막히면 오류의 마지막 줄을 봐요", RED)
TR = [("max(sales)가 엉뚱한 이름이에요", "딕셔너리는 키끼리 비교해요", "key=sales.get"),
      ("prices를 찍으니 None이에요", "prices = prices.sort()로 받았어요", "prices.sort()만"),
      ("['10', '100', '9'] 순서예요", "글자는 앞 글자부터 비교해요", "key=int"),
      ("TypeError: '<' not supported ...", "숫자와 글자를 섞었어요", "타입 맞추기, key=int"),
      ("TypeError: len() takes exactly ...", "key에 괄호를 붙였어요", "key=len"),
      ("NameError: name 'kv' is not defined", "lambda kv: 를 빠뜨렸어요", "key=lambda kv: kv[1]"),
      ("ValueError: max() iterable ... empty", "빈 리스트에 max를 썼어요", "default=0")]
for i, (q, a_, cmd) in enumerate(TR):
    y = 200 + i * 98
    mq = q.isascii()
    o.append(f'<div{at("rise", min(i + 1, 7))} style="position:absolute;left:96px;top:{y}px;width:1728px;height:98px;display:flex;flex-direction:row;align-items:center;gap:28px;padding:0 12px;border-bottom:2px solid {LINE}">'
             + num(i + 1, RED, 30)
             + p(f"width:700px;flex:none;{'font-family:' + MONO + ';font-size:26px;' if mq else 'font-size:28px;'}font-weight:700;color:{INK};white-space:nowrap", e(q))
             + p(f"width:480px;flex:none;font-size:26px;font-weight:500;color:{SUB};white-space:nowrap", e(a_))
             + p(f"flex:1;{'font-family:' + MONO + ';font-size:26px;' if cmd.isascii() else 'font-size:27px;'}font-weight:700;color:{GR};white-space:nowrap", e(cmd)) + '</div>')
o.append(caption("순서가 이상하면 map(key 함수, 리스트)로 비교할 값을 먼저 찍어 봐요.", 940, 8))
W("trouble", o, "순서가 이상하거나 오류가 나면 무엇끼리 비교했는지부터 봐요. 1번과 3번은 오류 없이 순서만 이상한 경우예요. 2번은 sort가 값을 돌려주지 않아서 생겨요. 4번은 타입이 섞였을 때, 5번과 6번은 key에 함수를 잘못 넣었을 때예요. 7번은 고른 결과가 비었을 때예요. 순서가 기대와 다르면 21의 map으로 key 함수 결과를 먼저 찍어 보면 원인이 보여요.", ("trouble", "정리"))

o = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>']
CH = [("sorted(xs)", "새 리스트, 원본 그대로", K2), ("xs.sort()", "원본을 바꾸고 None", K2), ("key=len", "len 결과로 비교", K2), ("key=lambda m: m[1]", "튜플 둘째 칸으로", K3),
      ("key=lambda m: (-m[1], m[0])", "많은 순, 같으면 이름순", K3), ("sorted(d, key=d.get)", "값 순서로 키 세우기", K3), ("max(d, key=d.get)", "값이 가장 큰 키", K4), ("max(xs, default=0)", "비어 있으면 0", K4)]
for i, (k, d, c) in enumerate(CH):
    x, y = 96 + (i // 4) * 888, 200 + (i % 4) * 130
    o.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:840px;height:130px;display:flex;flex-direction:column;justify-content:center;gap:6px;border-bottom:2px solid {LINE}">'
             + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:{c};white-space:pre", e(k)) + p(f"font-size:28px;font-weight:500;color:{SUB}", e(d)) + '</div>')
o.append(p(f"position:absolute;left:96px;top:780px;width:1728px;font-size:32px;font-weight:700;color:{INK}", "key에는 괄호 없이 함수 이름이나 lambda를 넣어요."))
o.append(p(f"position:absolute;left:96px;top:850px;width:1728px;font-size:30px;font-weight:500;color:{SUB}", "다음 챕터 23에서는 리스트 컴프리헨션으로 고르고 바꾸기를 한 줄에 적어요."))
W("cheatsheet", o, "key에 함수를 넣으면 그 결과로 비교한다는 것 하나로 이번 챕터를 묶을 수 있어요. sorted는 새 리스트를 주고 sort는 원본을 바꿔요. 튜플은 앞 칸부터 비교하니까 기준이 둘이면 튜플을 돌려주는 lambda를 써요. 딕셔너리는 get이나 items로 값 기준 정렬을 해요. max와 min도 key와 default를 받아요. 23에서는 21의 map, filter를 더 읽기 쉽게 쓰는 리스트 컴프리헨션을 배워요.")


# ---------- toc: number, title and pages only ----------
def finish(parts, toc_note, title):
    page = {sid: i + 1 for i, sid in enumerate(ORDER)}
    t = [f'<section id="toc" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
         f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>']
    for i, (ic, c, h, a, b) in enumerate(parts):
        x, y = 96 + (i // 3) * 888, 220 + (i % 3) * 200
        t.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:840px;height:200px;display:flex;flex-direction:row;align-items:center;gap:28px;border-bottom:2px solid {LINE}">'
                 f'<p style="width:70px;flex:none;font-size:72px;font-weight:900;line-height:1;color:{c}">{i + 1}</p>'
                 f'<x-icon name="{ic}" style="width:48px;height:48px;color:{c}"></x-icon>'
                 f'<p style="flex:1;font-size:40px;font-weight:700;color:{INK}">{e(h)}</p>'
                 f'<p style="font-size:30px;font-weight:700;color:{GRAY};white-space:nowrap">{page[a]}–{page[b]}쪽</p></div>')
    t.append(f'<p style="position:absolute;left:96px;top:900px;font-size:30px;color:{SUB}">{page["ready"]}쪽은 노트북 준비, {page["trouble"]}–{page["cheatsheet"]}쪽은 막힐 때와 한 장 요약이에요.</p>')
    with open(os.path.join(OUT, "toc.html"), "w") as f:
        f.write("\n".join(t) + f"\n<aside>{e(toc_note)}</aside>\n</section>\n")
    deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-04T03:00:00Z"}, "lists": "css", "title": title, "order": ORDER,
            "sections": SECTIONS,
            "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                      "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
            "designSystems": []}
    with open(os.path.join(OUT, "deck.json"), "w") as f:
        json.dump(deck, f, ensure_ascii=False, indent=2)
    print(len(ORDER), "slides")


finish([("Lightbulb", K1, "왜 필요한가", "s-why", "s-min"),
        ("Code", K2, "sorted, sort, key", "o-two", "k-lower"),
        ("Archive", K3, "튜플과 딕셔너리 정렬", "p-tuple", "p-get"),
        ("Star", K4, "max와 min", "m-basic", "m-with"),
        ("Warning", K5, "오류와 함정", "t-mix", "t-lambda"),
        ("Check", K6, "실습", "x-rank", "x-score")],
       "여섯 파트로 나눴고, 파트마다 새 커널에서 위에서부터 차례로 실행해요. 1파트는 max(sales)가 tea를 주는 장면과 key 그림이에요. 2파트는 sorted와 sort의 차이, reverse, 글자 비교 규칙, 이미 있는 함수를 key에 넣기예요. 3파트는 lambda를 key에 넣어 튜플과 딕셔너리를 줄 세워요. 4파트는 max와 min, 5파트는 자주 나는 오류, 6파트는 카페와 성적 실습이에요.",
       "정렬과 sorted, max, min 제대로 쓰기")
