"""Generates every slide of the Python basics 5 deck (16, sets) and slides/deck.json.

Story (CLAUDE.md 챕터 설계 틀): a day's orders where len() counts cups, not menus (why) -> the four containers
(big picture) -> set(nums) (smallest example) -> making, changing and checking sets -> |, & and - drawn as
Venn diagrams -> which container to pick, traps and errors -> real data (menu kinds, two classes, orders
not on the chapter 15 menu, the bill) -> one-page summary.

Layout follows the Stageshow rules (tools/DESIGN.md): one focal object per slide, terms written beside
the code line or the picture as leader tags instead of cards, no empty bands, values that change move
(fly) instead of swapping. Highlights come from the situation table in tools/HIGHLIGHT.md, as many kinds as fit:
slam on the cover, cursor and keycaps, spotlight, pen ring/underline/box, run band, line
spotlight, shake on a failure, pulse, code morph, zoom, staggered labels (delay), count-up. No typing effect.
Every cell and output comes from tools/demo.sh (tools/run_nb.py runs the cells with the project kernel).
Usage: python3 tools/gen.py slides
"""

import html, json, os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from highlight import (spot, spot_off, cursor, cursor_off, ring, box, underline, SLAM, DELAY, COUNT, MORPH, MORPH_FROM, tok,
                       run, run_off, lspot, lspot_off, zoom, zoom_off, keys, pulse, shake)

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
INK, SUB, LINE, CARD, BG = "#1D2330", "#4A5262", "#E1DED6", "#FFFFFF", "#F6F5F1"
BL, GR, OR, RED, TEAL, GRAY = "#2459C9", "#1F8A4C", "#B26A00", "#A33131", "#0F7C86", "#6A7180"
JP = "#B8560F"          # Jupyter, same as chapters 09 and 10
SEL = "#2F7DE1"         # selected cell bar, like VS Code's focus color
K1, K1BG = "#1E5FA8", "#E5EEF8"
K2, K2BG = "#A0620A", "#F7EEDD"
K3, K3BG = TEAL, "#E2F2F3"
K4, K4BG = "#A23B72", "#F6E7EF"
K5, K5BG = "#4A5262", "#ECEDF0"
GRBG, REDBG, GRAYBG = "#E6F4EC", "#F8E6E6", "#EEEFF2"
EB1, EB2, EB3, EB4, EB5 = "1. 집합이 뭔가요", "2. 바꾸고 확인하기", "3. 집합 연산", "4. 비교와 오류", "5. 실습"
NB = "basics.ipynb"
REAL = " 출력은 실제로 실행한 결과예요."
# Line tints, the same meaning as every deck: green run, gray skip, red error, blue mark, orange note.
HL = {"run": "#D6EEDF", "skip": "#E4E6EA", "err": "#F6DADA", "mark": "#DCE6F8", "note": "#F4E6CC"}


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


def sec(sid, transition="fade"):
    return f'<section id="{sid}" data-transition="{transition}" style="background:{BG};color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">'


def head(eyebrow, title, color):
    return [p(f"position:absolute;left:96px;top:48px;width:1728px;font-size:26px;font-weight:700;color:{color}", e(eyebrow), ' id="eyebrow"'),
            f'<h2 id="title" style="position:absolute;left:96px;top:92px;width:1728px;font-size:56px;font-weight:700;line-height:1.2;color:{INK}">{title}</h2>']


def caption(text, top=960, order=None):
    return p(f"position:absolute;left:96px;top:{top}px;width:1728px;font-size:32px;font-weight:700;line-height:1.4;color:{INK}", text, ' id="caption"' + (at("rise", order) if order else ' data-build-in="rise"'))


# ---------- notebook cells, drawn at CF[0] px ----------
CF = [30]


def LH():
    return CF[0] * 1.45


def cell_h(c):
    return 20 + len(c["lines"]) * LH() + sum(10 + LH() for _ in c.get("out", []))


def cell(c, left, top, w, sel=False, attrs=""):
    fs, lines, n = CF[0], c["lines"], c.get("n")
    o = [f'<div id="{c["id"]}"{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;display:flex;flex-direction:column;gap:10px">']
    bar = f'<div style="width:7px;flex:none;border-radius:4px;background:{SEL if sel else "transparent"}"></div>'
    gutter = p(f"width:58px;flex:none;font-family:{MONO};font-size:22px;color:{GRAY};text-align:right;padding-top:12px", f"[{n}]" if n else "")
    txt = "".join(p(f"font-family:{MONO};font-size:{fs}px;line-height:1.45;white-space:pre;color:{INK}", e(l) if l else "&#160;") for l in lines)
    tag_ = p(f"position:absolute;right:14px;bottom:6px;font-size:18px;color:{GRAY}", "Python")
    o.append(f'<div style="display:flex;flex-direction:row;gap:10px;align-items:stretch">{bar}{gutter}'
             f'<div style="flex:1;position:relative;background:#FFFFFF;border:2px solid {LINE};border-radius:10px;padding:8px 18px;display:flex;flex-direction:column">{txt}{tag_}</div></div>')
    for l in c.get("out", []):
        col = RED if re.match(r"[A-Za-z]+Error", l) else INK
        wide = c.get("wide")
        t = re.sub(r"([가-힣])", r'<span style="display:inline-block;width:1.2em;text-align:center">\1</span>', e(l)) if wide else e(l)
        o.append(p(f"margin-left:85px;padding:0 20px;font-family:{MONO};font-size:{fs}px;line-height:1.45;white-space:pre;color:{col}", t))
    o.append('</div>')
    return o


def ly(top, i):
    """Center y of code line i of a cell drawn at top."""
    return top + 10 + i * LH() + LH() / 2


def oy(top, n, j):
    """Center y of output line j of a cell with n code lines."""
    return top + 20 + n * LH() + 10 + j * (LH() + 10) + LH() / 2


def tw(s):
    """Rendered width of a code string: Hangul about one em, the rest 0.6 em."""
    return sum(CF[0] * (1.0 if '가' <= ch <= '힣' else 0.6) for ch in s)


def tx(left, lines, gap=34, out=False):
    """x just right of the longest of the given strings inside a cell drawn at left."""
    return int(left + (105 if out else 105) + max(tw(l) for l in lines) + gap)


def hl(left, top, w, i, n=1, kind="run", order=1):
    """Tints code lines i..i+n-1 of a cell (drawn over the cell, multiplied so the code stays dark)."""
    y = top + 10 + i * LH()
    return f'<div{at("fade", order)} style="position:absolute;left:{left + 89}px;top:{y:.0f}px;width:{w - 93}px;height:{n * LH():.0f}px;background:{HL[kind]};mix-blend-mode:multiply;border-radius:6px"></div>'


def hlo(left, top, w, ncode, j, kind="run", order=1, width=None):
    """Tints output line j."""
    y = top + 20 + ncode * LH() + 10 + j * (LH() + 10) - 3
    ww = width or (w - 95)
    return f'<div{at("fade", order)} style="position:absolute;left:{left + 95}px;top:{y:.0f}px;width:{ww:.0f}px;height:{LH() + 6:.0f}px;background:{HL[kind]};mix-blend-mode:multiply;border-radius:6px"></div>'


def tag(x, y, text, color, order=None, size=28, lead=True, anim="fade", mono=False):
    """A leader label: '← text' centred on y. No box."""
    fam = f"font-family:{MONO};" if mono else ""
    t = ("← " if lead else "") + text
    return p(f"position:absolute;left:{x}px;top:{y - size * 0.73:.0f}px;{fam}font-size:{size}px;font-weight:700;line-height:1.45;color:{color};white-space:nowrap", t, at(anim, order))


def code_span(text, color=INK, bg=None, size=30):
    b = f"background:{bg};border-radius:8px;padding:0 10px;" if bg else ""
    return f'<span style="font-family:{MONO};font-size:{size}px;font-weight:700;color:{color};{b}white-space:pre">{e(text)}</span>'


def mono(text, size=28, color=INK, bg="#F1F0EC", extra=""):
    return p(f"font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.4;color:{color};background:{bg};border-radius:10px;padding:4px 16px;white-space:pre;{extra}", e(text))


def fix(left, top, bad, good, order, size=30, note=None):
    """The wrong line struck through, an arrow, the right line."""
    return (f'<div{at("rise", order)} style="position:absolute;left:{left}px;top:{top}px;display:flex;flex-direction:row;align-items:center;gap:20px">'
            + p(f"font-size:{size}px;font-weight:900;color:{RED}", "✕")
            + p(f"font-family:{MONO};font-size:{size}px;font-weight:700;color:{RED};text-decoration:line-through;text-decoration-thickness:3px;white-space:pre", e(bad))
            + f'<x-shape kind="arrow-right" style="width:60px;height:28px;flex:none;background:#C9CED8"></x-shape>'
            + p(f"font-size:{size}px;font-weight:900;color:{GR}", "✓")
            + p(f"font-family:{MONO};font-size:{size}px;font-weight:700;color:{INK};background:{GRBG};border:3px solid {GR};border-radius:14px;padding:4px 18px;white-space:pre", e(good))
            + (p(f"font-size:26px;font-weight:700;color:{SUB};white-space:nowrap", e(note)) if note else "") + '</div>')


def marker(mid, x, y, w=10, h=10):
    """An invisible box that a flying chip starts from."""
    return f'<div id="{mid}" style="position:absolute;left:{x:.0f}px;top:{y:.0f}px;width:{w:.0f}px;height:{h:.0f}px"></div>'


def ref_box(left, top, w, lines, out, title, attrs="", fs=24):
    """Longer code that a shortcut replaces. It uses if, which students have not learned yet, so it is read-only."""
    code = "".join(p(f"font-family:{MONO};font-size:{fs}px;line-height:1.45;white-space:pre;color:{SUB}", e(l) if l else "&#160;") for l in lines)
    res = "".join(p(f"font-family:{MONO};font-size:{fs}px;line-height:1.45;white-space:pre;color:{GRAY}", e(l)) for l in out)
    return (f'<div{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;border:3px dashed #B4B9C3;border-radius:18px;padding:18px 26px;display:flex;flex-direction:column;gap:10px">'
            + '<div style="display:flex;flex-direction:row;align-items:center;gap:14px">' + p(f"font-size:22px;font-weight:700;color:#FFFFFF;background:{GRAY};border-radius:8px;padding:2px 12px;white-space:nowrap", e(title))
            + p(f"font-size:22px;color:{GRAY};white-space:nowrap", "if는 17에서 배워요. 읽기만 해요.") + '</div>'
            + f'<div style="display:flex;flex-direction:column">{code}</div>' + f'<div style="display:flex;flex-direction:column;border-top:2px solid {LINE};padding-top:8px">{res}</div></div>')


# ---------- set pictures ----------
def chip(text, color=K1, bg=K1BG, fs=30, extra="", attrs=""):
    return p(f"font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:1.2;color:{INK};background:{bg};border:3px solid {color};border-radius:999px;padding:6px 22px;white-space:pre;{extra}", e(text), attrs)


def bag(items, left, top, w, h, color=K1, bg=K1BG, attrs="", fs=34, name=None, pos=None, sid=None, chip_attrs=None, empty="비어 있어요"):
    """A set drawn as a pouch with a tie on top. Items float inside with no slot numbers (no order).
    pos: (x, y) of each item as fractions of the pouch. chip_attrs: extra attributes for each item (fly in)."""
    pos = pos or [(0.26, 0.36), (0.70, 0.32), (0.46, 0.68), (0.80, 0.70), (0.20, 0.72), (0.52, 0.40)]
    ida = f' id="{sid}"' if sid else ""
    tie = 200 if name and len(name) > 6 else 150
    o = [f'<div{ida}{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px">',
         f'<div style="position:absolute;left:{w / 2 - tie / 2:.0f}px;top:0;width:{tie}px;height:38px;border-radius:12px 12px 4px 4px;background:{color}"></div>',
         f'<div style="position:absolute;left:0;top:30px;width:{w}px;height:{h - 30}px;border:5px solid {color};background:{CARD};border-radius:80px 80px {min(w, h) * 0.42:.0f}px {min(w, h) * 0.42:.0f}px"></div>']
    if name:
        o.append(p(f"position:absolute;left:{w / 2 - tie / 2:.0f}px;top:0;width:{tie}px;height:38px;font-family:{MONO};font-size:24px;font-weight:700;line-height:38px;text-align:center;color:#FFFFFF", e(name)))
    for i, it in enumerate(items):
        x, y = pos[i % len(pos)]
        ca = (chip_attrs or {}).get(i, "")
        o.append(f'<div{ca} style="position:absolute;left:{x * w:.0f}px;top:{30 + y * (h - 30):.0f}px;transform:translate(-50%,-50%)">' + chip(it, color, bg, fs) + '</div>')
    if not items:
        o.append(p(f"position:absolute;left:0;top:{h / 2 + 4:.0f}px;width:{w}px;text-align:center;font-size:28px;color:{GRAY}", empty))
    o.append('</div>')
    return "".join(o)


