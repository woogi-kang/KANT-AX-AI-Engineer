"""Generates every slide of the functions 1 deck (19, def, parameters, return) and slides/deck.json.

Story: keeps writing in basics.ipynb from chapters 12-18. Starts from the cafe total copied for every customer,
draws a function as a box that takes ingredients and gives a result, then def and calling, parameters and arguments,
return next to print, None, early return and returning two values. Part 5 collects the usual errors, and part 6 turns
code from chapters 15-17 (cart total, stock check, grades, discount) into functions.

Layout rules (2026-11-08 remake, from the Stageshow skill): one focal object per slide (the notebook cell or one
diagram, drawn large), terms written as leader tags beside the line they explain instead of cards, each thing said
once (explanations live in the speaker notes), no empty bands, and values that move between places fly there
(an argument into its parameter box, a returned value back to where the function was called).
Highlights come from tools/HIGHLIGHT.md: line tints, fly, moving spotlight, cursor click, pen ring, underline, box.

Every cell and output comes from tools/demo.sh (tools/run_nb.py runs the cells with the project kernel).
Usage: python3 tools/gen.py slides
"""

import html, json, os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from highlight import spot, spot_off, cursor, cursor_off, ring, box, underline

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
INK, SUB, LINE, CARD, BG = "#1D2330", "#4A5262", "#E1DED6", "#FFFFFF", "#F6F5F1"
BL, GR, OR, PUR, RED, TEAL, GRAY = "#2459C9", "#1F8A4C", "#B26A00", "#5A3BB8", "#A33131", "#0F7C86", "#6A7180"
JP = "#B8560F"          # Jupyter, same as chapters 09 and 10
SEL = "#2F7DE1"         # selected cell bar, like VS Code's focus color
K1, K1BG = "#1E5FA8", "#E5EEF8"
K2, K2BG = "#A0620A", "#F7EEDD"
K3, K3BG = TEAL, "#E2F2F3"
K4, K4BG = "#A23B72", "#F6E7EF"
K5, K5BG = RED, "#F8E6E6"
K6, K6BG = PUR, "#ECE7F8"
GRBG, ORBG = "#E6F4EC", "#FBEFD9"
NB = "basics.ipynb"


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


def sec(sid, bg=BG):
    return f'<section id="{sid}" data-transition="fade" style="background:{bg};color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">'


def head(eyebrow, title, color):
    return [p(f"position:absolute;left:96px;top:48px;width:1728px;font-size:26px;font-weight:700;color:{color}", e(eyebrow), ' id="eyebrow"'),
            f'<h2 id="title" style="position:absolute;left:96px;top:92px;width:1728px;font-size:56px;font-weight:700;line-height:1.2;color:{INK}">{title}</h2>']


def caption(text, top=944, order=None):
    return p(f"position:absolute;left:96px;top:{top}px;width:1728px;font-size:34px;font-weight:700;line-height:1.4;color:{INK}", text, ' id="caption"' + (bi("rise", order) or ' data-build-in="rise"'))


def num(i, color, size=40):
    return p(f"width:{size + 16}px;height:{size + 16}px;flex:none;border-radius:50%;background:{color};color:#FFFFFF;font-size:{size * 0.6:.0f}px;font-weight:900;line-height:{size + 16}px;text-align:center", str(i))


def kbd(text, size=26):
    caps = [p(f"font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.2;white-space:nowrap;color:{INK};background:#FFFFFF;border:2px solid #C9CED8;border-bottom-width:5px;border-radius:10px;padding:6px 14px", e(k)) for k in text.split("+")]
    plus = p(f"font-size:{size * 0.8:.0f}px;font-weight:700;color:{GRAY}", "+")
    return '<div style="display:flex;flex-direction:row;align-items:center;gap:8px">' + plus.join(caps) + '</div>'


# ---------- notebook cell, drawn at a chosen font size ----------
# Geometry: the code box starts at top; its first text line sits at top + 10 (2px border + 8px padding).
# Text starts 105px right of the cell's left (7 bar + 10 + 58 gutter + 10 + 2 border + 18 padding).
# Output lines sit under the box, 10px apart, starting at the same x.

def LH(fs):
    return fs * 1.45


def tw(s, fs):
    """Rendered width of a code string: Hangul is about one em, the rest 0.6 em."""
    return sum(fs * (1.0 if '가' <= ch <= '힣' else 0.6) for ch in s)


def ly(top, i, fs):
    """Center y of code line i."""
    return top + 10 + i * LH(fs) + LH(fs) / 2


def oy(top, n, j, fs):
    """Center y of output line j of a cell with n code lines."""
    return top + 20 + n * LH(fs) + 10 + j * (LH(fs) + 10) + LH(fs) / 2


def lx(left, prefix, fs):
    """x where a piece of a code or output line starts, after prefix."""
    return left + 105 + tw(prefix, fs)


def box_bottom(top, n, fs):
    return top + 20 + n * LH(fs)


def tok(text, tid=None, color=None, bg=None):
    """A span inside a code line: gives it an id (fly source) and a color."""
    st = (f"color:{color};" if color else "") + (f"background:{bg};border-radius:6px;" if bg else "")
    return f'<span{f" id=\"{tid}\"" if tid else ""} style="{st}">{e(text)}</span>'


def plain(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s))


def cell(c, left, top, w, fs=30, sel=None, attrs="", run=False):
    """c: dict(id, lines, n, out, err, raw). raw=True: lines and out are already HTML (use tok()).
    run=True draws VS Code's run button in the gutter instead of the [n] count."""
    lines, n = c.get("lines", [""]), c.get("n")
    raw = c.get("raw")
    chosen = sel == c["id"]
    o = [f'<div id="{c["id"]}"{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;display:flex;flex-direction:column;gap:10px">']
    bar = f'<div style="width:7px;flex:none;border-radius:4px;background:{SEL if chosen else "transparent"}"></div>'
    if run:
        gut = (f'<div style="width:58px;flex:none;display:flex;justify-content:flex-end;padding-top:{LH(fs) / 2 - 8:.0f}px">'
               f'<svg id="{c["id"]}-run" viewBox="0 0 26 26" style="width:30px;height:30px"><circle cx="13" cy="13" r="12" fill="#FFFFFF" stroke="#9AA1AE" stroke-width="2"/>'
               f'<path d="M10,7.5 L18,13 L10,18.5 Z" fill="{GR}"/></svg></div>')
    else:
        gut = p(f"width:58px;flex:none;font-family:{MONO};font-size:20px;color:{GRAY};text-align:right;padding-top:{LH(fs) / 2 - 12:.0f}px", f"[{n}]" if n else "[ ]")
    txt = "".join(p(f"font-family:{MONO};font-size:{fs}px;line-height:1.45;white-space:pre;color:{INK}", (l if raw else e(l)) if l else "&#160;") for l in lines)
    tag_ = p(f"position:absolute;right:14px;bottom:6px;font-size:18px;color:{GRAY}", "Python")
    bx = f'<div style="flex:1;position:relative;background:#FFFFFF;border:2px solid {LINE};border-radius:10px;padding:8px 18px 8px;display:flex;flex-direction:column">{txt}{tag_}</div>'
    o.append(f'<div style="display:flex;flex-direction:row;gap:10px;align-items:stretch">{bar}{gut}{bx}</div>')
    if c.get("out"):
        col = lambda l: RED if c.get("err") and re.match(r"[A-Za-z]+(Error|Interrupt)", plain(l)) else INK
        o.append(''.join(p(f"margin-left:85px;padding:0 20px;font-family:{MONO};font-size:{fs}px;line-height:1.45;white-space:pre;color:{col(l)}", (l if raw else e(l)) if l else "&#160;") for l in c["out"]))
    o.append('</div>')
    return o


def outlines(left, top, lines, fs, order, err=False, oid=None):
    """Output lines drawn on their own (to show them after a click). top = the code box's bottom."""
    col = lambda l: RED if err and re.match(r"[A-Za-z]+Error", l) else INK
    rows = "".join(p(f"padding:0 20px;font-family:{MONO};font-size:{fs}px;line-height:1.45;white-space:pre;color:{col(l)}", e(l) if l else "&#160;") for l in lines)
    return f'<div{f" id=\"{oid}\"" if oid else ""}{bi("fade", order)} style="position:absolute;left:{left + 85}px;top:{top + 10}px;display:flex;flex-direction:column;gap:10px">{rows}</div>'


HL = {"run": "rgba(31,138,76,0.16)", "skip": "rgba(106,113,128,0.20)", "err": "rgba(163,49,49,0.14)", "mark": "rgba(36,89,201,0.13)"}
HLT = {"run": GR, "skip": GRAY, "err": RED, "mark": BL}


def hl(left, top, w, i, n=1, kind="run", order=1, fs=30, tag_=None):
    """Tints code lines i..i+n-1. tag_: a short word at the right end, inside the tint."""
    y = top + 10 + i * LH(fs)
    t = p(f"position:absolute;right:90px;top:0;font-size:22px;font-weight:700;line-height:{LH(fs):.0f}px;color:{HLT[kind]}", e(tag_)) if tag_ else ""
    return f'<div{bi("fade", order)} style="position:absolute;left:{left + 87}px;top:{y:.0f}px;width:{w - 89}px;height:{n * LH(fs):.0f}px;background:{HL[kind]};border-radius:6px">{t}</div>'


def tag(x, y, text, color, order=None, size=30, lead=True, anim="fade", w=None, align="left"):
    """A leader label: '← text' centred on y. No box."""
    ws = f"width:{w}px;text-align:{align};" if w else ""
    t = ("← " if lead else "") + e(text)
    return p(f"position:absolute;left:{x}px;top:{y - size * 0.725:.0f}px;{ws}font-size:{size}px;font-weight:700;line-height:1.45;color:{color};white-space:nowrap", t, bi(anim, order))


def leader(pts, color, order=None, width=3):
    """A fine line from a label to what it explains, ending in a dot on the object's side."""
    d = " ".join(f"{x:.0f},{y:.0f}" for x, y in pts)
    x, y = pts[-1]
    return (f'<svg{bi("fade", order)} viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none">'
            f'<polyline points="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round"/><circle cx="{x:.0f}" cy="{y:.0f}" r="7" fill="{color}"/></svg>')


def harrow(x, y, w, color="#B4B9C3", order=None, h=28):
    """A right arrow drawn in SVG, centred on y."""
    return (f'<svg{bi("fade", order)} viewBox="0 0 {w} {h}" style="position:absolute;left:{x}px;top:{y - h / 2:.0f}px;width:{w}px;height:{h}px">'
            f'<path d="M0,{h / 2 - 4} L{w - 22},{h / 2 - 4} L{w - 22},0 L{w},{h / 2} L{w - 22},{h} L{w - 22},{h / 2 + 4} L0,{h / 2 + 4} Z" fill="{color}"/></svg>')


