r"""Generates every slide of the SQL 5 deck (40, UNION and JOIN) and slides/deck.json.

Story: 36 to 39 read one table at a time. Real questions need two: who are the member numbers in enrollments, which
members took course 4 in any of three months. UNION stacks results of the same shape on top of each other (rows add
up); JOIN puts two tables side by side and pairs rows whose key matches (columns add up). Part 1 UNION ALL, UNION,
a label column, the column rules and ORDER BY at the end. Part 2 table aliases, JOIN ... ON, one row meeting many,
rows without a partner dropping out, three tables. Part 3 LEFT JOIN filling NULL, which side is left, FULL JOIN,
the three side by side and finding rows with no partner. Part 4 the same jobs in Python (13 list +, 16 set |,
15 dict lookup and get). Part 5 errors and traps, part 6 the class queries as real situations.
Tables are the class sports center in ../sports.sql (shared by 38 to 41). Subqueries (41) and GROUP BY stay out.

Every terminal line comes from tools/demo.py (real Docker and postgres:18 = PostgreSQL 18.7, in tools/out.json).
Usage (in 40-sql-union-join): python3 tools/gen.py slides
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


def obox(order, x, y, w, h, color, kind="fade", sw=4, r=12):
    """an outline drawn as svg, used to mark a column across terminal rows"""
    return (f'<svg{bi(kind, order)} style="position:absolute;left:{x:.0f}px;top:{y:.0f}px;width:{w:.0f}px;height:{h:.0f}px;overflow:visible">'
            f'<rect x="{sw/2}" y="{sw/2}" width="{w - sw:.0f}" height="{h - sw:.0f}" rx="{r}" fill="none" stroke="{color}" stroke-width="{sw}"/></svg>')


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
# chapter 40 helpers
# =====================================================================
EB1, EB2, EB3, EB4, EB5, EB6 = "1. 위아래로 쌓기 (UNION)", "2. 옆으로 붙이기 (JOIN)", "3. 짝이 없어도 남기기", "4. 앞에서 배운 것과 비교", "5. 자주 나는 오류와 함정", "6. 실제 상황 예제"
C1, C2, C3, C4, C5, C6 = TEAL, PG, OR, GR, RED, MAG
# one colour per table, used everywhere the table shows up
TE, TEBG = "#6B4BC4", "#EFEBFA"      # enrollments e
TM, TMBG = "#2459C9", "#E8EFFD"      # members m
TC, TCBG = "#1F8A4C", "#E4F3EA"      # courses c
TI, TIBG = "#B26A00", "#FBF0DF"      # instructors i
TS, TSBG = "#5B6270", "#EEF0F3"      # sports
NUL = NL
KWS = ("SELECT", "FROM", "WHERE", "JOIN", "LEFT", "FULL", "OUTER", "INNER", "ON", "UNION", "ALL", "AS", "AND", "OR",
       "ORDER", "BY", "LIMIT", "IS", "NULL", "NOT", "DESC", "IN", "COUNT")


def P(scene, *idx, k=0):
    """psql lines of statements idx of a scene, without blank lines at the end"""
    return Q(scene, *idx, k=k)


def body(lines):
    """the output part of one statement (everything after the prompt lines)"""
    i = next(n for n, l in enumerate(lines) if not PROMPT_RE.match(l))
    return lines[i:]


def sqlhl(line, marks=None):
    """one SQL line as HTML: keywords bold blue, 'strings' green, numbers orange; marks wrap substrings"""
    out, i = "", 0
    toks = re.findall(r"'[^']*'|[A-Za-z_][A-Za-z_0-9]*|\d+|\s+|.", line)
    for t_ in toks:
        if t_.startswith("'"):
            out += f'<span style="color:{GR}">{e(t_)}</span>'
        elif t_ in KWS:
            out += f'<span style="color:{PG};font-weight:700">{e(t_)}</span>'
        elif t_.isdigit():
            out += f'<span style="color:{OR}">{e(t_)}</span>'
        else:
            out += e(t_)
    for k, v in (marks or {}).items():
        attrs = v if "=" in v else f'id="{v}"'
        out = out.replace(e(k), f'<span {attrs}>{e(k)}</span>', 1) if "<" not in e(k) else out
    return out


def code(lines, x, y, w, size=28, cid="code", attrs="", marks=None, lh=1.55, pad=(26, 34), raw=None, h=None):
    """a white SQL card. marks: {line index: {substring: id or attrs}}. raw: {line index: html} replaces a line"""
    marks, raw = marks or {}, raw or {}
    lp = round(size * lh)
    hh = h or (2 * pad[0] + len(lines) * lp)
    rows = []
    for i, l in enumerate(lines):
        hl_ = raw.get(i) if i in raw else sqlhl(l, marks.get(i))
        rows.append(p(f"height:{lp}px;font-family:{MONO};font-size:{size}px;line-height:{lp}px;white-space:pre;color:{INK};font-weight:500", hl_ or "&#160;"))
        if x + pad[1] + tw(l, size) > x + w - 12:
            WARN.append(f"{cid}: line {i} '{l[:30]}' runs past the card")
    if y + hh > 1040:
        WARN.append(f"{cid}: card bottom {y + hh}")
    html_ = (f'<div id="{cid}"{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{hh}px;background:{CARD};border:2px solid {LINE};border-radius:16px;padding:{pad[0]}px {pad[1]}px;font-variant-ligatures:none">'
             + "".join(rows) + '</div>')
    g = {"x": x, "y": y, "w": w, "h": hh, "lp": lp, "tx": x + 2 + pad[1], "ty": y + 2 + pad[0], "size": size, "lines": lines}
    return html_, g


def cx_(g, i, sub):
    """x of substring sub on line i of a code card"""
    l = g["lines"][i]
    return g["tx"] + tw(l[:l.index(sub)], g["size"])


def cw_(g, sub):
    return tw(sub, g["size"])


def cline_y(g, i):
    return g["ty"] + i * g["lp"]


def cbox(g, i, sub, color, order, pad=6):
    x = cx_(g, i, sub)
    return pen_box(order, round(x - pad - 2), round(cline_y(g, i) + 2), round(cw_(g, sub) + 2 * pad + 4), round(g["lp"] - 4), color)


def cul(g, i, sub, color, order):
    x = cx_(g, i, sub)
    return underline(order, round(x), round(x + cw_(g, sub)), round(cline_y(g, i) + g["lp"] - 4), color)


def tname(x, y, text, color, size=24, attrs="", h=None):
    h = h or size + 20
    return p(f"position:absolute;left:{x:.0f}px;top:{y:.0f}px;height:{h}px;padding:0 16px;border-radius:10px 10px 0 0;background:{color};font-family:{MONO};font-size:{size}px;font-weight:700;line-height:{h}px;color:#FFFFFF;white-space:nowrap", e(text), attrs)


def mtable(x, y, name, color, cols, rows, widths, tid, size=24, rh=48, hh=None, row_attrs=None, cell_style=None,
           name_attrs="", attrs="", dim_rows=(), mono_cols=(), head=True, show_name=True, bg=CARD):
    """a small drawn table: name tab, header row and rows. Each row is a div #tid-rI (so it can fly or fade);
    cells are #tid-rIcJ. A cell value None is drawn as a NULL chip. Returns (html, geometry)."""
    row_attrs, cell_style = row_attrs or {}, cell_style or {}
    hh = hh or (rh if head else 0)
    W_ = sum(widths)
    ny = 0
    o = [f'<div id="{tid}"{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{W_}px;height:{(size + 20 if show_name else 0) + hh + rh * len(rows) + 4}px">']
    if show_name:
        o.append(tname(0, 0, name, color, size=size - 2, h=size + 18, attrs=name_attrs))
        ny = size + 18
    o.append(f'<div style="position:absolute;left:0;top:{ny}px;width:{W_}px;height:{hh + rh * len(rows) + 4}px;background:{bg};border:2px solid {color};border-radius:{"0 12px 12px 12px" if show_name else "12px"}"></div>')
    xs = [sum(widths[:j]) for j in range(len(widths))]
    if head:
        o.append(f'<div style="position:absolute;left:2px;top:{ny + 2}px;width:{W_ - 4}px;height:{hh}px;background:{color}14"></div>')
        for j, c_ in enumerate(cols):
            o.append(p(f"position:absolute;left:{xs[j]}px;top:{ny + 2 + (hh - size * 1.3) / 2:.0f}px;width:{widths[j]}px;text-align:center;font-family:{MONO};font-size:{size - 3}px;font-weight:700;line-height:1.3;color:{color};white-space:nowrap", e(c_), f' id="{tid}-h{j}"'))
    for i, r in enumerate(rows):
        ry = ny + 2 + hh + i * rh
        dim = i in dim_rows
        cells = []
        for j, v in enumerate(r):
            st = cell_style.get((i, j), "")
            if v is None:
                cells.append(p(f"position:absolute;left:{xs[j] + widths[j] / 2 - 40:.0f}px;top:{(rh - size - 6) / 2:.0f}px;width:80px;height:{size + 6}px;border-radius:8px;background:{NLBG};border:2px dashed {NUL};text-align:center;font-family:{MONO};font-size:{size - 6}px;font-weight:700;line-height:{size + 2}px;color:{NUL};{st}", "NULL", f' id="{tid}-r{i}c{j}"'))
            else:
                mono_ = j in mono_cols or re.fullmatch(r"[0-9\-:,]+", str(v))
                cells.append(p(f"position:absolute;left:{xs[j]}px;top:{(rh - size * 1.3) / 2:.0f}px;width:{widths[j]}px;text-align:center;font-family:{MONO if mono_ else SANS};font-size:{size}px;font-weight:{500};line-height:1.3;color:{GRAY if dim else INK};white-space:nowrap;{st}", e(str(v)), f' id="{tid}-r{i}c{j}"'))
                if tw(str(v), size, mono=bool(mono_)) > widths[j] - 10:
                    WARN.append(f"{tid}: cell r{i}c{j} '{v}' is wider than its column")
        line_ = f'<div style="position:absolute;left:0;top:0;width:{W_ - 4}px;height:2px;background:#E7E3DA"></div>' if (i or head) else ""
        o.append(f'<div id="{tid}-r{i}"{row_attrs.get(i, "")} style="position:absolute;left:2px;top:{ry}px;width:{W_ - 4}px;height:{rh}px">{line_}' + "".join(cells).replace(f"left:{xs[0]}px", f"left:{xs[0] - 2}px", 0) + '</div>')
    o.append('</div>')
    g = {"x": x, "y": y, "w": W_, "rh": rh, "y0": y + ny + 2 + hh, "xs": [x + 2 + s for s in xs], "widths": widths,
         "h": ny + hh + rh * len(rows) + 4, "n": len(rows)}
    if x + W_ > 1830:
        WARN.append(f"{tid}: table right edge {x + W_}")
    if y + g["h"] > 1040:
        WARN.append(f"{tid}: table bottom {y + g['h']:.0f}")
    return "".join(o), g


def ry_(g, i):
    """vertical centre of row i of an mtable"""
    return g["y0"] + i * g["rh"] + g["rh"] / 2


def curve(x1, y1, x2, y2, color, order=None, width=4, dash=None, pid=None, kind="draw", dot1=True, dot2=True, attrs=""):
    """a soft S curve from (x1, y1) to (x2, y2) with dots at both ends"""
    mx = (x1 + x2) / 2
    da = f' stroke-dasharray="{dash}"' if dash else ""
    pa = f' id="{pid}"' if pid else ""
    d = f"M{x1:.0f},{y1:.0f} C{mx:.0f},{y1:.0f} {mx:.0f},{y2:.0f} {x2:.0f},{y2:.0f}"
    dots = (f'<circle cx="{x1:.0f}" cy="{y1:.0f}" r="7" fill="{color}"/>' if dot1 else "") + (f'<circle cx="{x2:.0f}" cy="{y2:.0f}" r="7" fill="{color}"/>' if dot2 else "")
    return (f'<svg{bi(kind, order)}{attrs} viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible">'
            f'<path{pa} d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round"{da}/>{dots}</svg>')


def badge(x, y, text, color, order=None, size=26, attrs="", anim="pop", bg=None):
    bg = bg or color
    fg = "#FFFFFF" if bg == color else color
    bd = "" if bg == color else f"border:2px solid {color};"
    return p(f"position:absolute;left:{x:.0f}px;top:{y:.0f}px;height:{size + 20}px;padding:0 16px;border-radius:{(size + 20) // 2}px;background:{bg};{bd}font-size:{size}px;font-weight:700;line-height:{size + 20 - (4 if bd else 0)}px;color:{fg};white-space:nowrap", text, bi(anim, order) + attrs)


def badge_w(text, size=26):
    return tw(re.sub(r"<[^>]+>", "", text), size, mono=False) + 36


def psql_table(lines):
    """parse a psql result (header, ----, rows, (n rows)) into header list and rows (empty cell -> None)"""
    i = next(n for n, l in enumerate(lines) if re.match(r"^-+(\+-+)*$", l.strip()))
    head = [c.strip() for c in lines[i - 1].split("|")]
    rows = []
    for l in lines[i + 1:]:
        if re.match(r"^\(\d+ rows?\)$", l.strip()) or not l.strip():
            break
        rows.append([c.strip() or None for c in l.split("|")])
    return head, rows


# =====================================================================
# cover
# =====================================================================
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px">',
       p("position:absolute;left:128px;top:300px;font-size:28px;font-weight:700;color:#9DC1E6", "KANT AX/AI 엔지니어 트랙 · 40"),
       f'<h1{SLAM(1)} style="position:absolute;left:128px;top:350px;padding-bottom:14px;font-size:100px;font-weight:900;line-height:1.3;color:#F6F5F1">SQL 5</h1>',
       p("position:absolute;left:128px;top:500px;font-size:52px;font-weight:700;line-height:1.3;color:#F6F5F1", "UNION으로 쌓고<br>JOIN으로 붙이기"),
       p("position:absolute;left:128px;top:680px;font-size:30px;line-height:1.5;color:#BFC6D4", "PostgreSQL · UNION ALL, UNION,<br>JOIN, LEFT JOIN, FULL JOIN")]
