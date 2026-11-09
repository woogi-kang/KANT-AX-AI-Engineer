"""Generates every slide of the list comprehension deck (23) and slides/deck.json.

Story: keeps writing in basics.ipynb from chapters 12-22. Starts from the long for-and-append block and the nested
map/lambda of chapter 21, moves the value, the for and the if into the brackets, then the three ways side by side,
reading order, an if at the end (keep), an if-else in front (change), strings, range, tuples, dictionary and set
comprehensions, sum, max and sorted with comprehensions, and when a plain for reads better (a nested comprehension is
shown for reading only). Part 5 collects the usual errors, and part 6 makes a receipt, a stock board and a score sheet.
Every cell and output comes from tools/demo.sh (tools/run_nb.py runs the cells with the project kernel).

Layout rules (2026-11-08 remake, from the Stageshow skill: github.com/benjitaylor/skills):
1. one focal object per slide (a notebook cell at 30px or one dark code strip); the rest small and quiet
2. terms are labelled on the code line or the picture with leader tags, not in separate cards
3. say it once: what the speaker notes say does not repeat in cards
4. no empty bands: the focal object grows, or the payoff gets the room
5. values move instead of swapping (fly), and a fix is the wrong line struck through beside the right one
Highlights come from tools/HIGHLIGHT.md, as many kinds as fit: slam and shine on the cover, staggered rows (delay), line tint,
line spotlight, fly, spotlight, pen ring/underline/box, shake on a failure, code morph, zoom, paired colors (mark),
count-up, run band. No typing effect.
Usage: python3 tools/gen.py slides
"""

import html, json, os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from highlight import (spot, spot_off, cursor, cursor_off, ring, box, underline, lspot, lspot_off, run, run_off, zoom, zoom_off,
                       shine, shake, SLAM, COUNT, MARK, DELAY, MORPH, MORPH_FROM, tok)

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
INK, SUB, LINE, CARD = "#1D2330", "#4A5262", "#E1DED6", "#FFFFFF"
BL, GR, OR, PUR, RED, TEAL, GRAY = "#2459C9", "#1F8A4C", "#B26A00", "#5A3BB8", "#A33131", "#0F7C86", "#6A7180"
JP = "#B8560F"          # Jupyter, same as chapters 09 and 10
SEL = "#2F7DE1"         # selected cell bar, like VS Code's focus color
NB = "basics.ipynb"
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


EB1 = "1. 왜 필요한가"
EB2 = "2. 만들기와 고르기"
EB3 = "3. 여러 데이터에 쓰기"
EB4 = "4. 함수와 함께 쓰기"
EB5 = "5. 오류와 함정"
EB6 = "6. 실습"
PR4 = "prices = [4500, 5000, 6500, 3000]"
NEWK = " 이 파트는 새 커널이라 셀 번호가 [1]부터예요."


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


# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#F2B27A;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
       f'<h1{SLAM(1)} style="font-size:92px;font-weight:900;line-height:1.1;color:#F6F5F1">리스트<br>컴프리헨션</h1>',
       '<p style="font-size:40px;line-height:1.4;color:#BFC6D4">바꾸고 고르는 for를<br>대괄호 한 줄로 쓰기</p>',
       f'<div id="cov-code" style="position:absolute;left:900px;top:300px;width:900px;height:480px;background:{DARK};border-radius:24px;padding:44px 48px;display:flex;flex-direction:column;justify-content:center;gap:16px">']
for line, c in [(PR4, W_), ("", W_), ("[p + 500 for p in prices]", CF), ("# [5000, 5500, 7000, 3500]", "#9AA1AE"), ("", W_), ("[p for p in prices if p >= 5000]", CK), ("# [5000, 6500]", "#9AA1AE")]:
    cov.append(p(f"font-family:{MONO};font-size:30px;font-weight:700;line-height:1.45;color:{c};white-space:pre", e(line) if line else "&#160;"))
cov.append('</div>')
cov.append(shine(2, "cov-code"))
W("cover", cov, "21에서 map과 filter로 한 일을 대괄호 안의 for 한 줄로 써요. 이 모양을 리스트 컴프리헨션이라고 불러요. lambda 없이 읽혀서 파이썬에서 가장 자주 보는 모양이에요. 딕셔너리와 집합도 같은 모양으로 만들고, 22의 sorted, max와 함께 써요.", ("intro", "들어가기"))
ORDER.append("toc")

# ---------- ready ----------
o = [sec("ready")] + head("들어가기", "22에서 이어서 해요", JP)
for i, (a_, b_) in enumerate([("리스트, 튜플, for, append, join", "13"), ("딕셔너리 items(), 집합", "15, 16"), ("if, 한 줄 if else", "17"), ("range()", "18"), ("lambda, map, filter, key=", "21, 22")]):
    o.append(f'<div data-build-in="rise order 1"{DELAY(i * 90)} style="position:absolute;left:96px;top:{220 + i * 120}px;width:800px;height:104px;display:flex;flex-direction:row;gap:24px;align-items:center;border-bottom:2px solid {LINE}">'
             + f'<x-icon name="CheckCircle" style="width:48px;height:48px;color:{GR}"></x-icon>'
             + p(f"flex:1;font-size:34px;font-weight:700;color:{INK}", e(a_))
             + p(f"font-size:30px;font-weight:700;color:{GRAY}", e(b_)) + '</div>')
o.append(p(f"position:absolute;left:1000px;top:246px;font-size:36px;font-weight:700;color:{JP}", "노트북 다시 열기", rise(2)))
steps_ = [p(f"font-size:32px;color:{INK}", "VS Code로 hello-uv 폴더 열기"),
          p(f"font-size:32px;color:{INK}", "탐색기에서") + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{JP}", NB) + p(f"font-size:32px;color:{INK}", "열기"),
          p(f"font-size:32px;color:{INK}", "오른쪽 위 커널이 .venv인지 보기"),
          p(f"font-size:32px;color:{INK}", "셀에 적고") + kbd("Shift+Enter", 26) + p(f"font-size:32px;color:{INK}", "로 실행")]
for i, inner in enumerate(steps_):
    o.append(f'<div data-build-in="rise order 2"{DELAY(90 + i * 90)} style="position:absolute;left:1000px;top:{342 + i * 120}px;width:824px;height:104px;display:flex;flex-direction:row;align-items:center;gap:18px">' + num(i + 1, JP) + inner + '</div>')
o.append(caption("기억이 안 나면 왼쪽에 적힌 챕터를 먼저 다시 봐요.", 880, 3))
W("ready", o, "12부터 쓰던 basics.ipynb에 이어서 적어요. 09에서 만든 hello-uv 폴더를 VS Code로 열고 노트북을 열어요. 13의 for와 append, 17의 if와 한 줄 if else, 18의 range를 대괄호 안에 넣어요. 21의 map, filter와 나란히 비교하고, 22의 sorted, max와 함께 써요. 슬라이드의 출력은 tools/demo.sh가 hello-uv 커널에서 같은 셀을 실제로 실행한 결과예요. 셀 번호는 파트마다 [1]부터 다시 셌어요.")

# ---------- part 1 ----------
o = [sec("c-why")] + head(EB1, "for는 길고, map은 lambda까지 읽어야 해요", K1)
T, FW = 210, 1180
WHY = ["prices = [4500, 5000, 6500]", "up = []", "for p in prices:", "    up.append(p + 500)", "print(up)", "print(list(map(lambda p: p + 500, prices)))"]
o += cell({"id": "c-why1", "lines": WHY, "n": 1, "out": ["[5000, 5500, 7000]", "[5000, 5500, 7000]"]}, 96, T, FW, sel="c-why1")
TX = 96 + FW + 30
o.append(hl(96, T, FW, 1, 3, "mark", 1)); o.append(tag(TX, ly(T, 2), "세 줄을 매번 적어요", BL, 1))
o.append(hl(96, T, FW, 5, 1, "skip", 2)); o.append(tag(TX, ly(T, 5), "괄호를 풀어 가며 읽어요", GRAY, 2))
o.append(strip(96, 720, 1728, 170, [seg([("[", W_), ("p + 500", CV), (" ", W_), ("for p in prices", CF), ("]", W_)], 56)], rise(3), 60))
o.append(p(f"position:absolute;left:1066px;top:776px;font-size:32px;font-weight:700;line-height:1.8;color:{W_};white-space:nowrap", "← 한 줄인데 for처럼 읽혀요", rise(3)))
W("c-why", o, "for는 세 줄을 매번 적고, map은 lambda까지 풀어 읽어야 해요. 21의 장면으로 돌아가 모든 가격에 500원을 더해요. for와 append로 쓰면 읽기는 쉬운데 빈 리스트, for, append를 매번 적어요. map과 lambda로 쓰면 한 줄이지만 list 안의 map, map 안의 lambda를 차례로 풀어야 해요. 아래 줄처럼 대괄호 안에 for를 넣으면 한 줄로 쓰면서 for처럼 읽혀요. 이 모양이 리스트 컴프리헨션이에요." + NEWK + REAL, ("p1", "왜 필요한가"))

