"""Generates every slide of the Python basics 5 deck (16, sets) and slides/deck.json.

Story: keeps writing in basics.ipynb from chapters 12-15. Starts from the idea (a pouch that keeps one of each,
with no order), makes and changes sets, draws |, & and - as Venn diagrams with numbers, then uses sets
on real data: kinds of menus sold, two classes, and orders that are not on the menu from chapter 15.
Every cell and output comes from tools/demo.sh (tools/run_nb.py runs the cells with the project kernel).
Usage: python3 tools/gen.py slides
"""

import html, json, os, re, sys

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
INK, SUB, LINE, CARD = "#1D2330", "#4A5262", "#E1DED6", "#FFFFFF"
BL, GR, OR, PUR, RED, NAVY, TEAL, GRAY = "#2459C9", "#1F8A4C", "#B26A00", "#5A3BB8", "#A33131", "#1E3F8F", "#0F7C86", "#6A7180"
JP = "#B8560F"          # Jupyter, same as chapters 09 and 10
SEL = "#2F7DE1"         # selected cell bar, like VS Code's focus color
WIN, MAC = BL, "#3D4250"


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


def caption(text, top=944):
    return p(f"position:absolute;left:96px;top:{top}px;width:1728px;font-size:34px;font-weight:700;line-height:1.4;color:{INK}", text, ' id="caption" data-build-in="rise"')


def num(i, color, size=56, extra=""):
    return p(f"width:{size + 16}px;height:{size + 16}px;flex:none;border-radius:50%;background:{color};color:#FFFFFF;font-size:{size * 0.6:.0f}px;font-weight:900;line-height:{size + 16}px;text-align:center;{extra}", str(i))


def kbd(text, size=30, color=INK):
    """Key caps. Keys joined with + are pressed together; keys split by spaces are separate keys."""
    if " " in text:
        return '<div style="display:flex;flex-direction:row;align-items:center;gap:14px">' + "".join(kbd(t, size, color) for t in text.split()) + '</div>'
    caps = []
    for k in text.split("+"):
        caps.append(p(f"font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.2;white-space:nowrap;color:{color};background:#FFFFFF;border:2px solid #C9CED8;border-bottom-width:5px;border-radius:10px;padding:6px 14px", e(k)))
    plus = p(f"font-size:{size * 0.8:.0f}px;font-weight:700;color:{GRAY}", "+")
    return f'<div style="display:flex;flex-direction:row;align-items:center;gap:8px">' + plus.join(caps) + '</div>'


def key_pair(win, mac, size=30):
    """Windows and Mac keys side by side, labelled."""
    lab = lambda t, c: p(f"width:110px;flex:none;font-size:22px;font-weight:700;color:{c}", t)
    return ('<div style="display:flex;flex-direction:column;gap:12px">'
            + '<div style="display:flex;flex-direction:row;align-items:center;gap:12px">' + lab("Windows", WIN) + kbd(win, size) + '</div>'
            + '<div style="display:flex;flex-direction:row;align-items:center;gap:12px">' + lab("Mac", MAC) + kbd(mac, size) + '</div></div>')


# ---------- notebook mock (each cell keeps its id across scenes) ----------
LH = 38          # code line height (26px * 1.45)


def cell_h(c):
    h = 22 + LH * len(c.get("lines", [""]))
    if c.get("kind") == "mdr":
        h = 20 + sum(56 if l.startswith("# ") else LH for l in c["lines"])
    if c.get("out"):
        h += 10 + LH * len(c["out"])
    return h


def WIDE(t):
    """Draws each Hangul syllable two monospace columns wide, like a terminal."""
    return re.sub(r"([\uac00-\ud7a3])", r'<span style="display:inline-block;width:1.2em;text-align:center">\1</span>', t)


def cell(c, left, top, w, sel=None, mode="cmd", pre="", attrs=""):
    """c: dict(id, kind code|md|mdr, lines, n, out, err). sel: id of the selected cell."""
    kind, lines, n = c.get("kind", "code"), c.get("lines", [""]), c.get("n")
    chosen = sel == c["id"]
    edit = chosen and mode == "edit"
    o = [f'<div id="{pre}{c["id"]}"{attrs or c.get("attrs", "")} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;display:flex;flex-direction:column;gap:10px">']
    bar = f'<div style="width:7px;flex:none;border-radius:4px;background:{SEL if chosen else "transparent"}"></div>'
    gutter = p(f"width:58px;flex:none;font-family:{MONO};font-size:20px;color:{GRAY};text-align:right;padding-top:12px", "" if kind != "code" else (f"[{n}]" if n else "[ ]"))
    if kind == "mdr":
        body = "".join(p(f"font-size:{40 if l.startswith('# ') else 26}px;font-weight:{700 if l.startswith('# ') else 400};line-height:1.4;color:{INK}",
                         e(l[2:]) if l.startswith("# ") else ("• " + e(l[2:]) if l.startswith("- ") else e(l))) for l in lines)
        box = f'<div style="flex:1;padding:6px 18px;display:flex;flex-direction:column">{body}</div>'
    else:
        bd = f"3px solid {SEL}" if edit else f"2px solid {LINE}"
        bg = "#FFFFFF" if kind == "code" else "#FAF8F3"
        txt = "".join(p(f"font-family:{MONO};font-size:26px;line-height:1.45;white-space:pre;color:{INK}", (e(l) if l else "&#160;") + ('<span style="color:' + SEL + ';font-weight:700">|</span>' if edit and i == len(lines) - 1 else ""))
                      for i, l in enumerate(lines))
        tag = p(f"position:absolute;right:14px;bottom:8px;font-size:18px;color:{GRAY}", "Python" if kind == "code" else "Markdown")
        box = f'<div style="flex:1;position:relative;background:{bg};border:{bd};border-radius:10px;padding:8px 18px 8px;display:flex;flex-direction:column">{txt}{tag}</div>'
    o.append(f'<div style="display:flex;flex-direction:row;gap:10px;align-items:stretch">{bar}{gutter}{box}</div>')
    if c.get("out"):
        col = RED if c.get("err") else INK
        wide = WIDE if c.get("wide") else (lambda t: t)
        o.append(''.join(p(f"margin-left:85px;padding:0 20px;font-family:{MONO};font-size:26px;line-height:1.45;white-space:pre;color:{col}", wide(e(l))) for l in c["out"]))
    o.append('</div>')
    return o


def notebook(cells, left, top, w, sel=None, mode="cmd", pre="", bar=True, gap=22, file="notebook.ipynb", toolbar=True):
    o = []
    y = top
    if bar:
        tools = ["+ Code", "+ Markdown", "▷ Run All", "↻ Restart", "Clear All Outputs", "Variables"] if toolbar else []
        o.append(f'<div id="{pre}nb-bar" style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:64px;background:#ECEAE3;border-radius:14px;display:flex;flex-direction:row;align-items:center;padding:0 20px;gap:18px">'
                 + p(f"font-family:{MONO};font-size:22px;font-weight:700;color:{INK};white-space:nowrap", e(file))
                 + "".join(p(f"font-size:19px;color:{SUB};white-space:nowrap", e(t)) for t in tools) + '<div style="flex:1"></div>'
                 + p(f"font-size:19px;font-weight:700;color:{GR};background:#E6F4EC;border-radius:8px;padding:4px 12px;white-space:nowrap", ".venv (Python 3.14.6)") + '</div>')
        y += 88
    for c in cells:
        o += cell(c, left, y, w, sel, mode, pre)
        y += cell_h(c) + gap
    return o




def C(base, **kw):
    d = dict(base)
    d.update(kw)
    return d


TRUE_C, FALSE_C = GR, RED


def tf(v, size=26):
    """True / False chip."""
    c = TRUE_C if v == "True" else FALSE_C
    bg = "#E6F4EC" if v == "True" else "#F8E6E6"
    return p(f"display:inline-block;font-family:{MONO};font-size:{size}px;font-weight:700;color:{c};background:{bg};border-radius:10px;padding:2px 14px;white-space:nowrap", v)


def mono(text, size=28, color=INK, bg="#F1F0EC", extra=""):
    return p(f"font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.4;color:{color};background:{bg};border-radius:10px;padding:4px 16px;white-space:pre;{extra}", e(text))


def card(left, top, w, h, inner, color=None, attrs="", extra="", bg=CARD):
    bt = f"border-top:10px solid {color};" if color else ""
    return (f'<div{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:{bg};border:2px solid {LINE};{bt}border-radius:20px;'
            f'padding:24px 30px;display:flex;flex-direction:column;gap:14px;{extra}">' + inner + '</div>')


def var_box(sid, name, value, left, top, color=BL, w=420, attrs=""):
    """A variable drawn as a box with its name on top."""
    return (f'<div id="{sid}"{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:230px;background:{CARD};border:3px solid {color};border-radius:22px;display:flex;flex-direction:column;overflow:hidden">'
            + p(f"height:70px;flex:none;background:{color};color:#FFFFFF;font-family:{MONO};font-size:34px;font-weight:700;line-height:70px;padding:0 26px", e(name))
            + f'<div style="flex:1;display:flex;align-items:center;justify-content:center">' + p(f"font-family:{MONO};font-size:72px;font-weight:700;color:{INK}", e(value)) + '</div></div>')


def chain(rows, left, top, w, start=1, color=PUR, gap=74):
    """Evaluation steps shown one per click: (expression, result chip or None, label)."""
    o = []
    for i, (expr, res, lbl) in enumerate(rows):
        y = top + i * gap
        o.append(f'<div data-build-in="rise order {start + i}" style="position:absolute;left:{left}px;top:{y}px;width:{w}px;height:{gap - 12}px;display:flex;flex-direction:row;align-items:center;gap:18px">'
                 + (p(f"width:110px;flex:none;font-size:22px;font-weight:700;color:{color}", e(lbl)) if lbl is not None else "")
                 + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{INK};white-space:pre", expr)
                 + (f'<x-shape kind="arrow-right" style="width:44px;height:26px;flex:none;background:#C9CED8"></x-shape>' + tf(res) if res else "") + '</div>')
    return o


