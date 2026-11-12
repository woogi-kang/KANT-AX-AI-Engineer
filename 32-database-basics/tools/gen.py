"""Generates every slide of the database basics deck (32) and slides/deck.json.

Story: lists and dicts vanish when the program ends, so data goes to a database server (MySQL or PostgreSQL, the
same family of relational DBMS). Part 1 is the vocabulary (table, row, column, type, primary key, server > database
> table). Part 2 is four SQL statements (CREATE DATABASE, CREATE TABLE, INSERT, SELECT) run the same way in both,
side by side, then how SQL compares with 15's dict list and how the two servers differ. Part 3 is the errors,
part 4 two cafe tasks. Students do not open a client yet: starting the servers and typing is chapter 33.

Every mysql> and cafe=# screen comes from tools/demo.py (real MySQL 8.4 and PostgreSQL 18, saved in tools/out.json).
Usage (in 32-database-basics): python3 tools/gen.py slides
"""
import html, json, os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from highlight import (spot, spot_off, cursor, cursor_off, ring, box as pen_box, underline, text as set_text,  # noqa: E402
                       SLAM, SLIDE, DIM, DELAY, PATH, STAGGER, WIPE, MARK, MORPH, MORPH_FROM, tok,
                       pulse, shine, shake, zoom, zoom_off, lspot, lspot_off, link)

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT):
    if f.endswith(".html"):
        os.remove(os.path.join(OUT, f))
HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "out.json")))

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
REAL = " SQL 출력은 tools/demo.py로 실제 MySQL 8.4와 PostgreSQL 18에서 실행한 결과예요."


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
def sheet(x, y, cols, rows, sid, widths, size=32, rh=74, hbg="#EEF0F3", hcol=INK, types=None, attrs="", name=None, ncol=None, pk=False, cell_attrs=None, hcols=None, head_attrs=None):
    """A database table drawn as a grid. Cells get ids sid-rIcJ, headers sid-hJ. Returns (html, geometry)."""
    cell_attrs = cell_attrs or {}
    W_ = sum(widths)
    th = rh + (round(size * 0.66 * 1.3) + 6 if types else 0)
    top = y + (56 if name else 0)
    H = th + rh * len(rows)
    o = [f'<div id="{sid}"{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{W_}px;height:{H + (56 if name else 0) + 4}px">']
    if name:
        o.append(p(f"position:absolute;left:0;top:0;height:44px;padding:0 18px;border-radius:10px 10px 0 0;background:{ncol or MY};font-family:{MONO};font-size:24px;font-weight:700;line-height:44px;color:#FFFFFF;white-space:nowrap", e(name)))
    oy = top - y
    o.append(f'<div style="position:absolute;left:0;top:{oy}px;width:{W_}px;height:{H}px;box-sizing:border-box;background:{CARD};border:2px solid #CFCAC0;border-radius:{"0 14px 14px 14px" if name else "14px"};overflow:hidden">')
    o.append(f'<div style="position:absolute;left:0;top:0;width:{W_ - 4}px;height:{min(th, H - 4)}px;background:{hbg}"></div>')
    cx = 0
    for j, (c, w) in enumerate(zip(cols, widths)):
        kc = hcols[j] if hcols else (VO if (pk and j == 0) else hcol)
        o.append(p(f"position:absolute;left:{cx}px;top:{(rh - size * 1.3) / 2 + (0 if not types else 0):.0f}px;width:{w}px;text-align:center;font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.3;color:{kc};white-space:nowrap", e(c), f' id="{sid}-h{j}"' + (head_attrs or {}).get(j, "")))
        if types:
            o.append(p(f"position:absolute;left:{cx}px;top:{rh - 10}px;width:{w}px;text-align:center;font-family:{MONO};font-size:{size * 0.66:.0f}px;font-weight:700;line-height:1.3;color:{GRAY};white-space:nowrap", e(types[j]), f' id="{sid}-t{j}"'))
        if j:
            o.append(f'<div style="position:absolute;left:{cx - 1}px;top:0;width:2px;height:{H - 4}px;background:#E2DED5"></div>')
        cx += w
    for i, r in enumerate(rows):
        ry = th + i * rh
        o.append(f'<div style="position:absolute;left:0;top:{ry - 1}px;width:{W_ - 4}px;height:2px;background:#E2DED5"></div>')
        cx = 0
        for j, (v, w) in enumerate(zip(r, widths)):
            num = v.isdigit()
            col = VO if (pk and j == 0) else INK
            o.append(p(f"position:absolute;left:{cx}px;top:{ry + (rh - size * 1.3) / 2:.0f}px;width:{w}px;text-align:center;font-family:{MONO};font-size:{size}px;font-weight:{700 if pk and j == 0 else 400};line-height:1.3;color:{col};white-space:nowrap", (f'<span{cell_attrs[(i, j)]}>{e(v)}</span>' if (i, j) in cell_attrs else e(v)) if v else "&#160;", f' id="{sid}-r{i}c{j}"'))
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
            + (p(f"position:absolute;left:0;top:{h / 2 + tsize * 0.55 + 14:.0f}px;width:{w}px;text-align:center;font-size:{ssize}px;line-height:1.35;color:{SUB};white-space:nowrap", sub) if sub else "")
            + '</div>')


def mysql_rows(lines):
    """terminal rows for a mysql session: 'mysql>' and '->' prompts get the prompt color"""


# =====================================================================
# chapter 32
# =====================================================================
MY, MYBG = "#00758F", "#E2F1F5"      # MySQL
PG, PGBG = "#336791", "#E6EDF5"      # PostgreSQL
VO, VOBG = "#B26A00", "#FBF0DF"      # primary key
PY, PYBG = BL, "#E8EFFD"             # Python
C1, C2, C3, C4 = TEAL, BL, RED, OR
EB1, EB2, EB3, EB4 = "1. 데이터베이스와 표", "2. SQL 네 문장 맛보기", "3. 자주 나는 오류", "4. 실제 상황 예제"
ORD = [("1", "latte", "2"), ("2", "americano", "1")]
ORD3 = ORD + [("3", "cake", "1")]
COLS = ["id", "menu", "qty"]
TYPES = ["INT", "VARCHAR(20)", "INT"]
MYV, PGV = "MySQL 8.4", "PostgreSQL 18"
NAME = {"my": MYV, "pg": PGV}
DCOL = {"my": MY, "pg": PG}
PROMPT_RE = re.compile(r"^(mysql>|    ->|[a-z]+[=\-(]#) ?(.*)$")


def Q(scene, db, part=None):
    """real screen lines of scene for db; part=k keeps only the k-th prompt block (a prompt line and what follows)"""
    lines = [l.rstrip() for l in D[scene][db]]
    while lines and not lines[-1]:
        lines.pop()
    if part is None:
        return lines
    blocks, cur = [], []
    for l in lines:
        if (l.startswith("mysql>") or re.match(r"^[a-z]+=#", l)) and cur:
            blocks.append(cur)
            cur = []
        cur.append(l)
    blocks.append(cur)
    b = blocks[part]
    while b and not b[-1]:
        b.pop()
    return b


def sql_rows(lines, marks=None):
    """Term rows for a mysql or psql screen. marks: {line index: {substring: id or attrs}}"""
    marks = marks or {}
    out = []
    for i, l in enumerate(lines):
        mk = marks.get(i, {})
        m = PROMPT_RE.match(l)
        if m:
            out.append(("q", m.group(1), m.group(2), mk))
        elif l.startswith("ERROR"):
            out.append(("e", l, mk))
        elif l.startswith("Query OK") or re.match(r"^(CREATE|INSERT) ", l) or l == "Database changed" or l.startswith("You are now connected"):
            out.append(("g", l, mk))
        elif re.match(r"^(\d+ rows? in set|\(\d+ rows?\))", l):
            out.append(("d", l, mk))
        else:
            out.append(("o", l, mk))
    return out


_old_row = Term._row


def _row(self, l):
    if l[0] == "q":
        pr, c = l[1], l[2]
        marks = l[-1] if isinstance(l[-1], dict) else {}
        pid = (marks.pop("@prompt", None) or "") if marks else ""
        pa = f' id="{pid}"' if pid else ""
        return "q", f"{pr} {c}", f'<span{pa} style="color:#7FD1C8">{e(pr)}</span> ' + mark(c, marks), "#F2C46D"
    return _old_row(self, l)


Term._row = _row
_old_html = Term.html


def _html(self):
    h = _old_html(self)
    h = h.replace('font-weight:700;color:#F2C46D', 'font-weight:700;color:#F2C46D')
    if getattr(self, "title", None) and self.bar:
        dots_end = '</div>'
        k = h.index('<div style="display:flex;flex-direction:row;gap:10px;height:16px;margin-bottom:20px">')
        j = h.index(dots_end, h.index('background:#7FD18B', k)) + len(dots_end)
        t = (f'<p style="position:absolute;left:{self.PX + 96}px;top:{self.PT - 6}px;font-family:{SANS};font-size:22px;font-weight:700;'
             f'line-height:28px;color:{self.tcol};white-space:nowrap">{e(self.title)}</p>')
        h = h[:j] + t + h[j:]
    return h


Term.html = _html
for _k in ("q",):
    pass


def DT(db, lines, x, y, size=26, w=None, lh=1.5, tid=None, attrs="", marks=None, bar=True, h=None):
    """a terminal holding one client's screen, its title (MySQL 8.4 or PostgreSQL 18) in the bar"""
    t = Term(sql_rows(lines, marks), x, y, size=size, w=w, lh=lh, tid=tid or f"t-{db}", attrs=attrs, bar=bar, h=h)
    t.title = NAME[db]
    t.tcol = {"my": "#7FD1C8", "pg": "#9DB8DA"}[db]
    return t


def same_h(*ts):
    """side-by-side terminals get the same height"""
    h = max(t.h for t in ts)
    for t in ts:
        t.h = h
    return h


def bold_q(t):
    """prompt lines are bold like the shell prompt lines of the other decks"""
    return t


# Term draws "$" and "#" rows bold; make the client rows bold too
_old_html2 = Term.html


def _html2(self):
    h = _old_html2(self)
    return h


def chipline(x, y, items, color, order=None, size=28, gap=14, attrs=""):
    """mono chips in one row"""
    return (f'<div{STAGGER(order, 70) if order else ""}{attrs} style="position:absolute;left:{x}px;top:{y}px;display:flex;flex-direction:row;flex-wrap:wrap;gap:{gap}px">'
            + "".join(p(f"height:{size + 26}px;padding:0 18px;border-radius:12px;background:#FFFFFF;border:2px solid {color};font-family:{MONO};font-size:{size}px;font-weight:700;line-height:{size + 22}px;color:{color};white-space:nowrap", e(it)) for it in items) + '</div>')


def code_line(x, y, html_, size=40, attrs="", color=INK):
    return p(f"position:absolute;left:{x}px;top:{y}px;font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.4;color:{color};white-space:pre", html_, attrs)


# =====================================================================
# cover
# =====================================================================
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px">',
       p("position:absolute;left:128px;top:300px;font-size:28px;font-weight:700;color:#7FD1C8", "KANT AX/AI 엔지니어 트랙 · 32"),
       f'<h1{SLAM(1)} style="position:absolute;left:128px;top:360px;font-size:100px;font-weight:900;line-height:1.15;color:#F6F5F1">데이터베이스 기초</h1>',
       p("position:absolute;left:128px;top:500px;font-size:52px;font-weight:700;line-height:1.3;color:#F6F5F1", "표, 타입, 기본 키,<br>SQL 맛보기"),
       p("position:absolute;left:128px;top:680px;font-size:32px;line-height:1.5;color:#BFC6D4", "MySQL과 PostgreSQL에서 똑같이 도는 SQL을 읽어요")]
