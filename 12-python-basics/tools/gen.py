"""Generates every slide of the Python basics 1 deck (12) and slides/deck.json.

Story (chapter design frame in CLAUDE.md): a cafe bill written with bare numbers is hard to read and to fix,
so we give values names (part 1), look at their types (part 2), calculate (part 3), compare and join
conditions (part 4), then solve three cafe-order cases with all of it (part 5).

Layout rules taken from the Stageshow skill (github.com/benjitaylor/skills, references/craft.md, framing.md,
annotations.md, motion.md): one focal object per slide (the notebook cell or one diagram), terms labelled on
the code line with leader tags instead of cards, light tables with hairlines instead of bordered boxes,
values that change move or are covered in place, a wrong line is struck through beside the right one.
Highlights come from tools/HIGHLIGHT.md, spread over the deck: slam and shine on the cover, staggered rows with delay,
wiped arrows, cursor and keycaps, line tints and line spotlight, value swaps in place (text), spotlight, zoom, pulse,
dimmed past steps, code morph, count-up with marked letters, one shake on a failure, pen ring/underline/box, fly.
No slide needs more than five clicks.

Every cell and output comes from tools/demo.sh (tools/run_nb.py runs the cells with the project kernel).
Usage: python3 tools/gen.py slides
"""

import html, json, os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from highlight import (spot, spot_off, cursor, cursor_off, ring, underline, box, lspot, lspot_off, zoom, zoom_off, text,
                       pulse, shine, shake, keys, SLAM, WIPE, COUNT, MARK, DIM, DELAY, MORPH, MORPH_FROM, tok)

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT):
    if f.endswith(".html"):
        os.remove(os.path.join(OUT, f))
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
INK, SUB, LINE, CARD, BG = "#1D2330", "#4A5262", "#E1DED6", "#FFFFFF", "#F6F5F1"
BL, GR, OR, PUR, RED, NAVY, TEAL, GRAY = "#2459C9", "#1F8A4C", "#B26A00", "#5A3BB8", "#A33131", "#1E3F8F", "#0F7C86", "#6A7180"
JP = "#B8560F"          # Jupyter, same as chapters 09 and 10
SEL = "#2F7DE1"         # selected cell bar, like VS Code's focus color
CAFE = "#9A5B13"        # part 5, cafe examples
HL = {"run": "rgba(31,138,76,.16)", "skip": "rgba(106,113,128,.18)", "err": "rgba(163,49,49,.14)", "mark": "rgba(36,89,201,.13)", "note": "rgba(178,106,0,.16)"}
TINT = {BL: "#E3EBFA", NAVY: "#E1E6F2", TEAL: "#DDF0F1", PUR: "#ECE7F8", GR: "#E3F2E9", RED: "#F7E3E3", OR: "#FBEEDB", CAFE: "#F6EBDD", GRAY: "#ECEDEF"}


def e(s):
    return html.escape(s, quote=False)


def p(style, text, attrs=""):
    return f'<p{attrs} style="{style}">{text}</p>'


def bi(kind, order):
    return f' data-build-in="{kind} order {order}"' if order else ""


ORDER, SECTIONS = [], {}


def W(sid, parts, notes, section=None):
    if section:
        SECTIONS[section[0]] = {"description": section[1], "start": sid}
    ORDER.append(sid)
    with open(os.path.join(OUT, sid + ".html"), "w") as f:
        f.write("\n".join(parts) + f"\n<aside>{e(notes)}</aside>\n</section>\n")


def sec(sid, transition="fade"):
    return f'<section id="{sid}" data-transition="{transition}" style="background:{BG};color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">'


def head(eyebrow, title, color):
    return [p(f"position:absolute;left:96px;top:48px;width:1728px;font-size:26px;font-weight:700;color:{color}", e(eyebrow), ' id="eyebrow"'),
            f'<h2 id="title" style="position:absolute;left:96px;top:92px;width:1728px;font-size:56px;font-weight:700;line-height:1.2;color:{INK}">{title}</h2>']


def caption(text, order=None, top=956):
    return p(f"position:absolute;left:96px;top:{top}px;width:1728px;font-size:34px;font-weight:700;line-height:1.4;color:{INK}", text, ' id="caption"' + bi("rise", order))


def num(i, color, size=56, extra=""):
    return p(f"width:{size + 16}px;height:{size + 16}px;flex:none;border-radius:50%;background:{color};color:#FFFFFF;font-size:{size * 0.6:.0f}px;font-weight:900;line-height:{size + 16}px;text-align:center;{extra}", str(i))


def kbd(text, size=30, color=INK):
    caps = [p(f"font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.2;white-space:nowrap;color:{color};background:#FFFFFF;border:2px solid #C9CED8;border-bottom-width:5px;border-radius:10px;padding:6px 14px", e(k)) for k in text.split("+")]
    plus = p(f"font-size:{size * 0.8:.0f}px;font-weight:700;color:{GRAY}", "+")
    return '<div style="display:flex;flex-direction:row;align-items:center;gap:8px">' + plus.join(caps) + '</div>'


# ---------- notebook cell at 30px, with helpers to place tags and tints on its lines ----------
CF = 30
LH = CF * 1.45


def cell(c, left, top, w, sel=None, attrs=""):
    """c: dict(id, lines, n, out, err). The cell box starts at top; its text at left + 105."""
    lines, n = c.get("lines", [""]), c.get("n")
    chosen = sel == c["id"]
    o = [f'<div id="{c["id"]}"{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;display:flex;flex-direction:column;gap:10px">']
    bar = f'<div style="width:7px;flex:none;border-radius:4px;background:{SEL if chosen else "transparent"}"></div>'
    gutter = p(f"width:58px;flex:none;font-family:{MONO};font-size:22px;color:{GRAY};text-align:right;padding-top:12px", f"[{n}]" if n else "[ ]")
    txt = "".join(p(f"font-family:{MONO};font-size:{CF}px;line-height:1.45;white-space:pre;color:{INK}", e(l) if l else "&#160;") for l in lines)
    tag_ = p(f"position:absolute;right:14px;bottom:8px;font-size:18px;color:{GRAY}", "Python")
    box = f'<div style="flex:1;position:relative;background:#FFFFFF;border:2px solid {LINE};border-radius:10px;padding:8px 18px 8px;display:flex;flex-direction:column">{txt}{tag_}</div>'
    o.append(f'<div style="display:flex;flex-direction:row;gap:10px;align-items:stretch">{bar}{gutter}{box}</div>')
    if c.get("out"):
        col = lambda l: RED if c.get("err") and re.match(r"[A-Za-z]+Error", l) else INK
        o.append(''.join(p(f"margin-left:85px;padding:0 20px;font-family:{MONO};font-size:{CF}px;line-height:1.45;white-space:pre;color:{col(l)}", e(l)) for l in c["out"]))
    o.append('</div>')
    return o


def cell_h(c):
    return 20 + LH * len(c["lines"]) + (10 + LH) * len(c.get("out", []))


def ly(top, i):
    """Center y of code line i of a cell drawn at top."""
    return top + 10 + i * LH + LH / 2


def oy(top, n, j):
    """Center y of output line j of a cell with n code lines."""
    return top + 20 + n * LH + 10 + j * (LH + 10) + LH / 2


def tw(s, size=CF):
    return sum(size * (1.0 if '가' <= ch <= '힣' else 0.6) for ch in s)


def cx(left, s, upto):
    """x where character `upto` of string s starts inside a cell at left."""
    return left + 105 + tw(s[:upto])


def tx(left, lines, gap=36):
    """x just right of the longest of the given lines inside a cell at left."""
    return int(left + 105 + max(tw(l) for l in lines) + gap)


def hl(left, top, w, i, n=1, kind="mark", order=1):
    y = top + 10 + i * LH
    return f'<div{bi("fade", order)} style="position:absolute;left:{left + 87}px;top:{y:.0f}px;width:{w - 89}px;height:{n * LH:.0f}px;background:{HL[kind]};border-radius:6px"></div>'


def tag(x, y, text, color, order=None, size=28, lead=True, anim="fade", w=None):
    """A leader label '← text' centred on y. No box."""
    ws = f"width:{w}px;white-space:normal;" if w else "white-space:nowrap;"
    t = ("← " if lead else "") + text
    return p(f"position:absolute;left:{x:.0f}px;top:{y - size * 0.72:.0f}px;{ws}font-size:{size}px;font-weight:700;line-height:1.45;color:{color}", t, bi(anim, order))


def mono(text, size=28, color=INK, bg="#ECEAE3", extra="", raw=False):
    return p(f"font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.4;color:{color};background:{bg};border-radius:10px;padding:4px 16px;white-space:pre;{extra}", text if raw else e(text))


def hs(text, color):
    """Tint the part of an expression that is computed next."""
    return f'<span style="background:{TINT[color]};color:{color};border-radius:8px;padding:0 6px;box-shadow:inset 0 -4px 0 {color}">{e(text)}</span>'


def tf(v, size=26):
    c, bg = (GR, "#E3F2E9") if v == "True" else (RED, "#F7E3E3")
    return p(f"display:inline-block;font-family:{MONO};font-size:{size}px;font-weight:700;color:{c};background:{bg};border-radius:10px;padding:2px 14px;white-space:nowrap", v)


def arrow(w, color="#B9BEC8", h=None, extra=""):
    h = h or max(22, w * 0.55)
    return f'<x-shape kind="arrow-right" style="width:{w}px;height:{h:.0f}px;flex:none;background:{color};{extra}"></x-shape>'


def var_box(sid, name, value, left, top, color=BL, w=420, h=230, attrs="", vsize=72, vid=None):
    """A variable drawn as a box with its name on top. value may be '' for an empty box."""
    v = p(f"font-family:{MONO};font-size:{vsize}px;font-weight:700;color:{INK}", e(value), f' id="{vid}"' if vid else "") if value else ""
    return (f'<div id="{sid}"{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:{CARD};border:3px solid {color};border-radius:22px;display:flex;flex-direction:column;overflow:hidden">'
            + p(f"height:68px;flex:none;background:{color};color:#FFFFFF;font-family:{MONO};font-size:34px;font-weight:700;line-height:68px;padding:0 26px", e(name))
            + f'<div style="flex:1;display:flex;align-items:center;justify-content:center">{v}</div></div>')


def box_value(sid, value, left, top, w, h, attrs="", vsize=72, color=INK, struck=False):
    """A value placed over the body of a var_box (same left/top/w/h as the box). Opaque, so it covers the old value."""
    deco = "text-decoration:line-through;text-decoration-thickness:4px;" if struck else ""
    return (f'<div id="{sid}"{attrs} style="position:absolute;left:{left + 3}px;top:{top + 71}px;width:{w - 6}px;height:{h - 74}px;background:{CARD};border-radius:0 0 19px 19px;display:flex;align-items:center;justify-content:center">'
            + p(f"font-family:{MONO};font-size:{vsize}px;font-weight:700;color:{color};{deco}", e(value)) + '</div>')


def rows(left, top, w, data, widths, order0=1, rh=88, header=None, fs=30, kinds=None, step=1, rid=None, anim="rise", delay=0):
    """A light table: gray header over a dark rule, rows split by hairlines, no boxes.
    data cells are HTML. kinds: per column 'code' or 'text'. step=0 shows all rows at once (order0)."""
    o, y = [], top
    if header:
        o.append(f'<div style="position:absolute;left:{left}px;top:{y}px;width:{w}px;height:50px;display:flex;flex-direction:row;gap:24px;border-bottom:3px solid {INK}">'
                 + "".join(p(f"width:{cw}px;flex:none;font-size:24px;font-weight:700;color:{GRAY}", e(c)) for c, cw in zip(header, widths)) + '</div>')
        y += 50
    for i, r in enumerate(data):
        cells_ = "".join(f'<div style="width:{cw}px;flex:none;display:flex;flex-direction:row;align-items:center;gap:12px;font-size:{fs}px;line-height:1.35">{c}</div>' for c, cw in zip(r, widths))
        order = (order0 + i * step) if order0 else None
        ida = f' id="{rid}{i}"' if rid else ""
        dl = DELAY(i * delay) if delay and order else ""
        o.append(f'<div{ida}{bi(anim, order)}{dl} style="position:absolute;left:{left}px;top:{y + i * rh}px;width:{w}px;height:{rh}px;display:flex;flex-direction:row;align-items:center;gap:24px;border-bottom:2px solid {LINE}">{cells_}</div>')
    return o


def code(t, color=INK, size=30, raw=False):
    return f'<span style="font-family:{MONO};font-weight:700;font-size:{size}px;color:{color};white-space:pre">{t if raw else e(t)}</span>'


def txt(t, color=SUB, size=28, weight=500):
    return f'<span style="font-size:{size}px;font-weight:{weight};color:{color}">{t}</span>'


def fix(left, top, bad, good, order, size=34, after=""):
    """The wrong line struck through, an arrow, the right line."""
    return (f'<div{bi("rise", order)} style="position:absolute;left:{left}px;top:{top}px;display:flex;flex-direction:row;align-items:center;gap:22px">'
            + p(f"font-size:{size}px;font-weight:900;color:{RED}", "✕")
            + p(f"font-family:{MONO};font-size:{size}px;font-weight:700;color:{RED};text-decoration:line-through;text-decoration-thickness:3px;white-space:pre", e(bad))
            + arrow(70)
            + p(f"font-size:{size}px;font-weight:900;color:{GR}", "✓")
            + p(f"font-family:{MONO};font-size:{size}px;font-weight:700;color:{INK};background:#E3F2E9;border:3px solid {GR};border-radius:14px;padding:6px 20px;white-space:pre", e(good))
            + after + '</div>')


