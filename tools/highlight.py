"""Highlight helpers shared by every chapter's tools/gen.py. How to use them: tools/HIGHLIGHT.md.

Import from a chapter's gen.py:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tools"))
    from highlight import *

The player (tools/build_player.js) runs them. export.js and check.js ignore them, so the PDF shows the
slide's plain layout: spot and cursor boxes are empty, drawn lines are fully drawn.
"""

# Same meaning as the code-line tints: green run, gray skip, red error, blue mark, orange note.
GR, GRAY, RED, BL, OR = "#1F8A4C", "#6A7180", "#A33131", "#2459C9", "#B26A00"


def TYPE(order):
    """Old: letter-by-letter typing. Not in the guidelines any more (too many clicks per slide). Kept only because
    01-03 still call it; delete it and the player's 'type' kind once those decks drop it."""
    return f' data-build-in="type order {order}"'


def _box(kind, order, x, y, w, h, target, extra=""):
    t = f' data-target="{target}"' if target else ""
    return f'<div data-build-in="{kind} order {order}"{t}{extra} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px"></div>'


def spot(order, x=0, y=0, w=1, h=1, target=None, pad=12, r=18, dim=None):
    """Dims the whole slide except one box. Give the box (x, y, w, h) or the id of an element (target).
    The next spot on the same slide moves the hole there; spot_off clears it."""
    extra = f' data-pad="{pad}" data-r="{r}px"' + (f' data-dim="{dim}"' if dim is not None else "")
    return _box("spot", order, x, y, w, h, target, extra)


def spot_off(order):
    return _box("spot-off", order, 0, 0, 1, 1, None)


def cursor(order, x=0, y=0, target=None, click=True):
    """Moves a mouse pointer to the middle of a box or element. click=True adds a ripple when it arrives."""
    return _box("click" if click else "cursor", order, x - 1, y - 1, 2, 2, target)


def cursor_off(order):
    return _box("cursor-off", order, 0, 0, 1, 1, None)


def _svg(order, inner, color, width):
    return (f'<svg data-build-in="draw order {order}" viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;'
            f'pointer-events:none;overflow:visible"><g fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round">{inner}</g></svg>')


def ring(order, x, y, w, h, color=RED, width=6):
    """A pen-drawn loop around a box, like an instructor circling something on the screen."""
    cx, cy, rx, ry = x + w / 2, y + h / 2, w / 2 + 26, h / 2 + 22
    d = (f"M{cx - rx * 0.9:.0f},{cy - ry * 0.55:.0f} C{cx - rx * 0.6:.0f},{cy - ry * 1.12:.0f} {cx + rx * 0.7:.0f},{cy - ry * 1.08:.0f} {cx + rx:.0f},{cy - ry * 0.1:.0f} "
         f"C{cx + rx * 1.02:.0f},{cy + ry * 0.75:.0f} {cx + rx * 0.2:.0f},{cy + ry * 1.12:.0f} {cx - rx * 0.4:.0f},{cy + ry * 1.0:.0f} "
         f"C{cx - rx * 1.05:.0f},{cy + ry * 0.85:.0f} {cx - rx * 1.08:.0f},{cy - ry * 0.2:.0f} {cx - rx * 0.7:.0f},{cy - ry * 0.85:.0f}")
    return _svg(order, f'<path d="{d}"/>', color, width)


def underline(order, x1, x2, y, color=OR, width=5):
    """A slightly wavy pen underline from x1 to x2 at height y."""
    n = max(2, round((x2 - x1) / 60))
    pts = " ".join(f"{x1 + (x2 - x1) * k / n:.0f},{y + (3 if k % 2 else -2)}" for k in range(1, n + 1))
    return _svg(order, f'<path d="M{x1},{y} L{pts}"/>', color, width)


def box(order, x, y, w, h, color=RED, width=5, r=8):
    """A pen-drawn rounded box. Use it instead of ring() around rows packed close together, like menu items."""
    return _svg(order, f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}"/>', color, width)


# ---------- attributes for an element that enters on its step (put them inside the element's start tag) ----------

def WIPE(order):
    """Wipes in from the left, like a curtain pulled aside. Table rows, lines of a chart, a long sentence."""
    return f' data-build-in="wipe order {order}"'