o = [sec("c-big")] + head(EB1, "for의 세 조각을 대괄호 안으로 옮겨 적어요", K1)
o.append(label(96, 206, "for로 쓰면", GRAY, 30))
o.append(label(916, 206, "컴프리헨션으로 쓰면", K1, 30))
FS = 44
o.append(strip(96, 260, 780, 560, [seg([("up = []", W_)], FS), seg([("for p in prices:", CF, ' id="cb-f"')], FS), seg([("    ", W_), ("if p >= 5000:", CI, ' id="cb-i"')], FS),
                                    seg([("        up.append(", W_), ("p + 500", CV, ' id="cb-v"'), (")", W_)], FS)], "", 48))
FS2 = 48
o.append(strip(916, 260, 908, 560, [seg([("up = [", W_), ("p + 500", CV, ' id="cc-v"' + fly(1, "cb-v"))], FS2),
                                     seg([("      ", W_), ("for p in prices", CF, ' id="cc-f"' + fly(2, "cb-f"))], FS2),
                                     seg([("      ", W_), ("if p >= 5000", CI, ' id="cc-i"' + fly(3, "cb-i")), ("]", W_, fade(3))], FS2)], "", 48))
TXB = 916 + 48 + 21 * FS2 * 0.6 + 40
YB = 260 + 280 - 1.5 * FS2 * 1.5   # centre of the first of three lines
for k, (t, c) in enumerate([("① 넣을 값", CV), ("② 꺼내기", CF), ("③ 고르기", CI)]):
    o.append(tag(TXB, YB + FS2 * 1.5 * (k + 0.5), t, c, k + 1, 28))
o.append(caption("빈 리스트와 append는 대괄호가 맡고, for와 if의 콜론은 빼요.", 900, 4))
W("c-big", o, "for 문의 세 조각을 대괄호 안으로 옮기면 컴프리헨션이 돼요. 초록색은 append 괄호 안의 넣을 값, 청록색은 하나씩 꺼내는 for, 빨간색은 고르는 if예요. 넣을 값을 맨 앞에 적고, 그 뒤에 for와 if를 콜론 없이 이어 적어요. 빈 리스트와 append는 대괄호가 대신해요. if 조각은 고를 때만 붙여요. 한 줄로 적어도 되는데 그림에서는 조각이 보이게 세 줄로 나눴어요.")

o = [sec("c-min")] + head(EB1, "가장 짧은 컴프리헨션: 값마다 10 더하기", K1)
T = 210
o += cell({"id": "c-min1", "lines": ["numbers = [1, 2, 3]", "print([x + 10 for x in numbers])"], "n": 2, "out": ["[11, 12, 13]"]}, 96, T, 1728, sel="c-min1")
o.append(tag(tx(96, ["[11, 12, 13]"], out=True), oy(T, 2, 0), "21의 list(map(lambda x: x + 10, numbers))와 같아요", GRAY, 5, 28))
BY, BW, BH = 540, 210, 190
o.append(label(96, BY - 56, "numbers", GRAY, 30, "", True))
o += boxes(["1", "2", "3"], 96, BY, BW, BH, GRAY, "#F1F0EC", True, 72, 20, ids=["cm-a", "cm-b", "cm-c"])
o.append(p(f"position:absolute;left:836px;top:{BY + 50}px;width:248px;text-align:center;font-family:{MONO};font-size:36px;font-weight:700;color:{LV}", "x + 10", fade(1)))
o.append(arrow(200, LV, fade(1), f"position:absolute;left:860px;top:{BY + 110}px"))
o.append(label(1124, BY - 56, "새 리스트", K1, 30))
o += boxes(["11", "12", "13"], 1124, BY, BW, BH, K1, K1BG, True, 72, 20, ids=["cm-x", "cm-y", "cm-z"], attrs=[fly(2, "cm-a"), fly(3, "cm-b"), fly(4, "cm-c")])
o.append(caption("[넣을 값 for 이름 in 리스트]는 값마다 계산한 새 리스트예요.", 860, 5))
W("c-min", o, "[x + 10 for x in numbers]는 numbers의 값마다 10을 더한 새 리스트예요. numbers에서 x를 하나씩 꺼내 x + 10을 계산하고, 그 값을 모아요. 그림처럼 1은 11, 2는 12, 3은 13이 돼요. 결과는 21의 list(map(lambda x: x + 10, numbers))와 같아요. list와 lambda가 없어서 소리 내어 읽는 순서와 거의 같아요." + REAL)

# ---------- part 2 ----------
o = [sec("b-three")] + head(EB2, "같은 일을 세 가지로 써요", K2)
T, FW = 206, 1100
CFS[0] = 32
B3 = [PR4, "up = []", "for p in prices:", "    up.append(p + 500)", "print(up)", "print(list(map(lambda p: p + 500, prices)))", "print([p + 500 for p in prices])"]
o += cell({"id": "c-b1", "lines": B3, "n": 1, "out": ["[5000, 5500, 7000, 3500]"] * 3}, 96, T, FW, sel="c-b1")
TX = 96 + FW + 30
CB = (96 + 87, T, FW - 87, 10 + 7 * LH() + 8)   # the code box of the cell
for k, (i, n, t, c) in enumerate([(1, 3, "13의 for, 네 줄", BL), (5, 1, "21의 map, lambda까지", GRAY), (6, 1, "컴프리헨션, 한 줄", GR)]):
    o.append(lspot(k + 1, *CB, T + 10 + i * LH(), n * LH(), bar=c))
    o.append(tag(TX, ly(T, i + (n - 1) / 2), t, c, k + 1))
o.append(lspot_off(4))
OX, OW = 96 + 85 + 20, tw("[5000, 5500, 7000, 3500]")
o.append(box(4, OX - 16, oy(T, 7, 0) - LH() / 2 - 6, OW + 32, oy(T, 7, 2) - oy(T, 7, 0) + LH() + 12, OR, 5, 12))
o.append(tag(OX + OW + 50, oy(T, 7, 1), "결과는 셋 다 같아요", OR, 4))
o.append(caption("짧고 바로 읽히는 컴프리헨션을 가장 자주 써요.", 950, 5))
CFS[0] = 30
W("b-three", o, "for, map, 컴프리헨션은 같은 리스트를 만들어요. 1파트의 가격에 3000원짜리를 하나 더해서 세 방법을 한 셀에 나란히 적었어요. for는 네 줄이고, map은 한 줄이지만 lambda를 읽어야 해요. 컴프리헨션은 한 줄에 lambda도 없어요. 셋 다 새 리스트를 만들고 prices는 바꾸지 않아요. 파이썬 코드에서는 컴프리헨션을 가장 자주 봐요." + NEWK + REAL, ("p2", "만들기와 고르기"))

o = [sec("b-read")] + head(EB2, "뒤의 for부터 읽고, 앞의 값을 모아요", K2)
FS, X0 = 64, 96 + 64
o.append(strip(96, 206, 1728, 170, [seg([("[", W_), ("p + 500", CV), (" ", W_), ("for p in prices", CF), ("]", W_)], FS)], "", 64))
cw = FS * 0.6
o.append(underline(1, X0 + 9 * cw, X0 + 24 * cw, 336, CF, 6))
o.append(label(X0 + 9 * cw, 396, "① p를 하나 꺼내요", LF, 32, fade(1)))
o.append(underline(2, X0 + 1 * cw, X0 + 8 * cw, 336, CV, 6))
o.append(label(X0, 396, "② 계산해서 모아요", LV, 32, fade(2)))
o += plain_rows(96, 530, 1728, [("4500", "5000", "[5000]"), ("5000", "5500", "[5000, 5500]"), ("6500", "7000", "[5000, 5500, 7000]"), ("3000", "3500", "[5000, 5500, 7000, 3500]")],
                [300, 300, 1068], 3, 80, ("꺼낸 p", "p + 500", "모인 리스트"), 34, (0, 1, 2))
