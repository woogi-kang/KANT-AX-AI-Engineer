"""Generates every slide of the inheritance and class variable deck (26) and slides/deck.json.

Story: picks up the Bread class from chapters 24 and 25. A 슈크림 붕어빵 class made by copying Bread shows the two
problems: every line copied, and the shop name kept in every object. Part 2 puts shop and count on the class (class
variables) and compares them with instance variables. Part 3 inherits Bread, adds a method, adds a slot with
super().__init__, overrides intro, calls super().intro() and mixes objects in one list (isinstance). Part 4 compares
copying with inheriting and the "is a kind of" test. Part 5 collects the usual errors, and part 6 is a stamp card with a
VIP card and a 붕어빵 menu with mini 붕어빵.
Every cell and output comes from tools/demo.sh (tools/run_nb.py runs the cells with the project kernel).
Usage: python3 tools/gen.py slides
"""

import html, json, os, re, sys


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
        wide = WIDE if c.get("wide") else (lambda t: t)
        col = lambda l: RED if c.get("err") and re.match(r"[A-Za-z]+(Error|Interrupt)", l) else INK   # only the error line is red
        o.append(''.join(p(f"margin-left:85px;padding:0 20px;font-family:{MONO};font-size:26px;line-height:1.45;white-space:pre;color:{col(l)}", wide(e(l)) if l else "&#160;") for l in c["out"]))
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




def chip(text, color=K1, bg=K1BG, fs=30, extra=""):
    return p(f"font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:1.2;color:{INK};background:{bg};border:3px solid {color};border-radius:999px;padding:6px 22px;white-space:pre;{extra}", e(text))



def warn(left, top, w, h, title, body, attrs="", color=RED):
    return card(left, top, w, h, '<div style="display:flex;flex-direction:row;align-items:center;gap:14px">' + f'<x-icon name="Warning" style="width:40px;height:40px;color:{color}"></x-icon>'
                + p(f"font-size:28px;font-weight:700;color:{INK}", title) + '</div>' + p(f"font-size:24px;line-height:1.5;color:{INK}", body), color, attrs)


def note_card(left, top, w, h, title, body, color=None, attrs="", extra=""):
    return card(left, top, w, h, p(f"font-size:28px;font-weight:700;color:{INK}", title) + p(f"font-size:24px;line-height:1.5;color:{INK}", body), color, attrs, extra)




# ---------- control flow pictures ----------
HL = {"run": "rgba(31,138,76,0.16)", "skip": "rgba(106,113,128,0.20)", "err": "rgba(163,49,49,0.14)", "mark": "rgba(36,89,201,0.14)"}
HLT = {"run": GR, "skip": GRAY, "err": RED, "mark": BL}
LINE_H = 37.7


def hl(left, top, w, i, n=1, kind="run", order=1, tag=None):
    """Tints code lines i..i+n-1 of a cell drawn by cell(c, left, top, w). tag: small word at the right end."""
    y = top + 10 + i * LINE_H
    at = f' data-build-in="fade order {order}"' if order else ""
    t = p(f"position:absolute;right:120px;top:0;font-size:19px;font-weight:700;line-height:{LINE_H:.0f}px;color:{HLT[kind]}", e(tag)) if tag else ""
    return f'<div{at} style="position:absolute;left:{left + 87}px;top:{y:.0f}px;width:{w - 89}px;height:{n * LINE_H:.0f}px;background:{HL[kind]};border-radius:6px">{t}</div>'


_fl = [0]


def flow(left, top, w, h, nodes, edges, attrs=""):
    """A small flowchart. nodes: dict(x, y, w, h, kind box|diamond|pill, text, color, bg, order, fs, mono).
    edges: dict(pts [(x, y), ...], color, order, label, lx, ly). Coordinates are inside the w x h area."""
    o = [f'<div{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px">']
    for ed in edges:
        _fl[0] += 1
        mid = f"fa{_fl[0]}"
        col = ed.get("color", "#9AA1AE")
        at = f' data-build-in="fade order {ed["order"]}"' if ed.get("order") else ""
        pts = " ".join(f"{x:.0f},{y:.0f}" for x, y in ed["pts"])
        dash = ' stroke-dasharray="12 10"' if ed.get("dash") else ""
        o.append(f'<svg{at} style="position:absolute;left:0;top:0;width:{w}px;height:{h}px" viewBox="0 0 {w} {h}">'
                 f'<defs><marker id="{mid}" markerUnits="userSpaceOnUse" markerWidth="24" markerHeight="24" refX="20" refY="12" orient="auto"><path d="M0,0 L24,12 L0,24 z" fill="{col}"/></marker></defs>'
                 f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="5" stroke-linejoin="round"{dash} marker-end="url(#{mid})"/></svg>')
        if ed.get("label"):
            o.append(p(f"position:absolute;left:{ed['lx']}px;top:{ed['ly']}px;font-size:24px;font-weight:700;color:{col};white-space:nowrap", e(ed["label"]), at))
    for nd in nodes:
        x, y, nw, nh = nd["x"], nd["y"], nd["w"], nd["h"]
        col, bg = nd.get("color", GRAY), nd.get("bg", CARD)
        at = f' data-build-in="{nd.get("anim", "rise")} order {nd["order"]}"' if nd.get("order") else ""
        fs = nd.get("fs", 26)
        font = MONO if nd.get("mono", True) else SANS
        txt = p(f"font-family:{font};font-size:{fs}px;font-weight:700;line-height:1.3;color:{nd.get('tc', INK)};text-align:center;white-space:pre", e(nd["text"]))
        if nd.get("kind") == "diamond":
            o.append(f'<div{at} style="position:absolute;left:{x}px;top:{y}px;width:{nw}px;height:{nh}px">'
                     f'<svg style="position:absolute;left:0;top:0;width:{nw}px;height:{nh}px" viewBox="0 0 {nw} {nh}"><polygon points="{nw / 2:.0f},3 {nw - 3},{nh / 2:.0f} {nw / 2:.0f},{nh - 3} 3,{nh / 2:.0f}" fill="{bg}" stroke="{col}" stroke-width="4"/></svg>'
                     f'<div style="position:absolute;left:{nw * 0.18:.0f}px;top:0;width:{nw * 0.64:.0f}px;height:{nh}px;display:flex;align-items:center;justify-content:center">{txt}</div></div>')
        else:
            rad = "999px" if nd.get("kind") == "pill" else "16px"
            o.append(f'<div{at} style="position:absolute;left:{x}px;top:{y}px;width:{nw}px;height:{nh}px;background:{bg};border:3px solid {col};border-radius:{rad};display:flex;align-items:center;justify-content:center;padding:0 14px">{txt}</div>')
    o.append('</div>')
    return "".join(o)


def side(left, top, w, h, title, lines, out, color, bg, attrs="", fs=24, tag=None, dashed=False):
    """A code panel with its real output, for long-versus-short comparisons."""
    code = "".join(p(f"font-family:{MONO};font-size:{fs}px;line-height:1.45;white-space:pre;color:{INK}", e(l) if l else "&#160;") for l in lines)
    res = "".join(p(f"font-family:{MONO};font-size:{fs}px;line-height:1.45;white-space:pre;color:{SUB}", e(l)) for l in out)
    bd = f"3px dashed {color}" if dashed else f"2px solid {LINE}"
    tg = p(f"font-size:20px;font-weight:700;color:{color};background:{bg};border-radius:8px;padding:2px 12px", e(tag)) if tag else ""
    return (f'<div{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:{CARD};border:{bd};border-top:10px solid {color};border-radius:20px;padding:20px 28px;display:flex;flex-direction:column;gap:12px">'
            + '<div style="display:flex;flex-direction:row;align-items:center;gap:14px">' + p(f"font-size:26px;font-weight:700;color:{INK}", e(title)) + tg + '</div>'
            + f'<div style="display:flex;flex-direction:column">{code}</div>'
            + (f'<div style="display:flex;flex-direction:column;border-top:2px solid {LINE};padding-top:8px">{res}</div>' if out else "") + '</div>')


def yes_no(left, top, kind, text, order=None, w=None):
    at = f' data-build-in="rise order {order}"' if order else ""
    c, b = (GR, "#E6F4EC") if kind else (RED, "#F8E6E6")
    ws = f"width:{w}px;" if w else ""
    return p(f"position:absolute;left:{left}px;top:{top}px;{ws}font-size:24px;font-weight:700;color:{c};background:{b};border-radius:10px;padding:6px 16px;white-space:nowrap", e(text), at)


def table(left, top, w, cols, rows, order0=1, color=K3, rh=60, attrs_each=True, hi=()):
    """A small trace table: header row, then one row per click."""
    o = [f'<div data-build-in="fade order {order0}" style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:44px;display:flex;flex-direction:row;gap:12px;padding:0 20px">'
         + "".join(p(f"width:{cw}px;flex:none;font-family:{MONO};font-size:21px;font-weight:700;color:{GRAY};white-space:nowrap", e(c)) for c, cw in cols) + '</div>']
    for i, r in enumerate(rows):
        on = i in hi
        at = f' data-build-in="rise order {order0 + i}"' if attrs_each else ""
        cells_ = ""
        for (c, cw), v in zip(cols, r):
            cells_ += f'<div style="width:{cw}px;flex:none">' + (tf(v, 20) if v in ("True", "False") else p(f"font-family:{MONO if v.isascii() else SANS};font-size:24px;font-weight:700;color:{INK};white-space:nowrap", e(v))) + '</div>'
        o.append(f'<div{at} style="position:absolute;left:{left}px;top:{top + 50 + i * (rh + 8)}px;width:{w}px;height:{rh}px;background:{(K3BG if color == K3 else K4BG) if on else CARD};border:2px solid {color if on else LINE};border-radius:14px;padding:0 20px;display:flex;flex-direction:row;align-items:center;gap:12px">{cells_}</div>')
    return o




K5, K5BG = RED, "#F8E6E6"
K6, K6BG = PUR, "#ECE7F8"
REAL = " 출력은 실제로 실행한 결과예요."

def arrow(w=60, color="#C9CED8"):
    return f'<x-shape kind="arrow-right" style="width:{w}px;height:30px;flex:none;background:{color}"></x-shape>'


def fn_box(left, top, inp, name, out, color, bg, order=None, w=1728, h=104, inw=420, outw=420, fs=28):
    """A function drawn as a machine: input chip, arrow, named box, arrow, output chip."""
    at = f' data-build-in="rise order {order}"' if order else ""
    return (f'<div{at} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;display:flex;flex-direction:row;align-items:center;gap:20px">'
            + f'<div style="width:{inw}px;flex:none;display:flex;justify-content:flex-end">' + chip(inp, GRAY, "#F1F0EC", fs) + '</div>' + arrow()
            + p(f"width:300px;height:{h}px;flex:none;border-radius:20px;background:{color};color:#FFFFFF;font-family:{MONO};font-size:{fs + 6}px;font-weight:700;line-height:{h}px;text-align:center;padding:0 30px", e(name))
            + arrow() + f'<div style="width:{outw}px;flex:none;display:flex">' + chip(out, color, bg, fs) + '</div></div>')


def callout(left, top, w, h, code, text, color, order, size=26):
    """A label card that explains one piece of a code line."""
    return (f'<div data-build-in="rise order {order}" style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:{CARD};border:2px solid {LINE};border-left:10px solid {color};border-radius:16px;padding:0 22px;display:flex;flex-direction:row;align-items:center;gap:18px">'
            + p(f"min-width:140px;flex:none;font-family:{MONO};font-size:{size + 2}px;font-weight:700;color:{color};white-space:pre", e(code))
            + p(f"flex:1;font-size:{size - 2}px;line-height:1.4;color:{INK}", e(text)) + '</div>')


def steps(rows, left, top, w, start=1, color=K2, gap=78, cw=(70, 560)):
    """Run order: one row per click. rows: (number, code, what happens)."""
    o = []
    for i, (n_, code, what) in enumerate(rows):
        y = top + i * gap
        o.append(f'<div data-build-in="rise order {start + i}" style="position:absolute;left:{left}px;top:{y}px;width:{w}px;height:{gap - 10}px;background:{CARD};border:2px solid {LINE};border-radius:14px;padding:0 18px;display:flex;flex-direction:row;align-items:center;gap:16px">'
                 + p(f"width:{cw[0]}px;flex:none;font-size:24px;font-weight:900;color:{color}", e(n_))
                 + p(f"width:{cw[1]}px;flex:none;font-family:{MONO};font-size:23px;font-weight:700;color:{INK};white-space:pre", e(code))
                 + p(f"flex:1;font-size:21px;color:{SUB};white-space:nowrap", e(what)) + '</div>')
    return o




def pipe(left, top, items, fn, outs, color, bg, order=1, w=170, keep=None, fs=30, fn_w=None):
    """map and filter drawn as a pipe: input boxes on top, a function band in the middle, results below.
    keep: list of True/False per item for filter (False items are crossed out and do not reach the bottom)."""
    n = len(items)
    width = n * (w + 8) - 8
    fw = fn_w or width
    o = [slots(items, left, top, w, 90, top_lbl=False, fs=fs, color=GRAY, bg="#F1F0EC", attrs=f' data-build-in="fade order {order}"')]
    o.append(f'<div data-build-in="fade order {order + 1}" style="position:absolute;left:{left}px;top:{top + 116}px;width:{fw}px;height:90px;border-radius:18px;background:{color};display:flex;align-items:center;justify-content:center">'
             + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:#FFFFFF;white-space:pre", e(fn)) + '</div>')
    for i in range(n):
        x = left + i * (w + 8) + w // 2 - 13
        o.append(f'<x-shape data-build-in="fade order {order + 1}" kind="arrow-right" style="position:absolute;left:{x}px;top:{top + 92}px;width:26px;height:22px;transform:rotate(90deg);background:#C9CED8"></x-shape>')
    for i, v in enumerate(outs):
        x = left + i * (w + 8)
        ok = keep is None or keep[i]
        o.append(f'<x-shape data-build-in="fade order {order + 2}" kind="arrow-right" style="position:absolute;left:{x + w // 2 - 13}px;top:{top + 208}px;width:26px;height:22px;transform:rotate(90deg);background:{color if ok else "#E1DED6"}"></x-shape>')
        o.append(p(f"position:absolute;left:{x}px;top:{top + 232}px;width:{w}px;height:90px;border-radius:14px;border:3px {'solid' if ok else 'dashed'} {color if ok else '#C9CED8'};background:{bg if ok else CARD};"
                   f"font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:84px;text-align:center;color:{INK if ok else '#B4B9C3'};white-space:pre{';text-decoration:line-through' if not ok else ''}", e(v), f' data-build-in="rise order {order + 2}"'))
    return o


def compare3(left, top, w, rows, order=1, code_w=None, fs=24, h=None):
    """Rows of (label, code, color, bg) shown one per click: the same job written several ways."""
    o = []
    hh = h or 96
    for i, (lbl, code, c, b) in enumerate(rows):
        o.append(f'<div data-build-in="rise order {order + i}" style="position:absolute;left:{left}px;top:{top + i * (hh + 14)}px;width:{w}px;height:{hh}px;background:{CARD};border:2px solid {LINE};border-left:10px solid {c};border-radius:16px;padding:0 24px;display:flex;flex-direction:row;align-items:center;gap:22px">'
                 + p(f"width:{code_w or 200}px;flex:none;font-size:23px;font-weight:700;color:{c}", e(lbl))
                 + p(f"flex:1;font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:1.4;color:{INK};white-space:pre", e(code)) + '</div>')
    return o


def finish(parts, toc_note, title):
    page = {sid: i + 1 for i, sid in enumerate(ORDER)}
    t = [f'<section id="toc" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column;gap:32px">',
         f'<h2 style="font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>',
         f'<div style="display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(2,1fr);gap:18px;flex:1">']
    for i, (ic, c, h, s, a, b) in enumerate(parts, 1):
        t.append(f'<div style="display:flex;flex-direction:column;gap:10px;background:#FFFFFF;border:2px solid {LINE};border-top:10px solid {c};border-radius:20px;padding:20px 26px">'
                 f'<div style="display:flex;flex-direction:row;gap:16px;align-items:center"><p style="font-size:48px;font-weight:900;line-height:1.2;color:{c}">{i}</p>'
                 f'<x-icon name="{ic}" style="width:40px;height:40px;color:{c}"></x-icon><h3 style="font-size:28px;font-weight:700;color:{INK}">{e(h)}</h3></div>'
                 f'<p style="font-size:23px;line-height:1.45;color:{SUB}">{e(s)}</p><div style="flex:1"></div>'
                 f'<p style="font-size:24px;color:#6A7180">{page[a]}–{page[b]}쪽</p></div>')
    t += ['</div>', f'<p style="font-size:26px;color:{SUB}">{page["ready"]}쪽은 노트북 준비, {page["trouble"]}–{page["cheatsheet"]}쪽은 막힐 때와 한 장 요약이에요.</p>']
    with open(os.path.join(OUT, "toc.html"), "w") as f:
        f.write("\n".join(t) + f"\n<aside>{e(toc_note)}</aside>\n</section>\n")
    deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-05T06:00:00Z"}, "lists": "css", "title": title, "order": ORDER,
            "sections": SECTIONS,
            "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                      "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
            "designSystems": []}
    with open(os.path.join(OUT, "deck.json"), "w") as f:
        json.dump(deck, f, ensure_ascii=False, indent=2)
    print(len(ORDER), "slides")


def cover(lines, h1, sub, note, accent="#F2B27A", h1size=92):
    cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
           f'<p style="font-size:28px;font-weight:700;color:{accent};letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
           f'<h1 style="font-size:{h1size}px;font-weight:900;line-height:1.1;color:#F6F5F1">{h1}</h1>',
           f'<p style="font-size:40px;line-height:1.4;color:#BFC6D4">{sub}</p>']
    cov.append(f'<div style="position:absolute;left:900px;top:300px;width:900px;height:480px;background:#252B36;border-radius:24px;padding:44px 48px;display:flex;flex-direction:column;justify-content:center;gap:16px">')
    for line, c in lines:
        cov.append(p(f"font-family:{MONO};font-size:30px;font-weight:700;line-height:1.45;color:{c};white-space:pre", e(line)))
    cov.append('</div>')
    W("cover", cov, note, ("intro", "들어가기"))
    ORDER.append("toc")


