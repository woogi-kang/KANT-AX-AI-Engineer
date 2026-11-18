r"""Generates every slide of the SQL 4 deck (39, aggregate functions, GROUP BY, HAVING) and slides/deck.json.

Story: 36 picked rows; it could not say how much November earned without adding 63 rows by hand. An aggregate
function folds many rows into one value (COUNT, MIN, MAX, SUM, AVG, ROUND); GROUP BY first puts rows with the same
value into one bucket and folds every bucket; HAVING keeps only the buckets that pass. Part 1 the five functions,
part 2 COUNT(*), COUNT(column), COUNT(DISTINCT column), 0 vs NULL, part 3 GROUP BY one and two columns, part 4 HAVING,
WHERE vs HAVING and the order SQL runs, part 5 DISTINCT and the dict counting of 15, part 6 errors and four real reports.
Tables: the sports-center class database shared by 38 to 41 (sports.sql).

Every psql line comes from tools/demo.py (real postgres:18, in tools/out.json).
Usage (in 39-sql-aggregate): python3 tools/gen.py slides
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


def ttw(s, size):
    """terminal width: a Hangul letter takes two cells (1.2em) like in a real terminal"""
    return sum((1.2 if (0xAC00 <= ord(c) <= 0xD7A3 or 0x3130 <= ord(c) <= 0x318F) else 0.6) for c in s) * size


HANGUL = re.compile(r"([\uac00-\ud7a3\u3130-\u318f])")


def cells(h):
    """wrap each Hangul letter of a terminal row in a two-cell box so the psql columns line up"""
    return HANGUL.sub(r'<span style="display:inline-block;width:1.2em;text-align:center">\1</span>', h)


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
        self.tws = [ttw(r[1], size) for r in self.rows]
        self.w = w or round(max(self.tws) * 1.02 + 2 * self.PX + 4 + room)
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


LC = {BL: "#6F9BF5", GR: "#5CC287", OR: "#E3A84A", RED: "#F07A72", TEAL: "#4FB8C2", GRAY: "#9AA3B5", MAG: "#E07FB0", DK: "#6F9BF5", "#1D2330": "#C9CFDA", "#7A4FC4": "#B99AF0"}


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
    if color == "#1D2330":
        color = GRAY
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
    return f'<span style="font-family:{MONO};font-weight:700;color:{color};white-space:nowrap">{e(text)}</span>'


# =====================================================================


# =====================================================================
# chapter 39: aggregate functions, GROUP BY, HAVING
# =====================================================================
EB1, EB2, EB3, EB4, EB5, EB6 = "1. 집계 함수 다섯 개", "2. COUNT 세 가지와 NULL", "3. GROUP BY로 묶기", "4. HAVING으로 묶음 고르기", "5. 앞에서 배운 것과 비교", "6. 오류와 실제 상황"
C1, C2, C3, C4, C5, C6 = BL, TEAL, VO, MAG, GR, RED
MON = {"2026-09": BL, "2026-10": TEAL, "2026-11": OR}
TINT = {BL: "#E8EFFD", TEAL: "#E1F2F3", OR: "#FBF0DF", GR: "#E4F3EA", MAG: "#F7E6EF", RED: "#F9E3E3", GRAY: "#ECEDEF"}
STC = {"완료": GR, "신청": MAG, "취소": RED}
FOLD = "#1D2330"


def grid(x, y, cols, rows, widths, gid, size=24, rh=56, tints=None, row_attrs=None, colors=None, hsize=None, hcol=GRAY, attrs="", clip=True):
    """A data table drawn as a card. Every row is one element (gid-rI) so a copy can fly from it; cells are gid-rIcJ."""
    tints = tints or {}
    row_attrs = row_attrs or {}
    colors = colors or {}
    W_ = sum(widths)
    H = rh * (len(rows) + 1)
    hs = hsize or size - 2
    o = [f'<div id="{gid}"{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{W_}px;height:{H}px;background:{CARD};border:2px solid #CFCAC0;border-radius:14px;{"overflow:hidden;" if clip else ""}box-sizing:content-box">',
         f'<div style="position:absolute;left:0;top:0;width:{W_}px;height:{rh}px;background:#EEF0F3"></div>']
    cx = 0
    for j, (c, w) in enumerate(zip(cols, widths)):
        o.append(p(f"position:absolute;left:{cx}px;top:0;width:{w}px;height:{rh}px;text-align:center;font-family:{MONO};font-size:{hs}px;font-weight:700;line-height:{rh}px;color:{hcol};white-space:nowrap", e(c)))
        cx += w
    for i, r in enumerate(rows):
        bg = tints.get(i, CARD)
        o.append(f'<div id="{gid}-r{i}"{row_attrs.get(i, "")} style="position:absolute;left:0;top:{rh * (i + 1)}px;width:{W_}px;height:{rh}px;background:{bg};border-top:2px solid #E2DED5;box-sizing:border-box">')
        cx = 0
        for j, (v, w) in enumerate(zip(r, widths)):
            col = colors.get((i, j), INK)
            if v is None:
                o.append(p(f"position:absolute;left:{cx}px;top:0;width:{w}px;height:{rh - 2}px;text-align:center;font-family:{MONO};font-size:{size - 6}px;font-style:italic;line-height:{rh - 2}px;color:#A3A9B4;white-space:nowrap", "NULL", f' id="{gid}-r{i}c{j}"'))
            else:
                ff = SANS if HANGUL.search(v) else MONO
                o.append(p(f"position:absolute;left:{cx}px;top:0;width:{w}px;height:{rh - 2}px;text-align:center;font-family:{ff};font-size:{size}px;line-height:{rh - 2}px;color:{col};white-space:nowrap", e(v), f' id="{gid}-r{i}c{j}"'))
                if tw(v, size) > w - 12:
                    WARN.append(f"{gid}: cell {i},{j} '{v}' wider than {w - 12}")
            cx += w
        o.append('</div>')
    o.append('</div>')
    g = {"x": x, "y": y, "W": W_, "rh": rh, "H": H, "widths": widths}
    g["cx"] = [x + 2 + sum(widths[:j]) for j in range(len(widths))]
    g["top"] = lambda i, g=g: g["y"] + 2 + g["rh"] * (i + 1)
    g["cy"] = lambda i, g=g: g["y"] + 2 + g["rh"] * (i + 1.5)
    return o, g


def mrow(x, y, cells_, widths, rid, color, order=None, kind="fly", src=None, h=50, size=24, bg=CARD, attrs=""):
    """a small row card (one row of a table) that can fly in from src"""
    a = (f' data-build-in="{kind} order {order}"' + (f' data-from="{src}"' if src else "")) if order else ""
    o = f'<div id="{rid}"{a}{attrs} style="position:absolute;left:{x:.0f}px;top:{y:.0f}px;width:{sum(widths)}px;height:{h}px;background:{bg};border:2px solid {color};border-radius:10px;box-shadow:0 3px 8px rgba(29,35,48,.08)">'
    cx = 0
    for v, w in zip(cells_, widths):
        o += p(f"position:absolute;left:{cx}px;top:0;width:{w}px;height:{h - 4}px;text-align:center;font-family:{MONO};font-size:{size}px;font-weight:700;line-height:{h - 4}px;color:{INK};white-space:nowrap", v)
        cx += w
    return o + '</div>'


def bucket(x, y, w, h, label, color, order=None, bid=None, size=24, kind="fade"):
    """a dashed basket with its name on a tab; the basket is an svg rect so the tab may sit on its edge"""
    i = f' id="{bid}"' if bid else ""
    off = size // 2 + 10
    return (f'<div{i}{bi(kind, order)} style="position:absolute;left:{x:.0f}px;top:{y - off:.0f}px;width:{w}px;height:{h + off}px">'
            + f'<svg width="{w}" height="{h + off}" style="position:absolute;left:0;top:0;overflow:visible"><rect x="1" y="{off + 1}" width="{w - 2}" height="{h - 2}" rx="16" fill="{TINT.get(color, "#F1F2F4")}" stroke="{color}" stroke-width="2" stroke-dasharray="7 6"/></svg>'
            + p(f"position:absolute;left:16px;top:0;height:{size + 16}px;padding:0 14px;border-radius:9px;background:{color};font-family:{MONO};font-size:{size}px;font-weight:700;line-height:{size + 16}px;color:#FFFFFF;white-space:nowrap", e(label))
            + '</div>')


def note(x, y, w, text, color=SUB, size=24, order=None, weight=400, align="left", attrs=""):
    return p(f"position:absolute;left:{x:.0f}px;top:{y:.0f}px;width:{w}px;font-size:{size}px;font-weight:{weight};line-height:1.45;color:{color};text-align:{align}", text, bi("rise", order) + attrs)


def num(x, y, text, color, size=64, order=None, attrs="", w=None, align="left", kind="pop"):
    ww = f"width:{w}px;" if w else ""
    return p(f"position:absolute;left:{x:.0f}px;top:{y:.0f}px;{ww}font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.15;color:{color};text-align:{align};white-space:nowrap", text, bi(kind, order) + attrs)


def harr(x1, x2, y, color=GRAY, order=None, width=4):
    return svg(arrow_path(f"M{x1:.0f},{y:.0f} L{x2:.0f},{y:.0f}", color, width) + head_at(x2 + 2, y, 0, color, 14), order)


def varr(x, y1, y2, color=GRAY, order=None, width=4):
    return svg(arrow_path(f"M{x:.0f},{y1:.0f} L{x:.0f},{y2:.0f}", color, width) + head_at(x, y2 + 2, 90, color, 14), order)


def code_chip(x, y, text, color, order=None, size=24, attrs="", bg=None, anim="pop"):
    return chip(x, y, text, color, bg or TINT.get(color, "#FFFFFF"), order, size=size, attrs=attrs, anim=anim)


def colspan(text, color, order=None):
    """a span for a psql line, colored on its step (pairing colors)"""
    return f'style="color:{LC.get(color, color)};font-weight:700"' + (MARK(order) if order else "")


def cell_box(g, i, j, order, color, pad=6):
    """pen box around cell (i, j) of a grid"""
    x = g["cx"][j] + pad
    return pen_box(order, round(x), round(g["top"](i) + 4), round(g["widths"][j] - 2 * pad), round(g["rh"] - 8), color, width=4)


def term_cell(t, i, sub, order, color=OR, start=None):
    """pen box around sub on terminal line i (the last match if start says so)"""
    row = t.rows[i][1]
    at = row.rindex(sub) if start == "last" else row.index(sub)
    x1 = t.tx + ttw(row[:at], t.size)
    return pen_box(order, round(x1 - 5), round(t.top(i) + 1), round(ttw(sub, t.size) + 10), round(t.lp - 2), LC.get(color, color), width=4)


def lx(t, exact, start=0):
    """index of the terminal line whose stripped text is exactly this"""
    for n in range(start, len(t.rows)):
        if t.rows[n][1].strip() == exact:
            return n
    raise KeyError(exact)


SM = P("g-small")
SMR = [[c.strip() for c in l.split("|")] for l in SM if re.match(r"^\s+\d+ \|", l)]   # id, month, status, pay

# =====================================================================
# cover
# =====================================================================
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px">',
       p("position:absolute;left:128px;top:300px;font-size:28px;font-weight:700;color:#9DC1E6", "KANT AX/AI 엔지니어 트랙 · 39"),
       f'<h1{SLAM(1)} style="position:absolute;left:128px;top:350px;padding-bottom:14px;font-size:100px;font-weight:900;line-height:1.3;color:#F6F5F1">SQL 4</h1>',
       p("position:absolute;left:128px;top:500px;font-size:52px;font-weight:700;line-height:1.3;color:#F6F5F1", "집계 함수와 GROUP BY"),
       p("position:absolute;left:128px;top:600px;width:640px;font-size:32px;line-height:1.5;color:#BFC6D4", "여러 줄을 묶고 접어서<br>개수, 합계, 평균을 구해요")]
L = P("g-month")
t = PT(L, 860, 300, size=24, w=None, tid="cov-term", lh=1.5)
cov.append(t.html())
cov.append(shine(2, "cov-term"))
W("cover", cov, "39 챕터는 SQL 4, 집계 함수와 GROUP BY예요. 36에서는 표에서 필요한 줄을 골라 봤어요. 그런데 이번 달 매출이 얼마인지, 달마다 신청이 몇 건인지는 줄을 골라 보는 것만으로는 알 수 없어요. 여러 줄을 더하고 세야 하니까요. 오늘은 여러 줄을 한 줄로 접는 집계 함수와, 같은 값끼리 묶어서 묶음마다 접는 GROUP BY를 배워요. 오른쪽 화면이 오늘 만들 결과 중 하나예요. 신청 187건을 달마다 묶어서 건수와 매출을 냈어요." + REAL, ("intro", "들어가기"))

ORDER.append("toc")   # written last, after page numbers are known

# =====================================================================
# why
# =====================================================================
o = frame("why", "들어가기", "11월 매출을 알려면 63줄을 다 더해야 해요", INK)
L = P("why")
head_, body_ = L[:4], L[4:]
rows_ = L[:4] + body_[:6] + ["\x00          ⋮   51줄 더"] + body_[-3:]
prow = psql_rows([l for l in rows_ if not l.startswith("\x00")])
prow.insert(10, ("d", rows_[10][1:]))
t = Term(prow, 96, 214, size=23, w=920, lh=1.75, tid="t-why")
o.append(t.html())
o += tag(t, len(prow) - 1, "63줄", RED, 1, gap=40)
L2 = P("why-sum")
t2 = PT(L2, 1040, 214, size=26, w=784, tid="t-sum", lh=1.45)
t2.attrs = bi("rise", 2)
o.append(t2.html())
o.append(term_cell(t2, li(t2, "4950000"), "4950000", 3, GR))
o.append(note(1040, t2.y + t2.h + 40, 784, f"{kw('SUM(pay_amount)', GR)} 하나가 63줄을 모두 더해 한 줄로 돌려줘요.", INK, 30, 3, 700))
o.append(note(1040, t2.y + t2.h + 180, 784, "이렇게 여러 줄을 값 하나로 접는 함수를 집계 함수라고 해요.", SUB, 26, 3))
W("why", o, "11월에 들어온 신청의 결제 금액을 모두 뽑아 봤어요. 36에서 배운 WHERE로 11월만 골랐더니 63줄이 나와요. 화면에는 가운데를 줄여서 실었어요. 이번 달 매출을 알려면 이 63줄을 계산기로 다 더해야 해요. 오른쪽처럼 SUM이라는 함수를 쓰면 PostgreSQL이 대신 더해서 4950000원 한 줄로 돌려줘요. 여러 줄을 값 하나로 접는 함수를 집계 함수라고 해요. 오늘은 이 집계 함수 다섯 개와, 같은 값끼리 묶어서 접는 GROUP BY를 배워요." + REAL)

# =====================================================================
# big picture
# =====================================================================
o = frame("big", "들어가기", "집계 함수는 접고, GROUP BY는 묶은 다음 접어요", INK)
gw = [250, 200, 220]
rows_ = [[r[1], r[2], r[3]] for r in SMR]
tints = {i: TINT[MON[r[1]]] for i, r in enumerate(SMR)}
gh, g = grid(96, 300, ["enroll_month", "status", "pay_amount"], rows_, gw, "bg-src", size=24, rh=60, tints=tints, hsize=20)
o += gh
o.append(note(96, 236, 700, "강좌 11번의 신청 6줄", GRAY, 24, None, 700))
# top lane: everything folds into one row
y1 = 330
o.append(harr(800, 1010, y1 + 25, GRAY, 1))
o.append(code_chip(816, y1 - 48, "COUNT(*), SUM", FOLD, 1, size=22, bg="#FFFFFF"))
o.append(mrow(1060, y1, ["6건", "440000"], [200, 260], "bg-one", FOLD, 1, "fly", "bg-src", h=56, size=26))
o.append(note(1060, y1 + 72, 700, "표 전체가 한 줄로 접혀요", FOLD, 24, 1, 700))
# bottom lane: grouped by month, each group folds
y2 = 560
o.append(harr(800, 1010, y2 + 92, GRAY, 2))
o.append(code_chip(816, y2 + 20, "GROUP BY 월", VO, 2, size=22, bg="#FFFFFF"))
for k, m in enumerate(["2026-09", "2026-10", "2026-11"]):
    src = f"bg-src-r{[r[1] for r in SMR].index(m)}"
    tot = sum(int(r[3]) for r in SMR if r[1] == m)
    cnt = sum(1 for r in SMR if r[1] == m)
    o.append(mrow(1060, y2 + k * 70, [m, f"{cnt}건", str(tot)], [200, 120, 200], f"bg-g{k}", MON[m], 2, "fly", src, h=56, size=24, bg=TINT[MON[m]]))
o.append(note(1060, y2 + 3 * 70 + 16, 700, "같은 달끼리 묶은 뒤 묶음마다 한 줄로 접혀요", VO, 24, 2, 700))
o.append(caption("결과 줄 수는 표 전체면 1줄, GROUP BY면 묶음 수만큼이에요.", 920, 3, size=28, color=SUB))
W("big", o, "오늘 배울 두 가지를 그림 한 장으로 먼저 봐요. 왼쪽은 강좌 11번의 신청 6줄이에요. 위쪽 길은 집계 함수만 쓴 경우예요. COUNT와 SUM이 6줄을 한 줄로 접어서 6건, 440000원을 돌려줘요. 아래쪽 길은 GROUP BY를 쓴 경우예요. 먼저 같은 달끼리 묶고, 묶음마다 한 줄로 접어요. 그래서 결과가 세 줄이에요. 1파트와 2파트에서 접는 법을, 3파트에서 묶는 법을, 4파트에서 묶음을 고르는 HAVING을 배워요.")

# =====================================================================
# minimal example
# =====================================================================
o = frame("min", "들어가기", "36에서 쓴 COUNT(*)가 첫 집계 함수예요", INK)
CR = [[c.strip() for c in l.split("|")] for l in P("courses") if re.match(r"^\s+\d+ \|", l)]   # id, name, fee, capacity
stack = []
for i, r in enumerate(CR):
    stack.append(f'<div style="position:absolute;left:0;top:{i * 52}px;width:420px;height:46px;background:{CARD};border:2px solid #D6D2C8;border-radius:8px">'
                 + p(f"position:absolute;left:16px;top:9px;height:24px;font-family:{MONO};font-size:20px;line-height:24px;color:{GRAY}", r[0])
                 + p(f"position:absolute;left:66px;top:9px;height:24px;font-size:20px;line-height:24px;color:{INK};white-space:nowrap", e(r[1])) + '</div>')
o.append(f'<div id="mn-stack" style="position:absolute;left:96px;top:236px;width:420px;height:{len(CR) * 52 - 6}px">' + "".join(stack) + '</div>')
o.append(harr(560, 700, 236 + 320, GRAY, 1))
o.append(f'<div id="mn-one"{bi("fly", 1)} data-from="mn-stack" style="position:absolute;left:740px;top:{236 + 320 - 70}px;width:200px;height:140px;background:{CARD};border:3px solid {FOLD};border-radius:18px;box-shadow:{SHADOW}">'
         + p(f"position:absolute;left:0;top:18px;width:200px;text-align:center;font-family:{MONO};font-size:64px;font-weight:700;line-height:1.2;color:{FOLD}", "14")
         + p(f"position:absolute;left:0;top:100px;width:200px;text-align:center;font-size:20px;color:{SUB}", "줄") + '</div>')
L = P("min")
t = PT(L, 1060, 236, size=30, w=764, tid="t-min", lh=1.5)
o.append(t.html())
o += tag(t, li(t, "14"), "14줄을 1줄로", C1, 2, gap=40)
o.append(note(1060, t.y + t.h + 50, 764, "courses 표의 강좌 14줄을 세서 숫자 하나로 돌려줘요. 줄이 몇 개든 결과는 한 줄이에요.", SUB, 26, 2))
W("min", o, "가장 짧은 예부터 봐요. 36에서 줄 수를 셀 때 COUNT 별표를 썼어요. 이게 오늘 배울 집계 함수 중 하나예요. courses 표에는 강좌가 14개 있어요. COUNT 별표가 14줄을 세서 14라는 숫자 하나로 돌려줘요. 줄이 열 개든 백 개든 결과는 한 줄이에요. 이게 집계 함수의 공통점이에요. 이번 챕터의 표는 38에서 넣은 수업 예제, 스포츠 센터 데이터베이스예요. 강좌 courses, 회원 members, 신청 enrollments 표를 써요." + REAL)

# =====================================================================
# part 1: five aggregate functions
# =====================================================================
o = frame("p-minmax", EB1, "MIN은 가장 작은 값, MAX는 가장 큰 값을 골라요", C1)
gh, g = grid(96, 204, ["course_name", "fee"], [[r[1], r[2]] for r in CR], [420, 200], "mm", size=21, rh=52, hsize=20)
o += gh
imin = [r[2] for r in CR].index("60000")
imax = [r[2] for r in CR].index("160000")
o.append(cell_box(g, imin, 1, 1, BL))
o.append(cell_box(g, imax, 1, 2, OR))
L = P("minmax")
t = PT(L, 860, 204, size=30, w=964, tid="t-mm", lh=1.5)
o.append(t.html())
vr = li(t, "60000")
o.append(term_cell(t, vr, "60000", 1, BL))
o.append(term_cell(t, vr, "160000", 2, OR))
o.append(note(860, t.y + t.h + 50, 964, f"{kw('MIN(fee)', BL)}는 fee 열을 처음부터 끝까지 보고 가장 작은 값 하나를 돌려줘요.", INK, 28, 1, 700))
o.append(note(860, t.y + t.h + 170, 964, f"{kw('MAX(fee)', OR)}는 가장 큰 값이에요. 가장 싼 강좌, 가장 비싼 강좌를 찾을 때 써요.", INK, 28, 2, 700))
o.append(note(860, 900, 964, "괄호 안에 어느 열을 볼지 적어요. 결과는 한 줄이에요.", SUB, 24, 2))
W("p-minmax", o, "1파트는 집계 함수 다섯 개예요. 왼쪽은 courses 표의 강좌 이름과 수강료예요. MIN 괄호 fee는 fee 열 14칸을 모두 보고 가장 작은 값 60000을 돌려줘요. 아쿠아로빅이에요. MAX는 가장 큰 값 160000, 필라테스 중급이에요. 괄호 안에는 어느 열을 볼지 적어요. MIN과 MAX를 한 SELECT에 같이 적으면 결과 한 줄에 두 칸으로 나와요. 가장 싼 강좌, 가장 비싼 강좌, 가장 오래된 가입일을 찾을 때 써요." + REAL, ("p1", EB1[3:]))

o = frame("p-sum", EB1, "SUM은 열의 값을 모두 더해요", C1)
gh, g = grid(96, 204, ["course_name", "capacity"], [[r[1], r[3]] for r in CR], [420, 200], "sm", size=21, rh=52, hsize=20)
o += gh
o.append(f'<div id="sm-col" style="position:absolute;left:{g["cx"][1]}px;top:{g["top"](0)}px;width:200px;height:{52 * 14}px"></div>')
o.append(harr(760, 960, 690, GRAY, 1))
o.append(f'<div id="sm-one"{bi("fly", 1)} data-from="sm-col" style="position:absolute;left:990px;top:600px;width:240px;height:180px;background:{CARD};border:3px solid {C1};border-radius:18px;box-shadow:{SHADOW}">'
         + p(f"position:absolute;left:0;top:30px;width:240px;text-align:center;font-family:{MONO};font-size:72px;font-weight:700;line-height:1.2;color:{C1}", "191")
         + p(f"position:absolute;left:0;top:124px;width:240px;text-align:center;font-size:22px;color:{SUB}", "전체 정원") + '</div>')
L = P("sum")
t = PT(L, 800, 204, size=30, w=None, tid="t-sm", lh=1.5)
t.attrs = bi("rise", 2)
o.append(t.html())
o.append(term_cell(t, lx(t, "191"), "191", 2, C1))
o.append(note(1290, 610, 534, "강좌 14개의 정원 20 + 20 + 15 + … + 8을 더한 값이에요.", INK, 28, 2, 700))
o.append(note(1290, 760, 534, "매출 합계, 판매 수량 합계처럼 숫자 열을 모두 더할 때 써요.", SUB, 26, 2))
W("p-sum", o, "SUM은 열의 값을 모두 더해요. capacity는 강좌마다 받을 수 있는 정원이에요. SUM 괄호 capacity는 14칸을 모두 더해서 191을 돌려줘요. 스포츠 센터 전체에 191자리가 있다는 뜻이에요. 매출 합계, 판매 수량 합계처럼 숫자 열을 모두 더할 때 써요. 글자 열은 더할 수 없어요. 그 오류는 6파트에서 봐요." + REAL)

o = frame("p-avg", EB1, "AVG는 합을 개수로 나눈 값이에요. 소수는 ROUND로 줄여요", C1)
L = P("avg-why")
ta = PT(L, 96, 204, size=24, w=804, tid="t-aw", lh=1.5)
o.append(ta.html())
fy = ta.y + ta.h + 50
o.append(num(96, fy, f'1370000 <span style="color:{GRAY}">÷</span> 14', C1, 46))
o.append(note(96, fy + 70, 804, "SUM(fee) ÷ COUNT(fee) = AVG(fee)", SUB, 24))
o.append(num(96, fy + 130, "= 97857.142857142857", INK, 40))
o.append(note(96, fy + 200, 804, "나누어떨어지지 않아서 소수가 길게 나와요.", SUB, 24))
L = P("avg")
t = PT(L, 950, 204, size=24, w=874, tid="t-avg", lh=1.45)
o.append(t.html())
r1 = lx(t, "97857.142857142857")
r2 = lx(t, "97857.14")
r3 = lx(t, "97857")
o.append(term_cell(t, r1, ".142857142857", 1, OR))
o += tag(t, r2, "소수 둘째 자리까지", C1, 2, gap=40)
o += tag(t, r3, "정수로", C1, 3, gap=40)
o.append(note(950, t.y + t.h + 30, 874, f"{kw('ROUND(값, 2)', C1)}은 셋째 자리에서 반올림해요. 자리 수를 안 적으면 정수로 반올림해요.", INK, 24, 3, 700))
W("p-avg", o, "AVG는 평균이에요. 왼쪽 위처럼 수강료 합계 1370000을 강좌 수 14로 나눈 값이에요. 나누어떨어지지 않아서 97857.142857142857처럼 소수가 길게 나와요. 오른쪽 첫 결과예요. 이럴 때 ROUND로 감싸요. ROUND 괄호 AVG fee 쉼표 2는 소수 둘째 자리까지 남기고 셋째 자리에서 반올림해요. 자리 수를 안 적으면 정수로 반올림해요. 수업 코드에서는 평균 수강료를 ROUND 괄호 AVG fee 쉼표 2로 적었어요." + REAL)

o = frame("p-five", EB1, "다섯 함수를 한 SELECT에 같이 적어요", C1)
L = P("five")
PAIRS = [("강좌수", "14", C1, 1), ("최저수강료", "60000", TEAL, 2), ("최고수강료", "160000", OR, 3), ("전체정원", "191", GR, 4), ("평균수강료", "97857.14", MAG, 5)]
marks = {}
for k, l in enumerate(L):
    for nm, v, c, od in PAIRS:
        if f"AS {nm}" in l:
            marks[k] = {nm: colspan(nm, c, od)}
hdr = next(k for k, l in enumerate(L) if l.strip().startswith("강좌수"))
marks[hdr] = {nm: colspan(nm, c, od) for nm, v, c, od in PAIRS}
marks[hdr + 2] = {v: colspan(v, c, od) for nm, v, c, od in PAIRS}
t = PT(L, 96, 204, size=32, w=1728, tid="t-five", lh=1.5, marks=marks)
o.append(t.html())
o.append(note(96, t.y + t.h + 40, 1728, f"{kw('AS 이름', INK)}으로 붙인 이름이 결과 열 이름이 돼요(36). 함수가 몇 개든 결과는 한 줄이에요.", SUB, 28, 5))
W("p-five", o, "수업에서 친 코드예요. 강좌 수, 최저 수강료, 최고 수강료, 전체 정원, 평균 수강료를 한 번에 구해요. 함수마다 36에서 배운 AS로 한글 이름을 붙였어요. 같은 색끼리 짝이에요. COUNT 별표는 강좌수, MIN은 최저수강료 칸이 돼요. 함수를 다섯 개 적었으니 결과는 다섯 칸이고, 줄은 여전히 한 줄이에요. 쉼표로 함수를 이어 적으면 칸이 늘어나요." + REAL)

o = frame("p-where", EB1, "WHERE로 먼저 거르고 남은 줄만 접어요", C1)
FW = [("enrollments", "187줄", 640, GRAY), ("11월만", "63줄", 420, C1), ("집계", "1줄", 200, FOLD)]
y = 236
for k, (lab, cnt, w, c) in enumerate(FW):
    o.append(f'<div{bi("rise", k)} style="position:absolute;left:{96 + (640 - w) // 2}px;top:{y}px;width:{w}px;height:120px;background:{TINT.get(c, "#EEF0F3") if c != FOLD else "#EEF0F3"};border:3px solid {c};border-radius:18px">'
             + p(f"position:absolute;left:0;top:14px;width:{w}px;text-align:center;font-size:26px;font-weight:700;color:{c}", e(lab))
             + p(f"position:absolute;left:0;top:54px;width:{w}px;text-align:center;font-family:{MONO};font-size:40px;font-weight:700;color:{INK}", cnt) + '</div>')
    if k < 2:
        o.append(varr(416, y + 128, y + 200, GRAY, k + 1))
        o.append(code_chip(440, y + 140, ["WHERE enroll_month = '2026-11'", "COUNT(*), SUM, MAX"][k], [C1, FOLD][k], k + 1, size=20, bg="#FFFFFF"))
    y += 220
L = P("nov")
t = PT(L, 920, 204, size=24, w=904, tid="t-nov", lh=1.45)
o.append(t.html())
o.append(term_cell(t, lx(t, "187"), "187", 0, GR))
o.append(lband if False else "")
o.append(term_cell(t, li(t, "WHERE enroll_month"), "WHERE enroll_month = '2026-11'", 1, C1))
o.append(term_cell(t, li(t, "4950000"), "63 | 4950000 |   160000", 2, GR))
W("p-where", o, "집계 함수는 WHERE와 같이 써요. 신청 표 enrollments에는 모두 187줄이 있어요. WHERE로 11월만 고르면 63줄이 남아요. 집계 함수는 남은 63줄만 접어요. 그래서 신청건수가 187이 아니라 63이에요. 순서는 WHERE로 거르기가 먼저, 접기가 나중이에요. 이 순서는 4파트에서 HAVING을 배울 때 다시 써요. 수업에서는 이 코드로 11월 신청 건수, 매출, 가장 큰 결제 금액을 구했어요." + REAL)

# =====================================================================
# part 2: COUNT and NULL
# =====================================================================
o = frame("q-null", EB2, "COUNT(열)은 비어 있는 칸(NULL)을 빼고 세요", C2)
NR = [[c.strip() for c in l.split("|")] for l in P("nulls") if re.match(r"^\s+\d+ \|", l)]
rows_ = [[r[0], r[2] or None, r[3] or None] for r in NR]
gh, g = grid(96, 196, ["member_id", "email", "phone"], rows_, [150, 300, 260], "nl", size=21, rh=44, hsize=20)
o += gh
LX = [(900, "COUNT(*)", None, C1), (1170, "COUNT(email)", 1, C2), (1440, "COUNT(phone)", 2, OR)]
for k, (x, lab, col, c) in enumerate(LX):
    o.append(p(f"position:absolute;left:{x}px;top:{200 + 10}px;width:240px;text-align:center;font-family:{MONO};font-size:22px;font-weight:700;color:{c};white-space:nowrap", e(lab), bi("rise", k + 1)))
    dots = []
    n = 0
    for i, r in enumerate(rows_):
        ok = col is None or r[col] is not None
        n += ok
        dots.append(f'<div style="position:absolute;left:{x + 100 - 900 + 900 - x}px;top:{g["top"](i) - 196 + 11}px;width:22px;height:22px;border-radius:11px;'
                    + (f'background:{c}' if ok else f'border:3px solid #C9CDD5;box-sizing:border-box') + '"></div>')
    o.append(f'<div{STAGGER(k + 1, 60)} style="position:absolute;left:{x + 109}px;top:196px;width:22px;height:600px">' + "".join(
        d.replace(f"left:{100}px", "left:0px") for d in dots) + '</div>')
    o.append(num(x, g["y"] + g["H"] + 16, str(n), c, 52, k + 1, "", 240, "center"))
L = P("count3-10")
t = PT(L, 96, 790, size=24, w=None, tid="t-c10", lh=1.4, bar=False, maxb=1000)
o.append(t.html())
W("q-null", o, "2파트는 COUNT의 세 가지 모양과 NULL이에요. 왼쪽은 회원 10명의 이메일과 전화번호예요. 비어 있는 칸은 NULL이에요. COUNT 별표는 줄을 세요. 칸이 비었는지 보지 않으니 10이에요. COUNT 괄호 email은 email 칸에 값이 있는 줄만 세요. 3번, 5번, 10번이 비어서 7이에요. COUNT 괄호 phone은 4번과 10번이 비어서 8이에요. 아래가 실제로 실행한 결과예요. 이메일을 남긴 회원이 몇 명인지 셀 때 COUNT 괄호 email을 써요." + REAL, ("p2", EB2[3:]))

o = frame("q-dist", EB2, "COUNT(DISTINCT 열)은 겹친 값을 한 번만 세요", C2)
RC = {"영등포구": BL, "마포구": TEAL, "강서구": OR, "구로구": MAG}
regs = []
for nm in ["영등포구"] * 12 + ["마포구"] * 11 + ["강서구"] * 10 + ["구로구"] * 7:
    regs.append(nm)
import random as _r
_r.Random(39).shuffle(regs)
dots = []
for i, nm in enumerate(regs):
    cx_, cy_ = 96 + (i % 8) * 86, 236 + (i // 8) * 86
    dots.append(f'<div id="qd-{i}" style="position:absolute;left:{cx_}px;top:{cy_}px;width:70px;height:70px;border-radius:35px;background:{TINT[RC[nm]]};border:3px solid {RC[nm]};box-sizing:border-box">'
                + p(f"position:absolute;left:0;top:0;width:64px;height:64px;text-align:center;font-size:17px;font-weight:700;line-height:64px;color:{RC[nm]};white-space:nowrap", nm[:2]) + '</div>')
o += dots
o.append(note(96, 236 + 5 * 86 + 10, 700, "회원 40명이 사는 구", GRAY, 22, None, 700))
first = {}
for i, nm in enumerate(regs):
    first.setdefault(nm, i)
for k, nm in enumerate(["강서구", "구로구", "마포구", "영등포구"]):
    o.append(f'<div id="qd-u{k}"{bi("fly", 1)} data-from="qd-{first[nm]}" style="position:absolute;left:{96 + k * 172}px;top:{236 + 6 * 86 + 30}px;width:150px;height:70px;border-radius:35px;background:{TINT[RC[nm]]};border:3px solid {RC[nm]};box-sizing:border-box">'
             + p(f"position:absolute;left:0;top:0;width:144px;height:64px;text-align:center;font-size:24px;font-weight:700;line-height:64px;color:{RC[nm]};white-space:nowrap", nm) + '</div>')
o.append(note(96, 236 + 7 * 86 + 50, 700, "겹친 값을 하나로 줄이면 4개", C2, 24, 1, 700))
L = P("distinct")
t = PT(L, 900, 204, size=26, w=924, tid="t-qd", lh=1.45)
o.append(t.html())
cl = li(t, "40 |")
o.append(term_cell(t, cl, "40", 2, GRAY))
o.append(term_cell(t, cl, "4", 2, C2, "last"))
o.append(note(900, t.y + t.h + 30, 924, f"DISTINCT는 36에서 겹친 줄을 지울 때 썼어요. {kw('COUNT(DISTINCT region)', C2)}은 지우고 남은 개수를 세요.", INK, 24, 2, 700))
W("q-dist", o, "COUNT 괄호 region은 region 칸이 빈 줄만 빼고 세니까 40이에요. 같은 구가 여러 번 나와도 다 세요. 몇 개 구에 회원이 사는지 알고 싶으면 COUNT 괄호 DISTINCT region이에요. 36에서 DISTINCT로 겹친 줄을 지웠어요. 지우고 남은 구가 4개라서 4예요. 오른쪽 위 SELECT DISTINCT 결과의 줄 수와 같아요. 수업 코드에는 COUNT 괄호 DISTINCT 괄호 region처럼 괄호가 하나 더 있었는데, 결과는 같아요." + REAL)

o = frame("q-four", EB2, "COUNT 네 가지를 한 번에 비교해요", C2)
L = P("count3")
CP = [("회원수", "40", C1, 1), ("이메일있음", "31", C2, 2), ("전화번호있음", "33", OR, 3), ("사는구", "4", MAG, 4)]
marks = {}
for k, l in enumerate(L):
    for nm, v, c, od in CP:
        if f"AS {nm}" in l:
            marks[k] = {nm: colspan(nm, c, od)}
hdr = next(k for k, l in enumerate(L) if l.strip().startswith("회원수"))
marks[hdr] = {nm: colspan(nm, c, od) for nm, v, c, od in CP}
marks[hdr + 2] = {"40": colspan("40", C1, 1), "31": colspan("31", C2, 2), "33": colspan("33", OR, 3), "…4": colspan("4", MAG, 4)}
t = PT(L, 96, 204, size=24, w=1728, tid="t-q4", lh=1.4, marks=marks)
o.append(t.html())
rows_ = [(kw("COUNT(*)", C1), "줄 수", "회원 몇 명"), (kw("COUNT(email)", C2), "email 칸이 NULL이 아닌 줄 수", "이메일을 남긴 회원"),
         (kw("COUNT(phone)", OR), "phone 칸이 NULL이 아닌 줄 수", "전화번호를 남긴 회원"), (kw("COUNT(DISTINCT region)", MAG), "겹친 값을 뺀 개수", "몇 개 구에 사는지")]
tb, y0 = table(96, t.y + t.h + 30, ["모양", "세는 것", "예"], rows_, [560, 640, 528], "q4tb", size=24, rh=52, order=5)
o += tb
W("q-four", o, "수업에서 친 코드로 네 가지를 한 번에 비교해요. 회원은 40명이에요. 이메일을 남긴 회원은 31명, 전화번호를 남긴 회원은 33명이에요. 회원이 사는 구는 4개예요. 같은 COUNT라도 괄호 안에 무엇을 적느냐에 따라 세는 것이 달라요. 별표는 줄을, 열 이름은 그 칸이 채워진 줄을, DISTINCT 열 이름은 겹치지 않는 값을 세요." + REAL)

o = frame("q-zero", EB2, "취소한 0원도 평균에 들어가요", C2)
L = P("zero")
t = PT(L, 860, 204, size=24, w=964, tid="t-qz", lh=1.45)
o.append(t.html())
a1 = li(t, "78571")
a2 = li(t, "86842")
o.append(term_cell(t, a1, "78571", 1, RED))
o.append(term_cell(t, a2, "86842", 2, GR))
o.append(p(f"position:absolute;left:96px;top:214px;width:700px;font-size:26px;font-weight:700;color:{GRAY}", "11월 결제 63건"))
bars = []
pays = [int(l.split("|")[1]) for l in P("why") if re.match(r"^\s+\d+ \|", l)]
for i, v in enumerate(pays):
    h = round(v / 160000 * 150)
    bars.append(f'<div style="position:absolute;left:{i * 11}px;top:{150 - max(h, 4)}px;width:8px;height:{max(h, 4)}px;border-radius:2px;background:{RED if v == 0 else "#AEB6C6"}"></div>')
o.append(f'<div style="position:absolute;left:96px;top:270px;width:{63 * 11}px;height:150px">' + "".join(bars) + '</div>')
o.append(note(96, 440, 700, f"빨간 막대 6개가 취소 건이에요. 금액은 0원이에요.", RED, 24, None, 700))
o.append(f'<div{bi("rise", 1)} style="position:absolute;left:96px;top:540px;width:700px;height:150px;background:{CARD};border:2px solid {LINE};border-radius:16px">'
         + p(f"position:absolute;left:28px;top:20px;font-size:24px;font-weight:700;color:{RED}", "0원까지 넣어 나누면")
         + p(f"position:absolute;left:28px;top:70px;font-family:{MONO};font-size:34px;font-weight:700;color:{INK}", "4950000 ÷ 63 = 78571") + '</div>')
o.append(f'<div{bi("rise", 2)} style="position:absolute;left:96px;top:720px;width:700px;height:150px;background:{CARD};border:2px solid {LINE};border-radius:16px">'
         + p(f"position:absolute;left:28px;top:20px;font-size:24px;font-weight:700;color:{GR}", "취소를 WHERE로 빼고 나누면")
         + p(f"position:absolute;left:28px;top:70px;font-family:{MONO};font-size:34px;font-weight:700;color:{INK}", "4950000 ÷ 57 = 86842") + '</div>')
o.append(note(96, 900, 1728, "집계 함수는 NULL만 건너뛰어요. 0은 값이라서 개수에 들어가요.", SUB, 26, 2))
W("q-zero", o, "평균에서 자주 하는 실수예요. 이 데이터는 신청을 취소하면 결제 금액을 0원으로 적어요. 11월 63건 가운데 6건이 0원이에요. AVG는 NULL만 건너뛰고, 0은 값이라서 그대로 개수에 넣어요. 그래서 합계 4950000을 63으로 나눠서 78571이 나와요. 실제로 낸 사람의 평균 결제 금액을 알고 싶으면 WHERE로 취소를 빼요. 57건으로 나눠서 86842가 나와요. 합계는 둘 다 같아요. 0을 더해도 합은 그대로니까요." + REAL)

o = frame("q-empty", EB2, "고른 줄이 없으면 COUNT는 0, SUM과 MAX는 빈칸이에요", C2)
L = P("empty")
t = PT(L, 96, 214, size=32, w=1100, tid="t-qe", lh=1.5)
o.append(t.html())
vr = li(t, "     0 |")
o += [x for x in tag(t, vr, "COUNT는 0", C2, 1, gap=60)]
o.append(f'<div style="position:absolute;left:1260px;top:214px;width:564px;height:{t.h - 4}px;background:#F1F2F4;border:3px dashed #A3A9B4;border-radius:20px">'
         + p(f"position:absolute;left:0;top:{t.h // 2 - 50}px;width:564px;text-align:center;font-size:32px;font-weight:700;color:{GRAY}", "12월 신청 0줄")
         + p(f"position:absolute;left:0;top:{t.h // 2 + 6}px;width:564px;text-align:center;font-size:24px;color:{GRAY}", "더할 값도, 비교할 값도 없어요") + '</div>')
EC = [("COUNT(*)", "0", "센 줄이 0개라서 0", C2, 1), ("SUM(pay_amount)", "NULL", "더할 값이 없어서 빈칸", OR, 2), ("MAX(pay_amount)", "NULL", "비교할 값이 없어서 빈칸", OR, 2)]
cy0 = t.y + t.h + 40
for k, (fn, v, d_, c, od) in enumerate(EC):
    x_ = 96 + k * 588
    o.append(f'<div{bi("rise", od)} style="position:absolute;left:{x_}px;top:{cy0}px;width:552px;height:190px;background:{CARD};border:3px solid {c};border-radius:18px">'
             + p(f"position:absolute;left:0;top:18px;width:552px;text-align:center;font-family:{MONO};font-size:24px;font-weight:700;color:{c}", e(fn))
             + p(f"position:absolute;left:0;top:56px;width:552px;text-align:center;font-family:{MONO};font-size:56px;font-weight:700;line-height:1.2;color:{INK if v == '0' else '#A3A9B4'};{'font-style:italic;' if v != '0' else ''}", v)
             + p(f"position:absolute;left:0;top:138px;width:552px;text-align:center;font-size:22px;color:{SUB}", e(d_)) + '</div>')
o.append(note(96, cy0 + 220, 1728, "psql은 NULL을 빈칸으로 보여 줘요. 매출이 빈칸으로 나오면 먼저 WHERE 조건을 확인해요.", SUB, 26, 3))
W("q-empty", o, "WHERE로 고른 줄이 하나도 없으면 어떻게 될까요. 12월 신청은 아직 없어요. COUNT 별표는 0을 돌려줘요. SUM과 MAX는 더하거나 비교할 값이 없어서 NULL을 돌려줘요. psql은 NULL을 빈칸으로 보여 줘요. 결과가 0줄이 아니라 빈칸이 든 한 줄이라는 점도 봐 둬요. 집계 함수는 줄이 없어도 한 줄을 돌려줘요. 매출이 빈칸으로 나오면 먼저 WHERE 조건이 맞는지 확인해요." + REAL)

# =====================================================================
# part 3: GROUP BY
# =====================================================================
o = frame("g-why", EB3, "달마다 매출을 보려면 WHERE를 바꿔 세 번 쳐야 해요", C3)
L = P("g-why")
t = PT(L, 96, 204, size=24, w=1728, tid="t-gw", lh=1.45)
o.append(t.html())
for k, m in enumerate(["2026-09", "2026-10", "2026-11"]):
    i = li(t, f"'{m}'")
    o.append(term_cell(t, i, f"'{m}'", k + 1, MON[m]))
o.append(note(96, t.y + t.h + 40, 1728, "달이 12개면 12번이에요. 같은 달끼리 묶어서 한 번에 세는 방법이 GROUP BY예요.", INK, 30, 4, 700))
W("g-why", o, "3파트는 GROUP BY예요. 9월, 10월, 11월 매출을 따로 보고 싶어요. 지금까지 배운 것으로는 WHERE의 달만 바꿔서 세 번 쳐야 해요. 결과도 세 군데에 흩어져요. 1년치를 보려면 열두 번이에요. 같은 달끼리 묶어서 묶음마다 한 번에 세는 방법이 GROUP BY예요." + REAL, ("p3", EB3[3:]))

o = frame("g-pic", EB3, "GROUP BY는 같은 값끼리 묶고, 묶음마다 한 줄로 접어요", C3)
rows_ = [[r[0], r[1], r[3]] for r in SMR]
tints = {}
gh, g = grid(96, 236, ["id", "enroll_month", "pay_amount"], rows_, [120, 250, 220], "gp", size=24, rh=52, hsize=20,
             colors={(i, 1): MON[r[1]] for i, r in enumerate(SMR)})
o += gh
o.append(note(96, 190, 600, "강좌 11번의 신청 6줄", GRAY, 22, None, 700))
BY = ["2026-09", "2026-10", "2026-11"]
for k, m in enumerate(BY):
    by_ = 220 + k * 200
    o.append(bucket(800, by_, 440, 170, m, MON[m], 1, f"gp-b{k}", 22))
    idx = [i for i, r in enumerate(SMR) if r[1] == m]
    for n, i in enumerate(idx):
        o.append(mrow(830, by_ + 30 + n * 64, [SMR[i][0], SMR[i][3]], [110, 200], f"gp-m{i}", MON[m], 1, "fly", f"gp-r{i}", h=52, size=22))
    cnt, tot = len(idx), sum(int(SMR[i][3]) for i in idx)
    o.append(harr(1256, 1390, by_ + 85, MON[m], 2))
    o.append(mrow(1420, by_ + 59, [m, str(cnt), str(tot)], [170, 70, 140], f"gp-f{k}", MON[m], 2, "pop", None, h=52, size=22, bg=TINT[MON[m]]))
o.append(p(f"position:absolute;left:1420px;top:170px;width:380px;font-size:22px;font-weight:700;color:{GRAY}", "월 | COUNT(*) | SUM", bi("rise", 2)))
L = P("g-small-by")
t = PT(L, 96, 640, size=21, w=680, tid="t-gp", lh=1.4)
t.attrs = bi("rise", 3)
o.append(t.html())
o.append(note(800, 880, 1024, "실제 결과는 2026-11이 먼저 나왔어요. 묶음의 순서는 정해져 있지 않으니 순서가 필요하면 ORDER BY를 붙여요.", INK, 24, 3, 700))
W("g-pic", o, "GROUP BY가 하는 일을 그림으로 봐요. 강좌 11번의 신청 6줄이 있어요. GROUP BY enroll_month는 enroll_month가 같은 줄끼리 한 바구니에 담아요. 9월 바구니, 10월 바구니, 11월 바구니가 생겨요. 그다음 집계 함수가 바구니마다 따로 접어요. 9월은 2건 110000원, 11월은 2건 220000원이에요. 결과는 바구니 수만큼, 세 줄이에요. 왼쪽 아래 실제 결과를 보면 11월이 먼저 나왔어요. 묶음이 나오는 순서는 정해져 있지 않아요. 순서가 필요하면 36에서 배운 ORDER BY를 붙여요." + REAL)

o = frame("g-month", EB3, "신청 187줄을 달마다 묶어 건수와 매출을 내요", C3)
L = P("g-month")
t = PT(L, 96, 204, size=28, w=1160, tid="t-gm", lh=1.5)
o.append(t.html())
GM = [[c.strip() for c in l.split("|")] for l in L if re.match(r"^ 2026-\d\d \|", l)]
tot_ = sum(int(r[1]) for r in GM)
o.append(p(f"position:absolute;left:1320px;top:214px;width:504px;text-align:center;font-size:24px;font-weight:700;color:{GRAY}", f"신청 {tot_}줄", bi("rise", 4)))
yy_ = 264
for k, r in enumerate(GM):
    hh_ = round(int(r[1]) / tot_ * 600)
    c = MON[r[0]]
    o.append(f'<div{bi("rise", 4)} style="position:absolute;left:1320px;top:{yy_}px;width:240px;height:{hh_ - 8}px;background:{TINT[c]};border:3px solid {c};border-radius:14px;box-sizing:border-box">'
             + p(f"position:absolute;left:0;top:0;width:234px;height:{hh_ - 14}px;text-align:center;font-family:{MONO};font-size:28px;font-weight:700;line-height:{hh_ - 14}px;color:{c}", f"{r[1]}줄") + '</div>')
    o.append(p(f"position:absolute;left:1590px;top:{yy_ + hh_ // 2 - 40}px;width:234px;font-family:{MONO};font-size:24px;font-weight:700;line-height:1.4;color:{c}", f"{r[0]}<br>{r[2]}", bi("rise", 4)))
    yy_ += hh_
o += tag(t, li(t, "GROUP BY"), "같은 달끼리 한 묶음", C3, 1, gap=50)
o += tag(t, li(t, "ORDER BY"), "달 순서대로", GRAY, 2, gap=50)
o.append(lspot_t(t, li(t, "2026-09"), li(t, "2026-11"), 3))
o += tag(t, li(t, "2026-10"), "묶음 3개 → 3줄", C3, 3, gap=60)
o.append(spot_off(4))
W("g-month", o, "수업에서 친 코드예요. FROM enrollments 아래에 GROUP BY enroll_month를 적었어요. 187줄이 9월, 10월, 11월 세 묶음으로 나뉘고, COUNT와 SUM이 묶음마다 따로 계산해요. 9월은 64건 5265000원이에요. 앞 장에서 WHERE를 세 번 바꿔 친 결과와 같은 숫자예요. 묶은 열 enroll_month는 SELECT에 그대로 적어서 어느 묶음의 결과인지 보여 줘요. ORDER BY enroll_month로 달 순서대로 세웠어요." + REAL)

o = frame("g-level", EB3, "강좌를 난이도별로 묶어 개수와 평균 수강료를 봐요", C3)
L = P("g-level")
t = PT(L, 96, 204, size=28, w=1728, tid="t-gl", lh=1.45)
o.append(t.html())
s1 = li(t, " 초급")
s2 = li(t, " 초급", s1 + 1)
o.append(lspot_t(t, s1, s1 + 2, 1))
o += tag(t, s1 + 1, "초급, 고급, 중급 순서로 섞여 나와요", GRAY, 1, gap=70)
o.append(spot_off(2))
o += tag(t, li(t, "ORDER BY 평균수강료"), "AS 이름으로 줄 세우기", C3, 2, gap=50)
o += tag(t, s2 + 1, "평균 수강료가 낮은 순서", C3, 2, gap=70)
W("g-level", o, "다른 표로 한 번 더 해 봐요. courses 표를 level, 곧 난이도로 묶었어요. 초급 강좌는 7개이고 평균 수강료는 89286원이에요. 첫 결과는 초급, 고급, 중급 순서로 나왔어요. 앞 장에서 말한 것처럼 묶음 순서는 정해져 있지 않아요. 두 번째처럼 ORDER BY를 붙여요. AS로 붙인 평균수강료라는 이름으로 줄을 세울 수 있어요. 평균 수강료가 낮은 순서로 초급, 중급, 고급이 됐어요." + REAL)

o = frame("g-two", EB3, "열 두 개로 묶으면 두 값이 모두 같은 줄끼리 묶여요", C3)
rows_ = [[r[1], r[2]] for r in SMR]
gh, g = grid(96, 236, ["enroll_month", "status"], rows_, [250, 160], "gt", size=24, rh=56, hsize=20,
             colors={**{(i, 0): MON[r[1]] for i, r in enumerate(SMR)}, **{(i, 1): STC[r[2]] for i, r in enumerate(SMR)}})
o += gh
o.append(note(96, 184, 600, "강좌 11번의 신청 6줄", GRAY, 22, None, 700))
L0 = P("g-two-small")
keys_ = [[c.strip() for c in l.split("|")] for l in L0 if re.match(r"^ 2026", l)]
for k, (m, s_, c_) in enumerate(keys_):
    y_ = 236 + k * 76
    src = next(i for i, r in enumerate(SMR) if r[1] == m and r[2] == s_)
    o.append(mrow(600, y_, [m, s_, f"{c_}건"], [170, 100, 90], f"gt-k{k}", STC[s_], 1, "fly", f"gt-r{src}", h=56, size=22, bg=TINT[MON[m]]))
o.append(note(600, 236 + 5 * 76 + 10, 380, "(월, 상태) 짝마다 묶음 1개", C3, 22, 1, 700))
L = P("g-two")
t = PT(L, 1010, 204, size=21, w=814, tid="t-gt", lh=1.45)
o.append(t.html())
i_a, i_b = li(t, "2026-09      | 완료"), li(t, "2026-09      | 취소")
o.append(spot(2, x=t.x + 10, y=round(t.top(i_a) - 2), w=t.w - 20, h=round((i_b - i_a + 1) * t.lp + 4), dim=0.55))
o += tag(t, li(t, "2026-09      | 완료"), "9월 안에서 다시 나뉘어요", C3, 2, gap=40)
o.append(spot_off(3))
o.append(note(96, 900, 1728, f"{kw('GROUP BY enroll_month, status', C3)}는 월이 같고 상태도 같은 줄만 한 묶음이에요. 9월 완료와 9월 취소는 다른 묶음이에요.", INK, 26, 3, 700))
W("g-two", o, "GROUP BY 뒤에 열을 두 개 적을 수 있어요. 그러면 두 값이 모두 같은 줄끼리 묶여요. 왼쪽 강좌 11번의 6줄을 월과 상태로 묶으면 다섯 묶음이에요. 9월 완료, 9월 취소, 10월 완료, 10월 취소, 11월 신청이에요. 11월 신청 2줄만 한 묶음이 됐어요. 오른쪽은 수업 코드로 신청 전체를 월과 상태로 묶은 결과예요. 9월이 완료 58건, 취소 6건으로 다시 나뉘었어요." + REAL)

o = frame("g-rule", EB3, "묶지 않은 열은 SELECT에 그냥 적을 수 없어요", C3)
L = P("g-err")
t = PT(L, 96, 204, size=26, w=1728, tid="t-ge", lh=1.45)
o.append(t.html())
ei = li(t, "ERROR")
o.append(under(t, ei, 'column "enrollments.member_id" must appear in the GROUP BY clause', 1, RED))
by_ = t.y + t.h + 70
o.append(bucket(96, by_, 380, 210, "2026-09", BL, 2, "gr-b", 22))
for n, mid in enumerate(["25", "10"]):
    o.append(mrow(126, by_ + 36 + n * 80, ["member_id " + mid], [300], f"gr-m{n}", BL, None, h=56, size=22))
o.append(note(96, by_ + 220, 400, "9월 묶음 64줄 가운데 앞의 2줄", GRAY, 20))
o.append(harr(500, 600, by_ + 105, GRAY, 2))
o.append(mrow(620, by_ + 77, ["2026-09", "<span style=\"color:#A33131\">25? 10?</span>", "64"], [180, 200, 80], "gr-res", RED, 2, "pop", None, h=56, size=24))
o.append(note(1150, by_ + 40, 674, "묶음 하나에 member_id가 여러 개라서 한 칸에 무엇을 적을지 정할 수 없어요.", INK, 26, 2, 700))
o.append(note(96, by_ + 270, 1728, f"고치는 법: 묶을 열이면 {kw('GROUP BY enroll_month, member_id', C3)}, 세고 싶으면 {kw('COUNT(DISTINCT member_id)', C3)}처럼 집계 함수로 감싸요.", INK, 26, 3, 700))
W("g-rule", o, "GROUP BY에서 가장 자주 만나는 오류예요. 달로 묶었는데 SELECT에 member_id를 같이 적었어요. 오류 메시지는 member_id가 GROUP BY에 있거나 집계 함수 안에 있어야 한다는 뜻이에요. 그림으로 보면 이유가 보여요. 9월 바구니에는 회원 25번과 10번처럼 여러 회원이 같이 들어 있어요. 결과는 바구니마다 한 줄인데, member_id 칸에 25와 10 중 무엇을 적을지 정할 수 없어요. 그래서 묶지 않은 열은 GROUP BY에 더 적거나, COUNT 같은 집계 함수로 감싸요. 다음 장에 고친 결과가 있어요." + REAL)

o = frame("g-fix", EB3, "SELECT에는 묶은 열과 집계 함수만 적어요", C3)
L = P("g-fix")
t = PT(L, 96, 204, size=28, w=1728, tid="t-gf", lh=1.45)
o.append(t.html())
o += tag(t, li(t, "COUNT(DISTINCT"), "집계 함수로 감싸기", C3, 1, gap=50)
o += tag(t, li(t, "2026-09"), "9월에 신청한 회원 34명", C3, 2, gap=60)
L2 = P("g-err2")
t2 = PT(L2, 96, t.y + t.h + 40, size=22, w=1728, tid="t-ge2", lh=1.45)
t2.attrs = bi("rise", 3)
o.append(t2.html())
o += tag(t2, li(t2, "SELECT"), "GROUP BY를 빼먹어도 같은 오류예요", RED, 3, gap=40)
W("g-fix", o, "member_id를 COUNT DISTINCT로 감쌌어요. 이제 바구니마다 한 값이 정해져요. 9월에 신청한 회원은 34명이에요. 신청 건수는 64건이었으니 한 사람이 여러 강좌를 신청했다는 뜻이에요. 규칙을 한 줄로 적으면, GROUP BY를 쓴 SELECT에는 묶은 열과 집계 함수만 적어요. 아래처럼 집계 함수 옆에 열을 적고 GROUP BY를 빼먹어도 같은 오류가 나요." + REAL)

# =====================================================================
# part 4: HAVING
# =====================================================================
o = frame("h-why", EB4, "18건 넘는 강좌만 보려고 WHERE에 COUNT를 넣으면 오류가 나요", C4)
L = P("h-course-all")
t = PT(L, 96, 204, size=19, w=780, tid="t-ha", lh=1.35)
o.append(t.html())
i2_, i5_ = li(t, "        2 |"), li(t, "        5 |")
o.append(pen_box(1, round(t.tx - 8), round(t.top(i2_)), round(t.tws[i2_] + 16), round(2 * t.lp), LC[C4], width=4))
o += tag(t, li(t, "        5 |"), "18건 이상은 2개", C4, 1, gap=40)
L2 = P("h-where")
t2 = PT(L2, 920, 204, size=22, w=904, tid="t-hw", lh=1.45)
t2.attrs = bi("rise", 2)
o.append(t2.html())
o.append(under(t2, li(t2, "ERROR"), "aggregate functions are not allowed in WHERE", 2, RED))
o.append(note(920, t2.y + t2.h + 40, 904, "WHERE는 줄을 하나씩 볼 때 실행돼요. 그때는 아직 묶음이 없어서 COUNT(*)를 셀 수 없어요.", INK, 26, 3, 700))
W("h-why", o, "4파트는 HAVING이에요. 왼쪽은 강좌별로 취소를 뺀 신청 건수예요. 이 중에서 18건 넘는 인기 강좌만 보고 싶어요. 조건이니까 WHERE에 COUNT 별표 18 이상을 적어 봤어요. 오류가 나요. 집계 함수는 WHERE에 쓸 수 없다는 뜻이에요. WHERE는 표의 줄을 하나씩 보면서 거를 때 실행돼요. 그 순간에는 아직 묶음이 없어서 강좌마다 몇 건인지 셀 수 없어요." + REAL, ("p4", EB4[3:]))

o = frame("h-bar", EB4, "HAVING은 묶어서 센 다음 결과를 걸러요", C4)
CC = [[int(c.strip()) for c in l.split("|")] for l in P("h-course-all") if re.match(r"^\s+\d+ \|\s+\d+$", l)]
bx, by0, bh, sc = 210, 214, 46, 26
for i, (cid, n) in enumerate(CC):
    keep = n >= 18
    yy = by0 + i * bh
    o.append(p(f"position:absolute;left:96px;top:{yy}px;width:90px;height:38px;text-align:right;font-family:{MONO};font-size:20px;line-height:38px;color:{GRAY}", f"{cid}번"))
    col = C4 if keep else "#C9CDD5"
    o.append(f'<div{bi("mark", 2) if not keep else ""} style="position:absolute;left:{bx}px;top:{yy + 4}px;width:{n * sc}px;height:30px;border-radius:6px;background:{C4};{"" if keep else "opacity:1"}"></div>' if keep else
             f'<div style="position:absolute;left:{bx}px;top:{yy + 4}px;width:{n * sc}px;height:30px;border-radius:6px;background:#AEB6C6"></div>')
    lx_ = bx + n * sc + 12
    if not keep and lx_ + 30 > bx + 18 * sc - 6:
        lx_ = bx + 18 * sc + 14
    o.append(p(f"position:absolute;left:{lx_}px;top:{yy}px;height:38px;font-family:{MONO};font-size:20px;font-weight:700;line-height:38px;color:{C4 if keep else GRAY}", str(n)))
tx_ = bx + 18 * sc
o.append(svg(arrow_path(f"M{tx_},{by0 - 16} L{tx_},{by0 + len(CC) * bh + 4}", C4, 3, "10 8"), 1))
o.append(chip(tx_ - 70, by0 + len(CC) * bh + 14, "18건", C4, "#FFFFFF", 1, size=22))
L = P("h-course")
t = PT(L, 1000, 204, size=24, w=824, tid="t-hc", lh=1.45)
o.append(t.html())
o.append(term_cell(t, li(t, "HAVING"), "HAVING COUNT(*) >= 18", 1, C4))
o += tag(t, li(t, "        5 |"), "2줄만 남아요", C4, 2, gap=40)
o.append(note(1000, t.y + t.h + 30, 824, "GROUP BY 뒤에 적어요. 묶음마다 센 값을 보고 조건에 맞는 묶음만 남겨요.", INK, 24, 2, 700))
W("h-bar", o, "HAVING이 답이에요. 왼쪽 막대는 강좌 14개의 신청 건수예요. HAVING COUNT 별표 18 이상은 GROUP BY로 묶고 센 다음에 실행돼요. 묶음마다 센 값을 보고 18 이상인 묶음만 남겨요. 점선 오른쪽까지 간 막대, 2번과 5번 강좌만 남아요. HAVING은 GROUP BY 바로 뒤에 적어요. WHERE와 생김새는 같지만 거르는 대상이 달라요." + REAL)

o = frame("h-region", EB4, "회원이 10명 넘게 사는 구만 골라요", C4)
RG = [(l.split("|")[0].strip(), int(l.split("|")[1])) for l in P("c-distinct", 0, "SELECT region, COUNT(*)") if re.match(r"^ \S+\s+\|\s+\d+$", l)]
RG.sort(key=lambda x: -x[1])
for i, (nm, n) in enumerate(RG):
    yy = 236 + i * 150
    keep = n >= 10
    c = RC[nm]
    o.append(p(f"position:absolute;left:96px;top:{yy}px;width:140px;height:48px;font-size:28px;font-weight:700;line-height:48px;color:{c if keep else GRAY};white-space:nowrap", nm))
    dots = "".join(f'<div style="position:absolute;left:{k * 46}px;top:0;width:36px;height:36px;border-radius:18px;background:{c if keep else "#C9CDD5"}"></div>' for k in range(n))
    o.append(f'<div style="position:absolute;left:250px;top:{yy + 6}px;width:{n * 46}px;height:36px">{dots}</div>')
    o.append(p(f"position:absolute;left:{250 + n * 46 + 10}px;top:{yy}px;height:48px;font-family:{MONO};font-size:28px;font-weight:700;line-height:48px;color:{c if keep else GRAY}", f"{n}명"))
lx = 250 + 10 * 46 - 5
o.append(svg(arrow_path(f"M{lx},216 L{lx},{236 + 4 * 150 - 60}", C4, 3, "10 8"), 1))
o.append(chip(lx - 60, 236 + 4 * 150 - 46, "10명", C4, "#FFFFFF", 1, size=22))
L = P("h-region")
t = PT(L, 1000, 204, size=24, w=824, tid="t-hr", lh=1.45)
o.append(t.html())
o.append(term_cell(t, li(t, "HAVING"), "HAVING COUNT(*) >= 10", 1, C4))
o += tag(t, li(t, "강서구"), "구로구 7명은 빠져요", C4, 2, gap=40)
o.append(note(1000, t.y + t.h + 30, 824, "구로 묶고 구마다 센 다음, 10명 이상인 묶음만 남겨요. 10 이상이라 딱 10명인 강서구도 남아요.", INK, 24, 2, 700))
W("h-region", o, "수업에서 친 두 번째 HAVING이에요. 회원을 사는 구로 묶고 구마다 몇 명인지 셌어요. 영등포구 12명, 마포구 11명, 강서구 10명, 구로구 7명이에요. HAVING COUNT 별표 10 이상이라서 구로구 묶음이 빠지고 세 줄이 남아요. 10 이상이니 딱 10명인 강서구는 남아요. 회원이 많은 동네에 홍보 문자를 보낼 때 이런 식으로 골라요." + REAL)

o = frame("h-wh", EB4, "WHERE는 묶기 전에 줄을, HAVING은 묶은 뒤에 묶음을 걸러요", C4)
rows_ = [[r[0], r[1], r[2]] for r in SMR]
gh, g = grid(96, 236, ["id", "enroll_month", "status"], rows_, [100, 230, 150], "hw", size=22, rh=52, hsize=19,
             colors={**{(i, 1): MON[r[1]] for i, r in enumerate(SMR)}, **{(i, 2): STC[r[2]] for i, r in enumerate(SMR)}})
o += gh
o.append(p(f"position:absolute;left:96px;top:186px;font-size:22px;font-weight:700;color:{GRAY}", "강좌 11번 6줄"))
for i, r in enumerate(SMR):
    if r[2] == "취소":
        y_ = g["top"](i) + 26
        o.append(svg(arrow_path(f"M110,{y_:.0f} L560,{y_:.0f}", RED, 4), 1))
o.append(code_chip(96, g["y"] + g["H"] + 24, "WHERE status <> '취소'", RED, 1, size=21, bg="#FFFFFF"))
BYK = [("2026-09", ["55"]), ("2026-10", ["115"]), ("2026-11", ["179", "180"])]
for k, (m, ids) in enumerate(BYK):
    yy = 236 + k * 128
    o.append(bucket(680, yy, 400, 104, m, MON[m], 2, f"hw-b{k}", 20))
    for n, idd in enumerate(ids):
        o.append(mrow(700 + n * 130, yy + 30, [idd], [110], f"hw-i{k}{n}", MON[m], 2, "pop", None, h=50, size=22))
    o.append(p(f"position:absolute;left:{1000}px;top:{yy + 30}px;width:70px;height:50px;font-family:{MONO};font-size:26px;font-weight:700;line-height:50px;color:{INK};text-align:right", f"{len(ids)}건", bi("pop", 2)))
o.append(code_chip(680, 236 + 3 * 128 - 4, "GROUP BY enroll_month", C3, 2, size=21, bg="#FFFFFF"))
for k in range(2):
    yy = 236 + k * 128 + 52
    o.append(svg(arrow_path(f"M690,{yy} L1070,{yy}", RED, 4), 3))
o.append(harr(1100, 1180, 236 + 2 * 128 + 55, C4, 3))
o.append(mrow(1200, 236 + 2 * 128 + 30, ["2026-11", "2"], [180, 80], "hw-res", C4, 3, "pop", None, h=52, size=24, bg=TINT[C4]))
o.append(code_chip(1200, 236 + 3 * 128 - 4, "HAVING COUNT(*) >= 2", C4, 3, size=21, bg="#FFFFFF"))
L = P("h-small")
t = PT(L, 96, 700, size=21, w=1240, tid="t-hs", lh=1.4, maxb=985)
t.attrs = bi("rise", 4)
o.append(t.html())
o.append(note(1380, 720, 444, "WHERE에 적은 조건은 표의 열을, HAVING에 적은 조건은 묶음마다 센 값을 봐요.", INK, 24, 4, 700))
W("h-wh", o, "WHERE와 HAVING을 한 문장에 같이 쓰면 차이가 잘 보여요. 강좌 11번 6줄에서 시작해요. 먼저 WHERE status 다르다 취소가 줄을 하나씩 보고 취소 2줄을 빼요. 남은 4줄을 GROUP BY가 달마다 묶어요. 9월 1건, 10월 1건, 11월 2건이에요. 마지막으로 HAVING COUNT 별표 2 이상이 묶음을 보고 9월과 10월 묶음을 빼요. 11월만 남아요. WHERE는 묶기 전에 줄을, HAVING은 묶은 뒤에 묶음을 걸러요." + REAL)

o = frame("h-cmp", EB4, "WHERE를 빼면 취소까지 세서 결과가 달라져요", C4)
L1 = P("h-course")
L2 = P("h-nowhere")
t1 = PT(L1, 96, 204, size=24, w=840, tid="t-c1", lh=1.45)
t2 = PT(L2, 984, 204, size=24, w=840, tid="t-c2", lh=1.45)
o += [t1.html(), t2.html()]
o.append(term_cell(t1, li(t1, "WHERE"), "WHERE status <> '취소'", 1, RED))
o.append(lspot_t(t2, li(t2, "        2 |"), li(t2, "        8 |"), 2))
o.append(spot_off(3))
o += tag(t1, li(t1, "        5 |"), "2개", C4, 3, gap=40)
o += tag(t2, li(t2, "        8 |"), "4개", C4, 3, gap=40)
o.append(note(96, max(t1.y + t1.h, t2.y + t2.h) + 40, 1728, "취소한 신청까지 세면 1번과 8번 강좌도 18건을 넘어요. 무엇을 셀지는 WHERE로, 몇 건 이상인지는 HAVING으로 정해요.", INK, 26, 3, 700))
W("h-cmp", o, "WHERE를 빼면 어떻게 될까요. 왼쪽은 수업 코드, 오른쪽은 WHERE 줄만 지운 거예요. 오른쪽은 취소한 신청까지 세서 2번 강좌가 25건이 아니라 26건이에요. 1번과 8번 강좌도 18건을 넘어서 네 줄이 나와요. 인기 강좌를 고르는데 취소한 신청까지 세면 안 되겠죠. 무엇을 셀지는 WHERE로, 몇 건 이상인 묶음을 남길지는 HAVING으로 정해요." + REAL)

o = frame("h-order", EB4, "SQL은 적은 순서와 다른 순서로 실행돼요", C4)
WR = ["SELECT", "FROM", "WHERE", "GROUP BY", "HAVING", "ORDER BY", "LIMIT"]
EX = [("FROM", "표 고르기", GRAY), ("WHERE", "줄 거르기", RED), ("GROUP BY", "묶기", C3), ("HAVING", "묶음 거르기", C4), ("SELECT", "칸 고르기, AS 이름이 생겨요", C1), ("ORDER BY", "줄 세우기", GRAY), ("LIMIT", "자르기", GRAY)]
o.append(p(f"position:absolute;left:96px;top:206px;font-size:26px;font-weight:700;color:{GRAY}", "적는 순서"))
o.append(p(f"position:absolute;left:700px;top:206px;font-size:26px;font-weight:700;color:{C4}", "실행 순서", bi("rise", 1)))
for k, w_ in enumerate(WR):
    o.append(chip(96, 260 + k * 98, w_, INK, "#FFFFFF", None, size=28, attrs=f' id="ho-w{k}"'))
for k, (w_, d_, c) in enumerate(EX):
    o.append(p(f"position:absolute;left:640px;top:{260 + k * 98}px;width:44px;height:50px;text-align:right;font-family:{MONO};font-size:26px;font-weight:700;line-height:50px;color:{GRAY}", str(k + 1), bi("rise", 1)))
    o.append(chip(700, 260 + k * 98, w_, c, TINT.get(c, "#FFFFFF"), 1, size=28, attrs=f' data-from="ho-w{WR.index(w_)}"', anim="fly"))
    o.append(p(f"position:absolute;left:{700 + chip_w(w_, 28) + 24:.0f}px;top:{260 + k * 98}px;height:50px;font-size:26px;line-height:50px;color:{SUB};white-space:nowrap", e(d_), bi("rise", 1) + DELAY(200)))
o.append(f'<div{bi("rise", 2)} style="position:absolute;left:1340px;top:260px;width:484px;height:640px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:30px 32px;box-sizing:border-box">'
         + p(f"font-size:26px;font-weight:700;line-height:1.5;color:{INK}", "그래서")
         + p(f"margin-top:20px;font-size:24px;line-height:1.6;color:{SUB}", f"{kw('WHERE', RED)}에는 집계 함수를 못 써요. 아직 안 묶었어요.")
         + p(f"margin-top:20px;font-size:24px;line-height:1.6;color:{SUB}", f"{kw('HAVING', C4)}에는 AS 이름을 못 써요. 이름은 그다음 SELECT에서 생겨요.")
         + p(f"margin-top:20px;font-size:24px;line-height:1.6;color:{SUB}", f"{kw('ORDER BY', INK)}에는 AS 이름을 써도 돼요. SELECT 다음이에요.") + '</div>')
W("h-order", o, "지금까지 나온 절을 모아서 순서를 봐요. 왼쪽은 우리가 적는 순서예요. SELECT가 맨 앞이에요. 그런데 PostgreSQL은 오른쪽 순서로 실행해요. 먼저 FROM으로 표를 고르고, WHERE로 줄을 거르고, GROUP BY로 묶고, HAVING으로 묶음을 거른 다음에야 SELECT로 칸을 골라요. 마지막이 ORDER BY와 LIMIT이에요. 이 순서를 알면 오류 두 가지가 풀려요. WHERE는 묶기 전이라 집계 함수를 못 써요. AS로 붙인 이름은 SELECT에서 생기니까 그 앞의 HAVING에서는 못 쓰고, 뒤의 ORDER BY에서는 써요.")

o = frame("h-alias", EB4, "HAVING에 AS 이름을 적으면 없는 열이라고 나와요", C4)
L = P("h-alias")
t = PT(L, 96, 204, size=30, w=1728, tid="t-hal", lh=1.5)
o.append(t.html())
o.append(under(t, li(t, "ERROR"), 'column "누적신청" does not exist', 1, RED))
o.append(term_cell(t, li(t, "HAVING"), "누적신청", 1, RED, "last"))
L2 = P("h-course")
L2 = [l for l in L2 if "HAVING" in l or "ORDER BY" in l]
t2 = PT(L2, 96, t.y + t.h + 70, size=30, w=1728, tid="t-hal2", lh=1.5)
t2.attrs = bi("rise", 2)
o.append(t2.html())
o.append(p(f"position:absolute;left:96px;top:{t.y + t.h + 20}px;font-size:24px;font-weight:700;color:{GR}", "고친 줄 (수업 코드)", bi("rise", 2)))
o += tag(t2, 0, "HAVING에는 함수를 다시 적어요", C4, 2, gap=50)
o += tag(t2, 1, "ORDER BY는 이름으로 돼요", GR, 3, gap=50)
W("h-alias", o, "앞 장의 순서를 실제 오류로 확인해요. HAVING에 AS로 붙인 이름 누적신청을 적었더니 그런 열이 없다고 나와요. HAVING이 실행될 때는 아직 SELECT가 실행되지 않아서 이름이 없어요. HAVING에는 COUNT 별표를 다시 적어요. 수업 코드도 HAVING COUNT 별표 18 이상, ORDER BY 누적신청 DESC로 적었어요. ORDER BY는 SELECT 다음에 실행돼서 이름을 쓸 수 있어요." + REAL)

# =====================================================================
# part 5: compare with what we know
# =====================================================================
o = frame("c-dist", EB5, "DISTINCT와 GROUP BY는 같은 목록을 내요. 개수는 GROUP BY로 세요", C5)
L = P("c-distinct")
i2 = next(k for k, l in enumerate(L) if "SELECT region FROM" in l)
i3 = next(k for k, l in enumerate(L) if "SELECT region, COUNT" in l)
t2 = PT(L[i2:i3], 972, 250, size=22, w=852, tid="t-cd2", lh=1.4)
t1 = PT(L[:i2], 96, 250, size=t2.size, w=852, tid="t-cd1", lh=1.4)
t3 = PT(L[i3:], 96, max(t1.y + t1.h, t2.y + t2.h) + 40, size=22, w=1728, tid="t-cd3", lh=1.4)
t3.attrs = bi("rise", 2)
o += [t1.html(), t2.html(), t3.html()]
o.append(p(f"position:absolute;left:96px;top:204px;font-size:24px;font-weight:700;color:{GRAY}", "36에서 배운 DISTINCT"))
o.append(p(f"position:absolute;left:972px;top:204px;font-size:24px;font-weight:700;color:{C3}", "GROUP BY로 같은 목록"))
o += tag(t3, li(t3, "COUNT(*)"), "GROUP BY만 묶음마다 셀 수 있어요", C5, 2, gap=40)
W("c-dist", o, "5파트는 앞에서 배운 것과 비교예요. 36에서 DISTINCT로 겹치지 않는 구 목록을 뽑았어요. GROUP BY region만 적어도 같은 목록이 나와요. 둘 다 같은 값끼리 하나로 모으니까요. 차이는 그다음이에요. GROUP BY는 묶음을 기억해서 COUNT 별표로 구마다 몇 명인지 셀 수 있어요. 목록만 필요하면 DISTINCT, 개수나 합계까지 필요하면 GROUP BY를 써요." + REAL, ("p5", EB5[3:]))

o = frame("c-py", EB5, "15에서 딕셔너리로 세던 일을 GROUP BY가 한 줄로 해요", C5)
PYL = ['regions = ["마포구", "강서구", "마포구", "구로구", "마포구", "강서구"]', "counts = {}", "for r in regions:", "    counts[r] = counts.get(r, 0) + 1", "print(counts)"]
ed, eg = editor("py-ed", "count.py", PYL, 96, 214, 1040, fs=22, color=BL)
o.append(ed)
pt = Term([("$", "~/count", "uv run count.py"), ("o", "{'마포구': 3, '강서구': 2, '구로구': 1}")], 96, 214 + eg["h"] + 30, size=22, w=1040, tid="t-py")
o.append(pt.html())
o.append(lband(1, eg, 2, 2, BL))
L = P("c-py-sql")
t = PT(L, 1180, 214, size=24, w=644, tid="t-cpy", lh=1.45)
t.attrs = bi("rise", 2)
o.append(t.html())
o.append(note(96, pt.y + pt.h + 40, 1040, "for와 get으로 키마다 1씩 더하던 일을 GROUP BY와 COUNT(*)가 해요.", INK, 24, 2, 700))
W("c-py", o, "15에서 딕셔너리로 개수를 세는 법을 배웠어요. 왼쪽 코드는 for로 구를 하나씩 꺼내서, counts 딕셔너리에 그 구의 값을 1씩 늘려요. 마포구 3, 강서구 2, 구로구 1이 나와요. 오른쪽 SQL은 같은 일을 GROUP BY region과 COUNT 별표로 해요. 딕셔너리의 키가 묶음이고, 1씩 더한 값이 COUNT 별표예요. 데이터가 데이터베이스에 있으면 파이썬으로 다 가져와서 세지 않고 SQL로 세는 게 빨라요. 파이썬 출력은 uv run으로 실제로 실행한 결과예요." + REAL)

# =====================================================================
# part 6: errors and real situations
# =====================================================================
o = frame("x-err", EB6, "집계와 GROUP BY에서 나는 오류 네 가지", C6)
rows_ = [(f'<span style="font-family:{MONO};font-size:21px">must appear in the GROUP BY clause<br>or be used in an aggregate function</span>', "묶지 않은 열을 SELECT에 적었어요", "GROUP BY에 더하거나 집계 함수로 감싸요"),
         (f'<span style="font-family:{MONO};font-size:21px">aggregate functions are not<br>allowed in WHERE</span>', "WHERE에 COUNT, SUM을 적었어요", "그 조건은 HAVING으로 옮겨요"),
         (f'<span style="font-family:{MONO};font-size:21px">column "누적신청" does not exist</span>', "HAVING에 AS 이름을 적었어요", "HAVING에는 함수를 다시 적어요"),
         (f'<span style="font-family:{MONO};font-size:21px">function sum(character varying)<br>does not exist</span>', "글자 열을 SUM, AVG에 넣었어요", "숫자 열인지 확인해요. 글자는 COUNT, MIN, MAX만"),]
y = 214
o.append(p(f"position:absolute;left:96px;top:{y}px;font-size:22px;font-weight:700;color:{GRAY}", "ERROR 뒤에 나오는 말"))
o.append(p(f"position:absolute;left:700px;top:{y}px;font-size:22px;font-weight:700;color:{GRAY}", "왜"))
o.append(p(f"position:absolute;left:1250px;top:{y}px;font-size:22px;font-weight:700;color:{GRAY}", "고치는 법"))
for k, (a_, b_, c_) in enumerate(rows_):
    yy = 270 + k * 170
    o.append(f'<div style="position:absolute;left:96px;top:{yy}px;width:1728px;height:2px;background:{LINE}"></div>')
    o.append(p(f"position:absolute;left:96px;top:{yy + 30}px;width:580px;line-height:1.5;color:{RED};font-weight:700", a_, bi("rise", k + 1)))
    o.append(p(f"position:absolute;left:700px;top:{yy + 30}px;width:520px;font-size:24px;line-height:1.5;color:{INK}", e(b_), bi("rise", k + 1)))
    o.append(p(f"position:absolute;left:1250px;top:{yy + 30}px;width:574px;font-size:24px;font-weight:700;line-height:1.5;color:{GR}", e(c_), bi("rise", k + 1)))
o.append(f'<div style="position:absolute;left:96px;top:{270 + 4 * 170}px;width:1728px;height:2px;background:{LINE}"></div>')
W("x-err", o, "6파트는 오류와 실제 상황 예제예요. 오늘 나온 오류 네 가지를 모았어요. 첫째, 묶지 않은 열을 SELECT에 적으면 GROUP BY에 있거나 집계 함수 안에 있어야 한다고 나와요. 둘째, WHERE에 집계 함수를 적으면 WHERE에서는 못 쓴다고 나와요. HAVING으로 옮겨요. 셋째, HAVING에 AS 이름을 적으면 그런 열이 없다고 나와요. 넷째, 글자 열을 SUM이나 AVG에 넣으면 그런 함수가 없다고 나와요. 다음 장에서 넷째 오류를 직접 봐요.", ("p6", EB6[3:]))

o = frame("x-text", EB6, "글자 열은 COUNT, MIN, MAX만 돼요. SUM과 AVG는 숫자 열만", C6)
L = P("x-sum-text")
t = PT(L, 96, 204, size=28, w=1728, tid="t-xt", lh=1.5)
o.append(t.html())
o += tag(t, li(t, "강시우"), "글자 순서로 가장 앞, 가장 뒤", C6 if False else GR, 1, gap=50)
o.append(under(t, li(t, "ERROR"), "function sum(character varying) does not exist", 2, RED))
o.append(note(96, t.y + t.h + 40, 1728, "character varying은 VARCHAR예요(36). 이름을 더하는 함수는 없다는 뜻이에요. HINT는 타입을 바꾸라고 하지만, 이름은 더할 값이 아니니 열을 다시 골라요.", INK, 26, 3, 700))
W("x-text", o, "글자 열에도 집계 함수를 쓸 수 있을까요. COUNT 괄호 name은 이름이 있는 회원 수라서 40이에요. MIN과 MAX는 글자 순서로 비교해서 가장 앞인 강시우, 가장 뒤인 황민서를 돌려줘요. SUM 괄호 name은 오류가 나요. character varying은 36에서 배운 VARCHAR예요. VARCHAR를 더하는 SUM 함수는 없다는 뜻이에요. HINT는 타입을 바꿔 보라고 하지만, 이름은 더할 값이 아니에요. 열을 잘못 골랐는지 확인해요." + REAL)

o = frame("e-report", EB6, "실제 상황 1: 취소를 뺀 월별 매출 보고서를 만들어요", C6)
L = P("ex-report")
t = PT(L, 96, 204, size=26, w=1180, tid="t-er", lh=1.45)
o.append(t.html())
ER = [[c.strip() for c in l.split("|")] for l in L if re.match(r"^ 2026-\d\d \|", l)]
o.append(p(f"position:absolute;left:1330px;top:214px;width:494px;text-align:center;font-size:24px;font-weight:700;color:{GRAY}", "달마다 매출", bi("rise", 4)))
base_ = 880
for k, r in enumerate(ER):
    hh_ = round(int(r[2]) / 5265000 * 480)
    c = MON[r[0]]
    x_ = 1350 + k * 160
    o.append(f'<div{bi("rise", 4)} style="position:absolute;left:{x_}px;top:{base_ - hh_}px;width:120px;height:{hh_}px;background:{c};border-radius:10px 10px 0 0"></div>')
    o.append(p(f"position:absolute;left:{x_ - 20}px;top:{base_ - hh_ - 40}px;width:160px;text-align:center;font-family:{MONO};font-size:22px;font-weight:700;color:{c}", r[2], bi("rise", 4)))
    o.append(p(f"position:absolute;left:{x_ - 20}px;top:{base_ + 12}px;width:160px;text-align:center;font-family:{MONO};font-size:22px;font-weight:700;color:{SUB}", r[0], bi("rise", 4)))
o.append(f'<div style="position:absolute;left:1330px;top:{base_}px;width:494px;height:2px;background:{LINE}"></div>')
o += tag(t, li(t, "WHERE"), "취소는 빼고", RED, 1, gap=50)
o += tag(t, li(t, "GROUP BY"), "달마다", C3, 2, gap=50)
o += tag(t, li(t, "ROUND(AVG"), "평균 결제는 정수로", C1, 3, gap=50)
W("e-report", o, "여기부터는 실제 상황 예제예요. 센터장이 월별 매출 보고서를 달라고 했어요. 취소한 신청은 빼야 해요. WHERE로 취소를 빼고, GROUP BY로 달마다 묶고, 건수, 매출, 평균 결제를 냈어요. 평균은 ROUND로 정수로 줄였어요. 9월은 58건, 매출 5265000원이에요. 앞에서 본 9월 64건 가운데 취소 6건이 빠졌어요. 매출은 그대로예요. 취소는 0원이었으니까요." + REAL)

o = frame("e-top", EB6, "실제 상황 2: 신청이 가장 많은 강좌 세 개를 찾아요", C6)
L = P("ex-top")
k2 = next(k for k, l in enumerate(L) if "SELECT course_id, course_name" in l)
t = PT(L[:k2], 96, 204, size=26, w=900, tid="t-et", lh=1.45)
o.append(t.html())
o += tag(t, li(t, "ORDER BY"), "많은 순서로", C3, 1, gap=50)
o += tag(t, li(t, "LIMIT"), "세 줄만(36)", GRAY, 1, gap=50)
t2 = PT(L[k2:], 1030, 204, size=22, w=794, tid="t-et2", lh=1.45)
t2.attrs = bi("rise", 2)
o.append(t2.html())
o.append(term_cell(t2, li(t2, "IN (2, 5, 8)"), "IN (2, 5, 8)", 2, C5))
o.append(note(1030, t2.y + t2.h + 30, 794, "결과에는 번호만 있어서, courses 표에서 IN으로 강좌 이름을 찾았어요.", INK, 24, 2, 700))
W("e-top", o, "두 번째 예제예요. 인기 강좌 세 개를 홈페이지에 올리려고 해요. 강좌별로 묶어서 세고, ORDER BY로 많은 순서로 세운 다음, 36에서 배운 LIMIT 3으로 세 줄만 남겼어요. 2번, 5번, 8번 강좌예요. 결과에는 번호만 있어서, 강좌 이름은 courses 표에서 IN으로 다시 찾았어요. 두 표를 한 번에 이어서 읽는 방법은 다음 챕터의 JOIN에서 배워요." + REAL)

o = frame("e-vip", EB6, "실제 상황 3: 60만 원 넘게 결제한 단골 회원을 골라요", C6)
L = P("ex-vip")
t = PT(L, 96, 204, size=24, w=1150, tid="t-ev", lh=1.4)
o.append(t.html())
EV = [[c.strip() for c in l.split("|")] for l in L if re.match(r"^\s+\d+ \|\s+\d+ \|\s+\d+$", l)]
o.append(p(f"position:absolute;left:1300px;top:214px;width:524px;font-size:24px;font-weight:700;color:{GRAY}", "회원별 누적 결제", bi("rise", 4)))
for k, r in enumerate(EV):
    yy_ = 280 + k * 84
    ww_ = round(int(r[2]) / 745000 * 360)
    o.append(p(f"position:absolute;left:1300px;top:{yy_}px;width:70px;height:44px;text-align:right;font-family:{MONO};font-size:22px;line-height:44px;color:{GRAY}", f"{r[0]}번", bi("rise", 4)))
    o.append(f'<div{bi("rise", 4)} style="position:absolute;left:1390px;top:{yy_ + 6}px;width:{ww_}px;height:32px;border-radius:6px;background:{C4}"></div>')
    o.append(p(f"position:absolute;left:{1390 + ww_ + 10}px;top:{yy_}px;height:44px;font-family:{MONO};font-size:20px;font-weight:700;line-height:44px;color:{C4}", r[2], bi("rise", 4)))
lx6 = 1390 + round(600000 / 745000 * 360)
o.append(svg(arrow_path(f"M{lx6},266 L{lx6},{280 + len(EV) * 84}", INK, 3, "8 8"), 4))
o.append(chip(lx6 - 60, 290 + len(EV) * 84, "60만 원", INK, "#FFFFFF", 4, size=20))
o += tag(t, li(t, "GROUP BY member_id"), "회원마다", C3, 1, gap=50)
o += tag(t, li(t, "HAVING SUM"), "누적 결제 60만 원 이상인 회원만", C4, 2, gap=50)
o += tag(t, li(t, "ORDER BY"), "같은 금액이면 번호 순서", GRAY, 3, gap=50)
W("e-vip", o, "세 번째 예제예요. 단골 회원에게 할인 쿠폰을 주려고 해요. 기준은 취소를 뺀 누적 결제 60만 원 이상이에요. 회원마다 묶고, HAVING에 SUM 괄호 pay_amount 60만 이상을 적었어요. HAVING에는 COUNT뿐 아니라 SUM, AVG 같은 다른 집계 함수도 적을 수 있어요. 16번 회원이 8건, 745000원으로 가장 많이 냈어요. ORDER BY에 기준을 두 개 적어서 금액이 같으면 회원 번호 순서로 세웠어요." + REAL)

o = frame("e-sport", EB6, "실제 상황 4: 종목마다 강좌 수, 수강료 범위, 정원을 한눈에 봐요", C6)
L = P("ex-sport")
k2 = next(k for k, l in enumerate(L) if "SELECT * FROM sports" in l)
t = PT(L[:k2], 96, 204, size=27, w=1100, tid="t-es", lh=1.4)
o.append(t.html())
o += tag(t, li(t, "GROUP BY sport_id"), "종목마다", C3, 1, gap=40)
t2 = PT(L[k2:], 1240, 204, size=26, w=584, tid="t-es2", lh=1.4)
t2.attrs = bi("rise", 2)
o.append(t2.html())
o.append(note(1240, t2.y + t2.h + 30, 584, "sport_id 1은 수영이에요. 수영 강좌가 5개, 정원이 92명으로 가장 커요.", INK, 24, 2, 700))
W("e-sport", o, "마지막 예제예요. 종목마다 강좌가 몇 개인지, 수강료가 얼마부터 얼마까지인지, 정원이 몇 명인지 한 표로 봐요. courses를 sport_id로 묶고 COUNT, MIN, MAX, SUM을 같이 적었어요. 종목 이름은 sports 표에 있어서 오른쪽처럼 따로 봤어요. 1번 수영은 강좌 5개, 수강료 60000원부터 90000원, 정원 92명이에요. 5번 필라테스는 강좌 2개인데 수강료가 가장 비싸요." + REAL)

# =====================================================================
# summary
# =====================================================================
o = frame("sum", "정리", "언제 무엇을 쓰는지 정리해요", INK)
rows_ = [(kw("COUNT(*)", C1), "줄 수", "회원 수, 신청 건수"),
         (kw("COUNT(열)", C2), "NULL이 아닌 칸 수", "이메일을 남긴 회원 수"),
         (kw("COUNT(DISTINCT 열)", C2), "겹치지 않는 값 수", "회원이 사는 구 수"),
         (kw("SUM  AVG", C1), "합계, 평균 (숫자 열)", "매출, 평균 결제, ROUND(AVG(fee), 2)"),
         (kw("MIN  MAX", C1), "가장 작은 값, 가장 큰 값", "가장 싼 강좌, 최고 결제"),
         (kw("GROUP BY 열", C3), "같은 값끼리 묶어 묶음마다 한 줄", "달마다, 강좌마다, 구마다"),
         (kw("HAVING 조건", C4), "묶음 거르기 (집계 함수로)", "18건 이상 강좌, 10명 이상 구"),
         (kw("WHERE 조건", RED), "묶기 전에 줄 거르기", "취소 빼기, 11월만")]
tb, y0 = table(96, 206, ["쓸 것", "하는 일", "예"], rows_, [520, 600, 608], "sum", size=26, rh=70, order=None)
o += tb
o.append(f'<div style="position:absolute;left:96px;top:{y0 + 8 * 70 + 30:.0f}px;width:1728px;height:96px;background:{CARD};border:2px solid {LINE};border-radius:16px;padding:0 30px;display:flex;align-items:center;gap:24px">'
         + p(f"font-size:26px;font-weight:700;color:{INK};white-space:nowrap", "다음에 배울 것")
         + p(f"font-size:24px;color:{SUB};white-space:nowrap", f"강좌 번호 옆에 강좌 이름을 붙이는 {kw('JOIN', BL)}, 결과 두 개를 이어 붙이는 {kw('UNION', BL)} (40)") + '</div>')
W("sum", o, "오늘 배운 것을 한 장에 모았어요. 개수는 COUNT, 합계와 평균은 SUM과 AVG, 가장 작은 값과 큰 값은 MIN과 MAX예요. COUNT는 괄호 안에 별표, 열 이름, DISTINCT 열 이름 중 무엇을 적느냐에 따라 세는 것이 달라요. 같은 값끼리 묶어서 묶음마다 보고 싶으면 GROUP BY, 묶음을 거르려면 HAVING, 묶기 전에 줄을 거르려면 WHERE예요. 오늘 결과에는 강좌 번호만 나와서 이름을 따로 찾았어요. 다음 챕터에서 JOIN으로 두 표를 이어 읽어요.", ("end", "정리"))

o = frame("cheat", "치트시트", "집계 SELECT 한 장", INK)
CL0 = [("SELECT", ""), ("    course_id,", "묶은 열"), ("    COUNT(*)        AS 신청수,", "집계 함수"), ("    SUM(pay_amount) AS 매출", ""),
       ("FROM enrollments", ""), ("WHERE status <> '취소'", "줄 거르기"), ("GROUP BY course_id", "묶기"), ("HAVING COUNT(*) >= 18", "묶음 거르기"),
       ("ORDER BY 신청수 DESC", "줄 세우기"), ("LIMIT 3;", "")]
CL = []
for c_, m_ in CL0:
    cols_ = round(ttw(c_, 1) / 0.6)
    line_ = cells(e(c_))
    if m_:
        line_ += " " * (34 - cols_) + f'<span style="color:{GRAY}">-- {cells(e(m_))}</span>'
    CL.append(line_ if "<span" in line_ else f'<span>{line_}</span>')
ed, g = editor("ch-sql", "report.sql", CL, 96, 200, 1130, fs=28, nums=False, color=PG)
o.append(ed)
AL = [("COUNT(*)  COUNT(열)\nCOUNT(DISTINCT 열)", "줄 수, NULL 아닌 칸 수, 겹치지 않는 값 수"),
      ("SUM(열)  AVG(열)", "합계, 평균. 숫자 열만"),
      ("MIN(열)  MAX(열)", "가장 작은 값, 가장 큰 값"),
      ("ROUND(값, 2)  ROUND(값)", "소수 둘째 자리까지, 정수로"),
      ("GROUP BY a, b", "a와 b가 모두 같은 줄끼리 묶기")]
y = 206
for k_, d_ in AL:
    nl = k_.count("\n") + 1
    o.append(p(f"position:absolute;left:1270px;top:{y}px;width:554px;font-family:{MONO};font-size:22px;font-weight:700;line-height:1.4;color:{INK};white-space:pre", e(k_)))
    o.append(p(f"position:absolute;left:1270px;top:{y + nl * 22 * 1.4 + 4:.0f}px;width:554px;font-size:21px;line-height:1.35;color:{SUB}", e(d_)))
    y += nl * 22 * 1.4 + 4 + 21 * 1.35 + 34
o.append(caption("SELECT에는 묶은 열과 집계 함수만 적어요. 집계 함수 조건은 HAVING, 줄 조건은 WHERE예요.", 200 + g["h"] + 30, None, size=24, color=SUB))
W("cheat", o, "실습할 때 옆에 열어 둘 한 장이에요. 왼쪽은 오늘 배운 절을 다 넣은 SELECT예요. 주석은 절마다 하는 일이에요. WHERE로 줄을 거르고, GROUP BY로 묶고, HAVING으로 묶음을 거르고, ORDER BY로 줄을 세워요. 오른쪽은 집계 함수와 ROUND, 열 두 개로 묶기예요. SELECT에는 묶은 열과 집계 함수만 적는다는 규칙을 기억해요.")

# =====================================================================
# toc
# =====================================================================
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
PL = [(C1, EB1[3:], "COUNT, MIN, MAX, SUM, AVG, ROUND, WHERE와 같이 쓰기", "p-minmax", "p-where"),
      (C2, EB2[3:], "COUNT(*), COUNT(열), COUNT(DISTINCT 열), 0과 NULL, 빈 결과", "q-null", "q-empty"),
      (C3, EB3[3:], "GROUP BY 열 하나와 둘, 묶음 순서와 ORDER BY, 묶지 않은 열 오류", "g-why", "g-fix"),
      (C4, EB4[3:], "HAVING, WHERE와 HAVING 비교, 실행 순서, AS 이름", "h-why", "h-alias"),
      (C5, EB5[3:], "DISTINCT와 GROUP BY, 15의 딕셔너리로 세기", "c-dist", "c-py"),
      (C6, EB6[3:], "오류 네 가지, 월별 매출, 인기 강좌, 단골 회원, 종목별 현황", "x-err", "e-sport")]
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
    f.write("\n".join(o) + f"\n<aside>{e('여섯 파트로 나눴어요. 1파트는 여러 줄을 한 값으로 접는 집계 함수 다섯 개예요. 2파트에서 COUNT의 세 가지 모양과 NULL, 0을 구별해요. 3파트는 같은 값끼리 묶는 GROUP BY, 4파트는 묶음을 고르는 HAVING이에요. 5파트에서 36의 DISTINCT, 15의 딕셔너리와 비교하고, 6파트에서 오류를 모아 본 다음 실제 상황 예제 네 개를 풀어요.')}</aside>\n</section>\n")

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-18T00:00:00Z"}, "lists": "css", "title": "SQL 4 (집계 함수와 GROUP BY)", "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
for w_ in WARN:
    print("WARN", w_)
print(len(ORDER), "slides")