W("b-read", o, "컴프리헨션은 뒤의 for부터 움직이고, 앞의 값을 모아요. 적은 순서는 값이 먼저지만 실제로는 prices에서 p를 하나 꺼내는 일이 먼저예요. 그 p로 앞의 p + 500을 계산해 리스트에 모아요. 표처럼 4500을 꺼내 5000을 모으고, 5000을 꺼내 5500을 모아요. 네 값을 다 꺼내면 리스트가 완성돼요. 처음에는 for 부분을 먼저 읽고, 앞으로 돌아와 무엇을 모으는지 보면 쉬워요.")

o = [sec("b-filter")] + head(EB2, "뒤에 if를 붙이면 골라 담아요", K2)
T, FW = 200, 1180
BF = ["big = []", "for p in prices:", "    if p >= 5000:", "        big.append(p)", "print(big)", "print(list(filter(lambda p: p >= 5000, prices)))", "print([p for p in prices if p >= 5000])"]
o += cell({"id": "c-b2", "lines": BF, "n": 2, "out": ["[5000, 6500]"] * 3}, 96, T, FW, sel="c-b2")
TX = 96 + FW + 30
o.append(hl(96, T, FW, 0, 4, "mark", 1)); o.append(tag(TX, ly(T, 1.5), "17의 골라 담기", BL, 1))
o.append(hl(96, T, FW, 5, 1, "skip", 2)); o.append(tag(TX, ly(T, 5), "21의 filter", GRAY, 2))
o.append(hl(96, T, FW, 6, 1, "run", 3)); o.append(tag(TX, ly(T, 6), "if를 뒤에 붙여요", GR, 3))
FS, X0 = 46, 96 + 56
cw = FS * 0.6
o.append(strip(96, 770, 1728, 150, [seg([("[", W_), ("p", CV), (" ", W_), ("for p in prices", CF), (" ", W_), ("if p >= 5000", CI), ("]", W_)], FS)], rise(4), 56))
o.append(underline(5, X0 + cw, X0 + 2 * cw, 878, CV, 6))
o.append(underline(5, X0 + 19 * cw, X0 + 31 * cw, 878, CI, 6))
o.append(p(f"position:absolute;left:{X0 + 33 * cw + 30:.0f}px;top:810px;font-size:30px;font-weight:700;line-height:1.45;color:{W_};white-space:nowrap", "← p는 그대로, 조건이 True인 p만 모여요", fade(5)))
W("b-filter", o, "for 뒤에 if를 붙이면 조건이 True인 값만 골라 담아요. 17에서 for 안의 if로 골라 담던 일이고, 21에서는 filter로 썼어요. 이번에는 값을 바꾸지 않고 고르기만 해서 넣을 값 자리에 p를 그대로 적어요. p for p in이 같은 말을 되풀이하는 것 같지만, 앞의 p는 넣을 값이고 뒤의 p는 꺼낸 이름이에요. 세 방법 모두 [5000, 6500]이에요." + REAL)

o = [sec("b-both")] + head(EB2, "고르고 바꾸기를 한 번에 해요", K2)
T = 200
CFS[0] = 28
o += cell({"id": "c-b3", "lines": ["print([p * 9 // 10 for p in prices if p >= 5000])", "print(list(map(lambda p: p * 9 // 10, filter(lambda p: p >= 5000, prices))))"], "n": 3, "out": ["[4500, 5850]", "[4500, 5850]"]}, 96, T, 1728, sel="c-b3")
o.append(hl(96, T, 1728, 0, 1, "run", 1, "컴프리헨션"))
o.append(hl(96, T, 1728, 1, 1, "skip", 2, "21의 겹쳐 쓰기"))
CFS[0] = 30
BX, BY, BW = 96, 470, 190
o += boxes(["4500", "5000", "6500", "3000"], BX, BY, BW, 100, GRAY, "#F1F0EC", True, 34, 14, ids=["bb-0", "bb-1", "bb-2", "bb-3"], attrs=[fade(3)] * 4)
o.append(p(f"position:absolute;left:{BX}px;top:{BY + 128}px;width:{4 * BW + 42}px;height:84px;border-radius:18px;background:{LI};color:#FFFFFF;font-family:{MONO};font-size:32px;font-weight:700;line-height:84px;text-align:center", "if p >= 5000", fade(3)))
o += boxes(["4500", "5000", "6500", "3000"], BX, BY + 240, BW, 100, LI, K5BG, True, 34, 14, ids=["bk-0", "bk-1", "bk-2", "bk-3"], attrs=[rise(4)] * 4, struck=(0, 3))
o.append(arrow(110, LV, fade(5), f"position:absolute;left:{BX + 4 * BW + 42 + 40}px;top:{BY + 275}px"))
o.append(label(BX + 4 * BW + 42 + 20, BY + 200, "p * 9 // 10", LV, 32, fade(5), True))
o += boxes(["4500", "5850"], BX + 4 * BW + 42 + 190, BY + 240, 220, 100, LV, GRBG, True, 34, 18, attrs=[fly(5, "bk-1"), fly(6, "bk-2")])
o.append(caption("if로 남은 값만 앞의 식으로 바꿔서 모아요.", 920, 6))
W("b-both", o, "앞에 바꿀 식, 뒤에 고를 조건을 적으면 고르고 바꾸기가 한 번에 돼요. 21에서 5000원 이상만 골라 10% 할인할 때는 filter를 map 안에 넣어 괄호가 겹쳤어요. 그림처럼 if가 4500과 3000을 걸러 내고, 남은 5000과 6500만 9를 곱하고 10으로 몫 나누기해요. 결과는 같은데 한 줄이 훨씬 짧고 왼쪽부터 읽혀요." + REAL)

o = [sec("b-ifelse")] + head(EB2, "앞에 한 줄 if else를 넣으면 값을 바꿔 적어요", K2)
T = 200
o += cell({"id": "c-b4", "lines": ['print(["비쌈" if p >= 5000 else "보통" for p in prices])'], "n": 4, "out": ["['보통', '비쌈', '비쌈', '보통']"]}, 96, T, 1728, sel="c-b4")
FS, X0 = 44, 96 + 56
VAL = '"비쌈" if p >= 5000 else "보통"'
o.append(strip(96, 350, 1728, 140, [seg([("[", W_), (VAL, CV), (" ", W_), ("for p in prices", CF), ("]", W_)], FS)], "", 56))
o.append(underline(1, X0 + tw("[", FS), X0 + tw("[" + VAL, FS), 460, CV, 6))
o.append(label(X0 + tw("[", FS), 512, "↑ 17의 한 줄 if else는 값 하나라 넣을 값 자리에 들어가요", LV, 28, fade(1)))
rows_ = [("4500", "False", '"보통"'), ("5000", "True", '"비쌈"'), ("6500", "True", '"비쌈"'), ("3000", "False", '"보통"')]
pr = plain_rows(96, 590, 1728, rows_, [360, 420, 900], 2, 80, ("p", "p >= 5000", "넣을 값"), 34, (0, 2), ids=["bi-0", "bi-1", "bi-2", "bi-3"])
o += [x.replace("rise order 3", "rise order 2").replace("rise order 4", "rise order 2").replace("rise order 5", "rise order 2") for x in pr]
o.append(spot(3, target="bi-0", pad=4, r="10"))
o.append(spot(4, target="bi-1", pad=4, r="10"))
o.append(spot_off(5))
W("b-ifelse", o, "넣을 값 자리에 한 줄 if else를 넣으면 모든 값을 조건에 따라 바꿔 적어요. 17에서 배운 값1 if 조건 else 값2는 값 하나로 계산돼서 넣을 값 자리에 들어가요. 4500은 조건이 False라 보통, 5000은 True라 비쌈이 모여요. 고르지 않으니 개수는 네 개 그대로예요. 21에서 lambda에 한 줄 if else를 넣었던 것과 같은 이유예요." + REAL)