NB = "basics.ipynb"
K1, K1BG = "#1E5FA8", "#E5EEF8"
K2, K2BG = "#A0620A", "#F7EEDD"
K3, K3BG = TEAL, "#E2F2F3"
K4, K4BG = "#A23B72", "#F6E7EF"
T6, T6BG = K4, K4BG
EB1 = "1. 집합이 뭔가요"
EB2 = "2. 바꾸고 확인하기"
EB3 = "3. 집합 연산"
EB4 = "4. 실습"
def slots(items, left, top, w=170, h=96, hi=(), top_lbl=True, attrs="", fs=34, color=None, bg=None):
    """List items in a row of boxes with index numbers above."""
    c, b = color or T6, bg or T6BG
    o = [f'<div{attrs} style="position:absolute;left:{left}px;top:{top}px;display:flex;flex-direction:row;gap:8px">']
    for i, it in enumerate(items):
        on = i in hi
        o.append('<div style="display:flex;flex-direction:column;align-items:center;gap:8px">'
                 + (p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{c}", str(i)) if top_lbl else "")
                 + p(f"width:{w}px;height:{h}px;border-radius:14px;border:3px solid {c if on else LINE};background:{b if on else CARD};font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:{h - 6}px;text-align:center;color:{INK};white-space:pre", e(it)) + '</div>')
    o.append('</div>')
    return "".join(o)


def grid(rows, left=0, top=0, cw=150, ch=84, hi=(), attrs="", fs=32, lbl=24, cols=None, color=T6, inline=False, bg=None):
    """A list of lists drawn as a table: row numbers on the left, column numbers on top.
    hi: set of (row, col) cells to highlight. cols: optional names under the column numbers."""
    pos = "" if inline else f"position:absolute;left:{left}px;top:{top}px;"
    rw = lbl * 2 + 12
    o = [f'<div{attrs} style="{pos}display:flex;flex-direction:column;gap:6px">']
    head_ = f'<div style="width:{rw}px;flex:none"></div>' + "".join(
        p(f"width:{cw}px;flex:none;text-align:center;font-family:{MONO};font-size:{lbl}px;font-weight:700;color:{color};line-height:1.2", str(j) + (f'<br><span style="font-family:{SANS};font-size:{lbl - 4}px;color:{GRAY}">{e(cols[j])}</span>' if cols else ""))
        for j in range(len(rows[0])))
    o.append(f'<div style="display:flex;flex-direction:row;gap:6px">{head_}</div>')
    for i, r in enumerate(rows):
        cells = "".join(p(f"width:{cw}px;height:{ch}px;flex:none;border-radius:10px;border:3px solid {color if (i, j) in hi else LINE};background:{(bg or T6BG) if (i, j) in hi else CARD};"
                          f"font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:{ch - 6}px;text-align:center;color:{INK};white-space:pre", e(str(v))) for j, v in enumerate(r))
        o.append(f'<div style="display:flex;flex-direction:row;gap:6px;align-items:center">' + p(f"width:{rw}px;flex:none;text-align:right;padding-right:8px;font-family:{MONO};font-size:{lbl}px;font-weight:700;color:{color}", str(i)) + cells + '</div>')
    o.append('</div>')
    return "".join(o)


def row_card(left, top, w, h, code, res, desc, start, color, bg, code_w=380):
    """One line: code, its result, and what it means."""
    return (f'<div data-build-in="rise order {start}" style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:{CARD};border:2px solid {LINE};border-radius:16px;padding:0 22px;display:flex;flex-direction:row;align-items:center;gap:18px">'
            + f'<div style="width:{code_w}px;flex:none">' + mono(code, 24, color, bg, "display:inline-block") + '</div>'
            + (tf(res, 24) if res in ("True", "False") else p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{INK};white-space:pre", e(res)))
            + p(f"flex:1;font-size:21px;color:{SUB}", e(desc)) + '</div>')




def lockers(pairs, left=0, top=0, w=200, h=170, color=K1, bg=K1BG, hi=(), attrs="", fs=34, kfs=24, gap=12, inline=False, mode=None):
    """A dictionary drawn as a row of lockers: the key is written on the door band, the value sits inside.
    mode "key" or "val" dims the other half (for keys() and values())."""
    pos = "" if inline else f"position:absolute;left:{left}px;top:{top}px;"
    o = [f'<div{attrs} style="{pos}display:flex;flex-direction:row;gap:{gap}px">']
    for i, (k, v) in enumerate(pairs):
        on = i in hi or mode is not None
        kc = color if (on and mode != "val") else "#ECEAE3"
        kt = "#FFFFFF" if (on and mode != "val") else (GRAY if mode == "val" else INK)
        vt = "#B4B9C3" if mode == "key" else INK
        o.append(f'<div style="width:{w}px;height:{h}px;flex:none;border-radius:14px;border:3px solid {color if on else "#C9CED8"};background:{bg if (on and mode != "key") else CARD};display:flex;flex-direction:column;overflow:hidden">'
                 + p(f"height:{kfs + 26}px;flex:none;background:{kc};color:{kt};font-family:{MONO};font-size:{kfs}px;font-weight:700;line-height:{kfs + 26}px;text-align:center;white-space:pre", e(k))
                 + '<div style="flex:1;display:flex;align-items:center;justify-content:center;position:relative">'
                 + p(f"font-family:{MONO};font-size:{fs}px;font-weight:700;color:{vt};white-space:pre", e(v))
                 + f'<div style="position:absolute;right:10px;top:50%;width:7px;height:34px;margin-top:-17px;border-radius:4px;background:#D5D8DE"></div></div></div>')
    o.append('</div>')
    return "".join(o)


def label(text, left, top, color, attrs="", w=700, size=26):
    return p(f"position:absolute;left:{left}px;top:{top}px;width:{w}px;font-family:{MONO if text.isascii() else SANS};font-size:{size}px;font-weight:700;color:{color}", e(text), attrs)




# ---------- set pictures ----------
def chip(text, color=K1, bg=K1BG, fs=30, extra=""):
    return p(f"font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:1.2;color:{INK};background:{bg};border:3px solid {color};border-radius:999px;padding:6px 22px;white-space:pre;{extra}", e(text))


SCATTER = [(0.26, 0.34), (0.68, 0.30), (0.44, 0.66), (0.78, 0.68), (0.20, 0.72), (0.52, 0.42), (0.36, 0.20), (0.72, 0.50)]


def bag(items, left, top, w, h, color=K1, bg=K1BG, attrs="", fs=30, name=None, pos=None, sid=None):
    """A set drawn as a pouch with a tie on top. Items float inside with no slot numbers (no order)."""
    pos = pos or SCATTER
    ida = f' id="{sid}"' if sid else ""
    o = [f'<div{ida}{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px">',
         f'<div style="position:absolute;left:{w / 2 - 70:.0f}px;top:0;width:140px;height:34px;border-radius:12px 12px 4px 4px;background:{color}"></div>',
         f'<div style="position:absolute;left:0;top:26px;width:{w}px;height:{h - 26}px;border:4px solid {color};background:{CARD};border-radius:70px 70px {min(w, h) * 0.4:.0f}px {min(w, h) * 0.4:.0f}px"></div>']
    if name:
        o.append(p(f"position:absolute;left:{w / 2 - 70:.0f}px;top:0;width:140px;height:34px;font-family:{MONO};font-size:22px;font-weight:700;line-height:34px;text-align:center;color:#FFFFFF", e(name)))
    for i, it in enumerate(items):
        x, y = pos[i % len(pos)]
        o.append(f'<div style="position:absolute;left:{x * w:.0f}px;top:{26 + y * (h - 26):.0f}px;transform:translate(-50%,-50%)">' + chip(it, color, bg, fs) + '</div>')
    if not items:
        o.append(p(f"position:absolute;left:0;top:{h / 2:.0f}px;width:{w}px;text-align:center;font-size:26px;color:{GRAY}", "비어 있어요"))
    o.append('</div>')
    return "".join(o)


VA, VB = K1, K2
_vn = [0]


def venn(left, top, a_only, both, b_only, la="a", lb="b", w=760, h=470, hi=(), sid=None, attrs="", fs=28, regions=None, dim=False):
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
        o.append(f'<svg data-build-in="fade order {order}" style="position:absolute;left:0;top:0;width:{w}px;height:{h}px;opacity:0.42" viewBox="0 0 {w} {h}">{body}</svg>')
    o.append(f'<svg style="position:absolute;left:0;top:0;width:{w}px;height:{h}px" viewBox="0 0 {w} {h}">'
             + circ(ca, f'fill="none" stroke="{VA}" stroke-width="5"') + circ(cb, f'fill="none" stroke="{VB}" stroke-width="5"') + '</svg>')
    o.append(p(f"position:absolute;left:{ca - 200:.0f}px;top:{cy - r - 52:.0f}px;width:400px;text-align:center;font-family:{MONO};font-size:30px;font-weight:700;color:{VA}", e(la)))
    o.append(p(f"position:absolute;left:{cb - 200:.0f}px;top:{cy - r - 52:.0f}px;width:400px;text-align:center;font-family:{MONO};font-size:30px;font-weight:700;color:{VB}", e(lb)))
    for cx, items in [(w / 2 - r, a_only), (w / 2, both), (w / 2 + r, b_only)]:
        n = len(items)
        for j, it in enumerate(items):
            y = cy + (j - (n - 1) / 2) * (fs * 2.1)
            o.append(f'<p style="position:absolute;left:{cx - 90:.0f}px;top:{y - fs * 0.7:.0f}px;width:180px;text-align:center;font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:1.4;color:{INK}">{e(it)}</p>')
    if regions:
        for cx, (t, order) in zip([w / 2 - r * 1.1, w / 2, w / 2 + r * 1.1], regions):
            at = f' data-build-in="rise order {order}"' if order else ""
            o.append(p(f"position:absolute;left:{cx - 120:.0f}px;top:{h + 8}px;width:240px;text-align:center;font-size:24px;font-weight:700;color:{SUB}", e(t), at))
    o.append('</div>')
    return "".join(o)


def op_card(left, top, w, h, code, method, result, desc, color, bg, attrs=""):
    """An operator, its method name and the real result."""
    return card(left, top, w, h,
                '<div style="display:flex;flex-direction:row;align-items:center;gap:18px">' + mono(code, 34, color, bg)
                + p(f"font-size:24px;color:{GRAY}", "또는") + mono(method, 26, color, bg) + '</div>'
                + '<div style="display:flex;flex-direction:row;align-items:center;gap:16px">' + f'<x-shape kind="arrow-right" style="width:44px;height:26px;flex:none;background:#C9CED8"></x-shape>'
                + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:{INK}", e(result)) + '</div>'
                + p(f"font-size:26px;line-height:1.45;color:{INK}", desc), color, attrs)


def warn(left, top, w, h, title, body, attrs="", color=RED):
    return card(left, top, w, h, '<div style="display:flex;flex-direction:row;align-items:center;gap:14px">' + f'<x-icon name="Warning" style="width:40px;height:40px;color:{color}"></x-icon>'
                + p(f"font-size:28px;font-weight:700;color:{INK}", title) + '</div>' + p(f"font-size:24px;line-height:1.5;color:{INK}", body), color, attrs)


def note_card(left, top, w, h, title, body, color=None, attrs="", extra=""):
    return card(left, top, w, h, p(f"font-size:28px;font-weight:700;color:{INK}", title) + p(f"font-size:24px;line-height:1.5;color:{INK}", body), color, attrs, extra)


def ref_box(left, top, w, h, lines, out, attrs="", title="참고 · 원래는 이렇게", fs=24):
    """Longer code that the shortcut replaces. It uses if, which students have not learned yet, so it is read-only."""
    code = "".join(p(f"font-family:{MONO};font-size:{fs}px;line-height:1.4;white-space:pre;color:{INK}", e(l) if l else "&#160;") for l in lines)
    res = "".join(p(f"font-family:{MONO};font-size:{fs}px;line-height:1.4;white-space:pre;color:{SUB}", e(l)) for l in out)
    return (f'<div{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:#FAF8F3;border:3px dashed #B4B9C3;border-radius:20px;padding:20px 28px;display:flex;flex-direction:column;gap:12px">'
            + '<div style="display:flex;flex-direction:row;align-items:center;gap:14px">' + p(f"font-size:24px;font-weight:700;color:#FFFFFF;background:{GRAY};border-radius:8px;padding:2px 12px", e(title)) + '</div>'
            + f'<div style="display:flex;flex-direction:column">{code}</div>' + f'<div style="display:flex;flex-direction:column;border-top:2px solid {LINE};padding-top:8px">{res}</div>'
            + '<div style="flex:1"></div>' + p(f"font-size:22px;color:{GRAY}", "if는 다음에 배워요. 따라 치지 말고 읽기만 해요.") + '</div>')


MENUS = 'menus = {"coffee", "latte", "cake"}'
REAL = " 출력은 실제로 실행한 결과예요."

# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#F2B27A;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
       '<h1 style="font-size:92px;font-weight:900;line-height:1.1;color:#F6F5F1">파이썬 기초 5<br>집합</h1>',
       '<p style="font-size:40px;line-height:1.4;color:#BFC6D4">중복 없이 모으고<br>겹치는 것 찾기</p>']
cov.append(f'<div style="position:absolute;left:940px;top:300px;width:860px;height:480px;background:#252B36;border-radius:24px;padding:44px 48px;display:flex;flex-direction:column;justify-content:center;gap:34px">')
for code, out_, c in [('set([3, 1, 3, 2, 1])', '{1, 2, 3}', '#9DBDEB'), ('"tea" in menus', 'False', '#E3B877'), ('a & b', '{3, 4}', '#8FD8DE'), ('a - b', '{1, 2}', '#8FD8DE')]:
    cov.append('<div style="display:flex;flex-direction:row;align-items:center;gap:28px">'
               + p(f"width:450px;flex:none;font-family:{MONO};font-size:36px;font-weight:700;color:{c};white-space:pre", e(code))
               + f'<x-shape kind="arrow-right" style="width:50px;height:30px;background:#5A6172"></x-shape>'
               + p(f"font-family:{MONO};font-size:36px;font-weight:700;color:#E6E9EF;white-space:nowrap", e(out_)) + '</div>')
cov.append('</div>')
W("cover", cov, "13에서 리스트와 튜플, 15에서 딕셔너리를 배웠어요. 이번 챕터는 같은 값을 하나만 담는 집합이에요. 1파트에서 집합이 무엇인지 그림으로 잡고, 2파트에서 넣고 빼고 확인해요. 3파트는 합집합, 교집합, 차집합을 원 두 개로 그려 보고, 4파트에서 주문 목록과 수강생 명단, 15의 메뉴판에 써 봐요. 모든 예제는 12~15에서 쓰던 노트북 셀에 이어서 적고 실행해요.", ("intro", "들어가기"))

ORDER.append("toc")   # written last, after page numbers are known

# ---------- ready ----------
o = [sec("ready")] + head("들어가기", "15에서 이어서 해요", JP)
done = [("hello-uv 노트북, 커널 .venv", "09 · 25–27쪽"), ("리스트, 튜플, for, sorted, count", "13 · 2파트"), ("in과 not in", "14"), ("딕셔너리, KeyError, sorted(menu)", "15")]
for i, (a_, b_) in enumerate(done):
    y = 210 + i * 130
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:96px;top:{y}px;width:820px;height:112px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:0 28px;display:flex;flex-direction:row;gap:22px;align-items:center">'
             + f'<x-icon name="CheckCircle" style="width:48px;height:48px;color:{GR}"></x-icon>'
             + p(f"flex:1;font-size:30px;font-weight:700;color:{INK}", e(a_))
             + p(f"font-size:24px;font-weight:700;color:{GRAY};white-space:nowrap", e(b_)) + '</div>')
