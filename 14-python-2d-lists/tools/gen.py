"""Generates every slide of the Python basics 3 deck (14) and slides/deck.json.

Story: keeps writing in basics.ipynb from chapters 12 and 13. Part 1 asks whether a value is in a list, tuple or
string with in and not in. Part 2 puts table-shaped data into a list of lists. Part 3 uses both on a report card,
a seat map and a cafe's sales table.
Every cell and output comes from tools/demo.sh (tools/run_nb.py runs the cells with the project kernel).

Layout rules (Stageshow skill, tools/DESIGN.md): one focal object per slide, labels sit on the code line or the
picture (leader tags) instead of cards, say it once, no empty bands, values move instead of swapping.
Highlights (tools/HIGHLIGHT.md) change from slide to slide: line tints, pen ring and underline, spotlight,
cursor click, values flying into place. No typing animation.
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
BL, GR, OR, RED, GRAY = "#2459C9", "#1F8A4C", "#B26A00", "#A33131", "#6A7180"
JP = "#B8560F"          # Jupyter, same as chapters 09 and 10
SEL = "#2F7DE1"         # selected cell bar, like VS Code's focus color
T1, T1BG = "#0F7C86", "#E2F2F3"     # part 1: in
T6, T6BG = "#A23B72", "#F6E7EF"     # part 2: 2D lists
T3, T3BG = OR, "#FBEEDB"            # part 3: real examples
HL = {"run": "rgba(31,138,76,0.16)", "skip": "rgba(106,113,128,0.20)", "err": "rgba(163,49,49,0.14)",
      "mark": "rgba(36,89,201,0.13)", "t1": "rgba(15,124,134,0.15)", "t6": "rgba(162,59,114,0.13)", "t3": "rgba(178,106,0,0.15)"}
REAL = " 출력은 실제로 실행한 결과예요."


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


def sec(sid, bg="#F6F5F1"):
    return f'<section id="{sid}" data-transition="fade" style="background:{bg};color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">'


def head(eyebrow, title, color):
    return [p(f"position:absolute;left:96px;top:48px;width:1728px;font-size:26px;font-weight:700;color:{color}", e(eyebrow), ' id="eyebrow"'),
            f'<h2 id="title" style="position:absolute;left:96px;top:92px;width:1728px;font-size:56px;font-weight:700;line-height:1.2;color:{INK}">{title}</h2>']


def caption(text, order=None, top=930):
    return p(f"position:absolute;left:96px;top:{top}px;width:1728px;font-size:34px;font-weight:700;line-height:1.4;color:{INK}", text,
             ' id="caption"' + (bi("rise", order) if order else ' data-build-in="rise"'))


def num(i, color, size=56):
    return p(f"width:{size + 16}px;height:{size + 16}px;flex:none;border-radius:50%;background:{color};color:#FFFFFF;font-size:{size * 0.6:.0f}px;font-weight:900;line-height:{size + 16}px;text-align:center", str(i))


def kbd(text, size=30):
    caps = [p(f"font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.2;white-space:nowrap;color:{INK};background:#FFFFFF;border:2px solid #C9CED8;border-bottom-width:5px;border-radius:10px;padding:6px 14px", e(k)) for k in text.split("+")]
    plus = p(f"font-size:{size * 0.8:.0f}px;font-weight:700;color:{GRAY}", "+")
    return '<div style="display:flex;flex-direction:row;align-items:center;gap:8px">' + plus.join(caps) + '</div>'


def arrow(w=56, color="#C9CED8", h=28):
    return f'<x-shape kind="arrow-right" style="width:{w}px;height:{h}px;flex:none;background:{color}"></x-shape>'


# ---------- notebook cell, drawn so code lines and outputs can be pointed at ----------
F = [30]          # code font size of the slide being drawn


def LH():
    return F[0] * 1.45


def cell(c, left, top, w, sel=True, attrs=""):
    """c: dict(id, lines, n, out, oo={output index: build order}). Each code line gets id <id>-l<i>,
    each output line <id>-o<j>, so highlights and flying values can use them."""
    fs, lines, n = F[0], c.get("lines", [""]), c.get("n")
    cid = c["id"]
    o = [f'<div id="{cid}"{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;display:flex;flex-direction:column;gap:10px">']
    bar = f'<div style="width:7px;flex:none;border-radius:4px;background:{SEL if sel else "transparent"}"></div>'
    gutter = p(f"width:58px;flex:none;font-family:{MONO};font-size:22px;color:{GRAY};text-align:right;padding-top:12px", f"[{n}]" if n else "[ ]")
    txt = "".join(p(f"font-family:{MONO};font-size:{fs}px;line-height:1.45;white-space:pre;color:{INK}", e(l) if l else "&#160;", f' id="{cid}-l{i}"') for i, l in enumerate(lines))
    tag_ = p(f"position:absolute;right:14px;bottom:8px;font-size:18px;color:{GRAY}", "Python")
    bx = f'<div style="flex:1;position:relative;background:#FFFFFF;border:2px solid {LINE};border-radius:10px;padding:8px 18px 8px;display:flex;flex-direction:column">{txt}{tag_}</div>'
    o.append(f'<div style="display:flex;flex-direction:row;gap:10px;align-items:stretch">{bar}{gutter}{bx}</div>')
    oo = c.get("oo", {})
    for j, l in enumerate(c.get("out", [])):
        col = RED if re.match(r"[A-Za-z]+Error", l) else INK
        o.append(p(f"margin-left:85px;padding:0 20px;font-family:{MONO};font-size:{fs}px;line-height:1.45;white-space:pre;color:{col}", e(l) if l else "&#160;",
                   f' id="{cid}-o{j}"' + bi("fade", oo.get(j))))
    o.append('</div>')
    return o


def cell_h(c):
    return 20 + len(c["lines"]) * LH() + sum(10 + LH() for _ in c.get("out", []))


def hl(left, top, w, i, n=1, kind="mark", order=1):
    """Tints code lines i .. i+n-1 of the cell drawn at (left, top)."""
    y = top + 10 + i * LH()
    return f'<div{bi("fade", order)} style="position:absolute;left:{left + 87}px;top:{y:.0f}px;width:{w - 89}px;height:{n * LH():.0f}px;background:{HL[kind]};border-radius:6px"></div>'


def ly(top, i):
    """Centre y of code line i."""
    return top + 10 + i * LH() + LH() / 2


def oy(top, n, j):
    """Centre y of output line j of a cell with n code lines."""
    return top + 20 + n * LH() + 10 + j * (LH() + 10) + LH() / 2


def tw(s, fs=None):
    """Rendered width of a code string: Hangul is about one em, the rest 0.6 em."""
    fs = fs or F[0]
    return sum(fs * (1.0 if '가' <= ch <= '힣' else 0.6) for ch in s)


def cx(left, s="", col=0):
    """x where column col of a code line starts (or just after string s)."""
    return left + 105 + tw(s) + col * F[0] * 0.6


def tx(left, lines, gap=36):
    """x just right of the longest of the given strings inside a cell at left."""
    return int(left + 105 + max(tw(l) for l in lines) + gap)


def tag(x, y, text, color, order=None, size=28, lead=True, anim="fade", w=None):
    """A leader label: '← text' centred on y. No box."""
    ws = f"width:{w}px;white-space:normal;" if w else "white-space:nowrap;"
    return p(f"position:absolute;left:{x:.0f}px;top:{y - size * 0.72:.0f}px;{ws}font-size:{size}px;font-weight:700;line-height:1.45;color:{color}",
             ("← " if lead else "") + text, bi(anim, order))


def lit(x, y, w, h, order, color=T6, bg=None, anim="fade", r=12, width=4):
    """A tinted frame laid over part of a picture."""
    return f'<div{bi(anim, order)} style="position:absolute;left:{x:.0f}px;top:{y:.0f}px;width:{w:.0f}px;height:{h:.0f}px;border:{width}px solid {color};border-radius:{r}px;background:{bg or "transparent"}"></div>'


def mono(text, size=30, color=INK, extra=""):
    return p(f"font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.4;color:{color};white-space:pre;{extra}", e(text))


def tf(v, size=30):
    c, b = (GR, "#E6F4EC") if v == "True" else (RED, "#F8E6E6")
    return p(f"display:inline-block;font-family:{MONO};font-size:{size}px;font-weight:700;color:{c};background:{b};border-radius:10px;padding:2px 16px;white-space:nowrap", v)


# ---------- grid: a list of lists drawn as a table, every cell placed by hand ----------
class Grid:
    def __init__(self, rows, left, top, cw, ch, fs, pre, color=T6, cols=None, rows_lbl=None, gap=8, lbl=26, head=True, side=True,
                 hi=(), hi_color=None, hi_bg=None, dark=False):
        self.rows, self.left, self.top, self.cw, self.ch, self.gap, self.pre = rows, left, top, cw, ch, gap, pre
        self.fs, self.color, self.lbl, self.dark = fs, color, lbl, dark
        self.rw = (lbl * 1.6 + 14) if side else 0
        self.hh = ((lbl * 1.35 + (lbl * 1.25 if cols else 0)) + 10) if head else 0
        self.cols, self.rows_lbl, self.head, self.side = cols, rows_lbl, head, side
        self.hi, self.hi_color, self.hi_bg = set(hi), hi_color or color, hi_bg

    def x(self, j):
        return self.left + self.rw + j * (self.cw + self.gap)

    def y(self, i):
        return self.top + self.hh + i * (self.ch + self.gap)

    def rect(self, i, j):
        return self.x(j), self.y(i), self.cw, self.ch

    def row_rect(self, i, j0=0, j1=None):
        j1 = len(self.rows[0]) - 1 if j1 is None else j1
        return self.x(j0), self.y(i), self.x(j1) + self.cw - self.x(j0), self.ch

    def col_rect(self, j, i0=0, i1=None):
        i1 = len(self.rows) - 1 if i1 is None else i1
        return self.x(j), self.y(i0), self.cw, self.y(i1) + self.ch - self.y(i0)

    @property
    def right(self):
        return self.x(len(self.rows[0]) - 1) + self.cw

    @property
    def bottom(self):
        return self.y(len(self.rows) - 1) + self.ch

    def group(self, cells, attrs):
        """cells: [(i, j, v, bg, border)]. One box around them all, so fly and pop move them together."""
        xs = [self.x(j) for i, j, *_ in cells]
        ys = [self.y(i) for i, j, *_ in cells]
        x0, y0 = min(xs), min(ys)
        w, h = max(xs) + self.cw - x0, max(ys) + self.ch - y0
        inner = "".join(self.value_cell(i, j, v, bg=bg, border=bd, ox=x0, oy=y0) for i, j, v, bg, bd in cells)
        return f'<div{attrs} style="position:absolute;left:{x0:.0f}px;top:{y0:.0f}px;width:{w:.0f}px;height:{h:.0f}px">{inner}</div>'

    def value_cell(self, i, j, v, attrs="", color=None, bg=None, border=None, sid=None, ox=0, oy=0):
        bgc = bg or ("#252B36" if self.dark else CARD)
        bd = border or ("#3A4150" if self.dark else LINE)
        ink = color or ("#E6E9EF" if self.dark else INK)
        x, y, w, h = self.rect(i, j)
        x, y = x - ox, y - oy
        sid = f' id="{sid}"' if sid else ""
        return (f'<p{sid}{attrs} style="position:absolute;left:{x:.0f}px;top:{y:.0f}px;width:{w}px;height:{h}px;border-radius:12px;border:3px solid {bd};background:{bgc};'
                f'font-family:{MONO};font-size:{self.fs}px;font-weight:700;line-height:{h - 6}px;text-align:center;color:{ink};white-space:pre">{e(str(v))}</p>')

    def html(self, attrs="", only_rows=None, only_cols=None):
        o = [f'<div{attrs} style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none">']
        nr, nc = len(self.rows), len(self.rows[0])
        if self.head:
            for j in range(nc):
                if only_cols is not None and j not in only_cols:
                    continue
                sub = f'<br><span style="font-family:{SANS};font-size:{self.lbl - 2}px;color:{GRAY}">{e(self.cols[j])}</span>' if self.cols else ""
                o.append(p(f"position:absolute;left:{self.x(j):.0f}px;top:{self.top:.0f}px;width:{self.cw}px;text-align:center;font-family:{MONO};font-size:{self.lbl}px;font-weight:700;color:{self.color};line-height:1.25", str(j) + sub))
        for i in range(nr):
            if only_rows is not None and i not in only_rows:
                continue
            if self.side:
                lab = str(i) + (f' <span style="font-family:{SANS};font-size:{self.lbl - 4}px;color:{GRAY}">{e(self.rows_lbl[i])}</span>' if self.rows_lbl else "")
                o.append(p(f"position:absolute;left:{self.left - (60 if self.rows_lbl else 0):.0f}px;top:{self.y(i):.0f}px;width:{self.rw - 14 + (60 if self.rows_lbl else 0):.0f}px;height:{self.ch}px;text-align:right;font-family:{MONO};font-size:{self.lbl}px;font-weight:700;line-height:{self.ch}px;color:{self.color};white-space:nowrap", lab))
            for j in range(nc):
                if only_cols is not None and j not in only_cols:
                    continue
                on = (i, j) in self.hi
                o.append(self.value_cell(i, j, self.rows[i][j], sid=f"{self.pre}-{i}-{j}",
                                         bg=(self.hi_bg if on else None), border=(self.hi_color if on else None)))
        o.append('</div>')
        return "".join(o)


def fly_cell(g, i, j, v, order, src, color=T6, bg=T6BG):
    """A new value that flies from #src and lands over grid cell (i, j)."""
    return g.value_cell(i, j, v, f' data-build-in="fly order {order}" data-from="{src}"', bg=bg, border=color)


