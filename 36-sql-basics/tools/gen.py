r"""Generates every slide of the SQL 1 deck (36) and slides/deck.json.

Story: 34 ran PostgreSQL in a container and typed CREATE TABLE, INSERT and SELECT * once. Real work asks more of a
table: only the products low in stock, the three most expensive, change a price, take a product off. Part 1 enters
kant_shop (35's class names). Part 2 is data types (CHAR/VARCHAR/TEXT, SMALLINT/INTEGER/BIGINT, NUMERIC vs
REAL/DOUBLE, BOOLEAN, DATE/TIME/TIMESTAMP/TIMESTAMPTZ). Part 3 builds product and reads it with WHERE, IN, BETWEEN,
LIKE, ILIKE, IS NULL, AS, computed columns, COUNT(*) (row count only), ORDER BY, LIMIT, OFFSET. Part 4 changes it with UPDATE, DELETE, RETURNING and DROP ... IF EXISTS,
then SQL is set beside the Python of 15, 22 and 23. Part 5 errors, part 6 a member list, then what 37 adds.
Part 6 also shows DISTINCT. Constraints, JOIN, GROUP BY and aggregates other than COUNT(*) stay out.

Every terminal line comes from tools/demo.py (real Docker and postgres:18 = PostgreSQL 18.7, in tools/out.json).
Usage (in 36-sql-basics): python3 tools/gen.py slides
"""
import html, json, os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from highlight import (spot, spot_off, cursor, cursor_off, ring, box as pen_box, underline, text as set_text,  # noqa: E402
                       SLAM, SLIDE, DIM, DELAY, PATH, STAGGER, WIPE, MARK, MORPH, MORPH_FROM, tok,
                       pulse, shine, shake, zoom, zoom_off, lspot, lspot_off, link, COUNT, grow)

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT):
    if f.endswith(".html"):
        os.remove(os.path.join(OUT, f))
HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "out.json")))
sys.path.insert(0, HERE)
from files import TABLE, ROWS, PRODUCTS, MEMBER, MEMBER_ROWS, MEMBERS  # noqa: E402  (the SQL demo.py typed)

SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
BG, INK, SUB, LINE, CARD = "#F6F5F1", "#1D2330", "#4A5262", "#DCD8CE", "#FFFFFF"
BL, GR, OR, RED, TEAL, GRAY, MAG = "#2459C9", "#1F8A4C", "#B26A00", "#A33131", "#0F7C86", "#5B6270", "#A23B72"
DK = "#1D63ED"                       # Docker's blue
NG, NGBG = "#1F8A4C", "#E4F3EA"      # nginx (its own green)
AP, APBG = "#0F7C86", "#E1F2F3"      # app servers (whoami)
BW, BWBG = "#2459C9", "#E8EFFD"      # the browser / the student
T_BG = "#1B2029"
TCOL = {"o": "#D8DEE9", "e": "#FF9C94", "g": "#7FD18B", "d": "#7D8696", "y": "#F2C46D", "c": "#7D8696"}
SHADOW = "0 18px 40px rgba(29,35,48,.16), 0 2px 6px rgba(29,35,48,.08)"
WARN = []
REAL = " 터미널 출력은 tools/demo.py로 실제 Docker와 PostgreSQL 18을 실행한 결과예요."


def ttw(s, size):
    """terminal width: a Hangul letter takes two cells (1.2em) like in a real terminal"""
    return sum((1.2 if (0xAC00 <= ord(c) <= 0xD7A3 or 0x3130 <= ord(c) <= 0x318F) else 0.6) for c in s) * size


HANGUL = re.compile(r"([\uac00-\ud7a3\u3130-\u318f])")


def cells(h):
    """wrap each Hangul letter of a terminal row in a two-cell box so the psql columns line up"""
    return HANGUL.sub(r'<span style="display:inline-block;width:1.2em;text-align:center">\1</span>', h)



def e(s):
    return html.escape(s, quote=False)


def p(style, text, attrs=""):
    return f'<p{attrs} style="{style}">{text}</p>'


def tw(s, size, mono=True):
    """Width estimate in px. JetBrains Mono is 0.6em; Hangul falls back to Noto Sans KR at 0.92em."""
    w = 0.0
    for c in s:
        o = ord(c)
        if 0xAC00 <= o <= 0xD7A3 or 0x3130 <= o <= 0x318F:
            w += 0.92 if mono else 1.0
        elif mono:
            w += 0.6
        elif c == " ":
            w += 0.25
        elif c.isupper() or c.isdigit():
            w += 0.64
        else:
            w += 0.54
    return w * size


def bi(kind, order):
    return f' data-build-in="{kind} order {order}"' if order else ""


ORDER, SECTIONS = [], {}


def W(sid, parts, notes, section=None):
    if section:
        SECTIONS[section[0]] = {"description": section[1], "start": sid}
    ORDER.append(sid)
    with open(os.path.join(OUT, sid + ".html"), "w") as f:
        f.write("\n".join(parts) + f"\n<aside>{e(notes)}</aside>\n</section>\n")


def frame(sid, eyebrow, title, color, transition="fade"):
    return [f'<section id="{sid}" data-transition="{transition}" style="background:{BG};color:{INK};font-family:{SANS};font-variant-ligatures:none;word-break:keep-all;padding:96px">',
            p(f"position:absolute;left:96px;top:48px;width:1728px;font-size:26px;font-weight:700;color:{color}", e(eyebrow), ' id="eyebrow"'),
            f'<h2 id="title" style="position:absolute;left:96px;top:92px;width:1728px;font-size:52px;font-weight:700;line-height:1.2;color:{INK}">{title}</h2>']


def caption(text, top, order=None, left=96, width=1728, size=32, color=INK):
    return p(f"position:absolute;left:{left}px;top:{top:.0f}px;width:{width}px;font-size:{size}px;font-weight:700;line-height:1.45;color:{color}", text, bi("rise", order))


def cmd(text):
    return f'<span style="font-family:{MONO};font-weight:700">{e(text)}</span>'


def mark(text, marks):
    """wrap the first match of each key of marks in a span (a key starting with … takes the last match);
    the value is an id, or raw attributes when it has an = sign"""
    out, pos = "", 0
    hits = []
    for k, v in marks.items():
        last = k.startswith("…")
        k2 = k[1:] if last else k
        at = text.rfind(k2) if last else text.find(k2)
        if at >= 0:
            hits.append((at, k2, v))
    for at, k, v in sorted(hits):
        if at < pos:
            continue
        attrs = v if "=" in v else f'id="{v}"'
        out += e(text[pos:at]) + f'<span {attrs}>{e(k)}</span>'
        pos = at + len(k)
    out += e(text[pos:])
    return out.replace("  ", " &#160;") if out else "&#160;"


# ---------- real output ----------
def unwrap(lines, cols=80):
    """A real 80-column terminal wraps long lines; a wider window shows them whole. Join the wrapped pieces."""
    out = []
    for l in lines:
        if out and len(out[-1]) >= cols and out[-1].endswith(out[-1].rstrip()) and getattr(unwrap, "_cont", False):
            out[-1] += l
        else:
            out.append(l)
        unwrap._cont = len(l) == cols
    return out


def R(scene, k=0, wrap=False):
    lines = [l.rstrip() for l in D[scene][k]["out"]]
    while lines and not lines[0].strip():
        lines = lines[1:]
    return unwrap(lines) if wrap else lines


def rewrap(lines, cols=140):
    """wrap long lines at spaces, the way a wider terminal window would"""
    import textwrap
    out = []
    for l in lines:
        out += textwrap.wrap(l, cols, break_on_hyphens=False, drop_whitespace=True) if len(l) > cols else [l]
    return out


def C(scene, k=0):
    return D[scene][k]["cmd"]


# ---------- terminal ----------
class Term:
    PT, PX, BAR = 24, 34, 36

    def __init__(self, lines, x, y, size=28, w=None, lh=1.5, tid="term", attrs="", room=0, bar=True, bleed=False, h=None):
        self.x, self.y, self.size, self.tid, self.attrs = x, y, size, tid, attrs
        self.lp = round(size * lh)
        self.bar = self.BAR if bar else 0
        self.rows = [self._row(l) for l in lines]
        self.tws = [ttw(r[1], size) for r in self.rows]
        self.w = w or round(max(self.tws) + 2 * self.PX + room)
        self.h = h or round(2 * self.PT + self.bar + len(self.rows) * self.lp)
        self.inner = []
        if x + self.w > 1824 and not bleed:
            WARN.append(f"{tid}: terminal right edge {x + self.w}")
        for i, t_ in enumerate(self.tws):
            if self.tx + t_ > x + self.w - 10 and not bleed:
                WARN.append(f"{tid}: line {i} '{self.rows[i][1][:30]}' runs past the terminal ({self.tx + t_:.0f} > {x + self.w - 10})")
        if y + self.h > (995 if (x < 1150 and x + self.w > 770) else 1040):
            WARN.append(f"{tid}: terminal bottom {y + self.h}")

    def _row(self, l):
        kind = l[0]
        marks = l[-1] if isinstance(l[-1], dict) else {}
        if kind == "$":
            path, c = l[1], l[2]
            return kind, f"{path} $ {c}", f'<span style="color:#8FB3FF">{e(path)} $</span> ' + mark(c, marks), "#F2C46D"
        if kind == "#":                      # a shell inside a container: root@id:/path#
            pr, c = l[1], l[2]
            return kind, f"{pr}# {c}", f'<span style="color:#7FD1C8">{e(pr)}#</span> ' + mark(c, marks), "#F2C46D"
        t = l[1].replace("\t", "    ")
        return kind, t, mark(t, marks), TCOL[kind]

    tx = property(lambda s: s.x + s.PX)

    def top(self, i):
        return self.y + self.PT + self.bar + i * self.lp

    def cy(self, i):
        return self.top(i) + self.lp / 2

    def end(self, i):
        return self.tx + self.tws[i]

    def sx(self, i, sub):
        t = self.rows[i][1]
        return self.tx + ttw(t[:t.index(sub)], self.size)

    def sw(self, sub):
        return ttw(sub, self.size)

    def band(self, i, j=None, order=None, color="rgba(242,196,109,.17)", attrs=""):
        j = i if j is None else j
        self.inner.append(f'<div{bi("fade", order)}{attrs} style="position:absolute;left:{self.PX - 12}px;top:{self.PT + self.bar + i * self.lp:.0f}px;width:{self.w - 2 * self.PX + 24}px;height:{(j - i + 1) * self.lp:.0f}px;background:{color};border-radius:8px"></div>')

    def html(self):
        o = [f'<div id="{self.tid}"{self.attrs} style="position:absolute;left:{self.x}px;top:{self.y}px;width:{self.w}px;height:{self.h}px;background:{T_BG};border-radius:18px;padding:{self.PT}px {self.PX}px;font-family:{MONO};font-variant-ligatures:none;overflow:hidden;box-shadow:0 10px 30px rgba(29,35,48,.12)">']
        if self.bar:
            o.append('<div style="display:flex;flex-direction:row;gap:10px;height:16px;margin-bottom:20px">'
                     + "".join(f'<div style="width:16px;height:16px;border-radius:8px;background:{c}"></div>' for c in ("#F28B82", "#F2C46D", "#7FD18B")) + '</div>')
        o += self.inner
        for kind, _, h, col in self.rows:
            wt = "font-weight:700;" if kind in ("$", "#") else ""
            o.append(p(f"position:relative;font-size:{self.size}px;line-height:{self.lp:.0f}px;height:{self.lp:.0f}px;white-space:pre;{wt}color:{col}", cells(h)))
        o.append('</div>')
        return "".join(o)


LC = {BL: "#6F9BF5", GR: "#5CC287", OR: "#E3A84A", RED: "#F07A72", TEAL: "#4FB8C2", GRAY: "#9AA3B5", MAG: "#E07FB0", DK: "#6F9BF5"}


def tag(t, i, text, color, order=None, at=None, gap=44):
    """A pill on terminal line i: dot right after the text, a short leader, then the words."""
    x0 = at if at is not None else t.end(i)
    cy = t.cy(i)
    pw = tw(text, 23, mono=False) + 30
    px = x0 + gap
    if px + pw > t.x + t.w - 14:
        WARN.append(f"{t.tid}: tag '{text}' ends at {px + pw:.0f}, terminal ends {t.x + t.w}")
    lc = LC.get(color, color)
    return [f'<div{bi("fade", order)} style="position:absolute;left:{x0 + 12:.0f}px;top:{cy - 5:.0f}px;width:{gap - 12:.0f}px;height:10px">'
            f'<div style="position:absolute;left:0;top:0;width:10px;height:10px;border-radius:5px;background:{lc}"></div>'
            f'<div style="position:absolute;left:10px;top:4px;width:{gap - 22:.0f}px;height:2px;background:{lc}"></div></div>',
            p(f"position:absolute;left:{px:.0f}px;top:{cy - 20:.0f}px;height:40px;padding:0 15px;border-radius:10px;background:{color};font-family:{SANS};font-size:23px;font-weight:700;line-height:40px;color:#FFFFFF;white-space:nowrap", e(text), bi("pop", order))]


def pill(x, y, text, color, order=None, size=24, anim="pop", attrs=""):
    return p(f"position:absolute;left:{x:.0f}px;top:{y:.0f}px;height:{size + 18}px;padding:0 16px;border-radius:10px;background:{color};font-family:{SANS};font-size:{size}px;font-weight:700;line-height:{size + 18}px;color:#FFFFFF;white-space:nowrap", e(text), bi(anim, order) + attrs)


# ---------- browser window ----------
def browser(x, y, w, h, url, inner, bid, attrs="", pad="34px 44px"):
    return (f'<div id="{bid}"{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{CARD};border:1px solid #D2CEC4;border-radius:16px;overflow:hidden;box-shadow:{SHADOW};display:flex;flex-direction:column">'
            '<div style="height:52px;flex:none;background:#EEECE6;display:flex;flex-direction:row;align-items:center;gap:9px;padding:0 18px">'
            + "".join('<div style="width:13px;height:13px;border-radius:7px;background:#C9CED8"></div>' for _ in range(3))
            + p(f"margin-left:14px;font-family:{SANS};font-size:20px;font-weight:500;color:{SUB};background:#FFFFFF;border-radius:9px;padding:4px 16px;white-space:nowrap", e(url))
            + '</div>'
            f'<div style="flex:1;display:flex;flex-direction:column;align-items:flex-start;justify-content:flex-start;gap:16px;padding:{pad}">{inner}</div></div>')


def bar(w, c="#E4E1DA"):
    return f'<div style="width:{w}px;height:12px;flex:none;border-radius:6px;background:{c}"></div>'


# ---------- editor (VS Code-like file) ----------
TABH = 56


def editor(eid, name, lines, left, top, w, fs=26, attrs="", color=BL, h=None, nums=True, start=1):
    lh = fs * 1.45
    gw = 70 if nums else 0
    hh = h or (TABH + 36 + len(lines) * lh)
    o = [f'<div id="{eid}"{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{hh:.0f}px;background:{CARD};border:2px solid {LINE};border-radius:16px;overflow:hidden">',
         f'<div style="position:absolute;left:0;top:0;width:{w}px;height:{TABH}px;background:#EEF0F3;border-bottom:2px solid {LINE}"></div>',
         p(f"position:absolute;left:0;top:0;height:{TABH}px;padding:0 26px;background:{CARD};border-right:2px solid {LINE};border-top:4px solid {color};font-family:{MONO};font-size:24px;font-weight:700;line-height:{TABH - 6}px;color:{INK};white-space:nowrap", e(name))]
    if gw:
        o.append(f'<div style="position:absolute;left:0;top:{TABH + 16}px;width:{gw}px">' + "".join(
            p(f"height:{lh:.2f}px;font-family:{MONO};font-size:{fs * 0.8:.0f}px;line-height:{lh:.2f}px;text-align:right;padding-right:6px;color:#A3A9B4", str(i + start)) for i in range(len(lines))) + '</div>')
    body = "".join(p(f"height:{lh:.2f}px;font-family:{MONO};font-size:{fs}px;line-height:{lh:.2f}px;white-space:pre;color:{INK}", l if "<span" in l else (e(l) if l else "&#160;")) for l in lines)
    o.append(f'<div style="position:absolute;left:{gw}px;top:{TABH}px;right:0;padding:16px 24px;background:{CARD};display:flex;flex-direction:column">{body}</div>')
    o.append('</div>')
    g = {"left": left, "top": top, "w": w, "fs": fs, "lh": lh, "tx": left + 2 + gw + 24, "y0": top + 2 + TABH + 16, "h": hh, "n": len(lines)}
    for i, l in enumerate(lines):
        if g["tx"] + tw(re.sub(r"<[^>]+>", "", l), fs) > left + w - 12:
            WARN.append(f"{eid}: line {i} runs past the editor")
    return "".join(o), g


def gtop(g, i):
    return g["y0"] + i * g["lh"]


def gcy(g, i):
    return g["y0"] + i * g["lh"] + g["lh"] / 2


def gx(g, s):
    return g["tx"] + tw(s, g["fs"])


def lband(order, g, i, n=1, color=BL, anim="fade", alpha="1F"):
    x = g["left"] + 2 + (70 if g["tx"] - g["left"] > 60 else 0)
    return f'<div{bi(anim, order)} style="position:absolute;left:{x}px;top:{gtop(g, i):.1f}px;width:{g["left"] + g["w"] - 2 - x}px;height:{n * g["lh"]:.1f}px;background:{color}{alpha};border-left:6px solid {color}"></div>'


def leader(x1, y, x2, color, order=None, label=None, lw=None, size=26, sub=None):
    """A thin line from (x1, y) to a label starting at x2, ending in a dot on the code side."""
    o = [f'<div{bi("fade", order)} style="position:absolute;left:{x1:.0f}px;top:{y - 5:.0f}px;width:{x2 - x1 - 14:.0f}px;height:10px">'
         f'<div style="position:absolute;left:0;top:0;width:10px;height:10px;border-radius:5px;background:{color}"></div>'
         f'<div style="position:absolute;left:10px;top:4px;width:{x2 - x1 - 24:.0f}px;height:2px;background:{color}"></div></div>']
    if label:
        o.append(p(f"position:absolute;left:{x2:.0f}px;top:{y - size * 0.75:.0f}px;{'width:' + str(lw) + 'px;' if lw else ''}font-size:{size}px;font-weight:700;line-height:1.45;color:{color};white-space:nowrap", label, bi("rise", order)))
        if sub:
            o.append(p(f"position:absolute;left:{x2:.0f}px;top:{y + size * 0.75:.0f}px;font-size:{size - 4}px;line-height:1.4;color:{SUB};white-space:nowrap", sub, bi("rise", order)))
    return o


