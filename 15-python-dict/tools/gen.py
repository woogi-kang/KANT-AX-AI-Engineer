"""Generates every slide of the Python basics 4 deck (15, dictionaries) and slides/deck.json.

Story: keeps writing in basics.ipynb from chapters 12-14. Finds values by key instead of by index (lockers),
changes and deletes them, walks a dictionary with for, mixes dictionaries with lists, compares them with
lists and tuples, then uses them in three cafe examples (receipt, cart, sales count).
Every cell and output comes from tools/demo.sh (tools/run_nb.py runs the cells with the project kernel).

Layout rules (Stageshow, 2026-11-08 redo): one focal object per slide, labels drawn on the code or the picture
instead of side cards, say it once, no empty bands, values move (fly) instead of being swapped.
Highlights come from tools/highlight.py (see tools/HIGHLIGHT.md). No typing animation.
Usage: python3 tools/gen.py slides
"""

import html, json, os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from highlight import spot, spot_off, ring, box, underline

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
INK, SUB, LINE, CARD, BG = "#1D2330", "#4A5262", "#E1DED6", "#FFFFFF", "#F6F5F1"
BL, GR, OR, RED, GRAY = "#2459C9", "#1F8A4C", "#B26A00", "#A33131", "#6A7180"
JP = "#B8560F"          # Jupyter, same as chapters 09 and 10
SEL = "#2F7DE1"         # selected cell bar, like VS Code's focus color
K1, K1BG = "#1E5FA8", "#E5EEF8"
K2, K2BG = "#A0620A", "#F7EEDD"
K3, K3BG = "#0F7C86", "#E2F2F3"
K4, K4BG = "#A23B72", "#F6E7EF"
K5, K5BG = "#3E4A61", "#E9EBF0"
GBG = "#EEEFF2"
EB1, EB2, EB3, EB4, EB5 = "1. 만들고 꺼내기", "2. 바꾸고 지우기", "3. 둘러보기", "4. 리스트와 섞기", "5. 실제로 써 보기"


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


def sec(sid, transition="fade", bg=BG):
    return f'<section id="{sid}" data-transition="{transition}" style="background:{bg};color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">'


def head(eyebrow, title, color):
    return [p(f"position:absolute;left:96px;top:48px;width:1728px;font-size:26px;font-weight:700;color:{color}", e(eyebrow), ' id="eyebrow"'),
            f'<h2 id="title" style="position:absolute;left:96px;top:92px;width:1728px;font-size:56px;font-weight:700;line-height:1.2;color:{INK}">{title}</h2>']


def caption(text, top=960, order=None):
    return p(f"position:absolute;left:96px;top:{top}px;width:1728px;font-size:32px;font-weight:700;line-height:1.4;color:{INK}", text, ' id="caption"' + bi("rise", order))


def WIDE(t):
    """Draws each Hangul syllable two monospace columns wide, like a terminal."""
    return re.sub(r"([가-힣])", r'<span style="display:inline-block;width:1.2em;text-align:center">\1</span>', t)


# ---------- notebook cell, drawn at FS px; every position below is measured from it ----------
FS = 30


def LH(fs=None):
    return (fs or FS) * 1.45


def tw(s, fs=None, wide=False):
    """Rendered width of a code string: Hangul is one em (1.2 em in wide output), the rest 0.6 em."""
    fs = fs or FS
    return sum(fs * ((1.2 if wide else 1.0) if '가' <= ch <= '힣' else 0.6) for ch in s)


def cell_h(c, fs=None):
    n, m = len(c["lines"]), len(c.get("out", []))
    return n * LH(fs) + 20 + m * (LH(fs) + 10)


def ly(top, i, fs=None):
    """Centre y of code line i of a cell drawn at top."""
    return top + 10 + i * LH(fs) + LH(fs) / 2


def oy(c, top, j, fs=None):
    """Centre y of output line j."""
    return top + len(c["lines"]) * LH(fs) + 20 + 10 + j * (LH(fs) + 10) + LH(fs) / 2


def lx(left, s="", fs=None, wide=False):
    """x where code or output text s ends inside a cell at left (text starts at left + 105)."""
    return left + 105 + tw(s, fs, wide)


def mark(order, x, yc, w, color=RED, h=50):
    """A tight pen box around one output word; rows are only 53px apart, so a loop would touch its neighbours."""
    return box(order, round(x - 10), round(yc - h / 2), round(w + 20), h, color, 4, 10)


def cell(c, left, top, w, sel=False, fs=None, attrs=""):
    """c: dict(id, lines, n, out, err, wide, dim={line: color}, oattrs={j: attrs})."""
    fs = fs or FS
    lines, n = c["lines"], c.get("n")
    o = [f'<div id="{c["id"]}"{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;display:flex;flex-direction:column;gap:10px">']
    bar = f'<div style="width:7px;flex:none;border-radius:4px;background:{SEL if sel else "transparent"}"></div>'
    gutter = p(f"width:58px;flex:none;font-family:{MONO};font-size:20px;color:{GRAY};text-align:right;padding-top:{fs * 0.4:.0f}px", f"[{n}]" if n else "[ ]")
    dim = c.get("dim", {})
    txt = "".join(p(f"font-family:{MONO};font-size:{fs}px;line-height:1.45;white-space:pre;color:{dim.get(i, INK)}", e(l) if l else "&#160;") for i, l in enumerate(lines))
    tag_ = p(f"position:absolute;right:14px;bottom:6px;font-size:18px;color:{GRAY}", "Python")
    box_ = f'<div style="flex:1;position:relative;background:#FFFFFF;border:2px solid {LINE};border-radius:10px;padding:8px 18px;display:flex;flex-direction:column">{txt}{tag_}</div>'
    o.append(f'<div style="display:flex;flex-direction:row;gap:10px;align-items:stretch">{bar}{gutter}{box_}</div>')
    col = RED if c.get("err") else INK
    wide = WIDE if c.get("wide") else (lambda t: t)
    oa = c.get("oattrs", {})
    for j, l in enumerate(c.get("out", [])):
        o.append(p(f"margin-left:85px;padding:0 20px;font-family:{MONO};font-size:{fs}px;line-height:1.45;white-space:pre;color:{col};align-self:flex-start", wide(e(l)), oa.get(j, "")))
    o.append('</div>')
    return o


def tag(x, y, text, color, order=None, size=28, lead=True, anim="rise", mono=False, w=None):
    """A label beside a code line or a picture: '← text', centred on y. No box."""
    ws = f"width:{w}px;white-space:normal;" if w else "white-space:nowrap;"
    fam = f"font-family:{MONO};" if mono else ""
    return p(f"position:absolute;left:{x:.0f}px;top:{y - size * 0.725:.0f}px;{ws}{fam}font-size:{size}px;font-weight:700;line-height:1.45;color:{color}",
             ("← " if lead else "") + text, bi(anim, order))


def tick(x1, y1, x2, y2, color, order=None, width=3, dot=True):
    """A thin leader line ending in a dot (Stageshow annotations: 1px-ish line, dot short of the object)."""
    d = f'<circle cx="{x2}" cy="{y2}" r="5" fill="{color}" stroke="none"/>' if dot else ""
    return (f'<svg{bi("fade", order)} viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible">'
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" stroke-linecap="round"/>{d}</svg>')


def arrow(x1, y1, x2, y2, color="#9AA1AE", order=None, width=4, kind="draw", head=16):
    """A straight arrow; kind draw makes the player draw it like a pen."""
    import math
    a = math.atan2(y2 - y1, x2 - x1)
    hx1, hy1 = x2 - head * math.cos(a - 0.45), y2 - head * math.sin(a - 0.45)
    hx2, hy2 = x2 - head * math.cos(a + 0.45), y2 - head * math.sin(a + 0.45)
    return (f'<svg{bi(kind, order)} viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible">'
            f'<g fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="M{x1:.0f},{y1:.0f} L{x2:.0f},{y2:.0f}"/><path d="M{hx1:.0f},{hy1:.0f} L{x2:.0f},{y2:.0f} L{hx2:.0f},{hy2:.0f}"/></g></svg>')


def strike(order, x1, x2, y, color=RED, width=5):
    """A pen line through a value that was overwritten or deleted."""
    return (f'<svg data-build-in="draw order {order}" viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible">'
            f'<path d="M{x1},{y + 3} L{x2},{y - 3}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round"/></svg>')


def cross(order, x, y, w, h, color=RED, width=6):
    """A pen X over a locker that was removed."""
    return (f'<svg data-build-in="draw order {order}" viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible">'
            f'<g fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round"><path d="M{x + 30},{y + 30} L{x + w - 30},{y + h - 30}"/><path d="M{x + w - 30},{y + 30} L{x + 30},{y + h - 30}"/></g></svg>')


def anchor(aid, x, y, w=10, h=10):
    """An invisible box a flying value starts from (data-from needs an element)."""
    return f'<div id="{aid}" style="position:absolute;left:{x:.0f}px;top:{y:.0f}px;width:{w:.0f}px;height:{h:.0f}px"></div>'


def mono(text, size=30, color=INK, bg=None, extra="", attrs=""):
    b = f"background:{bg};border-radius:10px;padding:2px 14px;" if bg else ""
    return p(f"font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.4;color:{color};white-space:pre;{b}{extra}", e(text), attrs)


def at(x, y, inner, attrs="", extra=""):
    return f'<div{attrs} style="position:absolute;left:{x}px;top:{y}px;{extra}">{inner}</div>'


# ---------- lockers: the dictionary picture used on every slide ----------
def locker(lid, key, val, x, y, w=260, h=200, color=K1, bg=K1BG, state="on", mode=None, fs=40, kfs=28, attrs="", vattrs="", kid=True):
    """One locker: the key is written on the door band, the value sits inside.
    state on / off (quiet gray) / ghost (dashed, removed). mode key dims the value, val dims the key."""
    on = state == "on"
    border = f"3px solid {color}" if on else ("3px dashed #C9CED8" if state == "ghost" else "3px solid #C9CED8")
    band_bg = (color if mode != "val" else "#ECEAE3") if on else "#ECEAE3"
    band_fg = ("#FFFFFF" if mode != "val" else GRAY) if on else GRAY
    body_bg = (bg if mode != "key" else CARD) if on else (CARD if state == "off" else "transparent")
    vcol = ("#B4B9C3" if mode == "key" else INK) if on else ("#B4B9C3" if state == "ghost" else SUB)
    kh = kfs + 30
    ids = f' id="{lid}-k"' if kid else ""
    return (f'<div id="{lid}"{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;border-radius:16px;border:{border};background:{body_bg};display:flex;flex-direction:column;overflow:hidden">'
            + p(f"height:{kh}px;flex:none;background:{band_bg};color:{band_fg};font-family:{MONO};font-size:{kfs}px;font-weight:700;line-height:{kh}px;text-align:center;white-space:pre", e(key), ids)
            + '<div style="flex:1;display:flex;align-items:center;justify-content:center;position:relative">'
            + p(f"font-family:{MONO};font-size:{fs}px;font-weight:700;color:{vcol};white-space:pre", e(val), f' id="{lid}-v"{vattrs}')
            + (f'<div style="position:absolute;right:12px;top:50%;width:8px;height:38px;margin-top:-19px;border-radius:4px;background:#D5D8DE"></div>' if state != "ghost" and w >= 170 else "")
            + '</div></div>')


def row_of(pre, pairs, x, y, w, h, gap, color, bg, **kw):
    """A row of lockers. kw passes per-locker options as lists or single values."""
    o = []
    for i, (k, v) in enumerate(pairs):
        opt = {a: (b[i] if isinstance(b, list) else b) for a, b in kw.items()}
        o.append(locker(f"{pre}{i}", k, v, x + i * (w + gap), y, w, h, color, bg, **opt))
    return o


def name_label(text, x, y, color, order=None, size=28):
    return p(f"position:absolute;left:{x}px;top:{y}px;font-family:{MONO};font-size:{size}px;font-weight:700;color:{color};white-space:nowrap", e(text), bi("fade", order))


def slots(pre, items, x, y, w=180, h=110, color=GRAY, bg=GBG, hi=(), fs=34, attrs=""):
    """List items as numbered boxes (chapter 13's picture)."""
    o = [f'<div{attrs} style="position:absolute;left:{x}px;top:{y}px;display:flex;flex-direction:row;gap:10px">']
    for i, it in enumerate(items):
        on = i in hi
        o.append('<div style="display:flex;flex-direction:column;align-items:center;gap:8px">'
                 + p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{color}", str(i))
                 + p(f"width:{w}px;height:{h}px;border-radius:14px;border:3px solid {color if on else '#C9CED8'};background:{bg if on else CARD};font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:{h - 6}px;text-align:center;color:{INK};white-space:pre", e(it), f' id="{pre}{i}"') + '</div>')
    o.append('</div>')
    return "".join(o)


def hair(x, y, w, color=LINE, order=None, h=2):
    return f'<div{bi("fade", order)} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{color}"></div>'


def fix(x, y, bad, good, order, size=30, note=None, gap=26):
    """The wrong code struck through, an arrow, the right code (no card)."""
    return (f'<div{bi("rise", order)} style="position:absolute;left:{x}px;top:{y}px;display:flex;flex-direction:row;align-items:center;gap:{gap}px">'
            + p(f"font-family:{MONO};font-size:{size}px;font-weight:700;color:{RED};text-decoration:line-through;text-decoration-thickness:3px;white-space:pre", e(bad))
            + f'<x-shape kind="arrow-right" style="width:52px;height:30px;flex:none;background:#B4B9C3"></x-shape>'
            + p(f"font-family:{MONO};font-size:{size}px;font-weight:700;color:{INK};background:#E6F4EC;border:3px solid {GR};border-radius:14px;padding:4px 18px;white-space:pre", e(good))
            + (p(f"font-size:26px;font-weight:700;color:{SUB};white-space:nowrap", e(note)) if note else "") + '</div>')


MENU = 'menu = {"coffee": 4500, "latte": 5000, "cake": 6500}'
M0 = [('"coffee"', "4500"), ('"latte"', "5000"), ('"cake"', "6500")]
NB = "basics.ipynb"

# =====================================================================
# cover
# =====================================================================
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#F2B27A;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
       '<h1 style="font-size:92px;font-weight:900;line-height:1.1;color:#F6F5F1">파이썬 기초 4<br>딕셔너리</h1>',
       '<p style="font-size:40px;line-height:1.4;color:#BFC6D4">번호 대신 키로<br>값을 찾고 바꾸기</p>']
