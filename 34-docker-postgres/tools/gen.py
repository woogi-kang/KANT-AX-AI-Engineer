r"""Generates every slide of the PostgreSQL deck (34) and slides/deck.json.

Story: 33 ran MySQL in a container. Class material and companies also use PostgreSQL, and the MySQL commands do not
carry over as they are (docker exec ... mysql fails in a postgres container). Part 1 runs postgres:18 (-e
POSTGRES_PASSWORD, logs, env). Part 2 enters with psql (-U, -d, backslash commands, no password inside the
container, the password from outside). Part 3 is SQL in the same order as 33: CREATE DATABASE, \c, \l, CREATE TABLE,
\dt, \d, INSERT, SELECT, DROP. Part 4 is accounts (postgres, POSTGRES_USER is a superuser, CREATE USER for a plain
one). Part 5 shows the data vanish with the container, keeps it in a volume on /var/lib/postgresql (the 18+ place) and
moves the run into compose.yaml. Part 6 errors, part 7 two real tasks, then the MySQL comparison.
Analogy kept from 29/30: image = 붕어빵 틀, container = 붕어빵, volume = 붕어빵 밖 보관함.

Every terminal line comes from tools/demo.py (real Docker 29.9.2 and postgres:18 = PostgreSQL 18.6, in tools/out.json).
Usage (in 34-docker-postgres): python3 tools/gen.py slides
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
sys.path.insert(0, HERE)
from files import COMPOSE, COMPOSE_INIT, MENU_SQL  # noqa: E402  (the files demo.py wrote)

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
P_HOME, P_CAFE = "~", "~/cafe-pg"
ORD = [("1", "latte", "2"), ("2", "americano", "1")]
COLS = ["id", "menu", "qty"]
TYPES = ["INT", "VARCHAR(20)", "INT"]
PROMPT_RE = re.compile(r"^([a-z0-9_]+)(=#|-#|=>|->|\(#) (.*)$")
ROOT_RE = re.compile(r"^(root@[0-9a-f]+:/)# ?(.*)$")
ERR_RE = re.compile(r"^(ERROR|psql: error|FATAL|Error|docker: Error|OCI runtime|connection to server|DETAIL|HINT)")


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
        elif err and ERR_RE.match(l.strip()):
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


EB1, EB2, EB3, EB4, EB5, EB6 = "1. PostgreSQL 컨테이너 켜기", "2. 데이터베이스와 표 만들기", "3. 계정과 접속 방법", "4. 볼륨과 compose", "5. 자주 나는 오류", "6. 실제 상황 예제"
C1, C2, C3, C4, C5, C6 = PG, GR, US, VO, RED, OR
RUN = C("run")
RUNV = C("v-run")

# =====================================================================
# cover
# =====================================================================
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px">',
       p("position:absolute;left:128px;top:300px;font-size:28px;font-weight:700;color:#9DC1E6", "KANT AX/AI 엔지니어 트랙 · 34"),
       f'<h1{SLAM(1)} style="position:absolute;left:128px;top:350px;padding-bottom:14px;font-size:100px;font-weight:900;line-height:1.3;color:#F6F5F1">Docker 4</h1>',
       p("position:absolute;left:128px;top:500px;font-size:52px;font-weight:700;line-height:1.3;color:#F6F5F1", "PostgreSQL 컨테이너로<br>데이터베이스 쓰기"),
       p("position:absolute;left:128px;top:680px;font-size:32px;line-height:1.5;color:#BFC6D4", "33의 MySQL과 같은 일을 PostgreSQL로 해요")]
kept = S("v-kept")
kept = [l for l in kept if not l.startswith("shop=# \\q")]
while kept and not kept[-1].strip():
    kept.pop()
t = Term(psql_rows(kept), 1060, 330, size=30, w=760, tid="cov-term", lh=1.45)
cov.append(t.html())
cov.append(shine(2, "cov-term"))
W("cover", cov, "34 챕터는 Docker 4, PostgreSQL 컨테이너로 데이터베이스 쓰기예요. 33에서는 MySQL을 컨테이너로 켜서 주문을 표에 담았어요. 수업 자료나 회사에 따라 PostgreSQL을 쓰는 곳도 많아요. 오늘은 같은 순서로 PostgreSQL을 켜고, 데이터베이스와 표를 만들고, 컨테이너를 지워도 주문이 남게 해요. 오른쪽은 컨테이너를 지웠다 다시 켠 뒤에도 주문 두 개가 그대로 나온 화면이에요. 마지막에는 MySQL과 다른 점을 표 한 장으로 모아요." + REAL, ("intro", "들어가기"))

ORDER.append("toc")   # written last, after page numbers are known

# =====================================================================
# why
# =====================================================================
o = frame("why", "들어가기", "MySQL 명령을 그대로 치면 PostgreSQL에서는 안 돼요", INK)
why = RA("why")
t = Term([("$", P_HOME, RUN), ("o", idshort("run"), {}), ("o", ""), ("$", P_HOME, C("why"), {"mysql -u root -p": 'id="why-my"'})] + [("e", l) for l in why],
         96, 214, size=22, w=1728, tid="t-why", lh=1.6)
o.append(t.html())
o.append(shake(1, "t-why"))
o.append(pen_box(1, round(t.sx(3, "mysql") - 8), round(t.top(3) - 2), round(t.sw("mysql -u root -p") + 16), round(t.lp + 4), RED))
ey = t.y + t.h + 56
o.append(p(f"position:absolute;left:96px;top:{ey}px;font-size:28px;font-weight:700;color:{GRAY}", "같은 일, 다른 이름", bi("fade", 2)))
rows = [("이미지", "mysql:8.4", "postgres:18"), ("들어가는 프로그램", "mysql -u root -p", "psql -U postgres"), ("포트", "3306", "5432")]
o.append(p(f"position:absolute;left:560px;top:{ey}px;font-size:28px;font-weight:700;color:{MY}", "33 MySQL", bi("fade", 2)))
o.append(p(f"position:absolute;left:1180px;top:{ey}px;font-size:28px;font-weight:700;color:{PG}", "34 PostgreSQL", bi("fade", 2)))
for i, (a_, b_, c_) in enumerate(rows):
    y = ey + 60 + i * 74
    ra = bi("rise", 2) + DELAY(i * 90)
    o.append(f'<div{bi("fade", 2)} style="position:absolute;left:96px;top:{y}px;width:1728px;height:1px;background:{LINE}"></div>')
    o.append(p(f"position:absolute;left:96px;top:{y + 16}px;font-size:28px;color:{SUB};white-space:nowrap", e(a_), ra))
    o.append(p(f"position:absolute;left:560px;top:{y + 14}px;font-family:{MONO};font-size:30px;font-weight:700;color:{MY};white-space:nowrap", e(b_), ra))
    o.append(p(f"position:absolute;left:1180px;top:{y + 14}px;font-family:{MONO};font-size:30px;font-weight:700;color:{PG};white-space:nowrap", e(c_), ra))
o.append(caption("켜고, 표를 만들고, 볼륨으로 남기는 순서는 33과 같아요. 이름과 명령만 바꿔 익혀요.", ey + 60 + 3 * 74 + 50, 3, size=30))
W("why", o, "MySQL 명령을 그대로 치면 PostgreSQL에서는 안 돼요. 33에서 배운 대로 컨테이너를 켜고 들어가려고 mysql -u root -p를 쳤어요. 그런데 이 컨테이너는 postgres:18 이미지로 켰어요. 안에 mysql이라는 프로그램이 없어서 executable file not found, 실행 파일을 찾을 수 없다는 오류가 나요. 수업이나 자료에서 MySQL로 보여 주다가 PostgreSQL로 넘어가면 이런 데서 막혀요. 아래 표처럼 이미지, 들어가는 프로그램, 포트가 달라요. 켜고, 표를 만들고, 볼륨으로 남기는 순서는 33과 똑같아요. 오늘은 그 순서대로 PostgreSQL에서 쓰는 이름과 명령을 익혀요." + REAL)

# =====================================================================
# big picture
# =====================================================================
o = frame("big", "들어가기", "pg 컨테이너 안에서 PostgreSQL 서버가 5432번으로 기다려요", INK)
o.append(node(96, 300, 360, 170, "내 터미널", "docker exec -it pg psql", BW, BWBG, "bg-me", icon="Code", mono_sub=True, ssize=20))
o.append(node(96, 620, 360, 170, "밖의 프로그램", "5432번 포트로", GRAY, "#EEF0F3", "bg-app", icon="Link", attrs=bi("rise", 3)))
# container
o.append(f'<div id="bg-box" style="position:absolute;left:620px;top:224px;width:780px;height:640px;border:3px dashed {DK};border-radius:24px;background:#F1F5FD"></div>')
o.append(p(f"position:absolute;left:652px;top:244px;font-family:{MONO};font-size:26px;font-weight:700;color:{DK}", "컨테이너 pg · postgres:18"))
o.append(f'<div id="bg-srv" style="position:absolute;left:660px;top:304px;width:700px;height:520px;background:{CARD};border:3px solid {PG};border-radius:20px"></div>')
o.append(p(f"position:absolute;left:692px;top:324px;font-size:30px;font-weight:700;color:{PG}", "PostgreSQL 서버 · 5432"))
o.append(p(f"position:absolute;left:692px;top:372px;font-size:22px;color:{SUB}", "데이터베이스가 여러 개, 그 안에 표가 여러 개"))
dbs = [("postgres", "처음부터 있어요", None), ("shop", "오늘 만들어요", ["orders"])]
for k, (n_, s_, tbls) in enumerate(dbs):
    x = 692 + k * 336
    o.append(cyl(x, 430, 300, 230, n_, s_, PG, PGBG, f"bg-db{k}", attrs=bi("rise", 1) + DELAY(k * 120)))
    if tbls:
        o.append(p(f"position:absolute;left:{x + 70}px;top:670px;height:44px;padding:0 18px;border-radius:10px;background:{GR};font-family:{MONO};font-size:24px;font-weight:700;line-height:44px;color:#FFFFFF", "표 orders", bi("pop", 1) + DELAY(300)))
o.append(p(f"position:absolute;left:692px;top:744px;height:48px;padding:0 18px;border-radius:24px;background:{USBG};border:2px solid {US};font-size:24px;font-weight:700;line-height:44px;color:{US};white-space:nowrap", "관리자 계정 postgres · 비밀번호 cafe1234", bi("pop", 2)))
o.append(cyl(1520, 400, 300, 280, "pg-data", "볼륨 · 붕어빵 밖 보관함", VO, VOBG, "bg-vol", attrs=bi("rise", 4)))
o.append(p(f"position:absolute;left:1520px;top:700px;width:300px;text-align:center;font-family:{MONO};font-size:22px;font-weight:700;color:{VO}", "/var/lib/postgresql", bi("rise", 4)))
o.append(line_arrow(470, 385, 650, 450, BW, None, pid="bg-p1"))
o.append(dot(650, 450, BW, 1, "bg-p1"))
o.append(line_arrow(470, 705, 650, 640, GRAY, 3, dash="10 10"))
o.append(line_arrow(1410, 545, 1505, 545, VO, 4))
W("big", o, "오늘 만들 모습을 한 장에 그렸어요. 파란 점선 상자가 postgres:18 이미지로 켠 컨테이너 pg예요. 그 안에서 PostgreSQL 서버가 5432번 포트를 열고 기다려요. 서버 안에는 데이터베이스가 여러 개 들어가요. postgres는 처음부터 있는 데이터베이스이고, 오늘 shop을 만들어서 그 안에 주문 표 orders를 둬요. 들어갈 때는 관리자 계정 postgres를 써요. 비밀번호는 컨테이너를 켤 때 정해요. 내 터미널에서는 docker exec로 컨테이너 안의 psql을 열어요. 다른 프로그램은 5432번 포트로 붙는데, 이건 3파트에서 봐요. 데이터가 실제로 저장되는 /var/lib/postgresql 폴더는 4파트에서 볼륨 pg-data에 연결해요.")

# =====================================================================
# part 1: run PostgreSQL
# =====================================================================
o = frame("r-pull", EB1, "Docker Hub의 공식 이미지 postgres:18을 받아요", C1)
pl = RA("pull")
rows = [("$", P_HOME, C("pull"))] + [("o", l) for l in pl] + [("o", ""), ("$", P_HOME, C("images"))] + [("o", l.rstrip()) for l in RA("images")]
t = Term(rows, 96, 214, size=20, w=1100, lh=1.4, tid="t-pull")
o.append(t.html())
st = next(i for i, r in enumerate(rows) if r[0] == "o" and r[1].startswith("Status:"))
o += tag(t, st, "다 받았어요", GR, 1)
im = len(rows) - 1
o.append(underline(2, t.sx(im, "650MB"), t.sx(im, "650MB") + t.sw("650MB"), t.top(im) + t.lp - 2, OR))
# Docker Hub card
card = (f'<div id="hub" style="position:absolute;left:1260px;top:214px;width:564px;height:350px;background:{CARD};border:1px solid #D2CEC4;border-radius:16px;box-shadow:{SHADOW};padding:30px 34px;display:flex;flex-direction:column;gap:18px">'
        + '<div style="display:flex;flex-direction:row;align-items:center;gap:14px">'
        + f'<div style="width:56px;height:56px;flex:none;border-radius:12px;background:{PGBG};display:flex;align-items:center;justify-content:center"><x-icon name="Database" style="width:32px;height:32px;color:{PG}"></x-icon></div>'
        + p(f"font-family:{MONO};font-size:34px;font-weight:700;color:{INK}", "postgres") + '</div>'
        + p(f"align-self:flex-start;height:40px;padding:0 14px;border-radius:8px;background:#E7F0FF;font-size:22px;font-weight:700;line-height:40px;color:{DK};white-space:nowrap", "Docker Official Image")
        + p(f"font-size:24px;line-height:1.5;color:{SUB}", "PostgreSQL 팀과 Docker가 함께 관리해요")
        + p(f"font-size:22px;font-weight:700;color:{GRAY};margin-top:6px", "태그 고르기")
        + '<div style="display:flex;flex-direction:row;gap:12px">'
        + "".join(p(f"height:44px;padding:0 16px;border-radius:10px;background:{PG if k == 0 else '#EEF0F3'};font-family:{MONO};font-size:24px;font-weight:700;line-height:44px;color:{'#FFFFFF' if k == 0 else SUB};white-space:nowrap", e(tg)) for k, tg in enumerate(["18", "17", "latest"])) + '</div></div>')
o.append(card)
o.append(caption("18은 PostgreSQL 18이에요. latest는 새 버전이 나오면 바뀌니 숫자로 적어요.", 610, 3, left=1260, width=564, size=28))
o.append(caption("받은 이미지는 650MB예요. 처음 받을 때만 기다려요.", 780, 3, left=1260, width=564, size=26, color=SUB))
W("r-pull", o, "Docker Hub의 공식 이미지 postgres:18을 받아요. 29에서 배운 docker pull이에요. postgres는 Docker Official Image 마크가 붙은 공식 이미지라 이것부터 골라요. 태그 18은 PostgreSQL 18 버전이에요. latest로 받으면 새 버전이 나올 때마다 바뀌어서, 수업에서는 18로 적어 모두 같은 버전을 써요. 4파트에서 보겠지만 18은 데이터 폴더 자리가 17까지와 달라서, 버전을 꼭 적는 게 좋아요. docker images postgres로 받은 이미지를 확인해요. 650MB라 처음에는 조금 걸려요." + REAL, ("p1", "PostgreSQL 컨테이너 켜기"))

o = frame("r-run", EB1, "docker run 한 줄로 PostgreSQL 서버를 켜요", C1)
segs = [("docker run", INK, None, None), ("-d", BL, "뒤에서 켜기", None), ("--name pg", BL, "이름 pg", None),
        ("-e POSTGRES_PASSWORD=cafe1234", PG, "관리자 비밀번호<br>(꼭 있어야 해요)", "rr-e"), ("-p 5432:5432", BL, "5432번 문 열기", None), ("postgres:18", DK, "이미지", None)]
o += parts(96, 250, segs, size=31, order=1, lab=24, stagger=True, lw=300)
t = Term([("$", P_HOME, RUN), ("o", D["run"][0]["out"][0]), ("o", ""), ("$", P_HOME, C("ps"))] + [("o", l) for l in RA("ps")], 96, 470, size=24, w=1728, lh=1.65, tid="t-run")
o.append(t.html())
o.append(spot(4, target=None, x=round(t.sx(5, "Up 2 seconds") - 6), y=round(t.top(5) - 4), w=round(t.sw("Up 2 seconds   0.0.0.0:5432->5432/tcp") + 12), h=round(t.lp + 8)))
o.append(spot_off(5))
o.append(caption("새로 나온 건 -e 하나예요. 나머지는 29의 docker run 그대로예요.", t.y + t.h + 40, 5, size=30))
W("r-run", o, "docker run 한 줄로 PostgreSQL 서버를 켜요. 대부분 29에서 배운 옵션이에요. -d로 뒤에서 켜고, --name으로 이름을 pg로 붙이고, -p로 포트를 열어요. PostgreSQL은 5432번 포트에서 접속을 기다려서 5432:5432로 열어요. 새로 나온 건 -e예요. -e POSTGRES_PASSWORD는 관리자 계정의 비밀번호를 정해요. 이 값이 없으면 켜지자마자 꺼지는데, 5파트에서 실제로 봐요. 터미널에는 긴 컨테이너 ID 한 줄만 나와요. docker ps로 보면 STATUS가 Up이고 PORTS에 5432번이 열려 있어요." + REAL)

o = frame("r-env", EB1, "-e로 건네는 이름 세 개가 계정과 데이터베이스를 정해요", C1)
envs = [("POSTGRES_PASSWORD", "관리자 비밀번호", "꼭 적어야 해요", "cafe1234"),
        ("POSTGRES_USER", "관리자 이름", "안 적으면 postgres", "postgres"),
        ("POSTGRES_DB", "처음 만들 데이터베이스", "안 적으면 관리자 이름과 같아요", "postgres")]
o.append(p(f"position:absolute;left:96px;top:226px;font-size:24px;font-weight:700;color:{GRAY}", "-e 이름"))
o.append(p(f"position:absolute;left:590px;top:226px;font-size:24px;font-weight:700;color:{GRAY}", "정하는 것"))
o.append(p(f"position:absolute;left:1020px;top:226px;font-size:24px;font-weight:700;color:{GRAY}", "오늘 값"))
for i, (n_, w_, d_, v_) in enumerate(envs):
    y = 272 + i * 150
    ra = bi("rise", 1) + DELAY(i * 100)
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1160px;height:1px;background:{LINE}"></div>')
    o.append(p(f"position:absolute;left:96px;top:{y + 26}px;font-family:{MONO};font-size:30px;font-weight:700;color:{PG};white-space:nowrap", e(n_), ra + (' id="env-pw"' if i == 0 else "")))
    o.append(p(f"position:absolute;left:590px;top:{y + 20}px;font-size:28px;font-weight:700;color:{INK};white-space:nowrap", e(w_), ra))
    o.append(p(f"position:absolute;left:590px;top:{y + 66}px;font-size:23px;color:{SUB};white-space:nowrap", e(d_), ra))
    o.append(p(f"position:absolute;left:1020px;top:{y + 26}px;font-family:{MONO};font-size:30px;font-weight:700;color:{INK};white-space:nowrap", e(v_), ra))
o.append(f'<div style="position:absolute;left:96px;top:{272 + 3 * 150}px;width:1160px;height:1px;background:{LINE}"></div>')
env = RA("env")
t = Term([("$", P_HOME, C("env"))] + [("o", l) for l in env if not l.startswith("PATH=")], 1300, 214, size=20, w=524, lh=1.75, tid="t-env", bleed=True)
o.append(t.html())
pw = next(i for i, r in enumerate(t.rows) if r[1].startswith("POSTGRES_PASSWORD"))
o.append(f'<div{bi("fade", 2)} style="position:absolute;left:{t.x + 22}px;top:{t.top(pw):.0f}px;width:{t.w - 44}px;height:{t.lp}px;background:rgba(157,193,230,.22);border-radius:6px"></div>')
o.append(caption("오늘은 비밀번호만 건네요. 관리자는 postgres, 데이터베이스도 postgres로 시작해요.", 800, 3, size=30))
o.append(caption("POSTGRES_USER와 POSTGRES_DB는 3파트와 4파트에서 직접 써 봐요.", 862, 3, size=26, color=SUB))
W("r-env", o, "-e로 건네는 이름 세 개가 계정과 데이터베이스를 정해요. 이런 값을 환경 변수라고 해요. 프로그램이 켜질 때 읽는 이름=값 쪽지예요. POSTGRES_PASSWORD는 관리자 비밀번호로, 꼭 적어야 해요. POSTGRES_USER는 관리자 이름인데, 안 적으면 postgres예요. POSTGRES_DB는 처음 만들 데이터베이스 이름인데, 안 적으면 관리자 이름과 같아요. 오늘은 비밀번호만 건넸으니 관리자도 postgres, 데이터베이스도 postgres로 시작해요. 오른쪽은 31에서 배운 docker exec 이름 명령으로 env를 실행한 결과예요. 우리가 건넨 POSTGRES_PASSWORD가 들어 있어요. PGDATA는 데이터를 저장하는 폴더인데 4파트에서 다시 봐요. 맨 위 PATH 줄은 길어서 뺐어요. cafe1234는 연습용 비밀번호예요. 실제 서비스에서는 긴 비밀번호를 쓰고 GitHub에 올리지 않아요." + REAL)

o = frame("r-logs", EB1, "logs에 ready to accept connections가 두 번 나오면 준비 끝이에요", C1)
lg = RA("logs")
first_ready = next(i for i, l in enumerate(lg) if "ready to accept connections" in l)
init = next(i for i, l in enumerate(lg) if l.startswith("PostgreSQL init process complete"))
lis = next(i for i, l in enumerate(lg) if i > init and "listening on IPv4" in l)
last = max(i for i, l in enumerate(lg) if "ready to accept connections" in l)
pick = [lg[0], "…", short_log(lg[first_ready]), lg[first_ready + 3] if lg[first_ready + 3].startswith("server") else "server started", "…", lg[next(i for i, l in enumerate(lg) if l == "server stopped")], lg[init], "…", short_log(lg[lis]), short_log(lg[last])]
rows = [("$", P_HOME, C("logs"))] + [("d" if l == "…" else "o", l) for l in pick]
t = Term(rows, 96, 214, size=27, w=1728, lh=1.7, tid="t-logs")
t.band(3, order=1, color="rgba(127,135,150,.22)")
t.band(7, order=2, color="rgba(127,209,139,.16)")
t.band(9, 10, order=3, color="rgba(157,193,230,.22)")
o.append(t.html())
o += tag(t, 3, "준비용 서버 (밖에서 못 들어와요)", GRAY, 1)
o += tag(t, 7, "준비 끝, 진짜 서버를 켜요", GR, 2)
o += tag(t, 10, "5432번에서 기다려요", PG, 3)
o.append(caption("처음 켤 때는 몇 초 걸려요. 마지막 줄이 보이면 들어가요.", t.y + t.h + 44, 3, size=30))
W("r-logs", o, "logs에 ready to accept connections가 두 번 나오면 준비 끝이에요. 처음 켤 때 PostgreSQL은 할 일이 많아서 기록이 길어요. 먼저 데이터 파일을 만들어요. 다음에 밖에서는 못 들어오는 준비용 서버를 잠깐 켜서 비밀번호를 정하고 끄는데, 이때 ready to accept connections가 한 번 나와요. init process complete가 나오면 준비가 끝난 거예요. 그다음 진짜 서버를 5432번 포트로 켜고 ready to accept connections가 한 번 더 나와요. 이 마지막 줄이 보이면 들어가도 돼요. 너무 빨리 들어가면 생기는 오류는 5파트에서 봐요. 기록이 60줄쯤 돼서 가운데를 …로 줄였고, 줄 앞의 시각과 번호도 …로 줄였어요." + REAL)

o = frame("r-psql", EB1, "docker exec -it로 컨테이너 안의 psql을 열어요", C1)
segs = [("docker exec -it pg", INK, "30에서 배운<br>컨테이너 안에서 실행", None), ("psql", PG, "PostgreSQL에<br>접속하는 프로그램", "rp-psql"), ("-U postgres", US, "계정 이름<br>(User)", "rp-u")]
o += parts(96, 236, segs, size=44, order=1, lab=24, stagger=True, lw=330)
en = [l.rstrip() for l in D["enter" if "enter" in D else "psql"][0]["out"]]
en = [l for l in en if not l.startswith("postgres=# \\conninfo")][:4]
rows = [("$", P_HOME, C("psql"))] + psql_rows(en) + [("$", P_HOME, "")]
t = Term(rows, 96, 520, size=28, w=1060, lh=1.6, tid="t-psql")
o.append(t.html())
pi = next(i for i, r in enumerate(rows) if r[0] == "m")
o.append(underline(2, t.tx, t.tx + t.sw("postgres=#"), t.top(pi) + t.lp - 2, PG))
o.append(f'<div{bi("fade", 3)} style="position:absolute;left:{t.x + 22}px;top:{t.top(pi):.0f}px;width:{t.w - 44}px;height:{t.lp}px;background:rgba(242,196,109,.16);border-radius:6px"></div>')
side = 1220
o.append(p(f"position:absolute;left:{side}px;top:530px;font-family:{MONO};font-size:46px;font-weight:700;color:{PG}", "postgres=#", bi("rise", 2)))
o.append(p(f"position:absolute;left:{side}px;top:606px;width:604px;font-size:27px;line-height:1.5;color:{INK}", "앞은 지금 들어와 있는 데이터베이스 이름이에요. 이 뒤에 SQL을 쳐요.", bi("rise", 2)))
o.append(p(f"position:absolute;left:{side}px;top:770px;font-family:{MONO};font-size:46px;font-weight:700;color:{OR}", "\\q", bi("rise", 3)))
o.append(p(f"position:absolute;left:{side}px;top:846px;width:604px;font-size:27px;line-height:1.5;color:{INK}", "psql을 나와 내 터미널로 돌아와요. 컨테이너는 계속 돌아요.", bi("rise", 3)))
W("r-psql", o, "docker exec -it로 컨테이너 안의 psql을 열어요. 30에서 docker exec -it로 bash를 열었던 것과 같아요. 이번에는 bash 대신 PostgreSQL에 접속하는 프로그램 psql을 열어요. -U postgres는 postgres 계정으로 들어간다는 뜻이에요. 33의 mysql -u root처럼 계정 이름을 적는 자리인데, 대문자 U인 것만 달라요. 비밀번호는 묻지 않고 바로 들어가요. 이유는 3파트에서 봐요. 맨 위 두 줄은 psql 버전과 도움말 안내예요. 그 아래 postgres=# 표시가 나오면 들어온 거예요. 앞의 postgres는 지금 들어와 있는 데이터베이스 이름이에요. 이 뒤에 SQL을 쳐요. 백슬래시 q를 치면 psql을 나와 내 터미널로 돌아와요. 컨테이너는 계속 돌아요." + REAL)

# =====================================================================
# part 2: databases and tables
# =====================================================================
o = frame("s-meta", EB2, "psql에는 SQL과 백슬래시 명령, 두 가지를 쳐요", C2)
o.append(p(f"position:absolute;left:96px;top:226px;font-size:34px;font-weight:700;color:{GR}", "SQL"))
o.append(p(f"position:absolute;left:96px;top:282px;width:760px;font-size:26px;line-height:1.5;color:{SUB}", "데이터베이스에 시키는 말이에요. 33 MySQL에서도 같아요. 끝에 ;를 붙여야 실행돼요."))
sqls = ["CREATE DATABASE shop;", "CREATE TABLE orders (…);", "INSERT INTO orders VALUES (…);", "SELECT * FROM orders;", "DROP TABLE orders;"]
o.append(f'<div{STAGGER(1)} style="position:absolute;left:96px;top:400px;width:760px;display:flex;flex-direction:column;gap:16px">'
         + "".join(p(f"height:60px;padding:0 22px;border-radius:12px;background:#E4F3EA;font-family:{MONO};font-size:27px;font-weight:700;line-height:60px;color:{GR};white-space:nowrap", e(s_)) for s_ in sqls) + '</div>')
o.append(f'<div style="position:absolute;left:940px;top:226px;width:2px;height:720px;background:{LINE}"></div>')
o.append(p(f"position:absolute;left:1020px;top:226px;font-size:34px;font-weight:700;color:{PG}", "백슬래시 명령"))
o.append(p(f"position:absolute;left:1020px;top:282px;width:804px;font-size:26px;line-height:1.5;color:{SUB}", "psql이 알아듣는 짧은 명령이에요. \\로 시작하고 ;를 안 붙여요."))
metas = [("\\l", "데이터베이스 목록"), ("\\c shop", "shop으로 이동"), ("\\dt", "표 목록"), ("\\d orders", "표 구조"), ("\\du", "계정 목록"), ("\\q", "나가기")]
o.append(f'<div{STAGGER(2)} style="position:absolute;left:1020px;top:400px;width:804px;display:flex;flex-direction:column;gap:16px">'
         + "".join('<div style="display:flex;flex-direction:row;align-items:center;gap:26px">'
                   + p(f"width:230px;height:60px;flex:none;padding:0 22px;border-radius:12px;background:{PGBG};font-family:{MONO};font-size:27px;font-weight:700;line-height:60px;color:{PG};white-space:nowrap", e(k_))
                   + p(f"font-size:27px;color:{INK};white-space:nowrap", e(v_)) + '</div>' for k_, v_ in metas) + '</div>')
W("s-meta", o, "psql에는 SQL과 백슬래시 명령, 두 가지를 쳐요. 왼쪽 SQL은 데이터베이스에 시키는 말이에요. 32에서 읽어 본 CREATE TABLE, INSERT, SELECT가 여기에 들어가고, 33 MySQL에서 친 문장과 글자까지 같아요. SQL은 끝에 세미콜론을 붙여야 실행돼요. 오른쪽은 psql이 알아듣는 짧은 명령이에요. 백슬래시로 시작하고 세미콜론을 붙이지 않아요. 데이터베이스 목록은 백슬래시 l, 이동은 백슬래시 c, 표 목록은 백슬래시 dt예요. MySQL에서는 SHOW DATABASES 같은 SQL로 하던 일인데, PostgreSQL은 이런 일을 psql 명령으로 해요. 이 파트에서 하나씩 쳐 봐요. 맨 끝에 MySQL 명령과 나란히 놓은 표도 있어요.", ("p2", "데이터베이스와 표 만들기"))

o = frame("s-db", EB2, "CREATE DATABASE로 만들고 \\l로 목록을 봐요", C2)
sd = S("s-db")
rows = [("$", P_HOME, C("s-db"))] + psql_rows(sd)
t = Term(rows, 96, 214, size=19, w=1728, lh=1.75, tid="t-sdb")
shop_i = next(i for i, r in enumerate(rows) if r[0] == "o" and r[1].startswith(" shop "))
t.band(shop_i, order=2, color="rgba(127,209,139,.2)")
o.append(t.html())
cdi = next(i for i, r in enumerate(rows) if r[0] == "o" and r[1] == "CREATE DATABASE")
o += tag(t, cdi, "다 만들었다는 답이에요", GR, 1)
o += tag(t, shop_i, "새로 생긴 shop", GR, 2, at=t.sx(shop_i, "en_US.utf8 |  ") + 10, gap=60) if False else []
li = next(i for i, r in enumerate(rows) if r[0] == "m" and r[2] == "\\l")
o += tag(t, li, "데이터베이스 목록", PG, 2)
o.append(caption("postgres는 처음부터 있던 것, template0과 template1은 PostgreSQL이 새 데이터베이스를 만들 때 쓰는 틀이에요.", t.y + t.h + 36, 3, size=26, color=SUB))
W("s-db", o, "CREATE DATABASE로 만들고 백슬래시 l로 목록을 봐요. 서버 안에는 데이터베이스를 여러 개 둘 수 있어요. 카페 주문을 담을 shop을 새로 만들어요. CREATE DATABASE shop 뒤에 세미콜론을 붙이고 Enter를 치면 CREATE DATABASE라고 짧게 답해요. 잘 만들었다는 뜻이에요. 백슬래시 l을 치면 데이터베이스 목록이 표로 나와요. Name 칸에 shop이 새로 생겼어요. postgres는 처음부터 있던 데이터베이스예요. template0과 template1은 새 데이터베이스를 만들 때 PostgreSQL이 베껴 쓰는 틀이라 건드리지 않아요. 오른쪽 칸들은 글자 규칙과 권한이라 지금은 넘어가요. 이 표는 넓어서, 터미널 창이 좁으면 목록 보기 화면이 열려요. 그럴 땐 q를 누르면 닫혀요." + REAL)

o = frame("s-c", EB2, "\\c shop으로 옮기면 앞의 이름이 shop=#로 바뀌어요", C2)
sc = S("s-c")
rows = [("$", P_HOME, C("s-c"))] + psql_rows(sc)
t = Term(rows, 96, 214, size=28, w=1100, lh=1.65, tid="t-sc")
o.append(t.html())
ci = next(i for i, r in enumerate(rows) if r[0] == "o" and r[1].startswith("You are now"))
o.append(f'<div{bi("fade", 1)} style="position:absolute;left:{t.x + 22}px;top:{t.top(ci):.0f}px;width:{t.w - 44}px;height:{t.lp}px;background:rgba(127,209,139,.18);border-radius:6px"></div>')
# server with two databases and a "you are here" marker
SX, SY = 1260, 214
o.append(f'<div style="position:absolute;left:{SX}px;top:{SY}px;width:564px;height:520px;background:{CARD};border:3px solid {PG};border-radius:20px"></div>')
o.append(p(f"position:absolute;left:{SX + 28}px;top:{SY + 20}px;font-size:26px;font-weight:700;color:{PG}", "PostgreSQL 서버"))
o.append(cyl(SX + 30, SY + 110, 240, 200, "postgres", None, PG, PGBG, "sc-db0"))
o.append(cyl(SX + 294, SY + 110, 240, 200, "shop", None, PG, PGBG, "sc-db1"))
o.append(f'<div id="sc-here0"{MORPH_FROM()} style="position:absolute;left:{SX + 70}px;top:{SY + 340}px">{tok("here", "지금 여기", f"height:48px;padding:0 18px;border-radius:24px;background:{GR};font-size:24px;font-weight:700;line-height:48px;color:#FFFFFF;white-space:nowrap")}</div>')
o.append(f'<div{MORPH(2, "sc-here0")} style="position:absolute;left:{SX + 334}px;top:{SY + 340}px">{tok("here", "지금 여기", f"height:48px;padding:0 18px;border-radius:24px;background:{GR};font-size:24px;font-weight:700;line-height:48px;color:#FFFFFF;white-space:nowrap")}</div>')
o.append(p(f"position:absolute;left:{SX + 30}px;top:{SY + 420}px;width:504px;font-size:23px;line-height:1.45;color:{SUB}", "표는 데이터베이스 안에 만들어져요. 표를 만들기 전에 어디에 있는지 봐요."))
# prompt morph
o.append(f'<div id="sc-p0"{MORPH_FROM()} style="position:absolute;left:96px;top:620px;font-family:{MONO};font-size:80px;font-weight:700;line-height:1.2;white-space:nowrap">{tok("db", "postgres", f"color:{PG}")}{tok("sign", "=#", "color:#7D8696")}</div>')
o.append(f'<div{MORPH(3, "sc-p0")} style="position:absolute;left:96px;top:620px;font-family:{MONO};font-size:80px;font-weight:700;line-height:1.2;white-space:nowrap">{tok("db2", "shop", f"color:{GR}")}{tok("sign", "=#", "color:#7D8696")}</div>')
o.append(caption("psql을 새로 열 때 -d shop을 붙이면 처음부터 shop으로 들어가요.", 800, 3, size=30))
o.append(p(f"position:absolute;left:96px;top:868px;font-family:{MONO};font-size:28px;font-weight:700;color:{INK}", "docker exec -it pg psql -U postgres -d shop", bi("rise", 3)))
W("s-c", o, "백슬래시 c shop으로 옮기면 앞의 이름이 shop=#로 바뀌어요. psql은 한 번에 데이터베이스 하나에 들어가 있어요. 처음에는 postgres에 있어서 표시가 postgres=#였어요. 백슬래시 c 뒤에 shop을 적으면 You are now connected to database shop, shop에 연결했다는 답이 나오고 표시가 shop=#로 바뀌어요. 표는 지금 있는 데이터베이스 안에 만들어지니, 표를 만들기 전에 이 표시를 꼭 봐요. 33 MySQL의 USE shop과 같은 일이에요. psql을 새로 열 때부터 shop으로 들어가려면 끝에 -d shop을 붙여요. d는 데이터베이스예요. 다음 장부터는 이렇게 들어가요." + REAL)

o = frame("s-table", EB2, "CREATE TABLE로 표를 만들고 \\dt, \\d로 확인해요", C2)
stb = S("s-table")
stb = [l for l in stb if not l.startswith("shop=# \\q")]
while stb and not stb[-1].strip():
    stb.pop()
rows = [("$", P_HOME, C("s-table"))] + psql_rows(stb)
t = Term(rows, 96, 206, size=20, w=1728, lh=1.62, tid="t-stb")
o.append(t.html())
dti = next(i for i, r in enumerate(rows) if r[0] == "m" and r[2] == "\\dt")
ddi = next(i for i, r in enumerate(rows) if r[0] == "m" and r[2] == "\\d orders")
o += tag(t, dti, "표 목록", PG, 1)
o += tag(t, ddi, "orders 표의 열", PG, 2)
ii = next(i for i, r in enumerate(rows) if r[0] == "o" and r[1].startswith(" id "))
mi = next(i for i, r in enumerate(rows) if r[0] == "o" and r[1].startswith(" menu "))
ki = next(i for i, r in enumerate(rows) if r[0] == "o" and "PRIMARY KEY" in r[1])
o += tag(t, ii, "INT", GRAY, 3, at=t.end(ii) + 40)
o += tag(t, mi, "VARCHAR(20)", GRAY, 3, at=t.end(ii) + 40)
o += tag(t, ki, "id가 기본 키예요", VO, 4)
o.append(caption("INT는 integer, VARCHAR는 character varying으로, 긴 이름으로 보여 줘요.", t.y + t.h + 34, 4, size=28))
W("s-table", o, "CREATE TABLE로 표를 만들고 백슬래시 dt, 백슬래시 d로 확인해요. 이번에는 -d shop을 붙여 처음부터 shop으로 들어갔어요. CREATE TABLE 문장은 32와 33에서 쓴 것과 글자까지 같아요. id는 정수이면서 기본 키, menu는 20자까지의 글자, qty는 정수예요. CREATE TABLE이라고 답하면 표가 생긴 거예요. 백슬래시 dt는 지금 데이터베이스의 표 목록이에요. orders가 보여요. Schema 칸의 public은 표를 담는 기본 칸인데, 지금은 넘어가요. 백슬래시 d orders는 표의 열과 타입을 보여 줘요. INT는 integer, VARCHAR(20)은 character varying(20)으로, 같은 타입을 긴 이름으로 보여 줘요. 맨 아래 PRIMARY KEY 줄은 id가 기본 키라는 뜻이에요. 기본 키라서 id 칸은 비워 둘 수 없다고 not null이 붙었어요." + REAL)

o = frame("s-insert", EB2, "INSERT로 행을 넣고 SELECT로 꺼내 봐요", C2)
si = S("s-insert")
si = [l for l in si if not l.startswith("shop=# \\q")]
while si and not si[-1].strip():
    si.pop()
rows = [("$", P_HOME, C("s-insert"))] + psql_rows(si)
t = Term(rows, 96, 214, size=23, w=1020, lh=1.5, tid="t-sin")
o.append(t.html())
ins = [i for i, r in enumerate(rows) if r[0] == "o" and r[1] == "INSERT 0 1"]
o += tag(t, ins[0], "1행 넣었어요", GR, 1, gap=36)
s1 = next(i for i, r in enumerate(rows) if r[0] == "m" and r[2].startswith("SELECT *"))
s2 = next(i for i, r in enumerate(rows) if r[0] == "m" and r[2].startswith("SELECT menu"))
t_end = t
cells = {}
for i_ in range(2):
    for j_ in range(3):
        cells[(i_, j_)] = bi("rise", 1 + i_)
sh_html, g = sheet(1190, 260, COLS, ORD, "s-sheet", [160, 310, 160], size=30, rh=80, types=TYPES, name="orders", ncol=PG, pk=True, cell_attrs=cells)
o.append(sh_html)
o.append(spot(3, x=t.x + 12, y=round(t.top(s1) - 4), w=t.w - 24, h=round(t.lp * 6 + 8)))
o.append(spot(4, x=t.x + 12, y=round(t.top(s2) - 4), w=t.w - 24, h=round(t.lp * 6 + 8)))
o.append(spot_off(5))
o.append(p(f"position:absolute;left:1190px;top:{g['y'] + g['h'] + 50:.0f}px;width:634px;font-size:27px;line-height:1.5;color:{INK}", "값은 표를 만들 때 적은 열 순서대로 넣어요. 글자는 '작은따옴표'로 감싸요.", bi("rise", 5)))
o.append(p(f"position:absolute;left:1190px;top:{g['y'] + g['h'] + 190:.0f}px;width:634px;font-size:27px;line-height:1.5;color:{INK}", "*는 모든 열이에요. 열 이름을 적으면 그 열만 나와요.", bi("rise", 5)))
W("s-insert", o, "INSERT로 행을 넣고 SELECT로 꺼내 봐요. INSERT INTO orders VALUES 뒤 괄호에 값을 적어요. 값은 표를 만들 때 적은 열 순서대로예요. id, menu, qty 순서라서 1, 'latte', 2는 1번 주문, 라테 2잔이에요. 글자는 작은따옴표로 감싸고 숫자는 그대로 써요. PostgreSQL은 INSERT 0 1이라고 답해요. 뒤의 1이 넣은 행의 수예요. 앞의 0은 지금은 신경 쓰지 않아도 돼요. 두 번 넣었으니 오른쪽 표처럼 행이 두 개예요. SELECT 별표 FROM orders는 모든 열을 꺼내요. 결과 표 아래 2 rows는 행이 두 개라는 뜻이에요. 별표 대신 menu, qty처럼 열 이름을 적으면 그 열만 나와요. 33 MySQL에서 친 문장과 똑같고, 결과 표 모양만 테두리 없이 조금 달라요." + REAL)

o = frame("s-drop", EB2, "DROP으로 지워요. 들어가 있는 데이터베이스는 못 지워요", C2)
sdp = S("s-drop")
sdp = sdp[:next(i for i, l in enumerate(sdp) if l.startswith("postgres=# \\l"))]
rows = [("$", P_HOME, C("s-drop"))] + psql_rows(sdp)
t = Term(rows, 96, 214, size=26, w=1180, lh=1.62, tid="t-sdp")
o.append(t.html())
nf = next(i for i, r in enumerate(rows) if r[0] == "o" and r[1].startswith("Did not find"))
o += tag(t, nf, "표가 없어요", GR, 1, gap=36)
er = next(i for i, r in enumerate(rows) if r[0] == "e")
o.append(pen_box(2, round(t.tx - 8), round(t.top(er) - 2), round(t.sw(rows[er][1]) + 16), round(t.lp + 4), RED))
cp_ = next(i for i, r in enumerate(rows) if r[0] == "m" and r[2] == "\\c postgres")
dd = max(i for i, r in enumerate(rows) if r[1] == "DROP DATABASE")
t2 = None
o.append(f'<div{bi("fade", 3)} style="position:absolute;left:{t.x + 22}px;top:{t.top(cp_):.0f}px;width:{t.w - 44}px;height:{t.lp * (dd - cp_ + 1):.0f}px;background:rgba(127,209,139,.16);border-radius:6px"></div>')
side = 1340
o.append(p(f"position:absolute;left:{side}px;top:300px;width:484px;font-size:28px;font-weight:700;line-height:1.45;color:{RED}", "cannot drop the currently open database", bi("rise", 2)))
o.append(p(f"position:absolute;left:{side}px;top:400px;width:484px;font-size:26px;line-height:1.5;color:{INK}", "지금 들어가 있는 데이터베이스라서 못 지운다는 뜻이에요.", bi("rise", 2)))
o.append(p(f"position:absolute;left:{side}px;top:560px;width:484px;font-size:26px;line-height:1.5;color:{INK}", "\\c postgres로 다른 데이터베이스에 옮긴 뒤 지워요.", bi("rise", 3)))
o.append(f'<div{bi("rise", 4)} style="position:absolute;left:{side}px;top:740px;width:484px;padding:22px 26px;border-radius:14px;background:#FBEAEA;border-left:6px solid {RED}">'
         + p(f"font-size:25px;line-height:1.5;color:{INK}", "DROP은 되돌릴 수 없어요. 안의 표와 행도 같이 지워져요. 연습용에서만 쳐요.") + '</div>')
W("s-drop", o, "DROP으로 지워요. 들어가 있는 데이터베이스는 못 지워요. DROP TABLE orders는 표를 통째로 지워요. 백슬래시 dt로 보면 Did not find any tables, 표가 하나도 없다고 나와요. 이어서 DROP DATABASE shop을 치면 오류가 나요. cannot drop the currently open database, 지금 열려 있는 데이터베이스는 지울 수 없다는 뜻이에요. 표시가 shop=#인 걸 보면 지금 shop 안에 있어요. 백슬래시 c postgres로 옮긴 다음 다시 치면 DROP DATABASE라고 답하고 지워져요. 33 MySQL은 들어가 있는 데이터베이스도 지워지는데, PostgreSQL은 이렇게 막아 줘요. DROP은 되돌릴 수 없고 안의 표와 행이 모두 지워지니, 연습용 데이터베이스에서만 쳐요. 마지막에 친 백슬래시 l 결과는 앞 장과 같아서 뺐어요." + REAL)

# =====================================================================
# part 3: accounts and ways in
# =====================================================================
o = frame("u-roles", EB3, "관리자는 =#, 일반 계정은 =>로 표시가 달라요", C3)
ua = S("u-app")
ua = [l for l in ua if not l.startswith("postgres=# \\q")]
while ua and not ua[-1].strip():
    ua.pop()
rows = [("$", P_HOME, C("u-app"))] + psql_rows(ua)
t = Term(rows, 96, 214, size=22, w=1728, lh=1.5, tid="t-ua")
o.append(t.html())
ai = next(i for i, r in enumerate(rows) if r[0] == "o" and r[1].startswith(" app "))
pi = next(i for i, r in enumerate(rows) if r[0] == "o" and r[1].startswith(" postgres "))
o += tag(t, ai, "권한 없음", GRAY, 1, at=t.end(pi) + 0, gap=40)
o += tag(t, pi, "관리자 (Superuser)", US, 1)
ud = S("u-deny")
ud = [l for l in ud if not l.startswith("postgres=> \\q")]
while ud and not ud[-1].strip():
    ud.pop()
rows2 = [("$", P_HOME, C("u-deny"))] + psql_rows(ud)
t2 = Term(rows2, 96, t.y + t.h + 30, size=22, w=1728, lh=1.5, tid="t-ud")
o.append(t2.html())
pr = next(i for i, r in enumerate(rows2) if r[0] == "m")
o.append(pen_box(2, round(t2.tx - 6), round(t2.top(pr) - 2), round(t2.sw("postgres=>") + 12), round(t2.lp + 4), US))
er = next(i for i, r in enumerate(rows2) if r[0] == "e")
o += tag(t2, er, "만들 권한이 없어요", RED, 3)
o.append(caption("앱이 쓸 계정은 관리자 대신 일반 계정으로 만들어요. 실수로 데이터베이스를 지우지 못해요.", t2.y + t2.h + 32, 3, size=28))
W("u-roles", o, "관리자는 =#, 일반 계정은 =>로 표시가 달라요. postgres로 들어가서 CREATE USER로 계정 app을 만들었어요. WITH PASSWORD 뒤에 비밀번호를 작은따옴표로 적어요. PostgreSQL은 계정을 role이라고 불러서 CREATE ROLE이라고 답해요. 백슬래시 du로 계정 목록을 보면 postgres에는 Superuser, 관리자 표시가 붙어 있고 app은 비어 있어요. 아래는 app으로 들어간 모습이에요. 표시 끝이 =#이 아니라 =>예요. 관리자가 아니라는 뜻이에요. 여기서 CREATE DATABASE를 치면 permission denied, 권한이 없다는 오류가 나요. 실제 앱이 데이터베이스에 붙을 때는 이렇게 권한을 줄인 계정을 써요. 실수로 데이터베이스를 지우는 일을 막아 줘요. 일반 계정에 표를 쓸 권한을 주는 법은 다음에 배워요." + REAL, ("p3", "계정과 접속 방법"))

o = frame("u-env", EB3, "POSTGRES_USER를 주면 그 이름이 관리자가 되고 postgres는 없어요", C3)
rows = [("$", P_HOME, C("u-run"), {"-e POSTGRES_USER=cafe": f'style="color:{"#E07FB0"}"'}), ("o", idshort("u-run")), ("o", ""),
        ("$", P_HOME, C("u-nopg"))] + [("e", l) for l in RA("u-nopg")] + [("o", ""), ("$", P_HOME, C("u-cafe"))]
uc = S("u-cafe")
uc = [l for l in uc if not l.startswith("cafe=# \\q")]
while uc and not uc[-1].strip():
    uc.pop()
rows += psql_rows(uc)
t = Term(rows, 96, 214, size=19, w=1728, lh=1.5, tid="t-ue")
o.append(t.html())
fi = next(i for i, r in enumerate(rows) if r[0] == "e")
o.append(underline(1, t.sx(fi, 'role "postgres" does not exist'), t.sx(fi, 'role "postgres" does not exist') + t.sw('role "postgres" does not exist'), t.top(fi) + t.lp - 2, RED))
ci = next(i for i, r in enumerate(rows) if r[0] == "o" and r[1].startswith(" cafe "))
o += tag(t, ci, "cafe가 관리자", US, 2)
cd = next(i for i, r in enumerate(rows) if r[0] == "o" and r[1] == "CREATE DATABASE")
o += tag(t, cd, "관리자라서 돼요", GR, 3)
cy = t.y + t.h + 36
o.append(p(f"position:absolute;left:96px;top:{cy}px;font-size:26px;font-weight:700;color:{MY}", "33 MySQL의 MYSQL_USER", bi("rise", 4)))
o.append(p(f"position:absolute;left:96px;top:{cy + 44}px;width:820px;font-size:25px;line-height:1.45;color:{SUB}", "일반 계정을 하나 더 만들어요. root는 그대로 있어요.", bi("rise", 4)))
o.append(p(f"position:absolute;left:1000px;top:{cy}px;font-size:26px;font-weight:700;color:{PG}", "34 PostgreSQL의 POSTGRES_USER", bi("rise", 4)))
o.append(p(f"position:absolute;left:1000px;top:{cy + 44}px;width:824px;font-size:25px;line-height:1.45;color:{SUB}", "관리자 이름을 바꿔요. postgres 계정은 안 생겨요.", bi("rise", 4)))
W("u-env", o, "POSTGRES_USER를 주면 그 이름이 관리자가 되고 postgres는 없어요. 33 MySQL과 반대라서 헷갈리기 쉬운 곳이에요. 컨테이너 pg2를 -e POSTGRES_USER=cafe로 켰어요. pg가 5432번을 쓰고 있어서 내 컴퓨터 쪽 포트만 5433으로 바꿨어요. 그 뒤 33에서 하던 대로 -U postgres로 들어가면 role postgres does not exist, postgres라는 계정이 없다는 오류가 나요. POSTGRES_USER가 관리자 이름 자체를 바꿨기 때문이에요. -U cafe로 들어가면 표시가 cafe=#이에요. 데이터베이스 이름도 POSTGRES_DB를 안 줘서 관리자 이름과 같은 cafe예요. 백슬래시 du를 보면 cafe가 Superuser이고, CREATE DATABASE도 그대로 돼요. MySQL의 MYSQL_USER는 root 옆에 일반 계정을 하나 더 만들어서 CREATE DATABASE가 막혔어요. PostgreSQL에서 권한이 작은 계정이 필요하면 앞 장처럼 CREATE USER로 만들어요." + REAL)

o = frame("a-bash", EB3, "bash로 들어가서 psql을 쳐도 돼요. 안에서는 비밀번호를 안 물어요", C3)
bl = [l.rstrip() for l in D["bash"][0]["out"]]
bl = [l for l in bl if not l.startswith("psql (18") and not l.startswith('Type "help"') and l.strip()]
ci = next(i for i, l in enumerate(bl) if l.endswith("\\conninfo"))
ce = next(i for i, l in enumerate(bl) if l.startswith("(13 rows)"))
body = bl[ci + 4:ce]
bl = bl[:ci + 4] + [l for l in body if l.startswith(" Host  ") or l.startswith(" Password Used")] + ["…"] + bl[ce + 1:]
rows = [("$", P_HOME, C("bash"))] + [("d", "…") if r[1] == "…" else r for r in psql_rows(bl)]
t = Term(rows, 96, 214, size=21, w=1180, lh=1.5, tid="t-ab")
pu = next((i for i, r in enumerate(rows) if "Password Used" in r[1]), None)
if pu is not None:
    t.band(pu, order=2, color="rgba(242,196,109,.22)")
o.append(t.html())
r1 = [i for i, r in enumerate(rows) if r[0] == "#"]
o += tag(t, r1[0], "비밀번호 안 물어요", GR, 1, gap=36)
o += tag(t, r1[1], "-h localhost도 그대로", GR, 2, gap=36)
side = 1340
o.append(p(f"position:absolute;left:{side}px;top:240px;width:484px;font-size:27px;font-weight:700;line-height:1.45;color:{INK}", "컨테이너 안에서 오는 접속은 믿고 들여보내요.", bi("rise", 3)))
o.append(p(f"position:absolute;left:{side}px;top:350px;width:484px;font-size:25px;line-height:1.5;color:{SUB}", "공식 이미지가 그렇게 설정해 둬요. 이걸 trust라고 불러요.", bi("rise", 3)))
o.append(p(f"position:absolute;left:{side}px;top:500px;width:484px;font-size:27px;font-weight:700;line-height:1.45;color:{INK}", "root@…:/#는 컨테이너 안 bash예요.", bi("rise", 4)))
o.append(p(f"position:absolute;left:{side}px;top:566px;width:484px;font-size:25px;line-height:1.5;color:{SUB}", "psql을 나와도 아직 컨테이너 안이에요. exit로 내 터미널에 돌아와요.", bi("rise", 4)))
W("a-bash", o, "bash로 들어가서 psql을 쳐도 돼요. 30에서처럼 docker exec -it pg bash로 컨테이너 안에 먼저 들어가면 표시가 root@컨테이너ID:/#로 바뀌어요. 여기서 psql -U postgres를 치면 앞에서 본 것과 같은 psql이 열려요. 비밀번호는 묻지 않아요. -h localhost를 붙여서 주소로 접속해도 마찬가지예요. 백슬래시 conninfo의 Password Used가 false예요. 공식 이미지는 컨테이너 안에서 오는 접속을 믿고 들여보내게 설정해 둬요. 이걸 trust라고 불러요. 33 MySQL은 안에서도 -p로 비밀번호를 물었는데, 여기가 달라요. 백슬래시 q로 psql을 나와도 아직 컨테이너 안 bash예요. exit를 쳐야 내 터미널로 돌아와요. psql이 시작할 때 찍는 버전과 도움말 두 줄은 앞 장과 같아서 뺐고, 백슬래시 conninfo 결과는 필요한 줄만 옮겼어요." + REAL)

o = frame("a-out", EB3, "밖에서 5432번으로 붙으면 비밀번호를 물어요", C3)
segs = [("docker run --rm -it", INK, "잠깐 쓰고 지울<br>컨테이너 하나 더", None), ("--add-host host.docker.internal:host-gateway", GRAY, "이 이름을 쓰게 해 줘요<br>(Mac, Windows는 없어도 돼요)", None),
        ("postgres:18", DK, "psql이 들어 있는 이미지", None), ("psql -h host.docker.internal -U postgres", PG, "내 컴퓨터 5432번으로 접속", None)]
o += parts(96, 226, segs, size=19, order=1, lab=21, stagger=False, lw=340, drop=22)
ou = [l.rstrip() for l in D["out"][0]["out"]]
ou = [l for l in ou if not l.startswith("psql (18") and not l.startswith('Type "help"') and l.strip()]
ou = [l for l in ou if not l.startswith("postgres=# \\q")]
oc = next(i for i, l in enumerate(ou) if l.endswith("\\conninfo"))
oe = next(i for i, l in enumerate(ou) if l.startswith("(13 rows)"))
ou = ou[:oc + 4] + [l for l in ou[oc + 4:oe] if l.startswith(" Host  ") or l.startswith(" Server Port") or l.startswith(" Password Used")] + ["…"] + ou[oe + 1:]
rows = [("$", P_HOME, "docker run … psql -h host.docker.internal -U postgres")] + [("d", "…") if r[1] == "…" else r for r in psql_rows(ou)]
pu = next(i for i, r in enumerate(rows) if "Password Used" in r[1])
t = Term(rows, 96, 400, size=19, w=1000, lh=1.62, tid="t-out")
t.band(pu, order=2, color="rgba(242,196,109,.22)")
o.append(t.html())
o += tag(t, 1, "cafe1234를 쳤어요 (화면엔 안 보여요)", US, 2, gap=36)
bp = [l.rstrip() for l in D["badpw"][0]["out"]]
rows2 = [("$", P_HOME, "docker run … -U postgres")] + [("o", bp[0])] + [("e", l) for l in rewrap(bp[1:], 52)]
t2 = Term(rows2, 1150, 400, size=19, w=674, lh=1.62, tid="t-bad")
o.append(t2.html())
o += tag(t2, 1, "cafe123", RED, 3, gap=36)
o.append(caption("나중에 파이썬 앱도 이렇게 밖에서 5432번으로 붙어요. 그때 비밀번호가 필요해요.", t2.y + t2.h + 40, 3, left=1150, width=674, size=27))
W("a-out", o, "밖에서 5432번으로 붙으면 비밀번호를 물어요. 컨테이너 밖의 프로그램이 붙는 모습을 보려고, psql이 들어 있는 postgres:18 이미지로 컨테이너를 하나 더 켜서 내 컴퓨터의 5432번으로 접속했어요. --rm은 나가면 이 컨테이너를 바로 지우는 옵션이에요. host.docker.internal은 컨테이너 안에서 내 컴퓨터를 부르는 이름이에요. Docker Desktop을 쓰는 Mac과 Windows는 이 이름을 알아서 쓸 수 있고, --add-host 부분은 리눅스에서 이 이름을 쓰게 해 줘요. 이번에는 Password for user postgres:로 비밀번호를 물어요. cafe1234를 치면 화면에는 안 보이지만 들어가져요. 백슬래시 conninfo의 Password Used가 true예요. 오른쪽은 cafe123으로 하나 빠뜨려 친 결과예요. password authentication failed, 비밀번호가 틀렸다는 오류예요. 나중에 파이썬 앱이 데이터베이스에 붙을 때도 이렇게 밖에서 5432번으로 붙어서, 그때 -e로 정한 비밀번호가 필요해요. 이 장은 따라 치지 않고 보기만 해도 돼요. 출력은 리눅스에서 만들었고, 백슬래시 conninfo 결과는 필요한 줄만 옮겼어요." + REAL)

o = frame("a-oneshot", EB3, "-c를 붙이면 SQL 한 문장만 실행하고 바로 나와요", C3)
segs = [("docker exec pg", INK, "-it 없이", None), ("psql -U postgres", PG, None, None), ('-c "SELECT version();"', GR, "이 문장 하나만 실행", None)]
o += parts(96, 220, segs, size=40, order=1, lab=24, lw=300)
v = RA("oneshot", 0)
rows = [("$", P_HOME, C("oneshot", 0))] + [("o", l.rstrip()) for l in v] + [("o", ""), ("$", P_HOME, C("oneshot", 1))] + [("o", l.rstrip()) for l in RA("oneshot", 1)]
t = Term(rows, 96, 400, size=17, w=1728, lh=1.4, tid="t-one")
o.append(t.html())
o += tag(t, len(v) + 1, "psql 화면 없이 결과만 찍고 끝나요", GR, 2, gap=40) if False else []
o.append(caption("-it가 없어서 psql 화면에 들어가지 않아요. 결과만 찍고 내 터미널로 돌아와요.", t.y + t.h + 36, 2, size=28))
W("a-oneshot", o, "-c를 붙이면 SQL 한 문장만 실행하고 바로 나와요. 31에서 docker exec 이름 명령으로 nginx -t 하나만 실행했던 것과 같아요. 이번에는 -it를 빼고, psql 뒤에 -c와 큰따옴표로 감싼 문장을 적었어요. SELECT version()은 PostgreSQL 버전을 알려 주는 문장이에요. psql 화면에 들어가지 않고 결과 표만 찍고 내 터미널로 돌아와요. 백슬래시 명령도 -c로 실행할 수 있어요. 아래는 백슬래시 l을 실행한 결과예요. 33 MySQL에서는 같은 일을 mysql -e로 했어요. 한두 문장만 확인할 때나, 나중에 명령을 스크립트에 적어 둘 때 써요." + REAL)

# =====================================================================
# part 4: volume and compose
# =====================================================================
o = frame("v-gone", EB4, "볼륨 없이 켠 컨테이너를 지우면 데이터베이스도 같이 사라져요", C4)
gm = S("g-make")
gm = [l for l in gm if not l.startswith("shop=# \\q")]
gm_short = [gm[0], gm[1], gm[2], gm[3], "shop=# CREATE TABLE orders (…);", "CREATE TABLE"] + [l for l in gm if "INSERT" in l]
rows = [("$", P_HOME, C("g-make"))] + psql_rows(gm_short)
t = Term(rows, 96, 214, size=19, w=840, lh=1.5, tid="t-g1")
o.append(t.html())
rows2 = [("$", P_HOME, C("g-rm", 0)), ("o", "pg"), ("$", P_HOME, C("g-rm", 1)), ("o", "pg"), ("$", P_HOME, "docker run -d --name pg … postgres:18"), ("o", idshort("g-rerun")), ("o", ""),
         ("$", P_HOME, C("g-gone"))] + [("e", l) for l in rewrap(RA("g-gone"), 70)]
t2 = Term(rows2, 980, 214, size=19, w=844, lh=1.5, tid="t-g2")
o.append(t2.html())
o.append(f'<div{SLIDE(1, 0, 40)} style="position:absolute;left:0;top:0;width:1px;height:1px"></div>' if False else "")
ge = next(i for i, r in enumerate(rows2) if r[0] == "e" and "does not exist" in r[1])
gsub = 'database "shop" does not exist' if 'database "shop" does not exist' in rows2[ge][1] else "does not exist"
o.append(underline(2, t2.sx(ge, gsub), t2.sx(ge, gsub) + t2.sw(gsub), t2.top(ge) + t2.lp - 2, RED))
yb = max(t.y + t.h, t2.y + t2.h) + 50
o.append(cyl(96, yb, 220, 170, "shop", "주문 2개", PG, PGBG, "vg-db", attrs=bi("fade", 3)))
o.append(p(f"position:absolute;left:360px;top:{yb + 30}px;width:1460px;font-size:30px;font-weight:700;line-height:1.45;color:{INK}", "컨테이너를 지우면 그 안의 데이터 폴더도 같이 지워져요.", bi("rise", 3)))
o.append(p(f"position:absolute;left:360px;top:{yb + 90}px;width:1460px;font-size:26px;line-height:1.5;color:{SUB}", "새로 켠 pg에는 처음부터 있던 postgres 데이터베이스만 있어요.", bi("rise", 3)))
W("v-gone", o, "볼륨 없이 켠 컨테이너를 지우면 데이터베이스도 같이 사라져요. 왼쪽은 2파트에서 한 대로 shop 데이터베이스와 orders 표를 만들고 주문 두 개를 넣은 모습이에요. 오른쪽에서 pg를 docker stop, docker rm으로 지우고, 같은 docker run 명령으로 다시 켰어요. -d shop으로 들어가려 하면 database shop does not exist, shop이라는 데이터베이스가 없다는 오류가 나요. 표와 주문뿐 아니라 데이터베이스까지 통째로 사라졌어요. 새 컨테이너에는 처음부터 있던 postgres 데이터베이스만 있어요. 실제 카페라면 하루 주문이 다 날아간 거예요. 33 MySQL에서 본 것과 같은 일이에요. 왼쪽 CREATE TABLE의 열 목록과 오른쪽 docker run의 옵션은 앞과 같아서 …로 줄였어요." + REAL, ("p4", "볼륨과 compose"))

o = frame("v-why", EB4, "데이터는 컨테이너 안 /var/lib/postgresql에 저장돼요", C4)
vi = RA("v-inside")
files_ = vi[3:]
rows = [("$", P_HOME, "docker exec pg ls /var/lib/postgresql")] + [("o", vi[1])] + [("$", P_HOME, "docker exec pg ls /var/lib/postgresql/18/docker")] + [("o", "  ".join(files_[k:k + 5])) for k in range(0, len(files_), 5)]
t = Term(rows, 96, 214, size=19, w=1020, lh=1.55, tid="t-vw")
o.append(t.html())
o += tag(t, 1, "버전 번호 폴더", VO, 1, gap=36)
o.append(p(f"position:absolute;left:96px;top:{t.y + t.h + 24}px;width:1020px;font-size:23px;line-height:1.5;color:{SUB}", "1파트 env의 PGDATA=/var/lib/postgresql/18/docker가 이 폴더예요. 데이터베이스와 표가 이 안에 파일로 있어요.", bi("rise", 1)))
# picture: container with folder, volume outside
BX, BY = 1170, 214
o.append(f'<div style="position:absolute;left:{BX}px;top:{BY}px;width:654px;height:340px;border:3px dashed {DK};border-radius:22px;background:#F1F5FD"></div>')
o.append(p(f"position:absolute;left:{BX + 28}px;top:{BY + 18}px;font-family:{MONO};font-size:24px;font-weight:700;color:{DK}", "컨테이너 pg"))
o.append(f'<div id="vw-folder" style="position:absolute;left:{BX + 40}px;top:{BY + 86}px;width:574px;height:110px;background:{CARD};border:3px solid {PG};border-radius:16px;display:flex;flex-direction:column;justify-content:center;padding:0 24px">'
         + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{PG}", "/var/lib/postgresql") + p(f"font-size:21px;color:{SUB}", "└ 18/docker 안에 데이터베이스와 표") + '</div>')
o.append(p(f"position:absolute;left:{BX + 40}px;top:{BY + 222}px;width:250px;font-size:22px;line-height:1.45;color:{RED}", "docker rm 하면 이 폴더도 같이 지워져요", bi("rise", 2)))
o.append(cyl(BX + 177, 640, 300, 200, "pg-data", "볼륨 · 붕어빵 밖 보관함", VO, VOBG, "vw-vol", attrs=bi("rise", 3)))
o.append(line_arrow(BX + 327, 630, BX + 327, BY + 206, VO, 3))
o.append(p(f"position:absolute;left:{BX}px;top:860px;width:654px;text-align:center;font-family:{MONO};font-size:26px;font-weight:700;color:{VO}", "-v pg-data:/var/lib/postgresql", bi("rise", 3)))
o.append(f'<div{bi("rise", 4)} style="position:absolute;left:96px;top:800px;width:1020px;padding:20px 26px;border-radius:14px;background:{VOBG};border-left:6px solid {VO}">'
         + p(f"font-size:25px;line-height:1.5;color:{INK}", "18부터 자리가 바뀌었어요. 17까지는 /var/lib/postgresql/data였어요. 인터넷의 예전 글을 따라 할 때 버전을 같이 봐요.") + '</div>')
W("v-why", o, "데이터는 컨테이너 안 /var/lib/postgresql에 저장돼요. docker exec로 ls를 실행해 그 폴더를 들여다봤어요. 안에 버전 번호인 18 폴더가 있고, 그 아래 docker 폴더에 PostgreSQL이 쓰는 파일이 잔뜩 있어요. 1파트에서 env로 본 PGDATA가 바로 이 폴더예요. 데이터베이스와 표가 여기에 파일로 저장돼요. 볼륨이 없으면 이 폴더가 컨테이너 안에만 있어서, docker rm으로 컨테이너를 지울 때 같이 지워져요. 30에서 배운 이름 있는 볼륨 pg-data를 /var/lib/postgresql 자리에 붙이면 데이터가 붕어빵 밖 보관함에 저장돼요. 주의할 점이 있어요. PostgreSQL 18 이미지부터 이 자리가 바뀌었어요. 17까지는 /var/lib/postgresql/data였어요. 인터넷의 예전 글을 그대로 따라 하면 오류가 나는데, 5파트에서 실제로 봐요. ls는 두 폴더를 따로 실행했고, 두 번째 결과는 한 줄에 다섯 개씩 묶어 옮겼어요." + REAL)

o = frame("v-keep", EB4, "-v pg-data:/var/lib/postgresql을 붙이면 지웠다 켜도 남아요", C4)
vm = S("v-make")
vm = [l for l in vm if not l.startswith("shop=# \\q")]
vm_short = [vm[0], vm[1], vm[2], vm[3], "shop=# CREATE TABLE orders (…);", "CREATE TABLE"] + [l for l in vm if "INSERT" in l]
rows = [("$", P_HOME, RUNV.replace(" -p 5432:5432", " …"), {"-v pg-data:/var/lib/postgresql": f'style="color:#E3A84A"'}), ("o", D["v-run"][0]["out"][0][:12] + "…"), ("$", P_HOME, C("v-make"))] + psql_rows(vm_short) + \
       [("$", P_HOME, C("v-rm", 0)), ("o", "pg"), ("$", P_HOME, C("v-rm", 1)), ("o", "pg"), ("$", P_HOME, C("v-ls"))] + [("o", l) for l in RA("v-ls")]
t = Term(rows, 96, 214, size=17, w=1116, lh=1.45, tid="t-vk1")
vl = len(rows) - 1
o.append(t.html())
o += tag(t, vl, "볼륨은 남아 있어요", VO, 1, gap=36)
vk = S("v-kept")
vk = [l for l in vk if not l.startswith("shop=# \\q")]
while vk and not vk[-1].strip():
    vk.pop()
VL0 = next(l for l in RA("v-logs") if l.strip())
rows2 = [("$", P_HOME, "docker run -d --name pg … postgres:18"), ("o", D["v-rerun"][0]["out"][0][:12] + "…"), ("$", P_HOME, C("v-logs"))] + [("o", l) for l in rewrap([VL0], 50)] + [("d", "…"), ("$", P_HOME, C("v-kept"))] + psql_rows(vk)
t2 = Term(rows2, 1240, 214, size=17, w=584, lh=1.45, tid="t-vk2")
t2.band(len(rows2) - 3, len(rows2) - 2, order=3, color="rgba(127,209,139,.2)")
o.append(t2.html())
sk = next(i for i, r in enumerate(rows2) if "Skipping" in r[1])
o.append(underline(2, t2.sx(sk, "Skipping"), t2.sx(sk, "Skipping") + t2.sw("Skipping initialization" if "Skipping initialization" in rows2[sk][1] else "Skipping"), t2.top(sk) + t2.lp - 2, VO))
o.append(caption("새 컨테이너지만 pg-data의 데이터를 그대로 읽었어요.", max(t.y + t.h, t2.y + t2.h) + 40, 3, size=30))
W("v-keep", o, "-v pg-data:/var/lib/postgresql을 붙이면 지웠다 켜도 남아요. 왼쪽은 볼륨을 붙여 켠 pg에 shop 데이터베이스와 orders 표를 만들고 주문 두 개를 넣은 뒤, docker stop과 docker rm으로 지운 모습이에요. docker volume ls로 보면 컨테이너는 지웠지만 pg-data 볼륨은 남아 있어요. 오른쪽은 같은 명령으로 다시 켠 모습이에요. logs 첫 줄에 Skipping initialization이 보여요. 데이터 폴더에 이미 데이터베이스가 있어서 처음 준비를 건너뛰었다는 뜻이에요. -d shop으로 들어가 SELECT를 치면 주문 두 개가 그대로 나와요. 컨테이너는 새로 만들었지만 데이터는 붕어빵 밖 보관함인 pg-data에 있었기 때문이에요. 오른쪽 docker run은 왼쪽과 같은 옵션이라 가운데를 …로 줄였고, logs도 첫 줄만 옮겼어요." + REAL)

o = frame("c-yaml", EB4, "길어진 docker run을 compose.yaml에 옮겨 적어요", C4)
cl = COMPOSE.rstrip("\n").split("\n")
ed, g = editor("cy-ed", "~/cafe-pg/compose.yaml", [yaml_html(l) for l in cl], 96, 214, 900, fs=28)
o.append(ed)
src = [("--name pg 대신 서비스 이름", 1), ("postgres:18", 2), ("-e POSTGRES_PASSWORD=cafe1234", 4), ("-e POSTGRES_DB=cafe", 5), ("-p 5432:5432", 7), ("-v pg-data:/var/lib/postgresql", 9), ("이름 있는 볼륨은 여기 한 번 더", 11)]
for k, (s_, li) in enumerate(src):
    y = gcy(g, li)
    o += leader(g["left"] + g["w"] + 12, y, 1080, VO if "pg-data" in s_ or "볼륨" in s_ else PG, k + 1 if k < 6 else 6, e(s_), size=25)
W("c-yaml", o, "길어진 docker run을 compose.yaml에 옮겨 적어요. 30에서 배운 compose 그대로예요. 새 폴더 ~/cafe-pg를 만들고 그 안에 compose.yaml을 둬요. 서비스 이름은 pg, 이미지는 postgres:18이에요. -e는 environment 아래에 이름: 값 모양으로 적어요. 이번에는 POSTGRES_DB: cafe를 더해서 처음부터 cafe 데이터베이스를 만들어요. -p는 ports, -v는 volumes 자리예요. 맨 아래 volumes: 칸은 이름 있는 볼륨을 compose에서 쓸 때 한 번 더 적어 두는 자리예요. 들여쓰기는 30처럼 2칸씩이에요. 33 MySQL의 compose.yaml과 이미지, 환경 변수 이름, 포트, 볼륨 자리만 달라요.")

o = frame("c-up", EB4, "docker compose up -d로 켜고, 서비스 이름 pg로 들어가요", C4)
rows = [("$", P_CAFE, C("c-up"))] + [("o", l) for l in RA("c-up")] + [("o", ""), ("$", P_CAFE, C("c-ps"))] + [("o", l) for l in RA("c-ps")]
t = Term(rows, 96, 206, size=18, w=1728, lh=1.4, tid="t-cu")
o.append(t.html())
vi_ = next(i for i, r in enumerate(rows) if "Volume" in r[1])
o += tag(t, vi_, "폴더 이름이 앞에 붙어요", VO, 1)
cs = S("c-sql")
cs = [l for l in cs if not l.startswith("cafe=# \\q")]
while cs and not cs[-1].strip():
    cs.pop()
cs_short = ["cafe=# CREATE TABLE orders (…);", "CREATE TABLE"] + [l for l in cs if "INSERT" in l or l.startswith("INSERT")] + cs[cs.index(next(l for l in cs if l.startswith("cafe=# SELECT"))):]
rows2 = [("$", P_CAFE, C("c-sql"), {"pg": f'id="cu-svc"', "-d cafe": f'style="color:#9DC1E6"'})] + psql_rows(cs_short)
t2 = Term(rows2, 96, t.y + t.h + 20, size=18, w=1728, lh=1.4, tid="t-cu2")
o.append(t2.html())
o += tag(t2, 0, "서비스 이름 pg, POSTGRES_DB로 만든 cafe", PG, 2)
W("c-up", o, "docker compose up -d로 켜고, 서비스 이름 pg로 들어가요. ~/cafe-pg 폴더에서 up -d를 치면 네트워크, 볼륨, 컨테이너가 차례로 만들어져요. 볼륨 이름이 cafe-pg_pg-data예요. compose는 폴더 이름을 앞에 붙여서 다른 폴더의 볼륨과 겹치지 않게 해요. docker compose ps로 보면 컨테이너 이름은 cafe-pg-pg-1이에요. 긴 이름을 칠 필요 없이 docker compose exec 뒤에 서비스 이름 pg를 적으면 돼요. -d cafe로 들어가면 POSTGRES_DB로 만든 cafe 데이터베이스예요. 2파트와 같은 SQL이 그대로 돌아가요. 처음 켤 때는 1파트처럼 몇 초 기다렸다가 들어가요. CREATE TABLE의 열 목록은 앞과 같아서 …로 줄였어요." + REAL)

# =====================================================================
# part 5: errors
# =====================================================================
o = frame("x-nopw", EB5, "비밀번호 -e를 빠뜨리면 켜지자마자 꺼져요", C5)
rows = [("$", P_HOME, C("t-nopw")), ("o", idshort("t-nopw")), ("o", ""), ("$", P_HOME, C("t-nopw-ps"))] + [("o", l) for l in RA("t-nopw-ps")] + [("o", ""), ("$", P_HOME, C("t-nopw-logs"))] + \
       [("e", l) for l in RA("t-nopw-logs")[:3]] + [("d", "…")]
t = Term(rows, 96, 214, size=21, w=1728, lh=1.5, tid="t-xn")
o.append(t.html())
xi = 5
o.append(pen_box(1, round(t.sx(xi, "Exited (1)") - 8), round(t.top(xi) - 2), round(t.sw("Exited (1) 2 seconds ago") + 16), round(t.lp + 4), RED))
li_ = 8
o.append(underline(2, t.sx(li_ + 1, "POSTGRES_PASSWORD"), t.sx(li_ + 1, "POSTGRES_PASSWORD") + t.sw("POSTGRES_PASSWORD"), t.top(li_ + 1) + t.lp - 2, OR))
o.append(caption("이름 pg가 남아 있어요. docker rm pg로 지우고 -e POSTGRES_PASSWORD를 붙여 다시 켜요.", t.y + t.h + 36, 3, size=28))
W("x-nopw", o, "비밀번호 -e를 빠뜨리면 켜지자마자 꺼져요. docker run은 컨테이너 ID를 찍고 끝나서 잘 켜진 것처럼 보여요. 그런데 docker ps -a로 보면 STATUS가 Exited (1)이에요. 몇 초 만에 꺼진 거예요. docker logs pg로 이유를 보면, 데이터베이스가 아직 없는데 관리자 비밀번호가 없다고 나와요. POSTGRES_PASSWORD를 비어 있지 않은 값으로 달라는 뜻이에요. 꺼진 컨테이너도 이름 pg를 차지하고 있어서, 29에서 배운 대로 docker rm pg로 먼저 지우고 다시 켜요. logs의 아래 줄에는 비밀번호 없이 들어오게 하는 방법도 적혀 있는데, 권하지 않는다고 적혀 있으니 쓰지 않아요. logs는 앞의 세 줄만 옮겼어요." + REAL, ("p5", "자주 나는 오류"))

o = frame("x-early", EB5, "켜자마자 들어가면 아직 준비 중이라 접속이 안 돼요", C5)
rows = [("$", P_HOME, RUN), ("o", idshort("run")), ("$", P_HOME, C("early"))] + [("e", l.strip()) for l in rewrap(RA("early"), 100)]
t = Term(rows, 96, 214, size=23, w=1728, lh=1.6, tid="t-xe")
o.append(t.html())
o.append(underline(1, t.sx(3, "No such file or directory"), t.sx(3, "No such file or directory") + t.sw("No such file or directory"), t.top(3) + t.lp - 2, RED) if "No such file or directory" in rows[3][1] else "")
y2 = t.y + t.h + 40
lg = RA("logs")
last = max(i for i, l in enumerate(lg) if "ready to accept connections" in l)
rows2 = [("$", P_HOME, C("logs")), ("d", "…"), ("o", lg[next(i for i, l in enumerate(lg) if l.startswith("PostgreSQL init process complete"))]), ("d", "…"), ("o", short_log(lg[last]))]
t2 = Term(rows2, 96, y2, size=23, w=1728, lh=1.6, tid="t-xe2")
t2.band(4, order=2, color="rgba(127,209,139,.2)")
o.append(t2.html())
o += tag(t2, 4, "이 줄이 보이면 다시 들어가요", GR, 2)
W("x-early", o, "켜자마자 들어가면 아직 준비 중이라 접속이 안 돼요. docker run 바로 뒤에 psql로 들어가면 connection to server failed, No such file or directory가 나와요. 서버에 붙는 통로 파일을 못 찾았다는 뜻이에요. 1파트에서 본 것처럼 처음 켤 때는 데이터 파일을 만들고 준비용 서버를 켰다 끄느라 몇 초 걸려요. 그동안에는 들어갈 서버가 없어요. docker logs pg를 보고 init process complete 다음의 ready to accept connections가 나오면 다시 들어가요. 33 MySQL의 ERROR 2002와 같은 상황이에요. 볼륨에 이미 데이터가 있으면 준비가 짧아서 금방 돼요." + REAL)

o = frame("x-port", EB5, "5432번을 이미 쓰고 있으면 port is already allocated가 나요", C5)
pt = RA("u-port", 0)
rows = [("$", P_HOME, C("u-port", 0)), ("o", pt[0][:12] + "…")] + [("e", l) for l in rewrap(pt[1:], 110)] + [("o", ""), ("$", P_HOME, C("u-port", 1))] + [("o", l) for l in RA("u-port", 1)]
t = Term(rows, 96, 214, size=19, w=1728, lh=1.5, tid="t-xp")
o.append(t.html())
ei = next(i for i, r in enumerate(rows) if "port is already allocated" in r[1])
o.append(underline(1, t.sx(ei, "port is already allocated"), t.sx(ei, "port is already allocated") + t.sw("port is already allocated"), t.top(ei) + t.lp - 2, RED))
pgi = next(i for i, r in enumerate(rows) if r[1].rstrip().endswith("   pg") and "5432->5432" in r[1])
t_ = t
o.append(pen_box(2, round(t.sx(pgi, "0.0.0.0:5432") - 8), round(t.top(pgi) - 2), round(t.sw("0.0.0.0:5432->5432/tcp   pg") + 16), round(t.lp + 4), OR))
o.append(caption("앞의 pg가 5432번을 쓰는 중이에요. 하나를 끄거나, 내 컴퓨터 쪽 번호만 -p 5433:5432로 바꿔요.", t.y + t.h + 36, 3, size=28))
W("x-port", o, "5432번을 이미 쓰고 있으면 port is already allocated가 나요. 29에서 본 포트 겹침이 PostgreSQL에서도 나요. pg가 5432번을 쓰는 중에 pg3을 같은 포트로 켜려고 하니, 컨테이너는 만들어졌지만 켜지지 못하고 오류가 났어요. docker ps -a로 보면 pg3은 Created에 머물러 있고, 5432번은 pg가 쓰고 있어요. PostgreSQL을 컴퓨터에 직접 설치해 둔 사람도 같은 오류를 만나요. 설치한 PostgreSQL이 5432번을 쓰고 있어서예요. 안 쓰는 쪽을 끄거나, 둘 다 써야 하면 3파트의 pg2처럼 -p 5433:5432로 내 컴퓨터 쪽 번호만 바꿔요. 컨테이너 안의 PostgreSQL은 그대로 5432에서 기다려요. Created로 남은 pg3은 docker rm pg3으로 지워요. 긴 오류 줄은 화면 폭에 맞춰 줄만 바꿨어요." + REAL)

o = frame("x-sql", EB5, "psql에서 자주 하는 실수 두 가지예요", C5)
ss = S("s-semi")
ss = [l for l in ss if not l.startswith("shop=# \\q")]
while ss and not ss[-1].strip():
    ss.pop()
rows = psql_rows(ss)
t = Term(rows, 96, 280, size=26, w=840, lh=1.6, tid="t-xs1")
o.append(p(f"position:absolute;left:96px;top:222px;font-size:28px;font-weight:700;color:{INK}", "1. 세미콜론을 빠뜨렸어요"))
o.append(t.html())
o.append(ring(1, t.tx - 10, t.top(1) + 9, t.sw("shop-#") + 20, t.lp - 16, OR, width=4))
o.append(p(f"position:absolute;left:96px;top:{t.y + t.h + 26}px;width:840px;font-size:25px;line-height:1.5;color:{INK}", "=#가 -#로 바뀌면 문장이 아직 안 끝났다는 뜻이에요. ;만 치고 Enter를 눌러요.", bi("rise", 1)))
ty = S("s-typo")
ty = [l for l in ty if not l.startswith("postgres=# \\q")]
while ty and not ty[-1].strip():
    ty.pop()
rows2 = psql_rows(rewrap(ty, 44))
t2 = Term(rows2, 984, 280, size=26, w=840, lh=1.6, tid="t-xs2")
o.append(p(f"position:absolute;left:984px;top:222px;font-size:28px;font-weight:700;color:{INK}", "2. 데이터베이스 이름을 잘못 썼어요"))
o.append(t2.html())
kp = next(i for i, r in enumerate(rows2) if r[1].startswith("Previous connection kept"))
o.append(underline(2, t2.tx, t2.tx + t2.sw("Previous connection kept"), t2.top(kp) + t2.lp - 2, OR))
o.append(p(f"position:absolute;left:984px;top:{t2.y + t2.h + 26}px;width:840px;font-size:25px;line-height:1.5;color:{INK}", "없는 이름이라 못 옮기고, 원래 있던 postgres에 그대로 남아요. \\l로 이름을 보고 다시 쳐요.", bi("rise", 2)))
W("x-sql", o, "psql에서 자주 하는 실수 두 가지예요. 왼쪽은 SELECT 끝의 세미콜론을 빠뜨리고 Enter를 친 모습이에요. 실행되지 않고 표시가 shop=#에서 shop-#로 바뀌었어요. 문장이 아직 안 끝났으니 더 치라는 뜻이에요. 세미콜론만 치고 Enter를 누르면 앞 줄과 이어서 실행돼요. 33 MySQL에서 화살표 표시가 나온 것과 같아요. 오른쪽은 백슬래시 c 뒤에 shop을 shopp로 잘못 친 모습이에요. database shopp does not exist, 그런 데이터베이스가 없다는 오류가 나고, Previous connection kept, 원래 연결을 그대로 둔다고 나와요. 표시가 여전히 postgres=#예요. 백슬래시 l로 이름을 확인하고 다시 쳐요. 백슬래시 명령에는 세미콜론이 필요 없다는 것도 같이 기억해요. 긴 오류 줄은 화면 폭에 맞춰 줄만 바꿨어요." + REAL)

o = frame("x-old", EB5, "예전 글처럼 /var/lib/postgresql/data에 붙이면 18은 켜지지 않아요", C5)
OLDV = "-v old-data:/var/lib/postgresql/data"
rows = [("$", P_HOME, C("t-old"), {OLDV: 'style="color:#FF9C94"'}), ("o", idshort("t-old")), ("$", P_HOME, C("t-old-ps"))] + [("o", l) for l in RA("t-old-ps")]
t = Term(rows, 96, 214, size=19, w=1728, lh=1.5, tid="t-xo1")
o.append(t.html())
oi = 4
o.append(pen_box(1, round(t.sx(oi, "Exited (1)") - 8), round(t.top(oi) - 2), round(t.sw("Exited (1) 3 seconds ago") + 16), round(t.lp + 4), RED))
lg = RA("t-old-logs")
keep = [lg[0], "d"] + [l for l in lg if "/var/lib/postgresql/data (unused" in l] + ["d"] + [l for l in lg if l.strip().startswith("The suggested container") or l.strip().startswith("at /var/lib/postgresql which")]
rows2 = [("$", P_HOME, C("t-old-logs"))] + [("d", "…") if l == "d" else ("e", l.rstrip()) for l in keep]
t2 = Term(rows2, 96, t.y + t.h + 30, size=21, w=1180, lh=1.5, tid="t-xo2")
o.append(t2.html())
si = next(i for i, r in enumerate(rows2) if r[1].strip().startswith("The suggested"))
o.append(zoom(2, t2.x, round(t2.top(si) - 10), t2.w, round(t2.lp * 2 + 20), pad=60, max_scale=1.8))
o.append(zoom_off(3))
FX = 1330
fy = t2.y
o.append(p(f"position:absolute;left:{FX}px;top:{fy}px;font-size:24px;font-weight:700;color:{RED}", "17까지 쓰던 자리", bi("rise", 3)))
o.append(p(f"position:absolute;left:{FX}px;top:{fy + 40}px;font-family:{MONO};font-size:24px;font-weight:700;color:{INK};text-decoration:line-through;text-decoration-color:{RED}", "/var/lib/postgresql/data", bi("rise", 3)))
o.append(p(f"position:absolute;left:{FX}px;top:{fy + 120}px;font-size:24px;font-weight:700;color:{GR}", "18부터 붙이는 자리", bi("rise", 4)))
o.append(p(f"position:absolute;left:{FX}px;top:{fy + 160}px;font-family:{MONO};font-size:24px;font-weight:700;color:{INK}", "/var/lib/postgresql", bi("rise", 4)))
o.append(p(f"position:absolute;left:{FX}px;top:{fy + 230}px;width:494px;font-size:24px;line-height:1.5;color:{SUB}", f'docker rm pg로 지우고 <span style="font-family:{MONO};white-space:nowrap">-v pg-data:/var/lib/postgresql</span>로 다시 켜요.', bi("rise", 4)))
W("x-old", o, "예전 글처럼 /var/lib/postgresql/data에 붙이면 18은 켜지지 않아요. 인터넷의 PostgreSQL 컨테이너 글은 대부분 17 이전 기준이라 볼륨을 /var/lib/postgresql/data에 붙여요. 같은 명령을 postgres:18에 치면 docker run은 ID를 찍고 끝나지만, docker ps -a에서 Exited (1)로 바로 꺼진 게 보여요. docker logs pg의 첫 줄이 Error: in 18+예요. 18부터는 데이터를 버전 번호 폴더에 넣도록 바뀌었다는 설명이에요. 아래쪽에 /var/lib/postgresql/data에 볼륨이 붙어 있는데 쓰지 않는다고 나와요. 마지막 문단이 고치는 법이에요. 18부터는 /var/lib/postgresql 한 곳에 붙이라고 알려 줘요. 꺼진 pg는 docker rm pg로 지우고, 4파트처럼 -v pg-data:/var/lib/postgresql로 다시 켜요. 예전 글을 따라 할 때는 이미지 버전을 먼저 봐요. logs는 길어서 필요한 줄만 옮겼어요." + REAL)

o = frame("x-trap", EB5, "볼륨에 데이터가 있으면 바꾼 비밀번호는 무시돼요", C5)
NEWRUN = "docker run -d --name pg -e POSTGRES_PASSWORD=new5678 …"
nl = [l for l in RA("t-newpw-logs") if l.strip()]
rows = [("$", P_HOME, C("t-newpw-rm", 0)), ("o", "pg"), ("$", P_HOME, C("t-newpw-rm", 1)), ("o", "pg"),
        ("$", P_HOME, NEWRUN, {"new5678": 'style="color:#F2C46D"'}), ("o", idshort("t-newpw")), ("$", P_HOME, C("t-newpw-logs"))] + [("o", l) for l in rewrap([nl[0]], 70)] + [("d", "…")]
t = Term(rows, 96, 214, size=19, w=900, lh=1.5, tid="t-xt1")
o.append(t.html())
o += tag(t, 4, "볼륨은 그대로", VO, None, gap=24)
ki = 7
t.band(ki, ki + len(rewrap([nl[0]], 70)) - 1, order=1, color="rgba(242,196,109,.22)")
fi_ = RA("t-newpw-in")
rows2 = [("$", P_HOME, "docker run … psql -h host.docker.internal -U postgres"), ("o", fi_[0])] + [("e", l) for l in rewrap(fi_[1:], 62)]
t2 = Term(rows2, 1030, 214, size=19, w=794, lh=1.5, tid="t-xt2")
o.append(t2.html())
o += tag(t2, 1, "new5678", RED, 2, gap=36)
ol = [l.rstrip() for l in RA("t-newpw-old")]
ol = [l for l in ol if not l.startswith("psql (18") and not l.startswith('Type "help"') and l.strip() and not l.startswith("shop=# \\q")]
rows3 = [("$", P_HOME, "docker run … -U postgres -d shop")] + psql_rows(ol)
t3 = Term(rows3, 1030, t2.y + t2.h + 30, size=19, w=794, lh=1.5, tid="t-xt3")
o.append(t3.html())
o += tag(t3, 1, "처음 비밀번호 cafe1234", GR, 3, gap=36)
yb = max(t.y + t.h, t3.y + t3.h) + 40
o.append(f'<div{bi("rise", 4)} style="position:absolute;left:96px;top:{yb}px;width:1728px;padding:22px 28px;border-radius:14px;background:{VOBG};border-left:6px solid {VO}">'
         + p(f"font-size:27px;font-weight:700;line-height:1.5;color:{INK}", "POSTGRES_로 시작하는 -e는 데이터 폴더가 비어 있을 때 한 번만 읽어요.")
         + p(f"font-size:24px;line-height:1.5;color:{SUB}", "처음부터 다시 하려면 docker volume rm pg-data로 볼륨까지 지워요. 넣어 둔 데이터도 같이 지워져요.") + '</div>')
W("x-trap", o, "볼륨에 데이터가 있으면 바꾼 비밀번호는 무시돼요. 4파트의 pg를 지우고, 같은 pg-data 볼륨을 붙인 채 POSTGRES_PASSWORD만 new5678로 바꿔 다시 켰어요. logs에 Skipping initialization이 보여요. 데이터 폴더에 이미 데이터베이스가 있어서 처음 준비를 건너뛰었다는 뜻이에요. 비밀번호를 정하는 일도 그 처음 준비 안에 있어서, 이번 -e는 쓰이지 않았어요. 오른쪽 위처럼 밖에서 new5678로 들어가면 password authentication failed가 나요. 처음에 정한 cafe1234로 들어가면 shop의 주문 두 개가 그대로 보여요. POSTGRES_USER, POSTGRES_DB도 똑같이 처음 한 번만 읽어요. 33 MySQL의 MYSQL_ROOT_PASSWORD도 같은 함정이 있었어요. 처음부터 다시 하고 싶으면 docker volume rm pg-data로 볼륨까지 지워요. 넣어 둔 데이터도 같이 사라지니 연습용일 때만 해요. 비밀번호를 SQL로 바꾸는 방법도 있지만 이 챕터에서는 다루지 않아요. 오른쪽 접속 명령은 3파트와 같아서 앞부분을 …로 줄였어요." + REAL)

# =====================================================================
# part 6: real tasks
# =====================================================================
o = frame("e-day", EB6, "compose down 하고 다음 날 up 해도 어제 주문이 남아 있어요", C6)
def cz(l):
    return re.sub(r" {4,}", "   ", l)


rows = [("$", P_CAFE, C("c-down"))] + [("o", cz(l)) for l in RA("c-down")] + [("$", P_CAFE, C("c-vol"))] + [("o", l) for l in RA("c-vol")]
t = Term(rows, 96, 270, size=19, w=840, lh=1.5, tid="t-ed1")
o.append(p(f"position:absolute;left:96px;top:214px;font-size:28px;font-weight:700;color:{INK}", "1. 문 닫을 때", bi("rise", 1)))
o.append(t.html())
vli = len(rows) - 1
t.band(vli, order=1, color="rgba(227,168,74,.22)")
o += tag(t, vli, "볼륨은 남아요", VO, 1, gap=36)
es = [l.rstrip() for l in RA("e-sql")]
es = [l for l in es if not l.startswith("psql (18") and not l.startswith('Type "help"') and l.strip() and not l.startswith("cafe=# \\q")]
rows2 = [("$", P_CAFE, C("e-up"))] + [("o", cz(l)) for l in RA("e-up")] + [("$", P_CAFE, C("e-sql"))] + psql_rows(es)
t2 = Term(rows2, 984, 270, size=19, w=840, lh=1.5, tid="t-ed2")
o.append(p(f"position:absolute;left:984px;top:214px;font-size:28px;font-weight:700;color:{INK}", "2. 다음 날 문 열 때", bi("rise", 2)))
o.append(t2.html())
r3 = next(i for i, r in enumerate(rows2) if "cake" in r[1] and "|" in r[1])
r1 = next(i for i, r in enumerate(rows2) if "latte" in r[1] and "|" in r[1])
o.append(lspot(3, t2.x + 2, t2.y + t2.BAR, t2.w - 4, t2.h - t2.BAR - 2, t2.top(r1) - 4, t2.lp * 2 + 8, bg=T_BG, bar=GR))
o.append(lspot(4, t2.x + 2, t2.y + t2.BAR, t2.w - 4, t2.h - t2.BAR - 2, t2.top(r3) - 4, t2.lp + 8, bg=T_BG, bar=OR))
o.append(lspot_off(5))
yb = max(t.y + t.h, t2.y + t2.h) + 44
o.append(caption("down은 컨테이너와 네트워크만 지워요. 볼륨을 지우는 down -v는 연습을 끝낼 때만 쳐요.", yb, 5, size=28))
W("e-day", o, "compose down 하고 다음 날 up 해도 어제 주문이 남아 있어요. 카페 문을 닫는다고 생각해 봐요. 4파트에서 주문 두 개를 넣은 ~/cafe-pg에서 docker compose down을 치면 컨테이너와 네트워크가 지워져요. docker volume ls로 보면 cafe-pg_pg-data 볼륨은 그대로 남아 있어요. 다음 날 docker compose up -d로 다시 열고 들어가서, 오늘 첫 주문인 케이크 하나를 넣었어요. SELECT로 보면 어제 넣은 1번, 2번 주문 아래에 오늘 넣은 3번이 붙어 있어요. 볼륨을 지우는 docker compose down -v는 연습을 다 끝내고 정리할 때만 쳐요. 데이터가 같이 사라져요. compose 진행 줄은 가운데 빈칸을 줄였어요." + REAL, ("p6", "실제 상황 예제"))

o = frame("e-init", EB6, "init 폴더에 SQL 파일을 두면 처음 켤 때 메뉴가 들어가요", C6)
ml = MENU_SQL.rstrip("\n").split("\n")
ed, g = editor("ei-sql", "~/cafe-pg/init/menu.sql", [e(l) for l in ml], 96, 214, 1000, fs=19, color=GR)
o.append(ed)
cl = COMPOSE_INIT.rstrip("\n").split("\n")
ii = next(i for i, l in enumerate(cl) if "docker-entrypoint-initdb.d" in l)
ed2, g2 = editor("ei-yaml", "~/cafe-pg/compose.yaml (volumes 부분)", [yaml_html(l) for l in cl[ii - 2:ii + 1]], 96, g["top"] + g["h"] + 26, 1000, fs=21, start=ii - 1)
o.append(ed2)
o.append(lband(1, g2, 2, color=GR))
lgi = [l for l in RA("i-logs")]
ri = next(i for i, l in enumerate(lgi) if "running /docker-entrypoint-initdb.d" in l)
logrows = [("$", P_CAFE, C("i-up")), ("d", "…"), ("$", P_CAFE, C("i-logs")), ("d", "…")] + [("o", l.replace("/usr/local/bin/docker-entrypoint.sh: ", "… ")) for l in lgi[ri:ri + 4]]
t = Term(logrows, 96, g2["top"] + g2["h"] + 26, size=19, w=1000, lh=1.5, tid="t-ei1")
o.append(t.html())
t.band(4, order=2, color="rgba(127,209,139,.2)")
isq = [l.rstrip() for l in RA("i-sql")]
isq = [l for l in isq if not l.startswith("psql (18") and not l.startswith('Type "help"') and l.strip() and not l.startswith("cafe=# \\q")]
rows2 = [("$", P_CAFE, C("i-sql"))] + psql_rows(isq)
t2 = Term(rows2, 1140, 214, size=17, w=684, lh=1.5, tid="t-ei2")
o.append(t2.html())
mi = next(i for i, r in enumerate(rows2) if "americano" in r[1] and "4000" in r[1])
o.append(link(3, t.x + t.w + 6, t.top(4) + t.lp / 2, t2.x - 6, t2.top(mi) + t2.lp / 2, GR))
o.append(caption("볼륨이 비어 있을 때만 실행해요. 다시 넣으려면 down -v 뒤에 up -d예요.", t2.y + t2.h + 40, 4, left=1140, width=684, size=27))
W("e-init", o, "init 폴더에 SQL 파일을 두면 처음 켤 때 메뉴가 들어가요. 매번 메뉴 표를 손으로 만들기는 번거로워요. ~/cafe-pg 안에 init 폴더를 만들고 menu.sql에 CREATE TABLE과 INSERT 세 줄을 적어 뒀어요. compose.yaml의 volumes에 ./init:/docker-entrypoint-initdb.d 한 줄을 더해요. 30에서 배운 내 폴더 연결이에요. 앞 장 끝에서 down -v로 볼륨을 지웠으니 데이터 폴더가 비어 있어요. up -d로 켜고 logs를 보면 running docker-entrypoint-initdb.d/menu.sql 다음에 CREATE TABLE과 INSERT가 찍혀요. POSTGRES_DB로 정한 cafe 안에 실행돼요. 들어가서 백슬래시 dt와 SELECT를 치면 메뉴 세 개가 들어 있어요. 이 폴더도 5파트에서 본 비밀번호처럼 데이터 폴더가 비어 있을 때 처음 한 번만 실행해요. menu.sql을 고쳐서 다시 넣고 싶으면 down -v로 볼륨을 지우고 up -d를 쳐요. 33 MySQL에서도 같은 폴더 이름을 썼어요. logs는 필요한 줄만 옮겼고, 앞의 긴 경로는 …로 줄였어요." + REAL)

# =====================================================================
# wrap-up: MySQL comparison, trouble, cheatsheet
# =====================================================================
o = frame("m-cmp", "정리", "33 MySQL과 컨테이너 쪽에서 다른 점이에요", INK)
cmp_rows = [("이미지", "mysql:8.4", "postgres:18", 1),
            ("관리자", "root", "postgres", 1),
            ("관리자 비밀번호", "MYSQL_ROOT_PASSWORD", "POSTGRES_PASSWORD", 1),
            ("처음 만들 DB", "MYSQL_DATABASE", "POSTGRES_DB", 1),
            ("앱 계정 -e", "MYSQL_USER: 일반 계정을 하나 더", "POSTGRES_USER: 관리자 이름이 바뀌어요", 2),
            ("포트", "3306", "5432", 3),
            ("데이터 자리", "/var/lib/mysql", "/var/lib/postgresql", 3),
            ("들어가기", "docker exec -it db mysql -u root -p", "docker exec -it pg psql -U postgres", 3),
            ("안에서 비밀번호", "물어요", "안 물어요", 3)]
X0, X1, X2, RH = 96, 420, 1140, 78
o.append(p(f"position:absolute;left:{X1}px;top:210px;font-size:28px;font-weight:700;color:{MY}", "33 MySQL"))
o.append(p(f"position:absolute;left:{X2}px;top:210px;font-size:28px;font-weight:700;color:{PG}", "34 PostgreSQL"))
for i, (k, a_, b_, od) in enumerate(cmp_rows):
    y = 262 + i * RH
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:1px;background:{LINE}"></div>')
    ra_ = bi("rise", od) + DELAY((i % 4) * 70)
    o.append(p(f"position:absolute;left:{X0}px;top:{y + 20}px;width:310px;font-size:25px;font-weight:700;color:{SUB}", e(k), ra_))
    for x_, v_, c_ in ((X1, a_, MY), (X2, b_, PG)):
        mono = all(ord(ch) < 0x1100 for ch in v_)
        hi = od == 2
        st = f"font-family:{MONO};font-size:23px;" if mono else ("font-size:25px;" if ":" not in v_ else "")
        if ":" in v_ and not mono:
            name, rest = v_.split(": ", 1)
            body = f'<span style="font-family:{MONO};font-size:23px;font-weight:700">{e(name)}</span> <span style="font-size:24px;color:{SUB}">{e(rest)}</span>'
        else:
            body = e(v_)
        o.append(p(f"position:absolute;left:{x_}px;top:{y + 20}px;width:680px;{st}font-weight:700;color:{RED if hi and x_ == X2 else INK};white-space:nowrap", body, ra_))
o.append(f'<div style="position:absolute;left:96px;top:{262 + len(cmp_rows) * RH}px;width:1728px;height:1px;background:{LINE}"></div>')
o.append(f'<div{bi("fade", 2)} style="position:absolute;left:88px;top:{262 + 4 * RH + 4}px;width:1744px;height:{RH - 8}px;border-radius:10px;background:#A3313112"></div>')
W("m-cmp", o, "33 MySQL과 컨테이너 쪽에서 다른 점이에요. 이미지와 관리자 이름이 달라요. MySQL은 root, PostgreSQL은 postgres예요. 관리자 비밀번호와 처음 만들 데이터베이스는 -e 이름만 다르고 하는 일은 같아요. 가장 헷갈리는 줄이 앱 계정이에요. MYSQL_USER는 관리자 root 옆에 일반 계정을 하나 더 만들어요. POSTGRES_USER는 관리자 이름 자체를 바꿔서, 그 계정이 관리자가 되고 postgres 계정은 생기지 않아요. 포트는 3306과 5432, 데이터 자리는 /var/lib/mysql과 /var/lib/postgresql이에요. 들어갈 때는 mysql 대신 psql을 쓰고, -u 대신 대문자 -U를 써요. MySQL은 컨테이너 안에서도 비밀번호를 물었지만 PostgreSQL 공식 이미지는 안에서 오는 접속을 묻지 않고 들여보내요. 밖에서 붙을 때는 둘 다 비밀번호가 필요해요.", ("cmp", "MySQL과 비교"))

o = frame("m-cmd", "정리", "SQL은 같고, 목록을 보는 명령만 달라요", INK)
same = ["CREATE DATABASE shop;", "CREATE TABLE orders (…);", "INSERT INTO orders VALUES (…);", "SELECT * FROM orders;", "DROP TABLE orders;", "DROP DATABASE shop;"]
o.append(f'<div id="mc-same" style="position:absolute;left:96px;top:214px;width:560px;height:560px;border-radius:20px;background:{CARD};box-shadow:{SHADOW};padding:30px 34px">'
         + p(f"font-size:28px;font-weight:700;color:{GR};margin-bottom:22px", "둘 다 똑같이 쳐요")
         + "".join(p(f"font-family:{MONO};font-size:22px;font-weight:700;line-height:2.2;color:{INK};white-space:nowrap", e(s_)) for s_ in same)
         + p(f"font-size:23px;line-height:1.5;color:{SUB};margin-top:26px", "문장 끝 ;도 같아요.") + '</div>')
diff = [("데이터베이스 목록", "SHOW DATABASES;", "\\l"), ("다른 데이터베이스로", "USE shop;", "\\c shop"), ("표 목록", "SHOW TABLES;", "\\dt"),
        ("표 모양", "DESCRIBE orders;", "\\d orders"), ("나가기", "exit", "\\q"), ("한 문장만 실행", 'mysql … -e "…"', 'psql … -c "…"'), ("덜 끝난 문장 표시", "->", "-#")]
DX, DA, DB_ = 720, 1060, 1480
o.append(p(f"position:absolute;left:{DA}px;top:214px;font-size:26px;font-weight:700;color:{MY}", "MySQL"))
o.append(p(f"position:absolute;left:{DB_}px;top:214px;font-size:26px;font-weight:700;color:{PG}", "PostgreSQL"))
for i, (k, a_, b_) in enumerate(diff):
    y = 264 + i * 84
    o.append(f'<div style="position:absolute;left:{DX}px;top:{y}px;width:1104px;height:1px;background:{LINE}"></div>')
    o.append(p(f"position:absolute;left:{DX}px;top:{y + 26}px;width:330px;font-size:24px;font-weight:700;color:{SUB}", e(k)))
    o.append(p(f"position:absolute;left:{DA}px;top:{y + 24}px;width:400px;font-family:{MONO};font-size:25px;font-weight:700;color:{INK};white-space:nowrap", e(a_)))
    o.append(p(f"position:absolute;left:{DB_}px;top:{y + 24}px;width:344px;font-family:{MONO};font-size:25px;font-weight:700;color:{PG};white-space:nowrap", e(b_), bi("pop", 2) + DELAY(i * 90)))
o.append(f'<div style="position:absolute;left:{DX}px;top:{264 + len(diff) * 84}px;width:1104px;height:1px;background:{LINE}"></div>')
o.append(pulse(1, "mc-same"))
o.append(caption("PostgreSQL의 목록 명령은 \\로 시작하고 ;가 없어요.", 264 + len(diff) * 84 + 36, 3, left=DX, width=1104, size=28))
W("m-cmd", o, "SQL은 같고, 목록을 보는 명령만 달라요. 왼쪽 문장들은 33과 34에서 글자 하나 다르지 않게 쳤어요. CREATE DATABASE, CREATE TABLE, INSERT, SELECT, DROP은 SQL이라는 같은 언어라서 그래요. 끝에 세미콜론을 붙이는 것도 같아요. 다른 건 오른쪽 표예요. MySQL은 SHOW DATABASES, USE처럼 SQL 모양의 명령을 쓰고, PostgreSQL의 psql은 백슬래시 l, 백슬래시 c처럼 백슬래시로 시작하는 짧은 명령을 써요. 백슬래시 명령은 psql이 직접 처리해서 세미콜론이 없어요. 한 문장만 실행할 때 MySQL은 -e, psql은 -c예요. 문장이 덜 끝났을 때 MySQL은 화살표, psql은 -#를 보여 줘요. 두 데이터베이스를 오갈 때 이 표만 기억하면 돼요.")

o = frame("trouble", "정리", "막히면 이렇게 풀어요", RED)
tr = [("connection to server on socket … failed", "켜는 중이라 아직 서버가 없어요", "logs에서 ready 보고 다시"),
      ("password authentication failed", "비밀번호가 틀렸거나 볼륨의 처음 비밀번호예요", "처음 정한 비밀번호로"),
      ("Exited (1), POSTGRES_PASSWORD", "-e POSTGRES_PASSWORD가 빠졌어요", "docker rm pg 뒤 -e 붙이기"),
      ("Error: in 18+", "17까지 쓰던 /var/lib/postgresql/data에 붙였어요", "-v pg-data:/var/lib/postgresql"),
      ("port is already allocated", "5432번을 다른 것이 쓰고 있어요", "하나 끄거나 -p 5433:5432"),
      ("permission denied to create database", "일반 계정은 데이터베이스를 못 만들어요", "-U postgres로 들어가기"),
      ("표시가 -#로 바뀜", "문장 끝 ;가 빠졌어요", ";만 치고 Enter")]
o.append(p(f"position:absolute;left:96px;top:214px;font-size:24px;font-weight:700;color:{GRAY}", "이런 글이 보이면"))
o.append(p(f"position:absolute;left:1300px;top:214px;font-size:24px;font-weight:700;color:{GRAY}", "이렇게 해요"))
for i, (q, a_, c_) in enumerate(tr):
    y = 262 + i * 94
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:1px;background:{LINE}"></div>')
    ra_ = bi("rise", 1) + DELAY(i * 70)
    mono = not any(0xAC00 <= ord(ch) <= 0xD7A3 for ch in q)
    o.append(p(f"position:absolute;left:96px;top:{y + 12}px;width:1180px;{'font-family:' + MONO + ';font-size:24px;' if mono else 'font-size:25px;'}font-weight:700;color:{RED};white-space:nowrap", e(q), ra_))
    o.append(p(f"position:absolute;left:96px;top:{y + 54}px;width:1180px;font-size:23px;color:{SUB}", e(a_), ra_))
    mono2 = c_.startswith("-") or c_.startswith("docker")
    o.append(p(f"position:absolute;left:1300px;top:{y + 32}px;width:524px;{'font-family:' + MONO + ';font-size:23px;' if mono2 else 'font-size:25px;'}font-weight:700;color:{INK};white-space:nowrap", e(c_), ra_))
o.append(f'<div style="position:absolute;left:96px;top:{262 + len(tr) * 94}px;width:1728px;height:1px;background:{LINE}"></div>')
o.append(caption("무엇이든 막히면 docker ps -a로 켜져 있는지 보고, docker logs pg를 먼저 읽어요.", 262 + len(tr) * 94 + 30, 2, size=28))
W("trouble", o, "오늘 만난 오류를 모았어요. connection to server on socket은 켜는 중이라 아직 서버가 없다는 뜻이에요. logs에서 ready to accept connections를 보고 다시 들어가요. password authentication failed는 비밀번호가 틀렸다는 뜻인데, 볼륨을 다시 쓰고 있다면 처음 켤 때 정한 비밀번호가 맞는 비밀번호예요. 켜자마자 Exited (1)이 되면 logs를 봐요. POSTGRES_PASSWORD가 보이면 -e가 빠진 거고, Error: in 18+가 보이면 예전 자리에 볼륨을 붙인 거예요. 5432 포트 겹침은 29에서 본 것과 같아요. 일반 계정으로 데이터베이스를 만들려고 하면 permission denied가 나요. 표시가 -#로 바뀌면 세미콜론만 치면 돼요. 무엇이든 막히면 docker ps -a와 docker logs pg부터 봐요.", ("trouble", "막힐 때"))

o = frame("cheatsheet", "정리", "한 장 요약", INK)
groups = [("켜고 들어가기", PG, [("docker run -d --name pg -e POSTGRES_PASSWORD=… -p 5432:5432", "관리자 비밀번호를 주고 켜기"), ("docker logs pg", "ready 두 번 보기"), ("docker exec -it pg psql -U postgres", "관리자로 들어가기"), ("-d shop / -c \"…\"", "데이터베이스 고르기 / 한 문장만")]),
          ("psql 안에서", GR, [("\\l  \\c shop", "목록 보기 / 옮기기"), ("\\dt  \\d orders", "표 목록 / 표 모양"), ("\\du", "계정 목록"), ("\\q", "나가기")]),
          ("데이터 지키기", VO, [("-v pg-data:/var/lib/postgresql", "18부터 이 자리"), ("docker compose up -d / down", "볼륨은 남아요"), ("docker compose down -v", "볼륨까지 지우기"), ("./init:/docker-entrypoint-initdb.d", "처음 켤 때 SQL 실행")])]
GW = [640, 460, 540]
gx_ = [96, 96 + 640 + 50, 96 + 640 + 50 + 460 + 50]
for i, (t_, c, rows) in enumerate(groups):
    x = gx_[i]
    o.append(p(f"position:absolute;left:{x}px;top:220px;font-size:30px;font-weight:700;color:{c}", e(t_)))
    o.append(f'<div style="position:absolute;left:{x}px;top:270px;width:{GW[i]}px;height:3px;background:{c}"></div>')
    for j, (k, d_) in enumerate(rows):
        y = 296 + j * 120
        o.append(p(f"position:absolute;left:{x}px;top:{y}px;width:{GW[i]}px;font-family:{MONO};font-size:{17 if len(k) > 40 else 21}px;font-weight:700;color:{INK};white-space:nowrap", e(k)))
        o.append(p(f"position:absolute;left:{x}px;top:{y + 42}px;width:{GW[i]}px;font-size:23px;color:{SUB}", e(d_)))
o.append(caption("SQL은 MySQL과 같아요. 목록 명령과 계정, 데이터 자리만 챙기면 돼요.", 820, None, size=32))
o.append(caption("나중에는 파이썬 코드에서 이 데이터베이스에 붙어 주문을 넣고 꺼내 봐요.", 880, None, size=28, color=SUB))
W("cheatsheet", o, "오늘 쓴 것을 세 묶음으로 모았어요. 왼쪽은 켜고 들어가기예요. docker run에 POSTGRES_PASSWORD를 꼭 주고, logs에서 ready를 본 뒤 docker exec -it pg psql -U postgres로 들어가요. 가운데는 psql 안에서 쓰는 백슬래시 명령이에요. 오른쪽은 데이터를 지키는 방법이에요. 18부터는 볼륨을 /var/lib/postgresql에 붙여요. compose down으로는 볼륨이 남고, down -v를 쳐야 볼륨까지 지워져요. init 폴더의 SQL 파일은 처음 켤 때 한 번 실행돼요. SQL 문장은 33 MySQL과 같으니, 목록 명령과 계정, 데이터 자리만 챙기면 돼요. 나중에는 파이썬 코드에서 이 데이터베이스에 붙어 볼 거예요.")

# =====================================================================
# toc
# =====================================================================
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
PL = [(C1, EB1[3:], "pull, run, -e, logs, psql로 들어가기", "r-pull", "r-psql"),
      (C2, EB2[3:], "CREATE DATABASE, \\c, \\l, CREATE TABLE, \\dt, \\d, INSERT, SELECT, DROP", "s-meta", "s-drop"),
      (C3, EB3[3:], "postgres와 일반 계정, POSTGRES_USER, bash로, 밖에서 비밀번호, -c 한 문장", "u-roles", "a-oneshot"),
      (C4, EB4[3:], "지우면 사라지는 표, /var/lib/postgresql, compose.yaml", "v-gone", "c-up"),
      (C5, EB5[3:], "비밀번호 빠짐, 너무 빨리 접속, 5432 겹침, 세미콜론, 18의 볼륨 자리, 남은 볼륨", "x-nopw", "x-trap"),
      (C6, EB6[3:], "다음 날에도 남는 주문, init 폴더로 메뉴 채우기", "e-day", "e-init")]
plist = [x for x in PL if x[3] in page and x[4] in page]
o = frame("toc", "", "오늘의 순서", INK)
for i, (c, h, s_, a, b) in enumerate(plist):
    y = 214 + i * 122
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:1px;background:{LINE}"></div>')
    o.append(p(f"position:absolute;left:96px;top:{y + 22}px;width:80px;font-size:48px;font-weight:900;line-height:1.5;color:{c}", str(i + 1)))
    o.append(p(f"position:absolute;left:190px;top:{y + 18}px;font-size:34px;font-weight:700;color:{INK}", e(h)))
    o.append(p(f"position:absolute;left:190px;top:{y + 70}px;font-size:22px;color:{SUB}", e(s_)))
    o.append(p(f"position:absolute;left:1524px;top:{y + 40}px;width:300px;text-align:right;font-size:28px;font-weight:700;color:{GRAY}", f"{page[a]}–{page[b]}쪽"))
o.append(f'<div style="position:absolute;left:96px;top:{214 + len(plist) * 122}px;width:1728px;height:1px;background:{LINE}"></div>')
if "m-cmp" in page:
    o.append(p(f"position:absolute;left:96px;top:{214 + len(plist) * 122 + 34}px;font-size:26px;color:{SUB}", f"{page['why']}–{page['big']}쪽은 들어가기, {page['m-cmp']}–{page['cheatsheet']}쪽은 MySQL과 비교, 막힐 때, 한 장 요약이에요."))
o = [x for x in o if 'id="eyebrow"' not in x]
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(o) + f"\n<aside>{e('여섯 파트로 나눴어요. 33 MySQL과 같은 순서예요. 1파트에서 PostgreSQL 컨테이너를 켜고 psql로 들어가요. 2파트에서 데이터베이스와 표를 만들고 주문을 넣었다 지워요. 3파트에서 관리자 계정과 일반 계정, 여러 가지 접속 방법을 봐요. 4파트에서 볼륨으로 데이터를 지키고 compose로 옮겨요. 5파트는 자주 나는 오류, 6파트는 실제 상황 예제예요. 끝에 MySQL과 다른 점을 표로 모아요.')}</aside>\n</section>\n")

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-12T00:00:00Z"}, "lists": "css", "title": "Docker 4 (PostgreSQL 컨테이너로 데이터베이스 쓰기)", "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
for w_ in WARN:
    print("WARN", w_)
print(len(ORDER), "slides")