o.append(p(f"position:absolute;left:96px;top:750px;width:820px;font-size:26px;line-height:1.5;color:{SUB}", "기억이 안 나면 그 쪽을 먼저 다시 봐요.", ' data-build-in="fade order 4"'))
o.append(f'<div data-build-in="rise order 5" style="position:absolute;left:1000px;top:210px;width:824px;height:560px;background:{CARD};border:2px solid {LINE};border-top:10px solid {JP};border-radius:20px;padding:32px 40px;display:flex;flex-direction:column;gap:30px">'
         + p(f"font-size:32px;font-weight:700;color:{INK}", "노트북 다시 열기")
         + '<div style="display:flex;flex-direction:row;gap:18px;align-items:center">' + num(1, JP, 36) + p(f"font-size:28px;color:{INK}", "VS Code로 hello-uv 폴더 열기") + '</div>'
         + '<div style="display:flex;flex-direction:row;gap:18px;align-items:center">' + num(2, JP, 36) + p(f"font-size:28px;color:{INK}", "탐색기에서") + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{JP}", NB) + p(f"font-size:28px;color:{INK}", "열기") + '</div>'
         + '<div style="display:flex;flex-direction:row;gap:18px;align-items:center">' + num(3, JP, 36) + p(f"font-size:28px;color:{INK}", "오른쪽 위 커널이 .venv인지 보기") + '</div>'
         + '<div style="display:flex;flex-direction:row;gap:18px;align-items:center">' + num(4, JP, 36) + p(f"font-size:28px;color:{INK}", "셀에 적고") + kbd("Shift+Enter", 26) + p(f"font-size:28px;color:{INK}", "로 실행") + '</div></div>')
o.append(caption("이번 챕터의 코드도 모두 노트북 셀에 적어요.", 880))
W("ready", o, "09에서 만든 hello-uv 폴더를 VS Code로 열고, 12~15에서 쓰던 basics.ipynb를 다시 열어요. 13의 리스트, 튜플, for, sorted, count와 14의 in, 15의 딕셔너리를 그대로 써요. 슬라이드의 출력은 tools/demo.sh가 hello-uv 커널에서 같은 셀을 실제로 실행한 결과예요. 셀 번호는 파트마다 [1]부터 다시 셌어요.")