t1 = DT("my", Q("select", "my"), 1060, 150, size=26, w=736, tid="cov-my")
t2 = DT("pg", Q("select", "pg"), 1060, t1.y + t1.h + 30, size=26, w=736, tid="cov-pg")
cov += [t1.html(), t2.html(), shine(2, "cov-my")]
W("cover", cov, "32 챕터는 데이터베이스 기초예요. 지금까지 주문은 파이썬 리스트와 딕셔너리에 담았어요. 프로그램을 끄면 그 값은 사라져요. 오늘은 데이터를 오래 담아 두는 데이터베이스가 무엇인지 보고, 표, 행, 열, 타입, 기본 키 같은 낱말을 익혀요. 그리고 SQL 네 문장으로 표를 만들고 넣고 꺼내는 화면을 읽어요. 오른쪽처럼 MySQL과 PostgreSQL 두 서버에 같은 문장을 보내면 같은 표가 나와요. 직접 서버를 켜고 쳐 보는 건 33에서 해요." + REAL, ("intro", "들어가기"))

ORDER.append("toc")   # written last, after page numbers are known

# =====================================================================
# why
# =====================================================================
P_O = "~/orders"
o = frame("why", "들어가기", "프로그램이 끝나면 리스트에 담은 주문도 사라져요", INK)
code = ['orders = []', 'orders.append(("latte", 2))', 'orders.append(("americano", 1))', 'print(orders)']
ed, g = editor("why-ed", "main.py", code, 96, 214, 820, fs=32, color=PY)
o.append(ed)
OUTL = "[('latte', 2), ('americano', 1)]"
t = Term([("$", P_O, "uv run main.py"), ("o", OUTL), ("$", P_O, "uv run main.py"), ("o", OUTL)], 96, g["top"] + g["h"] + 30, size=28, w=820, tid="t-why")
t.band(2, 3, order=3, color="rgba(242,196,109,.16)")
o.append(t.html())
MX, MYY, MW, MH = 1000, 214, 824, t.y + t.h - 214
o.append(f'<div id="why-mem" style="position:absolute;left:{MX}px;top:{MYY}px;width:{MW}px;height:{MH}px;box-sizing:border-box;background:{PYBG};border:3px solid {PY};border-radius:20px"></div>')
o.append(p(f"position:absolute;left:{MX + 40}px;top:{MYY + 34}px;font-size:30px;font-weight:700;color:{PY}", "실행 중인 프로그램의 메모리"))
o.append(p(f"position:absolute;left:{MX + 40}px;top:{MYY + 120}px;font-family:{MONO};font-size:36px;font-weight:700;color:{INK}", "orders"))
for k, txt in enumerate(['("latte", 2)', '("americano", 1)']):
    o.append(p(f"position:absolute;left:{MX + 40}px;top:{MYY + 210 + k * 130}px;height:76px;padding:0 26px;border-radius:12px;background:#FFFFFF;border:2px solid {PY};font-family:{MONO};font-size:34px;font-weight:700;line-height:72px;color:{INK};white-space:nowrap", e(txt), bi("rise", 1) + DELAY(k * 120)))
o.append(f'<div{bi("fade", 2)} style="position:absolute;left:{MX + 3}px;top:{MYY + 3}px;width:{MW - 6}px;height:{MH - 6}px;border-radius:17px;background:#F6F5F1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px">'
         + p(f"font-size:48px;font-weight:700;color:{RED}", "프로그램 끝")
         + p(f"font-size:30px;color:{SUB}", "메모리를 비우면서 orders도 사라져요") + '</div>')
o += tag(t, 2, "다시 빈 리스트부터", OR, 3, at=t.x + 470, gap=36)
o.append(caption("어제 받은 주문을 오늘도 보려면, 프로그램 밖 어딘가에 따로 담아 둬야 해요.", t.y + t.h + 60, 4, size=32))
W("why", o, "프로그램이 끝나면 리스트에 담은 주문도 사라져요. 13에서 배운 append로 orders 리스트에 주문 두 개를 담고 찍었어요. 이 값은 프로그램이 실행되는 동안 컴퓨터 메모리에만 있어요. 프로그램이 끝나면 파이썬이 메모리를 비우면서 orders도 같이 없어져요. 그래서 다시 실행하면 orders = []부터 새로 시작하고, 두 번째 실행에도 주문은 두 개뿐이에요. 카페라면 어제 받은 주문, 회원, 매출을 오늘도 봐야 해요. 프로그램 밖에 데이터를 따로 담아 두는 곳이 필요해요. 그곳이 오늘 배울 데이터베이스예요. 터미널 출력은 uv run main.py를 두 번 실제로 실행한 결과예요.")

# =====================================================================
# big picture
# =====================================================================
o = frame("big", "들어가기", "프로그램은 데이터베이스 서버에 SQL로 부탁해요", INK)
cls = [("터미널", "mysql, psql 프로그램", 330, "Code"), ("파이썬 앱", "주문 받는 프로그램", 530, "Code"), ("카페 키오스크", "매장 화면", 730, "Home")]
for k, (nm, sub, cy, ic) in enumerate(cls):
    o.append(node(96, cy - 75, 400, 150, nm, sub, BW, BWBG, f"bg-c{k}", icon=ic, tsize=30, ssize=22))
    o.append(svg(f'<path id="bg-p{k}" d="M512,{cy} L716,{cy}" fill="none" stroke="{BW}" stroke-width="4" stroke-linecap="round"/>' + head_at(718, cy, 0, BW), 1))
    o.append(dot(716, cy, BW, 2, f"bg-p{k}", 900 + k * 150))
o.append(p(f"position:absolute;left:520px;top:226px;font-size:26px;font-weight:700;color:{BW};white-space:nowrap", "SQL로 부탁해요", bi("fade", 1) + DELAY(150)))
o.append(f'<div id="bg-dbms" style="position:absolute;left:736px;top:240px;width:560px;height:580px;box-sizing:border-box;border:3px dashed #A9B0BC;border-radius:24px"></div>')
o.append(p(f"position:absolute;left:770px;top:262px;font-size:24px;font-weight:700;color:{GRAY};white-space:nowrap", "데이터베이스 서버 (DBMS) · 둘 중 하나를 써요"))
o.append(node(776, 320, 480, 200, "MySQL 서버", "기본 포트 3306", MY, MYBG, "bg-my", icon="Database", tsize=40, ssize=24))
o.append(node(776, 580, 480, 200, "PostgreSQL 서버", "기본 포트 5432", PG, PGBG, "bg-pg", icon="Database", tsize=40, ssize=24))
o.append(line_arrow(1310, 530, 1430, 530, VO, 3))
o.append(cyl(1446, 400, 378, 260, "데이터 파일", "디스크에 남아요", VO, VOBG, "bg-d", attrs=bi("rise", 3)))
o.append(caption("프로그램은 데이터 파일을 직접 만지지 않아요. 서버가 부탁을 차례대로 받아 대신 읽고 써요.", 880, 4, size=30))
W("big", o, "프로그램은 데이터베이스 서버에 SQL로 부탁해요. 왼쪽은 데이터를 쓰고 싶은 프로그램들이에요. 터미널의 mysql, psql 프로그램, 주문을 받는 파이썬 앱, 매장의 키오스크예요. 가운데가 데이터베이스 서버예요. 데이터베이스를 관리해 주는 프로그램이라서 DBMS, 데이터베이스 관리 시스템이라고 불러요. MySQL과 PostgreSQL이 가장 많이 쓰는 두 가지예요. 수업에서는 둘을 번갈아 써도 오늘 배우는 내용은 같아요. 프로그램이 SQL이라는 말로 부탁하면, 서버가 부탁을 차례대로 받아서 디스크의 데이터 파일을 대신 읽고 써요. 여럿이 동시에 써도 데이터가 꼬이지 않는 이유예요.")

# =====================================================================
# smallest example
# =====================================================================
o = frame("smallest", "들어가기", "SQL 한 줄을 보내면 서버가 표를 돌려줘요", INK)
o += parts(96, 226, [("SELECT", BL, "꺼내 줘요", None), ("*", MAG, "모든 열을", None), ("FROM orders", TEAL, "orders 표에서", None), (";", OR, "여기서 끝", None)], size=56, order=1, lab=26, lw=300, drop=30)
t1 = DT("my", Q("select", "my"), 96, 424, size=26, w=844, tid="sm-my", attrs=bi("rise", 2))
t2 = DT("pg", Q("select", "pg"), 980, 424, size=26, w=844, tid="sm-pg", attrs=bi("rise", 3))
same_h(t1, t2)
o += [t1.html(), t2.html()]
o.append(caption("두 서버가 같은 문장을 알아듣고 같은 세 행을 줘요. 표를 그리는 모양만 조금 달라요.", max(t1.y + t1.h, t2.y + t2.h) + 44, 4, size=30))
W("smallest", o, "SQL 한 줄을 보내면 서버가 표를 돌려줘요. 오늘 배울 것 중 가장 짧은 문장이에요. SELECT는 꺼내 달라는 말이고, 별표는 모든 열, FROM orders는 orders 표에서라는 뜻이에요. 끝의 세미콜론이 문장이 끝났다는 표시예요. 왼쪽은 MySQL, 오른쪽은 PostgreSQL에 같은 문장을 보낸 화면이에요. 둘 다 주문 세 행을 표로 돌려줘요. 테두리 모양과 마지막 줄만 조금 달라요. 이 표가 어떻게 생겼고 어떻게 만드는지 차례로 봐요." + REAL)

# =====================================================================
# part 1: database and tables
# =====================================================================
o = frame("f-what", EB1, "데이터베이스는 끄고 켜도 남고, 여럿이 같이 쓰는 데이터 창고예요", C1)
heads = ["", "프로그램을 끄면", "여러 프로그램이 동시에", "주문 1만 개 중 하나 찾기"]
rows = [("파이썬 변수", "사라져요", "한 프로그램 안에서만", "for로 처음부터 하나씩"),
        ("파일 (엑셀, txt)", "남아요", "둘이 같이 고치면 덮어써요", "파일을 처음부터 읽어요"),
        ("데이터베이스", "남아요", "차례대로 받아서 지켜 줘요", "조건을 주면 바로 찾아요")]
xs = [130, 540, 950, 1400]
ws = [380, 380, 420, 410]
for j, h in enumerate(heads):
    o.append(p(f"position:absolute;left:{xs[j]}px;top:236px;width:{ws[j]}px;font-size:26px;font-weight:700;color:{GRAY};white-space:nowrap", e(h)))
for i, (a_, b_, c_, d_) in enumerate(rows):
    y = 296 + i * 172
    last = i == 2
    a = bi("rise", 1) if last else ""
    if last:
        o.append(f'<div{a} id="fw-db" style="position:absolute;left:96px;top:{y}px;width:1728px;height:150px;border-radius:18px;background:#E1F2F3;border:3px solid {C1}"></div>')
    else:
        o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:150px;border-radius:18px;background:{CARD};border:2px solid {LINE}"></div>')
    o.append(p(f"position:absolute;left:{xs[0]}px;top:{y + 52}px;font-size:34px;font-weight:700;color:{C1 if last else INK};white-space:nowrap", e(a_), a))
    for j, v in enumerate((b_, c_, d_)):
        o.append(p(f"position:absolute;left:{xs[j + 1]}px;top:{y + 54}px;width:{ws[j + 1]}px;font-size:29px;font-weight:{700 if last else 400};color:{C1 if last else SUB};white-space:nowrap", e(v), a))
o.append(caption("이 창고를 맡아서 관리하는 프로그램이 MySQL, PostgreSQL 같은 DBMS예요.", 860, 2, size=32))
W("f-what", o, "데이터베이스는 끄고 켜도 남고, 여럿이 같이 쓰는 데이터 창고예요. 데이터를 담는 방법 세 가지를 비교했어요. 파이썬 변수는 앞에서 본 것처럼 프로그램을 끄면 사라져요. 엑셀이나 txt 파일은 남지만, 키오스크와 사장님 노트북이 같은 파일을 동시에 고치면 한쪽이 덮어써요. 주문 1만 개 중 하나를 찾으려면 파일을 처음부터 읽어야 하고요. 데이터베이스는 끄고 켜도 남고, 여러 프로그램의 부탁을 차례대로 받아서 데이터가 꼬이지 않게 지켜 줘요. 찾고 싶은 조건을 주면 바로 찾아 줘요. 이 창고를 관리하는 프로그램이 MySQL, PostgreSQL 같은 DBMS예요.", ("p1", "데이터베이스와 표"))

