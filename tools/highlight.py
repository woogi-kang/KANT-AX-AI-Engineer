"""Highlight helpers shared by every chapter's tools/gen.py. How to use them: tools/HIGHLIGHT.md.

Import from a chapter's gen.py:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tools"))
    from highlight import spot, spot_off, cursor, cursor_off, ring, underline, TYPE

The player (tools/build_player.js) runs them. export.js and check.js ignore them, so the PDF shows the
slide's plain layout: spot and cursor boxes are empty, drawn lines are fully drawn, typed text is whole.
"""

# Same meaning as the code-line tints: green run, gray skip, red error, blue mark, orange note.
GR, GRAY, RED, BL, OR = "#1F8A4C", "#6A7180", "#A33131", "#2459C9", "#B26A00"


def TYPE(order):
    """Attribute for a text element (a terminal command line) that is typed in letter by letter."""
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