# ---------- part 1: what is a set ----------
o = [sec("s-why")] + head(EB1, "같은 값은 한 번만 담는 주머니예요", K1)
o += cell({"id": "c-w", "lines": ["nums = [3, 1, 3, 2, 1]", "print(nums)", "print(set(nums))"], "n": 1, "out": ["[3, 1, 3, 2, 1]", "{1, 2, 3}"]}, 96, 200, 860, sel="c-w")
o.append(label("리스트 · 넣은 그대로, 칸마다 번호", 1010, 200, GRAY, ' data-build-in="fade order 1"', 814, 24))
o.append(slots(["3", "1", "3", "2", "1"], 1010, 244, 150, 90, attrs=' data-build-in="rise order 1"', color=GRAY, bg="#EEEFF2"))
o.append(f'<x-shape data-build-in="fade order 2" kind="arrow-right" style="position:absolute;left:1360px;top:420px;width:60px;height:36px;transform:rotate(90deg);background:#C9CED8"></x-shape>')
o.append(label("집합 · 같은 값은 하나만, 번호 없음", 1010, 480, K1, ' data-build-in="fade order 2"', 814, 24))
o.append(bag(["3", "1", "2"], 1110, 520, 560, 340, attrs=' data-build-in="rise order 2"', fs=40, name="set"))
o.append(note_card(96, 470, 860, 190, "중복이 없어요", "3과 1을 두 번 넣어도 하나씩만 남아요. 그래서 개수를 세면 3이에요.", K1, ' data-build-in="rise order 3"'))
o.append(note_card(96, 680, 860, 190, "순서가 없어요", "주머니에 섞어 담아서 0번, 1번 같은 칸 번호가 없어요.", K1, ' data-build-in="rise order 4"'))
o.append(caption("집합(set)은 수학 시간의 그 집합이에요.", 920))
W("s-why", o, "리스트는 넣은 값을 그대로, 넣은 순서대로 칸에 담아요. 같은 값을 두 번 넣으면 두 칸을 차지해요. 집합은 주머니라고 생각해요. 같은 값은 하나만 들어가고, 칸 번호 없이 섞여 있어요. set(nums)로 리스트를 집합으로 바꾸면 3과 1이 하나씩만 남아 {1, 2, 3}이 돼요. 이 챕터는 이 주머니 그림 하나로 끝까지 가요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("what", "집합이 뭔가요"))

o = [sec("s-four")] + head(EB1, "괄호와 모양으로 네 가지를 구분해요", K1)
cols = [("리스트", "[1, 2]", "list", GRAY, ["있어요", "돼요", "[번호]", "돼요"]),
        ("튜플", "(1, 2)", "tuple", GRAY, ["있어요", "돼요", "[번호]", "안 돼요"]),
        ("딕셔너리", '{"a": 1}', "dict", GRAY, ["넣은 순서", "키는 안 돼요", "[키]", "돼요"]),
        ("집합", "{1, 2}", "set", K1, ["없어요", "안 돼요", "못 꺼내요", "돼요"])]
rows = ["순서", "중복", "꺼내기", "바꾸기"]
for i, (nm, lit, ty, c, vals) in enumerate(cols):
    on = c == K1
    x = 96 + i * 438
    inner = ('<div style="display:flex;flex-direction:row;align-items:baseline;gap:14px">' + p(f"font-size:32px;font-weight:700;color:{INK}", nm) + p(f"font-family:{MONO};font-size:22px;color:{GRAY}", ty) + '</div>'
             + mono(lit, 34, c if on else INK, K1BG if on else "#F1F0EC", "align-self:flex-start"))
    for rn, v in zip(rows, vals):
        inner += ('<div style="display:flex;flex-direction:row;align-items:center;gap:16px;border-top:2px solid ' + LINE + ';padding-top:20px">'
                  + p(f"width:100px;flex:none;font-size:24px;font-weight:700;color:{GRAY}", rn)
                  + p(f"font-size:30px;font-weight:700;color:{K1 if on else INK};white-space:nowrap", v) + '</div>')
    o.append(card(x, 196, 414, 660, inner, c, f' data-build-in="rise order {1 if i < 2 else i}"', "gap:34px", K1BG if on else CARD))
o.append(caption("중괄호 안에 키: 값이 있으면 딕셔너리, 값만 있으면 집합이에요.", 920))
W("s-four", o, "지금까지 배운 담는 그릇 네 가지를 나란히 놓아요. 리스트와 튜플은 순서가 있어서 번호로 꺼내고, 튜플은 만든 뒤 바꿀 수 없어요. 딕셔너리는 15에서 본 것처럼 넣은 순서를 지키고 키로 꺼내요. 집합은 딕셔너리와 같은 중괄호를 쓰지만 키: 값이 아니라 값만 적어요. 순서가 없고 중복이 없어서 번호로도, 키로도 꺼낼 수 없어요. 그 대신 값을 넣고 빼는 것은 돼요. 중괄호로 만든 집합의 type은 다음 장에서 확인해요.")

o = [sec("s-make")] + head(EB1, "중괄호 안에 값만 쉼표로 이어요", K1)
o += cell({"id": "c-m", "lines": ["nums = {3, 1, 2, 3}", "print(nums)", "print(type(nums))", "print(len(nums))"], "n": 2, "out": ["{1, 2, 3}", "<class 'set'>", "3"]}, 96, 200, 860, sel="c-m")
mk = [("{3, 1, 2, 3}", "{1, 2, 3}", "겹친 3은 하나만"), ("type(nums)", "<class 'set'>", "set은 집합"), ("len(nums)", "3", "값의 개수")]
for i, (k, r_, d) in enumerate(mk):
    o.append(row_card(1010, 200 + i * 116, 814, 100, k, r_, d, i + 1, K1, K1BG, 250))
o.append(bag(["3", "1", "2"], 1110, 560, 560, 320, attrs=' data-build-in="rise order 4"', fs=40, name="nums"))
anat = '<div style="display:flex;flex-direction:row;align-items:flex-end;gap:14px">'
for tok, lb in [("{", "여는 괄호"), ("3, 1, 2", "값만 쉼표로"), ("}", "닫는 괄호")]:
    anat += '<div style="display:flex;flex-direction:column;align-items:center;gap:8px">' + mono(tok, 36, K1, K1BG) + p(f"font-size:22px;font-weight:700;color:{SUB}", lb) + '</div>'
anat += '</div>'
o.append(card(96, 600, 860, 270, p(f"font-size:28px;font-weight:700;color:{INK}", "키: 값 없이 값만 적어요") + anat, None, ' data-build-in="rise order 1"'))
o.append(caption("처음부터 같은 값을 두 번 적어도 오류 없이 하나만 남아요.", 920))
W("s-make", o, "집합은 중괄호 안에 값만 쉼표로 이어서 만들어요. 15의 딕셔너리처럼 키: 값이 아니에요. 3을 두 번 적었지만 출력에는 하나만 남아요. 오류도 나지 않아요. type은 set이라고 알려 줘요. len은 값의 개수라 3이에요. 숫자 집합은 보통 작은 수부터 찍혀 나오지만, 그것도 정렬해 준다는 약속은 아니에요." + REAL)

o = [sec("s-order")] + head(EB1, "집합은 순서를 기억하지 않아요", K1)
o.append(label("처음 실행", 96, 200, K1, "", 860, 24))
o += cell({"id": "c-o1", "lines": [MENUS, "print(menus)", "print(sorted(menus))"], "n": 3, "out": ["{'latte', 'cake', 'coffee'}", "['cake', 'coffee', 'latte']"]}, 96, 244, 860, sel="c-o1")
o.append(label("Restart 하고 이 셀만 다시 실행", 984, 200, K1, ' data-build-in="fade order 1"', 840, 24))
o += cell({"id": "c-o2", "lines": [MENUS, "print(menus)", "print(sorted(menus))"], "n": 1, "out": ["{'coffee', 'cake', 'latte'}", "['cake', 'coffee', 'latte']"]}, 984, 244, 840, attrs=' data-build-in="rise order 1"')
o.append(note_card(96, 540, 860, 280, "print(menus) 순서는 바뀔 수 있어요",
                   "적은 순서는 coffee, latte, cake인데 다르게 나왔어요. 커널을 다시 켜면 또 달라질 수 있어요. 내 화면이 슬라이드와 달라도 괜찮아요.", K1, ' data-build-in="rise order 2"'))
o.append(note_card(984, 540, 840, 280, "순서가 필요하면 sorted()",
                   "13에서 배운 sorted()에 넣으면 abc 순서 리스트가 나와요. 몇 번을 실행해도 ['cake', 'coffee', 'latte']예요.", GR, ' data-build-in="rise order 3"'))
o.append(caption("집합에는 순서가 없으니 sorted()로 줄 세워서 봐요.", 920))
W("s-order", o, "글자를 담은 집합을 print로 찍으면 적은 순서와 다르게 나와요. 커널을 다시 시작하고 같은 셀을 실행하면 또 다른 순서가 나올 수 있어요. 파이썬이 집합 안에서 값을 빨리 찾으려고 자기 방식대로 놓기 때문이에요. 그래서 수강생 화면의 순서가 슬라이드와 달라도 틀린 게 아니에요. 순서가 필요하면 13에서 배운 sorted()에 넣어요. 결과는 리스트라 대괄호로 나오고, 언제나 abc 순서예요. 왼쪽과 오른쪽 모두 실제로 실행한 결과예요. 슬라이드를 다시 만들 때 같은 출력이 나오도록 demo.sh는 커널마다 PYTHONHASHSEED를 고정했어요.")

o = [sec("s-dedup")] + head(EB1, "set(리스트)로 중복을 없애요", K1)
o += cell({"id": "c-d", "lines": ['orders = ["coffee", "latte", "coffee", "cake", "latte"]', "kinds = set(orders)", "print(kinds)", "print(len(orders), len(kinds))", "print(sorted(kinds))"], "n": 4,
           "out": ["{'latte', 'cake', 'coffee'}", "5 3", "['cake', 'coffee', 'latte']"]}, 96, 200, 1000, sel="c-d")
o.append(label("orders · 주문 5잔", 1150, 200, GRAY, ' data-build-in="fade order 1"', 674, 24))
o.append(f'<div data-build-in="rise order 1" style="position:absolute;left:1150px;top:244px;width:674px;display:flex;flex-direction:row;flex-wrap:wrap;gap:10px">'
         + "".join(chip(f'"{x}"', GRAY, "#EEEFF2", 24) for x in ["coffee", "latte", "coffee", "cake", "latte"]) + '</div>')
o.append(f'<x-shape data-build-in="fade order 2" kind="arrow-right" style="position:absolute;left:1460px;top:384px;width:56px;height:34px;transform:rotate(90deg);background:#C9CED8"></x-shape>')
o.append(bag(['"latte"', '"cake"', '"coffee"'], 1190, 440, 600, 300, attrs=' data-build-in="rise order 2"', fs=28, name="kinds", pos=[(0.30, 0.34), (0.70, 0.36), (0.50, 0.70)]))
o.append(row_card(96, 620, 1000, 100, "len(kinds)", "3", "팔린 메뉴는 세 가지", 3, K1, K1BG, 250))
o.append(row_card(96, 736, 1000, 100, "sorted(kinds)", "['cake', 'coffee', 'latte']", "보기 좋게 줄 세우기", 4, K1, K1BG, 250))
o.append(caption("몇 가지인지 셀 때는 set으로 바꾸고 len을 써요.", 920))
W("s-dedup", o, "set() 괄호 안에 리스트를 넣으면 리스트의 값으로 집합을 만들어요. 겹친 coffee와 latte는 하나씩만 남아요. 주문은 5잔이지만 메뉴 종류는 3가지예요. 리스트 orders는 그대로 남아 있어요. 집합을 다시 리스트로 보고 싶으면 sorted()에 넣어요. 4파트에서 이 방법으로 하루 주문을 정리해요." + REAL)

o = [sec("s-long")] + head(EB1, "set(리스트)는 긴 반복을 한 줄로 줄인 거예요", K1)
o.append(card(96, 200, 860, 140, '<div style="display:flex;flex-direction:row;align-items:center;gap:18px">' + p(f"font-size:26px;font-weight:700;color:{K1}", "줄여 쓴 방법") + mono("kinds = set(orders)", 32, K1, K1BG) + '</div>', K1, ' data-build-in="rise order 1"', "justify-content:center"))
o.append(label("for와 add로 길게 쓰면", 96, 372, K1, ' data-build-in="fade order 2"', 860, 24))
o += cell({"id": "c-l", "lines": ["kinds = set()", "for o in orders:", "    kinds.add(o)", "print(sorted(kinds))"], "n": 5, "out": ["['cake', 'coffee', 'latte']"]}, 96, 414, 860, sel="c-l", attrs=' data-build-in="rise order 2"')
o.append(note_card(96, 680, 860, 200, "결과는 같아요", "빈 주머니에서 시작해 하나씩 add해요. add는 이미 있으면 그대로라서 겹친 주문이 하나만 남아요.", None, ' data-build-in="rise order 3"'))
o.append(ref_box(1010, 200, 814, 420, ["kinds = []", "for o in orders:", "    if o not in kinds:", "        kinds.append(o)", "print(kinds)"], ["['coffee', 'latte', 'cake']"], ' data-build-in="rise order 4"', "참고 · 집합이 없으면 이렇게"))
o.append(note_card(1010, 650, 814, 230, "리스트로는 하나씩 물어봐야 해요", "아직 없을 때만 append해요. 집합은 그 일을 알아서 해요.", None, ' data-build-in="rise order 5"'))
o.append(caption("한 줄짜리 기능은 이런 반복을 대신해 줘요. 원래 모양을 알면 결과를 읽기 쉬워요.", 920))
W("s-long", o, "set(orders) 한 줄이 실제로 하는 일을 길게 풀어 봐요. 빈 집합 kinds에서 시작해 for로 주문을 하나씩 꺼내 add해요. 2파트에서 볼 add는 이미 있는 값이면 아무 일도 하지 않아서, 겹친 주문은 하나만 남아요. 결과는 set(orders)와 같아요. 집합이 없으면 리스트에 담으면서 '아직 없을 때만 넣기'를 직접 물어야 해요. 그때 쓰는 if는 아직 배우지 않았으니 오른쪽은 읽기만 해요. 리스트는 처음 나온 순서를 지켜서 coffee, latte, cake 순서예요. 왼쪽 셀과 오른쪽 참고 코드 모두 실제로 실행한 결과예요.")

o = [sec("s-str")] + head(EB1, "문자열을 넣으면 글자로 쪼개져요", K1)
o += cell({"id": "c-s", "lines": ['print(set("banana"))', 'print(len(set("banana")))', 'print(set(["banana"]))', 'print({"banana"})'], "n": 6, "out": ["{'b', 'a', 'n'}", "3", "{'banana'}", "{'banana'}"]}, 96, 200, 860, sel="c-s")
o.append(label('set("banana")', 1010, 200, RED, ' data-build-in="fade order 1"', 814))
o.append(slots(list("banana"), 1010, 246, 58, 70, hi=(0, 1, 2), attrs=' data-build-in="rise order 1"', fs=28, color=GRAY, bg="#EEEFF2"))
o.append(bag(["'b'", "'a'", "'n'"], 1010, 400, 380, 260, RED, "#F8E6E6", ' data-build-in="rise order 1"', 28, pos=[(0.28, 0.36), (0.70, 0.40), (0.48, 0.72)]))
o.append(label('{"banana"}', 1444, 360, GR, ' data-build-in="fade order 2"', 380))
o.append(bag(["'banana'"], 1444, 400, 380, 260, GR, "#E6F4EC", ' data-build-in="rise order 2"', 28, pos=[(0.5, 0.52)]))
o.append(warn(96, 620, 860, 230, "문자열은 글자를 하나씩 담은 줄이에요", "13에서 문자열도 번호로 한 글자씩 꺼냈어요. 그래서 set()에 넣으면 글자마다 하나씩 들어가요.", ' data-build-in="rise order 3"', OR))
o.append(caption('단어 하나를 담으려면 {"banana"}로 적거나 리스트로 감싸요.', 920))
W("s-str", o, "set() 괄호 안에 문자열을 바로 넣으면 단어 하나가 아니라 글자가 들어가요. 13에서 문자열도 리스트처럼 번호로 한 글자씩 꺼냈던 것과 같은 이유예요. banana에서 a와 n이 겹쳐서 b, a, n 세 글자만 남아요. 단어를 통째로 하나 담고 싶으면 중괄호에 바로 적거나, 리스트로 감싼 뒤 set()에 넣어요. 앞 장의 set(orders)는 리스트를 넣어서 단어가 그대로 들어갔어요." + REAL)

o = [sec("s-empty")] + head(EB1, "빈 집합은 {}가 아니라 set()이에요", K1)
o += cell({"id": "c-e", "lines": ["a = {}", "print(type(a))", "b = set()", "print(type(b))", "print(b)", "print(len(b))"], "n": 7, "out": ["<class 'dict'>", "<class 'set'>", "set()", "0"]}, 96, 200, 860, sel="c-e")
o.append(card(1010, 200, 814, 300, '<div style="display:flex;flex-direction:row;align-items:center;gap:18px">' + mono("{}", 40, RED, "#F8E6E6") + f'<x-shape kind="arrow-right" style="width:44px;height:26px;flex:none;background:#C9CED8"></x-shape>'
              + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{INK}", e("<class 'dict'>")) + '</div>'
              + p(f"font-size:26px;line-height:1.5;color:{INK}", "15에서 본 빈 딕셔너리예요. 중괄호가 딕셔너리 차지가 됐어요."), RED, ' data-build-in="rise order 1"'))
o.append(card(1010, 530, 814, 330, '<div style="display:flex;flex-direction:row;align-items:center;gap:18px">' + mono("set()", 40, GR, "#E6F4EC") + f'<x-shape kind="arrow-right" style="width:44px;height:26px;flex:none;background:#C9CED8"></x-shape>'
              + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{INK}", e("<class 'set'>")) + '</div>'
              + p(f"font-size:26px;line-height:1.5;color:{INK}", "빈 집합은 set()으로 만들어요. print로 찍어도 set()이라고 나와요."), GR, ' data-build-in="rise order 2"'))
o.append(bag([], 96, 650, 420, 230, K1, K1BG, ' data-build-in="rise order 2"', name="b"))
o.append(caption("빈 주머니에서 시작해서 2파트의 add로 하나씩 넣어요.", 920))
W("s-empty", o, "빈 중괄호는 집합이 아니라 빈 딕셔너리예요. 딕셔너리가 먼저 중괄호를 쓰고 있었기 때문이에요. type으로 보면 dict라고 나와요. 빈 집합은 set()으로 만들어요. print로 찍어도 {}가 아니라 set()이라고 나와서 딕셔너리와 헷갈리지 않아요. 빈 딕셔너리에 집합처럼 add를 쓰면 어떤 오류가 나는지는 4파트 끝에서 봐요." + REAL)

o = [sec("s-hash")] + head(EB1, "숫자, 문자열, 튜플은 담고 리스트는 못 담아요", K1)
o += cell({"id": "c-h1", "lines": ['ok = {1, "kim", (2, 3)}', "print(len(ok))"], "n": 8, "out": ["3"]}, 96, 200, 860, sel="c-h1")
o += cell({"id": "c-h2", "lines": ["bad = {[1, 2], 3}"], "n": 9, "out": ["TypeError: unhashable type: 'list'"], "err": True}, 96, 380, 860, attrs=' data-build-in="rise order 2"')
o += cell({"id": "c-h3", "lines": ['d = {[1, 2]: "a"}'], "n": 10, "out": ["TypeError: unhashable type: 'list'"], "err": True}, 96, 520, 860, attrs=' data-build-in="rise order 3"')
for i, (v, ok_) in enumerate([("1", True), ('"kim"', True), ("(2, 3)", True), ("[1, 2]", False)]):
    x = 1010 + i * 206
    c = GR if ok_ else RED
    o.append(f'<div data-build-in="rise order {1 if ok_ else 2}" style="position:absolute;left:{x}px;top:200px;width:190px;height:200px;background:{CARD};border:3px solid {c};border-radius:20px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px">'
             + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{INK};white-space:pre", e(v))
             + f'<x-icon name="{"CheckCircle" if ok_ else "Warning"}" style="width:46px;height:46px;color:{c}"></x-icon></div>')
o.append(note_card(1010, 440, 814, 200, "리스트는 넣은 뒤에도 바뀌어요", "append로 늘어날 수 있는 값은 주머니에 못 넣어요. 튜플은 바뀌지 않아서 넣을 수 있어요.", RED, ' data-build-in="rise order 2"'))
o.append(note_card(1010, 670, 814, 200, "딕셔너리 키도 같은 규칙이에요", "15의 키 자리에도 리스트를 못 써요. 오류 메시지도 똑같아요.", K1, ' data-build-in="rise order 3"'))
o.append(warn(96, 680, 860, 190, "unhashable type: 'list'", "리스트는 집합에 넣을 수 없는 값이라는 뜻이에요.", ' data-build-in="rise order 4"'))
o.append(caption("주머니와 키 자리에는 바뀌지 않는 값만 들어가요.", 920))
W("s-hash", o, "집합에는 숫자, 문자열, 튜플을 넣을 수 있어요. 섞어 넣어도 돼요. 리스트는 넣으면 TypeError가 나요. 리스트는 append로 늘어나거나 값이 바뀔 수 있어서, 주머니가 같은 값인지 확인할 수가 없기 때문이에요. 튜플은 만든 뒤 바뀌지 않아서 넣을 수 있어요. 15의 딕셔너리 키도 같은 규칙이라 리스트를 키로 쓰면 같은 오류가 나요. 오류 끝의 unhashable은 집합이나 키 자리에 넣을 수 없는 값이라는 뜻으로 읽으면 돼요." + REAL)

# ---------- part 2: change and check ----------
o = [sec("s-add")] + head(EB2, "add로 하나 넣어요. 이미 있으면 그대로예요", K2)
o += cell({"id": "c-a", "lines": [MENUS, 'menus.add("tea")', "print(menus)", 'menus.add("coffee")', "print(menus)", "print(len(menus))"], "n": 1,
           "out": ["{'latte', 'cake', 'coffee', 'tea'}", "{'latte', 'cake', 'coffee', 'tea'}", "4"]}, 96, 200, 860, sel="c-a")
o.append(label('menus.add("tea")', 1010, 200, K2, ' data-build-in="fade order 1"', 814))
o.append(bag(['"latte"', '"cake"', '"coffee"', '"tea"'], 1010, 246, 814, 300, K2, K2BG, ' data-build-in="rise order 1"', 28, pos=[(0.22, 0.34), (0.55, 0.28), (0.36, 0.70), (0.78, 0.62)]))
o.append(card(1010, 590, 814, 270, '<div style="display:flex;flex-direction:row;align-items:center;gap:16px">' + mono('menus.add("coffee")', 28, K2, K2BG) + '</div>'
              + p(f"font-size:26px;line-height:1.5;color:{INK}", "coffee는 이미 있어서 아무 일도 안 일어나요. 오류도 안 나고, len도 4 그대로예요."), K2, ' data-build-in="rise order 2"'))
o.append(note_card(96, 680, 860, 190, "리스트는 append, 집합은 add", "add는 자리를 정해 넣지 않아요. 주머니에 던져 넣는 느낌이에요.", None, ' data-build-in="rise order 3"'))
o.append(caption("집합에 같은 값을 넣어도 하나만 남아요.", 920))
W("s-add", o, "집합에 값을 하나 넣을 때는 add를 써요. tea가 들어가서 네 개가 됐어요. 이미 있는 coffee를 한 번 더 add하면 아무것도 바뀌지 않아요. 오류도 나지 않아요. 13의 리스트는 append로 맨 뒤에 붙였지만, 집합은 순서가 없어서 맨 뒤라는 자리가 없어요. 이 파트는 새 커널이라 menus를 다시 만들고 셀 번호가 [1]부터예요." + REAL, ("change", "바꾸고 확인하기"))

o = [sec("s-remove")] + head(EB2, "remove는 없으면 오류, discard는 괜찮아요", K2)
o += cell({"id": "c-r1", "lines": ['menus.remove("latte")', "print(menus)"], "n": 2, "out": ["{'cake', 'coffee', 'tea'}"]}, 96, 200, 860, sel="c-r1")
o += cell({"id": "c-r2", "lines": ['menus.remove("juice")'], "n": 3, "out": ["KeyError: 'juice'"], "err": True}, 96, 380, 860, attrs=' data-build-in="rise order 2"')
o += cell({"id": "c-r3", "lines": ['menus.discard("juice")', 'menus.discard("tea")', "print(menus)"], "n": 4, "out": ["{'cake', 'coffee'}"]}, 96, 520, 860, attrs=' data-build-in="rise order 3"')
o.append(card(1010, 200, 814, 250, mono('remove("juice")', 30, RED, "#F8E6E6", "align-self:flex-start") + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{RED}", "KeyError: 'juice'")
              + p(f"font-size:26px;line-height:1.5;color:{INK}", "없는 값을 빼려고 하면 셀이 멈춰요. 꼭 있어야 하는 값에 써요."), RED, ' data-build-in="rise order 2"'))
o.append(card(1010, 470, 814, 250, mono('discard("juice")', 30, GR, "#E6F4EC", "align-self:flex-start") + p(f"font-size:26px;font-weight:700;color:{GR}", "오류 없음")
              + p(f"font-size:26px;line-height:1.5;color:{INK}", "있으면 빼고, 없으면 그냥 넘어가요. 있는지 모를 때 써요."), GR, ' data-build-in="rise order 3"'))
o.append(f'<div data-build-in="rise order 4" style="position:absolute;left:1010px;top:740px;width:814px;height:150px;background:#FAF8F3;border:3px dashed #B4B9C3;border-radius:18px;padding:14px 26px;display:flex;flex-direction:row;align-items:center;gap:22px">'
         + p(f"width:190px;flex:none;font-size:22px;font-weight:700;line-height:1.4;color:{GRAY}", "참고<br>discard를 길게 쓰면")
         + '<div style="display:flex;flex-direction:column">' + p(f"font-family:{MONO};font-size:24px;line-height:1.4;white-space:pre;color:{INK}", e('if "juice" in menus:')) + p(f"font-family:{MONO};font-size:24px;line-height:1.4;white-space:pre;color:{INK}", e('    menus.remove("juice")')) + '</div>'
         + p(f"font-size:20px;color:{GRAY}", "if는 다음에<br>배워요") + '</div>')
o.append(caption("15의 대괄호와 get처럼, remove와 discard도 짝이에요.", 920))
W("s-remove", o, "값을 빼는 방법은 두 가지예요. remove는 latte처럼 있는 값을 빼요. 없는 juice를 remove하면 KeyError가 나고 셀이 멈춰요. discard는 있으면 빼고 없으면 아무 일도 하지 않아요. juice는 없어서 그냥 넘어갔고, tea는 있어서 빠졌어요. 15에서 menu[\"tea\"]는 없으면 오류, menu.get(\"tea\")는 오류 없이 넘어갔던 것과 같은 관계예요. 아래 참고 칸은 discard가 줄여 준 원래 코드예요. 있는지 먼저 묻고 있을 때만 remove해요. if는 아직 배우지 않았으니 읽기만 해요." + REAL)

o = [sec("s-update")] + head(EB2, "update로 여러 개를 한 번에 넣어요", K2)
o += cell({"id": "c-u", "lines": ['menus.update(["juice", "tea", "coffee"])', "print(menus)", "print(len(menus))"], "n": 5, "out": ["{'tea', 'cake', 'coffee', 'juice'}", "4"]}, 96, 200, 860, sel="c-u")
o.append(label("넣기 전", 1010, 200, K2, ' data-build-in="fade order 1"', 380))
o.append(bag(['"cake"', '"coffee"'], 1010, 246, 380, 280, K2, K2BG, ' data-build-in="rise order 1"', 22, pos=[(0.32, 0.38), (0.62, 0.68)]))
o.append(label("update 뒤", 1444, 200, K2, ' data-build-in="fade order 2"', 380))
o.append(bag(['"tea"', '"cake"', '"coffee"', '"juice"'], 1444, 246, 380, 280, K2, K2BG, ' data-build-in="rise order 2"', 22, pos=[(0.30, 0.28), (0.70, 0.40), (0.30, 0.62), (0.68, 0.80)]))
o.append(note_card(1010, 560, 814, 300, "coffee는 하나만 남아요", "리스트에 coffee가 있어도 이미 들어 있어서 새로 생기지 않아요. 그래서 2개 더하기 3개가 아니라 4개예요.", K2, ' data-build-in="rise order 3"'))
o.append(note_card(96, 460, 860, 300, "add와 update", "add는 값 하나를 넣어요.<br>update는 리스트를 받아서 그 안의 값을 모두 넣어요.<br>13의 리스트 extend와 비슷해요.", None, ' data-build-in="rise order 4"'))
o.append(caption("update에는 리스트처럼 여러 값이 든 것을 넣어요.", 920))
W("s-update", o, "값 여러 개를 한 번에 넣을 때는 update를 써요. 괄호 안에 리스트를 넣으면 리스트의 값이 하나씩 주머니에 들어가요. 앞에서 남은 cake, coffee에 juice와 tea가 들어갔어요. coffee는 이미 있어서 그대로예요. 그래서 개수가 5가 아니라 4예요. 13에서 리스트 두 개를 이은 extend와 비슷하지만, 겹친 값은 하나만 남는다는 점이 달라요." + REAL)

o = [sec("s-pop")] + head(EB2, "집합의 pop은 아무거나 하나 빼요", K2)
o += cell({"id": "c-p", "lines": ["one = menus.pop()", "print(one)", "print(menus)", "nums = [10, 20, 30]", "print(nums.pop())"], "n": 6, "out": ["tea", "{'cake', 'coffee', 'juice'}", "30"]}, 96, 200, 860, sel="c-p")
o += cell({"id": "c-p2", "lines": ["menus.clear()", "print(menus)", "print(len(menus))"], "n": 7, "out": ["set()", "0"]}, 96, 610, 860, attrs=' data-build-in="rise order 3"')
o.append(card(1010, 200, 814, 250, '<div style="display:flex;flex-direction:row;align-items:center;gap:16px">' + mono("menus.pop()", 28, K2, K2BG) + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{INK}", "tea") + '</div>'
              + p(f"font-size:26px;line-height:1.5;color:{INK}", "어느 값이 나올지 정해져 있지 않아요. 순서가 없으니 맨 뒤도 없어요."), K2, ' data-build-in="rise order 1"'))
o.append(card(1010, 470, 814, 210, '<div style="display:flex;flex-direction:row;align-items:center;gap:16px">' + mono("nums.pop()", 28, GRAY, "#EEEFF2") + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{INK}", "30") + '</div>'
              + p(f"font-size:26px;line-height:1.5;color:{INK}", "13의 리스트 pop은 맨 뒤를 빼요."), GRAY, ' data-build-in="rise order 2"'))
o.append(card(1010, 700, 814, 170, '<div style="display:flex;flex-direction:row;align-items:center;gap:16px">' + mono("menus.clear()", 28, K2, K2BG) + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{INK}", "set()") + '</div>'
              + p(f"font-size:24px;color:{INK}", "모두 비워요. 빈 주머니가 남아요."), K2, ' data-build-in="rise order 3"'))
o.append(caption("특정 값을 빼려면 pop 대신 remove나 discard를 써요.", 920))
W("s-pop", o, "집합에도 pop이 있어요. 하지만 순서가 없어서 어느 값이 나올지 정해져 있지 않아요. 이번에는 tea가 나왔지만 수강생 화면에서는 다른 값이 나올 수 있어요. 13의 리스트 pop은 맨 뒤 값을 꺼냈어요. 집합에서 원하는 값을 빼려면 앞 장의 remove나 discard를 써요. clear는 값을 모두 비워요. 주머니는 그대로 남아서 set()으로 찍혀요. 출력은 실제로 실행한 결과이고, pop의 결과는 실행할 때마다 다를 수 있어요.")

o = [sec("s-in")] + head(EB2, "in으로 들어 있는지 물어요", K2)
o += cell({"id": "c-i", "lines": [MENUS, 'print("latte" in menus)', 'print("tea" in menus)', 'print("tea" not in menus)'], "n": 8, "out": ["True", "False", "True"]}, 96, 200, 860, sel="c-i")
o.append(bag(['"latte"', '"cake"', '"coffee"'], 1010, 200, 814, 280, K2, K2BG, ' data-build-in="rise order 1"', 28, pos=[(0.25, 0.40), (0.55, 0.30), (0.78, 0.66)]))
inn = [('"latte" in menus', "True", "주머니에 있어요"), ('"tea" in menus', "False", "없어요"), ('"tea" not in menus', "True", "없는 게 맞아요")]
for i, (k, r_, d) in enumerate(inn):
    o.append(row_card(1010, 520 + i * 116, 814, 100, k, r_, d, i + 1, K2, K2BG, 330))
o.append(note_card(96, 560, 860, 310, "14에서 배운 in 그대로예요", "리스트, 튜플, 문자열에 쓰던 in과 not in을 집합에도 써요. 답은 True 아니면 False예요.", None, ' data-build-in="rise order 4"'))
o.append(caption("집합은 꺼내기보다 들어 있는지 묻는 데 써요.", 920))
W("s-in", o, "14에서 리스트, 튜플, 문자열에 쓴 in과 not in을 집합에도 그대로 써요. latte는 들어 있어서 True, tea는 없어서 False예요. not in은 반대로 물어요. 집합은 번호로 꺼낼 수 없어서, 값이 있는지 묻는 게 주로 하는 일이에요. 나중에 배울 if와 함께 쓰면 있는 메뉴만 계산하는 코드를 만들어요. 앞 장에서 clear로 비운 menus를 이 셀에서 다시 만들었어요." + REAL)

o = [sec("s-noindex")] + head(EB2, "번호로 못 꺼내요. 필요하면 sorted()로 바꿔요", K2)
o += cell({"id": "c-n1", "lines": ["menus[0]"], "n": 9, "out": ["TypeError: 'set' object is not subscriptable"], "err": True}, 96, 200, 860, sel="c-n1")
o += cell({"id": "c-n2", "lines": ["print(sorted(menus))", "print(sorted(menus)[0])", "print(list(menus))"], "n": 10, "out": ["['cake', 'coffee', 'latte']", "cake", "['latte', 'cake', 'coffee']"]}, 96, 350, 860, attrs=' data-build-in="rise order 2"')
o.append(warn(1010, 200, 814, 230, "not subscriptable", "대괄호로 번호를 붙여 꺼낼 수 없다는 뜻이에요. 주머니에는 칸 번호가 없어요.", ' data-build-in="rise order 1"'))
o.append(card(1010, 460, 814, 200, '<div style="display:flex;flex-direction:row;align-items:center;gap:16px">' + mono("sorted(menus)[0]", 28, GR, "#E6F4EC") + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{INK}", "cake") + '</div>'
              + p(f"font-size:24px;line-height:1.5;color:{INK}", "abc 순서 리스트로 바꾼 뒤 꺼내요. 늘 같은 값이 나와요."), GR, ' data-build-in="rise order 2"'))
o.append(card(1010, 680, 814, 190, '<div style="display:flex;flex-direction:row;align-items:center;gap:16px">' + mono("list(menus)", 28, OR, "#F7EEDD") + '</div>'
              + p(f"font-size:24px;line-height:1.5;color:{INK}", "리스트가 되지만 순서는 집합이 찍히던 순서 그대로라 정해져 있지 않아요."), OR, ' data-build-in="rise order 3"'))
o.append(note_card(96, 640, 860, 230, "15의 keys()와 같아요", "list()로 바꾸면 번호를 쓸 수 있어요. 순서를 정하고 싶으면 sorted()를 써요.", None, ' data-build-in="rise order 4"'))
o.append(caption("번호가 필요하면 sorted()로 줄 세운 리스트를 써요.", 920))
W("s-noindex", o, "집합에 menus[0]처럼 번호를 붙이면 TypeError가 나요. subscriptable은 대괄호로 꺼낼 수 있다는 뜻인데, 집합은 칸 번호가 없어서 안 돼요. 꼭 번호로 꺼내야 하면 리스트로 바꿔요. sorted()는 abc 순서로 줄 세운 리스트를 줘서 [0]이 늘 cake예요. list()도 리스트를 주지만 집합이 찍히던 순서를 그대로 따라서 실행할 때마다 다를 수 있어요. 15에서 keys()에 번호를 붙이려고 list()로 바꾼 것과 같은 방법이에요." + REAL)

o = [sec("s-sort")] + head(EB2, "집합에는 sort()가 없어요. sorted()를 써요", K2)
o += cell({"id": "c-so1", "lines": ["menus.sort()"], "n": 11, "out": ["AttributeError: 'set' object has no attribute 'sort'"], "err": True}, 96, 200, 860, sel="c-so1")
o += cell({"id": "c-so2", "lines": ["nums = {30, 10, 20}", "print(sorted(nums))", "print(sorted(nums, reverse=True))", "print(sorted(menus, reverse=True))", "print(type(sorted(menus)))", "print(menus)"], "n": 12,
           "out": ["[10, 20, 30]", "[30, 20, 10]", "['latte', 'coffee', 'cake']", "<class 'list'>", "{'latte', 'cake', 'coffee'}"]}, 96, 340, 860, attrs=' data-build-in="rise order 2"')
o.append(warn(1010, 200, 814, 190, "sort()는 리스트에만 있어요", "13의 리스트 sort()는 리스트 자리를 바꿔 줄 세워요. 집합은 자리가 없어서 sort()가 없어요.", ' data-build-in="rise order 1"'))
o.append(note_card(1010, 410, 814, 210, "sorted()는 새 리스트를 줘요", "작은 것부터, reverse=True면 큰 것부터예요. 결과는 리스트이고 menus는 그대로 집합이에요.", GR, ' data-build-in="rise order 2"'))
o.append(label("중복 없애고 줄 세우기", 1010, 650, K2, ' data-build-in="fade order 3"', 814, 24))
o += cell({"id": "c-so3", "lines": ['orders = ["tea", "cake", "tea", "coffee", "cake"]', "print(sorted(set(orders)))"], "n": 13, "out": ["['cake', 'coffee', 'tea']"]}, 1010, 694, 814, attrs=' data-build-in="rise order 3"')
i3 = next(i for i, x in enumerate(o) if 'id="c-so3"' in x)
o = o[:i3] + [x.replace("font-size:26px;line-height:1.45", "font-size:22px;line-height:1.45") for x in o[i3:]]
o = [x.replace("font-size:26px;line-height:1.45;white-space:pre;color:#A33131", "font-size:22px;line-height:1.45;white-space:pre;color:#A33131") for x in o]
o.append(caption("set()으로 중복을 없애고 sorted()로 줄 세우면 깔끔한 목록이 돼요.", 920))
W("s-sort", o, "13에서 리스트는 sort()로 제자리 정렬을 했어요. 집합에 sort()를 쓰면 AttributeError가 나요. 집합에는 자리가 없어서 자리를 바꿔 줄 세우는 sort()가 없기 때문이에요. 대신 sorted()를 써요. sorted()는 집합을 그대로 두고, 줄 세운 새 리스트를 돌려줘요. 13에서 본 reverse=True를 넣으면 큰 것부터, 글자는 z 쪽부터예요. type으로 보면 결과는 list이고, menus는 여전히 집합이에요. 실제로 가장 많이 쓰는 모양은 sorted(set(orders))예요. 겹친 주문을 없애고 abc 순서로 줄 세운 목록이 한 줄에 나와요." + REAL)

o = [sec("s-for")] + head(EB2, "for로 하나씩 꺼낼 수 있어요", K2)
o += cell({"id": "c-f1", "lines": ["for m in menus:", "    print(m)"], "n": 14, "out": ["latte", "cake", "coffee"]}, 96, 200, 820, sel="c-f1")
o += cell({"id": "c-f2", "lines": ["for m in sorted(menus):", "    print(m)"], "n": 15, "out": ["cake", "coffee", "latte"]}, 1004, 200, 820, attrs=' data-build-in="rise order 2"')
o.append(note_card(96, 480, 820, 260, "순서는 정해져 있지 않아요", "주머니에서 손에 잡히는 대로 하나씩 꺼내요. 개수 세기나 합계처럼 순서가 상관없는 일에 그대로 써요.", OR, ' data-build-in="rise order 1"'))
o.append(note_card(1004, 480, 820, 260, "순서가 필요하면 sorted()", "sorted()로 줄 세운 리스트를 for에 넣어요. 화면에 찍을 때는 이쪽이 읽기 좋아요.", GR, ' data-build-in="rise order 2"'))
o.append(f'<div data-build-in="rise order 3" style="position:absolute;left:96px;top:770px;width:1728px;height:110px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:0 30px;display:flex;flex-direction:row;align-items:center;gap:24px">'
         + mono("for 이름 in 집합:", 28, K2, K2BG) + p(f"font-size:26px;color:{INK}", "13의 리스트 for와 같은 모양이에요. 집합은 값마다 한 번씩 돌아요.") + '</div>')
o.append(caption("집합 그대로 돌면 순서가 섞이고, sorted()로 돌면 abc 순서예요.", 920))
W("s-for", o, "13에서 리스트를 for로 돌았던 것처럼 집합도 for로 하나씩 꺼낼 수 있어요. 집합을 그대로 넣으면 값마다 한 번씩 돌지만 순서는 정해져 있지 않아요. 왼쪽 결과는 print(menus)가 찍히던 순서와 같아요. 순서를 맞추고 싶으면 sorted(menus)를 넣어요. 4파트 실습에서는 화면에 찍을 때 sorted()를 써서 언제 실행해도 같은 결과가 나오게 해요." + REAL)

# ---------- part 3: set operations ----------
A_, B_ = "a = {1, 2, 3, 4}", "b = {3, 4, 5, 6}"
VX, VY, VW, VH = 96, 250, 820, 500
o = [sec("s-venn", "magic")] + head(EB3, "두 집합을 원 두 개로 그려요", K3)
o.append(f'<div id="ab-code" style="position:absolute;left:96px;top:196px;display:flex;flex-direction:row;gap:20px">' + mono(A_, 30, VA, K1BG) + mono(B_, 30, VB, K2BG) + '</div>')
o.append(venn(VX, 290, ["1", "2"], ["3", "4"], ["5", "6"], w=VW, h=VH, sid="vn-ab", fs=40, regions=[("a에만", 1), ("둘 다", 2), ("b에만", 3)]))
ex = [("a에만 있는 값", "1, 2", VA, K1BG), ("a와 b에 다 있는 값", "3, 4", K3, K3BG), ("b에만 있는 값", "5, 6", VB, K2BG)]
for i, (t, v, c, bg) in enumerate(ex):
    o.append(card(1010, 200 + i * 230, 814, 210, p(f"font-size:28px;font-weight:700;color:{INK}", t) + mono(v, 34, c, bg, "align-self:flex-start"), c, f' data-build-in="rise order {i + 1}"'))
o.append(caption("겹친 곳에는 두 집합에 다 있는 값이 들어가요.", 920))
W("s-venn", o, "이제 집합 두 개를 비교해요. 원 하나가 집합 하나예요. a는 1부터 4, b는 3부터 6이에요. 3과 4는 두 집합에 다 있어서 원이 겹친 곳에 그려요. 1과 2는 a에만, 5와 6은 b에만 있어요. 이 그림을 벤 다이어그램이라고 불러요. 이 파트는 이 그림 하나에 색을 칠하면서 세 가지 연산을 봐요. 숫자로 시작하는 이유는 작은 정수 집합이 보통 작은 수부터 찍혀서 읽기 쉽기 때문이에요.", ("ops", "집합 연산"))

o = [sec("s-union", "magic")] + head(EB3, "합집합 | 은 어느 쪽이든 있는 값이에요", K3)
o.append(f'<div id="ab-code" style="position:absolute;left:96px;top:196px;display:flex;flex-direction:row;gap:20px">' + mono(A_, 30, VA, K1BG) + mono(B_, 30, VB, K2BG) + '</div>')
o.append(venn(VX, 290, ["1", "2"], ["3", "4"], ["5", "6"], w=VW, h=VH, sid="vn-ab", fs=40, hi=[("union", K3, 1)]))
o += cell({"id": "c-u1", "lines": [A_, B_, "print(a | b)", "print(a.union(b))"], "n": 1, "out": ["{1, 2, 3, 4, 5, 6}", "{1, 2, 3, 4, 5, 6}"]}, 1010, 200, 814, sel="c-u1", attrs=' data-build-in="rise order 2"')
o.append(op_card(1010, 560, 814, 300, "a | b", "a.union(b)", "{1, 2, 3, 4, 5, 6}", "두 주머니를 쏟아 합쳐요. 겹친 3, 4는 하나씩만 남아요.", K3, K3BG, ' data-build-in="rise order 3"'))
o.append(caption("| 는 세로줄이에요. 보통 Enter 위 키를 Shift와 함께 눌러요.", 920))
W("s-union", o, "합집합은 두 집합 중 어느 쪽에든 있는 값을 모두 모은 거예요. 파이썬에서는 세로줄 | 로 써요. 두 원 전체를 칠한 것과 같아요. 겹친 3과 4는 한 번씩만 들어가서 값은 6개예요. 같은 일을 a.union(b)처럼 메서드 이름으로도 쓸 수 있어요. 기호가 헷갈리면 이름으로 적어도 결과는 같아요. 세로줄은 보통 키보드 Enter 위, 원화 기호나 역슬래시 키에 있어요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL)

o = [sec("s-inter", "magic")] + head(EB3, "교집합 & 는 둘 다 있는 값이에요", K3)
o.append(f'<div id="ab-code" style="position:absolute;left:96px;top:196px;display:flex;flex-direction:row;gap:20px">' + mono(A_, 30, VA, K1BG) + mono(B_, 30, VB, K2BG) + '</div>')
o.append(venn(VX, 290, ["1", "2"], ["3", "4"], ["5", "6"], w=VW, h=VH, sid="vn-ab", fs=40, hi=[("inter", K3, 1)]))
o += cell({"id": "c-i1", "lines": ["print(a & b)", "print(a.intersection(b))"], "n": 2, "out": ["{3, 4}", "{3, 4}"]}, 1010, 200, 814, sel="c-i1", attrs=' data-build-in="rise order 2"')
o.append(op_card(1010, 480, 814, 300, "a & b", "a.intersection(b)", "{3, 4}", "두 주머니에 다 있는 값만 골라요. 겹친 곳만 칠해요.", K3, K3BG, ' data-build-in="rise order 3"'))
o.append(caption("겹치는 사람, 겹치는 메뉴를 찾을 때 & 를 써요.", 920))
W("s-inter", o, "교집합은 두 집합에 모두 있는 값이에요. 앰퍼샌드 & 로 써요. 원이 겹친 곳만 칠한 것과 같아요. a와 b에 다 있는 값은 3과 4예요. 메서드 이름은 intersection이에요. 영어로 교차로라는 뜻이라, 두 길이 만나는 곳이라고 기억해요. 앞 셀에서 만든 a와 b를 그대로 써서 셀 번호가 [2]예요." + REAL)

o = [sec("s-diff", "magic")] + head(EB3, "차집합 - 는 앞에만 있는 값이에요", K3)
o.append(f'<div id="ab-code" style="position:absolute;left:96px;top:196px;display:flex;flex-direction:row;gap:20px">' + mono(A_, 30, VA, K1BG) + mono(B_, 30, VB, K2BG) + '</div>')
o.append(venn(VX, 290, ["1", "2"], ["3", "4"], ["5", "6"], w=VW, h=VH, sid="vn-ab", fs=40, hi=[("a-b", VA, 1), ("b-a", VB, 3)]))
o += cell({"id": "c-d1", "lines": ["print(a - b)", "print(b - a)", "print(a.difference(b))"], "n": 3, "out": ["{1, 2}", "{5, 6}", "{1, 2}"]}, 1010, 200, 814, sel="c-d1", attrs=' data-build-in="rise order 2"')
o.append(row_card(1010, 530, 814, 100, "a - b", "{1, 2}", "a에서 b에 있는 걸 빼요", 2, VA, K1BG, 200))
o.append(row_card(1010, 646, 814, 100, "b - a", "{5, 6}", "b에서 a에 있는 걸 빼요", 3, VB, K2BG, 200))
o.append(row_card(1010, 762, 814, 100, "a.difference(b)", "{1, 2}", "a - b와 같아요", 4, VA, K1BG, 290))
o.append(caption("빼기는 앞뒤를 바꾸면 결과가 달라요. 앞에 적은 쪽이 기준이에요.", 920))
W("s-diff", o, "차집합은 앞 집합에서 뒤 집합에 있는 값을 뺀 거예요. 빼기 기호 - 로 써요. a - b는 a에서 3과 4를 빼서 1, 2만 남아요. 숫자 빼기처럼 앞뒤를 바꾸면 결과가 달라요. b - a는 b에서 3과 4를 빼서 5, 6이에요. 그림에서는 앞에 적은 원에서 겹친 곳을 뺀 부분만 칠해요. 메서드 이름은 difference예요." + REAL)

o = [sec("s-ops")] + head(EB3, "세 연산을 한 장에 모아요", K3)
ops3 = [("a | b", "a.union(b)", "{1, 2, 3, 4, 5, 6}", "어느 쪽이든", [("union", K3, 1)]),
        ("a & b", "a.intersection(b)", "{3, 4}", "둘 다", [("inter", K3, 2)]),
        ("a - b", "a.difference(b)", "{1, 2}", "a에만", [("a-b", K3, 3)])]
for i, (code, meth, res, d, hi_) in enumerate(ops3):
    x = 96 + i * 584
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:{x}px;top:190px;width:560px;height:420px;background:{CARD};border:2px solid {LINE};border-top:10px solid {K3};border-radius:20px"></div>')
    o.append(venn(x + 70, 206, ["1", "2"], ["3", "4"], ["5", "6"], w=420, h=240, fs=24, hi=hi_, attrs=f' data-build-in="rise order {i + 1}"'))
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:{x + 30}px;top:460px;width:500px;display:flex;flex-direction:column;gap:12px">'
             + '<div style="display:flex;flex-direction:row;align-items:center;gap:14px">' + mono(code, 30, K3, K3BG) + p(f"font-size:26px;font-weight:700;color:{INK}", d) + '</div>'
             + p(f"font-family:{MONO};font-size:22px;color:{SUB}", e(meth)) + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{INK}", e(res)) + '</div>')
o += cell({"id": "c-o", "lines": ["c = a | b", "print(a, b)", "print(len(c), len(a & b))"], "n": 4, "out": ["{1, 2, 3, 4} {3, 4, 5, 6}", "6 2"]}, 96, 640, 1000, sel="c-o", attrs=' data-build-in="rise order 4"')
o.append(note_card(1150, 640, 674, 230, "a와 b는 그대로예요", "연산은 새 집합을 만들어요. 결과를 쓰려면 c = a | b처럼 변수에 담아요.", K3, ' data-build-in="rise order 5"'))
o.append(caption("기호가 헷갈리면 union, intersection, difference로 적어요.", 920))
W("s-ops", o, "세 연산을 나란히 놓았어요. 어느 쪽이든 있으면 |, 둘 다 있으면 &, 앞에만 있으면 - 예요. 기호 대신 union, intersection, difference라는 이름으로 써도 같아요. 연산을 해도 a와 b는 바뀌지 않아요. 결과는 새 집합이라 c = a | b처럼 변수에 담아서 써요. len(c)는 6, 겹치는 값의 개수 len(a & b)는 2예요. 대칭차집합 ^, 부분집합 issubset, frozenset은 이번 챕터에서 다루지 않아요." + REAL)

o = [sec("s-long2")] + head(EB3, "연산 기호도 for를 줄인 거예요", K3)
o.append(f'<div data-build-in="rise order 1" style="position:absolute;left:96px;top:200px;width:860px;display:flex;flex-direction:row;align-items:center;gap:16px">' + mono("a | b", 32, K3, K3BG) + p(f"font-size:26px;font-weight:700;color:{INK}", "를 for와 add로 길게 쓰면") + '</div>')
o += cell({"id": "c-l2", "lines": ["c = set(a)", "for x in b:", "    c.add(x)", "print(c)"], "n": 5, "out": ["{1, 2, 3, 4, 5, 6}"]}, 96, 268, 860, sel="c-l2", attrs=' data-build-in="rise order 1"')
mp = [("a | b", "a를 담고, b를 하나씩 add"), ("a & b", "a에서 b에도 있는 것만 담기"), ("a - b", "a에서 b에 없는 것만 담기")]
o.append(card(96, 540, 860, 340, p(f"font-size:28px;font-weight:700;color:{INK}", "기호 하나가 하는 일")
              + "".join('<div style="display:flex;flex-direction:row;align-items:center;gap:20px">' + mono(k, 28, K3, K3BG) + p(f"font-size:26px;color:{INK}", e(d)) + '</div>' for k, d in mp), K3, ' data-build-in="rise order 4"'))
o.append(ref_box(1010, 196, 814, 340, ["both = set()", "for x in a:", "    if x in b:", "        both.add(x)", "print(both)"], ["{3, 4}"], ' data-build-in="rise order 2"', "참고 · a & b를 길게 쓰면", 22))
o.append(ref_box(1010, 556, 814, 340, ["only_a = set()", "for x in a:", "    if x not in b:", "        only_a.add(x)", "print(only_a)"], ["{1, 2}"], ' data-build-in="rise order 3"', "참고 · a - b를 길게 쓰면", 22))
o.append(caption("긴 코드를 알면 기호의 뜻이 보여요. 실제로 쓸 때는 기호 한 줄로 적어요.", 920))
W("s-long2", o, "앞에서 본 세 연산을 길게 풀면 이렇게 돼요. 합집합은 a를 그대로 담은 새 집합에 b의 값을 하나씩 add하면 돼요. 이건 지금까지 배운 것만으로 쓸 수 있어서 셀로 실행해요. 교집합과 차집합은 b에 있는지, 없는지 물어서 담을지 정해야 해서 if가 필요해요. if는 다음에 배우니 오른쪽 두 칸은 읽기만 해요. 결과는 각각 {3, 4}, {1, 2}로 & 와 - 결과와 같아요. 실제로는 기호 한 줄로 쓰고, 긴 코드는 기호가 무슨 일을 하는지 이해하는 데 써요." + REAL)

# ---------- part 4: practice ----------
o = [sec("x-kinds")] + head(EB4, "하루 주문에서 팔린 메뉴 종류를 뽑아요", K4)
o += cell({"id": "c-k", "lines": ['orders = ["coffee", "latte", "coffee", "cake",', '          "coffee", "latte", "tea"]', "kinds = set(orders)", 'print(f"주문 {len(orders)}잔, 메뉴 {len(kinds)}가지")', "for m in sorted(kinds):", "    print(m, orders.count(m))"], "n": 1,
           "out": ["주문 7잔, 메뉴 4가지", "cake 1", "coffee 3", "latte 2", "tea 1"]}, 96, 200, 1000, sel="c-k")
steps4 = [("set(orders)", "겹친 주문을 하나로", "종류만 남기기"), ("len(kinds)", "4", "몇 가지인지"), ("sorted(kinds)", "abc 순서로", "늘 같은 순서로 찍기"), ("orders.count(m)", "13의 count", "원래 리스트에서 잔 수 세기")]
for i, (k, r_, d) in enumerate(steps4):
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:1150px;top:{200 + i * 170}px;width:674px;height:150px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:16px 24px;display:flex;flex-direction:column;justify-content:center;gap:10px">'
             + '<div style="display:flex;flex-direction:row;align-items:center;gap:14px">' + num(i + 1, K4, 30) + mono(k, 26, K4, K4BG) + p(f"font-size:24px;font-weight:700;color:{INK}", e(r_)) + '</div>'
             + p(f"font-size:22px;color:{SUB};padding-left:60px", e(d)) + '</div>')
o.append(caption("종류는 집합으로, 잔 수는 원래 리스트로 세요.", 920))
W("x-kinds", o, "카페의 하루 주문이 리스트 orders에 7잔 쌓였어요. 메뉴가 몇 가지 팔렸는지 알고 싶으면 set으로 바꾸고 len을 세요. 4가지예요. 메뉴별로 몇 잔인지는 집합이 아니라 원래 리스트에서 13의 count로 세요. 집합은 중복을 없앴으니 셀 수가 없어요. for에는 sorted(kinds)를 넣어서 언제 실행해도 abc 순서로 찍히게 했어요. 리스트는 대괄호가 닫히기 전이라 두 줄로 나눠 적었어요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("practice", "실습"))

o = [sec("x-class")] + head(EB4, "두 반을 다 듣는 사람과 한쪽만 듣는 사람", K4)
o += cell({"id": "c-c", "lines": ['python_class = {"kim", "lee", "park", "choi"}', 'data_class = {"park", "choi", "jung", "kang"}', "both = python_class & data_class", "print(sorted(both))", "print(sorted(python_class - data_class))", "print(sorted(data_class - python_class))", 'print(f"모두 {len(python_class | data_class)}명")'], "n": 2,
           "out": ["['choi', 'park']", "['kim', 'lee']", "['jung', 'kang']", "모두 6명"]}, 96, 200, 1000, sel="c-c")
o.append(venn(1130, 200, ["kim", "lee"], ["park", "choi"], ["jung", "kang"], "python_class", "data_class", w=700, h=440, fs=28, hi=[("inter", K4, 1), ("a-b", VA, 2), ("b-a", VB, 3)]))
cl = [("&", "두 반 다 듣는 사람", "park, choi"), ("-", "파이썬반만", "kim, lee"), ("|", "중복 없이 전체 인원", "6명")]
for i, (k, d, r_) in enumerate(cl):
    o.append(f'<div data-build-in="rise order {i + 1 if i < 2 else 4}" style="position:absolute;left:{96 + i * 584}px;top:760px;width:560px;height:120px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:0 24px;display:flex;flex-direction:row;align-items:center;gap:18px">'
             + mono(k, 34, K4, K4BG) + '<div style="display:flex;flex-direction:column;gap:4px">' + p(f"font-size:24px;font-weight:700;color:{INK}", e(d)) + p(f"font-family:{MONO};font-size:24px;color:{SUB}", e(r_)) + '</div></div>')
o.append(caption("8명을 적었지만 겹친 두 명은 한 번만 세서 6명이에요.", 930))
W("x-class", o, "파이썬반과 데이터반 명단을 집합으로 만들었어요. 두 반을 다 듣는 사람은 교집합 & 로 찾아요. park과 choi예요. 파이썬반만 듣는 사람은 파이썬반에서 데이터반을 뺀 kim, lee예요. 반대로 빼면 데이터반만 듣는 jung, kang이 나와요. 전체 인원은 합집합의 len이에요. 명단에는 8명이 적혀 있지만 park과 choi가 겹쳐서 6명이에요. 결과는 sorted()로 줄 세워 찍어서 늘 같은 순서로 나와요." + REAL)

o = [sec("x-menu")] + head(EB4, "메뉴판에 없는 주문을 찾아요", K4)
o += cell({"id": "c-mn", "lines": ['menu = {"coffee": 4500, "latte": 5000, "cake": 6500}', 'orders = ["coffee", "tea", "cake", "juice", "coffee"]', "print(set(menu))", "print(sorted(set(orders) - set(menu)))", "print(sorted(set(orders) & set(menu)))"], "n": 3,
           "out": ["{'latte', 'cake', 'coffee'}", "['juice', 'tea']", "['cake', 'coffee']"]}, 96, 200, 1000, sel="c-mn")
o.append(venn(1130, 200, ["tea", "juice"], ["coffee", "cake"], ["latte"], "set(orders)", "set(menu)", w=700, h=440, fs=28, hi=[("a-b", RED, 2), ("inter", GR, 3)]))
o.append(card(96, 560, 1000, 150, '<div style="display:flex;flex-direction:row;align-items:center;gap:16px">' + mono("set(menu)", 28, K4, K4BG) + p(f"font-size:26px;color:{INK}", "딕셔너리를 넣으면 키만 모여요") + '</div>'
              + p(f"font-size:22px;color:{SUB}", "15의 sorted(menu)가 키만 줄 세운 것과 같아요"), None, ' data-build-in="rise order 1"', "justify-content:center;padding:16px 26px;gap:8px"))
o.append(row_card(96, 730, 1000, 70, "set(orders) - set(menu)", "['juice', 'tea']", "메뉴판에 없는 주문", 2, RED, "#F8E6E6", 400))
o.append(row_card(96, 810, 1000, 70, "set(orders) & set(menu)", "['cake', 'coffee']", "팔 수 있는 주문", 3, GR, "#E6F4EC", 400))
o.append(caption("두 목록을 비교할 때는 둘 다 집합으로 바꿔서 빼거나 겹쳐 봐요.", 930))
W("x-menu", o, "15의 메뉴판 딕셔너리 menu와 손님 주문 리스트 orders가 있어요. 주문 중에 메뉴판에 없는 것을 찾고 싶어요. set(menu)는 딕셔너리의 키만 모은 집합이에요. 15에서 sorted(menu)가 키만 줄 세웠던 것과 같아요. 주문을 집합으로 바꾸고 메뉴판 집합을 빼면 juice와 tea가 남아요. 교집합은 메뉴판에 있어서 팔 수 있는 주문이에요. latte는 메뉴판에만 있고 아무도 주문하지 않았어요." + REAL)

o = [sec("x-bill")] + head(EB4, "팔 수 있는 주문만 계산해요", K4)
o += cell({"id": "c-b", "lines": ["total = 0", "for m in sorted(set(orders) & set(menu)):", "    qty = orders.count(m)", '    print(f"{m:<8}{qty}개 {menu[m] * qty:>7,}원")', "    total += menu[m] * qty", 'print(f"합계 {total:,}원")'], "n": 4,
           "out": ["cake    1개   6,500원", "coffee  2개   9,000원", "합계 15,500원"], "wide": True}, 96, 200, 1100, sel="c-b")
bl = [("set(orders) & set(menu)", "메뉴판에 있는 주문만"), ("orders.count(m)", "그 메뉴가 몇 잔인지"), ("menu[m] * qty", "15의 키로 가격 꺼내 곱하기")]
for i, (k, d) in enumerate(bl):
    o.append(row_card(96, 630 + i * 92, 1100, 80, k, "", d, i + 1, K4, K4BG, 420))
o.append(note_card(1250, 200, 574, 330, "KeyError가 안 나요", "tea와 juice는 & 에서 빠져서 menu[m]으로 꺼낼 일이 없어요. 15에서는 get(name, 0)으로 피했어요.", GR, ' data-build-in="rise order 2"'))
o.append(note_card(1250, 560, 574, 330, "빠진 주문도 알려 줄 수 있어요", "앞 장의 set(orders) - set(menu)를 찍으면 juice, tea는 준비 중이라고 손님에게 알려 줄 수 있어요.", None, ' data-build-in="rise order 3"'))
o.append(caption("& 로 먼저 걸러 두면 for 안에서 없는 키를 만나지 않아요.", 930))
W("x-bill", o, "앞 장의 교집합으로 팔 수 있는 메뉴만 for로 돌아요. 메뉴마다 13의 count로 몇 잔인지 세고, 15처럼 menu[m]으로 가격을 꺼내 곱해요. tea와 juice는 교집합에서 이미 빠져서 menu[m]에서 KeyError가 나지 않아요. 15에서는 get(name, 0)으로 없는 메뉴를 0원 처리했는데, 집합으로 미리 거르는 방법도 있어요. 칸 맞추기와 콤마는 13의 f-string이에요. 출력의 한글은 영어 두 칸 너비로 그렸어요." + REAL)

o = [sec("x-choose")] + head(EB4, "무엇에 담을지 이렇게 골라요", K4)
ch = [("리스트", "[ ]", "순서대로 쌓고 번호로 꺼낼 때", "하루 주문 orders", GRAY),
      ("튜플", "( )", "바뀌지 않는 묶음", "(메뉴, 가격, 수량) 한 줄", GRAY),
      ("딕셔너리", "{키: 값}", "이름으로 값을 찾을 때", "메뉴판 menu", K1),
      ("집합", "{값}", "중복 없애기, 있는지 묻기, 겹침 찾기", "팔린 메뉴 종류, 두 반 명단", K4)]
for i, (nm, br, use, ex_, c) in enumerate(ch):
    y = 196 + i * 172
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:96px;top:{y}px;width:1728px;height:152px;background:{K4BG if c == K4 else CARD};border:2px solid {c if c == K4 else LINE};border-radius:20px;padding:0 34px;display:flex;flex-direction:row;align-items:center;gap:30px">'
             + p(f"width:170px;flex:none;font-size:34px;font-weight:700;color:{INK}", nm) + f'<div style="width:220px;flex:none">' + mono(br, 30, c, "#F6F5F1", "display:inline-block") + '</div>'
             + p(f"flex:1;font-size:30px;font-weight:700;color:{INK}", e(use)) + p(f"width:470px;flex:none;font-size:24px;color:{SUB}", "예: " + e(ex_)) + '</div>')
o.append(caption("섞어 써도 돼요. 4파트처럼 리스트를 집합으로 바꿔 비교하고 딕셔너리로 가격을 찾아요.", 900))
W("x-choose", o, "지금까지 배운 네 그릇을 언제 쓰는지 정리해요. 순서가 중요하고 같은 값이 여러 번 나와도 되면 리스트예요. 바뀌지 않는 한 묶음은 튜플이에요. 이름으로 값을 찾으면 딕셔너리예요. 중복을 없애거나, 들어 있는지 묻거나, 두 목록에서 겹치는 것을 찾으면 집합이에요. 실제로는 앞 장처럼 섞어 써요. 주문은 리스트로 쌓고, 비교할 때만 집합으로 바꾸고, 가격은 딕셔너리에서 찾아요.")

o = [sec("x-err")] + head(EB4, "집합에서 자주 나는 오류", K4)
o += cell({"id": "c-x1", "lines": ["cart = {}", 'cart.add("coffee")'], "n": 5, "out": ["AttributeError: 'dict' object has no attribute 'add'"], "err": True}, 96, 200, 1000, sel="c-x1")
o += cell({"id": "c-x2", "lines": ['menus = {"coffee", "latte"}', "menus[0]"], "n": 6, "out": ["TypeError: 'set' object is not subscriptable"], "err": True}, 96, 400, 1000, attrs=' data-build-in="rise order 2"')
o += cell({"id": "c-x3", "lines": ['menus.remove("tea")'], "n": 7, "out": ["KeyError: 'tea'"], "err": True}, 96, 600, 1000, attrs=' data-build-in="rise order 3"')
o += cell({"id": "c-x4", "lines": ['print(set("latte"))', 'print({"latte"})'], "n": 8, "out": ["{'e', 'a', 't', 'l'}", "{'latte'}"]}, 96, 762, 1000, attrs=' data-build-in="rise order 4"')
fx = [("{}는 빈 딕셔너리", "cart = set()"), ("집합은 번호가 없어요", "sorted(menus)[0]"), ("없는 값을 remove", 'menus.discard("tea")'), ("문자열이 글자로 쪼개짐", '{"latte"}')]
for i, (d, f_) in enumerate(fx):
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:1150px;top:{200 + i * 178}px;width:674px;height:156px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:16px 26px;display:flex;flex-direction:column;justify-content:center;gap:12px">'
             + '<div style="display:flex;flex-direction:row;align-items:center;gap:14px">' + num(i + 1, RED, 28) + p(f"font-size:26px;font-weight:700;color:{INK}", e(d)) + '</div>'
             + mono(f_, 26, GR, "#E6F4EC", "align-self:flex-start;margin-left:58px") + '</div>')