# ---------- a command taken apart ----------
def parts(x, y, segs, size=48, order=None, lab=24, drop=34, stagger=False, sep=1, lw=420):
    """segs: (text, color, label or None, id or None). Pieces are joined by spaces."""
    o, cx = [], x
    spans = []
    for k, (t, c, label, sid) in enumerate(segs):
        w = tw(t, size)
        i = f' id="{sid}"' if sid else ""
        spans.append(f'<span{i} style="color:{c}">{e(t)}</span>')
        if label:
            ord_ = (order + k) if (order and stagger) else order
            mid = cx + w / 2
            o.append(f'<div{bi("fade", ord_)} style="position:absolute;left:{mid - 1:.0f}px;top:{y + size * 1.3 + 4:.0f}px;width:2px;height:{drop}px;background:{c}"></div>')
            o.append(p(f"position:absolute;left:{mid - lw / 2:.0f}px;top:{y + size * 1.3 + drop + 10:.0f}px;width:{lw}px;text-align:center;font-size:{lab}px;font-weight:700;line-height:1.35;color:{c}", label, bi("pop", ord_)))
        cx += w + tw(" " * sep, size)
    o.insert(0, p(f"position:absolute;left:{x}px;top:{y}px;font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.3;white-space:pre", (" " * sep).join(spans)))
    return o


def svg(inner, order=None, kind="draw"):
    return (f'<svg{bi(kind, order)} viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible">{inner}</svg>')


def arrow_path(d, color, width=5, dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"{da}/>'


def head_at(x, y, ang, color, size=18):
    import math
    a = math.radians(ang)
    p1 = (x - size * math.cos(a - 0.45), y - size * math.sin(a - 0.45))
    p2 = (x - size * math.cos(a + 0.45), y - size * math.sin(a + 0.45))
    return f'<path d="M{p1[0]:.0f},{p1[1]:.0f} L{x:.0f},{y:.0f} L{p2[0]:.0f},{p2[1]:.0f}" fill="none" stroke="{color}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'


def harrow(x1, x2, y, color, order=None, width=5):
    return svg(arrow_path(f"M{x1},{y} L{x2},{y}", color, width) + head_at(x2 + 2, y, 0, color), order)


def file_chip(name, color=INK, bg=CARD, fid=None, attrs="", size=22):
    i = f' id="{fid}"' if fid else ""
    return p(f"height:{size + 22}px;flex:none;padding:0 14px;border-radius:9px;background:{bg};border:2px solid #D6D2C8;font-family:{MONO};font-size:{size}px;font-weight:700;line-height:{size + 18}px;color:{color};white-space:nowrap", e(name), i + attrs)




# ---------- boxes of the big picture ----------
def node(x, y, w, h, title, sub, color, bg, nid=None, attrs="", icon=None, tsize=30, ssize=22, mono_sub=False):
    i = f' id="{nid}"' if nid else ""
    ic = f'<x-icon name="{icon}" style="width:34px;height:34px;flex:none;color:{color}"></x-icon>' if icon else ""
    return (f'<div{i}{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{bg};border:3px solid {color};border-radius:20px;'
            f'display:flex;flex-direction:column;justify-content:center;gap:6px;padding:0 24px">'
            f'<div style="display:flex;flex-direction:row;align-items:center;gap:12px">{ic}'
            + p(f"font-size:{tsize}px;font-weight:700;color:{color};line-height:1.25;white-space:nowrap", title) + '</div>'
            + (p(f"{'font-family:' + MONO + ';' if mono_sub else ''}font-size:{ssize}px;font-weight:{700 if mono_sub else 400};color:{SUB};line-height:1.35;white-space:nowrap", sub) if sub else "")
            + '</div>')


def line_arrow(x1, y1, x2, y2, color, order=None, width=5, dash=None, kind="draw", pid=None, head=True):
    import math
    ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    pa = f' id="{pid}"' if pid else ""
    d = f"M{x1:.0f},{y1:.0f} L{x2:.0f},{y2:.0f}"
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return svg(f'<path{pa} d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round"{da}/>' + (head_at(x2 + 1, y2, ang, color) if head else ""), order, kind)


def dot(x, y, color, order, path_id, ms=1300, r=13, attrs=""):
    """a request (or answer) dot that travels along #path_id; drawn at the path's end"""
    return f'<div{PATH(order, path_id, ms)}{attrs} style="position:absolute;left:{x - r:.0f}px;top:{y - r:.0f}px;width:{2 * r}px;height:{2 * r}px;border-radius:{r}px;background:{color};box-shadow:0 0 0 5px #FFFFFF"></div>'


def addr(x, y, text, color=BW, order=None, size=30, aid=None, attrs="", anim="pop"):
    i = f' id="{aid}"' if aid else ""
    return (f'<div{i}{bi(anim, order)}{attrs} style="position:absolute;left:{x}px;top:{y}px;height:{size + 30}px;padding:0 22px;border-radius:{(size + 30) // 2}px;background:#FFFFFF;border:2px solid #D2CEC4;'
            f'display:flex;flex-direction:row;align-items:center;gap:12px;box-shadow:0 4px 12px rgba(29,35,48,.08)">'
            f'<x-icon name="Globe" style="width:{size - 4}px;height:{size - 4}px;flex:none;color:{GRAY}"></x-icon>'
            + p(f"font-family:{MONO};font-size:{size}px;font-weight:700;color:{color};white-space:nowrap", text) + '</div>')


def RA(scene, k=0, wrap=None):
    """real output of D[scene][k]; lines the 80-column pty wrapped (curl, compose) are joined back"""
    out = []
    cmd = D[scene][k]["cmd"]
    if wrap is None:
        wrap = cmd.startswith("curl") or cmd.startswith("docker compose up") or cmd.startswith("docker compose down")
    prev = 0                     # length of the previous raw pty line
    for raw in D[scene][k]["out"]:
        if wrap and out and prev >= 79 and raw.strip() and not re.search(r"\d\.\ds\s*$", out[-1]):
            out[-1] += raw if prev == 80 else " " + raw      # the pty wrapped at 80 columns (a space at the wrap is dropped)
        else:
            out.append(raw)
        prev = len(raw)
    out = [l.rstrip() for l in out]
    while out and not out[-1]:
        out.pop()
    return out




def yaml_html(line, marks=None):
    s = e(line)
    m = re.match(r"^(\s*)([a-z_]+):(.*)$", s)
    if m:
        lvl = len(m.group(1)) // 2
        col = [INK, AP, GRAY][min(lvl, 2)]
        s = f'{m.group(1)}<span style="color:{col};font-weight:700">{m.group(2)}</span>:{m.group(3)}'
    for k, v in (marks or {}).items():
        s = s.replace(e(k), f'<span {v}>{e(k)}</span>', 1)
    return s



def sheet(x, y, cols, rows, sid, widths, size=32, rh=74, hbg="#EEF0F3", hcol=INK, types=None, attrs="", name=None, ncol=None, pk=False, cell_attrs=None):
    """A database table drawn as a grid. Cells get ids sid-rIcJ, headers sid-hJ. Returns (html, geometry)."""
    cell_attrs = cell_attrs or {}
    W_ = sum(widths)
    th = rh + (34 if types else 0)
    top = y + (56 if name else 0)
    H = th + rh * len(rows)
    o = [f'<div id="{sid}"{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{W_}px;height:{H + 8 + (56 if name else 0)}px">']
    if name:
        o.append(p(f"position:absolute;left:0;top:0;height:44px;padding:0 18px;border-radius:10px 10px 0 0;background:{ncol or MY};font-family:{MONO};font-size:24px;font-weight:700;line-height:44px;color:#FFFFFF;white-space:nowrap", e(name)))
    oy = top - y
    o.append(f'<div style="position:absolute;left:0;top:{oy}px;width:{W_}px;height:{H + 4}px;background:{CARD};border:2px solid #CFCAC0;border-radius:{"0 14px 14px 14px" if name else "14px"};overflow:hidden">')
    o.append(f'<div style="position:absolute;left:0;top:0;width:{W_}px;height:{th}px;background:{hbg}"></div>')
    cx = 0
    for j, (c, w) in enumerate(zip(cols, widths)):
        kc = VO if (pk and j == 0) else hcol
        o.append(p(f"position:absolute;left:{cx}px;top:{(rh - size * 1.3) / 2 + (0 if not types else 0):.0f}px;width:{w}px;text-align:center;font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.3;color:{kc};white-space:nowrap", e(c), f' id="{sid}-h{j}"'))
        if types:
            o.append(p(f"position:absolute;left:{cx}px;top:{rh - 8}px;width:{w}px;text-align:center;font-family:{MONO};font-size:{size * 0.66:.0f}px;font-weight:700;line-height:1.3;color:{GRAY};white-space:nowrap", e(types[j]), f' id="{sid}-t{j}"'))
        if j:
            o.append(f'<div style="position:absolute;left:{cx - 1}px;top:0;width:2px;height:{H}px;background:#E2DED5"></div>')
        cx += w
    for i, r in enumerate(rows):
        ry = th + i * rh
        o.append(f'<div style="position:absolute;left:0;top:{ry - 1}px;width:{W_}px;height:2px;background:#E2DED5"></div>')
        cx = 0
        for j, (v, w) in enumerate(zip(r, widths)):
            num = v.isdigit()
            col = VO if (pk and j == 0) else INK
            o.append(p(f"position:absolute;left:{cx}px;top:{ry + (rh - size * 1.3) / 2:.0f}px;width:{w}px;text-align:center;font-family:{MONO};font-size:{size}px;font-weight:{700 if pk and j == 0 else 400};line-height:1.3;color:{col};white-space:nowrap", e(v) if v else "&#160;", f' id="{sid}-r{i}c{j}"' + cell_attrs.get((i, j), "")))
            cx += w
    o.append('</div></div>')
    g = {"x": x, "y": top, "w": W_, "th": th, "rh": rh, "h": H, "widths": widths,
         "cx": [x + sum(widths[:j]) for j in range(len(widths))]}
    return "".join(o), g


def row_y(g, i):
    return g["y"] + g["th"] + i * g["rh"]


def cyl(x, y, w, h, title, sub, color, bg, cid=None, attrs="", tsize=30, ssize=22):
    """a database drum: the usual picture for 'stored data'"""
    i = f' id="{cid}"' if cid else ""
    ry = 22
    return (f'<div{i}{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px">'
            f'<svg viewBox="0 0 {w} {h}" style="position:absolute;left:0;top:0;width:{w}px;height:{h}px;overflow:visible">'
            f'<path d="M3,{ry} L3,{h - ry} A{w / 2 - 3},{ry} 0 0 0 {w - 3},{h - ry} L{w - 3},{ry}" fill="{bg}" stroke="{color}" stroke-width="3"/>'
            f'<ellipse cx="{w / 2}" cy="{ry}" rx="{w / 2 - 3}" ry="{ry - 2}" fill="#FFFFFF" stroke="{color}" stroke-width="3"/></svg>'
            + p(f"position:absolute;left:0;top:{h / 2 - (tsize * 0.8 if sub else tsize * 0.5) + 8:.0f}px;width:{w}px;text-align:center;font-size:{tsize}px;font-weight:700;line-height:1.3;color:{color};white-space:nowrap", title)
            + (p(f"position:absolute;left:0;top:{h / 2 + tsize * 0.5 + 14:.0f}px;width:{w}px;text-align:center;font-size:{ssize}px;line-height:1.35;color:{SUB};white-space:nowrap", sub) if sub else "")
            + '</div>')


# =====================================================================


# =====================================================================
# chapter 36 helpers
# =====================================================================
PG, PGBG = "#336791", "#E6EDF5"      # PostgreSQL's own blue
NL, NLBG = "#A23B72", "#F7E6EF"      # NULL (모름)
PROMPT_RE = re.compile(r"^([a-z0-9_]+)(=#|-#|\(#|'#|=>) ?(.*)$")
ERR_RE = re.compile(r"^(ERROR|DETAIL|HINT|LINE \d+:|FATAL|psql: error)")
P_HOME = "~"
PS = "kant_shop=#"


def psql_rows(lines, marks=None):
    """terminal rows for psql lines; marks maps a row index to the mark dict of that row"""
    marks = marks or {}
    out = []
    for i, l in enumerate(lines):
        mk = marks.get(i)
        m = PROMPT_RE.match(l)
        if l.startswith("$ "):
            row = ("$", P_HOME, l[2:])
        elif m:
            row = ("m", m.group(1) + m.group(2), m.group(3))
        elif ERR_RE.match(l.strip()) or (l.strip() == "^"):
            row = ("e", l)
        elif l.startswith("NOTICE"):
            row = ("y", l)
        elif l == "…":
            row = ("d", "…")
        else:
            row = ("o", l)
        out.append(row + ((mk,) if mk else ()))
    return out


_old_row = Term._row


def _row(self, l):
    if l[0] == "m":
        pr, c = l[1], l[2]
        marks = l[-1] if isinstance(l[-1], dict) else {}
        return "m", f"{pr} {c}", f'<span style="color:#9DC1E6">{e(pr)}</span> ' + mark(c, marks), "#F2C46D"
    return _old_row(self, l)


Term._row = _row
_old_html = Term.html


def _html(self):
    h = _old_html(self)
    return h.replace('white-space:pre;color:#F2C46D"><span style="color:#9DC1E6">', 'white-space:pre;font-weight:700;color:#F2C46D"><span style="color:#9DC1E6">')


Term.html = _html


def stmts(scene, k=0):
    """the statements of an interactive psql session: each is its prompt line(s) and the output up to the next prompt"""
    out = [l.rstrip() for l in D[scene][k]["out"]]
    out = [l for l in out if not l.startswith("psql (18") and not l.startswith('Type "help"')]
    blocks, cur = [], None
    for l in out:
        m = PROMPT_RE.match(l)
        if m and m.group(2) in ("=#", "=>") and not (cur and PROMPT_RE.match(cur[-1] or "x") and False):
            if cur is not None:
                blocks.append(cur)
            cur = [l]
        elif cur is not None:
            cur.append(l)
    if cur:
        blocks.append(cur)
    return [b for b in blocks if not PROMPT_RE.match(b[0]).group(3).startswith("\\q")]


def Q(scene, *idx, k=0):
    """the lines of statements idx (all when none) of a scene, as psql printed them"""
    bs = stmts(scene, k)
    res = []
    for b in ([bs[i] for i in idx] if idx else bs):
        res += b
    while res and not res[-1].strip():
        res.pop()
    return res


def at(lines, sub, start=0):
    return next(i for i, l in enumerate(lines) if i >= start and sub in l)


def ins_short(lines, keep=2):
    """an INSERT of eight rows shown with its first rows, a … line and the last row (the run typed all of them)"""
    i = at(lines, "VALUES")
    j = at(lines, ";", i + 1)
    return lines[:i + 1 + keep] + ["…"] + lines[j:]


EB1, EB2, EB3, EB4, EB5, EB6 = "1. kant_shop에 들어가기", "2. 자료형 고르기", "3. 넣고 골라 보기", "4. 고치고 지우기", "5. 자주 나는 오류", "6. 실제 상황 예제"
C1, C2, C3, C4, C5, C6 = PG, TEAL, GR, OR, RED, MAG
KS = C("enter2")
ALL = Q("p-insert", 2)          # SELECT * FROM product, all nine rows


def cmd_chip(x, y, text, color, order=None, size=28, attrs="", anim="pop"):
    return p(f"position:absolute;left:{x:.0f}px;top:{y:.0f}px;height:{size + 24}px;padding:0 18px;border-radius:12px;background:{color};font-family:{MONO};font-size:{size}px;font-weight:700;line-height:{size + 24}px;color:#FFFFFF;white-space:nowrap", e(text), bi(anim, order) + attrs)


def note(x, y, w, text, color=SUB, size=26, order=None, attrs=""):
    return p(f"position:absolute;left:{x:.0f}px;top:{y:.0f}px;width:{w}px;font-size:{size}px;line-height:1.5;color:{color}", text, bi("rise", order) + attrs)


def hd(x, y, text, color, size=28, order=None, attrs="", w=None):
    ww = f"width:{w}px;" if w else ""
    return p(f"position:absolute;left:{x:.0f}px;top:{y:.0f}px;{ww}font-size:{size}px;font-weight:700;line-height:1.35;color:{color};white-space:nowrap", text, bi("rise", order) + attrs)


def mono(x, y, text, color=INK, size=26, order=None, attrs="", anim="rise"):
    return p(f"position:absolute;left:{x:.0f}px;top:{y:.0f}px;font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.35;color:{color};white-space:nowrap", e(text), bi(anim, order) + attrs)


def rule(x, y, w, color=LINE, order=None, attrs=""):
    return f'<div{bi("fade", order)}{attrs} style="position:absolute;left:{x}px;top:{y:.0f}px;width:{w}px;height:1px;background:{color}"></div>'


def term_q(lines, x, y, size=24, w=None, tid="t", lh=1.5, marks=None, bar=True, h=None, attrs=""):
    return Term(psql_rows(lines, marks), x, y, size=size, w=w, tid=tid, lh=lh, bar=bar, h=h, attrs=attrs)


def hbox(t, i, sub, color=OR, order=1, pad=6, which="ul"):
    """underline (ul) or pen box (box) around sub on terminal line i"""
    x = t.sx(i, sub)
    w = t.sw(sub)
    if which == "ul":
        return underline(order, x, x + w, t.top(i) + t.lp - 3, color)
    return pen_box(order, round(x - pad - 2), round(t.top(i) + 1), round(w + 2 * pad + 4), round(t.lp - 2), color)


# =====================================================================
# cover
# =====================================================================
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px">',
       p("position:absolute;left:128px;top:300px;font-size:28px;font-weight:700;color:#9DC1E6", "KANT AX/AI 엔지니어 트랙 · 36"),
       f'<h1{SLAM(1)} style="position:absolute;left:128px;top:350px;padding-bottom:14px;font-size:100px;font-weight:900;line-height:1.3;color:#F6F5F1">SQL 1</h1>',
       p("position:absolute;left:128px;top:500px;font-size:52px;font-weight:700;line-height:1.3;color:#F6F5F1", "표에서 골라 보고<br>고치고 지우기"),
       p("position:absolute;left:128px;top:680px;font-size:30px;line-height:1.5;color:#BFC6D4", "PostgreSQL · 자료형, WHERE, ORDER BY,<br>UPDATE, DELETE")]