cl = P("j-basic")
t = term_q(cl, 960, 360, size=19, w=864, tid="cov-term", lh=1.5)
cov.append(t.html())
cov.append(shine(2, "cov-term"))
W("cover", cov, "40 챕터는 SQL 5예요. 지금까지는 표 하나에서만 골라 봤어요. 오늘은 두 결과를 하나로 합쳐요. 결과를 위아래로 쌓는 UNION과, 두 표를 옆으로 붙이는 JOIN이에요. 오른쪽은 신청 표와 회원 표를 JOIN으로 붙여서 회원 번호 옆에 이름이 나온 화면이에요. 예제는 수업에서 쓴 체육 센터 표 다섯 개예요." + REAL, ("intro", "들어가기"))

ORDER.append("toc")   # written last, after page numbers are known

# =====================================================================
# why
# =====================================================================
o = frame("why", "들어가기", "신청 표에는 회원 번호만 있어서 이름을 보려면 한 번 더 물어봐야 해요", INK)
wl = [l for l in P("why") if l.strip()]
t = term_q(wl, 96, 214, size=22, w=1250, tid="t-why", lh=1.5)
i_h = at(wl, "enrollment_id |")
i_s2 = at(wl, "SELECT member_id, name")
mx = t.sx(i_h, "member_id")
mw = t.sw("member_id")
o.append(t.html())
o.append(obox(1, mx - 12, t.top(i_h) - 4, mw + 24, t.top(i_h + 6) - t.top(i_h) + 8, TE))
names_i = at(wl, "  3 | 박도현")
o.append(obox(2, t.x + 14, t.top(names_i) - 4, t.sw("        30 | 노채원") + 30, 4 * t.lp + 8, TM))
RX = t.x + t.w + 56
o.append(hd(RX, t.top(i_h) - 10, "3, 24, 14, 30번이 누구지?", TE, 30, 1))
o.append(note(RX, t.top(i_h) + 42, 1824 - RX, "enrollments 표에는 회원 번호만 있어요.", SUB, 26, 1))
o.append(hd(RX, t.top(names_i) - 10, "members 표에 또 물어봐요", TM, 30, 2))
o.append(note(RX, t.top(names_i) + 42, 1824 - RX, "번호를 손으로 옮겨 적었어요. 신청이 100건이면 못 해요.", SUB, 26, 2))

W("why", o, "신청 표에는 회원 번호만 있어서 이름을 보려면 한 번 더 물어봐야 해요. 11월 헬스 PT 입문을 신청한 사람을 enrollments 표에서 찾으면 member_id 3, 24, 14, 30이 나와요. 이 사람들이 누군지 알려면 members 표에서 번호를 다시 찾아야 해요. 아래처럼 번호를 손으로 IN 괄호에 옮겨 적었어요. 네 명이니까 할 만하지만 신청이 백 건이면 못 해요. 오늘은 이렇게 두 번 묻던 것을 한 문장으로 해요. 두 표를 옆으로 이어 붙이는 게 JOIN, 결과 두 개를 위아래로 모으는 게 UNION이에요." + REAL)

# =====================================================================
# big picture
# =====================================================================
o = frame("big", "들어가기", "UNION은 줄을 위아래로 쌓고, JOIN은 열을 옆으로 붙여요", INK)
# left: UNION
o.append(hd(96, 214, "UNION · 위아래로 쌓기", C1, 34))
o.append(note(96, 266, 760, "모양(열)이 같은 결과 두 개를 이어요. 줄이 늘어나요.", SUB, 26))
ta, ga = mtable(96, 360, "9월 신청", C1, ["member_id"], [["27"], ["17"]], [220], "bg-a", size=26, rh=52)
tb, gb = mtable(96, 600, "10월 신청", C1, ["member_id"], [["11"], ["19"], ["35"]], [220], "bg-b", size=26, rh=52)
o += [ta, tb]
UX = 520
o.append(tname(UX, 360, "합친 결과", C1, size=24, h=44))
o.append(f'<div style="position:absolute;left:{UX}px;top:404px;width:220px;height:{52 + 5 * 52 + 4}px;background:{CARD};border:2px solid {C1};border-radius:0 12px 12px 12px"></div>')
o.append(f'<div style="position:absolute;left:{UX + 2}px;top:406px;width:216px;height:52px;background:{C1}14"></div>')
o.append(p(f"position:absolute;left:{UX}px;top:415px;width:220px;text-align:center;font-family:{MONO};font-size:23px;font-weight:700;color:{C1}", "member_id"))
for k, v in enumerate(["27", "17", "11", "19", "35"]):
    src = f"bg-a-r{k}" if k < 2 else f"bg-b-r{k - 2}"
    o.append(f'<div data-build-in="fly order {1 if k < 2 else 2}" data-from="{src}" style="position:absolute;left:{UX + 2}px;top:{456 + k * 52}px;width:216px;height:52px">'
             + ('<div style="position:absolute;left:0;top:0;width:216px;height:2px;background:#E7E3DA"></div>')
             + p(f"position:absolute;left:0;top:10px;width:216px;text-align:center;font-family:{MONO};font-size:26px;color:{INK}", v) + '</div>')
o.append(badge(UX, 456 + 5 * 52 + 30, "2줄 + 3줄 = 5줄", C1, 2, size=24))
# divider
o.append(f'<div style="position:absolute;left:900px;top:220px;width:2px;height:720px;background:{LINE}"></div>')
# right: JOIN
JX = 960
o.append(hd(JX, 214, "JOIN · 옆으로 붙이기", C2, 34))
o.append(note(JX, 266, 860, "두 표에서 번호가 같은 줄끼리 짝지어요. 열이 늘어나요.", SUB, 26))
te_, ge = mtable(JX, 360, "enrollments", TE, ["member_id", "course_id"], [["3", "6"], ["14", "6"]], [170, 160], "bg-e", size=24, rh=52)
tm_, gm = mtable(JX + 470, 360, "members", TM, ["member_id", "name"], [["3", "박도현"], ["14", "신유찬"], ["24", "양다인"]], [170, 160], "bg-m", size=24, rh=52)
o += [te_, tm_]
for k, mi in enumerate([0, 1]):
    o.append(curve(JX + 330, ry_(ge, k), JX + 470, ry_(gm, mi), C2, 1 + 0, width=4))
jt, gj = mtable(JX, 680, "합친 결과", C2, ["member_id", "course_id", "name"], [["3", "6", "박도현"], ["14", "6", "신유찬"]], [170, 160, 160], "bg-j", size=24, rh=52,
                attrs=bi("rise", 2))
o.append(jt)
o.append(f'<div{bi("fade", 2)} style="position:absolute;left:{JX + 330}px;top:{gj["y0"] - 52}px;width:160px;height:{52 * 3}px;background:{TM}12;border-radius:0 10px 10px 0"></div>')
o.append(badge(JX + 520, 690, "열 2개 + 열 1개", C2, 2, size=24))
o.append(caption("오늘의 순서도 이래요. 1파트에서 쌓고, 2파트와 3파트에서 붙여요.", 960, 3, size=28, color=SUB))
W("big", o, "UNION은 줄을 위아래로 쌓고, JOIN은 열을 옆으로 붙여요. 왼쪽은 UNION이에요. 9월 신청자 두 명과 10월 신청자 세 명, 모양이 같은 결과 두 개를 이어서 다섯 줄로 만들어요. 열은 그대로고 줄이 늘어나요. 오른쪽은 JOIN이에요. 신청 표와 회원 표에서 member_id가 같은 줄끼리 짝을 지어요. 짝지은 줄을 옆으로 붙이니 열이 늘어나서 이름 열이 생겨요. 24번 양다인은 신청 표에 짝이 없어서 결과에 안 나와요. 이 둘만 구별하면 오늘 내용의 절반이에요.")

# =====================================================================
# the class tables
# =====================================================================
o = frame("db", "들어가기", "수업에서 쓴 체육 센터 표 다섯 개는 번호 열로 이어져 있어요", INK)


def tcard(x, y, w, name, alias, color, bg, cols, count, cid, keys=()):
    lines = []
    for c_ in cols:
        k = c_ in keys
        lines.append(p(f"height:36px;font-family:{MONO};font-size:22px;line-height:36px;color:{color if k else SUB};font-weight:{700 if k else 500};white-space:nowrap", e(c_)))
    h = 58 + 36 * len(cols) + 20
    return (f'<div id="{cid}" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{CARD};border:3px solid {color};border-radius:16px;box-shadow:{SHADOW}">'
            f'<div style="position:absolute;left:0;top:0;width:{w - 6}px;height:52px;background:{bg};border-radius:13px 13px 0 0"></div>'
            + p(f"position:absolute;left:20px;top:8px;font-family:{MONO};font-size:26px;font-weight:700;color:{color};white-space:nowrap", e(name) + (f' <span style="color:{GRAY};font-weight:500">{alias}</span>' if alias else ""))
            + p(f"position:absolute;right:16px;top:12px;font-size:20px;font-weight:700;color:{color};white-space:nowrap", e(count))
            + f'<div style="position:absolute;left:20px;top:62px">' + "".join(lines) + '</div></div>'), h


cards = [("members", "m", TM, TMBG, ["member_id", "name", "region", "phone", "…"], "40명", 96, 300, ("member_id",)),
         ("enrollments", "e", TE, TEBG, ["enrollment_id", "member_id", "course_id", "enroll_month", "status", "pay_amount"], "187줄", 470, 240, ("member_id", "course_id")),
         ("courses", "c", TC, TCBG, ["course_id", "course_name", "sport_id", "instructor_id", "fee", "…"], "14개", 880, 240, ("course_id", "instructor_id")),
         ("instructors", "i", TI, TIBG, ["instructor_id", "name", "phone", "sport_id"], "8명", 1300, 300, ("instructor_id",))]
geo = {}
for name, al, col, bgc, cols, cnt, x, y, keys in cards:
    w_ = 330
    h_, hh_ = tcard(x, y, w_, name, al, col, bgc, cols, cnt, "db-" + name, keys)
    o.append(h_)
    geo[name] = (x, y, w_, hh_)
# key rows: y of a column line inside a card


def ky(name, col):
    x, y, w_, h_ = geo[name]
    cols = [c for c in cards if c[0] == name][0][4]
    return y + 62 + 36 * cols.index(col) + 18


ex, ey, ew, eh = geo["enrollments"]
mx_, my_, mw_, mh_ = geo["members"]
cx0, cy0, cw0, ch0 = geo["courses"]
ix, iy, iw, ih = geo["instructors"]
o.append(curve(ex + 4, ky("enrollments", "member_id"), mx_ + mw_ - 4, ky("members", "member_id"), TM, 1, width=4))
o.append(curve(ex + ew - 4, ky("enrollments", "course_id"), cx0 + 4, ky("courses", "course_id"), TC, 2, width=4))
o.append(curve(cx0 + cw0 - 4, ky("courses", "instructor_id"), ix + 4, ky("instructors", "instructor_id"), TI, 3, width=4))
o.append(p(f"position:absolute;left:1300px;top:{iy + ih + 24}px;width:524px;font-size:23px;line-height:1.5;color:{SUB}", "종목 표 sports(5개)도 있지만 오늘은 안 써요."))
# load commands
LY = 640
lt = ["$ " + C("cp"), "$ " + C("load")]
ll = [l for l in RA("load") if l.strip()]
lt += [ll[0]] + ["…"] + ll[-2:]
t = term_q(lt, 96, LY + 48, size=21, tid="t-load", lh=1.5)
o.append(hd(96, LY, "표가 없으면 처음 한 번만 넣어요 (38과 같아요)", GRAY, 26))
o.append(t.html())
NX = t.x + t.w + 60
o.append(hd(NX, LY + 60, "선 하나가 ON 한 줄이에요", C2, 28, 4))
o.append(mono(NX, LY + 112, "e.member_id = m.member_id", TM, 26, 4))
o.append(mono(NX, LY + 156, "e.course_id = c.course_id", TC, 26, 4))
o.append(mono(NX, LY + 200, "c.instructor_id = i.instructor_id", TI, 26, 4))
W("db", o, "수업에서 쓴 체육 센터 표 다섯 개는 번호 열로 이어져 있어요. 가운데 enrollments가 신청 표예요. 한 줄이 신청 한 건이고, 누가 신청했는지는 member_id, 무슨 강좌인지는 course_id로만 적혀 있어요. member_id는 members 표의 member_id를, course_id는 courses 표의 course_id를 가리켜요. 37에서 배운 외래 키예요. courses의 instructor_id는 instructors 표를 가리켜요. 오늘 JOIN은 이 선을 따라 표를 이어요. 표 이름 옆의 e, m, c, i는 오늘 쓸 짧은 별명이에요. 표가 없으면 오른쪽처럼 sports.sql을 컨테이너에 복사하고 psql -f로 실행해요. 35에서 배운 방법이에요. 처음에는 지울 표가 없다는 NOTICE가 나오고, 마지막에 INSERT 0 187까지 나오면 끝이에요." + REAL)

