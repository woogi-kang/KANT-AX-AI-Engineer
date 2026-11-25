"""Generates every slide of the ML terms extra (번외 머신러닝 용어 풀이) and slides/deck.json.

What it is: a lookup dictionary for the words students got stuck on in chapters 45 to 50 (mean and median, IQR,
correlation, seed, feature and target, w and b, error, MAE, MSE, RMSE, R², loss, the MSE symbols, the parabola, the two
meanings of "기울기", derivative, gradient descent, learning rate, epoch, batch and stochastic, convergence,
hyperparameters, multiple regression, reading coefficients, the correlation heatmap). One term per slide, drawn first,
with the code line where it shows up and its real output. Every picture uses the same five students from 03_ml
(hours 1 to 5, scores 47 53 65 73 87, best line w = 10 and b = 35); only chapter 50's page uses its ten students.
Numbers come from tools/terms.py (run by tools/demo.sh, log in tools/demo.log, values in tools/data.json).

Layout rules (Stageshow skill, github.com/benjitaylor/skills, read in full for this deck):
1. one focal picture per page, drawn at full size; the code panel is the quiet second object (framing.md rule 1)
2. terms are labelled on the picture with leader tags and the term's own colour, never in separate cards (annotations.md)
3. say it once: the title says what the term means, the notes explain, no caption repeats the title (craft.md, Restraint)
4. the same word keeps the same colour on every page: w blue, b purple, error and loss red, the loss slope orange
5. one number gets to be big per page (craft.md, Restraint); the rest are lines
6. values move instead of swapping: points fly in from the table, w and b fill the empty model, 3 becomes 4 in place
Highlights come from tools/HIGHLIGHT.md, as many kinds as fit. No typing effect.
Usage: python3 tools/gen.py slides
"""
import html, json, math, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "tools"))
from highlight import *

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(HERE, "data.json")))
C, D = DATA["cells"], DATA["draw"]

SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
INK, SUB, LINE, CARD, BG = "#1D2330", "#4A5262", "#E1DED6", "#FFFFFF", "#F6F5F1"
BL, GR, OR, PUR, RED, TEAL, GRAY = "#2459C9", "#1F8A4C", "#B26A00", "#5A3BB8", "#A33131", "#0F7C86", "#6A7180"
MAG = "#A23B72"
WC, WBG = "#1E5FA8", "#E5EEF8"     # w, the line's slope (same blue as chapter 49)
BC, BBG = TEAL, "#E2F2F3"          # b, the intercept (same teal as chapter 49)
EC, EBG = RED, "#F8E6E6"           # error and loss
GC, GBG = OR, "#F7EEDD"            # the loss slope (경사), same orange as chapter 49
TC, TBG = TEAL, "#E2F2F3"
GRBG = "#E6F4EC"
DARK = "#252B36"
REAL = " 출력은 실제로 실행한 결과예요."
CALC = " 그림의 숫자는 tools/terms.py로 계산했어요."

PARTS = [("데이터 읽기", TEAL, "45~47"), ("모델과 채점", BL, "48"), ("경사 하강법", OR, "49"),
         ("여러 열로 예측", MAG, "50"), ("헷갈리는 짝과 오해", RED, "45~50"), ("용어로 코드 읽기", GR, "48~50")]


def e(s):
    return html.escape(str(s), quote=False)


def p(style, text, attrs=""):
    return f'<p{attrs} style="{style}">{text}</p>'


ORDER, SECTIONS, NOTES = [], {}, {}


def W(sid, parts, notes, section=None):
    if section:
        SECTIONS[section[0]] = {"description": section[1], "start": sid}
    ORDER.append(sid)
    with open(os.path.join(OUT, sid + ".html"), "w") as f:
        f.write("\n".join(parts) + f"\n<aside>{e(notes)}</aside>\n</section>\n")


def sec(sid, transition="fade", bg=BG):
    return f'<section id="{sid}" data-transition="{transition}" style="background:{bg};color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">'


PAGE = {}   # filled after the order is known (two passes)
if os.environ.get("PAGES"):
    PAGE.update(json.loads(os.environ["PAGES"]))


def pg(sid):
    return str(PAGE.get(sid, "?"))


def head(part, title, alias=None, where=None):
    """Eyebrow (part and chapter), the title that says what the term means, and a thin line of other names for it."""
    name, color, ch = PARTS[part]
    o = [p(f"position:absolute;left:96px;top:48px;font-size:26px;font-weight:700;color:{color};white-space:nowrap",
           f"{part + 1}. {e(name)} <span style=\"color:{GRAY};font-weight:500\">· {e(where or ch)}</span>", ' id="eyebrow"'),
         f'<h2 id="title" style="position:absolute;left:96px;top:92px;width:1728px;font-size:54px;font-weight:700;line-height:1.3;color:{INK}">{title}</h2>']
    if alias:
        chips = "".join(p(f"font-family:{MONO if a.isascii() else SANS};font-size:24px;font-weight:700;color:{c};background:{bg};border-radius:8px;padding:2px 14px;white-space:nowrap", e(a))
                        for a, c, bg in alias)
        o.append(f'<div id="alias" style="position:absolute;left:96px;top:178px;display:flex;flex-direction:row;align-items:center;gap:12px">'
                 + p(f"font-size:22px;font-weight:700;color:{GRAY};margin-right:6px;white-space:nowrap", "같은 말") + chips + '</div>')
    return o


def plain_head(eyebrow, title, color=GRAY):
    return [p(f"position:absolute;left:96px;top:48px;font-size:26px;font-weight:700;color:{color};white-space:nowrap", e(eyebrow)),
            f'<h2 id="title" style="position:absolute;left:96px;top:92px;width:1728px;font-size:54px;font-weight:700;line-height:1.3;color:{INK}">{title}</h2>']


def fade(order):
    return f' data-build-in="fade order {order}"'


def rise(order):
    return f' data-build-in="rise order {order}"'


def fly(order, src):
    return f' data-build-in="fly order {order}" data-from="{src}"'


def label(x, y, text, color, size=28, attrs="", mono=False, weight=700, anchor="left"):
    tr = {"left": "", "center": "transform:translateX(-50%);", "right": "transform:translateX(-100%);"}[anchor]
    return p(f"position:absolute;left:{x:.0f}px;top:{y:.0f}px;{tr}font-family:{MONO if mono else SANS};font-size:{size}px;font-weight:{weight};line-height:1.3;color:{color};white-space:nowrap", text, attrs)


def note(x, y, w, text, color=SUB, size=28, attrs="", weight=500):
    return p(f"position:absolute;left:{x}px;top:{y}px;width:{w}px;font-size:{size}px;font-weight:{weight};line-height:1.5;color:{color};word-break:keep-all", text, attrs)


def chip(text, color, bg, fs=26, attrs="", mono=None):
    m = text.isascii() if mono is None else mono
    return p(f"display:inline-block;font-family:{MONO if m else SANS};font-size:{fs}px;font-weight:700;line-height:1.3;color:{color};background:{bg};border-radius:8px;padding:2px 12px;white-space:nowrap", e(text), attrs)


def c(text, color, bold=True):
    """A coloured span inside running text."""
    return f'<span style="color:{color};{"font-weight:700" if bold else ""}">{text}</span>'


def mk(text, color, bg, order, extra=""):
    """A span already tinted, whose tint fades in on its step (HIGHLIGHT.md 4-4, 4-5)."""
    return f'<span{MARK(order)} style="color:{color};background:{bg};border-radius:6px;padding:0 4px;{extra}">{text}</span>'


# ---------- code panel (VS Code notebook cell look, like chapters 45 to 48) ----------
def code(left, top, w, lines, out=None, fs=24, n=None, tid=None, attrs="", out_colors=None, gap=8):
    """A notebook cell: code box and its output under it. Returns (html, bottom_y). Line i of code is centred at
    top + 12 + fs*1.5*(i+0.5); output line j at code_bottom + gap + fs*1.5*(j+0.5)."""
    lh = fs * 1.5
    idt = f' id="{tid}"' if tid else ""
    txt = "".join(p(f"font-family:{MONO};font-size:{fs}px;line-height:1.5;white-space:pre;color:{INK}", hl_py(l) if l else "&#160;") for l in lines)
    h = 24 + lh * len(lines)
    o = f'<div{idt}{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px">'
    o += f'<div style="background:#FFFFFF;border:2px solid {LINE};border-radius:12px;padding:10px 20px">{txt}</div>'
    bottom = top + h + 4
    if out:
        oc = out_colors or {}
        o += f'<div style="padding:{gap}px 22px 0">' + "".join(
            p(f"font-family:{MONO};font-size:{fs}px;line-height:1.5;white-space:pre;color:{oc.get(j, INK)}", e(l) if l else "&#160;") for j, l in enumerate(out)) + '</div>'
        bottom += gap + lh * len(out)
    o += '</div>'
    return o, bottom


def cline(top, i, fs=24):
    return top + 12 + fs * 1.5 * (i + 0.5)


def oline(top, nlines, j, fs=24, gap=8):
    return top + 24 + fs * 1.5 * nlines + 4 + gap + fs * 1.5 * (j + 0.5)


KW = {"for", "in", "print", "round", "import", "from", "as", "def", "return", "range"}


def hl_py(line):
    """Quiet syntax colour: comments gray, strings green, keywords blue. Enough for short cells."""
    out, i = "", 0
    m = re.match(r"^(.*?)(#.*)$", line)
    body, com = (m.group(1), m.group(2)) if m and line.count('"', 0, line.find("#")) % 2 == 0 else (line, "")
    for tok in re.split(r'("[^"]*")', body):
        if tok.startswith('"') and tok.endswith('"') and len(tok) >= 2:
            out += f'<span style="color:#1F7A45">{e(tok)}</span>'
        else:
            out += re.sub(r"\b(for|in|import|from|as|print|round)\b", lambda mm: f'<span style="color:#2459C9">{mm.group(1)}</span>', e(tok))
    if com:
        out += f'<span style="color:#8A909C">{e(com)}</span>'
    return out


def tw(s, fs=24):
    """Rendered width of a monospace string: Hangul 0.92 em (Noto Sans KR), the rest 0.6 em."""
    return sum(fs * (0.92 if '가' <= ch <= '힣' else 0.6) for ch in s)


def tag(x, y, text, color, attrs="", size=26, lead=True):
    return p(f"position:absolute;left:{x:.0f}px;top:{y - size * 0.68:.0f}px;font-size:{size}px;font-weight:700;line-height:1.36;color:{color};white-space:nowrap",
             ("← " if lead else "") + text, attrs)


# ---------- charts drawn in SVG from the real numbers ----------
class Ax:
    """A chart box at (x, y) of size (w, h) on the slide, data ranges xr and yr."""

    def __init__(self, x, y, w, h, xr, yr):
        self.x, self.y, self.w, self.h, self.xr, self.yr = x, y, w, h, xr, yr

    def X(self, v):
        return self.x + (v - self.xr[0]) / (self.xr[1] - self.xr[0]) * self.w

    def Y(self, v):
        return self.y + self.h - (v - self.yr[0]) / (self.yr[1] - self.yr[0]) * self.h


def svg(inner, attrs="", tid=None):
    """One full-slide SVG layer (1920 x 1080), so every layer shares slide coordinates."""
    idt = f' id="{tid}"' if tid else ""
    return f'<svg{idt}{attrs} style="position:absolute;left:0;top:0;width:1920px;height:1080px;overflow:visible;pointer-events:none" viewBox="0 0 1920 1080">{inner}</svg>'


def stext(x, y, t, color=GRAY, size=22, anchor="middle", weight=500, mono=False):
    return f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" font-family="{MONO if mono else SANS}">{e(t)}</text>'


def axes(a, xticks, yticks, xlabel="", ylabel="", fmt=str, yfmt=None):
    yfmt = yfmt or fmt
    o = f'<line x1="{a.x}" y1="{a.y + a.h}" x2="{a.x + a.w}" y2="{a.y + a.h}" stroke="#9AA0AB" stroke-width="3"/>'
    o += f'<line x1="{a.x}" y1="{a.y}" x2="{a.x}" y2="{a.y + a.h}" stroke="#9AA0AB" stroke-width="3"/>'
    for t in xticks:
        o += f'<line x1="{a.X(t):.1f}" y1="{a.y + a.h}" x2="{a.X(t):.1f}" y2="{a.y + a.h + 10}" stroke="#9AA0AB" stroke-width="3"/>'
        o += stext(a.X(t), a.y + a.h + 40, fmt(t))
    for t in yticks:
        o += f'<line x1="{a.x}" y1="{a.Y(t):.1f}" x2="{a.x + a.w}" y2="{a.Y(t):.1f}" stroke="#E7E5DF" stroke-width="2"/>'
        o += stext(a.x - 16, a.Y(t) + 8, yfmt(t), anchor="end")
    if xlabel:
        o += stext(a.x + a.w, a.y + a.h + 76, xlabel, SUB, 24, "end", 700)
    if ylabel:
        o += stext(a.x, a.y - 22, ylabel, SUB, 24, "start", 700)
    return o


def poly(a, pts, color, width=5, dash=None, extra=""):
    d = " ".join(f"{a.X(x):.1f},{a.Y(y):.1f}" for x, y in pts)
    ds = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<polyline points="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"{ds}{extra}/>'


def dot(a, x, y, color=INK, r=11, extra=""):
    return f'<circle cx="{a.X(x):.1f}" cy="{a.Y(y):.1f}" r="{r}" fill="{color}"{extra}/>'


def hdot(x, y, color=INK, r=11, attrs=""):
    """A point as an HTML disc, so it can fly in from a table row."""
    return f'<div{attrs} style="position:absolute;left:{x - r:.1f}px;top:{y - r:.1f}px;width:{2 * r}px;height:{2 * r}px;border-radius:50%;background:{color}"></div>'


def seg(x1, y1, x2, y2, color, width=4, dash=None, cap="round"):
    ds = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{width}" stroke-linecap="{cap}"{ds}/>'


def arrowhead(x, y, ang, color, s=16):
    """A filled triangle pointing at angle ang (radians) with its tip at (x, y)."""
    p1 = (x - s * math.cos(ang - 0.45), y - s * math.sin(ang - 0.45))
    p2 = (x - s * math.cos(ang + 0.45), y - s * math.sin(ang + 0.45))
    return f'<polygon points="{x:.1f},{y:.1f} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="{color}"/>'


def arr(x1, y1, x2, y2, color, width=4, s=16):
    ang = math.atan2(y2 - y1, x2 - x1)
    ex, ey = x2 - (s * 0.6) * math.cos(ang), y2 - (s * 0.6) * math.sin(ang)
    return seg(x1, y1, ex, ey, color, width) + arrowhead(x2, y2, ang, color, s)


def harrow(w=60, color="#C9CED8", attrs="", style=""):
    return f'<x-shape{attrs} kind="arrow-right" style="width:{w}px;height:30px;flex:none;background:{color};{style}"></x-shape>'


def bar(x, y, w, h, color, attrs="", r=6):
    return f'<div{attrs} style="position:absolute;left:{x:.0f}px;top:{y:.0f}px;width:{max(w, 0):.0f}px;height:{max(h, 0):.0f}px;border-radius:{r}px;background:{color}"></div>'


def table(left, top, cols, rows, widths, fs=28, rh=56, tid=None, attrs="", row_ids=None, row_attrs=None, cs=None, head_color=INK, idx=True):
    """A small DataFrame as the notebook shows it: bold header, index on the left, striped rows."""
    W_t = sum(widths) + (56 if idx else 0)
    idt = f' id="{tid}"' if tid else ""
    o = [f'<div{idt}{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{W_t}px;display:flex;flex-direction:column">']
    hd = (p(f"width:56px;flex:none", "&#160;") if idx else "") + "".join(
        p(f"width:{w}px;flex:none;padding-right:14px;text-align:right;font-family:{MONO};font-size:{fs}px;font-weight:700;color:{head_color};white-space:nowrap", cc) for cc, w in zip(cols, widths))
    o.append(f'<div style="height:{rh}px;display:flex;flex-direction:row;align-items:center;border-bottom:2px solid #BFC4CE">{hd}</div>')
    for i, r in enumerate(rows):
        bgc = "#F4F5F7" if i % 2 == 0 else "transparent"
        cells = (p(f"width:56px;flex:none;padding-right:14px;text-align:right;font-family:{MONO};font-size:{fs}px;font-weight:700;color:{INK}", str(i)) if idx else "")
        for j, (v, w) in enumerate(zip(r, widths)):
            extra = (cs or {}).get((i, j), "")
            cells += p(f"width:{w}px;flex:none;padding-right:14px;text-align:right;font-family:{MONO};font-size:{fs}px;color:{INK};white-space:nowrap;{extra}", e(v))
        rid = f' id="{row_ids[i]}"' if row_ids else ""
        ra = (row_attrs or {}).get(i, "")
        o.append(f'<div{rid}{ra} style="height:{rh}px;display:flex;flex-direction:row;align-items:center;background:{bgc}">{cells}</div>')
    o.append('</div>')
    return "".join(o)


def strip(left, top, w, h, inner, attrs="", pad=40, bg=DARK):
    return (f'<div{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:{bg};border-radius:20px;padding:0 {pad}px;display:flex;flex-direction:row;align-items:center;gap:0">'
            + inner + '</div>')


def mono_line(parts, size=40, color="#E6E9EF"):
    """One code line of coloured pieces: parts = [(text, colour, attrs), ...]."""
    sp = ""
    for pt in parts:
        t, col = pt[0], pt[1]
        a = pt[2] if len(pt) > 2 else ""
        sp += f'<span{a} style="display:inline-block;color:{col}">{e(t).replace(" ", "&#160;")}</span>'
    return p(f"font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.5;color:{color};white-space:pre", sp)