cl = Q("u-one", 1, 2)
t = term_q(cl, 1000, 330, size=20, w=824, tid="cov-term", lh=1.5)
cov.append(t.html())
cov.append(shine(2, "cov-term"))
W("cover", cov, "36 챕터는 SQL 1이에요. 34에서 PostgreSQL을 켜고 표 하나를 만들어 넣고 전부 꺼내 봤어요. 오늘은 표에서 필요한 줄만 골라 보고, 값을 고치고, 지우는 SQL을 배워요. 그 전에 열마다 어떤 자료형을 골라야 하는지부터 봐요. 오른쪽은 가격이 비어 있던 무선 충전기에 가격을 넣고 확인한 화면이에요. 예제는 35 수업에서 쓴 kant_shop 데이터베이스와 product 표예요." + REAL, ("intro", "들어가기"))

ORDER.append("toc")   # written last, after page numbers are known

# =====================================================================
# why
# =====================================================================
o = frame("why", "들어가기", "가게 일은 표에서 몇 줄만 골라 보고 고치는 일이에요", INK)
t = term_q(ALL, 96, 214, size=26, tid="t-why", lh=1.5)
qs = [("재고가 10개 안 남은 상품은?", "WHERE", ["노트북 거치대", "블루투스 스피커"]),
      ("가장 비싼 상품 3개는?", "ORDER BY · LIMIT", ["27인치 모니터", "기계식 키보드", "웹캠"]),
      ("충전기 가격이 정해졌어요", "UPDATE", ["무선 충전기"]),
      ("웹캠은 이제 안 팔아요", "DELETE", ["웹캠 "])]
texts = [r[1] for r in t.rows]
for k, (q, kw, names) in enumerate(qs):
    for nm in names:
        t.band(at(texts, nm, 2), order=k + 1, color="rgba(242,196,109,.22)" if k < 2 else "rgba(255,156,148,.22)", attrs=DIM("whyb"))
o.append(t.html())
QX = t.x + t.w + 72
for k, (q, kw, names) in enumerate(qs):
    y = 230 + k * 186
    od = k + 1
    o.append(p(f"position:absolute;left:{QX}px;top:{y}px;width:{1824 - QX}px;font-size:30px;font-weight:700;line-height:1.4;color:{INK}", e(q), bi("rise", od) + DIM("why")))
    o.append(cmd_chip(QX, y + 58, kw, [C3, C3, C4, C4][k], od, size=26, attrs=DELAY(150) + DIM("whyc")))
W("why", o, "가게 일은 표에서 몇 줄만 골라 보고 고치는 일이에요. 34에서는 SELECT 별표로 표 전체를 한 번에 봤어요. 상품이 아홉 개일 때는 눈으로 찾을 수 있지만, 상품이 수천 개면 못 해요. 재고가 10개 안 남은 상품만 보고 싶을 때는 WHERE로 줄을 골라요. 가장 비싼 상품 3개는 ORDER BY로 줄을 세우고 LIMIT로 앞에서 세 개만 잘라요. 가격이 정해진 충전기는 UPDATE로 고치고, 더 안 파는 웹캠은 DELETE로 지워요. 오늘 이 네 가지를 차례로 배워요." + REAL)

# =====================================================================
# big picture
# =====================================================================
o = frame("big", "들어가기", "SQL 네 문장으로 표에 넣고, 골라 보고, 고치고, 지워요", INK)
crumbs = [("컨테이너 my-pg", DK), ("데이터베이스 kant_shop", PG), ("표 product", GR)]
cx_ = 96
for k, (c_, col) in enumerate(crumbs):
    w_ = tw(c_, 24, mono=False) + 40
    o.append(p(f"position:absolute;left:{cx_}px;top:206px;height:46px;padding:0 20px;border-radius:23px;background:#FFFFFF;border:2px solid {col};font-size:24px;font-weight:700;line-height:42px;color:{col};white-space:nowrap", e(c_)))
    cx_ += w_ + 16
    if k < 2:
        o.append(p(f"position:absolute;left:{cx_ - 4}px;top:208px;font-size:28px;font-weight:700;color:{GRAY}", "›"))
        cx_ += 26
rows4 = [(str(i), n, f"{pr:,}", str(s)) for i, n, c, pr, s in PRODUCTS[:4]]
sh_, g = sheet(660, 360, ["id", "name", "price", "stock"], rows4, "bg-sheet", [90, 300, 170, 130], size=26, rh=66, name="product", ncol=GR)
o.append(sh_)
TX0, TX1 = 660, 660 + 690
nodes = [("INSERT", "넣기", "34에서 해 봤어요", GRAY, 96, 330, "bg-ins"),
         ("SELECT", "골라 보기", "WHERE · ORDER BY · LIMIT", C3, 1404, 330, "bg-sel"),
         ("UPDATE", "고치기", "SET 열 = 새 값", C4, 96, 680, "bg-upd"),
         ("DELETE", "지우기", "줄을 통째로", C4, 1404, 680, "bg-del")]
for k, (kw, ko, sub, col, x, y, nid) in enumerate(nodes):
    od = k + 1
    o.append(f'<div id="{nid}"{bi("rise", od)} style="position:absolute;left:{x}px;top:{y}px;width:420px;height:180px;background:{CARD};border:3px solid {col};border-radius:20px;box-shadow:{SHADOW}">'
             + p(f"position:absolute;left:30px;top:26px;font-family:{MONO};font-size:40px;font-weight:700;color:{col}", kw)
             + p(f"position:absolute;left:{36 + tw(kw, 40)}px;top:36px;font-size:28px;font-weight:700;color:{INK}", ko)
             + p(f"position:absolute;left:30px;top:104px;font-family:{MONO if k == 1 else SANS};font-size:23px;font-weight:{700 if k == 1 else 400};color:{SUB};white-space:nowrap", e(sub)) + '</div>')
ty0, ty1 = 420, 760
o.append(line_arrow(522, 440, 648, 517, GRAY, 1))
o.append(line_arrow(TX1 + 10, 517, 1396, 440, C3, 2))
o.append(line_arrow(522, 770, 648, 649, C4, 3))
o.append(line_arrow(1398, 770, TX1 + 12, 715, C4, 4))
o.append(caption("3파트에서 SELECT로 골라 보고, 4파트에서 UPDATE와 DELETE로 바꿔요. 그 전에 2파트에서 열마다 담을 값의 종류(자료형)를 정해요.", 900, 5, size=28))
W("big", o, "오늘 쓰는 SQL 네 문장을 한 장에 그렸어요. 위쪽 줄은 지금 있는 곳이에요. 35 수업에서 켠 컨테이너 my-pg 안에, 데이터베이스 kant_shop이 있고, 그 안에 상품 표 product가 있어요. INSERT는 표에 줄을 넣는 문장이에요. 34에서 이미 해 봤어요. SELECT는 표에서 줄을 꺼내 보는 문장인데, 오늘은 WHERE로 고르고, ORDER BY로 줄 세우고, LIMIT로 잘라요. UPDATE는 이미 있는 줄의 값을 고치고, DELETE는 줄을 통째로 지워요. 이 네 가지를 묶어서 넣기, 읽기, 고치기, 지우기라고 해요. 표를 만들 때 열마다 자료형을 정해야 하니 그것부터 봐요.")

# =====================================================================
# part 1: enter kant_shop
# =====================================================================
o = frame("s-enter", EB1, "35의 my-pg에 들어가서 kant_shop을 새로 만들어요", C1)
run_id = D["run"][0]["out"][0]
lines = ["$ " + C("run"), run_id[:12] + "…", "$ " + C("enter")] + Q("enter")
lines.append("kant_shop=# ")
t = term_q(lines, 96, 214, size=23, w=1728, tid="t-enter", lh=1.65)
o.append(t.html())
i_dr = at(lines, "DROP DATABASE IF EXISTS")
i_c = at(lines, "\\c kant_shop")
o += tag(t, i_dr, "35 수업 파일 첫 줄과 같아요", GRAY, 1)
o += tag(t, i_c + 1, "다른 데이터베이스로 옮겨요", PG, 2)
o.append(pen_box(2, round(t.tx - 10), round(t.top(len(lines) - 1) + 1), round(t.sw("kant_shop=#") + 20), round(t.lp - 2), PG))
y2 = t.y + t.h + 40
o.append(p(f"position:absolute;left:96px;top:{y2}px;font-size:28px;font-weight:700;color:{INK}", "다음부터는 -d로 바로 들어가요", bi("rise", 3)))
o.append(mono(96, y2 + 52, "$ " + KS, PG, 30, 3))
o.append(note(96, y2 + 110, 1728, "my-pg가 꺼져 있으면 docker start my-pg로 켜요. 컨테이너가 아예 없으면 위의 docker run부터 쳐요.", SUB, 26, 3))
W("s-enter", o, "35의 my-pg에 들어가서 kant_shop을 새로 만들어요. 35 수업에서 켠 my-pg 컨테이너를 그대로 써요. 컨테이너가 없으면 첫 줄 docker run으로 켜요. 비밀번호는 admin1234이고, pgdata 볼륨을 붙여서 지워도 데이터가 남아요. docker exec로 psql을 열고, 수업 파일 첫 줄처럼 DROP DATABASE IF EXISTS로 예전 kant_shop을 지운 뒤 새로 만들어요. 처음이라 없으면 does not exist, skipping이라는 알림만 나와요. IF EXISTS는 4파트에서 자세히 봐요. 백슬래시 c로 kant_shop에 옮겨 가면 프롬프트 앞 이름이 kant_shop으로 바뀌어요. 다음부터는 -d kant_shop을 붙여서 바로 들어가요." + REAL, ("p1", "kant_shop에 들어가기"))

# =====================================================================
# part 2: data types
# =====================================================================
o = frame("t-map", EB2, "열마다 담을 값의 종류(자료형)를 정해요", C2)
groups = [("글자", "CHAR(n) · VARCHAR(n) · TEXT", "'무선 이어폰'", "상품 이름, 이메일", BL),
          ("정수", "SMALLINT · INTEGER · BIGINT", "35000", "가격, 재고", GR),
          ("소수", "NUMERIC(p, s) · REAL · DOUBLE PRECISION", "3.14", "할인율, 무게", OR),
          ("참과 거짓", "BOOLEAN", "true", "판매 중인지", MAG),
          ("날짜와 시간", "DATE · TIME · TIMESTAMP · TIMESTAMPTZ", "'2026-11-17'", "가입일, 주문 시각", TEAL)]
X_ = [96, 330, 1080, 1440]
o.append(hd(X_[0], 214, "종류", GRAY, 24))
o.append(hd(X_[1], 214, "자료형 이름", GRAY, 24))
o.append(hd(X_[2], 214, "값 예", GRAY, 24))
o.append(hd(X_[3], 214, "어디에", GRAY, 24))
RH_ = 128
for k, (g_, ty, ex, wh, col) in enumerate(groups):
    y = 262 + k * RH_
    ra = bi("rise", 1) + DELAY(k * 90)
    o.append(rule(96, y, 1728))
    o.append(p(f"position:absolute;left:{X_[0]}px;top:{y + 36}px;height:52px;padding:0 20px;border-radius:12px;background:{col};font-size:28px;font-weight:700;line-height:52px;color:#FFFFFF;white-space:nowrap", e(g_), ra))
    o.append(mono(X_[1], y + 40, ty, INK, 28 if len(ty) < 34 else 25, None, ra))
    o.append(mono(X_[2], y + 40, ex, col, 28, None, ra))
    o.append(p(f"position:absolute;left:{X_[3]}px;top:{y + 42}px;font-size:28px;color:{SUB};white-space:nowrap", e(wh), ra))
o.append(rule(96, 262 + 5 * RH_, 1728))
o.append(caption("잘못 고르면 값이 안 들어가거나 계산이 틀려요. 종류마다 실제로 넣어 봐요.", 262 + 5 * RH_ + 40, 2, size=30))
W("t-map", o, "열마다 담을 값의 종류를 정해요. 이걸 자료형이라고 해요. 32에서 INT와 VARCHAR를 봤는데, PostgreSQL에는 더 많아요. 크게 다섯 묶음이에요. 글자는 CHAR, VARCHAR, TEXT, 정수는 SMALLINT, INTEGER, BIGINT, 소수는 NUMERIC, REAL, DOUBLE PRECISION이에요. 참과 거짓은 BOOLEAN, 날짜와 시간은 DATE, TIME, TIMESTAMP, TIMESTAMPTZ예요. 같은 묶음 안에서도 담을 수 있는 길이나 크기, 정확도가 달라요. 잘못 고르면 값이 아예 안 들어가거나, 돈 계산이 틀려요. 다음 장부터 묶음마다 실제로 값을 넣어 봐요.", ("p2", "자료형 고르기"))

# ---- text types
o = frame("t-text", EB2, "CHAR(n)는 남는 칸을 공백으로 채우고, VARCHAR(n)는 길이만 막아요", C2)
tl = Q("t-text")
t = term_q(tl, 96, 214, size=21, tid="t-text", lh=1.55)
i_sel = at(tl, "SELECT * FROM type_text") + 3
t.band(i_sel, order=1, color="rgba(127,209,200,.18)")
o.append(t.html())
i_e1 = at(tl, "character varying(5)")
i_e2 = at(tl, "character(5)")
o.append(hbox(t, i_e1, "ERROR:  value too long for type character varying(5)", RED, 2))
o.append(hbox(t, i_e2, "ERROR:  value too long for type character(5)", RED, 3))
PX0 = 96
py = t.y + t.h + 50
cells_ = [("code CHAR(5)", ["A", "1", "", "", ""], 1, BL), ("name VARCHAR(5)", ["m", "o", "u", "s", "e"], 2, BL)]
for k, (lab, ch, od, col) in enumerate(cells_):
    x0 = PX0 + k * 620
    o.append(mono(x0, py, lab, INK, 26, od))
    for j, c_ in enumerate(ch):
        bg_ = "#FFFFFF" if c_ else "#EEF0F3"
        o.append(f'<div{bi("pop", od)}{DELAY(80 + j * 60)} style="position:absolute;left:{x0 + j * 72}px;top:{py + 50}px;width:64px;height:64px;border-radius:10px;background:{bg_};border:2px solid {col if c_ else "#C9CED8"};font-family:{MONO};font-size:32px;font-weight:700;line-height:60px;text-align:center;color:{INK}">{e(c_) if c_ else "<span style=color:#A3A9B4>·</span>"}</div>')
    o.append(note(x0 + 5 * 72 + 10, py + 58, 230, "남는 세 칸은 공백" if k == 0 else "다섯 칸 꽉 참", SUB, 23, od))
o.append(note(1340, py, 484, "PostgreSQL에서는 셋의 빠르기가 같아요. 길이를 막을 이유가 없으면 TEXT, 막아야 하면 VARCHAR(n)를 써요.", INK, 26, 4))
W("t-text", o, "CHAR는 남는 칸을 공백으로 채우고, VARCHAR는 길이만 막아요. 연습 표 type_text에 세 종류 열을 하나씩 만들었어요. code는 CHAR 5, name은 VARCHAR 5, memo는 TEXT예요. 'A1'을 넣고 꺼내 보면 code 칸이 다섯 칸으로 넓어요. CHAR 5는 늘 다섯 글자라서 남는 세 칸을 공백으로 채워 둬요. VARCHAR 5는 다섯 글자까지만 받아요. keyboard처럼 여덟 글자를 넣으면 value too long 오류가 나요. CHAR 5에 일곱 글자를 넣어도 같은 오류예요. TEXT는 길이 제한이 없어요. PostgreSQL 문서에도 세 가지의 빠르기 차이가 없다고 적혀 있어요. 그래서 보통 TEXT를 쓰고, 이름처럼 너무 길면 안 되는 칸은 VARCHAR에 길이를 적어요. CHAR는 우편번호처럼 길이가 늘 같은 값에만 써요." + REAL)

# ---- integers
o = frame("t-int", EB2, "정수는 담을 수 있는 크기에 따라 세 가지예요", C2)
ints = [("SMALLINT", "2바이트", "-32,768 ~ 32,767", "재고, 나이", 300),
        ("INTEGER", "4바이트", "약 -21억 ~ 21억", "가격, 포인트", 640),
        ("BIGINT", "8바이트", "약 -922경 ~ 922경", "아주 큰 주문 번호", 980)]
for k, (nm, by, rg, us, bw) in enumerate(ints):
    y = 220 + k * 110
    o.append(mono(96, y + 12, nm, GR, 30))
    o.append(p(f"position:absolute;left:300px;top:{y + 18}px;font-size:22px;color:{GRAY};white-space:nowrap", by))
    o.append(f'<div{WIPE(1)}{DELAY(k * 200)} style="position:absolute;left:420px;top:{y + 6}px;width:{bw}px;height:60px;border-radius:12px;background:{GR}{"33" if k else "22"};border:2px solid {GR}"></div>')
    o.append(p(f"position:absolute;left:444px;top:{y + 16}px;font-family:{MONO};font-size:26px;font-weight:700;color:{INK};white-space:nowrap", e(rg), bi("fade", 1) + DELAY(k * 200 + 200)))
    o.append(p(f"position:absolute;left:{420 + bw + 24}px;top:{y + 18}px;font-size:24px;color:{SUB};white-space:nowrap", e(us), bi("fade", 1) + DELAY(k * 200 + 250)))
