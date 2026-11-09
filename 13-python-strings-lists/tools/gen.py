"""Generates every slide of the Python basics 2 deck (13) and slides/deck.json.

Story: three cafe orders become one printed receipt. Part 1 cuts strings and shapes output (%, format(), f-string),
part 2 puts the orders in lists and tuples and walks them with for, part 3 puts it all together in three examples.
Cells come from tools/cells.py; their outputs from tools/outputs.json, written by tools/run_nb.py (tools/demo.sh).

Layout rules (Stageshow, read in full from github.com/benjitaylor/skills): one hero per slide (the notebook cell or
one diagram), words on what the story is about, labels hung on the code with a 2px leader and a dot instead of
term cards, pictures lined up with the output line they explain, no empty bands, values move instead of swapping.
Usage: python3 tools/gen.py slides
"""

import html, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "tools"))
sys.path.insert(0, HERE)
from highlight import spot, spot_off, cursor, cursor_off, ring, box, underline  # noqa: E402
from cells import PARTS  # noqa: E402

OUTS = json.load(open(os.path.join(HERE, "outputs.json")))
SRC = {cid: src for cells in PARTS.values() for cid, src in cells}

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
INK, SUB, LINE, CARD, BG = "#1D2330", "#4A5262", "#E1DED6", "#FFFFFF", "#F6F5F1"
BL, GR, OR, RED, GRAY = "#2459C9", "#1F8A4C", "#B26A00", "#A33131", "#6A7180"
LEAD = "#9AA1AE"        # leader lines: quiet ink
SEL = "#2F7DE1"         # selected cell bar, like VS Code's focus color
JP = "#B8560F"          # Jupyter, same as chapters 09 and 10
T1, T1BG = GR, "#E6F4EC"           # part 1 strings
T2, T2BG = "#A23B72", "#F6E7EF"    # part 2 lists, tuples, for
T3, T3BG = BL, "#E7EEFB"           # part 3 examples
TINT = {"run": "rgba(31,138,76,0.16)", "skip": "rgba(106,113,128,0.20)", "err": "rgba(163,49,49,0.14)",
        "mark": "rgba(36,89,201,0.14)", "note": "rgba(178,106,0,0.16)", "list": "rgba(162,59,114,0.14)"}
TINTC = {"run": GR, "skip": GRAY, "err": RED, "mark": BL, "note": OR, "list": T2}
FS, LH = 30, 44         # code and output: 30px JetBrains Mono, 44px lines


def e(s):
    return html.escape(s, quote=False)


def p(style, text, attrs=""):
    return f'<p{attrs} style="{style}">{text}</p>'


def bi(kind, order):
    return f' data-build-in="{kind} order {order}"' if order else ""


def tw(s, fs=FS):
    """Width of a line in the code font: Latin is 0.6em, Hangul a full em."""
    return sum(fs if ord(ch) > 0x2E80 else fs * 0.6 for ch in s)


def m(code, color=INK, bg=None):
    """Inline code inside a sentence."""
    b = f"background:{bg};border-radius:8px;padding:0 8px;" if bg else ""
    return f'<span style="font-family:{MONO};font-weight:700;color:{color};{b}white-space:pre">{e(code)}</span>'


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
            f'<h2 id="title" style="position:absolute;left:96px;top:90px;width:1728px;font-size:56px;font-weight:700;line-height:1.2;color:{INK}">{title}</h2>']


def caption(text, top=968, order=0):
    return p(f"position:absolute;left:96px;top:{top}px;width:1728px;font-size:30px;font-weight:500;line-height:1.4;color:{SUB}", text, ' id="caption"' + bi("fade", order))


# ---------- notebook cell ----------
class G:
    """Geometry of a drawn cell, so highlights and leaders land on its lines."""

    def __init__(self, x, y, w, n, k, fs=FS):
        self.fs, self.lh, self.cw = fs, round(fs * 1.47), fs * 0.6
        self.x, self.y, self.w, self.n, self.k = x, y, w, n, k
        self.right = x + w
        self.tx = x + 107                       # left edge of the code text
        self.box_bottom = y + 24 + self.lh * n
        self.bottom = self.box_bottom + (12 + self.lh * k if k else 0)

    def line(self, i):
        return self.y + 12 + i * self.lh

    def mid(self, i):
        return self.line(i) + self.lh / 2

    def out(self, k):
        return self.box_bottom + 12 + k * self.lh

    def omid(self, k):
        return self.out(k) + self.lh / 2


def WIDE(t):
    """Draws each Hangul syllable two code columns wide (1.2em), like a terminal, so receipts line up."""
    return re.sub(r"([가-힣])", r'<span style="display:inline-block;width:1.2em;text-align:center">\1</span>', t)


def nb(cid, x, y, w=None, out=True, out_order=None, wide=False, sel=True, attrs="", minw=0, fs=FS):
    """A notebook cell: code box with [n] and its real output underneath. Returns (html list, G).
    out_order: one build order for the whole output, or a list with one order per output line."""
    src = SRC[cid].split("\n")
    rec = OUTS[cid]
    outl = rec["out"] if out else []
    widest = max([tw(l, fs) for l in src] + [tw(l, fs) * (1.2 if wide else 1) for l in outl] + [0])
    if w is None:
        w = int(max(minw, 107 + widest + 48))
    g = G(x, y, w, len(src), len(outl), fs)
    LH = g.lh
    o = [f'<div{attrs} id="{cid}" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{g.box_bottom - y}px">',
         f'<div style="position:absolute;left:0;top:0;width:7px;height:100%;border-radius:4px;background:{SEL if sel else "transparent"}"></div>',
         p(f"position:absolute;left:17px;top:12px;width:58px;font-family:{MONO};font-size:20px;line-height:{LH}px;color:{GRAY};text-align:right", f"[{rec['n']}]"),
         f'<div style="position:absolute;left:85px;top:0;right:0;bottom:0;background:#FFFFFF;border:2px solid {LINE};border-radius:10px"></div>']
    for i, l in enumerate(src):
        o.append(p(f"position:absolute;left:107px;top:{12 + i * LH}px;font-family:{MONO};font-size:{fs}px;line-height:{LH}px;white-space:pre;color:{INK}",
                   e(l) if l else "&#160;", f' id="{cid}-L{i}"'))
    o.append('</div>')
    col = RED if rec["err"] else INK
    for k, l in enumerate(outl):
        od = out_order[k] if isinstance(out_order, list) else out_order
        o.append(p(f"position:absolute;left:{g.tx}px;top:{g.out(k)}px;font-family:{MONO};font-size:{fs}px;line-height:{LH}px;white-space:pre;color:{col}",
                   (WIDE(e(l)) if wide else e(l)) or "&#160;", f' id="{cid}-O{k}"' + bi("fade", od)))
    return o, g


def hl(g, i, n=1, kind="run", order=1):
    """Tints code lines i..i+n-1."""
    return f'<div{bi("fade", order)} style="position:absolute;left:{g.x + 93}px;top:{g.line(i)}px;width:{g.w - 101}px;height:{n * g.lh}px;background:{TINT[kind]};border-radius:6px"></div>'


def hlo(g, k, kind="run", order=1, w=None, n=1):
    """Tints output lines k..k+n-1, same colour as the code line it came from."""
    return f'<div{bi("fade", order)} style="position:absolute;left:{g.tx - 12}px;top:{g.out(k)}px;width:{w or g.w - 95}px;height:{n * g.lh}px;background:{TINT[kind]};border-radius:6px"></div>'


def lead(order, x1, y1, x2, text, color=INK, y2=None, size=28, dot=LEAD, w=None):
    """A label hung on what it explains: 2px leader from a dot at (x1, y1) to the label at x2 (one bend if y2 differs)."""
    y2 = y1 if y2 is None else y2
    if y2 == y1:
        d = f"M{x1},{y1} L{x2 - 14},{y2}"
    else:
        xm = x2 - 40
        d = f"M{x1},{y1} L{xm},{y1} L{xm},{y2} L{x2 - 14},{y2}"
    lx, ly = min(x1, x2) - 10, min(y1, y2) - 10
    svg = (f'<svg style="position:absolute;left:0;top:0;width:1920px;height:1080px;overflow:visible;pointer-events:none" viewBox="0 0 1920 1080">'
           f'<path d="{d}" fill="none" stroke="{LEAD}" stroke-width="2"/><circle cx="{x1}" cy="{y1}" r="6" fill="{dot}"/></svg>')
    wd = f"width:{w}px;" if w else "white-space:nowrap;"
    lab = p(f"position:absolute;left:{x2}px;top:{y2 - size * 0.75:.0f}px;{wd}font-size:{size}px;font-weight:500;line-height:1.5;color:{color}", text)
    return f'<div{bi("fade", order)}>{svg}{lab}</div>'


def boxes(items, x, y, size=110, color=T1, idx=None, idx_bot=None, gap=10, fs=None, w=None, ids=None, fill=None, attrs="", ink=INK):
    """Values in boxes in a row, index numbers above (idx) and below (idx_bot). Returns (html, list of rects)."""
    bw = w or size
    fs = fs or int(size * 0.42)
    o, rects = [f'<div{attrs}>'], []
    for i, v in enumerate(items):
        bx = x + i * (bw + gap)
        rects.append((bx, y, bw, size))
        on = fill and i in fill
        idt = f' id="{ids}{i}"' if ids else ""
        if idx is not None:
            o.append(p(f"position:absolute;left:{bx}px;top:{y - 42}px;width:{bw}px;font-family:{MONO};font-size:24px;font-weight:700;line-height:32px;text-align:center;color:{color}", str(idx[i])))
        o.append(p(f"position:absolute;left:{bx}px;top:{y}px;width:{bw}px;height:{size}px;border-radius:14px;border:3px solid {color if on else '#CFCBC1'};background:{T2BG if on and color == T2 else (T1BG if on else CARD)};"
                   f"font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:{size - 6}px;text-align:center;white-space:pre;color:{ink}", e(str(v)) if str(v) != " " else "&#160;", idt))
        if idx_bot is not None:
            o.append(p(f"position:absolute;left:{bx}px;top:{y + size + 8}px;width:{bw}px;font-family:{MONO};font-size:22px;line-height:30px;text-align:center;color:{GRAY}", str(idx_bot[i])))
    o.append('</div>')
    return "".join(o), rects


def mark(order, r, color, pad=0, kind="fade", r_=14, width=5, fill=None):
    x, y, w, h = r
    f = f"background:{fill};" if fill else ""
    return f'<div{bi(kind, order)} style="position:absolute;left:{x - pad}px;top:{y - pad}px;width:{w + 2 * pad}px;height:{h + 2 * pad}px;border:{width}px solid {color};border-radius:{r_}px;{f}"></div>'


def chip(text, color, bg, size=28, extra=""):
    return p(f"display:inline-block;font-family:{MONO};font-size:{size}px;font-weight:700;color:{color};background:{bg};border-radius:10px;padding:2px 14px;white-space:pre;{extra}", e(text))


def var_box(vid, name, value, x, y, color=T2, w=300, h=150, attrs="", vfs=52):
    """A variable as a box with its name tab on top."""
    return (f'<div id="{vid}"{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{CARD};border:3px solid {color};border-radius:18px;overflow:hidden">'
            + p(f"height:52px;background:{color};color:#FFFFFF;font-family:{MONO};font-size:28px;font-weight:700;line-height:52px;padding:0 20px", e(name))
            + p(f"height:{h - 58}px;font-family:{MONO};font-size:{vfs}px;font-weight:700;line-height:{h - 58}px;text-align:center;color:{INK};white-space:pre", e(value)) + '</div>')


def arrow(order, pts, color="#9AA1AE", width=5, kind="draw", dash=False, head=True):
    """A drawn arrow through points; draws itself on (pen) when kind='draw'."""
    d = "M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in pts)
    (x1, y1), (x2, y2) = pts[-2], pts[-1]
    import math
    a = math.atan2(y2 - y1, x2 - x1)
    hx = lambda s, t: f"{x2 - 22 * math.cos(a) + s * 12 * math.sin(a):.0f},{y2 - 22 * math.sin(a) - s * 12 * math.cos(a):.0f}"
    hd = f'<path d="M{hx(1, 0)} L{x2:.0f},{y2:.0f} L{hx(-1, 0)}"/>' if head else ""
    da = ' stroke-dasharray="14 10"' if dash else ""
    return (f'<svg{bi(kind, order)} viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible">'
            f'<g fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"><path d="{d}"{da}/>{hd}</g></svg>')


def kbd(text, size=26):
    caps = [f'<span style="display:inline-block;font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.2;white-space:nowrap;color:{INK};background:#FFFFFF;border:2px solid #C9CED8;border-bottom-width:5px;border-radius:10px;padding:4px 12px">{e(k)}</span>' for k in text.split("+")]
    return f'<span style="display:inline-flex;gap:6px;align-items:center;vertical-align:middle">' + f'<span style="color:{GRAY};font-size:{size}px">+</span>'.join(caps) + '</span>'


def paper(x, y, w, lines, fs=26, attrs="", lh=None, pid="paper", pad=36):
    """A printed receipt: white paper with a soft shadow, monospace, Hangul two columns wide."""
    lh = lh or int(fs * 1.45)
    body = "".join(p(f"font-family:{MONO};font-size:{fs}px;line-height:{lh}px;white-space:pre;color:{INK}", WIDE(e(l)) or "&#160;") for l in lines)
    return (f'<div id="{pid}"{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;background:#FFFFFF;border-radius:6px;'
            f'box-shadow:0 1px 0 #E1DED6,0 18px 40px rgba(29,35,48,0.14);padding:{pad}px {pad}px {pad}px">{body}</div>')


RECEIPT = OUTS["ex-receipt"]["out"]


def note(order, x, y, color, text, w=900, size=28):
    """A short sentence with a coloured bar in front, matching the tint it explains."""
    return (f'<div{bi("fade", order)} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;display:flex;flex-direction:row;gap:16px;align-items:flex-start">'
            f'<div style="width:8px;height:{int(size * 1.5)}px;flex:none;border-radius:4px;background:{color}"></div>'
            + p(f"font-size:{size}px;line-height:1.5;color:{INK}", text) + '</div>')