o = [sec("b-pos")] + head(EB2, "if가 뒤에 있으면 고르기, 앞에 있으면 바꾸기", K2)
T = 206
CFS[0] = 34
P1, P2 = "print([p for p in prices if p >= 5000])", "print([p if p >= 5000 else 0 for p in prices])"
o += cell({"id": "c-b5", "lines": [P1, P2], "n": 5, "out": ["[5000, 6500]", "[0, 5000, 6500, 0]"]}, 96, T, 1728, sel="c-b5")
o.append(box(1, cx(96, "print([p for p in prices ") - 9, ly(T, 0) - LH() / 2, tw("if p >= 5000") + 14, LH(), RED, 4, 10))
o.append(box(2, cx(96, "print([") - 7, ly(T, 1) - LH() / 2, tw("p if p >= 5000 else 0") + 14, LH(), GR, 4, 10))
TX = tx(96, [P2], 70)
o.append(tag(TX, ly(T, 0), "for 뒤", RED, 1)); o.append(tag(TX, ly(T, 1), "for 앞", GR, 2))
pr = plain_rows(96, 560, 1728, [("for 뒤의 if", "고르기", "안 써요", "4개 → 2개"), ("for 앞의 if else", "바꾸기", "꼭 써요", "4개 → 4개")], [520, 360, 360, 420], 3, 110, ("자리", "하는 일", "else", "개수"), 36)
o += pr
CFS[0] = 30
o.append(caption("for보다 뒤인지 앞인지만 보면 돼요.", 930, 5))
W("b-pos", o, "for 뒤의 if는 고르기, for 앞의 if else는 바꾸기예요. if가 들어갈 자리가 두 곳이라 헷갈리기 쉬워요. for 뒤에 붙은 if는 조건에 맞는 값만 남겨서 개수가 줄고, else를 쓰지 않아요. 넣을 값 자리에 들어간 if else는 모든 값을 바꿔 적어서 개수가 그대로이고, else가 꼭 있어야 해요. 자리를 바꿔 쓰면 생기는 오류는 5파트에서 봐요." + REAL)

# ---------- part 3 ----------
o = [sec("r-str")] + head(EB3, "길이, 글자, range로도 만들어요", K3)
T = 210
CFS[0] = 36
RS = ['names = ["latte", "tea", "coffee"]', "print([len(m) for m in names])", "print([m[0] for m in names])", "print([n * n for n in range(1, 6)])"]
o += cell({"id": "c-r1", "lines": RS, "n": 1, "out": ["[5, 3, 6]", "['l', 't', 'c']", "[1, 4, 9, 16, 25]"]}, 96, T, 1040, sel="c-r1")
TX = 96 + 1040 + 30
for k, (t, pre, part) in enumerate([("함수도 불러요. 21의 map(len, names)", "print([", "len(m)"), ("13의 글자 꺼내기", "print([", "m[0]"), ("18의 range로 숫자 만들기", "print([n * n for n in ", "range(1, 6)")]):
    if k < 2:
        o.append(underline(k + 1, cx(96, pre), cx(96, pre + part), ly(T, k + 1) + LH() / 2 - 4, K3, 5))
    else:
        o.append(underline(k + 1, cx(96, pre), cx(96, pre + part), ly(T, k + 1) + LH() / 2 - 4, OR, 5))
    o.append(tag(TX, ly(T, k + 1), t, K3 if k < 2 else OR, k + 1, 30))
CFS[0] = 30
o.append(caption("in 뒤에는 for로 돌 수 있는 것이면 다 와요.", 900, 4))
W("r-str", o, "넣을 값에는 함수 호출도, in 뒤에는 range도 올 수 있어요. len(m)을 적으면 이름마다 길이를 모아요. 21의 map(len, names)와 같은 결과예요. m[0]은 13에서 배운 글자 꺼내기라서 첫 글자만 모여요. in 뒤에는 for에 쓰던 것이면 무엇이든 와요. 18의 range(1, 6)을 넣으면 1부터 5까지 제곱한 리스트가 돼요." + NEWK + REAL, ("p3", "여러 데이터에 쓰기"))

o = [sec("r-tuple")] + head(EB3, "튜플 리스트는 꺼내 담기로 이름을 붙여요", K3)
T = 200
CFS[0] = 26
OR_ = ['orders = [("kim", "latte", 2), ("lee", "cake", 1), ("park", "coffee", 3), ("kim", "tea", 1)]', "print([o[0] for o in orders])", "print([menu_name for name, menu_name, qty in orders if qty >= 2])"]
o += cell({"id": "c-r2", "lines": OR_, "n": 2, "out": ["['kim', 'lee', 'park', 'kim']", "['latte', 'coffee']"]}, 96, T, 1728, sel="c-r2")
o.append(hl(96, T, 1728, 1, 1, "mark", 1, "번호로 꺼내기"))
o.append(hl(96, T, 1728, 2, 1, "run", 2, "이름 붙여 꺼내기"))
CFS[0] = 30
CY = 600
o.append(label(96, CY - 64, "튜플 하나", GRAY, 30))
TUP = [('"kim"', GRAY, "#F1F0EC"), ('"latte"', K3, K3BG), ("2", OR, K2BG)]
NAMES = [("name", GRAY, "#F1F0EC"), ("menu_name", K3, K3BG), ("qty", OR, K2BG)]
o.append(f'<div style="position:absolute;left:96px;top:{CY}px;display:flex;flex-direction:row;gap:14px">' + "".join(chip(t, c, b, 48, f' id="rt-{i}"') for i, (t, c, b) in enumerate(TUP)) + '</div>')
o.append(arrow(100, K3, fade(3), f"position:absolute;left:{96 + 760}px;top:{CY + 28}px"))
o.append(f'<div style="position:absolute;left:1000px;top:{CY}px;display:flex;flex-direction:row;gap:14px">' + "".join(chip(t, c, b, 48, fly(3 + (i > 0) + (i > 1), f"rt-{i}")) for i, (t, c, b) in enumerate(NAMES)) + '</div>')
o.append(label(1000, CY + 110, "13의 for name, menu_name, qty in과 같아요", K3, 30, fade(5)))
o.append(caption("qty >= 2처럼 조건도 이름으로 읽혀요.", 900, 6))
W("r-tuple", o, "튜플 리스트는 for에 이름 세 개를 적어 꺼내 담아요. o[0]처럼 번호로 꺼내도 되지만, 13에서 for name, menu_name, qty in orders:로 꺼내 담았던 것처럼 컴프리헨션의 for에도 이름을 붙일 수 있어요. 그러면 qty >= 2처럼 조건을 이름으로 읽어요. 2잔 이상인 주문만 골라 메뉴 이름만 모았어요. 21에서는 filter와 map 두 번이 필요했던 일이에요." + REAL)

o = [sec("r-dict")] + head(EB3, "중괄호와 키: 값으로 딕셔너리도 만들어요", K3)
T = 200
CFS[0] = 28
DC = ['menu = {"coffee": 4500, "latte": 5000, "cake": 6500}', "print({m: p * 11 // 10 for m, p in menu.items()})", 'stock = {"coffee": 3, "latte": 0, "cake": 2}', "print({m: n for m, n in stock.items() if n > 0})", "print([m for m in stock if stock[m] == 0])"]
o += cell({"id": "c-r3", "lines": DC, "n": 3, "out": ["{'coffee': 4950, 'latte': 5500, 'cake': 7150}", "{'coffee': 3, 'cake': 2}", "['latte']"]}, 96, T, 1240, sel="c-r3")
TX = 96 + 1240 + 30
o.append(hl(96, T, 1240, 1, 1, "mark", 1)); o.append(tag(TX, ly(T, 1), "값을 10% 올린 딕셔너리", BL, 1, 26))
o.append(hl(96, T, 1240, 3, 1, "run", 2)); o.append(tag(TX, ly(T, 3), "재고 있는 것만 남기기", GR, 2, 26))
o.append(hl(96, T, 1240, 4, 1, "skip", 3)); o.append(tag(TX, ly(T, 4), "키만 필요하면 리스트", GRAY, 3, 26))
CFS[0] = 30
FS, X0 = 46, 96 + 56
cw = FS * 0.6
o.append(strip(96, 660, 1728, 150, [seg([("{", W_), ("m", CK), (": ", W_), ("p * 11 // 10", CV), (" ", W_), ("for m, p in menu.items()", CF), ("}", W_)], FS)], rise(4), 56))
o.append(underline(5, X0 + cw, X0 + 16 * cw, 770, CK, 6))
o.append(p(f"position:absolute;left:{X0 + 42 * cw + 40:.0f}px;top:713px;font-size:30px;font-weight:700;line-height:1.45;color:{W_};white-space:nowrap", "← 키: 값을 앞에 적어요", fade(5)))
o.append(caption("{키: 값 for ...}는 딕셔너리, [값 for ...]는 리스트예요.", 880, 6))
W("r-dict", o, "중괄호 안 넣을 값 자리에 키: 값을 적으면 딕셔너리가 만들어져요. 딕셔너리 컴프리헨션이라고 해요. 15의 items()로 메뉴 이름 m과 가격 p를 꺼내고, 키는 m 그대로, 값은 10% 올린 가격으로 적었어요. if를 붙이면 재고가 있는 메뉴만 남긴 딕셔너리가 돼요. 21의 filter는 키만 남겼는데, 이번에는 재고 숫자까지 같이 남아요. 키만 필요하면 마지막 줄처럼 리스트로 만들어요." + REAL)

