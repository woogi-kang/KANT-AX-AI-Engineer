r"""Generates every slide of the SQL 6 deck (41, subqueries) and slides/deck.json.

Story: to list the courses dearer than the average, a student runs SELECT AVG(fee), copies 97857 and types it into a
second query; when a course is added the copied number is stale. A subquery is a SELECT in parentheses: like (3 + 4)
in arithmetic, the inner part is worked out first and becomes a value, and the outer query uses it. Its result has one
of three shapes, and the shape decides where it may go: one value (WHERE fee > (...), a SELECT column), a list (IN,
NOT IN) or a table (FROM (...) AS paid). Part 1 one value in WHERE, part 2 lists with IN, part 3 a table in FROM
(compared with HAVING and JOIN), part 4 a value in SELECT, part 5 Python's two steps and EXPLAIN ANALYZE (read only),
part 6 errors and three real cases on the class sports-center database (members, courses, enrollments).
Aggregates, GROUP BY, HAVING and JOIN come from 39 and 40; correlated subqueries, EXISTS, ANY/ALL and WITH stay out.

Every psql line comes from tools/demo.py (real Docker and postgres:18, in tools/out.json); tools/sports.sql is the
shared class data of 38-41.
Usage (in 41-sql-subquery): python3 tools/gen.py slides
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
REAL = " psql 화면은 tools/demo.py로 실제 Docker와 PostgreSQL 18을 실행한 결과예요."


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
# chapter 41 helpers
# =====================================================================
MY, VO = "#00758F", "#B26A00"
EB1, EB2, EB3, EB4, EB5, EB6 = "1. 값 하나와 비교하기", "2. 목록과 IN", "3. FROM에 넣는 임시 표", "4. SELECT 칸에 넣기", "5. 비교하고 속 들여다보기", "6. 오류와 실제 상황"
C1, C2, C3, C4, C5, C6 = BL, TEAL, OR, MAG, GR, RED
IN_C, IN_T = "#B26A00", "#E3A84A"            # the inner query: orange on paper, light orange in the terminal
IN_BG = "#FBF0DF"
BAND_IN = "rgba(227,168,74,.20)"


def P(scene, a=None, b=None, k=0):
    """the psql lines of a scene: no banner, no blank lines, no final \\q; a and b cut by a substring"""
    ls = []
    for l in D[scene][k]["out"]:
        l = l.rstrip()
        if not l.strip() or l.startswith("psql (18") or l.startswith('Type "help"') or l.endswith("=# \\q"):
            continue
        if l.endswith("(# \\q"):
            l = l[:-2].rstrip() + " "
        ls.append(l)
    if a is not None:
        i = next(n for n, l in enumerate(ls) if a in l)
        ls = ls[i:]
    if b is not None:
        j = next(n for n, l in enumerate(ls) if n > 0 and b in l)
        ls = ls[:j]
    return ls


def li(t, sub, start=0):
    for n in range(start, len(t.rows)):
        if sub in t.rows[n][1]:
            return n
    raise KeyError(sub)


def PT(lines, x, y, size=26, w=1728, lh=1.5, tid="t", marks=None, maxb=990, **kw):
    """a psql terminal; the font shrinks until it ends above maxb and every line fits its width"""
    rows = psql_rows(lines, marks)
    while True:
        n = len(WARN)
        t = Term(rows, x, y, size=size, w=w, lh=lh, tid=tid, **kw)
        wide = any(t.tx + t_ * 1.01 > x + t.w - Term.PX for t_ in t.tws)
        if (y + t.h <= maxb and not wide) or size <= 16:
            return t
        del WARN[n:]
        size -= 1


def under(t, i, sub, order, color=OR):
    x1 = t.sx(i, sub)
    return underline(order, round(x1), round(x1 + t.sw(sub)), round(t.top(i) + t.lp - 4), color)


def rbox(t, i, sub, order, color=OR, j=None):
    """pen box around sub on line i (to the end of line j when given)"""
    x1 = t.sx(i, sub)
    j = i if j is None else j
    return pen_box(order, round(x1 - 8), round(t.top(i) + 1), round(t.sw(sub) + 16), round((j - i + 1) * t.lp - 2), color, width=4)


def spot_rows(t, i, j, order, dim=0.55, x=None, w=None):
    return spot(order, x=round(x if x is not None else t.x + 10), y=round(t.top(i) - 4), w=round(w if w is not None else t.w - 20), h=round((j - i + 1) * t.lp + 8), dim=dim)


def side(x, y, w, head, body, color, order=None, hsize=30, bsize=25, attrs=""):
    o = [p(f"position:absolute;left:{x}px;top:{y}px;width:{w}px;font-size:{hsize}px;font-weight:700;line-height:1.4;color:{color}", head, bi("rise", order) + attrs)]
    if body:
        o.append(p(f"position:absolute;left:{x}px;top:{y + hsize * 1.4 * (head.count('<br>') + 1) + 10:.0f}px;width:{w}px;font-size:{bsize}px;line-height:1.55;color:{SUB}", body, bi("rise", order) + attrs))
    return o


def kw(text, color=INK):
    return f'<span style="font-family:{MONO};font-weight:700;color:{color}">{e(text)}</span>'


def inner(text):
    """an inner query inside a light code line"""
    return f'<span style="color:{IN_C};font-weight:700">{e(text)}</span>'


def code(cid, x, y, w, lines, fs=28, attrs="", pad=28, lh=1.5, bg=CARD, border=LINE, title=None, tcolor=INK):
    """a light code card; lines are HTML (use e() for plain text)"""
    th = 0
    o = []
    if title:
        th = 50
    hh = round(th + 2 * pad + len(lines) * fs * lh)
    o.append(f'<div id="{cid}"{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{hh}px;background:{bg};border:2px solid {border};border-radius:16px;overflow:hidden">')
    if title:
        o.append(p(f"position:absolute;left:0;top:0;width:{w}px;height:{th}px;padding:0 {pad}px;background:#EEF0F3;border-bottom:2px solid {border};font-size:22px;font-weight:700;line-height:{th - 2}px;color:{tcolor};white-space:nowrap", title))
    body = "".join(p(f"height:{fs * lh:.1f}px;font-family:{MONO};font-size:{fs}px;font-weight:500;line-height:{fs * lh:.1f}px;white-space:pre;color:{INK}", l if l else "&#160;") for l in lines)
    o.append(f'<div style="position:absolute;left:{pad}px;top:{th + pad}px;right:{pad}px;display:flex;flex-direction:column">{body}</div></div>')
    for i, l in enumerate(lines):
        plain = re.sub(r"<[^>]+>", "", l).replace("&#160;", " ").replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
        if tw(plain, fs) > w - 2 * pad - 6:
            WARN.append(f"{cid}: line {i} '{plain[:30]}' wider than the card ({tw(plain, fs):.0f} > {w - 2 * pad - 6})")
    g = {"x": x, "y": y, "w": w, "h": hh, "tx": x + 2 + pad, "ty": y + 2 + th + pad, "lp": fs * lh, "fs": fs}
    return "".join(o), g


def cx_(g, line_plain, sub):
    return g["tx"] + tw(line_plain[:line_plain.index(sub)], g["fs"])


def cy_(g, i):
    return g["ty"] + i * g["lp"]


def grid(x, y, cols, rows, cw, rh, gid, color, fill="#FFFFFF", attrs="", size=26, head_bg=None, mono_=True):
    """a small table picture: cols are header strings (or None for no header), rows are lists of strings"""
    nc = len(rows[0]) if rows else len(cols)
    W_ = cw * nc if isinstance(cw, int) else sum(cw)
    cws = [cw] * nc if isinstance(cw, int) else cw
    hdr = 1 if cols else 0
    H = rh * (len(rows) + hdr)
    o = [f'<div id="{gid}"{attrs} style="position:absolute;left:{x:.0f}px;top:{y:.0f}px;width:{W_ + 6}px;height:{H + 6}px;background:{fill};border:3px solid {color};border-radius:12px;overflow:hidden">']
    ff = f"font-family:{MONO};" if mono_ else ""
    if cols:
        o.append(f'<div style="position:absolute;left:0;top:0;width:{W_}px;height:{rh}px;background:{head_bg or color + "1F"}"></div>')
        cx = 0
        for j, c in enumerate(cols):
            o.append(p(f"position:absolute;left:{cx}px;top:0;width:{cws[j]}px;height:{rh}px;text-align:center;{ff}font-size:{size - 2}px;font-weight:700;line-height:{rh}px;color:{color};white-space:nowrap", e(c)))
            cx += cws[j]
    for i, r in enumerate(rows):
        yy = (i + hdr) * rh
        if i + hdr:
            o.append(f'<div style="position:absolute;left:0;top:{yy - 1}px;width:{W_}px;height:2px;background:{color}33"></div>')
        cx = 0
        for j, v in enumerate(r):
            if j:
                pass
            o.append(p(f"position:absolute;left:{cx}px;top:{yy}px;width:{cws[j]}px;height:{rh}px;text-align:center;{ff}font-size:{size}px;font-weight:500;line-height:{rh}px;color:{INK};white-space:nowrap", e(v)))
            cx += cws[j]
    cx = 0
    for j in range(nc - 1):
        cx += cws[j]
        o.append(f'<div style="position:absolute;left:{cx - 1}px;top:0;width:2px;height:{H}px;background:{color}33"></div>')
    o.append('</div>')
    return "".join(o), (x, y, W_, H)


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
        if order and not stagger:
            ra += DELAY(i * 70)
        for j, v in enumerate(r):
            mono_ = j in mono_cols
            col = (colors[i][j] if colors and colors[i] and colors[i][j] else (INK if (j == 0 and bold_first) or mono_ else SUB))
            fw = 700 if (j == 0 and bold_first) or mono_ else 400
            fs = size - (2 if mono_ else 0)
            o.append(p(f"position:absolute;left:{cx[j]}px;top:{yy + (rh - fs * 1.35) / 2:.0f}px;width:{widths[j] - 20}px;{'font-family:' + MONO + ';' if mono_ else ''}font-size:{fs}px;font-weight:{fw};line-height:1.35;color:{col};white-space:nowrap", v, ra + f' id="{sid}-r{i}c{j}"'))
            if tw(re.sub(r"<[^>]+>|&[a-z#0-9]+;", "x", v), fs, mono_) > widths[j] - 20:
                WARN.append(f"{sid}: cell {i},{j} '{v[:20]}' wider than {widths[j] - 20}")
    o.append(f'<div style="position:absolute;left:{x}px;top:{y0 + len(rows) * rh:.0f}px;width:{W_}px;height:2px;background:{LINE}"></div>')
    return o, y0


def leader_v(x, y1, y2, color, order=None, attrs=""):
    """a vertical leader: dot at the top end"""
    return (f'<div{bi("fade", order)}{attrs} style="position:absolute;left:{x - 5:.0f}px;top:{y1 - 5:.0f}px;width:10px;height:{y2 - y1 + 5:.0f}px">'
            f'<div style="position:absolute;left:0;top:0;width:10px;height:10px;border-radius:5px;background:{color}"></div>'
            f'<div style="position:absolute;left:4px;top:10px;width:2px;height:{y2 - y1 - 5:.0f}px;background:{color}"></div></div>')


def leader_h(x1, x2, y, color, order=None, attrs=""):
    """a horizontal leader from x1 (dot) to x2"""
    return (f'<div{bi("fade", order)}{attrs} style="position:absolute;left:{x1 - 5:.0f}px;top:{y - 5:.0f}px;width:{x2 - x1 + 5:.0f}px;height:10px">'
            f'<div style="position:absolute;left:0;top:0;width:10px;height:10px;border-radius:5px;background:{color}"></div>'
            f'<div style="position:absolute;left:10px;top:4px;width:{x2 - x1 - 5:.0f}px;height:2px;background:{color}"></div></div>')


# =====================================================================
# cover
# =====================================================================
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px">',
       p("position:absolute;left:128px;top:300px;font-size:28px;font-weight:700;color:#9DC1E6", "KANT AX/AI 엔지니어 트랙 · 41"),
       f'<h1{SLAM(1)} style="position:absolute;left:128px;top:350px;padding-bottom:14px;font-size:100px;font-weight:900;line-height:1.3;color:#F6F5F1">SQL 6</h1>',
       p("position:absolute;left:128px;top:500px;font-size:52px;font-weight:700;line-height:1.3;color:#F6F5F1", "쿼리 안에 쿼리 넣기<br>(서브쿼리)"),
       p("position:absolute;left:128px;top:680px;width:700px;font-size:30px;line-height:1.5;color:#BFC6D4", "괄호 안 SELECT가 먼저 값이 되고,<br>바깥 SELECT가 그 값을 써요")]
L = P("min")
t = PT(L, 960, 300, size=20, w=864, tid="cov-term", lh=1.5, maxb=900)
t.band(li(t, "SELECT AVG"), None, None, BAND_IN)
cov.append(t.html())
cov.append(shine(2, "cov-term"))
W("cover", cov, "41 챕터는 SQL 6, 쿼리 안에 쿼리를 넣는 서브쿼리예요. 39에서 AVG, SUM 같은 집계와 GROUP BY를, 40에서 JOIN을 배웠어요. 오늘은 SELECT 문을 괄호로 감싸서 다른 SELECT 안에 넣어요. 오른쪽 화면에서 색칠한 줄이 안쪽 쿼리예요. 안쪽에서 강좌 평균 수강료를 먼저 구하고, 바깥 쿼리가 그 평균보다 비싼 강좌만 골라요. 예제는 38부터 쓰는 스포츠 센터 수업 데이터예요." + REAL, ("intro", "들어가기"))

ORDER.append("toc")   # written last, after page numbers are known

# =====================================================================
# why
# =====================================================================
o = frame("why", "들어가기", "평균을 보고 손으로 옮겨 적으면 쿼리를 두 번 쳐요", INK)
L = P("why")
t = PT(L, 96, 214, size=30, w=1728, lh=1.5, tid="t-why", maxb=880)
av = li(t, "97857.142857142857")
wq = li(t, "WHERE fee > 97857")
rr = li(t, "(6 rows)")
t.band(av, None, 1, BAND_IN)
o.append(t.html())
o += tag(t, av, "① 평균을 먼저 구해요", OR, 1, gap=60)
xn = t.sx(wq, "97857 ")
o.append(link(2, round(t.tx + t.sw("97857") / 2 + t.sw(" ")), round(t.top(av) + t.lp - 2), round(xn + t.sw("97857") / 2), round(t.top(wq) + 4), OR))
o.append(rbox(t, wq, "97857", 2, OR))
o += tag(t, wq, "② 그 숫자를 손으로 옮겨 적어요", OR, 2, gap=40)
o += tag(t, rr, "평균보다 비싼 강좌 6개", GR, 3, gap=40)
o.append(caption("강좌가 늘거나 수강료가 바뀌면 평균도 바뀌어요. 그때마다 이 숫자를 다시 구해서 고쳐 적어야 해요.", t.y + t.h + 36, 4, size=29))
W("why", o, "평균보다 비싼 강좌를 찾으려고 지금까지 배운 것만으로 해 봤어요. 먼저 AVG로 강좌 평균 수강료를 구해요. 97857.14원 정도가 나와요. 그다음 이 숫자를 보고 두 번째 쿼리의 WHERE에 손으로 옮겨 적어요. 결과는 맞게 6개가 나와요. 그런데 이 방법은 쿼리를 두 번 쳐야 하고, 사람이 숫자를 옮겨 적어요. 강좌가 하나 늘거나 수강료가 바뀌면 평균이 바뀌는데, 적어 둔 97857은 그대로 남아요. 오늘은 첫 번째 쿼리를 두 번째 쿼리 안에 통째로 넣어서 한 번에 끝내요." + REAL)

# =====================================================================
# big picture: parentheses first
# =====================================================================
o = frame("big", "들어가기", "괄호 안이 먼저 풀려서 값 하나가 돼요", INK)
LX = 96
o.append(p(f"position:absolute;left:{LX}px;top:252px;font-size:28px;font-weight:700;color:{GRAY}", "수학 괄호"))
o.append(p(f"position:absolute;left:{LX}px;top:560px;font-size:28px;font-weight:700;color:{GRAY}", "SQL 괄호"))
o.append(f'<div style="position:absolute;left:96px;top:470px;width:1728px;height:2px;background:{LINE}"></div>')
MS = 60
mx0 = 380
ARW = (f'<svg width="120" height="40" viewBox="0 0 120 40" style="flex:none">'
       f'<path d="M6,20 L100,20" stroke="{GRAY}" stroke-width="5" fill="none" stroke-linecap="round"/>'
       f'<path d="M96,8 L114,20 L96,32 Z" fill="{GRAY}"/></svg>')
chip = f"color:{IN_C};background:{IN_BG};border-radius:12px;padding:0 10px"
o.append(f'<div style="position:absolute;left:{mx0}px;top:236px;display:flex;align-items:center;gap:56px;font-family:{MONO};font-size:{MS}px;font-weight:700;line-height:1.3;white-space:pre;color:{INK}">'
         f'<span><span id="m-in" style="{chip}">(3 + 4)</span> × 2</span>'
         f'<span{bi("fade", 1)}>{ARW}</span>'
         f'<span><span id="m-7" data-build-in="fly order 1" data-from="m-in" style="display:inline-block;{chip}">7</span> × 2</span>'
         f'<span{bi("fade", 2)}>{ARW}</span>'
         f'<span{bi("pop", 2)} style="color:{GR}">14</span></div>')
o.append(p(f"position:absolute;left:{mx0}px;top:340px;font-size:26px;color:{SUB}", "괄호 안 3 + 4를 먼저 계산해서 7로 바꾼 다음, 바깥 × 2를 해요.", bi("rise", 2)))
# SQL row
SS = 44
sy = 540
sq = "WHERE fee > "
o.append(p(f"position:absolute;left:{mx0}px;top:{sy}px;font-family:{MONO};font-size:{SS}px;font-weight:700;line-height:1.4;white-space:pre;color:{INK}",
           e(sq) + f'<span id="s-in" style="color:{IN_C};background:{IN_BG};border-radius:12px;padding:2px 8px">(SELECT AVG(fee) FROM courses)</span>'))
ix = mx0 + tw(sq, SS)
iw = tw("(SELECT AVG(fee) FROM courses)", SS) + 16
o.append(leader_v(ix + iw / 2, sy + SS * 1.4 + 12, sy + SS * 1.4 + 60, IN_C, 3))
o.append(p(f"position:absolute;left:{ix + iw / 2 - 260:.0f}px;top:{sy + SS * 1.4 + 66:.0f}px;width:520px;text-align:center;font-size:26px;font-weight:700;color:{IN_C}", "① 안쪽 SELECT를 먼저 실행", bi("rise", 3)))
vy = sy + 230
o.append(p(f"position:absolute;left:{mx0}px;top:{vy}px;font-family:{MONO};font-size:{SS}px;font-weight:700;line-height:1.4;white-space:pre;color:{INK}",
           e(sq) + f'<span id="s-val" data-build-in="fly order 4" data-from="s-in" style="display:inline-block;color:{IN_C};background:{IN_BG};border-radius:12px;padding:2px 8px">97857.142857142857</span>'))
o.append(p(f"position:absolute;left:{mx0}px;top:{vy + 80}px;font-size:26px;color:{SUB}", "② 안쪽 결과가 그 자리에 값으로 들어가요. ③ 바깥 SELECT가 이 값으로 줄을 골라요.", bi("rise", 5)))
vx2 = mx0 + tw(sq + "97857.142857142857", SS) + 20 + 60
o.append(svg(arrow_path(f"M{vx2 - 40:.0f},{vy + 31} L{vx2 + 60:.0f},{vy + 31}", GRAY, 5) + head_at(vx2 + 62, vy + 31, 0, GRAY), 5, "draw"))
o.append(p(f"position:absolute;left:{vx2 + 96:.0f}px;top:{vy + 4}px;font-size:34px;font-weight:700;color:{GR};white-space:nowrap", "강좌 6개", bi("pop", 5)))
W("big", o, "서브쿼리는 수학의 괄호와 같아요. (3 더하기 4) 곱하기 2를 계산할 때 괄호 안을 먼저 풀어서 7로 바꾸고, 그다음 곱하기 2를 해요. SQL도 똑같아요. WHERE fee 뒤의 괄호 안에 SELECT 문이 통째로 들어 있어요. 이 안쪽 SELECT가 먼저 실행돼서 평균값 하나가 돼요. 그 값이 괄호 자리에 들어가면 바깥 쿼리는 WHERE fee > 97857.14와 같아져요. 그다음 바깥 SELECT가 이 값으로 줄을 골라서 강좌 6개가 나와요. SELECT 안에 들어간 SELECT를 서브쿼리라고 해요. 바깥 쪽은 메인 쿼리라고 불러요. 손으로 옮겨 적던 숫자를 PostgreSQL이 대신 구해서 넣어 주는 거예요.")

# =====================================================================
# shapes: one value, a list, a table
# =====================================================================
o = frame("shapes", "들어가기", "서브쿼리 결과의 모양이 들어갈 자리를 정해요", INK)
COLX = [96, 690, 1284]
CW = 540
shapes = [("값 하나", "1줄 1칸", C1, "fee > (서브쿼리)", "SELECT 칸에도 (서브쿼리)", "1파트, 4파트"),
          ("목록", "여러 줄 1칸", C2, "member_id IN (서브쿼리)", "NOT IN도 같아요", "2파트"),
          ("표", "여러 줄 여러 칸", C3, "FROM (서브쿼리) AS paid", "이름을 붙여 표처럼", "3파트")]
for k, (nm, sub, c, where1, where2, part) in enumerate(shapes):
    x = COLX[k]
    od = k + 1
    o.append(p(f"position:absolute;left:{x}px;top:226px;font-size:40px;font-weight:900;color:{c}", nm, bi("rise", od)))
    o.append(p(f"position:absolute;left:{x}px;top:286px;font-size:24px;color:{SUB}", sub, bi("rise", od)))
    if k == 0:
        g_, _ = grid(x, 350, ["avg"], [["97857.14"]], 300, 64, f"sh-{k}", c, attrs=bi("pop", od))
    elif k == 1:
        g_, _ = grid(x, 350, ["member_id"], [["11"], ["25"]], 300, 64, f"sh-{k}", c, attrs=bi("pop", od))
    else:
        g_, _ = grid(x, 350, ["member_id", "total_paid"], [["16", "745000"], ["3", "740000"], ["26", "705000"]], [210, 250], 64, f"sh-{k}", c, attrs=bi("pop", od))
    o.append(g_)
    o.append(p(f"position:absolute;left:{x}px;top:640px;font-size:24px;font-weight:700;color:{GRAY}", "들어가는 자리", bi("rise", od) + DELAY(150)))
    o.append(p(f"position:absolute;left:{x}px;top:684px;height:58px;padding:0 18px;border-radius:12px;background:{c};font-family:{MONO};font-size:25px;font-weight:700;line-height:58px;color:#FFFFFF;white-space:nowrap", e(where1), bi("pop", od) + DELAY(150)))
    o.append(p(f"position:absolute;left:{x}px;top:764px;font-size:25px;color:{SUB};white-space:nowrap", e(where2), bi("rise", od) + DELAY(150)))
    o.append(p(f"position:absolute;left:{x}px;top:820px;font-size:24px;font-weight:700;color:{c}", part, bi("rise", od) + DELAY(150)))
o.append(caption("서브쿼리를 쓰기 전에 안쪽 SELECT만 따로 쳐서 결과 모양부터 봐요.", 900, 4, size=30))
W("shapes", o, "서브쿼리 결과의 모양은 세 가지예요. 모양에 따라 들어갈 수 있는 자리가 정해져요. 첫째는 값 하나예요. 평균처럼 1줄 1칸이 나오면 비교 기호 뒤에 두고, SELECT 칸에도 넣을 수 있어요. 1파트와 4파트에서 봐요. 둘째는 목록이에요. 회원 번호 11, 25처럼 한 칸짜리 줄이 여러 개 나오면 IN 괄호 안에 넣어요. 2파트예요. 셋째는 표예요. 회원별 합계처럼 여러 칸, 여러 줄이 나오면 FROM 자리에 두고 AS로 이름을 붙여요. 3파트예요. 그래서 서브쿼리를 쓰기 전에 안쪽 SELECT만 따로 쳐서 어떤 모양이 나오는지 먼저 봐요.")

# =====================================================================
# smallest example
# =====================================================================
o = frame("min", "들어가기", "평균보다 비싼 강좌를 쿼리 한 번에 골라요", INK)
L = P("min")
t = PT(L, 96, 214, size=32, w=1728, lh=1.5, tid="t-min", maxb=900)
a1 = li(t, "kant_shop(# )")
ai = li(t, "SELECT AVG")
t.band(ai, None, 1, BAND_IN)
o.append(t.html())
o += tag(t, ai, "안쪽 쿼리: 평균 97857.14…를 먼저 구해요", OR, 1, gap=60)
o.append(rbox(t, ai, "kant_shop(#", 2, "#9DC1E6", j=a1))
o += tag(t, a1, "괄호가 열려 있는 동안 (# 로 바뀌어요", GRAY, 2, gap=60)
o += tag(t, li(t, "(6 rows)"), "옮겨 적은 숫자 없이 같은 6개", GR, 3, gap=40)
o.append(caption("안쪽 SELECT는 끝에 ;를 붙이지 않아요. 문장 끝 ;는 바깥 쿼리 끝에 하나만 써요.", t.y + t.h + 36, 4, size=29))
W("min", o, "가장 작은 서브쿼리예요. 오늘 수업에서 친 코드 그대로예요. WHERE fee 뒤에 괄호를 열고, 그 안에 SELECT AVG(fee) FROM courses를 적고, 괄호를 닫았어요. 색칠한 줄이 안쪽 쿼리예요. 괄호를 연 동안에는 psql 앞 표시가 kant_shop(#로 바뀌어요. 괄호가 아직 안 닫혔다는 뜻이에요. 결과는 앞 장에서 숫자를 옮겨 적었을 때와 같은 6개예요. 안쪽 SELECT 끝에는 세미콜론을 붙이지 않아요. 세미콜론은 문장 전체가 끝났다는 표시라서 바깥 쿼리 끝에 하나만 써요." + REAL)


# =====================================================================
# part 1: one value in WHERE
# =====================================================================
o = frame("w-max", EB1, "= 뒤에 두면 가장 비싼 강좌, 가장 나이 많은 회원을 찾아요", C1)
L = P("w-max")
t = PT(L, 96, 214, size=28, w=1728, lh=1.55, tid="t-wmax", maxb=760)
q1, q2 = li(t, "MAX(fee)"), li(t, "MIN(birth_year)")
r1, r2 = li(t, "160000"), li(t, "1952")
o.append(t.html())
o.append(rbox(t, q1, "(SELECT MAX(fee) FROM courses)", 1, IN_T))
o.append(spot_rows(t, r1, r1, 2, x=t.x + 10, w=520))
o.append(rbox(t, q2, "(SELECT MIN(birth_year) FROM members)", 3, IN_T))
o.append(spot_rows(t, r2, r2, 4, x=t.x + 10, w=520))
o.append(spot_off(5))
tb, _ = table(96, t.y + t.h + 40, ["안쪽 쿼리", "나오는 값", "바깥 쿼리가 고르는 줄"],
              [[kw("SELECT MAX(fee) FROM courses"), kw("160000", IN_C), "수강료가 160000인 강좌"],
               [kw("SELECT MIN(birth_year) FROM members"), kw("1952", IN_C), "1952년생 회원"]],
              [760, 300, 668], "wmax-tb", size=25, rh=60, order=5)
o += tb
W("w-max", o, "값 하나가 나오는 서브쿼리는 등호 뒤에도 둘 수 있어요. 첫 번째 쿼리는 가장 비싼 수강료를 MAX로 구해서, 그 수강료와 같은 강좌를 찾아요. 필라테스 중급 16만 원이에요. 두 번째는 가장 이른 출생 연도를 MIN으로 구해서 가장 나이 많은 회원을 찾아요. 1952년생 신유찬 회원이에요. MAX만 쓰면 16만이라는 숫자는 알 수 있지만, 그 강좌의 이름은 같이 꺼낼 수 없어요. 숫자를 서브쿼리로 구하고 바깥에서 그 숫자를 가진 줄을 고르면 이름까지 같이 나와요. 가장 비싼 강좌가 두 개면 두 줄이 다 나와요." + REAL, ("p1", "값 하나와 비교하기"))

o = frame("w-sport", EB1, "안쪽 쿼리에도 WHERE를 따로 붙여요", C1)
L = P("w-sport")
marks = {}
t0 = psql_rows(L)
idx_w = next(i for i, r in enumerate(t0) if r[-1].startswith("WHERE sport_id = 1"))
idx_i = next(i for i, r in enumerate(t0) if "AND fee >" in r[-1])
marks = {idx_w: {"sport_id = 1": f'style="color:#7FD1C8"' + MARK(2)}}
t = PT(L, 96, 214, size=32, w=1728, lh=1.55, tid="t-wsport", marks=marks, maxb=860)
av = li(t, "74000")
t.band(li(t, "AND fee >"), None, 1, BAND_IN)
o.append(t.html())
o += tag(t, av, "수영 강좌만의 평균", OR, 1, gap=60)
ii = li(t, "AND fee >")
xs = t.sx(ii, "sport_id = 1)")
o.append(underline(2, round(xs), round(xs + t.sw("sport_id = 1")), round(t.top(ii) + t.lp - 4), TEAL))
xo = t.sx(idx_w, "sport_id = 1")
o.append(underline(2, round(xo), round(xo + t.sw("sport_id = 1")), round(t.top(idx_w) + t.lp - 4), TEAL))
o += tag(t, idx_w, "바깥: 수영 강좌 중에서", TEAL, 2, gap=60)
o += tag(t, li(t, "(2 rows)"), "수영 평균 74000보다 비싼 수영 강좌", GR, 3, gap=40)
o.append(caption("바깥 WHERE와 안쪽 WHERE는 서로 모르는 사이예요. 수영끼리 비교하려면 두 곳에 다 적어요.", t.y + t.h + 36, 4, size=29))
W("w-sport", o, "안쪽 쿼리에도 WHERE를 붙일 수 있어요. 수영 강좌 중에서 수영 평균보다 비싼 강좌를 찾아 봐요. 먼저 수영 강좌 평균만 따로 구하면 74000원이에요. 서브쿼리 안에 WHERE sport_id = 1을 적으면 이 평균이 나와요. 바깥 쿼리에도 WHERE sport_id = 1을 적었어요. 바깥 WHERE가 없으면 요가, 테니스 강좌까지 수영 평균과 비교해요. 안쪽 WHERE가 없으면 전체 평균과 비교해요. 두 WHERE는 서로 영향을 주지 않으니, 필요한 곳에 각각 적어요. 결과는 수영 중급 새벽반 8만 원, 수영 고급반 9만 원이에요." + REAL)

# ---------- w-auto: a new course changes the average ----------
o = frame("w-auto", EB1, "강좌가 늘면 서브쿼리는 새 평균으로 다시 계산해요", C1)
L = P("w-auto")
o.append(p(f"position:absolute;left:96px;top:212px;font-size:26px;font-weight:700;color:{GRAY}", "새 강좌를 넣었어요"))
ins_ = next(l for l in L if l.startswith("kant_shop=# INSERT"))[len("kant_shop=# "):]
o.append(p(f"position:absolute;left:96px;top:256px;font-family:{MONO};font-size:24px;font-weight:700;color:{INK};white-space:nowrap", e(ins_)))
avg_new = L[next(i for i, l in enumerate(L) if "ROUND(AVG" in l) + 3].strip()
o.append(p(f"position:absolute;left:96px;top:306px;font-size:26px;color:{SUB}", f"평균 수강료가 97857.14에서 {kw(avg_new, IN_C)}로 올라갔어요.", bi("rise", 1)))


def rows_after(lines, start_sub):
    i = next(n for n, l in enumerate(lines) if start_sub in l)
    out = []
    for l in lines[i + 3:]:
        if l.startswith("("):
            break
        nm, fe = [x.strip() for x in l.split("|")]
        out.append((nm, fe))
    return out


hard = rows_after(L, "WHERE fee > 97857 ")
subq = rows_after(L, "WHERE fee > (SELECT")
BX = [96, 990]
heads = [("손으로 적은 숫자", f"WHERE fee > {inner('97857')}", RED), ("서브쿼리", f"WHERE fee > {inner('(SELECT AVG(fee) FROM courses)')}", GR)]
RH = 50
for k, (h, c, col) in enumerate(heads):
    x = BX[k]
    rows = hard if k == 0 else subq
    o.append(p(f"position:absolute;left:{x}px;top:390px;font-size:28px;font-weight:700;color:{col}", f"{h} · {len(rows)}개", bi("rise", 2 + k)))
    o.append(p(f"position:absolute;left:{x}px;top:438px;font-family:{MONO};font-size:23px;font-weight:700;color:{INK};white-space:nowrap", c, bi("rise", 2 + k)))
    g_, (gx_, gy_, gw_, gh_) = grid(x, 498, ["course_name", "fee"], [list(r) for r in rows], [470, 230], RH, f"wa-{k}", GRAY if k == 0 else GR, attrs=bi("rise", 2 + k), size=24, mono_=True)
    o.append(g_)
    if k == 0:
        lgb = gy_ + gh_
# the stale row: 헬스 근력 중급 100000 is under the new average
si = next(i for i, r in enumerate(hard) if r[1] == "100000")
ry = 498 + RH * (si + 1)
o.append(pen_box(4, 96 - 8, ry - 4, 700 + 16, RH + 8, RED, width=5))
o.append(p(f"position:absolute;left:96px;top:{lgb + 22}px;font-size:25px;font-weight:700;color:{RED};white-space:nowrap", "빨간 칸의 헬스 근력 중급은 새 평균보다 싸요", bi("rise", 4)))
W("w-auto", o, "서브쿼리는 실행할 때마다 평균을 새로 구해요. 20만 원짜리 헬스 PT 집중 강좌를 하나 넣었어요. 평균 수강료가 104666.67원으로 올라가요. 왼쪽은 처음에 손으로 적은 97857로 고른 결과예요. 7개가 나오는데, 맨 아래 헬스 근력 중급 10만 원은 새 평균보다 싸요. 숫자가 옛날 평균에 멈춰 있어서 틀린 줄이 섞였어요. 오른쪽 서브쿼리는 새 평균으로 다시 계산해서 6개만 골라요. 데이터는 계속 바뀌니까, 기준이 되는 값은 손으로 적지 말고 서브쿼리로 그때그때 구해요." + REAL)


# =====================================================================
# part 2: a list with IN
# =====================================================================
o = frame("i-err", EB2, "여러 줄이 나오는 서브쿼리는 = 뒤에 못 둬요", C2)
L = P("i-err")
t = PT(L, 96, 214, size=31, w=1728, lh=1.55, tid="t-ierr", maxb=790)
r11, r25 = li(t, "        11"), li(t, "        25")
er = li(t, "ERROR")
wq = li(t, "WHERE member_id = (")
t.band(r11, r25, 1, BAND_IN)
o.append(t.html())
o += tag(t, r25, "안쪽만 쳐 보면 두 줄이에요", OR, 1, at=t.tx + t.sw("        25") + 40, gap=60)
o.append(rbox(t, wq, "=", 2, RED))
o.append(under(t, er, "more than one row returned by a subquery", 3, RED))
o.append(shake(3, "t-ierr"))
# a picture: = takes one value, IN takes a list
py_ = t.y + t.h + 44
o.append(p(f"position:absolute;left:96px;top:{py_}px;font-family:{MONO};font-size:40px;font-weight:700;color:{INK};white-space:pre",
           f'member_id <span style="color:{RED}">=</span>  <span style="color:{IN_C}">11, 25</span>', bi("rise", 4)))
o.append(p(f"position:absolute;left:96px;top:{py_ + 72}px;font-size:27px;color:{SUB}", "= 는 값 하나와만 비교해요. 11이랑 같은지, 25랑 같은지 정할 수 없어요.", bi("rise", 4)))
o.append(p(f"position:absolute;left:1000px;top:{py_}px;font-family:{MONO};font-size:40px;font-weight:700;color:{INK};white-space:pre",
           f'member_id <span style="color:{TEAL}">IN</span> (<span style="color:{IN_C}">11, 25</span>)', bi("rise", 5)))
o.append(p(f"position:absolute;left:1000px;top:{py_ + 60}px;width:824px;font-size:25px;color:{SUB}", "IN은 목록 중 하나와 같은지 물어요. 36에서 배웠어요.", bi("rise", 5)))
o.append(caption("목록이 나오는 서브쿼리는 = 대신 IN 괄호 안에 넣어요.", py_ + 170, 6, size=30))
W("i-err", o, "결과가 여러 줄인 서브쿼리는 등호 뒤에 못 둬요. 11월에 필라테스 기구 초급, 13번 강좌를 신청한 회원 번호를 안쪽만 따로 쳐 보면 11과 25, 두 줄이 나와요. 이걸 member_id = 뒤에 넣으면 ERROR가 나요. 오류 문장은 식으로 쓰인 서브쿼리가 한 줄보다 많이 돌려줬다는 뜻이에요. 등호는 값 하나와만 비교하니까 11과 같은지 25와 같은지 정할 수 없어요. 이럴 때는 36에서 배운 IN을 써요. IN은 괄호 안 목록 중 하나와 같은지 물어요. 다음 장에서 IN 괄호 안에 서브쿼리를 넣어요." + REAL, ("p2", "목록과 IN"))

# ---------- i-in: IN (11, 25) becomes IN (subquery) ----------
o = frame("i-in", EB2, "IN 괄호 안에 서브쿼리를 넣으면 목록이 들어가요", C2)
L = P("i-in")
t = PT(L, 96, 214, size=25, w=1040, lh=1.5, tid="t-iin", maxb=990)
s1, s2 = li(t, "IN (11, 25)"), li(t, "WHERE member_id IN (")
ia, ib = li(t, "SELECT member_id FROM enrollments"), li(t, "WHERE course_id = 13")
t.band(ia, ib, 3, BAND_IN)
o.append(t.html())
o.append(rbox(t, s1, "(11, 25)", 1, IN_T))
o += tag(t, li(t, "(2 rows)"), "같은 두 사람", GR, 4, gap=40)
# morph card on the right
MX, MW = 1180, 644
o.append(p(f"position:absolute;left:{MX}px;top:226px;font-size:26px;font-weight:700;color:{GRAY}", "손으로 적은 목록을"))
FS = 26
c1 = ["WHERE member_id IN " + tok("o", "(") + tok("v", f'<span style="color:{IN_C}">11, 25</span>') + tok("c", ")")]
card1 = (f'<div id="mf-a"{MORPH_FROM()} style="position:absolute;left:{MX}px;top:282px;width:{MW}px;height:{round(FS * 1.5 * 6 + 56)}px;background:{CARD};border:2px solid {LINE};border-radius:16px;padding:28px">'
         + "".join(p(f"font-family:{MONO};font-size:{FS}px;font-weight:700;line-height:{FS * 1.5}px;white-space:pre;color:{INK}", l) for l in c1) + '</div>')
o.append(card1)
c2 = ["WHERE member_id IN " + tok("o", "("),
      f'    {tok("v", f"<span style=\"color:{IN_C}\">SELECT member_id</span>")}',
      f'    <span style="color:{IN_C}">FROM enrollments</span>',
      f'    <span style="color:{IN_C}">WHERE course_id = 13</span>',
      f'    <span style="color:{IN_C}">AND enroll_month = \'2026-11\'</span>',
      tok("c", ")")]
card2 = (f'<div id="mf-b"{MORPH(2, "mf-a")} style="position:absolute;left:{MX}px;top:282px;width:{MW}px;height:{round(FS * 1.5 * len(c2) + 56)}px;background:{CARD};border:2px solid {LINE};border-radius:16px;padding:28px">'
         + "".join(p(f"font-family:{MONO};font-size:{FS}px;font-weight:700;line-height:{FS * 1.5}px;white-space:pre;color:{INK}", l) for l in c2) + '</div>')
o.append(card2)
for i, l in enumerate(["  AND enroll_month = '2026-11'"]):
    if tw("    AND enroll_month = '2026-11'", FS) > MW - 60:
        WARN.append("i-in morph card too narrow")
o.append(p(f"position:absolute;left:{MX}px;top:{282 + round(FS * 1.5 * len(c2) + 56) + 24}px;width:{MW}px;font-size:25px;line-height:1.55;color:{SUB}", "PostgreSQL이 목록을 그때그때 구해서 넣어 줘요. 신청자가 바뀌어도 쿼리는 그대로예요.", bi("rise", 3)))
W("i-in", o, "IN 괄호 안에 서브쿼리를 넣으면 목록이 들어가요. 왼쪽 첫 쿼리는 회원 번호 11과 25를 손으로 적었어요. 오른쪽 위 카드처럼 이 목록 자리에 앞 장의 안쪽 쿼리를 그대로 넣으면 아래 카드가 돼요. 안쪽 쿼리가 먼저 실행돼서 11, 25 목록이 되고, 바깥 쿼리는 그 목록에 든 회원의 이름과 전화번호를 꺼내요. 결과는 같은 두 사람이에요. 두 결과의 순서가 다른 것은 ORDER BY를 안 붙였기 때문이에요. 순서가 중요하면 ORDER BY를 붙여요. 신청자가 늘거나 줄어도 쿼리는 고칠 필요가 없어요." + REAL)

# ---------- i-notin ----------
o = frame("i-notin", EB2, "NOT IN은 목록에 없는 사람을 골라요", C2)
L = P("i-notin")
t = PT(L, 96, 214, size=30, w=1180, lh=1.5, tid="t-inot", maxb=990)
ni = li(t, "SELECT member_id FROM enrollments")
n2 = li(t, "(8 rows)")
t.band(ni, None, 1, BAND_IN)
o.append(t.html())
o.append(rbox(t, li(t, "NOT IN ("), "NOT IN", 2, "#7FD1C8"))
o += tag(t, n2, "11월에 신청하지 않은 회원", TEAL, 3, gap=40)
# picture: all members, the November list inside, NOT IN outside
VX, VY = 1340, 250
o.append(f'<div id="v-all"{bi("rise", 4)} style="position:absolute;left:{VX}px;top:{VY}px;width:484px;height:520px;background:{C2}14;border:3px solid {C2};border-radius:28px"></div>')
o.append(p(f"position:absolute;left:{VX + 28}px;top:{VY + 22}px;font-size:26px;font-weight:700;color:{C2}", "회원 40명", bi("rise", 4)))
o.append(f'<div{bi("rise", 4)} style="position:absolute;left:{VX + 60}px;top:{VY + 90}px;width:364px;height:300px;background:#FFFFFF;border:3px dashed {IN_C};border-radius:22px"></div>')
o.append(p(f"position:absolute;left:{VX + 60}px;top:{VY + 200}px;width:364px;text-align:center;font-size:25px;font-weight:700;line-height:1.5;color:{IN_C}", "11월 신청 목록<br>32명", bi("rise", 4)))
o.append(p(f"position:absolute;left:{VX + 28}px;top:{VY + 420}px;width:430px;font-size:26px;font-weight:700;line-height:1.45;color:{INK}", "점선 밖 8명이<br>NOT IN 결과예요", bi("rise", 4)))
o.append(caption("NOT IN 목록 안에 NULL이 하나라도 있으면 결과가 0줄이 돼요. 안쪽 열에 빈 값이 없는지 먼저 봐요.", VY + 520 + 36, 5, size=24, color=SUB, left=1340, width=484))
W("i-notin", o, "NOT IN은 목록에 없는 사람을 골라요. 안쪽 쿼리는 11월 신청 표에 나온 회원 번호 목록이에요. 바깥 쿼리는 그 목록에 없는 회원만 골라요. 결과는 8명이에요. 오른쪽 그림처럼 회원 40명 중 11월 신청자 32명을 빼면 8명이 남아요. 한 가지 주의할 점이 있어요. NOT IN의 목록 안에 NULL이 하나라도 섞이면 결과가 0줄이 돼요. 회원 번호처럼 비어 있지 않은 열로 목록을 만들어요." + REAL)

# ---------- i-join: the same with JOIN ----------
o = frame("i-join", EB2, "JOIN으로 써도 같은 두 사람이 나와요", C2)
LI = P("i-in")
LI = LI[LI.index("kant_shop=# SELECT name, phone"):]
LJ = P("i-join")
o.append(p(f"position:absolute;left:96px;top:212px;font-size:28px;font-weight:700;color:{C2}", "IN 서브쿼리 (2파트)"))
o.append(p(f"position:absolute;left:972px;top:212px;font-size:28px;font-weight:700;color:{GRAY}", "JOIN (40)"))
tI = PT(LI, 96, 266, size=24, w=852, lh=1.5, tid="t-ij1", maxb=740)
tJ = PT(LJ, 972, 266, size=24, w=852, lh=1.5, tid="t-ij2", maxb=740)
tI.band(li(tI, "SELECT member_id FROM"), li(tI, "WHERE course_id"), None, BAND_IN)
o.append(tI.html())
o.append(tJ.html())
ty_ = max(tI.y + tI.h, tJ.y + tJ.h) + 48
tb, _ = table(96, ty_, ["이럴 때", "IN 서브쿼리", "JOIN"],
              [["보여 줄 열이 한 표에만 있어요", "읽기 쉬워요", "같은 결과"],
               ["두 표의 열을 같이 보여 줘요 (신청월과 이름)", "못 해요", "JOIN으로 해요"]],
              [900, 414, 414], "ij-tb", size=25, rh=58, order=1, bold_first=False)
o += tb
W("i-join", o, "같은 질문을 40에서 배운 JOIN으로도 풀 수 있어요. 왼쪽은 IN 서브쿼리, 오른쪽은 신청 표와 회원 표를 JOIN한 쿼리예요. 둘 다 한수아, 손현우 두 사람이 나와요. 보여 줄 열이 회원 표에만 있으면 IN 서브쿼리가 읽기 쉬워요. 회원 표에서 고르는데, 조건은 신청 표에서 가져온다고 바로 읽혀요. 신청월이나 강좌 이름처럼 두 표의 열을 같이 보여 줘야 하면 JOIN을 써요. IN 서브쿼리의 안쪽 열은 바깥에서 꺼낼 수 없어요. 한 회원이 같은 달에 두 번 신청했다면 JOIN은 그 회원을 두 줄로 보여 주고, IN은 한 줄로 보여 줘요." + REAL)


# =====================================================================
# part 3: a table in FROM
# =====================================================================
o = frame("f-err", EB3, "회원별 합계로 거르려고 WHERE에 SUM을 쓰면 막혀요", C3)
L = P("f-err")
t = PT(L, 96, 214, size=32, w=1728, lh=1.55, tid="t-ferr", maxb=640)
wl = li(t, "WHERE SUM")
er = li(t, "ERROR")
o.append(t.html())
o.append(rbox(t, wl, "SUM(pay_amount) >= 600000", 1, RED))
o.append(under(t, er, "aggregate functions are not allowed in WHERE", 2, RED))
# the order PostgreSQL works in
steps = [("FROM", "표를 꺼내요", INK), ("WHERE", "한 줄씩 걸러요", RED), ("GROUP BY", "회원별로 묶어요", INK), ("SUM", "묶음마다 더해요", IN_C), ("SELECT", "보여 줘요", INK)]
sy0 = t.y + t.h + 70
o.append(p(f"position:absolute;left:96px;top:{sy0 - 50}px;font-size:26px;font-weight:700;color:{GRAY}", "PostgreSQL이 처리하는 순서", bi("rise", 3)))
sx = 96
for k, (a_, b_, c) in enumerate(steps):
    w_ = 300
    o.append(f'<div id="fe-s{k}"{bi("rise", 3)}{DELAY(k * 80)} style="position:absolute;left:{sx}px;top:{sy0}px;width:{w_}px;height:120px;background:#FFFFFF;border:3px solid {c};border-radius:16px"></div>')
    o.append(p(f"position:absolute;left:{sx}px;top:{sy0 + 16}px;width:{w_}px;text-align:center;font-family:{MONO};font-size:30px;font-weight:700;color:{c}", a_, bi("rise", 3) + DELAY(k * 80)))
    o.append(p(f"position:absolute;left:{sx}px;top:{sy0 + 66}px;width:{w_}px;text-align:center;font-size:23px;color:{SUB}", b_, bi("rise", 3) + DELAY(k * 80)))
    if k < 4:
        o.append(svg(arrow_path(f"M{sx + w_ + 10},{sy0 + 60} L{sx + w_ + 42},{sy0 + 60}", GRAY, 4) + head_at(sx + w_ + 44, sy0 + 60, 0, GRAY, 14), 3))
    sx += w_ + 57
o.append(caption("WHERE가 일할 때는 아직 합계가 없어요. 합계로 거르려면 HAVING(39)이나 FROM 서브쿼리를 써요.", sy0 + 160, 4, size=29))
W("f-err", o, "합계가 60만 원 이상인 회원을 고르려고 WHERE에 SUM을 적으면 ERROR가 나요. 오류 문장은 WHERE에서는 집계 함수를 쓸 수 없다는 뜻이에요. 아래 그림이 PostgreSQL이 일하는 순서예요. 표를 꺼내고, WHERE로 한 줄씩 거르고, 그다음에 GROUP BY로 회원별로 묶어서 SUM으로 더해요. WHERE가 일하는 순간에는 아직 합계가 없어요. 그래서 합계로 거르는 방법은 두 가지예요. 39에서 배운 HAVING을 쓰거나, 합계를 먼저 구한 결과를 표 하나로 만들어 그 표에 WHERE를 거는 거예요. 이번 파트는 두 번째 방법이에요. 수업 코드는 40만 원 기준이었는데, 이 데이터에서는 6명이 나오도록 60만 원으로 바꿨어요." + REAL, ("p3", "FROM에 넣는 임시 표"))

# ---------- f-inner: the sums as one table ----------
o = frame("f-inner", EB3, "회원별 합계를 먼저 구하면 표 하나가 나와요", C3)
L = P("f-inner")
keep = L[:L.index(next(l for l in L if l.strip().startswith("6 |"))) + 1] + ["…", L[-2], L[-1]]
t = PT(keep, 96, 214, size=32, w=940, lh=1.5, tid="t-finner", maxb=990)
o.append(t.html())
o += tag(t, len(keep) - 1, "39줄짜리 결과", OR, 1, gap=40)
# the same rows as a named table
GX = 1100
gr, (gx_, gy_, gw_, gh_) = grid(GX, 300, ["member_id", "total_paid"], [[r.split("|")[0].strip(), r.split("|")[1].strip()] for r in keep if "|" in r and r.strip()[0].isdigit()][:4], [300, 300], 56, "fi-g", IN_C, attrs=bi("rise", 2), size=26)
o.append(gr)
o.append(p(f"position:absolute;left:{GX}px;top:{300 - 52}px;height:46px;padding:0 18px;border-radius:10px 10px 0 0;background:{IN_C};font-family:{MONO};font-size:26px;font-weight:700;line-height:46px;color:#FFFFFF;white-space:nowrap", "paid", bi("pop", 3) + ' id="fi-name"'))
o.append(p(f"position:absolute;left:{GX}px;top:{gy_ + gh_ + 20}px;width:724px;font-size:25px;line-height:1.55;color:{SUB}", "⋮ 39줄", bi("rise", 2)))
o.append(p(f"position:absolute;left:{GX}px;top:{gy_ + gh_ + 80}px;width:724px;font-size:28px;font-weight:700;line-height:1.5;color:{INK}", "이 결과에 paid라는 이름을 붙이면<br>표처럼 FROM에 둘 수 있어요.", bi("rise", 3)))
W("f-inner", o, "먼저 회원별 합계만 구해 봐요. 39에서 배운 GROUP BY와 SUM이에요. 회원 39명마다 한 줄씩, member_id와 total_paid 두 칸짜리 결과가 나와요. 화면에는 앞의 여섯 줄만 남기고 가운데를 줄였어요. 이 결과는 생긴 게 표와 똑같아요. 줄이 있고 열 이름이 있어요. 그래서 오른쪽처럼 이 결과에 paid라는 이름을 붙이면 courses나 members처럼 FROM 뒤에 둘 수 있어요. 저장되는 표는 아니고, 쿼리가 도는 동안만 있는 임시 표예요." + REAL)

# ---------- f-wrap ----------
o = frame("f-wrap", EB3, "괄호로 감싸고 AS paid를 붙이면 FROM에 표처럼 들어가요", C3)
L = P("f-wrap")
t0 = psql_rows(L)
ia = next(i for i, r in enumerate(t0) if r[-1].startswith(") AS paid"))
iw = next(i for i, r in enumerate(t0) if r[-1].startswith("WHERE paid"))
io = next(i for i, r in enumerate(t0) if r[-1].startswith("ORDER BY paid"))
PC = "#F2A3C8"
marks = {ia: {"paid": f'style="color:{PC}"' + MARK(2)}, iw: {"paid": f'style="color:{PC}"' + MARK(2)}, io: {"paid": f'style="color:{PC}"' + MARK(2)}}
t = PT(L, 96, 214, size=28, w=1160, lh=1.5, tid="t-fwrap", marks=marks, maxb=990)
b0, b1 = li(t, "SELECT member_id, SUM"), li(t, "GROUP BY member_id")
t.band(b0, b1, 1, BAND_IN)
o.append(t.html())
RX = 1310
notes_ = [("① 괄호 안", "회원별 합계 39줄을 먼저 만들어요", IN_C, b0, 1),
          ("② AS paid", "그 결과에 붙인 임시 표 이름", MAG, li(t, ") AS paid"), 2),
          ("③ paid.total_paid", "paid 표의 total_paid 열", MAG, li(t, "WHERE paid"), 3),
          ("④ 6줄", "60만 원 이상만 남았어요", GR, li(t, "(6 rows)"), 4)]
prev = -999
for k, (h, b, c, row, od) in enumerate(notes_):
    y = t.cy(row)
    ty = max(y - 22, prev + 112)
    prev = ty
    x0 = t.x + t.w + 12
    o.append(svg(f'<circle cx="{x0}" cy="{y:.0f}" r="6" fill="{c}"/>'
                 + arrow_path(f"M{x0},{y:.0f} L{x0 + 14},{y:.0f} L{RX - 12},{ty + 20:.0f}", c, 3), od))
    o.append(p(f"position:absolute;left:{RX}px;top:{ty:.0f}px;font-family:{MONO};font-size:26px;font-weight:700;color:{c};white-space:nowrap", e(h), bi("rise", od)))
    o.append(p(f"position:absolute;left:{RX}px;top:{ty + 40:.0f}px;width:514px;font-size:23px;line-height:1.45;color:{SUB}", e(b), bi("rise", od)))
W("f-wrap", o, "회원별 합계 쿼리를 괄호로 감싸서 FROM 뒤에 두고, 닫는 괄호 뒤에 AS paid를 붙였어요. 이제 paid는 member_id와 total_paid 열이 있는 표예요. 바깥 쿼리는 이 paid 표에서 WHERE paid.total_paid >= 600000으로 줄을 걸러요. 이 WHERE는 바깥 쿼리의 WHERE라서, 합계가 이미 다 만들어진 다음에 일해요. 그래서 이번에는 오류가 안 나요. paid.total_paid처럼 표 이름, 점, 열 이름으로 적으면 어느 표의 열인지 분명해요. 결과는 60만 원 이상 낸 회원 6명이에요." + REAL)

# ---------- f-join: the class code ----------
o = frame("f-join", EB3, "임시 표 paid를 회원 표와 JOIN해서 이름을 붙여요", C3)
L = P("f-join")
t = PT(L, 96, 200, size=24, w=1060, lh=1.42, tid="t-fjoin", maxb=985)
b0, b1 = li(t, "SELECT member_id, SUM"), li(t, "GROUP BY member_id")
t.band(b0, b1, None, BAND_IN)
jl = li(t, "LEFT JOIN members")
o.append(t.html())
o.append(lspot(1, t.x, t.y, t.w, t.h, round(t.top(jl)), t.lp, bg=T_BG))
o.append(lspot_off(2))
# picture: paid + members -> result
PX0 = 1240
gp, (_, gpy, gpw, gph) = grid(PX0, 260, ["member_id", "total"], [["16", "745000"], ["3", "740000"]], [140, 160], 52, "fj-p", IN_C, size=22)
o.append(p(f"position:absolute;left:{PX0}px;top:214px;height:40px;padding:0 14px;border-radius:9px 9px 0 0;background:{IN_C};font-family:{MONO};font-size:22px;font-weight:700;line-height:40px;color:#FFFFFF", "paid"))
o.append(gp)
gm, _ = grid(PX0 + 324, 260, ["member_id", "name"], [["16", "황민서"], ["3", "박도현"]], [140, 114], 52, "fj-m", BL, size=22)
o.append(p(f"position:absolute;left:{PX0 + 324}px;top:214px;height:40px;padding:0 14px;border-radius:9px 9px 0 0;background:{BL};font-family:{MONO};font-size:22px;font-weight:700;line-height:40px;color:#FFFFFF", "members m"))
o.append(gm)
o.append(svg(arrow_path(f"M{PX0 + 292},{260 + 52 * 3 + 30} L{PX0 + 292},{260 + 52 * 3 + 96}", GRAY, 5) + head_at(PX0 + 292, 260 + 52 * 3 + 98, 90, GRAY), 2))
o.append(p(f"position:absolute;left:{PX0 + 320}px;top:{260 + 52 * 3 + 44}px;font-family:{MONO};font-size:20px;font-weight:700;color:{GRAY};white-space:nowrap", "ON member_id", bi("rise", 2)))
gr_, _ = grid(PX0, 260 + 52 * 3 + 120, ["회원번호", "회원명", "매출액"], [["16", "황민서", "745000"], ["3", "박도현", "740000"]], [190, 190, 198], 52, "fj-r", GR, attrs=bi("rise", 3), size=22)
o.append(gr_)
o.append(p(f"position:absolute;left:{PX0}px;top:{260 + 52 * 3 + 120 + 52 * 3 + 24}px;width:584px;font-size:24px;line-height:1.55;color:{SUB}", "임시 표도 이름이 있으니 진짜 표처럼 JOIN, WHERE, ORDER BY를 다 붙일 수 있어요.", bi("rise", 3)))
o += tag(t, li(t, "(6 rows)"), "이름이 붙은 6명", GR, 3, gap=40)
W("f-join", o, "오늘 수업에서 친 FROM 서브쿼리예요. 기준만 60만 원으로 바꿨어요. 괄호 안에서 회원별 합계를 만들고 paid라고 이름을 붙였어요. paid에는 회원 번호와 합계만 있고 이름이 없어요. 그래서 40에서 배운 LEFT JOIN으로 회원 표 members를 붙였어요. ON paid.member_id = m.member_id로 같은 회원끼리 이어요. 오른쪽 그림처럼 paid의 한 줄에 회원 표의 이름이 붙어요. SELECT에서는 AS로 회원번호, 회원명, 매출액이라는 한글 열 이름을 붙였어요. 임시 표도 이름이 있으니 진짜 표처럼 JOIN, WHERE, ORDER BY를 다 붙일 수 있어요." + REAL)

# ---------- f-having: same result ----------
o = frame("f-having", EB3, "이 예제는 HAVING으로 써도 같은 6명이 나와요", C3)
L = P("f-having")
t = PT(L, 972, 214, size=24, w=852, lh=1.45, tid="t-fhav", maxb=900)
o.append(t.html())
o += tag(t, li(t, "HAVING"), "39", GRAY, 1, gap=30)
FS = 24
cl = ["SELECT *", "FROM (", inner("    SELECT member_id,"), inner("      SUM(pay_amount) AS total_paid"), inner("    FROM enrollments"), inner("    GROUP BY member_id"),
      ") AS paid", "WHERE paid.total_paid >= 600000", "ORDER BY paid.total_paid DESC;"]
cc, cg = code("fh-c", 96, 214, 852, cl, fs=FS, title="FROM 서브쿼리 (앞 장)", tcolor=C3)
o.append(cc)
by_ = max(cg["y"] + cg["h"], t.y + t.h) + 36
tb, _ = table(96, by_, ["이럴 때", "쓰는 것"],
              [["묶은 결과를 한 번 거르기만 해요", "HAVING이 짧아요"],
               ["묶은 결과로 또 계산하거나 다른 표와 JOIN해요", "FROM 서브쿼리"]],
              [1100, 628], "fh-tb", size=26, rh=60, order=2, bold_first=False)
o += tb
W("f-having", o, "앞 장의 FROM 서브쿼리는 39에서 배운 HAVING으로도 쓸 수 있어요. 오른쪽이 HAVING SUM(pay_amount) >= 600000으로 쓴 쿼리예요. 결과는 같은 6명이에요. 묶은 결과를 한 번 거르기만 할 때는 HAVING이 짧고 읽기 쉬워요. FROM 서브쿼리는 묶은 결과로 또 계산하거나, 앞 장처럼 다른 표와 JOIN할 때 써요. 다음 장에서 HAVING으로는 안 되고 FROM 서브쿼리로만 되는 예를 봐요." + REAL)

# ---------- f-avg: an average of sums ----------
o = frame("f-avg", EB3, "합계의 평균은 FROM 서브쿼리로 구해요", C3)
L = P("f-avg")
t = PT(L, 96, 214, size=28, w=1728, lh=1.5, tid="t-favg", maxb=800)
er = li(t, "ERROR")
b0, b1 = li(t, "    SELECT member_id"), li(t, "    GROUP BY")
t.band(b0, b1, 2, BAND_IN)
o.append(t.html())
o.append(under(t, er, "aggregate function calls cannot be nested", 1, RED))
o += tag(t, li(t, "AVG(SUM"), "AVG 안에 SUM을 바로 못 넣어요", RED, 1, gap=40)
o += tag(t, b1, "① 회원별 합계 39개", OR, 2, gap=60)
res = li(t, "378974")
o += tag(t, res, "② 39개의 평균", GR, 3, at=t.tx + t.sw("     378974") + 20, gap=60)
o.append(caption("한 번 묶어 더한 값을 다시 평균 낼 때처럼, 집계를 두 번 할 때 FROM 서브쿼리가 필요해요.", t.y + t.h + 36, 4, size=29))
W("f-avg", o, "회원 한 명이 평균 얼마를 냈는지 구해 봐요. 회원별 합계를 낸 다음 그 합계들의 평균을 내야 해요. AVG 안에 SUM을 바로 넣으면 ERROR가 나요. 집계 함수를 겹쳐 부를 수 없다는 뜻이에요. HAVING도 묶음 하나하나를 거를 뿐이라 이 계산은 못 해요. 그래서 회원별 합계 39개를 FROM 서브쿼리로 먼저 만들고, 바깥에서 그 39개의 평균을 냈어요. 회원 한 명당 378974원이에요. 이렇게 집계를 두 번 할 때 FROM 서브쿼리가 꼭 필요해요." + REAL)


# =====================================================================
# part 4: one value in SELECT
# =====================================================================
o = frame("s-col", EB4, "SELECT 칸에 넣으면 모든 줄 옆에 같은 값이 붙어요", C4)
L = P("s-col")
t = PT(L, 96, 200, size=23, w=1140, lh=1.42, tid="t-scol", maxb=985)
hd_ = li(t, "전체평균 |")
first, last = hd_ + 2, li(t, "(14 rows)") - 1
x_avg = t.sx(hd_, "전체평균")
x_dif = t.sx(hd_, "평균과차이")
t.band(li(t, "(SELECT ROUND"), li(t, "fee - (SELECT"), None, BAND_IN)
o.append(t.html())
o.append(spot(1, x=round(x_avg - 16), y=round(t.top(hd_) - 4), w=round(t.sw("전체평균 ") + 24), h=round((last - hd_ + 1) * t.lp + 8), dim=0.55))
o.append(spot(2, x=round(x_dif - 16), y=round(t.top(hd_) - 4), w=round(t.sw("평균과차이") + 34), h=round((last - hd_ + 1) * t.lp + 8), dim=0.55))
o.append(spot_off(3))
RX = 1300
o += side(RX, 240, 524, f"{kw('전체평균', C4)}", "안쪽 쿼리가 한 번 계산한 97857.14가 14줄 모두에 붙어요.", INK, 1, hsize=30, bsize=25)
o += side(RX, 470, 524, f"{kw('평균과차이', C4)}", "fee에서 평균을 빼요. 양수면 평균보다 비싼 강좌, 음수면 싼 강좌예요.", INK, 2, hsize=30, bsize=25)
o += side(RX, 720, 524, "값 하나만 돼요", "SELECT 칸 하나에는 값 하나만 들어가요. 그래서 1줄 1칸이 나오는 서브쿼리만 넣어요.", INK, 3, hsize=30, bsize=25)
W("s-col", o, "서브쿼리는 SELECT의 열 자리에도 넣을 수 있어요. 오늘 수업에서 친 스칼라 서브쿼리예요. 스칼라는 값 하나라는 뜻이에요. 전체평균 열에는 안쪽 쿼리가 구한 평균 97857.14가 14줄 모두에 똑같이 붙었어요. 평균과차이 열은 각 강좌의 fee에서 그 평균을 뺀 값이에요. 양수면 평균보다 비싸고, 음수면 평균보다 싸요. 집계 함수만 쓰면 결과가 한 줄로 줄어드는데, 서브쿼리로 넣으면 모든 줄을 그대로 두고 옆에 평균을 붙일 수 있어요. 열 하나에는 값 하나만 들어가니까 1줄 1칸이 나오는 서브쿼리만 넣어요." + REAL, ("p4", "SELECT 칸에 넣기"))

o = frame("s-ratio", EB4, "전체 회원 중 몇 %가 사는 구인지 계산해요", C4)
L = P("s-ratio")
t = PT(L, 96, 214, size=24, w=1160, lh=1.45, tid="t-srat", maxb=990)
t.band(li(t, "(SELECT COUNT(*) FROM members) AS"), li(t, "ROUND(COUNT(*)"), None, BAND_IN)
o.append(t.html())
hd_ = li(t, "region")
rows_ = [l for l in L if "|" in l and l.strip()[0] not in "r-"]
rows_ = [[c.strip() for c in l.split("|")] for l in rows_ if not l.strip().startswith("region")]
o += tag(t, li(t, " 영등포구"), "40은 모든 줄에 같아요 (전체 회원 수)", OR, 1, at=t.tx + t.sw(" 영등포구 |     12 |   40 | 30.0") + 20, gap=40)
# bars
BX0, BY0, BW = 1340, 300, 484
o.append(p(f"position:absolute;left:{BX0}px;top:{BY0 - 64}px;font-size:26px;font-weight:700;color:{GRAY}", "비율 (%)", bi("rise", 2)))
for k, (rg, cnt, tot, pct) in enumerate(rows_):
    y = BY0 + k * 130
    w_ = BW * float(pct) / 40
    o.append(p(f"position:absolute;left:{BX0}px;top:{y}px;font-size:26px;font-weight:700;color:{INK}", e(rg), bi("rise", 2) + DELAY(k * 80)))
    o.append(f'<div{WIPE(2)} style="position:absolute;left:{BX0}px;top:{y + 46}px;width:{w_:.0f}px;height:34px;border-radius:8px;background:{C4 if k == 0 else C4 + "99"}"></div>')
    o.append(p(f"position:absolute;left:{BX0 + w_ + 14:.0f}px;top:{y + 44}px;font-family:{MONO};font-size:26px;font-weight:700;color:{INK}", e(pct), bi("rise", 2) + DELAY(200 + k * 80)))
o.append(caption("100.0처럼 소수점을 붙여서 곱해야 나눗셈이 소수로 나와요.", t.y + t.h + 30, 3, size=26, color=SUB, width=1160))
W("s-ratio", o, "스칼라 서브쿼리는 전체에서 몇 퍼센트인지 계산할 때 자주 써요. 사는 구별로 묶어서 COUNT로 회원 수를 세면, 묶음 안에서는 전체 회원 수를 알 수 없어요. 그래서 전체 회원 수 40을 서브쿼리로 구해서 나눴어요. 영등포구는 12 나누기 40, 30퍼센트예요. 100 대신 100.0을 곱한 이유는 정수끼리 나누면 소수점 아래가 버려지기 때문이에요. 오른쪽 막대는 비율 열을 그린 거예요. ROUND로 소수 첫째 자리까지 남겼어요." + REAL)

o = frame("s-err", EB4, "SELECT 칸 서브쿼리가 열 두 개를 돌려주면 막혀요", C4)
L = P("s-err")
t = PT(L, 96, 214, size=30, w=1728, lh=1.55, tid="t-serr", maxb=600)
er = li(t, "ERROR")
o.append(t.html())
o.append(rbox(t, 0, "AVG(fee), MAX(fee)", 1, RED))
o.append(under(t, er, "subquery must return only one column", 2, RED))
# fix: two subqueries
fy = t.y + t.h + 60
o.append(p(f"position:absolute;left:96px;top:{fy}px;font-size:28px;font-weight:700;color:{GR}", "열마다 서브쿼리를 하나씩 둬요", bi("rise", 3)))
cl = ["SELECT course_name,",
      "       " + inner("(SELECT AVG(fee) FROM courses)") + " AS 평균,",
      "       " + inner("(SELECT MAX(fee) FROM courses)") + " AS 최고",
      "FROM courses;"]
cc, _ = code("se-fix", 96, fy + 56, 1100, cl, fs=28, attrs=bi("rise", 3))
o.append(cc)
W("s-err", o, "SELECT 칸에 넣은 서브쿼리가 열 두 개를 돌려주면 ERROR가 나요. 평균과 최고 수강료를 한 괄호 안에서 같이 꺼냈어요. 오류 문장은 서브쿼리가 열을 하나만 돌려줘야 한다는 뜻이에요. SELECT 칸 하나에는 값 하나만 들어가요. 두 값이 필요하면 아래처럼 칸마다 서브쿼리를 하나씩 두고 각각 AS로 이름을 붙여요." + REAL)


# =====================================================================
# part 5: compare and look inside
# =====================================================================
o = frame("c-python", EB5, "파이썬에서는 두 줄로 나눠 쓰던 일을 SQL은 한 문장에 담아요", C5)
PY = [l.rstrip("\n") for l in open(os.path.join(HERE, "fees.py"))]
pyl = [e(PY[0][:44]) + " …", f'<span style="color:{IN_C}">{e(PY[1])}</span>', e(PY[2]), e(PY[3])]
cc, cg = code("cp-py", 96, 214, 860, pyl, fs=25, title="fees.py (23 컴프리헨션)", tcolor=GR)
o.append(cc)
outp = D["py"][0]["out"]
o.append(f'<div style="position:absolute;left:96px;top:{cg["y"] + cg["h"] + 20}px;width:860px;height:{round(2 * 25 * 1.5 + 48)}px;background:{T_BG};border-radius:16px;padding:24px 28px">'
         + "".join(p(f"font-family:{MONO};font-size:23px;line-height:{25 * 1.5:.0f}px;white-space:pre;color:#D8DEE9", e(l)) for l in outp) + '</div>')
o.append(p(f"position:absolute;left:96px;top:{cg['y'] + cg['h'] + 20 + 2 * 25 * 1.5 + 48 + 16:.0f}px;width:860px;font-size:22px;color:{GRAY}", "$ uv run fees.py"))
sl = ["SELECT fee", "FROM courses", "WHERE fee > (", inner("    SELECT AVG(fee) FROM courses"), ");"]
sc, sg = code("cp-sql", 1000, 214, 824, sl, fs=25, title="SQL 서브쿼리", tcolor=GR)
o.append(sc)
o.append(link(1, 96 + 860, round(cy_(cg, 1) + cg["lp"] / 2), 1000, round(cy_(sg, 3) + sg["lp"] / 2), IN_C))
tb, _ = table(1000, sg["y"] + sg["h"] + 40, ["", "파이썬", "SQL"],
              [["평균", "변수 avg에 담아 둬요", "괄호 안 SELECT"], ["거르기", "if f > avg", "WHERE fee > (...)"], ["줄 수", "두 줄", "한 문장"]],
              [150, 337, 337], "cp-tb", size=24, rh=58, order=2)
o += tb
W("c-python", o, "23에서 배운 컴프리헨션으로 같은 일을 해 봐요. 파이썬에서는 수강료 목록의 평균을 먼저 구해서 변수 avg에 담고, 다음 줄에서 avg보다 큰 값만 골랐어요. 결과는 SQL과 같은 여섯 개 수강료예요. 파이썬은 평균을 변수에 담아 두고 다음 줄에서 써요. SQL에는 변수가 없으니, 평균을 구하는 SELECT를 쓸 자리에 괄호로 바로 넣어요. 두 줄이 한 문장이 된 거예요. 색칠한 부분끼리 같은 일을 해요." + " 파이썬 출력은 fees.py를 실제로 실행한 결과예요.", ("p5", "비교하고 속 들여다보기"))

o = frame("cmp", EB5, "서브쿼리를 넣는 자리는 네 곳이에요", C5)
rows_ = [[kw("WHERE 열 > (…)", C1), "값 하나", kw("fee > (SELECT AVG(fee) …)"), "없어요"],
         [kw("WHERE 열 IN (…)", C2), "목록", kw("member_id IN (SELECT member_id …)"), "JOIN"],
         [kw("FROM (…) AS 이름", C3), "표", kw("FROM (SELECT … GROUP BY …) AS paid"), "HAVING (거르기만 할 때)"],
         [kw("SELECT (…) AS 이름", C4), "값 하나", kw("(SELECT COUNT(*) FROM members) AS 전체"), "없어요"]]
tb, y0 = table(96, 220, ["자리", "결과 모양", "예", "같은 일을 하는 다른 방법"], rows_, [420, 200, 720, 388], "cmp-tb", size=26, rh=110, order=1, stagger=True, bold_first=False)
o += tb
o.append(caption("모양이 맞지 않으면 오류가 나요. 어떤 모양이 나오는지는 안쪽 SELECT만 따로 쳐서 확인해요.", y0 + 4 * 110 + 50, 5, size=29))
W("cmp", o, "지금까지 본 네 자리를 한 표에 모았어요. WHERE의 비교 기호 뒤에는 값 하나가 나오는 서브쿼리를 둬요. IN 괄호 안에는 목록이 나오는 서브쿼리를 둬요. 같은 일을 JOIN으로도 할 수 있어요. FROM 뒤에는 표가 나오는 서브쿼리를 두고 AS로 이름을 붙여요. 거르기만 할 때는 HAVING이 더 짧아요. SELECT 칸에는 값 하나가 나오는 서브쿼리를 둬요. 자리에 맞지 않는 모양을 넣으면 다음 파트에서 볼 오류가 나요. 그래서 안쪽 SELECT만 따로 쳐서 모양부터 확인하는 습관이 가장 쓸모 있어요.")

o = frame("explain", EB5, "EXPLAIN ANALYZE로 보면 안쪽 쿼리가 먼저 한 번 돌아요", C5)
o.append(p(f"position:absolute;left:{1824 - 260}px;top:56px;width:260px;height:44px;border-radius:22px;background:{GRAY};text-align:center;font-size:22px;font-weight:700;line-height:44px;color:#FFFFFF", "참고, 읽기만"))
L = P("explain")
t = PT(L, 96, 214, size=21, w=1728, lh=1.5, tid="t-expl", maxb=760)
fl = li(t, "Filter:")
ip = li(t, "InitPlan 1", fl + 1)
ag = li(t, "->  Aggregate")
rr = li(t, "Rows Removed")
o.append(t.html())
o.append(zoom(1, t.x, round(t.top(fl) - 10), t.w, round((ag + 2 - fl) * t.lp + 20)))
o.append(zoom_off(4))
def badge(x, y, n, c, od):
    return (f'<div{bi("pop", od)} style="position:absolute;left:{x:.0f}px;top:{y:.0f}px;width:28px;height:28px;border-radius:14px;background:{c};'
            f'text-align:center;font-size:19px;font-weight:900;line-height:28px;color:#FFFFFF">{n}</div>')


for row, n, c, od in [(ip, "1", OR, 2), (ag, "1", OR, 2), (fl, "2", BL, 3), (rr, "3", GRAY, 3)]:
    o.append(badge(t.end(row) + 16, t.top(row) + (t.lp - 28) / 2, n, c, od))
ly = t.y + t.h + 32
leg = [("1", OR, "InitPlan 1 · Aggregate", "안쪽 쿼리예요. 평균을 구하고 loops=1, 한 번만 돌아요.", 2),
       ("2", BL, "Filter", "그 평균과 fee를 비교해요.", 3),
       ("3", GRAY, "Rows Removed by Filter: 8", "14줄 중 8줄이 걸러지고 6줄이 남았어요.", 3)]
LXS = [96, 700, 1260]
for k, (n, c, h, b_, od) in enumerate(leg):
    x = LXS[k]
    o.append(badge(x, ly, n, c, od))
    o.append(p(f"position:absolute;left:{x + 48}px;top:{ly}px;width:{(LXS[k + 1] if k < 2 else 1824) - x - 80}px;font-family:{MONO};font-size:22px;font-weight:700;line-height:34px;color:{c};white-space:nowrap", e(h), bi("rise", od)))
    o.append(p(f"position:absolute;left:{x + 48}px;top:{ly + 42}px;width:{(LXS[k + 1] if k < 2 else 1824) - x - 80}px;font-size:23px;line-height:1.45;color:{SUB}", e(b_), bi("rise", od)))
o.append(caption("EXPLAIN ANALYZE는 쿼리를 실제로 돌리고 어떤 순서로 일했는지 보여 줘요. 시간 숫자는 칠 때마다 조금씩 달라요.", ly + 140, 5, size=27))
W("explain", o, "이 장은 참고로 읽기만 해요. 쿼리 앞에 EXPLAIN ANALYZE를 붙이면 PostgreSQL이 쿼리를 실제로 실행하고, 어떤 순서로 일했는지 보여 줘요. 수업에서 JOIN 쿼리에 한 번 붙여 봤어요. InitPlan 1이 안쪽 쿼리예요. Aggregate는 AVG를 계산한 단계이고, loops=1은 딱 한 번 실행됐다는 뜻이에요. 그 위의 Filter 줄은 fee를 InitPlan 1의 결과와 비교한다는 뜻이에요. 14줄 중 8줄이 걸러지고 6줄이 남았어요. 안쪽 쿼리가 먼저 한 번 돌고 바깥 쿼리가 그 값을 쓴다는 오늘의 설명이 그대로 보여요. 시간 숫자는 칠 때마다 조금씩 달라요." + REAL)


# =====================================================================
# part 6: errors and real cases
# =====================================================================
o = frame("x-table", EB6, "서브쿼리에서 자주 만나는 오류 여섯 가지", C6)
tr = [("more than one row returned by a subquery used as an expression", "= 뒤 서브쿼리가 여러 줄을 돌려줬어요", "IN (…)으로 바꿔요"),
      ("subquery must return only one column", "SELECT 칸 서브쿼리가 열 두 개를 꺼냈어요", "열마다 서브쿼리 하나"),
      ("aggregate functions are not allowed in WHERE", "WHERE에 SUM, COUNT를 썼어요", "HAVING이나 FROM 서브쿼리"),
      ("aggregate function calls cannot be nested", "AVG(SUM(…))처럼 겹쳐 썼어요", "안쪽 집계를 FROM 서브쿼리로"),
      ('missing FROM-clause entry for table "paid"', "FROM 서브쿼리에 AS 이름을 안 붙였어요", ") AS paid"),
      ('syntax error at or near "SELECT"', "서브쿼리를 괄호로 안 감쌌어요", "( )로 감싸요")]
o.append(p(f"position:absolute;left:96px;top:214px;font-size:24px;font-weight:700;color:{GRAY}", "ERROR:  뒤에 이런 글이 보이면"))
o.append(p(f"position:absolute;left:1400px;top:214px;font-size:24px;font-weight:700;color:{GRAY}", "이렇게 해요"))
for i, (q, a_, c_) in enumerate(tr):
    y = 262 + i * 112
    ra = bi("rise", 1) + DELAY(i * 70)
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:2px;background:{LINE}"></div>')
    o.append(p(f"position:absolute;left:96px;top:{y + 16}px;width:1280px;font-family:{MONO};font-size:24px;font-weight:700;color:{RED};white-space:nowrap", e(q), ra))
    o.append(p(f"position:absolute;left:96px;top:{y + 60}px;width:1280px;font-size:24px;color:{SUB}", e(a_), ra))
    o.append(p(f"position:absolute;left:1400px;top:{y + 36}px;width:424px;font-size:25px;font-weight:700;color:{INK};white-space:nowrap", e(c_), ra))
o.append(f'<div style="position:absolute;left:96px;top:{262 + 6 * 112}px;width:1728px;height:2px;background:{LINE}"></div>')
W("x-table", o, "서브쿼리에서 자주 만나는 오류 여섯 가지예요. 첫째, 등호 뒤 서브쿼리가 여러 줄을 돌려주면 more than one row 오류가 나요. IN으로 바꿔요. 둘째, SELECT 칸 서브쿼리가 열을 두 개 꺼내면 only one column 오류가 나요. 셋째, WHERE에 SUM이나 COUNT를 쓰면 not allowed in WHERE가 나요. HAVING이나 FROM 서브쿼리를 써요. 넷째, AVG 안에 SUM을 겹쳐 쓰면 cannot be nested가 나요. 다섯째, FROM 서브쿼리에 AS 이름을 안 붙이고 paid 점 열 이름으로 부르면 paid라는 표를 못 찾는다고 나와요. 여섯째, 괄호 없이 SELECT를 바로 쓰면 SELECT 근처에서 문법 오류가 나요. 다섯째와 여섯째는 다음 장에서 실제 화면으로 봐요.", ("p6", "오류와 실제 상황"))

o = frame("x-paren", EB6, "괄호와 AS 이름을 빼먹으면 이렇게 막혀요", C6)
L1 = P("x-paren")
L2 = P("f-noalias")
t1 = PT(L1, 96, 214, size=24, w=1728, lh=1.5, tid="t-xp1", maxb=520)
o.append(t1.html())
e1 = li(t1, "ERROR")
o.append(under(t1, e1, 'syntax error at or near "SELECT"', 1, RED))
wait = len(t1.rows) - 1
o += tag(t1, wait, "괄호를 안 닫아서 아직 기다려요", OR, 2, at=t1.tx + t1.sw("kant_shop(# ") + 10, gap=50)
t2 = PT(L2, 96, t1.y + t1.h + 40, size=24, w=1728, lh=1.5, tid="t-xp2", maxb=990)
o.append(t2.html())
e2 = li(t2, "ERROR")
o.append(under(t2, e2, 'missing FROM-clause entry for table "paid"', 3, RED))
o += tag(t2, len(t2.rows) - 1, "FROM 줄의 닫는 괄호 뒤에 AS paid가 없어요", RED, 3, gap=60)
W("x-paren", o, "위 화면은 괄호 실수 두 가지예요. 첫 줄은 fee > 뒤에 괄호 없이 SELECT를 바로 적었어요. PostgreSQL은 비교 기호 뒤에 SELECT라는 단어가 오면 문법 오류로 봐요. LINE 줄의 꺾쇠가 SELECT를 가리켜요. 두 번째 줄은 괄호를 열기만 하고 안 닫았어요. 세미콜론을 쳐도 앞 표시가 kant_shop(#로 남아서 계속 기다려요. 닫는 괄호와 세미콜론을 마저 치면 돼요. 아래 화면은 FROM 서브쿼리에 AS paid를 안 붙이고 paid.member_id로 불렀어요. paid라는 이름이 어디에도 없어서 그런 표를 못 찾는다고 나와요. 닫는 괄호 뒤에 AS paid를 붙여요." + REAL)

# ---------- real case 1: seats left ----------
o = frame("r-seat", EB6, "실제 상황 1 · 11월 강좌마다 남은 자리를 계산해요", C6)
L = P("r-seat")
t = PT(L, 96, 200, size=25, w=1728, lh=1.45, tid="t-rseat", maxb=860)
b0, b1 = li(t, "SELECT course_id, COUNT"), li(t, "GROUP BY course_id")
t.band(b0, b1, 1, BAND_IN)
o.append(t.html())
o += tag(t, b0 + 1, "임시 표 n: 강좌별 11월 신청 수", OR, 1, gap=60)
o.append(rbox(t, li(t, "AS n ON"), "AS n ON c.course_id = n.course_id", 2, "#9DC1E6"))
o += tag(t, li(t, "AS n ON"), "강좌 표와 이어요", BL, 2, gap=40)
hd_ = li(t, "| 정원 |")
o.append(spot_rows(t, hd_ + 2, hd_ + 2, 3))
o.append(spot_off(4))
o += tag(t, hd_ + 2, "자리가 가장 적게 남은 강좌", GR, 4, gap=40)
o.append(caption("신청 수를 먼저 세고(FROM 서브쿼리), 정원이 있는 강좌 표와 이어서 뺄셈했어요.", t.y + t.h + 32, 4, size=28))
W("r-seat", o, "첫 번째 실제 상황이에요. 데스크 직원이 11월 강좌마다 자리가 몇 개 남았는지 묻는다고 해 봐요. 정원은 courses 표에, 신청은 enrollments 표에 있어요. 먼저 괄호 안에서 11월 신청 중 취소를 뺀 신청 수를 강좌별로 셌어요. 이 결과에 n이라는 이름을 붙이고, 강좌 표 c와 JOIN했어요. 그러면 한 줄에 정원과 신청 수가 같이 있어서 c.capacity - n.cnt로 남은 자리를 계산할 수 있어요. 남은 자리가 적은 순으로 다섯 개만 봤어요. 테니스 고급 레슨은 정원 6명에 3명이 신청해서 3자리 남았어요." + REAL)

# ---------- real case 2: the most popular course ----------
o = frame("r-pop", EB6, "실제 상황 2 · 가장 많이 신청한 강좌의 이름을 찾아요", C6)
L = P("r-pop")
t = PT(L, 96, 200, size=25, w=1728, lh=1.42, tid="t-rpop", maxb=990)
top_ = li(t, "         2 |")
b0, b1 = li(t, "    SELECT course_id FROM"), li(t, "    LIMIT 1")
t.band(b0, b1, 2, BAND_IN)
o.append(t.html())
o.append(spot_rows(t, top_, top_, 1, x=t.x + 10, w=420))
o.append(spot_off(2))
o += tag(t, top_, "2번 강좌가 25건으로 가장 많아요", OR, 1, at=t.tx + t.sw("         2 |    25") + 10, gap=50)
o += tag(t, b1 - 1, "많은 순으로 세우고 LIMIT 1로 값 하나만 남겨요", OR, 2, gap=60)
o += tag(t, li(t, "수영 초급 저녁반"), "번호 대신 이름", GR, 3, gap=40)
W("r-pop", o, "두 번째 실제 상황이에요. 가장 인기 있는 강좌의 이름을 알고 싶어요. 먼저 신청 표에서 취소를 빼고 강좌별 신청 수를 세어 많은 순으로 세 개만 봤어요. 2번 강좌가 25건이에요. 그런데 신청 표에는 강좌 번호만 있고 이름이 없어요. 그래서 이 쿼리에 LIMIT 1을 붙여 번호 하나만 남기고, course_id = 뒤의 서브쿼리로 넣었어요. ORDER BY와 LIMIT을 쓴 서브쿼리도 1줄 1칸이면 등호 뒤에 둘 수 있어요. 결과는 수영 초급 저녁반이에요. 1등이 두 강좌로 같으면 LIMIT 1은 그중 하나만 남기니, 그럴 때는 숫자를 먼저 확인해요." + REAL)

# ---------- real case 3: text members who skipped November ----------
o = frame("r-sms", EB6, "실제 상황 3 · 11월에 신청하지 않은 회원에게 문자를 보내요", C6)
L = P("r-sms")
t = PT(L, 96, 214, size=28, w=1160, lh=1.5, tid="t-rsms", maxb=990)
b0, b1 = li(t, "    SELECT member_id FROM"), li(t, "    WHERE enroll_month")
t.band(b0, b1, 1, BAND_IN)
o.append(t.html())
o += tag(t, b1, "11월 신청자 목록", OR, 1, gap=40)
o.append(rbox(t, li(t, "AND phone IS NOT NULL"), "AND phone IS NOT NULL", 2, "#9DC1E6"))
o += tag(t, li(t, "AND phone IS NOT NULL"), "번호 없는 회원 빼기", BL, 2, gap=40)
# message cards
names = [l.split("|") for l in L if "| 010-" in l]
MX = 1320
o.append(p(f"position:absolute;left:{MX}px;top:226px;font-size:26px;font-weight:700;color:{GRAY}", "보낼 문자", bi("rise", 3)))
for k, (nm, ph) in enumerate(names):
    y = 280 + k * 150
    o.append(f'<div{bi("rise", 3)}{DELAY(k * 90)} style="position:absolute;left:{MX}px;top:{y}px;width:504px;height:124px;background:#FFFFFF;border:2px solid {LINE};border-radius:18px;box-shadow:0 6px 16px rgba(29,35,48,.08)"></div>')
    o.append(p(f"position:absolute;left:{MX + 26}px;top:{y + 18}px;font-family:{MONO};font-size:24px;font-weight:700;color:{INK};white-space:nowrap", e(ph.strip()), bi("rise", 3) + DELAY(k * 90)))
    o.append(p(f"position:absolute;left:{MX + 26}px;top:{y + 62}px;width:460px;font-size:23px;color:{SUB};white-space:nowrap", f"{e(nm.strip())} 회원님, 12월 강좌 신청이 열렸어요", bi("rise", 3) + DELAY(k * 90)))
o.append(caption("8명 중 전화번호가 있는 3명만 남았어요. NOT IN 목록에는 빈 값이 없는 member_id를 썼어요.", t.y + t.h + 34, 4, size=26, width=1160))
W("r-sms", o, "세 번째 실제 상황이에요. 11월에 아무 강좌도 신청하지 않은 회원에게 12월 강좌 안내 문자를 보내려고 해요. 괄호 안이 11월 신청자 목록이고, NOT IN으로 그 목록에 없는 회원을 골라요. 2파트에서 본 8명이에요. 문자를 보내려면 전화번호가 있어야 하니 AND phone IS NOT NULL을 붙였어요. 36에서 배운 IS NOT NULL이에요. 8명 중 전화번호가 있는 3명이 남았어요. 오른쪽은 이 결과로 만든 문자 예시예요." + REAL)

# =====================================================================
# wrap-up
# =====================================================================
o = frame("sum", "정리", "원하는 것이 값인지, 목록인지, 표인지 먼저 정해요", INK)
rows_ = [["평균, 최댓값 하나와 비교해요", kw("WHERE fee > (SELECT AVG(fee) FROM courses)", C1)],
         ["어떤 목록에 들어 있는지(없는지) 물어요", kw("WHERE member_id IN (SELECT member_id FROM …)", C2)],
         ["묶은 결과를 다시 거르거나 계산하거나 JOIN해요", kw("FROM (SELECT … GROUP BY …) AS paid", C3)],
         ["모든 줄 옆에 전체 값을 붙여요", kw("(SELECT ROUND(AVG(fee), 2) FROM courses) AS 전체평균", C4)]]
tb, y0 = table(96, 220, ["이럴 때", "이렇게 써요"], rows_, [700, 1028], "sum-tb", size=26, rh=100, order=1, stagger=True, bold_first=False)
o += tb
steps_ = ["안쪽 SELECT만 따로 쳐서 결과 모양을 봐요", "모양에 맞는 자리에 괄호로 감싸 넣어요", "FROM 자리면 AS 이름을 붙여요"]
yy = y0 + 4 * 100 + 50
o.append(p(f"position:absolute;left:96px;top:{yy}px;font-size:26px;font-weight:700;color:{GRAY}", "쓰는 순서", bi("rise", 5)))
for k, s_ in enumerate(steps_):
    x = 96 + k * 590
    o.append(p(f"position:absolute;left:{x}px;top:{yy + 50}px;width:44px;height:44px;border-radius:22px;background:{INK};text-align:center;font-size:24px;font-weight:700;line-height:44px;color:#FFFFFF", str(k + 1), bi("rise", 5) + DELAY(k * 80)))
    o.append(p(f"position:absolute;left:{x + 60}px;top:{yy + 54}px;width:500px;font-size:25px;line-height:1.45;color:{INK}", e(s_), bi("rise", 5) + DELAY(k * 80)))
W("sum", o, "서브쿼리를 쓸지 정할 때는 원하는 것이 값인지, 목록인지, 표인지부터 생각해요. 평균이나 최댓값 하나와 비교하면 WHERE 비교 기호 뒤에 둬요. 어떤 목록에 들어 있는지 물으면 IN, 없는지 물으면 NOT IN이에요. 묶은 결과를 다시 거르거나 계산하거나 다른 표와 JOIN하면 FROM 자리에 두고 이름을 붙여요. 모든 줄 옆에 전체 값을 붙이려면 SELECT 칸에 둬요. 쓰는 순서는 세 단계예요. 안쪽 SELECT만 따로 쳐서 결과 모양을 보고, 모양에 맞는 자리에 괄호로 감싸 넣고, FROM 자리면 AS 이름을 붙여요.", ("outro", "정리"))

o = frame("cheat", "정리", "한 장 요약", INK)
groups = [("값 하나", C1, [("WHERE fee > (SELECT AVG(fee) FROM courses)", "평균보다 비싼 강좌"), ("WHERE fee = (SELECT MAX(fee) FROM courses)", "가장 비싼 강좌"), ("(SELECT COUNT(*) FROM members) AS 전체", "SELECT 칸, 모든 줄에 같은 값")]),
          ("목록", C2, [("WHERE member_id IN (SELECT member_id FROM …)", "목록에 있는 회원"), ("WHERE member_id NOT IN (SELECT …)", "목록에 없는 회원"), ("같은 결과: JOIN … ON …", "두 표의 열을 같이 볼 때")]),
          ("표", C3, [("FROM (SELECT … GROUP BY …) AS paid", "임시 표에 이름 붙이기"), ("WHERE paid.total_paid >= 600000", "합계로 거르기"), ("SELECT AVG(total_paid) FROM (…) AS paid", "집계를 두 번")])]
GW = 560
for i, (t_, c, rows) in enumerate(groups):
    x = 96 + i * (GW + 24)
    o.append(p(f"position:absolute;left:{x}px;top:220px;font-size:30px;font-weight:700;color:{c}", e(t_)))
    o.append(f'<div style="position:absolute;left:{x}px;top:270px;width:{GW}px;height:3px;background:{c}"></div>')
    for j, (k_, d_) in enumerate(rows):
        y = 300 + j * 120
        fs = 20 if tw(k_, 20) < GW - 10 else 18
        if tw(k_, fs) > GW - 4:
            WARN.append(f"cheat: '{k_}' too wide")
        o.append(p(f"position:absolute;left:{x}px;top:{y}px;width:{GW}px;font-family:{MONO};font-size:{fs}px;font-weight:700;color:{INK};white-space:nowrap", e(k_)))
        o.append(p(f"position:absolute;left:{x}px;top:{y + 42}px;width:{GW}px;font-size:23px;color:{SUB}", e(d_)))
o.append(f'<div style="position:absolute;left:96px;top:690px;width:1728px;height:2px;background:{LINE}"></div>')
o.append(p(f"position:absolute;left:96px;top:716px;font-size:26px;font-weight:700;color:{RED}", "막히면"))
errs = [("more than one row …", "= 대신 IN"), ("must return only one column", "열 하나만"), ("not allowed in WHERE", "HAVING이나 FROM 서브쿼리"), ('missing FROM-clause entry', "AS 이름 붙이기")]
for k, (a_, b_) in enumerate(errs):
    x = 96 + (k % 2) * 864
    y = 770 + (k // 2) * 90
    o.append(p(f"position:absolute;left:{x}px;top:{y}px;width:840px;font-family:{MONO};font-size:22px;font-weight:700;color:{RED};white-space:nowrap", e(a_)))
    o.append(p(f"position:absolute;left:{x}px;top:{y + 38}px;width:840px;font-size:23px;color:{SUB}", e(b_)))
W("cheat", o, "오늘 쓴 것을 결과 모양 세 가지로 모았어요. 값 하나가 나오는 서브쿼리는 WHERE의 비교 기호 뒤나 SELECT 칸에 둬요. 목록이 나오는 서브쿼리는 IN, NOT IN 괄호 안에 둬요. 두 표의 열을 같이 봐야 하면 JOIN으로 바꿔요. 표가 나오는 서브쿼리는 FROM 자리에 두고 AS로 이름을 붙여요. 합계로 거르거나 합계의 평균처럼 집계를 두 번 할 때 써요. 아래는 자주 만나는 오류와 고치는 법이에요. 막히면 안쪽 SELECT만 따로 쳐서 모양부터 봐요.")

# =====================================================================
# toc
# =====================================================================
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
PL = [(C1, EB1[3:], "WHERE 열 > (서브쿼리), = (MAX), 안쪽 WHERE, 강좌가 늘면 다시 계산", "w-max", "w-auto"),
      (C2, EB2[3:], "= 와 여러 줄 오류, IN (서브쿼리), NOT IN, JOIN과 비교", "i-err", "i-join"),
      (C3, EB3[3:], "WHERE에 SUM 오류, FROM (서브쿼리) AS paid, JOIN, HAVING과 비교, 합계의 평균", "f-err", "f-avg"),
      (C4, EB4[3:], "스칼라 서브쿼리, 전체평균과 차이, 비율, 열 두 개 오류", "s-col", "s-err"),
      (C5, EB5[3:], "파이썬 두 줄과 비교, 넣는 자리 네 곳, EXPLAIN ANALYZE (참고)", "c-python", "explain"),
      (C6, EB6[3:], "오류 여섯 가지, 괄호와 AS, 남은 자리, 인기 강좌, 문자 보낼 회원", "x-table", "r-sms")]
o = frame("toc", "", "오늘의 순서", INK)
for i, (c, h, s_, a, b) in enumerate(PL):
    y = 214 + i * 112
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:2px;background:{LINE}"></div>')
    o.append(p(f"position:absolute;left:96px;top:{y + 22}px;width:80px;font-size:48px;font-weight:900;line-height:1.5;color:{c}", str(i + 1)))
    o.append(p(f"position:absolute;left:190px;top:{y + 18}px;font-size:34px;font-weight:700;color:{INK}", e(h)))
    o.append(p(f"position:absolute;left:190px;top:{y + 70}px;font-size:22px;color:{SUB};white-space:nowrap", e(s_)))
    o.append(p(f"position:absolute;left:1524px;top:{y + 40}px;width:300px;text-align:right;font-size:28px;font-weight:700;color:{GRAY}", f"{page[a]}–{page[b]}쪽"))
o.append(f'<div style="position:absolute;left:96px;top:{214 + len(PL) * 112}px;width:1728px;height:2px;background:{LINE}"></div>')
o.append(p(f"position:absolute;left:96px;top:{214 + len(PL) * 112 + 34}px;font-size:26px;color:{SUB}", f"{page['why']}–{page['min']}쪽은 들어가기, {page['sum']}–{page['cheat']}쪽은 정리예요. 예제는 38부터 쓰는 스포츠 센터 수업 데이터예요."))
o = [x for x in o if 'id="eyebrow"' not in x]
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(o) + f"\n<aside>{e('여섯 파트로 나눴어요. 1파트는 값 하나가 나오는 서브쿼리를 WHERE에서 비교해요. 2파트는 목록이 나오는 서브쿼리를 IN에 넣어요. 3파트는 표가 나오는 서브쿼리를 FROM에 두고 이름을 붙여요. 4파트는 SELECT 칸에 값을 넣어요. 5파트는 파이썬과 비교하고, EXPLAIN ANALYZE로 실행 순서를 읽어 봐요. 6파트는 오류와 실제 상황 예제예요.')}</aside>\n</section>\n")

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-18T00:00:00Z"}, "lists": "css", "title": "SQL 6 (서브쿼리)", "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
for w_ in WARN:
    print("WARN", w_)
print(len(ORDER), "slides")