def err_side(order, x, y, why, fix, w):
    return (f'<div{bi("fade", order)} style="position:absolute;left:{x}px;top:{y}px;width:{w}px">'
            + p(f"font-size:28px;font-weight:700;line-height:1.45;color:{RED}", why) + p(f"font-size:26px;line-height:1.6;color:{INK};margin-top:6px", fix) + '</div>')


def mono_line(x, y, segs, fs, attrs_each="", ids=None):
    """Big code written as coloured segments. Returns (html list, list of (x, width) per segment, end x)."""
    o, pos = [], []
    for i, (s_, col) in enumerate(segs):
        wpx = tw(s_, fs)
        idt = f' id="{ids}{i}"' if ids else ""
        o.append(p(f"position:absolute;left:{x:.0f}px;top:{y}px;font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:{round(fs * 1.35)}px;white-space:pre;color:{col}", e(s_), idt + attrs_each))
        pos.append((x, wpx))
        x += wpx
    return o, pos, x


# =====================================================================================
# cover
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px;display:flex;flex-direction:column;justify-content:center;gap:36px">',
       '<p style="font-size:28px;font-weight:700;color:#F2B27A">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
       '<h1 style="font-size:96px;font-weight:900;line-height:1.12;color:#F6F5F1">파이썬 기초 2<br>문자열, 리스트, for</h1>',
       '<p style="font-size:38px;line-height:1.45;color:#BFC6D4">주문 세 건을<br>영수증 한 장으로 찍어요</p>']
cov.append(paper(1150, 150, 660, RECEIPT, fs=27, pad=44, pid="cv-paper"))
W("cover", cov, "이번 챕터가 끝나면 오른쪽 영수증을 셀 하나로 찍을 수 있어요. 12에서 변수, 타입, 계산, 비교를 배웠어요. 1파트는 문자열을 자르고 f-string으로 출력 모양을 맞춰요. 2파트는 주문을 리스트와 튜플에 담고 for로 하나씩 꺼내요. 3파트에서 둘을 합쳐 영수증을 완성해요. 영수증은 3파트 셀을 실제로 실행한 결과예요.", ("intro", "들어가기"))

ORDER.append("toc")   # written last, after page numbers are known

# ---------- why ----------
o = [sec("why")] + head("들어가기", "12에서 배운 것만으로 찍으면 칸이 들쭉날쭉해요", JP)
c, g = nb("why", 96, 230, out_order=1, fs=34)
o += c
o.append(box(2, g.tx - 16, g.out(0) - 4, 440, g.lh * 4 + 8, RED, width=5, r=14))
o.append(p(f"position:absolute;left:{g.tx + 470}px;top:{g.out(1)}px;width:560px;font-size:30px;line-height:1.5;color:{RED};font-weight:700", "글자 길이가 달라서<br>숫자 칸이 안 맞아요", bi("fade", 2)))
o.append(p(f"position:absolute;left:1200px;top:{g.box_bottom + 30}px;font-size:28px;font-weight:700;color:{JP}", "이번 챕터 끝에 찍을 모양", bi("fade", 3)))
o.append(paper(1200, g.box_bottom + 84, 624, RECEIPT[3:11], fs=26, lh=40, attrs=bi("rise", 3), pid="why-paper", pad=32))
o.append(caption("주문이 열 건이면 print도 열 줄을 써야 해요.", 940, 4))
W("why", o, "12에서 배운 print와 계산만 쓰면 주문마다 줄을 새로 써야 하고, 숫자 칸도 맞지 않아요. 주문 세 건을 print 네 줄로 찍었어요. 메뉴 이름 길이가 달라서 가격과 수량이 들쭉날쭉해요. 주문이 열 건이면 print도 열 줄이에요. 이번 챕터에서 값 여러 개를 한 번에 담는 리스트와 튜플, 하나씩 꺼내 되풀이하는 for, 칸을 맞추는 f-string을 배워요. 오른쪽은 3파트에서 찍을 영수증이에요. 출력은 hello-uv 커널에서 실제로 실행한 결과예요.")

# ---------- big picture ----------
o = [sec("bigpic")] + head("들어가기", "주문 데이터가 영수증 한 줄이 되기까지", JP)
X1, Y1 = 96, 340
o.append(p(f"position:absolute;left:{X1}px;top:{Y1 - 64}px;font-family:{MONO};font-size:32px;font-weight:700;color:{T2}", "orders", bi("fade", 1)))
cols = [(0, 180), (190, 130), (330, 74)]
data_ = [("coffee", "4500", "2"), ("latte", "5000", "1"), ("cake", "6500", "3")]
for r, row in enumerate(data_):
    cells_ = "".join(p(f"position:absolute;left:{X1 + cx}px;top:{Y1 + r * 100}px;width:{cw}px;height:86px;border-radius:12px;border:3px solid {T2 if r == 0 else '#CFCBC1'};background:{T2BG if r == 0 else CARD};font-family:{MONO};font-size:30px;font-weight:700;line-height:80px;text-align:center;color:{INK}", v) for (cx, cw), v in zip(cols, row))
    o.append(f'<div{bi("rise", 1)}>{cells_}</div>')
o.append(p(f"position:absolute;left:{X1}px;top:{Y1 + 390}px;width:404px;font-size:27px;line-height:1.5;color:{SUB}", "리스트 하나에 주문 튜플 세 개", bi("fade", 1)))
o.append(arrow(2, [(520, Y1 + 43), (650, Y1 + 43)], T2))
o.append(p(f"position:absolute;left:530px;top:{Y1 - 8}px;font-family:{MONO};font-size:28px;font-weight:700;color:{T2}", "for", bi("fade", 2)))
for i, (nm, v) in enumerate([("menu", "'coffee'"), ("price", "4500"), ("qty", "2")]):
    o.append(var_box(f"bp-v{i}", nm, v, 676, Y1 - 30 + i * 136, T2, w=280, h=120, attrs=bi("rise", 2), vfs=36))
o.append(p(f"position:absolute;left:676px;top:{Y1 + 390}px;width:300px;font-size:27px;line-height:1.5;color:{SUB}", "한 건씩 꺼내<br>이름 세 개에 나눠 담기", bi("fade", 2)))
o.append(arrow(3, [(976, Y1 + 43), (1106, Y1 + 43)], T1))
o.append(p(f"position:absolute;left:982px;top:{Y1 - 8}px;font-family:{MONO};font-size:28px;font-weight:700;color:{T1}", "f-string", bi("fade", 3)))
o.append(paper(1130, Y1 - 56, 694, [RECEIPT[3], RECEIPT[4], RECEIPT[5]], fs=28, lh=48, attrs=bi("rise", 3), pid="bp-paper", pad=34))
o.append(mark(3, (1150, Y1 - 56 + 34 + 2 * 48 - 2, 654, 52), T1, width=4, r_=8))
o.append(p(f"position:absolute;left:1130px;top:{Y1 + 390}px;width:694px;font-size:27px;line-height:1.5;color:{SUB}", "칸을 맞춰 영수증 한 줄로", bi("fade", 3)))
strip = [("1파트", "문자열 자르기, f-string으로 칸 맞추기", T1), ("2파트", "리스트, 튜플에 담고 for로 하나씩", T2), ("3파트", "셋을 합쳐 영수증 완성", T3)]
for i, (a_, b_, c_) in enumerate(strip):
    o.append(f'<div{bi("rise", 4)} style="position:absolute;left:{96 + i * 584}px;top:860px;width:560px;height:100px;border-top:4px solid {c_};padding-top:18px;display:flex;flex-direction:row;gap:18px;align-items:baseline">'
             + p(f"font-size:28px;font-weight:900;color:{c_};white-space:nowrap", a_) + p(f"font-size:27px;line-height:1.4;color:{INK}", b_) + '</div>')
W("bigpic", o, "리스트에 담긴 주문을 for가 한 건씩 꺼내고, f-string이 칸을 맞춰 영수증 한 줄로 찍어요. 왼쪽 orders는 주문 세 건을 담은 리스트예요. 한 건은 메뉴, 가격, 수량을 묶은 튜플이에요. for는 주문을 한 건씩 꺼내서 menu, price, qty 세 이름에 나눠 넣어요. f-string은 그 값을 정해진 칸 수에 맞춰 한 줄로 만들어요. 1파트에서 f-string, 2파트에서 리스트와 for를 배우고 3파트에서 합쳐요.")

# =====================================================================================
# part 1: strings and output
EB1 = "1. 문자열과 출력"

o = [sec("str-make")] + head(EB1, "문자열은 따옴표로 감싼 글자예요", T1)
c, g = nb("str-make", 96, 230, out_order=[1, 2, 3], fs=38)
o += c
o.append(hl(g, 0, 3, "mark", 1))
o.append(hlo(g, 0, "mark", 1, w=110))
o.append(lead(1, g.right + 8, g.mid(1), g.right + 60, f"{m(chr(39) + 'kim' + chr(39), T1)} 와 {m(chr(34) + 'kim' + chr(34), T1)} 는 같은 값이라 {m('True')}"))
o.append(hl(g, 3, 1, "run", 2))
o.append(hlo(g, 1, "run", 2, w=60))
bx, rects = boxes(list("hello"), g.tx + 90, g.out(1) + 2, size=g.lh - 4, w=74, color=T1, gap=8, fs=30, attrs=bi("rise", 2))
o.append(bx)
for i, r_ in enumerate(rects):
    o.append(p(f"position:absolute;left:{r_[0] + r_[2] - 22}px;top:{r_[1] - 6}px;font-family:{MONO};font-size:18px;font-weight:700;color:{T1}", str(i + 1), bi("fade", 2)))
o.append(p(f"position:absolute;left:{rects[-1][0] + 110}px;top:{g.out(1) + 8}px;font-size:28px;line-height:1.5;color:{INK}", f"{m('len()')} 은 글자 수를 세요", bi("fade", 2)))
o.append(hl(g, 4, 1, "note", 3))
o.append(hlo(g, 2, "note", 3, w=200))
o.append(lead(3, g.right + 8, g.mid(4), g.right + 60, f"글자 안에 {m(chr(39), OR)} 가 있으면 바깥을 {m(chr(34), OR)} 로"))
o.append(caption("한 파일 안에서는 한 가지 따옴표로 맞춰 쓰면 읽기 쉬워요.", 968, 4))
W("str-make", o, "문자열은 글자를 따옴표로 감싼 값이고, 작은따옴표와 큰따옴표는 뜻이 같아요. 12의 2파트에서 본 str 타입이에요. 그래서 a == b 가 True예요. len()은 글자 수를 세요. hello는 다섯 글자라 5가 나와요. 공백도 한 글자로 세요. 글자 안에 작은따옴표가 들어가면 바깥을 큰따옴표로 감싸요. 출력은 hello-uv 커널에서 실제로 실행한 결과예요. 파트마다 새 커널에서 실행해서 셀 번호가 [1]부터예요.", ("strings", "문자열과 출력"))

# ---------- str-index ----------
o = [sec("str-index")] + head(EB1, "[번호]로 글자 하나를 꺼내요. 번호는 0부터예요", T1)
c, g = nb("str-index", 96, 250, out_order=[1, 2, 3], fs=38)
o += c
bx, rects = boxes(list("python"), 880, 300, size=150, color=T1, idx=list(range(6)), idx_bot=list(range(-6, 0)), gap=10, fs=64)
o.append(bx)
o.append(p(f"position:absolute;left:880px;top:500px;width:950px;font-size:26px;color:{GRAY}", "위는 앞에서부터, 아래는 뒤에서부터 센 번호"))
for k, (line, bi_) in enumerate([(1, 0), (2, 1), (3, 5)]):
    o.append(hl(g, line, 1, "run", k + 1))
    o.append(hlo(g, k, "run", k + 1, w=60))
    o.append(mark(k + 1, rects[bi_], T1, pad=0, fill="rgba(31,138,76,0.12)"))
c2, g2 = nb("str-index-err", 96, 740, attrs=bi("rise", 4), fs=38)
o += c2
ew = tw(OUTS["str-index-err"]["out"][0], 38)
o.append(underline(4, g2.tx, g2.tx + ew, g2.out(0) + g2.lh - 4, RED))
o.append(lead(4, g2.tx + ew + 20, g2.omid(0), g2.tx + ew + 70, f"마지막은 {m('5', T1)}번이라 {m('6')}번은 없어요"))
W("str-index", o, "문자열 뒤에 대괄호와 번호를 붙이면 그 자리의 글자 하나를 꺼내요. 이 번호를 인덱스라고 불러요. 첫 글자가 0번이라 python의 p는 0번, 마지막 n은 5번이에요. 음수 번호는 뒤에서부터 세요. -1이 맨 뒤 글자라서 길이를 몰라도 끝을 꺼낼 수 있어요. 없는 번호 6을 쓰면 IndexError가 나요. 출력은 실제로 실행한 결과에서 Traceback의 마지막 줄만 옮겼어요.")

# ---------- str-slice ----------
o = [sec("str-slice")] + head(EB1, "[시작:끝]은 글자 사이 번호로 잘라요", T1)
c, g = nb("str-slice", 96, 250, out_order=[1, 2, 3, 4], fs=42)
o += c
SS = 150
SX, SY = 1824 - 6 * SS, 300
bx, rects = boxes(list("python"), SX, SY, size=SS, color=T1, gap=0, fs=64)
o.append(bx)
for k in range(7):
    xk = SX + k * SS
    o.append(f'<div style="position:absolute;left:{xk - 2}px;top:{SY - 30}px;width:4px;height:{SS + 30}px;background:{T1}"></div>')
    o.append(p(f"position:absolute;left:{xk - 30}px;top:{SY - 76}px;width:60px;font-family:{MONO};font-size:30px;font-weight:700;text-align:center;color:{T1}", str(k)))
    o.append(f'<div style="position:absolute;left:{xk - 1}px;top:{SY + SS}px;width:2px;height:{g.out(3) + g.lh - SY - SS}px;background-image:linear-gradient({LEAD} 50%,transparent 50%);background-size:2px 12px;opacity:.7"></div>')
