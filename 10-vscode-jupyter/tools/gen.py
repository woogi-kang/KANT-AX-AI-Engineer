"""Generates every slide of the VS Code Jupyter deck and slides/deck.json.

Story (chapter design frame): why a notebook (a .py file reruns from the top), the big picture (cells run in
the kernel, results come back under the cell), the smallest run (Shift+Enter), then the notebook screen, the
run keys, run numbers and Restart, command and edit mode, a comparison with uv run main.py, the usual traps,
three real notes written in a notebook, and the shortcut tables.

Layout follows the Stageshow rules (github.com/benjitaylor/skills): one hero per slide (the notebook window,
bled off the right and bottom edges), labels drawn on the picture with leader lines instead of side cards,
values that change move in place (tools/states.js) instead of a before/after pair.
Leader lines aim at measured boxes: pass 1 writes the slides, tools/measure.js saves every id's box in
tools/rects.json, pass 2 writes the slides again with the lines.
Cell output comes from tools/demo.sh (tools/run_nb.py runs the cells with the project kernel).
Usage: python3 tools/gen.py slides
"""
import html, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "tools"))
from highlight import spot, spot_off, cursor, cursor_off, ring, box, underline, shine, pulse, keys as keycaps, shake, zoom, zoom_off, STAGGER, DIM, PATH  # noqa: E402

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
RECTS_FILE = os.path.join(HERE, "rects.json")
STATES_JS = open(os.path.join(HERE, "states.js")).read()

SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
BG, INK, SUB, LINE, GRAY = "#F6F5F1", "#1D2330", "#4A5262", "#E1DED6", "#6A7180"
BL, GR, OR, PUR, RED, NAVY, TEAL = "#2459C9", "#1F8A4C", "#B26A00", "#5A3BB8", "#A33131", "#1E3F8F", "#0F7C86"
JP = "#B8560F"          # Jupyter and the kernel, same as chapter 09 part 7
SEL = "#2F7DE1"         # selected cell bar, like VS Code's focus color
QUIET = "#9AA0AA"       # leader lines
HAIR = "#DDD9CF"        # hairlines between rows
SH_HERO = "0 1px 2px rgba(29,35,48,.05), 0 24px 56px rgba(29,35,48,.13)"
SH_SAT = "0 1px 2px rgba(29,35,48,.08), 0 12px 28px rgba(29,35,48,.16)"
CURVE = "cubic-bezier(.45,0,.1,1)"
MOVE = f"transition:top .6s {CURVE},height .6s {CURVE},opacity .4s ease"

# hero window on the right: inset top, bled off the right and bottom edges; words and keys sit in the left column
RX, RY, RW = 700, 214, 1320
LX, LR = 96, 640          # left column, left edge and right edge

RECTS, CUR = {}, None
ORDER, SECTIONS = [], {}


def e(s):
    return html.escape(s, quote=False)


def p(style, text, attrs=""):
    return f'<p{attrs} style="{style}">{text}</p>'


def st(d):
    """data-st for tools/states.js: {step: {"css": ..., "html": ...}} = the state shown before that step."""
    return f' data-st="{html.escape(json.dumps(d, ensure_ascii=False), quote=True)}"'


def bi(kind, order):
    return f' data-build-in="{kind} order {order}"' if order else ""


# the ↻ glyph is missing from most fonts, so draw it
RESTART_SVG = ('<svg viewBox="0 0 24 24" style="width:.8em;height:.8em;vertical-align:-.08em;overflow:visible" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">'
               '<path d="M20 12a8 8 0 1 1-2.6-5.9"/><path d="M20 3.5v5h-5"/></svg>')


def W(sid, parts, notes, section=None):
    if section:
        SECTIONS[section[0]] = {"description": section[1], "start": sid}
    if sid not in ORDER:
        ORDER.append(sid)
    body = "\n".join(parts).replace("↻", RESTART_SVG)
    script = f'\n<script type="text/slide-js">\n{STATES_JS}</script>' if "data-st=" in body else ""
    with open(os.path.join(OUT, sid + ".html"), "w") as f:
        f.write(body + script + f"\n<aside>{e(notes)}</aside>\n</section>\n")


def sec(sid, transition="fade", bg=BG):
    global CUR
    CUR = sid
    return f'<section id="{sid}" data-transition="{transition}" style="background:{bg};color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">'


def head(eyebrow, title, color):
    return [p(f"position:absolute;left:96px;top:52px;width:1728px;font-size:24px;font-weight:700;color:{color}", e(eyebrow), ' id="eyebrow"'),
            f'<h2 id="title" style="position:absolute;left:96px;top:88px;width:1728px;font-size:52px;font-weight:700;line-height:1.25;color:{INK}">{title}</h2>']


def kbd(text, size=30, color=INK, kid=None):
    """Key caps. Keys joined with + are pressed together; keys split by spaces are separate keys."""
    if " " in text:
        return '<div style="display:flex;flex-direction:row;align-items:center;gap:14px">' + "".join(kbd(t, size, color) for t in text.split()) + '</div>'
    caps = [p(f"font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.2;white-space:nowrap;color:{color};background:#FFFFFF;border:2px solid #C9CED8;border-bottom-width:5px;border-radius:10px;padding:6px 14px", e(k))
            for k in text.split("+")]
    plus = p(f"font-size:{size * 0.8:.0f}px;font-weight:700;color:{GRAY}", "+")
    idattr = f' id="{kid}"' if kid else ""
    return f'<div{idattr} style="display:flex;flex-direction:row;align-items:center;gap:8px;width:fit-content">' + plus.join(caps) + '</div>'


def keycard(x, y, w, win, mac, note=None, kid="keys", attrs="", size=30):
    """The keys of a scene, Windows over Mac, on a small raised card beside the notebook."""
    lab = lambda t, c: p(f"width:120px;flex:none;font-size:22px;font-weight:700;color:{c}", t)
    rows = ('<div style="display:flex;flex-direction:row;align-items:center;gap:12px">' + lab("Windows", BL) + kbd(win, size, kid=f"{kid}-win") + '</div>'
            + '<div style="display:flex;flex-direction:row;align-items:center;gap:12px">' + lab("Mac", GRAY) + kbd(mac, size, kid=f"{kid}-mac") + '</div>')
    n = (f'<div style="height:1px;background:{HAIR};margin:4px 0"></div>' + p(f"font-size:25px;line-height:1.45;color:{SUB}", note)) if note else ""
    return (f'<div id="{kid}"{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;background:#FFFFFF;border-radius:20px;box-shadow:{SH_SAT};'
            f'padding:26px 30px;display:flex;flex-direction:column;gap:16px">{rows}{n}</div>')


def caption(text, top, left=96, width=1728, size=30, color=INK, order=None, cid="caption"):
    return p(f"position:absolute;left:{left}px;top:{top}px;width:{width}px;font-size:{size}px;font-weight:700;line-height:1.45;color:{color}", text, f' id="{cid}"' + bi("fade", order))


# ---------- leader lines: a label joined to the thing it explains (Stageshow annotations.md) ----------
def lead(order, tid, text, side="l", dx=48, dy=0, color=INK, size=28, w=None, lid=None, gap=10, at=None, z=None, align="left", build="fade", edge=None, extra=""):
    """side l/r: the label sits left/right of the target at the same height (dy moves it, with one bend).
    side t/b: the line leaves the top/bottom of the target, goes dy up/down, and the label starts beside its end.
    at=(x, y) aims at that point instead of the target's edge. Needs tools/rects.json (pass 2)."""
    r = RECTS.get(CUR, {}).get(tid)
    if not r:
        return []
    x, y, wd, h = r
    half = size * 1.35 / 2
    zs = f";z-index:{z}" if z else ""
    if side in ("l", "r"):
        ax = x - gap if side == "l" else x + wd + gap
        ay = y + h / 2
        if at:
            ax, ay = at
        ly = ay + dy
        if side == "l":
            edge = edge if edge is not None else ax - dx
            dx = ax - edge
            pos, sx = f"right:{1920 - edge:.0f}px;text-align:right", edge + 14
            bend = ax - min(36, dx / 2)
        else:
            edge = ax + dx
            pos, sx = f"left:{edge:.0f}px", edge - 14
            bend = ax + min(36, dx / 2)
        pts = [(sx, ly), (ax, ay)] if abs(dy) < 1 else [(sx, ly), (bend, ly), (ax, ay)]
    else:
        ax = x + wd / 2
        ay = y + h + gap if side == "b" else y - gap
        if at:
            ax, ay = at
        ly = ay + (dy if side == "b" else -dy)
        if align == "center":
            cw = w or 360
            pos, ex = f"left:{ax - cw / 2:.0f}px;text-align:center", ax
            ly_label = ly + 14 + half
        elif align == "left":
            pos, ex = f"left:{ax + 22:.0f}px", ax + 12
        else:
            pos, ex = f"right:{1920 - ax + 22:.0f}px;text-align:right", ax - 12
        pts = [(ax, ay), (ax, ly), (ex, ly)]
        if align == "center":
            pts = [(ax, ay), (ax, ly)]
            ly = ly_label
    d = "M" + " L".join(f"{a:.0f},{b:.0f}" for a, b in pts)
    ws = f"width:{w}px;white-space:normal" if w else "white-space:nowrap"
    idattr = f' id="{lid}"' if lid else ""
    return [f'<svg{bi("draw", order)}{extra} viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible{zs}">'
            f'<path d="{d}" fill="none" stroke="{QUIET}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>',
            f'<div{bi("fade", order)}{extra} style="position:absolute;left:{ax - 6:.0f}px;top:{ay - 6:.0f}px;width:12px;height:12px;border-radius:50%;background:{color}{zs}"></div>',
            p(f"position:absolute;{pos};top:{ly - half:.0f}px;{ws};font-size:{size}px;font-weight:700;line-height:1.35;color:{color}{zs}", text, idattr + bi(build, order) + extra)]


def aim(order, tid, fx=0.85, fy=0.8):
    """Cursor that lands near the lower right of an element, so the pointer does not hide its words."""
    r = RECTS.get(CUR, {}).get(tid)
    if not r:
        return cursor(order, target=tid)
    x, y, wd, h = r
    return cursor(order, x + wd * fx, y + h * fy)


def sub(text):
    return f'<span style="font-weight:400;color:{SUB}">{text}</span>'


# ---------- notebook window and cells (each cell keeps its id across scenes) ----------
TAB_H, TB_H = 58, 64
TOOLS = [("tb-code", "+ Code"), ("tb-md", "+ Markdown"), ("tb-runall", "▷ Run All"), ("tb-restart", "↻ Restart"), ("tb-clear", "Clear All Outputs"), ("tb-vars", "Variables")]


def window(x, y, w, toolbar=True, pre="", h=None, file="notebook.ipynb", attrs="", compact=None):
    """A VS Code editor with one notebook open. Bled off the bottom unless h is given. Returns (parts, first cell top)."""
    H = h or (1080 - y + 80)
    hide = () if w >= 1180 else ("tb-clear", "tb-vars") if w >= 900 else ("tb-md", "tb-clear", "tb-vars")
    o = [f'<div{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{H}px;background:#FFFFFF;border:1.5px solid #D9D5CB;border-radius:18px;overflow:hidden;box-shadow:{SH_HERO}">',
         f'<div style="height:{TAB_H}px;background:#EFEDE7;display:flex;flex-direction:row;align-items:flex-end;padding:0 18px">'
         f'<div style="height:46px;background:#FFFFFF;border-radius:10px 10px 0 0;padding:0 24px;display:flex;flex-direction:row;align-items:center;gap:18px">'
         + p(f"font-family:{MONO};font-size:22px;font-weight:700;color:{INK};white-space:nowrap", e(file)) + p(f"font-size:22px;color:{GRAY}", "×") + '</div></div>']
    if toolbar:
        o.append(f'<div style="height:{TB_H}px;border-bottom:1px solid #ECEAE4;display:flex;flex-direction:row;align-items:center;padding:0 26px;gap:30px">'
                 f'<div id="{pre}tb-tools" style="display:flex;flex-direction:row;align-items:center;gap:30px">'
                 + "".join(p(f"font-size:22px;color:{SUB};white-space:nowrap", e(t), f' id="{pre}{i}"') for i, t in TOOLS if i not in hide) + '</div>'
                 + p(f"font-size:22px;color:{GRAY}", "···") + '<div style="flex:1"></div>'
                 + p(f"font-size:20px;font-weight:700;color:{GR};background:#E6F4EC;border-radius:8px;padding:5px 14px;white-space:nowrap", ".venv (Python 3.14.6)", f' id="{pre}kernel"') + '</div>')
    o.append('</div>')
    return o, y + TAB_H + (TB_H if toolbar else 0) + 30


