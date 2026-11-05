"""Generates every slide of the class deck (24) and slides/deck.json.

Story: keeps writing in basics.ipynb from chapters 12-23. Starts from a 붕어빵 kept in a dictionary with a separate
function, draws the class as a 붕어빵 틀 and each object as a 붕어빵, and shows that int, str and list were classes all
along. Part 2 makes an empty class and sticks values on by hand. Part 3 builds __init__ step by step from a chapter 19
function (setup(bread, ...) moved into the class, bread renamed to self), follows self while a and b are made, and
reads self.flavor = flavor side by side. Part 4 adds methods and shows a.intro() is Bread.intro(a). Part 5 collects the
usual errors, and part 6 is a 붕어빵 order, a cafe drink label and a stamp card.
Every cell and output comes from tools/demo.sh (tools/run_nb.py runs the cells with the project kernel).
Usage: python3 tools/gen.py slides
"""

import html, json, os, re, sys


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
             "".join(f'<span{(" id=" + chr(34) + x[2] + chr(34)) if len(x) > 2 else ""} style="color:{x[1]}">{e(x[0])}</span>' for x in parts))


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
EB2 = "2. 가장 작은 틀"
EB3 = "3. self와 __init__"
EB4 = "4. 메서드"
EB5 = "5. 오류와 함정"
EB6 = "6. 실습"

B_INIT = ["class Bread:", "    def __init__(self, flavor, price):", "        self.flavor = flavor", "        self.price = price"]
B_INTRO = ["    def intro(self):", '        print(self.flavor, "붕어빵", self.price, "원")']

# ---------- cover ----------
cover([("class Bread:", "#C7B8F2"), ("    def __init__(self, flavor, price):", W_), ("        self.flavor = flavor", "#F2C48D"), ("        self.price = price", "#F2C48D"), ("", W_),
       ('a = Bread("팥", 1000)', "#8FD8DE"), ('b = Bread("슈크림", 1200)', "#8FD8DE")],
      "클래스 1<br>붕어빵 틀과 붕어빵", "틀 하나로 붕어빵을<br>여러 개 찍어 내기",
      "오늘부터 세 챕터 동안 클래스를 배워요. 클래스는 붕어빵 틀이고, 그 틀로 찍어 낸 붕어빵 하나하나가 객체예요. 이번 챕터는 틀을 만들고, 찍을 때 재료를 넣는 __init__과 self를 천천히 봐요. 그다음 붕어빵이 할 일을 메서드로 붙여요. 25에서는 print로 보기 좋게 찍는 법, 26에서는 틀을 물려받는 상속을 배워요.", h1size=84)

ready([("변수, 타입, 함수 type()", "12"), ("리스트, f-string, for", "13"), ("딕셔너리", "15"), ("def, 매개변수, return", "19"), ("기본값, 지역 변수", "20")], "23",
      "09에서 만든 hello-uv 폴더를 VS Code로 열고, 12부터 쓰던 basics.ipynb를 다시 열어요. 이번 챕터는 19, 20의 함수를 많이 써요. 매개변수가 순서대로 들어간다는 것, 함수 안에서 만든 변수는 끝나면 사라진다는 것이 기억나지 않으면 19, 20을 먼저 봐요. 슬라이드의 출력은 tools/demo.sh가 hello-uv 커널에서 같은 셀을 실제로 실행한 결과예요. 셀 번호는 파트마다 [1]부터 다시 셌어요.")

# ---------- part 1 ----------
o = [sec("c-why")] + head(EB1, "붕어빵을 딕셔너리로 담으면 값과 할 일이 따로 놀아요", K1)
WHY = ['b1 = {"flavor": "팥", "price": 1000}', 'b2 = {"flavor": "슈크림", "price": 1200}', "", "def intro(bread):", '    print(bread["flavor"], "붕어빵", bread["price"], "원")', "", "intro(b1)", "intro(b2)"]
o += cell({"id": "c-why1", "lines": WHY, "n": 1, "out": ["팥 붕어빵 1000 원", "슈크림 붕어빵 1200 원"]}, 96, 196, 1100, sel="c-why1")
o += cell({"id": "c-why2", "lines": ['b3 = {"flavr": "피자", "price": 1500}', "intro(b3)"], "n": 2, "out": ["KeyError: 'flavor'"], "err": True, "attrs": ' data-build-in="rise order 2"'}, 96, 650, 1100, sel="c-why2")
o.append(note_card(1240, 196, 584, 300, "값은 딕셔너리, 할 일은 함수", "붕어빵 정보와 붕어빵 소개 함수가 서로 다른 곳에 있어요.", K1, ' data-build-in="rise order 1"'))
o.append(note_card(1240, 526, 584, 330, "키를 틀려도 모르고 넘어가요", "b3를 만들 때는 아무 말이 없다가, 소개할 때 KeyError가 나요.", RED, ' data-build-in="rise order 3"'))
o.append(caption("값과 할 일을 한 틀에 묶어 두는 방법이 클래스예요.", 944))
W("c-why", o, "지금까지 배운 것으로 붕어빵 가게를 만들어 봐요. 붕어빵 하나를 맛과 가격이 든 딕셔너리로 담고, 소개하는 일은 함수로 따로 만들었어요. 잘 돌아가지만 붕어빵 정보와 소개하는 함수가 서로 다른 곳에 있어요. 2번 셀처럼 키를 flavr로 잘못 적어도 만들 때는 아무 말이 없어요. 한참 뒤 소개할 때 KeyError가 나요. 값과 할 일을 한 틀에 묶어 두고, 찍을 때 재료를 꼭 넣게 하는 방법이 클래스예요." + REAL, ("p1", "왜 필요한가"))

