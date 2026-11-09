"""Generates every slide of the functions 2 deck (20, default values, local and global variables) and slides/deck.json.

Story: keeps writing in basics.ipynb from chapters 12-19. Starts from two pains with chapter 19's functions (typing "M"
every time, a total that vanishes outside the function) and draws default values and the inside/outside boxes. Then
default and keyword arguments, local variables, global variables (same name, UnboundLocalError, global versus return),
lists and dictionaries passed into a function, and three cafe exercises (orders, receipt, points).
Every cell and output comes from tools/demo.sh (tools/run_nb.py runs the cells with the project kernel).

Layout (2026-11-08, Stageshow rules, see tools/DESIGN.md):
- one hero per slide: the notebook cell, drawn large; at most one satellite (a variable box, a list, a scope picture)
- terms are labelled on the code line or the picture with leader tags in one column, never in side cards
- say it once: what the speaker note says is not repeated in cards; one caption line at most
- values that change move or roll in place (fly, stacked values), errors get a pen ring or a struck-through fix
Highlights (2026-11-09, tools/HIGHLIGHT.md, as many kinds as fit): slam and shine on the cover, staggered rows (delay),
line spotlight, code-to-output links, paired colors (mark), code morph for fixes, run band with changing values (text),
path animation, pulse, shake on the failure, blur, zoom, dimmed earlier rows, pen ring/underline/box, spotlight, fly.
No typing effect.
Usage: python3 tools/gen.py slides
"""

import html, json, os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from highlight import (spot, spot_off, cursor, cursor_off, ring, box, underline, lspot, lspot_off, run, run_off, zoom, zoom_off,
                       blur, blur_off, text, pulse, shine, shake, link, SLAM, MARK, DELAY, DIM, WIPE, PATH, MORPH, MORPH_FROM, tok)

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
INK, SUB, LINE, CARD = "#1D2330", "#4A5262", "#E1DED6", "#FFFFFF"
BL, GR, OR, PUR, RED, NAVY, TEAL, GRAY = "#2459C9", "#1F8A4C", "#B26A00", "#5A3BB8", "#A33131", "#1E3F8F", "#0F7C86", "#6A7180"
JP = "#B8560F"          # Jupyter, same as chapters 09 and 10
SEL = "#2F7DE1"         # selected cell bar, like VS Code's focus color
NB = "basics.ipynb"
K1, K1BG = "#1E5FA8", "#E5EEF8"
K2, K2BG = "#A0620A", "#F7EEDD"
K3, K3BG = TEAL, "#E2F2F3"
K4, K4BG = "#A23B72", "#F6E7EF"
K5, K5BG = GR, "#E6F4EC"
K6, K6BG = PUR, "#ECE7F8"
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


def sec(sid, bg="#F6F5F1"):
    return f'<section id="{sid}" data-transition="fade" style="background:{bg};color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">'


def head(eyebrow, title, color):
    return [p(f"position:absolute;left:96px;top:48px;width:1728px;font-size:26px;font-weight:700;color:{color}", e(eyebrow), ' id="eyebrow"'),
            f'<h2 id="title" style="position:absolute;left:96px;top:92px;width:1728px;font-size:56px;font-weight:700;line-height:1.2;color:{INK}">{title}</h2>']


def caption(text, top=944, order=None):
    return p(f"position:absolute;left:96px;top:{top}px;width:1728px;font-size:34px;font-weight:700;line-height:1.4;color:{INK}", text, ' id="caption"' + (at("rise", order) or ' data-build-in="rise"'))


# ---------- notebook cell, drawn at FS px ----------
FS = [30]


def LH():
    return FS[0] * 1.45


def cell(c, left, top, w, sel=True, attrs="", pytag=True):
    """A notebook cell: [n] gutter, white code box, outputs under it. Only the error line of an output is red."""
    fs, lines, n = FS[0], c.get("lines", [""]), c.get("n")
    o = [f'<div id="{c["id"]}"{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;display:flex;flex-direction:column;gap:10px">']
    bar = f'<div style="width:7px;flex:none;border-radius:4px;background:{SEL if sel else "transparent"}"></div>'
    gutter = p(f"width:58px;flex:none;font-family:{MONO};font-size:22px;color:{GRAY};text-align:right;padding-top:12px", f"[{n}]" if n else "[ ]")
    txt = "".join(p(f"font-family:{MONO};font-size:{fs}px;line-height:1.45;white-space:pre;color:{INK}", e(l) if l else "&#160;") for l in lines)
    tg = p(f"position:absolute;right:14px;bottom:8px;font-size:18px;color:{GRAY}", "Python") if pytag else ""
    o.append(f'<div style="display:flex;flex-direction:row;gap:10px;align-items:stretch">{bar}{gutter}'
             f'<div style="flex:1;position:relative;background:#FFFFFF;border:2px solid {LINE};border-radius:10px;padding:8px 18px;display:flex;flex-direction:column">{txt}{tg}</div></div>')
    if c.get("out"):
        col = lambda l: RED if c.get("err") and re.match(r"[A-Za-z]+(Error|Interrupt)", l) else INK
        o.append("".join(p(f"margin-left:85px;padding:0 20px;font-family:{MONO};font-size:{fs}px;line-height:1.45;white-space:pre;color:{col(l)}", e(l) if l else "&#160;") for l in c["out"]))
    o.append('</div>')
    return o


def cx(left, col):
    """x of character column col (code or output) in a cell drawn at left."""
    return left + 105 + col * FS[0] * 0.6


def tw(s):
    """Drawn width of a code string: Hangul about one em, the rest 0.6 em."""
    return sum(FS[0] * (1.0 if '가' <= ch <= '힣' else 0.6) for ch in s)


def ly(top, i):
    """Center y of code line i."""
    return top + 10 + i * LH() + LH() / 2


def oy(top, n, j):
    """Center y of output line j of a cell with n code lines."""
    return top + 20 + n * LH() + 10 + j * (LH() + 10) + LH() / 2


HL = {"run": "rgba(31,138,76,0.16)", "skip": "rgba(106,113,128,0.20)", "err": "rgba(163,49,49,0.14)", "mark": "rgba(36,89,201,0.14)", "note": "rgba(178,106,0,0.16)"}


def hl(left, top, w, i, n=1, kind="mark", order=1, sid=None):
    """Tints code lines i..i+n-1. sid gives the tint an id so a value can fly out of that line."""
    y = top + 10 + i * LH()
    idt = f' id="{sid}"' if sid else ""
    return f'<div{idt}{at("fade", order)} style="position:absolute;left:{left + 87}px;top:{y:.0f}px;width:{w - 89}px;height:{n * LH():.0f}px;background:{HL[kind]};border-radius:6px"></div>'


def tag(x, y, text, color, order=None, size=28, lead=True, anim="fade", code=False):
    """A leader label centred on y: '← text', no box."""
    t = ("← " if lead else "") + (f'<span style="font-family:{MONO}">{e(text)}</span>' if code else e(text))
    return p(f"position:absolute;left:{x:.0f}px;top:{y - size * 0.72:.0f}px;font-size:{size}px;font-weight:700;line-height:1.45;color:{color};white-space:nowrap", t, at(anim, order))


def out_ring(left, top, n, j, text, order, color=RED, k=1):
    """Pen ring around output lines j..j+k-1."""
    y0 = oy(top, n, j) - LH() / 2
    return ring(order, left + 105, y0, tw(text), k * LH() + (k - 1) * 10, color)


def fix(left, top, bad, good, order, size=30):
    """The wrong line struck through, an arrow, the right line."""
    return (f'<div{at("rise", order)} style="position:absolute;left:{left}px;top:{top}px;display:flex;flex-direction:row;align-items:center;gap:22px">'
            + p(f"font-size:{size}px;font-weight:900;color:{RED}", "✕")
            + p(f"font-family:{MONO};font-size:{size}px;font-weight:700;color:{RED};text-decoration:line-through;text-decoration-thickness:3px;white-space:pre", e(bad))
            + arrow(70)
            + p(f"font-size:{size}px;font-weight:900;color:{GR}", "✓")
            + p(f"font-family:{MONO};font-size:{size}px;font-weight:700;color:{INK};background:#E6F4EC;border:3px solid {GR};border-radius:14px;padding:6px 20px;white-space:pre", e(good)) + '</div>')


def arrow(w=60, color="#C9CED8"):
    return f'<x-shape kind="arrow-right" style="width:{w}px;height:30px;flex:none;background:{color}"></x-shape>'


_ar = [0]


def line_svg(pts, color, order=None, dash=False, head=True, width=4, anim="fade", pid=None):
    """A leader or arrow drawn as a polyline in slide coordinates. anim="wipe" uncovers it from the left.
    pid names the line so a dot can travel along it (PATH)."""
    _ar[0] += 1
    mid = f"ar{_ar[0]}"
    d = " ".join(f"{x:.0f},{y:.0f}" for x, y in pts)
    mk = (f'<defs><marker id="{mid}" markerUnits="userSpaceOnUse" markerWidth="22" markerHeight="22" refX="18" refY="11" orient="auto"><path d="M0,0 L22,11 L0,22 z" fill="{color}"/></marker></defs>' if head else "")
    return (f'<svg{at(anim, order) if anim in ("draw", "wipe") else at("fade", order)} viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible">{mk}'
            f'<polyline{f' id="{pid}"' if pid else ""} points="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"{" stroke-dasharray=&quot;12 10&quot;" if dash else ""}{f" marker-end=&quot;url(#{mid})&quot;" if head else ""}/></svg>').replace("&quot;", '"')


def dot(x, y, color, order=None, r=7):
    return f'<div{at("fade", order)} style="position:absolute;left:{x - r:.0f}px;top:{y - r:.0f}px;width:{2 * r}px;height:{2 * r}px;border-radius:50%;background:{color}"></div>'


def bracket(x, y1, y2, color, text, order=None, size=26):
    """A thin vertical bracket beside a group of code lines, with its name."""
    return (f'<div{at("fade", order)} style="position:absolute;left:{x:.0f}px;top:{y1:.0f}px;height:{y2 - y1:.0f}px;display:flex;flex-direction:row;align-items:center;gap:14px">'
            f'<div style="width:12px;height:100%;border:4px solid {color};border-left:none;border-radius:0 10px 10px 0"></div>'
            + p(f"font-size:{size}px;font-weight:700;color:{color};white-space:nowrap", e(text)) + '</div>')


