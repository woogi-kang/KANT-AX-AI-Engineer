r"""Generates every slide of the SQL 2 deck (37, PostgreSQL constraints) and slides/deck.json.

Story: 36 made tables with no rules, so a table took a duplicate id, the same e-mail twice, an empty name and a
negative age. A constraint is a gatekeeper in front of the table: every INSERT, UPDATE and DELETE passes it, and a
row that breaks a rule is turned away with an ERROR line naming the rule. Part 1 NOT NULL and DEFAULT, part 2 UNIQUE,
CHECK and naming a rule, part 3 PRIMARY KEY with SERIAL, IDENTITY and a composite key, part 4 FOREIGN KEY between
member and orders (RESTRICT, CASCADE, SET NULL), part 5 ALTER TABLE, part 6 errors and traps, then the shopping cart
of 28 (product, cart) moved into member, product and cart_item tables.
Names follow 35 and 36: container my-pg, database kant_shop, tables member and product. Products are the ones of 28's
product.py with English names (psql pads Hangul by two columns and the slide font draws it narrower).

Every psql line comes from tools/demo.py (real postgres:18, in tools/out.json).
Usage (in 37-sql-constraints): python3 tools/gen.py slides
"""
import html, json, os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from highlight import (spot, spot_off, cursor, cursor_off, ring, box as pen_box, underline, text as set_text, keys, COUNT,  # noqa: E402
                       SLAM, SLIDE, DIM, DELAY, PATH, STAGGER, WIPE, MARK, MORPH, MORPH_FROM, tok,
                       pulse, shine, shake, zoom, zoom_off, lspot, lspot_off, link)

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT):
    if f.endswith(".html"):
        os.remove(os.path.join(OUT, f))
HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "out.json")))
sys.path.insert(0, HERE)


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
REAL = " psql 화면은 tools/demo.py로 실제 postgres:18 컨테이너에서 실행한 결과예요."


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
        if len(l) > cols:
            w = textwrap.wrap(l, cols - 8, break_on_hyphens=False, drop_whitespace=True)
            out += [w[0]] + ["        " + x for x in w[1:]]
        else:
            out.append(l)
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
        self.tws = [tw(r[1], size) for r in self.rows]
        self.w = w or round(max(self.tws) + 2 * self.PX + room)
        self.h = h or round(2 * self.PT + self.bar + len(self.rows) * self.lp)
        self.inner = []
        if x + self.w > 1824 and not bleed:
            WARN.append(f"{tid}: terminal right edge {x + self.w}")
        for i, t_ in enumerate(self.tws):
            if self.tx + t_ > x + self.w - 10 and not bleed:
                WARN.append(f"{tid}: line {i} '{self.rows[i][1][:30]}' runs past the terminal ({self.tx + t_:.0f} > {x + self.w - 10})")
        if y + self.h > 1040:
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
        return self.tx + tw(t[:t.index(sub)], self.size)

    def sw(self, sub):
        return tw(sub, self.size)

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
            o.append(p(f"position:relative;font-size:{self.size}px;line-height:{self.lp:.0f}px;height:{self.lp:.0f}px;white-space:pre;{wt}color:{col}", h))
        o.append('</div>')
        return "".join(o)


LC = {BL: "#6F9BF5", GR: "#5CC287", OR: "#E3A84A", RED: "#F07A72", TEAL: "#4FB8C2", GRAY: "#9AA3B5", MAG: "#E07FB0", DK: "#6F9BF5"}


def tag(t, i, text, color, order=None, at=None, gap=44, size=None):
    """A pill on terminal line i: dot right after the text, a short leader, then the words."""
    x0 = at if at is not None else t.end(i)
    cy = t.cy(i)
    size = size or (23 if t.lp >= 36 else 19)
    ph = size + 17 if size == 23 else size + 12
    pw = tw(text, size, mono=False) + 30
    px = x0 + gap
    if px + pw > t.x + t.w - 14:
        WARN.append(f"{t.tid}: tag '{text}' ends at {px + pw:.0f}, terminal ends {t.x + t.w}")
    lc = LC.get(color, color)
    return [f'<div{bi("fade", order)} style="position:absolute;left:{x0 + 12:.0f}px;top:{cy - 5:.0f}px;width:{gap - 12:.0f}px;height:10px">'
            f'<div style="position:absolute;left:0;top:0;width:10px;height:10px;border-radius:5px;background:{lc}"></div>'
            f'<div style="position:absolute;left:10px;top:4px;width:{gap - 22:.0f}px;height:2px;background:{lc}"></div></div>',
            p(f"position:absolute;left:{px:.0f}px;top:{cy - ph / 2:.0f}px;height:{ph}px;padding:0 {13 if size < 23 else 15}px;border-radius:{8 if size < 23 else 10}px;background:{color};font-family:{SANS};font-size:{size}px;font-weight:700;line-height:{ph}px;color:#FFFFFF;white-space:nowrap", e(text), bi("pop", order))]


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
# chapter 34 helpers
# =====================================================================
PG, PGBG = "#336791", "#E6EDF5"      # PostgreSQL's own blue
MY, MYBG = "#00758F", "#E2F1F5"      # MySQL (33), only on the comparison slides
VO, VOBG = "#B26A00", "#FBF0DF"      # volume (보관함) and the primary key
US, USBG = "#A23B72", "#F7E6EF"      # accounts
P_KS = "~/kant-shop"
ORD = [("1", "latte", "2"), ("2", "americano", "1")]
COLS = ["id", "menu", "qty"]
TYPES = ["INT", "VARCHAR(20)", "INT"]
PROMPT_RE = re.compile(r"^([a-z0-9_]+)(=#|-#|=>|->|\(#) (.*)$")
ROOT_RE = re.compile(r"^(root@[0-9a-f]+:/)# ?(.*)$")
ERR_RE = re.compile(r"^(ERROR|psql: error|FATAL|Error|docker: |OCI runtime|connection to server|DETAIL|HINT|cannot attach|lstat|go-yaml|bash: )")


def psql_rows(lines, marks=None, err=True):
    """terminal rows for psql lines; marks maps a row index to the mark dict of that row"""
    marks = marks or {}
    out = []
    for i, l in enumerate(lines):
        mk = marks.get(i)
        m, r = PROMPT_RE.match(l), ROOT_RE.match(l)
        if m:
            row = ("m", m.group(1) + m.group(2), m.group(3))
        elif r:
            row = ("#", r.group(1), r.group(2))
        elif err and (ERR_RE.match(l.strip()) or (out and out[-1][0] == "e" and l.startswith("        "))):
            row = ("e", l)
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
    # psql prompt rows are bold like shell prompts
    return h.replace('white-space:pre;color:#F2C46D"><span style="color:#9DC1E6">', 'white-space:pre;font-weight:700;color:#F2C46D"><span style="color:#9DC1E6">')


Term.html = _html


def S(scene, k=0, drop_banner=True):
    """the real lines of an interactive session; the two banner lines psql prints first are dropped"""
    out = [l.rstrip() for l in D[scene][k]["out"]]
    res = []
    for i, l in enumerate(out):
        if drop_banner and (l.startswith("psql (18") or l.startswith('Type "help" for help.')):
            continue
        res.append(l)
    # a blank line left behind by the banner
    res = [l for i, l in enumerate(res) if not (l == "" and (i == 0 or PROMPT_RE.match(res[i + 1] if i + 1 < len(res) else "") and res[i - 1].startswith("psql (")))]
    while res and not res[0].strip():
        res.pop(0)
    while res and not res[-1].strip():
        res.pop()
    return res


def cut(lines, start, stop=None):
    """the lines from the first one starting with start up to (not including) the first one starting with stop"""
    i = next(k for k, l in enumerate(lines) if l.startswith(start))
    j = next((k for k, l in enumerate(lines) if k > i and stop and l.startswith(stop)), len(lines))
    return lines[i:j]


def ctag(x, y, text, color, order=None, w=None):
    """a small label pill without a leader"""
    return pill(x, y, text, color, order, size=22)


def short_log(l):
    """a postgres log line without its time stamp and process number"""
    return re.sub(r"^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\.\d+ UTC \[\d+\] ", "… ", l)


def idshort(scene, k=0):
    return D[scene][k]["out"][0][:12] + "…"



# =====================================================================
def out_rows(scene, k=0, kind=None, rew=None):
    """terminal rows for a command's real output; errors in red"""
    lines = RA(scene, k)
    if rew:
        lines = rewrap(lines, rew)
    rows = []
    for l in lines:
        if kind:
            rows.append((kind, l))
        else:
            rows.append(("e" if ERR_RE.match(l.strip()) or l.startswith("Error") else "o", l))
    return rows


def cmd_rows(scene, k=0, path=P_KS, marks=None, kind=None, rew=None):
    c = C(scene, k)
    first, *rest = c.split("\n")
    rows = [("$", path, first, marks or {})]
    rows += [("o", r_) for r_ in rest]
    return rows + out_rows(scene, k, kind, rew)


def chip(x, y, text, color, bg, order=None, size=24, attrs="", anim="pop", mono=True):
    ff = f"font-family:{MONO};" if mono else ""
    return p(f"position:absolute;left:{x:.0f}px;top:{y:.0f}px;height:{size + 22}px;padding:0 16px;border-radius:10px;background:{bg};border:2px solid {color};{ff}font-size:{size}px;font-weight:700;line-height:{size + 18}px;color:{color};white-space:nowrap", e(text), bi(anim, order) + attrs)


def chip_w(text, size=24, mono=True):
    return tw(text, size, mono) + 32 + 4


# =====================================================================
# chapter 37
# =====================================================================
EB1, EB2, EB3, EB4, EB5, EB6 = "1. 빈칸과 기본값", "2. 겹침과 범위", "3. 기본 키와 자동 번호", "4. 표끼리 잇기", "5. 나중에 규칙 바꾸기", "6. 오류와 실제 상황"
C1, C2, C3, C4, C5, C6 = BL, TEAL, VO, MAG, GR, RED
GATE, GATEBG = "#1D2330", "#EEF0F3"
OKC = GR


def P(scene, k=0, a=None, b=None):
    """the psql lines of a scene: no banner, no blank lines, no final \\q; a and b cut by the start of a line"""
    ls = [l for l in S(scene, k) if l.strip() and not l.endswith("=# \\q")]
    if a is not None:
        i = next(n for n, l in enumerate(ls) if a in l)
        ls = ls[i:]
    if b is not None:
        j = next(n for n, l in enumerate(ls) if n > 0 and b in l)
        ls = ls[:j]
    return ls


def li(lines_or_t, sub, start=0):
    rows = lines_or_t.rows if isinstance(lines_or_t, Term) else lines_or_t
    for n in range(start, len(rows)):
        t_ = rows[n][1] if isinstance(lines_or_t, Term) else rows[n]
        if sub in t_:
            return n
    raise KeyError(sub)


def PT(lines, x, y, size=26, w=1728, lh=1.5, tid="t", marks=None, maxb=1000, **kw):
    """a psql terminal; the font shrinks until the terminal ends above maxb and every line fits its width"""
    rows = psql_rows(lines, marks)
    while True:
        n = len(WARN)
        t = Term(rows, x, y, size=size, w=w, lh=lh, tid=tid, **kw)
        wide = any(t.tx + t_ * 1.01 > x + t.w - Term.PX for t_ in t.tws)
        if (y + t.h <= maxb and not wide) or size <= 16:
            return t
        del WARN[n:]
        size -= 1


def under(t, i, sub, order, color=OR, start=0):
    """pen underline under sub on terminal line i"""
    x1 = t.sx(i, sub)
    return underline(order, round(x1), round(x1 + t.sw(sub)), round(t.top(i) + t.lp - 4), color)


def rring(t, i, sub, order, color=OR):
    x1 = t.sx(i, sub)
    return pen_box(order, round(x1 - 8), round(t.top(i) + 1), round(t.sw(sub) + 16), round(t.lp - 2), color, width=4)


def lspot_t(t, i, j, order):
    return spot(order, x=t.x + 10, y=round(t.top(i) - 4), w=t.w - 20, h=round((j - i + 1) * t.lp + 8), dim=0.55)


def side(x, y, w, head, body, color, order=None, hsize=30, bsize=25):
    o = [p(f"position:absolute;left:{x}px;top:{y}px;width:{w}px;font-size:{hsize}px;font-weight:700;line-height:1.4;color:{color}", head, bi("rise", order))]
    if body:
        o.append(p(f"position:absolute;left:{x}px;top:{y + hsize * 1.4 * (head.count('<br>') + 1) + 14:.0f}px;width:{w}px;font-size:{bsize}px;line-height:1.55;color:{SUB}", body, bi("rise", order)))
    return o


