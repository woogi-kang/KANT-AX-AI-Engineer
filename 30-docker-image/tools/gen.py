"""Generates every slide of the Docker 2 deck (30) and slides/deck.json.

Story: 29 ended with a container that forgot what was changed inside it. Part 1 goes inside a running nginx
container with docker exec and changes its page; removing the container loses the change. Part 2 keeps it in a
volume, then connects the student's own site folder. Part 3 bakes chapter 28's shopping cart into an image with a
five-line Dockerfile (FROM, WORKDIR, COPY, RUN, CMD), builds it, runs it, rebuilds it and trims it with
.dockerignore. Part 4 writes the long nginx command into compose.yaml. Part 5 is the errors, part 6 real tasks.
Analogy from 24 (and 29): image = 붕어빵 틀, container = 붕어빵, Dockerfile = 틀을 만드는 레시피.

Every terminal line comes from tools/demo.py (real Docker 29.9.2, saved in tools/out.json).
Layout follows 11: the terminal is the one big object, a small colored tag on a line says what it means, and a
browser or editor straddles the terminal's edge as a satellite.
Usage (in 30-docker-image): python3 tools/gen.py slides
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
from files import SITE1, SITE2, COMPOSE, DOCKERFILE, DOCKERIGNORE  # noqa: E402  (the files demo.py wrote)

SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
BG, INK, SUB, LINE, CARD = "#F6F5F1", "#1D2330", "#4A5262", "#DCD8CE", "#FFFFFF"
BL, GR, OR, RED, TEAL, GRAY, MAG = "#2459C9", "#1F8A4C", "#B26A00", "#A33131", "#0F7C86", "#5B6270", "#A23B72"
DK = "#1D63ED"                       # Docker's blue, for the whale-side objects only
BR, BRBG = "#9A5B13", "#FBF0E0"      # 붕어빵 = container (same as 24-28)
MD, MDBG = "#5B4636", "#EFE8DF"      # 틀 = image
T_BG = "#1B2029"
TCOL = {"o": "#D8DEE9", "e": "#FF9C94", "g": "#7FD18B", "d": "#7D8696", "y": "#F2C46D", "c": "#7D8696"}
SHADOW = "0 18px 40px rgba(29,35,48,.16), 0 2px 6px rgba(29,35,48,.08)"
WARN = []
REAL = " 터미널 출력은 tools/demo.py로 실제 Docker를 실행한 결과예요."


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
    """wrap the first match of each key of marks in <span id=...>"""
    out, pos = "", 0
    hits = sorted(((text.find(k), k, v) for k, v in marks.items() if k in text), key=lambda t: t[0])
    for at, k, v in hits:
        if at < pos:
            continue
        out += e(text[pos:at]) + f'<span id="{v}">{e(k)}</span>'
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
    out = []
    for l in lines:
        while len(l) > cols:
            out.append(l[:cols])
            l = l[cols:]
        out.append(l)
    return out


def C(scene, k=0):
    return D[scene][k]["cmd"]


def short_build(lines):
    """docker build's final screen without the '=> =>' detail lines (pull, extract, export)."""
    out = []
    for l in lines:
        if l.startswith(" => => ") and "naming to" not in l:
            continue
        out.append(l)
    return out


P_HOME, P_CAFE, P_CART = "~", "~/cafe", "~/shopping-cart"
RUN_WEB = R("run-web")
WEB_ID = RUN_WEB[-1]
EXEC = R("exec")
HOST = EXEC[0].split(":")[0]               # root@1f06dedba4da
PS_A = R("psa")


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


def page_nginx(scale=1.0):
    """nginx's own welcome page: the heading and first sentence are real words, the rest is filler."""
    s = scale
    return (p(f"font-family:Tahoma, Verdana, Arial, sans-serif;font-size:{38 * s:.0f}px;font-weight:700;line-height:1.2;color:#111111", "Welcome to nginx!")
            + p(f"font-family:Tahoma, Verdana, Arial, sans-serif;font-size:{20 * s:.0f}px;line-height:1.4;color:#333333", "If you see this page, nginx is successfully installed and working.")
            + '<div style="display:flex;flex-direction:column;gap:12px;margin-top:6px">' + bar(round(380 * s)) + bar(round(300 * s)) + bar(round(340 * s)) + '</div>')


def page_kant(scale=1.0):
    return p(f"font-family:Tahoma, Verdana, Arial, sans-serif;font-size:{38 * s:.0f}px;font-weight:700;line-height:1.2;color:#111111", "KANT Cafe") if (s := scale) else ""


def page_menu(extra=False, order=None, scale=1.0):
    s = scale
    o = (p(f"font-size:{38 * s:.0f}px;font-weight:700;line-height:1.2;color:#111111", "KANT 카페 메뉴")
         + p(f"font-size:{24 * s:.0f}px;line-height:1.4;color:#333333", "아메리카노 4,500원"))
    if extra:
        o += p(f"font-size:{24 * s:.0f}px;line-height:1.4;color:#333333;background:#E4F3EA;border-radius:6px;padding:0 8px;margin-left:-8px", "카페라테 5,000원", bi("rise", order))
    return o


# ---------- editor (VS Code-like file) ----------
TABH = 56


def editor(eid, name, lines, left, top, w, fs=26, attrs="", color=BL, h=None, nums=True):
    lh = fs * 1.45
    gw = 70 if nums else 0
    hh = h or (TABH + 36 + len(lines) * lh)
    o = [f'<div id="{eid}"{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{hh:.0f}px;background:{CARD};border:2px solid {LINE};border-radius:16px;overflow:hidden">',
         f'<div style="position:absolute;left:0;top:0;width:{w}px;height:{TABH}px;background:#EEF0F3;border-bottom:2px solid {LINE}"></div>',
         p(f"position:absolute;left:0;top:0;height:{TABH}px;padding:0 26px;background:{CARD};border-right:2px solid {LINE};border-top:4px solid {color};font-family:{MONO};font-size:24px;font-weight:700;line-height:{TABH - 6}px;color:{INK};white-space:nowrap", e(name))]
    if gw:
        o.append(f'<div style="position:absolute;left:0;top:{TABH + 16}px;width:{gw}px">' + "".join(
            p(f"height:{lh:.2f}px;font-family:{MONO};font-size:{fs * 0.8:.0f}px;line-height:{lh:.2f}px;text-align:right;padding-right:6px;color:#A3A9B4", str(i + 1)) for i in range(len(lines))) + '</div>')
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


# ---------- objects of the story ----------
def image_box(x, y, w, name, layers, bid=None, attrs="", lh=46):
    """An image drawn as a 틀: a stack of layers, the newest on top, with its name on a label."""
    i = f' id="{bid}"' if bid else ""
    rows = "".join(p(f"height:{lh}px;flex:none;border-radius:10px;background:{CARD};border:2px solid #CDBFAE;padding:0 18px;{'' if any('가' <= ch <= '힣' for ch in l) else 'font-family:' + MONO + ';'}font-size:22px;font-weight:700;line-height:{lh - 4}px;color:{MD};white-space:nowrap", e(l)) for l in reversed(layers))
    return (f'<div{i}{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;background:{MDBG};border:3px solid {MD};border-radius:20px;padding:18px 20px 20px;display:flex;flex-direction:column;gap:8px">'
            + p(f"font-size:24px;font-weight:700;color:{MD};line-height:1.3;white-space:nowrap", f'이미지 <span style="font-family:{MONO}">{e(name)}</span>')
            + rows + '</div>')


def container_box(x, y, w, h, name, inner="", bid=None, attrs="", status="실행 중", scolor=GR):
    i = f' id="{bid}"' if bid else ""
    return (f'<div{i}{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{BRBG};border:3px solid {BR};border-radius:20px;padding:18px 22px;display:flex;flex-direction:column;gap:12px">'
            '<div style="display:flex;flex-direction:row;align-items:center;gap:12px">'
            + p(f"font-size:24px;font-weight:700;color:{BR};white-space:nowrap", f'컨테이너 <span style="font-family:{MONO}">{e(name)}</span>')
            + (f'<div style="margin-left:auto;display:flex;flex-direction:row;align-items:center;gap:8px"><div style="width:12px;height:12px;border-radius:6px;background:{scolor}"></div>'
               + p(f"font-size:20px;font-weight:700;color:{scolor};white-space:nowrap", e(status)) + '</div>' if status else "")
            + '</div>' + inner + '</div>')


def volume_box(x, y, w, h, name, inner="", bid=None, attrs="", color=GR):
    i = f' id="{bid}"' if bid else ""
    return (f'<div{i}{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:#E4F3EA;border:3px solid {color};border-radius:20px;padding:18px 22px;display:flex;flex-direction:column;gap:12px">'
            f'<div style="display:flex;flex-direction:row;align-items:center;gap:12px"><x-icon name="Database" style="width:28px;height:28px;color:{color}"></x-icon>'
            + p(f"font-size:24px;font-weight:700;color:{color};white-space:nowrap", name) + '</div>' + inner + '</div>')


def file_chip(name, color=INK, bg=CARD, fid=None, attrs="", size=22):
    i = f' id="{fid}"' if fid else ""
    return p(f"height:{size + 22}px;flex:none;padding:0 14px;border-radius:9px;background:{bg};border:2px solid #D6D2C8;font-family:{MONO};font-size:{size}px;font-weight:700;line-height:{size + 18}px;color:{color};white-space:nowrap", e(name), i + attrs)


EB1 = "1. 컨테이너 안에 들어가기"
EB2 = "2. 볼륨으로 남기기"
EB3 = "3. Dockerfile로 이미지 만들기"
EB4 = "4. docker compose 맛보기"
EB5 = "5. 자주 나는 오류"
EB6 = "6. 실제 상황 예제"
NV = "/usr/share/nginx/html"

# =====================================================================
# cover
# =====================================================================
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px">',
       p("position:absolute;left:128px;top:300px;font-size:28px;font-weight:700;color:#8FB3FF", "KANT AX/AI 엔지니어 트랙 · 30"),
       f'<h1{SLAM(1)} style="position:absolute;left:128px;top:360px;font-size:100px;font-weight:900;line-height:1.15;color:#F6F5F1">Docker 2</h1>',
       p("position:absolute;left:128px;top:500px;font-size:52px;font-weight:700;line-height:1.3;color:#F6F5F1", "내 프로그램을<br>이미지로 만들기"),
       p("position:absolute;left:128px;top:680px;font-size:32px;line-height:1.5;color:#BFC6D4", "exec, 볼륨, Dockerfile, compose")]
BUILD = R("build")
t = Term([("$", P_CART, "docker build -t cart ."), ("g", BUILD[0].split("  ")[0]), ("o", ""), ("$", P_CART, "docker run cart")] + [("o", l) for l in R("run-cart")[:6]],
         1000, 300, size=28, w=1000, tid="cov-term", bleed=True)
cov.append(t.html())
cov.append(shine(2, "cov-term"))
W("cover", cov, "30 챕터는 Docker 2예요. 29에서는 Docker Hub에서 받은 이미지로 컨테이너를 돌렸어요. 오늘은 컨테이너 안에 직접 들어가 보고, 지워도 남는 저장 공간인 볼륨을 붙여요. 그다음 28에서 만든 장바구니 프로그램을 내 이미지로 구워요. 마지막에 긴 docker run 명령을 파일 한 장에 적어 두는 docker compose를 맛봐요." + REAL, ("intro", "들어가기"))

ORDER.append("toc")   # written last, after page numbers are known

# =====================================================================
# why
# =====================================================================
o = frame("why", "들어가기", "29가 끝날 때 남은 질문이 두 개예요", INK)
# question 1: the change that disappears
o.append(p(f"position:absolute;left:96px;top:226px;font-size:30px;font-weight:900;color:{BL}", "1"))
o.append(p(f"position:absolute;left:140px;top:222px;font-size:34px;font-weight:700;color:{INK}", "컨테이너를 지우면 안에서 바꾼 것도 사라져요"))
o.append(p(f"position:absolute;left:140px;top:276px;font-size:26px;color:{SUB}", "지워도 남게 하려면 어떻게 할까요?"))
cx0 = 140
o.append(container_box(cx0, 340, 420, 190, "web", p(f"font-family:Tahoma, Verdana, Arial, sans-serif;font-size:30px;font-weight:700;color:#111111;background:#FFFFFF;border-radius:10px;padding:16px 20px", "KANT Cafe"), bid="why-c1"))
o.append(harrow(cx0 + 440, cx0 + 620, 435, GRAY, 1))
o.append(p(f"position:absolute;left:{cx0 + 446}px;top:380px;width:170px;text-align:center;font-family:{MONO};font-size:24px;font-weight:700;color:{GRAY}", "rm", bi("fade", 1)))
o.append(container_box(cx0 + 640, 340, 420, 190, "web", p(f"font-family:Tahoma, Verdana, Arial, sans-serif;font-size:30px;font-weight:700;color:#111111;background:#FFFFFF;border-radius:10px;padding:16px 20px", "Welcome to nginx!"), bid="why-c2", attrs=bi("rise", 1)))
o.append(pill(cx0 + 1080, 414, "처음 모습으로 돌아왔어요", RED, 1))
# question 2: my own program as an image
o.append(f'<div style="position:absolute;left:96px;top:592px;width:1728px;height:1px;background:{LINE}"></div>')
o.append(p(f"position:absolute;left:96px;top:636px;font-size:30px;font-weight:900;color:{TEAL}", "2", bi("fade", 2)))
o.append(p(f"position:absolute;left:140px;top:632px;font-size:34px;font-weight:700;color:{INK}", "29의 이미지는 모두 남이 만든 것이었어요", bi("fade", 2)))
o.append(p(f"position:absolute;left:140px;top:686px;font-size:26px;color:{SUB}", "28의 장바구니도 이미지로 만들 수 있을까요?", bi("fade", 2)))
chips = [("nginx", DK), ("hello-world", DK), ("python:3.12-slim", DK)]
o.append(f'<div{STAGGER(2, 90)} style="position:absolute;left:140px;top:760px;display:flex;flex-direction:row;gap:18px;align-items:center">'
         + "".join(file_chip(n, c, "#E8EFFD", size=26) for n, c in chips)
         + p(f"font-size:26px;font-weight:700;color:{GRAY};padding:0 14px", "다음은") + file_chip("cart", MD, MDBG, size=26, fid="why-cart") + '</div>')