def chip(text, color=K1, bg=K1BG, fs=30, extra="", attrs=""):
    return p(f"font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:1.2;color:{INK};background:{bg};border:3px solid {color};border-radius:999px;padding:6px 22px;white-space:pre;{extra}", e(text), attrs)


def var_box(sid, name, values, left, top, color, w=360, h=220, attrs="", fs=72, orders=None):
    """A variable as a box with its name on top. Several values roll in one slot: each later value covers the last."""
    values = values if isinstance(values, list) else [values]
    orders = orders or [None] * len(values)
    vh = h - 70
    slot = "".join(p(f"position:absolute;left:0;top:0;width:100%;height:{vh}px;background:{CARD};font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:{vh}px;text-align:center;color:{INK}", e(v), (at("rise", o) if k else ""))
                   for k, (v, o) in enumerate(zip(values, orders)))
    return (f'<div id="{sid}"{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:{CARD};border:3px solid {color};border-radius:22px;display:flex;flex-direction:column;overflow:hidden">'
            + p(f"height:64px;flex:none;background:{color};color:#FFFFFF;font-family:{MONO};font-size:32px;font-weight:700;line-height:64px;padding:0 24px;white-space:pre", e(name))
            + f'<div style="position:relative;flex:1;overflow:hidden">{slot}</div></div>')


def slot_row(items, left, top, color, bg, w=170, h=88, fs=28, attrs_each=None, sid=None, attrs=""):
    """A list drawn as a row of boxes."""
    attrs_each = attrs_each or [""] * len(items)
    idt = f' id="{sid}"' if sid else ""
    return (f'<div{idt}{attrs} style="position:absolute;left:{left}px;top:{top}px;display:flex;flex-direction:row;gap:10px">'
            + "".join(p(f"width:{w}px;height:{h}px;border-radius:14px;border:3px solid {color};background:{bg};font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:{h - 6}px;text-align:center;color:{INK};white-space:pre", e(it), a)
                      for it, a in zip(items, attrs_each)) + '</div>')


def rows(left, top, widths, data, order0=None, rh=84, head_=None, fs=28, colors=None, dim=None):
    """A light table: gray header over a dark rule, rows split by hairlines, no boxes."""
    o, y = [], top
    if head_:
        o.append(f'<div style="position:absolute;left:{left}px;top:{y}px;width:{sum(widths) + 24 * (len(widths) - 1)}px;height:46px;display:flex;flex-direction:row;gap:24px;border-bottom:3px solid {INK}">'
                 + "".join(p(f"width:{cw}px;flex:none;font-size:23px;font-weight:700;color:{GRAY}", e(c)) for c, cw in zip(head_, widths)) + '</div>')
        y += 54
    for i, r in enumerate(data):
        cs = ""
        for k, (c, cw) in enumerate(zip(r, widths)):
            code = bool(re.search(r'[=()\[\]".:]|^[a-z_]+$', c)) and not re.search(r'[가-힣]{3,}', c)
            colr = (colors[i] if colors else INK) if k == 0 else (INK if k == 1 else SUB)
            cs += p(f"width:{cw}px;flex:none;font-family:{MONO if code else SANS};font-size:{fs}px;font-weight:{700 if k < 2 else 500};color:{colr};white-space:pre", e(c))
        o.append(f'<div{at("rise", (order0 + i) if order0 else None)}{DIM(dim) if dim else ""} style="position:absolute;left:{left}px;top:{y + i * rh}px;width:{sum(widths) + 24 * (len(widths) - 1)}px;height:{rh}px;display:flex;flex-direction:row;align-items:center;gap:24px;border-bottom:2px solid {LINE}">{cs}</div>')
    return o


def kbd(text, size=26):
    caps = [p(f"font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.2;white-space:nowrap;color:{INK};background:#FFFFFF;border:2px solid #C9CED8;border-bottom-width:5px;border-radius:10px;padding:6px 14px", e(k)) for k in text.split("+")]
    return '<div style="display:flex;flex-direction:row;align-items:center;gap:8px">' + p(f"font-size:22px;font-weight:700;color:{GRAY}", "+").join(caps) + '</div>'


def dl(h, ms):
    """Adds DELAY(ms) to the first tag of an element string (a label that follows its box)."""
    i = h.index(" ")
    return h[:i] + DELAY(ms) + h[i:]


def code_box(left, top, w, n):
    """(x, y, w, h) of the white code box of a cell with n code lines, for lspot."""
    return (left + 85, top, w - 85, 20 + n * LH())


def band(top, i, n=1):
    """(y, h) of code lines i..i+n-1, for lspot."""
    return (top + 10 + i * LH(), n * LH())


def morph_fix(sid, left, top, bad, good, show, order, size=30):
    """A wrong line (red) that turns into the right line (green box) on its step; the shared tokens move into place.
    bad and good are lists of (key, text); the same key is the same piece of code."""
    st = f"position:absolute;left:{left}px;top:{top}px;font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.45;white-space:pre;border-radius:14px;padding:6px 20px;"
    a = "".join(tok(k, e(t)) for k, t in bad)
    b = "".join(tok(k, e(t)) for k, t in good)
    return (p(st + f"color:{RED};background:#FBECEC;border:3px dashed {RED}", a, f' id="{sid}"' + at("fade", show) + MORPH_FROM())
            + p(st + f"color:{INK};background:#E6F4EC;border:3px solid {GR}", b, MORPH(order, sid)))


EB1 = "1. 왜 필요한가"
EB2 = "2. 기본값과 키워드 인자"
EB3 = "3. 지역 변수"
EB4 = "4. 전역 변수"
EB5 = "5. 리스트와 딕셔너리 넘기기"
EB6 = "6. 실습"
TX = 1180     # tag column for full-width cells

# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#F2B27A">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
       f'<h1{SLAM(1)} style="font-size:92px;font-weight:900;line-height:1.1;color:#F6F5F1">함수 2<br>기본값과<br>변수 범위</h1>',
       '<p style="font-size:40px;line-height:1.4;color:#BFC6D4">자주 쓰는 값은 미리 채워 두고<br>함수 안과 밖의 변수 구분하기</p>']
cov.append('<div id="cov-code" style="position:absolute;left:940px;top:250px;width:1100px;height:580px;background:#252B36;border-radius:24px 0 0 24px;padding:56px 60px;display:flex;flex-direction:column;justify-content:center;gap:18px">')
for line, c in [('def order(menu_name, size="M"):', "#9DBDEB"), ('order("latte")', "#8FD8DE"), ('order(size="L", menu_name="tea")', "#8FD8DE"), ("", "#FFFFFF"), ("count = 0", "#E3B877"), ("def visit(count):", "#9DBDEB"), ("    return count + 1", "#F2A0A0")]:
    cov.append(p(f"font-family:{MONO};font-size:34px;font-weight:700;line-height:1.45;color:{c};white-space:pre", e(line) if line else "&#160;"))
cov.append('</div>')
cov.append(shine(2, "cov-code"))
W("cover", cov, "이번 챕터는 함수를 부를 때 빼도 되는 칸과, 변수가 보이는 범위를 배워요. 19에서 def로 함수를 만들고 return으로 값을 돌려받았어요. 먼저 기본값과 키워드 인자를 봐요. 그다음 함수 안에서 만든 변수와 밖에서 만든 변수가 어디까지 보이는지, 바깥 값을 바꾸려면 어떻게 하는지 봐요. 같은 카페 예제를 이어서 써요.", ("intro", "들어가기"))

ORDER.append("toc")

# ---------- ready: the notebook bar is the hero, the cursor points at the kernel ----------
o = [sec("ready")] + head("들어가기", "19에서 쓰던 노트북을 다시 열어요", JP)
o.append(f'<div id="nb-bar" style="position:absolute;left:96px;top:210px;width:1728px;height:76px;background:#ECEAE3;border-radius:14px;display:flex;flex-direction:row;align-items:center;padding:0 24px;gap:22px">'
         + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{INK};white-space:nowrap", NB)
         + "".join(p(f"font-size:22px;color:{SUB};white-space:nowrap", e(t)) for t in ["+ Code", "+ Markdown", "▷ Run All", "↻ Restart", "Variables"]) + '<div style="flex:1"></div>'
         + p(f"font-size:22px;font-weight:700;color:{GR};background:#E6F4EC;border-radius:8px;padding:6px 14px;white-space:nowrap", ".venv (Python 3.14.6)", ' id="kernel"') + '</div>')
steps = [("VS Code로 hello-uv 폴더 열기", None), ("탐색기에서 " + NB + " 열기", None), ("오른쪽 위 커널이 .venv인지 보기", None), ("셀에 적고", "Shift+Enter")]
for i, (s, k) in enumerate(steps):
    y = 360 + i * 100
    o.append(f'<div data-build-in="rise order 1"{DELAY(i * 90)} style="position:absolute;left:96px;top:{y}px;width:860px;height:84px;display:flex;flex-direction:row;align-items:center;gap:22px;border-bottom:2px solid {LINE}">'
             + p(f"width:52px;height:52px;flex:none;border-radius:50%;background:{JP};color:#FFFFFF;font-size:28px;font-weight:900;line-height:52px;text-align:center", str(i + 1))
             + p(f"font-size:30px;font-weight:700;color:{INK};white-space:nowrap", e(s)) + (kbd(k) + p(f"font-size:30px;font-weight:700;color:{INK}", "로 실행") if k else "") + '</div>')
o.append(cursor(2, target="kernel"))
o.append(cursor_off(3))
o.append(p(f"position:absolute;left:1060px;top:360px;font-size:24px;font-weight:700;color:{GRAY}", "이번 챕터에서 다시 쓰는 것"))
done = [("print의 sep, end", "13"), ("copy()", "13"), ("get, stock[name] -= 1", "15"), ("sorted(..., reverse=True)", "16"), ("if, for", "17, 18"), ("def, return, None", "19")]
o += rows(1060, 400, [520, 160], done, None, 74, None, 27)
o.append(caption("기억이 안 나는 줄은 오른쪽 챕터를 먼저 다시 봐요.", 900, 3))
W("ready", o, "12부터 쓰던 basics.ipynb에 이어서 적어요. 09에서 만든 hello-uv 폴더를 VS Code로 열고 노트북을 열어요. 오른쪽 위 커널이 .venv인지 꼭 확인해요. 13의 print sep, end와 copy, 15의 get과 재고 줄이기, 16의 sorted reverse를 다시 만나요. 19의 def와 return은 이번 챕터 내내 써요. 슬라이드의 출력은 tools/demo.sh가 hello-uv 커널에서 같은 셀을 실제로 실행한 결과예요. 셀 번호는 파트마다 [1]부터 다시 셌어요.")