il = Q("t-int", 0, 1, 2, 3)
t = term_q(il, 96, 570, size=21, tid="t-int", lh=1.55)
o.append(t.html())
o.append(hbox(t, at(il, "smallint out of range"), "ERROR:  smallint out of range", RED, 2))
o.append(hbox(t, at(il, "integer out of range"), "ERROR:  integer out of range", RED, 3))
o += tag(t, at(il, "VALUES (32768"), "32,767보다 1 커요", RED, 2)
o += tag(t, at(il, "2147483648"), "21억을 넘었어요", RED, 3)
o.append(note(t.x + t.w + 44, 590, 1824 - t.x - t.w - 44, "모르겠으면 INTEGER를 써요. 가격도 재고도 21억을 넘을 일은 드물어요.", INK, 26, 4))
W("t-int", o, "정수는 담을 수 있는 크기에 따라 세 가지예요. SMALLINT는 2바이트라서 3만 2767까지만 담아요. INTEGER는 4바이트로 약 21억까지, BIGINT는 8바이트로 약 922경까지 담아요. 막대 길이는 실제 비율이 아니고 크기 순서만 보여 줘요. 연습 표에 세 열을 만들고 각자 가장 큰 값을 넣으면 잘 들어가요. SMALLINT에 1을 더한 3만 2768을 넣으면 smallint out of range, INTEGER 칸에 21억을 넘는 값을 넣으면 integer out of range 오류가 나요. 큰 칸일수록 저장 공간을 더 써요. 보통은 INTEGER를 쓰고, 재고처럼 작은 값은 SMALLINT, 아주 큰 번호는 BIGINT를 써요." + REAL)

# ---- float vs numeric
o = frame("t-float", EB2, "DOUBLE PRECISION은 0.1 + 0.2를 정확히 0.3으로 계산하지 못해요", C2)
fl = Q("t-float")
t = term_q(fl, 96, 214, size=21, tid="t-float", lh=1.6)
i_r = at(fl, "0.30000000000000004")
o.append(t.html())
x_bad = t.sx(i_r, "0.30000000000000004")
o.append(pen_box(1, round(x_bad - 10), round(t.top(i_r) + 1), round(t.sw("0.30000000000000004") + 20), round(t.lp - 2), RED))
x_ok = t.sx(i_r, "0.30")
o.append(pen_box(2, round(t.tx + ttw(fl[i_r][:fl[i_r].rindex("0.30")], 21) - 10), round(t.top(i_r) + 1), round(t.sw("0.30") + 20), round(t.lp - 2), GR))
o += tag(t, i_r, "NUMERIC은 적은 대로 0.30", GR, 2, at=t.end(i_r))
# comparison table with real values
rl = Q("t-real")
r_real = rl[at(rl, "3.1415927")].split("|")
nps = Q("t-numps")
TY = t.y + t.h + 44
cols_ = [("자료형", 96), ("3.14159265358979를 넣으면", 560), ("정확도", 1100), ("어디에", 1440)]
for nm, x in cols_:
    o.append(hd(x, TY, nm, GRAY, 24))
trs = [("REAL", r_real[0].strip(), "약 6자리, 근삿값", "센서 값처럼 조금 틀려도 될 때", OR),
       ("DOUBLE PRECISION", r_real[1].strip(), "약 15자리, 근삿값", "과학 계산", OR),
       ("NUMERIC(5, 2)", next(l.strip() for l in nps if l.strip() == "3.14"), "적은 자리까지 정확", "돈, 포인트, 할인율", GR)]
for k, (nm, v, acc, wh, col) in enumerate(trs):
    y = TY + 48 + k * 78
    ra = bi("rise", 3) + DELAY(k * 90)
    o.append(rule(96, y, 1728, attrs=""))
    o.append(mono(96, y + 20, nm, col, 26, None, ra))
    o.append(mono(560, y + 20, v, INK, 26, None, ra))
    o.append(p(f"position:absolute;left:1100px;top:{y + 22}px;font-size:25px;color:{INK if col == GR else SUB};font-weight:{700 if col == GR else 400};white-space:nowrap", e(acc), ra))
    o.append(p(f"position:absolute;left:1440px;top:{y + 22}px;font-size:25px;color:{SUB};white-space:nowrap", e(wh), ra))
o.append(rule(96, TY + 48 + 3 * 78, 1728))
W("t-float", o, "DOUBLE PRECISION은 0.1 더하기 0.2를 정확히 0.3으로 계산하지 못해요. 연습 표 type_num에 같은 0.1과 0.2를 두 번 넣었어요. 앞의 두 열은 DOUBLE PRECISION, 뒤의 두 열은 NUMERIC이에요. 더해 보면 DOUBLE PRECISION은 0.30000000000000004가 나와요. 컴퓨터가 소수를 2진수로 바꿔 담으면서 아주 작은 차이가 생기기 때문이에요. NUMERIC은 적은 숫자 그대로 계산해서 0.30이 나와요. 아래 표는 원주율을 세 칸에 넣어 본 결과예요. REAL은 약 6자리, DOUBLE PRECISION은 약 15자리까지만 맞고, NUMERIC 5, 2는 소수 둘째 자리까지 정확하게 담아요. 돈처럼 1원도 틀리면 안 되는 값은 NUMERIC을 써요. 계산한 열에는 이름이 없어서 psql이 ?column?으로 보여 줘요." + REAL)

# ---- NUMERIC(p, s)
o = frame("t-numps", EB2, "NUMERIC(5, 2)는 전체 다섯 자리 중 두 자리가 소수점 아래예요", C2)
DX0, DY0, CW = 140, 290, 96
digs = ["9", "9", "9", "9", "9"]
for j, d_ in enumerate(digs):
    x = DX0 + j * (CW + 12) + (40 if j >= 3 else 0)
    col = OR if j >= 3 else C2
    o.append(f'<div{bi("pop", 1)}{DELAY(j * 70)} style="position:absolute;left:{x}px;top:{DY0}px;width:{CW}px;height:{CW}px;border-radius:14px;background:#FFFFFF;border:3px solid {col};font-family:{MONO};font-size:52px;font-weight:700;line-height:{CW - 6}px;text-align:center;color:{INK}">{d_}</div>')
o.append(p(f"position:absolute;left:{DX0 + 3 * (CW + 12) + 2}px;top:{DY0 + 30}px;font-family:{MONO};font-size:56px;font-weight:700;color:{INK}", ".", bi("pop", 1) + DELAY(180)))
x_end = DX0 + 4 * (CW + 12) + 40 + CW
o.append(f'<div style="position:absolute;left:{DX0}px;top:{DY0 - 30}px;width:{x_end - DX0}px;height:14px;border:3px solid {C2};border-bottom:none;border-radius:8px 8px 0 0"></div>')
o.append(hd(DX0, DY0 - 82, "p = 5 · 전체 자릿수", C2, 28))
xs = DX0 + 3 * (CW + 12) + 40
o.append(f'<div{bi("fade", 2)} style="position:absolute;left:{xs}px;top:{DY0 + CW + 16}px;width:{x_end - xs}px;height:14px;border:3px solid {OR};border-top:none;border-radius:0 0 8px 8px"></div>')
o.append(hd(xs - 30, DY0 + CW + 44, "s = 2 · 소수 자리", OR, 28, 2))
o.append(note(DX0, DY0 + CW + 44, 560, "가장 큰 값은 999.99예요", SUB, 26, 2))
# what happens to three inputs
ins = [("3.14159", "3.14", "소수 셋째 자리에서 반올림", GR), ("999.99", "999.99", "딱 맞아요", GR), ("1234.5", "오류", "정수 부분이 네 자리라 못 담아요", RED)]
o.append(hd(1000, 214, "넣은 값", GRAY, 24))
o.append(hd(1260, 214, "담긴 값", GRAY, 24))
for k, (a_, b_, why_, col) in enumerate(ins):
    y = 262 + k * 78
    ra = bi("rise", 3) + DELAY(k * 120)
    o.append(rule(1000, y, 824))
    o.append(mono(1000, y + 18, a_, INK, 30, None, ra))
    o.append(mono(1260, y + 18, b_, col, 30, None, ra) if b_ != "오류" else p(f"position:absolute;left:1260px;top:{y + 18}px;font-size:30px;font-weight:700;color:{RED}", "오류", ra))
    o.append(p(f"position:absolute;left:1480px;top:{y + 24}px;width:344px;font-size:23px;line-height:1.35;color:{SUB}", e(why_), ra))
o.append(rule(1000, 262 + 3 * 78, 824))
nl = Q("t-numps", 1, 2, 3, 4)
t = term_q(nl, 96, 540, size=19, tid="t-numps", lh=1.4)
o.append(t.html())
o.append(hbox(t, at(nl, "numeric field overflow"), "ERROR:  numeric field overflow", RED, 4))
W("t-numps", o, "NUMERIC 5, 2는 전체 다섯 자리 중 두 자리가 소수점 아래예요. 앞 숫자 p는 전체 자릿수, 뒤 숫자 s는 소수점 아래 자릿수예요. 그래서 정수 부분은 세 자리까지만 들어가고, 가장 큰 값은 999.99예요. 3.14159를 넣으면 소수 셋째 자리에서 반올림해서 3.14로 담겨요. 999.99는 딱 맞게 들어가요. 1234.5는 정수 부분이 네 자리라서 numeric field overflow 오류가 나요. DETAIL에는 10의 3제곱, 즉 1000보다 작아야 한다고 적혀 있어요. 원 단위 가격처럼 소수가 없으면 INTEGER로 충분하고, 할인율이나 달러 가격처럼 소수 자리가 정해진 값에 NUMERIC을 써요." + REAL)

# ---- boolean (+ names only)
o = frame("t-bool", EB2, "BOOLEAN은 true와 false를 담고, psql은 t와 f로 보여 줘요", C2)
bl = Q("t-bool")
t = term_q(bl, 96, 214, size=23, tid="t-bool", lh=1.55)
o.append(t.html())
i_t = at(bl, " mouse    | t")
o.append(hbox(t, i_t, "t", MAG, 1, which="box", pad=8))
o.append(hbox(t, i_t + 1, "f", MAG, 1, which="box", pad=8))
o += tag(t, i_t, "true", MAG, 1)
o += tag(t, i_t + 1, "false", MAG, 1)
i_w = at(bl, "WHERE on_sale = true")
o.append(hbox(t, i_w, "on_sale = true", OR, 2))
RX = t.x + t.w + 70
o.append(hd(RX, 230, "이름만 알아 둘 자료형", GRAY, 26))
names_ = [("UUID", "겹치지 않는 긴 아이디", "a0eebc99-9c0b-4ef8-…"), ("JSON", "15의 딕셔너리 모양을 그대로", '{"color": "black"}')]
for k, (nm, ds, ex) in enumerate(names_):
    y = 290 + k * 190
    ra = bi("rise", 3) + DELAY(k * 120)
    o.append(rule(RX, y, 1824 - RX))
    o.append(mono(RX, y + 24, nm, INK, 32, None, ra))
    o.append(p(f"position:absolute;left:{RX}px;top:{y + 78}px;font-size:25px;color:{SUB};white-space:nowrap", e(ds), ra))
    o.append(mono(RX, y + 122, ex, GRAY, 23, None, ra))
o.append(rule(RX, 290 + 2 * 190, 1824 - RX))
o.append(note(RX, 290 + 2 * 190 + 30, 1824 - RX, "자동으로 늘어나는 번호(SERIAL, IDENTITY)는 37에서 배워요.", SUB, 25, 3))
W("t-bool", o, "BOOLEAN은 true와 false를 담고, psql은 t와 f로 보여 줘요. 상품이 지금 할인 중인지처럼 예, 아니요로 답하는 값에 써요. 넣을 때는 따옴표 없이 true, false로 적어요. 꺼내 보면 psql은 짧게 t와 f로 보여 줘요. WHERE on_sale = true로 할인 중인 상품만 고를 수 있어요. WHERE는 3파트에서 자세히 배워요. 오른쪽 두 가지는 이름만 알아 둬요. UUID는 겹치지 않게 만든 긴 아이디이고, JSON은 15에서 배운 딕셔너리 모양 데이터를 그대로 담는 자료형이에요. 자동으로 1, 2, 3 늘어나는 번호는 37 챕터에서 배워요." + REAL)

# ---- date and time
o = frame("t-time", EB2, "TIMESTAMPTZ는 시간대를 기억해서 보는 곳의 시각으로 바꿔 보여 줘요", C2)
tm = [l for l in Q("t-time") if l.strip()]
t = term_q(tm, 96, 206, size=19, tid="t-time", lh=1.42, w=1728)
o.append(t.html())
i_z = at(tm, "Etc/UTC")
o.append(hbox(t, i_z, "Etc/UTC", OR, 1, which="box", pad=8))
o += tag(t, i_z, "컨테이너는 영국 기준 시간(UTC)이에요", OR, 1)
i_s1 = at(tm, "+09")
i_s2 = at(tm, "+00")
o.append(hbox(t, i_s1, "2026-11-17 09:30:00+09", TEAL, 2, which="box", pad=8))
o += tag(t, i_s1, "서울 9시 30분 (+09)", TEAL, 2)
o.append(hbox(t, i_s2, "2026-11-17 00:30:00+00", TEAL, 3, which="box", pad=8))
o += tag(t, i_s2, "같은 순간을 UTC로", TEAL, 3)
o.append(hbox(t, i_s2, "2026-11-17 09:30:00 ", GRAY, 3, which="ul"))
SY = t.y + t.h + 30
kinds = [("DATE", "날짜만"), ("TIME", "시각만"), ("TIMESTAMP", "날짜와 시각"), ("TIMESTAMPTZ", "날짜와 시각, 시간대까지")]
xk = 96
for nm, ds in kinds:
    o.append(mono(xk, SY, nm, C2, 25, 4))
    o.append(p(f"position:absolute;left:{xk + tw(nm, 25) + 14}px;top:{SY + 2}px;font-size:24px;color:{SUB};white-space:nowrap", e(ds), bi("rise", 4)))
    xk += tw(nm, 25) + 14 + tw(ds, 24, mono=False) + 56
W("t-time", o, "TIMESTAMPTZ는 시간대를 기억해서 보는 곳의 시각으로 바꿔 보여 줘요. 먼저 SHOW TIME ZONE을 치면 Etc/UTC가 나와요. 컨테이너는 영국 기준 시간인 UTC로 돌아가서, 한국보다 9시간 늦어요. SET TIME ZONE으로 서울 시간을 고르고 같은 9시 30분을 네 칸에 넣었어요. DATE는 날짜만, TIME은 시각만, TIMESTAMP는 날짜와 시각을, TIMESTAMPTZ는 시간대까지 담아요. 다시 UTC로 바꿔 보면 TIMESTAMP 칸은 그대로 9시 30분이고, TIMESTAMPTZ 칸은 0시 30분 플러스 00으로 바뀌어요. 같은 순간을 UTC 시각으로 보여 준 거예요. 주문 시각처럼 언제 일어났는지가 중요한 값은 TIMESTAMPTZ를 쓰고, 생일이나 가입일처럼 날짜만 있으면 DATE를 써요. SET TIME ZONE은 지금 접속에만 적용돼요." + REAL)

# =====================================================================
# part 3: product table, INSERT, SELECT
# =====================================================================
o = frame("p-create", EB3, "product 표를 만들 때 열 이름 옆에 자료형을 적어요", C3)
cl_ = Q("p-create")
t = term_q(cl_, 96, 214, size=23, tid="t-create", lh=1.45)
o.append(t.html())
whys = {"id INTEGER PRIMARY KEY": ("겹치지 않는 번호, 기본 키(32)", PG),
        "name VARCHAR(100)": ("상품 이름은 100자까지", BL),
        "category VARCHAR(20)": ("분류는 짧게 20자까지", BL),
        "price INTEGER": ("원 단위 가격이라 정수", GR),
        "stock INTEGER": ("재고 개수", GR)}
NX = t.x + t.w + 60
for k, (key, (txt, col)) in enumerate(whys.items()):
    i = at(cl_, key)
    o.append(lspot(k + 1, t.x, t.y, t.w, t.h, t.top(i) - 2, t.lp + 4, bg=T_BG, bar=col))
    o.append(p(f"position:absolute;left:{NX}px;top:{t.cy(i) - 14:.0f}px;font-size:23px;line-height:1.2;font-weight:700;color:{col};white-space:nowrap", e(txt), bi("rise", k + 1)))
o.append(lspot_off(6))
i_v = at(cl_, "character varying(100)")
o.append(hbox(t, i_v, "character varying(100)", OR, 6))
o.append(p(f"position:absolute;left:{NX}px;top:{t.cy(i_v) - 14:.0f}px;font-size:23px;line-height:1.2;font-weight:700;color:{OR};white-space:nowrap", "VARCHAR의 원래 이름", bi("rise", 6)))
i_nn = at(cl_, "| not null")
o.append(p(f"position:absolute;left:{NX}px;top:{t.cy(i_nn) - 14:.0f}px;font-size:23px;line-height:1.2;color:{SUB};white-space:nowrap", "기본 키는 비울 수 없어요(not null)", bi("rise", 6)))
W("p-create", o, "product 표를 만들 때 열 이름 옆에 자료형을 적어요. 35 수업 파일과 같은 이름이에요. id는 정수이고 기본 키예요. 32에서 배운 대로 겹치지 않는 번호예요. name은 상품 이름이라 100자까지, category는 audio, input 같은 짧은 분류라 20자까지로 막았어요. price는 원 단위 가격이라 소수가 필요 없어서 INTEGER, stock도 개수라 INTEGER예요. 줄이 길면 이렇게 여러 줄로 나눠 쳐도 되고, 프롬프트가 kant_shop 괄호 표시로 바뀌다가 세미콜론을 만나면 실행돼요. 백슬래시 d로 보면 VARCHAR가 원래 이름인 character varying으로 나와요. 기본 키인 id에는 not null이 붙어서 비울 수 없어요. 수업 파일의 NOT NULL과 SERIAL은 37에서 배워요." + REAL, ("p3", "넣고 골라 보기"))