# ---------- the five students, used on most pages ----------
HRS = [1, 2, 3, 4, 5]
SCO = [47, 53, 65, 73, 87]
U = D["u"]


def five_chart(a, pts_attrs=None, line=True, line_attrs="", show_pts=True, pt_ids=None):
    """Axes, the five points as HTML discs and the w=10, b=35 line. Returns a list of html parts."""
    o = [svg(axes(a, [0, 1, 2, 3, 4, 5, 6], [0, 20, 40, 60, 80, 100], "공부 시간 (hours)", "점수 (scores)"))]
    if line:
        o.append(svg(poly(a, [(0, 35), (6, 95)], WC, 6), line_attrs))
    if show_pts:
        for i, (hx, sy) in enumerate(zip(HRS, SCO)):
            at = (pts_attrs or {}).get(i, "")
            idt = f' id="{pt_ids[i]}"' if pt_ids else ""
            o.append(hdot(a.X(hx), a.Y(sy), INK, 12, idt + at))
    return o


def u_chart(a, xticks=(7, 8, 9, 10, 11, 12, 13), yticks=(0, 20, 40, 60, 80), curve_attrs="", xr=None, color=EC, width=6):
    o = [svg(axes(a, list(xticks), list(yticks), "기울기 w (b = 35로 고정)", "손실 MSE"))]
    pts = [(w, m) for w, m in U if (xr or a.xr)[0] <= w <= (xr or a.xr)[1] and m <= a.yr[1]]
    o.append(svg(poly(a, pts, color, width), curve_attrs))
    return o


def mse(w):
    return 3.2 + 11 * (w - 10) ** 2     # same as tools/terms.py's numbers (the 'ucurve' cell): checked below


for w_, m_ in [(8, 47.2), (9, 14.2), (10, 3.2), (11, 14.2), (12, 47.2)]:
    assert abs(mse(w_) - m_) < 1e-9
for w_, m_ in U:
    assert abs(mse(w_) - m_) < 1e-6, (w_, m_)


def tangent(a, w0, half, color=GC, width=5, attrs=""):
    g = 22 * (w0 - 10)
    x1, x2 = w0 - half, w0 + half
    top = a.yr[1] * 0.97
    if g:
        lim = w0 + (top - mse(w0)) / g    # where the line leaves the top of the chart
        x1, x2 = (max(x1, lim), x2) if g < 0 else (x1, min(x2, lim))
    return svg(seg(a.X(x1), a.Y(mse(w0) + g * (x1 - w0)), a.X(x2), a.Y(mse(w0) + g * (x2 - w0)), color, width), attrs)


# =====================================================================================
# cover
# =====================================================================================
o = [f'<section id="cover" data-transition="fade" style="background:{INK};color:{BG};font-family:{SANS};font-variant-ligatures:none;padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
     '<p style="font-size:28px;font-weight:700;color:#F2B27A;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 번외</p>',
     f'<h1{SLAM(1)} style="font-size:96px;font-weight:900;line-height:1.35;color:{BG}">머신러닝<br>용어 풀이</h1>',
     '<p style="font-size:38px;line-height:1.45;color:#BFC6D4">45~50에서 막히는 말을<br>그림 한 장씩으로 찾아봐요</p>']
o.append(f'<div id="cov-card" style="position:absolute;left:1040px;top:190px;width:760px;height:600px;background:#FFFFFF;border-radius:24px"></div>')
a = Ax(1150, 260, 580, 400, (6.5, 13.5), (0, 80))
o.append(svg(axes(a, [8, 10, 12], [0, 40, 80], "기울기 w", "손실 MSE")))
o.append(svg(poly(a, [(w, m) for w, m in U if m <= 80], EC, 7)))
o.append(tangent(a, 8, 0.6))
o.append(svg(dot(a, 8, 47.2, GC, 14) + dot(a, 10, 3.2, INK, 10)))
o.append(label(a.X(8) + 30, a.Y(47.2) - 20, "경사 −44", GC, 28))
o.append(label(a.X(10), a.Y(3.2) - 104, "가장 낮은 곳", INK, 26, anchor="center"))
o.append(p(f"position:absolute;left:1040px;top:820px;width:760px;font-size:26px;line-height:1.5;color:#BFC6D4",
           "공부 시간 5명 데이터에서 w를 바꿔 가며 잰 손실이에요. 이 덱의 그림은 대부분 이 5명으로 그렸어요."))
W("cover", o, "45부터 50까지 수업에서 막히는 용어를 한곳에 모은 사전이에요. 순서대로 읽는 덱이 아니라, 수업 중에 모르는 말이 나오면 2쪽 목차나 맨 뒤 가나다 찾아보기에서 쪽을 찾아 펴 보는 자료예요. 쪽마다 용어 하나를 그림 한 장, 그 말이 나오는 코드 한 줄, 실제 출력으로 풀어요. 거의 모든 그림은 03_ml 노트북의 공부 시간 5명 데이터로 그렸어요. 오른쪽 그림은 49 경사 하강법의 손실 그래프예요." + CALC, ("intro", "들어가기"))

# =====================================================================================
# 2 toc
# =====================================================================================
TOC_TERMS = [
    ("평균과 중앙값, 사분위수와 IQR, 상관계수, 난수와 시드", "mean", "seed"),
    ("특성과 타깃, 모델과 학습, 기울기와 절편, 예측값과 오차, MAE, MSE와 RMSE, R²", "xy", "r2"),
    ("손실 함수, 수식 기호, 2차함수, 기울기의 두 뜻, 미분, 경사 하강법, 학습률, epoch, 배치와 확률적, 수렴, 하이퍼파라미터", "loss", "hyper"),
    ("다중 선형 회귀, 계수 읽기, 상관계수 표와 heatmap", "multi", "heat"),
    ("오차·손실·점수, 상관계수·기울기·R², 오해 넷", "pair1", "myth2"),
    ("SGDRegressor 셀, 학습 기록 표, 결과 출력", "read1", "read3"),
]
o = [sec("toc"), f'<h2 style="position:absolute;left:96px;top:72px;font-size:60px;font-weight:700;line-height:1.3;color:{INK}">목차</h2>']
for i, ((name, color, ch), (terms, a_, b_)) in enumerate(zip(PARTS, TOC_TERMS)):
    x, y = 96 + (i % 2) * 884, 196 + (i // 2) * 228
    o.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:844px;height:208px;display:flex;flex-direction:row;gap:26px;border-bottom:2px solid {LINE}">'
             + p(f"width:56px;flex:none;font-size:64px;font-weight:900;line-height:1;color:{color}", str(i + 1))
             + '<div style="flex:1;display:flex;flex-direction:column;gap:8px">'
             + '<div style="display:flex;flex-direction:row;align-items:baseline;gap:18px">'
             + p(f"font-size:40px;font-weight:700;color:{INK};white-space:nowrap", e(name))
             + p(f"font-size:24px;font-weight:500;color:{GRAY};white-space:nowrap", f"챕터 {e(ch)} · {pg(a_)}–{pg(b_)}쪽") + '</div>'
             + p(f"font-size:25px;line-height:1.5;color:{SUB};word-break:keep-all", e(terms)) + '</div></div>')
o.append(p(f"position:absolute;left:96px;top:900px;font-size:28px;color:{SUB}",
           f"{pg('why')}–{pg('example')}쪽은 들어가기, {pg('index1')}–{pg('index2')}쪽은 가나다 순 찾아보기예요."))
W("toc", o, "용어를 수업에 나온 순서대로 여섯 묶음으로 나눴어요. 1은 45부터 47의 데이터 읽기, 2는 48의 모델과 채점, 3은 49의 경사 하강법, 4는 50의 여러 열 예측이에요. 5는 비슷해서 자주 섞이는 용어끼리 비교하고 흔한 오해를 실제 숫자로 바로잡아요. 6은 수업 코드 한 셀을 용어로 읽어 보는 연습이에요. 이름만 알고 쪽을 모르면 맨 뒤 가나다 찾아보기를 펴요.")

# =====================================================================================
# 3 why
# =====================================================================================
o = [sec("why")] + plain_head("들어가기", "같은 것에 이름이 셋, 같은 이름에 뜻이 둘이에요")
WHY = ['# 입력 데이터 (피쳐:Feature) : 2차원 - 독립변수',
       'X = df[["hours"]]   # 공부시간',
       '',
       'print(f"기울기: {model.coef_[0]:.2f}")  # 기울기 Weight',
       '',
       '## 경사하강법 (Gradient Descent)']
html_, bot = code(96, 236, 1180, WHY, fs=28)
o.append(html_)
LH28 = 28 * 1.5
# boxes on the class code: three names for X, then the two "기울기"
def wx(line, start):
    return 96 + 22 + tw(WHY[line][:WHY[line].find(start)], 28)
o.append(box(1, wx(0, "피쳐") - 6, cline(236, 0, 28) - 24, tw("피쳐:Feature", 28) + 12, 48, BL))
o.append(box(1, wx(0, "독립변수") - 6, cline(236, 0, 28) - 24, tw("독립변수", 28) + 12, 48, BL))
o.append(box(1, wx(1, "X") - 6, cline(236, 1, 28) - 24, tw("X", 28) + 12, 48, BL))
o.append(box(2, wx(3, "기울기 W") - 6, cline(236, 3, 28) - 24, tw("기울기 Weight", 28) + 12, 48, WC))
o.append(box(3, wx(5, "경사하강법") - 6, cline(236, 5, 28) - 24, tw("경사하강법 (Gradient Descent)", 28) + 12, 48, GC))
o.append(f'<div{rise(1)} style="position:absolute;left:96px;top:{bot + 56:.0f}px;width:1728px;display:flex;flex-direction:row;align-items:center;gap:18px">'
         + p(f"font-size:32px;font-weight:700;color:{BL};white-space:nowrap", "이름 셋")
         + chip("피쳐(Feature)", BL, WBG, 30) + chip("독립변수", BL, WBG, 30) + chip("X", BL, WBG, 30)
         + p(f"font-size:30px;color:{SUB};white-space:nowrap", "모두 모델에 넣는 문제 열이에요") + '</div>')
o.append(f'<div{rise(3)} style="position:absolute;left:96px;top:{bot + 140:.0f}px;width:1728px;display:flex;flex-direction:row;align-items:center;gap:18px">'
         + p(f"font-size:32px;font-weight:700;color:{GC};white-space:nowrap", "뜻 둘")
         + chip("기울기 Weight", WC, WBG, 30) + p(f"font-size:30px;color:{SUB};white-space:nowrap", "직선이 얼마나 가파른지")
         + chip("Gradient", GC, GBG, 30) + p(f"font-size:30px;color:{SUB};white-space:nowrap", "손실이 어느 쪽으로 내려가는지") + '</div>')
o.append(label(1320, cline(236, 3, 28) - 20, f"{pg('wb')}쪽", WC, 28, rise(2)))
o.append(label(1320, cline(236, 5, 28) - 20, f"{pg('two')}쪽", GC, 28, rise(3)))
W("why", o, "용어가 어려운 이유는 이름이 여러 개이기 때문이에요. 03_ml 노트북의 주석만 봐도 같은 X를 피쳐, Feature, 독립변수로 불러요. 반대로 기울기라는 한 단어는 두 뜻으로 나와요. coef_ 옆의 기울기는 직선이 얼마나 가파른지이고, 경사하강법의 경사, Gradient는 손실 그래프의 기울기예요. 그래서 이 사전은 쪽마다 위에 같은 말을 모아 두고, 같은 용어는 모든 쪽에서 같은 색으로 칠했어요. 직선의 기울기 w는 파랑, 손실의 기울기는 주황이에요. 코드는 수업 노트북에 있던 주석 그대로예요.", None)

# =====================================================================================
# 4 map
# =====================================================================================
o = [sec("map")] + plain_head("들어가기", "용어는 모델을 만드는 다섯 단계 위에 있어요")
STN = [("데이터", TEAL, [("평균·중앙값", "mean"), ("IQR", "iqr"), ("상관계수", "corr"), ("시드", "seed")]),
       ("문제와 정답", BL, [("특성과 타깃", "xy"), ("다중 회귀", "multi"), ("heatmap", "heat")]),
       ("모델", BL, [("모델·학습", "model"), ("기울기 w·절편 b", "wb"), ("하이퍼파라미터", "hyper")]),
       ("학습", OR, [("손실 함수", "loss"), ("미분", "deriv"), ("경사 하강법", "gd"), ("학습률", "lr"), ("epoch", "epoch")]),
       ("예측과 채점", PUR, [("예측값·오차", "error"), ("MAE", "mae"), ("MSE·RMSE", "mse"), ("R²", "r2")])]
for i, (name, color, items) in enumerate(STN):
    x = 96 + i * 352
    o.append(f'<div style="position:absolute;left:{x}px;top:250px;width:296px;height:96px;border-radius:18px;background:{color};display:flex;align-items:center;justify-content:center">'
             + p("font-size:34px;font-weight:700;color:#FFFFFF;white-space:nowrap", e(name)) + '</div>')
    if i < 4:
        o.append(harrow(44, "#C9CED8", "", f"position:absolute;left:{x + 302}px;top:283px"))
    rows = "".join(f'<div style="height:78px;display:flex;flex-direction:row;align-items:center;justify-content:space-between;border-bottom:2px solid {LINE}">'
                   + p(f"font-size:30px;font-weight:700;color:{INK};white-space:nowrap", e(t)) + p(f"font-size:26px;font-weight:700;color:{color};white-space:nowrap", f"{pg(s)}쪽") + '</div>'
                   for t, s in items)
    o.append(f'<div{STAGGER(i + 1, 80)} style="position:absolute;left:{x}px;top:372px;width:296px;display:flex;flex-direction:column">{rows}</div>')
o.append(note(96, 840, 1728, f"쓰는 순서는 왼쪽에서 오른쪽이에요. 학습 단계의 손실은 채점의 MSE와 같은 숫자예요({pg('pair1')}쪽).", SUB, 28, rise(6)))
W("map", o, "머신러닝 코드는 늘 다섯 단계로 흘러가요. 데이터를 읽고, 문제 열과 정답 열을 나누고, 모델을 만들고, 학습시키고, 예측해서 채점해요. 용어도 이 다섯 단계 중 한 곳에 붙어 있어요. 모르는 말이 나오면 지금 코드가 어느 단계인지 먼저 보고 그 단계 아래에서 찾으면 빨라요. 학습 단계의 손실과 채점 단계의 MSE는 같은 계산이라 헷갈리기 쉬운데, 뒤의 헷갈리는 짝에서 따로 비교해요.")

# =====================================================================================
# 5 example
# =====================================================================================
o = [sec("example")] + plain_head("들어가기", "그림은 대부분 공부 시간 5명으로 그려요")
FIVE = C["five"]
rows5 = [(h, s) for h, s in zip(HRS, SCO)]
o.append(code(96, 220, 600, FIVE["code"], fs=24)[0])
o.append(table(126, 470, ["hours", "scores"], rows5, [150, 170], fs=30, rh=60, row_ids=[f"r5-{i}" for i in range(5)]))
a = Ax(940, 250, 820, 560, (0, 6), (0, 100))
o += five_chart(a, pts_attrs={i: fly(1, f"r5-{i}") for i in range(5)}, line_attrs=WIPE(2))
o.append(label(a.X(5.0) + 20, a.Y(85) - 96, "w = 10, b = 35인 직선", WC, 28, fade(2) + DELAY(300), anchor="right"))
o.append(note(940, 920, 880, f"{pg('multi')}–{pg('heat')}쪽(50 다중 회귀)만 10명 데이터예요.", SUB, 26, rise(3)))
W("example", o, "이 사전의 그림은 거의 다 03_ml 노트북 첫 셀의 데이터로 그렸어요. 공부 시간 1시간부터 5시간인 학생 5명과 시험 점수예요. 표의 한 줄이 그래프의 점 하나예요. 이 5명에 가장 잘 맞는 직선은 기울기 10, 절편 35라서 숫자가 딱 떨어져요. 48의 LinearRegression도, 49의 경사 하강법도 이 직선을 찾아요. 같은 데이터로 계속 보면 용어끼리 어떻게 이어지는지 보여요. 50의 다중 회귀 쪽만 수업과 같은 10명 데이터를 써요." + REAL)

# =====================================================================================
# part 1: data
# =====================================================================================
# 6 mean and median
o = [sec("mean")] + head(0, "평균은 큰 값에 끌려가고, 중앙값은 한가운데 사람이에요",
                         [("mean()", TC, TBG), ("median()", TC, TBG), ("가운데값", TC, TBG)], "46")
FH = D["fare_hist"]
a = Ax(150, 300, 980, 520, (0, 110), (0, 330))
cnt, ed = FH["counts"], FH["edges"]
bars = ""
for k in range(len(cnt)):
    x0, x1 = ed[k], min(ed[k + 1], 110)
    if ed[k] >= 100:
        x0, x1 = 102, 110
    bars += f'<rect x="{a.X(x0) + 2:.1f}" y="{a.Y(cnt[k]):.1f}" width="{a.X(x1) - a.X(x0) - 4:.1f}" height="{a.Y(0) - a.Y(cnt[k]):.1f}" fill="{"#C9CED8" if ed[k] < 100 else "#E8B8B8"}" rx="3"/>'
