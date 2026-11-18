r"""Generates every slide of the SQL 3 deck (38) and slides/deck.json.

Story: 36 picked rows with WHERE and sorted them; class 2026-11-18 mixed AND and OR, labelled rows with CASE and sorted
by several keys. The deck opens on the class question that went wrong without parentheses, loads the shared class
database (../sports.sql: sports, instructors, courses, members, enrollments), then part 1 mixes AND, OR, parentheses
and NOT, part 2 builds CASE WHEN ... THEN ... ELSE ... END AS, part 3 sorts by several keys, ORDER BY CASE and NULLS
LAST, part 4 shows errors (END, types, AS name in WHERE, Hangul collation), part 5 three real situations.
Aggregates, GROUP BY, JOIN and subqueries stay out (39 to 41).

Every terminal line comes from tools/demo.py (real Docker and postgres:18 = PostgreSQL 18.7, in tools/out.json).
Usage (in 38-sql-case): python3 tools/gen.py slides
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
# chapter 38 helpers
# =====================================================================
VO = OR
MY = PG
EB1, EB2, EB3, EB4, EB5 = "1. 조건 섞기", "2. CASE로 값 붙이기", "3. 여러 기준으로 줄 세우기", "4. 자주 나는 오류와 함정", "5. 실제 상황 예제"
C1, C2, C3, C4, C5 = BL, TEAL, GR, RED, MAG
KS = D["tables"][0]["cmd"]
SQLKW = re.compile(r"\b(SELECT|FROM|WHERE|AND|OR|NOT|IN|LIKE|BETWEEN|CASE|WHEN|THEN|ELSE|END|AS|ORDER BY|DESC|ASC|NULLS LAST|NULLS FIRST|IS NOT NULL|IS NULL|COLLATE)\b")


def sqlhl(s, kw=PG):
    """light-card SQL colors: keywords bold blue, 'strings' green, numbers orange"""
    out, pos = "", 0
    for m in re.finditer(r"'[^']*'|\b\d+\b|\b(?:SELECT|FROM|WHERE|AND|OR|NOT|IN|LIKE|BETWEEN|CASE|WHEN|THEN|ELSE|END|AS|ORDER BY|DESC|ASC|NULLS LAST|NULLS FIRST|IS NOT NULL|IS NULL|COLLATE)\b", s):
        out += e(s[pos:m.start()])
        t_ = m.group(0)
        if t_.startswith("'"):
            out += f'<span style="color:{GR}">{e(t_)}</span>'
        elif t_[0].isdigit():
            out += f'<span style="color:{OR}">{e(t_)}</span>'
        else:
            out += f'<span style="color:{kw}">{e(t_)}</span>'
        pos = m.end()
    out += e(s[pos:])
    return out.replace("  ", " &#160;") or "&#160;"


def sqlcard(cid, x, y, w, lines, size=26, attrs="", lh=1.55, pad=(22, 30), raw=False, border=LINE):
    """a light code card; returns html and a geometry dict with line tops"""
    lp = round(size * lh)
    h = 2 * pad[0] + len(lines) * lp
    body = "".join(p(f"height:{lp}px;font-family:{MONO};font-size:{size}px;font-weight:700;line-height:{lp}px;white-space:pre;color:{INK}",
                     l if raw else sqlhl(l)) for l in lines)
    for i, l in enumerate(lines):
        if x + pad[1] + tw(re.sub(r"<[^>]+>", "", l), size) > x + w - 10:
            WARN.append(f"{cid}: line {i} runs past the card")
    if y + h > 1000:
        WARN.append(f"{cid}: card bottom {y + h}")
    html_ = (f'<div id="{cid}"{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{CARD};border:2px solid {border};'
             f'border-radius:16px;padding:{pad[0]}px {pad[1]}px;box-shadow:0 6px 18px rgba(29,35,48,.06)">{body}</div>')
    return html_, {"x": x, "y": y, "w": w, "h": h, "lp": lp, "top": lambda i: y + 2 + pad[0] + i * lp, "tx": x + 2 + pad[1], "size": size}


def cband(g, i, j=None, order=None, color=BL, attrs="", alpha="1A"):
    """a band behind lines i..j of a sqlcard (drawn before the card text by z-order: put it after, it is translucent)"""
    j = i if j is None else j
    return f'<div{bi("fade", order)}{attrs} style="position:absolute;left:{g["x"] + 8}px;top:{g["top"](i) - 2:.0f}px;width:{g["w"] - 16}px;height:{(j - i + 1) * g["lp"] + 4:.0f}px;background:{color}{alpha};border-left:6px solid {color};border-radius:6px"></div>'


def out_rows(lines):
    """only what psql printed: drop the prompt lines and trailing blanks"""
    res = [l for l in lines if not PROMPT_RE.match(l)]
    while res and not res[-1].strip():
        res.pop()
    while res and not res[0].strip():
        res = res[1:]
    return res


def chip(x, y, text, color, order=None, size=24, bg=None, border=None, attrs="", anim="pop", mono_=False, w=None):
    ww = f"width:{w}px;text-align:center;" if w else ""
    ff = f"font-family:{MONO};" if mono_ else ""
    return p(f"position:absolute;left:{x:.0f}px;top:{y:.0f}px;{ww}height:{size + 22}px;padding:0 16px;border-radius:10px;background:{bg or '#FFFFFF'};border:2px solid {border or color};{ff}font-size:{size}px;font-weight:700;line-height:{size + 18}px;color:{color};white-space:nowrap", e(text), bi(anim, order) + attrs)


def bignum(x, y, text, color, order=None, size=72, attrs=""):
    return p(f"position:absolute;left:{x:.0f}px;top:{y:.0f}px;font-size:{size}px;font-weight:900;line-height:1.1;color:{color};white-space:nowrap", text, bi("pop", order) + attrs)


def rowi(lines, name, start=0):
    """index of the psql row whose first column is name"""
    return next(i for i, l in enumerate(lines) if i >= start and l.startswith(" " + name + " ") or (i >= start and l.startswith(" " + name + "|")))


ROW_OK, ROW_BAD, ROW_HI, ROW_GRAY = "rgba(127,209,139,.20)", "rgba(255,156,148,.20)", "rgba(242,196,109,.20)", "rgba(157,193,230,.16)"


# =====================================================================
# cover
# =====================================================================
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px">',
       p("position:absolute;left:128px;top:300px;font-size:28px;font-weight:700;color:#9DC1E6", "KANT AX/AI 엔지니어 트랙 · 38"),
       f'<h1{SLAM(1)} style="position:absolute;left:128px;top:350px;padding-bottom:14px;font-size:100px;font-weight:900;line-height:1.3;color:#F6F5F1">SQL 3</h1>',
       p("position:absolute;left:128px;top:500px;font-size:52px;font-weight:700;line-height:1.3;color:#F6F5F1", "조건을 섞고<br>CASE로 등급 붙이기"),
       p("position:absolute;left:128px;top:680px;font-size:30px;line-height:1.5;color:#BFC6D4", "PostgreSQL · AND와 OR와 괄호, NOT,<br>CASE WHEN, 여러 기준 정렬, NULL 자리")]
cl = Q("case3")
t = term_q(cl, 1000, 200, size=19, w=824, tid="cov-term", lh=1.5)
cov.append(t.html())
cov.append(shine(2, "cov-term"))
W("cover", cov, "38 챕터는 SQL 3이에요. 36에서 WHERE로 줄을 고르고 ORDER BY로 세웠어요. 오늘은 조건 여러 개를 섞을 때 괄호가 왜 필요한지 보고, CASE로 줄마다 할인이나 청소년 같은 등급을 붙이고, 기준 여러 개로 줄을 세워요. 오른쪽은 마포구 회원에게 요금 등급을 붙인 화면이에요. 예제는 수업에서 쓴 체육 센터 데이터베이스예요." + REAL, ("intro", "들어가기"))

ORDER.append("toc")   # written last, after page numbers are known

# =====================================================================
# why
# =====================================================================
o = frame("why", "들어가기", "수영 강좌만 물었는데 헬스와 요가가 섞여 나왔어요", INK)
o.append(f'<div id="ask" style="position:absolute;left:96px;top:214px;width:540px;height:236px;background:{CARD};border:2px solid {LINE};border-radius:22px;box-shadow:{SHADOW}">'
         + p(f"position:absolute;left:32px;top:26px;font-size:24px;font-weight:700;color:{GRAY}", "회원 문의")
         + p(f"position:absolute;left:32px;top:72px;width:480px;font-size:32px;font-weight:700;line-height:1.45;color:{INK}", "수영 강좌 중에 초급이거나<br>아침 9시 전에 시작하는 반<br>있어요?") + '</div>')
wl = Q("noparen")
t = term_q(wl, 690, 214, size=22, tid="t-why", lh=1.6)
for nm in ("헬스 PT 입문", "아침 요가", "테니스 중급 레슨"):
    t.band(rowi(wl, nm), order=1, color=ROW_BAD)
o.append(t.html())
o += tag(t, rowi(wl, "아침 요가"), "수영(sport_id 1)이 아닌데 나왔어요", RED, 1)
o.append(hbox(t, at(wl, "(7 rows)"), "(7 rows)", RED, 2, which="box", pad=8))
o.append(hd(96, 500, "기대한 답은 수영 강좌 4개예요", GR, 28, 2))
for k, nm in enumerate(["수영 초급 아침반", "수영 초급 저녁반", "수영 중급 새벽반", "아쿠아로빅"]):
    o.append(chip(96, 556 + k * 70, nm, GR, None, 26, attrs=bi("pop", 2) + DELAY(120 + k * 80)))
o.append(caption("AND와 OR를 섞으면 PostgreSQL이 먼저 묶는 쪽이 정해져 있어요. 1파트에서 괄호로 바로잡아요.", 900, 3, size=28))
W("why", o, "수영 강좌만 물었는데 헬스와 요가가 섞여 나왔어요. 회원이 수영 강좌 중에 초급이거나 아침 9시 전에 시작하는 반을 물었어요. 36에서 배운 AND와 OR로 조건을 한 줄에 적었더니 7줄이 나왔어요. 그런데 헬스 PT 입문, 아침 요가, 테니스 중급 레슨은 수영이 아니에요. 기대한 답은 왼쪽의 수영 강좌 4개예요. SQL은 오류 없이 다른 답을 줬어요. AND와 OR를 섞으면 PostgreSQL이 먼저 묶는 쪽이 정해져 있기 때문이에요. 오늘 첫 파트에서 이걸 괄호로 바로잡아요." + REAL)

# =====================================================================
# big picture
# =====================================================================
o = frame("big", "들어가기", "SELECT 한 문장 안에서 오늘 배울 곳은 세 군데예요", INK)
big_sql = ["SELECT name, birth_year,",
           "       CASE WHEN birth_year <= 1960 THEN '할인'",
           "            ELSE '청소년' END AS 안내",
           "FROM members",
           "WHERE (birth_year <= 1960 OR birth_year >= 2000)",
           "  AND phone IS NOT NULL",
           "ORDER BY birth_year DESC, name;"]
h_, g = sqlcard("big-sql", 96, 214, 1000, big_sql, size=28, lh=1.75)
o.append(h_)
bands = [(4, 5, C1, "1파트 · 조건 섞기", "AND, OR, 괄호, NOT"), (1, 2, C2, "2파트 · CASE", "조건에 따라 값을 붙인 새 열"), (6, 6, C3, "3파트 · 줄 세우기", "기준 여러 개, NULL 자리")]
for k, (i, j, col, lab, sub) in enumerate(bands):
    od = k + 1
    o.append(cband(g, i, j, od, col, DIM("bigb")))
    ym = (g["top"](i) + g["top"](j) + g["lp"]) / 2
    o += leader(g["x"] + g["w"] + 8, ym, 1150, col, od, f'<span>{e(lab)}</span> <span style="font-weight:400;color:{SUB};font-size:23px;margin-left:10px">{e(sub)}</span>', None, 27)
FY = 750
o.append(hd(96, FY, "PostgreSQL은 이 순서로 처리해요", GRAY, 26, 4))
steps = [("FROM", "표 고르기"), ("WHERE", "줄 거르기"), ("SELECT", "열 만들기 (CASE)"), ("ORDER BY", "줄 세우기")]
SX, SW, SG = 96, 380, 69
for k, (kw, ko) in enumerate(steps):
    x = SX + k * (SW + SG)
    o.append(f'<div id="flow{k}"{bi("rise", 4)}{DELAY(k * 90)} style="position:absolute;left:{x}px;top:{FY + 52}px;width:{SW}px;height:104px;background:{CARD};border:2px solid {LINE};border-radius:16px">'
             + p(f"position:absolute;left:24px;top:14px;font-family:{MONO};font-size:30px;font-weight:700;color:{PG}", kw)
             + p(f"position:absolute;left:24px;top:58px;font-size:24px;color:{SUB};white-space:nowrap", e(ko)) + '</div>')
    if k < 3:
        o.append(harrow(x + SW + 10, x + SW + SG - 12, FY + 104, GRAY, 4))
o.append(note(96, FY + 186, 1728, "적는 순서와 처리 순서가 달라요. WHERE가 SELECT보다 먼저라서 생기는 오류를 4파트에서 봐요.", SUB, 26, 5))
W("big", o, "SELECT 한 문장 안에서 오늘 배울 곳은 세 군데예요. 1파트는 WHERE 자리예요. AND와 OR를 섞고, 괄호로 순서를 정하고, NOT으로 뒤집어요. 2파트는 SELECT 자리의 CASE예요. 줄마다 조건을 따져서 할인이나 청소년 같은 값을 붙인 새 열을 만들어요. 3파트는 ORDER BY 자리예요. 기준을 여러 개 적고, 비어 있는 NULL이 어디에 설지 정해요. 아래는 PostgreSQL이 이 문장을 처리하는 순서예요. 적을 때는 SELECT가 맨 앞이지만, 실제로는 FROM으로 표를 고르고 WHERE로 줄을 거른 뒤 SELECT에서 열을 만들고 마지막에 줄을 세워요. 이 순서는 4파트의 오류 하나를 이해할 때 다시 써요.")

# =====================================================================
# setup: load the class tables
# =====================================================================
o = frame("s-load", "들어가기", "수업 예제 표 다섯 개를 kant_shop에 넣어요", PG)
ld = ["$ " + D["load"][0]["cmd"]] + R("load", 0) + ["$ " + D["load"][1]["cmd"]] + R("load", 1)
t = term_q(ld, 96, 214, size=20, tid="t-load", lh=1.5)
o.append(t.html())
o += tag(t, 0, "35에서 배운 docker cp", GRAY, 1)
o.append(hbox(t, 2, "-f /tmp/sports.sql", PG, 1))
i_n = at(ld, "NOTICE")
o += tag(t, i_n + 5, "위 NOTICE는 지울 표가 없다는 알림", GRAY, 2)
i_c = at(ld, "INSERT 0 14")
o += tag(t, i_c, "courses 14줄, 다음 줄 members 40줄", C1, 3)
RX = t.x + t.w + 56
tabs = [("sports", "종목", "5", GRAY), ("instructors", "강사", "8", GRAY), ("courses", "강좌", "14", C1), ("members", "회원", "40", C2), ("enrollments", "수강 신청", "187", GRAY)]
o.append(hd(RX, 214, "들어간 표", GRAY, 24, 3))
for k, (nm, ko, n, col) in enumerate(tabs):
    y = 262 + k * 112
    main_ = col != GRAY
    o.append(f'<div{bi("rise", 3)}{DELAY(k * 80)} style="position:absolute;left:{RX}px;top:{y}px;width:{1824 - RX}px;height:98px;background:{CARD};border:{3 if main_ else 2}px solid {col if main_ else LINE};border-radius:16px">'
             + p(f"position:absolute;left:24px;top:12px;font-family:{MONO};font-size:27px;font-weight:700;color:{col if main_ else INK}", nm)
             + p(f"position:absolute;left:24px;top:52px;font-size:22px;color:{SUB};white-space:nowrap", f"{ko} {n}줄" + (" · 오늘 써요" if main_ else ""))
             + '</div>')
o.append(note(RX, 262 + 5 * 112 + 8, 1824 - RX, "sports.sql은 38-sql-case 폴더에 있어요. 39~41도 이 표를 그대로 써요.", SUB, 23, 4))
W("s-load", o, "수업 예제 표 다섯 개를 kant_shop에 넣어요. 36, 37처럼 35 수업의 my-pg 컨테이너와 kant_shop 데이터베이스를 그대로 써요. 레포 38-sql-case 폴더의 sports.sql을 받아서 그 폴더에서 docker cp로 컨테이너 안 tmp 폴더에 복사해요. 그다음 psql의 -f 옵션으로 파일 안의 SQL을 한 번에 실행해요. 35에서 배운 방법이에요. 처음이라 지울 표가 없다는 NOTICE가 다섯 줄 나오고, 표 다섯 개가 만들어져요. 오늘은 강좌 표 courses와 회원 표 members를 써요. 39부터 41까지도 이 표를 그대로 써요." + REAL)

# =====================================================================
# setup: courses
# =====================================================================
o = frame("s-courses", "들어가기", "courses 표에는 종목, 난이도, 시작 시각, 수강료가 있어요", PG)
cs = Q("tables", 1)
t = term_q(cs, 96, 214, size=21, tid="t-courses", lh=1.5)
for nm in ("1 | 수영 초급 아침반", "5 | 아쿠아로빅"):
    pass
i1 = at(cs, "수영 초급 아침반")
t.band(i1, i1 + 4, order=1, color=ROW_GRAY, attrs=DIM("csb"))
o.append(t.html())
hdr = at(cs, "course_id |")
o.append(hbox(t, hdr, "level", OR, 2))
o.append(hbox(t, hdr, "start_time", OR, 3))
o.append(hbox(t, hdr, "fee", OR, 4))
RX = t.x + t.w + 56
notes_ = [("sport_id 1은 수영", "1번부터 5번까지 다섯 강좌예요", 1),
          ("level", "초급, 중급, 고급 세 가지 글자", 2),
          ("start_time", "TIME 자료형. '09:00'처럼 작은따옴표로 비교해요", 3),
          ("fee", "원 단위 정수", 4)]
for k, (h1, s1, od) in enumerate(notes_):
    y = 240 + k * 160
    o.append(p(f"position:absolute;left:{RX}px;top:{y}px;font-family:{MONO if k else SANS};font-size:28px;font-weight:700;color:{OR if k else INK};white-space:nowrap", e(h1), bi("rise", od) + DIM("csn")))
    o.append(note(RX, y + 46, 1824 - RX, e(s1), SUB, 24, od, DIM("csn2")))
W("s-courses", o, "courses 표에는 종목, 난이도, 시작 시각, 수강료가 있어요. 강좌가 14개예요. sport_id는 종목 번호인데 1번이 수영이에요. 위의 다섯 줄이 수영 강좌예요. level은 초급, 중급, 고급 셋 중 하나를 글자로 적었어요. start_time은 36에서 본 TIME 자료형이에요. 06:30처럼 시와 분으로 적혀 있고, 비교할 때는 작은따옴표로 '09:00'처럼 적어요. fee는 수강료이고 원 단위 정수예요. 오늘 예제는 대부분 이 표와 회원 표에서 나와요." + REAL)

# =====================================================================
# part 1: AND / OR, truth
# =====================================================================
o = frame("a-truth", EB1, "조건은 줄마다 참(t)이나 거짓(f)으로 따져요", C1)
tr_ = Q("truth")
t = term_q(tr_, 96, 214, size=20, tid="t-truth", lh=1.5)
o.append(t.html())
o.append(hbox(t, 0, "level = '초급' AS 초급", OR, None))
o.append(hbox(t, 0, "start_time < '09:00' AS 아침", OR, None))
rows_ = [(l.split("|")[0].strip(), l.split("|")[1].strip(), l.split("|")[2].strip()) for l in out_rows(tr_)[2:-1]]
GX, GY = 96, t.y + t.h + 44
cols_ = [("강좌", 380, INK), ("초급", 150, INK), ("아침", 150, INK), ("초급 OR 아침", 330, C1), ("초급 AND 아침", 330, C2)]
RH = 58
gw = sum(c[1] for c in cols_)
o.append(f'<div style="position:absolute;left:{GX}px;top:{GY}px;width:{gw}px;height:{RH * (len(rows_) + 1)}px;background:{CARD};border:2px solid #CFCAC0;border-radius:14px;overflow:hidden"></div>')
o.append(f'<div style="position:absolute;left:{GX + 2}px;top:{GY + 2}px;width:{gw - 4}px;height:{RH - 2}px;background:#EEF0F3;border-radius:12px 12px 0 0"></div>')
cx = GX
for j, (cn, cw, cc) in enumerate(cols_):
    od = {3: 1, 4: 2}.get(j)
    o.append(p(f"position:absolute;left:{cx}px;top:{GY + 12}px;width:{cw}px;text-align:center;font-family:{MONO if j in (3, 4) else SANS};font-size:24px;font-weight:700;line-height:1.4;color:{cc};white-space:nowrap", e(cn), bi("rise", od) if od else ""))
    cx += cw
for i, (nm, a, b) in enumerate(rows_):
    y = GY + RH * (i + 1)
    o.append(rule(GX + 2, y, gw - 4, "#E2DED5"))
    orv = "t" if (a == "t" or b == "t") else "f"
    andv = "t" if (a == "t" and b == "t") else "f"
    vals = [nm, a, b, orv, andv]
    cx = GX
    for j, v in enumerate(vals):
        cw = cols_[j][1]
        if j == 0:
            o.append(p(f"position:absolute;left:{cx + 24}px;top:{y + 12}px;font-size:24px;font-weight:700;color:{INK};white-space:nowrap", e(v)))
        else:
            good = v == "t"
            colv = (C1 if j == 3 else C2 if j == 4 else GR) if good else GRAY
            bgv = (f"{colv}1F") if good else "#F1F0EC"
            od = {3: 1, 4: 2}.get(j)
            attrs = (bi("pop", od) + DELAY(i * 90)) if od else ""
            o.append(p(f"position:absolute;left:{cx + cw / 2 - 30:.0f}px;top:{y + 9}px;width:60px;height:40px;border-radius:10px;background:{bgv};text-align:center;font-family:{MONO};font-size:26px;font-weight:700;line-height:40px;color:{colv}", v, attrs))
        cx += cw
RX = GX + gw + 50
o.append(note(RX, GY + 70, 1824 - RX, "OR는 하나만 t여도 t예요.", C1, 28, 1))
o.append(note(RX, GY + 180, 1824 - RX, "AND는 둘 다 t일 때만 t예요.", C2, 28, 2))
W("a-truth", o, "조건은 줄마다 참이나 거짓으로 따져요. 위 SELECT는 조건을 WHERE에 넣지 않고 열 자리에 적었어요. 그러면 PostgreSQL이 줄마다 조건이 맞는지 t나 f로 보여 줘요. t는 참, f는 거짓이에요. 36에서 본 BOOLEAN 표시와 같아요. 아래 표는 이 결과로 OR와 AND를 계산한 거예요. OR는 둘 중 하나만 t여도 t라서 수영 고급반 빼고 모두 t예요. AND는 둘 다 t일 때만 t라서 수영 초급 아침반 하나만 t예요. WHERE는 이 값이 t인 줄만 남겨요." + REAL)

# =====================================================================
# part 1: AND first
# =====================================================================
o = frame("a-noparen", EB1, "괄호가 없으면 AND를 먼저 묶어요", C1)
T = lambda k, s, c=INK: tok(k, e(s), f"color:{c}")


def mcard(cid, y, toks, w, attrs="", size=34, x=96, h=96):
    return (f'<div id="{cid}"{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{CARD};border:2px solid {LINE};border-radius:16px;'
            f'padding:0 34px;font-family:{MONO};font-size:{size}px;font-weight:700;line-height:{h - 4}px;color:{INK};white-space:pre">{toks}</div>')


o.append(hd(96, 214, "12에서 본 계산 순서", GRAY, 24))
m0 = T("a", "2 + ") + T("b", "3 × 4") + T("c", " = 14", GRAY)
m1 = T("a", "2 + ") + T("p1", "(", OR) + T("b", "3 × 4") + T("p2", ")", OR) + T("c", " = 14", GRAY)
o.append(mcard("m-from", 256, m0, 560, MORPH_FROM()))
o.append(mcard("m-to", 256, m1, 560, MORPH(1, "m-from")))
o.append(note(700, 276, 1100, "곱셈을 먼저 하듯, SQL은 AND를 먼저 묶어요.", INK, 28, 1))
o.append(hd(96, 392, "PostgreSQL이 읽는 모양", GRAY, 24, 2))
s0 = T("w", "WHERE ") + T("a", "sport_id = 1 AND level = '초급'") + T("o", " OR ", RED) + T("b", "start_time < '09:00'")
s1 = T("w", "WHERE ") + T("p1", "(", OR) + T("a", "sport_id = 1 AND level = '초급'") + T("p2", ")", OR) + T("o", " OR ", RED) + T("b", "start_time < '09:00'")
o.append(mcard("s-from", 434, s0, 1728, MORPH_FROM() + bi("rise", 2), size=30))
o.append(mcard("s-to", 434, s1, 1728, MORPH(3, "s-from"), size=30))
GY = 580
grpA = ["수영 초급 아침반", "수영 초급 저녁반", "아쿠아로빅"]
grpB = ["수영 초급 아침반", "수영 중급 새벽반", "헬스 PT 입문", "아침 요가", "테니스 중급 레슨"]
o.append(hd(96, GY, "괄호 안 · 수영이면서 초급", OR, 26, 4))
o.append(hd(960, GY, "OR 오른쪽 · 종목 상관없이 9시 전", RED, 26, 4))
for k, nm in enumerate(grpA):
    o.append(chip(96 + (k % 2) * 380, GY + 52 + (k // 2) * 70, nm, OR, None, 25, attrs=bi("pop", 4) + DELAY(k * 70), w=340))
for k, nm in enumerate(grpB):
    bad = nm not in grpA and not nm.startswith("수영")
    o.append(chip(960 + (k % 2) * 400, GY + 52 + (k // 2) * 70, nm, RED if bad else INK, None, 25, attrs=bi("pop", 4) + DELAY(200 + k * 70), w=360, bg="#FBEDEC" if bad else None, border=RED if bad else "#CFCAC0"))
o.append(caption("두 묶음을 OR로 합쳐서 7줄이에요. 수영 초급 아침반은 양쪽에 있지만 한 번만 나와요.", GY + 52 + 3 * 70 + 40, 5, size=28))
W("a-noparen", o, "괄호가 없으면 AND를 먼저 묶어요. 12에서 2 더하기 3 곱하기 4를 계산할 때 곱셈을 먼저 해서 14가 나왔어요. SQL에서는 AND가 곱셈처럼 먼저 묶여요. 그래서 처음 친 WHERE는 수영이면서 초급인 강좌, 또는 종목에 상관없이 9시 전에 시작하는 강좌라는 뜻이 돼요. 왼쪽 묶음이 수영 초급 세 개, 오른쪽 묶음이 9시 전 다섯 개예요. 오른쪽에 헬스, 요가, 테니스가 들어 있어요. 두 묶음을 OR로 합치면 7줄이에요. 수영 초급 아침반은 양쪽에 다 있지만 한 줄로만 나와요.")

# =====================================================================
# part 1: parentheses
# =====================================================================
o = frame("a-paren", EB1, "OR를 괄호로 묶으면 수영 안에서만 골라요", C1)
po = Q("paren-or")
t = term_q(po, 96, 214, size=24, tid="t-paren", lh=1.6)
for i in range(at(po, "수영 초급 아침반"), at(po, "(4 rows)")):
    t.band(i, order=3, color=ROW_OK)
o.append(t.html())
o.append(hbox(t, at(po, "AND (level"), "(level = '초급' OR start_time < '09:00')", OR, 1, which="box"))
o += tag(t, at(po, "(4 rows)"), "기대한 답 4개", GR, 3)
RX = t.x + t.w + 70
fun = [("courses", "14개", INK, 1), ("WHERE sport_id = 1", "5개", C1, 2), ("AND (초급 OR 9시 전)", "4개", GR, 3)]
for k, (lab, n, col, od) in enumerate(fun):
    y = 230 + k * 210
    wbox = 1824 - RX - k * 60
    o.append(f'<div{bi("rise", od)} style="position:absolute;left:{RX + k * 30}px;top:{y}px;width:{wbox}px;height:130px;background:{CARD};border:3px solid {col};border-radius:20px">'
             + p(f"position:absolute;left:28px;top:20px;font-family:{MONO};font-size:{26 if k else 30}px;font-weight:700;color:{col};white-space:nowrap", e(lab))
             + p(f"position:absolute;left:28px;top:66px;font-size:36px;font-weight:900;color:{INK}", n) + '</div>')
    if k < 2:
        o.append(svg(arrow_path(f"M{RX + (1824 - RX) / 2:.0f},{y + 140} L{RX + (1824 - RX) / 2:.0f},{y + 196}", GRAY, 4) + head_at(RX + (1824 - RX) / 2, y + 198, 90, GRAY), od + 1))
o.append(note(RX, 230 + 3 * 210 - 20, 1824 - RX, "수영 고급반만 빠져요. 고급이고 저녁 8시라 둘 다 아니에요.", SUB, 25, 3))
W("a-paren", o, "OR를 괄호로 묶으면 수영 안에서만 골라요. 괄호 안은 먼저 계산돼요. 초급이거나 9시 전인지를 먼저 따지고, 그 결과를 sport_id = 1과 AND로 이어요. 오른쪽 그림처럼 강좌 14개에서 수영 5개를 먼저 남기고, 그 5개 중에서 초급이거나 9시 전인 4개를 남겨요. 수영 고급반은 고급이고 저녁 8시에 시작해서 빠져요. 이게 회원이 물어본 답이에요. 12의 계산처럼 괄호가 먼저예요. AND와 OR를 섞을 때는 헷갈리지 않게 늘 괄호를 쳐요." + REAL)

# =====================================================================
# part 1: OR vs AND inside
# =====================================================================
o = frame("a-and", EB1, "괄호 안을 AND로 바꾸면 둘 다 맞는 1줄만 남아요", C1)
pa = Q("paren-and")
t = term_q(pa, 96, 214, size=24, tid="t-and", lh=1.6)
t.band(at(pa, "수영 초급 아침반"), order=1, color=ROW_OK)
o.append(t.html())
o.append(hbox(t, at(pa, "AND (level"), "AND start_time", C2, 1))
BY = t.y + t.h + 50
o.append(hd(96, BY, "같은 질문, WHERE만 다르게", GRAY, 24, 2))
bars = [("sport_id = 1 AND level = '초급' OR start_time < '09:00'", 7, RED, "괄호 없음"),
        ("sport_id = 1 AND (level = '초급' OR start_time < '09:00')", 4, C1, "OR를 괄호로"),
        ("sport_id = 1 AND (level = '초급' AND start_time < '09:00')", 1, C2, "AND를 괄호로")]
for k, (sq, n, col, lab) in enumerate(bars):
    y = BY + 50 + k * 92
    o.append(p(f"position:absolute;left:96px;top:{y + 4}px;width:220px;font-size:24px;font-weight:700;color:{col};white-space:nowrap", e(lab), bi("rise", 2) + DELAY(k * 100)))
    o.append(p(f"position:absolute;left:300px;top:{y + 6}px;font-family:{MONO};font-size:21px;font-weight:700;color:{INK};white-space:nowrap", sqlhl(sq), bi("rise", 2) + DELAY(k * 100)))
    bx = 1180
    o.append(f'<div{WIPE(3)}{DELAY(k * 160)} style="position:absolute;left:{bx}px;top:{y}px;width:{n * 76}px;height:44px;border-radius:10px;background:{col}"></div>')
    o.append(p(f"position:absolute;left:{bx + n * 76 + 16}px;top:{y + 2}px;font-size:28px;font-weight:900;color:{col};white-space:nowrap", f"{n}줄", bi("rise", 3) + DELAY(k * 160 + 200)))
RX = t.x + t.w + 60
o.append(f'<div{bi("rise", 4)} style="position:absolute;left:{RX}px;top:{t.y}px;width:{1824 - RX}px;height:{t.h}px;box-sizing:border-box;background:{CARD};border:2px solid {LINE};border-radius:16px;padding:32px 40px;display:flex;flex-direction:column;justify-content:center">'
         + p(f"font-size:27px;font-weight:700;color:{C2};margin-bottom:18px", "AND끼리만 이을 때")
         + p(f"font-size:25px;line-height:1.55;color:{INK};margin-bottom:22px", "괄호가 있어도 없어도 결과가 같아요.")
         + p(f"font-size:27px;font-weight:700;color:{RED};margin-bottom:18px", "OR가 하나라도 섞이면")
         + p(f"font-size:25px;line-height:1.55;color:{INK}", "어느 쪽을 먼저 묶을지 괄호로 적어요.") + '</div>')
W("a-and", o, "괄호 안을 AND로 바꾸면 둘 다 맞는 1줄만 남아요. 이번에는 초급이면서 9시 전인 수영 강좌를 찾았어요. 수영 초급 아침반 하나만 나와요. 아래는 지금까지 친 세 문장을 나란히 놓은 거예요. 괄호가 없으면 7줄, OR를 괄호로 묶으면 4줄, AND를 괄호로 묶으면 1줄이에요. 글자 몇 개 차이로 결과가 크게 달라져요. OR는 고를 줄을 늘리고, AND는 줄여요. 사실 AND끼리만 이을 때는 괄호가 없어도 결과가 같아요. 그래도 OR가 하나라도 섞이면 괄호부터 쳐요." + REAL)

# =====================================================================
# part 1: NOT
# =====================================================================
o = frame("a-not", EB1, "NOT은 조건을 뒤집어요", C1)
nt = [l for l in Q("not") if l.strip()]
t = term_q(nt, 96, 214, size=20, tid="t-not", lh=1.5)
o.append(t.html())
o.append(hbox(t, at(nt, "NOT IN"), "NOT IN ('초급', '중급')", OR, 1))
o.append(hbox(t, at(nt, "NOT LIKE"), "NOT LIKE '%초급%'", OR, 2))
i3 = at(nt, "AND NOT (")
o.append(hbox(t, i3, "NOT (level = '초급' OR start_time < '09:00')", RED, 3, which="box"))
RX = t.x + t.w + 60
o.append(hd(RX, 222, "수영 강좌 5개", GRAY, 24, 3))
swim = [("수영 초급 아침반", True), ("수영 초급 저녁반", True), ("수영 중급 새벽반", True), ("아쿠아로빅", True), ("수영 고급반", False)]
for k, (nm, inside) in enumerate(swim):
    y = 270 + k * 74
    o.append(chip(RX, y, nm, GRAY if inside else RED, None, 24, attrs=bi("pop", 3) + DELAY(k * 60), w=1824 - RX - 36, bg="#F1F0EC" if inside else "#FBEDEC", border="#D6D2C8" if inside else RED))
o.append(note(RX, 270 + 5 * 74 + 14, 1824 - RX, "괄호 안에 맞는 4개를 빼고 남은 1개예요. 앞 장 4줄의 반대쪽이에요.", INK, 24, 3))
W("a-not", o, "NOT은 조건을 뒤집어요. 36에서 배운 IN, LIKE 앞에 NOT을 붙이면 반대가 돼요. 첫 문장은 초급도 중급도 아닌 강좌라서 고급 두 개가 나와요. 두 번째는 이름에 초급이 들어가지 않은 수영 강좌예요. BETWEEN에도 NOT BETWEEN처럼 붙여요. 세 번째는 괄호 앞에 NOT을 붙였어요. 괄호 안의 조건이 맞는 줄을 모두 빼고 나머지를 골라요. 앞 장에서 4줄이 나온 조건을 뒤집었더니 남은 수영 고급반 하나만 나왔어요. 오른쪽 그림이 그 관계예요." + REAL)

# =====================================================================
# part 2: CASE, two ways
# =====================================================================
o = frame("c-two", EB2, "CASE는 줄마다 조건을 따져서 값 하나를 새 열로 붙여요", C2, )
c2 = Q("case2")
t = term_q(c2, 96, 214, size=22, tid="t-case2", lh=1.6)  # right: question flow
hi = at(c2, "| 가격대")
o.append(t.html())
o.append(hbox(t, at(c2, "CASE WHEN"), "CASE WHEN fee >= 100000 THEN '고가' ELSE '일반' END AS 가격대", C2, 1, which="box"))
o += tag(t, hi, "새로 생긴 열", C2, 2, at=t.sx(hi, "가격대") + t.sw("가격대"))
o.append(hbox(t, at(c2, "테니스 입문"), "일반", OR, 2, which="box", pad=6))
RX = t.x + t.w + 60
RW = 1824 - RX
o.append(hd(RX, t.y + 8, "줄마다 이렇게 물어요", GRAY, 24, 3))
o.append(chip(RX, t.y + 62, "fee >= 100000 ?", OR, 3, 26, mono_=True, w=RW - 36, bg="#FFF6E8"))
for k, (ans, val, col) in enumerate([("예", "'고가'", GR), ("아니요", "'일반'", SUB)]):
    y = t.y + 170 + k * 96
    o.append(p(f"position:absolute;left:{RX}px;top:{y + 6}px;width:110px;font-size:25px;font-weight:700;color:{col};white-space:nowrap", ans, bi("rise", 4) + DELAY(k * 120)))
    o.append(harrow(RX + 110, RX + 210, y + 24, col, 4, 4))
    o.append(chip(RX + 228, y, val, col, 4, 26, mono_=True, attrs=DELAY(k * 120 + 80)))
o.append(note(RX, t.y + 390, RW, "다섯 줄 모두 이 질문을 거쳐서 가격대 칸이 채워져요.", SUB, 23, 5))
PY = t.y + t.h + 44
o.append(hd(96, PY, "17의 한 줄 if와 같은 모양이에요", GRAY, 24, 3))
py_ = (f'<span style="color:{GRAY}">label = </span><span {MARK(3)} style="color:{GR}">"고가"</span> if <span {MARK(3)} style="color:{OR}">fee &gt;= 100000</span> else <span {MARK(3)} style="color:{SUB}">"일반"</span>')
sq_ = (f'CASE WHEN <span {MARK(3)} style="color:{OR}">fee &gt;= 100000</span> THEN <span {MARK(3)} style="color:{GR}">\'고가\'</span> ELSE <span {MARK(3)} style="color:{SUB}">\'일반\'</span> END')
o.append(p(f"position:absolute;left:96px;top:{PY + 48}px;width:150px;font-size:24px;font-weight:700;color:{GRAY}", "파이썬", bi("rise", 3)))
o.append(p(f"position:absolute;left:250px;top:{PY + 44}px;font-family:{MONO};font-size:28px;font-weight:700;color:{INK};white-space:pre", py_, bi("rise", 3)))
o.append(p(f"position:absolute;left:96px;top:{PY + 108}px;width:150px;font-size:24px;font-weight:700;color:{GRAY}", "SQL", bi("rise", 3)))
o.append(p(f"position:absolute;left:250px;top:{PY + 104}px;font-family:{MONO};font-size:28px;font-weight:700;color:{PG};white-space:pre", sq_, bi("rise", 3)))
W("c-two", o, "CASE는 줄마다 조건을 따져서 값 하나를 새 열로 붙여요. 헬스와 테니스 강좌에 가격대를 붙였어요. 수강료가 10만 원 이상이면 고가, 아니면 일반이에요. CASE부터 END까지가 한 덩어리이고, AS로 가격대라는 열 이름을 붙였어요. 표에 없던 가격대 열이 결과에 생겼어요. 테니스 입문만 9만 원이라 일반이에요. 표 자체는 바뀌지 않고 보여 줄 때만 붙여요. 아래는 17에서 배운 한 줄 if와 나란히 놓은 거예요. 같은 색끼리 짝이에요. 파이썬은 참일 때 값을 앞에 적고, SQL은 WHEN 조건 뒤 THEN에 적어요." + REAL)

# =====================================================================
# part 2: anatomy
# =====================================================================
o = frame("c-parts", EB2, "CASE 한 덩어리는 여섯 조각으로 읽어요", C2)
segs = [("CASE", PG, "시작"), ("WHEN fee >= 100000", OR, "이 조건이 참이면"), ("THEN '고가'", GR, "이 값"), ("ELSE '일반'", GRAY, "모두 아니면 이 값"), ("END", PG, "끝"), ("AS 가격대", C2, "열 이름")]
SZ = 46
x0, y0 = 96, 250
cx = x0
spans = []
for k, (s_, col, lab) in enumerate(segs):
    w = tw(s_, SZ)
    spans.append(f'<span style="color:{col}">{e(s_)}</span>')
    mid = cx + w / 2
    low = k % 2 == 1
    drop = 90 if low else 30
    od = k + 1 if k < 4 else 4
    o.append(f'<div{bi("fade", od)} style="position:absolute;left:{mid - 1:.0f}px;top:{y0 + SZ * 1.3 + 6:.0f}px;width:2px;height:{drop}px;background:{col}"></div>')
    lw_ = tw(lab, 26, mono=False) + 20
    o.append(p(f"position:absolute;left:{mid - lw_ / 2:.0f}px;top:{y0 + SZ * 1.3 + drop + 14:.0f}px;width:{lw_:.0f}px;text-align:center;font-size:26px;font-weight:700;line-height:1.35;color:{col};white-space:nowrap", e(lab), bi("pop", od)))
    cx += w + tw(" ", SZ)
o.insert(len(o) - 2 * len(segs), p(f"position:absolute;left:{x0}px;top:{y0}px;font-family:{MONO};font-size:{SZ}px;font-weight:700;line-height:1.3;white-space:pre", " ".join(spans)))
CY = 540
o.append(hd(96, CY, "줄을 나눠 적어도 같아요", GRAY, 24, 5))
h_, g = sqlcard("parts-ml", 96, CY + 48, 900, ["CASE WHEN fee >= 100000 THEN '고가'", "     ELSE '일반'", "END AS 가격대"], size=30, attrs=bi("rise", 5))
o.append(h_)
RX = 1060
o.append(note(RX, CY + 56, 1824 - RX, "WHEN ... THEN ...은 여러 번 적을 수 있어요. 다음 장에서 봐요.", INK, 27, 5))
o.append(note(RX, CY + 190, 1824 - RX, "END를 빼면 오류가 나요. ELSE를 빼면 빈칸이 생겨요.", SUB, 25, 5))
W("c-parts", o, "CASE 한 덩어리는 여섯 조각으로 읽어요. CASE로 시작해요. WHEN 뒤에는 WHERE에 쓰던 조건을 그대로 적어요. 그 조건이 참이면 THEN 뒤의 값을 써요. 어느 조건에도 안 맞으면 ELSE 뒤의 값을 써요. END로 덩어리를 닫고, AS로 결과 열의 이름을 붙여요. 아래처럼 줄을 나눠 적어도 PostgreSQL은 똑같이 읽어요. 조건이 많아지면 이렇게 나눠 적는 게 읽기 편해요. WHEN과 THEN 짝은 여러 번 적을 수 있어요. END를 빼면 오류, ELSE를 빼면 빈칸이 생기는데, 둘 다 뒤에서 실제로 봐요.")

# =====================================================================
# part 2: many WHENs
# =====================================================================


def gate_grid(x, y, conds, people, order0, w=None, colw=None):
    """conds: header labels; people: (name, year, [cell...], result, color) cells are 예/아니요/안 봐요"""
    o_ = []
    colw = colw or [220] + [220] * len(conds) + [180]
    W_ = sum(colw)
    RH_ = 74
    o_.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:{W_}px;height:{RH_ * (len(people) + 1)}px;background:{CARD};border:2px solid #CFCAC0;border-radius:14px"></div>')
    o_.append(f'<div style="position:absolute;left:{x + 2}px;top:{y + 2}px;width:{W_ - 4}px;height:{RH_ - 2}px;background:#EEF0F3;border-radius:12px 12px 0 0"></div>')
    heads = ["회원"] + conds + ["요금"]
    cx_ = x
    for j, hname in enumerate(heads):
        o_.append(p(f"position:absolute;left:{cx_}px;top:{y + 20}px;width:{colw[j]}px;text-align:center;font-family:{MONO if 0 < j < len(heads) - 1 else SANS};font-size:22px;font-weight:700;line-height:1.4;color:{INK};white-space:nowrap", e(hname)))
        cx_ += colw[j]
    for i, (nm, yr, cells_, res, rc) in enumerate(people):
        yy = y + RH_ * (i + 1)
        od = order0 + i
        o_.append(rule(x + 2, yy, W_ - 4, "#E2DED5"))
        o_.append(p(f"position:absolute;left:{x + 20}px;top:{yy + 8}px;font-size:24px;font-weight:700;color:{INK};white-space:nowrap", e(nm), bi("rise", od)))
        o_.append(p(f"position:absolute;left:{x + 20}px;top:{yy + 40}px;font-family:{MONO};font-size:18px;color:{GRAY};white-space:nowrap", e(yr), bi("rise", od)))
        cx_ = x + colw[0]
        for j, c_ in enumerate(cells_):
            col = {"예": GR, "아니요": RED, "안 봐요": GRAY}[c_]
            bg = {"예": "#E4F3EA", "아니요": "#FBEDEC", "안 봐요": "#F1F0EC"}[c_]
            ww = tw(c_, 22, mono=False) + 30
            o_.append(p(f"position:absolute;left:{cx_ + colw[j + 1] / 2 - ww / 2:.0f}px;top:{yy + 16}px;width:{ww:.0f}px;height:42px;border-radius:10px;background:{bg};text-align:center;font-size:22px;font-weight:700;line-height:42px;color:{col}", e(c_), bi("pop", od) + DELAY(j * 160)))
            cx_ += colw[j + 1]
        ww = tw(res, 24, mono=False) + 34
        o_.append(p(f"position:absolute;left:{cx_ + colw[-1] / 2 - ww / 2:.0f}px;top:{yy + 15}px;width:{ww:.0f}px;height:44px;border-radius:10px;background:{rc};text-align:center;font-size:24px;font-weight:700;line-height:44px;color:#FFFFFF", e(res), bi("pop", od) + DELAY(len(cells_) * 160)))
    return o_, W_


o = frame("c-many", EB2, "WHEN이 여러 개면 위에서부터 처음 맞는 하나만 골라요", C2)
c3 = Q("case3")
t = term_q(c3, 96, 206, size=19, tid="t-case3", lh=1.5)
rws = [("전소율", "1958년생", ["예", "안 봐요"], "할인", OR), ("고은채", "2000년생", ["아니요", "예"], "청소년", BL), ("최지아", "1975년생", ["아니요", "아니요"], "일반", GRAY)]
for k, (nm, *_r) in enumerate(rws):
    t.band(rowi(c3, nm), order=k + 1, color=ROW_HI, attrs=DIM("c3b"))
o.append(t.html())
RX = t.x + t.w + 50
g_, gw_ = gate_grid(RX, 214, ["<= 1960", ">= 2000"], rws, 1, colw=[200, 190, 190, 1824 - RX - 580])
o += g_
o.append(note(RX, 214 + 74 * 4 + 34, 1824 - RX, "위에서부터 따지다가 처음 예가 나오면 그 THEN 값을 쓰고 나머지 WHEN은 안 봐요. 17의 elif와 같아요.", INK, 25, 4))
W("c-many", o, "WHEN이 여러 개면 위에서부터 처음 맞는 하나만 골라요. 수업에서 본 요금 등급이에요. 1960년 이전에 태어났으면 할인, 2000년 이후면 청소년, 나머지는 일반이에요. 마포구 회원 11명에게 붙였어요. 오른쪽 표에서 세 사람을 따라가 봐요. 전소율은 1958년생이라 첫 WHEN에서 바로 예가 나와서 할인이에요. 두 번째 WHEN은 보지도 않아요. 고은채는 첫 WHEN이 아니요, 두 번째가 예라서 청소년이에요. 최지아는 둘 다 아니요라서 ELSE의 일반이에요. 17에서 배운 if, elif, else와 똑같이 움직여요." + REAL)

# =====================================================================
# part 2: WHEN order
# =====================================================================
o = frame("c-wrong", EB2, "넓은 조건을 먼저 쓰면 뒤의 WHEN까지 오지 않아요", C2)
cw = Q("case-wrong")
t = term_q(cw, 96, 206, size=19, tid="t-wrong", lh=1.5)
o.append(t.html())
o.append(hbox(t, at(cw, "birth_year < 2000"), "WHEN birth_year < 2000 THEN '일반'", RED, 1))
iw = rowi(cw, "전소율")
o.append(hbox(t, iw, "일반", RED, 2, which="box", pad=6))
o += tag(t, iw, "1958년생인데 일반", RED, 2)
RX = t.x + t.w + 50
g_, gw_ = gate_grid(RX, 214, ["< 2000", "<= 1960"], [("전소율", "1958년생", ["예", "안 봐요"], "일반", GRAY)], 3, colw=[200, 190, 190, 1824 - RX - 580])
o += g_
o.append(hd(RX, 214 + 74 * 2 + 40, "고치는 법", GR, 26, 4))
h_, g = sqlcard("fix-order", RX, 214 + 74 * 2 + 88, 1824 - RX, ["CASE WHEN birth_year <= 1960 THEN '할인'", "     WHEN birth_year < 2000 THEN '일반'", "     ELSE '청소년' END"], size=21, attrs=bi("rise", 4))
o.append(h_)
o.append(note(RX, 214 + 74 * 2 + 88 + g["h"] + 24, 1824 - RX, "좁은 조건부터 적어요.", INK, 25, 4))
W("c-wrong", o, "넓은 조건을 먼저 쓰면 뒤의 WHEN까지 오지 않아요. 이번에는 2000년보다 앞이면 일반이라는 조건을 맨 위에 적었어요. 1958년생 전소율도 2000년보다 앞이라 첫 WHEN에서 예가 나와요. 그래서 바로 일반이 되고, 할인을 주는 두 번째 WHEN은 보지도 않아요. 오류는 안 나고 결과만 틀려요. 이런 실수가 더 위험해요. 고칠 때는 범위가 좁은 조건부터 적어요. 1960년 이하를 먼저 묻고, 그다음에 2000년 미만을 물으면 할인 회원이 제대로 나와요." + REAL)

# =====================================================================
# part 2: no ELSE
# =====================================================================
o = frame("c-noelse", EB2, "ELSE를 빼면 어느 WHEN에도 안 맞는 줄은 빈칸(NULL)이에요", C2)
ce = Q("case-noelse")
t = term_q(ce, 96, 206, size=20, tid="t-noelse", lh=1.6)
i0 = rowi(ce, "최지아")
t.band(i0, i0 + 5, order=2, color="rgba(224,127,176,.18)")
o.append(t.html())
o.append(hbox(t, at(ce, "END AS"), "END AS 요금", RED, 1))
o += tag(t, at(ce, "END AS"), "ELSE 줄이 없어요", RED, 1)
o += tag(t, i0 + 2, "빈칸 = NULL", NL, 2, at=t.sx(i0 + 2, "|") + t.sw("|       1980 |") + 30)
RX = t.x + t.w + 60
o.append(f'<div{bi("pop", 2)} style="position:absolute;left:{RX}px;top:240px;width:150px;height:150px;border-radius:24px;background:{NLBG};border:3px dashed {NL};font-family:{MONO};font-size:64px;font-weight:700;line-height:144px;text-align:center;color:{NL}">?</div>')
o.append(note(RX + 180, 250, 1824 - RX - 180, "36에서 본 NULL(모름)이에요. 오류 없이 칸만 비어요.", INK, 25, 2))
o.append(note(RX, 460, 1824 - RX, "빈칸이 생기면 안 되는 열이면 ELSE를 꼭 적어요.", INK, 26, 3))
h_, g_ = sqlcard("noelse-fix", RX, 530, 1824 - RX, ["       WHEN birth_year >= 2000 THEN '청소년'", "       ELSE '일반'", "  END AS 요금"], size=24, attrs=bi("rise", 3))
o.append(h_)
o.append(cband(g_, 1, 1, 3, GR, DIM("noelse")))
o.append(note(RX, 530 + g_["h"] + 24, 1824 - RX, "이 한 줄이 있으면 여섯 명 모두 일반이 돼요.", SUB, 24, 3))
W("c-noelse", o, "ELSE를 빼면 어느 WHEN에도 안 맞는 줄은 빈칸이에요. 앞 장의 요금 CASE에서 ELSE 줄만 지웠어요. 할인과 청소년은 그대로 나오지만, 1975년생부터 1998년생까지 여섯 명은 요금 칸이 비었어요. 이 빈칸이 36에서 본 NULL이에요. PostgreSQL은 ELSE가 없으면 ELSE NULL로 읽어요. 오류가 나지 않아서 놓치기 쉬워요. 빈칸이 생기면 안 되는 열이면 ELSE를 꼭 적어요." + REAL)

# =====================================================================
# part 2: conditions inside WHEN
# =====================================================================
o = frame("c-null", EB2, "WHEN에는 IS NULL, AND, IN 같은 조건을 그대로 써요", C2)
cn = Q("case-null")
t = term_q(cn, 96, 206, size=19, tid="t-cnull", lh=1.5)
outs = out_rows(cn)
cat = {"이메일": (1, "rgba(127,209,139,.18)"), "문자": (2, "rgba(157,193,230,.20)"), "연락처 없음": (3, "rgba(255,156,148,.20)")}
for i, l in enumerate(cn):
    for k_, (od, colr) in cat.items():
        if l.rstrip().endswith("| " + k_):
            t.band(i, order=od, color=colr)
o.append(t.html())
RX = t.x + t.w + 56
leg = [("이메일", "email이 있으면", GR, 1), ("문자", "email은 없고 phone이 있으면", BL, 2), ("연락처 없음", "둘 다 비었으면 ELSE", RED, 3)]
for k, (nm, ds, col, od) in enumerate(leg):
    y = 230 + k * 170
    n = sum(1 for l in outs if l.rstrip().endswith("| " + nm))
    o.append(chip(RX, y, nm, col, od, 28))
    o.append(p(f"position:absolute;left:{RX + tw(nm, 28, mono=False) + 70:.0f}px;top:{y + 4}px;font-size:28px;font-weight:900;color:{col};white-space:nowrap", f"{n}명", bi("pop", od)))
    o.append(note(RX, y + 66, 1824 - RX, e(ds), SUB, 24, od))
o.append(note(RX, 760, 1824 - RX, "WHEN 순서가 곧 연락 우선순위예요.", INK, 26, 4))
W("c-null", o, "WHEN에는 IS NULL, AND, IN 같은 조건을 그대로 써요. 마포구 회원에게 연락할 방법을 정했어요. 이메일이 있으면 이메일, 이메일은 없지만 전화번호가 있으면 문자, 둘 다 없으면 연락처 없음이에요. 첫 WHEN은 email IS NOT NULL이에요. WHERE에서 쓰던 조건이 WHEN에도 그대로 들어가요. 최지아는 전화번호가 없어도 이메일이 있어서 이메일이에요. 임준서와 황민서는 둘 다 비어서 연락처 없음이에요. WHEN을 적은 순서가 곧 어떤 방법을 먼저 쓸지 정하는 순서예요." + REAL)

# =====================================================================
# part 2: computed value
# =====================================================================
o = frame("c-calc", EB2, "THEN 뒤에는 글자뿐 아니라 계산한 값도 와요", C2)
cc = Q("case-calc")
t = term_q(cc, 96, 206, size=21, tid="t-calc", lh=1.55)
for nm in ("수영 중급 새벽반", "수영 초급 아침반", "아침 요가"):
    t.band(rowi(cc, nm), order=1, color=ROW_HI)
o.append(t.html())
o.append(hbox(t, at(cc, "CASE WHEN"), "THEN fee - 10000 ELSE fee", OR, 1))
ia = rowi(cc, "아침 요가")
o += tag(t, ia, "9시 전이라 1만 원 할인", OR, 1)
io = at(cc, "ORDER BY 이번달")
o.append(hbox(t, io, "ORDER BY 이번달 DESC", C3, 2))
o += tag(t, io, "AS로 붙인 이름으로 세울 수 있어요", C3, 2)
o.append(caption("THEN과 ELSE 값이 모두 숫자라서 이번달 열도 숫자예요. 그래서 큰 값부터 세울 수 있어요.", t.y + t.h + 40, 3, size=28))
W("c-calc", o, "THEN 뒤에는 글자뿐 아니라 계산한 값도 와요. 이번 달에 아침 9시 전 강좌는 1만 원을 깎아 주기로 했어요. 시작 시각이 9시 전이면 fee에서 10000을 뺀 값을, 아니면 fee를 그대로 써요. 36에서 본 price 곱하기 3 같은 계산 열과 같아요. 새벽반, 아침반, 아침 요가 세 줄이 1만 원씩 줄었어요. 마지막 줄 ORDER BY에는 AS로 붙인 이번달이라는 이름을 그대로 썼어요. ORDER BY는 SELECT 다음에 처리되니까 새 이름을 알아요. THEN과 ELSE 값이 모두 숫자라 이번달 열도 숫자로 세워졌어요." + REAL)

# =====================================================================
# part 2: python if
# =====================================================================
o = frame("c-python", EB2, "17의 if, elif, else와 CASE를 나란히 놓아요", C2)
PYL = ["birth_year = 1958",
       f'<span {MARK(1)} style="color:{OR}">if</span> birth_year &lt;= 1960:',
       '    fee_type = "할인"',
       f'<span {MARK(2)} style="color:{BL}">elif</span> birth_year &gt;= 2000:',
       '    fee_type = "청소년"',
       f'<span {MARK(3)} style="color:{GRAY}">else</span>:',
       '    fee_type = "일반"',
       "print(fee_type)"]
h_, g = editor("py-ed", "main.py", PYL, 96, 214, 820, fs=27)
o.append(h_)
pt = Term([("$", "~", "uv run main.py"), ("o", "할인")], 96, 214 + g["h"] + 30, size=24, w=820, tid="t-py", lh=1.5)
o.append(pt.html())
SQ = [f'<span style="color:{PG}">SELECT</span> name, birth_year,',
      f'  <span style="color:{PG}">CASE</span> <span {MARK(1)} style="color:{OR}">WHEN</span> birth_year &lt;= 1960 <span style="color:{PG}">THEN</span> <span style="color:{GR}">\'할인\'</span>',
      f'       <span {MARK(2)} style="color:{BL}">WHEN</span> birth_year &gt;= 2000 <span style="color:{PG}">THEN</span> <span style="color:{GR}">\'청소년\'</span>',
      f'       <span {MARK(3)} style="color:{GRAY}">ELSE</span> <span style="color:{GR}">\'일반\'</span>',
      f'  <span style="color:{PG}">END AS</span> 요금',
      f'<span style="color:{PG}">FROM</span> members;']
h_, g2 = sqlcard("py-sql", 970, 214, 854, SQ, size=24, raw=True)
o.append(h_)
DY = 214 + g2["h"] + 40
diffs = [("파이썬 if", "값 하나를 한 번 따져요"), ("SQL CASE", "표의 줄마다 한 번씩 따져서 열 하나를 만들어요")]
for k, (a_, b_) in enumerate(diffs):
    y = DY + k * 92
    o.append(rule(970, y, 854, order=4))
    o.append(p(f"position:absolute;left:970px;top:{y + 24}px;font-size:26px;font-weight:700;color:{INK};white-space:nowrap", e(a_), bi("rise", 4) + DELAY(k * 100)))
    o.append(p(f"position:absolute;left:1180px;top:{y + 24}px;width:644px;font-size:25px;color:{SUB}", e(b_), bi("rise", 4) + DELAY(k * 100)))
o.append(rule(970, DY + 184, 854, order=4))
W("c-python", o, "17에서 배운 if, elif, else와 CASE를 나란히 놓아요. 같은 색끼리 짝이에요. 파이썬의 if가 첫 WHEN, elif가 두 번째 WHEN, else가 ELSE예요. 위에서부터 처음 맞는 하나만 고르는 것도 같아요. 다른 점은 아래 표예요. 파이썬 코드는 birth_year 값 하나를 한 번 따져서 할인을 출력해요. CASE는 members 표의 줄마다 한 번씩 따져서 요금 열을 통째로 만들어요. 그래서 CASE에는 END와 AS가 붙어요." + REAL.replace("터미널 출력은", "SQL 결과와 파이썬 출력은"))

# =====================================================================
# part 3: two keys
# =====================================================================
o = frame("o-two", EB3, "앞 기준이 같은 줄끼리만 뒤 기준으로 순서를 정해요", C3)
s2a = Q("sort-two", 0)
s2b = Q("sort-two", 1)
t1 = term_q(s2a, 96, 206, size=21, tid="t-two1", lh=1.5)
t2 = term_q(s2b, 96, 206 + t1.h + 28, size=21, tid="t-two2", lh=1.5)
for tt, ll in ((t1, s2a), (t2, s2b)):
    i_ = at(ll, "70000")
    tt.band(i_, i_ + 1, order=1, color=ROW_HI)
o.append(t1.html())
o.append(t2.html())
o.append(hbox(t1, 0, "fee DESC, course_name;", C3, 1))
o.append(hbox(t2, 0, "fee DESC, course_name DESC;", OR, 2))
i_ = at(s2a, "70000")
o += tag(t1, i_, "70000원끼리 이름순", C3, 1, at=t1.sx(i_, "70000") + t1.sw("70000"))
j_ = at(s2b, "70000")
o += tag(t2, j_, "이 두 줄만 자리가 바뀌어요", OR, 2, at=t2.sx(j_, "70000") + t2.sw("70000"))
W("o-two", o, "앞 기준이 같은 줄끼리만 뒤 기준으로 순서를 정해요. 36에서 기준 두 개로 세우는 법을 봤어요. 수영 강좌를 수강료가 비싼 것부터 세우고, 수강료가 같으면 이름순으로 세웠어요. 7만 원인 아침반과 저녁반이 이름순으로 섰어요. 아래는 뒤 기준에만 DESC를 붙인 거예요. 결과에서 바뀐 건 7만 원인 두 줄뿐이에요. 앞 기준인 수강료가 모두 다른 줄은 뒤 기준을 보지도 않아요. 뒤 기준은 앞 기준이 같은 줄끼리 순서를 정할 때만 써요." + REAL)

# =====================================================================
# part 3: each key has its own direction
# =====================================================================
o = frame("o-dir", EB3, "DESC는 바로 앞 기준 하나에만 붙어요", C3)
sd = Q("sort-dir")
t = term_q(sd, 96, 214, size=24, tid="t-dir", lh=1.6)
grp_ = {}
for i, l in enumerate(sd):
    m = re.search(r"\| (고급|중급|초급)\s+\|", l)
    if m:
        grp_.setdefault(m.group(1), []).append(i)
for k, (g_k, ix) in enumerate(grp_.items()):
    t.band(ix[0], ix[-1], order=1, color=ROW_OK if k % 2 == 0 else ROW_GRAY)
o.append(t.html())
o.append(hbox(t, 0, "ORDER BY level, fee DESC", C3, 1))
PY_ = t.y + t.h + 50
segs = [("ORDER BY", PG, None), ("level,", C3, "작은 것부터"), ("fee DESC", OR, "큰 것부터")]
o += parts(96, PY_, [(s_, c_, l_, None) for s_, c_, l_ in segs], size=40, order=2, lab=26, drop=30, lw=520)
RX = 1150
o.append(note(RX, PY_ - 4, 1824 - RX, "글자 기준은 가나다 순이라 고급, 중급, 초급(ㄱ, ㅈ, ㅊ) 순서로 서요.", INK, 26, 3))
o.append(note(RX, PY_ + 100, 1824 - RX, "초급끼리는 수강료가 큰 것부터 섰어요. 방향을 안 적은 level은 ASC예요.", SUB, 25, 3))
W("o-dir", o, "DESC는 바로 앞 기준 하나에만 붙어요. ORDER BY level, fee DESC는 level을 작은 것부터, fee를 큰 것부터 세워요. level 뒤에 아무것도 안 적으면 ASC로 읽어요. 그래서 level이 먼저 세워지고, 같은 level 안에서 fee가 큰 것부터 서요. 초급 세 줄이 7만, 7만, 6만 원 순서예요. 그런데 level이 고급, 중급, 초급 순서로 섰어요. 글자는 가나다 순으로 세우니까 고급의 ㄱ, 중급의 ㅈ, 초급의 ㅊ 순서예요. 난이도 순서로 세우려면 다음 장의 방법을 써요." + REAL)

# =====================================================================
# part 3: ORDER BY CASE
# =====================================================================
o = frame("o-case", EB3, "난이도 순서는 CASE로 번호를 매겨서 세워요", C3)
la = Q("sort-level", 0)
lb = Q("sort-level", 1)
ra, rb = out_rows(la), out_rows(lb)
h1, g1 = sqlcard("lv-a", 96, 214, 820, ["ORDER BY level, fee;"], size=24)
o.append(h1)
ta = term_q(ra, 96, 214 + g1["h"] + 16, size=21, w=820, tid="t-lva", lh=1.5, bar=False)
h2, g2 = sqlcard("lv-b", 1004, 214, 820, ["ORDER BY CASE WHEN level = '초급' THEN 1", "              WHEN level = '중급' THEN 2", "              ELSE 3 END, fee, course_name;"], size=22)
o.append(h2)
tb = term_q(rb, 1004, 214 + g2["h"] + 16, size=21, w=820, tid="t-lvb", lh=1.5, bar=False)
for tt, rr, od in ((ta, ra, 1), (tb, rb, 2)):
    for k, lv in enumerate(("고급", "중급", "초급")):
        ix = [i for i, l in enumerate(rr) if re.search(rf"\| {lv}\s+\|", l)]
        if ix:
            tt.band(ix[0], ix[-1], order=od, color=[ROW_BAD, ROW_HI, ROW_OK][k])
o.append(ta.html())
o.append(tb.html())
o.append(f'<div{bi("rise", 1)} style="position:absolute;left:96px;top:{ta.y + ta.h + 24}px;font-size:26px;font-weight:700;color:{RED}">가나다 순이라 고급이 맨 앞</div>')
o.append(f'<div{bi("rise", 2)} style="position:absolute;left:1004px;top:{tb.y + tb.h + 24}px;font-size:26px;font-weight:700;color:{GR}">초급 1, 중급 2, 고급 3 순서</div>')
W("o-case", o, "난이도 순서는 CASE로 번호를 매겨서 세워요. 수영과 테니스 강좌 8개를 세웠어요. 왼쪽처럼 level로 세우면 가나다 순이라 고급이 맨 앞에 와요. 오른쪽은 ORDER BY에 CASE를 적었어요. 초급이면 1, 중급이면 2, 나머지는 3이라는 번호를 줄마다 매기고 그 번호로 세워요. 번호는 화면에 나오지 않고 순서를 정할 때만 써요. 같은 난이도 안에서는 수강료, 그다음 이름 순서예요. CASE는 SELECT뿐 아니라 ORDER BY에도 쓸 수 있어요." + REAL)

# =====================================================================
# part 3: NULL is the largest
# =====================================================================
o = frame("o-null", EB3, "NULL은 가장 큰 값처럼 서요. DESC면 맨 앞이에요", C3)
na, nb = out_rows(Q("null-sort", 0)), out_rows(Q("null-sort", 1))
h1, g1 = sqlcard("nl-a", 96, 214, 820, ["... WHERE region = '구로구'", "ORDER BY email;"], size=24)
h2, g2 = sqlcard("nl-b", 1004, 214, 820, ["... WHERE region = '구로구'", "ORDER BY email DESC, name;"], size=24)
o += [h1, h2]
ta = term_q(na, 96, 214 + g1["h"] + 16, size=22, w=820, tid="t-nla", lh=1.5, bar=False)
tb = term_q(nb, 1004, 214 + g2["h"] + 16, size=22, w=820, tid="t-nlb", lh=1.5, bar=False)
ia_ = [i for i, l in enumerate(na) if l.rstrip().endswith("|")]
ib_ = [i for i, l in enumerate(nb) if l.rstrip().endswith("|")]
ta.band(ia_[0], ia_[-1], order=1, color="rgba(224,127,176,.20)")
tb.band(ib_[0], ib_[-1], order=2, color="rgba(224,127,176,.20)")
o += [ta.html(), tb.html()]
o += tag(ta, ia_[0], "빈 이메일은 맨 뒤", NL, 1, at=ta.sx(ia_[0], "|") + 40)
o += tag(tb, ib_[0], "DESC면 맨 앞", NL, 2, at=tb.sx(ib_[0], "|") + 40)
LY = ta.y + ta.h + 70
o.append(f'<div{WIPE(3)} style="position:absolute;left:96px;top:{LY + 30}px;width:1640px;height:4px;background:{GRAY}"></div>')
o.append(svg(head_at(1744, LY + 32, 0, GRAY), 3))
pts = [("user01", 160), ("user06", 420), ("user13", 680), ("user34", 1000)]
for k, (lab, x) in enumerate(pts):
    o.append(f'<div{bi("pop", 3)}{DELAY(200 + k * 80)} style="position:absolute;left:{x - 9}px;top:{LY + 23}px;width:18px;height:18px;border-radius:9px;background:{BL}"></div>')
    o.append(p(f"position:absolute;left:{x - 60}px;top:{LY + 54}px;width:120px;text-align:center;font-family:{MONO};font-size:22px;font-weight:700;color:{BL}", lab, bi("pop", 3) + DELAY(200 + k * 80)))
o.append(p(f"position:absolute;left:1500px;top:{LY + 4}px;width:120px;height:56px;border-radius:14px;background:{NLBG};border:3px dashed {NL};text-align:center;font-family:{MONO};font-size:24px;font-weight:700;line-height:50px;color:{NL}", "NULL", bi("pop", 3) + DELAY(600)))
o.append(p(f"position:absolute;left:96px;top:{LY - 34}px;font-size:23px;color:{SUB}", "작은 값", bi("rise", 3)))
o.append(p(f"position:absolute;left:1640px;top:{LY - 34}px;font-size:23px;color:{SUB}", "큰 값", bi("rise", 3)))
W("o-null", o, "NULL은 가장 큰 값처럼 서요. DESC면 맨 앞이에요. 구로구 회원을 이메일 순서로 세웠어요. 이메일이 비어 있는 박도현과 양다인이 맨 뒤에 섰어요. 수업 코드처럼 DESC로 큰 것부터 세우면 이 두 사람이 맨 앞에 와요. PostgreSQL은 NULL을 어떤 값보다 큰 값처럼 다뤄요. 아래 그림의 오른쪽 끝에 NULL이 있다고 생각하면 돼요. 36에서 가격이 NULL인 상품이 DESC 맨 앞에 왔던 것과 같은 이유예요. 이메일이 있는 회원부터 보고 싶다면 이 순서가 불편해요. 다음 장에서 고쳐요." + REAL)

# =====================================================================
# part 3: NULLS LAST / FIRST
# =====================================================================
o = frame("o-nulls", EB3, "NULLS LAST, NULLS FIRST로 빈칸이 설 자리를 정해요", C3)
na, nb = out_rows(Q("nulls-last", 0)), out_rows(Q("nulls-last", 1))
h1, g1 = sqlcard("ns-a", 96, 214, 820, ["ORDER BY email DESC NULLS LAST, name;"], size=24)
h2, g2 = sqlcard("ns-b", 1004, 214, 820, ["ORDER BY email NULLS FIRST, name;"], size=24)
o += [h1, h2]
ta = term_q(na, 96, 214 + g1["h"] + 16, size=22, w=820, tid="t-nsa", lh=1.5, bar=False)
tb = term_q(nb, 1004, 214 + g2["h"] + 16, size=22, w=820, tid="t-nsb", lh=1.5, bar=False)
ia_ = [i for i, l in enumerate(na) if l.rstrip().endswith("|")]
ib_ = [i for i, l in enumerate(nb) if l.rstrip().endswith("|")]
ta.band(ia_[0], ia_[-1], order=1, color="rgba(224,127,176,.20)")
tb.band(ib_[0], ib_[-1], order=2, color="rgba(224,127,176,.20)")
o += [ta.html(), tb.html()]
o.append(underline(1, 96 + 30 + tw("ORDER BY email DESC ", 24), 96 + 30 + tw("ORDER BY email DESC NULLS LAST", 24), 214 + g1["h"] - 18, C3))
o.append(underline(2, 1004 + 30 + tw("ORDER BY email ", 24), 1004 + 30 + tw("ORDER BY email NULLS FIRST", 24), 214 + g2["h"] - 18, C3))
o.append(caption("NULLS LAST는 DESC여도 빈칸을 맨 뒤로, NULLS FIRST는 ASC여도 맨 앞으로 보내요. 붙이는 자리는 그 기준 바로 뒤예요.", ta.y + ta.h + 44, 3, size=28))
W("o-nulls", o, "NULLS LAST, NULLS FIRST로 빈칸이 설 자리를 정해요. 왼쪽은 email DESC 뒤에 NULLS LAST를 붙였어요. 큰 것부터 세우지만 NULL만은 맨 뒤로 가요. 이메일이 있는 다섯 명이 먼저 나와요. 오른쪽은 반대로 작은 것부터 세우면서 NULLS FIRST로 빈칸을 맨 앞에 뒀어요. 이메일을 아직 안 받은 회원부터 챙길 때 써요. NULLS LAST, NULLS FIRST는 그 기준 바로 뒤에 붙이고, 뒤에 오는 name 기준에는 영향이 없어요." + REAL)

# =====================================================================
# part 4: errors
# =====================================================================
o = frame("x-end", EB4, "END를 빼면 AS 앞에서 syntax error가 나요", C4)
xe = Q("x-end")
t = term_q(xe, 96, 214, size=22, tid="t-xend", lh=1.6)
o.append(t.html())
ic = at(xe, "^")
o.append(ring(1, round(t.sx(ic, "^") - 22), round(t.top(ic) - 6), 60, round(t.lp + 12), RED))
o.append(hbox(t, at(xe, "ERROR"), "syntax error at or near \"AS\"", RED, 1))
FY = t.y + t.h + 60
o.append(hd(96, FY, "고친 줄", GR, 26, 2))
f0 = T("a", "CASE WHEN birth_year <= 1960 THEN '할인' ELSE '일반'") + T("b", " AS 요금")
f1 = T("a", "CASE WHEN birth_year <= 1960 THEN '할인' ELSE '일반'") + T("e", " END", GR) + T("b", " AS 요금")
o.append(mcard("xe-from", FY + 50, f0, 1728, MORPH_FROM() + bi("rise", 2), size=30))
o.append(mcard("xe-to", FY + 50, f1, 1728, MORPH(3, "xe-from"), size=30))
o.append(note(96, FY + 180, 1728, "화살표(^)는 PostgreSQL이 이상하다고 느낀 자리예요. 빠진 END는 그 바로 앞에 넣어요.", SUB, 25, 3))
W("x-end", o, "END를 빼면 AS 앞에서 syntax error가 나요. CASE를 열었으면 END로 닫아야 해요. END 없이 AS를 적으면 PostgreSQL은 CASE 안에 AS가 왜 있는지 몰라서 AS 근처가 이상하다고 알려 줘요. 오류 아래 화살표가 AS를 가리켜요. 화살표는 PostgreSQL이 이상하다고 느낀 자리예요. 실수는 그 바로 앞에 있을 때가 많아요. ELSE 값 뒤, AS 앞에 END를 넣으면 돼요." + REAL)

o = frame("x-type", EB4, "THEN과 ELSE 값은 같은 자료형이어야 해요", C4)
xt = Q("x-type")
t = term_q(xt, 96, 214, size=22, tid="t-xtype", lh=1.55)
o.append(t.html())
i_e = at(xt, "ELSE 0")
o.append(hbox(t, i_e, "THEN '고가' ELSE 0", RED, 1, which="box"))
o.append(hbox(t, at(xt, "ERROR"), "invalid input syntax for type integer: \"고가\"", RED, 2))
i_f = at(xt, "ELSE '-'")
o.append(hbox(t, i_f, "ELSE '-'", GR, 3, which="box"))
o += tag(t, at(xt, "헬스 PT 입문"), "THEN, ELSE 둘 다 글자라 통과", GR, 3)
o.append(caption("한 열에는 한 자료형만 담겨요. 숫자 0을 '0'처럼 작은따옴표로 감싸도 돼요.", t.y + t.h + 40, 3, size=28))
W("x-type", o, "THEN과 ELSE 값은 같은 자료형이어야 해요. 고가 아니면 0을 적었더니 오류가 났어요. 결과는 열 하나라서 한 가지 자료형만 담을 수 있어요. PostgreSQL은 숫자 0을 보고 이 열을 정수 열로 정한 뒤, 고가라는 글자를 정수로 바꾸려다 실패했어요. 그래서 integer에 고가를 넣을 수 없다는 오류예요. 36에서 본 invalid input syntax와 같은 오류예요. ELSE에도 글자를 적으면 돼요. 숫자를 보여 주고 싶으면 '0'처럼 작은따옴표로 감싸요." + REAL)

o = frame("x-alias", EB4, "WHERE에서는 AS로 붙인 이름을 못 써요", C4)
xa = Q("x-alias")
t = term_q(xa, 96, 214, size=22, tid="t-xalias", lh=1.55)
o.append(t.html())
o.append(hbox(t, at(xa, "WHERE 요금"), "WHERE 요금 = '할인'", RED, 1))
o.append(hbox(t, at(xa, "ERROR"), "column \"요금\" does not exist", RED, 1))
ig = at(xa, "WHERE birth_year <= 1960")
o.append(hbox(t, ig, "WHERE birth_year <= 1960", GR, 3))
o += tag(t, ig + 4, "원래 열로 조건을 적었어요", GR, 3)
RX = t.x + t.w + 50
steps = [("FROM", GRAY), ("WHERE", RED), ("SELECT", C2), ("ORDER BY", C3)]
for k, (kw, col) in enumerate(steps):
    y = 230 + k * 150
    o.append(f'<div id="fl{k}"{bi("rise", 2)}{DELAY(k * 90)} style="position:absolute;left:{RX}px;top:{y}px;width:{1824 - RX}px;height:104px;background:{CARD};border:{3 if k in (1, 2) else 2}px solid {col if k in (1, 2) else LINE};border-radius:16px">'
             + p(f"position:absolute;left:24px;top:14px;font-family:{MONO};font-size:28px;font-weight:700;color:{col}", kw)
             + p(f"position:absolute;left:24px;top:56px;font-size:22px;color:{SUB};white-space:nowrap", ["표 고르기", "요금이 아직 없어요", "여기서 요금이 생겨요", "요금을 쓸 수 있어요"][k]) + '</div>')
    if k < 3:
        o.append(svg(arrow_path(f"M{RX + 60},{y + 110} L{RX + 60},{y + 140}", GRAY, 4) + head_at(RX + 60, y + 142, 90, GRAY), 2))
W("x-alias", o, "WHERE에서는 AS로 붙인 이름을 못 써요. 요금이 할인인 회원만 고르려고 WHERE 요금 = '할인'을 적었더니 요금이라는 열이 없다는 오류가 났어요. 들어가기에서 본 처리 순서를 떠올려요. WHERE는 SELECT보다 먼저 처리돼요. 요금은 SELECT에서 CASE로 만들어지니까, WHERE가 돌 때는 아직 없어요. 반대로 ORDER BY는 SELECT 다음이라 앞 파트에서 이번달이라는 이름으로 세울 수 있었어요. 고칠 때는 CASE가 쓰던 원래 열 birth_year로 조건을 적어요. 이름을 그대로 쓰는 방법은 41의 서브쿼리에서 배워요." + REAL)

o = frame("x-collate", EB4, "한글 이름은 가나다 순으로 안 설 때가 있어요", C4)
ca, cb = out_rows(Q("x-collate", 0)), out_rows(Q("x-collate", 1))
h1, g1 = sqlcard("co-a", 96, 214, 820, ["ORDER BY fee DESC, course_name;"], size=24)
h2, g2 = sqlcard("co-b", 1004, 214, 820, ["ORDER BY fee DESC,", "         course_name COLLATE \"C\";"], size=24)
o += [h1, h2]
ta = term_q(ca, 96, 214 + g2["h"] + 16, size=22, w=820, tid="t-coa", lh=1.5, bar=False)
tb = term_q(cb, 1004, 214 + g2["h"] + 16, size=22, w=820, tid="t-cob", lh=1.5, bar=False)
i9a = at(ca, "90000")
i9b = at(cb, "90000")
ta.band(i9a, i9a + 1, order=1, color=ROW_BAD)
tb.band(i9b, i9b + 1, order=2, color=ROW_OK)
o += [ta.html(), tb.html()]
o += tag(ta, i9a, "테니스가 수영보다 먼저", RED, 1, at=ta.sx(i9a, "90000") + ta.sw("90000"))
o += tag(tb, i9b, "가나다 순", GR, 2, at=tb.sx(i9b, "90000") + tb.sw("90000"))
o.append(caption("kant_shop의 기본 정렬 규칙(en_US.utf8)은 한글을 가나다 순으로 세우지 않을 때가 있어요. 가나다 순이 꼭 필요하면 그 기준 뒤에 COLLATE \"C\"를 붙여요.", ta.y + ta.h + 36, 3, size=26))
W("x-collate", o, "한글 이름은 가나다 순으로 안 설 때가 있어요. 수업 코드 그대로 수강료가 8만 원 이상인 강좌를 비싼 것부터, 같으면 이름순으로 세웠어요. 그런데 9만 원인 두 강좌에서 테니스 입문이 수영 고급반보다 먼저 나왔어요. ㅅ이 ㅌ보다 앞이니 수영이 먼저여야 해요. 데이터베이스를 만들 때 정해진 기본 정렬 규칙이 en_US.utf8인데, 이 규칙은 한글을 가나다 순으로 세우지 않을 때가 있어요. 가나다 순이 꼭 필요하면 오른쪽처럼 그 기준 뒤에 COLLATE C를 붙여요. 글자 번호 순서로 세우는데, 한글 글자 번호는 가나다 순서로 매겨져 있어요." + REAL)

# =====================================================================
# part 5: real situations
# =====================================================================
o = frame("e-fee", EB5, "회원 요금 안내: 영등포구 회원에게 요금 등급을 붙여요", C5)
ef = Q("e-fee")
t = term_q(ef, 96, 200, size=19, tid="t-efee", lh=1.46)
cats = [("할인", OR, "rgba(242,196,109,.22)"), ("일반", GRAY, "rgba(157,193,230,.14)"), ("청소년", BL, "rgba(127,209,139,.18)")]
for k, (cname, col, bgc) in enumerate(cats):
    ix = [i for i, l in enumerate(ef) if l.rstrip().endswith("| " + cname)]
    t.band(ix[0], ix[-1], order=k + 1, color=bgc)
o.append(t.html())
RX = t.x + t.w + 56
o.append(hd(RX, 214, "이번 달 요금표", GRAY, 26))
for k, (cname, col, bgc) in enumerate(cats):
    y = 270 + k * 150
    names = [l.split("|")[0].strip() for l in ef if l.rstrip().endswith("| " + cname)]
    o.append(chip(RX, y, cname, col, k + 1, 28))
    o.append(p(f"position:absolute;left:{RX + tw(cname, 28, mono=False) + 70:.0f}px;top:{y + 4}px;font-size:28px;font-weight:900;color:{col};white-space:nowrap", f"{len(names)}명", bi("pop", k + 1)))
    o.append(note(RX, y + 64, 1824 - RX, e(", ".join(names[:4]) + (" 외" if len(names) > 4 else "")), SUB, 23, k + 1))
o.append(note(RX, 270 + 3 * 150 + 20, 1824 - RX, "등급별로 몇 명인지 SQL로 세는 GROUP BY는 39에서 배워요.", SUB, 23, 4))
W("e-fee", o, "첫 번째 실제 상황이에요. 영등포구 회원에게 다음 달 요금 안내문을 보내려고 해요. 수업 코드 그대로 1960년 이전 출생은 할인, 2000년 이후 출생은 청소년, 나머지는 일반이에요. 나이 순서로 보려고 birth_year로 세우고, 같은 해에 태어나면 이름순으로 세웠어요. 할인 2명, 일반 7명, 청소년 3명이에요. 지금은 눈으로 셌지만, 등급별로 몇 명인지 SQL로 세는 방법은 39에서 GROUP BY로 배워요." + REAL)

o = frame("e-time", EB5, "시간표 만들기: 시작 시각으로 새벽, 오전, 오후, 저녁을 붙여요", C5)
et = Q("e-time")
t = term_q(et, 96, 200, size=18, tid="t-etime", lh=1.42)
o.append(t.html())
o.append(hbox(t, at(et, "ORDER BY start_time"), "ORDER BY start_time", C3, 1))
RX = t.x + t.w + 60
AX0, AX1 = RX + 20, 1800
AY = 520
hh0, hh1 = 5.5, 21.5
X = lambda hhmm: AX0 + (hhmm - hh0) / (hh1 - hh0) * (AX1 - AX0)
zones = [("새벽", 5.5, 7, "#5B6270"), ("오전", 7, 12, OR), ("오후", 12, 18, TEAL), ("저녁", 18, 21.5, BL)]
for k, (zn, a_, b_, col) in enumerate(zones):
    o.append(f'<div{bi("fade", 2)}{DELAY(k * 100)} style="position:absolute;left:{X(a_):.0f}px;top:{AY - 90}px;width:{X(b_) - X(a_) - 4:.0f}px;height:180px;border-radius:12px;background:{col}14;border-top:5px solid {col}"></div>')
    o.append(p(f"position:absolute;left:{X(a_):.0f}px;top:{AY - 136}px;width:{X(b_) - X(a_):.0f}px;text-align:center;font-size:24px;font-weight:700;color:{col};white-space:nowrap", zn, bi("rise", 2) + DELAY(k * 100)))
o.append(f'<div{WIPE(2)} style="position:absolute;left:{AX0}px;top:{AY - 2}px;width:{AX1 - AX0}px;height:4px;background:{GRAY}"></div>')
for hh in (6, 9, 12, 15, 18, 21):
    o.append(p(f"position:absolute;left:{X(hh) - 40:.0f}px;top:{AY + 100}px;width:80px;text-align:center;font-family:{MONO};font-size:20px;color:{GRAY}", f"{hh:02d}:00", bi("rise", 2)))
starts = []
for l in out_rows(et):
    m = re.search(r"\| (\d\d):(\d\d):00\s+\| (\S+)", l)
    if m:
        starts.append((int(m.group(1)) + int(m.group(2)) / 60, m.group(3)))
seen = {}
for k, (hv, zn) in enumerate(starts):
    col = {z[0]: z[3] for z in zones}[zn]
    stack = seen.get(hv, 0)
    seen[hv] = stack + 1
    o.append(f'<div{bi("pop", 3)}{DELAY(k * 50)} style="position:absolute;left:{X(hv) - 11:.0f}px;top:{AY - 11 - 30 - stack * 26:.0f}px;width:22px;height:22px;border-radius:11px;background:{col};box-shadow:0 0 0 3px #FFFFFF"></div>')
o.append(note(RX, AY + 170, 1824 - RX, "점 하나가 강좌 하나예요. 12시부터 18시 사이에는 강좌가 없어요. 오후 반을 새로 열면 좋겠다는 걸 바로 알 수 있어요.", INK, 25, 4))
W("e-time", o, "두 번째 실제 상황이에요. 센터 게시판에 붙일 시간표를 만들어요. 시작 시각으로 7시 전은 새벽, 12시 전은 오전, 18시 전은 오후, 나머지는 저녁을 붙였어요. WHEN을 위에서부터 따지니까 두 번째 WHEN에 7시보다 크거나 같다는 조건을 따로 적지 않아도 돼요. 첫 WHEN에서 7시 전은 이미 걸러졌어요. 시작 시각 순서로 세웠어요. 오른쪽 그림은 이 결과를 시간 줄 위에 점으로 찍은 거예요. 12시부터 18시 사이에는 강좌가 하나도 없어요. 오후 반을 새로 열면 좋겠다는 걸 바로 알 수 있어요." + REAL)

o = frame("e-sms", EB5, "문자 보낼 명단: 할인이나 청소년 회원 중 전화번호가 있는 사람만", C5)
es = Q("e-sms")
t = term_q(es, 96, 200, size=19, tid="t-esms", lh=1.48)
i_1960 = [i for i, l in enumerate(es) if "| 1960 |" in l.replace("       1960", "1960")]
o.append(t.html())
o.append(hbox(t, at(es, "WHERE (birth"), "(birth_year <= 1960 OR birth_year >= 2000)", OR, 1, which="box"))
o.append(hbox(t, at(es, "phone IS NOT NULL"), "phone IS NOT NULL", C2, 2))
o.append(hbox(t, at(es, "ORDER BY birth_year DESC, name"), "birth_year DESC, name", C3, 3))
i_k = rowi(es, "강시우")
o.append(f'<div{bi("fade", 3)} style="position:absolute;left:{t.x + 22}px;top:{t.top(i_k):.0f}px;width:{t.w - 44}px;height:{2 * t.lp:.0f}px;border-radius:8px;background:rgba(127,209,139,.20)"></div>')
RX = t.x + t.w + 56
notes_ = [("1", "괄호로 OR를 먼저 묶어서 할인이나 청소년 중에서 골라요.", OR, 1),
          ("2", "전화번호가 없는 황민서, 고은채는 빠졌어요.", C2, 2),
          ("3", "어린 회원부터, 1960년생 둘은 이름순이에요.", C3, 3)]
for k, (n_, txt, col, od) in enumerate(notes_):
    y = 240 + k * 200
    o.append(p(f"position:absolute;left:{RX}px;top:{y}px;width:52px;height:52px;border-radius:26px;background:{col};font-size:28px;font-weight:900;line-height:52px;text-align:center;color:#FFFFFF", n_, bi("pop", od)))
    o.append(note(RX + 72, y + 4, 1824 - RX - 72, e(txt), INK, 25, od))
W("e-sms", o, "세 번째 실제 상황이에요. 할인이나 청소년 요금을 받는 회원에게 문자로 안내하려고 해요. 문자를 보내려면 전화번호가 있어야 해요. WHERE에서 괄호로 OR를 먼저 묶어서 1960년 이전이거나 2000년 이후인 회원을 고르고, AND로 phone IS NOT NULL을 이었어요. 괄호가 없으면 AND가 먼저 묶여서 전화번호 없는 할인 회원까지 섞여요. 황민서와 고은채는 2000년 이후 출생이지만 전화번호가 없어서 빠졌어요. 어린 회원부터 세우고, 1960년생 강시우와 한수아는 이름순으로 섰어요. 1, 2, 3파트에서 배운 걸 한 문장에 다 썼어요." + REAL)

# =====================================================================
# wrap-up
# =====================================================================
o = frame("n-next", "정리", "39에서는 줄을 묶어서 세고 더해요", INK)
today = [("요금 등급별로 몇 명인지 세고 싶어요", "COUNT(*) · GROUP BY"), ("이번 달 매출 합계와 평균 수강료가 궁금해요", "SUM · AVG · ROUND"), ("신청이 10건 넘는 강좌만 보고 싶어요", "HAVING"),
         ("회원 이름과 신청한 강좌 이름을 한 줄에 보고 싶어요", "JOIN (40)"), ("평균보다 비싼 강좌만 고르고 싶어요", "서브쿼리 (41)")]
o.append(hd(96, 214, "오늘 결과를 보고 생긴 궁금증", GRAY, 24))
o.append(hd(1100, 214, "다음에 배울 것", GRAY, 24))
for k, (a_, b_) in enumerate(today):
    y = 262 + k * 100
    o.append(rule(96, y, 1728))
    o.append(p(f"position:absolute;left:96px;top:{y + 30}px;font-size:27px;color:{INK};white-space:nowrap", e(a_), bi("rise", 1) + DELAY(k * 70)))
    o.append(mono(1100, y + 30, b_, C3, 27, None, bi("pop", 2) + DELAY(k * 70)))
o.append(rule(96, 262 + 5 * 100, 1728))
o.append(note(96, 262 + 5 * 100 + 34, 1728, "오늘 배운 WHERE의 괄호, CASE, ORDER BY는 39부터 계속 같이 써요.", SUB, 26, 3))
W("n-next", o, "39에서는 줄을 묶어서 세고 더해요. 오늘 결과를 보면 이런 궁금증이 생겨요. 요금 등급별로 몇 명인지, 이번 달 매출 합계는 얼마인지, 신청이 많은 강좌는 어디인지예요. 39에서 COUNT, SUM, AVG 같은 집계 함수와 GROUP BY, HAVING으로 풀어요. 40에서는 회원 표와 수강 신청 표를 JOIN으로 이어서 한 줄에 보고, 41에서는 평균보다 비싼 강좌처럼 SELECT 안에 SELECT를 넣는 서브쿼리를 배워요. 오늘 배운 괄호, CASE, 정렬은 그때도 계속 써요.", ("outro", "정리"))

o = frame("trouble", "정리", "막히면 이렇게 풀어요", RED)
tr = [("결과에 다른 종목이 섞여 나와요", "AND와 OR를 괄호 없이 섞었어요", "OR 쪽을 괄호로"),
      ('syntax error at or near "AS"', "CASE를 END로 닫지 않았어요", "AS 앞에 END"),
      ("invalid input syntax for type integer", "THEN과 ELSE 값의 자료형이 달라요", "둘 다 글자나 둘 다 숫자"),
      ('column "요금" does not exist', "WHERE에서 AS 이름을 썼어요", "원래 열로 조건 적기"),
      ("CASE 결과가 다 같은 값이에요", "넓은 WHEN을 위에 적었어요", "좁은 조건부터"),
      ("CASE 열에 빈칸이 생겨요", "ELSE를 안 적었어요", "ELSE 값 적기"),
      ("DESC로 세웠는데 빈칸이 맨 앞이에요", "NULL은 가장 큰 값처럼 서요", "NULLS LAST")]
o.append(hd(96, 214, "이런 글이 보이면", GRAY, 24))
o.append(hd(1300, 214, "이렇게 해요", GRAY, 24))
for i, (q, a_, c_) in enumerate(tr):
    y = 262 + i * 88
    ra_ = bi("rise", 1) + DELAY(i * 70)
    o.append(rule(96, y, 1728))
    monoq = not any(0xAC00 <= ord(ch) <= 0xD7A3 for ch in q.replace("요금", ""))
    o.append(p(f"position:absolute;left:96px;top:{y + 10}px;width:1180px;{'font-family:' + MONO + ';font-size:24px;' if monoq else 'font-size:25px;'}font-weight:700;color:{RED};white-space:nowrap", e(q), ra_))
    o.append(p(f"position:absolute;left:96px;top:{y + 50}px;width:1180px;font-size:23px;color:{SUB}", e(a_), ra_))
    o.append(p(f"position:absolute;left:1300px;top:{y + 28}px;width:524px;font-size:25px;font-weight:700;color:{INK};white-space:nowrap", e(c_), ra_))
o.append(rule(96, 262 + len(tr) * 88, 1728))
o.append(caption("한글 열 정렬이 이상하면 COLLATE \"C\"를 붙여 봐요.", 262 + len(tr) * 88 + 30, 2, size=28))
W("trouble", o, "막히면 이렇게 풀어요. 결과에 엉뚱한 줄이 섞여 나오면 AND와 OR를 괄호 없이 섞었는지 봐요. AS 근처 syntax error는 대부분 END를 빠뜨린 거예요. integer에 글자를 넣을 수 없다는 오류는 THEN과 ELSE 값의 자료형이 다를 때 나요. AS로 붙인 이름이 없다고 하면 WHERE에서 그 이름을 쓴 거예요. CASE 결과가 다 같은 값이면 넓은 조건을 위에 적었는지, 빈칸이 생기면 ELSE를 빠뜨렸는지 봐요. DESC로 세웠는데 빈칸이 맨 앞이면 NULLS LAST를 붙여요. 한글 이름 순서가 이상하면 COLLATE C를 붙여요.")

o = frame("cheatsheet", "정리", "한 장 요약", INK)
groups = [("조건 섞기", C1, [("a AND (b OR c)", "OR가 섞이면 괄호부터"), ("AND가 OR보다 먼저", "곱셈이 덧셈보다 먼저처럼"), ("NOT IN · NOT LIKE", "반대로 고르기"), ("NOT (조건)", "괄호 안이 맞는 줄을 빼고")]),
          ("CASE로 값 붙이기", C2, [("CASE WHEN 조건 THEN 값", "처음 맞는 WHEN 하나만"), ("ELSE 값 END AS 이름", "ELSE가 없으면 NULL"), ("좁은 조건부터", "넓은 WHEN이 위면 아래는 안 봐요"), ("THEN 값끼리 같은 자료형", "글자면 모두 글자")]),
          ("줄 세우기", C3, [("ORDER BY a DESC, b", "DESC는 바로 앞 기준에만"), ("ORDER BY CASE ... END", "원하는 순서로 번호 매기기"), ("NULLS LAST · NULLS FIRST", "빈칸 자리 정하기"), ("COLLATE \"C\"", "한글 가나다 순")])]
GW = [560, 560, 560]
gx_ = [96, 96 + 560 + 24, 96 + 2 * (560 + 24)]
for i, (t_, c, rows) in enumerate(groups):
    x = gx_[i]
    o.append(p(f"position:absolute;left:{x}px;top:220px;font-size:30px;font-weight:700;color:{c}", e(t_)))
    o.append(f'<div style="position:absolute;left:{x}px;top:270px;width:{GW[i]}px;height:3px;background:{c}"></div>')
    for j, (k, d_) in enumerate(rows):
        y = 296 + j * 110
        monok = not any(0xAC00 <= ord(ch) <= 0xD7A3 for ch in k)
        fs = 22 if tw(k, 22) < GW[i] - 10 else 19
        o.append(p(f"position:absolute;left:{x}px;top:{y}px;width:{GW[i]}px;{'font-family:' + MONO + ';' if monok else ''}font-size:{fs}px;font-weight:700;color:{INK};white-space:nowrap", e(k)))
        o.append(p(f"position:absolute;left:{x}px;top:{y + 44}px;width:{GW[i]}px;font-size:23px;color:{SUB}", e(d_)))
o.append(caption("AND와 OR를 섞을 때는 괄호부터 쳐요.", 780, None, size=32))
o.append(caption("39에서는 COUNT, SUM, GROUP BY로 줄을 묶어서 세고 더해요.", 840, None, size=28, color=SUB))
W("cheatsheet", o, "오늘 쓴 것을 세 묶음으로 모았어요. 왼쪽은 조건 섞기예요. AND가 OR보다 먼저 묶이니까 OR가 섞이면 괄호부터 쳐요. NOT은 IN, LIKE, BETWEEN 앞이나 괄호 앞에 붙여서 뒤집어요. 가운데는 CASE예요. 위에서부터 처음 맞는 WHEN 하나만 고르고, ELSE가 없으면 NULL이에요. 좁은 조건부터 적고, THEN 값끼리 자료형을 맞춰요. 오른쪽은 줄 세우기예요. DESC는 바로 앞 기준에만 붙고, CASE로 원하는 순서를 만들고, NULLS LAST로 빈칸 자리를 정해요. 한글 이름 순서가 이상하면 COLLATE C를 붙여요. 다음 39에서는 집계와 GROUP BY를 배워요.")

# =====================================================================
# toc
# =====================================================================
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
PL = [(C1, EB1[3:], "AND와 OR를 줄마다 t, f로 따지기, AND가 먼저, 괄호, NOT IN · NOT LIKE · NOT (...)", "a-truth", "a-not"),
      (C2, EB2[3:], "CASE WHEN THEN ELSE END AS, WHEN 여러 개와 순서, ELSE가 없으면 NULL, 계산한 값, 파이썬 if와 비교", "c-two", "c-python"),
      (C3, EB3[3:], "기준 두 개, 기준마다 DESC, ORDER BY CASE, NULL이 서는 자리, NULLS LAST · NULLS FIRST", "o-two", "o-nulls"),
      (C4, EB4[3:], "END 빠짐, THEN 값의 자료형, WHERE에서 AS 이름, 한글 정렬과 COLLATE \"C\"", "x-end", "x-collate"),
      (C5, EB5[3:], "회원 요금 안내, 시간표 만들기, 문자 보낼 명단", "e-fee", "e-sms")]
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
o.append(p(f"position:absolute;left:96px;top:{214 + len(plist) * 112 + 34}px;font-size:26px;color:{SUB}", f"{page['why']}–{page['s-courses']}쪽은 들어가기와 예제 표 넣기, {page['n-next']}–{page['cheatsheet']}쪽은 다음에 배울 것, 막힐 때, 한 장 요약이에요."))
o = [x for x in o if 'id="eyebrow"' not in x]
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(o) + f"\n<aside>{e('다섯 파트로 나눴어요. 들어가기에서 수업 예제 표를 kant_shop에 넣어요. 1파트에서 AND와 OR를 섞을 때 괄호가 왜 필요한지 보고 NOT으로 뒤집어요. 2파트에서 CASE로 줄마다 등급을 붙이고, 3파트에서 기준 여러 개와 NULL 자리를 정해서 줄을 세워요. 4파트는 자주 나는 오류와 한글 정렬 함정, 5파트는 실제 상황 예제 세 개예요.')}</aside>\n</section>\n")

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-18T00:00:00Z"}, "lists": "css", "title": "SQL 3 (조건 조합과 CASE)", "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
for w_ in WARN:
    print("WARN", w_)
print(len(ORDER), "slides")