cov.append(p(f"position:absolute;left:1010px;top:300px;font-family:{MONO};font-size:44px;font-weight:700;color:#9DBDEB;white-space:pre", e('menu["latte"]')))
cov.append(p(f"position:absolute;left:1500px;top:300px;font-family:{MONO};font-size:44px;font-weight:700;color:#E6E9EF;white-space:pre", "→ 5000"))
for i, (k, v) in enumerate(M0):
    on = i == 1
    cov.append(f'<div style="position:absolute;left:{1010 + i * 280}px;top:420px;width:260px;height:300px;border-radius:18px;border:3px solid {"#9DBDEB" if on else "#4A5262"};background:{"#26344D" if on else "#252B36"};display:flex;flex-direction:column;overflow:hidden">'
               + p(f"height:66px;flex:none;background:{'#9DBDEB' if on else '#3A4150'};color:{INK if on else '#BFC6D4'};font-family:{MONO};font-size:28px;font-weight:700;line-height:66px;text-align:center", e(k))
               + '<div style="flex:1;display:flex;align-items:center;justify-content:center">' + p(f"font-family:{MONO};font-size:52px;font-weight:700;color:{'#FFFFFF' if on else '#8A93A3'}", v) + '</div></div>')
cov.append(tick(1420, 372, 1420, 412, "#9DBDEB", dot=False))
W("cover", cov, "이번 챕터는 번호 대신 이름(키)으로 값을 찾는 딕셔너리예요. 13에서 리스트와 튜플에 주문을 담고, 14에서 in과 2차원 리스트를 봤어요. 1파트는 만들고 꺼내기, 2파트는 바꾸고 지우기, 3파트는 for로 둘러보기예요. 4파트는 리스트와 섞고, 5파트는 리스트·튜플과 비교한 뒤 카페 예제 세 개로 마무리해요. 모든 예제는 12~14에서 쓰던 노트북 셀에 이어서 적고 실행해요.", ("intro", "들어가기"))

ORDER.append("toc")   # written last, after page numbers are known

# =====================================================================
# ready: the notebook itself is the picture; the cursor shows what to open, in order
# =====================================================================
o = [sec("ready")] + head("들어가기", "14에서 쓰던 노트북에 이어서 적어요", JP)
BX, BY, BW = 96, 230, 1728
o.append(f'<div style="position:absolute;left:{BX}px;top:{BY}px;width:{BW}px;height:300px;background:#FFFFFF;border:2px solid {LINE};border-radius:22px;overflow:hidden">'
         f'<div style="height:84px;background:#ECEAE3;display:flex;flex-direction:row;align-items:center;padding:0 30px;gap:18px">'
         + p(f"font-size:28px;font-weight:700;color:{SUB}", "hello-uv", ' id="rd-folder"') + p(f"font-size:28px;color:#9AA1AE", "/")
         + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{INK}", NB, ' id="rd-file"')
         + '<div style="flex:1"></div>'
         + p(f"font-size:24px;font-weight:700;color:{GR};background:#E6F4EC;border-radius:10px;padding:6px 16px;white-space:nowrap", ".venv (Python 3.14.6)", ' id="rd-kernel"') + '</div>'
         f'<div style="position:absolute;left:40px;top:140px;width:1648px;display:flex;flex-direction:row;gap:12px;align-items:stretch">'
         f'<div style="width:7px;flex:none;border-radius:4px;background:{SEL}"></div>'
         + p(f"width:58px;flex:none;font-family:{MONO};font-size:22px;color:{GRAY};text-align:right;padding-top:22px", "[ ]")
         + f'<div id="rd-cell" style="flex:1;height:96px;background:#FFFFFF;border:3px solid {SEL};border-radius:12px;padding:22px 26px">'
         + p(f"font-family:{MONO};font-size:32px;color:{INK}", f'<span style="color:{SEL};font-weight:700">|</span>') + '</div></div></div>')