# =====================================================================
# smallest example
# =====================================================================
o = frame("min", "들어가기", "가장 짧은 UNION ALL과 JOIN을 한 번씩 쳐 봐요", INK)
ml = P("min")
i2 = at(ml, "SELECT c.course_name")
t1 = term_q([l for l in ml[:i2] if l.strip()], 96, 214, size=22, w=1000, tid="t-min1", lh=1.5)
t2 = term_q(ml[i2:], 96, t1.y + t1.h + 30, size=22, w=1000, tid="t-min2", lh=1.5)
o += [t1.html(), t2.html()]
o.append(hbox(t1, 1, "UNION ALL", C1, 1, which="box"))
r1 = at(ml, " 정민재")
o.append(f'<div{bi("fade", 1)} style="position:absolute;left:{t1.x + 16:.0f}px;top:{t1.top(r1) - 2:.0f}px;width:{t1.sw(" 정민재") + 30:.0f}px;height:{2 * t1.lp + 4:.0f}px;border:3px solid {C1};border-radius:10px"></div>')
o.append(hbox(t2, 2, "JOIN instructors i ON c.instructor_id = i.instructor_id", C2, 2, which="ul"))
r2 = at(ml[i2:], "테니스 입문 |")
o.append(f'<div{bi("fade", 2)} style="position:absolute;left:{t2.x + 16:.0f}px;top:{t2.top(r2) - 2:.0f}px;width:{t2.sw(" 테니스 입문 | 정민재") + 24:.0f}px;height:{t2.lp + 4:.0f}px;border:3px solid {C2};border-radius:10px"></div>')
RX = 1150
o.append(hd(RX, t1.y + 40, "UNION ALL · 쌓기", C1, 32, 1))
o.append(note(RX, t1.y + 96, 1824 - RX, "강사 이름 아래에 회원 이름을 이어 붙였어요. 정민재는 강사, 김민준은 회원이에요.", INK, 27, 1))
o.append(hd(RX, t2.y + 40, "JOIN · 붙이기", C2, 32, 2))
o.append(note(RX, t2.y + 96, 1824 - RX, "강좌 표의 instructor_id로 강사 표를 찾아서 같은 줄에 강사 이름을 붙였어요.", INK, 27, 2))
W("min", o, "가장 짧은 UNION ALL과 JOIN을 한 번씩 쳐 봐요. 왼쪽은 강사 5번의 이름과 회원 1번의 이름을 따로 SELECT하고 가운데에 UNION ALL을 적었어요. 결과는 한 열짜리 표 하나로 나오고, 첫 줄이 강사 정민재, 둘째 줄이 회원 김민준이에요. 오른쪽은 테니스 입문 강좌를 찾으면서 JOIN으로 강사 표를 붙였어요. 강좌 표에는 강사 번호만 있는데, 결과에는 강사 이름 정민재가 같은 줄에 나와요. 처음 보는 c와 i, ON은 2파트에서 하나씩 봐요." + REAL)
# =====================================================================
# part 1: UNION
# =====================================================================
o = frame("u-all", EB1, "UNION ALL은 두 SELECT의 결과를 위아래로 이어 붙여요", C1)
ua = P("u-all")
qa = [PROMPT_RE.match(l).group(3) for l in ua if PROMPT_RE.match(l)]
ch, gc = code(qa, 96, 214, 800, size=24, cid="ua-code")
o.append(ch)
o.append(cbox(gc, 3, "UNION ALL", C1, 1))
_, s9 = psql_table(body(P("u-sep", 0)))
_, s10 = psql_table(body(P("u-sep", 1)))
_, ra = psql_table(body(ua))
SY = gc["y"] + gc["h"] + 40
t9, g9 = mtable(96, SY, "9월", C1, ["member_id"], s9, [200], "ua-9", size=26, rh=50)
t10, g10 = mtable(340, SY, "10월", C1, ["member_id"], s10, [200], "ua-10", size=26, rh=50)
o += [t9, t10]
o.append(note(580, SY + 60, 316, "SELECT를 하나씩 치면 결과도 따로따로 나와요.", SUB, 25))
RX0 = 1060
rows_attr = {}
for k in range(len(ra)):
    src = f"ua-9-r{k}" if k < len(s9) else f"ua-10-r{k - len(s9)}"
    rows_attr[k] = f' data-build-in="fly order {2 if k < len(s9) else 3}" data-from="{src}"'
tr, gr_ = mtable(RX0, 214, "UNION ALL 결과", C1, ["member_id"], ra, [280], "ua-res", size=28, rh=58, row_attrs=rows_attr)
o.append(tr)
dups = [k for k, r in enumerate(ra) if r[0] == "17"]
for k in dups:
    o.append(pen_box(4, RX0 + 60, round(gr_["y0"] + k * 58 + 6), 160, 46, RED, width=4))
o.append(badge(RX0 + 320, round(ry_(gr_, 1)) - 23, "9월 2줄", C1, 2, size=24))
o.append(badge(RX0 + 320, round(ry_(gr_, 4)) - 23, "10월 5줄", C1, 3, size=24))
o.append(hd(RX0 + 320, round(ry_(gr_, dups[1])) + 40, "17번이 두 번 나와요", RED, 28, 4))
o.append(note(RX0 + 320, round(ry_(gr_, dups[1])) + 84, 440, "두 달 모두 신청했으니 맞는 결과예요. 실제 화면 끝 줄은 (7 rows)예요.", SUB, 25, 4))
W("u-all", o, "UNION ALL은 두 SELECT의 결과를 위아래로 이어 붙여요. 수영 고급반, course_id 4번의 9월 신청자와 10월 신청자를 따로 SELECT하면 결과도 두 개로 따로 나와요. 두 SELECT 사이에 UNION ALL을 적으면 9월 결과 아래에 10월 결과가 붙어서 표 하나가 돼요. 2줄 더하기 5줄, 7줄이에요. 17번은 9월에도 10월에도 신청해서 두 번 나와요. UNION ALL은 겹쳐도 지우지 않고 다 붙여요. 문장 끝 세미콜론은 맨 마지막 SELECT 뒤에 한 번만 적어요. 결과 줄 순서는 컴퓨터마다 다를 수 있어요." + REAL, ("p1", "위아래로 쌓기"))

# ---- three months: UNION ALL then UNION (magic)
for sid, sc, op in (("u-all3", "u-all3", "UNION ALL"), ("u-union", "u-union", "UNION")):
    o = frame(sid, EB1, "UNION ALL은 겹친 줄도 다 남기고" if sid == "u-all3" else "UNION은 겹친 줄을 하나만 남겨요", C1, transition="magic")
    if sid == "u-all3":
        o[-1] = o[-1].replace("UNION ALL은 겹친 줄도 다 남기고", "세 달을 이으면 UNION ALL은 겹친 번호까지 다 남겨요")
    ul = P(sc)
    q3 = [PROMPT_RE.match(l).group(3) for l in ul if PROMPT_RE.match(l)]
    ch, gc = code(q3, 96, 214, 860, size=25, cid="u3-code", lh=1.5)
    o.append(ch)
    for i_, l_ in enumerate(q3):
        if l_.startswith("UNION"):
            o.append(cbox(gc, i_, l_, C1, 1 if sid == "u-union" else None) if sid == "u-union" else "")
    _, r3 = psql_table(body(ul))
    seen = {}
    CX0, CY0, CH = 1060, 214, 52
    o.append(p(f"position:absolute;left:{CX0}px;top:{CY0}px;width:200px;text-align:center;font-family:{MONO};font-size:24px;font-weight:700;color:{C1}", "member_id"))
    for k, r in enumerate(r3):
        v = r[0]
        seen[v] = seen.get(v, 0) + 1
        cid_ = f"u3-{v}-{seen[v]}"
        dup = seen[v] > 1
        y = CY0 + 46 + k * CH
        o.append(p(f"position:absolute;left:{CX0}px;top:{y}px;width:200px;height:{CH - 10}px;border-radius:12px;background:{RED + '1A' if dup else CARD};border:2px solid {RED if dup else C1};text-align:center;font-family:{MONO};font-size:28px;font-weight:700;line-height:{CH - 14}px;color:{RED if dup else INK}", v, f' id="{cid_}"'))
    n = len(r3)
    yb = CY0 + 46 + n * CH
    PY_ = gc["y"] + gc["h"] + 40
    if sid == "u-all3":
        o.append(hd(96, PY_, "13의 리스트 더하기와 같아요", GRAY, 24))
        pyl = ["[27, 17] + [11, 19, 35, 17, 20]", "# [27, 17, 11, 19, 35, 17, 20]"]
    else:
        o.append(hd(96, PY_, "16의 집합 합집합과 같아요", GRAY, 24))
        pyl = ["{27, 17} | {11, 19, 35, 17, 20}", "# 17은 한 번만 남아요"]
    pc, _ = code(pyl, 96, PY_ + 42, 860, size=24, cid="u3-py", raw={0: e(pyl[0]), 1: f'<span style="color:{GRAY}">{e(pyl[1])}</span>'}, lh=1.45)
    o.append(pc)
    o.append(badge(CX0, yb + 6, f"({n} rows)", C1, None, size=24, attrs=' id="u3-count"'))
    TX_ = CX0 + 260
    if sid == "u-all3":
        o.append(hd(TX_, 300, "11번과 17번이 두 번씩", RED, 30, 1))
        o.append(note(TX_, 350, 1824 - TX_, "11번은 10월과 11월, 17번은 9월과 10월에 신청했어요.", SUB, 26, 1))
        o.append(hd(TX_, 560, "ORDER BY는 맨 끝에 한 번", C1, 30, 2))
        o.append(note(TX_, 610, 1824 - TX_, "세 결과를 다 합친 다음에 번호 순으로 세워요.", SUB, 26, 2))
        o.append(cbox(gc, len(q3) - 1, "ORDER BY member_id", C1, 2))
    else:
        o.append(hd(TX_, 300, "겹친 번호 두 개가 빠져요", C1, 30, 2))
        o.append(note(TX_, 350, 1824 - TX_, "12줄에서 10줄이 됐어요. 한 번이라도 신청한 회원 명단이에요.", SUB, 26, 2))
        o.append(hd(TX_, 560, "36의 DISTINCT와 같은 일", GRAY, 28, 3))
        o.append(note(TX_, 610, 1824 - TX_, "합친 다음 겹치는 줄을 하나만 남겨요. 겹칠 일이 없으면 UNION ALL이 더 빨라요.", SUB, 26, 3))
    notes = ("세 달을 이으면 UNION ALL은 겹친 번호까지 다 남겨요. 이번에는 수업 코드 그대로 9월, 10월, 11월 세 SELECT를 UNION ALL로 이었어요. 마지막 줄의 ORDER BY는 세 결과를 다 합친 다음에 번호 순으로 세워요. 12줄 중 빨간 칸이 두 번째로 나온 번호예요. 11번은 10월과 11월, 17번은 9월과 10월에 신청해서 두 번씩 나와요. 신청 건수를 세려면 이게 맞아요."
             if sid == "u-all3" else
             "UNION은 겹친 줄을 하나만 남겨요. 같은 문장에서 ALL만 뺐어요. 결과가 12줄에서 10줄이 됐어요. 두 번 나오던 11번과 17번이 한 번씩만 남았어요. 세 달 동안 수영 고급반을 한 번이라도 신청한 회원 명단이 필요하면 UNION, 신청 건수가 필요하면 UNION ALL이에요. 36에서 배운 DISTINCT처럼 합친 다음에 겹치는 줄을 지워요. 겹칠 일이 없는 결과라면 지우는 일을 안 하는 UNION ALL이 더 빨라요.")
    W(sid, o, notes + REAL)

# ---- a label column
o = frame("u-label", EB1, "표에 없는 글자를 SELECT에 적으면 어느 쪽 줄인지 구분할 수 있어요", C1)
ll_ = P("u-label")
t = term_q(ll_, 96, 214, size=20, w=1060, tid="t-label", lh=1.45)
i_h = at(ll_, " 구분 |")
i_ins = [k for k, l in enumerate(ll_) if l.startswith(" 강사 |")]
i_mem = [k for k, l in enumerate(ll_) if l.startswith(" 회원 |")]
t.band(i_ins[0], i_ins[-1], order=1, color="rgba(227,168,74,.20)")
t.band(i_mem[0], i_mem[-1], order=2, color="rgba(111,155,245,.16)")
o.append(t.html())
o.append(hbox(t, 0, "'강사' AS 구분", TI, 1, which="box"))
o.append(hbox(t, 4, "'회원' AS 구분", TM, 2, which="box"))
i_null = at(ll_, "허윤아")
o += tag(t, i_null, "phone이 NULL이라 비어 보여요", NUL, 3, gap=max(t.end(k) for k in i_mem) - t.end(i_null) + 50)
RX = t.x + t.w + 50
o.append(hd(RX, 240, "강사 2명", TI, 30, 1))
o.append(note(RX, 290, 1824 - RX, "instructors에서 테니스(sport_id 4) 강사만 골랐어요.", SUB, 25, 1))
o.append(hd(RX, 480, "회원 12명", TM, 30, 2))
o.append(note(RX, 530, 1824 - RX, "members에서 영등포구 회원만 골랐어요. 표가 달라도 열 세 개의 모양이 같아서 이어져요.", SUB, 25, 2))
o.append(note(RX, 760, 1824 - RX, "'강사' AS 구분은 모든 줄에 같은 글자를 붙이고, 그 열 이름을 구분으로 정해요.", INK, 25, 3))
W("u-label", o, "표에 없는 글자를 SELECT에 적으면 어느 쪽 줄인지 구분할 수 있어요. 테니스 강사와 영등포구 회원에게 같은 안내 문자를 보낸다고 해 봐요. 두 표에서 이름과 전화번호를 UNION ALL로 이으면 한 목록이 되는데, 누가 강사인지 알 수가 없어요. 그래서 SELECT 맨 앞에 작은따옴표로 강사라는 글자를 적고 AS 구분으로 열 이름을 붙였어요. 표에 없는 값도 이렇게 적으면 모든 줄에 같은 글자가 붙어요. 아래 SELECT에는 회원이라고 적었어요. 허윤아 회원은 전화번호가 NULL이라서 빈칸으로 보여요." + REAL)

# ---- the rules
o = frame("u-rule", EB1, "위아래로 붙이려면 열 개수와 자료형이 같아야 해요", C1)
rl = [l for l in P("u-rule", 0, 1) if l.strip()]
t = term_q(rl, 96, 214, size=20, w=1080, tid="t-rule", lh=1.42)
o.append(t.html())
o.append(hbox(t, at(rl, "each UNION query"), "each UNION query must have the same number of columns", RED, 1))
o.append(hbox(t, at(rl, "UNION types"), "UNION types character varying and integer cannot be matched", RED, 2))
nl_ = P("u-rule", 2)
nl_ = nl_[:at(nl_, " 한지우") + 1] + ["…"] + nl_[at(nl_, "(5 rows)"):]
t3 = term_q(nl_, 96, t.y + t.h + 24, size=20, w=1080, tid="t-rule3", lh=1.42)
o.append(t3.html())
o.append(hbox(t3, 0, "AS 이름", C1, 3, which="box"))
o.append(hbox(t3, at(nl_, "이름") if at(nl_, "이름") > 0 else 3, "이름", C1, 3, which="box"))
RX = 1240