def ready(done, prev, note):
    o = [sec("ready")] + head("들어가기", f"{prev}에서 이어서 해요", JP)
    for i, (a_, b_) in enumerate(done):
        y = 196 + i * 112
        o.append(f'<div data-build-in="rise order {min(i + 1, 4)}" style="position:absolute;left:96px;top:{y}px;width:820px;height:96px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:0 28px;display:flex;flex-direction:row;gap:22px;align-items:center">'
                 + f'<x-icon name="CheckCircle" style="width:44px;height:44px;color:{GR}"></x-icon>'
                 + p(f"flex:1;font-size:28px;font-weight:700;color:{INK}", e(a_))
                 + p(f"font-size:24px;font-weight:700;color:{GRAY};white-space:nowrap", e(b_)) + '</div>')
    o.append(f'<div data-build-in="rise order 5" style="position:absolute;left:1000px;top:196px;width:824px;height:560px;background:{CARD};border:2px solid {LINE};border-top:10px solid {JP};border-radius:20px;padding:32px 40px;display:flex;flex-direction:column;gap:30px">'
             + p(f"font-size:32px;font-weight:700;color:{INK}", "노트북 다시 열기")
             + '<div style="display:flex;flex-direction:row;gap:18px;align-items:center">' + num(1, JP, 36) + p(f"font-size:28px;color:{INK}", "VS Code로 hello-uv 폴더 열기") + '</div>'
             + '<div style="display:flex;flex-direction:row;gap:18px;align-items:center">' + num(2, JP, 36) + p(f"font-size:28px;color:{INK}", "탐색기에서") + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{JP}", NB) + p(f"font-size:28px;color:{INK}", "열기") + '</div>'
             + '<div style="display:flex;flex-direction:row;gap:18px;align-items:center">' + num(3, JP, 36) + p(f"font-size:28px;color:{INK}", "오른쪽 위 커널이 .venv인지 보기") + '</div>'
             + '<div style="display:flex;flex-direction:row;gap:18px;align-items:center">' + num(4, JP, 36) + p(f"font-size:28px;color:{INK}", "셀에 적고") + kbd("Shift+Enter", 26) + p(f"font-size:28px;color:{INK}", "로 실행") + '</div></div>')
    o.append(caption("기억이 안 나면 오른쪽에 적힌 챕터를 먼저 다시 봐요.", 880))
    W("ready", o, note)


def trouble(tr, cap, note, cmd_w=380):
    o = [sec("trouble")] + head("정리", "막히면 오류의 마지막 줄을 봐요", RED)
    o.append('<div style="position:absolute;left:96px;top:196px;width:1728px;height:724px;display:flex;flex-direction:column;gap:8px">')
    for i, (q, a_, cmd) in enumerate(tr, 1):
        o.append(f'<div data-build-in="rise order {min(i, 6)}" style="flex:1;display:flex;flex-direction:row;gap:26px;align-items:center;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:6px 30px">'
                 + num(i, RED, 30)
                 + '<div style="flex:1;display:flex;flex-direction:column;gap:2px">' + p(f"{'font-family:' + MONO + ';' if q.isascii() else ''}font-size:22px;font-weight:700;color:{INK};white-space:nowrap", e(q)) + p(f"font-size:21px;color:{SUB}", e(a_)) + '</div>'
                 + p(f"width:{cmd_w}px;flex:none;{'font-family:' + MONO + ';font-size:22px;' if cmd.isascii() else 'font-size:23px;'}font-weight:700;line-height:1.4;color:{INK};background:#EEEFF2;padding:6px 18px;border-radius:12px;white-space:pre", e(cmd)) + '</div>')
    o.append('</div>')
    o.append(caption(cap, 950))
    W("trouble", o, note, ("trouble", "정리"))


def cheatsheet(cheat, bottom, note):
    o = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
         f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>']
    for i, (k, d, c) in enumerate(cheat):
        x, y = 96 + (i % 4) * 438, 200 + (i // 4) * 290
        o.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:414px;height:264px;background:{CARD};border:2px solid {LINE};border-top:10px solid {c};border-radius:20px;padding:28px 28px;display:flex;flex-direction:column;gap:20px">'
                 + (mono(k, 26 if len(k) <= 22 else 21, c, "#F6F5F1", "align-self:flex-start") if k.isascii() else p(f"font-size:30px;font-weight:900;color:{c}", e(k))) + p(f"font-size:28px;font-weight:700;color:{INK}", d) + '</div>')
    o.append(f'<div style="position:absolute;left:96px;top:780px;width:1728px;height:210px;background:{CARD};border:2px solid {LINE};border-radius:20px;padding:24px 36px;display:flex;flex-direction:column;justify-content:center;gap:14px">'
             + "".join(p(f"font-size:30px;font-weight:700;color:{INK}", b) for b in bottom) + '</div>')
    W("cheatsheet", o, note)