for k, (a_, b_) in enumerate([(0, 2), (2, 5), (0, 2), (2, 6)]):
    o.append(hl(g, k, 1, "run", k + 1))
    o.append(hlo(g, k, "run", k + 1, w=130))
    o.append(f'<div{bi("rise", k + 1)} style="position:absolute;left:{SX + a_ * SS + 8}px;top:{g.out(k) + 9}px;width:{(b_ - a_) * SS - 16}px;height:{g.lh - 18}px;border-radius:22px;background:{T1};display:flex;align-items:center;justify-content:center">'
             + f'<span style="font-family:{MONO};font-size:24px;font-weight:700;color:#FFFFFF">{e(SRC["str-slice"].split(chr(10))[k][10:-1])}</span></div>')
o.append(caption(f"{m('[0:2]', T1)} 는 0번 선부터 2번 선까지라서 두 글자예요. 앞을 비우면 처음부터, 뒤를 비우면 끝까지예요.", 940, 5))
W("str-slice", o, "대괄호 안에 시작과 끝 번호를 콜론으로 적으면 그 사이 글자를 잘라 와요. 번호를 글자 사이의 선이라고 생각하면 쉬워요. word[0:2]는 0번 선부터 2번 선까지라서 py예요. 끝 번호의 글자는 들어가지 않아요. word[2:5]는 tho예요. 시작을 비우면 처음부터, 끝을 비우면 끝까지예요. 이렇게 자르는 걸 슬라이싱이라고 불러요.")

# ---------- print sep end ----------
o = [sec("print-sep")] + head(EB1, "print의 sep, end와 \\n, \\t로 출력 모양을 바꿔요", T1)
c, g = nb("print-sep", 96, 226, fs=32)
o += c
pairs = [(1, 1, "run", f"{m('sep')} 값 사이에 넣을 글자. 기본은 빈칸"), (2, 1, "run", None),
         (3, 2, "mark", f"{m('end')} 줄 끝에 붙일 글자. 기본은 줄바꿈"), (5, 1, "note", f"{m(chr(92) + 'n')} 줄바꿈"), (6, 1, "note", f"{m(chr(92) + 't')} 탭, 칸 띄우기")]
outmap = {1: (1, 1), 2: (2, 1), 3: (3, 1), 5: (4, 2), 6: (6, 1)}
for order_, (line, n, kind, lab) in enumerate(pairs, 1):
    o.append(hl(g, line, n, kind, order_))
    k0, kn = outmap[line]
    o.append(hlo(g, k0, kind, order_, w=290, n=kn))
    if lab:
        o.append(lead(order_, g.right + 8, g.mid(line) + (g.lh / 2 if n == 2 else 0), g.right + 60, lab))
W("print-sep", o, "print의 sep은 값 사이에, end는 줄 끝에 붙는 글자예요. sep의 기본값은 빈칸이에요. 12에서 print(\"설명\", 값)이 빈칸으로 이어진 이유예요. sep=\"-\"면 kim-lee가 돼요. end의 기본값은 줄바꿈이에요. end=\" \"로 바꾸면 다음 print가 같은 줄에 이어져요. 따옴표 안의 \\n은 줄바꿈, \\t는 탭이에요. Windows 키보드에서는 역슬래시가 원화 기호로 보여요. 같은 키예요.")

# ---------- three ways ----------
o = [sec("fmt-ways")] + head(EB1, "값을 끼워 넣는 방법은 세 가지예요", T1)
c, g = nb("fmt-ways", 96, 250, out_order=[1, 2, 3], fs=40)
o += c
ways = [(3, "% 포맷팅", "가장 옛 방식", OR, "note"), (4, "format()", "파이썬 3.0부터", BL, "mark"), (5, "f-string", "3.6부터. 새 코드는 이걸로", T1, "run")]
for k, (line, nm, d, col, kind) in enumerate(ways):
    o.append(hl(g, line, 1, kind, k + 1))
    o.append(hlo(g, k, kind, k + 1, w=480))
    o.append(lead(k + 1, g.right + 8, g.mid(line), g.right + 60, f'<span style="font-weight:700;color:{col}">{nm}</span>  <span style="color:{SUB}">{d}</span>'))
o.append(lead(4, g.tx + 490, g.omid(1), g.tx + 550, "세 줄 모두 결과가 같아요", size=30))
W("fmt-ways", o, "문자열 안에 변수 값을 끼워 넣는 방법은 % 포맷팅, format(), f-string 세 가지이고 결과는 같아요. % 포맷팅은 가장 오래된 방식이라 옛 코드, 오래된 책, 블로그에서 자주 보여요. format()은 파이썬 3.0에서 나왔어요. f-string은 파이썬 3.6에서 나왔고 지금 표준이에요. 따옴표 앞에 f를 붙이고 중괄호 안에 변수 이름을 바로 적어서 가장 읽기 쉬워요. 새 코드는 f-string으로 쓰고, 나머지 둘은 읽을 수 있을 만큼만 알아 둬요.")

# ---------- %s %d vs f-string ----------
o = [sec("fmt-sd")] + head(EB1, "%는 자리 순서대로, f-string은 이름을 바로 적어요", T1)
TY1, TY2 = 296, 590
o.append(p(f"position:absolute;left:96px;top:{TY1 - 56}px;font-size:26px;font-weight:700;color:{OR}", "% 포맷팅"))
segs1 = [('"', INK), ("%s", OR), (" ", INK), ("%d", OR), ('개"', INK), (" % (", INK), ("cake", INK), (", ", INK), ("qty", INK), (")", INK)]
c, pos, xe = mono_line(96, TY1, segs1, 56)
o += c
cx = lambda i: pos[i][0] + pos[i][1] / 2
o.append(arrow(1, [(cx(6), TY1 + 82), (cx(6), TY1 + 132), (cx(1), TY1 + 132), (cx(1), TY1 + 86)], OR, width=4))
o.append(arrow(2, [(cx(8), TY1 + 82), (cx(8), TY1 + 162), (cx(3), TY1 + 162), (cx(3), TY1 + 86)], OR, width=4))
o.append(p(f"position:absolute;left:{xe + 70:.0f}px;top:{TY1 + 6}px;font-size:28px;line-height:1.55;color:{INK};width:{1824 - xe - 70:.0f}px", f"{m('%s', OR)} 글자 자리, {m('%d', OR)} 정수 자리<br>값은 뒤 괄호에 순서대로", bi("fade", 2)))
o.append(p(f"position:absolute;left:96px;top:{TY2 - 56}px;font-size:26px;font-weight:700;color:{T1}", "f-string", bi("fade", 3)))
segs2 = [("f", T1), ('"{', INK), ("cake", T1), ("} {", INK), ("qty", T1), ('}개"', INK)]
c, pos2, xe2 = mono_line(96, TY2, segs2, 56, bi("fade", 3))
o += c
o.append(p(f"position:absolute;left:{xe + 70:.0f}px;top:{TY2 + 6}px;font-size:28px;line-height:1.55;color:{INK};width:{1824 - xe - 70:.0f}px", f"자리에 이름을 바로 적어요<br>{m('{qty + 1}', T1)} 처럼 계산식도 돼요", bi("fade", 3)))
c, g = nb("fmt-sd", 96, 730, attrs=bi("rise", 4), fs=30)
o += c
o.append(hl(g, 2, 1, "run", 5))
o.append(hlo(g, 2, "run", 5, w=260))
W("fmt-sd", o, "% 방식은 %s, %d 자리에 뒤 괄호의 값이 순서대로 들어가고, f-string은 자리에 이름을 바로 적어요. %s는 글자 자리, %d는 정수 자리예요. 자리 수와 값 수가 같아야 하고 순서도 맞아야 해요. f-string은 따옴표 앞에 f를 붙이고 중괄호 안에 변수 이름을 적어요. 중괄호 안에 qty + 1 같은 계산식을 넣어도 돼요. 아래 셀은 앞 장 셀에 이어서 실행한 결과예요.")

# ---------- format() ----------
o = [sec("fmt-format")] + head(EB1, "format()은 {0} {1} {2} 번호로 값을 골라요", T1)
FY = 290
segs = [('"', INK), ("{0}", BL), (" ", INK), ("{1}", BL), ("원 ", INK), ("{2}", BL), ('개".format(', INK), ("cake", INK), (", ", INK), ("price", INK), (", ", INK), ("qty", INK), (")", INK)]
c, pos, xe = mono_line(96, FY, segs, 48)
o += c
for j, (si, di) in enumerate([(7, 1), (9, 3), (11, 5)]):
    sx_, dx_ = pos[si][0] + pos[si][1] / 2, pos[di][0] + pos[di][1] / 2
    o.append(p(f"position:absolute;left:{sx_ - 30:.0f}px;top:{FY - 50}px;width:60px;font-family:{MONO};font-size:28px;font-weight:700;text-align:center;color:{BL}", str(j)))
    o.append(arrow(j + 1, [(sx_, FY + 72), (sx_, FY + 108 + j * 30), (dx_, FY + 108 + j * 30), (dx_, FY + 74)], BL, width=4))
c, g = nb("fmt-format", 96, 530, out_order=[4, 5, 6], fs=32)
o += c
for k, lab in enumerate(["번호 순서대로", "번호를 바꾸면 순서가 바뀌어요", "같은 번호를 여러 번 써도 돼요"]):
    o.append(hl(g, k, 1, "mark", k + 4))
    o.append(hlo(g, k, "mark", k + 4, w=tw(OUTS["fmt-format"]["out"][k], 32) + 24))
    o.append(lead(k + 4, g.right + 8, g.mid(k), g.right + 60, lab))
W("fmt-format", o, "format()은 중괄호 안 번호로 괄호 안의 값을 골라요. 번호는 0부터 세요. {0}은 cake, {1}은 price, {2}는 qty예요. 번호를 바꾸면 값의 순서를 바꿀 수 있어요. {0}을 여러 번 쓰면 같은 값이 여러 번 들어가요. 번호를 비우고 {}만 쓰면 순서대로 들어가요. 옛 코드에서 자주 보이니 읽을 수 있을 만큼 알아 둬요.")

# ---------- width ----------
o = [sec("fmt-width")] + head(EB1, "콜론 뒤 숫자는 칸 수예요", T1)
c, g = nb("fmt-width", 96, 230, fs=36)
o += c
BXL = g.right + 80
rows = [("   42", None), ("   42", None), ("42   ", f"{m('<')} 왼쪽 맞춤"), ("00042", f"{m('0')} 빈칸을 0으로"), ("kim  ", "글자는 기본이 왼쪽"), ("  kim", f"{m('>')} 오른쪽 맞춤")]
CB = 50
for k, (txt, lab) in enumerate(rows):
    order_ = 1 if k < 2 else k
    y = g.out(k) + 4
    cells_ = "".join(p(f"position:absolute;left:{BXL + i * (CB + 6)}px;top:{y}px;width:{CB}px;height:{g.lh - 8}px;border-radius:8px;border:2px solid {T1 if ch != ' ' else '#CFCBC1'};background:{T1BG if ch != ' ' else CARD};font-family:{MONO};font-size:28px;font-weight:700;line-height:{g.lh - 12}px;text-align:center;color:{INK}", e(ch) if ch != " " else "")
                     for i, ch in enumerate(txt))
    o.append(f'<div{bi("rise", order_)}>{cells_}</div>')
    if lab:
        o.append(p(f"position:absolute;left:{BXL + 5 * (CB + 6) + 30}px;top:{y}px;font-size:28px;line-height:{g.lh - 8}px;white-space:nowrap;color:{INK}", lab, bi("fade", order_)))
    o.append(hl(g, k, 1, "run", order_))
    o.append(hlo(g, k, "run", order_, w=180))
o.append(p(f"position:absolute;left:{BXL + 5 * (CB + 6) + 30}px;top:{g.out(0) + 4}px;font-size:28px;line-height:1.5;white-space:nowrap;color:{INK}", f"{m('%5d', OR)} 와 {m('{42:5d}', T1)} 는 같아요<br>다섯 칸, 숫자는 오른쪽", bi("fade", 1)))
W("fmt-width", o, "콜론 뒤 숫자는 값이 차지할 칸 수예요. %5d와 {42:5d}는 다섯 칸을 잡고 숫자를 오른쪽에 붙여요. 빈 칸은 공백이에요. < 를 붙이면 왼쪽, > 를 붙이면 오른쪽으로 보내요. 0을 앞에 붙이면 빈칸이 0으로 채워져요. 숫자는 기본이 오른쪽, 글자는 기본이 왼쪽 맞춤이에요. 오른쪽 칸 그림은 출력의 글자를 한 칸씩 나눠 그린 거예요.")