o = frame("p-insert", EB3, "여러 줄을 한 번에 넣고, 안 적은 열은 NULL(모름)로 비워 둬요", C3)
il_ = Q("p-insert")
il_ = ins_short(il_, 2)
t = term_q(il_, 96, 210, size=20, tid="t-insert", lh=1.5)
i_v0 = at(il_, "VALUES")
t.band(i_v0 + 1, i_v0 + 4, order=1, color="rgba(127,209,139,.14)")
o.append(t.html())
o += tag(t, at(il_, "INSERT 0 8"), "8줄이 들어갔어요", GR, 1)
i_9 = at(il_, "  9 | ")
xp = t.sx(i_9, "|        |") + t.sw("| ")
o.append(ring(2, xp - 4, t.top(i_9) + 2, t.sw("      "), t.lp - 4, NL))
i_9i = at(il_, "(id, name, category, stock)")
o.append(hbox(t, i_9i, "(id, name, category, stock)", NL, 2))
RX = t.x + t.w + 56
o.append(note(RX, 260, 1824 - RX, "괄호 묶음을 쉼표로 잇고 맨 끝에만 ;를 붙여요.", INK, 26, 1))
o.append(note(RX, 560, 1824 - RX, "price를 적지 않아서 NULL이 들어갔어요. 값이 아직 없다, 모른다는 뜻이고 psql은 빈칸으로 보여 줘요.", INK, 26, 2))
W("p-insert", o, "여러 줄을 한 번에 넣고, 안 적은 열은 NULL로 비워 둬요. INSERT INTO 뒤에 열 이름을 괄호로 적고, VALUES 뒤에 한 줄씩 괄호로 묶어 쉼표로 이어요. 마지막 줄 끝에만 세미콜론을 붙여요. 실제로는 여덟 줄을 다 쳤는데, 화면에서는 가운데를 …로 줄였어요. INSERT 0 8은 여덟 줄이 들어갔다는 뜻이에요. 무선 충전기는 가격이 아직 정해지지 않아서 열 이름에서 price를 뺐어요. 그러면 price 칸에 NULL이 들어가요. NULL은 0도 아니고 빈 글자도 아닌, 값을 모른다는 표시예요. 15의 파이썬 None과 비슷해요. psql은 NULL을 빈칸으로 보여 줘요." + REAL)

# ---- AS and calculated columns
o = frame("a-alias", EB3, "AS로 결과 열에 새 이름을 붙이고, 계산한 값도 열로 꺼내요", C3)
al = Q("a-alias")
t = term_q(al, 96, 206, size=19, tid="t-alias", lh=1.38)
o.append(t.html())
o.append(hbox(t, 0, "name AS 상품명", GR, 1))
o.append(hbox(t, 0, "price AS 가격", GR, 1))
i_h0 = at(al, "상품명     |")
o.append(hbox(t, i_h0, "상품명", GR, 1, which="box", pad=6))
i_c = at(al, "?column?")
o.append(hbox(t, i_c - 1, "price * 3", OR, 2))
o.append(hbox(t, i_c, "?column?", OR, 2, which="box", pad=6))
i_e = at(al, "trailing junk")
o.append(hbox(t, i_e, "trailing junk after numeric literal", RED, 3))
o.append(hbox(t, i_e - 1, "AS 3개가격", RED, 3))
i_q = at(al, 'AS "3개 가격"')
o.append(hbox(t, i_q, 'AS "3개 가격"', GR, 4))
o.append(hbox(t, i_q + 1, "3개 가격", GR, 4, which="box", pad=6))
RX = t.x + t.w + 60
rules_ = [("AS 상품명", "한글 이름도 그냥 써요", GR, 1),
          ("price * 3", "+ - * / 로 계산한 값을 열로", OR, 2),
          ('AS "3개 가격"', "숫자로 시작하거나 띄어 쓰면 큰따옴표", GR, 4)]
for k, (cd, ds, col, od) in enumerate(rules_):
    y = 240 + k * 150
    o.append(mono(RX, y, cd, col, 26, od))
    o.append(p(f"position:absolute;left:{RX}px;top:{y + 46}px;width:{1824 - RX}px;font-size:23px;line-height:1.4;color:{SUB}", e(ds), bi("rise", od)))
o.append(note(RX, 720, 1824 - RX, "글자 값은 작은따옴표, 열 이름은 큰따옴표예요. 5파트에서 다시 봐요.", INK, 24, 4))
W("a-alias", o, "AS로 결과 열에 새 이름을 붙이고, 계산한 값도 열로 꺼내요. 첫 문장은 name을 상품명, price를 가격이라는 이름으로 보여 줘요. 표의 열 이름이 바뀌는 게 아니라 이번 결과에서만 바뀌어요. 한글 이름은 따옴표 없이 써도 돼요. 두 번째 문장처럼 price 곱하기 3을 적으면 세 개 살 때 가격을 계산해서 보여 줘요. 계산한 열은 이름이 없어서 psql이 물음표 column 물음표로 보여 줘요. 이름을 3개가격처럼 숫자로 시작하게 적으면 trailing junk 오류가 나요. 숫자 뒤에 쓸데없는 글자가 붙었다고 읽기 때문이에요. 숫자로 시작하거나 띄어쓰기가 있는 이름은 큰따옴표로 감싸요. WHERE id <= 3은 id가 3 이하인 줄만 고른다는 뜻이고, 다음 장에서 자세히 봐요." + REAL)

# ---- comparison operators
o = frame("w-cmp", EB3, "WHERE 뒤에 조건을 적으면 맞는 줄만 나와요", C3)
ops = [("=", "같다"), ("<>", "다르다"), ("<", "작다"), (">", "크다"), ("<=", "작거나 같다"), (">=", "크거나 같다")]
o.append(f'<div{STAGGER(1)} style="position:absolute;left:96px;top:206px;width:1728px;height:110px;display:flex;flex-direction:row;gap:20px">'
         + "".join(f'<div style="flex:1;height:110px;border-radius:16px;background:{CARD};border:2px solid {LINE};display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px">'
                   + p(f"font-family:{MONO};font-size:36px;font-weight:700;color:{C3}", e(op)) + p(f"font-size:22px;color:{SUB}", e(ds)) + '</div>' for op, ds in ops) + '</div>')
cm = Q("w-cmp")
t = term_q(cm, 96, 340, size=21, tid="t-cmp", lh=1.42)
o.append(t.html())
o.append(hbox(t, 0, "price >= 50000", OR, 2))
o.append(hbox(t, at(cm, "<> 'acc'"), "category <> 'acc'", OR, 3))
RX = t.x + t.w + 56
o.append(note(RX, 380, 1824 - RX, "파이썬의 != 자리에 <>를 써요. !=를 써도 돼요.", INK, 26, 3))
o.append(note(RX, 520, 1824 - RX, "글자 값은 작은따옴표로 감싸요.", SUB, 26, 3))
W("w-cmp", o, "WHERE 뒤에 조건을 적으면 맞는 줄만 나와요. 32에서 WHERE와 등호, 작다를 읽어 봤어요. 오늘은 비교 기호 여섯 개를 다 써요. 같다는 등호 하나예요. 파이썬처럼 두 개를 쓰지 않아요. 다르다는 꺾쇠 두 개를 붙여 쓰고, 파이썬처럼 느낌표 등호를 써도 돼요. 가격이 5만 원 이상인 상품은 price >= 50000으로 골라서 세 개가 나와요. 분류가 acc가 아닌 상품은 category <> 'acc'로 골라요. 글자 값은 작은따옴표로 감싸요. SELECT 뒤에 열 이름을 적으면 그 열만 보여 줘요." + REAL)

# ---- AND / OR
o = frame("w-andor", EB3, "AND는 두 조건이 모두 맞을 때, OR는 하나만 맞아도 골라요", C3)
ao = Q("w-andor")
t = term_q(ao, 96, 214, size=21, tid="t-andor", lh=1.6)
o.append(t.html())
o.append(hbox(t, 0, "category = 'audio' AND stock > 0", OR, 1))
o.append(hbox(t, at(ao, "OR price"), "price < 25000 OR price > 100000", OR, 2))
VX = 1380


def venn(y, mode, od, label):
    a, b = (VX + 130, y + 100), (VX + 270, y + 100)
    r = 90
    fa = f"{C3}55" if mode == "or" else "none"
    s = (f'<svg{bi("fade", od)} viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible">'
         f'<defs><clipPath id="cl-{mode}"><circle cx="{a[0]}" cy="{a[1]}" r="{r}"/></clipPath></defs>'
         f'<circle cx="{a[0]}" cy="{a[1]}" r="{r}" fill="{fa}" stroke="{C3}" stroke-width="4"/>'
         f'<circle cx="{b[0]}" cy="{b[1]}" r="{r}" fill="{fa}" stroke="{C3}" stroke-width="4"/>'
         + (f'<circle cx="{b[0]}" cy="{b[1]}" r="{r}" fill="{C3}88" clip-path="url(#cl-{mode})"/>' if mode == "and" else "")
         + '</svg>')
    return [s, hd(VX, y - 44, label, C3, 30, od)]


o += venn(250, "and", 1, "AND · 둘 다")
o += venn(640, "or", 2, "OR · 하나라도")
W("w-andor", o, "AND는 두 조건이 모두 맞을 때, OR는 하나만 맞아도 골라요. 17의 파이썬 if에서 쓴 and, or와 같아요. 첫 번째는 분류가 audio이면서 재고가 0보다 많은 상품이에요. 블루투스 스피커는 audio지만 재고가 0이라 빠지고, 무선 이어폰 하나만 나와요. 두 번째는 2만 5천 원보다 싸거나 10만 원보다 비싼 상품이에요. 둘 중 하나만 맞아도 나와서 세 개예요. 오른쪽 그림처럼 AND는 두 원이 겹친 곳, OR는 두 원 전체예요." + REAL)

# ---- IN / BETWEEN (morph)
o = frame("w-in", EB3, "IN과 BETWEEN은 긴 조건을 짧게 줄여 써요", C3)
wi = Q("w-in")
CW_ = 1020


def codecard(cid, y, l1, toks, attrs=""):
    return (f'<div id="{cid}"{attrs} style="position:absolute;left:96px;top:{y}px;width:{CW_}px;height:150px;background:{CARD};border:2px solid {LINE};border-radius:16px;padding:26px 34px;font-family:{MONO};font-size:27px;font-weight:700;line-height:1.6;color:{INK};white-space:pre">'
            f'{e(l1)}<br>{toks}</div>')


T = lambda k, s, c=INK: tok(k, e(s), f"color:{c}")
long_in = T("w", "WHERE ") + T("c1", "category") + T("eq1", " = ") + T("a", "'audio'", BL) + T("or", " OR category = ", RED) + T("b", "'input'", BL) + T("sc", ";")
short_in = T("w", "WHERE ") + T("c1", "category") + T("in", " IN (", GR) + T("a", "'audio'", BL) + T("cm", ", ", GR) + T("b", "'input'", BL) + T("cl", ")", GR) + T("sc", ";")
o.append(hd(96, 214, "긴 문장 · 결과 4줄", GRAY, 24))
o.append(codecard("in-long", 256, "SELECT name, category FROM product", long_in, MORPH_FROM()))
o.append(codecard("in-short", 256, "SELECT name, category FROM product", short_in, MORPH(1, "in-long")))
long_bt = T("w", "WHERE ") + T("p1", "price") + T("ge", " >= ", RED) + T("lo", "20000", OR) + T("and", " AND ") + T("p2", "price <= ", RED) + T("hi", "40000", OR) + T("sc", ";")
short_bt = T("w", "WHERE ") + T("p1", "price") + T("bt", " BETWEEN ", GR) + T("lo", "20000", OR) + T("and", " AND ") + T("hi", "40000", OR) + T("sc", ";")
o.append(hd(96, 560, "긴 문장 · 결과 3줄", GRAY, 24))
o.append(codecard("bt-long", 602, "SELECT name, price FROM product", long_bt, MORPH_FROM()))
o.append(codecard("bt-short", 602, "SELECT name, price FROM product", short_bt, MORPH(2, "bt-long")))
r_in = wi[at(wi, "IN ('audio'") + 1:]
r_in = r_in[:at(r_in, "(4 rows)") + 1]
r_bt = wi[at(wi, "BETWEEN 20000") + 1:]
r_bt = r_bt[:at(r_bt, "(3 rows)") + 1]
t1 = term_q(r_in, 1180, 214, size=22, w=644, tid="t-in", lh=1.45)
t2 = term_q(r_bt, 1180, 560, size=22, w=644, tid="t-bt", lh=1.45)
o.append(t1.html())
o.append(t2.html())
o.append(caption("짧게 쓴 문장도 긴 문장과 같은 줄이 나와요. BETWEEN은 양 끝 값을 포함해요.", 900, 3, size=28))
W("w-in", o, "IN과 BETWEEN은 긴 조건을 짧게 줄여 써요. 분류가 audio이거나 input인 상품을 고를 때 OR로 쓰면 category를 두 번 적어야 해요. IN 뒤 괄호에 값을 쉼표로 늘어놓으면 그중 하나라도 맞는 줄을 골라요. 14에서 배운 파이썬 in과 비슷해요. 가격이 2만 원에서 4만 원 사이인 상품은 크거나 같다와 작거나 같다를 AND로 이어도 되고, BETWEEN 2만 AND 4만으로 줄여도 돼요. BETWEEN은 양 끝 값을 포함해요. 오른쪽은 짧게 쓴 문장의 결과예요. 긴 문장도 실제로 실행해 보면 똑같이 네 줄, 세 줄이 나와요." + REAL)

# ---- LIKE / ILIKE
o = frame("w-like", EB3, "LIKE는 % 자리에 아무 글자나 와도 맞아요. ILIKE는 대소문자를 안 가려요", C3)
lk = [l for l in Q("w-like") if l.strip()]
t = term_q(lk, 96, 206, size=19, tid="t-like", lh=1.42)
i_w0 = at(lk, "(0 rows)")
t.band(i_w0, order=1, color="rgba(255,156,148,.18)")
i_u0 = at(lk, "(0 rows)", i_w0 + 1)
t.band(i_u0, order=2, color="rgba(255,156,148,.18)")
i_u1 = at(lk, "USB-C 허브")
t.band(i_u1, order=3, color="rgba(127,209,139,.20)")
o.append(t.html())
o.append(hbox(t, at(lk, "LIKE '무선';"), "LIKE '무선'", RED, 1))
o.append(hbox(t, at(lk, "LIKE 'usb%'"), "LIKE 'usb%'", RED, 2))
o.append(hbox(t, at(lk, "ILIKE 'usb%'"), "ILIKE 'usb%'", GR, 3))
RX = t.x + t.w + 70
pats = [("'%마우스%'", "마우스가 어디든 들어 있으면", ["…", "마우스", "…"]), ("'무선%'", "무선으로 시작하면", ["무선", "…"]), ("'무선'", "딱 무선일 때만 (= 와 같아요)", ["무선"])]
for k, (pt, ds, parts_) in enumerate(pats):
    y = 220 + k * 190
    ra = bi("rise", 1) + DELAY(k * 150)
    o.append(mono(RX, y, pt, C3, 32, None, ra))
    xx = RX
    for pc in parts_:
        wc = 120 if pc == "…" else tw(pc, 28, mono=False) + 40
        o.append(p(f"position:absolute;left:{xx}px;top:{y + 60}px;width:{wc:.0f}px;height:56px;border-radius:12px;background:{'#EEF0F3' if pc == '…' else '#FFFFFF'};border:2px {'dashed' if pc == '…' else 'solid'} {GRAY if pc == '…' else C3};font-size:28px;font-weight:700;line-height:52px;text-align:center;color:{GRAY if pc == '…' else INK}", "%" if pc == "…" else e(pc), ra))
        xx += wc + 10
    o.append(p(f"position:absolute;left:{RX}px;top:{y + 132}px;font-size:24px;color:{SUB};white-space:nowrap", e(ds), ra))
o.append(note(RX, 820, 1824 - RX, "% 대신 _를 쓰면 딱 한 글자 자리예요.", SUB, 25, 3))
W("w-like", o, "LIKE는 퍼센트 자리에 아무 글자나 와도 맞아요. 이름에 마우스가 들어 있는 상품을 찾을 때 등호를 쓰면 이름 전체가 같아야 해서 못 찾아요. LIKE 뒤에 퍼센트 마우스 퍼센트를 적으면 앞뒤에 무엇이 있어도 마우스만 들어 있으면 골라요. 무선 퍼센트는 무선으로 시작하는 이름이에요. 퍼센트를 빼고 LIKE 무선만 적으면 0줄이에요. 퍼센트가 없으면 이름 전체가 딱 무선이어야 해서 등호와 같아요. 김씨 회원을 찾을 때도 김이 아니라 김 퍼센트로 적어요. 그런데 소문자로 usb 퍼센트를 찾으면 0줄이에요. LIKE는 대문자와 소문자를 다르게 보기 때문이에요. ILIKE를 쓰면 대소문자를 가리지 않아서 USB-C 허브가 나와요. 퍼센트 대신 밑줄을 쓰면 딱 한 글자 자리라는 뜻이에요." + REAL)