def table(x, y, cols, rows, widths, sid, size=26, rh=66, hcol=GRAY, order=None, stagger=False, mono_cols=(), colors=None, hsize=None, bold_first=True):
    """a plain ruled table; rows reveal together (order) or one by one (stagger)"""
    o = []
    hsize = hsize or size - 2
    cx = [x + sum(widths[:j]) for j in range(len(widths))]
    W_ = sum(widths)
    for j, c in enumerate(cols):
        o.append(p(f"position:absolute;left:{cx[j]}px;top:{y}px;width:{widths[j] - 20}px;font-size:{hsize}px;font-weight:700;color:{hcol};white-space:nowrap", c))
    y0 = y + hsize * 1.45 + 14
    for i, r in enumerate(rows):
        yy = y0 + i * rh
        o.append(f'<div style="position:absolute;left:{x}px;top:{yy:.0f}px;width:{W_}px;height:2px;background:{LINE}"></div>')
        ra = bi("rise", (order + i) if stagger else order) if order else ""
        for j, v in enumerate(r):
            mono = j in mono_cols
            col = (colors[i][j] if colors and colors[i] and colors[i][j] else (INK if (j == 0 and bold_first) or mono else SUB))
            fw = 700 if (j == 0 and bold_first) or mono else 400
            fs = size - (2 if mono else 0)
            o.append(p(f"position:absolute;left:{cx[j]}px;top:{yy + (rh - fs * 1.35) / 2:.0f}px;width:{widths[j] - 20}px;{'font-family:' + MONO + ';' if mono else ''}font-size:{fs}px;font-weight:{fw};line-height:1.35;color:{col};white-space:nowrap", v, ra + f' id="{sid}-r{i}c{j}"'))
            if tw(re.sub(r"<[^>]+>|&[a-z]+;", "x", v), fs, mono) > widths[j] - 20:
                WARN.append(f"{sid}: cell {i},{j} '{v[:20]}' wider than {widths[j] - 20}")
    o.append(f'<div style="position:absolute;left:{x}px;top:{y0 + len(rows) * rh:.0f}px;width:{W_}px;height:2px;background:{LINE}"></div>')
    return o, y0


def kw(text, color):
    return f'<span style="font-family:{MONO};font-weight:700;color:{color}">{e(text)}</span>'


# =====================================================================
# cover
# =====================================================================
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px">',
       p("position:absolute;left:128px;top:300px;font-size:28px;font-weight:700;color:#9DC1E6", "KANT AX/AI 엔지니어 트랙 · 37"),
       f'<h1{SLAM(1)} style="position:absolute;left:128px;top:350px;padding-bottom:14px;font-size:100px;font-weight:900;line-height:1.3;color:#F6F5F1">SQL 2</h1>',
       p("position:absolute;left:128px;top:500px;font-size:52px;font-weight:700;line-height:1.3;color:#F6F5F1", "제약 조건으로 표 설계하기"),
       p("position:absolute;left:128px;top:600px;width:720px;font-size:32px;line-height:1.5;color:#BFC6D4", "잘못된 데이터가 표에 못 들어오게<br>표에 규칙을 붙여요")]
L = P("ck", 0, "INSERT INTO product VALUES (1, 'earphone', 0")
t = PT(L, 860, 320, size=17, w=964, tid="cov-term", lh=1.55)
cov.append(t.html())
cov.append(shine(2, "cov-term"))
W("cover", cov, "37 챕터는 SQL 2, 제약 조건으로 표 설계하기예요. 36에서는 규칙 없는 표를 만들고 데이터를 넣고 고치고 지웠어요. 규칙이 없으면 가격 0원, 재고 -1개 같은 값도 그대로 들어가요. 오늘은 표에 규칙을 붙여서 잘못된 행이 들어오는 순간 PostgreSQL이 막게 해요. 오른쪽 화면처럼 규칙에 걸린 행은 ERROR와 함께 돌려보내고, 맞는 행만 INSERT 0 1로 들어가요." + REAL, ("intro", "들어가기"))

ORDER.append("toc")   # written last, after page numbers are known

# =====================================================================
# why
# =====================================================================
o = frame("why", "들어가기", "규칙 없는 표는 무엇이든 받아요", INK)
L = P("why")
t = PT(L, 96, 214, size=30, w=1728, lh=1.55, tid="t-why", maxb=900)
sel = li(t, "SELECT")
r1, r2, r3 = sel + 3, sel + 4, sel + 5
t.band(r2, r2, 1, "rgba(240,122,114,.22)")
t.band(r3, r3, 2, "rgba(240,122,114,.22)")
o.append(t.html())
o.append(rring(t, r2, " 1 ", 1, RED) if False else "")
o += tag(t, r2, "id 1이 두 번, 이메일도 겹쳐요, 나이 -3", RED, 1, gap=60)
o += tag(t, r3, "이름과 이메일이 비었어요", RED, 2, gap=60)
o.append(caption("세 INSERT가 모두 INSERT 0 1로 들어갔어요. 막아 줄 규칙이 없었기 때문이에요.", t.y + t.h + 40, 3, size=30))
W("why", o, "36에서 만든 것처럼 규칙 없는 회원 표를 만들고 행 세 개를 넣었어요. 첫 행은 정상이에요. 두 번째 행은 id가 1로 첫 행과 겹치고, 이메일도 kim@mail.com으로 같아요. 나이는 -3이에요. 세 번째 행은 이름과 이메일이 비어 있어요. 그런데 세 INSERT 모두 INSERT 0 1, 잘 들어갔다고 나와요. 표는 타입만 맞으면 받아요. 이런 행이 쌓이면 회원 1번을 찾을 때 두 명이 나오고, 이메일로 로그인할 때 누구인지 모르게 돼요. 오늘은 이런 행을 표가 처음부터 거절하게 만들어요." + REAL)

# =====================================================================
# big picture: the gatekeeper
# =====================================================================
o = frame("big", "들어가기", "제약 조건은 표 앞에 선 문지기예요", INK)
# rows coming in
o.append(p(f"position:absolute;left:96px;top:238px;font-size:26px;font-weight:700;color:{GRAY}", "들어오는 행"))
o.append(chip(96, 300, "(1, 'kim', 'kim@mail.com')", BL, "#FFFFFF", None, size=24, attrs=' id="in-ok"'))
o.append(chip(96, 420, "(1, 'lee', 'kim@mail.com')", RED, "#FFFFFF", None, size=24, attrs=' id="in-bad"'))
# the gate
o.append(f'<div id="gate" style="position:absolute;left:720px;top:236px;width:420px;height:560px;background:{GATEBG};border:3px solid {GATE};border-radius:24px"></div>')
o.append(p(f"position:absolute;left:752px;top:258px;font-size:30px;font-weight:700;color:{GATE}", "문지기 (제약 조건)"))
GK = [("NOT NULL", "비우면 안 돼요", C1), ("DEFAULT", "안 적으면 채워요", C1), ("UNIQUE", "겹치면 안 돼요", C2), ("CHECK", "조건에 맞아야 해요", C2), ("PRIMARY KEY", "행마다 다른 번호", C3), ("FOREIGN KEY", "다른 표에 있어야 해요", C4)]
for k, (a_, b_, c) in enumerate(GK):
    y = 322 + k * 76
    o.append(p(f"position:absolute;left:752px;top:{y}px;font-family:{MONO};font-size:24px;font-weight:700;color:{c};white-space:nowrap", e(a_), STAGGER(1) if False else bi("rise", 1) + DELAY(k * 70)))
    o.append(p(f"position:absolute;left:752px;top:{y + 32}px;font-size:20px;color:{SUB};white-space:nowrap", e(b_), bi("rise", 1) + DELAY(k * 70)))
# the table
o.append(cyl(1440, 300, 384, 300, "member 표", "규칙에 맞는 행만", INK, "#FFFFFF", "tbl"))
# routes
# the good row: into the gate, then out of it into the table
o.append(svg(f'<path id="r-ok1" d="M520,323 C620,323 640,380 712,380" fill="none" stroke="{OKC}" stroke-width="5" stroke-linecap="round" stroke-dasharray="2 12"/>', 2, "fade"))
o.append(f'<div{PATH(2, "r-ok1", 900)} style="position:absolute;left:698px;top:366px;width:28px;height:28px;border-radius:14px;background:{OKC};box-shadow:0 0 0 5px #FFFFFF"></div>')
o.append(svg(f'<path id="r-ok2" d="M1148,450 L1430,450" fill="none" stroke="{OKC}" stroke-width="5" stroke-linecap="round" stroke-dasharray="2 12"/>', 3, "fade"))
o.append(f'<div{PATH(3, "r-ok2", 900)} style="position:absolute;left:1416px;top:436px;width:28px;height:28px;border-radius:14px;background:{OKC};box-shadow:0 0 0 5px #FFFFFF"></div>')
o.append(p(f"position:absolute;left:1440px;top:640px;width:384px;text-align:center;font-family:{MONO};font-size:28px;font-weight:700;color:{OKC}", "INSERT 0 1", bi("pop", 3) + DELAY(800)))
# the bad row: into the gate, stopped there
o.append(svg(f'<path id="r-bad" d="M520,443 C620,443 640,560 712,560" fill="none" stroke="{RED}" stroke-width="5" stroke-linecap="round" stroke-dasharray="2 12"/>', 4, "fade"))
o.append(f'<div id="bad-dot"{PATH(4, "r-bad", 900)} style="position:absolute;left:698px;top:546px;width:28px;height:28px;border-radius:14px;background:{RED};box-shadow:0 0 0 5px #FFFFFF"></div>')
o.append(shake(5, "gate"))
t_err = 'ERROR:  duplicate key value violates unique constraint "member_pkey"'
o.append(f'<div{bi("rise", 5)} style="position:absolute;left:96px;top:850px;width:1728px;height:110px;background:{T_BG};border-radius:18px;padding:0 34px;display:flex;flex-direction:column;justify-content:center">'
         + p(f"font-family:{MONO};font-size:27px;font-weight:700;color:{TCOL['e']};white-space:pre", e(t_err))
         + p(f"font-family:{MONO};font-size:24px;color:{TCOL['e']};white-space:pre;margin-top:6px", e("DETAIL:  Key (id)=(1) already exists.")) + '</div>')
o.append(p(f"position:absolute;left:96px;top:600px;width:540px;font-size:24px;line-height:1.5;color:{SUB}", "걸린 행은 표에 한 칸도 안 들어가요. 어느 규칙에 걸렸는지는 ERROR 줄에 나와요.", bi("rise", 5)))
W("big", o, "제약 조건은 표 앞에 선 문지기예요. INSERT로 들어오는 행, UPDATE로 바뀌는 행은 모두 문지기를 지나요. 가운데 문지기가 오늘 배울 여섯 가지 규칙이에요. NOT NULL과 DEFAULT는 1파트, UNIQUE와 CHECK는 2파트, PRIMARY KEY는 3파트, FOREIGN KEY는 4파트에서 봐요. 규칙에 맞는 행은 표에 들어가고 INSERT 0 1이 나와요. 규칙에 걸린 행은 한 칸도 들어가지 않아요. 아래처럼 ERROR 줄에 걸린 규칙의 이름이, DETAIL 줄에 무엇이 문제인지가 나와요. 표를 만들 때 규칙을 같이 적어 두면, 누가 넣든 잘못된 행은 표에 못 들어와요.")

# =====================================================================
# smallest example
# =====================================================================
o = frame("min", "들어가기", "CHECK 한 줄로 음수 가격을 막아요", INK)
L = P("min")
t = PT(L, 96, 214, size=32, w=1728, lh=1.55, tid="t-min", maxb=900)
ck = li(t, "CHECK")
er = li(t, "ERROR")
ok = li(t, "INSERT 0 1")
o.append(t.html())
o.append(rring(t, ck, "CHECK (price > 0)", 1, C2))
o += tag(t, ck, "가격은 0보다 커야 해요", C2, 1, gap=48)
o.append(under(t, er, '"product_price_check"', 2, OR))
o += tag(t, er + 1, "막힌 행", RED, 2, gap=48)
o += tag(t, ok, "맞는 값은 들어가요", OKC, 3, gap=48)
o.append(caption("열 뒤에 규칙을 적으면, 그 열에 들어오는 값마다 PostgreSQL이 검사해요.", t.y + t.h + 40, 3, size=30))
W("min", o, "가장 짧은 예부터 봐요. product 표의 price 열 뒤에 CHECK (price > 0)을 붙였어요. 가격은 0보다 커야 한다는 규칙이에요. 이 줄을 빼면 36에서 만든 표와 똑같아요. 이제 -89000원을 넣으면 ERROR가 나요. ERROR 줄의 product_price_check가 걸린 규칙의 이름이에요. 이름은 PostgreSQL이 표 이름, 열 이름, check를 이어서 지었어요. DETAIL 줄에는 막힌 행이 그대로 나와요. 가격을 89000으로 고쳐 넣으면 INSERT 0 1로 들어가요. 오늘 배우는 규칙은 모두 이렇게 열 뒤나 표 끝에 한 줄씩 붙여요. CREATE TABLE에서 줄을 나눠 치면 psql 앞 표시가 kant_shop(#로 바뀌어요. 괄호가 아직 안 닫혔다는 뜻이에요." + REAL)