# ---------- float ----------
o = [sec("fmt-float")] + head(EB1, ".2f는 소수점 아래 두 자리까지 보여 줘요", T1)
c, g = nb("fmt-float", 96, 230, out_order=[1, 1, 2, 3], fs=36)
o += c
o.append(hl(g, 1, 2, "run", 1))
o.append(hlo(g, 0, "run", 1, w=110, n=2))
o.append(lead(1, g.right + 8, g.line(2), g.right + 60, f"{m('%.2f', OR)} 와 {m('{pi:.2f}', T1)} 는 같아요"))
o.append(hl(g, 3, 1, "run", 2))
o.append(hlo(g, 2, "run", 2, w=130))
o.append(lead(2, g.right + 8, g.mid(3), g.right + 60, f"{m('.4f')} 네 자리"))
o.append(hl(g, 4, 1, "mark", 3))
o.append(hlo(g, 3, "mark", 3, w=230))
AX, AY = g.right + 60, g.out(1)
c, pos, xe = mono_line(AX, AY, [("{pi:", INK), ("8", BL), (".2", T1), ("f", OR), ("}", INK)], 88, bi("fade", 3))
o += c
for (ci, lab, col, dy) in [(1, "전체 여덟 칸", BL, 0), (2, "소수점 아래 두 자리", T1, 1), (3, "실수(소수) 모양", OR, 2)]:
    cxx = pos[ci][0] + pos[ci][1] / 2
    yy = AY + 150 + dy * 58
    o.append(f'<div{bi("fade", 3)}><svg style="position:absolute;left:0;top:0;width:1920px;height:1080px;overflow:visible" viewBox="0 0 1920 1080"><path d="M{cxx:.0f},{AY + 124} L{cxx:.0f},{yy} L{xe + 24:.0f},{yy}" fill="none" stroke="{LEAD}" stroke-width="2"/><circle cx="{cxx:.0f}" cy="{AY + 124}" r="6" fill="{col}"/></svg>'
             + p(f"position:absolute;left:{xe + 38:.0f}px;top:{yy - 21}px;font-size:28px;font-weight:700;line-height:42px;white-space:nowrap;color:{col}", lab) + '</div>')
W("fmt-float", o, "콜론 뒤 .2f는 소수점 아래 두 자리까지 반올림해서 보여 줘요. f는 실수 모양이라는 뜻이에요. %.2f와 {pi:.2f}는 같은 결과예요. .4f면 네 자리예요. 8.2f처럼 앞에 숫자를 붙이면 점과 소수까지 합쳐 여덟 칸을 잡아요. %0.2f처럼 0을 붙인 코드도 보이는데, 결과는 .2f와 같아요.")

# ---------- comma ----------
o = [sec("fmt-comma")] + head(EB1, "콜론 뒤 쉼표는 천 단위 콤마예요", T1)
c, g = nb("fmt-comma", 96, 230, out_order=[1, 2, 3, 4], fs=36)
o += c
labs = [(1, 0, f"{m(':,')} 세 자리마다 콤마"), (2, 1, f"{m(':,.2f')} 콤마와 소수 두 자리"), (4, 2, f"{m(':8,')} 여덟 칸과 콤마"), (5, 3, "계산식 결과에도 붙어요")]
for i, (line, k, lab) in enumerate(labs):
    o.append(hl(g, line, 1, "run", i + 1))
    o.append(hlo(g, k, "run", i + 1, w=tw(OUTS["fmt-comma"]["out"][k], 36) + 24))
    o.append(lead(i + 1, g.right + 8, g.mid(line), g.right + 60, lab))
o.append(caption(f"콤마는 보여 주는 모양만 바꿔요. {m('price')}에 든 값은 그대로 {m('1234567')}이에요.", 960, 5))
W("fmt-comma", o, "콜론 뒤에 쉼표를 적으면 세 자리마다 콤마를 찍어요. 가격처럼 큰 숫자를 읽기 쉽게 만들 때 써요. ,.2f처럼 소수 자리와 함께 쓸 수 있어요. 8,처럼 칸 수와 같이 쓰면 콤마까지 합쳐 여덟 칸이에요. 중괄호 안 계산식의 결과에도 붙어요. 콤마는 출력 모양만 바꾸고 변수의 값은 그대로예요. % 방식에는 콤마 옵션이 없어요. 오류 장에서 봐요.")

# ---------- align table ----------
o = [sec("fmt-align")] + head(EB1, "칸 수를 맞추면 줄이 표처럼 맞아요", T1)
c, g = nb("fmt-align", 96, 240, out_order=1, fs=38)
o += c
gx = g.tx
for i in range(11):
    o.append(f'<div{bi("fade", 2)} style="position:absolute;left:{gx + i * g.cw:.1f}px;top:{g.out(0) - 6}px;width:{g.cw:.1f}px;height:{g.lh * 4 + 12}px;border-left:1px solid {"#C9CED8" if i else "transparent"};background:{"rgba(31,138,76,0.08)" if i < 6 else "rgba(36,89,201,0.08)"}"></div>')
o.append(p(f"position:absolute;left:{gx}px;top:{g.out(4) + 16}px;width:{6 * g.cw:.0f}px;font-family:{MONO};font-size:24px;font-weight:700;text-align:center;color:{T1}", "&lt;6", bi("fade", 2)))
o.append(p(f"position:absolute;left:{gx + 6 * g.cw:.0f}px;top:{g.out(4) + 16}px;width:{5 * g.cw:.0f}px;font-family:{MONO};font-size:24px;font-weight:700;text-align:center;color:{BL}", "&gt;5", bi("fade", 2)))
o.append(lead(2, gx + 11 * g.cw + 20, g.omid(1), gx + 11 * g.cw + 70, "이름은 왼쪽 여섯 칸, 점수는 오른쪽 다섯 칸"))
o.append(hl(g, 3, 1, "note", 3))
o.append(hlo(g, 3, "note", 3, w=11 * g.cw + 24))
o.append(lead(3, g.right + 8, g.mid(3), g.right + 60, f"% 방식은 {m('%-6s', OR)} 가 왼쪽 여섯 칸"))
o.append(caption("성적표나 영수증처럼 줄을 맞춰 보여 줄 때 칸 수를 써요.", 940, 4))
W("fmt-align", o, "줄마다 같은 칸 수를 쓰면 글자 길이가 달라도 세로줄이 맞아요. 이름은 <6으로 왼쪽 여섯 칸, 점수는 >5로 오른쪽 다섯 칸을 잡았어요. kim, lee, park 길이가 달라도 점수 끝이 같은 세로줄에 와요. % 방식은 %-6s가 왼쪽 여섯 칸, %5d가 오른쪽 다섯 칸이에요. 3파트 영수증도 이 방법으로 맞춰요.")

# ---------- compare table ----------
o = [sec("fmt-compare")] + head(EB1, "세 방식 모두 콜론 뒤 모양은 같아요", T1)
cols_ = [(96, 360, "모양", INK), (456, 300, "% 방식", OR), (756, 340, "format()", BL), (1096, 340, "f-string", T1), (1436, 388, "결과", INK)]
rows_ = [("다섯 칸", "%5d", "{0:5d}", "{42:5d}", "[   42]"), ("소수 두 자리", "%.2f", "{0:.2f}", "{pi:.2f}", "3.14"), ("천 단위 콤마", "없음", "{0:,}", "{price:,}", "1,234,567")]
TY = 230
o.append(f'<div style="position:absolute;left:96px;top:{TY}px;width:1728px;height:66px;border-bottom:3px solid {INK}"></div>')
for x_, w_, h_, col in cols_:
    o.append(p(f"position:absolute;left:{x_ + 20}px;top:{TY + 12}px;font-size:28px;font-weight:700;color:{col}", h_))
for r, row in enumerate(rows_):
    y = TY + 66 + r * 100
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:100px;border-bottom:1px solid #D9D5CB"></div>')
    for j, ((x_, w_, _, col), v) in enumerate(zip(cols_, row)):
        if v == "없음":
            o.append(p(f"position:absolute;left:{x_ + 20}px;top:{y + 26}px;font-size:30px;color:{GRAY}", "없음"))
        else:
            o.append(p(f"position:absolute;left:{x_ + 20}px;top:{y + 26}px;font-size:32px;font-weight:700;color:{col};" + (f"font-family:{MONO};white-space:pre" if j else ""), e(v)))
o.append(spot(1, 1096, TY, 340, 66 + 3 * 100, pad=4, dim=0.45))
o.append(spot_off(2))
c, g = nb("fmt-compare", 96, 660, attrs=bi("rise", 2), fs=32)
o += c
o.append(lead(2, g.right + 8, g.mid(1), g.right + 60, "format()은 콜론 앞에 번호,<br>f-string은 이름을 적어요", w=700))
W("fmt-compare", o, "세 방식 모두 콜론 뒤에 적는 모양은 같아요. format()은 콜론 앞에 번호를, f-string은 변수 이름을 적어요. % 방식은 %5d처럼 % 뒤에 바로 모양을 적고, 콤마 옵션이 없어요. 새 코드는 f-string 칸만 기억하면 돼요. 아래 셀은 format()으로 실제로 실행한 결과예요.")

# ---------- format errors ----------
o = [sec("fmt-err")] + head(EB1, "자리와 값이 안 맞으면 오류가 나요", T1)
errs = [("fmt-err1", "%d 자리에 글자를 넣었어요", f"{m('%s')} 로 바꾸거나 f-string으로"),
        ("fmt-err2", "자리는 둘인데 값은 하나예요", f"{m('% (cake, qty)')} 처럼 값을 다 적어요"),
        ("fmt-err3", "글자에 정수 모양 d를 줬어요", f"{m('{cake}')} 만 적어요"),
        ("fmt-err4", "% 방식에는 콤마 옵션이 없어요", f"{m('f' + chr(34) + '{price:,}' + chr(34))} 로 써요")]
y = 222
for i, (cid, why, fix) in enumerate(errs):
    c, g = nb(cid, 96, y, w=1110, attrs=bi("rise", i + 1) if i else "", fs=26)
    o += c
    o.append(underline(i + 1, g.tx, g.tx + tw(OUTS[cid]["out"][0], 26), g.out(0) + g.lh - 2, RED))
    o.append(err_side(i + 1, 1250, y + 4, why, fix, 574))
    y = g.bottom + 44
W("fmt-err", o, "% 방식은 자리 수와 값 수, 자리 모양과 값의 타입이 맞아야 해요. %d 자리에 글자를 넣으면 TypeError가 나요. 자리는 둘인데 값이 하나여도 TypeError예요. f-string도 글자에 d 모양을 주면 ValueError가 나요. % 방식에는 콤마 옵션이 없어서 %,d는 ValueError예요. 오류가 나면 마지막 줄을 먼저 읽어요. 출력은 실제로 실행한 결과에서 Traceback의 마지막 줄만 옮겼어요.")

# =====================================================================================
# part 2: lists, tuples, for
EB2 = "2. 리스트, 튜플, for"

o = [sec("list-make")] + head(EB2, "리스트는 값 여러 개를 [ ] 하나에 담아요", T2)
o.append(p(f"position:absolute;left:96px;top:226px;font-size:26px;font-weight:700;color:{GRAY}", "12까지는 값마다 변수 하나"))
for i, (nm, v) in enumerate([("price1", "4500"), ("price2", "5000"), ("price3", "6500")]):
    o.append(var_box(f"lm-v{i}", nm, v, 96 + i * 250, 276, GRAY, w=230, h=128, vfs=40))
o.append(arrow(1, [(860, 340), (980, 340)], T2))
o.append(p(f"position:absolute;left:1010px;top:226px;font-family:{MONO};font-size:28px;font-weight:700;color:{T2}", "prices", bi("fade", 1)))
bx, rects = boxes(["4500", "5000", "6500"], 1010, 296, size=108, w=220, color=T2, fill=(0, 1, 2), attrs=bi("rise", 1), gap=12)
o.append(bx)
o.append(f'<div{bi("rise", 1)} style="position:absolute;left:996px;top:282px;width:{3 * 232 + 16}px;height:136px;border:3px dashed {T2};border-radius:22px"></div>')
c, g = nb("list-make", 96, 500, out_order=[2, 3, 4], fs=34)
o += c
for i, (line, lab) in enumerate([(1, "대괄호 안에 쉼표로 나눠 담아요"), (2, f"{m('len()')} 은 담긴 개수"), (3, f"타입 이름은 {m('list')}")]):
    o.append(hl(g, line, 1, "list", i + 2))
    o.append(hlo(g, i, "list", i + 2, w=tw(OUTS["list-make"]["out"][i], 34) + 24))
    o.append(lead(i + 2, g.right + 8, g.mid(line), g.right + 60, lab))
W("list-make", o, "리스트는 대괄호 안에 쉼표로 값을 나눠 담는 값이에요. 12까지는 가격이 세 개면 변수도 세 개였어요. 리스트는 변수 하나에 값 여러 개를 담아요. len()은 문자열에서는 글자 수, 리스트에서는 담긴 개수를 세요. type()으로 보면 list예요. 출력은 2파트 새 커널에서 실제로 실행한 결과예요.", ("lists", "리스트, 튜플, for"))

# ---------- list-index ----------
o = [sec("list-index")] + head(EB2, "꺼내고 자르는 법은 문자열과 같아요", T2)
c, g = nb("list-index", 96, 250, out_order=[1, 2, 3], fs=36)
o += c
bx, rects = boxes(["coffee", "latte", "cake"], 1824 - 3 * 252 + 12, 300, size=120, w=240, color=T2, idx=[0, 1, 2], idx_bot=[-3, -2, -1], gap=12, fs=38)
o.append(bx)
for k, (line, sel_) in enumerate([(1, (0,)), (2, (2,)), (3, (0, 1))]):
    o.append(hl(g, line, 1, "list", k + 1))
    o.append(hlo(g, k, "list", k + 1, w=tw(OUTS["list-index"]["out"][k], 36) + 24))
    rs = [rects[j] for j in sel_]
    if k < 2:
        o.append(mark(k + 1, rs[0], T2, pad=8, r_=20))
    else:
        o.append(f'<div{bi("rise", k + 1)} style="position:absolute;left:{rs[0][0] + 6}px;top:{rs[0][1] + rs[0][3] + 52}px;width:{rs[-1][0] + rs[-1][2] - rs[0][0] - 12}px;height:34px;border-radius:17px;background:{T2};font-family:{MONO};font-size:22px;font-weight:700;line-height:34px;text-align:center;color:#FFFFFF">[0:2]</div>')
o.append(f'<div{bi("rise", 4)} style="position:absolute;left:96px;top:800px;width:1728px;height:170px;border-top:2px solid #D9D5CB;padding-top:30px">'
         + p(f"font-size:26px;font-weight:700;color:{SUB};margin-bottom:18px", "1파트 문자열과 같은 문법")
         + '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:24px">'
         + "".join(f'<div style="display:flex;flex-direction:row;gap:16px;align-items:center">{chip(a_, T1, T1BG, 30)}<span style="font-size:30px;color:{GRAY}">↔</span>{chip(b_, T2, T2BG, 30)}</div>'
                   for a_, b_ in [("word[0]", "menus[0]"), ("word[-1]", "menus[-1]"), ("word[0:2]", "menus[0:2]")])
         + '</div></div>')