o = frame("f-rdb", EB1, "관계형 데이터베이스는 데이터를 표에 담아요", C1)
SX, SY = 96, 250
cw = [70, 110, 240, 130]
letters = ["", "A", "B", "C"]
grid = [["1", "id", "menu", "qty"], ["2", "1", "latte", "2"], ["3", "2", "americano", "1"]]
o.append(f'<div id="fr-sheet" style="position:absolute;left:{SX}px;top:{SY}px;width:{sum(cw) + 4}px;height:{56 + 4 * 64 + 4}px;box-sizing:border-box;background:{CARD};border:2px solid #CFCAC0;border-radius:14px;overflow:hidden">')
o.append(f'<div style="position:absolute;left:0;top:0;width:{sum(cw)}px;height:56px;background:#E7F0E9"></div>')
o.append(p(f"position:absolute;left:20px;top:12px;font-size:24px;font-weight:700;color:{GR}", "엑셀 · 주문.xlsx"))
for r in range(4):
    yy = 56 + r * 64
    cx = 0
    for c in range(4):
        txt = letters[c] if r == 0 else grid[r - 1][c]
        hdr = r == 0 or c == 0
        o.append(f'<div style="position:absolute;left:{cx}px;top:{yy}px;width:{cw[c]}px;height:64px;box-sizing:border-box;border-right:1px solid #DDD9D0;border-bottom:1px solid #DDD9D0;background:{"#F3F2EE" if hdr else "#FFFFFF"}"></div>')
        o.append(p(f"position:absolute;left:{cx}px;top:{yy + 14}px;width:{cw[c]}px;text-align:center;font-size:26px;font-weight:{700 if (r == 1 and c) else 400};color:{GRAY if hdr else INK};white-space:nowrap", e(txt)))
        cx += cw[c]
o.append('</div>')
ax = SX + sum(cw) + 40
o.append(line_arrow(ax, SY + 180, ax + 150, SY + 180, C1, 1))
html_, g = sheet(ax + 190, SY - 16, COLS, ORD, "fr-tab", [130, 300, 160], size=34, rh=80, name="orders", attrs=bi("rise", 1))
o.append(html_)
o.append(p(f"position:absolute;left:{g['x'] + g['w'] + 44}px;top:{SY + 90}px;width:{1824 - g['x'] - g['w'] - 44}px;font-size:28px;line-height:1.6;color:{SUB}", "시트 한 장을<br>데이터베이스에서는<br><b style=\"color:" + INK + "\">표(테이블)</b>라고 불러요.", bi("fade", 1) + DELAY(150)))
o.append(f'<div style="position:absolute;left:96px;top:640px;width:1728px;height:1px;background:{LINE}"></div>')
o.append(p(f"position:absolute;left:96px;top:676px;width:1728px;font-size:34px;font-weight:700;line-height:1.5;color:{INK}", "표끼리 번호로 이어서 쓸 수 있어서 관계형(Relational, RDB)이라고 불러요.", bi("fade", 2)))
o.append(p(f"position:absolute;left:96px;top:750px;width:1728px;font-size:28px;line-height:1.6;color:{SUB}", "주문 표에 메뉴 번호만 적고, 가격은 메뉴 표에서 찾아오는 식이에요. 표를 잇는 방법(JOIN)은 이 챕터에서 다루지 않아요.", bi("fade", 2)))
o.append(p(f"position:absolute;left:96px;top:880px;width:1728px;font-size:28px;line-height:1.6;color:{GRAY}", "MySQL과 PostgreSQL은 둘 다 관계형이에요. 표가 아닌 모양으로 담는 데이터베이스는 NoSQL이라고 따로 불러요.", bi("fade", 3)))
W("f-rdb", o, "관계형 데이터베이스는 데이터를 표에 담아요. 엑셀 시트를 떠올리면 쉬워요. 맨 위 줄에 항목 이름을 적고, 아래로 주문을 한 줄씩 적어요. 데이터베이스에서는 이런 시트 한 장을 표, 영어로 테이블이라고 불러요. 이 표의 이름은 orders예요. 표끼리 번호로 이어서 쓸 수 있어서 관계형 데이터베이스, 줄여서 RDB라고 불러요. 예를 들어 주문 표에 메뉴 번호만 적어 두고, 가격은 메뉴 표에서 찾아오는 식이에요. 표를 잇는 방법은 이 챕터에서 다루지 않아요. MySQL과 PostgreSQL은 둘 다 관계형이라서 오늘 배우는 낱말이 그대로 통해요.")

o = frame("f-rowcol", EB1, "가로 한 줄이 행(row), 세로 한 줄이 열(column)이에요", C1)
html_, g = sheet(96, 230, COLS, ORD3, "rc", [180, 380, 220], size=46, rh=112, name="orders")
o.append(html_)
LX = g["x"] + g["w"] + 70
r1y = row_y(g, 2)
o.append(spot(1, g["x"] - 4, r1y, LX - g["x"] + 700, g["rh"], pad=10, r=12))
o.append(p(f"position:absolute;left:{LX}px;top:{r1y + 6:.0f}px;font-size:36px;font-weight:700;color:{C1};white-space:nowrap", "행 = 주문 하나 (레코드)", bi("fade", 1)))
o.append(p(f"position:absolute;left:{LX}px;top:{r1y + 62:.0f}px;font-size:24px;color:{SUB};white-space:nowrap", "주문이 늘면 아래로 한 줄씩 늘어요", bi("fade", 1)))
cmx = g["cx"][1]
o.append(spot(2, cmx, g["y"], g["widths"][1], g["h"] + 150, pad=10, r=12))
o.append(p(f"position:absolute;left:{cmx}px;top:{g['y'] + g['h'] + 30:.0f}px;width:600px;font-size:36px;font-weight:700;color:{C1};white-space:nowrap", "열 = 항목 하나 (필드)", bi("fade", 2)))
o.append(p(f"position:absolute;left:{cmx}px;top:{g['y'] + g['h'] + 82:.0f}px;font-size:24px;color:{SUB};white-space:nowrap", "맨 위 이름이 그 열의 이름이에요", bi("fade", 2)))
o.append(spot_off(3))
PX0 = 1000
code = ['orders = [', '    {"id": 1, "menu": "latte", "qty": 2},', '    {"id": 2, "menu": "americano", "qty": 1},', '    {"id": 3, "menu": "cake", "qty": 1},', ']']
ed, g2 = editor("rc-py", "15의 딕셔너리 리스트", code, PX0, 230, 814, fs=25, color=PY, attrs=bi("rise", 3), nums=False)
o.append(ed)
o.append(lband(4, g2, 3, 1, C1))
o.append(p(f"position:absolute;left:{PX0}px;top:{g['y'] + g['h'] + 50:.0f}px;width:814px;font-size:27px;font-weight:700;line-height:1.5;color:{INK}", "딕셔너리 하나가 행, 키가 열이에요.", bi("fade", 4)))
W("f-rowcol", o, "가로 한 줄이 행, 세로 한 줄이 열이에요. 표의 가로 한 줄을 행, 영어로 row라고 해요. 주문 하나가 행 하나예요. 레코드라고도 불러요. 주문이 늘면 표가 아래로 한 줄씩 길어져요. 세로 한 줄은 열, 영어로 column이에요. id, menu, qty처럼 항목 하나가 열 하나예요. 필드라고도 해요. 맨 위에 적힌 이름이 그 열의 이름이에요. 15에서 배운 딕셔너리 리스트와 같은 모양이에요. 딕셔너리 하나가 행이고, 키 이름이 열이에요. 다른 점은 표에서는 모든 행이 같은 열을 가진다는 거예요.")

o = frame("f-type", EB1, "열마다 담을 값의 타입을 미리 정해 둬요", C1)
html_, g = sheet(96, 230, COLS, ORD, "ft", [180, 380, 200], size=40, rh=96, types=TYPES, name="orders")
o.append(html_)
o.append(pen_box(1, g["x"] + 8, g["y"] + g["rh"] - 12, g["w"] - 16, 46, MAG))
TX = 96 + g["w"] + 90
maps = [("INT", "정수", "int", "1, 2, 4500"), ("VARCHAR(20)", "글자, 20자까지", "str", "'latte'")]
for k, (sq, ko, py, ex) in enumerate(maps):
    y = 250 + k * 190
    o.append(p(f"position:absolute;left:{TX}px;top:{y}px;font-family:{MONO};font-size:40px;font-weight:700;color:{MAG};white-space:nowrap", e(sq), bi("rise", 2) + DELAY(k * 120)))
    o.append(p(f"position:absolute;left:{TX}px;top:{y + 64}px;font-size:28px;color:{SUB};white-space:nowrap", f"{e(ko)} · 파이썬의 <span style=\"font-family:{MONO};font-weight:700;color:{PY}\">{py}</span> · 예: <span style=\"font-family:{MONO}\">{e(ex)}</span>", bi("rise", 2) + DELAY(k * 120)))
o.append(f'<div style="position:absolute;left:96px;top:660px;width:1728px;height:1px;background:{LINE}"></div>')
o.append(p(f"position:absolute;left:96px;top:696px;width:1728px;font-size:34px;font-weight:700;line-height:1.5;color:{INK}", "파이썬 리스트는 아무 값이나 담지만, 표의 열은 정한 타입만 받아요.", bi("fade", 3)))
o.append(p(f"position:absolute;left:96px;top:770px;width:1728px;font-size:28px;line-height:1.6;color:{SUB}", "qty 열에 'many' 같은 글자를 넣으면 서버가 막아요. 3파트에서 실제 오류를 봐요.", bi("fade", 3)))
o.append(p(f"position:absolute;left:96px;top:880px;width:1728px;font-size:26px;line-height:1.6;color:{GRAY}", "INT와 VARCHAR는 MySQL과 PostgreSQL에서 이름이 같아요. 날짜, 소수 같은 타입도 있지만 이 챕터에서는 두 가지만 써요.", bi("fade", 3)))
W("f-type", o, "열마다 담을 값의 타입을 미리 정해 둬요. 표의 열 이름 아래 회색 글자가 열의 타입이에요. INT는 정수예요. 12에서 배운 파이썬의 int와 같아요. VARCHAR(20)은 20자까지의 글자예요. 파이썬의 str과 같고, 괄호 안 숫자가 최대 글자 수예요. 파이썬 리스트에는 숫자와 글자를 섞어 담을 수 있지만, 표의 열은 정한 타입만 받아요. 수량 칸에 many 같은 글자를 넣으면 서버가 막아 줘요. INT와 VARCHAR는 MySQL과 PostgreSQL에서 이름이 같아요. 날짜나 소수 같은 타입도 있지만 이 챕터에서는 두 가지만 써요.")

o = frame("f-pk", EB1, "기본 키(Primary Key)는 행마다 다른 번호예요", C1)
html_, g = sheet(96, 250, ["menu", "qty"], [("latte", "2"), ("latte", "2")], "pk0", [300, 180], size=38, rh=92, name="id 없는 표", ncol=GRAY)
o.append(html_)
o.append(p(f"position:absolute;left:96px;top:{g['y'] + g['h'] + 36:.0f}px;width:700px;font-size:32px;font-weight:700;line-height:1.5;color:{RED}", "두 손님이 라테 2잔씩 주문했어요.<br>한 분이 취소하면 어느 줄을 지울까요?", bi("fade", 1)))
html_, g2 = sheet(1000, 250, COLS, [("1", "latte", "2"), ("2", "latte", "2")], "pk1", [150, 300, 180], size=38, rh=92, name="orders", pk=True, attrs=bi("rise", 2))
o.append(html_)
o.append(ring(3, g2["cx"][0] + 30, row_y(g2, 1) + 14, 90, 64, VO))
o.append(p(f"position:absolute;left:1000px;top:{g2['y'] + g2['h'] + 36:.0f}px;width:824px;font-size:32px;font-weight:700;line-height:1.5;color:{VO}", "2번 주문을 지우면 돼요.", bi("fade", 3)))
o.append(f'<div style="position:absolute;left:96px;top:780px;width:1728px;height:1px;background:{LINE}"></div>')
rules = ["다른 행과 겹치면 안 돼요", "비워 둘 수 없어요", "카페 진동벨 번호처럼, 이 번호만 보면 행 하나가 정해져요"]
o.append(f'<div{STAGGER(4, 100)} style="position:absolute;left:96px;top:812px;width:1728px;display:flex;flex-direction:column;gap:12px">'
         + "".join(p(f"font-size:30px;line-height:1.45;color:{INK}", f'<span style="color:{VO};font-weight:700">{i + 1}</span>&#160;&#160;{e(r)}') for i, r in enumerate(rules)) + '</div>')