o = [sec("c-big")] + head(EB1, "틀 하나로 붕어빵을 여러 개 찍어요", K1)
o.append(mold(96, 200, 640, 470, "class Bread", ["맛    flavor = ?", "가격  price  = ?", "", "할 일 intro()"], ' data-build-in="rise order 1"'))
o.append(harrow(770, 300, 150, BR, ' data-build-in="fade order 2"'))
o.append(harrow(770, 540, 150, BR, ' data-build-in="fade order 3"'))
o.append(p(f"position:absolute;left:748px;top:250px;width:200px;text-align:center;font-size:22px;font-weight:700;color:{BR}", "팥, 1000", ' data-build-in="fade order 2"'))
o.append(p(f"position:absolute;left:748px;top:490px;width:200px;text-align:center;font-size:22px;font-weight:700;color:{BR}", "슈크림, 1200", ' data-build-in="fade order 3"'))
o.append(obj("a", [("flavor", '"팥"'), ("price", "1000")], 960, 200, 420, attrs=' data-build-in="rise order 2"'))
o.append(obj("b", [("flavor", '"슈크림"'), ("price", "1200")], 960, 450, 420, attrs=' data-build-in="rise order 3"'))
o.append(note_card(1420, 200, 404, 470, "틀은 하나", "틀에는 맛과 가격을 넣을 자리만 있어요. 붕어빵마다 다른 값이 들어가요.", MD, ' data-build-in="rise order 4"'))
for i, (k, d, c) in enumerate([("틀 = 클래스", "class로 만들어요", MD), ("붕어빵 = 객체", "틀로 찍어 낸 것 하나", BR), ("속성", "붕어빵에 든 값 (맛, 가격)", K3), ("메서드", "붕어빵이 하는 일 (소개하기)", K4)]):
    x, y = 96 + (i % 2) * 878, 710 + (i // 2) * 106
    o.append(callout(x, y, 850, 92, k, d, c, 5 + i, 26))
W("c-big", o, "클래스를 그림으로 봐요. 왼쪽의 점선 상자가 붕어빵 틀이에요. 틀에는 맛과 가격을 넣을 자리, 그리고 소개하기 같은 할 일이 적혀 있어요. 틀에 팥과 1000원을 넣고 찍으면 붕어빵 a가, 슈크림과 1200원을 넣고 찍으면 붕어빵 b가 나와요. 틀은 하나인데 붕어빵은 몇 개든 찍을 수 있어요. 틀을 클래스, 찍어 낸 붕어빵을 객체라고 불러요. 붕어빵에 든 값은 속성, 붕어빵이 하는 일은 메서드예요. 이 네 단어를 오늘 계속 써요.")

o = [sec("c-type")] + head(EB1, "사실 int, str, list도 틀이에요", K1)
o += cell({"id": "c-t1", "lines": ["print(type(3))", 'print(type("팥"))', "print(type([1, 2]))"], "n": 3, "out": ["<class 'int'>", "<class 'str'>", "<class 'list'>"]}, 96, 196, 900, sel="c-t1")
o += cell({"id": "c-t2", "lines": ["xs = [1, 2]", "xs.append(3)", "print(xs)", 'print("Pat".lower())'], "n": 4, "out": ["[1, 2, 3]", "pat"], "attrs": ' data-build-in="rise order 2"'}, 96, 540, 900, sel="c-t2")
o.append(note_card(1040, 196, 784, 300, "class라고 나와요", "12에서 본 type()의 결과예요. 3은 int 틀, \"팥\"은 str 틀, [1, 2]는 list 틀로 찍은 객체예요.", K1, ' data-build-in="rise order 1"'))
o.append(note_card(1040, 540, 784, 330, "점 뒤의 함수가 메서드예요", "13의 append, 22의 lower가 메서드였어요. 리스트 틀, 문자열 틀에 미리 들어 있는 할 일이에요.", K4, ' data-build-in="rise order 3"'))
o.append(caption("이미 써 온 틀처럼, 붕어빵 틀을 직접 만들어 봐요.", 944))
W("c-type", o, "클래스는 처음 보는 게 아니에요. 12에서 type()을 쳤을 때 class int, class str이라고 나왔어요. 숫자 3은 int라는 틀로, 글자 팥은 str이라는 틀로, 리스트는 list 틀로 찍은 객체예요. 13에서 쓴 append, 22에서 쓴 lower처럼 점 뒤에 붙여 쓰던 함수가 메서드예요. 파이썬이 미리 만들어 둔 틀 안의 할 일이에요. 오늘은 이런 틀을 Bread라는 이름으로 직접 만들어요." + REAL)

# ---------- part 2 ----------
o = [sec("m-empty")] + head(EB2, "빈 틀을 만들고 붕어빵 두 개를 찍어요", K2)
o += cell({"id": "c-m1", "lines": ["class Bread:", "    pass", "", "a = Bread()", "b = Bread()", "print(type(a))"], "n": 1, "out": ["<class '__main__.Bread'>"]}, 96, 196, 900, sel="c-m1")
o.append(callout(96, 560, 900, 96, "class Bread:", "틀 이름이에요. 첫 글자는 대문자로 적어요", MD, 1, 26))
o.append(callout(96, 670, 900, 96, "pass", "아직 아무것도 안 넣었다는 표시예요", GRAY, 2, 26))
o.append(callout(96, 780, 900, 96, "Bread()", "틀로 붕어빵 하나 찍기. 괄호를 꼭 붙여요", BR, 3, 26))
o.append(obj("a", [], 1060, 196, 360, empty="빈 붕어빵", attrs=' data-build-in="rise order 3"'))
o.append(obj("b", [], 1464, 196, 360, empty="빈 붕어빵", attrs=' data-build-in="rise order 3"'))
o.append(note_card(1060, 420, 764, 300, "__main__.Bread", "지금 노트북(__main__)에서 만든 Bread 틀로 찍었다는 뜻이에요.", K2, ' data-build-in="rise order 4"'))
W("m-empty", o, "가장 작은 틀을 만들어요. class 뒤에 틀 이름을 적고 콜론을 붙여요. 틀 이름은 첫 글자를 대문자로 적는 게 약속이에요. 틀 안에 아직 넣을 게 없으면 pass라고 적어요. 아무것도 안 적으면 오류가 나서 자리를 채우는 말이에요. Bread()처럼 틀 이름 뒤에 괄호를 붙이면 붕어빵이 하나 찍혀요. a와 b는 같은 틀로 찍었지만 서로 다른 붕어빵이에요. type(a)를 보면 지금 노트북에서 만든 Bread 틀의 객체라고 나와요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p2", "가장 작은 틀"))

o = [sec("m-attr")] + head(EB2, "점(.)으로 붕어빵에 값을 붙여요", K2)
o += cell({"id": "c-m2", "lines": ['a.flavor = "팥"', "a.price = 1000", 'b.flavor = "슈크림"', "b.price = 1200", "print(a.flavor, a.price)", "print(b.flavor, b.price)"], "n": 2, "out": ["팥 1000", "슈크림 1200"]}, 96, 196, 900, sel="c-m2")
o.append(obj("a", [("flavor", '"팥"'), ("price", "1000")], 1060, 196, 360, attrs=' data-build-in="rise order 1"'))
o.append(obj("b", [("flavor", '"슈크림"'), ("price", "1200")], 1464, 196, 360, attrs=' data-build-in="rise order 2"'))
o.append(trow(96, 600, 1728, ["", "딕셔너리 (15)", "붕어빵 (객체)"], [300, 640, 640], head=True))
o.append(trow(96, 674, 1728, ["값 넣기", 'b1["flavor"] = "팥"', 'a.flavor = "팥"'], [300, 640, 640], order=3))
o.append(trow(96, 748, 1728, ["값 꺼내기", 'b1["flavor"]', "a.flavor"], [300, 640, 640], order=4))
o.append(caption("a.flavor는 \"a의 flavor\"로 읽어요.", 944))
W("m-attr", o, "빈 붕어빵에 값을 붙여요. 붕어빵 이름 뒤에 점을 찍고 칸 이름을 적은 뒤 값을 넣어요. a.flavor는 a의 flavor라고 읽어요. 이렇게 붕어빵에 붙은 값을 속성이라고 불러요. a와 b에 서로 다른 맛과 가격이 들어갔어요. 15의 딕셔너리와 비교하면 대괄호와 따옴표 대신 점 하나로 넣고 꺼내요." + REAL)

o = [sec("m-tedious")] + head(EB2, "손으로 붙이면 길고, 하나 빠뜨리기 쉬워요", K2)
o += cell({"id": "c-m3", "lines": ["c = Bread()", 'c.flavor = "피자"', "print(c.price)"], "n": 3, "out": ["AttributeError: 'Bread' object has no attribute 'price'"], "err": True}, 96, 196, 1200, sel="c-m3")
o.append(obj("c", [("flavor", '"피자"'), ("price", None)], 96, 460, 440, attrs=' data-build-in="rise order 1"'))
o.append(note_card(600, 460, 600, 300, "price를 빠뜨렸어요", "c에는 price 칸이 없어서 AttributeError가 나요. 붕어빵에 그런 속성이 없다는 뜻이에요.", RED, ' data-build-in="rise order 2"'))
o.append(note_card(1340, 196, 484, 564, "붕어빵이 10개라면", "찍기 10줄, 맛 10줄, 가격 10줄을 적어야 해요. 한 줄만 빠져도 그 붕어빵은 칸이 비어요.", K2, ' data-build-in="rise order 3"'))
o.append(caption("찍는 순간 재료를 한 번에 넣게 하면 빠뜨릴 일이 없어요.", 944))
W("m-tedious", o, "손으로 붙이는 방법의 문제를 봐요. c를 찍고 맛만 붙였더니, 가격을 꺼낼 때 AttributeError가 났어요. Bread 객체에 price라는 속성이 없다는 뜻이에요. 붕어빵이 열 개라면 찍는 줄, 맛 붙이는 줄, 가격 붙이는 줄을 열 번씩 적어야 해요. 한 줄만 빠져도 그 붕어빵은 칸이 비어요. 찍는 순간 재료를 한 번에 넣게 만드는 방법이 다음 파트의 __init__이에요." + REAL)

# ---------- part 3 ----------
o = [sec("s-func")] + head(EB3, "먼저 19에서 배운 함수로 한 번에 붙여 봐요", K3)
SF = ["class Bread:", "    pass", "", "def setup(bread, flavor, price):", "    bread.flavor = flavor", "    bread.price = price", "", "a = Bread()", 'setup(a, "팥", 1000)', "print(a.flavor, a.price)"]
o += cell({"id": "c-s1", "lines": SF, "n": 1, "out": ["팥 1000"]}, 96, 196, 1000, sel="c-s1")
o.append(hl(96, 196, 1000, 3, 3, "mark", 1, "붙이는 함수"))
o.append(code_box(1140, 196, 684, [[("setup(", W_), ("a", CS), (", ", W_), ('"팥"', CA), (", ", W_), ("1000", CA), (")", W_)]], ' data-build-in="rise order 2"', 32, 110))
o.append(callout(1140, 336, 684, 100, "bread ← a", "어느 붕어빵에 붙일지", BR, 3, 26))
o.append(callout(1140, 450, 684, 100, "flavor ← \"팥\"", "넣을 맛", TEAL, 4, 26))
o.append(callout(1140, 564, 684, 100, "price ← 1000", "넣을 가격", TEAL, 5, 26))
o.append(note_card(1140, 690, 684, 200, "bread.flavor = flavor", "a에 맛 칸을 붙이는 것과 같아요.", K3, ' data-build-in="rise order 6"'))
W("s-func", o, "__init__으로 바로 가기 전에, 이미 아는 함수로 같은 일을 해 봐요. setup 함수는 붕어빵 하나와 맛, 가격을 받아요. 19에서 배운 대로 인자는 순서대로 들어가요. 첫 번째 칸 bread에는 a가, flavor에는 팥이, price에는 1000이 들어가요. 함수 안의 bread.flavor = flavor는 a에 맛 칸을 붙이는 것과 같아요. 첫 번째 칸이 어느 붕어빵에 붙일지 정한다는 것을 기억해 두세요. 이 칸이 곧 self가 돼요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p3", "self와 __init__"))