def slots(items, left, top, w=150, h=96, attrs="", fs=36, color=GRAY, bg=GRAYBG, ids=None, idx=True, strike=()):
    """A list in a row of boxes with index numbers above."""
    o = [f'<div{attrs} style="position:absolute;left:{left}px;top:{top}px;display:flex;flex-direction:row;gap:10px">']
    for i, it in enumerate(items):
        ida = f' id="{ids[i]}"' if ids else ""
        o.append('<div style="display:flex;flex-direction:column;align-items:center;gap:8px">'
                 + (p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{GRAY}", str(i)) if idx else "")
                 + p(f"width:{w}px;height:{h}px;border-radius:14px;border:3px solid #C9CED8;background:{CARD};font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:{h - 6}px;text-align:center;color:{INK};white-space:pre", e(it), ida) + '</div>')
    o.append('</div>')
    return "".join(o)


VA, VB = K1, K2
_vn = [0]


def venn(left, top, a_only, both, b_only, la="a", lb="b", w=760, h=470, hi=(), sid=None, attrs="", fs=28, regions=None):
    """Two overlapping circles with values in each region.
    hi: list of (mode, color, order) where mode is union, inter, a-b or b-a. Each one fades in on its own click.
    regions: optional captions under the three regions, as (text, order)."""
    _vn[0] += 1
    k = f"vn{_vn[0]}"
    r = h * 0.40
    cy = h / 2 + 22
    ca, cb = w / 2 - r * 0.62, w / 2 + r * 0.62
    circ = lambda cx, extra="": f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r:.0f}" {extra}/>'
    ida = f' id="{sid}"' if sid else ""
    o = [f'<div{ida}{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h + (60 if regions else 0)}px">']
    o.append(f'<svg style="position:absolute;left:0;top:0;width:{w}px;height:{h}px" viewBox="0 0 {w} {h}">'
             + circ(ca, f'fill="{K1BG}" fill-opacity="0.55"') + circ(cb, f'fill="{K2BG}" fill-opacity="0.55"') + '</svg>')
    for i, (mode, col, order) in enumerate(hi):
        m = f"{k}m{i}"
        if mode == "union":
            body = circ(ca, f'fill="{col}"') + circ(cb, f'fill="{col}"')
        elif mode == "inter":
            body = f'<defs><clipPath id="{m}">{circ(cb)}</clipPath></defs>' + circ(ca, f'fill="{col}" clip-path="url(#{m})"')
        else:
            keep, cut = (ca, cb) if mode == "a-b" else (cb, ca)
            body = (f'<defs><mask id="{m}"><rect x="0" y="0" width="{w}" height="{h}" fill="#FFFFFF"/>{circ(cut, chr(102) + "ill=" + chr(34) + "#000000" + chr(34))}</mask></defs>'
                    + circ(keep, f'fill="{col}" mask="url(#{m})"'))
        o.append(f'<svg{at("fade", order)} style="position:absolute;left:0;top:0;width:{w}px;height:{h}px;opacity:0.42" viewBox="0 0 {w} {h}">{body}</svg>')
    o.append(f'<svg style="position:absolute;left:0;top:0;width:{w}px;height:{h}px" viewBox="0 0 {w} {h}">'
             + circ(ca, f'fill="none" stroke="{VA}" stroke-width="5"') + circ(cb, f'fill="none" stroke="{VB}" stroke-width="5"') + '</svg>')
    o.append(p(f"position:absolute;left:{ca - 200:.0f}px;top:{cy - r - 54:.0f}px;width:400px;text-align:center;font-family:{MONO};font-size:{max(26, fs)}px;font-weight:700;color:{VA}", e(la)))
    o.append(p(f"position:absolute;left:{cb - 200:.0f}px;top:{cy - r - 54:.0f}px;width:400px;text-align:center;font-family:{MONO};font-size:{max(26, fs)}px;font-weight:700;color:{VB}", e(lb)))
    for cx, items in [(w / 2 - r, a_only), (w / 2, both), (w / 2 + r, b_only)]:
        n = len(items)
        for j, it in enumerate(items):
            y = cy + (j - (n - 1) / 2) * (fs * 2.0)
            o.append(f'<p style="position:absolute;left:{cx - 100:.0f}px;top:{y - fs * 0.7:.0f}px;width:200px;text-align:center;font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:1.4;color:{INK}">{e(it)}</p>')
    if regions:
        for cx, (t, order) in zip([w / 2 - r * 1.1, w / 2, w / 2 + r * 1.1], regions):
            o.append(p(f"position:absolute;left:{cx - 130:.0f}px;top:{h + 6}px;width:260px;text-align:center;font-size:28px;font-weight:700;color:{SUB}", e(t), at("rise", order)))
    o.append('</div>')
    return "".join(o)


def rows_table(left, top, widths, rows, head_=None, rh=88, fs=30, order0=None, ids=None, fonts=None, colors=None, hl_row=None):
    """A light table: header in gray, rows split by hairlines, no boxes.
    fonts: per column 'mono' or 'sans'. colors: per column ink. hl_row: index of a row drawn tinted."""
    o, y = [], top
    W_ = sum(widths) + 24 * (len(widths) - 1)
    if head_:
        o.append(f'<div style="position:absolute;left:{left}px;top:{y}px;width:{W_}px;height:52px;display:flex;flex-direction:row;gap:24px;border-bottom:3px solid {INK}">'
                 + "".join(p(f"width:{cw}px;flex:none;font-size:24px;font-weight:700;color:{GRAY}", e(c)) for c, cw in zip(head_, widths)) + '</div>')
        y += 52
    for i, r in enumerate(rows):
        cells_ = ""
        for k, (c, cw) in enumerate(zip(r, widths)):
            f_ = (fonts or ["sans"] * len(widths))[k]
            col = (colors or [INK] * len(widths))[k]
            cells_ += p(f"width:{cw}px;flex:none;{'font-family:' + MONO + ';' if f_ == 'mono' else ''}font-size:{fs if f_ != 'small' else fs - 4}px;font-weight:{700 if f_ != 'small' else 500};line-height:1.35;color:{col};white-space:pre-wrap", c)
        ida = f' id="{ids[i]}"' if ids else ""
        bgc = f"background:{hl_row[1]};" if hl_row and hl_row[0] == i else ""
        o.append(f'<div{ida}{at("rise", order0 + i) if order0 else ""} style="position:absolute;left:{left}px;top:{y + i * rh}px;width:{W_}px;height:{rh}px;display:flex;flex-direction:row;align-items:center;gap:24px;border-bottom:2px solid {LINE};{bgc}">{cells_}</div>')
    return o


MENUS = 'menus = {"coffee", "latte", "cake"}'
ORDERS = 'orders = ["coffee", "latte", "coffee", "cake", "latte"]'

# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:{BG};font-family:{SANS};font-variant-ligatures:none;padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#F2B27A;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
       f'<h1{SLAM(1)} style="font-size:92px;font-weight:900;line-height:1.1;color:#F6F5F1">파이썬 기초 5<br>집합</h1>',
       '<p style="font-size:40px;line-height:1.4;color:#BFC6D4">중복 없이 모으고<br>겹치는 것 찾기</p>']
# the chapter in one picture: a list with repeats drops into a pouch that keeps one of each
cov.append(f'<p style="position:absolute;left:1010px;top:250px;font-family:{MONO};font-size:44px;font-weight:700;color:#9AA3B5;white-space:pre">[3, 1, 3, 2, 1]</p>')
cov.append(f'<x-shape kind="arrow-right" style="position:absolute;left:1180px;top:350px;width:70px;height:40px;transform:rotate(90deg);background:#5A6172"></x-shape>')
cov.append(f'<div style="position:absolute;left:1240px;top:420px;width:180px;height:44px;border-radius:12px 12px 4px 4px;background:#9DBDEB"></div>')
cov.append(f'<div style="position:absolute;left:1010px;top:452px;width:640px;height:390px;border:6px solid #9DBDEB;border-radius:90px 90px 170px 170px"></div>')
for x, y, v in [(1150, 560, "3"), (1440, 590, "1"), (1290, 700, "2")]:
    cov.append(p(f"position:absolute;left:{x}px;top:{y}px;width:110px;height:110px;border-radius:50%;border:4px solid #9DBDEB;background:#252B36;font-family:{MONO};font-size:54px;font-weight:700;line-height:102px;text-align:center;color:#E6E9EF", v))
W("cover", cov, "이번 챕터는 같은 값을 하나만 담는 집합이에요. 13에서 리스트와 튜플, 15에서 딕셔너리를 배웠어요. 1파트에서 집합이 무엇인지 그림으로 잡고, 2파트에서 넣고 빼고 확인해요. 3파트는 합집합, 교집합, 차집합을 원 두 개로 그려요. 4파트에서 무엇에 담을지 고르는 법과 자주 나는 오류를 보고, 5파트에서 주문 목록과 수강생 명단, 15의 메뉴판에 써 봐요. 모든 예제는 12~15에서 쓰던 노트북 셀에 이어서 적고 실행해요.", ("intro", "들어가기"))

ORDER.append("toc")   # written last, after page numbers are known

# ---------- ready: the notebook bar is the one object, the cursor shows what to check ----------
o = [sec("ready")] + head("들어가기", "15에서 쓰던 노트북에 이어서 적어요", JP)
bx, by, bw = 96, 300, 1728
o.append(f'<div id="nb-bar" style="position:absolute;left:{bx}px;top:{by}px;width:{bw}px;height:96px;background:#ECEAE3;border-radius:18px;display:flex;flex-direction:row;align-items:center;padding:0 30px;gap:30px">'
         + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{INK};white-space:nowrap", e(NB), ' id="nb-file"')
         + "".join(p(f"font-size:24px;color:{SUB};white-space:nowrap", e(t)) for t in ["+ Code", "+ Markdown", "▷ Run All", "↻ Restart"]) + '<div style="flex:1"></div>'
         + p(f"font-size:26px;font-weight:700;color:{GR};background:{GRBG};border-radius:10px;padding:6px 16px;white-space:nowrap", ".venv (Python 3.14.6)", ' id="nb-kernel"') + '</div>')
o.append(f'<div style="position:absolute;left:{bx}px;top:{by + 120}px;width:{bw}px;height:210px;background:#FFFFFF;border:2px solid {LINE};border-radius:14px;padding:22px 30px;display:flex;flex-direction:column;gap:6px">'
         + "".join(p(f"font-family:{MONO};font-size:28px;line-height:1.45;color:{c};white-space:pre", e(t)) for t, c in
                   [("# 15 딕셔너리", GRAY), ('menu = {"coffee": 4500, "latte": 5000}', "#B4B9C3"), ("", INK), ("# 16 집합  ← 여기부터 이어서 적어요", JP)]) + '</div>')
o.append(p(f"position:absolute;left:{bx + 20}px;top:{by - 64}px;font-size:28px;font-weight:700;color:{JP};white-space:nowrap", "① VS Code로 hello-uv 폴더를 열고 이 파일을 열어요", at("fade", 1)))
o.append(cursor(1, target="nb-file"))
o.append(p(f"position:absolute;left:{bx + bw - 520}px;top:{by - 64}px;width:500px;text-align:right;font-size:28px;font-weight:700;color:{GR};white-space:nowrap", "② 커널이 .venv인지 봐요", at("fade", 2)))
o.append(cursor(2, target="nb-kernel"))
o.append(cursor_off(3))
o.append(keys(4, bx + bw - 330, by + 230, "Shift+Enter"))
o.append(p(f"position:absolute;left:{bx + bw - 330}px;top:{by + 186}px;font-size:24px;font-weight:700;color:{GRAY};white-space:nowrap", "셀 실행", at("fade", 4)))
o.append(p(f"position:absolute;left:96px;top:700px;width:1728px;font-size:26px;font-weight:700;color:{GRAY}", "다시 쓰는 것", ' data-build-in="fade order 3"'))
o += rows_table(96, 744, [180, 1524], [["13", "리스트와 튜플, <code style=\"font-family:'JetBrains Mono'\">for</code>, <code style=\"font-family:'JetBrains Mono'\">sorted()</code>, <code style=\"font-family:'JetBrains Mono'\">count()</code>, f-string"],
                                        ["14 · 15", "<code style=\"font-family:'JetBrains Mono'\">in</code>과 <code style=\"font-family:'JetBrains Mono'\">not in</code>, 딕셔너리와 <code style=\"font-family:'JetBrains Mono'\">KeyError</code>"]],
                rh=76, fs=28, order0=3, colors=[JP, INK])
W("ready", o, "09에서 만든 hello-uv 폴더를 VS Code로 열고, 12~15에서 쓰던 basics.ipynb에 이어서 적어요. 오른쪽 위 커널이 .venv인지 먼저 봐요. 13의 리스트, 튜플, for, sorted, count와 14의 in, 15의 딕셔너리를 그대로 써요. 슬라이드의 출력은 tools/demo.sh가 hello-uv 커널에서 같은 셀을 실제로 실행한 결과예요. 셀 번호는 파트마다 [1]부터 다시 셌어요.")

# ---------- part 1: what is a set ----------
# why: len() counts cups, not menus
o = [sec("s-why")] + head(EB1, "주문은 5잔인데, 메뉴는 몇 가지일까요", K1)
c = {"id": "c-why", "lines": [ORDERS, "print(orders)", "print(len(orders))"], "n": 1, "out": ["['coffee', 'latte', 'coffee', 'cake', 'latte']", "5"]}
CX, CY, CW = 96, 220, 1728
o += cell(c, CX, CY, CW, sel=True)
o.append(ring(1, CX + 104, oy(CY, 3, 1) - 26, 24, 52, RED))
o.append(tag(CX + 160, oy(CY, 3, 1), "len은 잔 수를 세요. 메뉴 종류는 3가지인데요", RED, 1))
chips_y = 600
x = 96
cols = {"coffee": (K1, K1BG), "latte": (K4, K4BG), "cake": (K3, K3BG)}
for i, v in enumerate(["coffee", "latte", "coffee", "cake", "latte"]):
    w_ = tw(f'"{v}"') * 52 / 30 + 56
    o.append(f'<div{at("rise", 2)} style="position:absolute;left:{x:.0f}px;top:{chips_y}px">' + chip(f'"{v}"', cols[v][0], cols[v][1], 52) + '</div>')
    if v != "cake":
        o.append(underline(3, int(x + 10), int(x + w_ - 10), chips_y + 104, cols[v][0], 7))
    x += w_ + 44