o.append(svg(axes(a, [0, 20, 40, 60, 80, 100], [0, 100, 200, 300], "요금 (fare)", "승객 수", fmt=lambda t: str(t) if t < 100 else "100+", yfmt=str)))
o.append(svg(bars, WIPE(1)))
o.append(label(a.X(106), a.Y(cnt[-1]) - 44, f"100 이상 {cnt[-1]}명", RED, 24, fade(1) + DELAY(300), anchor="center"))
o.append(svg(seg(a.X(FH["median"]), a.y - 10, a.X(FH["median"]), a.y + a.h, TC, 5), fade(2)))
o.append(label(a.X(FH["median"]) + 14, a.y - 6, f"중앙값 {FH['median']:.2f}", TC, 30, fade(2)))
o.append(svg(seg(a.X(FH["mean"]), a.y + 70, a.X(FH["mean"]), a.y + a.h, EC, 5, "12 8"), fade(3)))
o.append(label(a.X(FH["mean"]) + 14, a.y + 76, f"평균 {FH['mean']:.2f}", EC, 30, fade(3)))
cm = C["mean"]
html_, bot = code(1220, 300, 610, cm["code"][1:], cm["out"], fs=20)
o.append(html_)
o.append(f'<div id="maxv" style="position:absolute;left:{1220 + 22}px;top:{oline(300, 3, 2, 20) - 15:.0f}px;width:330px;height:30px"></div>')
o.append(pulse(4, "maxv"))
o.append(note(1240, bot + 30, 590, "요금 512를 낸 승객 몇 명이 평균을 오른쪽으로 끌어요. 빈칸을 채울 때 46은 중앙값을 써요.", SUB, 26, rise(4)))
W("mean", o, "평균은 모두 더해서 사람 수로 나눈 값이고, 중앙값은 줄을 세웠을 때 한가운데 사람의 값이에요. 타이타닉 891명의 요금을 보면 대부분 30 아래인데, 512를 낸 승객처럼 아주 큰 값이 몇 명 있어요. 그 몇 명 때문에 평균은 32.2로 오른쪽에 서고, 중앙값은 14.45에 그대로 있어요. 그래서 46에서는 큰 값이 섞인 열의 빈칸을 중앙값으로 채웠어요. 코드에서는 mean()과 median()이에요. 첫 줄의 titanic은 46처럼 sns.load_dataset으로 불러왔어요." + REAL, ("p1", "데이터 읽기"))

# 7 IQR
o = [sec("iqr")] + head(0, "IQR은 가운데 절반이 차지한 폭이고, 1.5배 밖은 튀는 값이에요",
                        [("quantile()", TC, TBG), ("사분위수", TC, TBG), ("이상치", TC, TBG), ("울타리", TC, TBG)], "46")
a = Ax(150, 330, 1600, 250, (0, 110), (0, 1))
o.append(svg(axes(a, [0, 20, 40, 60, 80, 100], [], "요금 (fare)", "")))
yb = a.y + 30
q1, q3, med, up = FH["q1"], FH["q3"], FH["median"], FH["upper"]
o.append(svg(f'<rect x="{a.X(q1):.1f}" y="{yb}" width="{a.X(q3) - a.X(q1):.1f}" height="110" fill="{TBG}" stroke="{TC}" stroke-width="4" rx="6"/>'
             + seg(a.X(med), yb, a.X(med), yb + 110, TC, 5) + seg(a.X(0), yb + 55, a.X(q1), yb + 55, TC, 3) + seg(a.X(q3), yb + 55, a.X(up), yb + 55, TC, 3)))
o.append(label(a.X(q1), yb - 86, "Q1 7.91", TC, 28, anchor="center"))
o.append(label(a.X(q1), yb - 42, "아래에서 25%", GRAY, 22, anchor="center"))
o.append(label(a.X(q3), yb - 86, "Q3 31.0", TC, 28, anchor="center"))
o.append(label(a.X(q3), yb - 42, "아래에서 75%", GRAY, 22, anchor="center"))
o.append(svg(seg(a.X(up), yb - 30, a.X(up), yb + 150, EC, 5, "12 8"), fade(2)))
o.append(label(a.X(up), yb - 86, f"울타리 {up:.2f}", EC, 28, fade(2), anchor="center"))
import random
random.seed(3)
outs = "".join(f'<circle cx="{a.X(min(105, up + 3 + random.random() * 40)):.1f}" cy="{yb + 20 + random.random() * 70:.1f}" r="6" fill="{EC}" fill-opacity="0.55"/>' for _ in range(40))
o.append(svg(outs, fade(3)))
o.append(label(a.X(96), yb + 128, f"울타리 밖 {FH['over']}명", EC, 28, fade(3), anchor="center"))
o.append(underline(1, a.X(q1), a.X(q3), yb + 128, TC, 6))
o.append(label((a.X(q1) + a.X(q3)) / 2, yb + 140, "IQR = Q3 − Q1 = 23.09", TC, 28, fade(1), anchor="center"))
ci = C["iqr"]
html_, bot = code(96, 730, 1000, ci["code"], fs=20)
o.append(html_)
o.append(f'<div style="position:absolute;left:1140px;top:740px;width:690px">' + "".join(p(f"font-family:{MONO};font-size:24px;line-height:1.6;white-space:pre;color:{INK}", e(l)) for l in ci["out"]) + '</div>')
o.append(note(1140, 880, 690, "울타리 = Q3 + 1.5 × IQR. 46은 울타리 밖에서 누구인지 보고 지웠어요.", SUB, 24, rise(3)))
W("iqr", o, "사분위수는 값을 작은 것부터 줄 세운 뒤 4등분한 자리예요. Q1은 아래에서 25%, Q3은 75% 자리의 값이에요. 그 사이, 가운데 절반이 차지한 폭이 IQR이에요. 요금은 Q1이 7.91, Q3이 31이라 IQR은 23.09예요. Q3에서 IQR의 1.5배만큼 더 간 곳에 울타리를 세우고, 그 밖의 값을 튀는 값, 이상치로 봐요. 요금은 65.63 위가 116명이에요. 1.5는 정해진 법칙이 아니라 많이 쓰는 약속이에요. 46에서는 울타리 밖이라고 바로 지우지 않고 누구인지 본 다음 지웠어요." + REAL)

# 8 correlation
o = [sec("corr")] + head(0, "상관계수는 점들이 직선에 얼마나 붙어 있는지예요",
                         [("corr()", TC, TBG), ("r", TC, TBG), ("−1 ~ 1", TC, TBG)], "47")
a = Ax(160, 580, 1600, 10, (-1, 1), (0, 1))
o.append(svg(seg(a.X(-1), 590, a.X(1), 590, "#9AA0AB", 4) + "".join(seg(a.X(t), 580, a.X(t), 600, "#9AA0AB", 4) for t in [-1, -0.5, 0, 0.5, 1])))
for t, s in [(-1, "−1"), (-0.5, "−0.5"), (0, "0"), (0.5, "0.5"), (1, "1")]:
    o.append(label(a.X(t), 612, s, GRAY, 24, anchor="center"))
o.append(label(a.X(-1), 650, "반대로 함께", SUB, 24, anchor="center"))
o.append(label(a.X(0), 650, "직선 관계 없음", SUB, 24, anchor="center"))
o.append(label(a.X(1), 650, "같이 커짐", SUB, 24, anchor="center"))


def thumb(cx_, r, pts, title, color, tid, attrs):
    """A small scatter card centred over r on the ruler, with a leader line down to it."""
    w, h = 400, 230
    x0, y0 = cx_ - w / 2, 290
    xs, ys = [q[0] for q in pts], [q[1] for q in pts]
    mx, Mx, my, My = min(xs), max(xs), min(ys), max(ys)
    dots_ = "".join(f'<circle cx="{x0 + 30 + (q[0] - mx) / ((Mx - mx) or 1) * (w - 60) + ((((k * 7) % 13) - 6) * 2 if Mx - mx < 4 else 0):.1f}" cy="{y0 + h - 30 - (q[1] - my) / ((My - my) or 1) * (h - 60):.1f}" r="7" fill="{color}" fill-opacity="0.6"/>'
                    for k, q in enumerate(pts))
    inner = (f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="16" fill="#FFFFFF" stroke="{LINE}" stroke-width="2"/>' + dots_
             + seg(cx_, y0 + h, cx_, 576, color, 3, "6 6") + f'<circle cx="{cx_}" cy="590" r="12" fill="{color}"/>')
    return [svg(inner, attrs, tid), label(cx_, 240, title, color, 28, attrs, anchor="center")]


o += thumb(a.X(-0.55), -0.55, D["corr_titanic"], "객실 등급과 요금 −0.55", RED, "th1", rise(2))
o += thumb(a.X(0.08), 0.08, D["corr_house"], "집 면적과 가격 0.08", GRAY, "th2", rise(3))
o += thumb(a.X(0.99) - 160, 0.99, [[h_, s_] for h_, s_ in zip(HRS, SCO)], "공부 시간과 점수 0.99", BL, "th3", rise(1))
c3 = C["corr3"]
o.append(code(96, 720, 1000, c3["code"], c3["out"], fs=21, attrs=rise(4))[0])
o.append(note(1150, 720, 680, "−0.55는 등급 숫자가 클수록(3등석) 요금이 낮다는 뜻이에요. 0에 가까우면 한쪽으로 다른 쪽을 짐작하기 어려워요. 원인과 결과까지 알려 주지는 않아요.", SUB, 26, rise(4)))
W("corr", o, "상관계수는 두 열이 직선 모양으로 같이 움직이는 정도를 마이너스 1부터 1 사이 숫자 하나로 나타내요. 1에 가까우면 한쪽이 클 때 다른 쪽도 커요. 공부 시간과 점수가 0.99예요. 마이너스면 반대로 움직여요. 객실 등급은 1등석이 1, 3등석이 3이라 숫자가 클수록 요금이 내려가서 마이너스 0.55예요. 0에 가까우면 직선 관계가 거의 없어요. 47의 미국 집 300채는 면적과 가격이 0.08이었어요. 코드는 df[\"a\"].corr(df[\"b\"])이고, 47에서 처음 썼어요. 상관계수가 높다고 한쪽이 다른 쪽의 원인이라는 뜻은 아니에요. " + REAL + " 작은 그림의 점은 그 데이터에서 일부만 찍었어요.")

# 9 random and seed
o = [sec("seed")] + head(0, "시드를 정하면 난수가 매번 같게 나와요",
                         [("default_rng(42)", TC, TBG), ("normal(평균, 표준편차, 개수)", TC, TBG), ("정규분포", TC, TBG)], "47")
NM = D["normal"]
a = Ax(150, 300, 960, 500, (-10000, 10000), (0, max(NM["counts"]) * 1.1))
nb = ""
for k, cc in enumerate(NM["counts"]):
    x0, x1 = NM["edges"][k], NM["edges"][k + 1]
    inside = -2500 <= x0 and x1 <= 2500
    nb += f'<rect x="{a.X(x0) + 1.5:.1f}" y="{a.Y(cc):.1f}" width="{a.X(x1) - a.X(x0) - 3:.1f}" height="{a.Y(0) - a.Y(cc):.1f}" fill="{"#8FC6CB" if inside else "#C9CED8"}" rx="2"/>'
o.append(svg(axes(a, [-10000, -5000, -2500, 0, 2500, 5000, 10000], [], "만든 값", "", fmt=lambda t: f"{t:,}".replace("-", "−"))))
o.append(svg(nb, WIPE(1)))
o.append(label(a.X(0), a.y - 4, "평균 0", INK, 28, fade(1) + DELAY(300), anchor="center"))
yy_ = a.y + a.h + 100
o.append(svg(seg(a.X(-2500), a.y + a.h + 58, a.X(-2500), yy_, TC, 3, "6 6") + seg(a.X(2500), a.y + a.h + 58, a.X(2500), yy_, TC, 3, "6 6") + arr(a.X(0), yy_, a.X(2500), yy_, TC, 4) + arr(a.X(0), yy_, a.X(-2500), yy_, TC, 4), fade(2)))
o.append(label(a.X(0), yy_ + 14, "표준편차 2500", TC, 26, fade(2), anchor="center"))
o.append(label(a.X(0), yy_ + 52, f"±2500 안에 {NM['in1'] * 100:.0f}%", TC, 26, fade(2), anchor="center"))
cs_ = C["seed"]
html_, bot = code(1180, 300, 650, cs_["code"], cs_["out"], fs=21)
o.append(html_)
o.append(box(3, 1180 + 16, oline(300, 4, 0, 21) - 20, 610, 21 * 1.5 * 2 + 10, TC))
o.append(note(1180, bot + 30, 650, "같은 시드 42면 두 번 다 같은 5개예요. 47에서 연습 데이터의 소음을 이렇게 만들었어요.", SUB, 25, rise(3)))
W("seed", o, "난수는 컴퓨터가 만드는 제멋대로인 숫자예요. 그런데 시작점인 시드를 정하면 몇 번을 돌려도 같은 숫자가 같은 순서로 나와요. 그래서 47에서 np.random.default_rng(42)로 시드를 정했어요. 42는 아무 숫자나 돼요. normal은 정규분포에서 뽑는데, 괄호 안은 평균, 표준편차, 개수 순서예요. 평균 0 근처가 가장 많고 멀어질수록 적어지는 종 모양이 돼요. 표준편차는 퍼진 정도라서, 평균에서 표준편차만큼 안쪽에 약 68%가 들어와요. 왼쪽 그림은 같은 시드로 1만 개를 뽑아 센 거예요. 49의 SGDRegressor에 있는 random_state=42도 같은 시드예요." + REAL + CALC)

# =====================================================================================
# part 2: model and scores (48)
# =====================================================================================
# 10 feature and target
o = [sec("xy")] + head(1, "특성은 모델에 넣는 문제, 타깃은 맞힐 정답이에요", None, "48")
o.append(table(150, 300, [mk("hours", WC, WBG, 1), mk("scores", GR, GRBG, 2)], rows5, [200, 220], fs=34, rh=70))
NAMES = [("문제", "정답"), ("특성 · feature · 피쳐", "타깃 · target"), ("독립변수 · 입력 변수", "종속변수 · 출력"), ("X  (대문자, 표)", "y  (소문자, 한 줄)")]
o.append(label(780, 300, "부르는 이름", GRAY, 24))
for k, (l_, r_) in enumerate(NAMES):
    yk = 350 + k * 84
    o.append(p(f"position:absolute;left:780px;top:{yk}px;width:520px;font-size:32px;font-weight:700;color:{WC};white-space:nowrap", e(l_), fade(1)))
    o.append(p(f"position:absolute;left:1320px;top:{yk}px;width:500px;font-size:32px;font-weight:700;color:{GR};white-space:nowrap", e(r_), fade(2)))
cx_ = C["xy"]
html_, bot = code(780, 720, 760, cx_["code"], cx_["out"], fs=26)
o.append(html_)
o.append(tag(780 + 22 + tw(cx_["out"][0], 26) + 24, oline(720, 3, 0, 26), "두 겹 대괄호라 표, 한 겹이라 한 줄", SUB, rise(3), 24))
W("xy", o, "모델에 넣는 쪽을 특성, 맞혀야 하는 쪽을 타깃이라고 해요. 48에서는 문제와 정답이라고 불렀어요. 수업 노트북 주석의 피쳐, 독립변수, 입력 변수도 모두 특성이고, 종속변수와 출력은 타깃이에요. 코드에서는 특성을 대문자 X, 타깃을 소문자 y에 담아요. X는 대괄호 두 겹으로 꺼내서 열이 하나여도 표 모양이고 shape가 (5, 1)이에요. y는 한 겹이라 한 줄짜리 Series이고 shape가 (5,)예요. 50처럼 특성이 여러 개가 되면 X에 열이 늘어나요." + REAL, ("p2", "모델과 채점"))

# 11 model, fit, predict
o = [sec("model")] + head(1, "모델은 학습(fit)으로 w와 b를 채우고, 예측(predict)으로 답해요",
                          [("LinearRegression()", BL, WBG), ("fit(X, y)", BL, WBG), ("predict(표)", BL, WBG), ("학습 = 훈련", BL, WBG)], "48")
def mbox(x, w_, b_, tid_w, tid_b, attrs="", title="model"):
    return (f'<div{attrs} style="position:absolute;left:{x}px;top:330px;width:400px;height:300px;border-radius:22px;background:#FFFFFF;border:3px solid {BL};display:flex;flex-direction:column;align-items:center;justify-content:center;gap:18px">'
            + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{GRAY}", e(title))
            + p(f"font-family:{MONO};font-size:44px;font-weight:700;color:{WC}", f'w = <span id="{tid_w}">{w_}</span>')
            + p(f"font-family:{MONO};font-size:44px;font-weight:700;color:{BC}", f'b = <span id="{tid_b}">{b_}</span>') + '</div>')
o.append(mbox(110, "?", "?", "mw0", "mb0", title="LinearRegression()"))
o.append(f'<div id="xchip" style="position:absolute;left:600px;top:250px">' + chip('X = df[["hours"]]', WC, WBG, 24) + '</div>')
o.append(f'<div id="ychip" style="position:absolute;left:600px;top:670px">' + chip('y = df["scores"]', GR, GRBG, 24) + '</div>')
o.append(harrow(150, "#C9CED8", "", "position:absolute;left:560px;top:465px"))
o.append(label(635, 410, "fit(X, y)", BL, 32, "", mono=True, anchor="center"))
o.append(f'<div{fly(1, "xchip")} style="position:absolute;left:575px;top:520px">' + chip("X", WC, WBG, 26) + '</div>')
o.append(f'<div{fly(1, "ychip")} style="position:absolute;left:650px;top:520px">' + chip("y", GR, GRBG, 26) + '</div>')
o.append(mbox(760, "10.0", "35.0", "mw1", "mb1", title="model").replace('id="mw1"', 'id="mw1" data-start="?"').replace('id="mb1"', 'id="mb1" data-start="?"'))
o.append(text(2, "mw1", "10.0"))
o.append(text(2, "mb1", "35.0"))
o.append(f'<div{rise(3)} style="position:absolute;left:1210px;top:330px;width:620px;height:300px;display:flex;flex-direction:row;align-items:center;gap:24px">'
         + '<div style="display:flex;flex-direction:column;align-items:center;gap:8px">' + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{BL};white-space:nowrap", "predict") + harrow(130) + p(f"font-size:24px;color:{GRAY};white-space:nowrap", "6시간") + '</div>'
         + p(f"font-family:{MONO};font-size:84px;font-weight:700;color:{INK}", "95.0") + p(f"font-size:30px;color:{SUB};white-space:nowrap", "점") + '</div>')