o = [sec("s-move")] + head(EB3, "그 함수를 틀 안에 넣으면 __init__이에요", K3)
o.append(side(96, 196, 840, 400, "밖에 둔 함수", ["def setup(bread, flavor, price):", "    bread.flavor = flavor", "    bread.price = price", "", "a = Bread()", 'setup(a, "팥", 1000)'], ["팥 1000"], GRAY, "#F1F0EC", fs=25))
o.append(side(984, 196, 840, 400, "틀 안의 __init__", ["class Bread:", "    def __init__(self, flavor, price):", "        self.flavor = flavor", "        self.price = price", "", 'a = Bread("팥", 1000)'], ["팥 1000"], K3, K3BG, ' data-build-in="rise order 1"', fs=25))
for i, (k, d, c) in enumerate([("들여쓰기", "class 아래로 넣어요", MD), ("setup → __init__", "찍을 때 저절로 불리는 약속된 이름", K3), ("bread → self", "이름만 바뀌고 하는 일은 같아요", BR), ('Bread("팥", 1000)', "a를 넘기지 않아요. 파이썬이 넣어 줘요", TEAL)]):
    x, y = 96 + (i % 2) * 878, 640 + (i // 2) * 130
    o.append(callout(x, y, 850, 114, k, d, c, 2 + i, 27))
W("s-move", o, "왼쪽은 앞 장의 setup 함수, 오른쪽은 같은 일을 틀 안에 넣은 모양이에요. 다른 점은 네 가지예요. 첫째, 함수를 class 아래로 들여 써서 틀 안에 넣었어요. 둘째, 이름을 __init__으로 바꿨어요. 이 이름은 파이썬과 약속된 이름이라, 붕어빵을 찍을 때 저절로 불려요. 셋째, 첫 번째 칸 이름이 bread에서 self로 바뀌었어요. 이름만 바뀌었고 어느 붕어빵에 붙일지 정하는 칸인 건 같아요. 넷째, 부를 때 a를 넘기지 않아요. 파이썬이 방금 찍은 붕어빵을 첫 칸에 넣어 줘요. 두 셀의 결과는 똑같아요." + REAL)

o = [sec("s-init")] + head(EB3, "괄호 안의 재료가 __init__의 칸에 들어가요", K3)
o.append(code_box(96, 196, 1728, [[("a = ", W_), ("Bread", W_, "si-new"), ("(", W_), ('"팥"', CA, "si-a1"), (", ", W_), ("1000", CA, "si-a2"), (")", W_), ("          ", W_), ("# 찍는 줄", "#9AA1AE")],
                                  [("def __init__(", W_), ("self", CS), (", ", W_), ("flavor", CA), (", ", W_), ("price", CA), ("):", W_), ("  ", W_), ("# 틀 안의 첫 줄", "#9AA1AE")]], "", 36, 170))
for i, (top_, bot, c, bg, o_) in enumerate([("새 붕어빵", "self", BR, BRBG, 1), ('"팥"', "flavor", TEAL, K3BG, 2), ("1000", "price", TEAL, K3BG, 3)]):
    x = 96 + i * 590
    o.append(p(f"position:absolute;left:{x}px;top:410px;width:548px;height:96px;border-radius:18px;border:3px {'dashed' if i == 0 else 'solid'} {c};background:{CARD};font-family:{MONO if i else SANS};font-size:34px;font-weight:700;line-height:90px;text-align:center;color:{INK}", e(top_), f' data-build-in="fly order {o_}" data-from="{["si-new", "si-a1", "si-a2"][i]}"'))
    o.append(harrow(x + 244, 540, 60, c, f' data-build-in="fade order {o_}"', 90))
    o.append(p(f"position:absolute;left:{x}px;top:610px;width:548px;height:96px;border-radius:18px;background:{bg};border:3px solid {c};font-family:{MONO};font-size:36px;font-weight:700;line-height:90px;text-align:center;color:{INK}", e(bot)))
o.append(p(f"position:absolute;left:96px;top:370px;width:548px;text-align:center;font-size:22px;font-weight:700;color:{BR}", "파이썬이 넣어 줘요", ' data-build-in="fade order 1"'))
o.append(p(f"position:absolute;left:686px;top:370px;width:1138px;text-align:center;font-size:22px;font-weight:700;color:{TEAL}", "괄호 안의 재료가 순서대로 (19의 매개변수)", ' data-build-in="fade order 2"'))
o.append(note_card(96, 750, 846, 170, "self는 적지 않아요", "칸은 세 개, 재료는 두 개예요. 첫 칸은 파이썬 몫이에요.", BR, ' data-build-in="rise order 4"'))
o.append(note_card(978, 750, 846, 170, "__init__ 이름", "앞뒤로 밑줄 두 개씩. init은 처음 준비한다는 뜻의 initialize예요.", K3, ' data-build-in="rise order 5"'))
W("s-init", o, "찍는 줄과 __init__의 첫 줄을 위아래로 놓았어요. Bread 괄호 안에는 재료가 두 개, __init__에는 칸이 세 개예요. 하나가 남는 이유가 self예요. self 칸에는 파이썬이 방금 찍은 빈 붕어빵을 넣어 줘요. 그래서 우리는 괄호 안에 self를 적지 않아요. 팥과 1000은 19에서 배운 매개변수처럼 flavor, price에 순서대로 들어가요. __init__은 앞뒤로 밑줄을 두 개씩 적어요. init은 처음 준비한다는 뜻의 initialize를 줄인 말이에요.")

o = [sec("s-print")] + head(EB3, "__init__은 찍는 순간 저절로 불려요", K3)
SP = ["class Bread:", "    def __init__(self, flavor, price):", '        print("반죽 붓는 중:", flavor)', "        self.flavor = flavor", "        self.price = price", "", 'a = Bread("팥", 1000)', 'b = Bread("슈크림", 1200)', "print(a.flavor, b.flavor)"]
o += cell({"id": "c-s3", "lines": SP, "n": 3, "out": ["반죽 붓는 중: 팥", "반죽 붓는 중: 슈크림", "팥 슈크림"]}, 96, 196, 1100, sel="c-s3")
o.append(hl(96, 196, 1100, 2, 1, "mark", 1, "확인용"))
o.append(hl(96, 196, 1100, 6, 2, "run", 2, "찍을 때마다"))
o.append(note_card(1240, 196, 584, 330, "직접 부르지 않아요", "a.__init__()이라고 치지 않았는데, 찍는 줄마다 한 번씩 출력됐어요.", K3, ' data-build-in="rise order 3"'))
o.append(note_card(1240, 556, 584, 300, "언제 쓰나요", "붕어빵마다 꼭 있어야 하는 값을 찍는 순간 넣어 둘 때 써요.", GRAY, ' data-build-in="rise order 4"'))
W("s-print", o, "__init__이 정말 저절로 불리는지 print를 넣어 확인해 봐요. __init__ 첫 줄에 반죽 붓는 중이라는 출력을 넣었어요. 우리는 __init__을 부르는 줄을 한 번도 적지 않았어요. 그런데 Bread를 찍는 두 줄마다 한 번씩 출력이 나왔어요. 파이썬이 찍을 때마다 __init__을 찾아서 불러 준 거예요. 붕어빵마다 꼭 있어야 하는 값을 찍는 순간 넣어 두고 싶을 때 __init__을 써요. 확인이 끝나면 print 줄은 지워도 돼요." + REAL)

SELF_CODE = [[("def __init__(", W_), ("self", CS), (", flavor, price):", W_)], [("    ", W_), ("self", CS), (".flavor = flavor", W_)], [("    ", W_), ("self", CS), (".price = price", W_)]]
for k, (sid, cur_line) in enumerate([("s-self1", 0), ("s-self2", 1)]):
    o = [sec(sid, "magic" if k else "fade")] + head(EB3, "self는 지금 찍고 있는 그 붕어빵이에요", K3)
    for i, t in enumerate(['a = Bread("팥", 1000)', 'b = Bread("슈크림", 1200)']):
        on = i == cur_line
        o.append(p(f"position:absolute;left:96px;top:{220 + i * 96}px;width:760px;height:80px;border-radius:14px;padding:0 24px;line-height:80px;font-family:{MONO};font-size:32px;font-weight:700;color:{INK if on else '#B4B9C3'};background:{K3BG if on else CARD};border:3px solid {K3 if on else LINE};white-space:pre", e(t), f' id="line{i}"'))
    o.append(code_box(96, 450, 760, SELF_CODE, ' id="initbox"', 30, 230))
    o.append(obj("a", [("flavor", '"팥"'), ("price", "1000")], 1080, 220, 440, sid="obj-a"))
    if k:
        o.append(obj("b", [("flavor", '"슈크림"'), ("price", "1200")], 1080, 520, 440, sid="obj-b", attrs=' data-build-in="rise order 1"'))
    o.append(pill("← self", 1560, 270 + k * 300, BR, "#FFE7C2", ' id="self-pill"', 34))
    o.append(note_card(96, 790, 1728, 150, "첫째 줄을 실행할 때 self는 a, 둘째 줄을 실행할 때 self는 b예요" if k else "a를 찍는 동안 self는 a를 가리켜요",
                       "그래서 __init__ 코드 한 벌로 붕어빵마다 다른 값을 붙일 수 있어요." if k else "self.flavor = flavor는 지금은 a.flavor = \"팥\"과 같아요.", K3, ' id="selfnote"'))
    W(sid, o, ("a를 찍는 순간을 멈춰서 봐요. 파이썬이 빈 붕어빵을 하나 만들고, 그 붕어빵을 self 칸에 넣어 __init__을 불러요. 그래서 지금 self는 a를 가리켜요. self.flavor = flavor는 지금은 a.flavor = 팥과 같은 일을 해요. 다음 장으로 넘기면 b를 찍을 때를 봐요."
                if not k else "b를 찍는 줄로 내려왔어요. 이번에는 새 빈 붕어빵이 self 칸에 들어가서 self가 b를 가리켜요. 같은 __init__ 코드가 이번엔 b에 슈크림과 1200을 붙여요. self라는 이름 하나가 찍을 때마다 다른 붕어빵을 가리키기 때문에 코드 한 벌로 붕어빵을 몇 개든 만들 수 있어요. self는 나 자신이라는 뜻의 영어예요. 붕어빵 입장에서 내 맛, 내 가격이라고 읽으면 쉬워요."))

o = [sec("s-steps")] + head(EB3, "a = Bread(\"팥\", 1000) 한 줄에서 일어나는 일", K3)
ST5 = [("①", 'Bread("팥", 1000)', "빈 붕어빵이 하나 생겨요"),
       ("②", "__init__(빈 붕어빵, ...)", "빈 붕어빵이 self로 들어가요"),
       ("③", 'self.flavor = "팥"', "맛 칸을 붙여요"),
       ("④", "self.price = 1000", "가격 칸을 붙여요"),
       ("⑤", "a = 다 된 붕어빵", "끝나면 a에 담아요")]
for i, (n_, code, what) in enumerate(ST5):
    o.append(f'<div id="stp-{i + 1}" data-build-in="rise order {i + 1}" style="position:absolute;left:96px;top:{200 + i * 140}px;width:1160px;height:124px;background:{CARD};border:2px solid {LINE};border-left:10px solid {K3};border-radius:16px;padding:0 26px;display:flex;flex-direction:column;justify-content:center;gap:6px">'
             + '<div style="display:flex;flex-direction:row;gap:18px;align-items:center">' + p(f"font-size:32px;font-weight:900;color:{K3}", e(n_)) + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{INK};white-space:pre", e(code)) + '</div>'
             + p(f"padding-left:52px;font-size:26px;color:{SUB}", e(what)) + '</div>')
o.append(obj("빈 붕어빵", [], 1320, 200, 504, empty="아직 칸이 없어요", attrs=' data-build-in="rise order 1"'))
o.append(obj("self", [("flavor", '"팥"')], 1320, 200, 504, attrs=' data-build-in="fly order 3" data-from="stp-3"'))
o.append(obj("self", [("flavor", '"팥"'), ("price", "1000")], 1320, 200, 504, attrs=' data-build-in="fly order 4" data-from="stp-4"'))
o.append(obj("a", [("flavor", '"팥"'), ("price", "1000")], 1320, 200, 504, attrs=' data-build-in="fly order 5" data-from="stp-5"'))
o.append(note_card(1320, 520, 504, 360, "self는 누구?", "②부터 ④까지 self는 방금 생긴 그 붕어빵이에요. ⑤에서 그 붕어빵에 a라는 이름이 붙어요.", K3, ' data-build-in="rise order 6"'))
W("s-steps", o, "a = Bread(팥, 1000) 한 줄을 다섯 단계로 나눠 봐요. 먼저 빈 붕어빵이 하나 생겨요. 파이썬이 그 빈 붕어빵을 self 칸에, 팥과 1000을 나머지 칸에 넣어 __init__을 불러요. __init__ 안에서 self에 맛 칸과 가격 칸이 붙어요. 오른쪽 그림에서 칸이 하나씩 늘어나는 걸 보세요. __init__이 끝나면 다 된 붕어빵이 등호 왼쪽의 a에 담겨요. 12에서 배운 대로 오른쪽을 먼저 끝내고 왼쪽 변수에 담는 순서예요.")

# ---------- 붕어빵 기계: a slide students press in the browser (tools/lab_stamp.js) ----------
LAB_CSS = ("<style>"
           "#s-lab button{font-family:" + SANS.replace("'", '"') + ";font-size:26px;font-weight:700;border-radius:14px;padding:10px 22px;cursor:pointer;border:3px solid #C9CED8;background:#FFFFFF;color:#1D2330}"
           "#s-lab .lb-pick button.lb-on{background:#9A5B13;border-color:#9A5B13;color:#FFFFFF}"
           "#s-lab button:disabled{opacity:.45;cursor:default}"
           "#s-lab .lb-go{background:#0F7C86;border-color:#0F7C86;color:#FFFFFF}"
           "#s-lab code{font-family:" + MONO.replace("'", '"') + ";font-size:28px;color:#1D2330;background:#F1F0EC;border-radius:8px;padding:2px 8px}"
           "@keyframes lbPop{from{opacity:0;transform:scale(.8)}to{opacity:1;transform:none}}"
           "</style>")


def lab_btns(rid, label, vals, on):
    bs = "".join(f'<button data-v="{e(v)}" class="{"lb-on" if v == on else ""}">{e(v)}</button>' for v in vals)
    return (f'<div id="{rid}" class="lb-pick" style="display:flex;flex-direction:row;align-items:center;gap:14px">'
            + p(f"width:90px;font-size:26px;font-weight:700;color:{SUB}", e(label)) + bs + '</div>')


def code_line(txt, c=W_, sid=None):
    idp = f' id="{sid}"' if sid else ""
    return p(f"height:58px;font-family:{MONO};font-size:30px;font-weight:700;line-height:58px;color:{c};white-space:pre", txt, idp)


o = [sec("s-lab"), LAB_CSS] + head(EB3, "눌러 보기: 붕어빵 기계로 한 단계씩 찍어 봐요", K3)
o.append(card(96, 196, 820, 224, '<div style="display:flex;flex-direction:column;gap:18px;padding:26px 30px">'
              + lab_btns("lb-flavors", "맛", ["팥", "슈크림", "피자", "고구마"], "팥") + lab_btns("lb-prices", "가격", ["1000", "1200", "1500"], "1000") + '</div>'))
o.append('<div style="position:absolute;left:96px;top:440px;width:820px;height:396px;background:#252B36;border-radius:22px;padding:24px 34px;overflow:hidden">'
         + f'<div id="lb-hl" style="position:absolute;left:0;top:24px;width:820px;height:58px;background:rgba(242,196,141,.20);border-left:8px solid {CS};opacity:0;transition:top .45s ease,opacity .3s"></div>'
         + code_line(f'<span style="color:{CK}">class</span> Bread:')
         + code_line(f'    <span style="color:{CK}">def</span> <span style="color:{CM}">__init__</span>(<span style="color:{CS}">self</span>, <span style="color:{CA}">flavor</span>, <span style="color:{CA}">price</span>):')
         + code_line(f'        <span style="color:{CS}">self</span>.flavor = <span style="color:{CA}">flavor</span>')
         + code_line(f'        <span style="color:{CS}">self</span>.price = <span style="color:{CA}">price</span>')
         + code_line("&#160;")
         + code_line(f'<span style="color:{CS}">a</span> = Bread(<span style="color:{CA}">"팥"</span>, <span style="color:{CA}">1000</span>)', sid="lb-call")
         + '</div>')
o.append('<div style="position:absolute;left:96px;top:852px;width:820px;display:flex;flex-direction:row;gap:16px">'
         '<button id="lb-next" class="lb-go">한 단계씩 ▶</button><button id="lb-auto">한 번에 찍기</button><button id="lb-reset">처음부터</button></div>')
o.append(mold(960, 196, 400, 190, "Bread", ["__init__(self, flavor,", "         price)"], fs=22))
o.append(f'<div id="lb-locals" style="position:absolute;left:1400px;top:196px;width:424px;height:190px;background:{K3BG};border:3px dashed {TEAL};border-radius:22px;padding:18px 26px;display:flex;flex-direction:column;gap:8px;opacity:0;transition:opacity .5s">'
         + p(f"font-size:22px;font-weight:700;color:{TEAL}", "__init__ 안의 재료 (지역 변수)")
         + f'<div style="display:flex;flex-direction:row;gap:12px">{p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{SUB}", "flavor =")}{p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{INK}", "&quot;팥&quot;", " id=\"lb-lf\"")}</div>'
         + f'<div style="display:flex;flex-direction:row;gap:12px">{p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{SUB}", "price =")}{p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{INK}", "1000", " id=\"lb-lp\"")}</div></div>')
o.append(f'<div id="lb-self" style="position:absolute;left:980px;top:440px;width:310px;height:80px;display:flex;flex-direction:row;align-items:center;gap:14px;opacity:0;transition:opacity .4s">'
         + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:{INK};background:{CS};border-radius:999px;padding:8px 26px", "self")
         + f'<x-shape kind="arrow-right" style="width:130px;height:30px;background:{BR}"></x-shape></div>')
o.append(p(f"position:absolute;left:1300px;top:470px;width:480px;font-size:24px;color:{GRAY};text-align:center", "찍으면 여기서 붕어빵이 만들어져요"))
o.append(f'<div style="position:absolute;left:960px;top:680px;width:864px;height:222px;background:{CARD};border:2px solid {LINE};border-radius:22px;padding:18px 26px;display:flex;flex-direction:column;gap:14px">'
         + '<div style="display:flex;flex-direction:row;gap:14px;align-items:center">' + p(f"font-size:24px;font-weight:700;color:{BR}", "찍은 붕어빵") + p(f"font-size:24px;font-weight:700;color:{GRAY}", "", ' id="lb-count"') + '</div>'
         + f'<div id="lb-tray" style="display:flex;flex-direction:row;gap:16px;align-items:center;height:124px">{p(f"font-size:24px;color:{GRAY}", "아직 없어요. 찍으면 여기에 쌓여요.")}</div></div>')
o.append(f'<div style="position:absolute;left:96px;top:930px;width:1728px;height:106px;background:{CARD};border:2px solid {LINE};border-left:10px solid {TEAL};border-radius:18px;padding:0 30px;display:flex;align-items:center">'
         + p(f"font-size:30px;font-weight:500;line-height:1.4;color:{INK}", "맛과 가격을 고르고 <b>한 단계씩</b>이나 <b>한 번에 찍기</b>를 눌러요. 브라우저로 슬라이드를 열면 눌러져요.", ' id="lb-msg"') + '</div>')
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lab_stamp.js")) as f:
    o.append('<script type="text/slide-js">\n' + f.read() + '</script>')
W("s-lab", o, "앞 장의 다섯 단계를 직접 눌러 보는 장이에요. 브라우저로 슬라이드를 열면 버튼이 눌러져요. 맛과 가격을 고르고 한 단계씩을 누르면 왼쪽 코드에서 지금 실행하는 줄에 불이 들어와요. 오른쪽에서는 빈 붕어빵이 생기고, self가 그 붕어빵을 가리키고, 맛 칸과 가격 칸이 하나씩 붙어요. __init__이 끝나면 재료 칸은 사라지고 붕어빵에 a라는 이름이 붙어요. 한 번 더 찍으면 이번엔 b가 만들어지고 self는 새 붕어빵을 가리켜요. 수강생에게 다음 단계에서 무엇이 바뀔지 먼저 물어보고 눌러 보세요.")

o = [sec("s-lr")] + head(EB3, "self.flavor = flavor는 왼쪽과 오른쪽이 달라요", K3)
o.append(code_box(96, 200, 1728, [[("self.flavor", CS), (" = ", W_), ("flavor", CA)]], ' data-build-in="rise order 1"', 56, 150))
o.append(card(96, 390, 846, 300, p(f"font-family:{MONO};font-size:40px;font-weight:700;color:{BR}", "self.flavor") + p(f"font-size:32px;font-weight:700;color:{INK}", "붕어빵에 붙는 칸")
              + p(f"font-size:27px;line-height:1.5;color:{SUB}", "붕어빵이 있는 동안 계속 남아요. 나중에 a.flavor로 꺼내요."), BR, ' data-build-in="rise order 2"'))
o.append(card(978, 390, 846, 300, p(f"font-family:{MONO};font-size:40px;font-weight:700;color:{TEAL}", "flavor") + p(f"font-size:32px;font-weight:700;color:{INK}", "찍을 때 들어온 재료")
              + p(f"font-size:27px;line-height:1.5;color:{SUB}", "__init__의 매개변수예요. 20의 지역 변수라서 __init__이 끝나면 사라져요."), TEAL, ' data-build-in="rise order 3"'))
o.append(note_card(96, 730, 1728, 150, "이름이 같아서 헷갈려요", "self. 이 붙은 쪽은 붕어빵 칸, 안 붙은 쪽은 잠깐 들고 온 재료예요. 보통은 같은 이름을 써요.", GRAY, ' data-build-in="rise order 4"'))
W("s-lr", o, "가장 헷갈리는 줄을 색으로 나눠 봐요. 왼쪽 self.flavor는 붕어빵에 붙는 칸이에요. 붕어빵이 있는 동안 계속 남아서 나중에 a.flavor로 꺼낼 수 있어요. 오른쪽 flavor는 찍을 때 괄호로 들어온 재료예요. __init__의 매개변수라서 20에서 배운 지역 변수처럼 __init__이 끝나면 사라져요. 그래서 사라지기 전에 붕어빵 칸에 옮겨 담는 줄이 self.flavor = flavor예요. 이름이 같아서 헷갈리면 self. 이 붙었는지만 보세요. 보통은 알아보기 쉽게 같은 이름을 써요.")

o = [sec("s-noself")] + head(EB3, "self.를 빼면 재료가 붕어빵에 안 붙어요", K3)
NS = ["class Bread:", "    def __init__(self, flavor, price):", "        flavor = flavor", "        price = price", "", 'a = Bread("팥", 1000)', "print(a.flavor)"]
o += cell({"id": "c-s4", "lines": NS, "n": 4, "out": ["AttributeError: 'Bread' object has no attribute 'flavor'"], "err": True}, 96, 196, 1100, sel="c-s4")
o.append(hl(96, 196, 1100, 2, 2, "err", 1, "self. 없음"))
o.append(obj("a", [], 1240, 196, 584, empty="붙은 칸이 없어요", attrs=' data-build-in="rise order 2"'))
o.append(note_card(1240, 430, 584, 330, "지역 변수에 다시 넣었을 뿐이에요", "flavor = flavor는 재료를 자기 자신에 다시 넣었어요. __init__이 끝나면 같이 사라져요.", RED, ' data-build-in="rise order 3"'))
o.append(caption("붕어빵에 남길 값은 꼭 self.이름 = 값으로 적어요.", 944))
W("s-noself", o, "self.를 빼먹으면 어떻게 되는지 봐요. flavor = flavor는 들어온 재료를 자기 자신에게 다시 넣었을 뿐이에요. 붕어빵에는 아무 칸도 붙지 않았어요. 그래서 a.flavor를 꺼내면 그런 속성이 없다는 AttributeError가 나요. 20에서 함수 안에서 만든 변수는 함수가 끝나면 사라진다고 배웠어요. __init__도 함수라서 똑같아요. 붕어빵에 남기려면 꼭 self.이름 = 값으로 적어요." + REAL)

o = [sec("s-start")] + head(EB3, "재료로 받지 않는 칸도 만들 수 있어요", K3)
SS = B_INIT + ["        self.baked = False", "", 'a = Bread("팥", 1000)', "print(a.flavor, a.price, a.baked)"]
o += cell({"id": "c-s5", "lines": SS, "n": 5, "out": ["팥 1000 False"]}, 96, 196, 1100, sel="c-s5")
o.append(hl(96, 196, 1100, 4, 1, "run", 1, "처음 값"))
o.append(obj("a", [("flavor", '"팥"'), ("price", "1000"), ("baked", "False")], 1240, 196, 584, attrs=' data-build-in="rise order 2"'))
o.append(note_card(1240, 520, 584, 340, "언제 쓰나요", "처음에는 모두 같은 값으로 시작하는 칸이에요. 다 구웠는지, 도장 0개, 판매 0개 같은 값이에요.", K3, ' data-build-in="rise order 3"'))
W("s-start", o, "__init__에서 모든 칸을 재료로 받을 필요는 없어요. baked 칸은 괄호로 받지 않고 처음부터 False로 정했어요. 찍은 붕어빵은 모두 아직 안 구운 상태로 시작해요. 도장 카드의 도장 개수, 가게의 판매 개수처럼 처음엔 모두 같은 값으로 시작하는 칸에 써요. 6파트의 도장 카드 실습에서 이 모양을 다시 써요." + REAL)

# ---------- part 4 ----------
o = [sec("f-method")] + head(EB4, "틀 안의 함수가 메서드예요", K4)
FM = B_INIT + [""] + B_INTRO + ["", 'a = Bread("팥", 1000)', 'b = Bread("슈크림", 1200)', "a.intro()", "b.intro()"]
o += cell({"id": "c-f1", "lines": FM, "n": 1, "out": ["팥 붕어빵 1000 원", "슈크림 붕어빵 1200 원"]}, 96, 196, 1100, sel="c-f1")
o.append(hl(96, 196, 1100, 5, 2, "mark", 1, "메서드"))
o.append(callout(1240, 196, 584, 120, "intro(self)", "틀 안에 들여 쓴 함수. 첫 칸은 self", K4, 2, 24))
o.append(callout(1240, 330, 584, 120, "self.flavor", "그 붕어빵의 맛을 꺼내요", BR, 3, 24))
o.append(callout(1240, 464, 584, 120, "a.intro()", "a에게 소개하라고 시켜요. 괄호는 비워요", TEAL, 4, 24))
o.append(note_card(1240, 610, 584, 250, "1파트의 intro와 비교", "intro(b1)처럼 넘기지 않고, 붕어빵에게 a.intro()로 시켜요.", GRAY, ' data-build-in="rise order 5"'))
W("f-method", o, "붕어빵이 할 일을 틀 안에 넣어요. __init__ 아래에 def intro를 같은 깊이로 들여 썼어요. 틀 안에 있는 함수를 메서드라고 불러요. 메서드의 첫 칸도 self예요. 그래서 안에서 self.flavor, self.price로 그 붕어빵의 값을 꺼낼 수 있어요. 부를 때는 a.intro()처럼 붕어빵 이름 뒤에 점을 찍어요. 1파트에서는 intro(b1)처럼 딕셔너리를 함수에 넘겼는데, 이제는 붕어빵에게 직접 시켜요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p4", "메서드"))

