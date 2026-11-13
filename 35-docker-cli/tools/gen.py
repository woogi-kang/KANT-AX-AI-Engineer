r"""Generates every slide of the Docker CLI deck (35) and slides/deck.json.

Story: 29-34 taught about twenty docker commands spread over six chapters, and the class (IndieGameMaker/kant_docker)
added a few more: docker cp, docker exec -i ... < file, psql -f, docker volume create / inspect, a long command split
with \. This chapter puts every command on one map, reads a command as pieces, then walks the groups: images and
containers, working inside a container (the class's kant_shop.sql into postgres:18), volumes, YAML and compose (the
class format with container_name, indentation, 2 vs 4 spaces, tabs) and every compose command. Errors, three real
tasks, then two cheat-sheet slides.
Analogy kept from 29/30: image = 붕어빵 틀, container = 붕어빵, volume = 붕어빵 밖 보관함.
Example names are the class ones: my-pg, admin1234, kant_shop, product, pgdata, folder ~/kant-shop.

Every terminal line comes from tools/demo.py (real Docker 29.9.2, Compose v5, postgres:18, in tools/out.json).
Usage (in 35-docker-cli): python3 tools/gen.py slides
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
from files import SQL, COMPOSE, COMPOSE_NONAME, COMPOSE_FOUR, COMPOSE_TAB, COMPOSE_MIX, COMPOSE_COLON  # noqa: E402  (the files demo.py wrote)

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
REAL = " 터미널 출력은 tools/demo.py로 실제 Docker와 postgres:18 이미지를 실행한 결과예요."


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



# =====================================================================
# chapter 35
# =====================================================================
CY, CYBG = "#5A3BB8", "#EEE9FB"      # compose and YAML
CP, CPBG = "#0F7C86", "#E1F2F3"      # working inside a container
EB1, EB2, EB3, EB4, EB5, EB6 = "1. 명령 읽는 법", "2. 이미지와 컨테이너", "3. 컨테이너 안에서 작업하기", "4. 볼륨", "5. YAML과 compose", "6. 오류와 실제 상황"
C1, C2, C3, C4, C5, C6 = BL, DK, CP, VO, CY, RED
RUN = C("run")
RUNV = C("v-run")
SEL = C("sel")


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
# cover
# =====================================================================
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px">',
       p("position:absolute;left:128px;top:300px;font-size:28px;font-weight:700;color:#9DC1E6", "KANT AX/AI 엔지니어 트랙 · 35"),
       f'<h1{SLAM(1)} style="position:absolute;left:128px;top:350px;padding-bottom:14px;font-size:100px;font-weight:900;line-height:1.3;color:#F6F5F1">Docker 5</h1>',
       p("position:absolute;left:128px;top:500px;font-size:52px;font-weight:700;line-height:1.3;color:#F6F5F1", "명령어 한눈에 보기"),
       p("position:absolute;left:128px;top:600px;width:760px;font-size:32px;line-height:1.5;color:#BFC6D4", "29부터 배운 docker 명령과<br>오늘 수업 명령을 한 장에 모아요")]
rows = cmd_rows("run3") + [("o", "")] + cmd_rows("cp") + [("o", "")] + cmd_rows("i-redirect")
t = Term(rows, 930, 250, size=18, w=894, tid="cov-term", lh=1.45)
cov.append(t.html())
cov.append(shine(2, "cov-term"))
W("cover", cov, "35 챕터는 Docker 5, 명령어 한눈에 보기예요. 29부터 34까지 여섯 챕터에서 docker 명령을 스무 개쯤 배웠어요. 오늘 수업에서는 docker cp, docker exec -i처럼 새 명령도 나왔어요. 명령이 여러 챕터에 흩어져 있으면 막힐 때 찾기 어려워요. 그래서 이번 챕터는 명령을 묶음별로 다시 보고, 수업 예제 그대로 실행해 보고, 마지막에 치트시트 두 장으로 모아요. 오른쪽은 수업 순서 그대로, 긴 docker run을 세 줄로 나눠 치고, SQL 파일을 컨테이너로 넣고 실행한 화면이에요." + REAL, ("intro", "들어가기"))

ORDER.append("toc")   # written last, after page numbers are known

# =====================================================================
# why
# =====================================================================
o = frame("why", "들어가기", "docker 명령이 여섯 챕터에 흩어져 있어요", INK)
cols_ = [("29", "Docker 1", DK, ["pull", "images", "run", "ps", "stop", "start", "restart", "rm", "rmi", "logs"]),
         ("30", "Docker 2", DK, ["exec -it", "volume ls", "volume rm", "compose up", "compose ps", "compose down"]),
         ("31", "nginx", DK, ["exec 이름 명령", "compose logs", "compose stop", "compose start"]),
         ("33·34", "MySQL, PostgreSQL", DK, ["compose exec", "-e 환경 변수"]),
         ("오늘", "수업 레포", OR, ["cp", "exec -i … <", "volume create", "volume inspect", "compose config"])]
CWX = [96, 440, 784, 1128, 1472]
for k, (ch, nm, c, cmds) in enumerate(cols_):
    x = CWX[k]
    o.append(p(f"position:absolute;left:{x}px;top:226px;font-size:34px;font-weight:900;color:{c}", e(ch)))
    o.append(p(f"position:absolute;left:{x}px;top:278px;font-size:22px;color:{SUB};white-space:nowrap", e(nm)))
    o.append(f'<div style="position:absolute;left:{x}px;top:322px;width:320px;height:3px;background:{c}"></div>')
    for j, cm in enumerate(cmds):
        bg = "#FFFFFF" if c == DK else "#FBF0DF"
        o.append(chip(x, 346 + j * 58, cm, c, bg, 1 if c == DK else 2, size=21, attrs=DELAY(k * 110 + j * 35), anim="rise", mono=not any(0xAC00 <= ord(ch_) <= 0xD7A3 for ch_ in cm)))
o.append(p(f"position:absolute;left:96px;top:{346 + 10 * 58 + 20}px;font-size:30px;font-weight:700;color:{INK}", f'29~34에서 배운 명령 <span{COUNT(3)} style="font-size:44px;font-weight:900;color:{DK}">20</span>개, 오늘 새로 나온 명령 <span style="font-size:44px;font-weight:900;color:{OR}">5</span>개', bi("rise", 3)))
W("why", o, "docker 명령이 여섯 챕터에 흩어져 있어요. 29에서 pull, run, ps, stop, rm 같은 기본 명령 열 개를 배웠어요. 30에서는 exec와 볼륨, compose를, 31에서는 compose logs, stop, start를 더했어요. 33과 34에서는 -e로 환경 변수를 넘기고 compose exec로 들어갔어요. 세어 보면 스무 개예요. 오늘 수업에서는 docker cp, docker exec -i와 파일, volume create, volume inspect, compose config까지 다섯 개가 더 나왔어요. 막혔을 때 이 명령이 몇 챕터에 있었는지 찾다 보면 시간이 걸려요. 이번 챕터에서 전부 한 지도에 놓고, 마지막 치트시트 두 장으로 모아요.")

# =====================================================================
# big picture: the command map
# =====================================================================
o = frame("big", "들어가기", "명령은 이미지, 컨테이너, 볼륨, 내 폴더 사이를 오가요", INK)
o.append(node(96, 230, 330, 130, "Docker Hub", "공식 이미지가 있는 곳", GRAY, "#EEF0F3", "mp-hub", icon="Globe"))
o.append(node(96, 560, 330, 150, "이미지", "postgres:18 · 붕어빵 틀", C2, "#E8EFFD", "mp-img", icon="Layers"))
o.append(f'<div id="mp-box" style="position:absolute;left:640px;top:250px;width:640px;height:460px;border:3px dashed {C2};border-radius:24px;background:#F1F5FD"></div>')
o.append(p(f"position:absolute;left:672px;top:270px;font-family:{MONO};font-size:28px;font-weight:700;color:{C2}", "컨테이너 my-pg"))
o.append(p(f"position:absolute;left:672px;top:316px;font-size:22px;color:{SUB}", "붕어빵 · 안에서 PostgreSQL 서버가 돌아요"))
inner = [("stop · start · restart · rm", C2, 2), ("logs", C2, 2), ("exec -it my-pg psql", C3, 3), ("exec my-pg ls /tmp", C3, 3)]
for j, (t_, c, od) in enumerate(inner):
    o.append(chip(672, 380 + j * 76, "docker " + t_, c, "#FFFFFF", od, size=22, attrs=DELAY(j % 2 * 120)))
o.append(cyl(1520, 330, 300, 270, "pgdata", "볼륨 · 붕어빵 밖 보관함", C4, VOBG, "mp-vol", attrs=bi("rise", 4)))
o.append(chip(1520, 620, "docker volume …", C4, "#FFFFFF", 4, size=22))
# my folder
o.append(f'<div id="mp-dir" style="position:absolute;left:640px;top:820px;width:640px;height:150px;background:{CARD};border:3px solid {INK};border-radius:20px"></div>')
o.append(p(f"position:absolute;left:672px;top:838px;font-size:26px;font-weight:700;color:{INK}", "내 폴더 ~/kant-shop"))
o.append(f'<div style="position:absolute;left:672px;top:892px;display:flex;flex-direction:row;gap:16px">' + file_chip("kant_shop.sql", fid="mp-sql") + file_chip("compose.yaml", color=C5, fid="mp-yml") + '</div>')
# arrows and their commands
o.append(line_arrow(261, 362, 261, 552, GRAY, 1))
o.append(p(f"position:absolute;left:290px;top:430px;font-family:{MONO};font-size:24px;font-weight:700;color:{C2}", "docker pull", bi("rise", 1)))
o.append(line_arrow(428, 635, 632, 635, C2, 1))
o.append(p(f"position:absolute;left:452px;top:586px;font-family:{MONO};font-size:24px;font-weight:700;color:{C2}", "docker run", bi("rise", 1)))
o.append(line_arrow(1284, 470, 1512, 470, C4, 4))
o.append(p(f"position:absolute;left:1302px;top:424px;font-family:{MONO};font-size:22px;font-weight:700;color:{C4}", "-v pgdata:…", bi("rise", 4)))
o.append(line_arrow(820, 816, 820, 720, C3, 3, pid="mp-cp"))
o.append(p(f"position:absolute;left:356px;top:744px;width:440px;text-align:right;font-family:{MONO};font-size:22px;font-weight:700;color:{C3}", "docker cp / exec -i … &lt;", bi("rise", 3)))
o.append(f'<div{PATH(3, "mp-cp", 1100)} style="position:absolute;left:806px;top:704px;width:28px;height:28px;border-radius:7px;background:{C3};box-shadow:0 0 0 5px #FFFFFF"></div>')
o.append(line_arrow(1100, 816, 1100, 720, C5, 5))
o.append(p(f"position:absolute;left:1130px;top:744px;font-family:{MONO};font-size:22px;font-weight:700;color:{C5}", "docker compose up -d / down", bi("rise", 5)))
o.append(caption("명령마다 무엇을 움직이는지 보면 덜 헷갈려요.", 1000 - 30, 6, left=1320, width=504, size=26, color=SUB))
W("big", o, "오늘 볼 명령을 한 지도에 놓았어요. 왼쪽 위 Docker Hub에서 docker pull로 이미지를 받아요. 이미지는 붕어빵 틀이에요. docker run으로 틀에서 붕어빵, 컨테이너 my-pg를 찍어요. 컨테이너를 켜고 끄고 지우는 명령, 기록을 보는 logs가 2파트예요. 청록색은 3파트예요. 컨테이너 안에 들어가거나, 내 폴더의 SQL 파일을 컨테이너로 넣는 명령이에요. 주황색 볼륨은 4파트예요. 컨테이너를 지워도 데이터가 남는 보관함이에요. 마지막 보라색은 5파트의 compose예요. 긴 docker run을 compose.yaml 파일에 적어 두고 up과 down으로 한 번에 켜고 꺼요.")

# =====================================================================
# part 1: reading a command
# =====================================================================
o = frame("r-shape", EB1, "docker 다음은 할 일, 그 뒤에 옵션과 이름이 와요", C1)
segs = [("docker", INK, None, None), ("run", C2, "할 일", None), ("-d --name my-pg -e POSTGRES_PASSWORD=admin1234 -p 5432:5432", BL, "옵션 네 개", None), ("postgres:18", OR, "이미지 이름", None)]
o += parts(96, 240, segs, size=31, order=1, lab=26, stagger=True, lw=240)
o.append(p(f"position:absolute;left:96px;top:440px;font-size:26px;font-weight:700;color:{GRAY}", "다른 명령도 같은 모양이에요"))
HX = [96, 640, 860, 1400]
for j, h_ in enumerate(["할 일", "옵션", "이름", "그 뒤에 붙는 것"]):
    o.append(p(f"position:absolute;left:{HX[j]}px;top:498px;font-size:24px;font-weight:700;color:{[C2, BL, OR, GRAY][j]}", e(h_)))
ex = [("docker volume create", "", "pgdata", ""),
      ("docker exec", "-it", "my-pg", "psql -U postgres"),
      ("docker logs", "--tail 3", "my-pg", ""),
      ("docker compose up", "-d", "", ""),
      ("docker cp", "", "kant_shop.sql", "my-pg:/tmp/kant_shop.sql")]
for i, row in enumerate(ex):
    y = 548 + i * 78
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:1px;background:{LINE}"></div>')
    for j, v in enumerate(row):
        if v:
            o.append(p(f"position:absolute;left:{HX[j]}px;top:{y + 20}px;font-family:{MONO};font-size:28px;font-weight:700;color:{[C2, BL, OR, INK][j]};white-space:nowrap", e(v), bi("rise", 2) + DELAY(i * 90)))
o.append(f'<div style="position:absolute;left:96px;top:{548 + len(ex) * 78}px;width:1728px;height:1px;background:{LINE}"></div>')
o.append(caption("할 일이 두 단어일 때도 있어요. volume create, compose up처럼요.", 548 + len(ex) * 78 + 26, 3, size=28))
W("r-shape", o, "docker 명령은 모양이 정해져 있어요. docker 다음에 할 일이 오고, 그 뒤에 옵션, 마지막에 이름이 와요. 위 줄은 수업에서 친 docker run이에요. run이 할 일이고, -d, --name, -e, -p는 옵션, 마지막 postgres:18은 이미지 이름이에요. 아래 표처럼 다른 명령도 같은 순서예요. docker exec는 이름 뒤에 컨테이너 안에서 실행할 명령이 하나 더 붙어요. docker cp는 이름 자리에 보낼 파일과 받을 곳 두 개가 와요. volume create, compose up처럼 할 일이 두 단어인 명령도 있어요. 처음 보는 명령도 이 순서로 끊어 읽으면 뜻이 보여요.", ("p1", "명령 읽는 법"))

o = frame("r-opts", EB1, "옵션은 글자 하나짜리가 많아요", C1)
opts = [("-d", "뒤에서 켜기", "터미널을 계속 쓰고 싶을 때", "29"),
        ("--name 이름", "컨테이너 이름 붙이기", "긴 ID 대신 이름으로 부를 때", "29"),
        ("-p 5432:5432", "포트 연결 (내 컴퓨터:컨테이너)", "밖에서 접속할 때", "29"),
        ("-e 이름=값", "환경 변수 넘기기", "비밀번호를 정할 때", "33"),
        ("-v pgdata:경로", "볼륨 연결", "지워도 데이터를 남길 때", "30"),
        ("-it", "들어가서 직접 치기", "psql, bash를 열 때", "29"),
        ("-i", "파일 내용을 넘기기", "< 파일로 SQL을 넣을 때", "오늘"),
        ("--tail 3", "마지막 3줄만", "기록이 길 때", "오늘"),
        ("-f", "계속 보기 (Ctrl+C로 멈춤)", "새 기록을 기다릴 때", "오늘")]
OX = [96, 420, 940, 1640]
for j, h_ in enumerate(["옵션", "뜻", "언제", "챕터"]):
    o.append(p(f"position:absolute;left:{OX[j]}px;top:220px;font-size:24px;font-weight:700;color:{GRAY}", e(h_)))
for i, (a_, b_, c_, d_) in enumerate(opts):
    y = 266 + i * 78
    new = d_ == "오늘"
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:1px;background:{LINE}"></div>')
    ra = bi("rise", 1 if not new else 2) + DELAY((i if not new else i - 6) * 60)
    o.append(p(f"position:absolute;left:{OX[0]}px;top:{y + 18}px;font-family:{MONO};font-size:28px;font-weight:700;color:{OR if new else BL};white-space:nowrap", e(a_), ra))
    o.append(p(f"position:absolute;left:{OX[1]}px;top:{y + 20}px;font-size:26px;font-weight:700;color:{INK};white-space:nowrap", e(b_), ra))
    o.append(p(f"position:absolute;left:{OX[2]}px;top:{y + 20}px;font-size:25px;color:{SUB};white-space:nowrap", e(c_), ra))
    o.append(p(f"position:absolute;left:{OX[3]}px;top:{y + 20}px;width:184px;text-align:right;font-size:25px;font-weight:700;color:{OR if new else GRAY};white-space:nowrap", e(d_), ra))
o.append(f'<div style="position:absolute;left:96px;top:{266 + len(opts) * 78}px;width:1728px;height:1px;background:{LINE}"></div>')
o.append(pen_box(3, 84, 266 + 6 * 78 + 4, 1752, 3 * 78 - 8, OR))
o.append(caption("주황색 세 줄은 오늘 처음 나와요. 2, 3파트에서 직접 쳐 봐요.", 266 + len(opts) * 78 + 26, 3, size=28))
W("r-opts", o, "옵션은 대부분 글자 하나짜리예요. 위 여섯 줄은 29부터 34까지 쓴 옵션이에요. -d는 뒤에서 켜기, --name은 이름 붙이기, -p는 내 컴퓨터 포트와 컨테이너 포트를 잇는 옵션이에요. -e로 비밀번호 같은 환경 변수를 넘기고, -v로 볼륨을 붙여요. -it는 컨테이너 안에 들어가서 직접 칠 때 써요. 아래 주황색 세 줄은 오늘 처음 나와요. -i는 i만 쓰는 옵션으로, 내 폴더의 파일 내용을 컨테이너 안 프로그램에 넘길 때 써요. --tail은 기록의 마지막 몇 줄만 보여 주고, -f는 기록을 계속 보여 줘요. -f는 Ctrl+C로 멈춰요.")

o = frame("r-split", EB1, "긴 명령은 줄 끝에 \\를 붙여 여러 줄로 나눠요", C1)
r3 = C("run3").split("\n")
rows = [("$", P_KS, r3[0], {"\\": 'id="sp-b1"'}), ("o", "> " + r3[1]), ("o", "> " + r3[2])] + out_rows("run3")
t = Term(rows, 96, 214, size=27, w=1110, lh=1.55, tid="t-split")
o.append(t.html())
for i in (0, 1):
    xx = t.end(i) - t.sw("\\")
    o.append(ring(1, round(xx - 10), round(t.top(i) - 2), round(t.sw("\\") + 20), round(t.lp + 4), OR))
o.append(p(f"position:absolute;left:1250px;top:236px;width:574px;font-size:28px;font-weight:700;line-height:1.5;color:{INK}", "\\ 는 \"다음 줄도 같은 명령\"이라는 표시예요.", bi("rise", 1)))
o.append(p(f"position:absolute;left:1250px;top:380px;width:574px;font-size:25px;line-height:1.55;color:{SUB}", "Enter를 쳐도 실행하지 않고 &gt; 를 띄워 다음 줄을 기다려요. 한 줄로 친 것과 똑같이 실행돼요.", bi("rise", 1)))
rs = C("runsp").split("\n")
rows2 = [("$", P_KS, rs[0].rstrip() + " ", {}), ("o", "> " + rs[1]), ("o", "> " + rs[2])] + out_rows("runsp")
t2 = Term(rows2, 96, t.y + t.h + 48, size=24, w=1728, lh=1.5, tid="t-sp")
o.append(f'<div{bi("rise", 2)}>' + t2.html() + "</div>")
xs = t2.end(0)
o.append(pen_box(2, round(xs - t2.sw("\\ ") - 6), round(t2.top(0) - 2), round(t2.sw("\\ ") + 22), round(t2.lp + 4), RED))
o += tag(t2, 0, "\\ 뒤에 띄어쓰기가 있으면 줄이 끊겨요", RED, 3)
o.append(caption("Mac 터미널과 Windows Git Bash에서 써요. 수업 자료의 두 가지 쓰는 법은 결과가 같아요.", t2.y + t2.h + 30, 3, size=27, color=SUB))
W("r-split", o, "긴 명령은 줄 끝에 백슬래시를 붙여 여러 줄로 나눠 쳐요. 수업 자료에도 docker run을 한 줄로 쓴 것과 세 줄로 나눈 것이 같이 있었어요. 백슬래시는 다음 줄도 같은 명령이라는 표시예요. Enter를 쳐도 바로 실행하지 않고 꺾쇠를 띄워서 다음 줄을 기다려요. 마지막 줄에서 Enter를 치면 한 줄로 친 것과 똑같이 실행돼요. 조심할 게 하나 있어요. 백슬래시 뒤에 띄어쓰기가 하나라도 있으면 그 줄에서 명령이 끝나요. 아래 화면이 그 경우예요. docker run은 이미지 이름이 없어서 invalid reference format이 나오고, 다음 줄의 -e는 명령으로 읽혀서 command not found가 나와요. 줄 끝은 백슬래시로 끝나야 해요." + REAL)

# =====================================================================
# part 2: images and containers
# =====================================================================
o = frame("i-pull", EB2, "이미지는 pull로 받고 images로 보고 rmi로 지워요", C2)
pl = RA("pull")
keep = [l for l in pl if not re.match(r"^[0-9a-f]{12}: ", l)]
nlay = len(pl) - len(keep)
rows = [("$", P_KS, C("pull")), ("o", pl[0]), ("d", f"… 층 {nlay}개를 받아요 (줄 {nlay}개 줄임)")] + [("o", l) for l in keep[1:]] + [("o", ""), ("$", P_KS, C("images"))] + [("o", l.rstrip()) for l in RA("images")]
t = Term(rows, 96, 214, size=25, w=1728, lh=1.5, tid="t-pull")
o.append(t.html())
st = next(i for i, r in enumerate(rows) if r[0] == "o" and r[1].startswith("Status:"))
o += tag(t, st, "다 받았어요", GR, 1, gap=30) if t.end(st) + 250 < t.x + t.w else []
im = len(rows) - 1
o.append(underline(2, t.sx(im, "postgres:18"), t.sx(im, "postgres:18") + t.sw("postgres:18"), t.top(im) + t.lp - 2, OR))
cmds = [("docker pull postgres:18", "받기"), ("docker images", "받은 목록"), ("docker rmi postgres:18", "지우기 (쓰는 컨테이너가 없을 때)")]
for i, (c_, d_) in enumerate(cmds):
    x = 96 + i * 590
    y = t.y + t.h + 50
    o.append(p(f"position:absolute;left:{x}px;top:{y}px;font-family:{MONO};font-size:28px;font-weight:700;color:{C2};white-space:nowrap", e(c_), bi("rise", 3) + DELAY(i * 90)))
    o.append(p(f"position:absolute;left:{x}px;top:{y + 50}px;width:560px;font-size:25px;color:{SUB}", e(d_), bi("rise", 3) + DELAY(i * 90)))
o.append(caption("태그 18은 PostgreSQL 18이에요. 숫자로 적어 두면 모두 같은 버전을 받아요.", t.y + t.h + 170, 3, size=28))
W("i-pull", o, "이미지는 pull로 받고 images로 보고 rmi로 지워요. 29에서 배운 세 명령이에요. docker pull postgres:18을 치면 이미지를 여러 층으로 나눠 받아요. 층마다 한 줄씩 나와서 화면에서는 줄였어요. Status 줄이 나오면 다 받은 거예요. docker images에 postgres:18이 보여요. docker rmi는 이미지를 지워요. 이 이미지로 만든 컨테이너가 남아 있으면 지워지지 않는데, 이 파트 끝에서 실제 오류를 봐요. 태그 18은 PostgreSQL 18 버전이라 숫자로 적어 두면 모두 같은 버전을 받아요." + REAL, ("p2", "이미지와 컨테이너"))

o = frame("i-run", EB2, "run으로 켜고 ps로 켜진 컨테이너를 봐요", C2)
rows = [("$", P_KS, RUN), ("o", D["run"][0]["out"][0]), ("o", ""), ("$", P_KS, C("ps"))] + [("o", l) for l in RA("ps")]
t = Term(rows, 96, 230, size=19, w=1728, lh=2.1, tid="t-run")
o.append(t.html())
o.append(spot(1, x=round(t.sx(1, D["run"][0]["out"][0][:12]) - 6), y=round(t.top(1) - 4), w=round(t.sw("0" * 64) + 12), h=round(t.lp + 8)))
o.append(spot(2, x=round(t.sx(5, "Up") - 6), y=round(t.top(4) - 4), w=round(t.sw("Up 2 seconds   0.0.0.0:5432->5432/tcp   my-pg") + 12), h=round(2 * t.lp + 8)))
o.append(spot_off(3))
lab = [("컨테이너 ID", "앞 12자리예요", t.tx), ("STATUS Up", "켜져 있어요", t.sx(5, "Up")), ("NAMES", "--name으로 붙인 이름", t.sx(5, "my-pg") - 150)]
for k, (a_, b_, x_) in enumerate(lab):
    y = t.y + t.h + 50
    o.append(f'<div{bi("fade", 3)} style="position:absolute;left:{x_ + 10:.0f}px;top:{t.y + t.h + 6}px;width:2px;height:40px;background:{C2}"></div>')
    o.append(p(f"position:absolute;left:{x_:.0f}px;top:{y}px;font-size:30px;font-weight:700;color:{C2};white-space:nowrap", e(a_), bi("rise", 3) + DELAY(k * 100)))
    o.append(p(f"position:absolute;left:{x_:.0f}px;top:{y + 46}px;font-size:26px;color:{SUB};white-space:nowrap", e(b_), bi("rise", 3) + DELAY(k * 100)))
o.append(caption("ps는 켜진 것만, ps -a는 꺼진 것까지 보여 줘요.", t.y + t.h + 220, 4, size=30))
W("i-run", o, "docker run으로 켜고 docker ps로 켜진 컨테이너를 봐요. 수업 명령 그대로 my-pg라는 이름으로 postgres:18을 켰어요. -d로 뒤에서 켜서 화면에는 긴 컨테이너 ID 한 줄만 나와요. docker ps를 치면 표가 나와요. 맨 앞은 컨테이너 ID 앞 12자리예요. STATUS가 Up이면 켜져 있다는 뜻이고, PORTS에 5432번이 이어져 있어요. 맨 끝 NAMES가 --name으로 붙인 이름이에요. 다른 명령에는 ID 대신 이 이름을 적으면 돼요. ps는 켜진 컨테이너만 보여 주고, 꺼진 것까지 보려면 ps -a를 쳐요." + REAL)

o = frame("i-state", EB2, "stop, start, restart는 상태만 바꾸고 rm이 지워요", C2)
S_ = [("만들어짐", "docker run", 96), ("켜짐 Up", "", 556), ("꺼짐 Exited", "", 1076), ("없어짐", "", 1544)]
for k, (n_, _, x) in enumerate(S_):
    col = [C2, GR, GRAY, RED][k]
    bg = ["#E8EFFD", "#E4F3EA", "#EEF0F3", "#FBEAEA"][k]
    o.append(f'<div id="st-{k}"{bi("rise", 1 if k < 2 else (2 if k == 2 else 4))} style="position:absolute;left:{x}px;top:250px;width:280px;height:120px;border-radius:60px;background:{bg};border:3px solid {col};display:flex;align-items:center;justify-content:center">'
             + p(f"font-size:32px;font-weight:700;color:{col};white-space:nowrap", e(n_)) + '</div>')
arw = [(380, 548, 300, "docker run", C2, 1), (840, 1068, 280, "docker stop", GRAY, 2), (1068, 840, 344, "docker start", GR, 3), (1360, 1536, 300, "docker rm", RED, 4)]
for x1, x2, y, lb, col, od in arw:
    o.append(line_arrow(x1, y, x2, y, col, od))
    o.append(p(f"position:absolute;left:{min(x1, x2) - 20:.0f}px;top:{y - (52 if y <= 300 else -14):.0f}px;width:{abs(x2 - x1) + 40}px;text-align:center;font-family:{MONO};font-size:21px;font-weight:700;color:{col};white-space:nowrap", e(lb), bi("rise", od)))
o.append(p(f"position:absolute;left:556px;top:390px;width:280px;text-align:center;font-family:{MONO};font-size:21px;font-weight:700;color:{GR}", "docker restart", bi("rise", 3)))
o.append(p(f"position:absolute;left:556px;top:424px;width:280px;text-align:center;font-size:20px;color:{SUB}", "껐다가 바로 켜기", bi("rise", 3)))
rows = [("$", P_KS, C("stop")), ("o", "my-pg"), ("$", P_KS, C("psa-stop"))] + [("o", l) for l in RA("psa-stop")] + [("o", ""), ("$", P_KS, C("start")), ("o", "my-pg"), ("$", P_KS, C("psa-up"))] + [("o", l) for l in RA("psa-up")]
t = Term(rows, 96, 500, size=18, w=1728, lh=1.5, tid="t-state")
o.append(t.html())
o.append(underline(2, t.sx(4, "Exited (0)"), t.sx(4, "Exited (0)") + t.sw("Exited (0)"), t.top(4) + t.lp - 2, GRAY))
o.append(underline(3, t.sx(10, "Up Less"), t.sx(10, "Up Less") + t.sw("Up Less than a second"), t.top(10) + t.lp - 2, GR))
o.append(caption("꺼져도 ps -a에 남아 있어요. 다시 켜면 안의 데이터도 그대로예요.", t.y + t.h + 26, 4, size=27))
W("i-state", o, "stop, start, restart는 상태만 바꾸고, rm이 컨테이너를 지워요. 위 그림처럼 컨테이너는 켜짐과 꺼짐 사이를 오가요. docker stop으로 끄면 docker ps에서는 안 보이지만 ps -a에는 STATUS가 Exited로 남아 있어요. docker start로 다시 켜면 Up이 돼요. docker restart는 껐다가 바로 켜는 명령이에요. 설정을 바꾼 뒤에 다시 읽게 할 때 써요. 꺼졌다 켜져도 컨테이너 안에 만든 데이터는 그대로 있어요. 지우는 건 docker rm뿐이에요. rm으로 지운 컨테이너는 다시 켤 수 없고, 안의 데이터도 같이 사라져요." + REAL)

o = frame("i-logs", EB2, "logs --tail은 마지막 몇 줄만, -f는 새 기록을 계속 보여 줘요", C2)
lt = [short_log(l) for l in RA("logs-tail")]
rows = [("$", P_KS, C("logs-tail"))] + [("o", l) for l in rewrap(lt, 108)]
t = Term(rows, 96, 214, size=24, w=1728, lh=1.5, tid="t-tail")
o.append(t.html())
lf = [short_log(l) for l in RA("logs-f")]
rows2 = [("$", P_KS, C("logs-f"))] + [("o" if l != "^C" else "y", l) for l in rewrap(lf, 108)]
t2 = Term(rows2, 96, t.y + t.h + 40, size=24, w=1728, lh=1.5, tid="t-f")
o.append(t2.html())
o += tag(t, len(rows) - 1, "3줄만 나오고 끝나요", C2, 1)
o += tag(t2, len(rows2) - 1, "Ctrl+C를 눌러야 멈춰요", OR, 2, gap=30)
o.append(keys(2, 1400, t2.y + t2.h + 30, "Ctrl+C"))
o.append(caption("줄 앞의 날짜와 번호는 화면에서 … 로 줄였어요.", t2.y + t2.h + 40, 3, size=25, color=SUB, width=1200))
W("i-logs", o, "docker logs는 컨테이너 안 프로그램이 남긴 기록을 보여 줘요. 34에서 ready to accept connections를 찾을 때 썼어요. PostgreSQL은 기록이 길어서 그냥 치면 화면이 넘쳐요. --tail 3을 붙이면 마지막 세 줄만 보여 주고 끝나요. -f는 follow, 따라가기라는 뜻이에요. 기록을 보여 준 뒤 끝나지 않고 새 줄이 생길 때마다 계속 보여 줘요. 서버가 다 켜지기를 기다리거나 접속 기록을 지켜볼 때 써요. 멈출 때는 Ctrl+C를 눌러요. 컨테이너는 그대로 켜져 있어요. 화면에서는 줄 앞의 날짜와 번호를 줄였어요." + REAL)

o = frame("i-rm", EB2, "켜진 컨테이너는 못 지우고, 쓰는 이미지도 못 지워요", C2)
rows = [("$", P_KS, C("rm-up"))] + out_rows("rm-up", rew=116) + [("o", ""), ("$", P_KS, C("rmi-used"))] + out_rows("rmi-used", rew=116)
t = Term(rows, 96, 214, size=23, w=1728, lh=1.55, tid="t-rmerr")
o.append(t.html())
o.append(shake(1, "t-rmerr"))
o.append(underline(1, t.sx(1, "container is running"), t.sx(1, "container is running") + t.sw("container is running"), t.top(1) + t.lp - 2, RED))
k2 = next(i for i, r in enumerate(rows) if "using its referenced" in r[1])
o.append(underline(2, t.sx(k2, "using its"), t.sx(k2, "using its") + t.sw("using its referenced image"), t.top(k2) + t.lp - 2, RED))
steps = [("1", "docker stop my-pg", "끄고"), ("2", "docker rm my-pg", "컨테이너를 지우고"), ("3", "docker rmi postgres:18", "이미지를 지워요")]
sy = t.y + t.h + 60
o.append(p(f"position:absolute;left:96px;top:{sy}px;font-size:26px;font-weight:700;color:{GRAY}", "지울 때는 이 순서예요", bi("fade", 3)))
for k, (n_, c_, d_) in enumerate(steps):
    x = 96 + k * 590
    o.append(f'<div{bi("rise", 3)}{DELAY(k * 140)} style="position:absolute;left:{x}px;top:{sy + 56}px;width:560px;height:150px;border-radius:18px;background:{CARD};box-shadow:{SHADOW};padding:24px 28px">'
             + p(f"font-size:24px;font-weight:900;color:{C2}", n_ + ". " + e(d_))
             + p(f"margin-top:14px;font-family:{MONO};font-size:26px;font-weight:700;color:{INK};white-space:nowrap", e(c_)) + '</div>')
W("i-rm", o, "켜진 컨테이너는 바로 못 지우고, 컨테이너가 쓰고 있는 이미지도 못 지워요. 첫 번째 오류는 container is running이에요. 켜진 채로 docker rm을 쳐서 먼저 끄라고 알려 줘요. 두 번째 오류는 이미지를 지우려 했는데 컨테이너가 그 이미지를 쓰고 있다는 뜻이에요. 꺼진 컨테이너도 남아 있으면 같은 오류가 나요. 29에서도 본 오류예요. 지울 때는 아래 순서로 해요. stop으로 끄고, rm으로 컨테이너를 지우고, 마지막에 rmi로 이미지를 지워요. 강제로 지우는 옵션도 있지만 수업에서는 이 순서로 해요." + REAL)

# =====================================================================
# part 3: working inside a container
# =====================================================================
o = frame("w-sql", EB3, "수업 파일 kant_shop.sql은 데이터베이스, 표, 상품 다섯 개를 만들어요", C3)
SQLL = SQL.rstrip("\n").split("\n")
ed, g = editor("ed-sql", "kant_shop.sql", [l.rstrip() for l in SQLL], 96, 206, 1010, fs=20, color=C3)
o.append(ed)
notes_ = [(0, 1, "-- 뒤는 설명이에요", "주석이라 실행하지 않아요"),
          (1, 1, "IF EXISTS", "있으면 지우고, 없으면 넘어가요"),
          (6, 1, "\\c kant_shop", "psql 명령이에요. 이 데이터베이스로 옮겨요"),
          (11, 4, "SERIAL · NOT NULL", "id는 1, 2, 3 자동 번호, 나머지는 비울 수 없어요"),
          (18, 6, "INSERT … VALUES", "상품 다섯 줄을 한 번에 넣어요")]
LX = 1150
for k, (i, n, a_, b_) in enumerate(notes_):
    od = k + 1
    o.append(lspot(od, g["left"], g["top"] + TABH, g["w"], g["h"] - TABH, gtop(g, i) - 4, n * g["lh"] + 8, bg=CARD, bar=C3))
    y = [gtop(g, 0) + 10, gtop(g, 2) + 34, gtop(g, 6) + 20, gtop(g, 12) + 20, gtop(g, 20) + 30][k]
    o.append(p(f"position:absolute;left:{LX}px;top:{y - 36:.0f}px;width:674px;font-family:{MONO};font-size:26px;font-weight:700;color:{C3};white-space:nowrap", e(a_), bi("rise", od) + DIM("sql")))
    o.append(p(f"position:absolute;left:{LX}px;top:{y + 4:.0f}px;width:674px;font-size:23px;line-height:1.4;color:{SUB}", e(b_), bi("rise", od) + DIM("sql")))
o.append(lspot_off(6))
W("w-sql", o, "수업 파일 kant_shop.sql은 데이터베이스와 표를 만들고 상품 다섯 개를 넣어요. 하나씩 읽어 봐요. 하이픈 두 개로 시작하는 줄은 주석, 사람이 읽는 설명이라 실행하지 않아요. DROP DATABASE IF EXISTS는 kant_shop이 있으면 지우고, 없으면 그냥 넘어가요. 그래서 이 파일은 몇 번을 실행해도 같은 결과가 나와요. 백슬래시 c는 34에서 본 psql 명령이에요. 방금 만든 kant_shop으로 옮겨 가요. 표 product의 id는 SERIAL이라 1, 2, 3처럼 번호가 자동으로 붙어요. NOT NULL은 그 칸을 비워 둘 수 없다는 뜻이에요. 마지막 INSERT는 상품 다섯 줄을 한 번에 넣어요. 이 파일을 컨테이너 안의 psql에게 건네는 방법을 다음 장부터 봐요.", ("p3", "컨테이너 안에서 작업하기"))

o = frame("w-cp", EB3, "docker cp는 내 폴더와 컨테이너 사이에서 파일을 복사해요", C3)
o.append(f'<div id="cp-dir" style="position:absolute;left:96px;top:226px;width:520px;height:220px;background:{CARD};border:3px solid {INK};border-radius:20px"></div>')
o.append(p(f"position:absolute;left:128px;top:246px;font-size:28px;font-weight:700;color:{INK}", "내 폴더 ~/kant-shop"))
o.append(f'<div id="cp-src" style="position:absolute;left:128px;top:330px">' + file_chip("kant_shop.sql", size=26) + '</div>')
o.append(f'<div id="cp-box" style="position:absolute;left:1304px;top:226px;width:520px;height:220px;background:#F1F5FD;border:3px dashed {C2};border-radius:20px"></div>')
o.append(p(f"position:absolute;left:1336px;top:246px;font-family:{MONO};font-size:28px;font-weight:700;color:{C2}", "컨테이너 my-pg"))
o.append(p(f"position:absolute;left:1336px;top:298px;font-family:{MONO};font-size:24px;font-weight:700;color:{SUB}", "/tmp/"))
o.append(f'<div id="cp-dst" data-build-in="fly order 1" data-from="cp-src" style="position:absolute;left:1336px;top:344px">' + file_chip("kant_shop.sql", color=C3, size=26) + '</div>')
o.append(line_arrow(640, 316, 1284, 316, C3, None))
o.append(p(f"position:absolute;left:640px;top:254px;width:644px;text-align:center;font-family:{MONO};font-size:24px;font-weight:700;color:{C3};white-space:nowrap", "docker cp 보낼파일 컨테이너:경로"))
o.append(line_arrow(1284, 396, 640, 396, GRAY, 3, dash="10 10"))
o.append(p(f"position:absolute;left:640px;top:410px;width:644px;text-align:center;font-family:{MONO};font-size:22px;font-weight:700;color:{GRAY};white-space:nowrap", "docker cp 컨테이너:경로 받을곳", bi("rise", 3)))
rows = [("$", P_KS, C("ls-before")), ("$", P_KS, C("cp"), {"my-pg:/tmp/kant_shop.sql": f'style="color:{C2}"'})] + out_rows("cp") + [("$", P_KS, C("ls-after"))] + out_rows("ls-after") + [("o", ""), ("$", P_KS, C("cp-out"))] + out_rows("cp-out") + [("$", P_KS, C("cp-out-ls"))] + out_rows("cp-out-ls")
t = Term(rows, 96, 500, size=22, w=1728, lh=1.45, tid="t-cp")
o.append(t.html())
o += tag(t, 0, "/tmp가 비어 있어요", GRAY, 2, gap=30)
o += tag(t, 4, "들어갔어요", C3, 2, gap=30)
o.append(f'<div{bi("fade", 3)} style="position:absolute;left:{t.x - 12}px;top:{t.top(6) - 4:.0f}px;width:{t.w + 24}px;height:0px"></div>')
o.append(caption("Windows Git Bash는 30에서 본 export MSYS_NO_PATHCONV=1을 먼저 쳐요. :/tmp 경로가 바뀌지 않아요.", t.y + t.h + 24, 4, size=25, color=SUB))
W("w-cp", o, "docker cp는 내 폴더와 컨테이너 사이에서 파일을 복사해요. 쓰는 모양은 리눅스의 cp와 같아요. 보낼 파일을 먼저 쓰고, 받을 곳을 뒤에 써요. 컨테이너 안의 경로는 컨테이너 이름, 쌍점, 경로로 적어요. my-pg:/tmp/kant_shop.sql은 my-pg 컨테이너 안의 /tmp 폴더에 kant_shop.sql이라는 이름으로 두라는 뜻이에요. 복사하기 전에 docker exec로 /tmp를 보면 비어 있고, 복사한 뒤에는 파일이 보여요. 앞뒤를 바꿔 쓰면 컨테이너 안의 파일을 내 폴더로 꺼내요. 아래쪽은 같은 파일을 copy.sql이라는 이름으로 꺼낸 화면이에요. Windows Git Bash에서는 30에서 배운 export MSYS_NO_PATHCONV=1을 먼저 쳐 두면 경로가 바뀌지 않아요." + REAL)

o = frame("w-exec", EB3, "컨테이너 안을 보는 방법은 세 가지예요", C3)
bs = D["bash"][0]["out"]
en = S("enter")
en = [l for l in en if not l.startswith("kant_shop=# \\d product")]
en = en[:en.index("kant_shop=# \\q") + 1] if "kant_shop=# \\q" in en else en
dt_end = next(i for i, l in enumerate(en) if l.startswith("(1 row)"))
en = en[:dt_end + 1]
rows = [("$", P_KS, C("bash"))] + psql_rows(bs) + [("o", ""), ("$", P_KS, C("ls-after"))] + out_rows("ls-after") + [("o", ""), ("$", P_KS, C("enter"))] + psql_rows(en)
t = Term(rows, 96, 214, size=23, w=1150, lh=1.45, tid="t-exec")
o.append(t.html())
blocks = [(0, 4, "1", "docker exec -it 이름 bash", "들어가서 여러 명령을 쳐요. exit로 나와요."),
          (6, 7, "2", "docker exec 이름 명령", "명령 하나만 실행하고 바로 끝나요."),
          (9, len(rows) - 1, "3", "docker exec -it 이름 psql …", "psql을 바로 열어요. \\q로 나와요.")]
for k, (a, b, n_, c_, d_) in enumerate(blocks):
    od = k + 1
    o.append(spot(od, x=t.x + 10, y=round(t.top(a) - 6), w=t.w - 20, h=round((b - a + 1) * t.lp + 12), dim=0.55))
    y = (t.top(a) + t.top(b) + t.lp) / 2
    o.append(p(f"position:absolute;left:1290px;top:{y - 50:.0f}px;font-family:{MONO};font-size:24px;font-weight:700;color:{C3};white-space:nowrap", e(c_), bi("rise", od)))
    o.append(p(f"position:absolute;left:1290px;top:{y - 6:.0f}px;width:534px;font-size:24px;line-height:1.45;color:{SUB}", e(d_), bi("rise", od)))
o.append(spot_off(4))
W("w-exec", o, "컨테이너 안을 보는 방법은 세 가지예요. 첫 번째는 docker exec -it 이름 bash예요. 컨테이너 안의 bash가 열려서 ls처럼 여러 명령을 차례로 칠 수 있어요. 앞의 표시가 root@로 바뀌면 컨테이너 안이에요. exit로 나와요. 두 번째는 -it 없이 명령 하나만 붙이는 방법이에요. 31에서 nginx -t를 칠 때 썼어요. 실행하고 바로 내 터미널로 돌아와요. 세 번째는 psql을 바로 여는 방법이에요. -d로 데이터베이스를 고르면 앞의 표시가 kant_shop=#이 돼요. 백슬래시 dt를 치면 kant_shop.sql이 만든 product 표가 보여요. 이 화면은 다음 장에서 파일을 실행한 뒤에 찍었어요." + REAL)

o = frame("w-f", EB3, "방법 1. 복사한 파일을 psql -f로 실행해요", C3)
fo = RA("f")
rows = [("$", P_KS, C("f"), {"-f /tmp/kant_shop.sql": f'style="color:{OR}"'})] + [("e" if "NOTICE" in l else "o", l) for l in fo] + [("o", ""), ("$", P_KS, SEL)] + [("o", l) for l in RA("sel")]
t = Term(rows, 96, 214, size=23, w=1728, lh=1.45, tid="t-f")
o.append(t.html())
mp = [(1, "IF EXISTS: 없어서 넘어가요"), (4, "\\c kant_shop 줄"), (6, "상품 다섯 줄")]
for k, (i, lb) in enumerate(mp):
    o += tag(t, i, lb, C3, 1, gap=30)
sel0 = next(i for i, r in enumerate(rows) if r[0] == "$" and r[2] == SEL)
o.append(spot(2, x=t.x + 10, y=round(t.top(sel0 + 1) - 6), w=t.w - 20, h=round(8 * t.lp + 12)))
o.append(spot_off(3))
o.append(caption("-f 파일은 파일 안의 SQL을 위에서부터 차례로 실행해요. 파일은 컨테이너 안에 있어야 해요.", t.y + t.h + 30, 3, size=28))
W("w-f", o, "방법 1은 수업 자료의 첫 번째 방법이에요. docker cp로 넣어 둔 /tmp/kant_shop.sql을 psql -f로 실행해요. -f는 file, 파일이라는 뜻이에요. 파일 안의 SQL을 위에서부터 차례로 실행하고, 문장마다 결과를 한 줄씩 보여 줘요. 첫 줄 NOTICE는 kant_shop이 아직 없어서 DROP을 건너뛰었다는 알림이에요. 오류가 아니에요. You are now connected는 백슬래시 c 줄의 결과이고, INSERT 0 5는 다섯 줄이 들어갔다는 뜻이에요. 아래는 -c로 SELECT 한 문장을 실행해서 상품 다섯 개를 확인한 화면이에요. 이 방법은 파일이 컨테이너 안에 있어야 해서, 먼저 docker cp를 해야 해요." + REAL)

o = frame("w-redirect", EB3, "방법 2. 내 폴더의 파일을 < 로 바로 넘겨요", C3)
rows = [("$", P_KS, C("i-redirect"), {"-i": f'style="color:{OR}"', "< kant_shop.sql": f'style="color:{OR}"'})] + out_rows("i-redirect")
t = Term(rows, 96, 214, size=26, w=1728, lh=1.5, tid="t-red")
o.append(t.html())
LY1, LY2 = t.y + t.h + 90, t.y + t.h + 250
o.append(p(f"position:absolute;left:96px;top:{LY1 - 20}px;font-size:26px;font-weight:700;color:{GRAY}", "방법 1"))
o.append(p(f"position:absolute;left:96px;top:{LY2 - 20}px;font-size:26px;font-weight:700;color:{C3}", "방법 2"))
o.append(chip(260, LY1 - 26, "kant_shop.sql", INK, "#FFFFFF", None, size=24))
o.append(line_arrow(540, LY1, 760, LY1, GRAY, None))
o.append(p(f"position:absolute;left:540px;top:{LY1 - 58}px;width:220px;text-align:center;font-family:{MONO};font-size:22px;font-weight:700;color:{GRAY}", "docker cp"))
o.append(chip(780, LY1 - 26, "/tmp/kant_shop.sql", C2, "#FFFFFF", None, size=24))
o.append(line_arrow(1110, LY1, 1330, LY1, GRAY, None))
o.append(p(f"position:absolute;left:1110px;top:{LY1 - 58}px;width:220px;text-align:center;font-family:{MONO};font-size:22px;font-weight:700;color:{GRAY}", "psql -f"))
o.append(chip(1350, LY1 - 26, "psql (컨테이너 안)", C2, "#FFFFFF", None, size=24, mono=False))
o.append(chip(260, LY2 - 26, "kant_shop.sql", INK, "#FFFFFF", 1, size=24))
o.append(line_arrow(540, LY2, 1330, LY2, C3, 1, pid="rd-path"))
o.append(p(f"position:absolute;left:540px;top:{LY2 - 58}px;width:790px;text-align:center;font-family:{MONO};font-size:22px;font-weight:700;color:{C3}", "&lt; 파일 + docker exec -i", bi("rise", 1)))
o.append(f'<div{PATH(2, "rd-path", 1300)} style="position:absolute;left:1310px;top:{LY2 - 14}px;width:28px;height:28px;border-radius:7px;background:{C3};box-shadow:0 0 0 5px #FFFFFF"></div>')
o.append(chip(1350, LY2 - 26, "psql (컨테이너 안)", C3, CPBG, 1, size=24, mono=False))
o.append(caption("&lt; 는 파일 내용을 명령에 흘려 넣어요. -i가 그 내용을 컨테이너 안까지 이어 줘요. 복사할 필요가 없어요.", LY2 + 70, 3, size=27))
W("w-redirect", o, "방법 2는 수업 자료의 두 번째 방법이에요. docker cp 없이 내 폴더의 파일을 바로 넘겨요. 명령 끝의 꺾쇠 kant_shop.sql은 이 파일 내용을 키보드 대신 명령에 흘려 넣으라는 뜻이에요. 그런데 그 내용은 내 컴퓨터에 있고, psql은 컨테이너 안에 있어요. -i 옵션이 내 쪽 입력을 컨테이너 안의 psql까지 이어 줘요. 결과는 방법 1과 같아요. 이번에는 kant_shop이 이미 있어서 NOTICE 없이 지우고 다시 만들었어요. 아래 그림처럼 방법 1은 복사하고 실행하는 두 단계, 방법 2는 한 단계예요. 파일을 고쳐 가며 여러 번 실행할 때는 방법 2가 편해요." + REAL)

o = frame("w-trap", EB3, "< 로 넘길 때 -it를 쓰면 거절돼요", C3)
rows = [("$", P_KS, C("it-redirect"), {"-it": 'id="tr-it"'})] + out_rows("it-redirect") + [("o", ""), ("$", P_KS, C("i-redirect"), {"-i": 'id="tr-i"'})] + out_rows("i-redirect")[:2] + [("d", "…")]
t = Term(rows, 96, 214, size=26, w=1728, lh=1.5, tid="t-trap")
o.append(t.html())
o.append(shake(1, "t-trap"))
o.append(pen_box(1, round(t.sx(0, "-it") - 6), round(t.top(0) - 2), round(t.sw("-it") + 12), round(t.lp + 4), RED))
o.append(underline(1, t.sx(1, "stdin is not a terminal"), t.sx(1, "stdin is not a terminal") + t.sw("stdin is not a terminal"), t.top(1) + t.lp - 2, RED))
o.append(pen_box(2, round(t.sx(3, "-i ") - 6), round(t.top(3) - 2), round(t.sw("-i") + 12), round(t.lp + 4), GR))
TY = t.y + t.h + 60
tbl = [("-i", "입력을 이어요", "키보드든 파일이든 받아요"), ("-t", "화면(터미널)을 이어요", "키보드로 칠 때만 써요")]
for k, (a_, b_, c_) in enumerate(tbl):
    y = TY + k * 96
    o.append(f'<div{bi("fade", 3)} style="position:absolute;left:96px;top:{y}px;width:1728px;height:1px;background:{LINE}"></div>')
    o.append(p(f"position:absolute;left:96px;top:{y + 22}px;font-family:{MONO};font-size:34px;font-weight:700;color:{BL}", e(a_), bi("rise", 3) + DELAY(k * 100)))
    o.append(p(f"position:absolute;left:260px;top:{y + 24}px;font-size:30px;font-weight:700;color:{INK}", e(b_), bi("rise", 3) + DELAY(k * 100)))
    o.append(p(f"position:absolute;left:800px;top:{y + 26}px;font-size:28px;color:{SUB}", e(c_), bi("rise", 3) + DELAY(k * 100)))
o.append(f'<div{bi("fade", 3)} style="position:absolute;left:96px;top:{TY + 192}px;width:1728px;height:1px;background:{LINE}"></div>')
o.append(caption("직접 칠 때는 -it, 파일을 넘길 때는 -i예요.", TY + 222, 4, size=30))
W("w-trap", o, "꺾쇠로 파일을 넘길 때 -it를 쓰면 거절돼요. 앞에서 psql을 열 때는 늘 -it를 써서 습관처럼 붙이기 쉬워요. 오류 문장은 stdin is not a terminal, 입력이 터미널이 아니라는 뜻이에요. -it는 -i와 -t 두 옵션을 붙여 쓴 거예요. -i는 입력을 이어 주고, -t는 키보드로 치는 화면을 이어 줘요. 꺾쇠로 파일을 넘기면 입력이 키보드가 아니라 파일이라서 -t를 붙일 수 없어요. 그래서 -i만 써요. 직접 칠 때는 -it, 파일을 넘길 때는 -i, 이렇게 기억해요." + REAL)

# =====================================================================
# part 4: volumes
# =====================================================================
o = frame("v-cmds", EB4, "볼륨은 create로 만들고 ls로 보고 inspect로 자세히 봐요", C4)
rows = [("$", P_KS, C("v-create"))] + out_rows("v-create") + [("$", P_KS, C("v-ls"))] + out_rows("v-ls") + [("$", P_KS, C("v-inspect"))] + out_rows("v-inspect")
t = Term(rows, 96, 214, size=23, w=1100, lh=1.42, tid="t-vol")
o.append(t.html())
mpi = next(i for i, r in enumerate(rows) if "Mountpoint" in r[1])
nmi = next(i for i, r in enumerate(rows) if '"Name"' in r[1])
o.append(underline(1, t.sx(mpi, "/var/lib"), t.sx(mpi, "/var/lib") + t.sw("/var/lib/docker/volumes/pgdata/_data"), t.top(mpi) + t.lp - 2, OR))
o += tag(t, nmi, "이름", C4, 1, gap=30)
vc = [("docker volume create pgdata", "이름 붙여 만들기"), ("docker volume ls", "볼륨 목록"), ("docker volume inspect pgdata", "자세히 보기 (어디에 저장되는지)"), ("docker volume rm pgdata", "지우기 (쓰는 컨테이너가 없을 때)")]
for k, (c_, d_) in enumerate(vc):
    y = 230 + k * 150
    o.append(p(f"position:absolute;left:1250px;top:{y}px;font-family:{MONO};font-size:25px;font-weight:700;color:{C4};white-space:nowrap", e(c_), bi("rise", 2) + DELAY(k * 90)))
    o.append(p(f"position:absolute;left:1250px;top:{y + 46}px;width:574px;font-size:24px;line-height:1.4;color:{SUB}", e(d_), bi("rise", 2) + DELAY(k * 90)))
o.append(caption("Mountpoint는 Docker가 데이터를 두는 곳이에요. 직접 열지 않고 컨테이너로 읽어요.", t.y + t.h + 34, 3, size=27))
W("v-cmds", o, "볼륨은 붕어빵 밖 보관함이에요. 30에서는 docker run에 -v를 쓰면 볼륨이 저절로 생겼어요. 수업에서는 docker volume create pgdata로 먼저 만들어 두는 방법도 봤어요. 결과는 같아요. docker volume ls로 목록을 보면 pgdata가 보여요. docker volume inspect는 볼륨 하나를 자세히 보여 줘요. Name은 이름, Mountpoint는 Docker가 실제로 데이터를 두는 폴더예요. 이 폴더는 Docker가 관리하는 곳이라 직접 열어서 고치지 않고, 볼륨을 붙인 컨테이너로 읽고 써요. 지울 때는 docker volume rm이에요. 쓰는 컨테이너가 있으면 지워지지 않는데, 두 장 뒤에서 봐요." + REAL, ("p4", "볼륨"))

o = frame("v-keep", EB4, "볼륨을 붙이면 컨테이너를 지워도 상품이 남아요", C4)
rows = [("$", P_KS, RUNV, {"-v pgdata:/var/lib/postgresql": f'style="color:{C4}"'})] + [("o", D["v-run"][0]["out"][0])] + [("$", P_KS, C("v-load"))] + [("d", "… 결과 6줄 줄임 (마지막 줄 INSERT 0 5)")] + [("$", P_KS, C("v-gone", 0)), ("o", "my-pg"), ("$", P_KS, C("v-gone", 1)), ("o", "my-pg"), ("$", P_KS, C("v-rerun"), {"-v pgdata:/var/lib/postgresql": f'style="color:{C4}"'}), ("o", D["v-rerun"][0]["out"][0]), ("$", P_KS, SEL)] + [("o", l) for l in RA("v-kept")]
t = Term(rows, 96, 214, size=19, w=1728, lh=1.45, tid="t-keep")
o.append(t.html())
o += tag(t, 6, "컨테이너를 지웠어요", RED, 1, gap=30)
o += tag(t, 9, "같은 볼륨으로 새로 켰어요", C4, 2, gap=30)
sel0 = 10
o.append(spot(3, x=t.x + 10, y=round(t.top(sel0 + 1) - 6), w=900, h=round(8 * t.lp + 12)))
o.append(spot_off(4))
o.append(caption("붕어빵(컨테이너)은 새로 찍었지만 보관함(pgdata)은 그대로라 상품 다섯 개가 다시 보여요.", t.y + t.h + 30, 4, size=28))
W("v-keep", o, "볼륨을 붙이면 컨테이너를 지워도 상품이 남아요. 수업 명령에 -v pgdata:/var/lib/postgresql을 붙여 켰어요. 34에서 본 것처럼 PostgreSQL 18은 데이터를 /var/lib/postgresql에 둬요. 그 자리에 pgdata 볼륨을 붙였어요. 상품 다섯 개를 넣은 뒤 stop과 rm으로 컨테이너를 지웠어요. 같은 -v로 새 컨테이너를 켜고 SELECT를 하면 상품 다섯 개가 그대로 나와요. 붕어빵은 새로 찍었지만 보관함은 그대로 있어서 그래요. 볼륨 없이 지우면 kant_shop 데이터베이스도 같이 사라져요." + REAL)

o = frame("v-rm", EB4, "쓰고 있는 볼륨은 지울 수 없어요", C4)
rows = [("$", P_KS, C("v-rm-used"))] + out_rows("v-rm-used", rew=110) + [("o", ""), ("d", "… docker stop my-pg, docker rm my-pg 뒤"), ("$", P_KS, C("v-rm"))] + out_rows("v-rm") + [("$", P_KS, C("v-ls2"))] + out_rows("v-ls2")
t = Term(rows, 96, 214, size=24, w=1728, lh=1.5, tid="t-vrm")
o.append(t.html())
o.append(underline(1, t.sx(1, "volume is in use"), t.sx(1, "volume is in use") + t.sw("volume is in use"), t.top(1) + t.lp - 2, RED))
TY = t.y + t.h + 56
o.append(p(f"position:absolute;left:96px;top:{TY}px;font-size:26px;font-weight:700;color:{GRAY}", "-v 뒤에 오는 것 두 가지 (30에서 배웠어요)", bi("fade", 2)))
cmp_ = [("-v pgdata:/var/lib/postgresql", "볼륨", "Docker가 관리하는 보관함, 데이터베이스 파일"), ("-v ./site:/usr/share/nginx/html", "내 폴더", "내가 직접 열어 고치는 파일, 웹 페이지")]
for k, (a_, b_, c_) in enumerate(cmp_):
    y = TY + 56 + k * 90
    o.append(f'<div{bi("fade", 2)} style="position:absolute;left:96px;top:{y}px;width:1728px;height:1px;background:{LINE}"></div>')
    o.append(p(f"position:absolute;left:96px;top:{y + 22}px;font-family:{MONO};font-size:27px;font-weight:700;color:{C4 if k == 0 else INK};white-space:nowrap", e(a_), bi("rise", 2) + DELAY(k * 100)))
    o.append(p(f"position:absolute;left:820px;top:{y + 24}px;font-size:27px;font-weight:700;color:{INK}", e(b_), bi("rise", 2) + DELAY(k * 100)))
    o.append(p(f"position:absolute;left:1060px;top:{y + 25}px;font-size:25px;color:{SUB}", e(c_), bi("rise", 2) + DELAY(k * 100)))
o.append(f'<div{bi("fade", 2)} style="position:absolute;left:96px;top:{TY + 56 + 180}px;width:1728px;height:1px;background:{LINE}"></div>')
W("v-rm", o, "쓰고 있는 볼륨은 지울 수 없어요. my-pg가 pgdata를 붙인 채 켜져 있을 때 docker volume rm을 치면 volume is in use, 쓰는 중이라는 오류가 나요. 꺾쇠 안의 긴 글자는 그 볼륨을 쓰는 컨테이너 ID예요. 컨테이너를 끄고 지운 다음에 rm을 치면 지워져요. 볼륨을 지우면 안의 데이터도 사라지니, 다시 쓸 데이터라면 지우지 않아요. 아래 표는 30에서 배운 -v의 두 가지 모양이에요. 이름을 쓰면 Docker가 관리하는 볼륨이고, 점과 슬래시로 시작하면 내 폴더를 그대로 연결해요. 데이터베이스 파일은 볼륨에, 내가 고치는 웹 페이지는 내 폴더에 둬요." + REAL)

# =====================================================================
# part 5: YAML and compose
# =====================================================================
YL = COMPOSE.rstrip("\n").split("\n")
LVC = [INK, CY, CP, VO]     # colors by indentation level (0, 2, 4, 6 spaces)


def yaml_line(l, size=None):
    """one compose.yaml line with its key colored by level; list dashes and values stay ink"""
    n = len(l) - len(l.lstrip(" "))
    body = l.lstrip(" ")
    lv = min(n // 2, 3)
    m = re.match(r"^(- )?([A-Za-z_]+):(.*)$", body)
    if m and not m.group(1):
        h = f'<span style="color:{LVC[lv]};font-weight:700">{e(m.group(2))}</span>:{e(m.group(3))}'
    else:
        h = e(body)
    return " " * n + h


o = frame("y-what", EB5, "YAML은 \"이름: 값\"을 한 줄에 하나씩 적는 설정 파일 형식이에요", C5)
ed, g = editor("ed-y", "compose.yaml", [yaml_line(l) for l in YL], 96, 206, 820, fs=30, color=C5)
o.append(ed)
lab = [(0, "실행할 컨테이너(서비스) 목록, 꼭 있어야 해요", 1), (1, "서비스 이름, 직접 정해요 (db, web …)", 1),
       (2, "쓸 이미지:태그", 2), (3, "컨테이너 이름 (-​-name), 안 적으면 자동", 2), (4, "환경 변수 (-e)", 2),
       (6, "포트 연결 (-p), 따옴표로 감싸요", 2), (8, "볼륨 연결 (-v)", 2), (11, "쓸 볼륨 이름 적어 두기 (맨 바깥)", 3)]
for k, (i, t_, od) in enumerate(lab):
    y = gcy(g, i)
    x1 = gx(g, YL[i]) + 18
    o += leader(x1, y, 1000, C5 if i else INK, od, e(t_), size=25)
    o[-1] = o[-1].replace(f'data-build-in="rise order {od}"', f'data-build-in="rise order {od}"' + DELAY(k * 70))
legend = [("이름: 값", ": 뒤에 한 칸 띄어요"), ("- 값", "목록의 한 칸"), ("# 설명", "주석, 실행 안 해요")]
for k, (a_, b_) in enumerate(legend):
    x = 96 + k * 600
    o.append(p(f"position:absolute;left:{x}px;top:{g['top'] + g['h'] + 44:.0f}px;font-family:{MONO};font-size:28px;font-weight:700;color:{C5};white-space:nowrap", e(a_), bi("rise", 4) + DELAY(k * 90)))
    o.append(p(f"position:absolute;left:{x + tw(a_, 28) + 20:.0f}px;top:{g['top'] + g['h'] + 47:.0f}px;font-size:25px;color:{SUB};white-space:nowrap", e(b_), bi("rise", 4) + DELAY(k * 90)))
W("y-what", o, "YAML은 이름: 값을 한 줄에 하나씩 적는 설정 파일 형식이에요. compose.yaml의 yaml이 이 형식이라는 뜻이에요. 수업에서 쓸 모양 그대로 적었어요. 맨 위 services는 실행할 컨테이너 목록이라 꼭 있어야 해요. 그 아래 db는 서비스 이름이고 직접 정해요. db 안에 image, container_name, environment, ports, volumes를 적어요. docker run의 옵션과 하나씩 짝이 맞아요. ports는 따옴표로 감싸는 게 좋아요. 쌍점이 들어간 숫자를 YAML이 다른 값으로 읽지 않게 하려고요. 맨 아래 volumes는 이 파일에서 쓸 볼륨 이름을 적어 두는 자리예요. 아래 세 가지 모양만 알면 compose.yaml을 읽을 수 있어요. 쌍점 뒤에는 한 칸을 띄우고, 하이픈은 목록의 한 칸, 샵 뒤는 주석이에요.", ("p5", "YAML과 compose"))

o = frame("y-indent", EB5, "들여쓰기가 \"누구 안에 있는지\"를 정해요", C5)
ed, g = editor("ed-yi", "compose.yaml", [yaml_line(l) for l in YL], 96, 206, 760, fs=30, color=C5)
o.append(ed)
for lv in (1, 2, 3):
    rows_ = [i for i, l in enumerate(YL) if l.strip() and (len(l) - len(l.lstrip(" "))) >= lv * 2]
    segs_, cur = [], []
    for i in rows_:
        if cur and i != cur[-1] + 1:
            segs_.append(cur); cur = []
        cur.append(i)
    if cur:
        segs_.append(cur)
    for sg in segs_:
        x = g["tx"] + tw("  " * (lv - 1), g["fs"]) + 4
        o.append(f'<div{bi("fade", lv)} style="position:absolute;left:{x:.0f}px;top:{gtop(g, sg[0]):.0f}px;width:4px;height:{len(sg) * g["lh"]:.0f}px;border-radius:2px;background:{LVC[lv]}"></div>')
# nested boxes
BX, BY = 960, 214
o.append(f'<div id="nb-0"{bi("rise", 1)} style="position:absolute;left:{BX}px;top:{BY}px;width:864px;height:620px;border:3px solid {INK};border-radius:22px;background:#FFFFFF"></div>')
o.append(p(f"position:absolute;left:{BX + 26}px;top:{BY + 16}px;font-family:{MONO};font-size:26px;font-weight:700;color:{INK}", "services", bi("rise", 1)))
o.append(f'<div id="nb-1"{bi("rise", 2)} style="position:absolute;left:{BX + 30}px;top:{BY + 70}px;width:804px;height:520px;border:3px solid {CY};border-radius:20px;background:{CYBG}"></div>')
o.append(p(f"position:absolute;left:{BX + 56}px;top:{BY + 84}px;font-family:{MONO};font-size:26px;font-weight:700;color:{CY}", "db", bi("rise", 2)))
items = [("image", "postgres:18"), ("container_name", "my-pg"), ("environment", "POSTGRES_PASSWORD"), ("ports", "\"5432:5432\""), ("volumes", "pgdata:/var/lib/…")]
for k, (a_, b_) in enumerate(items):
    y = BY + 140 + k * 86
    sub_box = a_ in ("environment", "ports", "volumes")
    o.append(f'<div{bi("rise", 3)}{DELAY(k * 70)} style="position:absolute;left:{BX + 60}px;top:{y}px;width:744px;height:70px;border:3px solid {CP};border-radius:14px;background:#FFFFFF"></div>')
    o.append(p(f"position:absolute;left:{BX + 84}px;top:{y + 16}px;font-family:{MONO};font-size:24px;font-weight:700;color:{CP};white-space:nowrap", e(a_), bi("rise", 3) + DELAY(k * 70)))
    if sub_box:
        o.append(p(f"position:absolute;left:{BX + 380}px;top:{y + 12}px;height:40px;padding:0 14px;border-radius:9px;background:{VOBG};border:2px solid {VO};font-family:{MONO};font-size:21px;font-weight:700;line-height:36px;color:{VO};white-space:nowrap", e(b_), bi("rise", 3) + DELAY(k * 70 + 120)))
    else:
        o.append(p(f"position:absolute;left:{BX + 380}px;top:{y + 18}px;font-family:{MONO};font-size:22px;font-weight:700;color:{INK};white-space:nowrap", e(b_), bi("rise", 3) + DELAY(k * 70)))
o.append(caption("같은 칸에서 시작하는 줄끼리 형제예요. 한 단계 더 들어가면 위 줄의 안쪽이에요.", BY + 650, 4, left=BX, width=864, size=27))
W("y-indent", o, "들여쓰기가 누구 안에 있는지를 정해요. 28에서 파이썬 들여쓰기를 상자 안의 상자로 읽었어요. YAML도 똑같아요. services는 맨 바깥 상자예요. 두 칸 들어간 db는 services 안에 있어요. 네 칸 들어간 image부터 volumes까지는 db 안에 있는 형제예요. environment 아래 여섯 칸 들어간 POSTGRES_PASSWORD는 environment 안에 있어요. 왼쪽 코드의 세로줄이 오른쪽 상자와 같은 색이에요. 맨 아래 volumes는 다시 맨 앞에서 시작해서 services와 형제예요. 그래서 이 volumes는 db의 볼륨 연결이 아니라 파일 전체에서 쓸 볼륨을 적어 두는 곳이에요. YAML에는 괄호가 없어서 칸 수가 곧 구조예요.")

o = frame("y-24", EB5, "2칸이든 4칸이든, 같은 단계끼리 칸이 맞으면 똑같이 읽혀요", C5)
CB = f"position:absolute;left:96px;top:214px;width:770px;height:640px;background:{CARD};border:2px solid {LINE};border-radius:16px;padding:28px 34px;font-family:{MONO};font-size:27px;line-height:1.55;white-space:pre;color:{INK}"
def tok_lines(lines):
    out = []
    for i, l in enumerate(lines):
        n = len(l) - len(l.lstrip(" "))
        out.append((" " * n) + (tok(f"y{i}", yaml_line(l.lstrip(' '))) if l.strip() else ""))
    return "\n".join(out)
o.append(p(CB, tok_lines(YL), ' id="y2"' + MORPH_FROM()))
o.append(p(CB, tok_lines(COMPOSE_FOUR.rstrip("\n").split("\n")), ' id="y4"' + MORPH(1, "y2")))
o.append(p(f"position:absolute;left:120px;top:870px;font-size:26px;font-weight:700;color:{CY}", "한 단계에 4칸으로 바꿨어요", bi("rise", 1)))
rows = [("$", P_KS, C("four-up"))] + [("o", l) for l in RA("four-up")]
t = Term(rows, 900, 214, size=17, w=924, lh=1.5, tid="t-four")
o.append(f'<div{bi("rise", 2)}>' + t.html() + '</div>')
o.append(p(f"position:absolute;left:900px;top:{t.y + t.h + 18}px;font-size:26px;font-weight:700;color:{GR}", "4칸 파일로도 그대로 켜져요", bi("rise", 2)))
tb = [("", "YAML", "파이썬 (28)"), ("관례", "2칸", "4칸"), ("꼭 지킬 것", "같은 단계는 같은 칸", "같은 단계는 같은 칸"), ("탭", "못 써요 (오류)", "쓰지 않아요")]
for k, (a_, b_, c_) in enumerate(tb):
    y = 520 + k * 80
    o.append(f'<div{bi("fade", 3)} style="position:absolute;left:900px;top:{y}px;width:924px;height:1px;background:{LINE}"></div>')
    st = "font-weight:700;color:" + (GRAY if k == 0 else INK)
    o.append(p(f"position:absolute;left:900px;top:{y + 22}px;font-size:25px;font-weight:700;color:{GRAY};white-space:nowrap", e(a_), bi("rise", 3) + DELAY(k * 80)))
    o.append(p(f"position:absolute;left:1130px;top:{y + 22}px;font-size:25px;{st if k else 'font-weight:700;color:' + CY};white-space:nowrap", e(b_), bi("rise", 3) + DELAY(k * 80)))
    o.append(p(f"position:absolute;left:1470px;top:{y + 22}px;font-size:25px;{st};white-space:nowrap", e(c_), bi("rise", 3) + DELAY(k * 80)))
o.append(f'<div{bi("fade", 3)} style="position:absolute;left:900px;top:{520 + 4 * 80}px;width:924px;height:1px;background:{LINE}"></div>')
o.append(caption("compose.yaml은 2칸으로 적어요. Docker 공식 문서와 수업 자료가 2칸이에요.", 920, 4, size=28))
W("y-24", o, "2칸이든 4칸이든, 같은 단계끼리 칸이 맞으면 똑같이 읽혀요. 왼쪽 파일을 한 단계에 네 칸씩 들어가게 바꿨어요. 이 파일로 docker compose up -d를 쳐도 아무 문제 없이 켜져요. YAML이 보는 건 칸 수 자체가 아니라, 어떤 줄이 위 줄보다 더 들어갔는지, 같은 칸에서 시작하는지예요. 파이썬은 28에서 4칸으로 배웠고, YAML은 보통 2칸으로 적어요. Docker 공식 문서와 수업 자료도 2칸이에요. 한 파일 안에서는 한 가지로 맞춰요. 그리고 YAML에서는 탭을 쓸 수 없어요. 다음 장에서 실제 오류를 봐요." + REAL)

o = frame("y-err", EB5, "탭, 어긋난 칸, 쌍점 뒤 띄어쓰기에서 오류가 나요", C5)
cases = [("tab", COMPOSE_TAB, 2, "탭으로 들여썼어요", "L3.C1", "3번째 줄 1번째 칸에 탭"),
         ("mix", COMPOSE_MIX, 3, "한 줄만 2칸이에요", "L5.C16", "4번째 줄이 어긋나서 다음 줄에서 오류"),
         ("colon", COMPOSE_COLON, 2, "image: 뒤에 띄어쓰기가 없어요", "L4.C19", "위 줄이 값 하나로 읽혀서 다음 줄에서 오류")]
for k, (nm, txt, bad, what, pos, why_) in enumerate(cases):
    y = 214 + k * 268
    ls_ = txt.split("\n")[1:5]
    o.append(f'<div{bi("rise", k + 1)} style="position:absolute;left:96px;top:{y}px;width:640px;height:236px;background:{CARD};border:2px solid {LINE};border-radius:16px"></div>')
    o.append(f'<div{bi("rise", k + 1)} style="position:absolute;left:98px;top:{y + 20 + (bad - 1) * 48}px;width:636px;height:48px;background:#A3313118;border-left:6px solid {RED}"></div>')
    for j, l in enumerate(ls_):
        shown = e(l).replace("\t", f'<span style="color:{RED}">⇥   </span>')
        o.append(p(f"position:absolute;left:150px;top:{y + 26 + j * 48}px;font-family:{MONO};font-size:26px;line-height:36px;white-space:pre;color:{INK}", shown, bi("rise", k + 1)))
        o.append(p(f"position:absolute;left:104px;top:{y + 30 + j * 48}px;width:34px;text-align:right;font-family:{MONO};font-size:20px;line-height:30px;color:#A3A9B4", str(j + 2), bi("rise", k + 1)))
    o.append(p(f"position:absolute;left:780px;top:{y + 6}px;font-size:28px;font-weight:700;color:{RED}", e(what), bi("rise", k + 1)))
    msg = RA("y-" + nm)[0]
    mw = rewrap([msg], 60)
    o.append(p(f"position:absolute;left:780px;top:{y + 58}px;width:1044px;font-family:{MONO};font-size:22px;line-height:1.5;color:{INK};white-space:pre", e("\n".join(mw)).replace(pos, f'<span style="color:{RED};font-weight:700">{pos}</span>'), bi("rise", k + 1)))
    o.append(p(f"position:absolute;left:780px;top:{y + 58 + len(mw) * 33 + 14}px;font-size:24px;color:{SUB}", f'{pos} = {e(why_)}', bi("rise", k + 1)))
W("y-err", o, "YAML 오류는 세 가지가 가장 많아요. 첫 번째는 탭이에요. 화면에서는 탭 자리를 빨간 화살표로 보이게 그렸어요. 실제 편집기에서는 띄어쓰기와 똑같아 보여서 찾기 어려워요. 오류의 L3.C1은 3번째 줄 1번째 칸이라는 뜻이에요. VS Code는 YAML 파일에서 Tab 키를 누르면 띄어쓰기를 넣어 줘서, 다른 곳에서 복사해 온 탭이 문제가 돼요. 두 번째는 한 줄만 칸이 어긋난 경우예요. 4번째 줄을 2칸만 들여서 YAML이 5번째 줄에서 헷갈렸다고 알려 줘요. 세 번째는 쌍점 뒤에 띄어쓰기를 빠뜨린 경우예요. image:postgres:18 전체가 글자 하나로 읽혀서 다음 줄에서 오류가 나요. 두 번째와 세 번째처럼 오류 줄 번호는 실제로 틀린 줄의 다음 줄일 때가 많아요. 알려 준 줄과 그 바로 위 줄을 같이 봐요." + REAL)

o = frame("c-map", EB5, "docker run의 옵션이 compose.yaml의 칸으로 옮겨 가요", C5)
pairs = [("--name my-pg", "container_name: my-pg", BL), ("-e POSTGRES_PASSWORD=admin1234", "environment:\n  POSTGRES_PASSWORD: admin1234", GR),
         ("-p 5432:5432", "ports:\n  - \"5432:5432\"", OR), ("-v pgdata:/var/lib/postgresql", "volumes:\n  - pgdata:/var/lib/postgresql", VO), ("postgres:18", "image: postgres:18", MAG)]
o.append(p(f"position:absolute;left:96px;top:222px;font-family:{MONO};font-size:28px;font-weight:700;color:{INK}", "docker run -d"))
o.append(p(f"position:absolute;left:1000px;top:222px;font-family:{MONO};font-size:28px;font-weight:700;color:{INK}", "services:  db:"))
o.append(p(f"position:absolute;left:96px;top:270px;font-size:23px;color:{SUB}", "한 줄 명령"))
o.append(p(f"position:absolute;left:1000px;top:270px;font-size:23px;color:{SUB}", "compose.yaml (db 안쪽, 4칸 들여쓰기는 줄였어요)"))
for k, (a_, b_, c) in enumerate(pairs):
    y = 330 + k * 128
    o.append(p(f"position:absolute;left:96px;top:{y}px;height:60px;padding:0 20px;border-radius:12px;background:{c}14;border:2px solid {c};font-family:{MONO};font-size:28px;font-weight:700;line-height:56px;color:{c};white-space:nowrap", e(a_), f' id="mp-a{k}"'))
    x1 = 96 + tw(a_, 28) + 44 + 16
    o.append(line_arrow(x1, y + 30, 984, y + 30, c, k // 2 + 1, width=3, dash="2 9"))
    o.append(p(f"position:absolute;left:1000px;top:{y - (8 if chr(10) in b_ else -6)}px;padding:6px 20px;border-radius:12px;background:#FFFFFF;border:2px solid {c};font-family:{MONO};font-size:28px;font-weight:700;line-height:1.45;color:{c};white-space:pre", e(b_), f' data-build-in="fly order {k // 2 + 1}" data-from="mp-a{k}"' + DELAY(k % 2 * 160)))
o.append(caption("-d는 docker compose up -d에 붙여요. 옵션 하나가 칸 하나예요.", 330 + 5 * 128 + 10, 4, size=28))
W("c-map", o, "docker run의 옵션이 compose.yaml의 칸으로 옮겨 가요. 왼쪽은 수업에서 친 긴 docker run을 옵션별로 끊은 거예요. 오른쪽은 같은 내용을 compose.yaml의 db 안에 적은 거예요. --name은 container_name, -e는 environment, -p는 ports, -v는 volumes, 맨 끝 이미지 이름은 image로 가요. -d는 파일에 적지 않고 docker compose up -d처럼 명령에 붙여요. 옵션과 칸이 하나씩 짝이 맞아서, 긴 docker run을 compose.yaml로 바꾸거나 거꾸로 읽을 때 이 표를 보면 돼요.")

o = frame("c-config", EB5, "compose config는 파일을 읽은 그대로 펼쳐 보여 줘요", C5)
cfg = RA("c-config")
rows = [("$", P_KS, C("c-config"))] + [("o", l) for l in cfg]
t = Term(rows, 96, 206, size=19, w=900, lh=1.38, tid="t-cfg")
o.append(t.html())
nm = next(i for i, r in enumerate(rows) if r[1].startswith("name: kant-shop"))
vn = next(i for i, r in enumerate(rows) if "name: kant-shop_pgdata" in r[1])
cn = next(i for i, r in enumerate(rows) if "container_name: my-pg" in r[1])
o += tag(t, nm, "폴더 이름이 프로젝트 이름", C5, 1, gap=30)
o += tag(t, cn, "내가 적은 칸", C5, 1, gap=30)
o += tag(t, vn, "볼륨 이름 앞에 kant-shop_", OR, 2, gap=30)
o.append(p(f"position:absolute;left:1260px;top:{t.y + 30}px;width:564px;font-size:30px;font-weight:700;line-height:1.45;color:{INK}", "up 하기 전에 쳐 봐요", bi("rise", 3)))
o.append(p(f"position:absolute;left:1260px;top:{t.y + 110}px;width:564px;font-size:26px;line-height:1.6;color:{SUB}", "파일에 오류가 있으면 여기서 오류가 나요. 오류가 없으면 Docker가 알아들은 내용을 빠짐없이 펼쳐 보여 줘요. 순서가 바뀌고 안 적은 칸이 채워져 있어도 괜찮아요.", bi("rise", 3)))
W("c-config", o, "docker compose config는 compose.yaml을 읽은 그대로 펼쳐 보여 줘요. 내가 적은 칸은 그대로 있고, 안 적은 칸은 Docker가 기본값으로 채워 넣어요. 순서도 이름순으로 바뀌어요. 눈여겨볼 곳이 두 군데 있어요. 맨 위 name: kant-shop은 폴더 이름이 프로젝트 이름이 된다는 뜻이에요. 맨 아래 볼륨 이름은 kant-shop_pgdata예요. compose로 만든 볼륨에는 앞에 프로젝트 이름이 붙어요. 4파트에서 docker volume create로 만든 pgdata와는 다른 볼륨이에요. compose.yaml을 고친 뒤 up 하기 전에 config를 쳐 보면, YAML 오류는 여기서 먼저 나와요." + REAL)

o = frame("c-run", EB5, "up -d로 켜고 ps로 보고 exec로 들어가요", C5)
rows = [("$", P_KS, C("c-up"))] + [("o", l) for l in RA("c-up")] + [("$", P_KS, C("c-ps"))] + [("o", l) for l in RA("c-ps")] + [("$", P_KS, C("c-load"))] + [("d", "… 결과 6줄 줄임 (마지막 줄 INSERT 0 5)")] + [("$", P_KS, C("c-exec"))] + [("o", l) for l in RA("c-exec")]
t = Term(rows, 96, 206, size=20, w=1728, lh=1.6, tid="t-crun")
o.append(t.html())
cm = [i for i, r in enumerate(rows) if r[0] == "$"]
labs = ["네트워크, 볼륨, 컨테이너를 한 번에 만들어요", "SERVICE 칸에 서비스 이름 db", "컨테이너 이름 my-pg로도 돼요", "compose exec 뒤에는 서비스 이름"]
for k, i in enumerate(cm):
    o.append(spot(k + 1, x=t.x + 10, y=round(t.top(i) - 5), w=t.w - 20, h=round(t.lp + 10), dim=0.5))
o.append(spot_off(5))
for k, i in enumerate(cm):
    o += tag(t, i, labs[k], C5, k + 1, gap=30)
W("c-run", o, "docker compose up -d로 켜고, ps로 보고, exec로 들어가요. up -d는 compose.yaml을 읽어서 네트워크, 볼륨, 컨테이너를 한 번에 만들고 켜요. docker compose ps는 이 폴더의 compose.yaml로 켠 컨테이너만 보여 줘요. SERVICE 칸에 서비스 이름 db가 보여요. container_name을 my-pg로 적어서, 3파트의 docker exec -i my-pg 명령을 그대로 써도 돼요. docker compose exec도 있어요. 이건 컨테이너 이름이 아니라 서비스 이름 db를 적어요. compose exec는 -it를 안 붙여도 들어가서 칠 수 있어요." + REAL)

o = frame("c-life", EB5, "logs, stop, start, restart 앞에 compose만 붙여요", C5)
rows = [("$", P_KS, C("c-logs"))] + [("o", short_log(l.replace("my-pg  | ", "my-pg  | "))) for l in RA("c-logs")] + [("$", P_KS, C("c-logs-f"))] + [("o" if l != "^C" else "y", l) for l in RA("c-logs-f")] + \
       [("$", P_KS, C("c-stop"))] + [("o", l) for l in RA("c-stop")] + [("$", P_KS, C("c-ps-stop"))] + [("o", l) for l in RA("c-ps-stop")] + [("$", P_KS, C("c-start"))] + [("o", l) for l in RA("c-start")] + [("$", P_KS, C("c-restart"))] + [("o", l) for l in RA("c-restart")]
t = Term(rows, 96, 206, size=19, w=1728, lh=1.5, tid="t-life")
o.append(t.html())
cm = [i for i, r in enumerate(rows) if r[0] == "$"]
o += tag(t, cm[0], "줄 앞에 컨테이너 이름이 붙어요", C5, 1, gap=30)
o += tag(t, cm[1], "Ctrl+C로 멈춰요", OR, 1, gap=30)
ex = next(i for i, r in enumerate(rows) if "Exited" in r[1])
o.append(underline(2, t.sx(ex, "Exited"), t.sx(ex, "Exited") + t.sw("Exited (0)"), t.top(ex) + t.lp - 2, GRAY))
o += tag(t, cm[3], "ps -a로 꺼진 것까지", C5, 2, gap=30)
o += tag(t, cm[5], "껐다가 바로 켜요", C5, 3, gap=30)
W("c-life", o, "logs, stop, start, restart는 2파트에서 본 명령 앞에 compose만 붙이면 돼요. 이름을 안 적어도 이 폴더의 compose.yaml에 있는 서비스 전부에 적용돼요. compose logs는 줄 앞에 컨테이너 이름이 붙어요. 서비스가 여러 개일 때 누가 남긴 기록인지 알 수 있어요. --tail과 -f도 똑같이 써요. compose stop으로 끄면 compose ps에는 안 보이고 ps -a에 Exited로 남아요. compose start로 다시 켜고, restart는 껐다가 바로 켜요. 컨테이너를 지우지 않으니 데이터는 그대로예요. 화면에서는 기록 줄 앞의 날짜와 번호를 줄였어요." + REAL)

o = frame("c-down", EB5, "down은 컨테이너를 지우고 볼륨은 남겨요. down -v는 볼륨까지 지워요", C5)
rows = [("$", P_KS, C("c-down"))] + [("o", l) for l in RA("c-down")] + [("$", P_KS, C("c-vol"))] + [("o", l) for l in RA("c-vol")] + [("$", P_KS, C("c-up2"))] + [("o", l) for l in RA("c-up2")] + [("$", P_KS, C("c-kept"))] + [("o", l) for l in RA("c-kept")][:4] + [("d", "… (5 rows)")] + [("$", P_KS, C("c-downv"))] + [("o", l) for l in RA("c-downv")] + [("$", P_KS, C("c-vol2"))] + [("o", l) for l in RA("c-vol2")]
t = Term(rows, 96, 206, size=18, w=1728, lh=1.5, tid="t-down")
o.append(t.html())
v1 = next(i for i, r in enumerate(rows) if r[1].strip().endswith("kant-shop_pgdata") and "local" in r[1])
o.append(spot(1, x=t.x + 10, y=round(t.top(v1) - 5), w=700, h=round(t.lp + 10)))
o.append(spot_off(2))
o += tag(t, v1, "down 뒤에도 볼륨이 남아요", C4, 2, gap=30)
kp = next(i for i, r in enumerate(rows) if "무선 이어폰" in r[1])
o += tag(t, kp, "다시 up 하면 상품이 그대로", GR, 3, gap=30)
vr = next(i for i, r in enumerate(rows) if "Volume kant-shop_pgdata   Removed" in r[1])
o += tag(t, vr, "-v는 볼륨까지 지워요", RED, 4, gap=30)
W("c-down", o, "docker compose down은 컨테이너와 네트워크를 지우고 볼륨은 남겨요. 33, 34에서 본 그대로예요. down 뒤에 docker volume ls를 치면 kant-shop_pgdata가 남아 있어요. 그래서 다시 up -d로 켜면 kant_shop의 상품이 그대로 나와요. 수업이 끝나고 내일 다시 켤 때 이렇게 쓰면 돼요. down -v는 볼륨까지 지워요. Removed 줄에 Volume이 보이고, volume ls가 비어요. 데이터를 처음부터 다시 만들고 싶을 때만 -v를 붙여요." + REAL)

o = frame("c-name", EB5, "container_name을 빼면 이름이 \"폴더-서비스-1\"로 붙어요", C5)
rows = [("$", P_KS, C("n-up"))] + [("o", l) for l in RA("n-up")] + [("$", P_KS, C("n-ps"))] + [("o", l) for l in RA("n-ps")] + [("$", P_KS, C("n-exec"))] + out_rows("n-exec")
t = Term(rows, 96, 206, size=19, w=1728, lh=1.45, tid="t-noname")
o.append(t.html())
ni = next(i for i, r in enumerate(rows) if r[1].startswith("kant-shop-db-1"))
o.append(pen_box(1, round(t.sx(ni, "kant-shop-db-1") - 6), round(t.top(ni) - 2), round(t.sw("kant-shop-db-1") + 12), round(t.lp + 4), C5))
o.append(underline(2, t.sx(len(rows) - 1, "No such container"), t.sx(len(rows) - 1, "No such container") + t.sw("No such container: my-pg"), t.top(len(rows) - 1) + t.lp - 2, RED))
CY0 = t.y + t.h + 40
more = [("docker compose ls", "compose로 켠 프로젝트 목록", RA("c-ls")[1].split()[0] + "  " + RA("c-ls")[1].split()[1]),
        ("docker compose pull", "compose.yaml의 이미지를 미리 받기", RA("c-pull")[1].strip().replace("  ", " ")[:40])]
o.append(p(f"position:absolute;left:96px;top:{CY0}px;font-size:26px;font-weight:700;color:{GRAY}", "그 밖의 compose 명령", bi("fade", 3)))
for k, (a_, b_, c_) in enumerate(more):
    y = CY0 + 54 + k * 84
    o.append(f'<div{bi("fade", 3)} style="position:absolute;left:96px;top:{y}px;width:1728px;height:1px;background:{LINE}"></div>')
    o.append(p(f"position:absolute;left:96px;top:{y + 22}px;font-family:{MONO};font-size:27px;font-weight:700;color:{C5};white-space:nowrap", e(a_), bi("rise", 3) + DELAY(k * 90)))
    o.append(p(f"position:absolute;left:640px;top:{y + 24}px;font-size:26px;color:{INK};white-space:nowrap", e(b_), bi("rise", 3) + DELAY(k * 90)))
    o.append(p(f"position:absolute;left:1220px;top:{y + 24}px;font-family:{MONO};font-size:22px;color:{SUB};white-space:nowrap", e(c_), bi("rise", 3) + DELAY(k * 90)))
o.append(f'<div{bi("fade", 3)} style="position:absolute;left:96px;top:{CY0 + 54 + 168}px;width:1728px;height:1px;background:{LINE}"></div>')
W("c-name", o, "container_name을 빼면 이름이 폴더-서비스-1로 붙어요. compose.yaml에서 container_name 한 줄만 지우고 켰어요. 컨테이너 이름이 kant-shop-db-1이 됐어요. 폴더 이름 kant-shop, 서비스 이름 db, 그리고 첫 번째라는 뜻의 1이에요. 31에서 본 cafe-web-1과 같은 규칙이에요. 이때 docker exec my-pg를 치면 No such container, 그런 컨테이너가 없다는 오류가 나요. container_name을 적었는지에 따라 쓸 이름이 달라져요. 헷갈리면 docker compose exec db처럼 서비스 이름으로 들어가면 늘 돼요. 아래 두 개는 가끔 쓰는 명령이에요. compose ls는 compose로 켠 프로젝트 목록, compose pull은 compose.yaml에 적은 이미지를 미리 받아요." + REAL)

# =====================================================================
# part 6: errors and real tasks
# =====================================================================
o = frame("x-errs", EB6, "오늘 만난 오류 여덟 가지를 한 장에 모았어요", C6)
errs = [("Conflict. The container name \"/my-pg\" is already in use", "같은 이름의 컨테이너가 있어요", "`docker rm my-pg` 뒤 다시"),
        ("Bind for 0.0.0.0:5432 failed: port is already allocated", "5432번을 다른 컨테이너가 써요", "하나 끄거나 `-p 5433:5432`"),
        ("invalid reference format  /  -e: command not found", "줄 끝 \\ 뒤에 띄어쓰기가 있어요", "`\\`로 줄을 끝내기"),
        ("cannot attach stdin to a TTY-enabled container", "< 파일과 -it를 같이 썼어요", "`-i`만 쓰기"),
        ("lstat …/kant_shop.sq: no such file or directory", "보낼 파일 이름이 틀렸거나 다른 폴더예요", "`ls`로 이름 확인"),
        ("No such container: my-pg", "container_name을 안 적어서 이름이 달라요", "`docker compose ps`로 이름 보기"),
        ("volume is in use", "그 볼륨을 쓰는 컨테이너가 있어요", "`stop`, `rm` 뒤 `volume rm`"),
        ("go-yaml load error … at L3.C1", "YAML에 탭, 어긋난 칸, 쌍점 뒤 띄어쓰기", "`docker compose config`로 확인")]
o.append(p(f"position:absolute;left:96px;top:214px;font-size:24px;font-weight:700;color:{GRAY}", "이런 글이 보이면"))
o.append(p(f"position:absolute;left:1340px;top:214px;font-size:24px;font-weight:700;color:{GRAY}", "이렇게 해요"))
for i, (q, a_, c_) in enumerate(errs):
    y = 258 + i * 92
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:1px;background:{LINE}"></div>')
    ra_ = bi("rise", 1 + i // 4) + DELAY(i % 4 * 70)
    o.append(p(f"position:absolute;left:96px;top:{y + 10}px;width:1220px;font-family:{MONO};font-size:23px;font-weight:700;color:{RED};white-space:nowrap", e(q), ra_))
    o.append(p(f"position:absolute;left:96px;top:{y + 50}px;width:1220px;font-size:23px;color:{SUB}", e(a_), ra_))
    segs = c_.split("`")
    rich = "".join(f'<span style="font-family:{MONO};font-size:22px;color:{C3}">{e(sg)}</span>' if j % 2 else e(sg) for j, sg in enumerate(segs))
    o.append(p(f"position:absolute;left:1340px;top:{y + 28}px;width:484px;font-size:25px;font-weight:700;color:{INK};white-space:nowrap", rich, ra_))
o.append(f'<div style="position:absolute;left:96px;top:{258 + len(errs) * 92}px;width:1728px;height:1px;background:{LINE}"></div>')
W("x-errs", o, "오늘 만난 오류 여덟 가지를 모았어요. 앞 넷은 docker run과 3파트에서, 뒤 넷은 볼륨과 compose에서 봤어요. 이름 겹침과 포트 겹침은 29에서도 본 오류예요. invalid reference format과 command not found가 같이 나오면 줄 끝 백슬래시 뒤에 띄어쓰기가 있는지 봐요. cannot attach stdin은 꺾쇠로 파일을 넘기면서 -it를 쓴 경우예요. lstat no such file은 docker cp로 보낼 파일을 못 찾았다는 뜻이에요. 이름 오타이거나 다른 폴더에서 쳤을 때 나요. No such container는 compose에서 container_name을 안 적었을 때 자주 봐요. volume is in use가 나오면 그 볼륨을 쓰는 컨테이너를 먼저 지워요. go-yaml로 시작하면 compose.yaml의 YAML 오류예요. 줄과 칸 번호를 보고 config로 다시 확인해요." + REAL, ("p6", "오류와 실제 상황"))

o = frame("e-class", EB6, "예제 1. 수업 흐름 그대로: 켜고, 넣고, 실행하고, 확인해요", C6)
steps = [("1", "켜기", "docker run -d \\\n  --name my-pg \\\n  -e POSTGRES_PASSWORD=admin1234 \\\n  -p 5432:5432 postgres:18", C2),
         ("2", "넣기", "docker cp kant_shop.sql \\\n  my-pg:/tmp/kant_shop.sql", C3),
         ("3", "실행하기", "docker exec -it my-pg \\\n  psql -U postgres \\\n  -f /tmp/kant_shop.sql", C3),
         ("4", "확인하기", "docker exec -it my-pg \\\n  psql -U postgres -d kant_shop \\\n  -c \"SELECT * FROM product\"", GR)]
for k, (n_, h_, c_, col) in enumerate(steps):
    x = 96 + k * 438
    o.append(f'<div{bi("rise", k + 1)} style="position:absolute;left:{x}px;top:214px;width:414px;height:222px;border-radius:18px;background:{CARD};box-shadow:{SHADOW};border-top:6px solid {col};padding:22px 24px"' + DIM("ec") + '>'
             + p(f"font-size:28px;font-weight:900;color:{col}", n_ + ". " + e(h_))
             + p(f"margin-top:14px;font-family:{MONO};font-size:17px;font-weight:700;line-height:1.55;color:{INK};white-space:pre", e(c_)) + '</div>')
rows = [("$", P_KS, SEL)] + [("o", l) for l in RA("sel")]
t = Term(rows, 96, 476, size=25, w=1728, lh=1.5, tid="t-ec")
o.append(f'<div{bi("rise", 4)}>' + t.html() + '</div>')
o.append(caption("2, 3 대신 docker exec -i my-pg psql -U postgres &lt; kant_shop.sql 한 줄로 해도 돼요.", t.y + t.h + 26, 5, size=27))
W("e-class", o, "예제 1은 오늘 수업 순서 그대로예요. 네 단계로 정리했어요. 첫째, docker run으로 my-pg를 켜요. 둘째, docker cp로 kant_shop.sql을 컨테이너의 /tmp에 넣어요. 셋째, psql -f로 그 파일을 실행해요. 넷째, -d kant_shop과 -c로 SELECT를 실행해서 상품 다섯 개가 들어갔는지 확인해요. 아래가 마지막 단계의 실제 결과예요. 둘째와 셋째 단계는 3파트에서 본 방법 2, docker exec -i와 꺾쇠로 한 번에 할 수도 있어요. 카드의 명령은 백슬래시로 줄을 나눠 적었어요. 그대로 복사해서 쳐도 돼요." + REAL)

o = frame("e-compose", EB6, "예제 2. compose로 같은 일을 해요: 파일 두 개, 명령 세 줄", C6)
o.append(f'<div style="position:absolute;left:96px;top:214px;width:520px;height:620px;background:{CARD};border:3px solid {INK};border-radius:20px"></div>')
o.append(p(f"position:absolute;left:128px;top:236px;font-size:28px;font-weight:700;color:{INK}", "~/kant-shop"))
o.append(f'<div style="position:absolute;left:128px;top:296px;display:flex;flex-direction:row;gap:14px">' + file_chip("kant_shop.sql", size=22) + file_chip("compose.yaml", color=C5, size=22) + '</div>')
o.append(p(f"position:absolute;left:128px;top:374px;width:460px;font-family:{MONO};font-size:19px;line-height:1.5;white-space:pre;color:{INK}", "\n".join(yaml_line(l) for l in YL)))
rows = [("$", P_KS, C("e-up"))] + [("o", l) for l in RA("e-up")] + [("$", P_KS, C("e-load"))] + [("o", l) for l in RA("e-load")] + [("$", P_KS, C("e-sel"))] + [("o", l) for l in RA("e-sel")]
t = Term(rows, 654, 214, size=18, w=1170, lh=1.5, tid="t-eco")
o.append(t.html())
cm = [i for i, r in enumerate(rows) if r[0] == "$"]
for k, i in enumerate(cm):
    o.append(spot(k + 1, x=t.x + 10, y=round(t.top(i) - 5), w=t.w - 20, h=round(((cm[k + 1] if k + 1 < len(cm) else len(rows)) - i) * t.lp + 10), dim=0.5))
o.append(spot_off(4))
o.append(caption("내일은 docker compose up -d 한 줄이면 돼요. down만 했다면 상품도 그대로 있어요.", t.y + t.h + 30, 4, left=654, width=1170, size=26))
W("e-compose", o, "예제 2는 같은 일을 compose로 해요. 폴더에 kant_shop.sql과 compose.yaml 두 파일을 둬요. 첫째, docker compose up -d로 켜요. 긴 docker run이 compose.yaml에 들어 있어요. 둘째, docker exec -i my-pg psql -U postgres 꺾쇠 kant_shop.sql로 파일을 넘겨요. container_name을 my-pg로 적어서 수업 명령을 그대로 쓸 수 있어요. 셋째, SELECT로 확인해요. 다음 날에는 docker compose up -d 한 줄로 다시 켜요. 전날 down만 했다면 볼륨이 남아 있어서 상품도 그대로예요. 친구에게 이 폴더를 넘기면 친구도 같은 명령 세 줄로 똑같이 만들 수 있어요." + REAL)

o = frame("e-clean", EB6, "예제 3. 다 쓴 것은 컨테이너, 볼륨, 이미지 순서로 지워요", C6)
rows = [("$", P_KS, C("e-down"))] + [("o", l) for l in RA("e-down")] + [("$", P_KS, C("e-psa"))] + [("o", l) for l in RA("e-psa")] + [("$", P_KS, C("e-vol"))] + [("o", l) for l in RA("e-vol")] + [("$", P_KS, C("e-rmi"))] + [("o", l) for l in RA("e-rmi")] + [("$", P_KS, C("e-images"))] + [("o", l) for l in RA("e-images")]
t = Term(rows, 96, 214, size=20, w=1040, lh=1.55, tid="t-clean")
o.append(t.html())
cm = [i for i, r in enumerate(rows) if r[0] == "$"]
o.append(p(f"position:absolute;left:1190px;top:226px;font-size:28px;font-weight:700;color:{C5}", "compose로 켰다면", bi("rise", 1)))
o.append(p(f"position:absolute;left:1190px;top:280px;font-family:{MONO};font-size:24px;font-weight:700;line-height:1.7;color:{INK};white-space:pre", "docker compose down -v\ndocker rmi postgres:18", bi("rise", 1)))
o.append(p(f"position:absolute;left:1190px;top:470px;font-size:28px;font-weight:700;color:{C2}", "docker run으로 켰다면", bi("rise", 2)))
o.append(p(f"position:absolute;left:1190px;top:524px;font-family:{MONO};font-size:24px;font-weight:700;line-height:1.7;color:{INK};white-space:pre", "docker stop my-pg\ndocker rm my-pg\ndocker volume rm pgdata\ndocker rmi postgres:18", bi("rise", 2)))
o.append(caption("빈 ps -a, 빈 volume ls, 빈 images가 다 지운 모습이에요.", t.y + t.h + 30, 3, size=27))
o.append(caption("이미지는 다음 수업에 또 쓸 거라면 남겨 둬요. 지우면 다음에 pull부터 다시 해요.", 730, 3, left=1190, width=634, size=24, color=SUB))
W("e-clean", o, "예제 3은 다 쓴 것을 정리하는 순서예요. 컨테이너, 볼륨, 이미지 순서로 지워요. compose로 켰다면 docker compose down -v 한 줄로 컨테이너와 볼륨, 네트워크까지 지워져요. 그다음 docker rmi로 이미지를 지워요. ps -a, volume ls, images가 모두 비면 다 지운 거예요. docker run으로 켰다면 stop, rm, volume rm, rmi를 차례로 쳐요. 순서를 바꾸면 2파트와 4파트에서 본 오류가 나요. 볼륨을 지우면 상품 데이터도 사라지니 다시 쓸 거라면 남겨요. 이미지도 다음 수업에 또 쓸 거라면 남겨 두는 게 좋아요." + REAL)

# =====================================================================
# wrap-up
# =====================================================================
o = frame("s-alias", "정리", "인터넷 자료에는 같은 명령의 긴 이름도 나와요", INK)
al = [("docker ps", "docker container ls"), ("docker images", "docker image ls"), ("docker rm my-pg", "docker container rm my-pg"),
      ("docker rmi postgres:18", "docker image rm postgres:18"), ("docker exec -it my-pg bash", "docker container exec -it my-pg bash"), ("docker cp …", "docker container cp …")]
o.append(p(f"position:absolute;left:96px;top:220px;font-size:26px;font-weight:700;color:{GRAY}", "수업에서 쓰는 이름"))
o.append(p(f"position:absolute;left:820px;top:220px;font-size:26px;font-weight:700;color:{GRAY}", "같은 명령 (긴 이름)"))
for i, (a_, b_) in enumerate(al):
    y = 270 + i * 76
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:1px;background:{LINE}"></div>')
    o.append(p(f"position:absolute;left:96px;top:{y + 18}px;font-family:{MONO};font-size:28px;font-weight:700;color:{INK};white-space:nowrap", e(a_)))
    o.append(p(f"position:absolute;left:820px;top:{y + 18}px;font-family:{MONO};font-size:28px;font-weight:700;color:{BL};white-space:nowrap", e(b_), bi("rise", 1) + DELAY(i * 70)))
o.append(f'<div style="position:absolute;left:96px;top:{270 + len(al) * 76}px;width:1728px;height:1px;background:{LINE}"></div>')
rows = [("$", P_KS, C("container-ls"))] + [("o", l) for l in RA("container-ls")]
t = Term(rows, 96, 270 + len(al) * 76 + 40, size=18, w=1728, lh=1.5, tid="t-alias")
o.append(f'<div{bi("rise", 2)}>' + t.html() + '</div>')
o.append(caption("docker ps와 똑같은 표가 나와요. 어느 쪽을 쳐도 돼요.", t.y + t.h + 24, 2, size=26, color=SUB))
W("s-alias", o, "인터넷의 치트시트나 공식 문서에는 같은 명령이 긴 이름으로 나오기도 해요. docker ps는 docker container ls, docker images는 docker image ls와 똑같아요. 무엇에 대한 명령인지 container, image를 앞에 붙인 이름이에요. 아래는 docker container ls를 친 실제 화면이에요. docker ps와 같은 표가 나와요. 수업에서는 짧은 이름을 쓰고, 긴 이름이 보이면 이 표로 짝을 찾아요. 각 명령의 --help 맨 아래 Aliases 줄에 같은 명령 목록이 나와요. 표의 짝은 Docker 29.9.2의 --help에서 확인했어요." + REAL, ("wrap", "정리"))

o = frame("s-help", "정리", "옵션이 기억 안 나면 명령 뒤에 --help를 붙여요", INK)
hp = RA("help")
rows = [("$", P_KS, C("help"))] + [("o", l.replace("\t", "        ")) for l in hp]
t = Term(rows, 96, 206, size=21, w=1150, lh=1.4, tid="t-help")
o.append(t.html())
o.append(pen_box(1, t.x + 18, round(t.top(1) - 4), round(t.sw("        docker cp [OPTIONS] SRC_PATH|- CONTAINER:DEST_PATH") + 160), round(2 * t.lp + 8), OR))
ai = next(i for i, r in enumerate(rows) if r[1].startswith("Aliases"))
o.append(underline(2, t.tx, t.tx + t.sw("  docker container cp, docker cp"), t.top(ai + 1) + t.lp - 2, BL))
look = [("29", "설치, pull, run, ps, stop, rm, logs"), ("30", "exec, 볼륨, compose 맛보기"), ("31", "compose 서비스 여러 개, logs"), ("33·34", "-e, MySQL, PostgreSQL"), ("35", "오늘 모은 명령, 치트시트")]
o.append(p(f"position:absolute;left:1300px;top:220px;font-size:26px;font-weight:700;color:{GRAY}", "다시 볼 챕터", bi("fade", 3)))
for k, (a_, b_) in enumerate(look):
    y = 270 + k * 110
    o.append(p(f"position:absolute;left:1300px;top:{y}px;font-size:30px;font-weight:900;color:{DK}", e(a_), bi("rise", 3) + DELAY(k * 70)))
    o.append(p(f"position:absolute;left:1300px;top:{y + 48}px;width:524px;font-size:23px;color:{SUB}", e(b_), bi("rise", 3) + DELAY(k * 70)))
W("s-help", o, "옵션이 기억 안 나면 명령 뒤에 --help를 붙여요. docker cp --help를 치면 맨 위 Usage에 쓰는 모양이 두 줄 나와요. 첫 줄은 컨테이너에서 꺼내기, 둘째 줄은 컨테이너로 넣기예요. 대괄호 OPTIONS는 옵션을 넣을 수 있는 자리라는 뜻이에요. 아래 Aliases는 앞 장에서 본 긴 이름이고, Options는 붙일 수 있는 옵션 목록이에요. 영어지만 Usage 줄만 읽어도 순서를 알 수 있어요. 오른쪽은 명령마다 처음 배운 챕터예요. 자세한 설명이 필요하면 그 챕터 슬라이드로 돌아가요." + REAL)

# cheat sheets
def cheat(sid, title, groups, cols_w, notes, foot=None):
    o = frame(sid, "치트시트", title, INK)
    xs = [96]
    for w_ in cols_w[:-1]:
        xs.append(xs[-1] + w_ + 48)
    for gi, (gt, c, rows_) in enumerate(groups):
        x = xs[gi]
        o.append(p(f"position:absolute;left:{x}px;top:206px;font-size:28px;font-weight:700;color:{c}", e(gt)))
        o.append(f'<div style="position:absolute;left:{x}px;top:252px;width:{cols_w[gi]}px;height:3px;background:{c}"></div>')
        y = 272
        for k, d_ in rows_:
            fs = 20 if tw(k, 20) <= cols_w[gi] else 17
            o.append(p(f"position:absolute;left:{x}px;top:{y}px;width:{cols_w[gi]}px;font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:1.4;color:{INK};white-space:pre", e(k)))
            nl = k.count("\n") + 1
            o.append(p(f"position:absolute;left:{x}px;top:{y + nl * fs * 1.4 + 4:.0f}px;width:{cols_w[gi]}px;font-size:19px;line-height:1.35;color:{SUB}", e(d_)))
            y += nl * fs * 1.4 + 4 + 19 * 1.35 + 22
        if y > 1040:
            WARN.append(f"{sid}: column {gi} ends at {y:.0f}")
    if foot:
        o.append(caption(foot, 950, None, size=22, color=SUB))
    W(sid, o, notes)


cheat("cheat1", "docker 명령 한 장", [
    ("이미지", C2, [("docker pull postgres:18", "Docker Hub에서 받기"), ("docker images", "받은 이미지 목록"), ("docker rmi postgres:18", "지우기 (쓰는 컨테이너 먼저 지우기)")]),
    ("컨테이너", C2, [("docker run -d --name my-pg \\\n  -e POSTGRES_PASSWORD=admin1234 \\\n  -p 5432:5432 postgres:18", "뒤에서 켜기, 이름, 환경 변수, 포트"), ("docker ps / docker ps -a", "켜진 것 / 꺼진 것까지"), ("docker stop my-pg", "끄기"), ("docker start my-pg", "다시 켜기"), ("docker restart my-pg", "껐다가 바로 켜기"), ("docker logs --tail 3 my-pg", "마지막 3줄 (-f는 계속, Ctrl+C)"), ("docker rm my-pg", "지우기 (끈 다음에)")]),
    ("안에서 작업", C3, [("docker exec -it my-pg bash", "들어가기, exit로 나오기"), ("docker exec my-pg ls /tmp", "명령 하나만 실행"), ("docker exec -it my-pg \\\n  psql -U postgres -d kant_shop", "psql 열기, \\q로 나오기"), ("docker cp kant_shop.sql \\\n  my-pg:/tmp/kant_shop.sql", "내 파일을 컨테이너로"), ("docker exec -i my-pg \\\n  psql -U postgres < kant_shop.sql", "파일 내용 넘기기 (-it 말고 -i)")]),
    ("볼륨", C4, [("docker volume create pgdata", "만들기"), ("docker volume ls", "목록"), ("docker volume inspect pgdata", "자세히 보기"), ("-v pgdata:/var/lib/postgresql", "run에 붙여 연결"), ("docker volume rm pgdata", "지우기 (쓰는 컨테이너 먼저)")])],
    [330, 450, 450, 352],
    "docker 명령을 한 장에 모았어요. 왼쪽부터 이미지, 컨테이너, 컨테이너 안에서 작업하기, 볼륨이에요. 모든 예시는 오늘 수업 이름 그대로예요. 컨테이너는 my-pg, 비밀번호는 admin1234, 데이터베이스는 kant_shop, 볼륨은 pgdata예요. 긴 명령은 백슬래시로 줄을 나눠 적었으니 그대로 복사해도 돼요. 지우는 명령에는 무엇을 먼저 지워야 하는지 같이 적었어요. 실습할 때 이 장을 열어 두고 옆에서 봐요.",
    "Windows Git Bash에서 docker cp, psql -f처럼 컨테이너 안 경로를 쓰기 전에 export MSYS_NO_PATHCONV=1을 먼저 쳐요.")

cheat("cheat2", "docker compose 명령 한 장", [
    ("compose.yaml", C5, []),
    ("켜고 보기", C5, [("docker compose config", "파일을 읽은 그대로 보기, YAML 오류 확인"), ("docker compose up -d", "만들고 켜기 (뒤에서)"), ("docker compose ps", "이 폴더의 컨테이너"), ("docker compose ps -a", "꺼진 것까지"), ("docker compose ls", "compose 프로젝트 목록"), ("docker compose pull", "이미지 미리 받기")]),
    ("다루고 끄기", C5, [("docker compose exec db \\\n  psql -U postgres -d kant_shop", "서비스 이름 db로 들어가기"), ("docker compose logs --tail 3", "마지막 3줄 (-f는 계속)"), ("docker compose stop", "끄기 (지우지 않아요)"), ("docker compose start", "다시 켜기"), ("docker compose restart", "껐다가 바로 켜기"), ("docker compose down", "지우기, 볼륨은 남아요"), ("docker compose down -v", "볼륨까지 지우기")])],
    [600, 500, 520],
    "docker compose 명령을 한 장에 모았어요. 왼쪽은 수업에서 쓰는 compose.yaml 모양이에요. 2칸 들여쓰기, 쌍점 뒤 한 칸, 탭은 쓰지 않아요. 가운데는 켜고 보는 명령이에요. up 하기 전에 config로 파일을 먼저 확인하면 YAML 오류를 일찍 찾아요. 오른쪽은 다루고 끄는 명령이에요. compose exec 뒤에는 컨테이너 이름이 아니라 서비스 이름 db를 적어요. down은 볼륨을 남기고 down -v는 볼륨까지 지워요. 모든 compose 명령은 compose.yaml이 있는 폴더에서 쳐요.",
    "모든 compose 명령은 compose.yaml이 있는 폴더(~/kant-shop)에서 쳐요.")
# the yaml card on cheat2
_c2 = os.path.join(OUT, "cheat2.html")
_h = open(_c2).read()
_card = (f'<div style="position:absolute;left:96px;top:272px;width:600px;height:640px;background:{CARD};border:2px solid {LINE};border-radius:16px;padding:24px 28px">'
         + p(f"font-family:{MONO};font-size:22px;line-height:1.55;white-space:pre;color:{INK}", "\n".join(yaml_line(l) for l in YL))
         + p(f"margin-top:18px;font-size:20px;line-height:1.5;color:{SUB}", "2칸 들여쓰기 · 쌍점 뒤 한 칸 · 탭 금지<br>container_name을 빼면 이름은 kant-shop-db-1")
         + '</div>')
_h = _h.replace("\n<aside>", "\n" + _card + "\n<aside>", 1)
open(_c2, "w").write(_h)

# ---- END SLIDES ----
# =====================================================================
# toc
# =====================================================================
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
PL = [(C1, EB1[3:], "docker 다음 할 일, 옵션, 이름 / 옵션 표 / \\로 줄 나누기", "r-shape", "r-split"),
      (C2, EB2[3:], "pull, images, run, ps, stop, start, restart, logs --tail, -f, rm, rmi", "i-pull", "i-rm"),
      (C3, EB3[3:], "kant_shop.sql, docker cp, exec 세 가지, psql -f, exec -i < 파일, -it 함정", "w-sql", "w-trap"),
      (C4, EB4[3:], "volume create, ls, inspect, -v pgdata:…, volume rm", "v-cmds", "v-rm"),
      (C5, EB5[3:], "YAML 모양, 들여쓰기, 2칸과 4칸, 탭 오류, run과 compose.yaml, config, up, logs, down, ls, pull", "y-what", "c-name"),
      (C6, EB6[3:], "오류 모음, 수업 흐름 그대로, compose로 다시, 다 쓴 것 정리", "x-errs", "e-clean")]
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
if "cheat2" in page:
    o.append(p(f"position:absolute;left:96px;top:{214 + len(plist) * 122 + 34}px;font-size:26px;color:{SUB}", f"{page['why']}–{page['big']}쪽은 들어가기, {page['s-alias']}–{page['s-help']}쪽은 긴 이름과 --help, {page['cheat1']}–{page['cheat2']}쪽은 치트시트 두 장이에요."))
o = [x for x in o if 'id="eyebrow"' not in x]
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(o) + f"\n<aside>{e('여섯 파트로 나눴어요. 1파트에서 docker 명령을 끊어 읽는 법을 봐요. 2파트는 이미지와 컨테이너를 켜고 끄고 지우는 명령이에요. 3파트에서 수업 예제 kant_shop.sql을 컨테이너 안으로 넣어 실행해요. 4파트는 볼륨, 5파트는 YAML과 compose예요. 6파트에서 오류를 모아 보고 실제 상황 세 가지를 풀어요. 끝에 치트시트 두 장이 있어요.')}</aside>\n</section>\n")

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-13T00:00:00Z"}, "lists": "css", "title": "Docker 5 (명령어 한눈에 보기)", "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
for w_ in WARN:
    print("WARN", w_)
print(len(ORDER), "slides")