def pop_cell(g, i, j, v, order, color=T6, bg=T6BG):
    return g.value_cell(i, j, v, bi("pop", order), bg=bg, border=color)


def slots(items, left, top, w, h, fs, pre, gap=12, color=None, bg=None, attrs="", lbl=True, lcolor=T1):
    """A 1-D list as a row of boxes, index numbers above. Box k has id <pre>-<k>."""
    o = [f'<div{attrs} style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none">']
    for k, it in enumerate(items):
        x = left + k * (w + gap)
        if lbl:
            o.append(p(f"position:absolute;left:{x}px;top:{top}px;width:{w}px;text-align:center;font-family:{MONO};font-size:24px;font-weight:700;color:{lcolor}", str(k)))
        o.append(p(f"position:absolute;left:{x}px;top:{top + (40 if lbl else 0)}px;width:{w}px;height:{h}px;border-radius:12px;border:3px solid {color or LINE};background:{bg or CARD};"
                   f"font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:{h - 6}px;text-align:center;color:{INK};white-space:pre", e(it), f' id="{pre}-{k}"'))
    o.append('</div>')
    return "".join(o)


def rule_rows(left, top, w, rows, widths, order0=1, rh=84, head_=None, fs=28, orders=None, colors=None):
    """A light table: header in gray, rows split by thin rules, no boxes. Cells may be (text, 'code'|'sans', color)."""
    o = []
    y = top
    if head_:
        o.append(f'<div style="position:absolute;left:{left}px;top:{y}px;width:{w}px;height:52px;display:flex;flex-direction:row;align-items:center;gap:24px;border-bottom:3px solid {INK}">'
                 + "".join(p(f"width:{cw}px;flex:none;font-size:24px;font-weight:700;color:{GRAY}", c) for c, cw in zip(head_, widths)) + '</div>')
        y += 60
    for i, r in enumerate(rows):
        cs = ""
        for k, (c, cw) in enumerate(zip(r, widths)):
            if isinstance(c, tuple):
                t, kind, col = (c + (INK,))[:3]
            else:
                t, kind, col = c, ("sans" if k == 0 else "code"), (SUB if k == 0 else INK)
            fam = MONO if kind == "code" else SANS
            cs += p(f"width:{cw}px;flex:none;font-family:{fam};font-size:{fs}px;font-weight:700;color:{col};white-space:pre", t)
        od = orders[i] if orders else order0 + i
        o.append(f'<div{bi("rise", od)} style="position:absolute;left:{left}px;top:{y + i * rh}px;width:{w}px;height:{rh}px;display:flex;flex-direction:row;align-items:center;gap:24px;border-bottom:2px solid {LINE}">{cs}</div>')
    return o


def svg_lines(lines, color="#C9CED8", width=4, attrs="", head=True):
    """Straight connector lines [(x1, y1, x2, y2)], each ending in an arrow head."""
    marker = (f'<defs><marker id="ah{abs(hash(str(lines))) % 99999}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
              f'<path d="M0,0 L10,5 L0,10 z" fill="{color}"/></marker></defs>') if head else ""
    mid = f"ah{abs(hash(str(lines))) % 99999}"
    ls = "".join(f'<line x1="{a}" y1="{b}" x2="{c}" y2="{d}" stroke="{color}" stroke-width="{width}" stroke-linecap="round"' + (f' marker-end="url(#{mid})"' if head else "") + '/>' for a, b, c, d in lines)
    return f'<svg{attrs} viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible">{marker}{ls}</svg>'


NB = "basics.ipynb"
EB1 = "1. in과 not in"
EB2 = "2. 2차원 리스트"
EB3 = "3. 실제로 써 보기"
SC0 = [[90, 85, 77], [70, 95, 88], [60, 75, 99]]
SC1 = [[90, 100, 77], [70, 95, 88], [65, 80, 90]]
SUBJ = ["kor", "eng", "math"]

# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#F2B27A;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
       '<h1 style="font-size:92px;font-weight:900;line-height:1.1;color:#F6F5F1">파이썬 기초 3<br>in과<br>2차원 리스트</h1>',
       '<p style="font-size:40px;line-height:1.4;color:#BFC6D4">들어 있는지 묻고,<br>표 모양 데이터 다루기</p>']
g = Grid(SC0, 1150, 250, 180, 124, 54, "cov", color="#8A93A6", lbl=28, dark=True, hi={(1, 2)}, hi_color="#E6A3C8", hi_bg="#4A2D3E")
cov.append(g.html())
cov.append(f'<div style="position:absolute;left:{g.x(0):.0f}px;top:{g.bottom + 56:.0f}px;display:flex;flex-direction:row;align-items:center;gap:28px">'
           + p(f"font-family:{MONO};font-size:44px;font-weight:700;color:#E6A3C8;white-space:pre", "scores[1][2]") + arrow(56, "#5A6172", 32)
           + p(f"font-family:{MONO};font-size:44px;font-weight:700;color:#E6E9EF", "88") + '</div>')
W("cover", cov, "이번 챕터는 리스트를 두 가지로 더 써 봐요. 1파트는 in과 not in으로 값이 들어 있는지 True, False로 묻는 법이에요. 2파트는 리스트 안에 리스트를 넣은 2차원 리스트로 성적표 같은 표 모양 데이터를 다뤄요. 3파트에서 둘을 섞어 성적표, 좌석표, 카페 판매표를 만들어요. 모든 예제는 12, 13에서 쓰던 노트북에 이어서 적고 실행해요.", ("intro", "들어가기"))

ORDER.append("toc")   # written last, after page numbers are known

# ---------- ready ----------
o = [sec("ready")] + head("들어가기", "13에서 이어서 해요", JP)
done = [("hello-uv 노트북, 커널 .venv", "09"), ("비교와 and, or, not", "12"), ("리스트, 튜플, count, index", "13"), ("for 문, += 로 합계 쌓기", "13"), ("f-string 칸 수 맞추기", "13")]
for i, (a_, b_) in enumerate(done):
    o.append(f'<div{bi("rise", min(i + 1, 3))} style="position:absolute;left:96px;top:{236 + i * 120}px;width:760px;height:104px;display:flex;flex-direction:row;gap:24px;align-items:center;border-bottom:2px solid {LINE}">'
             + f'<x-icon name="CheckCircle" style="width:48px;height:48px;flex:none;color:{GR}"></x-icon>'
             + p(f"flex:1;font-size:34px;font-weight:700;color:{INK}", e(a_))
             + p(f"font-size:30px;font-weight:700;color:{GRAY}", e(b_)) + '</div>')
o.append(p(f"position:absolute;left:1000px;top:262px;font-size:36px;font-weight:700;color:{JP}", "노트북 다시 열기", bi("rise", 4)))
steps_ = [p(f"font-size:32px;color:{INK}", "VS Code로 hello-uv 폴더 열기"),
          p(f"font-size:32px;color:{INK}", "탐색기에서") + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{JP}", NB) + p(f"font-size:32px;color:{INK}", "열기"),
          p(f"font-size:32px;color:{INK}", "오른쪽 위 커널이 .venv인지 보기"),
          p(f"font-size:32px;color:{INK}", "셀에 적고") + kbd("Shift+Enter", 26) + p(f"font-size:32px;color:{INK}", "로 실행")]
for i, inner in enumerate(steps_):
    o.append(f'<div{bi("rise", 4)} style="position:absolute;left:1000px;top:{356 + i * 120}px;width:824px;height:104px;display:flex;flex-direction:row;gap:20px;align-items:center;border-bottom:2px solid {LINE}">'
             + num(i + 1, JP, 40) + inner + '</div>')
