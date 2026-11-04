"""Generates every slide of the functions 3 deck (21, lambda, map, filter) and slides/deck.json.

Story: keeps writing in basics.ipynb from chapters 12-20. Starts from the for-and-append block written again for every
price change, draws map (change each value) and filter (keep the True ones) as pipes, then treats a function as a value
(store it, pass it), lambda next to def, map, map objects, built-in functions passed by name, filter with lists and
dictionaries, and filter feeding map. Part 5 collects the usual errors, and part 6 uses the café menu, stock and orders.
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
    deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-04T03:00:00Z"}, "lists": "css", "title": title, "order": ORDER,
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


EB1 = "1. 왜 필요한가"
EB2 = "2. 함수를 값처럼, lambda"
EB3 = "3. map"
EB4 = "4. filter"
EB5 = "5. 오류와 함정"
EB6 = "6. 실습"
PR = "prices = [4500, 5000, 6500]"


def lam_line(parts, size=44):
    """One code line with colored pieces: parts = [(text, color), ...]."""
    return p(f"font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.45;color:#E6E9EF;white-space:pre",
             "".join(f'<span style="color:{c}">{e(t)}</span>' for t, c in parts))


def dark(left, top, w, h, lines, attrs=""):
    return (f'<div{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:#252B36;border-radius:22px;padding:30px 40px;display:flex;flex-direction:column;justify-content:center;gap:8px">'
            + "".join(lines) + '</div>')


# ---------- cover ----------
cover([(PR, "#E6E9EF"), ("", "#E6E9EF"), ("list(map(lambda p: p + 500, prices))", "#8FD8DE"), ("# [5000, 5500, 7000]", "#9AA1AE"), ("", "#E6E9EF"),
       ("list(filter(lambda p: p >= 5000, prices))", "#E3B877"), ("# [5000, 6500]", "#9AA1AE")],
      "함수 3<br>lambda<br>map, filter", "짧은 함수는 이름 없이 만들고<br>리스트 전체에 한 번에 쓰기",
      "19와 20에서 def로 함수를 만들었어요. 이번에는 함수를 값처럼 변수에 담고 다른 함수에 넘겨요. 한 줄짜리 함수는 lambda로 이름 없이 만들어요. 리스트의 값마다 함수를 쓰는 map, 조건에 맞는 값만 남기는 filter를 같이 배워요. 22의 정렬과 23의 리스트 컴프리헨션이 이 챕터를 바탕으로 해요.")

ready([("리스트, 튜플, for, append", "13"), ("딕셔너리 키로 for 돌기", "15"), ("if, 한 줄 if else", "17"), ("def, return, 괄호를 뺀 hello", "19"), ("키워드 인자 reverse=True", "20")], "20",
      "09에서 만든 hello-uv 폴더를 VS Code로 열고, 12부터 쓰던 basics.ipynb를 다시 열어요. 13의 리스트와 튜플, 15의 딕셔너리, 17의 한 줄 if else, 19의 def와 return을 그대로 써요. 19에서 괄호를 빼고 hello만 적으면 함수 자체가 나왔던 장면을 기억해 두면 2파트가 쉬워요. 슬라이드의 출력은 tools/demo.sh가 hello-uv 커널에서 같은 셀을 실제로 실행한 결과예요. 셀 번호는 파트마다 [1]부터 다시 셌어요.")

# ---------- part 1 ----------
o = [sec("l-why")] + head(EB1, "가격을 바꿀 때마다 for 네 줄을 다시 적어요", K1)
WHY = [PR, "up = []", "for p in prices:", "    up.append(p + 500)", "print(up)", "down = []", "for p in prices:", "    down.append(p - 500)", "print(down)"]
o += cell({"id": "c-why", "lines": WHY, "n": 1, "out": ["[5000, 5500, 7000]", "[4000, 4500, 6000]"]}, 96, 200, 1010, sel="c-why")
o.append(hl(96, 200, 1010, 3, 1, "mark", 1, "500원 올리기"))
o.append(hl(96, 200, 1010, 7, 1, "mark", 2, "500원 내리기"))
o.append(note_card(1150, 200, 674, 300, "달라진 건 한 줄뿐", "p + 500과 p - 500만 달라요. 빈 리스트, for, append는 똑같이 되풀이해요.", K1, ' data-build-in="rise order 3"'))
o.append(note_card(1150, 530, 674, 330, "자주 나오는 틀이에요", "값마다 바꾸기, 조건에 맞는 값만 고르기는 카페 데이터에서 계속 나와요.", OR, ' data-build-in="rise order 4"'))
o.append(caption("리스트 전체에 같은 일을 할 때마다 같은 틀을 다시 적고 있어요.", 930))
W("l-why", o, "13의 가격 리스트로 모든 가격을 500원 올리고, 다시 500원 내려 봐요. for와 append로 새 리스트를 만드는 네 줄이 두 번 나와요. 두 덩어리에서 달라진 건 p + 500과 p - 500, 한 줄뿐이에요. 값마다 같은 일을 해서 새 리스트를 만드는 틀은 앞으로도 자주 나와요. 이 틀을 한 줄로 줄이는 방법이 이번 챕터예요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p1", "왜 필요한가"))

o = [sec("l-big")] + head(EB1, "map은 하나씩 바꾸고, filter는 골라내요", K1)
o.append(label("map: 값마다 바꿔요", 150, 196, K3, ' data-build-in="fade order 1"', 640, 30))
o += pipe(150, 250, ["4500", "5000", "6500"], "p + 500", ["5000", "5500", "7000"], K3, K3BG, 1, 200)
o.append(label("filter: 조건에 맞는 값만 남겨요", 1100, 196, K4, ' data-build-in="fade order 4"', 700, 30))
o += pipe(1100, 250, ["4500", "5000", "6500"], "p >= 5000", ["4500", "5000", "6500"], K4, K4BG, 4, 200, keep=[False, True, True])
o.append(note_card(96, 620, 846, 250, "map(함수, 리스트)", "리스트의 값을 하나씩 함수에 넣고, 돌려받은 값을 모아요. 개수는 그대로예요.", K3, ' data-build-in="rise order 7"'))
o.append(note_card(978, 620, 846, 250, "filter(함수, 리스트)", "함수가 True를 돌려준 값만 남겨요. 값은 그대로이고 개수가 줄어요.", K4, ' data-build-in="rise order 8"'))
o.append(caption("가운데 띠에 넣는 짧은 함수를 lambda로 만들어요.", 930))
W("l-big", o, "큰 그림부터 봐요. map은 리스트의 값을 하나씩 가운데 함수에 넣어요. 함수가 돌려준 값을 순서대로 모아서 새 결과를 만들어요. 값이 셋이면 결과도 셋이에요. filter도 값을 하나씩 함수에 넣는데, 함수는 True나 False를 돌려줘요. True인 값만 아래로 내려가고 False인 값은 버려요. 값은 바뀌지 않고 개수만 줄어요. 가운데 띠에 들어가는 p + 500, p >= 5000 같은 짧은 함수를 lambda로 만들어요.")

o = [sec("l-min")] + head(EB1, "가장 짧은 map: 값마다 10 더하기", K1)
o += cell({"id": "c-min", "lines": ["numbers = [1, 2, 3]", "print(list(map(lambda x: x + 10, numbers)))"], "n": 3, "out": ["[11, 12, 13]"]}, 96, 200, 1000, sel="c-min")
o += pipe(96, 420, ["1", "2", "3"], "lambda x: x + 10", ["11", "12", "13"], K1, K1BG, 1, 200, fn_w=616)
o.append(callout(1150, 200, 674, 150, "lambda x: x + 10", "x를 받아 x + 10을 돌려주는 함수", K2, 4, 24))
o.append(callout(1150, 380, 674, 150, "map(…, numbers)", "numbers의 값마다 함수를 써요", K3, 5, 24))
o.append(callout(1150, 560, 674, 150, "list(…)", "나온 값을 리스트로 모아요", K1, 6, 24))
o.append(caption("함수와 리스트를 map에 넘기면 값마다 함수를 써서 결과를 모아 줘요.", 930))
W("l-min", o, "가장 짧은 예예요. numbers의 값 1, 2, 3에 10씩 더해요. lambda x: x + 10은 x를 받아 x + 10을 돌려주는 함수예요. 2파트에서 자세히 봐요. map은 이 함수를 numbers의 값마다 써요. 1을 넣으면 11, 2를 넣으면 12, 3을 넣으면 13이 나와요. 마지막으로 list로 감싸서 [11, 12, 13] 리스트로 모아요. list가 왜 필요한지는 3파트에서 봐요. 앞 장의 for 네 줄이 한 줄이 됐어요." + REAL)

# ---------- part 2 ----------
o = [sec("v-value")] + head(EB2, "함수도 변수에 담을 수 있어요", K2)
o += cell({"id": "c-v1", "lines": ["def add10(x):", "    return x + 10", "", "plus = add10", "print(plus(5))", "print(add10)"], "n": 1, "out": ["15", "<function add10 at 0x7fdb817ce4b0>"]}, 96, 200, 1000, sel="c-v1")
o.append(hl(96, 200, 1000, 3, 1, "mark", 1, "괄호 없이"))
o.append(f'<div data-build-in="rise order 2" style="position:absolute;left:1150px;top:200px;width:674px;height:290px">'
         + f'<div style="position:absolute;left:40px;top:0">{chip("add10", K2, K2BG, 30)}</div>'
         + f'<div style="position:absolute;left:400px;top:0">{chip("plus", K2, K2BG, 30)}</div>'
         + f'<x-shape kind="arrow-right" style="position:absolute;left:96px;top:86px;width:44px;height:26px;transform:rotate(90deg);background:#C9CED8"></x-shape>'
         + f'<x-shape kind="arrow-right" style="position:absolute;left:440px;top:86px;width:44px;height:26px;transform:rotate(90deg);background:#C9CED8"></x-shape>'
         + f'<div style="position:absolute;left:0;top:130px;width:674px;height:150px;border-radius:20px;background:{K2};display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px">'
         + p(f"font-size:24px;font-weight:700;color:#FFFFFF", "함수 하나") + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:#FFFFFF", "x를 받아 x + 10") + '</div></div>')
o.append(note_card(1150, 520, 674, 340, "이름표가 하나 더 붙어요", "plus = add10은 함수를 실행하지 않아요. 같은 함수에 plus라는 이름을 하나 더 붙여서 plus(5)도 15가 돼요.", K2, ' data-build-in="rise order 3"'))
o.append(note_card(96, 580, 1000, 280, "19에서 본 그 모양이에요", "괄호를 빼면 실행하지 않고 함수 자체가 나왔어요. 0x로 시작하는 숫자는 실행할 때마다 달라요.", GRAY, ' data-build-in="rise order 4"'))
o.append(caption("괄호를 빼면 함수를 실행하지 않고 값처럼 다룰 수 있어요.", 930))
W("v-value", o, "19에서 괄호를 빼고 hello만 적었더니 함수 자체가 나왔어요. 함수도 숫자나 리스트처럼 하나의 값이에요. 그래서 plus = add10처럼 다른 변수에 담을 수 있어요. 괄호가 없으니 add10을 실행하지 않고 함수 그대로 담아요. 이제 plus와 add10은 같은 함수를 가리켜서 plus(5)도 15예요. print(add10)의 0x로 시작하는 숫자는 함수가 저장된 메모리 위치라서 화면마다 달라요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p2", "함수를 값처럼, lambda"))

o = [sec("v-pass")] + head(EB2, "함수를 다른 함수에 넘길 수 있어요", K2)
o += cell({"id": "c-v2", "lines": ["def double(x):", "    return x * 2", "", "def apply(f, x):", "    return f(x)", "", "print(apply(add10, 5))", "print(apply(double, 5))"], "n": 2, "out": ["15", "10"]}, 96, 200, 1000, sel="c-v2")
o.append(hl(96, 200, 1000, 4, 1, "mark", 1, "받은 함수를 불러요"))
for i, (a_, b_, c_) in enumerate([("apply(add10, 5)", "add10(5)", "15"), ("apply(double, 5)", "double(5)", "10")]):
    o.append(f'<div data-build-in="rise order {i + 2}" style="position:absolute;left:1150px;top:{200 + i * 130}px;width:674px;height:110px;background:{CARD};border:2px solid {LINE};border-radius:16px;padding:0 22px;display:flex;flex-direction:row;align-items:center;gap:14px">'
             + mono(a_, 24, INK, "#F1F0EC") + arrow(40, K2) + mono(b_, 24, K2, K2BG) + arrow(40, K2) + mono(c_, 24, INK, "#F1F0EC") + '</div>')
o.append(note_card(1150, 480, 674, 380, "함수를 받는 함수", "apply는 f 칸에 함수를 받아서 f(x)로 불러요. 넘길 때는 괄호 없이 이름만 적어요. map과 filter도 이렇게 함수를 받아요.", K2, ' data-build-in="rise order 4"'))
o.append(caption("함수도 인자로 넘길 수 있어요. 넘길 때는 이름만 적어요.", 930))
W("v-pass", o, "함수가 값이라서 다른 함수의 인자로도 넘길 수 있어요. apply는 함수 f와 값 x를 받아서 f(x)를 돌려줘요. apply(add10, 5)로 부르면 f 칸에 add10이 들어가서 add10(5)가 되고 15가 나와요. double을 넘기면 double(5)가 돼서 10이에요. 넘길 때 add10에 괄호를 붙이지 않은 점을 봐 두세요. 괄호를 붙이면 그 자리에서 실행해 버려요. 3파트의 map과 4파트의 filter가 바로 이렇게 함수를 받는 함수예요. add10은 앞 셀에서 정의했어요." + REAL)

o = [sec("d-side")] + head(EB2, "lambda는 한 줄로 만드는 이름 없는 함수예요", K2)
LB, LX, LC, LV = "#9DBDEB", "#8FD8DE", "#F2A0A0", "#B8E8BE"
o.append(label("def로 만들기", 96, 196, GRAY, "", 840, 26))
o.append(dark(96, 240, 840, 200, [lam_line([("def", LB), (" add10", "#E3B877"), ("(", "#E6E9EF"), ("x", LX), ("):", "#E6E9EF")], 38),
                                  lam_line([("    return ", "#E6E9EF"), ("x + 10", LV)], 38)]))
o.append(label("lambda로 만들기", 984, 196, K2, ' data-build-in="fade order 1"', 840, 26))
o.append(dark(984, 240, 840, 200, [lam_line([("lambda", LB), (" ", "#E6E9EF"), ("x", LX), (":", LC), (" x + 10", LV)], 44)], ' data-build-in="rise order 1"'))
for i, (k, d, c) in enumerate([("lambda", "함수를 만든다는 표시예요. def 대신 써요", BL), ("x", "매개변수예요. 괄호 없이 적어요", TEAL), (":", "콜론 뒤가 돌려줄 값이에요", RED), ("x + 10", "return 없이도 이 값을 돌려줘요", GR)]):
    o.append(callout(96 + (i % 2) * 888, 480 + (i // 2) * 170, 840, 150, k, d, c, i + 2, 26))
o.append(caption("이름, 괄호, return을 빼고 돌려줄 값 하나만 남긴 모양이에요.", 930))
W("d-side", o, "왼쪽은 19에서 배운 def 함수예요. 오른쪽 lambda도 같은 일을 하는 함수예요. 조각을 나눠 봐요. lambda는 def처럼 함수를 만든다는 표시예요. 그 뒤 x가 매개변수인데 괄호 없이 적어요. 콜론 뒤에는 돌려줄 값을 적어요. return을 쓰지 않아도 이 값이 돌아가요. 함수 이름 자리가 없어서 이름 없는 함수라고 불러요. 몸통에는 값 하나, 곧 식 하나만 적을 수 있어요.")

o = [sec("d-call")] + head(EB2, "lambda는 다른 함수에 바로 넘길 때 써요", K2)
o.append(label("변수에 담아 부르기", 96, 196, GRAY, ' data-build-in="fade order 1"', 1000, 26))
o += cell({"id": "c-d1", "lines": ["add10 = lambda x: x + 10", "print(add10(5))", "print(add10)"], "n": 3, "out": ["15", "<function <lambda> at 0x7fdb817cf270>"]}, 96, 240, 1000, attrs=' data-build-in="rise order 1"')
o.append(label("이름 없이 바로 넘기기", 96, 500, K2, ' data-build-in="fade order 3"', 1000, 26))
o += cell({"id": "c-d2", "lines": ["print(apply(lambda x: x * 3, 5))"], "n": 4, "out": ["15"]}, 96, 544, 1000, attrs=' data-build-in="rise order 3"')
o.append(note_card(1150, 240, 674, 230, "이름이 &lt;lambda&gt;예요", "lambda 함수에는 이름이 없어요. add10은 그 함수를 담은 변수일 뿐이에요.", GRAY, ' data-build-in="rise order 2"'))
o.append(note_card(1150, 500, 674, 360, "한 번 쓸 함수는 그 자리에", "앞 장의 apply에 lambda를 바로 넘겼어요. def로 이름을 붙이지 않아도 돼요.", K2, ' data-build-in="rise order 4"'))
o.append(note_card(96, 700, 1000, 160, "여러 번 부를 함수는 def로", "add10 = lambda보다 def add10(x):가 읽기 쉬워요.", OR, ' data-build-in="rise order 5"'))
o.append(caption("한 번 쓰고 말 짧은 함수는 lambda로 그 자리에 적어요.", 940))
W("d-call", o, "lambda로 만든 함수도 변수에 담아 부를 수 있어요. add10(5)는 15예요. print로 찍으면 함수 이름 자리에 lambda가 나와요. 이름 없는 함수라서예요. 그런데 lambda를 가장 많이 쓰는 곳은 아래 셀처럼 다른 함수에 바로 넘기는 자리예요. 앞 장의 apply에 x를 3배 하는 함수를 이름 없이 적어서 넘겼어요. 한 번 쓰고 말 함수에 def와 이름까지 붙이지 않아도 돼요. 반대로 여러 번 부를 함수라면 def로 만드는 편이 읽기 쉬워요. apply는 앞 셀에서 정의했어요." + REAL)

o = [sec("d-more")] + head(EB2, "매개변수 여러 개, 한 줄 if else도 돼요", K2)
o += cell({"id": "c-d3", "lines": ["price_of = lambda price, qty: price * qty", "print(price_of(4500, 2))", 'label = lambda p: "비쌈" if p >= 5000 else "보통"', "print(label(6500), label(4500))"], "n": 5, "out": ["9000", "비쌈 보통"]}, 96, 200, 1100, sel="c-d3")
o.append(hl(96, 200, 1100, 0, 1, "mark", 1, "쉼표로 둘"))
o.append(hl(96, 200, 1100, 2, 1, "mark", 2, "17의 한 줄 if"))
o.append(note_card(1240, 200, 584, 260, "if 문은 못 넣어요", "콜론 뒤에는 값 하나만 와요. 한 줄 if else는 값이라서 돼요.", K5, ' data-build-in="rise order 3"'))
rows_ = [("", "def", "lambda"), ("이름", "있어요", "없어요"), ("몸통", "여러 줄", "값 하나"), ("return", "적어요", "안 적어요"), ("언제", "여러 번 부를 함수", "다른 함수에 바로 넘길 때")]
for i, r in enumerate(rows_):
    hd = i == 0
    o.append(f'<div data-build-in="rise order {4 if i < 2 else i + 3}" style="position:absolute;left:96px;top:{500 + i * 80}px;width:1728px;height:70px;background:{"transparent" if hd else CARD};border:{"none" if hd else "2px solid " + LINE};border-radius:14px;padding:0 28px;display:flex;flex-direction:row;align-items:center;gap:20px">'
             + p(f"width:200px;flex:none;font-size:24px;font-weight:700;color:{GRAY}", e(r[0]))
             + p(f"width:700px;flex:none;{'font-family:' + MONO + ';' if hd else ''}font-size:{26 if hd else 25}px;font-weight:700;color:{OR if hd else INK}", e(r[1]))
             + p(f"flex:1;{'font-family:' + MONO + ';' if hd else ''}font-size:{26 if hd else 25}px;font-weight:700;color:{K2 if hd else INK}", e(r[2])) + '</div>')
W("d-more", o, "lambda도 매개변수를 쉼표로 여러 개 받을 수 있어요. price_of는 가격과 잔 수를 받아 곱한 값을 돌려줘요. 콜론 뒤에는 값 하나만 올 수 있어서 17의 if 문은 못 넣어요. 대신 17에서 배운 한 줄 if else는 값 하나로 계산되니까 쓸 수 있어요. 아래 표에 def와 lambda를 나란히 정리했어요. 이름이 있는지, 몸통이 몇 줄인지, return을 적는지가 달라요. 여러 번 부를 함수는 def, 다른 함수에 바로 넘길 짧은 함수는 lambda로 만들어요." + REAL)

# ---------- part 3 ----------
o = [sec("m-three")] + head(EB3, "for 네 줄이 map 한 줄이 돼요", K3)
o += cell({"id": "c-m1", "lines": [PR, "", "def add500(p):", "    return p + 500", "", "print(list(map(add500, prices)))", "print(list(map(lambda p: p + 500, prices)))", "print(prices)"], "n": 1, "out": ["[5000, 5500, 7000]", "[5000, 5500, 7000]", "[4500, 5000, 6500]"]}, 96, 200, 1240, sel="c-m1")
o.append(hl(96, 200, 1240, 5, 1, "mark", 1, "def 이름 넘기기"))
o.append(hl(96, 200, 1240, 6, 1, "run", 2, "lambda 바로 넘기기"))
o.append(hl(96, 200, 1240, 7, 1, "skip", 3, "원본은 그대로"))
o.append(side(1380, 200, 444, 250, "1파트의 for", ["up = []", "for p in prices:", "    up.append(p + 500)"], [], GRAY, "#F1F0EC", ' data-build-in="rise order 4"', 24, "같은 결과"))
o.append(note_card(1380, 480, 444, 380, "map은 새 결과를 만들어요", "세 방법 모두 [5000, 5500, 7000]이에요. prices는 바뀌지 않아요. 13의 sorted처럼 원본을 두고 새 결과를 줘요.", K3, ' data-build-in="rise order 5"'))
o.append(caption("map(함수, 리스트)는 for와 append로 새 리스트를 만드는 일을 한 줄로 줄여요.", 930))
W("m-three", o, "같은 일을 세 가지로 써 봐요. 1파트의 for와 append, def로 만든 add500을 map에 넘기기, lambda를 바로 넘기기예요. 결과는 셋 다 [5000, 5500, 7000]이에요. def로 넘길 때는 add500에 괄호를 붙이지 않아요. 2파트에서 본 것처럼 함수를 넘기는 거라서예요. map은 새 결과를 만들고 prices는 그대로 둬요. 13의 sorted가 원본을 두고 새 리스트를 준 것과 같아요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p3", "map"))

o = [sec("m-pic")] + head(EB3, "map은 값을 하나씩 함수에 넣어요", K3)
o += pipe(96, 220, ["4500", "5000", "6500"], "lambda p: p + 500", ["5000", "5500", "7000"], K3, K3BG, 1, 240)
o += steps([("1", "p = 4500", "4500 + 500을 돌려줘요"), ("2", "p = 5000", "5000 + 500을 돌려줘요"), ("3", "p = 6500", "6500 + 500을 돌려줘요")], 960, 220, 864, 4, K3, 104, (40, 260))
o.append(note_card(96, 640, 846, 230, "순서도 개수도 그대로", "넣은 순서대로 결과가 나와요. 값이 셋이면 결과도 셋이에요.", K3, ' data-build-in="rise order 7"'))
o.append(note_card(978, 640, 846, 230, "p는 lambda의 매개변수", "값이 하나씩 p 칸에 들어가요. 13의 for p in prices:의 p와 같은 역할이에요.", OR, ' data-build-in="rise order 8"'))
o.append(caption("map이 리스트의 값을 차례로 lambda에 넣고, 돌려받은 값을 모아요.", 930))
W("m-pic", o, "map 안에서 무슨 일이 일어나는지 그림으로 봐요. 첫 값 4500이 lambda의 p 칸에 들어가서 5000이 돌아와요. 다음 5000이 들어가 5500, 6500이 들어가 7000이 돌아와요. map은 이렇게 돌려받은 값을 순서대로 모아요. 그래서 결과는 원래 순서 그대로이고 개수도 같아요. lambda의 p는 13에서 for p in prices:라고 적었을 때 p와 같은 역할이에요.")

o = [sec("m-obj")] + head(EB3, "map만 찍으면 &lt;map object&gt;가 나와요", K3)
o += cell({"id": "c-m2", "lines": ["m = map(lambda p: p + 500, prices)", "print(m)", "print(list(m))"], "n": 2, "out": ["<map object at 0x7fe9b3214840>", "[5000, 5500, 7000]"]}, 96, 200, 1000, sel="c-m2")
o += cell({"id": "c-m3", "lines": ["for p in map(lambda p: p + 500, prices):", "    print(p)"], "n": 3, "out": ["5000", "5500", "7000"]}, 96, 480, 1000, attrs=' data-build-in="rise order 3"')
o.append(note_card(1150, 200, 674, 330, "map은 꺼내 줄 준비만 해요", "map object는 달라고 하면 값을 하나씩 꺼내 주는 묶음이에요. 아직 결과를 다 만들지 않았어요.", K3, ' data-build-in="rise order 1"'))
o.append(note_card(1150, 560, 674, 300, "list()가 끝까지 꺼내요", "list로 감싸면 값을 끝까지 꺼내 리스트로 모아요. for도 하나씩 꺼내 쓸 수 있어요.", GR, ' data-build-in="rise order 2"'))
o.append(note_card(96, 740, 1000, 140, "0x로 시작하는 숫자는 화면마다 달라요", "", GRAY, ' data-build-in="rise order 4"'))
o.append(caption("결과를 리스트로 보려면 list()로 감싸요.", 940))
W("m-obj", o, "list를 빼고 map만 찍으면 map object at 뒤에 숫자가 나와요. 오류가 아니에요. map은 결과를 바로 다 만들지 않고, 달라고 하면 값을 하나씩 꺼내 주는 묶음을 돌려줘요. list로 감싸면 값을 끝까지 꺼내서 리스트로 모아요. 그래서 지금까지 list(map(...))처럼 적었어요. for도 값을 하나씩 꺼내니까 찍기만 할 때는 list 없이 for로 돌려도 돼요. 0x 뒤 숫자는 메모리 위치라서 화면마다 달라요." + REAL)

o = [sec("m-builtin")] + head(EB3, "이미 있는 함수도 이름만 넘겨요", K3)
o += cell({"id": "c-m4", "lines": ["print(list(map(str, prices)))", 'print(", ".join(map(str, prices)))', 'print(list(map(int, ["3", "1", "2"])))', 'print(list(map(len, ["coffee", "latte", "tea"])))'], "n": 4, "out": ["['4500', '5000', '6500']", "4500, 5000, 6500", "[3, 1, 2]", "[6, 5, 3]"]}, 96, 200, 1100, sel="c-m4")
o.append(callout(1240, 200, 584, 150, "str", "숫자를 글자로. join 앞에", K3, 1, 26))
o.append(callout(1240, 370, 584, 150, "int", "글자를 숫자로. 12의 타입 바꾸기", OR, 2, 26))
o.append(callout(1240, 540, 584, 150, "len", "값마다 길이를 재요", BL, 3, 26))
o.append(note_card(96, 580, 1100, 280, "join은 글자만 이어요", "13의 join에 숫자 리스트를 넣으면 오류가 나요. map(str, prices)로 글자로 바꿔 넘기면 한 줄로 이어 찍을 수 있어요.", K3, ' data-build-in="rise order 4"'))
o.append(caption("str, int, len처럼 이미 있는 함수로 되는 일은 lambda 없이 이름만 넘겨요.", 930))
W("m-builtin", o, "map에는 우리가 만든 함수만 넘기는 게 아니에요. 12에서 배운 str, int와 13의 len도 함수라서 괄호 없이 이름만 넘기면 돼요. map(str, prices)는 가격마다 str을 써서 글자 리스트를 만들어요. 13의 join은 글자만 이을 수 있어서 숫자 리스트를 넣으면 오류가 나요. map(str, prices)를 넘기면 쉼표로 이은 한 줄이 돼요. int는 반대로 글자를 숫자로 바꾸고, len은 값마다 길이를 재요. 이미 있는 함수로 되는 일에는 lambda를 따로 만들지 않아요." + REAL)

# ---------- part 4 ----------
o = [sec("f-for")] + head(EB4, "for와 if로 골라 담던 일을 filter 한 줄로", K4)
o += cell({"id": "c-f1", "lines": ["prices = [4500, 5000, 6500, 3000]", "big = []", "for p in prices:", "    if p >= 5000:", "        big.append(p)", "print(big)", "print(list(filter(lambda p: p >= 5000, prices)))"], "n": 1, "out": ["[5000, 6500]", "[5000, 6500]"]}, 96, 200, 1100, sel="c-f1")
o.append(hl(96, 200, 1100, 2, 3, "mark", 1, "17의 골라 담기"))
o.append(hl(96, 200, 1100, 6, 1, "run", 2, "filter 한 줄"))
o.append(note_card(1240, 200, 584, 330, "filter(함수, 리스트)", "함수가 True를 돌려준 값만 남겨요. lambda 자리에는 True나 False가 나오는 조건을 적어요.", K4, ' data-build-in="rise order 3"'))
o.append(note_card(1240, 560, 584, 300, "원본은 그대로", "filter도 새 결과를 줘요. 결과를 보려면 map처럼 list로 감싸요.", GRAY, ' data-build-in="rise order 4"'))
o.append(caption("for 안의 if로 골라 담는 일은 filter 한 줄로 줄여요.", 930))
W("f-for", o, "17에서 for 안에 if를 넣어 조건에 맞는 값만 골라 담았어요. 5000원 이상인 가격만 big에 담는 다섯 줄이에요. filter는 이 일을 한 줄로 해요. 첫째 인자는 조건 함수이고, 둘째는 리스트예요. 조건 함수가 True를 돌려준 값만 남아요. lambda p: p >= 5000은 p가 5000 이상인지 True나 False로 답해요. filter도 map처럼 결과를 꺼내 줄 준비만 하니까 list로 감싸서 봐요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p4", "filter"))

o = [sec("f-pic")] + head(EB4, "True를 받은 값만 아래로 내려가요", K4)
o += pipe(96, 220, ["4500", "5000", "6500", "3000"], "lambda p: p >= 5000", ["4500", "5000", "6500", "3000"], K4, K4BG, 1, 190, keep=[False, True, True, False])
o += cell({"id": "c-f2", "lines": ["check = lambda p: p >= 5000", "print(check(4500), check(5000))", "print(check(6500), check(3000))"], "n": 2, "out": ["False True", "True False"]}, 960, 200, 864, attrs=' data-build-in="rise order 4"')
o += table(960, 470, 864, [("p", 140), ("p >= 5000", 220), ("filter는", 260)], [("4500", "False", "버려요"), ("5000", "True", "남겨요"), ("6500", "True", "남겨요"), ("3000", "False", "버려요")], 5, K4, 60, hi=(1, 2))
o.append(note_card(96, 620, 784, 250, "5000도 남아요", ">=는 같아도 True예요. 12의 비교 연산과 같아요.", OR, ' data-build-in="rise order 9"'))
o.append(caption("filter에 넘기는 함수는 True나 False를 돌려주는 조건이에요.", 930))
W("f-pic", o, "filter 안을 그림으로 봐요. 값이 하나씩 lambda에 들어가요. 4500은 False라서 버리고, 5000과 6500은 True라서 남겨요. 3000도 False예요. 오른쪽 셀은 같은 lambda를 check라는 이름에 담고 값마다 직접 불러 본 거예요. 돌려받은 True, False가 표와 같아요. 5000은 >=라서 같아도 True예요. map은 돌려받은 값을 모으고, filter는 True를 받은 원래 값을 모은다는 점이 달라요." + REAL)

o = [sec("f-dict")] + head(EB4, "딕셔너리를 넘기면 키가 하나씩 들어가요", K4)
o += cell({"id": "c-f3", "lines": ['stock = {"coffee": 3, "latte": 0, "cake": 2, "tea": 0}', "print(list(filter(lambda m: stock[m] > 0, stock)))"], "n": 3, "out": ["['coffee', 'cake']"]}, 96, 200, 1100, sel="c-f3")
o.append(lockers([("coffee", "3"), ("latte", "0"), ("cake", "2"), ("tea", "0")], 96, 420, 250, 170, K4, K4BG, hi=(0, 2), attrs=' data-build-in="rise order 1"'))
o.append(f'<div data-build-in="rise order 2" style="position:absolute;left:96px;top:640px;width:1100px;height:90px;display:flex;flex-direction:row;align-items:center;gap:20px">'
         + p(f"font-size:26px;font-weight:700;color:{SUB}", "재고가 0보다 큰 키만") + arrow(60, K4) + chip("['coffee', 'cake']", K4, K4BG, 30) + '</div>')
o.append(note_card(1240, 200, 584, 330, "m에는 키가 들어가요", "15에서 for m in stock:이 키를 꺼낸 것과 같아요. 값은 stock[m]으로 봐요.", K4, ' data-build-in="rise order 3"'))
o.append(note_card(1240, 560, 584, 300, "결과는 키 리스트", "품절이 아닌 메뉴 이름만 남았어요. 재고 숫자는 들어 있지 않아요.", GRAY, ' data-build-in="rise order 4"'))
o.append(caption("딕셔너리를 넘기면 키로 골라서, 조건에 맞는 키만 남겨요.", 930))
W("f-dict", o, "15의 재고 딕셔너리를 filter에 넘겨 봐요. 딕셔너리를 for로 돌면 키가 나왔던 것처럼, filter에도 키가 하나씩 들어가요. 그래서 lambda의 m은 coffee, latte 같은 메뉴 이름이고, 재고는 stock[m]으로 꺼내요. 재고가 0보다 큰 coffee와 cake만 남았어요. 결과는 키만 담은 리스트라서 재고 숫자는 없어요. 재고까지 같이 담은 딕셔너리로 고르는 방법은 23에서 배워요." + REAL)

o = [sec("f-chain")] + head(EB4, "고른 다음 바꾸려면 filter 결과를 map에 넘겨요", K4)
o += cell({"id": "c-f4", "lines": ["big = list(filter(lambda p: p >= 5000, prices))", "print(big)", "print(list(map(lambda p: p * 9 // 10, big)))", "print(list(map(lambda p: p * 9 // 10, filter(lambda p: p >= 5000, prices))))"], "n": 4, "out": ["[5000, 6500]", "[4500, 5850]", "[4500, 5850]"]}, 96, 200, 1728, sel="c-f4")
o.append(hl(96, 200, 1728, 0, 3, "mark", 1, "두 번에 나눠 쓰기"))
o.append(hl(96, 200, 1728, 3, 1, "skip", 2, "한 줄에 겹쳐 쓰기"))
o.append(note_card(96, 560, 846, 300, "나눠 쓰면 읽기 쉬워요", "5000원 이상만 고르고, 그 결과를 10% 할인해요. 중간 결과 big을 찍어 확인할 수 있어요.", K4, ' data-build-in="rise order 3"'))
o.append(note_card(978, 560, 846, 300, "겹치면 안쪽부터 읽어요", "filter가 먼저, map이 나중이에요. 괄호가 겹쳐서 읽기 어려워요. 23에서 더 짧게 쓰는 법을 배워요.", GRAY, ' data-build-in="rise order 4"'))
o.append(caption("고르고 바꾸기를 같이 할 땐 filter로 고른 결과를 map에 넘겨요.", 930))
W("f-chain", o, "5000원 이상인 메뉴만 10% 할인해 봐요. 먼저 filter로 5000원 이상을 골라 big에 담아요. 그다음 big을 map에 넘겨서 9를 곱하고 10으로 몫 나누기해요. 마지막 줄처럼 filter를 map 안에 바로 넣어도 결과는 같아요. 다만 괄호가 겹쳐서 안쪽 filter부터 읽어야 해요. 처음에는 두 번에 나눠 쓰고 중간 결과를 찍어 보는 편이 좋아요. 같은 일을 한 줄로 더 읽기 쉽게 쓰는 방법은 23의 리스트 컴프리헨션이에요." + REAL)

# ---------- part 5 ----------
o = [sec("t-list")] + head(EB5, "map 결과에는 번호도 len도 못 써요", K5)
o += cell({"id": "c-t1", "lines": ["doubled = map(lambda x: x * 2, [1, 2, 3])", "print(doubled[0])"], "n": 1, "out": ["TypeError: 'map' object is not subscriptable"], "err": True}, 96, 200, 1728, sel="c-t1")
o += cell({"id": "c-t2", "lines": ["print(len(doubled))"], "n": 2, "out": ["TypeError: object of type 'map' has no len()"], "err": True}, 96, 380, 1728, attrs=' data-build-in="rise order 1"')
o.append(note_card(96, 540, 700, 330, "map object는 리스트가 아니에요", "값을 하나씩 꺼내 줄 뿐이라 [0]으로 꺼내거나 len으로 셀 수 없어요. filter도 같아요.", K5, ' data-build-in="rise order 2"'))
o += cell({"id": "c-t2f", "lines": ["doubled = list(map(lambda x: x * 2, [1, 2, 3]))", "print(doubled[0])", "print(len(doubled))"], "n": 3, "out": ["2", "3"]}, 840, 540, 984, attrs=' data-build-in="rise order 3"')
o.append(caption("번호로 꺼내거나 길이를 재려면 먼저 list()로 바꿔요.", 930))
W("t-list", o, "list를 빼먹으면 이런 오류를 만나요. doubled는 리스트가 아니라 map object예요. 그래서 doubled[0]처럼 번호로 꺼내면 subscriptable이 아니라는 TypeError가 나요. len으로 길이를 재도 map에는 len이 없다는 TypeError가 나요. filter 결과도 똑같아요. 오른쪽처럼 list로 감싸 리스트로 만들어 두면 번호와 len을 쓸 수 있어요. Traceback 위쪽 줄은 빼고 마지막 줄만 옮겼어요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p5", "오류와 함정"))

o = [sec("t-twice")] + head(EB5, "map 결과는 한 번 꺼내면 비어요", K5)
o += cell({"id": "c-t3", "lines": ["m = map(lambda p: p + 500, [4500, 5000])", "print(list(m))", "print(list(m))"], "n": 4, "out": ["[5000, 5500]", "[]"]}, 96, 200, 900, sel="c-t3")
o.append(hl(96, 200, 900, 2, 1, "err", 1, "남은 값이 없어요"))
for i, (lbl, items) in enumerate([("첫 번째 list(m)", ["5000", "5500"]), ("두 번째 list(m)", [])]):
    y = 480 + i * 150
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:96px;top:{y}px;width:900px;height:120px;background:{CARD};border:2px solid {LINE};border-radius:16px;padding:0 26px;display:flex;flex-direction:row;align-items:center;gap:22px">'
             + p(f"width:260px;flex:none;font-family:{MONO};font-size:24px;font-weight:700;color:{INK}", e(lbl)) + arrow(50, K3 if items else RED)
             + ("".join(chip(v, K3, K3BG, 28) for v in items) if items else chip("[]", RED, "#F8E6E6", 28) + p(f"font-size:24px;font-weight:700;color:{RED}", "다 꺼낸 뒤라 비었어요")) + '</div>')
o.append(note_card(1040, 200, 784, 250, "오류 없이 비어 있어요", "첫 list(m)이 값을 끝까지 꺼냈어요. 같은 m에서 다시 꺼낼 값이 없어요.", K5, ' data-build-in="rise order 3"'))
o += cell({"id": "c-t3f", "lines": ["m = map(lambda p: p + 500, [4500, 5000])", "ups = list(m)", "print(ups)", "print(ups)"], "n": 5, "out": ["[5000, 5500]", "[5000, 5500]"]}, 1040, 490, 784, attrs=' data-build-in="rise order 4"')
o.append(caption("두 번 이상 쓸 결과는 list()로 바꿔 변수에 담아 둬요.", 930))
W("t-twice", o, "오류는 안 나는데 더 헷갈리는 함정이에요. m에 map을 담고 list(m)을 두 번 찍었어요. 첫 번째는 [5000, 5500]인데 두 번째는 빈 리스트예요. map은 값을 하나씩 꺼내 주는 묶음이라서, 첫 list가 끝까지 꺼내고 나면 남은 값이 없어요. 결과를 두 번 이상 쓸 거라면 오른쪽처럼 list(m)을 한 번만 해서 ups에 담아 두고 ups를 써요. 리스트는 몇 번을 찍어도 그대로예요." + REAL)

o = [sec("t-paren")] + head(EB5, "넘길 함수에 괄호를 붙이면 바로 실행돼요", K5)
o += cell({"id": "c-t4", "lines": ["def add10(x):", "    return x + 10", "", "print(list(map(add10(), [1, 2, 3])))"], "n": 6, "out": ["TypeError: add10() missing 1 required positional argument: 'x'"], "err": True}, 96, 200, 1728, sel="c-t4")
o.append(hl(96, 200, 1728, 3, 1, "err", 1, "add10()"))
o.append(note_card(96, 480, 846, 300, "map보다 add10()이 먼저 불려요", "괄호를 붙이면 그 자리에서 x 없이 실행해서 오류가 나요.", K5, ' data-build-in="rise order 2"'))
o.append(note_card(978, 480, 846, 300, "missing 1 ... 'x'", "19에서 본 오류예요. 칸 x에 넣을 값이 없다는 뜻이에요.", GRAY, ' data-build-in="rise order 3"'))
o.append(f'<div data-build-in="rise order 4" style="position:absolute;left:96px;top:810px;width:1728px;height:90px;display:flex;flex-direction:row;align-items:center;gap:24px">'
         + mono("map(add10(), ...)", 32, RED, "#F8E6E6") + arrow(60, GR) + mono("map(add10, ...)", 32, GR, "#E6F4EC") + '</div>')
W("t-paren", o, "map에 넘길 함수에 습관처럼 괄호를 붙였어요. 그러면 map이 실행되기 전에 add10()이 그 자리에서 먼저 불려요. x에 넣을 값이 없으니 19에서 본 missing 1 required positional argument 오류가 나요. 함수를 넘길 때는 괄호 없이 이름만 적어요. 괄호는 map이 값을 하나씩 넣으면서 대신 붙여 줘요." + REAL)

o = [sec("t-return")] + head(EB5, "lambda 안에 return을 쓰면 SyntaxError가 나요", K5)
o += cell({"id": "c-t5", "lines": ["add10 = lambda x: return x + 10"], "n": 7, "out": ["SyntaxError: invalid syntax"], "err": True}, 96, 200, 1000, sel="c-t5")
o.append(hl(96, 200, 1000, 0, 1, "err", 1, "return"))
o.append(note_card(1150, 200, 674, 300, "콜론 뒤에는 값만 와요", "return은 값이 아니라 문장이에요. lambda는 콜론 뒤의 값을 알아서 돌려줘요.", K5, ' data-build-in="rise order 2"'))
o.append(side(1150, 530, 674, 220, "이렇게 고쳐요", ["add10 = lambda x: x + 10"], [], GR, "#E6F4EC", ' data-build-in="rise order 3"', 26, "return 빼기"))
o.append(note_card(96, 360, 1000, 260, "if 문, for 문, =도 못 넣어요", "lambda 몸통은 값 하나예요. 줄을 나눠 적어야 하는 일은 def로 만들어요.", OR, ' data-build-in="rise order 4"'))
o.append(note_card(96, 650, 1000, 200, "오류 끝 괄호는 뺐어요", "SyntaxError 끝의 (1234.py, line 1)은 셀마다 달라서 슬라이드에서 뺐어요.", GRAY, ' data-build-in="rise order 5"'))
o.append(caption("lambda는 콜론 뒤에 돌려줄 값 하나만 적어요.", 930))
W("t-return", o, "def에서 return을 쓰던 습관대로 lambda에도 return을 적으면 invalid syntax가 나요. lambda는 콜론 뒤에 적은 값을 알아서 돌려주고, 그 자리에는 값만 올 수 있어요. return, if 문, for 문, 변수에 넣는 =는 값이 아니라서 못 넣어요. return을 빼면 돼요. SyntaxError 메시지 끝에는 셀마다 다른 파일 이름과 줄 번호가 괄호로 붙어요. 슬라이드에서는 그 부분을 뺐어요." + REAL)

o = [sec("t-long")] + head(EB5, "lambda가 길어지면 def로 바꿔요", K5)
o.append(label("lambda 한 줄", 96, 196, GRAY, "", 1000, 26))
o += cell({"id": "c-t6", "lines": ['label = lambda p: "비쌈" if p >= 6000 else ("보통" if p >= 4500 else "쌈")', "print(label(6500), label(5000), label(3000))"], "n": 8, "out": ["비쌈 보통 쌈"]}, 96, 240, 1728, sel="c-t6")
o.append(label("def로 나눠 쓰기", 96, 430, GR, ' data-build-in="fade order 1"', 1000, 26))
o += cell({"id": "c-t7", "lines": ["def label(p):", "    if p >= 6000:", '        return "비쌈"', "    elif p >= 4500:", '        return "보통"', '    return "쌈"', "", "print(label(6500), label(5000), label(3000))"], "n": 9, "out": ["비쌈 보통 쌈"]}, 96, 474, 1000, attrs=' data-build-in="rise order 1"')
o.append(note_card(1150, 474, 674, 380, "결과는 같아요", "조건이 두 개를 넘으면 lambda는 한눈에 안 읽혀요. def로 나누고 map(label, prices)처럼 이름을 넘겨요.", K5, ' data-build-in="rise order 2"'))
W("t-long", o, "오류는 아니지만 자주 보는 함정이에요. 한 줄 if else를 괄호로 겹치면 lambda 한 줄에 조건 두 개를 넣을 수 있어요. 결과도 맞아요. 그런데 어디까지가 어느 조건인지 읽기 어려워요. 아래 def처럼 if와 elif로 나눠 쓰면 19에서 본 모양이라 금방 읽혀요. map에는 label처럼 이름만 넘기면 돼요. lambda는 한 줄로 바로 읽히는 짧은 일에만 써요." + REAL)

# ---------- part 6 ----------
o = [sec("x-raise")] + head(EB6, "메뉴 가격을 10% 올린 표를 만들어요", K6)
RAISE = ['menu = {"coffee": 4500, "latte": 5000, "cake": 6500}', "print(list(map(lambda m: menu[m] * 11 // 10, menu)))", "", "def line(m):", "    new = menu[m] * 11 // 10", '    return f"{m:<7}{menu[m]:>6,}원 → {new:>6,}원"', "", 'print("\\n".join(map(line, menu)))']
o += cell({"id": "c-x1", "lines": RAISE, "n": 1, "out": ["[4950, 5500, 7150]", "coffee  4,500원 →  4,950원", "latte   5,000원 →  5,500원", "cake    6,500원 →  7,150원"]}, 96, 186, 1200, sel="c-x1")
o.append(hl(96, 186, 1200, 1, 1, "mark", 1, "새 가격만"))
o.append(hl(96, 186, 1200, 3, 3, "mark", 2, "길면 def"))
o.append(hl(96, 186, 1200, 7, 1, "run", 3, "줄마다 이어 찍기"))
o.append(note_card(1340, 196, 484, 330, "m은 메뉴 이름", "딕셔너리를 넘겨서 키가 들어가요. 가격은 menu[m]이에요.", K6, ' data-build-in="rise order 4"'))
o.append(note_card(1340, 556, 484, 300, "\\n으로 이어요", "13의 join에 줄바꿈 \\n을 넣어 한 줄에 하나씩 찍어요.", GRAY, ' data-build-in="rise order 5"'))
o.append(caption("한 줄 계산은 lambda, 줄 만들기처럼 긴 일은 def로 만들어 map에 넘겨요.", 930))
W("x-raise", o, "메뉴 가격을 10% 올려 봐요. 11을 곱하고 10으로 몫 나누기하면 10% 오른 값이 돼요. 먼저 lambda로 새 가격만 리스트로 뽑았어요. 다음은 원래 가격과 새 가격을 나란히 찍는 줄을 만들어요. 줄 만드는 일은 길어서 line이라는 def로 만들었어요. map(line, menu)가 메뉴마다 한 줄씩 만들고, join이 줄바꿈 \\n으로 이어서 한 번에 찍어요. 13의 칸 맞추기와 천 단위 콤마를 그대로 썼어요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p6", "실습"))

o = [sec("x-soldout")] + head(EB6, "품절이 아니고 5000원 미만인 메뉴를 골라요", K6)
o += cell({"id": "c-x2", "lines": ['menu = {"coffee": 4500, "latte": 5000, "cake": 6500, "tea": 4000}', 'stock = {"coffee": 3, "latte": 0, "cake": 2, "tea": 5}', "print(list(filter(lambda m: stock[m] > 0, menu)))", "print(list(filter(lambda m: stock[m] > 0 and menu[m] < 5000, menu)))"], "n": 2, "out": ["['coffee', 'cake', 'tea']", "['coffee', 'tea']"]}, 96, 196, 1400, sel="c-x2")
o += table(96, 500, 1300, [("m", 200), ("stock[m] > 0", 280), ("menu[m] < 5000", 300), ("둘 다", 200)], [("coffee", "True", "True", "True"), ("latte", "False", "False", "False"), ("cake", "True", "False", "False"), ("tea", "True", "True", "True")], 1, K6, 64, hi=(0, 3))
o.append(note_card(1440, 500, 384, 330, "and로 이어요", "17에서 배운 and예요. 둘 다 True일 때만 남아요.", K6, ' data-build-in="rise order 5"'))
o.append(caption("조건이 두 개면 lambda 안에서 and로 이어요.", 930))
W("x-soldout", o, "메뉴판과 재고 딕셔너리를 같이 써요. 먼저 재고가 남은 메뉴만 골랐어요. latte가 빠졌어요. 다음에는 재고가 있고 5000원 미만인 메뉴를 골라요. 조건 두 개를 17에서 배운 and로 이어요. 표처럼 두 조건이 모두 True인 coffee와 tea만 남아요. latte는 가격이 5000원이라 미만이 아니고 재고도 없어요. 조건이 더 늘어나면 앞에서 본 것처럼 def로 만들어 넘겨요." + REAL)

o = [sec("x-orders")] + head(EB6, "튜플로 적은 주문 기록을 고르고 꺼내요", K6)
ORD = ['orders = [("kim", "latte", 2), ("lee", "cake", 1), ("park", "coffee", 3), ("kim", "tea", 1)]', "many = list(filter(lambda o: o[2] >= 2, orders))", "print(many)", "print(list(map(lambda o: o[0], many)))", "print(sum(map(lambda o: o[2], orders)))"]
o += cell({"id": "c-x3", "lines": ORD, "n": 3, "out": ["[('kim', 'latte', 2), ('park', 'coffee', 3)]", "['kim', 'park']", "7"]}, 96, 196, 1728, sel="c-x3")
o.append(callout(96, 580, 560, 170, "o[2] >= 2", "2잔 이상 산 주문만 골라요", K4, 1, 26))
o.append(callout(680, 580, 560, 170, "o[0]", "고른 주문에서 이름만 꺼내요", K3, 2, 26))
o.append(callout(1264, 580, 560, 170, "sum(map(...))", "잔 수만 꺼내 바로 더해요", K6, 3, 26))
o.append(caption("튜플 하나가 lambda의 o 칸에 들어가고, 번호로 칸을 꺼내요.", 930))
W("x-orders", o, "13에서 배운 튜플로 주문 기록을 적었어요. 튜플 하나가 이름, 메뉴, 잔 수예요. filter에 넘기면 튜플 하나씩 o 칸에 들어가요. o[2]가 잔 수라서 2잔 이상인 주문만 골랐어요. 그 결과를 map에 넘겨 o[0], 곧 이름만 꺼냈어요. 마지막 줄은 모든 주문의 잔 수를 map으로 꺼내 sum에 바로 넘겼어요. sum은 list로 바꾸지 않아도 값을 하나씩 꺼내 더해요. 모두 7잔이에요." + REAL)

# ---------- wrap up ----------
trouble([("<map object at 0x...>가 나와요", "map 결과를 그대로 찍었어요", "list(map(...))"),
         ("TypeError: 'map' object is not subscriptable", "map 결과에 번호를 붙였어요", "list()로 바꾸기"),
         ("TypeError: object of type 'map' has no len()", "map 결과에 len을 썼어요", "list()로 바꾸기"),
         ("두 번째 list(m)이 []예요", "map은 한 번 꺼내면 비어요", "리스트로 담아 두기"),
         ("TypeError: add10() missing 1 required ...", "넘길 함수에 괄호를 붙였어요", "map(add10, xs)"),
         ("SyntaxError: invalid syntax", "lambda 안에 return을 적었어요", "lambda x: x + 10"),
         ("lambda가 한눈에 안 읽혀요", "조건이 여러 개예요", "def로 만들어 넘기기")],
        "결과가 이상하면 list()로 바꿔 중간 결과를 찍어 봐요.",
        "이번 챕터에서 자주 만나는 일을 모았어요. 1번부터 4번은 map과 filter 결과가 리스트가 아니라서 생겨요. list로 바꿔 담으면 대부분 풀려요. 5번은 함수를 넘길 때 괄호를 붙인 경우예요. 6번과 7번은 lambda에 너무 많은 걸 넣으려다 생겨요. 고르고 바꾸기를 겹쳐 쓸 때는 중간 결과를 list로 찍어 보면 어디서 틀렸는지 보여요.")

cheatsheet([("lambda x: x + 10", "이름 없는 한 줄 함수", K2), ("plus = add10", "괄호 없이 함수 담기", K2), ("map(f, xs)", "값마다 f를 써요", K3), ("list(map(...))", "리스트로 모으기", K3),
            ("map(str, xs)", "있는 함수는 이름만", K3), ("filter(f, xs)", "True인 값만 남겨요", K4), ("filter(f, d)", "딕셔너리는 키가 들어가요", K4), ("def label(p):", "길어지면 def로 넘기기", K6)],
           ["함수를 넘길 땐 괄호 없이 이름만 적어요", "다음 챕터: sorted, max, min의 key에 lambda 넣기"],
           "이번 챕터에서 쓴 모양을 한 장에 모았어요. 함수는 값이라서 담고 넘길 수 있어요. lambda는 이름 없이 값 하나를 돌려주는 짧은 함수예요. map은 값마다 함수를 써서 결과를 모으고, filter는 True를 받은 값만 남겨요. 결과를 리스트로 보려면 list로 감싸요. 22에서는 sorted, max, min에 lambda를 넘겨서 무엇을 기준으로 줄 세울지 정해요.")

finish([("Lightbulb", K1, "왜 필요한가", "되풀이하는 for와 append, map과 filter 그림, 가장 짧은 map", "l-why", "l-min"),
        ("Code", K2, "함수를 값처럼, lambda", "함수 담기와 넘기기, def와 lambda 비교, 바로 넘기기", "v-value", "d-more"),
        ("Settings", K3, "map", "for 네 줄을 한 줄로, 하나씩 넣는 그림, map object, str과 len 넘기기", "m-three", "m-builtin"),
        ("Search", K4, "filter", "골라 담기를 한 줄로, True만 남는 그림, 딕셔너리 키, map과 이어 쓰기", "f-for", "f-chain"),
        ("Warning", K5, "오류와 함정", "번호와 len, 한 번만 꺼내지는 map, 괄호, return, 긴 lambda", "t-list", "t-long"),
        ("Star", K6, "실습", "10% 인상 가격표, 품절 아닌 메뉴, 튜플 주문 기록", "x-raise", "x-orders")],
       "여섯 파트로 나눴어요. 1파트는 for와 append를 되풀이하는 장면과 map, filter 그림이에요. 2파트는 함수를 값처럼 담고 넘기는 법과 lambda예요. 3파트와 4파트가 이번 챕터의 중심인 map과 filter예요. 5파트는 자주 나는 오류, 6파트는 카페 실습이에요. 파트마다 새 커널에서 위에서부터 차례로 실행해요.",
       "함수 3 (lambda, map, filter)")