def lh_of(fs):
    return round(fs * 1.47)


PADY, GUT = 14, 104       # cell padding top/bottom, distance from the bar to the cell box


def box_h(c, fs):
    lh = lh_of(fs)
    if c.get("kind") == "mdr":
        return 24 + sum(md_line_h(l, fs) for l in c["lines"])
    return 2 * PADY + lh * len(c.get("lines", [""])) + 4


def md_line_h(l, fs):
    if l.startswith("# "):
        return round(fs * 1.9)
    if l.startswith("### "):
        return round(fs * 1.65)
    return 26 if l == "---" else lh_of(fs)


def out_h(c, fs):
    return 10 + lh_of(fs) * len(c["out"]) if c.get("out") else 0


def md_render(l, fs, lid=None):
    ida = f' id="{lid}"' if lid else ""
    if l == "---":
        return f'<div{ida} style="height:26px;display:flex;align-items:center"><div style="width:100%;height:3px;background:#C9CED8"></div></div>'
    if l.startswith("# "):
        return p(f"font-size:{fs * 1.3:.0f}px;font-weight:700;line-height:{round(fs * 1.9)}px;color:{INK}", e(l[2:]), ida)
    if l.startswith("### "):
        return p(f"font-size:{fs * 1.12:.0f}px;font-weight:700;line-height:{round(fs * 1.65)}px;color:{INK}", e(l[4:]), ida)
    t = e(l[2:]) if l.startswith("- ") else e(l)
    t = t.replace("**", "\x00")
    while "\x00" in t:
        t = t.replace("\x00", "<b>", 1).replace("\x00", "</b>", 1)
    if ": " in t:
        a_, b_ = t.split(": ", 1)
        t = f'{a_}: <span style="font-family:{MONO};font-weight:700;color:{TEAL}">{b_}</span>'
    return p(f"font-size:{fs * 0.9:.0f}px;line-height:{lh_of(fs)}px;color:{INK}", ("• " if l.startswith("- ") else "") + t, ida)


def cell(c, x, top, w, sel=None, mode="cmd", pre="", fs=34):
    """c: dict(id, kind code|md|mdr, lines, n, out, err, lids, oids, attrs, n_st, out_st, tag).
    x is where the selection bar sits; the cell box starts GUT px to the right."""
    kind, lines, n = c.get("kind", "code"), c.get("lines", [""]), c.get("n")
    lh = lh_of(fs)
    cid = pre + c["id"]
    edit = sel == c["id"] and mode == "edit"
    o = [f'<div id="{cid}"{c.get("attrs", "")} style="position:absolute;left:{x}px;top:{top}px;width:{w}px;{MOVE}">']
    if kind == "code":
        o.append(p(f"position:absolute;left:10px;top:{PADY + 2}px;width:84px;font-family:{MONO};font-size:{fs * 0.7:.0f}px;line-height:{lh}px;color:{GRAY};text-align:right;{MOVE}",
                   f"[{n}]" if n else "[ ]", f' id="{cid}-n"' + c.get("n_st", "")))
    lids = c.get("lids") or [None] * len(lines)
    if kind == "mdr":
        body = "".join(md_render(l, fs, lids[i] and pre + lids[i]) for i, l in enumerate(lines))
        o.append(f'<div id="{cid}-box" style="margin-left:{GUT}px;padding:12px 22px;display:flex;flex-direction:column">{body}</div>')
    else:
        bd = f"2px solid {SEL};box-shadow:0 0 0 1.5px {SEL}" if edit else f"2px solid {LINE}"
        bg = "#FFFFFF" if kind == "code" else "#FAF8F3"
        caret = f'<span style="display:inline-block;width:3px;height:{fs + 4}px;background:{SEL};vertical-align:-{fs * 0.22:.0f}px;margin-left:2px"></span>'
        txt = "".join(p(f"font-family:{MONO};font-size:{fs}px;line-height:{lh}px;white-space:pre;color:{INK};width:fit-content",
                        (e(l) if l else "&#8203;") + (caret if edit and i == len(lines) - 1 else ""), f' id="{pre}{lids[i]}"' if lids[i] else "")
                      for i, l in enumerate(lines))
        tag = p(f"position:absolute;right:16px;bottom:8px;font-size:{fs * 0.55:.0f}px;line-height:1.2;color:{GRAY}", "Python" if kind == "code" else "Markdown", f' id="{cid}-tag"')
        o.append(f'<div id="{cid}-box" style="margin-left:{GUT}px;position:relative;background:{bg};border:{bd};border-radius:10px;padding:{PADY}px 22px;display:flex;flex-direction:column">{txt}{tag}</div>')
    if c.get("out"):
        col = RED if c.get("err") else INK
        oids = c.get("oids") or [None] * len(c["out"])
        o.append(f'<div id="{cid}-out"{c.get("out_attrs", "")}{c.get("out_st", "")} style="margin-left:{GUT + 24}px;padding-top:10px">'
                 + "".join(p(f"font-family:{MONO};font-size:{fs}px;line-height:{lh}px;white-space:pre;color:{col};width:fit-content", e(l), f' id="{pre}{oids[i]}"' if oids[i] else "")
                           for i, l in enumerate(c["out"])) + '</div>')
    o.append('</div>')
    return o


def cells(cs, x, top, w, sel=None, mode="cmd", pre="", gap=22, fs=34):
    """Draws cells top to bottom. Returns (parts, pos) with pos[id] = (top, box height, height with output)."""
    o, pos, y = [], {}, top
    for c in cs:
        o += cell(c, x, y, w, sel, mode, pre, fs)
        bh = box_h(c, fs)
        pos[c["id"]] = (y, bh, bh + out_h(c, fs))
        y += bh + out_h(c, fs) + gap
    return o, pos


def selbar(x, top, h, pre="", attrs=""):
    return f'<div id="{pre}sel"{attrs} style="position:absolute;left:{x}px;top:{top}px;width:7px;height:{h}px;border-radius:4px;background:{SEL};{MOVE}"></div>'


def gopen(x, y, s):
    """Everything inside is drawn at size 1 and shown s times bigger (Stageshow close-up): pass local coordinates."""
    return f'<div style="position:absolute;left:{x}px;top:{y}px;width:0;height:0;transform:scale({s});transform-origin:0 0">'


def scene(cs, s=1.0, toolbar=True, sel=None, mode="cmd", pre="", x=RX, y=RY, right=1824, fs=34, gap=22, bottom=1080):
    """The right-hand hero: a notebook window from (x, y) to the right gutter, bled off the bottom.
    Returns (parts without the closing tag, pos in local px, local width, to_global)."""
    wl = (right - x) / s
    w_, top = window(0, 0, wl, toolbar, pre, h=(bottom - y) / s + 80)
    cs_, pos = cells(cs, 28, top, wl - 28 - 20, sel, mode, pre, gap, fs)
    return [gopen(x, y, s)] + w_ + cs_, pos, wl, (lambda lx, ly: (x + s * lx, y + s * ly))


