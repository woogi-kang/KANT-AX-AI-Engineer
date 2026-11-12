"""Generates every slide of the nginx deck (31) and slides/deck.json.

Story: after 29 and 30 every app got its own -p port. Part 1 lets nginx hand out the files of ./site and reads
its config (server, location, root). Part 2 puts two practice apps (traefik/whoami, which prints the request it
got) behind nginx with proxy_pass, all in one compose.yaml, so localhost, localhost/menu/ and localhost/order/
share port 80. Part 3 is the errors (502, 504, nginx -t, the trailing slash, port 80 busy), part 4 two real tasks.
Analogy: nginx = 카페 카운터 (takes every order at the door), app servers = 주방 (makes the answer).

Every terminal line comes from tools/demo.py (real Docker 29.9.2 and nginx 1.31.8, saved in tools/out.json).
Layout follows 30: the terminal or the diagram is the one big object, a small colored tag on a line says what it
means, a browser or editor straddles as a satellite.
Usage (in 31-nginx-basics): python3 tools/gen.py slides
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
from files import SITE, EVENT_HTML, CONF_FILES, CONF_MENU, CONF_BOTH, CONF_EVENT, COMPOSE, COMPOSE_EVENT  # noqa: E402  (the files demo.py wrote)

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
REAL = " 터미널 출력은 tools/demo.py로 실제 Docker와 nginx를 실행한 결과예요."


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




P_HOME, P_CAFE = "~", "~/cafe"
CW = "cafe-web-1"


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


# ---------- syntax colors for the two config files ----------
KW = {"server": NG, "location": NG, "listen": BL, "root": BL, "index": BL, "proxy_pass": MAG}


def conf_html(line, marks=None):
    """one line of default.conf with nginx's words colored; marks wraps substrings in spans (id or style)"""
    s = e(line)
    m = re.match(r"^(\s*)([a-z_]+)(.*)$", s)
    if m and m.group(2) in KW:
        s = f'{m.group(1)}<span style="color:{KW[m.group(2)]};font-weight:700">{m.group(2)}</span>{m.group(3)}'
    for k, v in (marks or {}).items():
        s = s.replace(e(k), f'<span {v}>{e(k)}</span>', 1)
    return s if s else ""


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


# ---------- pages the browser shows ----------
def page_home(scale=1.0):
    s = scale
    return (p(f"font-family:Tahoma, Verdana, Arial, sans-serif;font-size:{38 * s:.0f}px;font-weight:700;line-height:1.2;color:#111111", "KANT 카페")
            + p(f"font-size:{24 * s:.0f}px;line-height:1.4;color:#1A0DAB;text-decoration:underline", "메뉴 보기")
            + p(f"font-size:{24 * s:.0f}px;line-height:1.4;color:#1A0DAB;text-decoration:underline", "주문하기"))


def page_text(lines, size=22, hl=None):
    """a text/plain answer (whoami): the browser shows it in a monospace font, line by line"""
    hl = hl or {}
    return "".join(p(f"font-family:{MONO};font-size:{size}px;line-height:1.45;white-space:pre;color:{INK};{hl.get(i, '')}", e(l) if l else "&#160;") for i, l in enumerate(lines))


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


EB1 = "1. nginx로 파일 내주기"
EB2 = "2. 리버스 프록시"
EB3 = "3. 자주 나는 오류"
EB4 = "4. 실제 상황 예제"
C1, C2, C3, C4 = NG, MAG, RED, OR

# =====================================================================
# cover
# =====================================================================
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px">',
       p("position:absolute;left:128px;top:300px;font-size:28px;font-weight:700;color:#7FD18B", "KANT AX/AI 엔지니어 트랙 · 31"),
       f'<h1{SLAM(1)} style="position:absolute;left:128px;top:360px;font-size:100px;font-weight:900;line-height:1.15;color:#F6F5F1">nginx 기초</h1>',
       p("position:absolute;left:128px;top:500px;font-size:52px;font-weight:700;line-height:1.3;color:#F6F5F1", "웹 서버와<br>리버스 프록시"),
       p("position:absolute;left:128px;top:680px;font-size:32px;line-height:1.5;color:#BFC6D4", "앱 여러 개를 80번 포트 하나로 묶어요")]
mc = RA("p-curl", 1)
t = Term([("$", P_CAFE, "curl localhost/menu/")] + [("o", l) for l in mc[:6]] + [("o", ""), ("$", P_CAFE, "curl localhost/order/")] + [("o", l) for l in RA("p-reload", 3)[:1]],
         1010, 300, size=28, w=1000, tid="cov-term", bleed=True)
cov.append(t.html())
cov.append(shine(2, "cov-term"))
W("cover", cov, "31 챕터는 nginx 기초예요. 29, 30에서는 컨테이너마다 -p로 포트를 하나씩 열었어요. 앱이 늘어나면 주소의 포트 번호도 같이 늘어나요. 오늘은 nginx를 문 앞에 두고 앱 여러 개를 80번 포트 하나로 묶어요. 오른쪽 화면처럼 포트 번호 없이 /menu/, /order/로 각 앱에 들어가는 게 오늘의 마지막 모습이에요." + REAL, ("intro", "들어가기"))

ORDER.append("toc")   # written last, after page numbers are known

# =====================================================================
# why
# =====================================================================
o = frame("why", "들어가기", "앱이 하나 늘 때마다 포트 번호도 하나 늘어요", INK)
ps = RA("why-ps")
t = Term([("$", P_CAFE, "docker ps")] + [("o", l) for l in ps], 96, 214, size=20, w=1728, lh=1.7, tid="t-why")
o.append(t.html())
pc = ps[0].index("PORTS")
x_ports = t.tx + tw(ps[0][:pc], 20)
o.append(pen_box(1, round(x_ports - 10), round(t.top(1) - 4), round(tw("0.0.0.0:8080->80/tcp", 20) + 20), round(4 * t.lp + 8), RED))
y0 = t.y + t.h + 70
o.append(p(f"position:absolute;left:96px;top:{y0}px;font-size:28px;font-weight:700;color:{GRAY}", "손님에게 알려 줄 주소", bi("fade", 2)))
rows = [("localhost:8080", "홈페이지 (nginx)"), ("localhost:8001", "메뉴 앱"), ("localhost:8002", "주문 앱")]
o.append(f'<div{STAGGER(2, 100)} style="position:absolute;left:96px;top:{y0 + 56}px;width:820px;display:flex;flex-direction:column;gap:22px">'
         + "".join('<div style="display:flex;flex-direction:row;align-items:center;gap:22px">'
                   + f'<div style="height:72px;padding:0 22px;border-radius:30px;background:#FFFFFF;border:2px solid #D2CEC4;display:flex;flex-direction:row;align-items:center;gap:12px"><x-icon name="Globe" style="width:26px;height:26px;color:{GRAY}"></x-icon>'
                   + p(f"font-family:{MONO};font-size:34px;font-weight:700;color:{RED};white-space:nowrap", e(a_)) + '</div>'
                   + p(f"font-size:28px;color:{SUB};white-space:nowrap", e(b_)) + '</div>' for a_, b_ in rows) + '</div>')
o.append(line_arrow(960, y0 + 175, 1080, y0 + 175, NG, 3))
o.append(p(f"position:absolute;left:1120px;top:{y0}px;font-size:28px;font-weight:700;color:{GRAY}", "오늘 만들 주소", bi("fade", 3)))
o.append(f'<div{STAGGER(3, 100)} style="position:absolute;left:1120px;top:{y0 + 56}px;width:704px;display:flex;flex-direction:column;gap:22px">'
         + "".join(f'<div style="height:72px;align-self:flex-start;padding:0 22px;border-radius:30px;background:#FFFFFF;border:2px solid {NG};display:flex;flex-direction:row;align-items:center;gap:12px"><x-icon name="Globe" style="width:26px;height:26px;color:{GRAY}"></x-icon>'
                   + p(f"font-family:{MONO};font-size:34px;font-weight:700;color:{NG};white-space:nowrap", e(a_)) + '</div>' for a_ in ("localhost", "localhost/menu/", "localhost/order/")) + '</div>')
o.append(caption("포트 번호는 사라지고, 주소 뒤 경로로 앱을 골라요.", y0 + 56 + 3 * 72 + 2 * 22 + 44, 3, size=30, color=NG))
W("why", o, "앱이 하나 늘 때마다 포트 번호도 하나 늘어요. 29, 30에서 배운 대로 컨테이너 세 개를 띄웠어요. 홈페이지를 보여 주는 nginx와, 메뉴와 주문을 맡은 연습용 앱 두 개예요. 컨테이너마다 -p로 포트를 하나씩 열어야 해서 PORTS 칸에 8080, 8001, 8002가 생겼어요. 손님에게는 주소 세 개를 알려 줘야 하고, 앱이 늘면 포트도 계속 늘어요. 오늘은 오른쪽처럼 localhost 하나에 경로만 바꿔서 들어가게 만들어요. 연습용 앱은 2파트에서 자세히 봐요." + REAL)

# =====================================================================
# big picture
# =====================================================================
o = frame("big", "들어가기", "nginx가 문 앞에서 요청을 받아 뒤로 나눠 줘요", INK)
o.append(node(96, 456, 330, 170, "브라우저", "손님", BW, BWBG, "bg-br", icon="Globe"))
o.append(node(700, 386, 400, 310, "nginx", "카운터 · 80번 포트", NG, NGBG, "bg-ng", tsize=44, ssize=26))
o.append(line_arrow(440, 541, 686, 541, BW, None, pid="bg-p0"))
o.append(addr(446, 462, "localhost/…", BW, None, size=22))
o.append(p(f"position:absolute;left:700px;top:716px;width:400px;text-align:center;font-size:24px;color:{SUB}", "손님은 nginx 주소 하나만 알아요"))
BUSX = 1250
dests = [("bg-site", "site 폴더", "index.html 그대로", NG, NGBG, "/", 311, "Archive"),
         ("bg-menu", "menu 앱", "답을 만들어 줘요", AP, APBG, "/menu/", 541, "Code"),
         ("bg-order", "order 앱", "답을 만들어 줘요", AP, APBG, "/order/", 771, "Code")]