# =====================================================================
# part 1: NOT NULL, DEFAULT
# =====================================================================
o = frame("n-nn", EB1, "NOT NULL을 붙인 열은 비워 둘 수 없어요", C1)
L = P("nn")
t = PT(L, 96, 210, size=30, w=1728, lh=1.5, tid="t-nn", maxb=900)
nn = li(t, "NOT NULL")
er = li(t, "ERROR")
sel = li(t, "SELECT")
o.append(t.html())
o.append(rring(t, nn, "NOT NULL", 1, C1))
o += tag(t, nn, "이름은 꼭 있어야 해요", C1, 1, gap=48)
o.append(under(t, er, 'column "name"', 2, OR))
o.append(under(t, er + 1, "null", 2, OR))
o += tag(t, sel + 3, "email은 비어도 돼요 (NULL)", GRAY, 3, at=t.sx(sel + 3, "kim") + t.sw("kim") + 150, gap=48)
o.append(caption("NULL은 값이 없다는 뜻이에요. psql은 NULL 칸을 빈칸으로 보여 줘요.", t.y + t.h + 40, 3, size=30))
W("n-nn", o, "NOT NULL은 그 열을 비워 둘 수 없다는 규칙이에요. name 열 뒤에 NOT NULL을 붙였어요. 이름을 빼고 id와 email만 넣으면 ERROR가 나요. 오류 문장은 name 열의 null 값이 not-null 규칙을 어겼다는 뜻이에요. DETAIL에는 막힌 행이 (1, null, kim@mail.com)으로 나와요. null은 값이 없다는 뜻이에요. 이번에는 email을 빼고 넣었어요. email에는 NOT NULL이 없어서 들어가요. SELECT로 보면 email 칸이 비어 있어요. psql은 NULL을 빈칸으로 보여 줘요. 꼭 있어야 하는 값, 이름이나 가격 같은 열에 NOT NULL을 붙여요." + REAL, ("p1", "빈칸과 기본값"))

L = P("df", 0, None, "\\d member")
o = frame("n-df", EB1, "DEFAULT는 값을 안 적은 칸을 채워 줘요", C1)
t = PT(L, 96, 214, size=30, w=1728, lh=1.5, tid="t-df", maxb=900)
d0 = li(t, "DEFAULT 0")
d1 = li(t, "DEFAULT now()")
sel = li(t, "SELECT")
o.append(t.html())
o += tag(t, d0, "안 적으면 0", C1, 1, gap=48)
o += tag(t, d1, "안 적으면 지금 시각", C1, 1, gap=48)
o.append(lspot_t(t, li(t, "VALUES (1, 'kim')"), li(t, "VALUES (1, 'kim')"), 2))
o.append(lspot_t(t, sel + 3, sel + 3, 3))
o.append(spot_off(4))
_x = t.sx(sel + 1, "points")
o.append(pen_box(4, round(_x - 10), round(t.top(sel + 3) - 2), round(t.sw("points") + 20), round(2 * t.lp + 4), C1, width=4))
o.append(caption("TIMESTAMPTZ 끝의 +00은 세계 표준시(UTC)예요. 컨테이너의 시간대가 UTC라서 그래요. 한국 시간은 9시간 더해요.", t.y + t.h + 36, 5, size=26, color=SUB))
W("n-df", o, "DEFAULT는 INSERT에서 그 열을 안 적었을 때 넣을 값이에요. points는 안 적으면 0, joined_at은 안 적으면 now(), 지금 시각이에요. kim은 id와 name만 적었어요. SELECT로 보면 points에 0, joined_at에 넣은 순간의 시각이 들어 있어요. lee는 points를 500으로 직접 적었어요. 적은 값이 있으면 DEFAULT는 쓰이지 않아요. 가입 시각, 포인트, 재고처럼 처음 값이 정해져 있는 열에 DEFAULT를 붙여요. joined_at 끝의 +00은 36에서 본 TIMESTAMPTZ의 시간대예요. 컨테이너가 세계 표준시로 돌고 있어서 +00으로 나와요." + REAL)

L = P("df", 0, "\\d member")
o = frame("n-d", EB1, "\\d 표 이름으로 붙은 규칙을 확인해요", C1)
t = PT(L, 96, 230, size=36, w=1728, lh=1.6, tid="t-dd", maxb=760)
hd = li(t, "Nullable")
o.append(t.html())
xs_n = t.sx(hd, "Nullable")
xs_d = t.sx(hd, "Default")
top_ = t.top(hd) - 6
hgt = (len(L) - hd) * t.lp + 12
o.append(spot(1, x=round(xs_n - 14), y=round(top_), w=round(t.sw("Nullable") + 28), h=round(hgt), dim=0.55))
o.append(spot(2, x=round(xs_d - 14), y=round(top_), w=round(t.sw("now()") + 40), h=round(hgt), dim=0.55))
o.append(spot_off(3))
o += side(96, t.y + t.h + 40, 860, f"{kw('Nullable', C1)} 칸에 not null", "NOT NULL을 붙인 열이에요.", INK, 3, hsize=28, bsize=24)
o += side(1000, t.y + t.h + 40, 824, f"{kw('Default', C1)} 칸에 기본값", "안 적었을 때 들어갈 값이에요.", INK, 3, hsize=28, bsize=24)
W("n-d", o, "표에 어떤 규칙이 붙었는지는 백슬래시 d 뒤에 표 이름을 쳐서 봐요. 34에서 표 구조를 볼 때 쓴 명령이에요. Nullable 칸에 not null이 적힌 열이 NOT NULL을 붙인 열이에요. name 하나예요. Default 칸에는 기본값이 나와요. points는 0, joined_at은 now()예요. 표를 만든 뒤 규칙을 제대로 적었는지, 남이 만든 표에 어떤 규칙이 있는지 볼 때 이 명령부터 쳐요. 백슬래시 명령이라 끝에 세미콜론을 안 붙여요." + REAL)

# =====================================================================
# part 2: UNIQUE, CHECK, names
# =====================================================================
o = frame("u-uq", EB2, "UNIQUE를 붙인 열에는 같은 값이 두 번 못 들어가요", C2)
L = P("uq")
t = PT(L, 96, 214, size=30, w=1728, lh=1.55, tid="t-uq", maxb=900)
uq = li(t, "UNIQUE")
er = li(t, "ERROR")
o.append(t.html())
o.append(rring(t, uq, "UNIQUE", 1, C2))
o += tag(t, uq, "이메일은 한 사람에 하나", C2, 1, gap=48)
o.append(t.html() and "")
o.append(under(t, er, '"member_email_key"', 2, OR))
o.append(under(t, er + 1, "Key (email)=(kim@mail.com) already exists", 3, RED))
o += tag(t, li(t, "INSERT 0 1", er), "다른 이메일은 들어가요", OKC, 4, gap=48)
o.append(caption("이름은 겹쳐도 되고, 이메일과 아이디처럼 사람을 가려내는 값에 UNIQUE를 붙여요.", t.y + t.h + 40, 4, size=30))
W("u-uq", o, "UNIQUE는 그 열에 같은 값이 두 번 들어가지 못하게 하는 규칙이에요. email 뒤에 UNIQUE를 붙였어요. kim이 kim@mail.com으로 가입한 뒤, lee가 같은 이메일로 들어오면 ERROR가 나요. 오류 문장은 duplicate key, 겹치는 값이 member_email_key 규칙을 어겼다는 뜻이에요. 이름은 표 이름, 열 이름, key를 이어서 지었어요. DETAIL에 어떤 값이 이미 있는지 나와요. 이메일을 lee@mail.com으로 바꾸면 들어가요. 이름은 동명이인이 있으니 UNIQUE를 붙이지 않아요. 이메일, 아이디, 전화번호처럼 한 사람을 가려내는 값에 붙여요." + REAL, ("p2", "겹침과 범위"))

o = frame("c-ck", EB2, "CHECK는 괄호 안 조건이 맞는 값만 받아요", C2)
L = P("ck")
t = PT(L, 96, 214, size=30, w=1728, lh=1.55, tid="t-ck", maxb=900)
c1, c2 = li(t, "CHECK (price"), li(t, "CHECK (stock")
e1 = li(t, "ERROR")
e2 = li(t, "ERROR", e1 + 1)
o.append(t.html())
o += tag(t, c1, "0원은 안 돼요", C2, 1, gap=48)
o += tag(t, c2, "재고는 0개까지 돼요", C2, 1, gap=48)
o.append(under(t, e1, '"product_price_check"', 2, OR))
o.append(under(t, e2, '"product_stock_check"', 3, OR))
o += tag(t, li(t, "INSERT 0 1"), "둘 다 맞으면 들어가요", OKC, 4, gap=48)
o.append(caption(f"조건에는 WHERE에서 쓴 {kw('>', C2)} {kw('>=', C2)} {kw('<>', C2)} {kw('AND', C2)}를 그대로 써요.", t.y + t.h + 40, 4, size=30))
W("c-ck", o, "CHECK는 괄호 안 조건이 참인 값만 받는 규칙이에요. price는 0보다 커야 하고, stock은 0 이상이어야 해요. 가격 0원을 넣으면 product_price_check에 걸려요. 재고 -1개를 넣으면 product_stock_check에 걸려요. 하나의 표에 CHECK를 여러 개 붙일 수 있고, ERROR에 어느 것에 걸렸는지 이름이 나와요. 둘 다 맞으면 들어가요. 조건에는 WHERE에서 쓴 비교와 AND를 그대로 써요. 예를 들어 가격을 1만 원에서 10만 원 사이로 묶으려면 CHECK (price >= 10000 AND price <= 100000)처럼 적어요." + REAL)

o = frame("k-nm", EB2, "CONSTRAINT 이름을 붙이면 오류에 내 이름이 나와요", C2)
L = P("nm", 0, None, "\\d product")
t = PT(L, 96, 214, size=30, w=1728, lh=1.5, tid="t-nm", maxb=900)
n1, n2 = li(t, "price_positive"), li(t, "sale_lower")
e1 = li(t, "ERROR")
e2 = li(t, "ERROR", e1 + 1)
o.append(t.html())
o.append(rring(t, n1, "price_positive", 1, C2))
o.append(rring(t, n2, "sale_lower", 1, C2))
o += tag(t, n1, "내가 지은 이름", C2, 1, gap=48)
o += tag(t, n2, "열 두 개를 비교해요", C2, 1, gap=48)
o.append(under(t, e1, '"price_positive"', 2, OR))
o.append(under(t, e2, '"sale_lower"', 3, OR))
o.append(caption("이름만 봐도 무엇이 틀렸는지 보이게 지어요. 나중에 규칙을 지울 때도 이 이름을 써요.", t.y + t.h + 36, 4, size=28))
W("k-nm", o, "규칙에 이름을 직접 붙일 수도 있어요. CONSTRAINT 다음에 이름, 그 뒤에 규칙을 적어요. 열 뒤가 아니라 열 목록 끝에 한 줄로 따로 적었어요. 두 번째 규칙 sale_lower는 할인가가 정가보다 낮아야 한다는 규칙이에요. 열 두 개를 같이 비교하는 CHECK는 이렇게 표 끝에 적어요. 가격을 -15000으로 넣으면 price_positive에, 할인가가 정가보다 비싸면 sale_lower에 걸려요. 자동 이름 product_price_check보다 뜻이 바로 읽혀요. 5파트에서 규칙을 지울 때도 이 이름을 써요." + REAL)

o = frame("k-rule", EB2, "이름을 안 붙이면 PostgreSQL이 규칙대로 지어요", C2)
rows_ = [(kw("member_email_key", C2), "UNIQUE", "표_열_key"),
         (kw("product_price_check", C2), "CHECK", "표_열_check"),
         (kw("member_pkey", C3), "PRIMARY KEY", "표_pkey"),
         (kw("orders_member_id_fkey", C4), "FOREIGN KEY", "표_열_fkey"),
         (kw("order_item_pkey", C3), "PRIMARY KEY (열 두 개)", "표_pkey")]
tb, y0 = table(96, 232, ["오류에 나온 이름", "규칙", "짓는 법"], rows_, [760, 520, 448], "rule", size=32, rh=96, order=1, stagger=True)
o += tb
o.append(f'<div{bi("rise", 6)} style="position:absolute;left:96px;top:{y0 + 5 * 96 + 44:.0f}px;width:1728px;height:130px;background:{T_BG};border-radius:18px;padding:0 34px;display:flex;flex-direction:column;justify-content:center">'
         + p(f"font-family:{MONO};font-size:24px;color:{TCOL['e']};white-space:pre", e('ERROR:  null value in column "name" of relation "member" violates not-null constraint'))
         + p(f"font-size:22px;color:#BFC6D4;margin-top:8px", "NOT NULL은 이름이 없어요. 대신 열 이름이 나와요.") + '</div>')
W("k-rule", o, "이름을 안 붙이면 PostgreSQL이 정해진 규칙으로 지어요. UNIQUE는 표 이름, 열 이름, key를 밑줄로 이어요. CHECK는 끝이 check, 기본 키는 표 이름 뒤에 pkey, 4파트에서 볼 외래 키는 fkey예요. 열 두 개로 만든 기본 키도 표 이름 뒤에 pkey예요. 그래서 ERROR 줄에서 이름의 끝만 봐도 어느 종류의 규칙에 걸렸는지 알 수 있어요. NOT NULL은 이름이 없고, 대신 어느 열이 비었는지 열 이름이 나와요. 이 표는 오늘 덱의 실제 오류에서 모았어요.")

