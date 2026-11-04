"""Generates every slide of the list comprehension deck (23) and slides/deck.json.

Story: keeps writing in basics.ipynb from chapters 12-22. Starts from the long for-and-append block and the nested
map/lambda of chapter 21, draws how the value, the for and the if move into the brackets, then the three ways side by
side, reading order, an if at the end (keep), an if-else in front (change), strings, range, tuples, dictionary and set
comprehensions, sum, max and sorted with comprehensions, and when a plain for reads better (a nested comprehension is
shown for reading only). Part 5 collects the usual errors, and part 6 makes a receipt, a stock board and a score sheet.
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
EB2 = "2. 만들기와 고르기"
EB3 = "3. 여러 데이터에 쓰기"
EB4 = "4. 함수와 함께 쓰기"
EB5 = "5. 오류와 함정"
EB6 = "6. 실습"
PR4 = "prices = [4500, 5000, 6500, 3000]"
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

# ---------- cover ----------
cover([(PR4, W_), ("", W_), ("[p + 500 for p in prices]", "#8FD8DE"), ("# [5000, 5500, 7000, 3500]", "#9AA1AE"), ("", W_),
       ("[p for p in prices if p >= 5000]", "#E3B877"), ("# [5000, 6500]", "#9AA1AE")],
      "리스트<br>컴프리헨션", "바꾸고 고르는 for를<br>대괄호 한 줄로 쓰기",
      "21에서 map과 filter로 리스트 전체를 바꾸고 골랐어요. 이번에는 같은 일을 대괄호 안에 for를 넣어 한 줄로 써요. 이 모양을 리스트 컴프리헨션이라고 불러요. lambda 없이 읽혀서 파이썬에서 가장 많이 쓰는 방법이에요. 딕셔너리와 집합도 같은 모양으로 만들고, 22의 sorted, max와 함께 써요.")

ready([("리스트, 튜플, for, append, join", "13"), ("딕셔너리 items(), 집합", "15, 16"), ("if, 한 줄 if else", "17"), ("range()", "18"), ("lambda, map, filter, sorted의 key", "21, 22")], "22",
      "09에서 만든 hello-uv 폴더를 VS Code로 열고, 12부터 쓰던 basics.ipynb를 다시 열어요. 13의 for와 append, 17의 if와 한 줄 if else, 18의 range를 대괄호 안에 넣어요. 21의 map, filter와 나란히 비교하고, 22의 sorted, max와 함께 써요. 슬라이드의 출력은 tools/demo.sh가 hello-uv 커널에서 같은 셀을 실제로 실행한 결과예요. 셀 번호는 파트마다 [1]부터 다시 셌어요.")

# ---------- part 1 ----------
o = [sec("c-why")] + head(EB1, "for는 길고, map은 lambda까지 읽어야 해요", K1)
o += cell({"id": "c-why", "lines": ["prices = [4500, 5000, 6500]", "up = []", "for p in prices:", "    up.append(p + 500)", "print(up)", "print(list(map(lambda p: p + 500, prices)))"], "n": 1, "out": ["[5000, 5500, 7000]", "[5000, 5500, 7000]"]}, 96, 200, 1100, sel="c-why")
o.append(hl(96, 200, 1100, 1, 3, "mark", 1, "네 줄"))
o.append(hl(96, 200, 1100, 5, 1, "skip", 2, "괄호가 겹쳐요"))
o.append(note_card(1240, 200, 584, 300, "for와 append", "읽기는 쉬운데 빈 리스트, for, append 세 줄을 매번 적어요.", K1, ' data-build-in="rise order 3"'))
o.append(note_card(1240, 530, 584, 330, "map과 lambda", "한 줄이지만 list, map, lambda를 차례로 풀어 읽어야 해요.", OR, ' data-build-in="rise order 4"'))
o.append(caption("한 줄로 쓰면서 for처럼 바로 읽히는 방법이 있어요.", 930))
W("c-why", o, "21의 장면으로 돌아가요. 모든 가격에 500원을 더할 때 for와 append로 쓰면 읽기는 쉬운데 빈 리스트 만들기, for, append를 매번 적어요. map과 lambda로 쓰면 한 줄이지만 list 안에 map, map 안에 lambda가 있어서 괄호를 풀어 가며 읽어야 해요. 한 줄로 쓰면서도 for처럼 바로 읽히는 방법이 리스트 컴프리헨션이에요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p1", "왜 필요한가"))

o = [sec("c-big")] + head(EB1, "for의 세 조각을 대괄호 안에 옮겨 적어요", K1)
o.append(label("for로 쓰면", 96, 196, GRAY, "", 800, 26))
o.append(dark(96, 240, 800, 330, [seg([("up = []", W_)], 34), seg([("for p in prices:", CF)], 34), seg([("    if p >= 5000:", CI)], 34), seg([("        up.append(", W_), ("p + 500", CV), (")", W_)], 34)]))
o.append(label("컴프리헨션으로 쓰면", 960, 196, K1, ' data-build-in="fade order 1"', 860, 26))
o.append(dark(960, 240, 864, 330, [seg([("up = [", W_), ("p + 500", CV), (" ", W_)], 34), seg([("      ", W_), ("for p in prices", CF)], 34), seg([("      ", W_), ("if p >= 5000", CI), ("]", W_)], 34)], ' data-build-in="rise order 1"'))
for i, (k, d, c) in enumerate([("p + 500", "① 넣을 값. append 괄호 안에 있던 것", LV), ("for p in prices", "② 하나씩 꺼내기. 콜론은 빼요", LF), ("if p >= 5000", "③ 고르기. 필요 없으면 빼요", LI)]):
    o.append(callout(96, 600 + i * 100, 1728, 86, k, d, c, i + 2, 26))
W("c-big", o, "for 문을 컴프리헨션으로 옮기는 그림이에요. 왼쪽 for 문에는 세 조각이 있어요. 초록색은 append 괄호 안의 넣을 값, 청록색은 하나씩 꺼내는 for, 빨간색은 고르는 if예요. 컴프리헨션은 대괄호 안에 넣을 값을 맨 앞에 적고, 그 뒤에 for와 if를 콜론 없이 이어 적어요. 빈 리스트와 append는 대괄호가 대신해요. if 조각은 고를 때만 붙여요. 한 줄로 적어도 되지만 그림에서는 조각이 보이게 세 줄로 나눴어요.")

o = [sec("c-min")] + head(EB1, "가장 짧은 컴프리헨션: 값마다 10 더하기", K1)
o += cell({"id": "c-min", "lines": ["numbers = [1, 2, 3]", "print([x + 10 for x in numbers])"], "n": 2, "out": ["[11, 12, 13]"]}, 96, 200, 1000, sel="c-min")
o.append(f'<div data-build-in="rise order 1" style="position:absolute;left:96px;top:420px;width:1000px;height:120px;background:#252B36;border-radius:20px;display:flex;align-items:center;padding:0 40px">'
         + seg([("[", W_), ("x + 10", CV), (" ", W_), ("for x in numbers", CF), ("]", W_)], 44) + '</div>')
o.append(slots(["1", "2", "3"], 96, 600, 140, 84, top_lbl=False, fs=30, color=GRAY, bg="#F1F0EC", attrs=' data-build-in="fade order 2"'))
o.append(f'<x-shape data-build-in="fade order 3" kind="arrow-right" style="position:absolute;left:560px;top:628px;width:60px;height:30px;background:{K1}"></x-shape>')
o.append(slots(["11", "12", "13"], 640, 600, 140, 84, top_lbl=False, fs=30, color=K1, bg=K1BG, hi=(0, 1, 2), attrs=' data-build-in="fade order 3"'))
o.append(note_card(1150, 200, 674, 300, "21과 같은 결과", "list(map(lambda x: x + 10, numbers))와 같아요. list도 lambda도 없어요.", K1, ' data-build-in="rise order 4"'))
o.append(note_card(1150, 530, 674, 330, "읽는 법", "numbers에서 x를 하나씩 꺼내, x + 10을 모은 리스트예요.", GR, ' data-build-in="rise order 5"'))
o.append(caption("[넣을 값 for 이름 in 리스트]는 값마다 계산한 새 리스트예요.", 930))
W("c-min", o, "21의 첫 예제를 컴프리헨션으로 써요. 대괄호 안에 x + 10 for x in numbers라고 적어요. numbers에서 x를 하나씩 꺼내 x + 10을 계산하고, 그 값을 모아 새 리스트를 만들어요. 결과는 21의 list(map(lambda x: x + 10, numbers))와 같은 [11, 12, 13]이에요. list와 lambda가 없어서 소리 내어 읽은 순서와 거의 같아요." + REAL)

# ---------- part 2 ----------
o = [sec("b-three")] + head(EB2, "같은 일을 세 가지로 써요", K2)
o += cell({"id": "c-b1", "lines": [PR4, "up = []", "for p in prices:", "    up.append(p + 500)", "print(up)", "print(list(map(lambda p: p + 500, prices)))", "print([p + 500 for p in prices])"], "n": 1, "out": ["[5000, 5500, 7000, 3500]", "[5000, 5500, 7000, 3500]", "[5000, 5500, 7000, 3500]"]}, 96, 200, 1100, sel="c-b1")
o.append(hl(96, 200, 1100, 1, 3, "mark", 1, "13의 for"))
o.append(hl(96, 200, 1100, 5, 1, "skip", 2, "21의 map"))
o.append(hl(96, 200, 1100, 6, 1, "run", 3, "컴프리헨션"))
o += table(1240, 200, 584, [("방법", 200), ("줄 수", 100), ("lambda", 130)], [("for", "4줄", "없어요"), ("map", "1줄", "있어요"), ("컴프리헨션", "1줄", "없어요")], 4, K2, 70, hi=(2,))
o.append(note_card(1240, 500, 584, 360, "결과는 셋 다 같아요", "새 리스트를 만들고 prices는 그대로예요. 짧고 바로 읽히는 컴프리헨션을 가장 많이 써요.", K2, ' data-build-in="rise order 7"'))
W("b-three", o, "1파트의 가격에 3000원짜리를 하나 더해서 세 방법을 한 셀에 나란히 적었어요. 13의 for와 append, 21의 map과 lambda, 그리고 컴프리헨션이에요. 결과는 셋 다 같아요. for는 네 줄, map은 한 줄이지만 lambda를 읽어야 하고, 컴프리헨션은 한 줄에 lambda도 없어요. 셋 다 새 리스트를 만들고 prices는 바꾸지 않아요. 파이썬 코드에서는 컴프리헨션을 가장 자주 봐요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p2", "만들기와 고르기"))

o = [sec("b-read")] + head(EB2, "뒤의 for부터 읽고, 앞의 값을 모아요", K2)
o.append(f'<div style="position:absolute;left:96px;top:200px;width:1728px;height:130px;background:#252B36;border-radius:20px;display:flex;align-items:center;justify-content:center;padding:0 40px">'
         + seg([("[", W_), ("p + 500", CV), (" ", W_), ("for p in prices", CF), ("]", W_)], 52) + '</div>')
o.append(callout(96, 370, 846, 130, "① for p in prices", "prices에서 p를 하나 꺼내요", LF, 1, 26))
o.append(callout(978, 370, 846, 130, "② p + 500", "꺼낸 p로 값을 계산해 모아요", LV, 2, 26))
o += table(96, 540, 1728, [("꺼낸 p", 300), ("p + 500", 300), ("모인 리스트", 800)],
           [("4500", "5000", "[5000]"), ("5000", "5500", "[5000, 5500]"), ("6500", "7000", "[5000, 5500, 7000]"), ("3000", "3500", "[5000, 5500, 7000, 3500]")], 3, K2, 58)
W("b-read", o, "읽는 순서를 봐요. 적은 순서는 값이 먼저지만, 실제로는 뒤의 for부터 움직여요. prices에서 p를 하나 꺼내고, 그 p로 앞의 p + 500을 계산해 리스트에 모아요. 아래 표처럼 4500을 꺼내 5000을 모으고, 5000을 꺼내 5500을 모아요. 네 값을 다 꺼내면 대괄호 안의 리스트가 완성돼요. 처음에는 for 부분을 먼저 읽고, 앞으로 돌아와 무엇을 모으는지 보면 쉬워요.")

o = [sec("b-filter")] + head(EB2, "뒤에 if를 붙이면 골라 담아요", K2)
o += cell({"id": "c-b2", "lines": ["big = []", "for p in prices:", "    if p >= 5000:", "        big.append(p)", "print(big)", "print(list(filter(lambda p: p >= 5000, prices)))", "print([p for p in prices if p >= 5000])"], "n": 2, "out": ["[5000, 6500]", "[5000, 6500]", "[5000, 6500]"]}, 96, 200, 1100, sel="c-b2")
o.append(hl(96, 200, 1100, 0, 4, "mark", 1, "17의 골라 담기"))
o.append(hl(96, 200, 1100, 5, 1, "skip", 2, "21의 filter"))
o.append(hl(96, 200, 1100, 6, 1, "run", 3, "if를 뒤에"))
o.append(f'<div data-build-in="rise order 4" style="position:absolute;left:1240px;top:200px;width:584px;height:150px;background:#252B36;border-radius:20px;display:flex;align-items:center;justify-content:center">'
         + seg([("[", W_), ("p", CV), (" ", W_), ("for p in prices", CF), (" ", W_), ("if p >= 5000", CI), ("]", W_)], 26) + '</div>')
o.append(note_card(1240, 380, 584, 230, "값은 p 그대로", "바꾸지 않고 고르기만 해서 넣을 값이 p예요.", K2, ' data-build-in="rise order 5"'))
o.append(note_card(1240, 640, 584, 220, "if가 True일 때만", "if 뒤 조건이 True인 p만 모여요.", LI, ' data-build-in="rise order 6"'))
W("b-filter", o, "17에서 for 안의 if로 골라 담던 일이에요. 21에서는 filter로 썼어요. 컴프리헨션은 for 뒤에 if를 이어 붙여요. 조건이 True인 p만 모여요. 이번에는 값을 바꾸지 않고 고르기만 하니까 넣을 값 자리에 p를 그대로 적어요. p for p in이 같은 말을 되풀이하는 것 같지만, 앞의 p는 넣을 값이고 뒤의 p는 꺼낸 이름이에요. 세 방법 모두 [5000, 6500]이에요." + REAL)

o = [sec("b-both")] + head(EB2, "고르고 바꾸기를 한 번에 해요", K2)
o += cell({"id": "c-b3", "lines": ["print([p * 9 // 10 for p in prices if p >= 5000])", "print(list(map(lambda p: p * 9 // 10, filter(lambda p: p >= 5000, prices))))"], "n": 3, "out": ["[4500, 5850]", "[4500, 5850]"]}, 96, 200, 1728, sel="c-b3")
o.append(hl(96, 200, 1728, 0, 1, "run", 1, "컴프리헨션"))
o.append(hl(96, 200, 1728, 1, 1, "skip", 2, "21의 겹쳐 쓰기"))
o += pipe(96, 440, ["4500", "5000", "6500", "3000"], "if p >= 5000", ["4500", "5000", "6500", "3000"], LI, "#F8E6E6", 3, 180, keep=[False, True, True, False])
o.append(f'<div data-build-in="rise order 6" style="position:absolute;left:880px;top:672px;width:300px;height:90px;display:flex;flex-direction:row;align-items:center;gap:14px">' + arrow(50, LV) + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{LV}", "p * 9 // 10") + '</div>')
o.append(slots(["4500", "5850"], 1200, 672, 180, 90, top_lbl=False, fs=30, color=LV, bg="#E6F4EC", hi=(0, 1), attrs=' data-build-in="rise order 6"'))
o.append(caption("if로 고른 값만 앞의 식으로 바꿔서 모아요.", 930))
W("b-both", o, "21에서 5000원 이상만 골라 10% 할인할 때 filter를 map 안에 넣어 괄호가 겹쳤어요. 컴프리헨션은 앞에 바꿀 식, 뒤에 고를 조건을 적으면 돼요. 그림처럼 if가 4500과 3000을 걸러 내고, 남은 5000과 6500만 9를 곱하고 10으로 몫 나누기해요. 결과는 같은데 한 줄이 훨씬 짧고 왼쪽부터 읽혀요." + REAL)

o = [sec("b-ifelse")] + head(EB2, "앞에 한 줄 if else를 넣으면 값을 바꿔 적어요", K2)
o += cell({"id": "c-b4", "lines": ['print(["비쌈" if p >= 5000 else "보통" for p in prices])'], "n": 4, "out": ["['보통', '비쌈', '비쌈', '보통']"]}, 96, 200, 1300, sel="c-b4")
o.append(f'<div data-build-in="rise order 1" style="position:absolute;left:96px;top:360px;width:1728px;height:130px;background:#252B36;border-radius:20px;display:flex;align-items:center;justify-content:center">'
         + seg([("[", W_), ('"비쌈" if p >= 5000 else "보통"', CV), (" ", W_), ("for p in prices", CF), ("]", W_)], 40) + '</div>')
o += table(96, 530, 1100, [("p", 200), ("p >= 5000", 260), ("넣을 값", 300)], [("4500", "False", '"보통"'), ("5000", "True", '"비쌈"'), ("6500", "True", '"비쌈"'), ("3000", "False", '"보통"')], 2, K2, 56)
o.append(note_card(1240, 530, 584, 330, "17의 한 줄 if else", "값1 if 조건 else 값2는 값 하나라서 넣을 값 자리에 들어가요.", K2, ' data-build-in="rise order 6"'))
W("b-ifelse", o, "이번에는 고르지 않고 모든 가격에 이름표를 붙여요. 17에서 배운 한 줄 if else, 곧 값1 if 조건 else 값2를 넣을 값 자리에 넣어요. 조건이 True면 비쌈, False면 보통이 모여요. 개수는 네 개 그대로예요. 21에서 lambda에 한 줄 if else를 넣었던 것과 같은 이유예요. 한 줄 if else는 값 하나로 계산되니까 값 자리에 쓸 수 있어요." + REAL)

o = [sec("b-pos")] + head(EB2, "if가 뒤에 있으면 고르기, 앞에 있으면 바꾸기", K2)
o += cell({"id": "c-b5", "lines": ["print([p for p in prices if p >= 5000])", "print([p if p >= 5000 else 0 for p in prices])"], "n": 5, "out": ["[5000, 6500]", "[0, 5000, 6500, 0]"]}, 96, 200, 1100, sel="c-b5")
o.append(side(96, 420, 846, 210, "뒤의 if", ["[p for p in prices if p >= 5000]", "# [5000, 6500]"], [], LI, "#F8E6E6", ' data-build-in="rise order 1"', 24, "고르기"))
o.append(side(978, 420, 846, 210, "앞의 if else", ["[p if p >= 5000 else 0 for p in prices]", "# [0, 5000, 6500, 0]"], [], LV, "#E6F4EC", ' data-build-in="rise order 2"', 24, "바꾸기"))
o.append(note_card(96, 660, 846, 200, "조건에 맞는 값만 남아요", "else를 쓰지 않고, 개수가 줄어요.", LI, ' data-build-in="rise order 1"'))
o.append(note_card(978, 660, 846, 200, "모든 값을 바꿔 적어요", "else가 꼭 있어야 하고, 개수가 그대로예요.", LV, ' data-build-in="rise order 2"'))
o.append(note_card(1240, 200, 584, 190, "자리로 구분해요", "for보다 뒤인지 앞인지 봐요.", K2, ' data-build-in="rise order 3"'))
W("b-pos", o, "if가 들어갈 자리가 두 곳이라 헷갈리기 쉬워요. for 뒤에 붙은 if는 고르기예요. 조건에 맞는 값만 남아서 개수가 줄고, else를 쓰지 않아요. 넣을 값 자리, 곧 for 앞에 들어간 if else는 바꾸기예요. 모든 값을 조건에 따라 바꿔 적어서 개수가 그대로이고, else가 꼭 있어야 해요. 5000원 미만을 0으로 바꾼 결과와 골라낸 결과를 비교해 보세요. 자리를 바꿔 쓰면 생기는 오류는 5파트에서 봐요." + REAL)

# ---------- part 3 ----------
o = [sec("r-str")] + head(EB3, "길이, 글자, range로도 만들어요", K3)
o += cell({"id": "c-r1", "lines": ['names = ["latte", "tea", "coffee"]', "print([len(m) for m in names])", "print([m[0] for m in names])", "print([n * n for n in range(1, 6)])"], "n": 1, "out": ["[5, 3, 6]", "['l', 't', 'c']", "[1, 4, 9, 16, 25]"]}, 96, 200, 1000, sel="c-r1")
o.append(row_card(96, 560, 1728, 96, "[len(m) for m in names]", "[5, 3, 6]", "함수를 불러도 돼요. 21의 map(len, names)와 같아요", 1, K3, K3BG, 520))
o.append(row_card(96, 670, 1728, 96, "[m[0] for m in names]", "['l', 't', 'c']", "13의 글자 꺼내기. 첫 글자만 모아요", 2, K3, K3BG, 520))
o.append(row_card(96, 780, 1728, 96, "[n * n for n in range(1, 6)]", "[1, 4, 9, …]", "18의 range로 숫자를 만들며 계산해요", 3, K3, K3BG, 520))
o.append(note_card(1150, 200, 674, 320, "in 뒤에는 for에 쓰던 것", "리스트, 글자, range처럼 for로 돌 수 있는 건 모두 넣을 수 있어요.", K3, ' data-build-in="rise order 4"'))
W("r-str", o, "넣을 값 자리에는 계산뿐 아니라 함수 호출도 올 수 있어요. len(m)을 적으면 이름마다 길이를 모아요. 21의 map(len, names)와 같은 결과예요. m[0]은 13에서 배운 글자 꺼내기라서 첫 글자만 모여요. in 뒤에는 for에 쓰던 것이면 무엇이든 와요. 18의 range(1, 6)을 넣으면 1부터 5까지 제곱한 리스트가 돼요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p3", "여러 데이터에 쓰기"))

o = [sec("r-tuple")] + head(EB3, "튜플 리스트는 꺼내 담기로 이름을 붙여요", K3)
OR_ = ['orders = [("kim", "latte", 2), ("lee", "cake", 1), ("park", "coffee", 3), ("kim", "tea", 1)]', "print([o[0] for o in orders])", "print([menu_name for name, menu_name, qty in orders if qty >= 2])"]
o += cell({"id": "c-r2", "lines": OR_, "n": 2, "out": ["['kim', 'lee', 'park', 'kim']", "['latte', 'coffee']"]}, 96, 200, 1728, sel="c-r2")
o.append(hl(96, 200, 1728, 1, 1, "mark", 1, "번호로 꺼내기"))
o.append(hl(96, 200, 1728, 2, 1, "run", 2, "이름 붙여 꺼내기"))
o.append(row(96, 470, 1728, 110, small("튜플 하나", GRAY, 24, 160) + '<div style="display:flex;flex-direction:row;gap:8px">'
             + "".join(chip(t, c, b, 28) for t, c, b in [('"kim"', GRAY, "#F1F0EC"), ('"latte"', K3, K3BG), ("2", OR, "#F7EEDD")]) + '</div>' + arrow(50, K3)
             + '<div style="display:flex;flex-direction:row;gap:8px">' + "".join(chip(t, c, b, 28) for t, c, b in [("name", GRAY, "#F1F0EC"), ("menu_name", K3, K3BG), ("qty", OR, "#F7EEDD")]) + '</div>', 3))
o.append(note_card(96, 620, 846, 250, "13의 for name, menu_name, qty in", "for에서 쓰던 꺼내 담기를 그대로 써요. 번호 대신 이름으로 읽혀요.", K3, ' data-build-in="rise order 4"'))
o.append(note_card(978, 620, 846, 250, "21의 filter와 map을 한 줄에", "2잔 이상 주문만 고르고, 메뉴 이름만 꺼냈어요.", OR, ' data-build-in="rise order 5"'))
W("r-tuple", o, "21의 튜플 주문 기록을 다시 써요. o[0]처럼 번호로 꺼내도 되지만, 13에서 for name, menu_name, qty in orders:로 꺼내 담았던 것처럼 컴프리헨션의 for에도 이름 세 개를 적을 수 있어요. 그러면 qty >= 2처럼 이름으로 조건을 읽을 수 있어요. 2잔 이상인 주문만 고르고 메뉴 이름만 모았어요. 21에서는 filter와 map 두 번이 필요했던 일이에요. 모두 latte와 coffee예요." + REAL)

o = [sec("r-dict")] + head(EB3, "중괄호와 키: 값으로 딕셔너리도 만들어요", K3)
DC = ['menu = {"coffee": 4500, "latte": 5000, "cake": 6500}', "print({m: p * 11 // 10 for m, p in menu.items()})", 'stock = {"coffee": 3, "latte": 0, "cake": 2}', "print({m: n for m, n in stock.items() if n > 0})", "print([m for m in stock if stock[m] == 0])"]
o += cell({"id": "c-r3", "lines": DC, "n": 3, "out": ["{'coffee': 4950, 'latte': 5500, 'cake': 7150}", "{'coffee': 3, 'cake': 2}", "['latte']"]}, 96, 200, 1100, sel="c-r3")
o.append(hl(96, 200, 1100, 1, 1, "mark", 1))
o.append(hl(96, 200, 1100, 3, 1, "run", 2))
o.append(f'<div data-build-in="rise order 3" style="position:absolute;left:96px;top:620px;width:1100px;height:120px;background:#252B36;border-radius:20px;display:flex;align-items:center;justify-content:center">'
         + seg([("{", W_), ("m", "#E3B877"), (": ", W_), ("p * 11 // 10", CV), (" ", W_), ("for m, p in menu.items()", CF), ("}", W_)], 30) + '</div>')
o.append(note_card(1240, 200, 584, 330, "키: 값을 앞에 적어요", "15의 items()로 키와 값을 꺼내고, 새 키와 새 값을 콜론으로 이어요.", K3, ' data-build-in="rise order 4"'))
o.append(note_card(1240, 560, 584, 300, "키만 필요하면 리스트", "품절 메뉴 이름만 필요하면 대괄호로 리스트를 만들어요.", GRAY, ' data-build-in="rise order 5"'))
o.append(caption("{키: 값 for ...}는 딕셔너리, [값 for ...]는 리스트예요.", 930))
W("r-dict", o, "대괄호 대신 중괄호를 쓰고 넣을 값 자리에 키: 값을 적으면 딕셔너리가 만들어져요. 딕셔너리 컴프리헨션이라고 해요. 15의 items()로 메뉴 이름 m과 가격 p를 꺼내고, 키는 m 그대로, 값은 10% 올린 가격으로 적었어요. if를 붙이면 재고가 있는 메뉴만 남긴 딕셔너리가 돼요. 21의 filter는 키만 남겼는데, 이번에는 재고 숫자까지 같이 남아요. 키만 필요하면 마지막 줄처럼 리스트로 만들어요." + REAL)

o = [sec("r-set")] + head(EB3, "중괄호에 값만 적으면 집합이 돼요", K3)
o += cell({"id": "c-r4", "lines": ["buyers = {o[0] for o in orders}", "print(len(buyers))", "print(sorted(buyers))"], "n": 4, "out": ["3", "['kim', 'lee', 'park']"]}, 96, 200, 1000, sel="c-r4")
o.append(slots(['"kim"', '"lee"', '"park"', '"kim"'], 96, 470, 200, 84, top_lbl=False, fs=26, color=GRAY, bg="#F1F0EC", attrs=' data-build-in="fade order 1"'))
o.append(f'<x-shape data-build-in="fade order 2" kind="arrow-right" style="position:absolute;left:940px;top:497px;width:60px;height:30px;background:{K3}"></x-shape>')
o.append(slots(['"kim"', '"lee"', '"park"'], 1030, 470, 200, 84, top_lbl=False, fs=26, color=K3, bg=K3BG, hi=(0, 1, 2), attrs=' data-build-in="fade order 2"'))
o.append(note_card(1150, 200, 674, 240, "16의 집합 규칙 그대로", "kim이 두 번 주문했지만 한 번만 남아요.", K3, ' data-build-in="rise order 3"'))
o.append(note_card(96, 620, 846, 250, "찍는 순서는 그때그때 달라요", "집합은 순서가 없어서 sorted로 줄 세워 찍었어요.", OR, ' data-build-in="rise order 4"'))
o.append(note_card(978, 620, 846, 250, "괄호 모양으로 구분해요", "[값]은 리스트, {값}은 집합, {키: 값}은 딕셔너리예요.", GRAY, ' data-build-in="rise order 5"'))
W("r-set", o, "중괄호 안에 키: 값이 아니라 값 하나만 적으면 집합이 만들어져요. 주문 기록에서 손님 이름만 모았어요. kim이 두 번 주문했지만 16에서 배운 집합 규칙대로 한 번만 남아서 3명이에요. 집합을 그대로 찍으면 순서가 실행할 때마다 다를 수 있어서 22의 sorted로 줄 세워 찍었어요. 괄호 모양으로 무엇을 만드는지 구분해요. orders는 앞 셀에서 만들었어요." + REAL)

# ---------- part 4 ----------
o = [sec("w-sum")] + head(EB4, "sum, max에 바로 넘겨요", K4)
o += cell({"id": "c-w1", "lines": ['menu = {"coffee": 4500, "latte": 5000, "cake": 6500, "tea": 4000}', 'cart = ["coffee", "cake", "latte", "latte"]', "print(sum([menu[m] for m in cart]))", "print(max([len(m) for m in menu]))"], "n": 1, "out": ["21000", "6"]}, 96, 200, 1300, sel="c-w1")
o.append(hl(96, 200, 1300, 2, 1, "mark", 1, "장바구니 합계"))
o.append(side(96, 470, 846, 390, "19의 calc_total 몸통", ["total = 0", "for m in cart:", "    total += menu[m]"], ["21000"], GRAY, "#F1F0EC", ' data-build-in="rise order 2"', 24, "세 줄"))
o.append(note_card(978, 470, 846, 390, "가격 리스트를 만들어 더해요", "cart의 메뉴마다 menu[m]으로 가격을 꺼내 리스트를 만들고, sum이 그 리스트를 더해요. 메뉴 이름 중 가장 긴 길이는 6이에요.", K4, ' data-build-in="rise order 3"'))
o.append(caption("계산할 값만 리스트로 모아 sum, max, len에 넘겨요.", 930))
W("w-sum", o, "컴프리헨션이 만든 리스트를 sum이나 max에 바로 넘길 수 있어요. 장바구니 cart의 메뉴마다 menu[m]으로 가격을 꺼내 리스트를 만들고, sum이 더해요. 19에서 calc_total 안에 적었던 세 줄이 한 줄이 됐어요. 메뉴 이름 길이를 모아 max에 넘기면 가장 긴 이름의 길이 6이 나와요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p4", "함수와 함께 쓰기"))

o = [sec("w-sorted")] + head(EB4, "고른 다음 22의 sorted, min으로 이어요", K4)
o += cell({"id": "c-w2", "lines": ['stock = {"coffee": 3, "latte": 0, "cake": 2, "tea": 5}', "ok = [m for m in menu if stock[m] > 0]", "print(ok)", "print(sorted(ok, key=menu.get))", "print(min(ok, key=menu.get))"], "n": 2, "out": ["['coffee', 'cake', 'tea']", "['tea', 'coffee', 'cake']", "tea"]}, 96, 200, 1100, sel="c-w2")
o.append(hl(96, 200, 1100, 1, 1, "mark", 1, "주문 가능한 메뉴"))
o.append(hl(96, 200, 1100, 3, 2, "run", 2))
o.append(note_card(1240, 200, 584, 330, "고르기는 컴프리헨션", "품절이 아닌 메뉴만 골라 ok에 담아요.", K4, ' data-build-in="rise order 3"'))
o.append(note_card(1240, 560, 584, 300, "줄 세우기는 sorted", "22처럼 key=menu.get으로 가격순이에요. 주문 가능한 가장 싼 메뉴는 tea예요.", K2, ' data-build-in="rise order 4"'))
o.append(caption("고르고 바꾸기는 컴프리헨션, 줄 세우기와 고르기 하나는 sorted, min이에요.", 930))
W("w-sorted", o, "재고가 있는 메뉴만 컴프리헨션으로 골라 ok에 담았어요. 그다음 22에서 배운 sorted와 key=menu.get으로 가격순으로 줄 세웠어요. min에 같은 key를 주면 주문 가능한 메뉴 중 가장 싼 tea가 나와요. 고르고 바꾸는 일은 컴프리헨션, 순서와 가장 큰 값은 sorted, max, min으로 나눠 맡기면 각 줄이 짧아져요. menu는 앞 셀에서 만들었어요." + REAL)

o = [sec("w-when")] + head(EB4, "이럴 땐 for가 더 읽기 쉬워요", K4)
rows_ = [("새 리스트 하나를 만들 때", "컴프리헨션", "[p + 500 for p in prices]"), ("print로 찍기만 할 때", "for", "for m in names: print(m)"),
         ("한 번에 여러 줄을 할 때", "for", "합계 쌓기, 재고 줄이기"), ("break로 멈춰야 할 때", "for", "18의 break"), ("조건이 두 개를 넘을 때", "for나 def", "if, elif로 나눠 쓰기")]
for i, (a_, b_, c_) in enumerate(rows_):
    good = b_ == "컴프리헨션"
    o.append(f'<div data-build-in="rise order {min(i + 1, 4)}" style="position:absolute;left:96px;top:{200 + i * 96}px;width:1150px;height:84px;background:{CARD};border:2px solid {LINE};border-left:10px solid {K4 if good else GRAY};border-radius:14px;padding:0 24px;display:flex;flex-direction:row;align-items:center;gap:20px">'
             + p(f"width:380px;flex:none;font-size:25px;font-weight:700;color:{INK}", e(a_)) + p(f"width:200px;flex:none;font-size:25px;font-weight:900;color:{K4 if good else GRAY}", e(b_))
             + p(f"flex:1;{'font-family:' + MONO + ';font-size:22px;' if c_.isascii() else 'font-size:22px;'}font-weight:700;color:{SUB};white-space:nowrap", e(c_)) + '</div>')
o.append(label("참고, 읽기만: 겹친 컴프리헨션", 1290, 196, GRAY, ' data-build-in="fade order 5"', 540, 24))
o += cell({"id": "c-w3", "lines": ["scores = [[90, 80], [70, 60]]", "print([x for row in scores", "       for x in row])"], "n": 3, "out": ["[90, 80, 70, 60]"]}, 1290, 240, 534, attrs=' data-build-in="rise order 5"')
o.append(note_card(1290, 480, 534, 380, "for를 두 번 적을 수도 있어요", "14의 2차원 리스트를 한 줄로 펼쳤어요. 앞의 for가 바깥 반복이에요. 이런 코드를 만나면 읽을 수 있게만 봐 두세요.", GRAY, ' data-build-in="rise order 6"'))
W("w-when", o, "컴프리헨션이 늘 좋은 건 아니에요. 새 리스트 하나를 만드는 일에만 써요. print로 찍기만 하거나, 합계를 쌓으면서 재고도 줄이는 것처럼 한 번에 여러 줄을 할 때, 18의 break로 중간에 멈춰야 할 때는 for가 맞아요. 조건이 두 개를 넘으면 21에서처럼 if, elif로 나눠 쓰는 편이 읽기 쉬워요. 오른쪽은 참고로 보여 드리는 겹친 컴프리헨션이에요. 14의 2차원 리스트를 한 줄로 펼쳐요. 앞에 적은 for가 바깥 반복이에요. 따라 치지 않아도 되고, 남의 코드에서 만나면 읽을 수 있게만 봐 두세요. 한 줄 코드를 셀에서 두 줄로 나눠 적었는데, 대괄호 안에서는 줄을 나눠도 돼요." + REAL)

# ---------- part 5 ----------
o = [sec("t-else")] + head(EB5, "뒤의 if에 else를 붙이면 SyntaxError가 나요", K5)
o += cell({"id": "c-t1", "lines": [PR4, "print([p for p in prices if p >= 5000 else 0])"], "n": 1, "out": ["SyntaxError: invalid syntax"], "err": True}, 96, 200, 1100, sel="c-t1")
o.append(hl(96, 200, 1100, 1, 1, "err", 1, "뒤에는 else 없음"))
o.append(note_card(1240, 200, 584, 300, "else는 앞에서만", "for 뒤의 if는 고르기라서 else를 받지 않아요. 바꾸려면 if else를 앞으로 옮겨요.", K5, ' data-build-in="rise order 2"'))
o.append(side(96, 420, 1100, 210, "이렇게 고쳐요", ["[p for p in prices if p >= 5000]", "[p if p >= 5000 else 0 for p in prices]"], [], GR, "#E6F4EC", ' data-build-in="rise order 3"', 26, "고르기 또는 바꾸기"))
o.append(note_card(96, 670, 1100, 190, "오류 끝 괄호는 뺐어요", "SyntaxError 끝의 (1234.py, line 2)는 셀마다 달라서 슬라이드에서 뺐어요.", GRAY, ' data-build-in="rise order 4"'))
o.append(note_card(1240, 530, 584, 330, "셀 전체가 실행되지 않아요", "SyntaxError는 실행 전에 나서 첫 줄 prices도 만들어지지 않아요.", OR, ' data-build-in="rise order 5"'))
W("t-else", o, "2파트의 두 자리를 섞으면 나는 오류예요. 고르는 if 뒤에 else 0을 붙였더니 invalid syntax가 나요. for 뒤의 if는 고르기라서 else를 받지 않아요. 고르고 싶으면 else를 빼고, 모든 값을 바꾸고 싶으면 if else를 for 앞으로 옮겨요. SyntaxError는 셀을 실행하기 전에 나서 같은 셀의 첫 줄 prices도 만들어지지 않아요. 메시지 끝의 파일 이름과 줄 번호는 셀마다 달라서 뺐어요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p5", "오류와 함정"))

o = [sec("t-print")] + head(EB5, "print를 넣으면 None 리스트가 생겨요", K5)
o += cell({"id": "c-t2", "lines": ['[print(m) for m in ["latte", "tea"]]'], "n": 2, "out": ["latte", "tea", "", "[None, None]"]}, 96, 200, 1000, sel="c-t2")
o.append(hl(96, 200, 1000, 0, 1, "err", 1, "print가 돌려준 None"))
o.append(note_card(1150, 200, 674, 300, "찍히긴 하는데", "print는 화면에 찍고 None을 돌려줘요. 19에서 본 그 None이 리스트에 모였어요.", K5, ' data-build-in="rise order 2"'))
o.append(side(1150, 530, 674, 300, "이렇게 고쳐요", ['for m in ["latte", "tea"]:', "    print(m)"], [], GR, "#E6F4EC", ' data-build-in="rise order 3"', 24, "찍기는 for"))
o.append(note_card(96, 500, 1000, 360, "컴프리헨션은 값을 모으는 곳", "결과 리스트가 필요 없는 일, 곧 찍기만 하는 일에는 쓰지 않아요. 셀 마지막 줄이라 [None, None]이 결과로 보였어요.", OR, ' data-build-in="rise order 4"'))
W("t-print", o, "찍는 일도 한 줄로 하고 싶어서 대괄호 안에 print를 넣었어요. latte와 tea는 찍혀요. 그런데 셀 마지막 줄이라 결과로 [None, None]도 보여요. print는 찍고 나서 None을 돌려주고, 컴프리헨션이 그 None을 모았어요. 19에서 print와 return을 비교할 때 본 None이에요. 컴프리헨션은 값을 모아 리스트를 만드는 곳이에요. 찍기만 할 때는 for를 써요." + REAL)

o = [sec("t-paren")] + head(EB5, "소괄호로 감싸면 리스트가 아니에요", K5)
o += cell({"id": "c-t3", "lines": [PR4, "print((p + 500 for p in prices))", "print(list(p + 500 for p in prices))"], "n": 3, "out": ["<generator object <genexpr> at 0x7f2ba871b440>", "[5000, 5500, 7000, 3500]"]}, 96, 200, 1300, sel="c-t3")
o.append(hl(96, 200, 1300, 1, 1, "err", 1, "튜플이 아니에요"))
o.append(note_card(96, 480, 846, 380, "21의 map object와 비슷해요", "소괄호는 달라고 하면 값을 하나씩 꺼내 주는 묶음을 만들어요. list로 감싸야 결과가 보여요. 튜플을 만들지 않아요.", K5, ' data-build-in="rise order 2"'))
o.append(note_card(978, 480, 846, 380, "리스트가 필요하면 대괄호", "[p + 500 for p in prices]처럼 대괄호로 써요. 0x로 시작하는 숫자는 화면마다 달라요.", GR, ' data-build-in="rise order 3"'))
W("t-paren", o, "튜플을 만들려고 대괄호 대신 소괄호로 감쌌어요. 그런데 찍어 보면 튜플이 아니라 generator object가 나와요. 21의 map object처럼 달라고 하면 값을 하나씩 꺼내 주는 묶음이에요. list로 감싸야 결과가 보여요. 이번 챕터에서는 이 묶음을 따로 다루지 않아요. 리스트가 필요하면 대괄호로 써요. 0x 뒤 숫자는 메모리 위치라서 화면마다 달라요." + REAL)

o = [sec("t-name")] + head(EB5, "앞과 뒤의 이름이 다르면 NameError가 나요", K5)
o += cell({"id": "c-t4", "lines": ["print([x + 10 for p in prices])"], "n": 4, "out": ["NameError: name 'x' is not defined"], "err": True}, 96, 200, 1000, sel="c-t4")
o.append(hl(96, 200, 1000, 0, 1, "err", 1, "x와 p"))
o.append(f'<div data-build-in="rise order 2" style="position:absolute;left:96px;top:400px;width:1000px;height:120px;background:#252B36;border-radius:20px;display:flex;align-items:center;justify-content:center">'
         + seg([("[", W_), ("x", CI), (" + 10 for ", W_), ("p", CI), (" in prices]", W_)], 40) + '</div>')
o.append(note_card(1150, 200, 674, 320, "꺼낸 이름은 p예요", "for p in으로 꺼냈는데 앞에서 x를 썼어요. 그런 변수는 없어요.", K5, ' data-build-in="rise order 3"'))
o.append(side(1150, 550, 674, 220, "이렇게 고쳐요", ["[p + 10 for p in prices]"], [], GR, "#E6F4EC", ' data-build-in="rise order 4"', 26, "이름 맞추기"))
o.append(note_card(96, 560, 1000, 300, "복사해 고칠 때 자주 나요", "앞 예제의 [x + 10 for x in numbers]를 가져와 뒤만 바꾸면 생겨요. 앞과 뒤에서 같은 이름을 쓰는지 봐요.", OR, ' data-build-in="rise order 5"'))
W("t-name", o, "앞의 값에는 x를 쓰고 뒤의 for에는 p로 꺼냈어요. 꺼낸 이름은 p뿐이라 x가 없다는 NameError가 나요. 1파트의 [x + 10 for x in numbers]를 복사해서 뒤쪽만 prices로 바꿀 때 자주 생겨요. 넣을 값에 쓰는 이름과 for로 꺼내는 이름이 같은지 봐요. prices는 앞 셀에서 만들었어요." + REAL)

# ---------- part 6 ----------
o = [sec("x-receipt")] + head(EB6, "장바구니 영수증을 컴프리헨션으로 찍어요", K6)
RC = ['menu = {"coffee": 4500, "latte": 5000, "cake": 6500}', 'cart = ["latte", "cake", "coffee"]', 'lines = [f"{m:<7}{menu[m]:>6,}원" for m in cart]', 'print("\\n".join(lines))', 'print(f"합계   {sum([menu[m] for m in cart]):>6,}원")']
o += cell({"id": "c-x1", "lines": RC, "n": 1, "out": ["latte   5,000원", "cake    6,500원", "coffee  4,500원", "합계   16,000원"]}, 96, 196, 1200, sel="c-x1")
o.append(hl(96, 196, 1200, 2, 1, "mark", 1, "줄 만들기"))
o.append(hl(96, 196, 1200, 4, 1, "run", 2, "합계"))
o.append(note_card(1340, 196, 484, 330, "f-string도 값이에요", "13의 칸 맞추기를 넣을 값 자리에 그대로 적었어요.", K6, ' data-build-in="rise order 3"'))
o.append(note_card(1340, 556, 484, 300, "21에서는 def와 map", "줄 만드는 일을 def로 따로 만들었어요. 이번에는 한 줄이에요.", GRAY, ' data-build-in="rise order 4"'))
o.append(caption("줄 리스트를 만들고 join으로 이어 찍어요.", 930))
W("x-receipt", o, "장바구니 영수증을 찍어요. 메뉴마다 13의 칸 맞추기를 쓴 f-string 한 줄을 만들어 lines에 모았어요. f-string도 값이라 넣을 값 자리에 쓸 수 있어요. join과 줄바꿈으로 한 번에 찍고, 합계는 4파트처럼 가격 리스트를 sum에 넘겼어요. 21에서는 줄 만드는 일을 def로 만들어 map에 넘겼는데, 컴프리헨션으로는 한 줄이에요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p6", "실습"))

o = [sec("x-stock")] + head(EB6, "품절 목록과 주문 가능 메뉴판을 만들어요", K6)
ST = ['menu = {"coffee": 4500, "latte": 5000, "cake": 6500, "tea": 4000}', 'stock = {"coffee": 3, "latte": 0, "cake": 2, "tea": 0}', "soldout = [m for m in stock if stock[m] == 0]", 'print("품절:", ", ".join(soldout))', "board = {m: menu[m] * 11 // 10 for m in menu if stock[m] > 0}", "print(board)"]
o += cell({"id": "c-x2", "lines": ST, "n": 2, "out": ["품절: latte, tea", "{'coffee': 4950, 'cake': 7150}"]}, 96, 196, 1300, sel="c-x2")
o.append(hl(96, 196, 1300, 2, 1, "mark", 1, "리스트"))
o.append(hl(96, 196, 1300, 4, 1, "run", 2, "딕셔너리"))
o.append(lockers([("coffee", "4950"), ("cake", "7150")], 96, 580, 260, 170, K6, K6BG, hi=(0, 1), attrs=' data-build-in="rise order 3"'))
o.append(note_card(1440, 196, 384, 330, "고르고 바꾸기", "재고 있는 메뉴만 골라 10% 올린 가격을 담아요.", K6, ' data-build-in="rise order 4"'))
o.append(note_card(1440, 556, 384, 300, "join으로 한 줄", "품절 메뉴를 쉼표로 이어 찍어요.", GRAY, ' data-build-in="rise order 5"'))
W("x-stock", o, "재고 데이터로 두 가지를 만들어요. 품절 메뉴는 재고가 0인 키만 골라 리스트로 만들고, 13의 join으로 쉼표를 넣어 이어 찍었어요. 새 메뉴판은 재고가 있는 메뉴만 골라 10% 올린 가격을 담은 딕셔너리예요. 키: 값 앞자리에 바꿀 식을, 뒤에 고를 조건을 적었어요. 2파트의 고르고 바꾸기를 딕셔너리로 한 거예요." + REAL)

o = [sec("x-grades")] + head(EB6, "성적표에서 합격자, 결과표, 평균, 1등을 뽑아요", K6)
GR_ = ['scores = [["kim", 92], ["lee", 78], ["park", 85], ["choi", 59]]', "print([name for name, score in scores if score >= 80])", 'print(["합격" if score >= 60 else "재시험" for name, score in scores])', "print(sum([score for name, score in scores]) / len(scores))", "print(max(scores, key=lambda s: s[1])[0])"]
o += cell({"id": "c-x3", "lines": GR_, "n": 3, "out": ["['kim', 'park']", "['합격', '합격', '합격', '재시험']", "78.5", "kim"]}, 96, 196, 1300, sel="c-x3")
o.append(callout(96, 610, 846, 110, "if 뒤에", "80점 이상만 고르기", LI, 1, 26))
o.append(callout(978, 610, 846, 110, "if else 앞에", "모두에게 합격, 재시험 붙이기", LV, 2, 26))
o.append(callout(96, 740, 846, 110, "sum([...]) / len", "점수만 모아 평균", K4, 3, 26))
o.append(callout(978, 740, 846, 110, "max(..., key=)", "22의 key로 1등", K2, 4, 26))
o.append(note_card(1440, 196, 384, 330, "14의 2차원 리스트", "안쪽 리스트 두 칸을 name, score로 꺼내 담아요.", K6, ' data-build-in="rise order 5"'))
W("x-grades", o, "14의 성적 2차원 리스트로 네 가지를 뽑아요. 안쪽 리스트 두 칸을 name, score로 꺼내 담아요. 80점 이상은 뒤에 if를 붙여 골랐어요. 합격과 재시험은 앞에 한 줄 if else를 넣어 모두에게 붙였어요. 평균은 점수만 모은 리스트를 sum에 넘기고 사람 수로 나눴어요. 1등은 22에서 배운 max와 key예요. 고르기, 바꾸기, 함수와 함께 쓰기를 한 셀에서 다 썼어요." + REAL)

# ---------- wrap up ----------
trouble([("SyntaxError: invalid syntax", "뒤의 if에 else를 붙였어요", "else는 for 앞으로"),
         ("NameError: name 'x' is not defined", "앞과 뒤의 이름이 달라요", "같은 이름으로"),
         ("[None, None]이 같이 나와요", "대괄호 안에서 print를 했어요", "찍기는 for로"),
         ("<generator object ...>가 나와요", "소괄호로 감쌌어요", "대괄호로"),
         ("개수가 줄었어요", "for 뒤에 if를 붙여 골랐어요", "바꾸려면 if else를 앞에"),
         ("한 줄이 너무 길어요", "조건이나 할 일이 많아요", "for나 def로 나누기"),
         ("집합 순서가 슬라이드와 달라요", "집합은 순서가 없어요", "sorted()로 찍기")],
        "헷갈리면 같은 일을 for 문으로 먼저 써 보고 세 조각을 옮겨요.",
        "이번 챕터에서 자주 만나는 일을 모았어요. 1번과 5번은 if 자리 때문에 생겨요. 뒤의 if는 고르기, 앞의 if else는 바꾸기예요. 2번은 이름이 어긋났을 때, 3번과 4번은 컴프리헨션을 리스트 만들기 말고 다른 데 쓰려다 생겨요. 6번처럼 한 줄이 길어지면 for나 def로 나누는 게 더 좋아요. 막히면 for 문으로 먼저 써 보고 넣을 값, for, if 세 조각을 대괄호 안으로 옮기면 돼요.")

cheatsheet([("[x + 10 for x in xs]", "값마다 바꾼 리스트", K2), ("[x for x in xs if 조건]".replace("조건", "x > 0"), "조건에 맞는 값만", K2), ("[a if c else b for x in xs]", "앞의 if else는 바꾸기", K2), ("[n for n, s in pairs]", "튜플은 꺼내 담기로", K3),
            ("{k: v for k, v in d.items()}", "딕셔너리 만들기", K3), ("{x for x in xs}", "집합 만들기", K3), ("sum([...])", "모은 값을 바로 넘기기", K4), ("for 문", "찍기, 여러 줄, break", GRAY)],
           ["뒤의 if는 고르기, 앞의 if else는 바꾸기", "다음 단계: 함수, 정렬, 컴프리헨션을 섞어 카페 데이터를 다뤄요"],
           "이번 챕터에서 쓴 모양을 한 장에 모았어요. 대괄호 안에 넣을 값, for, if 순서로 적어요. 뒤의 if는 고르기, 앞의 if else는 바꾸기예요. 튜플은 꺼내 담기로 이름을 붙이고, 중괄호로 딕셔너리와 집합도 만들어요. 만든 리스트는 sum, max, sorted에 바로 넘겨요. 찍기만 하거나 여러 줄을 할 때는 for가 더 좋아요. 21부터 23까지 배운 lambda, 정렬, 컴프리헨션을 섞어 쓰면 카페 데이터를 짧게 다룰 수 있어요.")

finish([("Lightbulb", K1, "왜 필요한가", "길어지는 for와 읽기 어려운 map, 세 조각 옮기기, 가장 짧은 예", "c-why", "c-min"),
        ("Code", K2, "만들기와 고르기", "세 방법 비교, 읽는 순서, 뒤의 if, 고르고 바꾸기, 앞의 if else, 자리 비교", "b-three", "b-pos"),
        ("Archive", K3, "여러 데이터에 쓰기", "len과 range, 튜플 꺼내 담기, 딕셔너리와 집합 만들기", "r-str", "r-set"),
        ("Settings", K4, "함수와 함께 쓰기", "sum, max에 넘기기, sorted와 min, for가 나을 때", "w-sum", "w-when"),
        ("Warning", K5, "오류와 함정", "뒤의 if에 else, print 넣기, 소괄호, 이름 어긋남", "t-else", "t-name"),
        ("Star", K6, "실습", "영수증, 품절 목록과 새 메뉴판, 성적표", "x-receipt", "x-grades")],
       "여섯 파트로 나눴어요. 1파트는 for와 map의 불편한 점과 for의 세 조각을 옮기는 그림이에요. 2파트가 중심이에요. 만들기, 고르기, if 자리를 비교해요. 3파트는 튜플, 딕셔너리, 집합으로 넓히고, 4파트는 sum, sorted와 함께 쓰는 법과 for가 나은 경우예요. 5파트는 자주 나는 오류, 6파트는 카페와 성적 실습이에요. 파트마다 새 커널에서 위에서부터 차례로 실행해요.",
       "리스트 컴프리헨션")