# ---------- part 1 ----------
o = [sec("s-why")] + head(EB1, "19의 함수로 쓰다 보면 두 군데서 막혀요", K1)
FS[0] = 30
W1 = ["def order(menu_name, size):", '    print(f"{menu_name} {size} 사이즈")', "", 'order("latte", "M")', 'order("coffee", "M")', 'order("tea", "M")']
o.append(p(f"position:absolute;left:96px;top:196px;font-size:28px;font-weight:700;color:{K1}", "거의 늘 같은 값을 넣어요"))
o += cell({"id": "c-w1", "lines": W1, "n": 1, "out": ["latte M 사이즈", "coffee M 사이즈", "tea M 사이즈"]}, 96, 244, 860)
for i in (3, 4, 5):
    col = len(W1[i]) - 4
    o.append(underline(1, cx(96, col) - 4, cx(96, col + 3) + 4, ly(244, i) + 22, K1))
o.append(tag(cx(96, 22), ly(244, 4), "M, M, M", K1, 1))
o += cell({"id": "c-w2", "lines": ['order("cake")'], "n": 2, "out": ["TypeError: order() missing 1 required positional argument: 'size'"], "err": True}, 96, 730, 1728, sel=False, attrs=at("rise", 2))
o.append(out_ring(96, 730, 1, 0, "TypeError: order() missing 1 required positional argument: 'size'", 2))
o.append(p(f"position:absolute;left:1000px;top:196px;font-size:28px;font-weight:700;color:{K3}", "함수 안에서 만든 값이 안 보여요", at("fade", 3)))
o += cell({"id": "c-w3", "lines": ["def calc():", "    total = 4500 * 2", "", "calc()", "print(total)"], "n": 3, "out": ["NameError: name 'total' is not defined"], "err": True}, 1000, 244, 824, sel=False, attrs=at("rise", 3))
o.append(out_ring(1000, 244, 5, 0, "NameError: name 'total' is not defined", 4))
o.append(caption("오늘은 기본값과 변수가 보이는 범위를 배워요.", 944, 5))
W("s-why", o, "19의 함수로는 같은 값을 매번 적어야 하고, 함수 안에서 만든 값은 밖에서 안 보여요. 카페 주문은 대부분 M 사이즈인데도 매번 M을 적어야 해요. 빼면 19에서 본 TypeError가 나요. 오른쪽은 다른 문제예요. calc 안에서 total을 만들었는데 밖에서 찍으면 그런 이름이 없다고 해요. 오늘은 이 두 가지를 풀어요. 하나는 기본값이고, 다른 하나는 변수가 보이는 범위예요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p1", "왜 필요한가"))

# ---------- s-big: default slots on the left, the scope picture as the hero on the right ----------
o = [sec("s-big")] + head(EB1, "기본값은 미리 채운 칸, 변수는 안과 밖이 달라요", K1)
o.append(p(f"position:absolute;left:96px;top:226px;font-size:28px;font-weight:700;color:{K2}", "기본값", at("fade", 1)))
o.append(p(f"position:absolute;left:96px;top:290px;font-family:{MONO};font-size:34px;font-weight:700;color:{INK};white-space:pre", e('def order(menu_name, size="M"):'), at("fade", 1)))
o.append(f'<div{at("rise", 1)} style="position:absolute;left:96px;top:380px;width:300px;height:220px;border:3px dashed #B4B9C3;border-radius:20px;display:flex;flex-direction:column;overflow:hidden">'
         + p(f"height:64px;flex:none;background:#ECEAE3;font-family:{MONO};font-size:30px;font-weight:700;line-height:64px;padding:0 22px;color:{INK}", "menu_name")
         + p(f"flex:1;font-size:28px;font-weight:700;color:{GRAY};text-align:center;line-height:150px", "꼭 넣어요") + '</div>')
o.append(var_box("v-size", "size", '"M"', 430, 380, K2, 300, 220, at("rise", 1), 64))
o.append(p(f"position:absolute;left:96px;top:640px;width:700px;font-size:28px;line-height:1.5;color:{SUB}", "부를 때 빼면 \"M\"이 들어가고,<br>넣으면 넣은 값으로 바뀌어요.", at("fade", 1)))
o.append(f'<div style="position:absolute;left:836px;top:226px;width:2px;height:640px;background:{LINE}"></div>')
o.append(f'<div{at("rise", 2)} style="position:absolute;left:896px;top:226px;width:928px;height:640px;background:{K4BG};border:3px solid {K4};border-radius:26px">'
         + p(f"position:absolute;left:32px;top:24px;font-size:28px;font-weight:700;color:{K4}", "밖: 노트북 셀 (전역 변수)")
         + f'<div style="position:absolute;left:32px;top:84px;display:flex;flex-direction:row;gap:16px">' + chip('shop = "KANT 카페"', K4, "#FFFFFF", 28) + chip("count = 0", K4, "#FFFFFF", 28) + '</div>'
         + f'<div style="position:absolute;left:32px;top:220px;width:520px;height:380px;background:{CARD};border:3px solid {K3};border-radius:22px">'
         + p(f"position:absolute;left:28px;top:22px;font-size:28px;font-weight:700;color:{K3}", "안: calc() 몸통 (지역 변수)")
         + f'<div style="position:absolute;left:28px;top:84px;display:flex;flex-direction:column;align-items:flex-start;gap:16px">' + chip("total = 9000", K3, K3BG, 28) + chip("매개변수도 여기", K3, K3BG, 26) + '</div>'
         + p(f"position:absolute;left:28px;top:318px;font-size:24px;color:{SUB}", "함수가 끝나면 이 상자는 사라져요") + '</div></div>')
# read upward: green, solid; look inward: red, dashed and stopped at the border
o.append(line_svg([(1372, 470), (1372, 372)], GR, 3, width=5, anim="wipe"))
o.append(dl(tag(1394, 412, "안에서 밖은 보여요", GR, 3, 28, False), 300))
o.append(line_svg([(1790, 600), (1480, 600)], RED, 4, dash=True, width=5, anim="wipe"))
o.append(dl(p(f"position:absolute;left:1440px;top:572px;font-size:44px;font-weight:900;line-height:1.2;color:{RED}", "✕", at("fade", 4)), 300))
o.append(dl(tag(1500, 660, "밖에서 안은 안 보여요", RED, 4, 28, False), 300))
o.append(caption("함수 안에서는 밖이 보이고, 밖에서는 안이 보이지 않아요.", 944, 5))
W("s-big", o, "오늘 배울 두 가지를 그림 한 장에 담았어요. 왼쪽은 기본값이에요. def 줄에서 size 칸에 \"M\"을 미리 넣어 두면 부를 때 빼도 M이 들어가요. 오른쪽은 변수가 보이는 범위예요. 노트북에서 함수 밖에 만든 변수는 전역 변수, 함수 몸통에서 만든 변수와 매개변수는 지역 변수라고 해요. 함수 안에서는 바깥 변수를 읽을 수 있지만, 바깥에서는 함수 안의 변수를 볼 수 없어요. 함수가 끝나면 안쪽 상자가 통째로 사라지기 때문이에요.")

# ---------- s-min ----------
o = [sec("s-min")] + head(EB1, "def 줄에서 칸 = 값으로 기본값을 정해요", K1)
FS[0] = 40
T = 226
SM = ['def order(menu_name, size="M"):', '    print(f"{menu_name} {size} 사이즈")', "", 'order("latte")', 'order("latte", "L")']
o += cell({"id": "c-m1", "lines": SM, "n": 4, "out": ["latte M 사이즈", "latte L 사이즈"]}, 96, T, 1728)
CB = code_box(96, T, 1728, 5)
for k, i in enumerate((0, 3, 4)):
    o.append(lspot(k + 1, *CB, *band(T, i), bar=K2 if k == 0 else K1))
o.append(lspot_off(4))
o.append(underline(1, cx(96, 21), cx(96, 29), ly(T, 0) + 26, K2))
o.append(tag(TX, ly(T, 0), "기본값", K2, 1, 32))
o.append(tag(TX, ly(T, 3), "size를 뺐어요", K1, 2, 32))
o.append(tag(TX, ly(T, 4), "size에 \"L\"을 넣었어요", K1, 3, 32))
o.append(tag(cx(96, 18), oy(T, 5, 0), "기본값 M", K2, 2, 32))
o.append(tag(cx(96, 18), oy(T, 5, 1), "넣은 값 L", K1, 3, 32))
o.append(p(f"position:absolute;left:96px;top:820px;font-size:30px;font-weight:700;color:{SUB}", '괄호 안의 =는 앞뒤를 띄우지 않고 <span style="font-family:' + MONO + ';color:' + INK + '">size="M"</span>처럼 붙여 써요.', at("fade", 4)))
FS[0] = 30
W("s-min", o, "def 줄의 칸 뒤에 = 값을 적으면 그 칸의 기본값이 돼요. order(\"latte\")처럼 size를 빼고 부르면 size에 \"M\"이 들어가요. order(\"latte\", \"L\")처럼 넣으면 넣은 \"L\"이 들어가요. 기본값이 없는 menu_name은 19처럼 꼭 넣어야 해요. 괄호 안의 =는 앞뒤를 띄우지 않고 붙여 쓰는 게 관례예요." + REAL)