def tup(vals, hi=(), color=K3, bg=K3BG, w=170, h=74, fs=26, dim=()):
    """A tuple drawn as joined slots inside round brackets."""
    o = ['<div style="display:flex;flex-direction:row;align-items:center;gap:4px">' + p(f"font-family:{MONO};font-size:{fs + 14}px;font-weight:700;color:{GRAY}", "(")]
    for i, v in enumerate(vals):
        on, off = i in hi, i in dim
        o.append(p(f"width:{w}px;height:{h}px;border-radius:12px;border:3px solid {color if on else LINE};background:{bg if on else CARD};font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:{h - 6}px;text-align:center;color:{'#B4B9C3' if off else INK};white-space:pre", e(v)))
    o.append(p(f"font-family:{MONO};font-size:{fs + 14}px;font-weight:700;color:{GRAY}", ")") + '</div>')
    return "".join(o)


def row(left, top, w, h, inner, order=None, extra=""):
    at = f' data-build-in="rise order {order}"' if order else ""
    return f'<div{at} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;display:flex;flex-direction:row;align-items:center;gap:18px;{extra}">' + inner + '</div>'


def small(t, color=SUB, size=24, w=None):
    ws = f"width:{w}px;flex:none;" if w else ""
    return p(f"{ws}font-size:{size}px;font-weight:700;color:{color};white-space:nowrap", e(t))


CV, CF, CI = "#B8E8BE", "#8FD8DE", "#F2A0A0"      # value, for, if colors on dark boxes
LV, LF, LI = GR, TEAL, RED                        # same parts on light cards


def seg(parts, size=40):
    """A line on a dark box with colored pieces: parts = [(text, color), ...]."""
    return p(f"font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.5;color:#E6E9EF;white-space:pre",
             "".join(f'<span style="color:{c}">{e(t)}</span>' for t, c in parts))


def dark(left, top, w, h, lines, attrs=""):
    return (f'<div{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:#252B36;border-radius:22px;padding:28px 40px;display:flex;flex-direction:column;justify-content:center;gap:4px">'
            + "".join(lines) + '</div>')


W_ = "#E6E9EF"



# ---------- class pictures (shared by chapters 24-26) ----------
BR, BRBG = "#9A5B13", "#FBF0E0"      # 붕어빵 (an object)
MD, MDBG = "#5B4636", "#EFE8DF"      # 틀 (the class)


def obj(name, rows, left, top, w=440, color=BR, bg=BRBG, cls="Bread", attrs="", sid=None, rh=60, empty=None, fs=28):
    """A 붕어빵 (object) drawn as a card: its name on a band, then one line per attribute.
    rows: [(attribute, value)]; value None draws an empty dashed slot. empty: text shown when there are no rows."""
    idp = f' id="{sid}"' if sid else ""
    o = [f'<div{idp}{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;background:{CARD};border:3px solid {color};border-radius:26px;display:flex;flex-direction:column;overflow:hidden">'
         + f'<div style="height:66px;flex:none;background:{color};display:flex;flex-direction:row;align-items:center;padding:0 24px;gap:14px">'
         + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:#FFFFFF", e(name))
         + '<div style="flex:1"></div>' + p(f"font-size:20px;font-weight:700;color:#FFFFFF;opacity:.85;white-space:nowrap", e(cls + " 붕어빵" if cls == "Bread" else cls)) + '</div>'
         + '<div style="padding:14px 20px;display:flex;flex-direction:column;gap:8px">']
    if not rows:
        o.append(p(f"height:{rh}px;font-size:24px;color:{GRAY};line-height:{rh}px;text-align:center", e(empty or "아직 아무것도 없어요")))
    for k, v in rows:
        miss = v is None
        o.append(f'<div style="height:{rh}px;display:flex;flex-direction:row;align-items:center;gap:14px;border-radius:12px;background:{"#FFFFFF" if miss else bg};border:2px {"dashed" if miss else "solid"} {RED if miss else LINE};padding:0 16px">'
                 + p(f"width:42%;flex:none;font-family:{MONO};font-size:{fs - 4}px;font-weight:700;color:{RED if miss else SUB};white-space:nowrap", e(k))
                 + p(f"flex:1;font-family:{MONO};font-size:{fs}px;font-weight:700;color:{RED if miss else INK};white-space:nowrap", e("없음" if miss else v)) + '</div>')
    o.append('</div></div>')
    return "".join(o)


def mold(left, top, w, h, title, lines, attrs="", sid=None, color=MD, bg=MDBG, fs=26):
    """A 붕어빵 틀 (class): a thick dashed frame with the class line on top and what it promises inside."""
    idp = f' id="{sid}"' if sid else ""
    body = "".join(p(f"font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:1.5;color:{INK};white-space:pre", e(l) if l else "&#160;") for l in lines)
    return (f'<div{idp}{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:{bg};border:6px dashed {color};border-radius:30px;padding:22px 30px;display:flex;flex-direction:column;gap:12px">'
            + '<div style="display:flex;flex-direction:row;align-items:center;gap:14px">' + p(f"font-size:22px;font-weight:700;color:#FFFFFF;background:{color};border-radius:10px;padding:4px 14px", "틀") + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{color}", e(title)) + '</div>'
            + f'<div style="display:flex;flex-direction:column">{body}</div></div>')


def pill(text, left, top, color, bg, attrs="", sid=None, fs=30):
    idp = f' id="{sid}"' if sid else ""
    return p(f"position:absolute;left:{left}px;top:{top}px;font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:1.2;color:{INK};background:{bg};border:3px solid {color};border-radius:999px;padding:8px 24px;white-space:pre", e(text), idp + attrs)


def harrow(left, top, w, color="#C9CED8", attrs="", rot=0):
    r = f"transform:rotate({rot}deg);" if rot else ""
    return f'<x-shape{attrs} kind="arrow-right" style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:30px;{r}background:{color}"></x-shape>'


def code_box(left, top, w, lines, attrs="", fs=30, h=None, pad="24px 34px"):
    """A dark code box. lines: list of seg() part lists."""
    hh = f"height:{h}px;" if h else ""
    return (f'<div{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;{hh}background:#252B36;border-radius:22px;padding:{pad};display:flex;flex-direction:column;justify-content:center;gap:2px">'
            + "".join(seg(l, fs) for l in lines) + '</div>')


def trow(left, top, w, cells, widths, order=None, head=False, h=66, color=None, fs=24):
    """One table row. cells are plain strings; code-looking cells use the mono font."""
    at = f' data-build-in="rise order {order}"' if order else ""
    bg = "#ECEAE3" if head else CARD
    bl = f"border-left:10px solid {color};" if color else ""
    inner = ""
    for c, cw in zip(cells, widths):
        code = not head and (c.isascii() or re.search(r'[A-Za-z_]\.|[\[\]"=]', c) is not None)
        inner += p(f"width:{cw}px;flex:none;font-family:{MONO if code else SANS};font-size:{fs - 2 if head else fs}px;font-weight:700;color:{GRAY if head else INK};line-height:1.3;white-space:pre-wrap", e(c))
    return (f'<div{at} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:{bg};border:2px solid {LINE};{bl}border-radius:14px;padding:0 22px;display:flex;flex-direction:row;align-items:center;gap:16px">' + inner + '</div>')


# seg colors on dark boxes
CS, CA, CM, CK = "#F2C48D", "#8FD8DE", "#B8E8BE", "#C7B8F2"   # self / argument / method name / keyword


EB1 = "1. 왜 필요한가"
EB2 = "2. 클래스 변수"
EB3 = "3. 상속"
EB4 = "4. 복사와 상속 비교"
EB5 = "5. 오류와 함정"
EB6 = "6. 실습"

B_INIT = ["class Bread:", "    def __init__(self, flavor, price):", "        self.flavor = flavor", "        self.price = price"]
B_INTRO = ["    def intro(self):", '        print(self.flavor, "붕어빵", self.price, "원")']
B = B_INIT + [""] + B_INTRO
CR, CRBG = "#2F7D6B", "#E3F2EE"     # 슈크림 붕어빵 (child class)


def tree(left, top, parent, child, pl, cl, attrs="", pw=560, cw=560, gap=120, sid=None):
    """Inheritance drawn top-down: the parent mold, an up arrow labelled 물려받기, the child mold under it."""
    o = [mold(left, top, pw, 120 + 38 * len(pl), parent, pl, attrs, fs=25)]
    y2 = top + 120 + 38 * len(pl) + gap
    o.append(f'<x-shape{attrs} kind="arrow-right" style="position:absolute;left:{left + pw // 2 - 40}px;top:{y2 - gap // 2 - 15}px;width:80px;height:30px;transform:rotate(-90deg);background:{CR}"></x-shape>')
    o.append(p(f"position:absolute;left:{left + pw // 2 + 50}px;top:{y2 - gap // 2 - 18}px;font-size:24px;font-weight:700;color:{CR}", "물려받기", attrs))
    o.append(mold(left, y2, cw, 120 + 38 * len(cl), child, cl, attrs, color=CR, bg=CRBG, fs=25))
    return "".join(o)


# ---------- cover ----------
cover([("class Bread:", "#C7B8F2"), ('    shop = "붕어빵 1호점"', "#F2C48D"), ("", W_), ("class CreamBread(Bread):", "#8FD8DE"), ("    def __init__(self, f, p, cream):", W_), ("        super().__init__(f, p)", "#B8E8BE"), ("        self.cream = cream", W_)],
      "클래스 3<br>상속과<br>클래스 변수", "틀에 새긴 값과<br>물려받는 틀",
      "클래스 마지막 챕터예요. 24에서 붕어빵 틀을 만들고, 25에서 print했을 때 보기 좋게 바꿨어요. 이번에는 두 가지를 배워요. 하나는 붕어빵마다 따로가 아니라 틀 하나에 새겨서 모두 같이 쓰는 값, 클래스 변수예요. 다른 하나는 붕어빵 틀을 물려받아 슈크림 붕어빵 틀을 만드는 상속이에요. 같은 코드를 복사하지 않고 다른 점만 적는 방법이에요.", h1size=76)

ready([("class, __init__, self", "24"), ("메서드, a.intro()", "24"), ("__str__, __repr__", "25"), ("지역 변수와 전역 변수", "20"), ("for, 컴프리헨션", "13, 23")], "25",
      "09에서 만든 hello-uv 폴더를 VS Code로 열고, basics.ipynb를 다시 열어요. 24의 Bread 틀에서 이어서 해요. self와 __init__이 헷갈리면 24의 3파트를, __str__이 헷갈리면 25를 먼저 봐요. 클래스 변수를 볼 때 20의 전역 변수가 떠오를 거예요. 슬라이드의 출력은 tools/demo.sh가 hello-uv 커널에서 같은 셀을 실제로 실행한 결과예요.")