def chain(rs, left, top, start=1, gap=96, size=38, color=TEAL, note_w=None, step=1, delay=0, dim=None):
    """Evaluation steps, one per click: (expression html, note). The last row is the answer."""
    o = []
    for i, (ex, note) in enumerate(rs):
        last = i == len(rs) - 1
        ex_ = (DELAY(i * delay) if delay else "") + (DIM(dim) if dim else "")
        o.append(f'<div{bi("rise", start + i * step)}{ex_} style="position:absolute;left:{left}px;top:{top + i * gap}px;display:flex;flex-direction:row;align-items:center;gap:26px">'
                 + mono(ex, size, color if last else INK, TINT[color] if last else "#ECEAE3", raw=True)
                 + (p(f"font-size:26px;font-weight:700;color:{SUB};white-space:nowrap", e(note)) if note else "") + '</div>')
    return o


NB = "basics.ipynb"

# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#F2B27A;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
       f'<h1{SLAM(1)} style="font-size:92px;font-weight:900;line-height:1.1;color:#F6F5F1">파이썬 기초 1<br>변수, 타입, 연산</h1>',
       '<p style="font-size:40px;line-height:1.4;color:#BFC6D4">값에 이름을 붙이고,<br>계산하고, 비교하기</p>']
cov.append('<div id="cov-code" style="position:absolute;left:1080px;top:300px;width:720px;height:480px;background:#252B36;border-radius:24px;padding:44px 52px;display:flex;flex-direction:column;justify-content:center;gap:34px">')
for code_, out_, c in [('price = 4500', '', '#8FB4FF'), ('type(price)', 'int', '#9FB8E8'), ('price * 2', '9000', '#7FD3DA'), ('price * 2 >= 10000', 'False', '#C4B1FF')]:
    cov.append('<div style="display:flex;flex-direction:row;align-items:center;gap:28px">'
               + p(f"width:420px;flex:none;font-family:{MONO};font-size:36px;font-weight:700;color:{c};white-space:pre", e(code_))
               + (arrow(46, "#5A6172") + p(f"font-family:{MONO};font-size:36px;font-weight:700;color:#E6E9EF", e(out_)) if out_ else "") + '</div>')
cov.append('</div>')
cov.append(shine(2, "cov-code"))
W("cover", cov, "이번 챕터는 파이썬 코드를 직접 적어요. 값에 이름을 붙이는 변수, 값의 종류인 타입, 숫자를 계산하는 사칙연산, True와 False로 답하는 비교와 논리연산을 봐요. 마지막에는 카페 주문 계산을 이 네 가지로 풀어요. 문자열과 리스트는 다음 13 챕터에서 이어서 봐요. 모든 예제는 노트북 셀에 적고 실행해요.", ("intro", "들어가기"))

ORDER.append("toc")   # written last, after page numbers are known

# ---------- why ----------
EB0 = "왜 필요한가"
o = [sec("why")] + head(EB0, "숫자만 적으면 무슨 계산인지 잊어요", CAFE)
A, B = 270, 500
LA, LB = "print(4500 * 2 + 5000)", "print(20000 - (4500 * 2 + 5000))"
o += cell({"id": "c-why1", "lines": [LA], "n": 1, "out": ["14000"]}, 96, A, 1060, sel="c-why1")
o += cell({"id": "c-why2", "lines": [LB], "n": 2, "out": ["6000"]}, 96, B, 1060, sel="c-why2", attrs=bi("rise", 2))
o.append(tag(1196, ly(A, 0), "아메리카노 두 잔과 라떼 한 잔", CAFE, 1))
o.append(tag(1196, ly(B, 0), "2만 원을 내면 잔돈은? 같은 식을 또 적어요", CAFE, 2, w=620))
o.append(p(f"position:absolute;left:96px;top:740px;width:1728px;font-size:40px;font-weight:700;line-height:1.4;color:{RED}", "아메리카노가 4800원이 되면 4500을 찾아 두 줄 다 고쳐요", bi("fade", 3)))
for top_, s_, k in [(A, LA, 6), (B, LB, 15)]:
    o.append(underline(3, cx(96, s_, k), cx(96, s_, k + 4), ly(top_, 0) + 22, RED))
o.append(caption("숫자에 이름을 붙여 두면 읽기 쉽고, 고칠 곳도 한 곳이에요. 그 이름이 변수예요.", 4))
W("why", o, "숫자만으로 적은 계산은 금방 무슨 뜻인지 잊어요. 카페에서 아메리카노 4500원 두 잔과 라떼 5000원 한 잔을 계산했어요. 잔돈을 구하려면 같은 식을 한 번 더 적어야 해요. 가격이 4800원으로 오르면 4500이 나온 곳을 모두 찾아 고쳐야 하고, 하나라도 놓치면 계산이 틀려요. 숫자에 price 같은 이름을 붙이면 식이 읽히고, 고칠 곳도 한 곳으로 줄어요. 이 챕터 끝의 카페 예제에서 같은 계산을 변수로 다시 적어요. 출력은 hello-uv 커널에서 실제로 실행한 결과예요.", ("why", "왜 필요한가"))

# ---------- big picture ----------
o = [sec("big")] + head("큰 그림", "값을 상자에 담고, 계산하고, 비교해요", INK)
COLS = [(BL, "1", "변수", "americano = 4500"), (NAVY, "2", "타입", "type(4500)"), (TEAL, "3", "계산", "total = americano * 2"), (PUR, "4", "비교", "total >= 10000")]
X0, CW, GAP = 96, 372, 80
for i, (c, n_, name, code_) in enumerate(COLS):
    x = X0 + i * (CW + GAP)
    o.append(f'<div{bi("rise", i + 1)} style="position:absolute;left:{x}px;top:236px;width:{CW}px;display:flex;flex-direction:row;align-items:center;gap:16px">'
             + num(n_, c, 36) + p(f"font-size:36px;font-weight:700;color:{c}", name) + '</div>')
    o.append(p(f"position:absolute;left:{x}px;top:690px;width:{CW + 40}px;font-family:{MONO};font-size:24px;font-weight:700;color:{SUB};white-space:pre", e(code_), bi("fade", i + 1) + DELAY(250)))
    if i:
        o.append(f'<div{WIPE(i + 1)} style="position:absolute;left:{x - GAP + 14}px;top:470px">{arrow(52)}</div>')