W("list-index", o, "리스트도 문자열처럼 번호로 꺼내고 콜론으로 잘라요. 번호는 0부터예요. menus[0]은 coffee, menus[-1]은 맨 뒤 cake예요. menus[0:2]는 0번 선부터 2번 선까지라 coffee와 latte예요. 리스트를 자르면 결과도 리스트라서 대괄호에 담겨 나와요. 1파트의 word[0], word[0:2]와 같은 문법이에요.")

# ---------- list-change ----------
o = [sec("list-change")] + head(EB2, "리스트는 값을 바꾸고 더할 수 있어요", T2)
c, g = nb("list-change", 96, 230, out_order=[3, 4, 4, 4], fs=34)
o += c
LX = 1060
o.append(p(f"position:absolute;left:{LX}px;top:226px;font-family:{MONO};font-size:28px;font-weight:700;color:{T2}", "prices"))
bx, rects = boxes(["4500", "5000", "6500"], LX, 276, size=100, w=170, color=T2, gap=12, fs=36)
o.append(bx)
o.append(hl(g, 0, 1, "list", 1))
o.append(p(f"position:absolute;left:{rects[0][0]}px;top:{rects[0][1]}px;width:170px;height:100px;border-radius:14px;border:3px solid {T2};background:{T2BG};font-family:{MONO};font-size:36px;font-weight:700;line-height:94px;text-align:center;color:{INK}", "4800", ' data-build-in="fly order 1" data-from="list-change-L0"'))
o.append(hl(g, 1, 1, "list", 2))
o.append(p(f"position:absolute;left:{LX + 3 * 182}px;top:276px;width:170px;height:100px;border-radius:14px;border:3px solid {T2};background:{T2BG};font-family:{MONO};font-size:36px;font-weight:700;line-height:94px;text-align:center;color:{INK}", "3000", ' data-build-in="fly order 2" data-from="list-change-L1"'))
o.append(lead(1, LX + 85, 388, LX + 150, f"{m('prices[0] = 4800')} 0번 자리를 바꿔요", y2=450))
o.append(lead(2, LX + 3 * 182 + 85, 388, LX + 150, f"{m('append(3000)')} 맨 뒤에 하나 더해요", y2=510))
o.append(hlo(g, 0, "list", 3, w=tw(OUTS["list-change"]["out"][0], 34) + 24))
o.append(hl(g, 3, 3, "run", 4))
o.append(hlo(g, 1, "run", 4, w=130, n=3))
o.append(lead(4, g.tx + 150, g.omid(2), g.tx + 200, f"{m('sum')} 합계, {m('max')} 가장 큰 값, {m('min')} 가장 작은 값"))
W("list-change", o, "리스트는 만든 뒤에도 값을 바꾸고 더할 수 있어요. prices[0] = 4800은 0번 자리의 값을 바꿔요. append(3000)은 맨 뒤에 하나를 더해서 담긴 개수가 3에서 4로 늘어요. sum, max, min은 리스트를 괄호에 넣는 함수예요. 합계, 가장 큰 값, 가장 작은 값을 돌려줘요. 문자열은 이렇게 바꿀 수 없어요. 비교 장에서 다시 봐요.")

# ---------- list methods ----------
o = [sec("list-methods")] + head(EB2, "넣고 빼는 메서드: append, insert, remove, pop", T2)
c, g = nb("list-methods", 96, 240, out_order=6, fs=38)
o += c
states = [["coffee", "latte"], ["coffee", "latte", "cake"], ["tea", "coffee", "latte", "cake"], ["tea", "coffee", "cake"], ["tea", "coffee"], ["coffee"]]
notes_ = [None, "맨 뒤에 더하기", "0번 자리에 끼우기", "값을 찾아 지우기", f"맨 뒤를 빼서 {m('last')}에", f"0번을 빼서 {m('first')}에"]
MX, BW = g.right + 50, 132
for k, st in enumerate(states):
    y = g.line(k) + 4
    cells_ = "".join(p(f"position:absolute;left:{MX + i * (BW + 8)}px;top:{y}px;width:{BW}px;height:{g.lh - 8}px;border-radius:8px;border:2px solid {T2 if (k and v not in states[k - 1]) else '#CFCBC1'};background:{T2BG if (k and v not in states[k - 1]) else CARD};font-family:{MONO};font-size:24px;font-weight:700;line-height:{g.lh - 12}px;text-align:center;color:{INK}", v) for i, v in enumerate(st))
    gone = [v for v in (states[k - 1] if k else []) if v not in st]
    o.append(f'<div{bi("rise", k)}>{cells_}</div>')
    if k:
        o.append(hl(g, k, 1, "list", k))
        o.append(p(f"position:absolute;left:{MX + 4 * (BW + 8) + 20}px;top:{y}px;font-size:26px;line-height:{g.lh - 8}px;white-space:nowrap;color:{INK}", notes_[k] + (f'  <span style="color:{RED};text-decoration:line-through">{e(gone[0])}</span>' if gone else ""), bi("fade", k)))
o.append(hlo(g, 0, "list", 6, w=tw(OUTS["list-methods"]["out"][0], 38) + 24))
o.append(lead(6, g.tx + tw(OUTS["list-methods"]["out"][0], 38) + 30, g.omid(0), MX, "pop은 뺀 값을 돌려줘서 변수에 담을 수 있어요"))
W("list-methods", o, "리스트 이름 뒤에 점을 찍고 쓰는 함수를 메서드라고 불러요. append는 맨 뒤에 더하고, insert(0, \"tea\")는 0번 자리에 끼워요. 끼운 자리 뒤의 값은 한 칸씩 밀려요. remove는 값을 찾아 지워요. pop()은 맨 뒤를, pop(0)은 0번을 빼서 돌려줘요. 돌려준 값은 last, first처럼 변수에 담을 수 있어요. 오른쪽 칸은 줄마다 cart에 담긴 값이에요.")

# ---------- list find ----------
o = [sec("list-find")] + head(EB2, "찾고 세고 정렬하는 메서드: count, index, sort", T2)
c, g = nb("list-find", 96, 230, out_order=[1, 2, 3, 4, 5], fs=34)
o += c
FX = 1100
o.append(p(f"position:absolute;left:{FX}px;top:216px;font-family:{MONO};font-size:28px;font-weight:700;color:{T2}", "scores"))
bx, rects = boxes(["70", "95", "80", "95"], FX, 300, size=100, w=160, color=T2, idx=[0, 1, 2, 3], gap=14, fs=40)
o.append(bx)
steps = [(1, 0, 60, f"{m('count(95)')} 95가 몇 개인지"), (2, 1, 60, f"{m('index(80)')} 80이 몇 번 자리인지"), (3, 2, 90, f"{m('95 in scores')} 들어 있으면 True"),
         (4, 3, 300, f"{m('sort()')} 작은 수부터. 리스트가 바뀌어요"), (6, 4, 300, f"{m('reverse=True')} 큰 수부터")]
for i, (line, k, w_, lab) in enumerate(steps):
    o.append(hl(g, line, 1, "list", i + 1))
    o.append(hlo(g, k, "list", i + 1, w=w_))
    o.append(lead(i + 1, g.right + 8, g.mid(line), FX, lab, y2=470 + i * 60))
o.append(mark(1, rects[1], T2))
o.append(mark(1, rects[3], T2))
o.append(mark(2, rects[2], BL, pad=8, r_=18))
W("list-find", o, "count는 몇 개인지, index는 몇 번 자리인지, in은 들어 있는지 물어요. scores에 95가 두 개라서 count(95)는 2예요. 80은 2번 자리에 있어서 index(80)은 2예요. in은 True나 False로 답해요. sort()는 작은 수부터 정렬하고 리스트 자체를 바꿔요. reverse=True를 넣으면 큰 수부터예요.")

# ---------- slicing with step ----------
o = [sec("list-slice")] + head(EB2, "[시작:끝:간격]으로 원하는 만큼 잘라요", T2)
c, g = nb("list-slice", 96, 230, out_order=[1, 2, 3, 4, 5], fs=34)
o += c
NX, NW = 1824 - 6 * 128 + 8, 120
nums = ["10", "20", "30", "40", "50", "60"]
o.append(boxes(nums, NX, g.line(0) + 3, size=g.lh - 6, w=NW, color=T2, gap=8, fs=26)[0])
for k, s in enumerate([(1, 2, 3), (0, 1, 2), (4, 5), (0, 2, 4), (0, 1, 2, 3, 4, 5)]):
    o.append(hl(g, k + 1, 1, "list", k + 1))
    o.append(hlo(g, k, "list", k + 1, w=tw(OUTS["list-slice"]["out"][k], 34) + 24))
    vals = nums[::-1] if k == 4 else nums
    sel = s
    o.append(boxes(vals if k == 4 else nums, NX, g.out(k) + 3, size=g.lh - 6, w=NW, color=T2, gap=8, fs=26, fill=sel, attrs=bi("rise", k + 1))[0])
o.append(caption(f"셋째 숫자는 간격이에요. {m('2')}면 한 칸씩 건너뛰고, {m('-1')}이면 거꾸로 가요.", 940, 6))
W("list-slice", o, "자르기는 [시작:끝:간격]이에요. nums[1:4]는 1번 선부터 4번 선까지 20, 30, 40이에요. 앞을 비우면 처음부터, 뒤를 비우면 끝까지예요. -2:는 뒤에서 두 개예요. 셋째 숫자는 간격이라 ::2는 한 칸씩 건너뛰어요. ::-1은 거꾸로 전부예요. 문자열에도 똑같이 써요.")

# ---------- nested ----------
o = [sec("list-nested")] + head(EB2, "리스트 안의 리스트는 번호를 두 번 써요", T2)
c, g = nb("list-nested", 96, 230, out_order=[1, 2, 3, 4, 5], fs=32)
o += c
GX, GY = 1340, 310
o.append(p(f"position:absolute;left:{GX - 180}px;top:{GY - 80}px;font-family:{MONO};font-size:28px;font-weight:700;color:{T2}", "table"))
for r in range(3):
    o.append(p(f"position:absolute;left:{GX - 180}px;top:{GY + r * 116 + 34}px;font-family:{MONO};font-size:24px;font-weight:700;color:{T2}", f"table[{r}]"))
    o.append(boxes([str(3 * r + c_ + 1) for c_ in range(3)], GX, GY + r * 116, size=100, w=148, color=T2, idx=[0, 1, 2] if r == 0 else None, gap=12, fs=42)[0])
o.append(hl(g, 1, 1, "list", 1))
o.append(hlo(g, 0, "list", 1, w=180))
o.append(mark(1, (GX - 10, GY + 116 - 10, 3 * 160 + 8, 120), T2, r_=20))
o.append(hl(g, 2, 1, "list", 2))
o.append(hlo(g, 1, "list", 2, w=50))
o.append(spot(2, GX + 2 * 160, GY + 116, 148, 100, pad=8, dim=0.5))
o.append(hl(g, 3, 1, "list", 3))
o.append(hlo(g, 2, "list", 3, w=50))
o.append(spot(3, GX + 2 * 160, GY + 232, 148, 100, pad=8, dim=0.5))
o.append(spot_off(4))
o.append(hl(g, 4, 1, "list", 4))
o.append(hlo(g, 3, "list", 4, w=50))
o.append(lead(4, g.tx + 60, g.omid(3), GX - 180, f"{m('menus[0][0]')} coffee의 0번 글자", y2=g.omid(3)))
o.append(hl(g, 5, 2, "list", 5))
o.append(hlo(g, 4, "list", 5, w=tw(OUTS["list-nested"]["out"][4], 32) + 24))
o.append(lead(5, g.tx + tw(OUTS["list-nested"]["out"][4], 32) + 30, g.omid(4), GX - 180, "글자, 숫자, True를 섞어 담아도 돼요", y2=g.omid(4)))
W("list-nested", o, "리스트 안에 리스트가 들어 있으면 번호를 두 번 써서 꺼내요. table[1]은 둘째 줄 [4, 5, 6]이에요. table[1][2]는 그 줄의 2번 칸이라 6이에요. table[-1][-1]은 마지막 줄의 마지막 칸 9예요. menus[0][0]처럼 리스트에서 꺼낸 글자에도 번호를 한 번 더 쓸 수 있어요. 리스트에는 글자, 숫자, True를 섞어 담아도 돼요. 2차원 리스트는 14에서 더 자세히 봐요.")

# ---------- list-more ----------
o = [sec("list-more")] + head(EB2, "새 리스트를 만드는 것과 원래 리스트를 바꾸는 것", T2)
c, g = nb("list-more", 96, 230, out_order=[1, 1, 3], fs=40)
o += c
TAGX = g.right + 60
tags = [(2, "new", f"{m('a + b')}  {m('a * 2')}  이어 붙이기"), (3, "new", f"{m('sorted(a)')}  정렬, a는 그대로"),
        (4, "chg", f"{m('a.extend(b)')}  a 뒤에 b를"), (5, "chg", f"{m('a.reverse()')}  순서만 거꾸로"), (6, "new", f"{m('a.copy()')}  복사본"), (7, "chg", f"{m('c.clear()')}  전부 비우기")]
for line, kind, lab in tags:
    col, bgc, word = (GR, T1BG, "새 리스트") if kind == "new" else (OR, "#F8EEDC", "원래 것이 바뀜")
    order_ = 1 if line in (2, 3) else (2 if line in (4, 5) else 3)
    o.append(hl(g, line, 1, "run" if kind == "new" else "note", order_))
    o.append(f'<div{bi("fade", order_)} style="position:absolute;left:{TAGX}px;top:{g.line(line) + 4}px;height:{g.lh - 8}px;display:flex;flex-direction:row;gap:16px;align-items:center;white-space:nowrap">'
             + p(f"width:170px;flex:none;font-size:22px;font-weight:700;line-height:36px;color:{col};background:{bgc};border-radius:8px;text-align:center", word)
             + p(f"font-size:26px;line-height:40px;color:{INK}", lab) + '</div>')