# ---------- part 1 ----------
o = [sec("w-why")] + head(EB1, "슈크림 붕어빵 틀을 새로 만들면 거의 다 복사예요", K1)
W1 = ["class Bread:", "    def __init__(self, flavor, price):", "        self.flavor = flavor", "        self.price = price", '        self.shop = "붕어빵 1호점"', "", "    def intro(self):", '        print(self.flavor, "붕어빵", self.price, "원")']
W2 = ["class CreamBread:", "    def __init__(self, flavor, price, cream):", "        self.flavor = flavor", "        self.price = price", '        self.shop = "붕어빵 1호점"', "        self.cream = cream", "", "    def intro(self):", '        print(self.flavor, "붕어빵", self.price, "원")', "", 'c = CreamBread("슈크림", 1200, "많이")', "c.intro()"]
o.append(side(96, 196, 846, 470, "원래 붕어빵 틀", W1, [], GRAY, "#F1F0EC", fs=23))
o.append(side(978, 196, 846, 600, "새로 만든 슈크림 붕어빵 틀", W2, ["슈크림 붕어빵 1200 원"], K1, K1BG, ' data-build-in="rise order 1"', fs=23))
o.append(note_card(96, 700, 846, 200, "다른 건 cream 한 줄뿐이에요", "나머지는 그대로 복사했어요. intro를 고치면 두 군데를 다 고쳐야 해요.", RED, ' data-build-in="rise order 2"'))
o.append(note_card(978, 820, 846, 100, "가게 이름도 붕어빵마다 따로 들고 있어요", "", OR, ' data-build-in="rise order 3"', "padding:20px 30px"))
W("w-why", o, "슈크림 붕어빵은 크림 양이라는 칸이 하나 더 있어요. 24에서 배운 방법만으로 만들면 붕어빵 틀을 통째로 복사하고 cream 한 줄을 더해야 해요. 이 셀은 실제로 실행해서 슈크림 붕어빵이 잘 소개됐어요. 문제는 고칠 때예요. 소개 문구를 바꾸려면 두 틀을 다 고쳐야 하고, 하나를 빼먹으면 서로 달라져요. 가게 이름도 붕어빵마다 같은 값을 따로 들고 있어요. 이번 챕터의 두 가지가 이 두 문제를 풀어요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p1", "왜 필요한가"))

o = [sec("w-big")] + head(EB1, "틀에 새기는 값, 그리고 틀을 물려받는 틀", K1)
o.append(tree(96, 196, "class Bread", "class CreamBread(Bread)", ['shop = "붕어빵 1호점"  ← 틀에 새긴 값', "__init__(flavor, price)", "intro()"], ["cream  ← 더한 것만", "나머지는 물려받아요"], ' data-build-in="rise order 1"', 860, 860, 110))
o.append(obj("a", [("flavor", '"팥"'), ("price", "1000")], 1060, 196, 360, attrs=' data-build-in="rise order 2"'))
o.append(obj("b", [("flavor", '"피자"'), ("price", "1500")], 1464, 196, 360, attrs=' data-build-in="rise order 2"'))
o.append(obj("c", [("flavor", '"슈크림"'), ("price", "1200"), ("cream", '"많이"')], 1060, 560, 500, cls="CreamBread", color=CR, bg=CRBG, attrs=' data-build-in="rise order 3"'))
o.append(note_card(1060, 470 - 30, 764, 90, "a와 b는 shop을 틀에서 같이 봐요", "", K2, ' data-build-in="rise order 4"'))
o.append(note_card(1600, 560, 224, 300, "c도 붕어빵", "물려받은 틀로 찍어서 intro도, shop도 있어요.", CR, ' data-build-in="rise order 5"'))
for i, (k, d, c) in enumerate([("클래스 변수", "틀에 새겨 모두가 같이 보는 값", K2), ("상속", "틀을 물려받아 다른 점만 적기", CR)]):
    o.append(callout(96 + i * 878, 900, 850, 92, k, d, c, 6 + i, 26))
W("w-big", o, "그림으로 먼저 봐요. 붕어빵 틀에 가게 이름을 새겨 두면, 찍은 붕어빵마다 따로 들고 있지 않아도 모두 틀에서 같이 봐요. 이렇게 틀에 둔 값을 클래스 변수라고 불러요. 아래 슈크림 붕어빵 틀은 붕어빵 틀을 물려받았어요. 크림 칸만 더 적고 나머지는 모두 물려받아요. 이렇게 물려받는 걸 상속이라고 해요. 물려받은 틀로 찍은 c도 붕어빵이라서 intro와 가게 이름이 있어요.")

# ---------- part 2 ----------
o = [sec("cv-basic")] + head(EB2, "틀에 바로 적은 값은 모든 붕어빵이 같이 봐요", K2)
CV1 = ["class Bread:", '    shop = "붕어빵 1호점"', "", "    def __init__(self, flavor, price):", "        self.flavor = flavor", "        self.price = price", "", 'a = Bread("팥", 1000)', 'b = Bread("슈크림", 1200)', "print(a.shop)", "print(b.shop)", "print(Bread.shop)"]
o += cell({"id": "c-cv1", "lines": CV1, "n": 1, "out": ["붕어빵 1호점", "붕어빵 1호점", "붕어빵 1호점"]}, 96, 196, 1000, sel="c-cv1")
o.append(hl(96, 196, 1000, 1, 1, "run", 1, "self 없이"))
o.append(mold(1140, 196, 684, 150, "class Bread", ['shop = "붕어빵 1호점"'], ' data-build-in="rise order 2"'))
o.append(obj("a", [("flavor", '"팥"'), ("price", "1000")], 1140, 420, 330, attrs=' data-build-in="rise order 3"', fs=24, rh=52))
o.append(obj("b", [("flavor", '"슈크림"'), ("price", "1200")], 1494, 420, 330, attrs=' data-build-in="rise order 3"', fs=24, rh=52))
o.append(note_card(1140, 660, 684, 230, "a에 없으면 틀에서 찾아요", "a에는 shop 칸이 없어요. a.shop을 꺼내면 파이썬이 a의 틀 Bread에서 찾아요.", K2, ' data-build-in="rise order 4"'))
W("cv-basic", o, "class 바로 아래, def 밖에 shop을 적었어요. self.이 없어요. 이렇게 틀에 적은 값을 클래스 변수라고 해요. 붕어빵 a와 b에는 shop 칸이 없지만 a.shop을 꺼내면 붕어빵 1호점이 나와요. 파이썬은 붕어빵에서 먼저 찾고, 없으면 그 붕어빵을 찍은 틀에서 찾아요. 틀 이름으로 Bread.shop이라고 꺼내도 같은 값이에요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p2", "클래스 변수"))

o = [sec("cv-change")] + head(EB2, "틀의 값을 바꾸면 모든 붕어빵에 한 번에 바뀌어요", K2)
o += cell({"id": "c-cv2", "lines": ['Bread.shop = "붕어빵 2호점"', "print(a.shop)", "print(b.shop)"], "n": 2, "out": ["붕어빵 2호점", "붕어빵 2호점"]}, 96, 196, 1000, sel="c-cv2")
o.append(mold(1140, 196, 684, 150, "class Bread", ['shop = "붕어빵 2호점"'], ' data-build-in="rise order 1"'))
o.append(note_card(96, 500, 846, 330, "한 줄로 모두", "붕어빵이 100개여도 Bread.shop 한 줄만 바꾸면 돼요. 붕어빵마다 들고 있었다면 100번 바꿔야 해요.", K2, ' data-build-in="rise order 2"'))
o.append(note_card(978, 500, 846, 330, "바꿀 땐 틀 이름으로", "Bread.shop = 처럼 틀 이름으로 바꿔요. a.shop = 으로 바꾸면 다르게 돼요(5파트).", RED, ' data-build-in="rise order 3"'))
W("cv-change", o, "가게를 옮겼어요. Bread.shop 한 줄만 바꿨는데 a와 b 모두 2호점이 나와요. 붕어빵들이 각자 들고 있는 게 아니라 틀 하나를 같이 보고 있기 때문이에요. 1파트의 복사한 코드처럼 붕어빵마다 self.shop을 따로 넣었다면 붕어빵 수만큼 바꿔야 했어요. 클래스 변수를 바꿀 땐 꼭 틀 이름으로 바꿔요. 붕어빵 이름으로 바꾸면 어떻게 되는지는 5파트에서 봐요." + REAL)

o = [sec("cv-count")] + head(EB2, "찍을 때마다 틀에 개수를 세요", K2)
CV3 = ["class Bread:", "    count = 0", "", "    def __init__(self, flavor, price):", "        self.flavor = flavor", "        self.price = price", "        Bread.count = Bread.count + 1", "", 'a = Bread("팥", 1000)', 'b = Bread("슈크림", 1200)', 'c = Bread("피자", 1500)', "print(Bread.count)"]
o += cell({"id": "c-cv3", "lines": CV3, "n": 3, "out": ["3"]}, 96, 196, 1100, sel="c-cv3")
o.append(hl(96, 196, 1100, 6, 1, "run", 1, "틀의 값 +1"))
o += table(1240, 196, 584, [("찍은 줄", 300), ("Bread.count", 200)], [["처음", "0"], ['Bread("팥", ...)', "1"], ['Bread("슈크림", ...)', "2"], ['Bread("피자", ...)', "3"]], 2, K2)
o.append(note_card(1240, 560, 584, 300, "언제 쓰나요", "가게 이름, 전체 개수, 도장 목표 개수처럼 붕어빵 하나가 아니라 틀 전체에 하나만 있으면 되는 값이에요.", K2, ' data-build-in="rise order 6"'))
W("cv-count", o, "클래스 변수로 지금까지 찍은 붕어빵 수를 세요. count는 틀에 0으로 시작하고, __init__ 안에서 Bread.count에 1을 더해요. 24에서 본 것처럼 __init__은 찍을 때마다 불리니까, 세 번 찍으면 3이 돼요. 붕어빵 하나하나가 아니라 틀 전체에 하나만 있으면 되는 값에 클래스 변수를 써요. 더할 때도 self.count가 아니라 Bread.count로 적은 걸 보세요. 이유는 5파트에서 봐요." + REAL)

o = [sec("cv-table")] + head(EB2, "클래스 변수와 인스턴스 변수", K2)
CW = [360, 680, 640]
o.append(trow(96, 196, 1728, ["", "인스턴스 변수", "클래스 변수"], CW, head=True))
for i, r in enumerate([["어디에 적나요", "__init__ 안, self.flavor = ...", 'class 바로 아래, shop = ...'],
                       ["누구 것인가요", "붕어빵 하나하나 (객체)", "틀 하나 (클래스)"],
                       ["몇 개 있나요", "붕어빵 수만큼", "틀에 하나"],
                       ["꺼내기", "a.flavor", "a.shop, Bread.shop"],
                       ["바꾸기", "a.flavor = ...", "Bread.shop = ..."],
                       ["예", "맛, 가격, 도장 수", "가게 이름, 전체 개수"]]):
    o.append(trow(96, 276 + i * 92, 1728, r, CW, order=1 + i, h=80, fs=26))
o.append(caption("인스턴스는 객체와 같은 말이에요. 붕어빵마다 다르면 self.이름, 모두 같으면 틀에 적어요.", 860))
W("cv-table", o, "두 가지 변수를 표로 비교해요. 24에서 self.flavor처럼 붕어빵에 붙인 값은 인스턴스 변수예요. 인스턴스는 객체와 같은 말로, 틀로 찍은 붕어빵 하나를 뜻해요. 붕어빵 수만큼 따로 있어요. 틀에 바로 적은 shop은 클래스 변수예요. 틀에 하나만 있고 모두가 같이 봐요. 20의 지역 변수, 전역 변수와 비슷하게 보이지만, 클래스 변수는 틀 안에 묶여 있어요. 붕어빵마다 다른 값이면 self.이름으로, 모두 같은 값이면 틀에 적어요.")

