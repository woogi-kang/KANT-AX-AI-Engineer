"""Generates every slide of the control flow 2 deck (18, while, break) and slides/deck.json.

Story: keeps writing in basics.ipynb from chapters 12-17. Starts from a for loop that buys one coffee too many,
draws for and while side by side, teaches range and enumerate, then while, break and continue on the café's stock.
Part 5 builds totals, counts and maximums by hand next to sum(), max() and count(), and nests loops (times table,
chapter 14's scores). Ends with traps and four café exercises.
Every cell and output comes from tools/demo.sh (tools/run_nb.py runs the cells with the project kernel).

Layout follows the Stageshow rules (github.com/benjitaylor/skills, stageshow/SKILL.md and references/):
- one focal object per slide, the code cell, drawn large; at most one quiet picture beside it
- terms are written on the code line they belong to (leader tags), not in bordered cards
- say it once: what the speaker notes already say is not repeated on the slide
- no empty bands: the cell font grows to fill the slide instead
- values that change move (fly) or build row by row; one highlight at a time (tools/HIGHLIGHT.md)
Highlights (2026-11-09 player): slam and shine on the cover, staggered rows, spotlight, run band, line spotlight,
cursor click, keycaps, pen ring and underline, changed word (MARK), count-up, shake, fly. No typing effect.
Usage: python3 tools/gen.py slides
"""

import html, json, os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from highlight import (spot, spot_off, cursor, cursor_off, ring, box, underline, lspot, lspot_off, run, run_off, zoom, zoom_off,
                       shine, shake, keys, SLAM, STAGGER, COUNT, MARK, DELAY)

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
INK, SUB, LINE, CARD = "#1D2330", "#4A5262", "#E1DED6", "#FFFFFF"
BL, GR, OR, PUR, RED, NAVY, TEAL, GRAY = "#2459C9", "#1F8A4C", "#B26A00", "#5A3BB8", "#A33131", "#1E3F8F", "#0F7C86", "#6A7180"
JP = "#B8560F"          # Jupyter, same as chapters 09 and 10
SEL = "#2F7DE1"         # selected cell bar, like VS Code's focus color
WIN, MAC = BL, "#3D4250"
FAINT = "#B4B9C3"
GRBG, REDBG, ORBG, BLBG, GRAYBG = "#E6F4EC", "#F8E6E6", "#F7EEDD", "#E5EEF8", "#EEEFF2"


def e(s):
    return html.escape(s, quote=False)


def p(style, text, attrs=""):
    return f'<p{attrs} style="{style}">{text}</p>'


def bi(kind, order):
    return f' data-build-in="{kind} order {order}"' if order else ""


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


def caption(text, order, top=950):
    return p(f"position:absolute;left:96px;top:{top}px;width:1728px;font-size:34px;font-weight:700;line-height:1.4;color:{INK}", text, ' id="caption"' + bi("rise", order))


def num(i, color, size=56, extra=""):
    return p(f"width:{size + 16}px;height:{size + 16}px;flex:none;border-radius:50%;background:{color};color:#FFFFFF;font-size:{size * 0.6:.0f}px;font-weight:900;line-height:{size + 16}px;text-align:center;{extra}", str(i))


def kbd(text, size=30, color=INK):
    """Key caps. Keys joined with + are pressed together."""
    caps = [p(f"font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.2;white-space:nowrap;color:{color};background:#FFFFFF;border:2px solid #C9CED8;border-bottom-width:5px;border-radius:10px;padding:6px 14px", e(k)) for k in text.split("+")]
    plus = p(f"font-size:{size * 0.8:.0f}px;font-weight:700;color:{GRAY}", "+")
    return '<div style="display:flex;flex-direction:row;align-items:center;gap:8px">' + plus.join(caps) + '</div>'


def mono(text, size=28, color=INK, bg="#F1F0EC", extra=""):
    return p(f"font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.4;color:{color};background:{bg};border-radius:10px;padding:4px 16px;white-space:pre;{extra}", e(text))


# ---------- notebook cell, drawn at a per-slide font size ----------
FS = [30]


def LH():
    return FS[0] * 1.45


def tw(s, fs=None):
    """Rendered width of a code string: Hangul 0.92 em (Noto Sans KR), everything else 0.6 em."""
    f = fs or FS[0]
    return sum(f * (0.92 if '가' <= ch <= '힣' else 0.6) for ch in s)


def cell_w(lines, extra=0):
    """A cell that hugs its longest code line (plus room for the small Python tag)."""
    return int(87 + 40 + max(tw(l) for l in lines) + 96 + extra)


def cell_h(c):
    h = 20 + LH() * len(c["lines"])
    if c.get("out"):
        h += 10 + LH() * len(c["out"])
    return h


def WIDE(t):
    """Draws each Hangul syllable two monospace columns wide, like a terminal."""
    return re.sub(r"([가-힣])", r'<span style="display:inline-block;width:1.2em;text-align:center">\1</span>', t)


def cell(c, left, top, w=None, sel=True, attrs="", gutter=None, out_attrs=None):
    """c: dict(id, lines, n, out, err, wide). Error lines (SomethingError, KeyboardInterrupt) print red.
    gutter: html for the left gutter instead of [n]. out_attrs: {output line index: build-in attrs}."""
    fs, lines = FS[0], c["lines"]
    w = w or cell_w(lines)
    o = [f'<div id="{c["id"]}"{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;display:flex;flex-direction:column;gap:10px">']
    bar = f'<div style="width:7px;flex:none;border-radius:4px;background:{SEL if sel else "transparent"}"></div>'
    g = gutter if gutter is not None else p(f"font-family:{MONO};font-size:22px;color:{GRAY};text-align:right", f"[{c['n']}]" if c.get("n") else "[ ]")
    gut = f'<div style="width:58px;flex:none;padding-top:{fs * 0.45:.0f}px;display:flex;flex-direction:column;align-items:flex-end">{g}</div>'
    txt = "".join(p(f"font-family:{MONO};font-size:{fs}px;line-height:1.45;white-space:pre;color:{INK}", e(l) if l else "&#160;") for l in lines)
    tag_ = p(f"position:absolute;right:14px;bottom:8px;font-size:18px;color:{GRAY}", "Python")
    box_ = f'<div style="flex:1;position:relative;background:#FFFFFF;border:2px solid {LINE};border-radius:10px;padding:8px 18px 8px;display:flex;flex-direction:column">{txt}{tag_}</div>'
    o.append(f'<div style="display:flex;flex-direction:row;gap:10px;align-items:stretch">{bar}{gut}{box_}</div>')
    if c.get("out"):
        wide = WIDE if c.get("wide") else (lambda t: t)
        oa = out_attrs or {}
        rows = "".join(p(f"font-family:{MONO};font-size:{fs}px;line-height:1.45;white-space:pre;color:{RED if re.match(r'[A-Za-z]+(Error|Interrupt)', l) else INK}", wide(e(l)) if l else "&#160;", oa.get(j, ""))
                       for j, l in enumerate(c["out"]))
        o.append(f'<div style="margin-left:85px;padding:0 20px;display:flex;flex-direction:column">{rows}</div>')
    o.append('</div>')
    return o


def ly(top, i):
    """Centre y of code line i (may be fractional) of a cell drawn at top."""
    return top + 10 + i * LH() + LH() / 2


def oy(top, n, j):
    """Centre y of output line j of a cell with n code lines."""
    return top + 20 + n * LH() + 10 + j * LH() + LH() / 2


def cx(left, col):
    """x of character column col in a code or output line (ASCII before it)."""
    return left + 105 + col * 0.6 * FS[0]


HL = {"run": "rgba(31,138,76,0.16)", "skip": "rgba(106,113,128,0.20)", "err": "rgba(163,49,49,0.14)", "mark": "rgba(36,89,201,0.14)", "note": "rgba(178,106,0,0.16)"}
HLT = {"run": GR, "skip": GRAY, "err": RED, "mark": BL, "note": OR}


def hl(left, top, w, i, n=1, kind="run", order=1):
    """Tints code lines i..i+n-1 of a cell drawn at (left, top, w)."""
    y = top + 10 + i * LH()
    return f'<div{bi("fade", order)} style="position:absolute;left:{left + 87}px;top:{y:.0f}px;width:{w - 89}px;height:{n * LH():.0f}px;background:{HL[kind]};border-radius:6px"></div>'


def ohl(left, top, n, j, w, kind="mark", order=1, k=1):
    """Tints output lines j..j+k-1 of a cell with n code lines."""
    y = top + 20 + n * LH() + 10 + j * LH()
    return f'<div{bi("fade", order)} style="position:absolute;left:{left + 93}px;top:{y:.0f}px;width:{w}px;height:{k * LH():.0f}px;background:{HL[kind]};border-radius:6px"></div>'


def tag(x, y, text, color, order=None, size=28, lead=True, w=None, anim="fade", mono_=False):
    """A leader label '← text' centred on y. No box."""
    ws = f"width:{w}px;white-space:normal;" if w else "white-space:nowrap;"
    t = ("← " if lead else "") + e(text)
    fam = f"font-family:{MONO};" if mono_ else ""
    return p(f"position:absolute;left:{x:.0f}px;top:{y - size * 0.725:.0f}px;{ws}{fam}font-size:{size}px;font-weight:700;line-height:1.45;color:{color}", t, bi(anim, order))


def tx(left, lines, gap=36, out=False):
    """x just right of the longest of the given lines inside a cell at left."""
    return int(left + 105 + max(tw(l) for l in lines) + gap)


def rtag(left, w, y, text, color, order=None, size=28):
    """A leader tag just outside the right edge of a cell box."""
    return tag(left + w + 30, y, text, color, order, size)