def kernel_panel(x, y, w, rows, pre="", title="커널이 기억하는 값", attrs=""):
    """The kernel's memory, the same object on every slide: a warm surface with name and value rows."""
    o = [f'<div id="{pre}mem"{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;background:#FBF1E4;border-radius:22px;padding:24px 30px 18px;display:flex;flex-direction:column">',
         p(f"font-size:26px;font-weight:700;color:{JP};margin-bottom:8px", title)]
    for r in rows:
        name, val, extra, row_css = r[0], r[1], (r[2] if len(r) > 2 else ""), (r[4] if len(r) > 4 else "")
        o.append(f'<div id="{pre}mem-{name}"{extra} style="height:66px;border-top:1px solid #EBD8C0;display:flex;flex-direction:row;align-items:center;{MOVE};{row_css}">'
                 + p(f"width:46%;font-family:{MONO};font-size:32px;font-weight:700;color:{INK}", e(name))
                 + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:{INK};padding:2px 10px;border-radius:8px;transition:background .4s ease", e(val), f' id="{pre}mem-{name}-v"' + (r[3] if len(r) > 3 else "")) + '</div>')
    o.append('</div>')
    return o


def terminal(lines, x, y, w, h, fs=30, tid="term"):
    lh = round(fs * 1.5)
    o = [f'<div id="{tid}" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:#1B1F27;border-radius:18px;overflow:hidden;box-shadow:{SH_HERO}">',
         '<div style="height:48px;background:#262B35;display:flex;flex-direction:row;align-items:center;gap:10px;padding:0 20px">'
         + "".join(f'<div style="width:14px;height:14px;border-radius:50%;background:{c}"></div>' for c in ("#FF5F57", "#FEBC2E", "#28C840")) + '</div>',
         '<div style="padding:24px 34px;display:flex;flex-direction:column">']
    for i, l in enumerate(lines):
        if l.startswith("$ "):
            t = f'<span style="color:#7FD18B">$</span> <span style="color:#F1F3F7">{e(l[2:])}</span>'
        else:
            t = f'<span style="color:#C3CAD6">{e(l) if l else "&#8203;"}</span>'
        o.append(p(f"font-family:{MONO};font-size:{fs}px;line-height:{lh}px;white-space:pre;width:fit-content", t, f' id="{tid}-{i}"'))
    o.append('</div></div>')
    return o


def hairrow(x, y, w, h, inner, rid=None, attrs="", top_line=True):
    ida = f' id="{rid}"' if rid else ""
    bt = f"border-top:1.5px solid {HAIR};" if top_line else ""
    return f'<div{ida}{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;{bt}display:flex;flex-direction:row;align-items:center;gap:28px">{inner}</div>'


def C(base, **kw):
    d = dict(base)
    d.update(kw)
    return d


# ---------- real output (tools/demo.sh, tools/run_nb.py) ----------
C_X = {"id": "c-x", "lines": ["x = 10"], "lids": ["l-x"]}
C_P = {"id": "c-p", "lines": ["print(x * 2)"]}
C_NAME = {"id": "c-name", "lines": ['name = "kim"', 'name']}
C_INC = {"id": "c-inc", "lines": ["x = x + 1", "x"]}
NAME_ERR = "NameError: name 'x' is not defined"
SYN_ERR = "SyntaxError: invalid syntax"


def build():
    ORDER.clear()
    SECTIONS.clear()

    # ---------- cover ----------
    global CUR
    CUR = "cover"
    o = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
         '<p style="width:820px;font-size:28px;font-weight:700;color:#F2B27A">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
         '<h1 style="width:980px;font-size:92px;font-weight:900;line-height:1.14;color:#F6F5F1">VS Code에서<br>Jupyter 노트북 쓰기</h1>',
         '<p style="width:820px;font-size:40px;line-height:1.4;color:#BFC6D4">셀 실행하는 법과<br>자주 쓰는 단축키</p>']
    o2, pos, _, _ = scene([C(C_X, n=1), C(C_P, n=2, out=["20"])], s=1.25, toolbar=False, sel="c-p", pre="cv-", x=1180, y=330, right=2100)
    o += o2 + [selbar(28, pos["c-p"][0], pos["c-p"][2], pre="cv-"), '</div>']
    o.append(shine(1, "cv-c-p-box"))
    W("cover", o, "09에서 VS Code에 Jupyter를 연결하고 첫 셀을 실행했어요. 이번 챕터는 그 노트북을 손에 익히는 시간이에요. 셀을 실행하는 세 가지 키, 실행 번호 읽는 법, 명령 모드와 편집 모드, Windows와 Mac 단축키를 차례로 봐요.", ("intro", "들어가기"))

    ORDER.append("toc")   # written last, after page numbers are known

    # ---------- why: a .py file reruns from the top ----------
    o = [sec("why")] + head("들어가기", "파일은 실행할 때마다 처음부터 다시 돌아요", JP)
    term = ["$ uv run main.py", "20", "", "$ cat main.py", "x = 10", "print(x * 2)", "x = x + 1", "print(x)", "", "$ uv run main.py", "20", "11"]
    o += terminal(term, 96, 214, 1060, 1080 - 214 + 60, fs=30, tid="wt")
    if RECTS.get("why"):
        x_, y_, w2, h2 = RECTS["why"]["wt-10"]
        o.append(underline(1, x_ - 4, x_ + w2 + 4, y_ + h2 - 4, color="#F2B27A", width=5))
    o += lead(1, "wt-10", "앞에서 본 20이 또 나와요", side="r", dx=40, color="#F2B27A", gap=24)
    o.append(pulse(1, "wt-1"))
    o.append(f'<div{bi("rise", 2)} style="position:absolute;left:0;top:0;width:1920px;height:1080px">')
    w_, top = window(1110, 300, 714, toolbar=False, pre="wy-", h=540)
    o += w_
    cs, pos = cells([C(C_X, n=1, lids=None), C(C_P, n=2, out=["20"]), {"id": "c-new", "lines": ["x = x + 1", "print(x)"], "n": 3, "out": ["11"]}], 1136, top, 714, sel="c-new", pre="wy-", fs=30)
    o += cs + [selbar(1136, pos["c-new"][0], pos["c-new"][2], pre="wy-")]
    o.append(caption("노트북은 새로 적은 셀만 실행하고,<br>앞에서 만든 x를 그대로 써요.", 870, left=1200, width=624, size=28, color=INK))
    o.append('</div>')
    W("why", o, "파이썬 파일은 uv run으로 실행할 때마다 맨 윗줄부터 끝까지 다시 돌아요. 두 줄을 더 적고 다시 실행했더니 앞에서 이미 본 20이 또 나왔어요. 줄이 수십 개가 되면 한 줄 확인하려고 매번 처음부터 기다려야 해요. 노트북은 코드를 셀이라는 칸으로 나눠서, 새로 적은 셀만 실행해요. 앞 셀에서 만든 x도 그대로 기억하고 있어요. 터미널 출력은 tools/demo.sh로 hello-uv에서 실제로 실행한 결과예요.", None)

    # ---------- big picture: cells run in the kernel ----------
    o = [sec("big")] + head("들어가기", "셀은 커널에서 실행되고, 결과는 셀 아래로 돌아와요", JP)
    o2, pos, _, G = scene([C(C_X, n=1, n_st=st({"1": {"html": "[ ]"}})), C(C_P, n=2, out=["20"], n_st=st({"2": {"html": "[ ]"}}), out_attrs=bi("rise", 2)),
                           {"id": "c-e", "lines": [""]}], s=1.25, pre="bp-", x=96, y=214, right=1096)
    o += o2 + ['</div>']
    o += kernel_panel(1330, 380, 494, [("x", "10", bi("fly", 1) + ' data-from="bp-l-x"')], pre="bp-", title="기억하는 값")
    o.insert(len(o) - 3, p(f"font-size:40px;font-weight:700;color:{JP}", "커널") + p(f"font-size:26px;color:{SUB};margin-bottom:18px", ".venv 안의 파이썬"))
    y1 = G(0, pos["c-x"][0] + pos["c-x"][1] / 2)[1]
    y2 = G(0, pos["c-p"][0] + pos["c-p"][1] + 34)[1]
    o.append(f'<svg{bi("draw", 1)} viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible">'
             f'<path id="bp-go" d="M1076,{y1:.0f} C1190,{y1:.0f} 1200,470 1300,470" fill="none" stroke="{BL}" stroke-width="5" stroke-linecap="round"/>'
             f'<path d="M1300,470 l-20,-12 M1300,470 l-20,12" fill="none" stroke="{BL}" stroke-width="5" stroke-linecap="round"/></svg>')
    o.append(f'<div{PATH(1, "bp-go")} style="position:absolute;left:1291px;top:461px;width:18px;height:18px;border-radius:50%;background:{BL};box-shadow:0 0 0 6px rgba(36,89,201,.18)"></div>')
    o.append(p(f"position:absolute;left:1150px;top:{y1 - 60:.0f}px;font-size:26px;font-weight:700;color:{BL}", "코드를 보내요", bi("fade", 1)))
    o.append(f'<svg{bi("draw", 2)} viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible">'
             f'<path id="bp-back" d="M1300,640 C1190,640 1190,{y2:.0f} 1076,{y2:.0f}" fill="none" stroke="{GR}" stroke-width="5" stroke-linecap="round"/>'
             f'<path d="M1076,{y2:.0f} l20,-12 M1076,{y2:.0f} l20,12" fill="none" stroke="{GR}" stroke-width="5" stroke-linecap="round"/></svg>')
    o.append(f'<div{PATH(2, "bp-back")} style="position:absolute;left:1067px;top:{y2 - 9:.0f}px;width:18px;height:18px;border-radius:50%;background:{GR};box-shadow:0 0 0 6px rgba(31,138,76,.18)"></div>')
    o.append(p(f"position:absolute;left:1150px;top:{y2 + 34:.0f}px;font-size:26px;font-weight:700;color:{GR}", "결과를 돌려줘요", bi("fade", 2)))
    o.append(caption("값은 파일이 아니라 커널이 기억해요.", 880, left=1330, width=494, size=28, color=SUB, order=2))
    W("big", o, "노트북에서 셀을 실행하면 코드가 커널로 가요. 커널은 VS Code가 뒤에서 켜 둔 파이썬이에요. 09에서 고른 .venv의 파이썬이 커널이 돼요. 1번 셀의 x = 10을 실행하면 커널이 x를 기억해요. 2번 셀을 실행하면 커널이 기억한 x로 계산하고, 결과 20을 2번 셀 바로 아래로 돌려줘요. notebook.ipynb 파일에는 코드와 출력이 저장되고, x 같은 값은 커널에만 있어요. 그래서 VS Code를 다시 열면 값을 다시 만들어야 해요.", None)

    # ---------- ready: what chapter 09 already did ----------
    o = [sec("ready")] + head("들어가기", "준비는 09에서 마쳤어요", JP)
    done = [("Python, Jupyter 확장 설치", "09 · 25쪽", False), ("uv add --dev ipykernel", "09 · 26쪽", True), ("커널로 .venv 고르기", "09 · 27쪽", True)]
    for i, (a_, b_, mono) in enumerate(done):
        o.append(hairrow(96, 240 + i * 120, 700, 120,
                         f'<x-icon name="CheckCircle" style="width:44px;height:44px;color:{GR}"></x-icon>'
                         + p(f"flex:1;{'font-family:' + MONO + ';' if mono and a_.startswith('uv') else ''}font-size:30px;font-weight:700;color:{INK}", e(a_))
                         + p(f"font-size:24px;font-weight:700;color:{GRAY};white-space:nowrap", e(b_)), top_line=i > 0))
    o.append(p(f"position:absolute;left:96px;top:620px;width:700px;font-size:27px;line-height:1.5;color:{SUB}", "하나라도 빠졌으면 09 슬라이드의 그 쪽부터 따라 해요."))
    # command palette: the one new action on this slide
    o.append(p(f"position:absolute;left:900px;top:236px;font-size:26px;font-weight:700;color:{INK}", "새 노트북 만들기"))
    o.append(f'<div style="position:absolute;left:900px;top:290px;display:flex;flex-direction:row;align-items:center;gap:18px">'
             + p(f"font-size:22px;font-weight:700;color:{BL}", "Windows") + kbd("Ctrl+Shift+P", 26) + p(f"font-size:22px;font-weight:700;color:{GRAY};margin-left:18px", "Mac") + kbd("Cmd+Shift+P", 26) + '</div>')
    pal = [("Create: New Jupyter Notebook", True), ("Notebook: Select Notebook Kernel", False), ("Jupyter: Export to Python Script", False)]
    o.append(f'<div style="position:absolute;left:900px;top:380px;width:924px;background:#FFFFFF;border:1.5px solid #D9D5CB;border-radius:16px;box-shadow:{SH_HERO};padding:14px;display:flex;flex-direction:column;gap:6px">'
             + p(f"font-family:{MONO};font-size:26px;color:{INK};border:2px solid {SEL};border-radius:10px;padding:10px 16px", "&gt;Create: New Jupyter")
             + "".join(p(f"font-size:26px;{'font-weight:700;color:' + INK + ';background:#E8F0FD' if on else 'color:' + SUB};border-radius:10px;padding:12px 16px", e(t), ' id="pal-new"' if on else "") for t, on in pal) + '</div>')
    o.append(aim(1, "pal-new"))
    o.append(p(f"position:absolute;left:900px;top:760px;width:924px;font-size:27px;line-height:1.5;color:{SUB}", "열린 노트북을 hello-uv 폴더에 저장하고, 오른쪽 위 커널이 .venv인지 봐요.", bi("fade", 2)))
    o.append(cursor_off(2))
    o.append(f'<div style="position:absolute;left:96px;top:880px;width:1728px;height:1.5px;background:{HAIR}"></div>')
    o.append(caption("이번 챕터는 09에서 만든 hello-uv 폴더를 VS Code로 열고 시작해요.", 910, size=30))
    W("ready", o, "09의 7파트에서 확장 두 개를 설치하고, uv add --dev ipykernel로 커널 패키지를 넣고, 노트북 커널로 .venv를 골랐어요. 이 세 가지가 끝나야 셀이 실행돼요. 새 노트북은 09처럼 탐색기에서 notebook.ipynb 파일을 만들어도 되고, 명령 팔레트에서 Create: New Jupyter Notebook을 골라도 돼요. 명령 팔레트로 만들면 이름 없는 노트북이 열려서, 저장할 때 hello-uv 폴더 안에 이름을 붙여요. 새로 만들면 커널을 다시 골라야 할 수 있어요. 메뉴 글자는 VS Code 버전에 따라 조금 달라요.")

    # ---------- smallest run: Shift+Enter ----------
    o = [sec("first")] + head("들어가기", "Shift+Enter 한 번이면 셀이 실행돼요", JP)
    o2, pos, _, G = scene([C(C_X, n=1, n_st=st({"1": {"html": "[ ]"}})),
                           C(C_P, n=2, out=["20"], oids=["o-20"], n_st=st({"2": {"html": "[ ]"}}), out_attrs=bi("rise", 2)),
                           {"id": "c-n3", "lines": [""], "attrs": st({"2": {"css": "opacity:0"}})}], s=1.45, sel="c-n3", mode="edit")
    o += o2
    o.append(selbar(28, pos["c-n3"][0], pos["c-n3"][1], attrs=st({"1": {"css": f"top:{pos['c-x'][0]}px;height:{pos['c-x'][1]}px"}, "2": {"css": f"top:{pos['c-p'][0]}px;height:{pos['c-p'][1]}px"}})))
    o.append('</div>')
    o += lead(1, "c-x-n", "실행한 순서대로 번호가 붙어요", side="l", edge=640)
    o += lead(2, "o-20", "결과는 셀 바로 아래에 나와요", side="l", edge=640)
    o.append(keycard(96, 720, 544, "Shift+Enter", "Shift+Enter", "실행하고 다음 셀로 내려가요.<br>Windows와 Mac이 같아요."))
    W("first", o, "가장 많이 쓰는 키부터 눌러 봐요. 1번 셀을 고른 채 Shift+Enter를 치면 셀이 실행되고 [1] 번호가 붙어요. x = 10은 값을 기억만 해서 출력이 없어요. 파란 막대는 2번 셀로 내려가요. 한 번 더 치면 2번 셀이 실행되고 결과 20이 셀 바로 아래에 나와요. 마지막 셀에서 치면 아래에 빈 셀을 하나 만들어 줘요. 09에서 첫 셀을 실행할 때 쓴 키예요. 출력은 tools/run_nb.py로 hello-uv 커널에서 실제로 실행한 결과예요.", None)

    # ---------- part 1: the notebook screen ----------
    EB1 = "1. 노트북 화면 읽기"
    o = [sec("screen")] + head(EB1, "노트북 화면은 다섯 곳만 알면 돼요", BL)
    SX, SY, SW = 560, 300, 1264
    w_, top = window(SX, SY, SW)
    o += w_
    cs, pos = cells([C(C_X, n=1), C(C_P, n=2, out=["20"], oids=["o-20"]), {"id": "c-md", "kind": "mdr", "lines": ["# 오늘 배운 것", "- 셀은 따로 실행해요"]}], SX + 28, top, SW - 48, sel="c-p")
    o += cs + [selbar(SX + 28, pos["c-p"][0], pos["c-p"][2])]
    marks = [("kernel", "커널 " + sub("· .venv인지 봐요"), dict(side="t", dy=150, align="right")),
             ("tb-tools", "위쪽 버튼 " + sub("· 셀 추가, 전체 실행, 다시 시작"), dict(side="t", dy=100)),
             ("sel", "선택 막대 " + sub("· 지금 고른 셀"), dict(side="l", edge=500, at=(SX + 28 - 10, pos["c-p"][0] + pos["c-p"][2] - 24))),
             ("c-p-n", "실행 번호 " + sub("· 실행한 순서"), dict(side="l", edge=500, dy=-70)),
             ("o-20", "출력 " + sub("· 결과는 셀 바로 아래"), dict(side="r", dx=60))]
    for i, (tid, text, kw) in enumerate(marks, 1):
        o.append(spot(i, target=tid, pad=10, r=12))
        o += lead(i, tid, text, z=41, **kw)
    o.append(spot_off(6))
    W("screen", o, "VS Code에서 노트북을 열면 보이는 화면을 단순하게 그렸어요. 오른쪽 위는 커널 이름이에요. 09에서 고른 .venv가 보여야 해요. 위쪽 줄에는 셀을 더하는 + Code, + Markdown과 전체 실행, 다시 시작 버튼이 있어요. 셀 왼쪽의 파란 막대는 지금 고른 셀이에요. 대괄호 숫자는 몇 번째로 실행했는지 보여 줘요. 실행하지 않은 셀은 비어 있어요. 출력은 셀 바로 아래에 붙어요. 맨 아래 칸은 글을 적는 마크다운 셀이에요. 실제 화면은 VS Code 버전과 테마에 따라 색과 글자가 조금 달라요.", ("screen", "노트북 화면 읽기"))

    o = [sec("kinds")] + head(EB1, "셀은 코드 셀과 마크다운 셀 두 가지예요", BL)
    w_, top = window(96, 214, 1728, toolbar=False)
    o += w_
    kc = [C(C_NAME, n=3, out=["'kim'"], oids=["k-out"]), {"id": "m-edit", "kind": "md", "lines": ["# 오늘 배운 것", "- 셀은 따로 실행해요", "- **Shift+Enter**로 실행"]}]
    cs, pos = cells(kc, 124, top, 1672, sel="m-edit", mode="edit")
    o += cs + [selbar(124, pos["m-edit"][0], pos["m-edit"][1])]
    o += lead(1, "k-out", "마지막 줄이 값이면 print 없이도 보여 줘요", side="r", dx=60)
    if RECTS.get("kinds"):
        for tid in ("c-name-tag", "m-edit-tag"):
            x_, y_, w2, h2 = RECTS["kinds"][tid]
            o.append(box(2, x_ - 10, y_ - 6, w2 + 20, h2 + 12, color=OR, width=4))
    o.append(p(f"position:absolute;right:120px;top:{pos['m-edit'][0] + pos['m-edit'][1] + 22}px;font-size:26px;font-weight:700;color:{OR}", "셀 종류는 오른쪽 아래 글자로 봐요", bi("fade", 2)))
    my = pos["m-edit"][0] + pos["m-edit"][1] + 90
    o.append(f'<div id="m-view"{bi("fly", 3)} data-from="m-edit-box" style="position:absolute;left:228px;top:{my}px;width:760px;background:#FFFFFF;border-radius:18px;box-shadow:{SH_SAT};padding:22px 32px;display:flex;flex-direction:column">'
             + p(f"font-size:22px;font-weight:700;color:{GRAY};margin-bottom:6px", "Shift+Enter 뒤")
             + "".join(md_render(l, 34) for l in kc[1]["lines"]) + '</div>')
    W("kinds", o, "코드 셀은 파이썬 코드를 커널로 보내 실행하고 결과를 아래에 보여 줘요. 마지막 줄이 값이면 print 없이도 따옴표까지 그대로 보여요. 마크다운 셀은 실행하지 않고 글을 꾸며 보여 줘요. 01에서 README를 쓸 때 본 # 제목, - 목록, **굵게**를 그대로 써요. 마크다운 셀을 Shift+Enter로 실행하면 꾸며진 모습이 되고, 두 번 클릭하면 다시 고칠 수 있어요. 셀 종류는 셀 오른쪽 아래 글자로 구분하고, 그 글자를 눌러서 바꿀 수도 있어요. 왼쪽 셀의 출력은 tools/demo.sh에서 hello-uv 커널로 실제로 실행한 결과예요.")

    # ---------- part 2: running cells ----------
    EB2 = "2. 셀 실행하기"
    o = [sec("run-ctrl")] + head(EB2, "Ctrl+Enter는 실행하고 그 셀에 머물러요", BL)
    o2, pos, _, G = scene([C(C_X, n=1, n_st=st({"1": {"html": "[ ]"}})), C(C_P)], s=1.45, sel="c-x")
    o += o2 + [selbar(28, pos["c-x"][0], pos["c-x"][1]), '</div>']
    o += lead(1, "sel", "막대가 1번 셀에 그대로 있어요", side="l", edge=640)
    o.append(keycard(96, 720, 544, "Ctrl+Enter", "control+Enter", "같은 셀을 고쳐 가며<br>다시 돌려 볼 때 써요."))
    if RECTS.get("run-ctrl"):
        x_, y_, w2, h2 = RECTS["run-ctrl"]["keys-mac"]
        o.append(underline(2, x_ + 4, x_ + 150, y_ + h2 + 10, color=OR))
        o += lead(2, "keys-mac", "Cmd가 아니에요", side="r", dx=30, color=OR, size=24)
    W("run-ctrl", o, "셀을 고른 상태에서 Ctrl+Enter를 치면 그 셀만 실행해요. x = 10은 출력이 없어서 실행 번호 [1]만 생겨요. 파란 막대는 그대로 1번 셀에 있어요. 그래서 같은 셀을 고치고 Ctrl+Enter, 또 고치고 Ctrl+Enter 하며 결과를 바로 봐요. Mac은 Cmd가 아니라 control 키예요. VS Code 기본 설정이 그래요.", ("run", "셀 실행하기"))

    o = [sec("run-alt")] + head(EB2, "Alt+Enter는 실행하고 아래에 새 셀을 만들어요", BL)
    _, pos, _, _ = scene([C(C_X), {"id": "c-new", "lines": [""]}, C(C_P)], s=1.45)
    p_before = pos["c-new"][0]
    o2, _, _, G = scene([C(C_X, n=1, n_st=st({"1": {"html": "[ ]"}})), {"id": "c-new", "lines": [""], "attrs": st({"1": {"css": "opacity:0"}})},
                         C(C_P, attrs=st({"1": {"css": f"top:{p_before}px"}}))], s=1.45, sel="c-new", mode="edit")
    o += o2
    o.append(selbar(28, pos["c-new"][0], pos["c-new"][1], attrs=st({"1": {"css": f"top:{pos['c-x'][0]}px;height:{pos['c-x'][1]}px"}})))
    o.append('</div>')
    o += lead(1, "c-new-n", "새 셀이 끼어들고,<br>커서가 그 안에서 기다려요", side="l", edge=640)
    o.append(keycard(96, 720, 544, "Alt+Enter", "option+Enter", "결과를 보고 바로 이어서<br>새 코드를 적을 때 써요."))
    W("run-alt", o, "Alt+Enter는 실행하고 바로 아래에 빈 코드 셀을 끼워 넣어요. 새 셀에는 커서가 있어서 바로 칠 수 있어요. 원래 2번 셀은 한 칸 아래로 밀려요. Mac은 Alt 자리에 있는 option 키예요. 세 키를 다 외우기 어려우면 Shift+Enter 하나로 시작해도 충분해요.")

    # run order and the kernel's memory
    def run_scene(sid, title, transition, inc_n, inc_out, mem_x, extra):
        o = [sec(sid, transition)] + head(EB2, title, BL)
        o2, pos, _, _ = scene([C(C_X, n=1), C(C_P, n=2, out=["20"]), C(C_NAME, n=3, out=["'kim'"], oids=["o-kim"]), C(C_INC, n=inc_n, out=[inc_out], oids=["o-inc"], **extra.get("inc", {}))],
                              toolbar=False, sel="c-inc")
        o += o2 + [selbar(28, pos["c-inc"][0], pos["c-inc"][2]), '</div>']
        o += kernel_panel(96, 240, 520, [("name", "'kim'") + extra.get("mem_name", ()), ("x", mem_x) + extra.get("mem_x", ())])
        return o, pos

    o, pos = run_scene("order", "대괄호 숫자는 실행한 순서예요", "fade", 4, "11", "11",
                       {"mem_name": (bi("fly", 1) + ' data-from="o-kim"',), "mem_x": (bi("fly", 2) + ' data-from="o-inc"',)})
    o.append(caption("4번 셀을 한 번 더 실행하면<br>어떻게 될까요?", 620, width=520, size=32, order=3))
    o.append(pulse(3, "mem-x-v"))
    W("order", o, "1번 셀에서 x에 10을 넣었고, 2번 셀은 그 x로 20을 출력했어요. 셀은 따로 실행해도 값은 커널 하나가 계속 기억해요. 왼쪽이 지금 커널이 기억하는 값이에요. 3번 셀에서 name에 'kim'을 넣었고, 4번 셀은 x에 1을 더해서 11이 됐어요. 다음 장에서 4번 셀을 한 번 더 실행해요. 출력은 tools/run_nb.py로 hello-uv 커널에서 실제로 실행한 결과예요.")

    o, pos = run_scene("again", "같은 셀을 다시 실행하면 번호도 값도 바뀌어요", "magic", 5, "12", "12",
                       {"inc": {"n_st": st({"1": {"html": "[4]"}}), "out_st": ""}, "mem_x": ("", st({"1": {"html": "11", "css": "background:transparent"}}) + "")})
    # the output line and the memory value change in place
    o = [x_.replace('id="o-inc"', 'id="o-inc"' + st({"1": {"html": "11"}})) if 'id="o-inc"' in x_ else x_ for x_ in o]
    o = [x_.replace('id="mem-x-v" style="', 'id="mem-x-v" style="background:#FFE7A8;', 1) if 'id="mem-x-v"' in x_ else x_ for x_ in o]
    o += lead(1, "c-inc-n", "화면 순서가 아니라<br>누른 순서예요", side="l", edge=640)
    W("again", o, "같은 셀을 다시 실행하면 새 번호 [5]가 붙고, x는 11에서 1이 더 커져 12가 돼요. 노트북은 화면에 보이는 위아래 순서가 아니라 내가 누른 순서대로 실행해요. 그래서 셀을 이리저리 실행하다 보면 같은 코드인데 결과가 달라져요. 번호가 1, 2, 3 차례가 아니면 다음 장의 Restart와 Run All로 위에서부터 다시 실행해요. 출력은 run_nb.py로 같은 셀을 두 번 실행한 실제 결과예요.")

    o = [sec("restart")] + head(EB2, "Restart는 커널이 기억한 값을 지워요", BL)
    out20 = p(f"font-family:{MONO};font-size:32px;line-height:{lh_of(32)}px;white-space:pre;color:{INK};width:fit-content", "20")
    o2, pos, _, _ = scene([C(C_X, n=1), C(C_P, n=1, out=[NAME_ERR], err=True, oids=["o-err"], n_st=st({"2": {"html": "[2]"}}), out_st=st({"2": {"html": out20}})),
                           C(C_NAME, n=3, out=["'kim'"]), C(C_INC, n=5, out=["12"])], fs=32, sel="c-p")
    o += o2 + [selbar(28, pos["c-p"][0], pos["c-p"][2]), '</div>']
    gone = st({"1": {"css": "opacity:1"}})
    o += kernel_panel(96, 240, 520, [("name", "'kim'", gone, "", "opacity:0"), ("x", "12", gone, "", "opacity:0")])
    o.append(p(f"position:absolute;left:126px;top:340px;font-size:28px;color:{GRAY};{MOVE}", "비어 있어요", ' id="mem-empty"' + st({"1": {"css": "opacity:0"}})))
    o.append(aim(1, "tb-restart"))
    if RECTS.get("restart"):
        x_, y_, w2, h2 = RECTS["restart"]["o-err"]
        o.append(ring(2, x_, y_, w2, h2, color=RED, width=5))
    o.append(caption("2번 셀만 실행하면 x를 몰라서<br>NameError가 나요.", 560, width=520, size=28, color=RED, order=2))
    o.append(aim(3, "tb-runall"))
    o.append(caption("꼬이면 ↻ Restart 뒤 ▷ Run All.<br>맨 위 셀부터 다시 실행해요.", 760, width=540, size=28, color=GR, order=3))
    W("restart", o, "Restart는 커널을 껐다 켜요. 커널이 기억하던 x와 name이 모두 사라져요. 화면의 코드와 예전 출력은 그대로 남아 있어서 헷갈리기 쉬워요. 이 상태에서 2번 셀만 실행하면 번호가 [1]부터 다시 시작하고 NameError가 나요. 해결은 Run All이에요. 맨 위 셀부터 차례로 다시 실행해서 값을 다시 만들어요. 이미 불러온 패키지를 uv add로 바꾼 뒤에도 Restart를 눌러요. 출력은 run_nb.py가 새 커널에서 2번 셀만 실행한 실제 결과예요. 오류 위에 Traceback 몇 줄이 더 나오는데 마지막 줄만 옮겼어요.")

    # toolbar close-up: one strip, labels below each button
    o = [sec("buttons")] + head(EB2, "위쪽 버튼으로 노트북 전체를 다뤄요", BL)
    items = [("bt-code", "+ Code", False), ("bt-md", "+ Markdown", False), ("bt-run", "▷ Run All", False), ("bt-restart", "↻ Restart", False), ("bt-int", "□ Interrupt", True),
             ("bt-clear", "Clear All Outputs", False), ("bt-vars", "Variables", False)]
    o.append(f'<div style="position:absolute;left:96px;top:236px;width:1728px;height:150px;background:#FFFFFF;border:1.5px solid #D9D5CB;border-radius:18px;overflow:hidden;box-shadow:{SH_HERO}">'
             f'<div style="height:52px;background:#EFEDE7;display:flex;align-items:flex-end;padding:0 18px"><div style="height:42px;background:#FFFFFF;border-radius:10px 10px 0 0;padding:0 22px;display:flex;align-items:center">'
             + p(f"font-family:{MONO};font-size:20px;font-weight:700;color:{INK}", "notebook.ipynb") + '</div></div>'
             f'<div style="height:96px;display:flex;flex-direction:row;align-items:center;padding:0 34px;gap:66px">'
             + "".join(p(f"font-size:32px;color:{INK};white-space:nowrap;{'border:2px dashed #B9BEC8;border-radius:10px;padding:4px 12px;color:' + GRAY if dash else ''}", e(t), f' id="{i}"') for i, t, dash in items)
             + '</div></div>')
    expl = [("bt-run", "맨 위부터 끝까지 실행", "노트북을 처음 열었을 때,<br>Restart 뒤", 130),
            ("bt-restart", "커널이 기억한 값 지우기", "결과가 이상하거나<br>번호가 꼬였을 때", 400),
            ("bt-int", "실행 중인 셀 멈추기", "셀이 안 끝날 때.<br>실행 중에만 보여요", 124),
            ("bt-clear", "출력만 지우기", "커널이 기억한 값은 그대로예요", 400),
            ("bt-vars", "기억한 값을 표로 보기", "아래쪽에 표가 열려요", 130)]
    for i, (tid, a_, b_, dy) in enumerate(expl, 1):
        o += lead(i, tid, a_ + f'<br><span style="font-size:24px;font-weight:400;color:{SUB}">{b_}</span>', side="b", dy=dy, gap=12, align="center", w=360, extra=DIM("btn"))
    o.append(caption("+ Code와 + Markdown은 셀을 더하는 버튼이에요. 화면이 좁으면 몇 개는 ··· 메뉴 안에 들어가요.", 960, size=26, color=SUB))
    W("buttons", o, "맨 위 줄 버튼은 노트북 전체를 한 번에 다뤄요. Run All은 맨 위 셀부터 끝까지 실행해요. 노트북을 새로 열었을 때도 커널은 아무것도 기억하지 않아서 Run All부터 눌러요. Restart는 앞 장에서 본 대로 기억을 지워요. Interrupt는 셀이 실행되는 동안에만 보이는 버튼이에요. 끝나지 않는 셀을 멈춰요. Clear All Outputs는 화면의 출력만 지우고 커널의 값은 남겨요. Variables는 커널이 기억하는 값을 표로 보여 줘요.")

    # ---------- part 3: command mode and edit mode ----------
    EB3 = "3. 명령 모드와 편집 모드"
    o = [sec("modes")] + head(EB3, "셀에는 명령 모드와 편집 모드가 있어요", PUR)
    MX = 620
    o += cell(C(C_X), MX, 290, 1204, sel="c-x", mode="cmd", pre="m0-", fs=42)
    o.append(selbar(MX, 290, box_h(C_X, 42), pre="m0-"))
    o += cell(C(C_X), MX, 620, 1204, sel="c-x", mode="edit", pre="m1-", fs=42)
    o.append(selbar(MX, 620, box_h(C_X, 42), pre="m1-"))
    o += lead(None, "m0-sel", f'<span style="color:{PUR}">명령 모드</span><br><span style="font-size:26px;font-weight:400;color:{SUB}">막대만 보여요. 셀을 통째로 다뤄요</span>', side="l", dx=40, size=36, at=None)
    o += lead(None, "m1-sel", f'<span style="color:{SEL}">편집 모드</span><br><span style="font-size:26px;font-weight:400;color:{SUB}">테두리와 커서. 글자를 고쳐요</span>', side="l", dx=40, size=36)
    o.append(f'<div{bi("pop", 1)} style="position:absolute;left:980px;top:435px;display:flex;flex-direction:row;align-items:center;gap:16px">' + kbd("Enter", 32) + p(f"font-size:44px;font-weight:700;color:{SEL}", "↓") + '</div>')
    o.append(f'<div{bi("pop", 2)} style="position:absolute;left:1300px;top:435px;display:flex;flex-direction:row;align-items:center;gap:16px">' + p(f"font-size:44px;font-weight:700;color:{PUR}", "↑") + kbd("Esc", 32) + '</div>')
    o.append(aim(3, "m1-c-x-box", fx=0.55, fy=0.7))
    o.append(caption("셀 안을 클릭해도 편집 모드예요. A, B, M 같은 글자 키는 명령 모드에서만 동작해요.", 880, size=28, color=INK, order=3))
    W("modes", o, "같은 키가 모드에 따라 다르게 동작해요. 명령 모드는 셀 하나를 통째로 다루는 상태예요. 왼쪽에 막대만 보여요. 편집 모드는 셀 안에 커서가 깜빡이는 상태예요. 막대와 함께 셀 테두리가 파랗게 진해져요. 명령 모드에서 Enter를 치면 편집 모드, 편집 모드에서 Esc를 치면 명령 모드로 가요. 셀 안을 클릭해도 편집 모드, 셀 왼쪽 빈 곳을 클릭하면 명령 모드예요. 명령 모드에서 B를 치면 셀이 생기고, 편집 모드에서 B를 치면 글자 b가 들어가요. 처음에 가장 많이 헷갈리는 부분이에요. Enter와 Esc는 Windows와 Mac이 같아요.", ("modes", "명령 모드와 편집 모드"))

    flow = [("flow1", "Esc로 명령 모드", "Esc", [C(C_X, n=1)], "c-x", "cmd", "c-x-box", "커서와 테두리가 빠졌어요"),
            ("flow2", "B로 아래에 셀 추가", "B", [C(C_X, n=1), {"id": "c-n2", "lines": [""]}], "c-n2", "cmd", "c-n2-box", "새 코드 셀이 생기고<br>골라졌어요"),
            ("flow3", "M으로 마크다운, Enter로 글 적기", "M Enter", [C(C_X, n=1), {"id": "c-n2", "kind": "md", "lines": ["# 오늘 배운 것"]}], "c-n2", "edit", "c-n2-tag", "Markdown으로<br>바뀌었어요"),
            ("flow4", "Shift+Enter로 마무리", "Shift+Enter", [C(C_X, n=1), {"id": "c-n2", "kind": "mdr", "lines": ["# 오늘 배운 것"]}, {"id": "c-n3", "lines": [""]}], "c-n3", "edit", "c-n3-box", "제목이 꾸며지고<br>새 셀이 생겨요")]
    steps_ = [("Esc", "명령 모드로"), ("B", "아래에 셀 추가"), ("M Enter", "마크다운, 글 적기"), ("Shift+Enter", "실행하고 다음 셀로")]
    for i, (sid, t, keys, cs_, sel, mode, tid, lab) in enumerate(flow):
        o = [sec(sid, "magic" if i else "fade")] + head(EB3, f"키로만 셀 만들기 {i + 1} · {e(t)}", PUR)
        o2, pos, _, G = scene(cs_, s=1.5, toolbar=False, sel=sel, mode=mode, pre="f-")
        o += o2 + [selbar(28, pos[sel][0], pos[sel][1], pre="f-"), '</div>']
        if tid.endswith("-tag") and RECTS.get(sid):
            x_, y_, w2, h2 = RECTS[sid]["f-" + tid]
            o.append(box(1, x_ - 10, y_ - 6, w2 + 20, h2 + 12, color=PUR, width=4))
        rows = []
        for j, (k, d) in enumerate(steps_):
            col = INK if j == i else (GRAY if j > i else SUB)
            mark = (f'<x-icon name="CheckCircle" style="width:34px;height:34px;color:{GR}"></x-icon>' if j < i else
                    f'<div style="width:34px;height:34px;flex:none;border-radius:50%;background:{PUR if j == i else "#D6D9E0"}"></div>')
            now = (p(f"font-size:24px;font-weight:400;line-height:1.35;color:{PUR};width:270px;white-space:normal;margin-top:4px", lab, bi("fade", 1))) if j == i else ""
            rows.append(f'<div style="height:{124 if j == i else 92}px;display:flex;flex-direction:row;align-items:center;gap:20px;opacity:{1 if j <= i else .55}">{mark}'
                        f'<div style="width:236px;flex:none">{kbd(k, 26)}</div><div style="display:flex;flex-direction:column">' + p(f"font-size:26px;font-weight:{700 if j == i else 400};color:{col};white-space:nowrap", d) + now + '</div></div>')
        combo = {"flow1": ["Esc"], "flow2": ["B"], "flow3": ["M", "Enter"], "flow4": ["Shift+Enter"]}[sid]
        o.append(p(f"position:absolute;left:96px;top:790px;font-size:22px;font-weight:700;color:{GRAY}", "지금 누른 키", bi("fade", 1)))
        kx = 96
        for c_ in combo:
            o.append(keycaps(1, kx, 836, c_, size=34))
            kx += 64 + 26 * len(c_)
        o.append(f'<div id="flow-steps" style="position:absolute;left:96px;top:300px;width:560px;display:flex;flex-direction:column">' + "".join(rows) + '</div>')
        notes = {"flow1": "마우스 없이 셀을 만드는 흐름을 네 장에 걸쳐 봐요. 1번 셀에 x = 10을 적고 실행한 뒤, 셀 안을 다시 클릭해 편집 모드인 상태에서 시작해요. Esc를 치면 커서가 빠지고 명령 모드가 돼요. 지금부터 치는 글자는 셀에 들어가지 않고 명령으로 읽혀요.",
                 "flow2": "명령 모드에서 B를 치면 아래(Below)에 빈 코드 셀이 생겨요. A는 위(Above)에 만들어요. 새 셀은 골라진 상태지만 아직 명령 모드예요. 그래서 다음에 M을 치면 글자가 아니라 셀 종류가 바뀌어요.",
                 "flow3": "M은 마크다운(Markdown), Y는 다시 코드 셀로 바꾸는 키예요. 셀 오른쪽 아래 글자가 Markdown으로 바뀌어요. Enter를 치면 편집 모드가 되고, 01에서 배운 # 제목을 적어요. 한글을 적은 뒤에는 한/영 키로 영문으로 바꿔 두면 다음 단축키가 잘 먹어요.",
                 "flow4": "Shift+Enter로 마크다운 셀을 실행하면 꾸며진 제목이 돼요. 마지막 셀이었으니 아래에 새 코드 셀이 생기고 바로 칠 수 있어요. 키 다섯 번이면 마우스 없이 설명 칸과 코드 칸을 만들어요."}[sid]
        W(sid, o, notes)

    o = [sec("cmdkeys")] + head(EB3, "명령 모드에서 쓰는 글자 키", PUR)
    ck = [("A", "위에 셀 추가", "Above"), ("B", "아래에 셀 추가", "Below"), ("D+D", "셀 지우기", "D를 두 번"), ("Z", "지운 셀 되살리기", "방금 지운 것 되돌리기"),
          ("M", "마크다운 셀로", "Markdown"), ("Y", "코드 셀로", "다시 코드로"), ("L", "줄 번호 켜고 끄기", "오류 줄 찾을 때"), ("Enter", "편집 모드로", "셀 안으로 들어가기")]
    o.append(f'<div{STAGGER(1, 90)} style="position:absolute;left:0;top:0;width:1920px;height:1080px">')
    for i, (k, a_, b_) in enumerate(ck):
        col, row = i // 4, i % 4
        o.append(hairrow(96 + col * 880, 236 + row * 150, 848, 150,
                         f'<div style="width:190px;flex:none">{kbd(k, 40)}</div>'
                         + '<div style="display:flex;flex-direction:column;gap:4px">' + p(f"font-size:32px;font-weight:700;color:{INK}", e(a_)) + p(f"font-size:24px;color:{GRAY}", e(b_)) + '</div>',
                         top_line=row > 0))
    o.append('</div>')
    o.append(caption("Windows와 Mac이 같아요. Shift 없이 그냥 누르고, 글자가 셀에 들어가면 Esc부터 쳐요.", 880, size=28, color=SUB))
    W("cmdkeys", o, "명령 모드에서만 동작하는 글자 키예요. 대문자로 적었지만 Shift 없이 그냥 눌러요. D는 한 번이 아니라 두 번 연달아 눌러야 지워요. 실수로 지웠으면 바로 Z로 되살려요. L은 셀 하나의 줄 번호를 켜요. 오류 메시지에 line 3처럼 줄 번호가 나올 때 써요. 한글 입력 상태에서는 글자 키가 먹지 않을 수 있어요. 한/영 키로 영문으로 바꿔요.")

    # ---------- part 4: compare with uv run, and the usual traps ----------
    EBC = "4. 파일 실행과 비교하고 막힐 때 보기"
    o = [sec("compare")] + head(EBC, "uv run main.py와 노트북은 이렇게 달라요", TEAL)
    cols = [(96, 400), (540, 600), (1180, 644)]
    o.append(hairrow(96, 230, 1728, 70, p(f"width:{cols[0][1]}px;flex:none", "") + p(f"width:{cols[1][1]}px;flex:none;font-family:{MONO};font-size:28px;font-weight:700;color:{INK}", "uv run main.py")
                     + p(f"flex:1;font-size:28px;font-weight:700;color:{JP}", "노트북 셀"), top_line=False))
    cmp = [("cp-file", "코드를 두는 곳", "main.py 파일 하나", "notebook.ipynb의 셀 여러 개"), ("cp-run", "실행하는 단위", "파일 전체, 맨 위부터", "고른 셀 하나"),
           ("cp-mem", "값", "실행이 끝나면 사라져요", "커널이 계속 기억해요"), ("cp-show", "결과 보기", "print로 찍은 것만", "셀 마지막 줄의 값도"),
           ("cp-when", "이럴 때", "완성한 프로그램을 돌릴 때", "하나씩 시험하고 정리할 때")]
    for i, (rid, a_, b_, c_) in enumerate(cmp):
        o.append(hairrow(96, 300 + i * 112, 1728, 112, p(f"width:{cols[0][1]}px;flex:none;font-size:28px;font-weight:700;color:{GRAY}", a_)
                         + p(f"width:{cols[1][1]}px;flex:none;font-size:30px;color:{INK}", b_) + p(f"flex:1;font-size:30px;font-weight:700;color:{INK}", c_), rid=rid))
    o.append(spot(1, target="cp-mem", pad=6, r=14))
    o.append(spot_off(2))
    o.append(caption("다음 챕터부터 파이썬 기초는 노트북 셀에서 실습해요.", 900, size=28, color=SUB, order=2))
    W("compare", o, "09에서 배운 uv run main.py와 노트북을 나란히 놓았어요. 파일은 실행할 때마다 맨 위부터 끝까지 돌고, 끝나면 값이 사라져요. 노트북은 셀 하나씩 실행하고, 값은 커널이 계속 기억해요. 그래서 하나씩 시험해 보며 배울 때는 노트북이 편하고, 다 만든 프로그램을 돌릴 때는 파일이 편해요. 12부터 파이썬 기초 실습은 hello-uv 노트북에서 해요.", ("compare", "파일 실행과 비교하고 막힐 때 보기"))

    o = [sec("err-md")] + head(EBC, "설명 글을 코드 셀에 적으면 SyntaxError가 나요", TEAL)
    o2, pos, _, G = scene([C(C_X, n=1), {"id": "c-bad", "lines": ["오늘 배운 것"], "n": 2, "out": [SYN_ERR], "err": True, "oids": ["o-syn"]}], s=1.45, toolbar=False, sel="c-bad")
    o += o2 + [selbar(28, pos["c-bad"][0], pos["c-bad"][2]), '</div>']
    if RECTS.get("err-md"):
        x_, y_, w2, h2 = RECTS["err-md"]["o-syn"]
        o.append(ring(1, x_, y_, w2, h2, color=RED, width=5))
    o.append(shake(1, "o-syn"))
    o.append(caption("파이썬 코드로 읽어서 나는 오류예요.<br>오른쪽 아래가 Python이에요.", 300, width=540, size=28, color=RED, order=1))
    fx = [f'<div{bi("rise", 2)} style="position:absolute;left:96px;top:620px;width:760px;background:#FFFFFF;border-radius:20px;box-shadow:{SH_SAT};padding:26px 32px;display:flex;flex-direction:column;gap:18px">',
          '<div style="display:flex;flex-direction:row;align-items:center;gap:14px">' + p(f"font-size:26px;font-weight:700;color:{GR}", "이렇게 고쳐요") + kbd("Esc", 26) + p(f"font-size:26px;color:{GRAY}", "다음") + kbd("M", 26) + '</div>',
          md_render("# 오늘 배운 것", 30), p(f"font-size:24px;color:{SUB}", "마크다운 셀로 바꾸고 Shift+Enter를 치면 제목이 돼요."), '</div>']
    o += fx
    W("err-md", o, "셀을 새로 만들면 처음엔 코드 셀이에요. 여기에 설명 글을 적고 실행하면 파이썬이 글을 코드로 읽으려다 SyntaxError를 내요. 셀 오른쪽 아래가 Python이면 코드 셀이에요. Esc로 명령 모드에 간 다음 M을 누르면 마크다운 셀로 바뀌어요. Shift+Enter를 치면 꾸며진 제목이 돼요. 출력은 '오늘 배운 것'을 코드 셀에서 실행한 실제 결과예요. 실제로는 괄호 안에 임시 파일 이름과 줄 번호가 더 붙어요.")

    o = [sec("trouble")] + head(EBC, "노트북에서 막히면 여기부터 봐요", TEAL)
    o.append(hairrow(96, 226, 1728, 60, p(f"width:760px;flex:none;font-size:24px;font-weight:700;color:{GRAY}", "이럴 때") + p(f"width:520px;flex:none;font-size:24px;font-weight:700;color:{GRAY}", "이유")
                     + p(f"flex:1;font-size:24px;font-weight:700;color:{GRAY}", "이렇게"), top_line=False))
    tr = [("글자를 쳤는데 셀이 생기거나 지워져요", "명령 모드였어요", "셀 안 클릭, Enter"), ("A, B, M을 눌러도 아무 일이 없어요", "편집 모드거나 한글 입력 상태예요", "Esc, 한/영 키"),
          (NAME_ERR, "앞 셀을 안 돌렸거나 Restart 뒤예요", "▷ Run All"), (SYN_ERR, "설명 글을 코드 셀에 적었어요", "Esc 다음 M"),
          ("셀이 끝나지 않고 계속 돌아요", "오래 걸리거나 끝나지 않는 코드예요", "□ Interrupt"), ("Mac에서 Cmd+Enter로 실행이 안 돼요", "Mac 실행 키는 control이에요", "control+Enter")]
    o.append(f'<div{STAGGER(1, 90)} style="position:absolute;left:0;top:0;width:1920px;height:1080px">')
    for i, (q, a_, cmd) in enumerate(tr):
        mono = q.endswith(("defined", "syntax"))
        o.append(hairrow(96, 286 + i * 112, 1728, 112,
                         p(f"width:760px;flex:none;{'font-family:' + MONO + ';font-size:24px;color:' + RED if mono else 'font-size:29px;color:' + INK};font-weight:700", e(q))
                         + p(f"width:520px;flex:none;font-size:26px;color:{SUB}", e(a_))
                         + p(f"flex:1;font-size:28px;font-weight:700;color:{INK};white-space:nowrap", e(cmd))))
    o.append('</div>')
    W("trouble", o, "첫 두 줄은 모드를 헷갈려서 나요. 셀 테두리와 커서로 지금 모드를 봐요. 한글 입력 상태에서는 명령 모드 글자 키가 먹지 않을 수 있어서 한/영 키로 영문으로 바꿔요. NameError는 Restart 장에서, SyntaxError는 바로 앞 장에서 본 오류예요. 셀이 끝나지 않으면 셀 왼쪽에 도는 표시가 계속 보여요. Mac 실행 키는 다른 프로그램의 Jupyter와 VS Code 기본 설정이 다른 곳이에요. 커널이 .venv가 아니라서 나는 ModuleNotFoundError는 09의 31쪽을 봐요.")

    # ---------- part 5: real notes written in a notebook ----------
    EBM = "5. 노트북에 수업 내용 정리하기"
    RULES = ["---", "### 변수 이름 규칙", "- 숫자로 시작 불가", "- 공백 불가", "- 하이픈(-) 불가", "- 예약어 사용 불가"]
    o = [sec("md-rules")] + head(EBM, "예제 1 · 변수 이름 규칙을 마크다운 셀에 적어요", NAVY)
    mc = {"id": "m-rules", "kind": "md", "lines": RULES, "lids": ["mr-0", "mr-1", "mr-2", None, None, None]}
    o2, pos, _, G = scene([mc], toolbar=False, sel="m-rules", mode="edit")
    o += o2 + [selbar(28, pos["m-rules"][0], pos["m-rules"][1]), '</div>']
    for i, (tid, t) in enumerate([("mr-0", "가로줄"), ("mr-1", "작은 제목"), ("mr-2", "목록")]):
        o += lead(1, tid, t, side="l", edge=640, gap=36, color=NAVY)
    o.append(caption("기호 뒤에는 한 칸 띄워요.", 480, width=544, size=26, color=SUB, order=1))
    vy = RY + pos["m-rules"][0] + pos["m-rules"][1] + 40
    o.append(f'<div id="mr-view"{bi("fly", 2)} data-from="m-rules-box" style="position:absolute;left:300px;top:{vy}px;width:700px;background:#FFFFFF;border-radius:20px;box-shadow:{SH_SAT};padding:22px 34px;display:flex;flex-direction:column">'
             + p(f"font-size:22px;font-weight:700;color:{GRAY};margin-bottom:4px", "Shift+Enter 뒤") + "".join(md_render(l, 30) for l in RULES) + '</div>')
    W("md-rules", o, "노트북은 코드와 설명을 한 파일에 같이 둘 수 있어요. 수업에서 배운 변수 이름 규칙을 마크다운 셀에 적어 봐요. 세 줄 빼기는 위 내용과 나누는 가로줄, 샵 세 개는 01에서 본 # 제목보다 작은 제목, 빼기 하나는 목록이에요. 01과 같이 기호 뒤에는 한 칸을 띄워요. 적은 뒤 Shift+Enter를 치면 아래처럼 꾸며져요. 다음 장에서 규칙을 어기면 실제로 어떤 오류가 나는지 봐요.", ("rules", "노트북에 수업 내용 정리하기"))

    o = [sec("name-err")] + head(EBM, "규칙을 어기면 SyntaxError가 나요", NAVY)
    bad = [("숫자로 시작", '1st_name = "kim"', "SyntaxError: invalid decimal literal", "first_name"),
           ("공백", 'my name = "kim"', "SyntaxError: invalid syntax", "my_name"),
           ("하이픈", 'my-name = "kim"', "SyntaxError: cannot assign to expression here.", "my_name"),
           ("예약어", 'class = "kim"', "SyntaxError: invalid syntax", "class_name")]
    o2, pos, _, G = scene([{"id": f"ne{i}", "lines": [code], "n": i + 1, "out": [err], "err": True} for i, (_, code, err, _) in enumerate(bad)], toolbar=False, fs=32, gap=26)
    o += o2 + ['</div>']
    for i, (lbl, _, _, fix) in enumerate(bad):
        y_ = RY + pos[f"ne{i}"][0] + 6
        o.append(f'<div{bi("pop", i + 1)} style="position:absolute;left:96px;top:{y_}px;width:540px;display:flex;flex-direction:column;align-items:flex-end;gap:6px">'
                 + p(f"font-size:24px;font-weight:700;color:{RED}", e(lbl))
                 + '<div style="display:flex;flex-direction:row;align-items:center;gap:12px">' + p(f"font-size:24px;font-weight:700;color:{GR}", "이렇게")
                 + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{GR};background:#E6F4EC;border-radius:10px;padding:2px 14px", e(fix)) + '</div></div>')
    W("name-err", o, "네 셀을 hello-uv 커널로 실제로 실행한 오류의 마지막 줄이에요. 괄호 안의 임시 파일 이름과 줄 번호는 빼고 옮겼어요. 띄어쓰기와 하이픈 자리에는 밑줄을 써요. 하이픈 오류는 뒤에 Maybe you meant '==' instead of '='? 가 더 붙어요. 파이썬이 my-name을 my 빼기 name이라는 계산으로 읽어서 나는 오류예요. 예약어는 class, True, None처럼 파이썬이 이미 쓰는 단어예요. 예약어는 뒤에 단어를 붙여서 피해요. 오류 메시지 글자는 파이썬 버전에 따라 조금 다를 수 있어요.")

    CONV = ["### 컨벤션", "- 스네이크 표기법: user_name", "- 파스칼 표기법: UserProfile", "- 카멜 표기법: userName"]
    o = [sec("conv")] + head(EBM, "예제 2 · 이름 짓는 표기법 세 가지를 적어요", NAVY)
    kinds_ = [("스네이크 표기법", "snake_case", [("user", INK), ("_", RED), ("name", INK)], "파이썬 변수, 함수 이름", "우리가 쓰는 방식이에요", GR),
              ("파스칼 표기법", "PascalCase", [("U", RED), ("ser", INK), ("P", RED), ("rofile", INK)], "파이썬 클래스 이름", "단어 첫 글자를 모두 대문자로", BL),
              ("카멜 표기법", "camelCase", [("user", INK), ("N", RED), ("ame", INK)], "자바스크립트에서 많이 써요", "파이썬에서는 잘 안 써요", GRAY)]
    for i, (k, en, parts_, use, note, c) in enumerate(kinds_):
        word = "".join(f'<span style="color:{col}">{e(t)}</span>' for t, col in parts_)
        o.append(hairrow(96, 240 + i * 230, 1060, 230,
                         p(f"width:470px;flex:none;font-family:{MONO};font-size:62px;font-weight:700;line-height:1.2", word)
                         + '<div style="display:flex;flex-direction:column;gap:6px">'
                         + '<div style="display:flex;flex-direction:row;align-items:baseline;gap:14px">' + p(f"font-size:32px;font-weight:700;color:{c}", k) + p(f"font-family:{MONO};font-size:22px;color:{GRAY}", en) + '</div>'
                         + p(f"font-size:28px;font-weight:700;color:{INK}", e(use)) + p(f"font-size:24px;color:{SUB}", e(note)) + '</div>',
                         attrs=bi("rise", i + 1), top_line=i > 0))
    w_, top = window(1200, 240, 624, toolbar=False, h=330)
    o += w_
    cs, pos = cells([{"id": "m-conv", "kind": "md", "lines": CONV}], 1210, top, 600, sel="m-conv", mode="edit", fs=26)
    o += cs
    o.append(p(f"position:absolute;left:1200px;top:606px;width:624px;font-size:26px;line-height:1.5;color:{SUB}", "붉은 글자가 단어를 나누는 자리예요.<br>노트북 마크다운 셀에 이렇게 적어 둬요."))
    W("conv", o, "같은 두 단어 user와 name을 이어 붙이는 방법이 세 가지예요. 붉은 글자가 단어를 나누는 자리예요. 스네이크 표기법은 소문자와 밑줄로 이어요. 뱀처럼 바닥에 붙어 있어서 붙은 이름이에요. 파이썬은 변수와 함수 이름에 이 방식을 써요. 파스칼 표기법은 단어마다 첫 글자를 대문자로 써요. 파이썬에서는 클래스 이름에만 쓰고, 클래스는 뒤에서 배워요. 카멜 표기법은 첫 단어만 소문자로 시작해서 낙타 혹처럼 보여요. 자바스크립트 같은 다른 언어에서 많이 써요. 파이썬의 이름 규칙 문서인 PEP 8이 이렇게 정해 두었어요.")

    TYPES_SRC = ["# 정수형 자료형", "age = 25", "", "# 실수 자료형", "pi = 3.14", "", "# 불리언 자료형(Boolean)", "is_alive = True", "",
                 "# 문자열 자료형", 'user_name = "kim"', "", "# 리스트 (다른 언어의 배열과 비슷해요)", "grade_type = [1, 2, 3, 4, 5]"]
    TYPES = [("int", "정수", "소수점 없는 숫자", BL), ("float", "실수", "소수점 있는 숫자", NAVY), ("bool", "불리언", "True, False 두 값만", PUR),
             ("str", "문자열", "따옴표로 감싼 글자", GR), ("list", "리스트", "여러 값을 순서대로", JP)]
    VAL = [1, 4, 7, 10, 13]
    o = [sec("types")] + head(EBM, "예제 3 · 자료형을 코드 셀에 하나씩 적어요", NAVY)
    lids = [f"ty-{i}" if i in VAL else None for i in range(len(TYPES_SRC))]
    o2, pos, _, G = scene([{"id": "c-types", "lines": TYPES_SRC, "n": 1, "lids": lids}], toolbar=False, fs=31)
    o += o2
    lh31 = lh_of(31)
    line_top = lambda i: pos["c-types"][0] + PADY + 2 + i * lh31
    tint = {str(k + 2): {"css": f"opacity:1;top:{line_top(v)}px"} for k, v in enumerate(VAL)}
    tint["1"] = {"css": "opacity:0"}
    o.append(f'<div id="tint"{st(tint)} style="position:absolute;left:{28 + GUT + 2}px;top:{line_top(VAL[-1])}px;width:{1124 - 28 - GUT - 40}px;height:{lh31}px;background:rgba(36,89,201,.11);opacity:0;pointer-events:none;{MOVE}"></div>')
    o.append('</div>')
    for i, (t, k, d, c) in enumerate(TYPES):
        o += lead(i + 1, f"ty-{VAL[i]}", f'<span style="color:{c}">{k}</span> <span style="font-family:{MONO};font-size:24px;color:{GRAY}">{t}</span><br><span style="font-size:22px;font-weight:400;color:{SUB}">{d}</span>',
                  side="l", edge=640, gap=34, size=28, dy=14)
    W("types", o, "수업에서 보여 주는 기본 자료형 다섯 가지를 한 셀에 적었어요. 줄마다 # 주석으로 무슨 자료형인지 적어 두면 노트북만 다시 열어도 복습이 돼요. # 뒤는 설명이라 실행하지 않아요. 변수 이름은 앞 장의 스네이크 표기법을 따라 is_alive, user_name, grade_type처럼 적었어요. 대괄호로 묶은 [1, 2, 3, 4, 5]는 파이썬에서 리스트라고 불러요. 다른 언어에서 배열이라고 부르는 것과 비슷해요. True와 False는 첫 글자를 대문자로 써요. 이 셀은 값을 기억만 해서 출력이 없어요.")

    o = [sec("type-check")] + head(EBM, "type()으로 자료형을 물어봐요", NAVY)
    o2, pos, _, G = scene([{"id": "c-types-s", "lines": ["age = 25", "...", "grade_type = [1, 2, 3, 4, 5]"], "n": 1},
                     {"id": "c-type", "lines": ["print(type(age))", "print(type(pi))", "print(type(is_alive))", "print(type(user_name))", "print(type(grade_type))"], "n": 2,
                      "out": [f"<class '{t}'>" for t, _, _, _ in TYPES], "oids": [f"tc-{i}" for i in range(5)], "out_attrs": bi("rise", 1)}], toolbar=False, sel="c-type", fs=30)
    o += o2 + [selbar(28, pos["c-type"][0], pos["c-type"][2]), '</div>']
    for i, (t, k, d, c) in enumerate(TYPES):
        o += lead(2, f"tc-{i}", k, side="l", edge=640, gap=24, color=c, size=27)
    o.append(caption("1번 셀을 먼저 실행해야 해요.<br>Restart 뒤 2번만 돌리면 NameError예요.", 300, width=540, size=26, color=SUB, order=2))
    W("type-check", o, "type() 안에 변수를 넣으면 그 값의 자료형을 알려 줘요. 출력의 class 뒤 이름이 자료형이에요. int는 integer(정수), float는 실수, bool은 boolean(참과 거짓), str은 string(문자열), list는 리스트예요. 값을 보고 헷갈리면 type()으로 확인해요. 1번 셀은 화면 폭 때문에 가운데 줄을 ...로 줄였어요. 출력은 hello-uv 커널에서 같은 셀을 실제로 실행한 결과예요.")

    # ---------- part 6: shortcut tables ----------
    EB4 = "6. 단축키 모음 (Windows, Mac)"

    def key_table(rows, top=226, rid_prefix="kr"):
        o = [hairrow(96, top, 1728, 56, p(f"width:640px;flex:none;font-size:24px;font-weight:700;color:{GRAY}", "하는 일") + p(f"width:500px;flex:none;font-size:24px;font-weight:700;color:{BL}", "Windows")
                     + p(f"flex:1;font-size:24px;font-weight:700;color:{GRAY}", "Mac"), top_line=False)]
        for i, (what, where, win, mac) in enumerate(rows):
            o.append(hairrow(96, top + 56 + i * 92, 1728, 92,
                             '<div style="width:640px;flex:none;display:flex;flex-direction:row;align-items:baseline;gap:14px">' + p(f"font-size:30px;font-weight:700;color:{INK}", e(what))
                             + (p(f"font-size:22px;color:{GRAY}", e(where)) if where else "") + '</div>'
                             + f'<div style="width:500px;flex:none">{kbd(win, 26)}</div><div style="flex:1">{kbd(mac, 26)}</div>', rid=f"{rid_prefix}{i}"))
        return o

    o = [sec("keys-run")] + head(EB4, "실행하고 셀 다루는 키", NAVY)
    o += key_table([("실행하고 머물기", "", "Ctrl+Enter", "control+Enter"), ("실행하고 다음 셀로", "", "Shift+Enter", "Shift+Enter"), ("실행하고 아래에 새 셀", "", "Alt+Enter", "option+Enter"),
                    ("명령 모드로", "편집 모드에서", "Esc", "Esc"), ("편집 모드로", "명령 모드에서", "Enter", "Enter"), ("셀 위아래로 옮기기", "명령 모드에서", "Alt+↑", "option+↑"),
                    ("셀 추가, 종류 바꾸기", "명령 모드에서", "A B M Y", "A B M Y")])
    o.append(spot(1, target="kr0", pad=4, r=12))
    o.append(spot_off(2))
    o.append(caption("Mac의 실행 키는 Cmd가 아니라 control이에요.", 948, size=28, color=OR, order=2))
    W("keys-run", o, "Mac 실행 키만 조심하면 Windows와 Mac이 거의 같아요. Windows의 Ctrl은 Mac에서 보통 Cmd가 되지만, 노트북 실행 키는 예외예요. VS Code 기본 설정에서 Mac의 셀 실행은 control+Enter예요. Alt 자리는 Mac의 option 키예요. 셀을 아래로 옮길 때는 ↓를 눌러요. 단축키는 VS Code 버전이나 다른 확장 설정에 따라 바뀔 수 있어요. 안 먹으면 명령 팔레트에서 Preferences: Open Keyboard Shortcuts를 열고 notebook으로 검색해 지금 키를 확인해요.", ("keys", "단축키 모음"))

    o = [sec("keys-edit")] + head(EB4, "셀 안에서 글 고치는 키와 파일 키", NAVY)
    o += key_table([("주석 넣고 빼기", "편집 모드에서", "Ctrl+/", "Cmd+/"), ("되돌리기", "편집 모드에서", "Ctrl+Z", "Cmd+Z"), ("들여쓰기 빼기", "편집 모드에서", "Shift+Tab", "Shift+Tab"),
                    ("노트북에서 찾기", "", "Ctrl+F", "Cmd+F"), ("노트북 저장", "", "Ctrl+S", "Cmd+S"), ("명령 팔레트", "", "Ctrl+Shift+P", "Cmd+Shift+P"),
                    ("확장 화면 열기", "", "Ctrl+Shift+X", "Cmd+Shift+X")], rid_prefix="ke")
    o.append(caption("Windows의 Ctrl은 Mac에서 Cmd예요.", 948, size=28, color=SUB))
    W("keys-edit", o, "셀 안에서 코드를 고칠 때는 VS Code의 보통 편집 키를 그대로 써요. 주석 키는 줄 앞에 #을 붙였다 뗐다 해요. 여러 줄을 고르고 누르면 한 번에 바뀌어요. 노트북은 저장해야 출력까지 .ipynb 파일에 남아요. 탭 이름 옆에 동그라미가 있으면 아직 저장하지 않은 거예요. 명령 팔레트는 메뉴를 몰라도 이름으로 기능을 찾는 창이에요. 확장 화면 키는 09에서 Jupyter 확장을 설치할 때 쓴 키예요.")

    # ---------- summary ----------
    o = [f'<section id="cheatsheet" data-transition="fade" style="background:{BG};color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
         f'<h2 style="position:absolute;left:96px;top:72px;font-size:60px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>']
    CUR = "cheatsheet"
    cheat = [("Shift+Enter", "실행하고 다음 셀로", ""), ("Ctrl+Enter", "실행하고 머물기", "Mac은 control+Enter"), ("Esc", "명령 모드로", ""),
             ("Enter", "편집 모드로", ""), ("A B", "위, 아래에 셀 추가", "명령 모드에서"), ("M Y", "마크다운, 코드 셀로", "명령 모드에서")]
    o.append(f'<div{STAGGER(1, 90)} style="position:absolute;left:0;top:0;width:1920px;height:1080px">')
    for i, (k, d, n_) in enumerate(cheat):
        col, row = i % 2, i // 2
        o.append(hairrow(96 + col * 880, 210 + row * 140, 848, 140,
                         f'<div style="width:350px;flex:none">{kbd(k, 36)}</div>'
                         + '<div style="display:flex;flex-direction:column;gap:4px">' + p(f"font-size:32px;font-weight:700;color:{INK}", e(d)) + (p(f"font-size:22px;color:{GRAY}", e(n_)) if n_ else "") + '</div>',
                         top_line=row > 0))
    o.append('</div>')
    rules = ['<b>[숫자]는 실행한 순서예요.</b> ' + sub("화면 위아래 순서가 아니에요."),
             f'<b>꼬이면 <span style="color:{JP}">↻ Restart</span> 뒤 <span style="color:{GR}">▷ Run All</span></b>',
             f'<b>패키지는 터미널에서 <span style="font-family:{MONO};color:{TEAL}">uv add 패키지</span></b> ' + sub("알림의 Install 버튼은 쓰지 않아요.")]
    o.append(f'<div style="position:absolute;left:96px;top:660px;width:1728px;border-top:3px solid {INK};padding-top:26px;display:flex;flex-direction:column;gap:14px">'
             + "".join(p(f"font-size:30px;font-weight:400;line-height:1.4;color:{INK}", r) for r in rules) + '</div>')
    o.append(p(f"position:absolute;left:96px;top:880px;width:1728px;font-size:26px;color:{SUB}", "다음 11에서는 터미널에서 GitHub을 다루는 gh를 배워요. 파이썬 기초는 12부터 이 노트북에서 실습해요."))
    W("cheatsheet", o, "노트북에서 매일 쓰는 키는 이 여섯 개예요. 실행은 Shift+Enter 하나로 시작해도 충분해요. 결과가 이상하면 Restart 뒤 Run All로 위에서부터 다시 실행해요. 노트북에서 쓸 패키지도 09에서 배운 대로 터미널에서 uv add로 넣어요. VS Code 알림의 Install 버튼은 pip로 넣어서 쓰지 않아요.")

    # ---------- toc (page numbers from ORDER) ----------
    page = {sid: i + 1 for i, sid in enumerate(ORDER)}
    parts = [(BL, "노트북 화면 읽기", "커널, 버튼, 실행 번호, 코드 셀과 마크다운 셀", "screen", "kinds"),
             (BL, "셀 실행하기", "세 가지 실행 키, 실행 순서, Restart, 위쪽 버튼", "run-ctrl", "buttons"),
             (PUR, "명령 모드와 편집 모드", "Esc와 Enter, 키로만 셀 만들기, 글자 키", "modes", "cmdkeys"),
             (TEAL, "파일 실행과 비교하고 막힐 때 보기", "uv run과 비교, SyntaxError, 막힐 때 표", "compare", "trouble"),
             (NAVY, "노트북에 수업 내용 정리하기", "변수 이름 규칙, 표기법, 자료형과 type()", "md-rules", "type-check"),
             (NAVY, "단축키 모음", "Windows와 Mac 나란히", "keys-run", "keys-edit")]
    CUR = "toc"
    t = [f'<section id="toc" data-transition="fade" style="background:{BG};color:{INK};font-family:{SANS};padding:96px;display:flex;flex-direction:column">',
         f'<h2 style="position:absolute;left:96px;top:72px;font-size:60px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>']
    for i, (c, h, s, a, b) in enumerate(parts, 1):
        pg = f"{page[a]}–{page[b]}쪽" if a != b else f"{page[a]}쪽"
        t.append(hairrow(96, 196 + (i - 1) * 124, 1728, 124,
                         p(f"width:70px;flex:none;font-size:52px;font-weight:900;color:{c}", str(i))
                         + '<div style="flex:1;display:flex;flex-direction:column;gap:2px">' + p(f"font-size:34px;font-weight:700;color:{INK}", h) + p(f"font-size:25px;color:{SUB}", e(s)) + '</div>'
                         + p(f"font-size:26px;font-weight:700;color:{GRAY};white-space:nowrap", pg), top_line=i > 1))
    t.append(p(f"position:absolute;left:96px;top:960px;width:1728px;font-size:26px;color:{SUB}",
               f"{page['why']}–{page['first']}쪽은 노트북이 왜 필요한지와 첫 실행, {page['cheatsheet']}쪽은 한 장 요약이에요."))
    with open(os.path.join(OUT, "toc.html"), "w") as f:
        f.write("\n".join(t) + f"\n<aside>{e('09에서 만든 hello-uv 폴더와 notebook.ipynb를 그대로 써요. 들어가기에서 노트북이 왜 필요한지 보고 첫 셀을 실행해요. 1파트는 화면을 읽는 법, 2파트부터 직접 키를 눌러 봐요. 5파트는 수업에서 배운 이름 규칙과 자료형을 노트북에 정리해요. 6파트 표는 수업 중에 옆에 띄워 두고 봐도 돼요.')}</aside>\n</section>\n")

    deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-10-30T05:00:00Z"}, "lists": "css", "title": "VS Code에서 Jupyter 노트북 쓰기", "order": ORDER,
            "sections": SECTIONS,
            "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                      "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
            "designSystems": []}
    with open(os.path.join(OUT, "deck.json"), "w") as f:
        json.dump(deck, f, ensure_ascii=False, indent=2)


# pass 1: slides without leader lines; measure every box; pass 2: slides with lines aimed at the measured boxes
build()
for f_ in os.listdir(OUT):
    if f_.endswith(".html") and f_[:-5] not in ORDER:
        os.remove(os.path.join(OUT, f_))
try:
    subprocess.run(["node", os.path.join(HERE, "measure.js"), OUT, RECTS_FILE], check=True)
except (OSError, subprocess.CalledProcessError) as err:
    print("measure.js failed, using the saved tools/rects.json:", err)
if os.path.exists(RECTS_FILE):
    RECTS = json.load(open(RECTS_FILE))
    build()
print(len(ORDER), "slides")