o.append(caption("기억이 안 나면 줄 끝에 적힌 챕터를 먼저 다시 봐요.", 5, 900))
W("ready", o, "09에서 만든 hello-uv 폴더를 열고 12, 13에서 쓰던 basics.ipynb에 이어서 적어요. 12의 비교와 and, or, not, 13의 리스트, 튜플, for, f-string을 그대로 써요. 셀 번호는 파트마다 [1]부터 다시 셌어요. 슬라이드의 출력은 tools/demo.sh가 hello-uv 커널에서 같은 셀을 실제로 실행한 결과예요.")

# ---------- part 1: in / not in ----------
o = [sec("in-why")] + head(EB1, "count나 index로 있는지 물으면 한 번 더 따져야 해요", T1)
T, Wd = 240, 1180
c = {"id": "c-iw", "lines": ['menu = ["coffee", "latte", "cake"]', 'print(menu.count("juice"))', 'menu.index("juice")'], "n": 1, "out": ["0", "ValueError: 'juice' is not in list"]}
o += cell(c, 96, T, Wd)
o.append(hl(96, T, Wd, 1, 1, "t1", 1))
o.append(tag(tx(96, ["0"]), oy(T, 3, 0), "0개라서 없다는 뜻이에요", T1, 1))
o.append(hl(96, T, Wd, 2, 1, "err", 2))
EW = tw("ValueError: 'juice' is not in list")
o.append(box(2, cx(96) - 12, oy(T, 3, 1) - 27, EW + 24, 54))
o.append(tag(cx(96) + EW + 40, oy(T, 3, 1), "없으면 오류로 멈춰요", RED, 2))
o.append(p(f"position:absolute;left:96px;top:660px;font-size:32px;font-weight:700;color:{T1}", "있는지만 묻고 싶을 때는 이렇게 써요", bi("fade", 3)))
o.append(f'<div{bi("rise", 3)} style="position:absolute;left:96px;top:726px;display:flex;flex-direction:row;align-items:center;gap:36px">'
         + mono('"juice" in menu', 64, INK) + arrow(80, "#C9CED8", 40) + tf("False", 64) + '</div>')