# ---- NULL
o = frame("w-null", EB3, "비어 있는 값(NULL)은 = 대신 IS NULL로 찾아요", C3)
nl_ = Q("w-null")
t = term_q(nl_, 96, 214, size=21, tid="t-null", lh=1.55)
i_n1 = at(nl_, "IS NULL;") + 3
t.band(i_n1, order=2, color="rgba(127,209,139,.20)")
o.append(t.html())
o.append(hbox(t, 0, "price = NULL", RED, 1))
i_z = at(nl_, "(0 rows)")
o.append(hbox(t, i_z, "(0 rows)", RED, 1, which="box", pad=8))
o += tag(t, i_z, "오류도 없이 0줄", RED, 1)
o.append(hbox(t, at(nl_, "IS NULL;"), "price IS NULL", GR, 2))
i_cnt = at(nl_, "COUNT(*)")
o.append(hbox(t, i_cnt, "COUNT(*)", GR, 3))
o.append(hbox(t, i_cnt + 3, "1", GR, 3, which="box", pad=8))
o += tag(t, i_cnt + 3, "맞는 줄이 몇 개인지만", GR, 3)
RX = t.x + t.w + 70
o.append(f'<div{bi("pop", 1)} style="position:absolute;left:{RX}px;top:240px;width:150px;height:150px;border-radius:24px;background:{NLBG};border:3px dashed {NL};font-family:{MONO};font-size:64px;font-weight:700;line-height:144px;text-align:center;color:{NL}">?</div>')
o.append(note(RX + 180, 250, 1824 - RX - 180, "NULL은 모르는 값이에요. 모르는 값과 같은지 물으면 답도 모름이라 어떤 줄도 안 골라요.", INK, 25, 1))
o.append(note(RX, 470, 1824 - RX, "그래서 비어 있는지는 IS NULL, 값이 있는지는 IS NOT NULL로 물어요.", INK, 26, 2))
o.append(note(RX, 640, 1824 - RX, "COUNT(*)는 줄 수를 세는 함수예요. 합계와 평균 같은 다른 함수는 다음 SQL 챕터에서 배워요.", SUB, 25, 3))
W("w-null", o, "비어 있는 값은 등호 대신 IS NULL로 찾아요. 가격이 없는 상품을 찾으려고 price = NULL을 치면 오류도 안 나고 0줄이 나와요. 이게 함정이에요. NULL은 모르는 값이라서, 모르는 값과 같은지 물으면 답도 모름이 되고 어떤 줄도 골라지지 않아요. 비어 있는지 물을 때는 IS NULL을 써요. 그러면 무선 충전기가 나와요. 반대로 값이 있는 줄만 고를 때는 IS NOT NULL이에요. 파이썬에서 None을 is None으로 확인한 것과 같아요. 마지막 문장은 줄을 보여 주지 않고 몇 줄인지만 세요. COUNT 괄호 별표는 맞는 줄의 개수를 돌려줘요. 앞 장에서 배운 AS로 가격 미정이라는 이름을 붙였어요. 띄어쓰기가 있어서 큰따옴표로 감쌌어요. 오늘은 줄 수 세기만 보고, 합계나 평균은 다음 SQL 챕터에서 배워요." + REAL)

# ---- ORDER BY
o = frame("o-order", EB3, "ORDER BY로 줄을 세워요. DESC를 붙이면 큰 것부터예요", C3)
oa = Q("o-order", 0)
od_ = Q("o-order", 1)
t1 = term_q(oa, 96, 214, size=19, tid="t-asc", lh=1.55)
t2 = term_q(od_, 96 + t1.w + 44, 214, size=19, tid="t-desc", lh=1.55)
o.append(t1.html())
o.append(t2.html())
o.append(hbox(t1, 0, "ORDER BY price", OR, 1))
o.append(hbox(t2, 0, "ORDER BY price DESC", OR, 1))
ia = at(oa, "무선 충전기")
idd = at(od_, "무선 충전기")
o.append(hbox(t1, ia, "무선 충전기", NL, 2, which="box", pad=8))
o.append(hbox(t2, idd, "무선 충전기", NL, 2, which="box", pad=8))
o += tag(t1, ia, "NULL은 맨 뒤", NL, 2, at=t1.sx(ia, "|") + t1.sw("|        ") + 10)
o += tag(t2, idd, "DESC면 맨 앞", NL, 2, at=t2.sx(idd, "|") + t2.sw("|        ") + 10)
SY = t1.y + t1.h + 44
o.append(mono(96, SY, "ORDER BY 열", INK, 28, 3))
o.append(p(f"position:absolute;left:{96 + tw('ORDER BY 열', 28) + 20}px;top:{SY + 2}px;font-size:26px;color:{SUB};white-space:nowrap", "작은 것부터 (ASC, 안 적어도 돼요)", bi("rise", 3)))
o.append(mono(96, SY + 60, "ORDER BY 열 DESC", INK, 28, 3))
o.append(p(f"position:absolute;left:{96 + tw('ORDER BY 열 DESC', 28) + 20}px;top:{SY + 62}px;font-size:26px;color:{SUB};white-space:nowrap", "큰 것부터. 22의 sorted(..., reverse=True)와 같아요", bi("rise", 3)))
W("o-order", o, "ORDER BY로 줄을 세워요. DESC를 붙이면 큰 것부터예요. ORDER BY price는 가격이 싼 것부터 세워요. 작은 것부터 세우는 게 기본이라 ASC는 안 적어도 돼요. 뒤에 DESC를 붙이면 비싼 것부터 세워요. 22에서 배운 sorted에 reverse=True를 준 것과 같아요. 가격이 NULL인 무선 충전기를 봐요. 작은 것부터 세우면 맨 뒤에 오고, DESC로 세우면 맨 앞에 와요. PostgreSQL은 NULL을 가장 큰 값처럼 다뤄요. 비싼 상품을 찾을 때 이게 문제가 되는데, 두 장 뒤에서 풀어요." + REAL)

# ---- two keys
o = frame("o-two", EB3, "기준을 두 개 적으면 앞 기준이 같은 줄끼리 뒤 기준으로 세워요", C3)
tk = Q("o-two")
t = term_q(tk, 96, 214, size=24, tid="t-two", lh=1.55)
grp = {}
for i, l in enumerate(tk):
    m = re.match(r"^ (acc|audio|display|input) ", l)
    if m:
        grp.setdefault(m.group(1), []).append(i)
for k, (g_, ix) in enumerate(grp.items()):
    t.band(ix[0], ix[-1], order=1, color="rgba(127,209,139,.18)" if k % 2 == 0 else "rgba(157,193,230,.16)")
o.append(t.html())
o.append(hbox(t, 0, "category, price DESC", OR, 1))
RX = t.x + t.w + 70
steps = [("1", "category", "abc 순서로 먼저 세워요", 1), ("2", "price DESC", "category가 같은 줄끼리 비싼 것부터", 2)]
for k, (n_, kw, ds, od) in enumerate(steps):
    y = 250 + k * 200
    o.append(p(f"position:absolute;left:{RX}px;top:{y}px;width:56px;height:56px;border-radius:28px;background:{C3};font-size:30px;font-weight:900;line-height:56px;text-align:center;color:#FFFFFF", n_, bi("pop", od)))
    o.append(mono(RX + 76, y + 6, kw, C3, 32, od))
    o.append(note(RX + 76, y + 64, 1824 - RX - 76, ds, INK, 26, od))
i_a1 = at(tk, "acc      | 노트북 거치대")
o.append(underline(2, t.sx(i_a1, "24000") - 4, t.sx(i_a1, "24000") + t.sw("24000") + 4, t.top(i_a1) + t.lp - 3, OR))
o.append(note(RX, 680, 1824 - RX, "22에서 key=lambda m: (-m[1], m[0])로 두 기준을 세운 것과 같아요.", SUB, 25, 3))
W("o-two", o, "기준을 두 개 적으면 앞 기준이 같은 줄끼리 뒤 기준으로 세워요. ORDER BY category, price DESC는 먼저 분류를 abc 순서로 세우고, 분류가 같은 줄끼리는 가격이 비싼 것부터 세워요. 색 띠 하나가 같은 분류 묶음이에요. acc 묶음 안에서 무선 충전기, 노트북 거치대, USB-C 허브 순서예요. 가격이 NULL인 충전기가 DESC라서 맨 앞에 왔어요. 22에서 파이썬 sorted에 두 기준을 튜플로 준 것과 같은 일이에요. DESC는 바로 앞 열에만 붙어요. category는 그대로 작은 것부터예요." + REAL)

# ---- LIMIT / OFFSET
o = frame("o-limit", EB3, "LIMIT은 앞에서 몇 줄만 자르고, OFFSET은 그만큼 건너뛰어요", C3)
lm = Q("o-limit", 0)
t = term_q(lm, 96, 206, size=20, tid="t-top3", lh=1.5)
o.append(t.html())
o.append(hbox(t, 0, "WHERE price IS NOT NULL", NL, 1))
o.append(hbox(t, 0, "LIMIT 3", OR, 1))
o += [x for x in tag(t, 4, "NULL을 빼야 비싼 3개가 맞게 나와요", NL, 1)]
p1 = Q("o-limit", 1)
p2 = Q("o-limit", 2)
ty_ = t.y + t.h + 30
ta = term_q(p1, 96, ty_, size=18, tid="t-p1", lh=1.5)
tb = term_q(p2, 96 + ta.w + 40, ty_, size=18, tid="t-p2", lh=1.5)
o.append(ta.html())
o.append(tb.html())
o.append(hbox(ta, 0, "LIMIT 3", OR, 2))
o.append(hbox(tb, 0, "LIMIT 3 OFFSET 3", OR, 3))
SY = ta.y + ta.h + 30
for j in range(9):
    x = 96 + j * 112
    o.append(p(f"position:absolute;left:{x}px;top:{SY}px;width:100px;height:64px;border-radius:12px;background:#FFFFFF;border:2px solid {LINE};font-family:{MONO};font-size:28px;font-weight:700;line-height:60px;text-align:center;color:{INK}", str(j + 1)))
o.append(f'<div{bi("fade", 2)} style="position:absolute;left:90px;top:{SY - 6}px;width:{3 * 112 - 0}px;height:76px;border-radius:16px;border:4px solid {OR}"></div>')
o.append(f'<div{bi("fade", 3)} style="position:absolute;left:{90 + 3 * 112}px;top:{SY - 6}px;width:{3 * 112}px;height:76px;border-radius:16px;border:4px solid {C3}"></div>')
o.append(hd(96 + 9 * 112 + 30, SY + 14, "1쪽은 LIMIT 3, 2쪽은 OFFSET 3을 더해요. 게시판의 쪽 넘기기예요.", INK, 25, 3))
W("o-limit", o, "LIMIT은 앞에서 몇 줄만 자르고, OFFSET은 그만큼 건너뛰어요. 가장 비싼 상품 3개는 가격이 비싼 순으로 세우고 LIMIT 3으로 앞의 세 줄만 잘라요. 앞 장에서 본 것처럼 DESC로 세우면 가격이 NULL인 충전기가 맨 앞에 와요. 그래서 WHERE price IS NOT NULL로 빼고 세웠어요. 13에서 리스트를 대괄호 콜론 3으로 자른 것과 같아요. 아래는 id 순서로 세 줄씩 보는 장면이에요. LIMIT 3은 1번부터 3번, LIMIT 3 OFFSET 3은 앞의 세 줄을 건너뛰고 4번부터 6번이에요. 게시판에서 쪽을 넘길 때 이렇게 해요. LIMIT을 쓸 때는 ORDER BY를 같이 써야 매번 같은 줄이 나와요." + REAL)

# =====================================================================
# part 4: UPDATE, DELETE, RETURNING, DROP
# =====================================================================
o = frame("u-one", EB4, "UPDATE ... SET으로 값을 바꾸고, WHERE로 바꿀 줄을 골라요", C4)
segs = [("UPDATE product", INK, "바꿀 표", None), ("SET price = 32000", C4, "바꿀 열 = 새 값", None), ("WHERE id = 9;", C3, "바꿀 줄", None)]
o += parts(96, 230, segs, size=44, order=1, lab=26, stagger=True, lw=380)
u1 = Q("u-one")
t = term_q(u1, 96, 440, size=22, tid="t-u1", lh=1.55)
o.append(t.html())
o.append(hbox(t, at(u1, "UPDATE 1"), "UPDATE 1", C4, 2, which="box", pad=8))
o += tag(t, at(u1, "UPDATE 1"), "1줄 바뀌었어요", C4, 2)
RX = t.x + t.w + 80
sh_, g = sheet(RX, 470, ["id", "name", "price"], [("9", "무선 충전기", "32000")], "u1-sheet", [80, 260, 180], size=28, rh=80, name="product", ncol=C3,
               cell_attrs={(0, 2): ' data-start="NULL"'})
o.append(sh_)
o.append(set_text(3, "u1-sheet-r0c2", "32000"))
o.append(note(RX, 470 + g["h"] + 90, 1824 - RX, "바꾸기 전과 후에 같은 WHERE로 SELECT해서 확인했어요.", SUB, 25, 3))
W("u-one", o, "UPDATE SET으로 값을 바꾸고, WHERE로 바꿀 줄을 골라요. 문장은 세 조각이에요. UPDATE 뒤에 표 이름, SET 뒤에 바꿀 열과 새 값, WHERE 뒤에 바꿀 줄의 조건을 적어요. 가격이 비어 있던 9번 무선 충전기의 가격을 3만 2천 원으로 정했어요. 실행하면 UPDATE 1, 한 줄이 바뀌었다는 뜻이 나와요. 바꾸기 전과 후에 같은 WHERE로 SELECT해서 비어 있던 칸이 32000으로 바뀐 걸 확인했어요." + REAL, ("p4", "고치고 지우기"))

o = frame("u-calc", EB4, "SET에 계산식을 쓰면 지금 값에서 더하고 빼요", C4)
uc = Q("u-calc")
t = term_q(uc, 96, 214, size=22, tid="t-uc", lh=1.6)
o.append(t.html())
o.append(hbox(t, 0, "price = price - 5000", C4, 1))
o.append(hbox(t, 0, "stock = stock + 10", C4, 1))
o += tag(t, at(uc, "UPDATE 2"), "audio 2줄이 한 번에", C4, 1)
BY = t.y + t.h + 60
hdr = [("상품", 96), ("price", 640), ("stock", 1000)]
for nm, x in hdr:
    o.append(hd(x, BY, nm, GRAY, 24))
vals = [("무선 이어폰", 35000, 30000, 100, 110), ("블루투스 스피커", 45000, 40000, 0, 10)]
for k, (nm, a, b, c_, d_) in enumerate(vals):
    y = BY + 50 + k * 86
    o.append(rule(96, y, 1300))
    o.append(p(f"position:absolute;left:96px;top:{y + 22}px;font-size:30px;font-weight:700;color:{INK}", e(nm)))
    o.append(p(f"position:absolute;left:640px;top:{y + 20}px;font-family:{MONO};font-size:32px;font-weight:700;color:{C4}", str(b), f' id="uc-p{k}" data-start="{a}"'))
    o.append(p(f"position:absolute;left:1000px;top:{y + 20}px;font-family:{MONO};font-size:32px;font-weight:700;color:{C4}", str(d_), f' id="uc-s{k}" data-start="{c_}"'))
    o.append(set_text(2, f"uc-p{k}", str(b)))
    o.append(set_text(2, f"uc-s{k}", str(d_)))
o.append(rule(96, BY + 50 + 2 * 86, 1300))
o.append(note(1440, BY + 40, 384, "오른쪽 price는 지금 값이에요. 12에서 x = x + 1로 값을 늘린 것과 같아요.", INK, 25, 3))
W("u-calc", o, "SET에 계산식을 쓰면 지금 값에서 더하고 빼요. audio 상품을 5천 원 할인하고 재고를 10개씩 채웠어요. price = price - 5000에서 등호 오른쪽 price는 지금 값이에요. 12에서 x = x + 1로 값을 늘린 것과 같아요. 열 여러 개를 바꿀 때는 쉼표로 이어요. WHERE category = 'audio'에 맞는 줄이 두 개라서 UPDATE 2가 나왔어요. 아래 표는 바꾸기 전 값에서 바뀐 값으로 넘어가는 모습이에요. 바뀐 뒤 값은 SELECT로 확인한 실제 결과예요." + REAL)

o = frame("d-one", EB4, "DELETE FROM은 WHERE에 맞는 줄을 통째로 지워요", C4)
dl = Q("d-one")
t = term_q(dl, 96, 214, size=22, tid="t-del", lh=1.55)
o.append(t.html())
o.append(hbox(t, 0, "DELETE FROM product WHERE id = 8;", C4, 1))
o += tag(t, at(dl, "DELETE 1"), "1줄 지웠어요", C4, 1)
ids_ = [at(dl, f"  {n} | ") for n in (2, 9, 1, 7)]
o.append(hbox(t, ids_[1], " 9 ", OR, 2, which="box", pad=4))
o.append(hbox(t, ids_[2], " 1 ", OR, 2, which="box", pad=4))
o.append(hbox(t, ids_[3], " 7 ", OR, 2, which="box", pad=4))
RX = t.x + t.w + 70
rows_ = [("7", "블루투스 스피커"), ("8", "웹캠"), ("9", "무선 충전기")]
sh_, g = sheet(RX, 250, ["id", "name"], rows_, "d-sheet", [90, 330], size=28, rh=76, name="product", ncol=C3)
o.append(sh_)
o.append(f'<div{bi("fade", 1)} style="position:absolute;left:{RX - 6}px;top:{row_y(g, 1) + 4}px;width:{g["w"] + 12}px;height:{g["rh"] - 8}px;border-radius:10px;background:{RED}22;border:3px solid {RED}"></div>')
o.append(f'<div{bi("wipe", 1)} style="position:absolute;left:{RX + 20}px;top:{row_y(g, 1) + g["rh"] / 2 - 2:.0f}px;width:{g["w"] - 40}px;height:4px;background:{RED}"></div>')
o.append(note(RX, 250 + g["h"] + 110, 1824 - RX, "ORDER BY가 없으면 줄 순서는 정해져 있지 않아요. 바꾼 줄이 뒤로 갔어요.", INK, 26, 2))
W("d-one", o, "DELETE FROM은 WHERE에 맞는 줄을 통째로 지워요. 웹캠을 더 팔지 않아서 id가 8인 줄을 지웠어요. DELETE에는 열 이름을 적지 않아요. 한 칸이 아니라 줄 전체를 지우기 때문이에요. DELETE 1은 한 줄을 지웠다는 뜻이에요. 다시 SELECT해 보면 8번이 없어졌어요. 그런데 순서가 이상해요. 앞에서 UPDATE한 9번, 1번, 7번이 뒤로 갔어요. PostgreSQL은 ORDER BY가 없으면 저장된 순서대로 보여 주는데, 고친 줄은 새로 써지면서 뒤로 가요. 순서가 중요하면 늘 ORDER BY를 붙여요." + REAL)

o = frame("r-ret", EB4, "RETURNING을 붙이면 바뀐 줄을 SELECT 없이 바로 보여 줘요", C4)
rr = Q("r-ret")
t = term_q(rr, 96, 214, size=21, tid="t-ret", lh=1.55)
o.append(t.html())
marks_ = [(0, "RETURNING *", "고친 뒤의 줄"), (at(rr, "RETURNING id, name"), "RETURNING id, name", "지운 줄"), (at(rr, "INSERT INTO product VALUES (10"), "RETURNING *", "넣은 줄")]
RX = t.x + t.w + 60
for k, (i, kw, lab) in enumerate(marks_):
    o.append(hbox(t, i, kw, C4, k + 1))
    o.append(hd(RX, t.cy(i + 3) - 20, lab, C4, 28, k + 1))