def slots(x, y, labels, color, bad=None):
    o_, cx = [], x
    for k, lab in enumerate(labels):
        w = tw(lab, 22) + 30
        c_ = RED if bad == k else color
        o_.append(p(f"position:absolute;left:{cx:.0f}px;top:{y}px;height:44px;padding:0 14px;border-radius:9px;background:{c_}14;border:2px solid {c_};font-family:{MONO};font-size:22px;font-weight:700;line-height:40px;color:{c_};white-space:nowrap", e(lab)))
        cx += w + 10
    return o_


o.append(hd(RX, 230, "① 열 개수", RED, 28, 1))
o += [x for x in slots(RX, 280, ["name", "phone"], TI)]
o += [x for x in slots(RX, 334, ["name"], TM)]
o.append(p(f"position:absolute;left:{RX + tw('name', 22) + 40:.0f}px;top:334px;width:{tw('phone', 22) + 32:.0f}px;height:44px;border:3px dashed {RED};border-radius:9px", "", bi("fade", 1)))
o.append(hd(RX, 440, "② 같은 자리의 자료형", RED, 28, 2))
o += slots(RX, 490, ["name  VARCHAR"], TI)
o += slots(RX, 544, ["birth_year  INTEGER"], TM, bad=0)
o.append(hd(RX, 660, "③ 열 이름은 첫 SELECT 것", C1, 28, 3))
o.append(note(RX, 708, 1824 - RX, "아래 SELECT의 course_name은 이름 열 아래로 들어가요.", SUB, 25, 3))
W("u-rule", o, "위아래로 붙이려면 열 개수와 자료형이 같아야 해요. 첫 번째는 위 SELECT가 열 두 개, 아래 SELECT가 열 한 개라서 each UNION query must have the same number of columns, 열 개수가 같아야 한다는 오류가 나요. 두 번째는 개수는 하나씩 같지만 위는 글자, 아래는 정수예요. 같은 자리에 놓일 값의 자료형이 달라서 맞출 수 없다는 오류예요. 열 이름은 같지 않아도 돼요. 세 번째처럼 결과의 열 이름은 첫 SELECT를 따라요. 강사 이름 아래로 강좌 이름이 이름이라는 열 하나에 들어갔어요." + REAL)

# ---- ORDER BY at the end
o = frame("u-order", EB1, "ORDER BY는 마지막 SELECT 뒤에 한 번만 적어요", C1)
ol = P("u-order")
t = term_q(ol, 96, 214, size=24, w=1100, tid="t-order", lh=1.55)
o.append(t.html())
o.append(hbox(t, 1, "ORDER BY name", RED, 1, which="box"))
o.append(hbox(t, at(ol, 'syntax error at or near "UNION"'), 'syntax error at or near "UNION"', RED, 1))
i_fix = at(ol, "ORDER BY name;")
o.append(hbox(t, i_fix, "ORDER BY name", GR, 2, which="box"))
RX = t.x + t.w + 56
BX = [("SELECT …", C1), ("UNION ALL", GRAY), ("SELECT …", C1)]
for k, (lab, col) in enumerate(BX):
    o.append(p(f"position:absolute;left:{RX + 30}px;top:{300 + k * 74}px;width:380px;height:60px;border-radius:12px;background:{CARD};border:2px solid {col};font-family:{MONO};font-size:26px;font-weight:700;line-height:56px;padding-left:22px;color:{col}", e(lab), bi("rise", 2)))
o.append(f'<div{bi("fade", 2)} style="position:absolute;left:{RX}px;top:290px;width:16px;height:{3 * 74 - 4}px;border:4px solid {GR};border-right:none;border-radius:12px 0 0 12px"></div>')
o.append(p(f"position:absolute;left:{RX + 30}px;top:{300 + 3 * 74 + 10}px;width:380px;height:60px;border-radius:12px;background:{GR};font-family:{MONO};font-size:26px;font-weight:700;line-height:60px;padding-left:22px;color:#FFFFFF", "ORDER BY name", bi("rise", 2)))
o.append(p(f"position:absolute;left:{RX - 4}px;top:254px;font-size:22px;font-weight:700;color:{GR}", "합친 결과", bi("fade", 2)))
o.append(note(RX, 640, 1824 - RX, "합친 결과 전체를 한 번에 세워요. 김민준이 강사 두 명 앞으로 왔어요.", INK, 26, 2))
W("u-order", o, "ORDER BY는 마지막 SELECT 뒤에 한 번만 적어요. 첫 번째처럼 위 SELECT 안에 ORDER BY를 넣으면 UNION 근처에서 문법 오류가 나요. PostgreSQL은 ORDER BY가 나오면 문장이 끝나 간다고 읽는데, 그 뒤에 UNION이 와서 헷갈린 거예요. 두 번째처럼 맨 끝에 적으면 세 사람을 합친 다음 이름 순으로 세워요. 회원 김민준이 강사 정민재, 한지우 앞에 왔어요. 위아래 결과를 따로 세우는 게 아니라 합친 결과 전체를 세운다는 점을 기억해요." + REAL)

# =====================================================================
# part 2: alias and JOIN
# =====================================================================
o = frame("j-alias", EB2, "FROM 표 이름 뒤에 짧은 별명을 붙이면 열 앞에 별명만 적어요", C2)
jl = [PROMPT_RE.match(l).group(3) for l in P("j-long") if PROMPT_RE.match(l)]
js = [PROMPT_RE.match(l).group(3) for l in P("j-basic") if PROMPT_RE.match(l)]
o.append(hd(96, 206, "별명 없이", GRAY, 26))
ch1, g1 = code(jl, 96, 256, 1220, size=25, cid="al-long")
o.append(ch1)
for i_, l_ in enumerate(jl):
    for name_, col_ in (("enrollments.", TE), ("members.", TM)):
        st = 0
        while l_.find(name_, st) >= 0:
            k_ = l_.find(name_, st)
            x_ = g1["tx"] + tw(l_[:k_], 25)
            o.append(f'<svg{bi("fade", 1)} style="position:absolute;left:{x_:.0f}px;top:{cline_y(g1, i_) + 4:.0f}px;width:{tw(name_[:-1], 25):.0f}px;height:{g1["lp"] - 8}px"><rect width="100%" height="100%" rx="6" fill="{col_}" fill-opacity=".14"/></svg>')
            st = k_ + 1
Y2 = g1["y"] + g1["h"] + 90
o.append(hd(96, Y2 - 42, "별명 e, m", C2, 26, 2))
ch2, g2 = code(js, 96, Y2, 1220, size=25, cid="al-short", attrs=bi("rise", 2))
o.append(ch2)
for i_, l_ in enumerate(js):
    for a_, col_ in (("e.", TE), ("m.", TM)):
        st = 0
        while l_.find(a_, st) >= 0:
            k_ = l_.find(a_, st)
            if k_ == 0 or not l_[k_ - 1].isalnum():
                x_ = g2["tx"] + tw(l_[:k_], 25)
                o.append(f'<svg{bi("fade", 2)} style="position:absolute;left:{x_ - 2:.0f}px;top:{cline_y(g2, i_) + 4:.0f}px;width:{tw("e", 25) + 4:.0f}px;height:{g2["lp"] - 8}px"><rect width="100%" height="100%" rx="6" fill="{col_}" fill-opacity=".2"/></svg>')
            st = k_ + 1
o.append(cbox(g2, 1, "enrollments e", TE, 3))
o.append(cbox(g2, 2, "members m", TM, 3))
LY = g2["y"] + g2["h"] + 40
o.append(badge(96, LY, "e = enrollments", TE, 3, size=26))
o.append(badge(96 + badge_w("e = enrollments", 26) + 16, LY, "m = members", TM, 3, size=26))
o.append(note(96, LY + 74, 1200, "enrollments AS e처럼 AS를 넣어도 같아요. 별명은 이 문장 안에서만 써요.", SUB, 24, 3))
rl_ = body(P("j-basic"))
t = term_q(rl_, 1360, 256, size=20, w=464, tid="t-alias", lh=1.5)
o.append(hd(1360, 206, "두 문장의 결과가 같아요", GRAY, 26))
o.append(t.html())
W("j-alias", o, "FROM 표 이름 뒤에 짧은 별명을 붙이면 열 앞에 별명만 적어요. JOIN을 쓰면 두 표에 같은 이름의 열이 생겨요. member_id가 enrollments에도 있고 members에도 있어요. 그래서 어느 표의 열인지 표 이름과 점을 앞에 붙여요. 위처럼 매번 enrollments 점, members 점을 적으면 문장이 길어져요. FROM enrollments 뒤에 e, JOIN members 뒤에 m을 적으면 그 문장 안에서는 e 점, m 점으로 줄여 써요. 수업 코드도 이렇게 썼어요. AS를 넣어 enrollments AS e라고 써도 같아요. 두 문장을 실제로 실행하면 결과가 똑같이 네 줄이에요." + REAL, ("p2", "옆으로 붙이기"))

# ---- the JOIN line taken apart
o = frame("j-on", EB2, "JOIN 뒤에는 붙일 표를, ON 뒤에는 짝을 맞출 조건을 적어요", C2)
o += parts(150, 226, [("JOIN", PG, "붙일 표 앞에", None), ("members m", TM, "붙일 표와 별명", None), ("ON", PG, "짝 맞출 조건", None),
                      ("e.member_id", TE, "신청 표의<br>회원 번호", None), ("=", INK, None, None), ("m.member_id", TM, "회원 표의<br>회원 번호", None)],
          size=50, order=1, lab=26, drop=36, stagger=True, lw=300)
o.append(note(150, 476, 1620, "두 값이 같은 줄끼리 짝을 지어요. 37에서 enrollments.member_id가 members.member_id를 가리키게 만든 외래 키 선과 같아요.", INK, 28, 5))
bj = P("j-basic")
t = term_q(bj, 96, 572, size=20, w=1100, tid="t-on", lh=1.45)
o.append(t.html())
o.append(hbox(t, 2, "JOIN members m ON e.member_id = m.member_id", C2, 6, which="ul"))
RX = t.x + t.w + 50
o.append(hd(RX, 620, "FROM은 하나, JOIN은 여러 번", C2, 28, 6))
o.append(note(RX, 668, 1824 - RX, "FROM에 먼저 적은 표에 JOIN으로 다른 표를 붙여요. WHERE는 붙인 다음에 골라요.", SUB, 25, 6))
W("j-on", o, "JOIN 뒤에는 붙일 표를, ON 뒤에는 짝을 맞출 조건을 적어요. 한 줄을 조각내 봤어요. JOIN 다음에 붙일 표 members와 별명 m을 적어요. ON 다음에는 어떤 줄끼리 짝지을지 조건을 적어요. 신청 표의 member_id와 회원 표의 member_id가 같은 줄끼리예요. 37에서 외래 키로 이어 둔 그 선이에요. 아래가 실제로 친 문장이에요. FROM에 신청 표, JOIN으로 회원 표를 붙이고, 붙인 다음에 WHERE로 11월 헬스 PT 입문만 골랐어요." + REAL)

# ---- pairing rows, animated
o = frame("j-anim", EB2, "JOIN은 member_id가 같은 줄을 찾아서 옆에 붙여요", C2)
_, ej = psql_table(body(P("why", 0)))
erow = [[r[0], r[1], r[2]] for r in ej]          # enrollment_id, member_id, course_id
mids = [r[1] for r in erow]
mshow = [["1", "김민준"], ["3", "박도현"], ["14", "신유찬"], ["24", "양다인"], ["29", "노채원"], ["30", "노채원"]]
mshow = [["1", "김민준"], ["2", "이서윤"], ["3", "박도현"], ["14", "신유찬"], ["24", "양다인"], ["30", "노채원"], ["…", "…"]]
_, mres = psql_table(body(P("j-basic")))
te_, ge = mtable(96, 230, "enrollments e", TE, ["enrollment_id", "member_id", "course_id"], erow, [190, 160, 150], "ja-e", size=24, rh=48)
tm_, gm = mtable(860, 230, "members m", TM, ["member_id", "name"], mshow, [160, 160], "ja-m", size=24, rh=48, dim_rows=(0, 1, 6))
o += [te_, tm_]
for k, mid in enumerate(mids):
    mi = [r[0] for r in mshow].index(mid)
    x1 = ge["xs"][1] + ge["widths"][1] / 2 + 34
    o.append(curve(ge["x"] + ge["w"] + 2, ry_(ge, k), gm["x"] - 2, ry_(gm, mi), C2, k + 1, width=4))
    o.append(f'<div{bi("fade", k + 1)} style="position:absolute;left:{ge["xs"][1] + 30:.0f}px;top:{ry_(ge, k) - 22:.0f}px;width:100px;height:44px;border:3px solid {C2};border-radius:10px"></div>')
    o.append(f'<div{bi("fade", k + 1)} style="position:absolute;left:{gm["xs"][0] + 30:.0f}px;top:{ry_(gm, mi) - 22:.0f}px;width:100px;height:44px;border:3px solid {C2};border-radius:10px"></div>')
RY = max(ge["y"] + ge["h"], gm["y"] + gm["h"]) + 40
ra_ = {k: f' data-build-in="fly order 5" data-from="ja-e-r{k}"' for k in range(len(mres))}
tr_, gr2 = mtable(96, RY, "결과", C2, ["member_id", "course_id", "name"], mres, [160, 150, 160], "ja-r", size=24, rh=46, row_attrs=ra_)
o.append(tr_)
o.append(f'<div{bi("fade", 5)} style="position:absolute;left:{gr2["xs"][2]:.0f}px;top:{gr2["y0"]:.0f}px;width:156px;height:{46 * len(mres)}px;background:{TM}14"></div>')
RX = 1300
o.append(hd(RX, 260, "줄마다 짝을 찾아요", C2, 30, 1))
o.append(note(RX, 310, 1824 - RX, "신청 한 줄의 member_id를 들고 회원 표에서 같은 번호를 찾아요.", SUB, 25, 1))
o.append(hd(RX, RY + 30, "찾은 짝을 옆에 붙여요", C2, 30, 5))
o.append(note(RX, RY + 80, 1824 - RX, "이름 열이 하나 늘었어요. 짝이 없는 1번, 2번 회원은 결과에 안 나와요.", SUB, 25, 5))
W("j-anim", o, "JOIN은 member_id가 같은 줄을 찾아서 옆에 붙여요. 왼쪽은 11월 헬스 PT 입문 신청 네 건이에요. 첫 줄의 member_id 3을 들고 오른쪽 회원 표에서 3번을 찾아 박도현과 짝을 지어요. 14번은 신유찬, 24번은 양다인, 30번은 노채원이에요. 짝을 다 찾으면 신청 줄 옆에 회원 이름을 붙여서 결과를 만들어요. 그래서 결과에 name 열이 하나 늘었어요. 회원 표의 1번, 2번처럼 이번 신청에 없는 회원은 결과에 나오지 않아요. 아래 결과는 앞 장의 실제 실행 결과와 같아요. 줄 순서는 컴퓨터마다 다를 수 있어요." + REAL)