cf, cp = C["fit"], C["predict"]
h1, b1 = code(110, 740, 820, cf["code"], cf["out"], fs=21)
h2, b2 = code(1010, 740, 820, cp["code"], cp["out"], fs=21)
o += [h1, h2]
W("model", o, "모델은 빈 직선 틀이에요. LinearRegression()으로 막 만든 모델은 w와 b가 아직 비어 있어요. fit에 문제 X와 정답 y를 넣으면 모델이 데이터를 보고 w와 b를 정해요. 이것이 학습, 또는 훈련이에요. 학습이 끝난 모델에 predict로 새 문제를 넣으면 w × 6 + b를 계산해서 95점이라고 답해요. predict에는 학습 때와 같은 열 이름의 표를 넣어요. 48에서는 붕어빵 틀에 비유했어요." + REAL)

# 12 w and b
o = [sec("wb")] + head(1, "기울기 w는 1시간 늘 때 오르는 점수, 절편 b는 0시간의 점수예요",
                       [("coef_", WC, WBG), ("weight", WC, WBG), ("가중치", WC, WBG), ("intercept_", BC, BBG), ("bias", BC, BBG), ("편향", BC, BBG)], "48 · 49")
a = Ax(170, 300, 1000, 560, (0, 6), (0, 100))
o += five_chart(a)
o.append(svg(seg(a.X(2), a.Y(55), a.X(3), a.Y(55), WC, 5, "10 7") + seg(a.X(3), a.Y(55), a.X(3), a.Y(65), WC, 6)))
o.append(label(a.X(2.5), a.Y(55) + 8, "1시간", WC, 26, anchor="center"))
o.append(label(a.X(3) + 14, a.Y(60) - 18, "+10점", WC, 30))
o.append(svg(f'<circle cx="{a.X(0):.1f}" cy="{a.Y(35):.1f}" r="14" fill="{BC}"/>', fade(3)))
o.append(label(a.X(0) + 28, a.Y(35) + 4, "b = 35", BC, 32, fade(3)))
o.append(zoom(1, a.X(1.6), a.Y(72), a.X(3.6) - a.X(1.6), a.Y(50) - a.Y(72)))
o.append(zoom_off(2))
o.append(f'<div style="position:absolute;left:1260px;top:300px;width:570px;display:flex;flex-direction:column;gap:20px">'
         + p(f"font-family:{MONO};font-size:54px;font-weight:700;color:{INK}", f'y = {c("w", WC)}·x + {c("b", BC)}')
         + p(f"font-family:{MONO};font-size:40px;font-weight:700;color:{INK}", f'점수 = {c("10", WC)}×시간 + {c("35", BC)}') + '</div>')
cf = C["fit"]
o.append(code(1260, 560, 570, ["model.coef_[0]", "model.intercept_"], cf["out"], fs=24)[0])
o.append(note(1260, 820, 570, "coef_는 열마다 하나라서 배열이고, [0]으로 첫 칸을 꺼내요.", SUB, 25))
W("wb", o, "직선 y = wx + b의 w가 기울기, b가 절편이에요. 기울기 w는 x가 1 늘 때 y가 얼마나 오르는지예요. 공부 1시간에 10점씩 올라요. 절편 b는 x가 0일 때 y값, 직선이 세로축과 만나는 곳이에요. 공부를 안 해도 35점에서 시작한다는 뜻이에요. scikit-learn은 w를 coef_, b를 intercept_에 담아요. 수업 주석의 Weight와 Bias, 우리말로 가중치와 편향도 같은 두 값이에요. 끝의 밑줄은 fit을 한 뒤에 생기는 값이라는 표시예요. 49에서 손실 그래프의 기울기라는 말이 또 나오는데, 그건 다른 기울기예요. " + pg("two") + "쪽에서 비교해요." + REAL, None)

# 13 prediction and error
o = [sec("error")] + head(1, "오차는 정답 y에서 모델이 찍은 ŷ를 뺀 값이에요",
                          [("y_pred", WC, WBG), ("ŷ 와이 햇", WC, WBG), ("예측값", WC, WBG), ("잔차", EC, EBG), ("residual", EC, EBG)], "48")
a = Ax(170, 300, 1000, 560, (0, 6), (0, 100))
o += five_chart(a)
res = [2, -2, 0, -2, 2]
rl = ""
for hx, sy, r_ in zip(HRS, SCO, res):
    if r_:
        rl += seg(a.X(hx), a.Y(sy), a.X(hx), a.Y(sy - r_), EC, 6, cap="butt")
    rl += f'<circle cx="{a.X(hx):.1f}" cy="{a.Y(sy - r_):.1f}" r="8" fill="#FFFFFF" stroke="{WC}" stroke-width="4"/>'
o.append(svg(rl, fade(1)))
res_lab = ""
for i, (hx, sy, r_) in enumerate(zip(HRS, SCO, res)):
    o.append(label(a.X(hx) + (-16 if r_ > 0 else 18), a.Y(sy) + (-52 if r_ > 0 else 8) if r_ else a.Y(sy) - 56, f"{r_:+d}" if r_ else "0", EC, 28, rise(2), anchor="right" if r_ > 0 else ("center" if not r_ else "left")))
o.append(spot(3, a.X(1) - 40, a.Y(50), 80, a.Y(42) - a.Y(50) + 10))
o.append(spot_off(4))
o.append(f'<div{rise(3)} style="position:absolute;left:{a.X(1) + 70:.0f}px;top:{a.Y(30):.0f}px;display:flex;flex-direction:column;gap:4px">'
         + p(f"font-size:28px;font-weight:700;color:{INK};white-space:nowrap", "y 정답 47") + p(f"font-size:28px;font-weight:700;color:{WC};white-space:nowrap", "ŷ 예측 45")
         + p(f"font-size:28px;font-weight:700;color:{EC};white-space:nowrap", "오차 47 − 45 = 2") + '</div>')
cy_ = C["ypred"]
o.append(code(1225, 300, 605, cy_["code"], cy_["out"], fs=20)[0])
o.append(note(1250, 600, 580, "ŷ는 y 위에 모자(hat)를 씌운 기호예요. 코드에서는 y_pred라고 적어요.", SUB, 26, rise(4)))
o.append(note(1250, 740, 580, "오차를 그대로 더하면 0이 돼요. 그래서 채점은 부호를 없애고 해요.", SUB, 26, rise(4)))
W("error", o, "예측값은 모델이 직선 위에 찍은 값이에요. 수식에서는 y 위에 모자를 씌운 ŷ, 와이 햇이라고 쓰고, 코드에서는 y_pred에 담아요. 오차는 정답에서 예측을 뺀 값이에요. 1시간 학생은 정답이 47이고 예측이 45라서 오차가 2예요. 점이 직선보다 위에 있으면 플러스, 아래면 마이너스예요. 학습한 데이터에 대한 오차를 잔차라고도 해요. 다섯 오차를 그대로 더하면 플러스와 마이너스가 지워져서 0이 돼요. 그래서 다음 쪽의 MAE와 MSE는 부호를 없애고 더해요." + REAL)

# 14 MAE
o = [sec("mae")] + head(1, "MAE는 오차의 크기만 모아 평균 낸 값이에요",
                        [("mean_absolute_error", PUR, BBG), ("평균 절대 오차", PUR, BBG)], "48")
def ebar(x0, base, vals, color, attrs, absolute=False, unit=44):
    s = ""
    for k, v in enumerate(vals):
        vv = abs(v) if absolute else v
        x = x0 + k * 150
        hgt = vv * unit
        y0_ = base - hgt if vv >= 0 else base
        if vv:
            s += f'<rect x="{x}" y="{y0_:.1f}" width="90" height="{abs(hgt):.1f}" fill="{color}" rx="6"/>'
        s += stext(x + 45, (y0_ - 14) if vv >= 0 else (base + abs(hgt) + 34), (f"{vv:+d}" if not absolute else str(vv)) if vv else "0", color, 30, weight=700)
    s += seg(x0 - 20, base, x0 + 5 * 150 - 40, base, "#9AA0AB", 3)
    return svg(s, attrs)
o.append(label(150, 290, "오차 그대로", GRAY, 28, rise(1) + DIM("mae")))
o.append(ebar(160, 480, res, EC, rise(1) + DIM("mae")))
o.append(label(1000, 440, "더하면 0", EC, 40, rise(1) + DIM("mae")))
o.append(label(150, 640, "크기만 (절댓값)", GRAY, 28, rise(2) + DIM("mae")))
o.append(ebar(160, 880, res, PUR, rise(2) + DIM("mae"), absolute=True))
o.append(f'<div{rise(3)} style="position:absolute;left:1000px;top:740px;display:flex;flex-direction:row;align-items:baseline;gap:20px">'
         + p(f"font-size:40px;font-weight:700;color:{SUB};white-space:nowrap", "합 8 ÷ 5명 =")
         + p(f"font-family:{MONO};font-size:96px;font-weight:700;color:{PUR}", "1.6") + p(f"font-size:34px;font-weight:700;color:{SUB}", "점") + '</div>')
o.append(code(1000, 300, 830, ['mean_absolute_error(y, y_pred)'], ["1.6"], fs=26)[0])
W("mae", o, "MAE는 Mean Absolute Error, 평균 절대 오차예요. 오차를 그대로 더하면 0이 되니까 마이너스를 떼고 크기만 봐요. 그것이 절댓값이에요. 2, 2, 0, 2, 2를 더하면 8이고 5명으로 나누면 1.6이에요. 이 모델은 평균 1.6점쯤 빗나간다고 읽어요. 단위가 점수와 같아서 사람이 읽기 가장 쉬운 점수예요. 함수에는 정답 y를 먼저, 예측을 나중에 넣어요." + REAL)

# 15 MSE and RMSE
o = [sec("mse")] + head(1, "MSE는 오차를 제곱해 평균 낸 값, RMSE는 그 제곱근이에요",
                        [("mean_squared_error", PUR, BBG), ("평균 제곱 오차", PUR, BBG), ("root", PUR, BBG)], "48 · 49")
SQ = 46
sqs = ""
for k, v in enumerate(res):
    x = 170 + k * 230
    n_ = abs(v)
    for i in range(n_):
        for j in range(n_):
            sqs += f'<rect x="{x + i * SQ}" y="{560 - (j + 1) * SQ}" width="{SQ - 4}" height="{SQ - 4}" fill="{EC}" fill-opacity="0.75" rx="4"/>'
    sqs += stext(x + 45, 610, f"{v:+d}" if v else "0", EC, 28, weight=700)
    sqs += stext(x + 45, 650, f"{n_}² = {n_ * n_}", SUB, 26, weight=700)
o.append(f'<div{STAGGER(1, 120)} style="position:absolute;left:0;top:0;width:1920px;height:1080px">' + svg(sqs) + '</div>')
o.append(f'<div{rise(2)} style="position:absolute;left:170px;top:720px;display:flex;flex-direction:row;align-items:baseline;gap:18px">'
         + p(f"font-size:38px;font-weight:700;color:{SUB};white-space:nowrap", "합 16 ÷ 5명 = MSE")
         + p(f"font-family:{MONO};font-size:80px;font-weight:700;color:{PUR}", "3.2") + p(f"font-size:30px;color:{SUB};white-space:nowrap", "(점수²)") + '</div>')
o.append(f'<div id="rmse" {rise(3)[1:]} style="position:absolute;left:170px;top:850px;display:flex;flex-direction:row;align-items:baseline;gap:18px">'
         + p(f"font-size:38px;font-weight:700;color:{SUB};white-space:nowrap", "√3.2 = RMSE")
         + p(f"font-family:{MONO};font-size:80px;font-weight:700;color:{PUR}", "1.79") + p(f"font-size:30px;color:{SUB};white-space:nowrap", "(점수)") + '</div>')
o.append(grow(4, "rmse"))
cm = C["metrics"]
o.append(code(170, 270, 1000, cm["code"][1:3], cm["out"][1:3], fs=20)[0])
o.append(note(1300, 470, 530, "오차가 2배면 벌점은 4배예요. 큰 실수를 크게 혼내요.", SUB, 28, rise(2)))
o.append(note(1300, 700, 530, "제곱해서 단위가 점수²가 됐으니, 제곱근으로 점수 단위로 되돌린 것이 RMSE예요.", SUB, 28, rise(3)))
W("mse", o, "MSE는 Mean Squared Error, 평균 제곱 오차예요. 오차를 제곱하면 마이너스가 사라지고, 큰 오차는 훨씬 커져요. 오차 2는 정사각형 4칸, 오차 4라면 16칸이에요. 2배 틀리면 벌점이 4배라서 큰 실수를 크게 혼내요. 다섯 칸 수를 더하면 16, 5명으로 나누면 3.2예요. 다만 제곱했으니 단위가 점수의 제곱이라 3.2점 틀렸다고 읽으면 안 돼요. 제곱근을 씌워 점수 단위로 되돌린 것이 RMSE, 1.79점이에요. 49에서는 이 MSE를 손실로 써요." + REAL)

# 16 R2
o = [sec("r2")] + head(1, "R²는 평균만 찍을 때보다 오차를 얼마나 줄였는지예요",
                       [("r2_score", PUR, BBG), ("결정계수", PUR, BBG), ("R 제곱", PUR, BBG)], "48")
for k, (title_, line_, mse_, col, tid_) in enumerate([("평균만 찍기", 65, "203.2", GRAY, "r2a"), ("직선", None, "3.2", WC, "r2b")]):
    a = Ax(170 + k * 620, 300, 470, 300, (0, 6), (20, 100))
    inner = axes(a, [1, 3, 5], [20, 60, 100])
    rr = ""
    for hx, sy in zip(HRS, SCO):
        pv = line_ if line_ else 10 * hx + 35
        rr += seg(a.X(hx), a.Y(sy), a.X(hx), a.Y(pv), EC, 5, cap="butt")
    inner += poly(a, [(0, line_), (6, line_)] if line_ else [(0, 35), (6, 95)], col, 6) + rr + "".join(dot(a, hx, sy, INK, 10) for hx, sy in zip(HRS, SCO))
    o.append(f'<div id="{tid_}" style="position:absolute;left:{120 + k * 620}px;top:240px;width:580px;height:530px;border-radius:20px;background:#FFFFFF;border:2px solid {LINE}"></div>')
    o.append(svg(inner))
    o.append(label(a.x + a.w / 2, 664, title_, col, 32, anchor="center"))
    o.append(label(a.x + a.w / 2, 710, f"MSE {mse_}", EC, 30, mono=True, anchor="center"))
o.append(blur(1, "r2a"))
o.append(blur(2, "r2b"))
o.append(blur_off(3))
cr = C["r2base"]
o.append(code(120, 800, 1200, cr["code"], cr["out"], fs=21, attrs=rise(5))[0])
o.append(f'<div{rise(3)} style="position:absolute;left:1390px;top:300px;width:440px;display:flex;flex-direction:column;gap:14px">'
         + p(f"font-size:32px;font-weight:700;color:{SUB};white-space:nowrap", "1 − 3.2 ÷ 203.2")
         + p(f"font-family:{MONO};font-size:110px;font-weight:700;line-height:1.2;color:{PUR}", "0.98") + '</div>')
for k, (v, t_) in enumerate([("1", "다 맞힘"), ("0", "평균만큼"), ("음수", "평균보다 못함")]):
    o.append(p(f"position:absolute;left:1390px;top:{560 + k * 70}px;font-size:28px;font-weight:700;color:{INK};white-space:nowrap", f'<span style="font-family:{MONO};color:{PUR};display:inline-block;width:80px">{v}</span>{t_}', rise(4)))
W("r2", o, "R²는 결정계수, R 제곱이라고 읽어요. 아무 공부도 안 한 모델이 평균 65점만 찍으면 MSE가 203.2예요. 우리 직선은 3.2예요. 오차를 얼마나 줄였는지를 1 − 3.2 ÷ 203.2로 계산하면 0.98이에요. 1이면 다 맞힌 것이고, 0이면 평균만 찍은 것과 같아요. 평균보다 못하면 마이너스도 나와요. 그래서 R²가 0부터 1까지라는 말은 반만 맞아요. 마이너스 예는 뒤의 오해 쪽에서 실제로 보여 줘요. r2_score(y, y_pred)로 계산하고 48에서 다뤘어요." + REAL)

# =====================================================================================
# part 3: gradient descent (49)
# =====================================================================================
# 17 loss function
o = [sec("loss")] + head(2, "손실 함수는 w와 b를 넣으면 빗나간 정도를 숫자 하나로 돌려줘요",
                         [("loss", EC, EBG), ("손실", EC, EBG), ("비용 cost", EC, EBG), ('loss="squared_error"', EC, EBG)], "49")