# ---------- part 2 ----------
o = [sec("k-default")] + head(EB2, "기본값이 여러 개면 앞에서부터 채워요", K2)
T = 210
KD = ['def order(menu_name, size="M", qty=1):', '    print(f"{menu_name} {size} {qty}잔")', "", 'order("latte")', 'order("latte", "L")', 'order("latte", "L", 2)', 'order("latte", qty=3)']
o += cell({"id": "c-k1", "lines": KD, "n": 1, "out": ["latte M 1잔", "latte L 1잔", "latte L 2잔", "latte M 3잔"]}, 96, T, 1728)
o.append(dl(tag(TX, ly(T, 3), "둘 다 기본값", GRAY, 1), 0).replace(DELAY(0), DIM("kd")))
o.append(dl(tag(TX, ly(T, 4), "\"L\"은 둘째 칸 size로", K2, 2), 0).replace(DELAY(0), DIM("kd")))
o.append(dl(tag(TX, ly(T, 5), "2는 셋째 칸 qty로", K2, 3), 0).replace(DELAY(0), DIM("kd")))
o.append(underline(4, cx(96, 15), cx(96, 20), ly(T, 6) + 20, OR))
o.append(dl(tag(TX, ly(T, 6), "칸 이름을 붙이면 qty만 바꿔요", OR, 4), 0).replace(DELAY(0), DIM("kd")))
o.append(tag(cx(96, 14), oy(T, 7, 3), "size는 기본값 그대로", OR, 4))
o.append(caption("넣은 값은 앞 칸부터 채우고, 넣지 않은 칸만 기본값을 써요.", 944, 5))
W("k-default", o, "기본값 칸이 여러 개면 넣은 값은 앞 칸부터 채우고, 넣지 않은 칸만 기본값을 써요. order(\"latte\", \"L\", 2)는 size에 L, qty에 2가 들어가요. 그런데 잔 수만 3으로 바꾸고 싶을 땐 어떻게 할까요? 순서대로라면 size도 적어야 해요. 마지막 줄처럼 qty=3으로 칸 이름을 붙여 넣으면 size는 기본값 M으로 두고 qty만 바꿀 수 있어요. 이렇게 이름을 붙여 넣는 인자를 키워드 인자라고 해요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p2", "기본값과 키워드 인자"))

o = [sec("k-keyword")] + head(EB2, "칸 이름을 붙이면 순서를 바꿔도 돼요", K2)
T = 210
o += cell({"id": "c-k2", "lines": ['order(size="L", menu_name="tea")', 'order("tea", qty=2, size="S")'], "n": 2, "out": ["tea L 1잔", "tea S 2잔"]}, 96, T, 1728)
o.append(tag(TX, ly(T, 1), "이름 없는 값은 앞에, 이름 붙인 값은 뒤에", K2, 4))
big = ('order(<span' + MARK(1) + ' style="color:' + BL + '">size=</span><span id="kw-l">"L"</span>, '
       '<span' + MARK(2) + ' style="color:' + OR + '">menu_name=</span><span id="kw-tea">"tea"</span>)')
o.append(p(f"position:absolute;left:96px;top:520px;font-family:{MONO};font-size:44px;font-weight:700;color:{INK};white-space:pre", big))
o.append(var_box("v-k1", "menu_name", ['', '"tea"'], 96, 640, OR, 440, 220, "", 64, [None, 2]).replace('data-build-in="rise order 2"', 'data-build-in="fly order 2" data-from="kw-tea"'))
o.append(var_box("v-k2", "size", ['', '"L"'], 576, 640, BL, 300, 220, "", 64, [None, 1]).replace('data-build-in="rise order 1"', 'data-build-in="fly order 1" data-from="kw-l"'))
o.append(var_box("v-k3", "qty", ["1"], 916, 640, GRAY, 220, 220, "", 64))
o.append(tag(1180, 750, "넣지 않아서 기본값", GRAY, 3, 28))
o.append(tag(cx(96, 9), oy(T, 2, 0), "칸 이름을 보고 제자리에 들어가요", K2, 2))
W("k-keyword", o, "키워드 인자는 칸 이름을 보고 들어가서, 적는 순서를 바꿔도 돼요. size=\"L\"을 먼저 적어도 size 칸에, menu_name=\"tea\"는 menu_name 칸에 들어가요. qty는 넣지 않았으니 기본값 1이에요. 19에서 order(2, \"latte\")로 순서가 바뀌어 이상하게 찍혔던 문제를 이렇게 피할 수 있어요. 적은 순서대로 들어가는 인자는 위치 인자, 이름을 붙인 인자는 키워드 인자라고 해요. 둘을 같이 쓸 때는 위치 인자를 앞에 적어요." + REAL)

o = [sec("k-rule")] + head(EB2, "기본값과 키워드 인자는 뒤에 적어요", K2)
T1, T2 = 210, 580
FS[0] = 34
o.append(p(f"position:absolute;left:96px;top:{T1 - 4}px;font-size:26px;font-weight:700;color:{K2}", "만들 때"))
o += cell({"id": "c-k3", "lines": ['def order(size="M", menu_name):', "    print(menu_name, size)"], "n": 3, "out": ["SyntaxError: parameter without a default follows parameter with a default"], "err": True}, 96, T1 + 40, 1728)
o.append(morph_fix("kr-a", 201, T1 + 300, [("d", "def order("), ("s", 'size="M"'), ("c", ", "), ("m", "menu_name"), ("e", "):")],
                   [("d", "def order("), ("m", "menu_name"), ("c", ", "), ("s", 'size="M"'), ("e", "):")], None, 1, 34))
o.append(tag(1080, T1 + 330, "기본값 칸을 뒤로", GR, 1, 28))
o.append(p(f"position:absolute;left:96px;top:{T2 - 4}px;font-size:26px;font-weight:700;color:{K2}", "부를 때", at("fade", 2)))
o += cell({"id": "c-k4", "lines": ['order(size="L", "tea")'], "n": 4, "out": ["SyntaxError: positional argument follows keyword argument"], "err": True}, 96, T2 + 40, 1728, sel=False, attrs=at("rise", 2))
o.append(morph_fix("kr-b", 201, T2 + 230, [("o", "order("), ("s", 'size="L"'), ("c", ", "), ("t", '"tea"'), ("e", ")")],
                   [("o", "order("), ("t", '"tea"'), ("c", ", "), ("s", 'size="L"'), ("e", ")")], 2, 3, 34))
o.append(tag(830, T2 + 260, "이름 없는 값을 앞으로", GR, 3, 28))
o.append(caption("두 오류 모두 실행하기 전에 SyntaxError로 알려 줘요.", 944, 4))
FS[0] = 30
W("k-rule", o, "기본값 칸은 def 줄 뒤쪽에, 키워드 인자는 부를 때 뒤쪽에 적어요. 함수를 만들 때 기본값이 있는 칸을 앞에 두면 SyntaxError가 나요. 기본값 없는 칸을 앞에, 기본값 있는 칸을 뒤에 둬요. 부를 때는 키워드 인자 뒤에 이름 없는 값을 적으면 SyntaxError가 나요. 이름 없는 값을 먼저 적어요. 두 오류는 실행하기 전에 문법 검사에서 걸려요. 실제 메시지 끝에는 셀마다 다른 파일 이름과 줄 번호가 괄호로 붙는데, 그 부분은 빼고 옮겼어요." + REAL)

o = [sec("k-known")] + head(EB2, "키워드 인자는 이미 써 봤어요", K2)
FS[0] = 36
T = 220
KK = ['print("coffee", "latte", sep=" / ")', 'print("coffee", end=" ")', 'print("latte")', "print(sorted([5000, 4500, 6500], reverse=True))"]
o += cell({"id": "c-k5", "lines": KK, "n": 5, "out": ["coffee / latte", "coffee latte", "[6500, 5000, 4500]"]}, 96, T, 1728)
for i, (a_, b_, txt, order) in enumerate([(24, 33, "13 · 기본값은 빈칸 하나", 1), (16, 23, "13 · 기본값은 줄바꿈", 2), (34, 46, "16 · 기본값은 False", 3)]):
    li = (0, 1, 3)[i]
    o.append(hl(96, T, 1728, li, 1, "note", order))
    o.append(tag(1250, ly(T, li), txt, K2, order))
o.append(p(f"position:absolute;left:96px;top:820px;font-size:30px;font-weight:700;color:{SUB}", '<span style="font-family:' + MONO + ';color:' + INK + '">print()</span>만 쳐도 빈 줄이 찍히는 것도 end의 기본값이 줄바꿈이라서예요.', at("fade", 4)))
FS[0] = 30
W("k-known", o, "print의 sep, end와 sorted의 reverse가 이미 써 본 키워드 인자예요. 13에서 print의 sep과 end를, 16에서 sorted의 reverse=True를 썼어요. 셋 다 기본값이 있는 칸이라 평소에는 빼고 썼어요. sep의 기본값은 빈칸 하나라서 값 사이가 한 칸씩 띄워졌고, end의 기본값은 줄바꿈이라서 print마다 줄이 바뀌었어요. 18의 구구단에서 print()로 줄을 바꾼 것도 이 기본값 덕분이에요." + REAL)

# ---------- part 3 ----------
o = [sec("l-local")] + head(EB3, "함수 안에서 만든 변수는 밖에서 안 보여요", K3)
FS[0] = 32
T = 220
o += cell({"id": "c-l1", "lines": ["def calc():", "    total = 4500 * 2", '    print("안:", total)', "", "calc()", 'print("밖:", total)'], "n": 1, "out": ["안: 9000", "", "NameError: name 'total' is not defined"], "err": True}, 96, T, 1040)
o.append(tag(cx(96, 22), ly(T, 1), "지역 변수", K3, 1))
o.append(f'<div{at("rise", 1)} style="position:absolute;left:1220px;top:{T}px;width:604px;height:210px;background:{CARD};border:3px solid {K3};border-radius:22px;padding:24px 30px;display:flex;flex-direction:column;gap:22px">'
         + p(f"font-size:28px;font-weight:700;color:{K3}", "calc()를 부르는 동안") + chip("total = 9000", K3, K3BG, 32, "align-self:flex-start") + '</div>')
o.append(f'<div{at("rise", 2)} style="position:absolute;left:1220px;top:{T + 250}px;width:604px;height:210px;background:#F1F0EC;border:3px dashed #B4B9C3;border-radius:22px;padding:24px 30px;display:flex;flex-direction:column;gap:22px">'
         + p(f"font-size:28px;font-weight:700;color:{GRAY}", "calc()가 끝난 뒤")
         + p(f"font-family:{MONO};font-size:32px;font-weight:700;line-height:1.2;color:#B4B9C3;text-decoration:line-through;padding:6px 22px;border:3px dashed #C9CED8;border-radius:999px;align-self:flex-start", "total = 9000") + '</div>')