o.append(var_box("bg-am", "americano", "4500", X0, 340, BL, CW, 300, bi("rise", 1), 76))
# types: three values and their type names, stacked
x = X0 + CW + GAP
for j, (v, t, c) in enumerate([("4500", "int", BL), ('"라떼"', "str", GR), ("True", "bool", PUR)]):
    o.append(f'<div{bi("rise", 2)} style="position:absolute;left:{x}px;top:{350 + j * 100}px;width:{CW}px;height:84px;display:flex;flex-direction:row;align-items:center;gap:20px;border-bottom:2px solid {LINE}">'
             + p(f"width:180px;flex:none;font-family:{MONO};font-size:40px;font-weight:700;color:{INK}", e(v)) + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:{c}", t) + '</div>')
x = X0 + 2 * (CW + GAP)
o.append(var_box("bg-total", "total", "9000", x, 340, TEAL, CW, 300, bi("rise", 3), 76))
x = X0 + 3 * (CW + GAP)
o.append(f'<div{bi("rise", 4)} style="position:absolute;left:{x}px;top:340px;width:{CW}px;height:300px;display:flex;flex-direction:column;align-items:flex-start;justify-content:center;gap:26px">'
         + p(f"font-family:{MONO};font-size:40px;font-weight:700;color:{INK};white-space:pre", "9000 >= 10000") + tf("False", 56) + '</div>')
o.append(f'<div{bi("rise", 5)} style="position:absolute;left:96px;top:800px;width:1728px;height:96px;border-top:2px solid {LINE};display:flex;flex-direction:row;align-items:center;gap:20px">'
         + num(5, CAFE, 36) + p(f"font-size:34px;font-weight:700;color:{CAFE}", "카페 주문") + p(f"font-size:30px;color:{SUB}", "네 가지를 섞어 합계와 잔돈, 나눠 내기, 할인 조건을 풀어요") + '</div>')
W("big", o, "이번 챕터에서 배울 네 가지를 한 줄로 이었어요. 1파트는 값을 이름 붙은 상자에 담는 변수예요. 2파트는 값의 종류인 타입이에요. 4500은 정수, 따옴표로 감싼 라떼는 문자열, True는 불리언이에요. 3파트는 상자에 든 값으로 계산해서 새 상자에 담아요. 4파트는 계산한 값을 비교해서 True나 False로 답을 받아요. 마지막 5파트는 네 가지를 섞어서 카페 주문 계산을 풀어요.")

# ---------- ready ----------
o = [sec("ready")] + head("들어가기", "hello-uv에 새 노트북 basics.ipynb를 만들어요", JP)
o.append('<div id="nb-bar" style="position:absolute;left:96px;top:228px;width:1728px;height:76px;background:#ECEAE3;border-radius:14px;display:flex;flex-direction:row;align-items:center;padding:0 24px;gap:26px">'
         + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{INK};white-space:nowrap", e(NB), ' id="nb-file"')
         + "".join(p(f"font-size:22px;color:{SUB};white-space:nowrap", e(t)) for t in ["+ Code", "+ Markdown", "▷ Run All", "↻ Restart", "Variables"]) + '<div style="flex:1"></div>'
         + p(f"font-size:22px;font-weight:700;color:{GR};background:#E3F2E9;border-radius:8px;padding:6px 14px;white-space:nowrap", ".venv (Python 3.14.6)", ' id="nb-kernel"') + '</div>')
o += cell({"id": "c-empty", "lines": [""], "n": None}, 96, 330, 1728, sel="c-empty")
steps_ = [("VS Code로 hello-uv 폴더를 열어요", ""), ("탐색기에서 새 파일 basics.ipynb를 만들어요", ""), ("오른쪽 위 커널로 .venv를 골라요", ""), ("셀에 적고 Shift+Enter로 실행해요", "")]
for i, (s_, _) in enumerate(steps_):
    o.append(f'<div{bi("rise", i + 1)} style="position:absolute;left:96px;top:{450 + i * 104}px;width:1000px;height:96px;display:flex;flex-direction:row;align-items:center;gap:24px;border-bottom:2px solid {LINE}">'
             + num(i + 1, JP, 36) + p(f"font-size:32px;font-weight:700;color:{INK}", e(s_)) + '</div>')
o.append(cursor(2, target="nb-file"))
o.append(cursor(3, target="nb-kernel"))
o.append(cursor(4, x=400, y=355))
o.append(keys(4, 760, 770, "Shift+Enter", 26))
o.append(cursor_off(5))
o.append(p(f"position:absolute;left:1200px;top:462px;font-size:28px;font-weight:700;color:{GRAY}", "기억이 안 나면", bi("fade", 5)))
for i, (a_, b_) in enumerate([("커널 .venv 고르기", "09 · 25–27쪽"), ("변수 이름 규칙", "10 · 24–26쪽"), ("자료형과 type()", "10 · 27–28쪽")]):
    o.append(f'<div{bi("fade", 5)} style="position:absolute;left:1200px;top:{520 + i * 84}px;width:624px;height:76px;display:flex;flex-direction:row;align-items:center;gap:20px;border-bottom:2px solid {LINE}">'
             + p(f"flex:1;font-size:28px;color:{INK}", e(a_)) + p(f"font-size:26px;font-weight:700;color:{GRAY};white-space:nowrap", e(b_)) + '</div>')
W("ready", o, "09에서 만든 hello-uv 폴더를 VS Code로 열고, 그 안에 basics.ipynb라는 새 노트북을 만들어요. 커널은 09에서 고른 .venv예요. 셀에 코드를 적고 Shift+Enter를 누르면 실행되고 다음 셀로 내려가요. 10에서 배운 변수 이름 규칙(스네이크 표기법)과 자료형을 그대로 써요. 기억이 안 나면 오른쪽에 적힌 쪽을 먼저 다시 봐요. 슬라이드의 셀 번호는 파트마다 [1]부터 다시 셌어요. 한 노트북에서 이어서 실행하면 번호가 계속 커져요.")

# ---------- part 1: variables ----------
EB1 = "1. 변수에 값 넣기"
o = [sec("assign")] + head(EB1, "= 는 오른쪽 값을 왼쪽 이름에 넣어요", BL)
o += cell({"id": "c-age", "lines": ["age = 25"], "n": 1}, 96, 228, 700, sel="c-age")
o.append(tag(96 + 105, 340, "넣기만 해서 출력은 없어요. 값은 커널이 기억해요", GRAY, None, 26, False))
TY, TS = 540, 132       # token row top, token font size
TCH = TS * 0.6
for t, lbl, c, k in [("age", "이름", BL, 0), ("=", "넣어요", OR, 4), ("25", "값", GR, 6)]:
    x = 96 + k * TCH
    tid = ' id="tok-25"' if t == "25" else ""
    o.append(p(f"position:absolute;left:{x:.0f}px;top:{TY}px;font-family:{MONO};font-size:{TS}px;font-weight:700;line-height:1.2;color:{c};white-space:pre", e(t), tid))
    o.append(p(f"position:absolute;left:{x:.0f}px;top:{TY + 172}px;width:{len(t) * TCH:.0f}px;font-size:34px;font-weight:700;color:{c};text-align:center;white-space:nowrap", lbl))
# a pen arrow from 25 back over to age
x1, x2, yb = 96 + 7 * TCH, 96 + 1.5 * TCH, TY + 6
o.append(f'<svg data-build-in="draw order 1" viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible"><g fill="none" stroke="{OR}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round">'
         f'<path d="M{x1:.0f},{yb} C{x1 - 40:.0f},{yb - 90} {x2 + 40:.0f},{yb - 90} {x2:.0f},{yb}"/><path d="M{x2 - 18:.0f},{yb - 26} L{x2:.0f},{yb} L{x2 + 26:.0f},{yb - 14}"/></g></svg>')
o.append(p(f"position:absolute;left:{x2 + 60:.0f}px;top:{TY - 112}px;font-size:28px;font-weight:700;color:{OR};white-space:nowrap", "오른쪽에서 왼쪽으로", bi("fade", 1)))
BX, BY, BW, BH = 1300, 450, 460, 320
o.append(var_box("box-age", "age", "", BX, BY, BL, BW, BH))
o.append(f'<div id="v-age" data-build-in="fly order 2" data-from="tok-25" style="position:absolute;left:{BX + 3}px;top:{BY + 71}px;width:{BW - 6}px;height:{BH - 74}px;display:flex;align-items:center;justify-content:center">'
         + p(f"font-family:{MONO};font-size:{TS}px;font-weight:700;color:{INK}", "25") + '</div>')
o.append(caption("수학의 '같다'와 뜻이 달라요. 25를 age라는 상자에 넣어요.", 3))
W("assign", o, "등호 = 는 오른쪽 값을 왼쪽 이름에 넣으라는 명령이에요. 변수는 값에 붙인 이름이에요. age라는 이름의 상자에 25를 넣는다고 생각해요. 수학에서 = 는 양쪽이 같다는 뜻이지만 파이썬에서는 넣기라서 오른쪽에서 왼쪽으로 읽어요. 이름은 10에서 정한 대로 스네이크 표기법으로 적어요. 이 셀은 넣기만 해서 출력이 없고, 실행 번호 [1]만 생겨요.", ("var", "변수에 값 넣기"))

o = [sec("show")] + head(EB1, "넣은 값은 두 가지 방법으로 봐요", BL)
T = 300
o.append(p(f"position:absolute;left:96px;top:226px;font-size:30px;font-weight:700;color:{BL}", "셀 마지막 줄에 이름만"))
o += cell({"id": "c-show1", "lines": ["age"], "n": 2, "out": ["25"]}, 96, T, 820, sel=None, attrs=bi("rise", 1))
o.append(tag(tx(96, ["age"]), oy(T, 1, 0), "마지막 줄이 값이면 그대로 보여요", BL, 1, 26))
o.append(p(f"position:absolute;left:1004px;top:226px;font-size:30px;font-weight:700;color:{BL}", "print()로 꺼내기", bi("fade", 2)))
L2 = ["print(age)", 'print("나이:", age)']
o += cell({"id": "c-show2", "lines": L2, "n": 3, "out": ["25", "나이: 25"]}, 1004, T, 820, sel="c-show2", attrs=bi("rise", 2))
# the print line taken apart, big
BIGY, BS = 600, 76
BIG = 'print("나이:", age)'
o.append(p(f"position:absolute;left:96px;top:{BIGY}px;font-family:{MONO};font-size:{BS}px;font-weight:700;line-height:1.2;color:{INK};white-space:pre", e(BIG), bi("fade", 3)))
bx = lambda k: 96 + tw(BIG[:k], BS)
o.append(underline(3, bx(6), bx(12), BIGY + BS * 1.2 + 12, OR))
o.append(underline(4, bx(14), bx(17), BIGY + BS * 1.2 + 12, BL))
o.append(p(f"position:absolute;left:{bx(6):.0f}px;top:{BIGY + BS * 1.2 + 40:.0f}px;font-size:32px;font-weight:700;color:{OR};white-space:nowrap", "따옴표 안 글자는 그대로", bi("fade", 3)))
o.append(p(f"position:absolute;left:{bx(14) + 60:.0f}px;top:{BIGY + BS * 1.2 + 40:.0f}px;font-size:32px;font-weight:700;color:{BL};white-space:nowrap", "값 25로 바뀌고, 쉼표 자리는 한 칸", bi("fade", 4)))
W("show", o, "넣은 값을 보는 방법은 두 가지예요. 첫째, 셀 마지막 줄에 이름만 적으면 노트북이 그 값을 보여 줘요. 둘째, print()는 괄호 안의 값을 출력해요. 쉼표로 여러 개를 넣으면 한 칸씩 띄워서 한 줄로 보여 줘요. 따옴표로 감싼 글자는 그대로 나오고, 따옴표 없는 age는 그 안의 값 25로 바뀌어요. 빨리 확인할 땐 이름만, 설명을 붙일 땐 print(\"설명\", 값)을 써요. 이 챕터의 예제는 이 두 방법만 써요.")

o = [sec("reassign")] + head(EB1, "다시 넣으면 새 값으로 바뀌어요", BL)
T = 300
o += cell({"id": "c-age2", "lines": ["age = 26", "age"], "n": 4, "out": ["26"]}, 96, T, 860, sel="c-age2")
o.append(hl(96, T, 860, 0, 1, "mark", 1))
o.append(tag(tx(96, ["age = 26"]), ly(T, 0), "같은 이름에 새 값", BL, 1))
BX, BY, BW, BH = 1260, 260, 520, 340
o.append(var_box("box-age", "age", "26", BX, BY, BL, BW, BH, vsize=110, vid="v25").replace('id="v25"', 'id="v25" data-start="25"'))
o.append(text(1, "v25", "26"))
o.append(p(f"position:absolute;left:{BX}px;top:{BY + BH + 50}px;width:{BW}px;text-align:center;font-size:30px;font-weight:700;color:{GRAY}", "예전 값", bi("fade", 1)))
o.append(p(f"position:absolute;left:{BX}px;top:{BY + BH + 96}px;width:{BW}px;text-align:center;font-family:{MONO};font-size:72px;font-weight:700;color:{GRAY};text-decoration:line-through;text-decoration-thickness:5px", "25", ' id="old25" data-build-in="fly order 1" data-from="v25"'))
o += rows(96, 620, 860, [[code("[1]", GRAY, 24), code("age = 25", GRAY, 34, ) , txt("처음 넣은 값", GRAY, 26)], [code("[4]", BL, 24), code("age = 26", INK, 34), txt("지금 남은 값", BL, 26, 700)]], [60, 300, 400], 1, 96, ["셀", "넣은 순서", ""])
o.append(caption("상자 하나에는 값이 하나만 들어가요. 마지막에 넣은 값만 남아요.", 3))
W("reassign", o, "같은 이름에 다시 값을 넣으면 예전 값을 지우고 새 값을 넣어요. 변수라는 이름도 값이 변할 수 있어서 붙었어요. age에 26을 넣고 마지막 줄에 age를 적어서 26이 보여요. 예전 값 25는 더 이상 꺼낼 수 없어요. 셀 번호가 [4]인 건 앞 장의 두 셀 [2], [3]을 실행한 다음이라서예요.")

o = [sec("update")] + head(EB1, "age = age + 1은 오른쪽부터 계산해요", BL)
T = 228
o += cell({"id": "c-age3", "lines": ["age = age + 1", "age"], "n": 5, "out": ["27"]}, 96, T, 860, sel="c-age3")
BX, BY, BW, BH = 1300, 228, 460, 280
o.append(var_box("box-age", "age", "27", BX, BY, BL, BW, BH, vsize=96, vid="v27").replace('id="v27"', 'id="v27" data-start="26"'))
o.append(text(3, "v27", "27"))
UY, US = 600, 104
U = "age = age + 1"
ux = lambda k: 96 + k * US * 0.6
o.append(p(f"position:absolute;left:96px;top:{UY}px;font-family:{MONO};font-size:{US}px;font-weight:700;line-height:1.2;color:{INK};white-space:pre", e(U)))
LBY = UY + 160
for k1, k2, lab, c, order in [(6, 9, "① 지금 값 26", BL, 1), (10, 13, "② 1을 더해 27", TEAL, 2), (0, 3, "③ 27을 넣어요", OR, 3)]:
    o.append(underline(order, ux(k1), ux(k2), UY + 138, c))
    o.append(p(f"position:absolute;left:{ux(k1):.0f}px;top:{LBY}px;font-size:32px;font-weight:700;color:{c};white-space:nowrap", lab, bi("fade", order)))
o.append(caption("10에서 실행한 x = x + 1도 같은 순서예요.", 4))
W("update", o, "age = age + 1은 = 오른쪽을 먼저 계산하고 그 결과를 왼쪽에 넣어요. 수학이라면 말이 안 되는 식이에요. 1단계에서 지금 age에 든 26을 읽고, 2단계에서 1을 더해 27을 만들고, 3단계에서 그 27을 다시 age에 넣어요. 10의 실행 번호 장에서 x = x + 1을 두 번 실행했을 때 11, 12로 바뀐 것도 같은 원리예요. 이 셀도 실행할 때마다 1씩 커져요.")

o = [sec("last-line")] + head(EB1, "이름만 적으면 마지막 줄만 보여요", BL)
T = 250
L1 = ['user_name = "kim"', "age", "user_name"]
o += cell({"id": "c-ll1", "lines": L1, "n": 6, "out": ["'kim'"]}, 96, T, 820)
o.append(hl(96, T, 820, 1, 1, "skip", 1))
o.append(tag(tx(96, L1, 30), ly(T, 1), "실행돼도 안 보여요", GRAY, 1, 26))
o.append(hl(96, T, 820, 2, 1, "run", 2))
o.append(tag(tx(96, L1, 30), ly(T, 2), "이 줄만 보여요", GR, 2, 26))
o += cell({"id": "c-ll2", "lines": ["print(age)", "print(user_name)"], "n": 7, "out": ["27", "kim"]}, 1004, T, 820, sel="c-ll2", attrs=bi("rise", 3))
o.append(hl(1004, T, 820, 0, 2, "run", 3))
o.append(tag(tx(1004, ["print(user_name)"]), ly(T, 0.5), "둘 다 보여요", GR, 3, 26))
VY = 700
for x, v, lab in [(96, "'kim'", "이름만 적으면 따옴표까지"), (1004, "kim", "print는 글자만")]:
    o.append(f'<div{bi("rise", 4)} style="position:absolute;left:{x}px;top:{VY}px;width:820px;height:130px;border-top:2px solid {LINE};display:flex;flex-direction:row;align-items:center;gap:30px">'
             + p(f"font-family:{MONO};font-size:64px;font-weight:700;color:{INK}", e(v)) + p(f"font-size:30px;font-weight:700;color:{SUB}", lab) + '</div>')
o.append(caption("여러 값을 보려면 줄마다 print()를 써요.", 5))
W("last-line", o, "셀 마지막 줄에 이름만 적는 방법은 맨 마지막 줄 하나만 보여 줘요. 왼쪽 셀에서 age 줄도 실행은 됐지만 화면에는 나오지 않았어요. 값을 여러 개 보고 싶으면 오른쪽처럼 줄마다 print()를 써요. 출력 모양도 조금 달라요. 이름만 적으면 문자열이라는 걸 알려 주려고 따옴표까지 보여 주고, print는 글자만 보여 줘요. age가 27인 건 앞 장의 셀을 실행한 뒤라서예요.")

o = [sec("name-err")] + head(EB1, "이름을 틀리게 적으면 NameError가 나요", BL)
T = 240
ERR = "NameError: name 'Age' is not defined"
o += cell({"id": "c-ne", "lines": ["Age"], "n": 8, "out": [ERR], "err": True}, 96, T, 1100, sel="c-ne")
o.append(underline(1, cx(96, ERR, 17), cx(96, ERR, 22), oy(T, 1, 0) + 22, RED))
o.append(tag(tx(96, [ERR]), oy(T, 1, 0), "모르는 이름이에요", RED, 1))
o.append(fix(96, 470, "Age", "age", 2, after=p(f"font-size:30px;font-weight:700;color:{SUB};margin-left:20px", "대문자와 소문자는 다른 이름이에요")))
o.append(p(f"position:absolute;left:96px;top:640px;font-size:30px;font-weight:700;color:{INK}", "이럴 때도 같은 오류가 나요", bi("fade", 3)))
o += rows(96, 700, 1728, [[txt("철자를 틀렸어요", INK, 30), code("agee", RED)], [txt("넣는 셀을 아직 실행하지 않았어요", INK, 30), txt("넣는 셀부터 실행", SUB, 28)],
                          [txt("Restart 뒤에 아래 셀만 실행했어요", INK, 30), txt("▷ Run All", SUB, 28, 700)]], [900, 780], 3, 76, step=0)
W("name-err", o, "NameError는 파이썬이 모르는 이름을 썼다는 뜻이에요. 파이썬은 대문자와 소문자를 다른 글자로 봐서, age에 값을 넣었어도 Age는 모르는 이름이에요. 철자를 하나 틀려도 같은 오류가 나요. 10에서 본 것처럼 Restart 뒤에 넣는 셀을 건너뛰고 아래 셀만 실행해도 나요. 그럴 땐 Run All로 위에서부터 다시 실행해요. 출력은 Traceback 위쪽 줄을 빼고 마지막 줄만 옮겼어요.")

# ---------- part 2: types ----------
EBT = "2. 변수 타입"
TT = NAVY
o = [sec("types")] + head(EBT, "값마다 타입이 있어요", TT)
T = 214
LT = ["age = 25", "height = 172.5", 'user_name = "kim"', "is_member = False", "print(type(age))", "print(type(height))", "print(type(user_name))", "print(type(is_member))"]
TYPES4 = [("int", "정수 · 소수점 없는 숫자", BL), ("float", "실수 · 소수점 있는 숫자", NAVY), ("str", "문자열 · 따옴표로 감싼 글자", GR), ("bool", "불리언 · True 또는 False", PUR)]
o += cell({"id": "c-ty", "lines": LT, "n": 1, "out": [f"<class '{t[0]}'>" for t in TYPES4]}, 96, T, 1100, sel="c-ty")
for i, (t, d, c) in enumerate(TYPES4):
    o.append(lspot(i + 1, 96 + 85, T, 1100 - 85, 20 + LH * len(LT), T + 10 + i * LH, LH, bar=c))
    o.append(tag(tx(96, LT), ly(T, i), d, c, i + 1))
o.append(lspot_off(5))
o.append(caption("타입은 값의 종류예요. 10에서 본 자료형과 같은 말이에요.", 5))
W("types", o, "변수에 넣는 값에는 종류가 있고, 이 종류를 타입이라고 불러요. 10의 27, 28쪽에서는 자료형이라는 말로 다섯 가지를 type()으로 확인했어요. 이번 챕터에서 계산과 비교에 쓰는 네 가지를 다시 봐요. 정수 int, 실수 float, 문자열 str, 불리언 bool이에요. 리스트는 13에서 따로 배워요. 이 파트도 새 커널이라서 셀 번호가 [1]부터 시작해요. 출력은 hello-uv 커널에서 실제로 실행한 결과예요.", ("types", "변수 타입"))

o = [sec("type-follows")] + head(EBT, "타입은 이름이 아니라 값을 따라가요", TT)
T = 340
LF = ["x = 10", "print(type(x))", 'x = "ten"', "print(type(x))"]
o += cell({"id": "c-tf", "lines": LF, "n": 2, "out": ["<class 'int'>", "<class 'str'>"]}, 96, T, 860, sel="c-tf")
o.append(hl(96, T, 860, 0, 2, "mark", 1))
o.append(hl(96, T, 860, 2, 2, "note", 2))
BX, BY, BW, BH = 1200, 300, 520, 320
o.append(var_box("box-x", "x", '"ten"', BX, BY, TT, BW, BH, vsize=96, vid="v-x").replace('id="v-x"', 'id="v-x" data-start="10"'))
o.append(text(2, "v-x", "&quot;ten&quot;"))
o.append(p(f"position:absolute;left:{BX}px;top:{BY + BH + 30}px;width:{BW}px;height:70px;background:{BG};text-align:center;font-family:{MONO};font-size:44px;font-weight:700;color:{BL}", "int", bi("fade", 1)))
o.append(p(f"position:absolute;left:{BX}px;top:{BY + BH + 30}px;width:{BW}px;height:70px;background:{BG};text-align:center;font-family:{MONO};font-size:44px;font-weight:700;color:{GR}", "str", bi("fade", 2)))
o.append(caption("이름 x는 그대로예요. 넣은 값이 바뀌니 타입도 바뀌었어요.", 3))
W("type-follows", o, "파이썬은 변수를 만들 때 타입을 따로 적지 않아요. 넣은 값을 보고 타입이 정해져요. 그래서 같은 x에 10을 넣으면 int, \"ten\"을 넣으면 str이 돼요. 다른 언어 중에는 변수마다 타입을 정해 두고 다른 값을 못 넣게 하는 언어도 있어요. 파이썬은 자유로운 대신 실수하기 쉬워요. 나이를 넣던 이름에 갑자기 글자를 넣는 일은 피하고, 헷갈리면 type()으로 확인해요.")

o = [sec("quotes")] + head(EBT, "따옴표 하나로 숫자가 글자가 돼요", TT)
T = 240
o += cell({"id": "c-q", "lines": ["print(type(25))", 'print(type("25"))', "print(25 + 1)", 'print("25" + "1")'], "n": 3, "out": ["<class 'int'>", "<class 'str'>", "26", "251"]}, 96, T, 700, sel="c-q")
QX, QS = 900, 64
for i, (ex, r, t, d, c) in enumerate([("25 + 1", "26", "int", "숫자끼리 더해요", BL), ('"25" + "1"', "251", "str", "따옴표가 있으면 글자끼리 이어 붙여요", GR)]):
    y = 280 + i * 300
    o.append(f'<div{bi("rise", i + 1)} style="position:absolute;left:{QX}px;top:{y}px;display:flex;flex-direction:row;align-items:center;gap:30px">'
             + p(f"font-family:{MONO};font-size:{QS}px;font-weight:700;color:{INK};white-space:pre", e(ex)) + arrow(70)
             + p(f"font-family:{MONO};font-size:{QS + 8}px;font-weight:700;color:{c}", r) + '</div>')
    o.append(p(f"position:absolute;left:{QX}px;top:{y + 110}px;font-size:30px;font-weight:700;color:{c}", f'<span style="font-family:{MONO}">{t}</span> · {d}', bi("fade", i + 1)))
o.append(ring(3, QX + 8, 580 + 14, QS * 0.6 * 4 - 16, QS * 1.2 - 16, OR))
o.append(caption("겉모습이 숫자여도 따옴표 안에 있으면 글자예요.", 4))
W("quotes", o, "25와 \"25\"는 화면에서는 비슷해 보여도 타입이 달라요. 따옴표가 없으면 int라서 + 가 더하기가 되고, 따옴표가 있으면 str이라서 + 가 이어 붙이기가 돼요. 그래서 \"25\" + \"1\"은 26이 아니라 251이에요. print는 따옴표를 빼고 보여 줘서 출력만 보면 구분이 안 돼요. 헷갈리면 type()으로 확인해요. 파일에서 읽어 온 숫자는 대부분 글자로 들어와서 실제로 자주 만나는 문제예요. 5파트의 카페 예제에서 다시 만나요.")

o = [sec("convert")] + head(EBT, "int(), float(), str()로 타입을 바꿔요", TT)
T = 240
o += cell({"id": "c-cv", "lines": ['print(int("3") + 3)', 'print(str(3) + "3")', 'print(float("3.5"))', "print(int(3.9))"], "n": 4, "out": ["6", "33", "3.5", "3"]}, 96, T, 700, sel="c-cv")
CVX, CVY, CVR = 900, 250, 150
cv = [('int("3")', "3", "글자를 정수로", BL), ("str(3)", "'3'", "숫자를 글자로", GR), ('float("3.5")', "3.5", "글자를 실수로", NAVY), ("int(3.9)", "3", "소수점 아래는 버려요", OR)]
o += rows(CVX, CVY, 924, [[code(a, INK, 36), code(r, c, 40), txt(d, c, 30, 700)] for a, r, d, c in cv], [330, 150, 372], None, CVR, ["바꾸기", "결과", "뜻"], rid="cvr")
for i in range(4):
    o.append(spot(i + 1, target=f"cvr{i}", pad=10))
o.append(spot_off(5))
o.append(caption("바꾸고 싶은 타입 이름을 함수처럼 쓰고 괄호 안에 값을 넣어요.", 5))
W("convert", o, "타입 이름 int, float, str을 type()처럼 괄호와 함께 쓰면 그 타입으로 바꾼 값을 돌려줘요. int(\"3\")은 글자 3을 정수 3으로 바꿔서 3을 더하면 6이 돼요. str(3)은 반대로 숫자를 글자로 바꿔서 \"3\"과 이어 붙이면 33이에요. int(3.9)는 반올림하지 않고 소수점 아래를 버려서 3이에요. 원래 변수의 값은 그대로이고, 바꾼 값을 쓰려면 age = int(age)처럼 다시 넣어요.")

o = [sec("convert-err")] + head(EBT, "숫자로 못 읽는 글자는 ValueError가 나요", TT)
E1, E2 = "ValueError: invalid literal for int() with base 10: '삼'", "ValueError: invalid literal for int() with base 10: '3.5'"
T1 = 270
T2 = T1 + cell_h({"lines": [1], "out": [1]}) + 44
o += cell({"id": "c-ce1", "lines": ['int("삼")'], "n": 5, "out": [E1], "err": True}, 96, T1, 1728)
o += cell({"id": "c-ce2", "lines": ['int("3.5")'], "n": 6, "out": [E2], "err": True}, 96, T2, 1728, sel="c-ce2", attrs=bi("rise", 2))
o.append(ring(1, cx(96, E1, 52) - 6, oy(T1, 1, 0) - LH / 2, tw("'삼'") + 12, LH, RED))
o.append(tag(tx(96, [E2], 60), oy(T1, 1, 0), "한글 숫자는 못 읽어요", RED, 1))
o.append(ring(2, cx(96, E2, 52) - 6, oy(T2, 1, 0) - LH / 2, tw("'3.5'") + 12, LH, RED))
o.append(tag(tx(96, [E2], 60), oy(T2, 1, 0), "소수점 글자도 못 읽어요", RED, 2))
o.append(fix(96, 660, 'int("3.5")', 'float("3.5")', 3, 46, after=arrow(60) + p(f"font-family:{MONO};font-size:52px;font-weight:700;color:{NAVY}", "3.5")))
o.append(caption("ValueError는 타입은 맞는데 그 값으로는 바꿀 수 없다는 뜻이에요.", 4))
W("convert-err", o, "int()에 숫자로 읽을 수 없는 글자를 넣으면 ValueError가 나요. 메시지의 base 10은 10진수로 읽으려 했다는 뜻이에요. 한글 \"삼\"은 사람에게는 숫자지만 파이썬은 못 읽어요. \"3.5\"처럼 소수점이 있는 글자도 int()는 바로 못 읽어요. 그럴 땐 float(\"3.5\")로 바꿔요. 앞 장의 int(3.9)는 실수를 넣어서 오류 없이 3이 됐어요. 출력은 Traceback의 마지막 줄만 옮겼어요.")

# ---------- part 3: arithmetic ----------
EB2 = "3. 사칙연산"
T2C = TEAL
o = [sec("ops4")] + head(EB2, "더하기, 빼기, 곱하기, 나누기", T2C)
T = 240
L4 = ["print(7 + 3)", "print(7 - 3)", "print(7 * 3)", "print(7 / 3)", "print(6 / 2)"]
o += cell({"id": "c-ops", "lines": L4, "n": 1, "out": ["10", "4", "21", "2.3333333333333335", "3.0"]}, 96, T, 720, sel="c-ops")
o.append(tag(tx(96, ["2.3333333333333335"], 24), oy(T, 5, 3), "끝자리가 조금 어긋나요", OR, 2, 26))
o.append(zoom(2, 181, oy(T, 5, 3) - 40, 900, 80, 30, 2.4))
o.append(zoom_off(3))
o.append(tag(tx(96, ["2.3333333333333335"], 24), oy(T, 5, 4), "나눠떨어져도 .0", NAVY, 3, 26))
ops = [("+", "더하기", "", "7 + 3", "10"), ("-", "빼기", "", "7 - 3", "4"), ("*", "곱하기", "", "7 * 3", "21"), ("/", "나누기", "결과는 늘 실수", "7 / 3", "2.333…")]
o += rows(900, 250, 924, [[code(s, T2C, 64), txt(n_, INK, 32, 700) + (txt(" " + nt, GRAY, 24) if nt else ""), code(ex, INK, 32), code(r, T2C, 34)] for s, n_, nt, ex, r in ops],
          [90, 340, 180, 170], 1, 140, ["기호", "뜻", "예", "결과"], step=0, delay=120)
W("ops4", o, "사칙연산 기호예요. 더하기와 빼기는 수학과 같아요. 키보드에 ×와 ÷가 없어서 곱하기는 별표 *, 나누기는 빗금 / 를 써요. 셀 하나에 print 네 줄을 적어서 네 결과를 한 번에 봤어요. 7 나누기 3은 끝이 2.3333333333333335로 나와요. 컴퓨터가 소수를 저장하는 방식 때문에 마지막 자리가 조금 어긋나요. 지금은 2.333...으로 읽으면 돼요. 나누기 / 의 결과는 나눠떨어져도 항상 실수(float)라서 6 / 2는 3.0이에요. 값은 3과 같지만 타입이 2파트에서 본 float예요. 소수점 없는 몫만 필요하면 다음 장의 // 를 써요. 기호 양옆에 한 칸씩 띄워 적으면 읽기 쉬워요.", ("calc", "사칙연산"))

o = [sec("ops3")] + head(EB2, "몫 //, 나머지 %, 거듭제곱 **", T2C)
o.append(p(f"position:absolute;left:96px;top:226px;font-size:30px;font-weight:700;color:{INK}", "사탕 7개를 3개씩 나누면"))
CS, CG = 88, 14
GW = 3 * CS + 2 * CG + 48
for g in range(2):
    o.append(f'<div{bi("fade", 2)} style="position:absolute;left:{96 + g * (GW + 30)}px;top:290px;width:{GW}px;height:{CS + 48}px;border:4px dashed {T2C};border-radius:26px"></div>')
for i in range(7):
    x = 96 + (i // 3) * (GW + 30) + 24 + (i % 3) * (CS + CG) if i < 6 else 96 + 2 * (GW + 30) + 24
    o.append(f'<x-shape kind="ellipse"{bi("pop", 1)} style="position:absolute;left:{x}px;top:314px;width:{CS}px;height:{CS}px;background:{OR if i == 6 else T2C}"></x-shape>')
o.append(p(f"position:absolute;left:96px;top:450px;width:{2 * GW + 30}px;text-align:center;font-size:32px;font-weight:700;color:{T2C}", "몫 2 <span style='font-weight:500;color:#4A5262'>(묶음 수)</span>", bi("rise", 3)))
o.append(p(f"position:absolute;left:{96 + 2 * (GW + 30) - 40}px;top:450px;width:{CS + 128}px;text-align:center;font-size:32px;font-weight:700;color:{OR}", "나머지 1", bi("rise", 3)))
T = 240
o += cell({"id": "c-ops3", "lines": ["print(7 // 3)", "print(7 % 3)", "print(2 ** 3)"], "n": 2, "out": ["2", "1", "8"]}, 1180, T, 644, sel="c-ops3", attrs=bi("rise", 4))
o += rows(96, 580, 1728, [[code(s, c, 56), txt(n_, INK, 34, 700), code(ex, INK, 32), txt(d, SUB, 28)] for s, n_, ex, d, c in
                          [("//", "몫", "7 // 3  →  2", "나누고 소수점 아래는 버려요", T2C), ("%", "나머지", "7 % 3  →  1", "나누고 남은 수. 퍼센트가 아니에요", OR), ("**", "거듭제곱", "2 ** 3  →  8", "2 × 2 × 2", PUR)]],
          [120, 220, 420, 800], 5, 110, step=0, delay=120)
W("ops3", o, "사칙연산 말고 자주 쓰는 연산 세 가지예요. 사탕 7개를 3개씩 묶으면 두 묶음이 되고 하나가 남아요. 묶음 수 2가 몫이고, 남은 1개가 나머지예요. // 는 빗금 두 개로 몫만 구해요. 소수점 아래를 버리니까 결과가 정수예요. % 는 나머지예요. 퍼센트 기호지만 파이썬에서는 나머지를 구해요. 짝수인지 볼 때 숫자 % 2가 0인지 확인하는 식으로 많이 써요. ** 는 별표 두 개로 거듭제곱이에요. 2 ** 3은 2를 세 번 곱한 8이에요.")

o = [sec("order")] + head(EB2, "곱하기를 더하기보다 먼저 계산해요", T2C)
for k, (code_, rs, cid, n_, out_, x) in enumerate([("2 + 3 * 4", [("2 + " + hs("3 * 4", T2C), "곱하기 먼저"), (hs("2 + 12", T2C), "그다음 더하기"), ("14", "")], "c-o1", 3, "14", 96),
                                                  ("(2 + 3) * 4", [(hs("(2 + 3)", T2C) + " * 4", "괄호 먼저"), (hs("5 * 4", T2C), "그다음 곱하기"), ("20", "")], "c-o2", 4, "20", 984)]):
    o += cell({"id": cid, "lines": [code_], "n": n_, "out": [out_]}, x, 250, 840, attrs=bi("rise", 2) if k else "")
    o += chain(rs, x + 20, 470, 1 + k, 130, 52, step=0, delay=450)
o.append(caption("더하기를 먼저 하고 싶으면 그 부분을 괄호로 묶어요.", 3))
W("order", o, "파이썬도 수학처럼 곱하기와 나누기를 더하기와 빼기보다 먼저 계산해요. 2 + 3 * 4는 3 * 4를 먼저 해서 12, 거기에 2를 더해 14예요. 더하기를 먼저 하고 싶으면 괄호로 묶어요. (2 + 3) * 4는 5 * 4라서 20이에요. 결과를 먼저 예상해 보게 한 뒤 클릭하면 푸는 계단이 차례로 나와요.")

LEVELS = [("( )", "괄호", "가장 먼저", NAVY), ("**", "거듭제곱", "", PUR), ("*  /  //  %", "곱하기, 나누기, 몫, 나머지", "넷은 같은 순위. 몫과 나머지도 여기예요", T2C), ("+  -", "더하기, 빼기", "가장 나중", OR)]
o = [sec("order-ladder")] + head(EB2, "계산 순위는 네 계단이에요", T2C)
for i, (sym, nm, note, c) in enumerate(LEVELS):
    x, y = 96 + i * 170, 226 + i * 170
    o.append(f'<div id="lv{i}"{bi("rise", i + 1)} style="position:absolute;left:{x}px;top:{y}px;width:1220px;height:146px;background:{CARD};border-left:14px solid {c};border-radius:18px;box-shadow:0 1px 0 {LINE},0 10px 24px rgba(29,35,48,.06);padding:0 34px;display:flex;flex-direction:row;align-items:center;gap:30px">'
             + num(i + 1, c, 44) + p(f"width:300px;flex:none;font-family:{MONO};font-size:46px;font-weight:700;color:{c};white-space:pre", e(sym))
             + '<div style="display:flex;flex-direction:column;gap:4px">' + p(f"font-size:34px;font-weight:700;color:{INK}", nm)
             + (p(f"font-size:26px;color:{SUB}", note) if note else "") + '</div></div>')
o.append(pulse(5, "lv2"))
o.append(caption("위 계단부터 풀어요. 같은 계단끼리는 왼쪽부터예요.", 5))
W("order-ladder", o, "파이썬이 계산하는 순서를 네 계단으로 그렸어요. 1단계 괄호가 가장 먼저예요. 2단계는 거듭제곱 ** 예요. 3단계는 곱하기 *, 나누기 /, 몫 //, 나머지 % 네 가지가 같은 순위예요. 몫과 나머지를 따로 떼어 생각하기 쉬운데 곱하기, 나누기와 한 묶음이에요. 4단계가 더하기와 빼기예요. 같은 단계끼리 만나면 왼쪽부터 차례로 풀어요. 예외가 하나 있는데, 2 ** 3 ** 2처럼 거듭제곱끼리는 오른쪽부터 풀어서 3 ** 2 = 9를 먼저 하고 2 ** 9 = 512가 돼요. 이런 식은 괄호로 묶어 쓰는 게 좋아요. 512는 실제로 실행해 확인한 결과예요.")

o = [sec("order-pow")] + head(EB2, "** 는 곱하기와 몫보다 먼저 계산해요", T2C)
o += cell({"id": "c-op", "lines": ["print(2 ** 3 // 3)", "print(2 * 3 ** 2)", "print(-2 ** 2)", "print((-2) ** 2)"], "n": 5, "out": ["2", "18", "-4", "4"]}, 96, 226, 620, sel="c-op")
ex_ = [[(hs("2 ** 3", PUR) + " // 3", "** 먼저"), (hs("8 // 3", T2C), "그다음 몫"), ("2", "")],
       [("2 * " + hs("3 ** 2", PUR), "** 먼저"), (hs("2 * 9", T2C), "그다음 곱하기"), ("18", "")],
       [("-" + hs("2 ** 2", PUR), "** 가 빼기 기호보다 먼저"), ("-4", "")],
       [(hs("(-2)", NAVY) + " ** 2", "괄호 먼저"), ("4", "")]]
st = 1
for k, rs in enumerate(ex_):
    x, y = 800 + (k % 2) * 540, 236 + (k // 2) * 340
    o += chain(rs, x, y, st, 92, 34, step=0, delay=400)
    st += 1
o.append(caption("-2 ** 2는 -4예요. 음수를 거듭제곱하려면 (-2)처럼 괄호로 묶어요.", st))
W("order-pow", o, "거듭제곱은 곱하기와 몫보다 한 단계 위라서 먼저 풀어요. 2 ** 3 // 3은 2 ** 3 = 8을 먼저 하고 8 // 3 = 2예요. 왼쪽부터 3 // 3을 먼저 한다고 생각하면 1이 나와서 틀려요. 2 * 3 ** 2도 3 ** 2 = 9가 먼저라서 18이에요. -2 ** 2는 많이 헷갈려요. 앞의 빼기 기호보다 ** 가 먼저라서 -(2 ** 2) = -4가 돼요. -2를 제곱하고 싶으면 (-2) ** 2처럼 괄호로 묶어서 4를 얻어요. 출력은 같은 셀을 실제로 실행한 결과예요.")

o = [sec("order-same")] + head(EB2, "같은 순위끼리는 왼쪽부터 풀어요", T2C)
o += cell({"id": "c-os", "lines": ["print(10 - 4 + 2)", "print(8 / 2 * 4)", "print(7 // 2 * 2)"], "n": 6, "out": ["8", "16.0", "6"]}, 96, 226, 620, sel="c-os")
same = [([(hs("10 - 4", T2C) + " + 2", "왼쪽 빼기 먼저"), (hs("6 + 2", T2C), ""), ("8", "")], "10 - 6 = 4가 아니에요"),
        ([(hs("8 / 2", T2C) + " * 4", "왼쪽 나누기 먼저"), (hs("4.0 * 4", T2C), ""), ("16.0", "")], "8 / 8 = 1이 아니에요"),
        ([(hs("7 // 2", T2C) + " * 2", "왼쪽 몫 먼저"), (hs("3 * 2", T2C), ""), ("6", "")], "// 와 * 도 같은 순위")]
for k, (rs, warn) in enumerate(same):
    y = 226 + k * 240
    for i, (ex, note) in enumerate(rs):
        last = i == len(rs) - 1
        o.append(f'<div{bi("rise", k + 1)}{DELAY(i * 400)} style="position:absolute;left:{800 + i * 330}px;top:{y}px;display:flex;flex-direction:column;gap:8px">'
                 + mono(ex, 34, T2C if last else INK, TINT[T2C] if last else "#ECEAE3", "align-self:flex-start", raw=True) + (p(f"font-size:22px;font-weight:700;color:{SUB}", e(note)) if note else "") + '</div>')
    o.append(p(f"position:absolute;left:800px;top:{y + 120}px;font-size:26px;font-weight:700;color:{OR}", "⚠ " + e(warn), bi("pop", k + 1) + DELAY(1200)))
o.append(caption("뒤쪽을 먼저 하고 싶으면 그 부분을 괄호로 묶어요.", 4))
W("order-same", o, "같은 계단에 있는 연산끼리 만나면 왼쪽부터 풀어요. 10 - 4 + 2는 10 - 4 = 6을 먼저 하고 6 + 2 = 8이에요. 뒤의 4 + 2를 먼저 하면 4가 나와서 틀려요. 8 / 2 * 4도 8 / 2 = 4.0을 먼저 하고 4를 곱해 16.0이에요. 나누기가 들어가서 결과가 실수예요. 몫 // 도 곱하기와 같은 계단이라 7 // 2 * 2는 7 // 2 = 3을 먼저 하고 2를 곱해 6이에요. 수학 시간에 8 ÷ 2 × 4를 앞에서부터 계산한 것과 같아요. 출력은 같은 셀을 실제로 실행한 결과예요.")

o = [sec("order-mix")] + head(EB2, "섞여 있으면 한 계단씩 풀어요", T2C)
o += cell({"id": "c-om", "lines": ["print(10 - 2 * 3 ** 2 // 4)"], "n": 7, "out": ["6"]}, 96, 220, 1000, sel="c-om")
mix = [("10 - 2 * " + hs("3 ** 2", PUR) + " // 4", "2단계 ** 부터"), ("10 - " + hs("2 * 9", T2C) + " // 4", "3단계, 왼쪽부터"), ("10 - " + hs("18 // 4", T2C), "3단계"),
       (hs("10 - 4", OR), "4단계"), ("6", "")]
o += chain(mix, 96, 410, 1, 104, 42, OR, dim="mix")
o.append(p(f"position:absolute;left:1300px;top:410px;font-size:28px;font-weight:700;color:{GRAY}", "계단 순서"))
for i, (sym, _, _, c) in enumerate(LEVELS):
    o.append(f'<div style="position:absolute;left:1300px;top:{470 + i * 92}px;width:524px;height:80px;display:flex;flex-direction:row;align-items:center;gap:20px;border-bottom:2px solid {LINE};opacity:{0.45 if i == 0 else 1}">'
             + num(i + 1, c, 28) + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:{c};white-space:pre", e(sym)) + (p(f"font-size:24px;color:{GRAY}", "괄호가 없어 건너뛰어요") if i == 0 else "") + '</div>')
o.append(caption("직접 짤 땐 10 - (2 * 3 ** 2) // 4처럼 괄호로 순서를 보여 줘요.", 5))
W("order-mix", o, "네 계단이 모두 섞인 식을 한 단계씩 풀어 봐요. 칠해진 부분이 그 계단에서 계산하는 곳이에요. 괄호가 없으니 2단계 거듭제곱부터예요. 3 ** 2 = 9. 다음은 3단계인데, 곱하기와 몫이 같은 순위라서 왼쪽의 2 * 9 = 18을 먼저 하고 18 // 4 = 4를 해요. 마지막 4단계에서 10 - 4 = 6이에요. 이런 식을 직접 쓸 때는 괄호로 묶어서 읽는 사람이 순서를 바로 알게 해요. 괄호를 쳐도 결과는 같은 6이에요. 출력 6은 셀에서 실제로 실행한 결과예요.")

o = [sec("order-paren")] + head(EB2, "괄호 하나로 답이 달라져요", T2C)
pairs = [("10 + 2 * 3", "16", "(10 + 2) * 3", "36"), ("20 - 10 / 2", "15.0", "(20 - 10) / 2", "5.0"), ("12 / 3 * 2", "8.0", "12 / (3 * 2)", "2.0"), ("100 - 30 - 20", "50", "100 - (30 - 20)", "90"),
         ("2 ** 2 * 3", "12", "2 ** (2 * 3)", "64"), ("17 % 5 * 2", "4", "17 % (5 * 2)", "7"), ("3 + 10 // 3", "6", "(3 + 10) // 3", "4"), ("-3 ** 2", "-9", "(-3) ** 2", "9")]
PY, PR = 220, 82
o.append(f'<div style="position:absolute;left:96px;top:{PY}px;width:1728px;height:50px;display:flex;flex-direction:row;gap:24px;border-bottom:3px solid {INK}">'
         + p(f"width:500px;flex:none;font-size:24px;font-weight:700;color:{GRAY}", "괄호 없이") + p(f"width:300px;flex:none;font-size:24px;font-weight:700;color:{GRAY}", "결과")
         + p(f"width:560px;flex:none;font-size:24px;font-weight:700;color:{T2C}", "괄호를 치면") + p(f"width:200px;flex:none;font-size:24px;font-weight:700;color:{T2C}", "결과") + '</div>')
for i, (a, ra, b, rb) in enumerate(pairs):
    y = PY + 50 + i * PR
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:{PR}px;display:flex;flex-direction:row;align-items:center;gap:24px;border-bottom:2px solid {LINE}">'
             + p(f"width:500px;flex:none;font-family:{MONO};font-size:32px;font-weight:700;color:{INK};white-space:pre", e(a))
             + p(f"width:300px;flex:none;font-family:{MONO};font-size:34px;font-weight:700;color:{INK}", e(ra), bi("fade", 1) + DELAY(i * 110))
             + p(f"width:560px;flex:none;font-family:{MONO};font-size:32px;font-weight:700;color:{T2C};white-space:pre", e(b))
             + p(f"width:200px;flex:none;font-family:{MONO};font-size:34px;font-weight:700;color:{T2C}", e(rb), bi("fade", 2) + DELAY(i * 110)) + '</div>')
o.append(caption("%, // 는 곱하기와 같은 순위, ** 는 그보다 먼저예요.", 3, 966))
W("order-paren", o, "같은 숫자라도 괄호 자리에 따라 결과가 달라져요. 왼쪽 식의 결과를 먼저 예상해 보게 하고 클릭해서 확인해요. 한 번 더 누르면 괄호를 친 식의 결과가 나와요. 위 두 줄은 곱하기, 나누기가 더하기, 빼기보다 먼저라는 규칙이에요. 셋째, 넷째 줄은 같은 순위끼리 왼쪽부터 푼다는 규칙이에요. 12 / 3 * 2를 12 / 6으로 읽으면 2.0이 되는데, 파이썬은 왼쪽부터 12 / 3 = 4.0을 먼저 해요. 아래 네 줄은 거듭제곱, 몫, 나머지가 섞인 식이에요. 17 % 5 * 2는 % 와 * 가 같은 순위라서 왼쪽의 17 % 5 = 2를 먼저 하고 2를 곱해 4예요. -3 ** 2는 앞 장의 -2 ** 2처럼 ** 가 먼저라 -9예요. 열여섯 식은 모두 셀에 print()로 적어 실제로 실행한 결과예요.")

o = [sec("order-quiz")] + head(EB2, "직접 풀어 봐요", T2C)
quiz = [("7 // 2 ** 2", ["2 ** 2 = 4", "7 // 4 = 1"], "1"), ("10 % 3 ** 2", ["3 ** 2 = 9", "10 % 9 = 1"], "1"),
        ("2 + 3 * 4 ** 2 // 8", ["4 ** 2 = 16", "3 * 16 = 48", "48 // 8 = 6", "2 + 6 = 8"], "8"), ("50 - 5 * 2 ** 3 % 7", ["2 ** 3 = 8", "5 * 8 = 40", "40 % 7 = 5", "50 - 5 = 45"], "45")]
o.append(f'<div style="position:absolute;left:959px;top:230px;width:2px;height:680px;background:{LINE}"></div>')
o.append(f'<div style="position:absolute;left:96px;top:566px;width:1728px;height:2px;background:{LINE}"></div>')
for k, (ex, steps, ans) in enumerate(quiz):
    x, y = 96 + (k % 2) * 904, 240 + (k // 2) * 350
    o.append(f'<div style="position:absolute;left:{x}px;top:{y}px;display:flex;flex-direction:row;align-items:center;gap:20px">' + num(k + 1, T2C, 32) + mono(ex, 40) + '</div>')
    o.append(f'<div{bi("fade", k + 1)} style="position:absolute;left:{x + 68}px;top:{y + 96}px;width:740px;display:flex;flex-direction:row;align-items:flex-end;gap:30px">'
             + '<div style="flex:1;display:flex;flex-direction:column;gap:2px">' + "".join(p(f"font-family:{MONO};font-size:26px;line-height:1.45;color:{SUB}", f"{j + 1}. " + e(s_)) for j, s_ in enumerate(steps)) + '</div>'
             + p(f"font-family:{MONO};font-size:64px;font-weight:700;color:{T2C};background:{TINT[T2C]};border-radius:14px;padding:4px 28px", ans) + '</div>')
o.append(caption("셀에 print()로 적고 실행해서 답을 맞춰 봐요.", 5))
W("order-quiz", o, "앞에서 본 계단 순서로 푸는 문제예요. 식을 먼저 보여 주고 잠깐 풀게 한 뒤 클릭하면 푸는 과정과 답이 나와요. 1번과 2번은 ** 가 몫, 나머지보다 먼저라는 점을 확인해요. 3번과 4번은 네 계단이 다 나오는 식이에요. 3번은 4 ** 2 = 16, 3 * 16 = 48, 48 // 8 = 6, 2 + 6 = 8이에요. 4번은 2 ** 3 = 8, 5 * 8 = 40, 40 % 7 = 5, 50 - 5 = 45예요. 네 답은 print(7 // 2 ** 2)처럼 셀에 적어 실제로 실행한 결과예요.")

o = [sec("plus-eq")] + head(EB2, "+= 는 지금 값에 더해서 다시 넣어요", T2C)
T = 240
LP = ["score = 0", "score += 10", "score += 5", "score"]
o += cell({"id": "c-pe", "lines": LP, "n": 11, "out": ["15"]}, 96, T, 720, sel="c-pe")
for i, (v, lbl) in enumerate([("0", "score = 0"), ("10", "score += 10"), ("15", "score += 5")]):
    x = 900 + i * 320
    o.append(hl(96, T, 720, i, 1, "mark", i + 1))
    o.append(f'<div{bi("pop", i + 1)} style="position:absolute;left:{x}px;top:240px;width:250px;display:flex;flex-direction:column;align-items:center;gap:16px">'
             + f'<div style="width:250px;height:200px;background:{CARD};border:3px solid {T2C};border-radius:20px;display:flex;flex-direction:column;overflow:hidden">'
             + p(f"height:54px;flex:none;background:{T2C};color:#FFFFFF;font-family:{MONO};font-size:28px;font-weight:700;line-height:54px;padding:0 18px", "score")
             + f'<div style="flex:1;display:flex;align-items:center;justify-content:center">' + p(f"font-family:{MONO};font-size:64px;font-weight:700;color:{INK}", v) + '</div></div>'
             + p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{SUB};white-space:nowrap", e(lbl)) + '</div>')
    if i:
        o.append(f'<div{bi("fade", i + 1)} style="position:absolute;left:{x - 58}px;top:322px">{arrow(46)}</div>')
EQY = 640
o.append(f'<div style="position:absolute;left:96px;top:{EQY}px;width:1728px;height:2px;background:{LINE}"></div>')
MS = f"position:absolute;left:96px;top:{EQY + 40}px;font-family:{MONO};font-size:64px;font-weight:700;line-height:1.2;white-space:pre;color:{INK}"
PRE = "white-space:pre"
o.append(p(MS, tok("s", "score", PRE) + tok("eq", " = ", PRE) + tok("s2", "score", PRE) + tok("p", " +", PRE) + tok("n", " 10", PRE), ' id="pe-long"' + bi("rise", 4) + MORPH_FROM()))
o.append(p(MS, tok("s", "score", PRE) + tok("p", " +", f"{PRE};color:{T2C}") + tok("eq", "=", f"{PRE};color:{T2C}") + tok("n", " 10", PRE), MORPH(5, "pe-long")))
o.append(p(f"position:absolute;left:820px;top:{EQY + 62}px;font-size:32px;font-weight:700;color:{T2C}", "← score = score + 10을 줄인 모양", bi("fade", 5)))
o.append(p(f"position:absolute;left:96px;top:{EQY + 190}px;font-size:30px;color:{SUB}", "같은 모양으로 <b style='font-family:JetBrains Mono;color:#1D2330'>-=  *=  /=</b> 도 있어요", bi("fade", 5)))
W("plus-eq", o, "+= 는 지금 값에 오른쪽 값을 더해서 같은 이름에 다시 넣어요. 1파트의 age = age + 1을 짧게 적는 방법이에요. score는 0에서 시작해서 10을 더해 10, 5를 더해 15가 돼요. 점수나 합계처럼 값을 쌓아 갈 때 써요. 빼기는 -=, 곱하기는 *=, 나누기는 /= 처럼 기호 뒤에 = 를 붙여요. + 와 = 사이는 띄우지 않고 붙여 적어요.")

o = [sec("str-ops")] + head(EB2, "글자에도 + 와 * 를 써요", T2C)
so = [('"kim" + "lee"', "'kimlee'", "이어 붙여요", T2C), ('"ha" * 3', "'hahaha'", "3번 반복해요", T2C), ('"3" + "3"', "'33'", "따옴표가 있으면 숫자도 글자", OR),
      ('"3" + 3', 'TypeError: can only concatenate str (not "int") to str', "글자와 숫자는 더할 수 없어요", RED)]
SR = 120
o += rows(96, 236, 1728, [[code(a, INK, 36), code(r, c, 36 if i < 3 else 24), txt(d, c, 28, 700)] for i, (a, r, d, c) in enumerate(so)], [380, 860, 420], 1, SR, ["코드", "셀에 적은 결과", ""])
o.append(underline(4, 96 + 380 + 24, 96 + 380 + 24 + tw('TypeError', 24), 236 + 50 + 3 * SR + SR / 2 + 22, RED))
o.append(fix(96, 820, '"3" + 3', 'int("3") + 3', 5, 34, arrow(50) + p(f"font-family:{MONO};font-size:40px;font-weight:700;color:{T2C}", "6")))
W("str-ops", o, "문자열에도 + 와 * 를 쓸 수 있어요. + 는 두 글자를 이어 붙이고, * 는 정수만큼 반복해요. 셀 마지막 줄의 값이라서 출력에 따옴표가 붙었어요. 셋째 줄이 헷갈리기 쉬워요. 따옴표로 감싼 \"3\"은 숫자가 아니라 글자라서 \"3\" + \"3\"은 6이 아니라 '33'이에요. 넷째 줄처럼 글자와 숫자를 더하면 TypeError가 나요. 메시지는 str(문자열)에는 int(정수)를 이어 붙일 수 없다는 뜻이에요. 계산하려면 2파트에서 본 int(\"3\")처럼 숫자로 바꿔요. 출력은 Traceback의 마지막 줄만 옮겼어요.")

# ---------- part 4: comparison and logic ----------
EB3 = "4. 비교와 논리연산"
T3 = PUR
o = [sec("compare")] + head(EB3, "비교하면 답은 True 아니면 False예요", T3)
cmp_ = [(">", "크다", "age > 20", "True"), ("<", "작다", "age < 20", "False"), ("==", "같다", "age == 25", "True"),
        ("!=", "다르다", "age != 25", "False"), (">=", "크거나 같다", "age >= 25", "True"), ("<=", "작거나 같다", "age <= 24", "False")]
o += cell({"id": "c-cmp", "lines": ["age = 25"] + [f"print({c[2]})" for c in cmp_], "n": 1, "out": [c[3] for c in cmp_]}, 96, 214, 660, sel="c-cmp")
o += rows(840, 240, 984, [[code(s, T3, 44), txt(m, INK, 30, 700), code(ex, SUB, 28), tf(r, 28)] for s, m, ex, r in cmp_], [100, 250, 260, 200], 1, 104, ["기호", "뜻", "age = 25일 때", "결과"], step=0, rid="cmpr")
o.append(spot(2, target="cmpr2", pad=10))
o.append(tag(840 + 900, 240 + 50 + 2 * 104 + 52, "= 두 번", T3, 2, 28))
o.append(spot_off(3))
o.append(caption("결과는 2파트에서 본 불리언(bool)이에요.", 3))
W("compare", o, "비교 연산자 여섯 가지예요. 비교한 결과는 맞으면 True, 틀리면 False로 나와요. 2파트에서 본 불리언이에요. 같다는 = 를 두 번 써서 == 로, 다르다는 느낌표와 = 를 붙여 != 로 적어요. 크거나 같다는 >= 처럼 = 를 뒤에 붙여요. => 처럼 순서를 바꾸면 SyntaxError가 나요. 기호 두 개 사이는 띄우지 않아요. age는 25로 넣었어요.", ("logic", "비교와 논리연산"))

o = [sec("eq")] + head(EB3, "= 하나는 넣기, == 두 개는 묻기", T3)
o.append(p(f"position:absolute;left:96px;top:226px;font-size:36px;font-weight:700;color:{T3}", "== 묻기"))
o += cell({"id": "c-eq1", "lines": ["age == 30"], "n": 2, "out": ["False"]}, 96, 290, 840, attrs=bi("rise", 1))
o.append(tag(tx(96, ["age == 30"]), ly(290, 0), "age가 30이냐고 물어요", T3, 1, 26))
o.append(var_box("box-eq1", "age", "25", 96, 520, T3, 400, 260, bi("rise", 1), 80))
o.append(p(f"position:absolute;left:540px;top:620px;font-size:30px;font-weight:700;color:{SUB}", "그대로예요", bi("fade", 1)))
o.append(p(f"position:absolute;left:1004px;top:226px;font-size:36px;font-weight:700;color:{BL}", "= 넣기", bi("fade", 2)))
o += cell({"id": "c-eq2", "lines": ["age = 30", "age"], "n": 3, "out": ["30"]}, 1004, 290, 820, sel="c-eq2", attrs=bi("rise", 2))
o.append(tag(tx(1004, ["age = 30"]), ly(290, 0), "30을 넣어요", BL, 2, 26))
o.append(var_box("box-eq2", "age", "30", 1004, 520, BL, 400, 260, bi("rise", 2), 80))
o.append(p(f"position:absolute;left:1448px;top:620px;font-size:30px;font-weight:700;color:{RED}", "값이 바뀌었어요", bi("fade", 2)))
o.append(caption("비교하려고 = 를 하나만 쓰면 오류 없이 값이 바뀌어요.", 3))
W("eq", o, "= 하나와 == 두 개는 뜻이 완전히 달라서 가장 많이 헷갈려요. = 하나는 1파트에서 본 넣기예요. == 두 개는 같으냐고 묻는 비교예요. 왼쪽 셀은 age가 30인지 물어서 False가 나왔고, age는 25 그대로예요. 오른쪽 셀은 age에 30을 넣어서 값이 바뀌었어요. 비교하려다 = 하나만 적으면 오류 없이 값이 바뀌어서 알아채기 어려워요. 다음 장부터 다시 age를 25로 넣고 시작해요.")

o = [sec("bool-var")] + head(EB3, "비교한 결과도 변수에 넣을 수 있어요", T3)
T = 240
LBv = ["age = 25", "is_adult = age >= 20", "print(is_adult)", "print(type(is_adult))"]
o += cell({"id": "c-bv", "lines": LBv, "n": 4, "out": ["True", "<class 'bool'>"]}, 96, T, 860, sel="c-bv")
o.append(hl(96, T, 860, 1, 1, "mark", 1))
o.append(f'<div{bi("rise", 1)} style="position:absolute;left:1060px;top:250px;display:flex;flex-direction:row;align-items:center;gap:26px">'
         + p(f"font-family:{MONO};font-size:48px;font-weight:700;color:{INK};white-space:pre", "25 >= 20") + arrow(60) + f'<div id="tf-big">{tf("True", 52)}</div></div>')
o.append(var_box("box-adult", "is_adult", "", 1060, 430, T3, 520, 280))
o.append(f'<div data-build-in="fly order 2" data-from="tf-big" style="position:absolute;left:1063px;top:501px;width:514px;height:206px;display:flex;align-items:center;justify-content:center">{tf("True", 64)}</div>')
o.append(p(f"position:absolute;left:96px;top:{T + cell_h({'lines': LBv, 'out': [1, 2]}) + 60:.0f}px;width:860px;font-size:30px;font-weight:700;line-height:1.5;color:{T3}", "True, False를 담는 이름은 is_로 시작하면<br>'~인가요?'로 읽혀요. 10의 is_alive처럼요.", bi("fade", 3)))
o.append(caption("= 오른쪽을 먼저 계산한다는 규칙은 비교에서도 같아요.", 4))
W("bool-var", o, "비교한 결과 True, False도 값이라서 변수에 넣을 수 있어요. is_adult = age >= 20은 1파트의 규칙대로 = 오른쪽을 먼저 계산해요. 25 >= 20은 True라서 is_adult에 True가 들어가요. type()으로 보면 bool이에요. True와 False를 담는 변수는 is_로 시작하면 '~인가요?'라고 읽혀서 뜻이 잘 보여요. age를 다시 25로 넣은 건 앞 장에서 30으로 바꿨기 때문이에요.")


def truth(sid, op, rs, title, cap, notes, n_, hi_row, hi_text):
    o = [sec(sid)] + head(EB3, title, T3)
    o += cell({"id": f"c-{op}", "lines": [f"print({a} {op} {b})" for a, b, _ in rs], "n": n_, "out": [r for _, _, r in rs]}, 96, 240, 700, sel=f"c-{op}")
    o += rows(900, 250, 924, [[tf(a, 30), code(op, T3, 34), tf(b, 30), arrow(44), tf(r, 34)] for a, b, r in rs], [170, 110, 170, 60, 200], 1, 128, ["왼쪽", "", "오른쪽", "", "결과"])
    o.append(box(5, 886, 250 + 50 + hi_row * 128 + 10, 952, 108, OR, 5, 16))
    o.append(p(f"position:absolute;left:900px;top:{250 + 50 + 4 * 128 + 50}px;font-size:30px;font-weight:700;color:{OR}", hi_text, bi("fade", 5)))
    o.append(caption(cap, 5))
    W(sid, o, notes)


truth("and", "and", [("True", "True", "True"), ("True", "False", "False"), ("False", "True", "False"), ("False", "False", "False")],
      "and 는 둘 다 True일 때만 True예요", "하나라도 False면 결과는 False예요.",
      "and는 '그리고'예요. 왼쪽과 오른쪽이 모두 True일 때만 True가 돼요. 네 가지 경우 중에 True는 맨 위 한 줄뿐이에요. True와 False는 첫 글자를 대문자로 적어요. 실제 코드에서는 True, False를 직접 적기보다 age >= 20 같은 비교 결과를 양쪽에 둬요. 5파트의 카페 예제에서 그렇게 써요. 출력은 네 줄을 한 셀에서 실제로 실행한 결과예요.", 5, 0, "True는 이 한 줄뿐이에요")
truth("or", "or", [("True", "True", "True"), ("True", "False", "True"), ("False", "True", "True"), ("False", "False", "False")],
      "or 는 하나만 True여도 True예요", "둘 다 False일 때만 False예요.",
      "or는 '또는'이에요. 둘 중 하나라도 True면 True예요. 네 가지 경우 중에 False는 맨 아래, 둘 다 False인 한 줄뿐이에요. and와 반대로 생각하면 쉬워요. and는 하나만 False여도 False, or는 하나만 True여도 True예요.", 6, 3, "False는 이 한 줄뿐이에요")

o = [sec("not")] + head(EB3, "not 은 True와 False를 뒤집어요", T3)
o += cell({"id": "c-not", "lines": ["print(not True)", "print(not False)"], "n": 7, "out": ["False", "True"]}, 96, 240, 700, sel="c-not")
for i, (a, b) in enumerate([("True", "False"), ("False", "True")]):
    y = 260 + i * 230
    o.append(f'<div{bi("rise", i + 1)} style="position:absolute;left:900px;top:{y}px;width:924px;height:200px;border-bottom:2px solid {LINE};display:flex;flex-direction:row;align-items:center;gap:34px">'
             + p(f"font-family:{MONO};font-size:52px;font-weight:700;color:{T3}", "not") + tf(a, 52) + arrow(90, T3) + tf(b, 52) + '</div>')
o.append(p(f"position:absolute;left:96px;top:520px;width:700px;font-size:30px;font-weight:700;line-height:1.5;color:{T3}", "and, or는 값 두 개 사이에 두고,<br>not은 값 하나 앞에 붙여요.", bi("fade", 3)))
o.append(caption("not 은 '아니다'예요. 바로 뒤의 값을 반대로 바꿔요.", 4))
W("not", o, "not은 뒤에 오는 값 하나를 반대로 바꿔요. not True는 False, not False는 True예요. and와 or는 두 값 사이에 두는데, not은 값 하나 앞에 붙인다는 점이 달라요. is_member가 False일 때 not is_member는 '회원이 아닌가요?'라는 뜻이라서 True가 돼요. 이 예는 5파트의 카페 예제에서 실제로 실행해요.")

o = [sec("ride")] + head(EB3, "놀이기구 탑승 조건을 and로 적어요", T3)
o.append(p(f"position:absolute;left:96px;top:200px;width:1728px;font-size:30px;color:{SUB}", f"조건 · 키 120cm 이상 <b style='color:{T3}'>그리고</b> 7살 이상"))
for k, (h, cid, n_, res, rs, x) in enumerate([("130", "c-r1", 8, "True", [("130 >= 120", "True"), ("9 >= 7", "True"), ("True and True", "True")], 96),
                                              ("110", "c-r2", 9, "False", [("110 >= 120", "False"), ("9 >= 7", "True"), ("False and True", "False")], 984)]):
    lines = [f"height = {h}", "age = 9", "height >= 120 and age >= 7"] if k == 0 else [f"height = {h}", "height >= 120 and age >= 7"]
    o += cell({"id": cid, "lines": lines, "n": n_, "out": [res]}, x, 270, 840, sel=cid if k else None, attrs=bi("rise", 2) if k else "")
    for i, (ex, r) in enumerate(rs):
        o.append(f'<div{bi("rise", 1 + k)}{DELAY(300 + i * 350)} style="position:absolute;left:{x}px;top:{540 + i * 96}px;width:840px;height:84px;display:flex;flex-direction:row;align-items:center;gap:22px;border-bottom:2px solid {LINE}">'
                 + p(f"width:380px;flex:none;font-family:{MONO};font-size:34px;font-weight:700;color:{INK};white-space:pre", e(ex)) + arrow(44) + tf(r, 32) + '</div>')
    ok = res == "True"
    o.append(p(f"position:absolute;left:{x}px;top:850px;font-size:34px;font-weight:700;color:{GR if ok else RED}", "탈 수 있어요" if ok else "키가 모자라서 못 타요", bi("pop", 1 + k) + DELAY(1500)))
o.append(underline(3, 984 + 105, 984 + 105 + tw("height >= 120"), ly(270, 1) + 22, RED))
W("ride", o, "키가 120cm 이상이고 7살 이상이어야 탈 수 있는 놀이기구예요. 두 조건을 모두 만족해야 하니까 and로 이어요. 왼쪽은 키 130, 나이 9살이라서 비교 두 개가 모두 True, True and True는 True예요. 오른쪽은 키만 110으로 다시 넣었어요. age는 앞 셀의 9가 그대로 남아 있어요. 110 >= 120이 False라서 나이가 맞아도 결과는 False예요. 비교를 먼저 하고 and를 나중에 해서 괄호가 없어도 돼요. 조건을 모두 만족해야 하면 and예요.")

o = [sec("logic-order")] + head(EB3, "계산, 비교, not, and, or 순서로 풀어요", T3)
o += cell({"id": "c-lo", "lines": ["2 + 3 > 4 and not False"], "n": 10, "out": ["True"]}, 96, 220, 1000, sel="c-lo")
lo = [(hs("2 + 3", TEAL) + " > 4 and not False", "1 계산"), (hs("5 > 4", PUR) + " and not False", "2 비교"), ("True and " + hs("not False", PUR), "3 not"), (hs("True and True", PUR), "4 and"), ("True", "")]
o += chain(lo, 96, 410, 1, 104, 40, PUR, dim="lo")
o.append(p(f"position:absolute;left:1300px;top:410px;font-size:28px;font-weight:700;color:{GRAY}", "먼저 하는 순서"))
for i, (t, d) in enumerate([("+ - * /", "계산"), ("> == !=", "비교"), ("not", "뒤집기"), ("and", "그리고"), ("or", "또는")]):
    o.append(f'<div style="position:absolute;left:1300px;top:{466 + i * 86}px;width:524px;height:76px;display:flex;flex-direction:row;align-items:center;gap:20px;border-bottom:2px solid {LINE}">'
             + num(i + 1, T3, 26) + p(f"width:200px;flex:none;font-family:{MONO};font-size:30px;font-weight:700;color:{T3};white-space:pre", e(t)) + p(f"font-size:26px;color:{SUB}", d) + '</div>')
o.append(caption("헷갈리면 (age >= 20) and (age < 30)처럼 괄호로 묶어요.", 5))
W("logic-order", o, "여러 연산이 섞이면 계산, 비교, not, and, or 순서로 풀어요. 계산이 가장 먼저라서 2 + 3이 5가 돼요. 그다음 비교로 5 > 4가 True가 돼요. 그다음 not False가 True가 되고, 마지막에 True and True가 True예요. and와 or가 섞이면 and를 먼저 해요. 순서를 외우지 않아도 괄호로 묶으면 그 안을 먼저 계산해요. 예를 들어 age = 25일 때 age >= 20 and age < 30은 20대인지 묻는 식이고 True가 나와요. 출력은 같은 셀을 실제로 실행한 결과예요.")

# ---------- part 5: cafe examples ----------
EB5 = "5. 카페 주문으로 풀어 보기"
o = [sec("ex-order")] + head(EB5, "가격에 이름을 붙이면 한 줄만 고쳐요", CAFE)
T1 = 214
L1 = ["americano = 4500", "latte = 5000", "total = americano * 2 + latte", "paid = 20000", 'print("합계:", total)', 'print("잔돈:", paid - total)']
o += cell({"id": "c-ex1", "lines": L1, "n": 1, "out": ["합계: 14000", "잔돈: 6000"]}, 96, T1, 1100, sel="c-ex1")
T2 = T1 + cell_h({"lines": L1, "out": [1, 2]}) + 36
L2 = ["americano = 4800", "total = americano * 2 + latte", 'print("합계:", total)', 'print("잔돈:", paid - total)']
o += cell({"id": "c-ex2", "lines": L2, "n": 2, "out": ["합계: 14600", "잔돈: 5400"]}, 96, T2, 1100, sel="c-ex2", attrs=bi("rise", 3))
TXX = 96 + 1100 + 34
o.append(hl(96, T1, 1100, 0, 2, "mark", 1))
o.append(tag(TXX, ly(T1, 0.5), "가격은 맨 위에 한 번만", CAFE, 1))
o.append(hl(96, T1, 1100, 2, 1, "mark", 2))
o.append(tag(TXX, ly(T1, 2), "이름으로 읽히는 식", CAFE, 2))
o.append(tag(TXX, oy(T1, 6, 0.5), "앞의 숫자 식과 같은 답", GRAY, 2, 26))
o.append(hl(96, T2, 1100, 0, 1, "note", 4))
o.append(tag(TXX, ly(T2, 0), "가격이 오르면 이 줄만", OR, 4))
o.append(tag(TXX, oy(T2, 4, 0.5), "합계와 잔돈이 같이 바뀌어요", OR, 5))
o = [x.replace('>americano = 4800<', f'>americano = <span{MARK(4)} style="color:{OR};background:{TINT[OR]};border-radius:6px">4800</span><', 1) for x in o]
o = [x.replace('">합계: 14600</p>', '"' + COUNT(3) + '>합계: 14600</p>', 1) for x in o]
W("ex-order", o, "처음 장에서 숫자로만 적었던 카페 계산을 변수로 다시 적었어요. 아메리카노와 라떼 가격을 맨 위에서 한 번만 넣고, 합계는 americano * 2 + latte처럼 이름으로 계산해요. 3파트의 계산 순서대로 곱하기를 먼저 해서 9000에 5000을 더해 14000이에요. 잔돈은 낸 돈 paid에서 합계를 빼요. 아메리카노가 4800원으로 오르면 2번 셀처럼 가격 줄만 다시 넣고 합계 식을 다시 실행해요. latte와 paid는 1번 셀에서 넣은 값이 그대로 남아 있어요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요. 출력은 hello-uv 커널에서 실제로 실행한 결과예요.", ("cafe", "카페 주문으로 풀어 보기"))

o = [sec("ex-split")] + head(EB5, "글자로 온 수량을 숫자로 바꿔 나눠 내요", CAFE)
T1 = 214
L1 = ['qty = "3"', "total = 4500 * int(qty) + 5000", "people = 3", 'print("합계:", total)', 'print("한 사람:", total // people)', 'print("남는 돈:", total % people)']
o += cell({"id": "c-ex3", "lines": L1, "n": 3, "out": ["합계: 18500", "한 사람: 6166", "남는 돈: 2"]}, 96, T1, 1100, sel="c-ex3")
TXX = 96 + 1100 + 34
o.append(hl(96, T1, 1100, 0, 1, "note", 1))
o.append(tag(TXX, ly(T1, 0), "주문서에서 읽은 수량은 글자예요", OR, 1))
o.append(hl(96, T1, 1100, 1, 1, "mark", 2))
o.append(tag(TXX, ly(T1, 1), "int()로 바꿔서 곱해요 (2파트)", CAFE, 2))
o.append(tag(TXX, oy(T1, 6, 1), "몫 // 로 한 사람 몫", TEAL, 3))
o.append(tag(TXX, oy(T1, 6, 2), "나머지 % 로 남는 돈", TEAL, 3))
T2 = T1 + cell_h({"lines": L1, "out": [1, 2, 3]}) + 36
E = "TypeError: unsupported operand type(s) for +: 'int' and 'str'"
o += cell({"id": "c-ex4", "lines": ['qty = "3"', "print(5000 + qty)"], "n": 4, "out": [E], "err": True}, 96, T2, 1100, attrs=bi("rise", 4))
o.append(tag(TXX, ly(T2, 1), "int()를 빼면 이렇게 돼요", RED, 4))
o.append(underline(4, cx(96, E, 0), cx(96, E, 9), oy(T2, 2, 0) + 22, RED))
o = [x.replace(f'>{e(E)}</p>', f' id="err-ex4">{e(E)}</p>', 1) if e(E) in x else x for x in o]
o.append(shake(5, "err-ex4"))
W("ex-split", o, "주문서 파일에서 읽어 온 수량은 숫자처럼 보여도 글자인 경우가 많아요. 그래서 qty에 따옴표로 감싼 \"3\"을 넣었어요. 계산하려면 2파트의 int()로 정수로 바꿔요. 아메리카노 세 잔과 라떼 한 잔이라 4500 * 3 + 5000 = 18500이에요. 세 사람이 나눠 내면 3파트의 몫 // 로 한 사람이 낼 6166원, 나머지 % 로 남는 2원을 구해요. 아래 셀처럼 int() 없이 숫자와 글자를 더하면 TypeError가 나요. 메시지는 + 의 양쪽이 int와 str이라 더할 수 없다는 뜻이에요. 출력은 hello-uv 커널에서 실제로 실행한 결과예요.")

o = [sec("ex-discount")] + head(EB5, "사이즈 업과 할인 조건을 and, or로 적어요", CAFE)
o.append(p(f"position:absolute;left:96px;top:196px;width:1728px;font-size:28px;color:{SUB}", f"사이즈 업 · 15000원 이상 <b style='color:{PUR}'>그리고</b> 쿠폰 있음 &#160;&#160;|&#160;&#160; 할인 · 회원 <b style='color:{PUR}'>또는</b> 50000원 이상"))
T = 260
L = ["is_member = False", "has_coupon = True", "total = 18500", "size_up = total >= 15000 and has_coupon", "discount = is_member or total >= 50000",
     'print("사이즈 업:", size_up)', 'print("할인:", discount)', 'print("비회원:", not is_member)']
o += cell({"id": "c-ex5", "lines": L, "n": 5, "out": ["사이즈 업: True", "할인: False", "비회원: True"]}, 96, T, 1100, sel="c-ex5")
TXX = 96 + 1100 + 34
o.append(hl(96, T, 1100, 3, 1, "mark", 1))
o.append(tag(TXX, ly(T, 3), "True and True", PUR, 1))
o.append(tag(TXX, oy(T, 8, 0), "둘 다 맞아서 True", GR, 2))
o.append(hl(96, T, 1100, 4, 1, "mark", 3))
o.append(tag(TXX, ly(T, 4), "False or False", PUR, 3))
o.append(tag(TXX, oy(T, 8, 1), "하나도 안 맞아서 False", RED, 4))
o.append(hl(96, T, 1100, 7, 1, "mark", 5))
o.append(tag(TXX, oy(T, 8, 2), "not False · 회원이 아닌가요?", PUR, 5))
W("ex-discount", o, "카페의 두 가지 혜택을 조건으로 적었어요. 사이즈 업은 15000원 이상이고 쿠폰도 있어야 해서 and로 이어요. 18500 >= 15000이 True, has_coupon이 True라서 True and True는 True예요. 할인은 회원이거나 50000원 이상이면 돼서 or로 이어요. 회원이 아니고 18500원이라 False or False는 False예요. 4파트의 순서대로 비교를 먼저 하고 and, or를 나중에 해서 괄호가 없어도 돼요. not is_member는 '회원이 아닌가요?'라는 질문이라 True예요. True, False를 담는 이름은 is_, has_로 시작하면 질문처럼 읽혀요. 출력은 hello-uv 커널에서 실제로 실행한 결과예요.")

# ---------- summary ----------
EBS = "정리"
o = [sec("trouble")] + head(EBS, "막히면 오류의 마지막 줄을 봐요", RED)
tr = [("NameError: name 'Age' is not defined", "대문자, 소문자를 다르게 적었거나 넣는 셀을 안 돌렸어요", "철자 확인, Run All"),
      ("NameError: name 'true' is not defined", "True, False는 첫 글자가 대문자예요", "True  False"),
      ('TypeError: can only concatenate str (not "int") to str', "따옴표 글자와 숫자를 더했어요", 'int("3") + 3'),
      ("ValueError: invalid literal for int() with base 10: '삼'", "int()가 숫자로 못 읽는 글자예요", "소수 글자는 float()"),
      ("ZeroDivisionError: division by zero", "0으로 나눴어요", "나누는 수 확인"),
      ("비교했는데 값이 바뀌었어요", "= 를 하나만 썼어요", "== 두 개")]
o += rows(96, 210, 1728, [[f'<div style="display:flex;flex-direction:column;gap:4px">' + (code(q, INK, 24) if "Error" in q else txt(q, INK, 28, 700)) + txt(a_, SUB, 24) + '</div>', code(cmd, INK, 26)] for q, a_, cmd in tr],
          [1300, 380], 1, 118, ["마지막 줄", "고치기"], step=0, delay=110)
W("trouble", o, "오류 메시지는 길어도 맨 아래 한 줄에 원인이 있어요. 1번과 2번은 NameError예요. 이름 철자, 대소문자, True와 False의 첫 글자를 봐요. 3번은 따옴표로 감싼 글자와 숫자를 더했을 때예요. int()로 타입을 맞춰요. 4번은 int()가 숫자로 못 읽는 글자를 받았을 때예요. 5번은 0으로 나눴을 때예요. 6번은 오류 없이 값만 바뀌어서 알아채기 어려워요. 6 / 2가 3.0으로 나오는 건 3파트의 나누기 장을 봐요. 위 메시지는 모두 hello-uv 커널에서 실제로 실행한 결과의 마지막 줄이에요.", ("trouble", "정리"))

o = [f'<section id="cheatsheet" data-transition="fade" style="background:{BG};color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>']
cheat = [("값에 이름 붙이기", "price = 4500", BL), ("값 보기", 'print("합계:", total)', BL), ("타입 확인", "type(price)", NAVY), ("타입 바꾸기", 'int("3")  str(3)', NAVY),
         ("계산하기", "+  -  *  /  //  %  **", TEAL), ("먼저 할 계산", "(2 + 3) * 4", TEAL), ("값 쌓기", "score += 10", TEAL), ("비교하기", "==  !=  >  <  >=  <=", PUR)]
for col in range(2):
    o += rows(96 + col * 904, 200, 824, [[txt(w_, INK, 30, 700), code(c_, c, 30)] for w_, c_, c in cheat[col * 4:col * 4 + 4]], [300, 500], None, 104, ["하고 싶은 것", "코드"])
o.append(f'<div style="position:absolute;left:96px;top:700px;width:1728px;display:flex;flex-direction:column;gap:18px">'
         + p(f"font-size:32px;font-weight:700;color:{INK}", f'<span style="font-family:\'JetBrains Mono\';color:{PUR}">and</span> 둘 다 True · <span style="font-family:\'JetBrains Mono\';color:{PUR}">or</span> 하나라도 True · <span style="font-family:\'JetBrains Mono\';color:{PUR}">not</span> 뒤집기')
         + p(f"font-size:32px;font-weight:700;color:{INK}", '푸는 순서는 괄호, 계산, 비교, not, and, or <span style="font-weight:500;color:' + SUB + '">· 헷갈리면 괄호로 묶어요</span>') + '</div>')
o.append(p(f"position:absolute;left:96px;top:900px;width:1728px;font-size:30px;font-weight:700;color:{CAFE}", "다음 13에서는 문자열을 자르고, 주문 여러 개를 리스트에 담아요."))
W("cheatsheet", o, "이번 챕터에서 쓴 기호와 함수를 한 장에 모았어요. = 는 넣기, == 는 묻기라는 것만은 꼭 기억해요. 노트북에 이 장의 내용을 마크다운 셀로 정리해 두면 복습할 때 같이 봐요. 다음 13 챕터에서는 문자열을 다루고, 주문 여러 개를 리스트에 담아 for로 영수증을 찍어요.")

# ---------- toc ----------
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
parts = [("0", INK, "들어가기", "왜 변수가 필요한지, 큰 그림, 노트북 준비", "why", "ready"),
         ("1", BL, "변수에 값 넣기", "= 로 넣기, 값 보기, 다시 넣기, NameError", "assign", "name-err"),
         ("2", NAVY, "변수 타입", "int, float, str, bool, type(), 타입 바꾸기", "types", "convert-err"),
         ("3", TEAL, "사칙연산", "+ - * /, 몫과 나머지, 계산 순서, +=, 글자 연산", "ops4", "str-ops"),
         ("4", PUR, "비교와 논리연산", "비교 여섯 가지, = 와 ==, and, or, not", "compare", "logic-order"),
         ("5", CAFE, "카페 주문으로 풀어 보기", "합계와 잔돈, 나눠 내기, 할인 조건", "ex-order", "ex-discount"),
         ("", RED, "정리", "막힐 때, 한 장 요약", "trouble", "cheatsheet")]
TOC_NOTE = "다섯 파트는 앞 파트를 그대로 이어서 써요. 1파트의 = 로 넣는 법과 2파트의 타입을 뒤 파트에서 계속 써요. 3파트는 숫자 계산, 4파트는 True와 False로 답하는 비교와 논리연산이에요. 5파트는 앞의 네 파트를 섞어 카페 주문 계산을 풀어요. 셀은 위에서부터 차례로 실행해요."
DECK_TITLE = "파이썬 기초 1 (변수, 타입, 연산)"
t = [f'<section id="toc" data-transition="fade" style="background:{BG};color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>']
for i, (n_, c, h, s, a, b) in enumerate(parts):
    y = 196 + i * 116
    t.append(f'<div{bi("rise", 1)}{DELAY(i * 90)} style="position:absolute;left:96px;top:{y}px;width:1728px;height:108px;display:flex;flex-direction:row;align-items:center;gap:30px;border-bottom:2px solid {LINE}">'
             + p(f"width:60px;flex:none;font-size:52px;font-weight:900;color:{c};text-align:center", n_)
             + p(f"width:480px;flex:none;font-size:34px;font-weight:700;color:{INK}", h)
             + p(f"flex:1;font-size:28px;color:{SUB}", e(s))
             + p(f"font-size:28px;font-weight:700;color:{GRAY};white-space:nowrap", f"{page[a]}–{page[b]}쪽") + '</div>')
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(t) + f"\n<aside>{e(TOC_NOTE)}</aside>\n</section>\n")

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-02T03:00:00Z"}, "lists": "css", "title": DECK_TITLE, "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
print(len(ORDER), "slides")