o = [sec("f-same")] + head(EB4, "a.intro()는 Bread.intro(a)와 같아요", K4)
o += cell({"id": "c-f2", "lines": ["Bread.intro(a)", "Bread.intro(b)"], "n": 2, "out": ["팥 붕어빵 1000 원", "슈크림 붕어빵 1200 원"]}, 96, 196, 900, sel="c-f2")
o.append(code_box(96, 460, 820, [[("a", CS), (".intro()", W_)]], ' data-build-in="rise order 1"', 48, 130))
o.append(harrow(940, 510, 120, K4, ' data-build-in="fade order 2"'))
o.append(code_box(1084, 460, 740, [[("Bread.intro(", W_), ("a", CS), (")", W_)]], ' data-build-in="rise order 2"', 48, 130))
o.append(note_card(96, 640, 1728, 230, "괄호가 비어 있는데 self 칸이 있는 이유", "점 앞의 a가 self 칸으로 들어가요. 파이썬이 a.intro()를 Bread 틀의 intro에 a를 넣어 부르는 걸로 바꿔요. __init__에서 방금 찍은 붕어빵이 self로 들어간 것과 같아요.", K4, ' data-build-in="rise order 3"'))
o.append(note_card(1040, 196, 784, 230, "결과가 똑같아요", "앞 셀의 a.intro(), b.intro()와 같은 두 줄이 나왔어요.", GRAY, ' data-build-in="rise order 1"'))
W("f-same", o, "def intro(self)에는 칸이 하나 있는데, a.intro()의 괄호는 비어 있어요. 그 칸에는 무엇이 들어갈까요? 점 앞의 a예요. 파이썬은 a.intro()를 Bread 틀의 intro에 a를 넣어 부르는 것으로 바꿔서 실행해요. 실제로 Bread.intro(a)라고 쳐도 결과가 똑같아요. 평소에는 짧은 a.intro()를 써요. self는 메서드를 부른 그 붕어빵, __init__에서는 방금 찍은 그 붕어빵이에요." + REAL)