o.append(tag(1240, T + 500, "끝나면 상자째 사라져요", GRAY, 2, 28, False))
o.append(out_ring(96, T, 6, 2, "NameError: name 'total' is not defined", 3))
o.append(caption("함수 안의 값을 밖에서 쓰려면 19처럼 return으로 돌려받아요.", 944, 4))
FS[0] = 30
W("l-local", o, "함수 안에서 만든 변수는 함수가 끝나면 사라져서 밖에서 쓸 수 없어요. calc 안에서 total을 만들고 찍으면 9000이 잘 찍혀요. 그런데 밖에서 total을 찍으면 그런 이름이 없다는 NameError가 나요. 함수 안에서 만든 변수는 함수를 부르는 동안만 있다가, 함수가 끝나면 상자째 사라지기 때문이에요. 이런 변수를 지역 변수라고 해요. 함수 안의 값을 밖에서 쓰려면 19에서 배운 대로 return으로 돌려받아요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p3", "지역 변수"))

o = [sec("l-param")] + head(EB3, "매개변수도 함수 안에서만 쓰는 변수예요", K3)
FS[0] = 32
T = 220
o += cell({"id": "c-l2", "lines": ["def greet(name):", '    print(f"{name}님, 어서 오세요")', "", 'greet("kim")', "print(name)"], "n": 2, "out": ["kim님, 어서 오세요", "", "NameError: name 'name' is not defined"], "err": True}, 96, T, 1040)
o.append(hl(96, T, 1040, 3, 1, "mark", 1, "src-kim"))
o.append(f'<div style="position:absolute;left:1220px;top:{T}px;width:604px;height:210px;background:{CARD};border:3px solid {K3};border-radius:22px;padding:24px 30px;display:flex;flex-direction:column;gap:22px">'
         + p(f"font-size:28px;font-weight:700;color:{K3}", 'greet("kim")을 부르는 동안')
         + chip('name = "kim"', K3, K3BG, 32, "align-self:flex-start", ' data-build-in="fly order 1" data-from="src-kim"') + '</div>')
o.append(tag(1240, T + 250, "부를 때 넣은 값이 담긴 칸", K3, 1, 28, False))
o.append(out_ring(96, T, 5, 2, "NameError: name 'name' is not defined", 2))
o.append(caption("그래서 19의 calc_total(cart, menu)에서 menu 칸은 바깥 menu와 이름만 같아요.", 944, 3))
FS[0] = 30
W("l-param", o, "매개변수도 지역 변수라서 함수가 끝나면 사라져요. greet(\"kim\")을 부르는 동안 name에 kim이 담겨 있다가 함수가 끝나면 사라져요. 그래서 밖에서 name을 찍으면 NameError가 나요. 덕분에 매개변수 이름은 바깥 변수와 겹쳐도 서로 섞이지 않아요. 19의 calc_total(cart, menu)에서 menu 칸은 바깥의 menu 딕셔너리와 이름만 같은 다른 칸이었어요. 밖에서 쓰려면 인자로 넣거나 return한 값을 받아요." + REAL)

o = [sec("l-life")] + head(EB3, "부를 때마다 처음부터 새로 만들어요", K3)
FS[0] = 34
T = 220
o += cell({"id": "c-l3", "lines": ["def add_stamp():", "    stamp = 0", "    stamp += 1", '    print("도장", stamp)', "", "add_stamp()", "add_stamp()", "add_stamp()"], "n": 3, "out": ["도장 1", "도장 1", "도장 1"]}, 96, T, 900)
for k in range(3):
    o.append(run(k + 1, 96 + 89, T + 10 + (5 + k) * LH(), 900 - 93, LH()))
o.append(run_off(4))
for i in range(3):
    x = 1080 + i * 256
    o.append(f'<div{at("rise", i + 1)} style="position:absolute;left:{x}px;top:{T}px;width:232px;height:330px;border-top:6px solid {K3};padding-top:22px;display:flex;flex-direction:column;align-items:center;gap:18px">'
             + p(f"font-size:26px;font-weight:700;color:{K3}", ["첫째", "둘째", "셋째"][i] + " 부르기")
             + p(f"font-family:{MONO};font-size:28px;color:{GRAY}", "stamp = 0") + p(f"font-family:{MONO};font-size:28px;color:{GRAY}", "stamp += 1")
             + p(f"width:96px;height:96px;border-radius:50%;background:{K3BG};border:3px solid {K3};font-family:{MONO};font-size:44px;font-weight:700;line-height:90px;text-align:center;color:{INK}", "1") + '</div>')
o.append(ring(4, cx(96, 0) - 6, oy(T, 8, 0) - LH() / 2, tw("도장 1") + 12, 3 * LH() + 20, RED))
o.append(tag(cx(96, 9), oy(T, 8, 1), "쌓이지 않아요", RED, 4))
o.append(caption("값을 쌓으려면 함수 밖에 변수를 둬야 해요. 다음 파트에서 봐요.", 944, 5))
FS[0] = 30
W("l-life", o, "지역 변수는 부를 때마다 새로 생기고, 끝나면 사라져서 지난번 값을 기억하지 못해요. 손님이 올 때마다 도장을 하나씩 찍으려고 add_stamp를 만들었어요. 세 번 불렀는데 도장이 1, 1, 1이에요. 부를 때마다 새 상자에서 stamp = 0부터 시작하고, 끝나면 상자째 사라지기 때문이에요. 값을 쌓으려면 함수 밖에 변수를 둬야 해요. 다음 파트에서 바깥 변수를 읽고 바꾸는 법을 봐요." + REAL)

# ---------- part 4 ----------
o = [sec("g-read")] + head(EB4, "함수 밖에서 만든 변수는 안에서 읽을 수 있어요", K4)
FS[0] = 40
T = 290
GRD = ['shop = "KANT 카페"', "", "def hello():", '    print(f"{shop}에 어서 오세요")', "", "hello()"]
o += cell({"id": "c-g1", "lines": GRD, "n": 1, "out": ["KANT 카페에 어서 오세요"]}, 96, T, 1728)
o.append(bracket(1240, ly(T, 0) - 26, ly(T, 0) + 26, K4, "밖 (전역 변수)", 1, 30))
o.append(bracket(1240, ly(T, 2) - 26, ly(T, 3) + 26, K3, "hello() 안", 1, 30))
sx = cx(96, 13) + tw("shop") / 2
o.append(line_svg([(sx, ly(T, 3) - 24), (sx, ly(T, 1)), (cx(96, 2), ly(T, 1)), (cx(96, 2), ly(T, 0) + 26)], K4, 2, width=4, pid="rd-path"))
o.append(f'<div{PATH(2, "rd-path")} style="position:absolute;left:{cx(96, 2) - 11:.0f}px;top:{ly(T, 0) + 26 - 11:.0f}px;width:22px;height:22px;border-radius:50%;background:{K4};box-shadow:0 0 0 6px rgba(162,59,114,0.25)"></div>')
o.append(tag(sx + 24, ly(T, 1), "안에 없으면 밖에서 찾아요", K4, 2, 28, False))
o.append(caption("가게 이름처럼 바뀌지 않는 값은 밖에 두고 안에서 읽어도 괜찮아요.", 944, 3))
FS[0] = 30
W("g-read", o, "함수 안에서 이름을 찾을 땐 먼저 안을 보고, 없으면 밖을 봐요. shop은 함수 밖에서 만들었어요. 이런 변수를 전역 변수라고 해요. hello 안에는 shop이 없지만 찍어 보면 KANT 카페가 잘 나와요. 그래서 함수 안에서 전역 변수를 읽을 수 있어요. 가게 이름처럼 바뀌지 않는 값은 전역 변수로 두고 읽기만 해도 괜찮아요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p4", "전역 변수"))

o = [sec("g-same")] + head(EB4, "안에서 같은 이름에 넣으면 새 지역 변수가 생겨요", K4)
FS[0] = 32
T = 220
o += cell({"id": "c-g2", "lines": ["price = 4500", "", "def set_price():", "    price = 5000", '    print("안:", price)', "", "set_price()", 'print("밖:", price)'], "n": 2, "out": ["안: 5000", "밖: 4500"]}, 96, T, 1000)
o.append(hl(96, T, 1000, 3, 1, "mark", 1))
o.append(tag(cx(96, 17), ly(T, 3), "새 지역 변수", K3, 1))
o.append(var_box("v-out", "밖 price", "4500", 1180, T, K4, 300, 220))
o.append(var_box("v-in", "안 price", "5000", 1524, T, K3, 300, 220, at("rise", 1)))
o.append(tag(1180, T + 280, "이름만 같은 다른 상자예요", INK, 2, 28, False))
o.append(tag(cx(96, 10), oy(T, 8, 0), "안쪽 상자", K3, 2))
o.append(tag(cx(96, 10), oy(T, 8, 1), "바깥 상자는 그대로", K4, 2))
o.append(pulse(2, "v-out"))
o.append(caption("함수 안에서 = 로 값을 넣으면 그 이름은 지역 변수가 돼요.", 944, 3))
FS[0] = 30
W("g-same", o, "함수 안에서 = 로 값을 넣으면 바깥 변수가 아니라 같은 이름의 지역 변수가 새로 생겨요. 바깥에 price 4500이 있어요. set_price 안에서 price = 5000을 넣고 찍으면 5000이 나와요. 그런데 밖에서 다시 찍으면 4500 그대로예요. 이름만 같고 서로 다른 상자 두 개예요. 바깥 값을 바꾸고 싶었다면 이 방법으로는 안 돼요. 바꾸는 방법은 두 장 뒤에 봐요." + REAL)