# =====================================================================
# part 3: PRIMARY KEY, SERIAL, IDENTITY, composite
# =====================================================================
o = frame("p-pk", EB3, "PRIMARY KEY는 NOT NULL과 UNIQUE를 합친 규칙이에요", C3)
L = P("pk")
t = PT(L, 96, 206, size=30, w=1728, lh=1.42, tid="t-pk", maxb=1000)
pk = li(t, "PRIMARY KEY")
e1 = li(t, "ERROR")
e2 = li(t, "ERROR", e1 + 1)
ix = li(t, "member_pkey", e2)
o.append(t.html())
o.append(rring(t, pk, "PRIMARY KEY", 1, C3))
o += tag(t, e1, "겹치면 안 돼요 (UNIQUE)", C2, 2, gap=40)
o += tag(t, e2, "비우면 안 돼요 (NOT NULL)", C1, 3, gap=40)
o.append(lspot_t(t, ix, ix, 4))
o.append(spot_off(5))
o += tag(t, ix, "표에 하나만 둘 수 있어요", C3, 5, gap=48)
W("p-pk", o, "32에서 기본 키는 겹치지 않고 비울 수 없는 번호라고 했어요. 진동벨 번호처럼 행 하나를 가리키는 번호예요. id 뒤에 PRIMARY KEY를 붙이고 실제로 확인해 봐요. id 1을 두 번 넣으면 member_pkey에 걸려요. 오류 문장이 UNIQUE와 똑같은 duplicate key예요. id를 NULL로 넣으면 not-null 오류가 나요. NOT NULL과 같아요. 그래서 기본 키는 NOT NULL과 UNIQUE를 합친 규칙이에요. 백슬래시 d로 보면 id의 Nullable에 not null이 저절로 붙었고, 아래 Indexes에 member_pkey가 있어요. 기본 키는 표에 하나만 둘 수 있어요." + REAL, ("p3", "기본 키와 자동 번호"))

o = frame("p-sr", EB3, "SERIAL은 번호를 1, 2, 3 차례로 채워 줘요", C3)
L = P("sr")
t = PT(L, 96, 206, size=26, w=1320, lh=1.42, tid="t-sr", maxb=1000)
sr = li(t, "SERIAL")
ins = li(t, "INSERT INTO")
nv = li(t, "nextval")
sel = li(t, "SELECT")
o.append(t.html())
o.append(rring(t, sr, "SERIAL", 1, C3))
o.append(under(t, ins, "(name)", 2, OR))
o.append(rring(t, sel + 3, "1", 3, C3))
o.append(rring(t, sel + 4, "2", 3, C3))
o.append(under(t, nv, "nextval('member_id_seq'::regclass)", 4, C3))
# number machine
mx = 1460
o.append(f'<div style="position:absolute;left:{mx}px;top:240px;width:364px;height:380px;background:{VOBG};border:3px solid {C3};border-radius:24px"></div>')
o.append(p(f"position:absolute;left:{mx + 32}px;top:262px;font-size:28px;font-weight:700;color:{C3}", "번호표 기계"))
o.append(p(f"position:absolute;left:{mx + 32}px;top:306px;font-family:{MONO};font-size:22px;font-weight:700;color:{SUB}", "member_id_seq"))
o.append(p(f"position:absolute;left:{mx + 32}px;top:362px;font-size:24px;color:{SUB}", "다음에 줄 번호"))
o.append(p(f"position:absolute;left:{mx + 32}px;top:420px;font-family:{MONO};font-size:120px;font-weight:700;line-height:1.3;color:{C3}", "3", ' id="seq-n" data-start="1"'))
o.append(set_text(2, "seq-n", "3"))
o.append(p(f"position:absolute;left:{mx}px;top:650px;width:364px;font-size:24px;line-height:1.55;color:{SUB}", "INSERT에서 id를 빼면 기계가 다음 번호를 꺼내 넣어요. 꺼낸 번호는 다시 쓰지 않아요.", bi("rise", 4)))
W("p-sr", o, "회원이 늘 때마다 다음 번호를 직접 세어 넣기는 번거로워요. id를 SERIAL PRIMARY KEY로 만들면 번호를 PostgreSQL이 채워 줘요. INSERT에서 id를 빼고 name만 적었어요. SELECT로 보면 kim은 1, lee는 2가 들어갔어요. SERIAL은 오른쪽 번호표 기계, member_id_seq를 하나 만들어요. 백슬래시 d로 보면 id의 Default가 nextval, 이 기계에서 다음 번호를 꺼내라는 뜻이에요. 1파트의 DEFAULT와 같은 원리예요. 번호를 두 개 꺼냈으니 기계는 다음에 3을 줄 차례예요." + REAL)

o = frame("p-trap", EB3, "SERIAL 열에 번호를 직접 넣으면 나중에 겹쳐요", C3)
L = P("sr-trap")
t = PT(L, 96, 214, size=30, w=1240, lh=1.55, tid="t-st", maxb=900)
i3 = li(t, "VALUES (3, 'park')")
c1 = li(t, "VALUES ('choi')")
c2 = li(t, "VALUES ('choi')", c1 + 1)
er = li(t, "ERROR")
o.append(t.html())
o += tag(t, i3, "3을 직접 넣었어요", OR, 1, gap=40)
o.append(under(t, er + 1, "Key (id)=(3) already exists", 2, RED))
o += tag(t, c2, "다음 번호 4로 들어가요", OKC, 3, gap=40)
mx = 1400
o.append(f'<div style="position:absolute;left:{mx}px;top:240px;width:424px;height:380px;background:{VOBG};border:3px solid {C3};border-radius:24px"></div>')
o.append(p(f"position:absolute;left:{mx + 32}px;top:262px;font-size:28px;font-weight:700;color:{C3}", "번호표 기계"))
o.append(p(f"position:absolute;left:{mx + 32}px;top:362px;font-size:24px;color:{SUB}", "다음에 줄 번호"))
o.append(p(f"position:absolute;left:{mx + 32}px;top:420px;font-family:{MONO};font-size:120px;font-weight:700;line-height:1.3;color:{C3}", "5", ' id="seq-t" data-start="3"'))
o.append(set_text(2, "seq-t", "4"))
o.append(set_text(3, "seq-t", "5"))
o.append(p(f"position:absolute;left:{mx}px;top:650px;width:424px;font-size:24px;line-height:1.55;color:{SUB}", "기계는 3이 이미 쓰인 줄 몰라요. 직접 넣은 번호는 기계를 지나지 않기 때문이에요.", bi("rise", 2)))
o.append(caption("SERIAL 열에는 번호를 직접 넣지 말고 비워 둬요.", t.y + t.h + 40, 4, size=30))
W("p-trap", o, "SERIAL에는 함정이 하나 있어요. 번호를 직접 넣어도 막지 않아요. park을 id 3으로 직접 넣었어요. 그런데 번호표 기계는 이걸 몰라요. 기계를 거치지 않았으니까요. 다음에 choi를 id 없이 넣으면 기계가 3을 꺼내고, 이미 있는 3과 겹쳐서 member_pkey 오류가 나요. 같은 INSERT를 한 번 더 치면 기계가 4를 꺼내서 들어가요. 실패한 번호 3은 다시 쓰지 않아요. 그래서 SERIAL 열에는 번호를 직접 넣지 않아요. 다음 장의 IDENTITY는 이 실수를 처음부터 막아요." + REAL)

o = frame("p-id", EB3, "GENERATED ALWAYS AS IDENTITY는 직접 넣은 번호를 막아요", C3)
L = P("id", 0, None, "\\d product")
L2 = P("id", 0, "\\d product")
t = PT(L, 96, 206, size=28, w=1728, lh=1.42, tid="t-id", maxb=860)
gi = li(t, "GENERATED")
er = li(t, "ERROR")
o.append(t.html())
o.append(rring(t, gi, "GENERATED ALWAYS AS IDENTITY", 1, C3))
o += tag(t, gi, "번호는 늘 PostgreSQL이", C3, 1, gap=40)
o.append(under(t, er, "cannot insert a non-DEFAULT value", 2, RED))
o.append(under(t, er + 2, "OVERRIDING SYSTEM VALUE", 3, GRAY))
o += tag(t, er + 2, "꼭 넣어야 할 때 쓰는 방법, 수업에서는 안 써요", GRAY, 3, gap=40)
idl = next(l for l in L2 if l.startswith(" id "))
o.append(p(f"position:absolute;left:96px;top:{t.y + t.h + 32}px;font-size:24px;font-weight:700;color:{GRAY}", "\\d product의 id 줄", bi("rise", 4)))
o.append(f'<div{bi("rise", 4)} style="position:absolute;left:96px;top:{t.y + t.h + 76}px;width:1728px;height:64px;background:{T_BG};border-radius:14px;padding:0 34px;display:flex;align-items:center">' + p(f"font-family:{MONO};font-size:23px;color:{TCOL['o']};white-space:pre", e(idl)) + '</div>')
W("p-id", o, "SERIAL 대신 GENERATED ALWAYS AS IDENTITY를 쓰면 번호를 직접 넣는 실수를 막아요. 길지만 끊어 읽으면 쉬워요. 늘, ALWAYS, PostgreSQL이 번호를 만든다는 뜻이에요. 표준 SQL 문법이라 다른 데이터베이스에서도 비슷하게 써요. 이름만 빼고 넣으면 1, 2가 차례로 들어가요. 3을 직접 넣으려고 하면 ERROR가 나요. non-DEFAULT, 기본값이 아닌 값은 넣을 수 없다는 뜻이에요. HINT의 OVERRIDING SYSTEM VALUE는 다른 데이터베이스에서 옮겨 올 때처럼 꼭 넣어야 할 때 쓰는 방법이에요. 수업에서는 쓰지 않아요. 아래 백슬래시 d의 id 줄에는 generated always as identity가 보여요." + REAL)

o = frame("p-cmp", EB3, "새 표의 번호 열은 GENERATED ALWAYS AS IDENTITY로 만들어요", C3)
rows_ = [("id 없이 INSERT", "1, 2, 3 차례로", "1, 2, 3 차례로", "1, 2, 3 차례로"),
         ("번호를 직접 넣기", "들어가요", "들어가요", "ERROR로 막아요"),
         ("직접 넣은 뒤 자동 번호", "겹치면 ERROR", "겹치면 ERROR", "직접 못 넣어 안 겹쳐요"),
         ("표준 SQL", "PostgreSQL 문법", "표준", "표준")]
cols = ["", kw("SERIAL", C3), kw("BY DEFAULT AS IDENTITY", C3), kw("ALWAYS AS IDENTITY", C3)]
tb, y0 = table(96, 236, cols, rows_, [420, 360, 524, 424], "cmp", size=28, rh=92, order=1, stagger=True,
               colors=[None, [None, None, None, OKC], [None, RED, RED, OKC], [None, None, None, None]])
o += tb
o.append(f'<div{bi("fade", 5)} style="position:absolute;left:{96 + 420 + 360 + 524 - 14}px;top:214px;width:{424 + 14}px;height:{y0 - 214 + 4 * 92 + 12:.0f}px;border:4px solid {C3};border-radius:16px"></div>')
L = P("id-bd", 0, "INSERT INTO product VALUES (2")
t = PT(L[:4], 96, round(y0 + 4 * 92 + 50), size=22, w=1728, lh=1.5, tid="t-bd")
o.append(f'<div{bi("rise", 5)}>' + t.html() + '</div>')
o += tag(t, 2, "BY DEFAULT도 SERIAL처럼 겹쳐요", RED, 5, gap=40)
W("p-cmp", o, "번호를 자동으로 채우는 방법 세 가지를 나란히 놓았어요. 셋 다 id를 빼고 넣으면 1, 2, 3이 차례로 들어가요. 다른 점은 번호를 직접 넣을 때예요. SERIAL과 GENERATED BY DEFAULT AS IDENTITY는 직접 넣은 번호를 받아요. 그래서 앞 장처럼 나중에 자동 번호와 겹쳐요. 아래 화면이 BY DEFAULT로 만든 표에 2를 직접 넣은 뒤 자동 번호를 받은 결과예요. 키 2가 겹친다는 오류가 나요. ALWAYS는 직접 넣는 것부터 막아서 겹칠 일이 없어요. 새로 만드는 표는 ALWAYS로 만들고, SERIAL은 남이 만든 표나 예전 자료에서 읽을 수 있으면 돼요." + REAL)