# ---------- part 3 ----------
o = [sec("in-pass")] + head(EB3, "괄호에 부모 틀을 적으면 전부 물려받아요", K3)
IP = B + ["", "class CreamBread(Bread):", "    pass", "", 'c = CreamBread("슈크림", 1200)', "c.intro()", "print(c.flavor)"]
o += cell({"id": "c-i1", "lines": IP, "n": 1, "out": ["슈크림 붕어빵 1200 원", "슈크림"]}, 96, 196, 1100, sel="c-i1")
o.append(hl(96, 196, 1100, 8, 2, "run", 1, "물려받기"))
o.append(tree(1240, 196, "Bread", "CreamBread(Bread)", ["__init__", "intro"], ["pass (비어 있어요)"], ' data-build-in="rise order 2"', 584, 584, 110))
o.append(note_card(1240, 690, 584, 220, "부모와 자식", "물려주는 Bread를 부모 클래스, 물려받는 CreamBread를 자식 클래스라고 불러요.", CR, ' data-build-in="rise order 3"'))
W("in-pass", o, "상속은 class 이름 뒤 괄호에 물려받을 틀을 적으면 돼요. CreamBread 안에는 pass만 있어서 아무것도 적지 않았어요. 그런데도 슈크림과 1200을 넣어 찍을 수 있고, intro도 불러져요. 부모 틀 Bread의 __init__과 intro를 그대로 물려받았기 때문이에요. 물려주는 틀을 부모 클래스, 물려받는 틀을 자식 클래스라고 불러요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p3", "상속"))

o = [sec("in-add")] + head(EB3, "자식 틀에는 더 할 일을 적어요", K3)
IA = ["class CreamBread(Bread):", "    def keep(self):", '        print(self.flavor, "붕어빵은 차갑게 보관해요")', "", 'a = Bread("팥", 1000)', 'c = CreamBread("슈크림", 1200)', "c.intro()", "c.keep()"]
o += cell({"id": "c-i2", "lines": IA, "n": 2, "out": ["슈크림 붕어빵 1200 원", "슈크림 붕어빵은 차갑게 보관해요"]}, 96, 196, 1100, sel="c-i2")
o += cell({"id": "c-i3", "lines": ["a.keep()"], "n": 3, "out": ["AttributeError: 'Bread' object has no attribute 'keep'"], "err": True, "attrs": ' data-build-in="rise order 2"'}, 96, 640, 1100, sel="c-i3")
o.append(hl(96, 196, 1100, 1, 2, "run", 1, "자식에만"))
o.append(note_card(1240, 196, 584, 330, "물려받은 것 + 더한 것", "c는 부모의 intro와 자식의 keep을 둘 다 써요.", CR, ' data-build-in="rise order 1"'))
o.append(note_card(1240, 556, 584, 300, "부모는 자식 것을 몰라요", "팥 붕어빵 a에는 keep이 없어요. 물려받는 건 부모에서 자식 쪽으로만이에요.", RED, ' data-build-in="rise order 3"'))
W("in-add", o, "자식 틀에 새 메서드를 더해요. 슈크림 붕어빵만 차갑게 보관하라는 안내가 필요해서 keep을 적었어요. c는 부모에게 물려받은 intro와 자기 틀의 keep을 둘 다 쓸 수 있어요. 앞 셀의 Bread 틀을 그대로 쓰고 있어요. 반대로 팥 붕어빵 a는 부모 틀 Bread로 찍어서 keep이 없어요. 물려받기는 부모에서 자식 쪽으로만 일어나요." + REAL)

o = [sec("in-super")] + head(EB3, "칸을 더할 땐 super().__init__으로 부모에게 맡겨요", K3)
IS = ["class CreamBread(Bread):", "    def __init__(self, flavor, price, cream):", "        super().__init__(flavor, price)", "        self.cream = cream", "", 'c = CreamBread("슈크림", 1200, "많이")', "print(c.flavor, c.price, c.cream)"]
o += cell({"id": "c-i4", "lines": IS, "n": 4, "out": ["슈크림 1200 많이"]}, 96, 196, 1100, sel="c-i4")
o.append(hl(96, 196, 1100, 2, 1, "run", 1, "부모가 하던 일"))
o.append(hl(96, 196, 1100, 3, 1, "mark", 2, "더한 칸"))
o.append(obj("c", [("flavor", '"슈크림"'), ("price", "1200"), ("cream", '"많이"')], 1240, 196, 584, cls="CreamBread", color=CR, bg=CRBG, attrs=' data-build-in="rise order 3"'))
o.append(callout(96, 560, 1728, 100, "super()", "부모 틀을 가리켜요. 영어로 \"위의\"라는 뜻이에요", CR, 4, 27))
o.append(callout(96, 674, 1728, 100, ".__init__(flavor, price)", "부모의 __init__에 맛과 가격을 넣어요. self는 적지 않아요", K3, 5, 27))
o.append(callout(96, 788, 1728, 100, "self.cream = cream", "자식만 가진 칸은 자식이 직접 붙여요", BR, 6, 27))
W("in-super", o, "슈크림 붕어빵에는 cream 칸이 하나 더 있어요. 그래서 자식 틀에 __init__을 새로 적어야 해요. 맛과 가격을 붙이는 일은 부모의 __init__이 이미 하고 있으니 다시 적지 않고 맡겨요. super()는 부모 틀을 가리켜서, super().__init__(flavor, price)는 부모의 __init__에 맛과 가격을 넣어 부르는 줄이에요. 24의 a.intro()처럼 self는 적지 않아요. 부모가 맛과 가격을 붙인 뒤, 자식은 cream만 직접 붙여요." + REAL)

o = [sec("in-super2")] + head(EB3, "CreamBread(\"슈크림\", 1200, \"많이\") 한 줄에서 일어나는 일", K3)
ST5 = [("①", "CreamBread.__init__", "자식의 __init__이 불려요. self는 새 붕어빵"),
       ("②", "super().__init__(flavor, price)", "부모의 __init__으로 가요. 같은 self예요"),
       ("③", "self.flavor, self.price", "부모가 맛과 가격 칸을 붙여요"),
       ("④", "self.cream = cream", "자식으로 돌아와 크림 칸을 붙여요"),
       ("⑤", "c = 다 된 붕어빵", "세 칸이 다 붙은 붕어빵이 c에 담겨요")]
for i, (n_, code, what) in enumerate(ST5):
    o.append(f'<div id="stp-{i + 1}" data-build-in="rise order {i + 1}" style="position:absolute;left:96px;top:{196 + i * 140}px;width:1160px;height:124px;background:{CARD};border:2px solid {LINE};border-left:10px solid {CR if i != 2 else MD};border-radius:16px;padding:0 26px;display:flex;flex-direction:column;justify-content:center;gap:6px">'
             + '<div style="display:flex;flex-direction:row;gap:18px;align-items:center">' + p(f"font-size:32px;font-weight:900;color:{CR}", e(n_)) + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{INK};white-space:pre", e(code)) + '</div>'
             + p(f"padding-left:52px;font-size:26px;color:{SUB}", e(what)) + '</div>')
o.append(obj("self", [], 1320, 196, 504, cls="CreamBread", color=CR, bg=CRBG, empty="아직 칸이 없어요", attrs=' data-build-in="rise order 1"'))
o.append(obj("self", [("flavor", '"슈크림"'), ("price", "1200")], 1320, 196, 504, cls="CreamBread", color=CR, bg=CRBG, attrs=' data-build-in="fly order 3" data-from="stp-3"'))
o.append(obj("self", [("flavor", '"슈크림"'), ("price", "1200"), ("cream", '"많이"')], 1320, 196, 504, cls="CreamBread", color=CR, bg=CRBG, attrs=' data-build-in="fly order 4" data-from="stp-4"'))
o.append(obj("c", [("flavor", '"슈크림"'), ("price", "1200"), ("cream", '"많이"')], 1320, 196, 504, cls="CreamBread", color=CR, bg=CRBG, attrs=' data-build-in="fly order 5" data-from="stp-5"'))
o.append(note_card(1320, 560, 504, 320, "self는 하나예요", "부모의 __init__에서도 자식의 __init__에서도 같은 새 붕어빵이에요.", CR, ' data-build-in="rise order 6"'))
W("in-super2", o, "24의 다섯 단계 그림처럼 이 줄을 나눠 봐요. 찍으면 자식의 __init__이 먼저 불려요. 첫 줄에서 super().__init__을 만나 부모의 __init__으로 가요. 부모가 같은 self에 맛과 가격 칸을 붙이고 돌아오면, 자식이 크림 칸을 붙여요. 오른쪽 그림에서 칸이 늘어나는 걸 보세요. 부모의 __init__과 자식의 __init__에서 self는 같은 붕어빵 하나예요.")

o = [sec("in-over")] + head(EB3, "같은 이름의 메서드를 다시 적으면 자식 것이 쓰여요", K3)
IO = ["class CreamBread(Bread):", "    def __init__(self, flavor, price, cream):", "        super().__init__(flavor, price)", "        self.cream = cream", "", "    def intro(self):", '        print(self.flavor, "붕어빵", self.price, "원, 크림", self.cream)', "", 'a = Bread("팥", 1000)', 'c = CreamBread("슈크림", 1200, "많이")', "a.intro()", "c.intro()"]
o += cell({"id": "c-i5", "lines": IO, "n": 5, "out": ["팥 붕어빵 1000 원", "슈크림 붕어빵 1200 원, 크림 많이"]}, 96, 196, 1240, sel="c-i5")
o.append(hl(96, 196, 1240, 5, 2, "run", 1, "덮어쓰기"))
o.append(note_card(1380, 196, 444, 330, "자식부터 찾아요", "c.intro()는 CreamBread에 intro가 있어서 그걸 써요.", CR, ' data-build-in="rise order 2"'))
o.append(note_card(1380, 556, 444, 330, "없으면 부모에서", "a는 Bread로 찍었으니 원래 intro예요.", MD, ' data-build-in="rise order 3"'))
W("in-over", o, "부모에게 물려받은 메서드와 같은 이름으로 자식 틀에 다시 적으면, 자식 것이 쓰여요. 이걸 덮어쓰기라고 해요. 슈크림 붕어빵은 크림 양까지 소개하도록 intro를 다시 적었어요. 파이썬은 메서드를 찾을 때 자식 틀부터 보고, 없으면 부모 틀로 올라가요. c는 자식 틀에 intro가 있어서 그걸 쓰고, a는 부모 틀로 찍었으니 원래 intro를 써요." + REAL)

o = [sec("in-super3")] + head(EB3, "부모 것을 부르고 조금만 더할 수도 있어요", K3)
IS3 = ["class CreamBread(Bread):", "    def __init__(self, flavor, price, cream):", "        super().__init__(flavor, price)", "        self.cream = cream", "", "    def intro(self):", "        super().intro()", '        print("  크림:", self.cream)', "", 'c = CreamBread("슈크림", 1200, "많이")', "c.intro()"]
o += cell({"id": "c-i6", "lines": IS3, "n": 6, "out": ["슈크림 붕어빵 1200 원", "  크림: 많이"]}, 96, 196, 1100, sel="c-i6")
o.append(hl(96, 196, 1100, 6, 1, "run", 1, "부모의 intro"))
o.append(hl(96, 196, 1100, 7, 1, "mark", 2, "더한 줄"))
o.append(note_card(1240, 196, 584, 330, "같은 문구를 두 번 안 적어요", "소개 문구는 부모 intro에만 있어요. 부모를 고치면 자식도 같이 바뀌어요.", CR, ' data-build-in="rise order 3"'))
o.append(note_card(1240, 556, 584, 300, "__init__과 같은 모양", "super().__init__처럼 super().intro()로 부모 메서드를 불러요.", GRAY, ' data-build-in="rise order 4"'))
W("in-super3", o, "앞 장처럼 intro를 통째로 다시 적으면 소개 문구가 두 군데에 생겨요. 부모의 intro를 그대로 부르고 한 줄만 더하고 싶을 땐 super().intro()를 써요. __init__에서 super().__init__을 부른 것과 같은 모양이에요. 이렇게 하면 소개 문구는 부모 틀에만 있어서, 부모를 고치면 자식도 같이 바뀌어요. 1파트에서 본 두 군데 고치기 문제가 풀려요." + REAL)