o = [sec("r-set")] + head(EB3, "중괄호에 값만 적으면 집합이 돼요", K3)
T = 200
CFS[0] = 32
o += cell({"id": "c-r4", "lines": ["buyers = {o[0] for o in orders}", "print(len(buyers))", "print(sorted(buyers))"], "n": 4, "out": ["3", "['kim', 'lee', 'park']"]}, 96, T, 1100, sel="c-r4")
o.append(tag(tx(96, ["['kim', 'lee', 'park']"], out=True), oy(T, 3, 1), "sorted로 줄 세워 찍었어요", GRAY, 4, 28))
CFS[0] = 30
BY, BW = 590, 190
o.append(label(96, BY - 56, "o[0]을 모으면", GRAY, 30))
o += boxes(['"kim"', '"lee"', '"park"', '"kim"'], 96, BY, BW, 110, GRAY, "#F1F0EC", True, 32, 14, ids=["rs-0", "rs-1", "rs-2", "rs-3"])
o.append(arrow(110, K3, fade(1), f"position:absolute;left:{96 + 4 * BW + 42 + 40}px;top:{BY + 40}px"))
o.append(label(1124, BY - 56, "buyers", K3, 30, fade(1), True))
o += boxes(['"kim"', '"lee"', '"park"'], 1124, BY, BW, 110, K3, K3BG, True, 32, 14, attrs=[fly(1, "rs-0"), fly(1, "rs-1"), fly(1, "rs-2")])
o.append(box(2, 96 + 3 * (BW + 14) - 10, BY - 10, BW + 20, 130, RED, 5, 18))
o.append(shake(2, "rs-3"))
o.append(label(96 + 3 * (BW + 14) - 10, BY + 140, "↑ kim은 이미 있어서 빠져요", RED, 28, fade(2)))
o.append(caption("집합을 찍는 순서는 실행할 때마다 달라질 수 있어요.", 900, 3))
W("r-set", o, "중괄호 안에 키: 값 대신 값 하나만 적으면 집합이 만들어져요. 주문 기록에서 손님 이름만 모았어요. kim이 두 번 주문했지만 16의 집합 규칙대로 한 번만 남아서 3명이에요. 집합을 그대로 찍으면 순서가 실행할 때마다 다를 수 있어서 22의 sorted로 줄 세워 찍었어요. 괄호 모양으로 무엇을 만드는지 구분해요. 대괄호는 리스트, 값만 든 중괄호는 집합, 키: 값이 든 중괄호는 딕셔너리예요. orders는 앞 셀에서 만들었어요." + REAL)

# ---------- part 4 ----------
o = [sec("w-sum")] + head(EB4, "sum, max에 바로 넘겨요", K4)
T = 200
WS = ['menu = {"coffee": 4500, "latte": 5000, "cake": 6500, "tea": 4000}', 'cart = ["coffee", "cake", "latte", "latte"]', "print(sum([menu[m] for m in cart]))", "print(max([len(m) for m in menu]))"]
o += cell({"id": "c-w1", "lines": WS, "n": 1, "out": ["21000", "6"]}, 96, T, 1300, sel="c-w1")
TX = tx(96, [WS[2]], 40)
o.append(tag(TX, ly(T, 2), "장바구니 가격 합계 21000", K4, 1))
o.append(tag(TX, ly(T, 3), "가장 긴 메뉴 이름의 길이 6", K4, 2))
o.append(spot(1, 96 + 80, ly(T, 2) - LH() / 2 - 2, 1180, LH() + 4, pad=2, dim=0.5))
o.append(spot(2, 96 + 80, ly(T, 3) - LH() / 2 - 2, 1180, LH() + 4, pad=2, dim=0.5))
o.append(spot_off(3))
QY = 640
o.append(label(96, QY, "19의 calc_total에서는 세 줄", GRAY, 28, fade(3)))
QS = f"position:absolute;left:96px;top:{QY + 52}px;font-family:{MONO};font-size:30px;font-weight:700;line-height:1.5;color:{GRAY};white-space:pre"
o.append(p(QS, e("total = 0\nfor m in cart:\n    total += menu[m]"), fade(3)))
# a copy of the three lines that only the player shows: its tokens travel into the strip on click 4
o.append(p(QS, "total = 0\n" + tok("f", "for m in cart") + ":\n    total += " + tok("v", "menu[m]"), ' id="ws-a"' + fade(3) + MORPH_FROM()))
o.append(arrow(90, K4, fade(4), f"position:absolute;left:700px;top:{QY + 112}px"))
o.append(strip(830, QY + 40, 994, 150, [p(f"font-family:{MONO};font-size:44px;font-weight:700;line-height:1.5;color:{W_};white-space:pre",
                                          "sum([" + tok("v", "menu[m]", f"color:{CV}") + " " + tok("f", "for m in cart", f"color:{CF}") + "])")], MORPH(4, "ws-a"), 48))
o.append(caption("계산할 값만 리스트로 모아 sum, max, len에 넘겨요.", 920, 5))
W("w-sum", o, "컴프리헨션이 만든 리스트는 sum, max에 바로 넘길 수 있어요. 장바구니 cart의 메뉴마다 menu[m]으로 가격을 꺼내 리스트를 만들고, sum이 더해요. 19에서 calc_total 안에 적었던 세 줄이 한 줄이 됐어요. 메뉴 이름 길이를 모아 max에 넘기면 가장 긴 이름의 길이 6이 나와요." + NEWK + REAL, ("p4", "함수와 함께 쓰기"))

o = [sec("w-sorted")] + head(EB4, "고른 다음 22의 sorted, min으로 이어요", K4)
T, FW = 200, 1180
WSO = ['stock = {"coffee": 3, "latte": 0, "cake": 2, "tea": 5}', "ok = [m for m in menu if stock[m] > 0]", "print(ok)", "print(sorted(ok, key=menu.get))", "print(min(ok, key=menu.get))"]
o += cell({"id": "c-w2", "lines": WSO, "n": 2, "out": ["['coffee', 'cake', 'tea']", "['tea', 'coffee', 'cake']", "tea"]}, 96, T, FW, sel="c-w2")
TX = 96 + FW + 30
o.append(hl(96, T, FW, 1, 1, "mark", 1)); o.append(tag(TX, ly(T, 1), "품절 아닌 메뉴만 골라요", BL, 1))
o.append(hl(96, T, FW, 3, 2, "run", 2)); o.append(tag(TX, ly(T, 3.5), "22의 key로 가격순", GR, 2))
CY, CW = 760, 250
OKS = [("coffee", "4500"), ("cake", "6500"), ("tea", "4000")]
for i, (m, pr_) in enumerate(OKS):
    o.append(chip(m, K4, K4BG, 40, f' id="ws-{i}"').replace("display:inline-block;", f"position:absolute;left:{96 + i * CW}px;top:{CY}px;width:{CW - 30}px;text-align:center;"))
    o.append(p(f"position:absolute;left:{96 + i * CW}px;top:{CY + 84}px;width:{CW - 30}px;text-align:center;font-family:{MONO};font-size:28px;font-weight:700;color:{GRAY}", pr_))
o.append(label(96, CY - 50, "ok", K4, 28, "", True))
o.append(arrow(80, K2, fade(3), f"position:absolute;left:{96 + 3 * CW - 4}px;top:{CY + 20}px"))
SO = [("tea", 2, "4000"), ("coffee", 0, "4500"), ("cake", 1, "6500")]
SX = 96 + 3 * CW + 110
for j, (m, src, pr_) in enumerate(SO):
    o.append(chip(m, K2, K2BG, 40, fly(3, f"ws-{src}")).replace("display:inline-block;", f"position:absolute;left:{SX + j * CW}px;top:{CY}px;width:{CW - 30}px;text-align:center;"))
    o.append(p(f"position:absolute;left:{SX + j * CW}px;top:{CY + 84}px;width:{CW - 30}px;text-align:center;font-family:{MONO};font-size:28px;font-weight:700;color:{GRAY}", pr_, fade(3)))