o.append(f'<div style="position:absolute;left:640px;top:320px;width:620px;height:300px;border-radius:26px;background:{DARK};display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px">'
         + p("font-size:40px;font-weight:700;color:#FFFFFF", "손실 함수") + p(f"font-family:{MONO};font-size:30px;color:#C9CED8", "5명의 오차 → MSE") + '</div>')
o.append(svg(f'<path id="lpath" d="M 230 470 L 640 470" fill="none" stroke="#C9CED8" stroke-width="4"/>' + arr(1260, 470, 1400, 470, "#C9CED8", 4)))
ROWS = [("w = 8, b = 35", "47.2", 1), ("w = 10, b = 35", "3.2", 2), ("w = 12, b = 35", "47.2", 3)]
for k, (inp, outv, ordr) in enumerate(ROWS):
    o.append(p(f"position:absolute;left:96px;top:{720 + k * 76}px;font-family:{MONO};font-size:34px;font-weight:700;color:{INK};white-space:nowrap",
               f'w = {c(inp.split(",")[0][4:], WC)}, b = {c("35", BC)}', rise(ordr)))
    o.append(p(f"position:absolute;left:1420px;top:{720 + k * 76}px;font-family:{MONO};font-size:34px;font-weight:700;color:{EC};white-space:nowrap", f"손실 {outv}", rise(ordr)))
o.append(f'<div{PATH(1, "lpath")} style="position:absolute;left:640px;top:440px;transform:translate(-100%,0)">' + chip("w, b", WC, WBG, 32) + '</div>')
o.append(p(f"position:absolute;left:1420px;top:420px;font-family:{MONO};font-size:84px;font-weight:700;color:{EC}", "3.2", rise(2)))
o.append(note(96, 660, 1300, "w와 b가 다르면 손실도 달라요. 학습은 손실이 가장 작은 w와 b를 찾는 일이에요.", SUB, 28, rise(3)))
W("loss", o, "손실은 모델이 정답에서 얼마나 빗나갔는지를 숫자 하나로 나타낸 값이에요. 손실 함수는 그 숫자를 내는 규칙이고요. 회귀에서는 앞 쪽의 MSE를 손실 함수로 많이 써요. SGDRegressor의 loss=\"squared_error\"가 제곱 오차, 곧 MSE라는 뜻이에요. 같은 5명 데이터라도 직선의 w와 b가 바뀌면 손실이 달라져요. w가 8이면 47.2, 10이면 3.2, 12면 다시 47.2예요. 그래서 학습이란 손실이 가장 작아지는 w와 b를 찾는 일이에요. 비용 함수라는 말도 같은 뜻으로 써요." + REAL, ("p3", "경사 하강법"))

# 18 formula symbols
o = [sec("formula")] + head(2, "MSE 수식은 오른쪽 표를 줄여 쓴 거예요", [("Σ 시그마", EC, EBG), ("n", EC, EBG), ("i", EC, EBG), ("ŷ", WC, WBG)], "48 · 49")
F = (f'<span style="color:{INK}">MSE = </span>' + mk("1/n", PUR, BBG, 5) + " " + mk("Σ", OR, GBG, 4) + " ( " + mk("y<sub>i</sub>", GR, GRBG, 2) + " − "
     + mk("ŷ<sub>i</sub>", WC, WBG, 2) + " )" + mk("²", EC, EBG, 3))
o.append(p(f"position:absolute;left:96px;top:270px;font-family:{MONO};font-size:76px;font-weight:700;color:{INK};white-space:nowrap", F))
FT = [("i", "y", "ŷ", "y − ŷ", "²")] + [(str(i + 1), str(SCO[i]), str(10 * HRS[i] + 35), f"{res[i]:+d}" if res[i] else "0", str(res[i] ** 2)) for i in range(5)]
cols_ = [(mk("i", INK, "#EEF0F3", 1), 110), (mk("y", GR, GRBG, 2), 150), (mk("ŷ", WC, WBG, 2), 150), ("y − ŷ", 190), (mk("²", EC, EBG, 3), 150)]
x0 = 1070
o.append(f'<div style="position:absolute;left:{x0}px;top:420px;display:flex;flex-direction:row;height:56px;border-bottom:3px solid {INK}">' + "".join(p(f"width:{w}px;font-family:{MONO};font-size:32px;font-weight:700;text-align:right;padding-right:16px", h) for h, w in cols_) + '</div>')
for r in range(5):
    o.append(f'<div style="position:absolute;left:{x0}px;top:{480 + r * 58}px;display:flex;flex-direction:row;height:58px;border-bottom:2px solid {LINE}">'
             + "".join(p(f"width:{w}px;font-family:{MONO};font-size:30px;text-align:right;padding-right:16px;line-height:58px;color:{INK}", v) for v, (_, w) in zip(FT[r + 1], cols_)) + '</div>')
o.append(p(f"position:absolute;left:{x0}px;top:780px;width:750px;font-family:{MONO};font-size:32px;font-weight:700;text-align:right;padding-right:16px;color:{OR}", f'Σ 다 더하면 16', rise(4)))
o.append(p(f"position:absolute;left:{x0}px;top:840px;width:750px;font-family:{MONO};font-size:32px;font-weight:700;text-align:right;padding-right:16px;color:{PUR}", f'÷ n(5명) = 3.2', rise(5)))
EXPL = [("i", "몇 번째 학생인지 (1~5)", INK, 1), ("yᵢ, ŷᵢ", "i번 학생의 정답과 예측", GR, 2), ("( )²", "빼서 제곱", EC, 3), ("Σ", "i를 1부터 n까지 다 더하기", OR, 4), ("1/n", "사람 수 n으로 나누기", PUR, 5)]
for k, (s_, t_, col, ordr) in enumerate(EXPL):
    o.append(p(f"position:absolute;left:96px;top:{430 + k * 92}px;font-size:32px;font-weight:700;color:{INK};white-space:nowrap",
               f'<span style="font-family:{MONO};color:{col};display:inline-block;width:150px">{s_}</span>{e(t_)}', rise(ordr)))
W("formula", o, "수업 노트북의 MSE 그림에 나온 기호는 오른쪽 표를 짧게 쓴 거예요. i는 몇 번째 학생인지, n은 학생 수 5예요. y 아래의 작은 i는 i번 학생의 정답이라는 뜻이고, ŷ는 그 학생의 예측이에요. 괄호 안에서 정답에서 예측을 빼고, 위의 2로 제곱해요. 큰 시그마 Σ는 1번부터 n번까지 다 더하라는 기호예요. 마지막으로 1/n, n으로 나눠요. 그러니 수식 한 줄은 표를 만들어 마지막 칸을 더하고 사람 수로 나누라는 말이에요. 수식을 외울 필요는 없고, 기호가 표의 어느 칸인지만 알면 돼요.", None)

# 19 parabola
o = [sec("parab")] + head(2, "w를 바꿔 가며 잰 손실은 U자, 2차함수 모양이에요",
                          [("2차함수", EC, EBG), ("포물선", EC, EBG), ("x²", EC, EBG)], "49")
cu = C["ucurve"]
html_, bot = code(96, 260, 740, cu["code"], cu["out"], fs=21)
o.append(html_)
a = Ax(900, 290, 880, 560, (6.5, 13.5), (0, 80))
o += u_chart(a, curve_attrs=WIPE(2))
dts = "".join(dot(a, w, mse(w), INK, 13) for w in [8, 9, 10, 11, 12])
o.append(f'<div{STAGGER(1, 120)} style="position:absolute;left:0;top:0;width:1920px;height:1080px">' + "".join(svg(dot(a, w, mse(w), INK, 13)) for w in [8, 9, 10, 11, 12]) + '</div>')
o.append(label(a.X(10), a.Y(31), "가장 낮은 곳 w = 10", INK, 28, fade(2) + DELAY(400), anchor="center"))
o.append(svg(arr(a.X(10), a.Y(25), a.X(10), a.Y(6.5), INK, 3), fade(2) + DELAY(400)))
o.append(label(a.X(11) + 20, a.Y(14.2) + 6, "1칸 떨어지면 +11", EC, 26, fade(3)))
o.append(label(a.X(12) + 20, a.Y(47.2) + 6, "2칸이면 +44", EC, 26, fade(3)))
o.append(note(96, bot + 40, 740, "멀어진 거리의 제곱만큼 커져요. 1² × 11, 2² × 11. 그래서 2차함수예요.", SUB, 28, rise(3)))
W("parab", o, "b를 35로 고정하고 w만 8부터 12까지 바꿔서 MSE를 재면 47.2, 14.2, 3.2, 14.2, 47.2가 나와요. 점을 찍으면 가운데가 가장 낮고 양쪽이 올라가는 U자예요. 이런 모양을 포물선, 식으로는 2차함수라고 해요. w가 10에서 1칸 멀어지면 손실이 11 늘고, 2칸 멀어지면 44 늘어요. 거리 1의 제곱은 1, 거리 2의 제곱은 4라서 4배예요. MSE가 오차를 제곱하니까 손실 그래프가 U자가 되는 거예요. U자의 가장 낮은 곳이 우리가 찾는 w예요." + REAL)

# 20 two meanings
o = [sec("two")] + head(2, "기울기는 두 개예요: 직선의 기울기 w와 손실의 기울기",
                        [("w = coef_", WC, WBG), ("경사 = 미분값", GC, GBG), ("gradient", GC, GBG)], "48 · 49")
o.append(f'<div id="tw-l" style="position:absolute;left:96px;top:250px;width:840px;height:600px;border-radius:20px;background:#FFFFFF;border:3px solid {WC}"></div>')
o.append(f'<div id="tw-r" style="position:absolute;left:984px;top:250px;width:840px;height:600px;border-radius:20px;background:#FFFFFF;border:3px solid {GC}"></div>')
a = Ax(200, 330, 640, 380, (0, 6), (0, 100))
o.append(svg(axes(a, [0, 2, 4, 6], [0, 50, 100], "공부 시간", "점수") + poly(a, [(0, 35), (6, 95)], WC, 6)
             + "".join(dot(a, hx, sy, INK, 9) for hx, sy in zip(HRS, SCO)) + seg(a.X(2), a.Y(55), a.X(3), a.Y(55), WC, 4, "8 6") + seg(a.X(3), a.Y(55), a.X(3), a.Y(65), WC, 5)))
o.append(label(a.X(3) + 12, a.Y(60) - 18, "+10", WC, 28))
a2 = Ax(1090, 330, 640, 380, (6.5, 13.5), (0, 80))
o.append(svg(axes(a2, [8, 10, 12], [0, 40, 80], "w", "손실 MSE") + poly(a2, [(w, m) for w, m in U if m <= 80], EC, 6)))
o.append(tangent(a2, 8, 1.0))
o.append(svg(dot(a2, 8, 47.2, GC, 12)))
o.append(label(a2.X(8) + 30, a2.Y(47.2) - 30, "−44", GC, 30))
o.append(label(140, 780, "직선의 기울기 w = 10", WC, 34))
o.append(label(1028, 780, "손실의 기울기(경사) = −44", GC, 34))
o.append(spot(1, 96, 250, 840, 600, pad=6))
o.append(spot(2, 984, 250, 840, 600, pad=6))
o.append(spot_off(3))
TWO = [("어느 그래프?", "데이터: 공부 시간과 점수", "손실: w와 MSE"), ("뜻", "1시간에 오르는 점수", "w를 늘리면 손실이 변하는 양"), ("누가 쓰나?", "모델이 배워서 갖는 값", "w를 고칠 방향을 정하는 값")]
for k, (h_, l_, r_) in enumerate(TWO):
    yk = 880 + k * 46
    o.append(p(f"position:absolute;left:96px;top:{yk}px;width:1728px;font-size:26px;color:{INK};white-space:nowrap",
               f'<span style="display:inline-block;width:170px;color:{GRAY};font-weight:700">{e(h_)}</span><span style="display:inline-block;width:718px;color:{WC};font-weight:700">{e(l_)}</span><span style="color:{GC};font-weight:700">{e(r_)}</span>', rise(3)))
W("two", o, "수업에서 가장 많이 헷갈린 말이에요. 기울기가 두 개 나와요. 왼쪽은 48의 직선의 기울기 w예요. 데이터 그래프에서 공부 1시간에 점수가 10점 오른다는 뜻이고, 모델이 학습해서 갖는 값이에요. 오른쪽은 49의 손실 그래프의 기울기예요. 가로축이 w이고 세로축이 손실이에요. w가 8인 곳에서 기울기가 마이너스 44라는 건, w를 조금 늘리면 손실이 그 비율로 줄어든다는 뜻이에요. 경사 하강법의 경사, 미분값, gradient가 모두 이쪽이에요. 이 사전은 직선 쪽을 파랑 w, 손실 쪽을 주황 경사로 칠했어요. 어느 기울기인지 헷갈리면 가로축이 무엇인지 보면 돼요.", None)

# 21 derivative
o = [sec("deriv")] + head(2, "미분은 한 점에서의 기울기예요: 아주 조금 움직였을 때 변하는 비율",
                          [("미분값", GC, GBG), ("접선의 기울기", GC, GBG), ("경사", GC, GBG), ("gradient", GC, GBG)], "49")
a = Ax(170, 300, 1000, 560, (6.5, 13.5), (0, 80))
o += u_chart(a)
for k, (w0, g, ordr) in enumerate([(8, -44, 1), (10, 0, 2), (12, 44, 3)]):
    o.append(f'<div{rise(ordr)}{DIM("tan")} style="position:absolute;left:0;top:0;width:1920px;height:1080px">' + tangent(a, w0, 0.7) + svg(dot(a, w0, mse(w0), GC, 13))
             + label(a.X(w0) + (-30 if w0 == 8 else 30), a.Y(mse(w0)) - (70 if w0 != 10 else 64), f"{g:+d}" if g else "0", GC, 34, anchor="right" if w0 == 8 else ("center" if w0 == 10 else "left")) + '</div>')
cs2 = C["slope"]
html_, bot = code(1200, 290, 630, cs2["code"], cs2["out"], fs=19)
o.append(html_)
SG = [("−", "오른쪽이 내리막", "w를 키워요"), ("0", "바닥", "멈춰요"), ("+", "오른쪽이 오르막", "w를 줄여요")]
for k, (s_, t_, d_) in enumerate(SG):
    o.append(p(f"position:absolute;left:1200px;top:{bot + 36 + k * 60}px;font-size:28px;font-weight:700;color:{INK};white-space:nowrap",
               f'<span style="font-family:{MONO};color:{GC};display:inline-block;width:46px">{s_}</span>{e(t_)} <span style="color:{GRAY}">→ {e(d_)}</span>', rise(k + 1)))
W("deriv", o, "미분은 그래프의 한 점에서 기울기를 구하는 계산이에요. 그 점에 살짝 닿는 직선, 접선의 기울기라고도 해요. 공식 대신 직접 재 볼게요. w를 8에서 8.001로 아주 조금 늘리면 MSE가 0.044 줄어요. 변화를 움직인 양 0.001로 나누면 마이너스 44예요. 이것이 w가 8인 곳의 미분값이에요. 마이너스면 오른쪽이 내리막이니 w를 키워야 손실이 줄고, 플러스면 오르막이니 w를 줄여요. 바닥인 10에서는 0이라 더 갈 곳이 없어요. 49에서는 이 값을 경사라고 불러요." + REAL)

# 22 gradient descent
o = [sec("gd")] + head(2, "경사 하강법은 경사를 보고 내리막으로 한 걸음씩 가는 방법이에요",
                       [("gradient descent", GC, GBG), ("경사하강법", GC, GBG), ("GD", GC, GBG)], "49")
a = Ax(170, 300, 1000, 560, (6.5, 13.5), (0, 80))
o += u_chart(a)
P02 = D["gd"]["0.02"]
ppts = [(q[0], q[1]) for q in P02[:6]]
dpath = "M " + " L ".join(f"{a.X(w):.1f} {a.Y(m):.1f}" for w, m in ppts)
o.append(svg(f'<path id="gdpath" d="{dpath}" fill="none" stroke="{GC}" stroke-width="4" stroke-dasharray="8 8"/>' + "".join(dot(a, w, m, GC, 8) for w, m in ppts[:-1])))
o.append(f'<div{PATH(1, "gdpath", 2200)} style="position:absolute;left:{a.X(ppts[-1][0]) - 16:.1f}px;top:{a.Y(ppts[-1][1]) - 16:.1f}px;width:32px;height:32px;border-radius:50%;background:{INK}"></div>')
for k, (w, m) in enumerate(ppts[:3]):
    o.append(label(a.X(w) - 26, a.Y(m) - 14, f"{w:.2f}", GC, 24, fade(1) + DELAY(300 * k), mono=True, anchor="right"))
o.append(strip(1250, 300, 580, 110, mono_line([("새 w = w − ", "#E6E9EF"), ("학습률", "#9EC5FF"), (" × ", "#E6E9EF"), ("경사", "#F2B27A")], 30)))
STEP = [("1걸음", f"8 − 0.02 × (−44) = {P02[1][0]:.2f}"), ("2걸음", f"{P02[1][0]:.2f} − 0.02 × ({P02[1][2]:.2f}) = {P02[2][0]:.2f}")]
for k, (s_, t_) in enumerate(STEP):
    o.append(p(f"position:absolute;left:1250px;top:{450 + k * 64}px;font-size:26px;font-weight:700;color:{INK};white-space:nowrap",
               f'<span style="color:{GRAY};display:inline-block;width:90px">{s_}</span><span style="font-family:{MONO}">{e(t_)}</span>', rise(2)))
