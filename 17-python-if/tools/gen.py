"""Generates every slide of the control flow 1 deck (17, if) and slides/deck.json.

Story: keeps writing in basics.ipynb from chapters 12-16. Starts from the KeyError that stopped chapter 15's menu,
draws if as a fork in the road, then adds else, elif, and, or, not and empty values. Part 4 puts if inside for and
opens up the read-only "참고" code of chapters 15 and 16. Ends with the café: discounts, grades and a receipt.
Every cell and output comes from tools/demo.sh (tools/run_nb.py runs the cells with the project kernel).

Layout rules (Stageshow skill, tools/DESIGN.md): the notebook cell is the one focal object of a slide; terms are
leader tags beside the line they explain (tag, ly, oy, tx), not cards; a fix is the wrong line struck through
next to the right one (fix); tables are hairline rows (rows), not boxes; highlights come from tools/highlight.py.
Usage: python3 tools/gen.py slides
"""

import html, json, os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from highlight import spot, spot_off, cursor, cursor_off, ring, box, underline

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
INK, SUB, LINE, CARD = "#1D2330", "#4A5262", "#E1DED6", "#FFFFFF"
BL, GR, OR, PUR, RED, NAVY, TEAL, GRAY = "#2459C9", "#1F8A4C", "#B26A00", "#5A3BB8", "#A33131", "#1E3F8F", "#0F7C86", "#6A7180"
JP = "#B8560F"          # Jupyter, same as chapters 09 and 10
SEL = "#2F7DE1"         # selected cell bar, like VS Code's focus color
GRBG, REDBG = "#E6F4EC", "#F8E6E6"


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


def caption(text, top=960, order=None):
    at = f' data-build-in="rise order {order}"' if order else ' data-build-in="rise"'
    return p(f"position:absolute;left:96px;top:{top}px;width:1728px;font-size:34px;font-weight:700;line-height:1.4;color:{INK}", text, ' id="caption"' + at)


def at(order, kind="fade"):
    return f' data-build-in="{kind} order {order}"' if order else ""


# ---------- notebook cell, drawn at CFS[0] px ----------
CFS = [30]


def LH():
    return CFS[0] * 1.45


def WIDE(t):
    """Draws each Hangul syllable two monospace columns wide, like a terminal."""
    return re.sub(r"([가-힣])", r'<span style="display:inline-block;width:1.2em;text-align:center">\1</span>', t)


def cell(c, left, top, w, sel=None, attrs=""):
    """c: dict(id, lines, n, out, err, wide). sel: id of the selected cell (blue bar)."""
    fs, lines, n = CFS[0], c.get("lines", [""]), c.get("n")
    o = [f'<div id="{c["id"]}"{attrs or c.get("attrs", "")} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;display:flex;flex-direction:column;gap:10px">']
    bar = f'<div style="width:7px;flex:none;border-radius:4px;background:{SEL if sel == c["id"] else "transparent"}"></div>'
    gutter = p(f"width:58px;flex:none;font-family:{MONO};font-size:22px;color:{GRAY};text-align:right;padding-top:12px", f"[{n}]" if n else "[ ]")
    txt = "".join(p(f"font-family:{MONO};font-size:{fs}px;line-height:1.45;white-space:pre;color:{INK}", e(l) if l else "&#160;") for l in lines)
    tag_ = p(f"position:absolute;right:14px;bottom:8px;font-size:18px;color:{GRAY}", "Python")
    body = f'<div style="flex:1;position:relative;background:#FFFFFF;border:2px solid {LINE};border-radius:10px;padding:8px 18px 8px;display:flex;flex-direction:column">{txt}{tag_}</div>'
    o.append(f'<div style="display:flex;flex-direction:row;gap:10px;align-items:stretch">{bar}{gutter}{body}</div>')
    if c.get("out"):
        wide = WIDE if c.get("wide") else (lambda t: t)
        col = lambda l: RED if c.get("err") and re.match(r"([A-Za-z]+Error|Cell In)", l) else INK
        o.append("".join(p(f"margin-left:85px;padding:0 20px;font-family:{MONO};font-size:{fs}px;line-height:1.45;white-space:pre;color:{col(l)}", wide(e(l))) for l in c["out"]))
    o.append('</div>')
    return o


def cell_h(c):
    return 20 + LH() * len(c.get("lines", [""])) + sum(10 + LH() for _ in c.get("out", []))


def ly(top, i):
    """Center y of code line i (may be fractional) of a cell drawn at top."""
    return top + 10 + i * LH() + LH() / 2


def oy(top, n, j):
    """Center y of output line j of a cell with n code lines."""
    return top + 20 + n * LH() + 10 + j * (LH() + 10) + LH() / 2


def tw(s, fs=None):
    """Rendered width of a code string: Hangul about one em, the rest 0.6 em."""
    fs = fs or CFS[0]
    return sum(fs * (1.0 if '가' <= ch <= '힣' else 0.6) for ch in s)


def cx(left, prefix):
    """x where a code or output line inside a cell at left reaches after prefix."""
    return left + 105 + tw(prefix)


def tx(left, lines, gap=36):
    """x just right of the longest of the given lines inside a cell at left."""
    return int(left + 105 + max(tw(l) for l in lines) + gap)


def tag(x, y, text, color, order=None, size=28, lead=True, anim="fade", w=None):
    """A leader label '← text' centred on y. No box."""
    ws = f"width:{w}px;white-space:normal;" if w else "white-space:nowrap;"
    return p(f"position:absolute;left:{x:.0f}px;top:{y - size * 0.725:.0f}px;{ws}font-size:{size}px;font-weight:700;line-height:1.45;color:{color}", ("← " if lead else "") + e(text), at(order, anim))


HL = {"run": "rgba(31,138,76,0.16)", "skip": "rgba(106,113,128,0.20)", "err": "rgba(163,49,49,0.14)", "mark": "rgba(36,89,201,0.14)"}


def hl(left, top, w, i, n=1, kind="run", order=1, tag_=None, tc=None):
    """Tints code lines i..i+n-1 of a cell drawn at (left, top, w). tag_: a short word at the right end of the tint."""
    y = top + 10 + i * LH()
    t = p(f"position:absolute;right:104px;top:0;font-size:21px;font-weight:700;line-height:{LH():.0f}px;color:{tc or {'run': GR, 'skip': GRAY, 'err': RED, 'mark': BL}[kind]}", e(tag_)) if tag_ else ""
    return f'<div{at(order)} style="position:absolute;left:{left + 87}px;top:{y:.0f}px;width:{w - 89}px;height:{n * LH():.0f}px;background:{HL[kind]};border-radius:6px">{t}</div>'


def ring_tok(order, left, top, i, prefix, tok, color=RED, out_n=None):
    """Pen ring around a token of code line i (or of output line i when out_n gives the code line count)."""
    y = (oy(top, out_n, i) if out_n is not None else ly(top, i)) - LH() / 2
    return ring(order, cx(left, prefix) - 4, y + 2, tw(tok) + 8, LH() - 4, color)


def under_tok(order, left, top, i, prefix, tok, color=OR, out_n=None, dy=4):
    y = (oy(top, out_n, i) if out_n is not None else ly(top, i)) + LH() / 2 - dy
    return underline(order, int(cx(left, prefix)), int(cx(left, prefix + tok)), int(y), color)


def tf(v, size=26):
    """True / False chip (status color)."""
    c, bg = (GR, GRBG) if v == "True" else (RED, REDBG)
    return p(f"display:inline-block;font-family:{MONO};font-size:{size}px;font-weight:700;color:{c};background:{bg};border-radius:10px;padding:2px 14px;white-space:nowrap", v)


def chain(rows, left, top, start=1, color=PUR, gap=74, fs=28, lw=110):
    """Evaluation steps shown one per click: (expression, result chip or None, label)."""
    o = []
    for i, (expr, res, lbl) in enumerate(rows):
        y = top + i * gap
        o.append(f'<div{at(start + i, "rise")} style="position:absolute;left:{left}px;top:{y}px;height:{gap - 12}px;display:flex;flex-direction:row;align-items:center;gap:18px">'
                 + (p(f"width:{lw}px;flex:none;font-size:24px;font-weight:700;color:{color}", e(lbl)) if lbl is not None else "")
                 + p(f"font-family:{MONO};font-size:{fs}px;font-weight:700;color:{INK};white-space:pre", e(expr))
                 + (p(f"font-size:{fs}px;font-weight:700;color:#9AA1AE", "→") + tf(res, fs - 2) if res else "") + '</div>')
    return o


def rows(left, top, widths, data, head_=None, order0=1, rh=78, fs=28, step=1, kinds=None, ids=None):
    """A light table: gray header over a 3px rule, rows split by 2px hairlines, no boxes.
    kinds: per cell 'code', 'sans', 'tf' or a color for sans text. step: rows per build order."""
    o, y, w = [], top, sum(widths) + 24 * (len(widths) - 1)
    if head_:
        o.append(f'<div{at(order0) if order0 else ""} style="position:absolute;left:{left}px;top:{y}px;width:{w}px;height:50px;display:flex;flex-direction:row;gap:24px;border-bottom:3px solid {INK}">'
                 + "".join(p(f"width:{cw}px;flex:none;font-size:23px;font-weight:700;color:{GRAY}", e(c)) for c, cw in zip(head_, widths)) + '</div>')
        y += 58
    for i, r in enumerate(data):
        cs = ""
        for k, (c, cw) in enumerate(zip(r, widths)):
            kind = (kinds or ["sans"] * len(r))[k]
            if kind == "tf":
                cs += f'<div style="width:{cw}px;flex:none">{tf(c, fs - 4)}</div>' if c else f'<div style="width:{cw}px;flex:none"></div>'
            elif kind == "code":
                cs += p(f"width:{cw}px;flex:none;font-family:{MONO};font-size:{fs}px;font-weight:700;color:{INK};white-space:pre", e(c))
            else:
                col = kind if kind.startswith("#") else (INK if k == 0 else SUB)
                cs += p(f"width:{cw}px;flex:none;font-size:{fs}px;font-weight:{700 if k == 0 or kind.startswith('#') else 500};line-height:1.35;color:{col}", e(c))
        rid = f' id="{ids[i]}"' if ids else ""
        o.append(f'<div{rid}{at(order0 + i // step, "rise") if order0 else ""} style="position:absolute;left:{left}px;top:{y + i * rh:.0f}px;width:{w}px;height:{rh}px;display:flex;flex-direction:row;align-items:center;gap:24px;border-bottom:2px solid {LINE}">{cs}</div>')
    return o