o = [sec("g-unbound")] + head(EB4, "읽다가 바꾸면 UnboundLocalError가 나요", K4)
FS[0] = 40
T = 220
GU = ["count = 0", "", "def visit():", "    count = count + 1", "", "visit()"]
o += cell({"id": "c-g3", "lines": GU, "n": 3}, 96, T, 1728)
y3 = ly(T, 3)
x1 = cx(96, 4) + tw("count") / 2
x2 = cx(96, 12) + tw("count + 1") / 2
o.append(underline(1, cx(96, 4), cx(96, 11), y3 + 26, K4))
o.append(tag(cx(96, 4), ly(T, 4) + 8, "① = 로 넣으니 지역 변수예요", K4, 1, 28, False))
o.append(underline(2, cx(96, 12), cx(96, 21), y3 + 26, OR))
o.append(line_svg([(cx(96, 21) + 16, y3), (1180, y3)], OR, 2, head=False, width=3))
o.append(dot(1180, y3, OR, 2, 6))
o.append(tag(1200, y3, "② 오른쪽 count부터 읽어요", OR, 2, 28, False))
EY = T + 20 + 6 * LH() + 12
ERR = "UnboundLocalError: cannot access local variable 'count' where it is not associated with a value"
o.append(p(f"position:absolute;left:201px;top:{EY:.0f}px;font-family:{MONO};font-size:26px;line-height:1.45;color:{RED};white-space:pre", e(ERR), ' id="ub-err"'))
o.append(shake(3, "ub-err"))
o.append(ring(3, 201, EY + 2, 26 * 0.6 * 17, 34, RED))
o.append(tag(201, EY + 110, "③ 지역 count에는 아직 값이 없어요", RED, 3, 28, False))
o.append(caption("앞 장 규칙 그대로예요. 안에서 = 로 넣는 이름은 처음부터 지역 변수예요.", 944, 4))
FS[0] = 30
W("g-unbound", o, "함수 안에 count = 이 있으면 count는 처음부터 지역 변수라서, 바깥 count를 읽지 못해요. 방문자 수를 세려고 함수 안에서 count = count + 1을 했는데 UnboundLocalError가 나요. 파이썬은 실행하기 전에 함수 몸통을 훑어서 = 로 값을 넣는 이름을 지역 변수로 정해요. 그래서 count는 지역 변수가 됐어요. 오른쪽 count + 1을 계산하려고 지역 count를 읽는데, 아직 아무 값도 없어요. 메시지가 그 뜻이에요. 앞 장의 규칙이 그대로 적용된 거예요." + REAL)

o = [sec("g-global")] + head(EB4, "global을 적으면 바깥 변수를 바꿔요", K4)
FS[0] = 34
T = 210
GG = ["count = 0", "", "def visit():", "    global count", "    count = count + 1", "", "visit()", "visit()", "visit()", "print(count)"]
o += cell({"id": "c-g4", "lines": GG, "n": 4, "out": ["3"]}, 96, T, 1000)
o.append(hl(96, T, 1000, 3, 1, "mark", 1))
o.append(tag(cx(96, 17), ly(T, 3), "바깥 count를 쓴다는 뜻", K4, 1))
for k in range(3):
    o.append(tag(cx(96, 9), ly(T, 6 + k), f"count {k + 1}", K4, 2 + k, 28))
o.append(var_box("v-cnt", "밖 count", ["3"], 1180, T, K4, 644, 380, "", 140).replace("<p style", '<p id="cnt-v" data-start="0" style', 2).replace('<p id="cnt-v" data-start="0" style', "<p style", 1))
for k in range(3):
    o.append(run(2 + k, 96 + 89, T + 10 + (6 + k) * LH(), 1000 - 93, LH()))
    o.append(text(2 + k, "cnt-v", str(k + 1)))
o.append(run_off(5))
o.append(caption("global은 있다는 것만 알아 둬요. 다음 장에서 더 나은 방법을 봐요.", 944, 5))
FS[0] = 30
W("g-global", o, "함수 첫 줄에 global count를 적으면 그 함수 안의 count는 바깥 count라는 뜻이 돼요. 그래서 세 번 부르면 바깥 count가 3이 돼요. 이런 방법이 있다는 것만 알아 두면 돼요. 함수가 여러 개인데 모두 바깥 값을 바꾸면, 값이 이상해졌을 때 어느 함수가 바꿨는지 찾기 어려워요. 다음 장에서 return으로 푸는 방법과 비교해요." + REAL)

o = [sec("g-return")] + head(EB4, "바깥 값을 바꿀 땐 return으로 돌려받아요", K4)
FS[0] = 32
T = 250
GRP = '<div id="{}" style="position:absolute;left:0;top:0;width:0;height:0">'
o.append(GRP.format("gr-left"))
o.append(p(f"position:absolute;left:96px;top:200px;font-size:28px;font-weight:700;color:{GRAY};white-space:nowrap", "global로 바꾸기"))
o += cell({"id": "c-g4b", "lines": GG, "n": 4, "out": ["3"]}, 96, T, 846, sel=False)
o.append(hl(96, T, 846, 6, 3, "skip", 1))
o.append(tag(cx(96, 9), ly(T, 7), "count가 바뀌는지 안 보여요", GRAY, 1, 26))
o.append('</div>')
o.append(GRP.format("gr-right"))
o.append(p(f"position:absolute;left:978px;top:200px;font-size:28px;font-weight:700;color:{K4};white-space:nowrap", "return으로 돌려받기"))
GR5 = ["def visit(count):", "    return count + 1", "", "count = 0", "count = visit(count)", "count = visit(count)", "count = visit(count)", "print(count)"]
o += cell({"id": "c-g5", "lines": GR5, "n": 5, "out": ["3"]}, 978, T, 846)
o.append(box(2, 978 + 92, T + 10 + 4 * LH() - 4, 846 - 100, 3 * LH() + 8, K4, 5, 10))
o.append(tag(cx(978, 21) + 10, ly(T, 5), "바뀌는 줄이 보여요", K4, 2, 26))
o.append('</div>')
o.append(blur(1, "c-g4b"))
o.append(blur(2, "c-g5"))
o.append(blur_off(3))
o.append(caption("함수는 받은 값으로 계산해서 돌려주기만 해요. 이쪽을 권해요.", 944, 3))
FS[0] = 30
W("g-return", o, "바깥 값을 바꿔야 하면 global보다 인자로 넣고 return으로 돌려받는 쪽을 권해요. 같은 방문자 세기를 두 가지로 썼어요. 왼쪽은 global로 함수 안에서 바깥 count를 직접 바꿔요. visit()만 보면 count가 바뀌는지 알 수 없어요. 오른쪽은 count를 인자로 넣고, 1 더한 값을 돌려받아 다시 count에 담아요. count가 바뀌는 줄이 밖에 그대로 보여요. 함수는 받은 값으로 계산해서 돌려주기만 하니까 따로 떼어 확인하기도 쉬워요." + REAL)

# ---------- part 5 ----------
o = [sec("m-list")] + head(EB5, "리스트를 넘기고 안에서 append하면 원본이 바뀌어요", K5)
FS[0] = 32
T = 220
ML = ["def add_item(cart, name):", "    cart.append(name)", "", 'my_cart = ["coffee"]', 'add_item(my_cart, "cake")', 'add_item(my_cart, "latte")', "print(my_cart)"]
o += cell({"id": "c-n1", "lines": ML, "n": 1, "out": ["['coffee', 'cake', 'latte']"]}, 96, T, 1000)
o.append(hl(96, T, 1000, 4, 1, "mark", 2, "ml-4"))
o.append(hl(96, T, 1000, 5, 1, "mark", 3, "ml-5"))
o.append(chip("my_cart", K4, K4BG, 32, "position:absolute;left:1180px;top:250px"))
o.append(chip("cart", K3, K3BG, 32, "position:absolute;left:1180px;top:520px", at("rise", 1)))
o.append(slot_row(["coffee", "cake", "latte"], 1430, 380, K5, K5BG, 128, 96, 26, ["", ' data-build-in="fly order 2" data-from="ml-4"', ' data-build-in="fly order 3" data-from="ml-5"']))
o.append(line_svg([(1360, 282), (1470, 370)], K4, None, anim="fade"))
o.append(line_svg([(1300, 548), (1470, 486)], K3, 1))
o.append(tag(1180, 680, "이름 두 개, 리스트 하나", INK, 1, 30, False))
o.append(tag(cx(96, 28), oy(T, 7, 0), "return 없이도 바뀌었어요", K5, 4))
o.append(caption("my_cart와 cart는 리스트 하나를 같이 가리켜요.", 944, 5))
FS[0] = 30
W("m-list", o, "리스트를 함수에 넘기면 복사본이 아니라 같은 리스트가 들어가서, 안에서 고치면 원본이 바뀌어요. 장바구니 리스트를 함수에 넘기고 안에서 append했어요. return이 없는데도 밖에서 my_cart를 찍으면 cake과 latte가 들어 있어요. my_cart와 cart는 이름만 둘이고 리스트는 하나예요. 그래서 cart로 고치면 my_cart로 봐도 바뀌어 있어요. 원본을 지키는 방법은 22쪽에서 봐요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p5", "리스트와 딕셔너리 넘기기"))

o = [sec("m-int")] + head(EB5, "숫자는 안에서 바꿔도 밖이 그대로예요", K5)
FS[0] = 30
T = 210
o += cell({"id": "c-n2", "lines": ["def add_one(n):", "    n += 1", '    print("안:", n)', "", "x = 1", "add_one(x)", 'print("밖:", x)'], "n": 2, "out": ["안: 2", "밖: 1"]}, 96, T, 1000)
o.append(var_box("v-x", "밖 x", "1", 1180, T, K4, 300, 220))
o.append(var_box("v-n", "안 n", ["1", "2"], 1524, T, K3, 300, 220, "", 72, [None, 1]))
o.append(tag(cx(96, 12), ly(T, 1), "n에 새 값 2를 넣어요", K3, 1))
o += rows(96, 690, [440, 600, 580], [("n += 1", "새 값을 넣어요", "밖은 그대로"), ("cart.append(...)", "받은 리스트를 고쳐요", "밖도 바뀌어요"), ("stock[name] -= 1", "받은 딕셔너리 칸을 고쳐요", "밖도 바뀌어요")], 2, 80, None, 30, [K3, K5, K5], "mi")
W("m-int", o, "숫자를 넘기고 안에서 = 로 새 값을 넣으면 밖의 변수는 그대로예요. 안에서 n += 1을 하면 n은 2가 되지만 밖의 x는 1 그대로예요. n += 1은 n이라는 이름에 새 값 2를 넣는 일이라서 x와는 상관이 없어요. 앞 장의 append는 받은 리스트 자체를 고쳐서 밖에서도 바뀌었어요. 리스트나 딕셔너리를 메서드나 [키]로 고치면 밖도 바뀌어요." + REAL)