for k, (nid, t_, s_, c, bgc, path, cy, ic) in enumerate(dests):
    o.append(node(1460, cy - 80, 364, 160, t_, s_, c, bgc, nid, attrs=bi("rise", k + 1), icon=ic))
    d = f"M1114,541 L{BUSX},541 L{BUSX},{cy} L1444,{cy}" if cy != 541 else f"M1114,541 L1444,541"
    o.append(svg(f'<path id="bg-p{k + 1}" d="{d}" fill="none" stroke="{c}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>' + head_at(1445, cy, 0, c), k + 1))
    o.append(p(f"position:absolute;left:{BUSX + 22}px;top:{cy - 50}px;font-family:{MONO};font-size:28px;font-weight:700;color:{c};white-space:nowrap", e(path), bi("fade", k + 1) + DELAY(150)))
o.append(dot(1444, 541, AP, 4, "bg-p2", 1100))
o.append(caption("파일은 nginx가 바로 주고, 앱의 일은 뒤의 앱 서버에 넘겨요.", 900, 4, size=32))
W("big", o, "오늘 만들 모습을 한 장에 그렸어요. 카페로 생각하면 nginx는 문 앞의 카운터예요. 손님인 브라우저는 카운터 하나에만 주문해요. 카운터는 주문을 보고 나눠요. 그냥 /로 오면 site 폴더의 index.html을 그대로 꺼내 줘요. 진열대에서 바로 집어 주는 빵 같은 거예요. /menu/로 오면 menu 앱에, /order/로 오면 order 앱에 넘겨요. 앱은 주방처럼 그때그때 답을 만들어요. 이렇게 앞에서 대신 받아 뒤로 넘겨주는 것을 리버스 프록시라고 해요. 1파트에서 파일 내주기를, 2파트에서 리버스 프록시를 해요.")

# =====================================================================
# web server vs app server
# =====================================================================
o = frame("roles", "들어가기", "nginx는 있는 파일을 주고, 앱 서버는 답을 만들어 줘요", INK)
lanes = [("웹 서버", "nginx", NG, NGBG, "GET /index.html", "site/index.html", "Archive", "파일을 찾아서", "만든 그대로 보내요", 214),
         ("앱 서버", "FastAPI, whoami", AP, APBG, "GET /menu/", "코드 실행", "Code", "코드를 실행해서", "그때그때 답을 만들어요", 524)]
for k, (role, ex, c, bgc, req, mid, ic, v1, v2, y) in enumerate(lanes):
    a = bi("rise", 2) if k else ""
    o.append(f'<div{a} style="position:absolute;left:96px;top:{y}px;width:1728px;height:280px;background:{CARD};border:2px solid {LINE};border-radius:20px"></div>')
    y += 20
    o.append(p(f"position:absolute;left:136px;top:{y + 52}px;font-size:44px;font-weight:700;color:{c};white-space:nowrap", role, a))
    o.append(p(f"position:absolute;left:136px;top:{y + 120}px;font-size:28px;color:{SUB};white-space:nowrap", e(ex), a))
    o.append(addr(470, y + 88, req, BW, 2 if k else 1, size=24))
    o.append(line_arrow(820, y + 120, 960, y + 120, c, 2 if k else 1))
    o.append(node(980, y + 50, 330, 140, mid, None, c, bgc, attrs=bi("rise", 2 if k else 1), icon=ic, tsize=30))
    o.append(line_arrow(1324, y + 120, 1440, y + 120, c, 2 if k else 1))
    o.append(p(f"position:absolute;left:1470px;top:{y + 70}px;width:350px;font-size:30px;font-weight:700;line-height:1.5;color:{INK}", f"{v1}<br>{v2}", bi("fade", 2 if k else 1)))
o.append(p(f"position:absolute;left:96px;top:844px;width:1728px;box-sizing:border-box;padding:24px 32px;background:{APBG};border-radius:16px;border-left:8px solid {AP};font-size:28px;line-height:1.6;color:{INK}", "FastAPI 서버를 켜는 법은 아직 배우지 않았어요. 오늘은 받은 요청을 그대로 적어 돌려주는 연습용 앱 서버 <b style=\"color:" + AP + ";font-family:" + MONO + "\">traefik/whoami</b>를 대신 써요.", bi("fade", 3)))
W("roles", o, "서버라는 말이 두 가지로 쓰여요. nginx 같은 웹 서버는 요청받은 파일을 폴더에서 찾아 만든 그대로 보내요. 손대지 않으니 아주 빨라요. FastAPI로 만드는 앱 서버는 요청이 오면 파이썬 코드를 실행해서 그때그때 답을 만들어요. 로그인한 사람마다 다른 주문 목록을 보여 주는 일은 앱 서버가 해요. 보통은 두 가지를 같이 써요. nginx를 앞에 두고 파일은 nginx가 바로 주고, 앱의 일은 뒤의 앱 서버에 넘겨요. FastAPI 서버 켜기는 아직 배우지 않았으니, 오늘은 연습용 앱 서버인 whoami를 대신 써요.")

# =====================================================================
# ready
# =====================================================================
o = frame("ready", "들어가기", "30의 cafe 폴더에서 이어서 해요", INK)
t = Term([("$", P_HOME, "cd cafe"), ("$", P_CAFE, "mkdir conf"), ("$", P_CAFE, "docker pull traefik/whoami"), ("d", "…"), ("$", P_CAFE, "docker compose down")],
         96, 214, size=30, w=1000, lh=1.75, tid="t-ready")
o.append(t.html())
o += tag(t, 1, "nginx 설정 파일 자리", NG, 1)
o += tag(t, 2, "연습용 앱", AP, 2)
o += tag(t, 4, "30의 web이 켜져 있으면", GRAY, 3)
ed, g = editor("rd-ed", "site/index.html", SITE.strip().split("\n"), 96, t.y + t.h + 36, 1000, fs=32, color=NG, attrs=bi("rise", 4))
o.append(ed)
tree = [("~/cafe/", INK, 0), ("site/", NG, 1), ("index.html", INK, 2), ("conf/", NG, 1), ("default.conf", GRAY, 2), ("compose.yaml", GRAY, 1)]
o.append(f'<div{STAGGER(1, 80)} style="position:absolute;left:1180px;top:214px;width:644px;height:{g["top"] + g["h"] - 214:.0f}px;box-sizing:border-box;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:30px 34px;display:flex;flex-direction:column;gap:10px">'
         + "".join(p(f"margin-left:{d * 36}px;font-family:{MONO};font-size:30px;font-weight:700;line-height:1.5;color:{c};white-space:nowrap", e(n)) for n, c, d in tree)
         + p(f"margin-top:auto;padding-top:22px;border-top:2px solid {LINE};font-size:25px;line-height:1.6;color:{SUB}", "회색 파일은 1, 2파트에서 만들어요.<br>Windows Git Bash는 30처럼 새 창마다<br><span style=\"font-family:" + MONO + ";font-weight:700;color:" + INK + "\">export MSYS_NO_PATHCONV=1</span>을 먼저 쳐요.") + '</div>')
W("ready", o, "30에서 만든 ~/cafe 폴더를 그대로 써요. conf 폴더를 하나 더 만들어요. nginx 설정 파일을 둘 자리예요. 2파트에서 쓸 연습용 앱 이미지 traefik/whoami도 미리 받아요. 30의 compose로 띄운 web이 아직 켜져 있으면 docker compose down으로 먼저 꺼요. site/index.html은 오늘 홈페이지로 바꿔요. 메뉴 보기와 주문하기 링크가 있는 짧은 파일이에요. Windows Git Bash는 30처럼 새 창마다 export MSYS_NO_PATHCONV=1을 먼저 쳐요." + REAL)

# =====================================================================
# part 1: nginx hands out files
# =====================================================================
o = frame("w-run", EB1, "curl로 브라우저가 받는 글자를 터미널에서 봐요", C1)
wr = D["w-run"]
t = Term([("$", P_CAFE, wr[0]["cmd"]), ("d", wr[0]["out"][0][:12] + "…"), ("o", ""), ("$", P_CAFE, wr[1]["cmd"], {"curl": 'id="wr-curl"'})] + [("o", l) for l in RA("w-run", 1)],
         96, 214, size=26, w=1728, lh=1.55, tid="t-wr")
t.band(4, 7, order=2, color="rgba(127,209,139,.16)")
o.append(t.html())
o += tag(t, 3, "주소의 내용을 받아 화면에 찍어요", NG, 1, at=t.x + 700)
o.append(browser(1200, 640, 624, 380, "localhost:8080", page_home(0.95), "br-wr", attrs=SLIDE(3, 300, 0)))
o.append(p(f"position:absolute;left:96px;top:{t.y + t.h + 40}px;width:1040px;font-size:28px;line-height:1.6;color:{SUB}", "브라우저도 똑같은 글자를 받아요.<br>다만 HTML을 읽어서 제목과 링크로 그려 줘요.", bi("fade", 3)))
o.append(p(f"position:absolute;left:96px;top:{t.y + t.h + 170}px;width:1040px;font-size:24px;line-height:1.55;color:{GRAY}", "curl은 Mac 터미널과 Windows Git Bash에 들어 있어요.", bi("fade", 3)))
W("w-run", o, "curl로 브라우저가 받는 글자를 터미널에서 봐요. 30에서 배운 명령으로 nginx를 띄워요. ./site 폴더를 nginx가 파일을 찾는 폴더에 연결했어요. 이번에는 브라우저 대신 curl로 열어 봐요. curl 뒤에 주소를 적으면 그 주소에서 받은 내용을 터미널에 그대로 찍어요. 나온 글자는 site/index.html과 똑같아요. 브라우저도 이 글자를 받는데, HTML을 읽어서 제목과 링크로 그려 줄 뿐이에요. curl은 Mac 터미널과 Windows Git Bash에 이미 들어 있어요. 화면을 바꾸지 않고 결과를 보기 좋아서 오늘은 curl을 자주 써요." + REAL, ("p1", "nginx로 파일 내주기"))

