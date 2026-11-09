"""Generates every slide of the uv deck (09) and slides/deck.json.

Flow (CLAUDE.md 챕터 설계 틀): why (a cloned project fails) -> big picture (python, packages, .venv, uv)
-> install -> smallest example (uv init, uv run) -> one part at a time (add, tree, remove, sync, Jupyter)
-> compare with the old way -> errors -> three real situations -> summary.
Jupyter setup must stay on pages 25-27: chapters 10 and 12-26 cite "09 · 25–27쪽".

Design (Stageshow rules moved to HTML slides, tools/DESIGN.md): one hero per slide, terms labelled on the
picture with leader lines instead of side cards, lists drawn as hairline rows instead of bordered cards,
terminals sized to their lines, values that move between places fly there.
Terminal output comes from tools/demo.sh (uv 0.11.32, Python 3.14.6); paths are rewritten to /home/kim, /home/lee.
Usage (in 09-python-uv): python3 tools/gen.py slides
"""
import html, json, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from highlight import spot, spot_off, cursor, cursor_off, ring, box, underline  # noqa: E402

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT):
    if f.endswith(".html"):
        os.remove(os.path.join(OUT, f))

SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
BG = "#F6F5F1"
INK, SUB, GRAY, LINE, HAIR, CARD = "#1D2330", "#4A5262", "#6A7180", "#E1DED6", "#E3E0D8", "#FFFFFF"
BL, GR, OR, PUR, RED, NAVY, TEAL = "#2459C9", "#1F8A4C", "#B26A00", "#5A3BB8", "#A33131", "#1E3F8F", "#0F7C86"
JP = "#B8560F"                          # Jupyter, same as chapters 10 and 12-26
KIM, LEE, HUB = BL, GR, PUR             # team colours (CLAUDE.md)
F_PY, F_LOCK, F_VENV = NAVY, PUR, GR    # pyproject.toml, uv.lock, .venv
TC = {"$": "#F2C46D", "o": "#D8DEE9", "g": "#7FD18B", "r": "#F28B82", "#": "#8C95A6", "H": "#FFE7A8", "E": "#F28B82"}
CW = 0.6                                # JetBrains Mono advance per font-size


def e(s):
    return html.escape(s, quote=False)


def p(style, text, attrs=""):
    return f'<p{attrs} style="{style}">{text}</p>'


def bi(kind, order):
    return f' data-build-in="{kind} order {order}"'


ORDER, SECTIONS = [], {}


def W(sid, parts, notes, section=None):
    if section:
        SECTIONS[section[0]] = {"description": section[1], "start": sid}
    ORDER.append(sid)
    with open(os.path.join(OUT, sid + ".html"), "w") as f:
        f.write("\n".join(parts) + f"\n<aside>{e(notes)}</aside>\n</section>\n")


def sec(sid, bg=BG, transition="fade"):
    return (f'<section id="{sid}" data-transition="{transition}" style="background:{bg};color:{INK};font-family:{SANS};'
            f'font-variant-ligatures:none;word-break:keep-all;padding:96px;display:flex;flex-direction:column">')


def head(eyebrow, title, color):
    return [p(f"position:absolute;left:96px;top:48px;width:1728px;font-size:26px;font-weight:700;color:{color}", e(eyebrow), ' id="eyebrow"'),
            f'<h2 id="title" style="position:absolute;left:96px;top:92px;width:1728px;font-size:56px;font-weight:700;line-height:1.2;color:{INK}">{title}</h2>']


def caption(text, top, left=96, w=1728, attrs=""):
    return p(f"position:absolute;left:{left}px;top:{top}px;width:{w}px;font-size:32px;font-weight:700;line-height:1.45;color:{INK}", text, attrs)


def note(text, left, top, w, color=SUB, size=26, attrs="", weight=400, align="left"):
    return p(f"position:absolute;left:{left}px;top:{top}px;width:{w}px;font-size:{size}px;font-weight:{weight};line-height:1.45;text-align:{align};color:{color}", text, attrs)


def mono(text, size, color=INK, weight=700, extra=""):
    return p(f"font-family:{MONO};font-size:{size}px;font-weight:{weight};line-height:1.35;white-space:nowrap;color:{color};{extra}", text)


# ---------- terminal: fixed line height so labels and pen marks can be placed by line number ----------
class Term:
    def __init__(self, lines, x, y, w, size=28, lh=None, tid="term", attrs="", padx=36, pady=26, prompt="$ ", builds=None):
        self.x, self.y, self.w, self.size = x, y, w, size
        self.lh = lh or round(size * 1.5)
        self.padx, self.pady = padx, pady
        self.h = pady * 2 + len(lines) * self.lh
        o = [f'<div id="{tid}"{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{self.h}px;background:#1B2029;'
             f'border-radius:20px;padding:{pady}px {padx}px;display:flex;flex-direction:column;font-family:{MONO};font-variant-ligatures:none">']
        for k, (kind, text) in enumerate(lines):
            t = e(text)
            lead = len(t) - len(t.lstrip(" "))
            t = "&#160;" * lead + t.lstrip(" ") if t.strip() else "&#160;"
            at = bi("fade", builds[k]) if builds and builds.get(k) else ""
            if kind == "$":
                st, t = f"font-weight:700;color:{TC['$']}", prompt + t
            elif kind == "A":
                st, t = f"font-weight:700;color:{TC['$']}", f'<span style="color:#7FD18B">(hello-uv)</span> $ ' + t
            elif kind == "H":
                st = f"font-weight:700;color:{TC['H']};background:rgba(242,196,109,.2);border-radius:6px;margin:0 -10px;padding:0 10px"
            elif kind == "E":
                st = f"font-weight:700;color:{TC['E']}"
            else:
                st = f"color:{TC[kind]}"
            o.append(p(f"font-size:{size}px;line-height:{self.lh}px;height:{self.lh}px;white-space:pre;{st}", t, at))
        o.append('</div>')
        self.parts = o

    def ly(self, k):                 # vertical centre of line k
        return self.y + self.pady + k * self.lh + self.lh / 2

    def lt(self, k):                 # top of line k
        return self.y + self.pady + k * self.lh

    def tx(self, col):               # x of character column col
        return self.x + self.padx + col * self.size * CW


def lead(order, label_x, label_y, tx, ty, text, color, w=520, size=28, align="left", kind="fade", weight=700, dot=True):
    """Stageshow leader: a thin line from a label to what it explains, ending in a small dot just short of it.
    (label_x, label_y): where the label's text block starts (left edge, vertical centre)."""
    if align == "left":
        lx, ly_ = label_x - 14, label_y
        left = label_x
    else:                             # label sits left of the line, right-aligned
        lx, ly_ = label_x + 14, label_y
        left = label_x - w
    d = f'<circle cx="{tx}" cy="{ty}" r="7" fill="{color}" stroke="none"/>' if dot else ""
    svg = (f'<svg{bi(kind, order)} viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible">'
           f'<path d="M{lx:.0f},{ly_:.0f} L{tx:.0f},{ty:.0f}" fill="none" stroke="{color}" stroke-width="3" stroke-linecap="round"/>{d}</svg>')
    lab = p(f"position:absolute;left:{left:.0f}px;top:{label_y - size * 0.75:.0f}px;width:{w}px;font-size:{size}px;font-weight:{weight};line-height:1.5;"
            f"text-align:{align};color:{color}", text, bi("fade", order))
    return [svg, lab]


def tag(text, color, left, top, attrs=""):
    """Small label above a terminal or panel: whose computer it is."""
    return (f'<div{attrs} style="position:absolute;left:{left}px;top:{top}px;display:flex;flex-direction:row;gap:12px;align-items:center">'
            f'<div style="width:14px;height:14px;border-radius:50%;background:{color}"></div>'
            + p(f"font-size:26px;font-weight:700;color:{color};white-space:nowrap", e(text)) + '</div>')


def code_card(cid, name, lines, x, y, w, color=BL, size=28, lh=None, marks=(), attrs="", padx=30):
    """A file: name on top, code below, fixed line height. Returns parts and the y centre of each line."""
    lh = lh or round(size * 1.45)
    top_pad, name_h = 18, 44
    h = top_pad + name_h + len(lines) * lh + 22
    o = [f'<div id="{cid}"{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{CARD};border:2px solid {LINE};'
         f'border-radius:18px;padding:{top_pad}px {padx}px 0;display:flex;flex-direction:column">',
         p(f"font-family:{MONO};font-size:24px;font-weight:700;line-height:{name_h}px;height:{name_h}px;color:{color}", e(name))]
    for i, ln in enumerate(lines):
        mk = "background:#FFF1C9;border-radius:6px;margin:0 -10px;padding:0 10px;" if i in marks else ""
        o.append(p(f"font-family:{MONO};font-size:{size}px;line-height:{lh}px;height:{lh}px;white-space:pre;{mk}color:{INK}", e(ln) if ln else "&#160;"))
    o.append('</div>')
    ys = [y + 2 + top_pad + name_h + i * lh + lh / 2 for i in range(len(lines))]
    return o, ys, h


# ---------- a project folder drawn as one panel with hairline rows ----------
FNOTE = {".git": "Git 저장소 (02)", ".gitignore": "Git에 안 올릴 목록", ".python-version": "쓸 파이썬 버전", ".venv": "가상환경 (패키지 상자)",
         "README.md": "프로젝트 소개 글", "main.py": "실행할 코드", "pyproject.toml": "프로젝트 설명서", "uv.lock": "정확한 버전 목록"}
FDIR = {".git", ".venv"}


def glyph(name):
    if name in FDIR:
        g = '<div style="width:30px;height:22px;background:#E0B54A;border-radius:4px"></div>'
    else:
        g = '<div style="width:22px;height:28px;background:#B9BFCB;border-radius:3px"></div>'
    return f'<div style="width:30px;flex:none;display:flex;flex-direction:row;justify-content:flex-start;align-items:center">{g}</div>'


def folder(files, x, y, w, title="hello-uv", new=(), off=(), notes=True, pre="", rh=66, build_new=None, pop=None, note_map=None, note_color=None):
    """files in ls -a order. new: rows drawn as just made (green fill, pop in). off: rows crossed out."""
    h = 72 + len(files) * rh + 14
    o = [f'<div id="{pre}fold" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{CARD};border:2px solid {LINE};border-radius:20px"></div>',
         p(f"position:absolute;left:{x + 30}px;top:{y + 18}px;width:{w - 60}px;font-family:{MONO};font-size:26px;font-weight:700;color:{GRAY}", e(title + "/"), f' id="{pre}fold-t"')]
    rows = {}
    for i, name in enumerate(files):
        ry = y + 72 + i * rh
        rows[name] = ry + rh / 2
        isnew, crossed = name in new, name in off
        bg = "background:#E4F3EA;" if isnew else ""
        hair = f"border-top:2px solid {HAIR};" if i else f"border-top:2px solid {HAIR};"
        col = "#9AA0AB" if crossed else (GR if isnew else INK)
        deco = "text-decoration:line-through;text-decoration-thickness:3px;" if crossed else ""
        attrs = f' id="{pre}f-{name}"' + (bi("pop", build_new) if (isnew or (pop and name in pop)) and build_new else "")
        o.append(f'<div{attrs} style="position:absolute;left:{x + 16}px;top:{ry}px;width:{w - 32}px;height:{rh}px;{hair}{bg}border-radius:{10 if isnew else 0}px;'
                 f'padding:0 16px;display:flex;flex-direction:row;gap:18px;align-items:center">'
                 + glyph(name) + p(f"width:290px;flex:none;font-family:{MONO};font-size:27px;font-weight:700;white-space:nowrap;{deco}color:{col}", e(name))
                 + (p(f"flex:1;font-size:24px;white-space:nowrap;{'font-weight:700;' if note_color and name in (note_map or {}) else ''}color:{note_color if note_color and name in (note_map or {}) else SUB}", e((note_map or FNOTE).get(name, FNOTE.get(name, '')))) if notes else "") + '</div>')
    return o, rows, h


# ---------- the three places uv add / uv remove change: one panel, three hairline sections ----------
def three(state, x, y, w, attrs_by=None, hid=""):
    """state: key -> (value lines, sub, colour of value). attrs_by: key -> extra attrs (build-in, fly)."""
    items = [("py", "pyproject.toml", "내가 고른 패키지", F_PY), ("lock", "uv.lock", "따라온 것까지 정확한 버전", F_LOCK), ("venv", ".venv", "실제로 설치된 패키지", F_VENV)]
    sh = 214
    o = [f'<div id="{hid}three" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{sh * 3 + 8}px;background:{CARD};border:2px solid {LINE};border-radius:20px"></div>']
    for i, (k, name, role, c) in enumerate(items):
        sy = y + 4 + i * sh
        val, subt, vc = state[k]
        hair = f"border-top:2px solid {HAIR};" if i else ""
        ex = (attrs_by or {}).get(k, "")
        o.append(f'<div style="position:absolute;left:{x + 24}px;top:{sy}px;width:{w - 48}px;height:{sh}px;{hair}padding:22px 10px;display:flex;flex-direction:column;gap:10px">'
                 + '<div style="display:flex;flex-direction:row;gap:18px;align-items:center">'
                 + f'<div style="width:16px;height:16px;flex:none;border-radius:50%;background:{c}"></div>'
                 + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{c}", e(name)) + p(f"font-size:24px;color:{GRAY}", e(role)) + '</div>'
                 + f'<div id="{hid}v-{k}"{ex} style="display:flex;flex-direction:column;gap:6px;padding-left:34px">'
                 + p(f"font-family:{MONO};font-size:30px;font-weight:700;line-height:1.35;white-space:pre;color:{vc}", e(val))
                 + (p(f"font-size:24px;line-height:1.4;color:{SUB}", e(subt)) if subt else "") + '</div></div>')
    return o