o = [sec("f-change")] + head(EB4, "메서드로 값을 바꾸고, return으로 돌려받아요", K4)
FC = B_INIT + ["", "    def discount(self, won):", "        self.price = self.price - won", "", "    def total(self, qty):", "        return self.price * qty", "", 'a = Bread("팥", 1000)', 'b = Bread("슈크림", 1200)', "a.discount(200)", "print(a.price, b.price)", "print(a.total(3))"]
o += cell({"id": "c-f3", "lines": FC, "n": 3, "out": ["800 1200", "2400"]}, 96, 196, 1100, sel="c-f3")
o.append(hl(96, 196, 1100, 5, 2, "mark", 1, "값 바꾸기"))
o.append(hl(96, 196, 1100, 8, 2, "run", 2, "돌려주기"))
o.append(obj("a", [("flavor", '"팥"'), ("price", "1000 → 800")], 1240, 196, 584, attrs=' data-build-in="rise order 3"'))
o.append(obj("b", [("flavor", '"슈크림"'), ("price", "1200")], 1240, 456, 584, attrs=' data-build-in="rise order 4"'))
o.append(note_card(1240, 716, 584, 200, "a만 바뀌어요", "a.discount(200)의 self는 a예요. b의 가격은 그대로예요.", K4, ' data-build-in="rise order 5"'))
W("f-change", o, "메서드에도 self 뒤에 매개변수를 더 둘 수 있어요. discount는 깎을 금액을 받아서 자기 가격에서 빼요. a.discount(200)을 부르면 self는 a라서 a의 가격만 800원이 되고 b는 1200원 그대로예요. 붕어빵마다 칸이 따로 있다는 게 이거예요. total은 개수를 받아 가격을 곱한 값을 return해요. 19에서 배운 대로 return한 값은 print로 찍거나 변수에 담아 써요." + REAL)