o = frame("w-path", EB1, "주소 뒤의 경로가 폴더 속 파일 이름이에요", C1)
o += parts(96, 230, [("localhost:8080", BW, "nginx에게", None), ("/event.html", NG, "이 파일을 주세요", "wp-path")], size=52, order=None, sep=0, lw=380)
o.append(line_arrow(1020, 264, 1150, 264, NG, 1))
o.append(p(f"position:absolute;left:1180px;top:226px;font-family:{MONO};font-size:30px;font-weight:700;line-height:1.5;color:{INK};white-space:nowrap", '/usr/share/nginx/html<span style="color:' + NG + '">/event.html</span>', bi("fade", 1)))
o.append(p(f"position:absolute;left:1180px;top:280px;font-family:{MONO};font-size:30px;font-weight:700;line-height:1.5;color:{GRAY};white-space:nowrap", '= ./site<span style="color:' + NG + '">/event.html</span>', bi("fade", 1) + DELAY(200)))
wp, wp2 = D["w-path"], D["w-path2"]
t = Term([("$", P_CAFE, wp[1]["cmd"])] + [("o", l) for l in RA("w-path", 1)[:4]] + [("d", "…")], 96, 420, size=29, w=840, lh=1.6, tid="t-wp1", attrs=bi("rise", 2))
t.band(2, order=2, color="rgba(240,122,114,.2)")
o.append(t.html())
o.append(pill(96, t.y + t.h + 20, "site 폴더에 event.html이 없어요", RED, 2))
t2 = Term([("$", P_CAFE, wp2[0]["cmd"])] + [("o", l) for l in RA("w-path2", 0)] + [("$", P_CAFE, wp2[1]["cmd"])] + [("o", l) for l in RA("w-path2", 1)], 984, 420, size=29, w=840, lh=1.6, tid="t-wp2", attrs=bi("rise", 3))
t2.band(1, order=3, color="rgba(127,209,139,.2)")
t2.band(5, order=3, color="rgba(127,209,139,.2)")
o.append(t2.html())
o.append(pill(984, t2.y + t2.h + 20, "파일만 만들면 바로 나와요", NG, 3))
W("w-path", o, "주소 뒤의 경로가 폴더 속 파일 이름이에요. localhost:8080 뒤에 붙은 /event.html을 경로라고 해요. nginx는 경로를 보고 /usr/share/nginx/html 폴더에서 같은 이름의 파일을 찾아요. 그 폴더는 -v로 연결한 내 site 폴더예요. 아직 event.html이 없으니 nginx가 404 Not Found 페이지를 돌려줘요. 404는 찾는 파일이 없다는 번호예요. VS Code로 site 폴더에 event.html을 만들고 다시 curl을 치면 바로 나와요. nginx를 다시 켤 필요가 없어요. 경로 없이 localhost:8080만 치면 nginx는 index.html을 줘요. 왼쪽 404 출력은 앞의 네 줄만 옮겼어요." + REAL)

o = frame("w-logs", EB1, "docker logs에 받은 요청이 한 줄씩 남아요", C1)
lg = [l for l in RA("w-logs") if l.startswith("172.") and '"GET' in l]
t = Term([("$", P_CAFE, "docker logs web"), ("d", "…")] + [("o", l) for l in lg] + [("d", "…")], 96, 214, size=23, w=1728, lh=1.6, tid="t-wl")
t.band(5, order=1, color="rgba(240,122,114,.18)")
o.append(t.html())
one = lg[3]
ip_, rest = one.split(" - - ")
tm = rest[:rest.index("]") + 1]
req = rest[rest.index('"'):rest.index('"', rest.index('"') + 1) + 1]
code = rest.split('" ')[1].split()[0]
o += parts(96, t.y + t.h + 80, [(ip_, GRAY, "보낸 쪽", None), (tm[1:21], GRAY, "시각", None), (req, NG, "받은 요청", None), (code, RED, "결과 번호", None)], size=36, order=2, stagger=True, lab=28, lw=300, drop=40)
o.append(caption("200은 잘 줬다, 404는 그런 파일이 없다는 뜻이에요.", t.y + t.h + 80 + 47 + 40 + 10 + 90, 5, size=30))
W("w-logs", o, "29에서 배운 docker logs로 nginx 컨테이너의 기록을 봐요. 시작할 때 찍는 안내 줄 아래로, 받은 요청이 한 줄에 하나씩 남아 있어요. 한 줄을 나눠 읽으면 요청을 보낸 쪽 주소, 시각, 받은 요청, 결과 번호예요. 결과 번호 200은 잘 줬다, 404는 그런 파일이 없다는 뜻이에요. 앞 장에서 event.html을 만들기 전에 친 요청이 404로 남아 있어요. 앞으로 결과가 이상하면 먼저 이 기록을 봐요. 시작 안내 줄과 오류 줄은 …로 줄였어요." + REAL)

o = frame("w-conf", EB1, "nginx가 할 일은 설정 파일 default.conf에 적혀 있어요", C1)
cf = RA("w-conf")
t = Term([("$", P_CAFE, "docker exec web cat /etc/nginx/conf.d/default.conf")] + [("o", l) for l in cf[:10]] + [("d", "…")], 96, 214, size=28, w=1140, lh=1.7, tid="t-wc")
o.append(t.html())
o += tag(t, 2, "80번 포트에서 기다려요", BL, 1, at=t.x + 560)
o.append(pen_box(2, round(t.tx - 8), round(t.top(7) - 2), round(t.sw("        root   /usr/share/nginx/html;") + 36), round(t.lp * 4 + 4), NG))
o += leader(t.tx + t.sw("        root   /usr/share/nginx/html;") + 44, t.top(8) + t.lp / 2, 1290, NG, 2, "/로 시작하는 주소는", size=30, sub="이 폴더에서 찾아요")
o.append(f'<div{bi("rise", 1)} style="position:absolute;left:1290px;top:214px;width:534px;box-sizing:border-box;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:26px 30px">'
         + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{INK};white-space:nowrap", "docker exec 이름 명령")
         + p(f"margin-top:10px;font-size:26px;line-height:1.6;color:{SUB}", "컨테이너 안에서 명령 하나만 실행하고 돌아와요.") + '</div>')
W("w-conf", o, "nginx가 어느 포트에서 기다리고, 어느 폴더에서 파일을 찾을지는 설정 파일에 적혀 있어요. 컨테이너 안의 /etc/nginx/conf.d/default.conf예요. 30에서는 docker exec -it web bash로 안에 들어갔어요. 이번처럼 bash 대신 cat 같은 명령을 적으면 그 명령 하나만 안에서 실행하고 돌아와요. listen 80은 80번 포트에서 요청을 기다린다는 뜻이에요. -p 8080:80의 뒤쪽 80이 여기와 맞아요. location / 상자 안의 root가 파일을 찾는 폴더예요. 아래에는 #으로 시작하는 주석이 많아서 앞의 열 줄만 옮겼어요." + REAL)

o = frame("w-read", EB1, "server 상자 안에 location 상자가 들어 있어요", C1)
cl = CONF_FILES.rstrip("\n").split("\n")
ed, g = editor("wr-ed", "conf/default.conf", [conf_html(l) for l in cl], 96, 214, 1000, fs=38, color=NG)
o.append(ed)
gx0 = g["tx"]
GW = tw("        root /usr/share/nginx/html;", 38) + 60
o.append(f'<div{bi("fade", 1)} style="position:absolute;left:{gx0 - 20:.0f}px;top:{gtop(g, 0) - 6:.0f}px;width:{GW:.0f}px;height:{g["lh"] * 8 + 12:.0f}px;border:3px dashed {NG};border-radius:14px"></div>')
o.append(f'<div{bi("fade", 2)} style="position:absolute;left:{gx0 + tw("    ", 38) - 12:.0f}px;top:{gtop(g, 3) - 4:.0f}px;width:{tw("        root /usr/share/nginx/html;", 38) - tw("    ", 38) + 30:.0f}px;height:{g["lh"] * 4 + 8:.0f}px;border:3px dashed {BL};border-radius:12px"></div>')
labs = [(1, "80번 포트에서 기다려요", 1, NG), (3, "/로 시작하는 주소면", 2, BL), (4, "이 폴더에서 찾고", 3, BL), (5, "파일 이름이 없으면 index.html", 3, BL)]
for li, lab, od, c in labs:
    o += leader(gx0 - 20 + GW + 14, gcy(g, li), 1150, c, od, lab, size=30)
o.append(caption("{ }는 상자, 줄 끝의 ;는 한 줄이 끝났다는 표시예요.", 830, 4, size=32))
W("w-read", o, "기본 설정에서 주석과 꼭 필요하지 않은 줄을 빼면 이만큼 남아요. 오늘 쓸 내 설정 파일이에요. 중괄호는 상자예요. 28에서 들여쓰기를 상자 안의 상자로 읽었던 것처럼, server 상자 안에 location 상자가 들어 있어요. server 상자 하나가 웹사이트 하나예요. listen 80은 80번 포트에서 기다린다는 뜻이에요. location /는 /로 시작하는 주소, 곧 모든 주소에 이 상자의 규칙을 쓰겠다는 뜻이에요. root는 파일을 찾을 폴더, index는 파일 이름 없이 오면 줄 파일이에요. 줄 끝의 세미콜론을 빼먹으면 오류가 나요. 3파트에서 봐요.")

o = frame("w-mine", EB1, "내 설정 파일을 conf 폴더에 두고 -v로 연결해요", C1)
wm = D["w-mine"]
t = Term([("$", P_CAFE, wm[0]["cmd"])] + [("o", l) for l in RA("w-mine", 0)] + [("$", P_CAFE, wm[1]["cmd"], {"-v ./conf:/etc/nginx/conf.d": 'id="wm-v"'}), ("d", wm[1]["out"][0][:12] + "…"), ("$", P_CAFE, wm[2]["cmd"])] + [("o", l) for l in RA("w-mine", 2)],
         96, 214, size=24, w=1728, lh=1.5, tid="t-wm")
o.append(t.html())
vx = t.sx(3, "-v ./conf")
o.append(underline(1, round(vx), round(vx + t.sw("-v ./conf:/etc/nginx/conf.d")), round(t.top(3) + t.lp - 3), NG))
yb = t.y + t.h + 50
o.append(node(96, yb, 640, 160, "./conf/default.conf", "내 폴더 (VS Code로 고쳐요)", NG, NGBG, "wm-a", tsize=32, ssize=24))
o.append(line_arrow(750, yb + 80, 1010, yb + 80, NG, 2))
o.append(node(1024, yb, 800, 160, "/etc/nginx/conf.d/default.conf", "컨테이너 안 (nginx가 읽어요)", GRAY, "#EFEEEA", "wm-b", attrs=bi("rise", 2), tsize=32, ssize=24))
o.append(caption("curl 결과는 같아요. 이제 설정 파일을 내가 고칠 수 있어요.", yb + 200, 3, size=30))
W("w-mine", o, "내 설정 파일을 conf 폴더에 두고 -v로 연결해요. 앞 장의 내용으로 conf/default.conf 파일을 만들었어요. nginx를 띄울 때 -v를 하나 더 붙여서 conf 폴더를 nginx의 설정 폴더에 연결해요. 30에서 배운 -v ./폴더:경로 모양 그대로예요. 컨테이너 안의 기본 설정 대신 내 파일을 읽어요. curl 결과는 앞과 같아요. 달라진 건 이제 VS Code로 설정 파일을 고칠 수 있다는 거예요. 2파트에서 이 파일에 리버스 프록시 규칙을 더해요. 다 봤으면 docker stop web, docker rm web으로 지워요." + REAL)