def hrows(x, y, cols, rows, rh, size=30, header=None, hsize=24, rid=None, attrs_by_row=None, hcolors=None):
    """A table drawn with hairlines only. rows: list of cells; a cell is text or (html, style)."""
    o = []
    top = y
    if header:
        o.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:{sum(cols)}px;height:52px;border-bottom:3px solid {INK};display:flex;flex-direction:row;align-items:center">'
                 + "".join(p(f"width:{w}px;padding:0 20px;font-size:{hsize}px;font-weight:700;color:{(hcolors or [GRAY] * len(cols))[j]}", hcell) for j, (w, hcell) in enumerate(zip(cols, header)))
                 + '</div>')
        top = y + 52
    for i, r in enumerate(rows):
        ex = (attrs_by_row or {}).get(i, "")
        idat = f' id="{rid}{i}"' if rid else ""
        o.append(f'<div{idat}{ex} style="position:absolute;left:{x}px;top:{top + i * rh}px;width:{sum(cols)}px;height:{rh}px;border-bottom:2px solid {LINE};display:flex;flex-direction:row;align-items:center">')
        for w, c in zip(cols, r):
            text, st = c if isinstance(c, tuple) else (c, "")
            o.append(p(f"width:{w}px;padding:0 20px;font-size:{size}px;line-height:1.35;color:{INK};{st}", text))
        o.append('</div>')
    return o, top


def arrow_svg(x1, y1, x2, y2, color, order=None, width=5, kind="draw", dashed=False):
    import math
    ang = math.atan2(y2 - y1, x2 - x1)
    a1 = (x2 - 20 * math.cos(ang - 0.5), y2 - 20 * math.sin(ang - 0.5))
    a2 = (x2 - 20 * math.cos(ang + 0.5), y2 - 20 * math.sin(ang + 0.5))
    b = bi(kind, order) if order else ""
    dash = ' stroke-dasharray="14 12"' if dashed else ""
    return (f'<svg{b} viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible">'
            f'<g fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="M{x1},{y1} L{x2},{y2}"{dash}/><path d="M{a1[0]:.0f},{a1[1]:.0f} L{x2},{y2} L{a2[0]:.0f},{a2[1]:.0f}"/></g></svg>')


def chip(text, color, size=28, bg="#F1F0EC", attrs="", extra=""):
    return p(f"font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.5;white-space:nowrap;color:{color};background:{bg};border-radius:10px;padding:6px 18px;{extra}", e(text), attrs)


def cell(n, code_lines, out, x, y, w, attrs="", size=26, out_color=INK, cid=None, oid=None):
    """A notebook cell: [n] on the left, code box, output under it. Returns parts and total height."""
    lh = round(size * 1.45)
    ch = 24 + len(code_lines) * lh
    oh = (16 + lh + 8) if out is not None else 0
    o = [f'<div{f" id={chr(34)}{cid}{chr(34)}" if cid else ""}{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{ch + oh}px">',
         p(f"position:absolute;left:0;top:12px;width:70px;font-family:{MONO};font-size:22px;color:{GRAY};text-align:right", f"[{n}]"),
         f'<div style="position:absolute;left:86px;top:0;width:{w - 86}px;height:{ch}px;background:#FFFFFF;border:2px solid {LINE};border-left:6px solid {BL};border-radius:10px;padding:10px 20px">'
         + "".join(p(f"font-family:{MONO};font-size:{size}px;line-height:{lh}px;height:{lh}px;white-space:pre;color:{INK}", e(c)) for c in code_lines) + '</div>']
    if out is not None:
        o.append(p(f"position:absolute;left:112px;top:{ch + 14}px;width:{w - 120}px;font-family:{MONO};font-size:{size}px;line-height:{lh}px;white-space:pre;color:{out_color}", e(out),
                   f' id="{oid}"' if oid else ""))
    o.append('</div>')
    return o, ch + oh, ch


# ---------- real output (tools/demo.sh) ----------
PKGS = ["annotated-doc==0.0.5", "annotated-types==0.8.0", "anyio==4.16.0", "fastapi==0.162.2", "idna==3.20", "opentelemetry-api==1.45.2", "pydantic==2.14.3",
        "pydantic-core==2.50.4", "starlette==1.10.0", "typing-extensions==4.16.0", "typing-inspection==0.4.5"]
FILES0 = [".git", ".gitignore", ".python-version", "README.md", "main.py", "pyproject.toml"]
FILES1 = [".git", ".gitignore", ".python-version", ".venv", "README.md", "main.py", "pyproject.toml", "uv.lock"]
MAIN_REQ = ["import fastapi", "", 'print("fastapi 버전:", fastapi.__version__)']
LS_ONE = ".  ..  .git  .gitignore  .python-version  README.md  main.py  pyproject.toml  uv.lock"

EB1, EB2, EB3, EB4, EB5, EB6, EB7, EB8, EB9, EB10 = ("1. 왜 필요할까", "2. 큰 그림", "3. uv 설치하기", "4. 프로젝트 만들고 실행하기", "5. 패키지 넣고 빼기",
                                                     "6. 다른 컴퓨터에서 그대로", "7. VS Code에서 Jupyter 쓰기", "8. 예전 방식과 비교", "9. 막힐 때", "10. 실제 상황 예제")
C1, C2, C3, C4, C5, C6, C7, C8, C9, C10 = RED, BL, TEAL, BL, NAVY, PUR, JP, OR, RED, GR

# =====================================================================================
# 1. cover: one terminal, bled off the right and bottom edge (corner bleed)
# =====================================================================================
o = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px;display:flex;flex-direction:column;justify-content:center">',
     p("position:absolute;left:128px;top:300px;width:820px;font-size:28px;font-weight:700;color:#7FD6DC", "KANT AX/AI 엔지니어 트랙 · 보충 학습 자료"),
     '<h1 style="position:absolute;left:128px;top:356px;width:820px;font-size:104px;font-weight:900;line-height:1.12;color:#F6F5F1">uv로<br>파이썬 시작하기</h1>',
     p("position:absolute;left:128px;top:620px;width:820px;font-size:38px;line-height:1.45;color:#BFC6D4", "프로젝트를 만들고, 패키지를 넣고,<br>다른 컴퓨터에서 그대로 받기")]
o.append(f'<div style="position:absolute;left:1010px;top:240px;width:1000px;height:900px;background:#11151C;border-radius:24px;padding:44px 48px;display:flex;flex-direction:column;font-family:{MONO}">')
for k, l in [("$", "$ uv init hello-uv"), ("o", "Initialized project `hello-uv`"), ("$", "$ cd hello-uv"), ("$", "$ uv add fastapi"), ("o", "Installed 11 packages in 5ms"),
             ("$", "$ uv run main.py"), ("H", "fastapi 버전: 0.162.2"), ("$", "$ uv sync"), ("o", "Resolved 12 packages in 1ms")]:
    col = {"$": "#F2C46D", "o": "#9AA3B2", "H": "#FFE7A8"}[k]
    o.append(p(f"font-size:32px;line-height:64px;height:64px;white-space:pre;font-weight:{700 if k != 'o' else 400};color:{col}", e(l)))
o.append('</div>')
W("cover", o, "오늘부터 파이썬 프로젝트는 uv 하나로 만들고 실행해요. 먼저 받은 프로젝트가 왜 남의 컴퓨터에서 안 돌아가는지 봐요. 그다음 uv init, uv run, uv add, uv remove, uv sync를 순서대로 쳐 봐요. VS Code에서 Jupyter 노트북을 여는 준비까지 마쳐요. 마지막에 실제로 자주 만나는 상황 세 가지를 풀어요.",
  ("intro", "들어가기"))
ORDER.append("toc")      # written last, when page numbers are known

# =====================================================================================
# 1. why: lee clones kim's project and runs it with python3
# =====================================================================================
o = [sec("why")] + head(EB1, "받은 프로젝트를 실행했더니 오류가 나요", C1)
o.append(tag("lee 컴퓨터", LEE, 96, 196))
t = Term([("$", "git clone https://github.com/kim/hello-uv.git"), ("o", "Cloning into 'hello-uv'..."), ("o", "done."), ("$", "cd hello-uv"), ("$", "ls -a"), ("o", LS_ONE),
          ("$", "python3 main.py"), ("o", "Traceback (most recent call last):"), ("o", '  File "/home/lee/hello-uv/main.py", line 1, in <module>'), ("o", "    import fastapi"),
          ("E", "ModuleNotFoundError: No module named 'fastapi'")], 96, 248, 1560, size=29, lh=46)
o += t.parts
ex = t.tx(47) + 8
o.append(box(1, t.tx(0) - 12, t.lt(10) + 2, ex - t.tx(0) + 16, t.lh - 4, RED))
o += lead(2, 1160, t.ly(10), ex + 34, t.ly(10), "fastapi는 kim 컴퓨터에만 있어요", RED, w=620)
o.append(caption("코드와 목록 파일은 받았는데, 코드가 쓰는 패키지는 따라오지 않았어요.", 870, attrs=bi("fade", 3)))
W("why", o, "kim이 만든 프로젝트를 lee가 GitHub에서 받아 바로 실행했더니 ModuleNotFoundError가 났어요. main.py 첫 줄이 fastapi라는 패키지를 불러오는데, lee 컴퓨터에는 fastapi가 없어요. 패키지는 kim 컴퓨터의 가상환경 안에만 설치돼 있고 GitHub에는 올라가지 않아요. 예전에는 lee가 가상환경을 만들고 패키지를 하나씩 설치해야 했어요. 오늘 배우는 uv로는 uv sync 한 번이면 끝나요. 22쪽에서 같은 장면을 uv로 다시 봐요. 출력은 tools/demo.sh로 실제로 실행한 결과이고, ls -a는 터미널 창에서 보이는 대로 한 줄로 적었어요.",
  ("why", "왜 필요할까"))

# =====================================================================================
# 2. big picture
# =====================================================================================
# run: python reads the .py file
o = [sec("run")] + head(EB2, "python이 .py 파일을 읽고 실행해요", C2)
t = Term([("$", "python3 hello.py"), ("H", "안녕하세요")], 96, 430, 760, size=48, lh=84)
o += t.parts
cc, ys, chh = code_card("c-hello", "hello.py", ['print("안녕하세요")'], 1160, 430, 664, BL, 40, lh=64, attrs=bi("fade", 3))
o += cc
o.append(note(".py 파일은 메모장으로도 열리는 글자 파일이에요.", 1160, 430 + chh + 30, 664, SUB, 28, attrs=bi("fade", 3)))
x_py = t.tx(2) + 3.5 * 48 * CW
o += [f'<svg{bi("fade", 1)} viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible">'
      f'<path d="M{x_py:.0f},350 L{x_py:.0f},{t.lt(0) + 8:.0f}" stroke="{BL}" stroke-width="3"/><circle cx="{x_py:.0f}" cy="{t.lt(0) + 8:.0f}" r="7" fill="{BL}"/></svg>',
      p(f"position:absolute;left:{x_py - 200:.0f}px;top:300px;width:400px;font-size:30px;font-weight:700;text-align:center;color:{BL}", "파이썬 프로그램", bi("fade", 1))]
x_h = t.tx(10) + 4 * 48 * CW
o += [f'<svg{bi("fade", 2)} viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible">'
      f'<path d="M{x_h:.0f},350 L{x_h:.0f},{t.lt(0) + 8:.0f}" stroke="{BL}" stroke-width="3"/><circle cx="{x_h:.0f}" cy="{t.lt(0) + 8:.0f}" r="7" fill="{BL}"/></svg>',
      p(f"position:absolute;left:{x_h - 200:.0f}px;top:300px;width:400px;font-size:30px;font-weight:700;text-align:center;color:{BL}", "읽을 파일", bi("fade", 2))]
o.append(arrow_svg(t.x + t.w + 30, t.ly(0), 1140, t.ly(0), BL, 3, width=4))
x_o = t.tx(0) + 2.5 * 48 * CW
o += [f'<svg{bi("fade", 4)} viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible">'
      f'<path d="M{x_o:.0f},{t.y + t.h + 80:.0f} L{x_o:.0f},{t.lt(1) + t.lh - 10:.0f}" stroke="{BL}" stroke-width="3"/><circle cx="{x_o:.0f}" cy="{t.lt(1) + t.lh - 10:.0f}" r="7" fill="{BL}"/></svg>',
      p(f"position:absolute;left:{x_o - 200:.0f}px;top:{t.y + t.h + 86:.0f}px;width:400px;font-size:30px;font-weight:700;text-align:center;color:{BL}", "실행 결과", bi("fade", 4))]
W("run", o, "파이썬 코드는 python이라는 프로그램이 한 줄씩 읽어서 실행해요. hello.py는 메모장으로도 열 수 있는 글자 파일이에요. 터미널에서 python3 뒤에 파일 이름을 적으면 python이 그 파일을 읽고 결과를 보여 줘요. 그래서 파이썬을 쓰려면 먼저 컴퓨터에 python 프로그램이 있어야 해요. Mac과 Linux는 python3, Windows는 python이라는 이름으로 부르는 경우가 많아요. 출력은 uv가 받은 Python 3.14.6에서 실제로 실행한 결과예요.",
  ("big", "큰 그림"))