W("f-pk", o, "기본 키는 행마다 다른 번호예요. 영어로 Primary Key라고 해요. 왼쪽 표처럼 두 손님이 똑같이 라테 2잔을 주문하면 두 행이 완전히 같아져요. 한 분이 취소하면 어느 행을 지워야 할지 알 수 없어요. 그래서 행마다 겹치지 않는 번호 칸을 하나 둬요. 오른쪽 표의 id가 기본 키예요. 2번 주문을 취소한다고 말하면 행 하나가 정확히 정해져요. 카페 진동벨 번호와 같아요. 기본 키는 다른 행과 겹치면 안 되고, 비워 둘 수도 없어요. 같은 번호를 넣으면 서버가 막아요. 3파트에서 실제로 봐요.")

o = frame("f-tree", EB1, "서버 안에 데이터베이스가, 그 안에 표가 있어요", C1)
o.append(f'<div id="ft-srv" style="position:absolute;left:96px;top:214px;width:1140px;height:760px;box-sizing:border-box;background:{MYBG};border:3px solid {MY};border-radius:24px"></div>')
o.append(p(f"position:absolute;left:132px;top:238px;font-size:34px;font-weight:700;color:{MY}", "데이터베이스 서버 (MySQL 또는 PostgreSQL)"))
o.append(f'<div{bi("rise", 1)} style="position:absolute;left:132px;top:310px;width:640px;height:630px;box-sizing:border-box;background:#FFFFFF;border:3px solid {C1};border-radius:20px"></div>')
o.append(p(f"position:absolute;left:166px;top:334px;font-size:30px;font-weight:700;color:{C1};white-space:nowrap", "데이터베이스 cafe", bi("rise", 1)))
o.append(sheet(166, 410, COLS, ORD, "ft-o", [110, 250, 150], size=26, rh=54, name="orders", attrs=bi("rise", 2))[0])
o.append(sheet(166, 700, ["id", "name", "price"], [("1", "americano", "4000"), ("2", "latte", "4500")], "ft-m", [110, 250, 150], size=26, rh=54, name="menu", attrs=bi("rise", 2) + DELAY(150))[0])
sysd = [("MySQL", ["information_schema", "mysql", "performance_schema", "sys"]), ("PostgreSQL", ["postgres", "template0", "template1"])]
inner = p(f"font-size:28px;font-weight:700;line-height:1.4;color:{GRAY}", "서버가 스스로 쓰는<br>데이터베이스")
for nm, lst in sysd:
    inner += p(f"margin-top:14px;font-size:27px;font-weight:700;color:{DCOL['my' if nm == 'MySQL' else 'pg']}", nm)
    inner += "".join(p(f"font-family:{MONO};font-size:24px;font-weight:700;line-height:1.4;color:{GRAY};white-space:nowrap", e(s_)) for s_ in lst)
o.append(f'<div{bi("fade", 3)} style="position:absolute;left:804px;top:310px;width:400px;height:630px;box-sizing:border-box;border:3px dashed #A9B0BC;border-radius:20px;padding:26px 28px;display:flex;flex-direction:column;gap:8px">'
         + inner + p(f"margin-top:auto;font-size:26px;font-weight:700;line-height:1.5;color:{GRAY}", "건드리지 않아요") + '</div>')
an = [("서버", "컴퓨터", MY), ("데이터베이스", "폴더", C1), ("표", "엑셀 파일", VO), ("행과 열", "시트 안의 칸", INK)]
o.append(p(f"position:absolute;left:1300px;top:230px;font-size:30px;font-weight:700;color:{GRAY}", "파일로 치면", bi("fade", 4)))
o.append(f'<div{STAGGER(4, 90)} style="position:absolute;left:1300px;top:300px;width:524px;display:flex;flex-direction:column;gap:34px">'
         + "".join(f'<div style="display:flex;flex-direction:row;align-items:center;gap:16px;padding-left:{k * 26}px">'
                   + p(f"font-size:38px;font-weight:700;color:{c};white-space:nowrap", e(a_)) + p(f"font-size:32px;color:{SUB};white-space:nowrap", "= " + e(b_)) + '</div>' for k, (a_, b_, c) in enumerate(an)) + '</div>')
o.append(p(f"position:absolute;left:1300px;top:690px;width:524px;font-size:30px;line-height:1.6;color:{SUB}", "가게나 서비스마다<br>데이터베이스를 하나씩 만들고,<br>그 안에 주문 표, 메뉴 표처럼<br>표를 여러 개 둬요.", bi("fade", 5)))
W("f-tree", o, "서버 안에 데이터베이스가, 그 안에 표가 있어요. 서버 하나에 데이터베이스를 여러 개 만들 수 있어요. 보통 서비스나 가게마다 하나씩 만들어요. 오늘은 cafe 데이터베이스를 만들고, 그 안에 주문 표 orders를 둬요. 4파트에서는 메뉴 표 menu도 더해요. 오른쪽 점선 안은 서버가 처음부터 갖고 있는 데이터베이스예요. 서버가 스스로 쓰는 것이라 건드리지 않아요. MySQL과 PostgreSQL은 이름만 달라요. 파일로 치면 서버는 컴퓨터, 데이터베이스는 폴더, 표는 엑셀 파일, 행과 열은 시트 안의 칸이에요. 이름들은 두 서버의 데이터베이스 목록을 실제로 띄워서 옮겼어요. 다음 파트에서 이 구조를 SQL로 만들어요.")

# =====================================================================
# part 2: four SQL statements
# =====================================================================
o = frame("s-intro", EB2, "SQL은 서버에 보내는 부탁 문장이에요", C2)
stm = [("CREATE DATABASE", "데이터베이스를 만들어요", "CREATE DATABASE cafe;"),
       ("CREATE TABLE", "표를 만들고 열과 타입을 정해요", "CREATE TABLE orders (…);"),
       ("INSERT", "표에 행을 넣어요", "INSERT INTO orders VALUES (…);"),
       ("SELECT", "표에서 행을 꺼내요", "SELECT * FROM orders;")]
for k, (kw, ko, ex) in enumerate(stm):
    y = 226 + k * 172
    a = bi("rise", k + 1) + DIM("sql")
    o.append(p(f"position:absolute;left:96px;top:{y}px;width:72px;font-size:56px;font-weight:900;line-height:1.3;color:{C2}", str(k + 1), a))
    o.append(p(f"position:absolute;left:190px;top:{y + 4}px;font-family:{MONO};font-size:44px;font-weight:700;line-height:1.3;color:{INK};white-space:nowrap", e(kw), a))
    o.append(p(f"position:absolute;left:190px;top:{y + 72}px;font-size:28px;line-height:1.4;color:{SUB};white-space:nowrap", e(ko) + f' <span style="font-family:{MONO};font-size:24px;font-weight:700;color:{GRAY}">&#160;{e(ex)}</span>', a))
o.append(f'<div{bi("rise", 5)} style="position:absolute;left:1180px;top:226px;width:644px;height:{226 + 3 * 172 + 120 - 226}px;box-sizing:border-box;background:{CARD};border:2px solid {LINE};border-radius:20px;padding:40px 40px;display:flex;flex-direction:column;gap:30px">'
         + p(f"font-size:32px;font-weight:700;color:{C2}", "읽을 때 알아 둘 세 가지")
         + p(f"font-size:29px;line-height:1.55;color:{INK}", f'문장은 <b style="font-family:{MONO};color:{OR}">;</b>로 끝나요.<br>;가 나와야 서버가 실행해요.')
         + p(f"font-size:29px;line-height:1.55;color:{INK}", "SQL 낱말은 대문자로 쓰는 게 약속이에요.<br>소문자로 써도 돌아가요.")
         + p(f"font-size:29px;line-height:1.55;color:{INK}", f'글자 값은 <b style="font-family:{MONO};color:{MAG}">\'latte\'</b>처럼<br>작은따옴표로 감싸요.')
         + p(f"margin-top:auto;padding-top:26px;border-top:2px solid {LINE};font-size:26px;line-height:1.55;color:{SUB}", "이 챕터에서는 화면을 읽기만 해요.<br>서버를 켜고 직접 치는 건 33에서 해요.") + '</div>')
W("s-intro", o, "SQL은 서버에 보내는 부탁 문장이에요. 오늘은 네 문장만 봐요. CREATE DATABASE로 데이터베이스를 만들고, CREATE TABLE로 표를 만들어요. INSERT로 표에 행을 넣고, SELECT로 꺼내요. 이 네 문장은 MySQL과 PostgreSQL에서 글자 하나 안 바꾸고 똑같이 돌아요. 읽을 때 알아 둘 것이 세 가지 있어요. 문장은 세미콜론으로 끝나요. SQL 낱말은 대문자로 쓰는 게 약속이지만 소문자로 써도 돼요. 글자 값은 작은따옴표로 감싸요. 이 챕터에서는 실제로 실행한 화면을 읽기만 하고, 서버를 켜고 직접 치는 건 33에서 해요.", ("p2", "SQL 네 문장 맛보기"))

# --- CREATE DATABASE
o = frame("s-db", EB2, "CREATE DATABASE로 cafe를 만들고, 그 안으로 들어가요", C2)
lm = Q("db", "my")
lp = Q("db", "pg")
t1 = DT("my", lm, 96, 214, size=30, w=1728, tid="db-my", marks={3: {"USE cafe;": 'id="db-use"'}})
t1.band(0, 1, order=1, color="rgba(127,209,139,.14)")
t2 = DT("pg", lp, 96, t1.y + t1.h + 36, size=30, w=1728, tid="db-pg")
t2.band(0, 1, order=1, color="rgba(127,209,139,.14)")
o += [t1.html(), t2.html()]
o += tag(t1, 0, "만드는 문장은 같아요", GR, 1, at=t1.x + 900)
o.append(underline(2, round(t1.sx(3, "USE")), round(t1.sx(3, "USE") + t1.sw("USE cafe;")), round(t1.top(3) + t1.lp - 4), OR))
o.append(underline(2, round(t2.sx(2, "\\c")), round(t2.sx(2, "\\c") + t2.sw("\\c cafe")), round(t2.top(2) + t2.lp - 4), OR))
o += tag(t1, 3, "들어가는 명령은 달라요", OR, 2, at=t1.x + 900)
o += tag(t2, 2, "같은 일, 다른 모양", OR, 2, at=t1.x + 900)
o.append(caption("프롬프트도 바뀌어요. PostgreSQL은 지금 있는 데이터베이스 이름을 앞에 보여 줘요.", t2.y + t2.h + 44, 3, size=30))
W("s-db", o, "CREATE DATABASE로 cafe를 만들고, 그 안으로 들어가요. 위가 MySQL, 아래가 PostgreSQL 화면이에요. 첫 줄 CREATE DATABASE cafe;는 두 서버에서 똑같아요. 서버 안에 cafe라는 빈 데이터베이스가 생겨요. 다음은 이제부터 cafe에서 일하겠다고 알리는 명령이에요. MySQL은 USE cafe;, PostgreSQL은 역슬래시 c cafe를 써요. 하는 일은 같고 모양만 달라요. 역슬래시 c는 SQL이 아니라 psql 프로그램의 명령이라서 끝에 세미콜론이 없어요. PostgreSQL의 프롬프트는 postgres=#에서 cafe=#로 바뀌어요. 지금 있는 데이터베이스 이름이 앞에 나와요." + REAL)