# =====================================================================
# part 2: reverse proxy
# =====================================================================
o = frame("p-what", EB2, "리버스 프록시는 요청을 대신 받아 뒤로 넘겨줘요", C2)
YR = 490
o.append(node(96, YR - 115, 380, 230, "브라우저", "localhost/menu/", BW, BWBG, "pw-br", icon="Globe", mono_sub=True, tsize=36, ssize=26))
o.append(node(760, YR - 150, 400, 300, "nginx", "리버스 프록시", NG, NGBG, "pw-ng", tsize=48, ssize=28))
o.append(node(1444, YR - 115, 380, 230, "menu 앱", "주방", AP, APBG, "pw-app", icon="Code", tsize=36, ssize=26))
o.append(line_arrow(490, YR - 40, 746, YR - 40, BW, 1, pid="pw-a1"))
o.append(line_arrow(1174, YR - 40, 1430, YR - 40, MAG, 2, pid="pw-a2"))
o.append(line_arrow(1430, YR + 50, 1174, YR + 50, AP, 3, dash="2 12", pid="pw-a3"))
o.append(line_arrow(746, YR + 50, 490, YR + 50, AP, 4, dash="2 12", pid="pw-a4"))
o.append(dot(746, YR - 40, BW, 1, "pw-a1", 900))
o.append(dot(1430, YR - 40, MAG, 2, "pw-a2", 900))
o.append(dot(1174, YR + 50, AP, 3, "pw-a3", 900))
o.append(dot(490, YR + 50, AP, 4, "pw-a4", 900))
o.append(p(f"position:absolute;left:512px;top:{YR - 100}px;font-size:28px;font-weight:700;color:{BW}", "1 요청", bi("fade", 1)))
o.append(p(f"position:absolute;left:1196px;top:{YR - 100}px;font-size:28px;font-weight:700;color:{MAG}", "2 대신 전달", bi("fade", 2)))
o.append(p(f"position:absolute;left:1196px;top:{YR + 70}px;font-size:28px;font-weight:700;color:{AP}", "3 답", bi("fade", 3)))
o.append(p(f"position:absolute;left:512px;top:{YR + 70}px;font-size:28px;font-weight:700;color:{AP}", "4 답을 그대로", bi("fade", 4)))
o.append(f'<div style="position:absolute;left:96px;top:{YR + 230}px;width:1728px;height:1px;background:{LINE}"></div>')
o.append(p(f"position:absolute;left:96px;top:{YR + 266}px;width:1728px;font-size:34px;font-weight:700;line-height:1.5;color:{INK}", "브라우저는 nginx하고만 이야기해요. 뒤에 menu 앱이 있는지도 몰라요.", bi("fade", 5)))
o.append(p(f"position:absolute;left:96px;top:{YR + 340}px;width:1728px;font-size:28px;line-height:1.6;color:{SUB}", "프록시(proxy)는 대신해 주는 사람이라는 뜻이에요. 서버 앞에서 대신 받아 주니 리버스(거꾸로) 프록시라고 불러요.", bi("fade", 5)))
W("p-what", o, "리버스 프록시가 하는 일을 네 단계로 봐요. 1, 브라우저가 nginx에 localhost/menu/를 요청해요. 2, nginx는 직접 답하지 않고 뒤의 menu 앱에 같은 요청을 대신 보내요. 3, menu 앱이 답을 만들어 nginx에 돌려줘요. 4, nginx는 그 답을 그대로 브라우저에 건네요. 카페 손님이 카운터에 주문하면 카운터가 주방에 전하고, 나온 음식을 손님에게 건네는 것과 같아요. 손님은 주방이 어디 있는지 몰라도 돼요. 프록시는 대신해 주는 사람이라는 뜻이에요. 서버 쪽 앞에서 대신 받아 주니 리버스 프록시라고 해요.", ("p2", "리버스 프록시"))

o = frame("p-whoami", EB2, "연습용 앱 whoami는 받은 요청을 글자로 돌려줘요", C2)
wy = D["why"]
t = Term([("$", P_CAFE, wy[0]["cmd"], {"…--name menu": f'id="pw-nm" style="color:{AP}"'}), ("d", wy[0]["out"][0][:12] + "…"), ("$", P_CAFE, "curl localhost:8001")] + [("o", l) for l in RA("why-curl", 0)],
         96, 214, size=27, w=1270, lh=1.5, tid="t-pw")
t.band(3, order=1, color="rgba(79,184,194,.2)")
t.band(8, order=2, color="rgba(224,127,176,.18)")
t.band(9, order=3, color="rgba(242,196,109,.17)")
o.append(t.html())
o += tag(t, 3, "--name으로 붙인 이름", AP, 1, at=t.x + 560)
o += tag(t, 8, "받은 요청과 경로", MAG, 2, at=t.x + 560)
o += tag(t, 9, "요청에 적힌 주소", OR, 3, at=t.x + 560)
o.append(f'<div{bi("rise", 4)} style="position:absolute;left:1410px;top:214px;width:414px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:26px 28px;display:flex;flex-direction:column;gap:12px">'
         + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{AP};white-space:nowrap", "traefik/whoami")
         + p(f"font-size:25px;line-height:1.6;color:{SUB}", "리버스 프록시 프로그램 Traefik을 만든 Traefik Labs가 올린 연습용 이미지예요.")
         + p(f"font-size:25px;line-height:1.6;color:{SUB}", "인증 마크는 없지만 4천만 번 넘게 받았어요.") + '</div>')
o.append(caption("앱이 무엇을 받았는지 그대로 보여 줘서, nginx가 무엇을 넘겼는지 확인하기 좋아요.", t.y + t.h + 44, 4, size=30))
W("p-whoami", o, "FastAPI 앱 대신 쓸 연습용 앱 서버 whoami예요. 이미지 이름 뒤의 --name menu는 이 앱이 스스로를 menu라고 소개하게 하는 옵션이에요. docker run의 --name과 이름은 같지만, 이쪽은 이미지 뒤에 붙어서 whoami 프로그램에 전해져요. curl로 열면 받은 요청을 글자로 그대로 돌려줘요. Name은 붙인 이름이고, GET / HTTP/1.1은 경로 /를 달라는 요청이에요. Host는 요청에 적힌 주소예요. 29의 Docker Hub 마크 기준으로 보면 인증 마크는 없어요. 리버스 프록시 프로그램 Traefik을 만든 Traefik Labs가 올렸고, 4천만 번 넘게 받은 이미지예요." + REAL)

o = frame("p-conf", EB2, "location /menu/ 상자에 proxy_pass 한 줄을 써요", C2)
cm = CONF_MENU.rstrip("\n").split("\n")
mk = {"menu": f'id="pc-host" style="color:{AP};font-weight:700"'}
ed, g = editor("pc-ed", "conf/default.conf", [conf_html(l, mk if "proxy_pass" in l else None) for l in cm], 96, 214, 980, fs=32, color=NG)
o.append(ed)
o.append(lband(1, g, 8, 3, MAG, "fade"))
o += leader(gx(g, cm[8]) + 14, gcy(g, 8), 1130, MAG, 2, "/menu/로 시작하는 주소면", size=28)
o += leader(gx(g, cm[9]) + 14, gcy(g, 9), 1130, AP, 3, "menu라는 서비스로 넘겨요", size=28, sub="http:// 뒤는 주소, 끝의 / 는 3파트에서 봐요")
o.append(p(f"position:absolute;left:96px;top:{g['top'] + g['h'] + 40:.0f}px;width:1728px;font-size:28px;line-height:1.6;color:{SUB}", "위의 location / 상자는 그대로 둬요. nginx는 주소와 가장 길게 맞는 location을 골라요.", bi("fade", 4)))
W("p-conf", o, "1파트에서 만든 conf/default.conf에 location 상자를 하나 더 써요. location /menu/는 /menu/로 시작하는 주소에 이 상자의 규칙을 쓰겠다는 뜻이에요. 상자 안의 proxy_pass가 리버스 프록시 줄이에요. http:// 뒤에 적은 곳으로 요청을 넘겨요. menu는 다음 장의 compose.yaml에 적을 서비스 이름이에요. compose로 함께 띄운 컨테이너끼리는 서비스 이름으로 서로를 찾아요. localhost/menu/는 /로도 시작하고 /menu/로도 시작해요. nginx는 더 길게 맞는 /menu/ 상자를 골라요. 그래서 위의 location / 상자를 그대로 둬도 돼요. 끝의 슬래시 하나는 3파트 함정에서 봐요.")

o = frame("p-compose", EB2, "compose.yaml에 nginx와 앱 두 개를 같이 적어요", C2)
cy_ = COMPOSE.rstrip("\n").split("\n")
ylines = []
for i, l in enumerate(cy_):
    mk = {}
    if l.strip() in ("menu:", "order:"):
        mk = {l.strip()[:-1]: f'style="background:#E1F2F3;border-radius:6px"{MARK(4)}'}
    ylines.append(yaml_html(l, mk))
ed, g = editor("pcm-ed", "compose.yaml", ylines, 96, 214, 900, fs=26, color=MAG)
o.append(ed)
idx = {k: [i for i, l in enumerate(cy_) if l.strip().startswith(k)] for k in ("ports", "- ./conf", "depends_on", "command", "menu:")}
o.append(lband(1, g, idx["ports"][0], 2, NG, "fade"))
o += leader(gx(g, cy_[idx["ports"][0] + 1]) + 14, gcy(g, idx["ports"][0] + 1), 1060, NG, 1, "밖으로 여는 문은 nginx 하나", size=26)
o += leader(gx(g, cy_[idx["- ./conf"][0]]) + 14, gcy(g, idx["- ./conf"][0]), 1060, NG, 2, "1파트의 내 설정 폴더", size=26)
o.append(lband(3, g, idx["depends_on"][0], 3, OR, "fade"))
o += leader(gx(g, cy_[idx["depends_on"][0]]) + 14, gcy(g, idx["depends_on"][0]), 1060, OR, 3, "menu, order를 먼저 켜고 web을 켜요", size=26)
o += leader(gx(g, cy_[idx["command"][0]]) + 14, gcy(g, idx["command"][0]), 1060, AP, 4, "이미지 뒤에 붙이던 --name menu", size=26, sub="ports가 없어요. 밖에서는 못 들어와요")
o += leader(gx(g, cy_[idx["menu:"][0]]) + 14, gcy(g, idx["menu:"][0]), 1060, AP, 4, "서비스 이름 = proxy_pass의 menu", size=26)
W("p-compose", o, "compose.yaml에 nginx와 앱 두 개, 서비스 세 개를 적어요. 30에서는 서비스를 하나만 적었어요. web은 nginx예요. ports로 80번을 열고, volumes로 site 폴더와 conf 폴더를 연결해요. depends_on은 menu와 order를 먼저 켠 뒤에 web을 켜라는 뜻이에요. nginx는 켜질 때 proxy_pass에 적은 menu를 찾는데, 그때 menu가 없으면 켜지지 않아요. menu와 order는 whoami 이미지예요. command에는 docker run에서 이미지 뒤에 붙이던 --name menu를 적어요. 둘에는 ports가 없어요. 밖에서 바로 들어오는 문을 열지 않고 nginx를 거쳐서만 들어오게 해요. 서비스 이름 menu가 proxy_pass에 적은 menu와 같아야 해요.")