o = [sec("in-list")] + head(EB3, "섞어 담아도 붕어빵마다 자기 intro를 불러요", K3)
o += cell({"id": "c-i7", "lines": ['order = [Bread("팥", 1000), CreamBread("슈크림", 1200, "보통"), Bread("피자", 1500)]', "for b in order:", "    b.intro()"], "n": 7, "out": ["팥 붕어빵 1000 원", "슈크림 붕어빵 1200 원", "  크림: 보통", "피자 붕어빵 1500 원"]}, 96, 196, 1728, sel="c-i7")
o += cell({"id": "c-i8", "lines": ["print(isinstance(c, CreamBread))", "print(isinstance(c, Bread))", "print(isinstance(a, CreamBread))"], "n": 8, "out": ["True", "True", "False"], "attrs": ' data-build-in="rise order 2"'}, 96, 560, 900, sel="c-i8")
o.append(note_card(1040, 560, 784, 340, "isinstance(값, 틀)", "그 틀(또는 그 틀의 자식)로 찍었는지 True, False로 알려 줘요. 슈크림 붕어빵도 붕어빵이라 Bread에 True예요.", CR, ' data-build-in="rise order 3"'))
W("in-list", o, "팥, 슈크림, 피자 붕어빵을 한 리스트에 섞어 담았어요. for로 하나씩 b.intro()를 부르면 붕어빵마다 자기 틀의 intro가 불려요. 슈크림 붕어빵만 크림 줄이 더 나와요. 부르는 쪽은 어떤 붕어빵인지 몰라도 돼요. 어떤 틀로 찍었는지 알고 싶으면 isinstance를 써요. 슈크림 붕어빵은 CreamBread이면서 Bread이기도 해서 둘 다 True예요. 팥 붕어빵 a는 CreamBread가 아니라서 False예요." + REAL)

# ---------- 메서드 찾기: a slide students press in the browser (tools/lab_find.js) ----------
LF_CSS = ("<style>"
          "#in-lab button{font-family:" + MONO.replace("'", '"') + ";font-size:25px;font-weight:700;border-radius:14px;padding:8px 18px;cursor:pointer;border:3px solid #C9CED8;background:#FFFFFF;color:#1D2330}"
          "#in-lab button:disabled{opacity:.5;cursor:default}"
          "#in-lab button.lf-on{border-color:#2F7D6B;background:#E3F2EE}"
          "#in-lab #lf-go{font-family:" + SANS.replace("'", '"') + ";background:#2F7D6B;border-color:#2F7D6B;color:#FFFFFF}"
          "#in-lab code{font-family:" + MONO.replace("'", '"') + ";font-size:24px;background:#F1F0EC;border-radius:8px;padding:1px 8px}"
          "#in-lab .lf-box{transition:box-shadow .3s,opacity .3s}"
          "#in-lab .lf-look{box-shadow:0 0 0 8px rgba(178,106,0,.45)}"
          "#in-lab .lf-box.lf-yes{box-shadow:0 0 0 8px rgba(31,138,76,.40)}"
          "#in-lab .lf-box.lf-no{opacity:.55}"
          "#in-lab .lf-row{transition:all .3s;border:2px solid transparent}"
          "#in-lab .lf-row.lf-yes{background:#D7F0DF!important;border-color:#1F8A4C}"
          "#in-lab .lf-row.lf-super{background:#FFF1D9!important;border-color:#B26A00}"
          "@keyframes lfIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}"
          "</style>")


def lf_row(sid, txt, fs=23):
    return (f'<div id="{sid}" class="lf-row" style="height:50px;border-radius:10px;background:#FFFFFF;padding:0 14px;display:flex;align-items:center">'
            + p(f"font-family:{MONO};font-size:{fs}px;font-weight:700;color:{INK};white-space:pre", e(txt)) + '</div>')


def lf_mold(sid, left, top, title, rows, color, bg):
    return (f'<div id="{sid}" class="lf-box" style="position:absolute;left:{left}px;top:{top}px;width:620px;background:{bg};border:5px dashed {color};border-radius:26px;padding:16px 22px;display:flex;flex-direction:column;gap:8px">'
            + '<div style="display:flex;flex-direction:row;align-items:center;gap:12px">' + p(f"font-size:20px;font-weight:700;color:#FFFFFF;background:{color};border-radius:10px;padding:3px 12px", "틀") + p(f"font-family:{MONO};font-size:27px;font-weight:700;color:{color}", e(title)) + '</div>'
            + "".join(lf_row(f"{sid}-{k}", t) for k, t in rows) + '</div>')


def lf_obj(name, cls, rows, left, top, color):
    return (f'<div id="lf-o-{name}" class="lf-box" style="position:absolute;left:{left}px;top:{top}px;width:300px;background:{CARD};border:3px solid {color};border-radius:22px;overflow:hidden">'
            + f'<div style="height:56px;background:{color};display:flex;align-items:center;padding:0 18px;gap:10px">' + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:#FFFFFF", e(name)) + '<div style="flex:1"></div>' + p("font-size:18px;font-weight:700;color:#FFFFFF;opacity:.85", e(cls)) + '</div>'
            + '<div style="padding:10px 14px;display:flex;flex-direction:column;gap:6px">' + "".join(lf_row(f"lf-o-{name}-{k}", f"{k}  {v}", 21) for k, v in rows) + '</div></div>')


o = [sec("in-lab"), LF_CSS] + head(EB3, "눌러 보기: 파이썬은 어디서부터 찾을까요", K3)
o.append(lf_mold("lf-m-Bread", 96, 196, "class Bread", [("shop", 'shop = "붕어빵 1호점"'), ("__init__", "__init__(self, flavor, price)"), ("intro", "intro(self)")], MD, MDBG))
o.append(f'<x-shape kind="arrow-right" style="position:absolute;left:366px;top:476px;width:80px;height:30px;transform:rotate(-90deg);background:{CR}"></x-shape>')
o.append(p(f"position:absolute;left:456px;top:472px;font-size:24px;font-weight:700;color:{CR}", "물려받기"))
o.append(lf_mold("lf-m-CreamBread", 96, 540, "class CreamBread(Bread)", [("__init__", "__init__(self, flavor, price, cream)"), ("intro", "intro(self)  # super().intro() + 크림"), ("keep", "keep(self)")], CR, CRBG))
o.append(lf_obj("a", "Bread", [("flavor", '"팥"'), ("price", "1000")], 762, 226, BR))
o.append(lf_obj("c", "CreamBread", [("flavor", '"슈크림"'), ("price", "1200"), ("cream", '"많이"')], 762, 560, CR))
o.append(p(f"position:absolute;left:762px;top:452px;width:300px;font-size:22px;color:{SUB};text-align:center", "Bread 틀로 찍었어요"))
o.append(p(f"position:absolute;left:762px;top:842px;width:300px;font-size:22px;color:{SUB};text-align:center", "CreamBread 틀로 찍었어요"))
o.append(f'<div style="position:absolute;left:1100px;top:196px;width:724px;height:286px;background:{CARD};border:2px solid {LINE};border-radius:22px;padding:18px 24px;display:flex;flex-direction:column;gap:14px">'
         + f'<div id="lf-who" style="display:flex;flex-direction:row;gap:12px;align-items:center">{p(f"width:96px;font-size:24px;font-weight:700;color:{SUB}", "누구에게")}<button data-o="a">a</button><button data-o="c">c</button></div>'
         + f'<div id="lf-what" style="display:flex;flex-direction:row;flex-wrap:wrap;gap:10px;align-items:center">{p(f"width:96px;font-size:24px;font-weight:700;color:{SUB}", "무엇을")}<button data-k="intro">.intro()</button><button data-k="keep">.keep()</button><button data-k="shop">.shop</button><button data-k="cream">.cream</button><button data-k="flavor">.flavor</button></div>'
         + f'<div style="display:flex;flex-direction:row;gap:16px;align-items:center"><button id="lf-go">찾아보기 ▶</button>{p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{INK}", "c.intro()", " id=\"lf-code\"")}</div></div>')
o.append(f'<div id="lf-log" style="position:absolute;left:1100px;top:502px;width:724px;height:236px;background:{CARD};border:2px solid {LINE};border-radius:22px;padding:18px 24px;display:flex;flex-direction:column;gap:6px">'
         + p(f"font-size:25px;color:{GRAY}", "찾는 길이 여기에 한 줄씩 나와요.") + '</div>')
o.append(f'<div style="position:absolute;left:1100px;top:758px;width:724px;height:150px;background:{CARD};border:2px solid {LINE};border-left:10px solid {JP};border-radius:22px;padding:16px 24px;display:flex;flex-direction:column;gap:8px">'
         + p(f"font-size:24px;font-weight:700;color:{JP}", "출력") + p(f"font-family:{MONO};font-size:22px;font-weight:700;line-height:1.4;color:{INK};white-space:pre-wrap;overflow-wrap:break-word", "", ' id="lf-out"') + '</div>')
o.append(f'<div style="position:absolute;left:96px;top:930px;width:1728px;height:106px;background:{CARD};border:2px solid {LINE};border-left:10px solid {CR};border-radius:18px;padding:0 30px;display:flex;align-items:center">'
         + p(f"font-size:30px;font-weight:500;line-height:1.4;color:{INK}", "누구에게 무엇을 물을지 고르고 찾아보기를 눌러요. 브라우저로 슬라이드를 열면 눌러져요.", ' id="lf-msg"') + '</div>')
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lab_find.js")) as f:
    o.append('<script type="text/slide-js">\n' + f.read() + '</script>')
W("in-lab", o, "메서드와 값을 어디서 찾는지 직접 눌러 보는 장이에요. 브라우저로 슬라이드를 열면 버튼이 눌러져요. 붕어빵과 물을 것을 고르고 찾아보기를 누르면 파이썬이 찾는 순서대로 불이 들어와요. 먼저 붕어빵 자신, 다음은 그 붕어빵을 찍은 틀, 그다음은 부모 틀이에요. c.intro()는 자식 틀에서 찾고, 안에서 super().intro()로 부모 것도 불러요. c.shop은 부모 틀까지 올라가서 찾아요. a.keep()은 부모 틀 Bread에서 끝나서 AttributeError가 나요. 자식 틀은 보지 않기 때문이에요. 누르기 전에 어디서 찾을지 수강생에게 먼저 물어보세요. 출력은 tools/demo.sh로 실제로 실행한 결과예요.")

# ---------- part 4 ----------
o = [sec("cmp-copy")] + head(EB4, "복사해서 만든 틀 vs 물려받은 틀", K4)
o.append(side(96, 196, 846, 470, "복사 (1파트)", ["class CreamBread:", "    def __init__(self, flavor, price, cream):", "        self.flavor = flavor", "        self.price = price", "        self.cream = cream", "", "    def intro(self):", '        print(self.flavor, ...)'], [], GRAY, "#F1F0EC", fs=23))
o.append(side(978, 196, 846, 470, "상속 (3파트)", ["class CreamBread(Bread):", "    def __init__(self, flavor, price, cream):", "        super().__init__(flavor, price)", "        self.cream = cream", "", "    def intro(self):", "        super().intro()", '        print("  크림:", self.cream)'], [], CR, CRBG, ' data-build-in="rise order 1"', fs=23))
CW = [360, 660, 660]
o.append(trow(96, 700, 1728, ["", "복사", "상속"], CW, head=True))
for i, r in enumerate([["부모를 고치면", "두 군데 다 고쳐야 해요", "자식도 같이 바뀌어요"], ["적는 것", "모든 줄", "다른 점만"]]):
    o.append(trow(96, 780 + i * 90, 1728, r, CW, order=2 + i, h=78, fs=26))
