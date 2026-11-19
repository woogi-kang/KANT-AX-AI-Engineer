r"""Generates every slide of the SQL 8 deck (43, transactions) and slides/deck.json.

Story: in 36 an UPDATE without WHERE set every price and there was no way back. psql saves each statement the moment
it runs (autocommit). BEGIN opens a transaction: what follows is kept apart until COMMIT makes it permanent, and
ROLLBACK throws all of it away at once. The prompt shows the state: kant_shop=*# inside, kant_shop=!# after an error.
Part 1 BEGIN, COMMIT, ROLLBACK and the class-code trap (ROLLBACK without BEGIN), part 2 a second window (uncommitted
changes are invisible, the same row waits, \q throws away), part 3 all or nothing (moving a course, the aborted
transaction, DROP TABLE rolled back), part 4 delete safely (SELECT first, compare the row counts), part 5 Git and
errors, part 6 three real cases on the class sports-center database. SAVEPOINT, isolation levels and locks stay out.

Every psql line comes from tools/demo.py (real Docker and postgres:18, in tools/out.json); two-window scenes come
from tools/duo.py, two psql sessions typed in turn. tools/sports.sql is the shared class data of 38-43.
Usage (in 43-sql-transaction): python3 tools/gen.py slides
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
PROMPT_RE = re.compile(r"^([a-z0-9_]+)((?:=|-|\(|')[*!]?#|=>) ?(.*)$")
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
        if m and m.group(2) in ("=#", "=*#", "=!#", "=>") and not (cur and PROMPT_RE.match(cur[-1] or "x") and False):
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
# helpers shared with 41
# =====================================================================
MY, VO = "#00758F", "#B26A00"
C1, C2, C3, C4, C5, C6 = BL, TEAL, OR, MAG, GR, RED
IN_C, IN_T = "#B26A00", "#E3A84A"            # the inner query: orange on paper, light orange in the terminal
IN_BG = "#FBF0DF"
BAND_IN = "rgba(227,168,74,.20)"


def P(scene, a=None, b=None, k=0):
    """the psql lines of a scene: no banner, no blank lines, no final \\q; a and b cut by a substring"""
    ls = []
    for l in D[scene][k]["out"]:
        l = l.rstrip()
        if not l.strip() or l.startswith("psql (18") or l.startswith('Type "help"') or l.endswith("# \\q"):
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
# chapter 43 helpers
# =====================================================================
EB1, EB2, EB3, EB4, EB5, EB6 = "1. BEGIN, COMMIT, ROLLBACK", "2. 다른 창에서 보면", "3. 모두 되거나 모두 안 되거나", "4. 지우기 전에 확인하기", "5. 비교와 오류", "6. 실제 상황"
C1, C2, C3, C4, C5, C6 = BL, TEAL, OR, MAG, GR, RED
STAR, BANG = "#F2A65A", "#FF8A80"           # the * and ! of the psql prompt
WA, WB = BL, GR                              # window 1 and window 2
REAL2 = " 두 창 화면은 tools/duo.py로 psql 두 개를 동시에 띄워 실제로 친 결과예요."
PR_ONLY = re.compile(r"^kant_shop[=\-(][*!]?#$")


def _row43(self, l):
    if l[0] == "m":
        pr, c = l[1], l[2]
        marks = l[-1] if isinstance(l[-1], dict) else {}
        ph = e(pr).replace("*", f'<span style="color:{STAR}">*</span>').replace("!", f'<span style="color:{BANG}">!</span>')
        return "m", f"{pr} {c}", f'<span style="color:#9DC1E6">{ph}</span> ' + mark(c, marks), "#F2C46D"
    return _old_row(self, l)


Term._row = _row43


def _html43(self):
    """like Term.html, plus self.reveal: {row index: order} makes those rows rise in at that order"""
    rv = getattr(self, "reveal", {})
    o = [f'<div id="{self.tid}"{self.attrs} style="position:absolute;left:{self.x}px;top:{self.y}px;width:{self.w}px;height:{self.h}px;background:{T_BG};border-radius:18px;padding:{self.PT}px {self.PX}px;font-family:{MONO};font-variant-ligatures:none;overflow:hidden;box-shadow:0 10px 30px rgba(29,35,48,.12)">']
    if self.bar:
        o.append('<div style="display:flex;flex-direction:row;gap:10px;height:16px;margin-bottom:20px">'
                 + "".join(f'<div style="width:16px;height:16px;border-radius:8px;background:{c}"></div>' for c in ("#F28B82", "#F2C46D", "#7FD18B")) + '</div>')
    o += self.inner
    for i, (kind, _, h, col) in enumerate(self.rows):
        wt = "font-weight:700;" if kind in ("$", "#", "m") else ""
        o.append(p(f"position:relative;font-size:{self.size}px;line-height:{self.lp:.0f}px;height:{self.lp:.0f}px;white-space:pre;{wt}color:{col}", cells(h), bi("rise", rv.get(i))))
    o.append('</div>')
    return "".join(o)


Term.html = _html43


def SN(scene, snap, win):
    """the screen of one window of a two-window scene, without the banner, blank lines and the last empty prompt"""
    ls = [l.rstrip() for l in D[scene][0]["snaps"][snap][win]]
    ls = [l for l in ls if l.strip() and not l.startswith("psql (18") and not l.startswith('Type "help"')]
    while ls and PR_ONLY.match(ls[-1]):
        ls.pop()
    return ls


def winlabel(x, y, text, color, order=None):
    return p(f"position:absolute;left:{x}px;top:{y}px;height:44px;padding:0 18px;border-radius:10px;background:{color};font-size:24px;font-weight:700;line-height:44px;color:#FFFFFF;white-space:nowrap", text, bi("rise", order))


def barlabel(t, text, color, order=None):
    """a window name in the terminal's title bar, right of the three dots"""
    return p(f"position:absolute;left:{t.x + 122}px;top:{t.y + 13}px;height:34px;padding:0 14px;border-radius:8px;background:{color};font-size:20px;font-weight:700;line-height:34px;color:#FFFFFF;white-space:nowrap;z-index:2", text, bi("rise", order))


def li_eq(t, text, start=0):
    for n in range(start, len(t.rows)):
        if t.rows[n][1].strip() == text:
            return n
    raise KeyError(text)


def rows_from(t, i):
    """every row index from i to the end"""
    return list(range(i, len(t.rows)))


def badge(x, y, n, c, od=None, size=40):
    return p(f"position:absolute;left:{x:.0f}px;top:{y:.0f}px;width:{size}px;height:{size}px;border-radius:{size // 2}px;background:{c};text-align:center;font-size:{size * 0.55:.0f}px;font-weight:700;line-height:{size}px;color:#FFFFFF", str(n), bi("pop", od))


def chip(x, y, text, color, order=None, size=26, attrs="", anim="pop", fill=True):
    bg = color if fill else "#FFFFFF"
    fg = "#FFFFFF" if fill else color
    bd = "" if fill else f"border:3px solid {color};"
    return p(f"position:absolute;left:{x:.0f}px;top:{y:.0f}px;height:{size + 26}px;padding:0 18px;border-radius:12px;background:{bg};{bd}font-family:{MONO};font-size:{size}px;font-weight:700;line-height:{size + 26 - (6 if not fill else 0)}px;color:{fg};white-space:nowrap", e(text), bi(anim, order) + attrs)


def chip_w(text, size=26):
    return tw(text, size) + 36


# =====================================================================
# cover
# =====================================================================
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px">',
       p("position:absolute;left:128px;top:300px;font-size:28px;font-weight:700;color:#9DC1E6", "KANT AX/AI 엔지니어 트랙 · 43"),
       f'<h1{SLAM(1)} style="position:absolute;left:128px;top:350px;padding-bottom:14px;font-size:100px;font-weight:900;line-height:1.3;color:#F6F5F1">SQL 8</h1>',
       p("position:absolute;left:128px;top:500px;font-size:52px;font-weight:700;line-height:1.3;color:#F6F5F1", "트랜잭션으로<br>묶고 되돌리기"),
       p("position:absolute;left:128px;top:680px;width:700px;font-size:30px;line-height:1.5;color:#BFC6D4", "BEGIN으로 묶고, COMMIT으로 확정하고,<br>ROLLBACK으로 한꺼번에 되돌려요")]
L = P("min")
t = PT(L, 960, 250, size=21, w=864, tid="cov-term", lh=1.5, maxb=900)
t.band(li(t, "ROLLBACK;"), None, None, "rgba(242,166,90,.20)")
cov.append(t.html())
cov.append(shine(2, "cov-term"))
W("cover", cov, "43 챕터는 SQL 8, 트랜잭션이에요. 36에서 WHERE를 빼고 UPDATE를 쳐서 모든 줄이 바뀌는 사고를 봤어요. 그때는 되돌릴 방법이 없었어요. 오늘은 BEGIN으로 문장들을 묶고, 마음에 들면 COMMIT으로 확정하고, 실수했으면 ROLLBACK으로 한꺼번에 되돌려요. 오른쪽 화면은 수강료를 모두 0원으로 바꿨다가 ROLLBACK으로 살려 낸 장면이에요. 예제는 38부터 쓰는 스포츠 센터 수업 데이터예요." + REAL, ("intro", "들어가기"))

ORDER.append("toc")   # written last, after page numbers are known