# --- CREATE TABLE
o = frame("s-table", EB2, "CREATE TABLE로 열 이름, 타입, 기본 키를 정해요", C2)
cc = {"id": VO, "menu": MAG, "qty": TEAL}
mk = {1: {"id": f'style="color:{VO}"' + MARK(1)}, 2: {"menu": f'style="color:{MAG}"' + MARK(2)}, 3: {"qty": f'style="color:{TEAL}"' + MARK(3)}}
t1 = DT("my", Q("table", "my"), 96, 214, size=34, w=1000, lh=1.5, tid="tb-my", marks=mk)
o.append(t1.html())
o += tag(t1, 0, "표 이름 orders", BL, None, at=t1.x + 640, gap=30)
o += tag(t1, 1, "정수 · 기본 키", VO, 1, at=t1.x + 640, gap=30)
o += tag(t1, 2, "글자 20자까지", MAG, 2, at=t1.x + 640, gap=30)
o += tag(t1, 3, "정수", TEAL, 3, at=t1.x + 640, gap=30)
o += tag(t1, 4, ";가 나와야 실행해요", OR, 4, at=t1.x + 640, gap=30)
t2 = DT("pg", Q("table", "pg"), 1140, 214, size=26, w=684, lh=1.5, tid="tb-pg", attrs=bi("rise", 4))
o.append(t2.html())
html_, g = sheet(96, t1.y + t1.h + 50, COLS, [], "tb-tab", [200, 400, 240], size=40, rh=84, types=TYPES, name="orders", pk=True, hcols=[VO, MAG, TEAL], attrs=bi("rise", 5))
o.append(html_)
o.append(p(f"position:absolute;left:1140px;top:{t2.y + t2.h + 44}px;width:684px;font-size:28px;line-height:1.6;color:{SUB}", "길면 줄을 나눠 써도 돼요.<br>이어지는 줄의 프롬프트는 <span style=\"font-family:" + MONO + ";font-weight:700;color:" + INK + "\">-></span>, <span style=\"font-family:" + MONO + ";font-weight:700;color:" + INK + "\">cafe(#</span>로 바뀌어요.", bi("fade", 4)))
o.append(p(f"position:absolute;left:96px;top:{g['y'] + g['h'] + 36:.0f}px;width:1000px;font-size:30px;font-weight:700;line-height:1.6;color:{INK}", "만든 표는 아직 행이 없는 빈 표예요.", bi("fade", 5)))
W("s-table", o, "CREATE TABLE로 열 이름, 타입, 기본 키를 정해요. 표 이름 orders 뒤 괄호 안에 열을 쉼표로 나눠 적어요. 열마다 이름, 타입 순서예요. id는 정수이고, 뒤에 PRIMARY KEY를 붙여서 기본 키로 정했어요. menu는 20자까지의 글자, qty는 정수예요. 문장이 길어서 줄을 나눠 쳤어요. 세미콜론이 나오기 전까지는 서버가 실행하지 않고 다음 줄을 기다려요. 그래서 이어지는 줄의 프롬프트가 MySQL은 화살표, PostgreSQL은 cafe 괄호 샵으로 바뀌어요. 오른쪽 PostgreSQL도 같은 문장이에요. 다 만들면 열 이름과 타입만 있고 행은 없는 빈 표가 생겨요." + REAL)

# --- INSERT one row
o = frame("s-insert", EB2, "INSERT로 표에 행을 하나 넣어요", C2)
lm, lp = Q("insert", "my"), Q("insert", "pg")
t1 = DT("my", lm, 96, 214, size=26, w=844, tid="in-my", marks={0: {"(1, 'latte', 2)": 'id="in-v"'}})
t2 = DT("pg", lp, 980, 214, size=26, w=844, tid="in-pg")
t1.band(1, order=2, color="rgba(127,209,139,.16)")
t2.band(1, order=2, color="rgba(127,209,139,.16)")
o += [t1.html(), t2.html()]
o += tag(t1, 1, "1행이 들어갔어요", GR, 2, gap=30)
o += tag(t2, 1, "뒤의 1이 넣은 행 수", GR, 2, at=t2.x + 250, gap=30)
SY0 = t1.y + t1.h + 100
html_, g = sheet(96, SY0, COLS, [], "in-tab", [200, 420, 240], size=48, rh=120, name="orders", pk=True, hcols=[VO, MAG, TEAL])
o.append(html_)
ry = g["y"] + g["th"]
o.append(f'<div id="in-row" data-build-in="fly order 1" data-from="in-v" style="position:absolute;left:{g["x"] + 2}px;top:{ry}px;width:{g["w"] - 4}px;height:{g["rh"]}px;background:#FFFFFF;border:2px solid #CFCAC0;border-top:none;border-radius:0 0 14px 14px;display:flex;flex-direction:row">'
         + "".join(p(f"width:{w}px;flex:none;text-align:center;font-family:{MONO};font-size:48px;font-weight:{700 if j == 0 else 400};line-height:{g['rh']}px;color:{[VO, MAG, TEAL][j]}", e(v)) for j, (v, w) in enumerate(zip(["1", "latte", "2"], [198, 420, 238]))) + '</div>')
RX = 96 + g["w"] + 90
o.append(code_line(RX, SY0 + 40, f'VALUES (<span style="color:{VO}">1</span>, <span style="color:{MAG}">\'latte\'</span>, <span style="color:{TEAL}">2</span>)', size=40))
o.append(p(f"position:absolute;left:{RX}px;top:{SY0 + 130}px;width:{1824 - RX}px;font-size:30px;font-weight:700;line-height:1.6;color:{INK}", "괄호 안의 값이 열 순서대로 들어가요.", bi("fade", 3)))
o.append(p(f"position:absolute;left:{RX}px;top:{SY0 + 200}px;width:{1824 - RX}px;font-size:27px;line-height:1.6;color:{SUB}", "id, menu, qty 순서로 만들었으니<br>1, 'latte', 2 순서로 적어요.<br>글자 값만 작은따옴표로 감싸요.", bi("fade", 3)))
W("s-insert", o, "INSERT로 표에 행을 하나 넣어요. INSERT INTO orders는 orders 표에 넣겠다는 말이고, VALUES 뒤 괄호 안이 넣을 값이에요. 값은 표를 만들 때 정한 열 순서대로 들어가요. id, menu, qty 순서였으니 1, latte, 2로 적어요. latte는 글자라서 작은따옴표로 감쌌어요. 넣으면 빈 표에 행이 하나 생겨요. MySQL은 Query OK, 1 row affected, PostgreSQL은 INSERT 0 1이라고 알려 줘요. 둘 다 행 하나가 들어갔다는 뜻이에요. PostgreSQL의 앞 숫자 0은 이 챕터에서는 신경 쓰지 않아도 돼요." + REAL)

# --- INSERT with column names, two rows (code morph)
o = frame("s-insert2", EB2, "열 이름을 적으면 순서가 보이고, 여러 행을 한 번에 넣어요", C2)
S1 = (tok("ii", "INSERT INTO orders") + " " + tok("vv", "VALUES") + " " + tok("a", f'(<span style="color:{VO}">1</span>, \'latte\', 2)') + tok("sc", ";"))
o.append(code_line(96, 226, S1, size=44, attrs=' id="i2-a"' + MORPH_FROM()))
S2 = (tok("ii", "INSERT INTO orders") + " " + tok("cols", f'<span style="color:{BL}">(id, menu, qty)</span>') + "<br>"
      + tok("vv", "VALUES") + " " + tok("b", f'(<span style="color:{VO}">2</span>, \'americano\', 1),') + " " + tok("c", f'(<span style="color:{VO}">3</span>, \'cake\', 1)') + tok("sc", ";"))
o.append(code_line(96, 226, S2, size=44, attrs=MORPH(1, "i2-a")))
lm, lp = Q("insert2", "my"), Q("insert2", "pg")
t1 = DT("my", lm, 96, 420, size=24, w=1728, tid="i2-my", attrs=bi("rise", 2))
t2 = DT("pg", lp, 96, t1.y + t1.h + 30, size=24, w=1728, tid="i2-pg", attrs=bi("rise", 2) + DELAY(150))
o += [t1.html(), t2.html()]
o += tag(t1, 1, "두 행이 들어갔어요", GR, 3, at=t1.x + 640, gap=30)
o += tag(t2, 1, "뒤의 2가 넣은 행 수", GR, 3, at=t2.x + 640, gap=30)
o.append(caption("괄호 묶음을 쉼표로 이어 적으면 한 문장으로 여러 행이 들어가요.", t2.y + t2.h + 44, 4, size=30))
W("s-insert2", o, "열 이름을 적으면 순서가 보이고, 여러 행을 한 번에 넣어요. 앞 장의 문장에 두 가지를 더했어요. 표 이름 뒤에 열 이름을 괄호로 적으면 값이 어느 열에 들어가는지 한눈에 보여요. 표의 열 순서를 외우지 않아도 돼요. VALUES 뒤에는 괄호 묶음을 쉼표로 이어 적어서 2번, 3번 주문을 한 번에 넣었어요. MySQL은 2 rows affected, PostgreSQL은 INSERT 0 2로 두 행이 들어갔다고 알려 줘요. MySQL의 Records 줄은 넣은 행과 겹친 행, 경고 수를 보여 줘요." + REAL)

# --- SELECT columns and WHERE
o = frame("s-select", EB2, "SELECT 뒤에 열을 고르고, WHERE로 행을 골라요", C2)
lm, lp = Q("select2", "my"), Q("select2", "pg")
t1 = DT("my", lm, 96, 214, size=22, w=844, lh=1.45, tid="se-my")
t2 = DT("pg", lp, 980, 214, size=22, w=844, lh=1.45, tid="se-pg")
im = [i for i, l in enumerate(lm) if l.startswith("mysql>")]
ip = [i for i, l in enumerate(lp) if l.startswith("cafe=#")]
t1.band(im[0], im[1] - 2, order=1, color="rgba(111,155,245,.16)")
t2.band(ip[0], ip[1] - 1, order=1, color="rgba(111,155,245,.16)")
t1.band(im[1], len(lm) - 1, order=2, color="rgba(227,168,74,.18)")
t2.band(ip[1], len(lp) - 1, order=2, color="rgba(227,168,74,.18)")
o += [t1.html(), t2.html()]
o += tag(t1, im[0], "menu, qty 열만", BL, 1, at=t1.x + 520, gap=24)
o += tag(t1, im[1], "id가 2인 행만", OR, 2, at=t1.x + 560, gap=24)
yb = max(t1.y + t1.h, t2.y + t2.h) + 40
o.append(p(f"position:absolute;left:96px;top:{yb}px;width:1728px;font-size:30px;font-weight:700;line-height:1.6;color:{INK}", f'WHERE 뒤에 조건을 적어요. 같다는 파이썬의 <span style="font-family:{MONO}">==</span>와 달리 <span style="font-family:{MONO};color:{OR}">=</span> 하나예요.', bi("fade", 3)))
W("s-select", o, "SELECT 뒤에 열을 고르고, WHERE로 행을 골라요. 별표 대신 열 이름을 쉼표로 적으면 그 열만 꺼내요. 첫 문장은 menu와 qty 두 열만 꺼냈어요. 두 번째 문장은 끝에 WHERE id = 2를 붙였어요. WHERE 뒤에 조건을 적으면 조건에 맞는 행만 나와요. 17에서 배운 if와 비슷해요. 다만 같다를 파이썬은 등호 두 개로 쓰고, SQL은 하나로 써요. 작다, 크다는 파이썬처럼 부등호를 써요. 4파트 예제에서 써 봐요. 행이 몇 개 나왔는지는 MySQL은 rows in set, PostgreSQL은 괄호 안 rows로 알려 줘요." + REAL)

# --- compare with Python
o = frame("s-py", EB2, "파이썬 리스트로 하던 일을 SQL로 하면 이렇게 돼요", C2)
o.append(p(f"position:absolute;left:96px;top:226px;width:250px;font-size:26px;font-weight:700;color:{GRAY}", "하는 일"))
o.append(p(f"position:absolute;left:360px;top:226px;font-size:26px;font-weight:700;color:{PY}", "파이썬 (15, 23)"))
o.append(p(f"position:absolute;left:1180px;top:226px;font-size:26px;font-weight:700;color:{C2}", "SQL"))
cmpr = [("담을 곳 만들기", "orders = []", "CREATE TABLE orders (…);"),
        ("하나 넣기", 'orders.append({"id": 1, …})', "INSERT INTO orders VALUES (1, …);"),
        ("모두 보기", "print(orders)", "SELECT * FROM orders;"),
        ("골라 보기", '[o for o in orders if o["id"] == 2]', "SELECT * FROM orders WHERE id = 2;"),
        ("넣는 값", "아무 값이나 들어가요", "열 타입에 맞는 값만 들어가요"),
        ("프로그램을 끄면", "사라져요", "서버에 남아요")]
