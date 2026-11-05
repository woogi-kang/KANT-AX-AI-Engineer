"""Generates every slide of the __str__ and __repr__ deck (25) and slides/deck.json.

Story: picks up the Bread class from chapter 24. A 붕어빵 printed whole shows <__main__.Bread object at 0x...>, so the
deck draws the special methods Python looks up at set moments (__init__ when made, __str__ for print/str/f-string,
__repr__ for the last line of a cell and values inside a list). Part 2 builds __str__ and compares it with 24's intro().
Part 3 finds the places __str__ does not cover, links them to '팥' versus 팥, builds __repr__ in code form and shows
print borrowing __repr__ (len and + are shown read-only). Part 4 sorts a list of objects with key=lambda and changes
state with methods guarded by if. Part 5 collects the usual errors, and part 6 is a 붕어빵 stall and a cafe menu.
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
EB2 = "2. __str__"
EB3 = "3. __repr__"
EB4 = "4. 붕어빵 여러 개 다루기"
EB5 = "5. 오류와 함정"
EB6 = "6. 실습"

B_INIT = ["class Bread:", "    def __init__(self, flavor, price):", "        self.flavor = flavor", "        self.price = price"]
B_STR = ["    def __str__(self):", '        return f"{self.flavor} 붕어빵 {self.price:,}원"']
B_REPR = ["    def __repr__(self):", "        return f\"Bread('{self.flavor}', {self.price})\""]
AB = ['a = Bread("팥", 1000)', 'b = Bread("슈크림", 1200)']
ADDR = "0x7f6735bb38c0"


def moment(left, top, w, when, who, order, color, bg, h=96, ww=420, lbl=""):
    """One row of "when Python calls what": the moment on the left, the special method it looks for on the right."""
    return (f'<div data-build-in="rise order {order}" style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:{CARD};border:2px solid {LINE};border-left:10px solid {color};border-radius:16px;padding:0 26px;display:flex;flex-direction:row;align-items:center;gap:22px">'
            + p(f"width:{ww}px;flex:none;font-family:{MONO if when.isascii() else SANS};font-size:28px;font-weight:700;color:{INK};white-space:pre", e(when))
            + f'<x-shape kind="arrow-right" style="width:56px;height:28px;flex:none;background:{color}"></x-shape>'
            + (p(f"font-size:24px;font-weight:700;color:{SUB};white-space:nowrap", lbl) if lbl else "")
            + chip(who, color, bg, 28) + '</div>')


# ---------- cover ----------
cover([("class Bread:", "#C7B8F2"), ("    def __str__(self):", W_), ('        return "팥 붕어빵 1,000원"', "#F2C48D"), ("", W_),
       ("print(a)", "#8FD8DE"), ("# 팥 붕어빵 1,000원", "#9AA1AE"), ("# (전에는 <__main__.Bread object at ...>)", "#9AA1AE")],
      "클래스 2<br>__str__과<br>__repr__", "print했을 때<br>붕어빵이 보이게 만들기",
      "24에서 붕어빵 틀을 만들었어요. 그런데 붕어빵을 통째로 print하면 꺾쇠괄호 안에 낯선 글자가 나왔어요. 이번 챕터는 그 글자를 우리가 원하는 글자로 바꿔요. 파이썬이 정해진 순간에 알아서 부르는 메서드 두 개, __str__과 __repr__을 배워요. 왜 필요한지, 언제 불리는지, 둘이 어떻게 다른지를 차례로 봐요. 그다음 붕어빵을 여러 개 담아 정렬하고, 판매할 때마다 재고가 줄어드는 노점을 만들어요.", h1size=84)

ready([("class, __init__, self", "24"), ("메서드와 a.intro()", "24"), ("f-string과 칸 맞추기", "13"), ("return과 print의 차이", "19"), ("sorted와 key=lambda", "22")], "24",
      "09에서 만든 hello-uv 폴더를 VS Code로 열고, basics.ipynb를 다시 열어요. 24의 Bread 틀에서 이어서 해요. __init__과 self가 헷갈리면 24의 3파트를 먼저 봐요. 이번 챕터의 두 메서드는 글자를 return해야 해서 19의 return과 print의 차이가 중요해요. 4파트에서는 22의 sorted와 key=lambda를 써요. 슬라이드의 출력은 tools/demo.sh가 hello-uv 커널에서 같은 셀을 실제로 실행한 결과예요. 0x로 시작하는 주소는 실행할 때마다 달라져요.")

# ---------- part 1 ----------
o = [sec("w-why")] + head(EB1, "숫자와 리스트는 잘 보이는데, 붕어빵은 안 보여요", K1)
o += cell({"id": "c-w1", "lines": ["print(3)", 'print("팥")', "print([1, 2])"], "n": 1, "out": ["3", "팥", "[1, 2]"]}, 96, 196, 760, sel="c-w1")
o += cell({"id": "c-w2", "lines": B_INIT + [""] + AB + ["print(a)", "print([a, b])"], "n": 2, "out": [f"<__main__.Bread object at {ADDR}>", "[<__main__.Bread object at 0x7f6735bb38c0>, <__main__.Bread object at 0x7f6735dc4a50>]"], "attrs": ' data-build-in="rise order 1"'}, 96, 520, 1728, sel="c-w2")
o.append(note_card(900, 196, 924, 280, "파이썬은 우리 붕어빵을 몰라요", "3, \"팥\", 리스트는 파이썬이 만든 틀이라 보여 주는 법을 알아요. Bread는 우리가 만든 틀이라 몰라요.", K1, ' data-build-in="rise order 2"'))
W("w-why", o, "24의 마지막 오류 장면에서 시작해요. 숫자, 글자, 리스트를 print하면 우리가 넣은 그대로 보여요. 그런데 우리가 만든 붕어빵을 print하면 꺾쇠괄호 안에 낯선 글자가 나와요. 리스트에 담아 찍어도 마찬가지예요. int, str, list는 파이썬이 만든 틀이라 어떻게 보여 줄지 이미 정해져 있어요. Bread는 우리가 오늘 만든 틀이라 파이썬이 보여 주는 법을 몰라요. 그래서 틀에 보여 주는 법을 적어 줘야 해요. 주소는 실행할 때마다 달라요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p1", "왜 필요한가"))

o = [sec("w-big")] + head(EB1, "정해진 순간에 파이썬이 틀에서 찾아 부르는 메서드", K1)
o.append(mold(96, 196, 620, 520, "class Bread", ["__init__  찍을 때", "", "__str__   print할 때", "", "__repr__  리스트나", "          셀에서 볼 때", "", "intro     우리가 부를 때"], ' data-build-in="rise order 1"', fs=27))
o.append(moment(760, 196, 1064, 'Bread("팥", 1000)', "__init__", 2, K3, K3BG))
o.append(moment(760, 308, 1064, "print(a)", "__str__", 3, K2, K2BG))
o.append(moment(760, 420, 1064, "셀 마지막 줄의 a", "__repr__", 4, K3, K3BG))
o.append(moment(760, 532, 1064, "print([a, b])", "__repr__", 5, K3, K3BG))
o.append(note_card(760, 650, 1064, 240, "앞뒤 밑줄 두 개 = 파이썬과 약속한 이름", "a.__str__()처럼 직접 부르지 않아요. 이름만 맞게 적어 두면 그 순간에 파이썬이 찾아서 불러요. 없으면 기본 모양(<... object at 0x...>)을 써요.", K1, ' data-build-in="rise order 6"'))
W("w-big", o, "큰 그림을 봐요. 틀 안의 메서드 중에 앞뒤로 밑줄이 두 개씩 붙은 것들은 파이썬과 약속한 이름이에요. 24의 __init__이 그랬어요. 찍는 순간 파이썬이 틀에서 __init__을 찾아 불렀어요. 마찬가지로 print할 때는 __str__을, 셀 마지막 줄이나 리스트 안에서 보여 줄 때는 __repr__을 찾아요. 우리는 이 메서드를 직접 부르지 않고, 이름만 맞게 적어 둬요. 틀에 없으면 파이썬은 앞 장에서 본 기본 모양을 써요. intro처럼 우리가 이름을 지은 메서드는 우리가 직접 불러야 해요.")

o = [sec("w-min")] + head(EB1, "가장 짧은 __str__: 글자 하나를 돌려주기", K1)
o += cell({"id": "c-w3", "lines": B_INIT + ["", "    def __str__(self):", '        return "붕어빵이에요"', "", 'a = Bread("팥", 1000)', "print(a)"], "n": 3, "out": ["붕어빵이에요"]}, 96, 196, 1100, sel="c-w3")
o.append(hl(96, 196, 1100, 5, 2, "run", 1, "새로 넣은 두 줄"))
o.append(note_card(1240, 196, 584, 300, "print(a)가 바뀌었어요", "낯선 글자 대신 __str__이 돌려준 글자가 나왔어요.", K1, ' data-build-in="rise order 2"'))
o.append(note_card(1240, 526, 584, 330, "return이에요", "print가 대신 찍을 수 있게 글자를 돌려줘요. 안에서 print하지 않아요.", GR, ' data-build-in="rise order 3"'))
o.append(caption("print(a)를 치면 파이썬이 a의 __str__을 불러 그 글자를 찍어요.", 944))
W("w-min", o, "가장 짧은 __str__을 만들어요. 틀 안에 def __str__(self)를 적고 글자 하나를 return했어요. print(a)를 쳤더니 낯선 글자 대신 붕어빵이에요가 나왔어요. print가 a를 찍기 전에 a의 틀에서 __str__을 찾아 부르고, 돌려받은 글자를 찍은 거예요. 여기서 중요한 건 print가 아니라 return이라는 점이에요. 19에서 배운 것처럼 return한 글자를 print가 받아서 찍어요. 지금은 어떤 붕어빵이든 같은 글자가 나와요. 다음 파트에서 맛과 가격이 들어가게 바꿔요." + REAL)

# ---------- part 2 ----------
o = [sec("s-basic")] + head(EB2, "__str__에 self의 값을 넣어 붕어빵마다 다르게", K2)
o += cell({"id": "c-s1", "lines": B_INIT + [""] + B_STR + [""] + AB + ["print(a)", "print(b)"], "n": 1, "out": ["팥 붕어빵 1,000원", "슈크림 붕어빵 1,200원"]}, 96, 196, 1100, sel="c-s1")
o.append(hl(96, 196, 1100, 5, 2, "run", 1, "메뉴판 글씨"))
o.append(obj("a", [("flavor", '"팥"'), ("price", "1000")], 1240, 196, 584, attrs=' data-build-in="rise order 2"'))
o.append(pill("팥 붕어빵 1,000원", 1240, 450, K2, K2BG, ' data-build-in="rise order 3"', 30))
o.append(note_card(1240, 560, 584, 300, "손님에게 보여 주는 글씨", "__str__은 메뉴판처럼 사람이 읽기 좋은 글자를 돌려줘요.", K2, ' data-build-in="rise order 4"'))
W("s-basic", o, "__str__ 안에서 self를 쓰면 붕어빵마다 다른 글자를 돌려줄 수 있어요. 13의 f-string에 self.flavor와 self.price를 넣고, 가격에는 천 단위 콤마를 붙였어요. print(a)에서는 self가 a라서 팥 붕어빵 1,000원이, print(b)에서는 슈크림 붕어빵 1,200원이 나와요. __str__은 손님에게 보여 주는 메뉴판 글씨라고 생각하면 돼요. 사람이 읽기 좋은 글자로 적어요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p2", "__str__"))

o = [sec("s-where")] + head(EB2, "print 말고도 글자가 필요한 곳에서 불려요", K2)
o += cell({"id": "c-s2", "lines": ["print(str(a))", 'print(f"주문: {a}")', 'print("오늘의 빵:", b)'], "n": 2, "out": ["팥 붕어빵 1,000원", "주문: 팥 붕어빵 1,000원", "오늘의 빵: 슈크림 붕어빵 1,200원"]}, 96, 196, 1100, sel="c-s2")
o += cell({"id": "c-s3", "lines": ['msg = "포장할게요: " + str(a)', "print(msg)"], "n": 3, "out": ["포장할게요: 팥 붕어빵 1,000원"], "attrs": ' data-build-in="rise order 4"'}, 96, 600, 1100, sel="c-s3")
o.append(callout(1240, 196, 584, 110, "str(a)", "12의 타입 바꾸기. 글자로 바꿔요", K2, 1, 26))
o.append(callout(1240, 320, 584, 110, 'f"{a}"', "f-string 중괄호 안", K2, 2, 26))
o.append(callout(1240, 444, 584, 110, "print(\"...\", b)", "쉼표 뒤에 넣어도", K2, 3, 26))
o.append(note_card(1240, 600, 584, 270, "글자로 바꿀 때마다", "파이썬이 붕어빵을 글자로 바꿔야 할 때 __str__을 불러요.", GRAY, ' data-build-in="rise order 5"'))
W("s-where", o, "__str__은 print할 때만 불리는 게 아니에요. 12에서 숫자를 글자로 바꾸던 str()에 붕어빵을 넣어도, f-string 중괄호 안에 넣어도, print에 쉼표로 여러 개를 넘겨도 불려요. 공통점은 파이썬이 붕어빵을 글자로 바꿔야 하는 순간이라는 거예요. str(a)로 바꾼 글자는 더하기로 다른 글자와 이을 수도 있어요." + REAL)

o = [sec("s-intro")] + head(EB2, "24의 intro()와 무엇이 다른가요", K2)
o.append(side(96, 196, 846, 360, "intro (24)", ["    def intro(self):", '        print(self.flavor, "붕어빵")', "", "a.intro()", "print(a)   # 여전히 <... object>"], [], GRAY, "#F1F0EC", fs=25))
o.append(side(978, 196, 846, 360, "__str__", ["    def __str__(self):", '        return f"{self.flavor} 붕어빵"', "", "print(a)", 'f"주문: {a}"'], [], K2, K2BG, ' data-build-in="rise order 1"', fs=25))
CW = [300, 680, 680]
o.append(trow(96, 590, 1728, ["", "intro", "__str__"], CW, head=True))
for i, r in enumerate([["누가 부르나요", "우리가 a.intro()로", "print, str, f-string이 알아서"],
                       ["무엇을 하나요", "안에서 바로 print", "글자를 return"],
                       ["다른 글자와 잇기", "안 돼요", "f-string, 더하기로 이어요"]]):
    o.append(trow(96, 670 + i * 84, 1728, r, CW, order=2 + i, h=72, fs=26))
W("s-intro", o, "24에서 만든 intro도 붕어빵을 소개했어요. 그런데 __str__을 쓰는 이유가 있어요. intro는 우리가 직접 a.intro()로 불러야 하고, 안에서 바로 print해 버려요. 그래서 print(a)는 여전히 낯선 글자가 나오고, 소개 글자를 주문서나 영수증에 이어 붙일 수도 없어요. __str__은 print, str, f-string이 알아서 부르고 글자를 돌려줘요. 돌려받은 글자는 어디에든 다시 쓸 수 있어요. 파이썬이 원래 쓰던 방법에 우리 붕어빵이 끼어드는 거예요.")

# ---------- part 3 ----------
o = [sec("r-cell")] + head(EB3, "__str__을 만들었는데도 낯선 글자가 남아요", K3)
o += cell({"id": "c-r1", "lines": B_INIT + [""] + B_STR + [""] + AB + ["a"], "n": 1, "out": ["<__main__.Bread at 0x7febaa53c6e0>"]}, 96, 196, 1100, sel="c-r1")
o += cell({"id": "c-r2", "lines": ["print([a, b])"], "n": 2, "out": ["[<__main__.Bread object at 0x7febaa53c6e0>, <__main__.Bread object at 0x7febaa7fb890>]"], "attrs": ' data-build-in="rise order 2"'}, 96, 760, 1728, sel="c-r2")
o.append(hl(96, 196, 1100, 10, 1, "mark", 1, "print 없이"))
o.append(note_card(1240, 196, 584, 250, "셀 마지막 줄", "print 없이 이름만 적으면 __str__을 쓰지 않아요.", K3, ' data-build-in="rise order 1"'))
o.append(note_card(1240, 476, 584, 250, "리스트 안", "리스트를 print해도 안의 붕어빵은 __str__을 쓰지 않아요.", K3, ' data-build-in="rise order 3"'))
W("r-cell", o, "__str__을 만들었는데도 낯선 글자가 남는 곳이 두 군데 있어요. 하나는 셀 마지막 줄에 print 없이 이름만 적었을 때예요. 10에서 배운 대로 셀 마지막 줄의 값은 저절로 보이는데, 이때는 __str__이 아닌 다른 메서드를 써요. 노트북은 object라는 말을 빼고 보여 줘서 모양이 조금 달라요. 다른 하나는 붕어빵을 리스트에 담아 print했을 때예요. 리스트는 __str__로 찍지만, 리스트 안의 값은 __repr__이라는 메서드로 보여 줘요. 다음 장에서 이 차이를 이미 본 적이 있다는 걸 확인해요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p3", "__repr__"))

o = [sec("r-known")] + head(EB3, "이 차이는 \"팥\"에서 이미 봤어요", K3)
o += cell({"id": "c-r3", "lines": ['"팥"'], "n": 3, "out": ["'팥'"]}, 96, 196, 700, sel="c-r3")
o += cell({"id": "c-r4", "lines": ['print("팥")', 'print(["팥", "슈크림"])', 'print(str("팥"))', 'print(repr("팥"))'], "n": 4, "out": ["팥", "['팥', '슈크림']", "팥", "'팥'"], "attrs": ' data-build-in="rise order 1"'}, 96, 400, 900, sel="c-r4")
o.append(card(1040, 196, 380, 300, p(f"font-size:24px;font-weight:700;color:{K2}", "str  손님용") + p(f"font-family:{MONO};font-size:56px;font-weight:700;color:{INK}", "팥") + p(f"font-size:22px;color:{SUB}", "print, str()"), K2, ' data-build-in="rise order 2"'))
o.append(card(1444, 196, 380, 300, p(f"font-size:24px;font-weight:700;color:{K3}", "repr  만든 사람용") + p(f"font-family:{MONO};font-size:56px;font-weight:700;color:{INK}", "'팥'") + p(f"font-size:22px;color:{SUB}", "셀 마지막 줄, 리스트 안, repr()"), K3, ' data-build-in="rise order 3"'))
o.append(note_card(1040, 530, 784, 330, "따옴표가 있고 없고", "글자라는 걸 알 수 있게 따옴표까지 보여 주는 게 repr이에요. 리스트 안의 글자에 따옴표가 붙던 이유예요.", K3, ' data-build-in="rise order 4"'))
W("r-known", o, "str과 repr의 차이는 이미 본 적이 있어요. 셀 마지막 줄에 팥을 적으면 따옴표가 붙은 팥이 나왔어요. print하면 따옴표 없이 팥만 나와요. 13에서 리스트를 찍었을 때 안의 글자마다 따옴표가 붙어 있던 것도 같은 이유예요. 파이썬은 글자를 보여 주는 방법을 두 가지 갖고 있어요. 손님에게 보여 주는 str은 따옴표 없이, 만든 사람이 보는 repr은 글자라는 게 보이게 따옴표까지 붙여요. str()과 repr() 함수로 직접 확인할 수도 있어요. 붕어빵의 __str__과 __repr__이 바로 이 두 방법이에요." + REAL)

o = [sec("r-basic")] + head(EB3, "__repr__까지 만들면 어디서나 보여요", K3)
o += cell({"id": "c-r5", "lines": B_INIT + [""] + B_STR + [""] + B_REPR + [""] + AB + ["a"], "n": 5, "out": ["Bread('팥', 1000)"]}, 96, 196, 1100, sel="c-r5")
o.append(hl(96, 196, 1100, 8, 2, "run", 1, "주문표 글씨"))
o += cell({"id": "c-r6", "lines": ["print(a)", "print([a, b])"], "n": 6, "out": ["팥 붕어빵 1,000원", "[Bread('팥', 1000), Bread('슈크림', 1200)]"], "attrs": ' data-build-in="rise order 2"'}, 96, 816, 1728, sel="c-r6")
o.append(note_card(1240, 196, 584, 420, "코드처럼 적는 게 약속이에요", "Bread('팥', 1000)을 복사해서 셀에 붙여 넣으면 같은 붕어빵이 다시 찍혀요. 만든 사람이 무엇이 들었는지 한눈에 봐요.", K3, ' data-build-in="rise order 3"'))
W("r-basic", o, "__repr__을 더 만들어요. __repr__은 만든 사람이 보는 주문표 글씨예요. 보통 그 붕어빵을 다시 찍는 코드 모양으로 적어요. Bread('팥', 1000)을 그대로 복사해서 셀에 붙여 넣으면 같은 붕어빵이 다시 만들어져요. 맛 글자에는 따옴표를 직접 넣었어요. 이제 셀 마지막 줄에서도, 리스트 안에서도 낯선 글자 대신 Bread('팥', 1000)이 보여요. print(a)는 여전히 __str__의 메뉴판 글씨를 써요." + REAL)

o = [sec("r-who")] + head(EB3, "언제 어느 쪽이 불리는지 한 장으로", K3)
CW = [520, 380, 380, 380]
o.append(trow(96, 196, 1728, ["이렇게 쓰면", "불리는 메서드", "둘 다 있을 때", "아무것도 없을 때"], CW, head=True))
for i, r in enumerate([['Bread("팥", 1000)', "__init__", "찍기", "재료 없이 찍기"],
                       ["print(a), str(a), f\"{a}\"", "__str__", "팥 붕어빵 1,000원", "<... object at 0x...>"],
                       ["셀 마지막 줄의 a", "__repr__", "Bread('팥', 1000)", "<... at 0x...>"],
                       ["print([a, b])", "안의 값은 __repr__", "[Bread('팥', 1000), ...]", "[<... object ...>, ...]"],
                       ["a.intro()", "우리가 부른 것", "우리가 부를 때만", "AttributeError"]]):
    o.append(trow(96, 276 + i * 100, 1728, r, CW, order=1 + i, h=88, fs=24))
o.append(caption("print는 손님 글씨(__str__), 그 밖에 개발자가 볼 때는 주문표 글씨(__repr__)예요.", 800))
W("r-who", o, "세 메서드가 언제 불리는지 표로 모았어요. 찍을 때는 __init__, print와 str과 f-string은 __str__, 셀 마지막 줄과 리스트 안의 값은 __repr__이에요. 오른쪽 두 칸은 메서드가 있을 때와 없을 때 무엇이 보이는지예요. intro처럼 우리가 이름을 지은 메서드는 우리가 부를 때만 실행돼요. 손님에게 보여 줄 땐 __str__, 개발하면서 무엇이 들었는지 확인할 땐 __repr__이라고 기억하면 돼요.")

o = [sec("r-only")] + head(EB3, "하나만 만든다면 __repr__이에요", K3)
o += cell({"id": "c-r7", "lines": B_INIT + [""] + B_REPR + [""] + AB + ["print(a)", "print([a, b])"], "n": 7, "out": ["Bread('팥', 1000)", "[Bread('팥', 1000), Bread('슈크림', 1200)]"]}, 96, 196, 1100, sel="c-r7")
o.append(hl(96, 196, 1100, 5, 2, "run", 1, "__repr__만"))
o.append(note_card(1240, 196, 584, 330, "print도 __repr__을 써요", "__str__이 없으면 print는 __repr__을 빌려 써요. 반대로는 빌려 쓰지 않아요.", K3, ' data-build-in="rise order 2"'))
o.append(note_card(1240, 556, 584, 300, "언제 둘 다 만드나요", "손님용 글씨가 따로 필요할 때 __str__을 더해요. 영수증, 메뉴판처럼요.", GRAY, ' data-build-in="rise order 3"'))
W("r-only", o, "이번엔 __str__ 없이 __repr__만 만들었어요. print(a)도 __repr__의 글자를 찍었어요. __str__이 없으면 print는 __repr__을 빌려 써요. 반대로 __str__만 있으면 리스트 안이나 셀 마지막 줄에서는 빌려 쓰지 않아서 3파트 첫 장처럼 낯선 글자가 남아요. 그래서 하나만 만든다면 __repr__이 더 많은 곳을 해결해요. 영수증이나 메뉴판처럼 손님에게 보여 줄 글씨가 따로 필요할 때 __str__을 더해요." + REAL)

o = [sec("r-more")] + head(EB3, "참고, 읽기만: len과 +도 같은 원리예요", GRAY)
o += cell({"id": "c-r8", "lines": ["print(len([1, 2, 3]))", "print([1, 2, 3].__len__())", "print(3 + 4)", "print((3).__add__(4))"], "n": 8, "out": ["3", "3", "7", "7"]}, 96, 196, 1100, sel="c-r8")
o.append(moment(96, 640, 1728, "len(xs)", "__len__", 1, GRAY, "#F1F0EC", lbl="파이썬이 찾는 메서드"))
o.append(moment(96, 752, 1728, "a + b", "__add__", 2, GRAY, "#F1F0EC", lbl="파이썬이 찾는 메서드"))
o.append(note_card(1240, 196, 584, 380, "따라 치지 않아도 돼요", "리스트 틀에는 __len__이, 숫자 틀에는 __add__가 들어 있어요. 이 과정에서는 __init__, __str__, __repr__ 세 개만 만들어요.", GRAY, ' data-build-in="rise order 3"'))
W("r-more", o, "참고로 읽기만 하는 장이에요. 밑줄 두 개짜리 메서드는 세 개만 있는 게 아니에요. len을 부르면 파이썬은 리스트 틀의 __len__을, 더하기를 하면 숫자 틀의 __add__를 찾아 불러요. 직접 불러도 같은 결과가 나와요. 우리가 써 온 len과 더하기도 print와 __str__처럼 약속된 이름으로 돌아가고 있었어요. 이 과정에서는 __init__, __str__, __repr__ 세 개만 직접 만들고, 나머지는 이런 게 있다는 것만 알아 두세요." + REAL)

# ---------- part 4 ----------
o = [sec("l-for")] + head(EB4, "붕어빵 여러 개를 리스트에 담아 하나씩 찍어요", K4)
LB = B_INIT + [""] + B_STR + [""] + B_REPR + ["", 'breads = [Bread("팥", 1000), Bread("슈크림", 1200), Bread("피자", 1500)]', "for b in breads:", "    print(b)"]
o += cell({"id": "c-l1", "lines": LB, "n": 1, "out": ["팥 붕어빵 1,000원", "슈크림 붕어빵 1,200원", "피자 붕어빵 1,500원"]}, 96, 196, 1300, sel="c-l1")
o.append(hl(96, 196, 1300, 12, 2, "run", 1))
o.append(note_card(1440, 196, 384, 330, "for로 꺼낸 b", "b는 붕어빵 하나라서 print(b)는 __str__을 써요.", K4, ' data-build-in="rise order 2"'))
W("l-for", o, "이제 __str__과 __repr__이 모두 있는 틀로 붕어빵 세 개를 리스트에 담아요. for로 하나씩 꺼내 print하면 b는 붕어빵 하나라서 __str__의 메뉴판 글씨가 나와요. 24의 실습에서는 b.intro()를 불렀는데, 이제는 print(b)만 쳐도 돼요. 이 셀의 breads를 다음 두 장에서 계속 써요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p4", "붕어빵 여러 개 다루기"))

o = [sec("l-comp")] + head(EB4, "23의 컴프리헨션으로 맛만, 가격만, 비싼 것만", K4)
o += cell({"id": "c-l2", "lines": ["print([b.flavor for b in breads])", "print(sum([b.price for b in breads]))", "print([b for b in breads if b.price >= 1200])"], "n": 2, "out": ["['팥', '슈크림', '피자']", "3700", "[Bread('슈크림', 1200), Bread('피자', 1500)]"]}, 96, 196, 1300, sel="c-l2")
o.append(callout(96, 480, 1728, 100, "b.flavor", "붕어빵마다 맛 칸만 꺼내 모아요", K4, 1, 26))
o.append(callout(96, 594, 1728, 100, "b.price", "가격만 모아 sum에 넘겨요", K4, 2, 26))
o.append(callout(96, 708, 1728, 100, "if b.price >= 1200", "붕어빵을 통째로 골라 담아요. 리스트라서 __repr__이 보여요", K3, 3, 26))
o.append(caption("__repr__이 없었다면 마지막 줄은 <... object at 0x...>뿐이었어요.", 880))
W("l-comp", o, "23의 컴프리헨션을 붕어빵 리스트에 써요. b.flavor로 맛 칸만 모으고, b.price로 가격만 모아 sum에 넘겼어요. 마지막 줄은 1200원 이상인 붕어빵을 통째로 골라 담았어요. 골라 담은 리스트를 print하니 안의 붕어빵은 __repr__로 보여요. __repr__을 만들지 않았다면 무엇이 골라졌는지 알 수 없는 낯선 글자만 나왔을 거예요." + REAL)

o = [sec("l-sort")] + head(EB4, "22의 key=lambda로 가격순 정렬과 가장 비싼 붕어빵", K4)
o += cell({"id": "c-l3", "lines": ["print(sorted(breads, key=lambda b: b.price, reverse=True))", "print(max(breads, key=lambda b: b.price))"], "n": 3, "out": ["[Bread('피자', 1500), Bread('슈크림', 1200), Bread('팥', 1000)]", "피자 붕어빵 1,500원"]}, 96, 196, 1728, sel="c-l3")
o += cell({"id": "c-l4", "lines": ["print(sorted(breads))"], "n": 4, "out": ["TypeError: '<' not supported between instances of 'Bread' and 'Bread'"], "err": True, "attrs": ' data-build-in="rise order 2"'}, 96, 460, 1728, sel="c-l4")
o.append(note_card(96, 650, 846, 240, "key가 꼭 필요해요", "붕어빵끼리는 무엇으로 크기를 비교할지 몰라요. key로 가격을 비교하라고 알려 줘요.", RED, ' data-build-in="rise order 3"'))
o.append(note_card(978, 650, 846, 240, "max는 붕어빵 하나", "max가 돌려준 건 리스트가 아니라 붕어빵 하나라서 print가 __str__을 써요.", K4, ' data-build-in="rise order 4"'))
W("l-sort", o, "22에서 배운 key=lambda를 붕어빵에 써요. 가격 칸으로 비교하라고 알려 주면 비싼 순으로 정렬되고, max로 가장 비싼 붕어빵을 고를 수 있어요. key 없이 sorted를 부르면 TypeError가 나요. 숫자끼리는 크기를 비교할 수 있지만 붕어빵끼리는 맛으로 비교할지 가격으로 비교할지 몰라서예요. max가 돌려준 값은 붕어빵 하나라서 print가 __str__의 메뉴판 글씨를 찍었어요." + REAL)

o = [sec("st-sell")] + head(EB4, "메서드로 재고와 판매 개수를 바꿔요", K4)
SS = ["class Stall:", "    def __init__(self, name, stock):", "        self.name = name", "        self.stock = stock", "        self.sold = 0", "", "    def sell(self, qty):", "        self.stock = self.stock - qty", "        self.sold = self.sold + qty", "", "    def __str__(self):", '        return f"{self.name}: 남은 {self.stock}개, 판매 {self.sold}개"', "", 's = Stall("팥", 10)', "print(s)", "s.sell(3)", "print(s)"]
o += cell({"id": "c-st1", "lines": SS, "n": 5, "out": ["팥: 남은 10개, 판매 0개", "팥: 남은 7개, 판매 3개"]}, 96, 176, 1200, sel="c-st1")
o.append(hl(96, 176, 1200, 6, 3, "mark", 1, "값 바꾸기"))
o += table(1340, 176, 484, [("일", 170), ("stock", 120), ("sold", 100)], [["찍기", "10", "0"], ["sell(3)", "7", "3"]], 2, K4)
o.append(note_card(1340, 420, 484, 420, "상태가 남아요", "sell을 부를 때마다 self의 칸이 바뀌고, 바뀐 값은 다음에 부를 때까지 남아요. print(s)는 지금 상태를 보여 줘요.", K4, ' data-build-in="rise order 4"'))
W("st-sell", o, "붕어빵 노점 하나를 틀로 만들어요. 재고는 재료로 받고, 판매 개수는 24에서 본 것처럼 0에서 시작해요. sell 메서드는 판 개수만큼 재고를 빼고 판매 개수를 더해요. sell을 부를 때마다 칸의 값이 바뀌고, 바뀐 값은 다음에 부를 때까지 노점에 남아 있어요. 이렇게 객체가 지금 들고 있는 값을 상태라고 불러요. __str__이 있어서 print(s)만 쳐도 지금 상태가 보여요." + REAL)

o = [sec("st-if")] + head(EB4, "재고가 모자라면 팔지 않게 if로 막아요", K4)
SI = ["class Stall:", "    def __init__(self, name, stock):", "        self.name = name", "        self.stock = stock", "        self.sold = 0", "", "    def sell(self, qty):", "        if qty > self.stock:", '            return "재고가 모자라요"', "        self.stock = self.stock - qty", "        self.sold = self.sold + qty", '        return "판매 완료"', "", 's = Stall("팥", 5)', "print(s.sell(3))", "print(s.sell(4))", "print(s.stock, s.sold)"]
o += cell({"id": "c-st2", "lines": SI, "n": 6, "out": ["판매 완료", "재고가 모자라요", "2 3"]}, 96, 176, 1200, sel="c-st2")
o.append(hl(96, 176, 1200, 7, 2, "err", 1, "17의 if"))
o.append(note_card(1340, 176, 484, 330, "return에서 바로 끝나요", "19에서 배운 대로 return을 만나면 아래 줄은 실행하지 않아요.", K4, ' data-build-in="rise order 2"'))
o.append(note_card(1340, 536, 484, 300, "값이 지켜져요", "4개를 팔려고 했지만 재고가 2개라 그대로예요.", GR, ' data-build-in="rise order 3"'))
W("st-if", o, "재고보다 많이 팔면 재고가 마이너스가 돼요. sell 안에 17의 if를 넣어서, 재고가 모자라면 글자를 return하고 바로 끝나게 했어요. 19에서 배운 대로 return을 만나면 아래 줄은 실행하지 않아서 재고와 판매 개수가 바뀌지 않아요. 3개를 판 뒤 남은 2개는 그대로예요. 메서드 안에 값을 지키는 규칙을 둘 수 있다는 게 클래스의 좋은 점이에요." + REAL)

# ---------- part 5 ----------
o = [sec("t-print")] + head(EB5, "__str__ 안에서 print하면 returned non-string", K5)
o += cell({"id": "c-t1", "lines": B_INIT + ["", "    def __str__(self):", '        print(self.flavor, "붕어빵")', ""] + AB + ["print(a)"], "n": 1, "out": ["팥 붕어빵", "TypeError: __str__ returned non-string (type NoneType)"], "err": True}, 96, 196, 1300, sel="c-t1")
o.append(hl(96, 196, 1300, 6, 1, "err", 1, "return이 없어요"))
o.append(note_card(96, 760, 846, 160, "읽는 법", "__str__이 글자 대신 None을 돌려줬어요. return이 없으면 None이에요(19).", RED, ' data-build-in="rise order 2"'))
o.append(note_card(978, 760, 846, 160, "고치기", 'print 대신 return f"{self.flavor} 붕어빵"', GR, ' data-build-in="rise order 3"'))
W("t-print", o, "가장 많이 하는 실수예요. __str__ 안에서 return 대신 print를 썼어요. 출력을 보면 팥 붕어빵이 먼저 찍히고 바로 TypeError가 나요. __str__이 불려서 안의 print가 실행된 뒤, 돌려준 값이 글자가 아니라 None이었기 때문이에요. 19에서 배운 대로 return이 없는 함수는 None을 돌려줘요. __str__과 __repr__은 꼭 글자를 return해요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p5", "오류와 함정"))

o = [sec("t-int")] + head(EB5, "숫자를 돌려줘도 returned non-string", K5)
o += cell({"id": "c-t2", "lines": B_INIT + ["", "    def __str__(self):", "        return self.price", ""] + AB + ["print(a)"], "n": 2, "out": ["TypeError: __str__ returned non-string (type int)"], "err": True}, 96, 196, 1300, sel="c-t2")
o.append(hl(96, 196, 1300, 6, 1, "err", 1, "숫자"))
o.append(note_card(96, 720, 846, 180, "읽는 법", "글자(str)가 아니라 숫자(int)를 돌려줬어요.", RED, ' data-build-in="rise order 2"'))
o.append(note_card(978, 720, 846, 180, "고치기", 'return str(self.price) 또는 return f"{self.price}원"', GR, ' data-build-in="rise order 3"'))
W("t-int", o, "이번엔 return은 했는데 가격 숫자를 그대로 돌려줬어요. 오류 끝의 type int가 숫자를 돌려줬다는 뜻이에요. __str__과 __repr__은 이름 그대로 글자를 돌려줘야 해요. 12에서 배운 str()로 바꾸거나 f-string으로 감싸서 돌려줘요." + REAL)

o = [sec("t-under")] + head(EB5, "밑줄이 하나면 오류 없이 그냥 무시돼요", K5)
o += cell({"id": "c-t3", "lines": B_INIT + ["", "    def _str_(self):", '        return f"{self.flavor} 붕어빵"', ""] + AB + ["print(a)"], "n": 3, "out": ["<__main__.Bread object at 0x7fc8a2a6bcb0>"]}, 96, 196, 1300, sel="c-t3")
o.append(hl(96, 196, 1300, 5, 1, "err", 1, "_str_"))
o.append(note_card(96, 720, 846, 180, "오류가 안 나서 더 찾기 어려워요", "파이썬은 약속된 이름 __str__만 찾아요. _str_은 평범한 메서드예요.", RED, ' data-build-in="rise order 2"'))
o.append(note_card(978, 720, 846, 180, "고치기", "앞뒤로 밑줄 두 개씩 __str__, __repr__", GR, ' data-build-in="rise order 3"'))
W("t-under", o, "밑줄을 하나씩만 적었어요. 24의 __init__ 때는 TypeError가 났는데, 이번에는 오류가 안 나요. 파이썬이 print할 때 __str__을 찾았는데 없어서 그냥 기본 모양을 쓴 거예요. _str_은 이름이 비슷한 평범한 메서드일 뿐이에요. 오류가 없어서 오히려 찾기 어려우니, 낯선 글자가 그대로 나오면 밑줄 개수부터 봐요." + REAL)

o = [sec("t-plus")] + head(EB5, "글자에 붕어빵을 바로 더하면 can only concatenate", K5)
o += cell({"id": "c-t4", "lines": B_INIT + [""] + B_STR + [""] + AB + ['print("주문: " + a)'], "n": 4, "out": ['TypeError: can only concatenate str (not "Bread") to str'], "err": True}, 96, 196, 1300, sel="c-t4")
o.append(hl(96, 196, 1300, 10, 1, "err", 1, "글자 + 붕어빵"))
o.append(note_card(96, 680, 846, 220, "읽는 법", "글자에는 글자만 더할 수 있어요. 더하기는 __str__을 부르지 않아요.", RED, ' data-build-in="rise order 2"'))
o.append(note_card(978, 680, 846, 220, "고치기", '"주문: " + str(a), f"주문: {a}", print("주문:", a)', GR, ' data-build-in="rise order 3"'))
W("t-plus", o, "__str__을 만들었으니 글자에 바로 더해도 될 것 같지만 TypeError가 나요. 글자에는 글자만 더할 수 있다는 뜻이에요. 더하기는 붕어빵을 글자로 바꿔 주지 않아요. 2파트에서 본 것처럼 str(a)로 먼저 바꾸거나, f-string 중괄호에 넣거나, print에 쉼표로 넘기면 __str__이 불려요. 12에서 숫자와 글자를 더할 때 난 오류와 같은 원리예요." + REAL)

# ---------- part 6 ----------
XS = ["class Stall:", "    def __init__(self, flavor, price, stock):", "        self.flavor = flavor", "        self.price = price", "        self.stock = stock", "        self.sold = 0", "", "    def sell(self, qty):", "        if qty > self.stock:", '            return f"{self.flavor} 재고가 모자라요"', "        self.stock = self.stock - qty", "        self.sold = self.sold + qty", '        return f"{self.flavor} {qty}개 판매"', "", "    def __str__(self):", '        return f"{self.flavor}: 판매 {self.sold}개, 매출 {self.sold * self.price:,}원"']
XS2 = ['pat = Stall("팥", 1000, 20)', 'cream = Stall("슈크림", 1200, 10)', "print(pat.sell(5))", "print(cream.sell(12))", "print(cream.sell(4))", "print(pat)", "print(cream)"]
o = [sec("x-stall")] + head(EB6, "붕어빵 노점의 하루 ①: 노점 틀 만들기", K6)
o += cell({"id": "c-x1", "lines": XS, "n": 1}, 96, 176, 1728, sel="c-x1")
o.append(hl(96, 176, 1728, 1, 5, "mark", 1, "__init__: 재료 셋, 판매 0"))
o.append(hl(96, 176, 1728, 7, 6, "err", 2, "sell: if로 막고 상태 바꾸기"))
o.append(hl(96, 176, 1728, 14, 2, "run", 3, "__str__: 매출 글씨"))
o.append(caption("출력이 없는 셀이에요. 틀을 만들기만 했어요.", 880))
W("x-stall", o, "노점의 하루를 두 장에 걸쳐 만들어요. 먼저 틀이에요. __init__은 맛, 가격, 재고를 받고 판매 개수는 0에서 시작해요. sell은 4파트처럼 재고를 확인하고, 팔 수 있으면 상태를 바꾼 뒤 글자를 return해요. __str__은 판매 개수와 가격을 곱한 매출을 천 단위 콤마로 보여 줘요. 이 셀은 틀만 만들어서 출력이 없어요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p6", "실습"))

o = [sec("x-stall2")] + head(EB6, "붕어빵 노점의 하루 ②: 팔고, 막고, 매출 찍기", K6)
o += cell({"id": "c-x1b", "lines": XS2, "n": 2, "out": ["팥 5개 판매", "슈크림 재고가 모자라요", "슈크림 4개 판매", "팥: 판매 5개, 매출 5,000원", "슈크림: 판매 4개, 매출 4,800원"]}, 96, 176, 1000, sel="c-x1b")
o += table(1140, 176, 684, [("일", 260), ("팥 stock", 160), ("슈크림 stock", 180)], [["찍기", "20", "10"], ["pat.sell(5)", "15", "10"], ["cream.sell(12)", "15", "10"], ["cream.sell(4)", "15", "6"]], 1, K6, hi=(2,))
o.append(note_card(1140, 520, 684, 220, "12개는 막혔어요", "재고 10개보다 많아서 if에서 return했어요. 재고는 그대로예요.", RED, ' data-build-in="rise order 5"'))
o.append(note_card(96, 760, 1728, 140, "배운 것 모두", "__init__으로 찍기, 메서드로 상태 바꾸기, if와 return으로 막기, __str__로 보기 좋게 찍기", K6, ' data-build-in="rise order 6"'))
W("x-stall2", o, "앞 셀에서 만든 틀로 팥 노점과 슈크림 노점을 따로 찍었어요. 팥은 5개 팔렸어요. 슈크림 12개는 재고 10개보다 많아서 막혔고, 4개는 팔렸어요. 오른쪽 표에서 줄마다 재고가 어떻게 바뀌는지 보세요. 하루가 끝나면 print로 판매 개수와 매출을 찍어요. __str__이 있어서 print(pat)만 쳐도 돼요." + REAL)

o = [sec("x-menu")] + head(EB6, "카페 메뉴판: 손님용 줄 맞춤과 개발자용 확인", K6)
XM = ["class Drink:", "    def __init__(self, name, price):", "        self.name = name", "        self.price = price", "", "    def __str__(self):", '        return f"{self.name:<7}{self.price:>6,}원"', "", "    def __repr__(self):", "        return f\"Drink('{self.name}', {self.price})\"", "", 'menu = [Drink("latte", 5000), Drink("tea", 4000), Drink("coffee", 4500)]', "for d in sorted(menu, key=lambda d: d.price):", "    print(d)", "print([d for d in menu if d.price < 5000])"]
o += cell({"id": "c-x2", "lines": XM, "n": 3, "out": ["tea     4,000원", "coffee  4,500원", "latte   5,000원", "[Drink('tea', 4000), Drink('coffee', 4500)]"]}, 96, 196, 1300, sel="c-x2")
o.append(hl(96, 196, 1300, 5, 2, "run", 1, "손님용"))
o.append(hl(96, 196, 1300, 8, 2, "mark", 2, "개발자용"))
o.append(note_card(1440, 196, 384, 330, "메뉴판은 __str__", "13의 칸 맞추기로 줄을 맞춰 찍어요.", K2, ' data-build-in="rise order 3"'))
o.append(note_card(1440, 556, 384, 330, "확인은 __repr__", "5000원 미만을 골라 담은 리스트는 주문표 모양으로 보여요.", K3, ' data-build-in="rise order 4"'))
W("x-menu", o, "카페 메뉴판을 만들어요. __str__은 13의 칸 맞추기로 이름은 왼쪽 7칸, 가격은 오른쪽 6칸에 맞춰 손님용 줄을 만들어요. __repr__은 개발자가 확인할 때 쓰는 주문표 모양이에요. 22의 sorted와 key로 가격순 정렬해 하나씩 print하면 메뉴판 줄이 나오고, 23의 컴프리헨션으로 골라 담은 리스트를 print하면 주문표 모양이 나와요. 한 틀에 두 메서드를 다 두면 어디서 찍어도 알아보기 쉬워요." + REAL)

# ---------- wrap up ----------
trouble([("<__main__.Bread object at 0x...>", "__str__이나 __repr__이 없거나 밑줄이 하나예요", "__repr__ 만들기"),
         ("리스트 안만 <... object ...>", "__str__만 만들었어요", "__repr__도 만들기"),
         ("TypeError: __str__ returned non-string (type NoneType)", "안에서 print했어요", "return으로"),
         ("TypeError: __str__ returned non-string (type int)", "숫자를 돌려줬어요", "str()이나 f-string"),
         ("TypeError: can only concatenate str (not \"Bread\") to str", "글자에 붕어빵을 바로 더했어요", "str(a), f\"{a}\""),
         ("TypeError: '<' not supported between instances", "붕어빵끼리 비교할 기준이 없어요", "key=lambda b: b.price"),
         ("재고가 마이너스가 돼요", "메서드에서 값을 확인하지 않았어요", "if와 return으로 막기")],
        "낯선 글자가 나오면 \"지금 파이썬이 어느 메서드를 찾았을까\"부터 생각해요.",
        "이번 챕터에서 자주 만나는 일을 모았어요. 1번과 2번은 어느 메서드가 불리는지와 관련돼요. print는 __str__, 리스트 안은 __repr__이에요. 3번부터 5번은 두 메서드가 꼭 글자를 돌려줘야 해서 생기는 오류예요. 6번은 22의 key를, 7번은 17의 if를 메서드 안에서 쓰면 해결돼요. 낯선 글자가 나오면 지금 파이썬이 어느 메서드를 찾았을지부터 생각해 보세요.", cmd_w=330)

cheatsheet([("def __str__(self):", "print, str, f-string", K2), ("return f\"...\"", "꼭 글자를 돌려주기", K2), ("def __repr__(self):", "셀, 리스트 안, 확인할 때", K3), ("Bread('팥', 1000)", "repr은 코드 모양으로", K3),
            ("__repr__만", "print도 빌려 써요", K3), ("str(a)", "글자로 바꿔 잇기", K2), ("key=lambda b: b.price", "붕어빵 정렬", K4), ("self.stock - qty", "메서드로 상태 바꾸기", K4)],
           ["__str__은 손님용 메뉴판, __repr__은 만든 사람용 주문표예요", "다음 단계: 26에서 틀을 물려받아 슈크림 붕어빵 틀을 만들어요"],
           "이번 챕터의 핵심을 한 장에 모았어요. __str__과 __repr__은 파이썬이 정해진 순간에 알아서 부르는 메서드예요. print와 str과 f-string은 __str__을, 셀 마지막 줄과 리스트 안의 값은 __repr__을 찾아요. 둘 다 꼭 글자를 return해요. 하나만 만든다면 __repr__이에요. 붕어빵 여러 개는 22의 key로 정렬하고, 메서드 안에서 재고 같은 상태를 바꿔요. 26에서는 이 틀을 물려받아 새 틀을 만드는 상속을 배워요.")

finish([("Lightbulb", K1, "왜 필요한가", "print했을 때 낯선 글자, 파이썬이 찾아 부르는 메서드, 가장 짧은 __str__", "w-why", "w-min"),
        ("Code", K2, "__str__", "붕어빵마다 다른 글자, 불리는 곳, intro와 비교", "s-basic", "s-intro"),
        ("Archive", K3, "__repr__", "남는 낯선 글자, '팥'과 팥, 주문표 모양, 한 장 표, 하나만 만든다면", "r-cell", "r-more"),
        ("Settings", K4, "붕어빵 여러 개 다루기", "for, 컴프리헨션, key 정렬, 재고 바꾸기, if로 막기", "l-for", "st-if"),
        ("Warning", K5, "오류와 함정", "print를 쓴 __str__, 숫자 돌려주기, 밑줄 하나, 글자 더하기", "t-print", "t-plus"),
        ("Star", K6, "실습", "노점의 하루 두 장, 카페 메뉴판", "x-stall", "x-menu")],
       "여섯 파트로 나눴어요. 1파트는 붕어빵을 print했을 때의 문제와 파이썬이 알아서 부르는 메서드 그림이에요. 2파트와 3파트가 중심이에요. __str__과 __repr__을 하나씩 만들고, 언제 어느 쪽이 불리는지 표로 정리해요. 4파트는 붕어빵 여러 개를 정렬하고 상태를 바꾸는 메서드, 5파트는 자주 나는 오류, 6파트는 노점과 카페 실습이에요. 파트마다 새 커널에서 위에서부터 차례로 실행해요.",
       "클래스 2 (__str__과 __repr__)")