def arrow_r(w=64, color="#B4B9C3"):
    return (f'<svg style="width:{w}px;height:28px;flex:none" viewBox="0 0 {w} 28"><path d="M2,14 L{w - 16},14" stroke="{color}" stroke-width="5" stroke-linecap="round"/>'
            f'<path d="M{w - 22},4 L{w - 4},14 L{w - 22},24" fill="none" stroke="{color}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def fix(left, top, bad, good, order, size=30, note=None):
    """The wrong line struck through, an arrow, the right line."""
    return (f'<div{at(order, "rise")} style="position:absolute;left:{left}px;top:{top}px;display:flex;flex-direction:row;align-items:center;gap:22px">'
            + p(f"font-size:{size}px;font-weight:900;color:{RED}", "✕")
            + p(f"font-family:{MONO};font-size:{size}px;font-weight:700;color:{RED};text-decoration:line-through;text-decoration-thickness:3px;white-space:pre", e(bad))
            + arrow_r()
            + p(f"font-size:{size}px;font-weight:900;color:{GR}", "✓")
            + p(f"font-family:{MONO};font-size:{size}px;font-weight:700;color:{INK};background:{GRBG};border:3px solid {GR};border-radius:14px;padding:6px 20px;white-space:pre", e(good))
            + (p(f"margin-left:12px;font-size:{size - 2}px;font-weight:700;color:{GR};white-space:nowrap", e(note)) if note else "") + '</div>')


_fl = [0]


def flow(left, top, w, h, nodes, edges, attrs=""):
    """A small flowchart. nodes: dict(x, y, w, h, kind box|diamond, text, color, bg, order, fs, mono).
    edges: dict(pts [(x, y), ...], color, order, label, lx, ly). Coordinates are inside the w x h area."""
    o = [f'<div{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px">']
    for ed in edges:
        _fl[0] += 1
        mid = f"fa{_fl[0]}"
        col = ed.get("color", "#9AA1AE")
        a = at(ed.get("order"))
        pts = " ".join(f"{x:.0f},{y:.0f}" for x, y in ed["pts"])
        o.append(f'<svg{a} style="position:absolute;left:0;top:0;width:{w}px;height:{h}px" viewBox="0 0 {w} {h}">'
                 f'<defs><marker id="{mid}" markerUnits="userSpaceOnUse" markerWidth="24" markerHeight="24" refX="20" refY="12" orient="auto"><path d="M0,0 L24,12 L0,24 z" fill="{col}"/></marker></defs>'
                 f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="5" stroke-linejoin="round" marker-end="url(#{mid})"/></svg>')
        if ed.get("label"):
            o.append(p(f"position:absolute;left:{ed['lx']}px;top:{ed['ly']}px;font-size:{ed.get('fs', 26)}px;font-weight:700;color:{col};white-space:nowrap", e(ed["label"]), a))
    for nd in nodes:
        x, y, nw, nh = nd["x"], nd["y"], nd["w"], nd["h"]
        col, bg = nd.get("color", GRAY), nd.get("bg", CARD)
        a = at(nd.get("order"), nd.get("anim", "rise"))
        fs = nd.get("fs", 26)
        font = MONO if nd.get("mono", True) else SANS
        txt = p(f"font-family:{font};font-size:{fs}px;font-weight:700;line-height:1.3;color:{nd.get('tc', INK)};text-align:center;white-space:pre", e(nd["text"]))
        if nd.get("kind") == "diamond":
            o.append(f'<div{a} style="position:absolute;left:{x}px;top:{y}px;width:{nw}px;height:{nh}px">'
                     f'<svg style="position:absolute;left:0;top:0;width:{nw}px;height:{nh}px" viewBox="0 0 {nw} {nh}"><polygon points="{nw / 2:.0f},3 {nw - 3},{nh / 2:.0f} {nw / 2:.0f},{nh - 3} 3,{nh / 2:.0f}" fill="{bg}" stroke="{col}" stroke-width="4"/></svg>'
                     f'<div style="position:absolute;left:{nw * 0.15:.0f}px;top:0;width:{nw * 0.7:.0f}px;height:{nh}px;display:flex;align-items:center;justify-content:center">{txt}</div></div>')
        else:
            o.append(f'<div{a} style="position:absolute;left:{x}px;top:{y}px;width:{nw}px;height:{nh}px;background:{bg};border:3px solid {col};border-radius:16px;display:flex;align-items:center;justify-content:center;padding:0 14px">{txt}</div>')
    o.append('</div>')
    return "".join(o)


def kbd(text, size=30):
    caps = [p(f"font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.2;white-space:nowrap;color:{INK};background:#FFFFFF;border:2px solid #C9CED8;border-bottom-width:5px;border-radius:10px;padding:6px 14px", e(k)) for k in text.split("+")]
    return '<div style="display:flex;flex-direction:row;align-items:center;gap:8px">' + p(f"font-size:{size * 0.8:.0f}px;font-weight:700;color:{GRAY}", "+").join(caps) + '</div>'


EB1 = "1. 참과 거짓으로 길 고르기"
EB2 = "2. if, else, elif"
EB3 = "3. 조건 합치기"
EB4 = "4. for와 함께, 줄여 쓰기"
EB5 = "5. 자주 나는 오류"
EB6 = "6. 실습"
K1, K1BG = "#1E5FA8", "#E5EEF8"
K2, K2BG = "#A0620A", "#F7EEDD"
K3, K3BG = TEAL, "#E2F2F3"
K4, K4BG = "#A23B72", "#F6E7EF"
K5 = RED
K6, K6BG = PUR, "#ECE7F8"
MENU = 'menu = {"coffee": 4500, "latte": 5000, "cake": 6500}'
NB = "basics.ipynb"
REAL = " 출력은 실제로 실행한 결과예요."
NEWK = " 이 파트는 새 커널이라 셀 번호가 [1]부터예요."

# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#F2B27A">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
       '<h1 style="font-size:92px;font-weight:900;line-height:1.1;color:#F6F5F1">제어문 1<br>조건문 if</h1>',
       '<p style="font-size:40px;line-height:1.4;color:#BFC6D4">조건에 따라<br>다른 줄을 실행하기</p>']
cov.append('<div style="position:absolute;left:940px;top:300px;width:860px;height:480px;background:#252B36;border-radius:24px;padding:44px 48px;display:flex;flex-direction:column;justify-content:center;gap:16px">')
for line, c in [("if total >= 20000:", "#9DBDEB"), ('    print("10% 할인")', "#E6E9EF"), ("elif total >= 10000:", "#E3B877"), ('    print("5% 할인")', "#E6E9EF"), ("else:", "#E3B877"), ('    print("할인 없음")', "#E6E9EF")]:
    cov.append(p(f"font-family:{MONO};font-size:36px;font-weight:700;line-height:1.45;color:{c};white-space:pre", e(line)))
cov.append('</div>')
W("cover", cov, "이번 챕터에서는 조건이 True일 때만 실행하는 if를 직접 써요. 15와 16에서 참고 칸에 두고 읽기만 했던 if 코드를 이번에 직접 쳐요. 12의 비교와 and, or, not, 13의 for를 그대로 가져와요. 같은 카페 예제로 이어 가고, 18에서는 while과 break로 반복을 다뤄요.", ("intro", "들어가기"))

ORDER.append("toc")   # written last, after page numbers are known

# ---------- ready: what we carry over, and the notebook to open ----------
o = [sec("ready")] + head("들어가기", "16에서 쓰던 노트북에 이어서 적어요", JP)
o += rows(96, 210, [520, 220], [["hello-uv 노트북, 커널 .venv", "09 · 25–27쪽"], ["비교 ==, >=, and, or, not", "12 · 3파트"], ["리스트, for, f-string", "13"], ["in과 not in", "14"], ["딕셔너리 menu와 get", "15"], ["집합과 discard", "16"]],
          ["가져오는 것", "다시 볼 곳"], 1, 92, 28, 2, ["sans", GRAY])
# a VS Code notebook header as the hero: file name, toolbar, kernel chip
NBX, NBY, NBW = 960, 230, 864
o.append(f'<div style="position:absolute;left:{NBX}px;top:{NBY}px;width:{NBW}px;background:#FFFFFF;border:2px solid {LINE};border-radius:18px;overflow:hidden;box-shadow:0 18px 40px rgba(29,35,48,.10)">'
         f'<div style="height:58px;background:#ECEAE3;display:flex;flex-direction:row;align-items:center;padding:0 22px;gap:14px">'
         + p(f"font-family:{MONO};font-size:22px;font-weight:700;color:{INK}", NB) + '<div style="flex:1"></div>'
         + p(f"font-size:19px;color:{SUB}", "+ Code") + p(f"font-size:19px;color:{SUB}", "+ Markdown") + p(f"font-size:19px;color:{SUB}", "▷ Run All") + '</div>'
         f'<div style="height:64px;display:flex;flex-direction:row;align-items:center;padding:0 22px;border-bottom:2px solid {LINE}"><div style="flex:1"></div>'
         + p(f"font-size:21px;font-weight:700;color:{GR};background:{GRBG};border-radius:8px;padding:6px 14px", ".venv (Python 3.14.6)", ' id="kernel"') + '</div>'
         + '<div style="padding:28px 26px;display:flex;flex-direction:column;gap:20px">'
         + "".join('<div style="display:flex;flex-direction:row;gap:12px;align-items:center">' + p(f"width:50px;flex:none;font-family:{MONO};font-size:20px;color:{GRAY};text-align:right", n_)
                   + f'<div style="flex:1;height:58px;border:2px solid {LINE};border-radius:10px;display:flex;align-items:center;padding:0 16px">'
                   + f'<div style="height:12px;width:{w_}px;border-radius:6px;background:#E4E2DC"></div></div></div>' for n_, w_ in [("[1]", 420), ("[2]", 300), ("[3]", 360)])
         + '<div style="display:flex;flex-direction:row;gap:12px;align-items:center">' + p(f"width:50px;flex:none;font-family:{MONO};font-size:20px;color:{GRAY};text-align:right", "[ ]")
         + f'<div style="flex:1;height:58px;border:3px solid {SEL};border-radius:10px;display:flex;align-items:center;padding:0 16px">' + p(f"font-family:{MONO};font-size:24px;color:{SEL};font-weight:700", "|") + '</div></div>'
         + '</div></div>')
o.append(cursor(4, NBX + NBW - 34, NBY + 58 + 42))
o.append(tag(NBX, NBY + 520, "커널이 .venv인지 보고, 새 셀에서 Shift+Enter로 실행해요", JP, 4, 26, False))
W("ready", o, "09에서 만든 hello-uv 폴더를 VS Code로 열고 12부터 쓰던 basics.ipynb에 이어서 적어요. 왼쪽은 이번 챕터에서 다시 쓰는 내용과 기억이 안 날 때 볼 곳이에요. 오른쪽 위 커널이 .venv인지 먼저 보고, 새 셀에 적은 뒤 Shift+Enter로 실행해요. 슬라이드의 출력은 tools/demo.sh가 hello-uv 커널에서 같은 셀을 실제로 실행한 결과예요. 셀 번호는 파트마다 [1]부터 다시 셌어요.")

# ---------- part 1 ----------
CFS[0] = 32
o = [sec("i-why")] + head(EB1, "메뉴판에 없는 주문이 오면 셀이 멈춰요", K1)
T = 230
c = {"id": "c-why", "lines": [MENU, 'order = "tea"', "print(menu[order])"], "n": 1, "out": ["KeyError: 'tea'"], "err": True}
o += cell(c, 96, T, 1150, sel="c-why")
o.append(hl(96, T, 1150, 2, 1, "err", 1))
o.append(tag(tx(96, ["print(menu[order])"]), ly(T, 2), "tea가 없어도 이 줄을 실행해요", RED, 1))
o.append(ring_tok(2, 96, T, 0, "", "KeyError: 'tea'", RED, out_n=3))
o.append(p(f"position:absolute;left:96px;top:620px;width:1150px;font-size:30px;font-weight:700;line-height:1.5;color:{GRAY}", "원하는 것은", at(3)))
o.append(p(f"position:absolute;left:96px;top:676px;width:1150px;font-size:48px;font-weight:700;line-height:1.5;color:{INK}", "<b style=\"color:" + GR + "\">메뉴판에 있으면</b> 가격을 찍고,<br><b style=\"color:" + RED + "\">없으면</b> 없다고 말해요.", at(3)))
# 15, 16 read-only code: quiet satellite column, no boxes
RX = 1340
o.append(p(f"position:absolute;left:{RX}px;top:{T}px;width:484px;font-size:24px;font-weight:700;color:{GRAY}", "15, 16에서 읽기만 한 코드", at(4)))
refs = [('menu["cakee"] if "cakee" in menu', '    else 5000'), ('if "juice" in menus:', '    menus.remove("juice")'), ("for o in orders:", "    if o not in kinds:", "        kinds.append(o)")]
y = T + 56
for r in refs:
    o.append(f'<div{at(4)} style="position:absolute;left:{RX}px;top:{y}px;width:484px;padding:14px 0;border-top:2px solid {LINE};display:flex;flex-direction:column">'
             + "".join(p(f"font-family:{MONO};font-size:22px;line-height:1.5;white-space:pre;color:{SUB}", e(l)) for l in r) + '</div>')
    y += 30 + 33 * len(r) + 18
o.append(caption("조건에 따라 실행할 줄을 고르는 문법이 if예요.", 960, 5))
CFS[0] = 30
W("i-why", o, "지금까지 셀은 적은 줄을 위에서 아래로 모두 실행했어요. 주문이 메뉴판에 없는 tea여도 print(menu[order])를 그대로 실행해서 KeyError가 나요. 원하는 건 메뉴판에 있을 때만 가격을 찍고, 없으면 없다고 말하는 거예요. 조건에 따라 실행할 줄을 고르는 문법이 if예요. 오른쪽은 15와 16에서 참고 칸에 두고 읽기만 했던 코드예요. 모두 if를 썼고, 이번 챕터를 마치면 직접 쓸 수 있어요." + NEWK + REAL, ("p1", "참과 거짓으로 길 고르기"))

# big picture: straight road vs fork
o = [sec("i-big")] + head(EB1, "if는 코드에 갈림길을 만들어요", K1)
o.append(p(f"position:absolute;left:96px;top:214px;font-size:26px;font-weight:700;color:{GRAY}", "지금까지"))
o.append(flow(96, 270, 420, 600,
              [dict(x=30, y=0, w=360, h=84, text="money = 5000", color="#B4B9C3", fs=24, tc=SUB), dict(x=30, y=170, w=360, h=84, text="price = 4500", color="#B4B9C3", fs=24, tc=SUB),
               dict(x=30, y=340, w=360, h=84, text='print("주문")', color="#B4B9C3", fs=24, tc=SUB), dict(x=30, y=510, w=360, h=84, text='print("다음 손님")', color="#B4B9C3", fs=24, tc=SUB)],
              [dict(pts=[(210, 86), (210, 166)], color="#C9CED8"), dict(pts=[(210, 256), (210, 336)], color="#C9CED8"), dict(pts=[(210, 426), (210, 506)], color="#C9CED8")]))
o.append(f'<div style="position:absolute;left:600px;top:214px;width:3px;height:680px;background:{LINE}"></div>')
o.append(p(f"position:absolute;left:700px;top:214px;font-size:26px;font-weight:700;color:{K1}", "if를 쓰면", at(1)))
o.append(flow(700, 262, 1124, 660,
              [dict(x=110, y=0, w=460, h=92, text="money, price", color=GRAY, order=1, fs=28),
               dict(x=80, y=150, w=520, h=190, kind="diamond", text="money >= price", color=K1, bg=K1BG, order=2, fs=30),
               dict(x=110, y=400, w=460, h=96, text='print("주문할 수 있어요")', color=GR, bg=GRBG, order=3, fs=24),
               dict(x=110, y=560, w=460, h=92, text='print("다음 손님")', color=GRAY, order=5, fs=26)],
              [dict(pts=[(340, 94), (340, 146)], order=2),
               dict(pts=[(340, 342), (340, 396)], color=GR, order=3, label="True", lx=362, ly=346),
               dict(pts=[(340, 498), (340, 556)], color=GR, order=3),
               dict(pts=[(602, 245), (860, 245), (860, 606), (574, 606)], color=RED, order=4, label="False · 건너뛰기", lx=640, ly=196)],
              at(1)))
o.append(caption("마름모가 갈림길이에요. True면 아래로, False면 옆길로 가요.", 960, 6))
W("i-big", o, "if는 코드에 갈림길을 하나 만들어요. 왼쪽은 지금까지 쓰던 코드라 위에서 아래로 한 줄로 쭉 가요. 오른쪽 마름모 안의 조건이 True면 아래로 내려가 주문할 수 있어요를 찍어요. False면 옆길로 돌아가서 그 줄을 건너뛰어요. 두 길은 다음 손님에서 다시 만나요. 이 챕터의 모든 if는 이 그림 하나로 읽을 수 있어요.")

# minimal example: one big cell, labels outside it
CFS[0] = 44
o = [sec("i-min")] + head(EB1, "가장 짧은 if는 조건 한 줄, 들여쓴 줄 하나예요", K1)
T, MW = 220, 860
LMIN = ["money = 5000", "price = 4500", "if money >= price:", '    print("주문할 수 있어요")', 'print("다음 손님")']
o += cell({"id": "c-min", "lines": LMIN, "n": 2, "out": ["주문할 수 있어요", "다음 손님"]}, 96, T, MW, sel="c-min")
TXM = 96 + MW + 44
o.append(under_tok(1, 96, T, 2, "if ", "money >= price", BL))
o.append(tag(TXM, ly(T, 2) - 24, "조건 · True나 False가 나와요", BL, 1, 30))
o.append(box(2, cx(96, "if money >= price") - 3, ly(T, 2) - LH() / 2 + 6, tw(":") + 6, LH() - 12, OR, 4, 6))
o.append(tag(TXM, ly(T, 2) + 26, "끝에 콜론", OR, 2, 30))
o.append(hl(96, T, MW, 3, 1, "run", 3))
o.append(tag(TXM, ly(T, 3) + 10, "4칸 들여쓰면 True일 때만 실행", GR, 3, 30))
o.append(hl(96, T, MW, 4, 1, "skip", 4))
o.append(tag(TXM, ly(T, 4) + 10, "if 밖이라 늘 실행", GRAY, 4, 30))
o.append(caption("콜론 뒤에서 Enter를 치면 VS Code가 4칸을 넣어 줘요.", 960, 5))
W("i-min", o, "if 뒤에 조건을 적고 콜론으로 끝낸 다음, 다음 줄을 4칸 들여쓰면 가장 짧은 if예요. 13의 for와 같은 모양이에요. money 5000은 price 4500보다 크거나 같아서 조건이 True예요. 그래서 들여쓴 print를 실행해요. 들여쓰지 않은 마지막 print는 if 밖이라 조건과 상관없이 실행해요. VS Code에서 콜론 뒤에 Enter를 치면 4칸이 저절로 들어가요. 직접 넣을 땐 Tab을 한 번 눌러요." + REAL)
CFS[0] = 30

# conditions are bools
o = [sec("i-bool")] + head(EB1, "조건 자리에는 True나 False가 나오는 식을 적어요", K1)
T = 220
LB = ["print(money >= price)", "print(money == price)", 'print("tea" in menu)', 'print("tea" not in menu)', "print(type(money >= price))"]
o += cell({"id": "c-bool", "lines": LB, "n": 3, "out": ["True", "False", "False", "True", "<class 'bool'>"]}, 96, T, 860, sel="c-bool")
o.append(under_tok(1, 96, T, 4, "", "<class 'bool'>", BL, out_n=5))
o.append(tag(cx(96, "<class 'bool'>") + 30, oy(T, 5, 4), "True, False의 종류 이름", BL, 1))
o += rows(1060, T, [200, 360, 140], [["==", "같아요", "12"], ["!=", "달라요", "12"], ["<  >", "작아요, 커요", "12"], ["<=  >=", "작거나 같아요, 크거나 같아요", "12"], ["in", "들어 있어요", "14"], ["not in", "안 들어 있어요", "14"]],
          ["기호", "뜻", "배운 곳"], 2, 92, 28, 6, ["code", "sans", GRAY])
o.append(caption("if는 조건이 True인지 False인지 보고 길을 골라요.", 960, 3))
W("i-bool", o, "if 뒤에 오는 조건은 True나 False가 나오는 식이에요. 12에서 비교하면 답이 True 아니면 False였어요. 14의 in과 not in도 True, False로 답했어요. 이 두 값을 묶어서 bool이라고 부르고, type으로 보면 class bool이라고 나와요. 오른쪽은 조건에 쓰는 기호와 처음 배운 챕터예요. 셀 [3]은 앞 셀의 money와 price, menu를 그대로 썼어요." + REAL)

# ---------- part 2 ----------
CFS[0] = 34
o = [sec("i-false")] + head(EB2, "조건이 False면 들여쓴 줄을 건너뛰어요", K2)
BUYL = ["if money >= price:", '    print("주문할 수 있어요")', 'print("다음 손님")']
T1, T2 = 210, 630
L1 = ["price = 4500", "money = 5000"] + BUYL
o += cell({"id": "c-f1", "lines": L1, "n": 1, "out": ["주문할 수 있어요", "다음 손님"]}, 96, T1, 1100, sel="c-f1")
o += cell({"id": "c-f2", "lines": ["money = 3000"] + BUYL, "n": 2, "out": ["다음 손님"]}, 96, T2, 1100, attrs=at(3, "rise"))
TXF = 1250
o.append(hl(96, T1, 1100, 3, 1, "run", 1))
o.append(tag(TXF, ly(T1, 2), "5000 >= 4500", INK, 1, 30, False))
o.append(f'<div{at(2)} style="position:absolute;left:{TXF}px;top:{ly(T1, 2) + 30:.0f}px">' + tf("True", 26) + '</div>')
o.append(tag(TXF, ly(T1, 3) + 44, "실행해요", GR, 2))
o.append(hl(96, T2, 1100, 2, 1, "skip", 4))
o.append(tag(TXF, ly(T2, 1), "3000 >= 4500", INK, 4, 30, False))
o.append(f'<div{at(4)} style="position:absolute;left:{TXF}px;top:{ly(T2, 1) + 30:.0f}px">' + tf("False", 26) + '</div>')
o.append(tag(TXF, ly(T2, 2) + 44, "건너뛰어요", GRAY, 5))
o.append(tag(cx(96, "다음 손님") + 30, oy(T2, 4, 0), "출력이 한 줄뿐이지만 오류가 아니에요", GRAY, 6))
o.append(caption("같은 코드라도 값에 따라 실행하는 줄이 달라져요.", 960, 7))
CFS[0] = 30
W("i-false", o, "조건이 False면 들여쓴 줄을 건너뛰고 if 다음 줄로 가요. 같은 if를 money만 바꿔서 두 번 실행했어요. 위는 5000이라 조건이 True고, 들여쓴 print를 실행해요. 아래는 3000이라 조건이 False라서 들여쓴 print를 건너뛰고 바로 다음 손님을 찍어요. 오류가 난 게 아니라 일부러 건너뛴 거예요. 아래 셀에는 price를 다시 적지 않았어요. 셀 [1]에서 넣은 4500이 그대로 남아 있어요." + NEWK + REAL, ("p2", "if, else, elif"))

CFS[0] = 32
o = [sec("i-indent")] + head(EB2, "들여쓴 줄까지가 if에 속해요", K2)
T1, T2 = 210, 556
o += cell({"id": "c-i1", "lines": ["money = 3000", "if money >= price:", '    print("주문할 수 있어요")', '    print("커피 나왔어요")', 'print("다음 손님")'], "n": 3, "out": ["다음 손님"]}, 96, T1, 1100, sel="c-i1")
o += cell({"id": "c-i2", "lines": ["money = 3000", "if money >= price:", '    print("주문할 수 있어요")', 'print("커피 나왔어요")', 'print("다음 손님")'], "n": 4, "out": ["커피 나왔어요", "다음 손님"]}, 96, T2, 1100, attrs=at(2, "rise"))
o.append(hl(96, T1, 1100, 2, 2, "skip", 1))
o.append(tag(TXF, ly(T1, 2.5), "if 안 · 둘 다 건너뛰어요", GRAY, 1))
o.append(hl(96, T2, 1100, 2, 1, "skip", 3))
o.append(tag(TXF, ly(T2, 2), "if 안 · 건너뛰어요", GRAY, 3))
o.append(hl(96, T2, 1100, 3, 1, "err", 4))
o.append(tag(TXF, ly(T2, 3), "4칸을 빼먹어서 if 밖이에요", RED, 4))
o.append(box(5, 96 + 95, oy(T2, 5, 0) - LH() / 2 - 2, tw("커피 나왔어요") + 40, LH() + 4, RED))
o.append(tag(TXF, oy(T2, 5, 0), "돈이 모자라도 커피가 나와요", RED, 5))
o.append(caption("오류 없이 결과만 틀려요. 들여쓰기 칸 수가 if의 범위를 정해요.", 960, 6))
CFS[0] = 30
W("i-indent", o, "if 안에 넣을 줄은 모두 같은 칸만큼 들여써요. 위 셀은 두 print를 모두 들여써서 돈이 모자라면 둘 다 건너뛰어요. 아래 셀은 커피 나왔어요를 들여쓰지 않았어요. 그 줄은 if 밖이라 조건과 상관없이 실행해서, 돈이 3000원인데도 커피가 나와요. 파이썬은 오류를 내지 않아서 직접 찾아야 해요. 다른 언어는 중괄호로 범위를 정하지만 파이썬은 들여쓰기로 정해요." + REAL)

o = [sec("i-else")] + head(EB2, "else는 조건이 False일 때 갈 길이에요", K2)
T = 230
LE = ["money = 3000", "if money >= price:", '    print("주문할 수 있어요")', "else:", '    print(f"{price - money}원 더 필요해요")']
o += cell({"id": "c-e", "lines": LE, "n": 5, "out": ["1500원 더 필요해요"]}, 96, T, 980, sel="c-e")
o.append(hl(96, T, 980, 2, 1, "skip", 1))
o.append(hl(96, T, 980, 4, 1, "run", 2))
o.append(under_tok(3, 96, T, 3, "", "else:", OR))
o.append(tag(96 + 105, ly(T, 4) + 160, "else 뒤에는 조건 없이 콜론만 붙이고, if와 같은 칸에 맞춰요", OR, 3, 28, False))
o.append(flow(1150, 230, 674, 640,
              [dict(x=150, y=0, w=374, h=170, kind="diamond", text="money >= price", color=K2, bg=K2BG, fs=26),
               dict(x=0, y=290, w=300, h=110, text='print("주문할\n수 있어요")', color="#9AA1AE", bg=CARD, fs=22, tc=SUB, order=1),
               dict(x=374, y=290, w=300, h=110, text='print(f"...원\n더 필요해요")', color=RED, bg=REDBG, fs=22, order=2),
               dict(x=137, y=520, w=400, h=90, text="다음 줄", color=GRAY, mono=False, order=2)],
              [dict(pts=[(150, 85), (150, 286)], color="#9AA1AE", order=1, label="True · if", lx=166, ly=196, fs=24),
               dict(pts=[(524, 85), (524, 286)], color=RED, order=2, label="False · else", lx=372, ly=196, fs=24),
               dict(pts=[(150, 402), (150, 460), (290, 460), (290, 516)], order=2), dict(pts=[(524, 402), (524, 460), (384, 460), (384, 516)], order=2)]))
o.append(caption("if와 else 중 하나만, 그리고 반드시 하나는 실행해요.", 960, 4))
W("i-else", o, "else는 조건이 False일 때 갈 길을 따로 정해요. 앞 장에서는 돈이 모자라면 아무 말도 하지 않았어요. else는 if와 같은 칸에 맞춰 적고, 조건 없이 콜론만 붙여요. 그 안은 다시 4칸 들여써요. money가 3000이라 조건이 False고, else 안의 print를 실행해요. 1500원은 price - money를 13의 f-string에 넣어 계산했어요." + REAL)

SALEL = ["if total >= 20000:", '    print("10% 할인")', "elif total >= 10000:", '    print("5% 할인")', "else:", '    print("할인 없음")']
o = [sec("i-elif")] + head(EB2, "elif로 갈림길을 셋 이상 만들어요", K2)
T = 210
o += cell({"id": "c-l", "lines": ["total = 12000"] + SALEL, "n": 6, "out": ["5% 할인"]}, 96, T, 960, sel="c-l")
o.append(hl(96, T, 960, 1, 1, "skip", 1, "False"))
o.append(hl(96, T, 960, 3, 2, "run", 2, "True · 실행"))
o.append(hl(96, T, 960, 5, 2, "skip", 3, "보지 않음"))
o += rows(96, 650, [380, 300], [["total = 25000", "10% 할인"], ["total = 12000", "5% 할인"], ["total = 3000", "할인 없음"]], ["total만 바꿔 실행", "출력"], 4, 70, 28, 3, ["code", "sans"])
o.append(flow(1150, 210, 674, 560,
              [dict(x=0, y=0, w=380, h=140, kind="diamond", text=">= 20000", color=K2, bg=K2BG, fs=26),
               dict(x=0, y=200, w=380, h=140, kind="diamond", text=">= 10000", color=K2, bg=K2BG, fs=26, order=1),
               dict(x=50, y=410, w=280, h=84, text="할인 없음", color=GRAY, mono=False, fs=26, order=3),
               dict(x=470, y=28, w=204, h=84, text="10%", color="#9AA1AE", mono=False, fs=28, tc=SUB),
               dict(x=470, y=228, w=204, h=84, text="5%", color=GR, bg=GRBG, mono=False, fs=28, order=2)],
              [dict(pts=[(382, 70), (466, 70)], color="#9AA1AE", label="True", lx=388, ly=24), dict(pts=[(190, 142), (190, 196)], color=RED, order=1, label="False", lx=210, ly=148),
               dict(pts=[(382, 270), (466, 270)], color=GR, order=2, label="True", lx=388, ly=224), dict(pts=[(190, 342), (190, 406)], color=RED, order=3, label="False", lx=210, ly=356)]))
o.append(caption("위에서부터 묻고, 처음 True인 하나만 실행해요.", 960, 5))
W("i-elif", o, "갈림길이 셋 이상이면 elif를 써요. else if를 줄인 말이에요. 2만 원 이상이면 10퍼센트, 1만 원 이상이면 5퍼센트, 나머지는 할인 없음이에요. total 12000은 20000 이상이 아니라 False라서 elif로 내려가요. 10000 이상은 True라서 5% 할인을 찍고, 아래 else는 보지도 않아요. 왼쪽 아래는 같은 셀을 total만 바꿔 실행한 결과예요. elif는 몇 개든 쓸 수 있고 else는 없어도 돼요." + REAL)

o = [sec("i-order")] + head(EB2, "조건 순서를 바꾸면 결과가 달라져요", K2)
T = 210
LO = ["total = 25000", "if total >= 10000:", '    print("5% 할인")', "elif total >= 20000:", '    print("10% 할인")', "else:", '    print("할인 없음")']
o += cell({"id": "c-o", "lines": LO, "n": 9, "out": ["5% 할인"]}, 96, T, 1000, sel="c-o")
TXO = 1160
o.append(hl(96, T, 1000, 1, 2, "err", 1))
o.append(tag(TXO, ly(T, 1.5), "25000은 10000 이상이라 여기서 True", RED, 1))
o.append(hl(96, T, 1000, 3, 2, "skip", 2))
o.append(tag(TXO, ly(T, 3.5), "묻지도 않아요", GRAY, 2))
o.append(ring_tok(3, 96, T, 0, "", "5% 할인", RED, out_n=7))
o.append(tag(TXO, oy(T, 7, 0), "25000원인데 5%예요", RED, 3))
o.append(fix(96, 720, "if total >= 10000:", "if total >= 20000:", 4, 30, "좁은 조건을 위에"))
o.append(p(f"position:absolute;left:96px;top:810px;width:1728px;font-size:28px;color:{SUB}", "앞 장의 순서로 바꾸면 25000은 10% 할인, 12000은 5% 할인이 돼요.", at(4)))
o.append(caption("범위가 겹치는 조건은 좁은 쪽부터 적어요.", 960, 5))
W("i-order", o, "elif는 위에서부터 묻고 처음 True에서 멈춰서, 조건 순서를 바꾸면 결과가 달라져요. 앞 장의 두 조건을 순서만 바꿨어요. total이 25000이면 첫 조건 10000 이상이 이미 True라서 5% 할인을 찍고, 아래의 20000 이상은 묻지도 않아요. 오류가 나지 않아서 틀린 줄 모르고 지나치기 쉬워요. 범위가 겹치는 조건은 좁은 쪽, 여기서는 큰 금액 조건을 위에 둬요." + REAL)

CFS[0] = 28
o = [sec("i-ifif")] + head(EB2, "if를 따로 쓰면 둘 다 실행될 수 있어요", K2)
TXF = 1160
T1, T2 = 210, 584
o += cell({"id": "c-ii", "lines": ["total = 25000", "if total >= 20000:", '    print("10% 할인")', "if total >= 10000:", '    print("5% 할인")'], "n": 10, "out": ["10% 할인", "5% 할인"]}, 96, T1, 1000, sel="c-ii")
o += cell({"id": "c-ie", "lines": ["total = 25000"] + SALEL, "n": 7, "out": ["10% 할인"]}, 96, T2, 1000, attrs=at(3, "rise"))
o.append(hl(96, T1, 1000, 1, 2, "run", 1))
o.append(hl(96, T1, 1000, 3, 2, "err", 1))
o.append(tag(TXF, ly(T1, 1.5), "갈림길 하나", INK, 1))
o.append(tag(TXF, ly(T1, 3.5), "갈림길 또 하나 · 다시 물어요", RED, 1))
o.append(box(2, 96 + 95, oy(T1, 5, 0) - LH() / 2 - 4, 200, 2 * LH() + 18, RED))
o.append(tag(TXF, oy(T1, 5, 0.5), "할인을 두 번 받아요", RED, 2))
o.append(hl(96, T2, 1000, 1, 2, "run", 4))
o.append(hl(96, T2, 1000, 3, 4, "skip", 4))
o.append(tag(TXF, ly(T2, 4.5), "elif · 처음 True에서 멈춰요", GR, 4))
o.append(caption("하나만 고르면 elif, 각각 따로 확인하면 if 여러 개예요.", 960, 5))
CFS[0] = 30
W("i-ifif", o, "if를 두 번 쓰면 갈림길이 두 개라서 둘 다 실행될 수 있어요. 위 셀은 첫 if가 True라 10% 할인을 찍고, 둘째 if를 다시 물어요. 25000은 10000 이상이기도 해서 5% 할인도 찍어요. 아래 셀은 elif라서 처음 True를 만나면 나머지는 보지 않아요. 할인처럼 하나만 골라야 하면 elif를 써요. 회원 쿠폰과 생일 쿠폰처럼 각각 따로 확인할 일이면 if를 여러 번 써요. 아래 셀 [7]은 elif 장에서 total을 25000으로 바꿔 실행한 결과예요." + REAL)

# ---------- part 3 ----------
o = [sec("i-and")] + head(EB3, "and는 두 조건이 모두 True일 때만 True예요", K3)
RIDE = ["if height >= 120 and age >= 7:", '    print("탈 수 있어요")', "else:", '    print("다음에 타요")']
T1, T2 = 210, 580
o += cell({"id": "c-a1", "lines": ["height = 130", "age = 9"] + RIDE, "n": 1, "out": ["탈 수 있어요"]}, 96, T1, 960, sel="c-a1")
o += cell({"id": "c-a2", "lines": ["height = 110"] + RIDE, "n": 2, "out": ["다음에 타요"]}, 96, T2, 960, attrs=at(4, "rise"))
o += chain([("130 >= 120", "True", "키"), ("9 >= 7", "True", "나이"), ("True and True", "True", "and")], 1130, T1 + 20, 1, K3, 80)
o += chain([("110 >= 120", "False", "키"), ("9 >= 7", "True", "나이"), ("False and True", "False", "and")], 1130, T2 + 10, 4, K3, 80)
o.append(caption("12의 놀이기구 조건을 if에 넣어 실행할 줄을 골라요.", 960, 7))
W("i-and", o, "and로 이은 조건은 둘 다 True일 때만 True예요. 12에서 놀이기구 탑승 조건을 키 120 이상 그리고 7살 이상으로 적었어요. 그때는 True, False를 보기만 했는데, 이제 if에 넣어서 실행할 줄을 골라요. 위 셀은 두 비교가 모두 True라서 탈 수 있어요. 아래 셀은 키만 110으로 바꿨고, age는 앞 셀의 9가 그대로예요. 키가 False라 and 전체가 False고 else로 가요. 비교를 먼저 계산하고 and를 나중에 해서 괄호가 없어도 돼요." + NEWK + REAL, ("p3", "조건 합치기"))

CFS[0] = 34
o = [sec("i-nested")] + head(EB3, "if 안의 if는 and 한 줄로 줄일 수 있어요", K3)
T1, T2 = 220, 620
o += cell({"id": "c-n", "lines": ["height = 130", "if height >= 120:", "    if age >= 7:", '        print("탈 수 있어요")'], "n": 3, "out": ["탈 수 있어요"]}, 96, T1, 1000, sel="c-n")
o.append(hl(96, T1, 1000, 2, 1, "mark", 1))
o.append(tag(TXF, ly(T1, 2), "4칸 · 바깥 if가 True일 때만 물어요", BL, 1))
o.append(hl(96, T1, 1000, 3, 1, "run", 2))
o.append(tag(TXF, ly(T1, 3), "8칸 · 둘 다 True일 때만 실행", GR, 2))
o.append(p(f"position:absolute;left:96px;top:{T2 - 66}px;font-size:28px;font-weight:700;color:{K3}", "and로 줄이면", at(3)))
o += cell({"id": "c-n2", "lines": ["if height >= 120 and age >= 7:", '    print("탈 수 있어요")'], "n": None, "out": ["탈 수 있어요"]}, 96, T2, 1000, attrs=at(3, "rise"))
o.append(tag(TXF, oy(T2, 2, 0), "셀 [1]과 같은 결과, 들여쓰기는 한 번", K3, 4))
o.append(caption("들여쓰기가 깊어지면 and로 합칠 수 있는지 먼저 봐요.", 960, 5))
CFS[0] = 30
W("i-nested", o, "if 안에 다시 if를 넣을 수 있고, 할 일이 한 군데뿐이면 and 한 줄로 줄일 수 있어요. 바깥 if가 True일 때만 안쪽 if를 물어요. 안쪽 if의 줄은 4칸을 한 번 더 들여써서 8칸이에요. 키가 120 이상이고 나이가 7 이상이어야 실행하니 and로 이은 조건과 같아요. 아래처럼 한 줄로 적으면 들여쓰기가 얕아져서 읽기 쉬워요. 메뉴판에 있으면 먼저 가격을 찍고 그다음 5000원 이하인지 다시 묻는 것처럼, 바깥 조건이 맞은 뒤에 따로 할 일이 있을 때는 안쪽 if가 필요해요." + REAL)

CFS[0] = 34
o = [sec("i-or")] + head(EB3, "or는 하나만 True여도 True예요", K3)
T = 220
o += cell({"id": "c-or", "lines": ["is_member = False", "total = 60000", "if is_member or total >= 50000:", '    print("할인해 드려요")'], "n": 4, "out": ["할인해 드려요"]}, 96, T, 960, sel="c-or")
o += chain([("is_member", "False", "회원"), ("60000 >= 50000", "True", "금액"), ("False or True", "True", "or")], 96, 580, 1, K3, 88, 30)
o += rows(1170, T, [150, 150, 150, 150], [["True", "True", "True", "True"], ["True", "False", "False", "True"], ["False", "True", "False", "True"], ["False", "False", "False", "False"]],
          ["앞", "뒤", "and", "or"], 4, 84, 26, 4, ["tf", "tf", "tf", "tf"])
o.append(box(5, 1170 + 3 * 174 - 12, T + 58 + 3 * 84 + 42 - 28, 118, 56, RED))
o.append(tag(1170, T + 58 + 4 * 84 + 60, "or가 False인 건 둘 다 False일 때뿐이에요", RED, 5, 26, False))
o.append(caption("말로 '그리고'면 and, '또는'이면 or를 써요.", 960, 6))
CFS[0] = 30
W("i-or", o, "or로 이은 조건은 둘 중 하나만 True여도 True예요. 12의 할인 조건을 if에 넣었어요. 회원이거나 5만 원 이상 사면 할인해요. 회원은 아니라 False지만 금액이 True라서 전체가 True예요. 오른쪽 표는 and와 or를 나란히 놓았어요. and는 둘 다 True여야 True고, or는 둘 다 False여야 False예요. 조건을 말로 먼저 적어 보고 그리고로 이어지면 and, 또는으로 이어지면 or를 써요." + REAL)

CFS[0] = 32
o = [sec("i-not")] + head(EB3, "not과 not in으로 반대를 물어요", K3)
T = 220
LN = [MENU, 'order = "tea"', "if not order in menu:", '    print("메뉴판에 없어요")', "if order not in menu:", '    print("메뉴판에 없어요")']
o += cell({"id": "c-not", "lines": LN, "n": 5, "out": ["메뉴판에 없어요", "메뉴판에 없어요"]}, 96, T, 1150, sel="c-not")
o.append(hl(96, T, 1150, 2, 1, "mark", 1, "not (in)"))
o += chain([('"tea" in menu', "False", "in"), ("not False", "True", "not")], 1300, T + 10, 1, K3, 84, 28, 70)
o.append(hl(96, T, 1150, 4, 1, "run", 2, "not in"))
o.append(p(f"position:absolute;left:1300px;top:{T + 210}px;width:524px;font-size:28px;font-weight:700;line-height:1.5;color:{K3}", "결과는 같아요. 문장처럼 읽히는 not in을 더 많이 써요.", at(2)))
o.append(tag(96 + 105, oy(T, 6, 1) + 100, "없을 때만 할 일이 있으면 else 대신 조건을 뒤집어요. 1파트 처음의 KeyError를 막는 첫 방법이에요.", SUB, 3, 28, False, w=1600))
o.append(caption("\"없으면\"은 not in, \"아니면\"은 !=로 적어요.", 960, 4))
CFS[0] = 30
W("i-not", o, "not은 True와 False를 뒤집고, not in은 들어 있지 않은지 물어요. tea in menu는 False라서 not을 붙이면 True가 되고, 메뉴판에 없어요를 찍어요. 14의 not in으로 적어도 결과는 같은데, 영어 문장처럼 읽혀서 실제로는 not in을 많이 써요. 메뉴판에 없을 때만 할 일이 있으면 else를 쓰지 않고 조건을 뒤집어요. 1파트 처음의 KeyError는 이렇게 먼저 물어서 막을 수 있어요." + REAL)

o = [sec("i-range")] + head(EB3, "범위는 9 <= hour < 18처럼 이어 적어요", K3)
# the opening hours as a number line: the hero of the slide
NX, NY, NW = 96, 220, 116
o.append(p(f"position:absolute;left:{NX}px;top:{NY}px;font-size:26px;font-weight:700;color:{K3}", "영업시간 · 9시부터 18시 전까지"))
for i, h_ in enumerate(range(7, 21)):
    inside = 9 <= h_ < 18
    o.append(p(f"position:absolute;left:{NX + i * (NW + 8)}px;top:{NY + 52}px;width:{NW}px;height:80px;border-radius:14px;border:3px solid {K3 if inside else LINE};background:{K3BG if inside else CARD};"
               f"font-family:{MONO};font-size:30px;font-weight:700;line-height:74px;text-align:center;color:{INK if inside else GRAY}", str(h_), at(1) if inside else ""))
o.append(tag(NX + 2 * (NW + 8), NY + 176, "9는 들어가요 (<=)", GR, 2, 26, False))
o.append(tag(NX + 11 * (NW + 8) - 80, NY + 176, "18은 빠져요 (<)", RED, 2, 26, False))
o.append(ring(2, NX + 2 * (NW + 8), NY + 52, NW, 80, GR))
o.append(ring(2, NX + 11 * (NW + 8), NY + 52, NW, 80, RED))
T1 = 470
CFS[0] = 32
o += cell({"id": "c-r1", "lines": ["hour = 14", "if 9 <= hour < 18:", '    print("영업 중이에요")', "if hour >= 9 and hour < 18:", '    print("영업 중이에요")'], "n": 6, "out": ["영업 중이에요", "영업 중이에요"]}, 96, T1, 860, sel="c-r1", attrs=at(3, "rise"))
o.append(hl(96, T1, 860, 1, 1, "run", 3, "줄인 방법"))
o.append(hl(96, T1, 860, 3, 1, "skip", 3, "원래 방법", GRAY))
o += cell({"id": "c-r2", "lines": ["hour = 20", "if 9 <= hour < 18:", '    print("영업 중이에요")', "else:", '    print("문 닫았어요")'], "n": 7, "out": ["문 닫았어요"]}, 964, T1, 860, attrs=at(4, "rise"))
o.append(caption("\"사이에 있나요?\"는 작은 값 <= 변수 < 큰 값으로 물어요.", 960, 5))
CFS[0] = 30
W("i-range", o, "가운데에 변수를 두고 양쪽에 경계를 적으면 범위를 한 번에 물을 수 있어요. 가게가 9시부터 18시 전까지 열어요. 파이썬은 수학 부등식처럼 9 <= hour < 18로 이어 적을 수 있고, hour >= 9 and hour < 18과 결과가 같아요. 9는 작거나 같다라서 들어가고, 18은 작다라서 빠져요. 경계 숫자가 들어가는지는 등호가 있는지로 정해요. 20시는 범위 밖이라 else로 가요." + REAL)

CFS[0] = 34
o = [sec("i-truthy")] + head(EB3, "비어 있는 값은 False로 봐요", K3)
T = 220
o += cell({"id": "c-t", "lines": ["print(bool(0), bool(4500))", 'print(bool(""), bool("tea"))', 'print(bool([]), bool(["tea"]))', "print(bool({}), bool(set()))", "print(bool(None))"], "n": 8,
           "out": ["False True", "False True", "False True", "False False", "False"]}, 96, T, 860, sel="c-t")
o += rows(1040, T, [240, 230, 270], [["숫자", "0", "4500"], ["문자열", '""', '"tea"'], ["리스트", "[]", '["tea"]'], ["딕셔너리, 집합", "{}  set()", '{"tea"}'], ["15의 None", "None", ""]],
          ["종류", "False로 봐요", "True로 봐요"], 1, 110, 30, 5, ["sans", "code", "code"])
o.append(box(2, 1040 + 264 - 14, T + 58 + 8, 230 + 20, 5 * 110 - 16, RED))
o.append(tag(1040 + 264 - 14, T + 58 + 5 * 110 + 40, "0과 빈 것, None만 False예요", RED, 2, 28, False))
o.append(caption("bool(값)은 그 값을 if에 넣었을 때 True로 볼지 False로 볼지 알려 줘요.", 960, 3))
CFS[0] = 30
W("i-truthy", o, "0, 빈 문자열, 빈 리스트, 빈 딕셔너리, 빈 집합, None은 if에서 False로 보고 나머지는 모두 True로 봐요. if 뒤에 비교식이 아니라 값을 그냥 적어도 돼요. bool()에 넣어 보면 파이썬이 그 값을 어떻게 보는지 알 수 있어요. 숫자는 0만, 문자열은 빈 문자열만 False예요. 리스트, 딕셔너리, 집합은 비어 있으면 False예요. 15의 get에서 본 None도 False예요. 12의 int(), str()처럼 bool()도 값을 bool로 바꿔 주는 함수예요." + REAL)

CFS[0] = 32
o = [sec("i-empty")] + head(EB3, "if orders:는 하나라도 있는지 묻는 거예요", K3)
T = 210
LEM = ["orders = []", "if orders:", '    print(len(orders), "잔 주문")', "else:", '    print("아직 주문이 없어요")', "if len(orders) > 0:", '    print(len(orders), "잔 주문")', "else:", '    print("아직 주문이 없어요")']
o += cell({"id": "c-em", "lines": LEM, "n": 9, "out": ["아직 주문이 없어요", "아직 주문이 없어요"]}, 96, T, 1040, sel="c-em")
TXE = 1200
o.append(hl(96, T, 1040, 1, 1, "run", 1))
o.append(tag(TXE, ly(T, 1), "줄인 방법 · 빈 리스트는 False", K3, 1))
o.append(hl(96, T, 1040, 5, 1, "skip", 2))
o.append(tag(TXE, ly(T, 5), "원래 방법 · 뜻이 더 잘 보여요", GRAY, 2))
o.append(tag(TXE, oy(T, 9, 0.5), "두 방법 모두 else로 가요", INK, 3))
o.append(caption("처음엔 len(orders) > 0으로 적어도 돼요. if orders:는 읽을 수 있으면 돼요.", 960, 4))
W("i-empty", o, "if orders:는 주문이 하나라도 있으면이라고 읽어요. orders가 빈 리스트면 False로 봐서 else로 가요. 하나라도 들어 있으면 True로 봐서 if 안을 실행해요. 아래 if는 같은 일을 len으로 길게 쓴 거라 결과가 같아요. 처음에는 len(orders) > 0이 뜻이 더 잘 보여요. 실제 코드에서는 if orders:를 자주 만나니 읽을 수 있으면 돼요. 6파트 영수증 실습에서 이 모양을 써요." + REAL)
CFS[0] = 30

# ---------- part 4 ----------
o = [sec("f-pick")] + head(EB4, "for 안의 if로 골라 담아요", K4)
T = 210
LP = [MENU, "prices = [4500, 5000, 6500, 4000]", "cheap = []", "for p in prices:", "    if p <= 5000:", "        cheap.append(p)", "print(cheap)"]
o += cell({"id": "c-p", "lines": LP, "n": 1, "out": ["[4500, 5000, 4000]"]}, 96, T, 1300, sel="c-p")
o.append(hl(96, T, 1300, 4, 1, "mark", 1, "if는 for 안 · 4칸"))
o.append(hl(96, T, 1300, 5, 1, "run", 1, "append는 if 안 · 8칸"))
# prices row under the cell; each value that passes flies right into cheap
PX, PY, SW = 96 + 105, 690, 132
o.append(p(f"position:absolute;left:{PX}px;top:{PY - 50}px;font-family:{MONO};font-size:28px;font-weight:700;color:{GRAY}", "prices"))
for i, v in enumerate(["4500", "5000", "6500", "4000"]):
    o.append(p(f"position:absolute;left:{PX + i * (SW + 10)}px;top:{PY}px;width:{SW}px;height:84px;border-radius:14px;border:3px solid {LINE};background:{CARD};font-family:{MONO};font-size:30px;font-weight:700;line-height:78px;text-align:center;color:{INK}", v, f' id="pr{i}"'))
for i, ok in enumerate([True, True, False, True]):
    o.append(p(f"position:absolute;left:{PX + i * (SW + 10)}px;top:{PY + 100}px;width:{SW}px;text-align:center;font-family:{MONO};font-size:24px;font-weight:700;color:{GR if ok else RED}", "<= 5000" if ok else "건너뜀", at(2)))
CX0 = 1100
o.append(p(f"position:absolute;left:{CX0}px;top:{PY - 50}px;font-family:{MONO};font-size:28px;font-weight:700;color:{K4}", "cheap", at(3)))
o.append(f'<div{at(3)} style="position:absolute;left:{CX0}px;top:{PY - 8}px;width:{4 * SW + 48}px;height:100px;border-radius:16px;border:3px dashed {K4}"></div>')
for k, i in enumerate([0, 1, 3]):
    o.append(p(f"position:absolute;left:{CX0 + 9 + k * (SW + 10)}px;top:{PY}px;width:{SW}px;height:84px;border-radius:14px;border:3px solid {K4};background:{K4BG};font-family:{MONO};font-size:30px;font-weight:700;line-height:78px;text-align:center;color:{INK}",
               ["4500", "5000", "4000"][k], f' data-build-in="fly order {4 + k}" data-from="pr{i}"'))
o.append(tag(CX0, PY + 136, "True인 값만 append해요", K4, 6, 28, False))
o.append(caption("빈 리스트, for, if, append가 골라 담기의 기본 모양이에요.", 960, 7))
W("f-pick", o, "for로 하나씩 꺼내면서 if로 물으면 조건에 맞는 값만 골라 담을 수 있어요. 메뉴 가격 중 5000원 이하만 새 리스트에 담아요. 빈 리스트 cheap을 만들고, for로 가격을 하나씩 꺼내요. 꺼낼 때마다 if로 5000 이하인지 묻고, True면 append해요. 6500은 False라 건너뛰어요. if는 for 안에 있어서 4칸, append는 if 안에 있어서 8칸 들여써요. 첫 줄의 menu는 이 파트의 뒤 셀에서 써요." + NEWK + REAL, ("p4", "for와 함께, 줄여 쓰기"))

o = [sec("f-count")] + head(EB4, "조건에 맞는 것만 세요", K4)
T = 210
LC = ['orders = ["coffee", "latte", "coffee", "cake", "tea", "coffee"]', "n = 0", "for o in orders:", '    if o == "coffee":', "        n += 1", "print(n)", 'print(orders.count("coffee"))']
o += cell({"id": "c-c", "lines": LC, "n": 2, "out": ["3", "3"]}, 96, T, 1280, sel="c-c")
o.append(hl(96, T, 1280, 4, 1, "run", 1, "True일 때만 1 더하기"))
steps_ = [("coffee", "True", "1"), ("latte", "False", "1"), ("coffee", "True", "2"), ("cake", "False", "2"), ("tea", "False", "2"), ("coffee", "True", "3")]
o += rows(1436, T, [150, 130, 50], [list(s) for s in steps_], ["o", '== "coffee"', "n"], 2, 92, 28, 6, ["code", "tf", "code"], ids=[f"cnt{i}" for i in range(6)])
for k, i in enumerate([0, 2, 5]):
    o.append(spot(3 + k, target=f"cnt{i}", pad=6, r=10, dim=0.45))
o.append(spot_off(6))
o.append(tag(tx(96, ['print(orders.count("coffee"))']), oy(T, 7, 1), "같은 값 하나는 count로 바로 세요", K4, 6))
o.append(caption("세기는 n = 0에서 시작해서, 조건이 True일 때 n += 1이에요.", 960, 7))
W("f-count", o, "n을 0으로 두고 조건이 True일 때만 1을 더하면 조건에 맞는 개수를 셀 수 있어요. 주문 중 coffee가 몇 잔인지 세요. 오른쪽 표처럼 coffee를 만날 때마다 n이 1, 2, 3으로 늘어요. 같은 값 하나를 셀 때는 13의 count로 한 줄이면 되고 결과도 3으로 같아요. 그래도 for와 if를 알아야 하는 이유는 가격이 5000원 이상인 주문처럼 조건이 붙은 개수는 count로 못 세기 때문이에요." + REAL)

o = [sec("f-dict")] + head(EB4, "딕셔너리에서 조건에 맞는 메뉴를 찾아요", K4)
CFS[0] = 34
T = 220
LD = ["for name, price in menu.items():", "    if price <= 5000:", "        print(name, price)"]
o += cell({"id": "c-d", "lines": LD, "n": 3, "out": ["coffee 4500", "latte 5000"]}, 96, T, 820, sel="c-d")
o.append(hl(96, T, 820, 1, 1, "run", 1))
o.append(tag(96 + 820 + 40, ly(T, 1), "값 price로 물어요", K4, 1))
# the menu as lockers: key on the door, value inside
LKX, LKY, LKW = 96, 610, 380
for i, (k, v, ok) in enumerate([("coffee", "4500", True), ("latte", "5000", True), ("cake", "6500", False)]):
    x = LKX + i * (LKW + 40)
    o.append(f'<div style="position:absolute;left:{x}px;top:{LKY}px;width:{LKW}px;height:150px;border-radius:16px;border:3px solid #C9CED8;background:{CARD};display:flex;flex-direction:column;overflow:hidden">'
             + p(f"height:54px;flex:none;background:#ECEAE3;font-family:{MONO};font-size:28px;font-weight:700;line-height:54px;text-align:center;color:{INK}", e(k))
             + '<div style="flex:1;display:flex;align-items:center;justify-content:center">' + p(f"font-family:{MONO};font-size:40px;font-weight:700;color:{INK}", v) + '</div></div>')
    o.append(p(f"position:absolute;left:{x}px;top:{LKY + 170}px;width:{LKW}px;text-align:center;font-family:{MONO};font-size:26px;font-weight:700;color:{GR if ok else RED}",
               ("<= 5000 → 찍어요" if ok else "6500 → 건너뛰어요"), at(2 + (0 if ok else 1))))
o.append(tag(LKX + 3 * (LKW + 40) + 10, LKY + 75, "키로 물을 땐", K4, 4, 26, False))
o.append(tag(LKX + 3 * (LKW + 40) + 10, LKY + 117, 'if name == "cake":', K4, 4, 26, False))
o.append(caption("for k, v in d.items(): 안에서 if로 키나 값을 물어요.", 960, 5))
CFS[0] = 30
W("f-dict", o, "15의 items()로 키와 값을 한 쌍씩 꺼내고, if로 조건에 맞는 쌍만 골라요. 꺼낼 때마다 가격이 5000 이하인지 물어요. coffee와 latte는 True라서 찍고, cake는 6500이라 건너뛰어요. 조건에는 키도 값도 쓸 수 있어요. 품절 메뉴 찾기나 5000원 이하 메뉴 추천에 이 모양을 써요. 이름에 te가 들어간 메뉴를 찾으려면 14의 in을 문자열에 써서 te in name으로 물어요. 앞 셀의 menu를 그대로 썼어요." + REAL)

o = [sec("f-oneline")] + head(EB4, "if와 else를 한 줄로 줄여 쓸 수 있어요", K4)
T = 200
L1L = ["total = 12000", "if total >= 10000:", '    msg = "5% 할인"', "else:", '    msg = "할인 없음"', "print(msg)", 'msg = "5% 할인" if total >= 10000 else "할인 없음"', "print(msg)"]
o += cell({"id": "c-1l", "lines": L1L, "n": 4, "out": ["5% 할인", "5% 할인"]}, 96, T, 1300, sel="c-1l")
o.append(hl(96, T, 1300, 1, 4, "skip", 1, "원래 방법 · 4줄", GRAY))
o.append(hl(96, T, 1300, 6, 1, "run", 2, "줄인 방법 · 1줄"))
# the one-liner read part by part, underlined like an instructor would
BIG = 40
BX, BY = 96, 790
ONE = ['msg = ', '"5% 할인"', ' if total >= 10000', ' else "할인 없음"']
o.append(p(f"position:absolute;left:{BX}px;top:{BY}px;font-family:{MONO};font-size:{BIG}px;font-weight:700;line-height:1.3;white-space:pre;color:{INK}", e("".join(ONE)), at(3, "rise")))
xs = [BX]
for s_ in ONE:
    xs.append(xs[-1] + tw(s_, BIG))
for k, (col, lab) in enumerate([(GR, "True일 때 값"), (BL, "조건"), (RED, "False일 때 값")]):
    a, b = xs[k + 1] + (0 if k == 0 else tw(" ", BIG)), xs[k + 2]
    o.append(underline(4 + k, int(a), int(b), BY + 62, col))
    o.append(p(f"position:absolute;left:{a:.0f}px;top:{BY + 78}px;font-size:26px;font-weight:700;color:{col};white-space:nowrap", e(lab), at(4 + k)))
o.append(caption("변수에 둘 중 하나를 넣을 때만 줄여요.", 960, 7))
W("f-oneline", o, "값1 if 조건 else 값2는 조건이 True면 값1, 아니면 값2라는 뜻이에요. if와 else로 변수에 둘 중 하나를 넣는 모양은 아주 자주 나와서 한 줄로 줄이는 방법이 있어요. True일 때 값을 먼저 쓰고, if 조건, else False일 때 값 순서로 적어요. 결과는 4줄짜리와 같아요. 실행할 줄이 여러 개이거나 갈림길이 셋 이상이면 원래 모양이 읽기 쉬워요. 처음엔 4줄로 적고, 남의 코드에서 한 줄 모양을 만나면 읽을 수 있으면 돼요." + REAL)

CFS[0] = 34
o = [sec("f-get")] + head(EB4, "15의 get을 이제 if로 풀어서 읽어요", K4)
T = 210
LG = ['if "cakee" in menu:', '    price = menu["cakee"]', "else:", "    price = 5000", "print(price)", 'print(menu["cakee"] if "cakee" in menu else 5000)', 'print(menu.get("cakee", 5000))']
o += cell({"id": "c-g", "lines": LG, "n": 5, "out": ["5000", "5000", "5000"]}, 96, T, 1180, sel="c-g")
TXG = 1330
o.append(hl(96, T, 1180, 0, 4, "skip", 1))
o.append(tag(TXG, ly(T, 1.5), "1 · if, else 4줄 · 이번 챕터", INK, 1))
o.append(hl(96, T, 1180, 5, 1, "skip", 2))
o.append(tag(TXG, ly(T, 5), "2 · 한 줄 if else · 15 참고 칸", INK, 2))
o.append(hl(96, T, 1180, 6, 1, "run", 3))
o.append(tag(TXG, ly(T, 6), "3 · get · 15", K4, 3))
o.append(box(4, 96 + 95, oy(T, 7, 0) - LH() / 2 - 4, 124, 3 * LH() + 28, GR))
o.append(tag(96 + 260, oy(T, 7, 1), "세 방법 모두 5000", GR, 4))
o.append(caption("get은 위의 if, else를 대신해 주는 메서드예요. 실제로는 get을 써요.", 960, 5))
CFS[0] = 30
W("f-get", o, "15에서 배운 get은 if와 else 4줄을 대신해 주는 메서드예요. 15에서 get을 배울 때 같은 뜻의 한 줄 if else 코드를 참고 칸에 두고 읽기만 했어요. 이제 그 코드를 풀어서 if와 else 4줄로 쓸 수 있어요. cakee가 메뉴판에 있으면 그 가격, 없으면 5000이에요. 세 방법 모두 5000을 찍어요. 짧을수록 실수할 곳이 줄어서 실제로는 get을 쓰고, 4줄짜리는 get이 무슨 일을 하는지 이해하는 데 써요." + REAL)

o = [sec("f-set")] + head(EB4, "16에서 읽기만 한 코드를 직접 쳐 봐요", K4)
CFS[0] = 34
T = 280
o.append(p(f"position:absolute;left:96px;top:{T - 64}px;font-size:30px;font-weight:700;color:{K4}", "discard = 있으면 remove"))
o += cell({"id": "c-s1", "lines": ['menus = {"coffee", "cake"}', 'if "juice" in menus:', '    menus.remove("juice")', "print(sorted(menus))", 'menus.discard("juice")', "print(sorted(menus))"], "n": 6, "out": ["['cake', 'coffee']", "['cake', 'coffee']"]}, 96, T, 840, sel="c-s1")
o.append(p(f"position:absolute;left:984px;top:{T - 64}px;font-size:30px;font-weight:700;color:{K4}", "set() = 없을 때만 append", at(3)))
o += cell({"id": "c-s2", "lines": ["kinds = []", "for o in orders:", "    if o not in kinds:", "        kinds.append(o)", "print(kinds)", "print(sorted(set(orders)))"], "n": 7, "out": ["['coffee', 'latte', 'cake', 'tea']", "['cake', 'coffee', 'latte', 'tea']"]}, 984, T, 840, attrs=at(3, "rise"))
o.append(hl(96, T, 840, 1, 2, "run", 1, "원래 방법"))
o.append(hl(96, T, 840, 4, 1, "mark", 2, "줄인 방법"))
o.append(hl(984, T, 840, 0, 4, "run", 4, "원래 방법"))
o.append(hl(984, T, 840, 5, 1, "mark", 5, "줄인 방법"))
o.append(tag(984 + 105, oy(T, 6, 1) + 64, "리스트는 처음 나온 순서, 집합은 sorted() 순서예요", SUB, 6, 26, False))
o.append(caption("16의 \"참고, 읽기만\" 칸은 이제 모두 직접 칠 수 있어요.", 960, 7))
CFS[0] = 30
W("f-set", o, "16에서 읽기만 한 discard와 중복 없애기의 원래 코드를 이제 if로 직접 쳐요. 왼쪽은 discard예요. juice가 들어 있는지 먼저 묻고 있을 때만 remove해요. juice는 없어서 아무 일도 없고, discard 한 줄과 결과가 같아요. 오른쪽은 set(orders)로 중복을 없앤 일을 리스트로 직접 한 거예요. 아직 kinds에 없을 때만 append해요. 리스트는 처음 나온 순서를 지키고 집합은 sorted로 줄 세워서 순서가 다르지만, 담긴 값은 같아요. orders는 셀 [2]의 주문 리스트예요. 16의 교집합, 차집합 긴 코드도 같은 방법으로 직접 쳐 볼 수 있어요." + REAL)

# ---------- part 5 ----------
CFS[0] = 32
o = [sec("e-eq")] + head(EB5, "if 뒤에는 = 하나가 아니라 == 두 개예요", K5)
T = 220
EQO = ["Cell In[1], line 2", "SyntaxError: invalid syntax. Maybe you meant '==' or ':=' instead of '='?"]
o += cell({"id": "c-x1", "lines": ['order = "coffee"', 'if order = "coffee":', '    print("커피예요")'], "n": 1, "out": EQO, "err": True}, 96, T, 1728, sel="c-x1")
o.append(hl(96, T, 1728, 1, 1, "err", 1))
o.append(under_tok(1, 96, T, 0, "Cell In[1], ", "line 2", OR, out_n=3))
o.append(tag(cx(96, "Cell In[1], line 2") + 30, oy(T, 3, 0), "둘째 줄이 문제예요", OR, 1))
o.append(under_tok(2, 96, T, 1, "SyntaxError: invalid syntax. ", "Maybe you meant '=='", GR, out_n=3))
o.append(tag(cx(96, "SyntaxError: invalid syntax. "), oy(T, 3, 1) + 56, "\"== 를 쓰려던 거 아니에요?\" · := 는 배우지 않은 기호예요", GR, 2, 26, False))
o.append(fix(96, 650, 'if order = "coffee":', 'if order == "coffee":', 3, 34))
o.append(p(f"position:absolute;left:96px;top:756px;width:1728px;font-size:30px;font-weight:700;color:{INK}", "= 하나는 넣기, == 두 개는 묻기 (12)", at(4)))
o.append(p(f"position:absolute;left:96px;top:816px;width:1728px;font-size:28px;color:{SUB}", "SyntaxError는 실행 전에 문법을 검사하다 나서, 셀의 어느 줄도 실행되지 않아요.", at(4)))
o.append(caption("SyntaxError가 나면 line 숫자의 줄부터 봐요.", 960, 5))
CFS[0] = 30
W("e-eq", o, "if 뒤에 = 하나를 쓰면 SyntaxError가 나고, == 두 개로 고쳐요. 12에서 = 하나는 넣기, == 두 개는 묻기라고 배웠어요. 오류 위쪽의 line 2는 둘째 줄이 문제라는 뜻이에요. 마지막 줄은 ==를 쓰려던 거 아니냐고 고칠 곳까지 알려 줘요. :=는 배우지 않은 기호라 신경 쓰지 않아요. SyntaxError는 실행 전에 문법을 검사하다 나서 첫 줄의 order도 만들어지지 않아요." + NEWK + REAL, ("p5", "자주 나는 오류"))

o = [sec("e-colon")] + head(EB5, "콜론과 들여쓰기를 빠뜨리면 실행 전에 멈춰요", K5)
CFS[0] = 28
errs = [("c-x2", ['if order == "coffee"', '    print("커피예요")'], 2, ["SyntaxError: expected ':'"], "콜론이 없어요", "if 줄 끝에 :"),
        ("c-x3", ['if order == "coffee":', 'print("커피예요")'], 3, ["IndentationError: expected an indented block after 'if' statement on line 1"], "if 안에 들여쓴 줄이 없어요", "print 앞에 4칸"),
        ("c-x4", ['if order == "coffee":', '    print("커피예요")', '      print("나왔어요")'], 4, ["IndentationError: unexpected indent"], "들여쓰기 칸 수가 달라요", "같은 칸(4칸)에 맞추기")]
y = 206
for i, (cid, lines, n_, out, why, fx) in enumerate(errs):
    hh = cell_h({"lines": lines, "out": out})
    o += cell({"id": cid, "lines": lines, "n": n_, "out": out, "err": True}, 96, y, 1400, attrs=at(i + 1, "rise"))
    o.append(p(f"position:absolute;left:1540px;top:{y + 4}px;width:284px;font-size:26px;font-weight:700;line-height:1.35;color:{RED}", e(why), at(i + 1)))
    o.append(p(f"position:absolute;left:1540px;top:{y + 84}px;font-size:24px;font-weight:700;color:{INK};background:{GRBG};border:3px solid {GR};border-radius:12px;padding:4px 14px;white-space:nowrap", e(fx), at(i + 1)))
    y += hh + 34
o.append(ring(4, 96 + 105 + tw('if order == "coffee"') + 26, 206 + 10 + 4, 22, LH() - 8, RED))
CFS[0] = 30
o.append(caption("IndentationError는 들여쓰기 오류예요. 칸 수를 4칸에 맞춰요.", 960, 5))
W("e-colon", o, "콜론을 빠뜨리면 SyntaxError, 들여쓰기가 틀리면 IndentationError가 나고 둘 다 실행 전에 멈춰요. 1번은 if 줄 끝의 콜론이 없어서 expected 콜론이라고 정확히 알려 줘요. 2번은 if 다음 줄을 들여쓰지 않았어요. if 안에 들여쓴 줄이 하나는 있어야 해요. 3번은 같은 if 안에서 칸 수가 4칸, 6칸으로 달라요. unexpected indent는 생각지 못한 들여쓰기라는 뜻이에요. 오류 위쪽의 Cell In 줄은 빼고 마지막 줄만 옮겼어요." + REAL)

o = [sec("e-or")] + head(EB5, "or 뒤에도 비교를 다시 적어요", K5)
T1, T2 = 210, 560
LX5 = ['order = "cake"', 'if order == "coffee" or "latte":', '    print("커피 종류예요")', 'print(order == "coffee" or "latte")']
o += cell({"id": "c-x5", "lines": LX5, "n": 5, "out": ["커피 종류예요", "latte"]}, 96, T1, 1000, sel="c-x5")
o.append(under_tok(1, 96, T1, 1, 'if order == "coffee" ', 'or "latte"', RED))
o.append(tag(TXF, ly(T1, 1), "cake인데 커피 종류래요", RED, 1))
o += chain([('order == "coffee"', "False", "앞"), ('False or "latte"', None, "or"), ('"latte"', None, "결과")], TXF, T1 + 96, 2, K5, 64, 26, 70)
o.append(tag(TXF + 88 + tw('"latte"', 26) + 24, T1 + 96 + 2 * 64 + 26, "빈 글자가 아니라 True로 봐요", RED, 4, 26))
o += cell({"id": "c-x6", "lines": ['if order == "coffee" or order == "latte":', '    print("커피 종류예요")', "else:", '    print("커피 종류가 아니에요")', 'print(order in ["coffee", "latte"])'], "n": 6, "out": ["커피 종류가 아니에요", "False"]}, 96, T2, 1000, attrs=at(5, "rise"))
o.append(hl(96, T2, 1000, 0, 1, "run", 5))
o.append(tag(TXF, ly(T2, 0), "비교를 둘 다 적거나", GR, 5))
o.append(hl(96, T2, 1000, 4, 1, "run", 6))
o.append(tag(TXF, ly(T2, 4), "in과 리스트로 물어요", GR, 6))
o.append(caption("말로는 \"coffee 또는 latte\"지만 코드는 order == 를 두 번 적어요.", 960, 7))
W("e-or", o, "or 뒤에 비교 없이 값만 적으면 조건이 늘 True가 돼요. 말로는 주문이 coffee 또는 latte면이라고 하니 그대로 적기 쉬워요. 그런데 cake인데도 커피 종류예요가 찍히고, 오류가 나지 않아서 찾기 어려워요. 파이썬은 order == coffee와 latte를 or로 이은 걸로 읽어요. 앞은 False지만 뒤의 latte는 빈 문자열이 아니라 True로 봐요. print로 찍어 보면 latte가 그대로 나와요. 비교를 둘 다 적거나, 14의 in으로 리스트 안에 있는지 물으면 돼요." + REAL)

o = [sec("e-type")] + head(EB5, "글자와 숫자는 크기를 비교할 수 없어요", K5)
T1, T2 = 220, 520
TERR = "TypeError: '>=' not supported between instances of 'str' and 'int'"
o += cell({"id": "c-x7", "lines": ['price = "4500"', "if price >= 4000:", '    print("4000원 넘어요")'], "n": 7, "out": [TERR], "err": True}, 96, T1, 1440, sel="c-x7")
o.append(under_tok(1, 96, T1, 0, 'price = ', '"4500"', OR))
o.append(tag(tx(96, ['price = "4500"']) + 30, ly(T1, 0), "따옴표가 있으면 글자(str)예요", OR, 1))
o.append(under_tok(2, 96, T1, 0, "TypeError: '>=' not supported between instances of ", "'str' and 'int'", RED, out_n=3))
o.append(tag(cx(96, "TypeError: '>=' not supported between instances of "), oy(T1, 3, 0) + 58, "비교한 두 값의 종류", RED, 2, 26, False))
o += cell({"id": "c-x8", "lines": ["if int(price) >= 4000:", '    print("4000원 넘어요")'], "n": 8, "out": ["4000원 넘어요"]}, 96, T2, 1440, attrs=at(3, "rise"))
o.append(under_tok(3, 96, T2, 0, "if ", "int(price)", GR))
o.append(tag(tx(96, ["if int(price) >= 4000:"]) + 30, ly(T2, 0), "12의 int()로 숫자로 바꿔요", GR, 3))
o.append(p(f"position:absolute;left:96px;top:780px;width:1728px;font-size:28px;color:{SUB}", "== 로 비교하면 오류 없이 False가 나와서 if가 조용히 건너뛰어요. 더 찾기 어려워요.", at(4)))
o.append(caption("비교 오류가 나면 type()으로 두 값의 종류부터 봐요.", 960, 5))
W("e-type", o, "따옴표로 감싼 4500은 글자라서 숫자와 크기를 비교하면 TypeError가 나요. 오류 끝의 str and int는 비교한 두 값의 종류예요. 12에서 배운 int()로 숫자로 바꾸면 돼요. 조심할 건 ==예요. 글자 4500과 숫자 4500을 ==로 비교하면 오류 없이 False가 나와서 if가 조용히 건너뛰어요. 이상하면 type()으로 두 값의 종류부터 봐요." + REAL)

# ---------- part 6 (long cells: 26px) ----------
CFS[0] = 26
o = [sec("x-sale")] + head(EB6, "장바구니 금액에 따라 할인해요", K6)
T = 190
LS = [MENU, 'cart = {"coffee": 2, "cake": 1}', "total = 0", "for name, qty in cart.items():", "    total += menu[name] * qty", "if total >= 20000:", "    rate = 10", "elif total >= 10000:", "    rate = 5", "else:", "    rate = 0", "sale = total * rate // 100",
      'print(f"합계 {total:>7,}원")', 'print(f"할인 {sale:>7,}원 ({rate}%)")', 'print(f"결제 {total - sale:>7,}원")']
o += cell({"id": "c-p1", "lines": LS, "n": 1, "out": ["합계  15,500원", "할인     775원 (5%)", "결제  14,725원"], "wide": True}, 96, T, 1100, sel="c-p1")
o.append(hl(96, T, 1100, 3, 2, "mark", 1, "15 · 합계"))
o.append(hl(96, T, 1100, 5, 6, "run", 2, "elif · 할인율"))
o.append(hl(96, T, 1100, 11, 1, "mark", 3, "12 · 몫 //"))
o += rows(1270, T, [554], [["coffee 2잔  4,500 × 2 = 9,000"], ["cake 1개  6,500 × 1 = 6,500"], ["합계 15,500 · 10000 이상이라 5%"], ["할인  15500 × 5 // 100 = 775"]], ["계산 따라가기"], 1, 92, 26, 2, ["sans"])
o.append(caption("for로 합계를 내고, elif로 할인율 하나를 골라요.", 960, 4))
W("x-sale", o, "for로 장바구니 합계를 내고 elif로 할인율 하나를 고르면 할인 영수증이 나와요. 15의 메뉴판과 장바구니 딕셔너리를 써요. items()로 장바구니를 돌며 가격 곱하기 수량을 total에 쌓으면 15500원이에요. 2만 원 이상 10, 1만 원 이상 5, 나머지 0이라 15500은 5퍼센트예요. 할인 금액은 total 곱하기 rate를 100으로 나눈 몫이에요. 12의 // 라서 소수점 없이 775원이 돼요. 출력은 13의 칸 맞추기와 천 단위 콤마예요. cart를 바꿔 2만 원이 넘게 담아 보고 10% 할인이 나오는지 확인해요." + NEWK + REAL, ("p6", "실습"))

o = [sec("x-grade")] + head(EB6, "점수로 등급을 매겨요", K6)
T = 200
LGR = ['scores = [["kim", 92], ["lee", 78], ["park", 85], ["choi", 59]]', "for name, score in scores:", "    if score >= 90:", '        grade = "A"', "    elif score >= 80:", '        grade = "B"', "    elif score >= 70:", '        grade = "C"', "    else:", '        grade = "F"', '    print(f"{name:<5}{score:>3}  {grade}")']
o += cell({"id": "c-p2", "lines": LGR, "n": 2, "out": ["kim   92  A", "lee   78  C", "park  85  B", "choi  59  F"]}, 96, T, 1130, sel="c-p2")
o.append(hl(96, T, 1130, 2, 8, "run", 1, "elif 계단 · 8칸 안"))
o.append(hl(96, T, 1130, 10, 1, "mark", 2, "for 안, if 밖 · 4칸"))
stairs = [("90 이상", "A", GR), ("80 이상", "B", BL), ("70 이상", "C", OR), ("나머지", "F", RED)]
for i, (k, g, col) in enumerate(stairs):
    o.append(f'<div{at(i + 3, "rise")} style="position:absolute;left:{1270 + i * 44}px;top:{T + i * 124}px;width:{554 - i * 44}px;height:106px;border-top:4px solid {col};display:flex;flex-direction:row;align-items:center;gap:22px;padding:0 10px">'
             + p(f"font-family:{MONO};font-size:48px;font-weight:900;color:{col}", g) + p(f"font-size:28px;font-weight:700;color:{INK}", e(k)) + '</div>')
o.append(tag(1270, T + 4 * 124 + 50, "높은 점수 조건부터 내려가요", K6, 7, 28, False))
o.append(caption("for 안에 elif 계단을 넣으면 한 명씩 등급이 나와요.", 960, 8))
W("x-grade", o, "for 안에 elif 계단을 넣으면 한 명씩 등급을 매길 수 있어요. 14에서 이름과 점수를 같이 담은 2차원 리스트를 썼어요. 13의 for a, b in 모양으로 이름과 점수를 한 쌍씩 꺼내고, 점수가 높은 조건부터 elif로 계단을 내려가요. 92는 첫 계단에서 A, 78은 셋째 계단에서 C예요. 조건 순서를 바꾸면 2파트에서 본 것처럼 choi를 뺀 모두가 C가 돼요. if 계단은 for 안이라 4칸, 그 안의 grade는 8칸 들여써요. print는 for 안, if 밖이라 4칸이고 한 명마다 한 줄씩 찍혀요." + REAL)

o = [sec("x-receipt")] + head(EB6, "메뉴판에 없는 주문은 빼고 계산해요", K6)
T = 190
LR = ['orders = ["coffee", "tea", "cake", "coffee", "juice"]', "total = 0", "skipped = []", "for o in orders:", "    if o in menu:", '        print(f"{o:<8}{menu[o]:>6,}원")', "        total += menu[o]", "    else:", "        skipped.append(o)", 'print(f"합계 {total:,}원")', "if skipped:", '    print("준비 중:", skipped)']
o += cell({"id": "c-p3", "lines": LR, "n": 3, "out": ["coffee   4,500원", "cake     6,500원", "coffee   4,500원", "합계 15,500원", "준비 중: ['tea', 'juice']"], "wide": True}, 96, T, 1100, sel="c-p3")
TXR = 1250
o.append(hl(96, T, 1100, 4, 3, "run", 1))
o.append(tag(TXR, ly(T, 5), "있으면 찍고 합계에 더해요", GR, 1))
o.append(hl(96, T, 1100, 7, 2, "mark", 2))
o.append(tag(TXR, ly(T, 7.5), "없으면 따로 모아요 · KeyError 없음", BL, 2))
o.append(hl(96, T, 1100, 10, 1, "mark", 3))
o.append(tag(TXR, ly(T, 10), "하나라도 있을 때만 알려 줘요", BL, 3))
o.append(ring(4, 96 + 105, oy(T, 12, 4) - LH() / 2 + 2, 452, LH() - 4, BL))
o.append(tag(TXR, oy(T, 12, 4), "1파트 처음에 멈췄던 tea예요", BL, 4))
o.append(caption("if는 KeyError가 날 줄 앞에서 먼저 물어 막아 줘요.", 960, 5))
W("x-receipt", o, "for로 주문을 꺼내면서 메뉴판에 있는지 if로 먼저 물으면 KeyError 없이 계산할 수 있어요. 1파트 처음에 tea 주문에서 KeyError가 났어요. 이번에는 있으면 가격을 찍고 합계에 더하고, 없으면 else에서 skipped 리스트에 모아요. for가 끝나면 합계를 찍고, skipped가 비어 있지 않을 때만 준비 중인 메뉴를 알려 줘요. 3파트의 if 리스트: 모양이에요. 16에서는 집합의 교집합으로 미리 걸렀는데, 이번에는 하나씩 물어서 걸렀어요. 둘 다 맞는 방법이에요. 출력의 한글은 영어 두 칸 너비로 그렸어요." + REAL)
CFS[0] = 30

o = [sec("x-choose")] + head(EB6, "어떤 모양을 쓸지 이렇게 골라요", K6)
ch = [["if", "할 일이 한 가지, 조건이 맞을 때만", "있으면 알려 주기"],
      ["if, else", "둘 중 하나는 꼭", "살 수 있음, 돈이 모자람"],
      ["if, elif, else", "셋 이상 중 하나만", "할인율, 등급"],
      ["if 여러 개", "각각 따로 확인", "쿠폰 여러 장"],
      ["and, or, not", "조건 여러 개를 하나로", "키와 나이, 회원이거나 5만 원"],
      ["값1 if 조건 else 값2", "변수에 둘 중 하나 넣기", "msg 고르기"]]
o += rows(96, 210, [480, 600, 576], ch, ["모양", "언제", "예"], 1, 104, 30, 2, ["code", "sans", GRAY])
o.append(caption("처음에는 길게 적고, 같은 모양이 반복되면 줄여 써요.", 960, 4))
W("x-choose", o, "조건이 몇 개이고 몇 개를 실행할지에 따라 if 모양을 골라요. 조건이 맞을 때만 할 일이 있으면 if 하나, 둘 중 하나는 꼭 해야 하면 if와 else예요. 셋 이상 중 하나만 고르면 elif, 각각 따로 확인하면 if를 여러 번 써요. 조건이 여러 개면 and, or, not으로 하나로 묶어요. 변수에 둘 중 하나를 넣을 때는 한 줄 모양도 있어요. 처음에는 길게 적고 결과를 확인한 뒤 줄여요.")

# ---------- summary ----------
o = [sec("trouble")] + head("정리", "막히면 오류의 마지막 줄을 봐요", RED)
tr = [["1", "SyntaxError: ... Maybe you meant '=='", "if 뒤에 = 하나를 썼어요", "=="],
      ["2", "SyntaxError: expected ':'", "if, elif, else 줄 끝에 콜론이 없어요", "끝에 :"],
      ["3", "IndentationError: expected an indented block", "if 다음 줄을 들여쓰지 않았어요", "4칸 들여쓰기"],
      ["4", "IndentationError: unexpected indent", "들여쓰기 칸 수가 서로 달라요", "같은 칸에 맞추기"],
      ["5", "TypeError: '>=' not supported ... 'str' and 'int'", "글자와 숫자를 비교했어요", "int(price)"],
      ["6", "오류는 없는데 조건이 늘 True", "or 뒤에 비교 없이 값만 적었어요", 'o == "a" or o == "b"'],
      ["7", "오류는 없는데 결과가 이상함", "elif 순서, 들여쓰기 범위를 봐요", "좁은 조건부터"]]
o += rows(96, 200, [40, 740, 520, 340], tr, None, 1, 104, 24, 2, [RED, "code", "sans", "code"])
o.append(caption("오류가 안 나도 결과가 이상하면 if 안에 print를 넣어 어느 줄이 실행됐는지 봐요.", 960, 5))
W("trouble", o, "SyntaxError와 IndentationError는 실행 전에 나서 셀의 어느 줄도 실행되지 않으니, line 숫자로 어느 줄인지 먼저 찾아요. 5번은 글자와 숫자를 비교해서 나요. 6번과 7번은 오류가 없는데 결과가 이상한 경우예요. or 뒤에 비교를 빼먹었거나, elif 순서나 들여쓰기 범위가 틀렸어요. 어느 줄이 실행됐는지 궁금하면 if 안에 print를 하나 넣어 확인해요.", ("trouble", "정리"))

o = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>']
cheat = [("if 조건:", "True일 때만 실행", K1), ("else:", "False일 때 갈 길", K2), ("elif 조건:", "위에서부터 처음 True 하나", K2), ("    (4칸)", "들여쓴 줄까지 if 안", K2),
         ("a and b", "둘 다 True", K3), ("a or b", "하나라도 True", K3), ("x not in menu", "없으면", K3), ("9 <= h < 18", "범위 묻기", K3),
         ("if orders:", "비어 있지 않으면", K4), ("값1 if 조건 else 값2", "둘 중 하나를 넣기", K4)]
for i, (k, d, c_) in enumerate(cheat):
    col_, r_ = i // 5, i % 5
    x, y = 96 + col_ * 888, 210 + r_ * 116
    o.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:840px;height:116px;display:flex;flex-direction:row;align-items:center;gap:24px;border-bottom:2px solid {LINE}">'
             + p(f"width:400px;flex:none;font-family:{MONO};font-size:32px;font-weight:700;color:{c_};white-space:pre", e(k)) + p(f"font-size:30px;font-weight:700;color:{INK}", e(d)) + '</div>')