W("in-why", o, "13에서 배운 count와 index로도 값이 있는지 알 수는 있어요. count는 개수를 세니까 0이 나오면 없다는 뜻이에요. 다만 0이라는 숫자를 보고 없다고 한 번 더 바꿔 생각해야 해요. index는 없는 값을 찾으면 ValueError로 멈춰요. 있는지만 묻고 싶을 때는 in을 써요. 답이 바로 True나 False로 나와요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("in", "in과 not in"))

o = [sec("in-list")] + head(EB1, "in은 들어 있으면 True, 없으면 False예요", T1)
F[0] = 38
T, Wd = 236, 900
c = {"id": "c-il", "lines": ['print("latte" in menu)', 'print("juice" in menu)', 'print("juice" not in menu)', 'print("latte" not in menu)'], "n": 2, "out": ["True", "False", "True", "False"]}
o += cell(c, 96, T, Wd)
ilt = [("latte가 있어요", GR), ("juice는 없어요", RED), ("없는 게 맞아요", GR), ("있으니까 틀렸어요", RED)]
for i, (t_, col) in enumerate(ilt):
    o.append(tag(tx(96, ["False"]), oy(T, 4, i), t_, col, i + 1))
o.append(p(f"position:absolute;left:1100px;top:250px;font-family:{MONO};font-size:30px;font-weight:700;color:{T1}", "menu"))
SLX, SLW = 1100, 230
o.append(slots(["coffee", "latte", "cake"], SLX, 300, SLW, 110, 36, "il-s"))
o.append(lit(SLX + (SLW + 12), 340, SLW, 110, 1, T1, HL["t1"]))
o.append(f'<p{bi("rise", 2)} style="position:absolute;left:{SLX}px;top:490px;width:{SLW}px;height:110px;border-radius:12px;border:3px dashed {RED};font-family:{MONO};font-size:36px;font-weight:700;line-height:104px;text-align:center;color:{RED}">juice</p>')
o.append(tag(SLX + SLW + 24, 545, "menu 안에 없어요", RED, 2))
o += rule_rows(1100, 680, 724, [[("in", "code", T1), ("들어 있으면 True", "sans", INK)], [("not in", "code", T1), ("없으면 True", "sans", INK)]], [190, 480], rh=96, fs=36, orders=[5, 5])
F[0] = 30
W("in-list", o, "in은 왼쪽 값이 오른쪽 리스트 안에 들어 있는지 물어요. 답은 12에서 본 비교처럼 True나 False예요. latte는 menu에 있어서 True, juice는 없어서 False예요. not in은 반대로 없는지 물어요. 그래서 juice not in menu는 True, latte not in menu는 False예요. 13의 for 장에서 95 in scores를 잠깐 봤는데, 여기서 in과 not in을 한곳에 모아 정리해요." + REAL)

o = [sec("in-tuple-str")] + head(EB1, "튜플과 문자열에도 in을 써요", T1)
TA, TB, Wd = 236, 556, 1000
ca = {"id": "c-it", "lines": ['order = ("coffee", 4500, 2)', "print(4500 in order)", 'print("4500" in order)'], "n": 3, "out": ["True", "False"]}
cb = {"id": "c-is", "lines": ['word = "python"', 'print("th" in word)', 'print("pt" in word)', 'print("P" in word)'], "n": 4, "out": ["True", "False", "False"]}
o += cell(ca, 96, TA, Wd)
o += cell(cb, 96, TB, Wd, attrs=bi("rise", 2))
TX0 = tx(96, ["False"])
o.append(underline(1, cx(96, 'print('), cx(96, 'print("4500"'), ly(TA, 2) + 22, T1))
o.append(tag(TX0, oy(TA, 3, 1), '글자 "4500"은 숫자 4500과 다른 값이에요', T1, 1))
o.append(tag(TX0, oy(TB, 4, 0), "th는 붙어 있어요", GR, 2))
o.append(tag(TX0, oy(TB, 4, 1), "p와 t는 떨어져 있어요", RED, 3))
o.append(underline(4, cx(96, 'print('), cx(96, 'print("P"'), ly(TB, 3) + 22, T1))
o.append(tag(TX0, oy(TB, 4, 2), "대문자와 소문자를 구분해요", RED, 4))
# pictures: the tuple and the word as boxes
o.append(p(f"position:absolute;left:1190px;top:{TA + 10}px;font-family:{MONO};font-size:28px;font-weight:700;color:{T1}", "order"))
o.append(slots(['"coffee"', "4500", "2"], 1190, TA + 50, 196, 96, 32, "it-s"))
o.append(lit(1190 + 208, TA + 90, 196, 96, 1, T1, HL["t1"]))
o.append(p(f"position:absolute;left:1190px;top:{TB + 10}px;font-family:{MONO};font-size:28px;font-weight:700;color:{T1}", "word", bi("rise", 2)))
o.append(slots(list("python"), 1190, TB + 50, 96, 96, 40, "is-s", gap=8, attrs=bi("rise", 2)))
o.append(lit(1190 + 2 * 104 - 4, TB + 86, 2 * 96 + 8 + 8, 104, 2, GR, HL["run"]))
o.append(underline(3, 1190 + 14, 1190 + 82, TB + 210, RED))
o.append(underline(3, 1190 + 2 * 104 + 14, 1190 + 2 * 104 + 82, TB + 210, RED))
o.append(tag(1190, TB + 262, "p와 t 사이에 y가 있어요", RED, 3, size=28, lead=False))
W("in-tuple-str", o, "in은 튜플에도 그대로 써요. 4500은 order 안에 있어서 True예요. 따옴표로 감싼 \"4500\"은 글자라서 숫자 4500과 다른 값이고, 그래서 False예요. 12에서 본 타입 차이가 여기서도 나와요. 문자열에 in을 쓰면 글자 조각이 붙어 있는지 찾아요. th는 python 안에 붙어 있어서 True예요. p와 t는 사이에 y가 있어서 pt는 False예요. 대문자 P도 python에 없어서 False예요. 문자열에 숫자 3을 물으면 TypeError가 나는데, 정리 장에서 봐요." + REAL)

o = [sec("in-logic")] + head(EB1, "in의 답은 and, or, not과 섞어 써요", T1)
T, Wd = 236, 1100
c = {"id": "c-ig", "lines": ['has_both = "latte" in menu and "cake" in menu', "print(has_both)", 'print("juice" in menu or "tea" in menu)', 'print(not "juice" in menu)'], "n": 5, "out": ["True", "False", "True"]}
o += cell(c, 96, T, Wd)
TXo = tx(96, ["False"])
o.append(hl(96, T, Wd, 0, 2, "t1", 1))
# evaluation chain: in first, and last
CY = 740
o.append(p(f"position:absolute;left:96px;top:{CY - 96}px;font-size:28px;font-weight:700;color:{GRAY}", "has_both 줄은 이렇게 계산돼요", bi("fade", 1)))
o.append(f'<div{bi("rise", 1)} style="position:absolute;left:96px;top:{CY}px;height:70px;display:flex;flex-direction:row;align-items:center;gap:20px">'
         + p(f"font-family:{MONO};font-size:36px;font-weight:700;color:{INK};background:{T1BG};border-radius:10px;padding:4px 14px;white-space:pre", e('"latte" in menu'), ' id="ig-a"')
         + p(f"font-family:{MONO};font-size:36px;font-weight:700;color:{GRAY}", "and")
         + p(f"font-family:{MONO};font-size:36px;font-weight:700;color:{INK};background:{T1BG};border-radius:10px;padding:4px 14px;white-space:pre", e('"cake" in menu'), ' id="ig-b"') + '</div>')
X2 = 96 + 920
o.append(f'<x-shape kind="arrow-right"{bi("fade", 2)} style="position:absolute;left:{X2 - 70}px;top:{CY + 21}px;width:50px;height:28px;background:#C9CED8"></x-shape>')
o.append(f'<div style="position:absolute;left:{X2}px;top:{CY}px;height:70px;display:flex;flex-direction:row;align-items:center;gap:20px">'
         + f'<div data-build-in="fly order 2" data-from="ig-a" id="ig-ta">{tf("True", 36)}</div>'
         + p(f"font-family:{MONO};font-size:36px;font-weight:700;color:{GRAY}", "and", bi("fade", 2))
         + f'<div data-build-in="fly order 2" data-from="ig-b">{tf("True", 36)}</div></div>')
X3 = X2 + 420
o.append(f'<x-shape kind="arrow-right"{bi("fade", 3)} style="position:absolute;left:{X3 - 70}px;top:{CY + 21}px;width:50px;height:28px;background:#C9CED8"></x-shape>')
o.append(f'<div data-build-in="fly order 3" data-from="ig-ta" style="position:absolute;left:{X3}px;top:{CY}px;height:70px;display:flex;align-items:center">{tf("True", 36)}</div>')
o.append(p(f"position:absolute;left:96px;top:{CY + 96}px;font-size:26px;font-weight:700;color:{T1}", "① in 두 개를 먼저 계산해요", bi("fade", 1)))
o.append(p(f"position:absolute;left:{X2}px;top:{CY + 96}px;font-size:26px;font-weight:700;color:{T1}", "② and는 그다음", bi("fade", 2)))
o.append(tag(TXo, oy(T, 4, 0), "둘 다 있어서 True", GR, 3))
o.append(tag(TXo, oy(T, 4, 1), "juice도 tea도 없어서 False", RED, 4))
o.append(tag(TXo, oy(T, 4, 2), '"juice" not in menu와 같아요. not in 쪽이 읽기 쉬워요', T1, 5))
W("in-logic", o, "in의 답은 True나 False라서 12에서 배운 and, or, not과 섞어 쓸 수 있어요. 파이썬은 in 두 개를 먼저 계산해서 True and True를 만들고, 그다음 and를 계산해요. 결과를 has_both처럼 변수에 담아 둘 수도 있어요. or는 하나만 있어도 True인데, juice도 tea도 없어서 False예요. not \"juice\" in menu는 in을 먼저 계산한 뒤 not으로 뒤집어요. 결과는 \"juice\" not in menu와 같고, not in으로 붙여 쓰는 쪽이 읽기 쉬워요. 나중에 배울 if 문은 이 True, False로 할 일을 골라요." + REAL)

o = [sec("in-orders")] + head(EB1, "in은 바깥 한 겹만 들여다봐요", T1)
T, Wd = 236, 1460
c = {"id": "c-io", "lines": ['orders = [("coffee", 4500, 2), ("latte", 5000, 1), ("cake", 6500, 3)]', 'print(("cake", 6500, 3) in orders)', 'print("cake" in orders)', 'print("cake" in orders[2])'], "n": 6, "out": ["True", "False", "True"]}
o += cell(c, 96, T, Wd)
TXo = tx(96, ["False"])
# picture: the outer list holding three tuples
PY, PH = 690, 190
o.append(p(f"position:absolute;left:96px;top:{PY - 50}px;font-family:{MONO};font-size:28px;font-weight:700;color:{T1}", "orders  바깥 리스트"))
o.append(f'<div id="io-outer" style="position:absolute;left:96px;top:{PY}px;width:1728px;height:{PH}px;border:3px solid {T1};border-radius:22px;background:#FFFFFF"></div>')
for k, (m_, pr, q) in enumerate([("coffee", 4500, 2), ("latte", 5000, 1), ("cake", 6500, 3)]):
    x = 126 + k * 566
    o.append(f'<div id="io-t{k}" style="position:absolute;left:{x}px;top:{PY + 30}px;width:536px;height:{PH - 60}px;border:3px solid {LINE};border-radius:16px;background:#FAF8F3;display:flex;flex-direction:row;align-items:center;justify-content:center;gap:4px">'
             + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:{GRAY}", "(")
             + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:{INK};white-space:pre", e(f'"{m_}"'), f' id="io-n{k}"')
             + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:{INK};white-space:pre", e(f", {pr}, {q}"))
             + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:{GRAY}", ")") + '</div>')
o.append(spot(1, target="io-t2", pad=10, dim=0.5))
o.append(tag(TXo, oy(T, 4, 0), "튜플 통째로 물으면 찾아요", GR, 1))
o.append(spot(2, target="io-outer", pad=6, dim=0.5))
o.append(tag(TXo, oy(T, 4, 1), "바깥에는 튜플 세 개뿐이라 글자 cake는 없어요", RED, 2))
o.append(spot(3, target="io-n2", pad=10, dim=0.5))
o.append(tag(TXo, oy(T, 4, 2), "orders[2]로 한 겹 꺼내면 안에 있어요", GR, 3))
o.append(spot_off(4))
o.append(caption("안쪽까지 보려면 번호로 한 겹 꺼낸 뒤 in을 써요.", 4))
W("in-orders", o, "13의 orders는 리스트 안에 튜플을 넣은 모양이에요. in은 바깥 리스트에 든 값 하나하나와 통째로 비교해요. 그래서 튜플 (\"cake\", 6500, 3)은 찾지만, 글자 \"cake\"는 바깥에 없어서 False예요. 튜플 안까지 보려면 orders[2]로 한 겹 꺼낸 뒤 in을 써요. 다음 파트의 2차원 리스트에서도 같은 일이 생겨요." + REAL)

# ---------- part 2: 2D lists ----------
o = [sec("m-why")] + head(EB2, "학생마다 변수를 따로 두면 학생 수만큼 코드가 늘어요", T6)
T, Wd = 236, 1000
c = {"id": "c-mw", "lines": ["kim = [90, 85, 77]", "lee = [70, 95, 88]", "park = [60, 75, 99]", "print(sum(kim) + sum(lee) + sum(park))"], "n": 1, "out": ["739"]}
o += cell(c, 96, T, Wd)
TXc = 96 + Wd + 40
o.append(hl(96, T, Wd, 0, 3, "t6", 1))
o.append(tag(TXc, ly(T, 1), "학생 한 명에 변수 하나", T6, 1))
o.append(hl(96, T, Wd, 3, 1, "err", 2))
o.append(tag(TXc, ly(T, 3), "30명이면 sum을 30번 적어요", RED, 2))
g = Grid(SC0, 96, 600, 210, 88, 40, "mw", head=False, side=False, lbl=28)
o.append(p(f"position:absolute;left:96px;top:548px;font-family:{MONO};font-size:30px;font-weight:700;color:{T6}", "scores", bi("fade", 3)))
for i, name in enumerate(["kim", "lee", "park"]):
    o.append(g.group([(i, j, SC0[i][j], None, None) for j in range(3)], f' data-build-in="fly order 3" data-from="c-mw-l{i}"'))
    o.append(tag(g.right + 30, g.y(i) + g.ch / 2, name, GRAY, 3, size=28))
o.append(p(f"position:absolute;left:{g.right + 260:.0f}px;top:{g.y(0) + 10:.0f}px;width:{1824 - g.right - 260:.0f}px;font-size:34px;font-weight:700;line-height:1.5;color:{INK}",
           "세 줄을 리스트 하나에 담으면<br>for로 한 번에 돌 수 있어요", bi("fade", 4)))
W("m-why", o, "학생 세 명의 점수를 지금까지 배운 방법으로 담으면 학생마다 리스트 변수를 하나씩 만들어요. 세 명 합계를 내려면 sum을 세 번 적어요. 학생이 서른 명이면 변수도 서른 개, sum도 서른 번이에요. 세 리스트를 리스트 하나에 넣으면 표 하나가 되고, 13에서 배운 for로 한 번에 돌 수 있어요. 이 모양을 2차원 리스트라고 불러요. 이 파트도 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("matrix", "2차원 리스트"))

o = [sec("m-make")] + head(EB2, "리스트 안에 리스트를 넣으면 표가 돼요", T6)
T, Wd = 236, 860
c = {"id": "c-mm", "lines": ["scores = [[90, 85, 77],", "          [70, 95, 88],", "          [60, 75, 99]]", "print(scores)", "print(len(scores))", "print(len(scores[0]))"], "n": 2,
     "out": ["[[90, 85, 77], [70, 95, 88], [60, 75, 99]]", "3", "3"]}
o += cell(c, 96, T, Wd)
g = Grid(SC0, 1070, 240, 200, 112, 48, "mm", cols=SUBJ, lbl=28)
o.append(g.html())
o.append(hl(96, T, Wd, 0, 1, "t6", 1))
x_, y_, w_, h_ = g.row_rect(0)
o.append(lit(x_ - 8, y_ - 8, w_ + 16, h_ + 16, 1, T6, None, r=16))
o.append(tag(g.left - 10, g.bottom + 70, "가로 한 줄이 행이에요. 안쪽 리스트 하나가 한 행", T6, 1, lead=False))
x_, y_, w_, h_ = g.col_rect(1)
o.append(lit(x_ - 8, y_ - 8, w_ + 16, h_ + 16, 2, BL, None, r=16))
o.append(tag(g.left - 10, g.bottom + 130, "세로 한 줄이 열이에요. 과목 하나가 한 열", BL, 2, lead=False))
TXo = tx(96, ["3"])
o.append(hl(96, T, Wd, 4, 1, "t6", 3))
o.append(tag(TXo, oy(T, 6, 1), "len(scores): 바깥 리스트에 든 행 수", T6, 3))
o.append(hl(96, T, Wd, 5, 1, "mark", 4))
o.append(tag(TXo, oy(T, 6, 2), "len(scores[0]): 0행 안의 칸 수가 열 수", BL, 4))
o.append(caption("대괄호가 닫히기 전에는 줄을 바꿔 적어도 돼요. 그래서 표처럼 적어요.", 5))
W("m-make", o, "13의 리스트 모양 장에서 리스트 안에 리스트를 넣으면 표 모양이 된다고 했어요. scores는 학생 세 명의 국어, 영어, 수학 점수예요. 안쪽 리스트 하나가 학생 한 명, 표의 가로 한 줄이에요. 가로 줄을 행, 세로 줄을 열이라고 불러요. len(scores)는 바깥 리스트에 든 개수라서 행 수예요. len(scores[0])은 0행 안에 든 개수라서 열 수예요. 대괄호가 닫히기 전에는 줄을 바꿔도 되니까 표처럼 줄을 맞춰 적으면 읽기 쉬워요." + REAL)

o = [sec("m-index")] + head(EB2, "[행][열] 순서로 칸 하나를 꺼내요", T6)
F[0] = 38
T, Wd = 236, 740
c = {"id": "c-mi", "lines": ["print(scores[1])", "print(scores[1][2])", "print(scores[0][0])", "print(scores[-1][-1])"], "n": 3, "out": ["[70, 95, 88]", "88", "90", "99"]}
o += cell(c, 96, T, Wd)
g = Grid(SC0, 990, 240, 240, 150, 58, "mi", lbl=30)
o.append(g.html())
TXo = tx(96, ["[70, 95, 88]"])
steps = [(g.row_rect(1), "1행 통째로", 0), (g.rect(1, 2), "1행의 2열", 1), (g.rect(0, 0), "맨 왼쪽 위", 2), (g.rect(2, 2), "마지막 행의 마지막 열", 3)]
for k, ((x_, y_, w_, h_), t_, line) in enumerate(steps):
    o.append(spot(k + 1, x_, y_, w_, h_, pad=10, dim=0.5))
    o.append(tag(TXo if k == 0 else tx(96, ["88"]), oy(T, 4, k), t_, T6, k + 1))
o.append(spot_off(5))
o.append(caption("앞 번호가 행, 뒤 번호가 열이에요. 둘 다 0부터 세요.", 5))
F[0] = 30
W("m-index", o, "2차원 리스트도 13에서 orders[1][0]으로 꺼낸 것처럼 번호 두 개로 꺼내요. 번호 하나만 쓰면 행 하나가 리스트로 통째로 나와요. scores[1]은 1행 [70, 95, 88]이에요. 거기에 번호를 하나 더 붙이면 그 행 안의 칸이에요. scores[1][2]는 1행의 2열이라 88이에요. 번호는 행도 열도 0부터 세요. -1은 맨 뒤라서 scores[-1][-1]은 마지막 행의 마지막 열 99예요." + REAL)

o = [sec("m-change")] + head(EB2, "번호 두 개면 칸 하나, 번호 하나면 행 하나를 바꿔요", T6)
F[0] = 34
T, Wd = 236, 900
c = {"id": "c-mc", "lines": ["scores[0][1] = 100", "print(scores[0])", "scores[2] = [65, 80, 90]", "print(scores)"], "n": 4, "out": ["[90, 100, 77]", "[[90, 100, 77], [70, 95, 88], [65, 80, 90]]"]}
o += cell(c, 96, T, Wd)
g = Grid(SC0, 1090, 240, 210, 148, 54, "mc", lbl=30)
o.append(g.html())
o.append(hl(96, T, Wd, 0, 1, "t6", 1))
o.append(tag(tx(96, ["scores[0][1] = 100"]), ly(T, 0), "칸 하나", T6, 1))
o.append(fly_cell(g, 0, 1, 100, 1, "c-mc-l0"))
o.append(hl(96, T, Wd, 2, 1, "t6", 2))
o.append(tag(tx(96, ["scores[2] = [65, 80, 90]"]), ly(T, 2), "행 하나", T6, 2))
o.append(g.group([(2, j, v, T6BG, T6) for j, v in enumerate([65, 80, 90])], ' data-build-in="fly order 2" data-from="c-mc-l2"'))
o.append(caption("다음 장부터는 이렇게 바뀐 scores를 써요.", 3))
F[0] = 30
W("m-change", o, "리스트는 바꿀 수 있어서 2차원 리스트도 칸을 바꿀 수 있어요. 13에서 xs[1] = 값으로 바꾼 것과 같은 모양이에요. 번호 두 개를 쓰면 칸 하나, 번호 하나를 쓰면 행 하나를 통째로 바꿔요. 0행 1열 85가 100으로, 2행 전체가 [65, 80, 90]으로 바뀌었어요. 다음 장부터는 이렇게 바뀐 scores를 계속 써요." + REAL)

o = [sec("m-for")] + head(EB2, "for로 한 행씩 꺼내면 row에는 리스트가 들어가요", T6)
T, Wd = 236, 1300
c = {"id": "c-mf", "lines": ["for row in scores:", '    print(row, "합계:", sum(row), "최고:", max(row))'], "n": 5,
     "out": ["[90, 100, 77] 합계: 267 최고: 100", "[70, 95, 88] 합계: 253 최고: 95", "[65, 80, 90] 합계: 235 최고: 90"], "oo": {0: 1, 1: 2, 2: 3}}
o += cell(c, 96, T, Wd)
g = Grid(SC1, 96, 610, 140, 84, 38, "mf", head=False, lbl=28)
o.append(g.html())
for i in range(3):
    y = g.y(i)
    o.append(f'<x-shape kind="arrow-right"{bi("fade", i + 1)} style="position:absolute;left:{g.right + 30:.0f}px;top:{y + 28:.0f}px;width:50px;height:28px;background:#C9CED8"></x-shape>')
    o.append(p(f"position:absolute;left:{g.right + 100:.0f}px;top:{y + 18:.0f}px;font-family:{MONO};font-size:32px;font-weight:700;color:{T6}", "row =", bi("fade", i + 1)))
    o.append(f'<div data-build-in="fly order {i + 1}" data-from="mf-r{i}" style="position:absolute;left:{g.right + 220:.0f}px;top:{y:.0f}px;display:flex;flex-direction:row;gap:8px">'
             + "".join(p(f"width:120px;height:{g.ch}px;border-radius:12px;border:3px solid {T6};background:{T6BG};font-family:{MONO};font-size:34px;font-weight:700;line-height:{g.ch - 6}px;text-align:center;color:{INK}", str(v)) for v in SC1[i]) + '</div>')
    o.append(f'<div id="mf-r{i}" style="position:absolute;left:{g.x(0):.0f}px;top:{y:.0f}px;width:{g.right - g.x(0):.0f}px;height:{g.ch}px"></div>')
    o.append(p(f"position:absolute;left:{g.right + 650:.0f}px;top:{y + 18:.0f}px;font-family:{MONO};font-size:32px;font-weight:700;color:{INK};white-space:pre",
               f"sum {sum(SC1[i])}  max {max(SC1[i])}", bi("fade", i + 1)))
o.append(caption("row가 리스트라서 13에서 배운 sum, max를 바로 써요.", 4))
W("m-for", o, "13에서 for로 리스트 값을 하나씩 꺼냈어요. 2차원 리스트에 for를 쓰면 꺼내는 값 하나가 행 하나예요. 그래서 row에는 [90, 100, 77] 같은 리스트가 통째로 들어가요. row가 리스트니까 13에서 배운 sum, max를 바로 쓸 수 있어요. 학생마다 합계와 최고 점수가 한 줄씩 나와요." + REAL)

o = [sec("m-col")] + head(EB2, "열 하나는 행마다 같은 번호의 칸을 모아요", T6)
T, Wd = 236, 820
c = {"id": "c-mo", "lines": ["eng = []", "for row in scores:", "    eng.append(row[1])", "print(eng)", 'print("영어 합계:", sum(eng))'], "n": 6, "out": ["[100, 95, 80]", "영어 합계: 275"]}
o += cell(c, 96, T, Wd)
g = Grid(SC1, 1060, 240, 200, 130, 46, "mo", cols=SUBJ, lbl=28)
o.append(g.html())
o.append(hl(96, T, Wd, 1, 2, "t6", 1))
x_, y_, w_, h_ = g.col_rect(1)
o.append(lit(x_ - 8, y_ - 8, w_ + 16, h_ + 16, 1, T6, None, r=16))
EX, EY = 200, 720
o.append(p(f"position:absolute;left:96px;top:{EY + 30}px;font-family:{MONO};font-size:32px;font-weight:700;color:{T6}", "eng", bi("fade", 1)))
for i in range(3):
    o.append(p(f"position:absolute;left:{EX + i * 212}px;top:{EY}px;width:200px;height:104px;border-radius:12px;border:3px dashed {LINE};background:transparent", "", bi("fade", 1)))
    o.append(f'<p data-build-in="fly order {i + 2}" data-from="mo-{i}-1" style="position:absolute;left:{EX + i * 212}px;top:{EY}px;width:200px;height:104px;border-radius:12px;border:3px solid {T6};background:{T6BG};font-family:{MONO};font-size:44px;font-weight:700;line-height:98px;text-align:center;color:{INK}">{SC1[i][1]}</p>')
o.append(tag(EX, EY - 40, "for가 돌 때마다 row[1]이 하나씩 들어가요", T6, 2, size=28, lead=False))
o.append(tag(tx(96, ["영어 합계: 275"]), oy(T, 5, 1), "모은 eng는 보통 리스트라 sum을 써요", T6, 5))
o.append(caption("행은 scores[1]로 바로 꺼내지만, 열은 for로 모아요.", 5))
W("m-col", o, "행은 scores[1]처럼 번호 하나로 바로 꺼내요. 열은 바로 꺼내는 방법이 없어서 행마다 같은 번호의 칸을 모아요. 빈 리스트 eng를 만들고, for로 행을 하나씩 꺼내 row[1]을 append해요. 영어는 1열이라 [1]이에요. for가 세 번 돌면서 100, 95, 80이 차례로 들어가요. 모은 eng는 보통 리스트라서 sum을 바로 써요." + REAL)

o = [sec("m-total")] + head(EB2, "표 전체 합계는 행 합계를 차례로 쌓아요", T6)
T, Wd = 236, 820
c = {"id": "c-mt", "lines": ["total = 0", "count = 0", "for row in scores:", "    total += sum(row)", "    count += len(row)", 'print("전체 합계:", total)', 'print("칸 수:", count)', 'print(f"평균: {total / count:.1f}")'], "n": 7,
     "out": ["전체 합계: 755", "칸 수: 9", "평균: 83.9"]}
o += cell(c, 96, T, Wd)
o.append(hl(96, T, Wd, 0, 2, "skip", 1))
o.append(hl(96, T, Wd, 3, 2, "t6", 2))
widths = [300, 170, 150, 120]
o += rule_rows(1000, 240, 824, [[("[90, 100, 77]", "code", INK), ("267", "code", INK), ("267", "code", T6), ("3", "code", T6)],
                               [("[70, 95, 88]", "code", INK), ("253", "code", INK), ("520", "code", T6), ("6", "code", T6)],
                               [("[65, 80, 90]", "code", INK), ("235", "code", INK), ("755", "code", T6), ("9", "code", T6)]],
               widths, rh=96, head_=["row", "sum(row)", "total", "count"], fs=30, orders=[2, 3, 4])
o.append(p(f"position:absolute;left:1000px;top:198px;font-size:24px;font-weight:700;color:{GRAY}", "for가 한 번 돌 때마다", bi("fade", 1)))
o.append(hl(96, T, Wd, 7, 1, "t6", 5))
o.append(f'<div{bi("rise", 5)} style="position:absolute;left:1000px;top:690px;width:824px;display:flex;flex-direction:column;gap:14px">'
         + mono("755 / 9 = 83.888...", 40, INK) + p(f"font-size:30px;font-weight:700;color:{T6}", ":.1f 로 소수점 한 자리만 보여 줘요 (13)") + '</div>')
o.append(caption("total과 count는 for 앞에서 0으로 한 번만 시작해요.", 6))
W("m-total", o, "13의 for 합계 장처럼 for 앞에서 total을 0으로 시작해요. 이번에는 행마다 sum(row)를 더해서 표 전체의 합계를 쌓아요. count에는 len(row)를 더해서 칸 수를 세요. 세 행을 돌고 나면 total은 755, count는 9예요. 평균은 755 나누기 9라 83.888...인데, 13에서 배운 .1f로 소수점 한 자리만 보여 줘요. total = 0을 for 안에 넣으면 행마다 0으로 돌아가서 합계가 쌓이지 않아요." + REAL)

o = [sec("m-slice")] + head(EB2, "자르기도 앞 번호는 행, 뒤 번호는 열에 써요", T6)
T, Wd = 236, 900
c = {"id": "c-ms", "lines": ["print(scores[:2])", "print(scores[1][:2])", "print(scores[0][::-1])"], "n": 8, "out": ["[[90, 100, 77], [70, 95, 88]]", "[70, 95]", "[77, 100, 90]"]}
o += cell(c, 96, T, Wd)
o.append(p(f"position:absolute;left:1080px;top:{T + 14}px;width:744px;font-size:30px;line-height:1.5;color:{SUB}", "[시작:끝:간격]은 13에서 배운 그대로예요.<br>어느 리스트를 자르는지만 봐요."))
ms = [("scores[:2]", "바깥을 잘라서 행 두 개", [(i, j) for i in range(2) for j in range(3)]), ("scores[1][:2]", "1행을 꺼낸 뒤 칸 두 개", [(1, 0), (1, 1)]), ("scores[0][::-1]", "0행을 거꾸로", [(0, 0), (0, 1), (0, 2)])]
for k, (code, d, hi) in enumerate(ms):
    x0 = 96 + k * 600
    o.append(f'<div{bi("rise", k + 1)} style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none">'
             + mono(code, 32, T6, f"position:absolute;left:{x0}px;top:586px")
             + p(f"position:absolute;left:{x0}px;top:636px;font-size:26px;font-weight:700;color:{SUB}", d)
             + Grid(SC1, x0, 690, 140, 62, 30, f"ms{k}", head=False, side=False, hi=hi, hi_bg=T6BG).html() + '</div>')
o.append(caption("열 하나를 통째로 자르는 문법은 없어요. 앞 장처럼 for로 모아요.", 4))
W("m-slice", o, "13에서 배운 [시작:끝:간격] 자르기를 2차원 리스트에도 써요. scores[:2]는 바깥 리스트를 자르니까 행 두 개가 리스트로 나와요. scores[1][:2]는 1행을 먼저 꺼내고, 그 행의 0열과 1열을 잘라요. [::-1]은 거꾸로라서 0행이 [77, 100, 90]이 돼요. 열 하나를 통째로 자르는 문법은 없어서 앞 장처럼 for와 append로 모아요." + REAL)

o = [sec("m-in")] + head(EB2, "2차원 리스트에서 in은 바깥의 행만 봐요", T6)
T, Wd = 236, 860
c = {"id": "c-mn", "lines": ["print(95 in scores)", "print(95 in scores[1])", "print([70, 95, 88] in scores)", "for row in scores:", "    print(row, 100 in row)"], "n": 9,
     "out": ["False", "True", "True", "[90, 100, 77] True", "[70, 95, 88] False", "[65, 80, 90] False"]}
o += cell(c, 96, T, Wd)
TXo = tx(96, ["False"])
o.append(box(1, cx(96) - 12, oy(T, 5, 0) - 26, tw("False") + 24, 52))
o.append(tag(TXo, oy(T, 5, 0), "바깥에는 행 리스트 세 개만 있어요", RED, 1))
o.append(tag(TXo, oy(T, 5, 1), "1행을 꺼내서 물으면 찾아요", GR, 2))
o.append(tag(TXo, oy(T, 5, 2), "행을 통째로 적으면 찾아요", GR, 3))
o.append(hl(96, T, Wd, 3, 2, "t6", 4))
o.append(tag(tx(96, ["[90, 100, 77] True"]), oy(T, 5, 3), "for로 행마다 물어요", T6, 4))
# picture: the outer list holding three rows, same as part 1's orders
PX, PW = 1280, 544
o.append(p(f"position:absolute;left:{PX}px;top:240px;font-family:{MONO};font-size:28px;font-weight:700;color:{T6}", "scores  바깥 리스트"))
o.append(f'<div style="position:absolute;left:{PX}px;top:290px;width:{PW}px;height:420px;border:3px solid {T6};border-radius:22px;background:#FFFFFF"></div>')
for k, r in enumerate(SC1):
    o.append(p(f"position:absolute;left:{PX + 30}px;top:{320 + k * 128}px;width:{PW - 60}px;height:104px;border:3px solid {LINE};border-radius:16px;background:#FAF8F3;font-family:{MONO};font-size:34px;font-weight:700;line-height:98px;text-align:center;color:{INK};white-space:pre",
               e(str(r)), f' id="mn-r{k}"'))
o.append(lit(PX + 30, 320 + 128, PW - 60, 104, 2, GR, HL["run"], r=16))
o.append(tag(PX, 770, "1파트의 orders와 같은 모양이에요", GRAY, None, size=28, lead=False))
W("m-in", o, "1파트에서 in은 바깥 한 겹만 들여다본다고 했어요. 2차원 리스트도 같아요. scores에 든 값은 행 리스트 세 개라서 숫자 95를 물으면 False예요. scores[1]로 1행을 꺼낸 뒤 물으면 True예요. 행을 통째로 적어서 물으면 찾아요. 어느 행에 100이 있는지 알고 싶으면 for로 행마다 100 in row를 물어요. 0행만 True예요." + REAL)

o = [sec("m-add")] + head(EB2, "행은 append 한 번, 열은 행마다 append해요", T6)
T, Wd = 236, 760
c = {"id": "c-ma", "lines": ["scores.append([80, 70, 60])", "print(len(scores))", "for row in scores:", "    row.append(0)", "for row in scores:", "    print(row)"], "n": 10,
     "out": ["4", "[90, 100, 77, 0]", "[70, 95, 88, 0]", "[65, 80, 90, 0]", "[80, 70, 60, 0]"]}
o += cell(c, 96, T, Wd)
SC2 = [r + [0] for r in SC1] + [[80, 70, 60, 0]]
g = Grid(SC2, 980, 240, 176, 100, 42, "ma", lbl=28)
o.append(g.html(only_rows={0, 1, 2}, only_cols={0, 1, 2}))
o.append(hl(96, T, Wd, 0, 1, "t6", 1))
o.append(p(f"position:absolute;left:{g.left:.0f}px;top:{g.y(3):.0f}px;width:{g.rw - 14:.0f}px;height:{g.ch}px;text-align:right;font-family:{MONO};font-size:28px;font-weight:700;line-height:{g.ch}px;color:{T6}", "3", bi("fade", 1)))
o.append(g.group([(3, j, SC2[3][j], T6BG, T6) for j in range(3)], bi("pop", 1)))
o.append(tag(g.left, g.bottom + 64, "새 행은 바깥 리스트에 하나", T6, 1, lead=False))
o.append(hl(96, T, Wd, 2, 2, "mark", 2))
o.append(p(f"position:absolute;left:{g.x(3):.0f}px;top:{g.top:.0f}px;width:{g.cw}px;text-align:center;font-family:{MONO};font-size:28px;font-weight:700;color:{T6};line-height:1.25", "3", bi("fade", 2)))
o.append(g.group([(i, 3, 0, "#E3EBFA", BL) for i in range(4)], bi("pop", 2)))
o.append(tag(g.left, g.bottom + 120, "새 열은 행 네 개에 하나씩", BL, 2, lead=False))
o.append(caption("row는 scores 안의 행 그 자체라서, row에 붙이면 scores도 바뀌어요.", 3))
W("m-add", o, "새 학생을 더하는 건 바깥 리스트에 행 하나를 append하는 거예요. 행 수가 4가 됐어요. 새 과목처럼 열을 더하려면 모든 행 끝에 하나씩 붙여야 해요. 그래서 for로 행을 꺼내 row.append(0)을 해요. row는 scores 안의 행 그 자체라서 row에 붙이면 scores도 바뀌어요. 이제 scores는 4행 4열이에요." + REAL)

o = [sec("m-compare")] + head(EB2, "번호가 하나 늘었을 뿐, 13의 리스트와 쓰는 법이 같아요", T6)


def two(a, b=None):
    s = f'<span style="color:{INK}">{e(a)}</span>'
    return s + (f'<span style="color:{T6}">{e(b)}</span>' if b else "")


cmp_rows = [["만들기", (two("[90, 85, 77]"), "code"), (two("[[90, 85, 77], ...]"), "code")],
            ["칸 꺼내기", (two("xs[1]"), "code"), (two("scores[1]", "[2]"), "code")],
            ["개수", (two("len(xs)"), "code"), (two("len(scores)") + '<span style="color:' + GRAY + ';font-family:' + SANS + ';font-size:24px">  행 수</span>', "code")],
            ["for", (two("for x in xs:"), "code"), (two("for row in scores:") + '<span style="color:' + GRAY + ';font-family:' + SANS + ';font-size:24px">  row는 행</span>', "code")],
            ["더하기", (two("xs.append(5)"), "code"), (two("scores.append([80, 70, 60])"), "code")],
            ["in", (two("85 in xs"), "code"), (two("85 in scores", "[0]"), "code")],
            ["자르기", (two("xs[:2]"), "code"), (two("scores[:2]  scores[1]", "[:2]"), "code")]]
o += rule_rows(96, 236, 1728, cmp_rows, [220, 560, 860], rh=88, head_=["", "리스트 (13)", "2차원 리스트 (14)"], fs=30, orders=[1, 1, 2, 2, 3, 3, 3])
o.append(caption("안쪽까지 가려면 번호를 하나 더 붙여요.", 4))
W("m-compare", o, "13에서 배운 리스트와 이번 2차원 리스트를 나란히 놓았어요. 만들기, 꺼내기, len, for, append, in, 자르기를 모두 같은 문법으로 써요. 다른 점은 안쪽까지 가려면 번호를 하나 더 붙인다는 것뿐이에요. 색이 다른 부분이 그 번호예요. len(scores)와 for row in scores는 바깥 리스트, 행 단위로 움직인다는 것도 같이 기억해요.")

o = [sec("m-trap")] + head(EB2, "[[0] * 3] * 3은 같은 행 하나를 세 번 담아요", T6)
TA, TB, Wd = 236, 540, 900
ca = {"id": "c-mp1", "lines": ["board = [[0] * 3] * 3", "board[0][0] = 9", "print(board)"], "n": 11, "out": ["[[9, 0, 0], [9, 0, 0], [9, 0, 0]]"]}
cb = {"id": "c-mp2", "lines": ["board = [[0, 0, 0],", "         [0, 0, 0],", "         [0, 0, 0]]", "board[0][0] = 9", "print(board)"], "n": 12, "out": ["[[9, 0, 0], [0, 0, 0], [0, 0, 0]]"]}
o += cell(ca, 96, TA, Wd)
o.append(box(1, cx(96) - 12, oy(TA, 3, 0) - 27, tw("[[9, 0, 0], [9, 0, 0], [9, 0, 0]]") + 24, 54))
o += cell(cb, 96, TB, Wd, attrs=bi("rise", 2))


def share_pic(top, boxes, color, attrs):
    """board[0..2] on the left, arrows to one shared box or three boxes."""
    lx, bx_ = 1120, 1460
    o_ = [f'<div{attrs} style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none">']
    lines = []
    for i in range(3):
        y = top + 30 + i * 80
        o_.append(p(f"position:absolute;left:{lx}px;top:{y - 22}px;font-family:{MONO};font-size:30px;font-weight:700;color:{T6}", f"board[{i}]"))
        by = top + 30 + (0 if len(boxes) == 1 else i * 80)
        lines.append((lx + 190, y, bx_ - 16, by if len(boxes) > 1 else top + 110))
    o_.append(svg_lines(lines, "#B9BFCB", 4))
    for k, (t_, on) in enumerate(boxes):
        h = 220 if len(boxes) == 1 else 64
        y = top + (0 if len(boxes) == 1 else k * 80) - (0 if len(boxes) == 1 else 2)
        o_.append(p(f"position:absolute;left:{bx_}px;top:{y}px;width:330px;height:{h}px;border-radius:12px;border:3px solid {T6 if on else LINE};background:{T6BG if on else CARD};font-family:{MONO};font-size:32px;font-weight:700;line-height:{h - 6}px;text-align:center;color:{INK}", e(t_)))
    o_.append('</div>')
    return "".join(o_)


o.append(p(f"position:absolute;left:1120px;top:{TA - 6}px;font-size:28px;font-weight:700;color:{RED}", "행 리스트 하나를 셋이 같이 봐요", bi("fade", 1)))
o.append(share_pic(TA + 60, [("[9, 0, 0]", True)], RED, bi("rise", 1)))
o.append(p(f"position:absolute;left:1120px;top:{TB + 4}px;font-size:28px;font-weight:700;color:{GR}", "행이 세 개 따로 있어요", bi("fade", 2)))
o.append(share_pic(TB + 70, [("[9, 0, 0]", True), ("[0, 0, 0]", False), ("[0, 0, 0]", False)], GR, bi("rise", 2)))
o.append(caption("빈 표는 행을 하나씩 직접 적어서 만들어요.", 3))
W("m-trap", o, "13에서 리스트에 * 3을 하면 값이 세 번 되풀이된다고 했어요. 그래서 [[0] * 3] * 3으로 0이 가득 찬 3행 3열 표를 만들고 싶어져요. 그런데 이렇게 만들면 행 리스트 하나를 세 번 담은 거라서, 세 행이 사실 같은 리스트예요. 0행 0열만 9로 바꿨는데 모든 행이 바뀌어요. 오류는 안 나지만 결과가 틀려요. 빈 표는 행을 하나씩 직접 적어서 만들면 행마다 따로 있어서 괜찮아요." + REAL)

o = [sec("m-err")] + head(EB2, "번호가 넘치면 IndexError, 개수가 다르면 ValueError예요", T6)
errs = [("scores[5][0]", "IndexError: list index out of range", "행은 0~3번, 네 개뿐이에요", 13, "out of range"),
        ("scores[0][9]", "IndexError: list index out of range", "0행 안의 칸도 0~3번이에요", 14, "out of range"),
        ("kor, eng, math = scores[0]", "ValueError: too many values to unpack (expected 3)", "한 행에 값이 네 개예요", 15, "expected 3")]
Wd = 1160
for k, (code, err, why, n_, key) in enumerate(errs):
    T = 236 + k * 200
    o += cell({"id": f"c-me{k}", "lines": [code], "n": n_, "out": [err]}, 96, T, Wd, attrs=bi("rise", k + 1))
    x1 = cx(96, err[:err.index(key)])
    o.append(underline(k + 1, x1, x1 + tw(key), oy(T, 1, 0) + 22, RED))
    o.append(tag(96 + Wd + 40, oy(T, 1, 0), why, RED, k + 1))
o.append(f'<div{bi("rise", 4)} style="position:absolute;left:96px;top:{236 + 3 * 200 + 10}px;display:flex;flex-direction:row;align-items:center;gap:28px">'
         + p(f"font-size:32px;font-weight:700;color:{GR}", "확인하기") + mono("len(scores)", 32, INK) + p(f"font-size:30px;color:{SUB}", "행 수 4") + mono("len(scores[0])", 32, INK) + p(f"font-size:30px;color:{SUB}", "열 수 4") + '</div>')
o.append(caption("두 IndexError는 메시지가 같아요. 앞 번호와 뒤 번호 중 어느 쪽이 넘쳤는지 len으로 봐요.", 5))
W("m-err", o, "2차원 리스트에서 자주 나는 오류예요. 행과 열을 하나씩 더해서 scores는 이제 4행 4열이에요. scores[5][0]은 없는 5행을 꺼내서 IndexError예요. scores[0][9]는 0행은 있지만 그 안에 9열이 없어서 같은 IndexError예요. 메시지가 같으니까 앞 번호와 뒤 번호 중 어느 쪽이 넘쳤는지 len으로 확인해요. 한 행에 값이 네 개인데 변수를 세 개만 적어서 꺼내 담으면 ValueError가 나요. 변수 개수를 값 개수에 맞춰요." + REAL)

# ---------- part 3: real examples ----------
o = [sec("x-report")] + head(EB3, "이름을 넣은 성적표를 칸 맞춰 찍어요", T3)
T, Wd = 236, 1180
c = {"id": "c-xr", "lines": ['students = [["kim", 90, 85, 77],', '            ["lee", 70, 95, 88],', '            ["park", 60, 75, 99]]', "print(f\"{'name':<6}{'kor':>5}{'eng':>5}{'math':>5}\")", 'print("-" * 21)',
                             "for name, kor, eng, math in students:", '    print(f"{name:<6}{kor:>5}{eng:>5}{math:>5}")'], "n": 1,
     "out": ["name    kor  eng math", "---------------------", "kim      90   85   77", "lee      70   95   88", "park     60   75   99"]}
o += cell(c, 96, T, Wd)
TXc = 96 + Wd + 40
o.append(hl(96, T, Wd, 0, 3, "t3", 1))
o.append(tag(TXc, ly(T, 1), "행 맨 앞에 이름을 넣었어요", T3, 1))
o.append(hl(96, T, Wd, 5, 1, "t3", 2))
o.append(tag(TXc, ly(T, 5), "한 행의 값 네 개를 변수 네 개에", T3, 2))
o.append(underline(3, cx(96, '    print(f"{name:<6}'), cx(96, '    print(f"{name:<6}{kor:>5}'), ly(T, 6) + 22, T3))
o.append(tag(TXc, ly(T, 6), ":>5 는 오른쪽 맞춤 다섯 칸 (13)", T3, 3))
o.append(tag(tx(96, ["park     60   75   99"]), oy(T, 7, 3), "학생이 늘어도 for 두 줄은 그대로예요", T3, 4))
o.append(caption("for 뒤 변수 개수가 행의 값 개수와 같아야 해요. 다르면 ValueError예요.", 5))
W("x-report", o, "첫 번째 예제는 성적표예요. 행마다 맨 앞에 이름을 넣었어요. 한 리스트 안에 글자와 숫자를 섞어도 된다는 건 13에서 봤어요. for 뒤에 변수를 네 개 적으면 행 하나의 값 네 개가 차례로 나뉘어 담겨요. 13의 영수증에서 쓴 for menu, price, qty in orders:와 같은 모양이에요. 머리글과 칸 맞추기는 13의 f-string이에요. 영어 머리글이라 한글 폭 문제가 없어요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("real", "실제로 써 보기"))

o = [sec("x-seats")] + head(EB3, "좌석표도 행과 열이 있는 2차원 리스트예요", T3)
T, Wd = 236, 820
c = {"id": "c-xs", "lines": ['seats = [["O", "O", "X", "O"],', '         ["X", "O", "O", "O"],', '         ["O", "X", "X", "O"]]', 'seats[0][1] = "X"', "for row in seats:", '    print(" ".join(row))', 'print(seats[2].count("X"))', "print(len(seats) * len(seats[0]))"], "n": 2,
     "out": ["O X X O", "X O O O", "O X X O", "2", "12"]}
o += cell(c, 96, T, Wd)
SE0 = [["O", "O", "X", "O"], ["X", "O", "O", "O"], ["O", "X", "X", "O"]]
taken = {(i, j) for i, r in enumerate(SE0) for j, v in enumerate(r) if v == "X"}
g = Grid(SE0, 1010, 330, 180, 120, 46, "xs", lbl=28, hi=taken, hi_color=RED, hi_bg="#F8E6E6")
o.append(p(f"position:absolute;left:{g.x(0):.0f}px;top:250px;width:{g.right - g.x(0):.0f}px;height:48px;background:#E9E7E0;border-radius:10px;font-size:24px;font-weight:700;line-height:48px;text-align:center;color:{SUB}", "앞 (화면)"))
o.append(g.html())
x_, y_, w_, h_ = g.rect(0, 1)
o.append(hl(96, T, Wd, 3, 1, "t3", 1))
o.append(cursor(1, x_ + w_ * 0.84, y_ + h_ * 0.78))
o.append(g.value_cell(0, 1, "X", bi("pop", 1), color=INK, bg="#F8E6E6", border=RED))
o.append(cursor_off(2))
o.append(tag(tx(96, ["O X X O"]), oy(T, 8, 1), "join으로 행마다 한 줄 (13)", T3, 2))
x_, y_, w_, h_ = g.row_rect(2)
o.append(lit(x_ - 8, y_ - 8, w_ + 16, h_ + 16, 3, T3, None, r=16))
o.append(tag(tx(96, ["O X X O"]), oy(T, 8, 3), "2행의 찬 자리 2개", T3, 3))
o.append(tag(tx(96, ["O X X O"]), oy(T, 8, 4), "3행 × 4열 = 전체 12석", T3, 4))
W("x-seats", o, "두 번째 예제는 극장 좌석표예요. O는 빈자리, X는 찬 자리로 적었어요. seats[0][1] = \"X\"는 0행 1열 자리를 예약한 거예요. 13에서 배운 join으로 행마다 한 줄씩 찍으면 좌석표 모양이 나와요. count는 한 행 안의 X 개수를 세요. 행 수와 열 수를 곱하면 전체 좌석 수예요. 성적표, 좌석표, 달력, 엑셀 시트처럼 행과 열이 있는 데이터는 모두 이 모양으로 담아요." + REAL)

o = [sec("x-cafe")] + head(EB3, "카페 판매표에서 하루 합계와 메뉴 합계를 구해요", T3)
F[0] = 28
T, Wd = 220, 960
c = {"id": "c-xc", "lines": ['menu = ["coffee", "latte", "cake"]', "sales = [[12, 8, 5],", "         [10, 9, 7],", "         [15, 11, 4]]", "for row in sales:", '    print(row, "하루 합계:", sum(row))',
                             'col = menu.index("latte")', "latte = []", "for row in sales:", "    latte.append(row[col])", 'print("latte:", latte, "합계:", sum(latte))'], "n": 3,
     "out": ["[12, 8, 5] 하루 합계: 25", "[10, 9, 7] 하루 합계: 26", "[15, 11, 4] 하루 합계: 30", "latte: [8, 9, 11] 합계: 28"], "oo": {0: 1, 1: 1, 2: 1, 3: 3}}
o += cell(c, 96, T, Wd)
SA = [[12, 8, 5], [10, 9, 7], [15, 11, 4]]
g = Grid(SA, 1180, 250, 160, 100, 42, "xc", lbl=26, cols=["coffee", "latte", "cake"], rows_lbl=["월", "화", "수"], color=T3)
o.append(g.html())
o.append(p(f"position:absolute;left:{g.right + 30:.0f}px;top:{g.top + 30:.0f}px;font-size:22px;font-weight:700;color:{GRAY}", "합계", bi("fade", 1)))
o.append(hl(96, T, Wd, 4, 2, "t3", 1))
for i in range(3):
    o.append(p(f"position:absolute;left:{g.right + 24:.0f}px;top:{g.y(i):.0f}px;height:{g.ch}px;font-family:{MONO};font-size:40px;font-weight:700;line-height:{g.ch}px;color:{T3}", str(sum(SA[i])), bi("fade", 1)))
o.append(tag(tx(96, ['col = menu.index("latte")']), ly(T, 6), "latte는 1열", T3, 2))
x_, y_, w_, h_ = g.col_rect(1)
o.append(lit(x_ - 8, y_ - 8, w_ + 16, h_ + 16, 3, T3, None, r=16))
o.append(hl(96, T, Wd, 7, 3, "t3", 3))
o.append(tag(g.x(0) - 60, g.bottom + 70, "latte 열을 모으면 [8, 9, 11], 합계 28", T3, 3, lead=False))
F[0] = 30
W("x-cafe", o, "세 번째 예제는 카페의 사흘 판매표예요. 행은 월, 화, 수요일이고 열은 coffee, latte, cake예요. for로 행마다 sum을 구하면 하루 합계가 나와요. 메뉴 합계는 열 하나를 모으는 일이에요. latte가 몇 번째 열인지는 13에서 배운 index로 menu에서 찾아요. 그 번호로 행마다 칸을 모으면 [8, 9, 11]이고 합계는 28이에요. menu 리스트의 순서와 sales 열의 순서를 맞춰 두면 이렇게 이름으로 열을 찾을 수 있어요." + REAL)

# ---------- summary ----------
o = [sec("trouble")] + head("정리", "막히면 오류의 마지막 줄을 봐요", RED)
tr = [("TypeError: 'in <string>' requires string as left operand, not int", "문자열 안에 숫자를 물었어요", '"3" in word'),
      ("IndexError: list index out of range", "행이나 열 번호가 넘쳤어요", "len()으로 확인"),
      ("ValueError: too many values to unpack (expected 3)", "행의 값 개수와 변수 개수가 달라요", "변수를 값 수만큼"),
      ("[[9, 0, 0], [9, 0, 0], [9, 0, 0]]", "칸 하나만 바꿨는데 모든 행이 바뀌었어요", "행을 직접 적기"),
      ("95 in scores  →  False", "in은 바깥 한 겹만 봐요", "95 in scores[1]"),
      ('"P" in word  →  False', "대문자와 소문자가 달라요", '"p" in word')]
for i, (q, a_, cmd) in enumerate(tr):
    y = 222 + i * 112
    o.append(f'<div{bi("rise", min(i + 1, 4))} style="position:absolute;left:96px;top:{y}px;width:1728px;height:104px;display:flex;flex-direction:row;gap:28px;align-items:center;border-bottom:2px solid {LINE}">'
             + num(i + 1, RED, 34)
             + '<div style="flex:1;display:flex;flex-direction:column;gap:4px">' + p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{INK};white-space:nowrap", e(q)) + p(f"font-size:24px;color:{SUB}", e(a_)) + '</div>'
             + p(f"width:320px;flex:none;{'font-family:' + MONO + ';font-size:26px;' if cmd.isascii() else 'font-size:26px;'}font-weight:700;line-height:1.5;color:{GR};white-space:pre", e(cmd)) + '</div>')
o.append(caption("오류가 안 나도 결과가 이상하면 몇 겹을 보고 있는지 따져 봐요.", 5))
W("trouble", o, "1번은 1파트의 word에 숫자 3을 물었을 때예요. 문자열 안에서는 글자만 찾을 수 있어서 \"3\"처럼 글자로 물어요. 2번과 3번은 2파트 오류 장에서 본 오류예요. 4번부터는 오류는 안 나지만 결과가 틀린 경우예요. 4번은 [[0] * 3] * 3으로 표를 만든 경우, 5번은 바깥 리스트에 안쪽 값을 물은 경우, 6번은 대소문자가 다른 경우예요. 1번 오류는 1파트 커널에서 3 in word를 실제로 실행한 결과예요. 나머지도 모두 hello-uv 커널에서 실제로 실행한 결과예요.", ("trouble", "정리"))

o = [sec("cheatsheet"), f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>']
L = [('"latte" in menu', "들어 있으면 True"), ('"tea" not in menu', "없으면 True"), ('"th" in word', "붙어 있는 글자 조각"), ("a in xs and b in xs", "둘 다 들어 있는지")]
R = [("scores[1][2]", "1행 2열 칸"), ("len(scores[0])", "열 수"), ("for row in scores:", "한 행씩 꺼내기"), ("col.append(row[1])", "열 하나 모으기")]
o.append(p(f"position:absolute;left:96px;top:200px;font-size:30px;font-weight:700;color:{T1}", "in과 not in"))
o += rule_rows(96, 250, 830, [[(e(a), "code", T1), (e(b), "sans", INK)] for a, b in L], [420, 380], rh=96, fs=30, orders=[None] * 4)
o.append(p(f"position:absolute;left:994px;top:200px;font-size:30px;font-weight:700;color:{T6}", "2차원 리스트"))
o += rule_rows(994, 250, 830, [[(e(a), "code", T6), (e(b), "sans", INK)] for a, b in R], [420, 380], rh=96, fs=30, orders=[None] * 4)
o.append(p(f"position:absolute;left:96px;top:720px;width:1728px;font-size:34px;font-weight:700;line-height:1.6;color:{INK}",
           'in은 바깥 한 겹만 봐요. 안쪽은 번호로 꺼낸 뒤 물어요.<br>'
           f'<span style="font-family:{MONO};color:{T6}">[행][열]</span> 순서예요. 행 수는 len(scores), 열 수는 len(scores[0])예요.'))
o.append(p(f"position:absolute;left:96px;top:900px;font-size:30px;font-weight:700;color:{GRAY}", "다음 챕터 15에서는 번호 대신 키로 값을 꺼내는 딕셔너리를 배워요."))
W("cheatsheet", o, "이번 챕터에서 쓴 코드를 한 장에 모았어요. in과 not in은 True, False로 답하고, 바깥 한 겹만 본다는 것을 기억해요. 2차원 리스트는 앞 번호가 행, 뒤 번호가 열이에요. 노트북에 이 장의 내용을 마크다운 셀로 정리해 두면 복습할 때 같이 봐요. 15에서는 번호 대신 이름으로 값을 꺼내는 딕셔너리를 배우고, 17에서 배울 if 문은 in이 만든 True, False로 할 일을 골라요.")

# ---------- toc ----------
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
parts = [(T1, "in과 not in", "리스트, 튜플, 문자열에서 들어 있는지 묻기, and와 or로 섞기, 한 겹만 보는 in", "in-why", "in-orders"),
         (T6, "2차원 리스트", "[행][열]로 꺼내기, 행 수와 열 수, for로 행과 열 다루기, 13의 리스트와 비교, 함정과 오류", "m-why", "m-err"),
         (T3, "실제로 써 보기", "성적표, 좌석표, 카페 판매표", "x-report", "x-cafe")]
TOC_NOTE = "세 파트는 앞 파트를 그대로 이어서 써요. 1파트는 in과 not in으로 값이 들어 있는지 묻는 법이에요. 2파트는 리스트 안에 리스트를 넣은 2차원 리스트로 표 모양 데이터를 다뤄요. 3파트는 둘을 섞어 실제 데이터 세 가지를 다뤄요. 셀은 위에서부터 차례로 실행해요."
DECK_TITLE = "파이썬 기초 3 (in, 2차원 리스트)"
t = [sec("toc"), f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>']
for i, (c_, h, s, a, b) in enumerate(parts, 1):
    y = 236 + (i - 1) * 200
    t.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:184px;display:flex;flex-direction:row;align-items:center;gap:40px;border-bottom:2px solid {LINE}">'
             + p(f"width:80px;flex:none;font-size:80px;font-weight:900;line-height:1;color:{c_}", str(i))
             + f'<div style="flex:1;display:flex;flex-direction:column;gap:10px">' + p(f"font-size:44px;font-weight:700;color:{INK}", h) + p(f"font-size:28px;line-height:1.45;color:{SUB}", e(s)) + '</div>'
             + p(f"width:200px;flex:none;text-align:right;font-size:30px;font-weight:700;color:{GRAY}", f"{page[a]}–{page[b]}쪽") + '</div>')
t.append(p(f"position:absolute;left:96px;top:880px;font-size:28px;color:{SUB}", f'{page["ready"]}쪽은 노트북 준비, {page["trouble"]}–{page["cheatsheet"]}쪽은 막힐 때와 한 장 요약이에요.'))
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(t) + f"\n<aside>{e(TOC_NOTE)}</aside>\n</section>\n")

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-02T05:00:00Z"}, "lists": "css", "title": DECK_TITLE, "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
print(len(ORDER), "slides")