def SLAM(order):
    """Comes in big and settles to its size. Only for a cover word or a part opener: it moves while people read."""
    return f' data-build-in="slam order {order}"'


def SLIDE(order, dx=0, dy=60):
    """Slides in from (dx, dy) px away. A small window coming in from a corner: SLIDE(n, 400, 300)."""
    return f' data-build-in="slide order {order}" data-dx="{dx}" data-dy="{dy}"'


def STAGGER(order, gap=70):
    """On a container: its children come in one by one, gap ms apart, on one click."""
    return f' data-build-in="stagger order {order}" data-gap="{gap}"'


def COUNT(order, ms=1200):
    """The first number in the element's text counts up from 0. Keep the final number in the HTML (the PDF shows it)."""
    return f' data-build-in="count order {order}" data-ms="{ms}"'


def MARK(order):
    """On a span already styled with its final tint, color or line-through: the style fades in on its step.
    Before the step the span reads as plain text. Use it for the changed letters of a fix, or pairing colors."""
    return f' data-build-in="mark order {order}"'


def PATH(order, path_id, ms=1400):
    """The element travels along the SVG path #path_id and lands where it is drawn (put it at the path's end)."""
    return f' data-build-in="path order {order}" data-path="{path_id}" data-ms="{ms}"'


def DIM(group):
    """Add to builds of one list: when a later one comes in, the earlier ones turn gray."""
    return f' data-dimgroup="{group}"'


def DELAY(ms):
    """Starts this element's entry ms later than the others of the same step (a label that follows its box)."""
    return f' data-delay="{ms}"'


def MORPH_FROM():
    """On the first code block of a morph. It is hidden in the PDF, which shows only the second block."""
    return ' data-pdf="hide"'


def MORPH(order, from_id):
    """On the second code block, drawn at the same place: tokens with the same data-m key move from the first block,
    tokens only in the first fade out, tokens only in the second fade in. Wrap tokens with tok()."""
    return f' data-build-in="morph order {order}" data-from="{from_id}"'


def tok(key, text, style=""):
    """A morph token. The same key in both blocks means the same piece of code."""
    return f'<span data-m="{key}" style="display:inline-block;{style}">{text}</span>'


# ---------- markers: empty boxes that are never painted ----------

def _mark(kind, order, x=0, y=0, w=1, h=1, extra=""):
    return f'<div data-build-in="{kind} order {order}"{extra} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px"></div>'


def lspot(order, x, y, w, h, ly, lh, bg="#FFFFFF", bar=BL):
    """Line spotlight. (x, y, w, h) is the code box; the band from ly with height lh stays clear and the rest of the box
    is veiled with bg (the box's own background). The next lspot slides the band; lspot_off clears it."""
    return _mark("lspot", order, x, y, w, h, f' data-ly="{ly:.0f}" data-lh="{lh:.0f}" data-bg="{bg}" data-bar="{bar}"')


def lspot_off(order):
    return _mark("lspot-off", order)


def run(order, x, y, w, h):
    """A green run band over the line being run. The next run moves it there; run_off hides it."""
    return _mark("run", order, x, y, w, h)


def run_off(order):
    return _mark("run-off", order)


def zoom(order, x, y, w, h, pad=40, max_scale=3):
    """Moves the camera in so the box fills the screen. zoom_off comes back. Once a slide at most."""
    return _mark("zoom", order, x, y, w, h, f' data-pad="{pad}" data-max="{max_scale}"')


def zoom_off(order):
    return _mark("zoom-off", order)


def blur(order, target):
    """Blurs every part of the slide except the one holding #target. For light screens where dimming hides text."""
    return _mark("blur", order, extra=f' data-target="{target}"')


def blur_off(order):
    return _mark("blur-off", order)


def text(order, target, value):
    """#target's text becomes value on this step, with a short yellow flash. Give #target its last value in the HTML
    and its first value as data-start="..." (the PDF shows the last value)."""
    return _mark("text", order, extra=f' data-target="{target}" data-text="{value}"')


def pan(order, target, y, ms=2000):
    """Moves #target (a long output inside a box with overflow:hidden) by y px, like a camera going down it."""
    return _mark("pan", order, extra=f' data-target="{target}" data-y="{y}" data-ms="{ms}"')