def mono(text, size=30, color=INK, bg=None, extra="", attrs="", raw=False):
    b = f"background:{bg};border-radius:12px;padding:4px 18px;" if bg else ""
    return p(f"font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.4;color:{color};white-space:pre;{b}{extra}", text if raw else e(text), attrs)


def at(x, y, inner, attrs=""):
    return f'<div{attrs} style="position:absolute;left:{x}px;top:{y}px">{inner}</div>'


def var_box(sid, name, left, top, color, w=420, h=200, attrs=""):
    """A parameter or variable drawn as a box with its name on top. The value is drawn by val() so it can fly in."""
    return (f'<div id="{sid}"{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:{CARD};border:3px solid {color};border-radius:22px;overflow:hidden">'
            + p(f"height:66px;background:{color};color:#FFFFFF;font-family:{MONO};font-size:32px;font-weight:700;line-height:66px;padding:0 26px", e(name)) + '</div>')


def val(left, top, w, h, text, color=INK, order=None, src=None, size=60):
    """The value inside a var_box (same left, top, w, h). Flies in from #src when given."""
    a = f' data-build-in="fly order {order}" data-from="{src}"' if src else bi("rise", order)
    return (f'<div{a} style="position:absolute;left:{left}px;top:{top + 66}px;width:{w}px;height:{h - 66}px;display:flex;align-items:center;justify-content:center">'
            + p(f"font-family:{MONO};font-size:{size}px;font-weight:700;color:{color};white-space:pre", e(text)) + '</div>')


def fix(left, top, bads, good, order, size=32):
    """The wrong lines struck through, an arrow, the right line."""
    if isinstance(bads, str):
        bads = [bads]
    o = [f'<div{bi("rise", order)} style="position:absolute;left:{left}px;top:{top}px;display:flex;flex-direction:row;align-items:center;gap:22px">']
    for b in bads:
        o.append(p(f"font-size:{size}px;font-weight:900;color:{RED}", "✕") + p(f"font-family:{MONO};font-size:{size}px;font-weight:700;color:{RED};text-decoration:line-through;text-decoration-thickness:3px;white-space:pre;margin-right:14px", e(b)))
    o.append(f'<svg viewBox="0 0 70 28" style="width:70px;height:28px;flex:none"><path d="M0,10 L48,10 L48,0 L70,14 L48,28 L48,18 L0,18 Z" fill="#B4B9C3"/></svg>')
    o.append(p(f"font-size:{size}px;font-weight:900;color:{GR}", "✓") + p(f"font-family:{MONO};font-size:{size}px;font-weight:700;color:{INK};background:{GRBG};border:3px solid {GR};border-radius:14px;padding:6px 20px;white-space:pre", e(good)))
    o.append('</div>')
    return "".join(o)


def rows_table(left, top, widths, header, rows, order0=1, rh=78, fs=28, ids=None, mono_cols=()):
    """A light table: gray header over a dark rule, rows split by hairlines, no boxes."""
    w = sum(widths) + 20 * (len(widths) - 1)
    o = [f'<div style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:50px;display:flex;flex-direction:row;gap:20px;border-bottom:3px solid {INK}"{bi("fade", order0)}>'
         + "".join(p(f"width:{cw}px;flex:none;font-size:24px;font-weight:700;color:{GRAY};white-space:nowrap", e(c)) for c, cw in zip(header, widths)) + '</div>']
    for i, r in enumerate(rows):
        cells_ = ""
        for k, (c, cw) in enumerate(zip(r, widths)):
            if c in ("True", "False"):
                cc, cb = (GR, GRBG) if c == "True" else (RED, K5BG)
                cells_ += f'<div style="width:{cw}px;flex:none">' + p(f"display:inline-block;font-family:{MONO};font-size:{fs - 2}px;font-weight:700;color:{cc};background:{cb};border-radius:10px;padding:2px 14px", c) + '</div>'
            else:
                m = k in mono_cols
                cells_ += p(f"width:{cw}px;flex:none;font-family:{MONO if m else SANS};font-size:{fs}px;font-weight:{700 if m or k == 0 else 500};color:{INK};white-space:pre", e(c))
        rid = f' id="{ids[i]}"' if ids else ""
        o.append(f'<div{rid}{bi("rise", order0 + i if order0 else None)} style="position:absolute;left:{left}px;top:{top + 56 + i * rh}px;width:{w}px;height:{rh}px;display:flex;flex-direction:row;align-items:center;gap:20px;border-bottom:2px solid {LINE}">{cells_}</div>')
    return o


EB1, EB2, EB3, EB4, EB5, EB6 = "1. 왜 필요한가", "2. 정의와 호출", "3. 매개변수와 인자", "4. return", "5. 오류와 함정", "6. 실습"
REAL = " 출력은 실제로 실행한 결과예요."
NEWK = " 이 파트는 새 커널이라 셀 번호가 [1]부터예요."
MENU = 'menu = {"coffee": 4500, "latte": 5000, "cake": 6500}'


# ---------- cover: the code panel runs off the right edge ----------
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px;display:flex;flex-direction:column">',
       p("position:absolute;left:128px;top:300px;width:760px;font-size:28px;font-weight:700;color:#F2B27A", "KANT AX/AI 엔지니어 트랙 · 보충 학습 자료"),
       '<h1 style="position:absolute;left:128px;top:360px;width:800px;font-size:96px;font-weight:900;line-height:1.12;color:#F6F5F1">함수 1<br>정의와 return</h1>',
       p("position:absolute;left:128px;top:610px;width:760px;font-size:40px;line-height:1.45;color:#BFC6D4", "자주 쓰는 계산에 이름을 붙이고<br>값을 넣어 결과를 돌려받아요")]
cov.append(f'<div style="position:absolute;left:1000px;top:250px;width:1100px;height:580px;background:#252B36;border-radius:28px;padding:64px 64px;display:flex;flex-direction:column;justify-content:center">')
for line, c in [("def calc_total(cart, menu):", "#9DBDEB"), ("    total = 0", "#E6E9EF"), ("    for m in cart:", "#E3B877"), ("        total += menu[m]", "#E6E9EF"), ("    return total", "#F2A0A0"), ("", "#E6E9EF"), ("calc_total(cart, menu)", "#8FD8DE")]:
    cov.append(p(f"font-family:{MONO};font-size:38px;font-weight:700;line-height:1.5;color:{c};white-space:pre", e(line) if line else "&#160;"))
cov.append('</div>')
W("cover", cov, "이번 챕터부터 함수를 배워요. 자주 쓰는 코드 묶음에 이름을 붙여 두고, 필요할 때 이름으로 불러 써요. 값을 넣고 결과를 돌려받는 데까지가 이번 챕터예요. 기본값, 지역 변수와 전역 변수는 20에서 이어서 배워요. 17, 18과 같은 카페 예제를 써요.", ("intro", "들어가기"))

ORDER.append("toc")

# ---------- ready: plain checklist and four steps, no cards ----------
o = [sec("ready")] + head("들어가기", "18에서 이어서 해요", JP)
done = [("hello-uv 노트북, 커널 .venv", "09"), ("변수 이름 규칙, Restart", "10"), ("f-string, 리스트, for, 튜플 꺼내 담기", "13"), ("딕셔너리 menu[\"latte\"], None", "15"), ("if, elif, else", "17"), ("range, while, break", "18")]
for i, (a_, b_) in enumerate(done):
    o.append(f'<div{bi("rise", min(i + 1, 3))} style="position:absolute;left:96px;top:{220 + i * 112}px;width:800px;height:100px;display:flex;flex-direction:row;gap:24px;align-items:center;border-bottom:2px solid {LINE}">'
             + f'<x-icon name="CheckCircle" style="width:44px;height:44px;color:{GR}"></x-icon>'
             + p(f"flex:1;font-size:32px;font-weight:700;color:{INK}", e(a_))
             + p(f"font-size:30px;font-weight:700;color:{GRAY}", e(b_)) + '</div>')
o.append(p(f"position:absolute;left:1000px;top:236px;font-size:36px;font-weight:700;color:{JP}", "노트북 다시 열기", bi("rise", 4)))
steps_ = [p(f"font-size:32px;color:{INK}", "VS Code로 hello-uv 폴더 열기"),
          p(f"font-size:32px;color:{INK}", "탐색기에서") + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{JP}", NB) + p(f"font-size:32px;color:{INK}", "열기"),
          p(f"font-size:32px;color:{INK}", "오른쪽 위 커널이 .venv인지 보기"),
          p(f"font-size:32px;color:{INK}", "셀에 적고") + kbd("Shift+Enter", 26) + p(f"font-size:32px;color:{INK}", "로 실행")]
for i, inner in enumerate(steps_):
    o.append(f'<div{bi("rise", 4)} style="position:absolute;left:1000px;top:{320 + i * 112}px;width:824px;height:100px;display:flex;flex-direction:row;gap:20px;align-items:center;border-bottom:2px solid {LINE}">' + num(i + 1, JP, 36) + inner + '</div>')
o.append(caption("기억이 안 나면 왼쪽에 적힌 챕터를 먼저 다시 봐요.", 920, 5))
W("ready", o, "09에서 만든 hello-uv 폴더를 VS Code로 열고, 12부터 쓰던 basics.ipynb를 다시 열어요. 10의 변수 이름 규칙은 함수 이름에도 그대로 써요. 13의 f-string과 for, 튜플 꺼내 담기, 15의 딕셔너리와 None, 17의 if, 18의 반복을 함수 안에서 그대로 써요. 슬라이드의 출력은 tools/demo.sh가 hello-uv 커널에서 같은 셀을 실제로 실행한 결과예요. 셀 번호는 파트마다 [1]부터 다시 셌어요.")