# ---------- pictures ----------
def slots(items, left, top, w=170, h=96, idx=True, attrs="", fs=34, states=None, color=BL, bg=BLBG, ids=None, gap=10):
    """List items in a row of boxes, index numbers above. states: per item 'on', 'off' (faded) or a (border, fill) pair."""
    o = [f'<div{attrs} style="position:absolute;left:{left}px;top:{top}px;display:flex;flex-direction:row;gap:{gap}px">']
    for i, it in enumerate(items):
        st = (states or ["on"] * len(items))[i]
        bc, fc, tc = (color, bg, INK) if st == "on" else (("#D5D8DE", "#F1F0EC", FAINT) if st == "off" else (st[0], st[1], INK))
        idd = f' id="{ids[i]}"' if ids else ""
        o.append('<div style="display:flex;flex-direction:column;align-items:center;gap:8px">'
                 + (p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{GRAY}", str(i)) if idx else "")
                 + p(f"width:{w}px;height:{h}px;border-radius:14px;border:3px solid {bc};background:{fc};font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:{h - 6}px;text-align:center;color:{tc};white-space:pre", e(it), idd) + '</div>')
    o.append('</div>')
    return "".join(o)


def grid(rows, left, top, cw=150, ch=84, states=None, attrs="", fs=32, color=GR, rid=None):
    """A list of lists as a table with row numbers left and column numbers on top.
    states: {(r, c): 'hit' | 'off' | 'on'}. rid: id prefix for each row (for spotlights)."""
    st = states or {}
    o = [f'<div{attrs} style="position:absolute;left:{left}px;top:{top}px;display:flex;flex-direction:column;gap:8px">']
    o.append('<div style="display:flex;flex-direction:row;gap:8px"><div style="width:56px;flex:none"></div>'
             + "".join(p(f"width:{cw}px;flex:none;text-align:center;font-family:{MONO};font-size:24px;font-weight:700;color:{GRAY}", str(j)) for j in range(len(rows[0]))) + '</div>')
    for i, r in enumerate(rows):
        cells_ = ""
        for j, v in enumerate(r):
            s = st.get((i, j), "plain")
            bc, fc, tc = {"plain": (LINE, CARD, INK), "on": (color, GRBG if color == GR else BLBG, INK), "hit": (RED, REDBG, INK), "off": ("#E4E5E8", "#F1F0EC", FAINT)}[s]
            cells_ += p(f"width:{cw}px;height:{ch}px;flex:none;border-radius:12px;border:3px solid {bc};background:{fc};font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:{ch - 6}px;text-align:center;color:{tc};white-space:pre", e(str(v)), f' id="{rid}{i}-{j}"' if rid else "")
        o.append(f'<div style="display:flex;flex-direction:row;gap:8px;align-items:center">' + p(f"width:56px;flex:none;text-align:right;padding-right:10px;font-family:{MONO};font-size:24px;font-weight:700;color:{GRAY}", str(i)) + cells_ + '</div>')
    o.append('</div>')
    return "".join(o)


def tf(v, size=26):
    c, b = (GR, GRBG) if v == "True" else (RED, REDBG)
    return p(f"display:inline-block;font-family:{MONO};font-size:{size}px;font-weight:700;color:{c};background:{b};border-radius:10px;padding:2px 14px;white-space:nowrap", v)


def trace(left, top, cols, rows, order0=1, rh=72, fs=30, rid=None, each=True, delay=0):
    """A trace table drawn with hairlines only: gray header, one row per click."""
    w = sum(cw for _, cw in cols) + 24 * (len(cols) - 1)
    o = [f'<div{bi("fade", order0)} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:52px;display:flex;flex-direction:row;gap:24px;align-items:center;border-bottom:3px solid {INK}">'
         + "".join(p(f"width:{cw}px;flex:none;font-family:{MONO if c.isascii() else SANS};font-size:24px;font-weight:700;color:{GRAY};white-space:nowrap", e(c)) for c, cw in cols) + '</div>']
    for i, r in enumerate(rows):
        cs = ""
        for (c, cw), v in zip(cols, r):
            if v in ("True", "False"):
                cs += f'<div style="width:{cw}px;flex:none">{tf(v, fs - 4)}</div>'
            else:
                cs += p(f"width:{cw}px;flex:none;font-family:{MONO if v.isascii() else SANS};font-size:{fs}px;font-weight:700;color:{INK};white-space:nowrap", e(v))
        idd = f' id="{rid}{i}"' if rid else ""
        o.append(f'<div{idd}{bi("rise", order0 + i) if each else bi("rise", order0) + (DELAY(i * delay) if delay else "")} style="position:absolute;left:{left}px;top:{top + 56 + i * rh}px;width:{w}px;height:{rh}px;display:flex;flex-direction:row;gap:24px;align-items:center;border-bottom:2px solid {LINE}">{cs}</div>')
    return o


def plain_rows(left, top, w, rows, widths, order0=1, rh=84, head_=None, fs=28, head_colors=None, step=True):
    """A light table: header row, rows split by hairlines, no boxes. A cell that is ASCII is drawn in mono."""
    o = []
    y = top
    if head_:
        hc = head_colors or [GRAY] * len(head_)
        o.append(f'<div{bi("fade", order0)} style="position:absolute;left:{left}px;top:{y}px;width:{w}px;height:56px;display:flex;flex-direction:row;gap:24px;align-items:center;border-bottom:3px solid {INK}">'
                 + "".join(p(f"width:{cw}px;flex:none;font-family:{MONO if c.isascii() and c else SANS};font-size:{30 if c.isascii() and c else 24}px;font-weight:700;color:{col}", e(c)) for c, cw, col in zip(head_, widths, hc)) + '</div>')
        y += 60
    for i, r in enumerate(rows):
        cs = ""
        for k, (c, cw) in enumerate(zip(r, widths)):
            code = c.isascii() and k > 0
            cs += p(f"width:{cw}px;flex:none;font-family:{MONO if code else SANS};font-size:{fs}px;font-weight:{700 if k == 0 or code else 500};color:{SUB if k == 0 else INK};line-height:1.35;white-space:pre-wrap", e(c))
        o.append(f'<div{bi("rise", order0 + (i if step else 0))} style="position:absolute;left:{left}px;top:{y + i * rh}px;width:{w}px;height:{rh}px;display:flex;flex-direction:row;align-items:center;gap:24px;border-bottom:2px solid {LINE}">{cs}</div>')
    return o


_fl = [0]


def arrow_svg(pts, color, w, h, left=0, top=0, order=None, dash=False, sw=5):
    _fl[0] += 1
    mid = f"fa{_fl[0]}"
    ps = " ".join(f"{x:.0f},{y:.0f}" for x, y in pts)
    d = ' stroke-dasharray="12 10"' if dash else ""
    return (f'<svg{bi("fade", order)} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;overflow:visible" viewBox="0 0 {w} {h}">'
            f'<defs><marker id="{mid}" markerUnits="userSpaceOnUse" markerWidth="24" markerHeight="24" refX="20" refY="12" orient="auto"><path d="M0,0 L24,12 L0,24 z" fill="{color}"/></marker></defs>'
            f'<polyline points="{ps}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linejoin="round"{d} marker-end="url(#{mid})"/></svg>')


def jump(left, top, w, fi, ti, color, text, order, reach=56):
    """An arrow just outside the right edge of a cell box, from code line fi to code line ti (where break or continue goes)."""
    x0 = left + w + 6
    yf, yt = ly(top, fi), ly(top, ti)
    lo, hi_ = min(yf, yt) - 20, max(yf, yt) + 20
    o = [arrow_svg([(0, yf - lo), (reach, yf - lo), (reach, yt - lo), (6, yt - lo)], color, reach + 20, hi_ - lo, x0, lo, order)]
    o.append(p(f"position:absolute;left:{x0 + reach + 16}px;top:{(yf + yt) / 2 - 20:.0f}px;font-size:28px;font-weight:700;line-height:1.45;color:{color};white-space:nowrap", e(text), bi("fade", order)))
    return "".join(o)


def flow(left, top, w, h, nodes, edges, attrs=""):
    """A small flowchart. nodes: dict(x, y, w, h, kind box|diamond, text, color, bg, order, fs, mono).
    edges: dict(pts, color, order, label, lx, ly, dash). Coordinates are inside the w x h area."""
    o = [f'<div{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px">']
    for ed in edges:
        col = ed.get("color", "#9AA1AE")
        o.append(arrow_svg(ed["pts"], col, w, h, 0, 0, ed.get("order"), ed.get("dash")))
        if ed.get("label"):
            o.append(p(f"position:absolute;left:{ed['lx']}px;top:{ed['ly']}px;font-size:26px;font-weight:700;color:{col};white-space:nowrap", e(ed["label"]), bi("fade", ed.get("order"))))
    for nd in nodes:
        x, y, nw, nh = nd["x"], nd["y"], nd["w"], nd["h"]
        col, bg = nd.get("color", GRAY), nd.get("bg", CARD)
        at = bi(nd.get("anim", "rise"), nd.get("order")) + (f' id="{nd["id"]}"' if nd.get("id") else "")
        font = MONO if nd.get("mono", True) else SANS
        txt = p(f"font-family:{font};font-size:{nd.get('fs', 30)}px;font-weight:700;line-height:1.3;color:{INK};text-align:center;white-space:pre", e(nd["text"]))
        if nd.get("kind") == "diamond":
            o.append(f'<div{at} style="position:absolute;left:{x}px;top:{y}px;width:{nw}px;height:{nh}px">'
                     f'<svg style="position:absolute;left:0;top:0;width:{nw}px;height:{nh}px" viewBox="0 0 {nw} {nh}"><polygon points="{nw / 2:.0f},3 {nw - 3},{nh / 2:.0f} {nw / 2:.0f},{nh - 3} 3,{nh / 2:.0f}" fill="{bg}" stroke="{col}" stroke-width="4"/></svg>'
                     f'<div style="position:absolute;left:{nw * 0.18:.0f}px;top:0;width:{nw * 0.64:.0f}px;height:{nh}px;display:flex;align-items:center;justify-content:center">{txt}</div></div>')
        else:
            o.append(f'<div{at} style="position:absolute;left:{x}px;top:{y}px;width:{nw}px;height:{nh}px;background:{bg};border:3px solid {col};border-radius:16px;display:flex;align-items:center;justify-content:center;padding:0 14px">{txt}</div>')
    o.append('</div>')
    return "".join(o)


def strike_fix(left, top, bad, good, order, size=32, label=None):
    """The old line struck through, an arrow, the new line."""
    lab = p(f"font-size:26px;font-weight:700;color:{GRAY};margin-bottom:14px", e(label)) if label else ""
    return (f'<div{bi("rise", order)} style="position:absolute;left:{left}px;top:{top}px;display:flex;flex-direction:column">{lab}'
            f'<div style="display:flex;flex-direction:row;align-items:center;gap:24px">'
            + p(f"font-family:{MONO};font-size:{size}px;font-weight:700;color:{GRAY};text-decoration:line-through;text-decoration-color:{RED};text-decoration-thickness:4px;white-space:pre", e(bad))
            + f'<x-shape kind="arrow-right" style="width:64px;height:32px;flex:none;background:#C9CED8"></x-shape>'
            + p(f"font-family:{MONO};font-size:{size}px;font-weight:700;color:{INK};background:{GRBG};border:3px solid {GR};border-radius:14px;padding:6px 20px;white-space:pre", e(good)) + '</div></div>')


def state_row(left, top, items, states, order, title=None, color=INK, w=110, h=118, fs=22, gap=8):
    """Orders in a row with what happened to each: 받음, 멈춤, 건너뜀, 안 봄 (same look in part 4 and 6)."""
    o = [p(f"position:absolute;left:{left}px;top:{top}px;font-size:26px;font-weight:700;color:{color};white-space:nowrap", e(title), bi("fade", order))] if title else []
    y = top + (48 if title else 0)
    sty = {"받음": (GR, GRBG, INK, GR), "나감": (GR, GRBG, INK, GR), "멈춤": (RED, REDBG, INK, RED), "건너뜀": (OR, ORBG, INK, OR), "안 봄": ("#D5D8DE", "#F1F0EC", FAINT, GRAY)}
    for i, (m, st) in enumerate(zip(items, states)):
        b, f, t_, sc = sty[st]
        o.append(f'<div{bi("rise", order)} style="position:absolute;left:{left + i * (w + gap)}px;top:{y}px;width:{w}px;height:{h}px;border-radius:14px;border:3px solid {b};background:{f};display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px">'
                 + p(f"font-family:{MONO};font-size:{fs}px;font-weight:700;color:{t_}", e(m)) + p(f"font-size:20px;font-weight:700;color:{sc}", e(st)) + '</div>')
    return o


EB1 = "1. 왜 필요한가"
EB2 = "2. range와 번호"
EB3 = "3. while"
EB4 = "4. break와 continue"
EB5 = "5. 쌓기와 겹친 반복"
EB6 = "6. 함정과 실습"
K1, K2, K3, K4, K5, K6 = "#1E5FA8", "#A0620A", TEAL, "#A23B72", GR, PUR
K2BG, K6BG = "#F7EEDD", "#ECE7F8"
REAL = " 출력은 실제로 실행한 결과예요."
NEWK = " 이 파트는 새 커널이라 셀 번호가 [1]부터예요."
MENUS = 'menus = ["coffee", "latte", "cake"]'
NB = "basics.ipynb"
T0 = 220            # top of the focal object under the title

# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#F2B27A;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
       f'<h1{SLAM(1)} style="font-size:92px;font-weight:900;line-height:1.1;color:#F6F5F1">제어문 2<br>반복 제어</h1>',
       '<p style="font-size:40px;line-height:1.4;color:#BFC6D4">조건이 맞는 동안 돌고<br>필요하면 멈추기</p>']
# corner bleed: the code panel runs off the right and bottom edges
cov.append('<div id="cov-code" style="position:absolute;left:1010px;top:300px;width:1010px;height:900px;background:#252B36;border-radius:28px;padding:64px 64px;display:flex;flex-direction:column">')
for line, c in [("for i in range(1, 4):", "#9DBDEB"), ("    print(i)", "#E6E9EF"), ("", "#E6E9EF"), ("while stock > 0:", "#E3B877"), ("    stock -= 1", "#E6E9EF"), ("    if stock == 1:", "#8FD8DE"), ("        break", "#F2A0A0")]:
    cov.append(p(f"font-family:{MONO};font-size:40px;font-weight:700;line-height:1.55;color:{c};white-space:pre", e(line) if line else "&#160;"))
cov.append('</div>')
cov.append(shine(2, "cov-code"))
W("cover", cov, "이번 챕터는 반복을 원하는 만큼만 돌리는 법을 배워요. 17에서 if로 조건에 따라 실행할 줄을 골랐어요. 13의 for는 리스트를 처음부터 끝까지 돌았어요. 이번에는 range로 정한 횟수만큼 돌고, while로 조건이 맞는 동안 돌고, break와 continue로 도중에 멈추거나 건너뛰어요. 17과 같은 카페 예제를 이어서 써요.", ("intro", "들어가기"))

ORDER.append("toc")

# ---------- ready ----------
o = [sec("ready")] + head("들어가기", "17에서 이어서 해요", JP)
done = [("hello-uv 노트북, 커널 .venv", "09 · 25–27쪽"), ("+=, -=, //", "12"), ("리스트, for, f-string, end=", "13"), ("2차원 리스트 scores", "14"), ("딕셔너리 items()", "15"), ("if, elif, else, and, or", "17")]
for i, (a_, b_) in enumerate(done):
    o.append(f'<div{bi("rise", 1)}{DELAY(i * 90)} style="position:absolute;left:96px;top:{T0 + i * 108}px;width:800px;height:96px;display:flex;flex-direction:row;gap:24px;align-items:center;border-bottom:2px solid {LINE}">'
             + f'<x-icon name="CheckCircle" style="width:44px;height:44px;color:{GR}"></x-icon>'
             + p(f"flex:1;font-size:32px;font-weight:700;color:{INK}", e(a_))
             + p(f"font-size:28px;font-weight:700;color:{GRAY};white-space:nowrap", e(b_)) + '</div>')
o.append(p(f"position:absolute;left:1000px;top:{T0 + 14}px;font-size:36px;font-weight:700;color:{JP}", "노트북 다시 열기", bi("rise", 2)))
steps_ = [p(f"font-size:32px;color:{INK}", "VS Code로 hello-uv 폴더 열기"),
          p(f"font-size:32px;color:{INK}", "탐색기에서") + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{JP}", NB) + p(f"font-size:32px;color:{INK}", "열기"),
          p(f"font-size:32px;color:{INK}", "오른쪽 위 커널이 .venv인지 보기"),
          p(f"font-size:32px;color:{INK}", "셀에 적고") + kbd("Shift+Enter", 26) + p(f"font-size:32px;color:{INK}", "로 실행")]
for i, inner in enumerate(steps_):
    o.append(f'<div{bi("rise", 2)}{DELAY(90 + i * 90)} style="position:absolute;left:1000px;top:{T0 + 108 + i * 120}px;width:824px;height:104px;display:flex;flex-direction:row;gap:20px;align-items:center">' + num(i + 1, JP, 40) + inner + '</div>')
o.append(caption("기억이 안 나면 왼쪽에 적힌 챕터를 먼저 다시 봐요.", 3, 900))
W("ready", o, "12부터 쓰던 basics.ipynb를 열고 시작해요. 09에서 만든 hello-uv 폴더를 VS Code로 열어요. 12의 +=와 -=, 13의 for와 f-string, print의 end, 14의 2차원 리스트, 15의 items(), 17의 if를 그대로 써요. 슬라이드의 출력은 tools/demo.sh가 hello-uv 커널에서 같은 셀을 실제로 실행한 결과예요. 셀 번호는 파트마다 [1]부터 다시 셌어요.")

