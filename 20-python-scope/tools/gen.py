"""Generates every slide of the functions 2 deck (20, default values, local and global variables) and slides/deck.json.

Story: keeps writing in basics.ipynb from chapters 12-19. Starts from two pains with chapter 19's functions (typing "M"
every time, a total that vanishes outside the function) and draws default values and the inside/outside boxes. Then
default and keyword arguments, local variables, global variables (same name, UnboundLocalError, global versus return),
lists and dictionaries passed into a function, and three café exercises (orders, receipt, points).
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
EB2 = "2. 기본값과 키워드 인자"
EB3 = "3. 지역 변수"
EB4 = "4. 전역 변수"
EB5 = "5. 리스트와 딕셔너리 넘기기"
EB6 = "6. 실습"
K5, K5BG = GR, "#E6F4EC"
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



# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#F2B27A;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
       '<h1 style="font-size:92px;font-weight:900;line-height:1.1;color:#F6F5F1">함수 2<br>기본값과<br>변수 범위</h1>',
       '<p style="font-size:40px;line-height:1.4;color:#BFC6D4">자주 쓰는 값은 미리 채워 두고<br>함수 안과 밖의 변수 구분하기</p>']
cov.append(f'<div style="position:absolute;left:940px;top:300px;width:860px;height:480px;background:#252B36;border-radius:24px;padding:44px 48px;display:flex;flex-direction:column;justify-content:center;gap:16px">')
for line, c in [('def order(menu_name, size="M"):', "#9DBDEB"), ('order("latte")', "#8FD8DE"), ('order(size="L", menu_name="tea")', "#8FD8DE"), ("count = 0", "#E3B877"), ("def visit(count):", "#9DBDEB"), ("    return count + 1", "#F2A0A0")]:
    cov.append(p(f"font-family:{MONO};font-size:32px;font-weight:700;line-height:1.45;color:{c};white-space:pre", e(line)))
cov.append('</div>')
W("cover", cov, "19에서 def로 함수를 만들고 return으로 값을 돌려받았어요. 이번 챕터는 함수 2예요. 부를 때 빼도 되는 기본값, 칸 이름을 적어 넣는 키워드 인자를 먼저 봐요. 그다음 함수 안에서 만든 변수와 밖에서 만든 변수가 어디까지 보이는지, 바깥 변수를 바꾸려면 어떻게 하는지 봐요. 같은 카페 예제를 이어서 써요.", ("intro", "들어가기"))

ORDER.append("toc")

# ---------- ready ----------
o = [sec("ready")] + head("들어가기", "19에서 이어서 해요", JP)
done = [("hello-uv 노트북, 커널 .venv", "09 · 25–27쪽"), ("print의 sep, end와 copy()", "13"), ("딕셔너리 get, stock[name] -= 1", "15"), ("sorted(..., reverse=True)", "16"), ("if, for, while", "17, 18"), ("def, 매개변수, return, None", "19")]
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
W("ready", o, "09에서 만든 hello-uv 폴더를 VS Code로 열고, 12부터 쓰던 basics.ipynb를 다시 열어요. 13의 print sep, end와 copy, 15의 get과 재고 줄이기, 16의 sorted reverse를 다시 만나요. 19의 def, 매개변수, return은 이번 챕터 내내 써요. 슬라이드의 출력은 tools/demo.sh가 hello-uv 커널에서 같은 셀을 실제로 실행한 결과예요. 셀 번호는 파트마다 [1]부터 다시 셌어요.")

# ---------- part 1 ----------
o = [sec("s-why")] + head(EB1, "19의 함수로 쓰다 보면 두 군데서 막혀요", K1)
o.append(label("거의 늘 같은 값을 넣어요", 96, 190, K1, ' data-build-in="fade order 1"', 846, 26))
o += cell({"id": "c-w1", "lines": ["def order(menu_name, size):", '    print(f"{menu_name} {size} 사이즈")', "", 'order("latte", "M")', 'order("coffee", "M")', 'order("tea", "M")'], "n": 1, "out": ["latte M 사이즈", "coffee M 사이즈", "tea M 사이즈"]}, 96, 236, 846, sel="c-w1", attrs=' data-build-in="rise order 1"')
o += cell({"id": "c-w2", "lines": ['order("cake")'], "n": 2, "out": ["TypeError: order() missing 1 required positional argument: 'size'"], "err": True}, 96, 630, 1728, attrs=' data-build-in="rise order 2"')
o.append(label("함수 안에서 만든 값이 안 보여요", 978, 190, K3, ' data-build-in="fade order 3"', 846, 26))
o += cell({"id": "c-w3", "lines": ["def calc():", "    total = 4500 * 2", "", "calc()", "print(total)"], "n": 3, "out": ["NameError: name 'total' is not defined"], "err": True}, 978, 236, 846, attrs=' data-build-in="rise order 3"')
o.append(note_card(96, 760, 846, 170, "M을 매번 적어야 해요", "빼면 TypeError예요. 안 적으면 M으로 해 주면 좋겠어요.", K1, ' data-build-in="rise order 4"'))
o.append(note_card(978, 760, 846, 170, "total이 어디 갔나요", "calc 안에서 분명히 만들었는데 밖에서는 없다고 나와요.", K3, ' data-build-in="rise order 5"'))
o.append(caption("오늘은 기본값과 변수가 보이는 범위를 배워요.", 960))
W("s-why", o, "19에서 만든 order 함수를 카페에서 써 보면 대부분 M 사이즈예요. 그런데도 매번 M을 적어야 하고, 빼면 19에서 본 TypeError가 나요. 안 적으면 M으로 알아서 해 주면 편하겠죠. 오른쪽은 다른 문제예요. calc 안에서 total을 만들었는데 밖에서 찍으면 그런 이름이 없다고 해요. 오늘은 이 두 가지를 풀어요. 하나는 기본값이고, 다른 하나는 변수가 보이는 범위예요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p1", "왜 필요한가"))

o = [sec("s-big")] + head(EB1, "칸에 미리 채운 값, 그리고 안과 밖", K1)
o.append(f'<div data-build-in="rise order 1" style="position:absolute;left:96px;top:196px;width:640px;height:640px;background:{CARD};border:2px solid {LINE};border-top:10px solid {K2};border-radius:20px;padding:28px 32px;display:flex;flex-direction:column;gap:22px">'
         + p(f"font-size:28px;font-weight:700;color:{INK}", "기본값: 칸에 미리 넣어 둔 값")
         + mono('def order(menu_name, size="M"):', 22, K2, K2BG, "align-self:flex-start")
         + '<div style="display:flex;flex-direction:row;gap:18px;margin-top:10px">'
         + '<div style="flex:1;height:170px;border:3px dashed #C9CED8;border-radius:16px;display:flex;flex-direction:column;overflow:hidden">' + p(f"height:56px;background:#ECEAE3;font-family:{MONO};font-size:24px;font-weight:700;line-height:56px;padding:0 18px;color:{INK}", "menu_name") + p(f"flex:1;font-size:24px;color:{GRAY};text-align:center;line-height:110px", "꼭 넣어요") + '</div>'
         + '<div style="flex:1;height:170px;border:3px solid ' + K2 + ';border-radius:16px;display:flex;flex-direction:column;overflow:hidden">' + p(f"height:56px;background:{K2};font-family:{MONO};font-size:24px;font-weight:700;line-height:56px;padding:0 18px;color:#FFFFFF", "size") + p(f"flex:1;font-family:{MONO};font-size:40px;font-weight:700;color:{INK};text-align:center;line-height:110px", '"M"') + '</div></div>'
         + p(f"font-size:24px;line-height:1.5;color:{INK}", "부를 때 빼면 \"M\"이 들어가요. 넣으면 넣은 값으로 바뀌어요.") + '</div>')
o.append(f'<div data-build-in="rise order 2" style="position:absolute;left:780px;top:196px;width:1044px;height:640px;background:#EFF3FB;border:3px solid {K4};border-radius:24px;padding:24px 30px">'
         + p(f"font-size:26px;font-weight:700;color:{K4}", "밖: 노트북 전체 (전역)")
         + '<div style="position:absolute;left:30px;top:80px;display:flex;flex-direction:row;gap:14px">' + chip('shop = "KANT 카페"', K4, K4BG, 24) + chip("count = 0", K4, K4BG, 24) + '</div>'
         + f'<div style="position:absolute;left:30px;top:180px;width:560px;height:420px;background:{CARD};border:3px solid {K3};border-radius:20px;padding:20px 26px">'
         + p(f"font-size:26px;font-weight:700;color:{K3}", "안: def calc() 몸통 (지역)")
         + '<div style="position:absolute;left:26px;top:80px;display:flex;flex-direction:column;gap:14px">' + chip("total = 9000", K3, K3BG, 24) + chip("매개변수도 여기", K3, K3BG, 22) + '</div>'
         + p(f"position:absolute;left:26px;bottom:20px;width:500px;font-size:22px;color:{SUB}", "함수가 끝나면 이 상자는 사라져요") + '</div></div>')
o.append(f'<div data-build-in="rise order 3" style="position:absolute;left:1400px;top:420px;width:400px;height:150px;display:flex;flex-direction:column;gap:10px">'
         + yes_no(0, 0, True, "안에서 밖은 보여요").replace("position:absolute;left:0px;top:0px;", "") + '</div>')
o.append(f'<div data-build-in="rise order 4" style="position:absolute;left:1400px;top:520px;width:400px;height:150px;display:flex;flex-direction:column;gap:10px">'
         + yes_no(0, 0, False, "밖에서 안은 안 보여요").replace("position:absolute;left:0px;top:0px;", "") + '</div>')
o.append(caption("함수 안에서는 밖이 보이고, 밖에서는 안이 보이지 않아요.", 920))
W("s-big", o, "오늘 배울 두 가지를 그림 한 장에 담았어요. 왼쪽은 기본값이에요. def 줄에서 size 칸에 \"M\"을 미리 넣어 두면 부를 때 빼도 M이 들어가요. 오른쪽은 변수가 보이는 범위예요. 노트북에서 함수 밖에 만든 변수는 전역 변수라고 하고, 함수 몸통에서 만든 변수와 매개변수는 지역 변수라고 해요. 함수 안에서는 바깥 변수를 읽을 수 있지만, 바깥에서는 함수 안의 변수를 볼 수 없어요. 함수가 끝나면 안쪽 상자가 통째로 사라지기 때문이에요.")

o = [sec("s-min")] + head(EB1, "def 줄에서 칸 = 값으로 기본값을 정해요", K1)
o += cell({"id": "c-m1", "lines": ['def order(menu_name, size="M"):', '    print(f"{menu_name} {size} 사이즈")', "", 'order("latte")', 'order("latte", "L")'], "n": 4, "out": ["latte M 사이즈", "latte L 사이즈"]}, 96, 200, 1000, sel="c-m1")
o.append(hl(96, 200, 1000, 0, 1, "mark", 1, 'size="M"'))
o += table(1150, 200, 674, [("부르기", 320), ("size", 100), ("", 120)], [('order("latte")', '"M"', "기본값"), ('order("latte", "L")', '"L"', "넣은 값")], 2, K2, 80)
o.append(note_card(96, 560, 1000, 300, "빼도 되는 칸이 생겼어요", "기본값이 있는 칸은 부를 때 빼도 돼요. 기본값이 없는 menu_name은 지금처럼 꼭 넣어요.", K2, ' data-build-in="rise order 4"'))
o.append(note_card(1150, 420, 674, 440, "= 앞뒤를 띄우지 않아요", "변수에 넣을 땐 x = 1처럼 띄웠지만, 괄호 안 기본값은 size=\"M\"처럼 붙여 쓰는 게 파이썬 관례예요.", None, ' data-build-in="rise order 5"'))
o.append(caption("기본값이 있는 칸은 빼면 기본값, 넣으면 넣은 값이에요.", 920))
W("s-min", o, "def 줄의 칸 뒤에 = 값을 적으면 기본값이 돼요. order(\"latte\")처럼 size를 빼고 부르면 size에 \"M\"이 들어가요. order(\"latte\", \"L\")처럼 넣으면 넣은 \"L\"이 들어가요. 기본값이 없는 menu_name은 19처럼 꼭 넣어야 해요. 괄호 안의 =는 앞뒤를 띄우지 않고 붙여 쓰는 게 관례예요." + REAL)

# ---------- part 2 ----------
o = [sec("k-default")] + head(EB2, "기본값이 여러 개면 앞에서부터 채워요", K2)
o += cell({"id": "c-k1", "lines": ['def order(menu_name, size="M", qty=1):', '    print(f"{menu_name} {size} {qty}잔")', "", 'order("latte")', 'order("latte", "L")', 'order("latte", "L", 2)', 'order("latte", qty=3)'], "n": 1, "out": ["latte M 1잔", "latte L 1잔", "latte L 2잔", "latte M 3잔"]}, 96, 200, 900, sel="c-k1")
o += table(1050, 200, 774, [("부르기", 360), ("size", 90), ("qty", 70)], [('order("latte")', '"M"', "1"), ('order("latte", "L")', '"L"', "1"), ('order("latte", "L", 2)', '"L"', "2"), ('order("latte", qty=3)', '"M"', "3")], 1, K2, 76, hi=(3,))
o.append(note_card(1050, 620, 774, 260, "qty만 바꾸고 싶으면", "순서대로 넣으면 size를 먼저 적어야 해요. qty=3처럼 칸 이름을 붙이면 size는 기본값으로 두고 qty만 바꿔요.", K2, ' data-build-in="rise order 5"'))
o.append(note_card(96, 680, 900, 200, "넣은 값은 앞 칸부터", "\"L\"은 둘째 칸 size에, 2는 셋째 칸 qty에 들어가요. 넣지 않은 칸만 기본값이에요.", None, ' data-build-in="rise order 2"'))
o.append(caption("칸 이름 = 값으로 넣으면 원하는 칸만 고를 수 있어요.", 920))
W("k-default", o, "기본값 칸이 두 개예요. 인자를 순서대로 넣으면 앞 칸부터 채우고, 넣지 않은 칸만 기본값을 써요. order(\"latte\", \"L\", 2)는 size에 L, qty에 2가 들어가요. 그런데 잔 수만 3으로 바꾸고 싶을 땐 어떻게 할까요? 순서대로라면 size도 적어야 해요. 마지막 줄처럼 qty=3으로 칸 이름을 붙여 넣으면 size는 기본값 M으로 두고 qty만 바꿀 수 있어요. 이렇게 이름을 붙여 넣는 인자를 키워드 인자라고 해요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p2", "기본값과 키워드 인자"))

o = [sec("k-keyword")] + head(EB2, "칸 이름을 붙이면 순서를 바꿔도 돼요", K2)
o += cell({"id": "c-k2", "lines": ['order(size="L", menu_name="tea")', 'order("tea", qty=2, size="S")'], "n": 2, "out": ["tea L 1잔", "tea S 2잔"]}, 96, 200, 900, sel="c-k2")
o.append(f'<div data-build-in="rise order 1" style="position:absolute;left:96px;top:440px;width:900px;height:80px;display:flex;align-items:center">'
         + p(f"font-family:{MONO};font-size:34px;font-weight:700;color:{INK};white-space:pre", 'order(<span style="color:' + BL + '">size=</span>"L", <span style="color:' + OR + '">menu_name=</span>"tea")') + '</div>')
o.append(var_box("v-k1", "menu_name", '"tea"', 96, 540, OR, 400, ' data-build-in="rise order 2"'))
o.append(var_box("v-k2", "size", '"L"', 530, 540, BL, 230, ' data-build-in="rise order 2"'))
o.append(var_box("v-k3", "qty", "1", 794, 540, GRAY, 200, ' data-build-in="rise order 2"'))
o.append(callout(1050, 200, 774, 160, '"tea"', "위치 인자. 적은 순서대로 칸에 들어가요", OR, 3, 26))
o.append(callout(1050, 390, 774, 160, "qty=2", "키워드 인자. 칸 이름을 보고 들어가요", BL, 4, 26))
o.append(note_card(1050, 580, 774, 280, "같이 쓸 땐 순서대로 먼저", "order(\"tea\", qty=2, size=\"S\")처럼 위치 인자를 앞에, 키워드 인자를 뒤에 적어요.", K2, ' data-build-in="rise order 5"'))
o.append(caption("키워드 인자는 칸 이름을 적어서 넣어요. 순서를 외우지 않아도 돼요.", 920))
W("k-keyword", o, "칸 이름을 붙여 넣으면 순서를 바꿔도 제자리를 찾아가요. size=\"L\"을 먼저 적어도 size 칸에, menu_name=\"tea\"는 menu_name 칸에 들어가요. qty는 넣지 않았으니 기본값 1이에요. 19에서 order(2, \"latte\")로 순서가 바뀌어 이상하게 찍혔던 문제를 이렇게 피할 수 있어요. 적은 순서대로 들어가는 인자는 위치 인자, 이름을 붙인 인자는 키워드 인자라고 해요. 둘을 같이 쓸 때는 위치 인자를 앞에 적어요." + REAL)

o = [sec("k-rule")] + head(EB2, "기본값과 키워드 인자는 뒤에 적어요", K2)
o += cell({"id": "c-k3", "lines": ['def order(size="M", menu_name):', "    print(menu_name, size)"], "n": 3, "out": ["SyntaxError: parameter without a default follows parameter with a default"], "err": True}, 96, 200, 1728, sel="c-k3")
o += cell({"id": "c-k4", "lines": ['order(size="L", "tea")'], "n": 4, "out": ["SyntaxError: positional argument follows keyword argument"], "err": True}, 96, 420, 1728, attrs=' data-build-in="rise order 2"')
o.append(note_card(96, 600, 846, 280, "만들 때: 기본값 칸은 뒤로", "기본값 없는 칸 뒤에 기본값 칸을 둬요. def order(menu_name, size=\"M\"):", K2, ' data-build-in="rise order 1"'))
o.append(note_card(978, 600, 846, 280, "부를 때: 키워드 인자는 뒤로", "이름 없는 값이 이름 붙인 값 뒤에 오면 안 돼요. order(\"tea\", size=\"L\")", K2, ' data-build-in="rise order 3"'))
o.append(caption("두 오류 모두 실행 전에 SyntaxError로 알려 줘요.", 930))
W("k-rule", o, "기본값과 키워드 인자에는 순서 규칙이 하나씩 있어요. 함수를 만들 때 기본값이 있는 칸을 앞에 두면 SyntaxError가 나요. 기본값 없는 칸을 앞에, 기본값 있는 칸을 뒤에 둬요. 부를 때는 키워드 인자 뒤에 이름 없는 값을 적으면 SyntaxError가 나요. 이름 없는 값을 먼저 적어요. 두 오류는 실행하기 전에 문법 검사에서 걸려요. 실제 메시지 끝에는 셀마다 다른 파일 이름과 줄 번호가 괄호로 붙는데, 그 부분은 빼고 옮겼어요." + REAL)

o = [sec("k-known")] + head(EB2, "키워드 인자는 이미 써 봤어요", K2)
o += cell({"id": "c-k5", "lines": ['print("coffee", "latte", sep=" / ")', 'print("coffee", end=" ")', 'print("latte")', "print(sorted([5000, 4500, 6500], reverse=True))"], "n": 5, "out": ["coffee / latte", "coffee latte", "[6500, 5000, 4500]"]}, 96, 200, 1000, sel="c-k5")
kn = [('sep=" / "', "print 13", "값 사이에 넣을 글자. 기본값은 빈칸 하나"), ('end=" "', "print 13", "끝에 붙일 글자. 기본값은 줄바꿈"), ("reverse=True", "sorted 16", "큰 것부터. 기본값은 False")]
for i, (k, w_, d) in enumerate(kn):
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:1150px;top:{200 + i * 170}px;width:674px;height:150px;background:{CARD};border:2px solid {LINE};border-left:10px solid {K2};border-radius:18px;padding:16px 24px;display:flex;flex-direction:column;gap:10px">'
             + '<div style="display:flex;flex-direction:row;align-items:center;gap:16px">' + mono(k, 24, K2, K2BG) + p(f"font-size:22px;font-weight:700;color:{GRAY}", e(w_)) + '</div>'
             + p(f"font-size:23px;color:{INK}", e(d)) + '</div>')
o.append(note_card(96, 560, 1000, 300, "print()만 쳐도 줄이 바뀌는 이유", "end의 기본값이 줄바꿈이라서 print()는 빈 줄 하나를 찍어요. 18의 구구단에서 쓴 그 print()예요.", OR, ' data-build-in="rise order 4"'))
o.append(caption("파이썬이 만든 함수도 기본값과 키워드 인자로 만들어져 있어요.", 920))
W("k-known", o, "키워드 인자는 처음이 아니에요. 13에서 print의 sep과 end를, 16에서 sorted의 reverse=True를 썼어요. 셋 다 기본값이 있는 칸이라 평소에는 빼고 썼어요. sep의 기본값은 빈칸 하나라서 값 사이가 한 칸씩 띄워졌고, end의 기본값은 줄바꿈이라서 print마다 줄이 바뀌었어요. 18의 구구단에서 print()로 줄을 바꾼 것도 이 기본값 덕분이에요." + REAL)

# ---------- part 3 ----------
o = [sec("l-local")] + head(EB3, "함수 안에서 만든 변수는 밖에서 안 보여요", K3)
o += cell({"id": "c-l1", "lines": ["def calc():", "    total = 4500 * 2", '    print("안:", total)', "", "calc()", 'print("밖:", total)'], "n": 1, "out": ["안: 9000", "", "NameError: name 'total' is not defined"], "err": True}, 96, 200, 1000, sel="c-l1")
o.append(hl(96, 200, 1000, 5, 1, "err", 3, "여기서 오류"))
o.append(f'<div data-build-in="rise order 1" style="position:absolute;left:1150px;top:200px;width:674px;height:300px;background:{CARD};border:3px solid {K3};border-radius:22px;padding:22px 28px;display:flex;flex-direction:column;gap:16px">'
         + p(f"font-size:26px;font-weight:700;color:{K3}", "calc()를 부르는 동안")
         + chip("total = 9000", K3, K3BG, 30, "align-self:flex-start")
         + p(f"font-size:22px;color:{SUB}", "몸통 안에서는 total을 쓸 수 있어요") + '</div>')
o.append(f'<div data-build-in="rise order 2" style="position:absolute;left:1150px;top:530px;width:674px;height:300px;background:#F1F0EC;border:3px dashed #B4B9C3;border-radius:22px;padding:22px 28px;display:flex;flex-direction:column;gap:16px">'
         + p(f"font-size:26px;font-weight:700;color:{GRAY}", "calc()가 끝난 뒤")
         + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:#B4B9C3;text-decoration:line-through", "total = 9000")
         + p(f"font-size:22px;color:{SUB}", "상자가 사라져서 밖에서는 찾을 수 없어요") + '</div>')
o.append(note_card(96, 600, 1000, 260, "지역 변수", "함수 안에서 만든 변수예요. 그 함수 안에서만 쓰고, 함수가 끝나면 사라져요. 밖에서 쓰려면 19처럼 return으로 돌려받아요.", K3, ' data-build-in="rise order 4"'))
o.append(caption("함수 안의 값을 밖에서 쓰려면 return으로 돌려받아요.", 920))
W("l-local", o, "calc 안에서 total을 만들고 찍었어요. 몸통 안에서는 9000이 잘 찍혀요. 그런데 밖에서 total을 찍으면 그런 이름이 없다는 NameError가 나요. 함수 안에서 만든 변수는 함수를 부르는 동안만 있다가, 함수가 끝나면 상자째 사라지기 때문이에요. 이런 변수를 지역 변수라고 해요. 함수 안의 값을 밖에서 쓰려면 19에서 배운 대로 return으로 돌려받아요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p3", "지역 변수"))

o = [sec("l-param")] + head(EB3, "매개변수도 함수 안에서만 쓰는 변수예요", K3)
o += cell({"id": "c-l2", "lines": ["def greet(name):", '    print(f"{name}님, 어서 오세요")', "", 'greet("kim")', "print(name)"], "n": 2, "out": ["kim님, 어서 오세요", "", "NameError: name 'name' is not defined"], "err": True}, 96, 200, 1000, sel="c-l2")
o.append(hl(96, 200, 1000, 4, 1, "err", 1, "밖"))
o.append(f'<div data-build-in="rise order 2" style="position:absolute;left:1150px;top:200px;width:674px;height:340px;background:{CARD};border:3px solid {K3};border-radius:22px;padding:22px 28px;display:flex;flex-direction:column;gap:16px">'
         + p(f"font-size:26px;font-weight:700;color:{K3}", 'greet("kim") 안')
         + chip('name = "kim"', K3, K3BG, 30, "align-self:flex-start")
         + p(f"font-size:23px;line-height:1.5;color:{INK}", "부를 때 넣은 값이 담긴 칸도 함수 안에만 있어요.") + '</div>')
o.append(note_card(96, 600, 1000, 260, "그래서 이름이 겹쳐도 괜찮아요", "19의 calc_total(cart, menu)에서 menu 칸은 바깥 menu 딕셔너리와 이름만 같은 다른 칸이에요.", OR, ' data-build-in="rise order 3"'))
o.append(note_card(1150, 570, 674, 290, "밖에서 쓰려면", "밖에서 만든 변수를 인자로 넣거나, 함수가 return한 값을 받아요.", GR, ' data-build-in="rise order 4"'))
W("l-param", o, "매개변수도 지역 변수예요. greet(\"kim\")을 부르는 동안 name에 kim이 담겨 있다가 함수가 끝나면 사라져요. 그래서 밖에서 name을 찍으면 NameError가 나요. 덕분에 매개변수 이름은 바깥 변수와 겹쳐도 서로 섞이지 않아요. 19의 calc_total(cart, menu)에서 menu 칸은 바깥의 menu 딕셔너리와 이름만 같은 다른 칸이었어요." + REAL)

o = [sec("l-life")] + head(EB3, "부를 때마다 처음부터 새로 만들어요", K3)
o += cell({"id": "c-l3", "lines": ["def add_stamp():", "    stamp = 0", "    stamp += 1", '    print("도장", stamp)', "", "add_stamp()", "add_stamp()", "add_stamp()"], "n": 3, "out": ["도장 1", "도장 1", "도장 1"]}, 96, 200, 900, sel="c-l3")
for i in range(3):
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:{1050 + i * 262}px;top:200px;width:240px;height:260px;background:{CARD};border:3px solid {K3};border-radius:20px;padding:18px 20px;display:flex;flex-direction:column;gap:14px;align-items:center">'
             + p(f"font-size:22px;font-weight:700;color:{K3}", ["첫째", "둘째", "셋째"][i] + " 부르기")
             + p(f"font-family:{MONO};font-size:24px;color:{GRAY}", "stamp = 0") + p(f"font-family:{MONO};font-size:24px;color:{GRAY}", "stamp += 1")
             + chip("1", K3, K3BG, 30) + '</div>')
o.append(warn(1050, 500, 774, 330, "도장이 쌓이지 않아요", "부를 때마다 새 상자에서 stamp = 0부터 시작해요. 끝나면 상자째 사라져서 지난번 값을 기억하지 못해요.", ' data-build-in="rise order 4"'))
o.append(note_card(96, 680, 900, 180, "쌓으려면 바깥에 둬야 해요", "다음 파트에서 바깥 변수를 읽고 바꾸는 법을 봐요.", GR, ' data-build-in="rise order 5"'))
o.append(caption("지역 변수는 부를 때마다 새로 생기고, 끝나면 사라져요.", 920))
W("l-life", o, "손님이 올 때마다 도장을 하나씩 찍으려고 add_stamp를 만들었어요. 세 번 불렀는데 도장이 1, 1, 1이에요. 부를 때마다 새 상자에서 stamp = 0부터 시작하고, 끝나면 상자째 사라지기 때문이에요. 지역 변수는 지난번 값을 기억하지 못해요. 값을 쌓으려면 함수 밖에 변수를 둬야 해요. 다음 파트에서 바깥 변수를 읽고 바꾸는 법을 봐요." + REAL)

# ---------- part 4 ----------
o = [sec("g-read")] + head(EB4, "함수 밖에서 만든 변수는 안에서 읽을 수 있어요", K4)
o += cell({"id": "c-g1", "lines": ['shop = "KANT 카페"', "", "def hello():", '    print(f"{shop}에 어서 오세요")', "", "hello()"], "n": 1, "out": ["KANT 카페에 어서 오세요"]}, 96, 200, 900, sel="c-g1")
o.append(hl(96, 200, 900, 0, 1, "mark", 1, "밖에서 만듦"))
o.append(hl(96, 200, 900, 3, 1, "run", 2, "안에서 읽음"))
o.append(f'<div data-build-in="rise order 1" style="position:absolute;left:1050px;top:200px;width:774px;height:560px;background:#EFF3FB;border:3px solid {K4};border-radius:24px;padding:22px 28px">'
         + p(f"font-size:24px;font-weight:700;color:{K4}", "밖 (전역)")
         + '<div style="position:absolute;left:28px;top:76px">' + chip('shop = "KANT 카페"', K4, K4BG, 26) + '</div>'
         + f'<div style="position:absolute;left:28px;top:220px;width:714px;height:300px;background:{CARD};border:3px solid {K3};border-radius:20px;padding:20px 24px">'
         + p(f"font-size:24px;font-weight:700;color:{K3}", "hello() 안 (지역)")
         + p(f"position:absolute;left:24px;top:90px;font-family:{MONO};font-size:24px;color:{INK};white-space:pre", e('print(f"{shop}에 ...")'))
         + p(f"position:absolute;left:24px;top:170px;width:660px;font-size:22px;line-height:1.5;color:{SUB}", "안에 shop이 없으면 바깥에서 찾아요") + '</div></div>')
o.append(note_card(96, 520, 900, 340, "전역 변수", "함수 밖, 노트북 셀에서 만든 변수예요. 모든 함수 안에서 읽을 수 있어요. 가게 이름처럼 바뀌지 않는 값에 써요.", K4, ' data-build-in="rise order 3"'))
o.append(caption("함수 안에서 이름을 찾을 땐 안부터 보고, 없으면 밖을 봐요.", 920))
W("g-read", o, "shop은 함수 밖에서 만들었어요. 이런 변수를 전역 변수라고 해요. hello 안에는 shop이 없지만 찍어 보면 KANT 카페가 잘 나와요. 함수 안에서 이름을 찾을 때 먼저 안을 보고, 없으면 바깥을 보기 때문이에요. 그래서 함수 안에서 전역 변수를 읽을 수 있어요. 가게 이름처럼 바뀌지 않는 값은 전역 변수로 두고 읽기만 해도 괜찮아요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p4", "전역 변수"))

o = [sec("g-same")] + head(EB4, "안에서 같은 이름에 넣으면 새 지역 변수가 생겨요", K4)
o += cell({"id": "c-g2", "lines": ["price = 4500", "", "def set_price():", "    price = 5000", '    print("안:", price)', "", "set_price()", 'print("밖:", price)'], "n": 2, "out": ["안: 5000", "밖: 4500"]}, 96, 200, 900, sel="c-g2")
o.append(hl(96, 200, 900, 3, 1, "mark", 1, "새 지역 변수"))
o.append(var_box("v-out", "밖 price", "4500", 1050, 200, K4, 360, ' data-build-in="rise order 1"'))
o.append(var_box("v-in", "안 price", "5000", 1464, 200, K3, 360, ' data-build-in="rise order 2"'))
o.append(note_card(1050, 470, 774, 390, "이름만 같은 다른 상자예요", "함수 안에서 price = 5000처럼 값을 넣으면 안쪽에 price를 새로 만들어요. 바깥 price는 손대지 않아요. 함수가 끝나면 안쪽 price만 사라져요.", K3, ' data-build-in="rise order 3"'))
o.append(note_card(96, 620, 900, 240, "가격을 바꾸려던 거라면", "바깥 price는 그대로 4500이에요. 바깥 값을 바꾸는 법은 두 장 뒤에 봐요.", OR, ' data-build-in="rise order 4"'))
o.append(caption("함수 안에서 = 로 값을 넣으면 그 이름은 지역 변수가 돼요.", 920))
W("g-same", o, "바깥에 price 4500이 있어요. set_price 안에서 price = 5000을 넣고 찍으면 5000이 나와요. 그런데 밖에서 다시 찍으면 4500 그대로예요. 함수 안에서 = 로 값을 넣으면 바깥 변수를 바꾸는 게 아니라 같은 이름의 지역 변수를 새로 만들기 때문이에요. 이름만 같고 서로 다른 상자 두 개예요. 바깥 값을 바꾸고 싶었다면 이 방법으로는 안 돼요." + REAL)

o = [sec("g-unbound")] + head(EB4, "읽다가 바꾸면 UnboundLocalError가 나요", K4)
o += cell({"id": "c-g3", "lines": ["count = 0", "", "def visit():", "    count = count + 1", "", "visit()"], "n": 3, "out": ["UnboundLocalError: cannot access local variable 'count' where it is not associated with a value"], "err": True}, 96, 200, 1728, sel="c-g3")
o.append(hl(96, 200, 1728, 3, 1, "err", 1, "count는 지역 변수로 정해짐"))
st_ = [("1", "count = ... 이 함수 안에 있어요", "그래서 count는 이 함수의 지역 변수예요"), ("2", "오른쪽 count + 1을 먼저 계산해요", "지역 count를 읽으려는데"), ("3", "지역 count에는 아직 값이 없어요", "UnboundLocalError")]
for i, (n_, a_, b_) in enumerate(st_):
    o.append(f'<div data-build-in="rise order {i + 2}" style="position:absolute;left:96px;top:{500 + i * 120}px;width:1100px;height:104px;background:{CARD};border:2px solid {LINE};border-radius:16px;padding:0 24px;display:flex;flex-direction:row;align-items:center;gap:20px">'
             + num(int(n_), RED if i == 2 else K4, 30) + p(f"width:520px;flex:none;font-size:25px;font-weight:700;color:{INK}", e(a_)) + p(f"flex:1;font-size:23px;color:{RED if i == 2 else SUB}", e(b_)) + '</div>')
o.append(note_card(1240, 500, 584, 344, "앞 장과 같은 규칙이에요", "함수 안에서 = 로 넣는 이름은 지역 변수예요. 읽기만 하면 바깥을 보지만, 넣는 순간 지역 변수가 돼요.", K4, ' data-build-in="rise order 5"'))
W("g-unbound", o, "방문자 수를 세려고 함수 안에서 count = count + 1을 했어요. 바깥에 count가 있는데도 UnboundLocalError가 나요. 메시지는 지역 변수 count에 아직 값이 없어서 읽을 수 없다는 뜻이에요. 파이썬은 실행하기 전에 함수 몸통을 훑어서 = 로 값을 넣는 이름을 지역 변수로 정해요. 그래서 count는 지역 변수가 됐고, 오른쪽 count + 1을 계산하려고 지역 count를 읽는데 아직 아무 값도 없어요. 앞 장의 규칙이 그대로 적용된 거예요." + REAL)

o = [sec("g-global")] + head(EB4, "global을 적으면 바깥 변수를 바꿔요", K4)
o += cell({"id": "c-g4", "lines": ["count = 0", "", "def visit():", "    global count", "    count = count + 1", "", "visit()", "visit()", "visit()", "print(count)"], "n": 4, "out": ["3"]}, 96, 200, 900, sel="c-g4")
o.append(hl(96, 200, 900, 3, 1, "mark", 1, "바깥 count를 써요"))
o.append(var_box("v-cnt", "밖 count", "0 → 3", 1050, 200, K4, 774, ' data-build-in="rise order 2"'))
o.append(note_card(1050, 470, 774, 200, "global count", "함수 첫 줄에 적으면, 이 함수 안의 count는 바깥 count라는 뜻이에요.", K4, ' data-build-in="rise order 3"'))
o.append(warn(1050, 700, 774, 190, "있다는 것만 알아 둬요", "여러 함수가 바깥 값을 바꾸면 어디서 바뀌었는지 찾기 어려워요.", ' data-build-in="rise order 4"', OR))
o.append(caption("global은 꼭 필요할 때만 써요. 다음 장에서 더 나은 방법을 봐요.", 920))
W("g-global", o, "함수 첫 줄에 global count를 적으면 이 함수 안의 count는 새 지역 변수가 아니라 바깥 count라는 뜻이 돼요. 그래서 세 번 부르면 바깥 count가 3이 돼요. 이런 방법이 있다는 것만 알아 두면 돼요. 함수가 여러 개인데 모두 바깥 값을 바꾸면, 값이 이상해졌을 때 어느 함수가 바꿨는지 찾기 어려워요. 다음 장에서 return으로 푸는 방법과 비교해요." + REAL)

o = [sec("g-return")] + head(EB4, "바깥 값을 바꿀 땐 return으로 돌려받아요", K4)
o.append(label("global로 바꾸기", 96, 196, GRAY, ' data-build-in="fade order 1"', 846, 26))
o += cell({"id": "c-g4b", "lines": ["count = 0", "", "def visit():", "    global count", "    count = count + 1", "", "visit()", "visit()", "visit()", "print(count)"], "n": 4, "out": ["3"]}, 96, 240, 846, attrs=' data-build-in="rise order 1"')
o.append(label("return으로 돌려받기", 978, 196, K4, ' data-build-in="fade order 2"', 846, 26))
o += cell({"id": "c-g5", "lines": ["def visit(count):", "    return count + 1", "", "count = 0", "count = visit(count)", "count = visit(count)", "count = visit(count)", "print(count)"], "n": 5, "out": ["3"]}, 978, 240, 846, attrs=' data-build-in="rise order 2"')
o.append(hl(978, 240, 846, 4, 3, "run", 3, "바뀌는 곳이 보여요"))
o.append(note_card(96, 750, 1728, 150, "return 쪽을 권해요", "count가 바뀌는 줄이 count = visit(count)로 눈에 보여요. 함수는 받은 값으로 계산해서 돌려주기만 해요.", K4, ' data-build-in="rise order 4"'))
W("g-return", o, "같은 방문자 세기를 두 가지로 썼어요. 왼쪽은 global로 함수 안에서 바깥 count를 직접 바꿔요. visit()만 보면 count가 바뀌는지 알 수 없어요. 오른쪽은 count를 인자로 넣고, 1 더한 값을 돌려받아 다시 count에 담아요. count가 바뀌는 줄이 밖에 그대로 보여요. 함수는 받은 값으로 계산해서 돌려주기만 하니까 따로 떼어 확인하기도 쉬워요. 실무에서는 오른쪽처럼 return으로 돌려받는 쪽을 권해요." + REAL)

# ---------- part 5 ----------
o = [sec("m-list")] + head(EB5, "리스트를 넘기고 안에서 append하면 원본이 바뀌어요", K5)
o += cell({"id": "c-n1", "lines": ["def add_item(cart, name):", "    cart.append(name)", "", 'my_cart = ["coffee"]', 'add_item(my_cart, "cake")', 'add_item(my_cart, "latte")', "print(my_cart)"], "n": 1, "out": ["['coffee', 'cake', 'latte']"]}, 96, 200, 900, sel="c-n1")
o.append(chip("my_cart", K4, K4BG, 30, "position:absolute;left:1050px;top:236px"))
o.append(p(f"position:absolute;left:1050px;top:420px;font-family:{MONO};font-size:30px;font-weight:700;line-height:1.2;color:{INK};background:{K3BG};border:3px solid {K3};border-radius:999px;padding:6px 22px", "cart", ' data-build-in="rise order 1"'))
o.append(slots(["coffee", "cake", "latte"], 1400, 280, 130, 96, top_lbl=False, color=K5, bg=K5BG, hi=(0, 1, 2), fs=24))
o.append(f'<svg style="position:absolute;left:1050px;top:200px;width:774px;height:320px" viewBox="0 0 774 320"><defs><marker id="ma1" markerUnits="userSpaceOnUse" markerWidth="24" markerHeight="24" refX="20" refY="12" orient="auto"><path d="M0,0 L24,12 L0,24 z" fill="{K4}"/></marker><marker id="ma2" markerUnits="userSpaceOnUse" markerWidth="24" markerHeight="24" refX="20" refY="12" orient="auto"><path d="M0,0 L24,12 L0,24 z" fill="{K3}"/></marker></defs>'
         f'<polyline points="190,60 340,110" fill="none" stroke="{K4}" stroke-width="5" marker-end="url(#ma1)"/></svg>')
o.append(f'<svg data-build-in="fade order 1" style="position:absolute;left:1050px;top:200px;width:774px;height:320px" viewBox="0 0 774 320"><defs><marker id="ma3" markerUnits="userSpaceOnUse" markerWidth="24" markerHeight="24" refX="20" refY="12" orient="auto"><path d="M0,0 L24,12 L0,24 z" fill="{K3}"/></marker></defs>'
         f'<polyline points="140,240 340,170" fill="none" stroke="{K3}" stroke-width="5" marker-end="url(#ma3)"/></svg>')
o.append(note_card(1050, 560, 774, 300, "이름 두 개, 리스트 하나", "add_item(my_cart, ...)로 부르면 cart도 같은 리스트를 가리켜요. cart로 append하면 my_cart로 봐도 늘어나 있어요.", K5, ' data-build-in="rise order 2"'))
o.append(note_card(96, 560, 900, 300, "return 없이도 바뀌었어요", "함수가 새 값을 만든 게 아니라 받은 리스트 자체를 고쳤어요. 원본을 지키는 법은 22쪽에서 봐요.", None, ' data-build-in="rise order 3"'))
o.append(caption("리스트를 넘기면 복사본이 아니라 같은 리스트가 들어가요.", 920))
W("m-list", o, "장바구니 리스트를 함수에 넘기고 안에서 append했어요. return이 없는데도 밖에서 my_cart를 찍으면 cake과 latte가 들어 있어요. 함수에 리스트를 넘기면 복사본이 아니라 같은 리스트가 들어가요. my_cart와 cart는 이름만 둘이고 리스트는 하나예요. 그래서 cart로 고치면 my_cart로 봐도 바뀌어 있어요. 원본을 지키고 싶으면 22쪽처럼 copy로 복사본을 만들어요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p5", "리스트와 딕셔너리 넘기기"))

o = [sec("m-int")] + head(EB5, "숫자는 안에서 바꿔도 밖이 그대로예요", K5)
o += cell({"id": "c-n2", "lines": ["def add_one(n):", "    n += 1", '    print("안:", n)', "", "x = 1", "add_one(x)", 'print("밖:", x)'], "n": 2, "out": ["안: 2", "밖: 1"]}, 96, 200, 900, sel="c-n2")
o.append(var_box("v-x", "밖 x", "1", 1050, 200, K4, 360, ' data-build-in="rise order 1"'))
o.append(var_box("v-n", "안 n", "1 → 2", 1464, 200, K3, 360, ' data-build-in="rise order 2"'))
cmp_ = [("n += 1, n = ...", "새 값을 넣어요", "밖은 그대로", K3), ("cart.append(...)", "받은 리스트를 고쳐요", "밖도 바뀌어요", K5), ("stock[name] -= 1", "받은 딕셔너리 칸을 고쳐요", "밖도 바뀌어요", K5)]
for i, (k, a_, b_, c) in enumerate(cmp_):
    o.append(f'<div data-build-in="rise order {i + 3}" style="position:absolute;left:96px;top:{610 + i * 104}px;width:1728px;height:90px;background:{CARD};border:2px solid {LINE};border-left:10px solid {c};border-radius:16px;padding:0 26px;display:flex;flex-direction:row;align-items:center;gap:24px">'
             + p(f"width:420px;flex:none;font-family:{MONO};font-size:26px;font-weight:700;color:{c};white-space:pre", e(k)) + p(f"width:520px;flex:none;font-size:25px;color:{INK}", e(a_)) + p(f"flex:1;font-size:25px;font-weight:700;color:{c}", e(b_)) + '</div>')
W("m-int", o, "이번에는 숫자를 넘겼어요. 안에서 n += 1을 하면 n은 2가 되지만 밖의 x는 1 그대로예요. n += 1은 n이라는 이름에 새 값 2를 넣는 일이라서 x와는 상관이 없어요. 앞 장의 append는 받은 리스트 자체를 고쳐서 밖에서도 바뀌었어요. 정리하면, 함수 안에서 = 로 새 값을 넣으면 밖은 그대로예요. 리스트나 딕셔너리를 메서드나 [키]로 고치면 밖도 바뀌어요." + REAL)

o = [sec("m-dict")] + head(EB5, "딕셔너리를 넘기면 재고를 바로 줄일 수 있어요", K5)
o += cell({"id": "c-n3", "lines": ["def sell(stock, name):", "    stock[name] -= 1", "", 'stock = {"coffee": 3, "latte": 1}', 'sell(stock, "latte")', 'sell(stock, "coffee")', "print(stock)"], "n": 3, "out": ["{'coffee': 2, 'latte': 0}"]}, 96, 200, 900, sel="c-n3")
o.append(label("부르기 전", 1050, 200, GRAY, ' data-build-in="fade order 1"', 774, 24))
o.append(lockers([("coffee", "3"), ("latte", "1")], 1050, 240, 220, 160, K5, K5BG, attrs=' data-build-in="rise order 1"'))
o.append(label("두 번 부른 뒤", 1050, 440, K5, ' data-build-in="fade order 2"', 774, 24))
o.append(lockers([("coffee", "2"), ("latte", "0")], 1050, 480, 220, 160, K5, K5BG, hi=(0, 1), attrs=' data-build-in="rise order 2"'))
o.append(note_card(96, 560, 900, 300, "global이 필요 없어요", "stock = 새 딕셔너리로 바꾼 게 아니라 받은 딕셔너리의 칸만 고쳤어요. 그래서 바깥 stock이 그대로 바뀌어요.", K5, ' data-build-in="rise order 3"'))
o.append(caption("받은 딕셔너리의 칸을 고치면 원본 딕셔너리가 바뀌어요.", 920))
W("m-dict", o, "18에서 재고를 줄일 때 쓴 stock[o] -= 1을 함수로 만들었어요. 재고 딕셔너리와 메뉴 이름을 받아서 그 칸을 1 줄여요. 두 번 부른 뒤 밖에서 찍으면 latte는 0, coffee는 2로 바뀌어 있어요. 4파트의 count와 달리 global이 필요 없어요. stock에 새 딕셔너리를 넣은 게 아니라 받은 딕셔너리의 칸만 고쳤기 때문이에요." + REAL)

o = [sec("m-copy")] + head(EB5, "원본을 지키려면 copy()로 새로 만들어 돌려줘요", K5)
o += cell({"id": "c-n4", "lines": ["def with_item(cart, name):", "    new_cart = cart.copy()", "    new_cart.append(name)", "    return new_cart", "", 'my_cart = ["coffee"]', 'big_cart = with_item(my_cart, "cake")', "print(my_cart)", "print(big_cart)"], "n": 4, "out": ["['coffee']", "['coffee', 'cake']"]}, 96, 200, 1000, sel="c-n4")
o.append(hl(96, 200, 1000, 1, 1, "mark", 1, "복사본"))
o.append(label("my_cart", 1150, 200, K4, ' data-build-in="fade order 2"', 674, 26))
o.append(slots(["coffee"], 1150, 246, 150, 90, top_lbl=False, color=K4, bg=K4BG, hi=(0,), fs=24, attrs=' data-build-in="rise order 2"'))
o.append(label("big_cart", 1150, 380, K5, ' data-build-in="fade order 3"', 674, 26))
o.append(slots(["coffee", "cake"], 1150, 426, 150, 90, top_lbl=False, color=K5, bg=K5BG, hi=(0, 1), fs=24, attrs=' data-build-in="rise order 3"'))
o.append(note_card(1150, 560, 674, 300, "언제 어느 쪽?", "원본을 고치는 게 목적이면 앞 장들처럼 바로 고쳐요. 원본은 두고 결과만 받고 싶으면 copy()로 새로 만들어 return해요.", K5, ' data-build-in="rise order 4"'))
o.append(caption("함수가 받은 리스트를 고칠지, 새로 만들어 돌려줄지 정해서 써요.", 920))
W("m-copy", o, "원본 장바구니는 그대로 두고 하나 더한 장바구니를 따로 받고 싶을 때가 있어요. 함수 안에서 13의 copy로 복사본을 만들고, 복사본에 append한 뒤 return해요. my_cart는 coffee만 그대로이고 big_cart는 cake까지 들어 있어요. 원본을 바꾸는 게 목적이면 앞에서처럼 바로 고치고, 원본을 지키고 싶으면 복사본을 만들어 돌려줘요." + REAL)

# ---------- part 6 ----------
o = [sec("x-order")] + head(EB6, "주문 함수: 기본값과 재고 딕셔너리", K6)
TO = ["def take_order(stock, name, qty=1):", "    if stock[name] < qty:", '        print(f"{name} {qty}개: 재고가 {stock[name]}개뿐이에요")', "        return False", "    stock[name] -= qty", '    print(f"{name} {qty}개 나갔어요")', "    return True", "", 'stock = {"coffee": 3, "latte": 1, "cake": 2}', 'take_order(stock, "coffee", 2)', 'take_order(stock, "latte")', 'take_order(stock, "latte")', 'take_order(stock, "cake", qty=3)', "print(stock)"]
o += cell({"id": "c-x1", "lines": TO, "n": 1, "out": ["coffee 2개 나갔어요", "latte 1개 나갔어요", "latte 1개: 재고가 0개뿐이에요", "cake 3개: 재고가 2개뿐이에요", "{'coffee': 1, 'latte': 0, 'cake': 2}"], "wide": False}, 96, 186, 1200, sel="c-x1")
o.append(hl(96, 186, 1200, 0, 1, "mark", 1, "qty=1"))
o.append(hl(96, 186, 1200, 3, 1, "run", 2, "모자라면 끝"))
o.append(hl(96, 186, 1200, 4, 1, "mark", 3, "원본 재고"))
o.append(note_card(1340, 186, 484, 250, "기본값 qty=1", "한 개 주문이 대부분이라 빼고 불러요.", K2, ' data-build-in="rise order 1"'))
o.append(note_card(1340, 466, 484, 230, "if 안의 return", "재고가 모자라면 바로 나가요. 19에서 본 return이에요.", K4, ' data-build-in="rise order 2"'))
o.append(note_card(1340, 726, 484, 200, "밖의 stock이 줄었어요", "받은 딕셔너리 칸을 고쳤으니까요.", K5, ' data-build-in="rise order 3"'))
W("x-order", o, "오늘 배운 것을 모아 주문 함수를 만들었어요. qty는 기본값 1이라 한 개 주문은 빼고 불러요. 재고가 모자라면 안내를 찍고 return False로 바로 나가요. 19에서 본 return을 만나면 함수가 끝나는 성질이에요. 재고가 있으면 받은 딕셔너리 칸을 줄이고 True를 돌려줘요. 마지막에 밖에서 stock을 찍으면 실제로 줄어 있어요. 돌려준 True, False는 이 셀에서는 쓰지 않았지만, 19의 can_order처럼 if 뒤에 바로 쓸 수 있어요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p6", "실습"))

o = [sec("x-receipt")] + head(EB6, "영수증 함수: 함수 안에서 함수 부르기", K6)
RC = ['menu = {"coffee": 4500, "latte": 5000, "cake": 6500}', "", "def calc_total(cart, menu):", "    total = 0", "    for name, qty in cart.items():", "        total += menu[name] * qty", "    return total", "", "def print_receipt(cart, menu, rate=0):", "    total = calc_total(cart, menu)", "    sale = total * rate // 100", "    for name, qty in cart.items():", '        print(f"{name:<7}{qty}개 {menu[name] * qty:>7,}원")', '    print(f"할인   {rate:>2}% {sale:>7,}원")', '    print(f"결제       {total - sale:>7,}원")']
o += cell({"id": "c-x2", "lines": RC, "n": 2}, 96, 186, 960, sel="c-x2")
o.append(hl(96, 186, 960, 8, 1, "mark", 1, "rate=0"))
o.append(hl(96, 186, 960, 9, 1, "run", 1, "다른 함수"))
o += cell({"id": "c-x3", "lines": ['cart1 = {"coffee": 2, "cake": 1}', 'cart2 = {"latte": 3, "cake": 2}', "print_receipt(cart1, menu)", 'print("---")', "print_receipt(cart2, menu, rate=10)"], "n": 3, "out": ["coffee 2개   9,000원", "cake   1개   6,500원", "할인    0%       0원", "결제        15,500원", "---", "latte  3개  15,000원", "cake   2개  13,000원", "할인   10%   2,800원", "결제        25,200원"], "wide": True}, 1090, 186, 734, attrs=' data-build-in="rise order 2"')
o.append(p(f"position:absolute;left:96px;top:830px;width:960px;font-size:28px;font-weight:700;line-height:1.4;color:{INK}", "할인이 없으면 rate를 빼고, 있을 때만 rate=10처럼 이름을 붙여 넣어요.", ' data-build-in="rise order 3"'))
W("x-receipt", o, "17에서 쓴 장바구니 딕셔너리로 영수증을 찍어요. calc_total은 합계만 돌려주고, print_receipt는 그 함수를 불러 합계를 받은 뒤 할인과 결제 금액을 찍어요. 할인율 rate는 기본값 0이라서 할인이 없으면 빼고 불러요. 둘째 손님만 rate=10으로 키워드 인자를 넣었어요. 한글은 두 칸을 차지해서 13에서 본 것처럼 할인, 결제 뒤 빈칸 수를 맞췄어요." + REAL)

o = [sec("x-point")] + head(EB6, "적립 함수: get과 기본값으로 포인트 쌓기", K6)
PT = ["def add_point(points, name, amount, rate=5):", "    points[name] = points.get(name, 0) + amount * rate // 100", "", 'points = {"kim": 300}', 'add_point(points, "kim", 9000)', 'add_point(points, "lee", 6500)', 'add_point(points, "lee", 10000, rate=10)', "print(points)"]
o += cell({"id": "c-x4", "lines": PT, "n": 4, "out": ["{'kim': 750, 'lee': 1325}"]}, 96, 200, 1160, sel="c-x4")
o += table(1290, 200, 534, [("부르기", 150), ("더한 값", 120), ("합", 100)], [("kim 9000", "450", "750"), ("lee 6500", "325", "325"), ("lee 10000", "1000", "1325")], 1, K4, 76)
o.append(note_card(96, 600, 560, 270, "rate=5", "평소 적립률은 5%예요. 행사 때만 rate=10으로 넣어요.", K2, ' data-build-in="rise order 4"'))
o.append(note_card(686, 600, 560, 270, "get(name, 0)", "처음 온 손님 lee는 키가 없어서 15의 기본값 0에서 시작해요.", K4, ' data-build-in="rise order 5"'))
o.append(note_card(1276, 600, 548, 270, "return 없이 쌓여요", "받은 딕셔너리에 키를 넣고 고쳤어요.", K5, ' data-build-in="rise order 6"'))
W("x-point", o, "손님별 포인트 딕셔너리에 결제 금액의 일부를 적립해요. 적립률 rate는 기본값 5%이고, 행사 때만 rate=10으로 넣어요. 처음 온 lee는 딕셔너리에 키가 없어서 15에서 배운 get(name, 0)으로 0에서 시작해요. kim은 300에 9000원의 5%인 450을 더해 750이 돼요. 받은 딕셔너리에 바로 넣으니 return 없이도 밖의 points에 쌓여요." + REAL)

# ---------- wrap up ----------
o = [sec("trouble")] + head("정리", "막히면 오류의 마지막 줄을 봐요", RED)
tr = [("SyntaxError: parameter without a default follows ...", "def 줄에서 기본값 칸을 앞에 뒀어요", "기본값 칸을 뒤로"),
      ("SyntaxError: positional argument follows keyword argument", "부를 때 이름 없는 값을 뒤에 적었어요", "위치 인자를 앞으로"),
      ("NameError: name 'total' is not defined", "함수 안의 지역 변수를 밖에서 썼어요", "return으로 돌려받기"),
      ("UnboundLocalError: cannot access local variable", "함수 안에서 바깥 변수를 읽다가 바꿨어요", "인자로 받고 return"),
      ("함수 안에서 바꿨는데 밖이 그대로예요", "안에서 = 로 새 지역 변수를 만들었어요", "x = 함수(x)로 받기"),
      ("함수에 넘긴 리스트가 바뀌었어요", "받은 리스트를 append로 고쳤어요", "copy()로 복사해 쓰기"),
      ("부를 때마다 값이 처음으로 돌아가요", "지역 변수는 부를 때마다 새로 생겨요", "값을 밖에 두고 넘기기")]
o.append('<div style="position:absolute;left:96px;top:196px;width:1728px;height:724px;display:flex;flex-direction:column;gap:8px">')
for i, (q, a_, cmd) in enumerate(tr, 1):
    o.append(f'<div data-build-in="rise order {min(i, 6)}" style="flex:1;display:flex;flex-direction:row;gap:26px;align-items:center;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:6px 30px">'
             + num(i, RED, 30)
             + '<div style="flex:1;display:flex;flex-direction:column;gap:2px">' + p(f"{'font-family:' + MONO + ';' if q.isascii() else ''}font-size:22px;font-weight:700;color:{INK};white-space:nowrap", e(q)) + p(f"font-size:21px;color:{SUB}", e(a_)) + '</div>'
             + p(f"width:380px;flex:none;{'font-family:' + MONO + ';font-size:22px;' if cmd.isascii() else 'font-size:23px;'}font-weight:700;line-height:1.4;color:{INK};background:#EEEFF2;padding:6px 18px;border-radius:12px;white-space:pre", e(cmd)) + '</div>')
o.append('</div>')
o.append(caption("헷갈리면 함수 안과 밖에서 print로 같은 변수를 찍어 비교해 봐요.", 950))
W("trouble", o, "이번 챕터에서 자주 만나는 일을 모았어요. 1번과 2번은 기본값과 키워드 인자의 순서 규칙이에요. 3번과 4번은 지역 변수와 전역 변수를 섞어 쓸 때 나요. 5번부터 7번은 오류 없이 결과만 이상한 경우예요. 함수 안과 밖에서 같은 변수를 찍어 보면 어느 상자의 값인지 보여요.", ("trouble", "정리"))

o = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>']
cheat = [('def f(a, b="M"):', "기본값은 뒤 칸에", K2), ("f(1, b=2)", "키워드 인자는 뒤에", K2), ("지역 변수", "안에서 만들고 끝나면 사라져요", K3), ("전역 변수", "밖에서 만들고 안에서 읽어요", K4),
         ("global x", "바깥 x 바꾸기, 되도록 피하기", K4), ("x = f(x)", "return으로 돌려받기", K4), ("cart.append()", "넘긴 리스트는 원본이 바뀌어요", K5), ("cart.copy()", "원본 지키기", K5)]
for i, (k, d, c) in enumerate(cheat):
    x, y = 96 + (i % 4) * 438, 200 + (i // 4) * 290
    o.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:414px;height:264px;background:{CARD};border:2px solid {LINE};border-top:10px solid {c};border-radius:20px;padding:28px 28px;display:flex;flex-direction:column;gap:20px">'
             + (mono(k, 26 if len(k) <= 17 else 22, c, "#F6F5F1", "align-self:flex-start") if k.isascii() else p(f"font-size:30px;font-weight:900;color:{c}", e(k))) + p(f"font-size:28px;font-weight:700;color:{INK}", d) + '</div>')
o.append(f'<div style="position:absolute;left:96px;top:780px;width:1728px;height:210px;background:{CARD};border:2px solid {LINE};border-radius:20px;padding:24px 36px;display:flex;flex-direction:column;justify-content:center;gap:14px">'
         + p(f"font-size:30px;font-weight:700;color:{INK}", "함수 안에서 = 로 넣은 이름은 지역 변수")
         + p(f"font-size:30px;font-weight:700;color:{INK}", "바깥 값을 바꿀 땐 global보다 인자와 return") + '</div>')
W("cheatsheet", o, "이번 챕터에서 쓴 모양을 한 장에 모았어요. 기본값 칸은 def 줄 뒤쪽에 두고, 키워드 인자는 부를 때 뒤쪽에 적어요. 함수 안에서 만든 변수와 매개변수는 지역 변수, 밖에서 만든 변수는 전역 변수예요. 바깥 값을 바꿔야 하면 global보다 인자로 넣고 return으로 돌려받는 쪽을 써요. 리스트와 딕셔너리는 넘긴 원본이 바뀐다는 점을 기억해요. 19와 20으로 함수를 마쳤어요.")

# ---------- toc ----------
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
parts = [("Lightbulb", K1, "왜 필요한가", "매번 적는 M, 사라진 total, 기본값과 안팎 그림, 가장 짧은 기본값", "s-why", "s-min"),
         ("Key", K2, "기본값과 키워드 인자", "여러 기본값, 칸 이름으로 넣기, 순서 규칙, print와 sorted에서 본 키워드 인자", "k-default", "k-known"),
         ("Lock", K3, "지역 변수", "안에서 만든 변수, 매개변수, 부를 때마다 새로", "l-local", "l-life"),
         ("Globe", K4, "전역 변수", "밖의 변수 읽기, 같은 이름, UnboundLocalError, global, return과 비교", "g-read", "g-return"),
         ("Archive", K5, "리스트와 딕셔너리 넘기기", "append로 원본 바뀌기, 숫자와 비교, 재고 줄이기, copy", "m-list", "m-copy"),
         ("Star", K6, "실습", "주문 함수, 영수증 함수, 포인트 적립", "x-order", "x-point")]
TOC_NOTE = "여섯 파트로 나눴어요. 1파트는 19의 함수로는 불편한 두 장면과 큰 그림이에요. 2파트는 기본값과 키워드 인자예요. 3파트와 4파트는 지역 변수와 전역 변수로, 이번 챕터의 중심이에요. 5파트는 리스트와 딕셔너리를 넘겼을 때 원본이 바뀌는 경우, 6파트는 카페 실습이에요. 파트마다 새 커널에서 위에서부터 차례로 실행해요."

DECK_TITLE = "함수 2 (기본값, 지역 변수와 전역 변수)"
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