o.append(p(f"position:absolute;left:96px;top:840px;width:1728px;font-size:32px;font-weight:700;color:{INK}", "조건 뒤에 콜론, 다음 줄은 4칸. 묻기는 ==, 넣기는 ="))
o.append(p(f"position:absolute;left:96px;top:910px;width:1728px;font-size:30px;color:{SUB}", "다음 18에서는 while로 조건이 True인 동안 반복하고, break로 멈춰요."))
W("cheatsheet", o, "if 조건 콜론, 다음 줄 4칸 들여쓰기가 기본이에요. else는 False일 때, elif는 위에서부터 처음 True 하나예요. and, or, not으로 조건을 묶고, 범위는 이어서 적어요. 빈 값은 False로 봐요. 18에서는 같은 조건으로 반복을 멈추는 while과 break, continue를 배워요. 이 장을 노트북 마크다운 셀에 정리해 두면 복습할 때 같이 봐요.")

# ---------- toc: number, title, pages; one line under each ----------
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
parts = [(K1, "참과 거짓으로 길 고르기", "왜 필요한가, 갈림길 그림, 가장 짧은 if, 조건은 True와 False", "i-why", "i-bool"),
         (K2, "if, else, elif", "False면 건너뛰기, 들여쓰기 범위, else, elif, 순서, if 여러 개", "i-false", "i-ifif"),
         (K3, "조건 합치기", "and, if 안의 if, or, not in, 범위, 빈 값은 False", "i-and", "i-empty"),
         (K4, "for와 함께, 줄여 쓰기", "골라 담기, 세기, items(), 한 줄 if else, get과 16 코드 다시 읽기", "f-pick", "f-set"),
         (K5, "자주 나는 오류", "= 와 ==, 콜론과 들여쓰기, or 함정, 글자와 숫자 비교", "e-eq", "e-type"),
         (K6, "실습", "장바구니 할인, 성적 등급, 메뉴판 없는 주문 빼기, 모양 고르기", "x-sale", "x-choose")]