# ---------- part 1 ----------
o = [sec("f-why")] + head(EB1, "같은 계산을 손님마다 복사하고 있어요", K1)
WHY = [MENU, 'cart = ["coffee", "cake"]', "total = 0", "for m in cart:", "    total += menu[m]", 'print(f"합계 {total:,}원")', 'cart = ["latte", "latte", "cake"]', "total = 0", "for m in cart:", "    total += menu[m]", 'print(f"합계 {total:,}원")']
T, FS, CW = 200, 32, 1160
TX = 96 + CW + 40
o += cell({"id": "c-why", "lines": WHY, "n": 1, "out": ["합계 11,000원", "합계 16,500원"]}, 96, T, CW, FS, sel="c-why")
o.append(hl(96, T, CW, 2, 4, "mark", 1, FS))
o.append(tag(TX, (ly(T, 2, FS) + ly(T, 5, FS)) / 2, "첫 손님 합계 4줄", K1, 1))
o.append(hl(96, T, CW, 7, 4, "mark", 2, FS))
o.append(tag(TX, (ly(T, 7, FS) + ly(T, 10, FS)) / 2, "둘째 손님, 글자까지 같은 4줄", K1, 2))
o.append(tag(TX, oy(T, 11, 0, FS), "셋째 손님이 오면 또 붙여 넣어요", RED, 3, lead=False))
o.append(tag(TX, oy(T, 11, 1, FS), "할인이 생기면 전부 찾아 고쳐요", RED, 3, lead=False))
o.append(caption("같은 일을 하는 줄에 이름을 붙이고, 이름으로 불러 쓰는 게 함수예요.", 944, 4))
W("f-why", o, "같은 계산을 손님마다 복사하면 길어지고, 고칠 때 한 곳을 빠뜨리기 쉬워요. 15의 메뉴 딕셔너리로 장바구니 합계를 구했어요. 첫 손님과 둘째 손님의 계산 4줄이 글자 하나까지 똑같고 장바구니만 달라요. 손님이 늘면 이 4줄을 계속 복사해야 해요. 할인 규칙이 생기면 복사한 곳을 다 찾아서 고쳐야 하고, 한 곳만 빠뜨려도 손님마다 금액이 달라져요. 이 4줄에 이름을 붙여 두고 이름으로 부르면 고칠 곳이 한 곳이 돼요." + NEWK + REAL, ("p1", "왜 필요한가"))

# f-big: three machines; each result flies out of its box
o = [sec("f-big")] + head(EB1, "함수는 재료를 넣으면 결과가 나오는 상자예요", K1)
FX = 200
IW, AW, BW = 400, 90, 260
BX = FX + IW + 20 + AW + 20          # function box left
OX = BX + BW + 20 + AW + 20          # result left
for x, w, t, al in [(FX, IW, "재료", "right"), (BX, BW, "함수", "center"), (OX, 360, "결과", "left")]:
    o.append(p(f"position:absolute;left:{x}px;top:200px;width:{w}px;font-size:26px;font-weight:700;color:{GRAY};text-align:{al}", t))
MACH = [('["coffee", "cake"]', "len", "2", K1, K1BG), ("[6500, 4500, 5000]", "sorted", "[4500, 5000, 6500]", K2, K2BG), ("[4500, 6500]", "sum", "11000", K3, K3BG)]
for i, (inp, name, res, c, bg) in enumerate(MACH):
    y = 250 + i * 130
    cy = y + 50
    o.append(f'<div style="position:absolute;left:{FX}px;top:{y}px;width:{IW}px;height:100px;display:flex;align-items:center;justify-content:flex-end">' + mono(inp, 30, INK, "#ECEAE3") + '</div>')
    o.append(harrow(FX + IW + 20, cy, AW))
    o.append(p(f"position:absolute;left:{BX}px;top:{y}px;width:{BW}px;height:100px;border-radius:20px;background:{c};color:#FFFFFF;font-family:{MONO};font-size:40px;font-weight:700;line-height:100px;text-align:center", e(name), f' id="m-{name}"'))
    o.append(harrow(BX + BW + 20, cy, AW, c, i + 1))
    o.append(f'<div data-build-in="fly order {i + 1}" data-from="m-{name}" style="position:absolute;left:{OX}px;top:{y + 18}px;height:64px;display:flex;align-items:center">' + mono(res, 30, INK, bg, f"border:3px solid {c}") + '</div>')
T2, FS2 = 660, 28
o += cell({"id": "c-big", "lines": ['cart = ["coffee", "cake"]', "print(len(cart))", "print(sorted([6500, 4500, 5000]))", "print(sum([4500, 6500]))"], "n": 2, "out": ["2", "[4500, 5000, 6500]", "11000"]}, 96, T2, 1000, FS2, attrs=bi("rise", 4))
o.append(tag(96 + 1000 + 40, ly(T2, 1.5, FS2), "13에서 써 본 상자들이에요", K1, 4))
o.append(tag(96 + 1000 + 40, oy(T2, 4, 1, FS2), "오늘은 이런 상자를 def로 만들어요", INK, 5, 32, lead=False))
W("f-big", o, "함수는 괄호 안에 재료를 넣으면 일을 하고 결과를 내놓는 상자예요. 13에서 len, sum, sorted를 함수라고 불렀어요. len에 장바구니를 넣으면 2가 나오고, sorted에 가격 리스트를 넣으면 줄 세운 리스트가 나와요. 지금까지는 파이썬이 만들어 둔 상자만 썼어요. 오늘은 앞 장의 합계 계산처럼 늘 쓰던 줄로 상자를 직접 만들어요." + REAL)

o = [sec("f-min")] + head(EB1, "def로 만들고, 이름()으로 불러요", K1)
T, FS, CW = 220, 48, 1000
o += cell({"id": "c-min", "lines": ["def hello():", '    print("어서 오세요")', "", "hello()", "hello()"], "n": 3, "out": ["어서 오세요", "어서 오세요"]}, 96, T, CW, FS, sel="c-min")
TX = 96 + CW + 48
o.append(hl(96, T, CW, 0, 2, "mark", 1, FS))
o.append(tag(TX, ly(T, 0.5, FS), "정의: 만들어 두기", K1, 1, 36))
o.append(hl(96, T, CW, 3, 2, "run", 2, FS))
o.append(tag(TX, ly(T, 3.5, FS), "호출: 실행하기", GR, 2, 36))
o.append(f'<div{bi("fade", 3)} style="position:absolute;left:{TX - 28}px;top:{oy(T, 5, 0, FS) - 26:.0f}px;width:16px;height:{oy(T, 5, 1, FS) - oy(T, 5, 0, FS) + 52:.0f}px;border:4px solid {OR};border-left:none;border-radius:0 10px 10px 0"></div>')
o.append(tag(TX + 8, (oy(T, 5, 0, FS) + oy(T, 5, 1, FS)) / 2, "두 번 불러서 두 번 찍혀요", OR, 3, 36, lead=False))
o.append(caption("몸통은 한 번만 적고, 부른 만큼 실행돼요.", 900, 4))
W("f-min", o, "def로 함수를 만들고, 이름 뒤에 괄호를 붙여 불러요. def 다음에 함수 이름 hello와 빈 괄호, 콜론을 적어요. 다음 줄은 4칸 들여써서 함수가 할 일을 적어요. 여기까지가 함수를 만드는 정의예요. 아래 hello()는 만든 함수를 실행하는 호출이에요. 두 번 불러서 어서 오세요가 두 번 찍혔어요." + REAL)

# ---------- part 2 ----------
o = [sec("d-shape")] + head(EB2, "def 줄은 다섯 조각으로 읽어요", K2)
PT, PX, FSP = 330, 96, 96
CH = FSP * 0.6
X0 = PX + 72                         # text left inside the panel
L1Y = PT + 44 + LH(FSP) / 2          # centre of line 1
L2Y = L1Y + LH(FSP)
o.append(f'<div style="position:absolute;left:{PX}px;top:{PT}px;width:1728px;height:{88 + 2 * LH(FSP):.0f}px;background:#252B36;border-radius:26px"></div>')
o.append(f'<div{bi("fade", 5)} style="position:absolute;left:{X0}px;top:{L2Y - LH(FSP) / 2 + 10:.0f}px;width:{4 * CH:.0f}px;height:{LH(FSP) - 20:.0f}px;background:rgba(122,214,140,0.28);border-radius:10px"></div>')
o.append(p(f"position:absolute;left:{X0}px;top:{PT + 44}px;font-family:{MONO};font-size:{FSP}px;font-weight:700;line-height:1.45;color:#E6E9EF;white-space:pre",
           '<span style="color:#9DBDEB">def</span> <span style="color:#E3B877">hello</span><span style="color:#8FD8DE">()</span><span style="color:#F2A0A0">:</span><br>    print("어서 오세요")'))
PIECES = [("def", 0, 3, "만든다는 표시", BL, 0), ("hello", 4, 5, "함수 이름", OR, 0), ("()", 9, 2, "재료 칸", TEAL, 1), (":", 11, 1, "콜론 (if, for와 같아요)", RED, 2)]
LBL_Y = [230, 230, 230, 230]
lab_x = [X0 - 10, X0 + 4 * CH + 60, X0 + 9 * CH + 120, X0 + 12 * CH + 240]
for k, (t_, c0, n_, lab, col, _) in enumerate(PIECES):
    tx_ = X0 + (c0 + n_ / 2) * CH
    lx_ = lab_x[k]
    o.append(p(f"position:absolute;left:{lx_:.0f}px;top:{LBL_Y[k] - 22}px;font-size:30px;font-weight:700;color:{col};white-space:nowrap", e(lab), bi("fade", k + 1)))
    o.append(leader([(lx_ + 30, LBL_Y[k] + 28), (lx_ + 30, LBL_Y[k] + 50), (tx_, PT + 30), (tx_, PT + 44 + 12)], col, k + 1))
IND_X = X0 + 2 * CH
o.append(leader([(IND_X, 780), (IND_X, L2Y + LH(FSP) / 2 - 6)], GR, 5))
o.append(p(f"position:absolute;left:{IND_X - 30:.0f}px;top:790px;font-size:30px;font-weight:700;color:{GR};white-space:nowrap", "4칸 들여쓴 줄이 함수 몸통이에요", bi("fade", 5)))
o.append(tag(1080, 811, "이름은 하는 일로: calc_total, print_menu", GRAY, 6, 30, lead=False))
o.append(caption("모양은 if, for와 같아요. 콜론 뒤 4칸 들여쓴 줄이 한 덩어리예요.", 930, 7))
W("d-shape", o, "def 줄은 def, 이름, 괄호, 콜론, 들여쓴 몸통의 다섯 조각으로 읽어요. def는 함수를 만든다는 표시예요. hello는 함수 이름이고 10에서 배운 변수 이름 규칙을 그대로 따라요. 괄호는 재료를 받는 칸인데 지금은 비어 있어요. 3파트에서 채워요. 줄 끝 콜론과 다음 줄 4칸 들여쓰기는 17의 if, 13의 for와 같아요. 함수 이름은 calc_total처럼 하는 일이 보이게 지으면 나중에 읽기 쉬워요.", ("p2", "정의와 호출"))