o.append(note(RX, max(820, t.cy(marks_[-1][0] + 3) + 50), 1824 - RX, "확인용 SELECT를 한 번 덜 쳐요.", SUB, 25, 3))
W("r-ret", o, "RETURNING을 붙이면 바뀐 줄을 SELECT 없이 바로 보여 줘요. UPDATE 끝에 RETURNING 별표를 붙이면 고친 뒤의 줄 전체가 나오고, 그 아래 UPDATE 1이 찍혀요. 노트북 거치대의 재고를 0으로 바꿨어요. DELETE에 RETURNING id, name을 붙이면 지운 줄의 id와 이름만 보여 줘요. 재고가 0인 노트북 거치대가 지워졌어요. INSERT에도 붙일 수 있어서, 넣은 줄을 바로 확인해요. 확인용 SELECT를 한 번 덜 쳐도 돼요. 이 기능은 PostgreSQL에 있고, 33의 MySQL에는 없어요." + REAL)

o = frame("u-oops", EB4, "WHERE를 빼면 모든 줄이 바뀌고, 되돌리는 명령은 없어요", C4)
ou = Q("u-oops", 1, 2) + [""] + Q("d-oops")
t = term_q(ou, 96, 214, size=20, tid="t-oops", lh=1.5)
o.append(t.html())
o.append(shake(1, "t-oops"))
o.append(hbox(t, 0, "UPDATE product SET price = 0;", RED, 1))
o += tag(t, at(ou, "UPDATE 8"), "8줄 모두 0원", RED, 1)
i_d = at(ou, "DELETE FROM product;")
o.append(hbox(t, i_d, "DELETE FROM product;", RED, 2))
o += tag(t, at(ou, "DELETE 8"), "표가 텅 비었어요", RED, 2)
RX = t.x + t.w + 70
o.append(hd(RX, 230, "바꾸기 전에 같은 WHERE로 먼저 봐요", INK, 30, 3, w=1824 - RX))
habit = [("1", "SELECT * FROM product WHERE id = 3;", "몇 줄이 나오는지 봐요"), ("2", "UPDATE product SET price = 250000", "WHERE id = 3;")]
for k, (n_, c1, c2) in enumerate(habit):
    y = 310 + k * 170
    o.append(p(f"position:absolute;left:{RX}px;top:{y}px;width:52px;height:52px;border-radius:26px;background:{C3};font-size:28px;font-weight:900;line-height:52px;text-align:center;color:#FFFFFF", n_, bi("pop", 3) + DELAY(k * 150)))
    o.append(mono(RX + 72, y + 6, c1, INK, 24, 3, DELAY(k * 150)))
    o.append(p(f"position:absolute;left:{RX + 72}px;top:{y + 52}px;font-family:{MONO if k else SANS};font-size:24px;font-weight:{700 if k else 400};color:{INK if k else SUB};white-space:nowrap", e(c2), bi("rise", 3) + DELAY(k * 150)))
o.append(note(RX, 680, 1824 - RX, "지운 데이터는 다시 INSERT해야 해요. 실습은 연습 데이터로만 해요.", RED, 25, 3))
W("u-oops", o, "WHERE를 빼면 모든 줄이 바뀌고, 되돌리는 명령은 없어요. 모니터 가격만 바꾸려다 WHERE를 빼먹었어요. UPDATE 8, 여덟 줄 모두 0원이 됐어요. DELETE FROM product에서 WHERE를 빼면 표가 텅 비어요. psql은 정말 바꿀 거냐고 묻지 않아요. 지운 데이터는 다시 INSERT하는 수밖에 없어요. 그래서 UPDATE와 DELETE 전에는 같은 WHERE로 SELECT를 먼저 쳐서 몇 줄이 나오는지 봐요. 원하는 줄만 나오면 SELECT 별표 FROM 부분을 UPDATE나 DELETE로 바꿔서 실행해요. 6파트 예제에서 이 순서로 해요." + REAL)

o = frame("d-drop", EB4, "DROP TABLE IF EXISTS는 표가 없어도 오류 없이 넘어가요", C4)
dd = Q("d-drop", 1, 2, 3, 4, 5)
t = term_q(dd, 96, 210, size=21, tid="t-drop", lh=1.42)
i_er = at(dd, "ERROR:")
i_no = at(dd, "NOTICE:")
t.band(i_no, order=2, color="rgba(242,196,109,.16)")
o.append(t.html())
o.append(hbox(t, i_er, 'ERROR:  table "type_text" does not exist', RED, 1))
o += tag(t, i_er - 1, "한 번 더 지우면", RED, 1)
o += tag(t, i_no, "알림만 하고 넘어가요", OR, 2)
o.append(hbox(t, at(dd, "DROP TABLE type_int,"), "type_int, type_num", C4, 3))
o += tag(t, at(dd, "DROP TABLE type_int,") + 1, "쉼표로 여러 표를 한 번에", C4, 3)
dbl = Q("d-dropdb")
ty_ = t.y + t.h + 30
t2 = term_q(dbl, 96, ty_ - 6, size=18, tid="t-dropdb", lh=1.4)
o.append(t2.html())
RX = max(t.x + t.w, t2.x + t2.w) + 60
o.append(note(RX, 240, 1824 - RX, "35 수업 파일의 첫 줄 DROP DATABASE IF EXISTS kant_shop;도 같은 뜻이에요. 처음 실행해도 오류 없이 지나가요.", INK, 25, 4))
W("d-drop", o, "DROP TABLE IF EXISTS는 표가 없어도 오류 없이 넘어가요. 자료형 연습 표 type_text를 지웠어요. 한 번 더 지우려고 하면 표가 없다는 ERROR가 나요. IF EXISTS를 붙이면 없으면 넘어간다는 NOTICE 알림만 나오고 오류가 아니에요. SQL 파일을 처음부터 다시 실행할 때 첫 줄에서 멈추지 않게 이렇게 써요. 표 여러 개는 쉼표로 이어 한 번에 지워요. 데이터베이스도 같아요. 35 수업 파일 첫 줄 DROP DATABASE IF EXISTS kant_shop이 이 뜻이었어요. DROP도 되돌릴 수 없으니 이름을 잘 보고 쳐요." + REAL)

# ---- compare with python
o = frame("c-python", "4. 고치고 지우기 · 비교", "15, 22, 23에서 파이썬으로 하던 일을 SQL 한 문장으로 해요", C4)
rows_ = [("넣기", 'products.append({"id": 10, ...})', "INSERT INTO product VALUES (10, ...);"),
         ("고르기", '[p for p in products if p["price"] >= 50000]', "SELECT * FROM product WHERE price >= 50000;"),
         ("줄 세우기", 'sorted(products, key=lambda p: p["price"], reverse=True)', "ORDER BY price DESC"),
         ("앞에서 3개", "결과[:3]", "LIMIT 3"),
         ("고치기", 'p["price"] = 32000', "UPDATE product SET price = 32000 WHERE id = 9;"),
         ("지우기", "products.remove(p)", "DELETE FROM product WHERE id = 8;"),
         ("비어 있음", "None, is None", "NULL, IS NULL")]
X0, X1, X2 = 96, 330, 1100
o.append(hd(X1, 214, "파이썬 (딕셔너리 리스트 products)", GRAY, 24))
o.append(hd(X2, 214, "SQL (표 product)", GRAY, 24))
for k, (a_, b_, c_) in enumerate(rows_):
    y = 262 + k * 88
    ra = bi("rise", 1) + DELAY(k * 70)
    o.append(rule(96, y, 1728))
    o.append(p(f"position:absolute;left:{X0}px;top:{y + 26}px;font-size:26px;font-weight:700;color:{SUB};white-space:nowrap", e(a_), ra))
    o.append(mono(X1, y + 28, b_, BL, 21 if len(b_) > 40 else 23, None, ra))
    o.append(mono(X2, y + 28, c_, C3 if k < 4 else (C4 if k < 6 else NL), 21 if len(c_) > 40 else 23, None, ra))
o.append(rule(96, 262 + 7 * 88, 1728))
o.append(caption("파이썬 리스트는 프로그램이 끝나면 사라지지만, 표는 볼륨에 남아서 다음 날에도 그대로예요.", 262 + 7 * 88 + 36, 2, size=28))
W("c-python", o, "15, 22, 23에서 파이썬으로 하던 일을 SQL 한 문장으로 해요. 왼쪽은 상품을 딕셔너리 리스트로 담았을 때 쓰던 코드예요. 넣기는 append, 고르기는 23의 컴프리헨션에 if, 줄 세우기는 22의 sorted와 key, reverse예요. 앞에서 세 개는 슬라이싱이에요. 고치기는 딕셔너리 칸에 새 값을 넣었고, 지우기는 remove였어요. 비어 있음은 None이었어요. SQL에서는 같은 일을 표 이름과 조건만 적어서 해요. 가장 큰 차이는 남느냐예요. 파이썬 리스트는 프로그램이 끝나면 사라지지만, 표는 34에서 붙인 볼륨에 남아서 다음 날에도 그대로예요.")

# =====================================================================
# part 5: errors
# =====================================================================
o = frame("x-quote", EB5, "글자 값은 작은따옴표로 감싸요. 큰따옴표는 열 이름으로 읽어요", C5)
xq = Q("x-quote", 0)
xc = Q("x-ctrlc")
xq_all = xq + [""] + xc
t = term_q(xq_all, 96, 214, size=21, tid="t-quote", lh=1.5)
i_open = at(xq_all, "kant_shop'#")
t.band(i_open, order=2, color="rgba(255,156,148,.16)")
i_ok = at(xq_all, "  8 | 웹캠")
t.band(i_ok, order=3, color="rgba(127,209,139,.20)")
o.append(t.html())
o.append(hbox(t, 0, '"웹캠"', RED, 1, which="box", pad=6))
o.append(hbox(t, at(xq_all, 'column "웹캠" does not exist'), 'ERROR:  column "웹캠" does not exist', RED, 1))
o += tag(t, i_open, "따옴표가 열린 채예요", RED, 2)
o.append(hbox(t, i_open, "^C", OR, 2, which="box", pad=6))
RX = t.x + t.w + 60
o.append(note(RX, 240, 1824 - RX, "큰따옴표 안은 열 이름이에요. 그래서 웹캠이라는 열을 찾다가 없다고 해요.", INK, 25, 1))
o.append(note(RX, 520, 1824 - RX, "프롬프트가 '#로 바뀌면 작은따옴표 하나를 안 닫은 거예요. Ctrl+C로 지우고 다시 쳐요.", INK, 25, 2))
W("x-quote", o, "글자 값은 작은따옴표로 감싸요. 큰따옴표는 열 이름으로 읽어요. 웹캠을 큰따옴표로 감싸면 column 웹캠 does not exist, 웹캠이라는 열이 없다는 오류가 나요. 32에서 본 것처럼 MySQL은 큰따옴표도 받아 주지만 PostgreSQL은 열 이름으로 읽어요. HINT 줄은 비슷한 열 이름을 추천하는데 여기서는 상관없어요. 아래는 닫는 작은따옴표를 빼먹은 장면이에요. 엔터를 쳐도 실행되지 않고 프롬프트가 작은따옴표 샵으로 바뀌어요. 문장이 아직 글자 값 안에 있다는 뜻이에요. Ctrl+C를 누르면 쓰던 문장이 지워지고 원래 프롬프트로 돌아와요. 다시 바르게 치면 웹캠 한 줄이 나와요." + REAL, ("p5", "자주 나는 오류"))

o = frame("x-typo", EB5, "열 이름 오타는 HINT가 알려 주고, 빠진 쉼표는 오류 없이 이름을 바꿔요", C5)
xt = Q("x-typo")
t = term_q(xt, 96, 214, size=22, tid="t-typo", lh=1.55)
o.append(t.html())
o.append(hbox(t, 0, "nmae", RED, 1, which="box", pad=6))
i_h = at(xt, "HINT:")
o.append(hbox(t, i_h, 'HINT:  Perhaps you meant to reference the column "product.name".', OR, 1))
i_s = at(xt, "SELECT name price")
o.append(hbox(t, i_s, "name price", RED, 2, which="box", pad=6))
o.append(hbox(t, i_s + 1, "price", RED, 2, which="box", pad=6))
o += tag(t, i_s + 1, "열 이름이 price로 바뀌었어요", RED, 2)
RX = 96
NY = t.y + t.h + 40
o.append(note(RX, NY, 1728, "SELECT name, price처럼 쉼표를 넣어야 두 열이 나와요. 쉼표가 빠지면 뒤 단어를 앞 열의 새 이름으로 읽어요.", INK, 26, 3))
W("x-typo", o, "열 이름 오타는 HINT가 알려 주고, 빠진 쉼표는 오류 없이 이름을 바꿔요. name을 nmae로 잘못 치면 column nmae does not exist 오류가 나고, HINT 줄에서 혹시 product.name이냐고 물어봐 줘요. 오류 아래 화살표는 문장의 어디서 막혔는지 가리켜요. 더 무서운 건 오류가 안 나는 실수예요. name과 price 사이 쉼표를 빼먹으면 두 열이 나오지 않고, 상품 이름이 price라는 이름표를 달고 한 열만 나와요. 오류가 없으니 그냥 넘어가기 쉬워요. 결과의 열 이름이 내가 적은 것과 같은지 꼭 봐요." + REAL)

o = frame("x-type", EB5, "숫자나 날짜 칸에 형식이 다른 글자를 넣으면 invalid input이에요", C5)
xy = Q("x-type") + [""] + Q("t-date-bad")
t = term_q(xy, 96, 214, size=21, tid="t-type", lh=1.55)
o.append(t.html())
o.append(hbox(t, at(xy, "invalid input syntax for type integer: \"24,000\""), 'ERROR:  invalid input syntax for type integer: "24,000"', RED, 1))
o.append(hbox(t, at(xy, "비쌈\"") , 'ERROR:  invalid input syntax for type integer: "비쌈"', RED, 2))
i_ok = at(xy, "UPDATE 1")
o.append(hbox(t, i_ok, "UPDATE 1", GR, 3, which="box", pad=6))
o += tag(t, i_ok, "숫자만 있으면 따옴표가 있어도 들어가요", GR, 3)
o.append(hbox(t, at(xy, "date/time field value out of range"), 'ERROR:  date/time field value out of range: "2026-02-30"', RED, 4))
i_d = at(xy, "type_time (d) VALUES")
o.append(p(f"position:absolute;left:{t.x + t.w + 60}px;top:{t.cy(i_d) - 19:.0f}px;font-size:26px;font-weight:700;color:{RED};white-space:nowrap", "2월 30일은 없어요", bi("rise", 4)))
W("x-type", o, "숫자나 날짜 칸에 형식이 다른 글자를 넣으면 invalid input 오류가 나요. 가격을 24,000처럼 쉼표를 넣어 적으면 INTEGER 칸이 읽지 못해서 오류가 나요. 숫자 칸과 글자를 비교해도 같은 오류예요. 그런데 따옴표 안에 숫자만 있는 '24000'은 PostgreSQL이 숫자로 바꿔서 넣어 줘요. 날짜 칸은 연도 네 자리, 월, 일을 빼기로 이어 적어요. 2월 30일처럼 없는 날짜는 out of range 오류가 나요. 오류 아래 LINE 줄과 화살표가 막힌 값을 가리켜요." + REAL)

# =====================================================================
# part 6: member list
# =====================================================================
o = frame("e-find", EB6, "10월에 가입했는데 전화번호가 없는 회원을 찾아요", C6)
mm = Q("m-make", 2)
mf = Q("m-find", 0)
t = term_q(mm + [""] + mf, 96, 214, size=19, tid="t-find", lh=1.5)
ft = mm + [""] + mf
i_f = at(ft, "WHERE joined BETWEEN")
for nm in ("이도윤", "최지우"):
    t.band(at(ft, nm, i_f), order=2, color="rgba(224,127,176,.18)")
o.append(t.html())
o.append(hbox(t, i_f, "joined BETWEEN '2026-10-01' AND '2026-10-31'", C6, 1))
o.append(hbox(t, i_f, "phone IS NULL", NL, 1))
o.append(note(96, t.y + t.h + 34, 1728, "회원 표 member는 36에서 배운 자료형으로 만들었어요. 가입일 joined는 DATE, 포인트 points는 INTEGER, 이메일 email은 TEXT, 사는 구 region은 VARCHAR(10)이에요.", SUB, 25, 3))
W("e-find", o, "10월에 가입했는데 전화번호가 없는 회원을 찾아요. 이제 실제 상황 예제예요. 회원 여섯 명이 든 member 표를 만들었어요. 가입일 joined는 DATE, 포인트는 INTEGER, 이메일은 TEXT, 전화번호는 VARCHAR 13, 사는 구는 VARCHAR 10이에요. 전화번호를 안 남긴 회원은 NULL이라 빈칸이에요. 10월 가입은 날짜도 BETWEEN으로 고를 수 있어요. 날짜는 작은따옴표로 감싸요. 전화번호가 없는 건 IS NULL이에요. 두 조건을 AND로 이으면 이도윤과 최지우 두 명이 나와요. 이 회원들에게 전화번호를 남겨 달라고 알림을 보낼 수 있어요." + REAL, ("p6", "실제 상황 예제"))

o = frame("e-region", EB6, "DISTINCT를 붙이면 겹치는 줄을 하나만 남겨요", C6)
rg = Q("m-region")
i2 = at(rg, "SELECT DISTINCT region, grade")
left_, right_ = rg[:i2], rg[i2:]
t1 = term_q(left_, 96, 206, size=21, tid="t-reg1", lh=1.42)
t2 = term_q(right_, 96 + t1.w + 44, 206, size=21, tid="t-reg2", lh=1.42)
i_d = at(left_, "SELECT DISTINCT region")
for k, nm in enumerate(left_[:i_d]):
    if nm.strip() == "마포구":
        t1.band(k, order=1, color="rgba(224,127,176,.16)")