steps = [("rd-folder", "VS Code로 hello-uv 폴더를 열어요"), ("rd-file", "탐색기에서 basics.ipynb를 열어요"), ("rd-kernel", "오른쪽 위 커널이 .venv인지 봐요"), ("rd-cell", "셀에 적고 Shift+Enter로 실행해요")]
for i, (tid, text) in enumerate(steps, 1):
    x, y = 96 + ((i - 1) % 2) * 880, 600 + ((i - 1) // 2) * 100
    o.append(f'<div{bi("rise", i)} style="position:absolute;left:{x}px;top:{y}px;display:flex;flex-direction:row;align-items:center;gap:18px">'
             + p(f"width:56px;height:56px;flex:none;border-radius:50%;background:{JP};color:#FFFFFF;font-size:30px;font-weight:900;line-height:56px;text-align:center", str(i))
             + p(f"font-size:32px;font-weight:700;color:{INK};white-space:nowrap", e(text)) + '</div>')
    o.append(f'<div data-build-in="click order {i}" data-target="{tid}" style="position:absolute;left:0;top:0;width:2px;height:2px"></div>')
o.append(f'<div data-build-in="cursor-off order 5" style="position:absolute;left:0;top:0;width:1px;height:1px"></div>')
o.append(hair(96, 840, 1728))
o.append(p(f"position:absolute;left:96px;top:868px;width:1728px;font-size:28px;line-height:1.6;color:{SUB}",
           "기억이 안 나면 먼저 다시 봐요. &#160;노트북과 커널 <b style='color:" + INK + "'>09 · 25–27쪽</b> &#160;·&#160; f-string, 리스트, for <b style='color:" + INK + "'>13</b> &#160;·&#160; in, 2차원 리스트 <b style='color:" + INK + "'>14</b>"))
W("ready", o, "09에서 만든 hello-uv 폴더를 열고 12~14에서 쓰던 basics.ipynb에 이어서 적어요. 오른쪽 위 커널이 .venv인지 꼭 봐요. 13의 f-string과 리스트, 튜플, for, 14의 in을 그대로 써요. 셀 번호는 파트마다 [1]부터 다시 셌어요. 슬라이드의 출력은 tools/demo.sh가 hello-uv 커널에서 같은 셀을 실제로 실행한 결과예요.")

# =====================================================================
# part 1: make and read
# =====================================================================
# --- d-why: list by number, dictionary by key (step 1: why) ---
o = [sec("d-why")] + head(EB1, "번호 대신 키로 찾아요", K1)
ca = {"id": "c-w1", "lines": ['student = ["kim", 90, 85, 77]', "print(student[2])"], "n": 1, "out": ["85"]}
cb = {"id": "c-w2", "lines": ['student = {"name": "kim", "kor": 90,', '           "eng": 85, "math": 77}', 'print(student["eng"])'], "n": 2, "out": ["85"]}
o += cell(ca, 96, 230, 790)
o += row_of("w-a", [("0", '"kim"'), ("1", "90"), ("2", "85"), ("3", "77")], 940, 210, 206, 190, 14, GRAY, GBG, state=["off", "off", "on", "off"])
o.append(tag(940 + 2 * 220, 440, "2번이 영어라는 걸 외워야 해요", GRAY, 1, 26, lead=False))
o.append(spot(1, 940 + 2 * 220, 210, 206, 190, dim=0.45))
o.append(spot_off(2))
o += cell(cb, 96, 560, 790, sel=True, attrs=bi("rise", 2))
o += row_of("w-b", [('"name"', '"kim"'), ('"kor"', "90"), ('"eng"', "85"), ('"math"', "77")], 940, 560, 206, 190, 14, K1, K1BG, attrs=bi("rise", 2), kfs=24)
o.append(ring(3, 940 + 2 * 220, 560, 206, 190, K1))
o.append(tag(940 + 2 * 220 - 40, 800, "읽기만 해도 영어 점수예요", K1, 3, 26, lead=False))
o.append(caption("문에 적힌 이름이 키(key), 안에 든 것이 값(value)이에요.", 930, 3))
W("d-why", o, "리스트는 번호로, 딕셔너리는 이름(키)으로 값을 찾아요. 13에서 학생 한 명의 점수를 리스트에 담으면 student[2]처럼 번호로 꺼냈어요. 2번이 영어라는 건 코드를 쓴 사람이 외워 둬야 해요. 딕셔너리는 사물함처럼 칸마다 문에 이름을 붙여 둬요. 문에 적힌 이름을 키, 안에 든 것을 값이라고 불러요. student[\"eng\"]는 읽기만 해도 영어 점수인 걸 알아요. 결과는 둘 다 85예요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요. 출력은 실제로 실행한 결과예요.", ("make", "만들고 꺼내기"))

# --- d-big: where dictionaries live (step 2: big picture) ---
o = [sec("d-big")] + head(EB1, "메뉴판이 바로 딕셔너리 모양이에요", K1)
o.append(f'<div style="position:absolute;left:96px;top:230px;width:640px;height:560px;background:#2B3140;border-radius:24px;padding:44px 52px;display:flex;flex-direction:column;gap:26px">'
         + p("font-size:36px;font-weight:900;color:#F2B27A;text-align:center;letter-spacing:2px", "KANT 카페")
         + "".join(f'<div id="bd-r{i}" style="display:flex;flex-direction:row;align-items:baseline;gap:16px;height:84px;align-items:center">'
                   + p(f"font-size:44px;font-weight:700;color:#F6F5F1", k) + '<div style="flex:1;border-bottom:3px dotted #5A6172;margin-top:20px"></div>'
                   + p(f"font-family:{MONO};font-size:44px;font-weight:700;color:#F6F5F1", v) + '</div>'
                   for i, (k, v) in enumerate([("coffee", "4,500"), ("latte", "5,000"), ("cake", "6,500")])) + '</div>')
code_big = ['menu = {', '    "coffee": 4500,', '    "latte": 5000,', '    "cake": 6500,', '}']
for i, l in enumerate(code_big):
    o.append(p(f"position:absolute;left:1010px;top:{300 + i * 96}px;font-family:{MONO};font-size:46px;font-weight:700;color:{INK};white-space:pre", e(l), f' id="bd-c{i}"'))
for i in range(3):
    y = 230 + 44 + 54 + 26 + i * 110 + 42
    o.append(arrow(760, y, 1080, 300 + (i + 1) * 96 + 34, "#9AA1AE", 1))
o.append(p(f"position:absolute;left:1130px;top:736px;width:200px;text-align:center;font-size:30px;font-weight:700;color:{K1}", "메뉴 이름이 키", bi("rise", 2)))
o.append(p(f"position:absolute;left:1372px;top:736px;width:160px;text-align:center;font-size:30px;font-weight:700;color:{K1}", "가격이 값", bi("rise", 2)))
o.append(underline(2, 1120, 1340, 662, K1, 4))
o.append(underline(2, 1396, 1508, 662, K1, 4))
o.append(tick(1230, 730, 1230, 676, K1, 2, dot=False))
o.append(tick(1452, 730, 1452, 676, K1, 2, dot=False))
o.append(p(f"position:absolute;left:96px;top:850px;width:1728px;font-size:30px;line-height:1.5;color:{SUB}",
           "이름으로 값을 찾는 표는 딕셔너리로 담을 수 있어요. &#160;연락처는 <b style='color:" + INK + "'>이름 → 전화번호</b>, 설정은 <b style='color:" + INK + "'>항목 → 값</b>이에요.", bi("rise", 3)))
W("d-big", o, "메뉴판처럼 이름을 보고 값을 찾는 표는 그대로 딕셔너리로 옮길 수 있어요. 카페 메뉴판은 메뉴 이름 옆에 가격이 적혀 있어요. 손님은 몇 번째 줄인지 세지 않고 이름으로 가격을 찾아요. 이 모양을 코드로 옮기면 메뉴 이름이 키, 가격이 값인 딕셔너리가 돼요. 연락처의 이름과 전화번호, 프로그램 설정의 항목과 값도 같은 모양이에요. 이 덱은 메뉴판 menu를 계속 써요. 오른쪽처럼 줄을 나눠 적어도 같은 딕셔너리예요.")

# --- d-make: anatomy labelled on the code line itself (step 3: smallest example) ---
o = [sec("d-make")] + head(EB1, "중괄호 안에 키: 값을 쉼표로 이어요", K1)
cm = {"id": "c-m", "lines": [MENU, "print(menu)", "print(type(menu))", "print(len(menu))", "cart = {}", "print(cart)", "print(len(cart))"], "n": 3,
      "out": ["{'coffee': 4500, 'latte': 5000, 'cake': 6500}", "<class 'dict'>", "3", "{}", "0"]}
CL, CT = 96, 360
o += cell(cm, CL, CT, 1180, sel=True)
cx = lambda i: CL + 105 + i * 18
labels = [(7, 1, "중괄호", 300, K1), (8, 8, "키", 300, K1), (18, 4, "값", 300, K1), (16, 1, "콜론", 240, SUB), (22, 1, "쉼표", 240, SUB)]
for idx, ln, txt, y, col in labels:
    mid = cx(idx) + ln * 9
    order = 1 if col == K1 else 2
    o.append(p(f"position:absolute;left:{mid - 60}px;top:{y - 40}px;width:120px;text-align:center;font-size:28px;font-weight:700;color:{col}", txt, bi("rise", order)))
    o.append(tick(mid, y + 2, mid, CT + 6, col, order, 3, dot=False))
o.append(underline(1, cx(8), cx(16), CT + 50, K1, 4))
o.append(underline(1, cx(18), cx(22), CT + 50, K1, 4))
outs_tags = [(1, "dict는 dictionary(사전)의 줄임말"), (2, "키: 값 쌍이 3개"), (3, "빈 딕셔너리"), (4, "쌍이 0개")]
for j, t in outs_tags:
    o.append(tag(lx(CL, cm["out"][j]) + 40, oy(cm, CT, j), t, K1, 3, 26))
for i, (k, v) in enumerate(M0):
    o.append(locker(f"mk{i}", k, v, 1380, 360 + i * 190, 444, 170, K1, K1BG, fs=44, kfs=28, attrs=bi("rise", 4)))
o.append(name_label("menu", 1380, 310, K1, 4))
W("d-make", o, "딕셔너리는 중괄호 안에 키: 값을 적고, 쌍과 쌍 사이를 쉼표로 이어요. 메뉴 이름이 키, 가격이 값이에요. 키와 값 사이에는 콜론을 적어요. print로 찍으면 적은 순서대로 나와요. type은 dict라고 알려 주는데, dictionary(사전)의 줄임말이에요. 사전에서 단어를 찾으면 뜻이 나오듯 키로 값을 찾아요. len은 쌍의 개수라 3이에요. 빈 중괄호는 빈 딕셔너리예요. 출력은 실제로 실행한 결과예요.")

# --- d-key: the value leaves its locker and lands in the output ---
o = [sec("d-key")] + head(EB1, "대괄호에 키를 넣어 꺼내요", K1)
ck = {"id": "c-k1", "lines": ['print(menu["latte"])', 'price = menu["cake"]', "print(price * 2)"], "n": 4, "out": ["5000", "13000"],
      "oattrs": {0: ' id="k-o0" data-build-in="fly order 2" data-from="ky1-v"', 1: bi("rise", 3)}}
ce = {"id": "c-k2", "lines": ['menu["tea"]'], "n": 5, "out": ["KeyError: 'tea'"], "err": True}
o += cell(ck, 96, 220, 880, sel=True)
o += cell(ce, 1040, 220, 784, attrs=bi("rise", 4))
o.append(underline(1, lx(96, 'print(menu['), lx(96, 'print(menu["latte"'), ly(220, 0) + 22, K1, 4))
o.append(tag(lx(96, "13000") + 40, oy(ck, 220, 1), "꺼낸 값으로 바로 계산해요", K1, 3, 26))
o.append(underline(5, round(lx(1040, "KeyError: ")), round(lx(1040, "KeyError: 'tea'")), round(oy(ce, 220, 0) + 24), RED, 5))
o.append(tag(lx(1040, "KeyError: 'tea'") + 50, oy(ce, 220, 0), "찾던 키가 없어요", RED, 5, 26))
o += row_of("ky", M0, 96, 620, 552, 260, 36, K1, K1BG, state=["off", "on", "off"], fs=56, kfs=32)
o.append(name_label("menu", 96, 568, K1))
W("d-key", o, "딕셔너리에서 값을 꺼낼 때도 대괄호를 써요. 리스트는 대괄호 안에 번호를 넣었지만, 딕셔너리는 키를 넣어요. menu[\"latte\"]는 latte 칸의 값 5000이에요. 꺼낸 값은 숫자라서 변수에 담아 바로 계산할 수 있어요. 없는 키를 꺼내면 KeyError가 나요. 오류 마지막 줄에 찾던 키 'tea'가 함께 나와서 어느 키가 문제인지 알 수 있어요. 출력은 실제로 실행한 결과예요.")

# --- d-get ---
o = [sec("d-get")] + head(EB1, "get은 없는 키에도 오류 없이 답해요", K1)
cg = {"id": "c-g", "lines": ['print(menu.get("latte"))', 'print(menu.get("tea"))', 'print(menu.get("tea", 0))'], "n": 6, "out": ["5000", "None", "0"]}
GT = 220
o += cell(cg, 96, GT, 900, sel=True)
gtags = [("latte가 있으니 그 값", K1), ("tea가 없으면 None, 값이 없다는 뜻이에요", K1), ("없을 때 줄 값을 정해 둘 수 있어요", K1)]
for j, (t, c) in enumerate(gtags):
    o.append(tag(lx(96, "None") + 50, oy(cg, GT, j), t, c, j + 1, 28))
o.append(hair(96, 640, 1728))
o.append(p(f"position:absolute;left:96px;top:676px;font-size:28px;font-weight:700;color:{SUB}", "없는 키를 물었을 때", bi("fade", 4)))
o.append(at(96, 740, mono('menu["tea"]', 34, RED), bi("rise", 4)))
o.append(at(560, 740, mono("KeyError: 'tea'", 34, RED), bi("rise", 4)))
o.append(at(1060, 746, p(f"font-size:30px;font-weight:700;color:{INK}", "셀이 거기서 멈춰요"), bi("rise", 4)))
o.append(at(96, 830, mono('menu.get("tea", 0)', 34, GR), bi("rise", 5)))
o.append(at(560, 830, mono("0", 34, GR), bi("rise", 5)))
o.append(at(1060, 836, p(f"font-size:30px;font-weight:700;color:{INK}", "0을 받고 다음 줄로 넘어가요"), bi("rise", 5)))
o.append(box(5, 80, 818, 1560, 84, GR, 4, 12))
W("d-get", o, "get은 없는 키를 물어도 오류 없이 답해요. 키가 있으면 값을 돌려주고, 없으면 None을 돌려줘요. None은 값이 없다는 뜻의 파이썬 값이에요. 괄호 안에 쉼표 뒤로 값을 하나 더 적으면, 키가 없을 때 None 대신 그 값을 돌려줘요. 가격이나 개수처럼 숫자를 다룰 때는 0을 많이 적어요. 대괄호로 꺼내면 셀이 오류에서 멈추지만, get은 다음 줄로 넘어가요. 키가 꼭 있어야 하는 곳은 대괄호, 없을 수도 있는 곳은 get을 써요. 출력은 실제로 실행한 결과예요.")

# --- d-short: get beside the long original (read only) ---
o = [sec("d-short")] + head(EB1, "get은 긴 코드를 한 줄로 줄인 거예요", K1)
cs = {"id": "c-s1", "lines": ['print(menu["cakee"] if "cakee" in menu else 5000)', 'print(menu.get("cakee", 5000))', 'print(menu["cake"] if "cake" in menu else 5000)', 'print(menu.get("cake", 5000))'], "n": 7,
      "out": ["5000", "5000", "6500", "6500"], "dim": {0: "#8A93A3", 2: "#8A93A3"}}
ST = 250
o.append(p(f"position:absolute;left:201px;top:200px;font-size:24px;font-weight:700;color:{GRAY}", "회색 줄은 참고, 읽기만 해요. if는 17에서 배워요."))
o += cell(cs, 96, ST, 1110, sel=True)
for i, t in [(0, "긴 방법"), (1, "줄인 방법")]:
    pass
bx = 1240
for a, txt in [(0, "cakee는 키가 없어서 둘 다 5000"), (2, "cake는 키가 있어서 둘 다 6500")]:
    y1, y2 = ly(ST, a) - 16, ly(ST, a + 1) + 16
    o.append(f'<svg{bi("draw", 1 if a == 0 else 2)} viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible"><path d="M{bx},{y1:.0f} L{bx + 18},{y1:.0f} L{bx + 18},{y2:.0f} L{bx},{y2:.0f}" fill="none" stroke="{K1}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></svg>')
    o.append(tag(bx + 40, (y1 + y2) / 2, txt, K1, 1 if a == 0 else 2, 26, lead=False, w=520))
cs2 = {"id": "c-s2", "lines": ['sale = {"cake": None}', 'print(sale.get("cake", 5000))', 'print(sale.get("cakee", 5000))'], "n": 8, "out": ["None", "5000"]}
S2 = 690
o += cell(cs2, 96, S2, 760, attrs=bi("rise", 3))
o.append(tag(lx(96, "None") + 50, oy(cs2, S2, 0), "cake 키는 있어요. 값 None을 그대로 줘요", RED, 4, 28))
o.append(tag(lx(96, "None") + 50, oy(cs2, S2, 1), "기본값은 키가 없을 때만 써요", K1, 4, 28))
W("d-short", o, "get(키, 기본값)은 '키가 있으면 꺼내고, 없으면 기본값'을 한 줄로 줄인 메서드예요. 원래는 키가 menu에 있는지 in으로 묻고, 있으면 대괄호로 꺼내고, 없으면 5000을 쓰는 코드를 써야 해요. if와 else는 17에서 배우니 지금은 이런 뜻이라고 읽기만 해요. cakee는 오타라 키가 없어서 두 줄 모두 5000, cake는 키가 있어서 두 줄 모두 6500이에요. 주의할 점이 하나 있어요. 기본값은 키가 없을 때만 써요. sale처럼 cake 키가 있고 값이 None이면 None이 그대로 나와요. 출력은 실제로 실행한 결과예요.")

# =====================================================================
# part 2: change
# =====================================================================
o = [sec("d-add")] + head(EB2, "없는 키면 추가, 있는 키면 수정이에요", K2)
ca2 = {"id": "c-a", "lines": [MENU, 'menu["tea"] = 4000', "print(menu)", 'menu["latte"] = 5500', "print(menu)", "print(len(menu))"], "n": 1,
       "out": ["{'coffee': 4500, 'latte': 5000, 'cake': 6500, 'tea': 4000}", "{'coffee': 4500, 'latte': 5500, 'cake': 6500, 'tea': 4000}", "4"]}
AT = 200
o += cell(ca2, 96, AT, 1330, sel=True)
o.append(tag(lx(96, 'menu["tea"] = 4000') + 40, ly(AT, 1), "tea 키가 없어서 새 칸이 생겨요", K2, 1, 26))
o.append(tag(lx(96, 'menu["latte"] = 5500') + 40, ly(AT, 3), "latte 키가 있어서 값만 바뀌어요", K2, 2, 26))
o.append(mark(3, lx(96), oy(ca2, AT, 2), tw("4"), K2))
o.append(tag(lx(96, "4") + 50, oy(ca2, AT, 2), "칸은 4개 그대로예요", K2, 3, 26))
LY_ = 690
o += row_of("ad", [('"coffee"', "4500"), ('"latte"', "5000"), ('"cake"', "6500")], 96, LY_, 330, 210, 24, K2, K2BG, state=["off", "on", "off"], fs=48, kfs=28)
o.append(name_label("menu", 96, 640, K2))
o.append(anchor("a-l1", 96 + 105, ly(AT, 1) - 20, tw('menu["tea"] = 4000'), 40))
o.append(anchor("a-l3", 96 + 105, ly(AT, 3) - 20, tw('menu["latte"] = 5500'), 40))
o.append(locker("ad3", '"tea"', "4000", 96 + 3 * 354, LY_, 330, 210, K2, K2BG, fs=48, kfs=28, attrs=' data-build-in="fly order 1" data-from="a-l1"'))
# latte: the old value is struck, the new one flies in from the code line
o.append(locker("ad1n", '"latte"', "5500", 96 + 354, LY_, 330, 210, K2, K2BG, fs=48, kfs=28, attrs=' data-build-in="fly order 2" data-from="a-l3"', kid=False))
o.append(p(f"position:absolute;left:{96 + 354 + 230}px;top:{LY_ + 64}px;font-family:{MONO};font-size:26px;font-weight:700;color:#9AA1AE;text-decoration:line-through", "5000", bi("fade", 2)))
W("d-add", o, "딕셔너리에 값을 넣는 문법은 menu[키] = 값 하나예요. 키가 없으면 새 칸이 생기고, 키가 이미 있으면 그 칸의 값만 바뀌어요. tea는 없던 키라 맨 뒤에 추가됐어요. latte는 있던 키라 5000이 5500으로 바뀌었어요. 칸은 네 개 그대로라 len은 4예요. 리스트는 append로 더했지만, 딕셔너리는 대괄호에 새 키를 넣으면 돼요. 이 파트도 새 커널이라 menu를 다시 만들고 셀 번호가 [1]부터예요. 출력은 실제로 실행한 결과예요.", ("change", "바꾸고 지우기"))

o = [sec("d-dup")] + head(EB2, "키는 겹치지 않아요. 값은 겹쳐도 돼요", K2)
cd = {"id": "c-d", "lines": ['dup = {"latte": 5000, "latte": 5500}', "print(dup)", "print(len(dup))", 'score = {"kim": 90, "lee": 90, "park": 90}', "print(score)"], "n": 2,
      "out": ["{'latte': 5500}", "1", "{'kim': 90, 'lee': 90, 'park': 90}"]}
DT = 210
o += cell(cd, 96, DT, 1000, sel=True)
o.append(name_label("dup", 1200, 210, K2))
o.append(locker("dp", '"latte"', "5500", 1200, 260, 360, 230, K2, K2BG, fs=56, kfs=30, attrs=bi("rise", 1)))
o.append(p(f"position:absolute;left:1600px;top:330px;font-family:{MONO};font-size:40px;font-weight:700;color:#9AA1AE", "5000", bi("rise", 1)))
o.append(strike(2, 1590, 1712, 360))
o.append(tag(1600, 440, "먼저 넣은 값은 덮어써요", K2, 2, 26, lead=False))
o.append(name_label("score", 96, 660, K2, 3))
o += row_of("sc", [('"kim"', "90"), ('"lee"', "90"), ('"park"', "90")], 96, 710, 330, 200, 24, K2, K2BG, attrs=bi("rise", 3), fs=52, kfs=28)
for k in range(3):
    o.append(underline(4, 96 + k * 354 + 120, 96 + k * 354 + 210, 872, OR, 5))
o.append(tag(1200, 810, "값은 같아도 키가 다르면 칸이 따로예요", K2, 4, 28, lead=False))
W("d-dup", o, "딕셔너리의 키는 겹치지 않고, 값은 겹쳐도 돼요. 처음부터 같은 키를 두 번 적어도 오류는 나지 않고, 마지막에 적은 5500만 남아요. 그래서 len이 1이에요. 앞 장에서 latte를 5500으로 바꾼 것과 같은 일이에요. kim, lee, park이 모두 90점이어도 키가 달라서 칸이 세 개예요. 사물함 이름은 하나씩이지만, 안에 든 물건은 같아도 되는 것과 같아요. 출력은 실제로 실행한 결과예요.")

o = [sec("d-del")] + head(EB2, "del과 pop으로 지워요", K2)
cx_ = {"id": "c-x", "lines": ['del menu["tea"]', "print(menu)", 'price = menu.pop("cake")', "print(price)", "print(menu)"], "n": 3,
       "out": ["{'coffee': 4500, 'latte': 5500, 'cake': 6500}", "6500", "{'coffee': 4500, 'latte': 5500}"],
       "oattrs": {1: ' id="x-o1" data-build-in="fly order 2" data-from="dl2-v"'}}
XT = 200
o += cell(cx_, 96, XT, 1000, sel=True)
o.append(tag(lx(96, 'del menu["tea"]') + 40, ly(XT, 0), "키와 값을 같이 지워요", K2, 1, 26))
o.append(tag(lx(96, 'price = menu.pop("cake")') + 40, ly(XT, 2), "지우면서 값을 돌려줘요", K2, 2, 26))
cx2 = {"id": "c-x2", "lines": ['del menu["tea"]'], "n": 4, "out": ["KeyError: 'tea'"], "err": True}
o += cell(cx2, 1180, 200, 644, attrs=bi("rise", 3))
o.append(tag(1180 + 105, 372, "없는 키를 지우면 꺼낼 때와 같은 오류예요", RED, 3, 24, lead=False))
DLY = 680
o += row_of("dl", [('"coffee"', "4500"), ('"latte"', "5500"), ('"cake"', "6500"), ('"tea"', "4000")], 96, DLY, 400, 210, 42, K2, K2BG, fs=48, kfs=28)
o.append(name_label("menu", 96, 630, K2))
o.append(cross(1, 96 + 3 * 442, DLY, 400, 210))
o.append(cross(2, 96 + 2 * 442, DLY, 400, 210))
o.append(caption("13의 리스트 pop은 번호를, 딕셔너리 pop은 키를 넣어요.", 950, 4))
W("d-del", o, "del 뒤에 menu[키]를 적으면 그 키와 값이 함께 사라져요. pop도 지우는데, 지운 값을 돌려줘서 변수에 담을 수 있어요. cake의 6500이 price에 들어갔어요. 13에서 리스트의 pop은 번호를 넣었어요. 딕셔너리의 pop은 키를 넣어요. 이미 지운 tea를 한 번 더 지우면 KeyError가 나요. 꺼낼 때와 같은 오류예요. 출력은 실제로 실행한 결과예요.")

FS = 34
o = [sec("d-in")] + head(EB2, "in은 키 쪽만 봐요", K2)
ci = {"id": "c-i", "lines": ['print("latte" in menu)', 'print("tea" in menu)', 'print("tea" not in menu)', "print(5500 in menu)", "print(len(menu))"], "n": 5,
      "out": ["True", "False", "True", "False", "2"]}
IT = 210
o += cell(ci, 96, IT, 860, sel=True)
itags = [("latte는 키예요", K2), ("tea는 앞 장에서 지웠어요", K2), ("not in은 반대로 답해요", K2), ("5500은 값이라 안 봐요", RED), ("남은 쌍은 2개", K2)]
for j, (t, c) in enumerate(itags):
    o.append(tag(lx(96, "False") + 40, oy(ci, IT, j), t, c, 2 if j == 3 else 1, 28))
o.append(name_label("menu", 1040, 210, K2))
o += row_of("in", [('"coffee"', "4500"), ('"latte"', "5500")], 1040, 260, 380, 280, 24, K2, K2BG, mode="key", fs=56, kfs=32)
o.append(spot(1, 1040, 260, 784, 62, pad=10, r=14, dim=0.4))
o.append(spot_off(2))
o.append(mark(2, lx(96), oy(ci, IT, 3), tw("False"), RED))
o.append(hair(1040, 620, 784))
o.append(p(f"position:absolute;left:1040px;top:650px;font-size:28px;font-weight:700;color:{SUB}", "값에서 찾으려면", bi("rise", 3)))
o.append(at(1040, 700, mono("5500 in menu.values()", 38, K3), bi("rise", 3)))
o.append(at(1040, 770, p(f"font-size:26px;font-weight:700;color:{GRAY}", "values()는 3파트에서 봐요"), bi("rise", 3)))
W("d-in", o, "딕셔너리에 in을 쓰면 키 쪽만 찾아요. 14에서 in은 들어 있는지 True, False로 답한다고 했어요. latte는 키라 True고, tea는 앞 장에서 지워서 False예요. not in도 그대로 써요. 5500은 latte의 값이지만 키가 아니라서 False예요. 값에서 찾고 싶으면 3파트에서 볼 menu.values()에 in을 써요. 17에서 배울 if와 함께 쓰면 키가 있을 때만 꺼내는 코드를 만들어요. 출력은 실제로 실행한 결과예요.")
FS = 30

# =====================================================================
# part 3: browse
# =====================================================================
o = [sec("d-views")] + head(EB3, "keys, values, items로 모아 봐요", K3)
cv = {"id": "c-v", "lines": [MENU, "print(menu.keys())", "print(menu.values())", "print(menu.items())", "print(list(menu.keys()))"], "n": 1,
      "out": ["dict_keys(['coffee', 'latte', 'cake'])", "dict_values([4500, 5000, 6500])", "dict_items([('coffee', 4500), ('latte', 5000), ('cake', 6500)])", "['coffee', 'latte', 'cake']"]}
VT = 200
o += cell(cv, 96, VT, 1728, sel=True)
vtags = [(0, "키만"), (1, "값만"), (2, "(키, 값) 튜플"), (3, "보통 리스트")]
for j, t in vtags:
    o.append(tag(lx(96, cv["out"][j]) + 36, oy(cv, VT, j), t, K3, j + 1, 28))
GY = 760
for g, (lbl, md) in enumerate([("keys()", "key"), ("values()", "val"), ("items()", None)]):
    gx = 96 + g * 590
    o.append(name_label(lbl, gx, GY - 50, K3, g + 1))
    o += row_of(f"vw{g}-", M0, gx, GY, 168, 180, 12, K3, K3BG, mode=md, fs=38, kfs=22, attrs=bi("rise", g + 1))
W("d-views", o, "keys는 키만, values는 값만, items는 (키, 값) 쌍을 모아요. items는 키와 값을 튜플 하나로 묶어서 모아요. 출력의 dict_keys, dict_values, dict_items는 딕셔너리에서 꺼내 보여 주는 모양이라는 뜻이에요. 보통 리스트가 필요하면 13에서 배운 list()로 감싸요. 이 파트도 새 커널이라 menu를 다시 만들어요. 출력은 실제로 실행한 결과예요.", ("browse", "둘러보기"))

o = [sec("d-list")] + head(EB3, "list()로 바꾸면 번호로 꺼낼 수 있어요", K3)
cn = {"id": "c-n", "lines": ["keys = list(menu.keys())", "print(keys)", "print(keys[0])", "print(list(menu.values())[-1])", "pair = list(menu.items())[1]", "print(pair)", "print(pair[0], pair[1])"], "n": 2,
      "out": ["['coffee', 'latte', 'cake']", "coffee", "6500", "('latte', 5000)", "latte 5000"]}
NT = 200
o += cell(cn, 96, NT, 960, sel=True)
ntags = [(1, "키 0번", 2), (2, "값 맨 뒤", 2), (3, "1번 쌍은 튜플", 3), (4, "튜플도 번호로 꺼내요", 3)]
for j, t, od in ntags:
    o.append(tag(lx(96, "('latte', 5000)") + 40, oy(cn, NT, j), t, K3, od, 26))
o.append(p(f"position:absolute;left:1170px;top:216px;font-size:26px;font-weight:700;color:{K3}", "list(menu.keys())", bi("fade", 1)))
o.append(slots("ls", ["coffee", "latte", "cake"], 1170, 270, 196, 110, K3, K3BG, hi=(0,), fs=32, attrs=bi("rise", 1)))
o.append(p(f"position:absolute;left:1170px;top:470px;font-size:26px;font-weight:700;color:{K3}", "list(menu.items())", bi("fade", 3)))
o.append(slots("li", ["('coffee', 4500)", "('latte', 5000)", "('cake', 6500)"], 1170, 524, 210, 96, K3, K3BG, hi=(1,), fs=21, attrs=bi("rise", 3)))
cn2 = {"id": "c-n2", "lines": ["menu.keys()[0]"], "n": 3, "out": ["TypeError: 'dict_keys' object is not subscriptable"], "err": True}
N2 = 820
o += cell(cn2, 96, N2, 1100, attrs=bi("rise", 4))
o.append(underline(4, lx(96, "TypeError: 'dict_keys' object is "), lx(96, "TypeError: 'dict_keys' object is not subscriptable"), oy(cn2, N2, 0) + 24, RED, 5))
o.append(tag(1250, oy(cn2, N2, 0), "번호를 못 붙여요. list()로 먼저 바꿔요", RED, 4, 26, lead=False))
W("d-list", o, "keys, values, items로 모은 것은 list()로 바꿔야 번호로 꺼낼 수 있어요. 13에서 배운 list()로 감싸면 보통 리스트가 돼서 [0], [-1]처럼 번호로 꺼내요. items()를 리스트로 바꾸면 값 하나하나가 (키, 값) 튜플이에요. 그래서 [1]로 꺼낸 pair에 다시 [0], [1]을 붙이면 키와 값이 나와요. menu.keys()[0]처럼 바로 번호를 붙이면 TypeError가 나요. subscriptable은 번호를 붙여 꺼낼 수 있다는 뜻이에요. 첫 번째 메뉴처럼 순서가 필요할 때만 쓰고, 보통은 menu[\"latte\"]처럼 키로 꺼내요. 출력은 실제로 실행한 결과예요.")

o = [sec("d-for")] + head(EB3, "for로 한 쌍씩 꺼내요", K3)
cf1 = {"id": "c-f1", "lines": ["for name in menu:", "    print(name)"], "n": 4, "out": ["coffee", "latte", "cake"]}
cf2 = {"id": "c-f2", "lines": ["for name, price in menu.items():", '    print(f"{name:<8}{price:>6,}원")'], "n": 5, "out": ["coffee   4,500원", "latte    5,000원", "cake     6,500원"], "wide": True}
o += cell(cf1, 96, 200, 640)
o.append(tag(lx(96, "coffee") + 50, oy(cf1, 200, 1), "딕셔너리를 그대로 넣으면 키만 나와요", K3, None, 26))
F2 = 520
o += cell(cf2, 96, F2, 900, sel=True, attrs=bi("rise", 1))
for j, (k, v) in enumerate([("coffee", 4500), ("latte", 5000), ("cake", 6500)]):
    o.append(tag(lx(96, "coffee   4,500", wide=True) + 90, oy(cf2, F2, j), f'name = "{k}", price = {v}', K3, j + 2, 26, mono=True))
# the first pair splits into name and price
o.append(at(1150, 250, mono('("coffee", 4500)', 40, K3, K3BG, attrs=' id="f-pair"'), bi("rise", 1)))
o.append(arrow(1270, 330, 1210, 410, K3, 2))
o.append(arrow(1440, 330, 1550, 410, K3, 2))
for k, (nm, v) in enumerate([("name", '"coffee"'), ("price", "4500")]):
    bx_ = 1120 + k * 370
    o.append(f'<div id="f-v{k}" data-build-in="fly order 2" data-from="f-pair" style="position:absolute;left:{bx_}px;top:420px;width:340px;height:180px;background:{CARD};border:3px solid {K3};border-radius:20px;overflow:hidden;display:flex;flex-direction:column">'
             + p(f"height:58px;flex:none;background:{K3};color:#FFFFFF;font-family:{MONO};font-size:28px;font-weight:700;line-height:58px;padding:0 22px", nm)
             + '<div style="flex:1;display:flex;align-items:center;justify-content:center">' + p(f"font-family:{MONO};font-size:44px;font-weight:700;color:{INK}", e(v)) + '</div></div>')
W("d-for", o, "for 뒤에 변수를 두 개 적고 items()를 넣으면 키와 값을 한 쌍씩 꺼내요. 딕셔너리를 for에 그대로 넣으면 키만 하나씩 나와요. items()의 값 하나는 (키, 값) 튜플이라서 name과 price에 나눠 담겨요. 13에서 for menu, price, qty in orders:로 튜플을 나눠 담은 것과 같은 모양이에요. 출력의 칸 맞추기와 콤마는 13의 1파트 f-string이에요. 출력은 실제로 실행한 결과예요.")

o = [sec("d-calc")] + head(EB3, "values()에도 sum, max, in을 써요", K3)
cc = {"id": "c-c", "lines": ["print(sum(menu.values()))", "print(max(menu.values()))", "print(5000 in menu.values())", "print(sorted(menu))"], "n": 6,
      "out": ["16000", "6500", "True", "['cake', 'coffee', 'latte']"]}
CT2 = 210
o += cell(cc, 96, CT2, 720, sel=True)
ctags = [(0, "값을 모두 더해요"), (1, "가장 큰 값"), (2, "값 쪽에서 찾아요"), (3, "키만 abc 순으로 정렬해요")]
for j, t in ctags:
    o.append(tag(lx(96, "['cake', 'coffee', 'latte']") + 40 if j == 3 else lx(96, "16000") + 40, oy(cc, CT2, j), t, K3, j + 1, 26))
o.append(name_label("menu.values()", 1210, 210, K3))
o += row_of("cv", M0, 1210, 260, 196, 180, 14, K3, K3BG, mode="val", fs=40, kfs=24)
o.append(box(1, 1210, 260 + 54, 616, 126, K3, 4, 12))
o.append(hair(96, 720, 1728))
o.append(p(f"position:absolute;left:96px;top:752px;font-size:28px;font-weight:700;color:{SUB}", "13에서 리스트에 쓰던 함수 그대로예요", bi("fade", 5)))
o.append(at(96, 812, mono("sum([4500, 5000, 6500])", 34, GRAY), bi("rise", 5)))
o.append(at(800, 812, mono("sum(menu.values())", 34, K3), bi("rise", 5)))
o.append(at(1300, 818, p(f"font-size:30px;font-weight:700;color:{INK}", "둘 다 16000"), bi("rise", 5)))
W("d-calc", o, "values()로 모은 값에는 13에서 리스트에 쓴 sum, max를 그대로 써요. 메뉴 가격을 모두 더하면 16000, 가장 비싼 값은 6500이에요. 2파트에서 in은 키만 본다고 했어요. 값에서 찾으려면 values()에 in을 써요. sorted에 딕셔너리를 그대로 넣으면 키만 abc 순으로 정렬한 리스트가 나와요. 딕셔너리 자체는 바뀌지 않아요. 출력은 실제로 실행한 결과예요.")

o = [sec("d-getuse")] + head(EB3, "get은 없을 수도 있는 키에 써요", K3)
cu1 = {"id": "c-u1", "lines": ['settings = {"name": "kim"}', 'print(settings.get("name", "guest"))', 'print(settings.get("lang", "ko"))', 'print(settings.get("theme", "light"))', "print(settings)"], "n": 7,
       "out": ["kim", "ko", "light", "{'name': 'kim'}"]}
cu2 = {"id": "c-u2", "lines": ['cart = {"coffee": 2, "tea": 1}', "total = 0", "for name, qty in cart.items():", "    price = menu.get(name, 0)", "    print(name, qty, price * qty)", "    total += price * qty", 'print("합계:", total)'], "n": 8,
       "out": ["coffee 2 9000", "tea 1 0", "합계: 9000"]}
o += cell(cu1, 96, 200, 800)
o.append(tag(lx(96, "light") + 40, oy(cu1, 200, 1), "lang이 없어서 기본값", K3, 1, 26))
o.append(tag(lx(96, "{'name': 'kim'}") + 40, oy(cu1, 200, 3), "settings는 그대로예요", K3, 1, 26))
o += cell(cu2, 960, 200, 864, sel=True, attrs=bi("rise", 2))
o.append(tag(lx(960, "coffee 2 9000") + 40, oy(cu2, 200, 1), "메뉴판에 없으면 0원", K3, 2, 26))
o.append(hair(96, 760, 1728))
o.append(fix(96, 800, "price = menu[name]", "price = menu.get(name, 0)", 3, 32, "tea에서 KeyError로 멈추지 않아요"))
W("d-getuse", o, "get은 키가 없을 수도 있는 곳에 써요. 첫째는 설정값이에요. 사용자가 이름만 적고 언어와 테마는 적지 않았으면, get의 두 번째 값으로 정해 둔 기본값을 써요. get은 꺼내기만 해서 settings는 바뀌지 않아요. 둘째는 장바구니예요. 메뉴판에 없는 tea가 들어와도 menu.get(name, 0)은 0을 줘서 for가 끝까지 돌아요. menu[name]으로 꺼냈다면 tea에서 KeyError가 나고 셀이 멈춰요. 출력은 실제로 실행한 결과예요.")

o = [sec("d-count")] + head(EB3, "get으로 개수를 세요", K3)
cq = {"id": "c-q1", "lines": ['words = "coffee latte coffee cake coffee latte".split()', "count = {}", "for w in words:", "    count[w] = count.get(w, 0) + 1", "print(count)", 'print(count["coffee"])'], "n": 9,
      "out": ["{'coffee': 3, 'latte': 2, 'cake': 1}", "3"]}
o += cell(cq, 96, 200, 1100, sel=True)
TX0 = 1250
hd = [("w", 0), ("count.get(w, 0)", 170), ("넣는 값", 420)]
for t, dx in hd:
    o.append(p(f"position:absolute;left:{TX0 + dx}px;top:206px;font-family:{MONO if t != '넣는 값' else SANS};font-size:22px;font-weight:700;color:{GRAY}", e(t)))
o.append(hair(TX0, 246, 574, INK))
steps_ = [("coffee", 0), ("latte", 0), ("coffee", 1), ("cake", 0), ("coffee", 2), ("latte", 1)]
for i, (w_, g) in enumerate(steps_):
    y = 256 + i * 58
    o.append(f'<div{bi("rise", i // 2 + 1)} style="position:absolute;left:{TX0}px;top:{y}px;width:574px;height:58px;border-bottom:2px solid {LINE};display:flex;flex-direction:row;align-items:center">'
             + p(f"width:170px;flex:none;font-family:{MONO};font-size:24px;font-weight:700;color:{INK}", e(f'"{w_}"'))
             + p(f"width:250px;flex:none;font-family:{MONO};font-size:24px;font-weight:700;color:{GRAY if g == 0 else INK}", str(g))
             + p(f"flex:1;font-family:{MONO};font-size:24px;font-weight:700;color:{K3}", f"{g} + 1 = {g + 1}") + '</div>')
o += row_of("cq", [('"coffee"', "3"), ('"latte"', "2"), ('"cake"', "1")], TX0, 660, 182, 170, 14, K3, K3BG, attrs=bi("rise", 4), fs=48, kfs=24)
o.append(name_label("count", TX0, 612, K3, 4))
cq2 = {"id": "c-q2", "lines": ["votes = {}", 'votes["coffee"] = votes["coffee"] + 1'], "n": 10, "out": ["KeyError: 'coffee'"], "err": True}
Q2 = 640
o += cell(cq2, 96, Q2, 1100, attrs=bi("rise", 5))
o.append(tag(lx(96, "KeyError: 'coffee'") + 40, oy(cq2, Q2, 0), "처음엔 아무 키도 없어요", RED, 5, 26))
o.append(p(f"position:absolute;left:96px;top:860px;font-size:22px;font-weight:700;color:{GRAY}", "참고, 읽기만 · get이 줄인 원래 코드 (if는 17에서)", bi("fade", 6)))
o.append(at(96, 898, mono("count[w] = (count[w] if w in count else 0) + 1", 26, "#8A93A3"), bi("rise", 6)))
W("d-count", o, "count[w] = count.get(w, 0) + 1 한 줄로 몇 번 나왔는지 세요. 빈 딕셔너리 count에서 시작해요. for로 단어를 하나씩 꺼내서 count.get(w, 0) + 1을 다시 그 키에 넣어요. 처음 나온 단어는 키가 없어서 get이 0을 주고, 1이 들어가요. 두 번째부터는 지금까지 센 값에 1을 더해요. 2파트에서 본 것처럼 없는 키면 추가, 있는 키면 수정이라 한 줄로 둘 다 돼요. 대괄호로 꺼내면 처음 나온 키에서 KeyError가 나요. 맨 아래 회색 줄은 get이 줄여 준 원래 코드예요. 키가 있으면 그 값, 없으면 0에 1을 더해요. if는 17에서 배우니 읽기만 해요. 출력은 실제로 실행한 결과예요.")

# =====================================================================
# part 4: mix with lists
# =====================================================================
o = [sec("x-listval")] + head(EB4, "값에 리스트를 넣을 수 있어요", K4)
cl = {"id": "c-l", "lines": ['scores = {"kim": [90, 85, 77],', '          "lee": [70, 95, 88],', '          "park": [60, 75, 99]}', 'print(scores["lee"])', 'print(scores["lee"][1])', "for name, s in scores.items():", "    print(name, sum(s), max(s))"], "n": 1,
      "out": ["[70, 95, 88]", "95", "kim 252 90", "lee 253 95", "park 234 99"]}
LT = 200
o += cell(cl, 96, LT, 900, sel=True)
o.append(tag(lx(96, "[70, 95, 88]") + 40, oy(cl, LT, 0), "키로 리스트를 꺼내요", K4, 1, 26))
o.append(tag(lx(96, "[70, 95, 88]") + 40, oy(cl, LT, 1), "그 리스트의 1번", K4, 2, 26))
o.append(tag(lx(96, "park 234 99") + 40, oy(cl, LT, 3), "s가 리스트라 sum, max를 써요", K4, 3, 26))
o.append(name_label("scores", 1060, 200, K4))
o += row_of("lv", [('"kim"', "[90, 85, 77]"), ('"lee"', "[70, 95, 88]"), ('"park"', "[60, 75, 99]")], 1060, 250, 246, 160, 13, K4, K4BG, state=["off", "on", "off"], fs=24, kfs=24)
o.append(slots("lvs", ["70", "95", "88"], 1150, 520, 160, 110, K4, K4BG, hi=(1,), fs=40, attrs=' data-build-in="fly order 1" data-from="lv1-v"'))
o.append(arrow(1060 + 259 + 123, 420, 1060 + 259 + 123, 500, K4, 1))
o.append(box(2, 1150 + 170 - 8, 520 + 42 - 8, 176, 126, K4, 4, 18))
o.append(hair(1060, 720, 764))
o.append(p(f"position:absolute;left:1060px;top:746px;font-size:26px;font-weight:700;color:{SUB}", "14와 같은 점수를 찾을 때", bi("fade", 4)))
o.append(at(1060, 796, mono("scores[1][1]", 32, GRAY) + p(f"font-size:24px;font-weight:700;color:{GRAY};margin-top:6px", "14 · 1번 학생이 lee라는 걸 외워요"), bi("rise", 4)))
o.append(at(1060, 896, mono('scores["lee"][1]', 32, K4), bi("rise", 4)))
W("x-listval", o, "값 자리에 리스트를 넣으면 키로 한 겹, 번호로 한 겹 더 꺼내요. 학생 이름을 키로, 세 과목 점수 리스트를 값으로 담았어요. scores[\"lee\"]는 lee의 점수 리스트예요. 거기에 [1]을 붙이면 그 리스트의 1번, 영어 95점이에요. 14의 scores[1][1]과 같은 점수를 이번에는 이름으로 찾았어요. for로 items()를 돌면 s에 리스트가 들어가서 sum, max를 바로 써요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요. 출력은 실제로 실행한 결과예요.", ("mix", "리스트와 섞기"))


def order_rows(pre, x, y, rows, w=136, h=96, gap=8, hi_row=None, hi_key=None, order=None, rgap=118, keys=("menu", "price", "qty")):
    """A list of order dictionaries: index on the left, one row of small lockers per order."""
    o = []
    for i, vals in enumerate(rows):
        yy = y + i * rgap
        on = hi_row is None or hi_row == i
        o.append(p(f"position:absolute;left:{x}px;top:{yy + h / 2 - 20:.0f}px;width:40px;text-align:right;font-family:{MONO};font-size:28px;font-weight:700;color:{K4 if on else GRAY}", str(i), bi("rise", order)))
        for k, (kk, vv) in enumerate(zip(keys, vals)):
            st = "on" if (on and (hi_key is None or hi_key == k)) else "off"
            o.append(locker(f"{pre}{i}-{k}", f'"{kk}"', vv, x + 60 + k * (w + gap), yy, w, h, K4, K4BG, state=st, fs=22, kfs=18, attrs=bi("rise", order), kid=False))
    return o


ORD3 = [('"coffee"', "4500", "2"), ('"latte"', "5000", "1"), ('"cake"', "6500", "3")]
o = [sec("x-dictlist")] + head(EB4, "딕셔너리를 리스트에 담으면 주문 목록이 돼요", K4)
co = {"id": "c-o", "lines": ['orders = [{"menu": "coffee", "price": 4500, "qty": 2},', '          {"menu": "latte", "price": 5000, "qty": 1},', '          {"menu": "cake", "price": 6500, "qty": 3}]',
                             "print(len(orders))", "print(orders[1])", 'print(orders[1]["menu"])', 'print(orders[2]["price"] * orders[2]["qty"])'], "n": 2,
      "out": ["3", "{'menu': 'latte', 'price': 5000, 'qty': 1}", "latte", "19500"],
      "oattrs": {2: ' id="o-o2" data-build-in="fly order 2" data-from="od1-0"'}}
OT = 200
o += cell(co, 96, OT, 1150, sel=True)
o.append(tag(lx(96, "latte") + 40, oy(co, OT, 2), "바깥은 [번호], 안쪽은 [키]", K4, 2, 26))
o.append(name_label("orders", 1320, 200, K4))
o += order_rows("od", 1300, 250, ORD3, w=146, h=104, rgap=124)
o.append(spot(1, 1300, 250 + 124, 522, 104, pad=10, dim=0.45))
o.append(spot_off(2))
o.append(box(2, 1360 - 8, 250 + 124 - 8, 162, 120, K4, 4, 18))
o.append(hair(1300, 680, 524))
o.append(p(f"position:absolute;left:1300px;top:704px;font-size:26px;font-weight:700;color:{SUB}", "13과 비교해요", bi("fade", 3)))
o.append(at(1300, 752, mono("orders[1][0]", 32, GRAY) + p(f"font-size:24px;font-weight:700;color:{GRAY};margin-top:4px", "13 · 0번이 메뉴라는 걸 외워요"), bi("rise", 3)))
o.append(at(1300, 862, mono('orders[1]["menu"]', 32, K4) + p(f"font-size:24px;font-weight:700;color:{K4};margin-top:4px", "15 · 키가 뜻을 말해 줘요"), bi("rise", 3)))
W("x-dictlist", o, "딕셔너리를 리스트에 담으면 바깥은 번호로, 안쪽은 키로 꺼내요. 13의 orders는 튜플을 담은 리스트라서 orders[1][0]처럼 번호 두 개로 꺼냈어요. 0번이 메뉴, 1번이 가격이라는 건 외워 둬야 했어요. 튜플 대신 딕셔너리를 담으면 orders[1][\"menu\"]처럼 이름으로 꺼내요. 대괄호가 닫히기 전에는 줄을 바꿔 적어도 돼요. 출력은 실제로 실행한 결과예요.")

o = [sec("x-for")] + head(EB4, "for로 주문을 하나씩 꺼내요", K4)
cr = {"id": "c-r", "lines": ["for order in orders:", '    print(order["menu"], order["price"] * order["qty"])'], "n": 3, "out": ["coffee 9000", "latte 5000", "cake 19500"],
      "oattrs": {j: bi("rise", j + 1) for j in range(3)}}
RT = 200
o += cell(cr, 96, RT, 1180, sel=True)
o.append(name_label("orders", 1320, 200, K4))
o += order_rows("fr", 1300, 250, ORD3, w=146, h=104, rgap=124)
for i, (m_, pr, q) in enumerate([("coffee", 4500, 2), ("latte", 5000, 1), ("cake", 6500, 3)]):
    y = 560 + i * 116
    o.append(f'<div data-build-in="fly order {i + 1}" data-from="fr{i}-0" style="position:absolute;left:96px;top:{y}px;display:flex;flex-direction:row;align-items:center;gap:22px">'
             + mono("order =", 30, K4) + mono(f'{{"menu": "{m_}", "price": {pr}, "qty": {q}}}', 28, INK, K4BG) + '</div>')
o.append(caption("order에는 주문 딕셔너리 하나가 통째로 들어가요.", 950, 3))
W("x-for", o, "for로 딕셔너리 리스트를 돌면 order에 주문 딕셔너리 하나가 통째로 들어가요. 14에서 2차원 리스트를 for로 돌면 row에 행 리스트가 통째로 들어갔어요. 딕셔너리 리스트도 같아요. order[\"menu\"], order[\"price\"]처럼 키로 꺼내고, 가격과 수량을 곱하면 주문마다 금액이 나와요. 출력은 실제로 실행한 결과예요.")

# =====================================================================
# part 5: compare, errors, three cafe examples
# =====================================================================
o = [sec("x-compare")] + head(EB5, "리스트, 튜플, 딕셔너리를 나란히 봐요", K5)
cols_x = [96, 420, 900, 1300]
cols_w = [300, 460, 380, 524]
hdr = ["", "리스트", "튜플", "딕셔너리"]
rows_ = [("만들기", '["latte", 5000]', '("latte", 5000)', '{"latte": 5000}'),
         ("꺼내기", "xs[0]", "t[0]", 'menu["latte"]'),
         ("값 바꾸기", 'xs[0] = "tea"', "못 바꿔요", 'menu["latte"] = 5500'),
         ("더하기", 'xs.append("tea")', "못 더해요", 'menu["tea"] = 4000'),
         ("지우기", "xs.pop(0)", "못 지워요", 'del menu["tea"]'),
         ("in이 보는 곳", "값", "값", "키")]
TY0, RH = 220, 104
o.append(f'<div style="position:absolute;left:1280px;top:{TY0 - 8}px;width:544px;height:{64 + RH * len(rows_) + 8}px;background:{K1BG};border-radius:18px"></div>')
for k, h in enumerate(hdr):
    o.append(p(f"position:absolute;left:{cols_x[k]}px;top:{TY0}px;width:{cols_w[k]}px;font-size:30px;font-weight:700;color:{K1 if k == 3 else SUB}", h))
o.append(hair(96, TY0 + 56, 1728, INK, h=3))
for i, r in enumerate(rows_):
    y = TY0 + 64 + i * RH
    for k, v in enumerate(r):
        code = k > 0 and (v[:1] in '[("{xmd' or v.startswith("xs") or v.startswith("t[") or v.startswith("del"))
        col = INK if k != 3 else K1
        if v.startswith("못"):
            col = GRAY
        o.append(p(f"position:absolute;left:{cols_x[k]}px;top:{y + 26}px;width:{cols_w[k]}px;font-family:{MONO if code else SANS};font-size:{28 if code else 30}px;font-weight:700;color:{col if k else SUB};white-space:pre", e(v)))
    o.append(hair(96, y + RH, 1728))
o.append(spot(1, 1280, TY0 - 8, 544, 64 + RH * len(rows_) + 8, pad=6, dim=0.45))
o.append(spot(2, 96, TY0 + 64 + 5 * RH, 1728, RH, pad=6, dim=0.45))
o.append(spot_off(3))
o.append(caption("순서대로 번호로 찾으면 리스트, 이름으로 찾으면 딕셔너리에 담아요.", 950, 3))
W("x-compare", o, "순서대로 번호로 찾을 값은 리스트, 이름으로 찾을 값은 딕셔너리에 담아요. 13의 리스트와 튜플은 번호로 꺼내고, 딕셔너리는 키로 꺼내요. 튜플은 만든 뒤에 바꾸거나 더하거나 지울 수 없어요. 리스트는 append로 더하지만, 딕셔너리는 새 키에 값을 넣으면 더해져요. in은 리스트와 튜플에서는 값을, 딕셔너리에서는 키를 봐요. 다음 장부터 앞에서 배운 것을 섞어서 써요.", ("use", "실제로 써 보기"))

o = [sec("x-err")] + head(EB5, "딕셔너리에서 자주 나는 오류 세 가지", K5)
errs = [({"id": "c-e0", "lines": ["scores[0]"], "n": 4, "out": ["KeyError: 0"], "err": True}, 'scores["kim"]', "딕셔너리에는 번호가 없어요"),
        ({"id": "c-e1", "lines": ['scores["Lee"]'], "n": 5, "out": ["KeyError: 'Lee'"], "err": True}, 'scores["lee"]', "키는 대문자와 소문자를 구분해요"),
        ({"id": "c-e2", "lines": ['orders["menu"]'], "n": 6, "out": ["TypeError: list indices must be integers or slices, not str"], "err": True}, 'orders[0]["menu"]', "orders는 리스트예요. 번호부터 적어요")]
for i, (c, good, why) in enumerate(errs):
    y = 210 + i * 245
    o += cell(c, 96, y, 1190)
    o.append(p(f"position:absolute;left:1340px;top:{y + 4}px;font-size:28px;font-weight:900;color:{GR}", "고치기"))
    o.append(at(1340, y + 50, mono(good, 32, INK, "#E6F4EC", "border:3px solid " + GR + ";")))
    o.append(p(f"position:absolute;left:1340px;top:{y + 124}px;width:484px;font-size:24px;font-weight:700;line-height:1.4;color:{SUB}", e(why)))
    o.append(spot(i + 1, 96, y, 1728, 190, pad=10, dim=0.45))
o.append(spot_off(4))
W("x-err", o, "오류 마지막 줄의 KeyError 뒤에는 찾던 키가 나와요. scores[0]은 리스트처럼 번호로 꺼낸 경우예요. 딕셔너리에는 번호가 없어서 0이라는 키를 찾다가 KeyError가 나요. scores[\"Lee\"]는 대문자 L로 적어서 lee와 다른 키예요. orders[\"menu\"]는 리스트에 키를 넣은 경우예요. orders는 바깥이 리스트라 번호부터 적고, 그다음에 키를 적어요. scores와 orders는 4파트에서 만든 것을 그대로 써서 셀 번호가 이어져요. 출력은 실제로 실행한 결과예요.")

RECEIPT = ['print("=" * 33)', "print(f\"{'KANT 카페':^31}\")", "print(f\"{'2026-11-03  14:30':^33}\")", 'print("=" * 33)', "print(f\"{'메뉴명':<7}{'단가':>6}{'수량':>3}{'금액':>8}\")", 'print("-" * 33)',
           "total = 0", "count = 0", "for order in orders:", '    amount = order["price"] * order["qty"]', "    print(f\"{order['menu']:<10}{order['price']:>8,}{order['qty']:>5}{amount:>10,}\")",
           "    total += amount", '    count += order["qty"]', 'print("-" * 33)', "print(f\"{'수량':<6}{count:>15}\")", "print(f\"{'합계':<6}{total:>25,}\")", 'print("=" * 33)', "print(f\"{'감사합니다':^28}\")"]
RC_OUT = ["=================================", "            KANT 카페            ", "        2026-11-03  14:30        ", "=================================", "메뉴명        단가 수량      금액",
          "---------------------------------", "coffee       4,500    2     9,000", "latte        5,000    1     5,000", "cake         6,500    3    19,500", "---------------------------------",
          "수량                  6", "합계                       33,500", "=================================", "           감사합니다            "]
o = [sec("x-receipt")] + head(EB5, "KANT 카페 영수증을 딕셔너리로 다시 찍어요", K5)
crc = {"id": "c-rc", "lines": RECEIPT, "n": 7}
RFS = 20
o += cell(crc, 96, 210, 1150, sel=True, fs=RFS)
o.append(f'<div{bi("fade", 1)} style="position:absolute;left:{96 + 87}px;top:{ly(210, 8, RFS) - LH(RFS) / 2:.0f}px;width:{1150 - 89}px;height:{LH(RFS) * 5:.0f}px;background:rgba(162,59,114,0.10);border-left:6px solid {K4};border-radius:6px"></div>')
o.append(tag(96 + 105, 210 + cell_h(crc, RFS) + 50, '13은 for menu, price, qty in orders:, 이번에는 order["price"]처럼 키로 꺼내요', K4, 1, 26, lead=False))
o.append(f'<div data-build-in="rise order 2" style="position:absolute;left:1250px;top:250px;width:560px;padding:34px 30px;background:#FFFFFF;border-radius:10px;box-shadow:0 2px 0 rgba(0,0,0,0.04),0 18px 40px rgba(29,35,48,0.16);display:flex;flex-direction:column">'
         + "".join(p(f"font-family:{MONO};font-size:24px;line-height:1.5;white-space:pre;color:{INK}", WIDE(e(l))) for l in RC_OUT) + '</div>')
W("x-receipt", o, "13에서 찍은 KANT 카페 영수증을 딕셔너리 리스트로 다시 찍어요. 머리글과 구분선은 13과 같고, 바뀐 곳은 for 안쪽이에요. 13에서는 for menu, price, qty in orders:로 튜플을 나눠 담았어요. 이번에는 order 하나에 딕셔너리가 통째로 들어가서 order[\"price\"]처럼 키로 꺼내요. f-string 중괄호 안에서 키를 적을 때는 바깥 큰따옴표와 겹치지 않게 작은따옴표로 적어요. 결과는 13과 같은 영수증이에요. 영수증의 한글은 영어 두 칸 너비로 그렸어요. 출력은 실제로 실행한 결과예요.")

o = [sec("x-cart")] + head(EB5, "장바구니에는 수량만, 가격은 메뉴판에서 찾아요", K5)
ct = {"id": "c-t", "lines": [MENU, 'cart = {"coffee": 2, "cake": 3}', "total = 0", "for name, qty in cart.items():", "    price = menu[name]", '    print(f"{name} {qty}개 {price * qty:,}원")', "    total += price * qty", 'print(f"합계 {total:,}원")'], "n": 8,
      "out": ["coffee 2개 9,000원", "cake 3개 19,500원", "합계 28,500원"], "wide": True}
TT = 200
o += cell(ct, 96, TT, 1100, sel=True)
o.append(name_label("menu", 1260, 200, K1))
o += row_of("tm", M0, 1260, 250, 180, 150, 12, K1, K1BG, state=["on", "off", "on"], fs=36, kfs=22)
o.append(name_label("cart", 1260, 440, K4))
o += row_of("tc", [('"coffee"', "2"), ('"cake"', "3")], 1260, 490, 180, 150, 12, K4, K4BG, fs=36, kfs=22)
for i, (k, pr, q, src) in enumerate([("coffee", 4500, 2, "tm0-v"), ("cake", 6500, 3, "tm2-v")]):
    y = 700 + i * 96
    o.append(at(1260, y, mono(f'menu["{k}"]', 28, K1), bi("rise", i + 1)))
    o.append(p(f"position:absolute;left:1500px;top:{y}px;font-family:{MONO};font-size:30px;font-weight:700;color:{INK};white-space:pre", f"{pr}", f' data-build-in="fly order {i + 1}" data-from="{src}"'))
    o.append(p(f"position:absolute;left:1590px;top:{y}px;font-family:{MONO};font-size:30px;font-weight:700;color:{INK};white-space:pre", f"× {q} = {pr * q:,}", bi("rise", i + 1)))
o.append(caption("가격이 바뀌면 메뉴판 한 곳만 고치면 돼요.", 950, 3))
W("x-cart", o, "가게에서는 메뉴판과 주문을 따로 둬요. menu는 메뉴 이름으로 가격을 찾는 딕셔너리, cart는 메뉴 이름으로 수량을 찾는 딕셔너리예요. for로 cart의 items()를 돌면서, 메뉴 이름 name으로 menu[name]을 꺼내면 가격이 나와요. 가격과 수량을 곱해 줄마다 찍고 total에 쌓아요. 가격이 바뀌면 메뉴판 한 곳만 고치면 돼요. 출력은 실제로 실행한 결과예요.")

o = [sec("x-sold")] + head(EB5, "주문 목록에서 메뉴별로 몇 개 팔렸는지 세요", K5)
csd = {"id": "c-sd", "lines": ['orders = [{"menu": "coffee", "qty": 2},', '          {"menu": "latte", "qty": 1},', '          {"menu": "coffee", "qty": 1},', '          {"menu": "cake", "qty": 2},', '          {"menu": "latte", "qty": 3}]',
                               "sold = {}", "for order in orders:", '    name = order["menu"]', '    sold[name] = sold.get(name, 0) + order["qty"]', "print(sold)", 'print(sold["latte"])', "print(sum(sold.values()))"], "n": 9,
       "out": ["{'coffee': 3, 'latte': 4, 'cake': 2}", "4", "9"]}
SDT = 196
o += cell(csd, 96, SDT, 1060, sel=True, fs=26)
o.append(f'<div{bi("fade", 1)} style="position:absolute;left:{96 + 87}px;top:{ly(SDT, 8, 26) - LH(26) / 2:.0f}px;width:{1060 - 89}px;height:{LH(26):.0f}px;background:rgba(15,124,134,0.12);border-left:6px solid {K3};border-radius:6px"></div>')
o.append(tag(lx(96, "{'coffee': 3, 'latte': 4, 'cake': 2}", 26) + 36, oy(csd, SDT, 0, 26), "메뉴별 개수", K5, 3, 24))
o.append(tag(lx(96, "4", 26) + 36, oy(csd, SDT, 2, 26), "모두 9개", K5, 3, 24))
sold_rows = [("coffee", 2), ("latte", 1), ("coffee", 1), ("cake", 2), ("latte", 3)]
o.append(name_label("orders", 1230, 200, K4))
for i, (m_, q) in enumerate(sold_rows):
    y = 250 + i * 70
    o.append(p(f"position:absolute;left:1230px;top:{y}px;height:56px;padding:0 20px;border-radius:12px;background:{K4BG};font-family:{MONO};font-size:26px;font-weight:700;line-height:56px;color:{INK};white-space:pre", f"{m_:<7} {q}", f' id="sd-o{i}"'))
o.append(name_label("sold", 1230, 640, K3, 2))
for k, (nm, v, src) in enumerate([('"coffee"', "3", "sd-o2"), ('"latte"', "4", "sd-o4"), ('"cake"', "2", "sd-o3")]):
    o.append(locker(f"sdl{k}", nm, v, 1230 + k * 200, 690, 186, 180, K3, K3BG, fs=52, kfs=24, attrs=f' data-build-in="fly order 2" data-from="{src}"'))
for r_ in (0, 2):
    o.append(underline(1, 1236, 1400, 250 + r_ * 70 + 62, K3, 5))
o.append(tag(1450, 250 + 140 + 28, "coffee는 2 + 1", K3, 1, 26, lead=False))
W("x-sold", o, "주문이 몇 번 들어왔든 sold[이름] = sold.get(이름, 0) + 수량 한 줄로 메뉴별로 모아요. 3파트에서 단어 개수를 센 것과 같은 방법이에요. 이번에는 1씩 더하지 않고 주문의 qty만큼 더해요. coffee는 2잔과 1잔이 들어와서 3, latte는 1잔과 3잔이 들어와서 4예요. 다 모은 뒤 values()에 sum을 쓰면 모두 몇 개 팔렸는지 나와요. orders를 새로 만들어서 앞 장의 orders는 이 목록으로 바뀌었어요. 출력은 실제로 실행한 결과예요.")

# =====================================================================
# wrap up
# =====================================================================
o = [sec("trouble")] + head("정리", "막히면 오류의 마지막 줄을 봐요", RED)
tr = [("KeyError: 'tea'", "없는 키를 꺼냈어요", 'menu.get("tea", 0)'),
      ("KeyError: 0", "딕셔너리에서 번호로 꺼냈어요", 'menu["coffee"]'),
      ("KeyError: 'Latte'", "키의 대문자와 소문자가 달라요", 'menu["latte"]'),
      ("TypeError: list indices must be integers ...", "리스트에 키를 넣었어요", 'orders[0]["menu"]'),
      ("{'latte': 5500}", "같은 키를 두 번 넣어 하나만 남았어요", "키를 다르게 적기"),
      ("5500 in menu  →  False", "in은 키만 봐요", "5500 in menu.values()")]
o.append(p(f"position:absolute;left:96px;top:206px;font-size:24px;font-weight:700;color:{GRAY}", "보이는 것"))
o.append(p(f"position:absolute;left:880px;top:206px;font-size:24px;font-weight:700;color:{GRAY}", "까닭"))
o.append(p(f"position:absolute;left:1380px;top:206px;font-size:24px;font-weight:700;color:{GRAY}", "고치기"))
o.append(hair(96, 248, 1728, INK, h=3))
for i, (q, a_, cmd) in enumerate(tr):
    y = 252 + i * 108
    o.append(f'<div{bi("rise", i + 1)} style="position:absolute;left:96px;top:{y}px;width:1728px;height:108px;border-bottom:2px solid {LINE};display:flex;flex-direction:row;align-items:center">'
             + p(f"width:784px;flex:none;font-family:{MONO};font-size:26px;font-weight:700;color:{RED if 'Error' in q else INK};white-space:pre", e(q))
             + p(f"width:500px;flex:none;font-size:26px;font-weight:700;color:{SUB}", e(a_))
             + p(f"flex:1;{'font-family:' + MONO + ';' if cmd.isascii() else ''}font-size:26px;font-weight:700;color:{GR};white-space:pre", e(cmd)) + '</div>')
o.append(caption("오류가 안 나도 결과가 이상하면 키가 겹치지 않았는지 봐요.", 950, 6))
W("trouble", o, "1번부터 3번은 모두 KeyError예요. 오류 마지막 줄의 KeyError 뒤에 찾던 키가 나와서, 어떤 키가 없는지 바로 알 수 있어요. 없을 수도 있는 키는 get으로 꺼내요. 4번은 바깥이 리스트인데 키부터 적은 경우예요. 5번과 6번은 오류는 안 나지만 결과가 생각과 다른 경우예요. 같은 키를 두 번 넣으면 마지막 값만 남고, in은 값이 아니라 키를 봐요. 오류 메시지는 hello-uv 커널에서 실제로 실행한 결과예요.", ("trouble", "정리"))

o = [sec("cheatsheet")] + head("정리", "이럴 땐 이렇게 써요", RED)
cheat = [("값을 이름으로 담기", '{"latte": 5000}'), ("이름으로 꺼내기", 'menu["latte"]'), ("없을 수도 있는 키 꺼내기", 'menu.get("tea", 0)'), ("더하거나 바꾸기", 'menu["tea"] = 4000'),
         ("지우기", 'del menu["tea"]   menu.pop("tea")'), ("키가 있는지 묻기", '"tea" in menu'), ("한 쌍씩 돌기", "for k, v in menu.items():"), ("개수 세기", "count[w] = count.get(w, 0) + 1")]
for i, (when, code) in enumerate(cheat):
    col, row = i // 4, i % 4
    x, y = 96 + col * 880, 220 + row * 132
    o.append(p(f"position:absolute;left:{x}px;top:{y}px;font-size:26px;font-weight:700;color:{SUB}", e(when)))
    o.append(p(f"position:absolute;left:{x}px;top:{y + 42}px;font-family:{MONO};font-size:{30 if len(code) < 28 else 27}px;font-weight:700;color:{INK};white-space:pre", e(code)))
    o.append(hair(x, y + 112, 848))
o.append(f'<div style="position:absolute;left:96px;top:800px;width:1728px;height:130px;border-radius:20px;background:{INK};display:flex;flex-direction:row;align-items:center;padding:0 44px;gap:36px">'
         + p("font-size:28px;font-weight:700;color:#F2B27A;white-space:nowrap", "다음 · 16 집합")
         + p("font-size:30px;font-weight:700;color:#F6F5F1", "같은 값은 한 번만 담는 그릇이에요. 딕셔너리의 키처럼 겹치지 않아요.") + '</div>')
W("cheatsheet", o, "딕셔너리는 이름으로 값을 찾을 때 써요. 이 장의 코드를 노트북 마크다운 셀에 옮겨 두면 복습할 때 같이 봐요. 키는 겹치지 않고, 같은 키에 넣으면 값이 바뀐다는 것만 기억해요. 다음 16에서는 같은 값을 한 번만 담는 집합을 배워요. 집합의 값도 딕셔너리의 키처럼 겹치지 않아요.")

# ---------- toc ----------
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
parts = [(K1, "만들고 꺼내기", "번호 대신 키, 메뉴판 모양, { 키: 값 }, [키]와 KeyError, get", "d-why", "d-short"),
         (K2, "바꾸고 지우기", "추가와 수정, 겹치지 않는 키, del과 pop, 키를 보는 in", "d-add", "d-in"),
         (K3, "둘러보기", "keys, values, items, list(), for로 한 쌍씩, sum과 sorted, get으로 세기", "d-views", "d-count"),
         (K4, "리스트와 섞기", "값이 리스트인 딕셔너리, 딕셔너리 리스트, for로 주문 돌기", "x-listval", "x-for"),
         (K5, "실제로 써 보기", "리스트·튜플과 비교, 오류 세 가지, 영수증, 장바구니, 판매 개수", "x-compare", "x-sold")]
TOC_NOTE = "다섯 파트로 나눴어요. 1파트는 딕셔너리를 만들고 키로 꺼내는 법, 2파트는 추가, 수정, 삭제예요. 3파트는 for로 둘러보고, 4파트는 리스트와 섞어요. 5파트는 리스트, 튜플과 비교한 뒤 카페 예제 세 개를 풀어요. 파트마다 새 커널에서 위에서부터 차례로 실행해요. 5파트는 4파트 커널에 이어서 실행해요."
t = [sec("toc"), f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>']
for i, (c, h, s, a, b) in enumerate(parts):
    y = 210 + i * 136
    t.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:136px;border-bottom:2px solid {LINE};display:flex;flex-direction:row;align-items:center;gap:36px">'
             + p(f"width:70px;flex:none;font-size:64px;font-weight:900;color:{c}", str(i + 1))
             + '<div style="flex:1;display:flex;flex-direction:column;gap:6px">' + p(f"font-size:36px;font-weight:700;color:{INK}", h) + p(f"font-size:24px;color:{SUB}", e(s)) + '</div>'
             + p(f"font-size:28px;font-weight:700;color:{GRAY};white-space:nowrap", f"{page[a]}–{page[b]}쪽") + '</div>')
t.append(p(f"position:absolute;left:96px;top:910px;font-size:26px;color:{SUB}", f'{page["ready"]}쪽은 노트북 준비, {page["trouble"]}–{page["cheatsheet"]}쪽은 막힐 때와 정리예요.'))
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(t) + f"\n<aside>{e(TOC_NOTE)}</aside>\n</section>\n")

DECK_TITLE = "파이썬 기초 4 (딕셔너리)"
deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-03T01:00:00Z"}, "lists": "css", "title": DECK_TITLE, "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
print(len(ORDER), "slides")