o = [sec("d-def")] + head(EB2, "정의만 하면 아무것도 찍히지 않아요", K2)
T, FS, CW = 220, 40, 1000
TX = 96 + CW + 48
o += cell({"id": "c-def", "lines": ["def hello():", '    print("어서 오세요")', '    print("주문하시겠어요?")'], "n": 1}, 96, T, CW, FS)
o.append(tag(201, box_bottom(T, 3, FS) + 46, "출력 없음", GRAY, 1, 32, lead=False))
o.append(tag(TX, ly(T, 1, FS), "hello라는 이름에", K2, 1, 32))
o.append(tag(TX + 44, ly(T, 2, FS), "몸통을 기억만 해요", K2, 1, 32, lead=False))
T2 = 560
o += cell({"id": "c-call", "lines": ["hello()"], "n": None}, 96, T2, CW, FS, sel="c-call", attrs=bi("rise", 2), run=True)
o.append(cursor(2, target="c-call-run"))
o.append(outlines(96, box_bottom(T2, 1, FS), ["어서 오세요", "주문하시겠어요?"], FS, 3))
o.append(cursor_off(3))
o.append(tag(TX, oy(T2, 1, 0.5, FS), "부르면 그제야 실행돼요", GR, 3, 32))
o.append(caption("def는 기억해 두기만 하고, 실행은 이름()을 부를 때 해요.", 930, 4))
W("d-def", o, "def 셀은 실행해도 아무것도 찍히지 않고, 이름()을 불러야 몸통이 실행돼요. def 셀을 실행하면 파이썬은 hello라는 이름에 몸통 두 줄을 기억해 두기만 해요. 레시피 카드에 만드는 법을 적어 둔 것과 같아요. 다음 셀에서 hello()를 실행하면 그제야 기억한 몸통을 실행해서 두 줄이 찍혀요. 노트북에서는 def 셀을 한 번 실행해 두면 아래 셀 어디서든 부를 수 있어요." + NEWK + REAL)

# d-flow: a spotlight walks the lines in run order; badges keep the order for the PDF
o = [sec("d-flow")] + head(EB2, "부르면 몸통으로 갔다가 제자리로 돌아와요", K2)
FS = 34
TA, LA, WA = 250, 96, 1000        # hello's def (top)
TB, LB, WB = 520, 96, 1000        # the calling cell (below)
OX2 = 1240                        # outputs column
o.append(p(f"position:absolute;left:{LA + 85}px;top:200px;font-size:26px;font-weight:700;color:{GRAY}", "앞 셀에서 정의한 hello"))
o += cell({"id": "c-hello", "lines": ["def hello():", '    print("어서 오세요")', '    print("주문하시겠어요?")'], "n": 1}, LA, TA, WA, FS)
o.append(p(f"position:absolute;left:{LB + 85}px;top:{TB - 50}px;font-size:26px;font-weight:700;color:{GRAY}", "이번에 실행하는 셀"))
FLOW = ['print("가게 문 열어요")', "hello()", 'print("다음 손님")', "hello()"]
o += cell({"id": "c-flow", "lines": FLOW, "n": 3}, LB, TB, WB, FS, sel="c-flow")
o.append(p(f"position:absolute;left:{OX2}px;top:200px;font-size:26px;font-weight:700;color:{GRAY}", "출력"))
OUTS = ["가게 문 열어요", "어서 오세요", "주문하시겠어요?", "다음 손님", "어서 오세요", "주문하시겠어요?"]
# step: (cell, line, which output appears)
SEQ = [("B", 0, [0]), ("B", 1, []), ("A", 1, [1]), ("A", 2, [2]), ("B", 2, [3]), ("B", 3, []), ("A", 1, [4]), ("A", 2, [5])]
badges = {}
for k, (cl, ln, outs) in enumerate(SEQ, 1):
    left, top, w = (LA, TA, WA) if cl == "A" else (LB, TB, WB)
    y = top + 10 + ln * LH(FS)
    o.append(spot(k, left + 87, y, w - 89, LH(FS), pad=6, r="10", dim=0.4))
    badges.setdefault((cl, ln), []).append(k)
    for j in outs:
        o.append(f'<div{bi("fade", k)} style="position:absolute;left:{OX2}px;top:{250 + j * 76}px;height:64px;display:flex;flex-direction:row;align-items:center;gap:22px">'
                 + p(f"width:40px;height:40px;flex:none;border-radius:50%;background:{K2};color:#FFFFFF;font-size:22px;font-weight:900;line-height:40px;text-align:center", str(k))
                 + p(f"font-family:{MONO};font-size:{FS}px;white-space:pre;color:{INK}", e(OUTS[j])) + '</div>')
for (cl, ln), ks in badges.items():
    left, top, w = (LA, TA, WA) if cl == "A" else (LB, TB, WB)
    cy = ly(top, ln, FS)
    for m, k in enumerate(ks):
        x = left + w - 200 + m * 50
        o.append(p(f"position:absolute;left:{x}px;top:{cy - 20:.0f}px;width:40px;height:40px;border-radius:50%;background:{K2};color:#FFFFFF;font-size:22px;font-weight:900;line-height:40px;text-align:center", str(k), bi("fade", k)))
o.append(spot_off(9))
o.append(tag(LB + 105, 790, "몸통이 끝나면 부른 줄의 다음 줄로 돌아와요", K2, 9, 32, lead=False))
o.append(caption("부를 때마다 몸통을 처음부터 끝까지 실행하고 돌아와요.", 930, 9))
W("d-flow", o, "함수를 부르면 몸통으로 가서 끝까지 실행한 뒤, 부른 자리 다음 줄로 돌아와요. 앞 셀에서 hello를 정의해 뒀어요. 오른쪽 셀은 위에서 아래로 실행돼요. 첫 줄을 찍고, hello()를 만나면 왼쪽 몸통으로 가서 두 줄을 실행해요. 몸통이 끝나면 돌아와 다음 손님을 찍어요. 다시 hello()를 만나서 몸통을 한 번 더 실행해요. 동그라미 숫자가 실행 순서이고, 출력 여섯 줄이 그 순서 그대로예요." + REAL)

# ---------- part 3 ----------
o = [sec("a-one")] + head(EB3, "괄호 안에 재료 칸을 만들어요", K3)
T, FS, CW = 230, 40, 1190
A1 = [f'def greet({tok("name", "t-name", TEAL)}):', e('    print(f"{name}님, 어서 오세요")'), "", f'greet({tok(chr(34) + "kim" + chr(34), "t-kim", OR)})', f'greet({tok(chr(34) + "lee" + chr(34), "t-lee", OR)})']
o += cell({"id": "c-a1", "raw": True, "lines": A1, "n": 1, "out": [e("kim님, 어서 오세요"), e("lee님, 어서 오세요")]}, 96, T, CW, FS, sel="c-a1")
VX, VW, VH = 1340, 484, 200
o.append(var_box("v-name1", "name", VX, 230, TEAL, VW, VH, bi("rise", 1)))
o.append(val(VX, 230, VW, VH, '"kim"', OR, 1, "t-kim"))
o.append(tag(VX, 230 + VH + 34, 'greet("kim")를 부를 때', GRAY, 1, 26, lead=False))
o.append(var_box("v-name2", "name", VX, 520, TEAL, VW, VH, bi("rise", 2)))
o.append(val(VX, 520, VW, VH, '"lee"', OR, 2, "t-lee"))
o.append(tag(VX, 520 + VH + 34, 'greet("lee")를 부를 때', GRAY, 2, 26, lead=False))
o.append(p(f"position:absolute;left:96px;top:810px;font-size:34px;font-weight:700;color:{INK};white-space:nowrap", f'<span style="font-family:{MONO};color:{TEAL}">name</span>  매개변수, def 괄호 안의 칸 이름', bi("fade", 3)))
o.append(p(f"position:absolute;left:96px;top:880px;font-size:34px;font-weight:700;color:{INK};white-space:nowrap", f'<span style="font-family:{MONO};color:{OR}">"kim"</span>  인자, 부를 때 괄호에 넣는 값', bi("fade", 4)))
W("a-one", o, "부를 때 넣은 값이 괄호 안의 칸에 담겨서 몸통에서 쓰여요. 괄호 안에 name을 적으면 재료를 받는 칸이 생겨요. 이 칸을 매개변수라고 해요. greet(\"kim\")처럼 부를 때 넣는 값은 인자라고 해요. 부르면 \"kim\"이 name 칸에 담기고, 몸통의 f-string이 name 자리에 kim을 넣어 찍어요. greet(\"lee\")로 부르면 name에 lee가 담겨요. 함수는 하나인데 넣는 값에 따라 결과가 달라져요." + NEWK + REAL, ("p3", "매개변수와 인자"))

o = [sec("a-two")] + head(EB3, "재료 칸은 쉼표로 여러 개 만들어요", K3)
A2 = [f'def order({tok("menu_name", None, OR)}, {tok("qty", None, BL)}):', e('    print(f"{menu_name} {qty}잔 주문 받았어요")'), "", f'order({tok(chr(34) + "latte" + chr(34), "t-latte", OR)}, {tok("2", "t-2", BL)})', e('order("coffee", 1)')]
o += cell({"id": "c-a2", "raw": True, "lines": A2, "n": 2, "out": [e("latte 2잔 주문 받았어요"), e("coffee 1잔 주문 받았어요")]}, 96, T, CW, FS, sel="c-a2")
o.append(var_box("v-mn", "menu_name", VX, 230, OR, VW, VH, bi("rise", 1)))
o.append(val(VX, 230, VW, VH, '"latte"', INK, 1, "t-latte"))
o.append(var_box("v-qty", "qty", VX, 470, BL, VW, VH, bi("rise", 1)))
o.append(val(VX, 470, VW, VH, "2", INK, 1, "t-2"))
o.append(tag(VX, 720, "첫째 값은 첫째 칸에", INK, 2, 32, lead=False))
o.append(tag(VX, 770, "둘째 값은 둘째 칸에", INK, 2, 32, lead=False))
o.append(caption("칸이 여러 개면 쉼표로 나눠 적고, 부를 때도 쉼표로 나눠 넣어요.", 930, 3))
W("a-two", o, "재료가 두 개 필요하면 괄호 안에 쉼표로 칸을 두 개 만들어요. order는 메뉴 이름과 잔 수를 받아요. order(\"latte\", 2)로 부르면 첫째 인자 \"latte\"가 첫째 칸 menu_name에, 둘째 인자 2가 둘째 칸 qty에 담겨요. 매개변수 이름을 menu가 아니라 menu_name으로 지은 건 15의 menu 딕셔너리와 헷갈리지 않게 하려는 거예요." + REAL)