o.append(t1.html())
o.append(t2.html())
o.append(hbox(t1, i_d, "DISTINCT", C6, 2))
o.append(hbox(t2, 0, "DISTINCT region, grade", C6, 3))
i_mb = at(right_, "마포구 | basic")
o.append(hbox(t2, i_mb, "마포구 | basic", C6, 3, which="box", pad=6))
o += tag(t2, i_mb, "박서연, 강민서 두 줄이 하나로", C6, 3)
NY = max(t1.y + t1.h, t2.y + t2.h) + 36
o.append(note(96, NY, 1728, "열을 두 개 적으면 두 값의 짝이 겹칠 때만 하나로 합쳐요. 순서는 정해져 있지 않으니 줄을 세우려면 ORDER BY를 붙여요.", INK, 25, 4))
W("e-region", o, "DISTINCT를 붙이면 겹치는 줄을 하나만 남겨요. 회원 표에 사는 구 region 열을 더했어요. 그냥 SELECT하면 여섯 줄에 마포구가 세 번 나와요. SELECT 바로 뒤에 DISTINCT를 붙이면 겹치는 값을 하나만 남겨서 세 줄이 돼요. 이벤트를 어느 구에서 열지 정할 때처럼 어떤 값들이 있는지만 볼 때 써요. 열을 두 개 적으면 구와 등급의 짝이 같을 때만 합쳐요. 마포구 basic은 박서연과 강민서 두 명이라 한 줄이 됐고, 마포구 silver는 따로 남아서 다섯 줄이에요. DISTINCT 결과의 순서는 정해져 있지 않아요. 순서가 필요하면 ORDER BY를 붙여요." + REAL)

o = frame("e-grade", EB6, "포인트 3만 이상 회원의 등급을 gold로 올려요. SELECT로 먼저 봐요", C6)
mg = Q("m-grade")
t = term_q(mg, 96, 214, size=19, tid="t-grade", lh=1.6)
o.append(t.html())
o.append(hbox(t, 0, "WHERE points >= 30000 AND grade <> 'gold'", C6, 1))
o += tag(t, 3, "2명이 맞아요", C6, 1, at=t.end(4) + 20)
i_u = at(mg, "UPDATE member")
o.append(hbox(t, i_u, "WHERE points >= 30000 AND grade <> 'gold'", C6, 2))
o.append(hbox(t, i_u, "RETURNING name, grade, points", C4, 3))
o += tag(t, i_u + 3, "같은 2명이 gold로", C4, 3)
NY = t.y + t.h + 40
o.append(note(96, NY, 1728, "1. 같은 WHERE로 SELECT해서 몇 명인지 보고 2. SELECT * FROM을 UPDATE ... SET으로 바꿔 실행하고 3. RETURNING으로 바뀐 줄을 확인해요.", INK, 26, 4))
W("e-grade", o, "포인트 3만 이상 회원의 등급을 gold로 올려요. 4파트에서 본 사고를 막는 순서로 해요. 먼저 같은 WHERE로 SELECT를 쳐요. 포인트가 3만 이상이고 아직 gold가 아닌 회원은 김하늘과 박서연 두 명이에요. 정우진은 이미 gold라서 빠졌어요. 원하는 사람만 나왔으니 같은 WHERE를 그대로 두고 UPDATE로 바꿔요. RETURNING을 붙여서 바뀐 두 줄을 바로 확인해요. UPDATE 2, SELECT에서 본 숫자와 같아요." + REAL)

o = frame("e-leave", EB6, "메일 받을 회원을 고르고, 탈퇴한 회원을 지워요", C6)
ml = Q("m-find", 1) + [""] + Q("m-leave", 1, 2)
t = term_q(ml, 96, 214, size=19, tid="t-leave", lh=1.5)
o.append(t.html())
o.append(hbox(t, 0, "email ILIKE '%@gmail.com'", C6, 1))
i_G = at(ml, "jung@Gmail.com", 1)
o.append(hbox(t, i_G, "jung@Gmail.com", OR, 1, which="box", pad=6))
o += tag(t, i_G, "대문자 G도 찾았어요", OR, 1)
i_d = at(ml, "DELETE FROM member")
o.append(hbox(t, i_d, "DELETE FROM member WHERE id = 4 RETURNING *;", C4, 2))
o += tag(t, at(ml, "DELETE 1"), "지운 줄이 남아 보여요", C4, 2)
i_l = at(ml, "ORDER BY joined DESC LIMIT 3")
o.append(hbox(t, i_l, "ORDER BY joined DESC LIMIT 3", C3, 3))
o += tag(t, i_l + 3, "최근 가입 3명", C3, 3)
W("e-leave", o, "메일 받을 회원을 고르고, 탈퇴한 회원을 지워요. gmail 회원에게 쿠폰 메일을 보내려고 해요. 정우진은 이메일을 대문자 G로 적었어요. LIKE로 찾으면 빠지지만 ILIKE를 쓰면 대소문자를 가리지 않아서 세 명이 다 나와요. ORDER BY name으로 이름순으로 세웠어요. 최지우 회원은 탈퇴를 신청했어요. id로 한 명만 지우고 RETURNING 별표로 지운 줄을 보여 줘요. 혹시 잘못 지웠으면 이 줄을 보고 다시 넣을 수 있어요. 마지막은 가입일을 최근 순으로 세워 세 명만 봤어요. DATE 칸도 ORDER BY로 세울 수 있어요." + REAL)

# =====================================================================
# wrap-up
# =====================================================================
o = frame("n-next", "정리", "37에서는 잘못된 값이 아예 못 들어오게 표를 설계해요", INK)
today = [("가격이 NULL인 상품이 들어갔어요", "NOT NULL"), ("같은 이메일 회원이 두 명이어도 막지 않아요", "UNIQUE"), ("가격에 -5000을 넣어도 들어가요", "CHECK (price >= 0)"),
         ("가입일을 매번 손으로 적어요", "DEFAULT now()"), ("id 번호를 매번 손으로 적어요", "SERIAL · IDENTITY"), ("주문 표가 없는 회원을 가리켜도 몰라요", "FOREIGN KEY")]
o.append(hd(96, 214, "오늘 본 빈틈", GRAY, 24))
o.append(hd(1000, 214, "37에서 배울 막는 법", GRAY, 24))
for k, (a_, b_) in enumerate(today):
    y = 262 + k * 86
    o.append(rule(96, y, 1728))
    o.append(p(f"position:absolute;left:96px;top:{y + 24}px;font-size:27px;color:{INK};white-space:nowrap", e(a_), bi("rise", 1) + DELAY(k * 70)))
    o.append(mono(1000, y + 24, b_, C3, 27, None, bi("pop", 2) + DELAY(k * 70)))
o.append(rule(96, 262 + 6 * 86, 1728))
o.append(note(96, 262 + 6 * 86 + 34, 1728, "그다음에는 표 두 개를 잇는 JOIN, 줄을 묶어 세는 GROUP BY와 SUM, AVG를 배워요. 오늘은 이름만 알아 둬요.", SUB, 26, 3))
W("n-next", o, "37에서는 잘못된 값이 아예 못 들어오게 표를 설계해요. 오늘 왼쪽 같은 빈틈을 봤어요. 가격이 NULL인 상품이 들어갔고, 같은 이메일로 회원이 두 번 가입해도 막을 방법이 없었어요. 가격에 음수를 넣어도 들어가고, 가입일과 id를 매번 손으로 적었어요. 37에서는 표를 만들 때 NOT NULL, UNIQUE, CHECK 같은 제약 조건을 붙여서 이런 값이 들어오면 오류가 나게 해요. 번호를 자동으로 매기는 SERIAL과 IDENTITY, 표끼리 잇는 FOREIGN KEY도 배워요. 그다음에는 두 표를 합쳐 보는 JOIN과, 줄을 묶어 세는 GROUP BY와 SUM, AVG를 배워요.", ("outro", "정리"))

o = frame("trouble", "정리", "막히면 이렇게 풀어요", RED)
tr = [('column "웹캠" does not exist', "글자 값을 큰따옴표로 감쌌어요", "작은따옴표로 '웹캠'"),
      ("프롬프트가 '#로 바뀜", "작은따옴표를 안 닫았어요", "Ctrl+C 뒤 다시 치기"),
      ("value too long for type …", "VARCHAR(n), CHAR(n)보다 긴 글자예요", "길이를 늘리거나 TEXT"),
      ("smallint / integer out of range", "정수 칸이 담을 수 있는 크기를 넘었어요", "INTEGER나 BIGINT"),
      ("invalid input syntax for type integer", "숫자 칸에 24,000 같은 글자를 넣었어요", "숫자만 24000"),
      ("= NULL인데 (0 rows)", "NULL은 =로 비교할 수 없어요", "IS NULL"),
      ("UPDATE 8, DELETE 8", "WHERE를 빼서 모든 줄이 바뀌었어요", "SELECT로 먼저 확인")]
o.append(hd(96, 214, "이런 글이 보이면", GRAY, 24))
o.append(hd(1300, 214, "이렇게 해요", GRAY, 24))
for i, (q, a_, c_) in enumerate(tr):
    y = 262 + i * 88
    ra = bi("rise", 1) + DELAY(i * 70)
    o.append(rule(96, y, 1728))
    monoq = not any(0xAC00 <= ord(ch) <= 0xD7A3 for ch in q)
    o.append(p(f"position:absolute;left:96px;top:{y + 10}px;width:1180px;{'font-family:' + MONO + ';font-size:24px;' if monoq else 'font-size:25px;'}font-weight:700;color:{RED};white-space:nowrap", e(q), ra))
    o.append(p(f"position:absolute;left:96px;top:{y + 50}px;width:1180px;font-size:23px;color:{SUB}", e(a_), ra))
    o.append(p(f"position:absolute;left:1300px;top:{y + 28}px;width:524px;font-size:25px;font-weight:700;color:{INK};white-space:nowrap", e(c_), ra))
o.append(rule(96, 262 + len(tr) * 88, 1728))
o.append(caption("오류 아래 LINE 줄의 화살표(^)가 막힌 자리를 가리켜요. 그 자리부터 봐요.", 262 + len(tr) * 88 + 30, 2, size=28))
W("trouble", o, "막히면 이렇게 풀어요. 열이 없다는 오류인데 내가 적은 건 값이었다면 큰따옴표를 쓴 거예요. 작은따옴표로 바꿔요. 프롬프트가 작은따옴표 샵으로 바뀌면 따옴표를 안 닫은 거라 Ctrl+C로 지우고 다시 쳐요. value too long은 칸의 길이보다 긴 글자, out of range는 정수 칸이 담을 크기를 넘은 거예요. invalid input syntax는 숫자 칸에 쉼표나 글자를 넣었을 때 나요. 등호 NULL은 오류 없이 0줄이 나오니 IS NULL로 바꿔요. UPDATE나 DELETE 뒤 숫자가 생각보다 크면 WHERE를 빼먹은 거예요. 되돌릴 수 없으니 늘 SELECT로 먼저 확인해요. 어떤 오류든 LINE 줄의 화살표가 막힌 자리를 가리켜요.")

o = frame("cheatsheet", "정리", "한 장 요약", INK)
groups = [("자료형 고르기", C2, [("VARCHAR(n) · TEXT", "글자, 길이를 막을 때만 n"), ("INTEGER (SMALLINT · BIGINT)", "정수, 21억까지"), ("NUMERIC(p, s)", "돈처럼 정확해야 하는 소수"), ("BOOLEAN · DATE · TIMESTAMPTZ", "참거짓, 날짜, 시간대 있는 시각")]),
          ("골라 보기", C3, [("WHERE = <> < >= AND OR", "조건에 맞는 줄"), ("IN (...) · BETWEEN a AND b", "긴 조건 줄이기"), ("LIKE '%글자%' · ILIKE · IS NULL", "글자 찾기, 빈 값"), ("ORDER BY 열 DESC LIMIT 3 OFFSET 3", "줄 세우고 자르기"), ("AS 새이름 · DISTINCT · COUNT(*)", "열 이름 붙이기, 겹침 빼기, 줄 수 세기")]),
          ("고치고 지우기", C4, [("UPDATE 표 SET 열 = 값 WHERE ...", "값 바꾸기"), ("DELETE FROM 표 WHERE ...", "줄 지우기"), ("... RETURNING *", "바뀐 줄 바로 보기"), ("DROP TABLE IF EXISTS 표", "없어도 오류 없이")])]
GW = [560, 560, 560]
gx_ = [96, 96 + 560 + 24, 96 + 2 * (560 + 24)]
for i, (t_, c, rows) in enumerate(groups):
    x = gx_[i]
    o.append(p(f"position:absolute;left:{x}px;top:220px;font-size:30px;font-weight:700;color:{c}", e(t_)))
    o.append(f'<div style="position:absolute;left:{x}px;top:270px;width:{GW[i]}px;height:3px;background:{c}"></div>')
    for j, (k, d_) in enumerate(rows):
        y = 296 + j * 100
        fs = 21 if tw(k, 21) < GW[i] - 10 else 18
        o.append(p(f"position:absolute;left:{x}px;top:{y}px;width:{GW[i]}px;font-family:{MONO};font-size:{fs}px;font-weight:700;color:{INK};white-space:nowrap", e(k)))
        o.append(p(f"position:absolute;left:{x}px;top:{y + 42}px;width:{GW[i]}px;font-size:23px;color:{SUB}", e(d_)))
o.append(caption("UPDATE와 DELETE 전에는 같은 WHERE로 SELECT부터 쳐요.", 820, None, size=32))
o.append(caption("37에서는 제약 조건으로 잘못된 값이 못 들어오게 표를 설계해요.", 880, None, size=28, color=SUB))
W("cheatsheet", o, "오늘 쓴 것을 세 묶음으로 모았어요. 왼쪽은 자료형이에요. 글자는 VARCHAR나 TEXT, 정수는 INTEGER, 돈처럼 정확해야 하는 소수는 NUMERIC, 시각은 TIMESTAMPTZ예요. 가운데는 골라 보기예요. WHERE에 비교 기호와 AND, OR를 쓰고, IN과 BETWEEN으로 줄여 쓰고, LIKE와 ILIKE로 글자를 찾고, 빈 값은 IS NULL로 찾아요. ORDER BY로 세우고 LIMIT과 OFFSET으로 잘라요. AS로 결과 열에 이름을 붙이고, DISTINCT로 겹치는 줄을 빼고, COUNT 별표로 줄 수를 세요. 오른쪽은 고치고 지우기예요. UPDATE와 DELETE에는 꼭 WHERE를 붙이고, RETURNING으로 바뀐 줄을 바로 봐요. 가장 중요한 습관은 바꾸기 전에 같은 WHERE로 SELECT부터 치는 거예요. 다음 37에서는 제약 조건을 배워요.")

# =====================================================================
# toc
# =====================================================================
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
PL = [(C1, EB1[3:], "my-pg, DROP DATABASE IF EXISTS, CREATE DATABASE, \\c, -d", "s-enter", "s-enter"),
      (C2, EB2[3:], "CHAR·VARCHAR·TEXT, SMALLINT·INTEGER·BIGINT, NUMERIC·REAL·DOUBLE, BOOLEAN, DATE·TIMESTAMPTZ", "t-map", "t-time"),
      (C3, EB3[3:], "CREATE TABLE, INSERT, AS·계산 열, WHERE, AND·OR, IN, BETWEEN, LIKE, IS NULL, COUNT(*), ORDER BY, LIMIT", "p-create", "o-limit"),
      (C4, EB4[3:], "UPDATE, DELETE, RETURNING, WHERE를 뺀 사고, DROP ... IF EXISTS, 파이썬과 비교", "u-one", "c-python"),
      (C5, EB5[3:], "큰따옴표와 닫지 않은 따옴표, 열 이름 오타와 빠진 쉼표, 자료형이 안 맞는 값", "x-quote", "x-type"),
      (C6, EB6[3:], "회원 표에서 찾기, DISTINCT로 사는 구 보기, 등급 올리기, 메일 보낼 회원과 탈퇴", "e-find", "e-leave")]
plist = [x for x in PL if x[3] in page and x[4] in page]
o = frame("toc", "", "오늘의 순서", INK)
for i, (c, h, s_, a, b) in enumerate(plist):
    y = 214 + i * 112
    o.append(rule(96, y, 1728))
    o.append(p(f"position:absolute;left:96px;top:{y + 22}px;width:80px;font-size:48px;font-weight:900;line-height:1.5;color:{c}", str(i + 1)))
    o.append(p(f"position:absolute;left:190px;top:{y + 18}px;font-size:34px;font-weight:700;color:{INK}", e(h)))
    o.append(p(f"position:absolute;left:190px;top:{y + 70}px;font-size:22px;color:{SUB};white-space:nowrap", e(s_)))
    o.append(p(f"position:absolute;left:1524px;top:{y + 40}px;width:300px;text-align:right;font-size:28px;font-weight:700;color:{GRAY}", f"{page[a]}쪽" if a == b else f"{page[a]}–{page[b]}쪽"))
o.append(rule(96, 214 + len(plist) * 112, 1728))
if "n-next" in page:
    o.append(p(f"position:absolute;left:96px;top:{214 + len(plist) * 112 + 34}px;font-size:26px;color:{SUB}", f"{page['why']}–{page['big']}쪽은 들어가기, {page['n-next']}–{page['cheatsheet']}쪽은 다음에 배울 것, 막힐 때, 한 장 요약이에요."))
o = [x for x in o if 'id="eyebrow"' not in x]
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(o) + f"\n<aside>{e('여섯 파트로 나눴어요. 1파트에서 kant_shop 데이터베이스에 들어가요. 2파트에서 자료형을 하나씩 넣어 보며 골라요. 3파트에서 product 표를 만들고 WHERE, ORDER BY, LIMIT로 골라 봐요. 4파트에서 UPDATE와 DELETE로 고치고 지우고, 파이썬으로 하던 일과 비교해요. 5파트는 자주 나는 오류, 6파트는 회원 표로 하는 실제 상황 예제예요.')}</aside>\n</section>\n")

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-17T00:00:00Z"}, "lists": "css", "title": "SQL 1 (PostgreSQL에서 골라 보고 고치기)", "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
for w_ in WARN:
    print("WARN", w_)
print(len(ORDER), "slides")