# ---------- part 1 ----------
FS[0] = 38
o = [sec("w-why")] + head(EB1, "몇 번 돌지 모르면 for로 쓰기 어려워요", K1)
c = {"id": "c-why", "lines": ["money = 10000", "for cup in [1, 2, 3]:", "    money -= 4500", '    print(f"{cup}잔째, 남은 돈 {money}원")'], "n": 1, "out": ["1잔째, 남은 돈 5500원", "2잔째, 남은 돈 1000원", "3잔째, 남은 돈 -3500원"]}
cw = cell_w(c["lines"])
o += cell(c, 96, T0, cw)
o.append(hl(96, T0, cw, 1, 1, "mark", 1))
o.append(rtag(96, cw, ly(T0, 1), "3번으로 정했어요", BL, 1))
x3 = cx(96, 0) + tw("3잔째, 남은 돈 ")
o.append(ring(2, x3 + 16, oy(T0, 4, 2) - LH() / 2, tw("-3500원") - 32, LH(), RED))
o.append(tag(cx(96, 0) + tw("3잔째, 남은 돈 -3500원") + 70, oy(T0, 4, 2), "돈이 모자라도 셋째 잔을 사요", RED, 2))
o.append(strike_fix(96, 760, "for cup in [1, 2, 3]:", "돈이 4500원 이상인 동안 사요", 3, 36, "몇 잔인지 모르니 횟수 대신 조건으로 말해요"))
o.append(caption("\"~인 동안 반복\"을 적는 문법이 while이에요.", 4))
W("w-why", o, "몇 번 돌지 미리 모르는 반복은 for로 쓰기 어려워요. 13에서 for는 리스트의 값 개수만큼 돌았어요. 여기서는 1, 2, 3 세 번으로 정했어요. 그런데 10000원으로는 두 잔만 살 수 있어서 셋째 잔에서 돈이 마이너스가 돼요. for는 돈이 모자란지 신경 쓰지 않고 정한 만큼 돌아요. 알고 싶은 건 몇 잔 살 수 있는지라서 횟수를 미리 정할 수 없어요. 돈이 4500원 이상인 동안 계속 사라고 적는 문법이 while이에요." + NEWK + REAL, ("p1", "왜 필요한가"))

o = [sec("w-big")] + head(EB1, "for는 묶음을 하나씩, while은 조건이 True인 동안", K1)
o.append(p(f"position:absolute;left:96px;top:{T0}px;font-size:30px;font-weight:700;color:{BL}", "for", bi("fade", 1)))
o.append(slots(["coffee", "latte", "cake"], 96, T0 + 60, 220, 84, idx=False, attrs=bi("rise", 1), fs=30))
o.append(flow(96, T0 + 200, 760, 470,
              [dict(x=120, y=0, w=520, h=100, text="다음 값을 꺼내요", color=BL, mono=False, order=2),
               dict(x=120, y=180, w=520, h=100, text="들여쓴 줄 실행", color=GR, bg=GRBG, mono=False, order=2),
               dict(x=120, y=360, w=520, h=100, text="값이 없으면 끝", color=GRAY, mono=False, order=2)],
              [dict(pts=[(380, 102), (380, 176)], order=2), dict(pts=[(640, 230), (720, 230), (720, 50), (644, 50)], color=BL, order=2),
               dict(pts=[(120, 50), (40, 50), (40, 410), (116, 410)], color=GRAY, order=2, dash=True)]))
o.append(f'<div style="position:absolute;left:940px;top:{T0}px;width:2px;height:690px;background:{LINE}"></div>')
o.append(p(f"position:absolute;left:1020px;top:{T0}px;font-size:30px;font-weight:700;color:{OR}", "while", bi("fade", 3)))
o.append(flow(1020, T0 + 60, 804, 630,
              [dict(id="wb-dia", x=150, y=0, w=500, h=190, kind="diamond", text="money >= 4500", color=OR, bg=ORBG, order=3, fs=30),
               dict(x=170, y=290, w=460, h=100, text="money -= 4500", color=GR, bg=GRBG, order=4),
               dict(x=170, y=500, w=460, h=100, text="반복 끝, 다음 줄", color=GRAY, mono=False, order=4)],
              [dict(pts=[(400, 192), (400, 286)], color=GR, order=4, label="True", lx=420, ly=214),
               dict(pts=[(630, 340), (760, 340), (760, 95), (654, 95)], color=GR, order=4, label="다시 묻기", lx=640, ly=40),
               dict(pts=[(150, 95), (50, 95), (50, 550), (166, 550)], color=RED, order=4, label="False", lx=66, ly=300)]))
o.append(caption("횟수를 알면 for, 조건만 알면 while이에요.", 5))
W("w-big", o, "for는 줄 선 값을 하나씩 꺼내고, while은 조건이 True인 동안 계속 물어요. 왼쪽 for는 리스트처럼 줄 선 값을 하나씩 꺼내서 들여쓴 줄을 실행하고, 값이 떨어지면 끝나요. 몇 번 도는지 처음부터 정해져 있어요. 오른쪽 while은 17의 if처럼 마름모에서 조건을 물어요. True면 들여쓴 줄을 실행하고, 다시 마름모로 돌아가 또 물어요. False가 나오는 순간 반복을 끝내고 다음 줄로 가요. if는 한 번 묻고 지나가지만 while은 False가 될 때까지 계속 물어요.")

FS[0] = 34
o = [sec("w-min")] + head(EB1, "가장 짧은 while로 몇 잔인지 세요", K1)
c = {"id": "c-min", "lines": ["money = 10000", "cups = 0", "while money >= 4500:", "    money -= 4500", "    cups += 1", 'print(f"{cups}잔, 남은 돈 {money}원")'], "n": 2, "out": ["2잔, 남은 돈 1000원"]}
cw = cell_w(c["lines"])
o += cell(c, 96, T0, cw)
o.append(hl(96, T0, cw, 2, 1, "mark", 1))
o.append(rtag(96, cw, ly(T0, 2), "조건 뒤에 콜론, if와 같은 모양", BL, 1))
o.append(hl(96, T0, cw, 3, 2, "run", 2))
o.append(rtag(96, cw, ly(T0, 3.5), "True인 동안 이 두 줄을 반복", GR, 2))
o += trace(183, 640, [("money", 190), (">= 4500", 200), ("cups", 130), ("", 160)],
           [("10000", "True", "0", "사요"), ("5500", "True", "1", "사요"), ("1000", "False", "2", "멈춰요")], 3, 68, 32, rid="wm-r", each=False, delay=160)
o.append(spot(4, target="wm-r2", pad=10, r=12))
o.append(spot_off(5))
o.append(caption("while 조건: 은 조건이 True인 동안 들여쓴 줄을 반복해요.", 5))
W("w-min", o, "while 조건: 은 조건이 True인 동안 들여쓴 줄을 반복해요. 앞 장의 질문을 while로 풀었어요. money가 4500 이상인 동안 커피를 사요. 살 때마다 money에서 4500을 빼고 cups에 1을 더해요. 오른쪽 표처럼 10000일 때 True, 5500일 때 True, 1000일 때 False가 나와서 두 잔에서 멈춰요. 모양은 17의 if와 같아요. 조건 뒤에 콜론, 다음 줄은 4칸 들여써요. 다른 점은 들여쓴 줄을 다 실행한 뒤 다시 조건으로 돌아가 묻는다는 거예요. money -= 4500 줄이 돌 때마다 money를 줄여서 언젠가 조건이 False가 돼요." + REAL)

# ---------- part 2 ----------
FS[0] = 44
o = [sec("r-range")] + head(EB2, "range(5)는 0부터 4까지 다섯 개예요", K2)
c = {"id": "c-r1", "lines": ["print(range(5))", "print(list(range(5)))", "print(len(range(5)))"], "n": 1, "out": ["range(0, 5)", "[0, 1, 2, 3, 4]", "5"]}
cw = cell_w(c["lines"])
o += cell(c, 96, T0, cw)
ox = cx(96, 0) + tw("[0, 1, 2, 3, 4]") + 50
o.append(tag(ox, oy(T0, 3, 0), "그냥 찍으면 이렇게만 나와요", GRAY, 1))
o.append(tag(ox, oy(T0, 3, 1), "list()로 감싸면 숫자가 보여요", K2, 2))
o.append(tag(ox, oy(T0, 3, 2), "다섯 개", K2, 2))
o.append(p(f"position:absolute;left:96px;top:680px;font-family:{MONO};font-size:30px;font-weight:700;color:{K2}", "range(5)", bi("fade", 3)))
o.append(slots(["0", "1", "2", "3", "4"], 96, 730, 170, 130, idx=False, attrs=STAGGER(3, 110), fs=56, color=K2, bg=K2BG))
o.append(p(f"position:absolute;left:996px;top:730px;width:170px;height:130px;border-radius:14px;border:3px dashed {RED};font-family:{MONO};font-size:56px;font-weight:700;line-height:124px;text-align:center;color:{RED}", "5", bi("rise", 4)))
o.append(tag(1200, 795, "끝 숫자 5는 안 들어가요. 13의 [0:5]와 같아요", RED, 4))
o.append(caption("range(n)은 0부터 n-1까지, n개예요.", 5))
W("r-range", o, "range(n)은 0부터 n-1까지 정수 n개를 만들어요. range(5)는 0, 1, 2, 3, 4 다섯 개예요. print로 그냥 찍으면 range(0, 5)라고만 나와서 13의 list()로 감싸서 확인해요. 끝 숫자 5는 들어가지 않아요. 그래서 개수가 딱 5개예요. 13에서 문자열과 리스트를 [0:5]로 자를 때도 5번 칸은 빠졌어요. 같은 규칙이에요." + NEWK + REAL, ("p2", "range와 번호"))