# ---- one member, many enrollments
o = frame("j-many", EB2, "회원 한 명이 여러 번 신청했으면 그 회원 줄이 신청 수만큼 되풀이돼요", C2)
mm = P("j-many")
t = term_q(mm, 96, 214, size=22, w=1000, tid="t-many", lh=1.5)
o.append(t.html())
i0 = at(mm, " 한수아 |")
o.append(obox(2, t.x + 16, t.top(i0) - 2, t.sw(" 한수아 ") + 20, 8 * t.lp + 4, TM))
DX = 1180
_, mr = psql_table(body(mm))
tm1, g1 = mtable(DX, 420, "members", TM, ["id", "name"], [["11", "한수아"]], [90, 130], "jm-m", size=24, rh=54)
o.append(tm1)
te1, g2 = mtable(DX + 360, 214, "enrollments", TE, ["course", "month"], [[r[1], r[2]] for r in mr], [110, 150], "jm-e", size=22, rh=50)
o.append(te1)
for k in range(len(mr)):
    o.append(curve(g1["x"] + g1["w"] + 2, ry_(g1, 0), g2["x"] - 2, ry_(g2, k), TM, 1, width=3, dot1=(k == 0)))
o.append(hd(DX, g2["y"] + g2["h"] + 40, "1 줄 × 8 줄", TM, 30, 2))
o.append(note(DX, g2["y"] + g2["h"] + 86, 1824 - DX, "회원 표 한 줄이 신청 여덟 줄과 짝지어져요.", SUB, 25, 2))
W("j-many", o, "회원 한 명이 여러 번 신청했으면 그 회원 줄이 신청 수만큼 되풀이돼요. 11번 한수아 회원은 9월부터 11월까지 여덟 번 신청했어요. members 표에는 한수아가 한 줄뿐이지만 enrollments 표에는 member_id 11이 여덟 줄이에요. JOIN은 짝이 되는 줄을 모두 만들어서 결과에 한수아가 여덟 번 나와요. 틀린 게 아니라 신청 한 건이 결과 한 줄이에요. 결과 줄 수는 보통 여러 줄 쪽, 여기서는 신청 표를 따라가요." + REAL)

# ---- courses and instructors: one picture for JOIN, LEFT JOIN and FULL JOIN
_, CR = psql_table(body(P("l-left")))          # course_id, course_name, instructor name (None for 5)
INS = ["박서연", "이도윤", "김하준", "최유나", "정민재", "한지우", "오세린", "윤태호"]
DY0, DRH = 236, 47
CXL, CW_L = 96, 330
IXL, IW_L = 680, 170


def cip(mode, order_line=None):
    """the courses / instructors diagram. mode: inner, left, full"""
    o_ = []
    o_.append(hd(CXL, DY0 - 46, "courses c", TC, 26))
    o_.append(hd(IXL, DY0 - 46, "instructors i", TI, 26))
    iy = {n: DY0 + 20 + k * (DRH * 14 - 40) / 7 for k, n in enumerate(INS)}
    for k, (cid, cname, iname) in enumerate(CR):
        y = DY0 + k * DRH
        lone = iname is None
        col = RED if (lone and mode == "inner") else (TC if not lone else NUL)
        st = "dashed" if lone else "solid"
        o_.append(p(f"position:absolute;left:{CXL}px;top:{y}px;width:{CW_L}px;height:{DRH - 8}px;border-radius:10px;background:{CARD};border:2px {st} {col};font-size:22px;line-height:{DRH - 12}px;padding-left:14px;color:{INK if not (lone and mode == 'inner') else GRAY};white-space:nowrap",
                    f'<span style="font-family:{MONO};font-weight:700;color:{col}">{cid}</span>&#160; {e(cname)}', f' id="cd-c{cid}"'))
        if iname:
            o_.append(curve(CXL + CW_L + 4, y + (DRH - 8) / 2, IXL - 4, iy[iname] + (DRH - 8) / 2, TC, None, width=3, attrs=f' id="cd-l{cid}"'))
    for n in INS:
        lone = n == "윤태호"
        col = RED if (lone and mode in ("inner", "left")) else (NUL if lone else TI)
        st = "dashed" if lone else "solid"
        o_.append(p(f"position:absolute;left:{IXL}px;top:{iy[n]:.0f}px;width:{IW_L}px;height:{DRH - 8}px;border-radius:10px;background:{CARD};border:2px {st} {col};text-align:center;font-size:22px;line-height:{DRH - 12}px;color:{INK if not (lone and mode != 'full') else GRAY};white-space:nowrap", e(n), f' id="cd-i{n}"'))
    y5 = DY0 + 4 * DRH
    yT = iy["윤태호"]
    if mode == "inner":
        o_.append(p(f"position:absolute;left:{CXL + CW_L + 18}px;top:{y5 + 4}px;font-size:21px;font-weight:700;color:{RED};white-space:nowrap", "강사 없음", bi("rise", 1)))
        o_.append(p(f"position:absolute;left:{IXL - 4}px;top:{yT + DRH - 2:.0f}px;width:{IW_L + 8}px;text-align:center;font-size:21px;font-weight:700;color:{RED};white-space:nowrap", "강좌 없음", bi("rise", 1)))
    if mode in ("left", "full"):
        o_.append(curve(CXL + CW_L + 4, y5 + (DRH - 8) / 2, IXL - 110, y5 + (DRH - 8) / 2, NUL, None, width=3, dash="8 8", dot2=False))
        o_.append(p(f"position:absolute;left:{IXL - 104}px;top:{y5 + 2}px;width:90px;height:{DRH - 12}px;border-radius:8px;background:{NLBG};border:2px dashed {NUL};text-align:center;font-family:{MONO};font-size:19px;font-weight:700;line-height:{DRH - 16}px;color:{NUL}", "NULL", bi("pop", order_line) + ' id="cd-n5"'))
    if mode == "full":
        o_.append(p(f"position:absolute;left:{IXL - 104}px;top:{yT + 2:.0f}px;width:90px;height:{DRH - 12}px;border-radius:8px;background:{NLBG};border:2px dashed {NUL};text-align:center;font-family:{MONO};font-size:19px;font-weight:700;line-height:{DRH - 16}px;color:{NUL}", "NULL", bi("pop", order_line + 1) + ' id="cd-n8"'))
        o_.append(curve(IXL - 14, yT + (DRH - 8) / 2, IXL - 4, yT + (DRH - 8) / 2, NUL, None, width=3, dot1=False, dot2=False))
    return o_


TX0 = 920
o = frame("j-inner", EB2, "JOIN은 짝이 없는 줄을 결과에서 빼요", C2, transition="magic")
o += cip("inner")
ji = P("j-inner")
t = term_q(ji, TX0, 214, size=19, w=904, tid="t-cip", lh=1.42)
o.append(t.html())
i4 = at(ji, "         4 |")
o += tag(t, i4, "5번 아쿠아로빅이 없어요", RED, 2, gap=60)
o.append(hbox(t, at(ji, "(13 rows)"), "(13 rows)", RED, 3, which="box"))
o.append(note(TX0, t.y + t.h + 26, 904, "강좌 14개 중 13개만 나와요. 강좌가 없는 강사 윤태호도 안 나와요. JOIN은 INNER JOIN을 줄인 말이에요.", INK, 25, 3))
W("j-inner", o, "JOIN은 짝이 없는 줄을 결과에서 빼요. 왼쪽 그림은 강좌 14개와 강사 8명을 instructor_id로 이은 거예요. 박서연 강사는 수영 강좌 두 개를 맡아서 선이 두 개예요. 5번 아쿠아로빅은 instructor_id가 NULL이라 이을 강사가 없어요. 윤태호 강사는 아직 맡은 강좌가 없어요. JOIN 결과에는 선으로 이어진 13줄만 나와요. 오른쪽 결과에서 4번 다음이 바로 6번이에요. 수업에서 쓴 JOIN은 정식 이름이 INNER JOIN이에요. INNER를 빼고 JOIN만 써도 같아요." + REAL)

# ---- three tables
o = frame("j-3", EB2, "JOIN을 두 번 이어 쓰면 표 세 개를 한 줄로 붙여요", C2)
q3 = [PROMPT_RE.match(l).group(3) for l in P("j-3") if PROMPT_RE.match(l)]
ch, gc = code(q3, 96, 214, 1010, size=23, cid="j3-code")
o.append(ch)
o.append(cbox(gc, 2, "JOIN members m ON e.member_id = m.member_id", TM, 1))
o.append(cbox(gc, 3, "JOIN courses c ON e.course_id = c.course_id", TC, 2))
r3 = body(P("j-3"))
t = term_q(r3, 96, gc["y"] + gc["h"] + 30, size=21, w=1010, tid="t-j3", lh=1.45)
o.append(t.html())
DX = 1180
def mini(x, y, name, col, bgc, sub, mid):
    return (f'<div id="{mid}" style="position:absolute;left:{x}px;top:{y}px;width:300px;height:96px;background:{CARD};border:3px solid {col};border-radius:16px;box-shadow:{SHADOW}">'
            + p(f"position:absolute;left:20px;top:12px;font-family:{MONO};font-size:26px;font-weight:700;color:{col}", e(name))
            + p(f"position:absolute;left:20px;top:54px;font-family:{MONO};font-size:18px;color:{SUB};white-space:nowrap", e(sub)) + '</div>')
o.append(mini(DX + 170, 260, "enrollments e", TE, TEBG, "member_id · course_id", "j3-e"))
o.append(mini(DX, 520, "members m", TM, TMBG, "member_id · name", "j3-m"))
o.append(mini(DX + 340, 520, "courses c", TC, TCBG, "course_id · course_name", "j3-c"))
o.append(curve(DX + 260, 360, DX + 150, 516, TM, 1, width=4))
o.append(curve(DX + 380, 360, DX + 490, 516, TC, 2, width=4))
o.append(note(DX, 660, 1824 - DX, "e를 가운데 두고 m과 c를 하나씩 붙였어요.", INK, 25, 3))
o.append(hd(DX, 760, "결과 한 줄", GRAY, 26, 3))
_cx = DX
for _txt, _col in ((r3[2].split("|")[0].strip(), TM), (r3[2].split("|")[1].strip(), TC), (r3[2].split("|")[2].strip() + " · " + r3[2].split("|")[3].strip(), TE)):
    o.append(pill(_cx, 810, _txt, _col, 3, size=22))
    _cx += tw(_txt, 22, mono=False) + 44
o.append(note(DX, 880, 1824 - DX, "이름은 m, 강좌 이름은 c, 월과 상태는 e에서 왔어요.", SUB, 24, 3))
W("j-3", o, "JOIN을 두 번 이어 쓰면 표 세 개를 한 줄로 붙여요. 한수아 회원이 신청한 강좌 이름까지 보고 싶어요. 신청 표에는 회원 번호와 강좌 번호만 있으니 회원 표와 강좌 표를 둘 다 붙여야 해요. FROM enrollments e에 JOIN members를 붙이고, 그 결과에 JOIN courses를 한 번 더 붙여요. ON 조건은 표마다 따로 적어요. 회원은 member_id로, 강좌는 course_id로 짝을 지어요. 결과 한 줄에 회원 이름과 강좌 이름이 같이 나와요." + REAL)

# =====================================================================
# part 3: LEFT JOIN, FULL JOIN
# =====================================================================
o = frame("l-left", EB3, "LEFT JOIN은 왼쪽 표의 줄을 다 남기고, 짝이 없으면 NULL로 채워요", C3, transition="magic")
o += cip("left", 1)
ll3 = P("l-left")
t = term_q(ll3, TX0, 214, size=19, w=904, tid="t-cip", lh=1.42)
o.append(t.html())
i5 = at(ll3, "         5 |")
o += tag(t, i5, "강사 칸이 NULL", NUL, 1, gap=150)
o.append(hbox(t, 2, "LEFT JOIN", C3, 1, which="box"))
o.append(hbox(t, at(ll3, "(14 rows)"), "(14 rows)", C3, 2, which="box"))
o.append(note(TX0, t.y + t.h + 26, 904, "강좌 14개가 모두 나와요. 짝이 없는 아쿠아로빅은 강사 이름 자리를 NULL로 채워서 빈칸으로 보여요.", INK, 25, 2))
W("l-left", o, "LEFT JOIN은 왼쪽 표의 줄을 다 남기고, 짝이 없으면 NULL로 채워요. 수업에서 친 문장이에요. JOIN 앞에 LEFT만 붙였어요. 왼쪽 표는 FROM에 먼저 적은 courses예요. 아쿠아로빅은 이을 강사가 없지만 결과에서 빠지지 않고, 강사 이름 칸이 NULL로 채워져요. psql은 NULL을 빈칸으로 보여 줘요. 그래서 결과가 14줄이에요. 강좌 목록을 다 보면서 강사가 정해진 곳만 이름을 붙이고 싶을 때 써요. 강좌가 없는 윤태호는 오른쪽 표라서 여전히 안 나와요." + REAL, ("p3", "짝이 없어도 남기기"))