o = [sec("m-dict")] + head(EB5, "딕셔너리를 넘기면 재고를 바로 줄일 수 있어요", K5)
FS[0] = 36
T = 220
o += cell({"id": "c-n3", "lines": ["def sell(stock, name):", "    stock[name] -= 1", "", 'stock = {"coffee": 3, "latte": 1}', 'sell(stock, "latte")', 'sell(stock, "coffee")', "print(stock)"], "n": 3, "out": ["{'coffee': 2, 'latte': 0}"]}, 96, T, 1100)
o.append(tag(cx(96, 22), ly(T, 1), "칸만 고쳐요", K5, 1, 28))
o.append(p(f"position:absolute;left:1240px;top:{T}px;font-family:{MONO};font-size:30px;font-weight:700;color:{K5}", "stock"))
o.append(var_box("v-cof", "coffee", ["2"], 1240, T + 56, K5, 270, 300, "", 96).replace("<p style", '<p id="cof-v" data-start="3" style', 2).replace('<p id="cof-v" data-start="3" style', "<p style", 1))
o.append(var_box("v-lat", "latte", ["0"], 1554, T + 56, K5, 270, 300, "", 96).replace("<p style", '<p id="lat-v" data-start="1" style', 2).replace('<p id="lat-v" data-start="1" style', "<p style", 1))
o.append(text(2, "lat-v", "0"))
o.append(text(3, "cof-v", "2"))
o.append(tag(cx(96, 21), ly(T, 4), "latte 1 → 0", K5, 2, 28))
o.append(tag(cx(96, 22), ly(T, 5), "coffee 3 → 2", K5, 3, 28))
o.append(caption("받은 딕셔너리의 칸만 고쳤으니 global이 필요 없어요.", 944, 4))
FS[0] = 30
W("m-dict", o, "받은 딕셔너리의 칸을 고치면 global 없이도 원본 딕셔너리가 바뀌어요. 18에서 재고를 줄일 때 쓴 stock[o] -= 1을 함수로 만들었어요. 재고 딕셔너리와 메뉴 이름을 받아서 그 칸을 1 줄여요. 두 번 부른 뒤 밖에서 찍으면 latte는 0, coffee는 2로 바뀌어 있어요. 4파트의 count와 달리 global이 필요 없어요. stock에 새 딕셔너리를 넣은 게 아니라 받은 딕셔너리의 칸만 고쳤기 때문이에요." + REAL)

o = [sec("m-copy")] + head(EB5, "원본을 지키려면 copy()로 새로 만들어 돌려줘요", K5)
FS[0] = 34
T = 210
o += cell({"id": "c-n4", "lines": ["def with_item(cart, name):", "    new_cart = cart.copy()", "    new_cart.append(name)", "    return new_cart", "", 'my_cart = ["coffee"]', 'big_cart = with_item(my_cart, "cake")', "print(my_cart)", "print(big_cart)"], "n": 4, "out": ["['coffee']", "['coffee', 'cake']"]}, 96, T, 1100)
o.append(hl(96, T, 1100, 1, 1, "mark", 1))
o.append(tag(cx(96, 28), ly(T, 1), "복사본", BL, 1))
o.append(p(f"position:absolute;left:1240px;top:{T}px;font-family:{MONO};font-size:30px;font-weight:700;color:{K4}", "my_cart", at("fade", 2)))
o.append(slot_row(["coffee"], 1240, T + 52, K4, K4BG, 160, 92, 26, attrs=at("rise", 2)))
o.append(tag(1430, T + 98, "그대로예요", K4, 2, 28))
o.append(p(f"position:absolute;left:1240px;top:{T + 200}px;font-family:{MONO};font-size:30px;font-weight:700;color:{K5}", "big_cart", at("fade", 3)))
o.append(slot_row(["coffee", "cake"], 1240, T + 252, K5, K5BG, 160, 92, 26, attrs=at("rise", 3)))
o.append(caption("원본을 고칠지, 새로 만들어 돌려줄지 정하고 써요.", 944, 4))
FS[0] = 30
W("m-copy", o, "원본은 두고 결과만 받고 싶으면 copy()로 복사본을 만들어 고친 뒤 return해요. 함수 안에서 13의 copy로 복사본을 만들고, 복사본에 append한 뒤 돌려줘요. my_cart는 coffee만 그대로이고 big_cart는 cake까지 들어 있어요. 원본을 바꾸는 게 목적이면 앞에서처럼 바로 고치고, 원본을 지키고 싶으면 복사본을 만들어 돌려줘요." + REAL)

# ---------- part 6 ----------
o = [sec("x-order")] + head(EB6, "주문 함수: 기본값과 재고 딕셔너리", K6)
FS[0] = 26
T = 190
TO = ["def take_order(stock, name, qty=1):", "    if stock[name] < qty:", '        print(f"{name} {qty}개: 재고가 {stock[name]}개뿐이에요")', "        return False", "    stock[name] -= qty", '    print(f"{name} {qty}개 나갔어요")', "    return True", "", 'stock = {"coffee": 3, "latte": 1, "cake": 2}', 'take_order(stock, "coffee", 2)', 'take_order(stock, "latte")', 'take_order(stock, "latte")', 'take_order(stock, "cake", qty=3)', "print(stock)"]
TOO = ["coffee 2개 나갔어요", "latte 1개 나갔어요", "latte 1개: 재고가 0개뿐이에요", "cake 3개: 재고가 2개뿐이에요", "{'coffee': 1, 'latte': 0, 'cake': 2}"]
o += cell({"id": "c-x1", "lines": TO, "n": 1, "out": TOO}, 96, T, 1728)
CB = code_box(96, T, 1728, 14)
for k, i in enumerate((0, 3, 4)):
    o.append(lspot(k + 1, *CB, *band(T, i), bar=(K2, K4, K5)[k]))
o.append(lspot_off(4))
o.append(tag(TX + 60, ly(T, 0), "기본값: 한 개 주문은 빼고 불러요", K2, 1, 26))
o.append(tag(TX + 60, ly(T, 3), "모자라면 여기서 끝나요", K4, 2, 26))
o.append(tag(TX + 60, ly(T, 4), "받은 딕셔너리 칸을 줄여요", K5, 3, 26))
o.append(spot(4, cx(96, 0) - 10, oy(T, 14, 2) - LH() / 2 - 6, tw("latte 1개: 재고가 0개뿐이에요") + 20, 2 * LH() + 22))
o.append(spot_off(5))
o.append(tag(cx(96, 0) + tw("{'coffee': 1, 'latte': 0, 'cake': 2}") + 30, oy(T, 14, 4), "밖의 stock이 줄었어요", K5, 5, 26))
FS[0] = 30
W("x-order", o, "기본값, 딕셔너리 넘기기, return을 모아 주문 함수를 만들어요. qty는 기본값 1이라 한 개 주문은 빼고 불러요. 재고가 모자라면 안내를 찍고 return False로 바로 나가요. 19에서 본 return을 만나면 함수가 끝나는 성질이에요. 재고가 있으면 받은 딕셔너리 칸을 줄이고 True를 돌려줘요. 마지막에 밖에서 stock을 찍으면 실제로 줄어 있어요. 돌려준 True, False는 이 셀에서는 쓰지 않았지만, 19의 can_order처럼 if 뒤에 바로 쓸 수 있어요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p6", "실습"))

o = [sec("x-receipt")] + head(EB6, "영수증 함수: 함수 안에서 함수 부르기", K6)
FS[0] = 25
T = 190
RC = ['menu = {"coffee": 4500, "latte": 5000, "cake": 6500}', "", "def calc_total(cart, menu):", "    total = 0", "    for name, qty in cart.items():", "        total += menu[name] * qty", "    return total", "", "def print_receipt(cart, menu, rate=0):", "    total = calc_total(cart, menu)", "    sale = total * rate // 100", "    for name, qty in cart.items():", '        print(f"{name:<7}{qty}개 {menu[name] * qty:>7,}원")', '    print(f"할인   {rate:>2}% {sale:>7,}원")', '    print(f"결제       {total - sale:>7,}원")']
o += cell({"id": "c-x2", "lines": RC, "n": 2}, 96, T, 1000)
o.append(underline(1, cx(96, 30), cx(96, 36), ly(T, 8) + 18, K2))
o.append(underline(2, cx(96, 12), cx(96, 22), ly(T, 9) + 18, GR))
o.append(underline(2, cx(96, 4), cx(96, 14), ly(T, 2) + 18, GR))
o.append(tag(cx(96, 36), ly(T, 9), "위에서 만든 함수", GR, 2, 24))
RCO = ["coffee 2개   9,000원", "cake   1개   6,500원", "할인    0%       0원", "결제        15,500원", "---", "latte  3개  15,000원", "cake   2개  13,000원", "할인   10%   2,800원", "결제        25,200원"]
FS[0] = 26
o += cell({"id": "c-x3", "lines": ['cart1 = {"coffee": 2, "cake": 1}', 'cart2 = {"latte": 3, "cake": 2}', "print_receipt(cart1, menu)", 'print("---")', "print_receipt(cart2, menu, rate=10)"], "n": 3, "out": RCO}, 1130, T, 694, sel=False, attrs=at("rise", 3), pytag=False)
o.append(underline(4, cx(1130, 27), cx(1130, 34), ly(T, 4) + 18, K2))
o.append(tag(cx(1130, 21), oy(T, 5, 7), "rate=10", K2, 4, 24, code=True))
o.append(zoom(4, 1130, oy(T, 5, 5) - LH(), 694, oy(T, 5, 8) - oy(T, 5, 5) + 2 * LH(), 60))
o.append(zoom_off(5))
FS[0] = 30
o.append(caption("할인이 없으면 rate를 빼고, 있을 때만 rate=10처럼 넣어요.", 944, 5))
W("x-receipt", o, "합계 함수를 영수증 함수 안에서 불러, 할인율 기본값과 함께 영수증을 찍어요. 17에서 쓴 장바구니 딕셔너리를 그대로 써요. calc_total은 합계만 돌려주고, print_receipt는 그 함수를 불러 합계를 받은 뒤 할인과 결제 금액을 찍어요. 할인율 rate는 기본값 0이라서 할인이 없으면 빼고 불러요. 둘째 손님만 rate=10으로 키워드 인자를 넣었어요. 한글은 두 칸을 차지해서 13에서 본 것처럼 할인, 결제 뒤 빈칸 수를 맞췄어요." + REAL)