o = [sec("f-compare")] + head(EB4, "딕셔너리와 함수 vs 클래스", K4)
o.append(side(96, 196, 846, 240, "딕셔너리와 함수 (1파트)", ['b1 = {"flavor": "팥", "price": 1000}', "intro(b1)", 'b1["flavor"]'], [], GRAY, "#F1F0EC", fs=24))
o.append(side(978, 196, 846, 240, "클래스", ['a = Bread("팥", 1000)', "a.intro()", "a.flavor"], [], K4, K4BG, ' data-build-in="rise order 1"', fs=24))
CW = [300, 680, 680]
o.append(trow(96, 480, 1728, ["", "딕셔너리와 함수", "클래스"], CW, head=True))
for i, r in enumerate([["할 일은 어디에", "함수가 밖에 따로 있어요", "틀 안에 같이 있어요"],
                       ["값 꺼내기", 'b1["flavor"]', "a.flavor"],
                       ["재료를 빠뜨리면", "쓸 때 KeyError", "찍을 때 바로 TypeError"],
                       ["어울리는 곳", "잠깐 담아 두는 값", "같은 모양을 여러 개 찍을 때"]]):
    o.append(trow(96, 560 + i * 84, 1728, r, CW, order=2 + i, h=72, fs=26))
W("f-compare", o, "1파트의 딕셔너리 방식과 비교해요. 딕셔너리는 값만 담고 할 일은 밖의 함수가 해요. 클래스는 값과 할 일이 한 틀에 같이 있어요. 값을 꺼낼 때는 대괄호와 따옴표 대신 점을 써요. 가장 큰 차이는 재료를 빠뜨렸을 때예요. 딕셔너리는 나중에 쓸 때 KeyError가 나지만, 클래스는 찍는 순간 재료가 모자라다고 알려 줘요. 잠깐 값을 담아 둘 때는 딕셔너리가 편하고, 같은 모양을 여러 개 찍어 쓸 때는 클래스가 좋아요.")