o.append(tag(96, chips_y + 190, "같은 메뉴가 두 번씩 있어요. 겹친 것을 하나로 줄여야 종류가 나와요", INK, 3, 32, lead=False))
o.append(caption("같은 값을 하나만 남기는 그릇이 집합(set)이에요.", 960, 4))
W("s-why", o, "주문 리스트의 len은 잔 수예요. 메뉴가 몇 가지인지는 알려 주지 않아요. 카페 주문 5잔이 리스트에 쌓였어요. coffee와 latte가 두 번씩 있어서 메뉴는 coffee, latte, cake 세 가지예요. 지금 배운 것만으로 종류를 세려면 하나씩 보면서 처음 보는 메뉴인지 물어야 해요. 이 일을 한 번에 해 주는 그릇이 집합이에요. 이 장의 orders를 1파트 뒤에서 다시 써요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("what", "집합이 뭔가요"))

# big picture: four containers, the set is the one in color
o = [sec("s-four")] + head(EB1, "집합은 네 번째 그릇이에요", K1)
PX = [276, 668, 1060, 1452]
PW = 372
# list: numbered slots
o.append(slots(["1", "2"], PX[0], 214, 140, 100, fs=38))
# tuple: same slots, locked
o.append(slots(["1", "2"], PX[1], 214, 140, 100, fs=38))
o.append(f'<x-icon name="Lock" style="position:absolute;left:{PX[1] + 306}px;top:262px;width:44px;height:44px;color:{GRAY}"></x-icon>')
# dict: lockers with a key on the door
for j, (kk, vv) in enumerate([('"a"', "1"), ('"b"', "2")]):
    o.append(f'<div style="position:absolute;left:{PX[2] + j * 166}px;top:214px;width:150px;height:140px;border:3px solid #C9CED8;border-radius:14px;background:{CARD};overflow:hidden">'
             + p(f"height:44px;background:#ECEAE3;font-family:{MONO};font-size:24px;font-weight:700;line-height:44px;text-align:center;color:{INK}", e(kk))
             + p(f"font-family:{MONO};font-size:38px;font-weight:700;line-height:90px;text-align:center;color:{INK}", vv) + '</div>')
# set: the pouch
o.append(bag(["1", "2"], PX[3], 196, 340, 190, K1, K1BG, fs=34, pos=[(0.32, 0.52), (0.68, 0.48)]))
for i, (nm, lit, c_) in enumerate([("리스트", "[1, 2]", GRAY), ("튜플", "(1, 2)", GRAY), ("딕셔너리", '{"a": 1}', GRAY), ("집합", "{1, 2}", K1)]):
    o.append(f'<div style="position:absolute;left:{PX[i]}px;top:420px;width:{PW}px;display:flex;flex-direction:row;align-items:center;gap:16px">'
             + p(f"font-size:34px;font-weight:700;color:{K1 if c_ == K1 else INK}", nm) + mono(lit, 28, c_ if c_ == K1 else SUB, K1BG if c_ == K1 else "#ECEAE3") + '</div>')
rows_ = [("순서", ["있어요", "있어요", "넣은 순서", "없어요"]), ("중복", ["돼요", "돼요", "키는 안 돼요", "안 돼요"]),
         ("꺼내기", ["[번호]", "[번호]", "[키]", "못 꺼내요"]), ("바꾸기", ["돼요", "안 돼요", "돼요", "돼요"])]
for r, (rn, vals) in enumerate(rows_):
    y = 520 + r * 96
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:96px;border-top:2px solid {LINE}"></div>')
    for i, v in enumerate(vals):
        o.append(p(f"position:absolute;left:{PX[i]}px;top:{y + 24}px;width:{PW}px;font-size:32px;font-weight:700;color:{K1 if i == 3 else INK};white-space:nowrap", e(v)))
    o.append(p(f"position:absolute;left:96px;top:{y + 26}px;font-size:28px;font-weight:700;color:{GRAY}", e(rn)))
o.append(f'<div style="position:absolute;left:96px;top:904px;width:1728px;border-top:2px solid {LINE}"></div>')
o.append(f'<div id="set-col" style="position:absolute;left:{PX[3] - 10}px;top:190px;width:{PW + 20}px;height:720px"></div>')
o.append(spot(1, target="set-col", pad=8, r="22", dim=0.45))
o.append(spot_off(2))
o.append(caption("집합은 딕셔너리처럼 중괄호를 쓰지만 키 없이 값만 적어요.", 952, 2))
W("s-four", o, "집합은 리스트, 튜플, 딕셔너리 다음에 배우는 네 번째 그릇이에요. 리스트와 튜플은 순서가 있어서 번호로 꺼내고, 튜플은 만든 뒤 바꿀 수 없어요. 딕셔너리는 15에서 본 것처럼 넣은 순서를 지키고 키로 꺼내요. 집합은 딕셔너리와 같은 중괄호를 쓰지만 키: 값이 아니라 값만 적어요. 순서가 없고 중복이 없어서 번호로도, 키로도 꺼낼 수 없어요. 값을 넣고 빼는 것은 돼요.")

# smallest example: set(list), the repeats fall away
o = [sec("s-min")] + head(EB1, "set()에 리스트를 넣으면 같은 값이 하나만 남아요", K1)
c = {"id": "c-min", "lines": ["nums = [3, 1, 3, 2, 1]", "print(nums)", "print(set(nums))"], "n": 2, "out": ["[3, 1, 3, 2, 1]", "{1, 2, 3}"]}
CX, CY, CW = 96, 220, 860
o += cell(c, CX, CY, CW, sel=True)
o.append(hl(CX, CY, CW, 2, 1, "mark", 1))
o.append(tag(CX + 105 + tw("{1, 2, 3}") + 34, oy(CY, 3, 1), "3과 1이 하나씩만 남았어요", K1, 2))
o.append(p(f"position:absolute;left:96px;top:600px;font-size:28px;font-weight:700;color:{GRAY}", "리스트 · 넣은 그대로, 칸마다 번호"))
o.append(slots(["3", "1", "3", "2", "1"], 96, 650, 150, 110, fs=44, ids=["sl0", "sl1", "sl2", "sl3", "sl4"]))
o.append(box(2, 96 + 2 * 160 - 8, 650 + 40 - 8, 166, 126, RED, 5))
o.append(box(2, 96 + 4 * 160 - 8, 650 + 40 - 8, 166, 126, RED, 5))
o.append(tag(96, 870, "겹친 값은 주머니에 또 들어가지 않아요", RED, 2, 28, lead=False))
o.append(p(f"position:absolute;left:1060px;top:220px;font-size:28px;font-weight:700;color:{K1}", "집합 · 같은 값은 하나만, 번호 없음", at("fade", 1)))
o.append(bag(["3", "1", "2"], 1060, 280, 764, 620, K1, K1BG, fs=60, name="set", pos=[(0.28, 0.38), (0.72, 0.36), (0.50, 0.72)],
             chip_attrs={0: ' data-build-in="fly order 1" data-from="sl0"', 1: ' data-build-in="fly order 1" data-from="sl1"', 2: ' data-build-in="fly order 1" data-from="sl3"'}))
W("s-min", o, "set() 괄호 안에 리스트를 넣으면 같은 값은 하나만 남아요. 리스트는 넣은 값을 그대로, 넣은 순서대로 칸에 담아요. 같은 값을 두 번 넣으면 두 칸을 차지해요. 집합은 주머니라고 생각해요. 같은 값은 하나만 들어가고 칸 번호 없이 섞여 있어요. 그래서 3과 1은 하나씩만 남아 {1, 2, 3}이 돼요. 이 챕터는 이 주머니 그림 하나로 끝까지 가요. 집합(set)은 수학 시간의 그 집합이에요." + REAL)

# make with braces
o = [sec("s-make")] + head(EB1, "중괄호 안에 값만 적으면 집합이에요", K1)
c = {"id": "c-make", "lines": ["nums = {3, 1, 2, 3}", "print(nums)", "print(type(nums))", "print(len(nums))"], "n": 3, "out": ["{1, 2, 3}", "<class 'set'>", "3"]}
CX, CY, CW = 96, 230, 1000
o += cell(c, CX, CY, CW, sel=True)
x0 = CX + 105 + tw("nums = {3, 1, 2, ")
o.append(underline(1, int(x0) - 2, int(x0 + tw("3")) + 4, int(ly(CY, 0) + 22), OR, 5))
o.append(tag(tx(CX, ["nums = {3, 1, 2, 3}"]) , ly(CY, 0), "3을 두 번 적었어요", OR, 1))
ox = tx(CX, ["<class 'set'>"], out=True)
o.append(tag(ox, oy(CY, 4, 0), "오류 없이 하나만 남아요", K1, 2))
o.append(tag(ox, oy(CY, 4, 1), "set은 집합", K1, 2))
o.append(tag(ox, oy(CY, 4, 2), "값의 개수", K1, 2))
o.append(p(f"position:absolute;left:96px;top:720px;font-size:26px;font-weight:700;color:{GRAY}", "중괄호 안을 보고 구분해요", at("fade", 3)))
o.append(f'<div{at("rise", 3)} style="position:absolute;left:96px;top:770px;width:1728px;display:flex;flex-direction:row;align-items:center;gap:40px">'
         + mono('{"coffee": 4500}', 36, SUB, "#ECEAE3") + p(f"font-size:30px;font-weight:700;color:{SUB}", "키: 값이 있으면 딕셔너리")
         + '<div style="width:40px"></div>' + mono('{"coffee", "latte"}', 36, K1, K1BG) + p(f"font-size:30px;font-weight:700;color:{K1}", "값만 있으면 집합") + '</div>')
o.append(bag(["3", "1", "2"], 1200, 250, 624, 420, K1, K1BG, fs=52, name="nums", pos=[(0.28, 0.40), (0.72, 0.38), (0.50, 0.74)], attrs=at("rise", 2)))
W("s-make", o, "집합은 중괄호 안에 값만 쉼표로 이어서 만들어요. 15의 딕셔너리처럼 키: 값이 아니에요. 3을 두 번 적었지만 출력에는 하나만 남아요. 오류도 나지 않아요. type은 set이라고 알려 줘요. len은 값의 개수라 3이에요. 숫자 집합은 보통 작은 수부터 찍혀 나오지만, 정렬해 준다는 약속은 아니에요." + REAL)

# no order
o = [sec("s-order")] + head(EB1, "집합은 순서를 기억하지 않아요", K1)
LW = 852
c1 = {"id": "c-o1", "lines": [MENUS, "print(menus)", "print(sorted(menus))"], "n": 4, "out": ["{'latte', 'cake', 'coffee'}", "['cake', 'coffee', 'latte']"]}
c2 = {"id": "c-o2", "lines": [MENUS, "print(menus)", "print(sorted(menus))"], "n": 1, "out": ["{'coffee', 'cake', 'latte'}", "['cake', 'coffee', 'latte']"]}
CF[0] = 26
o.append(p(f"position:absolute;left:96px;top:220px;font-size:26px;font-weight:700;color:{K1}", "처음 실행"))
o += cell(c1, 96, 268, LW, sel=True)
o.append(p(f"position:absolute;left:972px;top:220px;font-size:26px;font-weight:700;color:{K1}", "Restart 하고 이 셀만 다시 실행", at("fade", 1)))
o += cell(c2, 972, 268, LW, attrs=at("rise", 1))
y0 = oy(268, 3, 0)
o.append(underline(2, 96 + 105, int(96 + 105 + tw("{'latte', 'cake', 'coffee'}")), int(y0 + 20), RED, 5))
o.append(underline(2, 972 + 105, int(972 + 105 + tw("{'coffee', 'cake', 'latte'}")), int(y0 + 20), RED, 5))
o.append(hlo(96, 268, LW, 3, 1, "run", 3, tw("['cake', 'coffee', 'latte']") + 30))
o.append(hlo(972, 268, LW, 3, 1, "run", 3, tw("['cake', 'coffee', 'latte']") + 30))
CF[0] = 30
o.append(p(f"position:absolute;left:96px;top:560px;width:1728px;font-size:34px;font-weight:700;line-height:1.5;color:{RED}", "print(menus)는 실행할 때마다 순서가 바뀔 수 있어요", at("rise", 2)))
o.append(p(f"position:absolute;left:96px;top:620px;width:1728px;font-size:30px;line-height:1.5;color:{SUB}", "내 화면이 슬라이드와 달라도 틀린 게 아니에요.", at("rise", 2)))
o.append(p(f"position:absolute;left:96px;top:740px;width:1728px;font-size:34px;font-weight:700;line-height:1.5;color:{GR}", "sorted()에 넣으면 언제나 abc 순서 리스트예요", at("rise", 3)))
o.append(p(f"position:absolute;left:96px;top:800px;width:1728px;font-size:30px;line-height:1.5;color:{SUB}", "13에서 배운 그 sorted()예요. 결과는 리스트라 대괄호로 나와요.", at("rise", 3)))
W("s-order", o, "집합은 값을 넣은 순서를 기억하지 않아요. 글자를 담은 집합을 print로 찍으면 적은 순서와 다르게 나와요. 커널을 다시 시작하고 같은 셀을 실행하면 또 다른 순서가 나올 수 있어요. 파이썬이 집합 안에서 값을 빨리 찾으려고 자기 방식대로 놓기 때문이에요. 그래서 수강생 화면의 순서가 슬라이드와 달라도 틀린 게 아니에요. 순서가 필요하면 13에서 배운 sorted()에 넣어요. 결과는 리스트라 대괄호로 나오고, 언제나 abc 순서예요. 슬라이드를 다시 만들 때 같은 출력이 나오도록 demo.sh는 커널마다 PYTHONHASHSEED를 고정했어요." + REAL)

# dedup: back to the orders from s-why
o = [sec("s-dedup")] + head(EB1, "set(orders)로 메뉴 종류를 뽑아요", K1)
c = {"id": "c-d", "lines": ["kinds = set(orders)", "print(kinds)", "print(len(orders), len(kinds))", "print(sorted(kinds))"], "n": 5,
     "out": ["{'latte', 'cake', 'coffee'}", "5 3", "['cake', 'coffee', 'latte']"]}
CX, CY, CW = 96, 220, 900
o += cell(c, CX, CY, CW, sel=True)
o.append(hl(CX, CY, CW, 0, 1, "mark", 1))
o.append(tag(CX + 105 + tw("5 3") + 34, oy(CY, 4, 1), "주문 5잔, 메뉴 3가지", K1, 2))
o.append(tag(CX + 105 + tw("['cake', 'coffee', 'latte']") + 34, oy(CY, 4, 2), "abc 순서", K1, 2))
o.append(p(f"position:absolute;left:96px;top:700px;font-size:28px;font-weight:700;color:{GRAY}", "orders · 1파트 처음의 주문 5잔"))
x = 96
ids = ["od0", "od1", "od2", "od3", "od4"]
for i, v in enumerate(["coffee", "latte", "coffee", "cake", "latte"]):
    w_ = tw(f'"{v}"') * 28 / 30 + 44
    o.append(f'<div style="position:absolute;left:{x:.0f}px;top:760px">' + chip(f'"{v}"', GRAY, GRAYBG, 28, attrs=f' id="{ids[i]}"') + '</div>')
    if i in (2, 4):
        o.append(box(2, int(x - 8), 750, int(w_ + 16), 74, RED, 4))
    x += w_ + 20
o.append(tag(96, 890, "겹친 coffee, latte는 또 들어가지 않아요", RED, 2, 28, lead=False))
o.append(bag(['"latte"', '"cake"', '"coffee"'], 1080, 240, 744, 660, K1, K1BG, fs=40, name="kinds", pos=[(0.30, 0.36), (0.70, 0.40), (0.50, 0.72)],
             chip_attrs={0: ' data-build-in="fly order 1" data-from="od1"', 1: ' data-build-in="fly order 1" data-from="od3"', 2: ' data-build-in="fly order 1" data-from="od0"'}))
W("s-dedup", o, "set(orders)로 바꾸면 겹친 주문이 하나씩만 남아서 메뉴 종류가 돼요. 1파트 처음에 본 주문 5잔 orders를 다시 써요. set() 괄호 안에 리스트를 넣으면 리스트의 값으로 집합을 만들어요. 겹친 coffee와 latte는 하나씩만 남아요. 주문은 5잔이지만 메뉴 종류는 3가지예요. 리스트 orders는 그대로 남아 있어요. 집합을 다시 리스트로 보고 싶으면 sorted()에 넣어요." + REAL)

# long way: for + add
o = [sec("s-long")] + head(EB1, "set(orders)는 for와 add를 한 줄로 줄인 거예요", K1)
o.append(f'<div style="position:absolute;left:96px;top:220px;display:flex;flex-direction:row;align-items:center;gap:22px">'
         + p(f"font-size:28px;font-weight:700;color:{K1}", "줄여 쓰면") + mono("kinds = set(orders)", 34, K1, K1BG) + '</div>')
o.append(p(f"position:absolute;left:96px;top:320px;font-size:28px;font-weight:700;color:{K1}", "for와 add로 길게 쓰면", at("fade", 1)))
c = {"id": "c-l", "lines": ["kinds = set()", "for o in orders:", "    kinds.add(o)", "print(sorted(kinds))"], "n": 6, "out": ["['cake', 'coffee', 'latte']"]}
CX, CY, CW = 96, 370, 1000
o += cell(c, CX, CY, CW, sel=True, attrs=at("rise", 1))
tx0 = tx(CX, c["lines"])
for i, (t, k) in enumerate([("빈 주머니로 시작", 1), ("주문을 하나씩 꺼내서", 2), ("넣어요. 있으면 그대로", 3)]):
    o.append(run(k, CX + 89, CY + 10 + i * LH(), CW - 93, LH()))
    o.append(tag(tx0, ly(CY, i), t, GR, k))
o.append(run_off(4))
o.append(tag(CX + 105 + tw("['cake', 'coffee', 'latte']") + 34, oy(CY, 4, 0), "set(orders)와 같아요", K1, 4))
o.append(ref_box(96, 690, 1000, ["kinds = []", "for o in orders:", "    if o not in kinds:", "        kinds.append(o)", "print(kinds)"], ["['coffee', 'latte', 'cake']"], "참고 · 집합이 없으면", at("rise", 5), 20))
o.append(bag([], 1180, 240, 644, 600, K1, K1BG, fs=40, name="kinds", empty="", attrs=at("rise", 1)))
for i, (v, px, py) in enumerate([('"coffee"', 0.50, 0.70), ('"latte"', 0.30, 0.36), ('"cake"', 0.70, 0.40)]):
    o.append(f'<div{at("rise", 3)} style="position:absolute;left:{1180 + px * 644:.0f}px;top:{240 + 30 + py * 570:.0f}px;transform:translate(-50%,-50%)">' + chip(v, K1, K1BG, 40) + '</div>')
o.append(p(f"position:absolute;left:1180px;top:880px;width:644px;text-align:center;font-size:28px;font-weight:700;color:{GRAY}", "coffee, latte를 또 넣어도 하나씩", at("rise", 3)))
W("s-long", o, "set(orders) 한 줄은 빈 집합에서 시작해 하나씩 add하는 반복을 줄인 거예요. 빈 집합 kinds에서 시작해 for로 주문을 하나씩 꺼내 add해요. 2파트에서 볼 add는 이미 있는 값이면 아무 일도 하지 않아서, 겹친 주문은 하나만 남아요. 결과는 set(orders)와 같아요. 집합이 없으면 리스트에 담으면서 아직 없을 때만 넣기를 직접 물어야 해요. 그때 쓰는 if는 17에서 배우니 아래 참고 칸은 읽기만 해요. 리스트는 처음 나온 순서를 지켜서 coffee, latte, cake 순서예요. 한 줄짜리 기능의 원래 모양을 알면 결과를 읽기 쉬워요. 왼쪽 셀과 참고 코드 모두 실제로 실행한 결과예요.")

# empty set
o = [sec("s-empty")] + head(EB1, "빈 집합은 {}가 아니라 set()이에요", K1)
c = {"id": "c-e", "lines": ["a = {}", "print(type(a))", "b = set()", "print(type(b))", "print(b)", "print(len(b))"], "n": 7, "out": ["<class 'dict'>", "<class 'set'>", "set()", "0"]}
CX, CY, CW = 96, 220, 900
o += cell(c, CX, CY, CW, sel=True)
ox = tx(CX, ["<class 'dict'>"], out=True)
o.append(tag(ox, oy(CY, 6, 0), "{}는 15의 빈 딕셔너리예요", RED, 1))
o.append(tag(ox, oy(CY, 6, 1), "빈 집합은 set()", GR, 2))
o.append(tag(ox, oy(CY, 6, 2), "찍어도 set()이라고 나와요", GR, 2))
c2 = {"id": "c-e2", "lines": ["cart = {}", 'cart.add("coffee")'], "n": 8, "out": ["AttributeError: 'dict' object has no attribute 'add'"]}
CY2 = CY + cell_h(c) + 30
o += cell(c2, CX, CY2, 1728, attrs=at("rise", 3))
o.append(underline(3, CX + 105, int(CX + 105 + tw("AttributeError: 'dict' object has no attribute 'add'")), int(oy(CY2, 2, 0) + 24), RED, 5))
o.append(fix(96, 960, "cart = {}", "cart = set()", 4, 30, "add는 집합에 있어요"))
o.append(bag([], 1240, 230, 540, 320, K1, K1BG, name="b", empty="set()", attrs=at("rise", 2)))
W("s-empty", o, "빈 중괄호는 집합이 아니라 빈 딕셔너리예요. 딕셔너리가 먼저 중괄호를 쓰고 있었기 때문이에요. type으로 보면 dict라고 나와요. 빈 집합은 set()으로 만들어요. print로 찍어도 {}가 아니라 set()이라고 나와서 딕셔너리와 헷갈리지 않아요. 빈 딕셔너리에 집합처럼 add를 쓰면 딕셔너리에는 add가 없다는 AttributeError가 나요. cart = set()으로 만들면 돼요." + REAL)

# what can go in
o = [sec("s-hash")] + head(EB1, "숫자, 문자열, 튜플은 담고 리스트는 못 담아요", K1)
CX, CW = 96, 1000
c1 = {"id": "c-h1", "lines": ['ok = {1, "kim", (2, 3)}', "print(len(ok))"], "n": 9, "out": ["3"]}
c2 = {"id": "c-h2", "lines": ["bad = {[1, 2], 3}"], "n": 10, "out": ["TypeError: unhashable type: 'list'"]}
c3 = {"id": "c-h3", "lines": ['d = {[1, 2]: "a"}'], "n": 11, "out": ["TypeError: unhashable type: 'list'"]}
y1 = 230
o += cell(c1, CX, y1, CW, sel=True)
y2 = y1 + cell_h(c1) + 40
o += cell(c2, CX, y2, CW, attrs=at("rise", 2))
y3 = y2 + cell_h(c2) + 40
o += cell(c3, CX, y3, CW, attrs=at("rise", 3))
ew = int(tw("TypeError: unhashable type: 'list'"))
o.append(box(2, CX + 95, int(oy(y2, 1, 0) - 30), ew + 24, 60, RED, 5))
o.append(tag(CX + 105 + 40, oy(y3, 1, 0) + 64, "15의 딕셔너리 키도 같은 규칙, 같은 오류예요", K1, 3, 28, lead=False))
o.append(bag(["1", '"kim"', "(2, 3)"], 1190, 300, 600, 380, GR, GRBG, fs=36, name="ok", pos=[(0.26, 0.40), (0.70, 0.36), (0.48, 0.74)], attrs=at("rise", 1)))
o.append(f'<div{at("rise", 2)} style="position:absolute;left:1360px;top:760px;display:flex;flex-direction:row;align-items:center;gap:18px">'
         + chip("[1, 2]", RED, REDBG, 36) + p(f"font-size:30px;font-weight:700;color:{RED};white-space:nowrap", "✕ 못 들어가요") + '</div>')
o.append(tag(1360, 870, "리스트는 append로 바뀔 수 있어서요", RED, 2, 26, lead=False))
W("s-hash", o, "집합에는 바뀌지 않는 값만 넣을 수 있어요. 숫자, 문자열, 튜플을 넣을 수 있고 섞어 넣어도 돼요. 리스트를 넣으면 TypeError가 나요. 리스트는 append로 늘어나거나 값이 바뀔 수 있어서, 주머니가 같은 값인지 확인할 수가 없기 때문이에요. 튜플은 만든 뒤 바뀌지 않아서 넣을 수 있어요. 15의 딕셔너리 키도 같은 규칙이라 리스트를 키로 쓰면 같은 오류가 나요. 오류 끝의 unhashable은 집합이나 키 자리에 넣을 수 없는 값이라는 뜻으로 읽으면 돼요." + REAL)

# ---------- part 2: change and check ----------
o = [sec("s-add")] + head(EB2, "add로 하나 넣어요. 이미 있으면 그대로예요", K2)
c = {"id": "c-a", "lines": [MENUS, 'menus.add("tea")', "print(menus)", 'menus.add("coffee")', "print(menus)", "print(len(menus))"], "n": 1,
     "out": ["{'latte', 'cake', 'coffee', 'tea'}", "{'latte', 'cake', 'coffee', 'tea'}", "4"]}
CX, CY, CW = 96, 220, 960
o += cell(c, CX, CY, CW, sel=True)
o.append(marker("add-src", CX + 105 + tw('menus.add('), ly(CY, 1) - 20, tw('"tea"'), 40))
o.append(hl(CX, CY, CW, 1, 1, "run", 1))
o.append(hl(CX, CY, CW, 3, 1, "skip", 2))
o.append(tag(tx(CX, ['menus.add("coffee")']), ly(CY, 3), "이미 있어서 아무 일도 없어요", GRAY, 2))
o.append(tag(CX + 105 + tw("4") + 34, oy(CY, 6, 2), "4개 그대로", K2, 2))
PB = (1130, 240, 694, 640)
o.append(bag(['"latte"', '"cake"', '"coffee"', '"tea"'], *PB, K2, K2BG, fs=40, name="menus", pos=[(0.27, 0.32), (0.70, 0.28), (0.34, 0.70), (0.74, 0.64)],
             chip_attrs={3: ' data-build-in="fly order 1" data-from="add-src"'}))
o.append(ring(2, PB[0] + int(0.34 * PB[2]) - 100, PB[1] + 30 + int(0.70 * (PB[3] - 30)) - 32, 200, 64, GRAY, 4))
o.append(p(f"position:absolute;left:96px;top:760px;width:960px;font-size:30px;font-weight:700;line-height:1.55;color:{SUB}", "리스트는 append로 맨 뒤에 붙이지만,<br>집합은 자리가 없어서 그냥 넣어요.", at("rise", 3)))
W("s-add", o, "집합에 값을 하나 넣을 때는 add를 써요. tea가 들어가서 네 개가 됐어요. 이미 있는 coffee를 한 번 더 add하면 아무것도 바뀌지 않아요. 오류도 나지 않아요. 13의 리스트는 append로 맨 뒤에 붙였지만, 집합은 순서가 없어서 맨 뒤라는 자리가 없어요. 이 파트는 새 커널이라 menus를 다시 만들고 셀 번호가 [1]부터예요." + REAL, ("change", "바꾸고 확인하기"))

o = [sec("s-remove")] + head(EB2, "remove는 없으면 오류, discard는 괜찮아요", K2)
CX, CW = 96, 1000
c1 = {"id": "c-r1", "lines": ['menus.remove("latte")', "print(menus)"], "n": 2, "out": ["{'cake', 'coffee', 'tea'}"]}
c2 = {"id": "c-r2", "lines": ['menus.remove("juice")'], "n": 3, "out": ["KeyError: 'juice'"]}
c3 = {"id": "c-r3", "lines": ['menus.discard("juice")', 'menus.discard("tea")', "print(menus)"], "n": 4, "out": ["{'cake', 'coffee'}"]}
y1 = 220
o += cell(c1, CX, y1, CW, sel=True)
y2 = y1 + cell_h(c1) + 30
o += cell(c2, CX, y2, CW, attrs=at("rise", 1))
y3 = y2 + cell_h(c2) + 30
o += cell(c3, CX, y3, CW, attrs=at("rise", 2))
T = tx(CX, ['menus.discard("juice")'])
o.append(tag(T, ly(y1, 0), "있는 값을 빼요", K2))
o.append(ring(1, CX + 105, int(oy(y2, 1, 0) - 22), int(tw("KeyError: 'juice'")), 44, RED, 5))
o.append(tag(CX + 105 + tw("KeyError: 'juice'") + 60, oy(y2, 1, 0), "없는 값이면 셀이 멈춰요", RED, 1))
o.append(shake(1, "c-r2"))
o.append(hl(CX, y3, CW, 0, 1, "skip", 2))
o.append(tag(T, ly(y3, 0), "없으면 그냥 넘어가요", GRAY, 2))
o.append(hl(CX, y3, CW, 1, 1, "run", 2))
o.append(tag(T, ly(y3, 1), "있으면 빼요", GR, 2))
o.append(f'<div{at("rise", 3)} style="position:absolute;left:1150px;top:770px;width:674px;border:3px dashed #B4B9C3;border-radius:18px;padding:16px 24px;display:flex;flex-direction:column;gap:6px">'
         + p(f"font-size:22px;font-weight:700;color:{GRAY}", "참고 · discard를 길게 쓰면 (if는 17에서 배워요)")
         + p(f"font-family:{MONO};font-size:24px;line-height:1.45;white-space:pre;color:{SUB}", e('if "juice" in menus:')) + p(f"font-family:{MONO};font-size:24px;line-height:1.45;white-space:pre;color:{SUB}", e('    menus.remove("juice")')) + '</div>')
o.append(bag(['"cake"', '"coffee"'], 1180, 220, 644, 420, K2, K2BG, fs=36, name="menus", pos=[(0.32, 0.46), (0.68, 0.62)]))
for i, (v, k, x_) in enumerate([('"latte"', 0, 1220), ('"tea"', 2, 1500)]):
    o.append(f'<div{at("rise", k) if k else ""} style="position:absolute;left:{x_}px;top:670px">' + chip(v, GRAY, GRAYBG, 32, "border-style:dashed;text-decoration:line-through") + '</div>')
o.append(caption("15의 menu[키]와 get()처럼, remove와 discard도 짝이에요.", 960, 3))
W("s-remove", o, "값을 빼는 방법은 두 가지예요. 없는 값을 빼면 remove는 멈추고 discard는 넘어가요. remove는 latte처럼 있는 값을 빼요. 없는 juice를 remove하면 KeyError가 나고 셀이 멈춰요. discard는 있으면 빼고 없으면 아무 일도 하지 않아요. juice는 없어서 그냥 넘어갔고, tea는 있어서 빠졌어요. 15에서 menu[\"tea\"]는 없으면 오류, menu.get(\"tea\")는 오류 없이 넘어갔던 것과 같은 관계예요. 오른쪽 아래 참고 칸은 discard가 줄여 준 원래 코드예요. if는 아직 배우지 않았으니 읽기만 해요." + REAL)

o = [sec("s-update")] + head(EB2, "update로 여러 개를 한 번에 넣어요", K2)
c = {"id": "c-u", "lines": ['menus.update(["juice", "tea", "coffee"])', "print(menus)", "print(len(menus))"], "n": 5, "out": ["{'tea', 'cake', 'coffee', 'juice'}", "4"]}
CX, CY, CW = 96, 220, 1000
o += cell(c, CX, CY, CW, sel=True)
base = CX + 105 + tw('menus.update([')
o.append(marker("up-j", base, ly(CY, 0) - 20, tw('"juice"'), 40))
o.append(marker("up-t", base + tw('"juice", '), ly(CY, 0) - 20, tw('"tea"'), 40))
o.append(hl(CX, CY, CW, 0, 1, "run", 1))
o.append(tag(CX + 105 + tw("4") + 34, oy(CY, 3, 1), "2개 + 3개인데 4개예요", K2, 2))
o.append(p(f"position:absolute;left:96px;top:620px;width:960px;font-size:30px;font-weight:700;line-height:1.5;color:{SUB}", "add는 값 하나, update는 리스트 안의 값을 모두 넣어요.<br>13의 리스트 extend와 비슷해요.", at("rise", 3)))
o.append(bag(['"cake"', '"coffee"', '"juice"', '"tea"'], 1150, 260, 680, 460, K2, K2BG, fs=34, name="menus", pos=[(0.28, 0.34), (0.68, 0.30), (0.34, 0.72), (0.74, 0.68)],
             chip_attrs={2: ' data-build-in="fly order 1" data-from="up-j"', 3: ' data-build-in="fly order 1" data-from="up-t"'}))
o.append(f'<div{at("rise", 2)} style="position:absolute;left:1260px;top:790px;display:flex;flex-direction:row;align-items:center;gap:18px">'
         + chip('"coffee"', GRAY, GRAYBG, 30, "text-decoration:line-through") + p(f"font-size:28px;font-weight:700;color:{GRAY};white-space:nowrap", "이미 있어서 그대로") + '</div>')
W("s-update", o, "값 여러 개를 한 번에 넣을 때는 update를 써요. 괄호 안에 리스트를 넣으면 리스트의 값이 하나씩 주머니에 들어가요. 앞에서 남은 cake, coffee에 juice와 tea가 들어갔어요. coffee는 이미 있어서 그대로예요. 그래서 개수가 5가 아니라 4예요. 13에서 리스트 두 개를 이은 extend와 비슷하지만, 겹친 값은 하나만 남는다는 점이 달라요." + REAL)

o = [sec("s-pop")] + head(EB2, "집합의 pop은 아무거나 하나 빼요", K2)
CX, CW = 96, 1000
c1 = {"id": "c-p", "lines": ["one = menus.pop()", "print(one)", "print(menus)", "nums = [10, 20, 30]", "print(nums.pop())"], "n": 6, "out": ["tea", "{'cake', 'coffee', 'juice'}", "30"]}
c2 = {"id": "c-p2", "lines": ["menus.clear()", "print(menus)", "print(len(menus))"], "n": 7, "out": ["set()", "0"]}
y1 = 220
o += cell(c1, CX, y1, CW, sel=True)
y2 = y1 + cell_h(c1) + 30
o += cell(c2, CX, y2, CW, attrs=at("rise", 3))
o.append(hlo(CX, y1, CW, 5, 0, "note", 1, tw("tea") + 30))
o.append(tag(CX + 105 + tw("tea") + 40, oy(y1, 5, 0), "어느 값이 나올지 정해져 있지 않아요", OR, 1))
o.append(tag(CX + 105 + tw("30") + 40, oy(y1, 5, 2), "리스트 pop은 맨 뒤를 빼요", GRAY, 2))
o.append(tag(tx(CX, ["menus.clear()"]), ly(y2, 0), "모두 비워요. 빈 주머니가 남아요", K2, 3))
o.append(bag(['"cake"', '"coffee"', '"juice"'], 1150, 260, 660, 400, K2, K2BG, fs=32, name="menus", pos=[(0.28, 0.38), (0.70, 0.34), (0.48, 0.72)]))
o.append(f'<div id="pop-one" style="position:absolute;left:1300px;top:740px;width:360px;height:130px;border:3px solid {K2};border-radius:18px;background:{CARD};display:flex;flex-direction:row;align-items:center;gap:20px;padding:0 26px">'
         + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{K2}", "one") + f'<div{at("fly", 1)} data-from="menus-pop-src">' + chip('"tea"', K2, K2BG, 32) + '</div></div>')
o.append(marker("menus-pop-src", 1150 + 330 - 50, 260 + 200, 100, 40))
W("s-pop", o, "집합에도 pop이 있지만, 순서가 없어서 어느 값이 나올지 정해져 있지 않아요. 이번에는 tea가 나왔지만 수강생 화면에서는 다른 값이 나올 수 있어요. 13의 리스트 pop은 맨 뒤 값을 꺼냈어요. 집합에서 원하는 값을 빼려면 앞 장의 remove나 discard를 써요. clear는 값을 모두 비워요. 주머니는 그대로 남아서 set()으로 찍혀요. 출력은 실제로 실행한 결과이고, pop의 결과는 실행할 때마다 다를 수 있어요.")

o = [sec("s-in")] + head(EB2, "in으로 들어 있는지 물어요", K2)
CF[0] = 34
c = {"id": "c-i", "lines": [MENUS, 'print("latte" in menus)', 'print("tea" in menus)', 'print("tea" not in menus)'], "n": 8, "out": ["True", "False", "True"]}
CX, CY, CW = 96, 220, 1000
o += cell(c, CX, CY, CW, sel=True)
ox = CX + 105 + tw("False") + 40
for j, (t, col, k) in enumerate([("latte가 주머니에 있어요", GR, 1), ("tea는 없어요", RED, 2), ("없는 게 맞아요", GR, 3)]):
    o.append(hlo(CX, CY, CW, 4, j, "run" if col == GR else "err", k, tw("False") + 30))
    o.append(tag(ox, oy(CY, 4, j), t, col, k))
CF[0] = 30
o.append(p(f"position:absolute;left:96px;top:720px;width:1000px;font-size:30px;font-weight:700;line-height:1.5;color:{SUB}", "14에서 리스트, 튜플, 문자열에 쓴 in 그대로예요.<br>집합은 꺼내기보다 들어 있는지 묻는 데 써요.", at("rise", 4)))
o.append(bag(['"latte"', '"cake"', '"coffee"'], 1150, 260, 660, 420, K2, K2BG, fs=34, name="menus", pos=[(0.28, 0.38), (0.70, 0.34), (0.48, 0.72)], chip_attrs={0: ' id="in-latte"'}))
o.append(pulse(1, "in-latte"))
o.append(ring(1, 1150 + int(0.28 * 660) - 85, 260 + 30 + int(0.38 * 390) - 30, 170, 60, GR, 5))
o.append(f'<div{at("rise", 2)} style="position:absolute;left:1380px;top:760px">' + chip('"tea"', GRAY, GRAYBG, 32, "border-style:dashed") + '</div>')
o.append(tag(1380 + 150, 790, "밖에 있어요", GRAY, 2, 28))
W("s-in", o, "in과 not in으로 집합에 값이 들어 있는지 물어요. 14에서 리스트, 튜플, 문자열에 쓴 그대로예요. latte는 들어 있어서 True, tea는 없어서 False예요. not in은 반대로 물어요. 집합은 번호로 꺼낼 수 없어서, 값이 있는지 묻는 게 주로 하는 일이에요. 17에서 배울 if와 함께 쓰면 있는 메뉴만 계산하는 코드를 만들어요. 앞 장에서 clear로 비운 menus를 이 셀에서 다시 만들었어요." + REAL)

o = [sec("s-noindex")] + head(EB2, "번호로 못 꺼내요. 필요하면 sorted()로 바꿔요", K2)
CX, CW = 96, 1100
c1 = {"id": "c-n1", "lines": ["menus[0]"], "n": 9, "out": ["TypeError: 'set' object is not subscriptable"]}
c2 = {"id": "c-n2", "lines": ["print(sorted(menus))", "print(sorted(menus)[0])", "print(list(menus))"], "n": 10, "out": ["['cake', 'coffee', 'latte']", "cake", "['latte', 'cake', 'coffee']"]}
y1 = 220
o += cell(c1, CX, y1, CW, sel=True)
o.append(underline(1, CX + 105, int(CX + 105 + tw("TypeError: 'set' object is not subscriptable")), int(oy(y1, 1, 0) + 20), RED, 5))
o.append(tag(tx(CX, ["menus[0]"]), ly(y1, 0), "주머니에는 칸 번호가 없어요", RED, 1))
y2 = y1 + cell_h(c1) + 40
o += cell(c2, CX, y2, CW, attrs=at("rise", 2))
o.append(hlo(CX, y2, CW, 3, 1, "run", 2, tw("cake") + 30))
o.append(tag(CX + 105 + tw("cake") + 40, oy(y2, 3, 1), "abc 순서 리스트라 [0]은 늘 cake", GR, 2))
o.append(tag(CX + 105 + tw("['latte', 'cake', 'coffee']") + 40, oy(y2, 3, 2), "list()는 순서가 정해져 있지 않아요", OR, 3))
MS = f"position:absolute;left:96px;top:850px;font-family:{MONO};font-size:44px;font-weight:700;line-height:1.4;white-space:pre"
o.append(p(MS + f";color:{RED}", tok("m", "menus") + tok("i", "[0]"), ' id="ni-a"' + at("fade", 3) + MORPH_FROM()))
o.append(p(MS + f";color:{GR}", "sorted(" + tok("m", "menus") + ")" + tok("i", "[0]"), MORPH(4, "ni-a")))
o.append(p(f"position:absolute;left:{96 + int(tw('sorted(menus)[0]') * 44 / 30) + 50}px;top:866px;font-size:30px;font-weight:700;color:{SUB};white-space:nowrap", "15의 list(menu.keys())처럼 리스트로 바꿔요", at("fade", 4)))
W("s-noindex", o, "집합에는 칸 번호가 없어서 menus[0]처럼 꺼내면 TypeError가 나요. subscriptable은 대괄호로 꺼낼 수 있다는 뜻이에요. 꼭 번호로 꺼내야 하면 리스트로 바꿔요. sorted()는 abc 순서로 줄 세운 리스트를 줘서 [0]이 늘 cake예요. list()도 리스트를 주지만 집합이 찍히던 순서를 그대로 따라서 실행할 때마다 다를 수 있어요. 15에서 keys()에 번호를 붙이려고 list()로 바꾼 것과 같은 방법이에요." + REAL)

o = [sec("s-sort")] + head(EB2, "집합에는 sort()가 없어요. sorted()를 써요", K2)
CF[0] = 26
CX, CW = 96, 1000
c1 = {"id": "c-so1", "lines": ["menus.sort()"], "n": 11, "out": ["AttributeError: 'set' object has no attribute 'sort'"]}
c2 = {"id": "c-so2", "lines": ["nums = {30, 10, 20}", "print(sorted(nums))", "print(sorted(nums, reverse=True))", "print(sorted(menus, reverse=True))", "print(type(sorted(menus)))", "print(menus)"], "n": 12,
      "out": ["[10, 20, 30]", "[30, 20, 10]", "['latte', 'coffee', 'cake']", "<class 'list'>", "{'latte', 'cake', 'coffee'}"]}
c3 = {"id": "c-so3", "lines": ['orders = ["tea", "cake", "tea",', '          "coffee", "cake"]', "print(sorted(set(orders)))"], "n": 13, "out": ["['cake', 'coffee', 'tea']"]}
y1 = 220
o += cell(c1, CX, y1, CW, sel=True)
o.append(underline(1, CX + 105, int(CX + 105 + tw("AttributeError: 'set' object has no attribute 'sort'")), int(oy(y1, 1, 0) + 20), RED, 5))
o.append(tag(tx(CX, ["menus.sort()"]), ly(y1, 0), "sort()는 리스트에만 있어요", RED, 1, 26))
y2 = y1 + cell_h(c1) + 28
o += cell(c2, CX, y2, CW, attrs=at("rise", 2))
OX = CX + 105 + tw("['latte', 'coffee', 'cake']") + 34
o.append(tag(CX + 105 + tw("[10, 20, 30]") + 34, oy(y2, 6, 0), "작은 것부터", GR, 2, 26))
o.append(tag(CX + 105 + tw("[30, 20, 10]") + 34, oy(y2, 6, 1), "reverse=True면 큰 것부터", GR, 2, 26))
o.append(tag(CX + 105 + tw("<class 'list'>") + 34, oy(y2, 6, 3), "결과는 새 리스트", GR, 2, 26))
o.append(tag(OX + 40, oy(y2, 6, 4), "menus는 그대로 집합", K2, 2, 26))
o.append(p(f"position:absolute;left:1150px;top:220px;font-size:26px;font-weight:700;color:{K2}", "가장 많이 쓰는 모양", at("fade", 3)))
o += cell(c3, 1150, 266, 674, attrs=at("rise", 3))
o.append(hl(1150, 266, 674, 2, 1, "run", 3))
o.append(zoom(4, 1140, 210, 700, 220, 30))
o.append(zoom_off(5))
CF[0] = 30
o.append(p(f"position:absolute;left:1150px;top:540px;width:674px;font-size:28px;font-weight:700;line-height:1.5;color:{SUB}", "겹친 주문을 없애고<br>abc 순서로 줄 세운 목록이<br>한 줄에 나와요", at("rise", 3)))
W("s-sort", o, "집합에는 sort()가 없어서 sorted()로 줄 세운 새 리스트를 받아요. 13에서 리스트는 sort()로 제자리 정렬을 했어요. 집합에 sort()를 쓰면 AttributeError가 나요. 집합에는 자리가 없어서 자리를 바꿔 줄 세우는 sort()가 없기 때문이에요. sorted()는 집합을 그대로 두고, 줄 세운 새 리스트를 돌려줘요. 13에서 본 reverse=True를 넣으면 큰 것부터, 글자는 z 쪽부터예요. type으로 보면 결과는 list이고, menus는 여전히 집합이에요. 실제로 가장 많이 쓰는 모양은 sorted(set(orders))예요." + REAL)

o = [sec("s-for")] + head(EB2, "for로 하나씩 꺼낼 수 있어요", K2)
c1 = {"id": "c-f1", "lines": ["for m in menus:", "    print(m)"], "n": 14, "out": ["latte", "cake", "coffee"]}
c2 = {"id": "c-f2", "lines": ["for m in sorted(menus):", "    print(m)"], "n": 15, "out": ["cake", "coffee", "latte"]}
CF[0] = 40
o += cell(c1, 96, 230, 820, sel=True)
o += cell(c2, 1004, 230, 820, attrs=at("rise", 2))
o.append(tag(96 + 105 + tw("coffee") + 40, oy(230, 2, 1), "순서는 정해져 있지 않아요", OR, 1, 28))
o.append(hl(1004, 230, 820, 0, 1, "run", 2))
o.append(tag(1004 + 105 + tw("coffee") + 40, oy(230, 2, 1), "abc 순서", GR, 2, 28))
CF[0] = 30
o.append(f'<div{at("rise", 3)} style="position:absolute;left:96px;top:700px;width:1728px;display:flex;flex-direction:row;align-items:center;gap:26px;border-top:2px solid {LINE};padding-top:40px">'
         + mono("for 이름 in 집합:", 34, K2, K2BG) + p(f"font-size:30px;font-weight:700;color:{INK}", "13의 리스트 for와 같은 모양이에요. 값마다 한 번씩 돌아요.") + '</div>')
W("s-for", o, "집합도 13의 리스트처럼 for로 하나씩 꺼낼 수 있어요. 집합을 그대로 넣으면 값마다 한 번씩 돌지만 순서는 정해져 있지 않아요. 왼쪽 결과는 print(menus)가 찍히던 순서와 같아요. 개수 세기나 합계처럼 순서가 상관없는 일에는 그대로 써요. 화면에 찍을 때는 sorted(menus)를 넣어서 언제 실행해도 같은 결과가 나오게 해요. 5파트 실습도 이렇게 해요." + REAL)

# ---------- part 3: set operations ----------
A_, B_ = "a = {1, 2, 3, 4}", "b = {3, 4, 5, 6}"
VX, VY, VW, VH = 96, 290, 900, 560
o = [sec("s-venn", "magic")] + head(EB3, "두 집합을 원 두 개로 그려요", K3)
o.append(f'<div id="ab-code" style="position:absolute;left:96px;top:206px;display:flex;flex-direction:row;gap:20px">' + mono(A_, 32, VA, K1BG) + mono(B_, 32, VB, K2BG) + '</div>')
o.append(venn(VX, VY, ["1", "2"], ["3", "4"], ["5", "6"], w=VW, h=VH, sid="vn-ab", fs=46,
              hi=[("a-b", VA, 1), ("inter", K3, 2), ("b-a", VB, 3)]))
for i, (t, c_) in enumerate([("a에만 있는 값  1, 2", VA), ("a와 b에 다 있는 값  3, 4", K3), ("b에만 있는 값  5, 6", VB)]):
    o.append(p(f"position:absolute;left:1100px;top:{400 + i * 120}px;font-size:34px;font-weight:700;color:{c_};white-space:nowrap", e(t), at("rise", i + 1) + DELAY(250)))
o.append(caption("이 그림을 벤 다이어그램이라고 불러요.", 960, 4))
W("s-venn", o, "원 하나가 집합 하나예요. 겹친 곳에는 두 집합에 다 있는 값이 들어가요. a는 1부터 4, b는 3부터 6이에요. 3과 4는 두 집합에 다 있어서 원이 겹친 곳에 그려요. 1과 2는 a에만, 5와 6은 b에만 있어요. 이 파트는 이 그림 하나에 색을 칠하면서 세 가지 연산을 봐요. 숫자로 시작하는 이유는 작은 정수 집합이 보통 작은 수부터 찍혀서 읽기 쉽기 때문이에요.", ("ops", "집합 연산"))


def op_slide(sid, title, hi, c, mode_lines, notes, code_tag, extra=None):
    o = [sec(sid, "magic")] + head(EB3, title, K3)
    o.append(f'<div id="ab-code" style="position:absolute;left:96px;top:206px;display:flex;flex-direction:row;gap:20px">' + mono(A_, 32, VA, K1BG) + mono(B_, 32, VB, K2BG) + '</div>')
    o.append(venn(VX, VY, ["1", "2"], ["3", "4"], ["5", "6"], w=VW, h=VH, sid="vn-ab", fs=46, hi=hi))
    CX, CY, CW = 1060, 290, 764
    o += cell(c, CX, CY, CW, sel=True, attrs=at("rise", 2))
    for j, t, col in mode_lines:
        o.append(tag(CX + 105 + tw(c["out"][j]) + 30, oy(CY, len(c["lines"]), j), t, col, 3, 28))
    o.append(f'<div{at("rise", 4)} style="position:absolute;left:{CX + 20}px;top:{CY + cell_h(c) + 70}px;display:flex;flex-direction:row;align-items:center;gap:18px">'
             + mono(code_tag[0], 38, K3, K3BG) + p(f"font-size:28px;color:{GRAY}", "또는") + mono(code_tag[1], 30, K3, K3BG) + '</div>')
    if extra:
        o += extra(CX, CY + cell_h(c) + 170)
    W(sid, o, notes)


op_slide("s-union", "합집합 | 은 어느 쪽이든 있는 값이에요", [("union", K3, 1)],
         {"id": "c-u1", "lines": [A_, B_, "print(a | b)", "print(a.union(b))"], "n": 1, "out": ["{1, 2, 3, 4, 5, 6}", "{1, 2, 3, 4, 5, 6}"]},
         [(0, "겹친 3, 4는 하나씩", K3)],
         "합집합은 두 집합 중 어느 쪽에든 있는 값을 모두 모은 거예요. 파이썬에서는 세로줄 | 로 써요. 두 원 전체를 칠한 것과 같아요. 겹친 3과 4는 한 번씩만 들어가서 값은 6개예요. 같은 일을 a.union(b)처럼 메서드 이름으로도 쓸 수 있어요. 기호가 헷갈리면 이름으로 적어도 결과는 같아요. 세로줄은 보통 키보드 Enter 위, 원화 기호나 역슬래시 키에 Shift와 함께 있어요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL,
         ("a | b", "a.union(b)"),
         lambda x, y: [p(f"position:absolute;left:{x + 20}px;top:{y}px;width:760px;font-size:28px;line-height:1.5;color:{SUB}", "| 는 세로줄이에요. 보통 Enter 위 키를 Shift와 함께 눌러요.", at("rise", 4))])
op_slide("s-inter", "교집합 & 는 둘 다 있는 값이에요", [("inter", K3, 1)],
         {"id": "c-i1", "lines": ["print(a & b)", "print(a.intersection(b))"], "n": 2, "out": ["{3, 4}", "{3, 4}"]},
         [(0, "겹친 곳만", K3)],
         "교집합은 두 집합에 모두 있는 값이에요. 앰퍼샌드 & 로 써요. 원이 겹친 곳만 칠한 것과 같아요. a와 b에 다 있는 값은 3과 4예요. 메서드 이름은 intersection이에요. 영어로 교차로라는 뜻이라, 두 길이 만나는 곳이라고 기억해요. 겹치는 사람, 겹치는 메뉴를 찾을 때 써요. 앞 셀에서 만든 a와 b를 그대로 써서 셀 번호가 [2]예요." + REAL,
         ("a & b", "a.intersection(b)"),
         lambda x, y: [p(f"position:absolute;left:{x + 20}px;top:{y}px;width:760px;font-size:28px;line-height:1.5;color:{SUB}", "겹치는 사람, 겹치는 메뉴를 찾을 때 써요.", at("rise", 4))])
op_slide("s-diff", "차집합 - 는 앞에만 있는 값이에요", [("a-b", VA, 1), ("b-a", VB, 3)],
         {"id": "c-d1", "lines": ["print(a - b)", "print(b - a)", "print(a.difference(b))"], "n": 3, "out": ["{1, 2}", "{5, 6}", "{1, 2}"]},
         [(0, "a에서 b에 있는 걸 빼요", VA), (1, "앞뒤를 바꾸면 결과도 달라요", VB)],
         "차집합은 앞 집합에서 뒤 집합에 있는 값을 뺀 거예요. 빼기 기호 - 로 써요. a - b는 a에서 3과 4를 빼서 1, 2만 남아요. 숫자 빼기처럼 앞뒤를 바꾸면 결과가 달라요. b - a는 b에서 3과 4를 빼서 5, 6이에요. 그림에서는 앞에 적은 원에서 겹친 곳을 뺀 부분만 칠해요. 메서드 이름은 difference예요." + REAL,
         ("a - b", "a.difference(b)"))

o = [sec("s-ops")] + head(EB3, "세 연산을 한 장에 모아요", K3)
ops3 = [("a | b", "a.union(b)", "{1, 2, 3, 4, 5, 6}", "어느 쪽이든", [("union", K3, 0)]),
        ("a & b", "a.intersection(b)", "{3, 4}", "둘 다", [("inter", K3, 0)]),
        ("a - b", "a.difference(b)", "{1, 2}", "a에만", [("a-b", K3, 0)])]
for i, (code, meth, res, d, hi_) in enumerate(ops3):
    x = 96 + i * 590
    o.append(f'<div id="op{i}" style="position:absolute;left:{x}px;top:200px;width:560px;height:440px"></div>')
    o.append(venn(x + 30, 200, ["1", "2"], ["3", "4"], ["5", "6"], w=500, h=280, fs=28, hi=hi_))
    o.append(f'<div style="position:absolute;left:{x + 40}px;top:500px;width:500px;display:flex;flex-direction:column;gap:10px">'
             + '<div style="display:flex;flex-direction:row;align-items:center;gap:16px">' + mono(code, 34, K3, K3BG) + p(f"font-size:30px;font-weight:700;color:{INK}", d) + '</div>'
             + p(f"font-family:{MONO};font-size:24px;color:{SUB}", e(meth)) + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{INK}", e(res)) + '</div>')
    o.append(spot(i + 1, target=f"op{i}", pad=6, r="22"))
o.append(spot_off(4))
c = {"id": "c-o", "lines": ["c = a | b", "print(a, b)", "print(len(c), len(a & b))"], "n": 4, "out": ["{1, 2, 3, 4} {3, 4, 5, 6}", "6 2"]}
o += cell(c, 96, 690, 1100, sel=True, attrs=at("rise", 4))
o.append(tag(96 + 105 + tw("{1, 2, 3, 4} {3, 4, 5, 6}") + 34, oy(690, 3, 0), "연산을 해도 a, b는 그대로예요", K3, 4))
o.append(tag(96 + 105 + tw("6 2") + 34, oy(690, 3, 1), "결과는 c처럼 변수에 담아요", K3, 4))
W("s-ops", o, "세 연산을 나란히 놓았어요. 어느 쪽이든 있으면 |, 둘 다 있으면 &, 앞에만 있으면 - 예요. 기호 대신 union, intersection, difference라는 이름으로 써도 같아요. 연산을 해도 a와 b는 바뀌지 않아요. 결과는 새 집합이라 c = a | b처럼 변수에 담아서 써요. len(c)는 6, 겹치는 값의 개수 len(a & b)는 2예요. 대칭차집합 ^, 부분집합 issubset, frozenset은 이번 챕터에서 다루지 않아요." + REAL)

o = [sec("s-long2")] + head(EB3, "연산 기호도 for를 줄인 거예요", K3)
o.append(f'<div style="position:absolute;left:96px;top:220px;display:flex;flex-direction:row;align-items:center;gap:18px">' + mono("a | b", 34, K3, K3BG) + p(f"font-size:28px;font-weight:700;color:{INK}", "를 for와 add로 길게 쓰면") + '</div>')
c = {"id": "c-l2", "lines": ["c = set(a)", "for x in b:", "    c.add(x)", "print(c)"], "n": 5, "out": ["{1, 2, 3, 4, 5, 6}"]}
CX, CY, CW = 96, 310, 960
o += cell(c, CX, CY, CW, sel=True)
T = tx(CX, c["lines"])
for i, (t, k) in enumerate([("a를 복사해 담고", 1), ("b를 하나씩 꺼내서", 2), ("넣어요. 겹친 3, 4는 그대로", 3)]):
    o.append(lspot(k, CX + 87, CY + 2, CW - 89, 16 + 4 * LH(), CY + 10 + i * LH(), LH()))
    o.append(tag(T, ly(CY, i), t, GR, k, 26))
o.append(lspot_off(4))
o.append(p(f"position:absolute;left:96px;top:660px;width:960px;font-size:30px;font-weight:700;line-height:1.55;color:{SUB}", "& 와 - 는 b에 있는지 물어서 담을지 정해요.<br>그때 if가 필요해서 오른쪽은 읽기만 해요.", at("rise", 4)))
o.append(ref_box(1150, 200, 674, ["both = set()", "for x in a:", "    if x in b:", "        both.add(x)", "print(both)"], ["{3, 4}"], "참고 · a & b", at("rise", 4), 22))
o.append(ref_box(1150, 560, 674, ["only_a = set()", "for x in a:", "    if x not in b:", "        only_a.add(x)", "print(only_a)"], ["{1, 2}"], "참고 · a - b", at("rise", 4) + DELAY(300), 22))
o.append(caption("실제로 쓸 때는 기호 한 줄로 적어요.", 960, 5))
W("s-long2", o, "연산 기호 하나는 for로 하나씩 담는 반복을 줄인 거예요. 합집합은 a를 그대로 담은 새 집합에 b의 값을 하나씩 add하면 돼요. 이건 지금까지 배운 것만으로 쓸 수 있어서 셀로 실행해요. 교집합과 차집합은 b에 있는지, 없는지 물어서 담을지 정해야 해서 if가 필요해요. if는 17에서 배우니 오른쪽 두 칸은 읽기만 해요. 결과는 각각 {3, 4}, {1, 2}로 & 와 - 결과와 같아요. 긴 코드는 기호가 무슨 일을 하는지 이해하는 데 써요." + REAL)

# ---------- part 4: compare and errors ----------
o = [sec("x-choose")] + head(EB4, "무엇에 담을지 이렇게 골라요", K5)
mc = lambda s: f"<code style=\"font-family:'JetBrains Mono'\">{e(s)}</code>"
rows4 = [["리스트", mc("[ ]"), "순서대로 쌓고 번호로 꺼낼 때", "하루 주문 orders"],
         ["튜플", mc("( )"), "바뀌지 않는 묶음", "(메뉴, 가격, 수량) 한 줄"],
         ["딕셔너리", mc("{키: 값}"), "이름으로 값을 찾을 때", "메뉴판 menu"],
         ["집합", mc("{값}"), "중복 없애기, 있는지 묻기, 겹침 찾기", "팔린 메뉴 종류, 두 반 명단"]]
o += rows_table(96, 230, [240, 260, 700, 456], rows4, head_=["그릇", "모양", "언제", "예"], rh=130, fs=34, ids=["ch0", "ch1", "ch2", "ch3"], fonts=["sans", "sans", "sans", "small"], colors=[INK, SUB, INK, SUB])
o.append(spot(1, target="ch3", pad=10, r="16"))
o.append(spot_off(2))
o.append(caption("섞어 써도 돼요. 5파트에서는 주문을 리스트로 쌓고, 비교할 때만 집합으로 바꿔요.", 900, 2))
W("x-choose", o, "지금까지 배운 네 그릇은 하는 일로 골라요. 순서가 중요하고 같은 값이 여러 번 나와도 되면 리스트예요. 바뀌지 않는 한 묶음은 튜플이에요. 이름으로 값을 찾으면 딕셔너리예요. 중복을 없애거나, 들어 있는지 묻거나, 두 목록에서 겹치는 것을 찾으면 집합이에요. 실제로는 섞어 써요. 5파트 실습에서 주문은 리스트로 쌓고, 비교할 때만 집합으로 바꾸고, 가격은 딕셔너리에서 찾아요.", ("trouble", "비교와 오류"))

o = [sec("s-str")] + head(EB4, "set(\"banana\")는 글자로 쪼개져요", K5)
c = {"id": "c-s", "lines": ['print(set("banana"))', 'print(len(set("banana")))', 'print(set(["banana"]))', 'print({"banana"})'], "n": 1, "out": ["{'b', 'a', 'n'}", "3", "{'banana'}", "{'banana'}"]}
CX, CY, CW = 96, 220, 900
o += cell(c, CX, CY, CW, sel=True)
o.append(ring(1, CX + 105, int(oy(CY, 4, 0) - 22), int(tw("{'b', 'a', 'n'}")), 44, RED, 5))
o.append(tag(CX + 105 + tw("{'b', 'a', 'n'}") + 60, oy(CY, 4, 0), "단어가 아니라 글자가 들어갔어요", RED, 1))
o.append(hlo(CX, CY, CW, 4, 2, "run", 3, tw("{'banana'}") + 30))
o.append(hlo(CX, CY, CW, 4, 3, "run", 3, tw("{'banana'}") + 30))
o.append(tag(CX + 105 + tw("{'banana'}") + 40, oy(CY, 4, 2) + 32, "리스트로 감싸거나 중괄호에 바로 적어요", GR, 3))
lx = 1060
o.append(slots(list("banana"), lx, 230, 92, 84, fs=34, ids=[f"bn{i}" for i in range(6)]))
o.append(bag(["'b'", "'a'", "'n'"], lx, 420, 440, 330, RED, REDBG, fs=32, pos=[(0.28, 0.38), (0.72, 0.42), (0.50, 0.74)],
             chip_attrs={0: ' data-build-in="fly order 1" data-from="bn0"', 1: ' data-build-in="fly order 1" data-from="bn1"', 2: ' data-build-in="fly order 1" data-from="bn2"'}))
o.append(bag(["'banana'"], 1534, 470, 290, 280, GR, GRBG, fs=28, pos=[(0.5, 0.56)], attrs=at("rise", 3)))
o.append(caption("13에서 문자열도 번호로 한 글자씩 꺼냈어요. 그래서 글자마다 하나씩 들어가요.", 960, 2))
W("s-str", o, "set() 괄호 안에 문자열을 바로 넣으면 단어 하나가 아니라 글자가 들어가요. 13에서 문자열도 리스트처럼 번호로 한 글자씩 꺼냈던 것과 같은 이유예요. banana에서 a와 n이 겹쳐서 b, a, n 세 글자만 남아요. 오류가 나지 않아서 더 헷갈려요. 단어를 통째로 하나 담고 싶으면 중괄호에 바로 적거나, 리스트로 감싼 뒤 set()에 넣어요. 1파트의 set(orders)는 리스트를 넣어서 단어가 그대로 들어갔어요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL)

o = [sec("trouble")] + head(EB4, "막히면 오류의 마지막 줄을 봐요", K5)
tr = [("AttributeError: 'dict' object has no attribute 'add'", "빈 집합을 {}로 만들었어요", "cart = set()"),
      ("TypeError: 'set' object is not subscriptable", "집합에 번호를 붙였어요", "sorted(menus)[0]"),
      ("KeyError: 'juice'", "없는 값을 remove했어요", 'discard("juice")'),
      ("TypeError: unhashable type: 'list'", "집합에 리스트를 넣었어요", "튜플로 바꾸기"),
      ("{'b', 'a', 'n'}", "set()에 문자열을 넣었어요", '{"banana"}'),
      ("print 순서가 슬라이드와 달라요", "집합은 순서가 없어요", "sorted(menus)")]
o.append(f'<div style="position:absolute;left:96px;top:214px;width:1728px;height:52px;display:flex;flex-direction:row;gap:24px;border-bottom:3px solid {INK}">'
         + "".join(p(f"width:{w_}px;flex:none;font-size:24px;font-weight:700;color:{GRAY}", t) for t, w_ in [("마지막 줄", 870), ("까닭", 440), ("고치기", 370)]) + '</div>')
for i, (q, a_, cmd) in enumerate(tr):
    y = 266 + i * 108
    qa = q.isascii()
    o.append(f'<div{at("rise", 1 if i < 4 else 2)}{DELAY((i % 4) * 120)} style="position:absolute;left:96px;top:{y}px;width:1728px;height:108px;display:flex;flex-direction:row;align-items:center;gap:24px;border-bottom:2px solid {LINE}">'
             + p(f"width:870px;flex:none;{'font-family:' + MONO + ';font-size:26px;' if qa else 'font-size:28px;'}font-weight:700;color:{RED if 'Error' in q else INK};white-space:nowrap", e(q))
             + p(f"width:440px;flex:none;font-size:28px;color:{SUB}", e(a_))
             + p(f"width:370px;flex:none;{'font-family:' + MONO + ';font-size:26px;' if cmd.isascii() else 'font-size:28px;'}font-weight:700;color:{GR};white-space:pre", ("✓ " if True else "") + e(cmd)) + '</div>')
o.append(caption("마지막 두 줄은 오류가 안 나지만 결과가 생각과 달라요.", 960, 2))
W("trouble", o, "오류가 나면 마지막 줄에 어떤 값이 문제인지 나와요. 1번은 {}가 딕셔너리라서, 2번은 집합에 번호가 없어서, 3번은 없는 값을 remove해서, 4번은 리스트를 집합에 넣어서 나요. 5번과 6번은 오류는 안 나지만 결과가 생각과 다른 경우예요. 집합을 print한 순서가 슬라이드와 다른 것은 정상이에요. 모두 hello-uv 커널에서 실제로 실행한 결과예요.")

# ---------- part 5: practice ----------
o = [sec("x-kinds")] + head(EB5, "하루 주문에서 팔린 메뉴 종류를 뽑아요", K4)
c = {"id": "c-k", "lines": ['orders = ["coffee", "latte", "coffee", "cake",', '          "coffee", "latte", "tea"]', "kinds = set(orders)", 'print(f"주문 {len(orders)}잔, 메뉴 {len(kinds)}가지")', "for m in sorted(kinds):", "    print(m, orders.count(m))"], "n": 1,
     "out": ["주문 7잔, 메뉴 4가지", "cake 1", "coffee 3", "latte 2", "tea 1"]}
CF[0] = 32
CX, CY, CW = 96, 220, 1728
o += cell(c, CX, CY, CW, sel=True)
T = tx(CX, ['print(f"주문 {len(orders)}잔, 메뉴 {len(kinds)}가지")'], 40)
for k, (i, t) in enumerate([(2, "① 겹친 주문을 하나로"), (3, "② len으로 몇 가지인지"), (4, "③ abc 순서로 돌기"), (5, "④ 잔 수는 원래 리스트에서 count")], 1):
    o.append(hl(CX, CY, CW, i, 1, "mark", k))
    o.append(tag(T, ly(CY, i), t, K4, k, 28, lead=False))
o.append(tag(CX + 105 + tw("coffee 3") + 40, oy(CY, 6, 2), "집합은 중복을 없앴으니 셀 수 없어요", SUB, 4, 28))
CF[0] = 30
W("x-kinds", o, "종류는 집합으로, 잔 수는 원래 리스트로 세요. 카페의 하루 주문이 리스트 orders에 7잔 쌓였어요. 메뉴가 몇 가지 팔렸는지 알고 싶으면 set으로 바꾸고 len을 세요. 4가지예요. 메뉴별로 몇 잔인지는 집합이 아니라 원래 리스트에서 13의 count로 세요. 집합은 중복을 없앴으니 셀 수가 없어요. for에는 sorted(kinds)를 넣어서 언제 실행해도 abc 순서로 찍히게 했어요. 리스트는 대괄호가 닫히기 전이라 두 줄로 나눠 적었어요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("practice", "실습"))

o = [sec("x-class")] + head(EB5, "두 반을 다 듣는 사람과 한쪽만 듣는 사람", K4)
CF[0] = 26
c = {"id": "c-c", "lines": ['python_class = {"kim", "lee", "park", "choi"}', 'data_class = {"park", "choi", "jung", "kang"}', "both = python_class & data_class", "print(sorted(both))", "print(sorted(python_class - data_class))", "print(sorted(data_class - python_class))", 'print(f"모두 {len(python_class | data_class)}명")'], "n": 2,
     "out": ["['choi', 'park']", "['kim', 'lee']", "['jung', 'kang']", "모두 6명"]}
CX, CY, CW = 96, 220, 1000
o += cell(c, CX, CY, CW, sel=True)
for j, (t, col, k) in enumerate([("& 두 반 다", K4, 1), ("- 파이썬반만", VA, 2), ("- 데이터반만", VB, 3), ("| 겹친 둘은 한 번만", K4, 4)]):
    w_ = tw(c["out"][j])
    o.append(hlo(CX, CY, CW, 7, j, "mark", k, w_ + 30))
    o.append(tag(CX + 105 + w_ + 40, oy(CY, 7, j), t, col, k, 26))
CF[0] = 30
o.append(venn(1120, 280, ["kim", "lee"], ["park", "choi"], ["jung", "kang"], "python_class", "data_class", w=720, h=470, fs=30, hi=[("inter", K4, 1), ("a-b", VA, 2), ("b-a", VB, 3)]))
o.append(p(f"position:absolute;left:1120px;top:810px;width:720px;text-align:center;font-size:30px;font-weight:700;color:{INK}", "8명을 적었지만 모두 6명", at("rise", 4)))
W("x-class", o, "두 명단을 집합으로 만들면 겹친 사람과 한쪽만 듣는 사람을 한 줄씩으로 찾아요. 두 반을 다 듣는 사람은 교집합 & 로 찾아요. park과 choi예요. 파이썬반만 듣는 사람은 파이썬반에서 데이터반을 뺀 kim, lee예요. 반대로 빼면 데이터반만 듣는 jung, kang이 나와요. 전체 인원은 합집합의 len이에요. 명단에는 8명이 적혀 있지만 park과 choi가 겹쳐서 6명이에요. 결과는 sorted()로 줄 세워 찍어서 늘 같은 순서로 나와요." + REAL)

o = [sec("x-menu")] + head(EB5, "메뉴판에 없는 주문을 찾아요", K4)
CF[0] = 26
c = {"id": "c-mn", "lines": ['menu = {"coffee": 4500, "latte": 5000, "cake": 6500}', 'orders = ["coffee", "tea", "cake", "juice", "coffee"]', "print(set(menu))", "print(sorted(set(orders) - set(menu)))", "print(sorted(set(orders) & set(menu)))"], "n": 3,
     "out": ["{'latte', 'cake', 'coffee'}", "['juice', 'tea']", "['cake', 'coffee']"]}
CX, CY, CW = 96, 220, 1000
o += cell(c, CX, CY, CW, sel=True)
for j, (t, col, k) in enumerate([("딕셔너리를 넣으면 키만 모여요", K4, 1), ("메뉴판에 없는 주문", RED, 2), ("팔 수 있는 주문", GR, 3)]):
    w_ = tw(c["out"][j])
    o.append(hlo(CX, CY, CW, 5, j, "mark" if k == 1 else ("err" if k == 2 else "run"), k, w_ + 30))
    o.append(tag(CX + 105 + w_ + 40, oy(CY, 5, j), t, col, k, 26))
CF[0] = 30
o.append(venn(1120, 280, ["tea", "juice"], ["coffee", "cake"], ["latte"], "set(orders)", "set(menu)", w=720, h=470, fs=30, hi=[("a-b", RED, 2), ("inter", GR, 3)]))
o.append(p(f"position:absolute;left:96px;top:700px;width:1000px;font-size:30px;font-weight:700;line-height:1.5;color:{SUB}", "15에서 sorted(menu)가 키만 줄 세운 것과 같아요.<br>latte는 메뉴판에만 있고 아무도 안 시켰어요.", at("rise", 4)))
W("x-menu", o, "두 목록을 비교할 때는 둘 다 집합으로 바꿔서 빼거나 겹쳐 봐요. 15의 메뉴판 딕셔너리 menu와 손님 주문 리스트 orders가 있어요. 주문 중에 메뉴판에 없는 것을 찾고 싶어요. set(menu)는 딕셔너리의 키만 모은 집합이에요. 15에서 sorted(menu)가 키만 줄 세웠던 것과 같아요. 주문을 집합으로 바꾸고 메뉴판 집합을 빼면 juice와 tea가 남아요. 교집합은 메뉴판에 있어서 팔 수 있는 주문이에요. latte는 메뉴판에만 있고 아무도 주문하지 않았어요." + REAL)

o = [sec("x-bill")] + head(EB5, "팔 수 있는 주문만 계산해요", K4)
c = {"id": "c-b", "lines": ["total = 0", "for m in sorted(set(orders) & set(menu)):", "    qty = orders.count(m)", '    print(f"{m:<8}{qty}개 {menu[m] * qty:>7,}원")', "    total += menu[m] * qty", 'print(f"합계 {total:,}원")'], "n": 4,
     "out": ["cake    1개   6,500원", "coffee  2개   9,000원", "합계 15,500원"], "wide": True}
CF[0] = 36
CX, CY, CW = 96, 220, 1728
o += cell(c, CX, CY, CW, sel=True)
T = tx(CX, ['    print(f"{m:<8}{qty}개 {menu[m] * qty:>7,}원")'], 40)
for k, (i, t) in enumerate([(1, "메뉴판에 있는 주문만 돌아요"), (2, "13의 count로 잔 수"), (3, "15처럼 키로 가격을 꺼내요")], 1):
    o.append(hl(CX, CY, CW, i, 1, "mark", k))
    o.append(tag(T - 20 if i == 1 else T, ly(CY, i), t, K4, k, 26))
o.append(tag(CX + 105 + tw("합계 15,500원") + 80, oy(CY, 6, 2), "tea, juice는 & 에서 빠져서 menu[m]에서 KeyError가 안 나요", GR, 4, 28))
# the total counts up when its tag comes in
o = [x.replace("<p style=", "<p" + COUNT(4) + " style=", 1) if "15,500" in x and x.startswith("<p") else x for x in o]
CF[0] = 30
o.append(p(f"position:absolute;left:96px;top:900px;width:1728px;font-size:30px;font-weight:700;line-height:1.55;color:{SUB}", "15에서는 menu.get(name, 0)으로 없는 메뉴를 0원 처리했어요. 집합으로 먼저 거르면 그럴 일이 없어요.", at("rise", 5)))
W("x-bill", o, "교집합으로 먼저 걸러 두면 for 안에서 없는 키를 만나지 않아요. 앞 장의 교집합으로 팔 수 있는 메뉴만 for로 돌아요. 메뉴마다 13의 count로 몇 잔인지 세고, 15처럼 menu[m]으로 가격을 꺼내 곱해요. tea와 juice는 교집합에서 이미 빠져서 menu[m]에서 KeyError가 나지 않아요. 15에서는 get(name, 0)으로 없는 메뉴를 0원 처리했는데, 집합으로 미리 거르는 방법도 있어요. 앞 장의 set(orders) - set(menu)를 찍으면 준비 중인 메뉴를 손님에게 알려 줄 수도 있어요. 칸 맞추기와 콤마는 13의 f-string이에요. 출력의 한글은 영어 두 칸 너비로 그렸어요." + REAL)

# ---------- summary ----------
o = [f'<section id="cheatsheet" data-transition="fade" style="background:{BG};color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>']
cheat = [("{1, 2, 3}", "값만 적어 만들기", K1), ("set(orders)", "리스트에서 중복 없애기", K1), ("set()", "빈 집합", K1), ('s.add("tea")', "하나 넣기", K2),
         ('s.discard("tea")', "있으면 빼기", K2), ('"tea" in s', "들어 있는지 묻기", K2), ("a | b  a & b  a - b", "합집합, 교집합, 차집합", K3), ("sorted(s)", "줄 세운 리스트로", K4)]
for i, (k, d, c_) in enumerate(cheat):
    x, y = 96 + (i // 4) * 884, 220 + (i % 4) * 130
    o.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:844px;height:130px;display:flex;flex-direction:row;align-items:center;gap:24px;border-bottom:2px solid {LINE}">'
             + p(f"width:470px;flex:none;font-family:{MONO};font-size:34px;font-weight:700;color:{c_};white-space:pre", e(k)) + p(f"font-size:32px;font-weight:700;color:{INK}", e(d)) + '</div>')
o.append(p(f"position:absolute;left:96px;top:800px;width:1728px;font-size:34px;font-weight:700;line-height:1.6;color:{INK}", "집합은 같은 값을 하나만 담는 주머니예요. 순서와 번호가 없어서 화면에 찍을 땐 sorted()를 써요."))
o.append(p(f"position:absolute;left:96px;top:880px;width:1728px;font-size:30px;line-height:1.6;color:{SUB}", "17에서 if를 배우면 이번 챕터의 '참고' 코드를 직접 쳐 봐요."))
W("cheatsheet", o, "이번 챕터에서 쓴 코드를 한 장에 모았어요. 집합은 중복이 없고 순서가 없는 주머니라는 것을 기억해요. 노트북에 이 장의 내용을 마크다운 셀로 정리해 두면 복습할 때 같이 봐요. 17에서 if를 배우면 참고 칸의 긴 코드를 직접 쳐 보고, in과 함께 메뉴판에 있는 주문만 계산하는 코드도 다른 방법으로 만들어요.", ("summary", "정리"))

# ---------- toc: number, title, pages ----------
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
parts = [(K1, "집합이 뭔가요", "s-why", "s-hash"), (K2, "바꾸고 확인하기", "s-add", "s-for"), (K3, "집합 연산", "s-venn", "s-long2"),
         (K5, "비교와 오류", "x-choose", "trouble"), (K4, "실습", "x-kinds", "x-bill")]
TOC_NOTE = "다섯 파트로 나눴어요. 1파트는 집합이 무엇인지 그림으로 잡고, 2파트는 값을 넣고 빼고 확인해요. 3파트는 원 두 개로 집합 연산을 봐요. 4파트에서 네 그릇을 비교하고 자주 나는 오류를 모아 보고, 5파트는 앞에서 배운 것을 섞어 실제 주문과 명단을 정리해요. 파트마다 새 커널에서 위에서부터 차례로 실행해요."
DECK_TITLE = "파이썬 기초 5 (집합)"
t = [f'<section id="toc" data-transition="fade" style="background:{BG};color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>']
for i, (c_, h, a, b) in enumerate(parts, 1):
    y = 220 + (i - 1) * 132
    t.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:132px;display:flex;flex-direction:row;align-items:center;gap:40px;border-bottom:2px solid {LINE}">'
             f'<p style="width:80px;flex:none;font-size:64px;font-weight:900;color:{c_}">{i}</p>'
             f'<p style="flex:1;font-size:44px;font-weight:700;color:{INK}">{h}</p>'
             f'<p style="font-size:30px;font-weight:700;color:{GRAY}">{page[a]}–{page[b]}쪽</p></div>')
t.append(f'<p style="position:absolute;left:96px;top:{220 + 5 * 132 + 40}px;font-size:28px;color:{SUB}">{page["ready"]}쪽은 노트북 준비, {page["cheatsheet"]}쪽은 한 장 요약이에요.</p>')
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(t) + f"\n<aside>{e(TOC_NOTE)}</aside>\n</section>\n")

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-03T02:00:00Z"}, "lists": "css", "title": DECK_TITLE, "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
print(len(ORDER), "slides")