o = [sec("x-point")] + head(EB6, "적립 함수: get과 기본값으로 포인트 쌓기", K6)
FS[0] = 30
T = 210
PT = ["def add_point(points, name, amount, rate=5):", "    points[name] = points.get(name, 0) + amount * rate // 100", "", 'points = {"kim": 300}', 'add_point(points, "kim", 9000)', 'add_point(points, "lee", 6500)', 'add_point(points, "lee", 10000, rate=10)', "print(points)"]
o += cell({"id": "c-x4", "lines": PT, "n": 4, "out": ["{'kim': 750, 'lee': 1325}"]}, 96, T, 1728)
o.append(underline(1, cx(96, 36), cx(96, 42), ly(T, 0) + 22, K2))
o.append(tag(cx(96, 45), ly(T, 0), "평소 5%, 행사 때만 rate=10", K2, 1, 26))
o.append(underline(2, cx(96, 19), cx(96, 36), ly(T, 1) + 22, K4))
o.append(tag(cx(96, 19), ly(T, 2), "처음 온 손님은 0에서 시작 (15)", K4, 2, 26, False))
o += rows(96, 690, [360, 300, 300], [("kim 9000", "+ 450", "750"), ("lee 6500", "+ 325", "325"), ("lee 10000, rate=10", "+ 1000", "1325")], 3, 74, ["부르기", "더한 값", "합"], 28)
o.append(tag(1180, 820, "return 없이 받은 딕셔너리에 쌓여요", K5, 6, 28, False))
W("x-point", o, "포인트 딕셔너리를 넘겨, 적립률 기본값과 get으로 손님별 포인트를 쌓아요. 적립률 rate는 기본값 5%이고, 행사 때만 rate=10으로 넣어요. 처음 온 lee는 딕셔너리에 키가 없어서 15에서 배운 get(name, 0)으로 0에서 시작해요. kim은 300에 9000원의 5%인 450을 더해 750이 돼요. 받은 딕셔너리에 바로 넣으니 return 없이도 밖의 points에 쌓여요." + REAL)

# ---------- wrap up ----------
o = [sec("trouble")] + head("정리", "막히면 오류의 마지막 줄을 봐요", RED)
tr = [("SyntaxError: parameter without a default follows ...", "def 줄에서 기본값 칸을 앞에 뒀어요", "기본값 칸을 뒤로"),
      ("SyntaxError: positional argument follows keyword ...", "부를 때 이름 없는 값을 뒤에 적었어요", "위치 인자를 앞으로"),
      ("NameError: name 'total' is not defined", "함수 안의 지역 변수를 밖에서 썼어요", "return으로 돌려받기"),
      ("UnboundLocalError: cannot access local variable", "안에서 바깥 변수를 읽다가 바꿨어요", "인자로 받고 return"),
      ("안에서 바꿨는데 밖이 그대로예요", "안에서 = 로 새 지역 변수를 만들었어요", "x = 함수(x)로 받기"),
      ("함수에 넘긴 리스트가 바뀌었어요", "받은 리스트를 append로 고쳤어요", "copy()로 복사해 쓰기"),
      ("부를 때마다 값이 처음으로 돌아가요", "지역 변수는 부를 때마다 새로 생겨요", "값을 밖에 두고 넘기기")]
o.append(f'<div style="position:absolute;left:96px;top:200px;width:1728px;height:46px;display:flex;flex-direction:row;gap:24px;border-bottom:3px solid {INK}">'
         + "".join(p(f"width:{w}px;flex:none;font-size:23px;font-weight:700;color:{GRAY}", t) for t, w in [("보이는 것", 900), ("이유", 520), ("고치기", 260)]) + '</div>')
for i, (q, a_, cmd) in enumerate(tr):
    y = 254 + i * 92
    color = RED if q.isascii() else OR
    o.append(f'<div{at("rise", 1)}{DELAY(i * 80)} style="position:absolute;left:96px;top:{y}px;width:1728px;height:92px;display:flex;flex-direction:row;align-items:center;gap:24px;border-bottom:2px solid {LINE}">'
             + p(f"width:900px;flex:none;{'font-family:' + MONO + ';font-size:25px;' if q.isascii() else 'font-size:27px;'}font-weight:700;color:{color};white-space:nowrap", e(q))
             + p(f"width:520px;flex:none;font-size:25px;color:{SUB}", e(a_))
             + p(f"width:260px;flex:none;font-size:25px;font-weight:700;color:{INK};white-space:nowrap", e(cmd)) + '</div>')
o.append(caption("헷갈리면 함수 안과 밖에서 print로 같은 변수를 찍어 비교해요.", 944, 2))
W("trouble", o, "빨간 줄은 오류 메시지, 주황 줄은 오류 없이 결과만 이상한 경우예요. 1번과 2번은 기본값과 키워드 인자의 순서 규칙이에요. 3번과 4번은 지역 변수와 전역 변수를 섞어 쓸 때 나요. 5번부터 7번은 오류 메시지가 없어서 더 찾기 어려워요. 함수 안과 밖에서 같은 변수를 찍어 보면 어느 상자의 값인지 보여요.", ("trouble", "정리"))

o = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>']
cheat = [('def f(a, b="M"):', "기본값 칸은 def 줄 뒤쪽에", "기본값", K2), ("f(1, b=2)", "키워드 인자는 부를 때 뒤쪽에", "키워드 인자", K2),
         ("total = 9000", "함수 안에서 만들고, 끝나면 사라져요", "지역 변수", K3), ('shop = "KANT"', "함수 밖에서 만들고, 안에서 읽어요", "전역 변수", K4),
         ("x = f(x)", "global보다 return으로 돌려받아 바꿔요", "바깥 값 바꾸기", K4), ("cart.append(x)", "넘긴 리스트는 원본이 바뀌어요", "리스트, 딕셔너리", K5),
         ("cart.copy()", "원본을 지키려면 복사해서 써요", "원본 지키기", K5)]
o.append(f'<div style="position:absolute;left:96px;top:210px;width:1728px;height:46px;display:flex;flex-direction:row;gap:24px;border-bottom:3px solid {INK}">'
         + "".join(p(f"width:{w}px;flex:none;font-size:23px;font-weight:700;color:{GRAY}", t) for t, w in [("이름", 300), ("모양", 520), ("기억할 것", 860)]) + '</div>')
for i, (code, d, name, c) in enumerate(cheat):
    y = 264 + i * 96
    o.append(f'<div{at("rise", 1)}{DELAY(i * 80)} style="position:absolute;left:96px;top:{y}px;width:1728px;height:96px;display:flex;flex-direction:row;align-items:center;gap:24px;border-bottom:2px solid {LINE}">'
             + p(f"width:300px;flex:none;font-size:28px;font-weight:700;color:{c}", e(name))
             + p(f"width:520px;flex:none;font-family:{MONO};font-size:30px;font-weight:700;color:{INK};white-space:pre", e(code))
             + p(f"width:860px;flex:none;font-size:29px;font-weight:500;color:{INK}", e(d)) + '</div>')
o.append(p(f"position:absolute;left:96px;top:966px;width:1728px;font-size:30px;font-weight:700;color:{SUB}", "다음 21에서는 함수를 값처럼 넘기는 lambda를 배워요."))
W("cheatsheet", o, "함수 안에서 = 로 넣은 이름은 지역 변수이고, 바깥 값을 바꿀 땐 global보다 인자와 return을 써요. 기본값 칸은 def 줄 뒤쪽에 두고, 키워드 인자는 부를 때 뒤쪽에 적어요. 밖에서 만든 변수는 전역 변수라서 함수 안에서 읽을 수 있어요. 리스트와 딕셔너리는 넘긴 원본이 바뀐다는 점을 기억해요. 19와 20으로 함수를 마쳤고, 21에서는 함수를 값처럼 다른 함수에 넘기는 lambda를 봐요.")

# ---------- toc: number, title, what is in it, pages; hairlines only ----------
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
parts = [(K1, "왜 필요한가", "매번 적는 M, 사라진 total, 기본값과 안팎 그림", "s-why", "s-min"),
         (K2, "기본값과 키워드 인자", "여러 기본값, 칸 이름으로 넣기, 순서 규칙, print와 sorted", "k-default", "k-known"),
         (K3, "지역 변수", "안에서 만든 변수, 매개변수, 부를 때마다 새로", "l-local", "l-life"),
         (K4, "전역 변수", "밖의 변수 읽기, 같은 이름, UnboundLocalError, global과 return", "g-read", "g-return"),
         (K5, "리스트와 딕셔너리 넘기기", "append로 원본 바뀌기, 숫자와 비교, 재고 줄이기, copy", "m-list", "m-copy"),
         (K6, "실습", "주문 함수, 영수증 함수, 포인트 적립", "x-order", "x-point")]
TOC_NOTE = "여섯 파트 중 3파트와 4파트, 지역 변수와 전역 변수가 이번 챕터의 중심이에요. 1파트는 19의 함수로는 불편한 두 장면과 큰 그림이에요. 2파트는 기본값과 키워드 인자예요. 5파트는 리스트와 딕셔너리를 넘겼을 때 원본이 바뀌는 경우, 6파트는 카페 실습이에요. 파트마다 새 커널에서 위에서부터 차례로 실행해요."
t = [f'<section id="toc" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>']
for i, (c, h, s, a, b) in enumerate(parts):
    y = 210 + i * 116
    t.append(f'<div{at("rise", 1)}{DELAY(i * 90)} style="position:absolute;left:96px;top:{y}px;width:1728px;height:116px;display:flex;flex-direction:row;align-items:center;gap:36px;border-bottom:2px solid {LINE}">'
             f'<p style="width:60px;flex:none;font-size:56px;font-weight:900;line-height:1.2;color:{c}">{i + 1}</p>'
             f'<p style="width:520px;flex:none;font-size:36px;font-weight:700;color:{INK}">{e(h)}</p>'
             f'<p style="flex:1;font-size:26px;color:{SUB}">{e(s)}</p>'
             f'<p style="width:140px;flex:none;font-size:26px;font-weight:700;color:{GRAY};text-align:right">{page[a]}–{page[b]}쪽</p></div>')
t.append(f'<p style="position:absolute;left:96px;top:944px;font-size:28px;color:{SUB}">{page["ready"]}쪽은 노트북 준비, {page["trouble"]}–{page["cheatsheet"]}쪽은 막힐 때와 한 장 요약이에요.</p>')
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(t) + f"\n<aside>{e(TOC_NOTE)}</aside>\n</section>\n")

DECK_TITLE = "함수 2 (기본값, 지역 변수와 전역 변수)"
deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-03T03:00:00Z"}, "lists": "css", "title": DECK_TITLE, "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
print(len(ORDER), "slides")