# ---- which side is left
o = frame("l-swap", EB3, "왼쪽은 FROM에 먼저 적은 표예요. 순서를 바꾸면 남는 쪽이 바뀌어요", C3)
sw = P("l-swap")
t = term_q(sw, 96, 214, size=20, w=1060, tid="t-swap", lh=1.42)
o.append(t.html())
o.append(hbox(t, 1, "FROM instructors i", TI, 1, which="box"))
i8 = at(sw, "             8 |")
o += tag(t, i8, "강좌 칸이 NULL", NUL, 2, gap=210)
RX = t.x + t.w + 50
o.append(hd(RX, 240, "courses LEFT JOIN instructors", TC, 26, 1))
o.append(note(RX, 282, 1824 - RX, "강좌는 다 남아요. 아쿠아로빅 옆이 NULL.", SUB, 25, 1))
o.append(hd(RX, 400, "instructors LEFT JOIN courses", TI, 26, 2))
o.append(note(RX, 442, 1824 - RX, "강사는 다 남아요. 윤태호 옆이 NULL. 박서연처럼 강좌가 둘이면 두 줄이에요.", SUB, 25, 2))
o.append(note(RX, 640, 1824 - RX, "RIGHT JOIN이라는 반대 방향도 있어요. 표 순서를 바꾼 LEFT JOIN과 같아서 수업에서는 LEFT JOIN으로 써요.", GRAY, 24, 3))
W("l-swap", o, "왼쪽은 FROM에 먼저 적은 표예요. 순서를 바꾸면 남는 쪽이 바뀌어요. 이번에는 FROM에 instructors를 먼저 적고 courses를 LEFT JOIN으로 붙였어요. 이제 강사 8명이 모두 남아요. 강좌가 없는 윤태호는 강좌 이름 칸이 NULL이에요. 강좌가 두 개인 강사는 두 줄씩 나와서 모두 14줄이에요. 아쿠아로빅은 이번엔 오른쪽 표라서 안 나와요. RIGHT JOIN이라는 것도 있는데, 표 순서를 바꾼 LEFT JOIN과 같아요. 헷갈리지 않게 남길 표를 FROM에 먼저 적고 LEFT JOIN으로 써요." + REAL)

# ---- FULL JOIN
o = frame("f-full", EB3, "FULL JOIN은 양쪽 표의 줄을 모두 남겨요", C3, transition="magic")
o += cip("full", 1)
ff = P("f-full")
t = term_q(ff, TX0, 214, size=19, w=904, tid="t-cip", lh=1.42)
o.append(t.html())
o.append(hbox(t, 2, "FULL JOIN", C3, 1, which="box"))
iT = at(ff, "윤태호")
o += tag(t, iT, "강좌 칸이 NULL", NUL, 2, gap=40)
o.append(note(TX0, t.y + t.h + 26, 904, "아쿠아로빅도 윤태호도 남아서 15줄이에요. FULL OUTER JOIN이라고 적어도 같아요.", INK, 25, 2))
W("f-full", o, "FULL JOIN은 양쪽 표의 줄을 모두 남겨요. 수업에서 친 문장이에요. 짝이 있는 13줄에, 강사가 없는 아쿠아로빅 한 줄과, 강좌가 없는 윤태호 한 줄이 더해져서 15줄이에요. 아쿠아로빅 줄은 강사 이름이 NULL이고, 윤태호 줄은 강좌 번호와 강좌 이름이 NULL이에요. ORDER BY course_id로 세웠더니 NULL인 윤태호가 맨 끝으로 갔어요. 36에서 본 것처럼 오름차순에서 NULL은 끝에 와요. 수업 코드처럼 FULL OUTER JOIN이라고 적어도 같아요." + REAL)

# ---- the three side by side
o = frame("f-cmp", EB3, "세 JOIN은 짝이 없는 줄을 어디까지 남기느냐만 달라요", C3)
VY = 330
specs = [("JOIN", "짝이 있는 줄만", "13", "a&b", C2), ("LEFT JOIN", "+ 왼쪽의 짝 없는 줄", "14", "a", C3), ("FULL JOIN", "+ 양쪽의 짝 없는 줄", "15", "ab", C3)]
for k, (nm, sub, cnt, mode, col) in enumerate(specs):
    x0 = 96 + k * 590
    ca, cb = (x0 + 170, VY + 150), (x0 + 330, VY + 150)
    r = 120
    fa = f"{col}55"
    cid = f"cl-{k}"
    inner = (f'<defs><clipPath id="{cid}"><circle cx="{ca[0]}" cy="{ca[1]}" r="{r}"/></clipPath></defs>')
    if mode == "a&b":
        inner += f'<circle cx="{cb[0]}" cy="{cb[1]}" r="{r}" fill="{fa}" clip-path="url(#{cid})"/>'
    elif mode == "a":
        inner += f'<circle cx="{ca[0]}" cy="{ca[1]}" r="{r}" fill="{fa}"/>'
    else:
        inner += f'<circle cx="{ca[0]}" cy="{ca[1]}" r="{r}" fill="{fa}"/><circle cx="{cb[0]}" cy="{cb[1]}" r="{r}" fill="{fa}"/>'
    inner += f'<circle cx="{ca[0]}" cy="{ca[1]}" r="{r}" fill="none" stroke="{TC}" stroke-width="4"/><circle cx="{cb[0]}" cy="{cb[1]}" r="{r}" fill="none" stroke="{TI}" stroke-width="4"/>'
    o.append(f'<svg{bi("fade", k + 1)} viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible">{inner}</svg>')
    o.append(p(f"position:absolute;left:{x0}px;top:{VY - 104}px;width:500px;text-align:center;font-family:{MONO};font-size:34px;font-weight:700;color:{col}", e(nm), bi("rise", k + 1)))
    o.append(p(f"position:absolute;left:{x0}px;top:{VY - 56}px;width:500px;text-align:center;font-size:24px;color:{SUB}", e(sub), bi("rise", k + 1)))
    o.append(p(f"position:absolute;left:{ca[0] - 110}px;top:{ca[1] + r + 12}px;width:120px;text-align:center;font-family:{MONO};font-size:22px;font-weight:700;color:{TC}", "courses", bi("rise", k + 1)))
    o.append(p(f"position:absolute;left:{cb[0] - 10}px;top:{cb[1] + r + 12}px;width:160px;text-align:center;font-family:{MONO};font-size:22px;font-weight:700;color:{TI}", "instructors", bi("rise", k + 1)))
    o.append(p(f"position:absolute;left:{x0}px;top:{VY + 320}px;width:500px;text-align:center;font-size:44px;font-weight:900;color:{col}", f"{cnt}줄", bi("rise", k + 1) + COUNT(k + 1) if k == 0 else bi("rise", k + 1)))
lc = [l for l in P("l-count") if l.strip()]
counts = [l.strip() for l in lc if l.strip().isdigit()]
o.append(note(96, 760, 1728, "COUNT(*)로 세어 봐도 " + ", ".join(counts) + "줄이에요. 원 하나는 표 하나, 겹친 곳은 ON 조건이 맞는 짝이에요.", INK, 28, 4))
cmp_rows = [("courses JOIN instructors", "아쿠아로빅 빠짐, 윤태호 빠짐"), ("courses LEFT JOIN instructors", "아쿠아로빅 남음 (강사 NULL)"), ("courses FULL JOIN instructors", "둘 다 남음 (NULL로 채움)")]
for k, (a_, b_) in enumerate(cmp_rows):
    y = 840 + k * 50
    o.append(mono(96, y, a_, INK, 24, 4))
    o.append(p(f"position:absolute;left:640px;top:{y}px;font-size:24px;color:{SUB};white-space:nowrap", e(b_), bi("rise", 4)))
W("f-cmp", o, "세 JOIN은 짝이 없는 줄을 어디까지 남기느냐만 달라요. 원 두 개가 강좌 표와 강사 표예요. 겹친 곳이 ON 조건이 맞는 짝이에요. JOIN은 겹친 곳만 남겨서 13줄이에요. LEFT JOIN은 왼쪽 원 전체를 남겨서 짝 없는 아쿠아로빅까지 14줄이에요. FULL JOIN은 두 원 전체를 남겨서 윤태호까지 15줄이에요. 36에서 배운 COUNT 별표로 줄 수를 세어 봐도 13, 14, 15예요. 어느 JOIN을 쓸지는 짝이 없는 줄을 결과에 보여 줄지로 정해요." + " COUNT(*) 결과는 tools/demo.py로 실제 PostgreSQL 18에서 센 값이에요.")

# ---- find rows with no partner
o = frame("l-find", EB3, "LEFT JOIN 뒤에 IS NULL을 걸면 짝이 없는 줄만 골라져요", C3)
nv = P("e-never")
t = term_q(nv, 96, 214, size=24, w=1000, tid="t-find", lh=1.5)
o.append(t.html())
o.append(hbox(t, 2, "LEFT JOIN enrollments e", C3, 1, which="box"))
o.append(hbox(t, 3, "WHERE e.enrollment_id IS NULL", NUL, 2, which="box"))
i40 = at(nv, "        40 |")
o.append(f'<div{bi("fade", 3)} style="position:absolute;left:{t.x + 16:.0f}px;top:{t.top(i40) - 2:.0f}px;width:{t.w - 32}px;height:{t.lp + 4:.0f}px;border:3px solid {NUL};border-radius:10px"></div>')
FY = t.y + t.h + 50
steps = [("① members LEFT JOIN enrollments", "회원 40명이 다 남아요. 신청이 없는 회원은 e 칸이 NULL이에요.", C3),
         ("② WHERE e.enrollment_id IS NULL", "e 칸이 NULL인 줄, 즉 신청이 한 번도 없는 회원만 남겨요.", NUL),
         ("③ 결과 1줄", "40번 채윤서는 가입만 하고 아직 신청하지 않았어요.", INK)]
for k, (h_, b_, col) in enumerate(steps):
    y = FY + k * 92
    o.append(mono(96, y, h_, col, 26, k + 1))
    o.append(p(f"position:absolute;left:700px;top:{y + 2}px;width:1124px;font-size:25px;line-height:1.45;color:{SUB}", e(b_), bi("rise", k + 1)))
RX = t.x + t.w + 50
o.append(note(RX, 260, 1824 - RX, "36에서 비어 있는 값은 = NULL이 아니라 IS NULL로 찾았어요. 여기서도 같아요.", SUB, 25, 2))
W("l-find", o, "LEFT JOIN 뒤에 IS NULL을 걸면 짝이 없는 줄만 골라져요. 한 번도 신청하지 않은 회원을 찾아서 안내 문자를 보내려고 해요. 먼저 members를 왼쪽에 두고 enrollments를 LEFT JOIN으로 붙여요. 회원 40명이 다 남고, 신청이 없는 회원은 신청 표 칸이 모두 NULL로 채워져요. 여기에 WHERE로 신청 번호가 NULL인 줄만 남기면 짝이 없던 회원만 나와요. 40번 채윤서 한 명이에요. 전화번호도 NULL이라 이메일로 연락해야겠어요. 36에서처럼 NULL은 등호가 아니라 IS NULL로 찾아요." + REAL)

# =====================================================================
# part 4: compare
# =====================================================================
o = frame("c-py", EB4, "파이썬으로 하던 리스트 잇기, 집합 합치기, 딕셔너리 찾기와 같아요", C4)
rows_ = [("UNION ALL", "13 리스트 +", "[27, 17] + [11, 17]", "[27, 17, 11, 17]", C1),
         ("UNION", "16 집합 |", "{27, 17} | {11, 17}", "{27, 17, 11}", C1),
         ("JOIN", "15 딕셔너리 찾기", 'names[3]', "'박도현'", C2),
         ("LEFT JOIN", "15 get()", 'names.get(40)', "None", C3)]
X0, X1, X2, X3 = 96, 400, 760, 1380
o.append(hd(X1, 214, "앞에서 배운 것", GRAY, 24))
o.append(hd(X2, 214, "파이썬 코드", GRAY, 24))
o.append(hd(X3, 214, "결과", GRAY, 24))
RH_ = 132
for k, (sq, ch_, py, res, col) in enumerate(rows_):
    y = 262 + k * RH_
    ra = bi("rise", k + 1)
    o.append(rule(96, y, 1728))
    o.append(p(f"position:absolute;left:{X0}px;top:{y + 40}px;height:52px;padding:0 18px;border-radius:12px;background:{col};font-family:{MONO};font-size:27px;font-weight:700;line-height:52px;color:#FFFFFF;white-space:nowrap", e(sq), ra))
    o.append(p(f"position:absolute;left:{X1}px;top:{y + 46}px;font-size:28px;font-weight:700;color:{INK};white-space:nowrap", e(ch_), ra))
    o.append(mono(X2, y + 46, py, BL, 28, None, ra))
    o.append(mono(X3, y + 46, res, NUL if res == "None" else INK, 28, None, ra))
o.append(rule(96, 262 + 4 * RH_, 1728))
o.append(note(96, 262 + 4 * RH_ + 30, 1728, "names는 회원 번호를 키로, 이름을 값으로 담은 딕셔너리예요. 없는 키를 get()으로 꺼내면 None이 나오듯이, LEFT JOIN은 짝이 없으면 NULL을 채워요.", INK, 27, 4))
W("c-py", o, "파이썬으로 하던 리스트 잇기, 집합 합치기, 딕셔너리 찾기와 같아요. UNION ALL은 13에서 배운 리스트 더하기처럼 그대로 이어 붙여서 17이 두 번 남아요. UNION은 16의 집합 합집합처럼 겹친 값을 하나만 남겨요. JOIN은 15의 딕셔너리에서 키로 값을 찾는 것과 같아요. 회원 번호를 키로 이름을 담은 names에서 3을 찾으면 박도현이 나오죠. JOIN은 신청 한 줄마다 이 찾기를 해 줘요. LEFT JOIN은 get과 비슷해요. 없는 키 40을 get으로 꺼내면 오류 대신 None이 나오듯, 짝이 없으면 NULL을 채워요. 파이썬과 달리 SQL은 표가 커도 한 문장이면 돼요.")

o = frame("c-when", EB4, "열 모양이 같은 결과를 이으면 UNION, 번호로 짝지어 붙이면 JOIN이에요", C4)
cols_ = ["", "UNION · UNION ALL", "JOIN · LEFT JOIN · FULL JOIN"]
X_ = [96, 520, 1160]
for j, c_ in enumerate(cols_):
    o.append(hd(X_[j], 214, c_, [GRAY, C1, C2][j], 28))