o = [sec("a-order")] + head(EB3, "인자는 적은 순서대로 칸에 들어가요", K3)
T = 230
A3 = [f'order({tok("2", "t-2b", BL)}, {tok(chr(34) + "latte" + chr(34), "t-latteb", OR)})']
o += cell({"id": "c-a3", "raw": True, "lines": A3, "n": 3, "out": [e("2 latte잔 주문 받았어요")]}, 96, T, CW, FS, sel="c-a3")
o.append(var_box("v-mn2", "menu_name", VX, 230, OR, VW, VH, bi("rise", 1)))
o.append(val(VX, 230, VW, VH, "2", RED, 1, "t-2b"))
o.append(var_box("v-qty2", "qty", VX, 470, BL, VW, VH, bi("rise", 1)))
o.append(val(VX, 470, VW, VH, '"latte"', RED, 1, "t-latteb"))
OY = oy(T, 1, 0, FS)
o.append(underline(2, 96 + 105, int(96 + 105 + tw("2 latte잔", FS)), int(OY + 30), RED))
o.append(tag(int(96 + 105 + tw("2 latte잔 주문 받았어요", FS) + 36), OY, "오류 없이 이상하게 찍혀요", RED, 2, 30))
o.append(mono("def order(menu_name, qty):", 32, GRAY, None, "position:absolute;left:96px;top:600px", bi("fade", 3)))
o.append(tag(96 + 26 * 19.2 + 40, 622, "def 줄의 칸 순서를 보고 넣어요", GRAY, 3, 30))
o.append(fix(96, 720, 'order(2, "latte")', 'order("latte", 2)', 3))
o.append(caption("칸 순서를 바꿔 넣으면 값도 바뀌어 들어가요.", 930, 4))
W("a-order", o, "인자는 뜻이 아니라 적은 순서대로 칸에 들어가요. 같은 order에 순서를 바꿔 2, \"latte\"로 넣었어요. 파이썬은 첫째 값을 첫째 칸에 넣어서 menu_name이 2, qty가 latte가 되어 2 latte잔이라고 찍혀요. 오류가 나지 않아서 더 알아채기 어려워요. 부를 때는 def 줄을 보고 칸 순서대로 넣어요. 칸 이름을 직접 적어서 순서를 신경 쓰지 않는 방법은 20에서 배워요." + REAL)

# ---------- part 4 ----------
o = [sec("r-ret")] + head(EB4, "return은 결과를 부른 자리로 돌려줘요", K4)
T, FS, CW = 220, 36, 980
R1 = [e("def price_of(qty):"), f'    return {tok("4500 * qty", "t-ret", K4)}', "", e("x = price_of(2)"), e("print(x)"), e("print(price_of(3) + 1000)")]
o += cell({"id": "c-r1", "raw": True, "lines": R1, "n": 1, "out": ["9000", "14500"]}, 96, T, CW, FS, sel="c-r1")
o.append(hl(96, T, CW, 1, 1, "mark", 1, FS, "돌려줄 값"))
CX = 1160
o.append(p(f"position:absolute;left:{CX}px;top:220px;font-size:26px;font-weight:700;color:{GRAY}", "부른 자리가 값으로 바뀌어요", bi("fade", 2)))
o.append(mono("x = price_of(2)", 34, INK, None, f"position:absolute;left:{CX}px;top:280px", bi("rise", 2)))
o.append(p(f"position:absolute;left:{CX}px;top:356px;font-family:{MONO};font-size:34px;font-weight:700;line-height:1.4;color:{INK};white-space:pre", "x = ", bi("rise", 2)))
o.append(f'<div data-build-in="fly order 2" data-from="t-ret" style="position:absolute;left:{CX + 4 * 20.4:.0f}px;top:350px">' + mono("9000", 34, K4, K4BG) + '</div>')
o.append(mono("price_of(3) + 1000", 34, INK, None, f"position:absolute;left:{CX}px;top:540px", bi("rise", 3)))
o.append(f'<div data-build-in="fly order 3" data-from="t-ret" style="position:absolute;left:{CX}px;top:610px">' + mono("13500", 34, K4, K4BG) + '</div>')
o.append(p(f"position:absolute;left:{CX + 5 * 20.4 + 56:.0f}px;top:616px;font-family:{MONO};font-size:34px;font-weight:700;line-height:1.4;color:{INK};white-space:pre", "+ 1000", bi("rise", 3)))
o.append(harrow(CX, 760, 70, "#B4B9C3", 4))
o.append(at(CX + 96, 732, mono("14500", 34, INK, "#ECEAE3"), bi("rise", 4)))
o.append(caption("return 뒤의 값이 함수를 부른 자리에 들어가요.", 930, 5))
W("r-ret", o, "return은 계산한 값을 들고 함수를 나가서, 함수를 부른 자리에 그 값을 놓아요. 지금까지 만든 함수는 print로 찍기만 했어요. price_of는 잔 수를 받아 4500을 곱한 값을 돌려줘요. x = price_of(2)는 부른 자리가 9000으로 바뀌어서 x = 9000이 돼요. price_of(3) + 1000도 13500 + 1000으로 바뀐 뒤 14500이 돼요. 13의 len과 sum이 값을 돌려준 것과 같은 방식이에요." + NEWK + REAL, ("p4", "return"))

o = [sec("r-vs")] + head(EB4, "print는 화면에 찍기만, return은 값을 돌려줘요", K4)
T, FS, CW = 270, 32, 840
o.append(p(f"position:absolute;left:96px;top:205px;font-size:30px;font-weight:700;color:{OR}", "print로 찍는 함수"))
o += cell({"id": "c-r2", "lines": ["def show(qty):", "    print(4500 * qty)", "", "a = show(2)", 'print("a:", a)'], "n": 2, "out": ["9000", "a: None"]}, 96, T, CW, FS)
o.append(hl(96, T, CW, 1, 1, "skip", None, FS))
o.append(p(f"position:absolute;left:984px;top:205px;font-size:30px;font-weight:700;color:{K4}", "return으로 돌려주는 함수"))
o += cell({"id": "c-r3", "lines": ["def calc(qty):", "    return 4500 * qty", "", "b = calc(2)", 'print("b:", b)', "print(b + 1000)"], "n": 3, "out": ["b: 9000", "10000"]}, 984, T, CW, FS)
o.append(hl(984, T, CW, 1, 1, "mark", None, FS))
ya = oy(T, 5, 1, FS)
o.append(box(1, 96 + 105 - 14, int(ya - 28), int(tw("a: None", FS)) + 28, 56, OR))
o.append(tag(96 + 105, 750, "9000은 찍혔을 뿐, a에는 None", OR, 1, 32, lead=False))
yb = oy(T, 6, 0, FS)
o.append(box(2, 984 + 105 - 14, int(yb - 28), int(tw("b: 9000", FS)) + 28, 56, GR))
o.append(tag(984 + 105, 750, "b에 9000이 담겨서 더할 수 있어요", GR, 2, 32, lead=False))
o.append(caption("사람이 볼 값은 print, 다음 계산에 쓸 값은 return이에요.", 930, 3))
W("r-vs", o, "print는 화면에 찍기만 하고, return은 값을 돌려줘서 변수에 담을 수 있어요. 가장 많이 헷갈리는 부분이라 두 함수를 한 줄만 다르게 나란히 놓았어요. 왼쪽 show는 9000을 찍지만 돌려준 값이 없어서 a에는 None이 담겨요. 오른쪽 calc는 화면에 찍지 않지만 b에 9000이 담겨서 1000을 더할 수 있어요. 화면에 보이는 것과 변수에 담기는 것은 달라요." + REAL)

o = [sec("r-none")] + head(EB4, "return이 없으면 None을 돌려줘요", K4)
T, FS, CW = 220, 36, 900
TX = 96 + CW + 48
o += cell({"id": "c-r4", "lines": ['result = print("안녕")', "print(result)", "print(type(result))"], "n": 4, "out": ["안녕", "None", "<class 'NoneType'>"]}, 96, T, CW, FS, sel="c-r4")
y1 = oy(T, 3, 1, FS)
o.append(underline(1, 96 + 105, int(96 + 105 + tw("None", FS)), int(y1 + 28), K4))
o.append(tag(TX, y1, "print도 돌려주는 값이 없어요", K4, 1, 32))
o.append(tag(TX, oy(T, 3, 2, FS), "None은 '값이 없음', 15의 get과 같아요", GRAY, 2, 30))
T2 = 650
o += cell({"id": "c-r5", "lines": ["def hi():", '    print("안녕")', "print(hi())"], "n": 5, "out": ["안녕", "None"]}, 96, T2, CW, FS, attrs=bi("rise", 3))
o.append(tag(TX, oy(T2, 3, 1, FS), "직접 만든 함수도 return이 없으면 None", K4, 3, 32))
W("r-none", o, "몸통 끝까지 return을 만나지 않으면 파이썬이 None을 대신 돌려줘요. print도 함수라서 결과를 변수에 담아 볼 수 있어요. 안녕은 화면에 찍히고, result에는 None이 담겨요. type으로 보면 NoneType이에요. 15에서 get이 없는 키를 만났을 때 돌려준 그 None이에요. 5번 셀의 hi도 return이 없어서 print(hi())가 None을 찍어요. 돌려받은 값이 None이면 함수에 return이 있는지 먼저 봐요." + REAL)

o = [sec("r-stop")] + head(EB4, "return을 만나면 함수가 바로 끝나요", K4)
T, FS, CW = 220, 34, 960
TX = 96 + CW + 44
CHK = ["def check(stock):", "    if stock == 0:", '        return "품절"', '    return "주문 가능"', "", "print(check(0))", "print(check(3))"]
o += cell({"id": "c-r6", "lines": CHK, "n": 6, "out": ["품절", "주문 가능"]}, 96, T, CW, FS, sel="c-r6")
o.append(hl(96, T, CW, 2, 1, "run", 1, FS))
o.append(tag(TX, ly(T, 2, FS), "check(0)은 여기서 끝", GR, 1, 30))
o.append(hl(96, T, CW, 3, 1, "skip", 1, FS))
o.append(tag(TX, ly(T, 3, FS), "check(0)은 여기까지 안 와요", GRAY, 1, 30))
o += rows_table(TX, 560, [190, 170, 280], ["부르기", "stock == 0", "만난 return"], [("check(0)", "True", 'return "품절"'), ("check(3)", "False", 'return "주문 가능"')], 2, 80, 26, mono_cols=(0, 2))
o.append(caption("return은 값을 돌려주면서 함수를 끝내요. 그래서 else가 없어도 돼요.", 930, 4))
W("r-stop", o, "return은 값을 돌려주는 동시에 함수를 끝내요. 18에서 break가 반복을 끝낸 것처럼요. check(0)은 if가 True라서 return \"품절\"을 만나고 바로 나가요. 그 아래 return \"주문 가능\"까지 가지 않아요. check(3)은 if가 False라서 아래로 내려가 주문 가능을 돌려줘요. 그래서 else를 쓰지 않아도 돼요. 17처럼 if, else로 나눠 써도 결과는 같아요." + REAL)

