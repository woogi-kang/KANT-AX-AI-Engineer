r"""Generates every slide of the SQL 7 deck (42, insert, update and delete using other tables) and slides/deck.json.

Story: the sports center wants a list of members to call because their email or phone is missing. Typing the rows
of a SELECT result into INSERT ... VALUES by hand is slow and goes stale, so the rows a SELECT picks go straight into
another table (INSERT ... SELECT), into UPDATE and into DELETE. Part 1 INSERT ... SELECT (column pairs by position,
fixed-value columns, UNION and the text/date error, CAST and ::), part 2 UPDATE (ALTER TABLE ADD COLUMN, several
columns, an INT column rounds a computed value, WHERE IN (subquery)), part 3 EXISTS and NOT EXISTS (one question per
outer row, SELECT 1, NOT IN with a NULL), part 4 DELETE after a SELECT with the same WHERE, the foreign key error,
DELETE / TRUNCATE / DROP, part 5 errors, part 6 three real cases. BEGIN, COMMIT and ROLLBACK are left to 43.

Every psql line comes from tools/demo.py (real Docker and postgres:18, in tools/out.json); tools/sports.sql is the
shared class data of 38-42.
Usage (in 42-sql-insert-select): python3 tools/gen.py slides
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
# chapter 41 helpers (42 uses the same)
# =====================================================================
MY, VO = "#00758F", "#B26A00"
EB1, EB2, EB3, EB4, EB5, EB6 = "1. 다른 표에서 골라 넣기", "2. 여러 열과 계산으로 고치기", "3. 있는지 묻기 (EXISTS)", "4. 지우기와 표 비우기", "5. 오류와 함정", "6. 실제 상황"
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
# chapter 42
# =====================================================================
SEL_C, SEL_T, SEL_BG = IN_C, IN_T, IN_BG       # the SELECT that picks rows: orange, as the inner query of 41
BAND_SEL = BAND_IN
GOOD = "rgba(127,209,139,.18)"


def kcode(text, color=INK, size=None):
    s = f"font-size:{size}px;" if size else ""
    return f'<span style="font-family:{MONO};font-weight:700;color:{color};{s}">{e(text)}</span>'


def card_lines(cid, x, y, w, lines, fs=28, attrs="", pad=28, lh=1.5):
    """a light code card whose lines are already HTML"""
    hh = round(2 * pad + len(lines) * fs * lh)
    body = "".join(p(f"height:{fs * lh:.1f}px;font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:{fs * lh:.1f}px;white-space:pre;color:{INK}", l if l else "&#160;") for l in lines)
    for i, l in enumerate(lines):
        plain = re.sub(r"<[^>]+>", "", l).replace("&#160;", " ").replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#x27;", "'")
        if tw(plain, fs) > w - 2 * pad - 6:
            WARN.append(f"{cid}: line {i} '{plain[:30]}' wider than the card")
    return (f'<div id="{cid}"{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{hh}px;background:{CARD};border:2px solid {LINE};border-radius:16px;padding:{pad}px">{body}</div>'), hh


def sp(text, color, bold=True, attrs=""):
    return f'<span{attrs} style="color:{color};{"font-weight:700;" if bold else ""}">{e(text)}</span>'


# =====================================================================
# cover
# =====================================================================
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px">',
       p("position:absolute;left:128px;top:300px;font-size:28px;font-weight:700;color:#9DC1E6", "KANT AX/AI 엔지니어 트랙 · 42"),
       f'<h1{SLAM(1)} style="position:absolute;left:128px;top:350px;padding-bottom:14px;font-size:100px;font-weight:900;line-height:1.3;color:#F6F5F1">SQL 7</h1>',
       p("position:absolute;left:128px;top:500px;font-size:52px;font-weight:700;line-height:1.3;color:#F6F5F1", "다른 표를 보고<br>넣고, 고치고, 지우기"),
       p("position:absolute;left:128px;top:680px;width:700px;font-size:30px;line-height:1.5;color:#BFC6D4", "SELECT로 고른 줄을<br>INSERT, UPDATE, DELETE에 바로 써요")]
L = P("min", None, "SELECT * FROM contact_lists")
t = PT(L, 900, 330, size=24, w=924, tid="cov-term", lh=1.5, maxb=900)
t.band(li(t, "SELECT member_id"), li(t, "WHERE email"), None, BAND_SEL)
cov.append(t.html())
cov.append(shine(2, "cov-term"))
W("cover", cov, "42 챕터는 SQL 7, 다른 표를 보고 넣고, 고치고, 지우는 법이에요. 36에서 INSERT, UPDATE, DELETE를 배웠고, 41에서 쿼리 안에 쿼리를 넣었어요. 오늘은 SELECT로 고른 줄을 그대로 INSERT, UPDATE, DELETE에 써요. 오른쪽 화면에서 색칠한 줄이 회원 표에서 줄을 고르는 SELECT예요. 고른 9줄이 다른 표에 한 번에 들어가요. 예제는 38부터 쓰는 스포츠 센터 수업 데이터예요." + REAL, ("intro", "들어가기"))

ORDER.append("toc")   # written last, after page numbers are known

# =====================================================================
# why
# =====================================================================
o = frame("why", "들어가기", "SELECT 결과를 보고 INSERT에 손으로 옮겨 적으면 느리고 틀려요", INK)
L = P("why")
L = ins_short(L, keep=2)
t = PT(L, 96, 214, size=25, w=1728, lh=1.45, tid="t-why", maxb=930)
r3 = li(t, "| 박도현")
v3 = li(t, "(3, '박도현'")
r5 = li(t, "| 정하은")
v5 = li(t, "(5, '정하은'")
t.band(li(t, "SELECT member_id"), None, 1, BAND_SEL)
o.append(t.html())
o += tag(t, li(t, "(9 rows)"), "① 이메일이 없는 회원 9명을 찾았어요", OR, 1, gap=60)
for (ra_, va_, xv) in ((r3, v3, 1560), (r5, v5, 1620)):
    xs, ys, xe, ye = round(t.end(ra_) + 24), round(t.cy(ra_)), round(t.end(va_) + 30), round(t.cy(va_))
    o.append(svg(arrow_path(f"M{xs},{ys} H{xv - 20} Q{xv},{ys} {xv},{ys + 20} V{ye - 20} Q{xv},{ye} {xv - 20},{ye} H{xe + 2}", LC[OR], 4) + head_at(xe, ye, 180, LC[OR]), 2))
o += tag(t, li(t, "…"), "② 한 줄씩 보고 VALUES에 옮겨 적어요, 9줄 모두", OR, 2, gap=60)
o.append(caption("회원이 연락처를 새로 적거나 새 회원이 들어오면, 이 9줄을 다시 보고 다시 쳐야 해요.", t.y + t.h + 30, 3, size=29))
W("why", o, "SELECT 결과를 보고 INSERT에 손으로 옮겨 적으면 느리고 틀리기 쉬워요. 스포츠 센터에서 이메일이 없는 회원에게 연락해서 받아 두기로 했어요. 그래서 연락할 회원을 따로 모아 둘 명단 표 contact_lists를 만들었어요. 먼저 SELECT로 이메일이 없는 회원 9명을 찾아요. 그다음 36에서 배운 INSERT VALUES로 한 줄씩 옮겨 적어요. 9줄을 다 치면 INSERT 0 9가 나와요. 회원 번호나 이름을 하나 잘못 옮겨도 오류가 나지 않아서 틀린 줄을 찾기 어려워요. 회원이 바뀌면 처음부터 다시 쳐야 해요. 오늘은 이 SELECT를 INSERT에 바로 붙여요." + REAL)

# =====================================================================
# big picture
# =====================================================================
o = frame("big", "들어가기", "SELECT로 고른 줄을 넣고, 고치고, 지우는 데 바로 써요", INK)
rows_m = [["3", "박도현", "NULL"], ["4", "최지아", "user04@…"], ["5", "정하은", "NULL"], ["6", "강시우", "user06@…"], ["10", "임준서", "NULL"]]
g, (gx_, gy_, gw_, gh_) = grid(96, 300, ["member_id", "name", "email"], rows_m, [170, 150, 210], 66, "big-m", GRAY, size=26)
o.append(p(f"position:absolute;left:96px;top:240px;font-family:{MONO};font-size:28px;font-weight:700;color:{GRAY}", "members"))
o.append(g)
for i in (0, 2, 4):
    o.append(f'<div{bi("fade", 1)} style="position:absolute;left:99px;top:{300 + 3 + 66 * (i + 1)}px;width:{gw_}px;height:66px;background:{SEL_BG};border-left:6px solid {SEL_C};mix-blend-mode:multiply"></div>')
o.append(p(f"position:absolute;left:96px;top:{300 + gh_ + 30}px;height:54px;padding:0 18px;border-radius:12px;background:{SEL_C};font-family:{MONO};font-size:25px;font-weight:700;line-height:54px;color:#FFFFFF;white-space:nowrap", e("SELECT … WHERE email IS NULL"), bi("pop", 1)))
# picked rows
g2, (px_, py_, pw_, ph_) = grid(760, 360, ["member_id", "name"], [["3", "박도현"], ["5", "정하은"], ["10", "임준서"]], [170, 150], 66, "big-pick", SEL_C, size=26, attrs=' data-build-in="fly order 2" data-from="big-m"')
o.append(g2)
o.append(p(f"position:absolute;left:760px;top:300px;font-size:26px;font-weight:700;color:{SEL_C}", "고른 줄", bi("rise", 2)))
o.append(harrow(650, 745, 460, SEL_C, 2))
# three destinations
dests = [("INSERT INTO 명단 …  SELECT …", "다른 표에 넣어요", BL, "1파트"),
         ("UPDATE … WHERE id IN (SELECT …)", "그 줄만 고쳐요", TEAL, "2파트"),
         ("DELETE … WHERE NOT EXISTS (…)", "그 줄만 지워요", MAG, "3, 4파트")]
for k, (c_, d_, col, part) in enumerate(dests):
    y = 290 + k * 170
    o.append(svg(arrow_path(f"M1100,460 C1160,460 1150,{y + 50} 1210,{y + 50}", col, 4) + head_at(1212, y + 50, 0, col), 3 + k))
    o.append(p(f"position:absolute;left:1226px;top:{y + 22}px;height:56px;padding:0 18px;border-radius:12px;background:{col};font-family:{MONO};font-size:22px;font-weight:700;line-height:56px;color:#FFFFFF;white-space:nowrap", e(c_), bi("pop", 3 + k)))
    o.append(p(f"position:absolute;left:1226px;top:{y + 90}px;font-size:26px;font-weight:700;color:{INK};white-space:nowrap", f"{e(d_)} <span style='color:{GRAY};font-weight:400'>· {part}</span>", bi("rise", 3 + k) + DELAY(150)))
o.append(caption("고르는 일은 SELECT가 맡고, 넣기, 고치기, 지우기는 고른 줄을 받아서 해요.", 860, 5, size=30))
W("big", o, "오늘 배울 것을 그림 한 장으로 보면 이래요. 왼쪽 회원 표에서 SELECT가 이메일이 빈 줄만 골라요. 고른 줄은 세 군데로 갈 수 있어요. 첫째, INSERT 뒤에 붙여서 다른 표에 넣어요. 1파트예요. 둘째, UPDATE의 WHERE에 넣어서 그 줄만 고쳐요. 41에서 배운 IN 서브쿼리를 그대로 써요. 2파트예요. 셋째, DELETE의 WHERE에 넣어서 그 줄만 지워요. 이때 있는지 없는지만 묻는 EXISTS를 3파트에서 새로 배우고, 4파트에서 지우기에 써요. 고르는 방법은 지금까지 배운 SELECT 그대로예요.")

# =====================================================================
# create the list table
# =====================================================================
o = frame("create", "들어가기", "연락할 회원을 모아 둘 명단 표부터 만들어요", INK)
L = P("create")
t = PT(L, 96, 214, size=30, w=1728, lh=1.5, tid="t-create", maxb=900)
o.append(t.html())
o.append(under(t, li(t, "SERIAL"), "SERIAL", 1, OR))
o += tag(t, li(t, "SERIAL"), "번호는 저절로", OR, 1, gap=40)
o.append(rbox(t, li(t, "reason"), "reason", 2, "#9DC1E6"))
o += tag(t, li(t, "reason"), "왜 연락하는지", BL, 2, gap=40)
o.append(rbox(t, li(t, "request_date"), "request_date", 2, "#9DC1E6"))
o += tag(t, li(t, "request_date"), "요청한 날", BL, 2, gap=40)
o += tag(t, li(t, "(0 rows)"), "아직 빈 표", GRAY, 3, gap=40)
o.append(caption("member_id와 name은 members 표에 있어요. reason과 request_date는 members에 없어서 INSERT할 때 직접 적어요.", t.y + t.h + 30, 4, size=28))
o.append(caption("SERIAL과 NOT NULL은 37에서 배운 규칙이에요.", t.y + t.h + 80, 4, size=26, color=SUB))
W("create", o, "연락할 회원을 모아 둘 명단 표부터 만들어요. 수업에서 만든 contact_lists 표예요. request_id는 37에서 배운 SERIAL이라서 번호를 안 적어도 1부터 저절로 붙어요. member_id와 name은 회원 표에 이미 있는 열이에요. reason은 왜 연락하는지, request_date는 연락을 요청한 날이에요. 이 두 열은 회원 표에 없어서 넣을 때 직접 적어 줘야 해요. 다섯 열 모두 NOT NULL이라 비워 둘 수 없어요. 아직 아무 줄도 없어서 SELECT하면 0 rows가 나와요." + REAL)

# =====================================================================
# smallest example
# =====================================================================
o = frame("min", "들어가기", "INSERT 뒤에 VALUES 대신 SELECT를 붙이면 고른 줄이 다 들어가요", INK)
L = P("min")
t = PT(L, 96, 214, size=26, w=1728, lh=1.45, tid="t-min", maxb=990)
a, b = li(t, "SELECT member_id"), li(t, "WHERE email")
t.band(a, b, 1, BAND_SEL)
o.append(t.html())
o += tag(t, li(t, "INSERT INTO"), "어느 표, 어느 열에", BL, 1, gap=60)
o += tag(t, a, "VALUES 자리에 SELECT 문을 그대로", OR, 1, gap=60)
o.append(rbox(t, li(t, "INSERT 0 9"), "INSERT 0 9", 2, "#7FD18B"))
o += tag(t, li(t, "INSERT 0 9"), "고른 9줄이 한 번에 들어갔어요", GR, 2, gap=40)
o.append(spot_rows(t, li(t, "| 박도현"), li(t, "| 진우성"), 3))
o.append(spot_off(4))
W("min", o, "INSERT 뒤에 VALUES 대신 SELECT 문을 붙이면 SELECT가 고른 줄이 다 들어가요. 첫 줄은 36처럼 어느 표의 어느 열에 넣을지 적어요. 그 아래 VALUES 자리에 SELECT 문을 그대로 붙였어요. 색칠한 부분이 앞 장에서 친 SELECT와 같은 문장이에요. 이메일 미등록과 날짜는 모든 줄에 같은 글자를 넣었어요. 결과 INSERT 0 9는 9줄이 들어갔다는 뜻이에요. 명단을 SELECT해 보면 request_id가 1부터 9까지 붙어 있어요. 손으로 옮겨 적은 9줄과 같은 결과를 네 줄로 만들었어요." + REAL)

# =====================================================================
# part 1: column pairs
# =====================================================================
o = frame("pair", EB1, "열은 이름이 아니라 적은 순서대로 짝을 지어요", C1)
FS = 34
y1, y2, y3 = 300, 470, 540
seg1 = [("INSERT INTO contact_lists (", None), ("member_id", BL), (", ", None), ("name", GR), (", ", None), ("reason", OR), (", ", None), ("request_date", MAG), (")", None)]
seg2 = [("SELECT ", None), ("member_id", BL), (", ", None), ("name", GR), (", ", None), ("'이메일 미등록'", OR), (", ", None), ("'2026-11-19'", MAG)]
X0 = 140


def segline(segs, y, order_of):
    html_, x, pos = "", X0, {}
    for txt, col in segs:
        w = tw(txt, FS)
        if col:
            od = order_of(col)
            html_ += f'<span{MARK(od)} style="color:{col}">{e(txt)}</span>'
            pos[col] = (x, w)
        else:
            html_ += e(txt)
        x += w
    return p(f"position:absolute;left:{X0}px;top:{y}px;font-family:{MONO};font-size:{FS}px;font-weight:700;line-height:1.4;white-space:pre;color:{INK}", html_), pos


od_of = lambda c: 1 if c in (BL, GR) else 2
l1, pos1 = segline(seg1, y1, od_of)
l2, pos2 = segline(seg2, y2, od_of)
o.append(f'<div style="position:absolute;left:96px;top:250px;width:1728px;height:400px;background:{CARD};border:2px solid {LINE};border-radius:18px"></div>')
o += [l1, l2]
o.append(p(f"position:absolute;left:{X0}px;top:{y3}px;font-family:{MONO};font-size:{FS}px;font-weight:700;line-height:1.4;white-space:pre;color:{INK}", "FROM members WHERE email IS NULL;"))
for col in (BL, GR, OR, MAG):
    xa, wa = pos1[col]
    xb, wb = pos2[col]
    o.append(link(od_of(col), round(xa + wa / 2), y1 + FS * 1.4 + 4, round(xb + wb / 2), y2 - 4, col, 4))
o.append(p(f"position:absolute;left:{pos1[BL][0]:.0f}px;top:{y1 - 46}px;font-size:24px;font-weight:700;color:{SUB}", "① 넣을 열", bi("rise", 1)))
o.append(p(f"position:absolute;left:1240px;top:{y2 + 8}px;font-size:24px;font-weight:700;color:{SUB}", "② 넣을 값", bi("rise", 1)))
# explanation
rows_ = [[kw("member_id", BL), kw("member_id", BL), "1번째 칸끼리"],
         [kw("name", GR), kw("name", GR), "2번째 칸끼리"],
         [kw("reason", OR), kw("'이메일 미등록'", OR), "모든 줄에 같은 글자"],
         [kw("request_date", MAG), kw("'2026-11-19'", MAG), "모든 줄에 같은 날짜"]]
tb, y0 = table(96, 690, ["넣을 열", "SELECT 칸", "짝"], rows_, [420, 560, 748], "pair-tb", size=25, rh=54, order=3)
o += tb
W("pair", o, "INSERT의 열과 SELECT의 칸은 이름이 아니라 적은 순서대로 짝을 지어요. 첫 줄 괄호에 적은 넣을 열이 네 개예요. SELECT도 칸을 네 개 돌려줘요. 첫 번째 칸은 첫 번째 열에, 두 번째 칸은 두 번째 열에 들어가요. member_id와 name은 회원 표의 열이라 줄마다 다른 값이 들어가요. 세 번째와 네 번째는 회원 표에 없는 글자를 적었어요. 그래서 모든 줄에 같은 이메일 미등록과 같은 날짜가 들어가요. request_id는 괄호에 적지 않았으니 SERIAL이 번호를 채워요. 칸 개수나 순서가 어긋나면 5파트에서 볼 오류가 나요.", ("p1", "다른 표에서 골라 넣기"))

# =====================================================================
# part 1: fixed-value columns
# =====================================================================
o = frame("fixed", EB1, "표에 없는 글자를 SELECT하면 모든 줄에 같은 값이 붙어요", C1)
L = P("fixed")
t = PT(L, 96, 214, size=27, w=1728, lh=1.45, tid="t-fixed", maxb=900)
o.append(t.html())
h0 = li(t, "| request_date")
r0, r1 = li(t, "| 박도현"), li(t, "| 진우성")
xr = t.sx(h0, "reason") - 70
o.append(spot(1, x=round(xr), y=round(t.top(h0) - 6), w=round(t.sw("   reason      | request_date") + 70), h=round((r1 - h0 + 1) * t.lp + 12), dim=0.5))
o.append(spot_off(2))
o += tag(t, h0, "AS로 붙인 이름이 열 이름이 돼요", BL, 2, gap=40)
o.append(caption("40에서 '강사' AS 구분으로 구분 열을 붙인 것과 같아요. INSERT 전에 SELECT만 먼저 쳐서 들어갈 줄을 확인해요.", t.y + t.h + 30, 3, size=28))
W("fixed", o, "FROM에 적은 표에 없는 글자를 SELECT하면 모든 줄에 같은 값이 붙어요. 이 SELECT는 INSERT 없이 SELECT 부분만 쳐 본 거예요. reason 칸은 9줄 모두 이메일 미등록이고, request_date도 모두 같은 날짜예요. AS로 열 이름을 붙이면 넣을 열과 이름이 맞아서 읽기 쉬워요. INSERT는 이름이 아니라 순서로 짝을 지으니 AS는 없어도 돼요. 40에서 UNION으로 강사와 회원을 합칠 때 구분 열을 붙인 것과 같은 방법이에요. INSERT 앞에 SELECT만 먼저 쳐 보면 어떤 줄이 들어갈지 미리 볼 수 있어요." + REAL)

# =====================================================================
# part 1: VALUES vs SELECT (morph)
# =====================================================================
o = frame("vs", EB1, "VALUES 열 줄이 SELECT 세 줄로 줄어요", C1)
FS = 25
head = tok("h", "INSERT INTO contact_lists (member_id, name, reason, request_date)")
va = [head, tok("v", "VALUES")] + [f"({n}, '{m}', '이메일 미등록', '2026-11-19')," for n, m in
                                  [(3, "박도현"), (5, "정하은"), (10, "임준서"), (16, "황민서"), (17, "안태윤"), (24, "양다인"), (27, "백준혁"), (31, "하동건")]] + ["(38, '진우성', '이메일 미등록', '2026-11-19');"]
va = [l if l.startswith("<span") else e(l) for l in va]
CW_ = 1180
ca, ha = card_lines("vs-a", 96, 214, CW_, va, fs=FS, attrs=MORPH_FROM(), lh=1.5)
o.append(ca)
vb = [head, tok("v", f'<span style="color:{SEL_C}">SELECT member_id, name, \'이메일 미등록\', \'2026-11-19\'</span>'),
      f'<span style="color:{SEL_C}">FROM members</span>', f'<span style="color:{SEL_C}">WHERE email IS NULL;</span>']
vb += [""] * (len(va) - len(vb) - 1) + [f'<span style="color:{GRAY};font-weight:400">-- 회원이 바뀌어도 이 세 줄을 그대로 다시 실행해요</span>']
cb, hb = card_lines("vs-b", 96, 214, CW_, vb, fs=FS, attrs=MORPH(1, "vs-a"), lh=1.5)
o.append(cb)
RX = 1330
o += side(RX, 240, 494, "VALUES", "줄마다 값을 손으로 적어요.", GRAY, None, hsize=30, bsize=25)
o += side(RX, 380, 494, "SELECT", "조건을 한 번 적어요.", SEL_C, 1, hsize=30, bsize=25)
tb, _ = table(96, 214 + hb + 36, ["", "VALUES", "SELECT"],
              [["줄 수 (회원 9명)", "10줄", "3줄"],
               ["회원이 바뀌면", "다시 적어요", "다시 실행만 해요"],
               ["어울리는 때", "넣을 값을 이미 알 때", "다른 표에서 골라 올 때"]],
              [440, 640, 648], "vs-tb", size=26, rh=64, order=2, colors=[[None, None, SEL_C]] * 3)
o += tb
W("vs", o, "같은 9줄을 넣을 때 VALUES는 열 줄, SELECT는 세 줄이에요. 위 카드는 36에서 배운 VALUES 방식이에요. 한 줄에 회원 한 명씩 손으로 적었어요. 넘기면 VALUES부터 아래가 SELECT 세 줄로 바뀌어요. 첫 줄 INSERT INTO는 그대로 남아요. SELECT는 조건을 한 번 적어 두면 실행하는 날의 회원을 골라 와요. 새 상품 하나를 넣을 때처럼 넣을 값을 이미 알면 VALUES를 써요. 다른 표에 있는 줄을 골라 와야 하면 SELECT를 써요.")

# =====================================================================
# part 1: UNION error
# =====================================================================
o = frame("union-err", EB1, "UNION으로 합친 날짜 글자는 text가 돼서 DATE 열에 못 들어가요", C1)
L = P("union-err")
t = PT(L, 96, 214, size=24, w=1728, lh=1.5, tid="t-uerr", maxb=600)
o.append(t.html())
er = li(t, "ERROR")
o.append(rbox(t, er, "is of type date but expression is of type text", 1, "#FF9C94"))
o.append(shake(1, "t-uerr"))
o.append(under(t, li(t, "UNION"), "UNION", 2, "#9DC1E6"))
# explanation picture
BY = t.y + t.h + 50
o.append(p(f"position:absolute;left:96px;top:{BY}px;font-size:28px;font-weight:700;color:{INK}", "UNION이 먼저 두 SELECT를 합치면서 칸의 자료형을 정해요", bi("rise", 2)))
steps_ = [("'2026-11-19'", "따옴표 글자", GRAY), ("UNION으로 합칠 때", "text로 정해요", OR), ("request_date", "DATE 열이라 거절", RED)]
x = 96
for k, (a_, b_, c_) in enumerate(steps_):
    bw = tw(a_, 26) + 46
    o.append(p(f"position:absolute;left:{x}px;top:{BY + 70}px;height:60px;padding:0 20px;border-radius:12px;background:{CARD};border:3px solid {c_};font-family:{MONO};font-size:26px;font-weight:700;line-height:54px;color:{c_};white-space:nowrap", e(a_), bi("pop", 3) + DELAY(k * 150)))
    o.append(p(f"position:absolute;left:{x}px;top:{BY + 146}px;font-size:26px;color:{SUB};white-space:nowrap", e(b_), bi("rise", 3) + DELAY(k * 150)))
    if k < 2:
        o.append(harrow(x + bw + 40, x + bw + 190, BY + 100, GRAY, 3))
    x += bw + 230
o.append(caption("SELECT가 하나일 때는 PostgreSQL이 열에 맞춰 DATE로 읽어서 괜찮았어요.", BY + 220, 4, size=28, color=SUB))
W("union-err", o, "두 조건의 회원을 UNION으로 합쳐서 넣으면 날짜 글자가 text가 돼서 오류가 나요. 이메일이 없는 회원과 전화번호가 없는 회원을 한 번에 명단에 넣으려고 40에서 배운 UNION을 썼어요. 그런데 ERROR가 났어요. request_date 열은 DATE인데 들어오는 값은 text라는 뜻이에요. 따옴표로 감싼 2026-11-19는 아직 자료형이 정해지지 않은 글자예요. SELECT 하나만 INSERT할 때는 PostgreSQL이 넣을 열을 보고 DATE로 읽어 줬어요. UNION은 넣기 전에 두 SELECT를 먼저 합치면서 이 칸을 text로 정해 버려요. 그래서 날짜라고 직접 알려 줘야 해요. HINT도 rewrite or cast, 다시 쓰거나 자료형을 바꾸라고 말해요." + REAL)

# =====================================================================
# part 1: CAST and ::
# =====================================================================
o = frame("cast", EB1, "CAST(값 AS DATE)와 값::DATE는 같은 뜻이에요", C1)
L = P("cast")
t = PT(L, 96, 214, size=27, w=1728, lh=1.5, tid="t-cast", maxb=760)
o.append(t.html())
e1 = li(t, "ERROR")
o += tag(t, li(t, "SELECT '2026-11-19' + 7"), "그냥 글자라 날짜 계산이 안 돼요", RED, 1, gap=60)
q2 = li(t, "CAST(")
o.append(under(t, q2, "CAST('2026-11-19' AS DATE)", 2, "#7FD18B"))
o.append(under(t, q2, "'2026-11-19'::DATE", 2, "#7FD18B"))
o.append(spot_rows(t, li(t, "2026-11-26 | 2026-11-26"), li(t, "2026-11-26 | 2026-11-26"), 3, x=t.x + 10, w=520))
o.append(spot_off(4))
o += tag(t, li(t, "'120'::INTEGER"), "숫자 글자도 같은 방법", BL, 4, gap=40)
tb, _ = table(96, t.y + t.h + 34, ["쓰는 법", "모양", "읽는 법"],
              [[kw("CAST(값 AS 자료형)"), "SQL 표준", "다른 데이터베이스에서도 써요"],
               [kw("값::자료형"), "PostgreSQL 줄임", "짧아서 psql에서 자주 써요"]],
              [520, 420, 788], "cast-tb", size=25, rh=56, order=4)
o += tb
W("cast", o, "CAST 값 AS DATE와 값 콜론 콜론 DATE는 같은 뜻이에요. 자료형을 바꾼다고 해서 형 변환이라고 불러요. 첫 줄처럼 따옴표 글자에 7을 더하면 ERROR가 나요. 날짜가 아니라 글자로 읽어서 계산할 수 없어요. 둘째 줄은 두 가지 방법으로 DATE로 바꾼 다음 7을 더했어요. 둘 다 일주일 뒤인 11월 26일이 나와요. CAST는 SQL 표준 문법이라 MySQL 같은 다른 데이터베이스에서도 써요. 콜론 두 개는 PostgreSQL에서 쓰는 줄임 표현이에요. 숫자 글자 120도 INTEGER로 바꾸면 1을 더할 수 있어요." + REAL)

# =====================================================================
# part 1: UNION insert
# =====================================================================
o = frame("union", EB1, "두 SELECT를 날짜로 맞추면 UNION 결과 16줄이 한 번에 들어가요", C1)
L = P("union")
t = PT(L, 96, 214, size=22, w=1180, lh=1.4, tid="t-union", maxb=1000)
a10, b10 = li(t, "| 임준서 | 전화번호"), li(t, "| 임준서 | 이메일")
a16, b16 = li(t, "| 황민서 | 전화번호"), li(t, "| 황민서 | 이메일")
t.band(a10, b10, 2, "rgba(111,155,245,.22)")
t.band(a16, b16, 2, "rgba(111,155,245,.22)")
o.append(t.html())
o.append(under(t, li(t, "CAST("), "CAST('2026-11-19' AS DATE)", 1, "#7FD18B"))
o.append(under(t, li(t, "::DATE"), "'2026-11-19'::DATE", 1, "#7FD18B"))
o += side(1320, 240, 504, "이메일 9 + 전화번호 7", "UNION 결과 16줄이 그대로 들어갔어요.", INK, 1, hsize=30, bsize=25)
o += side(1320, 430, 504, "임준서, 황민서는 두 줄", "둘 다 없는 회원이에요. UNION은 완전히 같은 줄만 하나로 합쳐요. reason이 달라서 두 줄이 남아요.", BL, 2, hsize=30, bsize=25)
o += side(1320, 700, 504, "ORDER BY는 맨 끝에", "회원 번호 순서로 request_id가 붙어요.", GRAY, 3, hsize=30, bsize=25)
W("union", o, "두 SELECT의 날짜를 DATE로 맞추면 UNION 결과 16줄이 한 번에 들어가요. 수업 코드처럼 첫 SELECT는 CAST, 둘째 SELECT는 콜론 두 개로 바꿨어요. 이메일이 없는 회원 9명과 전화번호가 없는 회원 7명, 모두 16줄이 들어갔어요. RETURNING은 36에서 배운 대로 방금 들어간 줄을 바로 보여 줘요. 임준서와 황민서는 이메일도 전화번호도 없어서 두 번 나와요. UNION은 중복을 지우지만 완전히 같은 줄만 하나로 합쳐요. 두 줄은 reason이 달라서 둘 다 남아요. 40에서 배운 대로 ORDER BY는 맨 끝에 한 번 적어요. 그래서 request_id가 회원 번호 순서로 붙었어요." + REAL)

# =====================================================================
# part 2: ALTER TABLE ADD COLUMN
# =====================================================================
o = frame("alter", EB2, "ALTER TABLE ... ADD COLUMN으로 있는 표에 열을 더해요", C2)
L = P("alter")
t = PT(L, 96, 214, size=27, w=1728, lh=1.5, tid="t-alter", maxb=760)
o.append(t.html())
q1, q2 = li(t, "ADD COLUMN class_days"), li(t, "ADD COLUMN is_open")
o.append(under(t, q1, "ADD COLUMN class_days VARCHAR(10)", 1, "#7FD18B"))
o.append(under(t, q2, "DEFAULT true", 2, "#7FD18B"))
hh = li(t, "class_days | is_open")
rl = li(t, "4 | 수영 고급반")
xa = t.sx(hh, "| class_days") + 10
o.append(spot(3, x=round(xa), y=round(t.top(hh) - 6), w=round(t.sw("| class_days ")), h=round((rl - hh + 1) * t.lp + 12), dim=0.5))
xb = t.sx(hh, "| is_open") + 10
o.append(spot(4, x=round(xb), y=round(t.top(hh) - 6), w=round(t.sw("| is_open ")), h=round((rl - hh + 1) * t.lp + 12), dim=0.5))
o.append(spot_off(5))
tb, _ = table(96, t.y + t.h + 34, ["더한 열", "있던 14줄에 들어간 값"],
              [[kw("class_days VARCHAR(10)"), "모두 NULL (빈칸으로 보여요)"],
               [kw("is_open BOOLEAN NOT NULL DEFAULT true"), "모두 DEFAULT 값 t"]],
              [860, 868], "alter-tb", size=25, rh=56, order=5)
o += tb
W("alter", o, "ALTER TABLE 표 ADD COLUMN으로 이미 있는 표에 열을 더해요. 강좌 표에 수업 요일 칸이 없어서 class_days 열을 더했어요. 37에서는 ALTER TABLE로 규칙을 붙였고, 오늘은 열을 붙여요. 이미 있던 강좌 14줄의 새 칸에는 아무것도 안 들어 있어서 NULL이에요. psql은 NULL을 빈칸으로 보여 줘요. 둘째 줄처럼 DEFAULT를 붙여서 열을 더하면 있던 줄에도 기본값이 들어가요. is_open은 모두 t, 참이에요. 새 칸을 채우는 방법은 다음 장의 UPDATE예요." + REAL, ("p2", "여러 열과 계산으로 고치기"))

# =====================================================================
# part 2: several columns at once
# =====================================================================
o = frame("multi", EB2, "SET 뒤에 쉼표로 이어 적으면 여러 열을 한 번에 고쳐요", C2)
L = P("multi")
t = PT(L, 96, 214, size=27, w=1728, lh=1.5, tid="t-multi", maxb=720)
o.append(t.html())
sl = li(t, "SET class_days")
o.append(under(t, sl, "class_days = '월수금'", 1, "#7FD18B"))
o.append(under(t, sl, "start_time = '20:00'", 1, "#7FD18B"))
o += tag(t, sl, "쉼표로 이어요", GR, 1, gap=40)
# row card: before -> after
CY = t.y + t.h + 40
o.append(p(f"position:absolute;left:96px;top:{CY}px;font-size:26px;font-weight:700;color:{GRAY}", "9번 강좌 한 줄"))
cols_ = [("course_name", "요가 중급", None), ("class_days", "월수금", "(빈칸)"), ("start_time", "20:00:00", "19:30:00")]
x = 96
for k, (cn, last, first) in enumerate(cols_):
    w = 380
    o.append(p(f"position:absolute;left:{x}px;top:{CY + 50}px;width:{w}px;font-family:{MONO};font-size:24px;font-weight:700;color:{SUB}", cn))
    attrs = f' id="mv-{k}" data-start="{first}"' if first else ""
    o.append(p(f"position:absolute;left:{x}px;top:{CY + 90}px;width:{w - 24}px;height:64px;border-radius:12px;background:{CARD};border:2px solid {LINE};padding:0 20px;font-family:{MONO};font-size:28px;font-weight:700;line-height:60px;color:{INK if not first else TEAL};white-space:nowrap", e(last), attrs))
    x += w
o.append(set_text(2, "mv-1", "월수금"))
o.append(set_text(2, "mv-2", "20:00:00"))
o.append(p(f"position:absolute;left:1260px;top:{CY + 100}px;width:564px;font-size:26px;line-height:1.5;color:{SUB}", "UPDATE 1, 한 줄의 두 칸이 같이 바뀌었어요.", bi("rise", 2)))
W("multi", o, "SET 뒤에 열 = 값을 쉼표로 이어 적으면 여러 열을 한 번에 고쳐요. 요가 중급반의 요일을 월수금으로 정하고 시작 시간을 저녁 8시로 옮겨요. 먼저 SELECT로 9번 강좌를 보면 요일은 빈칸, 시작 시간은 7시 반이에요. UPDATE의 SET 뒤에 두 열을 쉼표로 이어 적었어요. WHERE로 9번 강좌만 골랐으니 UPDATE 1, 한 줄이 바뀌었어요. RETURNING으로 바뀐 두 칸을 바로 확인했어요. UPDATE를 두 번 쳐도 되지만, 한 번에 쓰면 한 줄의 두 칸이 같이 바뀌어요." + REAL)

# =====================================================================
# part 2: INT rounds a computed value
# =====================================================================
o = frame("round", EB2, "INTEGER 열에 계산한 값을 넣으면 소수점 아래는 반올림돼요", C2)
L = P("round")
t = PT(L, 96, 214, size=27, w=1728, lh=1.5, tid="t-round", maxb=780)
o.append(t.html())
r1 = li(t, "63636.363636363636")
r2 = li(t, "59090.909090909091")
s1, s2 = li(t, "|  63636"), li(t, "|  59091")
o.append(rbox(t, r1, "63636.363636363636", 1, IN_T))
o.append(rbox(t, r2, "59090.909090909091", 1, IN_T))
o += tag(t, r1, "계산하면 소수가 나와요", OR, 1, gap=40)
o.append(under(t, li(t, "ADD COLUMN supply INTEGER"), "supply INTEGER", 2, "#9DC1E6"))
o.append(rbox(t, s1, "63636", 3, "#7FD18B"))
o.append(rbox(t, s2, "59091", 3, "#7FD18B"))
o += tag(t, s1, "0.36…은 버리고 0.90…은 올려요", GR, 3, gap=40)
o.append(caption("36에서 친 fee = fee * 1.05도 fee가 INTEGER라서 같은 규칙으로 저장돼요. 소수까지 남기려면 열을 NUMERIC으로 만들어요.", t.y + t.h + 30, 4, size=28))
W("round", o, "INTEGER 열에 계산한 값을 넣으면 소수점 아래는 반올림돼서 저장돼요. 수강료에서 부가세 10퍼센트를 뺀 공급가를 구하려고 fee를 1.1로 나눴어요. SELECT로 계산만 해 보면 63636.36과 59090.90처럼 소수가 나와요. 공급가를 담을 supply 열을 INTEGER로 더하고 UPDATE로 계산한 값을 넣었어요. 63636.36은 63636으로, 59090.90은 59091로 들어갔어요. 잘라 버리는 게 아니라 반올림이에요. 36에서 친 fee = fee * 1.05도 fee가 INTEGER라서 소수가 생기면 이렇게 반올림돼요. 원 단위 아래까지 남겨야 하면 36에서 본 NUMERIC으로 열을 만들어요." + REAL)

# =====================================================================
# part 2: UPDATE with WHERE IN (subquery)
# =====================================================================
o = frame("sub-upd", EB2, "UPDATE의 WHERE에 서브쿼리를 넣으면 고를 줄을 다른 표가 정해요", C2)
L1 = P("sub-upd", None, "UPDATE courses")
L2 = P("sub-upd", "UPDATE courses")
t1 = PT(L1, 96, 214, size=24, w=700, lh=1.45, tid="t-su1", maxb=990)
t2 = PT(L2, 836, 214, size=24, w=988, lh=1.45, tid="t-su2", maxb=990)
ia, ib = li(t2, "SELECT course_id FROM"), li(t2, "HAVING COUNT")
t2.band(ia, ib, 2, BAND_SEL)
o.append(t1.html())
o.append(t2.html())
o += tag(t1, li(t1, "(6 rows)"), "① 안쪽만 먼저: 6개", OR, 1, gap=40)
r_a, r_b = li(t1, "         1"), li(t1, "         9")
o.append(spot_rows(t1, r_a, r_b, 1, x=t1.x + 10, w=300))
o.append(spot_off(2))
o += tag(t2, li(t2, "WHERE course_id IN ("), "② 그대로 IN 안에", OR, 2, gap=40)
ra, rb = li(t2, "1 | 수영 초급 아침반"), li(t2, "9 | 요가 중급")
o.append(rbox(t2, ra, "25", 3, "#7FD18B"))
o.append(rbox(t2, rb, "23", 3, "#7FD18B"))
o += tag(t2, li(t2, "UPDATE 6"), "같은 6개만 +5", GR, 3, gap=40)
o.append(note(96, t1.y + t1.h + 30, 700, "GROUP BY와 HAVING은 39, IN 서브쿼리는 41에서 배웠어요.", SUB, 26, 1))
W("sub-upd", o, "UPDATE의 WHERE에 서브쿼리를 넣으면 고칠 줄을 다른 표가 정해요. 11월 신청이 5명 이상인 인기 강좌의 정원을 5명씩 늘려요. 신청 수는 enrollments에 있고 정원은 courses에 있어요. 왼쪽처럼 안쪽 쿼리만 먼저 쳐서 강좌 번호 6개를 확인해요. 39에서 배운 GROUP BY와 HAVING이에요. 오른쪽은 그 쿼리를 41에서 배운 IN 괄호 안에 그대로 넣은 UPDATE예요. 정원 20이던 1번 강좌는 25가 됐어요. 왼쪽과 같은 6개 강좌만 바뀌어서 UPDATE 6이 나왔어요. SET capacity = capacity + 5는 36에서 배운 계산해서 고치기예요." + REAL)

# =====================================================================
# part 3: EXISTS, the smallest example
# =====================================================================
o = frame("ex-min", EB3, "EXISTS는 괄호 안에 줄이 하나라도 있으면 t, 없으면 f예요", C3)
L = P("ex-min")
t = PT(L, 96, 214, size=24, w=1180, lh=1.5, tid="t-exmin", maxb=990)
o.append(t.html())
q0 = li(t, "SELECT 1 FROM enrollments")
o += tag(t, li(t, "(5 rows)"), "10번 회원 신청 5건, 칸에는 1만 찍혀요", GRAY, 1, gap=40)
o.append(rbox(t, li(t, "member_id = 10);"), "EXISTS", 2, "#9DC1E6"))
o.append(rbox(t, li(t, " t"), "t", 2, "#7FD18B"))
o += tag(t, li(t, " t"), "있어요", GR, 2, gap=40)
o.append(rbox(t, li(t, " f"), "f", 3, "#FF9C94"))
o += tag(t, li(t, " f"), "40번 회원은 신청이 없어요", RED, 3, gap=40)
o += side(1320, 250, 504, "왜 SELECT 1?", "EXISTS는 칸에 무엇이 있는지 보지 않고 줄이 있는지만 봐요. 그래서 안쪽은 짧게 SELECT 1로 적어요.", OR, 4, hsize=30, bsize=26)
W("ex-min", o, "EXISTS는 괄호 안 SELECT에 줄이 하나라도 있으면 t, 하나도 없으면 f예요. 첫 쿼리는 10번 회원의 신청 줄을 고르면서 칸에는 숫자 1만 적었어요. 줄이 5개라 1이 다섯 번 찍혀요. 두 번째는 같은 SELECT를 EXISTS 괄호로 감쌌어요. 줄이 있으니 t, 참이에요. 40번 회원은 신청이 하나도 없어서 f, 거짓이에요. EXISTS는 칸에 들어 있는 값은 보지 않아요. 줄이 있는지만 봐요. 그래서 열 이름 대신 아무 값이나 적어도 되고, 짧게 SELECT 1로 쓰는 게 관례예요. SELECT 별표를 적어도 결과는 같아요." + REAL, ("p3", "있는지 묻기 (EXISTS)"))

# =====================================================================
# part 3: one question per outer row (picture)
# =====================================================================
o = frame("ex-idea", EB3, "바깥 줄마다 안쪽에 \"이 회원 신청 있어요?\"를 물어요", C3)
code_l = ["SELECT m.name FROM members m",
          "WHERE EXISTS (SELECT 1 FROM enrollments e",
          "              WHERE e.member_id = " + "\x00m.member_id\x01" + ")"]
html_l = [e(l).replace("\x00", f'<span id="ex-mid" style="color:{OR};background:{IN_BG};border-radius:8px;padding:0 6px">').replace("\x01", "</span>") for l in code_l]
cc, ch = card_lines("ex-code", 96, 214, 1000, html_l, fs=28, lh=1.5)
o.append(cc)
o.append(p(f"position:absolute;left:1140px;top:250px;width:684px;font-size:26px;line-height:1.55;color:{SUB}", "<b style='color:#B26A00'>m.member_id</b> 자리에 바깥 회원의 번호가 한 명씩 들어가요. 41의 서브쿼리는 안쪽이 한 번만 실행됐지만, 여기서는 회원마다 다시 물어요."))
MY0 = 214 + ch + 60
mem = [("3", "박도현", "t"), ("11", "한수아", "t"), ("25", "손현우", "t"), ("40", "채윤서", "f")]
o.append(p(f"position:absolute;left:96px;top:{MY0}px;font-family:{MONO};font-size:26px;font-weight:700;color:{GRAY}", "members m"))
RH = 78
for k, (n_, nm, ans) in enumerate(mem):
    y = MY0 + 50 + k * RH
    o.append(p(f"position:absolute;left:96px;top:{y}px;width:340px;height:{RH - 14}px;border-radius:12px;background:{CARD};border:2px solid {LINE};padding:0 20px;font-family:{MONO};font-size:27px;font-weight:700;line-height:{RH - 18}px;color:{INK};white-space:pre", f"{n_:>2}  {e(nm)}", f' id="exm-{k}"'))
    col = GR if ans == "t" else RED
    od = 1 if k == 0 else (2 if k == 3 else 3)
    o.append(p(f"position:absolute;left:470px;top:{y + 8}px;width:48px;height:48px;border-radius:24px;background:{col};text-align:center;font-family:{MONO};font-size:28px;font-weight:700;line-height:48px;color:#FFFFFF", ans, bi("pop", od) + (DELAY(1300) if k in (0, 3) else "")))
# enrollments box
EX, EY = 1180, MY0 + 50
er_ = [("1", "25", "1"), ("2", "10", "1"), ("9", "3", "2"), ("…", "…", "…"), ("187", "11", "14")]
g, (_, _, EW, EH) = grid(EX, EY, ["id", "member_id", "course_id"], er_, [130, 200, 200], 52, "ex-enr", GRAY, size=24)
o.append(p(f"position:absolute;left:{EX}px;top:{MY0}px;font-family:{MONO};font-size:26px;font-weight:700;color:{GRAY}", "enrollments e (187줄)"))
o.append(g)
# path 1: member 3 -> row "9 | 3"
y0 = MY0 + 50 + (RH - 14) / 2
pth = f'<path id="exp-1" d="M540,{y0:.0f} C820,{y0:.0f} 900,{EY + 52 * 3 + 26:.0f} {EX - 14},{EY + 52 * 3 + 26:.0f}" fill="none" stroke="{OR}" stroke-width="3" stroke-dasharray="8 8"/>'
o.append(svg(pth, 1, "draw"))
o.append(dot(EX - 14, EY + 52 * 3 + 26, OR, 1, "exp-1"))
o.append(f'<div{bi("fade", 1)}{DELAY(1300)} style="position:absolute;left:{EX + 3}px;top:{EY + 3 + 52 * 3}px;width:{EW}px;height:52px;background:{GOOD};border-left:6px solid {GR}"></div>')
# path 2: member 40 -> nowhere
y3 = MY0 + 50 + 3 * RH + (RH - 14) / 2
YE2 = EY + EH + 44
pth2 = f'<path id="exp-2" d="M540,{y3:.0f} C820,{y3:.0f} 900,{YE2:.0f} {EX - 14},{YE2:.0f}" fill="none" stroke="{RED}" stroke-width="3" stroke-dasharray="8 8"/>'
o.append(svg(pth2, 2, "draw"))
o.append(dot(EX - 14, YE2, RED, 2, "exp-2"))
o.append(p(f"position:absolute;left:{EX + 16}px;top:{YE2 - 20}px;font-size:26px;font-weight:700;color:{RED}", "40번은 한 줄도 없어요", bi("rise", 2) + DELAY(1300)))
o.append(caption("EXISTS는 t인 회원만, NOT EXISTS는 f인 회원만 남겨요.", 960, 4, size=29))
W("ex-idea", o, "EXISTS 안쪽 쿼리는 바깥 회원 한 명마다 이 회원 신청 있어요라고 다시 물어요. 코드의 m.member_id 자리에 바깥 줄의 회원 번호가 들어가요. 첫 번째로 3번 박도현 회원을 들고 신청 표를 찾아요. 3번이 적힌 줄이 있으니 t예요. 40번 채윤서 회원은 신청 표에 한 줄도 없어서 f예요. 나머지 회원도 같은 질문을 받아요. EXISTS는 t인 회원만 남기고, NOT EXISTS는 f인 회원만 남겨요. 41의 서브쿼리는 안쪽이 먼저 한 번 실행돼서 값이 됐어요. EXISTS는 바깥 줄을 하나씩 들고 안쪽에 물어서, 안쪽에 바깥 표의 열이 들어 있어요.")

# =====================================================================
# part 3: EXISTS and IN give the same people
# =====================================================================
o = frame("exists", EB3, "11월 13번 강좌 신청자는 EXISTS로도 IN으로도 같은 두 사람이에요", C3)
La = P("exists", None, "SELECT member_id, name FROM members")
Lb = P("exists", "SELECT member_id, name FROM members")
t1 = PT(La, 96, 214, size=25, w=900, lh=1.45, tid="t-ex1", maxb=860)
t2 = PT(Lb, 1020, 214, size=25, w=804, lh=1.45, tid="t-ex2", maxb=860, h=t1.h)
o.append(t1.html())
o.append(t2.html())
o.append(rbox(t1, li(t1, "e.member_id = m.member_id"), "e.member_id = m.member_id", 1, IN_T))
o += tag(t1, li(t1, "e.member_id = m.member_id"), "바깥과 잇는 조건", OR, 1, gap=30)
o.append(rbox(t2, li(t2, "WHERE member_id IN ("), "member_id IN (", 2, "#9DC1E6"))
o.append(spot_rows(t1, li(t1, "25 | 손현우"), li(t1, "11 | 한수아"), 3, x=t1.x + 10, w=400))
o.append(spot_rows(t2, li(t2, "25 | 손현우"), li(t2, "11 | 한수아"), 3, x=t2.x + 10, w=400))
yb = max(t1.y + t1.h, t2.y + t2.h) + 30
tb, _ = table(96, yb, ["", "EXISTS", "IN (41)"],
              [["안쪽이 묻는 것", "이 회원 줄이 있나요? (t, f)", "회원 번호 목록"],
               ["안쪽에 바깥 열", kw("m.member_id", OR) + " 를 씀", "안 씀, 혼자 실행돼요"]],
              [400, 700, 628], "ex-tb", size=28, rh=76, order=4)
o += tb
o.append(spot_off(4))
W("exists", o, "11월에 13번 강좌를 신청한 회원은 EXISTS로 찾아도, 41에서 배운 IN으로 찾아도 같은 두 사람이에요. 왼쪽 EXISTS는 안쪽 WHERE에 e.member_id = m.member_id를 적어서 바깥 회원과 이었어요. 이 줄이 있어야 회원마다 질문이 달라져요. 오른쪽 IN은 안쪽이 혼자 실행돼서 회원 번호 목록을 만들고, 바깥이 그 목록에 든 회원을 골라요. 결과는 손현우와 한수아, 같은 두 줄이에요. 이 정도 질문은 어느 쪽으로 써도 돼요. 차이는 목록에 NULL이 섞일 때 드러나요. 다음 두 장에서 봐요." + REAL)

# =====================================================================
# part 3: NOT EXISTS, members with no enrollment
# =====================================================================
o = frame("not-exists", EB3, "NOT EXISTS로 신청 기록이 한 번도 없는 회원을 찾아요", C3)
L = P("not-exists")
t = PT(L, 96, 214, size=34, w=1728, lh=1.5, tid="t-nex", maxb=900)
o.append(t.html())
o.append(rbox(t, li(t, "WHERE NOT EXISTS"), "NOT EXISTS", 1, "#9DC1E6"))
o += tag(t, li(t, "WHERE NOT EXISTS"), "f인 회원만", BL, 1, gap=40)
o.append(spot_rows(t, li(t, "40 | 채윤서"), li(t, "40 | 채윤서"), 2, x=t.x + 10, w=520))
o.append(spot_off(3))
o += tag(t, li(t, "40 | 채윤서"), "회원 40명 중 1명", GR, 3, gap=40)
o.append(caption("이 회원을 지우는 DELETE는 4파트에서 같은 WHERE로 써요.", t.y + t.h + 30, 3, size=28, color=SUB))
W("not-exists", o, "NOT EXISTS를 쓰면 신청 기록이 한 번도 없는 회원을 찾아요. 오늘 수업 코드 그대로예요. 회원마다 신청 표에 그 회원 번호가 있는지 묻고, 없다고 답한 회원만 남겨요. 회원 40명 중 채윤서 회원 한 명이에요. 가입만 하고 한 번도 수강하지 않은 회원이에요. 이렇게 찾은 회원을 지우는 DELETE는 4파트에서 같은 WHERE로 써요." + REAL)

# =====================================================================
# part 3: NOT IN with a NULL vs NOT EXISTS
# =====================================================================
o = frame("notin-null", EB3, "목록에 NULL이 섞이면 NOT IN은 0줄, NOT EXISTS는 맞게 나와요", C3)
L = P("notin-null")
t = PT(L, 96, 214, size=26, w=1728, lh=1.45, tid="t-nin", maxb=990)
r5 = li(t, "5 | 아쿠아로빅")
t.band(r5, r5, 1, "rgba(240,122,114,.22)")
o.append(t.html())
o += tag(t, r5, "강사 칸이 비어 있어요 (NULL)", RED, 1, at=t.end(li(t, "4 | 수영 고급반")), gap=60)
o.append(rbox(t, li(t, "(0 rows)"), "(0 rows)", 2, "#FF9C94"))
o += tag(t, li(t, "(0 rows)"), "NOT IN: NULL과 비교한 답은 모름이라 아무도 안 나와요", RED, 2, gap=40)
o.append(rbox(t, li(t, " 윤태호"), "윤태호", 3, "#7FD18B"))
o += tag(t, li(t, " 윤태호"), "NOT EXISTS: 강좌가 없는 강사 1명", GR, 3, gap=40)
W("notin-null", o, "NOT IN 목록에 NULL이 하나라도 섞이면 결과가 0줄이 되고, NOT EXISTS는 맞게 나와요. 강좌를 하나도 맡지 않은 강사를 찾아요. 먼저 강좌 표를 보면 5번 아쿠아로빅은 강사 칸이 비어 있어요. NULL이에요. NOT IN으로 물으면 0 rows가 나와요. 8번 윤태호 강사는 어느 강좌에도 없는데도 안 나와요. NOT IN은 목록의 모든 값과 다른지 확인하는데, NULL과 비교하면 36에서 본 것처럼 참도 거짓도 아닌 모름이 돼요. 그래서 어떤 강사도 통과하지 못해요. NOT EXISTS는 줄이 있는지만 물어서 윤태호 강사가 맞게 나와요. 41에서 NOT IN 목록에 NULL을 조심하자고 했던 경우예요. 빈칸이 있을 수 있는 열이면 NOT EXISTS를 써요." + REAL)

# =====================================================================
# part 3: IN, EXISTS, JOIN compared
# =====================================================================
o = frame("cmp", EB3, "목록이면 IN, 있는지만 물으면 EXISTS, 두 표의 열이 필요하면 JOIN", C3)
rows_ = [[kw("IN (서브쿼리)", C2) + f" <span style='color:{GRAY};font-size:22px'>41</span>", "안쪽이 목록을 만들어요", "목록에 든 회원", "NULL이 섞이면 NOT IN 0줄"],
         [kw("EXISTS (서브쿼리)", C3) + f" <span style='color:{GRAY};font-size:22px'>42</span>", "바깥 줄마다 있나요? 물어요", "신청이 있는/없는 회원", "바깥과 잇는 조건 꼭 적기"],
         [kw("JOIN … ON", C1) + f" <span style='color:{GRAY};font-size:22px'>40</span>", "두 표를 옆으로 붙여요", "회원 이름과 강좌 이름 같이", "한 회원이 여러 줄로 나와요"]]
tb, y0 = table(96, 240, ["쓰는 것", "하는 일", "어울리는 질문", "조심할 것"], rows_, [400, 440, 430, 458], "cmp-tb", size=27, rh=140, order=1, stagger=True)
o += tb
o.append(caption("같은 회원을 찾는 질문은 셋 다 쓸 수 있어요. 지울 때와 NULL이 섞일 수 있을 때는 NOT EXISTS가 안전해요.", y0 + 3 * 140 + 60, 4, size=29))
W("cmp", o, "목록이 필요하면 IN, 있는지만 물으면 EXISTS, 두 표의 열을 같이 봐야 하면 JOIN을 써요. IN은 41에서 배웠어요. 안쪽 쿼리가 먼저 목록을 만들고, 바깥은 그 목록에 들어 있는지 봐요. EXISTS는 오늘 배웠어요. 바깥 줄마다 안쪽에 있는지 물어서 t, f로 답해요. JOIN은 40에서 배웠어요. 두 표를 옆으로 붙여서 회원 이름과 강좌 이름을 한 줄에 같이 보여 줘요. 다만 한 회원이 여러 번 신청했으면 여러 줄로 나와요. 신청 기록이 없는 회원을 지울 때처럼 없는 것을 찾을 때는 NOT EXISTS가 안전해요.")

# =====================================================================
# part 4: SELECT first, then DELETE with the same WHERE
# =====================================================================
o = frame("del-check", EB4, "지우기 전에 같은 WHERE로 SELECT부터 해 봐요", C4)
L = P("del-check")
t = PT(L, 96, 214, size=26, w=1728, lh=1.45, tid="t-dc", maxb=990)
w1, w2 = li(t, "WHERE NOT EXISTS"), li(t, "WHERE NOT EXISTS", li(t, "DELETE FROM") + 1)
o.append(t.html())
WH = "WHERE NOT EXISTS (SELECT 1 FROM enrollments e WHERE e.member_id = m.member_id)"
o.append(rbox(t, w1, WH, 1, IN_T))
o += tag(t, li(t, "40 | 채윤서"), "① 지워질 줄을 먼저 봐요", OR, 1, gap=40)
o.append(rbox(t, w2, WH, 2, IN_T))
xs_ = round(t.sx(w1, WH) + t.sw(WH) + 22)
xv_ = xs_ + 60
o.append(svg(arrow_path(f"M{xs_},{t.cy(w1):.0f} H{xv_ - 20} Q{xv_},{t.cy(w1):.0f} {xv_},{t.cy(w1) + 20:.0f} V{t.cy(w2) - 20:.0f} Q{xv_},{t.cy(w2):.0f} {xv_ - 20},{t.cy(w2):.0f} H{xs_ + 2}", LC[OR], 4) + head_at(xs_, t.cy(w2), 180, LC[OR]), 2))
o += tag(t, li(t, "DELETE FROM"), "② WHERE를 그대로 복사해요", OR, 2, gap=40)
o.append(rbox(t, li(t, "DELETE 1"), "DELETE 1", 3, "#7FD18B"))
o += tag(t, li(t, "DELETE 1"), "본 것과 같은 1줄만 지워졌어요", GR, 3, gap=40)
o.append(caption("SELECT 줄 수와 DELETE 뒤의 숫자가 같은지 봐요. 다르면 WHERE가 바뀐 거예요.", t.y + t.h + 26, 4, size=28))
W("del-check", o, "지우기 전에는 같은 WHERE로 SELECT부터 해 봐요. 먼저 SELECT로 신청 기록이 없는 회원을 찾았어요. 채윤서 회원 한 명이에요. 그다음 이 WHERE를 그대로 복사해서 DELETE FROM members 뒤에 붙였어요. DELETE에도 표 별명 m을 붙일 수 있어요. RETURNING으로 지운 줄을 바로 보여 줬어요. SELECT에서 본 1줄과 DELETE 1의 숫자가 같아요. 지운 줄은 되돌릴 수 없으니 지우기 전에 늘 SELECT로 먼저 봐요. 실행한 뒤에도 취소할 수 있게 묶어 두는 방법은 다음 43 챕터의 트랜잭션에서 배워요." + REAL, ("p4", "지우기와 표 비우기"))

# =====================================================================
# part 4: a member with enrollments cannot be deleted
# =====================================================================
o = frame("fk-err", EB4, "신청 기록이 있는 회원을 지우려고 하면 외래 키가 막아요", C4)
L = P("fk-err")
t = PT(L, 96, 214, size=22, w=1728, lh=1.5, tid="t-fk", maxb=500)
o.append(t.html())
o.append(rbox(t, li(t, "DETAIL"), "Key (member_id)=(10) is still referenced", 1, "#FF9C94"))
o += tag(t, li(t, "DETAIL"), "아직 쓰는 줄이 있어요", RED, 1, gap=40)
# picture: members 10 <- enrollments rows
PY = t.y + t.h + 60
g, (_, _, MW_, MH_) = grid(160, PY + 50, ["member_id", "name"], [["10", "임준서"]], [180, 160], 62, "fk-m", MAG, size=26)
o.append(p(f"position:absolute;left:160px;top:{PY}px;font-family:{MONO};font-size:26px;font-weight:700;color:{MAG}", "members (부모)"))
o.append(g)
g2, (_, _, EW2, EH2) = grid(1100, PY + 50, ["id", "member_id", "status"], [["2", "10", "취소"], ["54", "10", "취소"], ["72", "10", "완료"]], [120, 200, 160], 62, "fk-e", GRAY, size=26)
o.append(p(f"position:absolute;left:1100px;top:{PY}px;font-family:{MONO};font-size:26px;font-weight:700;color:{GRAY}", "enrollments (자식, 5줄)"))
o.append(g2)
for k in range(3):
    yy = PY + 50 + 62 * (k + 1) + 31
    o.append(svg(arrow_path(f"M1094,{yy} C900,{yy} 700,{PY + 50 + 93} 512,{PY + 50 + 93}", MAG, 3) + head_at(510, PY + 50 + 93, 180, MAG), 2))
o.append(p(f"position:absolute;left:160px;top:{PY + 200}px;font-size:26px;font-weight:700;color:{MAG};white-space:nowrap", "member_id REFERENCES members", bi("rise", 2)))
o.append(p(f"position:absolute;left:1100px;top:{PY + 312}px;font-size:24px;color:{GRAY}", "79, 95번 줄도 10번 회원이에요", bi("rise", 2)))
o.append(caption("앞 장의 NOT EXISTS가 신청 기록이 없는 회원만 고른 덕분에 이 오류 없이 지울 수 있었어요.", PY + 400, 3, size=28))
W("fk-err", o, "신청 기록이 있는 회원을 지우려고 하면 외래 키가 막아서 ERROR가 나요. 10번 임준서 회원을 지우려고 했어요. DETAIL을 읽으면 member_id 10을 enrollments 표가 아직 가리키고 있다는 뜻이에요. 37에서 배운 외래 키예요. 신청 표의 member_id가 회원 표를 가리키니까, 가리키는 줄이 남아 있는 부모 줄은 지울 수 없어요. 앞 장에서 NOT EXISTS로 신청 기록이 없는 회원만 고른 덕분에 이 오류 없이 지울 수 있었어요. 이 회원을 꼭 지워야 한다면 37에서 본 것처럼 자식 줄인 신청 기록부터 지워요." + REAL)

# =====================================================================
# part 4: DELETE, TRUNCATE, DROP (picture)
# =====================================================================
o = frame("three-pic", EB4, "DELETE는 고른 줄, TRUNCATE는 모든 줄, DROP은 표까지 없애요", C4)
COLW = 540
items = [("DELETE FROM 표 WHERE …", "고른 줄만 지워요", "표와 다른 줄은 남아요", "WHERE를 빼면 모든 줄", 2, MAG),
         ("TRUNCATE 표", "모든 줄을 한 번에 비워요", "빈 표는 남아요", "RESTART IDENTITY로 번호 다시 1부터 (37)", 0, OR),
         ("DROP TABLE 표", "표를 통째로 없애요", "표도 열도 남지 않아요", "다시 쓰려면 CREATE TABLE부터", -1, RED)]
for k, (c_, h_, s_, n_, keep, col) in enumerate(items):
    x = 96 + k * (COLW + 54)
    od = k + 1
    o.append(p(f"position:absolute;left:{x}px;top:228px;height:60px;padding:0 18px;border-radius:12px;background:{col};font-family:{MONO};font-size:25px;font-weight:700;line-height:60px;color:#FFFFFF;white-space:nowrap", e(c_), bi("pop", od)))
    # a small table picture: header + 4 rows
    TX, TY, TW_, RH_ = x, 330, 420, 56
    frame_col = col if keep >= 0 else "#D6D2C8"
    dash = "dashed" if keep < 0 else "solid"
    o.append(f'<div{bi("fade", od)} style="position:absolute;left:{TX}px;top:{TY}px;width:{TW_}px;height:{RH_ * 5}px;border:3px {dash} {frame_col};border-radius:12px;background:{"#FFFFFF" if keep >= 0 else "transparent"}"></div>')
    if keep >= 0:
        o.append(f'<div{bi("fade", od)} style="position:absolute;left:{TX + 3}px;top:{TY + 3}px;width:{TW_ - 6}px;height:{RH_ - 3}px;background:{col}22;border-radius:9px 9px 0 0"></div>')
        o.append(p(f"position:absolute;left:{TX + 24}px;top:{TY + 12}px;font-family:{MONO};font-size:22px;font-weight:700;color:{col}", "request_id | name …", bi("fade", od)))
    for r in range(4):
        yy = TY + RH_ * (r + 1) + 14
        stay = keep == 2 and r in (0, 2)
        if keep < 0:
            continue
        colr = "#E4E1DA" if (keep == 2 and not stay) or keep == 0 else "#9AA3B5"
        style_ = f"border:2px dashed #C9C4B8;background:transparent" if colr == "#E4E1DA" else f"background:{colr}"
        o.append(f'<div{bi("fade", od)} style="position:absolute;left:{TX + 24}px;top:{yy}px;width:{[300, 240, 280, 220][r]}px;height:24px;border-radius:12px;{style_}"></div>')
    if keep < 0:
        o.append(p(f"position:absolute;left:{TX}px;top:{TY + RH_ * 2 + 20}px;width:{TW_}px;text-align:center;font-size:26px;font-weight:700;color:{RED}", "표가 없어요", bi("fade", od)))
    o.append(p(f"position:absolute;left:{x}px;top:{TY + RH_ * 5 + 30}px;width:{COLW}px;font-size:30px;font-weight:700;color:{INK}", e(h_), bi("rise", od)))
    o.append(p(f"position:absolute;left:{x}px;top:{TY + RH_ * 5 + 82}px;width:{COLW}px;font-size:25px;line-height:1.5;color:{SUB}", e(s_) + "<br>" + e(n_), bi("rise", od)))
o.append(caption("세 명령 모두 되돌릴 수 없어요. 무엇을 지우는지 먼저 확인해요.", 900, 4, size=30))
W("three-pic", o, "DELETE는 고른 줄만, TRUNCATE는 모든 줄을, DROP TABLE은 표까지 없애요. 왼쪽 DELETE는 WHERE에 맞는 줄만 지우고 나머지 줄과 표는 그대로 둬요. WHERE를 빼면 모든 줄을 지워요. 가운데 TRUNCATE는 모든 줄을 한 번에 비워요. 열과 규칙이 있는 빈 표는 남아요. 37에서 본 RESTART IDENTITY를 붙이면 SERIAL 번호도 다시 1부터 세요. 오른쪽 DROP TABLE은 표를 통째로 없애요. 다시 쓰려면 CREATE TABLE부터 해야 해요. 세 명령 모두 실행하면 바로 저장돼서 되돌릴 수 없어요.")

# =====================================================================
# part 4: DELETE, TRUNCATE, DROP (real)
# =====================================================================
o = frame("three", EB4, "명단 표에 세 명령을 차례로 쳐 보면 줄 수가 9, 0, 표 없음이 돼요", C4)
L = P("three")
t = PT(L, 96, 214, size=24, w=1300, lh=1.42, tid="t-three", maxb=1000)
o.append(t.html())
TBG = T_BG
segs = [(li(t, "DELETE FROM"), li(t, "(1 row)")), (li(t, "TRUNCATE"), li(t, "(1 row)", li(t, "TRUNCATE"))), (li(t, "DROP TABLE"), len(t.rows) - 1)]
for k, (a_, b_) in enumerate(segs):
    o.append(lspot(k + 1, t.x, t.y, t.w, t.h, t.top(a_) - 4, (b_ - a_ + 1) * t.lp + 8, bg=TBG, bar=[MAG, OR, RED][k]))
o.append(lspot_off(4))
notes_ = [("DELETE 7", "전화번호 미등록 7줄만 지워서 9줄 남아요", MAG), ("TRUNCATE TABLE", "모두 비워서 0줄", OR), ("relation … does not exist", "표가 없어졌어요", RED)]
for k, (h_, b_, c_) in enumerate(notes_):
    y = 260 + k * 230
    o.append(p(f"position:absolute;left:1440px;top:{y}px;width:384px;font-family:{MONO};font-size:24px;font-weight:700;color:{c_}", e(h_), bi("rise", k + 1)))
    o.append(p(f"position:absolute;left:1440px;top:{y + 44}px;width:384px;font-size:25px;line-height:1.5;color:{SUB}", e(b_), bi("rise", k + 1)))
W("three", o, "명단 표에 세 명령을 차례로 쳐 보면 줄 수가 9, 0, 그다음엔 표가 없다는 오류로 바뀌어요. 명단 표에는 16줄이 들어 있었어요. 먼저 DELETE로 전화번호 미등록 7줄만 지웠어요. 9줄이 남아요. 다음 TRUNCATE로 남은 줄을 다 비웠어요. COUNT가 0이에요. 표는 남아 있어서 COUNT를 칠 수 있어요. 마지막으로 DROP TABLE로 표를 없앴어요. 이제 COUNT를 치면 relation does not exist, 그런 표가 없다는 ERROR가 나요." + REAL)

# =====================================================================
# part 5: column count and order
# =====================================================================
o = frame("err-cols", EB5, "넣을 열과 SELECT 칸은 개수도 순서도 맞아야 해요", C5)
La, Lb = P("err-count"), P("err-order")
t1 = PT(La, 96, 214, size=23, w=1728, lh=1.45, tid="t-ec1", maxb=520)
t2 = PT(Lb, 96, t1.y + t1.h + 40, size=23, w=1728, lh=1.45, tid="t-ec2", maxb=900)
o.append(t1.html())
o.append(t2.html())
o.append(rbox(t1, li(t1, "ERROR"), "more target columns than expressions", 1, "#FF9C94"))
o += tag(t1, li(t1, "SELECT member_id"), "열은 4개, 칸은 3개", RED, 1, gap=40)
o.append(rbox(t2, li(t2, "SELECT name"), "name, member_id", 2, "#FF9C94"))
o += tag(t2, li(t2, "ERROR"), "이름을 숫자 칸에 넣으려 했어요", RED, 2, gap=30)
o.append(caption("고칠 때는 첫 줄 괄호의 열을 하나씩 읽으면서 SELECT 칸을 같은 순서로 맞춰요.", t2.y + t2.h + 30, 3, size=28))
W("err-cols", o, "넣을 열과 SELECT 칸은 개수도 순서도 맞아야 해요. 위는 넣을 열은 네 개인데 SELECT 칸을 세 개만 적었어요. 날짜를 빠뜨렸어요. ERROR는 넣을 열이 값보다 많다는 뜻이에요. 아래는 개수는 맞는데 name과 member_id의 순서를 바꿔 적었어요. 이름이 첫 번째 열인 member_id에 들어가려다가 숫자 열에 글자를 넣을 수 없다는 ERROR가 났어요. INSERT는 열 이름이 아니라 순서로 짝을 지어서 생긴 오류예요. 자료형이 같은 두 열을 바꿔 적으면 오류 없이 틀린 값이 들어가니 더 조심해요." + REAL, ("p5", "오류와 함정"))

# =====================================================================
# part 5: EXISTS without the linking condition
# =====================================================================
o = frame("err-link", EB5, "EXISTS 안쪽에 바깥과 잇는 조건을 빠뜨리면 0명 아니면 40명이에요", C5)
L = P("err-link")
t = PT(L, 96, 214, size=26, w=1180, lh=1.45, tid="t-el", maxb=990)
o.append(t.html())
r1, r2, r3 = li(t, "     1"), li(t, "     0"), li(t, "    40")
o.append(rbox(t, li(t, "e.member_id = m.member_id"), "e.member_id = m.member_id", 1, "#7FD18B"))
o += tag(t, r1, "맞아요: 1명", GR, 1, gap=40)
o.append(rbox(t, li(t, "FROM enrollments e);"), "(SELECT 1 FROM enrollments e)", 2, "#FF9C94"))
o += tag(t, r2, "0명", RED, 2, gap=40)
o += tag(t, r3, "40명 전부", RED, 3, gap=40)
o += side(1320, 250, 504, "잇는 조건이 없으면", "안쪽이 회원마다 같은 질문, \"신청 표에 줄이 있나요?\"가 돼요. 신청 표에는 늘 줄이 있으니 답이 모두 같아요.", RED, 2, hsize=30, bsize=25)
o += side(1320, 580, 504, "DELETE였다면", "NOT EXISTS는 아무도 안 지우고, EXISTS는 40명 모두 지우려고 해요. 지우기 전에 SELECT로 줄 수를 봐요.", INK, 4, hsize=30, bsize=25)
W("err-link", o, "EXISTS 안쪽에 바깥 줄과 잇는 조건을 빠뜨리면 결과가 0명 아니면 40명이 돼요. 첫 쿼리는 e.member_id = m.member_id가 있어서 신청이 없는 회원 1명을 맞게 셌어요. 두 번째는 이 조건을 빠뜨렸어요. 그러면 안쪽이 회원과 상관없이 신청 표에 줄이 있는지만 물어요. 신청 표에는 늘 줄이 있으니 NOT EXISTS는 모두 거짓이라 0명이에요. 세 번째 EXISTS는 모두 참이라 40명 전부예요. 오류 메시지가 없어서 알아채기 어려워요. 이게 DELETE였다면 아무도 안 지우거나 40명 모두 지우려고 했을 거예요. 그래서 지우기 전에 같은 WHERE로 SELECT부터 해요." + REAL)

# =====================================================================
# part 5: ADD COLUMN NOT NULL
# =====================================================================
o = frame("err-notnull", EB5, "줄이 있는 표에 NOT NULL 열만 더하면 막혀요. DEFAULT를 같이 줘요", C5)
L = P("err-notnull")
t = PT(L, 96, 214, size=26, w=1728, lh=1.5, tid="t-enn", maxb=760)
o.append(t.html())
o.append(rbox(t, li(t, "ERROR"), "contains null values", 1, "#FF9C94"))
o += tag(t, li(t, "ERROR"), "있던 14줄의 새 칸이 비어요", RED, 1, gap=40)
o.append(under(t, li(t, "DEFAULT '미정'"), "DEFAULT '미정'", 2, "#7FD18B"))
o.append(spot_rows(t, li(t, "1 | 미정"), li(t, "3 | 미정"), 3, x=t.x + 10, w=420))
o.append(spot_off(4))
o.append(caption("빈 표라면 NOT NULL 열을 그냥 더해도 돼요. 채울 줄이 없어서 비는 칸이 없기 때문이에요.", t.y + t.h + 30, 4, size=28))
W("err-notnull", o, "줄이 이미 있는 표에 NOT NULL 열만 더하면 ERROR가 나고, DEFAULT를 같이 주면 들어가요. 강좌 표에는 14줄이 있어요. 새 열 class_days를 비울 수 없게 NOT NULL로 더하면, 있던 14줄의 새 칸이 모두 비어서 규칙에 맞지 않아요. ERROR는 class_days 열에 NULL 값이 있다는 뜻이에요. DEFAULT 미정을 같이 적으면 있던 줄에도 미정이 들어가서 NOT NULL을 지킬 수 있어요. 37에서 ALTER TABLE로 규칙을 붙일 때 이미 맞지 않는 줄이 있으면 막혔던 것과 같은 이유예요." + REAL)

# =====================================================================
# part 6: real case 1, move cancelled enrollments
# =====================================================================
o = frame("r-move", EB6, "취소한 신청을 보관 표로 옮겨요: 같은 WHERE로 넣고 지우기", C6)
L = P("r-move")
t = PT(L, 96, 214, size=24, w=1180, lh=1.45, tid="t-rm", maxb=1000)
o.append(t.html())
i1, i2 = li(t, "FROM enrollments WHERE status"), li(t, "DELETE FROM enrollments WHERE")
o.append(rbox(t, i1, "WHERE status = '취소'", 1, IN_T))
o.append(rbox(t, i2, "WHERE status = '취소'", 1, IN_T))
o.append(rbox(t, li(t, "INSERT 0 20"), "20", 2, "#7FD18B"))
o.append(rbox(t, li(t, "DELETE 20"), "20", 2, "#7FD18B"))
o += tag(t, li(t, "INSERT 0 20"), "옮긴 줄", GR, 2, gap=40)
o += tag(t, li(t, "DELETE 20"), "지운 줄, 같은 20", GR, 2, gap=40)
o += tag(t, li(t, "   167"), "187 - 20 = 167", GR, 3, gap=40)
o += side(1320, 250, 504, "넣을 열을 안 적으면", "보관 표의 열 순서 그대로 SELECT 칸을 맞춰요. 네 칸 모두 같은 순서예요.", INK, 1, hsize=30, bsize=25)
o += side(1320, 520, 504, "둘 중 하나만 되면?", "INSERT 뒤에 컴퓨터가 꺼지면 같은 줄이 두 표에 다 남아요. 둘을 한 묶음으로 처리하는 법은 43 트랜잭션에서 배워요.", RED, 4, hsize=30, bsize=25)
W("r-move", o, "취소한 신청을 보관 표로 옮겨 볼게요. 옮기기는 같은 WHERE로 넣고 지우는 두 문장이에요. 먼저 보관할 cancelled 표를 만들어요. INSERT 뒤에 넣을 열 괄호를 적지 않으면 표의 모든 열을 만든 순서대로 채워요. 그래서 SELECT 칸도 같은 순서로 네 개를 적었어요. 취소 20줄이 들어갔어요. 그다음 같은 WHERE로 신청 표에서 지웠어요. DELETE 20, 넣은 줄 수와 같아요. 신청 표는 187줄에서 167줄이 됐어요. 그런데 INSERT만 되고 DELETE 전에 문제가 생기면 같은 줄이 두 표에 다 남아요. 두 문장을 한 묶음으로 처리하는 방법은 다음 43 챕터의 트랜잭션에서 배워요." + REAL, ("p6", "실제 상황"))

# =====================================================================
# part 6: real case 2, give the course with no instructor a teacher
# =====================================================================
o = frame("r-teacher", EB6, "강좌가 없는 강사를 강사가 없는 강좌에 맡겨요", C6)
L = P("r-teacher")
t = PT(L, 96, 214, size=24, w=1728, lh=1.45, tid="t-rt", maxb=990)
o.append(t.html())
a8 = li(t, "8 | 윤태호")
a5 = li(t, "5 | 아쿠아로빅  |        1")
o.append(spot_rows(t, a8, a8, 1, x=t.x + 10, w=560))
o += tag(t, a8, "① NOT EXISTS: 맡은 강좌가 없는 수영 강사", OR, 1, gap=60)
o.append(spot_rows(t, a5, a5, 2, x=t.x + 10, w=560))
o += tag(t, a5, "② IS NULL: 강사가 없는 수영 강좌", OR, 2, gap=60)
o.append(spot_off(3))
sl = li(t, "SET instructor_id = (")
o.append(rbox(t, sl, "(SELECT instructor_id FROM instructors WHERE name = '윤태호')", 3, IN_T))
o += tag(t, sl, "값 하나", OR, 3, gap=30)
o.append(rbox(t, li(t, "5 | 아쿠아로빅  |             8"), "8", 4, "#7FD18B"))
o += tag(t, li(t, "5 | 아쿠아로빅  |             8"), "번호를 손으로 안 적었어요", GR, 4, gap=40)
W("r-teacher", o, "강좌가 없는 강사를 강사가 없는 강좌에 맡겨요. 먼저 NOT EXISTS로 맡은 강좌가 하나도 없는 강사를 찾아요. 8번 윤태호 강사예요. 종목 번호 1, 수영 강사예요. 다음으로 강사 칸이 비어 있는 강좌를 찾아요. 5번 아쿠아로빅, 역시 수영 강좌예요. 그래서 UPDATE로 아쿠아로빅의 강사를 정해요. SET의 값 자리에 41에서 배운 값 하나가 나오는 서브쿼리를 넣었어요. 이름이 윤태호인 강사의 번호를 PostgreSQL이 찾아서 넣어 줘요. RETURNING을 보면 강사 번호 8이 들어갔어요." + REAL)

# =====================================================================
# part 6: real case 3, clean the contact list
# =====================================================================
o = frame("r-contact", EB6, "이메일을 받은 회원은 명단에서 지워요", C6)
L = P("r-contact")
t = PT(L, 96, 214, size=24, w=1728, lh=1.45, tid="t-rc", maxb=1000)
o.append(t.html())
u1, u2 = li(t, "member_id = 3;"), li(t, "member_id = 10;")
o += tag(t, u1, "① 전화로 받은 이메일을 적어요", BL, 1, gap=40)
inl = li(t, "AND member_id IN (")
o.append(rbox(t, inl, "member_id IN (SELECT member_id FROM members WHERE email IS NOT NULL)", 2, IN_T))
o += tag(t, li(t, "WHERE reason"), "② 이메일 사유 줄 중에서", OR, 2, gap=40)
o.append(spot_rows(t, li(t, "1 |         3"), li(t, "5 |        10"), 3, x=t.x + 10, w=560))
o.append(spot_off(4))
o += tag(t, li(t, "   14"), "16줄에서 2줄 빠졌어요", GR, 4, gap=40)
W("r-contact", o, "이메일을 받은 회원은 명단에서 지워요. 전화로 박도현, 임준서 회원의 이메일을 받아서 UPDATE로 회원 표에 적었어요. 이제 명단에서 이메일 미등록 사유 줄 중 회원 표에 이메일이 생긴 회원을 지워요. 명단 표와 회원 표가 따로 있어서 WHERE에 IN 서브쿼리를 넣었어요. RETURNING을 보면 3번과 10번, 두 줄이 지워졌어요. 임준서 회원은 전화번호 미등록 줄이 하나 더 있었는데, reason 조건이 있어서 그 줄은 남았어요. 명단은 16줄에서 14줄이 됐어요." + REAL)

# =====================================================================
# summary
# =====================================================================
o = frame("sum", "정리", "다른 표를 보고 할 일마다 쓰는 모양이 정해져 있어요", INK)
rows_ = [["다른 표에서 골라 넣어요", kw("INSERT INTO 표 (열, …) SELECT 칸, … FROM … WHERE …", C1)],
         ["UNION 결과에 날짜 글자가 있어요", kw("CAST('2026-11-19' AS DATE)  또는  '2026-11-19'::DATE", C1)],
         ["있는 표에 열을 더해요", kw("ALTER TABLE 표 ADD COLUMN 열 자료형 [DEFAULT 값]", C2)],
         ["여러 열을 한 번에, 다른 표를 보고 고쳐요", kw("UPDATE … SET a = …, b = … WHERE id IN (SELECT …)", C2)],
         ["다른 표에 있는(없는) 줄만 골라요", kw("WHERE [NOT] EXISTS (SELECT 1 FROM … WHERE 잇는 조건)", C3)],
         ["지워요, 비워요, 없애요", kw("DELETE … WHERE  /  TRUNCATE 표  /  DROP TABLE 표", C4)]]
tb, y0 = table(96, 220, ["이럴 때", "이렇게 써요"], rows_, [620, 1108], "sum-tb", size=25, rh=86, order=1, stagger=False, bold_first=False)
o += tb
yy = y0 + 6 * 86 + 40
o.append(p(f"position:absolute;left:96px;top:{yy}px;font-size:28px;font-weight:700;color:{INK}", "다음 43 챕터: 넣고 지우는 여러 문장을 한 묶음으로 처리하고, 잘못 친 UPDATE를 되돌리는 트랜잭션(BEGIN, COMMIT, ROLLBACK)", bi("rise", 2)))
W("sum", o, "다른 표를 보고 넣고, 고치고, 지울 때 쓰는 모양을 한 표로 모았어요. 다른 표에서 골라 넣을 때는 INSERT 뒤에 SELECT를 붙여요. UNION으로 합친 결과에 날짜 글자가 있으면 CAST나 콜론 두 개로 DATE로 바꿔요. 있는 표에 열을 더할 때는 ALTER TABLE ADD COLUMN이에요. 여러 열은 SET 뒤에 쉼표로 잇고, 다른 표를 보고 고를 때는 WHERE에 서브쿼리를 넣어요. 다른 표에 있는지 없는지만 물을 때는 EXISTS와 NOT EXISTS예요. 지울 때는 DELETE, 모두 비울 때는 TRUNCATE, 표를 없앨 때는 DROP TABLE이에요. 오늘 본 명령은 치는 순간 저장돼요. 다음 43 챕터에서는 여러 문장을 한 묶음으로 처리하고 되돌리는 트랜잭션을 배워요.")

o = frame("cheat", "정리", "한 장 요약", INK)
groups = [("넣기", C1, [("INSERT INTO 표 (열, …) SELECT …", "VALUES 자리에 SELECT"), ("'이메일 미등록' AS reason", "모든 줄에 같은 값"), ("CAST(값 AS DATE), 값::DATE", "UNION 날짜는 꼭 바꿔요")]),
          ("고치기", C2, [("ALTER TABLE 표 ADD COLUMN 열 …", "있던 줄은 NULL이나 DEFAULT"), ("SET a = …, b = …", "여러 열을 한 번에"), ("WHERE id IN (SELECT …)", "INTEGER 열은 반올림돼요")]),
          ("묻기와 지우기", C3, [("WHERE NOT EXISTS (SELECT 1 …)", "잇는 조건을 꼭 적어요"), ("SELECT 먼저, 같은 WHERE로 DELETE", "줄 수가 같은지 봐요"), ("DELETE / TRUNCATE / DROP", "고른 줄 / 모든 줄 / 표까지")])]
GW = 560
for i, (t_, c, rows) in enumerate(groups):
    x = 96 + i * (GW + 24)
    o.append(p(f"position:absolute;left:{x}px;top:220px;font-size:30px;font-weight:700;color:{c}", e(t_)))
    o.append(f'<div style="position:absolute;left:{x}px;top:270px;width:{GW}px;height:3px;background:{c}"></div>')
    for j, (k_, d_) in enumerate(rows):
        y = 300 + j * 120
        fs = 22 if tw(k_, 22) < GW - 10 else 19
        if tw(k_, fs) > GW - 4:
            WARN.append(f"cheat: '{k_}' too wide")
        o.append(p(f"position:absolute;left:{x}px;top:{y}px;width:{GW}px;font-family:{MONO};font-size:{fs}px;font-weight:700;color:{INK};white-space:nowrap", e(k_)))
        o.append(p(f"position:absolute;left:{x}px;top:{y + 42}px;width:{GW}px;font-size:23px;color:{SUB}", e(d_)))
o.append(f'<div style="position:absolute;left:96px;top:690px;width:1728px;height:2px;background:{LINE}"></div>')
o.append(p(f"position:absolute;left:96px;top:716px;font-size:26px;font-weight:700;color:{RED}", "막히면"))
errs = [("is of type date but expression is of type text", "CAST나 ::DATE"), ("INSERT has more target columns than expressions", "열과 칸 개수 맞추기"),
        ("violates foreign key constraint", "자식 줄부터, 또는 NOT EXISTS로 고르기"), ("contains null values", "ADD COLUMN에 DEFAULT")]
for k, (a_, b_) in enumerate(errs):
    x = 96 + (k % 2) * 864
    y = 770 + (k // 2) * 90
    o.append(p(f"position:absolute;left:{x}px;top:{y}px;width:840px;font-family:{MONO};font-size:22px;font-weight:700;color:{RED};white-space:nowrap", e(a_)))
    o.append(p(f"position:absolute;left:{x}px;top:{y + 38}px;width:840px;font-size:23px;color:{SUB}", e(b_)))
W("cheat", o, "오늘 쓴 명령을 넣기, 고치기, 묻기와 지우기로 모았어요. 넣기는 VALUES 자리에 SELECT를 붙이고, 표에 없는 글자는 모든 줄에 같은 값이 돼요. UNION으로 합친 날짜는 CAST나 콜론 두 개로 바꿔요. 고치기는 ADD COLUMN으로 열을 더하고, SET 뒤에 쉼표로 여러 열을 고치고, WHERE에 서브쿼리를 넣어요. 묻기와 지우기는 NOT EXISTS에 잇는 조건을 꼭 적고, 지우기 전에 같은 WHERE로 SELECT부터 해요. 아래는 오늘 본 오류 네 가지와 고치는 방법이에요.", ("end", "정리"))

# =====================================================================
# toc
# =====================================================================
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
PL = [(C1, EB1[3:], "INSERT … SELECT, 열 짝 맞추기, 고정값 열, VALUES와 비교, UNION과 날짜, CAST와 ::", "pair", "union"),
      (C2, EB2[3:], "ALTER TABLE ADD COLUMN, SET 여러 열, INTEGER 반올림, WHERE IN (서브쿼리)", "alter", "sub-upd"),
      (C3, EB3[3:], "EXISTS와 SELECT 1, 바깥 줄마다 묻기, NOT EXISTS, NOT IN과 NULL, IN·JOIN과 비교", "ex-min", "cmp"),
      (C4, EB4[3:], "SELECT 먼저 보고 DELETE, 외래 키 오류, DELETE·TRUNCATE·DROP", "del-check", "three"),
      (C5, EB5[3:], "열 개수와 순서, 잇는 조건 빠뜨리기, NOT NULL 열 더하기", "err-cols", "err-notnull"),
      (C6, EB6[3:], "취소 신청 옮기기, 강사 맡기기, 명단 정리", "r-move", "r-contact")]
o = frame("toc", "", "오늘의 순서", INK)
for i, (c, h_, s_, a_, b_) in enumerate(PL):
    y = 214 + i * 112
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:2px;background:{LINE}"></div>')
    o.append(p(f"position:absolute;left:96px;top:{y + 22}px;width:80px;font-size:48px;font-weight:900;line-height:1.5;color:{c}", str(i + 1)))
    o.append(p(f"position:absolute;left:190px;top:{y + 18}px;font-size:34px;font-weight:700;color:{INK}", e(h_)))
    o.append(p(f"position:absolute;left:190px;top:{y + 70}px;font-size:22px;color:{SUB};white-space:nowrap", e(s_)))
    o.append(p(f"position:absolute;left:1524px;top:{y + 40}px;width:300px;text-align:right;font-size:28px;font-weight:700;color:{GRAY}", f"{page[a_]}–{page[b_]}쪽"))
o.append(f'<div style="position:absolute;left:96px;top:{214 + len(PL) * 112}px;width:1728px;height:2px;background:{LINE}"></div>')
o.append(p(f"position:absolute;left:96px;top:{214 + len(PL) * 112 + 34}px;font-size:26px;color:{SUB}", f"{page['why']}–{page['min']}쪽은 들어가기, {page['sum']}–{page['cheat']}쪽은 정리예요. 예제는 38부터 쓰는 스포츠 센터 수업 데이터예요."))
o = [x for x in o if 'id="eyebrow"' not in x]
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(o) + f"\n<aside>{e('여섯 파트로 나눴어요. 1파트는 다른 표에서 고른 줄을 INSERT로 넣어요. 2파트는 열을 더하고, 여러 열을 한 번에, 다른 표를 보고 고쳐요. 3파트는 다른 표에 줄이 있는지만 묻는 EXISTS를 새로 배워요. 4파트는 그 조건으로 지우고, DELETE, TRUNCATE, DROP을 비교해요. 5파트는 자주 나는 오류, 6파트는 실제 상황 세 가지예요. 트랜잭션은 다음 43 챕터에서 다뤄요.')}</aside>\n</section>\n")

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-19T00:00:00Z"}, "lists": "css", "title": "SQL 7 (다른 표를 보고 넣고, 고치고, 지우기)", "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
for w_ in WARN:
    print("WARN", w_)
print(len(ORDER), "slides")