o = frame("p-cp", EB3, "열 두 개를 묶어 기본 키 하나로 만들 수 있어요", C3)
L = P("cp", 0, None, "\\d order_item")
t = PT(L, 96, 206, size=28, w=1140, lh=1.45, tid="t-cp", maxb=900)
pk = li(t, "PRIMARY KEY (order_id")
er = li(t, "ERROR")
sel = li(t, "SELECT")
o.append(t.html())
o.append(rring(t, pk, "PRIMARY KEY (order_id, product_id)", 1, C3))
o.append(under(t, er + 1, "Key (order_id, product_id)=(1, 1)", 3, RED))
# pair picture
gx_ = 1290
o.append(p(f"position:absolute;left:{gx_}px;top:236px;font-size:26px;font-weight:700;color:{GRAY}", "주문 번호와 상품 번호를 한 쌍으로 봐요"))
pairs = [("1", "1", "1번 주문의 1번 상품", INK), ("1", "2", "1번 주문의 2번 상품", INK), ("2", "1", "2번 주문의 1번 상품", INK), ("1", "1", "이미 있는 쌍이에요", RED)]
for k, (a_, b_, d_, c) in enumerate(pairs):
    y = 300 + k * 104
    od = 2 if k < 3 else 3
    bd = c if c == RED else C3
    o.append(f'<div{bi("rise", od)}{DELAY(k * 90 if k < 3 else 0)} style="position:absolute;left:{gx_}px;top:{y}px;width:200px;height:76px;border:3px solid {bd};border-radius:14px;background:{"#FBEAEA" if c == RED else VOBG};display:flex;align-items:center;justify-content:center;font-family:{MONO};font-size:34px;font-weight:700;color:{bd}" id="pair{k}">({a_}, {b_})</div>')
    o.append(p(f"position:absolute;left:{gx_ + 228}px;top:{y + 20}px;font-size:25px;color:{c if c == RED else SUB};white-space:nowrap", e(d_), bi("rise", od) + DELAY(k * 90 if k < 3 else 0)))
o.append(shake(3, "pair3"))
o.append(caption("order_id 1도, product_id 1도 여러 번 나와요. 겹치면 안 되는 건 두 값의 쌍이에요.", t.y + t.h + 40, 4, size=28))
W("p-cp", o, "주문 하나에는 상품이 여러 개 담겨요. order_item 표는 몇 번 주문에 몇 번 상품을 몇 개 담았는지 적는 표예요. 여기서는 order_id만으로도, product_id만으로도 행을 가려낼 수 없어요. 1번 주문에 상품이 둘이고, 1번 상품은 주문 둘에 들어 있으니까요. 그래서 PRIMARY KEY를 열 뒤가 아니라 표 끝에 적고 괄호 안에 열 두 개를 넣었어요. 복합 기본 키라고 불러요. 이제 겹치면 안 되는 건 두 값의 쌍이에요. 1번 주문에 1번 상품을 또 넣으면 쌍 (1, 1)이 겹쳐서 order_item_pkey 오류가 나요. 같은 상품을 더 사면 행을 새로 넣지 말고 qty를 늘려요. 6파트 장바구니에서 해 봐요." + REAL)

o = frame("p-cu", EB3, "번호 열을 따로 두면 UNIQUE (열, 열)로 쌍을 막아요", C3)
L = P("cu")
t = PT(L, 96, 206, size=24, w=1728, lh=1.36, tid="t-cu", maxb=830)
uq = li(t, "UNIQUE (member_id")
er = li(t, "ERROR")
nl = li(t, "VALUES (NULL")
sel = li(t, "SELECT")
o.append(t.html())
o.append(rring(t, uq, "UNIQUE (member_id, product_id)", 1, C2))
o += tag(t, uq, "쌍이 겹치면 안 돼요", C2, 1, gap=40)
o.append(under(t, er, '"cart_item_member_id_product_id_key"', 2, OR))
o += tag(t, nl, "NULL이 든 쌍은 막지 않아요", OR, 3, gap=40)
o.append(lspot_t(t, sel + 5, sel + 6, 3))
o.append(spot_off(4))
L2 = P("cp-null")
t2 = PT(L2, 96, t.y + t.h + 24, size=24, w=1728, lh=1.36, tid="t-cpn", bar=False, maxb=985)
o.append(f'<div{bi("rise", 4)}>' + t2.html() + '</div>')
o += tag(t2, 1, "복합 기본 키는 NULL을 막아요", C3, 4, gap=40)
W("p-cu", o, "같은 쌍 막기를 다르게 할 수도 있어요. 번호 열 id를 기본 키로 따로 두고, 쌍에는 UNIQUE (member_id, product_id)를 붙여요. 같은 회원이 같은 상품을 또 담으면 cart_item_member_id_product_id_key에 걸려요. 표 이름 뒤에 열 이름 두 개와 key를 이었어요. 다른 점은 NULL이에요. UNIQUE는 NULL이 든 쌍을 서로 다르다고 봐서 두 번 들어가요. 아래처럼 복합 기본 키는 NULL부터 막아요. 행을 따로 가리킬 번호가 필요하면 id와 복합 UNIQUE를, 쌍 자체가 행의 이름이면 복합 기본 키를 써요. 이때 UNIQUE 쪽 열에는 NOT NULL을 같이 붙여요." + REAL)

# =====================================================================
# part 4: FOREIGN KEY
# =====================================================================
o = frame("f-pic", EB4, "FOREIGN KEY는 다른 표에 있는 번호만 받아요", C4)
s1, g1 = sheet(96, 330, ["id", "name"], [("1", "kim"), ("2", "lee")], "fm", [170, 240], size=32, rh=80, pk=True)
o.append(s1)
s2, g2 = sheet(980, 330, ["id", "member_id", "total"], [("1", "1", "104000"), ("2", "99", "15000")], "fo", [150, 300, 280], size=32, rh=80, pk=True)
o.append(s2)
o.append(p(f"position:absolute;left:{g1['x']}px;top:{g1['y'] + g1['h'] + 18}px;font-family:{MONO};font-size:28px;font-weight:700;color:{C3};white-space:nowrap", "member"))
o.append(p(f"position:absolute;left:{g2['x']}px;top:{g2['y'] + g2['h'] + 18}px;font-family:{MONO};font-size:28px;font-weight:700;color:{C4};white-space:nowrap", "orders"))
# tint the member_id column, then arc above both tables from its header to member.id
o.append(f'<div{bi("fade", 1)} style="position:absolute;left:{g2["cx"][1] + 4}px;top:{g2["y"] + 4}px;width:{g2["widths"][1] - 8}px;height:{g2["h"] - 6}px;background:rgba(160,48,120,.10);border-radius:8px"></div>')
xo = g2["cx"][1] + g2["widths"][1] / 2
xm = g1["x"] + g1["widths"][0] / 2
yt = g1["y"] - 10
o.append(svg(f'<path id="fk-a" d="M{xo:.0f},{yt} C{xo:.0f},{yt - 120} {xm:.0f},{yt - 120} {xm:.0f},{yt - 6}" fill="none" stroke="{C4}" stroke-width="5" stroke-linecap="round"/>' + head_at(xm, yt - 4, 90, C4), 1))
o.append(p(f"position:absolute;left:{g1['x'] + g1['w']}px;top:{g1['y'] + 60}px;width:{g2['x'] - g1['x'] - g1['w']}px;text-align:center;font-family:{MONO};font-size:26px;font-weight:700;color:{C4};white-space:nowrap", "REFERENCES member (id)", bi("rise", 1)))
o.append(f'<div{bi("fade", 2)} style="position:absolute;left:{g2["cx"][0]}px;top:{row_y(g2, 1):.0f}px;width:{g2["w"]}px;height:{g2["rh"]}px;background:rgba(163,49,49,.12);border:3px solid {RED};border-radius:8px"></div>')
o.append(p(f"position:absolute;left:{g2['x']}px;top:{g2['y'] + g2['h'] + 18}px;width:{g2['w']}px;text-align:right;font-size:28px;font-weight:700;color:{RED};white-space:nowrap", "99번 회원은 없어요", bi("pop", 2)))
o += side(96, 720, 820, "부모 표 member", "번호를 빌려주는 쪽이에요. 가리키는 열(id)은 기본 키나 UNIQUE여야 해요.", C3, 3, hsize=30, bsize=25)
o += side(980, 720, 844, "자식 표 orders", f"{kw('member_id', C4)}에 member에 있는 id만 들어가요. 이 열을 외래 키라고 불러요.", C4, 3, hsize=30, bsize=25)
W("f-pic", o, "이제 표 두 개를 이어요. 회원 member와 주문 orders예요. 주문에는 누가 주문했는지 회원 번호 member_id를 적어요. 그런데 규칙이 없으면 99번처럼 없는 회원 번호도 들어가요. 누구의 주문인지 찾을 수 없는 주문이 생겨요. member_id 뒤에 REFERENCES member (id)를 붙이면 member 표의 id에 있는 번호만 받아요. 이 규칙을 FOREIGN KEY, 외래 키라고 해요. 번호를 빌려주는 member가 부모 표, 빌려 쓰는 orders가 자식 표예요. 부모 쪽 열은 기본 키나 UNIQUE여야 해요. 그래야 번호 하나가 회원 한 명을 가리켜요.", ("p4", "표끼리 잇기"))

o = frame("f-fk", EB4, "없는 회원 번호로 주문하면 FOREIGN KEY에 걸려요", C4)
L = P("fk")
t = PT(L, 96, 214, size=30, w=1728, lh=1.5, tid="t-fk", maxb=900)
rf = li(t, "REFERENCES")
er = li(t, "ERROR")
o.append(t.html())
o.append(rring(t, rf, "REFERENCES member (id)", 1, C4))
o += tag(t, rf, "member의 id만 받아요", C4, 1, gap=40)
o.append(under(t, er, '"orders_member_id_fkey"', 2, OR))
o.append(under(t, er + 1, 'is not present in table "member"', 3, RED))
o.append(caption("member 표를 먼저 만들어야 orders에서 가리킬 수 있어요. 지울 때는 거꾸로 orders부터예요.", t.y + t.h + 40, 4, size=28))
W("f-fk", o, "member 표를 먼저 만들어 두고 orders를 만들었어요. member_id 뒤에 REFERENCES member (id)를 붙였어요. 회원 kim과 lee를 넣었으니 id는 1과 2예요. kim의 주문은 들어가요. member_id 99로 주문하면 orders_member_id_fkey에 걸려요. DETAIL은 키 99가 member 표에 없다는 뜻이에요. SELECT로 보면 kim의 주문 하나만 들어 있어요. 가리킬 표가 있어야 하니 member를 먼저 만들어요. 지울 때는 반대로 자식 표 orders부터 지워요. 4파트 끝에서 순서가 틀리면 나는 오류를 봐요." + REAL)

o = frame("f-del", EB4, "주문이 남은 회원은 지울 수 없어요", C4)
L = P("fk-del")
t = PT(rewrap(L, 92), 96, 250, size=32, w=1728, lh=1.6, tid="t-fd", maxb=880)
er = li(t, "ERROR")
d2 = li(t, "DELETE 1")
o.append(t.html())
o.append(under(t, li(t, "DETAIL"), 'is still referenced from table "orders"', 1, RED))
o += tag(t, d2, "lee는 주문이 없어서 지워져요", OKC, 2, gap=48)
o.append(caption("지우면 orders에 주인 없는 주문이 생기니, PostgreSQL이 부모 쪽 DELETE도 막아요.", t.y + t.h + 48, 3, size=30))
W("f-del", o, "외래 키는 자식 표에 넣을 때만 막는 게 아니에요. 부모 표에서 지울 때도 막아요. kim은 주문이 하나 있어요. kim을 지우려고 하면 ERROR가 나요. DETAIL은 키 1이 아직 orders 표에서 쓰이고 있다는 뜻이에요. kim을 지우면 orders에 주인 없는 주문이 남으니까 막는 거예요. lee는 주문이 없어서 DELETE 1로 지워져요. 회원이 탈퇴할 때 주문을 어떻게 할지 정하는 방법이 다음 장이에요." + REAL)

o = frame("f-cas", EB4, "ON DELETE CASCADE를 붙이면 자식 행도 같이 지워져요", C4)
L = P("fk-cascade")
t = PT(L, 96, 214, size=30, w=1728, lh=1.5, tid="t-fc", maxb=1000)
cs = li(t, "ON DELETE CASCADE")
dl = li(t, "DELETE 1")
sel = li(t, "SELECT")
o.append(t.html())
o.append(rring(t, cs, "ON DELETE CASCADE", 1, C4))
o += tag(t, cs, "부모를 지우면 같이", C4, 1, gap=40)
o.append(lspot_t(t, li(t, "VALUES (1, 104000)"), li(t, "VALUES (1, 104000)"), 2))
o.append(lspot_t(t, dl - 1, dl, 3))
o.append(lspot_t(t, sel, len(L) - 1, 4))
o.append(spot_off(5))
o += tag(t, sel + 3, "kim의 주문 2개가 사라지고 lee 주문만 남았어요", C4, 5, gap=40)
W("f-cas", o, "member_id 뒤에 ON DELETE CASCADE를 더 붙였어요. 부모 행을 지우면 그 번호를 쓰던 자식 행도 같이 지우라는 뜻이에요. kim의 주문 두 개, lee의 주문 하나를 넣었어요. 이번에는 kim을 지워도 오류가 안 나요. SELECT로 보면 kim의 주문 두 개가 같이 사라지고 lee의 주문만 남았어요. 편하지만 한 줄 DELETE로 여러 표의 행이 사라질 수 있어요. 장바구니처럼 회원이 없으면 의미가 없는 행에만 붙여요. 주문 기록처럼 남겨야 하는 행에는 붙이지 않아요." + REAL)