# pkg: PyPI shelf, fastapi flies into my project
o = [sec("pkg")] + head(EB2, "남이 만든 코드 묶음을 패키지라고 해요", C2)
o.append(note("PyPI · 파이썬 패키지 창고", 96, 214, 900, PUR, 30, weight=700))
shelf = ["requests", "numpy", "pandas", "openai", "fastapi", "pytest", "matplotlib", "flask", "pillow", "scikit-learn", "httpx", "rich", "django", "pydantic", "polars"]
for i, n in enumerate(shelf):
    cx, cy = 96 + (i % 3) * 304, 284 + (i // 3) * 118
    hot = n == "fastapi"
    o.append(f'<div id="sh-{n}" style="position:absolute;left:{cx}px;top:{cy}px;width:280px;height:92px;border-radius:14px;'
             f'background:{"#E7DEFC" if hot else "#FFFFFF"};border:2px solid {"#8E6FEA" if hot else LINE};display:flex;align-items:center;justify-content:center;'
             f'{"box-shadow:0 10px 24px rgba(90,59,184,.22);" if hot else ""}">' + mono(e(n), 30, PUR if hot else SUB, 700 if hot else 400) + '</div>')
o.append(note("… 60만 개 넘게", 96, 284 + 5 * 118, 860, GRAY, 26))
o.append(f'<div style="position:absolute;left:1180px;top:284px;width:644px;height:{72 + 2 * 76 + 18}px;background:{CARD};border:2px solid {LINE};border-radius:20px"></div>')
o.append(p(f"position:absolute;left:1210px;top:302px;width:584px;font-family:{MONO};font-size:26px;font-weight:700;color:{GRAY}", "hello-uv/"))
o.append(f'<div style="position:absolute;left:1196px;top:356px;width:612px;height:76px;border-top:2px solid {HAIR};padding:0 16px;display:flex;flex-direction:row;gap:18px;align-items:center">'
         + glyph("main.py") + mono("main.py", 28) + '</div>')
o.append(f'<div id="pk-fast" data-build-in="fly order 1" data-from="sh-fastapi" style="position:absolute;left:1196px;top:436px;width:612px;height:72px;'
         f'background:#EEE8FD;border-radius:10px;padding:0 16px;display:flex;flex-direction:row;gap:18px;align-items:center">'
         f'<div style="width:30px;height:22px;flex:none;background:#8E6FEA;border-radius:4px"></div>' + mono("fastapi", 28, PUR) + p(f"font-size:24px;color:{SUB}", "받아 온 패키지") + '</div>')
o.append(note("fastapi는 웹 서버를 만드는 패키지예요. 이 자료는 fastapi를 넣고, 불러오고, 빼 봐요.", 1180, 580, 644, SUB, 30, attrs=bi("fade", 2)))
W("pkg", o, "파이썬으로 하는 일 대부분은 남이 만들어 둔 코드를 받아서 써요. 이 코드 묶음을 패키지라고 하고, PyPI라는 인터넷 창고에 60만 개 넘게 모여 있어요. 데이터 분석은 pandas, AI API는 openai처럼 필요한 패키지를 골라 받아요. 오늘 예시는 웹 서버를 만드는 fastapi예요. 서버를 켜는 건 뒤 수업에서 하고, 오늘은 넣고 불러오고 빼는 데까지만 해요. 받은 패키지를 어디에 두느냐가 다음 장의 가상환경이에요.")

# venv: one shared box breaks, one box per project works
o = [sec("venv")] + head(EB2, "가상환경은 프로젝트마다 따로 쓰는 패키지 상자예요", C2)
o.append(f'<div style="position:absolute;left:96px;top:226px;width:1728px;height:96px;border-bottom:2px solid {LINE};display:flex;flex-direction:row;gap:22px;align-items:center">'
         + f'<x-icon name="Settings" style="width:44px;height:44px;color:{GRAY}"></x-icon>' + p(f"font-size:32px;font-weight:700;color:{INK}", "컴퓨터에 설치한 파이썬")
         + p(f"font-size:26px;color:{GRAY}", "여기에 바로 넣으면 모든 프로젝트가 한 벌을 같이 써요") + '</div>')
for i, (name, ver, c) in enumerate([("project-a", "fastapi 0.162.2", BL), ("project-b", "fastapi 0.110.0", GR)]):
    x = 96 + i * 888
    o.append(f'<div{bi("rise", i + 1)} style="position:absolute;left:{x}px;top:380px;width:840px;height:380px;background:{CARD};border:2px solid {LINE};border-radius:22px;padding:30px 36px;display:flex;flex-direction:column;gap:22px">'
             + mono(e(name + "/"), 30, GRAY)
             + '<div style="display:flex;flex-direction:row;gap:18px;align-items:center">' + glyph("main.py") + mono("main.py", 28) + '</div>'
             + f'<div style="flex:1;background:#E4F3EA;border-radius:16px;padding:22px 28px;display:flex;flex-direction:column;gap:14px">'
             + '<div style="display:flex;flex-direction:row;gap:18px;align-items:center">' + glyph(".venv") + mono(".venv/", 28, GR) + '</div>'
             + chip(ver, c, 30, "#FFFFFF", extra="align-self:flex-start") + '</div></div>')
o.append(caption("프로젝트끼리 패키지 버전이 달라도 부딪히지 않아요. uv도 이 .venv를 그대로 써요.", 820, attrs=bi("fade", 3)))
W("venv", o, "가상환경은 프로젝트 폴더마다 따로 두는 패키지 상자예요. 상자 없이 컴퓨터 파이썬에 바로 넣으면 모든 프로젝트가 패키지 한 벌을 같이 써요. 그러면 A는 fastapi 0.162, B는 0.110이 필요할 때 둘 중 하나가 깨져요. 그래서 폴더마다 .venv라는 상자를 두고 그 안에 패키지를 넣어요. .venv는 점으로 시작해서 ls -a로만 보여요(01). uv도 이 .venv를 그대로 써요. 다른 건 누가 상자를 만들고 켜느냐예요.")

# map: where uv sits
o = [sec("map")] + head(EB2, "uv가 파이썬, 가상환경, 패키지 목록을 챙겨요", C2)
MAPN = {".python-version": "이 버전의 파이썬을 받아요", ".venv": "만들고, 실행할 때 켜요", "pyproject.toml": "넣은 패키지를 적어요", "uv.lock": "정확한 버전까지 적어요", "main.py": "내가 쓰는 코드"}
ff, rows, fh = folder([".python-version", ".venv", "main.py", "pyproject.toml", "uv.lock"], 1000, 226, 824, rh=112, note_map=MAPN, note_color=TEAL, pop=list(MAPN), build_new=None)
o += ff
mid = (rows[".venv"] + rows["pyproject.toml"]) / 2
o.append(f'<div style="position:absolute;left:96px;top:{mid - 90:.0f}px;width:280px;height:180px;background:{CARD};border:2px solid {LINE};border-radius:20px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px">'
         + f'<x-icon name="Archive" style="width:52px;height:52px;color:{PUR}"></x-icon>' + p(f"font-size:32px;font-weight:700;color:{PUR}", "PyPI") + p(f"font-size:22px;color:{GRAY}", "패키지 창고") + '</div>')
o.append(f'<div id="m-uv" style="position:absolute;left:500px;top:{mid - 110:.0f}px;width:240px;height:220px;background:{TEAL};border-radius:28px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px">'
         + mono("uv", 72, "#FFFFFF") + '</div>')
o.append(arrow_svg(392, mid, 484, mid, "#B9BFCB", None, kind="fade"))
for k, name in enumerate([".python-version", ".venv", "pyproject.toml", "uv.lock"]):
    o.append(arrow_svg(756, mid + (k - 1.5) * 40, 1006, rows[name], TEAL, k + 1, width=4))
o.append(note("이 목록만 있으면 다른 컴퓨터에서도 같은 .venv를 다시 만들어요.", 1000, 226 + fh + 28, 824, SUB, 26, attrs=bi("fade", 4)))
W("map", o, "uv는 파이썬 프로젝트에 필요한 세 가지를 한 번에 챙기는 도구예요. 첫째, 프로젝트가 쓸 파이썬이 없으면 받아요. 둘째, 가상환경 .venv를 만들고 실행할 때 켜요. 셋째, 넣은 패키지를 pyproject.toml과 uv.lock에 적어요. 이 목록 파일만 있으면 다른 컴퓨터에서도 같은 .venv를 다시 만들어요. 1장에서 lee가 막힌 문제가 셋째 덕분에 풀려요. uv는 Astral이라는 회사가 만든 무료 도구예요.")

# =====================================================================================
# 3. install
# =====================================================================================
o = [sec("install")] + head(EB3, "명령 한 줄로 uv를 설치해요", C3)
rws = [[("macOS", "font-weight:700"), ("터미널", f"color:{GRAY};font-size:26px"), ('<span style="font-family:' + MONO + ';font-weight:700">brew install uv</span>', "")],
       [("Windows", "font-weight:700"), ("PowerShell", f"color:{GRAY};font-size:26px"), ('<span style="font-family:' + MONO + ';font-weight:700">winget install --id=astral-sh.uv -e</span>', "")]]
tb, top = hrows(96, 220, [300, 300, 1128], rws, 128, 34, header=["컴퓨터", "여는 곳", "치는 명령"], rid="ins")
o += tb
o.append(note("Homebrew가 없으면 brew.sh의 설치 명령을 먼저 쳐요. winget은 Windows 10, 11에 들어 있어요.", 116, top + 2 * 128 + 18, 1700, GRAY, 26))
o.append(f'<div{bi("fade", 1)} style="position:absolute;left:96px;top:650px;display:flex;flex-direction:row;gap:20px;align-items:center">'
         + p(f"width:52px;height:52px;flex:none;border-radius:50%;background:{TEAL};color:#FFFFFF;font-size:28px;font-weight:900;line-height:52px;text-align:center", "!")
         + p(f"font-size:32px;font-weight:700;color:{INK}", "설치가 끝나면 터미널을 닫았다가 새로 열어요. Windows는 Git Bash를 새로 열어요.") + '</div>')
t = Term([("$", "uv --version"), ("o", "uv 0.11.32 (x86_64-unknown-linux-gnu)")], 96, 746, 1728, size=34, lh=56, attrs=bi("rise", 2))
o += t.parts
o.append(underline(3, t.tx(0), t.tx(10), t.ly(1) + 24, TEAL))
W("install", o, "uv 설치는 컴퓨터마다 한 번만 해요. Mac은 터미널에서 brew install uv를 쳐요. brew --version에 버전이 나오면 Homebrew가 이미 있어요. Windows는 시작 메뉴에서 PowerShell을 열어 winget 명령을 치고, 약관 동의를 물으면 Y를 쳐요. 설치가 끝나면 터미널을 새로 열어야 uv 명령을 찾아요. uv --version에 버전이 나오면 준비가 끝났어요. 숫자는 설치한 날에 따라 달라요. brew와 winget 설치 화면은 버전과 컴퓨터마다 달라서 옮기지 않았고, uv --version은 실제로 실행한 결과예요.",
  ("uv", "uv 설치하기"))

# =====================================================================================
# 4. uv init, uv run (smallest example)
# =====================================================================================
o = [sec("init")] + head(EB4, "uv init으로 프로젝트를 만들어요", C4)
t = Term([("$", "cd ~"), ("$", "uv init hello-uv"), ("o", "Downloading cpython-3.14.6-linux-x86_64-gnu"), ("o", "  (download) (34.3MiB)"), ("o", " Downloaded cpython-3.14.6-linux-x86_64-gnu"),
          ("g", "Initialized project `hello-uv`"), ("g", "  at `/home/kim/hello-uv`"), ("$", "cd hello-uv"), ("$", "ls -a")], 96, 220, 880, size=28, lh=54)
o += t.parts
ff, rows, fh = folder(FILES0, 1020, 220, 804, pop=FILES0, build_new=1, rh=82)
o += ff
o.append(note("← 파이썬이 없어서 받았어요", t.tx(23), t.ly(3) - 20, 410, "#7FD6DC", 26, attrs=bi("fade", 2), weight=700))
W("init", o, "uv init 뒤에 적은 이름으로 프로젝트 폴더가 생겨요. 수업 저장소 hello-git 안이 아니라 홈 폴더에서 시작해요. 컴퓨터에 파이썬이 없어서 uv가 3.14.6을 받았어요. 파이썬이 이미 있는 컴퓨터는 Downloading 줄이 없고 있던 버전을 써요. uv init은 git init까지 해 줘서 .git도 생겨요. 출력은 tools/demo.sh로 실제로 실행한 결과이고, 긴 줄은 화면 폭에 맞춰 두 줄로 나눴으며 ls -a 출력은 오른쪽 그림과 같아서 뺐어요.",
  ("init", "프로젝트 만들고 실행하기"))

o = [sec("init-files")] + head(EB4, "pyproject.toml은 프로젝트 설명서예요", C4)
py0 = ['[project]', 'name = "hello-uv"', 'version = "0.1.0"', 'description = "Add your description here"', 'readme = "README.md"', 'requires-python = ">=3.14"', 'dependencies = []']
cc, ys, chh = code_card("c-py", "pyproject.toml", py0, 96, 220, 1100, F_PY, 32, lh=54)
o += cc
xr = 96 + 1100
o += lead(1, xr + 90, ys[1], 96 + 30 + 17 * 32 * CW + 18, ys[1], "프로젝트 이름", F_PY, w=520)
o += lead(2, xr + 90, ys[5], 96 + 30 + 26 * 32 * CW + 18, ys[5], "쓸 수 있는 파이썬 버전", F_PY, w=520)
o += lead(3, xr + 90, ys[6], 96 + 30 + 17 * 32 * CW + 18, ys[6], "쓰는 패키지, 아직 없어요", F_PY, w=520)
cc2, ys2, ch2 = code_card("c-ver", ".python-version", ["3.14"], 96, 220 + chh + 36, 400, BL, 32, lh=50, attrs=bi("rise", 4))
o += cc2
o.append(note("이 폴더에서 쓸 파이썬 버전이에요. uv가 이 버전을 받아서 써요.", 540, 220 + chh + 36 + 40, 1100, SUB, 28, attrs=bi("fade", 4)))
W("init-files", o, "pyproject.toml은 이 프로젝트가 무엇이고 무엇이 필요한지 적은 설명서예요. name은 프로젝트 이름, requires-python은 쓸 수 있는 파이썬 버전이에요. dependencies는 이 프로젝트가 쓰는 패키지 목록이고, 지금은 비어 있어요. 이 파일은 손으로 고치지 않고 uv add, uv remove로 바꿔요. .python-version은 이 폴더에서 쓸 파이썬 버전이에요. main.py는 uv가 만들어 준 연습용 코드이고 다음 장에서 실행해요.")

o = [sec("run1")] + head(EB4, "uv run으로 실행해요", C4)
t = Term([("$", "uv run main.py"), ("o", "Using CPython 3.14.6"), ("o", "Creating virtual environment at: .venv"), ("H", "Hello from hello-uv!")], 96, 220, 860, size=27, lh=50)
o += t.parts
cc, ys, chh = code_card("c-main", "main.py", ["def main():", '    print("Hello from hello-uv!")', "", 'if __name__ == "__main__":', "    main()"], 96, 220 + t.h + 36, 860, BL, 25, lh=40)
o += cc
ff, rows, fh = folder(FILES1, 1000, 220, 824, new=(".venv", "uv.lock"), build_new=1)
o += ff
o.append(caption("처음 실행할 때 .venv와 uv.lock이 생겨요. activate는 치지 않아요.", 900, attrs=bi("fade", 2)))
W("run1", o, "uv run 뒤에 실행할 파일 이름을 적어요. 처음 실행하면 uv가 가상환경 .venv를 만들고, 그 안의 파이썬으로 main.py를 실행해요. 예전에 직접 치던 가상환경 만들기와 켜기를 uv run이 대신했어요. uv.lock은 패키지의 정확한 버전을 적는 파일이에요. 지금은 패키지가 없어서 거의 비어 있어요. main.py 맨 아래 두 줄은 이 파일을 직접 실행할 때 main()을 부르라는 뜻이고, 지금은 그대로 둬요.")

o = [sec("run2")] + head(EB4, "두 번째부터는 바로 실행돼요", C4)
t = Term([("$", "uv run main.py"), ("H", "Hello from hello-uv!")], 96, 220, 1728, size=40, lh=70)
o += t.parts
steps_ = [("켜요", ".venv 안의 파이썬을 골라요", GR), ("실행해요", "main.py를 읽고 실행해요", BL), ("꺼요", "끝나면 원래대로 돌아와요", GRAY)]
for i, (h_, s_, c) in enumerate(steps_):
    x = 96 + i * 600
    o.append(f'<div{bi("fade", i + 1)} style="position:absolute;left:{x}px;top:540px;width:520px;display:flex;flex-direction:column;gap:14px">'
             + '<div style="display:flex;flex-direction:row;gap:18px;align-items:center">'
             + p(f"width:60px;height:60px;flex:none;border-radius:50%;background:{c};color:#FFFFFF;font-size:30px;font-weight:900;line-height:60px;text-align:center", str(i + 1))
             + p(f"font-size:40px;font-weight:700;color:{c}", h_) + '</div>' + p(f"font-size:30px;line-height:1.45;color:{SUB};padding-left:78px", s_) + '</div>')
    if i < 2:
        o.append(arrow_svg(x + 420, 570, x + 560, 570, "#B9BFCB", i + 2, kind="fade"))
o.append(f'<div style="position:absolute;left:96px;top:500px;width:1728px;height:2px;background:{LINE}"></div>')
o.append(caption("uv run 한 줄이 이 세 가지를 해요. 프롬프트에 (hello-uv)가 붙지 않아서 끄는 걸 잊을 일이 없어요.", 800, attrs=bi("fade", 3)))
W("run2", o, "uv run은 .venv를 켜고, 실행하고, 끄는 일을 한 번에 해요. .venv가 이미 있어서 이번엔 결과만 나와요. 실행할 때만 .venv의 파이썬을 쓰고 끝나면 원래대로 돌아와서 프롬프트가 바뀌지 않아요. main.py를 고친 뒤에도 같은 명령으로 다시 실행해요. 출력은 tools/demo.sh로 실제로 실행한 결과예요.")

o = [sec("act")] + head(EB4, "가상환경을 직접 켤 수도 있어요", C4)
rws = [[("macOS, Linux", "font-weight:700;font-size:27px"), (f'<span style="font-family:{MONO};font-weight:700;color:{GR}">source .venv/bin/activate</span>', "font-size:26px")],
       [("Git Bash", "font-weight:700;font-size:27px"), (f'<span style="font-family:{MONO};font-weight:700;color:{GR}">source .venv/Scripts/activate</span>', "font-size:26px")],
       [("PowerShell", "font-weight:700;font-size:27px"), (f'<span style="font-family:{MONO};font-weight:700;color:{GR}">.venv\\Scripts\\activate</span>', "font-size:26px")],
       [("끄기", "font-weight:700;font-size:27px"), (f'<span style="font-family:{MONO};font-weight:700;color:{GRAY}">deactivate</span>', "font-size:26px")]]
tb, top = hrows(96, 220, [250, 600], rws, 118, header=["터미널", "켜기"], rid="act")
o += tb
t = Term([("$", "source .venv/bin/activate"), ("A", "which python"), ("o", "/home/kim/hello-uv/.venv/bin/python"), ("A", "python main.py"), ("H", "Hello from hello-uv!"),
          ("A", "deactivate"), ("$", "")], 1000, 220, 824, size=27, lh=62, attrs=bi("rise", 1))
o += t.parts
for k in (1, 3, 5):
    o.append(box(2, t.tx(0) - 8, t.lt(k) + 8, 10 * 27 * CW + 16, t.lh - 16, GR, width=4))
o.append(note("켜면 프롬프트 앞에 (hello-uv)가 붙어요.", 1000, t.y + t.h + 24, 824, GR, 28, attrs=bi("fade", 2), weight=700))
o.append(caption("켜는 걸 잊어도 uv run은 늘 동작해요. 수업 실습은 uv run으로 적어요.", 900, attrs=bi("fade", 3)))
W("act", o, "uv가 만든 .venv도 예전 방식과 같은 가상환경이라 activate로 직접 켤 수 있어요. 켜면 프롬프트 앞에 프로젝트 이름 (hello-uv)가 붙어요. which python으로 보면 .venv 안의 python을 쓰고 있어요. 켠 상태에서는 uv run 없이 python main.py로 실행해도 돼요. Windows Git Bash는 bin 대신 Scripts 폴더예요. PowerShell에서 스크립트 실행이 막혔다는 오류가 나면 Git Bash에서 쳐요. 다 쓰면 deactivate로 꺼요. 출력은 tools/demo.sh로 실제로 실행한 결과이고, 폴더 주소는 01처럼 /home/kim으로 바꿨어요.")

o = [sec("pyver")] + head(EB4, "파이썬 버전은 .python-version이 정해요", C4)
t = Term([("$", "cd ~"), ("$", "uv init --python 3.13 hello-313"), ("o", "Initialized project `hello-313` at `/home/kim/hello-313`"), ("$", "cd hello-313"),
          ("$", "cat .python-version"), ("H", "3.13"), ("$", "uv run python --version"), ("o", "Downloading cpython-3.13.14-linux-x86_64-gnu (download) (33.2MiB)"),
          ("o", " Downloaded cpython-3.13.14-linux-x86_64-gnu (download)"), ("o", "Using CPython 3.13.14"), ("o", "Creating virtual environment at: .venv"), ("H", "Python 3.13.14")],
         96, 220, 1728, size=27, lh=50)
o += t.parts
o += lead(1, 1300, t.ly(1), t.tx(34) + 16, t.ly(1), "버전을 정해서 만들어요", C4, w=500)
o += lead(2, 1300, t.ly(4) + 4, t.tx(66) + 16, t.ly(7), "없는 버전은 uv가 받아요", C4, w=500)
W("pyver", o, "보기만 해도 되는 장이에요. 수업 프로젝트는 uv init 이름으로 만들면 돼요. 회사나 강의에서 파이썬 버전을 정해 줄 때 --python 버전을 붙여요. 이 컴퓨터에 3.13이 없어서 uv가 받아 왔어요. 폴더마다 버전이 달라도 그 폴더에서 uv run을 치면 그 폴더의 버전으로 실행돼요. 출력은 tools/demo.sh로 실제로 실행한 결과예요.")

# =====================================================================================
# 5. uv add, uv tree, uv remove
# =====================================================================================
o = [sec("add")] + head(EB5, "uv add로 패키지를 넣어요", C5)
lines = [("$", "uv add fastapi"), ("o", "Resolved 12 packages in 1.77s"), ("o", "Downloading pydantic-core (2.2MiB)"), ("o", " Downloaded pydantic-core"), ("o", "Prepared 11 packages in 437ms"),
         ("H", "Installed 11 packages in 5ms")] + [("g", " + " + x) for x in PKGS]
t = Term(lines, 96, 210, 880, size=24, lh=44, tid="t-add")
o += t.parts
o.append(f'<p id="tok-fast" style="position:absolute;left:{t.tx(9):.0f}px;top:{t.lt(0):.0f}px;font-family:{MONO};font-size:24px;line-height:44px;color:transparent">fastapi</p>')
o += three({"py": ('"fastapi>=0.162.2",', "dependencies 칸에 적혀요", INK), "lock": ("고른 1개 + 따라온 10개", "pydantic 2.14.3, starlette 1.10.0 …", INK),
            "venv": ("패키지 11개 설치", "uv run으로 실행하면 바로 써요", INK)}, 1020, 210, 804,
           attrs_by={"py": ' data-build-in="fly order 1" data-from="tok-fast"', "lock": bi("rise", 2), "venv": bi("rise", 3)})
W("add", o, "uv add는 명령 하나로 세 곳을 함께 바꿔요. pyproject.toml의 dependencies 칸에 fastapi를 적고, uv.lock에 정확한 버전을 적고, .venv에 설치해요. 예전의 pip install과 목록 적기를 합친 일이에요. >=0.162.2는 0.162.2 이상이면 된다는 뜻이고, 실제로 쓸 버전은 uv.lock이 정해요. Downloading pydantic-core 줄은 크기가 큰 패키지를 받을 때만 보여요. hello-uv 폴더에서 쳐요. 출력은 tools/demo.sh로 실제로 실행한 결과예요.",
  ("add", "패키지 넣고 빼기"))

o = [sec("tree")] + head(EB5, "하나를 넣었는데 11개가 들어왔어요", C5)
TREE = ["annotated-doc v0.0.5", "opentelemetry-api v1.45.2", "pydantic v2.14.3", "starlette v1.10.0", "typing-extensions v4.16.0", "typing-inspection v0.4.5"]
t = Term([("$", "uv tree --depth 2"), ("o", "Resolved 12 packages in 1ms"), ("o", "hello-uv v0.1.0"), ("H", "└── fastapi v0.162.2")]
         + [("o", ("    └── " if i == len(TREE) - 1 else "    ├── ") + x) for i, x in enumerate(TREE)], 96, 220, 840, size=32, lh=56)
o += t.parts
o += lead(1, 1060, t.ly(3), t.x + t.w + 16, t.ly(3), "내가 고른 패키지", C5, w=700)
bx_ = t.tx(33) + 44
o.append(f'<svg{bi("fade", 2)} viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible">'
         f'<path d="M{bx_:.0f},{t.lt(4) + 10:.0f} q14,0 14,14 L{bx_ + 14:.0f},{t.lt(10) - 24:.0f} q0,14 -14,14" fill="none" stroke="{C5}" stroke-width="3"/></svg>')
o += lead(2, 1060, (t.lt(4) + t.lt(10)) / 2, bx_ + 22, (t.lt(4) + t.lt(10)) / 2, "fastapi가 쓰는 패키지 6개", C5, w=700, dot=False)
o.append(note("그 아래 단계에서 4개가 더 들어와서 모두 11개예요.", 1060, (t.lt(4) + t.lt(10)) / 2 + 40, 764, SUB, 28, attrs=bi("fade", 2)))
o.append(caption("pyproject.toml에는 내가 고른 fastapi 하나만 적혀요. 뺄 때는 따라온 것까지 함께 빠져요.", 920, attrs=bi("fade", 3)))
W("tree", o, "uv tree는 어떤 패키지가 어떤 패키지 때문에 들어왔는지 나무 모양으로 보여 줘요. 01에서 본 폴더 지도와 같은 모양이에요. --depth 2는 두 단계까지만 보여 달라는 뜻이에요. fastapi가 바로 쓰는 패키지가 여섯 개이고, 그 아래 단계에서 pydantic-core, anyio, idna, annotated-types 네 개가 더 들어와요. fastapi는 데이터 검사를 pydantic에, 웹 요청 처리를 starlette에 맡겨요. 출력은 tools/demo.sh로 실제로 실행한 결과예요.")

o = [sec("use")] + head(EB5, "넣은 패키지를 코드에서 불러와요", C5)
cc, ys, chh = code_card("c-main", "main.py", MAIN_REQ, 96, 220, 1100, BL, 40, lh=68)
o += cc
t = Term([("$", "uv run main.py"), ("H", "fastapi 버전: 0.162.2")], 96, 220 + chh + 40, 1100, size=40, lh=70, attrs=bi("rise", 2))
o += t.parts
o += lead(1, 1290, ys[0], 96 + 30 + 14 * 40 * CW + 16, ys[0], ".venv에서 fastapi를 찾아 불러와요", C5, w=530, size=28)
o += lead(3, 1290, t.ly(1), t.tx(21) + 30, t.ly(1), "불러온 fastapi의 버전", C5, w=530, size=28)
o.append(caption("uv add로 넣은 패키지는 uv run으로 실행하면 바로 불러와요.", 900, attrs=bi("fade", 3)))
W("use", o, "main.py를 이 세 줄로 바꿔 저장하고 uv run으로 실행해요. import fastapi는 .venv에 설치된 fastapi를 불러오라는 뜻이에요. 불러온 fastapi의 버전을 print로 찍었어요. uv run이 .venv 안의 파이썬으로 실행해서 fastapi를 찾아요. fastapi로 웹 서버를 만들고 켜는 건 뒤 수업에서 해요. 출력은 tools/demo.sh로 실제로 실행한 결과예요.")

o = [sec("remove")] + head(EB5, "uv remove로 패키지를 빼요", C5)
lines = [("$", "uv remove fastapi"), ("o", "Resolved 1 package in 2ms"), ("H", "Uninstalled 11 packages in 15ms")] + [("r", " - " + x) for x in PKGS[:4]] \
    + [("#", "   … 6줄 생략 …"), ("r", " - " + PKGS[-1]), ("$", "uv run main.py"), ("o", "Traceback (most recent call last):"), ("o", "  …"), ("E", "ModuleNotFoundError: No module named 'fastapi'")]
t = Term(lines, 96, 210, 880, size=24, lh=44)
o += t.parts
o += three({"py": ("dependencies = []", "fastapi 줄이 지워져요", RED), "lock": ("프로젝트만 남아요", "따라왔던 10개도 지워요", RED),
            "venv": ("패키지 11개 삭제", "딸린 패키지까지 같이 빠져요", RED)}, 1020, 210, 804,
           attrs_by={"py": bi("fade", 1), "lock": bi("fade", 2), "venv": bi("fade", 3)})
o.append(box(4, t.tx(0) - 10, t.lt(12) + 2, 46 * 24 * CW + 20, t.lh - 4, RED))
W("remove", o, "uv remove는 uv add를 거꾸로 해서 세 곳에서 함께 빼요. pyproject.toml에서 지우고, uv.lock과 .venv에서도 빼요. 함께 들어왔던 10개도 다른 패키지가 쓰지 않으면 같이 빠져요. main.py는 아직 fastapi를 불러오고 있어서 실행하면 ModuleNotFoundError가 나요. 다음 장에서 다시 넣어요. 출력은 tools/demo.sh로 실제로 실행한 결과이고, 지운 목록 가운데 6줄과 Traceback 가운데 두 줄은 뺐어요.")

o = [sec("again")] + head(EB5, "다시 넣으면 받지 않고 바로 들어가요", C5)
t = Term([("$", "uv add fastapi"), ("o", "Resolved 12 packages in 8ms"), ("H", "Installed 11 packages in 2ms")] + [("g", " + " + x) for x in PKGS[:3]]
         + [("#", "   … 7줄 생략 …"), ("g", " + " + PKGS[-1]), ("$", "uv run main.py"), ("o", "fastapi 버전: 0.162.2")], 96, 220, 1100, size=30, lh=54)
o += t.parts
o += lead(1, 1290, t.ly(2), t.x + t.w + 16, t.ly(2), "11개가 0.002초 만에", C5, w=530, size=30)
o.append(f'<div{bi("fade", 2)} style="position:absolute;left:1290px;top:{t.ly(2) + 70:.0f}px;width:534px;display:flex;flex-direction:column;gap:12px">'
         + p(f"font-size:26px;font-weight:700;color:{GRAY}", "처음 넣을 때 있던 줄")
         + p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{GRAY};text-decoration:line-through;text-decoration-thickness:3px", "Prepared 11 packages in 437ms")
         + p(f"font-size:28px;line-height:1.45;color:{SUB}", "한 번 받은 패키지는 uv 캐시에 있어서 다시 받지 않아요.") + '</div>')
W("again", o, "앞에서 뺀 fastapi를 다시 넣었어요. 처음 넣을 때는 인터넷에서 받아 준비하는 Prepared 줄이 있었어요. 이번엔 uv 캐시라는 보관함에 있어서 받지 않고 바로 설치했어요. 프로젝트를 여러 개 만들어도 같은 패키지는 한 번만 받아요. 다시 넣었으니 main.py도 다시 동작해요. 출력은 tools/demo.sh로 실제로 실행한 결과이고, 설치 목록 가운데 7줄은 뺐어요.")

# =====================================================================================
# 6. GitHub, uv sync
# =====================================================================================
UP = [".gitignore", ".python-version", "README.md", "main.py", "pyproject.toml", "uv.lock"]
o = [sec("commit")] + head(EB6, ".venv는 GitHub에 올리지 않아요", C6)
t = Term([("$", "git status --short")] + [("r", "?? " + f) for f in UP] + [("$", "git add ."), ("$", 'git commit -m "feat: hello-uv 프로젝트 만들기"'),
         ("o", "[main (root-commit) a61cccf] feat: hello-uv"), ("o", "  프로젝트 만들기")], 96, 220, 880, size=26, lh=46)
o += t.parts
ff, rows, fh = folder([".gitignore", ".python-version", ".venv", "README.md", "main.py", "pyproject.toml", "uv.lock"], 1020, 220, 804, off=(".venv",), notes=False, pre="u")
o += ff
o += lead(1, 1450, rows[".venv"], 1020 + 16 + 16 + 30 + 18 + 6 * 27 * CW + 18, rows[".venv"], ".gitignore가 막아요", RED, w=360, size=26)
o.append(caption("pyproject.toml, uv.lock, .python-version만 있으면 .venv는 똑같이 다시 만들어요.", 870, attrs=bi("fade", 2)))
W("commit", o, "git status에 .venv가 없어요. uv init이 만든 .gitignore에 .venv가 적혀 있어서예요(04). .venv는 컴퓨터마다 다시 만들 수 있고 크기도 커서 올리지 않아요. 대신 pyproject.toml, uv.lock, .python-version은 꼭 같이 올려요. 이 세 파일이 다른 컴퓨터에서 같은 환경을 만드는 설명서예요. git add .는 지금 폴더의 바뀐 파일을 모두 대기실에 올린다는 뜻이에요. 출력은 tools/demo.sh로 실제로 실행한 결과이고, 커밋 줄은 화면 폭 때문에 두 줄로 나눴어요.",
  ("sync", "다른 컴퓨터에서 그대로"))

o = [sec("sync-flow")] + head(EB6, "lee 컴퓨터에서는 uv sync 한 번이면 돼요", C6)
cols = [("kim 컴퓨터", KIM, "#EEF3FC", 96), ("GitHub", HUB, "#F3EFFC", 700), ("lee 컴퓨터", LEE, "#ECF6F0", 1304)]
for who, c, bg, x in cols:
    o.append(f'<div style="position:absolute;left:{x}px;top:220px;width:520px;height:520px;background:{bg};border-radius:24px"></div>')
    o.append(p(f"position:absolute;left:{x + 32}px;top:248px;width:460px;font-size:34px;font-weight:700;color:{c}", who))


def fchip(fid, name, x, y, c, attrs="", off=False, bg="#FFFFFF"):
    deco = "text-decoration:line-through;text-decoration-thickness:3px;color:#9AA0AB;" if off else f"color:{c};"
    return (f'<div id="{fid}"{attrs} style="position:absolute;left:{x}px;top:{y}px;height:64px;background:{bg};border:2px solid {LINE};border-radius:12px;'
            f'padding:0 22px;display:flex;align-items:center">' + p(f"font-family:{MONO};font-size:28px;font-weight:700;white-space:nowrap;{deco}", e(name)) + '</div>')


o.append(fchip("k-py", "pyproject.toml", 128, 330, INK))
o.append(fchip("k-lock", "uv.lock", 128, 414, INK))
o.append(fchip("k-venv", ".venv", 128, 498, INK, bg="#E4F3EA"))
o.append(fchip("g-py", "pyproject.toml", 732, 330, INK, attrs=' data-build-in="fly order 1" data-from="k-py"'))
o.append(fchip("g-lock", "uv.lock", 732, 414, INK, attrs=' data-build-in="fly order 1" data-from="k-lock"'))
o.append(note("git push origin main", 128, 676, 460, KIM, 26, attrs=bi("fade", 1), weight=700))
o.append(note("git clone 주소", 732, 676, 460, HUB, 26, attrs=bi("fade", 2), weight=700))
o.append(fchip("l-py", "pyproject.toml", 1336, 330, INK, attrs=' data-build-in="fly order 2" data-from="g-py"'))
o.append(fchip("l-lock", "uv.lock", 1336, 414, INK, attrs=' data-build-in="fly order 2" data-from="g-lock"'))
o.append(fchip("l-venv", ".venv", 1336, 498, GR, attrs=bi("pop", 3), bg="#E4F3EA"))
o.append(p(f"position:absolute;left:1336px;top:590px;width:460px;font-family:{MONO};font-size:30px;font-weight:700;color:{LEE}", "$ uv sync", bi("fade", 3)))
o.append(note("파이썬 받기, .venv 만들기, 패키지 11개 설치", 1336, 640, 460, SUB, 26, attrs=bi("fade", 3)))
o.append(note(".venv는 올라가지 않아요", 128, 590, 460, GRAY, 26))
o.append(caption("uv.lock에 적힌 버전 그대로 설치돼서 kim과 lee의 환경이 같아져요.", 800, attrs=bi("fade", 4)))
W("sync-flow", o, "lee는 uv sync 한 번으로 kim과 같은 .venv를 만들어요. 06의 팀 레포처럼 kim이 프로젝트를 GitHub에 올리고 lee가 clone했어요. GitHub에는 .venv가 없으니 lee 컴퓨터에도 없어요. uv sync가 .python-version의 파이썬을 받고, .venv를 만들고, uv.lock에 적힌 버전 그대로 패키지를 설치해요. 1장에서 python3 main.py가 실패한 lee 컴퓨터가 이 방법으로 풀려요.")

o = [sec("sync-term")] + head(EB6, "lee 컴퓨터에서 uv sync를 쳐 봐요", C6)
o.append(tag("lee 컴퓨터", LEE, 96, 196))
t = Term([("$", "git clone https://github.com/kim/hello-uv.git"), ("$", "cd hello-uv"), ("$", "uv sync"), ("o", "Downloading cpython-3.14.6-linux-x86_64-gnu (download) (34.3MiB)"),
          ("o", " Downloaded cpython-3.14.6-linux-x86_64-gnu (download)"), ("o", "Using CPython 3.14.6"), ("o", "Creating virtual environment at: .venv"),
          ("o", "Resolved 12 packages in 1ms"), ("o", "Prepared 11 packages in 5.63s"), ("H", "Installed 11 packages in 4ms"), ("g", " + annotated-doc==0.0.5"), ("#", "   … 10줄 생략 …"),
          ("$", "uv run main.py"), ("H", "fastapi 버전: 0.162.2")], 96, 248, 1300, size=25, lh=46)
o += t.parts
for k, (ln, txt) in enumerate([(3, "파이썬 받기"), (6, ".venv 만들기"), (9, "패키지 11개 설치")]):
    o += lead(k + 1, 1460, t.ly(ln), t.x + t.w + 16, t.ly(ln), txt, LEE, w=360, size=28)
W("sync-term", o, "lee 컴퓨터에는 파이썬도 패키지도 없는 상태에서 시작했어요. uv sync가 파이썬 3.14.6을 받고, .venv를 만들고, 패키지 11개를 설치했어요. 버전은 kim 컴퓨터와 똑같아요. 1장에서 실패했던 uv run main.py가 이제 fastapi 버전을 찍어요. 출력은 tools/demo.sh로 실제로 실행한 결과이고, clone 출력과 pydantic-core를 받는 줄, 설치 목록 10줄은 뺐어요.")

o = [sec("sync-when")] + head(EB6, "uv sync는 이럴 때 쳐요", C6)
mk = lambda s: f'<span style="font-family:{MONO};font-weight:700">{e(s)}</span>'
why_c = f"font-size:27px;line-height:1.45;color:{SUB}"
rws = [[("1", f"font-size:36px;font-weight:900;color:{GR}"), ("clone한 직후", "font-weight:700"), (mk("git clone 주소") + "<br>" + mk("cd 폴더") + "<br>" + mk("uv sync"), "font-size:28px;line-height:1.6"), ("받은 폴더에는 .venv가 없어요", why_c)],
       [("2", f"font-size:36px;font-weight:900;color:{GR}"), ("pull로 uv.lock이 바뀐 뒤", "font-weight:700"), (mk("git pull origin main") + "<br>" + mk("uv sync"), "font-size:28px;line-height:1.6"), ("목록은 바뀌었지만 내 .venv는 그대로예요", why_c)],
       [("3", f"font-size:36px;font-weight:900;color:{GRAY}"), ("잊었다면", "font-weight:700"), (mk("uv run main.py"), "font-size:28px;line-height:1.6"), ("uv run이 실행 전에 sync를 알아서 해요", why_c)]]
tb, top = hrows(96, 220, [110, 560, 520, 538], rws, 196, 34, header=["", "언제", "치는 명령", "왜"], attrs_by_row={0: bi("fade", 1), 1: bi("fade", 2), 2: bi("fade", 3)})
o += tb
W("sync-when", o, "uv sync는 받은 프로젝트를 처음 열 때와 팀원이 패키지를 바꿨을 때 쳐요. 1번은 다른 사람 프로젝트를 처음 받았을 때예요. 2번은 팀원이 uv add로 패키지를 넣고 push한 경우예요. pull로 pyproject.toml과 uv.lock은 바뀌었지만 내 .venv에는 아직 그 패키지가 없어요. 3번처럼 uv run도 실행 전에 같은 일을 해서, sync를 잊어도 uv run이면 돌아가요. 그래도 처음 받을 땐 uv sync로 설치가 끝났는지 눈으로 확인해요. 34쪽에서 2번을 실제로 해 봐요.")

# =====================================================================================
# 7. Jupyter in VS Code (pages 25-27 are cited by later chapters)
# =====================================================================================
o = [sec("jup-what")] + head(EB7, "노트북은 코드를 셀 단위로 실행해요", C7)
o.append(p(f"position:absolute;left:96px;top:214px;width:1100px;font-family:{MONO};font-size:28px;font-weight:700;color:{JP}", "notebook.ipynb"))
y0 = 270
for i, (code, out) in enumerate([("데이터 읽기", "표 5줄"), ("정리하기", "빈칸 3개 지움"), ("그래프 그리기", "그래프 그림")]):
    cp, chh_, cch = cell(i + 1, [code], out, 96, y0 + i * 186, 1100, attrs=bi("rise", i + 1), size=30)
    o += cp
o += lead(4, 1290, y0 + 30, 96 + 1100 + 14, y0 + 30, "셀: 코드를 나눠 담는 칸", JP, w=530)
o += lead(4, 1290, y0 + 104, 96 + 112 + 6 * 30 * CW + 14, y0 + 104, "결과가 바로 아래에 남아요", JP, w=530)
o.append(f'<div{bi("fade", 5)} style="position:absolute;left:1290px;top:640px;width:534px;display:flex;flex-direction:column;gap:12px">'
         + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{BL}", "main.py") + p(f"font-size:28px;line-height:1.45;color:{SUB}", "처음부터 끝까지 한 번에 실행하고, 결과는 터미널에 모여요.") + '</div>')
W("jup-what", o, "Jupyter 노트북은 코드를 셀이라는 칸으로 나눠 하나씩 실행하는 파일이에요. 확장자는 .ipynb예요. 셀마다 따로 실행하고, 결과는 그 셀 바로 아래에 남아요. 앞 셀에서 만든 값은 뒤 셀에서 그대로 써요. 그래서 데이터를 읽고 모양을 보고, 고치고 다시 보는 머신러닝 실습에 잘 맞아요. VS Code 안에서 노트북을 열 수 있어서 따로 프로그램을 설치하지 않아요. 그림 속 셀 내용은 예시예요.",
  ("jupyter", "VS Code에서 Jupyter 쓰기"))

# jup-ext: a simplified VS Code; the pointer clicks in order
o = [sec("jup-ext")] + head(EB7, "VS Code에 확장 두 개를 설치해요", C7)
o.append(f'<div style="position:absolute;left:96px;top:214px;width:1120px;height:700px;background:#1F2430;border-radius:22px;overflow:hidden"></div>')
o.append('<div style="position:absolute;left:96px;top:214px;width:96px;height:700px;background:#181C25;border-radius:22px 0 0 22px"></div>')
for k in range(4):
    o.append(f'<div style="position:absolute;left:124px;top:{250 + k * 72}px;width:40px;height:40px;border-radius:8px;background:#3A4150"></div>')
o.append(f'<div id="vx-ext" style="position:absolute;left:118px;top:538px;width:52px;height:52px;border-radius:10px;border:3px solid #F2C46D;display:flex;align-items:center;justify-content:center">'
         f'<x-icon name="Archive" style="width:30px;height:30px;color:#F2C46D"></x-icon></div>')
o.append(p("position:absolute;left:226px;top:244px;width:600px;font-size:22px;font-weight:700;letter-spacing:1px;color:#AEB6C4", "EXTENSIONS"))
o.append(p(f"position:absolute;left:226px;top:292px;width:956px;font-family:{MONO};font-size:26px;line-height:1.5;color:#E6E9EF;background:#2B3140;border:2px solid #4A90E2;border-radius:8px;padding:8px 18px", "Python"))
for k, (n, c, sub) in enumerate([("Python", "#3A6FB0", "Microsoft · Python 코드 실행"), ("Jupyter", JP, "Microsoft · .ipynb 노트북 열기")]):
    yy = 384 + k * 150
    o.append(f'<div style="position:absolute;left:226px;top:{yy}px;width:956px;height:126px;background:#262C39;border-radius:14px;padding:0 24px;display:flex;flex-direction:row;gap:22px;align-items:center">'
             + f'<div style="width:72px;height:72px;flex:none;border-radius:14px;background:{c}"></div>'
             + '<div style="flex:1;display:flex;flex-direction:column;gap:6px">' + p("font-size:32px;font-weight:700;color:#FFFFFF", n) + p("font-size:24px;color:#AEB6C4", sub) + '</div>'
             + p("font-size:24px;font-weight:700;color:#FFFFFF;background:#2F7D32;border-radius:8px;padding:8px 22px", "Install", f' id="vx-in{k}"') + '</div>')
for k in range(2):
    yy = 684 + k * 110
    o.append(f'<div style="position:absolute;left:226px;top:{yy}px;width:956px;height:90px;border-radius:14px;padding:0 24px;display:flex;flex-direction:row;gap:22px;align-items:center">'
             + '<div style="width:56px;height:56px;flex:none;border-radius:12px;background:#323949"></div>'
             + '<div style="display:flex;flex-direction:column;gap:12px">' + f'<div style="width:{[260, 200][k]}px;height:14px;border-radius:7px;background:#3A4150"></div>'
             + f'<div style="width:{[380, 320][k]}px;height:10px;border-radius:5px;background:#30363F"></div></div></div>')
o.append(cursor(1, target="vx-ext"))
o.append(cursor(2, target="vx-in0"))
o.append(cursor(3, target="vx-in1"))
o.append(cursor_off(4))
stp = [("확장 아이콘을 눌러요", "Mac Cmd+Shift+X<br>Windows Ctrl+Shift+X"), ("Python을 검색해 Install", "만든 곳이 Microsoft인지 봐요"), ("Jupyter를 검색해 Install", "다 되면 VS Code를 다시 열어요")]
for k, (a_, b_) in enumerate(stp):
    yy = 214 + k * 234
    o.append(f'<div{bi("fade", k + 1)} style="position:absolute;left:1270px;top:{yy}px;width:554px;height:{234 if k < 2 else 210}px;{"border-bottom:2px solid " + LINE + ";" if k < 2 else ""}padding-top:20px;display:flex;flex-direction:row;gap:20px">'
             + p(f"width:52px;height:52px;flex:none;border-radius:50%;background:{JP};color:#FFFFFF;font-size:26px;font-weight:900;line-height:52px;text-align:center", str(k + 1))
             + '<div style="display:flex;flex-direction:column;gap:10px">' + p(f"font-size:32px;font-weight:700;line-height:1.3;color:{INK}", a_) + p(f"font-size:26px;line-height:1.45;color:{SUB}", b_) + '</div></div>')
W("jup-ext", o, "확장은 VS Code에 기능을 더하는 프로그램이고, 노트북에는 Python과 Jupyter 두 개가 필요해요. 05에서 Git Graph를 설치한 것과 같은 화면이에요. Python 확장은 파이썬 코드를 읽고 실행하는 기능, Jupyter 확장은 .ipynb 노트북을 여는 기능이에요. 둘 다 만든 곳이 Microsoft인 것을 골라요. 이름이 비슷한 다른 확장이 많아요. Python을 설치하면 Pylance 같은 확장이 함께 깔리는데 그대로 둬요. 컴퓨터마다 한 번만 설치해요. 왼쪽 그림은 실제 화면을 단순하게 그린 거예요.")

o = [sec("jup-kernel")] + head(EB7, "uv add --dev ipykernel로 커널을 넣어요", C7)
t = Term([("$", "cd ~/hello-uv"), ("$", "uv add --dev ipykernel"), ("o", "Resolved 44 packages in 1.43s"), ("#", "  … Downloading 줄 생략 …"), ("o", "Prepared 28 packages in 7.29s"),
          ("H", "Installed 28 packages in 61ms"), ("g", " + asttokens==3.0.2"), ("g", " + comm==0.2.3"), ("#", "   … 25줄 생략 …"), ("g", " + wcwidth==0.9.4")], 96, 220, 860, size=27, lh=48)
o += t.parts
cc, ys, chh = code_card("c-py", "pyproject.toml", ["dependencies = [", '    "fastapi>=0.162.2",', "]", "", "[dependency-groups]", "dev = [", '    "ipykernel>=7.4.0",', "]"],
                        1000, 220, 824, F_PY, 27, lh=46, marks=(4, 5, 6, 7), attrs=bi("rise", 1))
o += cc
o.append(note("--dev로 넣은 도구는 [dependency-groups]의 dev 칸에 따로 적혀요.", 1000, 220 + chh + 22, 824, F_PY, 28, attrs=bi("fade", 2), weight=700))
o.append(caption("커널은 노트북 셀을 실행하는 파이썬이에요. 노트북도 .venv 안의 파이썬으로 실행하려고 ipykernel을 .venv에 넣어요.", 860, attrs=bi("fade", 3)))
W("jup-kernel", o, "노트북의 셀은 커널이라는 파이썬 프로그램이 실행해요. VS Code가 hello-uv의 .venv를 커널로 쓰려면 .venv 안에 ipykernel 패키지가 있어야 해요. --dev를 붙이면 dependencies가 아니라 dependency-groups의 dev 칸에 적혀요. main.py 실행에 꼭 필요한 패키지와 개발할 때만 쓰는 도구를 나눠 두는 거예요. uv sync는 dev 칸도 함께 설치해서, lee 컴퓨터에서도 uv sync 한 번이면 노트북을 열 수 있어요. 출력은 tools/demo.sh로 실제로 실행한 결과이고, 받는 줄과 설치 목록 가운데는 뺐어요.")

# jup-pick: spotlight walks the kernel picker
o = [sec("jup-pick")] + head(EB7, "노트북을 만들고 커널로 .venv를 골라요", C7)
picks = [("File > Open Folder로 hello-uv 열기", "폴더 자체를 열어요"), ("탐색기에서 새 파일 notebook.ipynb", "이름 끝이 .ipynb면 노트북으로 열려요"),
         ("오른쪽 위 Select Kernel", ""), ("Python Environments", ""), (".venv (Python 3.14.6)", "hello-uv 안의 .venv예요")]
for i, (a_, b_) in enumerate(picks):
    yy = 214 + i * 150
    o.append(f'<div style="position:absolute;left:96px;top:{yy}px;width:760px;height:150px;{"border-bottom:2px solid " + LINE + ";" if i < 4 else ""}display:flex;flex-direction:row;gap:22px;align-items:center">'
             + p(f"width:52px;height:52px;flex:none;border-radius:50%;background:{JP};color:#FFFFFF;font-size:26px;font-weight:900;line-height:52px;text-align:center", str(i + 1))
             + '<div style="flex:1;display:flex;flex-direction:column;gap:6px">' + p(f"font-size:30px;font-weight:700;color:{INK}", e(a_))
             + (p(f"font-size:24px;color:{SUB}", e(b_)) if b_ else "") + '</div></div>')
o.append(f'<div style="position:absolute;left:920px;top:214px;width:904px;height:720px;background:#1F2430;border-radius:22px;overflow:hidden"></div>')
o.append(f'<div style="position:absolute;left:920px;top:214px;width:904px;height:80px;background:#181C25;border-radius:22px 22px 0 0;display:flex;flex-direction:row;align-items:center;padding:0 28px;gap:16px">'
         + p(f"flex:1;font-family:{MONO};font-size:24px;color:#AEB6C4", "notebook.ipynb")
         + p("font-size:24px;font-weight:700;color:#FFFFFF;border:2px solid #F2C46D;border-radius:8px;padding:6px 16px", "Select Kernel", ' id="vp-sel"') + '</div>')
o.append(f'<div style="position:absolute;left:950px;top:324px;width:844px;height:226px;background:#2B3140;border:2px solid #4A90E2;border-radius:12px;padding:18px;display:flex;flex-direction:column;gap:10px">'
         + p("font-size:24px;color:#AEB6C4", "Select Another Kernel")
         + p("font-size:28px;font-weight:700;color:#FFFFFF;background:#36507A;border-radius:8px;padding:10px 18px", "Python Environments...", ' id="vp-env"')
         + p("font-size:28px;color:#C9CED8;padding:10px 18px", "Existing Jupyter Server...") + '</div>')
o.append(f'<div style="position:absolute;left:950px;top:580px;width:844px;height:240px;background:#2B3140;border:2px solid #4A90E2;border-radius:12px;padding:18px;display:flex;flex-direction:column;gap:10px">'
         + f'<div id="vp-venv" style="background:#36507A;border-radius:8px;padding:12px 18px;display:flex;flex-direction:column;gap:4px">'
         + p("font-size:28px;font-weight:700;color:#FFFFFF", "★ .venv (Python 3.14.6)") + p(f"font-family:{MONO};font-size:22px;color:#AEB6C4", ".venv/bin/python") + '</div>'
         + p("font-size:26px;color:#C9CED8;padding:8px 18px", "Python 3.12 (/usr/bin/python3)") + '</div>')
o.append(spot(1, target="vp-sel", pad=10, r=12))
o.append(spot(2, target="vp-env", pad=8, r=12))
o.append(spot(3, target="vp-venv", pad=8, r=12))
o.append(spot_off(4))
o.append(caption("커널을 한 번 고르면 이 노트북을 열 때마다 기억해요.", 966, left=920, w=904, attrs=bi("fade", 4)))
W("jup-pick", o, "노트북 커널은 꼭 hello-uv 안의 .venv를 골라요. VS Code는 열린 폴더 안의 .venv를 찾아서 목록 맨 위에 별표로 보여 줘요. 그래서 hello-uv의 부모 폴더가 아니라 hello-uv 폴더 자체를 열어요. Mac 메뉴에 Open Folder가 없으면 File > Open...으로 폴더를 골라요. Windows는 경로가 .venv\\Scripts\\python.exe로 보여요. 컴퓨터에 다른 파이썬이 있으면 목록에 여러 줄이 나오는데, 꼭 .venv를 골라요. 오른쪽 그림은 실제 화면을 단순하게 그린 거예요.")

o = [sec("jup-run")] + head(EB7, "Shift+Enter로 셀을 실행해요", C7)
o.append(f'<div style="position:absolute;left:96px;top:210px;width:1728px;height:66px;border-bottom:2px solid {LINE};display:flex;flex-direction:row;align-items:center;gap:16px">'
         + p(f"flex:1;font-family:{MONO};font-size:26px;font-weight:700;color:{INK}", "notebook.ipynb")
         + p(f"font-size:24px;font-weight:700;color:{GR};background:#E4F3EA;border-radius:8px;padding:4px 14px", ".venv (Python 3.14.6)") + '</div>')
yy = 300
cells_ = [(1, ['print("안녕하세요")'], "안녕하세요"), (2, ["import sys", "print(sys.executable)"], "/home/kim/hello-uv/.venv/bin/python"),
          (3, ["import fastapi", "print(fastapi.__version__)"], "0.162.2"), (4, ["1 + 2"], "3")]
geo = {}
for k, (n, code, out) in enumerate(cells_):
    cp, hh, cch = cell(n, code, out, 96, yy, 1200, attrs=bi("rise", k + 1), size=27, oid=f"jo{n}")
    o += cp
    geo[n] = (yy, hh, cch)
    yy += hh + 24
y2, h2, c2 = geo[2]
o.append(underline(5, 96 + 112 + 15 * 27 * CW, 96 + 112 + 30 * 27 * CW, y2 + c2 + 14 + 40, GR))
o += lead(5, 1420, y2 + c2 + 14 + 20, 96 + 112 + 36 * 27 * CW + 14, y2 + c2 + 14 + 20, ".venv면 잘 고른 거예요", GR, w=404, size=28)
W("jup-run", o, "셀을 누르고 Shift+Enter를 치면 실행하고 다음 셀로 넘어가요. 셀 왼쪽의 실행 버튼을 눌러도 돼요. 2번 셀은 지금 커널이 어느 파이썬인지 보여 줘요. hello-uv/.venv 안이면 맞게 고른 거예요. 3번 셀처럼 uv add로 넣은 fastapi도 노트북에서 바로 불러와요. 4번 셀처럼 셀 마지막 줄이 값이면 print 없이도 그 값을 보여 줘요. 출력은 tools/demo.sh가 hello-uv의 커널로 같은 셀을 실제로 실행한 결과이고, 폴더 주소만 01처럼 /home/kim으로 바꿨어요.")

# =====================================================================================
# 8. compare with the old way
# =====================================================================================
o = [sec("compare")] + head(EB8, "인터넷 자료의 예전 명령은 이렇게 바꿔 쳐요", C8)
cmpr = [("파이썬 설치", "python.org에서 받아 설치", "없으면 uv가 받아요", False), ("가상환경 만들기", "python3 -m venv .venv", "uv init 이름", True),
        ("가상환경 켜기", "source .venv/bin/activate", "uv run이 알아서 켜요", False), ("패키지 넣기", "pip install fastapi", "uv add fastapi", True),
        ("목록 적기", "pip freeze > requirements.txt", "uv add가 알아서 적어요", False), ("받은 프로젝트 맞추기", "pip install -r requirements.txt", "uv sync", True),
        ("실행", "python main.py", "uv run main.py", True), ("패키지 빼기", "pip uninstall fastapi  (10개 남아요)", "uv remove fastapi  (11개 다 빠져요)", True)]
rws = []
for job, old_, new, cmd in cmpr:
    om = "" if old_.startswith("python.org") else f"font-family:{MONO};"
    nm = f"font-family:{MONO};font-weight:700;color:{TEAL}" if cmd else f"font-weight:700;color:{TEAL}"
    rws.append([(job, "font-weight:700;font-size:28px"), (e(old_), f"{om}font-size:26px;color:#8A6A33"), (e(new), f"{nm};font-size:27px")])
tb, top = hrows(96, 210, [380, 720, 628], rws, 90, header=["할 일", "예전 (따라 치지 않아요)", "uv"], hcolors=[GRAY, OR, TEAL], rid="cmp",
                attrs_by_row={i: bi("fade", 1) for i in range(len(rws))})
o += tb
o.append(spot(2, target="cmp3", pad=6, r=10))
o.append(spot(3, target="cmp7", pad=6, r=10))
o.append(spot_off(4))
W("compare", o, "인터넷 자료나 옛 강의에 왼쪽 명령이 나오면 오른쪽 uv 명령으로 바꿔 쳐요. 예전에는 왼쪽 여섯 단계를 순서대로 직접 챙겼고, 하나라도 빼먹으면 ModuleNotFoundError가 났어요. uv로는 init, add, run, sync만 쳐요. 가장 자주 만나는 건 pip install 패키지예요. pip로 넣으면 pyproject.toml과 uv.lock에 적히지 않아서 다른 컴퓨터에서 uv sync로 받을 수 없어요. 뺄 때도 차이가 나요. pip uninstall fastapi는 fastapi 하나만 지우고 따라온 10개를 남기고, uv remove는 11개를 모두 빼요. 예전 방식은 따라 치지 않고 눈으로만 봐요. 예전 방식의 남은 10개는 tools/demo.sh로 실제로 실행한 결과예요.",
  ("compare", "예전 방식과 비교"))

# =====================================================================================
# 9. errors
# =====================================================================================
o = [sec("trouble")] + head(EB9, "uv에서 자주 만나는 메시지", C9)
cases = [("bash: uv: command not found", "uv:", "설치 뒤 터미널을 새로 열지 않았어요", "터미널 닫고 다시 열기", False),
         ("error: No `pyproject.toml` found in current directory or any parent directory", "No `pyproject.toml` found", "프로젝트 폴더 밖에서 쳤어요", "cd hello-uv", True),
         ("ModuleNotFoundError: No module named 'fastapi'", "ModuleNotFoundError", "패키지를 안 넣었거나 python3로 실행했어요", "uv add fastapi\nuv run main.py", True),
         ("error: Project is already initialized in `/home/kim/hello-uv`", "already initialized", "이미 만든 프로젝트 안에서 uv init을 쳤어요", "uv init은 처음 한 번만", False)]
for i, (msg, key, why_, fix, mfix) in enumerate(cases):
    yy = 214 + i * 196
    o.append(f'<div{bi("fade", i + 1)} style="position:absolute;left:96px;top:{yy}px;width:1728px;height:196px;border-bottom:2px solid {LINE};display:flex;flex-direction:row;align-items:center;gap:40px">'
             + '<div style="width:1150px;flex:none;display:flex;flex-direction:column;gap:14px">'
             + p(f"font-family:{MONO};font-size:{24 if len(msg) > 60 else 27}px;font-weight:700;line-height:1.35;color:{RED}", e(msg))
             + p(f"font-size:28px;color:{SUB}", e(why_)) + '</div>'
             + p(f"flex:1;{'font-family:' + MONO + ';' if mfix else ''}font-size:28px;font-weight:700;line-height:1.55;white-space:nowrap;color:{INK}", e(fix).replace(chr(10), "<br>"))
             + '</div>')
    kx = msg.index(key)
    fs = 24 if len(msg) > 60 else 27
    o.append(underline(i + 1, 96 + kx * fs * CW, 96 + (kx + len(key)) * fs * CW, yy + 196 / 2 - 36 + fs * 1.35 - 2 - (0 if True else 0), RED))
W("trouble", o, "uv를 쓰다 막히면 메시지에서 밑줄 친 부분을 먼저 읽어요. 1번은 설치 직후에 가장 많이 나요. Mac 기본 터미널은 zsh라서 zsh: command not found: uv로 보여요. 2번은 홈 폴더처럼 pyproject.toml이 없는 곳에서 uv add를 친 경우예요. pwd로 위치를 보고 프로젝트 폴더로 cd 해요. 3번은 uv add를 안 했거나, 가상환경을 켜지 않고 python3 main.py로 실행한 경우예요. 4번은 이미 pyproject.toml이 있는 폴더라 다시 만들 필요가 없어요. 메시지는 tools/demo.sh로 실제로 실행한 결과예요.",
  ("trouble", "막힐 때"))

o = [sec("trouble2")] + head(EB9, "노트북과 pull에서 막힐 때", C9)
cases = [("ipykernel을 설치하라는 알림이 떠요", "알림의 Install은 pip로 넣어서 pyproject.toml에 안 적혀요.", "uv add --dev ipykernel", True, JP),
         ("커널 목록에 .venv가 없어요", "hello-uv 폴더 자체를 열었는지 봐요. 그다음 VS Code를 다시 열어요.", "uv sync", True, JP),
         ("셀에서 ModuleNotFoundError", "커널이 .venv가 아니에요. 오른쪽 위 커널 이름을 눌러 바꿔요.", ".venv 고르기", False, JP),
         ("fatal: Need to specify how to reconcile divergent branches.", "pull 설정이 없어요. 한 번만 설정하면 돼요(06).", "git config --global\n  pull.rebase false", True, RED)]
for i, (q, a_, fix, mfix, c) in enumerate(cases):
    yy = 214 + i * 196
    is_msg = q.startswith("fatal")
    o.append(f'<div{bi("fade", i + 1)} style="position:absolute;left:96px;top:{yy}px;width:1728px;height:196px;border-bottom:2px solid {LINE};display:flex;flex-direction:row;align-items:center;gap:40px">'
             + '<div style="width:1150px;flex:none;display:flex;flex-direction:column;gap:14px">'
             + p(f"{'font-family:' + MONO + ';font-size:25px;color:' + RED if is_msg else 'font-size:32px;color:' + INK};font-weight:700;line-height:1.35", e(q))
             + p(f"font-size:28px;color:{SUB}", e(a_)) + '</div>'
             + p(f"flex:1;{'font-family:' + MONO + ';' if mfix else ''}font-size:28px;font-weight:700;line-height:1.55;white-space:pre;color:{INK}", e(fix))
             + '</div>')
W("trouble2", o, "노트북 문제는 대부분 커널이 .venv가 아니어서 생겨요. 1번은 ipykernel 없이 셀을 실행하면 VS Code가 띄우는 알림이에요. Install 버튼은 pip로 설치해서 pyproject.toml과 uv.lock에 적히지 않으니, 알림을 닫고 터미널에서 uv add --dev ipykernel을 쳐요. 2번은 hello-uv의 부모 폴더를 열었거나, clone 뒤 uv sync를 안 해서 .venv가 없을 때 나요. 3번은 컴퓨터에 원래 있던 파이썬을 커널로 고른 경우예요. 4번은 내 컴퓨터와 GitHub에 서로 다른 커밋이 있을 때 git pull에서 나요. 06에서 본 대로 git config --global pull.rebase false를 한 번 치고 다시 pull해요. fatal 메시지는 tools/demo.sh로 실제로 실행한 결과예요.")

# =====================================================================================
# 10. real situations
# =====================================================================================
# R1: a tutorial says pip install requests
o = [sec("real-tutorial")] + head(EB10, "튜토리얼에 pip install이 나오면 uv add로 바꿔요", C10)
tut = ["python3 -m venv .venv", "source .venv/bin/activate", "pip install requests", "python main.py"]
o.append(f'<div style="position:absolute;left:96px;top:220px;width:720px;height:452px;background:#FFFDF6;border:2px solid {LINE};border-radius:16px"></div>')
o.append(note("인터넷 튜토리얼", 132, 244, 640, GRAY, 26, weight=700))
o.append(note("카페 주문 프로그램을 만들어 봅시다. 먼저 가상환경을 만들고 requests를 설치하세요.", 132, 288, 650, INK, 28))
for k, x in enumerate(tut):
    yy = 410 + k * 60
    o.append(p(f"position:absolute;left:132px;top:{yy}px;width:640px;font-family:{MONO};font-size:27px;font-weight:700;line-height:44px;color:#8A6A33", e(x), f' id="tu{k}"'))
for k in (0, 1):
    o.append(f'<div{bi("fade", 1)} style="position:absolute;left:128px;top:{410 + k * 60 + 22}px;width:{len(tut[k]) * 27 * CW + 8:.0f}px;height:3px;background:{GRAY}"></div>')
o.append(note("uv init과 uv run이 대신해요", 132 + 26 * 27 * CW + 30, 410 + 30 - 18, 260, GRAY, 22, attrs=bi("fade", 1), weight=700))
o.append(box(2, 122, 410 + 2 * 60 - 2, 20 * 27 * CW + 20, 48, OR))
t = Term([("$", "uv init cafe-order"), ("o", "Initialized project `cafe-order` at `/home/kim/cafe-order`"), ("$", "cd cafe-order"), ("$", "uv add requests"),
          ("o", "Using CPython 3.14.6"), ("o", "Creating virtual environment at: .venv"), ("o", "Resolved 6 packages in 223ms"), ("o", "Prepared 4 packages in 309ms"),
          ("H", "Installed 5 packages in 4ms"), ("g", " + requests==2.34.2  + urllib3==2.8.0  …"), ("$", "uv run main.py"), ("H", "requests 버전: 2.34.2")],
         860, 220, 964, size=24, lh=46, builds={0: 1, 1: 1, 2: 1, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 2, 9: 2, 10: 3, 11: 3})
o += t.parts
cc, ys, chh = code_card("c-cafe", "main.py", ["import requests", "", 'print("requests 버전:", requests.__version__)'], 96, 704, 720, BL, 23, lh=36, attrs=bi("fade", 3))
o += cc
o.append(caption("이렇게 넣으면 pyproject.toml에 requests가 적혀서 팀원도 uv sync로 받아요.", 920, attrs=bi("fade", 4)))
W("real-tutorial", o, "인터넷 튜토리얼에 pip install 패키지가 나오면 우리 프로젝트에서는 uv add 패키지로 바꿔 쳐요. 튜토리얼의 네 줄 가운데 가상환경 만들기와 켜기는 uv init과 uv run이 대신해요. pip install requests는 uv add requests로 바꿔요. requests는 인터넷에서 데이터를 받아 오는 패키지이고, 함께 따라온 4개까지 5개가 들어왔어요. python main.py는 uv run main.py로 실행해요. 이렇게 넣으면 pyproject.toml에 requests가 적혀서 팀원도 uv sync로 받을 수 있어요. 출력은 tools/demo.sh로 실제로 실행한 결과이고, 설치 목록 5줄은 한 줄로 줄였어요.",
  ("real", "실제 상황 예제"))

# R2: a notebook cell needs a package that is not in .venv
o = [sec("real-notebook")] + head(EB10, "노트북에서 없는 패키지는 터미널에서 uv add로 넣어요", C10)
o.append(p(f"position:absolute;left:96px;top:214px;width:860px;font-family:{MONO};font-size:26px;font-weight:700;color:{JP}", "notebook.ipynb"))
cp, hh, cch = cell(1, ["import requests", 'print("requests 버전:", requests.__version__)'], "ModuleNotFoundError: No module named 'requests'", 96, 266, 880, size=24, out_color=RED, oid="nb-err")
o += cp
o.append(box(1, 96 + 112 - 12, 266 + cch + 12, 46 * 24 * CW + 24, 42, RED))
t = Term([("$", "uv add requests"), ("o", "Resolved 48 packages in 16ms"), ("H", "Installed 4 packages in 3ms"), ("g", " + certifi==2026.10.23"), ("g", " + charset-normalizer==3.5.2"),
          ("g", " + requests==2.34.2"), ("g", " + urllib3==2.8.0")], 1020, 266, 804, size=26, lh=46, attrs=bi("rise", 2))
o += t.parts
o.append(tag("hello-uv 터미널", INK, 1020, 214, attrs=bi("fade", 2)))
cp, hh2, cch2 = cell(2, ["import requests", 'print("requests 버전:", requests.__version__)'], "requests 버전: 2.34.2", 96, 266 + hh + 150, 880, size=24, attrs=bi("rise", 3), oid="nb-ok")
o += cp
o.append(note("같은 셀을 다시 실행해요", 182, 266 + hh + 88, 700, GR, 26, attrs=bi("fade", 3), weight=700))
o.append(caption("셀은 노트북에서, 패키지는 터미널에서 넣어요. VS Code 알림의 Install 버튼은 누르지 않아요.", 870, attrs=bi("fade", 4)))
W("real-notebook", o, "노트북 셀에서 ModuleNotFoundError가 나면 VS Code 터미널에서 uv add로 패키지를 넣고 같은 셀을 다시 실행해요. 커널은 hello-uv의 .venv라서, uv add로 .venv에 넣으면 노트북에서도 바로 불러와요. idna는 fastapi와 함께 이미 들어와 있어서 이번엔 4개만 설치됐어요. 알림의 Install이나 pip install은 목록 파일에 적히지 않아서 쓰지 않아요. 노트북 출력은 tools/demo.sh가 커널 하나에서 셀, uv add, 같은 셀 순서로 실제로 실행한 결과예요.")

# R3: kim pushes the new package, lee pulls and syncs
o = [sec("real-team")] + head(EB10, "팀원이 넣은 패키지는 pull 뒤 uv sync로 받아요", C10)
o.append(tag("kim 컴퓨터", KIM, 96, 196))
tk = Term([("$", "git status --short"), ("o", " M pyproject.toml"), ("o", " M uv.lock"), ("$", "git add pyproject.toml uv.lock"), ("$", 'git commit -m "feat: requests 패키지 넣기"'), ("o", "[main faabfb6] feat: requests 패키지 넣기"), ("$", "git push origin main"), ("o", "   0a438ca..faabfb6  main -> main")],
          96, 248, 840, size=25, lh=44, tid="tkim")
o += tk.parts
o.append(note("올리는 건 목록 파일 두 개예요. .venv는 올라가지 않아요.", 96, tk.y + tk.h + 28, 840, SUB, 26))
o.append(tag("lee 컴퓨터", LEE, 984, 196, attrs=bi("fade", 1)))
tl = Term([("$", "git pull origin main"), ("o", "Fast-forward"), ("o", " pyproject.toml |   1 +"), ("o", " uv.lock        | 133 +++++++++…"), ("$", "uv sync"), ("H", "Installed 4 packages in 3ms"),
           ("g", " + requests==2.34.2  …"), ("$", "uv tree --depth 1"), ("o", "hello-uv v0.1.0"), ("o", "├── fastapi v0.162.2"), ("H", "├── requests v2.34.2"),
           ("o", "└── ipykernel v7.4.0 (group: dev)")], 984, 248, 840, size=25, lh=44, tid="tlee", attrs=bi("rise", 1), builds={4: 2, 5: 2, 6: 2, 7: 3, 8: 3, 9: 3, 10: 3, 11: 3})
o += tl.parts
o.append(caption("pull은 목록 파일만 바꿔요. 내 .venv에 실제로 설치하는 건 uv sync예요.", 870, attrs=bi("fade", 4)))
W("real-team", o, "팀원이 패키지를 넣고 push했으면 git pull origin main 뒤에 uv sync를 쳐요. kim은 앞 장에서 넣은 requests를 커밋해서 올렸어요. git add는 바뀐 두 파일 pyproject.toml과 uv.lock을 적어요. lee는 pull로 두 파일을 받고, uv sync로 requests와 따라온 패키지를 .venv에 설치했어요. uv tree --depth 1로 보면 lee의 프로젝트에도 requests가 들어 있어요. pull에서 fatal: Need to specify how to reconcile divergent branches.가 나오면 31쪽처럼 pull.rebase false를 설정해요. 출력은 tools/demo.sh로 실제로 실행한 결과이고, pull 출력 앞부분과 설치 목록 3줄, uv tree의 Resolved 줄은 뺐어요.")

# =====================================================================================
# summary
# =====================================================================================
o = [sec("cheatsheet")] + head("정리", "언제 무엇을 치나", INK)
cs = [("새 프로젝트를 만들 때", "uv init 이름"), ("코드를 실행할 때", "uv run main.py"), ("패키지를 넣을 때 (pip install 대신)", "uv add 패키지"),
      ("패키지를 뺄 때", "uv remove 패키지"), ("받은 프로젝트를 맞출 때 (clone, pull 뒤)", "uv sync"), ("노트북 커널을 넣을 때", "uv add --dev ipykernel")]
rws = [[(e(a_), "font-size:30px"), (e(b_), f"font-family:{MONO};font-weight:700;font-size:32px;color:{TEAL}")] for a_, b_ in cs]
tb, top = hrows(96, 210, [900, 828], rws, 92, header=["이럴 때", "이렇게"])
o += tb
o.append(f'<div style="position:absolute;left:96px;top:{top + 6 * 92 + 40}px;width:1728px;display:flex;flex-direction:row;gap:60px;align-items:center">'
         + p(f"font-size:28px;font-weight:700;color:{INK}", f'GitHub에 올려요 <span style="font-family:{MONO};color:{GR}">pyproject.toml  uv.lock  .python-version</span>')
         + p(f"font-size:28px;font-weight:700;color:{INK}", f'올리지 않아요 <span style="font-family:{MONO};color:{RED}">.venv</span>') + '</div>')
o.append(note("다음 챕터: 10 · VS Code에서 Jupyter 노트북 쓰기. 오늘 만든 hello-uv 노트북을 손에 익혀요.", 96, top + 6 * 92 + 120, 1728, SUB, 28, weight=700))
W("cheatsheet", o, "파이썬 프로젝트에서 치는 uv 명령은 거의 이 여섯 개예요. 새 프로젝트는 uv init, 실행은 uv run, 패키지는 uv add와 uv remove, 받은 프로젝트는 uv sync예요. 인터넷 자료에 pip install이 보이면 uv add로 바꿔 쳐요. GitHub에는 목록 파일 세 개를 올리고 .venv는 올리지 않아요. 다음 10챕터에서는 오늘 만든 hello-uv의 노트북을 손에 익혀요.",
  ("summary", "정리"))

# =====================================================================================
# toc (page numbers from ORDER): hairline rows, no cards
# =====================================================================================
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
parts = [(C1, "왜 필요할까", "받은 프로젝트가 안 돌아가는 이유", "why", "why"), (C2, "큰 그림", "python, 패키지, 가상환경, uv", "run", "map"),
         (C3, "uv 설치하기", "brew, winget", "install", "install"), (C4, "프로젝트 만들고 실행하기", "uv init, uv run, 가상환경 켜기", "init", "pyver"),
         (C5, "패키지 넣고 빼기", "uv add, uv tree, uv remove", "add", "again"), (C6, "다른 컴퓨터에서 그대로", "GitHub, uv sync", "commit", "sync-when"),
         (C7, "VS Code에서 Jupyter 쓰기", "확장, ipykernel, 커널 고르기", "jup-what", "jup-run"), (C8, "예전 방식과 비교", "pip, venv를 uv로 바꿔 치기", "compare", "compare"),
         (C9, "막힐 때", "자주 만나는 메시지", "trouble", "trouble2"), (C10, "실제 상황 예제", "튜토리얼, 노트북, 팀원과 함께", "real-tutorial", "real-team")]
t = [f'<section id="toc" data-transition="fade" style="background:{BG};color:{INK};font-family:{SANS};word-break:keep-all;padding:96px">',
     f'<h2 style="position:absolute;left:96px;top:72px;width:1728px;font-size:56px;font-weight:700;line-height:1.2;color:{INK}">오늘의 순서</h2>']
for i, (c, h_, s_, a, b) in enumerate(parts):
    yy = 176 + i * 78
    pg = f"{page[a]}–{page[b]}쪽" if a != b else f"{page[a]}쪽"
    t.append(f'<div style="position:absolute;left:96px;top:{yy}px;width:1728px;height:78px;border-bottom:2px solid {LINE};display:flex;flex-direction:row;align-items:center">'
             + p(f"width:90px;flex:none;font-size:36px;font-weight:900;color:{c}", str(i + 1))
             + p(f"width:620px;flex:none;font-size:32px;font-weight:700;color:{INK}", h_)
             + p(f"flex:1;font-size:27px;color:{SUB}", e(s_))
             + p(f"width:160px;flex:none;font-size:26px;text-align:right;color:{GRAY}", pg) + '</div>')
t.append(p(f"position:absolute;left:96px;top:{176 + 10 * 78 + 24}px;width:1728px;font-size:26px;color:{SUB}", f'{page["cheatsheet"]}쪽은 한 장 요약이에요. 4파트에서 만든 hello-uv 폴더를 끝까지 계속 써요.'))
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(t) + f"\n<aside>{e('1, 2파트는 눈으로 보는 배경이에요. 3파트에서 uv를 설치하고, 4파트부터 직접 따라 쳐요. 4파트에서 만든 hello-uv 폴더를 5, 6, 7파트와 실제 상황 예제에서 계속 써요. 8파트의 예전 방식은 따라 치지 않아요.')}</aside>\n</section>\n")

assert page["jup-ext"] == 25 and page["jup-kernel"] == 26 and page["jup-pick"] == 27, "Jupyter setup must stay on pages 25-27"
deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-10-30T02:00:00Z"}, "lists": "css", "title": "uv로 파이썬 시작하기", "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
print(len(ORDER), "slides", {k: page[k] for k in ("why", "jup-ext", "compare", "trouble", "real-team")})