o = frame("p-up", EB2, "포트 번호 없이 localhost/menu/로 앱에 들어가요", C2)
up = RA("p-up")
t = Term([("$", P_CAFE, "docker compose up -d")] + [("o", l) for l in up] + [("o", ""), ("$", P_CAFE, "curl localhost/menu/", {"localhost/menu/": 'id="pu-url"'})] + [("o", l) for l in RA("p-curl", 1)],
         96, 214, size=22, w=1200, lh=1.5, tid="t-pu")
i0 = len(up) + 3
t.band(i0, order=2, color="rgba(79,184,194,.2)")
t.band(i0 + 5, order=3, color="rgba(224,127,176,.18)")
t.band(i0 + 6, order=3, color="rgba(242,196,109,.17)")
o.append(t.html())
o += tag(t, i0, "menu 앱이 답했어요", AP, 2, at=t.x + 520)
o += tag(t, i0 + 5, "/menu/는 떼고 / 로 받았어요", MAG, 3, at=t.x + 520)
o += tag(t, i0 + 6, "nginx가 보낸 요청", OR, 3, at=t.x + 520)
ux = t.sx(len(up) + 2, "localhost/menu/")
o.append(underline(1, round(ux), round(ux + t.sw("localhost/menu/")), round(t.top(len(up) + 2) + t.lp - 3), NG))
o.append(browser(1360, 214, 464, 560, "localhost/menu/", page_text(RA("p-curl", 1)[:6], 19), "br-pu", attrs=SLIDE(4, 300, 0), pad="26px 30px"))
o.append(p(f"position:absolute;left:1360px;top:800px;width:464px;font-size:24px;line-height:1.55;color:{SUB}", "브라우저 주소창에 쳐도 같은 글자가 나와요.", bi("fade", 4)))
W("p-up", o, "포트 번호 없이 localhost/menu/로 menu 앱에 들어가요. ~/cafe 폴더에서 docker compose up -d를 쳐요. depends_on에 적은 대로 menu와 order가 먼저 켜지고 web이 켜져요. 이제 포트 번호 없이 curl localhost/menu/를 쳐요. 주소에 포트를 안 적으면 80번으로 가요. 80번에서 기다리던 nginx가 /menu/ 상자를 보고 menu 앱에 넘겼어요. 답에 Name: menu가 찍혀 있어요. 앱이 받은 요청은 GET /예요. proxy_pass 끝에 /를 붙여서 nginx가 앞의 /menu/를 떼고 넘겼어요. Host가 menu인 것도 nginx가 보낸 요청이라서예요. 브라우저 주소창에 localhost/menu/를 쳐도 같은 글자가 나와요." + REAL)

o = frame("p-reload", EB2, "설정을 고치면 nginx -t로 검사하고 reload로 다시 읽혀요", C2)
cb = CONF_BOTH.rstrip("\n").split("\n")
s0 = cb.index("    location /order/ {")
snip = cb[s0 - 4:s0 + 3]
ed, g = editor("pr-ed", "conf/default.conf", [conf_html(l) if i < 4 else f'<span style="background:#FBE9F1"{MARK(1)}>{conf_html(l)}</span>' for i, l in enumerate(snip)], 96, 214, 720, fs=28, color=NG, nums=False)
o.append(ed)
o.append(p(f"position:absolute;left:96px;top:{g['top'] + g['h'] + 18:.0f}px;font-size:24px;color:{SUB}", "/order/ 상자를 더하고 저장했어요", bi("fade", 1)))
pr = D["p-reload"]
rows = [("$", P_CAFE, pr[0]["cmd"])] + [("o", l) for l in RA("p-reload", 0)[:4]] + [("d", "…"),
        ("$", P_CAFE, pr[1]["cmd"])] + [("g", l) for l in RA("p-reload", 1)] + [
        ("$", P_CAFE, pr[2]["cmd"])] + [("d", l) for l in RA("p-reload", 2)] + [
        ("$", P_CAFE, pr[3]["cmd"])] + [("o", l) for l in RA("p-reload", 3)[:1]] + [("d", "…")]
t = Term(rows, 860, 214, size=22, w=964, lh=1.6, tid="t-pr")
t.band(2, order=2, color="rgba(240,122,114,.2)")
t.band(7, 8, order=3, color="rgba(127,209,139,.18)")
t.band(12, order=5, color="rgba(79,184,194,.2)")
o.append(t.html())
o += tag(t, 2, "저장만 하면 아직 몰라요", RED, 2)
o += tag(t, 12, "다시 읽은 뒤", AP, 5)
steps = [("1", "설정 파일 고치고 저장", NG), ("2", "docker exec cafe-web-1 nginx -t", GR), ("3", "docker exec cafe-web-1 nginx -s reload", MAG)]
o.append(f'<div style="position:absolute;left:96px;top:{g["top"] + g["h"] + 100:.0f}px;width:720px;display:flex;flex-direction:column;gap:22px">'
         + "".join(f'<div{bi("rise", [1, 3, 4][k])}{DIM("pr")} style="display:flex;flex-direction:row;align-items:center;gap:18px">'
                   + p(f"width:44px;height:44px;flex:none;border-radius:22px;background:{c};color:#FFFFFF;font-size:24px;font-weight:900;line-height:44px;text-align:center", n)
                   + p(f"{'font-family:' + MONO + ';font-size:22px;' if s.isascii() else 'font-size:26px;'}font-weight:700;color:{INK};white-space:nowrap", e(s)) + '</div>' for k, (n, s, c) in enumerate(steps)) + '</div>')
W("p-reload", o, "주문 앱도 붙여 봐요. 설정 파일에 /order/ 상자를 더하고 저장해요. 그런데 바로 curl을 치면 404가 나와요. nginx는 켜질 때 한 번 읽은 설정을 계속 쓰기 때문이에요. 먼저 nginx -t로 설정 파일에 틀린 곳이 없는지 검사해요. syntax is ok와 test is successful이 나오면 통과예요. 그다음 nginx -s reload로 설정을 다시 읽게 해요. 컨테이너를 끄지 않아서 다른 손님의 요청은 끊기지 않아요. 둘 다 1파트에서 본 docker exec로 컨테이너 안에서 실행해요. cafe-web-1은 compose가 지은 web 컨테이너 이름이에요. 이제 curl을 치면 order 앱이 답해요. 404 출력은 앞의 네 줄, 마지막 답은 첫 줄만 옮겼어요." + REAL)

o = frame("p-closed", EB2, "밖으로 열린 문은 nginx의 80번 하나예요", C2)
pp = RA("p-ps")
t = Term([("$", P_CAFE, "docker compose ps")] + [("o", l) for l in pp] + [("o", ""), ("$", P_CAFE, "curl localhost:8001")] + [("e", l) for l in RA("p-closed")],
         96, 214, size=22, w=1728, lh=1.6, tid="t-pc")
o.append(t.html())
pc = pp[0].index("PORTS")
xp = t.tx + tw(pp[0][:pc], 22)
o.append(pen_box(1, round(xp - 8), round(t.top(2) - 3), round(tw("80/tcp", 22) + 16), round(2 * t.lp + 6), AP))
o.append(pen_box(2, round(xp - 8), round(t.top(4) - 3), round(tw("0.0.0.0:80->80/tcp", 22) + 16), round(t.lp + 6), NG))
o.append(underline(3, round(t.tx), round(t.end(7)), round(t.top(7) + t.lp - 3), RED))
yb = t.y + t.h + 50
o.append(node(96, yb, 560, 190, "80/tcp", "컨테이너 안에서만 열려 있어요", AP, APBG, tsize=40, ssize=26, attrs=bi("rise", 1)))
o.append(node(700, yb, 560, 190, "0.0.0.0:80->80/tcp", "내 컴퓨터의 80번과 이어져요", NG, NGBG, tsize=36, ssize=26, attrs=bi("rise", 2)))
o.append(p(f"position:absolute;left:1310px;top:{yb + 30}px;width:514px;font-size:32px;font-weight:700;line-height:1.6;color:{INK}", "8001번 문은 없어요.<br><span style=\"font-weight:400;font-size:28px;color:" + SUB + "\">손님은 nginx를 거쳐서만 앱에 닿아요.</span>", bi("fade", 3)))
W("p-closed", o, "밖으로 열린 문은 nginx의 80번 하나예요. docker compose ps로 PORTS 칸을 봐요. menu와 order는 80/tcp라고만 나와요. 앱이 컨테이너 안에서 80번으로 기다린다는 뜻이고, 내 컴퓨터와는 이어져 있지 않아요. web만 0.0.0.0:80->80/tcp라서 내 컴퓨터의 80번과 이어져 있어요. 그래서 들어가기에서 쓴 localhost:8001은 이제 연결되지 않아요. 앱에 닿는 길이 nginx 하나뿐이라, 누가 어떤 요청을 보냈는지도 nginx 기록 한 곳에서 볼 수 있어요. curl 오류 문장은 curl 버전에 따라 조금 다를 수 있어요." + REAL)