o = [sec("r-multi")] + head(EB4, "쉼표로 값 여러 개를 한 번에 돌려줘요", K4)
T, FS, CW = 220, 38, 1010
RM = [e("def summary(prices):"), e("    return sum(prices), len(prices)"), "", e("print(summary([4500, 5000, 6500]))"), e("total, n = summary([4500, 5000, 6500])"), e("print(total, n)")]
o += cell({"id": "c-r7", "raw": True, "lines": RM, "n": 7, "out": [f'({tok("16000", "t-16000")}, {tok("3", "t-3")})', e("16000 3")]}, 96, T, CW, FS, sel="c-r7")
y0 = oy(T, 6, 0, FS)
o.append(underline(1, 96 + 105, int(96 + 105 + tw("(16000, 3)", FS)), int(y0 + 28), K4))
o.append(tag(int(96 + 105 + tw("(16000, 3)", FS) + 36), y0, "괄호로 묶인 튜플 하나로 와요 (13)", K4, 1, 30))
VX2 = 1170
o.append(var_box("v-total", "total", VX2, 230, K4, 370, 230, bi("rise", 2)))
o.append(val(VX2, 230, 370, 230, "16000", INK, 2, "t-16000", 60))
o.append(var_box("v-n", "n", VX2 + 400, 230, BL, 254, 230, bi("rise", 2)))
o.append(val(VX2 + 400, 230, 254, 230, "3", INK, 2, "t-3", 60))
o.append(tag(VX2, 520, "13의 꺼내 담기와 같아요", INK, 3, 30, lead=False))
o.append(tag(VX2, 575, "왼쪽 이름 수 = 돌려준 값 수", GRAY, 3, 28, lead=False))
o.append(caption("return a, b는 튜플로 돌려주고, x, y = 함수()로 나눠 받아요.", 930, 4))
W("r-multi", o, "return 뒤에 쉼표로 값을 이어 적으면 튜플 하나로 돌려줘요. 합계와 개수를 같이 알고 싶을 때 써요. 그대로 찍으면 괄호로 묶인 (16000, 3)이 나와요. 13에서 배운 튜플이에요. 받을 때는 13의 꺼내 담기처럼 total, n = summary(...)로 적으면 두 변수에 하나씩 담겨요. 이 장은 가볍게 보고 넘어가도 돼요." + REAL)

# ---------- part 5 ----------
o = [sec("t-paren")] + head(EB5, "괄호를 빼면 실행하지 않고 함수 자체가 나와요", K5)
T, FS, CW = 220, 34, 1100
o += cell({"id": "c-t1", "lines": ["def hello():", '    print("어서 오세요")', "", "hello"], "n": 1, "out": ["<function __main__.hello()>"]}, 96, T, CW, FS, sel="c-t1")
y0 = oy(T, 4, 0, FS)
s0 = "<function __main__.hello()>"
o.append(underline(1, 96 + 105, int(96 + 105 + tw(s0, FS)), int(y0 + 28), RED))
o.append(tag(int(96 + 105 + tw(s0, FS) + 36), y0, "실행하지 않고 함수만 보여 줘요", RED, 1, 30))
T2 = 560
s1 = "<function hello at 0x7efc68143530>"
o += cell({"id": "c-t2", "lines": ["print(hello)"], "n": 2, "out": [s1]}, 96, T2, CW, FS, attrs=bi("rise", 2))
o.append(tag(int(96 + 105 + tw(s1, FS) + 36), oy(T2, 1, 0, FS), "0x 뒤 숫자는 실행마다 달라요", GRAY, 2, 30))
o.append(fix(96, 790, "hello", "hello()", 3, 36))
o.append(caption("부를 때는 재료가 없어도 괄호 ()를 꼭 붙여요.", 930, 4))
W("t-paren", o, "괄호를 빼고 이름만 적으면 함수를 실행하지 않고 함수 자체를 보여 줘요. 셀 마지막 줄에 hello만 적으면 노트북이 함수 자체를 보여 주고, print(hello)로 찍으면 function hello at 뒤에 숫자가 나와요. 그 숫자는 함수가 저장된 메모리 위치라서 실행할 때마다 달라져요. 수강생 화면과 슬라이드 숫자가 달라도 괜찮아요. 함수를 실행하려면 재료가 없어도 괄호를 붙여요." + NEWK + REAL, ("p5", "오류와 함정"))

o = [sec("t-args")] + head(EB5, "칸 수와 인자 수가 다르면 TypeError가 나요", K5)
T, FS, CW = 220, 30, 1728
E1 = "TypeError: order() missing 1 required positional argument: 'qty'"
E2 = "TypeError: order() takes 2 positional arguments but 3 were given"
o += cell({"id": "c-t3", "lines": ["def order(menu_name, qty):", '    print(f"{menu_name} {qty}잔 주문 받았어요")', "", 'order("latte")'], "n": 3, "out": [E1], "err": True}, 96, T, CW, FS, sel="c-t3")
y1 = oy(T, 4, 0, FS)
x1 = lx(96, "TypeError: order() missing 1 required positional argument: ", FS)
o.append(ring(1, int(x1) + 16, int(y1 - 18), int(tw("'qty'", FS)) - 16, 36, RED))
o.append(tag(int(lx(96, E1, FS) + 60), y1, "qty 칸이 비었어요", RED, 1, 30))
T2 = 560
o += cell({"id": "c-t4", "lines": ['order("latte", 2, "L")'], "n": 4, "out": [E2], "err": True}, 96, T2, CW, FS, attrs=bi("rise", 2))
y2 = oy(T2, 1, 0, FS)
o.append(underline(3, int(lx(96, "TypeError: order() ", FS)), int(lx(96, E2, FS)), int(y2 + 24), RED))
o.append(tag(int(lx(96, E2, FS) + 60), y2, "칸은 2개, 넣은 값은 3개", RED, 3, 30))
o.append(fix(96, 790, ['order("latte")', 'order("latte", 2, "L")'], 'order("latte", 2)', 4, 32))
o.append(caption("def 줄의 칸 수만큼 인자를 넣어요.", 930, 5))
W("t-args", o, "def 줄의 칸 수와 부를 때 넣은 인자 수가 다르면 TypeError가 나요. 칸이 두 개인 order에 인자를 하나만 넣으면 missing 1 required positional argument: 'qty'가 나요. qty 칸에 들어갈 값이 없다는 뜻이에요. 세 개를 넣으면 takes 2 positional arguments but 3 were given이 나요. 칸은 2개인데 3개를 받았다는 뜻이에요. 오류가 나면 def 줄을 보고 칸 수를 세어 봐요. Traceback 위쪽 줄은 빼고 마지막 줄만 옮겼어요." + REAL)

o = [sec("t-dead")] + head(EB5, "return 아래에 적은 줄은 실행되지 않아요", K5)
T, FS, CW = 220, 36, 980
TX = 96 + CW + 44
DEAD = ["def calc(qty):", "    total = 4500 * qty", "    return total", '    print("계산 끝")', "", "print(calc(2))"]
o += cell({"id": "c-t5", "lines": DEAD, "n": 5, "out": ["9000"]}, 96, T, CW, FS, sel="c-t5")
o.append(hl(96, T, CW, 2, 1, "run", 1, FS))
o.append(tag(TX, ly(T, 2, FS), "여기서 함수를 나가요", GR, 1, 30))
o.append(hl(96, T, CW, 3, 1, "skip", 1, FS))
o.append(tag(TX, ly(T, 3, FS), "그래서 이 줄은 안 와요", GRAY, 1, 30))
yo = oy(T, 6, 0, FS)
o.append(tag(int(96 + 105 + tw("9000", FS) + 36), yo, "계산 끝이 없는데 오류도 없어요", RED, 2, 30))
o.append(p(f"position:absolute;left:{TX}px;top:560px;font-size:28px;font-weight:700;color:{GR}", "print를 return 위로 옮겨요", bi("rise", 3)))
FIXD = ["def calc(qty):", "    total = 4500 * qty", '    print("계산 끝")', "    return total"]
o += cell({"id": "c-t5b", "lines": FIXD, "n": None}, TX - 85, 610, 1824 - TX + 85, 28, attrs=bi("rise", 3))
o.append(hl(TX - 85, 610, 1824 - TX + 85, 2, 1, "run", 3, 28))
o.append(caption("함수에서 할 일을 다 적고 return은 마지막에 둬요.", 930, 4))
W("t-dead", o, "return 아래에 적은 줄은 실행되지 않아요. 실행하면 9000만 나오고 계산 끝은 찍히지 않아요. return을 만나서 함수를 이미 나갔기 때문이에요. 오류가 나지 않아서 빠진 줄을 알아채기 어려워요. 함수 안에서 할 일을 다 적은 뒤 return을 마지막에 둬요. 앞의 check처럼 if 안의 return은 괜찮아요. 그 return을 만났을 때만 나가요." + REAL)

o = [sec("t-none")] + head(EB5, "찍기만 하는 함수로 계산하면 TypeError가 나요", K5)
T, FS, CW = 220, 32, 1728
E3 = "TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'"
o += cell({"id": "c-t6", "lines": ["def show(qty):", "    print(4500 * qty)", "", "show(2) + 1000"], "n": 6, "out": ["9000", "", E3], "err": True}, 96, T, CW, FS, sel="c-t6")
ye = oy(T, 4, 2, FS)
o.append(box(1, int(lx(96, "TypeError: unsupported operand type(s) for +: ", FS)) - 8, int(ye - 27), int(tw("'NoneType'", FS)) + 16, 54, RED))
o.append(mono("show(2) + 1000", 34, INK, "#ECEAE3", "position:absolute;left:96px;top:660px", bi("rise", 2)))
o.append(harrow(96 + int(14 * 20.4) + 70, 690, 70, RED, 2))
o.append(mono("None + 1000", 34, RED, K5BG, f"position:absolute;left:{96 + int(14 * 20.4) + 170}px;top:660px", bi("rise", 2)))
o.append(tag(96 + int(14 * 20.4) + 170 + int(11 * 20.4) + 80, 690, "None에는 더할 수 없어요", RED, 2, 30, lead=False))
o.append(fix(96, 790, "print(4500 * qty)", "return 4500 * qty", 3, 32))
o.append(caption("NoneType이 보이면 return이 빠진 함수를 찾아요.", 930, 4))
W("t-none", o, "찍기만 하는 함수는 None을 돌려줘서, 그 값으로 계산하면 TypeError가 나요. show(2)는 9000을 찍지만 돌려주는 값은 None이에요. 그래서 show(2) + 1000은 None + 1000이 되고, None과 정수는 더할 수 없다는 오류가 나요. print와 return을 비교한 장의 a와 같아요. 오류 메시지에 NoneType이 보이면 return이 빠진 함수가 있는지 찾아요. 계산에 쓸 값은 print 대신 return으로 돌려줘요." + REAL)