o.append(ring(3, 140 + tw("nginx", 26) + tw("hello-world", 26) + tw("python:3.12-slim", 26) + 3 * 28 + 3 * 18 + tw("다음은", 26, False) + 28 + 18 + 4, 760, tw("cart", 26) + 28, 48, TEAL))
o.append(caption("두 질문의 답이 볼륨과 Dockerfile이에요.", 900, 3, size=32))
W("why", o, "29 마지막 장면을 떠올려 봐요. 컨테이너 안의 페이지를 바꾼 뒤 컨테이너를 지우고 다시 만들면 처음 모습으로 돌아왔어요. 바꾼 것을 남기는 방법이 첫 번째 질문이에요. 두 번째 질문은 이미지예요. 29에서 쓴 nginx, hello-world, python 이미지는 모두 Docker Hub에서 받은 남의 이미지였어요. 오늘은 28에서 만든 장바구니를 cart라는 내 이미지로 만들어요. 1, 2파트가 첫 질문, 3파트가 두 번째 질문의 답이에요.")

# =====================================================================
# big picture
# =====================================================================
o = frame("big", "들어가기", "레시피로 틀을 굽고, 틀로 붕어빵을 찍어요", INK)
Y0 = 300
# Dockerfile
df_lines = DOCKERFILE.strip().split("\n")
o.append(f'<div id="big-df" style="position:absolute;left:96px;top:{Y0}px;width:380px;height:330px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:22px 24px;display:flex;flex-direction:column;gap:10px">'
         + p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{TEAL}", "Dockerfile")
         + "".join(p(f"font-family:{MONO};font-size:19px;font-weight:700;color:{INK};white-space:nowrap", e(l.split(" ")[0]) + f'<span style="color:{GRAY};font-weight:400"> …</span>') for l in df_lines) + '</div>')
o.append(p(f"position:absolute;left:96px;top:{Y0 + 352}px;width:380px;text-align:center;font-size:24px;font-weight:700;color:{TEAL}", "레시피"))
o.append(harrow(490, 640, Y0 + 165, TEAL, 1))
o.append(p(f"position:absolute;left:480px;top:{Y0 + 108}px;width:170px;text-align:center;font-family:{MONO};font-size:24px;font-weight:700;color:{TEAL}", "build", bi("fade", 1)))
o.append(image_box(660, Y0, 400, "cart", ["FROM astral/uv…", "WORKDIR /app", "COPY . .", "RUN uv sync"], bid="big-img", attrs=bi("rise", 1)))
o.append(p(f"position:absolute;left:660px;top:{Y0 + 352}px;width:400px;text-align:center;font-size:24px;font-weight:700;color:{MD}", "붕어빵 틀", bi("fade", 1)))
o.append(harrow(1076, 1226, Y0 + 165, BR, 2))
o.append(p(f"position:absolute;left:1066px;top:{Y0 + 108}px;width:170px;text-align:center;font-family:{MONO};font-size:24px;font-weight:700;color:{BR}", "run", bi("fade", 2)))
for k in range(3):
    if k < 2:  # cards behind the front one: only their edges show
        o.append(f'<div{bi("rise", 2)}{DELAY(k * 120)} style="position:absolute;left:1268px;top:{Y0 + k * 22}px;width:540px;height:150px;background:{BRBG};border:3px solid {BR};border-radius:20px"></div>')
    else:
        o.append(container_box(1268, Y0 + k * 22, 540, 150, "cart", "", attrs=bi("rise", 2) + DELAY(k * 120)))
o.append(p(f"position:absolute;left:1250px;top:{Y0 + 210}px;width:576px;text-align:center;font-size:24px;font-weight:700;color:{BR}", "붕어빵 (몇 개든 찍어요)", bi("fade", 2)))
# volume under the container
o.append(volume_box(1286, Y0 + 400, 504, 150, "볼륨", p(f"font-size:22px;color:{SUB}", "컨테이너 밖 보관함"), bid="big-vol", attrs=bi("rise", 3)))
o.append(svg(arrow_path(f"M1740,{Y0 + 196} L1740,{Y0 + 394}", GR, 5, dash="2 12"), 3))
o.append(p(f"position:absolute;left:1756px;top:{Y0 + 280}px;font-family:{MONO};font-size:24px;font-weight:700;color:{GR}", "-v", bi("fade", 3)))
# compose bracket
o.append(f'<div{bi("fade", 4)} style="position:absolute;left:1230px;top:{Y0 - 46}px;width:594px;height:{620}px;border:3px dashed {MAG};border-radius:26px"></div>')
o.append(pill(1250, Y0 - 66, "compose.yaml에 적어 두기", MAG, 4))
# part numbers
o.append(caption("1파트 exec는 붕어빵 안, 2파트 볼륨은 붕어빵 밖, 3파트 Dockerfile은 틀, 4파트 compose는 찍는 방법이에요.", 900, 4, size=28, color=SUB))
W("big", o, "오늘 나오는 네 가지가 어디에 있는지 한 장에 그렸어요. 29에서 이미지는 붕어빵 틀, 컨테이너는 그 틀로 찍은 붕어빵이라고 했어요. 3파트에서는 Dockerfile이라는 레시피를 써서 docker build로 내 틀을 구워요. 틀 안은 레시피 한 줄마다 한 층씩 쌓여요. docker run으로 붕어빵을 찍는 건 29와 같아요. 1파트의 exec는 찍어 둔 붕어빵 안으로 들어가는 명령이에요. 2파트의 볼륨은 붕어빵 밖에 두는 보관함이라 붕어빵을 버려도 남아요. 4파트의 compose는 붕어빵을 찍는 긴 명령을 파일에 적어 두는 방법이에요.")

# =====================================================================
# ready
# =====================================================================
o = frame("ready", "들어가기", "실습 폴더 두 개를 준비해요", INK)
t = Term([("$", P_HOME, "mkdir cafe"), ("$", P_HOME, "cd cafe"), ("$", P_CAFE, "mkdir site"), ("o", ""),
          ("$", P_HOME, "cd shopping-cart"), ("$", P_CART, "ls")] + [("o", l) for l in R("cart-ls2")],
         96, 214, size=26, w=1100, lh=1.6)
o.append(t.html())
o += tag(t, 2, "1, 2, 4파트", BL, 1)
o += tag(t, 4, "3파트: 28의 장바구니", TEAL, 2)
tree = [("~/", INK, 0), ("cafe/", BL, 1), ("site/", BL, 2), ("shopping-cart/", TEAL, 1), ("main.py  cart.py  product.py", GRAY, 2), ("pyproject.toml  uv.lock", GRAY, 2)]
o.append(f'<div{STAGGER(2, 80)} style="position:absolute;left:1240px;top:214px;width:584px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:26px 30px;display:flex;flex-direction:column;gap:10px">'
         + "".join(p(f"margin-left:{d * 34}px;font-family:{MONO};font-size:26px;font-weight:700;line-height:1.5;color:{c};white-space:nowrap", e(n)) for n, c, d in tree) + '</div>')
o.append(f'<div style="position:absolute;left:96px;top:{t.y + t.h + 50}px;width:1728px;height:1px;background:{LINE}"></div>')
o.append(p(f"position:absolute;left:96px;top:{t.y + t.h + 80}px;font-size:28px;font-weight:700;color:{INK}", "Windows Git Bash는 새 창을 열 때마다 이 줄을 먼저 쳐요.", bi("fade", 3)))
tw_ = Term([("$", P_HOME, "export MSYS_NO_PATHCONV=1")], 96, t.y + t.h + 140, size=34, w=860, tid="t-msys", attrs=bi("rise", 3))
o.append(tw_.html())
o.append(p(f"position:absolute;left:1000px;top:{t.y + t.h + 150}px;width:824px;font-size:28px;line-height:1.55;color:{SUB}", "Git Bash가 /usr/share 같은 컨테이너 경로를<br>Windows 경로로 바꿔 버리는 것을 막아요.", bi("fade", 3)))
W("ready", o, "실습 폴더는 두 개예요. 홈 폴더에 cafe 폴더와 그 안의 site 폴더를 만들어요. 1, 2, 4파트에서 nginx 웹 페이지를 띄울 때 써요. 3파트는 28에서 만든 shopping-cart 폴더를 그대로 써요. main.py가 28 마지막 실습의 주문 코드인지 확인해요. Windows의 Git Bash는 /로 시작하는 글자를 Windows 경로로 바꾸는 버릇이 있어요. 오늘은 -v 뒤에 컨테이너 안 경로를 적으니, 새 Git Bash 창을 열 때마다 export MSYS_NO_PATHCONV=1을 먼저 쳐요. Mac은 치지 않아도 돼요." + REAL)

# =====================================================================
# part 1: exec
# =====================================================================
o = frame("e-run", EB1, "29처럼 nginx 컨테이너를 하나 띄워요", BL)
lines = [("$", P_CAFE, C("run-web"))] + [("d" if ("Pull" in l or "Download" in l or "Digest" in l) else "o", l) for l in RUN_WEB[:-1]] + [("g", WEB_ID, {WEB_ID[:12]: "run-id"})]
t = Term(lines, 96, 214, size=22, w=1120, lh=1.5)
t.band(1, order=1)
t.band(len(lines) - 1, order=2, color="rgba(127,209,139,.16)")
o.append(t.html())
o += tag(t, 1, "29 끝에서 지워서 다시 받아요", BL, 1)
o.append(pill(t.tx, t.y + t.h + 18, "컨테이너 ID", GR, 2))
o.append(underline(2, round(t.tx), round(t.tx + t.sw(WEB_ID[:12])), round(t.top(len(lines) - 1) + t.lp - 4), GR))
o.append(browser(1260, 360, 564, 440, "localhost:8080", page_nginx(0.78), "br-run", attrs=SLIDE(3, 300, 0)))
o.append(cursor(3, target="br-run"))
o.append(cursor_off(4))
W("e-run", o, "29에서 친 명령 그대로 nginx 컨테이너를 web이라는 이름으로 띄워요. 29 마지막에 nginx 이미지를 지웠으니 Unable to find image가 나오고 Docker Hub에서 다시 받아요. 받는 줄의 숫자와 글자는 받는 날마다 달라요. 마지막 줄의 긴 글자는 컨테이너 ID예요. 앞 12글자를 기억해 두세요. 다음 장에서 다시 나와요. 브라우저로 localhost:8080을 열면 nginx 환영 페이지가 보여요. 브라우저 화면은 단순하게 그린 그림이에요." + REAL, ("p1", "컨테이너 안에 들어가기"))

o = frame("e-exec", EB1, "docker exec -it로 실행 중인 컨테이너 안에 들어가요", BL)
o += parts(96, 230, [("docker", INK, None, None), ("exec", BL, "실행 중인<br>컨테이너에서", None), ("-it", OR, "키보드로<br>주고받기", None),
                     ("web", BR, "컨테이너 이름", None), ("bash", TEAL, "열 프로그램<br>(셸)", None)], size=64, order=1, lab=26, drop=36, stagger=True, lw=300)
t = Term([("$", P_CAFE, C("exec")), ("#", HOST + ":/", "", {HOST.split("@")[1]: "ex-host"})], 96, 560, size=34, w=1100, tid="t-exec", attrs=bi("rise", 5))
o.append(t.html())
hx = t.tx + t.sw("root@")
o.append(underline(6, round(hx), round(hx + t.sw(HOST.split("@")[1])), round(t.top(1) + t.lp - 4), GR))
o.append(p(f"position:absolute;left:96px;top:{t.y + t.h + 30}px;width:1100px;font-size:28px;font-weight:700;line-height:1.5;color:{GR}", f"@ 뒤는 앞 장의 컨테이너 ID 앞 12글자예요.", bi("fade", 6)))
o.append(f'<div{bi("rise", 7)} style="position:absolute;left:1290px;top:230px;width:534px;background:{CARD};border:2px solid {LINE};border-left:8px solid {GRAY};border-radius:16px;padding:20px 26px;display:flex;flex-direction:column;gap:8px">'
         + p(f"font-size:22px;font-weight:700;color:{GRAY}", "29에서는")
         + p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{INK};white-space:nowrap", "docker run -it ... bash")
         + p(f"font-size:22px;line-height:1.45;color:{SUB}", "새 컨테이너를 만들면서 들어갔어요.<br>exec는 켜 둔 컨테이너에 들어가요.") + '</div>')