o = frame("p-one80", EB2, "주소 세 개가 localhost 하나로 모였어요", C2)
before = [("localhost:8080", "홈페이지"), ("localhost:8001", "메뉴"), ("localhost:8002", "주문")]
after = [("localhost", "/  site 폴더"), ("localhost/menu/", "/menu/  menu 앱"), ("localhost/order/", "/order/  order 앱")]
o.append(p(f"position:absolute;left:96px;top:226px;font-size:30px;font-weight:700;color:{GRAY}", "29, 30처럼 컨테이너마다 -p"))
o.append(p(f"position:absolute;left:1040px;top:226px;font-size:30px;font-weight:700;color:{NG}", "nginx 하나만 -p 80:80", bi("fade", 1)))
for k, (a_, b_) in enumerate(before):
    y = 300 + k * 150
    o.append(addr(96, y, a_, GRAY, None, size=32, aid=f"o8-b{k}"))
    o.append(p(f"position:absolute;left:96px;top:{y + 76}px;font-size:24px;color:{SUB}", e(b_)))
for k, (a_, b_) in enumerate(after):
    y = 300 + k * 150
    o.append(f'<div data-build-in="fly order {k + 1}" data-from="o8-b{k}" style="position:absolute;left:1040px;top:{y}px">' + addr(0, 0, a_, NG, None, size=32) + '</div>')
    o.append(p(f"position:absolute;left:1040px;top:{y + 76}px;font-family:{MONO};font-size:24px;font-weight:700;color:{SUB};white-space:pre", e(b_), bi("fade", k + 1) + DELAY(200)))