o.append(label(SX, CY - 50, "sorted(ok, key=menu.get)", K2, 28, fade(3), True))
o.append(label(SX, CY + 136, "↑ 가장 싼 tea가 min이에요", K2, 28, fade(4)))
W("w-sorted", o, "고르기는 컴프리헨션에, 줄 세우기와 하나 고르기는 sorted, min에 맡겨요. 재고가 있는 메뉴만 골라 ok에 담았어요. 그다음 22에서 배운 sorted와 key=menu.get으로 가격순으로 줄 세웠어요. 그림처럼 4000원인 tea가 맨 앞으로 와요. min에 같은 key를 주면 주문 가능한 메뉴 중 가장 싼 tea가 나와요. 일을 나눠 맡기면 줄마다 짧아져요. menu는 앞 셀에서 만들었어요." + REAL)

o = [sec("w-when")] + head(EB4, "이럴 땐 for가 더 읽기 쉬워요", K4)
rows_ = [("새 리스트 하나를 만들 때", "컴프리헨션"), ("print로 찍기만 할 때", "for"), ("한 번에 여러 줄을 할 때", "for"), ("break로 멈춰야 할 때", "for"), ("조건이 두 개를 넘을 때", "for나 def")]
o.append(f'<div style="position:absolute;left:96px;top:206px;width:1000px;height:50px;display:flex;flex-direction:row;gap:20px;border-bottom:3px solid {INK}">'
         + p(f"width:560px;flex:none;font-size:24px;font-weight:700;color:{GRAY}", "이럴 때") + p(f"font-size:24px;font-weight:700;color:{GRAY}", "쓰는 것") + '</div>')
for i, (a_, b_) in enumerate(rows_):
    good = i == 0
    o.append(f'<div data-build-in="rise order {1 if good else 2}" style="position:absolute;left:96px;top:{264 + i * 120}px;width:1000px;height:120px;display:flex;flex-direction:row;align-items:center;gap:20px;border-bottom:2px solid {LINE}">'
             + p(f"width:560px;flex:none;font-size:36px;font-weight:700;color:{INK}", e(a_)) + p(f"font-size:36px;font-weight:900;color:{K4 if good else GRAY}", e(b_)) + '</div>')
o.append(label(1180, 330, "참고, 읽기만", GRAY, 28, fade(3)))
CFS[0] = 28
o += cell({"id": "c-w3", "lines": ["scores = [[90, 80], [70, 60]]", "print([x for row in scores", "       for x in row])"], "n": 3, "out": ["[90, 80, 70, 60]"]}, 1180, 384, 644, attrs=rise(3))
o.append(p(f"position:absolute;left:1180px;top:680px;width:644px;font-size:28px;font-weight:700;line-height:1.5;color:{GRAY}", "for를 두 번 적었어요. 앞의 for가 바깥 반복이에요.", fade(4)))
o.append(zoom(4, 1160, 320, 684, 440, 30))
o.append(zoom_off(5))
CFS[0] = 30
o.append(caption("한 줄이 길어지면 for로 풀어 써요.", 950, 5))
W("w-when", o, "컴프리헨션은 새 리스트 하나를 만들 때만 써요. print로 찍기만 하거나, 합계를 쌓으면서 재고도 줄이는 것처럼 한 번에 여러 줄을 할 때는 for가 맞아요. 18의 break로 중간에 멈춰야 할 때도 for예요. 조건이 두 개를 넘으면 if, elif로 나눠 쓰는 편이 읽기 쉬워요. 오른쪽은 참고로 보여 드리는 겹친 컴프리헨션이에요. 14의 2차원 리스트를 한 줄로 펼쳐요. 앞에 적은 for가 바깥 반복이에요. 따라 치지 않아도 되고, 남의 코드에서 만나면 읽을 수 있게만 봐 두세요. 대괄호 안에서는 줄을 나눠 적어도 돼요." + REAL)

# ---------- part 5 ----------
o = [sec("t-else")] + head(EB5, "뒤의 if에 else를 붙이면 SyntaxError가 나요", K5)
T = 206
CFS[0] = 32
o += cell({"id": "c-t1", "lines": [PR4, "print([p for p in prices if p >= 5000 else 0])"], "n": 1, "out": ["SyntaxError: invalid syntax"], "err": True}, 96, T, 1728, sel="c-t1")
o.append(hl(96, T, 1728, 1, 1, "err", 1, "뒤의 if에 else"))
o.append(shake(1, "c-t1"))
o.append(box(1, cx(96, "", True) - 10, oy(T, 2, 0) - LH() / 2 - 2, tw("SyntaxError: invalid syntax") + 20, LH() + 4, RED, 4, 10))
CFS[0] = 30
o.append(reading(96, 450, "읽는 법: for 뒤의 if는 고르기라서 else를 받지 않아요.", RED, 2))
o.append(label(96, 548, "고르기만 하려면 else를 빼요", GRAY, 28, rise(3)))
o.append(fix(96, 594, "[p for p in prices if p >= 5000 else 0]", "[p for p in prices if p >= 5000]", 3, 28))
o.append(label(96, 718, "모두 바꾸려면 if else를 for 앞으로 옮겨요", GRAY, 28, rise(4)))
o.append(fix(96, 764, "[p for p in prices if p >= 5000 else 0]", "[p if p >= 5000 else 0 for p in prices]", 4, 28))
o.append(caption("SyntaxError는 실행 전에 나서 첫 줄 prices도 만들어지지 않아요.", 920, 5))
W("t-else", o, "for 뒤의 if에 else를 붙이면 invalid syntax가 나요. 2파트의 두 자리를 섞으면 나는 오류예요. for 뒤의 if는 고르기라서 else를 받지 않아요. 고르고 싶으면 else를 빼고, 모든 값을 바꾸고 싶으면 if else를 for 앞으로 옮겨요. SyntaxError는 셀을 실행하기 전에 나서 같은 셀의 첫 줄 prices도 만들어지지 않아요. 메시지 끝의 파일 이름과 줄 번호는 셀마다 달라서 그 부분은 빼고 옮겼어요." + NEWK + REAL, ("p5", "오류와 함정"))

o = [sec("t-print")] + head(EB5, "print를 넣으면 None 리스트가 생겨요", K5)
T = 206
CFS[0] = 32
o += cell({"id": "c-t2", "lines": ['[print(m) for m in ["latte", "tea"]]'], "n": 2, "out": ["latte", "tea", "", "[None, None]"]}, 96, T, 1100, sel="c-t2")
o.append(tag(tx(96, ["latte"], 60, True), (oy(T, 1, 0) + oy(T, 1, 1)) / 2, "찍히기는 해요", GRAY, 1))
o.append(ring(2, cx(96, "", True), oy(T, 1, 3) - LH() / 2 + 4, tw("[None, None]"), LH() - 8, RED, 5))
o.append(tag(tx(96, ["[None, None]"], 70, True), oy(T, 1, 3), "print가 돌려준 None이 모였어요", RED, 2))
CFS[0] = 30
o.append(reading(96, 590, "읽는 법: 컴프리헨션은 값을 모으는 곳이에요. 찍기만 할 때는 for를 써요.", RED, 3))
o.append(fix(96, 690, '[print(m) for m in ["latte", "tea"]]', 'for m in ["latte", "tea"]:\n    print(m)', 4, 30))
o.append(caption("셀 마지막 줄이라 [None, None]이 결과로 보였어요.", 920, 5))
W("t-print", o, "대괄호 안에 print를 넣으면 찍히기는 하지만 None 리스트가 생겨요. latte와 tea는 찍혀요. 그런데 셀 마지막 줄이라 결과로 [None, None]도 보여요. print는 찍고 나서 None을 돌려주고, 컴프리헨션이 그 None을 모았어요. 19에서 print와 return을 비교할 때 본 None이에요. 찍기만 할 때는 for를 써요." + REAL)