o = [sec("t-name")] + head(EB5, "정의보다 먼저 부르면 NameError가 나요", K5)
T, FS, CW = 210, 34, 1000
TX = 96 + CW + 44
E4 = "NameError: name 'welcome' is not defined"
o += cell({"id": "c-t7", "lines": ["welcome()", "", "def welcome():", '    print("어서 오세요")'], "n": 1, "out": [E4], "err": True}, 96, T, CW, FS, sel="c-t7")
o.append(hl(96, T, CW, 0, 1, "err", 1, FS))
o.append(tag(TX, ly(T, 0, FS), "아직 def를 만나기 전이에요", RED, 1, 30))
o.append(tag(TX, ly(T, 2.5, FS), "오류에서 멈춰서 여기까지 못 와요", GRAY, 1, 30))
T2 = 530
o += cell({"id": "c-t8", "lines": ["welcome()"], "n": 2, "out": [E4], "err": True}, 96, T2, CW, FS, attrs=bi("rise", 2))
o.append(tag(TX, oy(T2, 1, 0, FS), "다시 불러도 같은 오류", RED, 2, 30))
BY = 740
bar = [f'<div id="nb-bar" style="position:absolute;left:96px;top:{BY}px;width:1000px;height:64px;background:#ECEAE3;border-radius:14px;display:flex;flex-direction:row;align-items:center;padding:0 22px;gap:26px">',
       p(f"font-family:{MONO};font-size:22px;font-weight:700;color:{INK}", NB),
       p(f"font-size:20px;color:{SUB}", "▷ Run All"), p(f"font-size:20px;font-weight:700;color:{INK}", "↻ Restart", ' id="nb-restart"'), p(f"font-size:20px;color:{SUB}", "Clear All Outputs"), '</div>']
o.append(f'<div{bi("rise", 3)}>' + "".join(bar) + '</div>')
o.append(cursor(3, target="nb-restart"))
o.append(tag(TX, BY + 32, "def 셀을 지워도 커널은 기억해요", OR, 3, 30))
o.append(tag(TX, BY + 84, "Restart 뒤 위에서부터 실행하면 드러나요", OR, 3, 28, lead=False))
o.append(cursor_off(4))
o.append(caption("def 셀을 먼저 실행하고, 부르는 셀은 아래에 둬요.", 930, 4))
W("t-name", o, "파이썬은 위에서부터 실행해서, def보다 먼저 부르면 그런 이름이 없다는 NameError가 나요. 첫 줄에서 welcome을 찾았는데 아직 def를 만나지 않았어요. 오류에서 셀이 멈춰서 아래 def도 실행되지 않았어요. 그래서 다음 셀에서 다시 불러도 같은 오류가 나요. 노트북에서는 def 셀을 지워도 커널이 함수를 기억하고 있어서 괜찮아 보이다가, 10에서 배운 Restart 뒤에 위에서부터 실행하면 오류가 드러나요. 이 두 셀은 따로 띄운 새 커널에서 실행했어요." + REAL)

# ---------- part 6 ----------
o = [sec("x-total")] + head(EB6, "장바구니 총액을 함수로 만들어요", K6)
T, FS, CW = 196, 30, 1100
TX = 96 + CW + 40
TOT = [MENU, "", "def calc_total(cart, menu):", "    total = 0", "    for m in cart:", "        total += menu[m]", "    return total", "", 'cart1 = ["coffee", "cake"]', 'cart2 = ["latte", "latte", "cake"]', 'print(f"합계 {calc_total(cart1, menu):,}원")', 'print(f"합계 {calc_total(cart2, menu):,}원")']
o += cell({"id": "c-x1", "lines": TOT, "n": 1, "out": ["합계 11,000원", "합계 16,500원"]}, 96, T, CW, FS, sel="c-x1")
o.append(hl(96, T, CW, 3, 3, "mark", 1, FS))
o.append(tag(TX, ly(T, 4, FS), "1파트에서 복사하던 4줄", K1, 1))
o.append(hl(96, T, CW, 10, 2, "run", 2, FS))
o.append(tag(TX, ly(T, 10.5, FS), "손님마다 한 줄", GR, 2))
o.append(tag(TX, ly(T, 2, FS), "할인이 생기면 여기만 고쳐요", K6, 3))
o.append(caption("반복해서 쓰는 계산은 함수로 묶고, return으로 결과를 돌려받아요.", 944, 4))
W("x-total", o, "1파트에서 손님마다 복사했던 합계 계산을 calc_total 함수 하나로 바꿨어요. calc_total은 장바구니와 메뉴판을 받아서 합계를 돌려줘요. 함수 안의 4줄은 1파트와 같고, 마지막에 return total을 붙였어요. 부를 때는 f-string 안에서 바로 불러서 13의 천 단위 콤마로 찍었어요. 손님이 늘어도 한 줄씩만 더하면 되고, 할인이 생기면 calc_total만 고치면 돼요." + NEWK + REAL, ("p6", "실습"))

o = [sec("x-soldout")] + head(EB6, "주문할 수 있는지 True, False로 돌려줘요", K6)
T, FS, CW = 196, 30, 1060
CAN = ["def can_order(stock, name):", "    if stock[name] > 0:", "        return True", "    return False", "", 'stock = {"coffee": 3, "latte": 0, "cake": 2}', 'for o in ["coffee", "latte", "cake"]:', "    if can_order(stock, o):", '        print(o, "주문 받았어요")', "    else:", '        print(o, "품절이에요")']
o += cell({"id": "c-x2", "lines": CAN, "n": 2, "out": ["coffee 주문 받았어요", "latte 품절이에요", "cake 주문 받았어요"]}, 96, T, CW, FS, sel="c-x2")
o.append(hl(96, T, CW, 7, 1, "mark", 1, FS, "주문할 수 있나요?"))
TBX = 1220
o += rows_table(TBX, 206, [150, 160, 234], ["o", "stock[o]", "돌려준 값"], [("coffee", "3", "True"), ("latte", "0", "False"), ("cake", "2", "True")], 2, 80, 28, ids=["sr0", "sr1", "sr2"], mono_cols=(0, 1))
o.append(box(5, TBX - 12, 206 + 56 + 80 - 4, 604, 88, RED))
o.append(tag(TBX, 560, "False라서 else로 가요", RED, 5, 30, lead=False))
o.append(caption("True, False를 돌려주는 함수는 if 뒤에 바로 써요.", 944, 6))
W("x-soldout", o, "True나 False를 돌려주는 함수는 if 뒤에 바로 써서 질문처럼 읽혀요. 15의 재고 딕셔너리로 주문할 수 있는지 묻는 함수를 만들었어요. 재고가 0보다 크면 True를 돌려주고 끝내요. 아니면 아래 return False까지 가요. 반복에서는 if can_order(stock, o):처럼 if 뒤에 함수를 바로 써요. 돌려준 True나 False가 if 조건이 돼요. latte는 재고가 0이라 False가 돌아와서 else로 가요." + REAL)

o = [sec("x-grade")] + head(EB6, "17의 등급 계산을 함수로 바꿔요", K6)
T, FS, CW = 190, 28, 1210
GRD = ["def grade(score):", "    if score >= 90:", '        return "A"', "    elif score >= 80:", '        return "B"', "    elif score >= 70:", '        return "C"', '    return "F"', "", 'scores = [["kim", 92], ["lee", 78], ["park", 85], ["choi", 59]]', "for name, score in scores:", '    print(f"{name:<5}{score:>3}  {grade(score)}")']
o += cell({"id": "c-x3", "lines": GRD, "n": 3, "out": ["kim   92  A", "lee   78  C", "park  85  B", "choi  59  F"]}, 96, T, CW, FS, sel="c-x3")
SX = 96 + CW + 40
o.append(hl(96, T, CW, 0, 8, "mark", 1, FS))
o.append(tag(SX, ly(T, 3.5, FS), "등급 정하기만 함수로 뺐어요", K6, 1, 30))
o.append(p(f"position:absolute;left:{SX}px;top:540px;font-size:26px;font-weight:700;color:{GRAY}", "17에서는 for 안에 이만큼 있었어요", bi("rise", 2)))
OLD = ["for name, score in scores:", "    if score >= 90:", '        grade = "A"', "    elif score >= 80:", '        grade = "B"', "    ...", "    print(... grade)"]
o.append(f'<div{bi("rise", 2)} style="position:absolute;left:{SX}px;top:590px;width:{1824 - SX}px;padding:16px 22px;background:#ECEAE3;border-radius:14px;display:flex;flex-direction:column">'
         + "".join(p(f"font-family:{MONO};font-size:22px;line-height:1.45;white-space:pre;color:{SUB}", e(l)) for l in OLD) + '</div>')
o.append(hl(96, T, CW, 11, 1, "run", 3, FS))
o.append(tag(520, oy(T, 12, 1.5, FS), "for 안에는 찍는 줄 하나만 남았어요", GR, 3, 30))
W("x-grade", o, "17의 성적표에서 등급을 정하는 부분만 grade 함수로 뺐어요. 17에서는 for 안에 if, elif를 길게 적고 grade 변수에 등급을 담았어요. 이번에는 조건마다 바로 return해서 grade 변수가 필요 없어요. for 안에는 찍는 줄 하나만 남아서 무엇을 하는지 한눈에 보여요. 점수 기준이 바뀌면 grade 함수만 고쳐요." + REAL)