# ---------- part 5 ----------
o = [sec("t-missing")] + head(EB5, "재료 수가 모자라면 missing argument", K5)
TM = B_INIT + ["", "    def intro():", '        print("붕어빵")', "", 'a = Bread("팥")']
o += cell({"id": "c-t1", "lines": TM, "n": 1, "out": ["TypeError: Bread.__init__() missing 1 required positional argument: 'price'"], "err": True}, 96, 196, 1500, sel="c-t1")
o.append(hl(96, 196, 1500, 8, 1, "err", 1, "재료 하나"))
o.append(note_card(96, 680, 846, 220, "읽는 법", "__init__에 꼭 필요한 칸 price가 1개 모자라요.", RED, ' data-build-in="rise order 2"'))
o.append(note_card(978, 680, 846, 220, "고치기", 'Bread("팥", 1000)처럼 self 뒤 칸 수만큼 재료를 넣어요.', GR, ' data-build-in="rise order 3"'))
W("t-missing", o, "자주 나는 오류를 봐요. 붕어빵을 찍을 때 맛만 넣고 가격을 빠뜨렸어요. __init__에 꼭 필요한 칸 price가 하나 모자라다는 TypeError예요. self는 파이썬이 채우니까 self를 뺀 칸 수만큼 재료를 넣으면 돼요. 1파트의 딕셔너리는 나중에 쓸 때 오류가 났지만, 클래스는 찍는 순간 알려 줘요. 틀 안의 intro에는 일부러 실수를 넣어 뒀어요. 다음 장에서 봐요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p5", "오류와 함정"))

o = [sec("t-noself")] + head(EB5, "메서드에 self를 빼면 takes 0 positional arguments", K5)
o.append(side(96, 196, 760, 190, "앞 셀의 틀 일부", ["    def intro():", '        print("붕어빵")'], [], RED, "#F8E6E6", fs=26, dashed=True))
o += cell({"id": "c-t2", "lines": ['a = Bread("팥", 1000)', "a.intro()"], "n": 2, "out": ["TypeError: Bread.intro() takes 0 positional arguments but 1 was given"], "err": True}, 96, 420, 1728, sel="c-t2")
o.append(note_card(96, 600, 846, 240, "읽는 법", "intro는 받을 칸이 0개인데 1개가 들어왔어요. 그 1개는 점 앞의 a예요.", RED, ' data-build-in="rise order 1"'))
o.append(note_card(978, 600, 846, 240, "고치기", "메서드 첫 칸에 self를 꼭 적어요. def intro(self):", GR, ' data-build-in="rise order 2"'))
o.append(caption("a.intro()는 Bread.intro(a)라서 a가 하나 들어가요.", 900))
W("t-noself", o, "intro를 만들 때 self를 빼먹었어요. a.intro()를 부르면 받을 칸이 0개인데 1개가 들어왔다는 TypeError가 나요. 괄호를 비웠는데 왜 1개일까요? 4파트에서 본 것처럼 a.intro()는 Bread.intro(a)로 바뀌어서 a가 하나 들어가요. 메서드를 만들 때는 쓰지 않더라도 첫 칸에 self를 꼭 적어요." + REAL)

o = [sec("t-init")] + head(EB5, "밑줄을 하나만 적으면 takes no arguments", K5)
TI = ["class Bread:", "    def _init_(self, flavor, price):", "        self.flavor = flavor", "        self.price = price", "", 'a = Bread("팥", 1000)']
o += cell({"id": "c-t4", "lines": TI, "n": 3, "out": ["TypeError: Bread() takes no arguments"], "err": True}, 96, 196, 1100, sel="c-t4")
o.append(hl(96, 196, 1100, 1, 1, "err", 1, "_init_"))
o.append(note_card(1240, 196, 584, 330, "읽는 법", "Bread 틀은 재료를 받지 않는다는 뜻이에요. 약속된 이름 __init__을 찾지 못했어요.", RED, ' data-build-in="rise order 2"'))
o.append(note_card(1240, 556, 584, 300, "고치기", "앞뒤로 밑줄 두 개씩 __init__. __int__처럼 글자가 빠져도 같은 오류가 나요.", GR, ' data-build-in="rise order 3"'))
W("t-init", o, "__init__의 밑줄을 하나씩만 적었어요. 파이썬은 앞뒤 밑줄 두 개짜리 __init__이라는 이름만 찾아요. 이름이 다르면 그냥 평범한 메서드라서 찍을 때 불리지 않아요. 그래서 Bread 틀은 재료를 받지 않는다는 TypeError가 나요. 밑줄이 두 개인지, init 글자가 맞는지 확인해요. VS Code에서는 밑줄 두 개가 붙어 보여서 놓치기 쉬워요." + REAL)

o = [sec("t-print")] + head(EB5, "붕어빵을 print하면 이상한 글자가 나와요", K5)
TP = B_INIT + ["", 'a = Bread("팥", 1000)', "print(a)"]
o += cell({"id": "c-t5", "lines": TP, "n": 4, "out": ["<__main__.Bread object at 0x7f440c2dbb60>"]}, 96, 196, 1100, sel="c-t5")
o.append(callout(96, 560, 1100, 96, "__main__.Bread", "지금 노트북에서 만든 Bread 틀의", MD, 1, 26))
o.append(callout(96, 670, 1100, 96, "object", "객체(붕어빵)예요", BR, 2, 26))
o.append(callout(96, 780, 1100, 96, "at 0x7f…", "컴퓨터 안의 자리. 실행할 때마다 달라요", GRAY, 3, 26))
o.append(note_card(1240, 196, 584, 330, "오류는 아니에요", "파이썬이 이 붕어빵을 글자로 어떻게 보여 줄지 몰라서 기본 모양으로 찍었어요.", K5, ' data-build-in="rise order 4"'))
o.append(note_card(1240, 556, 584, 300, "25에서 바꿔요", "지금은 a.flavor처럼 칸을 꺼내 찍어요. 다음 챕터의 __str__로 보기 좋게 바꿔요.", GR, ' data-build-in="rise order 5"'))
W("t-print", o, "붕어빵을 통째로 print하면 꺾쇠괄호 안에 낯선 글자가 나와요. 오류는 아니에요. 지금 노트북에서 만든 Bread 틀의 객체이고, 컴퓨터 안의 어느 자리에 있다는 뜻이에요. 0x로 시작하는 주소는 실행할 때마다 달라서 여러분 화면과 슬라이드가 달라도 괜찮아요. 파이썬은 우리가 만든 붕어빵을 글자로 어떻게 보여 줄지 몰라요. 지금은 a.flavor처럼 칸을 꺼내 찍고, 다음 챕터에서 __str__로 보기 좋게 바꿔요." + REAL)

# ---------- part 6 ----------
o = [sec("x-order")] + head(EB6, "붕어빵 가게: 주문 받은 붕어빵을 소개하고 합계 내기", K6)
XO = B_INIT + [""] + B_INTRO + ["", 'order = [Bread("팥", 1000), Bread("슈크림", 1200), Bread("팥", 1000)]', "for b in order:", "    b.intro()", "total = sum([b.price for b in order])", 'print("합계", total, "원")']
o += cell({"id": "c-x1", "lines": XO, "n": 1, "out": ["팥 붕어빵 1000 원", "슈크림 붕어빵 1200 원", "팥 붕어빵 1000 원", "합계 3200 원"]}, 96, 196, 1300, sel="c-x1")
o.append(hl(96, 196, 1300, 8, 1, "mark", 1))
o.append(hl(96, 196, 1300, 9, 2, "run", 2, "하나씩"))
o.append(hl(96, 196, 1300, 11, 1, "mark", 3))
o.append(note_card(1440, 196, 384, 300, "객체도 값이에요", "리스트에 담고 for로 하나씩 꺼내요.", K6, ' data-build-in="rise order 4"'))
o.append(note_card(1440, 526, 384, 330, "b.price만 모아요", "23의 컴프리헨션으로 가격을 모아 sum에 넘겨요.", GRAY, ' data-build-in="rise order 5"'))
W("x-order", o, "배운 것을 섞어 붕어빵 가게 주문을 처리해요. 손님이 주문한 붕어빵 세 개를 찍어서 바로 리스트에 담았어요. 객체도 숫자나 글자처럼 값이라 리스트에 담을 수 있어요. for로 하나씩 꺼내 b.intro()를 부르면 붕어빵마다 자기 맛과 가격으로 소개해요. 합계는 23의 컴프리헨션으로 b.price만 모아 sum에 넘겼어요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p6", "실습"))