TOC_NOTE = "여섯 파트로 나눴고, 파트마다 새 커널에서 위에서부터 차례로 실행해요. 1파트는 왜 if가 필요한지와 갈림길 그림, 2파트는 if, else, elif 모양이에요. 3파트는 and, or, not으로 조건을 합치고, 4파트는 for와 같이 쓰고 15, 16의 줄인 기능을 원래 모양과 비교해요. 5파트는 자주 나는 오류, 6파트는 카페 실습이에요."
t = [f'<section id="toc" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>']
for i, (c_, h, s, a, b) in enumerate(parts):
    y = 196 + i * 120
    t.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:120px;display:flex;flex-direction:row;align-items:center;gap:36px;border-bottom:2px solid {LINE}">'
             + p(f"width:60px;flex:none;font-size:52px;font-weight:900;color:{c_}", str(i + 1))
             + '<div style="flex:1;display:flex;flex-direction:column;gap:4px">' + f'<h3 style="font-size:34px;font-weight:700;line-height:1.3;color:{INK}">{e(h)}</h3>'
             + p(f"font-size:24px;line-height:1.4;color:{SUB}", e(s)) + '</div>'
             + p(f"font-size:26px;font-weight:700;color:{GRAY};white-space:nowrap", f"{page[a]}–{page[b]}쪽") + '</div>')
t.append(p(f"position:absolute;left:96px;top:954px;font-size:26px;color:{SUB}", f'{page["ready"]}쪽은 노트북 준비, {page["trouble"]}–{page["cheatsheet"]}쪽은 막힐 때와 한 장 요약이에요.'))
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(t) + f"\n<aside>{e(TOC_NOTE)}</aside>\n</section>\n")

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-03T03:00:00Z"}, "lists": "css", "title": "제어문 1 (조건문 if)", "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
print(len(ORDER), "slides")