for i, (k_, a_, b_) in enumerate(cmpr):
    y = 276 + i * 100
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:1px;background:{LINE}"></div>')
    an = bi("rise", 1 if i < 2 else (2 if i < 4 else 3)) + DELAY((i % 2) * 120)
    mono_a = not a_.endswith("요")
    o.append(p(f"position:absolute;left:96px;top:{y + 28}px;width:250px;font-size:28px;font-weight:700;color:{INK};white-space:nowrap", e(k_), an))
    o.append(p(f"position:absolute;left:360px;top:{y + 28}px;width:780px;{'font-family:' + MONO + ';font-size:28px;font-weight:700;' if mono_a else 'font-size:28px;'}color:{PY};white-space:nowrap", e(a_), an))
    o.append(p(f"position:absolute;left:1180px;top:{y + 28}px;width:644px;{'font-family:' + MONO + ';font-size:28px;font-weight:700;' if mono_a else 'font-size:28px;font-weight:700;'}color:{C2};white-space:nowrap", e(b_), an))
o.append(f'<div style="position:absolute;left:96px;top:{276 + 6 * 100}px;width:1728px;height:1px;background:{LINE}"></div>')
o.append(caption("넣고 꺼내는 일은 같고, 담는 곳이 메모리에서 서버로 바뀌어요.", 276 + 6 * 100 + 36, 4, size=30))
W("s-py", o, "파이썬 리스트로 하던 일을 SQL로 하면 이렇게 돼요. 담을 곳을 만드는 일은 빈 리스트 대신 CREATE TABLE이에요. 하나 넣기는 append 대신 INSERT, 모두 보기는 print 대신 SELECT 별표예요. 23에서 배운 리스트 컴프리헨션으로 id가 2인 주문을 고르던 일은 WHERE 한 줄이면 돼요. 다른 점도 두 가지예요. 리스트에는 아무 값이나 들어가지만 표의 열은 정한 타입만 받아요. 그리고 리스트는 프로그램을 끄면 사라지지만 표는 서버에 남아요.")

# --- MySQL and PostgreSQL side by side
o = frame("s-two", EB2, "MySQL과 PostgreSQL은 SQL이 같고, 프로그램 명령 몇 개가 달라요", C2)
o.append(p(f"position:absolute;left:96px;top:226px;font-size:26px;font-weight:700;color:{GR}", "그대로 같은 것"))
o.append(chipline(96, 270, ["CREATE DATABASE", "CREATE TABLE", "INSERT", "SELECT", "WHERE", "INT", "VARCHAR(20)", "PRIMARY KEY"], GR, 1, size=26))
TY = 370
o.append(p(f"position:absolute;left:96px;top:{TY}px;font-size:26px;font-weight:700;color:{OR}", "다른 것"))
o.append(p(f"position:absolute;left:620px;top:{TY}px;font-size:26px;font-weight:700;color:{MY}", MYV))
o.append(p(f"position:absolute;left:1220px;top:{TY}px;font-size:26px;font-weight:700;color:{PG}", PGV))
diff = [("프롬프트", "mysql>", "cafe=#"),
        ("데이터베이스 고르기", "USE cafe;", "\\c cafe"),
        ("데이터베이스 목록", "SHOW DATABASES;", "\\l"),
        ("결과 끝 줄", "3 rows in set", "(3 rows)"),
        ("번호 자동으로 붙이기", "id INT AUTO_INCREMENT", "id SERIAL"),
        ("기본 포트", "3306", "5432")]
for i, (k_, a_, b_) in enumerate(diff):
    y = TY + 50 + i * 74
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:1px;background:{LINE}"></div>')
    an = bi("rise", 2) + DELAY(i * 80)
    rid = ' id="tw-auto"' if i == 4 else ""
    o.append(f'<div{rid} style="position:absolute;left:96px;top:{y + 4}px;width:1728px;height:66px"></div>')
    o.append(p(f"position:absolute;left:96px;top:{y + 16}px;width:500px;font-size:27px;font-weight:700;color:{INK};white-space:nowrap", e(k_), an))
    o.append(p(f"position:absolute;left:620px;top:{y + 16}px;width:580px;font-family:{MONO};font-size:27px;font-weight:700;color:{MY};white-space:nowrap", e(a_), an))
    o.append(p(f"position:absolute;left:1220px;top:{y + 16}px;width:600px;font-family:{MONO};font-size:27px;font-weight:700;color:{PG};white-space:nowrap", e(b_), an))
o.append(f'<div style="position:absolute;left:96px;top:{TY + 50 + 6 * 74}px;width:1728px;height:1px;background:{LINE}"></div>')
o.append(spot(3, 96, TY + 54 + 4 * 74, 1728, 66, pad=6, r=10, dim=0.5))
o.append(p(f"position:absolute;left:96px;top:{TY + 50 + 6 * 74 + 26}px;width:1728px;font-size:27px;line-height:1.6;color:{SUB}", "자동 번호는 1, 2, 3을 서버가 붙여 주는 기능이에요. 이 챕터에서는 번호를 직접 넣어요.", bi("fade", 3)))
o.append(spot_off(4))
o.append(p(f"position:absolute;left:96px;top:{TY + 50 + 6 * 74 + 74}px;width:1728px;font-size:27px;line-height:1.6;color:{SUB}", f'<span style="font-family:{MONO};font-weight:700;color:{INK}">\\c</span>, <span style="font-family:{MONO};font-weight:700;color:{INK}">\\l</span>처럼 역슬래시로 시작하는 것은 SQL이 아니라 psql 프로그램의 명령이에요.', bi("fade", 4)))
W("s-two", o, "MySQL과 PostgreSQL은 SQL이 같고, 프로그램 명령 몇 개가 달라요. 오늘 본 네 문장과 WHERE, 열 타입 INT와 VARCHAR, PRIMARY KEY는 두 서버에서 그대로 같아요. 다른 것은 아래 표예요. 프롬프트 모양이 다르고, 데이터베이스를 고르는 명령과 목록을 보는 명령이 달라요. 결과 끝 줄의 모양도 조금 달라요. 번호를 자동으로 붙이는 방법도 달라요. MySQL은 AUTO_INCREMENT, PostgreSQL은 SERIAL이라고 적어요. 이 챕터에서는 번호를 직접 넣으니 이름만 알아 두면 돼요. 서버가 기다리는 기본 포트는 3306과 5432예요. 33에서 컨테이너로 켤 때 다시 봐요. 수업에서 강사님이 두 서버를 오가도 SQL 부분은 그대로 따라가면 돼요.")

# =====================================================================
# part 3: errors
# =====================================================================
def two_stacked(scene, y0, size=26, gap=30, marks_my=None, marks_pg=None, attrs_my="", attrs_pg="", lm=None, lp=None, lh=1.5):
    lm = lm or Q(scene, "my")
    lp = lp or Q(scene, "pg")
    a = DT("my", lm, 96, y0, size=size, w=1728, lh=lh, tid=f"{scene}-my", marks=marks_my, attrs=attrs_my)
    b = DT("pg", lp, 96, a.y + a.h + gap, size=size, w=1728, lh=lh, tid=f"{scene}-pg", marks=marks_pg, attrs=attrs_pg)
    return a, b


def err_line(t):
    return [i for i, r in enumerate(t.rows) if r[0] == "e"][0]


o = frame("x-dup", EB3, "이미 있는 기본 키를 또 넣으면 서버가 막아요", C3)
t1, t2 = two_stacked("x-dup", 214, size=28)
o += [t1.html(), t2.html()]
i1, i2 = err_line(t1), err_line(t2)
o.append(underline(1, round(t1.sx(i1, "Duplicate")), round(t1.end(i1)), round(t1.top(i1) + t1.lp - 4), RED))
o.append(shake(1, "x-dup-my"))
o.append(underline(2, round(t2.sx(i2, "duplicate")), round(t2.end(i2)), round(t2.top(i2) + t2.lp - 4), RED))
o.append(underline(2, round(t2.sx(i2 + 1, "Key")), round(t2.end(i2 + 1)), round(t2.top(i2 + 1) + t2.lp - 4), RED))
yb = t2.y + t2.h + 50
o.append(p(f"position:absolute;left:96px;top:{yb}px;font-size:30px;font-weight:700;color:{INK}", "1번은 라테 주문이 이미 쓰고 있어요. 아직 안 쓴 번호로 바꿔요.", bi("fade", 3)))
o.append(code_line(96, yb + 66, f'INSERT INTO orders VALUES (<span style="background:#E4F3EA;border-radius:6px;padding:0 4px;color:{GR}"{MARK(3)}>4</span>, \'tea\', 1);', size=36, attrs=bi("fade", 3)))
html_, g = sheet(1240, t2.y + t2.h + 40, COLS, [("1", "latte", "2")], "xd-tab", [130, 300, 154], size=30, rh=62, name="orders", pk=True, attrs=bi("rise", 2))
o.append(html_)
gy = g["y"] + g["h"] + 8
o.append(f'<div id="xd-ghost"{bi("pop", 2) + DELAY(200)} style="position:absolute;left:{g["x"]}px;top:{gy}px;width:{g["w"]}px;height:{g["rh"]}px;box-sizing:border-box;border:3px dashed {RED};border-radius:12px;background:#FBEAE8;display:flex;flex-direction:row">'
         + "".join(p(f"width:{w}px;flex:none;text-align:center;font-family:{MONO};font-size:30px;font-weight:700;line-height:{g['rh'] - 6}px;color:{RED};text-decoration:line-through", e(v)) for v, w in zip(["1", "tea", "1"], [127, 300, 151])) + '</div>')
o.append(p(f"position:absolute;left:{g['x']}px;top:{gy + g['rh'] + 14}px;width:{g['w']}px;font-size:26px;font-weight:700;color:{RED}", "같은 1번이라 들어가지 않아요", bi("fade", 2) + DELAY(300)))
W("x-dup", o, "이미 있는 기본 키를 또 넣으면 서버가 막아요. 1번 행이 있는데 id가 1인 티 주문을 넣었어요. MySQL은 Duplicate entry 1, PostgreSQL은 duplicate key value라고 알려 줘요. 둘 다 기본 키가 겹쳤다는 뜻이에요. 1파트에서 본 기본 키 규칙을 서버가 지켜 준 거예요. 오류가 나면 행은 하나도 들어가지 않아요. 아직 안 쓴 번호로 바꿔서 다시 넣어요. PostgreSQL은 DETAIL 줄에 어느 열의 어느 값이 겹쳤는지까지 보여 줘요." + REAL, ("p3", "자주 나는 오류"))

o = frame("x-type", EB3, "열 타입에 맞지 않는 값도 막아요", C3)
lab_y = 214
o.append(p(f"position:absolute;left:96px;top:{lab_y}px;font-size:26px;font-weight:700;color:{RED}", "INT 열 qty에 글자 'many'"))
t1, t2 = two_stacked("x-type", lab_y + 46, size=20, gap=14, lh=1.4)
o += [t1.html(), t2.html()]
i1, i2 = err_line(t1), err_line(t2)
o.append(underline(1, round(t1.sx(i1, "Incorrect")), round(t1.end(i1)), round(t1.top(i1) + t1.lp - 3), RED))
o.append(underline(1, round(t2.sx(i2, "invalid")), round(t2.end(i2)), round(t2.top(i2) + t2.lp - 3), RED))
y2 = t2.y + t2.h + 26
o.append(p(f"position:absolute;left:96px;top:{y2}px;font-size:26px;font-weight:700;color:{RED}", "VARCHAR(20) 열 menu에 25자", bi("fade", 2)))
t3, t4 = two_stacked("x-long", y2 + 46, size=20, gap=14, lh=1.4, attrs_my=bi("rise", 2), attrs_pg=bi("rise", 2))
o += [t3.html(), t4.html()]
i3, i4 = err_line(t3), err_line(t4)
o.append(underline(3, round(t3.sx(i3, "Data")), round(t3.end(i3)), round(t3.top(i3) + t3.lp - 3), RED))
o.append(underline(3, round(t4.sx(i4, "value")), round(t4.end(i4)), round(t4.top(i4) + t4.lp - 3), RED))
W("x-type", o, "열 타입에 맞지 않는 값도 막아요. 위는 정수만 받는 qty 열에 many라는 글자를 넣은 경우예요. MySQL은 Incorrect integer value, PostgreSQL은 invalid input syntax for type integer라고 해요. 둘 다 정수가 아니라는 뜻이에요. PostgreSQL은 LINE 줄 아래 꺾쇠로 문제가 된 자리를 짚어 줘요. 아래는 20자까지만 받는 menu 열에 25자짜리 메뉴 이름을 넣은 경우예요. Data too long, value too long 모두 너무 길다는 뜻이에요. 값을 고치거나, 표를 만들 때 VARCHAR의 숫자를 넉넉히 정해요. 파이썬 리스트였다면 아무 말 없이 들어갔을 값이에요." + REAL)