o.append(hlo(g, 0, "run", 1, w=tw(OUTS["list-more"]["out"][0], 40) + 24, n=2))
o.append(hlo(g, 2, "note", 3, w=tw(OUTS["list-more"]["out"][2], 40) + 24))
W("list-more", o, "괄호에 넣는 함수와 +, *는 새 리스트를 만들고, 점으로 부르는 메서드는 원래 리스트를 바꿔요. a + b는 두 리스트를 이은 새 리스트, a * 2는 두 번 반복한 새 리스트예요. sorted(a)는 정렬한 새 리스트를 돌려주고 a는 그대로예요. a.sort()는 a 자체를 바꿔요. extend는 a 뒤에 b를 이어 붙이고, reverse는 순서만 거꾸로 해요. copy는 복사본을 만들어서 c를 비워도 a는 그대로예요.")

# ---------- split join ----------
o = [sec("list-str")] + head(EB2, "split은 글자를 리스트로, join은 리스트를 글자로", T2)
SY_ = 300
o.append(p(f"position:absolute;left:96px;top:{SY_ + 6}px;font-family:{MONO};font-size:38px;font-weight:700;line-height:64px;color:{T1};white-space:pre", e('"coffee,latte,cake"'), ' id="ls-src"'))
o.append(arrow(1, [(560, SY_ + 38), (676, SY_ + 38)], T2))
o.append(p(f"position:absolute;left:548px;top:{SY_ - 46}px;font-family:{MONO};font-size:26px;font-weight:700;color:{T2}", e('split(",")'), bi("fade", 1)))
bx, rects = boxes(["coffee", "latte", "cake"], 700, SY_ - 4, size=84, w=170, color=T2, gap=10, fs=30, fill=(0, 1, 2), attrs=bi("rise", 1))
o.append(bx)
o.append(arrow(2, [(1250, SY_ + 38), (1366, SY_ + 38)], T1))
o.append(p(f"position:absolute;left:1236px;top:{SY_ - 46}px;font-family:{MONO};font-size:26px;font-weight:700;color:{T1}", e('" / ".join'), bi("fade", 2)))
o.append(p(f"position:absolute;left:1390px;top:{SY_ + 14}px;font-family:{MONO};font-size:26px;font-weight:700;line-height:48px;color:{T1};white-space:pre", e('"coffee / latte / cake"'), bi("rise", 2)))
c, g = nb("list-str", 96, 470, out_order=[1, 2, 3, 4], fs=32)
o += c
o.append(hl(g, 1, 1, "list", 1))
o.append(hlo(g, 0, "list", 1, w=tw(OUTS["list-str"]["out"][0], 32) + 24))
o.append(hl(g, 3, 1, "run", 2))
o.append(hlo(g, 1, "run", 2, w=tw(OUTS["list-str"]["out"][1], 32) + 24))
o.append(hl(g, 4, 1, "mark", 3))
o.append(hlo(g, 2, "mark", 3, w=tw(OUTS["list-str"]["out"][2], 32) + 24))
o.append(lead(3, g.right + 8, g.mid(4), g.right + 60, "괄호를 비우면 빈칸에서 잘라요"))
o.append(hl(g, 5, 1, "mark", 4))
o.append(hlo(g, 3, "mark", 4, w=tw(OUTS["list-str"]["out"][3], 32) + 24))
o.append(lead(4, g.right + 8, g.mid(5), g.right + 60, f"{m('list(' + chr(34) + 'abc' + chr(34) + ')')} 는 한 글자씩 나눠요"))
W("list-str", o, "split은 글자를 기준 글자에서 잘라 리스트로 만들고, join은 리스트를 사이에 글자를 넣어 하나로 이어요. text.split(\",\")은 쉼표에서 잘라 세 칸짜리 리스트를 만들어요. \" / \".join(words)는 사이에 슬래시를 넣어 문자열 하나로 이어요. split()처럼 괄호를 비우면 빈칸에서 잘라요. list(\"abc\")는 한 글자씩 나눈 리스트예요. 3파트 주문 메모 예제에서 다시 써요.")

# ---------- compare: str vs list ----------
o = [sec("list-compare")] + head(EB2, "문자열과 리스트: 꺼내는 법은 같고, 바꾸기만 달라요", T2)
cols_ = [(96, 520, ""), (616, 600, "문자열"), (1216, 608, "리스트")]
rows_ = [("번호로 꺼내기, 자르기", "word[0]  word[0:2]", "menus[0]  menus[0:2]", None),
         ("개수, 들어 있는지", "len(word)  'p' in word", "len(menus)  95 in scores", None),
         ("자리의 값 바꾸기", "안 돼요 (TypeError)", "names[0] = \"park\"", "diff"),
         ("메서드", "split", "append insert remove pop sort", None)]
TY = 222
o.append(f'<div style="position:absolute;left:96px;top:{TY}px;width:1728px;height:60px;border-bottom:3px solid {INK}"></div>')
for x_, w_, h_ in cols_:
    o.append(p(f"position:absolute;left:{x_ + 20}px;top:{TY + 10}px;font-size:28px;font-weight:700;color:{T1 if h_ == '문자열' else T2}", h_))
for r, (a_, b_, c_, d_) in enumerate(rows_):
    y = TY + 60 + r * 84
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:84px;border-bottom:1px solid #D9D5CB"></div>')
    o.append(p(f"position:absolute;left:116px;top:{y + 22}px;font-size:28px;font-weight:700;color:{INK}", a_))
    o.append(p(f"position:absolute;left:636px;top:{y + 22}px;font-size:27px;font-weight:700;white-space:pre;color:{RED if d_ else T1};" + ("" if d_ else f"font-family:{MONO}"), e(b_)))
    o.append(p(f"position:absolute;left:1236px;top:{y + 22}px;font-family:{MONO};font-size:27px;font-weight:700;white-space:pre;color:{T2}", e(c_)))
o.append(box(1, 100, TY + 60 + 2 * 84 + 4, 1720, 76, RED, width=4))
c, g = nb("list-compare", 96, 640, attrs=bi("rise", 2), fs=30)
o += c
o.append(underline(2, g.tx, g.tx + tw(OUTS["list-compare"]["out"][1]), g.out(1) + g.lh - 2, RED))
o.append(lead(2, g.right + 8, g.mid(1), g.right + 60, "리스트는 바뀌어요"))
o.append(lead(2, g.right + 8, g.mid(4), g.right + 60, "문자열은 안 바뀌어요"))
W("list-compare", o, "문자열과 리스트는 번호로 꺼내고 자르는 법이 같고, 자리의 값을 바꾸는 것만 달라요. len과 in도 둘 다 써요. 리스트는 names[0] = \"park\"처럼 자리의 값을 바꿀 수 있어요. 문자열은 word[0] = \"P\"처럼 바꾸려 하면 TypeError가 나요. 바꾼 글자가 필요하면 새 문자열을 만들어요. 리스트 메서드는 대부분 리스트 자체를 바꿔요. 출력은 실제로 실행한 결과예요.")

# ---------- tuple ----------
o = [sec("tuple")] + head(EB2, "튜플은 ( )에 묶고, 만든 뒤에는 못 바꿔요", T2)
c, g = nb("tuple", 96, 230, out_order=[1, 2, 3, 4], fs=34)
o += c
o.append(hl(g, 1, 3, "list", 1))
o.append(hlo(g, 0, "list", 1, w=150, n=3))
o.append(lead(1, g.right + 8, g.mid(2), g.right + 60, "꺼내고 자르는 건 리스트와 같아요"))
TX_ = 1000
TY_ = g.out(0) + 10
o.append(p(f"position:absolute;left:{TX_}px;top:{TY_ - 50}px;font-family:{MONO};font-size:28px;font-weight:700;color:{T2}", "order"))
bx, rects = boxes(["'coffee'", "4500", "2"], TX_, TY_ + 16, size=104, w=200, color=T2, gap=12, fs=34, fill=(0, 1, 2))
o.append(bx)
o.append(f'<div style="position:absolute;left:{TX_ - 16}px;top:{TY_}px;width:{3 * 212 + 20}px;height:136px;border:3px solid {T2};border-radius:60px"></div>')
o.append(f'<x-icon name="Lock" style="position:absolute;left:{TX_ + 3 * 212 + 30}px;top:{TY_ + 42}px;width:52px;height:52px;color:{T2}"></x-icon>')
c2, g2 = nb("tuple-err", 96, g.bottom + 50, attrs=bi("rise", 2), fs=34)
o += c2
ew = tw(OUTS["tuple-err"]["out"][0], 34)
o.append(underline(2, g2.tx, g2.tx + ew, g2.out(0) + g2.lh - 2, RED))
o.append(lead(2, g2.right + 8, g2.mid(0), g2.right + 60, "바꾸기는 안 돼요"))
o.append(caption("주문 한 건, 날짜처럼 묶어 두고 바꾸지 않을 값은 튜플에 담아요.", 960, 3))
W("tuple", o, "튜플은 소괄호로 값 여러 개를 묶고, 만든 뒤에는 바꿀 수 없어요. 꺼내기, 자르기, 계산은 리스트와 똑같아요. order[1] = 5000처럼 바꾸려 하면 TypeError가 나요. 주문 한 건의 메뉴, 가격, 수량처럼 한 묶음으로 두고 바꾸지 않을 값에 써요. 1파트의 % (cake, qty)에서 괄호로 묶은 것도 튜플이었어요.")

# ---------- orders ----------
o = [sec("orders")] + head(EB2, "주문 여러 건은 튜플을 리스트에 담아요", T2)
c, g = nb("orders", 96, 230, out_order=[1, 2, 3, 4], fs=30)
o += c
OX, OY = 1120, 560
for c_, h_ in enumerate(["[0] 메뉴", "[1] 가격", "[2] 수량"]):
    o.append(p(f"position:absolute;left:{OX + c_ * 236}px;top:{OY - 48}px;width:224px;font-family:{MONO};font-size:24px;font-weight:700;text-align:center;color:{T2}", h_))
for r, row in enumerate(data_):
    o.append(p(f"position:absolute;left:{OX - 190}px;top:{OY + r * 104 + 30}px;font-family:{MONO};font-size:26px;font-weight:700;color:{T2}", f"orders[{r}]"))
    o.append(boxes(list(row), OX, OY + r * 104, size=90, w=224, color=T2, gap=12, fs=34)[0])
o.append(hl(g, 1, 1, "list", 1))
o.append(hlo(g, 0, "list", 1, w=40))
for i, (line, k, r_) in enumerate([(2, 1, (OX, OY + 104, 3 * 236 - 12, 90)), (3, 2, (OX, OY + 104, 224, 90)), (4, 3, (OX + 236, OY + 208, 2 * 236 - 12, 90))]):
    o.append(hl(g, line, 1, "list", i + 2))
    o.append(hlo(g, k, "list", i + 2, w=tw(OUTS["orders"]["out"][k]) + 24))
    o.append(spot(i + 2, *r_, pad=10, dim=0.5))
o.append(spot_off(5))
o.append(p(f"position:absolute;left:{OX - 190}px;top:{OY + 330}px;width:900px;font-size:28px;line-height:1.5;color:{INK}", "앞 번호는 몇째 주문, 뒤 번호는 그 안의 몇째 값이에요.", bi("fade", 5)))
W("orders", o, "주문 여러 건은 튜플 한 건씩을 리스트에 담아요. orders에는 튜플이 세 개 있어서 len은 3이에요. orders[1]은 둘째 주문 튜플이에요. orders[1][0]은 둘째 주문의 0번 값 latte예요. orders[2][1] * orders[2][2]는 cake의 가격과 수량을 곱해 19500이에요. 앞 번호는 몇째 주문, 뒤 번호는 그 안의 몇째 값이에요.")

# ---------- unpack ----------
o = [sec("tuple-more")] + head(EB2, "튜플 값을 변수 여러 개에 한 번에 꺼내 담아요", T2)
c, g = nb("tuple-more", 96, 230, out_order=[1, 2, 3, 3], fs=32)
o += c
UX, UY = 1130, 250
o.append(p(f"position:absolute;left:{UX}px;top:{UY - 30}px;font-family:{MONO};font-size:26px;font-weight:700;color:{T2}", "orders[2]"))
bx, rects = boxes(["'cake'", "6500", "3"], UX, UY + 20, size=84, w=220, color=T2, gap=12, fs=32, ids="tm-s")
o.append(bx)
for i, (nm, v) in enumerate([("menu", "'cake'"), ("price", "6500"), ("qty", "3")]):
    o.append(var_box(f"tm-v{i}", nm, "", UX + i * 232, UY + 190, T2, w=220, h=130))
    o.append(p(f"position:absolute;left:{UX + i * 232 + 3}px;top:{UY + 190 + 55}px;width:214px;height:70px;background:#FFFFFF;font-family:{MONO};font-size:34px;font-weight:700;line-height:70px;text-align:center;color:{INK}", e(v), f' data-build-in="fly order 1" data-from="tm-s{i}"'))