W("cmp-copy", o, "1파트의 복사한 틀과 3파트의 물려받은 틀을 나란히 놓았어요. 복사한 틀은 맛과 가격을 붙이는 줄, 소개 문구를 모두 다시 적었어요. 물려받은 틀은 크림과 관련된 줄만 적고 나머지는 부모에게 맡겼어요. 붕어빵 틀의 소개 문구를 바꾸면 물려받은 틀도 같이 바뀌어요. 다른 점만 적으면 돼서 코드가 짧고, 고칠 곳이 한 군데예요.")

o = [sec("cmp-when")] + head(EB4, "\"~는 ~의 한 종류\"일 때 상속해요", K4)
for i, (q, ok, a_) in enumerate([("슈크림 붕어빵은 붕어빵의 한 종류예요", True, "CreamBread(Bread)"), ("미니 붕어빵은 붕어빵의 한 종류예요", True, "MiniBread(Bread)"), ("VIP 카드는 도장 카드의 한 종류예요", True, "VipCard(Card)"),
                                 ("붕어빵 노점은 붕어빵의 한 종류가 아니에요", False, "Stall 틀을 따로 만들어요 (25)"), ("음료는 붕어빵의 한 종류가 아니에요", False, "Drink 틀을 따로 만들어요")]):
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:96px;top:{196 + i * 124}px;width:1728px;height:108px;background:{CARD};border:2px solid {LINE};border-left:10px solid {GR if ok else RED};border-radius:16px;padding:0 28px;display:flex;flex-direction:row;align-items:center;gap:24px">'
             + p(f"width:80px;flex:none;font-size:30px;font-weight:900;color:{GR if ok else RED}", "상속" if ok else "따로")
             + p(f"flex:1;font-size:30px;font-weight:700;color:{INK}", e(q))
             + p(f"font-family:{MONO if a_.isascii() else SANS};font-size:26px;font-weight:700;color:{SUB};white-space:nowrap", e(a_)) + '</div>')
o.append(caption("코드가 비슷해 보여도 한 종류가 아니면 상속하지 않아요.", 850))
W("cmp-when", o, "상속은 언제 쓸까요? 자식이 부모의 한 종류일 때예요. 슈크림 붕어빵과 미니 붕어빵은 붕어빵의 한 종류라서 붕어빵 틀을 물려받아요. VIP 카드도 도장 카드의 한 종류예요. 붕어빵 노점은 붕어빵이 아니에요. 노점은 붕어빵을 파는 곳이라서, 25처럼 Stall 틀을 따로 만들면 돼요. 음료도 붕어빵의 한 종류가 아니니 따로 만들어요. 소리 내어 \"~는 ~의 한 종류예요\"가 자연스러운지 읽어 보세요.")

# ---------- part 5 ----------
o = [sec("t-nosuper")] + head(EB5, "super().__init__을 빼먹으면 부모 칸이 없어요", K5)
TN = B + ["", "class CreamBread(Bread):", "    def __init__(self, flavor, price, cream):", "        self.cream = cream", "", 'c = CreamBread("슈크림", 1200, "많이")', "c.intro()"]
o += cell({"id": "c-t1", "lines": TN, "n": 1, "out": ["AttributeError: 'CreamBread' object has no attribute 'flavor'"], "err": True}, 96, 196, 1240, sel="c-t1")
o.append(hl(96, 196, 1240, 8, 2, "err", 1, "super 없음"))
o.append(obj("c", [("cream", '"많이"'), ("flavor", None), ("price", None)], 1380, 196, 444, cls="CreamBread", color=CR, bg=CRBG, attrs=' data-build-in="rise order 2"'))
o.append(note_card(1380, 520, 444, 360, "고치기", "자식 __init__ 첫 줄에 super().__init__(flavor, price)를 적어요.", GR, ' data-build-in="rise order 3"'))
W("t-nosuper", o, "자식 틀에 __init__을 새로 적으면 부모의 __init__은 저절로 불리지 않아요. 3파트의 덮어쓰기와 같아요. 자식 __init__에서 cream만 붙이고 super().__init__을 빼먹어서, 맛과 가격 칸이 없는 붕어빵이 찍혔어요. 찍을 때는 아무 말이 없다가 intro에서 self.flavor를 꺼낼 때 AttributeError가 나요. 자식 __init__의 첫 줄에 super().__init__을 적어요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p5", "오류와 함정"))

o = [sec("t-superself")] + head(EB5, "super().__init__에 self를 넣으면 4 were given", K5)
o += cell({"id": "c-t2", "lines": ["class CreamBread(Bread):", "    def __init__(self, flavor, price, cream):", "        super().__init__(self, flavor, price)", "        self.cream = cream", "", 'c = CreamBread("슈크림", 1200, "많이")'], "n": 2, "out": ["TypeError: Bread.__init__() takes 3 positional arguments but 4 were given"], "err": True}, 96, 196, 1500, sel="c-t2")
o.append(hl(96, 196, 1500, 2, 1, "err", 1, "self가 두 번"))
o.append(note_card(96, 560, 846, 300, "읽는 법", "부모 __init__은 칸이 3개(self, flavor, price)인데 4개가 들어왔어요. self를 파이썬이 이미 넣었어요.", RED, ' data-build-in="rise order 2"'))
o.append(note_card(978, 560, 846, 300, "고치기", "super().__init__(flavor, price). a.intro()에 self를 안 적는 것과 같아요.", GR, ' data-build-in="rise order 3"'))
W("t-superself", o, "super().__init__ 괄호에 self를 같이 적었어요. 부모의 __init__은 self, flavor, price 세 칸인데 네 개가 들어왔다는 TypeError예요. super()로 부를 때도 a.intro()처럼 파이썬이 self를 알아서 넣어 줘요. 그래서 우리가 적은 self까지 합쳐 네 개가 됐어요. super().__init__(flavor, price)처럼 self 없이 적어요." + REAL)

o = [sec("t-cream")] + head(EB5, "자식 틀은 재료가 하나 더 필요해요", K5)
o += cell({"id": "c-t3", "lines": ["class CreamBread(Bread):", "    def __init__(self, flavor, price, cream):", "        super().__init__(flavor, price)", "        self.cream = cream", "", 'c = CreamBread("슈크림", 1200)'], "n": 3, "out": ["TypeError: CreamBread.__init__() missing 1 required positional argument: 'cream'"], "err": True}, 96, 196, 1500, sel="c-t3")
o.append(hl(96, 196, 1500, 5, 1, "err", 1, "cream이 없어요"))
o.append(note_card(96, 560, 846, 300, "읽는 법", "찍을 때 불리는 건 자식의 __init__이에요. 자식은 cream까지 3개가 필요해요.", RED, ' data-build-in="rise order 2"'))
o.append(note_card(978, 560, 846, 300, "고치기", 'CreamBread("슈크림", 1200, "많이")처럼 자식 __init__의 칸 수에 맞춰요. 기본값(20)으로 cream="보통"을 둘 수도 있어요.', GR, ' data-build-in="rise order 3"'))
W("t-cream", o, "부모 틀처럼 맛과 가격만 넣어 찍었더니 cream이 모자라다는 TypeError가 나요. 자식 틀에 __init__을 새로 적었으니 찍을 때 불리는 건 자식의 __init__이에요. 자식 __init__의 칸 수에 맞춰 재료를 넣어요. 크림을 자주 안 적는다면 20에서 배운 기본값으로 cream=\"보통\"을 둘 수도 있어요." + REAL)

o = [sec("t-shop")] + head(EB5, "a.shop = 으로 바꾸면 a에만 새 칸이 생겨요", K5)
TS = ["class Bread:", '    shop = "붕어빵 1호점"', "", "    def __init__(self, flavor, price):", "        self.flavor = flavor", "        self.price = price", "", 'a = Bread("팥", 1000)', 'b = Bread("슈크림", 1200)', 'a.shop = "옆 가게"', "print(a.shop)", "print(b.shop)", "print(Bread.shop)"]
o += cell({"id": "c-t4", "lines": TS, "n": 4, "out": ["옆 가게", "붕어빵 1호점", "붕어빵 1호점"]}, 96, 196, 1000, sel="c-t4")
o.append(hl(96, 196, 1000, 9, 1, "err", 1, "a에 붙이기"))
o.append(mold(1140, 196, 684, 150, "class Bread", ['shop = "붕어빵 1호점"'], ' data-build-in="rise order 2"'))
o.append(obj("a", [("flavor", '"팥"'), ("shop", '"옆 가게"')], 1140, 400, 330, attrs=' data-build-in="rise order 3"', fs=24, rh=52))
o.append(obj("b", [("flavor", '"슈크림"')], 1494, 400, 330, attrs=' data-build-in="rise order 3"', fs=24, rh=52))
o.append(note_card(1140, 660, 684, 230, "오류는 안 나요", "24에서 손으로 칸을 붙인 것과 같아요. 틀의 값은 그대로예요. 모두 바꾸려면 Bread.shop =", RED, ' data-build-in="rise order 4"'))
W("t-shop", o, "클래스 변수를 붕어빵 이름으로 바꿨어요. 오류는 나지 않지만, 틀의 값이 바뀌는 게 아니라 a에만 shop이라는 새 칸이 붙어요. 24의 2파트에서 점으로 칸을 붙인 것과 같아요. 이제 a.shop을 꺼내면 a에 붙은 칸이 먼저 보여서 옆 가게가 나오고, b와 틀은 그대로 1호점이에요. 모두의 값을 바꾸려면 Bread.shop =처럼 틀 이름으로 바꿔요." + REAL)

o = [sec("t-count")] + head(EB5, "self.count로 세면 틀의 개수가 안 늘어요", K5)
TC = ["class Bread:", "    count = 0", "", "    def __init__(self, flavor, price):", "        self.flavor = flavor", "        self.price = price", "        self.count = self.count + 1", "", 'a = Bread("팥", 1000)', 'b = Bread("슈크림", 1200)', "print(a.count, b.count)", "print(Bread.count)"]
o += cell({"id": "c-t5", "lines": TC, "n": 5, "out": ["1 1", "0"]}, 96, 196, 1100, sel="c-t5")
o.append(hl(96, 196, 1100, 6, 1, "err", 1, "self.count"))
o.append(note_card(1240, 196, 584, 360, "왼쪽과 오른쪽이 달라요", "오른쪽 self.count는 틀의 0을 읽어요. 왼쪽 self.count =은 붕어빵에 새 칸을 붙여요. 그래서 붕어빵마다 1이에요.", RED, ' data-build-in="rise order 2"'))
o.append(note_card(1240, 586, 584, 270, "고치기", "Bread.count = Bread.count + 1처럼 틀 이름으로 적어요.", GR, ' data-build-in="rise order 3"'))
W("t-count", o, "2파트의 개수 세기를 self.count로 적었어요. 오류는 없는데 Bread.count는 0이고, 붕어빵마다 1이에요. 오른쪽 self.count는 붕어빵에 count 칸이 없으니 틀의 0을 읽어요. 왼쪽 self.count =은 앞 장처럼 붕어빵에 새 칸을 붙여요. 그래서 틀의 값은 한 번도 안 바뀌어요. 20의 전역 변수에서 같은 이름에 넣으면 새 지역 변수가 생기던 것과 비슷해요. 틀의 값을 바꿀 땐 Bread.count처럼 틀 이름으로 적어요." + REAL)

