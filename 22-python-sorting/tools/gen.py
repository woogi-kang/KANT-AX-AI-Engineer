"""Generates every slide of the sorting deck (22, sorted, sort, max, min and key) and slides/deck.json.

Story: keeps writing in basics.ipynb from chapters 12-21. Starts from max(sales) returning 'tea' instead of the best
seller, draws key as a function that makes the values to compare, then sorted next to sort (and the None trap), reverse,
how strings compare, key=len, str.lower and int, tuples compared slot by slot, lambda keys and two-part keys, sorting a
dictionary by key, value or item, max and min with key and default, and sum, len and slicing. Part 5 collects the usual
errors, and part 6 builds a sales ranking, price board, menu board and score sheet.
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
EB2 = "2. sorted, sort, key"
EB3 = "3. 튜플과 딕셔너리 정렬"
EB4 = "4. max와 min"
EB5 = "5. 오류와 함정"
EB6 = "6. 실습"
SALES = 'sales = {"coffee": 12, "latte": 30, "cake": 8, "tea": 15}'
SALES_P = [("coffee", "12"), ("latte", "30"), ("cake", "8"), ("tea", "15")]


# ---------- cover ----------
cover([('sales = {"coffee": 12, "latte": 30,', "#E6E9EF"), ('         "cake": 8, "tea": 15}', "#E6E9EF"), ("", "#E6E9EF"),
       ("sorted(sales, key=sales.get, reverse=True)", "#8FD8DE"), ("# ['latte', 'tea', 'coffee', 'cake']", "#9AA1AE"), ("", "#E6E9EF"),
       ("max(sales, key=sales.get)", "#E3B877"), ("# 'latte'", "#9AA1AE")],
      "정렬과<br>sorted, max, min", "무엇을 기준으로 줄 세우고<br>가장 큰 값을 고를지 key로 정하기",
      "13에서 sorted와 sort, max와 min을 써 봤어요. 그때는 숫자는 작은 순, 글자는 abc 순으로만 줄 세웠어요. 이번에는 key로 기준을 직접 정해요. 길이순, 가격순, 판매량 많은 순처럼요. 21에서 배운 lambda를 key에 넣는 게 이번 챕터의 중심이에요. 튜플 리스트와 딕셔너리도 원하는 기준으로 줄 세워요.", h1size=76)

ready([("리스트, 튜플, sort, sorted, max, min", "13"), ("딕셔너리 get, items()", "15"), ("sorted(..., reverse=True)", "16, 20"), ("for, enumerate()", "13, 18"), ("lambda, map, filter", "21")], "21",
      "09에서 만든 hello-uv 폴더를 VS Code로 열고, 12부터 쓰던 basics.ipynb를 다시 열어요. 13의 sorted, sort, max, min과 튜플, 15의 get과 items, 16과 20의 reverse=True를 다시 써요. 21의 lambda를 key에 넣는 게 이번 챕터의 중심이라 21을 먼저 보고 오면 좋아요. 슬라이드의 출력은 tools/demo.sh가 hello-uv 커널에서 같은 셀을 실제로 실행한 결과예요. 셀 번호는 파트마다 [1]부터 다시 셌어요.")

# ---------- part 1 ----------
o = [sec("s-why")] + head(EB1, "가장 많이 팔린 메뉴를 물었는데 tea가 나와요", K1)
o += cell({"id": "c-why", "lines": [SALES, "print(sorted(sales))", "print(max(sales))"], "n": 1, "out": ["['cake', 'coffee', 'latte', 'tea']", "tea"]}, 96, 200, 1100, sel="c-why")
o.append(hl(96, 200, 1100, 2, 1, "err", 1, "기대한 건 latte"))
o.append(lockers(SALES_P, 96, 480, 250, 170, K1, K1BG, hi=(1,), attrs=' data-build-in="rise order 2"'))
o.append(p(f"position:absolute;left:96px;top:670px;width:1100px;font-size:26px;font-weight:700;color:{K1}", "판매량은 latte가 30잔으로 가장 많아요", ' data-build-in="fade order 2"'))
o.append(note_card(1240, 200, 584, 320, "키끼리 비교했어요", "sorted와 max는 딕셔너리의 키만 봐요. 글자는 abc 순이라 tea가 가장 뒤, 곧 가장 커요.", K1, ' data-build-in="rise order 3"'))
o.append(note_card(1240, 550, 584, 310, "기준을 바꾸고 싶어요", "이름 말고 판매량으로 비교하라고 알려 주는 방법이 key예요.", OR, ' data-build-in="rise order 4"'))
o.append(caption("sorted와 max는 따로 말하지 않으면 값 자체를 비교해요.", 930))
W("s-why", o, "메뉴별 판매량을 딕셔너리에 담았어요. 가장 많이 팔린 메뉴를 알고 싶어서 max(sales)를 쳤더니 tea가 나와요. 판매량은 latte가 30잔으로 가장 많은데요. sorted와 max는 딕셔너리를 받으면 키만 봐요. 키가 글자라서 abc 순으로 비교했고, tea가 가장 뒤라서 가장 큰 값이 됐어요. 이름이 아니라 판매량으로 비교하라고 알려 줘야 해요. 그 방법이 key예요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p1", "왜 필요한가"))

o = [sec("s-big")] + head(EB1, "key는 비교할 값을 따로 만들어 줘요", K1)
o.append(label("원래 값", 96, 206, GRAY, ' data-build-in="fade order 1"', 300, 24))
o += pipe(96, 250, ['"latte"', '"tea"', '"coffee"'], "key=len", ["5", "3", "6"], K1, K1BG, 1, 200)
o.append(label("비교할 값", 96, 590, K1, ' data-build-in="fade order 3"', 300, 24))
o.append(row(96, 630, 1120, 120, small("작은 것부터", K1, 26) + arrow(60, K1) + slots(["3", "5", "6"], 0, 0, 110, 80, top_lbl=False, fs=28, color=K1, bg=K1BG).replace("position:absolute;left:0px;top:0px;", "")
             + arrow(60, K1) + slots(['"tea"', '"latte"', '"coffee"'], 0, 0, 160, 80, top_lbl=False, fs=26, color=K1, bg=K1BG, hi=(0, 1, 2)).replace("position:absolute;left:0px;top:0px;", ""), 4))
o.append(note_card(1240, 250, 584, 300, "key는 함수예요", "값마다 key 함수를 써서 비교할 값을 만들어요. 21의 map처럼 하나씩 넣어요.", K1, ' data-build-in="rise order 5"'))
o.append(note_card(1240, 580, 584, 280, "결과는 원래 값", "줄은 비교할 값으로 세우고, 결과에는 원래 값이 그대로 들어가요.", GR, ' data-build-in="rise order 6"'))
o.append(caption("key=함수를 넣으면 sorted, max, min이 그 함수의 결과로 비교해요.", 930))
W("s-big", o, "key가 하는 일을 그림으로 봐요. 이름 세 개를 길이순으로 세우고 싶어요. key=len을 주면 sorted가 값마다 len을 써서 비교할 값 5, 3, 6을 만들어요. 21의 map이 값을 하나씩 함수에 넣던 것과 같아요. 그다음 비교할 값이 작은 것부터 줄을 세워요. 결과에는 숫자가 아니라 원래 이름이 들어가요. tea, latte, coffee 순이에요. max와 min도 key를 받아서 같은 방식으로 비교해요.")

o = [sec("s-min")] + head(EB1, "가장 짧은 key: 이름을 길이순으로", K1)
o += cell({"id": "c-min", "lines": ['names = ["latte", "tea", "coffee"]', "print(sorted(names))", "print(sorted(names, key=len))", "print(max(sales, key=sales.get))"], "n": 2, "out": ["['coffee', 'latte', 'tea']", "['tea', 'latte', 'coffee']", "latte"]}, 96, 200, 1100, sel="c-min")
o.append(hl(96, 200, 1100, 2, 1, "mark", 1, "길이로 비교"))
o.append(hl(96, 200, 1100, 3, 1, "run", 2, "판매량으로 비교"))
o.append(callout(1240, 200, 584, 150, "key=len", "len 결과로 비교해요", K1, 1, 26))
o.append(callout(1240, 380, 584, 150, "key=sales.get", "판매량으로 비교해요", GR, 2, 26))
o.append(note_card(96, 560, 1100, 300, "괄호 없이 이름만 넣어요", "21에서 map(len, names)처럼 함수를 넘긴 것과 같아요. sales.get도 키를 넣으면 값을 주는 함수예요. 3파트에서 다시 봐요.", K1, ' data-build-in="rise order 3"'))
o.append(note_card(1240, 560, 584, 300, "이제 latte", "앞 장에서 tea가 나왔던 max가 latte를 골라요.", OR, ' data-build-in="rise order 4"'))
o.append(caption("key= 뒤에 함수를 넣으면 무엇으로 비교할지 바뀌어요.", 930))
W("s-min", o, "가장 짧은 예예요. 그냥 sorted는 abc 순이라 coffee가 먼저예요. key=len을 주면 길이 3인 tea, 5인 latte, 6인 coffee 순이 돼요. 마지막 줄은 앞 장의 문제를 푼 거예요. key=sales.get을 주면 키마다 sales.get으로 판매량을 꺼내 비교해서 latte를 골라요. key에는 21처럼 괄호 없이 함수 이름만 넣어요. sales.get은 3파트에서 자세히 봐요. sales는 앞 셀에서 만들었어요." + REAL)

# ---------- part 2 ----------
o = [sec("o-two")] + head(EB2, "sorted는 새 리스트, sort는 원본을 바꿔요", K2)
o += cell({"id": "c-o1", "lines": ["prices = [6500, 4500, 5000]", "a = sorted(prices)", "print(a)", "print(prices)", "prices.sort()", "print(prices)"], "n": 1, "out": ["[4500, 5000, 6500]", "[6500, 4500, 5000]", "[4500, 5000, 6500]"]}, 96, 200, 900, sel="c-o1")
o.append(hl(96, 200, 900, 1, 1, "mark", 1, "새 리스트 a"))
o.append(hl(96, 200, 900, 4, 1, "run", 2, "prices가 바뀌어요"))
o.append(callout(984, 200, 840, 150, "sorted(prices)", "함수예요. 줄 세운 새 리스트를 주고 prices는 그대로 둬요", K2, 1, 26))
o.append(callout(984, 380, 840, 150, "prices.sort()", "리스트의 메서드예요. prices 자체를 줄 세우고 돌려주는 값이 없어요", GR, 2, 26))
o.append(note_card(984, 560, 840, 300, "원본이 필요하면 sorted", "가격표를 적은 순서도 나중에 필요하면 sorted를 써요. 줄 세운 결과만 있으면 되면 sort도 괜찮아요.", OR, ' data-build-in="rise order 3"'))
o.append(caption("원본을 지키려면 sorted, 원본을 바꿔도 되면 sort를 써요.", 930))
W("o-two", o, "13에서 본 두 가지를 다시 짚어요. sorted(prices)는 함수예요. 줄 세운 새 리스트를 돌려주고 prices는 그대로 둬요. 그래서 a는 줄 섰지만 prices를 찍으면 원래 순서예요. prices.sort()는 리스트의 메서드예요. prices 자체를 줄 세워요. 다음 장에서 보겠지만 sort는 돌려주는 값이 없어요. 원래 순서가 나중에도 필요하면 sorted, 필요 없으면 sort를 써요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p2", "sorted, sort, key"))

o = [sec("o-none")] + head(EB2, "prices = prices.sort()를 하면 None만 남아요", K2)
o += cell({"id": "c-o2", "lines": ["prices = [6500, 4500, 5000]", "prices = prices.sort()", "print(prices)"], "n": 2, "out": ["None"]}, 96, 200, 900, sel="c-o2")
o.append(hl(96, 200, 900, 1, 1, "err", 1, "돌려준 값은 None"))
steps_ = [("1", "prices.sort()", "prices를 줄 세워요"), ("2", "돌려준 값", "None"), ("3", "prices = None", "줄 세운 리스트를 잃어요")]
o += steps(steps_, 984, 200, 840, 2, K5, 96, (40, 300))
o.append(note_card(96, 420, 840, 300, "19의 return 없는 함수와 같아요", "sort는 원본을 바꾸기만 하고 값을 돌려주지 않아요. 돌려받은 None을 prices에 넣었어요.", K5, ' data-build-in="rise order 5"'))
o.append(side(984, 520, 840, 300, "이렇게 고쳐요", ["prices.sort()", "", "prices = sorted(prices)"], [], GR, "#E6F4EC", ' data-build-in="rise order 6"', 26, "둘 중 하나"))
o.append(caption("sort는 그 줄 하나로 쓰고, 결과를 담으려면 sorted를 써요.", 930))
W("o-none", o, "자주 하는 실수예요. 줄 세운 결과를 다시 prices에 담으려고 prices = prices.sort()라고 적었어요. 찍어 보면 None이에요. sort는 prices를 줄 세우기만 하고 돌려주는 값이 없어요. 19에서 return이 없는 함수가 None을 돌려준 것과 같아요. 그 None을 prices에 넣어서 줄 세운 리스트를 잃었어요. sort는 prices.sort()처럼 한 줄로만 쓰고, 결과를 변수에 담고 싶으면 sorted를 써요." + REAL)

o = [sec("o-rev")] + head(EB2, "큰 것부터 세우려면 reverse=True", K2)
o += cell({"id": "c-o3", "lines": ["prices = [6500, 4500, 5000]", "print(sorted(prices, reverse=True))", "prices.sort(reverse=True)", "print(prices)"], "n": 3, "out": ["[6500, 5000, 4500]", "[6500, 5000, 4500]"]}, 96, 200, 1000, sel="c-o3")
o.append(row(96, 470, 1000, 110, slots(["4500", "5000", "6500"], 0, 0, 150, 84, top_lbl=False, fs=28, color=GRAY, bg="#F1F0EC").replace("position:absolute;left:0px;top:0px;", "") + small("기본", GRAY, 24), 1))
o.append(row(96, 600, 1000, 110, slots(["6500", "5000", "4500"], 0, 0, 150, 84, top_lbl=False, fs=28, color=K2, bg=K2BG, hi=(0, 1, 2)).replace("position:absolute;left:0px;top:0px;", "") + small("reverse=True", K2, 24), 2))
o.append(note_card(1150, 200, 674, 300, "20에서 본 키워드 인자", "reverse의 기본값이 False라서 빼면 작은 것부터예요. True를 넣으면 거꾸로예요.", K2, ' data-build-in="rise order 3"'))
o.append(note_card(1150, 530, 674, 330, "sort에도 똑같이", "prices.sort(reverse=True)처럼 sort도 reverse와 key를 받아요.", GR, ' data-build-in="rise order 4"'))
o.append(caption("reverse=True는 큰 것부터, 글자는 z부터 세워요.", 930))
W("o-rev", o, "16과 20에서 본 reverse=True예요. 기본값이 False라서 빼면 작은 것부터 세우고, True를 넣으면 거꾸로 큰 것부터 세워요. 글자라면 z 쪽부터예요. 20에서 배운 대로 칸 이름을 붙여 넣는 키워드 인자예요. sort도 같은 키워드 인자를 받아서 prices.sort(reverse=True)로 원본을 큰 것부터 세워요. 뒤에 나올 key도 sorted와 sort 둘 다 받아요." + REAL)

o = [sec("o-what")] + head(EB2, "글자는 앞 글자부터 하나씩 비교해요", K2)
o += cell({"id": "c-o4", "lines": ['print(sorted(["Latte", "cake", "Tea", "coffee"]))', 'print(sorted(["라떼", "커피", "녹차"]))', 'print(sorted(["10", "9", "100"]))'], "n": 4, "out": ["['Latte', 'Tea', 'cake', 'coffee']", "['녹차', '라떼', '커피']", "['10', '100', '9']"]}, 96, 200, 1100, sel="c-o4")
o.append(row_card(96, 520, 1728, 100, '"Tea" < "cake"', "True", "대문자가 소문자보다 먼저예요. 대문자 A~Z 뒤에 소문자 a~z가 와요", 1, K2, K2BG, 420))
o.append(row_card(96, 640, 1728, 100, '"녹차" < "라떼"', "True", "한글은 가나다 순이에요", 2, K2, K2BG, 420))
o.append(row_card(96, 760, 1728, 100, '"100" < "9"', "True", "첫 글자 1과 9를 먼저 비교해요. 글자로 담긴 숫자는 크기순이 아니에요", 3, K5, K5BG, 420))
o.append(caption("글자는 사전처럼 첫 글자부터 비교해요. 숫자 크기로 세우려면 숫자로 바꿔요.", 930))
W("o-what", o, "글자를 줄 세울 때 알아 둘 규칙이에요. 글자는 사전처럼 첫 글자부터 하나씩 비교해요. 첫째 줄에서 Latte와 Tea가 cake보다 앞에 왔어요. 파이썬은 대문자를 소문자보다 앞에 둬요. 한글은 가나다 순이에요. 셋째 줄은 숫자를 글자로 담았어요. 첫 글자 1과 9를 비교해서 10과 100이 9보다 앞에 와요. 이렇게 크기순이 아닌 결과는 다음 두 장의 key로 고쳐요." + REAL)

o = [sec("k-len")] + head(EB2, "key=len: 길이를 재서 비교해요", K2)
o += cell({"id": "c-k1", "lines": ['names = ["latte", "tea", "coffee", "mocha"]', "print(list(map(len, names)))", "print(sorted(names, key=len))", "print(sorted(names, key=len, reverse=True))"], "n": 5, "out": ["[5, 3, 6, 5]", "['tea', 'latte', 'mocha', 'coffee']", "['coffee', 'latte', 'mocha', 'tea']"]}, 96, 200, 1100, sel="c-k1")
o.append(label("names", 96, 540, GRAY, ' data-build-in="fade order 1"', 300, 24))
o.append(slots(['"latte"', '"tea"', '"coffee"', '"mocha"'], 96, 580, 200, 80, top_lbl=False, fs=26, color=GRAY, bg="#F1F0EC", attrs=' data-build-in="fade order 1"'))
o.append(label("len", 96, 680, K2, ' data-build-in="fade order 2"', 300, 24))
o.append(slots(["5", "3", "6", "5"], 96, 720, 200, 80, top_lbl=False, fs=28, color=K2, bg=K2BG, hi=(0, 3), attrs=' data-build-in="fade order 2"'))
o.append(note_card(1240, 200, 584, 300, "21의 map(len, …)과 같은 값", "sorted가 안에서 이 길이 값으로 비교해요.", K2, ' data-build-in="rise order 3"'))
o.append(note_card(1240, 530, 584, 330, "길이가 같으면 원래 순서", "latte와 mocha는 둘 다 5예요. 처음 적은 순서대로 latte가 먼저 남아요.", OR, ' data-build-in="rise order 4"'))
o.append(caption("key=len은 len 결과로, 같으면 원래 순서를 지켜 줄 세워요.", 930))
W("k-len", o, "key=len을 자세히 봐요. 21에서 map(len, names)로 뽑은 길이 5, 3, 6, 5가 sorted가 안에서 쓰는 비교 값이에요. 작은 것부터 세우면 tea, latte와 mocha, coffee 순이에요. latte와 mocha는 길이가 같아요. 이럴 땐 처음 적은 순서를 그대로 지켜서 latte가 먼저 와요. reverse=True를 같이 주면 긴 이름부터 세워요. 길이가 같은 둘의 순서는 그대로예요." + REAL)

o = [sec("k-lower")] + head(EB2, "key=str.lower, key=int로 비교 방법을 바꿔요", K2)
o += cell({"id": "c-k2", "lines": ['print("Latte".lower())', 'print(sorted(["Latte", "cake", "Tea", "coffee"], key=str.lower))', 'print(sorted(["10", "9", "100"], key=int))'], "n": 6, "out": ["latte", "['cake', 'coffee', 'Latte', 'Tea']", "['9', '10', '100']"]}, 96, 200, 1300, sel="c-k2")
o.append(callout(96, 490, 846, 150, '"Latte".lower()', "글자를 모두 소문자로 바꾼 새 글자를 줘요", K2, 1, 26))
o.append(callout(978, 490, 846, 150, "key=str.lower", "소문자로 바꿔서 비교해요. 결과는 원래 글자", K2, 2, 26))
o.append(callout(96, 670, 846, 150, "key=int", "숫자로 바꿔서 크기순으로 비교해요", OR, 3, 26))
o.append(note_card(978, 670, 846, 180, "str.lower는 이름만", "lower는 글자(str)의 메서드라서 str.lower로 적어 넘겨요.", GRAY, ' data-build-in="rise order 4"'))
o.append(caption("결과는 그대로 두고 비교할 때만 바꾸고 싶으면 key에 바꾸는 함수를 넣어요.", 930))
W("k-lower", o, "앞 장에서 이상했던 두 결과를 key로 고쳐요. lower는 이번에 처음 보는 글자 메서드예요. 글자를 모두 소문자로 바꾼 새 글자를 줘요. key=str.lower를 주면 소문자로 바꾼 값끼리 비교해서 대소문자 상관없이 abc 순이 돼요. 결과에는 Latte, Tea처럼 원래 글자가 그대로 들어가요. 글자로 담긴 숫자는 12에서 배운 int를 key로 주면 숫자 크기순이 돼요. str.lower는 글자 메서드 lower를 함수로 넘기는 이름이에요. 괄호는 붙이지 않아요." + REAL)

# ---------- part 3 ----------
o = [sec("p-tuple")] + head(EB3, "튜플은 앞 칸부터 비교해요", K3)
o += cell({"id": "c-p1", "lines": ['items = [("latte", 5000), ("cake", 6500), ("coffee", 4500), ("cake", 6000)]', "print(sorted(items))"], "n": 1, "out": ["[('cake', 6000), ('cake', 6500), ('coffee', 4500), ('latte', 5000)]"]}, 96, 200, 1728, sel="c-p1")
o.append(row(96, 420, 1100, 100, tup(['"cake"', "6000"], hi=(1,)) + small("<", K3, 34) + tup(['"cake"', "6500"], hi=(1,)), 1))
o.append(p(f"position:absolute;left:96px;top:530px;width:1100px;font-size:24px;font-weight:700;color:{SUB}", "첫 칸이 같아서 둘째 칸 6000과 6500을 비교해요", ' data-build-in="fade order 1"'))
o.append(row(96, 610, 1100, 100, tup(['"coffee"', "4500"], hi=(0,)) + small("<", K3, 34) + tup(['"latte"', "5000"], hi=(0,)), 2))
o.append(p(f"position:absolute;left:96px;top:720px;width:1100px;font-size:24px;font-weight:700;color:{SUB}", "첫 칸이 다르면 둘째 칸은 보지 않아요", ' data-build-in="fade order 2"'))
o.append(note_card(1240, 420, 584, 440, "글자 비교와 같은 방식", "글자가 첫 글자부터 비교했듯이 튜플은 첫 칸부터 비교해요. 그래서 그냥 sorted하면 이름순이에요.", K3, ' data-build-in="rise order 3"'))
o.append(caption("튜플 리스트를 그냥 줄 세우면 첫 칸 기준, 같으면 둘째 칸 기준이에요.", 930))
W("p-tuple", o, "13에서 배운 튜플로 메뉴와 가격을 묶었어요. 튜플 리스트를 그냥 sorted하면 첫 칸인 이름 순으로 서요. cake가 둘이라 첫 칸이 같아요. 그럴 때는 둘째 칸 6000과 6500을 비교해서 6000짜리가 먼저예요. coffee와 latte는 첫 칸이 달라서 둘째 칸은 보지 않아요. 앞 파트에서 글자를 첫 글자부터 비교한 것과 같은 방식이에요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p3", "튜플과 딕셔너리 정렬"))

o = [sec("p-index")] + head(EB3, "key=lambda m: m[1]로 둘째 칸 기준", K3)
o += cell({"id": "c-p2", "lines": ['items = [("latte", 5000), ("cake", 6500), ("coffee", 4500)]', "print(sorted(items, key=lambda m: m[1]))", "print(sorted(items, key=lambda m: m[1], reverse=True))"], "n": 2, "out": ["[('coffee', 4500), ('latte', 5000), ('cake', 6500)]", "[('cake', 6500), ('latte', 5000), ('coffee', 4500)]"]}, 96, 200, 1300, sel="c-p2")
for i, (n_, v) in enumerate([('"latte"', "5000"), ('"cake"', "6500"), ('"coffee"', "4500")]):
    o.append(row(96, 500 + i * 110, 1100, 96, tup([n_, v], hi=(1,), dim=(0,)) + arrow(50, K3) + chip(v, K3, K3BG, 28), 1))
o.append(note_card(1240, 500, 584, 360, "m은 튜플 하나", "lambda의 m에 튜플이 하나씩 들어가요. m[1]이 가격이라 가격으로 비교해요.", K3, ' data-build-in="rise order 2"'))
o.append(caption("원하는 칸으로 세우려면 그 칸을 꺼내는 lambda를 key에 넣어요.", 930))
W("p-index", o, "가격순으로 세우고 싶어요. 이번에는 이미 있는 함수가 없어서 21의 lambda로 만들어요. key=lambda m: m[1]은 튜플 하나를 m으로 받아 둘째 칸, 곧 가격을 돌려줘요. sorted는 이 가격으로 비교해서 4500, 5000, 6500 순으로 세워요. 결과에는 튜플이 그대로 들어가요. reverse=True를 같이 주면 비싼 것부터예요. 이름은 m[0]이라 key=lambda m: m[0]이면 그냥 sorted와 같아요." + REAL)

o = [sec("p-multi")] + head(EB3, "판매량 많은 순, 같으면 이름순으로 세워요", K3)
MUL = ['sales = [("latte", 30), ("cake", 8), ("coffee", 30), ("tea", 15)]', "print(sorted(sales, key=lambda m: m[1], reverse=True))", "print(list(map(lambda m: (-m[1], m[0]), sales)))", "print(sorted(sales, key=lambda m: (-m[1], m[0])))"]
o += cell({"id": "c-p3", "lines": MUL, "n": 3, "out": ["[('latte', 30), ('coffee', 30), ('tea', 15), ('cake', 8)]", "[(-30, 'latte'), (-8, 'cake'), (-30, 'coffee'), (-15, 'tea')]", "[('coffee', 30), ('latte', 30), ('tea', 15), ('cake', 8)]"]}, 96, 196, 1300, sel="c-p3")
o.append(hl(96, 196, 1300, 1, 1, "skip", 1, "30끼리는 원래 순서"))
o.append(hl(96, 196, 1300, 3, 1, "run", 2, "같으면 이름순"))
o += table(96, 560, 1300, [("튜플", 300), ("key 결과", 300), ("읽는 법", 560)],
           [('("latte", 30)', "(-30, 'latte')", "-30이 가장 작아서 앞으로"), ('("coffee", 30)', "(-30, 'coffee')", "-30이 같아서 이름으로, coffee가 먼저"), ('("tea", 15)', "(-15, 'tea')", "다음은 -15"), ('("cake", 8)', "(-8, 'cake')", "-8이 가장 커서 맨 뒤")], 3, K3, 56, hi=(0, 1))
o.append(note_card(1440, 196, 384, 680, "빼기로 뒤집기", "숫자 앞에 -를 붙이면 큰 수가 작은 수가 돼요. 판매량은 많은 순, 이름은 abc 순으로 한 번에 세울 수 있어요.", K3, ' data-build-in="rise order 7"'))
W("p-multi", o, "판매량이 같은 메뉴가 있을 때예요. reverse=True로 많은 순을 세우면 30잔인 latte와 coffee는 원래 순서대로 남아요. 같은 판매량끼리는 이름순으로 세우고 싶어요. key가 튜플을 돌려주면 앞 장처럼 첫 칸부터 비교해요. 첫 칸에 -m[1], 둘째 칸에 m[0]을 넣었어요. 판매량에 -를 붙이면 30이 -30이 돼서 작은 것부터 세워도 많이 팔린 메뉴가 앞에 와요. 첫 칸이 -30으로 같으면 둘째 칸 이름으로 비교해서 coffee가 먼저예요. reverse는 쓰지 않았어요." + REAL)

o = [sec("p-dict")] + head(EB3, "딕셔너리는 키, 값, 짝 중 무엇을 줄 세울지 골라요", K3)
o += cell({"id": "c-p4", "lines": [SALES, "print(sorted(sales))", "print(sorted(sales.values()))", "print(sorted(sales.items()))"], "n": 4, "out": ["['cake', 'coffee', 'latte', 'tea']", "[8, 12, 15, 30]", "[('cake', 8), ('coffee', 12), ('latte', 30), ('tea', 15)]"]}, 96, 196, 1300, sel="c-p4")
o.append(row_card(96, 540, 1728, 100, "sorted(sales)", "키만", "이름이 abc 순으로. 판매량은 빠져요", 1, K3, K3BG, 440))
o.append(row_card(96, 660, 1728, 100, "sorted(sales.values())", "값만", "판매량이 작은 순으로. 어느 메뉴인지 빠져요", 2, K3, K3BG, 440))
o.append(row_card(96, 780, 1728, 100, "sorted(sales.items())", "(키, 값)", "튜플 리스트가 돼요. 첫 칸인 이름 순이에요", 3, K3, K3BG, 440))
W("p-dict", o, "15의 판매량 딕셔너리로 돌아와요. sorted에 무엇을 넘기느냐에 따라 결과가 달라요. 딕셔너리를 그대로 넘기면 키만 줄 세워요. values()를 넘기면 판매량만 줄 세우는데 어느 메뉴인지가 빠져요. items()를 넘기면 키와 값을 묶은 튜플 리스트가 돼요. 앞 장의 튜플 규칙대로 첫 칸인 이름 순이에요. 이름과 판매량을 같이 두고 판매량으로 세우려면 다음 장처럼 items()에 key를 줘요." + REAL)

o = [sec("p-items")] + head(EB3, "items()에 key=lambda kv: kv[1]로 판매 순위", K3)
o += cell({"id": "c-p5", "lines": ["rank = sorted(sales.items(), key=lambda kv: kv[1], reverse=True)", "print(rank)", "for name, n in rank:", '    print(f"{name:<7}{n:>3}잔")'], "n": 5, "out": ["[('latte', 30), ('tea', 15), ('coffee', 12), ('cake', 8)]", "latte   30잔", "tea     15잔", "coffee  12잔", "cake     8잔"]}, 96, 196, 1300, sel="c-p5")
o.append(row(96, 640, 1300, 100, tup(['"latte"', "30"], hi=(1,)) + small("kv[0] 이름", GRAY, 24) + small("kv[1] 판매량", K3, 24), 1))
o.append(note_card(1440, 196, 384, 330, "kv는 짝 하나", "key와 value를 줄여 kv라고 지었어요. 이름은 자유예요.", K3, ' data-build-in="rise order 2"'))
o.append(note_card(1440, 556, 384, 320, "13의 꺼내 담기", "for name, n in rank:로 튜플을 두 변수에 나눠 담아 찍어요.", GRAY, ' data-build-in="rise order 3"'))
o.append(caption("이름과 값을 같이 두고 값으로 세우려면 items()에 key를 줘요.", 930))
W("p-items", o, "이름과 판매량을 같이 두고 판매량 많은 순으로 세워요. items()가 주는 튜플 하나를 kv로 받아요. key와 value의 첫 글자라서 kv라고 지었어요. kv[1]이 판매량이라 판매량으로 비교하고, reverse=True로 많은 순이에요. 결과는 튜플 리스트라서 for name, n in rank:처럼 13의 꺼내 담기로 두 변수에 나눠 찍어요. 칸 맞추기도 13에서 배운 그대로예요." + REAL)

o = [sec("p-get")] + head(EB3, "키만 필요하면 key=sales.get", K3)
o += cell({"id": "c-p6", "lines": ['print(sales.get("latte"))', "print(sorted(sales, key=sales.get))", "print(sorted(sales, key=sales.get, reverse=True))"], "n": 6, "out": ["30", "['cake', 'coffee', 'tea', 'latte']", "['latte', 'tea', 'coffee', 'cake']"]}, 96, 196, 1100, sel="c-p6")
o += pipe(96, 520, ['"coffee"', '"latte"', '"cake"', '"tea"'], "sales.get", ["12", "30", "8", "15"], K3, K3BG, 1, 200)
o.append(note_card(1240, 196, 584, 320, "get은 키를 넣으면 값을 줘요", "15의 sales.get(\"latte\")예요. 괄호 없이 sales.get만 넘기면 함수 자체가 넘어가요.", K3, ' data-build-in="rise order 4"'))
o.append(note_card(1240, 546, 584, 300, "lambda로 써도 같아요", "key=lambda k: sales[k]도 키마다 판매량을 꺼내요.", GRAY, ' data-build-in="rise order 5"'))
o.append(caption("키를 값 순서로 세우려면 key에 sales.get을 넘겨요.", 930))
W("p-get", o, "결과에 이름만 있으면 될 때는 더 짧게 써요. 15에서 배운 get은 키를 넣으면 값을 주는 메서드예요. 괄호 없이 sales.get만 key에 넘기면 sorted가 키마다 sales.get을 불러 판매량을 꺼내 비교해요. 결과는 키 리스트예요. 21에서 함수를 괄호 없이 넘긴 것과 같아요. lambda k: sales[k]로 적어도 결과는 같아요. 1파트의 max(sales, key=sales.get)도 이 방식이었어요." + REAL)

# ---------- part 4 ----------
o = [sec("m-basic")] + head(EB4, "max와 min도 key를 받아요", K4)
o += cell({"id": "c-m1", "lines": ["prices = [4500, 5000, 6500, 3000]", "print(max(prices), min(prices))", 'names = ["latte", "tea", "coffee"]', "print(max(names), min(names))", "print(max(names, key=len))"], "n": 1, "out": ["6500 3000", "tea coffee", "coffee"]}, 96, 200, 1000, sel="c-m1")
o.append(hl(96, 200, 1000, 4, 1, "mark", 1, "가장 긴 이름"))
o.append(note_card(1150, 200, 674, 280, "sorted와 같은 비교", "숫자는 크기, 글자는 abc 순이에요. tea가 가장 크고 coffee가 가장 작아요.", K4, ' data-build-in="rise order 2"'))
o.append(note_card(1150, 510, 674, 350, "결과는 원래 값 하나", "key=len으로 길이를 비교해도 돌아오는 건 길이 6이 아니라 이름 coffee예요.", GR, ' data-build-in="rise order 3"'))
o.append(note_card(96, 560, 1000, 300, "sorted 맨 앞, 맨 뒤와 같아요", "min은 sorted 결과의 첫 값, max는 마지막 값과 같아요. 하나만 필요하면 max, min이 짧아요.", OR, ' data-build-in="rise order 4"'))
o.append(caption("max(xs, key=함수)는 함수 결과가 가장 큰 원래 값을 돌려줘요.", 930))
W("m-basic", o, "13에서 max와 min은 가장 큰 값과 가장 작은 값을 줬어요. 비교 규칙은 sorted와 같아서 글자는 abc 순이에요. tea가 가장 크고 coffee가 가장 작아요. max와 min도 key를 받아요. key=len을 주면 길이로 비교해서 가장 긴 coffee를 돌려줘요. 돌아오는 건 길이 6이 아니라 원래 값이에요. sorted로 줄 세운 맨 뒤가 max, 맨 앞이 min이라고 생각하면 돼요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p4", "max와 min"))

o = [sec("m-dict")] + head(EB4, "가장 많이 팔린 메뉴는 max(sales, key=sales.get)", K4)
o += cell({"id": "c-m2", "lines": [SALES, "print(max(sales))", "print(max(sales, key=sales.get))", "print(min(sales, key=sales.get))", "print(max(sales.items(), key=lambda kv: kv[1]))"], "n": 2, "out": ["tea", "latte", "cake", "('latte', 30)"]}, 96, 196, 1100, sel="c-m2")
o.append(hl(96, 196, 1100, 1, 1, "skip", 1, "1파트의 tea"))
o.append(lockers(SALES_P, 96, 640, 250, 170, K4, K4BG, hi=(1,), attrs=' data-build-in="rise order 2"'))
o.append(callout(1240, 196, 584, 140, "key=sales.get", "이름만 받아요", K4, 3, 24))
o.append(callout(1240, 356, 584, 140, "min(…)", "가장 적게 팔린 cake", GRAY, 4, 24))
o.append(callout(1240, 516, 584, 140, "items(), kv[1]", "이름과 판매량을 같이", K3, 5, 24))
o.append(note_card(1240, 676, 584, 200, "필요한 것만 골라 써요", "이름만이면 get, 둘 다면 items()예요.", OR, ' data-build-in="rise order 6"'))
W("m-dict", o, "1파트의 문제를 다시 봐요. max(sales)는 키끼리 비교해서 tea였어요. key=sales.get을 주면 키마다 판매량을 꺼내 비교해서 latte를 돌려줘요. min도 같아서 가장 적게 팔린 cake이 나와요. 이름과 판매량이 같이 필요하면 items()를 넘기고 kv[1]로 비교해요. 결과가 ('latte', 30) 튜플이에요. 이름만 필요하면 get, 둘 다 필요하면 items()를 골라요." + REAL)

o = [sec("m-default")] + head(EB4, "빈 리스트에 max를 쓰면 ValueError가 나요", K4)
o += cell({"id": "c-m3", "lines": ["print(max([]))"], "n": 3, "out": ["ValueError: max() iterable argument is empty"], "err": True}, 96, 200, 1100, sel="c-m3")
o += cell({"id": "c-m4", "lines": ["big = list(filter(lambda p: p > 10000, prices))", "print(big)", "print(max(big, default=0))"], "n": 4, "out": ["[]", "0"]}, 96, 360, 1100, attrs=' data-build-in="rise order 2"')
o.append(hl(96, 360, 1100, 2, 1, "run", 3, "비면 0"))
o.append(note_card(1240, 200, 584, 300, "가장 큰 값이 없어요", "값이 하나도 없으면 고를 게 없어서 오류가 나요. min도 같아요.", K5, ' data-build-in="rise order 1"'))
o.append(note_card(1240, 530, 584, 330, "default=값", "비어 있을 때 대신 돌려줄 값이에요. 15의 get(키, 기본값)과 비슷해요.", K4, ' data-build-in="rise order 4"'))
o.append(note_card(96, 650, 1100, 210, "filter 결과는 비어 있을 수 있어요", "1만 원이 넘는 메뉴가 없어서 big이 빈 리스트예요. 고른 결과에 max를 쓸 땐 default를 같이 적어요.", OR, ' data-build-in="rise order 5"'))
W("m-default", o, "빈 리스트에 max를 쓰면 iterable argument is empty라는 ValueError가 나요. 가장 큰 값을 고르려는데 값이 하나도 없어서예요. 21의 filter로 고른 결과는 이렇게 비어 있을 수 있어요. 1만 원이 넘는 메뉴가 없어서 big이 빈 리스트예요. default=0처럼 적으면 비어 있을 때 오류 대신 0을 돌려줘요. 15의 get에 기본값을 준 것과 비슷해요. min도 똑같이 default를 받아요. Traceback 위쪽 줄은 빼고 마지막 줄만 옮겼어요. prices는 앞 셀에서 만들었어요." + REAL)

o = [sec("m-with")] + head(EB4, "sum, len, 자르기와 같이 써요", K4)
o += cell({"id": "c-m5", "lines": ["print(sum(sales.values()), len(sales))", "print(sum(sales.values()) / len(sales))", "top3 = sorted(sales, key=sales.get, reverse=True)[:3]", "print(top3)"], "n": 5, "out": ["65 4", "16.25", "['latte', 'tea', 'coffee']"]}, 96, 200, 1100, sel="c-m5")
o.append(callout(1240, 200, 584, 150, "sum, len", "모두 65잔, 메뉴 4개", K4, 1, 26))
o.append(callout(1240, 370, 584, 150, "sum / len", "메뉴 하나당 평균 16.25잔", OR, 2, 26))
o.append(callout(1240, 540, 584, 150, "[:3]", "줄 세운 리스트에서 앞 3개", K3, 3, 26))
o.append(slots(['"latte"', '"tea"', '"coffee"', '"cake"'], 96, 560, 220, 84, hi=(0, 1, 2), fs=26, color=K3, bg=K3BG, attrs=' data-build-in="rise order 3"'))
o.append(p(f"position:absolute;left:96px;top:700px;width:1100px;font-size:24px;font-weight:700;color:{SUB}", "sorted가 리스트를 주니까 13의 자르기를 바로 붙여요", ' data-build-in="fade order 3"'))
o.append(caption("상위 몇 개는 sorted 뒤에 [:n]을 붙여서 뽑아요.", 930))
W("m-with", o, "13의 sum, len과 자르기를 같이 써요. sales.values()를 sum하면 모두 65잔, len(sales)는 메뉴 4개예요. 나누면 메뉴 하나당 평균 16.25잔이에요. 많이 팔린 상위 3개는 sorted로 많은 순으로 세운 뒤 [:3]을 붙여요. sorted가 리스트를 주니까 바로 자를 수 있어요. 하나만 필요하면 max, 여러 개가 필요하면 sorted와 자르기예요." + REAL)

# ---------- part 5 ----------
o = [sec("t-mix")] + head(EB5, "숫자와 글자를 섞으면 비교할 수 없어요", K5)
o += cell({"id": "c-t1", "lines": ['print(sorted([4500, "5000", 6500]))'], "n": 1, "out": ["TypeError: '<' not supported between instances of 'str' and 'int'"], "err": True}, 96, 200, 1728, sel="c-t1")
o += cell({"id": "c-t2", "lines": ['print(sorted([4500, "5000", 6500], key=int))'], "n": 2, "out": ["[4500, '5000', 6500]"]}, 96, 370, 1100, attrs=' data-build-in="rise order 2"')
o.append(note_card(96, 540, 846, 320, "'<' not supported", "글자 \"5000\"과 숫자 4500 중 무엇이 작은지 정할 수 없다는 뜻이에요. max, min도 같은 오류가 나요.", K5, ' data-build-in="rise order 1"'))
o.append(note_card(978, 540, 846, 320, "key=int로 비교만 숫자로", "결과에는 \"5000\"이 글자로 남아 있어요. 처음부터 같은 타입으로 담는 게 가장 좋아요.", GR, ' data-build-in="rise order 3"'))
o.append(caption("한 리스트에는 같은 타입을 담아요. 섞였으면 key로 맞춰 비교해요.", 930))
W("t-mix", o, "가격 하나가 글자 \"5000\"으로 들어갔어요. sorted가 4500과 \"5000\"을 비교하려다 str과 int 사이에는 < 를 쓸 수 없다는 TypeError가 나요. 글자와 숫자는 어느 쪽이 작은지 정할 수 없어서예요. max와 min도 똑같은 오류가 나요. key=int를 주면 비교할 때만 숫자로 바꿔서 줄 세워요. 결과에는 \"5000\"이 글자로 그대로 남아요. 처음부터 같은 타입으로 담는 게 가장 좋아요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p5", "오류와 함정"))

o = [sec("t-paren")] + head(EB5, "key에 괄호를 붙이면 TypeError가 나요", K5)
o += cell({"id": "c-t3", "lines": ['print(sorted(["latte", "tea"], key=len()))'], "n": 3, "out": ["TypeError: len() takes exactly one argument (0 given)"], "err": True}, 96, 200, 1728, sel="c-t3")
o += cell({"id": "c-t4", "lines": [SALES, "print(sorted(sales, key=sales.get()))"], "n": 4, "out": ["TypeError: get expected at least 1 argument, got 0"], "err": True}, 96, 370, 1728, attrs=' data-build-in="rise order 1"')
o.append(note_card(96, 580, 1728, 170, "괄호를 붙이면 그 자리에서 아무것도 넣지 않고 실행해요", "len()과 sales.get()이 값 없이 먼저 불려서 0 given, got 0이 나왔어요. 21의 map(add10())과 같은 실수예요.", K5, ' data-build-in="rise order 2"'))
o.append(row(96, 790, 1728, 100, mono("key=len()", 32, RED, "#F8E6E6") + arrow(60, GR) + mono("key=len", 32, GR, "#E6F4EC") + '<div style="width:60px"></div>' + mono("key=sales.get()", 32, RED, "#F8E6E6") + arrow(60, GR) + mono("key=sales.get", 32, GR, "#E6F4EC"), 3))
W("t-paren", o, "key에 함수를 넣을 때 괄호를 붙이면 그 자리에서 함수가 먼저 실행돼요. len()은 재료 없이 불려서 하나를 받아야 하는데 0개를 받았다는 TypeError가 나요. sales.get()도 키 없이 불려서 got 0이라는 오류가 나요. 21에서 map에 add10()을 넘겼을 때와 같은 실수예요. key에는 괄호 없이 함수 이름만 적어요. 괄호는 sorted가 값을 하나씩 넣으면서 대신 붙여 줘요." + REAL)

o = [sec("t-lambda")] + head(EB5, "lambda나 key=를 빠뜨리면 생기는 오류", K5)
o += cell({"id": "c-t5", "lines": ["print(sorted(sales.items(), key=kv[1]))"], "n": 5, "out": ["NameError: name 'kv' is not defined"], "err": True}, 96, 200, 1100, sel="c-t5")
o += cell({"id": "c-t6", "lines": ["print(sorted(sales, sales.get))"], "n": 6, "out": ["TypeError: sorted expected 1 argument, got 2"], "err": True}, 96, 360, 1100, attrs=' data-build-in="rise order 2"')
o.append(note_card(1240, 200, 584, 250, "lambda kv: 가 빠졌어요", "kv는 lambda가 만드는 칸 이름이에요. lambda 없이 쓰면 그런 변수가 없어요.", K5, ' data-build-in="rise order 1"'))
o.append(note_card(1240, 480, 584, 250, "key= 이름을 빠뜨렸어요", "sorted는 줄 세울 값 하나만 위치로 받아요. key는 꼭 key=로 적어요.", K5, ' data-build-in="rise order 3"'))
o.append(side(96, 540, 1100, 190, "이렇게 고쳐요", ["sorted(sales.items(), key=lambda kv: kv[1])", "sorted(sales, key=sales.get)"], [], GR, "#E6F4EC", ' data-build-in="rise order 4"', 26))
W("t-lambda", o, "두 가지 빠뜨리기예요. 첫째는 lambda kv: 를 빼고 kv[1]만 적었어요. kv는 lambda가 만드는 매개변수 이름인데 lambda가 없으니 그런 변수가 없다는 NameError가 나요. 둘째는 key= 없이 sales.get을 둘째 자리에 넣었어요. sorted는 줄 세울 값 하나만 위치로 받고, key와 reverse는 20에서 배운 키워드 인자로만 받아요. 그래서 1개를 받아야 하는데 2개를 받았다는 TypeError가 나요." + REAL)

# ---------- part 6 ----------
o = [sec("x-rank")] + head(EB6, "판매 순위표 3위까지 찍기", K6)
RK = ['sales = {"coffee": 12, "latte": 30, "cake": 8, "tea": 15, "juice": 15}', "rank = sorted(sales.items(), key=lambda kv: (-kv[1], kv[0]))", "for i, kv in enumerate(rank[:3], 1):", '    print(f"{i}위 {kv[0]:<6}{kv[1]:>3}잔")']
o += cell({"id": "c-x1", "lines": RK, "n": 1, "out": ["1위 latte  30잔", "2위 juice  15잔", "3위 tea    15잔"]}, 96, 196, 1300, sel="c-x1")
o.append(hl(96, 196, 1300, 1, 1, "mark", 1))
o.append(hl(96, 196, 1300, 2, 1, "run", 2))
o.append(callout(96, 560, 846, 150, "(-kv[1], kv[0])", "3파트의 두 기준. juice와 tea가 15로 같아요", K3, 3, 24))
o.append(callout(978, 560, 846, 150, "enumerate(…, 1)", "18에서 배운 번호 붙이기. 1위부터", K6, 4, 24))
o.append(note_card(1440, 196, 384, 330, "kv는 튜플", "kv[0]이 이름, kv[1]이 잔 수예요.", GRAY, ' data-build-in="rise order 5"'))
o.append(caption("줄 세우기, 자르기, 번호 붙이기를 이어서 순위표를 만들어요.", 930))
W("x-rank", o, "판매 순위표를 만들어요. juice를 더해서 tea와 juice가 15잔으로 같아요. 3파트의 두 기준 key로 많은 순, 같으면 이름순으로 세워요. 앞 3개만 [:3]으로 자르고, 18에서 배운 enumerate에 시작 번호 1을 줘서 1위부터 번호를 붙였어요. kv는 튜플이라 kv[0]이 이름, kv[1]이 잔 수예요. 15잔끼리는 이름순이라 juice가 tea보다 앞이에요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p6", "실습"))

o = [sec("x-price")] + head(EB6, "가장 비싼 메뉴, 가장 싼 메뉴, 가격순 메뉴판", K6)
PRC = ['menu = {"coffee": 4500, "latte": 5000, "cake": 6500, "tea": 4000}', "hi = max(menu, key=menu.get)", "lo = min(menu, key=menu.get)", 'print(f"가장 비싼 메뉴 {hi} {menu[hi]:,}원")', 'print(f"가장 싼 메뉴 {lo} {menu[lo]:,}원")', "for m in sorted(menu, key=menu.get):", '    print(f"{m:<7}{menu[m]:>6,}원")']
o += cell({"id": "c-x2", "lines": PRC, "n": 2, "out": ["가장 비싼 메뉴 cake 6,500원", "가장 싼 메뉴 tea 4,000원", "tea     4,000원", "coffee  4,500원", "latte   5,000원", "cake    6,500원"]}, 96, 186, 1240, sel="c-x2")
o.append(hl(96, 186, 1240, 1, 2, "mark", 1, "이름을 받아요"))
o.append(hl(96, 186, 1240, 5, 1, "run", 2, "가격순 키"))
o.append(note_card(1380, 196, 444, 330, "이름으로 값 꺼내기", "max가 이름을 주니까 menu[hi]로 가격을 꺼내 같이 찍어요.", K6, ' data-build-in="rise order 3"'))
o.append(note_card(1380, 556, 444, 300, "for와 바로 써요", "sorted가 준 키 리스트를 for로 돌아요.", GRAY, ' data-build-in="rise order 4"'))
W("x-price", o, "메뉴판에서 가장 비싼 메뉴와 가장 싼 메뉴를 찾아요. 4파트처럼 max, min에 key=menu.get을 주면 가격으로 비교해서 이름을 돌려줘요. 이름을 받았으니 menu[hi]로 가격도 꺼내서 같이 찍어요. 가격순 메뉴판은 sorted(menu, key=menu.get)이 준 키 리스트를 for로 돌면서 찍었어요. 칸 맞추기와 천 단위 콤마는 13에서 배운 그대로예요." + REAL)

o = [sec("x-board")] + head(EB6, "메뉴판을 이름 길이순, 같으면 abc 순으로", K6)
o += cell({"id": "c-x3", "lines": ['names = ["mocha", "tea", "latte", "americano", "cake"]', "print(sorted(names, key=len))", "print(sorted(names, key=lambda n: (len(n), n)))"], "n": 3, "out": ["['tea', 'cake', 'mocha', 'latte', 'americano']", "['tea', 'cake', 'latte', 'mocha', 'americano']"]}, 96, 200, 1300, sel="c-x3")
o.append(hl(96, 200, 1300, 1, 1, "skip", 1, "5끼리는 원래 순서"))
o.append(hl(96, 200, 1300, 2, 1, "run", 2, "같으면 abc"))
o.append(row(96, 480, 1300, 100, small("key 결과", GRAY, 24, 160) + tup(["5", '"mocha"'], hi=(0,), w=120) + small(">", K6, 34) + tup(["5", '"latte"'], hi=(0,), w=120), 3))
o.append(p(f"position:absolute;left:96px;top:600px;width:1300px;font-size:24px;font-weight:700;color:{SUB}", "첫 칸 5가 같아서 둘째 칸 이름으로 비교해요. latte가 앞이에요", ' data-build-in="fade order 3"'))
o.append(note_card(1440, 200, 384, 400, "같을 때 기준 하나 더", "튜플로 돌려주면 첫 기준이 같을 때 둘째 기준을 봐요.", K6, ' data-build-in="rise order 4"'))
o.append(caption("기준이 둘이면 key가 (첫째 기준, 둘째 기준) 튜플을 돌려주게 해요.", 930))
W("x-board", o, "메뉴판 이름을 짧은 것부터 적고 싶어요. key=len만 주면 길이 5인 mocha와 latte는 처음 적은 순서대로 mocha가 먼저예요. 같은 길이끼리는 abc 순으로 세우고 싶으면 key가 길이와 이름을 묶은 튜플을 돌려주게 해요. 첫 칸 5가 같으니 둘째 칸 이름을 비교해서 latte가 앞으로 와요. 3파트의 판매량 순위와 같은 방법이에요. 이번에는 둘 다 작은 것부터라 -를 붙이지 않아요." + REAL)

o = [sec("x-score")] + head(EB6, "성적표를 점수순으로 세우고 1등과 평균 구하기", K6)
SC = ['scores = [("kim", 92), ("lee", 78), ("park", 85), ("choi", 59)]', "ranked = sorted(scores, key=lambda s: s[1], reverse=True)", "for name, score in ranked:", '    print(f"{name:<5}{score:>3}")', 'print("1등:", max(scores, key=lambda s: s[1])[0])', 'print("평균:", sum(map(lambda s: s[1], scores)) / len(scores))']
o += cell({"id": "c-x4", "lines": SC, "n": 4, "out": ["kim   92", "park  85", "lee   78", "choi  59", "1등: kim", "평균: 78.5"]}, 96, 186, 1300, sel="c-x4")
o.append(hl(96, 186, 1300, 1, 1, "mark", 1, "점수 높은 순"))
o.append(hl(96, 186, 1300, 4, 1, "mark", 2, "튜플에서 이름만"))
o.append(hl(96, 186, 1300, 5, 1, "run", 3, "21의 map"))
o.append(note_card(1440, 196, 384, 330, "[0]을 붙여 이름만", "max가 튜플 ('kim', 92)를 주니까 [0]으로 이름을 꺼내요.", K6, ' data-build-in="rise order 4"'))
o.append(note_card(1440, 556, 384, 310, "점수만 모아 더하기", "map으로 점수만 꺼내 sum에 넘겨요.", GRAY, ' data-build-in="rise order 5"'))
W("x-score", o, "17에서 만든 성적 데이터를 튜플 리스트로 적었어요. key=lambda s: s[1]과 reverse=True로 점수 높은 순으로 세워 찍어요. 1등은 max에 같은 key를 주면 돼요. max가 튜플을 통째로 주니까 [0]을 붙여 이름만 꺼냈어요. 평균은 21의 map으로 점수만 꺼내 sum에 넘기고 사람 수로 나눴어요. 정렬, max, map을 섞어서 썼어요." + REAL)

# ---------- wrap up ----------
trouble([("max(sales)가 엉뚱한 이름이에요", "딕셔너리는 키끼리 abc로 비교해요", "key=sales.get"),
         ("prices를 찍으니 None이에요", "prices = prices.sort()로 받았어요", "prices.sort()만"),
         ("['10', '100', '9'] 순서예요", "글자는 앞 글자부터 비교해요", "key=int"),
         ("TypeError: '<' not supported between ...", "숫자와 글자를 섞었어요", "타입 맞추기, key=int"),
         ("TypeError: len() takes exactly one argument", "key에 괄호를 붙였어요", "key=len"),
         ("NameError: name 'kv' is not defined", "lambda kv: 를 빠뜨렸어요", "key=lambda kv: kv[1]"),
         ("ValueError: max() iterable argument is empty", "빈 리스트에 max를 썼어요", "default=0")],
        "순서가 이상하면 map(key 함수, 리스트)로 비교할 값을 먼저 찍어 봐요.",
        "이번 챕터에서 자주 만나는 일을 모았어요. 1번과 3번은 오류 없이 순서만 이상한 경우예요. 무엇끼리 비교하는지 생각해 봐요. 2번은 sort가 값을 돌려주지 않아서 생겨요. 4번은 타입이 섞였을 때, 5번과 6번은 key에 함수를 잘못 넣었을 때예요. 7번은 고른 결과가 비었을 때예요. 순서가 기대와 다르면 21의 map으로 key 함수 결과를 먼저 찍어 보면 원인이 보여요.", 420)

cheatsheet([("sorted(xs)", "새 리스트, 원본 그대로", K2), ("xs.sort()", "원본을 바꾸고 None", K2), ("key=len", "len 결과로 비교", K2), ("key=lambda m: m[1]", "튜플 둘째 칸으로", K3),
            ("key=lambda m: (-m[1], m[0])", "많은 순, 같으면 이름순", K3), ("sorted(d, key=d.get)", "값 순서로 키 세우기", K3), ("max(d, key=d.get)", "값이 가장 큰 키", K4), ("max(xs, default=0)", "비어 있으면 0", K4)],
           ["key에는 괄호 없이 함수 이름이나 lambda를 넣어요", "다음 챕터: 리스트 컴프리헨션으로 고르고 바꾸기를 한 줄에"],
           "이번 챕터에서 쓴 모양을 한 장에 모았어요. sorted는 새 리스트를 주고 sort는 원본을 바꿔요. key에 함수를 넣으면 그 결과로 비교해요. 튜플은 앞 칸부터 비교하니까 기준이 둘이면 튜플을 돌려주는 lambda를 써요. 딕셔너리는 get이나 items로 값 기준 정렬을 해요. max와 min도 key와 default를 받아요. 23에서는 21의 map, filter를 더 읽기 쉽게 쓰는 리스트 컴프리헨션을 배워요.")

finish([("Lightbulb", K1, "왜 필요한가", "max(sales)가 tea인 이유, key 그림, 가장 짧은 key", "s-why", "s-min"),
        ("Code", K2, "sorted, sort, key", "새 리스트와 원본, None 함정, reverse, 글자 비교, key=len, str.lower, int", "o-two", "k-lower"),
        ("Archive", K3, "튜플과 딕셔너리 정렬", "앞 칸부터 비교, m[1] 기준, 두 기준, 키와 값과 items, get", "p-tuple", "p-get"),
        ("Star", K4, "max와 min", "key로 고르기, 가장 많이 팔린 메뉴, default, 상위 3개", "m-basic", "m-with"),
        ("Warning", K5, "오류와 함정", "숫자와 글자 섞기, key에 괄호, lambda와 key= 빠뜨리기", "t-mix", "t-lambda"),
        ("Check", K6, "실습", "판매 순위표, 가장 비싼 메뉴, 이름 길이순, 성적표", "x-rank", "x-score")],
       "여섯 파트로 나눴어요. 1파트는 max(sales)가 tea를 주는 장면과 key 그림이에요. 2파트는 sorted와 sort의 차이, reverse, 글자 비교 규칙, 이미 있는 함수를 key에 넣기예요. 3파트는 lambda를 key에 넣어 튜플과 딕셔너리를 줄 세워요. 4파트는 max와 min, 5파트는 자주 나는 오류, 6파트는 카페와 성적 실습이에요. 파트마다 새 커널에서 위에서부터 차례로 실행해요.",
       "정렬과 sorted, max, min 제대로 쓰기")