o = [sec("x-pay")] + head(EB6, "함수 안에서 다른 함수를 불러요", K6)
T, FS, CW = 180, 28, 980
PAY = ["def discount_rate(total):", "    if total >= 20000:", "        return 10", "    elif total >= 10000:", "        return 5", "    return 0", "", "def pay(total):", "    rate = discount_rate(total)", "    sale = total * rate // 100", "    return total - sale", "", "print(pay(8000))", "print(pay(15500))", "print(pay(22000))"]
o += cell({"id": "c-x4", "lines": PAY, "n": 4, "out": ["8000", "14725", "19800"]}, 96, T, CW, FS, sel="c-x4")
o.append(hl(96, T, CW, 8, 1, "mark", 1, FS, "다른 함수 부르기"))
PX2 = 1140
o += rows_table(PX2, 200, [140, 100, 120, 164], ["total", "rate", "sale", "pay()"], [("8000", "0", "0", "8000"), ("15500", "5", "775", "14725"), ("22000", "10", "2200", "19800")], None, 86, 30, ids=["pr0", "pr1", "pr2"], mono_cols=(0, 1, 2, 3))
for k in range(3):
    o.append(spot(2 + k, target=f"pr{k}", pad=10, r="12", dim=0.5))
o.append(spot_off(5))
o.append(tag(PX2, 600, "15500원은 5% 할인, 775원이 빠져요", INK, 5, 30, lead=False))
o.append(tag(PX2, 660, "기준이 바뀌면 discount_rate만 고쳐요", K6, 5, 30, lead=False))
W("x-pay", o, "함수 안에서 다른 함수를 불러서 일을 나눌 수 있어요. 17에서 합계에 따라 할인율을 정했던 규칙을 함수 두 개로 나눴어요. discount_rate는 합계를 받아 할인율을 돌려줘요. pay는 그 함수를 불러서 할인율을 받고, 할인 금액을 뺀 결제 금액을 돌려줘요. 오른쪽 표처럼 15500원은 5% 할인으로 775원이 빠져 14725원이에요. 작은 함수로 나누면 하나씩 고치고 확인하기 쉬워요." + REAL)

# ---------- wrap up ----------
o = [sec("trouble")] + head("정리", "막히면 오류의 마지막 줄을 봐요", RED)
tr = [("<function hello at 0x...>", "괄호를 빼서 실행하지 않았어요", "hello()"),
      ("missing 1 required positional argument", "인자를 덜 넣었어요", "def 줄 칸 수 세기"),
      ("takes 2 positional arguments but 3 were given", "인자를 더 넣었어요", "def 줄 칸 수 세기"),
      ("NameError: name 'welcome' is not defined", "def 셀보다 먼저 불렀어요", "def 셀 먼저 실행"),
      ("돌려받은 값이 None", "함수에 return이 없어요", "print 대신 return"),
      ("'NoneType' and 'int'", "None으로 계산했어요", "return 넣기"),
      ("return 아래 print가 안 찍혀요", "return에서 함수가 끝났어요", "return 위로 옮기기")]
o.append(f'<div style="position:absolute;left:96px;top:196px;width:1728px;height:50px;display:flex;flex-direction:row;gap:30px;border-bottom:3px solid {INK}">'
         + p(f"width:900px;font-size:24px;font-weight:700;color:{GRAY}", "보이는 것") + p(f"width:460px;font-size:24px;font-weight:700;color:{GRAY}", "까닭") + p(f"font-size:24px;font-weight:700;color:{GRAY}", "고치기") + '</div>')
for i, (q, a_, cmd) in enumerate(tr):
    o.append(f'<div{bi("rise", min(i + 1, 6))} style="position:absolute;left:96px;top:{252 + i * 94}px;width:1728px;height:94px;display:flex;flex-direction:row;gap:30px;align-items:center;border-bottom:2px solid {LINE}">'
             + p(f"width:900px;flex:none;{'font-family:' + MONO + ';font-size:28px;' if q.isascii() else 'font-size:30px;'}font-weight:700;color:{INK};white-space:nowrap", e(q))
             + p(f"width:460px;flex:none;font-size:28px;color:{SUB}", e(a_))
             + p(f"{'font-family:' + MONO + ';font-size:28px;' if cmd.isascii() else 'font-size:28px;'}font-weight:700;color:{GR};white-space:nowrap", e(cmd)) + '</div>')
o.append(caption("결과가 이상하면 함수 안에 print를 넣어 받은 값을 찍어 봐요.", 944, 6))
W("trouble", o, "함수에서 자주 만나는 일곱 가지와 고치는 법이에요. 첫째 줄은 괄호를 빼서 함수를 실행하지 않은 경우예요. 둘째와 셋째 줄은 칸 수와 인자 수가 맞지 않아요. def 줄을 보고 칸을 세어 봐요. 넷째 줄은 노트북에서 셀 순서가 꼬였을 때 자주 나요. 다섯째와 여섯째 줄은 return이 빠진 함수예요. 마지막 줄은 오류 없이 줄이 빠지는 경우예요. 결과가 이상하면 함수 안에 print를 넣어 매개변수에 무엇이 들어왔는지 찍어 보면 원인이 보여요.", ("trouble", "정리"))

# cheatsheet: one annotated function instead of eight cards
o = [sec("cheatsheet")]
o.append(f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>')
PT, FSC = 200, 40
CHL = [("def calc(price, qty):", "#9DBDEB"), ("    return price * qty", "#F2A0A0"), ("", "#E6E9EF"), ("x = calc(4500, 2)", "#8FD8DE"), ("a, b = summary(prices)", "#E3B877")]
o.append(f'<div style="position:absolute;left:96px;top:{PT}px;width:900px;height:{80 + len(CHL) * LH(FSC):.0f}px;background:#252B36;border-radius:24px;padding:40px 48px;display:flex;flex-direction:column">'
         + "".join(p(f"font-family:{MONO};font-size:{FSC}px;font-weight:700;line-height:1.45;color:{c};white-space:pre", e(l) if l else "&#160;") for l, c in CHL) + '</div>')
LBLS = [(0, "정의", "def 이름(매개변수):, 콜론 뒤 4칸 몸통", K2), (1, "return", "값을 돌려주고 바로 끝내요. 없으면 None", K4), (3, "호출", "이름(인자), 인자는 적은 순서대로 칸에", K3), (4, "값 두 개", "return a, b는 튜플, 받을 땐 꺼내 담기", K4)]
for ln, t_, d_, c in LBLS:
    cy = PT + 40 + ln * LH(FSC) + LH(FSC) / 2
    o.append(f'<div style="position:absolute;left:1040px;top:{cy - 24:.0f}px;display:flex;flex-direction:row;align-items:baseline;gap:20px;white-space:nowrap">'
             + p(f"width:150px;flex:none;font-size:32px;font-weight:700;color:{c}", "← " + e(t_)) + p(f"font-size:28px;color:{INK}", e(d_)) + '</div>')
o += rows_table(96, 620, [220, 1000], ["", "언제 쓰나요"], [("print", "사람이 화면에서 볼 값을 찍을 때"), ("return", "결과를 변수에 담거나 다음 계산에 쓸 때")], None, 80, 30, mono_cols=(0,))
o.append(p(f"position:absolute;left:96px;top:880px;width:1728px;font-size:32px;font-weight:700;color:{INK}", "다음 챕터 20: 기본값, 키워드 인자, 지역 변수와 전역 변수"))
W("cheatsheet", o, "이번 챕터에서 쓴 모양을 함수 하나에 모았어요. def로 만들고 이름과 괄호로 불러요. 괄호 안의 칸이 매개변수, 부를 때 넣는 값이 인자이고 순서대로 짝을 지어요. return은 값을 돌려주면서 함수를 끝내고, return이 없으면 None이 돌아와요. 20에서는 인자를 안 넣어도 되는 기본값, 칸 이름으로 넣는 키워드 인자, 함수 안과 밖의 변수가 어떻게 다른지 배워요.")

# ---------- toc: one row per part, hairlines ----------
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
parts = [("Lightbulb", K1, "왜 필요한가", "복사한 계산, 재료와 결과 상자, 가장 짧은 def", "f-why", "f-min"),
         ("Code", K2, "정의와 호출", "def 줄 다섯 조각, 정의만 하면 안 찍혀요, 실행 순서", "d-shape", "d-flow"),
         ("Key", K3, "매개변수와 인자", "재료 칸 하나, 여러 개, 순서대로 들어가요", "a-one", "a-order"),
         ("PaperPlane", K4, "return", "돌려주기, print와 비교, None, 바로 끝, 값 두 개", "r-ret", "r-multi"),
         ("Warning", K5, "오류와 함정", "괄호 빼기, 인자 수, return 아래 줄, None 계산, NameError", "t-paren", "t-name"),
         ("Star", K6, "실습", "장바구니 총액, 품절 확인, 성적 등급, 할인 결제", "x-total", "x-pay")]
t = [sec("toc"), f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>']
for i, (ic, c, h, s, a, b) in enumerate(parts, 1):
    t.append(f'<div style="position:absolute;left:96px;top:{196 + (i - 1) * 118}px;width:1728px;height:118px;display:flex;flex-direction:row;align-items:center;gap:28px;border-bottom:2px solid {LINE}">'
             + p(f"width:50px;flex:none;font-size:52px;font-weight:900;color:{c}", str(i))
             + f'<x-icon name="{ic}" style="width:44px;height:44px;flex:none;color:{c}"></x-icon>'
             + p(f"width:340px;flex:none;font-size:38px;font-weight:700;color:{INK}", e(h))
             + p(f"flex:1;font-size:30px;color:{SUB}", e(s))
             + p(f"font-size:30px;font-weight:700;color:{c};white-space:nowrap", f"{page[a]}–{page[b]}쪽") + '</div>')
t.append(p(f"position:absolute;left:96px;top:940px;width:1728px;font-size:30px;color:{SUB}", f"{page['ready']}쪽은 노트북 준비, {page['trouble']}–{page['cheatsheet']}쪽은 막힐 때와 한 장 요약이에요."))
TOC_NOTE = "여섯 파트로 나눴어요. 1파트는 함수가 왜 필요한지와 큰 그림, 2파트는 def로 만들고 부르는 법이에요. 3파트는 괄호 안의 재료 칸, 4파트는 return으로 결과를 돌려받는 법이에요. print와 return의 차이를 꼭 짚어요. 5파트는 자주 나는 오류, 6파트는 앞 챕터의 카페 코드를 함수로 바꾸는 실습이에요. 파트마다 새 커널에서 위에서부터 차례로 실행해요."
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(t) + f"\n<aside>{e(TOC_NOTE)}</aside>\n</section>\n")

DECK_TITLE = "함수 1 (정의, 매개변수, return)"
deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-03T03:00:00Z"}, "lists": "css", "title": DECK_TITLE, "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
print(len(ORDER), "slides")