# ---------- part 6 ----------
o = [sec("x-card")] + head(EB6, "도장 카드 ①: 틀에 가게와 목표, VIP는 두 배로", K6)
XC = ["class Card:", '    shop = "KANT 카페"', "    goal = 10", "", "    def __init__(self, name):", "        self.name = name", "        self.stamps = 0", "", "    def add(self):", "        self.stamps = self.stamps + 1", "", "    def __str__(self):", "        left = Card.goal - self.stamps", '        return f"[{Card.shop}] {self.name}: 도장 {self.stamps}개, {left}개 남음"', "", "class VipCard(Card):", "    def add(self):", "        self.stamps = self.stamps + 2"]
o += cell({"id": "c-x1", "lines": XC, "n": 1}, 96, 176, 1500, sel="c-x1")
o.append(hl(96, 176, 1500, 1, 2, "mark", 1, "클래스 변수"))
o.append(hl(96, 176, 1500, 11, 3, "run", 2, "__str__ (25)"))
o.append(hl(96, 176, 1500, 15, 3, "err", 3, "add만 덮어쓰기"))
o.append(caption("출력이 없는 셀이에요. 틀만 만들었어요.", 900))
W("x-card", o, "24에서 만든 도장 카드를 이어서 만들어요. 가게 이름과 목표 도장 수는 모든 카드가 같아서 클래스 변수로 틀에 적었어요. __str__은 25에서 배운 대로 남은 도장 수까지 글자로 돌려줘요. VIP 카드는 도장 카드의 한 종류라서 Card를 물려받고, add만 두 개씩 찍도록 덮어썼어요. __init__과 __str__은 그대로 물려받아요. 이 셀은 틀만 만들어서 출력이 없어요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p6", "실습"))

o = [sec("x-card2")] + head(EB6, "도장 카드 ②: 같은 add인데 카드마다 다르게", K6)
o += cell({"id": "c-x2", "lines": ['kim = Card("kim")', 'lee = VipCard("lee")', "kim.add()", "kim.add()", "lee.add()", "lee.add()", "print(kim)", "print(lee)"], "n": 2, "out": ["[KANT 카페] kim: 도장 2개, 8개 남음", "[KANT 카페] lee: 도장 4개, 6개 남음"]}, 96, 196, 1100, sel="c-x2")
o.append(obj("kim", [("name", '"kim"'), ("stamps", "2")], 1240, 196, 584, cls="Card", color=BL, bg=K1BG, attrs=' data-build-in="rise order 1"'))
o.append(obj("lee", [("name", '"lee"'), ("stamps", "4")], 1240, 446, 584, cls="VipCard", color=CR, bg=CRBG, attrs=' data-build-in="rise order 2"'))
o.append(note_card(96, 700, 1728, 180, "물려받은 것과 덮어쓴 것", "두 카드 모두 add를 두 번 불렀어요. lee는 VipCard의 add로 4개, __str__과 가게 이름은 둘 다 Card에서 왔어요.", K6, ' data-build-in="rise order 3"'))
W("x-card2", o, "앞 셀의 틀로 일반 카드 kim과 VIP 카드 lee를 만들었어요. 둘 다 add를 두 번 불렀는데 kim은 2개, lee는 4개예요. lee는 VipCard 틀에 덮어쓴 add를 쓰기 때문이에요. print는 두 카드 모두 Card의 __str__을 쓰고, 가게 이름과 목표도 틀에서 같이 봐요. 부르는 쪽은 똑같이 add()라고만 적어도 카드마다 알맞게 동작해요." + REAL)

o = [sec("x-mini")] + head(EB6, "붕어빵 메뉴판 ①: 미니 붕어빵 틀을 물려받기", K6)
XM = ["class Bread:", "    count = 0", "", "    def __init__(self, flavor, price):", "        self.flavor = flavor", "        self.price = price", "        Bread.count = Bread.count + 1", "", "    def __str__(self):", '        return f"{self.flavor} 붕어빵 {self.price:,}원"', "", "class MiniBread(Bread):", "    def __init__(self, flavor, price, qty):", "        super().__init__(flavor, price)", "        self.qty = qty", "", "    def __str__(self):", '        return f"미니 {self.flavor} {self.qty}개 {self.price * self.qty:,}원"']
o += cell({"id": "c-x3", "lines": XM, "n": 3}, 96, 176, 1500, sel="c-x3")
o.append(hl(96, 176, 1500, 6, 1, "mark", 1, "개수 세기"))
o.append(hl(96, 176, 1500, 13, 1, "run", 2, "부모에게 맡기기"))
o.append(hl(96, 176, 1500, 16, 2, "err", 3, "__str__ 덮어쓰기"))
o.append(caption("이 셀도 출력이 없어요.", 940))
W("x-mini", o, "미니 붕어빵은 한 개 가격과 묶음 개수가 있어요. 미니 붕어빵도 붕어빵의 한 종류라서 Bread를 물려받았어요. 자식 __init__은 맛과 가격을 super().__init__에 맡기고 개수만 붙여요. 부모 __init__ 안에서 Bread.count가 늘어나니까 미니 붕어빵을 찍어도 개수가 세져요. __str__은 묶음 가격을 보여 주도록 덮어썼어요. 이 셀도 틀만 만들어서 출력이 없어요." + REAL)

o = [sec("x-mini2")] + head(EB6, "붕어빵 메뉴판 ②: 섞어 담고 찍고 세기", K6)
o += cell({"id": "c-x4", "lines": ['menu = [Bread("팥", 1000), MiniBread("팥", 300, 5), Bread("슈크림", 1200), MiniBread("슈크림", 400, 5)]', "for m in menu:", "    print(m)", 'print("찍은 붕어빵:", Bread.count)', "print([m.flavor for m in menu if isinstance(m, MiniBread)])"], "n": 4, "out": ["팥 붕어빵 1,000원", "미니 팥 5개 1,500원", "슈크림 붕어빵 1,200원", "미니 슈크림 5개 2,000원", "찍은 붕어빵: 4", "['팥', '슈크림']"]}, 96, 196, 1728, sel="c-x4")
o.append(note_card(96, 790, 560, 170, "print(m)", "붕어빵마다 자기 틀의 __str__ (25)", K2, ' data-build-in="rise order 1"'))
o.append(note_card(680, 790, 560, 170, "Bread.count", "미니도 부모 __init__을 거쳐서 4개", K2, ' data-build-in="rise order 2"'))
o.append(note_card(1264, 790, 560, 170, "isinstance", "컴프리헨션(23)으로 미니만 골라요", CR, ' data-build-in="rise order 3"'))
W("x-mini2", o, "보통 붕어빵과 미니 붕어빵을 섞어 메뉴판 리스트에 담았어요. for로 print하면 붕어빵마다 자기 틀의 __str__이 불려서 미니는 묶음 가격이 나와요. 찍은 붕어빵은 미니까지 4개로 세졌어요. 미니도 super().__init__으로 부모의 __init__을 거쳤기 때문이에요. 마지막 줄은 23의 컴프리헨션과 isinstance로 미니 붕어빵의 맛만 골랐어요. 24부터 26까지 배운 클래스를 한 셀에서 다 썼어요." + REAL)

# ---------- wrap up ----------
trouble([("AttributeError: 'CreamBread' object has no attribute 'flavor'", "자식 __init__에서 super().__init__을 안 불렀어요", "super().__init__(...)"),
         ("TypeError: ... takes 3 positional arguments but 4 were given", "super().__init__에 self를 넣었어요", "self 빼기"),
         ("TypeError: CreamBread.__init__() missing ... 'cream'", "자식 틀의 재료가 모자라요", "칸 수 맞추기, 기본값"),
         ("NameError: name 'Bred' is not defined", "괄호 안 부모 이름 오타이거나 부모를 아직 안 만들었어요", "부모 셀 먼저 실행"),
         ("한 붕어빵만 값이 달라요", "a.shop = 으로 바꿨어요", "Bread.shop = "),
         ("개수가 0에서 안 늘어요", "self.count로 셌어요", "Bread.count"),
         ("부모 메서드를 고쳤는데 자식은 그대로예요", "자식이 같은 이름으로 덮어썼어요", "super().메서드()")],
        "헷갈리면 \"이 메서드를 자식 틀에서 먼저 찾고, 없으면 부모 틀\" 순서로 따라가 봐요.",
        "이번 챕터에서 자주 만나는 일을 모았어요. 1번부터 3번은 자식 __init__과 super에서 생겨요. 4번은 부모 틀 이름을 틀렸거나 부모 틀 셀을 아직 실행하지 않았을 때 나요. 5번과 6번은 오류가 없어서 더 찾기 어려워요. 클래스 변수는 틀 이름으로 바꾼다는 것만 기억하세요. 7번은 자식이 덮어쓴 메서드라서 부모를 고쳐도 안 바뀌는 경우예요. super로 부모 것을 부르면 같이 바뀌어요.", cmd_w=330)

cheatsheet([('shop = "1호점"', "틀에 새긴 값", K2), ("Bread.shop = ...", "모두 한 번에 바꾸기", K2), ("class A(Bread):", "틀 물려받기", CR), ("super().__init__(...)", "부모에게 맡기기", CR),
            ("def intro(self):", "같은 이름이면 덮어쓰기", K3), ("super().intro()", "부모 것 + 조금 더", K3), ("isinstance(c, Bread)", "어떤 틀로 찍었나", K4), ("~는 ~의 한 종류", "상속할지 고르는 말", K4)],
           ["붕어빵마다 다르면 self.이름, 모두 같으면 틀에. 한 종류면 물려받아요", "클래스 세 챕터 끝: 붕어빵 틀로 데이터와 할 일을 한 곳에 묶었어요"],
           "이번 챕터의 핵심을 한 장에 모았어요. 모두 같은 값은 틀에 적는 클래스 변수로, 바꿀 땐 틀 이름으로 바꿔요. 자식 틀은 괄호에 부모 틀을 적어 물려받고, 칸을 더할 땐 super().__init__으로 부모에게 맡겨요. 같은 이름의 메서드를 다시 적으면 덮어쓰고, 부모 것도 쓰고 싶으면 super()로 불러요. 상속은 자식이 부모의 한 종류일 때만 써요. 24부터 26까지 붕어빵 틀 하나로 클래스의 기본을 모두 봤어요.")

finish([("Lightbulb", K1, "왜 필요한가", "복사해서 만든 슈크림 틀, 틀에 새긴 값과 물려받는 틀", "w-why", "w-big"),
        ("Archive", K2, "클래스 변수", "틀에 적은 값, 한 번에 바꾸기, 개수 세기, 두 변수 비교", "cv-basic", "cv-table"),
        ("Code", K3, "상속", "물려받기, 더하기, super().__init__, 덮어쓰기, 섞어 담기", "in-pass", "in-list"),
        ("Settings", K4, "복사와 상속 비교", "고칠 곳 한 군데, 한 종류일 때만", "cmp-copy", "cmp-when"),
        ("Warning", K5, "오류와 함정", "super 빠짐, self 두 번, 재료 수, a.shop, self.count", "t-nosuper", "t-count"),
        ("Star", K6, "실습", "도장 카드와 VIP 카드, 붕어빵과 미니 붕어빵 메뉴판", "x-card", "x-mini2")],
       "여섯 파트로 나눴어요. 1파트는 복사로 만든 틀의 문제와 큰 그림이에요. 2파트는 틀에 새기는 클래스 변수, 3파트가 중심인 상속이에요. 4파트는 복사와 상속을 비교하고 언제 상속하는지 정해요. 5파트는 자주 나는 오류, 6파트는 도장 카드와 붕어빵 메뉴판 실습이에요. 파트마다 새 커널에서 위에서부터 차례로 실행해요.",
       "클래스 3 (상속과 클래스 변수)")