trs = [("방향", "위아래로 쌓기", "옆으로 붙이기"),
       ("늘어나는 것", "줄", "열 (짝이 여러 개면 줄도)"),
       ("맞춰야 하는 것", "열 개수와 같은 자리 자료형", "ON 조건 (보통 외래 키)"),
       ("겹친 값", "UNION은 지우고 ALL은 남겨요", "짝마다 한 줄씩 만들어요"),
       ("짝이 없는 줄", "해당 없음", "JOIN은 빼고, LEFT·FULL은 NULL로"),
       ("오늘 예", "세 달 신청자 명단, 강사와 회원 연락처", "신청 옆에 회원 이름, 강좌 옆에 강사")]
for k, row in enumerate(trs):
    y = 270 + k * 104
    o.append(rule(96, y, 1728))
    ra = bi("rise", 1) + DELAY(k * 80)
    o.append(p(f"position:absolute;left:{X_[0]}px;top:{y + 32}px;font-size:26px;font-weight:700;color:{SUB};white-space:nowrap", e(row[0]), ra))
    o.append(p(f"position:absolute;left:{X_[1]}px;top:{y + 32}px;width:600px;font-size:27px;color:{INK};white-space:nowrap", e(row[1]), ra))
    o.append(p(f"position:absolute;left:{X_[2]}px;top:{y + 32}px;width:660px;font-size:27px;color:{INK};white-space:nowrap", e(row[2]), ra))
o.append(rule(96, 270 + 6 * 104, 1728))
o.append(caption("둘을 섞어 쓸 수도 있어요. 6파트에서 JOIN한 결과 두 개를 UNION ALL로 이어 봐요.", 270 + 6 * 104 + 34, 2, size=28, color=SUB))
W("c-when", o, "열 모양이 같은 결과를 이으면 UNION, 번호로 짝지어 붙이면 JOIN이에요. UNION은 위아래로 쌓아서 줄이 늘어나요. 그래서 위아래 결과의 열 개수와 자료형을 맞춰야 해요. JOIN은 옆으로 붙여서 열이 늘어나고, 어떤 줄끼리 붙일지 ON 조건을 적어요. 겹친 값은 UNION이 지우고 UNION ALL이 남겨요. JOIN은 짝이 되는 조합마다 한 줄을 만들어서, 한 회원이 신청을 여러 번 하면 줄이 늘어나요. 짝이 없는 줄은 JOIN이 빼고, LEFT JOIN과 FULL JOIN은 NULL로 채워서 남겨요.")

# =====================================================================
# part 5: errors and traps
# =====================================================================
o = frame("x-amb", EB5, "두 표에 다 있는 열 이름을 그냥 쓰면 어느 표 것인지 몰라요", C5)
xa = P("x-amb")
t = term_q(xa, 96, 214, size=24, w=1150, tid="t-amb", lh=1.55)
o.append(t.html())
o.append(hbox(t, 0, "member_id", RED, 1, which="box"))
o.append(hbox(t, at(xa, "is ambiguous"), 'column reference "member_id" is ambiguous', RED, 1))
FY = t.y + t.h + 50
o.append(hd(96, FY, "고치기: 어느 표의 열인지 별명을 붙여요", GR, 30, 2))
ch, gc = code(["SELECT e.member_id, m.name"], 96, FY + 56, 1150, size=30, cid="amb-fix", attrs=bi("rise", 2))
o.append(ch)
o.append(cbox(gc, 0, "e.", GR, 3, pad=4))
RX = t.x + t.w + 50
o.append(note(RX, 250, 1824 - RX, "ambiguous는 '애매하다'예요. member_id가 enrollments에도 members에도 있어서 PostgreSQL이 고르지 못해요.", INK, 26, 1))
o.append(note(RX, 560, 1824 - RX, "name은 members에만 있어서 별명이 없어도 돼요. 그래도 다 붙여 두면 읽기 쉬워요.", SUB, 25, 2))
W("x-amb", o, "두 표에 다 있는 열 이름을 그냥 쓰면 어느 표 것인지 몰라요. SELECT에 member_id만 적었더니 column reference member_id is ambiguous, 열 이름이 애매하다는 오류가 났어요. JOIN으로 붙인 두 표에 member_id가 둘 다 있어서 어느 쪽을 보여 줄지 PostgreSQL이 고를 수 없는 거예요. 앞에 e 점이나 m 점을 붙여서 표를 정해 주면 돼요. 이 경우는 짝이 맞는 줄이라 둘 다 값이 같지만 그래도 정해 줘야 해요. name처럼 한 표에만 있는 열은 별명 없이도 되지만, 다 붙여 두면 나중에 읽기 쉬워요." + REAL, ("p5", "자주 나는 오류와 함정"))

o = frame("x-alias", EB5, "별명을 붙였으면 표 이름 대신 별명을 써요. JOIN에는 ON이 꼭 있어야 해요", C5)
xl = P("x-alias")
t = term_q(xl, 96, 214, size=24, w=1250, tid="t-xal", lh=1.55)
o.append(t.html())
o.append(hbox(t, 0, "members.name", RED, 1, which="box"))
o.append(hbox(t, at(xl, 'Perhaps you meant'), 'Perhaps you meant to reference the table alias "m".', GR, 1))
i2 = at(xl, "SELECT * FROM courses c JOIN")
o.append(hbox(t, i2, "JOIN instructors i;", RED, 2, which="box"))
RX = t.x + t.w + 50
o.append(note(RX, 260, 1824 - RX, "FROM members m이라고 적는 순간 그 문장에서 members는 m이 돼요. HINT가 m을 쓰라고 알려 줘요.", INK, 25, 1))
o.append(note(RX, t.top(i2) - 10, 1824 - RX, "세미콜론 앞에서 문법 오류가 나요. ON 조건을 빼먹은 거예요.", INK, 25, 2))
o.append(mono(96, t.y + t.h + 40, "JOIN instructors i ON c.instructor_id = i.instructor_id;", GR, 28, 3))
o.append(note(96, t.y + t.h + 92, 1600, "어떤 줄끼리 짝지을지 ON 뒤에 적어야 문장이 끝나요.", SUB, 25, 3))
W("x-alias", o, "별명을 붙였으면 표 이름 대신 별명을 써요. JOIN에는 ON이 꼭 있어야 해요. 첫 번째는 FROM members m으로 별명을 붙여 놓고 SELECT에서 members 점 name이라고 적었어요. 별명을 붙인 순간 그 문장 안에서 members는 m으로 불러야 해서, invalid reference, 잘못 가리켰다는 오류가 나요. HINT 줄이 별명 m을 쓰려던 거냐고 알려 줘요. 두 번째는 JOIN 뒤에 ON을 빼먹었어요. PostgreSQL은 ON이 와야 문장이 끝난다고 읽어서 세미콜론에서 문법 오류를 내요. 아래처럼 ON 조건을 붙이면 돼요." + REAL)

o = frame("x-on", EB5, "ON에 엉뚱한 열을 짝지으면 오류 없이 틀린 결과가 나와요", C5)
xo = P("x-on")
eo = P("e-roster")
t1 = term_q(xo, 96, 214, size=19, w=860, tid="t-xon", lh=1.42)
o.append(t1.html())
o.append(hbox(t1, 3, "e.member_id = c.course_id", RED, 1, which="box"))
_, rr = psql_table(body(eo))
t2 = term_q(body(eo)[:2] + [l for l in body(eo)[2:] if l.strip()], 990, 214 + 6 * t1.lp, size=19, w=834, tid="t-xon2", lh=1.42)
o.append(hd(990, 214, "고친 ON: e.course_id = c.course_id", GR, 26, 2))
o.append(note(990, 262, 834, "같은 문장에서 이 한 곳만 고친 결과예요. 모두 수영 초급 아침반이에요.", SUB, 24, 2))
o.append(t2.html())
i_b = at(xo, "   3 | 박도현")
o.append(obox(1, t1.x + 16, t1.top(i_b) - 2, t1.w - 32, t1.lp + 4, RED, sw=3, r=10))
o += tag(t1, at(xo, "22 | 고은채"), "강좌 이름이 비었어요", RED, 1, gap=150)
o.append(note(96, t1.y + t1.h + 30, 1728, "회원 번호(member_id)와 강좌 번호(course_id)를 짝지었어요. 3번 회원은 3번 강좌 '수영 중급 새벽반'에 붙고, 15번이 넘는 회원은 짝이 없어서 NULL이에요. 수업 코드에 있던 실수라서 고쳐서 썼어요.", INK, 25, 3))
W("x-on", o, "ON에 엉뚱한 열을 짝지으면 오류 없이 틀린 결과가 나와요. 수업 코드의 세 번째 줄을 그대로 실행했어요. 강좌 표를 붙이면서 신청 표의 member_id와 강좌 표의 course_id를 짝지었어요. 회원 번호와 강좌 번호는 뜻이 다른 숫자인데 둘 다 정수라서 PostgreSQL은 그냥 실행해요. 3번 회원 박도현은 3번 강좌 수영 중급 새벽반에 붙었고, 강좌는 14번까지라서 22번 같은 회원은 짝이 없어 NULL이 됐어요. 오른쪽처럼 신청 표의 course_id와 강좌 표의 course_id를 짝지어야 해요. ON에는 같은 뜻의 열끼리, 보통 외래 키와 그 키가 가리키는 열을 적어요." + REAL)

o = frame("x-nocol", EB5, "SELECT 뒤에 열을 빼먹으면 오류 없이 칸이 없는 줄만 나와요", C5)
xn = P("x-nocol")
t = term_q(xn, 96, 214, size=23, w=1150, tid="t-nocol", lh=1.5)
o.append(t.html())
o.append(hbox(t, 0, "SELECT FROM", RED, 1, which="box"))
i_dash = at(xn, "--")
o += tag(t, i_dash, "열이 0개인 표", RED, 1, gap=80)
o.append(hbox(t, at(xn, "SELECT m.member_id"), "m.member_id, m.name, e.course_id", GR, 2, which="box"))
RX = t.x + t.w + 50
o.append(note(RX, 250, 1824 - RX, "수업 코드의 SELECT FROM members m은 오류 대신 빈 줄을 돌려줘요. LIMIT 3을 붙여서 세 줄만 봤어요.", INK, 25, 1))
o.append(note(RX, 560, 1824 - RX, "열을 적으면 내용이 보여요. 신청이 없는 40번 채윤서는 course_id가 NULL이에요.", INK, 25, 2))
W("x-nocol", o, "SELECT 뒤에 열을 빼먹으면 오류 없이 칸이 없는 줄만 나와요. 수업 마지막 FULL OUTER JOIN 코드는 SELECT 바로 뒤에 FROM이 왔어요. PostgreSQL은 이걸 열이 0개인 결과로 읽어서 오류를 내지 않아요. 줄 수만 세어 주고 화면에는 줄표만 나와요. 원래는 188줄이 나오는데 LIMIT 3으로 세 줄만 봤어요. SELECT 뒤에 보고 싶은 열을 적으면 내용이 나와요. 회원 번호 큰 순으로 세웠더니 신청이 없는 40번 채윤서가 맨 위에 course_id NULL로 나와요." + REAL)

o = frame("x-where", EB5, "LEFT JOIN 뒤 WHERE에서 오른쪽 표 열을 비교하면 NULL 줄이 사라져요", C5)
xw = P("x-where")
t = term_q(xw, 96, 214, size=20, w=1000, tid="t-xw", lh=1.42)
o.append(t.html())
o.append(hbox(t, 3, "i.name <> '박서연'", RED, 1, which="box"))
o.append(hbox(t, at(xw, "(2 rows)"), "(2 rows)", RED, 1, which="box"))
ia = at(xw, " 아쿠아로빅")
o += tag(t, ia, "두 번째에는 있어요", NUL, 2, gap=170)
RX = t.x + t.w + 50
o.append(hd(RX, 240, "아쿠아로빅이 빠졌어요", RED, 30, 1))
o.append(note(RX, 290, 1824 - RX, "강사가 NULL인데 NULL <> '박서연'은 참이 아니에요. 36에서 = NULL이 0줄이던 것과 같은 이유예요.", SUB, 25, 1))
o.append(hd(RX, 560, "NULL 줄도 남기려면", GR, 30, 3))
o.append(mono(RX, 610, "OR i.name IS NULL", GR, 28, 3))
o.append(note(RX, 660, 1824 - RX, "조건에 IS NULL을 더해요. 38에서 배운 괄호로 AND와 OR를 묶어요.", SUB, 25, 3))
W("x-where", o, "LEFT JOIN 뒤 WHERE에서 오른쪽 표 열을 비교하면 NULL 줄이 사라져요. 수영 강좌 중 박서연 강사가 아닌 강좌를 보려고 WHERE에 i.name이 박서연이 아니다를 적었어요. 이도윤 강좌 두 개만 나오고, 강사가 없는 아쿠아로빅이 사라졌어요. 강사 이름이 NULL이면 박서연과 다른지 비교한 결과도 참이 아니라서 WHERE에서 걸러져요. 36에서 = NULL로 찾으면 0줄이던 것과 같은 이유예요. 아래처럼 WHERE를 빼면 아쿠아로빅이 NULL로 남아 있어요. NULL 줄도 남기려면 괄호로 묶어서 OR i.name IS NULL을 더해요." + REAL)

# =====================================================================
# part 6: real situations
# =====================================================================
o = frame("e-roster", EB6, "강좌 명단: 신청 표에 회원 이름과 강좌 이름을 붙여요", C6)
er = P("e-roster")
t = term_q(er, 96, 214, size=21, w=1300, tid="t-roster", lh=1.5)
o.append(t.html())
o.append(hbox(t, 3, "LEFT JOIN members m ON e.member_id = m.member_id", TM, 1, which="ul"))
o.append(hbox(t, 4, "LEFT JOIN courses c ON e.course_id = c.course_id", TC, 1, which="ul"))
cancel = [k for k, l in enumerate(er) if "| 취소" in l]
for k in cancel:
    t.band(k, order=2, color="rgba(255,156,148,.18)")