o = [sec("t-paren")] + head(EB5, "소괄호로 감싸면 리스트가 아니에요", K5)
T = 206
CFS[0] = 32
GEN = "<generator object <genexpr> at 0x7f2ba871b440>"
o += cell({"id": "c-t3", "lines": [PR4, "print((p + 500 for p in prices))", "print(list(p + 500 for p in prices))"], "n": 3, "out": [GEN, "[5000, 5500, 7000, 3500]"]}, 96, T, 1728, sel="c-t3")
o.append(hl(96, T, 1728, 1, 1, "err", 1))
o.append(underline(1, cx(96, "", True), cx(96, GEN, True), oy(T, 3, 0) + LH() / 2 - 2, RED, 5))
o.append(tag(tx(96, [GEN], 40, True), oy(T, 3, 0), "튜플이 아니에요", RED, 1))
o.append(tag(tx(96, ["[5000, 5500, 7000, 3500]"], 40, True), oy(T, 3, 1), "list로 감싸야 보여요", GRAY, 2))
CFS[0] = 30
o.append(reading(96, 580, "읽는 법: 소괄호는 달라고 하면 값을 하나씩 꺼내 주는 묶음이에요. 21의 map object와 비슷해요.", RED, 3, 30))
o.append(fix(96, 700, "(p + 500 for p in prices)", "[p + 500 for p in prices]", 4, 38))
o.append(caption("0x 뒤 숫자는 메모리 위치라서 화면마다 달라요.", 920, 5))
W("t-paren", o, "컴프리헨션을 소괄호로 감싸면 리스트도 튜플도 아니에요. 찍어 보면 generator object가 나와요. 21의 map object처럼 달라고 하면 값을 하나씩 꺼내 주는 묶음이에요. list로 감싸야 결과가 보여요. 이번 챕터에서는 이 묶음을 따로 다루지 않아요. 리스트가 필요하면 대괄호로 써요. 0x 뒤 숫자는 메모리 위치라서 화면마다 달라요." + REAL)

o = [sec("t-name")] + head(EB5, "앞과 뒤의 이름이 다르면 NameError가 나요", K5)
T = 206
CFS[0] = 32
o += cell({"id": "c-t4", "lines": ["print([x + 10 for p in prices])"], "n": 4, "out": ["NameError: name 'x' is not defined"], "err": True}, 96, T, 1728, sel="c-t4")
o.append(tag(tx(96, ["NameError: name 'x' is not defined"], 40, True), oy(T, 1, 0), "x라는 변수는 없어요", RED, 1))
CFS[0] = 30
FS, X0 = 72, 96 + 64
cw = FS * 0.6
o.append(strip(96, 400, 1728, 180, [seg([("[", W_), ("x", CI, MARK(2)), (" + 10 for ", W_), ("p", CF, MARK(3)), (" in prices]", W_)], FS)], "", 64))
o.append(box(2, X0 + cw - 4, 436, cw + 8, 108, CI, 5, 10))
o.append(label(X0 + cw - 12, 608, "↑ 앞의 값은 x", RED, 30, fade(2)))
o.append(box(3, X0 + 12 * cw - 4, 436, cw + 8, 108, CF, 5, 10))
o.append(label(X0 + 12 * cw - 12, 608, "↑ 꺼낸 이름은 p", TEAL, 30, fade(3)))
o.append(fix(96, 720, "[x + 10 for p in prices]", "[p + 10 for p in prices]", 4, 38))
o.append(caption("앞 예제를 복사해서 뒤쪽만 고칠 때 자주 나요.", 860, 5))
W("t-name", o, "넣을 값의 이름과 for로 꺼낸 이름이 다르면 NameError가 나요. 앞의 값에는 x를 쓰고 뒤의 for에서는 p로 꺼냈어요. 꺼낸 이름은 p뿐이라 x가 없다는 오류예요. 1파트의 [x + 10 for x in numbers]를 복사해서 뒤쪽만 prices로 바꿀 때 자주 생겨요. 두 이름이 같은지 봐요. prices는 앞 셀에서 만들었어요." + REAL)

# ---------- part 6 ----------
o = [sec("x-receipt")] + head(EB6, "장바구니 영수증을 컴프리헨션으로 찍어요", K6)
T, FW = 200, 1240
CFS[0] = 34
RC = ['menu = {"coffee": 4500, "latte": 5000, "cake": 6500}', 'cart = ["latte", "cake", "coffee"]', 'lines = [f"{m:<7}{menu[m]:>6,}원" for m in cart]', 'print("\\n".join(lines))', 'print(f"합계   {sum([menu[m] for m in cart]):>6,}원")']
o += cell({"id": "c-x1", "lines": RC, "n": 1, "out": ["latte   5,000원", "cake    6,500원", "coffee  4,500원", "합계   16,000원"]}, 96, T, FW, sel="c-x1")
o = [re.sub(r'<p( style="[^"]*">합계   16,000원</p>)', lambda m: "<p" + COUNT(3) + m.group(1), x) for x in o]
TX = 96 + FW + 30
o.append(hl(96, T, FW, 2, 1, "mark", 1)); o.append(tag(TX, ly(T, 2), "메뉴마다 한 줄씩", BL, 1))
o.append(hl(96, T, FW, 4, 1, "run", 2)); o.append(tag(TX, ly(T, 4), "합계는 가격 리스트를 sum", GR, 2))
RW = tw("coffee  4,500원")
o.append(box(3, cx(96, "", True) - 16, oy(T, 5, 0) - LH() / 2 - 6, RW + 32, oy(T, 5, 3) - oy(T, 5, 0) + LH() + 12, K6, 5, 12))
o.append(tag(cx(96, "", True) + RW + 60, oy(T, 5, 1.5), "13의 칸 맞추기 f-string도 넣을 값이에요", K6, 3))
CFS[0] = 30
o.append(caption("21에서 def와 map으로 한 일을 한 줄로 했어요.", 920, 4))
W("x-receipt", o, "메뉴마다 영수증 한 줄을 컴프리헨션으로 만들어 join으로 이어 찍어요. 13의 칸 맞추기를 쓴 f-string도 값이라 넣을 값 자리에 쓸 수 있어요. 줄바꿈으로 join해서 한 번에 찍고, 합계는 4파트처럼 가격 리스트를 sum에 넘겼어요. 21에서는 줄 만드는 일을 def로 만들어 map에 넘겼는데, 컴프리헨션으로는 한 줄이에요." + NEWK + REAL, ("p6", "실습"))

o = [sec("x-stock")] + head(EB6, "품절 목록과 주문 가능 메뉴판을 만들어요", K6)
T, FW = 200, 1340
CFS[0] = 28
ST = ['menu = {"coffee": 4500, "latte": 5000, "cake": 6500, "tea": 4000}', 'stock = {"coffee": 3, "latte": 0, "cake": 2, "tea": 0}', "soldout = [m for m in stock if stock[m] == 0]", 'print("품절:", ", ".join(soldout))', "board = {m: menu[m] * 11 // 10 for m in menu if stock[m] > 0}", "print(board)"]
o += cell({"id": "c-x2", "lines": ST, "n": 2, "out": ["품절: latte, tea", "{'coffee': 4950, 'cake': 7150}"]}, 96, T, FW, sel="c-x2")
TX = 96 + FW + 30
o.append(hl(96, T, FW, 2, 1, "mark", 1)); o.append(tag(TX, ly(T, 2), "품절 리스트", BL, 1))
o.append(hl(96, T, FW, 4, 1, "run", 2)); o.append(tag(TX, ly(T, 4), "새 메뉴판 딕셔너리", GR, 2))
CFS[0] = 30
LY_ = 670
o.append(label(96, LY_ - 50, "stock", GRAY, 28, fade(3), True))
o.append(lockers([("coffee", "3"), ("latte", "0"), ("cake", "2"), ("tea", "0")], 96, LY_, 200, 160, GRAY, "#F1F0EC", rise(3), 36, 24, 12))
o.append(arrow(100, K6, fade(4), f"position:absolute;left:{96 + 4 * 212 + 30}px;top:{LY_ + 65}px"))
o.append(label(1100, LY_ - 50, "board", K6, 28, fade(4), True))
o.append(lockers([("coffee", "4950"), ("cake", "7150")], 1100, LY_, 230, 160, K6, K6BG, rise(4), 36, 24, 12))
o.append(label(1100, LY_ + 180, "↑ 재고 있는 것만, 10% 올려서", K6, 28, fade(4)))
W("x-stock", o, "재고 데이터로 품절 목록과 새 메뉴판을 만들어요. 품절 메뉴는 재고가 0인 키만 골라 리스트로 만들고, 13의 join으로 쉼표를 넣어 이어 찍었어요. 새 메뉴판은 재고가 있는 메뉴만 골라 10% 올린 가격을 담은 딕셔너리예요. 키: 값 자리에 바꿀 식을, 뒤에 고를 조건을 적었어요. 2파트의 고르고 바꾸기를 딕셔너리로 한 거예요." + REAL)