o.append(note(1250, 600, 580, "경사가 마이너스면 빼기가 더하기가 돼서 w가 커져요. 바닥에 가까울수록 경사가 작아져 걸음도 작아져요.", SUB, 26, rise(3)))
W("gd", o, "경사 하강법은 눈을 감고 산을 내려가는 방법이에요. 발밑의 경사만 느끼고 낮은 쪽으로 한 걸음 가고, 다시 경사를 느끼고 또 한 걸음 가요. 걸음 규칙은 한 줄이에요. 새 w는 지금 w에서 학습률 곱하기 경사를 빼요. w가 8이면 경사가 마이너스 44라서 0.02 × −44를 빼면 8.88로 커져요. 바닥에 가까워질수록 경사가 작아지니 걸음도 저절로 작아져요. 그림은 b를 35로 고정하고 w만 움직인 계산이에요. 49의 SGDRegressor는 w와 b를 같이 이렇게 고쳐요." + CALC)

# 23 learning rate
o = [sec("lr")] + head(2, "학습률은 한 걸음의 크기예요: 너무 작으면 느리고, 너무 크면 튀어요",
                       [("eta0", GC, GBG), ("learning rate", GC, GBG), ("η 에타", GC, GBG), ("보폭", GC, GBG)], "49")
LR = [("0.004", "너무 작으면", "8걸음에 8.95까지", "lr1"), ("0.02", "알맞으면", "6걸음에 9.80", "lr2"), ("0.1", "너무 크면", "튀어 나가요", "lr3")]
for k, (eta, t_, s_, tid_) in enumerate(LR):
    x = 96 + k * 584
    o.append(f'<div id="{tid_}" style="position:absolute;left:{x}px;top:250px;width:560px;height:540px;border-radius:20px;background:#FFFFFF;border:2px solid {LINE}"></div>')
    a = Ax(x + 50, 330, 470, 330, (3.5, 16.5) if eta == "0.1" else (6.5, 13.5), (0, 150 if eta == "0.1" else 60))
    pts = [(w, m) for w, m in U if m <= a.yr[1]] if eta != "0.1" else [(w / 100, mse(w / 100)) for w in range(350, 1651, 5) if mse(w / 100) <= 150]
    path = [(q[0], q[1]) for q in D["gd"][eta]][: (8 if eta == "0.004" else 6 if eta == "0.02" else 4)]
    inner = seg(a.x, a.y + a.h, a.x + a.w, a.y + a.h, "#9AA0AB", 3) + poly(a, pts, EC, 5) + poly(a, path, GC, 3) + "".join(dot(a, w, m, GC, 7) for w, m in path) + dot(a, path[0][0], path[0][1], INK, 9)
    o.append(svg(inner, rise(k + 1)))
    o.append(label(x + 280, 280, f"eta0 = {eta}", GC, 30, rise(k + 1), mono=True, anchor="center"))
    o.append(label(x + 280, 690, t_, INK, 30, rise(k + 1), anchor="center"))
    o.append(label(x + 280, 740, s_, GRAY, 24, rise(k + 1), anchor="center"))
o.append(shake(4, "lr3"))
ce = C["eta"]
o.append(code(96, 822, 1000, ce["code"][:3] + ["    ...  # 1000번 학습한 뒤 MSE"], None, fs=20)[0])
o.append(f'<div{rise(4)} style="position:absolute;left:1140px;top:818px;width:690px">' + "".join(
    p(f"font-family:{MONO};font-size:26px;line-height:1.55;white-space:pre;color:{RED if k == 2 else INK}", e(l)) for k, l in enumerate(ce["out"])) + '</div>')
W("lr", o, "학습률은 경사에 곱하는 수, 곧 한 걸음의 크기예요. SGDRegressor에서는 eta0이라고 적고, 그리스 글자 에타에서 온 이름이에요. 너무 작으면 바닥 쪽으로 가긴 하는데 한참 걸려요. 알맞으면 몇 걸음 만에 바닥 근처에 가요. 너무 크면 바닥을 지나쳐 반대편 더 높은 곳에 떨어지고, 점점 더 멀리 튀어 나가요. 위 세 그림은 w만 움직인 계산이고, 아래는 실제 SGDRegressor를 1000번 학습시킨 MSE예요. 0.001은 33으로 아직 멀고, 0.01은 3.25, 0.3은 10의 24제곱으로 터졌어요. 수업에서 0.01을 쓴 이유예요. learning_rate=\"constant\"는 학습률을 끝까지 바꾸지 않는다는 뜻이에요." + REAL + CALC)

# 24 epoch
o = [sec("epoch")] + head(2, "epoch는 데이터 전체를 한 바퀴 다 보는 거예요",
                          [("에포크", GC, GBG), ("partial_fit", GC, GBG), ("반복 횟수", GC, GBG)], "49")
