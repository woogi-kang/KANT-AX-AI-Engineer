"""Generates every slide of the functions 1 deck (19, def, parameters, return) and slides/deck.json.

Story: keeps writing in basics.ipynb from chapters 12-18. Starts from the café total copied for every customer,
draws a function as a box that takes ingredients and gives a result, then def and calling, parameters and arguments,
return next to print, None, early return and returning two values. Part 5 collects the usual errors, and part 6 turns
code from chapters 15-17 (cart total, stock check, grades, discount) into functions.
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
            cells_ += f'<div style="width:{cw}px;flex:none">' + (tf(v, 20) if v in ("True", "False") else p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{INK};white-space:nowrap", e(v))) + '</div>'
        o.append(f'<div{at} style="position:absolute;left:{left}px;top:{top + 50 + i * (rh + 8)}px;width:{w}px;height:{rh}px;background:{(K3BG if color == K3 else K4BG) if on else CARD};border:2px solid {color if on else LINE};border-radius:14px;padding:0 20px;display:flex;flex-direction:row;align-items:center;gap:12px">{cells_}</div>')
    return o




EB1 = "1. 왜 필요한가"
EB2 = "2. 정의와 호출"
EB3 = "3. 매개변수와 인자"
EB4 = "4. return"
EB5 = "5. 오류와 함정"
EB6 = "6. 실습"
K5, K5BG = RED, "#F8E6E6"
K6, K6BG = PUR, "#ECE7F8"
REAL = " 출력은 실제로 실행한 결과예요."
MENU = 'menu = {"coffee": 4500, "latte": 5000, "cake": 6500}'


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


# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#F2B27A;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
       '<h1 style="font-size:92px;font-weight:900;line-height:1.1;color:#F6F5F1">함수 1<br>정의와 return</h1>',
       '<p style="font-size:40px;line-height:1.4;color:#BFC6D4">자주 쓰는 코드에 이름을 붙이고<br>값을 넣어 결과를 돌려받기</p>']
cov.append(f'<div style="position:absolute;left:940px;top:300px;width:860px;height:480px;background:#252B36;border-radius:24px;padding:44px 48px;display:flex;flex-direction:column;justify-content:center;gap:16px">')
for line, c in [("def calc_total(cart, menu):", "#9DBDEB"), ("    total = 0", "#E6E9EF"), ("    for m in cart:", "#E3B877"), ("        total += menu[m]", "#E6E9EF"), ("    return total", "#F2A0A0"), ("calc_total(cart, menu)", "#8FD8DE")]:
    cov.append(p(f"font-family:{MONO};font-size:34px;font-weight:700;line-height:1.45;color:{c};white-space:pre", e(line)))
cov.append('</div>')
W("cover", cov, "17과 18에서 제어문을 배웠어요. 이번 챕터부터 함수를 다뤄요. 자주 쓰는 코드 묶음에 이름을 붙여 두고, 필요할 때 이름으로 불러 써요. 값을 넣고 결과를 돌려받는 데까지가 이번 챕터예요. 기본값, 지역 변수와 전역 변수는 20에서 이어서 배워요. 17, 18과 같은 카페 예제를 써요.", ("intro", "들어가기"))

ORDER.append("toc")

# ---------- ready ----------
o = [sec("ready")] + head("들어가기", "18에서 이어서 해요", JP)
done = [("hello-uv 노트북, 커널 .venv", "09 · 25–27쪽"), ("변수 이름 규칙", "10"), ("f-string, 리스트, for, 튜플 꺼내 담기", "13"), ("딕셔너리 menu[\"latte\"], None", "15"), ("if, elif, else", "17"), ("range, while, break", "18")]
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
W("ready", o, "09에서 만든 hello-uv 폴더를 VS Code로 열고, 12부터 쓰던 basics.ipynb를 다시 열어요. 10의 변수 이름 규칙은 함수 이름에도 그대로 써요. 13의 f-string과 for, 튜플 꺼내 담기, 15의 딕셔너리와 None, 17의 if, 18의 반복을 함수 안에서 그대로 써요. 슬라이드의 출력은 tools/demo.sh가 hello-uv 커널에서 같은 셀을 실제로 실행한 결과예요. 셀 번호는 파트마다 [1]부터 다시 셌어요.")

# ---------- part 1 ----------
o = [sec("f-why")] + head(EB1, "같은 계산을 손님마다 복사하고 있어요", K1)
WHY = [MENU, 'cart = ["coffee", "cake"]', "total = 0", "for m in cart:", "    total += menu[m]", 'print(f"합계 {total:,}원")', 'cart = ["latte", "latte", "cake"]', "total = 0", "for m in cart:", "    total += menu[m]", 'print(f"합계 {total:,}원")']
o += cell({"id": "c-why", "lines": WHY, "n": 1, "out": ["합계 11,000원", "합계 16,500원"]}, 96, 196, 1010, sel="c-why")
o.append(hl(96, 196, 1010, 2, 4, "mark", 1, "첫 손님"))
o.append(hl(96, 196, 1010, 7, 4, "mark", 2, "똑같은 4줄"))
o.append(note_card(1150, 196, 674, 250, "손님이 올 때마다 4줄 복사", "세 번째 손님이 오면 또 붙여 넣어요. 노트북이 같은 줄로 금방 길어져요.", K1, ' data-build-in="rise order 3"'))
o.append(warn(1150, 476, 674, 300, "고칠 때 한 곳을 빠뜨리면", "할인 규칙이 생기면 복사한 곳을 전부 고쳐야 해요. 한 곳만 빠뜨려도 손님마다 금액이 달라져요.", ' data-build-in="rise order 4"'))
o.append(caption("같은 일을 하는 줄에 이름을 붙이고, 이름으로 불러 쓰는 게 함수예요.", 930))
W("f-why", o, "15의 메뉴 딕셔너리로 장바구니 합계를 구해요. 첫 손님과 둘째 손님의 계산 4줄이 글자 하나까지 똑같아요. 장바구니만 달라요. 손님이 늘면 이 4줄을 계속 복사해야 해요. 더 큰 문제는 고칠 때예요. 할인 규칙이 생기면 복사한 곳을 다 찾아서 고쳐야 하고, 한 곳만 빠뜨려도 손님마다 금액이 달라져요. 이 4줄에 이름을 붙여 두고 이름으로 부르면 고칠 곳이 한 곳이 돼요. 그 이름 붙인 코드 묶음이 함수예요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p1", "왜 필요한가"))

o = [sec("f-big")] + head(EB1, "함수는 재료를 넣으면 결과가 나오는 상자예요", K1)
o.append(p(f"position:absolute;left:96px;top:190px;width:420px;font-size:24px;font-weight:700;color:{GRAY};text-align:right", "재료", ' data-build-in="fade order 1"'))
o.append(p(f"position:absolute;left:616px;top:190px;width:300px;font-size:24px;font-weight:700;color:{GRAY};text-align:center", "함수", ' data-build-in="fade order 1"'))
o.append(p(f"position:absolute;left:1016px;top:190px;width:300px;font-size:24px;font-weight:700;color:{GRAY}", "결과", ' data-build-in="fade order 1"'))
o.append(fn_box(96, 236, '["coffee", "cake"]', "len", "2", K1, K1BG, 1))
o.append(fn_box(96, 360, "[6500, 4500, 5000]", "sorted", "[4500, 5000, 6500]", K2, K2BG, 2))
o.append(fn_box(96, 484, "[4500, 6500]", "sum", "11000", K3, K3BG, 3))
o += cell({"id": "c-big", "lines": ['cart = ["coffee", "cake"]', "print(len(cart))", "print(sorted([6500, 4500, 5000]))", "print(sum([4500, 6500]))"], "n": 2, "out": ["2", "[4500, 5000, 6500]", "11000"]}, 96, 630, 900, attrs=' data-build-in="rise order 4"')
o.append(note_card(1050, 630, 774, 270, "13에서 이미 써 봤어요", "len, sorted, sum은 파이썬에 들어 있는 함수예요. 오늘은 이런 상자를 def로 직접 만들어요.", K1, ' data-build-in="rise order 5"'))
W("f-big", o, "13에서 len, sum, sorted를 함수라고 불렀어요. 함수는 상자처럼 생각하면 쉬워요. 괄호 안에 재료를 넣으면 상자가 일을 하고 결과를 내놓아요. len에 장바구니를 넣으면 2가 나오고, sorted에 가격 리스트를 넣으면 줄 세운 리스트가 나와요. 지금까지는 파이썬이 만들어 둔 상자만 썼어요. 오늘은 앞 장의 합계 계산처럼 우리가 쓰는 줄로 상자를 직접 만들어요." + REAL)

o = [sec("f-min")] + head(EB1, "def로 만들고, 이름()으로 불러요", K1)
o += cell({"id": "c-min", "lines": ["def hello():", '    print("어서 오세요")', "", "hello()", "hello()"], "n": 3, "out": ["어서 오세요", "어서 오세요"]}, 96, 200, 900, sel="c-min")
o.append(hl(96, 200, 900, 0, 2, "mark", 1, "만들기"))
o.append(hl(96, 200, 900, 3, 2, "run", 2, "부르기"))
o.append(callout(1050, 200, 774, 150, "def", "함수를 만들어요. 정의라고 해요.", K1, 1))
o.append(callout(1050, 380, 774, 150, "hello()", "만든 함수를 실행해요. 호출이라고 해요.", GR, 2))
o.append(note_card(96, 600, 1728, 230, "부른 만큼 실행돼요", "hello()를 두 번 불러서 \"어서 오세요\"가 두 번 찍혔어요. 몸통은 한 번만 적었어요.", OR, ' data-build-in="rise order 3"'))
o.append(caption("만드는 걸 정의, 부르는 걸 호출이라고 해요.", 920))
W("f-min", o, "가장 짧은 함수예요. def 다음에 함수 이름 hello와 빈 괄호, 콜론을 적어요. 다음 줄은 4칸 들여써서 함수가 할 일을 적어요. 여기까지가 함수를 만드는 정의예요. 아래 hello()는 만든 함수를 실행하는 호출이에요. 두 번 불러서 어서 오세요가 두 번 찍혔어요. 몸통은 한 번만 적었는데 부른 만큼 실행돼요." + REAL)

# ---------- part 2 ----------
o = [sec("d-shape")] + head(EB2, "def 줄은 다섯 조각으로 읽어요", K2)
o.append(f'<div style="position:absolute;left:96px;top:210px;width:900px;height:250px;background:#252B36;border-radius:22px;padding:34px 40px;display:flex;flex-direction:column;justify-content:center;gap:10px">'
         + p(f"font-family:{MONO};font-size:44px;font-weight:700;line-height:1.45;color:#E6E9EF;white-space:pre", '<span style="color:#9DBDEB">def</span> <span style="color:#E3B877">hello</span><span style="color:#8FD8DE">()</span><span style="color:#F2A0A0">:</span>')
         + p(f"font-family:{MONO};font-size:44px;font-weight:700;line-height:1.45;color:#E6E9EF;white-space:pre", '<span style="background:rgba(184,232,190,0.18);border-radius:6px">    </span>print("어서 오세요")') + '</div>')
parts_ = [("def", "함수를 만든다는 표시예요", BL), ("hello", "함수 이름이에요. 10의 변수 이름 규칙과 같아요", OR), ("()", "재료 칸이에요. 3파트에서 채워요", TEAL), (":", "콜론이에요. if, for 줄 끝과 같아요", RED), ("4칸", "들여쓴 줄이 함수 몸통이에요", GR)]
for i, (k, d, c) in enumerate(parts_):
    o.append(callout(1050, 196 + i * 136, 774, 116, k, d, c, i + 1, 26))
o.append(note_card(96, 500, 900, 340, "이름은 하는 일로 지어요", "hello, calc_total, print_menu처럼 소문자와 밑줄로 적어요. 이름만 봐도 무엇을 하는지 알 수 있게 동사를 넣으면 좋아요.", OR, ' data-build-in="rise order 6"'))
o.append(caption("모양은 if, for와 같아요. 콜론 뒤 4칸 들여쓴 줄이 한 덩어리예요.", 920))
W("d-shape", o, "def 줄을 조각으로 나눠 봐요. def는 함수를 만든다는 표시예요. hello는 함수 이름이에요. 10에서 배운 변수 이름 규칙을 그대로 따라요. 괄호는 재료를 받는 칸인데, 지금은 비어 있어요. 3파트에서 채워요. 줄 끝 콜론과 다음 줄 4칸 들여쓰기는 17의 if, 13의 for와 같아요. 들여쓴 줄이 모두 함수 몸통이에요. 함수 이름은 calc_total처럼 하는 일을 알 수 있게 지으면 나중에 읽기 쉬워요.", ("p2", "정의와 호출"))

o = [sec("d-def")] + head(EB2, "정의만 하면 아무것도 찍히지 않아요", K2)
o += cell({"id": "c-def", "lines": ["def hello():", '    print("어서 오세요")', '    print("주문하시겠어요?")'], "n": 1}, 96, 200, 900, sel="c-def")
o.append(yes_no(780, 340, False, "출력 없음", 1))
o.append(f'<div data-build-in="rise order 2" style="position:absolute;left:1050px;top:200px;width:774px;height:300px;background:{CARD};border:3px dashed {K2};border-radius:22px;padding:24px 30px;display:flex;flex-direction:column;gap:14px">'
         + '<div style="display:flex;flex-direction:row;align-items:center;gap:16px">' + chip("hello", K2, K2BG, 30) + p(f"font-size:24px;font-weight:700;color:{SUB}", "이 이름에 몸통을 기억해 둬요") + '</div>'
         + p(f"font-family:{MONO};font-size:26px;line-height:1.5;color:{INK};white-space:pre;background:#FAF8F3;border-radius:12px;padding:12px 20px", e('print("어서 오세요")') + "<br>" + e('print("주문하시겠어요?")')) + '</div>')
o += cell({"id": "c-call", "lines": ["hello()"], "n": 2, "out": ["어서 오세요", "주문하시겠어요?"]}, 96, 420, 900, attrs=' data-build-in="rise order 3"')
o.append(note_card(1050, 540, 774, 300, "레시피 카드와 같아요", "def는 카드에 만드는 법을 적어 두기만 해요. 음료는 주문이 들어올 때, 곧 hello()를 부를 때 만들어요.", OR, ' data-build-in="rise order 4"'))
o.append(caption("def는 기억해 두기만 하고, 실행은 이름()을 부를 때 해요.", 920))
W("d-def", o, "def 셀만 실행하면 아무것도 찍히지 않아요. 파이썬은 hello라는 이름에 몸통 두 줄을 기억해 두기만 해요. 레시피 카드에 만드는 법을 적어 둔 것과 같아요. 다음 셀에서 hello()를 부르면 그제야 기억한 몸통을 실행해서 두 줄이 찍혀요. 노트북에서는 def 셀을 한 번 실행해 두면 아래 셀 어디서든 부를 수 있어요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL)

o = [sec("d-flow")] + head(EB2, "부르면 몸통으로 갔다가 제자리로 돌아와요", K2)
o += cell({"id": "c-flow", "lines": ['print("가게 문 열어요")', "hello()", 'print("다음 손님")', "hello()"], "n": 3, "out": ["가게 문 열어요", "어서 오세요", "주문하시겠어요?", "다음 손님", "어서 오세요", "주문하시겠어요?"]}, 96, 200, 800, sel="c-flow")
o += steps([("1", 'print("가게 문 열어요")', "셀 1줄"), ("2", "hello()", "몸통으로 가요"), ("3", '  print("어서 오세요")', "몸통 1줄"), ("4", '  print("주문하시겠어요?")', "몸통 2줄, 돌아와요"),
            ("5", 'print("다음 손님")', "셀 3줄"), ("6", "hello()", "다시 몸통으로"), ("7", '  print(...) 두 줄', "몸통 실행 후 끝")], 950, 196, 874, 1, K2, 84, (50, 470))
o.append(caption("함수를 부를 때마다 몸통을 처음부터 끝까지 실행하고 돌아와요.", 920))
W("d-flow", o, "앞 셀에서 hello를 정의해 뒀어요. 이번 셀은 위에서 아래로 실행돼요. 첫 줄을 찍고, hello()를 만나면 몸통으로 가서 두 줄을 실행해요. 몸통이 끝나면 hello()를 부른 자리로 돌아와 다음 줄인 다음 손님을 찍어요. 다시 hello()를 만나서 몸통을 한 번 더 실행해요. 출력 여섯 줄이 오른쪽 순서 그대로예요." + REAL)

# ---------- part 3 ----------
o = [sec("a-one")] + head(EB3, "괄호 안에 재료 칸을 만들어요", K3)
o += cell({"id": "c-a1", "lines": ["def greet(name):", '    print(f"{name}님, 어서 오세요")', "", 'greet("kim")', 'greet("lee")'], "n": 1, "out": ["kim님, 어서 오세요", "lee님, 어서 오세요"]}, 96, 200, 900, sel="c-a1")
o.append(hl(96, 200, 900, 3, 1, "run", 1, "kim"))
o.append(f'<div data-build-in="rise order 1" style="position:absolute;left:1050px;top:210px;width:774px;height:120px;display:flex;flex-direction:row;align-items:center;gap:22px">' + chip('greet("kim")', GRAY, "#F1F0EC", 30) + arrow(70, K3) + '</div>')
o.append(var_box("v-name1", "name", '"kim"', 1404, 200, K3, 420, ' data-build-in="rise order 1"'))
o.append(f'<div data-build-in="rise order 2" style="position:absolute;left:1050px;top:470px;width:774px;height:120px;display:flex;flex-direction:row;align-items:center;gap:22px">' + chip('greet("lee")', GRAY, "#F1F0EC", 30) + arrow(70, K3) + '</div>')
o.append(var_box("v-name2", "name", '"lee"', 1404, 460, K3, 420, ' data-build-in="rise order 2"'))
o.append(callout(96, 560, 900, 130, "name", "매개변수. def 괄호 안에 적은 칸 이름이에요", K3, 3, 26))
o.append(callout(96, 720, 900, 130, '"kim"', "인자. 부를 때 괄호에 넣는 값이에요", OR, 4, 26))
o.append(caption("부를 때 넣은 값이 매개변수 칸에 담겨서 몸통에서 쓰여요.", 920))
W("a-one", o, "괄호 안에 name을 적으면 재료를 받는 칸이 생겨요. 이 칸을 매개변수라고 해요. greet(\"kim\")처럼 부를 때 넣는 값은 인자라고 해요. 부르면 \"kim\"이 name 칸에 담기고, 몸통의 f-string이 name 자리에 kim을 넣어 찍어요. 다음에 greet(\"lee\")로 부르면 name에 lee가 담겨요. 함수는 하나인데 넣는 값에 따라 결과가 달라져요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p3", "매개변수와 인자"))

o = [sec("a-two")] + head(EB3, "재료 칸은 쉼표로 여러 개 만들어요", K3)
o += cell({"id": "c-a2", "lines": ["def order(menu_name, qty):", '    print(f"{menu_name} {qty}잔 주문 받았어요")', "", 'order("latte", 2)', 'order("coffee", 1)'], "n": 2, "out": ["latte 2잔 주문 받았어요", "coffee 1잔 주문 받았어요"]}, 96, 200, 1000, sel="c-a2")
o.append(f'<div data-build-in="rise order 1" style="position:absolute;left:96px;top:560px;width:1000px;height:90px;display:flex;flex-direction:row;align-items:center;gap:0">'
         + p(f"font-family:{MONO};font-size:40px;font-weight:700;color:{INK};white-space:pre", 'order(<span style="color:' + OR + '">"latte"</span>, <span style="color:' + BL + '">2</span>)') + '</div>')
o.append(var_box("v-mn", "menu_name", '"latte"', 96, 670, OR, 460, ' data-build-in="rise order 2"'))
o.append(var_box("v-qty", "qty", "2", 600, 670, BL, 300, ' data-build-in="rise order 2"'))
o.append(note_card(1150, 200, 674, 300, "첫째는 첫째 칸, 둘째는 둘째 칸", "\"latte\"는 menu_name에, 2는 qty에 들어가요. 적은 순서대로 짝을 지어요.", K3, ' data-build-in="rise order 3"'))
o.append(note_card(1150, 530, 674, 370, "왜 menu가 아니라 menu_name인가요", "15의 menu 딕셔너리와 헷갈리지 않게 이름을 다르게 지었어요. 매개변수 이름도 하는 일이 보이게 지어요.", OR, ' data-build-in="rise order 4"'))
W("a-two", o, "재료가 두 개 필요하면 괄호 안에 쉼표로 칸을 두 개 만들어요. order는 메뉴 이름과 잔 수를 받아요. order(\"latte\", 2)로 부르면 첫째 인자 \"latte\"가 첫째 칸 menu_name에, 둘째 인자 2가 둘째 칸 qty에 담겨요. 매개변수 이름을 menu가 아니라 menu_name으로 지은 건 15의 menu 딕셔너리와 헷갈리지 않게 하려는 거예요." + REAL)

o = [sec("a-order")] + head(EB3, "인자는 적은 순서대로 칸에 들어가요", K3)
o += cell({"id": "c-a3", "lines": ['order(2, "latte")'], "n": 3, "out": ["2 latte잔 주문 받았어요"]}, 96, 200, 900, sel="c-a3")
o.append(f'<div data-build-in="rise order 1" style="position:absolute;left:96px;top:380px;width:900px;height:90px;display:flex;flex-direction:row;align-items:center">'
         + p(f"font-family:{MONO};font-size:40px;font-weight:700;color:{INK};white-space:pre", 'order(<span style="color:' + BL + '">2</span>, <span style="color:' + OR + '">"latte"</span>)') + '</div>')
o.append(var_box("v-mn2", "menu_name", "2", 96, 490, OR, 460, ' data-build-in="rise order 2"'))
o.append(var_box("v-qty2", "qty", '"latte"', 600, 490, BL, 380, ' data-build-in="rise order 2"'))
o.append(warn(1050, 200, 774, 320, "오류 없이 이상하게 찍혀요", "파이썬은 값의 뜻을 몰라요. 첫째 값을 첫째 칸에 넣을 뿐이에요. 2가 메뉴 이름이 됐어요.", ' data-build-in="rise order 3"'))
o.append(note_card(1050, 550, 774, 300, "def 줄을 보고 순서를 맞춰요", "order(menu_name, qty)이니 메뉴, 잔 수 순서로 넣어요. 20에서 칸 이름을 적어 넣는 키워드 인자를 배워요.", GR, ' data-build-in="rise order 4"'))
o.append(caption("칸 순서를 바꿔 넣으면 값도 바뀌어 들어가요.", 920))
W("a-order", o, "같은 order에 순서를 바꿔 2, \"latte\"로 넣었어요. 파이썬은 값의 뜻을 따지지 않고 첫째 값을 첫째 칸에 넣어요. 그래서 menu_name이 2, qty가 latte가 되어 2 latte잔이라고 찍혀요. 오류가 나지 않아서 더 알아채기 어려워요. 부를 때는 def 줄을 보고 칸 순서대로 넣어요. 칸 이름을 직접 적어서 순서를 신경 쓰지 않는 방법은 20에서 배워요." + REAL)

# ---------- part 4 ----------
o = [sec("r-ret")] + head(EB4, "return은 결과를 부른 자리로 돌려줘요", K4)
o += cell({"id": "c-r1", "lines": ["def price_of(qty):", "    return 4500 * qty", "", "x = price_of(2)", "print(x)", "print(price_of(3) + 1000)"], "n": 1, "out": ["9000", "14500"]}, 96, 200, 900, sel="c-r1")
o.append(hl(96, 200, 900, 1, 1, "mark", 1, "돌려줄 값"))
rows_ = [("x = price_of(2)", "x = 9000", 2), ("price_of(3) + 1000", "13500 + 1000", 3), ("13500 + 1000", "14500", 4)]
for i, (a_, b_, od) in enumerate(rows_):
    o.append(f'<div data-build-in="rise order {od}" style="position:absolute;left:1050px;top:{200 + i * 130}px;width:774px;height:110px;background:{CARD};border:2px solid {LINE};border-radius:16px;padding:0 24px;display:flex;flex-direction:row;align-items:center;gap:20px">'
             + mono(a_, 26, INK, "#F1F0EC") + arrow(50, K4) + mono(b_, 26, K4, K4BG) + '</div>')
o.append(note_card(96, 600, 900, 260, "부른 자리가 값으로 바뀌어요", "price_of(2)를 9000으로 바꿔 읽으면 돼요. 변수에 담을 수도 있고, 바로 더하기에 쓸 수도 있어요.", K4, ' data-build-in="rise order 5"'))
o.append(note_card(1050, 600, 774, 260, "return 뒤에 돌려줄 값을 적어요", "return 4500 * qty는 계산한 값을 들고 함수를 나가요. len, sum도 이렇게 값을 돌려줘요.", None, ' data-build-in="rise order 6"'))
o.append(caption("return 뒤의 값이 함수를 부른 자리에 들어가요.", 920))
W("r-ret", o, "지금까지 만든 함수는 print로 찍기만 했어요. 결과를 받아서 다시 쓰려면 return을 써요. price_of는 잔 수를 받아 4500을 곱한 값을 돌려줘요. x = price_of(2)는 함수를 부른 자리가 9000으로 바뀌어서 x = 9000이 돼요. price_of(3) + 1000도 13500 + 1000으로 바뀐 뒤 14500이 돼요. 13의 len과 sum이 값을 돌려준 것과 같은 방식이에요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p4", "return"))

o = [sec("r-vs")] + head(EB4, "print는 화면에 찍기만, return은 값을 돌려줘요", K4)
o.append(label("print로 찍는 함수", 96, 196, OR, ' data-build-in="fade order 1"', 840, 28))
o += cell({"id": "c-r2", "lines": ["def show(qty):", "    print(4500 * qty)", "", "a = show(2)", 'print("a:", a)'], "n": 2, "out": ["9000", "a: None"]}, 96, 246, 840, attrs=' data-build-in="rise order 1"')
o.append(label("return으로 돌려주는 함수", 984, 196, K4, ' data-build-in="fade order 2"', 840, 28))
o += cell({"id": "c-r3", "lines": ["def calc(qty):", "    return 4500 * qty", "", "b = calc(2)", 'print("b:", b)', "print(b + 1000)"], "n": 3, "out": ["b: 9000", "10000"]}, 984, 246, 840, attrs=' data-build-in="rise order 2"')
o.append(note_card(96, 650, 840, 230, "a에 남은 건 None", "9000은 화면에 찍혔을 뿐이에요. 함수가 돌려준 값이 없어서 a에는 None만 남았어요.", OR, ' data-build-in="rise order 3"'))
o.append(note_card(984, 650, 840, 230, "b에 9000이 담겼어요", "돌려받은 값이라 b + 1000처럼 다음 계산에 쓸 수 있어요.", K4, ' data-build-in="rise order 4"'))
o.append(caption("사람이 볼 값은 print, 다음 계산에 쓸 값은 return이에요.", 930))
W("r-vs", o, "가장 많이 헷갈리는 부분이에요. 왼쪽 show는 계산한 값을 print로 찍기만 해요. 화면에 9000이 보이지만 함수가 돌려준 값은 없어서 a에는 None이 담겨요. 오른쪽 calc는 return으로 값을 돌려줘요. 화면에는 아무것도 안 찍히지만 b에 9000이 담겨서 1000을 더할 수 있어요. 화면에 보이는 것과 변수에 담기는 것은 달라요. 결과를 다른 계산에 쓰려면 return을 써요." + REAL)

o = [sec("r-none")] + head(EB4, "return이 없으면 None을 돌려줘요", K4)
o += cell({"id": "c-r4", "lines": ['result = print("안녕")', "print(result)", "print(type(result))"], "n": 4, "out": ["안녕", "None", "<class 'NoneType'>"]}, 96, 200, 900, sel="c-r4")
o.append(note_card(96, 500, 900, 340, "print도 return이 없는 함수예요", "print는 화면에 찍는 일만 하고 돌려주는 값이 없어요. 그래서 result에 None이 담겼어요. 앞 장의 show도 같아요.", K4, ' data-build-in="rise order 1"'))
o.append(f'<div data-build-in="rise order 2" style="position:absolute;left:1050px;top:200px;width:774px;height:300px;background:{CARD};border:2px solid {LINE};border-top:10px solid {GRAY};border-radius:20px;padding:26px 32px;display:flex;flex-direction:column;gap:18px">'
         + p(f"font-size:28px;font-weight:700;color:{INK}", "None은 \"값이 없음\"이에요")
         + mono("None", 40, GRAY, "#F1F0EC", "align-self:flex-start")
         + p(f"font-size:24px;line-height:1.5;color:{INK}", "15에서 get이 없는 키를 만났을 때 돌려준 값과 같아요.") + '</div>')
o.append(note_card(1050, 530, 774, 310, "값이 필요하면 return을 적어요", "몸통 끝까지 return이 없으면 파이썬이 None을 대신 돌려줘요.", GR, ' data-build-in="rise order 3"'))
o.append(caption("돌려받은 값이 None이면 함수에 return이 있는지 먼저 봐요.", 920))
W("r-none", o, "print도 함수라서 결과를 변수에 담아 볼 수 있어요. 안녕은 화면에 찍히고, result에는 None이 담겨요. type으로 보면 NoneType이에요. print는 찍는 일만 하고 돌려주는 값이 없어서예요. 15에서 get이 없는 키를 만났을 때 돌려준 그 None이에요. 우리가 만든 함수도 몸통 끝까지 return을 만나지 않으면 파이썬이 None을 돌려줘요." + REAL)

o = [sec("r-stop")] + head(EB4, "return을 만나면 함수가 바로 끝나요", K4)
CHK = ["def check(stock):", "    if stock == 0:", '        return "품절"', '    return "주문 가능"', "", "print(check(0))", "print(check(3))"]
o += cell({"id": "c-r5", "lines": CHK, "n": 5, "out": ["품절", "주문 가능"]}, 96, 200, 900, sel="c-r5")
o.append(hl(96, 200, 900, 2, 1, "run", 1, "check(0) 여기서 끝"))
o.append(hl(96, 200, 900, 3, 1, "skip", 1, "check(0)은 안 감"))
o += table(1050, 200, 774, [("부르기", 180), ("stock == 0", 170), ("만난 return", 280)],
           [("check(0)", "True", 'return "품절"'), ("check(3)", "False", 'return "주문 가능"')], 2, K4, 80)
o.append(note_card(1050, 440, 774, 400, "else를 안 써도 돼요", "stock이 0이면 위의 return에서 이미 함수를 나가요. 아래 줄까지 왔다면 0이 아니라는 뜻이에요. 17의 if, else로 써도 결과는 같아요.", K4, ' data-build-in="rise order 4"'))
o.append(caption("return은 값을 돌려주면서 함수를 끝내요. 아래 줄은 실행하지 않아요.", 920))
W("r-stop", o, "return은 값을 돌려주는 동시에 함수를 끝내요. 18에서 break가 반복을 끝낸 것처럼요. check(0)은 if가 True라서 return \"품절\"을 만나고 바로 나가요. 그 아래 return \"주문 가능\"까지 가지 않아요. check(3)은 if가 False라서 아래로 내려가 주문 가능을 돌려줘요. 그래서 else를 쓰지 않아도 돼요. 17처럼 if, else로 나눠 써도 결과는 같아요." + REAL)

o = [sec("r-multi")] + head(EB4, "쉼표로 값 여러 개를 한 번에 돌려줘요", K4)
o += cell({"id": "c-r6", "lines": ["def summary(prices):", "    return sum(prices), len(prices)", "", "print(summary([4500, 5000, 6500]))", "total, n = summary([4500, 5000, 6500])", "print(total, n)"], "n": 6, "out": ["(16000, 3)", "16000 3"]}, 96, 200, 1000, sel="c-r6")
o.append(f'<div data-build-in="rise order 1" style="position:absolute;left:1150px;top:200px;width:674px;height:260px;background:{CARD};border:2px solid {LINE};border-top:10px solid {K4};border-radius:20px;padding:24px 30px;display:flex;flex-direction:column;gap:16px">'
         + p(f"font-size:26px;font-weight:700;color:{INK}", "튜플 하나로 돌아와요") + mono("(16000, 3)", 36, K4, K4BG, "align-self:flex-start")
         + p(f"font-size:22px;color:{SUB}", "13에서 배운 괄호 묶음, 튜플이에요") + '</div>')
o.append(f'<div data-build-in="rise order 2" style="position:absolute;left:1150px;top:490px;width:674px;height:200px;display:flex;flex-direction:row;gap:24px">'
         + '<div style="flex:1;position:relative">' + var_box("v-t", "total", "16000", 0, 0, K4, 320).replace("height:230px", "height:200px") + '</div>'
         + '<div style="flex:1;position:relative">' + var_box("v-n", "n", "3", 0, 0, BL, 320).replace("height:230px", "height:200px") + '</div></div>')
o.append(note_card(96, 600, 1000, 260, "받는 쪽은 13의 꺼내 담기", "a, b, c = 튜플처럼 total, n = summary(...)로 두 변수에 나눠 담아요. 왼쪽 개수와 돌려준 값 개수가 같아야 해요.", None, ' data-build-in="rise order 3"'))
o.append(caption("return a, b는 튜플로 돌려주고, x, y = 함수()로 나눠 받아요.", 920))
W("r-multi", o, "합계와 개수를 같이 알고 싶을 때는 return 뒤에 쉼표로 값을 이어 적어요. 그대로 찍으면 괄호로 묶인 (16000, 3)이 나와요. 13에서 배운 튜플이에요. 받을 때는 13의 꺼내 담기처럼 total, n = summary(...)로 적으면 두 변수에 하나씩 담겨요. 이 장은 가볍게 보고 넘어가도 돼요." + REAL)

# ---------- part 5 ----------
o = [sec("t-paren")] + head(EB5, "괄호를 빼면 실행하지 않고 함수 자체가 나와요", K5)
o += cell({"id": "c-t1", "lines": ["def hello():", '    print("어서 오세요")', "", "hello"], "n": 1, "out": ["<function __main__.hello()>"]}, 96, 200, 900, sel="c-t1")
o += cell({"id": "c-t2", "lines": ["print(hello)"], "n": 2, "out": ["<function hello at 0x7efc68143530>"]}, 96, 470, 900, attrs=' data-build-in="rise order 1"')
o.append(note_card(1050, 200, 774, 290, "어서 오세요가 안 찍혀요", "hello만 적으면 \"hello라는 함수가 있어요\"라고 보여 줄 뿐이에요. 실행하려면 괄호를 붙여요.", K5, ' data-build-in="rise order 2"'))
o.append(note_card(1050, 520, 774, 320, "0x로 시작하는 숫자는 달라요", "함수가 저장된 메모리 위치예요. 실행할 때마다 바뀌어서 화면이 슬라이드와 달라도 괜찮아요.", GRAY, ' data-build-in="rise order 3"'))
o.append(f'<div data-build-in="rise order 4" style="position:absolute;left:96px;top:660px;width:900px;height:180px;display:flex;flex-direction:row;align-items:center;gap:24px">'
         + mono("hello", 34, RED, "#F8E6E6") + arrow(60, GR) + mono("hello()", 34, GR, "#E6F4EC") + '</div>')
o.append(caption("부를 때는 재료가 없어도 괄호 ()를 꼭 붙여요.", 920))
W("t-paren", o, "괄호를 빼고 hello만 적으면 함수를 실행하지 않아요. 셀 마지막 줄에 적으면 노트북이 함수 자체를 보여 주고, print(hello)로 찍으면 function hello at 뒤에 숫자가 나와요. 그 숫자는 함수가 저장된 메모리 위치라서 실행할 때마다 달라져요. 수강생 화면과 슬라이드 숫자가 달라도 괜찮아요. 함수를 실행하려면 재료가 없어도 괄호를 붙여요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p5", "오류와 함정"))

o = [sec("t-args")] + head(EB5, "칸 수와 인자 수가 다르면 TypeError가 나요", K5)
o += cell({"id": "c-t3", "lines": ["def order(menu_name, qty):", '    print(f"{menu_name} {qty}잔 주문 받았어요")', "", 'order("latte")'], "n": 3, "out": ["TypeError: order() missing 1 required positional argument: 'qty'"], "err": True}, 96, 200, 1728, sel="c-t3")
o += cell({"id": "c-t4", "lines": ['order("latte", 2, "L")'], "n": 4, "out": ["TypeError: order() takes 2 positional arguments but 3 were given"], "err": True}, 96, 450, 1728, attrs=' data-build-in="rise order 1"')
o.append(note_card(96, 620, 846, 260, "missing 1 ... 'qty'", "칸 qty가 비었어요. 인자를 하나 덜 넣었어요.", K5, ' data-build-in="rise order 2"'))
o.append(note_card(978, 620, 846, 260, "takes 2 ... but 3 were given", "칸은 2개인데 인자를 3개 넣었어요.", K5, ' data-build-in="rise order 3"'))
o.append(caption("def 줄의 칸 수만큼 인자를 넣어요.", 930))
W("t-args", o, "칸이 두 개인 order에 인자를 하나만 넣으면 TypeError가 나요. 마지막 줄의 missing 1 required positional argument: 'qty'는 qty 칸에 들어갈 값이 없다는 뜻이에요. 반대로 세 개를 넣으면 takes 2 positional arguments but 3 were given이 나요. 칸은 2개인데 3개를 받았다는 뜻이에요. 오류가 나면 def 줄을 보고 칸 수를 세어 봐요. Traceback 위쪽 줄은 빼고 마지막 줄만 옮겼어요." + REAL)

o = [sec("t-dead")] + head(EB5, "return 아래에 적은 줄은 실행되지 않아요", K5)
DEAD = ["def calc(qty):", "    total = 4500 * qty", "    return total", '    print("계산 끝")', "", "print(calc(2))"]
o += cell({"id": "c-t5", "lines": DEAD, "n": 5, "out": ["9000"]}, 96, 200, 900, sel="c-t5")
o.append(hl(96, 200, 900, 2, 1, "run", 1, "여기서 나감"))
o.append(hl(96, 200, 900, 3, 1, "skip", 1, "안 찍힘"))
o.append(note_card(1050, 200, 774, 300, "계산 끝이 안 보여요", "return에서 함수를 나갔기 때문이에요. 오류도 나지 않아서 빠진 줄을 알아채기 어려워요.", K5, ' data-build-in="rise order 2"'))
o.append(side(1050, 530, 774, 330, "이렇게 고쳐요", ["def calc(qty):", "    total = 4500 * qty", '    print("계산 끝")', "    return total"], [], GR, "#E6F4EC", ' data-build-in="rise order 3"', 24, "print를 return 위로"))
o.append(caption("함수에서 할 일을 다 적고 return은 마지막에 둬요.", 920))
W("t-dead", o, "return 아래에 print를 적었어요. 실행하면 9000만 나오고 계산 끝은 찍히지 않아요. return을 만나서 함수를 이미 나갔기 때문이에요. 오류가 나지 않아서 빠진 줄을 알아채기 어려워요. 함수 안에서 할 일을 다 적은 뒤 return을 마지막에 둬요. 앞 장처럼 if 안의 return은 괜찮아요. 그 return을 만났을 때만 나가요." + REAL)

o = [sec("t-none")] + head(EB5, "찍기만 하는 함수로 계산하면 TypeError가 나요", K5)
o += cell({"id": "c-t6", "lines": ["def show(qty):", "    print(4500 * qty)", "", "show(2) + 1000"], "n": 6, "out": ["9000", "", "TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'"], "err": True}, 96, 200, 1728, sel="c-t6")
o.append(f'<div data-build-in="rise order 1" style="position:absolute;left:96px;top:520px;width:1728px;height:110px;display:flex;flex-direction:row;align-items:center;gap:22px">'
         + mono("show(2) + 1000", 32, INK, "#F1F0EC") + arrow(60, RED) + mono("None + 1000", 32, RED, "#F8E6E6") + p(f"font-size:26px;font-weight:700;color:{RED}", "None에는 더할 수 없어요") + '</div>')
o.append(note_card(96, 660, 846, 230, "9000은 찍혔는데", "화면에 찍힌 것일 뿐 돌려준 값은 None이에요. print와 return을 비교한 장의 a와 같아요.", K5, ' data-build-in="rise order 2"'))
o.append(side(978, 660, 846, 230, "이렇게 고쳐요", ["def show(qty):", "    return 4500 * qty"], [], GR, "#E6F4EC", ' data-build-in="rise order 3"', 24, "print 대신 return"))
o.append(caption("NoneType이 보이면 return이 빠진 함수를 찾아요.", 930))
W("t-none", o, "show(2)는 9000을 찍지만 돌려주는 값은 None이에요. 그래서 show(2) + 1000은 None + 1000이 되고, None과 정수는 더할 수 없다는 TypeError가 나요. 오류 메시지에 NoneType이 보이면 return이 빠진 함수가 있는지 찾아요. 계산에 쓸 값은 print 대신 return으로 돌려줘요." + REAL)

o = [sec("t-name")] + head(EB5, "정의보다 먼저 부르면 NameError가 나요", K5)
o += cell({"id": "c-t7", "lines": ["welcome()", "", "def welcome():", '    print("어서 오세요")'], "n": 1, "out": ["NameError: name 'welcome' is not defined"], "err": True}, 96, 200, 1000, sel="c-t7")
o.append(hl(96, 200, 1000, 0, 1, "err", 1, "아직 모르는 이름"))
o += cell({"id": "c-t8", "lines": ["welcome()"], "n": 2, "out": ["NameError: name 'welcome' is not defined"], "err": True}, 96, 480, 1000, attrs=' data-build-in="rise order 2"')
o.append(note_card(1150, 200, 674, 330, "위에서부터 실행해요", "첫 줄에서 welcome을 찾았는데 아직 def를 만나지 않았어요. 오류가 나서 아래 def도 실행되지 않았어요.", K5, ' data-build-in="rise order 1"'))
o.append(note_card(1150, 560, 674, 300, "다시 불러도 같아요", "def가 한 번도 실행되지 않았으니까요. def 셀을 먼저 실행하고, 부르는 셀을 아래에 둬요.", GR, ' data-build-in="rise order 3"'))
o.append(note_card(96, 650, 1000, 210, "노트북에서 더 조심해요", "def 셀을 지운 뒤에도 커널은 함수를 기억해요. Restart 뒤 위에서부터 실행하면 그제야 오류가 드러나요.", OR, ' data-build-in="rise order 4"'))
W("t-name", o, "파이썬은 위에서부터 한 줄씩 실행해요. 첫 줄에서 welcome을 찾았는데 아직 def를 만나지 않아서 그런 이름이 없다는 NameError가 나요. 오류에서 셀이 멈춰서 아래 def도 실행되지 않았어요. 그래서 다음 셀에서 다시 불러도 같은 오류가 나요. def 셀을 먼저 실행하고 부르는 셀을 아래에 둬요. 노트북에서는 def 셀을 지워도 커널이 함수를 기억하고 있어서 괜찮아 보이다가, 10에서 배운 Restart 뒤에 위에서부터 실행하면 오류가 드러나요. 이 두 셀은 따로 띄운 새 커널에서 실행했어요." + REAL)

# ---------- part 6 ----------
o = [sec("x-total")] + head(EB6, "장바구니 총액을 함수로 만들어요", K6)
TOT = [MENU, "", "def calc_total(cart, menu):", "    total = 0", "    for m in cart:", "        total += menu[m]", "    return total", "", 'cart1 = ["coffee", "cake"]', 'cart2 = ["latte", "latte", "cake"]', 'print(f"합계 {calc_total(cart1, menu):,}원")', 'print(f"합계 {calc_total(cart2, menu):,}원")']
o += cell({"id": "c-x1", "lines": TOT, "n": 1, "out": ["합계 11,000원", "합계 16,500원"]}, 96, 186, 1240, sel="c-x1")
o.append(hl(96, 186, 1240, 3, 3, "mark", 1, "1파트의 4줄"))
o.append(hl(96, 186, 1240, 10, 2, "run", 2, "손님마다 한 줄"))
o.append(note_card(1380, 196, 444, 330, "복사가 사라졌어요", "1파트에서 손님마다 복사한 줄이 함수 안 한 곳에만 있어요.", K6, ' data-build-in="rise order 3"'))
o.append(note_card(1380, 556, 444, 300, "고칠 곳도 한 곳", "할인이 생기면 calc_total만 고치면 돼요.", GR, ' data-build-in="rise order 4"'))
o.append(caption("반복해서 쓰는 계산은 함수로 묶고, return으로 결과를 돌려받아요.", 930))
W("x-total", o, "1파트에서 손님마다 복사했던 합계 계산을 함수로 바꿨어요. calc_total은 장바구니와 메뉴판을 받아서 합계를 돌려줘요. 함수 안의 4줄은 1파트와 같고, 마지막에 return total을 붙였어요. 부를 때는 f-string 안에서 바로 불러서 13의 천 단위 콤마로 찍었어요. 손님이 늘어도 한 줄씩만 더하면 되고, 할인이 생기면 calc_total만 고치면 돼요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p6", "실습"))

o = [sec("x-soldout")] + head(EB6, "주문할 수 있는지 True, False로 돌려줘요", K6)
CAN = ["def can_order(stock, name):", "    if stock[name] > 0:", "        return True", "    return False", "", 'stock = {"coffee": 3, "latte": 0, "cake": 2}', 'for o in ["coffee", "latte", "cake"]:', "    if can_order(stock, o):", '        print(o, "주문 받았어요")', "    else:", '        print(o, "품절이에요")']
o += cell({"id": "c-x2", "lines": CAN, "n": 2, "out": ["coffee 주문 받았어요", "latte 품절이에요", "cake 주문 받았어요"]}, 96, 196, 1100, sel="c-x2")
o.append(hl(96, 196, 1100, 7, 1, "mark", 1, "if 뒤에 바로"))
o += table(1240, 196, 584, [("o", 110), ("stock[o]", 130), ("돌려준 값", 160)], [("coffee", "3", "True"), ("latte", "0", "False"), ("cake", "2", "True")], 2, K4, 70, hi=(1,))
o.append(note_card(1240, 500, 584, 380, "이름이 질문이 돼요", "if can_order(stock, o):는 \"주문할 수 있나요?\"로 읽혀요. 조건이 길어져도 함수 안에만 적으면 돼요.", K6, ' data-build-in="rise order 5"'))
o.append(caption("True, False를 돌려주는 함수는 if 뒤에 바로 써요.", 930))
W("x-soldout", o, "15의 재고 딕셔너리로 주문할 수 있는지 묻는 함수를 만들었어요. 재고가 0보다 크면 True를 돌려주고 끝내요. 아니면 아래 return False까지 가요. 반복에서는 if can_order(stock, o):처럼 if 뒤에 함수를 바로 써요. 돌려준 True나 False가 if 조건이 돼요. 함수 이름 덕분에 이 줄이 주문할 수 있나요라는 질문처럼 읽혀요." + REAL)

o = [sec("x-grade")] + head(EB6, "17의 등급 계산을 함수로 바꿔요", K6)
GRD = ["def grade(score):", "    if score >= 90:", '        return "A"', "    elif score >= 80:", '        return "B"', "    elif score >= 70:", '        return "C"', '    return "F"', "", 'scores = [["kim", 92], ["lee", 78], ["park", 85], ["choi", 59]]', "for name, score in scores:", '    print(f"{name:<5}{score:>3}  {grade(score)}")']
o += cell({"id": "c-x3", "lines": GRD, "n": 3, "out": ["kim   92  A", "lee   78  C", "park  85  B", "choi  59  F"]}, 96, 186, 1200, sel="c-x3")
o.append(hl(96, 186, 1200, 1, 7, "mark", 1, "등급만 정해요"))
o.append(side(1340, 186, 484, 400, "17에서는", ["if score >= 90:", '    grade = "A"', "elif score >= 80:", '    grade = "B"', "...", "print(... grade)"], [], GRAY, "#F1F0EC", ' data-build-in="rise order 2"', 22, "반복 안에"))
o.append(note_card(1340, 616, 484, 290, "반복이 짧아졌어요", "for 안에는 찍는 줄 하나만 남았어요.", K6, ' data-build-in="rise order 3"'))
W("x-grade", o, "17에서 성적표를 찍을 때 for 안에 if, elif를 길게 적고 grade 변수에 등급을 담았어요. 이번에는 등급을 정하는 부분만 grade 함수로 뺐어요. 조건마다 바로 return해서 grade 변수가 필요 없어요. for 안에는 찍는 줄 하나만 남아서 무엇을 하는지 한눈에 보여요. 점수 기준이 바뀌면 grade 함수만 고쳐요." + REAL)

o = [sec("x-pay")] + head(EB6, "함수 안에서 다른 함수를 불러요", K6)
PAY = ["def discount_rate(total):", "    if total >= 20000:", "        return 10", "    elif total >= 10000:", "        return 5", "    return 0", "", "def pay(total):", "    rate = discount_rate(total)", "    sale = total * rate // 100", "    return total - sale", "", "print(pay(8000))", "print(pay(15500))", "print(pay(22000))"]
o += cell({"id": "c-x4", "lines": PAY, "n": 4, "out": ["8000", "14725", "19800"]}, 96, 180, 1000, sel="c-x4")
o.append(hl(96, 180, 1000, 8, 1, "mark", 1, "다른 함수 부르기"))
o += table(1140, 180, 684, [("total", 120), ("rate", 90), ("sale", 110), ("pay", 140)], [("8000", "0", "0", "8000"), ("15500", "5", "775", "14725"), ("22000", "10", "2200", "19800")], 2, K4, 70)
o.append(note_card(1140, 470, 684, 400, "17의 할인 규칙이에요", "할인율 정하기와 결제 금액 계산을 두 함수로 나눴어요. 할인 기준이 바뀌면 discount_rate만 고쳐요.", K6, ' data-build-in="rise order 5"'))
W("x-pay", o, "17에서 합계에 따라 할인율을 정했던 규칙을 함수 두 개로 나눴어요. discount_rate는 합계를 받아 할인율을 돌려줘요. pay는 그 함수를 불러서 할인율을 받고, 할인 금액을 뺀 결제 금액을 돌려줘요. 함수 안에서 다른 함수를 부를 수 있어요. 오른쪽 표처럼 15500원은 5% 할인으로 775원이 빠져 14725원이에요. 작은 함수로 나누면 하나씩 고치고 확인하기 쉬워요." + REAL)

# ---------- wrap up ----------
o = [sec("trouble")] + head("정리", "막히면 오류의 마지막 줄을 봐요", RED)
tr = [("<function hello at 0x...>가 나와요", "괄호를 빼서 실행하지 않았어요", "hello()"),
      ("TypeError: ... missing 1 required positional argument", "인자를 덜 넣었어요", "def 줄 칸 수 세기"),
      ("TypeError: ... takes 2 positional arguments but 3 were given", "인자를 더 넣었어요", "def 줄 칸 수 세기"),
      ("NameError: name 'welcome' is not defined", "def 셀보다 먼저 불렀어요", "def 셀 먼저 실행"),
      ("돌려받은 값이 None이에요", "함수에 return이 없어요", "print 대신 return"),
      ("TypeError: ... 'NoneType' and 'int'", "None으로 계산했어요", "return 넣기"),
      ("return 아래 print가 안 찍혀요", "return에서 함수가 끝났어요", "return 위로 옮기기")]
o.append('<div style="position:absolute;left:96px;top:196px;width:1728px;height:724px;display:flex;flex-direction:column;gap:8px">')
for i, (q, a_, cmd) in enumerate(tr, 1):
    o.append(f'<div data-build-in="rise order {min(i, 6)}" style="flex:1;display:flex;flex-direction:row;gap:26px;align-items:center;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:6px 30px">'
             + num(i, RED, 30)
             + '<div style="flex:1;display:flex;flex-direction:column;gap:2px">' + p(f"{'font-family:' + MONO + ';' if q.isascii() else ''}font-size:22px;font-weight:700;color:{INK};white-space:nowrap", e(q)) + p(f"font-size:21px;color:{SUB}", e(a_)) + '</div>'
             + p(f"width:380px;flex:none;{'font-family:' + MONO + ';font-size:22px;' if cmd.isascii() else 'font-size:23px;'}font-weight:700;line-height:1.4;color:{INK};background:#EEEFF2;padding:6px 18px;border-radius:12px;white-space:pre", e(cmd)) + '</div>')
o.append('</div>')
o.append(caption("결과가 이상하면 함수 안에 print를 넣어 받은 값과 돌려줄 값을 찍어 봐요.", 950))
W("trouble", o, "함수에서 자주 만나는 일을 모았어요. 1번은 괄호를 빼서 함수를 실행하지 않은 경우예요. 2번과 3번은 칸 수와 인자 수가 맞지 않아요. def 줄을 보고 칸을 세어 봐요. 4번은 노트북에서 셀 순서가 꼬였을 때 자주 나요. 5번과 6번은 return이 빠진 함수예요. 7번은 오류 없이 줄이 빠지는 경우예요. 결과가 이상하면 함수 안에 print를 넣어 매개변수에 무엇이 들어왔는지 찍어 보면 원인이 보여요.", ("trouble", "정리"))

o = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>']
cheat = [("def 이름():", "함수 만들기(정의)", K2), ("이름()", "함수 실행하기(호출)", K2), ("def f(a, b):", "매개변수 칸 두 개", K3), ("f(1, 2)", "인자는 순서대로", K3),
         ("return 값", "값을 돌려주고 끝내기", K4), ("None", "return이 없을 때", K4), ("return a, b", "튜플로 돌려주기", K4), ("x, y = f()", "나눠서 받기", K4)]
for i, (k, d, c) in enumerate(cheat):
    x, y = 96 + (i % 4) * 438, 200 + (i // 4) * 290
    o.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:414px;height:264px;background:{CARD};border:2px solid {LINE};border-top:10px solid {c};border-radius:20px;padding:28px 28px;display:flex;flex-direction:column;gap:20px">'
             + mono(k, 26 if len(k) <= 17 else 22, c, "#F6F5F1", "align-self:flex-start") + p(f"font-size:28px;font-weight:700;color:{INK}", d) + '</div>')
o.append(f'<div style="position:absolute;left:96px;top:780px;width:1728px;height:210px;background:{CARD};border:2px solid {LINE};border-radius:20px;padding:24px 36px;display:flex;flex-direction:column;justify-content:center;gap:14px">'
         + p(f"font-size:30px;font-weight:700;color:{INK}", "사람이 볼 값은 print, 다음 계산에 쓸 값은 return")
         + p(f"font-size:30px;font-weight:700;color:{INK}", "다음 챕터: 기본값, 키워드 인자, 지역 변수와 전역 변수") + '</div>')
W("cheatsheet", o, "이번 챕터에서 쓴 모양을 한 장에 모았어요. def로 만들고 이름과 괄호로 불러요. 괄호 안의 칸이 매개변수, 부를 때 넣는 값이 인자이고 순서대로 짝을 지어요. return은 값을 돌려주면서 함수를 끝내고, return이 없으면 None이 돌아와요. 20에서는 인자를 안 넣어도 되는 기본값, 칸 이름으로 넣는 키워드 인자, 함수 안과 밖의 변수가 어떻게 다른지 배워요.")

# ---------- toc ----------
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
parts = [("Lightbulb", K1, "왜 필요한가", "손님마다 복사한 계산, 재료와 결과 상자, 가장 짧은 def", "f-why", "f-min"),
         ("Code", K2, "정의와 호출", "def 줄 다섯 조각, 정의만 하면 안 찍혀요, 몸통으로 갔다 돌아오기", "d-shape", "d-flow"),
         ("Key", K3, "매개변수와 인자", "재료 칸 하나, 여러 개, 순서대로 들어가요", "a-one", "a-order"),
         ("PaperPlane", K4, "return", "돌려주기, print와 비교, None, 바로 끝내기, 값 여러 개", "r-ret", "r-multi"),
         ("Warning", K5, "오류와 함정", "괄호 빼기, 인자 수 TypeError, return 아래 줄, None 계산, NameError", "t-paren", "t-name"),
         ("Star", K6, "실습", "장바구니 총액, 품절 확인, 성적 등급, 할인 결제", "x-total", "x-pay")]
TOC_NOTE = "여섯 파트로 나눴어요. 1파트는 함수가 왜 필요한지와 큰 그림, 2파트는 def로 만들고 부르는 법이에요. 3파트는 괄호 안의 재료 칸, 4파트는 return으로 결과를 돌려받는 법이에요. print와 return의 차이를 꼭 짚어요. 5파트는 자주 나는 오류, 6파트는 앞 챕터의 카페 코드를 함수로 바꾸는 실습이에요. 파트마다 새 커널에서 위에서부터 차례로 실행해요."

DECK_TITLE = "함수 1 (정의, 매개변수, return)"
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
    f.write("\n".join(t) + f"\n<aside>{e(TOC_NOTE)}</aside>\n</section>\n")

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-03T03:00:00Z"}, "lists": "css", "title": DECK_TITLE, "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
print(len(ORDER), "slides")