FS[0] = 38
o = [sec("r-step")] + head(EB2, "시작, 끝, 간격을 정할 수 있어요", K2)
c = {"id": "c-r2", "lines": ["print(list(range(1, 6)))", "print(list(range(0, 10, 2)))", "print(list(range(5, 0, -1)))", "print(list(range(3, 3)))"], "n": 2, "out": ["[1, 2, 3, 4, 5]", "[0, 2, 4, 6, 8]", "[5, 4, 3, 2, 1]", "[]"]}
cw = cell_w(c["lines"])
o += cell(c, 96, T0, cw)
ox = cx(96, 0) + tw("[0, 2, 4, 6, 8]") + 50
for j, (t_, col) in enumerate([("1부터 6 앞까지", K2), ("0부터 2씩 건너뛰기", K2), ("간격 -1이면 거꾸로, 0 앞까지", K2), ("시작과 끝이 같으면 비어요", GRAY)]):
    o.append(ohl(96, T0, 4, j, tw("[0, 2, 4, 6, 8]") + 24, "note", j // 2 + 1))
    o.append(tag(ox, oy(T0, 4, j), t_, col, j // 2 + 1))
# the signature, labelled under each slot, and the end slot underlined
SIG = 760
o.append(f'<div{bi("rise", 3)} style="position:absolute;left:96px;top:{SIG}px;display:flex;flex-direction:row;align-items:baseline;font-family:{MONO};font-size:52px;font-weight:700;color:{INK};white-space:pre">'
         + 'range(<span style="color:#2459C9">시작</span>, <span style="color:#A33131">끝</span>, <span style="color:#1F8A4C">간격</span>)</div>')
end_x = 96 + tw("range(시작, ", 52)
o.append(underline(4, end_x - 4, end_x + tw("끝", 52) + 4, SIG + 86, RED))
o.append(tag(end_x - 10, SIG + 124, "끝은 늘 빠져요", RED, 4, 26, False))
o.append(tag(96 + tw("range(시작, 끝, 간격)", 52) + 60, SIG + 38, "13의 자르기 [시작:끝:간격]과 같은 순서", GRAY, 3, 28, False))
o.append(caption("1부터 5까지는 range(1, 6)이에요.", 5))
W("r-step", o, "range는 시작, 끝, 간격 순서로 숫자를 받아요. 숫자를 두 개 넣으면 시작과 끝이에요. range(1, 6)은 1부터 6 바로 앞인 5까지예요. 세 개를 넣으면 셋째가 간격이에요. range(0, 10, 2)는 0부터 2씩 건너뛰어 짝수만 나와요. 간격을 -1로 하면 거꾸로 세요. 이때는 시작 5가 끝 0보다 커야 해요. 시작과 끝이 같으면 빈 줄이에요. 13의 자르기 [시작:끝:간격]과 순서도, 끝이 빠지는 규칙도 같아요." + REAL)

FS[0] = 40
o = [sec("r-for")] + head(EB2, "for와 range로 정한 횟수만큼 돌아요", K2)
c = {"id": "c-r3", "lines": ["for i in range(3):", '    print("주문", i)', "for i in range(1, 4):", '    print(f"{i}번 손님")'], "n": 3, "out": ["주문 0", "주문 1", "주문 2", "1번 손님", "2번 손님", "3번 손님"]}
cw = cell_w(c["lines"])
o += cell(c, 96, T0, cw)
o.append(hl(96, T0, cw, 0, 1, "mark", 1))
o.append(rtag(96, cw, ly(T0, 0), "리스트 자리에 range", BL, 1))
# picture: range(3) gives 0, 1, 2 to i one at a time
PX = 1240
o.append(p(f"position:absolute;left:{PX}px;top:{T0}px;font-family:{MONO};font-size:30px;font-weight:700;color:{K2}", "range(3)", bi("fade", 1)))
o.append(slots(["0", "1", "2"], PX, T0 + 50, 120, 100, idx=False, attrs=bi("rise", 1), fs=44, color=K2, bg=K2BG, ids=["rf-s0", "rf-s1", "rf-s2"], gap=16))
o.append(p(f"position:absolute;left:{PX}px;top:{T0 + 220}px;font-family:{MONO};font-size:30px;font-weight:700;color:{BL}", "i", bi("fade", 2)))
o.append(f'<div{bi("fade", 2)} style="position:absolute;left:{PX}px;top:{T0 + 270}px;width:200px;height:130px;border:3px solid {BL};border-radius:18px;background:{CARD}"></div>')
for k in range(3):
    o.append(p(f"position:absolute;left:{PX + 3}px;top:{T0 + 273}px;width:194px;height:124px;border-radius:16px;background:{BLBG};font-family:{MONO};font-size:60px;font-weight:700;line-height:124px;text-align:center;color:{INK}", str(k), f' data-build-in="fly order {k + 2}" data-from="rf-s{k}"'))
    o.append(ohl(96, T0, 4, k, tw("1번 손님") + 30, "mark", k + 2))
o.append(tag(PX + 230, T0 + 335, "다음 숫자가 들어가요", BL, 2))
o.append(hl(96, T0, cw, 2, 1, "note", 5))
o.append(rtag(96, cw, ly(T0, 2), "사람에게 보일 번호는 1부터", OR, 5))
o.append(caption("\"n번 반복\"은 for i in range(n): 이에요.", 5))
W("r-for", o, "for 뒤에 리스트 대신 range를 넣으면 정한 횟수만큼 돌아요. range(3)은 0, 1, 2라서 세 번 돌고, i에는 차례로 0, 1, 2가 들어가요. 손님 번호처럼 사람에게 보일 번호는 1부터 세는 게 자연스러워서 range(1, 4)로 1, 2, 3을 만들어요. i는 정해진 이름이 아니에요. 번호라는 뜻의 index 앞 글자를 관례로 많이 쓰고, n이나 k로 적어도 돼요. 1파트의 [1, 2, 3] 리스트도 range(1, 4)로 바꿔 쓸 수 있어요." + REAL)

FS[0] = 30
o = [sec("r-index")] + head(EB2, "번호와 값을 같이 쓰려면 range(len())", K2)
c4 = {"id": "c-r4", "lines": [MENUS, "for i in range(len(menus)):", "    print(i, menus[i])"], "n": 4, "out": ["0 coffee", "1 latte", "2 cake"]}
c5 = {"id": "c-r5", "lines": ["i = 0", "for m in menus:", "    print(i, m)", "    i += 1"], "n": 5, "out": ["0 coffee", "1 latte", "2 cake"]}
cw = cell_w(c4["lines"])
o += cell(c4, 96, T0, cw)
o.append(hl(96, T0, cw, 1, 1, "mark", 1))
o.append(rtag(96, cw, ly(T0, 1), "len(menus)는 3, 그래서 0, 1, 2", BL, 1))
o.append(hl(96, T0, cw, 2, 1, "run", 2))
o.append(rtag(96, cw, ly(T0, 2), "i번 칸을 꺼내요 (13)", GR, 2))
SL = 1180
o.append(slots(["coffee", "latte", "cake"], SL, 720, 200, 90, fs=30, ids=["ri-s0", "ri-s1", "ri-s2"]))
o.append(p(f"position:absolute;left:{SL}px;top:676px;font-family:{MONO};font-size:26px;font-weight:700;color:{GRAY}", "menus"))
for k in range(3):
    o.append(spot(2 + k, target=f"ri-s{k}", pad=10, r=16))
o.append(spot_off(5))
T5 = 560
o += cell(c5, 96, T5, cw, sel=False, attrs=bi("rise", 5))
o.append(rtag(96, cw, ly(T5, 0), "번호를 직접 세는 방법, 결과가 같아요", GRAY, 5))
o.append(hl(96, T5, cw, 3, 1, "mark", 5))
o.append(caption("번호가 필요하면 range(len(리스트))로 돌고 [i]로 꺼내요.", 5))
W("r-index", o, "번호가 필요하면 range(len(리스트))로 돌고 [i]로 값을 꺼내요. range(len(menus))는 range(3)이라 0, 1, 2를 돌아요. i가 번호라서 값은 13처럼 menus[i]로 꺼내요. 리스트 길이가 바뀌어도 len이 맞춰 줘요. 아래 셀은 같은 일을 번호를 직접 세며 한 거예요. i를 0으로 두고 한 번 돌 때마다 1을 더해요. 두 방법 다 결과가 같아요. 다음 장에서 이 둘을 한 줄로 줄인 enumerate를 봐요." + REAL)

FS[0] = 30
o = [sec("r-enum")] + head(EB2, "enumerate는 번호와 값을 한 쌍씩 줘요", K2)
c6 = {"id": "c-r6", "lines": ["for i, m in enumerate(menus):", "    print(i, m)", "for i, m in enumerate(menus, 1):", '    print(f"{i}. {m}")'], "n": 6, "out": ["0 coffee", "1 latte", "2 cake", "1. coffee", "2. latte", "3. cake"]}
c7 = {"id": "c-r7", "lines": ["print(list(enumerate(menus)))"], "n": 7, "out": ["[(0, 'coffee'), (1, 'latte'), (2, 'cake')]"]}
cw = cell_w(c6["lines"])
o += cell(c6, 96, T0, cw)
o.append(hl(96, T0, cw, 0, 1, "mark", 1))
o.append(rtag(96, cw, ly(T0, 0), "번호는 i, 값은 m에", BL, 1))
o.append(hl(96, T0, cw, 2, 1, "note", 2))
o.append(rtag(96, cw, ly(T0, 2), "둘째 자리 1: 번호를 1부터", OR, 2))
T7 = 730
o += cell(c7, 96, T7, cw + 140, sel=False, attrs=bi("rise", 3))
o.append(underline(3, cx(96, 1), cx(96, 14), oy(T7, 1, 0) + LH() / 2 - 2, K2))
o.append(tag(cx(96, 0) + tw(c7["out"][0]) + 50, oy(T7, 1, 0), "(번호, 값) 튜플", K2, 3))
# the three ways, quiet, top right
RX, RY = 1080, 440
o.append(p(f"position:absolute;left:{RX}px;top:{RY}px;font-size:26px;font-weight:700;color:{GRAY}", "같은 결과, 세 가지 모양", bi("fade", 4)))
for k, (code, lab, col) in enumerate([("enumerate(menus)", "줄인 방법", K2), ("range(len(menus))", "앞 장", GRAY), ("i = 0 … i += 1", "직접 세기", GRAY)]):
    o.append(f'<div{bi("rise", 4)} style="position:absolute;left:{RX}px;top:{RY + 52 + k * 84}px;width:744px;height:76px;display:flex;flex-direction:row;align-items:center;gap:20px;border-bottom:2px solid {LINE}">'
             + p(f"flex:1;font-family:{MONO};font-size:26px;font-weight:700;color:{col};white-space:pre", e(code)) + p(f"font-size:24px;font-weight:700;color:{GRAY}", e(lab)) + '</div>')
o.append(caption("번호와 값이 둘 다 필요하면 enumerate를 써요.", 5, 960))
W("r-enum", o, "enumerate는 번호와 값을 한 쌍씩 줘요. 앞 장의 두 방법을 한 줄로 줄인 모양이에요. list()로 찍어 보면 (번호, 값) 튜플의 리스트예요. 그래서 13에서 튜플 리스트를 돌 때처럼 for i, m in으로 두 이름에 나눠 담아요. 괄호 안 둘째 자리에 1을 넣으면 번호가 1부터 시작해서 메뉴판 번호를 찍기 좋아요. 처음에는 range(len())이 이해하기 쉽고, 익숙해지면 enumerate를 써요." + REAL)

# ---------- part 3 ----------
FS[0] = 44
o = [sec("w-shape")] + head(EB3, "while은 묻기, 실행, 값 바꾸기를 돌아요", K3)
c = {"id": "c-w1", "lines": ["count = 1", "while count <= 3:", '    print(f"{count}번째")', "    count += 1", 'print("끝, count는", count)'], "n": 1, "out": ["1번째", "2번째", "3번째", "끝, count는 4"]}
cw = cell_w(c["lines"])
o += cell(c, 96, T0, cw)
for k, (i, kind, t_, col) in enumerate([(0, "mark", "① 시작값", K3), (1, "note", "② 묻기", OR), (2, "run", "③ 실행", GR), (3, "mark", "④ 값 바꾸기", BL)]):
    o.append(run(k + 1, 96 + 89, T0 + 10 + i * LH(), cw - 93, LH()))
    o.append(tag(96 + cw + 160, ly(T0, i), t_, col, k + 1))
o.append(run_off(5))
o.append(jump(96, T0, cw, 3, 1, BL, "", 5, 110))
o.append(tag(cx(96, 0) + tw("끝, count는 4") + 50, oy(T0, 5, 3), "4 <= 3이 False라서 멈춘 뒤의 값", K3, 5))
o.append(caption("while에는 시작값, 조건, 값 바꾸기 세 가지가 꼭 있어야 해요.", 5))
W("w-shape", o, "while에는 시작값, 조건, 값 바꾸기 세 가지가 꼭 있어야 해요. 먼저 반복 전에 시작값을 정해요. count는 1이에요. 다음으로 조건을 물어요. True면 들여쓴 줄을 실행해요. 마지막 줄에서 count에 1을 더해 값을 바꿔요. 그리고 화살표처럼 다시 조건으로 돌아가 물어요. 4가 되면 4 <= 3이 False라서 반복을 끝내요. 끝난 뒤에도 count는 4로 남아 있어요. 셋 중 하나라도 빠지면 반복이 아예 안 돌거나 끝나지 않아요." + NEWK + REAL, ("p3", "while"))

FS[0] = 28
o = [sec("w-trace")] + head(EB3, "재고가 0이 될 때까지 주문을 받아요", K3)
c2 = {"id": "c-w2", "lines": ["stock = 3", "while stock > 0:", "    stock -= 1", '    print(f"주문 받았어요. 남은 재고 {stock}")', 'print("품절이에요")'], "n": 2, "out": ["주문 받았어요. 남은 재고 2", "주문 받았어요. 남은 재고 1", "주문 받았어요. 남은 재고 0", "품절이에요"]}
c3 = {"id": "c-w3", "lines": ["stock = 0", "while stock > 0:", "    stock -= 1", '    print("주문 받았어요")', 'print("품절이에요")'], "n": 3, "out": ["품절이에요"]}
cw = cell_w(c2["lines"])
o += cell(c2, 96, T0, cw)
o += trace(1150, T0, [("stock", 130), ("> 0", 150), ("하는 일", 300)],
           [("3", "True", "1 빼고 찍기"), ("2", "True", "1 빼고 찍기"), ("1", "True", "1 빼고 찍기"), ("0", "False", "반복 끝")], 1, 70, 28, rid="wt-r", each=False, delay=160)
o.append(spot(2, target="wt-r3", pad=10, r=12))
T3 = 650
o += cell(c3, 96, T3, cw, sel=False, attrs=bi("rise", 3))
o.append(spot_off(3))
o.append(hl(96, T3, cw, 0, 2, "err", 3))
o.append(rtag(96, cw, ly(T3, 0.5), "처음부터 0 > 0은 False", RED, 3))
o.append(hl(96, T3, cw, 2, 2, "skip", 4))
o.append(rtag(96, cw, ly(T3, 2.5), "한 번도 실행하지 않아요", GRAY, 4))
o.append(caption("조건은 반복할 때마다 처음에 물어요.", 5, 960))
W("w-trace", o, "while은 들여쓴 줄을 실행하기 전에 매번 조건부터 물어요. 재고 3개에서 시작해 주문을 받을 때마다 하나씩 줄여요. 오른쪽 표처럼 3, 2, 1일 때는 조건이 True라서 주문을 받아요. 0이 되면 0 > 0이 False라서 반복을 끝내고 품절이에요를 찍어요. 아래 셀은 재고가 처음부터 0이에요. 조건을 처음 물을 때 이미 False라서 들여쓴 줄은 한 번도 실행하지 않아요." + REAL)

FS[0] = 36
o = [sec("w-inf")] + head(EB3, "값을 안 바꾸면 끝나지 않아요", RED)
c = {"id": "c-w5", "lines": ["count = 1", "while count <= 3:", "    print(count)"], "n": 5, "out": ["1", "1", "1", "1", "...  (1초 동안 17만 줄 넘게)", "KeyboardInterrupt:"]}
cw = 860
# the notebook toolbar above the cell, with Interrupt
o.append(f'<div style="position:absolute;left:96px;top:{T0}px;width:{cw}px;height:64px;background:#ECEAE3;border-radius:14px;display:flex;flex-direction:row;align-items:center;padding:0 22px;gap:24px">'
         + p(f"font-family:{MONO};font-size:22px;font-weight:700;color:{INK}", NB) + p(f"font-size:20px;color:{SUB}", "▷ Run All")
         + p(f"font-size:20px;font-weight:700;color:{RED};white-space:nowrap", "■ Interrupt", ' id="wi-int"') + p(f"font-size:20px;color:{SUB}", "↻ Restart") + '</div>')
TC = T0 + 96
stop = f'<div id="wi-stop" style="width:40px;height:40px;border-radius:50%;border:3px solid {RED};display:flex;align-items:center;justify-content:center"><div style="width:14px;height:14px;background:{RED};border-radius:2px"></div></div>'
o += cell(c, 96, TC, cw, gutter=stop, out_attrs={5: bi("rise", 4)})
o.append(hl(96, TC, cw, 2, 1, "err", 1))
o.append(rtag(96, cw, ly(TC, 2), "count += 1이 없어요", RED, 1))
o.append(tag(cx(96, 0) + tw("...  (1초 동안 17만 줄 넘게)") + 40, oy(TC, 3, 4), "count가 늘 1, 조건이 늘 True", RED, 2))
o.append(cursor(3, target="wi-stop"))
o.append(tag(96 + cw + 30, TC + 26, "■ 정지 버튼이나 위쪽 Interrupt", JP, 3))
o.append(cursor_off(4))
o.append(underline(4, cx(96, 0), cx(96, 18), oy(TC, 3, 5) + LH() / 2 - 2, RED))
o.append(tag(cx(96, 0) + tw("KeyboardInterrupt:") + 60, oy(TC, 3, 5), "멈췄다는 표시예요", RED, 4))
o.append(p(f"position:absolute;left:1300px;top:640px;font-size:28px;font-weight:700;color:{GRAY}", "터미널에서 uv run으로 돌렸다면", bi("rise", 5)))
for k, (lab, combo, col) in enumerate([("Windows", "Ctrl+C", WIN), ("Mac", "control+C", MAC)]):
    o.append(p(f"position:absolute;left:1300px;top:{708 + k * 96}px;width:140px;font-size:26px;font-weight:700;color:{col}", lab, bi("rise", 5)))
    o.append(keys(5, 1450, 694 + k * 96, combo, 26))
o.append(caption("while 안에 조건을 바꾸는 줄이 있는지 먼저 봐요.", 5))
W("w-inf", o, "while 안에서 조건의 값을 바꾸지 않으면 반복이 끝나지 않아요. 앞 장의 while에서 count += 1을 빼먹었어요. count가 계속 1이라 조건이 늘 True예요. 이걸 무한 반복이라고 해요. 노트북에서는 실행 중인 셀 왼쪽 버튼이 네모 정지 버튼으로 바뀌어요. 그 버튼이나 위쪽의 Interrupt를 누르면 멈추고 KeyboardInterrupt가 나와요. 09처럼 터미널에서 uv run으로 실행했다면 Ctrl+C, Mac은 control+C를 눌러요. 출력이 너무 많으면 VS Code가 느려질 수 있으니 바로 멈춰요. 실제로 1초 만에 멈췄는데 1이 17만 줄 넘게 찍혔어요. 슬라이드에는 앞의 네 줄과 마지막 줄만 옮겼어요.")

FS[0] = 34
o = [sec("w-vs")] + head(EB3, "for와 while은 이럴 때 써요", K3)
c = {"id": "c-w4", "lines": ["for i in range(1, 4):", "    print(i)", "i = 1", "while i <= 3:", "    print(i)", "    i += 1"], "n": 4, "out": ["1", "2", "3", "1", "2", "3"]}
cw = cell_w(c["lines"])
o += cell(c, 96, T0, cw)
o.append(hl(96, T0, cw, 0, 2, "mark", 1))
o.append(rtag(96, cw, ly(T0, 0.5), "2줄", BL, 1))
o.append(hl(96, T0, cw, 2, 4, "note", 2))
o.append(rtag(96, cw, ly(T0, 3.5), "4줄", OR, 2))
o += plain_rows(1000, T0, 824, [("언제", "횟수나 묶음이 정해졌을 때", "조건이 False가 될 때까지"), ("예", "메뉴 하나씩, 10번 반복", "돈이 남는 동안, 재고가 있는 동안"),
                                 ("멈춤", "값이 떨어지면 저절로", "값 바꾸기를 직접 적어야"), ("실수", "거의 없어요", "무한 반복")],
                [90, 330, 340], 3, 112, ["", "for", "while"], 28, [GRAY, BL, OR], step=False)
o.append(f'<div id="wv-stop" style="position:absolute;left:1000px;top:{T0 + 60 + 2 * 112}px;width:824px;height:112px"></div>')
o.append(spot(4, target="wv-stop", pad=4, r=12))
o.append(spot_off(5))
o.append(caption("둘 다 쓸 수 있으면 for가 짧고 안전해요.", 5))
W("w-vs", o, "횟수나 묶음이 정해져 있으면 for, 몇 번 돌지 모르면 while을 써요. 1부터 3까지 찍는 일은 for와 while 둘 다 할 수 있어요. for는 range가 숫자를 알아서 바꿔 줘서 두 줄이에요. while은 시작값과 값 바꾸기를 직접 적어서 네 줄이에요. 돈이 남는 동안, 재고가 있는 동안처럼 몇 번 돌지 모를 때 while을 써요. while은 값 바꾸기를 빼먹으면 앞 장처럼 끝나지 않으니 그 줄부터 확인해요." + REAL)

# ---------- part 4 ----------
ORD = ['orders = ["coffee", "cake", "latte", "tea", "cake"]', 'soldout = ["latte"]']
ORDERS = ["coffee", "cake", "latte", "tea", "cake"]
BRK = ["for o in orders:", "    if o in soldout:", '        print(f"{o} 품절, 주문을 멈춰요")', "        break", '    print(f"{o} 주문 받았어요")', 'print("끝")']
CNT = ["for o in orders:", "    if o in soldout:", '        print(f"{o} 품절, 건너뛰어요")', "        continue", '    print(f"{o} 주문 받았어요")', 'print("끝")']

FS[0] = 30
o = [sec("b-break")] + head(EB4, "break는 반복을 그 자리에서 끝내요", K4)
c = {"id": "c-b1", "lines": ORD + BRK, "n": 1, "out": ["coffee 주문 받았어요", "cake 주문 받았어요", "latte 품절, 주문을 멈춰요", "끝"]}
cw = cell_w(c["lines"], -60)
o += cell(c, 96, T0, cw)
o.append(hl(96, T0, cw, 3, 1, "note", 1))
o.append(tag(tx(96, [BRK[1]]), ly(T0, 3), "품절일 때만 멈추게 if 안에", OR, 1))
o.append(hl(96, T0, cw, 5, 1, "err", 2))
o.append(hl(96, T0, cw, 7, 1, "run", 2))
o.append(jump(96, T0, cw, 5, 7, RED, "for 밖으로", 2))
o += state_row(1234, 600, ORDERS, ["받음", "받음", "멈춤", "안 봄", "안 봄"], 3, "orders 다섯 개 중 셋만 봤어요", K4)
o.append(tag(1234, 800, "남은 tea, cake는 보지도 않아요", GRAY, 4, 26, False))
o.append(caption("break는 \"여기서 그만\". 남은 차례를 버리고 반복 아래 줄로 가요.", 5))
W("b-break", o, "break를 만나면 반복을 그 자리에서 끝내고 반복 아래 줄로 가요. 주문 리스트를 하나씩 받다가 품절 메뉴를 만나면 그만 받아요. orders에 다섯 주문이 있고, latte가 품절이에요. coffee와 cake는 품절이 아니라 주문 받았어요를 찍어요. latte에서 if가 True고, 품절이라고 찍은 뒤 break를 만나요. break는 빨간 화살표처럼 for 밖의 다음 줄, print 끝으로 가요. 뒤에 남은 tea와 cake는 보지도 않아요. break 아래의 주문 받았어요 줄도 실행하지 않아요. break를 if 없이 쓰면 첫 주문에서 바로 끝나서, 멈출 때를 if로 적어요." + NEWK + REAL, ("p4", "break와 continue"))

FS[0] = 30
o = [sec("b-continue")] + head(EB4, "continue는 이번 차례만 건너뛰고 계속 돌아요", K4)
c = {"id": "c-b2", "lines": CNT, "n": 2, "out": ["coffee 주문 받았어요", "cake 주문 받았어요", "latte 품절, 건너뛰어요", "tea 주문 받았어요", "cake 주문 받았어요", "끝"]}
cw = cell_w(c["lines"], -60)
o += cell(c, 96, T0, cw)
o.append(tag(tx(96, ["        continue"]) + 10, ly(T0, 3), "break만 바꿨어요", OR, 1))
o.append(hl(96, T0, cw, 0, 1, "run", 2))
o.append(jump(96, T0, cw, 3, 0, OR, "다음 주문", 2, 260))
o += state_row(1234, T0 + 380, ORDERS, ["받음", "받음", "멈춤", "안 봄", "안 봄"], 3, "break · 셀 [1]", RED)
o += state_row(1234, T0 + 590, ORDERS, ["받음", "받음", "건너뜀", "받음", "받음"], 4, "continue · 셀 [2]", OR)
o.append(caption("continue는 \"이번만 넘기기\". 아래 줄을 건너뛰고 다음 차례로 가요.", 5))
o = [x.replace(">        continue</p>", f'>        <span{MARK(1)} style="color:{OR};background:{ORBG};border-radius:6px">continue</span></p>', 1) if 'id="c-b2"' in x or ">        continue</p>" in x else x for x in o]
W("b-continue", o, "continue를 만나면 아래 줄을 건너뛰고 다음 차례로 가요. 앞 장과 같은 주문 리스트에서 break만 continue로 바꿨어요. latte에서 품절이라고 찍은 뒤 continue를 만나요. continue는 주황 화살표처럼 for 줄로 돌아가 다음 주문을 꺼내요. 그래서 latte의 주문 받았어요만 빠지고 tea와 cake는 받아요. 오른쪽에 두 결과를 나란히 놓았어요. break는 latte에서 끝나서 셋만 봤고, continue는 다섯을 모두 봤어요. 셀 [2]는 셀 [1]의 orders와 soldout을 그대로 써요." + REAL)

FS[0] = 30
o = [sec("b-jump")] + head(EB4, "화살표로 보면 어디로 가는지 보여요", K4)
c = {"id": "c-b3", "lines": ["for i in range(1, 6):", "    if i == 3:", "        break", "    print(i)", 'print("---")', "for i in range(1, 6):", "    if i == 3:", "        continue", "    print(i)"], "n": 3, "out": ["1", "2", "---", "1", "2", "4", "5"]}
cw = cell_w(c["lines"])
o += cell(c, 96, 200, cw)
o.append(hl(96, 200, cw, 2, 1, "err", 1))
o.append(jump(96, 200, cw, 2, 4, RED, "break", 1))
o.append(hl(96, 200, cw, 7, 1, "note", 2))
o.append(jump(96, 200, cw, 7, 5, OR, "continue", 2))
for row, (lbl, kind) in enumerate([("break", "b"), ("continue", "c")]):
    y = 230 + row * 330
    col_ = RED if kind == "b" else OR
    o.append(p(f"position:absolute;left:1100px;top:{y}px;font-family:{MONO};font-size:30px;font-weight:700;color:{col_}", lbl, bi("fade", row + 1)))
    for j in range(5):
        v = j + 1
        on = (v < 3) if kind == "b" else (v != 3)
        bc = GR if on else (col_ if v == 3 else "#D5D8DE")
        fc = GRBG if on else ((REDBG if kind == "b" else ORBG) if v == 3 else "#F1F0EC")
        o.append(p(f"position:absolute;left:{1100 + j * 145}px;top:{y + 56}px;width:130px;height:110px;border-radius:16px;border:3px solid {bc};background:{fc};font-family:{MONO};font-size:44px;font-weight:700;line-height:104px;text-align:center;color:{INK if on or v == 3 else FAINT}", str(v), bi("rise", row + 1)))
    o.append(p(f"position:absolute;left:1100px;top:{y + 190}px;width:724px;font-size:26px;font-weight:700;color:{SUB}", "3에서 반복 끝. 4, 5는 돌지도 않아요" if kind == "b" else "3만 건너뛰고 4, 5는 계속 돌아요", bi("fade", row + 1)))
o.append(caption("break 화살표는 반복 아래로, continue 화살표는 반복 맨 위로 가요.", 3, 960))
W("b-jump", o, "break는 반복 아래로 나가고, continue는 반복 맨 위로 돌아가요. 1부터 5까지 돌면서 3에서 break와 continue를 써요. 빨간 화살표의 break는 반복 아래 줄인 대시 줄로 바로 가요. 그래서 1, 2만 찍히고 4, 5는 돌지도 않아요. 주황 화살표의 continue는 for 줄로 돌아가 다음 숫자 4를 꺼내요. 3만 빠지고 1, 2, 4, 5가 찍혀요. 헷갈리면 이 두 화살표 방향을 떠올려요." + REAL)

FS[0] = 30
o = [sec("b-long")] + head(EB4, "continue는 else로 길게 쓸 수도 있어요", K4)
c = {"id": "c-b4", "lines": ["for o in orders:", "    if o in soldout:", '        print(f"{o} 품절, 건너뛰어요")', "    else:", '        print(f"{o} 주문 받았어요")', 'print("끝")'], "n": 4, "out": ["coffee 주문 받았어요", "cake 주문 받았어요", "latte 품절, 건너뛰어요", "tea 주문 받았어요", "cake 주문 받았어요", "끝"]}
cw = cell_w(c["lines"])
o += cell(c, 96, T0, cw)
o.append(hl(96, T0, cw, 3, 2, "mark", 1))
o.append(rtag(96, cw, ly(T0, 3.5), "else 안이라 8칸", BL, 1))
# the continue version beside it, quiet: no card
RX = 1010
FS[0] = 26
cc = {"id": "c-b4c", "lines": CNT[:5], "n": 2}
ccw = cell_w(cc["lines"], -40)
RY = 500
o.append(p(f"position:absolute;left:{RX}px;top:{RY}px;font-size:26px;font-weight:700;color:{OR}", "continue로 쓰면 · 셀 [2]", bi("rise", 2)))
o += cell(cc, RX, RY + 50, ccw, sel=False, attrs=bi("rise", 2))
o.append(hl(RX, RY + 50, ccw, 4, 1, "note", 3))
o.append(tag(RX + 87, RY + 50 + cell_h(cc) + 44, "주문 받기가 4칸, 한 단계 얕아요", OR, 3, 28, False))
o.append(tag(RX + 87, RY + 50 + cell_h(cc) + 96, "출력은 왼쪽과 똑같아요", GRAY, 3, 26, False))
o.append(caption("continue는 \"이 경우는 빼고\"를 맨 위에 적는 방법이에요.", 4, 960))
W("b-long", o, "continue 없이 17의 if, else로 써도 결과가 같아요. 품절이면 건너뛴다고 찍고, 아니면 else에서 주문을 받아요. 오른쪽은 셀 [2]의 continue 버전이에요. 차이는 모양이에요. continue는 건너뛸 경우를 맨 위에서 걸러 내서, 아래 할 일을 else 안에 넣지 않아도 돼요. 주문 받기가 여러 줄로 길어지면 들여쓰기가 한 단계 얕아서 읽기 쉬워요. 처음에는 if, else로 적어도 괜찮아요." + REAL)

FS[0] = 30
o = [sec("b-true")] + head(EB4, "while True와 break로 \"될 때까지\" 돌아요", K4)
c = {"id": "c-b5", "lines": ["left = 3", "n = 0", "while True:", "    if left == 0:", '        print("재고가 떨어졌어요")', "        break", "    left -= 1", "    n += 1", '    print(f"{n}번째 주문, 남은 재고 {left}")'], "n": 5, "out": ["1번째 주문, 남은 재고 2", "2번째 주문, 남은 재고 1", "3번째 주문, 남은 재고 0", "재고가 떨어졌어요"]}
cw = cell_w(c["lines"])
o += cell(c, 96, T0, cw)
o.append(underline(1, cx(96, 6) - 2, cx(96, 10) + 2, ly(T0, 2) + LH() / 2 - 4, K4))
o.append(rtag(96, cw, ly(T0, 2), "늘 True라 스스로는 끝나지 않아요", K4, 1))
o.append(hl(96, T0, cw, 5, 1, "err", 2))
o.append(jump(96, T0, cw, 5, 9, RED, "여기로만 나가요", 2))
o.append(ohl(96, T0, 9, 3, tw("재고가 떨어졌어요") + 30, "err", 3))
o.append(tag(cx(96, 0) + tw("1번째 주문, 남은 재고 2") + 60, oy(T0, 9, 3), "재고가 0이 되면 나가요", RED, 3))
o.append(caption("while True:를 쓰면 break가 나가는 문이에요.", 4, 960))
W("b-true", o, "while True:는 조건이 늘 True라서 안쪽의 break가 유일한 출구예요. 재고가 0이 되면 재고가 떨어졌어요를 찍고 break로 나가요. 화살표가 가리키는 마지막 줄 아래, 반복 밖으로 나가요. while left > 0으로도 쓸 수 있어요. 멈출 조건을 반복 중간에 확인하고 싶을 때나, 맞힐 때까지처럼 끝을 미리 정하기 어려울 때 이 모양을 써요. break를 빼먹으면 3파트의 무한 반복이 되니 꼭 확인해요." + REAL)

# ---------- part 5 ----------
FS[0] = 34
o = [sec("a-sum")] + head(EB5, "합계는 0에서 시작해 하나씩 더해요", K5)
c = {"id": "c-a1", "lines": ["prices = [4500, 5000, 6500, 4500]", "total = 0", "for p in prices:", "    total += p", "print(total)", "print(sum(prices))"], "n": 1, "out": ["20500", "20500"]}
cw = cell_w(c["lines"])
o += cell(c, 96, T0, cw, out_attrs={0: COUNT(3)})
o.append(hl(96, T0, cw, 1, 3, "mark", 1))
o.append(rtag(96, cw, ly(T0, 2), "원래 방법: 밖에서 0, 안에서 +=", BL, 1))
o += trace(1060, 545, [("p", 120), ("total += p", 280), ("total", 160)],
           [("", "", "0"), ("4500", "0 + 4500", "4500"), ("5000", "4500 + 5000", "9500"), ("6500", "9500 + 6500", "16000"), ("4500", "16000 + 4500", "20500")], 2, 62, 30, rid="as-r", each=False, delay=160)
o.append(hl(96, T0, cw, 5, 1, "run", 4))
o.append(rtag(96, cw, ly(T0, 5), "13의 sum()은 위 세 줄을 대신해요", GR, 4))
o.append(caption("쌓을 변수를 반복 밖에서 0으로 두고, 안에서 +=로 더해요.", 5))
W("a-sum", o, "합계는 반복 밖에서 0으로 두고 안에서 하나씩 더해 쌓아요. 오른쪽 표처럼 0에서 4500, 9500, 16000, 20500으로 늘어요. 13에서 배운 sum(prices)는 이 세 줄을 한 번에 해 주는 함수예요. 결과가 20500으로 같아요. 숫자 리스트의 합계는 sum을 쓰면 돼요. 다음 장부터는 sum처럼 한 줄로 되지 않는 일을 같은 모양으로 풀어요." + NEWK + REAL, ("p5", "쌓기와 겹친 반복"))

FS[0] = 30
o = [sec("a-count")] + head(EB5, "조건에 맞는 것을 세고 모아요", K5)
ca = {"id": "c-a2", "lines": ["n = 0", "for p in prices:", "    if p >= 5000:", "        n += 1", "print(n)", "print(prices.count(5000))"], "n": 2, "out": ["2", "1"]}
cb = {"id": "c-a4", "lines": ["big = []", "for p in prices:", "    if p >= 5000:", "        big.append(p)", "print(big)", "print(len(big))"], "n": 3, "out": ["[5000, 6500]", "2"]}
o.append(slots(["4500", "5000", "6500", "4500"], 96, T0, 200, 90, idx=False, attrs=bi("rise", 1), fs=34, states=["off", "on", "on", "off"], color=GR, bg=GRBG))
o.append(tag(96 + 4 * 210 + 30, T0 + 45, "5000 이상은 두 개", GR, 1))
TA = 380
o += cell(ca, 96, TA, 840)
o.append(hl(96, TA, 840, 3, 1, "run", 2))
o.append(tag(tx(96, ["        n += 1"]), ly(TA, 3), "세기", GR, 2))
o.append(tag(cx(96, 0) + 40, oy(TA, 6, 1), "count()는 5000과 같은 값만 세요", GRAY, 3, 26))
o += cell(cb, 984, TA, 840, sel=False, attrs=bi("rise", 4))
o.append(hl(984, TA, 840, 3, 1, "run", 4))
o.append(tag(tx(984, ["        big.append(p)"]), ly(TA, 3), "모으기", GR, 4))
o.append(tag(cx(984, 0) + tw("[5000, 6500]") + 40, oy(TA, 6, 0), "17의 골라 담기", GRAY, 5, 26))
o.append(tag(cx(984, 0) + 40, oy(TA, 6, 1), "모은 리스트의 len이 개수", GRAY, 5, 26))
o.append(caption("세기는 n += 1, 모으기는 append예요. 둘 다 if 안에 둬요.", 5))
W("a-count", o, "조건에 맞는 것은 if 안에서 n += 1로 세거나 append로 모아요. 가격이 5000원 이상인 메뉴가 몇 개인지 세요. n을 0으로 두고 조건이 True일 때만 1을 더해요. 5000과 6500, 두 개예요. 아래 줄의 13의 count는 5000과 같은 값 하나만 세서 1이 나와요. count는 5000 이상처럼 범위가 붙은 조건에는 못 써요. 오른쪽은 같은 조건으로 값을 모은 거예요. 17의 골라 담기 모양이에요. 모은 리스트의 len을 보면 개수도 알 수 있어요. 값도 필요하면 모으고, 개수만 필요하면 세요." + REAL)

FS[0] = 34
o = [sec("a-max")] + head(EB5, "가장 큰 값은 지금까지 1등과 비교해요", K5)
c = {"id": "c-a3", "lines": ["big = prices[0]", "for p in prices:", "    if p > big:", "        big = p", "print(big)", "print(max(prices), min(prices))"], "n": 4, "out": ["6500", "6500 4500"]}
cw = cell_w(c["lines"])
o += cell(c, 96, T0, cw)
o.append(hl(96, T0, cw, 0, 1, "mark", 1))
o.append(rtag(96, cw, ly(T0, 0), "0이 아니라 첫 값으로 시작", BL, 1))
o.append(hl(96, T0, cw, 2, 2, "run", 2))
o.append(rtag(96, cw, ly(T0, 2.5), "더 크면 바꾸기", GR, 2))
o += trace(1060, 545, [("p", 140), ("p > big", 200), ("big", 160)],
           [("", "", "4500"), ("4500", "False", "4500"), ("5000", "True", "5000"), ("6500", "True", "6500"), ("4500", "False", "6500")], 3, 62, 30, rid="am-r", each=False)
o.append(spot(4, target="am-r3", pad=8, r=12))
o.append(spot_off(5))
o.append(hl(96, T0, cw, 5, 1, "run", 5))
o.append(rtag(96, cw, ly(T0, 5), "13의 max()와 min()이 한 줄로", GR, 5))
o.append(caption("지금까지 가장 큰 값을 big에 두고, 더 큰 값을 만나면 바꿔요.", 5))
W("a-max", o, "지금까지 가장 큰 값을 big에 두고, 더 큰 값을 만나면 바꿔요. big에 리스트의 첫 값을 넣고 시작해요. 하나씩 꺼내 big보다 크면 big을 그 값으로 바꿔요. 오른쪽 표처럼 5000, 6500에서 바뀌고, 마지막 4500에서는 그대로예요. 0으로 시작하지 않는 이유는 값이 모두 음수일 때 0이 답으로 나와 버리기 때문이에요. 13의 max와 min은 이 반복을 한 줄로 해 줘요. 결과가 같아요." + REAL)

FS[0] = 32
o = [sec("n-gugu")] + head(EB5, "반복 안에 반복을 넣으면 표를 만들어요", K5)
c = {"id": "c-n1", "lines": ["for dan in range(2, 4):", "    for i in range(1, 4):", '        print(f"{dan} x {i} = {dan * i}")', '    print("---")'], "n": 5, "out": ["2 x 1 = 2", "2 x 2 = 4", "2 x 3 = 6", "---", "3 x 1 = 3", "3 x 2 = 6", "3 x 3 = 9", "---"]}
cw = cell_w(c["lines"])
o += cell(c, 96, 200, cw)
o.append(hl(96, 200, cw, 0, 1, "mark", 1))
o.append(rtag(96, cw, ly(200, 0), "바깥 · dan = 2, 3", BL, 1))
o.append(hl(96, 200, cw, 1, 2, "run", 2))
o.append(rtag(96, cw, ly(200, 1.5), "안쪽 · i = 1, 2, 3", GR, 2))
GX = 1180
o.append(grid([[f"{d}x{i}" for i in range(1, 4)] for d in range(2, 4)], GX, 520, 170, 90, states={(0, j): "on" for j in range(3)}, attrs=STAGGER(3, 120), fs=30, color=GR))
o.append(tag(GX, 470, "바깥이 한 번 돌 때 안쪽은 세 번", GR, 3, 28, False))
o.append(ohl(96, 200, 4, 0, tw("2 x 1 = 2") + 30, "run", 3, 3))
o.append(hl(96, 200, cw, 3, 1, "note", 4))
o.append(rtag(96, cw, ly(200, 3), "4칸, 단마다 한 번", OR, 4))
o.append(caption("바깥 2번 × 안쪽 3번 = 모두 6번 실행해요.", 5, 960))
W("n-gugu", o, "반복 안에 반복을 넣으면 바깥이 한 번 돌 때 안쪽이 처음부터 끝까지 돌아요. 17에서 if 안에 if를 넣은 것과 같아요. 바깥 for가 dan에 2를 넣으면 안쪽 for가 i를 1, 2, 3까지 다 돌아요. 그다음에 바깥이 3으로 바뀌고 안쪽이 다시 처음부터 돌아요. 시계의 시침이 한 칸 갈 때 분침이 한 바퀴 도는 것과 같아요. 그래서 2 곱하기 3, 모두 6줄이 찍혀요. 안쪽 print는 8칸, 바깥의 대시 줄은 4칸 들여써서 단마다 한 번씩 찍혀요." + REAL)

FS[0] = 30
o = [sec("n-2d")] + head(EB5, "14의 성적표를 행과 열 번호로 돌아요", K5)
c = {"id": "c-n2", "lines": ["scores = [[90, 85, 77],", "          [70, 95, 88],", "          [60, 75, 99]]", "for i in range(len(scores)):", "    for j in range(len(scores[i])):", "        if scores[i][j] < 70:", '            print(f"{i}행 {j}열: {scores[i][j]}점")'], "n": 6, "out": ["2행 0열: 60점"]}
cw = cell_w(c["lines"])
o += cell(c, 96, T0, cw)
o.append(hl(96, T0, cw, 3, 1, "mark", 1))
o.append(rtag(96, cw, ly(T0, 3), "바깥 i는 행 번호", BL, 1))
o.append(hl(96, T0, cw, 4, 1, "mark", 2))
o.append(rtag(96, cw, ly(T0, 4), "안쪽 j는 열 번호", BL, 2))
GX = 1300
o.append(grid([[90, 85, 77], [70, 95, 88], [60, 75, 99]], GX, 520, 150, 90, states={(2, 0): "hit"}, attrs=bi("rise", 1), fs=34, color=GR, rid="nd-"))
o.append(spot(3, target="nd-2-0", pad=10, r=16))
o.append(spot_off(4))
o.append(ohl(96, T0, 7, 0, tw("2행 0열: 60점") + 30, "err", 4))
o.append(tag(cx(96, 0) + tw("2행 0열: 60점") + 60, oy(T0, 7, 0), "scores[2][0], 14의 [행][열] 순서", RED, 4))
o.append(caption("2차원 리스트는 바깥 for가 행, 안쪽 for가 열이에요.", 5))
W("n-2d", o, "2차원 리스트는 바깥 for가 행 번호, 안쪽 for가 열 번호를 돌아요. 14에서는 for row in scores로 행을 통째로 꺼냈어요. 이번에는 번호도 알고 싶어서 range(len())을 두 번 겹쳤어요. 안쪽 길이는 그 행의 길이 len(scores[i])예요. 70점 아래인 칸을 찾으면 몇 행 몇 열인지 찍어요. 2행 0열의 60점 하나예요. 14에서 본 [행][열] 순서 그대로예요." + REAL)

FS[0] = 30
o = [sec("n-break")] + head(EB5, "안쪽 break는 안쪽 반복만 멈춰요", K5)
c = {"id": "c-n3", "lines": ["for row in scores:", "    for s in row:", "        if s < 80:", '            print("80점 아래", s, "찾음")', "            break", '    print("이 행 확인 끝", row)'], "n": 7, "out": ["80점 아래 77 찾음", "이 행 확인 끝 [90, 85, 77]", "80점 아래 70 찾음", "이 행 확인 끝 [70, 95, 88]", "80점 아래 60 찾음", "이 행 확인 끝 [60, 75, 99]"]}
cw = cell_w(c["lines"])
o += cell(c, 96, T0, cw)
o.append(hl(96, T0, cw, 4, 1, "err", 1))
o.append(rtag(96, cw, ly(T0, 4), "안쪽 for만 끝", RED, 1))
o.append(hl(96, T0, cw, 5, 1, "run", 2))
o.append(rtag(96, cw, ly(T0, 5), "바깥 for는 다음 행으로", GR, 2))
GX = 1240
SC = [[90, 85, 77], [70, 95, 88], [60, 75, 99]]
st = {(0, 2): "hit", (1, 0): "hit", (2, 0): "hit", (1, 1): "off", (1, 2): "off", (2, 1): "off", (2, 2): "off"}
o.append(grid(SC, GX, 600, 150, 80, states=st, attrs=bi("rise", 3), fs=32))
o.append(p(f"position:absolute;left:{GX}px;top:548px;font-size:26px;font-weight:700;color:{SUB}", "빨강은 찾은 값, 회색은 안 본 값", bi("fade", 3)))
o.append(caption("행마다 처음 찾은 값에서 멈추고, 다음 행은 계속 확인해요.", 4, 960))
W("n-break", o, "break는 자기를 감싼 가장 가까운 반복 하나만 끝내요. 행마다 80점 아래인 값을 처음 찾으면 break해요. 첫 행은 77에서 안쪽 for가 끝나고, 바깥 for의 이 행 확인 끝을 찍은 뒤 다음 행으로 가요. 둘째 행은 첫 칸 70에서 바로 멈춰서 95, 88은 보지 않아요. 오른쪽 그림의 회색 칸이 보지 않은 값이에요. 바깥까지 다 멈추는 방법은 이번 챕터에서 다루지 않아요." + REAL)

# ---------- part 6 ----------
FS[0] = 28
o = [sec("t-remove")] + head(EB6, "돌면서 같은 리스트를 지우면 하나를 놓쳐요", RED)
c1 = {"id": "c-t1", "lines": ['orders = ["tea", "tea", "coffee", "tea", "cake"]', "for o in orders:", '    if o == "tea":', "        orders.remove(o)", "print(orders)"], "n": 1, "out": ["['coffee', 'tea', 'cake']"]}
c2 = {"id": "c-t2", "lines": ['orders = ["tea", "tea", "coffee", "tea", "cake"]', "keep = []", "for o in orders:", '    if o != "tea":', "        keep.append(o)", "print(keep)"], "n": 2, "out": ["['coffee', 'cake']"]}
cw = cell_w(c1["lines"])
o += cell(c1, 96, T0, cw)
o.append(hl(96, T0, cw, 3, 1, "err", 1))
o.append(underline(2, cx(96, 11) - 2, cx(96, 16) + 2, oy(T0, 5, 0) + LH() / 2 - 2, RED))
o.append(tag(cx(96, 0) + tw(c1["out"][0]) + 60, oy(T0, 5, 0), "tea가 하나 남았어요", RED, 2))
PX = 1180
o.append(p(f"position:absolute;left:{PX}px;top:{T0}px;font-size:26px;font-weight:700;color:{RED}", "0번 tea를 지우면 뒤가 한 칸씩 당겨져요", bi("fade", 3)))
o.append(slots(["tea", "tea", "coffee", "tea", "cake"], PX, T0 + 44, 116, 70, attrs=bi("rise", 3), fs=24, states=[(RED, REDBG), "on", "on", "on", "on"], color=GRAY, bg="#FFFFFF"))
o.append(slots(["tea", "coffee", "tea", "cake"], PX, T0 + 190, 116, 70, attrs=bi("rise", 3), fs=24, states=["on", (OR, ORBG), "on", "on"], color=GRAY, bg="#FFFFFF"))
o.append(p(f"position:absolute;left:{PX}px;top:{T0 + 300}px;width:644px;font-size:26px;font-weight:700;line-height:1.5;color:{SUB}", "for는 다음 차례인 1번 coffee로 가서 당겨진 tea를 못 봐요", bi("fade", 3)))
T2 = 600
o += cell(c2, 96, T2, cw, sel=False, attrs=bi("rise", 4))
o.append(hl(96, T2, cw, 4, 1, "run", 4))
o.append(tag(tx(96, ["        keep.append(o)"]), ly(T2, 4), "남길 것만 새 리스트에 (17의 골라 담기)", GR, 4))
o.append(caption("돌고 있는 리스트는 지우지 않아요. 새 리스트에 모아요.", 5, 960))
W("t-remove", o, "돌고 있는 리스트를 지우면 당겨진 값을 건너뛰어서 하나를 놓쳐요. 주문에서 tea를 모두 지우려고 돌면서 remove했어요. 그런데 tea 하나가 남았어요. 0번 tea를 지우면 뒤의 값이 한 칸씩 앞으로 당겨져서 둘째 tea가 0번 자리로 와요. for는 이미 0번을 봤으니 다음 차례인 1번으로 넘어가요. 오류가 나지 않아서 놓치기 쉬워요. 원래 리스트는 그대로 두고 남길 것만 새 리스트에 모아요." + NEWK + REAL, ("p6", "함정과 실습"))

FS[0] = 26
o = [sec("t-indent")] + head(EB6, "들여쓰기 한 단계 차이로 결과가 달라져요", RED)
cs = [("c-t3", ["total = 0", "for p in [4500, 5000, 6500]:", "    total += p", "    print(total)"], 3, ["4500", "9500", "16000"], "print가 for 안", "돌 때마다 찍어요", 3, "run", GR),
      ("c-t4", ["total = 0", "for p in [4500, 5000, 6500]:", "    total += p", "print(total)"], 4, ["16000"], "print가 for 밖", "다 돈 뒤 한 번", 3, "mark", BL),
      ("c-t5", ["for p in [4500, 5000, 6500]:", "    total = 0", "    total += p", "print(total)"], 5, ["6500"], "total = 0이 for 안", "돌 때마다 0으로 돌아가요", 1, "err", RED)]
for i, (cid, lines, n_, out, t_, d, li, kind, col) in enumerate(cs):
    x = 96 + i * 584
    o += cell({"id": cid, "lines": lines, "n": n_, "out": out}, x, T0, 560, sel=i == 0, attrs=bi("rise", i + 1))
    o.append(hl(x, T0, 560, li, 1, kind, i + 1))
    o.append(p(f"position:absolute;left:{x + 87}px;top:590px;width:470px;font-size:36px;font-weight:700;color:{col}", e(t_), bi("rise", i + 1)))
    o.append(p(f"position:absolute;left:{x + 87}px;top:650px;width:470px;font-size:30px;line-height:1.5;color:{SUB}", e(d), bi("rise", i + 1)))
o.append(caption("쌓을 변수는 for 위에서 0으로, 결과는 for 아래에서 찍어요.", 4))
W("t-indent", o, "들여쓰기 한 단계 차이로 결과가 달라지고, 셋 다 오류는 나지 않아요. 첫째는 print가 for 안이라 돌 때마다 지금까지의 합계를 찍어요. 둘째는 print를 for 밖으로 뺐어요. 다 돈 뒤에 16000을 한 번만 찍어요. 셋째는 total = 0을 for 안에 넣었어요. 돌 때마다 0으로 돌아가서 마지막 가격 6500만 남아요. 오류가 없어서 결과를 보고 찾아야 해요. 쌓을 변수는 반복 위, 결과는 반복 아래가 기본이에요." + REAL)

FS[0] = 32
o = [sec("t-range")] + head(EB6, "range(len())에 1을 더하면 칸을 넘어가요", RED)
c6 = {"id": "c-t6", "lines": [MENUS, "for i in range(len(menus) + 1):", "    print(menus[i])"], "n": 6, "out": ["coffee", "latte", "cake", "IndexError: list index out of range"]}
c7 = {"id": "c-t7", "lines": ["print(list(range(1, 5)))", "print(list(range(len(menus))))"], "n": 7, "out": ["[1, 2, 3, 4]", "[0, 1, 2]"]}
cw = cell_w(c6["lines"])
o += cell(c6, 96, T0, cw)
o.append(underline(1, cx(96, 26) - 2, cx(96, 29) + 2, ly(T0, 1) + LH() / 2 - 4, RED))
o.append(rtag(96, cw, ly(T0, 1), "0, 1, 2, 3", RED, 1))
o.append(underline(2, cx(96, 0), cx(96, 10), oy(T0, 3, 3) + LH() / 2 - 2, RED))
o.append(shake(2, "c-t6"))
o.append(tag(cx(96, 0) + tw(c6["out"][3]) + 50, oy(T0, 3, 3), "없는 3번 칸", RED, 2))
SX = 1180
o.append(slots(["coffee", "latte", "cake"], SX, 380, 140, 80, attrs=bi("rise", 2), fs=24, color=K2, bg=K2BG))
o.append(p(f"position:absolute;left:{SX + 3 * 150}px;top:420px;width:140px;height:80px;border-radius:14px;border:3px dashed {RED};font-size:24px;font-weight:700;line-height:74px;text-align:center;color:{RED}", "3번 없음", bi("rise", 2)))
T7 = 640
o += cell(c7, 96, T7, cw, sel=False, attrs=bi("rise", 3))
o.append(tag(cx(96, 0) + tw("[1, 2, 3, 4]") + 50, oy(T7, 2, 0), "1부터 5까지는 range(1, 6)", GRAY, 3, 26))
o.append(tag(cx(96, 0) + tw("[1, 2, 3, 4]") + 50, oy(T7, 2, 1), "딱 맞는 번호", K2, 3, 26))
o.append(caption("IndexError가 나면 range의 끝 숫자부터 봐요.", 4, 960))
W("t-range", o, "range(len(리스트))가 이미 마지막 번호까지 딱 맞아서, 1을 더하면 없는 칸을 꺼내요. menus는 3칸이라 번호는 0, 1, 2이고 len은 3이에요. 1을 더하면 3번 칸을 꺼내려다 IndexError가 나요. 오류가 나기 전까지 coffee, latte, cake는 찍혀요. 반대로 1부터 5까지 돌고 싶은데 range(1, 5)라고 적으면 4에서 끝나요. 끝 숫자는 늘 빠진다는 2파트의 규칙을 떠올려요." + REAL)

FS[0] = 26
o = [sec("x-stock")] + head(EB6, "재고가 모자랄 때까지 주문을 받아요", K6)
c = {"id": "c-x1", "lines": ["stock = 5", "orders = [2, 1, 3, 1]", "sold = 0", "i = 0", "while i < len(orders):", "    want = orders[i]", "    if want > stock:", '        print(f"{i + 1}번 손님 {want}잔: 재고가 {stock}잔뿐이에요")', "        break", "    stock -= want", "    sold += want", '    print(f"{i + 1}번 손님 {want}잔, 남은 재고 {stock}")', "    i += 1", 'print(f"판매 {sold}잔, 남은 재고 {stock}")'],
     "n": 8, "out": ["1번 손님 2잔, 남은 재고 3", "2번 손님 1잔, 남은 재고 2", "3번 손님 3잔: 재고가 2잔뿐이에요", "판매 3잔, 남은 재고 2"]}
cw = cell_w(c["lines"], -40)
o += cell(c, 96, 196, cw)
o.append(hl(96, 196, cw, 4, 1, "mark", 1))
o.append(rtag(96, cw, ly(196, 4), "손님이 남은 동안", BL, 1))
o.append(hl(96, 196, cw, 6, 3, "err", 2))
o.append(rtag(96, cw, ly(196, 7), "재고가 모자라면 멈춤", RED, 2))
o.append(hl(96, 196, cw, 12, 1, "mark", 1))
o.append(tag(tx(96, ["    i += 1"]), ly(196, 12), "다음 손님", BL, 1, 26))
o += trace(1290, 560, [("손님", 90), ("want", 90), ("stock", 110), ("", 110)],
           [("1번", "2", "5→3", "팔아요"), ("2번", "1", "3→2", "팔아요"), ("3번", "3", "2", "break")], 3, 70, 28, rid="xs-r", each=False, delay=160)
o.append(spot(4, target="xs-r2", pad=8, r=12))
o.append(spot_off(5))
o.append(caption("멈출 조건이 두 개면 하나는 while에, 하나는 if와 break로 적어요.", 5, 970))
W("x-stock", o, "멈출 이유가 두 가지면 하나는 while 조건에, 하나는 if와 break로 적어요. 재고 5잔으로 손님 주문을 차례로 받아요. 손님이 원하는 잔 수는 orders 리스트에 있어요. while은 i가 손님 수보다 작은 동안 돌아요. 원하는 잔 수가 재고보다 많으면 재고가 모자란다고 알리고 break해요. 아니면 재고에서 빼고 판매에 더하고, i를 1 늘려 다음 손님으로 가요. 3번 손님은 3잔을 원하는데 2잔뿐이라 멈춰요. 번호 i는 0부터라 손님에게는 i + 1로 보여 줘요." + REAL)

FS[0] = 28
o = [sec("x-soldout")] + head(EB6, "처음 품절이 나오면 주문을 멈춰요", K6)
c = {"id": "c-x2", "lines": ['stock = {"coffee": 2, "latte": 1, "cake": 3}', 'orders = ["coffee", "latte", "coffee", "latte", "cake"]', "for o in orders:", "    if stock[o] == 0:", '        print(f"{o} 품절이에요. 주문을 멈춰요")', "        break", "    stock[o] -= 1", '    print(f"{o} 나갔어요. 남은 수 {stock[o]}")', "print(stock)"],
     "n": 9, "out": ["coffee 나갔어요. 남은 수 1", "latte 나갔어요. 남은 수 0", "coffee 나갔어요. 남은 수 0", "latte 품절이에요. 주문을 멈춰요", "{'coffee': 0, 'latte': 0, 'cake': 3}"]}
cw = cell_w(c["lines"], -40)
o += cell(c, 96, T0, cw)
o.append(hl(96, T0, cw, 3, 3, "err", 1))
o.append(rtag(96, cw, ly(T0, 4), "품절이면 break", RED, 1))
o.append(hl(96, T0, cw, 6, 1, "mark", 2))
o.append(rtag(96, cw, ly(T0, 6), "15처럼 값 바꾸기", BL, 2))
o += state_row(1234, 640, ["coffee", "latte", "coffee", "latte", "cake"], ["나감", "나감", "나감", "멈춤", "안 봄"], 3, "다섯째 cake는 재고가 있어도 안 봐요", K6)
o.append(caption("break를 continue로 바꾸면 품절만 건너뛰고 cake도 받아요.", 4, 960))
W("x-soldout", o, "처음 품절이 나오면 break로 주문을 그만 받아요. 메뉴별 재고 딕셔너리와 주문 리스트가 있어요. 주문을 하나씩 꺼내 재고가 0인지 물어요. 0이 아니면 15에서 배운 대로 stock[o] -= 1로 재고를 줄여요. latte는 둘째 주문에서 마지막 하나가 나가 0이 됐어요. 넷째 주문이 다시 latte라서 품절이에요를 찍고 break해요. 그래서 다섯째 cake는 재고가 있어도 받지 않았어요. break를 continue로 바꿔 실행해 보면 cake까지 받는 걸 확인할 수 있어요." + REAL)

FS[0] = 34
o = [sec("x-gugu")] + head(EB6, "구구단 표를 한 번에 찍어요", K6)
c = {"id": "c-x3", "lines": ["for dan in range(2, 10):", '    print(f"{dan}단", end=" ")', "    for i in range(1, 10):", '        print(f"{dan * i:>3}", end="")', "    print()"], "n": 10,
     "out": ["2단   2  4  6  8 10 12 14 16 18", "3단   3  6  9 12 15 18 21 24 27", "4단   4  8 12 16 20 24 28 32 36", "5단   5 10 15 20 25 30 35 40 45", "6단   6 12 18 24 30 36 42 48 54", "7단   7 14 21 28 35 42 49 56 63", "8단   8 16 24 32 40 48 56 64 72", "9단   9 18 27 36 45 54 63 72 81"], "wide": True}
cw = cell_w(c["lines"])
o += cell(c, 96, 196, cw)
for k, (i, kind, t_, col) in enumerate([(1, "mark", 'end=" "로 줄을 안 바꿔요 (13)', BL), (3, "run", ">3은 3칸 오른쪽 맞춤 (13)", GR), (4, "note", "print()는 줄만 바꿔요", OR)]):
    o.append(lspot(k + 1, 96 + 85, 196, cw - 85, 20 + 5 * LH(), 196 + 10 + i * LH(), LH(), bar=col))
    o.append(rtag(96, cw, ly(196, i), t_, col, k + 1))
o.append(lspot_off(4))
o.append(f'<div id="xg-row" style="position:absolute;left:{96 + 93}px;top:{196 + 20 + 5 * LH() + 10:.0f}px;width:{tw("2단   2  4  6  8 10 12 14 16 18") + 140:.0f}px;height:{LH():.0f}px"></div>')
o.append(spot(4, target="xg-row", pad=8, r=10))
o.append(tag(cx(96, 0) + tw("2단   2  4  6  8 10 12 14 16 18") + 180, oy(196, 5, 0), "안쪽 for가 채운 한 줄", GR, 4))
o.append(spot_off(5))
o.append(caption("안쪽 for는 한 줄을, 바깥 for는 줄 수를 맡아요.", 5, 970))
W("x-gugu", o, "안쪽 for는 한 줄을 채우고, 바깥 for는 줄 수를 맡아요. 5파트의 겹친 반복으로 2단부터 9단까지 표를 찍어요. 바깥 for는 단, 안쪽 for는 곱하는 수예요. 줄 앞에 몇 단인지 찍고, 13에서 배운 end로 줄을 바꾸지 않아요. 안쪽에서 곱한 값을 3칸 오른쪽 맞춤으로 이어 찍어서 칸이 맞아요. 안쪽 for가 끝나면 괄호만 있는 print()로 줄을 바꿔요. print()는 아무것도 찍지 않고 줄만 바꿔요. 출력의 한글은 영어 두 칸 너비로 그렸어요." + REAL)

FS[0] = 30
o = [sec("x-guess")] + head(EB6, "숫자 맞히기, 맞히면 멈춰요", K6)
c = {"id": "c-x4", "lines": ["answer = 37", "guesses = [50, 25, 37, 40]", "tries = 0", "for g in guesses:", "    tries += 1", "    if g == answer:", '        print(f"{g}: 정답이에요. {tries}번 만에 맞혔어요")', "        break", "    elif g > answer:", '        print(f"{g}: 더 작아요")', "    else:", '        print(f"{g}: 더 커요")'],
     "n": 11, "out": ["50: 더 작아요", "25: 더 커요", "37: 정답이에요. 3번 만에 맞혔어요"]}
cw = cell_w(c["lines"], -40)
o += cell(c, 96, T0, cw)
o.append(hl(96, T0, cw, 5, 3, "run", 1))
o.append(rtag(96, cw, ly(T0, 6), "맞히면 break", GR, 1))
o.append(hl(96, T0, cw, 8, 4, "mark", 2))
o.append(rtag(96, cw, ly(T0, 9.5), "17의 elif로 힌트", BL, 2))
o += state_row(1300, 700, ["50", "25", "37", "40"], ["받음", "받음", "멈춤", "안 봄"], 3, "넷째 추측 40은 보지 않아요", K6, 120, 118, 30)
o.append(caption("guesses를 바꾸면 끝까지 못 맞히고 힌트만 찍혀요.", 4, 960))
W("x-guess", o, "17의 elif로 힌트를 주고, 맞히면 break로 끝내요. 입력은 아직 배우지 않아서 추측을 리스트에 미리 적었어요. 추측마다 시도 횟수를 1 늘리고 17의 if, elif, else로 비교해요. 같으면 정답이라고 찍고 break해요. 크면 더 작다, 작으면 더 크다고 힌트를 줘요. 셋째 추측 37에서 맞혀서 넷째 40은 보지 않아요. guesses를 [10, 90, 50]처럼 바꿔 끝까지 못 맞히는 경우도 실행해 봐요." + REAL)

# ---------- summary ----------
o = [sec("trouble")] + head("정리", "막히면 오류의 마지막 줄을 봐요", RED)
tr = [("셀이 끝나지 않고 출력이 계속 나와요", "while 조건이 늘 True예요", "■ 또는 Interrupt, 값 바꾸기 줄 넣기"),
      ("KeyboardInterrupt", "직접 멈춘 표시라 오류가 아니에요", "값 바꾸기 줄 넣기"),
      ("IndexError: list index out of range", "range(len(xs) + 1)처럼 칸을 넘었어요", "range(len(xs))"),
      ("1부터 5까지 도는데 4에서 끝나요", "range의 끝 숫자는 빠져요", "range(1, 6)"),
      ("지웠는데 하나가 남아요", "돌고 있는 리스트를 remove했어요", "새 리스트에 append"),
      ("합계가 마지막 값만 나와요", "total = 0을 for 안에 넣었어요", "for 위로 옮기기"),
      ("바깥 반복이 멈추지 않아요", "break는 가장 가까운 반복 하나만 끝내요", "어느 for 안인지 보기")]
o.append(f'<div{bi("fade", 1)} style="position:absolute;left:96px;top:208px;width:1728px;height:48px;display:flex;flex-direction:row;gap:28px;align-items:center;border-bottom:3px solid {INK}">'
         + p(f"width:640px;padding-left:76px;font-size:24px;font-weight:700;color:{GRAY}", "이럴 때") + p(f"width:600px;font-size:24px;font-weight:700;color:{GRAY}", "까닭") + p(f"flex:1;font-size:24px;font-weight:700;color:{GRAY}", "이렇게") + '</div>')
for i, (q, a_, cmd) in enumerate(tr):
    o.append(f'<div{bi("rise", 1 + (0 if i < 2 else 1 if i < 4 else 2))}{DELAY((i if i < 2 else i - 2 if i < 4 else i - 4) * 90)} style="position:absolute;left:96px;top:{262 + i * 96}px;width:1728px;height:96px;display:flex;flex-direction:row;gap:28px;align-items:center;border-bottom:2px solid {LINE}">'
             + p(f"width:48px;flex:none;font-size:30px;font-weight:900;color:{RED};text-align:center", str(i + 1))
             + p(f"width:564px;flex:none;{'font-family:' + MONO + ';font-size:24px;' if q.isascii() else 'font-size:26px;'}font-weight:700;color:{INK}", e(q))
             + p(f"width:600px;flex:none;font-size:25px;color:{SUB}", e(a_))
             + p(f"flex:1;{'font-family:' + MONO + ';font-size:24px;' if cmd.isascii() else 'font-size:25px;'}font-weight:700;color:{INK}", e(cmd)) + '</div>')
o.append(caption("결과가 이상하면 반복 안에 print를 넣어 값이 어떻게 바뀌는지 찍어 봐요.", 4, 960))
W("trouble", o, "결과가 이상하면 반복 안에 print를 넣어 값이 바뀌는 모습을 찍어 봐요. 1번과 2번은 무한 반복이에요. 정지 버튼으로 멈추고 값 바꾸기 줄을 넣어요. KeyboardInterrupt는 내가 멈춘 표시라 오류가 아니에요. 3번과 4번은 range의 끝 숫자 문제예요. 5번부터 7번은 오류 없이 결과만 이상한 경우예요. 반복 안에 print를 넣어 변수가 어떻게 바뀌는지 찍어 보면 원인이 보여요.", ("trouble", "정리"))

o = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>']
cheat = [("range(1, 6)", "1부터 5까지, 끝은 빠져요", K2), ("for i in range(n):", "n번 반복", K2), ("enumerate(xs, 1)", "번호와 값을 같이", K2), ("while 조건:", "True인 동안 반복", K3),
         ("break", "반복을 바로 끝내기", K4), ("continue", "이번 차례만 넘기기", K4), ("total += p", "0에서 시작해 쌓기", K5), ("for 안의 for", "표 만들기, 2차원 리스트", K5)]
for i, (k, d, col) in enumerate(cheat):
    x, y = 96 + (i // 4) * 888, 200 + (i % 4) * 116
    o.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:840px;height:116px;display:flex;flex-direction:row;align-items:center;gap:28px;border-bottom:2px solid {LINE}">'
             + f'<div style="width:12px;height:56px;flex:none;border-radius:6px;background:{col}"></div>'
             + p(f"width:380px;flex:none;font-family:{MONO if k.isascii() else SANS};font-size:32px;font-weight:700;color:{col};white-space:pre", e(k)) + p(f"flex:1;font-size:30px;font-weight:700;color:{INK}", e(d)) + '</div>')
o.append(p(f"position:absolute;left:96px;top:740px;width:1728px;font-size:40px;font-weight:700;line-height:1.5;color:{INK}", "횟수를 알면 for, 조건만 알면 while이에요."))
o.append(p(f"position:absolute;left:96px;top:810px;width:1728px;font-size:40px;font-weight:700;line-height:1.5;color:{INK}", "while에는 시작값, 조건, 값 바꾸기 세 가지가 꼭 있어야 해요."))
o.append(p(f"position:absolute;left:96px;top:910px;width:1728px;font-size:28px;font-weight:700;color:{GRAY}", "다음 챕터 19에서는 여러 줄을 함수로 묶고 이름을 붙여요."))
W("cheatsheet", o, "이번 챕터에서 쓴 반복 모양을 한 장에 모았어요. range는 끝 숫자가 빠져요. 정한 횟수는 for와 range, 번호와 값은 enumerate, 조건이 맞는 동안은 while이에요. break는 반복을 끝내고, continue는 이번 차례만 넘겨요. 합계, 개수, 최댓값은 반복 밖에서 시작값을 두고 안에서 쌓아요. 17과 18로 제어문을 마쳤어요. 이 장을 노트북 마크다운 셀에 정리해 두고 복습할 때 같이 봐요.")

# ---------- toc ----------
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
parts = [(K1, "왜 필요한가", "몇 번 돌지 모르는 장면, for와 while 그림, 가장 짧은 while", "w-why", "w-min"),
         (K2, "range와 번호", "range(5), 시작과 끝과 간격, for i in range, range(len()), enumerate", "r-range", "r-enum"),
         (K3, "while", "묻기, 실행, 값 바꾸기, 재고 줄이기, 무한 반복과 멈추는 법, for와 비교", "w-shape", "w-vs"),
         (K4, "break와 continue", "같은 주문으로 break와 continue, 점프 화살표, else로 길게 쓰기, while True", "b-break", "b-true"),
         (K5, "쌓기와 겹친 반복", "합계, 세기와 모으기, 최댓값, 구구단, 2차원 리스트, 안쪽 break", "a-sum", "n-break"),
         (K6, "함정과 실습", "돌면서 지우기, 들여쓰기, range 끝, 재고, 품절, 구구단 표, 숫자 맞히기", "t-remove", "x-guess")]
TOC_NOTE = "여섯 파트를 차례로 보고, 막히면 끝의 두 장을 봐요. 1파트는 while이 왜 필요한지와 큰 그림, 2파트는 range와 번호예요. 3파트는 while 모양과 무한 반복, 4파트는 같은 주문 리스트로 break와 continue를 비교해요. 5파트는 합계, 개수, 최댓값을 직접 쌓고 sum, max와 비교한 뒤 반복을 겹쳐요. 6파트는 함정과 카페 실습이에요. 파트마다 새 커널에서 위에서부터 차례로 실행해요."

DECK_TITLE = "제어문 2 (반복 제어 while, break)"
t = [f'<section id="toc" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>']
for i, (col, h, s, a, b) in enumerate(parts):
    x, y = 96 + (i // 3) * 888, 210 + (i % 3) * 210
    t.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:840px;height:210px;display:flex;flex-direction:row;gap:28px;align-items:flex-start;padding-top:28px;border-top:2px solid {LINE}">'
             + p(f"width:60px;flex:none;font-size:64px;font-weight:900;line-height:1;color:{col}", str(i + 1))
             + '<div style="flex:1;display:flex;flex-direction:column;gap:10px">'
             + '<div style="display:flex;flex-direction:row;align-items:baseline;gap:20px">' + p(f"flex:1;font-size:34px;font-weight:700;color:{INK}", e(h)) + p(f"font-size:26px;font-weight:700;color:{GRAY};white-space:nowrap", f"{page[a]}–{page[b]}쪽") + '</div>'
             + p(f"font-size:25px;line-height:1.5;color:{SUB}", e(s)) + '</div></div>')
t.append(p(f"position:absolute;left:96px;top:880px;width:1728px;font-size:28px;color:{SUB}", f"{page['ready']}쪽은 노트북 준비, {page['trouble']}–{page['cheatsheet']}쪽은 막힐 때와 한 장 요약이에요."))
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
