"""Generates every slide of the control flow 2 deck (18, while, break) and slides/deck.json.

Story: keeps writing in basics.ipynb from chapters 12-17. Starts from a for loop that buys one coffee too many,
draws for and while side by side, teaches range and enumerate, then while, break and continue on the café's stock.
Part 5 builds totals, counts and maximums by hand next to sum(), max() and count(), and nests loops (times table,
chapter 14's scores). Ends with traps and four café exercises.
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


EB1 = "1. 왜 필요한가"
EB2 = "2. range와 번호"
EB3 = "3. while"
EB4 = "4. break와 continue"
EB5 = "5. 쌓기와 겹친 반복"
EB6 = "6. 함정과 실습"
K5, K5BG = GR, "#E6F4EC"
K6, K6BG = PUR, "#ECE7F8"
REAL = " 출력은 실제로 실행한 결과예요."
MENUS = 'menus = ["coffee", "latte", "cake"]'


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


# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#F2B27A;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
       '<h1 style="font-size:92px;font-weight:900;line-height:1.1;color:#F6F5F1">제어문 2<br>반복 제어</h1>',
       '<p style="font-size:40px;line-height:1.4;color:#BFC6D4">조건이 맞는 동안 돌고<br>필요하면 멈추기</p>']
cov.append(f'<div style="position:absolute;left:940px;top:300px;width:860px;height:480px;background:#252B36;border-radius:24px;padding:44px 48px;display:flex;flex-direction:column;justify-content:center;gap:16px">')
for line, c in [("for i in range(1, 4):", "#9DBDEB"), ("while stock > 0:", "#E3B877"), ("    stock -= 1", "#E6E9EF"), ("    if stock == 1:", "#8FD8DE"), ("        break", "#F2A0A0"), ("for i, m in enumerate(menus):", "#9DBDEB")]:
    cov.append(p(f"font-family:{MONO};font-size:34px;font-weight:700;line-height:1.45;color:{c};white-space:pre", e(line)))
cov.append('</div>')
W("cover", cov, "17에서 if로 조건에 따라 실행할 줄을 골랐어요. 이번 챕터는 반복을 다뤄요. 13의 for는 리스트를 처음부터 끝까지 돌았어요. 이번에는 range로 정한 횟수만큼 돌고, while로 조건이 맞는 동안 돌고, break와 continue로 도중에 멈추거나 건너뛰어요. 17과 같은 카페 예제를 이어서 써요.", ("intro", "들어가기"))

ORDER.append("toc")

# ---------- ready ----------
o = [sec("ready")] + head("들어가기", "17에서 이어서 해요", JP)
done = [("hello-uv 노트북, 커널 .venv", "09 · 25–27쪽"), ("+=, -=, //", "12"), ("리스트, for, f-string, end=", "13"), ("2차원 리스트 scores", "14"), ("딕셔너리 items()", "15"), ("if, elif, else, and, or", "17")]
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
W("ready", o, "09에서 만든 hello-uv 폴더를 VS Code로 열고, 12부터 쓰던 basics.ipynb를 다시 열어요. 12의 +=와 -=, 13의 for와 f-string, print의 end, 14의 2차원 리스트, 15의 items(), 17의 if를 그대로 써요. 슬라이드의 출력은 tools/demo.sh가 hello-uv 커널에서 같은 셀을 실제로 실행한 결과예요. 셀 번호는 파트마다 [1]부터 다시 셌어요.")

# ---------- part 1 ----------
o = [sec("w-why")] + head(EB1, "몇 번 돌지 모르면 for로 쓰기 어려워요", K1)
o += cell({"id": "c-why", "lines": ["money = 10000", "for cup in [1, 2, 3]:", "    money -= 4500", '    print(f"{cup}잔째, 남은 돈 {money}원")'], "n": 1, "out": ["1잔째, 남은 돈 5500원", "2잔째, 남은 돈 1000원", "3잔째, 남은 돈 -3500원"]}, 96, 200, 960, sel="c-why")
o.append(hl(96, 200, 960, 1, 1, "mark", 1, "3번으로 정함"))
o.append(warn(96, 540, 960, 200, "돈이 -3500원이 됐어요", "for는 리스트 길이만큼 꼭 돌아요. 돈이 모자라도 셋째 잔을 계산해요.", ' data-build-in="rise order 2"'))
o.append(note_card(1110, 200, 714, 300, "묻고 싶은 건 이거예요", "\"10000원으로 4500원짜리 커피를 몇 잔 살 수 있나요?\" 몇 잔인지 모르니 리스트를 미리 만들 수 없어요.", K1, ' data-build-in="rise order 3"'))
o.append(note_card(1110, 530, 714, 210, "말로 바꾸면", "\"돈이 4500원 이상인 동안 계속 사요.\" 횟수가 아니라 조건으로 반복해요.", GR, ' data-build-in="rise order 4"'))
o.append(caption("\"~인 동안 반복\"을 적는 문법이 while이에요.", 920))
W("w-why", o, "13에서 for는 리스트의 값 개수만큼 돌았어요. 여기서는 1, 2, 3 세 번으로 정했어요. 그런데 10000원으로는 두 잔만 살 수 있어서 셋째 잔에서 돈이 마이너스가 돼요. for는 돈이 모자란지 신경 쓰지 않고 정한 만큼 돌아요. 알고 싶은 건 몇 잔 살 수 있는지라서 횟수를 미리 정할 수 없어요. 이럴 때 돈이 4500원 이상인 동안 계속 사라고 적는 문법이 while이에요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p1", "왜 필요한가"))

o = [sec("w-big")] + head(EB1, "for는 묶음을 하나씩, while은 조건이 True인 동안", K1)
o.append(label("for · 줄 선 값을 하나씩 꺼내요", 96, 200, BL, ' data-build-in="fade order 1"', 820, 26))
o.append(slots(["coffee", "latte", "cake"], 96, 250, 240, 90, attrs=' data-build-in="rise order 1"', fs=30, color=BL, bg="#E5EEF8", hi=(0,)))
o.append(flow(96, 400, 820, 400,
              [dict(x=160, y=0, w=500, h=90, text="다음 값을 꺼내요", color=BL, mono=False, order=2),
               dict(x=160, y=150, w=500, h=90, text="들여쓴 줄 실행", color=GR, bg="#E6F4EC", mono=False, order=2),
               dict(x=160, y=300, w=500, h=90, text="값이 없으면 끝", color=GRAY, mono=False, order=3)],
              [dict(pts=[(410, 92), (410, 146)], order=2), dict(pts=[(660, 195), (760, 195), (760, 45), (664, 45)], color=BL, order=2), dict(pts=[(160, 45), (60, 45), (60, 345), (156, 345)], color=GRAY, order=3, dash=True)]))
o.append(label("while · 조건을 묻고 또 물어요", 1010, 200, OR, ' data-build-in="fade order 4"', 814, 26))
o.append(flow(1010, 250, 814, 560,
              [dict(x=140, y=0, w=480, h=170, kind="diamond", text="money >= 4500", color=OR, bg="#F7EEDD", order=4, fs=26),
               dict(x=160, y=250, w=440, h=90, text="money -= 4500", color=GR, bg="#E6F4EC", order=5),
               dict(x=160, y=440, w=440, h=90, text="반복 끝, 다음 줄", color=GRAY, mono=False, order=6)],
              [dict(pts=[(380, 172), (380, 246)], color=GR, order=5, label="True", lx=400, ly=190),
               dict(pts=[(600, 295), (720, 295), (720, 85), (624, 85)], color=GR, order=5, label="다시 묻기", lx=600, ly=30),
               dict(pts=[(140, 85), (50, 85), (50, 485), (156, 485)], color=RED, order=6, label="False", lx=60, ly=260)]))
o.append(caption("횟수를 알면 for, 조건만 알면 while이에요.", 920))
W("w-big", o, "반복은 두 가지예요. 왼쪽 for는 리스트처럼 줄 선 값을 하나씩 꺼내서 들여쓴 줄을 실행하고, 값이 떨어지면 끝나요. 몇 번 도는지 처음부터 정해져 있어요. 오른쪽 while은 17의 if처럼 마름모에서 조건을 물어요. True면 들여쓴 줄을 실행하고, 다시 마름모로 돌아가 또 물어요. False가 나오는 순간 반복을 끝내고 다음 줄로 가요. if는 한 번 묻고 지나가지만 while은 False가 될 때까지 계속 물어요.")

o = [sec("w-min")] + head(EB1, "가장 짧은 while로 몇 잔인지 세요", K1)
o += cell({"id": "c-min", "lines": ["money = 10000", "cups = 0", "while money >= 4500:", "    money -= 4500", "    cups += 1", 'print(f"{cups}잔, 남은 돈 {money}원")'], "n": 2, "out": ["2잔, 남은 돈 1000원"]}, 96, 200, 900, sel="c-min")
o.append(hl(96, 200, 900, 2, 1, "mark", 1, "조건"))
o.append(hl(96, 200, 900, 3, 2, "run", 1, "True인 동안"))
o += table(1050, 200, 774, [("money", 170), (">= 4500", 190), ("cups", 120), ("", 180)],
           [("10000", "True", "0", "사요"), ("5500", "True", "1", "사요"), ("1000", "False", "2", "멈춰요")], 2, K1, 76, hi=(2,))
o.append(note_card(96, 520, 900, 340, "if와 같은 모양이에요", "while 조건 콜론, 다음 줄 4칸 들여쓰기. if는 한 번 묻고 끝나지만 while은 들여쓴 줄을 다 실행한 뒤 다시 조건으로 돌아가요.", K1, ' data-build-in="rise order 3"'))
o.append(note_card(1050, 520, 774, 340, "멈추는 열쇠는 money -= 4500", "돌 때마다 money가 줄어서 언젠가 조건이 False가 돼요. 3파트에서 이 줄을 빼면 어떻게 되는지 봐요.", OR, ' data-build-in="rise order 5"'))
o.append(caption("while 조건: 은 조건이 True인 동안 들여쓴 줄을 반복해요.", 920))
W("w-min", o, "앞 장의 질문을 while로 풀었어요. money가 4500 이상인 동안 커피를 사요. 살 때마다 money에서 4500을 빼고 cups에 1을 더해요. 오른쪽 표처럼 10000일 때 True, 5500일 때 True, 1000일 때 False가 나와서 두 잔에서 멈춰요. 모양은 17의 if와 같아요. 조건 뒤에 콜론, 다음 줄은 4칸 들여써요. 다른 점은 들여쓴 줄을 다 실행한 뒤 다시 조건으로 돌아가 묻는다는 거예요." + REAL)

# ---------- part 2 ----------
o = [sec("r-range")] + head(EB2, "range(5)는 0부터 4까지 다섯 개예요", K2)
o += cell({"id": "c-r1", "lines": ["print(range(5))", "print(list(range(5)))", "print(len(range(5)))"], "n": 1, "out": ["range(0, 5)", "[0, 1, 2, 3, 4]", "5"]}, 96, 200, 860, sel="c-r1")
o.append(label("range(5)", 1010, 200, K2, ' data-build-in="fade order 1"', 814, 28))
o.append(slots(["0", "1", "2", "3", "4"], 1010, 250, 120, 96, top_lbl=False, attrs=' data-build-in="rise order 1"', fs=38, color=K2, bg=K2BG, hi=(0, 1, 2, 3, 4)))
o.append(p(f"position:absolute;left:1650px;top:250px;width:120px;height:96px;border-radius:14px;border:3px dashed {RED};font-family:{MONO};font-size:38px;font-weight:700;line-height:90px;text-align:center;color:{RED}", "5", ' data-build-in="rise order 2"'))
o.append(label("5는 안 들어가요", 1600, 360, RED, ' data-build-in="fade order 2"', 224, 22))
o.append(note_card(96, 500, 860, 360, "숫자 줄을 만들어 줘요", "range(5)는 0부터 5 바로 앞까지 정수 다섯 개예요. print로 찍으면 range(0, 5)라고만 나와서 list()로 감싸 눈으로 확인해요. 리스트 번호처럼 0부터 세요.", K2, ' data-build-in="rise order 3"'))
o.append(note_card(1010, 440, 814, 420, "왜 끝 숫자가 빠지나요", "range(5)의 개수가 딱 5개가 되도록 정했어요. 13의 자르기 [0:5]도 5번 칸은 빠졌어요. 리스트 길이 len(menus)를 넣으면 마지막 번호까지 딱 맞아요.", None, ' data-build-in="rise order 4"'))
o.append(caption("range(n)은 0부터 n-1까지, n개예요.", 920))
W("r-range", o, "range는 숫자 줄을 만들어 줘요. range(5)는 0, 1, 2, 3, 4 다섯 개예요. print로 그냥 찍으면 range(0, 5)라고만 나와서 13의 list()로 감싸서 확인해요. 끝 숫자 5는 들어가지 않아요. 그래서 개수가 딱 5개예요. 13에서 문자열과 리스트를 [0:5]로 자를 때도 5번 칸은 빠졌어요. 같은 규칙이에요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p2", "range와 번호"))

o = [sec("r-step")] + head(EB2, "시작, 끝, 간격을 정할 수 있어요", K2)
o += cell({"id": "c-r2", "lines": ["print(list(range(1, 6)))", "print(list(range(0, 10, 2)))", "print(list(range(5, 0, -1)))", "print(list(range(3, 3)))"], "n": 2, "out": ["[1, 2, 3, 4, 5]", "[0, 2, 4, 6, 8]", "[5, 4, 3, 2, 1]", "[]"]}, 96, 200, 860, sel="c-r2")
rr = [("range(1, 6)", ["1", "2", "3", "4", "5"], "1부터 6 앞까지"), ("range(0, 10, 2)", ["0", "2", "4", "6", "8"], "2씩 건너뛰기"), ("range(5, 0, -1)", ["5", "4", "3", "2", "1"], "거꾸로, 0 앞까지"), ("range(3, 3)", [], "시작과 끝이 같으면 비어요")]
for i, (k, vals, d) in enumerate(rr):
    y = 200 + i * 170
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:1010px;top:{y}px;width:814px;height:150px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:14px 24px;display:flex;flex-direction:column;gap:10px">'
             + '<div style="display:flex;flex-direction:row;align-items:center;gap:16px">' + mono(k, 24, K2, K2BG) + p(f"font-size:22px;color:{SUB}", e(d)) + '</div>'
             + '<div style="display:flex;flex-direction:row;gap:8px">' + ("".join(p(f"width:72px;height:56px;border-radius:10px;border:2px solid {K2};background:{K2BG};font-family:{MONO};font-size:26px;font-weight:700;line-height:52px;text-align:center;color:{INK}", v) for v in vals) if vals else p(f"font-size:24px;color:{GRAY};line-height:56px", "아무것도 없어요")) + '</div></div>')
o.append(f'<div data-build-in="rise order 5" style="position:absolute;left:96px;top:560px;width:860px;height:300px;background:{CARD};border:2px solid {LINE};border-top:10px solid {K2};border-radius:20px;padding:24px 30px;display:flex;flex-direction:column;gap:16px">'
         + p(f"font-size:28px;font-weight:700;color:{INK}", "range(시작, 끝, 간격)")
         + p(f"font-size:24px;line-height:1.5;color:{INK}", "13의 자르기 [시작:끝:간격]과 같은 순서예요. 하나만 적으면 끝, 둘이면 시작과 끝이에요.")
         + p(f"font-size:24px;line-height:1.5;color:{INK}", "간격이 -1이면 거꾸로 세요. 이때는 시작이 끝보다 커야 해요.") + '</div>')
o.append(caption("끝 숫자는 늘 빠져요. 1부터 5까지는 range(1, 6)이에요.", 920))
W("r-step", o, "range에 숫자를 두 개 넣으면 시작과 끝이에요. range(1, 6)은 1부터 6 바로 앞인 5까지예요. 세 개를 넣으면 셋째가 간격이에요. range(0, 10, 2)는 0부터 2씩 건너뛰어 짝수만 나와요. 간격을 -1로 하면 거꾸로 세요. 이때는 시작 5가 끝 0보다 커야 해요. 시작과 끝이 같으면 빈 줄이에요. 13의 자르기 [시작:끝:간격]과 순서도, 끝이 빠지는 규칙도 같아요." + REAL)

o = [sec("r-for")] + head(EB2, "for와 range로 정한 횟수만큼 돌아요", K2)
o += cell({"id": "c-r3", "lines": ["for i in range(3):", '    print("주문", i)', "for i in range(1, 4):", '    print(f"{i}번 손님")'], "n": 3, "out": ["주문 0", "주문 1", "주문 2", "1번 손님", "2번 손님", "3번 손님"]}, 96, 200, 860, sel="c-r3")
o.append(note_card(1010, 200, 814, 250, "리스트 대신 range를 넣어요", "13에서는 for o in orders처럼 리스트를 돌았어요. range(3)을 넣으면 0, 1, 2를 하나씩 i에 넣어요. 그래서 세 번 돌아요.", K2, ' data-build-in="rise order 1"'))
o.append(note_card(1010, 480, 814, 200, "사람에게 보일 번호는 1부터", "range(1, 4)로 1, 2, 3을 만들어요. i + 1로 적어도 돼요.", None, ' data-build-in="rise order 2"', "gap:8px"))
o.append(note_card(1010, 710, 814, 150, "i는 그냥 이름이에요", "번호(index)의 앞 글자 i를 많이 써요. n, k로 적어도 돼요.", None, ' data-build-in="rise order 3"', "gap:8px;padding:16px 30px"))
o.append(caption("\"n번 반복\"은 for i in range(n): 이에요.", 920))
W("r-for", o, "for 뒤에 리스트 대신 range를 넣으면 정한 횟수만큼 돌아요. range(3)은 0, 1, 2라서 세 번 돌고, i에는 차례로 0, 1, 2가 들어가요. 손님 번호처럼 사람에게 보일 번호는 1부터 세는 게 자연스러워서 range(1, 4)로 1, 2, 3을 만들어요. i는 정해진 이름이 아니에요. 번호라는 뜻의 index 앞 글자를 관례로 많이 써요. 1파트의 [1, 2, 3] 리스트도 range(1, 4)로 바꿔 쓸 수 있어요." + REAL)

o = [sec("r-index")] + head(EB2, "번호와 값을 같이 쓰려면 range(len())", K2)
o += cell({"id": "c-r4", "lines": [MENUS, "for i in range(len(menus)):", "    print(i, menus[i])"], "n": 4, "out": ["0 coffee", "1 latte", "2 cake"]}, 96, 200, 860, sel="c-r4")
o += cell({"id": "c-r5", "lines": ["i = 0", "for m in menus:", "    print(i, m)", "    i += 1"], "n": 5, "out": ["0 coffee", "1 latte", "2 cake"]}, 96, 520, 860, attrs=' data-build-in="rise order 3"')
o += chain([("len(menus)", None, "3"), ("range(3)", None, "0, 1, 2"), ("menus[i]", None, "번호로 꺼내기")], 1010, 200, 814, 1, K2, 84)
o.append(note_card(1010, 470, 814, 210, "번호로 값을 꺼내요", "i가 번호라서 값은 13처럼 menus[i]로 꺼내요. 리스트 길이가 바뀌어도 len이 맞춰 줘요.", K2, ' data-build-in="rise order 2"'))
o.append(note_card(1010, 700, 814, 160, "아래는 번호를 직접 세는 방법", "i를 0에서 시작해 돌 때마다 1씩 더해요.", None, ' data-build-in="rise order 3"', "gap:8px"))
o.append(caption("번호가 필요하면 range(len(리스트))로 돌고 [i]로 꺼내요.", 940))
W("r-index", o, "값과 함께 몇 번째인지도 필요할 때가 있어요. range(len(menus))는 range(3)이라 0, 1, 2를 돌아요. i가 번호라서 값은 menus[i]로 꺼내요. 아래 셀은 같은 일을 번호를 직접 세며 한 거예요. i를 0으로 두고 한 번 돌 때마다 1을 더해요. 두 방법 다 결과가 같아요. 다음 장에서 이 둘을 한 줄로 줄인 enumerate를 봐요." + REAL)

o = [sec("r-enum")] + head(EB2, "enumerate는 번호와 값을 한 쌍씩 줘요", K2)
o += cell({"id": "c-r6", "lines": ["for i, m in enumerate(menus):", "    print(i, m)", "for i, m in enumerate(menus, 1):", '    print(f"{i}. {m}")'], "n": 6, "out": ["0 coffee", "1 latte", "2 cake", "1. coffee", "2. latte", "3. cake"]}, 96, 200, 860, sel="c-r6")
o += cell({"id": "c-r7", "lines": ["print(list(enumerate(menus)))"], "n": 7, "out": ["[(0, 'coffee'), (1, 'latte'), (2, 'cake')]"]}, 96, 720, 860, attrs=' data-build-in="rise order 2"')
o.append(card(1010, 200, 814, 330, p(f"font-size:26px;font-weight:700;color:{INK}", "같은 결과, 세 가지 모양")
              + '<div style="display:flex;flex-direction:row;align-items:center;gap:16px">' + mono("for i, m in enumerate(menus):", 22, K2, K2BG) + p(f"font-size:20px;color:{SUB}", "줄인 방법") + '</div>'
              + '<div style="display:flex;flex-direction:row;align-items:center;gap:16px">' + mono("for i in range(len(menus)):", 22, GRAY, "#EEEFF2") + p(f"font-size:20px;color:{SUB}", "앞 장") + '</div>'
              + '<div style="display:flex;flex-direction:row;align-items:center;gap:16px">' + mono("i = 0 ... i += 1", 22, GRAY, "#EEEFF2") + p(f"font-size:20px;color:{SUB}", "직접 세기") + '</div>', None, ' data-build-in="rise order 1"'))
o.append(note_card(1010, 560, 814, 300, "(번호, 값) 튜플을 줘요", "list()로 찍으면 튜플 리스트예요. 13의 for a, b in 튜플리스트처럼 두 이름에 나눠 담아요. 둘째 자리에 1을 넣으면 번호가 1부터 시작해요.", K2, ' data-build-in="rise order 3"'))
o.append(caption("번호와 값이 둘 다 필요하면 enumerate를 써요.", 940))
W("r-enum", o, "앞 장의 두 방법을 한 줄로 줄인 게 enumerate예요. enumerate(menus)는 번호와 값을 한 쌍씩 줘요. list()로 찍어 보면 (번호, 값) 튜플의 리스트예요. 그래서 13에서 튜플 리스트를 돌 때처럼 for i, m in으로 두 이름에 나눠 담아요. 괄호 안 둘째 자리에 1을 넣으면 번호가 1부터 시작해서 메뉴판 번호를 찍기 좋아요. 처음에는 range(len())이 이해하기 쉽고, 익숙해지면 enumerate를 써요." + REAL)

# ---------- part 3 ----------
o = [sec("w-shape")] + head(EB3, "while은 묻기, 실행, 값 바꾸기를 돌아요", K3)
o += cell({"id": "c-w1", "lines": ["count = 1", "while count <= 3:", '    print(f"{count}번째")', "    count += 1", 'print("끝, count는", count)'], "n": 1, "out": ["1번째", "2번째", "3번째", "끝, count는 4"]}, 96, 200, 860, sel="c-w1")
o.append(hl(96, 200, 860, 0, 1, "mark", 1, "1 · 시작값"))
o.append(hl(96, 200, 860, 1, 1, "mark", 2, "2 · 묻기"))
o.append(hl(96, 200, 860, 2, 1, "run", 3, "3 · 실행"))
o.append(hl(96, 200, 860, 3, 1, "run", 4, "4 · 값 바꾸기"))
steps = [("1", "시작값", "count = 1", K3), ("2", "묻기", "count <= 3", OR), ("3", "실행", "print(...)", GR), ("4", "값 바꾸기", "count += 1", BL)]
for i, (n_, t_, k, col) in enumerate(steps):
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:1010px;top:{200 + i * 140}px;width:814px;height:120px;background:{CARD};border:2px solid {LINE};border-left:10px solid {col};border-radius:18px;padding:0 24px;display:flex;flex-direction:row;align-items:center;gap:20px">'
             + num(int(n_), col, 32) + p(f"width:170px;flex:none;font-size:28px;font-weight:700;color:{INK}", e(t_)) + mono(k, 26, col, "#F6F5F1") + '</div>')
o.append(p(f"position:absolute;left:1010px;top:770px;width:814px;font-size:24px;font-weight:700;color:{SUB}", "4 다음에 2로 돌아가 다시 물어요. False면 끝.", ' data-build-in="fade order 5"'))
o.append(note_card(96, 600, 860, 260, "끝난 뒤 count는 4", "3번째를 찍고 4가 된 뒤 4 <= 3을 물어서 False가 나와 멈췄어요. 반복이 끝나도 count는 마지막 값을 갖고 있어요.", K3, ' data-build-in="rise order 6"'))
o.append(caption("while에는 시작값, 조건, 값 바꾸기 세 가지가 꼭 있어야 해요.", 920))
W("w-shape", o, "while 반복은 네 단계로 읽어요. 먼저 반복 전에 시작값을 정해요. count는 1이에요. 다음으로 조건을 물어요. True면 들여쓴 줄을 실행해요. 마지막 줄에서 count에 1을 더해 값을 바꿔요. 그리고 다시 조건으로 돌아가 물어요. 4가 되면 4 <= 3이 False라서 반복을 끝내요. 끝난 뒤에도 count는 4로 남아 있어요. 시작값, 조건, 값 바꾸기 중 하나라도 빠지면 반복이 아예 안 돌거나 끝나지 않아요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p3", "while"))

o = [sec("w-trace")] + head(EB3, "재고가 0이 될 때까지 주문을 받아요", K3)
o += cell({"id": "c-w2", "lines": ["stock = 3", "while stock > 0:", "    stock -= 1", '    print(f"주문 받았어요. 남은 재고 {stock}")', 'print("품절이에요")'], "n": 2, "out": ["주문 받았어요. 남은 재고 2", "주문 받았어요. 남은 재고 1", "주문 받았어요. 남은 재고 0", "품절이에요"]}, 96, 200, 1000, sel="c-w2")
o += cell({"id": "c-w3", "lines": ["stock = 0", "while stock > 0:", "    stock -= 1", '    print("주문 받았어요")', 'print("품절이에요")'], "n": 3, "out": ["품절이에요"]}, 96, 600, 1000, attrs=' data-build-in="rise order 5"')
o += table(1150, 200, 674, [("stock", 130), ("> 0", 150), ("하는 일", 250)],
           [("3", "True", "1 빼고 찍기"), ("2", "True", "1 빼고 찍기"), ("1", "True", "1 빼고 찍기"), ("0", "False", "반복 끝")], 1, K3, 70, hi=(3,))
o.append(note_card(1150, 560, 674, 300, "처음부터 False면 0번", "재고가 처음부터 0이면 조건이 바로 False예요. 들여쓴 줄을 한 번도 실행하지 않고 품절이에요로 가요.", OR, ' data-build-in="rise order 5"'))
o.append(caption("조건은 반복할 때마다 처음에 물어요. 처음부터 False면 한 번도 안 돌아요.", 920))
W("w-trace", o, "재고 3개에서 시작해 주문을 받을 때마다 하나씩 줄여요. 오른쪽 표처럼 3, 2, 1일 때는 조건이 True라서 주문을 받아요. 0이 되면 0 > 0이 False라서 반복을 끝내고 품절이에요를 찍어요. 아래 셀은 재고가 처음부터 0이에요. 조건을 처음 물을 때 이미 False라서 들여쓴 줄은 한 번도 실행하지 않아요. while은 들여쓴 줄을 실행하기 전에 매번 조건부터 물어요." + REAL)

o = [sec("w-inf")] + head(EB3, "값을 안 바꾸면 끝나지 않아요", RED)
o += cell({"id": "c-w5", "lines": ["count = 1", "while count <= 3:", "    print(count)"], "n": 5, "out": ["1", "1", "1", "1", "...  (1초 동안 17만 줄 넘게)", "KeyboardInterrupt:"]}, 96, 200, 860, sel="c-w5")
o.append(hl(96, 200, 860, 2, 1, "err", 1, "count += 1이 없어요"))
o.append(warn(96, 640, 860, 220, "무한 반복이에요", "count가 늘 1이라 1 <= 3이 늘 True예요. 출력이 끝없이 쌓이고 셀 왼쪽이 계속 돌아가요.", ' data-build-in="rise order 2"'))
o.append(f'<div data-build-in="rise order 3" style="position:absolute;left:1010px;top:200px;width:814px;height:380px;background:{CARD};border:2px solid {LINE};border-top:10px solid {JP};border-radius:20px;padding:26px 32px;display:flex;flex-direction:column;gap:22px">'
         + p(f"font-size:30px;font-weight:700;color:{INK}", "노트북에서 멈추기")
         + '<div style="display:flex;flex-direction:row;gap:18px;align-items:center">' + num(1, JP, 34) + p(f"font-size:26px;color:{INK}", "셀 왼쪽의") + mono("■", 28, RED, "#F8E6E6") + p(f"font-size:26px;color:{INK}", "버튼 누르기") + '</div>'
         + '<div style="display:flex;flex-direction:row;gap:18px;align-items:center">' + num(2, JP, 34) + p(f"font-size:26px;color:{INK}", "또는 위쪽 도구 막대의") + mono("Interrupt", 24, JP, "#F7EEDD") + '</div>'
         + '<div style="display:flex;flex-direction:row;gap:18px;align-items:center">' + num(3, JP, 34) + p(f"font-size:26px;color:{INK}", "KeyboardInterrupt가 나오면 멈춘 거예요") + '</div></div>')
o.append(f'<div data-build-in="rise order 4" style="position:absolute;left:1010px;top:610px;width:814px;height:250px;background:{CARD};border:2px solid {LINE};border-top:10px solid {GRAY};border-radius:20px;padding:26px 32px;display:flex;flex-direction:column;gap:18px">'
         + p(f"font-size:30px;font-weight:700;color:{INK}", "터미널(uv run main.py)에서 멈추기") + key_pair("Ctrl+C", "control+C", 28) + '</div>')
o.append(caption("while 안에 조건을 바꾸는 줄이 있는지 먼저 봐요.", 920))
W("w-inf", o, "앞 장의 while에서 count += 1을 빼먹었어요. count가 계속 1이라 조건이 늘 True고, 반복이 끝나지 않아요. 이걸 무한 반복이라고 해요. 노트북에서는 실행 중인 셀 왼쪽 버튼이 네모 정지 버튼으로 바뀌어요. 그 버튼이나 위쪽의 Interrupt를 누르면 멈추고 KeyboardInterrupt가 나와요. 09처럼 터미널에서 uv run으로 실행했다면 Ctrl+C, Mac은 control+C를 눌러요. 실제로 1초 만에 멈췄는데 1이 17만 줄 넘게 찍혔어요. 슬라이드에는 앞의 네 줄과 마지막 줄만 옮겼어요. 출력이 너무 많으면 VS Code가 느려질 수 있으니 바로 멈춰요.")

o = [sec("w-vs")] + head(EB3, "for와 while은 이럴 때 써요", K3)
o += cell({"id": "c-w4", "lines": ["for i in range(1, 4):", "    print(i)", "i = 1", "while i <= 3:", "    print(i)", "    i += 1"], "n": 4, "out": ["1", "2", "3", "1", "2", "3"]}, 96, 200, 760, sel="c-w4")
o.append(hl(96, 200, 760, 0, 2, "run", 1, "2줄"))
o.append(hl(96, 200, 760, 2, 4, "mark", 2, "4줄"))
cmp_ = [("", "for", "while"), ("언제", "횟수나 묶음이 정해졌을 때", "조건이 False가 될 때까지"), ("예", "메뉴 하나씩, 10번 반복", "돈이 남는 동안, 재고가 있는 동안"), ("멈춤", "값이 떨어지면 저절로", "값 바꾸기를 직접 적어야"), ("실수", "거의 없어요", "무한 반복")]
for i, row in enumerate(cmp_):
    y = 200 + i * 116
    hd = i == 0
    o.append(f'<div data-build-in="rise order {3 if i else 3}" style="position:absolute;left:910px;top:{y}px;width:914px;height:100px;background:{"transparent" if hd else CARD};border:{"none" if hd else "2px solid " + LINE};border-radius:16px;padding:0 24px;display:flex;flex-direction:row;align-items:center;gap:20px">'
             + p(f"width:100px;flex:none;font-size:24px;font-weight:700;color:{GRAY}", e(row[0]))
             + p(f"width:360px;flex:none;font-size:{30 if hd else 24}px;font-weight:700;{'font-family:' + MONO + ';' if hd else ''}color:{BL if hd else INK}", e(row[1]))
             + p(f"flex:1;font-size:{30 if hd else 24}px;font-weight:700;{'font-family:' + MONO + ';' if hd else ''}color:{OR if hd else INK}", e(row[2])) + '</div>')
o.append(caption("둘 다 쓸 수 있으면 for가 짧고 안전해요. 횟수를 모를 때 while을 써요.", 920))
W("w-vs", o, "1부터 3까지 찍는 일은 for와 while 둘 다 할 수 있어요. for는 range가 숫자를 알아서 바꿔 줘서 두 줄이에요. while은 시작값과 값 바꾸기를 직접 적어서 네 줄이에요. 그래서 횟수나 묶음이 정해져 있으면 for를 써요. 돈이 남는 동안, 재고가 있는 동안처럼 몇 번 돌지 모를 때는 while을 써요. while은 값 바꾸기를 빼먹으면 앞 장처럼 끝나지 않으니 그 줄부터 확인해요." + REAL)

# ---------- part 4 ----------
ORD = ['orders = ["coffee", "cake", "latte", "tea", "cake"]', 'soldout = ["latte"]']
ORDERS = ["coffee", "cake", "latte", "tea", "cake"]


def jump(left, top, w, fi, ti, color, text, order):
    """An arrow outside the right edge of a cell, from code line fi to code line ti: where break or continue jumps to."""
    yc = lambda i: 10 + i * LINE_H + LINE_H / 2
    yf, yt = yc(fi), yc(ti)
    y0 = min(yf, yt) - 20
    return flow(left + w + 4, top + y0, 230, abs(yt - yf) + 40,
                [], [dict(pts=[(0, yf - y0), (56, yf - y0), (56, yt - y0), (6, yt - y0)], color=color, order=order, label=text, lx=68, ly=abs(yt - yf) / 2 + 2)])


def order_row(left, top, states, order, title, color):
    """Five orders in a row with what happened to each: 받음, 품절, 건너뜀, 안 봄."""
    o = [label(title, left, top, color, f' data-build-in="fade order {order}"', 590, 24)]
    sty = {"받음": (GR, "#E6F4EC", INK), "멈춤": (RED, "#F8E6E6", INK), "건너뜀": (OR, "#F7EEDD", INK), "안 봄": ("#C9CED8", "#F1F0EC", "#B4B9C3")}
    for i, (m, st) in enumerate(zip(ORDERS, states)):
        c, b, t_ = sty[st]
        o.append(f'<div data-build-in="rise order {order}" style="position:absolute;left:{left + i * 118}px;top:{top + 44}px;width:110px;height:118px;border-radius:14px;border:3px solid {c};background:{b};display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px">'
                 + p(f"font-family:{MONO};font-size:22px;font-weight:700;color:{t_}", e(m)) + p(f"font-size:20px;font-weight:700;color:{c if st != '안 봄' else GRAY}", e(st)) + '</div>')
    return o


BRK = ["for o in orders:", "    if o in soldout:", '        print(f"{o} 품절, 주문을 멈춰요")', "        break", '    print(f"{o} 주문 받았어요")', 'print("끝")']
CNT = ["for o in orders:", "    if o in soldout:", '        print(f"{o} 품절, 건너뛰어요")', "        continue", '    print(f"{o} 주문 받았어요")', 'print("끝")']

o = [sec("b-break")] + head(EB4, "break는 반복을 그 자리에서 끝내요", K4)
o += cell({"id": "c-b1", "lines": ORD + BRK, "n": 1, "out": ["coffee 주문 받았어요", "cake 주문 받았어요", "latte 품절, 주문을 멈춰요", "끝"]}, 96, 200, 940, sel="c-b1")
o.append(hl(96, 200, 940, 5, 1, "err", 1))
o.append(hl(96, 200, 940, 7, 1, "run", 2))
o.append(jump(96, 200, 940, 5, 7, RED, "for 밖으로", 2))
o += order_row(1230, 200, ["받음", "받음", "멈춤", "안 봄", "안 봄"], 3, "orders 다섯 개 중 셋만 봤어요", K4)
o.append(note_card(1230, 420, 594, 240, "남은 주문은 보지도 않아요", "break를 만나면 tea, cake가 남아 있어도 for를 끝내고 for 밖의 print(\"끝\")으로 가요.", RED, ' data-build-in="rise order 4"'))
o.append(note_card(1230, 690, 594, 170, "break는 if 안에 둬요", "if 없이 쓰면 첫 주문에서 바로 끝나요. \"이러면 그만\"을 if로 적어요.", None, ' data-build-in="rise order 5"', "gap:8px"))
o.append(caption("break는 \"여기서 그만\". 남은 차례를 버리고 반복 아래 줄로 가요.", 920))
W("b-break", o, "주문 리스트를 하나씩 받다가 품절 메뉴를 만나면 그만 받아요. orders에 다섯 주문이 있고, latte가 품절이에요. coffee와 cake는 품절이 아니라 주문 받았어요를 찍어요. latte에서 if가 True고, 품절이라고 찍은 뒤 break를 만나요. break는 빨간 화살표처럼 반복을 그 자리에서 끝내고 for 밖의 다음 줄, print 끝으로 가요. 뒤에 남은 tea와 cake는 보지도 않아요. break 아래의 주문 받았어요 줄도 실행하지 않아요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p4", "break와 continue"))

o = [sec("b-continue")] + head(EB4, "continue는 이번 차례만 건너뛰고 계속 돌아요", K4)
o += cell({"id": "c-b2", "lines": CNT, "n": 2, "out": ["coffee 주문 받았어요", "cake 주문 받았어요", "latte 품절, 건너뛰어요", "tea 주문 받았어요", "cake 주문 받았어요", "끝"]}, 96, 200, 940, sel="c-b2")
o.append(hl(96, 200, 940, 3, 1, "mark", 1))
o.append(hl(96, 200, 940, 0, 1, "run", 2))
o.append(jump(96, 200, 940, 3, 0, OR, "다음 주문", 2))
o += order_row(1230, 200, ["받음", "받음", "멈춤", "안 봄", "안 봄"], 3, "break · 셀 [1]", RED)
o += order_row(1230, 400, ["받음", "받음", "건너뜀", "받음", "받음"], 4, "continue · 셀 [2]", OR)
o.append(note_card(1230, 620, 594, 240, "한 단어만 바꿨어요", "같은 주문 리스트에서 break를 continue로만 바꿨어요. latte만 빼고 tea, cake까지 모두 받아요.", OR, ' data-build-in="rise order 5"'))
o.append(caption("continue는 \"이번만 넘기기\". 아래 줄을 건너뛰고 다음 차례로 가요.", 920))
W("b-continue", o, "앞 장과 같은 주문 리스트에서 break만 continue로 바꿨어요. latte에서 품절이라고 찍은 뒤 continue를 만나요. continue는 주황 화살표처럼 아래 줄을 건너뛰고 for 줄로 돌아가 다음 주문을 꺼내요. 그래서 latte의 주문 받았어요만 빠지고 tea와 cake는 받아요. 오른쪽에 두 결과를 나란히 놓았어요. break는 latte에서 끝나서 셋만 봤고, continue는 다섯을 모두 봤어요. 셀 [2]는 셀 [1]의 orders와 soldout을 그대로 써요." + REAL)

o = [sec("b-jump")] + head(EB4, "화살표로 보면 어디로 가는지 보여요", K4)
o += cell({"id": "c-b3", "lines": ["for i in range(1, 6):", "    if i == 3:", "        break", "    print(i)", 'print("---")', "for i in range(1, 6):", "    if i == 3:", "        continue", "    print(i)"], "n": 3, "out": ["1", "2", "---", "1", "2", "4", "5"]}, 96, 200, 700, sel="c-b3")
o.append(jump(96, 200, 700, 2, 4, RED, "break", 1))
o.append(jump(96, 200, 700, 7, 5, OR, "continue", 2))
for row, (lbl, kind) in enumerate([("break", "b"), ("continue", "c")]):
    y = 210 + row * 330
    o.append(label(lbl, 1100, y, RED if kind == "b" else OR, f' data-build-in="fade order {row + 1}"', 400, 30))
    for j in range(5):
        v = j + 1
        on = (v < 3) if kind == "b" else (v != 3)
        col = GR if on else ((RED if kind == "b" else OR) if v == 3 else "#C9CED8")
        bg = "#E6F4EC" if on else (("#F8E6E6" if kind == "b" else "#F7EEDD") if v == 3 else "#F1F0EC")
        o.append(p(f"position:absolute;left:{1100 + j * 145}px;top:{y + 56}px;width:130px;height:110px;border-radius:16px;border:3px solid {col};background:{bg};font-family:{MONO};font-size:44px;font-weight:700;line-height:104px;text-align:center;color:{INK if on or v == 3 else '#B4B9C3'}", str(v), f' data-build-in="rise order {row + 1}"'))
    o.append(p(f"position:absolute;left:1100px;top:{y + 186}px;width:724px;font-size:24px;font-weight:700;color:{SUB}", "3에서 반복 끝. 4, 5는 돌지도 않아요" if kind == "b" else "3만 건너뛰고 4, 5는 계속 돌아요", f' data-build-in="fade order {row + 1}"'))
o.append(caption("break 화살표는 반복 아래로, continue 화살표는 반복 맨 위로 가요.", 920))
W("b-jump", o, "숫자로 한 번 더 비교해요. 1부터 5까지 돌면서 3에서 break와 continue를 써요. 빨간 화살표의 break는 반복 아래 줄인 대시 줄로 바로 가요. 그래서 1, 2만 찍히고 4, 5는 돌지도 않아요. 주황 화살표의 continue는 반복 맨 위 for 줄로 돌아가 다음 숫자 4를 꺼내요. 3만 빠지고 1, 2, 4, 5가 찍혀요. 헷갈리면 이 두 화살표 방향을 떠올려요. 아래로 나가면 break, 위로 돌아가면 continue예요." + REAL)

o = [sec("b-long")] + head(EB4, "continue는 else로 길게 쓸 수도 있어요", K4)
o += cell({"id": "c-b4", "lines": ["for o in orders:", "    if o in soldout:", '        print(f"{o} 품절, 건너뛰어요")', "    else:", '        print(f"{o} 주문 받았어요")', 'print("끝")'], "n": 4, "out": ["coffee 주문 받았어요", "cake 주문 받았어요", "latte 품절, 건너뛰어요", "tea 주문 받았어요", "cake 주문 받았어요", "끝"]}, 96, 200, 860, sel="c-b4")
o.append(hl(96, 200, 860, 3, 2, "mark", 1, "else 안"))
o.append(side(1010, 200, 814, 330, "continue로 쓰면 · 셀 [2]", CNT[:5], [], OR, "#F7EEDD", ' data-build-in="rise order 2"', 23, "결과가 같아요"))
o.append(note_card(1010, 560, 814, 300, "언제 continue가 편한가요", "건너뛸 경우를 맨 위에서 먼저 걸러 두면 아래 줄을 else 안에 넣지 않아도 돼요. 아래 할 일이 길수록 들여쓰기 한 단계가 줄어서 읽기 쉬워요.", OR, ' data-build-in="rise order 3"'))
o.append(caption("continue는 \"이 경우는 빼고\"를 맨 위에 적는 방법이에요.", 920))
W("b-long", o, "continue 없이 17의 if, else로 써도 결과가 같아요. 품절이면 건너뛴다고 찍고, 아니면 else에서 주문을 받아요. 오른쪽은 셀 [2]의 continue 버전이에요. 차이는 모양이에요. continue는 건너뛸 경우를 맨 위에서 걸러 내서, 아래 할 일을 else 안에 넣지 않아도 돼요. 주문 받기가 여러 줄로 길어지면 들여쓰기가 한 단계 얕아서 읽기 쉬워요. 처음에는 if, else로 적어도 괜찮아요." + REAL)

o = [sec("b-true")] + head(EB4, "while True와 break로 \"될 때까지\" 돌아요", K4)
o += cell({"id": "c-b5", "lines": ["left = 3", "n = 0", "while True:", "    if left == 0:", '        print("재고가 떨어졌어요")', "        break", "    left -= 1", "    n += 1", '    print(f"{n}번째 주문, 남은 재고 {left}")'], "n": 5, "out": ["1번째 주문, 남은 재고 2", "2번째 주문, 남은 재고 1", "3번째 주문, 남은 재고 0", "재고가 떨어졌어요"]}, 96, 200, 940, sel="c-b5")
o.append(hl(96, 200, 940, 2, 1, "mark", 1, "늘 True"))
o.append(jump(96, 200, 940, 5, 9, RED, "반복 밖으로", 2))
o.append(note_card(1290, 200, 534, 280, "조건 자리에 True를 적어요", "while True:는 늘 True라서 스스로는 끝나지 않아요. 안쪽의 break가 유일한 출구예요.", K4, ' data-build-in="rise order 1"'))
o.append(note_card(1290, 510, 534, 350, "언제 쓰나요", "멈출 조건을 반복 중간에 확인할 때예요. 숫자 맞히기처럼 \"맞힐 때까지\" 돌 때도 써요. break가 꼭 있는지 먼저 봐요. 없으면 3파트의 무한 반복이에요.", RED, ' data-build-in="rise order 3"'))
o.append(caption("while True:를 쓰면 break가 나가는 문이에요.", 920))
W("b-true", o, "while 뒤에 True를 그대로 적으면 조건이 늘 True예요. 그래서 반복이 스스로는 끝나지 않고, 안쪽 if 안의 break가 유일한 출구예요. 재고가 0이 되면 재고가 떨어졌어요를 찍고 break로 나가요. 화살표가 가리키는 마지막 줄 아래, 반복 밖으로 나가요. while left > 0으로도 쓸 수 있지만, 멈출 조건을 반복 중간에 확인하고 싶을 때나 맞힐 때까지처럼 끝을 미리 정하기 어려울 때 이 모양을 써요. break를 빼먹으면 무한 반복이 되니 꼭 확인해요." + REAL)


# ---------- part 5 ----------
o = [sec("a-sum")] + head(EB5, "합계는 0에서 시작해 하나씩 더해요", K5)
o += cell({"id": "c-a1", "lines": ["prices = [4500, 5000, 6500, 4500]", "total = 0", "for p in prices:", "    total += p", "print(total)", "print(sum(prices))"], "n": 1, "out": ["20500", "20500"]}, 96, 200, 860, sel="c-a1")
o.append(hl(96, 200, 860, 1, 3, "mark", 1, "원래 방법"))
o.append(hl(96, 200, 860, 5, 1, "run", 3, "줄인 방법"))
o += table(1010, 200, 814, [("p", 160), ("total += p", 260), ("total", 200)],
           [("", "", "0"), ("4500", "0 + 4500", "4500"), ("5000", "4500 + 5000", "9500"), ("6500", "9500 + 6500", "16000"), ("4500", "16000 + 4500", "20500")], 2, K5, 64, hi=(4,))
o.append(note_card(96, 560, 860, 300, "sum()은 이 반복을 대신해요", "13에서 배운 sum(prices)는 위 세 줄과 같은 일을 해요. 숫자 리스트의 합계는 sum()을 쓰고, 원래 모양은 sum()이 무엇을 하는지 이해하는 데 써요.", K5, ' data-build-in="rise order 3"'))
o.append(caption("쌓을 변수를 반복 밖에서 0으로 두고, 안에서 +=로 더해요.", 920))
W("a-sum", o, "반복으로 값을 쌓는 기본 모양이에요. 반복 밖에서 total을 0으로 두고, 안에서 가격을 하나씩 더해요. 오른쪽 표처럼 0에서 4500, 9500, 16000, 20500으로 늘어요. 13에서 배운 sum(prices)는 이 세 줄을 한 번에 해 주는 함수예요. 결과가 20500으로 같아요. 숫자 리스트의 합계는 sum을 쓰면 돼요. 다음 장부터는 sum처럼 한 줄로 되지 않는 일을 같은 모양으로 풀어요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p5", "쌓기와 겹친 반복"))

o = [sec("a-count")] + head(EB5, "조건에 맞는 것을 세고 모아요", K5)
o += cell({"id": "c-a2", "lines": ["n = 0", "for p in prices:", "    if p >= 5000:", "        n += 1", "print(n)", "print(prices.count(4500))"], "n": 2, "out": ["2", "2"]}, 96, 200, 840, sel="c-a2")
o += cell({"id": "c-a4", "lines": ["big = []", "for p in prices:", "    if p >= 5000:", "        big.append(p)", "print(big)", "print(len(big))"], "n": 4, "out": ["[5000, 6500]", "2"]}, 984, 200, 840, attrs=' data-build-in="rise order 2"')
o.append(hl(96, 200, 840, 3, 1, "run", 1, "세기"))
o.append(hl(984, 200, 840, 3, 1, "run", 2, "모으기"))
o.append(slots(["4500", "5000", "6500", "4500"], 96, 560, 190, 84, top_lbl=False, hi=(1, 2), attrs=' data-build-in="rise order 1"', fs=30, color=K5, bg=K5BG))
o.append(note_card(96, 680, 840, 180, "count()는 같은 값만 세요", "5000 이상처럼 조건이 붙으면 for와 if로 세요.", None, ' data-build-in="rise order 3"', "gap:8px"))
o.append(note_card(984, 600, 840, 260, "모으면 개수도 알아요", "17의 골라 담기와 같아요. 모은 리스트의 len이 개수예요. 값도 필요하면 모으고, 개수만 필요하면 세요.", K5, ' data-build-in="rise order 3"'))
o.append(caption("세기는 n += 1, 모으기는 append예요. 둘 다 if 안에 둬요.", 920))
W("a-count", o, "가격이 5000원 이상인 메뉴가 몇 개인지 세요. n을 0으로 두고 조건이 True일 때만 1을 더해요. 5000과 6500, 두 개예요. 13의 count는 4500처럼 같은 값만 셀 수 있어서 이런 조건에는 못 써요. 오른쪽은 같은 조건으로 값을 모은 거예요. 17의 골라 담기 모양이에요. 모은 리스트의 len을 보면 개수도 알 수 있어요. 셀 [3]은 다음 장의 최댓값이라 순서를 바꿔 보여 줬어요." + REAL)

o = [sec("a-max")] + head(EB5, "가장 큰 값은 지금까지 1등과 비교해요", K5)
o += cell({"id": "c-a3", "lines": ["big = prices[0]", "for p in prices:", "    if p > big:", "        big = p", "print(big)", "print(max(prices), min(prices))"], "n": 3, "out": ["6500", "6500 4500"]}, 96, 200, 860, sel="c-a3")
o.append(hl(96, 200, 860, 0, 1, "mark", 1, "첫 값으로 시작"))
o.append(hl(96, 200, 860, 2, 2, "run", 2, "더 크면 바꾸기"))
o += table(1010, 200, 814, [("p", 150), ("p > big", 190), ("big", 160)],
           [("", "", "4500"), ("4500", "False", "4500"), ("5000", "True", "5000"), ("6500", "True", "6500"), ("4500", "False", "6500")], 2, K5, 64, hi=(3,))
o.append(note_card(96, 540, 860, 320, "왜 0이 아니라 첫 값으로 시작하나요", "값이 모두 음수라면 0이 가장 크다고 잘못 나와요. 리스트의 첫 값으로 시작하면 어떤 숫자든 맞아요. 13의 max()와 min()이 이 일을 한 줄로 해 줘요.", K5, ' data-build-in="rise order 3"'))
o.append(caption("지금까지 가장 큰 값을 big에 두고, 더 큰 값을 만나면 바꿔요.", 920))
W("a-max", o, "가장 비싼 가격을 직접 찾아요. big에 리스트의 첫 값을 넣고 시작해요. 하나씩 꺼내 big보다 크면 big을 그 값으로 바꿔요. 오른쪽 표처럼 5000, 6500에서 바뀌고, 마지막 4500에서는 그대로예요. 0으로 시작하지 않는 이유는 값이 모두 음수일 때 0이 답으로 나와 버리기 때문이에요. 13의 max와 min은 이 반복을 한 줄로 해 줘요. 결과가 같아요." + REAL)

o = [sec("n-gugu")] + head(EB5, "반복 안에 반복을 넣으면 표를 만들어요", K5)
o += cell({"id": "c-n1", "lines": ["for dan in range(2, 4):", "    for i in range(1, 4):", '        print(f"{dan} x {i} = {dan * i}")', '    print("---")'], "n": 5, "out": ["2 x 1 = 2", "2 x 2 = 4", "2 x 3 = 6", "---", "3 x 1 = 3", "3 x 2 = 6", "3 x 3 = 9", "---"]}, 96, 200, 860, sel="c-n1")
o.append(hl(96, 200, 860, 0, 1, "mark", 1, "바깥 · 2번"))
o.append(hl(96, 200, 860, 1, 2, "run", 2, "안쪽 · 3번씩"))
grid_ = [[f"{d}x{i}" for i in range(1, 4)] for d in range(2, 4)]
o.append(label("바깥 dan = 2, 3 · 안쪽 i = 1, 2, 3", 1010, 200, K5, ' data-build-in="fade order 2"', 814, 24))
o.append(grid(grid_, 1010, 250, 170, 84, hi={(0, 0), (0, 1), (0, 2)}, attrs=' data-build-in="rise order 2"', fs=30, color=K5, bg=K5BG))
o.append(note_card(1010, 540, 814, 320, "시계의 시침과 분침", "바깥이 한 번 움직일 때 안쪽이 처음부터 끝까지 돌아요. 2단의 1, 2, 3을 다 돌고 나서야 3단으로 가요. 안쪽 print는 8칸, 바깥의 --- 는 4칸이에요.", K5, ' data-build-in="rise order 3"'))
o.append(caption("바깥 2번 × 안쪽 3번 = 모두 6번 실행해요.", 920))
W("n-gugu", o, "for 안에 for를 넣을 수 있어요. 17에서 if 안에 if를 넣은 것과 같아요. 바깥 for가 dan에 2를 넣으면 안쪽 for가 i를 1, 2, 3까지 다 돌아요. 그다음에 바깥이 3으로 바뀌고 안쪽이 다시 처음부터 돌아요. 시계의 시침이 한 칸 갈 때 분침이 한 바퀴 도는 것과 같아요. 그래서 2 곱하기 3, 모두 6줄이 찍혀요. 안쪽 print는 8칸, 바깥의 대시 줄은 4칸 들여써서 단마다 한 번씩 찍혀요." + REAL)

o = [sec("n-2d")] + head(EB5, "14의 성적표를 행과 열 번호로 돌아요", K5)
o += cell({"id": "c-n2", "lines": ["scores = [[90, 85, 77],", "          [70, 95, 88],", "          [60, 75, 99]]", "for i in range(len(scores)):", "    for j in range(len(scores[i])):", "        if scores[i][j] < 70:", '            print(f"{i}행 {j}열: {scores[i][j]}점")'], "n": 6, "out": ["2행 0열: 60점"]}, 96, 200, 1000, sel="c-n2")
o.append(hl(96, 200, 1000, 3, 1, "mark", 1, "행 번호 i"))
o.append(hl(96, 200, 1000, 4, 1, "mark", 2, "열 번호 j"))
o.append(grid([[90, 85, 77], [70, 95, 88], [60, 75, 99]], 1150, 200, 150, 84, hi={(2, 0)}, attrs=' data-build-in="rise order 3"', fs=32, color=K5, bg=K5BG))
o.append(note_card(96, 600, 1000, 260, "14에서는 for row in scores로 돌았어요", "그때는 행 리스트를 통째로 꺼냈어요. 번호도 알고 싶으면 range(len())을 두 번 겹쳐요. 안쪽 길이는 len(scores[i])예요.", K5, ' data-build-in="rise order 3"'))
o.append(note_card(1150, 560, 674, 300, "[행][열] 순서", "scores[2][0]은 2행 0열이에요. 몇 번째 학생의 몇 번째 과목인지 알려 줄 수 있어요.", None, ' data-build-in="rise order 4"'))
o.append(caption("2차원 리스트는 바깥 for가 행, 안쪽 for가 열이에요.", 940))
W("n-2d", o, "14의 성적표 2차원 리스트를 다시 돌아요. 14에서는 for row in scores로 행을 통째로 꺼냈어요. 이번에는 번호도 알고 싶어서 range(len())을 두 번 겹쳤어요. 바깥 i는 행 번호, 안쪽 j는 열 번호예요. 안쪽 길이는 그 행의 길이 len(scores[i])예요. 70점 아래인 칸을 찾으면 몇 행 몇 열인지 찍어요. 2행 0열의 60점 하나예요. 14에서 본 [행][열] 순서 그대로예요." + REAL)

o = [sec("n-break")] + head(EB5, "안쪽 break는 안쪽 반복만 멈춰요", K5)
o += cell({"id": "c-n3", "lines": ["for row in scores:", "    for s in row:", "        if s < 80:", '            print("80점 아래", s, "찾음")', "            break", '    print("이 행 확인 끝", row)'], "n": 7, "out": ["80점 아래 77 찾음", "이 행 확인 끝 [90, 85, 77]", "80점 아래 70 찾음", "이 행 확인 끝 [70, 95, 88]", "80점 아래 60 찾음", "이 행 확인 끝 [60, 75, 99]"]}, 96, 200, 1000, sel="c-n3")
o.append(hl(96, 200, 1000, 4, 1, "err", 1, "안쪽만 끝"))
o.append(hl(96, 200, 1000, 5, 1, "run", 2, "바깥은 계속"))
o.append(grid([[90, 85, 77], [70, 95, 88], [60, 75, 99]], 1150, 200, 150, 84, hi={(0, 2), (1, 0), (2, 0)}, attrs=' data-build-in="rise order 1"', fs=32, color=RED, bg="#F8E6E6"))
o.append(note_card(1150, 560, 674, 300, "가장 가까운 반복 하나", "break는 자기를 감싼 가장 가까운 for 하나만 끝내요. 바깥 for는 다음 행으로 넘어가요.", K5, ' data-build-in="rise order 2"'))
o.append(caption("행마다 처음 찾은 값에서 멈추고, 다음 행은 계속 확인해요.", 940))
W("n-break", o, "반복을 겹쳤을 때 break가 어디까지 멈추는지 봐요. 행마다 80점 아래인 값을 처음 찾으면 break해요. 첫 행은 77에서 안쪽 for가 끝나고, 바깥 for의 이 행 확인 끝을 찍은 뒤 다음 행으로 가요. 둘째 행은 첫 칸 70에서 바로 멈춰서 95, 88은 보지 않아요. break는 자기를 감싼 가장 가까운 반복 하나만 끝내요. 바깥까지 다 멈추는 방법은 이번 챕터에서 다루지 않아요." + REAL)

# ---------- part 6 ----------
o = [sec("t-remove")] + head(EB6, "돌면서 같은 리스트를 지우면 하나를 놓쳐요", RED)
o += cell({"id": "c-t1", "lines": ['orders = ["tea", "tea", "coffee", "tea", "cake"]', "for o in orders:", '    if o == "tea":', "        orders.remove(o)", "print(orders)"], "n": 1, "out": ["['coffee', 'tea', 'cake']"]}, 96, 200, 900, sel="c-t1")
o += cell({"id": "c-t2", "lines": ['orders = ["tea", "tea", "coffee", "tea", "cake"]', "keep = []", "for o in orders:", '    if o != "tea":', "        keep.append(o)", "print(keep)"], "n": 2, "out": ["['coffee', 'cake']"]}, 96, 520, 900, attrs=' data-build-in="rise order 3"')
o.append(hl(96, 200, 900, 3, 1, "err", 1, "도는 중에 지우기"))
o.append(label("지울 때마다 뒤 값이 한 칸씩 당겨져요", 1050, 200, RED, ' data-build-in="fade order 2"', 774, 24))
o.append(slots(["tea", "tea", "coffee", "tea", "cake"], 1050, 244, 140, 80, hi=(0,), attrs=' data-build-in="rise order 2"', fs=24, color=RED, bg="#F8E6E6"))
o.append(slots(["tea", "coffee", "tea", "cake"], 1050, 374, 140, 80, hi=(1,), attrs=' data-build-in="rise order 2"', fs=24, color=GRAY, bg="#EEEFF2"))
o.append(p(f"position:absolute;left:1050px;top:490px;width:774px;font-size:22px;line-height:1.5;color:{SUB}", "0번 tea를 지우면 둘째 tea가 0번으로 와요. for는 다음 차례인 1번 coffee로 넘어가서 그 tea를 못 봐요.", ' data-build-in="fade order 2"'))
o.append(note_card(1050, 620, 774, 240, "새 리스트에 남길 것만 모아요", "원래 리스트는 그대로 두고 keep에 tea가 아닌 것만 append해요. 17의 골라 담기예요.", GR, ' data-build-in="rise order 3"'))
o.append(caption("돌고 있는 리스트는 지우지 않아요. 새 리스트에 모아요.", 920))
W("t-remove", o, "주문에서 tea를 모두 지우려고 돌면서 remove했어요. 그런데 tea 하나가 남았어요. 0번 tea를 지우면 뒤의 값이 한 칸씩 앞으로 당겨져서 둘째 tea가 0번 자리로 와요. for는 이미 0번을 봤으니 다음 차례인 1번으로 넘어가요. 그래서 당겨진 tea를 건너뛰어요. 오류가 나지 않아서 놓치기 쉬워요. 돌고 있는 리스트를 바꾸지 말고, 남길 것만 새 리스트에 모아요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p6", "함정과 실습"))

o = [sec("t-indent")] + head(EB6, "들여쓰기 한 단계 차이로 결과가 달라져요", RED)
cs = [("c-t3", ["total = 0", "for p in [4500, 5000, 6500]:", "    total += p", "    print(total)"], 3, ["4500", "9500", "16000"], "print가 for 안", "돌 때마다 찍어요"),
      ("c-t4", ["total = 0", "for p in [4500, 5000, 6500]:", "    total += p", "print(total)"], 4, ["16000"], "print가 for 밖", "다 돈 뒤 한 번"),
      ("c-t5", ["for p in [4500, 5000, 6500]:", "    total = 0", "    total += p", "print(total)"], 5, ["6500"], "total = 0이 for 안", "돌 때마다 0으로 돌아가요")]
for i, (cid, lines, n_, out, t_, d) in enumerate(cs):
    x = 96 + i * 584
    o += cell({"id": cid, "lines": lines, "n": n_, "out": out}, x, 200, 560, attrs=f' data-build-in="rise order {i + 1}"', sel=cid if i == 0 else None)
    o.append(hl(x, 200, 560, 3 if i < 2 else 1, 1, "err" if i == 2 else ("run" if i == 0 else "mark"), i + 1))
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:{x}px;top:600px;width:560px;height:200px;background:{CARD};border:2px solid {LINE};border-top:10px solid {RED if i == 2 else GR};border-radius:18px;padding:20px 26px;display:flex;flex-direction:column;gap:10px">'
             + p(f"font-size:26px;font-weight:700;color:{INK}", e(t_)) + p(f"font-size:24px;line-height:1.5;color:{SUB}", e(d)) + '</div>')
o.append(caption("쌓을 변수는 for 위에서 0으로, 결과는 for 아래에서 찍어요.", 920))
W("t-indent", o, "들여쓰기 한 단계 차이로 결과가 달라지는 세 경우예요. 첫째는 print가 for 안이라 돌 때마다 지금까지의 합계를 찍어요. 둘째는 print를 for 밖으로 뺐어요. 다 돈 뒤에 16000을 한 번만 찍어요. 셋째는 total = 0을 for 안에 넣었어요. 돌 때마다 0으로 돌아가서 마지막 가격 6500만 남아요. 셋 다 오류가 없어서 결과를 보고 찾아야 해요. 쌓을 변수는 반복 위, 결과는 반복 아래가 기본이에요." + REAL)

o = [sec("t-range")] + head(EB6, "range(len())에 1을 더하면 칸을 넘어가요", RED)
o += cell({"id": "c-t6", "lines": [MENUS, "for i in range(len(menus) + 1):", "    print(menus[i])"], "n": 6, "out": ["coffee", "latte", "cake", "IndexError: list index out of range"]}, 96, 200, 900, sel="c-t6")
o += cell({"id": "c-t7", "lines": ["print(list(range(1, 5)))", "print(list(range(len(menus))))"], "n": 7, "out": ["[1, 2, 3, 4]", "[0, 1, 2]"]}, 96, 560, 900, attrs=' data-build-in="rise order 3"')
o.append(slots(["coffee", "latte", "cake"], 1050, 200, 180, 84, hi=(0, 1, 2), attrs=' data-build-in="rise order 1"', fs=26, color=K2, bg=K2BG))
o.append(p(f"position:absolute;left:1626px;top:240px;width:180px;height:84px;border-radius:14px;border:3px dashed {RED};font-family:{MONO};font-size:26px;font-weight:700;line-height:78px;text-align:center;color:{RED}", "3번 없음", ' data-build-in="rise order 2"'))
o.append(note_card(1050, 380, 774, 250, "번호는 0부터 len - 1까지", "menus는 3칸이라 번호는 0, 1, 2예요. range(len(menus))가 딱 맞아요. + 1을 하면 없는 3번 칸을 꺼내다 오류가 나요.", RED, ' data-build-in="rise order 2"'))
o.append(note_card(1050, 660, 774, 200, "1부터 5까지는 range(1, 6)", "range(1, 5)는 4에서 끝나요. 끝 숫자는 늘 빠져요.", None, ' data-build-in="rise order 3"', "gap:8px"))
o.append(caption("IndexError가 나면 range의 끝 숫자부터 봐요.", 920))
W("t-range", o, "마지막 칸까지 꼭 돌고 싶어서 len에 1을 더하는 실수를 자주 해요. menus는 3칸이라 번호는 0, 1, 2이고 len은 3이에요. range(3)이 이미 0, 1, 2라서 딱 맞아요. 1을 더하면 3번 칸을 꺼내려다 IndexError가 나요. 오류가 나기 전까지 coffee, latte, cake는 찍혀요. 반대로 1부터 5까지 돌고 싶은데 range(1, 5)라고 적으면 4에서 끝나요. 끝 숫자는 늘 빠진다는 2파트의 규칙을 떠올려요." + REAL)

o = [sec("x-stock")] + head(EB6, "재고가 모자랄 때까지 주문을 받아요", K6)
o += cell({"id": "c-x1", "lines": ["stock = 5", "orders = [2, 1, 3, 1]", "sold = 0", "i = 0", "while i < len(orders):", "    want = orders[i]", "    if want > stock:", '        print(f"{i + 1}번 손님 {want}잔: 재고가 {stock}잔뿐이에요")', "        break", "    stock -= want", "    sold += want", '    print(f"{i + 1}번 손님 {want}잔, 남은 재고 {stock}")', "    i += 1", 'print(f"판매 {sold}잔, 남은 재고 {stock}")'], "n": 8,
           "out": ["1번 손님 2잔, 남은 재고 3", "2번 손님 1잔, 남은 재고 2", "3번 손님 3잔: 재고가 2잔뿐이에요", "판매 3잔, 남은 재고 2"]}, 96, 190, 1160, sel="c-x1")
o.append(hl(96, 190, 1160, 6, 3, "err", 1, "모자라면 멈춤"))
o.append(hl(96, 190, 1160, 12, 1, "mark", 2, "값 바꾸기"))
o += table(1300, 190, 524, [("손님", 90), ("want", 100), ("stock", 110), ("", 110)],
           [("1번", "2", "5→3", "팔아요"), ("2번", "1", "3→2", "팔아요"), ("3번", "3", "2", "break")], 3, K4, 70, hi=(2,))
o.append(note_card(1300, 470, 524, 400, "배운 것을 섞었어요", "while과 번호 i로 손님을 차례로 받아요. if로 재고를 확인하고, 모자라면 break해요. 번호 i는 0부터라 손님에게는 i + 1로 보여 줘요.", K6, ' data-build-in="rise order 4"'))
o.append(caption("멈출 조건이 두 개면 하나는 while에, 하나는 if와 break로 적어요.", 970))
W("x-stock", o, "재고 5잔으로 손님 주문을 차례로 받아요. 손님이 원하는 잔 수는 orders 리스트에 있어요. while은 i가 손님 수보다 작은 동안 돌아요. 손님마다 원하는 잔 수가 재고보다 많으면 재고가 모자란다고 알리고 break해요. 아니면 재고에서 빼고 판매에 더하고, i를 1 늘려 다음 손님으로 가요. 3번 손님은 3잔을 원하는데 2잔뿐이라 멈춰요. 멈추는 이유가 두 가지라서 하나는 while 조건에, 하나는 if와 break로 적었어요." + REAL)

o = [sec("x-soldout")] + head(EB6, "처음 품절이 나오면 주문을 멈춰요", K6)
o += cell({"id": "c-x2", "lines": ['stock = {"coffee": 2, "latte": 1, "cake": 3}', 'orders = ["coffee", "latte", "coffee", "latte", "cake"]', "for o in orders:", "    if stock[o] == 0:", '        print(f"{o} 품절이에요. 주문을 멈춰요")', "        break", "    stock[o] -= 1", '    print(f"{o} 나갔어요. 남은 수 {stock[o]}")', "print(stock)"], "n": 9,
           "out": ["coffee 나갔어요. 남은 수 1", "latte 나갔어요. 남은 수 0", "coffee 나갔어요. 남은 수 0", "latte 품절이에요. 주문을 멈춰요", "{'coffee': 0, 'latte': 0, 'cake': 3}"]}, 96, 190, 1100, sel="c-x2")
o.append(hl(96, 190, 1100, 3, 3, "err", 1, "품절이면 break"))
o.append(hl(96, 190, 1100, 6, 1, "mark", 2, "15 · 값 바꾸기"))
o.append(slots(["coffee", "latte", "coffee", "latte", "cake"], 1250, 190, 104, 70, hi=(0, 1, 2), attrs=' data-build-in="rise order 3"', fs=17, color=K6, bg=K6BG))
o.append(note_card(1250, 330, 574, 280, "cake는 받지 않았어요", "넷째 주문 latte가 품절이라 break했어요. 다섯째 cake는 재고가 있어도 보지 않아요.", RED, ' data-build-in="rise order 3"'))
o.append(note_card(1250, 640, 574, 230, "멈추지 않으려면", "break 대신 continue를 쓰면 품절만 건너뛰고 cake도 받아요.", K6, ' data-build-in="rise order 4"', "gap:8px"))
o.append(caption("break는 \"여기서 그만\", 4파트처럼 continue로 바꾸면 \"이것만 빼고\"예요.", 960))
W("x-soldout", o, "메뉴별 재고 딕셔너리와 주문 리스트가 있어요. 주문을 하나씩 꺼내 재고가 0인지 물어요. 0이 아니면 15에서 배운 대로 stock[o] -= 1로 재고를 줄여요. latte는 둘째 주문에서 마지막 하나가 나가 0이 됐어요. 넷째 주문이 다시 latte라서 품절이에요를 찍고 break해요. 그래서 다섯째 cake는 재고가 있어도 받지 않았어요. break를 continue로 바꿔 실행해 보면 cake까지 받는 걸 확인할 수 있어요." + REAL)

o = [sec("x-gugu")] + head(EB6, "구구단 표를 한 번에 찍어요", K6)
o += cell({"id": "c-x3", "lines": ["for dan in range(2, 10):", '    print(f"{dan}단", end=" ")', "    for i in range(1, 10):", '        print(f"{dan * i:>3}", end="")', "    print()"], "n": 10,
           "out": ["2단   2  4  6  8 10 12 14 16 18", "3단   3  6  9 12 15 18 21 24 27", "4단   4  8 12 16 20 24 28 32 36", "5단   5 10 15 20 25 30 35 40 45", "6단   6 12 18 24 30 36 42 48 54", "7단   7 14 21 28 35 42 49 56 63", "8단   8 16 24 32 40 48 56 64 72", "9단   9 18 27 36 45 54 63 72 81"], "wide": True}, 96, 190, 1000, sel="c-x3")
o.append(hl(96, 190, 1000, 1, 1, "mark", 1, "줄 앞머리"))
o.append(hl(96, 190, 1000, 3, 1, "run", 2, "줄 안 9칸"))
o.append(hl(96, 190, 1000, 4, 1, "mark", 3, "줄 바꾸기"))
pt = [('end=""', "줄을 바꾸지 않고 이어 찍기 (13)"), ("{dan * i:>3}", "3칸 오른쪽 맞춤 (13)"), ("print()", "아무것도 안 찍고 줄만 바꾸기")]
for i, (k, d) in enumerate(pt):
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:1150px;top:{190 + i * 150}px;width:674px;height:130px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:16px 24px;display:flex;flex-direction:column;justify-content:center;gap:10px">'
             + mono(k, 26, K6, K6BG, "align-self:flex-start") + p(f"font-size:24px;font-weight:700;color:{INK}", e(d)) + '</div>')
o.append(note_card(1150, 650, 674, 220, "바깥 8번 × 안쪽 9번", "안쪽이 한 줄을 채우고, 바깥이 줄을 바꿔요.", K6, ' data-build-in="rise order 4"', "gap:8px"))
o.append(caption("안쪽 for는 한 줄을, 바깥 for는 줄 수를 맡아요.", 960))
W("x-gugu", o, "5파트의 겹친 반복으로 2단부터 9단까지 표를 찍어요. 바깥 for는 단, 안쪽 for는 곱하는 수예요. 줄 앞에 몇 단인지 찍고, 13에서 배운 end로 줄을 바꾸지 않아요. 안쪽에서 곱한 값을 3칸 오른쪽 맞춤으로 이어 찍어서 칸이 맞아요. 안쪽 for가 끝나면 괄호만 있는 print()로 줄을 바꿔요. print()는 아무것도 찍지 않고 줄만 바꿔요. 출력의 한글은 영어 두 칸 너비로 그렸어요." + REAL)

o = [sec("x-guess")] + head(EB6, "숫자 맞히기, 맞히면 멈춰요", K6)
o += cell({"id": "c-x4", "lines": ["answer = 37", "guesses = [50, 25, 37, 40]", "tries = 0", "for g in guesses:", "    tries += 1", "    if g == answer:", '        print(f"{g}: 정답이에요. {tries}번 만에 맞혔어요")', "        break", "    elif g > answer:", '        print(f"{g}: 더 작아요")', "    else:", '        print(f"{g}: 더 커요")'], "n": 11,
           "out": ["50: 더 작아요", "25: 더 커요", "37: 정답이에요. 3번 만에 맞혔어요"]}, 96, 190, 1100, sel="c-x4")
o.append(hl(96, 190, 1100, 5, 3, "run", 1, "맞히면 break"))
o.append(hl(96, 190, 1100, 8, 4, "mark", 2, "17 · elif로 힌트"))
o.append(slots(["50", "25", "37", "40"], 1250, 190, 120, 80, hi=(0, 1, 2), attrs=' data-build-in="rise order 3"', fs=30, color=K6, bg=K6BG))
o.append(note_card(1250, 330, 574, 280, "40은 말하지 않았어요", "셋째에 맞혀서 break했어요. 넷째 추측 40은 보지 않아요.", GR, ' data-build-in="rise order 3"'))
o.append(note_card(1250, 640, 574, 230, "추측을 바꿔 봐요", "guesses를 [10, 90, 50]처럼 바꾸면 끝까지 못 맞히고 힌트만 찍혀요.", None, ' data-build-in="rise order 4"', "gap:8px"))
o.append(caption("17의 elif로 힌트를 주고, 맞히면 break로 끝내요.", 960))
W("x-guess", o, "정해진 추측 리스트로 숫자 맞히기를 해요. 입력은 아직 배우지 않아서 추측을 리스트에 미리 적었어요. 추측마다 시도 횟수를 1 늘리고 17의 if, elif, else로 비교해요. 같으면 정답이라고 찍고 break해요. 크면 더 작다, 작으면 더 크다고 힌트를 줘요. 셋째 추측 37에서 맞혀서 넷째 40은 보지 않아요. guesses를 바꿔 끝까지 못 맞히는 경우도 실행해 봐요." + REAL)

# ---------- summary ----------
o = [sec("trouble")] + head("정리", "막히면 오류의 마지막 줄을 봐요", RED)
tr = [("셀이 끝나지 않고 출력이 계속 나와요", "while 조건이 늘 True예요. 값 바꾸기를 빠뜨렸어요", "■ 또는 Interrupt"),
      ("KeyboardInterrupt", "직접 멈춘 거예요. 오류가 아니에요", "값 바꾸기 줄 넣기"),
      ("IndexError: list index out of range", "range(len(리스트) + 1)처럼 칸을 넘었어요", "range(len(xs))"),
      ("1부터 5까지 도는데 4에서 끝나요", "range의 끝 숫자는 빠져요", "range(1, 6)"),
      ("지웠는데 하나가 남아요", "돌고 있는 리스트를 remove했어요", "새 리스트에 append"),
      ("합계가 마지막 값만 나와요", "total = 0을 for 안에 넣었어요", "for 위로 옮기기"),
      ("바깥 반복이 멈추지 않아요", "break는 가장 가까운 반복 하나만 끝내요", "어느 for 안인지 보기")]
o.append('<div style="position:absolute;left:96px;top:196px;width:1728px;height:724px;display:flex;flex-direction:column;gap:8px">')
for i, (q, a_, cmd) in enumerate(tr, 1):
    o.append(f'<div data-build-in="rise order {min(i, 6)}" style="flex:1;display:flex;flex-direction:row;gap:26px;align-items:center;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:6px 30px">'
             + num(i, RED, 30)
             + '<div style="flex:1;display:flex;flex-direction:column;gap:2px">' + p(f"{'font-family:' + MONO + ';' if q.isascii() else ''}font-size:22px;font-weight:700;color:{INK};white-space:nowrap", e(q)) + p(f"font-size:21px;color:{SUB}", e(a_)) + '</div>'
             + p(f"width:380px;flex:none;{'font-family:' + MONO + ';font-size:22px;' if cmd.isascii() else 'font-size:23px;'}font-weight:700;line-height:1.4;color:{INK};background:#EEEFF2;padding:6px 18px;border-radius:12px;white-space:pre", e(cmd)) + '</div>')
o.append('</div>')
o.append(caption("결과가 이상하면 반복 안에 print를 넣어 값이 어떻게 바뀌는지 찍어 봐요.", 950))
W("trouble", o, "반복에서 자주 만나는 일을 모았어요. 1번과 2번은 무한 반복이에요. 정지 버튼으로 멈추고 값 바꾸기 줄을 넣어요. KeyboardInterrupt는 내가 멈춘 표시라 오류가 아니에요. 3번과 4번은 range의 끝 숫자 문제예요. 5번부터 7번은 오류 없이 결과만 이상한 경우예요. 이럴 때는 반복 안에 print를 넣어 변수가 어떻게 바뀌는지 찍어 보면 원인이 보여요.", ("trouble", "정리"))

o = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>']
cheat = [("range(1, 6)", "1부터 5까지, 끝은 빠져요", K2), ("for i in range(n):", "n번 반복", K2), ("enumerate(xs, 1)", "번호와 값을 같이", K2), ("while 조건:", "True인 동안 반복", K3),
         ("break", "반복을 바로 끝내기", K4), ("continue", "이번 차례만 넘기기", K4), ("total += p", "0에서 시작해 쌓기", K5), ("for 안의 for", "표 만들기, 2차원 리스트", K5)]
for i, (k, d, c) in enumerate(cheat):
    x, y = 96 + (i % 4) * 438, 200 + (i // 4) * 290
    o.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:414px;height:264px;background:{CARD};border:2px solid {LINE};border-top:10px solid {c};border-radius:20px;padding:28px 28px;display:flex;flex-direction:column;gap:20px">'
             + mono(k, 26 if len(k) <= 17 else 22, c, "#F6F5F1", "align-self:flex-start") + p(f"font-size:28px;font-weight:700;color:{INK}", d) + '</div>')
o.append(f'<div style="position:absolute;left:96px;top:780px;width:1728px;height:210px;background:{CARD};border:2px solid {LINE};border-radius:20px;padding:24px 36px;display:flex;flex-direction:column;justify-content:center;gap:14px">'
         + p(f"font-size:30px;font-weight:700;color:{INK}", "횟수를 알면 for, 조건만 알면 while")
         + p(f"font-size:30px;font-weight:700;color:{INK}", "while에는 시작값, 조건, 값 바꾸기 세 가지가 꼭 있어야 해요") + '</div>')
W("cheatsheet", o, "이번 챕터에서 쓴 모양을 한 장에 모았어요. range는 끝 숫자가 빠져요. 정한 횟수는 for와 range, 번호와 값은 enumerate, 조건이 맞는 동안은 while이에요. break는 반복을 끝내고, continue는 이번 차례만 넘겨요. 합계, 개수, 최댓값은 반복 밖에서 시작값을 두고 안에서 쌓아요. 17과 18로 제어문을 마쳤어요. 이 장을 노트북 마크다운 셀에 정리해 두면 복습할 때 같이 봐요.")

# ---------- toc ----------
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
parts = [("Lightbulb", K1, "왜 필요한가", "몇 번 돌지 모르는 장면, for와 while 그림, 가장 짧은 while", "w-why", "w-min"),
         ("Code", K2, "range와 번호", "range(5), 시작과 끝과 간격, for i in range, range(len()), enumerate", "r-range", "r-enum"),
         ("Activity", K3, "while", "묻기, 실행, 값 바꾸기, 재고 줄이기, 무한 반복과 멈추는 법, for와 비교", "w-shape", "w-vs"),
         ("Wrench", K4, "break와 continue", "같은 주문으로 break와 continue, 점프 화살표, else로 길게 쓰기, while True", "b-break", "b-true"),
         ("Database", K5, "쌓기와 겹친 반복", "합계, 세기와 모으기, 최댓값, 구구단, 2차원 리스트, 안쪽 break", "a-sum", "n-break"),
         ("Star", K6, "함정과 실습", "돌면서 지우기, 들여쓰기, range 끝, 재고, 품절, 구구단 표, 숫자 맞히기", "t-remove", "x-guess")]
TOC_NOTE = "여섯 파트로 나눴어요. 1파트는 while이 왜 필요한지와 큰 그림, 2파트는 range와 번호예요. 3파트는 while 모양과 무한 반복, 4파트는 같은 주문 리스트로 break와 continue를 비교해요. 5파트는 합계, 개수, 최댓값을 직접 쌓고 sum, max와 비교한 뒤 반복을 겹쳐요. 6파트는 함정과 카페 실습이에요. 파트마다 새 커널에서 위에서부터 차례로 실행해요."

DECK_TITLE = "제어문 2 (반복 제어 while, break)"
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