o = frame("f-cmp", EB4, "부모를 지울 때 자식 행을 어떻게 할지 골라요", C4)
L_r = P("fk-restrict", 0, "DELETE FROM")
L_n = P("fk-setnull", 0, "SELECT")
rows_ = [(kw("(안 적음)", GRAY), "자식이 있으면 DELETE를 막아요", "기본값, 주문 기록"),
         (kw("ON DELETE RESTRICT", C4), "자식이 있으면 DELETE를 막아요", "막는다는 뜻을 적어 두고 싶을 때"),
         (kw("ON DELETE CASCADE", C4), "자식 행도 같이 지워요", "장바구니, 회원의 설정"),
         (kw("ON DELETE SET NULL", C4), "자식의 외래 키 칸을 NULL로 바꿔요", "탈퇴해도 주문은 남길 때")]
tb, y0 = table(96, 222, ["붙이는 말", "부모 행을 지우면", "언제"], rows_, [560, 680, 488], "fcmp", size=27, rh=78, order=1, stagger=True)
o += tb
yt = round(y0 + 4 * 78 + 36)
t1 = PT(rewrap(L_r, 80), 96, yt, size=19, w=1060, lh=1.45, tid="t-rs", maxb=960)
t2 = PT(L_n, 1196, yt, size=19, w=628, lh=1.45, tid="t-sn", maxb=960)
o.append(f'<div{bi("rise", 5)}>' + t1.html() + t2.html() + '</div>')
o.append(p(f"position:absolute;left:96px;top:{yt + max(t1.h, t2.h) + 14}px;font-size:22px;color:{SUB}", "RESTRICT로 만든 표에서 kim 지우기", bi("rise", 5)))
o.append(p(f"position:absolute;left:1196px;top:{yt + max(t1.h, t2.h) + 14}px;font-size:22px;color:{SUB}", "SET NULL로 만든 표, kim을 지운 뒤", bi("rise", 5)))
W("f-cmp", o, "부모 행을 지울 때 자식 행을 어떻게 할지는 ON DELETE 뒤에 적어요. 아무것도 안 적으면 앞 장처럼 DELETE를 막아요. RESTRICT도 막아요. 아래 왼쪽처럼 오류 문장에 RESTRICT setting이 들어가는 것만 달라요. 막는다는 뜻을 표 설계에 적어 두고 싶을 때 써요. CASCADE는 자식 행도 같이 지워요. SET NULL은 자식 행은 남기고 외래 키 칸만 NULL로 바꿔요. 아래 오른쪽처럼 kim의 주문이 남고 member_id 칸이 비었어요. 매출 기록은 남겨야 하니 이런 경우에 써요. 이때 그 열에는 NOT NULL을 붙이면 안 돼요." + REAL)

o = frame("f-ord", EB4, "만들 때는 부모부터, 지울 때는 자식부터예요", C4)
L1 = P("fk-order")
L2 = P("fk-drop")
t1 = PT(L1, 96, 214, size=30, w=1728, lh=1.5, tid="t-fo1", maxb=530)
t2 = PT(L2, 96, t1.y + t1.h + 30, size=30, w=1728, lh=1.5, tid="t-fo2", maxb=1000)
o.append(t1.html())
o.append(t2.html())
e1 = li(t1, "ERROR")
o.append(under(t1, e1, 'relation "member" does not exist', 1, RED))
o += tag(t1, e1, "member가 아직 없어요", RED, 1, gap=40)
e2 = li(t2, "ERROR")
o.append(under(t2, e2 + 1, "constraint orders_member_id_fkey", 2, OR))
o += tag(t2, li(t2, "DROP TABLE orders"), "자식부터 지우면", OKC, 3, gap=40)
o += tag(t2, len(L2) - 1, "부모도 지워져요", OKC, 3, gap=40)
W("f-ord", o, "표를 만들고 지우는 순서도 외래 키가 정해요. 위는 member가 없는 데이터베이스에서 orders부터 만든 화면이에요. 가리킬 member 표가 없다고 ERROR가 나요. 그래서 부모 member를 먼저 만들어요. 아래는 orders가 남아 있는데 member부터 지우려고 한 화면이에요. orders_member_id_fkey가 member에 기대고 있어서 못 지운다고 나와요. HINT의 DROP ... CASCADE는 기대는 규칙까지 같이 지우는 방법인데, 무엇이 지워지는지 헷갈려서 수업에서는 쓰지 않아요. 자식 orders를 먼저 지우면 member도 지워져요." + REAL)

o = frame("f-tr", EB4, "TRUNCATE로 비우고 RESTART IDENTITY로 번호를 1부터 세요", C4)
L = P("tc-reset")
t = PT(L, 96, 214, size=26, w=1180, lh=1.36, tid="t-tr", maxb=1000)
o.append(t.html())
r1, r2, r3 = li(t, "3 | park"), li(t, "4 | choi"), li(t, "1 | choi")
o.append(rring(t, r1, "3", 1, C3))
o += tag(t, r1, "DELETE 뒤에도 3번부터", C3, 1, gap=40)
o.append(rring(t, r2, "4", 2, C3))
o += tag(t, r2, "TRUNCATE만으로는 4번", C3, 2, gap=40)
o.append(rring(t, r3, "1", 3, OKC))
o += tag(t, r3, "RESTART IDENTITY면 1번", OKC, 3, gap=40)
o += side(1330, 230, 494, kw("DELETE FROM 표;", C4), "행을 하나씩 지워요. WHERE로 골라 지울 수 있어요. 번호는 이어서 써요.", C4, 1, hsize=26, bsize=24)
o += side(1330, 450, 494, kw("TRUNCATE 표;", C4), "WHERE 없이 표를 통째로 비워요. 표 모양과 규칙은 남아요.", C4, 2, hsize=26, bsize=24)
o += side(1330, 650, 494, kw("TRUNCATE 표", OKC) + "<br>" + kw("RESTART IDENTITY;", OKC), "비우면서 자동 번호도 1로 돌려요. 연습 데이터를 처음부터 다시 넣을 때 써요.", OKC, 3, hsize=26, bsize=24)
W("f-tr", o, "표의 행을 모두 지우는 방법은 두 가지예요. 36에서 배운 DELETE는 행을 하나씩 지우고, WHERE로 고를 수도 있어요. DELETE로 다 지운 뒤 새로 넣으면 번호는 3번이에요. 번호표 기계는 지운 번호를 다시 주지 않아요. TRUNCATE는 WHERE 없이 표를 통째로 비워요. 결과도 DELETE 2가 아니라 TRUNCATE TABLE로 나와요. TRUNCATE만 쓰면 번호는 여전히 이어져서 4번이에요. 뒤에 RESTART IDENTITY를 붙이면 번호도 1부터 다시 세요. 실습 데이터를 깨끗이 지우고 다시 넣을 때 이 모양을 써요. 표 자체와 규칙은 남아요. 표까지 없애는 건 DROP TABLE이에요." + REAL)

o = frame("f-trfk", EB4, "외래 키로 이어진 표는 한 줄에 같이 적어서 비워요", C4)
L1 = P("tc-fk")
L2 = P("tc-cascade")
t1 = PT(L1, 96, 214, size=26, w=1728, lh=1.42, tid="t-tf1", maxb=560)
t2 = PT(L2, 96, t1.y + t1.h + 24, size=26, w=1728, lh=1.42, tid="t-tf2", maxb=850)
o.append(t1.html())
e1 = li(t1, "ERROR")
o.append(under(t1, e1, "cannot truncate a table referenced in a foreign key constraint", 1, RED))
o.append(under(t1, e1 + 2, 'Truncate table "orders" at the same time', 2, OR))
ok = li(t1, "TRUNCATE orders, member")
o.append(rring(t1, ok, "orders, member", 3, OKC))
o += tag(t1, ok, "자식 표와 같이 적으면 돼요", OKC, 3, gap=40)
o.append(f'<div{bi("rise", 4)}>' + t2.html() + '</div>')
o.append(under(t2, li(t2, "NOTICE"), 'truncate cascades to table "orders"', 4, OR))
o += tag(t2, li(t2, "NOTICE"), "CASCADE는 이어진 표도 비워요", C4, 4, gap=40)
cy = t2.y + t2.h + 24
o.append(p(f"position:absolute;left:96px;top:{cy}px;font-size:24px;font-weight:700;color:{GRAY}", "수업 예시: 표 여섯 개를 한 줄로 비우고 번호도 1부터", bi("rise", 5)))
o.append(p(f"position:absolute;left:96px;top:{cy + 40}px;width:1728px;padding:12px 22px;box-sizing:border-box;border-radius:12px;background:{CARD};border:2px solid #CFCAC0;font-family:{MONO};font-size:24px;font-weight:700;line-height:1.4;color:{INK};white-space:nowrap", "TRUNCATE enrollments, lockers, courses, instructors, sports, members RESTART IDENTITY;", bi("rise", 5)))
W("f-trfk", o, "외래 키로 이어진 표는 부모만 따로 비울 수 없어요. member만 TRUNCATE하면 orders가 member를 가리킨다고 ERROR가 나요. HINT는 orders도 같이 비우거나 CASCADE를 쓰라고 해요. 쉼표로 표 이름을 이어 적으면 한 번에 비워져요. 같이 비우니 적는 순서는 상관없어요. member, orders 순서로 적어도 돼요. CASCADE를 붙이면 이어진 자식 표까지 알아서 비우고, NOTICE로 어느 표를 비웠는지 알려 줘요. 어디까지 지워질지 헷갈리면 CASCADE 대신 표 이름을 다 적어요. 수업에서 쓴 줄도 같은 모양이에요. 연결된 표 여섯 개를 한 줄에 적고 RESTART IDENTITY로 번호까지 1부터 다시 세요." + REAL)

# =====================================================================
# part 5: ALTER TABLE
# =====================================================================
o = frame("a-add", EB5, "ALTER TABLE ... ADD CONSTRAINT로 만든 표에 규칙을 더해요", C5)
L = P("al-add")
t = PT(L, 96, 214, size=30, w=1728, lh=1.5, tid="t-aa", maxb=900)
sel = li(t, "SELECT")
a1 = li(t, "ALTER TABLE")
er = li(t, "ERROR")
up = li(t, "UPDATE member")
a2 = li(t, "ALTER TABLE", er + 1)
o.append(t.html())
o.append(lspot_t(t, sel + 3, sel + 4, 1))
o.append(spot_off(2))
o += tag(t, sel + 4, "이미 겹친 이메일", RED, 1, gap=40)
o.append(under(t, er + 1, "Key (email)=(kim@mail.com) is duplicated", 2, RED))
o += tag(t, up, "36의 UPDATE로 먼저 고쳐요", C5, 3, gap=40)
o += tag(t, a2 + 1, "이제 붙어요", OKC, 4, gap=40)
o.append(caption("규칙은 지금 들어 있는 행까지 검사해요. 어긋난 행부터 고쳐야 붙어요.", t.y + t.h + 40, 4, size=30))
W("a-add", o, "표를 다 만든 뒤에 규칙이 필요해질 때가 많아요. 들어가기의 규칙 없는 회원 표처럼요. ALTER TABLE 표 이름 ADD CONSTRAINT 이름 다음에 규칙을 적으면 나중에 더할 수 있어요. 그런데 email에 UNIQUE를 더하려고 하니 ERROR가 나요. kim@mail.com이 이미 두 번 들어 있어서예요. 규칙은 새로 들어올 행뿐 아니라 지금 있는 행까지 검사해요. 36에서 배운 UPDATE로 lee의 이메일을 고친 뒤 다시 치면 ALTER TABLE이 나오고 규칙이 붙어요." + REAL, ("p5", "나중에 규칙 바꾸기"))

o = frame("a-col", EB5, "NOT NULL과 DEFAULT는 ALTER COLUMN으로 바꿔요", C5)
L = P("al-col", 0, None, "\\d member")
L2 = P("al-col", 0, "\\d member")
t = PT(L, 96, 214, size=28, w=1728, lh=1.5, tid="t-ac", maxb=760)
er = li(t, "ERROR")
o.append(t.html())
o.append(under(t, er, "contains null values", 1, RED))
o += tag(t, li(t, "UPDATE member"), "비어 있던 이름부터 채워요", C5, 2, gap=40)
pkl = li(t, "ADD PRIMARY KEY")
o += tag(t, pkl, "기본 키도 나중에 붙여요", C3, 3, gap=40)
o += tag(t, li(t, "ADD COLUMN"), "열을 더하면서 기본값까지", C1, 4, gap=40)
t2 = PT(L2[:8], 96, t.y + t.h + 26, size=24, w=1728, lh=1.4, tid="t-ac2", bar=False, maxb=985)
o.append(f'<div{bi("rise", 5)}>' + t2.html() + '</div>')
W("a-col", o, "열 하나에 붙는 NOT NULL과 DEFAULT는 ALTER COLUMN으로 바꿔요. name에 SET NOT NULL을 하려니 ERROR가 나요. 3번 회원의 이름이 비어 있어서예요. 앞 장처럼 UPDATE로 이름부터 채우면 붙어요. 기본 키도 ADD PRIMARY KEY로 나중에 붙일 수 있어요. ADD COLUMN으로 열을 새로 더하면서 DEFAULT를 같이 적으면, 이미 있던 행의 points에도 0이 채워져요. 아래 백슬래시 d에 바뀐 결과가 모였어요." + REAL)