o.append(hl(g, 0, 2, "list", 1))
o.append(hlo(g, 0, "list", 1, w=tw(OUTS["tuple-more"]["out"][0], 32) + 24))
o.append(p(f"position:absolute;left:{UX}px;top:{UY + 344}px;width:690px;font-size:27px;line-height:1.5;color:{INK}", "왼쪽 이름 수와 튜플 값 수가 같아야 해요.", bi("fade", 1)))
o.append(hl(g, 2, 3, "mark", 2))
o.append(hlo(g, 1, "mark", 2, w=130))
o.append(lead(2, g.tx + 150, g.omid(1), g.tx + 200, f"{m('a, b = b, a')} 두 값을 맞바꿔요"))
o.append(hl(g, 5, 2, "run", 3))
o.append(hlo(g, 2, "run", 3, w=tw(OUTS["tuple-more"]["out"][3], 32) + 24, n=2))
o.append(lead(3, g.tx + tw(OUTS["tuple-more"]["out"][3], 32) + 30, g.omid(2) + g.lh / 2, g.tx + tw(OUTS["tuple-more"]["out"][3], 32) + 80, f"튜플 메서드는 {m('count')}, {m('index')} 두 개<br>고치려면 {m('list()')}로 바꿔서", w=640))
W("tuple-more", o, "menu, price, qty = orders[2]처럼 쓰면 튜플 값이 순서대로 하나씩 들어가요. 왼쪽 이름 수와 튜플 값 수가 같아야 해요. 이렇게 꺼내 담으면 orders[2][1] 대신 price처럼 이름으로 쓸 수 있어요. a, b = b, a는 두 변수의 값을 맞바꿔요. 튜플은 바꾸는 메서드가 없고 count와 index만 있어요. 고쳐야 하면 list()로 리스트로 바꿔서 고쳐요. 다음 장의 for가 이 꺼내 담기를 되풀이해요.")

# ---------- for intro ----------
o = [sec("for-intro")] + head(EB2, "for는 리스트에서 하나씩 꺼내 같은 일을 되풀이해요", T2)
c, g = nb("for-intro", 96, 250, out_order=[1, 2, 3], fs=42)
o += c
o.append(lead(0, g.right + 8, g.mid(0), g.right + 60, f"줄 끝에 콜론 {m(':')}"))
o.append(lead(0, g.right + 8, g.mid(1), g.right + 60, "네 칸 들여 쓴 줄을 되풀이해요"))
FX_, FY_ = 900, 620
o.append(p(f"position:absolute;left:{FX_}px;top:{FY_ - 96}px;font-family:{MONO};font-size:28px;font-weight:700;color:{T2}", "menus"))
bx, rects = boxes(["coffee", "latte", "cake"], FX_, FY_, size=100, w=200, color=T2, gap=12, fs=34, ids="fi-s", idx=["1번째", "2번째", "3번째"])
o.append(bx)
o.append(arrow(0, [(FX_ + 3 * 212 + 10, FY_ + 50), (1560, FY_ + 50)], LEAD, width=4, kind="fade"))
o.append(var_box("fi-var", "menu", "", 1590, FY_ - 26, T2, w=234, h=152))
for k, v in enumerate(["coffee", "latte", "cake"]):
    o.append(p(f"position:absolute;left:1593px;top:{FY_ - 26 + 55}px;width:228px;height:90px;background:#FFFFFF;font-family:{MONO};font-size:36px;font-weight:700;line-height:90px;text-align:center;color:{INK}", f"'{v}'", f' data-build-in="fly order {k + 1}" data-from="fi-s{k}"'))
    o.append(spot(k + 1, *rects[k], pad=8, dim=0.3))
    o.append(hlo(g, k, "list", k + 1, w=180))
o.append(spot_off(4))
o.append(hl(g, 1, 1, "list", 1))
o.append(p(f"position:absolute;left:{FX_}px;top:{FY_ + 150}px;width:924px;font-size:28px;line-height:1.5;color:{INK}", "값이 세 개라서 세 번 되풀이하고 끝나요.", bi("fade", 4)))
W("for-intro", o, "for 이름 in 리스트: 는 리스트에서 값을 하나씩 꺼내 이름에 넣고, 아래 들여 쓴 줄을 되풀이해요. 처음에는 menu에 coffee가 들어가서 print(menu)가 coffee를 찍어요. 다음에는 latte, 그다음 cake예요. 값이 세 개라서 세 번 되풀이하고 끝나요. 줄 끝 콜론과 네 칸 들여쓰기가 for의 범위를 정해요. VS Code는 콜론 뒤 Enter를 치면 자동으로 네 칸을 들여 줘요.")

# ---------- for orders ----------
o = [sec("for-orders")] + head(EB2, "for로 주문 튜플을 꺼내 담으면서 되풀이해요", T2)
c, g = nb("for-orders", 96, 250, out_order=[1, 2, 3], fs=36)
o += c
OX, OY = 1130, 250
for r, row in enumerate(data_):
    o.append(p(f"position:absolute;left:{OX - 180}px;top:{OY + r * 96 + 26}px;font-family:{MONO};font-size:24px;font-weight:700;color:{T2}", f"orders[{r}]"))
    o.append(boxes(list(row), OX, OY + r * 96, size=82, w=220, color=T2, gap=12, fs=32, ids=f"fo{r}-")[0])
for i, nm in enumerate(["menu", "price", "qty"]):
    o.append(var_box(f"fo-v{i}", nm, "", OX + i * 232, OY + 350, T2, w=220, h=134))
for r, row in enumerate(data_):
    o.append(spot(r + 1, OX, OY + r * 96, 3 * 232 - 12, 82, pad=8, dim=0.35))
    o.append(hlo(g, r, "list", r + 1, w=tw(OUTS["for-orders"]["out"][r], 36) + 24))
    for i, v in enumerate(row):
        o.append(p(f"position:absolute;left:{OX + i * 232 + 3}px;top:{OY + 350 + 55}px;width:214px;height:74px;background:#FFFFFF;font-family:{MONO};font-size:34px;font-weight:700;line-height:74px;text-align:center;color:{INK}", e(v), f' data-build-in="fly order {r + 1}" data-from="fo{r}-{i}"'))
o.append(spot_off(4))
o.append(p(f"position:absolute;left:96px;top:760px;width:1728px;font-size:30px;line-height:1.5;color:{INK}", f"한 번 돌 때마다 {m('menu, price, qty = orders[0]')} 같은 꺼내 담기가 저절로 일어나요.", bi("fade", 4)))
W("for-orders", o, "for 뒤에 이름 세 개를 적으면 주문 튜플 하나가 세 이름에 나눠 들어가요. 앞 장의 menu, price, qty = orders[2]를 for가 주문마다 되풀이하는 셈이에요. 첫 번에는 coffee, 4500, 2가 들어가요. 다음에는 latte 주문, 그다음 cake 주문이에요. 번호를 쓰지 않아도 되고, 주문이 늘어도 코드는 그대로예요.")

# ---------- for total ----------
o = [sec("for-total")] + head(EB2, "for 앞에서 0으로 시작하고, 안에서 합계를 쌓아요", T2)
c, g = nb("for-total", 96, 230, out_order=[1, 2, 3, 4], fs=34)
o += c
o.append(hl(g, 0, 1, "mark", 0))
o.append(lead(0, g.right + 8, g.mid(0), g.right + 60, "for 앞: 한 번만 실행"))
o.append(hl(g, 2, 2, "list", 1))
o.append(lead(1, g.right + 8, g.mid(2) + g.lh / 2, g.right + 60, "for 안: 주문마다 실행"))
o.append(hl(g, 4, 1, "mark", 4))
o.append(hlo(g, 3, "mark", 4, w=230))
o.append(lead(4, g.right + 8, g.mid(4), g.right + 60, "for 밖: 다 돈 뒤 한 번"))
TOX, TOY = 1000, 610
o.append(var_box("ft-var", "total", "", 1560, TOY + 10, BL, w=264, h=160))
steps_ = [("시작", "", "0"), ("coffee", "4500 × 2 = 9000", "9000"), ("latte", "5000 × 1 = 5000", "14000"), ("cake", "6500 × 3 = 19500", "33500")]
for k, (nm, calc, tot) in enumerate(steps_):
    y = TOY + k * 54
    o.append(p(f"position:absolute;left:{TOX}px;top:{y}px;width:540px;font-size:26px;line-height:44px;white-space:nowrap;color:{INK}", f'<b style="display:inline-block;width:120px;color:{T2}">{e(nm)}</b>' + (f'<span style="font-family:{MONO};color:{SUB}">+ {e(calc)}</span>' if calc else ""), bi("fade", k)))
    o.append(p(f"position:absolute;left:1563px;top:{TOY + 10 + 55}px;width:258px;height:102px;background:#FFFFFF;font-family:{MONO};font-size:46px;font-weight:700;line-height:102px;text-align:center;color:{BL}", tot, bi("rise", k)))
    if k:
        o.append(hlo(g, k - 1, "list", k, w=tw(OUTS["for-total"]["out"][k - 1], 34) + 24))
W("for-total", o, "합계는 for 앞에서 total = 0으로 시작하고, for 안에서 total += price * qty로 쌓아요. total = 0은 for 앞에 있어서 한 번만 실행돼요. 들여 쓴 두 줄은 주문마다 실행돼서 total이 9000, 14000, 33500으로 커져요. 마지막 print는 들여 쓰지 않아서 for가 다 끝난 뒤 한 번 실행돼요. total = 0을 for 안에 넣으면 매번 0으로 돌아가서 합계가 쌓이지 않아요.")

# ---------- list errors ----------
o = [sec("list-err")] + head(EB2, "없는 번호와 없는 값은 오류가 나요", T2)
errs = [("list-err1", "menus는 0, 1, 2번까지예요", f"마지막 번호는 {m('len(menus) - 1')}"),
        ("list-err2", "튜플 안은 0, 1, 2번까지예요", "메시지에 list인지 tuple인지 나와요"),
        ("list-err3", "cart에 juice가 없어요", f"{m(chr(34) + 'juice' + chr(34) + ' in cart')} 로 먼저 확인")]
y = 240
for i, (cid, why, fix) in enumerate(errs):
    c, g = nb(cid, 96, y, w=1060, attrs=bi("rise", i) if i else "", fs=32)
    o += c
    o.append(underline(i + 1, g.tx, g.tx + tw(OUTS[cid]["out"][0], 32), g.out(0) + g.lh - 2, RED))
    o.append(err_side(i + 1, 1220, y + 4, why, fix, 604))
    y = g.bottom + 56
W("list-err", o, "리스트와 튜플에 없는 번호를 쓰면 IndexError, 없는 값을 remove하면 ValueError가 나요. menus는 값이 세 개라 마지막 번호는 2예요. orders[0][3]은 튜플 안에서 번호가 넘쳐서 메시지에 tuple이 나와요. remove는 값을 찾아 지우는데, 없는 값이면 ValueError예요. if는 17에서 배워요. 지금은 in으로 들어 있는지 먼저 확인해요. 출력은 실제로 실행한 결과에서 Traceback의 마지막 줄만 옮겼어요.")

# ---------- for errors ----------
o = [sec("for-err")] + head(EB2, "for는 콜론과 들여쓰기를 꼭 지켜요", T2)
errs = [("for-err1", "줄 끝 콜론을 빠뜨렸어요.", f"{m('for menu in menus:')} 처럼 끝에 콜론"),
        ("for-err2", "되풀이할 줄을 들여 쓰지 않았어요.", f"{kbd('Tab')} 한 번이나 빈칸 네 개")]
y = 236
for i, (cid, why, fix) in enumerate(errs):
    c, g = nb(cid, 96, y, w=1728, attrs=bi("rise", i) if i else "", fs=34)
    o += c
    o.append(underline(i + 1, g.tx, g.tx + tw(OUTS[cid]["out"][0], 34), g.out(0) + g.lh - 2, RED))
    r_ = (g.tx + tw("for menu in menus", 34) + 2, g.line(0) + 10, 20, g.lh - 20) if i == 0 else (g.tx, g.line(1) + 8, tw("print(menu)", 34), g.lh - 16)
    o.append(ring(i + 1, *r_, color=OR, width=5))
    o.append(f'<div{bi("fade", i + 1)} style="position:absolute;left:{g.tx}px;top:{g.bottom + 16}px;display:flex;flex-direction:row;gap:24px;align-items:center;white-space:nowrap">'
             + p(f"font-size:28px;font-weight:700;color:{RED}", why) + p(f"font-size:28px;color:{INK}", fix) + '</div>')
    y = g.bottom + 110
o.append(caption("VS Code는 콜론 뒤에 Enter를 치면 네 칸을 자동으로 들여 줘요.", 960, 3))
W("for-err", o, "for 줄 끝에 콜론이 없으면 SyntaxError, 되풀이할 줄을 들여 쓰지 않으면 IndentationError가 나요. SyntaxError 메시지는 콜론이 필요하다는 뜻이에요. IndentationError 메시지는 1번째 줄 for 뒤에 들여 쓴 줄이 있어야 한다는 뜻이에요. 들여쓰기는 빈칸 네 개로 맞춰요. 출력은 실제로 실행한 결과이고, 오류 메시지 뒤 괄호 안의 위치 표시는 빼고 옮겼어요.")

# =====================================================================================
# part 3: three examples
EB3 = "3. 영수증 만들기"

o = [sec("ex-line")] + head(EB3 + " · 예제 1", "주문 한 줄을 칸에 맞춰 찍어요", T3)
c, g = nb("ex-line", 96, 220, wide=True, out_order=[0, 1, 2, 0], fs=30)
o += c
o.append(hl(g, 1, 1, "mark", 0))
CW = g.cw
for j, (s, n, lab) in enumerate([(0, 10, "<10"), (10, 8, ">8"), (18, 5, ">5"), (23, 10, ">10")]):
    o.append(f'<div style="position:absolute;left:{g.tx + s * CW:.0f}px;top:{g.out(0) - 6}px;width:{n * CW:.0f}px;height:{g.lh * 4 + 12}px;background:{"rgba(36,89,201,0.08)" if j % 2 == 0 else "rgba(36,89,201,0.03)"};border-left:2px solid #C9D3EA"></div>')
    o.append(p(f"position:absolute;left:{g.tx + s * CW:.0f}px;top:{g.out(3) + g.lh + 10}px;width:{n * CW:.0f}px;font-family:{MONO};font-size:22px;font-weight:700;text-align:center;color:{BL}", e(lab)))
