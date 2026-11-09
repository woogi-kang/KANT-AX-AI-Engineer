"""Generates every slide of the class deck (24) and slides/deck.json.

Story: keeps writing in basics.ipynb from chapters 12-23. Starts from a 붕어빵 kept in a dictionary with a separate
function, draws the class as a 붕어빵 틀 and each object as a 붕어빵, and shows that int, str and list were classes all
along. Part 2 makes an empty class and sticks values on by hand. Part 3 builds __init__ step by step from a chapter 19
function (setup(bread, ...) moved into the class, bread renamed to self), follows self while a and b are made, and
reads self.flavor = flavor side by side. Part 4 adds methods and shows a.intro() is Bread.intro(a). Part 5 collects the
usual errors, and part 6 is a 붕어빵 order, a cafe drink label and a stamp card.
Every cell and output comes from tools/demo.sh (tools/run_nb.py runs the cells with the project kernel).
Highlights (tools/HIGHLIGHT.md): line spotlight, run band, text() value changes, DELAY on labels, fly,
magic move of self between s-self1 and s-self2, DIM on the steps, spotlight on table rows, a cursor on the lab button,
pen underlines and boxes, MARK on fixed letters, shake on a failure, COUNT on the total, SLAM and shine on the cover.
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
           f'<h1{SLAM(1)} style="font-size:{h1size}px;font-weight:900;line-height:1.1;color:#F6F5F1">{h1}</h1>',
           f'<p style="font-size:40px;line-height:1.4;color:#BFC6D4">{sub}</p>']
    cov.append(f'<div id="cov-code" style="position:absolute;left:900px;top:300px;width:900px;height:480px;background:#252B36;border-radius:24px;padding:44px 48px;display:flex;flex-direction:column;justify-content:center;gap:16px">')
    for line, c in lines:
        cov.append(p(f"font-family:{MONO};font-size:30px;font-weight:700;line-height:1.45;color:{c};white-space:pre", e(line)))
    cov.append('</div>')
    cov.append(shine(2, "cov-code"))
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


def obj(name, rows, left, top, w=440, color=BR, bg=BRBG, cls="Bread", attrs="", sid=None, rh=60, empty=None, fs=28, vids=None):
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
                 + p(f"flex:1;font-family:{MONO};font-size:{fs}px;font-weight:700;color:{RED if miss else INK};white-space:nowrap", e("없음" if miss else v), (f' id="{vids[k][0]}" data-start="{vids[k][1]}"' if vids and k in vids else "")) + '</div>')
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

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "tools"))
from highlight import *  # noqa: E402,F401,F403


# ---------- new helpers ----------
CFS = [30]   # code font size for the after deck (26 before)


def LHf():
    return CFS[0] * 1.45


def cell(c, left, top, w, sel=None, mode="cmd", pre="", attrs="", gut=True):
    """Same notebook cell as base.py, drawn at CFS[0] px. gut=False hides the [n] gutter."""
    fs, lines, n = CFS[0], c.get("lines", [""]), c.get("n")
    chosen = sel == c["id"]
    o = [f'<div id="{pre}{c["id"]}"{attrs or c.get("attrs", "")} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;display:flex;flex-direction:column;gap:10px">']
    bar = f'<div style="width:7px;flex:none;border-radius:4px;background:{SEL if chosen else "transparent"}"></div>'
    gutter = p(f"width:58px;flex:none;font-family:{MONO};font-size:22px;color:{GRAY};text-align:right;padding-top:12px", (f"[{n}]" if n else "") if gut else "")
    txt = "".join(p(f"font-family:{MONO};font-size:{fs}px;line-height:1.45;white-space:pre;color:{INK}", e(l) if l else "&#160;") for l in lines)
    tag_ = p(f"position:absolute;right:14px;bottom:8px;font-size:18px;color:{GRAY}", "Python")
    box = f'<div style="flex:1;position:relative;background:#FFFFFF;border:2px solid {LINE};border-radius:10px;padding:8px 18px 8px;display:flex;flex-direction:column">{txt}{tag_}</div>'
    o.append(f'<div style="display:flex;flex-direction:row;gap:10px;align-items:stretch">{bar}{gutter}{box}</div>')
    if c.get("out"):
        col = lambda l: RED if c.get("err") and re.match(r"[A-Za-z]+(Error|Interrupt)", l) else INK
        o.append(''.join(p(f"margin-left:85px;padding:0 20px;font-family:{MONO};font-size:{fs}px;line-height:1.45;white-space:pre;color:{col(l)}", e(l) if l else "&#160;") for l in c["out"]))
    o.append('</div>')
    return o


def hl(left, top, w, i, n=1, kind="run", order=1, tag=None):
    y = top + 10 + i * LHf()
    at = f' data-build-in="fade order {order}"' if order else ""
    return f'<div{at} style="position:absolute;left:{left + 87}px;top:{y:.0f}px;width:{w - 89}px;height:{n * LHf():.0f}px;background:{HL[kind]};border-radius:6px"></div>'


def ly(top, i):
    """Center y of code line i in a cell drawn at top."""
    return top + 10 + i * LHf() + LHf() / 2


def oy(top, n, j):
    """Center y of output line j of a cell with n code lines (output lines sit 10px apart)."""
    return top + 20 + n * LHf() + 10 + j * (LHf() + 10) + LHf() / 2


def tw(s):
    """Rendered width of a code string: Hangul is about one em, the rest 0.6 em."""
    return sum(CFS[0] * (1.0 if '가' <= ch <= '힣' else 0.6) for ch in s)


def tx(left, lines, gap=36, out=False):
    """x just right of the longest of the given lines inside a cell at left."""
    return int(left + 87 + 18 + max(tw(l) for l in lines) + gap) if not out else int(left + 85 + 20 + max(tw(l) for l in lines) + gap)


def tag(x, y, text, color, order=None, size=28, lead=True, w=None, anim="fade"):
    """A leader label: '← text' centred on y. No box."""
    at = f' data-build-in="{anim} order {order}"' if order else ""
    ws = f"width:{w}px;" if w else ""
    t = ("← " if lead else "") + e(text)
    return p(f"position:absolute;left:{x}px;top:{y - size * 0.72:.0f}px;{ws}font-size:{size}px;font-weight:700;line-height:1.45;color:{color};white-space:nowrap", t, at)


def mk(left, top, w, i, n=1, kind="mark", order=1):
    return hl(left, top, w, i, n, kind, order)


def lsp(order, left, top, w, nl, i, n=1, bar=BL):
    """Line spotlight on lines i..i+n-1 of a cell with nl code lines."""
    return lspot(order, left + 87, top, w - 87, round(18 + nl * LHf()), top + 10 + i * LHf(), n * LHf(), bar=bar)


def rb(order, left, top, w, i, n=1):
    """Green run band on lines i..i+n-1 of a cell."""
    return run(order, left + 89, round(top + 10 + i * LHf()), w - 93, round(n * LHf()))



def fix(left, top, bad, good, order, size=30, w=1728, good_html=None):
    """The wrong line struck through, an arrow, the right line."""
    return (f'<div data-build-in="rise order {order}" style="position:absolute;left:{left}px;top:{top}px;width:{w}px;display:flex;flex-direction:row;align-items:center;gap:22px">'
            + p(f"font-size:{size}px;font-weight:900;color:{RED}", "✕")
            + p(f"font-family:{MONO};font-size:{size}px;font-weight:700;color:{RED};text-decoration:line-through;text-decoration-thickness:3px;white-space:pre", e(bad))
            + arrow(70, "#C9CED8")
            + p(f"font-size:{size}px;font-weight:900;color:{GR}", "✓")
            + p(f"font-family:{MONO};font-size:{size}px;font-weight:700;color:{INK};background:#E6F4EC;border:3px solid {GR};border-radius:14px;padding:6px 20px;white-space:pre", good_html or e(good)) + '</div>')


def plain_rows(left, top, w, rows, widths, order0=1, rh=78, head_=None, fs=28, rid=None, same=False):
    """A light table: header in gray, rows split by thin rules, no boxes."""
    o = []
    y = top
    if head_:
        o.append(f'<div style="position:absolute;left:{left}px;top:{y}px;width:{w}px;height:48px;display:flex;flex-direction:row;gap:20px;border-bottom:3px solid {INK}">'
                 + "".join(p(f"width:{cw}px;flex:none;font-size:24px;font-weight:700;color:{GRAY}", e(c)) for c, cw in zip(head_, widths)) + '</div>')
        y += 56
    for i, r in enumerate(rows):
        cells_ = ""
        for k, (c, cw) in enumerate(zip(r, widths)):
            code = k > 0 and (c.isascii() or ('"' in c or "[" in c or "." in c))
            cells_ += p(f"width:{cw}px;flex:none;font-family:{MONO if code else SANS};font-size:{fs}px;font-weight:{700 if k == 0 or code else 500};color:{INK if k else SUB};white-space:pre", e(c))
        idp = f' id="{rid}{i}"' if rid else ""
        o.append(f'<div{idp} data-build-in="rise order {order0 if same else order0 + i}" style="position:absolute;left:{left}px;top:{y + i * rh}px;width:{w}px;height:{rh}px;display:flex;flex-direction:row;align-items:center;gap:20px;border-bottom:2px solid {LINE}">{cells_}</div>')
    return o


def mold2(left, top, w, title, lines, attrs="", fs=32, tfs=38):
    body = "".join(p(f"font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:1.6;color:{INK};white-space:pre", (e(l) if l else "&#160;")) for l in lines)
    return (f'<div{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;background:{MDBG};border:6px dashed {MD};border-radius:30px;padding:36px 44px;display:flex;flex-direction:column;gap:18px">'
            + p(f"font-family:{MONO};font-size:{tfs}px;font-weight:700;color:{MD}", e(title)) + f'<div style="display:flex;flex-direction:column">{body}</div></div>')


def mini(left, top, rows_ok, order):
    """A small 붕어빵 for the '10개라면' picture: two slots, a missing one dashed red."""
    slots_ = "".join(f'<div style="height:22px;border-radius:6px;background:{BRBG if ok else CARD};border:2px {"solid" if ok else "dashed"} {LINE if ok else RED}"></div>' for ok in rows_ok)
    return (f'<div data-build-in="rise order {order}" style="position:absolute;left:{left}px;top:{top}px;width:132px;background:{CARD};border:3px solid {BR};border-radius:16px;overflow:hidden">'
            f'<div style="height:24px;background:{BR}"></div><div style="padding:8px;display:flex;flex-direction:column;gap:6px">{slots_}</div></div>')


def caption2(text, top=960, order=None):
    at = f' data-build-in="rise order {order}"' if order else ' data-build-in="rise"'
    return p(f"position:absolute;left:96px;top:{top}px;width:1728px;font-size:34px;font-weight:700;line-height:1.4;color:{INK}", text, ' id="caption"' + at)


def x_of(left, prefix):
    """x where text starts after prefix on a code or output line of a cell drawn at left."""
    return left + 105 + tw(prefix)


def out_ring(order, left, top, n, j, prefix, text, color=RED):
    """Pen ring around part of output line j (cell at left, top with n code lines)."""
    return ring(order, round(x_of(left, prefix)), round(oy(top, n, j) - LHf() / 2), round(tw(text)), round(LHf()), color)


def code_box_mark(order, left, top, i, prefix, text, color=RED):
    """Pen box around part of code line i. Code lines sit close together, so a box instead of a ring (HIGHLIGHT.md)."""
    return box(order, round(x_of(left, prefix)) - 10, round(ly(top, i) - LHf() / 2) - 2, round(tw(text)) + 12, round(LHf()) + 4, color)


def out_ul(order, left, top, n, j, prefix, text, color=RED):
    x1 = round(x_of(left, prefix))
    return underline(order, x1, round(x1 + tw(text)), round(oy(top, n, j) + LHf() * 0.4), color)


def code_ul(order, left, top, i, prefix, text, color=OR):
    x1 = round(x_of(left, prefix))
    return underline(order, x1, round(x1 + tw(text)), round(ly(top, i) + LHf() * 0.4), color)


B = lambda: None
FW = 1180   # code cell width when tags sit to its right
TX = 96 + FW + 30   # x of leader tags right of a cell


# ---------- cover ----------
cover([("class Bread:", "#C7B8F2"), ("    def __init__(self, flavor, price):", W_), ("        self.flavor = flavor", "#F2C48D"), ("        self.price = price", "#F2C48D"), ("", W_),
       ('a = Bread("팥", 1000)', "#8FD8DE"), ('b = Bread("슈크림", 1200)', "#8FD8DE")],
      "클래스 1<br>붕어빵 틀과 붕어빵", "틀 하나로 붕어빵을<br>여러 개 찍어 내기",
      "클래스는 붕어빵 틀이고, 틀로 찍어 낸 붕어빵 하나하나가 객체예요. 오늘부터 세 챕터 동안 클래스를 배워요. 클래스는 붕어빵 틀이고, 그 틀로 찍어 낸 붕어빵 하나하나가 객체예요. 이번 챕터는 틀을 만들고, 찍을 때 재료를 넣는 __init__과 self를 천천히 봐요. 그다음 붕어빵이 할 일을 메서드로 붙여요. 25에서는 print로 보기 좋게 찍는 법, 26에서는 틀을 물려받는 상속을 배워요.", h1size=84)

# ---------- ready: plain checklist, one panel ----------
o = [sec("ready")] + head("들어가기", "23에서 이어서 해요", JP)
for i, (a_, b_) in enumerate([("변수, 타입, 함수 type()", "12"), ("리스트, f-string, for", "13"), ("딕셔너리", "15"), ("def, 매개변수, return", "19"), ("기본값, 지역 변수", "20")]):
    o.append(f'<div data-build-in="rise order 1"{DELAY(i * 90)} style="position:absolute;left:96px;top:{230 + i * 120}px;width:760px;height:104px;display:flex;flex-direction:row;gap:24px;align-items:center;border-bottom:2px solid {LINE}">'
             + f'<x-icon name="CheckCircle" style="width:48px;height:48px;color:{GR}"></x-icon>'
             + p(f"flex:1;font-size:34px;font-weight:700;color:{INK}", e(a_))
             + p(f"font-size:30px;font-weight:700;color:{GRAY}", e(b_)) + '</div>')
o.append(p(f"position:absolute;left:1000px;top:256px;font-size:36px;font-weight:700;color:{JP}", "노트북 다시 열기", ' data-build-in="rise order 2"'))
steps_ = [p(f"font-size:32px;color:{INK}", "VS Code로 hello-uv 폴더 열기"),
          p(f"font-size:32px;color:{INK}", "탐색기에서") + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{JP}", NB) + p(f"font-size:32px;color:{INK}", "열기"),
          p(f"font-size:32px;color:{INK}", "오른쪽 위 커널이 .venv인지 보기"),
          p(f"font-size:32px;color:{INK}", "셀에 적고") + kbd("Shift+Enter", 26) + p(f"font-size:32px;color:{INK}", "로 실행")]
for i, inner in enumerate(steps_):
    o.append(row(1000, 352 + i * 120, 824, 104, num(i + 1, JP, 40) + inner, 2).replace('data-build-in="rise order 2"', 'data-build-in="rise order 2"' + DELAY(90 + i * 90), 1))
o.append(caption2("기억이 안 나면 왼쪽에 적힌 챕터를 먼저 다시 봐요.", 900))
W("ready", o, "12부터 쓰던 basics.ipynb에 이어서 적어요. 09에서 만든 hello-uv 폴더를 VS Code로 열고, 12부터 쓰던 basics.ipynb를 다시 열어요. 이번 챕터는 19, 20의 함수를 많이 써요. 매개변수가 순서대로 들어간다는 것, 함수 안에서 만든 변수는 끝나면 사라진다는 것이 기억나지 않으면 19, 20을 먼저 봐요. 슬라이드의 출력은 tools/demo.sh가 hello-uv 커널에서 같은 셀을 실제로 실행한 결과예요. 셀 번호는 파트마다 [1]부터 다시 셌어요.")

# ---------- part 1 ----------
o = [sec("c-why")] + head(EB1, "붕어빵을 딕셔너리로 담으면 값과 할 일이 따로 놀아요", K1)
WHY = ['b1 = {"flavor": "팥", "price": 1000}', 'b2 = {"flavor": "슈크림", "price": 1200}', "", "def intro(bread):", '    print(bread["flavor"], "붕어빵", bread["price"], "원")', "", "intro(b1)", "intro(b2)"]
T1, T2 = 210, 710
o += cell({"id": "c-why1", "lines": WHY, "n": 1, "out": ["팥 붕어빵 1000 원", "슈크림 붕어빵 1200 원"]}, 96, T1, FW, sel="c-why1")
o += cell({"id": "c-why2", "lines": ['b3 = {"flavr": "피자", "price": 1500}', "intro(b3)"], "n": 2, "out": ["KeyError: 'flavor'"], "err": True, "attrs": ' data-build-in="rise order 3"'}, 96, T2, FW, sel="c-why2")
o.append(lsp(1, 96, T1, FW, len(WHY), 0, 2, K1))
o.append(tag(TX, ly(T1, 0.5), "값은 딕셔너리에", K1, 1))
o.append(lsp(2, 96, T1, FW, len(WHY), 3, 2, K1))
o.append(lspot_off(3))
o.append(tag(TX, ly(T1, 3.5), "할 일은 밖의 함수에", K1, 2))
o.append(code_ul(4, 96, T2, 0, 'b3 = {', '"flavr"', RED))
o.append(tag(TX, ly(T2, 0), "키를 틀려도 조용해요", RED, 4))
o.append(out_ring(5, 96, T2, 2, 0, "", "KeyError: 'flavor'"))
o.append(tag(TX, oy(T2, 2, 0), "쓸 때 터져요", RED, 5))
o.append(caption2("값과 할 일을 한 틀에 묶어 두는 방법이 클래스예요.", 960, 6))
W("c-why", o, "딕셔너리와 함수로는 값과 할 일이 따로 있어서, 키를 틀려도 쓸 때까지 몰라요. 지금까지 배운 것으로 붕어빵 가게를 만들어 봐요. 붕어빵 하나를 맛과 가격이 든 딕셔너리로 담고, 소개하는 일은 함수로 따로 만들었어요. 잘 돌아가지만 붕어빵 정보와 소개하는 함수가 서로 다른 곳에 있어요. 2번 셀처럼 키를 flavr로 잘못 적어도 만들 때는 아무 말이 없어요. 한참 뒤 소개할 때 KeyError가 나요. 값과 할 일을 한 틀에 묶어 두고, 찍을 때 재료를 꼭 넣게 하는 방법이 클래스예요." + REAL, ("p1", "왜 필요한가"))

o = [sec("c-big")] + head(EB1, "틀 하나로 붕어빵을 여러 개 찍어요", K1)
# geometry: two objects 300-545 and 580-825; the mold spans the same height so the three read as one row
OA, OB, OH = 260, 540, 245
MROW = lambda lab, code, extra="": (f'<div style="display:flex;flex-direction:row;align-items:center;height:64px">'
        + p(f"width:110px;flex:none;font-size:32px;font-weight:700;color:{SUB}", e(lab))
        + p(f"font-family:{MONO};font-size:34px;font-weight:700;color:{INK};white-space:pre", e(code)) + extra + '</div>')
o.append(f'<div id="mold" data-build-in="rise order 1" style="position:absolute;left:96px;top:{OA}px;width:660px;height:{OB + OH - OA}px;background:{MDBG};border:6px dashed {MD};border-radius:30px;padding:0 48px;display:flex;flex-direction:column;justify-content:center;gap:10px">'
         + p(f"font-family:{MONO};font-size:40px;font-weight:700;color:{MD};margin-bottom:18px", "class Bread")
         + MROW("맛", "flavor = ?") + MROW("가격", "price  = ?")
         + '<div style="height:24px"></div>'
         + MROW("할 일", "intro()", p(f"margin-left:24px;font-size:30px;font-weight:700;color:{K4}", "← 메서드", ' data-build-in="fade order 5"'))
         + '</div>')
o.append(tag(96, OB + OH + 50, "틀 = 클래스", MD, 1, 32, False))
for k, (top_, lab) in enumerate([(OA, "팥, 1000"), (OB, "슈크림, 1200")]):
    cy = top_ + OH // 2
    o.append(harrow(800, cy - 15, 240, BR, f' data-build-in="fade order {2 + k}"'))
    o.append(p(f"position:absolute;left:800px;top:{cy - 68}px;width:240px;text-align:center;font-size:30px;font-weight:700;color:{BR}", lab, f' data-build-in="fade order {2 + k}"'))
o.append(obj("a", [("flavor", '"팥"'), ("price", "1000")], 1100, OA, 560, cls="", rh=68, fs=32, attrs=' data-build-in="fly order 2" data-from="mold"'))
o.append(obj("b", [("flavor", '"슈크림"'), ("price", "1200")], 1100, OB, 560, cls="", rh=68, fs=32, attrs=' data-build-in="fly order 3" data-from="mold"'))
o.append(tag(1100, OB + OH + 50, "붕어빵 = 객체", BR, 4, 32, False))
# 속성: a bracket beside a's two rows
o.append(f'<div data-build-in="fade order 5" style="position:absolute;left:1676px;top:{OA + 82}px;width:16px;height:150px;border:4px solid {K3};border-left:none;border-radius:0 10px 10px 0"></div>')
o.append(tag(1708, OA + 82 + 75, "속성", K3, 5, 32, False))
W("c-big", o, "틀은 클래스, 틀로 찍어 낸 붕어빵 하나하나는 객체예요. 왼쪽의 점선 상자가 붕어빵 틀이에요. 틀에는 맛과 가격을 넣을 자리, 그리고 소개하기 같은 할 일이 적혀 있어요. 틀에 팥과 1000원을 넣고 찍으면 붕어빵 a가, 슈크림과 1200원을 넣고 찍으면 붕어빵 b가 나와요. 틀은 하나인데 붕어빵은 몇 개든 찍을 수 있어요. 틀을 클래스, 찍어 낸 붕어빵을 객체라고 불러요. 붕어빵에 든 값은 속성, 붕어빵이 하는 일은 메서드예요. 이 네 단어를 오늘 계속 써요. 틀은 class로 만들어요.")

o = [sec("c-type")] + head(EB1, "사실 int, str, list도 틀이에요", K1)
T1, T2 = 220, 590
o += cell({"id": "c-t1", "lines": ["print(type(3))", 'print(type("팥"))', "print(type([1, 2]))"], "n": 3, "out": ["<class 'int'>", "<class 'str'>", "<class 'list'>"]}, 96, T1, 900, sel="c-t1")
o += cell({"id": "c-t2", "lines": ["xs = [1, 2]", "xs.append(3)", "print(xs)", 'print("Pat".lower())'], "n": 4, "out": ["[1, 2, 3]", "pat"], "attrs": ' data-build-in="rise order 3"'}, 96, T2, 900, sel="c-t2")
TC = tx(96, ['print("Pat".lower())'])
o.append(tag(TC, oy(T1, 3, 0), "int 틀로 찍은 객체", K1, 1))
o.append(tag(TC, oy(T1, 3, 1), "str 틀로 찍은 객체", K1, 2))
o.append(tag(TC, oy(T1, 3, 2), "list 틀로 찍은 객체", K1, 2))
o.append(code_ul(4, 96, T2, 1, "xs.", "append", K4))
o.append(tag(TC, ly(T2, 1), "list 틀의 메서드 (13)", K4, 4))
o.append(code_ul(5, 96, T2, 3, 'print("Pat".', "lower", K4))
o.append(tag(TC, ly(T2, 3), "str 틀의 메서드 (22)", K4, 5))
o.append(caption2("이미 써 온 틀처럼, 붕어빵 틀을 직접 만들어 봐요.", 960, 6))
W("c-type", o, "int, str, list도 파이썬이 미리 만들어 둔 틀이에요. 클래스는 처음 보는 게 아니에요. 12에서 type()을 쳤을 때 class int, class str이라고 나왔어요. 숫자 3은 int라는 틀로, 글자 팥은 str이라는 틀로, 리스트는 list 틀로 찍은 객체예요. 13에서 쓴 append, 22에서 쓴 lower처럼 점 뒤에 붙여 쓰던 함수가 메서드예요. 파이썬이 미리 만들어 둔 틀 안의 할 일이에요. 오늘은 이런 틀을 Bread라는 이름으로 직접 만들어요." + REAL)

# ---------- part 2 ----------
o = [sec("m-empty")] + head(EB2, "빈 틀을 만들고 붕어빵 두 개를 찍어요", K2)
T1 = 300
o += cell({"id": "c-m1", "lines": ["class Bread:", "    pass", "", "a = Bread()", "b = Bread()", "print(type(a))"], "n": 1, "out": ["<class '__main__.Bread'>"]}, 96, T1, 1000, sel="c-m1")
o.append(lsp(1, 96, T1, 1000, 6, 0, 1, MD)); o.append(tag(tx(96, ["print(type(a))"]), ly(T1, 0), "틀 이름, 첫 글자는 대문자", MD, 1))
o.append(lsp(2, 96, T1, 1000, 6, 1, 1, GRAY)); o.append(tag(tx(96, ["print(type(a))"]), ly(T1, 1), "아직 빈 틀", GRAY, 2))
o.append(lsp(3, 96, T1, 1000, 6, 3, 2, BR)); o.append(lspot_off(4)); o.append(tag(tx(96, ["print(type(a))"]), ly(T1, 3.5), "괄호를 붙이면 한 개 찍혀요", BR, 3))
o.append(tag(tx(96, ["<class '__main__.Bread'>"], out=True), oy(T1, 6, 0), "이 노트북(__main__)의 Bread", K2, 4))
o.append(obj("a", [], 1180, 300, 300, cls="", empty="빈 붕어빵", rh=300, attrs=' data-build-in="rise order 3"'))
o.append(obj("b", [], 1524, 300, 300, cls="", empty="빈 붕어빵", rh=300, attrs=' data-build-in="rise order 3"'))
o.append(caption2("a와 b는 같은 틀로 찍은 서로 다른 붕어빵이에요.", 900, 5))
W("m-empty", o, "class 이름:과 pass만 있으면 틀이 되고, 이름 뒤에 괄호를 붙이면 붕어빵이 찍혀요. class 뒤에 틀 이름을 적고 콜론을 붙여요. 틀 이름은 첫 글자를 대문자로 적는 게 약속이에요. 틀 안에 아직 넣을 게 없으면 pass라고 적어요. 아무것도 안 적으면 오류가 나서 자리를 채우는 말이에요. Bread()처럼 틀 이름 뒤에 괄호를 붙이면 붕어빵이 하나 찍혀요. a와 b는 같은 틀로 찍었지만 서로 다른 붕어빵이에요. type(a)를 보면 지금 노트북에서 만든 Bread 틀의 객체라고 나와요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p2", "가장 작은 틀"))

o = [sec("m-attr")] + head(EB2, "점(.)으로 붕어빵에 값을 붙여요", K2)
T1 = 230
o += cell({"id": "c-m2", "lines": ['a.flavor = "팥"', "a.price = 1000", 'b.flavor = "슈크림"', "b.price = 1200", "print(a.flavor, a.price)", "print(b.flavor, b.price)"], "n": 2, "out": ["팥 1000", "슈크림 1200"]}, 96, T1, 900, sel="c-m2")
o.append(obj("a", [("flavor", '"팥"'), ("price", "1000")], 1060, 230, 360, cls="", rh=64, fs=30, attrs=' data-build-in="rise order 1"'))
o.append(obj("b", [("flavor", '"슈크림"'), ("price", "1200")], 1464, 230, 360, cls="", rh=64, fs=30, attrs=' data-build-in="rise order 2"'))
o.append(tag(1060, 520, "붕어빵에 붙은 값 = 속성", K3, 2, 28, False))
o += plain_rows(96, 680, 1728, [["값 넣기", 'b1["flavor"] = "팥"', 'a.flavor = "팥"'], ["값 꺼내기", 'b1["flavor"]', "a.flavor"]], [300, 680, 680], 3, 84, ["", "딕셔너리 (15)", "붕어빵"], 30, rid="ma-r", same=True)
o.append(spot(4, target="ma-r0", pad=8, r=12, dim=0.5))
o.append(spot(5, target="ma-r1", pad=8, r=12, dim=0.5))
o.append(spot_off(6))
o.append(caption2("a.flavor는 \"a의 flavor\"로 읽어요.", 960, 6))
W("m-attr", o, "붕어빵 이름 뒤에 점을 찍고 칸 이름을 적으면 값을 붙이고 꺼낼 수 있어요. 붕어빵 이름 뒤에 점을 찍고 칸 이름을 적은 뒤 값을 넣어요. a.flavor는 a의 flavor라고 읽어요. 이렇게 붕어빵에 붙은 값을 속성이라고 불러요. a와 b에 서로 다른 맛과 가격이 들어갔어요. 15의 딕셔너리와 비교하면 대괄호와 따옴표 대신 점 하나로 넣고 꺼내요." + REAL)

o = [sec("m-tedious")] + head(EB2, "손으로 붙이면 길고, 하나 빠뜨리기 쉬워요", K2)
T1 = 230
o += cell({"id": "c-m3", "lines": ["c = Bread()", 'c.flavor = "피자"', "print(c.price)"], "n": 3, "out": ["AttributeError: 'Bread' object has no attribute 'price'"], "err": True}, 96, T1, 1100, sel="c-m3")
o.append(mk(96, T1, 1100, 1, 1, "err", 1)); o.append(tag(tx(96, ['c.flavor = "피자"']), ly(T1, 1), "price 줄을 빠뜨렸어요", RED, 1))
o.append(out_ul(2, 96, T1, 3, 0, "AttributeError: 'Bread' object ", "has no attribute 'price'"))
o.append(obj("c", [("flavor", '"피자"'), ("price", None)], 1300, 230, 524, cls="", rh=68, fs=30, attrs=' data-build-in="rise order 2"'))
o.append(p(f"position:absolute;left:96px;top:560px;font-size:32px;font-weight:700;color:{K2}", "붕어빵이 10개라면 30줄을 손으로 적어요", ' data-build-in="fade order 3"'))
for i in range(10):
    miss = i in (3, 7)
    o.append(mini(96 + i * 174, 630, [True, not miss], 3).replace('"rise order 3"', '"rise order 3"' + DELAY(120 + i * 60), 1))
o.append(p(f"position:absolute;left:96px;top:800px;font-size:28px;font-weight:700;color:{RED}", "한 줄만 빠져도 그 붕어빵은 칸이 비어요", ' data-build-in="fade order 4"'))
o.append(caption2("찍는 순간 재료를 한 번에 넣게 하면 빠뜨릴 일이 없어요.", 960, 5))
W("m-tedious", o, "손으로 붙이면 붕어빵마다 줄이 늘고, 한 줄만 빠져도 칸이 비어요. c를 찍고 맛만 붙였더니, 가격을 꺼낼 때 AttributeError가 났어요. Bread 객체에 price라는 속성이 없다는 뜻이에요. 붕어빵이 열 개라면 찍는 줄, 맛 붙이는 줄, 가격 붙이는 줄을 열 번씩 적어야 해요. 한 줄만 빠져도 그 붕어빵은 칸이 비어요. 찍는 순간 재료를 한 번에 넣게 만드는 방법이 다음 파트의 __init__이에요." + REAL)

# ---------- part 3 ----------
o = [sec("s-func")] + head(EB3, "먼저 19에서 배운 함수로 한 번에 붙여 봐요", K3)
SF = ["class Bread:", "    pass", "", "def setup(bread, flavor, price):", "    bread.flavor = flavor", "    bread.price = price", "", "a = Bread()", 'setup(a, "팥", 1000)', "print(a.flavor, a.price)"]
T1 = 220
o += cell({"id": "c-s1", "lines": SF, "n": 1, "out": ["팥 1000"]}, 96, T1, 900, sel="c-s1")
o.append(mk(96, T1, 900, 3, 3, "mark", 1))
o.append(code_box(1060, 220, 764, [[("setup(", W_), ("a", CS, "sf-a"), (", ", W_), ('"팥"', CA, "sf-f"), (", ", W_), ("1000", CA, "sf-p"), (")", W_)]], ' data-build-in="rise order 2"', 40, 130))
for i, (top_, bot, c, bg) in enumerate([("a", "bread", BR, BRBG), ('"팥"', "flavor", TEAL, K3BG), ("1000", "price", TEAL, K3BG)]):
    x = 1060 + i * 262
    o.append(harrow(x + 86, 410, 70, c, f' data-build-in="fade order {3 + i}"', 90))
    o.append(p(f"position:absolute;left:{x}px;top:480px;width:240px;height:96px;border-radius:18px;background:{bg};border:3px solid {c};font-family:{MONO};font-size:34px;font-weight:700;line-height:90px;text-align:center;color:{INK}", e(bot), f' data-build-in="rise order {3 + i}"'))
o.append(tag(1060, 640, "첫 칸이 어느 붕어빵에 붙일지 정해요", BR, 6, 30, False))
o.append(tag(1060, 700, "이 칸이 곧 self가 돼요", K3, 6, 30, False))
o.append(caption2("bread.flavor = flavor는 a에 맛 칸을 붙이는 것과 같아요.", 820, 7))
W("s-func", o, "함수의 첫 칸에 붕어빵을 넘기면 그 붕어빵에 칸을 붙일 수 있어요. __init__으로 바로 가기 전에, 이미 아는 함수로 같은 일을 해 봐요. setup 함수는 붕어빵 하나와 맛, 가격을 받아요. 19에서 배운 대로 인자는 순서대로 들어가요. 첫 번째 칸 bread에는 a가, flavor에는 팥이, price에는 1000이 들어가요. 함수 안의 bread.flavor = flavor는 a에 맛 칸을 붙이는 것과 같아요. 첫 번째 칸이 어느 붕어빵에 붙일지 정한다는 것을 기억해 둬요. 이 칸이 곧 self가 돼요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p3", "self와 __init__"))

o = [sec("s-move")] + head(EB3, "그 함수를 틀 안에 넣으면 __init__이에요", K3)
L1 = ["", "def setup(bread, flavor, price):", "    bread.flavor = flavor", "    bread.price = price", "", "a = Bread()", 'setup(a, "팥", 1000)']
L2 = ["class Bread:", "    def __init__(self, flavor, price):", "        self.flavor = flavor", "        self.price = price", "", "", 'a = Bread("팥", 1000)']
T1 = 230
o += cell({"id": "mv1", "lines": L1, "out": ["팥 1000"]}, 96, T1, 840)
o += cell({"id": "mv2", "lines": L2, "out": ["팥 1000"], "attrs": ' data-build-in="rise order 1"'}, 984, T1, 840)
o.append(p(f"position:absolute;left:183px;top:186px;font-size:26px;font-weight:700;color:{GRAY}", "밖에 둔 함수"))
o.append(p(f"position:absolute;left:1071px;top:186px;font-size:26px;font-weight:700;color:{K3}", "틀 안의 __init__", ' data-build-in="fade order 1"'))
o.append(lsp(2, 984, T1, 840, 7, 0, 1, MD))
o.append(lsp(3, 984, T1, 840, 7, 1, 1, K3))
o.append(lsp(4, 984, T1, 840, 7, 6, 1, BR))
o.append(lspot_off(5))
for i, (k, d, c, o_) in enumerate([("① 들여쓰기", "class 아래로 넣어요", MD, 2), ("② setup → __init__", "찍을 때 저절로 불리는 약속된 이름", K3, 3), ("③ bread → self", "이름만 바뀌고 하는 일은 같아요", BR, 3), ('④ Bread("팥", 1000)', "a를 넘기지 않아요. 파이썬이 넣어 줘요", TEAL, 4)]):
    y = 690 + i * 70
    o.append(row(96, y, 1728, 64, p(f"width:520px;flex:none;font-family:{MONO};font-size:30px;font-weight:700;color:{c};white-space:pre", e(k)) + p(f"font-size:30px;color:{INK}", e(d)), o_))
W("s-move", o, "setup 함수를 틀 안에 넣고 이름을 __init__으로 바꾸면 찍을 때 저절로 불려요. 왼쪽은 앞 장의 setup 함수, 오른쪽은 같은 일을 틀 안에 넣은 모양이에요. 다른 점은 네 가지예요. 첫째, 함수를 class 아래로 들여 써서 틀 안에 넣었어요. 둘째, 이름을 __init__으로 바꿨어요. 이 이름은 파이썬과 약속된 이름이라, 붕어빵을 찍을 때 저절로 불려요. 셋째, 첫 번째 칸 이름이 bread에서 self로 바뀌었어요. 이름만 바뀌었고 어느 붕어빵에 붙일지 정하는 칸인 건 같아요. 넷째, 부를 때 a를 넘기지 않아요. 파이썬이 방금 찍은 붕어빵을 첫 칸에 넣어 줘요. 두 셀의 결과는 똑같아요." + REAL)

o = [sec("s-init")] + head(EB3, "괄호 안의 재료가 __init__의 칸에 들어가요", K3)
o.append(code_box(96, 220, 1728, [[("a = ", W_), ("Bread", W_, "si-new"), ("(", W_), ('"팥"', CA, "si-a1"), (", ", W_), ("1000", CA, "si-a2"), (")", W_)]], "", 44, 130))
for i, (top_, bot, c, bg, o_) in enumerate([("새 붕어빵", "self", BR, BRBG, 1), ('"팥"', "flavor", TEAL, K3BG, 2), ("1000", "price", TEAL, K3BG, 3)]):
    x = 96 + i * 590
    o.append(p(f"position:absolute;left:{x}px;top:450px;width:548px;height:110px;border-radius:18px;border:3px {'dashed' if i == 0 else 'solid'} {c};background:{CARD};font-family:{MONO if i else SANS};font-size:40px;font-weight:700;line-height:104px;text-align:center;color:{INK}", e(top_), f' data-build-in="fly order {o_}" data-from="{["si-new", "si-a1", "si-a2"][i]}"'))
    o.append(harrow(x + 239, 600, 70, c, f' data-build-in="fade order {o_}"', 90))
o.append(code_box(96, 680, 1728, [[("def __init__(", W_), ("self", CS), (", ", W_), ("flavor", CA), (", ", W_), ("price", CA), ("):", W_)]], "", 44, 130))
# put the three parameter words right under their chips by drawing chips over the def line? Keep labels below instead.
o.append(tag(96, 404, "파이썬이 넣어 줘요", BR, 1, 28, False))
o.append(tag(686, 404, "괄호 안의 재료가 순서대로 (19의 매개변수)", TEAL, 2, 28, False))
o.append(underline(4, 473, 579, 778, CS))
o.append(tag(96, 870, "칸은 셋, 재료는 둘. 첫 칸 self는 적지 않아요", BR, 4, 30, False))
o.append(tag(96, 930, "__init__ = 앞뒤 밑줄 두 개씩, initialize(처음 준비)", K3, 5, 30, False))
W("s-init", o, "괄호 안의 재료는 self 뒤 칸에 순서대로 들어가고, self 칸은 파이썬이 채워요. 찍는 줄과 __init__의 첫 줄을 위아래로 놓았어요. Bread 괄호 안에는 재료가 두 개, __init__에는 칸이 세 개예요. 하나가 남는 이유가 self예요. self 칸에는 파이썬이 방금 찍은 빈 붕어빵을 넣어 줘요. 그래서 우리는 괄호 안에 self를 적지 않아요. 팥과 1000은 19에서 배운 매개변수처럼 flavor, price에 순서대로 들어가요. __init__은 앞뒤로 밑줄을 두 개씩 적어요. init은 처음 준비한다는 뜻의 initialize를 줄인 말이에요.")

o = [sec("s-print")] + head(EB3, "__init__은 찍는 순간 저절로 불려요", K3)
SP = ["class Bread:", "    def __init__(self, flavor, price):", '        print("반죽 붓는 중:", flavor)', "        self.flavor = flavor", "        self.price = price", "", 'a = Bread("팥", 1000)', 'b = Bread("슈크림", 1200)', "print(a.flavor, b.flavor)"]
T1 = 220
o += cell({"id": "c-s3", "lines": SP, "n": 3, "out": ["반죽 붓는 중: 팥", "반죽 붓는 중: 슈크림", "팥 슈크림"]}, 96, T1, FW, sel="c-s3")
o.append(mk(96, T1, FW, 2, 1, "mark", 1)); o.append(tag(TX, ly(T1, 2), "확인용 print", BL, 1))
o.append(mk(96, T1, FW, 6, 2, "run", 2)); o.append(tag(TX, ly(T1, 6.5), "__init__을 직접 부르지 않았어요", GR, 2))
o.append(tag(tx(96, ["반죽 붓는 중: 슈크림"], out=True), oy(T1, 9, 0), "a를 찍을 때 한 번", GR, 3))
o.append(tag(tx(96, ["반죽 붓는 중: 슈크림"], out=True), oy(T1, 9, 1), "b를 찍을 때 한 번", GR, 3).replace('order 3"', 'order 3"' + DELAY(250), 1))
o.append(caption2("붕어빵마다 꼭 있어야 하는 값을 찍는 순간 넣어 둘 때 써요.", 880, 4))
W("s-print", o, "__init__은 붕어빵을 찍을 때마다 한 번씩 저절로 불려요. __init__이 정말 저절로 불리는지 print를 넣어 확인해 봐요. __init__ 첫 줄에 반죽 붓는 중이라는 출력을 넣었어요. 우리는 __init__을 부르는 줄을 한 번도 적지 않았어요. 그런데 Bread를 찍는 두 줄마다 한 번씩 출력이 나왔어요. 파이썬이 찍을 때마다 __init__을 찾아서 불러 준 거예요. 붕어빵마다 꼭 있어야 하는 값을 찍는 순간 넣어 두고 싶을 때 __init__을 써요. 확인이 끝나면 print 줄은 지워도 돼요." + REAL)

SELF_CODE = [[("def __init__(", W_), ("self", CS), (", flavor, price):", W_)], [("    ", W_), ("self", CS), (".flavor = flavor", W_)], [("    ", W_), ("self", CS), (".price = price", W_)]]
for k, (sid, cur_line) in enumerate([("s-self1", 0), ("s-self2", 1)]):
    o = [sec(sid, "magic" if k else "fade")] + head(EB3, "self는 지금 찍고 있는 그 붕어빵이에요", K3)
    for i, t in enumerate(['a = Bread("팥", 1000)', 'b = Bread("슈크림", 1200)']):
        on = i == cur_line
        o.append(p(f"position:absolute;left:96px;top:{240 + i * 110}px;width:820px;height:92px;border-radius:14px;padding:0 28px;line-height:92px;font-family:{MONO};font-size:36px;font-weight:700;color:{INK if on else '#B4B9C3'};background:{K3BG if on else CARD};border:3px solid {K3 if on else LINE};white-space:pre", e(t), f' id="line{i}"'))
    o.append(code_box(96, 500, 820, SELF_CODE, ' id="initbox"', 34, 260))
    o.append(obj("a", [("flavor", '"팥"'), ("price", "1000")], 1100, 240, 480, cls="", rh=68, fs=32, sid="obj-a"))
    if k:
        o.append(obj("b", [("flavor", '"슈크림"'), ("price", "1200")], 1100, 560, 480, cls="", rh=68, fs=32, sid="obj-b", attrs=' data-build-in="rise order 1"'))
    o.append(pill("← self", 1610, 300 + k * 320, BR, "#FFE7C2", ' id="self-pill"', 36))
    if not k:
        o.append(pulse(1, "self-pill"))
    o.append(p(f"position:absolute;left:96px;top:880px;width:1728px;font-size:34px;font-weight:700;line-height:1.4;color:{INK}",
               ("첫째 줄에서 self는 a, 둘째 줄에서 self는 b예요. 코드 한 벌로 붕어빵마다 다른 값을 붙여요." if k else "a를 찍는 동안 self.flavor = flavor는 a.flavor = \"팥\"과 같아요."), ' id="selfnote"'))
    W(sid, o, ("a를 찍는 동안 self는 a예요. a를 찍는 순간을 멈춰서 봐요. 파이썬이 빈 붕어빵을 하나 만들고, 그 붕어빵을 self 칸에 넣어 __init__을 불러요. 그래서 지금 self는 a를 가리켜요. self.flavor = flavor는 지금은 a.flavor = 팥과 같은 일을 해요. 다음 장으로 넘기면 b를 찍을 때를 봐요."
                if not k else "b를 찍을 때는 self가 b라서, 코드 한 벌로 붕어빵마다 다른 값을 붙여요. b를 찍는 줄로 내려왔어요. 이번에는 새 빈 붕어빵이 self 칸에 들어가서 self가 b를 가리켜요. 같은 __init__ 코드가 이번엔 b에 슈크림과 1200을 붙여요. self라는 이름 하나가 찍을 때마다 다른 붕어빵을 가리키기 때문에 코드 한 벌로 붕어빵을 몇 개든 만들 수 있어요. self는 나 자신이라는 뜻의 영어예요. 붕어빵 입장에서 내 맛, 내 가격이라고 읽으면 쉬워요."))

o = [sec("s-steps")] + head(EB3, "a = Bread(\"팥\", 1000) 한 줄에서 일어나는 일", K3)
ST5 = [("①", 'Bread("팥", 1000)', "빈 붕어빵이 하나 생겨요"),
       ("②", "__init__(빈 붕어빵, ...)", "빈 붕어빵이 self로 들어가요"),
       ("③", 'self.flavor = "팥"', "맛 칸을 붙여요"),
       ("④", "self.price = 1000", "가격 칸을 붙여요"),
       ("⑤", "a = 다 된 붕어빵", "끝나면 a에 담아요")]
o.append(f'<div style="position:absolute;left:122px;top:250px;width:4px;height:600px;background:{K3BG}"></div>')
for i, (n_, code, what) in enumerate(ST5):
    o.append(f'<div id="stp-{i + 1}" data-build-in="rise order {i + 1}"{DIM("st")} style="position:absolute;left:96px;top:{220 + i * 146}px;width:1100px;height:130px;display:flex;flex-direction:row;align-items:center;gap:26px">'
             + p(f"width:56px;height:56px;flex:none;border-radius:50%;background:{K3};color:#FFFFFF;font-size:30px;font-weight:900;line-height:56px;text-align:center", str(i + 1))
             + '<div style="display:flex;flex-direction:column;gap:4px">' + p(f"font-family:{MONO};font-size:36px;font-weight:700;color:{INK};white-space:pre", e(code))
             + p(f"font-size:28px;color:{SUB}", e(what)) + '</div></div>')
o.append(obj("빈 붕어빵", [], 1260, 230, 564, cls="", empty="아직 칸이 없어요", rh=68, attrs=' data-build-in="rise order 1"'))
o.append(obj("self", [("flavor", '"팥"')], 1260, 230, 564, cls="", rh=68, fs=32, attrs=' data-build-in="fly order 3" data-from="stp-3"'))
o.append(obj("self", [("flavor", '"팥"'), ("price", "1000")], 1260, 230, 564, cls="", rh=68, fs=32, attrs=' data-build-in="fly order 4" data-from="stp-4"'))
o.append(obj("a", [("flavor", '"팥"'), ("price", "1000")], 1260, 230, 564, cls="", rh=68, fs=32, attrs=' data-build-in="fly order 5" data-from="stp-5"'))
o.append(p(f"position:absolute;left:1260px;top:540px;width:564px;font-size:30px;font-weight:700;line-height:1.5;word-break:keep-all;color:{K3}", "②~④에서 self는 이 붕어빵이에요. ⑤에서 a라는 이름이 붙어요.", ' data-build-in="fade order 6"'))
W("s-steps", o, "찍는 한 줄 안에서 빈 붕어빵이 생기고, self로 칸이 붙고, 마지막에 a에 담겨요. a = Bread(팥, 1000) 한 줄을 다섯 단계로 나눠 봐요. 먼저 빈 붕어빵이 하나 생겨요. 파이썬이 그 빈 붕어빵을 self 칸에, 팥과 1000을 나머지 칸에 넣어 __init__을 불러요. __init__ 안에서 self에 맛 칸과 가격 칸이 붙어요. 오른쪽 그림에서 칸이 하나씩 늘어나는 걸 봐요. __init__이 끝나면 다 된 붕어빵이 등호 왼쪽의 a에 담겨요. 12에서 배운 대로 오른쪽을 먼저 끝내고 왼쪽 변수에 담는 순서예요.")

# ---------- 붕어빵 기계 (positions are fixed by lab_stamp.js; only the help line loses its card) ----------
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
o.append('<div style="position:absolute;left:96px;top:196px;width:820px;height:224px;display:flex;flex-direction:column;gap:18px;padding:26px 0">'
         + lab_btns("lb-flavors", "맛", ["팥", "슈크림", "피자", "고구마"], "팥") + lab_btns("lb-prices", "가격", ["1000", "1200", "1500"], "1000") + '</div>')
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
o.append(f'<div style="position:absolute;left:960px;top:680px;width:864px;height:222px;border-top:3px solid {LINE};padding:18px 0;display:flex;flex-direction:column;gap:14px">'
         + '<div style="display:flex;flex-direction:row;gap:14px;align-items:center">' + p(f"font-size:24px;font-weight:700;color:{BR}", "찍은 붕어빵") + p(f"font-size:24px;font-weight:700;color:{GRAY}", "", ' id="lb-count"') + '</div>'
         + f'<div id="lb-tray" style="display:flex;flex-direction:row;gap:16px;align-items:center;height:124px">{p(f"font-size:24px;color:{GRAY}", "아직 없어요. 찍으면 여기에 쌓여요.")}</div></div>')
o.append(f'<div style="position:absolute;left:96px;top:940px;width:1728px;height:96px;display:flex;align-items:center">'
         + p(f"font-size:32px;font-weight:500;line-height:1.4;color:{INK}", "맛과 가격을 고르고 <b>한 단계씩</b>이나 <b>한 번에 찍기</b>를 눌러요. 브라우저로 슬라이드를 열면 눌러져요.", ' id="lb-msg"') + '</div>')
o.append(cursor(1, target="lb-next"))
o.append(cursor_off(2))
with open(os.path.join(HERE, "lab_stamp.js")) as f:
    o.append('<script type="text/slide-js">\n' + f.read() + '</script>')
W("s-lab", o, "버튼을 눌러 다섯 단계를 직접 따라가요. 앞 장의 다섯 단계를 직접 눌러 보는 장이에요. 브라우저로 슬라이드를 열면 버튼이 눌러져요. 맛과 가격을 고르고 한 단계씩을 누르면 왼쪽 코드에서 지금 실행하는 줄에 불이 들어와요. 오른쪽에서는 빈 붕어빵이 생기고, self가 그 붕어빵을 가리키고, 맛 칸과 가격 칸이 하나씩 붙어요. __init__이 끝나면 재료 칸은 사라지고 붕어빵에 a라는 이름이 붙어요. 한 번 더 찍으면 이번엔 b가 만들어지고 self는 새 붕어빵을 가리켜요. 수강생에게 다음 단계에서 무엇이 바뀔지 먼저 물어보고 눌러 봐요.")

o = [sec("s-lr")] + head(EB3, "self.flavor = flavor는 왼쪽과 오른쪽이 달라요", K3)
o.append(code_box(96, 230, 1728, [[("self.flavor", CS), (" = ", W_), ("flavor", CA)]], ' data-build-in="rise order 1"', 72, 190, "24px 80px"))
o.append(harrow(330, 470, 80, BR, ' data-build-in="fade order 2"', 90))
o.append(harrow(1050, 470, 80, TEAL, ' data-build-in="fade order 3"', 90))
o.append(obj("a", [("flavor", '"팥"')], 96, 560, 620, cls="", rh=72, fs=34, attrs=' data-build-in="rise order 2"'))
o.append(tag(96, 790, "붕어빵에 붙는 칸. 계속 남아서 a.flavor로 꺼내요", BR, 2, 30, False))
o.append(p(f"position:absolute;left:820px;top:580px;height:90px;border-radius:18px;border:3px dashed {TEAL};background:{K3BG};padding:0 30px;font-family:{MONO};font-size:36px;font-weight:700;line-height:84px;color:{INK}", 'flavor = "팥"', ' data-build-in="rise order 3"'))
o.append(tag(820, 790, "들고 온 재료. __init__이 끝나면 사라져요 (20의 지역 변수)", TEAL, 3, 30, False))
o.append(caption2("이름이 같아서 헷갈리면 self.이 붙었는지만 봐요.", 960, 4))
W("s-lr", o, "self.flavor는 붕어빵에 남는 칸, 오른쪽 flavor는 끝나면 사라지는 재료예요. 가장 헷갈리는 줄을 색으로 나눠 봐요. 왼쪽 self.flavor는 붕어빵에 붙는 칸이에요. 붕어빵이 있는 동안 계속 남아서 나중에 a.flavor로 꺼낼 수 있어요. 오른쪽 flavor는 찍을 때 괄호로 들어온 재료예요. __init__의 매개변수라서 20에서 배운 지역 변수처럼 __init__이 끝나면 사라져요. 그래서 사라지기 전에 붕어빵 칸에 옮겨 담는 줄이 self.flavor = flavor예요. 이름이 같아서 헷갈리면 self.이 붙었는지만 봐요. 보통은 알아보기 쉽게 같은 이름을 써요.")

o = [sec("s-noself")] + head(EB3, "self.를 빼면 재료가 붕어빵에 안 붙어요", K3)
NS = ["class Bread:", "    def __init__(self, flavor, price):", "        flavor = flavor", "        price = price", "", 'a = Bread("팥", 1000)', "print(a.flavor)"]
T1 = 220
o += cell({"id": "c-s4", "lines": NS, "n": 4, "out": ["AttributeError: 'Bread' object has no attribute 'flavor'"], "err": True}, 96, T1, 1100, sel="c-s4")
o.append(mk(96, T1, 1100, 2, 2, "err", 1)); o.append(tag(tx(96, ["        flavor = flavor"]), ly(T1, 2.5), "자기 자신에 다시 넣었을 뿐", RED, 1))
o.append(obj("a", [], 1300, 220, 524, cls="", empty="붙은 칸이 없어요", rh=90, attrs=' data-build-in="rise order 2"'))
o.append(out_ul(2, 96, T1, 7, 0, "AttributeError: 'Bread' object ", "has no attribute 'flavor'"))
o.append(fix(96, 680, "flavor = flavor", "self.flavor = flavor", 3, 34, good_html=f'<span{MARK(4)} style="background:#FFE58A;border-radius:6px">self.</span>flavor = flavor'))
o.append(caption2("붕어빵에 남길 값은 꼭 self.이름 = 값으로 적어요.", 820, 4))
W("s-noself", o, "self.를 빼면 값이 붕어빵에 붙지 않아서 AttributeError가 나요. flavor = flavor는 들어온 재료를 자기 자신에게 다시 넣었을 뿐이에요. 붕어빵에는 아무 칸도 붙지 않았어요. 그래서 a.flavor를 꺼내면 그런 속성이 없다는 AttributeError가 나요. 20에서 함수 안에서 만든 변수는 함수가 끝나면 사라진다고 배웠어요. __init__도 함수라서 똑같아요. 붕어빵에 남기려면 꼭 self.이름 = 값으로 적어요." + REAL)

o = [sec("s-start")] + head(EB3, "재료로 받지 않는 칸도 만들 수 있어요", K3)
SS = B_INIT + ["        self.baked = False", "", 'a = Bread("팥", 1000)', "print(a.flavor, a.price, a.baked)"]
T1 = 250
o += cell({"id": "c-s5", "lines": SS, "n": 5, "out": ["팥 1000 False"]}, 96, T1, 1100, sel="c-s5")
o.append(code_ul(1, 96, T1, 4, "        ", "self.baked = False", GR)); o.append(tag(tx(96, ["        self.baked = False"]), ly(T1, 4), "괄호로 받지 않고 처음부터 False", GR, 1))
o.append(obj("a", [("flavor", '"팥"'), ("price", "1000"), ("baked", "False")], 1300, 250, 524, cls="", rh=68, fs=32, attrs=' data-build-in="rise order 2"'))
o.append(caption2("도장 0개, 판매 0개처럼 모두 같은 값으로 시작하는 칸에 써요.", 800, 3))
W("s-start", o, "재료로 받지 않고 처음 값을 정해 둔 칸도 만들 수 있어요. baked 칸은 괄호로 받지 않고 처음부터 False로 정했어요. 찍은 붕어빵은 모두 아직 안 구운 상태로 시작해요. 도장 카드의 도장 개수, 가게의 판매 개수처럼 처음엔 모두 같은 값으로 시작하는 칸에 써요. 6파트의 도장 카드 실습에서 이 모양을 다시 써요." + REAL)

# ---------- part 4 ----------
o = [sec("f-method")] + head(EB4, "틀 안의 함수가 메서드예요", K4)
FM = B_INIT + [""] + B_INTRO + ["", 'a = Bread("팥", 1000)', 'b = Bread("슈크림", 1200)', "a.intro()", "b.intro()"]
T1 = 210
o += cell({"id": "c-f1", "lines": FM, "n": 1, "out": ["팥 붕어빵 1000 원", "슈크림 붕어빵 1200 원"]}, 96, T1, FW, sel="c-f1")
o.append(mk(96, T1, FW, 5, 2, "mark", 1)); o.append(tag(TX, ly(T1, 5), "메서드. 첫 칸은 self", K4, 1))
o.append(tag(TX, ly(T1, 6), "그 붕어빵의 맛과 가격", BR, 2))
o.append(rb(3, 96, T1, FW, 10, 2)); o.append(tag(TX, ly(T1, 10.5), "붕어빵에게 시켜요", GR, 3))
o.append(run_off(4))
o.append(caption2("intro(b1)처럼 넘기지 않고 a.intro()로 시켜요.", 960, 4))
W("f-method", o, "틀 안의 함수가 메서드이고, a.intro()처럼 붕어빵에게 시켜요. __init__ 아래에 def intro를 같은 깊이로 들여 썼어요. 틀 안에 있는 함수를 메서드라고 불러요. 메서드의 첫 칸도 self예요. 그래서 안에서 self.flavor, self.price로 그 붕어빵의 값을 꺼낼 수 있어요. 부를 때는 a.intro()처럼 붕어빵 이름 뒤에 점을 찍어요. 1파트에서는 intro(b1)처럼 딕셔너리를 함수에 넘겼는데, 이제는 붕어빵에게 직접 시켜요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p4", "메서드"))

o = [sec("f-same")] + head(EB4, "a.intro()는 Bread.intro(a)와 같아요", K4)
o.append(code_box(96, 270, 760, [[("a", CS), (".intro()", W_)]], ' id="fs-short" data-build-in="rise order 1"', 64, 170))
o.append(harrow(890, 340, 150, K4, ' data-build-in="fade order 2"'))
o.append(code_box(1074, 270, 750, [[("Bread.intro(", W_), ("a", CS), (")", W_)]], ' data-build-in="fly order 2" data-from="fs-short"', 64, 170))
o.append(tag(1074, 490, "점 앞의 a가 self 칸으로 들어가요", BR, 3, 30, False))
T1 = 620
o += cell({"id": "c-f2", "lines": ["Bread.intro(a)", "Bread.intro(b)"], "n": 2, "out": ["팥 붕어빵 1000 원", "슈크림 붕어빵 1200 원"], "attrs": ' data-build-in="rise order 4"'}, 96, T1, 900, sel="c-f2")
o.append(tag(tx(96, ["슈크림 붕어빵 1200 원"], out=True), oy(T1, 2, 0.5), "a.intro(), b.intro()와 똑같아요", GRAY, 4))
W("f-same", o, "a.intro()를 부르면 점 앞의 a가 self 칸에 들어가요. def intro(self)에는 칸이 하나 있는데, a.intro()의 괄호는 비어 있어요. 그 칸에는 무엇이 들어갈까요? 점 앞의 a예요. 파이썬은 a.intro()를 Bread 틀의 intro에 a를 넣어 부르는 것으로 바꿔서 실행해요. 실제로 Bread.intro(a)라고 쳐도 결과가 똑같아요. 평소에는 짧은 a.intro()를 써요. self는 메서드를 부른 그 붕어빵, __init__에서는 방금 찍은 그 붕어빵이에요." + REAL)

o = [sec("f-change")] + head(EB4, "메서드로 값을 바꾸고, return으로 돌려받아요", K4)
FC = B_INIT + ["", "    def discount(self, won):", "        self.price = self.price - won", "", "    def total(self, qty):", "        return self.price * qty", "", 'a = Bread("팥", 1000)', 'b = Bread("슈크림", 1200)', "a.discount(200)", "print(a.price, b.price)", "print(a.total(3))"]
T1 = 200
o += cell({"id": "c-f3", "lines": FC, "n": 3, "out": ["800 1200", "2400"]}, 96, T1, 1100, sel="c-f3")
o.append(lsp(1, 96, T1, 1100, len(FC), 5, 2, BL)); o.append(tag(tx(96, ["        self.price = self.price - won"]), ly(T1, 5.5), "값 바꾸기", BL, 1))
o.append(lsp(2, 96, T1, 1100, len(FC), 8, 2, GR)); o.append(tag(tx(96, ["        self.price = self.price - won"]), ly(T1, 8.5), "돌려주기", GR, 2))
o.append(lspot_off(3))
o.append(obj("a", [("flavor", '"팥"'), ("price", "800")], 1300, 200, 524, cls="", rh=68, fs=32, attrs=' data-build-in="rise order 3"', vids={"price": ("fc-ap", "1000")}))
o.append(obj("b", [("flavor", '"슈크림"'), ("price", "1200")], 1300, 480, 524, cls="", rh=68, fs=32, attrs=' data-build-in="rise order 3"'))
o.append(mk(96, T1, 1100, 13, 1, "mark", 4))
o.append(text(4, "fc-ap", "800"))
o.append(tag(1300, 770, "a.discount(200)의 self는 a. b는 그대로예요", K4, 5, 28, False))
W("f-change", o, "메서드는 self.price처럼 자기 칸을 바꿀 수도 있고, return으로 값을 돌려줄 수도 있어요. 메서드에도 self 뒤에 매개변수를 더 둘 수 있어요. discount는 깎을 금액을 받아서 자기 가격에서 빼요. a.discount(200)을 부르면 self는 a라서 a의 가격만 800원이 되고 b는 1200원 그대로예요. 붕어빵마다 칸이 따로 있다는 게 이거예요. total은 개수를 받아 가격을 곱한 값을 return해요. 19에서 배운 대로 return한 값은 print로 찍거나 변수에 담아 써요." + REAL)

o = [sec("f-compare")] + head(EB4, "클래스는 재료를 빠뜨리면 찍을 때 바로 알려 줘요", K4)
CW = [330, 660, 660]
o += plain_rows(96, 220, 1728, [["모양", 'b1 = {"flavor": "팥", ...}', 'a = Bread("팥", 1000)'],
                                ["할 일", "intro(b1)", "a.intro()"],
                                ["할 일은 어디에", "함수가 밖에 따로", "틀 안에 같이"],
                                ["값 꺼내기", 'b1["flavor"]', "a.flavor"],
                                ["재료를 빠뜨리면", "쓸 때 KeyError", "찍을 때 바로 TypeError"],
                                ["어울리는 곳", "잠깐 담아 두는 값", "같은 모양을 여러 개 찍을 때"]], CW, 1, 104, ["", "딕셔너리와 함수 (1파트)", "클래스"], 30, rid="fc-r", same=True)
o.append(spot(2, target="fc-r2", pad=6, r=12, dim=0.5))
o.append(spot(3, target="fc-r4", pad=6, r=12, dim=0.5))
o.append(spot_off(4))
W("f-compare", o, "클래스는 값과 할 일을 한 틀에 두고, 재료가 모자라면 찍는 순간 알려 줘요. 1파트의 딕셔너리 방식과 비교해요. 딕셔너리는 값만 담고 할 일은 밖의 함수가 해요. 클래스는 값과 할 일이 한 틀에 같이 있어요. 값을 꺼낼 때는 대괄호와 따옴표 대신 점을 써요. 가장 큰 차이는 재료를 빠뜨렸을 때예요. 딕셔너리는 나중에 쓸 때 KeyError가 나지만, 클래스는 찍는 순간 재료가 모자라다고 알려 줘요. 잠깐 값을 담아 둘 때는 딕셔너리가 편하고, 같은 모양을 여러 개 찍어 쓸 때는 클래스가 좋아요.")

# ---------- part 5: the error line, one reading tag, the fix ----------
o = [sec("t-missing")] + head(EB5, "재료 수가 모자라면 missing argument", K5)
TM = B_INIT + ["", "    def intro():", '        print("붕어빵")', "", 'a = Bread("팥")']
T1 = 210
o += cell({"id": "c-t1", "lines": TM, "n": 1, "out": ["TypeError: Bread.__init__() missing 1 required positional argument: 'price'"], "err": True}, 96, T1, 1728, sel="c-t1")
o.append(mk(96, T1, 1728, 8, 1, "err", 1)); o.append(shake(1, "c-t1")); o.append(tag(tx(96, ['a = Bread("팥")']), ly(T1, 8), "재료가 하나뿐", RED, 1))
o.append(out_ul(2, 96, T1, 9, 0, "TypeError: Bread.__init__() ", "missing 1 required positional argument: 'price'"))
o.append(tag(96, 740, "읽는 법: __init__에 꼭 필요한 칸 price가 1개 모자라요", RED, 2, 32, False))
o.append(fix(96, 820, 'a = Bread("팥")', 'a = Bread("팥", 1000)', 3, 34))
o.append(caption2("self는 파이썬이 채우니까, self를 뺀 칸 수만큼 재료를 넣어요.", 960, 4))
W("t-missing", o, "missing argument는 찍을 때 재료가 모자라다는 뜻이에요. 붕어빵을 찍을 때 맛만 넣고 가격을 빠뜨렸어요. __init__에 꼭 필요한 칸 price가 하나 모자라다는 TypeError예요. self는 파이썬이 채우니까 self를 뺀 칸 수만큼 재료를 넣으면 돼요. 1파트의 딕셔너리는 나중에 쓸 때 오류가 났지만, 클래스는 찍는 순간 알려 줘요. 틀 안의 intro에는 일부러 실수를 넣어 뒀어요. 다음 장에서 봐요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p5", "오류와 함정"))

o = [sec("t-noself")] + head(EB5, "메서드에 self를 빼면 takes 0 positional arguments", K5)
o.append(side(96, 210, 900, 190, "앞 셀의 틀 일부", ["    def intro():", '        print("붕어빵")'], [], RED, "#F8E6E6", fs=28, dashed=True))
T1 = 440
o += cell({"id": "c-t2", "lines": ['a = Bread("팥", 1000)', "a.intro()"], "n": 2, "out": ["TypeError: Bread.intro() takes 0 positional arguments but 1 was given"], "err": True}, 96, T1, 1728, sel="c-t2")
o.append(out_ul(1, 96, T1, 2, 0, "TypeError: Bread.intro() ", "takes 0 positional arguments but 1 was given"))
o.append(tag(96, 650, "읽는 법: 받을 칸은 0개인데 점 앞의 a가 1개 들어왔어요", RED, 1, 32, False))
o.append(underline(2, 196, 398, 325, RED))
o.append(fix(96, 740, "def intro():", "def intro(self):", 3, 34, good_html=f'def intro(<span{MARK(4)} style="background:#FFE58A;border-radius:6px">self</span>):'))
o.append(caption2("a.intro()는 Bread.intro(a)라서 a가 하나 들어가요.", 960, 4))
W("t-noself", o, "메서드의 첫 칸 self를 빼면 a.intro()를 부를 때 TypeError가 나요. intro를 만들 때 self를 빼먹었어요. a.intro()를 부르면 받을 칸이 0개인데 1개가 들어왔다는 TypeError가 나요. 괄호를 비웠는데 왜 1개일까요? 4파트에서 본 것처럼 a.intro()는 Bread.intro(a)로 바뀌어서 a가 하나 들어가요. 메서드를 만들 때는 쓰지 않더라도 첫 칸에 self를 꼭 적어요." + REAL)

o = [sec("t-init")] + head(EB5, "밑줄을 하나만 적으면 takes no arguments", K5)
TI = ["class Bread:", "    def _init_(self, flavor, price):", "        self.flavor = flavor", "        self.price = price", "", 'a = Bread("팥", 1000)']
T1 = 210
o += cell({"id": "c-t4", "lines": TI, "n": 3, "out": ["TypeError: Bread() takes no arguments"], "err": True}, 96, T1, 1728, sel="c-t4")
o.append(code_box_mark(1, 96, T1, 1, "    def ", "_init_")); o.append(tag(tx(96, ["    def _init_(self, flavor, price):"]), ly(T1, 1), "밑줄이 하나씩", RED, 1))
o.append(tag(96, 630, "읽는 법: 약속된 이름 __init__을 못 찾아서, 재료를 받지 않는 틀이 됐어요", RED, 2, 32, False))
o.append(fix(96, 710, "def _init_(self, ...)", "def __init__(self, ...)", 3, 34, good_html=f'def _<span{MARK(4)} style="background:#FFE58A;border-radius:4px">_</span>init_<span{MARK(4)} style="background:#FFE58A;border-radius:4px">_</span>(self, ...)'))
o.append(caption2("__int__처럼 글자가 빠져도 같은 오류가 나요.", 880, 4))
W("t-init", o, "takes no arguments가 나면 __init__ 이름부터 봐요. __init__의 밑줄을 하나씩만 적었어요. 파이썬은 앞뒤 밑줄 두 개짜리 __init__이라는 이름만 찾아요. 이름이 다르면 그냥 평범한 메서드라서 찍을 때 불리지 않아요. 그래서 Bread 틀은 재료를 받지 않는다는 TypeError가 나요. 밑줄이 두 개인지, init 글자가 맞는지 확인해요. VS Code에서는 밑줄 두 개가 붙어 보여서 놓치기 쉬워요." + REAL)

o = [sec("t-print")] + head(EB5, "붕어빵을 print하면 이상한 글자가 나와요", K5)
TP = B_INIT + ["", 'a = Bread("팥", 1000)', "print(a)"]
T1 = 210
o += cell({"id": "c-t5", "lines": TP, "n": 4, "out": ["<__main__.Bread object at 0x7f440c2dbb60>"]}, 96, T1, 1100, sel="c-t5")
o.append(tag(tx(96, ["<__main__.Bread object at 0x7f440c2dbb60>"], out=True), oy(T1, 7, 0), "오류는 아니에요", K5, 1))
segs = [("<", W_, None), ("__main__.Bread", "#D9C2A8", "이 노트북의 Bread 틀의"), (" ", W_, None), ("object", CS, "객체(붕어빵)"), (" ", W_, None), ("at 0x7f440c2dbb60", "#9AA1AE", "컴퓨터 안의 자리. 실행마다 달라요"), (">", W_, None)]
o.append(code_box(96, 640, 1728, [[(t, c) for t, c, _ in segs]], "", 40, 120))
for i, (x, txt, c) in enumerate([(154, "이 노트북의 Bread 틀의", MD), (514, "객체(붕어빵)", BR), (756, "컴퓨터 안의 자리. 실행할 때마다 달라요", GRAY)]):
    o.append(f'<div data-build-in="fade order {2 + i}" style="position:absolute;left:{x}px;top:774px;width:6px;height:44px;background:{c};border-radius:3px"></div>')
    o.append(p(f"position:absolute;left:{x}px;top:826px;font-size:30px;font-weight:700;color:{c};white-space:nowrap", e(txt), f' data-build-in="fade order {2 + i}"'))
o.append(caption2("지금은 a.flavor처럼 칸을 꺼내 찍고, 25의 __str__로 보기 좋게 바꿔요.", 940, 5))
W("t-print", o, "붕어빵을 통째로 print하면 오류는 아니지만 알아보기 힘든 글자가 나와요. 지금 노트북에서 만든 Bread 틀의 객체이고, 컴퓨터 안의 어느 자리에 있다는 뜻이에요. 0x로 시작하는 주소는 실행할 때마다 달라서 내 화면과 슬라이드가 달라도 괜찮아요. 파이썬은 우리가 만든 붕어빵을 글자로 어떻게 보여 줄지 몰라요. 지금은 a.flavor처럼 칸을 꺼내 찍고, 다음 챕터에서 __str__로 보기 좋게 바꿔요." + REAL)

# ---------- part 6 ----------
o = [sec("x-order")] + head(EB6, "붕어빵 가게: 주문 받은 붕어빵을 소개하고 합계 내기", K6)
XO = B_INIT + [""] + B_INTRO + ["", 'order = [Bread("팥", 1000), Bread("슈크림", 1200), Bread("팥", 1000)]', "for b in order:", "    b.intro()", "total = sum([b.price for b in order])", 'print("합계", total, "원")']
T1 = 200
CFS[0] = 28
o += [re.sub(r'<p( style="[^"]*">합계 3200 원</p>)', lambda m: "<p" + COUNT(4) + m.group(1), x) for x in cell({"id": "c-x1", "lines": XO, "n": 1, "out": ["팥 붕어빵 1000 원", "슈크림 붕어빵 1200 원", "팥 붕어빵 1000 원", "합계 3200 원"]}, 96, T1, 1340, sel="c-x1")]
o.append(rb(1, 96, T1, 1340, 8)); o.append(tag(1460, ly(T1, 8), "객체도 리스트에", BL, 1))
o.append(rb(2, 96, T1, 1340, 9, 2)); o.append(tag(1460, ly(T1, 9.5), "하나씩 소개", GR, 2))
o.append(rb(3, 96, T1, 1340, 11)); o.append(run_off(4)); o.append(tag(1460, ly(T1, 11), "23의 컴프리헨션", BL, 3))
o.append(tag(tx(96, ["슈크림 붕어빵 1200 원"], out=True), oy(T1, 13, 3), "b.price만 모아 더했어요", K6, 4))
CFS[0] = 30
W("x-order", o, "객체도 리스트에 담고 for로 하나씩 꺼내 쓸 수 있어요. 배운 것을 섞어 붕어빵 가게 주문을 처리해요. 손님이 주문한 붕어빵 세 개를 찍어서 바로 리스트에 담았어요. 객체도 숫자나 글자처럼 값이라 리스트에 담을 수 있어요. for로 하나씩 꺼내 b.intro()를 부르면 붕어빵마다 자기 맛과 가격으로 소개해요. 합계는 23의 컴프리헨션으로 b.price만 모아 sum에 넘겼어요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p6", "실습"))

o = [sec("x-drink")] + head(EB6, "카페 음료: 기본값 사이즈와 메뉴 이름표 만들기", K6)
XD = ["class Drink:", '    def __init__(self, name, price, size="M"):', "        self.name = name", "        self.price = price", "        self.size = size", "", "    def label(self):", '        return f"{self.name}({self.size}) {self.price:,}원"', "", 'd1 = Drink("latte", 5000)', 'd2 = Drink("tea", 4000, "L")', "print(d1.label())", "print(d2.label())"]
T1 = 200
o += cell({"id": "c-x2", "lines": XD, "n": 2, "out": ["latte(M) 5,000원", "tea(L) 4,000원"]}, 96, T1, 1300, sel="c-x2")
o.append(lsp(1, 96, T1, 1300, len(XD), 1, 1, BL)); o.append(tag(tx(96, ['    def __init__(self, name, price, size="M"):']), ly(T1, 1), "20의 기본값", BL, 1))
o.append(lsp(2, 96, T1, 1300, len(XD), 6, 2, GR)); o.append(lspot_off(3)); o.append(tag(tx(96, ["    def label(self):"]), ly(T1, 6), "글자를 돌려줘요", GR, 2))
o.append(obj("d1", [("name", '"latte"'), ("price", "5000"), ("size", '"M"')], 1440, 200, 384, cls="", fs=26, rh=54, attrs=' data-build-in="rise order 3"'))
o.append(obj("d2", [("name", '"tea"'), ("price", "4000"), ("size", '"L"')], 1440, 500, 384, cls="", fs=26, rh=54, attrs=' data-build-in="rise order 4"'))
o.append(tag(1440, 820, "size를 안 넣으면 \"M\"", BL, 4, 26, False))
W("x-drink", o, "__init__에도 기본값을 쓸 수 있고, 메서드는 글자를 return해 돌려줄 수 있어요. 카페 음료 틀을 만들어요. __init__에도 20에서 배운 기본값을 쓸 수 있어요. 사이즈를 안 넣으면 M이 들어가요. label 메서드는 13의 f-string과 천 단위 콤마로 메뉴 이름표 글자를 만들어 return해요. 메서드 안에서 print하지 않고 글자를 돌려주면, 밖에서 찍을 수도 있고 영수증이나 메뉴판에 다시 쓸 수도 있어요. 19에서 본 print와 return의 차이와 같아요." + REAL)

o = [sec("x-card")] + head(EB6, "도장 카드: 처음 0개에서 손님마다 따로 쌓기", K6)
XC = ["class Card:", "    def __init__(self, name):", "        self.name = name", "        self.stamps = 0", "", "    def add(self):", "        self.stamps = self.stamps + 1", "", 'kim = Card("kim")', 'lee = Card("lee")', "kim.add()", "kim.add()", "kim.add()", "lee.add()", "print(kim.name, kim.stamps)", "print(lee.name, lee.stamps)"]
T1 = 200
CFS[0] = 28
o += cell({"id": "c-x3", "lines": XC, "n": 3, "out": ["kim 3", "lee 1"]}, 96, T1, 1100, sel="c-x3")
o.append(mk(96, T1, 1100, 3, 1, "mark", 1)); o.append(tag(tx(96, ["        self.stamps = self.stamps + 1"]), ly(T1, 3), "처음 값 0", BL, 1))
o.append(mk(96, T1, 1100, 6, 1, "run", 2)); o.append(tag(tx(96, ["        self.stamps = self.stamps + 1"]), ly(T1, 6), "자기 도장 +1", GR, 2))
o.append(obj("kim", [("name", '"kim"'), ("stamps", "3")], 1300, 200, 524, cls="", color=BL, bg=K1BG, rh=68, fs=32, attrs=' data-build-in="rise order 2"' + DELAY(150), vids={"stamps": ("xc-k", "0")}))
o.append(obj("lee", [("name", '"lee"'), ("stamps", "1")], 1300, 480, 524, cls="", color=GR, bg="#E6F4EC", rh=68, fs=32, attrs=' data-build-in="rise order 2"' + DELAY(300), vids={"stamps": ("xc-l", "0")}))
o.append(rb(3, 96, T1, 1100, 10, 3)); o.append(text(3, "xc-k", "3"))
o.append(rb(4, 96, T1, 1100, 13)); o.append(text(4, "xc-l", "1"))
o.append(run_off(5))
o.append(tag(1300, 770, "같은 틀, 카드마다 칸이 따로", K6, 5, 28, False))
CFS[0] = 30
W("x-card", o, "같은 틀로 찍어도 카드마다 칸이 따로라서 도장이 섞이지 않아요. 카페 도장 카드를 만들어요. 3파트에서 본 것처럼 stamps 칸은 재료로 받지 않고 0에서 시작해요. add 메서드는 자기 도장을 하나 늘려요. kim.add()를 세 번 부르면 self는 매번 kim이라서 kim의 도장만 3개가 돼요. lee는 따로 1개예요. 같은 틀로 찍었지만 카드마다 칸이 따로 있어서 서로 섞이지 않아요. 26에서 이 카드에 가게 이름처럼 모두가 같이 쓰는 값을 더해요." + REAL)

# ---------- wrap up ----------
o = [sec("trouble")] + head("정리", "막히면 오류의 마지막 줄을 봐요", RED)
TR = [("TypeError: ... missing 1 required positional argument", "찍을 때 재료가 모자라요", "self 뒤 칸 수만큼"),
      ("TypeError: ... takes 0 positional arguments but 1 was given", "메서드에 self가 없어요", "def intro(self):"),
      ("TypeError: Bread() takes no arguments", "__init__ 이름이 틀렸어요", "밑줄 두 개씩"),
      ("AttributeError: 'Bread' object has no attribute ...", "칸 이름 오타이거나 self.를 뺐어요", "self.이름 = 값"),
      ("NameError: name 'flavor' is not defined", "메서드 안에서 flavor만 썼어요", "self.flavor"),
      ("<__main__.Bread object at 0x...>", "붕어빵을 통째로 print했어요", "a.flavor, 25의 __str__"),
      ("TypeError: ... missing 1 required positional argument: 'self'", "a = Bread처럼 괄호 없이 담았어요", "Bread(재료)")]
for i, (q, a_, cmd) in enumerate(TR):
    o.append(f'<div data-build-in="rise order {min(i + 1, 6)}" style="position:absolute;left:96px;top:{206 + i * 104}px;width:1728px;height:104px;display:flex;flex-direction:row;align-items:center;gap:26px;border-bottom:2px solid {LINE}">'
             + '<div style="flex:1;display:flex;flex-direction:column;gap:4px">' + p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{RED};white-space:nowrap", e(q)) + p(f"font-size:26px;color:{INK}", e(a_)) + '</div>'
             + p(f"width:400px;flex:none;{'font-family:' + MONO + ';' if cmd.isascii() else ''}font-size:28px;font-weight:700;color:{GR};white-space:pre", f'<span style="font-family:{SANS}">✓</span> ' + e(cmd)) + '</div>')
o.append(caption2("헷갈리면 self 자리에 붕어빵 이름(a)을 넣어 소리 내어 읽어 봐요.", 960))
W("trouble", o, "막히면 오류의 마지막 줄을 읽고 이 표에서 찾아요. 이번 챕터에서 자주 만나는 일을 모았어요. 1번부터 3번은 칸 수와 이름이 안 맞을 때 나는 TypeError예요. 4번은 칸 이름을 틀렸거나 __init__에서 self.를 빼먹었을 때 나요. 5번은 메서드 안에서 자기 값을 꺼낼 때 self.를 빼먹으면 나요. __init__의 재료 flavor는 __init__이 끝나면 사라졌기 때문이에요. 6번은 오류가 아니라 25에서 해결해요. 7번처럼 괄호 없이 a = Bread라고 적으면 붕어빵이 아니라 틀 자체가 담겨요. 그래서 a.intro()를 부르면 self에 넣을 붕어빵이 없다는 오류가 나요. 막히면 self 자리에 a를 넣어 a.flavor = 팥처럼 소리 내어 읽어 봐요.", ("trouble", "정리"))

o = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>']
CH = [("class Bread:", "틀 만들기", MD), ('Bread("팥", 1000)', "붕어빵 찍기", BR), ("def __init__(self, ...):", "찍을 때 재료 넣기", K3), ("self.flavor = flavor", "붕어빵에 칸 붙이기", K3),
      ("self", "지금 그 붕어빵", BR), ("def intro(self):", "메서드 만들기", K4), ("a.intro()", "Bread.intro(a)와 같아요", K4), ("a.flavor", "속성 꺼내기", K2)]
for i, (k, d, c) in enumerate(CH):
    x, y = 96 + (i // 4) * 884, 210 + (i % 4) * 150
    o.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:844px;height:130px;display:flex;flex-direction:column;justify-content:center;gap:6px;border-bottom:2px solid {LINE}">'
             + p(f"font-family:{MONO};font-size:38px;font-weight:700;color:{c};white-space:pre", e(k)) + p(f"font-size:30px;color:{SUB}", e(d)) + '</div>')
o.append(p(f"position:absolute;left:96px;top:850px;width:1728px;font-size:34px;font-weight:700;line-height:1.5;color:{INK}", "self는 \"방금 찍은 붕어빵\", \"메서드를 부른 붕어빵\"이에요.<br>" + f'<span style="color:{GRAY}">다음: 25에서 __str__, __repr__로 붕어빵을 보기 좋게 찍어요.</span>'))
W("cheatsheet", o, "self는 방금 찍은 붕어빵, 또는 메서드를 부른 붕어빵이에요. 이번 챕터에서 쓴 모양을 한 장에 모았어요. class로 틀을 만들고, 틀 이름 뒤에 괄호와 재료를 넣어 붕어빵을 찍어요. __init__은 찍을 때 저절로 불려서 self.이름 = 값으로 붕어빵에 칸을 붙여요. self는 __init__에서는 방금 찍은 붕어빵, 메서드에서는 그 메서드를 부른 붕어빵이에요. 25에서는 print했을 때 이상한 글자 대신 보기 좋은 글자가 나오게 만들어요.")

# ---------- toc: number, icon and title only ----------
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
parts_ = [("Lightbulb", K1, "왜 필요한가", "c-why", "c-type"), ("Archive", K2, "가장 작은 틀", "m-empty", "m-tedious"), ("Code", K3, "self와 __init__", "s-func", "s-start"),
          ("Settings", K4, "메서드", "f-method", "f-compare"), ("Warning", K5, "오류와 함정", "t-missing", "t-print"), ("Star", K6, "실습", "x-order", "x-card")]
t = [f'<section id="toc" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>']
for i, (ic, c, h, a, b) in enumerate(parts_):
    x, y = 96 + (i // 3) * 884, 230 + (i % 3) * 190
    t.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:844px;height:160px;display:flex;flex-direction:row;align-items:center;gap:28px;border-bottom:2px solid {LINE}">'
             f'<p style="width:70px;font-size:72px;font-weight:900;color:{c}">{i + 1}</p><x-icon name="{ic}" style="width:52px;height:52px;color:{c}"></x-icon>'
             f'<p style="flex:1;font-size:44px;font-weight:700;color:{INK}">{e(h)}</p><p style="font-size:28px;color:{GRAY}">{page[a]}–{page[b]}쪽</p></div>')
t.append(f'<p style="position:absolute;left:96px;top:880px;font-size:30px;color:{SUB}">{page["ready"]}쪽은 노트북 준비, {page["trouble"]}–{page["cheatsheet"]}쪽은 막힐 때와 한 장 요약이에요.</p>')
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(t) + "\n<aside>" + e("여섯 파트로 나눴어요. 1파트는 딕셔너리로 만들 때의 불편함과 틀과 붕어빵 그림이에요. 2파트는 가장 작은 틀을 만들고 손으로 값을 붙여 봐요. 3파트가 오늘의 중심이에요. 19의 함수에서 출발해 __init__과 self를 한 걸음씩 봐요. 4파트는 메서드, 5파트는 자주 나는 오류, 6파트는 가게와 카페 실습이에요. 파트마다 새 커널에서 위에서부터 차례로 실행해요.") + "</aside>\n</section>\n")
deck = {"v": 4, "lists": "css", "title": "클래스 1 (붕어빵 틀과 붕어빵)", "order": ORDER, "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}}, "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
print(len(ORDER), "slides")