W("x-err", o, "집합에서 자주 나는 오류예요. 1번은 빈 집합을 {}로 만든 경우예요. {}는 딕셔너리라 add가 없다는 AttributeError가 나요. set()으로 만들어요. 2번은 집합에 번호를 붙인 경우예요. 번호가 필요하면 sorted()로 리스트를 만들어요. 3번은 없는 값을 remove한 경우예요. 있는지 모르면 discard를 써요. 4번은 오류는 안 나지만 결과가 이상한 경우예요. set()에 문자열을 넣으면 글자로 쪼개져요." + REAL)

# ---------- summary ----------
o = [sec("trouble")] + head("정리", "막히면 오류의 마지막 줄을 봐요", RED)
tr = [("AttributeError: 'dict' object has no attribute 'add'", "빈 집합을 {}로 만들었어요", "set()"),
      ("TypeError: 'set' object is not subscriptable", "집합에 번호를 붙였어요", "sorted(menus)[0]"),
      ("KeyError: 'juice'", "없는 값을 remove했어요", 'discard("juice")'),
      ("TypeError: unhashable type: 'list'", "집합에 리스트를 넣었어요", "튜플로 바꾸기"),
      ("{'b', 'a', 'n'}", "set()에 문자열을 넣어 글자로 쪼개졌어요", '{"banana"}'),
      ("print 순서가 슬라이드와 달라요", "집합은 순서가 없어요. 틀린 게 아니에요", "sorted(menus)")]