o.append(t.html().replace('id="t-roster"', 'id="t-roster-b"') if False else "")
RX = t.x + t.w + 50
o.append(hd(RX, 250, "11월 수영 초급 아침반", C6, 28, 1))
o.append(note(RX, 296, 1824 - RX, "번호만 있던 신청 7건에 이름과 강좌 이름이 붙었어요.", SUB, 25, 1))
o.append(hd(RX, 520, "취소 2건", RED, 28, 2))
o.append(note(RX, 566, 1824 - RX, "명단을 뽑을 때는 AND e.status <> '취소'를 더해요.", SUB, 25, 2))
W("e-roster", o, "강좌 명단을 뽑아 봐요. 수업에서 친 문장을 ON만 고쳐서 실행했어요. 11월 수영 초급 아침반 신청 일곱 건에 회원 이름과 강좌 이름이 붙었어요. 신청 표는 짝이 반드시 있어서 LEFT JOIN을 JOIN으로 바꿔도 결과가 같아요. 회원이 지워졌는데 신청 기록만 남은 경우까지 대비하려고 LEFT JOIN으로 썼어요. 상태가 취소인 두 줄은 실제로 오지 않을 사람이에요. 출석부로 쓰려면 WHERE에 AND status가 취소가 아니다를 더해요. 이름 순 정렬은 세 글자 이름끼리라서 가나다 순으로 나와요." + REAL, ("p6", "실제 상황 예제"))

o = frame("e-contact", EB6, "연락처 한 목록: JOIN한 결과 두 개를 UNION ALL로 이어요", C6)
ec = P("e-contact")
t = term_q(ec, 96, 214, size=21, w=1180, tid="t-contact", lh=1.5)
iu = at(ec, "UNION ALL")
t.band(0, iu - 1, order=1, color="rgba(227,168,74,.14)")
t.band(iu + 1, iu + 6, order=2, color="rgba(111,155,245,.14)")
o.append(t.html())
RX = t.x + t.w + 50
o.append(hd(RX, 240, "위: 강좌 → 강사", TI, 28, 1))
o.append(note(RX, 286, 1824 - RX, "4번 수영 고급반에 강사 표를 JOIN해서 이도윤을 찾았어요.", SUB, 25, 1))
o.append(hd(RX, 470, "아래: 신청 → 회원", TM, 28, 2))
o.append(note(RX, 516, 1824 - RX, "11월 신청에서 취소를 빼고 회원 표를 JOIN했어요.", SUB, 25, 2))
o.append(hd(RX, 700, "가운데: UNION ALL", C1, 28, 3))
o.append(note(RX, 746, 1824 - RX, "열 세 개의 모양이 같아서 위아래로 이어져요.", SUB, 25, 3))
W("e-contact", o, "강좌 시간이 바뀌어서 강사와 수강생에게 한꺼번에 문자를 보내야 해요. 위 SELECT는 4번 수영 고급반에 강사 표를 JOIN해서 강사 이도윤의 연락처를 찾아요. 아래 SELECT는 11월 신청 중 취소가 아닌 줄에 회원 표를 JOIN해서 수강생 세 명의 연락처를 찾아요. 두 결과 모두 구분, 이름, 전화번호 세 열이라서 UNION ALL로 이을 수 있어요. JOIN과 UNION을 한 문장에 같이 썼어요. 구분 열 덕분에 누가 강사인지 바로 보여요." + REAL)

o = frame("e-check", EB6, "점검 목록: 짝이 없는 강좌와 강사를 한 번에 찾아요", C6)
ek = P("e-check")
t = term_q(ek, 96, 214, size=25, w=1180, tid="t-check", lh=1.55)
o.append(t.html())
o.append(hbox(t, 3, "WHERE i.instructor_id IS NULL", NUL, 1, which="box"))
o.append(hbox(t, 8, "WHERE c.course_id IS NULL;", NUL, 2, which="box"))
RX = t.x + t.w + 50
o.append(hd(RX, 250, "강사 없는 강좌", TC, 28, 1))
o.append(note(RX, 296, 1824 - RX, "courses LEFT JOIN instructors에서 강사 칸이 NULL인 줄이에요.", SUB, 25, 1))
o.append(hd(RX, 470, "강좌 없는 강사", TI, 28, 2))
o.append(note(RX, 516, 1824 - RX, "instructors LEFT JOIN courses에서 강좌 칸이 NULL인 줄이에요.", SUB, 25, 2))
o.append(hd(RX, 700, "윤태호 강사에게 아쿠아로빅을", C6, 28, 3))
o.append(note(RX, 746, 1824 - RX, "두 줄을 보면 할 일이 보여요.", SUB, 25, 3))
W("e-check", o, "센터 관리자가 매달 짝이 없는 강좌와 강사를 점검한다고 해 봐요. 위 SELECT는 강좌 표에 강사 표를 LEFT JOIN하고 강사 번호가 NULL인 줄만 골라요. 아래 SELECT는 거꾸로 강사 표에 강좌 표를 LEFT JOIN하고 강좌 번호가 NULL인 줄만 골라요. 3파트에서 본 짝 없는 줄 찾기를 양쪽으로 한 거예요. 두 결과를 구분 열을 붙여 UNION ALL로 이으면 점검 목록 한 장이 돼요. 강사가 없는 아쿠아로빅과 강좌가 없는 윤태호가 나왔으니, 윤태호 강사에게 아쿠아로빅을 맡기면 되겠어요." + REAL)

# =====================================================================
# summary
# =====================================================================
o = frame("sum", "정리", "언제 무엇을 쓰는지 한 장에 모았어요", INK)
srow = [("UNION ALL", "결과를 그대로 위아래로 이어요", "세 달 신청 건수, 겹쳐도 되는 목록", C1),
        ("UNION", "이은 뒤 겹친 줄을 하나만 남겨요", "한 번이라도 신청한 회원 명단", C1),
        ("JOIN", "ON이 맞는 짝만 옆으로 붙여요", "신청 옆에 회원 이름", C2),
        ("LEFT JOIN", "왼쪽은 다 남기고 짝이 없으면 NULL", "강좌 전체와 강사 이름, 짝 없는 줄 찾기", C3),
        ("FULL JOIN", "양쪽 다 남기고 빈 쪽은 NULL", "강좌와 강사를 빠짐없이 한 표로", C3)]
X_ = [96, 430, 1060]
o.append(hd(X_[1], 214, "하는 일", GRAY, 24))
o.append(hd(X_[2], 214, "오늘 예", GRAY, 24))
for k, (a_, b_, c_, col) in enumerate(srow):
    y = 262 + k * 106
    ra = bi("rise", 1) + DELAY(k * 80)
    o.append(rule(96, y, 1728))
    o.append(p(f"position:absolute;left:{X_[0]}px;top:{y + 28}px;height:50px;padding:0 18px;border-radius:12px;background:{col};font-family:{MONO};font-size:26px;font-weight:700;line-height:50px;color:#FFFFFF;white-space:nowrap", e(a_), ra))
    o.append(p(f"position:absolute;left:{X_[1]}px;top:{y + 34}px;font-size:27px;color:{INK};white-space:nowrap", e(b_), ra))
    o.append(p(f"position:absolute;left:{X_[2]}px;top:{y + 34}px;font-size:27px;color:{SUB};white-space:nowrap", e(c_), ra))
o.append(rule(96, 262 + 5 * 106, 1728))
o.append(caption("다음 41에서는 SELECT 안에 SELECT를 넣는 서브쿼리를 배워요. 평균보다 비싼 강좌처럼 한 번 계산한 결과로 다시 골라요.", 262 + 5 * 106 + 36, 2, size=28, color=SUB))
W("sum", o, "언제 무엇을 쓰는지 한 장에 모았어요. 위 두 줄은 위아래로 쌓는 UNION이에요. 겹쳐도 되면 UNION ALL, 겹친 줄을 지워야 하면 UNION이에요. 아래 세 줄은 옆으로 붙이는 JOIN이에요. 짝이 있는 줄만 필요하면 JOIN, 왼쪽 표를 빠짐없이 보면서 짝이 없으면 비워 두려면 LEFT JOIN, 양쪽 모두 빠짐없이 보려면 FULL JOIN이에요. 다음 41에서는 SELECT 안에 SELECT를 넣는 서브쿼리를 배워요.")

o = frame("cheat", "정리", "오늘 친 문장 모양", INK)
cards_ = [("위아래로 쌓기", C1, ["SELECT 열1, 열2 FROM 표A", "UNION ALL        -- UNION", "SELECT 열1, 열2 FROM 표B", "ORDER BY 열1;    -- 맨 끝에 한 번"]),
          ("옆으로 붙이기", C2, ["SELECT e.열, m.열", "FROM 표A e", "JOIN 표B m ON e.키 = m.키", "JOIN 표C c ON e.키2 = c.키2;"]),
          ("짝 없는 줄 남기기와 찾기", C3, ["FROM 표A a", "LEFT JOIN 표B b ON a.키 = b.키", "-- FULL JOIN: 양쪽 다", "WHERE b.키 IS NULL;  -- 짝 없음"])]
for k, (h_, col, ls) in enumerate(cards_):
    y = 214 + k * 262
    o.append(hd(96, y, h_, col, 28, k + 1))
    ch, gc = code(ls, 96, y + 46, 900, size=24, cid=f"ch-{k}", attrs=bi("rise", k + 1), lh=1.4)
    o.append(ch)
tips = [("열 이름이 애매하다", "별명을 붙여요 e.member_id"), ("별명을 붙였는데 표 이름을 썼다", "별명 m으로 바꿔요"),
        ("JOIN 뒤 ; 에서 문법 오류", "ON 조건을 적어요"), ("결과가 이상하게 NULL투성이", "ON에 같은 뜻의 열끼리"), ("UNION 열 개수, 자료형 오류", "위아래 SELECT 모양을 맞춰요"),
        ("LEFT JOIN인데 NULL 줄이 없다", "WHERE의 오른쪽 열 조건을 봐요")]
o.append(hd(1060, 214, "막히면", RED, 28, 4))
for k, (a_, b_) in enumerate(tips):
    y = 270 + k * 118
    o.append(p(f"position:absolute;left:1060px;top:{y}px;width:764px;font-size:25px;font-weight:700;color:{INK};white-space:nowrap", e(a_), bi("rise", 4)))
    o.append(p(f"position:absolute;left:1060px;top:{y + 40}px;width:764px;font-size:24px;color:{SUB};white-space:nowrap", e(b_), bi("rise", 4)))
W("cheat", o, "오늘 친 문장 모양을 모았어요. 위아래로 쌓을 때는 모양이 같은 SELECT 사이에 UNION ALL이나 UNION을 적고, ORDER BY는 맨 끝에 한 번만 적어요. 옆으로 붙일 때는 FROM 표에 별명을 붙이고 JOIN 표 ON 조건을 적어요. 표가 세 개면 JOIN을 한 번 더 적어요. 짝이 없는 줄도 남기려면 LEFT JOIN이나 FULL JOIN을 쓰고, 짝이 없는 줄만 찾으려면 WHERE에 IS NULL을 걸어요. 오른쪽은 막혔을 때 볼 곳이에요.")
# ===== TAIL =====
# =====================================================================
# toc
# =====================================================================
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
PL = [(C1, EB1[3:], "UNION ALL, UNION, 구분 열 붙이기, 열 개수와 자료형, 맨 끝의 ORDER BY", "u-all", "u-order"),
      (C2, EB2[3:], "표 별명 e, m, JOIN ... ON, 한 줄이 여러 줄과 짝, 짝 없는 줄은 빠져요, 표 세 개", "j-alias", "j-3"),
      (C3, EB3[3:], "LEFT JOIN과 NULL, 왼쪽은 먼저 적은 표, FULL JOIN, 셋 비교, 짝 없는 줄 찾기", "l-left", "l-find"),
      (C4, EB4[3:], "파이썬 리스트 +, 집합 |, 딕셔너리 찾기와 get, 언제 무엇을 쓰나", "c-py", "c-when"),
      (C5, EB5[3:], "ambiguous, 별명 대신 표 이름, ON 빠짐, 잘못 짝지은 ON, 열 없는 SELECT, LEFT JOIN 뒤 WHERE", "x-amb", "x-where"),
      (C6, EB6[3:], "강좌 명단, 강사와 수강생 연락처 한 목록, 짝 없는 강좌와 강사 점검", "e-roster", "e-check")]
plist = [x for x in PL if x[3] in page and x[4] in page]
o = frame("toc", "", "오늘의 순서", INK)
for i, (c, h, s_, a, b) in enumerate(plist):
    y = 214 + i * 124
    o.append(rule(96, y, 1728))
    o.append(p(f"position:absolute;left:96px;top:{y + 26}px;width:80px;font-size:48px;font-weight:900;line-height:1.5;color:{c}", str(i + 1)))
    o.append(p(f"position:absolute;left:190px;top:{y + 20}px;font-size:34px;font-weight:700;color:{INK}", e(h)))
    o.append(p(f"position:absolute;left:190px;top:{y + 74}px;font-size:23px;color:{SUB};white-space:nowrap", e(s_)))
    o.append(p(f"position:absolute;left:1500px;top:{y + 34}px;width:324px;text-align:right;font-size:26px;font-weight:700;color:{GRAY}", f"{page[a]}–{page[b]}쪽"))
if plist:
    o.append(rule(96, 214 + len(plist) * 124, 1728))
o = [x for x in o if 'id="eyebrow"' not in x]
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(o) + f"\n<aside>{e('여섯 파트로 나눴어요. 1파트는 결과를 위아래로 쌓는 UNION이에요. 2파트는 두 표를 옆으로 붙이는 JOIN, 3파트는 짝이 없는 줄도 남기는 LEFT JOIN과 FULL JOIN이에요. 4파트에서 파이썬으로 하던 일과 비교하고, 5파트는 자주 나는 오류와 함정, 6파트는 수업 코드로 푸는 실제 상황 예제예요.')}</aside>\n</section>\n")

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-18T00:00:00Z"}, "lists": "css", "title": "SQL 5 (UNION과 JOIN으로 결과 합치기)", "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
for w_ in WARN:
    print("WARN", w_)
print(len(ORDER), "slides")