o = [sec("x-grades")] + head(EB6, "성적표에서 합격자, 결과표, 평균, 1등을 뽑아요", K6)
T = 200
GR_ = ['scores = [["kim", 92], ["lee", 78], ["park", 85], ["choi", 59]]', "print([name for name, score in scores if score >= 80])", 'print(["합격" if score >= 60 else "재시험" for name, score in scores])', "print(sum([score for name, score in scores]) / len(scores))", "print(max(scores, key=lambda s: s[1])[0])"]
CFS[0] = 28
FW = 1260
o += cell({"id": "c-x3", "lines": GR_, "n": 3, "out": ["['kim', 'park']", "['합격', '합격', '합격', '재시험']", "78.5", "kim"]}, 96, T, FW, sel="c-x3")
TX = 96 + FW + 30
for k, t in enumerate(["뒤의 if: 80점 이상 고르기", "앞의 if else: 모두에게", "점수만 모아 평균", "22의 key로 1등"]):
    o.append(run(k + 1, 96 + 89, T + 10 + (k + 1) * LH(), FW - 93, LH()))
    o.append(tag(TX, ly(T, k + 1), t, GR, k + 1, 28))
o.append(run_off(5))
CFS[0] = 30
o.append(caption("고르기, 바꾸기, 함수와 함께 쓰기를 한 셀에서 다 썼어요.", 860, 5))
W("x-grades", o, "14의 성적 2차원 리스트에서 고르기, 바꾸기, 평균, 1등을 한 셀로 뽑아요. 안쪽 리스트 두 칸을 name, score로 꺼내 담아요. 80점 이상은 뒤에 if를 붙여 골랐어요. 합격과 재시험은 앞에 한 줄 if else를 넣어 모두에게 붙였어요. 평균은 점수만 모은 리스트를 sum에 넘기고 사람 수로 나눴어요. 1등은 22에서 배운 max와 key예요." + REAL)

# ---------- wrap up ----------
o = [sec("trouble")] + head("정리", "막히면 오류의 마지막 줄을 봐요", RED)
TR = [("SyntaxError: invalid syntax", "뒤의 if에 else를 붙였어요", "else는 for 앞으로"),
      ("NameError: name 'x' is not defined", "앞과 뒤의 이름이 달라요", "같은 이름으로"),
      ("[None, None]이 같이 나와요", "대괄호 안에서 print를 했어요", "찍기는 for로"),
      ("<generator object ...>가 나와요", "소괄호로 감쌌어요", "대괄호로"),
      ("개수가 줄었어요", "for 뒤에 if를 붙여 골랐어요", "바꾸려면 if else를 앞에"),
      ("한 줄이 너무 길어요", "조건이나 할 일이 많아요", "for나 def로 나누기"),
      ("집합 순서가 슬라이드와 달라요", "집합은 순서가 없어요", "sorted()로 찍기")]
for i, (q, a_, cmd) in enumerate(TR):
    o.append(f'<div data-build-in="rise order {min(i + 1, 6)}" style="position:absolute;left:96px;top:{200 + i * 104}px;width:1728px;height:104px;display:flex;flex-direction:row;align-items:center;gap:26px;border-bottom:2px solid {LINE}">'
             + '<div style="flex:1;display:flex;flex-direction:column;gap:4px">' + p(f"{'font-family:' + MONO + ';' if q.isascii() else ''}font-size:26px;font-weight:700;color:{RED};white-space:nowrap", e(q)) + p(f"font-size:26px;color:{INK}", e(a_)) + '</div>'
             + p(f"width:520px;flex:none;font-size:28px;font-weight:700;color:{GR};white-space:pre", '✓ ' + e(cmd)) + '</div>')
o.append(caption("헷갈리면 같은 일을 for 문으로 먼저 써 보고 세 조각을 옮겨요.", 960))
W("trouble", o, "막히면 for 문으로 먼저 써 보고 넣을 값, for, if 세 조각을 대괄호 안으로 옮겨요. 이번 챕터에서 자주 만나는 일을 모았어요. 1번과 5번은 if 자리 때문에 생겨요. 뒤의 if는 고르기, 앞의 if else는 바꾸기예요. 2번은 이름이 어긋났을 때, 3번과 4번은 컴프리헨션을 리스트 만들기 말고 다른 데 쓰려다 생겨요. 6번처럼 한 줄이 길어지면 for나 def로 나눠요.", ("trouble", "정리"))

o = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>']
CH = [("[x + 10 for x in xs]", "값마다 바꾼 리스트", K2), ("[x for x in xs if x > 0]", "조건에 맞는 값만 고르기", K2), ("[a if c else b for x in xs]", "앞의 if else는 바꾸기", K2), ("[n for n, s in pairs]", "튜플은 꺼내 담기로", K3),
      ("{k: v for k, v in d.items()}", "딕셔너리 만들기", K3), ("{x for x in xs}", "집합 만들기", K3), ("sum([...]), max([...])", "모은 리스트를 바로 넘기기", K4), ("for 문", "찍기, 여러 줄, break는 for로", GRAY)]
for i, (k, d, c) in enumerate(CH):
    x, y = 96 + (i // 4) * 884, 200 + (i % 4) * 150
    o.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:844px;height:130px;display:flex;flex-direction:column;justify-content:center;gap:6px;border-bottom:2px solid {LINE}">'
             + p(f"font-family:{MONO if k.isascii() else SANS};font-size:36px;font-weight:700;color:{c};white-space:pre", e(k)) + p(f"font-size:30px;color:{SUB}", e(d)) + '</div>')
o.append(p(f"position:absolute;left:96px;top:840px;width:1728px;font-size:34px;font-weight:700;line-height:1.5;color:{INK}", "뒤의 if는 고르기, 앞의 if else는 바꾸기예요.<br>" + f'<span style="color:{GRAY}">다음: 24에서 클래스로 붕어빵 틀을 직접 만들어요.</span>'))
W("cheatsheet", o, "대괄호 안에 넣을 값, for, if 순서로 적어요. 뒤의 if는 고르기, 앞의 if else는 바꾸기예요. 튜플은 꺼내 담기로 이름을 붙이고, 중괄호로 딕셔너리와 집합도 만들어요. 만든 리스트는 sum, max, sorted에 바로 넘겨요. 찍기만 하거나 여러 줄을 할 때는 for가 더 좋아요. 24에서는 클래스로 값과 할 일을 한 틀에 묶어요.")

# ---------- toc ----------
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
parts_ = [("Lightbulb", K1, "왜 필요한가", "c-why", "c-min"), ("Code", K2, "만들기와 고르기", "b-three", "b-pos"), ("Archive", K3, "여러 데이터에 쓰기", "r-str", "r-set"),
          ("Settings", K4, "함수와 함께 쓰기", "w-sum", "w-when"), ("Warning", K5, "오류와 함정", "t-else", "t-name"), ("Star", K6, "실습", "x-receipt", "x-grades")]
t = [f'<section id="toc" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>']
for i, (ic, c, h, a, b) in enumerate(parts_):
    x, y = 96 + (i // 3) * 884, 230 + (i % 3) * 190
    t.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:844px;height:160px;display:flex;flex-direction:row;align-items:center;gap:28px;border-bottom:2px solid {LINE}">'
             f'<p style="width:70px;font-size:72px;font-weight:900;color:{c}">{i + 1}</p><x-icon name="{ic}" style="width:52px;height:52px;color:{c}"></x-icon>'
             f'<p style="flex:1;font-size:44px;font-weight:700;color:{INK}">{e(h)}</p><p style="font-size:28px;color:{GRAY}">{page[a]}–{page[b]}쪽</p></div>')
t.append(f'<p style="position:absolute;left:96px;top:880px;font-size:30px;color:{SUB}">{page["ready"]}쪽은 노트북 준비, {page["trouble"]}–{page["cheatsheet"]}쪽은 막힐 때와 한 장 요약이에요.</p>')
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(t) + "\n<aside>" + e("2파트가 중심이고, 만들기와 고르기, if 자리를 비교해요. 1파트는 for와 map의 불편한 점과 for의 세 조각을 옮기는 그림이에요. 3파트는 튜플, 딕셔너리, 집합으로 넓히고, 4파트는 sum, sorted와 함께 쓰는 법과 for가 나은 경우예요. 5파트는 자주 나는 오류, 6파트는 카페와 성적 실습이에요. 파트마다 새 커널에서 위에서부터 차례로 실행해요.") + "</aside>\n</section>\n")
deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-04T03:00:00Z"}, "lists": "css", "title": "리스트 컴프리헨션", "order": ORDER, "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
print(len(ORDER), "slides")