o = frame("x-semi", EB3, "끝에 ;를 빠뜨리면 다음 줄을 기다려요", C3)
lm, lp = Q("x-semi", "my"), Q("x-semi", "pg")
SEMI = {";": 'style="color:#7FD18B"' + MARK(2)}
t1 = DT("my", lm, 96, 214, size=30, w=844, tid="xs-my", marks={1: {"@prompt": "xs-p1", **SEMI}})
t2 = DT("pg", lp, 980, 214, size=30, w=844, tid="xs-pg", marks={1: {"@prompt": "xs-p2", **SEMI}})
same_h(t1, t2)
o += [t1.html(), t2.html()]
o.append(pen_box(1, round(t1.tx + t1.sw("    ") - 10), round(t1.top(1)) + 2, round(t1.sw("->")) + 20, round(t1.lp) - 4, OR))
o.append(pen_box(1, round(t2.tx - 10), round(t2.top(1)) + 2, round(t2.sw("cafe-#")) + 20, round(t2.lp) - 4, OR))
yb = max(t1.y + t1.h, t2.y + t2.h) + 44
o.append(p(f"position:absolute;left:96px;top:{yb}px;width:1728px;font-size:30px;font-weight:700;line-height:1.6;color:{INK}", f'<span style="font-family:{MONO};color:{OR}">-></span>나 <span style="font-family:{MONO};color:{OR}">cafe-#</span>가 보이면 서버가 문장 끝을 기다리는 중이에요. <span style="font-family:{MONO};color:{GR}">;</span>만 치고 Enter를 눌러요.', bi("fade", 2)))
o.append(p(f"position:absolute;left:96px;top:{yb + 70}px;width:1728px;font-size:27px;line-height:1.6;color:{SUB}", "앞에서 친 줄과 합쳐서 한 문장으로 실행해요. CREATE TABLE을 줄 나눠 친 것도 같은 원리예요.", bi("fade", 3)))
W("x-semi", o, "끝에 세미콜론을 빠뜨리면 다음 줄을 기다려요. SELECT 문장을 세미콜론 없이 치고 Enter를 눌렀어요. 오류가 나지 않고 프롬프트만 바뀌어요. MySQL은 화살표, PostgreSQL은 cafe 빼기 샵이에요. 서버가 문장이 아직 안 끝났다고 보고 다음 줄을 기다리는 거예요. 처음엔 멈춘 것처럼 보여서 당황하기 쉬워요. 세미콜론만 치고 Enter를 누르면 앞에서 친 줄과 합쳐서 실행해요. 2파트에서 CREATE TABLE을 여러 줄로 나눠 친 것도 같은 원리예요." + REAL)

o = frame("x-quote", EB3, "글자 값에 작은따옴표를 빠뜨리면 열 이름으로 읽어요", C3)
lm, lp = Q("x-quote", "my"), Q("x-quote", "pg")
t1 = DT("my", lm, 96, 214, size=30, w=1728, tid="xq-my")
t2 = DT("pg", lp, 96, t1.y + t1.h + 30, size=30, w=1728, tid="xq-pg")
o += [t1.html(), t2.html()]
i1, i2 = err_line(t1), err_line(t2)
o.append(underline(1, round(t1.sx(i1, "Unknown")), round(t1.end(i1)), round(t1.top(i1) + t1.lp - 3), RED))
o.append(underline(1, round(t2.sx(i2, "column")), round(t2.end(i2)), round(t2.top(i2) + t2.lp - 3), RED))
o.append(pen_box(1, round(t1.sx(0, "latte")) - 8, round(t1.top(0)) + 2, round(t1.sw("latte")) + 16, round(t1.lp) - 4, RED))
o.append(pen_box(1, round(t2.sx(0, "latte")) - 8, round(t2.top(0)) + 2, round(t2.sw("latte")) + 16, round(t2.lp) - 4, RED))
yb = t2.y + t2.h + 44
o.append(p(f"position:absolute;left:96px;top:{yb}px;font-size:28px;font-weight:700;color:{GRAY}", "고친 문장", bi("fade", 2)))
q_ = f'<span style="background:#E4F3EA;border-radius:6px;padding:0 2px;color:{GR}"{MARK(2)}>\'</span>'
o.append(code_line(96, yb + 54, f"INSERT INTO orders VALUES (4, {q_}latte{q_}, 1);", size=48, attrs=bi("fade", 2)))
o.append(p(f"position:absolute;left:96px;top:{yb + 150}px;width:1728px;font-size:28px;line-height:1.6;color:{SUB}", "따옴표가 없으면 latte를 열 이름으로 읽고, 그런 열이 없다고 해요. 숫자 값은 따옴표 없이 적어요.", bi("fade", 3)))
W("x-quote", o, "글자 값에 작은따옴표를 빠뜨리면 열 이름으로 읽어요. latte를 따옴표 없이 적었어요. 서버는 따옴표 없는 낱말을 열 이름으로 읽어서, latte라는 열을 찾다가 없다고 알려 줘요. MySQL은 Unknown column, PostgreSQL은 column does not exist예요. 글자 값의 앞뒤에 작은따옴표를 붙이면 돼요. 파이썬처럼 큰따옴표를 쓰면 MySQL은 받아 주지만 PostgreSQL은 열 이름으로 읽어요. 두 서버에서 다 되도록 작은따옴표로 적어요. 숫자 값 4와 1은 따옴표 없이 적어요." + REAL)

o = frame("x-nodb", EB3, "데이터베이스를 고르지 않으면 표를 못 찾아요", C3)
lm, lp = Q("x-nodb", "my"), Q("x-nodb", "pg")
t1 = DT("my", lm, 96, 214, size=30, w=1728, tid="xn-my")
t2 = DT("pg", lp, 96, t1.y + t1.h + 30, size=30, w=1728, tid="xn-pg", marks={0: {"@prompt": "xn-p"}})
o += [t1.html(), t2.html()]
i1, i2 = err_line(t1), err_line(t2)
o.append(underline(1, round(t1.sx(i1, "No")), round(t1.end(i1)), round(t1.top(i1) + t1.lp - 3), RED))
o.append(underline(1, round(t2.sx(i2, "relation")), round(t2.end(i2)), round(t2.top(i2) + t2.lp - 3), RED))
o.append(pen_box(2, round(t2.tx) - 10, round(t2.top(0)) + 2, round(t2.sw("postgres=#")) + 20, round(t2.lp) - 4, OR))
o += tag(t2, 0, "지금 postgres 안이에요", OR, 2, at=t2.x + 760, gap=26)
yb = t2.y + t2.h + 44
o.append(p(f"position:absolute;left:96px;top:{yb}px;font-size:28px;font-weight:700;color:{GRAY}", "먼저 들어갈 데이터베이스를 골라요", bi("fade", 3)))
o.append(code_line(96, yb + 56, f'<span style="color:{MY}">USE cafe;</span>', size=48, attrs=bi("rise", 3)))
o.append(code_line(980, yb + 56, f'<span style="color:{PG}">\\c cafe</span>', size=48, attrs=bi("rise", 3)))
o.append(p(f"position:absolute;left:96px;top:{yb + 156}px;width:1728px;font-size:28px;line-height:1.6;color:{SUB}", "표는 데이터베이스 안에 있어서, 어느 데이터베이스인지부터 정해야 해요.", bi("fade", 3)))
W("x-nodb", o, "데이터베이스를 고르지 않으면 표를 못 찾아요. 서버에 막 들어온 상태에서 바로 SELECT를 쳤어요. MySQL은 No database selected, 고른 데이터베이스가 없다고 해요. PostgreSQL은 처음 들어가면 postgres 데이터베이스 안에 있어서, 거기서 orders를 찾다가 없다고 해요. 프롬프트가 postgres=#인 걸 보면 알 수 있어요. 1파트에서 본 것처럼 표는 데이터베이스 안에 있어요. 먼저 USE cafe; 나 역슬래시 c cafe로 들어간 다음 SELECT를 쳐요." + REAL)

# =====================================================================
# part 4: real tasks
# =====================================================================
o = frame("r-day", EB4, "예제 1 · 오늘 들어온 주문을 넣고, 라테 주문만 골라 봐요", C4)
slips = [("4", "latte", "1잔"), ("5", "tea", "2잔")]
for k, (n_, m_, q_) in enumerate(slips):
    y = 230 + k * 210
    o.append(f'<div id="rd-s{k}" style="position:absolute;left:96px;top:{y}px;width:520px;height:180px;box-sizing:border-box;background:#FFFDF6;border:2px solid #E4DCC8;border-radius:14px;box-shadow:{SHADOW};padding:26px 32px">'
             + p(f"font-size:24px;font-weight:700;color:{GRAY}", f"주문서 · 진동벨 {n_}번")
             + p(f"margin-top:14px;font-family:{MONO};font-size:40px;font-weight:700;color:{INK};white-space:nowrap", f'{e(m_)} <span style="font-family:{SANS};font-size:32px;color:{SUB}">{q_}</span>') + '</div>')
lm = Q("r-day", "my")
t1 = DT("my", lm, 680, 214, size=22, w=1144, lh=1.5, tid="rd-my")
sel_i = [i for i, l in enumerate(lm) if l.startswith("mysql> SELECT")][0]
t1.band(0, 2, order=1, color="rgba(127,209,139,.14)")
t1.band(sel_i + 4, sel_i + 5, order=2, color="rgba(227,168,74,.2)")
o.append(t1.html())
o += tag(t1, 1, "주문서 두 장이 두 행으로", GR, 1, at=t1.x + 560, gap=26)
o += tag(t1, sel_i + 4, "1번과 오늘 넣은 4번", OR, 2, at=t1.x + 400, gap=26)
lp = Q("r-day", "pg", 1)
t2 = DT("pg", lp, 680, t1.y + t1.h + 24, size=19, w=1144, lh=1.45, tid="rd-pg", attrs=bi("rise", 3))
o.append(t2.html())
o += tag(t2, 0, "같은 문장, 같은 두 행", PG, 3, at=t2.x + 700, gap=26)
allrows = [("1", "latte", "2"), ("2", "americano", "1"), ("3", "cake", "1"), ("4", "latte", "1"), ("5", "tea", "2")]
lat = {(i, j): f' style="color:{OR};font-weight:700"' + MARK(2) for i in (0, 3) for j in range(3)}
html_, g = sheet(96, 660, COLS, allrows, "rd-tab", [110, 250, 160], size=22, rh=46, name="orders 지금 모습", pk=True, cell_attrs=lat)
o.append(html_)
W("r-day", o, "오늘 들어온 주문서 두 장을 표에 넣고, 라테 주문만 골라 봐요. 진동벨 번호를 id로 쓰면 기본 키가 겹치지 않아요. INSERT 한 문장에 괄호 묶음 두 개를 이어 적어서 4번, 5번 주문을 한 번에 넣었어요. 그다음 WHERE menu = latte로 메뉴가 라테인 행만 골랐어요. 글자 값이라 작은따옴표로 감쌌어요. 아침에 넣은 1번과 지금 넣은 4번이 나와요. 왼쪽 아래는 PostgreSQL에 같은 두 문장을 보낸 결과에서 SELECT 부분만 옮긴 거예요. 결과가 같아요." + REAL, ("p4", "실제 상황 예제"))