o.append('<div style="position:absolute;left:96px;top:196px;width:1728px;height:724px;display:flex;flex-direction:column;gap:8px">')
for i, (q, a_, cmd) in enumerate(tr, 1):
    o.append(f'<div data-build-in="rise order {i}" style="flex:1;display:flex;flex-direction:row;gap:26px;align-items:center;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:8px 30px">'
             + num(i, RED, 32)
             + '<div style="flex:1;display:flex;flex-direction:column;gap:4px">' + p(f"{'font-family:' + MONO + ';' if q.isascii() else ''}font-size:22px;font-weight:700;color:{INK};white-space:nowrap", e(q)) + p(f"font-size:22px;color:{SUB}", e(a_)) + '</div>'
             + p(f"width:360px;flex:none;{'font-family:' + MONO + ';font-size:22px;' if cmd.isascii() else 'font-size:24px;'}font-weight:700;line-height:1.5;color:{INK};background:#EEEFF2;padding:8px 18px;border-radius:12px;white-space:pre", e(cmd)) + '</div>')
o.append('</div>')
o.append(caption("오류가 안 나도 결과가 이상하면 문자열을 그대로 set()에 넣지 않았는지 봐요.", 940))
W("trouble", o, "1번부터 4번은 오류 메시지가 나는 경우예요. 오류 마지막 줄을 보면 어떤 값이 문제인지 나와요. 1번은 {}가 딕셔너리라서, 2번은 집합에 번호가 없어서, 3번은 없는 값을 remove해서, 4번은 리스트를 집합에 넣어서 나요. 5번과 6번은 오류는 안 나지만 결과가 생각과 다른 경우예요. 집합을 print한 순서가 슬라이드와 다른 것은 정상이에요. 모두 hello-uv 커널에서 실제로 실행한 결과예요.", ("trouble", "정리"))

o = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>']
cheat = [("{1, 2, 3}", "값만 적어 만들기", K1), ("set(orders)", "리스트에서 중복 없애기", K1), ("set()", "빈 집합", K1), ('s.add("tea")', "하나 넣기", K2),
         ('s.discard("tea")', "있으면 빼기", K2), ('"tea" in s', "들어 있는지 묻기", K2), ("a | b   a & b   a - b", "합집합, 교집합, 차집합", K3), ("sorted(s)", "줄 세운 리스트로", K4)]
for i, (k, d, c) in enumerate(cheat):
    x, y = 96 + (i % 4) * 438, 200 + (i // 4) * 290
    o.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:414px;height:264px;background:{CARD};border:2px solid {LINE};border-top:10px solid {c};border-radius:20px;padding:28px 28px;display:flex;flex-direction:column;gap:20px">'
             + mono(k, 26 if len(k) <= 19 else 21, c, "#F6F5F1", "align-self:flex-start") + p(f"font-size:28px;font-weight:700;color:{INK}", d) + '</div>')
o.append(f'<div style="position:absolute;left:96px;top:780px;width:1728px;height:210px;background:{CARD};border:2px solid {LINE};border-radius:20px;padding:24px 36px;display:flex;flex-direction:column;justify-content:center;gap:14px">'
         + p(f"font-size:30px;font-weight:700;color:{INK}", "집합은 같은 값을 하나만 담는 주머니예요. 순서와 번호가 없어요")
         + p(f"font-size:30px;font-weight:700;color:{INK}", '빈 집합은 <span style="font-family:\'JetBrains Mono\';color:' + K1 + '">set()</span>, 화면에 찍을 땐 <span style="font-family:\'JetBrains Mono\';color:' + K4 + '">sorted()</span>') + '</div>')