o.append(hl(g, 3, 1, "err", 1))
o.append(hlo(g, 1, "err", 1, w=40 * CW))
o.append(hl(g, 4, 1, "run", 2))
o.append(hlo(g, 2, "run", 2, w=34 * CW))
NY = g.out(3) + g.lh + 64
o.append(note(0, 96, NY, BL, f"꺼내 담은 {m('menu')}, {m('price')}, {m('qty')}를 칸 수에 맞춰 찍어요. 1파트 칸 맞추기와 2파트 꺼내 담기를 합쳤어요.", w=1728))
o.append(note(1, 96, NY + 64, RED, "한글 머리글만 밀려요. 파이썬은 한글을 한 칸으로 세지만 화면에서는 두 칸이에요.", w=1728))
o.append(note(2, 96, NY + 128, GR, f"한글 글자 수만큼 칸 수를 빼요. {m('메뉴명')}은 세 글자라 {m('<10')} 대신 {m('<7')}", w=1728))
W("ex-line", o, "주문 한 건을 꺼내 담고 칸 수를 정해 찍으면 머리글과 세로줄이 맞아요. 메뉴는 왼쪽 열 칸, 가격은 콤마와 함께 오른쪽 여덟 칸, 수량은 다섯 칸, 금액은 열 칸이에요. 영어 머리글은 칸이 맞는데 한글 머리글만 밀려요. 파이썬은 한글 한 글자를 한 칸으로 세지만 화면에서는 두 칸 너비라서 그래요. 그래서 한글 머리글은 한글 글자 수만큼 칸 수를 빼요. 글꼴에 따라 조금 어긋나면 머리글을 영어로 써요. 출력의 한글은 슬라이드에서 영어 두 칸 너비로 그렸어요. 3파트도 새 커널에서 실제로 실행한 결과예요.", ("examples", "영수증 만들기"))

# ---------- example 2 ----------
o = [sec("ex-receipt")] + head(EB3 + " · 예제 2", "for 두 줄로 영수증 한 장을 찍어요", T3)
c, g = nb("ex-receipt", 96, 214, out=False, fs=28)
o += c
PX, PY, PLH, PP = 1310, 214, 40, 26
o.append(paper(PX, PY, 520, RECEIPT, fs=24, lh=PLH, pid="er-paper", pad=PP))
groups = [(0, 5, "mark", 1, 0, 5), (6, 3, "list", 2, 5, 3), (9, 3, "run", 3, 8, 3)]
for (l0, n, kind, order_, r0, rn) in groups:
    o.append(hl(g, l0, n, kind, order_))
    o.append(f'<div{bi("fade", order_)} style="position:absolute;left:{PX + PP - 10}px;top:{PY + PP + r0 * PLH}px;width:{520 - 2 * PP + 20}px;height:{rn * PLH}px;border-radius:4px;background:{TINT[kind]}"></div>')
o.append(hl(g, 5, 1, "skip", 3))
o.append(caption("같은 색끼리 짝이에요. 주문이 열 건으로 늘어도 셀은 그대로예요.", 940, 4))
W("ex-receipt", o, "for로 주문 줄을 찍으면 주문이 몇 건이든 셀 하나로 영수증 한 장이 나와요. 위 다섯 줄은 테두리, 가게 이름, 머리글이에요. ^는 가운데 맞춤이에요. total = 0은 for 앞에서 한 번, 들여 쓴 두 줄은 주문마다 실행돼요. 다 돈 뒤에 합계와 테두리를 찍어요. 2파트의 합계 쌓기와 같은 흐름에 1파트의 칸 맞추기를 더했어요. 오른쪽 영수증은 이 셀을 실제로 실행한 결과예요. 한글은 영어 두 칸 너비로 그렸어요.")

# ---------- example 3 ----------
o = [sec("ex-memo")] + head(EB3 + " · 예제 3", "주문 메모 한 줄을 정리해서 다시 글자로", T3)
c, g = nb("ex-memo", 96, 220, out_order=[3, 5], fs=26)
o += c
MX_, MY_, MB = 1200, 236, 118
stages = [("split", ["latte", "cake", "latte", "coffee", "latte"], 1), ("remove · append", ["latte", "cake", "latte", "latte", "tea"], 2), ("sort", ["cake", "latte", "latte", "latte", "tea"], 4)]
for j, (lab, items, order_) in enumerate(stages):
    y = MY_ + j * 150
    o.append(p(f"position:absolute;left:{MX_}px;top:{y}px;font-family:{MONO};font-size:24px;font-weight:700;color:{T2}", e(lab), bi("fade", order_)))
    o.append(boxes(items, MX_, y + 42, size=62, w=MB, color=T2, gap=8, fs=24, fill=(4,) if j == 1 else (), attrs=bi("rise", order_))[0])
o.append(p(f"position:absolute;left:{MX_ + 3 * (MB + 8)}px;top:{MY_ + 150}px;font-size:22px;font-weight:700;color:{RED}", "coffee 취소, tea 추가", bi("fade", 2)))
o.append(hl(g, 1, 1, "list", 1))
o.append(hl(g, 2, 2, "list", 2))
o.append(hl(g, 4, 1, "run", 3))
o.append(hlo(g, 0, "run", 3, w=tw(OUTS["ex-memo"]["out"][0], 26) + 24))
o.append(hl(g, 5, 1, "list", 4))
o.append(hl(g, 6, 1, "run", 5))
o.append(hlo(g, 1, "run", 5, w=tw(OUTS["ex-memo"]["out"][1], 26) + 24))
o.append(arrow(5, [(MX_ + 310, MY_ + 2 * 150 + 116), (MX_ + 310, MY_ + 2 * 150 + 166)], T1))
o.append(p(f"position:absolute;left:{MX_}px;top:{MY_ + 2 * 150 + 180}px;font-family:{MONO};font-size:26px;font-weight:700;color:{T1};white-space:pre", e('"cake / latte / latte / latte / tea"'), bi("rise", 5)))
o.append(caption(f"{m('split')}으로 리스트가 되면 리스트 메서드를 다 쓸 수 있어요. 다 고친 뒤 {m('join')}으로 다시 이어요.", 940, 6))
W("ex-memo", o, "주문 메모를 split으로 리스트로 바꾸면 리스트 메서드로 고치고 센 다음, join으로 다시 한 줄 글자로 만들 수 있어요. 메모는 쉼표로 이어진 문자열 하나예요. split(\",\")으로 다섯 칸 리스트가 돼요. coffee 주문을 remove로 지우고 tea를 append로 더해요. len은 주문 수, count는 latte 잔 수예요. sort로 이름순 정렬한 뒤 join으로 다시 이어요.")

# =====================================================================================
# wrap-up
EB4 = "정리"
o = [sec("trouble")] + head(EB4, "막히면 오류의 마지막 줄부터 읽어요", GRAY)
rows_ = [("IndexError: ... index out of range", "없는 번호예요. 마지막 번호는 len() - 1"),
         ("TypeError: not enough arguments for format string", "% 자리 수와 값 수가 달라요. f-string으로"),
         ("ValueError: unsupported format character ','", "% 에는 콤마가 없어요. f\"{price:,}\""),
         ("ValueError: list.remove(x): x not in list", "없는 값을 지우려 했어요. in으로 먼저 확인"),
         ("TypeError: 'tuple' object does not support item assignment", "튜플과 문자열은 못 바꿔요. 리스트에 담아요"),
         ("SyntaxError: expected ':'", "for 줄 끝에 콜론"),
         ("IndentationError: expected an indented block ...", "되풀이할 줄을 네 칸 들여 쓰기")]
TY = 220
for r, (a_, b_) in enumerate(rows_):
    y = TY + r * 100
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:100px;border-bottom:1px solid #D9D5CB"></div>')
    o.append(p(f"position:absolute;left:110px;top:{y + 30}px;width:1000px;font-family:{MONO};font-size:24px;font-weight:700;white-space:pre;color:{RED}", e(a_)))
    o.append(p(f"position:absolute;left:1130px;top:{y + 28}px;width:694px;font-size:27px;color:{INK}", e(b_)))
W("trouble", o, "오류가 나면 위쪽 Traceback보다 맨 아래 줄을 먼저 읽어요. 마지막 줄에 오류 이름과 이유가 있어요. IndexError는 없는 번호, TypeError는 타입이 안 맞거나 바꿀 수 없는 값을 바꾸려 할 때예요. ValueError는 값이 안 맞을 때예요. SyntaxError와 IndentationError는 문법과 들여쓰기 문제예요.", ("trouble", "정리"))

o = [sec("cheatsheet")] + head(EB4, "언제 무엇을 쓰는지", GRAY)
rows_ = [("글자 꺼내기, 자르기", "word[0]  word[0:2]  word[::-1]", T1), ("값을 문장에 끼워 넣기", 'f"{menu} {qty}개"', T1),
         ("칸, 소수점, 콤마 맞추기", '{qty:>5}  {pi:.2f}  {price:,}', T1), ("값 여러 개 담고 고치기", "[ ]  append  insert  remove  pop  sort", T2),
         ("묶어 두고 안 바꿀 값", '( )  menu, price, qty = order', T2), ("글자와 리스트 오가기", 'split(",")  " / ".join(words)', T2),
         ("하나씩 꺼내 되풀이하기", "for menu, price, qty in orders:", T2)]
TY = 210
for r, (a_, b_, col) in enumerate(rows_):
    y = TY + r * 84
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:84px;border-bottom:1px solid #D9D5CB"></div>')
    o.append(p(f"position:absolute;left:110px;top:{y + 20}px;width:560px;font-size:28px;font-weight:700;color:{INK}", e(a_)))
    o.append(p(f"position:absolute;left:690px;top:{y + 20}px;font-family:{MONO};font-size:28px;font-weight:700;white-space:pre;color:{col}", e(b_)))
o.append(f'<div style="position:absolute;left:96px;top:830px;width:1728px;height:150px;background:#EDEBE4;border-radius:18px;padding:30px 36px;display:flex;flex-direction:column;gap:10px">'
         + p(f"font-size:26px;font-weight:700;color:{T2}", "다음: 14 · 파이썬 기초 3")
         + p(f"font-size:28px;color:{INK}", f"{m('in')}, {m('not in')}으로 묻기와 {m('scores[1][2]')} 같은 2차원 리스트를 정리해요.") + '</div>')
W("cheatsheet", o, "이번 챕터에서 배운 것을 언제 쓰는지 한 장에 모았어요. 문자열은 번호로 꺼내고 자르고, f-string으로 칸, 소수점, 콤마를 맞춰요. 값 여러 개는 리스트에 담아 메서드로 고치고, 바꾸지 않을 묶음은 튜플에 담아요. split과 join으로 글자와 리스트를 오가요. for로 하나씩 꺼내 되풀이해요. 14에서는 in과 2차원 리스트를 더 연습해요.")
# =====================================================================================
# toc
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
TOC = [("1", "문자열과 출력", "자르기, sep과 end, %, format(), f-string, 칸 수, 소수점, 콤마", "str-make", "fmt-err", T1),
       ("2", "리스트, 튜플, for", "[ ]와 ( ), 메서드, split과 join, 주문 데이터, 꺼내 담기, for", "list-make", "for-err", T2),
       ("3", "영수증 만들기", "주문 한 줄, for로 영수증 한 장, 주문 메모 정리", "ex-line", "ex-memo", T3),
       ("", "정리", "막힐 때, 언제 무엇을 쓰는지", "trouble", "cheatsheet", GRAY)]
t = [sec("toc"), f'<h2 style="position:absolute;left:96px;top:80px;font-size:60px;font-weight:700;line-height:1.2;color:{INK}">오늘의 순서</h2>']
for i, (n_, h_, s_, a_, b_, col) in enumerate(TOC):
    y = 210 + i * 132
    t.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:132px;border-bottom:1px solid #D9D5CB"></div>')
    t.append(f'<div style="position:absolute;left:96px;top:{y + 30}px;width:8px;height:72px;border-radius:4px;background:{col}"></div>')
    t.append(p(f"position:absolute;left:130px;top:{y + 34}px;width:60px;font-size:48px;font-weight:900;line-height:64px;color:{col}", n_))
    t.append(p(f"position:absolute;left:200px;top:{y + 38}px;width:460px;font-size:34px;font-weight:700;line-height:56px;color:{INK}", h_))
    t.append(p(f"position:absolute;left:680px;top:{y + 44}px;width:960px;font-size:26px;line-height:44px;color:{SUB}", e(s_)))
    t.append(p(f"position:absolute;left:1640px;top:{y + 44}px;width:184px;font-size:26px;font-weight:700;line-height:44px;text-align:right;color:{col}", f"{page[a_]}–{page[b_]}쪽"))
t.append(f'<div style="position:absolute;left:96px;top:800px;width:1728px;height:150px;background:#EDEBE4;border-radius:18px;padding:28px 36px;display:flex;flex-direction:column;gap:14px">'
         + p(f"font-size:26px;font-weight:700;color:{JP}", "준비")
         + f'<div style="display:flex;flex-direction:row;gap:14px;align-items:center;font-size:28px;color:{INK};white-space:nowrap">VS Code로 hello-uv 열기 <span style="color:{GRAY}">·</span> {m("basics.ipynb", JP)} 열기 <span style="color:{GRAY}">·</span> 커널 {m(".venv", GR)} 확인 <span style="color:{GRAY}">·</span> 셀마다 {kbd("Shift+Enter")}</div></div>')
TOC_NOTE = "1파트는 문자열과 출력 모양, 2파트는 리스트와 튜플과 for, 3파트는 둘을 합친 예제 세 개예요. 12에서 쓰던 hello-uv 폴더의 basics.ipynb에 이어서 적어요. 커널은 09에서 고른 .venv예요. 셀은 위에서부터 차례로 실행해요. 2파트는 1파트 변수를 쓰지 않아요."
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(t) + f"\n<aside>{e(TOC_NOTE)}</aside>\n</section>\n")

DECK_TITLE = "파이썬 기초 2 (문자열, 리스트, for)"
deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-02T03:00:00Z"}, "lists": "css", "title": DECK_TITLE, "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
print(len(ORDER), "slides")