o = [sec("x-drink")] + head(EB6, "카페 음료: 기본값 사이즈와 메뉴 이름표 만들기", K6)
XD = ["class Drink:", '    def __init__(self, name, price, size="M"):', "        self.name = name", "        self.price = price", "        self.size = size", "", "    def label(self):", '        return f"{self.name}({self.size}) {self.price:,}원"', "", 'd1 = Drink("latte", 5000)', 'd2 = Drink("tea", 4000, "L")', "print(d1.label())", "print(d2.label())"]
o += cell({"id": "c-x2", "lines": XD, "n": 2, "out": ["latte(M) 5,000원", "tea(L) 4,000원"]}, 96, 196, 1300, sel="c-x2")
o.append(hl(96, 196, 1300, 1, 1, "mark", 1, "20 기본값"))
o.append(hl(96, 196, 1300, 7, 1, "run", 2, "return"))
o.append(obj("d1", [("name", '"latte"'), ("price", "5000"), ("size", '"M"')], 1440, 196, 384, cls="Drink", fs=24, rh=52, attrs=' data-build-in="rise order 3"'))
o.append(obj("d2", [("name", '"tea"'), ("price", "4000"), ("size", '"L"')], 1440, 490, 384, cls="Drink", fs=24, rh=52, attrs=' data-build-in="rise order 4"'))
o.append(note_card(1440, 790, 384, 200, "label은 글자를 돌려줘요", "print는 밖에서 해요. 영수증에 다시 쓸 수 있어요.", K6, ' data-build-in="rise order 5"'))
W("x-drink", o, "카페 음료 틀을 만들어요. __init__에도 20에서 배운 기본값을 쓸 수 있어요. 사이즈를 안 넣으면 M이 들어가요. label 메서드는 13의 f-string과 천 단위 콤마로 메뉴 이름표 글자를 만들어 return해요. 메서드 안에서 print하지 않고 글자를 돌려주면, 밖에서 찍을 수도 있고 영수증이나 메뉴판에 다시 쓸 수도 있어요. 19에서 본 print와 return의 차이와 같아요." + REAL)

o = [sec("x-card")] + head(EB6, "도장 카드: 처음 0개에서 손님마다 따로 쌓기", K6)
XC = ["class Card:", "    def __init__(self, name):", "        self.name = name", "        self.stamps = 0", "", "    def add(self):", "        self.stamps = self.stamps + 1", "", 'kim = Card("kim")', 'lee = Card("lee")', "kim.add()", "kim.add()", "kim.add()", "lee.add()", "print(kim.name, kim.stamps)", "print(lee.name, lee.stamps)"]
o += cell({"id": "c-x3", "lines": XC, "n": 3, "out": ["kim 3", "lee 1"]}, 96, 196, 1100, sel="c-x3")
o.append(hl(96, 196, 1100, 3, 1, "mark", 1, "처음 값"))
o.append(hl(96, 196, 1100, 6, 1, "run", 2, "하나 더하기"))
o.append(obj("kim", [("name", '"kim"'), ("stamps", "0 → 3")], 1240, 196, 584, cls="Card", color=BL, bg=K1BG, attrs=' data-build-in="rise order 3"'))
o.append(obj("lee", [("name", '"lee"'), ("stamps", "0 → 1")], 1240, 456, 584, cls="Card", color=GR, bg="#E6F4EC", attrs=' data-build-in="rise order 4"'))
o.append(note_card(1240, 716, 584, 200, "self 덕분에 따로 쌓여요", "kim.add()는 kim의 도장만, lee.add()는 lee의 도장만 늘려요.", K6, ' data-build-in="rise order 5"'))
W("x-card", o, "카페 도장 카드를 만들어요. 3파트에서 본 것처럼 stamps 칸은 재료로 받지 않고 0에서 시작해요. add 메서드는 자기 도장을 하나 늘려요. kim.add()를 세 번 부르면 self는 매번 kim이라서 kim의 도장만 3개가 돼요. lee는 따로 1개예요. 같은 틀로 찍었지만 카드마다 칸이 따로 있어서 서로 섞이지 않아요. 26에서 이 카드에 가게 이름처럼 모두가 같이 쓰는 값을 더해요." + REAL)

# ---------- wrap up ----------
trouble([("TypeError: ... missing 1 required positional argument", "찍을 때 재료가 모자라요", "self 뒤 칸 수만큼"),
         ("TypeError: ... takes 0 positional arguments but 1 was given", "메서드에 self가 없어요", "def intro(self):"),
         ("TypeError: Bread() takes no arguments", "__init__ 이름이 틀렸어요", "밑줄 두 개씩"),
         ("AttributeError: 'Bread' object has no attribute ...", "칸 이름 오타이거나 self.를 뺐어요", "self.이름 = 값"),
         ("NameError: name 'flavor' is not defined", "메서드 안에서 self.flavor 대신 flavor를 썼어요", "self.flavor"),
         ("<__main__.Bread object at 0x...>", "붕어빵을 통째로 print했어요", "a.flavor로, 25의 __str__"),
         ("TypeError: ... missing 1 required positional argument: 'self'", "a = Bread처럼 괄호 없이 틀을 담았어요", "Bread(재료)")],
        "헷갈리면 self 자리에 붕어빵 이름(a)을 넣어 소리 내어 읽어 봐요.",
        "이번 챕터에서 자주 만나는 일을 모았어요. 1번부터 3번은 칸 수와 이름이 안 맞을 때 나는 TypeError예요. 4번은 칸 이름을 틀렸거나 __init__에서 self.를 빼먹었을 때 나요. 5번은 메서드 안에서 자기 값을 꺼낼 때 self.를 빼먹으면 나요. __init__의 재료 flavor는 __init__이 끝나면 사라졌기 때문이에요. 6번은 오류가 아니라 25에서 해결해요. 7번처럼 괄호 없이 a = Bread라고 적으면 붕어빵이 아니라 틀 자체가 담겨요. 그래서 a.intro()를 부르면 self에 넣을 붕어빵이 없다는 오류가 나요. 막히면 self 자리에 a를 넣어 a.flavor = 팥처럼 소리 내어 읽어 봐요.", cmd_w=330)

cheatsheet([("class Bread:", "틀 만들기", MD), ('Bread("팥", 1000)', "붕어빵 찍기", BR), ("def __init__(self, ...)", "찍을 때 재료 넣기", K3), ("self.flavor = flavor", "붕어빵에 칸 붙이기", K3),
            ("self", "지금 그 붕어빵", BR), ("def intro(self):", "메서드 만들기", K4), ("a.intro()", "Bread.intro(a)와 같아요", K4), ("a.flavor", "속성 꺼내기", K2)],
           ["self는 \"방금 찍은 붕어빵\", \"메서드를 부른 붕어빵\"이에요", "다음 단계: 25에서 __str__, __repr__로 붕어빵을 보기 좋게 찍어요"],
           "이번 챕터에서 쓴 모양을 한 장에 모았어요. class로 틀을 만들고, 틀 이름 뒤에 괄호와 재료를 넣어 붕어빵을 찍어요. __init__은 찍을 때 저절로 불려서 self.이름 = 값으로 붕어빵에 칸을 붙여요. self는 __init__에서는 방금 찍은 붕어빵, 메서드에서는 그 메서드를 부른 붕어빵이에요. 25에서는 print했을 때 이상한 글자 대신 보기 좋은 글자가 나오게 만들어요.")

finish([("Lightbulb", K1, "왜 필요한가", "딕셔너리와 함수의 불편함, 틀과 붕어빵 그림, 이미 써 온 틀", "c-why", "c-type"),
        ("Archive", K2, "가장 작은 틀", "class와 pass, 점으로 값 붙이기, 손으로 붙일 때의 문제", "m-empty", "m-tedious"),
        ("Code", K3, "self와 __init__", "함수에서 __init__으로, self 따라가기, 왼쪽과 오른쪽", "s-func", "s-start"),
        ("Settings", K4, "메서드", "intro 만들기, Bread.intro(a), 값 바꾸기와 return, 비교", "f-method", "f-compare"),
        ("Warning", K5, "오류와 함정", "재료 수, self 빠짐, __init__ 이름, print 결과", "t-missing", "t-print"),
        ("Star", K6, "실습", "붕어빵 주문, 카페 음료 이름표, 도장 카드", "x-order", "x-card")],
       "여섯 파트로 나눴어요. 1파트는 딕셔너리로 만들 때의 불편함과 틀과 붕어빵 그림이에요. 2파트는 가장 작은 틀을 만들고 손으로 값을 붙여 봐요. 3파트가 오늘의 중심이에요. 19의 함수에서 출발해 __init__과 self를 한 걸음씩 봐요. 4파트는 메서드, 5파트는 자주 나는 오류, 6파트는 가게와 카페 실습이에요. 파트마다 새 커널에서 위에서부터 차례로 실행해요.",
       "클래스 1 (붕어빵 틀과 붕어빵)")