W("cheatsheet", o, "이번 챕터에서 쓴 코드를 한 장에 모았어요. 집합은 중복이 없고 순서가 없는 주머니라는 것을 기억해요. 노트북에 이 장의 내용을 마크다운 셀로 정리해 두면 복습할 때 같이 봐요. 다음에 배울 if 문과 in을 함께 쓰면 메뉴판에 있는 주문만 계산하는 코드를 다른 방법으로도 만들 수 있어요.")

# ---------- toc ----------
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
parts = [("Archive", K1, "집합이 뭔가요", "중복 없는 주머니, 네 그릇 비교, { }로 만들기, 순서 없음과 sorted(), set(리스트)와 긴 방법, 문자열 함정, 빈 집합 set(), 담을 수 있는 값", "s-why", "s-hash"),
         ("Wrench", K2, "바꾸고 확인하기", "add, remove와 discard, update, pop과 clear, in, 번호로 못 꺼내기, sort 대신 sorted(), for", "s-add", "s-for"),
         ("Activity", K3, "집합 연산", "벤 다이어그램, 합집합 |, 교집합 &, 차집합 -, union, intersection, difference, for로 길게 쓰면", "s-venn", "s-long2"),
         ("Database", K4, "실습", "팔린 메뉴 종류, 두 반 명단, 메뉴판에 없는 주문, 무엇에 담을지, 오류", "x-kinds", "x-err")]
TOC_NOTE = "네 파트로 나눴어요. 1파트는 집합이 무엇인지 그림으로 잡고, 2파트는 값을 넣고 빼고 확인해요. 3파트는 원 두 개로 집합 연산을 보고, 4파트는 앞에서 배운 것을 섞어 실제 주문과 명단을 정리해요. 파트마다 새 커널에서 위에서부터 차례로 실행해요."

DECK_TITLE = "파이썬 기초 5 (집합)"
t = [f'<section id="toc" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column;gap:40px">',
     f'<h2 style="font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>',
     f'<div style="display:grid;grid-template-columns:repeat({len(parts)},1fr);gap:18px;flex:1">']
for i, (ic, c, h, s, a, b) in enumerate(parts, 1):
    t.append(f'<div style="display:flex;flex-direction:column;gap:14px;background:#FFFFFF;border:2px solid {LINE};border-top:10px solid {c};border-radius:20px;padding:28px 26px">'
             f'<div style="display:flex;flex-direction:row;gap:16px;align-items:center"><p style="font-size:60px;font-weight:900;line-height:1.25;color:{c}">{i}</p>'
             f'<x-icon name="{ic}" style="width:48px;height:48px;color:{c}"></x-icon></div>'
             f'<h3 style="font-size:28px;font-weight:700;color:{INK}">{h}</h3>'
             f'<p style="font-size:24px;line-height:1.5;color:{SUB}">{e(s)}</p><div style="flex:1"></div>'
             f'<p style="font-size:26px;color:#6A7180">{page[a]}–{page[b]}쪽</p></div>')
t += ['</div>', f'<p style="font-size:26px;color:{SUB}">{page["ready"]}쪽은 노트북 준비, {page["trouble"]}–{page["cheatsheet"]}쪽은 막힐 때와 한 장 요약이에요.</p>']
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