o = frame("a-drop", EB5, "DROP CONSTRAINT 이름으로 규칙을 지워요", C5)
L = P("al-drop")
t = PT(L, 96, 214, size=30, w=1728, lh=1.5, tid="t-ad", maxb=1000)
d1 = li(t, "DROP CONSTRAINT")
o.append(t.html())
o.append(rring(t, d1, "member_email_key", 1, C2))
o += tag(t, d1, "규칙 이름으로 지워요", C5, 1, gap=40)
o += tag(t, li(t, "DROP NOT NULL"), "NOT NULL 빼기", C5, 2, gap=40)
o += tag(t, li(t, "SET DEFAULT 100"), "기본값 바꾸기", C5, 3, gap=40)
ix = li(t, "Indexes")
o.append(lspot_t(t, ix, len(L) - 1, 4))
o.append(spot_off(5))
o += tag(t, len(L) - 1, "member_email_key가 없어졌어요", C5, 5, gap=40)
W("a-drop", o, "규칙을 지울 때는 DROP CONSTRAINT 뒤에 규칙 이름을 적어요. 2파트에서 본 이름이 여기서 쓰여요. 이름을 모르면 먼저 백슬래시 d로 봐요. NOT NULL은 이름이 없어서 ALTER COLUMN name DROP NOT NULL로 빼요. 기본값은 SET DEFAULT로 바꿔요. 바꾼 기본값은 앞으로 넣는 행에만 쓰이고, 이미 있는 행의 값은 그대로예요. 백슬래시 d로 보면 Indexes에 member_pkey만 남고 member_email_key가 없어졌어요." + REAL)

# =====================================================================
# part 6: errors, traps, the shopping cart
# =====================================================================
o = frame("x-read", EB6, "ERROR 줄의 앞부분으로 어느 규칙인지 알아봐요", C6)
rows_ = [(kw("null value in column ...", C6), "NOT NULL", "비운 열에 값을 넣어요"),
         (kw("duplicate key value ... unique", C6), "UNIQUE, PRIMARY KEY", "DETAIL의 겹친 값을 바꿔요"),
         (kw("violates check constraint", C6), "CHECK", "조건에 맞게 값을 고쳐요"),
         (kw("violates foreign key constraint", C6), "FOREIGN KEY", "부모 행을 먼저 넣거나, 자식 행부터 지워요"),
         (kw("cannot insert a non-DEFAULT value", C6), "ALWAYS AS IDENTITY", "번호 열을 INSERT에서 빼요"),
         (kw("could not create unique index", C6), "ALTER TABLE ADD", "어긋난 행을 UPDATE로 고친 뒤 다시"),
         (kw("cannot drop table ...", C6), "DROP 순서", "자식 표부터 지워요")]
tb, y0 = table(96, 222, ["ERROR 줄", "걸린 규칙", "고치는 법"], rows_, [760, 420, 548], "xr", size=26, rh=80, order=1, stagger=False)
o += tb
o.append(caption("DETAIL 줄에는 막힌 행이나 겹친 값이 그대로 나와요. 고칠 값은 거기서 찾아요.", y0 + 7 * 80 + 36, 2, size=28))
W("x-read", o, "오늘 본 오류를 한 표에 모았어요. 영어 문장이 길어도 앞부분만 읽으면 어느 규칙에 걸렸는지 알 수 있어요. null value는 NOT NULL, duplicate key는 UNIQUE나 기본 키, check constraint는 CHECK, foreign key constraint는 외래 키예요. 그 뒤의 따옴표 안이 규칙 이름이에요. DETAIL 줄에는 막힌 행이나 겹친 값이 그대로 나와요. 고칠 값은 거기서 찾아요. 외래 키 오류는 넣을 때와 지울 때 둘 다 나요. 넣을 때는 부모 행을 먼저 넣고, 지울 때는 자식 행부터 지워요.")

o = frame("x-trap", EB6, "NULL은 UNIQUE, CHECK, DEFAULT를 그냥 지나가요", C6)
L = P("tr-null")
L2 = P("tr-default")
t = PT(L, 96, 206, size=26, w=1728, lh=1.4, tid="t-tn", maxb=680)
ins = li(t, "VALUES (1, NULL")
sel = li(t, "SELECT")
o.append(t.html())
o.append(lspot_t(t, sel + 3, sel + 4, 1))
o.append(spot_off(4))
o += tag(t, sel + 3, "email NULL이 두 번 들어갔어요 (UNIQUE 통과)", OR, 1, gap=40, at=t.x + 560)
o += tag(t, sel + 5, "points도 NULL, DEFAULT 0이 안 쓰이고 CHECK도 통과", OR, 2, gap=40, at=t.x + 560)
t2 = PT(L2, 96, t.y + t.h + 24, size=26, w=1728, lh=1.4, tid="t-td", bar=False, maxb=1010)
o.append(f'<div{bi("rise", 3)}>' + t2.html() + '</div>')
o.append(rring(t2, 0, "DEFAULT", 3, C1))
o += tag(t2, 0, "값 자리에 DEFAULT를 쓰면 기본값", C1, 3, gap=40)
W("x-trap", o, "NULL은 값이 없다는 뜻이라서 규칙 몇 개를 그냥 지나가요. email에 UNIQUE가 있어도 NULL은 두 번 들어가요. 없는 값끼리는 겹친다고 보지 않아서예요. points에 NULL을 직접 적으면 DEFAULT 0이 쓰이지 않아요. DEFAULT는 열을 안 적었을 때만 쓰여요. CHECK (points >= 0)도 통과해요. NULL과 비교한 결과는 참도 거짓도 아니라서, CHECK는 거짓일 때만 막아요. 아래처럼 값 자리에 DEFAULT라고 적으면 기본값이 들어가요. 이 구멍을 막는 방법이 다음 장이에요." + REAL)

o = frame("x-fix", EB6, "비면 안 되는 열에는 NOT NULL을 같이 붙여요", C6)
L = P("tr-fix")
t = PT(L, 96, 214, size=30, w=1728, lh=1.5, tid="t-tf", maxb=900)
r1 = li(t, "NOT NULL UNIQUE")
r2 = li(t, "NOT NULL DEFAULT 0")
e1 = li(t, "ERROR")
e2 = li(t, "ERROR", e1 + 1)
o.append(t.html())
o.append(rring(t, r1, "NOT NULL", 1, C1))
o.append(rring(t, r2, "NOT NULL", 1, C1))
o += tag(t, e1 + 1, "email이 비면 막아요", C1, 2, gap=40)
o += tag(t, e2 + 1, "points에 NULL을 적어도 막아요", C1, 3, gap=40)
o += tag(t, li(t, "INSERT 0 1"), "points를 빼면 DEFAULT 0", OKC, 4, gap=40)
o.append(caption(f"{kw('NOT NULL UNIQUE', C2)}, {kw('NOT NULL DEFAULT 0 CHECK (...)', C2)}처럼 한 열에 규칙 여러 개를 이어 적어요.", t.y + t.h + 40, 4, size=28))
W("x-fix", o, "앞 장의 구멍은 NOT NULL로 막아요. email은 NOT NULL UNIQUE, points는 NOT NULL DEFAULT 0 CHECK로 바꿨어요. 한 열에 규칙을 여러 개 띄어서 이어 적으면 돼요. 이제 email이 비면 not-null 오류가 나요. points에 NULL을 직접 적어도 막아요. points를 아예 빼면 DEFAULT 0이 들어가요. 그래서 비어 있으면 안 되는 열에는 UNIQUE, CHECK, DEFAULT를 붙일 때 NOT NULL을 같이 붙여요." + REAL)

# --- the shopping cart of 28 ---
o = frame("e-map", EB6, "28의 장바구니를 표 세 개로 옮겨요", C6)
o.append(p(f"position:absolute;left:96px;top:226px;font-size:26px;font-weight:700;color:{GRAY}", "28의 파이썬 코드"))
code_l = ["class Product:", "    def __init__(self, name,", "                 price, stock):", "        self.id = Product.next_id", "        self.name = name", "        self.price = price", "        self.stock = stock", "", "class Cart:", "    def __init__(self):", "        self.items = {}  # {상품: 수량}"]
ed, g = editor("e-py", "product.py, cart.py", code_l, 96, 270, 760, fs=24, nums=False)
o.append(ed)
# tables
s1, gt1 = sheet(1000, 250, ["id", "name", "price", "stock"], [], "tp", [110, 200, 160, 160], size=26, rh=64, name="product", ncol=C3, pk=True)
s2, gt2 = sheet(1000, 470, ["member_id", "product_id", "qty"], [], "tc", [230, 240, 160], size=26, rh=64, name="cart_item", ncol=C4)
s3, gt3 = sheet(1000, 690, ["id", "name", "email"], [], "tm", [110, 200, 320], size=26, rh=64, name="member", ncol=C3, pk=True)
o += [f'<div{bi("rise", 1)}>{s1}</div>', f'<div{bi("rise", 2)}>{s2}</div>', f'<div{bi("rise", 3)}>{s3}</div>']
o.append(link(1, g["tx"] + tw("        self.stock = stock", 24) + 20, gcy(g, 5), 996, 300, C3))
o.append(link(2, g["tx"] + tw("        self.items = {}  # {상품: 수량}", 24) - 140, gcy(g, 10) - 16, 996, 520, C4))
o += side(96, 270 + g["h"] + 36, 760, "items 딕셔너리의 키 = 복합 기본 키", f"딕셔너리 키가 겹치지 않듯이, {kw('(member_id, product_id)', C3)} 쌍도 겹치면 안 돼요.", INK, 4, hsize=27, bsize=24)
o.append(p(f"position:absolute;left:1000px;top:900px;width:824px;font-size:24px;line-height:1.5;color:{SUB}", "파이썬 장바구니는 한 사람 것이었지만, 표에는 회원이 여럿이라 member 표와 member_id가 더 생겨요.", bi("rise", 3)))
W("e-map", o, "28 미니 프로젝트의 장바구니를 표로 옮겨 봐요. Product 클래스의 칸 id, name, price, stock은 product 표의 열이 돼요. Product.next_id로 번호를 세던 일은 IDENTITY가 해요. Cart의 items 딕셔너리는 상품을 키로, 수량을 값으로 담았어요. 표로 옮기면 cart_item 표의 product_id와 qty예요. 파이썬 장바구니는 한 사람 것이었지만, 데이터베이스에는 회원이 여럿이니 member 표와 member_id가 더 생겨요. 15에서 딕셔너리 키는 겹치지 않는다고 했어요. 그 규칙이 표에서는 (member_id, product_id) 복합 기본 키예요.")

o = frame("e-make", EB6, "규칙을 붙여 member, product, cart_item을 만들어요", C6)
L = P("ex-make")
t = PT(L, 96, 200, size=24, w=1728, lh=1.4, tid="t-em", maxb=1010)
o.append(t.html())
labels = [("NOT NULL UNIQUE", "로그인용 이메일은 겹치지 않게", C2, 1), ("DEFAULT 0 CHECK (stock >= 0)", "0원 상품, 음수 재고 막기", C2, 1),
          ("ON DELETE CASCADE", "탈퇴하면 장바구니도 비우기", C4, 2), ("PRIMARY KEY (member_id", "같은 상품은 한 줄", C3, 3)]
for sub, lab, c, k in labels:
    i = li(t, sub)
    o += tag(t, i, lab, c, k, gap=40)
W("e-make", o, "오늘 배운 규칙을 모아 표 세 개를 만들어요. member의 email은 로그인에 쓰니 NOT NULL UNIQUE예요. product의 price는 0보다 커야 하고, stock은 안 적으면 0, 음수는 안 돼요. cart_item의 member_id는 member를 가리키고, 탈퇴하면 장바구니도 같이 비우도록 CASCADE를 붙였어요. product_id는 product를 가리켜요. 아무것도 안 적었으니 장바구니에 담긴 상품은 못 지워요. qty는 0보다 커야 하고, 같은 회원이 같은 상품을 두 줄로 담지 않게 복합 기본 키를 붙였어요. 백슬래시 dt로 표 세 개를 확인해요. 부모 표 member와 product를 먼저 만들었어요." + REAL)