# =====================================================================
# why
# =====================================================================
o = frame("why", "들어가기", "WHERE를 빠뜨린 UPDATE는 ROLLBACK을 쳐도 안 돌아와요", INK)
L = P("why")
t = PT(L, 96, 214, size=32, w=1728, lh=1.5, tid="t-why", maxb=880)
u = li(t, "UPDATE 14")
w_ = li(t, "WARNING")
o.append(t.html())
o += tag(t, li(t, "SET fee = 0;"), "WHERE course_id = 5를 빠뜨렸어요", RED, 1, gap=60)
o += tag(t, u, "14줄이 모두 0원", RED, 1, gap=60)
o.append(under(t, w_, "there is no transaction in progress", 2, RED))
o += tag(t, w_, "되돌릴 거리가 없대요", OR, 2, gap=40)
o.append(spot_rows(t, li(t, "| fee"), li(t, "(4 rows)"), 3, x=t.x + 10, w=560))
o.append(spot_off(4))
o.append(caption("psql은 문장을 치는 순간 저장해요. 그래서 ROLLBACK을 쳐도 돌아갈 곳이 없어요.", t.y + t.h + 36, 4, size=30))
W("why", o, "아쿠아로빅 하나만 고치려다 WHERE를 빠뜨렸다고 해 봐요. UPDATE 14가 나왔어요. 강좌 14개의 수강료가 모두 0원이 됐어요. 급하게 ROLLBACK을 쳐 봤지만 WARNING이 나와요. 진행 중인 트랜잭션이 없다는 뜻이에요. 다시 SELECT해 보면 여전히 0원이에요. psql은 문장 하나를 칠 때마다 바로 저장하기 때문이에요. 오늘은 문장을 치기 전에 BEGIN으로 저장 지점을 만들어서, 이런 실수를 ROLLBACK 한 번으로 되돌려요." + REAL)

# =====================================================================
# big picture
# =====================================================================
o = frame("big", "들어가기", "BEGIN 뒤의 변경은 COMMIT하기 전까지 되돌릴 수 있어요", INK)
Y = 480
# the save point
o.append(f'<div{bi("pop", 1)} style="position:absolute;left:150px;top:{Y - 110}px;width:6px;height:150px;background:{INK};border-radius:3px"></div>')
o.append(f'<svg{bi("pop", 1)} viewBox="0 0 90 60" style="position:absolute;left:156px;top:{Y - 110}px;width:90px;height:60px"><path d="M0,0 L86,0 L66,30 L86,60 L0,60 Z" fill="{STAR}"/></svg>')
o.append(chip(96, Y + 60, "BEGIN;", INK, 1, size=30))
o.append(note(96, Y + 140, 300, "저장 지점", INK, 28, 1))
# the work line
o.append(f'<div{WIPE(2)} style="position:absolute;left:160px;top:{Y + 30}px;width:1060px;height:6px;background:{LINE};border-radius:3px"></div>')
ws = [("UPDATE 14", 360), ("DELETE 64", 610), ("INSERT 0 1", 860)]
for k, (txt, x) in enumerate(ws):
    o.append(chip(x, Y - 44, txt, GRAY, 2, size=28, attrs=DELAY(k * 140), fill=False, anim="rise"))
o.append(note(360, Y + 70, 820, "바꾼 내용은 아직 내 창에만 있어요. 프롬프트에 * 가 붙어요.", SUB, 28, 2))
# two exits
X2 = 1240
o.append(svg(arrow_path(f"M1220,{Y + 33} C1290,{Y + 33} 1290,{Y - 170} 1360,{Y - 170}", GR, 6) + head_at(1362, Y - 170, 0, GR), 3))
o.append(chip(1380, Y - 200, "COMMIT;", GR, 3, size=30))
o.append(note(1380, Y - 128, 460, "확정해요. 다른 창에도 보여요.<br>이제 못 되돌려요.", INK, 28, 3))
o.append(svg(arrow_path(f"M1220,{Y + 33} C1290,{Y + 33} 1290,{Y + 236} 1360,{Y + 236}", RED, 6) + head_at(1362, Y + 236, 0, RED), 4))
o.append(chip(1380, Y + 206, "ROLLBACK;", RED, 4, size=30))
o.append(note(1380, Y + 278, 460, "BEGIN 때로 돌아가요.<br>세 문장이 한꺼번에 사라져요.", INK, 28, 4))
o.append(svg(arrow_path(f"M1370,{Y + 330} C1000,{Y + 420} 420,{Y + 420} 210,{Y + 190}", RED, 4, "4 12") + head_at(206, Y + 186, -130, RED), 4))
W("big", o, "트랜잭션은 문장 여러 개를 하나로 묶는 단위예요. BEGIN을 치면 그 자리가 저장 지점이 돼요. 그 뒤에 UPDATE, DELETE, INSERT를 쳐도 바뀐 내용은 아직 확정되지 않아요. 연필로 쓴 글씨라고 생각하면 돼요. 끝에서 길이 두 개로 갈라져요. COMMIT을 치면 연필 글씨를 펜으로 덧써서 확정해요. 다른 창에서도 바뀐 값이 보이고, 이제는 되돌릴 수 없어요. ROLLBACK을 치면 저장 지점으로 돌아가요. BEGIN 뒤에 친 세 문장이 한꺼번에 지워져요. 문서 프로그램의 되돌리기 버튼을 여러 번 누른 것과 같아요.")

# =====================================================================
# smallest example
# =====================================================================
o = frame("min", "들어가기", "BEGIN을 먼저 치면 같은 실수도 ROLLBACK 한 번으로 살려요", INK)
L = P("min")
t = PT(L, 96, 214, size=27, w=1728, lh=1.45, tid="t-min", maxb=990)
b0 = li(t, "BEGIN;")
rb = li(t, "ROLLBACK;")
o.append(t.html())
o.append(rbox(t, b0, "kant_shop=# BEGIN;", 1, STAR))
o += tag(t, b0, "저장 지점을 먼저 만들어요", OR, 1, gap=60)
o.append(rbox(t, b0 + 2, "kant_shop=*#", 2, STAR))
o += tag(t, li(t, "UPDATE 14"), "같은 실수, 14줄이 0원", RED, 2, gap=60)
o.append(rbox(t, rb, "kant_shop=*# ROLLBACK;", 3, STAR))
o += tag(t, rb, "BEGIN 때로 돌아가요", GR, 3, gap=60)
o.append(spot_rows(t, li(t, "70000"), li(t, "80000"), 4, x=t.x + 10, w=560))
o.append(spot_off(5))
W("min", o, "앞 장과 같은 실수를 이번에는 BEGIN 다음에 해 봤어요. 먼저 BEGIN을 쳤어요. 그러자 프롬프트가 kant_shop=*#으로 바뀌었어요. 별표는 지금 트랜잭션 안에 있다는 표시예요. UPDATE 14가 나왔고, SELECT해 보면 이 창에서는 정말 0원으로 보여요. 이번에는 ROLLBACK이 경고 없이 끝나요. 별표도 사라졌어요. 다시 SELECT하면 7만 원, 7만 원, 8만 원이 그대로 있어요. 오늘 배울 세 명령이 이 화면에 다 있어요." + REAL)

# =====================================================================
# DDL, DML, TCL
# =====================================================================
o = frame("kinds", "들어가기", "SQL 문장은 하는 일에 따라 DDL, DML, TCL로 나눠요", INK)
COLS = [(96, "DDL", "표의 모양을 정해요", BL, ["CREATE TABLE", "DROP TABLE", "ALTER TABLE", "TRUNCATE"], "32, 37"),
        (690, "DML", "표 안의 줄을 다뤄요", GR, ["INSERT", "UPDATE", "DELETE", "SELECT"], "36, 38~41"),
        (1284, "TCL", "DML 묶음을 확정하거나 취소해요", STAR, ["BEGIN", "COMMIT", "ROLLBACK"], "오늘")]
