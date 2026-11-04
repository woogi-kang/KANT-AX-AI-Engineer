"""Generates every slide of the control flow 1 deck (17, if) and slides/deck.json.

Story: keeps writing in basics.ipynb from chapters 12-16. Starts from the KeyError that stopped chapter 15's menu,
draws if as a fork in the road, then adds else, elif, and, or, not and empty values. Part 4 puts if inside for and
opens up the read-only "참고" code of chapters 15 and 16. Ends with the café: discounts, grades and a receipt.
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


EB1 = "1. 참과 거짓으로 길 고르기"
EB2 = "2. if, else, elif"
EB3 = "3. 조건 합치기"
EB4 = "4. for와 함께, 줄여 쓰기"
EB5 = "5. 자주 나는 오류"
EB6 = "6. 실습"
K5, K5BG = RED, "#F8E6E6"
K6, K6BG = PUR, "#ECE7F8"
MENU = 'menu = {"coffee": 4500, "latte": 5000, "cake": 6500}'
REAL = " 출력은 실제로 실행한 결과예요."
YES, NO = GR, RED


def yes_no(left, top, kind, text, order=None, w=None):
    """A small chip that says which way a condition went."""
    at = f' data-build-in="rise order {order}"' if order else ""
    c, b = (GR, "#E6F4EC") if kind else (RED, "#F8E6E6")
    ws = f"width:{w}px;" if w else ""
    return p(f"position:absolute;left:{left}px;top:{top}px;{ws}font-size:24px;font-weight:700;color:{c};background:{b};border-radius:10px;padding:6px 16px;white-space:nowrap", e(text), at)


# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#F2B27A;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
       '<h1 style="font-size:92px;font-weight:900;line-height:1.1;color:#F6F5F1">제어문 1<br>조건문 if</h1>',
       '<p style="font-size:40px;line-height:1.4;color:#BFC6D4">조건에 따라<br>다른 줄을 실행하기</p>']
cov.append(f'<div style="position:absolute;left:940px;top:300px;width:860px;height:480px;background:#252B36;border-radius:24px;padding:44px 48px;display:flex;flex-direction:column;justify-content:center;gap:16px">')
for line, c in [("if money >= price:", "#9DBDEB"), ('    print("주문할 수 있어요")', "#E6E9EF"), ("elif total >= 10000:", "#E3B877"), ('    print("5% 할인")', "#E6E9EF"), ("else:", "#E3B877"), ('    print("할인 없음")', "#E6E9EF")]:
    cov.append(p(f"font-family:{MONO};font-size:36px;font-weight:700;line-height:1.45;color:{c};white-space:pre", e(line)))
cov.append('</div>')
W("cover", cov, "12에서 비교와 and, or, not을 배웠고, 13에서 for로 리스트를 돌았어요. 15와 16에서는 if가 들어간 코드를 참고 칸에 두고 읽기만 했어요. 이번 챕터에서 그 if를 직접 써요. 조건이 True면 들여쓴 줄을 실행하고, False면 건너뛰어요. 같은 카페 예제로 이어 가고, 18에서는 while과 break로 반복을 다뤄요.", ("intro", "들어가기"))

ORDER.append("toc")   # written last, after page numbers are known

# ---------- ready ----------
o = [sec("ready")] + head("들어가기", "16에서 이어서 해요", JP)
done = [("hello-uv 노트북, 커널 .venv", "09 · 25–27쪽"), ("비교 ==, >=, and, or, not", "12 · 3파트"), ("리스트, for, f-string", "13"), ("in과 not in", "14"), ("딕셔너리 menu와 get", "15"), ("집합과 discard", "16")]
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
W("ready", o, "09에서 만든 hello-uv 폴더를 VS Code로 열고, 12부터 쓰던 basics.ipynb를 다시 열어요. 12의 비교와 and, or, not, 13의 for와 f-string, 14의 in, 15의 딕셔너리, 16의 집합을 그대로 써요. 슬라이드의 출력은 tools/demo.sh가 hello-uv 커널에서 같은 셀을 실제로 실행한 결과예요. 셀 번호는 파트마다 [1]부터 다시 셌어요.")

# ---------- part 1 ----------
o = [sec("i-why")] + head(EB1, "지금까지는 적은 줄이 모두 실행됐어요", K1)
o += cell({"id": "c-why", "lines": [MENU, 'order = "tea"', "print(menu[order])"], "n": 1, "out": ["KeyError: 'tea'"], "err": True}, 96, 200, 1000, sel="c-why")
o.append(note_card(96, 430, 1000, 200, "메뉴판에 없는 주문이 오면 멈춰요", "셀은 위에서 아래로 한 줄씩 모두 실행해요. tea가 없어도 print(menu[order])를 그대로 실행해서 KeyError가 나요.", RED, ' data-build-in="rise order 1"'))
o.append(note_card(96, 660, 1000, 200, "있을 때만 꺼내고 싶어요", "\"tea가 메뉴판에 있으면 가격을 찍고, 없으면 없다고 말해요\"처럼 조건에 따라 다른 줄을 실행해야 해요.", GR, ' data-build-in="rise order 2"'))
o.append(label("15, 16에서 읽기만 한 코드", 1150, 200, GRAY, ' data-build-in="fade order 3"', 674, 24))
refs = [("15 · get 비교", 'menu["cakee"] if "cakee" in menu else 5000'), ("16 · discard 긴 코드", 'if "juice" in menus:\n    menus.remove("juice")'), ("16 · 중복 없애기 긴 코드", "for o in orders:\n    if o not in kinds:\n        kinds.append(o)")]
y = 244
for i, (t_, code) in enumerate(refs):
    hh = 70 + 32 * (code.count("\n") + 1)
    o.append(f'<div data-build-in="rise order 3" style="position:absolute;left:1150px;top:{y}px;width:674px;height:{hh}px;background:#FAF8F3;border:3px dashed #B4B9C3;border-radius:16px;padding:12px 22px;display:flex;flex-direction:column;gap:6px">'
             + p(f"font-size:20px;font-weight:700;color:{GRAY}", e(t_))
             + "".join(p(f"font-family:{MONO};font-size:{19 if len(l) > 40 else 22}px;line-height:1.4;white-space:pre;color:{INK}", e(l)) for l in code.split("\n")) + '</div>')
    y += hh + 16
o.append(caption("이번 챕터에서 이 if를 직접 써요.", 920))
W("i-why", o, "지금까지 셀은 위에서 아래로 적은 줄을 모두 실행했어요. 주문이 메뉴판에 없는 tea여도 print(menu[order])를 그대로 실행해서 KeyError가 나요. 원하는 건 메뉴판에 있을 때만 가격을 찍는 거예요. 조건에 따라 실행할 줄을 고르는 문법이 if예요. 15와 16에서 참고 칸에 두고 읽기만 했던 코드가 모두 if를 썼어요. 이번 챕터를 마치면 오른쪽 세 코드를 직접 쓸 수 있어요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p1", "참과 거짓으로 길 고르기"))

# big picture: straight road vs fork
o = [sec("i-big")] + head(EB1, "if는 코드에 갈림길을 만들어요", K1)
o.append(label("지금까지 · 한 줄로 쭉", 96, 200, GRAY, "", 600, 26))
o.append(flow(96, 250, 600, 620,
              [dict(x=100, y=0, w=400, h=90, text="money = 5000", color=GRAY), dict(x=100, y=170, w=400, h=90, text="price = 4500", color=GRAY),
               dict(x=100, y=340, w=400, h=90, text='print("주문")', color=GRAY), dict(x=100, y=510, w=400, h=90, text='print("다음 손님")', color=GRAY)],
              [dict(pts=[(300, 92), (300, 166)]), dict(pts=[(300, 262), (300, 336)]), dict(pts=[(300, 432), (300, 506)])]))
o.append(label("if를 쓰면 · 조건으로 길을 골라요", 820, 200, K1, ' data-build-in="fade order 1"', 1000, 26))
o.append(flow(820, 250, 1004, 640,
              [dict(x=60, y=0, w=420, h=86, text="money, price", color=GRAY, order=1),
               dict(x=30, y=150, w=480, h=170, kind="diamond", text="money >= price", color=K1, bg=K1BG, order=2, fs=26),
               dict(x=60, y=384, w=420, h=86, text='print("주문할 수\n있어요")', color=GR, bg="#E6F4EC", order=3, fs=22),
               dict(x=60, y=540, w=420, h=86, text='print("다음 손님")', color=GRAY, order=5)],
              [dict(pts=[(270, 88), (270, 146)], order=2),
               dict(pts=[(270, 322), (270, 380)], color=GR, order=3, label="True", lx=290, ly=330),
               dict(pts=[(270, 472), (270, 536)], color=GR, order=3),
               dict(pts=[(512, 235), (700, 235), (700, 583), (484, 583)], color=RED, order=4, label="False · 건너뛰기", lx=560, ly=190)],
              ' data-build-in="fade order 1"'))
o.append(caption("갈림길은 마름모예요. True면 아래로, False면 옆길로 가요.", 920))
W("i-big", o, "왼쪽은 지금까지 쓰던 코드예요. 위에서 아래로 한 줄로 쭉 가요. 오른쪽은 if를 쓴 코드예요. 마름모가 갈림길이에요. 마름모 안의 조건이 True면 아래로 내려가 주문할 수 있어요를 찍어요. False면 옆길로 돌아가서 그 줄을 건너뛰어요. 두 길은 다음 손님에서 다시 만나요. 이 챕터의 모든 if는 이 그림 하나로 읽을 수 있어요. 다음 장에서 이 그림을 실제 코드로 옮겨요.")

# minimal example
o = [sec("i-min")] + head(EB1, "가장 짧은 if는 두 줄이에요", K1)
c = {"id": "c-min", "lines": ["money = 5000", "price = 4500", "if money >= price:", '    print("주문할 수 있어요")', 'print("다음 손님")'], "n": 2, "out": ["주문할 수 있어요", "다음 손님"]}
o += cell(c, 96, 200, 900, sel="c-min")
o.append(hl(96, 200, 900, 2, 1, "mark", 1, "조건"))
o.append(hl(96, 200, 900, 3, 1, "run", 2, "True라서 실행"))
o.append(hl(96, 200, 900, 4, 1, "mark", 3, "if 밖"))
parts_ = [("if", "만약", K1), ("money >= price", "조건 · True나 False가 나와요", K1), (":", "콜론 · 여기까지가 조건", K1), ("    ", "4칸 들여쓰기 · if 안의 줄", GR)]
for i, (k, d, col) in enumerate(parts_):
    y = 200 + i * 128
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:1060px;top:{y}px;width:764px;height:110px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:0 26px;display:flex;flex-direction:row;align-items:center;gap:22px">'
             + mono(k if k.strip() else "␣␣␣␣", 30, col, K1BG if col == K1 else "#E6F4EC", "min-width:120px;text-align:center") + p(f"font-size:26px;font-weight:700;color:{INK}", e(d)) + '</div>')
o.append(note_card(96, 560, 900, 300, "들여쓴 줄만 if에 속해요", "들여쓴 print는 조건이 True일 때만 실행해요. 들여쓰지 않은 print(\"다음 손님\")은 if와 상관없이 늘 실행해요.", GR, ' data-build-in="rise order 3"'))
o.append(note_card(1060, 716, 764, 150, "들여쓰기는 Tab 한 번", "VS Code는 Tab을 누르면 4칸을 넣어 줘요. 콜론 뒤 Enter를 치면 알아서 들여써요.", None, ' data-build-in="rise order 4"', "padding:16px 26px;gap:6px"))
o.append(caption("if 조건: 다음 줄을 들여쓰면 조건이 True일 때만 실행해요.", 920))
W("i-min", o, "가장 짧은 if예요. if 뒤에 조건을 적고 콜론으로 끝내요. 다음 줄은 4칸 들여써요. 13의 for와 같은 모양이에요. money 5000은 price 4500보다 크거나 같아서 조건이 True예요. 그래서 들여쓴 print를 실행해요. 들여쓰지 않은 마지막 print는 if 밖이라 조건과 상관없이 실행해요. VS Code에서 콜론 뒤에 Enter를 치면 4칸이 저절로 들어가요. 직접 넣을 땐 Tab을 한 번 눌러요." + REAL)

# conditions are bools
o = [sec("i-bool")] + head(EB1, "조건 자리에는 True나 False가 나오는 식을 적어요", K1)
o += cell({"id": "c-bool", "lines": ["print(money >= price)", "print(money == price)", 'print("tea" in menu)', 'print("tea" not in menu)', "print(type(money >= price))"], "n": 3,
           "out": ["True", "False", "False", "True", "<class 'bool'>"]}, 96, 200, 860, sel="c-bool")
ops = [("==", "같아요", "12"), ("!=", "달라요", "12"), ("<  >", "작아요, 커요", "12"), ("<=  >=", "작거나 같아요, 크거나 같아요", "12"), ("in", "들어 있어요", "14"), ("not in", "안 들어 있어요", "14")]
for i, (k, d, ch_) in enumerate(ops):
    y = 200 + i * 108
    o.append(f'<div data-build-in="rise order {1 if i < 4 else 2}" style="position:absolute;left:1010px;top:{y}px;width:814px;height:92px;background:{CARD};border:2px solid {LINE};border-radius:16px;padding:0 24px;display:flex;flex-direction:row;align-items:center;gap:22px">'
             + f'<div style="width:170px;flex:none">' + mono(k, 30, K1, K1BG, "display:inline-block") + '</div>' + p(f"flex:1;font-size:26px;font-weight:700;color:{INK}", e(d)) + p(f"font-size:22px;font-weight:700;color:{GRAY}", ch_ + "에서 배움") + '</div>')
o.append(note_card(96, 680, 860, 190, "bool은 참, 거짓 두 가지 값", "비교와 in의 결과는 True 아니면 False예요. type으로 보면 bool이라고 나와요.", K1, ' data-build-in="rise order 3"'))
o.append(caption("if는 이 True와 False를 보고 길을 골라요.", 920))
W("i-bool", o, "if 뒤에 오는 조건은 12에서 배운 비교식이에요. 비교하면 답은 True 아니면 False였어요. 14의 in과 not in도 True, False로 답했어요. 이 두 값을 묶어서 bool이라고 불러요. type으로 보면 class bool이라고 나와요. if는 조건을 계산한 뒤 True면 들여쓴 줄을 실행하고 False면 건너뛰어요. 셀 [3]은 앞 셀의 money와 price, menu를 그대로 썼어요." + REAL)

# ---------- part 2 ----------
o = [sec("i-false")] + head(EB2, "조건이 False면 들여쓴 줄을 건너뛰어요", K2)
BUYL = ["if money >= price:", '    print("주문할 수 있어요")', 'print("다음 손님")']
o += cell({"id": "c-f1", "lines": ["price = 4500", "money = 5000"] + BUYL, "n": 1, "out": ["주문할 수 있어요", "다음 손님"]}, 96, 200, 840, sel="c-f1")
o += cell({"id": "c-f2", "lines": ["money = 3000"] + BUYL, "n": 2, "out": ["다음 손님"]}, 984, 200, 840, attrs=' data-build-in="rise order 2"')
o.append(hl(96, 200, 840, 3, 1, "run", 1, "실행"))
o.append(hl(984, 200, 840, 2, 1, "skip", 3, "건너뜀"))
o.append(yes_no(96, 560, True, "5000 >= 4500  →  True", 1))
o.append(yes_no(984, 560, False, "3000 >= 4500  →  False", 3))
o.append(note_card(96, 650, 1728, 210, "오류가 아니에요", "False면 들여쓴 줄을 그냥 건너뛰고 if 다음 줄로 가요. 오른쪽 셀은 출력이 한 줄뿐이지만 정상이에요. price는 셀 [1]에서 넣은 4500이 그대로 남아 있어요.", None, ' data-build-in="rise order 4"'))
o.append(caption("같은 코드라도 값에 따라 실행하는 줄이 달라져요.", 920))
W("i-false", o, "같은 if를 money만 바꿔서 두 번 실행해요. 왼쪽은 5000이라 조건이 True고, 들여쓴 print를 실행해요. 오른쪽은 3000이라 조건이 False예요. 들여쓴 print를 건너뛰고 바로 다음 손님을 찍어요. 오류가 난 게 아니라 일부러 건너뛴 거예요. 오른쪽 셀에는 price를 다시 적지 않았어요. 셀 [1]에서 넣은 4500이 그대로 남아 있어요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p2", "if, else, elif"))

o = [sec("i-indent")] + head(EB2, "들여쓴 줄까지가 if에 속해요", K2)
o += cell({"id": "c-i1", "lines": ["money = 3000", "if money >= price:", '    print("주문할 수 있어요")', '    print("커피 나왔어요")', 'print("다음 손님")'], "n": 3, "out": ["다음 손님"]}, 96, 200, 840, sel="c-i1")
o += cell({"id": "c-i2", "lines": ["money = 3000", "if money >= price:", '    print("주문할 수 있어요")', 'print("커피 나왔어요")', 'print("다음 손님")'], "n": 4, "out": ["커피 나왔어요", "다음 손님"]}, 984, 200, 840, attrs=' data-build-in="rise order 2"')
o.append(hl(96, 200, 840, 2, 2, "skip", 1, "if 안 · 둘 다 건너뜀"))
o.append(hl(984, 200, 840, 2, 1, "skip", 3, "if 안 · 건너뜀"))
o.append(hl(984, 200, 840, 3, 1, "err", 3, "if 밖 · 늘 실행"))
o.append(note_card(96, 560, 840, 300, "왼쪽 · 두 줄 모두 들여씀", "돈이 모자라면 두 줄을 모두 건너뛰어요. 커피도 안 나와요.", GR, ' data-build-in="rise order 1"'))
o.append(note_card(984, 560, 840, 300, "오른쪽 · 한 줄만 들여씀", "커피 나왔어요가 if 밖으로 나갔어요. 돈이 모자라도 커피가 나와요. 오류는 안 나지만 틀린 결과예요.", RED, ' data-build-in="rise order 3"'))
o.append(caption("들여쓰기 4칸이 \"어디까지 if인지\"를 정해요.", 920))
W("i-indent", o, "if 안에 여러 줄을 넣으려면 모두 같은 칸만큼 들여써요. 왼쪽은 두 print를 모두 들여써서 돈이 모자라면 둘 다 건너뛰어요. 오른쪽은 커피 나왔어요를 들여쓰지 않았어요. 그 줄은 if 밖이라 조건과 상관없이 실행해요. 돈이 3000원인데도 커피가 나왔어요. 파이썬은 오류를 내지 않아서 직접 찾아야 해요. 다른 언어는 중괄호로 범위를 정하지만 파이썬은 들여쓰기로 정해요." + REAL)

o = [sec("i-else")] + head(EB2, "else는 조건이 False일 때 갈 길이에요", K2)
o += cell({"id": "c-e", "lines": ["money = 3000", "if money >= price:", '    print("주문할 수 있어요")', "else:", '    print(f"{price - money}원 더 필요해요")'], "n": 5, "out": ["1500원 더 필요해요"]}, 96, 200, 900, sel="c-e")
o.append(hl(96, 200, 900, 2, 1, "skip", 1, "건너뜀"))
o.append(hl(96, 200, 900, 4, 1, "run", 1, "실행"))
o.append(flow(1050, 200, 774, 600,
              [dict(x=147, y=0, w=480, h=170, kind="diamond", text="money >= price", color=K2, bg=K2BG, fs=26),
               dict(x=0, y=260, w=340, h=100, text='print("주문할\n수 있어요")', color=GR, bg="#E6F4EC", fs=22, order=2),
               dict(x=434, y=260, w=340, h=100, text="print(f\"...원\n더 필요해요\")", color=RED, bg="#F8E6E6", fs=22, order=2),
               dict(x=147, y=480, w=480, h=90, text="다음 줄", color=GRAY, mono=False, order=3)],
              [dict(pts=[(147, 85), (170, 85), (170, 256)], color=GR, order=2, label="True · if", lx=10, ly=40),
               dict(pts=[(627, 85), (604, 85), (604, 256)], color=RED, order=2, label="False · else", lx=620, ly=40),
               dict(pts=[(170, 362), (170, 420), (330, 420), (330, 476)], order=3), dict(pts=[(604, 362), (604, 420), (444, 420), (444, 476)], order=3)]))
o.append(note_card(96, 560, 900, 300, "둘 중 하나는 꼭 실행해요", "else 뒤에는 조건이 없고 콜론만 붙여요. if와 같은 칸에 맞춰 적고, 그 안은 다시 4칸 들여써요.", K2, ' data-build-in="rise order 3"'))
o.append(caption("if는 True일 때, else는 False일 때. 두 길 중 하나만 가요.", 920))
W("i-else", o, "앞 장에서는 돈이 모자라면 아무 말도 하지 않았어요. else를 붙이면 조건이 False일 때 갈 길을 따로 정해요. else는 if와 같은 칸에 맞춰 적고, 조건 없이 콜론만 붙여요. 그 안은 다시 4칸 들여써요. money가 3000이라 조건이 False고, else 안의 print를 실행해요. 1500원은 price - money를 13의 f-string에 넣어 계산했어요. if와 else 중 하나는 반드시 실행하고, 둘 다 실행하는 일은 없어요." + REAL)

SALEL = ["if total >= 20000:", '    print("10% 할인")', "elif total >= 10000:", '    print("5% 할인")', "else:", '    print("할인 없음")']
o = [sec("i-elif")] + head(EB2, "elif로 갈림길을 여러 개 만들어요", K2)
o += cell({"id": "c-l", "lines": ["total = 12000"] + SALEL, "n": 6, "out": ["5% 할인"]}, 96, 200, 860, sel="c-l")
o.append(hl(96, 200, 860, 1, 1, "skip", 1, "False"))
o.append(hl(96, 200, 860, 3, 2, "run", 2, "True · 실행"))
o.append(hl(96, 200, 860, 5, 2, "skip", 3, "안 봄"))
o.append(flow(1010, 200, 814, 470,
              [dict(x=0, y=0, w=360, h=130, kind="diamond", text=">= 20000", color=K2, bg=K2BG, fs=24),
               dict(x=0, y=170, w=360, h=130, kind="diamond", text=">= 10000", color=K2, bg=K2BG, fs=24, order=1),
               dict(x=40, y=350, w=280, h=80, text="할인 없음", color=GRAY, mono=False, fs=24, order=3),
               dict(x=520, y=25, w=280, h=80, text="10% 할인", color=GR, bg="#E6F4EC", mono=False, fs=24),
               dict(x=520, y=195, w=280, h=80, text="5% 할인", color=GR, bg="#E6F4EC", mono=False, fs=24, order=2)],
              [dict(pts=[(362, 65), (516, 65)], color=GR, label="True", lx=400, ly=20), dict(pts=[(180, 132), (180, 166)], color=RED, order=1),
               dict(pts=[(362, 235), (516, 235)], color=GR, order=2, label="True", lx=400, ly=190), dict(pts=[(180, 302), (180, 346)], color=RED, order=3, label="False", lx=200, ly=306)]))
tb = [("total = 25000", "10% 할인"), ("total = 12000", "5% 할인"), ("total = 3000", "할인 없음")]
for i, (k, r_) in enumerate(tb):
    o.append(row_card(1010, 690 + i * 72, 814, 62, k, r_, "", 4, K2, K2BG, 300))
o.append(note_card(96, 560, 860, 300, "위에서부터 처음 True인 하나만", "elif는 else if를 줄인 말이에요. 앞 조건이 False일 때만 다음 조건을 물어요. True를 만나면 그 길만 가고 나머지는 보지 않아요.", K2, ' data-build-in="rise order 3"'))
o.append(caption("if 하나, elif 여러 개, else 하나. 그중 하나만 실행해요.", 940))
W("i-elif", o, "갈림길이 세 개 이상이면 elif를 써요. else if를 줄인 말이에요. 2만 원 이상이면 10퍼센트, 1만 원 이상이면 5퍼센트, 나머지는 할인 없음이에요. 파이썬은 위에서부터 조건을 하나씩 물어요. total 12000은 20000 이상이 아니라 False라서 elif로 내려가요. 10000 이상은 True라서 5% 할인을 찍고, 아래 else는 보지도 않아요. 오른쪽 아래는 같은 셀을 total만 바꿔 실행한 결과예요. elif는 몇 개든 쓸 수 있고 else는 없어도 돼요." + REAL)

o = [sec("i-order")] + head(EB2, "조건 순서를 바꾸면 결과가 달라져요", K2)
o += cell({"id": "c-o", "lines": ["total = 25000", "if total >= 10000:", '    print("5% 할인")', "elif total >= 20000:", '    print("10% 할인")', "else:", '    print("할인 없음")'], "n": 9, "out": ["5% 할인"]}, 96, 200, 860, sel="c-o")
o.append(hl(96, 200, 860, 1, 2, "err", 1, "먼저 True"))
o.append(hl(96, 200, 860, 3, 2, "skip", 2, "물어보지도 않음"))
o.append(warn(1010, 200, 814, 260, "25000원인데 5% 할인이 나왔어요", "25000은 10000 이상이기도 해서 첫 줄에서 True가 나와요. 그 뒤의 elif는 보지 않아요.", ' data-build-in="rise order 1"'))
o.append(f'<div data-build-in="rise order 3" style="position:absolute;left:1010px;top:490px;width:814px;height:370px;background:{CARD};border:2px solid {LINE};border-top:10px solid {GR};border-radius:20px;padding:24px 30px;display:flex;flex-direction:column;gap:14px">'
         + p(f"font-size:28px;font-weight:700;color:{INK}", "좁은 조건부터 적어요")
         + "".join(p(f"font-family:{MONO};font-size:24px;line-height:1.4;white-space:pre;color:{INK}", e(l)) for l in ["if total >= 20000:      # 좁은 조건", "elif total >= 10000:    # 넓은 조건", "else:"])
         + p(f"font-size:24px;line-height:1.5;color:{SUB}", "앞 장의 순서예요. 25000을 넣으면 10% 할인이 나와요.") + '</div>')
o.append(caption("elif는 위에서부터 묻고 처음 True에서 멈춰요. 큰 금액 조건을 위에 둬요.", 920))
W("i-order", o, "앞 장의 두 조건을 순서만 바꿨어요. total이 25000이면 첫 조건 10000 이상이 이미 True예요. 그래서 5% 할인을 찍고, 아래의 20000 이상은 묻지도 않아요. 오류가 나지 않아서 틀린 줄 모르고 지나치기 쉬워요. 범위가 겹치는 조건은 좁은 쪽, 여기서는 큰 금액 조건을 위에 둬요. 그러면 25000은 첫 줄에서 10% 할인이 되고, 12000은 둘째 줄에서 5% 할인이 돼요." + REAL)

o = [sec("i-ifif")] + head(EB2, "if를 따로 쓰면 둘 다 실행될 수 있어요", K2)
o += cell({"id": "c-ii", "lines": ["total = 25000", "if total >= 20000:", '    print("10% 할인")', "if total >= 10000:", '    print("5% 할인")'], "n": 10, "out": ["10% 할인", "5% 할인"]}, 96, 200, 840, sel="c-ii")
o += cell({"id": "c-ie", "lines": ["total = 25000"] + SALEL, "n": 7, "out": ["10% 할인"]}, 984, 200, 840, attrs=' data-build-in="rise order 2"')
o.append(hl(96, 200, 840, 2, 1, "run", 1, "실행"))
o.append(hl(96, 200, 840, 4, 1, "err", 1, "또 실행"))
o.append(yes_no(96, 512, False, "if 두 개 · 할인을 두 번 받아요", 1))
o.append(yes_no(984, 590, True, "if, elif · 하나만 받아요", 2))
o.append(note_card(96, 580, 840, 280, "if마다 따로 물어요", "if를 두 번 쓰면 갈림길이 두 개예요. 앞에서 True였어도 아래 if를 다시 물어서 둘 다 실행해요.", RED, ' data-build-in="rise order 3"'))
o.append(note_card(984, 680, 840, 180, "하나만 고를 땐 elif", "따로 따로 확인할 일이면 if를 여러 번 써요.", GR, ' data-build-in="rise order 3"', "gap:8px"))
o.append(caption("둘 중 하나만이면 elif, 각각 따로 확인하면 if 여러 개예요.", 920))
W("i-ifif", o, "if를 두 번 쓰면 무엇이 다른지 봐요. 왼쪽은 if를 두 번 썼어요. 첫 if가 True라 10% 할인을 찍고, 둘째 if를 다시 물어요. 25000은 10000 이상이기도 해서 5% 할인도 찍어요. 할인을 두 번 받는 셈이에요. 오른쪽은 elif예요. 처음 True를 만나면 나머지는 보지 않아서 하나만 찍어요. 할인처럼 하나만 골라야 하면 elif를 써요. 회원 쿠폰과 생일 쿠폰처럼 각각 따로 확인할 일이면 if를 여러 번 써요. 오른쪽 셀 [7]은 elif 장에서 total을 25000으로 바꿔 실행한 결과예요." + REAL)

# ---------- part 3 ----------
o = [sec("i-and")] + head(EB3, "and는 두 조건이 모두 True일 때만 True예요", K3)
RIDE = ["if height >= 120 and age >= 7:", '    print("탈 수 있어요")', "else:", '    print("다음에 타요")']
o += cell({"id": "c-a1", "lines": ["height = 130", "age = 9"] + RIDE, "n": 1, "out": ["탈 수 있어요"]}, 96, 200, 840, sel="c-a1")
o += cell({"id": "c-a2", "lines": ["height = 110"] + RIDE, "n": 2, "out": ["다음에 타요"]}, 984, 200, 840, attrs=' data-build-in="rise order 2"')
o += chain([("130 >= 120", "True", "키"), ("9 >= 7", "True", "나이"), ("True and True", "True", "and")], 96, 540, 840, 1, K3)
o += chain([("110 >= 120", "False", "키"), ("9 >= 7", "True", "나이"), ("False and True", "False", "and")], 984, 540, 840, 3, K3)
o.append(caption("12의 놀이기구 조건이에요. 이제 결과로 실행할 줄을 골라요.", 920))
W("i-and", o, "12에서 놀이기구 탑승 조건을 and로 적었어요. 키 120 이상 그리고 7살 이상이에요. 그때는 True, False를 보기만 했는데, 이제 if에 넣어서 실행할 줄을 골라요. 왼쪽은 두 비교가 모두 True라서 탈 수 있어요. 오른쪽은 키만 110으로 바꿨어요. age는 앞 셀의 9가 그대로예요. 키가 False라 and 전체가 False고 else로 가요. 비교를 먼저 계산하고 and를 나중에 해서 괄호가 없어도 돼요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p3", "조건 합치기"))

o = [sec("i-nested")] + head(EB3, "if 안의 if는 and 한 줄로 줄일 수 있어요", K3)
o += cell({"id": "c-n", "lines": ["height = 130", "if height >= 120:", "    if age >= 7:", '        print("탈 수 있어요")'], "n": 3, "out": ["탈 수 있어요"]}, 96, 200, 840, sel="c-n")
o.append(hl(96, 200, 840, 2, 1, "mark", 1, "4칸"))
o.append(hl(96, 200, 840, 3, 1, "run", 1, "8칸"))
o.append(side(984, 200, 840, 270, "and로 줄이면", ["if height >= 120 and age >= 7:", '    print("탈 수 있어요")'], ["탈 수 있어요"], K3, K3BG, ' data-build-in="rise order 2"', 26, "셀 [1]과 같은 결과"))
o.append(note_card(96, 480, 840, 380, "if 안에도 if를 넣을 수 있어요", "바깥 if가 True일 때만 안쪽 if를 물어요. 안쪽 if 안의 줄은 8칸 들여써요. 두 조건이 모두 맞아야 실행하니 and와 같아요.", K3, ' data-build-in="rise order 1"'))
o.append(note_card(984, 500, 840, 360, "언제 안쪽 if를 쓰나요", "바깥 조건이 맞은 뒤에 따로 할 일이 있을 때예요. 예를 들어 메뉴판에 있으면 먼저 가격을 찍고, 그다음 5000원 이하인지 다시 물어요. 할 일이 한 군데뿐이면 and가 더 읽기 쉬워요.", None, ' data-build-in="rise order 3"'))
o.append(caption("들여쓰기가 깊어지면 and로 합칠 수 있는지 먼저 봐요.", 920))
W("i-nested", o, "if 안에 다시 if를 넣을 수 있어요. 바깥 if가 True일 때만 안쪽 if를 물어요. 안쪽 if의 줄은 4칸을 한 번 더 들여써서 8칸이에요. 키가 120 이상이고, 그다음 나이가 7 이상이어야 실행하니 and로 이은 조건과 같아요. 오른쪽처럼 한 줄로 적으면 들여쓰기가 얕아져서 읽기 쉬워요. 바깥 조건이 맞은 뒤에 따로 할 일이 있을 때는 안쪽 if가 필요해요." + REAL)

o = [sec("i-or")] + head(EB3, "or는 하나만 True여도 True예요", K3)
o += cell({"id": "c-or", "lines": ["is_member = False", "total = 60000", "if is_member or total >= 50000:", '    print("할인해 드려요")'], "n": 4, "out": ["할인해 드려요"]}, 96, 200, 900, sel="c-or")
o += chain([("is_member", "False", "회원"), ("60000 >= 50000", "True", "금액"), ("False or True", "True", "or")], 96, 470, 900, 1, K3)
o.append(f'<div data-build-in="rise order 4" style="position:absolute;left:1050px;top:200px;width:774px;height:430px;background:{CARD};border:2px solid {LINE};border-radius:20px;padding:24px 30px;display:flex;flex-direction:column;gap:12px">'
         + p(f"font-size:28px;font-weight:700;color:{INK}", "and와 or 한눈에")
         + '<div style="display:flex;flex-direction:row;gap:12px">' + "".join(p(f"width:{w_}px;flex:none;font-size:22px;font-weight:700;color:{GRAY}", t) for t, w_ in [("앞", 150), ("뒤", 150), ("and", 180), ("or", 180)]) + '</div>'
         + "".join('<div style="display:flex;flex-direction:row;gap:12px;align-items:center">' + f'<div style="width:150px;flex:none">{tf(a, 22)}</div><div style="width:150px;flex:none">{tf(b, 22)}</div><div style="width:180px;flex:none">{tf(x, 22)}</div><div style="width:180px;flex:none">{tf(y, 22)}</div></div>'
                   for a, b, x, y in [("True", "True", "True", "True"), ("True", "False", "False", "True"), ("False", "True", "False", "True"), ("False", "False", "False", "False")]) + '</div>')
o.append(note_card(1050, 660, 774, 200, "and는 모두, or는 하나라도", "and는 하나라도 False면 False, or는 하나라도 True면 True예요.", K3, ' data-build-in="rise order 5"', "gap:8px"))
o.append(caption("회원이 아니어도 5만 원 이상이면 할인해요. 12의 할인 조건이에요.", 920))
W("i-or", o, "12의 할인 조건을 if에 넣었어요. 회원이거나 5만 원 이상 사면 할인해요. 둘 중 하나만 맞아도 되니까 or로 이어요. 회원은 아니라 False지만 금액이 True라서 전체가 True예요. 오른쪽 표는 and와 or를 나란히 놓았어요. and는 둘 다 True여야 True고, or는 둘 다 False여야 False예요. 조건을 말로 먼저 적어 보고, '그리고'로 이어지면 and, '또는'으로 이어지면 or를 써요." + REAL)

o = [sec("i-not")] + head(EB3, "not과 not in으로 반대를 물어요", K3)
o += cell({"id": "c-not", "lines": [MENU, 'order = "tea"', "if not order in menu:", '    print("메뉴판에 없어요")', "if order not in menu:", '    print("메뉴판에 없어요")'], "n": 5, "out": ["메뉴판에 없어요", "메뉴판에 없어요"]}, 96, 200, 1000, sel="c-not")
o.append(hl(96, 200, 1000, 2, 1, "mark", 1, "not (in)"))
o.append(hl(96, 200, 1000, 4, 1, "run", 2, "not in · 이쪽을 써요"))
o += chain([('"tea" in menu', "False", "in"), ("not False", "True", "not")], 1150, 200, 674, 1, K3, 84)
o.append(note_card(1150, 400, 674, 230, "not in이 읽기 쉬워요", "결과는 같아요. 영어 문장처럼 order not in menu로 읽혀서 실제로는 not in을 많이 써요.", K3, ' data-build-in="rise order 2"'))
o.append(note_card(96, 580, 1000, 280, "없을 때 할 일만 있으면", "\"없으면 알려 주기\"처럼 False일 때만 할 일이 있으면 else 대신 조건을 뒤집어요. 1파트 처음의 KeyError를 막는 첫 방법이에요.", None, ' data-build-in="rise order 3"'))
o.append(note_card(1150, 660, 674, 200, "not은 12에서 배웠어요", "True와 False를 뒤집어요. not True는 False예요.", None, ' data-build-in="rise order 3"', "gap:8px"))
o.append(caption("\"없으면\"은 not in, \"아니면\"은 !=로 적어요.", 920))
W("i-not", o, "12에서 not은 True와 False를 뒤집었어요. tea in menu는 False라서 not을 붙이면 True가 되고, 메뉴판에 없어요를 찍어요. 14의 not in으로 적어도 결과는 같아요. 영어 문장처럼 읽혀서 실제로는 not in을 많이 써요. 메뉴판에 없을 때만 할 일이 있으면 else를 쓰지 않고 조건을 뒤집어요. 1파트 처음의 KeyError는 이렇게 먼저 물어서 막을 수 있어요." + REAL)

o = [sec("i-range")] + head(EB3, "범위는 9 <= hour < 18처럼 이어 적어요", K3)
o += cell({"id": "c-r1", "lines": ["hour = 14", "if 9 <= hour < 18:", '    print("영업 중이에요")', "if hour >= 9 and hour < 18:", '    print("영업 중이에요")'], "n": 6, "out": ["영업 중이에요", "영업 중이에요"]}, 96, 200, 860, sel="c-r1")
o += cell({"id": "c-r2", "lines": ["hour = 20", "if 9 <= hour < 18:", '    print("영업 중이에요")', "else:", '    print("문 닫았어요")'], "n": 7, "out": ["문 닫았어요"]}, 96, 580, 860, attrs=' data-build-in="rise order 3"')
hours = [str(h) for h in range(7, 21)]
o.append(label("영업시간 · 9시부터 18시 전까지", 1010, 200, K3, ' data-build-in="fade order 1"', 814, 24))
o.append(slots(hours, 1010, 244, 50, 70, hi=tuple(range(2, 11)), top_lbl=False, attrs=' data-build-in="rise order 1"', fs=22, color=K3, bg=K3BG))
o.append(label("9는 들어가요 (<=)", 1010, 340, GR, ' data-build-in="fade order 1"', 400, 22))
o.append(label("18은 빠져요 (<)", 1450, 340, RED, ' data-build-in="fade order 1"', 374, 22))
o.append(f'<div data-build-in="rise order 2" style="position:absolute;left:1010px;top:410px;width:814px;height:250px;background:{CARD};border:2px solid {LINE};border-radius:20px;padding:24px 30px;display:flex;flex-direction:column;gap:14px">'
         + p(f"font-size:26px;font-weight:700;color:{INK}", "같은 뜻이에요")
         + '<div style="display:flex;flex-direction:row;align-items:center;gap:16px">' + mono("9 <= hour < 18", 28, K3, K3BG) + p(f"font-size:22px;color:{SUB}", "줄인 방법") + '</div>'
         + '<div style="display:flex;flex-direction:row;align-items:center;gap:16px">' + mono("hour >= 9 and hour < 18", 24, GRAY, "#EEEFF2") + p(f"font-size:22px;color:{SUB}", "원래 방법") + '</div></div>')
o.append(note_card(1010, 690, 814, 170, "수학 시간의 부등식처럼", "가운데에 변수를 두고 양쪽에 경계를 적어요.", None, ' data-build-in="rise order 3"', "gap:8px"))
o.append(caption("\"사이에 있나요?\"는 작은 값 <= 변수 < 큰 값으로 물어요.", 940))
W("i-range", o, "가게가 9시부터 18시 전까지 열어요. hour가 이 사이에 있는지 물을 때 파이썬은 수학 부등식처럼 9 <= hour < 18로 이어 적을 수 있어요. 이건 hour >= 9 and hour < 18을 줄인 거예요. 결과는 같아요. 9는 작거나 같다(<=)라서 들어가고, 18은 작다(<)라서 빠져요. 경계 숫자가 들어가는지 빠지는지는 등호가 있는지로 정해요. 20시는 범위 밖이라 else로 가요." + REAL)

o = [sec("i-truthy")] + head(EB3, "비어 있는 값은 False로 봐요", K3)
o += cell({"id": "c-t", "lines": ["print(bool(0), bool(4500))", 'print(bool(""), bool("tea"))', 'print(bool([]), bool(["tea"]))', "print(bool({}), bool(set()))", "print(bool(None))"], "n": 8,
           "out": ["False True", "False True", "False True", "False False", "False"]}, 96, 200, 860, sel="c-t")
vals = [("0", "4500", "숫자"), ('""', '"tea"', "문자열"), ("[]", '["tea"]', "리스트"), ("{}  set()", "{\"a\": 1}  {\"tea\"}", "딕셔너리, 집합"), ("None", "", "15의 None")]
o.append(f'<div data-build-in="fade order 1" style="position:absolute;left:1010px;top:200px;width:814px;height:50px;display:flex;flex-direction:row;align-items:center;gap:16px;padding:0 22px">'
         + p(f"width:220px;flex:none;font-size:22px;font-weight:700;color:{GRAY}", "종류") + p(f"width:240px;flex:none;font-size:22px;font-weight:700;color:{RED}", "False로 봐요") + p(f"font-size:22px;font-weight:700;color:{GR}", "True로 봐요") + '</div>')
for i, (f_, t_, k) in enumerate(vals):
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:1010px;top:{256 + i * 96}px;width:814px;height:84px;background:{CARD};border:2px solid {LINE};border-radius:16px;padding:0 22px;display:flex;flex-direction:row;align-items:center;gap:16px">'
             + p(f"width:220px;flex:none;font-size:24px;font-weight:700;color:{INK}", e(k)) + f'<div style="width:240px;flex:none">' + mono(f_, 24, RED, "#F8E6E6", "display:inline-block") + '</div>'
             + (mono(t_, 24, GR, "#E6F4EC") if t_ else "") + '</div>')
o.append(note_card(96, 664, 860, 200, "bool()로 확인해요", "bool(값)은 그 값을 if에 넣었을 때 True로 볼지 False로 볼지 알려 줘요. 0과 빈 것, None만 False예요.", K3, ' data-build-in="rise order 5"'))
o.append(caption("0, 빈 문자열, 빈 리스트, 빈 딕셔너리, 빈 집합, None은 모두 False예요.", 920))
W("i-truthy", o, "if 뒤에 비교식이 아니라 값을 그냥 적을 수도 있어요. 그때 파이썬은 그 값을 True나 False로 보고 판단해요. bool()에 넣어 보면 어떻게 보는지 알 수 있어요. 숫자는 0만 False, 문자열은 빈 문자열만 False예요. 리스트, 딕셔너리, 집합은 비어 있으면 False예요. 15의 get에서 본 None도 False예요. 나머지는 모두 True예요. 12의 int(), str()처럼 bool()도 값을 bool로 바꿔 주는 함수예요." + REAL)

o = [sec("i-empty")] + head(EB3, "if orders:는 비어 있지 않은지 묻는 거예요", K3)
o += cell({"id": "c-em", "lines": ["orders = []", "if orders:", '    print(len(orders), "잔 주문")', "else:", '    print("아직 주문이 없어요")', "if len(orders) > 0:", '    print(len(orders), "잔 주문")', "else:", '    print("아직 주문이 없어요")'], "n": 9, "out": ["아직 주문이 없어요", "아직 주문이 없어요"]}, 96, 200, 900, sel="c-em")
o.append(hl(96, 200, 900, 1, 1, "run", 1, "줄인 방법"))
o.append(hl(96, 200, 900, 5, 1, "mark", 2, "원래 방법"))
o.append(card(1050, 200, 774, 290, p(f"font-size:26px;font-weight:700;color:{INK}", "같은 뜻이에요")
              + '<div style="display:flex;flex-direction:row;align-items:center;gap:16px">' + mono("if orders:", 28, K3, K3BG) + p(f"font-size:22px;color:{SUB}", "줄인 방법") + '</div>'
              + '<div style="display:flex;flex-direction:row;align-items:center;gap:16px">' + mono("if len(orders) > 0:", 26, GRAY, "#EEEFF2") + p(f"font-size:22px;color:{SUB}", "원래 방법") + '</div>', None, ' data-build-in="rise order 2"'))
o.append(note_card(1050, 520, 774, 340, "처음엔 원래 방법도 괜찮아요", "if orders:는 \"주문이 하나라도 있으면\"이라고 읽어요. 헷갈리면 len(orders) > 0으로 적어도 결과가 같아요. 남이 쓴 코드에서 if orders:를 만나면 이 뜻으로 읽어요.", None, ' data-build-in="rise order 3"'))
o.append(caption("빈 리스트는 False라서 if 리스트:는 \"하나라도 있으면\"이에요.", 920))
W("i-empty", o, "앞 장의 규칙을 실제로 쓰는 모양이에요. orders가 빈 리스트면 False로 봐서 else로 가요. 하나라도 들어 있으면 True로 봐서 if 안을 실행해요. 아래 if는 같은 일을 len으로 길게 쓴 거예요. 결과가 같아요. 처음에는 len(orders) > 0이 뜻이 더 잘 보여요. 실제 코드에서는 if orders:를 자주 만나니 읽을 수 있으면 돼요. 6파트 영수증 실습에서 이 모양을 써요." + REAL)

# ---------- part 4 ----------
o = [sec("f-pick")] + head(EB4, "for 안의 if로 골라 담아요", K4)
o += cell({"id": "c-p", "lines": [MENU, "prices = [4500, 5000, 6500, 4000]", "cheap = []", "for p in prices:", "    if p <= 5000:", "        cheap.append(p)", "print(cheap)"], "n": 1, "out": ["[4500, 5000, 4000]"]}, 96, 200, 1000, sel="c-p")
o.append(hl(96, 200, 1000, 4, 1, "mark", 1, "4칸"))
o.append(hl(96, 200, 1000, 5, 1, "run", 1, "8칸"))
o.append(label("prices", 1150, 200, GRAY, ' data-build-in="fade order 2"', 674, 24))
o.append(slots(["4500", "5000", "6500", "4000"], 1150, 240, 150, 84, hi=(0, 1, 3), attrs=' data-build-in="rise order 2"', fs=30, color=K4, bg=K4BG))
for i, (v, ok) in enumerate([("4500", True), ("5000", True), ("6500", False), ("4000", True)]):
    o.append(yes_no(1150 + i * 158, 380, ok, "담아요" if ok else "건너뛰어요", 3, 150))
o.append(label("cheap", 1150, 470, K4, ' data-build-in="fade order 4"', 674, 24))
o.append(slots(["4500", "5000", "4000"], 1150, 510, 150, 84, attrs=' data-build-in="rise order 4"', fs=30, color=K4, bg=K4BG))
o.append(note_card(96, 560, 1000, 300, "한 바퀴 돌 때마다 if를 한 번 물어요", "p가 바뀔 때마다 5000 이하인지 물어요. True인 값만 append해요. 들여쓰기가 for 4칸, if 8칸으로 두 번 들어가요.", K4, ' data-build-in="rise order 3"'))
o.append(caption("빈 리스트 + for + if + append가 \"골라 담기\"의 기본 모양이에요.", 920))
W("f-pick", o, "13의 for와 이번 if를 같이 써요. 메뉴 가격 중 5000원 이하만 골라 새 리스트에 담아요. 빈 리스트 cheap을 만들고, for로 가격을 하나씩 꺼내요. 꺼낼 때마다 if로 5000 이하인지 묻고, True면 append해요. 6500은 False라 건너뛰어요. if는 for 안에 있어서 4칸, append는 if 안에 있어서 8칸 들여써요. 이 모양은 18에서도 계속 써요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요. 첫 줄의 menu는 이 파트의 뒤 셀에서 써요." + REAL, ("p4", "for와 함께, 줄여 쓰기"))

o = [sec("f-count")] + head(EB4, "조건에 맞는 것만 세요", K4)
o += cell({"id": "c-c", "lines": ['orders = ["coffee", "latte", "coffee", "cake", "tea", "coffee"]', "n = 0", "for o in orders:", '    if o == "coffee":', "        n += 1", "print(n)", 'print(orders.count("coffee"))'], "n": 2, "out": ["3", "3"]}, 96, 200, 1100, sel="c-c")
o.append(hl(96, 200, 1100, 4, 1, "run", 1, "True일 때만 1 더하기"))
steps = [("coffee", "1"), ("latte", "1"), ("coffee", "2"), ("cake", "2"), ("tea", "2"), ("coffee", "3")]
o.append(f'<div data-build-in="fade order 2" style="position:absolute;left:1250px;top:200px;width:574px;height:44px;display:flex;flex-direction:row;gap:16px;padding:0 22px">'
         + p(f"width:180px;flex:none;font-family:{MONO};font-size:22px;font-weight:700;color:{GRAY}", "o") + p(f"width:150px;flex:none;font-family:{MONO};font-size:22px;font-weight:700;color:{GRAY}", '== "coffee"') + p(f"font-family:{MONO};font-size:22px;font-weight:700;color:{GRAY}", "n") + '</div>')
for i, (o_, n_) in enumerate(steps):
    ok = o_ == "coffee"
    o.append(f'<div data-build-in="rise order {i + 2}" style="position:absolute;left:1250px;top:{250 + i * 70}px;width:574px;height:60px;background:{K4BG if ok else CARD};border:2px solid {K4 if ok else LINE};border-radius:14px;padding:0 22px;display:flex;flex-direction:row;align-items:center;gap:16px">'
             + p(f"width:180px;flex:none;font-family:{MONO};font-size:24px;font-weight:700;color:{INK}", e(o_)) + f'<div style="width:150px;flex:none">{tf("True" if ok else "False", 20)}</div>' + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{INK}", n_) + '</div>')
o.append(note_card(96, 600, 1100, 260, "값 하나를 셀 땐 count가 짧아요", "같은 값의 개수는 13의 count로 바로 세요. 5000원 이상처럼 조건이 붙으면 count로는 못 세서 for와 if를 써요.", None, ' data-build-in="rise order 8"'))
o.append(caption("세기는 n = 0에서 시작해 조건이 True일 때 n += 1이에요.", 920))
W("f-count", o, "주문 중 coffee가 몇 잔인지 세요. n을 0으로 두고 for로 하나씩 꺼내요. coffee일 때만 n에 1을 더해요. 오른쪽 표처럼 coffee를 만날 때마다 n이 1, 2, 3으로 늘어요. 같은 값 하나를 셀 때는 13의 count로 한 줄이면 돼요. 결과가 3으로 같아요. 그래도 for와 if를 알아야 하는 이유는 가격이 5000원 이상인 주문처럼 조건이 붙은 개수는 count로 못 세기 때문이에요." + REAL)

o = [sec("f-dict")] + head(EB4, "딕셔너리에서 조건에 맞는 메뉴를 찾아요", K4)
o += cell({"id": "c-d", "lines": ["for name, price in menu.items():", "    if price <= 5000:", "        print(name, price)"], "n": 3, "out": ["coffee 4500", "latte 5000"]}, 96, 200, 900, sel="c-d")
o.append(lockers([("coffee", "4500"), ("latte", "5000"), ("cake", "6500")], 1050, 200, 240, 170, K4, K4BG, hi=(0, 1), attrs=' data-build-in="rise order 1"', fs=38))
for i, ok in enumerate([True, True, False]):
    o.append(yes_no(1050 + i * 252, 400, ok, "<= 5000 True" if ok else "<= 5000 False", 2, 240))
o.append(note_card(96, 470, 900, 390, "15의 items()에 if를 붙였어요", "items()는 키와 값을 한 쌍씩 꺼내요. 값인 price로 조건을 묻고, 맞는 쌍만 찍어요. 키로 묻고 싶으면 if name == \"cake\":처럼 name을 써요.", K4, ' data-build-in="rise order 3"'))
o.append(note_card(1050, 490, 774, 370, "메뉴판에 쓰면", "5000원 이하 메뉴 추천, 품절인 메뉴 찾기, 이름에 te가 들어간 메뉴 찾기(\"te\" in name)처럼 쓸 수 있어요.", None, ' data-build-in="rise order 4"'))
o.append(caption("for k, v in d.items(): 안에서 if로 키나 값을 물어요.", 920))
W("f-dict", o, "15에서 배운 items()로 메뉴판의 키와 값을 한 쌍씩 꺼내요. 꺼낼 때마다 가격이 5000 이하인지 물어요. coffee와 latte는 True라서 찍고, cake는 6500이라 건너뛰어요. 조건에는 키도 값도 쓸 수 있어요. 이름에 te가 들어간 메뉴를 찾으려면 14의 in을 문자열에 써서 te in name으로 물어요. 앞 셀의 menu를 그대로 썼어요." + REAL)

o = [sec("f-oneline")] + head(EB4, "if와 else를 한 줄로 줄여 쓸 수 있어요", K4)
o += cell({"id": "c-1l", "lines": ["total = 12000", "if total >= 10000:", '    msg = "5% 할인"', "else:", '    msg = "할인 없음"', "print(msg)", 'msg = "5% 할인" if total >= 10000 else "할인 없음"', "print(msg)"], "n": 4, "out": ["5% 할인", "5% 할인"]}, 96, 200, 1100, sel="c-1l")
o.append(hl(96, 200, 1100, 1, 4, "mark", 1, "원래 방법 · 4줄"))
o.append(hl(96, 200, 1100, 6, 1, "run", 2, "줄인 방법"))
pc = [("True일 때 값", '"5% 할인"', GR), ("조건", "if total >= 10000", K4), ("False일 때 값", 'else "할인 없음"', RED)]
for i, (t_, k, col) in enumerate(pc):
    o.append(f'<div data-build-in="rise order {i + 3}" style="position:absolute;left:1250px;top:{200 + i * 150}px;width:574px;height:130px;background:{CARD};border:2px solid {LINE};border-left:10px solid {col};border-radius:18px;padding:16px 24px;display:flex;flex-direction:column;justify-content:center;gap:10px">'
             + p(f"font-size:22px;font-weight:700;color:{col}", e(t_)) + mono(k, 26, INK, "#F1F0EC", "align-self:flex-start") + '</div>')
o.append(note_card(96, 640, 1100, 220, "값 하나를 고를 때만 줄여요", "변수에 넣을 값이 둘 중 하나일 때 써요. 실행할 줄이 여러 개이거나 elif가 필요하면 원래 모양으로 적어요.", None, ' data-build-in="rise order 6"'))
o.append(note_card(1250, 660, 574, 200, "읽는 순서", "\"1만 원 이상이면 5% 할인, 아니면 할인 없음\"", None, ' data-build-in="rise order 6"', "gap:8px"))
o.append(caption("값1 if 조건 else 값2는 \"조건이 True면 값1, 아니면 값2\"예요.", 940))
W("f-oneline", o, "if와 else로 변수에 둘 중 하나를 넣는 모양은 아주 자주 나와요. 그래서 한 줄로 줄이는 방법이 있어요. True일 때 값을 먼저 쓰고, if 조건, else False일 때 값 순서로 적어요. 결과는 4줄짜리와 같아요. 줄인 방법은 값 하나를 고를 때만 써요. 실행할 줄이 여러 개이거나 갈림길이 셋 이상이면 원래 모양이 읽기 쉬워요. 처음엔 4줄로 적고, 남의 코드에서 한 줄 모양을 만나면 읽을 수 있으면 돼요." + REAL)

o = [sec("f-get")] + head(EB4, "15의 get을 이제 풀어서 읽을 수 있어요", K4)
o += cell({"id": "c-g", "lines": ['if "cakee" in menu:', '    price = menu["cakee"]', "else:", "    price = 5000", "print(price)", 'print(menu["cakee"] if "cakee" in menu else 5000)', 'print(menu.get("cakee", 5000))'], "n": 5, "out": ["5000", "5000", "5000"]}, 96, 200, 1000, sel="c-g")
o.append(hl(96, 200, 1000, 0, 5, "mark", 1, "1 · if, else"))
o.append(hl(96, 200, 1000, 5, 1, "mark", 2))
o.append(hl(96, 200, 1000, 6, 1, "run", 3, "3 · get"))
lv = [("1", "if, else 4줄", "이번 챕터에서 배운 원래 모양", GRAY), ("2", "한 줄 if else", "15의 참고 칸에서 읽기만 한 코드", GRAY), ("3", 'menu.get("cakee", 5000)', "15에서 배운 줄인 메서드", K4)]
for i, (n_, k, d, col) in enumerate(lv):
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:1150px;top:{200 + i * 150}px;width:674px;height:130px;background:{K4BG if col == K4 else CARD};border:2px solid {col if col == K4 else LINE};border-radius:18px;padding:0 24px;display:flex;flex-direction:row;align-items:center;gap:18px">'
             + num(int(n_), col, 30) + '<div style="display:flex;flex-direction:column;gap:6px">' + p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{INK}", e(k)) + p(f"font-size:22px;color:{SUB}", e(d)) + '</div></div>')
o.append(note_card(96, 640, 1000, 220, "get은 if를 대신 써 준 거예요", "키가 있으면 그 값, 없으면 기본값. 세 줄 모두 같은 일을 해요. 짧을수록 실수할 곳이 줄어서 실제로는 get을 써요.", K4, ' data-build-in="rise order 4"'))
o.append(note_card(1150, 680, 674, 180, "15에서는 왜 읽기만 했나요", "if를 아직 몰라서예요. 이제 1번을 직접 칠 수 있어요.", None, ' data-build-in="rise order 4"', "gap:8px"))
o.append(caption("줄인 메서드 안에는 이런 if가 들어 있어요. 원래 모양을 알면 결과를 읽기 쉬워요.", 920))
W("f-get", o, "15에서 get을 배울 때, 같은 뜻의 한 줄 if else 코드를 참고 칸에 두고 읽기만 했어요. 이제 그 코드를 풀어서 if와 else 4줄로 쓸 수 있어요. cakee가 메뉴판에 있으면 그 가격, 없으면 5000이에요. 세 방법 모두 5000을 찍어요. get은 이 if를 대신 해 주는 메서드예요. 실제로는 가장 짧은 get을 쓰고, 4줄짜리는 get이 무슨 일을 하는지 이해하는 데 써요." + REAL)

o = [sec("f-set")] + head(EB4, "16에서 읽기만 한 코드를 직접 쳐 봐요", K4)
o += cell({"id": "c-s1", "lines": ['menus = {"coffee", "cake"}', 'if "juice" in menus:', '    menus.remove("juice")', "print(sorted(menus))", 'menus.discard("juice")', "print(sorted(menus))"], "n": 6, "out": ["['cake', 'coffee']", "['cake', 'coffee']"]}, 96, 200, 840, sel="c-s1")
o += cell({"id": "c-s2", "lines": ["kinds = []", "for o in orders:", "    if o not in kinds:", "        kinds.append(o)", "print(kinds)", "print(sorted(set(orders)))"], "n": 7, "out": ["['coffee', 'latte', 'cake', 'tea']", "['cake', 'coffee', 'latte', 'tea']"]}, 984, 200, 840, attrs=' data-build-in="rise order 2"')
o.append(hl(96, 200, 840, 1, 2, "mark", 1, "원래 방법"))
o.append(hl(96, 200, 840, 4, 1, "run", 1, "줄인 방법"))
o.append(hl(984, 200, 840, 0, 4, "mark", 2, "원래 방법"))
o.append(hl(984, 200, 840, 5, 1, "run", 2, "줄인 방법"))
o.append(note_card(96, 560, 840, 300, "discard = 있으면 remove", "있는지 먼저 묻고 있을 때만 remove해요. juice는 없어서 아무 일도 없어요. discard 한 줄과 결과가 같아요.", K4, ' data-build-in="rise order 3"'))
o.append(note_card(984, 600, 840, 260, "set() = 없을 때만 append", "리스트는 처음 나온 순서를 지키고, 집합은 sorted()로 줄 세워 찍었어요. 담긴 값은 같아요.", K4, ' data-build-in="rise order 3"'))
o.append(caption("16의 \"참고, 읽기만\" 칸은 이제 모두 직접 칠 수 있어요.", 920))
W("f-set", o, "16에서 집합의 줄인 기능을 배우며 if가 들어간 원래 코드를 읽기만 했어요. 왼쪽은 discard예요. juice가 들어 있는지 먼저 묻고 있을 때만 remove해요. discard 한 줄과 결과가 같아요. 오른쪽은 set(orders)로 중복을 없앤 일을 리스트로 직접 한 거예요. 아직 kinds에 없을 때만 append해요. 리스트는 처음 나온 순서를 지키고, 집합은 sorted로 줄 세워서 순서가 달라요. orders는 셀 [2]의 주문 리스트예요. 16의 교집합, 차집합 긴 코드도 같은 방법으로 직접 쳐 볼 수 있어요." + REAL)

# ---------- part 5 ----------
o = [sec("e-eq")] + head(EB5, "if 뒤에는 = 하나가 아니라 == 두 개예요", K5)
o += cell({"id": "c-x1", "lines": ['order = "coffee"', 'if order = "coffee":', '    print("커피예요")'], "n": 1, "out": ["Cell In[1], line 2", "SyntaxError: invalid syntax. Maybe you meant '==' or ':=' instead of '='?"], "err": True}, 96, 200, 1728, sel="c-x1")
o.append(hl(96, 200, 1728, 1, 1, "err", 1, "line 2"))
o.append(f'<div data-build-in="rise order 2" style="position:absolute;left:96px;top:470px;width:840px;height:390px;background:{CARD};border:2px solid {LINE};border-top:10px solid {RED};border-radius:20px;padding:24px 30px;display:flex;flex-direction:column;gap:16px">'
         + p(f"font-size:28px;font-weight:700;color:{INK}", "오류 메시지 읽기")
         + p(f"font-size:24px;line-height:1.5;color:{INK}", "line 2는 둘째 줄이 문제라는 뜻이에요.")
         + p(f"font-size:24px;line-height:1.5;color:{INK}", "Maybe you meant '==' 는 \"== 를 쓰려던 거 아니에요?\"라고 고칠 곳을 알려 주는 말이에요.")
         + p(f"font-size:22px;line-height:1.5;color:{SUB}", ":= 는 배우지 않은 기호라 신경 쓰지 않아요.") + '</div>')
o.append(f'<div data-build-in="rise order 3" style="position:absolute;left:984px;top:470px;width:840px;height:390px;background:{CARD};border:2px solid {LINE};border-top:10px solid {GR};border-radius:20px;padding:24px 30px;display:flex;flex-direction:column;gap:16px">'
         + p(f"font-size:28px;font-weight:700;color:{INK}", "12에서 본 규칙 그대로")
         + '<div style="display:flex;flex-direction:row;align-items:center;gap:18px">' + mono('order = "coffee"', 26, BL, "#E5EEF8") + p(f"font-size:24px;color:{INK}", "넣기") + '</div>'
         + '<div style="display:flex;flex-direction:row;align-items:center;gap:18px">' + mono('if order == "coffee":', 26, GR, "#E6F4EC") + p(f"font-size:24px;color:{INK}", "묻기") + '</div>'
         + p(f"font-size:22px;line-height:1.5;color:{SUB}", "SyntaxError는 실행하기 전에 문법을 검사하다 나서, 셀의 어느 줄도 실행되지 않아요.") + '</div>')
o.append(caption("SyntaxError가 나면 line 숫자의 줄부터 봐요.", 920))
W("e-eq", o, "12에서 = 하나는 넣기, == 두 개는 묻기라고 배웠어요. if 뒤에 = 하나를 쓰면 SyntaxError가 나요. 오류 위쪽의 line 2는 둘째 줄이 문제라는 뜻이에요. 마지막 줄은 ==를 쓰려던 거 아니냐고 고칠 곳까지 알려 줘요. :=는 배우지 않은 기호라 신경 쓰지 않아요. SyntaxError는 실행 전에 문법을 검사하다 나서 첫 줄의 order도 만들어지지 않아요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p5", "자주 나는 오류"))

o = [sec("e-colon")] + head(EB5, "콜론과 들여쓰기를 빠뜨리면 실행 전에 멈춰요", K5)
errs = [("c-x2", ['if order == "coffee"', '    print("커피예요")'], 2, ["SyntaxError: expected ':'"], "콜론이 없어요", "if 줄 끝에 : 붙이기"),
        ("c-x3", ['if order == "coffee":', 'print("커피예요")'], 3, ["IndentationError: expected an indented block after 'if' statement on line 1"], "if 안에 들여쓴 줄이 없어요", "print 앞에 4칸"),
        ("c-x4", ['if order == "coffee":', '    print("커피예요")', '      print("나왔어요")'], 4, ["IndentationError: unexpected indent"], "들여쓰기 칸 수가 달라요", "같은 칸(4칸)에 맞추기")]
y = 196
for i, (cid, lines, n_, out, why, fix) in enumerate(errs):
    hh = cell_h({"lines": lines, "out": out})
    o += cell({"id": cid, "lines": lines, "n": n_, "out": out, "err": True}, 96, y, 1330, attrs=f' data-build-in="rise order {i + 1}"')
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:1460px;top:{y}px;width:364px;height:{hh}px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:12px 24px;display:flex;flex-direction:column;justify-content:center;gap:10px">'
             + p(f"font-size:24px;font-weight:700;color:{INK}", e(why)) + mono(fix, 22, GR, "#E6F4EC", "align-self:flex-start") + '</div>')
    y += hh + 26
o.append(caption("IndentationError는 들여쓰기 오류예요. 칸 수를 4칸에 맞춰요.", 940))
W("e-colon", o, "if 모양에서 자주 빠뜨리는 세 가지예요. 1번은 if 줄 끝의 콜론이 없어요. expected 콜론이라고 정확히 알려 줘요. 2번은 if 다음 줄을 들여쓰지 않았어요. if 안에 들여쓴 줄이 하나는 있어야 해요. 3번은 같은 if 안에서 칸 수가 4칸, 6칸으로 달라요. unexpected indent는 생각지 못한 들여쓰기라는 뜻이에요. 셋 다 실행 전에 나서 셀의 어느 줄도 실행되지 않아요. 오류 위쪽의 Cell In 줄은 빼고 마지막 줄만 옮겼어요." + REAL)

o = [sec("e-or")] + head(EB5, "or 뒤에도 비교를 다시 적어요", K5)
o += cell({"id": "c-x5", "lines": ['order = "cake"', 'if order == "coffee" or "latte":', '    print("커피 종류예요")', 'print(order == "coffee" or "latte")'], "n": 5, "out": ["커피 종류예요", "latte"]}, 96, 200, 900, sel="c-x5")
o.append(hl(96, 200, 900, 1, 1, "err", 1, "늘 True"))
o += cell({"id": "c-x6", "lines": ['if order == "coffee" or order == "latte":', '    print("커피 종류예요")', "else:", '    print("커피 종류가 아니에요")', 'print(order in ["coffee", "latte"])'], "n": 6, "out": ["커피 종류가 아니에요", "False"]}, 96, 520, 900, attrs=' data-build-in="rise order 3"')
o += chain([('order == "coffee"', "False", "앞"), ('False or "latte"', None, "or"), ('"latte"', None, "결과")], 1050, 200, 774, 1, K5, 84)
o.append(note_card(1050, 470, 774, 210, "\"latte\"는 빈 문자열이 아니라 True로 봐요", "3파트에서 본 규칙이에요. or 뒤가 비교가 아니라 글자 하나라서 늘 True로 봐요.", RED, ' data-build-in="rise order 2"'))
o.append(note_card(1050, 700, 774, 160, "고치는 두 가지", "비교를 둘 다 적거나, in과 리스트로 물어요.", GR, ' data-build-in="rise order 3"', "gap:8px"))
o.append(caption("말로는 \"coffee 또는 latte\"지만 코드는 order == 를 두 번 적어요.", 940))
W("e-or", o, "말로는 주문이 coffee 또는 latte면이라고 하니 그대로 적기 쉬워요. 그런데 cake인데도 커피 종류예요가 찍혀요. 오류가 나지 않아서 찾기 어려워요. 파이썬은 order == coffee와 latte를 or로 이은 걸로 읽어요. 앞은 False지만 뒤의 latte는 빈 문자열이 아니라 True로 봐요. 그래서 조건이 늘 True예요. print로 찍어 보면 latte가 그대로 나와요. 비교를 둘 다 적거나, 14의 in으로 리스트 안에 있는지 물으면 돼요." + REAL)

o = [sec("e-type")] + head(EB5, "글자와 숫자는 크기를 비교할 수 없어요", K5)
o += cell({"id": "c-x7", "lines": ['price = "4500"', "if price >= 4000:", '    print("4000원 넘어요")'], "n": 7, "out": ["TypeError: '>=' not supported between instances of 'str' and 'int'"], "err": True}, 96, 200, 1300, sel="c-x7")
o += cell({"id": "c-x8", "lines": ["if int(price) >= 4000:", '    print("4000원 넘어요")'], "n": 8, "out": ["4000원 넘어요"]}, 96, 420, 1300, attrs=' data-build-in="rise order 2"')
o.append(var_box("v-p", "price", '"4500"', 1450, 200, OR, 374, ' data-build-in="rise order 1"'))
o.append(note_card(96, 620, 840, 240, "따옴표가 있으면 글자예요", "\"4500\"은 str, 4000은 int라서 크고 작음을 비교할 수 없어요. str과 int 사이에서는 >=를 지원하지 않는다는 뜻이에요.", RED, ' data-build-in="rise order 1"'))
o.append(note_card(984, 620, 840, 240, "12의 int()로 바꿔요", "int(price)는 숫자 4500이 돼요. ==는 오류 없이 False가 나와서 더 찾기 어려워요.", GR, ' data-build-in="rise order 2"'))
o.append(caption("비교 오류가 나면 type()으로 두 값의 종류부터 봐요.", 920))
W("e-type", o, "따옴표로 감싼 4500은 숫자가 아니라 글자예요. 글자와 숫자는 크고 작음을 비교할 수 없어서 TypeError가 나요. 오류 끝의 str and int는 비교한 두 값의 종류예요. 12에서 배운 int()로 숫자로 바꾸면 돼요. 조심할 건 == 예요. 글자 4500과 숫자 4500을 ==로 비교하면 오류 없이 False가 나와서 if가 조용히 건너뛰어요. 이상하면 type()으로 두 값의 종류부터 봐요." + REAL)

# ---------- part 6 ----------
o = [sec("x-sale")] + head(EB6, "장바구니 금액에 따라 할인해요", K6)
o += cell({"id": "c-p1", "lines": [MENU, 'cart = {"coffee": 2, "cake": 1}', "total = 0", "for name, qty in cart.items():", "    total += menu[name] * qty", "if total >= 20000:", "    rate = 10", "elif total >= 10000:", "    rate = 5", "else:", "    rate = 0", "sale = total * rate // 100",
                                   'print(f"합계 {total:>7,}원")', 'print(f"할인 {sale:>7,}원 ({rate}%)")', 'print(f"결제 {total - sale:>7,}원")'], "n": 1,
           "out": ["합계  15,500원", "할인     775원 (5%)", "결제  14,725원"], "wide": True}, 96, 190, 1100, sel="c-p1")
o.append(hl(96, 190, 1100, 3, 2, "mark", 1, "15 · 합계"))
o.append(hl(96, 190, 1100, 5, 6, "run", 2, "elif · 할인율"))
o.append(hl(96, 190, 1100, 11, 1, "mark", 3, "12 · 몫"))
st = [("coffee 2잔", "4,500 × 2 = 9,000"), ("cake 1개", "6,500 × 1 = 6,500"), ("합계 15,500", "10000 이상 · 5%"), ("할인", "15500 × 5 // 100 = 775")]
for i, (k, d) in enumerate(st):
    o.append(f'<div data-build-in="rise order {min(i + 1, 3)}" style="position:absolute;left:1250px;top:{190 + i * 128}px;width:574px;height:110px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:0 24px;display:flex;flex-direction:column;justify-content:center;gap:6px">'
             + p(f"font-size:24px;font-weight:700;color:{INK}", e(k)) + p(f"font-family:{MONO};font-size:22px;color:{SUB}", e(d)) + '</div>')
o.append(caption("for로 합계를 내고, elif로 할인율 하나를 골라요.", 960))
W("x-sale", o, "15의 메뉴판과 장바구니 딕셔너리로 할인 영수증을 찍어요. 먼저 items()로 장바구니를 돌며 가격 곱하기 수량을 total에 쌓아요. 15500원이에요. 그다음 elif로 할인율 하나를 골라요. 2만 원 이상 10, 1만 원 이상 5, 나머지 0이에요. 15500은 5퍼센트예요. 할인 금액은 total 곱하기 rate를 100으로 나눈 몫이에요. 12의 // 라서 소수점 없이 775원이 돼요. 출력은 13의 칸 맞추기와 천 단위 콤마예요. cart를 바꿔 2만 원이 넘게 담아 보고 10% 할인이 나오는지 확인해요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p6", "실습"))

o = [sec("x-grade")] + head(EB6, "점수로 등급을 매겨요", K6)
o += cell({"id": "c-p2", "lines": ['scores = [["kim", 92], ["lee", 78], ["park", 85], ["choi", 59]]', "for name, score in scores:", "    if score >= 90:", '        grade = "A"', "    elif score >= 80:", '        grade = "B"', "    elif score >= 70:", '        grade = "C"', "    else:", '        grade = "F"', '    print(f"{name:<5}{score:>3}  {grade}")'], "n": 2,
           "out": ["kim   92  A", "lee   78  C", "park  85  B", "choi  59  F"]}, 96, 190, 1100, sel="c-p2")
o.append(hl(96, 190, 1100, 10, 1, "mark", 1, "for 안 · 4칸"))
stairs = [("90 이상", "A", GR), ("80 이상", "B", BL), ("70 이상", "C", OR), ("나머지", "F", RED)]
for i, (k, g, col) in enumerate(stairs):
    o.append(f'<div data-build-in="rise order {i + 2}" style="position:absolute;left:{1250 + i * 36}px;top:{190 + i * 120}px;width:{574 - i * 36}px;height:104px;background:{CARD};border:2px solid {LINE};border-left:10px solid {col};border-radius:18px;padding:0 24px;display:flex;flex-direction:row;align-items:center;gap:20px">'
             + p(f"font-family:{MONO};font-size:44px;font-weight:900;color:{col}", g) + p(f"font-size:26px;font-weight:700;color:{INK}", e(k)) + '</div>')
o.append(note_card(1250, 700, 574, 170, "계단은 위에서부터", "높은 점수 조건을 먼저 적어요. 2파트의 순서 규칙이에요.", None, ' data-build-in="rise order 6"', "gap:8px"))
o.append(caption("for 안에 elif 계단을 넣으면 한 명씩 등급이 나와요.", 940))
W("x-grade", o, "14에서 이름과 점수를 같이 담은 2차원 리스트를 썼어요. 13의 for a, b in 모양으로 이름과 점수를 한 쌍씩 꺼내요. 그리고 점수가 높은 조건부터 elif로 계단을 내려가요. 92는 첫 계단에서 A, 78은 셋째 계단에서 C예요. 조건 순서를 바꾸면 2파트에서 본 것처럼 choi를 뺀 모두가 C가 돼요. if 계단은 for 안이라 4칸, 그 안의 grade는 8칸 들여써요. print는 for 안, if 밖이라 4칸이에요. 한 명마다 한 줄씩 찍혀요." + REAL)

o = [sec("x-receipt")] + head(EB6, "메뉴판에 없는 주문은 빼고 계산해요", K6)
o += cell({"id": "c-p3", "lines": ['orders = ["coffee", "tea", "cake", "coffee", "juice"]', "total = 0", "skipped = []", "for o in orders:", "    if o in menu:", '        print(f"{o:<8}{menu[o]:>6,}원")', "        total += menu[o]", "    else:", "        skipped.append(o)", 'print(f"합계 {total:,}원")', "if skipped:", '    print("준비 중:", skipped)'], "n": 3,
           "out": ["coffee   4,500원", "cake     6,500원", "coffee   4,500원", "합계 15,500원", "준비 중: ['tea', 'juice']"], "wide": True}, 96, 190, 1100, sel="c-p3")
o.append(hl(96, 190, 1100, 4, 3, "run", 1, "있으면 계산"))
o.append(hl(96, 190, 1100, 7, 2, "mark", 2, "없으면 따로 모으기"))
o.append(hl(96, 190, 1100, 10, 1, "mark", 3, "if 리스트:"))
o.append(note_card(1250, 190, 574, 230, "KeyError가 안 나요", "1파트 처음에 멈췄던 tea를 이제 if로 먼저 물어서 건너뛰어요.", GR, ' data-build-in="rise order 1"'))
o.append(note_card(1250, 440, 574, 230, "빠진 주문도 알려 줘요", "else에서 skipped에 모았다가 끝에 한 번 찍어요. 하나도 없으면 3파트의 규칙대로 찍지 않아요.", None, ' data-build-in="rise order 2"'))
o.append(note_card(1250, 690, 574, 180, "16과 비교", "16은 & 로 먼저 걸렀어요. 이번엔 for 안에서 하나씩 물어요.", None, ' data-build-in="rise order 3"', "gap:8px"))
o.append(caption("if는 KeyError가 날 줄 앞에서 먼저 물어 막아 줘요.", 960))
W("x-receipt", o, "1파트 처음에 tea 주문에서 KeyError가 났어요. 이제 for로 주문을 하나씩 꺼내면서 메뉴판에 있는지 if로 먼저 물어요. 있으면 가격을 찍고 합계에 더해요. 없으면 else에서 skipped 리스트에 모아요. for가 끝나면 합계를 찍고, skipped가 비어 있지 않을 때만 준비 중인 메뉴를 알려 줘요. 3파트의 if 리스트: 모양이에요. 16에서는 집합의 교집합으로 미리 걸렀는데, 이번에는 하나씩 물어서 걸렀어요. 둘 다 맞는 방법이에요. 출력의 한글은 영어 두 칸 너비로 그렸어요." + REAL)

o = [sec("x-choose")] + head(EB6, "어떤 모양을 쓸지 이렇게 골라요", K6)
ch = [("if", "할 일이 한 가지, 조건이 맞을 때만", "있으면 알려 주기"),
      ("if, else", "둘 중 하나는 꼭", "살 수 있음, 돈이 모자람"),
      ("if, elif, else", "셋 이상 중 하나만", "할인율, 등급"),
      ("if 여러 개", "각각 따로 확인", "쿠폰 여러 장"),
      ("and, or, not", "조건 여러 개를 하나로", "키와 나이, 회원이거나 5만 원"),
      ("값1 if 조건 else 값2", "변수에 둘 중 하나 넣기", "msg 고르기")]
for i, (k, use, ex_) in enumerate(ch):
    y = 196 + i * 116
    o.append(f'<div data-build-in="rise order {i // 2 + 1}" style="position:absolute;left:96px;top:{y}px;width:1728px;height:100px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:0 30px;display:flex;flex-direction:row;align-items:center;gap:30px">'
             + f'<div style="width:420px;flex:none">' + mono(k, 26, K6, K6BG, "display:inline-block") + '</div>'
             + p(f"flex:1;font-size:28px;font-weight:700;color:{INK}", e(use)) + p(f"width:460px;flex:none;font-size:24px;color:{SUB}", "예: " + e(ex_)) + '</div>')
o.append(caption("처음에는 길게 적고, 같은 모양이 반복되면 줄여 써요.", 920))
W("x-choose", o, "이번 챕터에서 본 모양을 언제 쓰는지 정리해요. 조건이 맞을 때만 할 일이 있으면 if 하나, 둘 중 하나는 꼭 해야 하면 if와 else예요. 셋 이상 중 하나만 고르면 elif, 각각 따로 확인하면 if를 여러 번 써요. 조건이 여러 개면 and, or, not으로 하나로 묶어요. 변수에 둘 중 하나를 넣을 때는 한 줄 모양도 있어요. 처음에는 길게 적고 결과를 확인한 뒤 줄여요.")

# ---------- summary ----------
o = [sec("trouble")] + head("정리", "막히면 오류의 마지막 줄을 봐요", RED)
tr = [("SyntaxError: invalid syntax. Maybe you meant '=='...", "if 뒤에 = 하나를 썼어요", "=="),
      ("SyntaxError: expected ':'", "if, elif, else 줄 끝에 콜론이 없어요", "끝에 :"),
      ("IndentationError: expected an indented block", "if 다음 줄을 들여쓰지 않았어요", "4칸 들여쓰기"),
      ("IndentationError: unexpected indent", "들여쓰기 칸 수가 서로 달라요", "같은 칸에 맞추기"),
      ("TypeError: '>=' not supported ... 'str' and 'int'", "글자와 숫자를 비교했어요", "int(price)"),
      ("조건이 늘 True예요", "or 뒤에 비교 없이 값만 적었어요", 'o == "a" or o == "b"'),
      ("결과가 이상해요", "elif 순서, 들여쓰기 범위를 봐요", "좁은 조건부터")]
o.append('<div style="position:absolute;left:96px;top:196px;width:1728px;height:724px;display:flex;flex-direction:column;gap:8px">')
for i, (q, a_, cmd) in enumerate(tr, 1):
    o.append(f'<div data-build-in="rise order {min(i, 6)}" style="flex:1;display:flex;flex-direction:row;gap:26px;align-items:center;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:6px 30px">'
             + num(i, RED, 30)
             + '<div style="flex:1;display:flex;flex-direction:column;gap:2px">' + p(f"{'font-family:' + MONO + ';' if q.isascii() else ''}font-size:22px;font-weight:700;color:{INK};white-space:nowrap", e(q)) + p(f"font-size:21px;color:{SUB}", e(a_)) + '</div>'
             + p(f"width:380px;flex:none;{'font-family:' + MONO + ';font-size:22px;' if cmd.isascii() else 'font-size:23px;'}font-weight:700;line-height:1.4;color:{INK};background:#EEEFF2;padding:6px 18px;border-radius:12px;white-space:pre", e(cmd)) + '</div>')
o.append('</div>')
o.append(caption("오류가 안 나도 결과가 이상하면 어느 줄이 실행됐는지 print로 찍어 봐요.", 950))
W("trouble", o, "1번부터 5번은 오류 메시지가 나는 경우예요. SyntaxError와 IndentationError는 실행 전에 나서 셀의 어느 줄도 실행되지 않아요. 오류 위쪽의 line 숫자로 어느 줄인지 찾아요. 5번은 글자와 숫자를 비교해서 나요. 6번과 7번은 오류가 없는데 결과가 이상한 경우예요. or 뒤에 비교를 빼먹었거나, elif 순서나 들여쓰기 범위가 틀렸어요. 어느 줄이 실행됐는지 궁금하면 if 안에 print를 하나 넣어 확인해요.", ("trouble", "정리"))

o = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>']
cheat = [("if 조건:", "True일 때만 실행", K1), ("else:", "False일 때 갈 길", K2), ("elif 조건:", "위에서부터 처음 True 하나", K2), ("    (4칸)", "들여쓴 줄까지 if 안", K2),
         ("a and b   a or b", "둘 다, 하나라도", K3), ("x not in menu", "없으면", K3), ("9 <= h < 18", "범위 묻기", K3), ("if orders:", "비어 있지 않으면", K4)]
for i, (k, d, c) in enumerate(cheat):
    x, y = 96 + (i % 4) * 438, 200 + (i // 4) * 290
    o.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:414px;height:264px;background:{CARD};border:2px solid {LINE};border-top:10px solid {c};border-radius:20px;padding:28px 28px;display:flex;flex-direction:column;gap:20px">'
             + mono(k, 26 if len(k) <= 17 else 22, c, "#F6F5F1", "align-self:flex-start") + p(f"font-size:28px;font-weight:700;color:{INK}", d) + '</div>')
o.append(f'<div style="position:absolute;left:96px;top:780px;width:1728px;height:210px;background:{CARD};border:2px solid {LINE};border-radius:20px;padding:24px 36px;display:flex;flex-direction:column;justify-content:center;gap:14px">'
         + p(f"font-size:30px;font-weight:700;color:{INK}", "조건 뒤에 콜론, 다음 줄은 4칸. 묻기는 ==, 넣기는 =")
         + p(f"font-size:30px;font-weight:700;color:{INK}", "다음 챕터 18에서는 while로 조건이 True인 동안 반복하고, break로 멈춰요") + '</div>')
W("cheatsheet", o, "이번 챕터에서 쓴 모양을 한 장에 모았어요. if 조건 콜론, 다음 줄 4칸 들여쓰기가 기본이에요. else는 False일 때, elif는 위에서부터 처음 True 하나예요. and, or, not으로 조건을 묶고, 범위는 이어서 적어요. 빈 값은 False로 봐요. 18에서는 같은 조건으로 반복을 멈추는 while과 break, continue를 배워요. 이 장을 노트북 마크다운 셀에 정리해 두면 복습할 때 같이 봐요.")

# ---------- toc ----------
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
parts = [("Lightbulb", K1, "참과 거짓으로 길 고르기", "왜 필요한가, 갈림길 그림, 가장 짧은 if, 조건은 True와 False", "i-why", "i-bool"),
         ("Link", K2, "if, else, elif", "False면 건너뛰기, 들여쓰기 범위, else, elif, 순서, if 여러 개", "i-false", "i-ifif"),
         ("Activity", K3, "조건 합치기", "and, if 안의 if, or, not in, 범위, 빈 값은 False", "i-and", "i-empty"),
         ("Wrench", K4, "for와 함께, 줄여 쓰기", "골라 담기, 세기, items(), 한 줄 if else, get과 16 코드 다시 읽기", "f-pick", "f-set"),
         ("Warning", K5, "자주 나는 오류", "= 와 ==, 콜론과 들여쓰기, or 함정, 글자와 숫자 비교", "e-eq", "e-type"),
         ("Star", K6, "실습", "장바구니 할인, 성적 등급, 메뉴판 없는 주문 빼기, 모양 고르기", "x-sale", "x-choose")]
TOC_NOTE = "여섯 파트로 나눴어요. 1파트는 왜 if가 필요한지와 갈림길 그림, 2파트는 if, else, elif 모양이에요. 3파트는 and, or, not으로 조건을 합치고, 4파트는 for와 같이 쓰고 15, 16의 줄인 기능을 원래 모양과 비교해요. 5파트는 자주 나는 오류, 6파트는 카페 실습이에요. 파트마다 새 커널에서 위에서부터 차례로 실행해요."

DECK_TITLE = "제어문 1 (조건문 if)"
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