o.append(line_arrow(760, 520, 960, 520, NG, 1))
o.append(f'<div{bi("rise", 4)} style="position:absolute;left:96px;top:790px;width:1728px;background:{CARD};border:2px solid {LINE};border-left:8px solid {BL};border-radius:16px;padding:24px 32px">'
         + p(f"font-size:28px;font-weight:700;color:{INK};line-height:1.5", "주소에 포트를 안 적으면 웹은 80번이 기본이에요.")
         + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{SUB};line-height:1.6", "localhost = localhost:80") + '</div>')
W("p-one80", o, "주소 세 개가 localhost 하나로 모였어요. 들어가기에서 본 주소와 비교해 봐요. 컨테이너마다 -p로 문을 열 때는 포트 번호로 앱을 골랐어요. 이제는 nginx 하나만 80번 문을 열고, 경로로 앱을 골라요. 웹 주소에 포트를 안 적으면 80번으로 가요. 그래서 localhost는 localhost:80과 같아요. 실제 서비스 주소에 포트 번호가 안 보이는 것도 이 덕분이에요. 앱이 몇 개로 늘어도 손님이 외울 주소는 하나예요.")

o = frame("cmp", EB2, "29, 30의 -p와 무엇이 달라졌는지 봐요", C2)
hdr = ["", "컨테이너마다 -p", "nginx 앞에 두기"]
rows = [("손님이 아는 주소", "localhost:8001, :8002 …", "localhost/menu/, /order/"),
        ("밖으로 연 포트", "앱 수만큼", "80번 하나"),
        ("앱을 늘리면", "새 포트를 열고 주소를 알려요", "location 상자 하나 더"),
        ("요청 기록", "앱마다 따로", "nginx 기록 한 곳"),
        ("파일 주기", "앱이 직접", "nginx가 바로")]
X = [96, 560, 1200]
Wd = [440, 620, 624]
o.append(f'<div style="position:absolute;left:{X[2] - 16}px;top:214px;width:{Wd[2] + 16}px;height:{80 + len(rows) * 120}px;background:{NGBG};border-radius:18px"{bi("fade", 1)}></div>')
for j, h_ in enumerate(hdr):
    o.append(p(f"position:absolute;left:{X[j]}px;top:234px;width:{Wd[j]}px;font-size:30px;font-weight:700;color:{[INK, GRAY, NG][j]};white-space:nowrap", e(h_)))
for i, r in enumerate(rows):
    y = 300 + i * 120
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:1px;background:{LINE}"></div>')
    for j, c_ in enumerate(r):
        mono = c_.isascii() or "localhost" in c_
        o.append(p(f"position:absolute;left:{X[j]}px;top:{y + 36}px;width:{Wd[j]}px;{'font-family:' + MONO + ';font-size:26px;' if mono and j else 'font-size:28px;'}font-weight:{700 if j != 1 else 400};color:{[INK, SUB, INK][j]};white-space:nowrap", e(c_), (bi("rise", 1) + DELAY(i * 80)) if j == 2 else ""))
o.append(f'<div style="position:absolute;left:96px;top:{300 + len(rows) * 120}px;width:1728px;height:1px;background:{LINE}"></div>')
o.append(caption("-p는 그대로 써요. nginx 컨테이너 하나에만 쓰는 게 달라요.", 960, 2, size=30))
W("cmp", o, "29, 30에서 배운 -p와 비교해 정리해요. 컨테이너마다 -p로 문을 열면 손님이 포트 번호를 알아야 하고, 앱을 늘릴 때마다 새 포트를 열어야 해요. nginx를 앞에 두면 밖으로 여는 문은 80번 하나예요. 앱을 늘릴 때는 location 상자 하나를 더 써요. 요청 기록도 nginx 한 곳에 모이고, 홈페이지 같은 파일은 nginx가 바로 줘요. -p를 버리는 게 아니라 nginx 컨테이너 하나에만 쓴다는 점이 달라요.")

# =====================================================================
# part 3: errors
# =====================================================================
def logline(scene, word):
    l = [x for x in RA(scene) if word in x][-1]
    l = l.split("[error] ")[1]
    l = re.sub(r"^\d+#\d+: \*\d+ ", "", l)
    return l.split(", client:")[0]


o = frame("x-gw", EB3, "502, 504는 nginx가 뒤의 앱에 닿지 못했다는 뜻이에요", C3)
cases = [("localhost를 적었어요", f"proxy_pass http://localhost:8001/;", "x-local", 0, "x-local-log", "connect() failed", "컨테이너 안의 localhost는 nginx 자신이에요", "proxy_pass http://menu/;"),
         ("menu 앱이 꺼져 있어요", "docker compose stop menu", "x-502", 1, "x-502-log", "timed out", "1분쯤 기다린 뒤에 나와요", "docker compose start menu")]
y = 214
for k, (head, why_cmd, sc, ki, lsc, word, why_, fix) in enumerate(cases):
    a = bi("rise", 2 * k + 1)
    o.append(p(f"position:absolute;left:96px;top:{y}px;font-size:30px;font-weight:700;color:{INK};white-space:nowrap", e(head), a))
    o.append(p(f"position:absolute;left:{96 + tw(head, 30, False) + 30:.0f}px;top:{y + 4}px;font-family:{MONO};font-size:24px;font-weight:700;line-height:1.5;color:{RED};white-space:nowrap", e(why_cmd), a))
    body = RA(sc, ki)
    tl = [l for l in body if "<title>" in l][0]
    t = Term([("$", P_CAFE, "curl localhost/menu/"), ("e", tl), ("d", "…"), ("$", P_CAFE, "docker compose logs web"), ("e", "web-1  | … " + logline(lsc, word))],
             96, y + 56, size=21, w=1728, lh=1.5, tid=f"t-xg{k}", attrs=a)
    t.band(1, order=2 * k + 2, color="rgba(240,122,114,.2)")
    t.band(4, order=2 * k + 2, color="rgba(240,122,114,.2)")
    o.append(t.html())
    yy = t.y + t.h + 14
    o.append(p(f"position:absolute;left:96px;top:{yy}px;font-size:26px;font-weight:700;color:{INK}", e(why_), bi("fade", 2 * k + 2)))
    o.append(pill(96 + tw(why_, 26, False) + 40, yy - 4, fix, GR, 2 * k + 2, size=22))
    y = yy + 90
W("x-gw", o, "5로 시작하는 Gateway 오류는 nginx는 살아 있는데 뒤의 앱에 닿지 못했다는 뜻이에요. 첫 번째는 proxy_pass에 localhost:8001을 적었을 때예요. 컨테이너 안에서 localhost는 nginx 컨테이너 자신이라, 그 안에는 8001번에서 기다리는 앱이 없어요. 기록에 connect() failed, Connection refused가 남아요. 서비스 이름 menu로 적어요. 두 번째는 menu 앱이 꺼져 있을 때예요. nginx가 1분쯤 기다리다 504 Gateway Time-out을 돌려주고, 기록에 upstream timed out이 남아요. docker compose start menu로 다시 켜요. docker compose logs web은 compose의 web 서비스 기록을 보여 줘요. 29의 docker logs와 같아요. HTML은 제목 줄, 기록은 마지막 오류 줄만 옮겼어요." + REAL, ("p3", "자주 나는 오류"))

o = frame("x-test", EB3, "nginx -t가 틀린 파일과 줄 번호를 알려 줘요", C3)
semi = RA("x-semi")
host = RA("x-host")
xt_lines = CONF_BOTH.rstrip("\n").split("\n")[7:12]
xt_lines[2] = xt_lines[2].rstrip(";")        # the broken line: no ; at the end
ed, g = editor("xt-ed", "conf/default.conf", [conf_html(l) for l in xt_lines], 96, 214, 780, fs=28, color=RED, start=8)
o.append(ed)
bad = xt_lines[2]
o.append(f'<div{bi("fade", 1)} style="position:absolute;left:{gx(g, bad) - 2:.0f}px;top:{gtop(g, 2) + 6:.0f}px;width:22px;height:{g["lh"] - 12:.0f}px;border-radius:5px;background:#F6D9D9;border:2px dashed {RED}"></div>')
o.append(p(f"position:absolute;left:{gx(g, bad) + 34:.0f}px;top:{gtop(g, 2) + 6:.0f}px;font-size:24px;font-weight:700;color:{RED};white-space:nowrap", "; 빠짐", bi("fade", 1)))
t = Term([("$", P_CAFE, "docker exec cafe-web-1 nginx -t")] + [("e", l) for l in semi[1:]], 940, 214, size=19, w=884, lh=1.5, tid="t-xt1", attrs=bi("rise", 1))
o.append(t.html())
o.append(underline(2, round(t.sx(1, "unexpected")), round(t.end(1)), round(t.top(1) + t.lp - 3), RED))
o.append(p(f"position:absolute;left:940px;top:{t.y + t.h + 16}px;width:884px;font-size:24px;line-height:1.55;color:{SUB}", "10번 줄에 ;가 없어서 11번 줄의 }에서 걸렸어요. 알려 준 줄과 바로 윗줄을 같이 봐요.", bi("fade", 2)))
y2 = 580
o.append(p(f"position:absolute;left:96px;top:{y2}px;font-size:30px;font-weight:700;color:{INK}", "서비스 이름 오타", bi("fade", 3)))
o.append(p(f"position:absolute;left:380px;top:{y2 + 4}px;font-family:{MONO};font-size:26px;font-weight:700;color:{INK};white-space:nowrap", 'proxy_pass http://<span style="color:' + RED + '">menuu</span>/;', bi("fade", 3)))
t2 = Term([("$", P_CAFE, "docker exec cafe-web-1 nginx -t")] + [("e", l) for l in host[1:]], 96, y2 + 64, size=25, w=1728, lh=1.6, tid="t-xt2", attrs=bi("rise", 3))
o.append(t2.html())
o.append(pen_box(4, round(t2.sx(1, "host not found") - 8), round(t2.top(1) + 1), round(t2.sw('host not found in upstream "menuu"') + 16), round(t2.lp - 2), RED))
o.append(p(f"position:absolute;left:96px;top:{t2.y + t2.h + 24}px;width:1728px;font-size:28px;line-height:1.55;color:{SUB}", "compose.yaml의 서비스 이름과 똑같이 적어요. test failed가 나오면 reload하지 말고 먼저 고쳐요.", bi("fade", 4)))
W("x-test", o, "설정 파일을 고친 뒤 reload 전에 nginx -t를 치는 이유예요. 첫 번째는 proxy_pass 줄 끝의 세미콜론을 빼먹었을 때예요. 오류는 11번 줄의 닫는 중괄호에서 났다고 나와요. 10번 줄이 끝나지 않은 채로 다음 줄까지 읽었기 때문이에요. 알려 준 줄과 바로 윗줄을 같이 봐요. 두 번째는 서비스 이름을 menuu로 잘못 적었을 때예요. host not found in upstream은 그런 이름의 서비스를 못 찾았다는 뜻이에요. compose.yaml의 서비스 이름과 똑같이 적어요. test failed가 나오면 reload하지 말고 먼저 고쳐요. 틀린 설정으로 nginx를 새로 켜면 nginx가 켜지지 않아요. 첫 줄의 시각이 찍힌 줄은 같은 내용이라 뺐어요." + REAL)

o = frame("x-slash", EB3, "proxy_pass 끝의 / 하나로 앱이 받는 경로가 달라져요", C3)
for k, (conf, sc, label, col) in enumerate([("proxy_pass http://menu;", "x-slash", "/ 없음: 경로를 그대로 넘겨요", RED), ("proxy_pass http://menu/;", "x-slash-ok", "/ 있음: /menu/를 떼고 넘겨요", NG)]):
    x = 96 + k * 884
    a = bi("rise", 2 * k + 1) if k else ""
    o.append(p(f"position:absolute;left:{x}px;top:226px;font-size:28px;font-weight:700;color:{col};white-space:nowrap", e(label), a))
    sl = '<span style="background:#E4F3EA;border-radius:4px;padding:0 2px">/</span>' if k else ''
    o.append(p(f"position:absolute;left:{x}px;top:286px;font-family:{MONO};font-size:34px;font-weight:700;color:{INK};white-space:nowrap", conf_html(conf.replace("menu/;", "menu").replace("menu;", "menu")) + sl + ";", a))
    out = RA(sc)
    t = Term([("$", P_CAFE, "curl localhost/menu/today")] + [("o", l) for l in out], x, 370, size=25, w=844, lh=1.55, tid=f"t-xs{k}", attrs=a)
    t.band(6, order=2 * k + 2, color=("rgba(240,122,114,.2)" if not k else "rgba(127,209,139,.2)"))
    o.append(t.html())
    o += tag(t, 6, "앱이 받은 경로", col, 2 * k + 2, gap=36)
o.append(caption("앱이 /today로 받아야 하면 끝에 /를 붙여요. 이 챕터에서는 붙이는 쪽으로 써요.", t.y + t.h + 44, 4, size=30))
W("x-slash", o, "proxy_pass 끝의 / 하나로 앱이 받는 경로가 달라져요. 오류 메시지가 없어서 헷갈리는 함정이에요. 두 설정은 http://menu 뒤의 슬래시 하나만 달라요. 끝에 슬래시가 없으면 nginx는 받은 경로 /menu/today를 그대로 앱에 넘겨요. 앱은 /menu/today라는 주소를 받아요. 끝에 슬래시가 있으면 location에 적은 /menu/를 떼고 남은 /today만 넘겨요. menu 앱 입장에서는 자기가 /menu/ 아래에 붙어 있는지 몰라도 돼요. 이 챕터에서는 붙이는 쪽으로 통일해요. 앱이 무엇을 받는지는 whoami의 GET 줄로 확인해요." + REAL)

o = frame("x-port", EB3, "80번을 다른 프로그램이 쓰고 있으면 8080:80으로 바꿔요", C3)
xp_ = rewrap(RA("x-port", 2), 132)
t = Term([("$", P_CAFE, "docker compose up -d")] + [("o" if l.startswith(" ") or l.startswith("[") else "e", l) for l in xp_], 96, 214, size=20, w=1728, lh=1.6, tid="t-xp")
o.append(t.html())
ei = [i for i, l in enumerate(xp_) if "Bind for" in l][0] + 1
o.append(underline(1, round(t.sx(ei, "Bind for")), round(t.end(ei)), round(t.top(ei) + t.lp - 3), RED))
yb = t.y + t.h + 50
xpl = COMPOSE.split("\n")[1:5]
xpl[3] = xpl[3].replace('"80:80"', '"8080:80"')
ed, g = editor("xp-ed", "compose.yaml", [yaml_html(l, {"8080": f'style="background:#E4F3EA;border-radius:4px"{MARK(2)}'} if "8080" in l else None) for l in xpl], 96, yb, 760, fs=34, color=MAG, nums=False)
o.append(ed)
o.append(addr(920, yb + 30, "localhost:8080/menu/", NG, 3, size=34))
o.append(p(f"position:absolute;left:920px;top:{yb + 130}px;width:904px;font-size:30px;font-weight:700;line-height:1.6;color:{INK}", "주소에 :8080만 붙이면 나머지는 그대로예요.", bi("fade", 3)))
o.append(p(f"position:absolute;left:920px;top:{yb + 200}px;width:904px;font-size:27px;line-height:1.6;color:{SUB}", "Windows의 IIS나 Mac의 다른 웹 서버가 80번을 쓰고 있을 수 있어요.", bi("fade", 3)))
W("x-port", o, "29에서 본 포트 겹침 오류가 80번에서도 나요. 다른 컨테이너나 프로그램이 이미 80번을 쓰고 있으면 web만 켜지지 못하고 port is already allocated가 나와요. menu와 order는 켜졌는데 web만 Starting에서 멈췄어요. 먼저 docker ps로 80번을 쓰는 컨테이너가 있는지 보고 꺼요. 컨테이너가 아닌 프로그램이 쓰고 있으면 compose.yaml의 ports를 8080:80으로 바꾸고 다시 docker compose up -d를 쳐요. 주소에 :8080만 붙이면 /menu/, /order/는 그대로예요. 이 출력은 80번에 nginx 컨테이너 하나를 먼저 띄워서 만들었어요. 긴 오류 줄은 화면 폭에 맞춰 줄만 바꿨어요." + REAL)

# =====================================================================
# part 4: real tasks
# =====================================================================
o = frame("r-site", EB4, "예제 1 · 카페 홈페이지와 앱 둘을 주소 하나로 열어요", C4)
wins = [("localhost", page_home(1.1), None), ("localhost/menu/", page_text(RA("r-site", 2)[:8] + ["…"], 21, {0: f"color:{AP};font-weight:700"}), None), ("localhost/order/", page_text(RA("r-site", 3)[:8] + ["…"], 21, {0: f"color:{AP};font-weight:700"}), None)]
for k, (u, inner, _) in enumerate(wins):
    x = 96 + k * 586
    o.append(browser(x, 214, 556, 590, u, inner, f"br-rs{k}", attrs=bi("rise", k + 1), pad="30px 34px"))
o.append(cursor(2, 96 + 34 + 70, 214 + 52 + 30 + 74))
o.append(cursor(3, 96 + 34 + 70, 214 + 52 + 30 + 114))
o.append(cursor_off(4))
o.append(p(f"position:absolute;left:96px;top:846px;width:1728px;font-size:30px;font-weight:700;line-height:1.6;color:{INK}", "홈의 링크 <span style=\"font-family:" + MONO + ";font-weight:700\">/menu/</span>와 <span style=\"font-family:" + MONO + ";font-weight:700\">/order/</span>도 같은 주소 안에 있어서 그대로 눌려요.", bi("fade", 4)))
o.append(p(f"position:absolute;left:96px;top:906px;width:1728px;font-size:27px;line-height:1.6;color:{SUB}", "앱이 다른 포트에 있었다면 링크마다 포트 번호를 적어야 했어요.", bi("fade", 4)))
W("r-site", o, "카페 홈페이지와 앱 둘을 주소 하나로 열어요. 1, 2파트를 합친 예제예요. ~/cafe 폴더에서 docker compose up -d로 셋을 켜고 브라우저로 localhost를 열어요. 홈페이지는 nginx가 site 폴더에서 바로 준 파일이에요. 메뉴 보기 링크를 누르면 /menu/로 가고, nginx가 menu 앱에 넘겨요. 주문하기는 order 앱이 답해요. index.html의 링크에는 /menu/, /order/처럼 경로만 적었어요. 모두 같은 주소 안에 있어서 그대로 눌려요. 앱마다 포트가 달랐다면 링크에 포트 번호를 하나하나 적어야 했어요. 브라우저 화면은 curl로 받은 실제 답을 그대로 그렸어요." + REAL, ("p4", "실제 상황 예제"))

o = frame("r-add", EB4, "예제 2 · 이벤트 앱을 붙여도 다른 주소는 그대로예요", C4)
ce = COMPOSE_EVENT.rstrip("\n").split("\n")
ys = ce[ce.index("  event:"):]
dep = [l for l in ce if l.strip() == "- event"][0]
ed, g = editor("ra-y", "compose.yaml", [yaml_html(l) for l in ["    depends_on:", "      ...", dep, "  ..."] + ys], 96, 214, 700, fs=28, color=MAG, nums=False)
o.append(ed)
o.append(lband(1, g, 2, 1, MAG, "fade"))
o.append(lband(1, g, 4, 3, MAG, "fade"))
cev = CONF_EVENT.rstrip("\n").split("\n")
s1 = cev.index("    location /event/ {")
ed2, g2 = editor("ra-c", "conf/default.conf", [conf_html(l) for l in cev[s1:s1 + 3]], 96, g["top"] + g["h"] + 30, 700, fs=28, color=NG, nums=False)
o.append(ed2)
o.append(lband(2, g2, 0, 3, NG, "fade"))
ra = D["r-add"]
rows = [("$", P_CAFE, ra[0]["cmd"])] + [("o", l) for l in RA("r-add", 0)] + [("$", P_CAFE, ra[1]["cmd"])] + [("g", l) for l in RA("r-add", 1)[1:]] + [("$", P_CAFE, ra[2]["cmd"]), ("d", "…"), ("$", P_CAFE, ra[3]["cmd"])] + [("o", l) for l in RA("r-add", 3)[:1]] + [("d", "…")]
t = Term(rows, 860, 214, size=18, w=964, lh=1.9, tid="t-ra")
ri = [i for i, r in enumerate(t.rows) if "Running" in r[1]]
t.band(ri[0], ri[-1], order=3, color="rgba(127,134,150,.25)")
st = [i for i, r in enumerate(t.rows) if "Started" in r[1]][0]
t.band(st, order=3, color="rgba(224,127,176,.18)")
t.band(len(t.rows) - 2, order=4, color="rgba(79,184,194,.2)")
o.append(t.html())
o += tag(t, ri[1], "그대로 돌아요", GRAY, 3, at=t.x + 450)
o += tag(t, st, "새로 켜요", MAG, 3, at=t.x + 450)
o += tag(t, len(t.rows) - 2, "새 주소", AP, 4)
o.append(p(f"position:absolute;left:860px;top:{t.y + t.h + 30}px;width:964px;font-size:28px;line-height:1.6;color:{SUB}", "다 쓰면 docker compose down으로 넷을 한 번에 지워요.", bi("fade", 5)))
W("r-add", o, "이번 주 이벤트를 보여 줄 앱 하나를 새로 붙여요. 할 일은 두 파일에 몇 줄씩이에요. compose.yaml에 event 서비스 세 줄과 depends_on 한 줄을 더하고, 설정 파일에 /event/ 상자를 더해요. docker compose up -d를 다시 치면 바뀐 event만 새로 켜고 나머지는 Running 그대로 둬요. nginx -t로 검사하고 reload로 다시 읽히면 localhost/event/가 열려요. 이 사이에 손님이 보던 /menu/, /order/는 끊기지 않았어요. 다 쓰면 docker compose down으로 넷을 한 번에 지워요. reload 출력과 답의 나머지 줄은 …로 줄였어요." + REAL)

# =====================================================================
# wrap-up
# =====================================================================
o = frame("trouble", "정리", "막히면 이렇게 풀어요", RED)
tr = [("404 Not Found", "그 경로에 파일이나 location이 없어요", "파일 이름, location, reload"),
      ("502 Bad Gateway", "nginx가 앱에 연결하지 못했어요", "proxy_pass에 서비스 이름"),
      ("504 Gateway Time-out", "앱이 꺼져 있거나 답이 없어요", "docker compose ps 뒤 start"),
      ("[emerg] unexpected \"}\"", "윗줄 끝에 ;가 빠졌어요", "알려 준 줄과 윗줄 보기"),
      ("host not found in upstream", "서비스 이름이 compose.yaml과 달라요", "이름을 똑같이"),
      ("port is already allocated", "80번을 다른 것이 쓰고 있어요", "\"8080:80\"으로 바꾸기")]
o.append(p(f"position:absolute;left:96px;top:214px;font-size:24px;font-weight:700;color:{GRAY}", "이런 글이 보이면"))
o.append(p(f"position:absolute;left:1240px;top:214px;font-size:24px;font-weight:700;color:{GRAY}", "이렇게 해요"))
for i, (q, a_, c_) in enumerate(tr):
    y = 262 + i * 118
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:1px;background:{LINE}"></div>')
    ra_ = bi("rise", 1) + DELAY(i * 80)
    o.append(p(f"position:absolute;left:96px;top:{y + 16}px;width:1100px;font-family:{MONO};font-size:25px;font-weight:700;color:{RED};white-space:nowrap", e(q), ra_))
    o.append(p(f"position:absolute;left:96px;top:{y + 64}px;width:1100px;font-size:24px;color:{SUB}", e(a_), ra_))
    o.append(p(f"position:absolute;left:1240px;top:{y + 38}px;width:584px;font-size:26px;font-weight:700;color:{INK};white-space:nowrap", e(c_), ra_))
o.append(f'<div style="position:absolute;left:96px;top:{262 + 6 * 118}px;width:1728px;height:1px;background:{LINE}"></div>')
W("trouble", o, "오늘 만난 오류를 모았어요. 404는 nginx까지는 왔는데 그 경로에 줄 것이 없다는 뜻이에요. 파일 이름이나 location을 보고, 설정을 고쳤다면 reload했는지 봐요. 5로 시작하는 502, 504는 nginx 뒤의 앱 문제예요. 설정 오류는 nginx -t가 줄 번호를 알려 줘요. 포트 겹침은 29에서 본 것과 같아요. 무엇이든 막히면 docker compose ps로 켜진 것을 보고, docker compose logs web으로 nginx 기록을 먼저 봐요.", ("trouble", "정리"))

o = frame("cheatsheet", "정리", "한 장 요약", INK)
groups = [("파일 내주기", NG, [("curl 주소", "받은 내용을 터미널에 찍기"), ("location / { root …; }", "경로를 폴더 속 파일로"), ("-v ./conf:/etc/nginx/conf.d", "내 설정 파일 연결"), ("docker logs web", "받은 요청 기록")]),
          ("리버스 프록시", MAG, [("proxy_pass http://menu/;", "서비스 이름으로 넘기기"), ("ports는 web 하나만", "앱은 nginx 뒤에"), ("depends_on", "앱 먼저, nginx 나중"), ("localhost = :80", "포트 없이 경로로 고르기")]),
          ("고친 뒤", OR, [("docker exec cafe-web-1 nginx -t", "설정 검사"), ("… nginx -s reload", "끄지 않고 다시 읽기"), ("docker compose logs web", "502, 504 원인 보기"), ("docker compose down", "다 쓰면 지우기")])]
for i, (t_, c, rows) in enumerate(groups):
    x = 96 + i * 600
    o.append(p(f"position:absolute;left:{x}px;top:220px;font-size:30px;font-weight:700;color:{c}", e(t_)))
    o.append(f'<div style="position:absolute;left:{x}px;top:270px;width:540px;height:3px;background:{c}"></div>')
    for j, (k, d_) in enumerate(rows):
        y = 296 + j * 120
        mono = all(ord(ch) < 0x1100 or ch == "…" for ch in k) or k.startswith("ports")
        o.append(p(f"position:absolute;left:{x}px;top:{y}px;width:560px;{'font-family:' + MONO + ';font-size:23px;' if mono else 'font-size:26px;'}font-weight:700;color:{INK};white-space:nowrap", e(k)))
        o.append(p(f"position:absolute;left:{x}px;top:{y + 42}px;width:540px;font-size:23px;color:{SUB}", e(d_)))
o.append(caption("nginx는 카운터, 앱 서버는 주방이에요. 손님은 카운터 하나만 알면 돼요.", 820, None, size=32))
o.append(caption("FastAPI 서버를 띄우는 법을 배우면, whoami 자리에 내 앱을 넣어요.", 880, None, size=28, color=SUB))
W("cheatsheet", o, "오늘 쓴 것을 세 묶음으로 모았어요. nginx는 location과 root로 폴더 속 파일을 바로 줘요. proxy_pass로 요청을 뒤의 앱에 넘기면 리버스 프록시가 돼요. 밖으로 여는 문은 nginx 하나만 두고 앱은 그 뒤에 둬요. 설정을 고치면 nginx -t로 검사하고 reload로 다시 읽혀요. 나중에 FastAPI 서버를 띄우는 법을 배우면, 오늘 whoami가 있던 자리에 내 앱 이미지를 넣으면 돼요.")

# =====================================================================
# toc
# =====================================================================
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
plist = [(NG, "nginx로 파일 내주기", "curl, 경로와 파일, docker logs, default.conf, server와 location", "w-run", "w-mine"),
         (MAG, "리버스 프록시", "whoami, proxy_pass, compose 세 서비스, nginx -t, reload, 80번 하나", "p-what", "cmp"),
         (RED, "자주 나는 오류", "502와 504, nginx -t 오류, 끝의 /, 80번 겹침", "x-gw", "x-port"),
         (OR, "실제 상황 예제", "카페 홈페이지와 앱 둘, 이벤트 앱 붙이기", "r-site", "r-add")]
o = frame("toc", "", "오늘의 순서", INK)
for i, (c, h, s_, a, b) in enumerate(plist):
    y = 230 + i * 160
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:1px;background:{LINE}"></div>')
    o.append(p(f"position:absolute;left:96px;top:{y + 30}px;width:80px;font-size:56px;font-weight:900;line-height:1.5;color:{c}", str(i + 1)))
    o.append(p(f"position:absolute;left:200px;top:{y + 30}px;font-size:40px;font-weight:700;color:{INK}", h))
    o.append(p(f"position:absolute;left:200px;top:{y + 92}px;font-size:24px;color:{SUB}", e(s_)))
    o.append(p(f"position:absolute;left:1524px;top:{y + 54}px;width:300px;text-align:right;font-size:30px;font-weight:700;color:{GRAY}", f"{page[a]}–{page[b]}쪽"))
o.append(f'<div style="position:absolute;left:96px;top:{230 + 4 * 160}px;width:1728px;height:1px;background:{LINE}"></div>')
o.append(p(f"position:absolute;left:96px;top:944px;font-size:26px;color:{SUB}", f"{page['why']}–{page['ready']}쪽은 들어가기, {page['trouble']}–{page['cheatsheet']}쪽은 막힐 때와 한 장 요약이에요."))
o = [x for x in o if 'id="eyebrow"' not in x]
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(o) + f"\n<aside>{e('네 파트로 나눴어요. 1파트에서 nginx가 폴더 속 파일을 내주는 모습과 설정 파일을 봐요. 2파트에서 nginx 뒤에 앱 둘을 두고 80번 포트 하나로 묶어요. 3파트에서 자주 나는 오류를 모아 보고, 4파트에서 앞의 것을 섞은 예제 두 개를 풀어요.')}</aside>\n</section>\n")

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-12T00:00:00Z"}, "lists": "css", "title": "nginx 기초 (웹 서버와 리버스 프록시)", "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
for w_ in WARN:
    print("WARN", w_)
print(len(ORDER), "slides")