o = frame("e-cart", EB6, "장바구니에 담을 때 규칙이 실수를 막아요", C6)
L = P("ex-data", 0, "SELECT")
L2 = P("ex-cart")
t = PT(L2, 96, 200, size=26, w=1728, lh=1.42, tid="t-ec", maxb=890)
o.append(t.html())
e1 = li(t, "ERROR")
up = li(t, "UPDATE cart_item")
e2 = li(t, "ERROR", up)
e3 = li(t, "ERROR", e2 + 1)
o += tag(t, e1, "같은 상품을 또 담으면 막혀요", C3, 1, gap=30)
o += tag(t, up, "qty를 늘려요, 28의 get(product, 0) + qty", C5, 2, gap=30)
o += tag(t, e2, "9번 상품은 없어요", C4, 3, gap=30)
o += tag(t, e3, "0개는 못 담아요", C2, 4, gap=30)
prods = [l.split("|") for l in L if re.match(r"^\s+\d+ \|", l)]
px_ = 96
o.append(p(f"position:absolute;left:96px;top:{t.y + t.h + 30}px;font-size:22px;font-weight:700;color:{GRAY}", "product 표에 넣어 둔 28의 상품 (SELECT * FROM product 결과)"))
cs = []
for pr in prods:
    txt = f"{pr[0].strip()} {pr[1].strip()} {int(pr[2]):,}원" + (" 품절" if pr[3].strip() == "0" else "")
    cs.append(chip(0, 0, txt, C3, VOBG, None, size=22, mono=False).replace("position:absolute;left:0px;top:0px;", "position:relative;"))
o.append(f'<div style="position:absolute;left:96px;top:{t.y + t.h + 72}px;display:flex;gap:16px">' + "".join(cs) + '</div>')
W("e-cart", o, "28의 상품 다섯 개를 product 표에 넣었어요. 이름은 psql 표가 줄이 맞게 영어로 바꿨어요. kim이 이어폰 하나와 텀블러 두 개를 담았어요. 텀블러를 하나 더 담으려고 INSERT를 또 치면 복합 기본 키에 걸려요. 28의 cart.py에서는 self.items.get(product, 0) + qty로 수량을 늘렸어요. 표에서도 같아요. UPDATE로 qty를 1 늘려요. 없는 9번 상품을 담으면 외래 키에, 0개를 담으면 CHECK에 걸려요. 파이썬 코드에서 if로 막던 실수를 표의 규칙이 막아요. 마지막 SELECT에 텀블러가 3개로 한 줄만 있어요." + REAL)

o = frame("e-leave", EB6, "탈퇴, 상품 삭제, 같은 이메일도 규칙대로 처리돼요", C6)
L = P("ex-leave")
t = PT(L, 96, 214, size=28, w=1728, lh=1.5, tid="t-el", maxb=1000)
e1 = li(t, "ERROR")
dm = li(t, "DELETE FROM member")
sel = li(t, "SELECT")
e2 = li(t, "ERROR", sel)
e3 = li(t, "ERROR", e2 + 1)
o.append(t.html())
o += tag(t, e1 + 1, "장바구니에 담긴 상품은 못 지워요", C4, 1, gap=40)
o += tag(t, dm + 1, "kim 탈퇴, CASCADE", C4, 2, gap=40)
o.append(lspot_t(t, sel, sel + 3, 2))
o.append(spot_off(3))
o += tag(t, sel + 3, "lee 것만 남았어요", C4, 2, gap=40)
o += tag(t, e2, "이메일 겹침", C2, 3, gap=40)
o += tag(t, e3, "재고 음수", C2, 4, gap=40)
W("e-leave", o, "장바구니가 찬 상태에서 일을 몇 가지 해 봐요. 텀블러는 kim과 lee의 장바구니에 담겨 있어서 product에서 지우려고 하면 외래 키에 걸려요. 담긴 상품이 사라지면 장바구니에 없는 상품이 남으니까요. kim이 탈퇴하면 CASCADE 때문에 kim의 장바구니 두 줄도 같이 지워져요. SELECT로 보면 lee의 텀블러 한 줄만 남았어요. 새 회원 park이 lee와 같은 이메일로 가입하면 UNIQUE에, 재고를 -1로 바꾸면 CHECK에 걸려요. UPDATE도 INSERT처럼 문지기를 지나요." + REAL)

# =====================================================================
# summary
# =====================================================================
o = frame("sum", "정리", "규칙마다 언제 붙이는지 정리해요", INK)
rows_ = [(kw("NOT NULL", C1), "꼭 있어야 하는 값", "이름, 가격, 수량"),
         (kw("DEFAULT 값", C1), "안 적으면 채울 값", "포인트 0, 가입 시각 now()"),
         (kw("UNIQUE", C2), "겹치면 안 되는 값", "이메일, 아이디"),
         (kw("CHECK (조건)", C2), "범위가 정해진 값", "가격 > 0, 재고 >= 0"),
         (kw("PRIMARY KEY", C3), "행마다 다른 번호", "GENERATED ALWAYS AS IDENTITY와 같이"),
         (kw("PRIMARY KEY (a, b)", C3), "쌍이 겹치면 안 될 때", "주문 상품, 장바구니"),
         (kw("REFERENCES 표 (열)", C4), "다른 표에 있는 번호만", "주문의 회원 번호, ON DELETE"),
         (kw("ALTER TABLE", C5), "만든 뒤 규칙 더하기, 지우기", "ADD CONSTRAINT, DROP CONSTRAINT")]
tb, y0 = table(96, 206, ["규칙", "언제", "예"], rows_, [560, 560, 608], "sum", size=26, rh=72, order=None)
o += tb
o.append(f'<div style="position:absolute;left:96px;top:{y0 + 8 * 72 + 30:.0f}px;width:1728px;height:96px;background:{CARD};border:2px solid {LINE};border-radius:16px;padding:0 30px;display:flex;align-items:center;gap:24px">'
         + p(f"font-size:26px;font-weight:700;color:{INK};white-space:nowrap", "다음에 배울 것")
         + p(f"font-size:24px;color:{SUB};white-space:nowrap", f"표 여러 개를 이어 읽는 {kw('JOIN', BL)}, 개수와 합계를 세는 {kw('COUNT', BL)} {kw('SUM', BL)}, 묶어서 세는 {kw('GROUP BY', BL)}") + '</div>')
W("sum", o, "오늘 배운 규칙을 한 장에 모았어요. 꼭 있어야 하는 값은 NOT NULL, 안 적으면 채울 값은 DEFAULT, 겹치면 안 되는 값은 UNIQUE, 범위가 정해진 값은 CHECK예요. 행마다 다른 번호는 기본 키로, 번호는 GENERATED ALWAYS AS IDENTITY로 채워요. 쌍이 겹치면 안 되면 복합 기본 키, 다른 표의 번호만 받으려면 REFERENCES예요. 이미 만든 표는 ALTER TABLE로 고쳐요. 오늘 만든 member, product, cart_item은 외래 키로 이어져 있어요. 다음에는 이렇게 이어진 표를 한 번에 읽는 JOIN과, 개수와 합계를 세는 집계 함수를 배워요.", ("end", "정리"))

o = frame("cheat", "치트시트", "규칙을 붙인 CREATE TABLE 한 장", INK)
CL = ["CREATE TABLE member (",
      "  id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,",
      "  name VARCHAR(20) NOT NULL,",
      "  email VARCHAR(50) NOT NULL UNIQUE,",
      "  points INTEGER NOT NULL DEFAULT 0 CHECK (points >= 0),",
      "  joined_at TIMESTAMPTZ DEFAULT now()",
      ");",
      f"-- product는 {ORDER.index('e-make') + 1}쪽과 같아요",
      "CREATE TABLE cart_item (",
      "  member_id INTEGER REFERENCES member (id) ON DELETE CASCADE,",
      "  product_id INTEGER REFERENCES product (id),",
      "  qty INTEGER NOT NULL CHECK (qty > 0),",
      "  PRIMARY KEY (member_id, product_id),",
      "  CONSTRAINT qty_limit CHECK (qty <= 99)",
      ");"]
ed, g = editor("ch-sql", "schema.sql", CL, 96, 200, 1130, fs=22, nums=False, color=PG)
o.append(ed)
AL = [("ALTER TABLE member\n  ADD CONSTRAINT 이름 UNIQUE (email);", "규칙 더하기"),
      ("ALTER TABLE member\n  DROP CONSTRAINT 이름;", "규칙 지우기"),
      ("ALTER TABLE member ALTER COLUMN\n  name SET NOT NULL;", "NOT NULL 붙이기 (DROP으로 빼기)"),
      ("ALTER TABLE member ALTER COLUMN\n  points SET DEFAULT 100;", "기본값 바꾸기"),
      ("TRUNCATE cart_item, member\n  RESTART IDENTITY;", "같이 비우고 번호는 1부터"),
      ("\\d member", "붙은 규칙 보기")]
y = 206
for k_, d_ in AL:
    nl = k_.count("\n") + 1
    o.append(p(f"position:absolute;left:1270px;top:{y}px;width:554px;font-family:{MONO};font-size:19px;font-weight:700;line-height:1.4;color:{INK};white-space:pre", e(k_)))
    o.append(p(f"position:absolute;left:1270px;top:{y + nl * 19 * 1.4 + 4:.0f}px;width:554px;font-size:19px;line-height:1.35;color:{SUB}", e(d_)))
    y += nl * 19 * 1.4 + 4 + 19 * 1.35 + 30
o.append(caption("만들 때는 부모 표(member, product)부터, 지울 때는 자식 표(cart_item)부터예요.", 200 + g["h"] + 30, None, size=24, color=SUB))
W("cheat", o, "실습할 때 옆에 열어 둘 한 장이에요. 왼쪽은 오늘 배운 규칙을 다 붙인 CREATE TABLE이에요. 번호 열, NOT NULL, UNIQUE, DEFAULT, CHECK, 외래 키와 ON DELETE, 복합 기본 키, 이름을 붙인 규칙이 다 들어 있어요. 오른쪽은 만든 표를 고치는 ALTER TABLE 명령이에요. 규칙이 잘 붙었는지는 백슬래시 d로 봐요. 표를 만들 때는 부모 표부터, 지울 때는 자식 표부터예요.")

# =====================================================================
# toc
# =====================================================================
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
PL = [(C1, EB1[3:], "NOT NULL, DEFAULT와 now(), \\d로 규칙 보기", "n-nn", "n-d"),
      (C2, EB2[3:], "UNIQUE, CHECK, CONSTRAINT 이름 붙이기, 자동 이름 읽기", "u-uq", "k-rule"),
      (C3, EB3[3:], "PRIMARY KEY, SERIAL과 함정, GENERATED ALWAYS AS IDENTITY, 복합 기본 키와 복합 UNIQUE", "p-pk", "p-cu"),
      (C4, EB4[3:], "FOREIGN KEY, 부모 행 지우기, ON DELETE CASCADE, RESTRICT, SET NULL, 만들고 지우는 순서, TRUNCATE", "f-pic", "f-trfk"),
      (C5, EB5[3:], "ALTER TABLE ADD CONSTRAINT, ALTER COLUMN, DROP CONSTRAINT", "a-add", "a-drop"),
      (C6, EB6[3:], "오류 읽기, NULL 함정, 28 장바구니를 member, product, cart_item으로", "x-read", "e-leave")]
o = frame("toc", "", "오늘의 순서", INK)
for i, (c, h, s_, a, b) in enumerate(PL):
    y = 214 + i * 116
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:1px;background:{LINE}"></div>')
    o.append(p(f"position:absolute;left:96px;top:{y + 22}px;width:80px;font-size:48px;font-weight:900;line-height:1.5;color:{c}", str(i + 1)))
    o.append(p(f"position:absolute;left:190px;top:{y + 18}px;font-size:34px;font-weight:700;color:{INK}", e(h)))
    o.append(p(f"position:absolute;left:190px;top:{y + 70}px;font-size:22px;color:{SUB}", e(s_)))
    o.append(p(f"position:absolute;left:1524px;top:{y + 40}px;width:300px;text-align:right;font-size:28px;font-weight:700;color:{GRAY}", f"{page[a]}–{page[b]}쪽"))
o.append(f'<div style="position:absolute;left:96px;top:{214 + len(PL) * 116}px;width:1728px;height:1px;background:{LINE}"></div>')
o.append(p(f"position:absolute;left:96px;top:{214 + len(PL) * 116 + 30}px;font-size:26px;color:{SUB}", f"{page['why']}–{page['min']}쪽은 들어가기, {page['sum']}–{page['cheat']}쪽은 정리와 치트시트예요."))
o = [x for x in o if 'id="eyebrow"' not in x]
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(o) + f"\n<aside>{e('여섯 파트로 나눴어요. 1파트는 비우면 안 되는 열과 기본값, 2파트는 겹치면 안 되는 값과 범위예요. 3파트에서 기본 키와 자동 번호, 열 두 개로 만든 기본 키를 보고, 4파트에서 외래 키로 회원과 주문을 이어요. 5파트는 만든 표에 규칙을 더하고 지우는 ALTER TABLE이에요. 6파트에서 오류를 모아 읽고, 28의 장바구니를 표 세 개로 옮겨요.')}</aside>\n</section>\n")

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-17T00:00:00Z"}, "lists": "css", "title": "SQL 2 (제약 조건으로 표 설계하기)", "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
for w_ in WARN:
    print("WARN", w_)
print(len(ORDER), "slides")