def kenburns(order, target, scale=1.12, ms=6000, origin="50% 50%"):
    """Slowly zooms #target. Only for a picture with no text to read, such as a cover image."""
    return _mark("kenburns", order, extra=f' data-target="{target}" data-scale="{scale}" data-ms="{ms}" data-origin="{origin}"')


def pulse(order, target):
    """Taps #target twice, to point back at something already on the slide."""
    return _mark("pulse", order, extra=f' data-target="{target}"')


def grow(order, target):
    """#target grows and settles back once."""
    return _mark("grow", order, extra=f' data-target="{target}"')


def shine(order, target):
    """A light sweeps over #target. Cover or part opener only."""
    return _mark("shine", order, extra=f' data-target="{target}"')


def shake(order, target):
    """#target shakes sideways once. Only for the moment something fails, once a deck."""
    return _mark("shake", order, extra=f' data-target="{target}"')


# ---------- small drawings ----------

def link(order, x1, y1, x2, y2, color=BL, width=4):
    """A pen-drawn curve from a code line (x1, y1) to its output line (x2, y2)."""
    mx = (x1 + x2) / 2
    return _svg(order, f'<path d="M{x1:.0f},{y1:.0f} C{mx:.0f},{y1:.0f} {mx:.0f},{y2:.0f} {x2:.0f},{y2:.0f}"/>', color, width)


def keys(order, x, y, combo, size=30):
    """Keycaps for a shortcut such as "control+Enter", popping in one by one in a corner."""
    caps = [f'<span style="display:inline-block;font-family:\'JetBrains Mono\',monospace;font-size:{size}px;font-weight:700;line-height:1.2;color:#1D2330;background:#FFFFFF;border:2px solid #C9CED8;border-bottom-width:6px;border-radius:12px;padding:8px 18px">{k}</span>' for k in combo.split("+")]
    plus = f'<span style="font-size:{size * 0.8:.0f}px;font-weight:700;color:{GRAY}">+</span>'
    items = []
    for i, c in enumerate(caps):
        if i:
            items.append(plus)
        items.append(c)
    return f'<div{STAGGER(order, 160)} style="position:absolute;left:{x}px;top:{y}px;display:flex;flex-direction:row;align-items:center;gap:12px">{"".join(items)}</div>'


def compare(cid, x, y, w, h, before, after, start=50):
    """A before/after slider students drag (a slide-js lab). before and after are HTML drawn at (0, 0) inside a w x h box.
    The PDF shows the split at start %."""
    sx = w * start / 100
    js = f"""const b=sec.querySelector('#{cid}'),a=b.querySelector('.cmp-a'),d=b.querySelector('.cmp-d');
const set=x=>{{x=Math.max(0,Math.min({w},x));a.style.clipPath='inset(0 0 0 '+x+'px)';d.style.left=(x-3)+'px';}};
let on=false;const pos=e=>{{const r=api.rectIn(b);const S=sec.getBoundingClientRect(),k=S.width/1920;return (e.clientX-S.left)/k-r.x;}};
d.addEventListener('pointerdown',e=>{{on=true;d.setPointerCapture(e.pointerId);e.stopPropagation();}});
d.addEventListener('pointermove',e=>{{if(on)set(pos(e));}});d.addEventListener('pointerup',()=>on=false);
return {{enter(){{set({sx:.0f});}}}};"""
    return (f'<div id="{cid}" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;overflow:hidden;border-radius:16px">'
            f'<div style="position:absolute;inset:0">{before}</div>'
            f'<div class="cmp-a" style="position:absolute;inset:0;clip-path:inset(0 0 0 {sx:.0f}px)">{after}</div>'
            f'<div class="cmp-d" style="position:absolute;left:{sx - 3:.0f}px;top:0;width:6px;height:{h}px;background:{BL};cursor:ew-resize">'
            f'<div style="position:absolute;left:-25px;top:{h / 2 - 28:.0f}px;width:56px;height:56px;border-radius:50%;background:{BL};color:#FFFFFF;font-size:26px;font-weight:900;line-height:56px;text-align:center">&#8646;</div></div>'
            f'</div><script type="text/slide-js">{js}</script>')