cl = C["loop"]
LP = cl["code"][:3]
html_, bot = code(96, 260, 800, LP, None, fs=30)
o.append(html_)
o.append(run(1, 96 + 4, cline(260, 1, 30) - 23, 792, 46))
o.append(run(2, 96 + 4, cline(260, 2, 30) - 23, 792, 46))
o.append(run(3, 96 + 4, cline(260, 1, 30) - 23, 792, 46))
o.append(run(4, 96 + 4, cline(260, 2, 30) - 23, 792, 46))
o.append(run_off(5))
for k in range(5):
    x = 1000 + k * 160
    o.append(f'<div style="position:absolute;left:{x}px;top:300px;width:130px;height:150px;border-radius:16px;background:#FFFFFF;border:3px solid {LINE};display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px">'
             + p(f"font-size:24px;color:{GRAY}", f"{k + 1}번") + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{INK}", f"{HRS[k]}h·{SCO[k]}") + '</div>')
o.append(svg(f'<path d="M 1010 480 C 1100 560, 1640 560, 1740 480" fill="none" stroke="{GC}" stroke-width="5"/>' + arrowhead(1740, 480, -0.7, GC, 20)))
o.append(p(f"position:absolute;left:1180px;top:560px;font-size:34px;font-weight:700;color:{GC};white-space:nowrap", f'5명을 다 보면 epoch <span id="ep" data-start="1">2</span>'))
o.append(text(3, "ep", "2"))
o.append(note(96, bot + 40, 800, "partial_fit 한 번이 한 바퀴예요. for로 1000번 돌리면 1000 epoch예요.", SUB, 30, rise(5)))
EPC = [("1 epoch", "5명을 한 번씩 봐요", "5번"), ("10 epoch", "5명을 10바퀴", "50번"), ("1000 epoch", "5명을 1000바퀴", "5,000번")]
for k, (t_, d_, n_) in enumerate(EPC):
    x = 96 + k * 584
    o.append(f'<div{rise(6 + k)} style="position:absolute;left:{x}px;top:800px;width:560px;height:180px;border-radius:18px;background:#FFFFFF;border:2px solid {LINE};padding:24px 30px;display:flex;flex-direction:column;gap:10px">'
             + p(f"font-family:{MONO};font-size:36px;font-weight:700;color:{GC}", t_)
             + p(f"font-size:28px;color:{INK};white-space:nowrap", f'{d_} <span style="color:{GRAY}">· 학생을 본 횟수 {n_}</span>') + '</div>')
o.append(note(1000, 660, 820, "수업 코드의 max_iter=1000은 fit()이 쓰는 값이라 partial_fit 반복에는 쓰이지 않아요. 바퀴 수는 for의 range(1000)이 정해요.", SUB, 26, rise(5)))
W("epoch", o, "epoch, 에포크는 학습 데이터 전체를 처음부터 끝까지 한 번 보는 것을 말해요. 5명 데이터라면 5명을 한 번씩 다 보면 1 epoch예요. 49의 수업 코드는 partial_fit을 한 번 부를 때마다 5명을 한 바퀴 돌며 w와 b를 고쳐요. 그걸 for로 1000번 돌렸으니 1000 epoch를 학습한 거예요. SGDRegressor를 만들 때 적은 max_iter=1000은 fit()을 쓸 때 몇 바퀴 돌지 정하는 값이라서 수업처럼 partial_fit을 직접 돌리면 쓰이지 않아요. 바퀴 수는 for의 range가 정해요." + REAL)

# 25 batch vs stochastic
o = [sec("sgd")] + head(2, "배치는 다 보고 한 걸음, 확률적은 한 명 보고 한 걸음이에요",
                        [("BGD", GC, GBG), ("SGD", GC, GBG), ("Stochastic", GC, GBG), ("SGDRegressor", GC, GBG)], "49")
PS = D["per_student"]
o.append(label(96, 260, "w = 8에서 학생마다 잰 경사", GRAY, 26))
scale = 4.2
for k, g in enumerate(PS):
    y = 320 + k * 78
    o.append(p(f"position:absolute;left:96px;top:{y}px;width:120px;font-size:28px;font-weight:700;color:{INK};white-space:nowrap", f"{k + 1}번"))
    o.append(bar(240, y + 6, -g * scale, 40, GC, rise(1) + DELAY(90 * k)))
    o.append(label(240 - g * scale + 16, y + 4, f"{g:+.0f}", GC, 28, rise(1) + DELAY(90 * k), mono=True))
o.append(svg(seg(96, 720, 900, 720, LINE, 3)))
o.append(p(f"position:absolute;left:96px;top:740px;width:140px;font-size:28px;font-weight:700;color:{INK};white-space:nowrap", "평균"))
o.append(bar(240, 746, 44 * scale, 40, WC, rise(2)))
o.append(label(240 + 44 * scale + 16, 744, "−44", WC, 28, rise(2), mono=True))
o.append(f'<div{rise(2)} style="position:absolute;left:1020px;top:300px;width:810px;display:flex;flex-direction:column;gap:10px">'
         + p(f"font-size:36px;font-weight:700;color:{WC}", "배치 경사 하강법 (BGD)") + p(f"font-size:28px;line-height:1.5;color:{SUB}", "5명 경사의 평균 −44로 1 epoch에 한 걸음") + '</div>')
o.append(f'<div{rise(3)} style="position:absolute;left:1020px;top:520px;width:810px;display:flex;flex-direction:column;gap:10px">'
         + p(f"font-size:36px;font-weight:700;color:{GC}", "확률적 경사 하강법 (SGD)") + p(f"font-size:28px;line-height:1.5;color:{SUB}", "한 명의 경사로 바로 한 걸음, 1 epoch에 다섯 걸음. 걸음마다 방향과 크기가 들쭉날쭉해요.") + '</div>')
o.append(note(1020, 780, 810, "SGDRegressor의 S가 Stochastic(확률적)이에요. 데이터가 크면 한 명씩 가는 쪽이 빨라요.", SUB, 26, rise(4)))
W("sgd", o, "경사를 몇 명을 보고 재느냐에 따라 이름이 달라요. 배치 경사 하강법은 5명 모두의 경사를 재서 평균을 낸 뒤 한 걸음 가요. 정확하지만 데이터가 수백만 줄이면 한 걸음에 오래 걸려요. 확률적 경사 하강법은 한 명의 경사만 보고 바로 한 걸음 가요. 1번 학생은 마이너스 8, 5번은 마이너스 120처럼 학생마다 경사가 달라서 걸음이 들쭉날쭉해요. 그래도 여러 걸음이 모이면 평균 방향으로 가요. 수업에서 쓴 SGDRegressor의 S가 Stochastic, 확률적이에요. shuffle=False라서 수업에서는 1번부터 5번 순서대로 한 명씩 봤어요. 그림의 경사는 w 8, b 35에서 학생마다 잰 값이에요." + CALC)

# 26 learning curve and convergence
o = [sec("conv")] + head(2, "학습 곡선이 평평해지면 수렴했다고 해요", [("학습 곡선", GC, GBG), ("수렴", GC, GBG), ("history", GC, GBG)], "49")
HS = D["history"]
ep = HS["epoch"]
a = Ax(170, 300, 760, 500, (0, 1000), (0, 200))
o.append(svg(axes(a, [0, 250, 500, 750, 1000], [0, 50, 100, 150, 200], "epoch", "손실 MSE")))
o.append(svg(poly(a, [(x, min(m, 200)) for x, m in zip(ep, HS["mse"]) if x >= 2][::3], EC, 5), WIPE(1)))
o.append(label(a.X(30) + 10, a.y - 12, "1번째 1369.8", EC, 24, fade(1)))
o.append(label(a.X(1000), a.Y(3.25) - 50, "3.25", EC, 30, fade(1) + DELAY(600), mono=True, anchor="right"))
a2 = Ax(1100, 300, 620, 200, (0, 1000), (0, 20))
o.append(svg(axes(a2, [], [0, 10, 20], "", "기울기 w") + poly(a2, [(0, 10), (1000, 10)], GRAY, 3, "8 8")))
o.append(svg(poly(a2, list(zip(ep, HS["w"]))[::3], WC, 5), WIPE(2)))
o.append(label(a2.X(1000) + 10, a2.Y(10.13) - 20, "10.13", WC, 26, fade(2) + DELAY(600), mono=True))
a3 = Ax(1100, 600, 620, 200, (0, 1000), (0, 40))
o.append(svg(axes(a3, [0, 500, 1000], [0, 20, 40], "epoch", "절편 b") + poly(a3, [(0, 35), (1000, 35)], GRAY, 3, "8 8")))
o.append(svg(poly(a3, list(zip(ep, HS["b"]))[::3], BC, 5), WIPE(2)))
o.append(label(a3.X(1000) + 10, a3.Y(34.74) - 10, "34.74", BC, 26, fade(2) + DELAY(600), mono=True))
o.append(note(170, 900, 1660, "500번째 3.30, 1000번째 3.25. 더 돌려도 거의 안 바뀌는 상태가 수렴이에요. 회색 점선은 LinearRegression이 구한 10과 35예요.", SUB, 26, rise(3)))
W("conv", o, "학습 곡선은 epoch마다 손실을 기록해서 그린 그래프예요. 49에서 history에 쌓은 mse 열이에요. 처음에는 1369.8로 아주 크다가 빠르게 내려가고, 나중에는 거의 평평해져요. 500번째가 3.30, 1000번째가 3.25예요. 더 돌려도 손실과 w, b가 거의 안 바뀌는 상태를 수렴했다고 해요. 오른쪽은 같은 기록의 w와 b예요. 회색 점선인 LinearRegression의 답 10과 35 근처, 10.13과 34.74에 멈췄어요. 왼쪽 그래프는 200 위를 잘라서 그렸어요." + REAL)

# 27 hyperparameters
o = [sec("hyper")] + head(2, "괄호 안은 사람이 정하는 값, 끝에 _가 붙은 건 모델이 배운 값이에요",
                          [("하이퍼파라미터", GC, GBG), ("파라미터", WC, WBG), ("coef_", WC, WBG), ("intercept_", BC, BBG)], "48 · 49")
cs3 = C["sgd"]
html_, bot = code(96, 260, 860, cs3["code"], None, fs=28)
o.append(html_)
o.append(box(1, 96 + 10, cline(260, 1, 28) - 24, 840, 28 * 1.5 * 6 + 6, GC))
HY = [("loss", "손실 함수", "loss"), ("learning_rate", "학습률을 바꿀지", "lr"), ("eta0", "학습률", "lr"), ("max_iter", "fit()의 바퀴 수", "epoch"), ("shuffle", "섞을지", "sgd"), ("random_state", "시드", "seed")]
for k, (arg, t_, sid) in enumerate(HY):
    o.append(tag(96 + 22 + tw(cs3["code"][k + 1], 28) + 30, cline(260, k + 1, 28), f"{e(t_)} <span style=\"color:{GRAY}\">{pg(sid)}쪽</span>", GC, fade(1) + DELAY(70 * k), 25))
o.append(code(1300, 300, 530, ["sgd.coef_", "sgd.intercept_"], ["array([10.12933517])", "array([34.74123793])"], fs=22)[0])
o.append(box(2, 1300 + 6, 300 + 4, 518, 22 * 1.5 * 2 + 16, WC))
o.append(note(1300, 520, 530, "학습이 끝나야 생기는 값이라 이름 끝에 _가 붙어요.", SUB, 26, rise(2)))
o.append(f'<div{rise(3)} style="position:absolute;left:96px;top:{bot + 50:.0f}px;width:1728px;display:flex;flex-direction:row;gap:60px">'
         + p(f"font-size:30px;font-weight:700;color:{GC};white-space:nowrap", "하이퍼파라미터: 학습 전에 사람이 골라요")
         + p(f"font-size:30px;font-weight:700;color:{WC};white-space:nowrap", "파라미터: 학습하면서 모델이 찾아요") + '</div>')
W("hyper", o, "숫자에는 두 종류가 있어요. SGDRegressor 괄호 안에 적는 값은 학습을 시작하기 전에 사람이 골라요. 이걸 하이퍼파라미터라고 해요. 손실 함수, 학습률, 바퀴 수, 섞을지, 시드가 모두 여기에 들어가요. 반대로 coef_와 intercept_는 학습하면서 모델이 데이터에서 찾은 값이에요. 이쪽을 파라미터라고 해요. scikit-learn은 학습한 뒤에 생기는 값의 이름 끝에 밑줄을 붙여요. 괄호 안에 왜 그 값이 들어가는지 궁금하면 오른쪽 쪽 번호로 가요. 오른쪽 출력은 이 셀 뒤에 1000 epoch를 학습한 결과예요.")

# =====================================================================================
# part 4: several columns (50)
# =====================================================================================
cm3 = C["multi"]
co = D["coef3"]
# 28 multiple regression
o = [sec("multi")] + head(3, "다중 선형 회귀는 문제 열이 여러 개인 선형 회귀예요",
                          [("multiple linear regression", MAG, "#F6E7EF"), ("coef_ 배열", WC, WBG)], "50")
o.append(f'<div id="m-one"{MORPH_FROM()} style="position:absolute;left:96px;top:300px;font-family:{MONO};font-size:50px;font-weight:700;color:{INK};white-space:nowrap">'
         + tok("y", "점수") + tok("eq", "\u00a0=\u00a0") + tok("w1", "w", f"color:{WC}") + tok("x1", "×공부") + tok("pb", "\u00a0+\u00a0") + tok("b", "b", f"color:{BC}") + '</div>')
o.append(f'<div{MORPH(1, "m-one")} style="position:absolute;left:96px;top:300px;font-family:{MONO};font-size:50px;font-weight:700;color:{INK};white-space:nowrap">'
         + tok("y", "점수") + tok("eq", "\u00a0=\u00a0") + tok("w1", "5.80", f"color:{WC}") + tok("x1", "×공부") + " + " + '<span style="color:#1F8A4C">2.68</span>×수면 + <span style="color:#7A5BD0">0.63</span>×문제' + tok("pb", "\u00a0+\u00a0") + tok("b", "17.66", f"color:{BC}") + '</div>')
html_, bot = code(96, 440, 1020, cm3["code"][7:], cm3["out"], fs=22)
o.append(html_)
yo = oline(440, len(cm3["code"][7:]), 0, 22)
o.append(tag(96 + 22 + tw(cm3["out"][0], 22) + 30, yo, "열 3개라 숫자 3개, 열 순서대로", WC, rise(2), 22))
o.append(tag(96 + 22 + tw(cm3["out"][1], 22) + 30, yo + 33, "b는 여전히 하나", BC, rise(2), 22))
o.append(table(1190, 440, ["study", "sleep", "practice", "score"], [r_[:4] for r_ in D["study"][:6]], [130, 130, 160, 130], fs=24, rh=52))
o.append(note(1190, 820, 640, "10명 중 6명이에요. 50에서 쓰는 수업 데이터예요.", GRAY, 24))
W("multi", o, "48과 49는 공부 시간 하나로 점수를 예측했어요. 다중 선형 회귀는 문제 열을 여러 개 넣어요. 50에서는 공부 시간, 수면 시간, 푼 문제 수 세 열을 넣었어요. 식은 열마다 w가 하나씩 붙고 b는 하나예요. 그래서 coef_는 열 수만큼의 숫자가 든 배열이 되고, 순서는 X에 넣은 열 순서와 같아요. 숫자 하나일 때 coef_[0]으로 꺼낸 이유가 여기 있어요. intercept_는 여전히 하나예요." + REAL, ("p4", "여러 열로 예측"))

# 29 reading coefficients
o = [sec("coefread")] + head(3, "계수는 다른 열은 그대로 두고 그 열만 1 늘렸을 때 바뀌는 점수예요", [("계수", MAG, "#F6E7EF"), ("coefficient", MAG, "#F6E7EF")], "50")
cmp_ = C["multipred"]
o.append(f'<div style="position:absolute;left:96px;top:290px;display:flex;flex-direction:row;gap:24px">'
         + chip('공부 ', WC, WBG, 34).replace("공부 ", '공부 <span id="sh" data-start="3">4</span>') + chip("수면 7", GR, GRBG, 34) + chip("문제 20", "#7A5BD0", "#ECE7F8", 34) + '</div>')
o.append(text(2, "sh", "4"))
# stacked bar of contributions for 3 and 4 hours
base_x, unit = 96, 15.5
parts_ = [("b", co[3], BC), ("공부", co[0] * 3, WC), ("수면", co[1] * 7, GR), ("문제", co[2] * 20, "#7A5BD0")]
xx = base_x
for nm, v, col in parts_:
    o.append(bar(xx, 440, v * unit - 4, 90, col))
    o.append(label(xx + v * unit / 2, 455, f"{v:.1f}", "#FFFFFF", 26, "", mono=True, anchor="center"))
    o.append(label(xx + v * unit / 2, 545, nm, GRAY, 22, "", anchor="center"))
    xx += v * unit
o.append(label(xx + 16, 460, "66.48", INK, 40, fade(1), mono=True))
xx = base_x
for nm, v, col in parts_[:2] + [("+", co[0], None)] + parts_[2:]:
    if col:
        o.append(f'<div{fade(2)} style="position:absolute;left:{xx:.0f}px;top:640px;width:{v * unit - 4:.0f}px;height:90px;border-radius:6px;background:{col};opacity:0.28"></div>')
    xx += v * unit
o.append(bar(base_x + (co[3] + co[0] * 3) * unit, 640, co[0] * unit - 4, 90, WC, fade(2)))
o.append(label(base_x + (co[3] + co[0] * 3.5) * unit, 655, "+5.80", "#FFFFFF", 26, fade(2), mono=True, anchor="center"))
o.append(label(base_x + (co[3] + co[0] * 4 + co[1] * 7 + co[2] * 20) * unit + 16, 660, "72.28", INK, 40, fade(2), mono=True))
o.append(label(96, 600, "공부만 1시간 더", WC, 26, fade(2)))
o.append(code(96, 790, 1150, cmp_["code"], cmp_["out"], fs=19)[0])
o.append(note(1300, 790, 530, "혼자 학습하면 공부 기울기가 8.9였는데 같이 넣으면 5.80이에요. 문제 수가 공부 시간과 같이 움직여서 몫을 나눠 가졌어요.", SUB, 25, rise(3)))
W("coefread", o, "다중 회귀의 계수는 이렇게 읽어요. 다른 열은 그대로 두고 그 열만 1 늘리면 점수가 계수만큼 바뀌어요. 공부 3시간, 수면 7시간, 문제 20개인 학생의 예측은 66.48점이에요. 수면과 문제는 그대로 두고 공부만 4시간으로 늘리면 72.28점, 정확히 공부 계수 5.80만큼 올라요. 막대는 절편 17.66에 열마다 계수 곱하기 값을 쌓은 거예요. 공부 시간 하나로만 학습하면 기울기가 8.9였는데, 세 열을 같이 넣으면 5.80으로 줄어요. 문제 수가 공부 시간과 같이 늘어나서 점수 오르는 몫을 나눠 가졌기 때문이에요. 혼자일 때 8.9는 50 스레드에서 실행한 값이에요." + REAL)

# 30 heatmap
o = [sec("heat")] + head(3, "상관계수 표는 모든 열 짝의 상관계수, heatmap은 그걸 색으로 칠한 거예요",
                         [("df.corr()", MAG, "#F6E7EF"), ("sns.heatmap", MAG, "#F6E7EF"), ("annot", MAG, "#F6E7EF"), ("vmin, vmax", MAG, "#F6E7EF")], "47 · 50")
HM, HC = D["heat"], ["study_hours", "sleep_hours", "practice_count", "score"]
S = 150
x0, y0 = 360, 270


def hcol(v):
    """-1 blue, 0 white, 1 red, like a diverging colour bar from vmin=-1 to vmax=1."""
    if v >= 0:
        r, g, b = 255, int(255 - v * (255 - 120)), int(255 - v * (255 - 110))
    else:
        r, g, b = int(255 + v * (255 - 90)), int(255 + v * (255 - 140)), 255
    return f"rgb({r},{g},{b})"


cells_ = ""
for i in range(4):
    for j in range(4):
        v = HM[i][j]
        cells_ += f'<rect x="{x0 + j * S}" y="{y0 + i * S}" width="{S - 4}" height="{S - 4}" fill="{hcol(v)}" rx="6"/>' + stext(x0 + j * S + S / 2 - 2, y0 + i * S + S / 2 + 12, f"{v:.2f}", INK, 34, weight=700, mono=True)
o.append(svg(cells_))
for i, nm in enumerate(HC):
    o.append(label(x0 - 20, y0 + i * S + S / 2 - 18, nm, INK, 24, "", mono=True, anchor="right"))
    o.append(label(x0 + i * S + S / 2, y0 + 4 * S + 10, nm.split("_")[0], INK, 24, "", mono=True, anchor="center"))
o.append(spot(1, x0 - 250, y0 + 3 * S - 4, 4 * S + 260, S + 4))
o.append(spot_off(2))
grad_ = "".join(f'<rect x="1000" y="{y0 + k * 6}" width="40" height="6" fill="{hcol(1 - k / 50)}"/>' for k in range(100))
o.append(svg(grad_ + stext(1056, y0 + 12, "1.00", GRAY, 22, "start") + stext(1056, y0 + 306, "0.00", GRAY, 22, "start") + stext(1056, y0 + 600, "−1.00", GRAY, 22, "start")))
HA = [('annot=True', "칸에 숫자를 적어요"), ('fmt=".2f"', "소수 둘째 자리까지"), ('vmin=-1, vmax=1', "색 막대를 −1~1로 고정")]
for k, (arg, t_) in enumerate(HA):
    o.append(p(f"position:absolute;left:1200px;top:{300 + k * 110}px;width:630px;display:flex;flex-direction:column;gap:4px",
               f'<span style="font-family:{MONO};font-size:28px;font-weight:700;color:{MAG}">{e(arg)}</span><span style="font-size:26px;color:{SUB}">{e(t_)}</span>', rise(2 + (k > 0))))
o.append(note(1200, 660, 630, "대각선은 자기 자신이라 늘 1.00이에요. score 줄을 보면 점수와 같이 움직이는 열을 찾을 수 있어요.", SUB, 25, rise(3)))
W("heat", o, "df.corr()는 모든 열 짝의 상관계수를 표로 줘요. 47에서는 두 열 사이 하나만 구했는데, 열이 넷이면 4 곱하기 4 표가 돼요. heatmap은 그 표를 색으로 칠한 그림이에요. 맨 아래 score 줄을 보면 공부 시간과 문제 수가 0.93으로 점수와 같이 움직이고, 수면은 0.29로 약해요. 대각선은 자기 자신과의 상관계수라 늘 1이에요. annot=True는 칸에 숫자를 적고, fmt는 소수 둘째 자리, vmin과 vmax는 색 막대를 마이너스 1부터 1로 고정해요. 고정하지 않으면 표 안의 가장 작은 값이 가장 진한 색이 돼서 0이 파랗게 보일 수 있어요. 그림의 색은 seaborn 기본 색과 다르게 이 사전에서 칠했어요." + REAL)

# =====================================================================================
# part 5: pairs and myths
# =====================================================================================
o = [sec("pair1")] + head(4, "오차는 한 명, 손실은 모델 전체, 손실 함수는 재는 규칙이에요", None, "48 · 49")
PR = [("오차", "학생 한 명이 빗나간 양", "2, −2, 0, −2, 2", EC, "error"),
      ("손실", "모델 전체를 숫자 하나로", "3.2", EC, "loss"),
      ("손실 함수", "그 숫자를 내는 규칙", "MSE, MAE …", EC, "loss"),
      ("평가 지표", "사람이 읽는 성적표", "MAE 1.6, R² 0.98", PUR, "r2")]
for k, (t_, d_, v_, col, sid) in enumerate(PR):
    y = 290 + k * 150
    o.append(f'<div{rise(k + 1)} style="position:absolute;left:96px;top:{y}px;width:1728px;height:130px;display:flex;flex-direction:row;align-items:center;gap:30px;border-bottom:2px solid {LINE}">'
             + p(f"width:260px;flex:none;font-size:44px;font-weight:700;color:{col}", e(t_)) + p(f"width:560px;flex:none;font-size:32px;color:{INK}", e(d_))
             + p(f"flex:1;font-family:{MONO};font-size:34px;font-weight:700;color:{INK};white-space:nowrap", e(v_)) + p(f"font-size:26px;font-weight:700;color:{GRAY};white-space:nowrap", f"{pg(sid)}쪽") + '</div>')
o.append(note(96, 900, 1728, "49의 손실 3.2와 48의 MSE 3.2는 같은 계산이에요. 학습할 때 부르면 손실, 채점할 때 부르면 지표예요.", SUB, 28, rise(5)))
W("pair1", o, "비슷해서 자주 섞이는 넷이에요. 오차는 학생 한 명마다 하나씩 있어요. 손실은 그 오차들을 모아 모델 전체를 숫자 하나로 나타낸 값이고, 손실 함수는 그 숫자를 어떤 규칙으로 낼지예요. MSE도 MAE도 손실 함수가 될 수 있어요. 평가 지표는 학습이 끝난 뒤 사람이 모델을 채점하려고 보는 점수예요. 같은 MSE 3.2라도 학습 중에 모델이 줄이려고 보면 손실, 학습 뒤에 우리가 성적으로 보면 평가 지표라고 불러요.", ("p5", "헷갈리는 짝과 오해"))

o = [sec("pair2")] + head(4, "상관계수, 기울기, R²는 재는 것이 달라요", None, "47 · 48")
PR2 = [("상관계수 r", "얼마나 직선에 붙어 있나", "0.99", "0.99", TC, "corr"),
       ("기울기 w", "1시간에 몇 점 오르나", "10", "20", WC, "wb"),
       ("R²", "직선이 오차를 얼마나 줄였나", "0.98", "0.98", PUR, "r2")]
o.append(p(f"position:absolute;left:1180px;top:270px;width:300px;font-size:26px;font-weight:700;color:{GRAY};text-align:center", "점수 그대로"))
o.append(p(f"position:absolute;left:1500px;top:270px;width:300px;font-size:26px;font-weight:700;color:{GRAY};text-align:center", "점수 × 2"))
for k, (t_, d_, v1, v2, col, sid) in enumerate(PR2):
    y = 330 + k * 160
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:140px;display:flex;flex-direction:row;align-items:center;border-bottom:2px solid {LINE}">'
             + p(f"width:300px;flex:none;font-size:40px;font-weight:700;color:{col}", e(t_)) + p(f"width:684px;flex:none;font-size:30px;color:{INK}", e(d_) + f' <span style="color:{GRAY};font-size:24px">{pg(sid)}쪽</span>')
             + p(f"width:320px;flex:none;font-family:{MONO};font-size:54px;font-weight:700;color:{INK};text-align:center", v1)
             + p(f"width:320px;flex:none;font-family:{MONO};font-size:54px;font-weight:700;color:{INK};text-align:center", (f'<span id="pv{k}" data-start="{v1}">{v2}</span>' if k == 1 else f'<span id="pv{k}">{v2}</span>')) + '</div>')
o.append(text(1, "pv1", "20"))
o.append(pulse(2, "pv0"))
o.append(pulse(2, "pv2"))
cd = C["double"]
o.append(code(96, 830, 900, cd["code"][1:], cd["out"], fs=20)[0])
o.append(note(1100, 830, 720, "점수를 2배로 바꿔도 r와 R²는 그대로예요. 단위를 타는 건 기울기 w뿐이에요. r를 제곱하면 R²예요.", SUB, 26, rise(2)))
W("pair2", o, "셋 다 두 열의 관계를 말하지만 재는 것이 달라요. 상관계수는 점들이 직선에 얼마나 붙어 있는지라 단위가 없어요. 기울기 w는 1시간에 몇 점 오르는지라 단위가 점수 나누기 시간이에요. R²는 직선이 평균만 찍을 때보다 오차를 얼마나 줄였는지예요. 점수를 모두 2배로 바꿔서 다시 학습하면 기울기는 20이 되는데, 상관계수와 R²는 그대로예요. 그래서 기울기가 크다고 관계가 강한 게 아니에요. 열이 하나인 선형 회귀에서는 상관계수를 제곱하면 R²와 같아요. 0.9921의 제곱이 0.9843이에요." + REAL)

o = [sec("myth1")] + head(4, "오해 1: R²는 0~1이고, MSE 3.2는 3.2점 틀렸다는 뜻이다", None, "48")
cn = C["r2neg"]
a = Ax(170, 390, 700, 380, (0, 6), (0, 110))
o.append(svg(axes(a, [0, 2, 4, 6], [0, 50, 100], "공부 시간", "점수") + poly(a, [(0, 0), (5.5, 110)], EC, 5) + poly(a, [(0, 65), (6, 65)], GRAY, 3, "8 8") + "".join(dot(a, hx, sy, INK, 10) for hx, sy in zip(HRS, SCO))))
o.append(label(a.X(4.6), a.Y(100) - 10, "20 × 공부 시간", EC, 26, "", anchor="right"))
o.append(label(a.X(6), a.Y(65) + 8, "평균 65", GRAY, 24, "", anchor="right"))
o.append(code(170, 870, 760, cn["code"], cn["out"], fs=20)[0])
o.append(ring(1, 170 + 14, oline(870, 2, 0, 20) - 20, tw(cn["out"][0], 20) + 18, 40, RED))
o.append(label(170, 270, "R²가 마이너스면 평균만 찍기보다 못한 직선이에요", EC, 28, rise(1)))
cm = C["metrics"]
o.append(label(1040, 270, "MSE는 점수²라서 점수로 읽으려면", PUR, 28, rise(2)))
o.append(f'<div{rise(2)} style="position:absolute;left:1040px;top:340px;width:790px;display:flex;flex-direction:column;gap:22px">'
         + "".join(p(f"font-family:{MONO};font-size:44px;font-weight:700;color:{INK};white-space:nowrap", f'{k_} <span style="color:{PUR}">{v_}</span> <span style="font-family:{SANS};font-size:28px;color:{GRAY}">{u_}</span>')
                   for k_, v_, u_ in [("MSE ", "3.2", "점수²"), ("RMSE", "1.79", "점수"), ("MAE ", "1.6", "점수")]) + '</div>')