for k, (x, nm, sub, c, cmds, ch) in enumerate(COLS):
    od = k + 1
    o.append(p(f"position:absolute;left:{x}px;top:224px;font-family:{MONO};font-size:56px;font-weight:700;line-height:1.2;color:{c}", nm, bi("rise", od)))
    o.append(p(f"position:absolute;left:{x}px;top:300px;width:520px;font-size:27px;font-weight:700;color:{INK}", e(sub), bi("rise", od)))
    # a small table picture: DDL lights the frame and header, DML one row, TCL a bracket
    gx_, gy_ = x, 372
    gw_, rh_ = 440, 52
    rows_ = 4
    frame_c = c if k == 0 else "#CFCAC0"
    o.append(f'<div{bi("rise", od)} style="position:absolute;left:{gx_}px;top:{gy_}px;width:{gw_}px;height:{rh_ * (rows_ + 1)}px;background:#FFFFFF;border:{4 if k == 0 else 2}px solid {frame_c};border-radius:12px;overflow:hidden">'
             f'<div style="position:absolute;left:0;top:0;width:100%;height:{rh_}px;background:{(c + "33") if k == 0 else "#EEF0F3"}"></div>'
             + "".join(f'<div style="position:absolute;left:0;top:{rh_ * (r + 1)}px;width:100%;height:2px;background:#E2DED5"></div>' for r in range(rows_))
             + (f'<div style="position:absolute;left:0;top:{rh_ * 2 + 2}px;width:100%;height:{rh_ - 2}px;background:{c}33"></div>' if k == 1 else "")
             + "".join(f'<div style="position:absolute;left:{24 + j * 140}px;top:{rh_ * (r + 1) + 20}px;width:{[90, 70, 100][(r + j) % 3]}px;height:12px;border-radius:6px;background:#E4E1DA"></div>' for r in range(rows_) for j in range(3))
             + '</div>')
    if k == 2:
        o.append(f'<div{bi("rise", od)} style="position:absolute;left:{gx_ - 8}px;top:{gy_ - 8}px;width:{gw_ + 16}px;height:{rh_ * (rows_ + 1) + 16}px;border:4px dashed {c};border-radius:16px"></div>')
    for j, cm in enumerate(cmds):
        o.append(chip(x + (j % 2) * 250, 660 + (j // 2) * 76, cm, c, od, size=24, attrs=DELAY(100 + j * 60)))
    o.append(p(f"position:absolute;left:{x}px;top:{660 + 2 * 76 + 14}px;font-size:24px;color:{GRAY}", f"배운 곳: {ch}", bi("rise", od) + DELAY(300)))
o.append(caption("수업 파일 주석에 나온 이름이에요. 트랜잭션은 DML을 묶어요.", 930, 4, size=29))
W("kinds", o, "수업 파일 주석에 DDL, DML이라는 말이 나왔어요. SQL 문장을 하는 일로 나눈 이름이에요. DDL은 Data Definition Language, 표의 모양을 정하는 문장이에요. CREATE TABLE, DROP TABLE, ALTER TABLE, TRUNCATE가 여기에 들어가요. DML은 Data Manipulation Language, 표 안의 줄을 넣고 고치고 지우고 읽는 문장이에요. INSERT, UPDATE, DELETE, SELECT예요. TCL은 Transaction Control Language예요. 오늘 배우는 BEGIN, COMMIT, ROLLBACK이고, DML 여러 개를 묶어서 확정하거나 취소해요. SELECT는 따로 DQL이라고 부르는 책도 있어요. 이름보다 하는 일을 기억하면 돼요.")

# =====================================================================
# part 1
# =====================================================================
o = frame("auto", EB1, "BEGIN이 없으면 문장 하나하나가 바로 저장돼요", C1)
L = P("auto")
t = PT(L, 96, 214, size=32, w=1728, lh=1.5, tid="t-auto", maxb=640)
o.append(t.html())
o += tag(t, li(t, "UPDATE 1"), "이 순간 저장돼요", C1, 1, gap=60)
# the hidden BEGIN/COMMIT around each statement, in one row
GY = t.y + t.h + 50
o.append(p(f"position:absolute;left:96px;top:{GY}px;font-size:28px;font-weight:700;color:{GRAY}", "psql이 문장마다 몰래 하는 일", bi("rise", 2)))
xx = 96
for k, st in enumerate(["UPDATE …;", "SELECT …;"]):
    for j, (txt, c, fl) in enumerate([("BEGIN", GRAY, False), (st, C1, True), ("COMMIT", GRAY, False)]):
        o.append(chip(xx, GY + 56, txt, c, 2, size=26, fill=fl, attrs=DELAY(k * 300 + j * 90)))
        xx += chip_w(txt, 26) + 16
    xx += 70
o.append(caption("이것을 자동 커밋(autocommit)이라고 해요. 그래서 치자마자 되돌릴 수 없어요.", GY + 160, 3, size=30))
W("auto", o, "BEGIN을 치지 않으면 psql은 문장 하나를 치는 순간 바로 저장해요. 이것을 자동 커밋, 오토커밋이라고 해요. 오른쪽 그림처럼 문장마다 앞에 BEGIN, 뒤에 COMMIT을 몰래 붙여서 실행한다고 생각하면 돼요. 그래서 UPDATE 1이 나온 순간 아쿠아로빅 수강료는 이미 65000원으로 확정됐어요. 35부터 41까지 친 문장도 모두 이렇게 바로 저장됐어요. 그동안은 편했지만 실수도 바로 저장돼요." + REAL, ("p1", "BEGIN, COMMIT, ROLLBACK"))

o = frame("begin", EB1, "BEGIN을 치면 프롬프트에 *가 붙고, COMMIT하면 사라져요", C1)
L = P("begin")
t = PT(L, 96, 214, size=28, w=1728, lh=1.45, tid="t-begin", maxb=990)
b0 = li(t, "BEGIN;")
c0 = li(t, "COMMIT;")
o.append(t.html())
o.append(rbox(t, b0 + 2, "kant_shop=*#", 1, STAR, j=li(t, "SELECT course_name")))
o += tag(t, b0 + 2, "* : 지금 트랜잭션 안이에요", OR, 1, gap=60)
o.append(rbox(t, c0, "COMMIT;", 2, GR))
o += tag(t, c0, "여기서 확정, 저장돼요", GR, 2, gap=60)
o.append(rbox(t, c0 + 2, "kant_shop=#", 3, "#9DC1E6"))
o += tag(t, c0 + 2, "*가 사라졌어요", C1, 3, gap=60)
W("begin", o, "같은 UPDATE를 이번에는 BEGIN 다음에 쳤어요. BEGIN을 치면 psql은 BEGIN이라고 대답하고, 프롬프트가 kant_shop=*#으로 바뀌어요. 별표가 보이는 동안은 트랜잭션 안에 있어요. 이 창에서 SELECT하면 65000원으로 보이지만 아직 확정된 값은 아니에요. COMMIT을 치면 COMMIT이라고 대답하고 그때 저장돼요. 프롬프트의 별표도 사라져요. 별표가 보이면 아직 확정하지 않은 변경이 있다고 기억해요." + REAL)

o = frame("commit-late", EB1, "COMMIT한 뒤에는 ROLLBACK으로 돌아가지 않아요", C1)
L = P("commit-late")
t = PT(L, 96, 214, size=30, w=1728, lh=1.5, tid="t-cl", maxb=880)
c0 = li(t, "COMMIT;")
w_ = li(t, "WARNING")
o.append(t.html())
o += tag(t, c0, "이미 확정했어요", GR, 1, gap=60)
o.append(under(t, w_, "there is no transaction in progress", 2, RED))
o += tag(t, w_, "되돌릴 트랜잭션이 없어요", RED, 2, gap=40)
o.append(spot_rows(t, li(t, "아쿠아로빅"), li(t, "아쿠아로빅"), 3, x=t.x + 10, w=480))
o.append(spot_off(4))
o.append(caption("확정한 값을 되돌리려면 원래 값으로 UPDATE를 한 번 더 쳐요. 그래서 COMMIT 전에 꼭 확인해요.", t.y + t.h + 36, 4, size=29))
W("commit-late", o, "COMMIT은 되돌릴 수 없는 확정이에요. COMMIT 다음에 ROLLBACK을 치면 첫 장에서 본 WARNING이 그대로 나와요. 진행 중인 트랜잭션이 없다는 뜻이에요. 수강료도 65000원 그대로예요. 확정한 값을 되돌리려면 UPDATE courses SET fee = 60000 WHERE course_id = 5처럼 원래 값을 알고 다시 고쳐야 해요. 그래서 COMMIT을 치기 전에 SELECT로 결과를 한 번 보는 습관을 들여요." + REAL)

o = frame("rb-many", EB1, "ROLLBACK은 BEGIN 뒤의 문장을 한꺼번에 되돌려요", C1)
L = P("rb-many")
t = PT(L, 96, 200, size=25, w=1728, lh=1.4, tid="t-rbm", maxb=990)
o.append(t.html())
o.append(rbox(t, li(t, "UPDATE 1"), "UPDATE 1", 1, OR))
o += tag(t, li(t, "UPDATE 1"), "정원 25 → 30", OR, 1, gap=60)
o.append(rbox(t, li(t, "DELETE 64"), "DELETE 64", 1, OR))
o += tag(t, li(t, "DELETE 64"), "9월 신청 64줄 지우기", OR, 1, gap=60)
r0 = li(t, "ROLLBACK;")
o.append(rbox(t, r0, "ROLLBACK;", 2, RED))
o += tag(t, r0, "한 번에 둘 다 되돌려요", RED, 2, gap=60)
i25, i64 = li(t, "      25"), li(t, "    64")
o.append(rbox(t, i25, "25", 3, GR))
o += tag(t, i25, "정원은 원래대로", GR, 3, gap=60)
o.append(rbox(t, i64, "64", 4, GR))
o += tag(t, i64, "64줄도 그대로", GR, 4, gap=60)
W("rb-many", o, "BEGIN 다음에 문장 두 개를 쳤어요. 아쿠아로빅 정원을 30명으로 바꾸고, 9월 신청 64줄을 지웠어요. 그다음 ROLLBACK 한 번을 쳤어요. 아래에서 하나씩 확인해 봐요. 정원은 원래 25명이에요. 9월 신청도 64줄이 그대로 있어요. ROLLBACK은 마지막 문장 하나가 아니라 BEGIN 뒤에 친 문장 전부를 되돌려요. 문장이 열 개여도 ROLLBACK 한 번이면 돼요." + REAL)

o = frame("rb-trap", EB1, "수업 코드처럼 BEGIN 없이 치면 ROLLBACK이 안 먹혀요", C1)
L = P("rb-trap")
a_ = next(i for i, l in enumerate(L) if l.endswith("ROLLBACK;"))
L1, L2 = L[:a_], L[a_:]
t1 = PT(L1, 96, 214, size=21, w=849, lh=1.42, tid="t-trap1", maxb=990)
t2 = PT(L2, 975, 214, size=26, w=849, lh=1.42, tid="t-trap2", maxb=990)
o.append(t1.html())
o.append(t2.html())
o.append(rbox(t1, 0, "kant_shop=#", 1, "#9DC1E6"))
o += tag(t1, 0, "BEGIN 없이 시작", C1, 1, gap=60)
o += tag(t1, li(t1, "UPDATE 6"), "이 순간 저장", RED, 1, gap=40)
w_ = li(t2, "WARNING")
o.append(shake(2, "t-trap2"))
o.append(under(t2, w_, "there is no transaction in progress", 2, RED))
o += tag(t2, w_, "이미 저장됐어요", RED, 2, gap=30) if t2.end(w_) + 300 < t2.x + t2.w else []
i30 = li(t2, "      30")
o.append(rbox(t2, i30, "30", 3, RED))
o += tag(t2, i30, "25가 아니라 30 그대로", RED, 3, gap=60)
o.append(caption("고칠 수도 있는 문장 앞에서는 BEGIN부터 쳐요.", t2.y + t2.h + 40, 4, left=975, width=849, size=30))
W("rb-trap", o, "오늘 수업 코드에서 실제로 있었던 장면이에요. 11월에 5명 이상 신청한 강좌의 정원을 5명씩 늘리는 UPDATE를 쳤어요. 서브쿼리 부분은 42에서 자세히 봐요. RETURNING으로 6개 강좌가 바뀐 것을 보고, 다시 되돌리려고 ROLLBACK을 쳤어요. 그런데 WARNING이 나와요. BEGIN 없이 쳤기 때문에 UPDATE 6이 나온 순간 이미 저장됐어요. 다시 SELECT해 보면 아쿠아로빅 정원이 25명이 아니라 30명 그대로예요. 수업에서는 그다음에 BEGIN을 쳤는데, 순서가 반대예요. 되돌릴 수도 있는 문장을 치기 전에 BEGIN부터 쳐요." + REAL)

# =====================================================================
# part 2: another window
# =====================================================================
def duo_pair(scene, snap, sz=24, y=280, maxb=900, wa=846, xb=978):
    LA, LB = SN(scene, snap, "A"), SN(scene, snap, "B")
    ta = PT(LA, 96, y, size=sz, w=wa, lh=1.45, tid=f"{scene}-a", maxb=maxb)
    tb = PT(LB, xb, y, size=sz, w=1824 - xb, lh=1.45, tid=f"{scene}-b", maxb=maxb)
    return ta, tb


o = frame("w-see", EB2, "COMMIT하기 전에는 다른 창에서 바뀐 값이 안 보여요", C2)
ta, tb = duo_pair("w-see", "end", sz=22, wa=880, xb=1006)
o.append(winlabel(96, 214, "창 1 · 데스크", WA))
o.append(winlabel(1006, 214, "창 2 · 강사", WB))
# typed order: A BEGIN, UPDATE, SELECT (1); B SELECT (2); A COMMIT (3); B SELECT (4)
ca = li(ta, "COMMIT;")
ta.reveal = {i: 3 for i in rows_from(ta, ca)}
sb2 = [i for i, r in enumerate(tb.rows) if "SELECT fee" in r[1]][1]
tb.reveal = {i: 2 for i in range(0, sb2)}
tb.reveal.update({i: 4 for i in rows_from(tb, sb2)})
o.append(ta.html())
o.append(tb.html())
i65 = li_eq(ta, "65000")
o.append(rbox(ta, i65, "65000", 1, STAR))
o += tag(ta, i65, "창 1에서는 65000", C2, 1, gap=60)
i60 = li_eq(tb, "60000")
o.append(rbox(tb, i60, "60000", 2, "#9DC1E6"))
o += tag(tb, i60, "창 2는 아직 60000", GR, 2, gap=60)
o.append(rbox(ta, ca, "COMMIT;", 3, GR))
j65 = li_eq(tb, "65000")
o.append(link(4, round(ta.end(ca) + 20), round(ta.cy(ca)), round(tb.sx(j65, "65000") - 14), round(tb.cy(j65)), GR))
o.append(rbox(tb, j65, "65000", 4, GR))
o += tag(tb, j65, "COMMIT 뒤에 보여요", GR, 4, gap=60)
o.append(caption("확정하지 않은 변경은 바꾼 창에서만 보여요. COMMIT을 잊으면 다른 사람은 계속 옛 값을 봐요.", max(ta.y + ta.h, tb.y + tb.h) + 44, 5, size=29))
W("w-see", o, "psql 창을 두 개 띄웠어요. 데스크 직원과 강사가 같은 데이터베이스에 붙은 장면이에요. 창 1에서 BEGIN을 치고 아쿠아로빅 수강료를 65000원으로 바꿨어요. 창 1에서 SELECT하면 65000원이 보여요. 이때 창 2에서 같은 줄을 읽으면 아직 60000원이에요. 확정하지 않은 변경은 바꾼 창에서만 보여요. 창 1에서 COMMIT을 친 뒤에 창 2에서 다시 읽으면 그제야 65000원이 보여요. BEGIN만 치고 COMMIT을 잊으면 다른 사람은 계속 옛 값을 봐요." + REAL + REAL2, ("p2", "다른 창에서 보면"))

o = frame("w-wait", EB2, "같은 줄을 고치려는 다른 창은 COMMIT할 때까지 기다려요", C2)
LA, LB = SN("w-wait", "end", "A"), SN("w-wait", "end", "B")
ta = PT(LA, 96, 214, size=26, w=1728, lh=1.45, tid="w-wait-a", maxb=520)
tb = PT(LB, 96, ta.y + ta.h + 24, size=ta.size, w=1728, lh=1.45, tid="w-wait-b", maxb=1000)
o.append(barlabel(ta, "창 1 · 데스크", WA))
o.append(barlabel(tb, "창 2 · 강사", WB))
ca = li(ta, "COMMIT;")
ta.reveal = {i: 3 for i in rows_from(ta, ca)}
u1 = li(tb, "UPDATE 1")
tb.reveal = {0: 2}
tb.reveal.update({i: 3 for i in rows_from(tb, u1)})
s2 = li(tb, "SELECT capacity")
tb.reveal.update({i: 4 for i in rows_from(tb, s2)})
o.append(ta.html())
o.append(tb.html())
o.append(rbox(ta, li(ta, "capacity + 5"), "capacity + 5", 1, STAR))
o += tag(ta, li(ta, "capacity + 5"), "아직 COMMIT 전", OR, 1, gap=40)
o.append(rbox(tb, 0, "capacity + 1", 2, "#9DC1E6"))
o += tag(tb, 0, "대답 없이 기다려요", OR, 2, gap=40)
o.append(rbox(ta, ca, "COMMIT;", 3, GR))
o += tag(ta, ca, "COMMIT하는 순간", GR, 3, gap=60)
o += tag(tb, u1, "창 2가 바로 실행돼요", GR, 3, gap=60)
o.append(rbox(tb, li(tb, "      31"), "31", 4, GR))
o += tag(tb, li(tb, "      31"), "25 + 5 + 1, 둘 다 반영", GR, 4, gap=60)
W("w-wait", o, "이번에는 두 창이 같은 줄을 고쳐요. 창 1이 BEGIN을 치고 아쿠아로빅 정원을 5명 늘렸어요. 아직 COMMIT하지 않았어요. 이때 창 2가 같은 강좌의 정원을 1명 늘리려고 하면 UPDATE 1이 나오지 않고 멈춰요. 오류가 아니라 창 1이 끝내기를 기다리는 거예요. 창 1이 COMMIT을 치는 순간 창 2의 UPDATE가 실행돼요. 마지막에 읽어 보면 25에 5와 1을 더한 31명이에요. 두 사람이 동시에 고쳐도 한 사람씩 차례로 들어가서 값이 꼬이지 않아요. 대신 BEGIN을 켜 둔 채 자리를 비우면 다른 사람이 계속 기다려요." + REAL + REAL2)

o = frame("w-quit", EB2, "COMMIT 없이 psql을 나가면 바꾼 내용은 버려져요", C2)
LA, LB = SN("w-quit", "end", "A"), SN("w-quit", "end", "B")
ta = PT(LA, 96, 214, size=28, w=1728, lh=1.45, tid="w-quit-a", maxb=520)
tb = PT(LB, 96, ta.y + ta.h + 24, size=ta.size, w=1728, lh=1.45, tid="w-quit-b", maxb=880)
o.append(barlabel(ta, "창 1 · 데스크", WA))
o.append(barlabel(tb, "창 2 · 강사", WB))
tb.reveal = {i: 2 for i in range(len(tb.rows))}
o.append(ta.html())
o.append(tb.html())
q_ = li(ta, "\\q")
o.append(rbox(ta, q_, "\\q", 1, RED))
o += tag(ta, q_, "COMMIT 없이 나가기", RED, 1, gap=60)
o.append(rbox(tb, li(tb, " 60000"), "60000", 3, GR))
o += tag(tb, li(tb, " 60000"), "바뀌지 않았어요", GR, 3, gap=60)
o.append(caption("수업 코드도 마지막 BEGIN 뒤에 COMMIT이 없어요. psql을 닫으면 그 UPDATE는 사라져요.", tb.y + tb.h + 36, 4, size=29))
W("w-quit", o, "창 1에서 BEGIN을 치고 수강료를 바꾼 다음, COMMIT 없이 백슬래시 q로 psql을 나갔어요. 창 2에서 읽어 보면 60000원 그대로예요. 확정하지 않은 트랜잭션은 창을 닫으면 ROLLBACK한 것처럼 버려져요. 오늘 수업 코드도 마지막에 BEGIN을 치고 UPDATE를 했지만 COMMIT이 없어요. 그 상태로 창을 닫았다면 그 UPDATE는 저장되지 않았어요. 작업을 끝낼 때는 프롬프트에 별표가 남아 있는지 보고, 남아 있으면 COMMIT이나 ROLLBACK으로 마무리해요." + REAL + REAL2)

# =====================================================================
# part 3: all or nothing
# =====================================================================
o = frame("move-why", EB3, "강좌 옮기기는 두 문장이 함께 성공해야 해요", C3)
SX = 96
o.append(p(f"position:absolute;left:{SX}px;top:214px;font-size:28px;font-weight:700;color:{GRAY}", "11번 회원이 필라테스 기구 초급을 요가 중급으로 옮겨요"))
STEPS = [("①", "UPDATE", "184번 신청을 취소", "status = '취소', pay_amount = 0"), ("②", "INSERT", "요가 중급을 새로 신청", "(188, 11, 9, '2026-11', '신청', 75000)")]
for k, (n, kw_, d_, sql_) in enumerate(STEPS):
    x = SX + k * 880
    o.append(f'<div{bi("rise", 1)}{DELAY(k * 120)} style="position:absolute;left:{x}px;top:280px;width:830px;height:150px;background:#FFFFFF;border:2px solid {LINE};border-radius:18px;box-shadow:0 6px 16px rgba(29,35,48,.06)"></div>')
    o.append(badge(x + 28, 304, n.replace("①", "1").replace("②", "2"), C3, 1))
    o.append(p(f"position:absolute;left:{x + 88}px;top:302px;font-size:30px;font-weight:700;color:{INK};white-space:nowrap", f"{kw(kw_, C3)} {e(d_)}", bi("rise", 1) + DELAY(k * 120)))
    o.append(p(f"position:absolute;left:{x + 88}px;top:360px;font-family:{MONO};font-size:22px;font-weight:700;color:{SUB};white-space:nowrap", e(sql_), bi("rise", 1) + DELAY(k * 120)))
RES = [("둘 다 됐어요", "새 강좌로 옮겨졌어요", GR, "✓", 2), ("①만 되고 ②가 실패", "돈은 돌려줬는데 들을 강좌가 없어요", RED, "✗", 3), ("둘 다 안 됐어요", "원래 강좌 그대로, 다시 하면 돼요", GR, "✓", 4)]
for k, (h_, d_, c, mk, od) in enumerate(RES):
    y = 500 + k * 120
    o.append(f'<div{bi("rise", od)} style="position:absolute;left:{SX}px;top:{y}px;width:1728px;height:2px;background:{LINE}"></div>')
    o.append(p(f"position:absolute;left:{SX}px;top:{y + 26}px;width:60px;font-size:40px;font-weight:900;line-height:1.5;color:{c}", mk, bi("pop", od)))
    o.append(p(f"position:absolute;left:{SX + 80}px;top:{y + 30}px;font-size:32px;font-weight:700;color:{INK};white-space:nowrap", e(h_), bi("rise", od)))
    o.append(p(f"position:absolute;left:{SX + 620}px;top:{y + 34}px;font-size:28px;color:{SUB};white-space:nowrap", e(d_), bi("rise", od)))
o.append(f'<div style="position:absolute;left:{SX}px;top:860px;width:1728px;height:2px;background:{LINE}"></div>')
o.append(caption("BEGIN으로 묶으면 가운데 줄은 생기지 않아요. 모두 되거나, 모두 안 되거나 둘 중 하나예요.", 900, 4, size=30))
W("move-why", o, "트랜잭션이 정말 필요한 곳은 여러 문장이 짝을 이룰 때예요. 11번 회원이 11월 필라테스 기구 초급을 요가 중급으로 옮긴다고 해 봐요. 첫째, 184번 신청을 취소로 바꾸고 낸 돈을 0원으로 해요. 둘째, 요가 중급 신청을 새로 넣어요. 결과는 세 가지가 나올 수 있어요. 둘 다 되면 좋아요. 둘 다 안 되면 원래대로라서 다시 하면 돼요. 문제는 가운데 줄이에요. 첫째만 되고 둘째가 실패하면 회원은 들을 강좌가 없어져요. 두 문장을 BEGIN과 COMMIT 사이에 묶으면 가운데 줄이 생기지 않아요. 모두 되거나 모두 안 되거나예요.")

o = frame("move-ok", EB3, "두 문장 모두 성공하면 COMMIT으로 한꺼번에 확정해요", C3)
L = P("move-ok")
t = PT(L, 96, 214, size=23, w=1728, lh=1.45, tid="t-mok", maxb=990)
b0, c0 = li(t, "BEGIN;"), li(t, "COMMIT;")
t.band(b0, c0 + 1, 1, "rgba(242,166,90,.14)")
o.append(t.html())
o += tag(t, li(t, "UPDATE 1"), "① 취소", C3, 1, gap=60)
o += tag(t, li(t, "INSERT 0 1"), "② 새 신청", C3, 1, gap=60)
o.append(rbox(t, c0, "COMMIT;", 2, GR))
o += tag(t, c0, "둘을 한 번에 확정", GR, 2, gap=60)
o.append(spot_rows(t, li(t, "| 취소"), li(t, "| 신청   |      75000"), 3, x=t.x + 10, w=1100))
o.append(spot_off(4))
W("move-ok", o, "먼저 옮기기 전의 184번 신청을 봤어요. 필라테스 기구 초급, 15만 원이에요. BEGIN을 치고 첫째 문장으로 184번을 취소, 0원으로 바꿨어요. 둘째 문장으로 188번 요가 중급 신청을 넣었어요. 둘 다 성공했으니 COMMIT으로 확정해요. 마지막 SELECT를 보면 184번은 취소, 188번은 신청으로 두 줄이 같이 바뀌었어요. 신청 번호는 손으로 적었어요. 마지막 번호가 187이라서 188을 썼어요." + REAL)

o = frame("move-err", EB3, "중간에 오류가 나면 *가 !로 바뀌고 ROLLBACK만 받아요", C3)
L = P("move-err")
t = PT(L, 96, 214, size=24, w=1728, lh=1.45, tid="t-merr", maxb=990)
e1 = li(t, "duplicate key")
ab = li(t, "current transaction is aborted")
r0 = li(t, "ROLLBACK;")
o.append(t.html())
o.append(under(t, e1, 'duplicate key value violates unique constraint "enrollments_pkey"', 1, RED))
o += tag(t, li(t, "already exists"), "187번은 이미 있어요", RED, 1, gap=40)
o.append(rbox(t, ab - 1, "kant_shop=!#", 2, BANG, j=r0))
o.append(under(t, ab, "current transaction is aborted, commands ignored until end of transaction block", 2, RED))
o.append(rbox(t, r0, "ROLLBACK;", 3, GR))
o += tag(t, r0, "①도 같이 되돌려요", GR, 3, gap=60)
o.append(spot_rows(t, li(t, "| 신청"), li(t, "| 신청"), 4, x=t.x + 10, w=1100))
o.append(spot_off(5))
W("move-err", o, "이번에는 둘째 문장에서 번호를 187로 잘못 적었어요. 187번은 이미 있어서 기본 키 오류가 나요. 37에서 본 duplicate key 오류예요. 그러자 프롬프트가 kant_shop=!#으로 바뀌었어요. 느낌표는 이 트랜잭션이 실패했다는 표시예요. 이 상태에서는 SELECT를 쳐도 current transaction is aborted가 나오고 아무 문장도 실행되지 않아요. 트랜잭션을 끝낼 때까지 무시한다는 뜻이에요. ROLLBACK을 치면 느낌표가 사라지고, 첫째 문장의 취소도 같이 되돌아가요. 184번은 다시 신청, 15만 원이에요. 번호를 고쳐서 처음부터 다시 하면 돼요." + REAL)

o = frame("move-commit", EB3, "오류 뒤에 COMMIT을 쳐도 ROLLBACK이라고 대답해요", C3)
L = P("move-commit")
t = PT(L, 96, 214, size=26, w=1728, lh=1.5, tid="t-mcm", maxb=880)
c0 = li(t, "COMMIT;")
o.append(t.html())
o.append(rbox(t, c0, "kant_shop=!# COMMIT;", 1, BANG))
o.append(rbox(t, c0 + 1, "ROLLBACK", 2, RED))
o += tag(t, c0 + 1, "COMMIT을 쳤는데 ROLLBACK", RED, 2, gap=60)
o.append(spot_rows(t, li(t, "| 신청"), li(t, "| 신청"), 3, x=t.x + 10, w=800))
o.append(spot_off(4))
o.append(caption("실패한 트랜잭션은 확정할 수 없어요. 대답이 COMMIT인지 ROLLBACK인지 꼭 읽어요.", t.y + t.h + 36, 4, size=29))
W("move-commit", o, "앞 장과 같은 오류가 난 뒤에 이번에는 COMMIT을 쳐 봤어요. 그런데 psql이 ROLLBACK이라고 대답해요. 오류 메시지도 없어서 그냥 지나치기 쉬워요. 느낌표가 붙은 트랜잭션은 확정할 수 없어서, COMMIT을 쳐도 PostgreSQL이 알아서 되돌려요. 첫째 문장의 취소도 저장되지 않았어요. 그래서 COMMIT을 친 뒤에는 대답이 정말 COMMIT인지 읽어 봐요." + REAL)

o = frame("ddl", EB3, "PostgreSQL은 DROP TABLE과 TRUNCATE도 되돌려요", C3)
L = P("ddl")
a_ = next(i for i, l in enumerate(L) if l.endswith("BEGIN;") and i > 2)
L1, L2 = L[:a_], L[a_:]
t1 = PT(L1, 96, 214, size=24, w=1000, lh=1.45, tid="t-ddl1", maxb=990)
t2 = PT(L2, 1130, 214, size=24, w=694, lh=1.45, tid="t-ddl2", maxb=990)
o.append(t1.html())
o.append(t2.html())
o.append(rbox(t1, li(t1, "DROP TABLE enrollments"), "DROP TABLE enrollments;", 1, RED))
o.append(under(t1, li(t1, "does not exist"), 'relation "enrollments" does not exist', 1, RED))
o.append(rbox(t1, li(t1, "ROLLBACK;"), "ROLLBACK;", 2, GR))
o.append(rbox(t1, li(t1, "   187"), "187", 2, GR))
o += tag(t1, li(t1, "   187"), "표가 돌아왔어요", GR, 2, gap=60)
o.append(rbox(t2, li(t2, "TRUNCATE enrollments"), "TRUNCATE enrollments;", 3, RED))
o.append(rbox(t2, li(t2, "   187"), "187", 4, GR))
o += tag(t2, li(t2, "   187"), "187줄 그대로", GR, 4, gap=60)
o.append(caption("모든 데이터베이스가 그렇지는 않아요. MySQL은 DROP TABLE을 치는 순간 저장돼요.", max(t1.y + t1.h, t2.y + t2.h) + 36, 5, size=29))
W("ddl", o, "DDL도 트랜잭션 안에서 되돌릴 수 있을까요. BEGIN을 치고 신청 표를 DROP TABLE로 통째로 지웠어요. SELECT하면 그런 표가 없다는 오류가 나고, 프롬프트에 느낌표가 붙어요. ROLLBACK을 치고 다시 세어 보면 187줄이 그대로 있어요. 오른쪽은 37에서 배운 TRUNCATE예요. 표를 비웠다가 ROLLBACK하니 187줄이 돌아왔어요. PostgreSQL은 DROP TABLE과 TRUNCATE도 트랜잭션에 넣어 줘요. 모든 데이터베이스가 그렇지는 않아요. MySQL은 DROP TABLE을 치는 순간 저장돼요. 연습용 표에서 해 보고, 실제 표에서는 DROP을 치지 않아요." + REAL)

# =====================================================================
# part 4: delete safely
# =====================================================================
o = frame("safe", EB4, "지우기 전에 줄 수를 세고, BEGIN 안에서 지운 뒤 숫자를 맞춰 봐요", C4)
L = P("safe-del")
t = PT(L, 96, 214, size=23, w=1300, lh=1.42, tid="t-safe", maxb=990)
o.append(t.html())
s1 = li(t, "SELECT COUNT")
s2 = li(t, "BEGIN;")
s3 = li(t, "DELETE FROM")
s4 = li(t, "COMMIT;")
n6 = li(t, "     6")
d6 = li(t, "DELETE 6")
BX = 1440
for k, (i_, h_, c) in enumerate([(s1, "같은 WHERE로 먼저 세요", C4), (s2, "저장 지점 만들기", C4), (s3, "RETURNING으로 지운 줄 보기", C4), (s4, "숫자가 같으면 COMMIT", GR)]):
    od = k + 1
    o.append(badge(t.x - 0 + t.w + 30, t.cy(i_) - 20, k + 1, c, od))
    o.append(p(f"position:absolute;left:{t.x + t.w + 86}px;top:{t.cy(i_) - 18:.0f}px;font-size:25px;font-weight:700;color:{c};white-space:nowrap", e(h_), bi("rise", od)))
o.append(rbox(t, n6, "6", 1, OR))
o.append(rbox(t, d6, "DELETE 6", 4, GR))
W("safe", o, "36에서 지우기 전에 SELECT부터 해 보라고 했어요. 오늘은 여기에 트랜잭션을 더해서 네 단계로 지워요. 11월 취소 신청을 정리하는 장면이에요. 첫째, 지울 때와 같은 WHERE로 COUNT를 세요. 6줄이에요. 둘째, BEGIN으로 저장 지점을 만들어요. 셋째, DELETE에 RETURNING을 붙여 지운 줄을 눈으로 봐요. 넷째, 끝에 나온 DELETE 6이 처음에 센 6과 같은지 맞춰 봐요. 같으면 COMMIT, 다르면 ROLLBACK이에요. 오른쪽 번호가 그 순서예요." + REAL, ("p4", "지우기 전에 확인하기"))

o = frame("oops", EB4, "숫자가 다르면 COMMIT하지 말고 ROLLBACK해요", C4)
L = P("oops-del")
t = PT(L, 96, 214, size=28, w=1728, lh=1.5, tid="t-oops", maxb=880)
n6 = li(t, "     6")
dn = next(i for i, r in enumerate(t.rows) if r[1].startswith("DELETE "))
o.append(t.html())
o.append(rbox(t, n6, "6", 1, OR))
o += tag(t, n6, "지울 줄은 6줄", OR, 1, gap=60, at=t.tx + t.sw("     6"))
o.append(rbox(t, li(t, "OR status"), "OR", 2, RED))
dtext = t.rows[dn][1].strip()
o.append(rbox(t, dn, dtext, 2, RED))
o += tag(t, dn, "AND를 OR로 잘못 쳤어요", RED, 2, gap=60)
o.append(rbox(t, li(t, "ROLLBACK;"), "ROLLBACK;", 3, GR))
o.append(rbox(t, li(t, "   187"), "187", 4, GR))
o += tag(t, li(t, "   187"), "한 줄도 안 지워졌어요", GR, 4, gap=60)
W("oops", o, "이번에는 같은 일을 하다가 AND를 OR로 잘못 쳤어요. OR는 둘 중 하나만 맞아도 골라서, 11월 신청 전부와 다른 달 취소까지 지워요. 처음에 센 숫자는 6인데 DELETE 뒤의 숫자는 훨씬 커요. 숫자가 다르면 COMMIT하지 않아요. ROLLBACK을 치고 전체를 세어 보면 187줄이 그대로예요. BEGIN이 없었다면 이 줄들은 그대로 사라졌어요. 38에서 본 AND와 OR의 차이가 이런 사고로 이어져요." + REAL)

# =====================================================================
# part 5: compare and errors
# =====================================================================
o = frame("cmp-git", EB5, "Git의 commit, restore와 닮았지만 다른 점이 있어요", C5)
rows_ = [["고치는 중", "파일을 고쳤지만 아직 커밋 전", "BEGIN 뒤에 UPDATE, DELETE"],
         ["확정하기", kw("git commit -m \"...\""), kw("COMMIT;")],
         ["고친 것 버리기", kw("git restore 파일") + " (07)", kw("ROLLBACK;")],
         ["다른 사람에게 보이는 때", kw("git push origin main") + " 뒤", kw("COMMIT;") + " 바로 뒤"],
         ["확정한 뒤 되돌리기", "커밋 기록이 남아 있어요", "기록이 없어요. 다시 UPDATE해요"]]
tb, y0 = table(96, 220, ["", "Git (02, 07)", "SQL 트랜잭션"], rows_, [470, 640, 618], "git-tb", size=30, rh=124, order=1, stagger=True)
o += tb
o.append(f'<div{bi("fade", 5)} style="position:absolute;left:84px;top:{y0 + 4 * 124 + 6:.0f}px;width:1752px;height:{124 - 10}px;border:4px solid {RED};border-radius:12px"></div>')
W("cmp-git", o, "02와 07에서 배운 Git과 나란히 놓아 봐요. 파일을 고쳤지만 커밋하기 전인 상태가 BEGIN 뒤에 UPDATE를 친 상태와 닮았어요. git commit이 COMMIT, git restore로 고친 것을 버리는 것이 ROLLBACK이에요. 다른 점도 있어요. Git은 git push를 해야 다른 사람에게 보이지만, 데이터베이스는 COMMIT하는 순간 다른 창에 보여요. 가장 큰 차이는 마지막 줄이에요. Git은 커밋 기록이 남아서 예전 커밋으로 돌아갈 수 있지만, 데이터베이스는 COMMIT한 뒤에 돌아갈 기록이 없어요. 원래 값을 알아서 다시 UPDATE해야 해요.", ("p5", "비교와 오류"))

o = frame("x-warn", EB5, "BEGIN을 두 번 쳐도, BEGIN 없이 ROLLBACK해도 경고만 나와요", C5)
L = P("begin2")
t = PT(L, 96, 214, size=30, w=1728, lh=1.5, tid="t-warn", maxb=760)
o.append(t.html())
w1 = li(t, "already a transaction")
w2 = li(t, "no transaction in progress")
o.append(under(t, w1, "there is already a transaction in progress", 1, OR))
o += tag(t, w1, "이미 BEGIN 상태예요", OR, 1, gap=40)
o.append(under(t, w2, "there is no transaction in progress", 2, OR))
o += tag(t, w2, "끝낼 트랜잭션이 없어요", OR, 2, gap=40)
o.append(caption("WARNING은 오류가 아니라 안내예요. 그래도 내가 생각한 상태와 다르다는 뜻이니 프롬프트를 다시 봐요.", t.y + t.h + 40, 3, size=29))
W("x-warn", o, "트랜잭션 명령을 순서에 맞지 않게 치면 WARNING이 나와요. BEGIN 상태에서 BEGIN을 한 번 더 치면 이미 트랜잭션이 진행 중이라고 알려 줘요. 새 저장 지점이 생기지는 않아요. 그 뒤 첫 ROLLBACK은 정상으로 끝나고, 두 번째 ROLLBACK은 끝낼 트랜잭션이 없다고 나와요. WARNING은 ERROR와 달리 문장을 막지 않는 안내예요. 하지만 내가 생각한 상태와 실제 상태가 다르다는 신호라서, 프롬프트에 별표가 있는지 다시 봐요." + REAL)

o = frame("x-table", EB5, "트랜잭션에서 자주 만나는 메시지와 상황", C5)
tr = [("WARNING:  there is no transaction in progress", "BEGIN 없이 ROLLBACK, COMMIT을 쳤어요", "이미 저장됐어요. 다음엔 BEGIN부터"),
      ("WARNING:  there is already a transaction in progress", "BEGIN 상태에서 BEGIN을 또 쳤어요", "그대로 이어서 쳐요"),
      ("ERROR:  current transaction is aborted, …", "앞 문장 오류로 트랜잭션이 실패했어요 (!#)", "ROLLBACK 뒤 처음부터"),
      ("COMMIT을 쳤는데 ROLLBACK", "실패한 트랜잭션은 확정이 안 돼요", "오류를 고쳐 다시 해요"),
      ("다른 창의 UPDATE가 대답이 없어요", "BEGIN한 창이 같은 줄을 잡고 있어요", "그 창에서 COMMIT이나 ROLLBACK"),
      ("나갔다 오니 바꾼 값이 없어요", "COMMIT 없이 \\q로 나갔어요", "끝내기 전에 * 확인")]
o.append(p(f"position:absolute;left:96px;top:214px;font-size:24px;font-weight:700;color:{GRAY}", "이런 게 보이면"))
o.append(p(f"position:absolute;left:1360px;top:214px;font-size:24px;font-weight:700;color:{GRAY}", "이렇게 해요"))
for i, (q, a_, c_) in enumerate(tr):
    y = 262 + i * 112
    ra = bi("rise", 1) + DELAY(i * 70)
    mono_ = q.startswith("WARNING") or q.startswith("ERROR")
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:2px;background:{LINE}"></div>')
    o.append(p(f"position:absolute;left:96px;top:{y + 16}px;width:1240px;{'font-family:' + MONO + ';' if mono_ else ''}font-size:{23 if mono_ else 25}px;font-weight:700;color:{RED if q.startswith('ERROR') else (OR if mono_ else INK)};white-space:pre", e(q), ra))
    o.append(p(f"position:absolute;left:96px;top:{y + 60}px;width:1240px;font-size:24px;color:{SUB}", e(a_), ra))
    o.append(p(f"position:absolute;left:1360px;top:{y + 36}px;width:464px;font-size:25px;font-weight:700;color:{INK};white-space:nowrap", e(c_), ra))
o.append(f'<div style="position:absolute;left:96px;top:{262 + 6 * 112}px;width:1728px;height:2px;background:{LINE}"></div>')
W("x-table", o, "오늘 본 메시지와 상황을 모았어요. 위의 두 줄은 WARNING이에요. BEGIN 없이 ROLLBACK을 치면 이미 저장된 뒤라서 되돌릴 수 없어요. 다음부터 BEGIN을 먼저 쳐요. BEGIN을 두 번 치면 그냥 이어서 쓰면 돼요. 셋째와 넷째는 트랜잭션 안에서 오류가 난 경우예요. 프롬프트가 느낌표로 바뀌고, 무엇을 쳐도 무시돼요. COMMIT을 쳐도 ROLLBACK이 돼요. ROLLBACK하고 고쳐서 다시 해요. 다섯째, 다른 창의 UPDATE가 대답이 없으면 BEGIN한 창이 같은 줄을 고치는 중이에요. 여섯째, COMMIT 없이 나가면 바꾼 값은 사라져요.")

# =====================================================================
# part 6: real cases
# =====================================================================
o = frame("r-fee", EB6, "실제 상황 1 · 수강료 5% 인상을 미리 해 보고 되돌려요", C6)
L = P("r-fee")
t = PT(L, 96, 214, size=27, w=1728, lh=1.45, tid="t-rfee", maxb=990)
o.append(t.html())
rr = li(t, "RETURNING")
o.append(spot_rows(t, rr + 1, li(t, "UPDATE 2"), 1, x=t.x + 10, w=760))
o.append(spot_off(2))
o += tag(t, li(t, "UPDATE 2"), "새 수강료를 먼저 봐요", C6, 1, gap=60)
o.append(rbox(t, li(t, "ROLLBACK;"), "ROLLBACK;", 2, GR))
o += tag(t, li(t, "ROLLBACK;"), "보고 나서 되돌리기", GR, 2, gap=60)
o.append(rbox(t, li(t, "65000"), "65000", 3, GR, j=li(t, "75000")))
o += tag(t, li(t, "65000"), "원래 값 그대로", GR, 3, gap=60)
W("r-fee", o, "첫 번째 실제 상황이에요. 센터장이 요가 수강료를 5% 올리면 얼마가 되는지 묻는다고 해 봐요. BEGIN을 치고 요가 강좌에 fee = fee * 1.05를 해 봤어요. RETURNING으로 새 수강료가 바로 보여요. 아침 요가는 68250원, 요가 중급은 78750원이에요. 숫자만 확인했으니 ROLLBACK으로 되돌려요. 다시 읽어 보면 원래 수강료 그대로예요. 계산 결과를 보기만 할 때도 BEGIN과 ROLLBACK을 미리보기처럼 쓸 수 있어요." + REAL, ("p6", "실제 상황"))

o = frame("r-cap", EB6, "실제 상황 2 · 수업 코드를 BEGIN으로 감싸서 확인하고 확정해요", C6)
L = P("r-cap")
t = PT(L, 96, 200, size=23, w=1728, lh=1.4, tid="t-rcap", maxb=990)
o.append(t.html())
o.append(rbox(t, 0, "kant_shop=# BEGIN;", 1, STAR))
o += tag(t, 0, "이번엔 BEGIN부터", C6, 1, gap=60)
rr = li(t, "| capacity")
o.append(spot_rows(t, rr, li(t, "UPDATE 6"), 2, x=t.x + 10, w=520))
o.append(spot_off(3))
o += tag(t, li(t, "UPDATE 6"), "6개 강좌, 정원 +5 확인", OR, 2, gap=60)
o.append(rbox(t, li(t, "COMMIT;"), "COMMIT;", 3, GR))
o += tag(t, li(t, "COMMIT;"), "맞으니 확정", GR, 3, gap=60)
W("r-cap", o, "두 번째 실제 상황은 1파트에서 본 수업 코드예요. 11월에 5명 이상 신청한 강좌의 정원을 5명씩 늘려요. 이번에는 순서를 바로잡아서 BEGIN부터 쳤어요. 프롬프트에 별표가 붙은 채로 UPDATE를 쳤고, RETURNING으로 바뀐 6개 강좌와 정원을 봤어요. 아쿠아로빅이 30명, 수영 고급반이 17명처럼 원래보다 5명씩 많아요. 생각한 대로라서 COMMIT으로 확정했어요. 만약 강좌 수가 이상했다면 ROLLBACK을 쳤으면 돼요." + REAL)

o = frame("r-quit", EB6, "실제 상황 3 · 회원 탈퇴는 신청 기록과 회원을 한 묶음으로 지워요", C6)
L = P("r-quit")
t = PT(L, 96, 200, size=23, w=1728, lh=1.4, tid="t-rquit", maxb=990)
o.append(t.html())
ef = li(t, "ERROR")
o.append(rbox(t, ef, "ERROR:", 1, RED))
o.append(under(t, li(t, "DETAIL"), "is still referenced from table", 1, RED))
o.append(rbox(t, li(t, "ROLLBACK;"), "ROLLBACK;", 2, OR))
o += tag(t, li(t, "ROLLBACK;") + 1, "신청 기록이 남아서 막혔어요 (37 외래 키)", OR, 2, gap=40, at=t.tx + t.sw("kant_shop=!# ROLLBACK;") + 20)
b2 = [i for i, r in enumerate(t.rows) if r[1].endswith("BEGIN;")][1]
o.append(rbox(t, b2 + 2, "DELETE FROM enrollments", 3, C6))
o += tag(t, b2 + 2, "자식 표부터", C6, 3, gap=60)
o.append(rbox(t, li(t, "RETURNING name"), "DELETE FROM members", 4, C6))
o += tag(t, li(t, "RETURNING name"), "그다음 회원", C6, 4, gap=60)
o.append(rbox(t, li(t, "COMMIT;"), "COMMIT;", 5, GR))
o += tag(t, li(t, "COMMIT;"), "둘을 한 번에 확정", GR, 5, gap=60)
W("r-quit", o, "세 번째 실제 상황이에요. 10번 회원이 탈퇴해서 회원 정보를 지워야 해요. 먼저 회원 표에서 바로 지우려고 했더니 외래 키 오류가 났어요. 37에서 배운 대로 신청 표가 이 회원을 가리키고 있어서 부모 줄을 먼저 지울 수 없어요. 트랜잭션은 실패 상태가 됐으니 ROLLBACK으로 정리해요. 다시 BEGIN을 치고 자식 표인 신청 기록부터 지웠어요. 5줄이에요. 그다음 회원을 지웠어요. 두 DELETE가 모두 성공했으니 COMMIT으로 한꺼번에 확정해요. 둘 중 하나만 지워지는 일이 없어요." + REAL)

# =====================================================================
# wrap-up
# =====================================================================
o = frame("sum", "정리", "되돌릴 수도 있는 일 앞에서는 BEGIN부터 쳐요", INK)
rows_ = [["여러 줄을 UPDATE, DELETE해요", kw("BEGIN; … 줄 수 확인 … COMMIT;", C1)],
         ["두 문장이 함께 성공해야 해요 (강좌 옮기기, 탈퇴)", kw("BEGIN; 문장1; 문장2; COMMIT;", C3)],
         ["결과를 보기만 하고 싶어요 (인상 미리보기)", kw("BEGIN; UPDATE … RETURNING …; ROLLBACK;", C6)],
         ["오류가 나서 프롬프트가 !# 예요", kw("ROLLBACK;", RED) + " 뒤 고쳐서 처음부터"]]
tb, y0 = table(96, 220, ["이럴 때", "이렇게 해요"], rows_, [800, 928], "sum-tb", size=26, rh=100, order=1, stagger=True, bold_first=False)
o += tb
yy = y0 + 4 * 100 + 50
o.append(p(f"position:absolute;left:96px;top:{yy}px;font-size:26px;font-weight:700;color:{GRAY}", "프롬프트로 상태 읽기", bi("rise", 5)))
for k, (pr, d_, c) in enumerate([("kant_shop=#", "자동 저장 중", "#9DC1E6"), ("kant_shop=*#", "트랜잭션 안, 아직 확정 전", STAR), ("kant_shop=!#", "실패, ROLLBACK만 받아요", BANG)]):
    x = 96 + k * 590
    o.append(p(f"position:absolute;left:{x}px;top:{yy + 50}px;height:56px;padding:0 18px;border-radius:12px;background:{T_BG};font-family:{MONO};font-size:26px;font-weight:700;line-height:56px;color:{c};white-space:nowrap", e(pr), bi("rise", 5) + DELAY(k * 80)))
    o.append(p(f"position:absolute;left:{x}px;top:{yy + 122}px;width:540px;font-size:25px;line-height:1.45;color:{INK}", e(d_), bi("rise", 5) + DELAY(k * 80)))
W("sum", o, "트랜잭션을 언제 쓰는지 정리해요. 여러 줄을 고치거나 지울 때는 BEGIN을 치고, 줄 수를 확인한 뒤 COMMIT해요. 강좌 옮기기나 회원 탈퇴처럼 두 문장이 함께 성공해야 하면 BEGIN과 COMMIT 사이에 묶어요. 결과를 보기만 하고 싶을 때는 BEGIN 뒤에 UPDATE와 RETURNING을 치고 ROLLBACK해요. 오류가 나서 프롬프트가 느낌표로 바뀌면 ROLLBACK하고 고쳐서 처음부터 다시 해요. 지금 상태는 프롬프트에서 읽어요. 아무 표시가 없으면 자동 저장 중, 별표면 확정 전, 느낌표면 실패한 트랜잭션이에요. 44에서는 파이썬에서 PostgreSQL을 쓰면서 같은 COMMIT이 어디서 일어나는지 봐요.", ("outro", "정리"))

o = frame("cheat", "정리", "한 장 요약", INK)
groups = [("세 명령", C1, [("BEGIN;", "저장 지점, 프롬프트에 *"), ("COMMIT;", "확정, 다른 창에도 보여요"), ("ROLLBACK;", "BEGIN 뒤 문장을 모두 되돌려요")]),
          ("안전하게 지우기", C4, [("SELECT COUNT(*) … WHERE …;", "같은 WHERE로 먼저 세기"), ("DELETE … WHERE … RETURNING …;", "BEGIN 안에서 지우고 보기"), ("DELETE 6 = 6 → COMMIT;", "숫자가 다르면 ROLLBACK")]),
          ("기억할 것", C3, [("BEGIN 없이는 바로 저장", "ROLLBACK이 안 먹혀요"), ("COMMIT 전엔 나만 보여요", "\\q로 나가면 버려져요"), ("오류 뒤 !#", "COMMIT도 ROLLBACK이 돼요")])]
GW = 560
for i, (t_, c, rows) in enumerate(groups):
    x = 96 + i * (GW + 24)
    o.append(p(f"position:absolute;left:{x}px;top:220px;font-size:30px;font-weight:700;color:{c}", e(t_)))
    o.append(f'<div style="position:absolute;left:{x}px;top:270px;width:{GW}px;height:3px;background:{c}"></div>')
    for j, (k_, d_) in enumerate(rows):
        y = 300 + j * 120
        mono_ = i < 2
        fs = 22 if mono_ else 25
        if mono_ and tw(k_, fs) > GW - 4:
            WARN.append(f"cheat: '{k_}' too wide")
        o.append(p(f"position:absolute;left:{x}px;top:{y}px;width:{GW}px;{'font-family:' + MONO + ';' if mono_ else ''}font-size:{fs}px;font-weight:700;color:{INK};white-space:nowrap", e(k_)))
        o.append(p(f"position:absolute;left:{x}px;top:{y + 42}px;width:{GW}px;font-size:23px;color:{SUB}", e(d_)))
o.append(f'<div style="position:absolute;left:96px;top:690px;width:1728px;height:2px;background:{LINE}"></div>')
o.append(p(f"position:absolute;left:96px;top:716px;font-size:26px;font-weight:700;color:{GRAY}", "문장 종류"))
kinds_ = [("DDL", BL, "CREATE  DROP  ALTER  TRUNCATE"), ("DML", GR, "INSERT  UPDATE  DELETE  SELECT"), ("TCL", STAR, "BEGIN  COMMIT  ROLLBACK")]
for k, (n_, c, d_) in enumerate(kinds_):
    x = 96 + k * 584
    o.append(p(f"position:absolute;left:{x}px;top:770px;font-family:{MONO};font-size:30px;font-weight:700;color:{c}", n_))
    o.append(p(f"position:absolute;left:{x}px;top:822px;width:560px;font-family:{MONO};font-size:21px;font-weight:700;color:{SUB};white-space:pre", e(d_)))
W("cheat", o, "오늘 배운 것을 한 장에 모았어요. 세 명령은 BEGIN, COMMIT, ROLLBACK이에요. 지울 때는 같은 WHERE로 먼저 세고, BEGIN 안에서 RETURNING을 붙여 지우고, 숫자가 같을 때만 COMMIT해요. 기억할 것 세 가지도 있어요. BEGIN 없이 친 문장은 바로 저장돼요. COMMIT하기 전의 변경은 내 창에만 보이고 나가면 버려져요. 오류가 난 뒤에는 COMMIT을 쳐도 ROLLBACK이 돼요. 아래는 문장 종류 세 가지예요.")

# =====================================================================
# toc
# =====================================================================
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
PL = [(C1, EB1[3:], "자동 저장, BEGIN과 *, COMMIT 뒤의 ROLLBACK, 한꺼번에 되돌리기, 수업 코드의 함정", "auto", "rb-trap"),
      (C2, EB2[3:], "확정 전에는 안 보여요, 같은 줄은 기다려요, \\q로 나가면 버려져요", "w-see", "w-quit"),
      (C3, EB3[3:], "강좌 옮기기, 오류와 !#, COMMIT이 ROLLBACK이 되는 때, DROP TABLE 되돌리기", "move-why", "ddl"),
      (C4, EB4[3:], "같은 WHERE로 먼저 세기, 숫자가 다르면 ROLLBACK", "safe", "oops"),
      (C5, EB5[3:], "Git과 비교, WARNING 두 가지, 메시지 모음", "cmp-git", "x-table"),
      (C6, EB6[3:], "인상 미리보기, 정원 늘리기, 회원 탈퇴", "r-fee", "r-quit")]
o = frame("toc", "", "오늘의 순서", INK)
for i, (c, h, s_, a, b) in enumerate(PL):
    y = 214 + i * 112
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:2px;background:{LINE}"></div>')
    o.append(p(f"position:absolute;left:96px;top:{y + 22}px;width:80px;font-size:48px;font-weight:900;line-height:1.5;color:{c}", str(i + 1)))
    o.append(p(f"position:absolute;left:190px;top:{y + 18}px;font-size:34px;font-weight:700;color:{INK}", e(h)))
    o.append(p(f"position:absolute;left:190px;top:{y + 70}px;font-size:22px;color:{SUB};white-space:nowrap", e(s_)))
    o.append(p(f"position:absolute;left:1524px;top:{y + 40}px;width:300px;text-align:right;font-size:28px;font-weight:700;color:{GRAY}", f"{page[a]}–{page[b]}쪽"))
o.append(f'<div style="position:absolute;left:96px;top:{214 + len(PL) * 112}px;width:1728px;height:2px;background:{LINE}"></div>')
o.append(p(f"position:absolute;left:96px;top:{214 + len(PL) * 112 + 34}px;font-size:26px;color:{SUB}", f"{page['why']}–{page['kinds']}쪽은 들어가기, {page['sum']}–{page['cheat']}쪽은 정리예요. 예제는 38부터 쓰는 스포츠 센터 수업 데이터예요."))
o = [x for x in o if 'id="eyebrow"' not in x]
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(o) + f"\n<aside>{e('여섯 파트로 나눴어요. 1파트는 BEGIN, COMMIT, ROLLBACK 세 명령과 수업 코드의 함정이에요. 2파트는 창을 두 개 띄워서 확정 전 변경이 다른 사람에게 어떻게 보이는지 봐요. 3파트는 두 문장을 하나로 묶는 이유와 오류가 났을 때예요. 4파트는 지우기 전에 줄 수로 확인하는 순서예요. 5파트는 Git과 비교하고 메시지를 모아요. 6파트는 실제 상황 세 가지예요.')}</aside>\n</section>\n")

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-19T00:00:00Z"}, "lists": "css", "title": "SQL 8 (트랜잭션)", "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
for w_ in WARN:
    print("WARN", w_)
print(len(ORDER), "slides")