# picture: the student inside the 붕어빵
o.append(container_box(1290, 560, 534, 300, "web", p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{INK};background:#FFFFFF;border-radius:10px;padding:14px 18px;white-space:nowrap", "root@…:/#") + p(f"font-size:24px;line-height:1.45;color:{SUB}", "지금 치는 명령은<br>컨테이너 안의 리눅스에서 돌아요"), bid="ex-box", attrs=bi("rise", 6)))
W("e-exec", o, "exec는 이미 돌고 있는 컨테이너 안에서 프로그램 하나를 실행하는 명령이에요. 여기서는 bash라는 셸을 열어요. 셸은 01부터 써 온 터미널 안의 그 프로그램이에요. -it는 -i와 -t를 붙여 쓴 것으로, 키보드로 치고 화면으로 받겠다는 뜻이에요. 빼먹으면 셸이 열리자마자 끝나요. 엔터를 치면 프롬프트가 root@로 시작하는 모양으로 바뀌어요. @ 뒤의 글자는 앞 장에서 본 컨테이너 ID 앞 12글자예요. 이제부터 치는 명령은 내 컴퓨터가 아니라 컨테이너 안의 리눅스에서 돌아요. 29에서는 docker run -it ubuntu:24.04 bash로 새 컨테이너를 만들면서 들어갔고, exit하면 컨테이너가 꺼졌어요. exec는 이미 켜 둔 컨테이너에 들어가는 명령이라, exit로 나와도 nginx는 계속 돌아요." + REAL)

o = frame("e-inside", EB1, "안에서는 01에서 배운 명령이 그대로 통해요", BL)
ex = []
for l in EXEC:
    if "# " in l and l.startswith("root@"):
        pr, c_ = l.split("# ", 1)
        ex.append(("#", pr, c_))
    else:
        ex.append(("o", l))
t = Term(ex, 96, 214, size=23, w=1180, lh=1.5, tid="t-in")
iln = [i for i, r in enumerate(ex) if r[0] == "#"]
steps = [(iln[0], iln[1] - 1, iln[0], "컨테이너 안의 맨 위 폴더(/)", BL), (iln[1], iln[3] - 1, iln[1], "nginx가 보여 주는 폴더", BL),
         (iln[3], iln[5] - 1, iln[4] + 1, "index.html 내용 바꾸기", OR), (iln[5], len(ex) - 1, iln[5], "내 컴퓨터로 돌아오기", GRAY)]
for k, (a_, b_, ti, txt, c_) in enumerate(steps):
    t.band(a_, b_, order=k + 1, attrs=DIM("in"))
o.append(t.html())
for k, (a_, b_, ti, txt, c_) in enumerate(steps):
    o += tag(t, ti, txt, c_, k + 1, at=t.x + 760)
o.append(browser(1290, 600, 534, 300, "localhost:8080", page_kant(0.9), "br-in", attrs=SLIDE(3, 300, 0)))
o.append(p(f"position:absolute;left:1290px;top:924px;width:534px;font-size:26px;font-weight:700;line-height:1.45;color:{OR}", "새로 고치면 바뀐 페이지가 보여요.", bi("fade", 3)))
W("e-inside", o, "들어간 뒤 ls를 치면 리눅스의 맨 위 폴더가 보여요. 내 컴퓨터의 폴더가 아니라 컨테이너 안이에요. nginx는 /usr/share/nginx/html 폴더의 index.html을 웹 페이지로 보여 줘요. 그 폴더로 cd 해서 01에서 배운 echo와 >로 index.html 내용을 KANT Cafe 한 줄로 바꿔요. cat으로 바뀐 내용을 보고, 브라우저를 새로 고치면 페이지가 바로 바뀌어요. 다 봤으면 exit로 컨테이너 밖, 내 컴퓨터 터미널로 돌아와요. 이때 컨테이너는 멈추지 않고 계속 돌아요." + REAL)

o = frame("e-gone", EB1, "컨테이너를 지우면 안에서 바꾼 것도 같이 사라져요", BL)
g_ = D["gone"]
t = Term([("$", P_CAFE, g_[0]["cmd"]), ("o", g_[0]["out"][0]), ("$", P_CAFE, g_[1]["cmd"]), ("o", g_[1]["out"][0]), ("$", P_CAFE, g_[2]["cmd"]), ("g", g_[2]["out"][0])],
         96, 214, size=26, w=1728, lh=1.55)
t.band(4, 5, order=1)
o.append(t.html())
o += tag(t, 5, "같은 이름, 새 컨테이너", GR, 1, at=t.x + 1200)
o.append(browser(96, t.y + t.h + 40, 700, 340, "localhost:8080", page_kant(0.9), "br-before"))
o.append(browser(1124, t.y + t.h + 40, 700, 340, "localhost:8080", page_nginx(0.8), "br-after", attrs=bi("rise", 2)))
o.append(harrow(820, 1100, t.y + t.h + 210, GRAY, 2))
o.append(p(f"position:absolute;left:812px;top:{t.y + t.h + 140}px;width:300px;text-align:center;font-size:24px;font-weight:700;color:{GRAY}", "지우고 다시 run", bi("fade", 2)))
o.append(shake(3, "br-after"))
o.append(caption("안에서 바꾼 파일은 그 붕어빵에만 있었어요.", t.y + t.h + 410, 3, color=RED, size=30))
W("e-gone", o, "29에서 배운 대로 stop, rm으로 컨테이너를 지우고 같은 명령으로 다시 만들어요. 이름은 web으로 같지만 ID가 달라요. 같은 틀로 새로 찍은 붕어빵이에요. 브라우저를 새로 고치면 KANT Cafe가 사라지고 처음 환영 페이지가 다시 나와요. exec로 바꾼 파일은 지운 붕어빵 안에만 있었기 때문이에요. 틀인 nginx 이미지는 한 번도 바뀌지 않았어요. 다음 파트에서 이 문제를 볼륨으로 풀어요." + REAL)

# =====================================================================
# part 2: volumes
# =====================================================================
o = frame("v-what", EB2, "볼륨은 컨테이너 밖에 두는 보관함이에요", GR)
slot = lambda: (f'<div style="height:130px;border:3px dashed {GR};border-radius:14px;background:#F3FAF5;display:flex;flex-direction:row;align-items:center;gap:12px;padding:0 20px">'
                + file_chip("index.html") + file_chip("50x.html") + '</div>')
o.append(container_box(96, 240, 680, 290, "web", p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{BR}", e(NV)) + slot(), bid="vw-c1"))
o.append(volume_box(96, 700, 680, 200, "볼륨 cafe-html", '<div style="display:flex;flex-direction:row;gap:12px">' + file_chip("index.html") + file_chip("50x.html") + '</div>', bid="vw-v"))
o.append(svg(arrow_path("M436,690 L436,546", GR, 6) + head_at(436, 542, -90, GR), 1))
o.append(p(f"position:absolute;left:460px;top:592px;font-family:{MONO};font-size:24px;font-weight:700;color:{GR};white-space:nowrap", "-v cafe-html:" + e(NV), bi("fade", 1)))
o.append(p(f"position:absolute;left:96px;top:592px;width:320px;font-size:24px;font-weight:700;line-height:1.4;color:{GR}", "점선 칸에 보이는 파일은<br>사실 볼륨에 있어요", bi("fade", 1)))
o.append(f'<div{bi("fade", 2)} style="position:absolute;left:96px;top:240px;width:680px;height:290px;border-radius:20px;background:rgba(246,245,241,.86)"></div>')
o.append(pill(330, 364, "rm으로 지워요", RED, 2))
o.append(container_box(1144, 240, 680, 290, "web", p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{BR}", e(NV)) + slot(), bid="vw-c2", attrs=bi("rise", 3), status="새로 만든 컨테이너"))
o.append(svg(arrow_path("M790,800 C1060,800 1300,720 1430,552", GR, 6) + head_at(1433, 546, -58, GR), 3))
o.append(p(f"position:absolute;left:1000px;top:820px;width:824px;font-size:28px;font-weight:700;line-height:1.45;color:{GR}", "새 컨테이너에 같은 볼륨을 붙이면<br>파일이 그대로 보여요", bi("fade", 3)))
W("v-what", o, "볼륨은 Docker가 컨테이너 밖에 따로 만들어 두는 저장 공간이에요. docker run에 -v 볼륨이름:컨테이너 안 경로를 붙이면, 그 경로에 넣는 파일이 실제로는 볼륨에 들어가요. 그래서 컨테이너를 rm으로 지워도 볼륨은 그대로 남아요. 새 컨테이너를 만들 때 같은 볼륨을 다시 붙이면 파일이 그대로 보여요. 처음 붙일 때 볼륨이 비어 있으면, Docker가 이미지 안 그 폴더의 파일(index.html, 50x.html)을 볼륨으로 복사해 줘요.", ("p2", "볼륨으로 남기기"))

o = frame("v-named", EB2, "-v 볼륨이름:경로를 붙이면 지웠다 만들어도 남아요", GR)
vv = D["vol"]
lines = [("$", P_CAFE, vv[0]["cmd"], {"-v cafe-html:" + NV: "vn-v"}), ("d", vv[0]["out"][0][:12] + "…"),
         ("$", P_CAFE, vv[1]["cmd"])] + [("#", l.split("# ", 1)[0], l.split("# ", 1)[1]) for l in vv[1]["out"][1:-1]] + [("o", "exit"),
         ("$", P_CAFE, vv[2]["cmd"] + "; " + vv[3]["cmd"]), ("d", "web"), ("d", "web"),
         ("$", P_CAFE, vv[4]["cmd"], {"-v cafe-html:" + NV: "vn-v2"}), ("d", vv[4]["out"][0][:12] + "…")]
t = Term(lines, 96, 214, size=22, w=1728, lh=1.5)
o.append(t.html())
vx = t.sx(0, "-v ")
o.append(pen_box(1, round(vx - 6), round(t.top(0) - 2), round(t.sw("-v cafe-html:" + NV) + 12), round(t.lp + 4), GR))
o.append(pen_box(3, round(t.sx(len(lines) - 2, "-v ") - 6), round(t.top(len(lines) - 2) - 2), round(t.sw("-v cafe-html:" + NV) + 12), round(t.lp + 4), GR))
o += tag(t, 4, "1파트처럼 index.html 바꾸기", OR, 2, at=t.x + 1100)
o += tag(t, 7, "지우고", RED, 2, at=t.x + 1100)
o.append(browser(1180, t.y + t.h + 30, 644, 1000 - (t.y + t.h + 30), "localhost:8080", page_kant(0.9), "br-vn", attrs=bi("rise", 4)))
o.append(caption("지웠다 다시 만들어도<br>KANT Cafe가 그대로예요.", t.y + t.h + 60, 4, width=1000, size=34, color=GR))
W("v-named", o, "1파트와 같은 순서를 볼륨을 붙여서 다시 해요. 차이는 docker run 뒤에 붙인 -v cafe-html:/usr/share/nginx/html 하나예요. cafe-html이라는 볼륨을 nginx가 페이지를 읽는 폴더에 붙였어요. 볼륨이 없으면 Docker가 처음에 만들어 줘요. exec로 들어가서 index.html을 바꾸고, stop과 rm으로 지워요. 세미콜론(;)은 두 명령을 한 줄에 이어 친 거예요. 같은 -v를 붙여 다시 만들면 브라우저에 KANT Cafe가 그대로 나와요. 긴 ID는 화면에 맞추려고 앞 12글자만 적었어요." + REAL)

o = frame("v-ls", EB2, "docker volume ls로 남아 있는 볼륨을 봐요", GR)
t = Term([("$", P_CAFE, C("vol-ls"))] + [("o", l) for l in R("vol-ls")], 96, 214, size=40, w=1000, lh=1.6)
t.band(2, order=1, color="rgba(127,209,139,.18)")
o.append(t.html())
o += tag(t, 2, "-v에 적은 이름", GR, 1)
rows = [("docker volume ls", "볼륨 목록 보기"), ("docker volume rm 이름", "볼륨 지우기 (붙은 컨테이너를 먼저 지워요)")]
o.append(f'<div{STAGGER(2, 100)} style="position:absolute;left:96px;top:{t.y + t.h + 60}px;width:1728px;display:flex;flex-direction:column">'
         + "".join(f'<div style="display:flex;flex-direction:row;align-items:center;gap:40px;height:130px;border-top:2px solid {LINE}">'
                   + p(f"width:640px;font-family:{MONO};font-size:38px;font-weight:700;color:{INK};white-space:nowrap", e(a_)) + p(f"font-size:32px;color:{SUB}", e(b_)) + '</div>' for a_, b_ in rows) + f'<div style="height:2px;background:{LINE}"></div></div>')
o.append(p(f"position:absolute;left:1180px;top:240px;width:644px;font-size:32px;line-height:1.55;color:{SUB}", "Docker Desktop 왼쪽<br><b style=\"color:" + INK + "\">Volumes</b> 메뉴에서도 보여요.", bi("fade", 3)))
W("v-ls", o, "docker volume ls는 지금 남아 있는 볼륨 목록이에요. 앞 장에서 -v에 적은 cafe-html이 보여요. DRIVER의 local은 내 컴퓨터 안에 저장한다는 뜻이에요. 컨테이너를 지워도 볼륨은 남으니, 안 쓰는 볼륨은 docker volume rm 이름으로 지워요. 컨테이너가 붙어 있으면 지울 수 없어서 컨테이너부터 지워요. 29처럼 Docker Desktop 화면의 Volumes 메뉴에서도 확인할 수 있어요. 명령은 터미널에서 쳐요." + REAL)

o = frame("v-bind", EB2, "-v ./폴더:경로는 내 폴더를 컨테이너에 그대로 연결해요", GR)
bcmd = D["bind"][1]["cmd"]
t = Term([("$", P_CAFE, bcmd, {"./site": "vb-site"})], 96, 214, size=26, w=1728, tid="t-vb")
o.append(t.html())
sx_ = t.sx(0, "./site")
o.append(underline(1, round(sx_), round(sx_ + t.sw("./site")), round(t.top(0) + t.lp - 4), GR))
s1 = SITE2.strip().split("\n")
ed, g = editor("vb-ed", "site/index.html", s1, 96, 380, 900, fs=32, color=GR)
o.append(ed)
o.append(lband(2, g, 3, 1, GR, "rise"))
o.append(browser(1040, 380, 784, 460, "localhost:8080", page_menu(True, 3, 1.15), "br-vb"))
o.append(cursor(3, 1200, 410))
o.append(cursor_off(4))
o.append(caption("VS Code에서 저장하고 새로 고치기만 하면 돼요.", 870, 3, left=1040, width=784, size=30, color=GR))
o.append(p(f"position:absolute;left:96px;top:{g['top'] + g['h'] + 40:.0f}px;width:900px;font-size:30px;line-height:1.5;color:{SUB}", "<b style=\"color:" + INK + "\">./</b>로 시작하면 내 폴더, 아니면 볼륨 이름이에요.", bi("fade", 4)))
W("v-bind", o, "볼륨 이름 대신 ./site처럼 내 폴더를 적으면 그 폴더가 컨테이너 안 경로에 그대로 연결돼요. 앞의 ./는 01에서 배운 지금 폴더라는 뜻이에요. 그래서 ~/cafe 폴더에서 쳐야 해요. VS Code로 site/index.html에 카페라테 한 줄을 더하고 저장해요. 브라우저를 새로 고치면 바로 보여요. 컨테이너 안에 들어가지 않고 내 편집기로 고치는 거예요. ./를 빼고 site만 적으면 site라는 이름의 볼륨이 새로 생겨요. 5파트에서 그 장면을 봐요." + REAL)

o = frame("v-cmp", EB2, "남길 때는 볼륨, 고치면서 볼 때는 폴더 연결을 써요", GR)
hd = ["", "볼륨 이름", "내 폴더 연결"]
rows = [("쓰는 모양", "-v cafe-html:경로", "-v ./site:경로"), ("파일이 있는 곳", "Docker가 관리하는 곳", "내 폴더 (VS Code로 열려요)"),
        ("목록 보기", "docker volume ls", "ls site"), ("고르는 때", "컨테이너가 만든 데이터를 남길 때", "내가 고친 파일을 바로 보고 싶을 때")]
xs, wd = [96, 480, 1160], [380, 660, 664]
o.append(p(f"position:absolute;left:{xs[1]}px;top:222px;font-size:30px;font-weight:700;color:{GR}", hd[1]))
o.append(p(f"position:absolute;left:{xs[2]}px;top:222px;font-size:30px;font-weight:700;color:{BL}", hd[2]))
for i, r in enumerate(rows):
    y = 290 + i * 140
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:2px;background:{LINE}"></div>')
    for k, c_ in enumerate(r):
        mono = c_.startswith("-v") or c_.startswith("docker") or c_.startswith("ls")
        o.append(p(f"position:absolute;left:{xs[k]}px;top:{y + 46}px;width:{wd[k]}px;{'font-family:' + MONO + ';' if mono else ''}font-size:30px;font-weight:{700 if k == 0 or mono else 500};color:{INK if k else SUB};white-space:nowrap",
                   e(c_), bi("rise", 1) + DELAY(i * 90) if k else ""))
o.append(f'<div style="position:absolute;left:96px;top:{290 + 4 * 140}px;width:1728px;height:2px;background:{LINE}"></div>')
o.append(pen_box(2, xs[2] + round(tw("-v ", 30)) - 8, 290 + 38, round(tw("./", 30)) + 12, 58, BL))
o.append(caption("4파트 compose와 6파트 예제에서는 폴더 연결을 써요.", 900, 2, size=30, color=SUB))
W("v-cmp", o, "두 가지 -v를 나란히 놓았어요. 볼륨 이름을 적으면 Docker가 알아서 정한 곳에 저장해요. 지워지면 안 되는 데이터를 남길 때 써요. 데이터베이스처럼 컨테이너가 계속 쓰는 파일이 그런 예예요. 폴더 연결은 내 컴퓨터의 폴더를 그대로 보여 줘서 VS Code로 고치고 바로 확인할 때 좋아요. 둘을 가르는 건 이름 앞의 ./ 하나예요. 이후 compose와 실습 예제에서는 폴더 연결을 써요.")

# =====================================================================
# part 3: Dockerfile
# =====================================================================
o = frame("d-why", EB3, "장바구니를 친구 컴퓨터에서 돌리려면 준비할 게 많아요", TEAL)
need = ["파이썬 3.14 설치", "uv 설치", "uv sync", "uv run main.py"]
o.append(p(f"position:absolute;left:96px;top:230px;font-size:30px;font-weight:700;color:{GRAY}", "지금까지 (09, 28)"))
o.append(f'<div{STAGGER(1, 100)} style="position:absolute;left:96px;top:290px;width:820px;display:flex;flex-direction:column;gap:16px">'
         + "".join(f'<div style="display:flex;flex-direction:row;align-items:center;gap:22px;height:92px;background:{CARD};border:2px solid {LINE};border-radius:16px;padding:0 28px">'
                   + p(f"width:44px;height:44px;flex:none;border-radius:22px;background:{GRAY};color:#FFFFFF;font-size:24px;font-weight:900;line-height:44px;text-align:center", str(i + 1))
                   + p(f"font-size:30px;font-weight:700;color:{INK};{'font-family:' + MONO if n in ('uv sync', 'uv run main.py') else ''}", e(n)) + '</div>' for i, n in enumerate(need)) + '</div>')
o.append(p(f"position:absolute;left:96px;top:740px;width:820px;font-size:26px;line-height:1.5;color:{SUB}", "Windows와 Mac, 파이썬 버전마다<br>막히는 곳이 달라요.", bi("fade", 1)))
o.append(p(f"position:absolute;left:1040px;top:230px;font-size:30px;font-weight:700;color:{TEAL}", "이미지로 건네면", bi("fade", 2)))
o.append(image_box(1040, 290, 784, "cart", ["파이썬 3.14 + uv", "장바구니 코드", "uv sync 끝난 상태"], bid="dw-img", attrs=bi("rise", 2), lh=56))
o.append(f'<div{bi("rise", 3)} style="position:absolute;left:1040px;top:640px;width:784px;height:92px;background:{CARD};border:2px solid {TEAL};border-radius:16px;display:flex;flex-direction:row;align-items:center;gap:22px;padding:0 28px">'
         + p(f"width:44px;height:44px;flex:none;border-radius:22px;background:{TEAL};color:#FFFFFF;font-size:24px;font-weight:900;line-height:44px;text-align:center", "1")
         + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{INK}", "docker run cart") + '</div>')
o.append(p(f"position:absolute;left:1040px;top:760px;width:784px;font-size:26px;line-height:1.5;color:{SUB}", "Docker만 있으면 어느 컴퓨터에서나 같은 결과예요.", bi("fade", 3)))
W("d-why", o, "28의 장바구니를 친구 컴퓨터에서 돌린다고 해 봐요. 09에서 했던 것처럼 파이썬과 uv를 설치하고, uv sync로 패키지를 맞춘 뒤에야 uv run main.py를 칠 수 있어요. 운영체제와 파이썬 버전에 따라 막히는 곳도 달라요. 이 준비를 모두 마친 상태를 이미지로 구워 두면, 친구는 Docker만 설치하고 docker run 한 줄로 같은 결과를 봐요. 그 이미지를 만드는 레시피가 Dockerfile이에요.", ("p3", "Dockerfile로 이미지 만들기"))

o = frame("d-file", EB3, "Dockerfile은 다섯 줄이에요", TEAL)
ed, g = editor("df-ed", "Dockerfile", df_lines, 96, 214, 1000, fs=36, color=TEAL)
o.append(ed)
lab = [("어떤 틀 위에서 시작할까", "파이썬과 uv가 든 이미지"), ("안에서 일할 폴더", "없으면 만들고 cd 해요"), ("내 파일을 넣기", "지금 폴더를 /app으로"),
       ("만들 때 한 번 실행", "패키지 맞추기"), ("찍을 때마다 실행", "켜지면 칠 명령")]
LX = 1150
for i, (a_, b_) in enumerate(lab):
    o += leader(gx(g, df_lines[i]) + 16, gcy(g, i), LX, TEAL, i + 1)
    o.append(p(f"position:absolute;left:{LX}px;top:{gcy(g, i) - 21:.0f}px;font-size:28px;font-weight:700;line-height:1.5;color:{TEAL};white-space:nowrap",
               e(a_) + f' <span style="font-size:22px;font-weight:500;color:{SUB}">{e(b_)}</span>', bi("rise", i + 1)))
for i in range(5):
    o.append(lspot(i + 1, g["left"] + 2, g["y0"] - 6, g["w"] - 4, g["n"] * g["lh"] + 12, gtop(g, i), g["lh"], bar=TEAL))
o.append(lspot_off(6))
o.append(caption("파일 이름은 확장자 없이 <span style=\"font-family:" + MONO + "\">Dockerfile</span>, D는 대문자예요.", g["top"] + g["h"] + 70, 6, size=32))
o.append(p(f"position:absolute;left:96px;top:{g['top'] + g['h'] + 134:.0f}px;font-size:28px;color:{SUB}", "shopping-cart 폴더 맨 위, main.py 옆에 VS Code로 새 파일을 만들어요.", bi("rise", 6)))
W("d-file", o, "shopping-cart 폴더 맨 위에 Dockerfile이라는 새 파일을 만들어 다섯 줄을 적어요. 확장자는 없고 첫 글자 D는 대문자예요. 위에서부터 한 줄씩 읽어요. FROM은 어떤 이미지 위에서 시작할지예요. WORKDIR은 이미지 안에서 일할 폴더예요. COPY는 내 폴더의 파일을 이미지 안으로 넣어요. RUN은 이미지를 만드는 동안 한 번 실행할 명령이고, CMD는 이 이미지로 컨테이너를 찍을 때마다 실행할 명령이에요. 다음 장부터 한 줄씩 자세히 봐요.")

o = frame("d-from", EB3, "FROM: uv를 만든 회사의 이미지 위에서 시작해요", TEAL)
o += parts(96, 240, [("FROM ", TEAL, None, None), ("astral/uv", BL, "만든 곳/이미지 이름", None), (":", GRAY, None, None),
                     ("python3.14", OR, "파이썬 버전", None), ("-bookworm-slim", GRAY, "리눅스 종류<br>(가벼운 판)", None)], size=54, order=1, lab=26, drop=36, sep=0, lw=360)
o.append(p(f"position:absolute;left:96px;top:520px;font-size:28px;font-weight:700;color:{INK}", "29에서 본 이미지 이름 규칙 그대로예요.", bi("fade", 2)))
o.append(p(f"position:absolute;left:96px;top:570px;font-family:{MONO};font-size:30px;font-weight:700;color:{SUB}", '이름<span style="color:' + GRAY + '">:</span>태그', bi("fade", 2)))
# hub card (satellite) and .python-version
hub = (f'<div{bi("rise", 3)} style="position:absolute;left:96px;top:660px;width:900px;height:300px;background:{CARD};border:1px solid #D2CEC4;border-radius:18px;box-shadow:{SHADOW};padding:30px 36px;display:flex;flex-direction:column;gap:14px">'
       + p(f"font-size:22px;font-weight:700;color:{GRAY}", "Docker Hub")
       + p(f"font-family:{MONO};font-size:34px;font-weight:700;color:{INK}", "astral/uv")
       + p(f"font-size:24px;line-height:1.4;color:{SUB}", "The official Docker image for uv, the Python package manager.")
       + p(f"font-size:26px;font-weight:700;line-height:1.45;color:{OR}", "인증 마크는 없어요. uv를 만든 회사 Astral이 올렸고<br>uv 공식 문서가 이 이미지를 안내해요.") + '</div>')
o.append(hub)
ed, g = editor("pv-ed", ".python-version", ["3.14"], 1100, 660, 724, fs=34, color=OR, attrs=bi("rise", 4))
o.append(ed)
o.append(p(f"position:absolute;left:1100px;top:{g['top'] + g['h'] + 24:.0f}px;width:724px;font-size:26px;line-height:1.5;color:{SUB}", "28 프로젝트의 버전과 FROM의<br>python 숫자를 맞춰요.", bi("rise", 4)))
o.append(link(4, 1300, 650, 96 + tw("FROM astral/uv:python3.1", 54), 420, OR))
W("d-from", o, "FROM 뒤에는 시작할 이미지를 적어요. 29에서 본 이름:태그 모양 그대로예요. astral/uv는 uv를 만든 회사 Astral이 Docker Hub에 올린 이미지예요. 29에서 Docker Official Image 인증 마크를 먼저 보라고 했는데, 이 이미지에는 마크가 없어요. 대신 uv를 만든 회사가 직접 올렸고 uv 공식 문서도 이 이미지를 쓰라고 안내해요. 마크가 없는 이미지는 이렇게 누가 올렸는지 확인하고 써요. 태그의 python3.14는 이미지에 든 파이썬 버전, bookworm-slim은 리눅스 종류예요. 28 프로젝트의 .python-version 숫자와 맞춰요. 내 파일이 3.13이면 python3.13으로 바꿔요.")

o = frame("d-copy", EB3, "WORKDIR과 COPY: 내 파일을 이미지 안 /app에 넣어요", TEAL)
o.append(p(f"position:absolute;left:96px;top:222px;font-family:{MONO};font-size:40px;font-weight:700;color:{INK};white-space:pre", f'WORKDIR <span style="color:{TEAL}">/app</span>'))
o.append(p(f"position:absolute;left:96px;top:282px;font-family:{MONO};font-size:40px;font-weight:700;color:{INK};white-space:pre", f'COPY <span style="color:{BL}">.</span> <span style="color:{TEAL}">.</span>'))
o.append(p(f"position:absolute;left:{96 + tw('COPY . . ', 40) + 30:.0f}px;top:292px;font-size:26px;font-weight:700;color:{SUB};white-space:nowrap", f'<span style="color:{BL}">지금 폴더</span>를 <span style="color:{TEAL}">일하는 폴더(/app)</span>로'))
files = ["main.py", "cart.py", "product.py", "pyproject.toml", "uv.lock", ".python-version", "Dockerfile"]
o.append(f'<div id="cp-src" style="position:absolute;left:96px;top:400px;width:700px;height:520px;background:{CARD};border:2px solid {LINE};border-radius:20px;padding:24px 28px">'
         + p(f"font-size:24px;font-weight:700;color:{BL}", "내 컴퓨터 ~/shopping-cart") + '</div>')
o.append(f'<div style="position:absolute;left:1124px;top:400px;width:700px;height:520px;background:{MDBG};border:3px solid {MD};border-radius:20px;padding:24px 28px">'
         + p(f"font-size:24px;font-weight:700;color:{MD}", '이미지 안 <span style="font-family:' + MONO + '">/app</span>') + '</div>')
for i, n in enumerate(files):
    cx_, cy_ = 130 + (i % 2) * 330, 470 + (i // 2) * 100
    o.append(f'<div id="cp-s{i}" style="position:absolute;left:{cx_}px;top:{cy_}px">' + file_chip(n, size=24) + '</div>')
    o.append(f'<div data-build-in="fly order {1}" data-from="cp-s{i}"{DELAY(i * 90)} style="position:absolute;left:{cx_ + 1028}px;top:{cy_}px">' + file_chip(n, MD, size=24) + '</div>')
o.append(harrow(820, 1100, 660, TEAL, 1))
o.append(caption("이제 이미지 안에서 uv sync, uv run main.py를 칠 수 있어요.", 950, 2, size=30, color=TEAL))
W("d-copy", o, "WORKDIR /app은 이미지 안에 /app 폴더를 만들고 그 안으로 cd 하는 줄이에요. 뒤의 줄들은 모두 /app에서 실행돼요. COPY . .의 첫 번째 점은 내 컴퓨터의 지금 폴더, 두 번째 점은 이미지 안의 지금 폴더(/app)예요. 그래서 shopping-cart 폴더의 파일이 /app으로 복사돼요. 01에서 배운 cp와 비슷하지만, 내 컴퓨터에서 이미지 안으로 넘어간다는 점이 달라요. .venv 같은 폴더도 같이 넘어가는데, 이건 .dockerignore 장에서 다뤄요.")

o = frame("d-runcmd", EB3, "RUN은 틀을 만들 때 한 번, CMD는 찍을 때마다 실행돼요", TEAL)
rows_ = [("docker build", TEAL, "RUN uv sync", "틀 만들 때 한 번", 250), ("docker run", BR, 'CMD ["uv", "run", "main.py"]', "붕어빵 찍을 때마다", 600)]
for k, (cm, c_, line, when, y) in enumerate(rows_):
    o.append(p(f"position:absolute;left:96px;top:{y}px;font-family:{MONO};font-size:36px;font-weight:700;color:{c_}", e(cm), bi("fade", k + 1)))
    o.append(p(f"position:absolute;left:96px;top:{y + 58}px;font-size:28px;color:{SUB}", e(when), bi("fade", k + 1)))
    o.append(p(f"position:absolute;left:96px;top:{y + 120}px;height:76px;padding:0 26px;border-radius:14px;background:{CARD};border:3px solid {c_};font-family:{MONO};font-size:30px;font-weight:700;line-height:70px;color:{INK};white-space:nowrap", e(line), bi("pop", k + 1)))
o.append(harrow(700, 900, 410, TEAL, 1))
o.append(image_box(940, 250, 520, "cart", ["… COPY . .", "RUN uv sync 결과 (.venv)"], attrs=bi("rise", 1), lh=54))
o.append(p(f"position:absolute;left:1490px;top:300px;width:334px;font-size:28px;font-weight:700;line-height:1.45;color:{TEAL}", "결과가 틀 안에<br>구워져요", bi("fade", 1)))
o.append(harrow(700, 900, 790, BR, 2))
for j in range(3):
    o.append(container_box(940 + j * 300, 700, 280, 180, "cart", p(f"font-family:{MONO};font-size:20px;font-weight:700;color:{BR};white-space:nowrap", "uv run main.py") + p(f"font-size:20px;color:{SUB}", f"{j + 1}번째 실행"), attrs=bi("rise", 2) + DELAY(j * 150), status=""))
o.append(caption("CMD는 틀에 적어만 뒀다가 붕어빵을 찍을 때마다 실행해요.", 930, 3, size=30))
W("d-runcmd", o, "RUN과 CMD는 둘 다 명령을 적지만 실행되는 때가 달라요. RUN uv sync는 docker build로 틀을 만드는 동안 딱 한 번 실행되고, 그 결과(.venv)가 틀 안에 구워져요. CMD는 틀에 적어만 둬요. docker run으로 붕어빵을 찍을 때마다 그 명령이 실행돼요. 붕어빵을 세 개 찍으면 uv run main.py가 세 번 돌아요. CMD는 대괄호 안에 명령을 낱말마다 따옴표로 나눠 적어요. 파이썬 리스트와 모양이 같아요.")

o = frame("d-build", EB3, "docker build -t cart .로 틀을 구워요", TEAL)
o += parts(96, 214, [("docker", INK, None, None), ("build", TEAL, "틀 굽기", None), ("-t", OR, None, None), ("cart", OR, "이미지 이름", None), (".", BL, "재료가 있는 폴더<br>(지금 폴더)", None)], size=48, order=1, lab=24, drop=26, lw=210, sep=3)
bl = short_build(BUILD)
lines = [("$", P_CART, C("build"))] + [("g" if "FINISHED" in l else "o", l) for l in bl]
t = Term(lines, 96, 440, size=22, w=1180, lh=1.5)
steps = [i for i, l in enumerate([r[-1] for r in lines[1:]], 1) if re.search(r"\[\d/4\]", l)]
t.band(steps[0], steps[-1], order=2, color="rgba(79,184,194,.16)")
nm = [i for i, r in enumerate(lines) if "naming to" in r[-1]][0]
t.band(1, order=3, color="rgba(127,209,139,.16)")
t.band(nm, order=3, color="rgba(242,196,109,.17)")
o.append(t.html())
LX = t.x + t.w + 40
o += leader(t.x + t.w + 8, t.cy(steps[0]) + (t.cy(steps[-1]) - t.cy(steps[0])) / 2, LX, TEAL, 2, "Dockerfile 1~4줄", size=26, sub="CMD 줄은 적어만 둬요")
o += leader(t.x + t.w + 8, t.cy(1), LX, GR, 3, "끝나면 FINISHED", size=26)
o += leader(t.x + t.w + 8, t.cy(nm), LX, OR, 3, "이름이 cart", size=26)
W("d-build", o, "shopping-cart 폴더에서 docker build -t cart .를 쳐요. -t cart는 만들 이미지에 cart라는 이름을 붙이는 옵션이에요. 맨 끝의 점은 재료가 있는 폴더, 곧 지금 폴더예요. 점을 빼먹으면 오류가 나요. 출력의 [1/4]부터 [4/4]가 Dockerfile의 FROM, WORKDIR, COPY, RUN 줄이에요. CMD는 적어만 두는 줄이라 단계에 없어요. 처음에는 FROM의 astral/uv 이미지를 받느라 시간이 조금 걸려요. => => 로 시작하는 세부 줄은 빼고 옮겼어요. 숫자와 시간은 컴퓨터마다 달라요." + REAL)

o = frame("d-run", EB3, "docker run cart로 내가 구운 틀에서 붕어빵을 찍어요", TEAL)
t1 = Term([("$", P_CART, C("images"))] + [("o", l) for l in R("images")], 96, 214, size=22, w=1000, tid="t-img")
t1.band(2, order=1, color="rgba(242,196,109,.17)")
o.append(t1.html())
o.append(pen_box(1, round(t1.tx - 8), round(t1.top(2) - 3), round(t1.sw("cart:latest") + 16), round(t1.lp + 6), OR))
rc = R("run-cart")
t2 = Term([("$", P_CART, C("run-cart"))] + [("o", l) for l in rc], 96, t1.y + t1.h + 24, size=19, w=1000, tid="t-run", attrs=bi("rise", 2))
o.append(t2.html())
o.append(p(f"position:absolute;left:1160px;top:240px;font-size:28px;font-weight:700;color:{GRAY}", "28에서 친 명령과 비교", bi("fade", 3)))
cmpr = [("uv run main.py", "내 컴퓨터의 파이썬과 uv로", BL), ("docker run cart", "이미지 안의 파이썬과 uv로", TEAL)]
for k, (a_, b_, c_) in enumerate(cmpr):
    y = 300 + k * 170
    o.append(f'<div{bi("rise", 3)} style="position:absolute;left:1160px;top:{y}px;width:664px;height:140px;background:{CARD};border:2px solid {LINE};border-left:8px solid {c_};border-radius:16px;padding:18px 26px;display:flex;flex-direction:column;gap:6px">'
             + p(f"font-family:{MONO};font-size:34px;font-weight:700;color:{INK}", e(a_)) + p(f"font-size:26px;color:{SUB}", e(b_)) + '</div>')
o.append(p(f"position:absolute;left:1160px;top:670px;width:664px;font-size:32px;font-weight:700;line-height:1.5;color:{TEAL}", "출력이 한 글자도 다르지 않아요.", bi("fade", 3)))
W("d-run", o, "docker images로 보면 cart:latest가 생겼어요. 태그를 안 적으면 latest가 붙는 건 29와 같아요. 이제 docker run cart를 치면 CMD에 적은 uv run main.py가 컨테이너 안에서 실행되고 28 실습의 영수증이 그대로 나와요. nginx처럼 계속 도는 프로그램이 아니라 영수증을 찍고 끝나는 프로그램이라 -d와 -p는 붙이지 않아요. 내 컴퓨터에서 uv run main.py를 친 결과와 비교해 보세요. 출력이 똑같아요. 다른 점은 파이썬과 uv가 내 컴퓨터가 아니라 이미지 안에 있다는 것뿐이에요." + REAL)

o = frame("d-stale", EB3, "코드를 고쳤으면 build부터 다시 해요", TEAL)
ed, g = editor("st-ed", "main.py", ["cart = Cart()", 'cart.add(tumbler, <span id="st-n" data-start="2" style="background:#F7EEDD;border-radius:4px;padding:0 4px">3</span>)', "cart.add(earphone, 1)"], 96, 214, 760, fs=28, color=OR)
o.append(ed)
o.append(set_text(1, "st-n", "3"))
st = R("stale")
t = Term([("$", P_CART, C("stale"))] + [("o", l) for l in st[:5]] + [("d", "…")], 920, 214, size=24, w=904, tid="t-stale", attrs=bi("rise", 2))
o.append(t.html())
o.append(underline(3, round(t.tx), round(t.tx + t.sw(st[0])), round(t.top(1) + t.lp - 2), RED))
o.append(pill(96, g["top"] + g["h"] + 40, "build할 때 복사한 옛 main.py로 찍었어요", RED, 3))
rb = R("rebuild")
keep = lambda l: ("[+]" in l or re.search(r"\[\d/4\]", l))
bl = []
for l in short_build(rb):
    if keep(l):
        bl.append(l)
    elif bl and bl[-1] != "…":
        bl.append("…")
lines = [("$", P_CART, C("rebuild"))] + [("g" if "FINISHED" in l else ("d" if l == "…" else "o"), l) for l in bl] + [("$", P_CART, D["rebuild"][1]["cmd"])] + [("o", D["rebuild"][1]["out"][0]), ("d", "…")]
t2 = Term(lines, 96, 560, size=20, w=1728, lh=1.4, tid="t-rb", attrs=bi("rise", 4))
TXT = [r[-1] if isinstance(r[-1], str) else r[-2] for r in lines]
cl = [i for i, l in enumerate(TXT) if "CACHED" in l][0]
cp = [i for i, l in enumerate(TXT) if "COPY" in l][0]
t2.band(cl, order=5, color="rgba(127,134,150,.25)")
t2.band(cp, cp + 1, order=5, color="rgba(79,184,194,.18)")
t2.band(len(lines) - 2, order=6, color="rgba(127,209,139,.18)")
o.append(t2.html())
o += tag(t2, cl, "그대로 써요", GRAY, 5, at=t2.x + 1080)
o += tag(t2, cp, "바뀐 COPY부터 다시", TEAL, 5, at=t2.x + 1330)
o += tag(t2, len(lines) - 2, "이제 3개", GR, 6)
W("d-stale", o, "main.py에서 텀블러를 3개로 고치고 바로 docker run cart를 쳐요. 영수증은 여전히 2개예요. 틀인 이미지에는 build할 때 복사한 옛 main.py가 들어 있기 때문이에요. 그래서 코드를 고치면 docker build -t cart .부터 다시 쳐요. 두 번째 build는 빨라요. 바뀌지 않은 WORKDIR 줄은 CACHED로 전에 만든 층을 그대로 쓰고, 파일이 바뀐 COPY 줄부터 다시 만들어요. 다시 run 하면 이제 3개가 담겨요. 출력은 줄여서 앞부분만 옮겼어요." + REAL)

o = frame("d-rm", EB3, "run할 때마다 컨테이너가 쌓여요. --rm을 붙이면 끝나고 지워져요", TEAL)
t = Term([("$", P_CART, C("psa"))] + [("o", l) for l in R("psa")], 96, 214, size=18, w=1728, lh=1.6, tid="t-psa")
t.band(1, 3, order=1, color="rgba(240,122,114,.16)")
o.append(t.html())
o.append(pill(t.sx(2, "Exited"), t.y + t.h + 16, "Exited 컨테이너 3개", RED, 1))
rr = D["rm-run"]
t2 = Term([("$", P_CART, rr[0]["cmd"], {"--rm": "rm-flag"}), ("d", rr[0]["out"][0]), ("d", "…"), ("$", P_CART, rr[1]["cmd"])] + [("o", l) for l in R("rm-run", 1)], 96, t.y + t.h + 90, size=18, w=1728, lh=1.6, tid="t-rmrun", attrs=bi("rise", 2))
o.append(t2.html())
o.append(underline(3, round(t2.sx(0, "--rm")), round(t2.sx(0, "--rm") + t2.sw("--rm")), round(t2.top(0) + t2.lp - 3), OR))
o.append(caption("--rm으로 찍은 붕어빵은 목록에 늘지 않아요. 영수증처럼 찍고 끝나는 프로그램에 붙여요.", t2.y + t2.h + 34, 3, size=28))
W("d-rm", o, "docker ps -a로 보면 docker run cart를 칠 때마다 만든 컨테이너가 Exited 상태로 쌓여 있어요. 29에서 본 것처럼 run은 매번 새 붕어빵을 찍기 때문이에요. 이름은 --name을 안 줘서 Docker가 아무렇게나 지었어요. IMAGE 칸이 글자 대신 ID인 줄은 다시 build하기 전의 옛 cart로 찍은 컨테이너예요. docker run --rm cart처럼 --rm을 붙이면 프로그램이 끝날 때 컨테이너도 같이 지워져요. 다시 ps -a를 쳐도 목록이 늘지 않았어요. 쌓인 세 개는 6파트 정리 예제에서 지워요." + REAL)

o = frame("d-ignore", EB3, ".dockerignore에 적은 파일은 이미지에 넣지 않아요", TEAL)
ig = DOCKERIGNORE.strip().split("\n")
ed, g = editor("ig-ed", ".dockerignore", ig, 96, 214, 620, fs=30, color=TEAL)
o.append(ed)
why = ["내 컴퓨터용 가상환경", "파이썬이 만든 임시 파일", "Git 기록"]
for i, w_ in enumerate(why):
    o += leader(gx(g, ig[i]) + 14, gcy(g, i), 446, TEAL, 1, None)
    o.append(p(f"position:absolute;left:446px;top:{gcy(g, i) - 16:.0f}px;font-size:22px;font-weight:700;color:{TEAL};white-space:nowrap", e(w_), bi("rise", 1)))
ca, cb = R("app-ls-all"), R("app-ls")
def lsbox(x, title, items, color, gone=(), order=None, bid=None):
    i = f' id="{bid}"' if bid else ""
    rows = "".join(p(f"font-family:{MONO};font-size:24px;font-weight:700;line-height:1.5;color:{RED if n in gone else INK};{'text-decoration:line-through;' if False else ''}white-space:nowrap", e(n)) for n in items if n not in (".", ".."))
    return (f'<div{i}{bi("rise", order)} style="position:absolute;left:{x}px;top:214px;width:530px;background:{CARD};border:2px solid {LINE};border-top:6px solid {color};border-radius:16px;padding:20px 26px;display:flex;flex-direction:column;gap:2px">'
            + p(f"font-size:24px;font-weight:700;color:{color};margin-bottom:8px;white-space:nowrap", title) + rows + '</div>')
o.append(lsbox(760, '없을 때 <span style="font-family:' + MONO + '">/app</span>', [n for n in ca if n != ".dockerignore.off"], GRAY, gone=(".git", "__pycache__"), order=2))
o.append(lsbox(1294, '있을 때 <span style="font-family:' + MONO + '">/app</span>', cb, TEAL, order=3))
o.append(p(f"position:absolute;left:96px;top:{g['top'] + g['h'] + 40:.0f}px;width:600px;font-size:24px;line-height:1.5;color:{SUB}", "이미지 안의 .venv는 RUN uv sync가<br>리눅스용으로 새로 만든 거예요.", bi("fade", 3)))
cb_ = [l for l in R("ctx-before") if "transferring context" in l][-1].split(":")[-1].split()[0]
ca_ = [l for l in R("ctx-after") if "transferring context" in l][-1].split(":")[-1].split()[0]
o.append(p(f"position:absolute;left:96px;top:{g['top'] + g['h'] + 160:.0f}px;font-size:26px;font-weight:700;color:{INK};white-space:nowrap", "build할 때 보내는 재료 (transferring context)", bi("fade", 4)))
o.append(p(f"position:absolute;left:96px;top:{g['top'] + g['h'] + 210:.0f}px;font-family:{MONO};font-size:48px;font-weight:700;color:{TEAL};white-space:nowrap", f'<span style="color:{GRAY}">{e(cb_)} →</span> <span id="ig-sz">{e(ca_)}</span>', bi("fade", 4)))
W("d-ignore", o, "COPY . .은 폴더의 모든 파일을 넣어요. 그런데 .venv는 내 컴퓨터의 파이썬에 맞춰 만든 가상환경이라 리눅스인 이미지 안에서는 못 써요. .git과 __pycache__도 프로그램 실행에 필요 없어요. shopping-cart 폴더 맨 위에 .dockerignore 파일을 만들고 넣지 않을 이름을 한 줄에 하나씩 적어요. 04의 .gitignore와 같은 모양이에요. 왼쪽 목록에는 .git과 __pycache__가 들어가 있고, 오른쪽 목록에서는 빠졌어요. 이미지 안의 .venv는 RUN uv sync가 새로 만든 거예요. build할 때 Docker에 보내는 재료도 수십 kB에서 수백 B로 줄었어요. .venv를 넣으면 uv sync가 Ignoring existing virtual environment라는 경고를 내고 새로 만들어요." + REAL)

# =====================================================================
# part 4: compose
# =====================================================================
o = frame("c-why", EB4, "긴 docker run을 compose.yaml에 옮겨 적어요", MAG)
long_ = "docker run -d --name web -p 8080:80 -v ./site:/usr/share/nginx/html nginx"
o.append(p(f"position:absolute;left:96px;top:222px;font-size:26px;font-weight:700;color:{GRAY}", "지금까지 친 명령"))
segs = [("img", "nginx"), ("port", "-p 8080:80"), ("vol", "-v ./site:/usr/share/nginx/html")]
o.append(p(f"position:absolute;left:96px;top:270px;font-family:{MONO};font-size:34px;font-weight:700;line-height:1.4;white-space:pre;color:{INK}",
           'docker run -d --name web <span id="cw-port" style="color:' + OR + '">-p 8080:80</span> <span id="cw-vol" style="color:' + GR + '">-v ./site:/usr/share/nginx/html</span> <span id="cw-img" style="color:' + DK + '">nginx</span>'))
cy_ = COMPOSE.rstrip("\n").split("\n")
hl = {2: DK, 4: OR, 6: GR}
ylines = []
for i, l in enumerate(cy_):
    c_ = hl.get(i)
    ylines.append(f'<span style="color:{c_}">{e(l)}</span>' if c_ else l)
ed, g = editor("cw-ed", "compose.yaml", ylines, 96, 380, 900, fs=34, color=MAG, attrs=bi("rise", 1))
o.append(ed)
for i, (src, c_) in enumerate([("cw-img", DK), ("cw-port", OR), ("cw-vol", GR)]):
    li = [2, 4, 6][i]
    y_ = gcy(g, li)
    o.append(f'<div data-build-in="fly order {i + 2}" data-from="{src}" style="position:absolute;left:{gx(g, cy_[li]) + 30:.0f}px;top:{y_ - 22:.0f}px;height:44px;padding:0 14px;border-radius:9px;background:{c_};font-family:{MONO};font-size:22px;font-weight:700;line-height:44px;color:#FFFFFF;white-space:nowrap">{e([ "nginx", "-p 8080:80", "-v ./site:…"][i])}</div>')
o.append(p(f"position:absolute;left:1120px;top:420px;width:704px;font-size:30px;line-height:1.6;color:{SUB}", "<b style=\"color:" + INK + "\">services</b> 아래 <b style=\"color:" + INK + "\">web</b>이 컨테이너 하나예요.<br>들여쓰기는 2칸씩, 목록은 <span style=\"font-family:" + MONO + "\">-</span>로 시작해요.", bi("fade", 5)))
o.append(p(f"position:absolute;left:1120px;top:600px;width:704px;font-size:30px;line-height:1.6;color:{SUB}", "~/cafe 폴더 맨 위,<br>site 폴더 옆에 둬요.", bi("fade", 5)))
o.append(caption("한 번 적어 두면 다음부터는 짧은 명령 두 개로 켜고 꺼요.", 940, 5, size=30, color=MAG))
W("c-why", o, "2파트에서 친 명령은 옵션이 네 개나 붙어서 길어요. 칠 때마다 오타가 나기 쉬워요. docker compose는 이 내용을 compose.yaml 파일에 적어 두고 짧은 명령으로 켜고 끄는 도구예요. Docker Desktop에 같이 들어 있어요. services 아래 web이 컨테이너 하나예요. image는 이미지 이름, ports는 -p, volumes는 -v 자리예요. 이름은 web으로 적은 서비스 이름을 바탕으로 compose가 붙여 줘요. yaml은 들여쓰기로 소속을 정해요. 28에서 본 파이썬 들여쓰기와 같은 생각이고, 2칸씩 들여 써요. 맛보기라서 컨테이너 하나만 적었어요.", ("p4", "docker compose 맛보기"))

o = frame("c-up", EB4, "docker compose up -d로 켜고 down으로 지워요", MAG)
cu = R("compose-up")
cps = R("compose-ps")
cd_ = R("compose-down")
lines = [("$", P_CAFE, C("compose-up"))] + [("o", l) for l in cu] + [("o", ""), ("$", P_CAFE, C("compose-ps"))] + [("o", l) for l in cps] + [("o", ""), ("$", P_CAFE, C("compose-down"))] + [("o", l) for l in cd_]
t = Term(lines, 96, 214, size=20, w=1728, lh=1.55)
t.band(1, len(cu), order=1, color="rgba(224,127,176,.16)")
psi = len(cu) + 3
t.band(psi, psi + 1, order=2, color="rgba(242,196,109,.17)")
dni = psi + 3
t.band(dni, len(lines) - 1, order=4, color="rgba(240,122,114,.14)")
o.append(t.html())
o += tag(t, 1, "-d 그대로, 뒤에서 돌아요", MAG, 1, at=t.x + 1160)
o += tag(t, dni, "stop과 rm을 한 번에", RED, 4, at=t.x + 1160)
nx = t.tx
o.append(pen_box(2, round(nx - 6), round(t.top(psi + 1) - 2), round(t.sw("cafe-web-1") + 12), round(t.lp + 4), MAG))
yb = t.y + t.h + 30
o.append(pill(96, yb, "이름: 폴더 이름-서비스 이름-번호", MAG, 2))
o.append(p(f"position:absolute;left:96px;top:{yb + 70}px;width:1100px;font-size:26px;line-height:1.55;color:{SUB}", "Network 줄은 compose가 만든 연결망이에요. 이 챕터에서는 넘어가요.", bi("fade", 4)))
o.append(browser(1250, yb, 574, 1040 - yb - 10, "localhost:8080", page_menu(False, None, 0.8), "br-cu", attrs=SLIDE(3, 300, 0)))
W("c-up", o, "compose.yaml이 있는 ~/cafe 폴더에서 docker compose up -d를 쳐요. -d는 29의 docker run -d처럼 뒤에서 돌게 하는 옵션이에요. docker compose ps는 이 폴더의 compose가 띄운 컨테이너만 보여 줘요. 이름 cafe-web-1은 폴더 이름 cafe, 서비스 이름 web, 첫 번째라는 1을 이은 거예요. 브라우저에는 2파트의 메뉴 페이지가 그대로 나와요. 다 쓰면 docker compose down으로 멈추고 지워요. Network 줄은 compose가 컨테이너끼리 이어 주려고 만든 연결망인데, 이 챕터에서는 다루지 않아요." + REAL)

# =====================================================================
# part 5: errors
# =====================================================================
o = frame("x-build", EB5, "build 오류는 마지막 ERROR 줄부터 읽어요", RED)
nd = R("err-nodot", wrap=True)
nf = [l for l in R("err-nofile", wrap=True) if l.startswith("ERROR")]
fr = R("err-from", wrap=True)
fe = [l for l in fr if l.startswith("ERROR")]
fl = [l for l in fr if l.startswith("   1 |")]
y = 214
blocks = [("err-nodot", P_CART, nd[:1], "끝의 점(.)을 빼먹었어요", "docker build -t cart ."),
          ("err-nofile", P_HOME, nf, "Dockerfile이 없는 폴더에서 쳤어요", "cd shopping-cart"),
          ("err-from", P_CART, fl + rewrap(fe, 132), "FROM의 이미지 이름이나 태그에 오타가 있어요", "bookwrom → bookworm")]
for k, (sc, pth, ls_, why_, fix) in enumerate(blocks):
    t = Term([("$", pth, C(sc))] + [("e" if l.startswith("ERROR") else "o", l) for l in ls_], 96, y, size=20, w=1728, lh=1.5, tid=f"t-xb{k}", attrs=bi("rise", k + 1) if k else "")
    o.append(t.html())
    yy = t.y + t.h + 12
    o.append(p(f"position:absolute;left:96px;top:{yy}px;font-size:26px;font-weight:700;color:{INK}", e(why_), bi("fade", k + 1) if k else ""))
    o.append(pill(96 + tw(why_, 26, False) + 40, yy - 4, fix, GR, k + 1 if k else None, size=22))
    y = yy + 64
W("x-build", o, "build가 실패하면 출력 맨 아래 ERROR 줄을 먼저 읽어요. 첫 번째는 끝의 점을 빼먹었을 때예요. requires 1 argument는 재료 폴더를 하나 적으라는 뜻이에요. 두 번째는 Dockerfile이 없는 홈 폴더에서 쳤을 때예요. open Dockerfile: no such file or directory가 나오면 pwd로 위치를 보고 cd shopping-cart로 들어가요. 세 번째는 FROM의 태그에 오타가 있을 때예요. 몇 번째 줄이 틀렸는지 >>> 표시로 보여 주고, Hub에 없는 이름이라 not found가 나와요. 긴 줄은 터미널 창 너비에 따라 꺾이는 자리가 달라요. 세 번째는 줄 표시와 ERROR 줄만 옮겼어요." + REAL, ("p5", "자주 나는 오류"))

o = frame("x-run", EB5, "run과 exec 오류는 원인이 한 줄에 다 적혀 있어요", RED)
y = 214
pb = R("port-busy")
pbe = [l for l in pb if l.startswith("docker: Error")][0]
pbe_short = pbe.split("): ")[-1] if "): " in pbe else pbe
xs_ = [("err-cmd", P_CART, C("err-cmd").replace("cart-typo", "cart"), R("err-cmd"), "CMD의 파일 이름 오타 (mian.py)", "Dockerfile 고치고 다시 build"),
       ("exec-stopped", P_CAFE, D["exec-stopped"][1]["cmd"], ["Error response from daemon: container " + WEB_ID[:12] + "… is not running"], "멈춘 컨테이너에는 못 들어가요", "docker start web"),
       ("port-busy", P_CAFE, C("port-busy"), ["docker: Error response from daemon: … " + pbe_short], "8080을 다른 컨테이너가 쓰고 있어요", "docker compose down 또는 -p 8081:80")]
for k, (sc, pth, cm, ls_, why_, fix) in enumerate(xs_):
    t = Term([("$", pth, cm)] + [("e", l) for l in ls_], 96, y, size=23, w=1728, lh=1.5, tid=f"t-xr{k}", attrs=bi("rise", k + 1) if k else "")
    o.append(t.html())
    yy = t.y + t.h + 12
    o.append(p(f"position:absolute;left:96px;top:{yy}px;font-size:26px;font-weight:700;color:{INK}", e(why_), bi("fade", k + 1) if k else ""))
    o.append(pill(96 + tw(why_, 26, False) + 40, yy - 4, fix, GR, k + 1 if k else None, size=22))
    y = yy + 70
W("x-run", o, "첫 번째는 CMD에 main.py를 mian.py로 잘못 적고 build한 이미지를 run 했을 때예요. uv가 mian.py라는 파일을 못 찾아요. Dockerfile을 고치고 build부터 다시 해요. 두 번째는 stop으로 멈춘 컨테이너에 exec로 들어가려 할 때예요. is not running이 나오면 docker start로 다시 켜고 들어가요. 세 번째는 compose로 띄운 cafe-web-1이 8080을 쓰는 동안 docker run으로 8080을 또 쓰려 할 때예요. port is already allocated가 나오면 먼저 띄운 쪽을 끄거나 다른 포트를 써요. 이때 web 컨테이너는 만들어진 채 남으니 docker rm web으로 지워요. 첫 번째 출력은 cart-typo라는 이름으로 만든 이미지에서 옮겼고, 두 번째와 세 번째의 긴 ID와 설명은 …로 줄였어요." + REAL)

o = frame("x-vol", EB5, "-v에서 ./를 빼면 폴더가 아니라 새 볼륨이 생겨요", RED)
bt = D["bind-typo"]
t = Term([("$", P_CAFE, bt[0]["cmd"], {" site:": "xv-site"}), ("d", bt[0]["out"][0][:12] + "…"), ("o", ""), ("$", P_CAFE, bt[1]["cmd"])] + [("o", l) for l in bt[1]["out"]],
         96, 214, size=24, w=1728, lh=1.55)
t.band(len(t.rows) - 1, order=2, color="rgba(240,122,114,.16)")
o.append(t.html())
sx_ = t.sx(0, " site:") + t.sw(" ")
o.append(pen_box(1, round(sx_ - 8), round(t.top(0) - 2), round(t.sw("site:") + 16), round(t.lp + 4), RED))
o += tag(t, len(t.rows) - 1, "site라는 볼륨이 생겼어요", RED, 2)
o.append(browser(96, t.y + t.h + 40, 760, 1000 - (t.y + t.h + 40), "localhost:8080", page_nginx(0.8), "br-xv", attrs=bi("rise", 3)))
o.append(p(f"position:absolute;left:940px;top:{t.y + t.h + 60}px;width:884px;font-size:30px;font-weight:700;line-height:1.5;color:{INK}", "메뉴 대신 nginx 환영 페이지가 나와요.", bi("fade", 3)))
o.append(p(f"position:absolute;left:940px;top:{t.y + t.h + 120}px;width:884px;font-family:{MONO};font-size:30px;font-weight:700;line-height:1.5;color:{GR}", "-v ./site:/usr/share/nginx/html", bi("fade", 4)))
o.append(p(f"position:absolute;left:940px;top:{t.y + t.h + 180}px;width:884px;font-size:26px;line-height:1.5;color:{SUB}", "./를 붙여 다시 만들고, 잘못 생긴 볼륨은<br>docker volume rm site로 지워요.", bi("fade", 4)))
nn = R("compose-none")
t2 = Term([("$", P_HOME, C("compose-none")), ("e", nn[0])], 940, 1000 - 150, size=22, w=884, tid="t-xn", attrs=bi("rise", 5), h=150)
o.append(t2.html())
o += tag(t2, 1, "yaml 없는 폴더", RED, 5)
W("x-vol", o, "오류 메시지가 없는 함정이라 더 헷갈려요. -v site:처럼 ./ 없이 이름만 적으면 Docker는 site라는 볼륨을 새로 만들어 붙여요. 빈 볼륨이라 nginx의 기본 파일이 복사되고, 브라우저에는 메뉴 대신 환영 페이지가 나와요. docker volume ls로 보면 site라는 볼륨이 생겨 있어요. ./를 붙여 다시 만들고, 잘못 생긴 볼륨은 지워요. 오른쪽 아래는 compose.yaml이 없는 폴더에서 docker compose up을 쳤을 때예요. no configuration file provided가 나오면 cd cafe로 compose.yaml이 있는 폴더에 들어가요." + REAL)

# =====================================================================
# part 6: real tasks
# =====================================================================
o = frame("r-menu", EB6, "예제 1 · 카페 메뉴판을 compose로 띄우고 고쳐요", OR)
steps = [("cd cafe", "compose.yaml이 있는 폴더로"), ("docker compose up -d", "켜기"), ("site/index.html 고치고 저장", "VS Code에서"), ("브라우저 새로 고침", "localhost:8080"), ("docker compose down", "끄고 지우기")]
o.append(f'<div style="position:absolute;left:96px;top:214px;width:820px;display:flex;flex-direction:column;gap:14px">'
         + "".join(f'<div{bi("rise", i + 1)}{DIM("rm")} style="display:flex;flex-direction:row;align-items:center;gap:22px;height:118px;background:{CARD};border:2px solid {LINE};border-radius:16px;padding:0 28px">'
                   + p(f"width:48px;height:48px;flex:none;border-radius:24px;background:{OR};color:#FFFFFF;font-size:26px;font-weight:900;line-height:48px;text-align:center", str(i + 1))
                   + '<div style="display:flex;flex-direction:column;gap:4px">' + p(f"{'font-family:' + MONO + ';' if a_.isascii() else ''}font-size:30px;font-weight:700;color:{INK};white-space:nowrap", e(a_)) + p(f"font-size:22px;color:{SUB}", e(b_)) + '</div></div>' for i, (a_, b_) in enumerate(steps)) + '</div>')
ed, g = editor("rm-ed", "site/index.html", SITE2.strip().split("\n"), 1000, 214, 824, fs=24, color=GR, attrs=bi("rise", 3))
o.append(ed)
o.append(lband(3, g, 3, 1, GR, "rise"))
o.append(browser(1000, g["top"] + g["h"] + 30, 824, 1000 - (g["top"] + g["h"] + 30), "localhost:8080", page_menu(True, 4, 0.9), "br-rm", attrs=bi("rise", 4)))
o.append(cursor(4, 1150, round(g["top"] + g["h"] + 56)))
o.append(cursor_off(5))
W("r-menu", o, "2파트와 4파트를 합친 예제예요. 카페 메뉴판 페이지를 띄워 두고 메뉴를 고쳐 봐요. ~/cafe 폴더에서 docker compose up -d로 켜요. compose.yaml에 ./site 폴더 연결을 적어 뒀으니, VS Code에서 site/index.html에 메뉴 한 줄을 더하고 저장해요. 브라우저를 새로 고치면 바로 보여요. 컨테이너를 다시 만들 필요가 없어요. 다 쓰면 docker compose down으로 지워요. site 폴더는 내 폴더라 지워지지 않아요. 직접 메뉴를 하나 더 넣어 보세요.", ("p6", "실제 상황 예제"))

o = frame("r-friend", EB6, "예제 2 · 친구는 clone하고 build, run 두 줄이면 돼요", OR)
o.append(p(f"position:absolute;left:96px;top:222px;font-size:26px;font-weight:700;color:{GRAY}", "내가 할 일"))
mine = [("Dockerfile, .dockerignore 커밋", "git add 파일 뒤 git commit -m"), ("git push origin main", "02에서 배운 그대로")]
o.append(image_box(1260, 230, 564, "cart", ["CMD uv run main.py", "RUN uv sync", "COPY . .", "FROM astral/uv…"][::-1], attrs=bi("rise", 3), lh=50))
o.append(f'<div{STAGGER(1, 100)} style="position:absolute;left:96px;top:270px;width:1100px;display:flex;flex-direction:column;gap:14px">'
         + "".join(f'<div style="display:flex;flex-direction:column;gap:6px;background:{CARD};border:2px solid {LINE};border-left:8px solid {BL};border-radius:16px;padding:20px 28px">'
                   + p(f"{'font-family:' + MONO + ';' if a_.isascii() else ''}font-size:28px;font-weight:700;color:{INK};white-space:nowrap", e(a_)) + p(f"font-size:22px;color:{SUB}", e(b_)) + '</div>' for a_, b_ in mine) + '</div>')
o.append(p(f"position:absolute;left:96px;top:536px;font-size:26px;font-weight:700;color:{GRAY}", "친구가 할 일", bi("fade", 2)))
fr_ = R("rm-run")
t = Term([("$", "~", "git clone https://github.com/kim/shopping-cart.git"), ("$", "~", "cd shopping-cart"), ("$", P_CART, "docker build -t cart ."), ("d", "…"), ("$", P_CART, "docker run --rm cart")] + [("o", l) for l in fr_[:2]] + [("d", "…")],
         96, 582, size=21, w=1100, tid="t-fr", attrs=bi("rise", 2))
o.append(t.html())
o += tag(t, 2, "Docker만 있으면 돼요", OR, 3, at=t.x + 640)
o.append(p(f"position:absolute;left:1260px;top:640px;width:564px;font-size:30px;font-weight:700;line-height:1.5;color:{INK}", "친구 컴퓨터에 없어도 되는 것", bi("fade", 3)))
o.append(f'<div{STAGGER(3, 100)} style="position:absolute;left:1260px;top:710px;width:564px;display:flex;flex-direction:column;gap:18px">'
         + "".join(f'<div style="display:flex;flex-direction:row;align-items:center;gap:18px">{file_chip(n, GRAY, "#F0EFEA", size=28)}' + p(f"font-size:28px;color:{SUB}", e(d_)) + '</div>'
                   for n, d_ in [("python", "이미지 안에 있어요"), ("uv", "이미지 안에 있어요"), (".venv", "build할 때 만들어요")]) + '</div>')
W("r-friend", o, "Dockerfile과 .dockerignore도 코드처럼 커밋해서 GitHub에 올려요. 02에서 배운 대로 git add 파일, git commit -m, git push origin main 순서예요. 친구는 clone하고 폴더에 들어가 docker build와 docker run 두 줄만 치면 같은 영수증을 봐요. 친구 컴퓨터에 파이썬도 uv도 없어도 돼요. .venv는 .gitignore에 있어서 GitHub에 안 올라가고, build할 때 이미지 안에서 새로 만들어져요. 레포 주소는 예시라 kim 자리에 내 아이디를 적어요. clone 출력은 02와 같아서 빼고, build 출력은 앞에서 봤으니 줄였어요." + REAL)

o = frame("r-clean", EB6, "예제 3 · 다 쓴 컨테이너, 이미지, 볼륨을 정리해요", OR)
cl_ = D["clean"]
cv = D["clean-vol"]
lines = ([("$", P_CART, cl_[0]["cmd"])] + [("o", l) for l in cl_[0]["out"]] + [("$", P_CART, cl_[1]["cmd"])] + [("d", l) for l in cl_[1]["out"]]
         + [("$", P_CART, cl_[2]["cmd"])] + [("d", l) for l in cl_[2]["out"]] + [("$", P_CART, cv[1]["cmd"])] + [("d", l) for l in cv[1]["out"]])
t = Term(lines, 96, 214, size=18, w=1728, lh=1.6, tid="t-cl")
i_rm = 1 + len(cl_[0]["out"])
i_rmi = i_rm + 1 + len(cl_[1]["out"])
i_vol = i_rmi + 1 + len(cl_[2]["out"])
t.band(i_rm, i_rm, order=1)
t.band(i_rmi, i_rmi, order=2)
t.band(i_vol, i_vol, order=3)
o.append(t.html())
o += tag(t, i_rm, "1 컨테이너 (붕어빵)", BR, 1, at=t.x + 1220)
o += tag(t, i_rmi, "2 이미지 (틀)", MD, 2, at=t.x + 1220)
o += tag(t, i_vol, "3 볼륨 (보관함)", GR, 3, at=t.x + 1220)
o.append(caption("붕어빵부터 지우고 틀과 보관함을 지워요. 지우면 되돌릴 수 없으니 이름을 한 번 더 봐요.", t.y + t.h + 40, 4, size=28))
W("r-clean", o, "실습이 끝나면 쌓인 것을 정리해요. docker ps -a로 남은 컨테이너를 보고 NAMES 칸의 이름으로 지워요. 이름은 여러 개를 띄어 쓰면 한 번에 지워져요. 그다음 docker rmi cart로 이미지를 지워요. 마지막으로 2파트와 5파트에서 만든 볼륨 두 개를 docker volume rm으로 지워요. 컨테이너가 붙어 있는 이미지와 볼륨은 지울 수 없으니 붕어빵부터 지워요. 볼륨을 지우면 안의 파일도 같이 사라져서 되돌릴 수 없어요. 내 컴퓨터의 site 폴더와 shopping-cart 폴더는 그대로 남아요. 컨테이너 이름은 Docker가 아무렇게나 지어서 실습할 때마다 달라요." + REAL)

# =====================================================================
# wrap up
# =====================================================================
o = frame("trouble", "정리", "막히면 이렇게 풀어요", RED)
tr = [("Error ... container ... is not running", "멈춘 컨테이너에 exec 했어요", "docker start 이름"),
      ("ERROR: ... requires 1 argument", "docker build 끝의 점(.)이 없어요", "docker build -t cart ."),
      ("open Dockerfile: no such file or directory", "Dockerfile이 없는 폴더예요", "pwd 뒤 cd shopping-cart"),
      ("port is already allocated", "다른 컨테이너가 그 포트를 써요", "docker ps 뒤 stop, down"),
      ("코드를 고쳤는데 결과가 그대로예요", "이미지는 build할 때의 코드예요", "docker build 다시"),
      ("Git Bash에서 경로에 C:/Program Files/Git가 붙어요", "Git Bash가 /usr/...를 바꿨어요", "export MSYS_NO_PATHCONV=1")]
o.append(p(f"position:absolute;left:96px;top:214px;font-size:24px;font-weight:700;color:{GRAY}", "이런 글이 보이면"))
o.append(p(f"position:absolute;left:1240px;top:214px;font-size:24px;font-weight:700;color:{GRAY}", "이렇게 해요"))
for i, (q, a_, c_) in enumerate(tr):
    y = 262 + i * 118
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:1px;background:{LINE}"></div>')
    mono = q.isascii()
    ra = bi("rise", 1) + DELAY(i * 80)
    o.append(p(f"position:absolute;left:96px;top:{y + 16}px;width:1100px;{'font-family:' + MONO + ';font-size:25px;' if mono else 'font-size:28px;'}font-weight:700;color:{RED if mono else INK};white-space:nowrap", e(q), ra))
    o.append(p(f"position:absolute;left:96px;top:{y + 64}px;width:1100px;font-size:24px;color:{SUB}", e(a_), ra))
    o.append(p(f"position:absolute;left:1240px;top:{y + 38}px;width:584px;font-family:{MONO};font-size:25px;font-weight:700;color:{INK};white-space:nowrap", e(c_), ra))
o.append(f'<div style="position:absolute;left:96px;top:{262 + 6 * 118}px;width:1728px;height:1px;background:{LINE}"></div>')
W("trouble", o, "오늘 자주 만나는 일을 모았어요. 1번부터 4번은 5파트에서 실제로 본 오류예요. 5번은 오류 없이 결과만 옛날 그대로인 경우예요. 이미지는 build할 때의 코드를 담고 있으니 다시 build해요. 6번은 Windows Git Bash에서만 나요. -v 뒤의 /usr/share/nginx/html이 C:/Program Files/Git/usr/share/nginx/html처럼 바뀌어 들어가면 그 창에서 export MSYS_NO_PATHCONV=1을 치고 다시 해요. 6번 메시지는 이 자료를 만든 환경에서 실행할 수 없어서 원문을 옮기지 않았어요.", ("trouble", "정리"))

o = frame("cheatsheet", "정리", "한 장 요약", INK)
groups = [("안에 들어가기, 남기기", BL, [("docker exec -it 이름 bash", "실행 중인 컨테이너 안으로"), ("-v 볼륨이름:경로", "지워도 남는 보관함"), ("-v ./폴더:경로", "내 폴더 연결"), ("docker volume ls / rm", "볼륨 보기, 지우기")]),
          ("이미지 만들기", TEAL, [("FROM WORKDIR COPY RUN CMD", "Dockerfile 다섯 줄"), ("docker build -t 이름 .", "틀 굽기 (코드 고치면 다시)"), ("docker run --rm 이름", "찍고 끝나면 지우기"), (".dockerignore", ".venv  __pycache__  .git")]),
          ("compose", MAG, [("compose.yaml", "image, ports, volumes"), ("docker compose up -d", "켜기"), ("docker compose ps", "이 폴더 것만 보기"), ("docker compose down", "끄고 지우기")])]
for i, (t_, c, rows) in enumerate(groups):
    x = 96 + i * 600
    o.append(p(f"position:absolute;left:{x}px;top:220px;font-size:30px;font-weight:700;color:{c}", e(t_)))
    o.append(f'<div style="position:absolute;left:{x}px;top:270px;width:540px;height:3px;background:{c}"></div>')
    for j, (k, d) in enumerate(rows):
        y = 296 + j * 120
        o.append(p(f"position:absolute;left:{x}px;top:{y}px;width:560px;font-family:{MONO};font-size:25px;font-weight:700;color:{INK};white-space:nowrap", e(k)))
        o.append(p(f"position:absolute;left:{x}px;top:{y + 42}px;width:540px;font-size:23px;color:{SUB}", e(d)))
o.append(caption("이미지는 틀, 컨테이너는 붕어빵, 볼륨은 붕어빵 밖 보관함이에요.", 820, None, size=32))
o.append(caption("오늘 만든 cart 이미지를 친구 컴퓨터에서도 돌려 봐요.", 880, None, size=28, color=SUB))
W("cheatsheet", o, "오늘 쓴 명령을 세 묶음으로 모았어요. 실행 중인 컨테이너에는 exec로 들어가고, 지워도 남길 것은 볼륨에, 고치면서 볼 파일은 폴더 연결로 둬요. 내 프로그램은 Dockerfile 다섯 줄과 docker build로 이미지를 만들고, 코드를 고치면 build부터 다시 해요. 긴 run 명령은 compose.yaml에 적어 두고 up과 down으로 켜고 꺼요. 오늘 만든 cart 이미지를 친구 컴퓨터에서도 돌려 보세요.")

# =====================================================================
# toc
# =====================================================================
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
plist = [(BL, "컨테이너 안에 들어가기", "docker exec -it, 지우면 사라지는 변경", "e-run", "e-gone"),
         (GR, "볼륨으로 남기기", "-v 볼륨이름, -v ./폴더, docker volume ls", "v-what", "v-cmp"),
         (TEAL, "Dockerfile로 이미지 만들기", "FROM WORKDIR COPY RUN CMD, build, --rm, .dockerignore", "d-why", "d-ignore"),
         (MAG, "docker compose 맛보기", "compose.yaml, up -d, ps, down", "c-why", "c-up"),
         (RED, "자주 나는 오류", "build, run, exec, -v 오류", "x-build", "x-vol"),
         (OR, "실제 상황 예제", "메뉴판 고치기, 친구에게 건네기, 정리하기", "r-menu", "r-clean")]
o = frame("toc", "", "오늘의 순서", INK)
for i, (c, h, s_, a, b) in enumerate(plist):
    y = 210 + i * 116
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:1px;background:{LINE}"></div>')
    o.append(p(f"position:absolute;left:96px;top:{y + 18}px;width:80px;font-size:52px;font-weight:900;line-height:1.5;color:{c}", str(i + 1)))
    o.append(p(f"position:absolute;left:200px;top:{y + 18}px;font-size:36px;font-weight:700;color:{INK}", h))
    o.append(p(f"position:absolute;left:200px;top:{y + 70}px;font-family:{MONO};font-size:22px;font-weight:700;color:{SUB}", e(s_)))
    o.append(p(f"position:absolute;left:1524px;top:{y + 36}px;width:300px;text-align:right;font-size:30px;font-weight:700;color:{GRAY}", f"{page[a]}–{page[b]}쪽"))
o.append(f'<div style="position:absolute;left:96px;top:{210 + 6 * 116}px;width:1728px;height:1px;background:{LINE}"></div>')
o.append(p(f"position:absolute;left:96px;top:944px;font-size:26px;color:{SUB}", f"{page['why']}–{page['ready']}쪽은 들어가기, {page['trouble']}–{page['cheatsheet']}쪽은 막힐 때와 한 장 요약이에요."))
o = [x for x in o if 'id="eyebrow"' not in x]
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(o) + f"\n<aside>{e('여섯 파트로 나눴어요. 1, 2파트는 29의 nginx 컨테이너로 안에 들어가 보고 볼륨을 붙여요. 3파트는 28의 장바구니로 내 이미지를 만들어요. 4파트는 compose 맛보기예요. 5파트에서 자주 나는 오류를 모아 보고, 6파트에서 앞의 것을 섞은 예제 세 개를 풀어요.')}</aside>\n</section>\n")

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-12T00:00:00Z"}, "lists": "css", "title": "Docker 2 (내 프로그램을 이미지로 만들기)", "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
for w_ in WARN:
    print("WARN", w_)
print(len(ORDER), "slides")