o.append(note(1040, 640, 790, "평균 몇 점 틀렸는지는 MAE 1.6이나 RMSE 1.79로 말해요.", SUB, 28, rise(2)))
W("myth1", o, "자주 듣는 두 가지 오해를 실제 숫자로 볼게요. 첫째, R²는 0부터 1 사이라는 말이요. 평균만 찍으면 0이고, 그보다 못한 모델은 마이너스가 나와요. 공부 시간에 20을 곱한 엉터리 직선은 R²가 마이너스 0.12예요. 오류가 아니라 평균보다 못하다는 성적이에요. 둘째, MSE 3.2는 3.2점 틀렸다는 뜻이 아니에요. 제곱해서 더했으니 단위가 점수의 제곱이에요. 평균 몇 점 틀렸는지 말하려면 MAE 1.6이나 RMSE 1.79를 써요." + REAL)

o = [sec("myth2")] + head(4, "오해 2: 학습률이 크면 빨리 끝나고, epoch는 많을수록 좋다", None, "49")
EH = D["eta_hist"]
a = Ax(170, 390, 700, 400, (0, 1000), (0, 200))
o.append(svg(axes(a, [0, 500, 1000], [0, 100, 200], "epoch", "MSE")))
o.append(svg(poly(a, [(i + 1, min(m, 200)) for i, m in enumerate(EH["0.01"])][::4], GR, 5)))
o.append(svg(poly(a, [(i + 1, min(m, 200)) for i, m in enumerate(EH["0.001"])][::4], GRAY, 5)))
o.append(svg(f'<line x1="{a.X(0)}" y1="{a.Y(200)}" x2="{a.X(1000)}" y2="{a.Y(200)}" stroke="{RED}" stroke-width="6"/>'))
o.append(label(a.X(1000) + 16, a.Y(200) - 64, "eta0", SUB, 22, "", mono=True))
o.append(label(a.X(1000) + 16, a.Y(200) - 18, "0.3 터짐", RED, 24, ""))
o.append(label(a.X(1000) + 16, a.Y(EH["0.001"][-1]) - 18, "0.001: 33", GRAY, 24, ""))
o.append(label(a.X(1000) + 16, a.Y(3) - 18, "0.01: 3.25", GR, 24, ""))
o.append(label(170, 270, "학습률은 크면 튀고, 작으면 느려요", RED, 28, rise(1)))
o.append(label(1040, 270, "수렴한 뒤에는 더 돌려도 그대로예요", OR, 28, rise(2)))
HSs = D["history"]["mse"]
o.append(f'<div{rise(2)} style="position:absolute;left:1040px;top:340px;width:790px;display:flex;flex-direction:column;gap:14px">'
         + "".join(p(f"font-family:{MONO};font-size:40px;font-weight:700;color:{INK};white-space:nowrap", f'epoch {k_:>4} <span style="color:{EC}">{HSs[k_ - 1]:.2f}</span>') for k_ in [100, 300, 500, 1000]) + '</div>')
o.append(f'<div id="m2last" style="position:absolute;left:1040px;top:{340 + 3 * 74 - 4}px;width:470px;height:62px"></div>')
o.append(ring(3, 1030, 340 + 2 * 74 - 8, 470, 140, OR))
o.append(note(1040, 700, 790, "500에서 1000으로 두 배 돌려도 3.30이 3.25가 될 뿐이에요. 데이터가 커지면 시간만 두 배 들어요.", SUB, 28, rise(3)))
W("myth2", o, "경사 하강법의 오해 둘이에요. 첫째, 학습률을 키우면 큰 걸음으로 빨리 끝난다는 생각이요. 0.3으로 키우면 첫 epoch부터 손실이 바닥을 지나쳐 튀어 오르고, 1000번 뒤에는 10의 24제곱이 됐어요. 반대로 0.001은 안전하지만 1000번을 돌려도 33이에요. 둘째, epoch는 많을수록 좋다는 생각이요. 0.01로 돌린 기록을 보면 300번째 4.25, 500번째 3.30, 1000번째 3.25예요. 수렴한 뒤에는 바퀴를 두 배로 늘려도 거의 그대로이고 시간만 두 배 들어요." + REAL)

# =====================================================================================
# part 6: read code with terms
# =====================================================================================
o = [sec("read1")] + head(5, "수업 셀 읽기 1: SGDRegressor를 만드는 셀", None, "49")
html_, bot = code(96, 240, 1000, cs3["code"], None, fs=36)
o.append(html_)
RD = [(1, "손실 함수는 제곱 오차(MSE)", "loss"), (2, "학습률을 끝까지 그대로", "lr"), (3, "학습률(한 걸음) 0.01", "lr"), (4, "fit()의 바퀴 수 (partial_fit엔 안 쓰임)", "epoch"), (5, "1번부터 순서대로 한 명씩", "sgd"), (6, "시드 42, 매번 같은 결과", "seed")]
for k, (ln, t_, sid) in enumerate(RD):
    o.append(lspot(k + 1 if k < 4 else 4 + (k - 3), 96, 240, 1000, 24 + 54 * 8, cline(240, ln, 36) - 27, 54))
o.append(lspot_off(7))
for k, (ln, t_, sid) in enumerate(RD):
    o.append(tag(1130, cline(240, ln, 36), f"{e(t_)} <span style=\"color:{GRAY}\">{pg(sid)}쪽</span>", GC, rise(min(k + 1, 5) if k < 4 else 5), 28))
o.append(note(96, bot + 50, 1728, "괄호 안 여섯 개가 모두 학습 전에 사람이 고른 하이퍼파라미터예요.", SUB, 30, rise(5)))
W("read1", o, "앞에서 본 용어로 수업 셀을 읽어 볼게요. 49에서 SGDRegressor를 만드는 셀이에요. loss=\"squared_error\"는 손실 함수를 제곱 오차, 곧 MSE로 쓴다는 뜻이에요. learning_rate=\"constant\"는 학습률을 바꾸지 않고, eta0=0.01이 그 학습률이에요. max_iter는 fit()이 몇 바퀴 돌지인데, 수업은 partial_fit을 for로 직접 돌려서 쓰이지 않았어요. shuffle=False는 데이터를 섞지 않고 1번 학생부터 순서대로 보라는 뜻이고, random_state는 시드예요. 여섯 개 모두 사람이 정한 하이퍼파라미터예요. 수업 주석에는 eta0이 초기 학습률로 적혀 있었는데, constant라서 처음부터 끝까지 같은 학습률이에요.", ("p6", "용어로 코드 읽기"))

o = [sec("read2")] + head(5, "수업 셀 읽기 2: 학습 기록 history_df", None, "49")
LO = cl["out"]
o.append(f'<div id="hist" style="position:absolute;left:96px;top:330px;width:1100px">' + "".join(
    p(f"font-family:{MONO};font-size:34px;line-height:1.6;white-space:pre;color:{INK};{'font-weight:700' if j == 0 else ''}", e(l)) for j, l in enumerate(LO)) + '</div>')
cols_x = {"epoch": LO[0].find("epoch"), "weight": LO[0].find("weight"), "bias": LO[0].find("bias"), "mse": LO[0].find("mse")}
TAGS = [("epoch", "몇 바퀴째", GC, "epoch"), ("weight", "기울기 w", WC, "wb"), ("bias", "절편 b", BC, "wb"), ("mse", "손실", EC, "loss")]
for k, (cn_, t_, col, sid) in enumerate(TAGS):
    xx = 96 + tw(LO[0][:cols_x[cn_]], 34)
    o.append(p(f"position:absolute;left:{xx:.0f}px;top:250px;font-size:28px;font-weight:700;color:{col};white-space:nowrap", f"{e(t_)} <span style=\"color:{GRAY};font-size:22px\">{pg(sid)}</span>", rise(1) + DELAY(120 * k)))
o.append(spot(2, 96, 330 + 34 * 1.6, 1100, 34 * 1.6, pad=8))
o.append(spot(3, 96, 330 + 34 * 1.6 * 6, 1100, 34 * 1.6, pad=8))
o.append(spot_off(4))
o.append(note(1260, 330, 570, "1번째: w 8.46, b 2.73, 손실 1369.8. 아직 엉뚱한 직선이에요.", SUB, 28, rise(2)))
o.append(note(1260, 520, 570, "1000번째: w 10.13, b 34.74, 손실 3.25. 10과 35 근처에 수렴했어요.", SUB, 28, rise(3)))
o.append(note(1260, 710, 570, "w가 17까지 갔다가 돌아오는 건 b가 아직 작아서예요. 둘이 같이 맞춰져요.", SUB, 26, rise(4)))
o.append(code(96, 800, 1100, cl["code"][-1:], None, fs=24, attrs=rise(5))[0])
o.append(note(96, 900, 1100, "isin으로 고른 여섯 줄만 봐요. 맨 왼쪽 0, 4, 9는 원래 표의 행 번호예요.", SUB, 26, rise(5)))
W("read2", o, "49에서 epoch마다 w, b, 손실을 쌓은 표예요. 열 이름을 용어로 바꿔 읽으면 돼요. epoch는 몇 바퀴째인지, weight는 직선의 기울기 w, bias는 절편 b, mse는 그 순간의 손실이에요. 1번째 줄은 w 8.46, b 2.73으로 아직 엉뚱한 직선이라 손실이 1369.8이에요. 1000번째 줄은 w 10.13, b 34.74, 손실 3.25로 LinearRegression의 답 근처에 수렴했어요. 중간에 w가 17까지 커졌다가 돌아오는 건, 처음에 b가 너무 작아서 w가 대신 점수를 끌어올리다가 b가 커지면서 제자리를 찾기 때문이에요. 수업은 1, 5, 10, 50, 100, 300, 500, 1000번째 줄을 봤고, 여기서는 그중 여섯 줄이에요." + REAL)

o = [sec("read3")] + head(5, "수업 셀 읽기 3: 학습과 채점 결과 여섯 줄", None, "48")
OUT6 = C["fit"]["out"] + C["metrics"]["out"]
o.append(f'<div style="position:absolute;left:96px;top:290px;width:760px;background:#FFFFFF;border:2px solid {LINE};border-radius:16px;padding:20px 30px">' + "".join(
    p(f"font-family:{MONO};font-size:40px;line-height:1.7;white-space:pre;color:{INK}", e(l)) for l in OUT6) + '</div>')
R3 = [("직선의 기울기, 1시간에 +10점", "wb", WC), ("0시간의 점수", "wb", BC), ("평균 1.6점 빗나감", "mae", PUR), ("오차 제곱의 평균 (점수²)", "mse", PUR), ("점수 단위로 되돌린 MSE", "mse", PUR), ("평균만 찍기보다 98% 줄임", "r2", PUR)]
for k, (t_, sid, col) in enumerate(R3):
    yy = 290 + 20 + 40 * 1.7 * (k + 0.5)
    o.append(p(f"position:absolute;left:1010px;top:{yy - 24:.0f}px;font-size:32px;font-weight:700;color:{col};white-space:nowrap", f"{e(t_)} <span style=\"color:{GRAY};font-size:24px\">{pg(sid)}쪽</span>", rise(min(k + 1, 5)) if k < 4 else rise(5)))
    o.append(link(min(k + 1, 5), 96 + 30 + tw(OUT6[k], 40) + 20, yy, 990, yy, col, 4))
o.append(note(96, 790, 1728, f"48의 LinearRegression 결과예요. 수업 마크다운의 6시간 예측 96점은 실제로 실행하면 95.0점이에요({pg('model')}쪽).", SUB, 28, rise(5)))
W("read3", o, "48과 49에서 학습과 채점을 하면 나오는 여섯 줄이에요. 위 두 줄은 모델이 배운 파라미터예요. 기울기 w 10은 1시간에 10점, 절편 b 35는 공부를 안 했을 때의 점수예요. 아래 네 줄은 채점이에요. MAE 1.6은 평균 1.6점 빗나갔다는 뜻이고, MSE 3.2는 오차 제곱의 평균이라 단위가 점수의 제곱이에요. RMSE 1.79는 그걸 점수 단위로 되돌린 값이에요. R² 0.98은 평균만 찍을 때보다 오차를 98% 줄였다는 뜻이에요. 쪽 번호를 따라가면 각 줄을 자세히 볼 수 있어요." + REAL)

# =====================================================================================
# index (가나다)
# =====================================================================================
IDX = [("경사 하강법", "경사를 보고 내리막으로 한 걸음씩", "gd"), ("계수", "그 열만 1 늘렸을 때 바뀌는 값", "coefread"), ("기울기 w", "1시간에 오르는 점수 (coef_)", "wb"),
       ("기울기 두 뜻", "직선의 w와 손실의 경사", "two"), ("난수와 시드", "같은 시드면 같은 숫자", "seed"), ("다중 선형 회귀", "문제 열이 여러 개", "multi"),
       ("모델", "학습으로 w와 b를 채우는 틀", "model"), ("미분", "한 점에서의 기울기", "deriv"), ("배치와 확률적", "다 보고 한 걸음, 한 명 보고 한 걸음", "sgd"),
       ("사분위수, IQR", "가운데 절반의 폭과 울타리", "iqr"), ("상관계수", "직선에 붙은 정도, −1~1", "corr"), ("상관계수 표", "모든 열 짝의 상관계수", "heat"),
       ("손실", "모델 전체가 빗나간 정도", "loss"), ("손실 함수", "손실을 내는 규칙 (MSE)", "loss"), ("수렴", "더 돌려도 거의 안 바뀜", "conv"), ("수식 기호", "Σ, n, i, ŷ", "formula"),
       ("에포크", "데이터 전체를 한 바퀴", "epoch"), ("예측값 ŷ", "모델이 찍은 값 (y_pred)", "error"), ("오차", "정답 − 예측", "error"), ("이상치", "울타리 밖의 튀는 값", "iqr"),
       ("절편 b", "0일 때의 값 (intercept_)", "wb"), ("정규분포", "평균 근처가 많은 종 모양", "seed"), ("중앙값", "한가운데 사람의 값", "mean"), ("특성과 타깃", "문제 X와 정답 y", "xy"),
       ("평균", "모두 더해 사람 수로 나눔", "mean"), ("평가 지표", "사람이 읽는 성적표", "pair1"), ("포물선, 2차함수", "U자 그래프", "parab"), ("하이퍼파라미터", "학습 전에 사람이 고르는 값", "hyper"),
       ("학습", "fit으로 w와 b를 찾음", "model"), ("학습 곡선", "epoch마다 손실 그래프", "conv"), ("학습률", "한 걸음의 크기 (eta0)", "lr"), ("heatmap", "상관계수 표를 색으로", "heat"),
       ("MAE", "오차 크기의 평균", "mae"), ("MSE", "오차 제곱의 평균", "mse"), ("R²", "평균보다 오차를 줄인 비율", "r2"), ("RMSE", "MSE의 제곱근", "mse")]
assert len(IDX) == 36
for part_, (sid, rng_) in enumerate([("index1", IDX[:18]), ("index2", IDX[18:])]):
    o = [sec(sid), f'<h2 style="position:absolute;left:96px;top:72px;font-size:60px;font-weight:700;line-height:1.3;color:{INK}">찾아보기 {part_ + 1}</h2>',
         p(f"position:absolute;left:520px;top:96px;font-size:28px;color:{GRAY}", "가나다 순, 영어는 뒤에")]
    for k, (t_, d_, s_) in enumerate(rng_):
        x, y = 96 + (k // 9) * 884, 200 + (k % 9) * 84
        o.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:844px;height:84px;display:flex;flex-direction:row;align-items:center;gap:20px;border-bottom:2px solid {LINE}">'
                 + p(f"width:270px;flex:none;font-size:30px;font-weight:700;color:{INK};white-space:nowrap", e(t_)) + p(f"flex:1;font-size:26px;color:{SUB};white-space:nowrap", e(d_))
                 + p(f"width:80px;flex:none;font-size:28px;font-weight:700;color:{BL};text-align:right", pg(s_)) + '</div>')
    if part_ == 1:
        o.append(p(f"position:absolute;left:96px;top:980px;font-size:26px;color:{GRAY}", "다음: 학습용과 채점용 데이터 나누기, 다른 모델은 다음 수업에서 이어져요."))
    W(sid, o, ("용어를 가나다 순으로 모은 찾아보기예요. 이름만 기억나고 뜻이 헷갈리면 여기서 한 줄 뜻을 보고, 더 자세히 보려면 오른쪽 쪽 번호로 가요." if part_ == 0 else
               "찾아보기의 나머지와 영어 이름 용어예요. MAE, MSE, RMSE, R²는 모두 48의 채점 쪽에 있어요. 이 사전은 45부터 50까지의 용어만 담았어요. 학습용과 채점용 데이터를 나누는 법처럼 다음 수업에 나오는 말은 그때 더해요."),
      ("index", "찾아보기") if part_ == 0 else None)

# ---------- order ----------
want = ["cover", "toc", "why", "map", "example",
        "mean", "iqr", "corr", "seed",
        "xy", "model", "wb", "error", "mae", "mse", "r2",
        "loss", "formula", "parab", "two", "deriv", "gd", "lr", "epoch", "sgd", "conv", "hyper",
        "multi", "coefread", "heat",
        "pair1", "pair2", "myth1", "myth2",
        "read1", "read2", "read3",
        "index1", "index2"]
assert sorted(want) == sorted(ORDER), (set(want) ^ set(ORDER))
ORDER[:] = want
pages = {sid: i + 1 for i, sid in enumerate(ORDER)}
if PAGE != pages:
    # second pass with page numbers known
    os.environ["PAGES"] = json.dumps(pages)
    os.execv(sys.executable, [sys.executable] + sys.argv)
deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-25T13:00:00Z"}, "lists": "css", "title": "머신러닝 용어 풀이", "order": ORDER, "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
print(len(ORDER), "slides")