o = frame("r-menu", EB4, "예제 2 · 메뉴판을 보고 menu 표를 설계해요", C4)
o.append(f'<div id="rm-board" style="position:absolute;left:96px;top:214px;width:480px;height:330px;box-sizing:border-box;background:#2B3A33;border:10px solid #7A5A3A;border-radius:16px;padding:28px 36px;display:flex;flex-direction:column;gap:18px">'
         + p("font-size:30px;font-weight:700;color:#F6F5F1", "KANT 카페 메뉴")
         + "".join(f'<div style="display:flex;flex-direction:row;justify-content:space-between;gap:20px">' + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:#F6F5F1", n_) + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:#F2C46D", pr_) + '</div>'
                   for n_, pr_ in [("americano", "4000"), ("latte", "4500"), ("cake", "5500")]) + '</div>')
o.append(line_arrow(596, 380, 676, 380, C4, 1))
html_, g = sheet(700, 214, ["id", "name", "price"], [("1", "americano", "4000"), ("2", "latte", "4500"), ("3", "cake", "5500")], "rm-tab", [120, 280, 170], size=28, rh=58, types=["INT", "VARCHAR(20)", "INT"], name="menu", pk=True, attrs=bi("rise", 1))
o.append(html_)
notes = [("id", "새로 붙인 번호, 기본 키", VO), ("name", "글자라서 VARCHAR(20)", MAG), ("price", "원 단위 정수라서 INT", TEAL)]
o.append(f'<div{STAGGER(1, 90)} style="position:absolute;left:{g["x"] + g["w"] + 50}px;top:{g["y"] + 6}px;width:{1824 - g["x"] - g["w"] - 50}px;display:flex;flex-direction:column;gap:22px">'
         + "".join(f'<div style="display:flex;flex-direction:column;gap:2px">' + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{c}", e(a_)) + p(f"font-size:24px;line-height:1.4;color:{SUB};white-space:nowrap", e(b_)) + '</div>' for a_, b_, c in notes) + '</div>')
lp = Q("r-menu", "pg")
t2 = DT("pg", lp, 96, 600, size=21, w=1728, lh=1.45, tid="rm-pg", attrs=bi("rise", 2))
sel_i = [i for i, l in enumerate(lp) if l.startswith("cafe=# SELECT")][0]
t2.band(sel_i, len(lp) - 1, order=3, color="rgba(227,168,74,.2)")
o.append(t2.html())
o += tag(t2, sel_i, "5000원보다 싼 메뉴만", OR, 3, at=t2.x + 800, gap=26)
W("r-menu", o, "메뉴판을 보고 menu 표를 설계해요. 표를 만들기 전에 열 세 가지를 정해요. 메뉴마다 겹치지 않는 번호를 새로 붙여서 id로 두고 기본 키로 정해요. 메뉴 이름은 글자라서 VARCHAR(20), 가격은 원 단위 정수라서 INT예요. 설계가 끝나면 CREATE TABLE, INSERT, SELECT 세 문장을 보내요. 이번에는 PostgreSQL 화면이에요. WHERE price < 5000으로 5000원보다 싼 메뉴만 골랐어요. 숫자 비교라서 따옴표가 없어요. 같은 세 문장을 MySQL에 보내도 같은 두 행이 나와요. 1파트에서 본 것처럼 주문 표에 메뉴 번호만 적고 가격은 이 표에서 찾는 방법은 다음에 배워요." + REAL)

# =====================================================================
# wrap-up
# =====================================================================
o = frame("trouble", "정리", "막히면 이렇게 풀어요", RED)
tr = [("Duplicate entry '1'", "duplicate key value", "기본 키가 겹쳐요", "안 쓴 번호로 바꾸기"),
      ("Incorrect integer value", "invalid input syntax for type integer", "INT 열에 글자를 넣었어요", "숫자로 고치기"),
      ("Data too long", "value too long", "VARCHAR(20)보다 길어요", "줄이거나 숫자를 넉넉히"),
      ("Unknown column 'latte'", "column \"latte\" does not exist", "글자 값에 따옴표가 없어요", "'latte'처럼 감싸기"),
      ("No database selected", "relation \"orders\" does not exist", "데이터베이스를 안 골랐어요", "USE cafe; 또는 \\c cafe"),
      ("    ->", "cafe-#", "문장 끝 ;가 없어요", "; 치고 Enter")]
o.append(p(f"position:absolute;left:96px;top:214px;font-size:24px;font-weight:700;color:{MY}", MYV))
o.append(p(f"position:absolute;left:96px;top:214px;width:1100px;text-align:right;font-size:24px;font-weight:700;color:{PG}", PGV))
o.append(p(f"position:absolute;left:1240px;top:214px;font-size:24px;font-weight:700;color:{GRAY}", "까닭과 해결"))
for i, (a_, b_, c_, d_) in enumerate(tr):
    y = 262 + i * 118
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:1px;background:{LINE}"></div>')
    ra_ = bi("rise", 1) + DELAY(i * 80)
    o.append(p(f"position:absolute;left:96px;top:{y + 18}px;width:1100px;font-family:{MONO};font-size:24px;font-weight:700;color:{MY};white-space:pre", e(a_), ra_))
    o.append(p(f"position:absolute;left:96px;top:{y + 64}px;width:1100px;text-align:right;font-family:{MONO};font-size:24px;font-weight:700;color:{PG};white-space:pre", e(b_), ra_))
    o.append(p(f"position:absolute;left:1240px;top:{y + 18}px;width:584px;font-size:25px;color:{SUB};white-space:nowrap", e(c_), ra_))
    o.append(p(f"position:absolute;left:1240px;top:{y + 62}px;width:584px;font-size:26px;font-weight:700;color:{INK};white-space:nowrap", e(d_), ra_))
o.append(f'<div style="position:absolute;left:96px;top:{262 + 6 * 118}px;width:1728px;height:1px;background:{LINE}"></div>')
W("trouble", o, "오늘 본 오류를 모았어요. 왼쪽 위가 MySQL, 오른쪽 아래가 PostgreSQL의 문구예요. 문구는 달라도 까닭과 해결은 같아요. 겹친 기본 키, 타입에 안 맞는 값, 너무 긴 글자는 서버가 표의 규칙을 지켜 준 거예요. 따옴표가 없거나 데이터베이스를 안 고른 것은 문장을 고쳐서 다시 보내요. 프롬프트가 화살표나 cafe 빼기 샵이면 오류가 아니라 세미콜론을 기다리는 중이에요.", ("trouble", "정리"))

o = frame("cheatsheet", "정리", "한 장 요약", INK)
groups = [("낱말", C1, [("표 (테이블)", "엑셀 시트 한 장"), ("행 (row)", "주문 하나"), ("열 (column)", "항목 하나, 타입이 있어요"), ("기본 키", "행마다 다른 번호")]),
          ("SQL 네 문장", C2, [("CREATE DATABASE cafe;", "데이터베이스 만들기"), ("CREATE TABLE orders (…);", "열 이름과 타입 정하기"), ("INSERT INTO orders VALUES (…);", "행 넣기"), ("SELECT * FROM orders;", "꺼내기, WHERE로 고르기")]),
          ("두 서버의 차이", OR, [("USE cafe;  \\c cafe", "데이터베이스 고르기"), ("mysql>  cafe=#", "프롬프트"), ("AUTO_INCREMENT  SERIAL", "자동 번호"), ("3306  5432", "기본 포트")])]
for i, (t_, c, rows_) in enumerate(groups):
    x = 96 + i * 594
    o.append(p(f"position:absolute;left:{x}px;top:220px;font-size:30px;font-weight:700;color:{c}", e(t_)))
    o.append(f'<div style="position:absolute;left:{x}px;top:270px;width:540px;height:3px;background:{c}"></div>')
    for j, (k, d_) in enumerate(rows_):
        y = 296 + j * 120
        mono = i > 0
        o.append(p(f"position:absolute;left:{x}px;top:{y}px;width:560px;{'font-family:' + MONO + ';font-size:23px;' if mono else 'font-size:27px;'}font-weight:700;color:{INK};white-space:pre", e(k)))
        o.append(p(f"position:absolute;left:{x}px;top:{y + 42}px;width:540px;font-size:23px;color:{SUB}", e(d_)))
o.append(caption("MySQL과 PostgreSQL은 같은 SQL을 알아들어요. 다른 건 프로그램 명령 몇 개예요.", 820, None, size=32))
o.append(caption("33에서 Docker로 두 서버를 직접 켜고, 오늘 읽은 문장을 쳐 봐요.", 880, None, size=28, color=SUB))
W("cheatsheet", o, "오늘 쓴 것을 세 묶음으로 모았어요. 데이터베이스는 표에 데이터를 담아요. 행은 주문 하나, 열은 항목 하나이고, 열마다 타입이 있어요. 기본 키는 행마다 다른 번호예요. SQL 네 문장으로 데이터베이스와 표를 만들고, 행을 넣고 꺼내요. MySQL과 PostgreSQL은 이 SQL이 같고, 데이터베이스를 고르는 명령과 프롬프트, 자동 번호, 기본 포트가 달라요. 다음 33에서는 Docker로 두 서버를 직접 켜고 오늘 읽은 문장을 쳐 봐요.")

# =====================================================================
# toc
# =====================================================================
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
plist = [(C1, "데이터베이스와 표", "데이터베이스와 DBMS, 관계형, 행과 열, 타입, 기본 키, 서버 안의 구조", "f-what", "f-tree"),
         (C2, "SQL 네 문장 맛보기", "CREATE DATABASE, CREATE TABLE, INSERT, SELECT와 WHERE, 파이썬과 비교, 두 서버 비교", "s-intro", "s-two"),
         (C3, "자주 나는 오류", "겹친 기본 키, 타입과 길이, 빠진 ;, 빠진 따옴표, 고르지 않은 데이터베이스", "x-dup", "x-nodb"),
         (C4, "실제 상황 예제", "오늘 주문 넣고 고르기, 메뉴판으로 표 설계하기", "r-day", "r-menu")]
o = frame("toc", "", "오늘의 순서", INK)
for i, (c, h, s_, a, b) in enumerate(plist):
    y = 230 + i * 160
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:1px;background:{LINE}"></div>')
    o.append(p(f"position:absolute;left:96px;top:{y + 30}px;width:80px;font-size:56px;font-weight:900;line-height:1.5;color:{c}", str(i + 1)))
    o.append(p(f"position:absolute;left:200px;top:{y + 30}px;font-size:40px;font-weight:700;color:{INK}", h))
    o.append(p(f"position:absolute;left:200px;top:{y + 92}px;font-size:24px;color:{SUB}", e(s_)))
    o.append(p(f"position:absolute;left:1524px;top:{y + 54}px;width:300px;text-align:right;font-size:30px;font-weight:700;color:{GRAY}", f"{page[a]}–{page[b]}쪽"))
o.append(f'<div style="position:absolute;left:96px;top:{230 + 4 * 160}px;width:1728px;height:1px;background:{LINE}"></div>')
o.append(p(f"position:absolute;left:96px;top:944px;font-size:26px;color:{SUB}", f"{page['why']}–{page['smallest']}쪽은 들어가기, {page['trouble']}–{page['cheatsheet']}쪽은 막힐 때와 한 장 요약이에요."))
o = [x for x in o if 'id="eyebrow"' not in x]
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(o) + f"\n<aside>{e('네 파트로 나눴어요. 1파트에서 데이터베이스와 표에 쓰는 낱말을 익혀요. 2파트에서 SQL 네 문장으로 표를 만들고 넣고 꺼내는 화면을 MySQL과 PostgreSQL에서 나란히 읽어요. 3파트에서 자주 나는 오류를 모아 보고, 4파트에서 앞의 것을 섞은 카페 예제 두 개를 풀어요.')}</aside>\n</section>\n")

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-12T00:00:00Z"}, "lists": "css", "title": "데이터베이스 기초 (표, 타입, 기본 키, SQL 맛보기)", "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
for w_ in WARN:
    print("WARN", w_)
print(len(ORDER), "slides")
