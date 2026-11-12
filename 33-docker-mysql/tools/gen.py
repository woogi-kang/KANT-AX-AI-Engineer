"""Generates every slide of the MySQL deck (33) and slides/deck.json.

Story: 32 (database basics) explained tables, rows, columns, types, the primary key and read four SQL statements.
This deck runs the MySQL server in a container instead of installing it. Part 1 runs it (-e environment variables,
docker logs, docker exec -it ... mysql). Part 2 types the SQL for real on the cafe orders table. Part 3 shows the
table vanish with the container, keeps it in a named volume on /var/lib/mysql and moves the long docker run into
compose.yaml. Part 4 is the errors, part 5 two real tasks. Analogy kept from 29/30: image = 붕어빵 틀, container = 붕어빵, volume = 붕어빵 밖 보관함; table = 엑셀 시트.

Every terminal line comes from tools/demo.py (real Docker 29.9.2 and MySQL 8.4, saved in tools/out.json).
Usage (in 33-docker-mysql): python3 tools/gen.py slides
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
REAL = " 터미널 출력은 tools/demo.py로 실제 Docker와 MySQL을 실행한 결과예요."


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
            wt = "font-weight:700;" if kind in ("$", "#", "m") else ""
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




P_HOME, P_DB = "~", "~/cafe-db"


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



# =====================================================================
# chapter 33 helpers
# =====================================================================
MY, MYBG = "#00758F", "#E2F1F5"      # MySQL server
VO, VOBG = "#B26A00", "#FBF0DF"      # volume (보관함) and the primary key
PY, PYBG = "#2459C9", "#E8EFFD"      # Python
C2, C3, CU, C4, C5, C6 = DK, MAG, TEAL, GR, RED, OR
EB2, EB3, EBU, EB4, EB5, EB6 = "1. MySQL 컨테이너 켜기", "2. 데이터베이스와 표 만들기", "3. 계정과 접속 방법", "4. 볼륨과 compose", "5. 자주 나는 오류", "6. 실제 상황 예제"
ORD = [("1", "latte", "2"), ("2", "americano", "1")]
ORD3 = ORD + [("3", "cake", "1")]
COLS = ["id", "menu", "qty"]
TYPES = ["INT", "VARCHAR(20)", "INT"]


def sheet(x, y, cols, rows, sid, widths, size=32, rh=74, hbg="#EEF0F3", hcol=INK, types=None, attrs="", name=None, ncol=None, pk=False, cell_attrs=None):
    """A database table drawn as a grid. Cells get ids sid-rIcJ, headers sid-hJ. Returns (html, geometry)."""
    cell_attrs = cell_attrs or {}
    W_ = sum(widths)
    th = rh + (34 if types else 0)
    top = y + (56 if name else 0)
    H = th + rh * len(rows)
    o = [f'<div id="{sid}"{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{W_}px;height:{H + 4 + (56 if name else 0)}px">']
    if name:
        o.append(p(f"position:absolute;left:0;top:0;height:44px;padding:0 18px;border-radius:10px 10px 0 0;background:{ncol or MY};font-family:{MONO};font-size:24px;font-weight:700;line-height:44px;color:#FFFFFF;white-space:nowrap", e(name)))
    oy = top - y
    o.append(f'<div style="position:absolute;left:0;top:{oy}px;width:{W_}px;height:{H + 4}px;box-sizing:border-box;background:{CARD};border:2px solid #CFCAC0;border-radius:{"0 14px 14px 14px" if name else "14px"};overflow:hidden">')
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
            + (p(f"position:absolute;left:0;top:{h / 2 + tsize * 0.55 + 6:.0f}px;width:{w}px;text-align:center;font-size:{ssize}px;line-height:1.35;color:{SUB};white-space:nowrap", sub) if sub else "")
            + '</div>')


def mysql_rows(lines):
    """terminal rows for a mysql session: 'mysql>' and '->' prompts get the prompt color"""
    out = []
    for l in lines:
        if l.startswith("mysql> "):
            out.append(("m", "mysql>", l[7:]))
        elif l.startswith("    -> "):
            out.append(("m", "    ->", l[7:]))
        elif l.startswith("ERROR"):
            out.append(("e", l))
        else:
            out.append(("o", l))
    return out


_old_row = Term._row


def _row(self, l):
    if l[0] == "m":
        pr, c = l[1], l[2]
        marks = l[-1] if isinstance(l[-1], dict) else {}
        return "m", f"{pr} {c}", f'<span style="color:#7FD1C8">{e(pr)}</span> ' + mark(c, marks), "#F2C46D"
    return _old_row(self, l)


Term._row = _row
_old_html = Term.html


def _html(self):
    h = _old_html(self)
    return h


def session(scene, k=0, keep=None):
    """the real lines of a mysql session without the long welcome text"""
    out = RA(scene, k, wrap=True)
    res, skip = [], False
    for l in out:
        if l.startswith("Reading table information") or l.startswith("You can turn off this feature"):
            continue
        if l.startswith("Welcome to the MySQL monitor"):
            skip = True
            continue
        if skip:
            if l.startswith("Type 'help;'"):
                skip = False
            continue
        res.append(l)
    while res and not res[0].strip():
        res.pop(0)
    # drop blank line right after the password prompt
    res = [l for i, l in enumerate(res) if not (l == "" and i > 0 and res[i - 1].startswith("Enter password"))]
    return res


# =====================================================================
# cover
# =====================================================================
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px">',
       p("position:absolute;left:128px;top:300px;font-size:28px;font-weight:700;color:#7FD1C8", "KANT AX/AI 엔지니어 트랙 · 33"),
       f'<h1{SLAM(1)} style="position:absolute;left:128px;top:360px;font-size:100px;font-weight:900;line-height:1.15;color:#F6F5F1">Docker 3</h1>',
       p("position:absolute;left:128px;top:500px;font-size:52px;font-weight:700;line-height:1.3;color:#F6F5F1", "MySQL 컨테이너로<br>데이터베이스 쓰기"),
       p("position:absolute;left:128px;top:680px;font-size:32px;line-height:1.5;color:#BFC6D4", "주문을 표에 담고, 지워도 남게 해요")]
ck = session("c-kept")
sel = ck[ck.index([l for l in ck if l.startswith("mysql> SELECT")][0]):]
sel = [l for l in sel if not l.startswith("mysql> exit") and l != "Bye"]
while sel and not sel[-1].strip():
    sel.pop()
t = Term(mysql_rows(sel), 1060, 330, size=30, w=760, tid="cov-term", lh=1.45)
cov.append(t.html())
cov.append(shine(2, "cov-term"))
W("cover", cov, "33 챕터는 Docker 3, MySQL 컨테이너로 데이터베이스 쓰기예요. 32에서 표, 타입, 기본 키를 그림으로 읽고 SQL을 맛봤어요. 오늘은 MySQL을 컨테이너로 켜고, 데이터베이스와 표를 직접 만들어 주문을 담아요. 오른쪽 화면처럼 컨테이너를 껐다 켜도 주문이 그대로 남는 게 오늘의 마지막 모습이에요." + REAL, ("intro", "들어가기"))

ORDER.append("toc")   # written last, after page numbers are known

# =====================================================================
# why
# =====================================================================
o = frame("why", "들어가기", "MySQL을 직접 설치하면 켜고 지우고 버전 맞추기가 번거로워요", INK)
cols = [("컴퓨터에 직접 설치", GRAY, ["설치 파일을 받아 설치 마법사를 넘겨요", "컴퓨터를 켤 때마다 뒤에서 늘 돌아요", "지우려면 프로그램과 데이터 폴더를 따로 찾아요", "프로젝트마다 다른 버전을 쓰기 어려워요"]),
        ("Docker 컨테이너", DK, ["docker run 한 줄로 켜요", "쓸 때만 켜고 docker stop으로 꺼요", "docker rm으로 깨끗이 지워요", "mysql:8.4처럼 태그로 버전을 골라요"])]
for k, (h, c, items) in enumerate(cols):
    x = 96 + k * 884
    a_ = bi("rise", 1) if k else ""
    o.append(f'<div{a_} style="position:absolute;left:{x}px;top:220px;width:844px;height:560px;box-sizing:border-box;background:{CARD if not k else "#EEF3FE"};border:{2 if not k else 3}px solid {LINE if not k else DK};border-radius:20px;padding:36px 40px;display:flex;flex-direction:column;gap:26px">'
             + p(f"font-size:36px;font-weight:700;color:{c}", h)
             + "".join(p(f"font-size:29px;line-height:1.5;color:{INK if k else SUB}", f'<span style="color:{c};font-weight:900">{i + 1}</span>&#160;&#160;' + e(it).replace("docker run", f'<b style="font-family:{MONO}">docker run</b>').replace("docker stop", f'<b style="font-family:{MONO}">docker stop</b>').replace("docker rm", f'<b style="font-family:{MONO}">docker rm</b>').replace("mysql:8.4", f'<b style="font-family:{MONO}">mysql:8.4</b>')) for i, it in enumerate(items)) + '</div>')
o.append(p(f"position:absolute;left:96px;top:830px;width:1728px;font-size:32px;font-weight:700;line-height:1.5;color:{INK}", "32에서 읽어 본 표와 SQL을 오늘은 컨테이너로 켠 MySQL에서 직접 쳐 봐요.", bi("fade", 2)))
o.append(p(f"position:absolute;left:96px;top:900px;width:1728px;font-size:28px;line-height:1.6;color:{SUB}", "실제 회사에서도 개발할 때는 데이터베이스를 컨테이너로 띄워 쓰는 경우가 많아요.", bi("fade", 2)))
W("why", o, "MySQL을 컴퓨터에 직접 설치하면 번거로운 일이 많아요. 설치 파일을 받아 마법사를 넘겨야 하고, 설치하고 나면 컴퓨터를 켤 때마다 뒤에서 늘 돌아요. 지울 때도 프로그램과 데이터 폴더를 따로 찾아 지워야 해요. 프로젝트마다 다른 버전이 필요하면 더 곤란해요. 29부터 써 온 Docker로 켜면 docker run 한 줄로 켜고, 쓸 때만 켜고, docker rm으로 깨끗이 지워요. 버전은 mysql:8.4처럼 태그로 골라요. 32에서 표와 SQL을 읽어 봤으니, 오늘은 컨테이너로 켠 MySQL에서 직접 쳐 봐요.")

# =====================================================================
# big picture
# =====================================================================
o = frame("big", "들어가기", "MySQL 서버는 컨테이너 안에서 돌고, 데이터는 볼륨에 남아요", INK)
o.append(node(96, 420, 340, 170, "내 터미널", "docker exec … mysql", BW, BWBG, "bg-t", icon="Code", mono_sub=True, ssize=20))
# container box
o.append(f'<div id="bg-c" style="position:absolute;left:640px;top:250px;width:760px;height:500px;box-sizing:border-box;background:#EEF3FE;border:3px solid {DK};border-radius:22px"></div>')
o.append(p(f"position:absolute;left:672px;top:272px;font-size:26px;font-weight:700;color:{DK}", "컨테이너 db  ·  이미지 mysql:8.4"))
o.append(node(700, 340, 640, 150, "MySQL 서버", "3306번 포트에서 기다려요", MY, MYBG, "bg-s", icon="Database", tsize=36, ssize=24))
o.append(sheet(780, 540, COLS, ORD, "bg-tab", [110, 240, 130], size=24, rh=48, name="cafe · orders", attrs=bi("rise", 2))[0])
o.append(line_arrow(450, 505, 686, 415, BW, 1, pid="bg-p1"))
o.append(p(f"position:absolute;left:452px;top:372px;font-size:26px;font-weight:700;color:{BW};white-space:nowrap", "SQL로 말해요", bi("fade", 1) + DELAY(150)))
o.append(dot(686, 415, BW, 1, "bg-p1", 900))
# volume
o.append(cyl(1520, 690, 304, 220, "cafe-data", "볼륨 · 붕어빵 밖 보관함", VO, VOBG, "bg-v", attrs=bi("rise", 3)))
o.append(svg(arrow_path("M1400,720 L1510,780", VO, 5, "2 12") + head_at(1512, 781, 29, VO), 3))
o.append(p(f"position:absolute;left:1430px;top:640px;font-family:{MONO};font-size:22px;font-weight:700;color:{VO};white-space:nowrap", "/var/lib/mysql", bi("fade", 3) + DELAY(150)))
# python app later
o.append(f'<div{bi("fade", 4)} style="position:absolute;left:1520px;top:330px;width:304px;height:170px;box-sizing:border-box;border:3px dashed {GRAY};border-radius:20px;display:flex;flex-direction:column;justify-content:center;padding:0 26px;gap:6px">'
         + p(f"font-size:30px;font-weight:700;color:{GRAY};white-space:nowrap", "파이썬 앱") + p(f"font-size:22px;color:{GRAY};white-space:nowrap", "다음에 이어 붙여요") + '</div>')
o.append(svg(arrow_path("M1506,415 L1354,415", GRAY, 4, "2 12") + head_at(1352, 415, 180, GRAY), 4))
o.append(caption("컨테이너를 지워도 표는 볼륨에 남아서, 다시 켜면 그대로예요.", 900, 5, size=32))
W("big", o, "오늘 만들 모습을 한 장에 그렸어요. 가운데 파란 상자가 mysql:8.4 이미지로 띄운 컨테이너예요. 그 안에서 MySQL 서버가 3306번 포트를 열고 기다려요. 서버 안에는 cafe라는 데이터베이스가 있고, 주문을 담는 orders 표가 들어 있어요. 내 터미널에서는 docker exec로 컨테이너 안의 mysql 프로그램을 열고, SQL이라는 말로 표에 넣고 꺼내요. 표가 실제로 저장되는 /var/lib/mysql 폴더는 30에서 배운 볼륨에 연결해요. 그러면 컨테이너를 지워도 표가 남아요. 나중에 파이썬 앱도 같은 서버에 붙이게 되는데, 그건 다음에 해요.")

# =====================================================================
# part 2: run MySQL in a container
# =====================================================================
RUNC = C("run")
RUNV = C("vrun")


def short_log(l):
    """docker logs lines are long; keep the part after the time stamp"""
    m = re.match(r"^\d{4}-\d\d-\d\d[T ][\d:.]+Z?(\+00:00)? (\d+ )?", l)
    return l[m.end():] if m else l


o = frame("r-pull", EB2, "Docker Hub의 공식 이미지 mysql:8.4를 받아요", C2)
pl = [l if not l.startswith("Digest") else l[:27] + "…" for l in RA("pull")]
t = Term([("$", P_HOME, "docker pull mysql:8.4")] + [("o", l) for l in pl] + [("o", ""), ("$", P_HOME, "docker images mysql")] + [("o", l) for l in RA("images")], 96, 214, size=26, w=1100, lh=1.6, tid="t-pull")
t.band(len(t.rows) - 1, order=2, color="rgba(242,196,109,.17)")
o.append(t.html())
o += tag(t, 0, "29에서 배운 pull", DK, 1)
o.append(f'<div{bi("rise", 1)} style="position:absolute;left:1260px;top:214px;width:564px;box-sizing:border-box;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:30px 32px;display:flex;flex-direction:column;gap:14px">'
         + '<div style="display:flex;flex-direction:row;align-items:center;gap:12px"><x-icon name="Verified" style="width:30px;height:30px;flex:none;color:' + GR + '"></x-icon>'
         + p(f"font-size:28px;font-weight:700;color:{GR};white-space:nowrap", "Docker Official Image") + '</div>'
         + p(f"font-size:25px;line-height:1.6;color:{SUB}", "29에서 본 공식 마크가 붙은 이미지예요. Docker Hub에서 mysql을 검색하면 맨 위에 나와요.") + '</div>')
o.append(f'<div{bi("rise", 2)} style="position:absolute;left:1260px;top:540px;width:564px;box-sizing:border-box;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:30px 32px;display:flex;flex-direction:column;gap:14px">'
         + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{DK};white-space:nowrap", "태그 8.4")
         + p(f"font-size:25px;line-height:1.6;color:{SUB}", "오래 고쳐 주는 LTS 버전이에요. latest 대신 버전을 적어 두면 다음 달에 받아도 같은 MySQL이 와요.") + '</div>')
o.append(caption("이미지가 1GB가 넘어서 처음 받을 때는 몇 분 걸릴 수 있어요.", t.y + t.h + 50, 3, size=30, width=1100))
W("r-pull", o, "Docker Hub의 공식 이미지 mysql:8.4를 받아요. 29에서 배운 docker pull이에요. mysql은 Docker Official Image 마크가 붙은 공식 이미지예요. 태그 8.4는 오래 고쳐 주는 LTS 버전이에요. latest로 받으면 새 버전이 나올 때마다 바뀌니, 수업에서는 8.4로 적어서 모두 같은 MySQL을 써요. docker images mysql로 받은 이미지를 확인해요. 1GB가 넘어서 처음에는 몇 분 걸릴 수 있어요." + REAL, ("p2", "MySQL 컨테이너 켜기"))

o = frame("r-run", EB2, "docker run 한 줄로 MySQL 서버를 켜요", C2)
t = Term([("$", P_HOME, RUNC)] + [("d", RA("run")[0][:12] + "…")], 96, 214, size=24, w=1728, lh=1.6, tid="t-run")
o.append(t.html())
pieces = [("docker run -d --name db", "29에서 배운 대로 뒤에서 켜고 이름은 db", DK, None),
          ("-e MYSQL_ROOT_PASSWORD=cafe1234", "관리자(root) 비밀번호 · 꼭 있어야 해요", MAG, "rr-e1"),
          ("-e MYSQL_DATABASE=cafe", "처음 켤 때 cafe 데이터베이스를 만들어요", MAG, "rr-e2"),
          ("-p 3306:3306", "MySQL이 기다리는 3306번 포트를 열어요", DK, None),
          ("mysql:8.4", "받아 둔 이미지", DK, None)]
y0 = t.y + t.h + 50
for k, (pc, lab, col, pid) in enumerate(pieces):
    y = y0 + k * 92
    i_ = f' id="{pid}"' if pid else ""
    o.append(p(f"position:absolute;left:96px;top:{y}px;font-family:{MONO};font-size:36px;font-weight:700;line-height:1.4;color:{col};white-space:nowrap", e(pc), i_ + bi("rise", 1 if k == 0 or k > 2 else 2) + DELAY(k * 80)))
    o += leader(96 + tw(pc, 36) + 24, y + 25, 1020, col, 1 if k == 0 or k > 2 else 2, e(lab), size=28)
o.append(caption("-e 두 개만 새로 나왔어요. 다음 장에서 봐요.", y0 + 5 * 92 + 20, 3, size=30, color=MAG))
W("r-run", o, "docker run 한 줄로 MySQL 서버를 켜요. 길어 보이지만 대부분 29에서 배운 옵션이에요. -d로 뒤에서 켜고, --name으로 이름을 db로 붙이고, -p로 포트를 열어요. MySQL은 3306번 포트에서 접속을 기다려서 3306:3306으로 열어요. 앱이 쓸 계정을 만드는 -e 두 개는 3파트에서 더해요. 오늘은 컨테이너 안에서 접속해서 -p가 없어도 되지만, 나중에 내 컴퓨터의 파이썬 앱이 붙을 때 필요해서 미리 열어 둬요. 새로 나온 건 -e 두 개예요. MYSQL_ROOT_PASSWORD는 관리자 root의 비밀번호, MYSQL_DATABASE는 처음 켤 때 만들 데이터베이스 이름이에요. 터미널에는 긴 컨테이너 ID 한 줄만 나와요." + REAL)

o = frame("r-env", EB2, "-e로 컨테이너에 설정값(환경 변수)을 건네요", C2)
ev = RA("env")
t = Term([("$", P_HOME, "docker exec db env")] + [("d", "PATH=…") if l.startswith("PATH") else ("o", l) for l in ev], 96, 214, size=28, w=900, lh=1.6, tid="t-env")
i1 = [i for i, r in enumerate(t.rows) if r[1].startswith("MYSQL_ROOT")][0]
t.band(i1, i1 + 1, order=1, color="rgba(224,127,176,.2)")
o.append(t.html())
o += tag(t, i1, "-e로 건넨 값", MAG, 1, gap=36)
RX = 1060
o.append(p(f"position:absolute;left:{RX}px;top:230px;width:764px;font-size:34px;font-weight:700;line-height:1.5;color:{INK}", "환경 변수는 프로그램이 켜질 때 읽는 <span style=\"color:" + MAG + "\">이름=값</span> 쪽지예요.", bi("fade", 2)))
o.append(p(f"position:absolute;left:{RX}px;top:360px;width:764px;font-size:28px;line-height:1.6;color:{SUB}", "MySQL 이미지는 처음 켜질 때 이 쪽지를 읽고 비밀번호와 데이터베이스를 만들어요. 쓸 수 있는 이름은 Docker Hub의 mysql 설명 페이지 Environment Variables에 적혀 있어요.", bi("fade", 2)))
o.append(f'<div{bi("rise", 3)} style="position:absolute;left:{RX}px;top:640px;width:764px;box-sizing:border-box;padding:24px 30px;background:#FBE9E7;border-left:8px solid {RED};border-radius:14px">'
         + p(f"font-size:27px;font-weight:700;line-height:1.5;color:{RED}", "cafe1234는 연습용이에요")
         + p(f"margin-top:8px;font-size:25px;line-height:1.6;color:{INK}", "실제 서비스는 긴 비밀번호를 쓰고, 비밀번호를 적은 파일은 GitHub에 올리지 않아요.") + '</div>')
W("r-env", o, "-e로 컨테이너에 설정값을 건네요. 이런 값을 환경 변수라고 불러요. 프로그램이 켜질 때 읽는 이름=값 쪽지라고 생각하면 돼요. 31에서 배운 docker exec 이름 명령으로 env를 실행하면 컨테이너 안의 환경 변수가 나와요. 우리가 -e로 건넨 두 줄이 그대로 들어 있어요. MySQL 이미지는 처음 켜질 때 이 값을 읽고 root 비밀번호를 정하고 cafe 데이터베이스를 만들어요. 어떤 이름을 쓸 수 있는지는 Docker Hub의 mysql 설명 페이지에 나와 있어요. cafe1234는 연습용이에요. 실제 서비스에서는 긴 비밀번호를 쓰고, 비밀번호를 적은 파일은 GitHub에 올리지 않아요." + REAL)

o = frame("r-logs", EB2, "logs에 port: 3306이 찍히면 다 켜진 거예요", C2)
lg = RA("logs")
pick = [l for l in lg if "[Entrypoint]" in l and any(k in l for k in ("Initializing database files", "Creating database cafe", "MySQL init process done"))]
rd = [l for l in lg if "mysqld: ready for connections" in l]
rows = [("$", P_HOME, "docker logs db"), ("d", "…")]
for l in pick:
    rows.append(("o", short_log(l)))
rows.append(("d", "…"))
for l in rd:
    s_ = short_log(l)
    rows.append(("o", "… " + s_[s_.index("ready for connections"):]))
t = Term(rows, 96, 214, size=22, w=1728, lh=1.7, tid="t-logs")
ri0 = len(rows) - 2
ri1 = len(rows) - 1
t.band(2, 4, order=1, color="rgba(127,134,150,.22)")
t.band(ri0, order=2, color="rgba(242,196,109,.17)")
t.band(ri1, order=3, color="rgba(127,209,139,.22)")
o.append(t.html())
o.append(underline(3, round(t.sx(ri1, "port: 3306")), round(t.sx(ri1, "port: 3306") + t.sw("port: 3306")), round(t.top(ri1) + t.lp - 4), GR))
yb = t.y + t.h + 50
steps = [("1", "데이터 파일을 만들어요", GRAY, 1), ("2", "잠깐 켠 임시 서버(port: 0)로 cafe를 만들어요", OR, 2), ("3", "진짜 서버를 3306번 포트로 켜요", GR, 3)]
for k, (n, s_, c, od) in enumerate(steps):
    o.append(p(f"position:absolute;left:96px;top:{yb + k * 62}px;font-size:30px;line-height:1.5;color:{INK};white-space:nowrap", f'<span style="color:{c};font-weight:900">{n}</span>&#160;&#160;{e(s_)}', bi("fade", od)))
o.append(p(f"position:absolute;left:1200px;top:{yb}px;width:624px;font-size:27px;line-height:1.6;color:{SUB}", "처음 켤 때는 10초쯤 걸려요. 그 전에 들어가면 오류가 나요. 5파트에서 봐요.", bi("fade", 3)))
W("r-logs", o, "docker logs에 port: 3306이 찍히면 다 켜진 거예요. MySQL은 처음 켤 때 할 일이 많아서 기록이 길어요. 크게 세 단계예요. 먼저 데이터 파일을 만들어요. 다음에 밖에서 못 들어오는 임시 서버를 잠깐 켜서 비밀번호를 정하고 cafe 데이터베이스를 만들어요. 그래서 ready for connections가 port: 0으로 한 번 나와요. 마지막으로 진짜 서버를 3306번 포트로 켜요. 마지막 줄에 port: 3306이 보이면 들어가도 돼요. 처음에는 10초쯤 걸려요. 줄이 길어서 앞의 시각과 중간 줄을 …로 줄였어요." + REAL)

o = frame("r-enter", EB2, "docker exec -it로 컨테이너 안의 mysql 프로그램에 들어가요", C2)
en = RA("enter", wrap=True)
wel = [l for l in en if l.startswith("Welcome") or l.startswith("Server version")]
rows = [("$", P_HOME, "docker exec -it db mysql -u root -p", {"mysql": f'id="re-m" style="color:{MY}"', "-u root": f'style="color:{MAG}"', "…-p": f'style="color:{MAG}"'}), ("o", "Enter password:"), ("o", wel[0]), ("d", "…"), ("o", wel[1]), ("d", "…"), ("m", "mysql>", "exit"), ("o", "Bye"), ("$", P_HOME, "")]
t = Term(rows, 96, 214, size=30, w=1240, lh=1.7, tid="t-enter")
o.append(t.html())
o += tag(t, 0, "root 사용자로, 비밀번호는 물어봐요", MAG, 1, gap=36, at=t.x + 760) if False else []
o += tag(t, 1, "cafe1234를 쳐요. 화면에 안 보여요", MAG, 1)
o.append(spot(2, t.x + 20, t.top(6) - 6, 300, t.lp + 12, pad=6, r=10))
o.append(spot_off(3))
o += tag(t, 6, "SQL을 칠 차례예요", MY, 3, at=t.x + 360)
o += tag(t, 8, "내 터미널로 돌아왔어요", DK, 4, at=t.x + 200)
RX = 1390
o.append(f'<div{bi("rise", 1)} style="position:absolute;left:{RX}px;top:214px;width:434px;box-sizing:border-box;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:26px 28px;display:flex;flex-direction:column;gap:12px">'
         + p(f"font-size:24px;font-weight:700;color:{GRAY}", "30에서는")
         + p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{INK};white-space:nowrap", "exec -it web <span style=\"color:" + DK + "\">bash</span>")
         + p(f"margin-top:10px;font-size:24px;font-weight:700;color:{GRAY}", "오늘은")
         + p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{INK};white-space:nowrap", "exec -it db <span style=\"color:" + MY + "\">mysql</span>")
         + p(f"margin-top:10px;font-size:23px;line-height:1.6;color:{SUB}", "bash 대신 MySQL에 접속하는 프로그램 mysql을 열어요.") + '</div>')
o.append(f'<div{bi("rise", 4)} style="position:absolute;left:{RX}px;top:640px;width:434px;box-sizing:border-box;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:26px 28px;display:flex;flex-direction:column;gap:10px">'
         + p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{MAG};white-space:nowrap", "-u root -p")
         + p(f"font-size:23px;line-height:1.6;color:{SUB}", "-u는 사용자 이름, -p는 비밀번호를 물어보라는 뜻이에요.") + '</div>')
W("r-enter", o, "docker exec -it로 컨테이너 안의 mysql 프로그램에 들어가요. 30에서는 bash를 열었는데, 이번에는 MySQL에 접속하는 프로그램 mysql을 열어요. -u root는 관리자 root로 들어간다는 뜻이고, -p는 비밀번호를 물어보라는 뜻이에요. Enter password:가 나오면 cafe1234를 치고 Enter를 눌러요. 비밀번호는 쳐도 화면에 아무것도 안 보이는 게 정상이에요. 환영 문구가 나오고 mysql> 표시가 보이면 SQL을 칠 차례예요. exit를 치면 Bye가 나오고 내 터미널로 돌아와요. 컨테이너는 계속 돌고 있어요. 환영 문구의 저작권 안내 줄은 …로 줄였어요." + REAL)

# =====================================================================
# part 3: four SQL statements
# =====================================================================
def sess_rows(scene, upto=None, k=0, marks=None):
    s_ = session(scene, k)
    s_ = [l for l in s_ if l not in ("Bye",) and not l.startswith("mysql> exit")]
    while s_ and not s_[-1].strip():
        s_.pop()
    rows = mysql_rows(s_)
    if marks:
        rows = [r + (marks,) if r[0] == "m" else r for r in rows]
    return rows


o = frame("s-show", EB3, "SHOW DATABASES;로 서버 안의 데이터베이스를 봐요", C3)
rows = [("$", P_HOME, "docker exec -it db mysql -u root -p"), ("o", "Enter password:"), ("d", "…")] + sess_rows("show")[1:]
t = Term(rows, 96, 214, size=28, w=1100, lh=1.55, tid="t-show")
ci = [i for i, r in enumerate(t.rows) if "| cafe" in r[1]][0]
t.band(ci, order=2, color="rgba(224,127,176,.22)")
t.band(ci + 1, ci + 4, order=3, color="rgba(127,134,150,.2)")
o.append(t.html())
o += tag(t, 3, "문장 끝에 ;", MAG, 1, at=t.x + 560)
o += tag(t, ci, "-e MYSQL_DATABASE로 만든 것", MAG, 2, at=t.x + 470)
o += tag(t, ci + 2, "MySQL이 스스로 쓰는 것", GRAY, 3, at=t.x + 470)
RX = 1260
o.append(f'<div{bi("rise", 4)} style="position:absolute;left:{RX}px;top:214px;width:564px;box-sizing:border-box;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:30px 32px;display:flex;flex-direction:column;gap:16px">'
         + p(f"font-size:28px;font-weight:700;color:{MAG}", "SQL 문장 쓰는 법")
         + "".join(p(f"font-size:25px;line-height:1.6;color:{INK}", s_) for s_ in ["끝에 <b style=\"font-family:" + MONO + "\">;</b>를 붙여야 실행돼요", "SQL 낱말은 대문자로 쓰는 게 약속이에요. 소문자도 돼요", "표와 데이터베이스 이름은 소문자로 써요"]) + '</div>')
W("s-show", o, "SQL 첫 문장이에요. SHOW DATABASES;는 서버 안의 데이터베이스 목록을 보여 줘요. 문장 끝의 세미콜론은 여기서 문장이 끝났다는 표시예요. 세미콜론을 쳐야 MySQL이 실행해요. 결과는 표 모양으로 나와요. cafe는 -e MYSQL_DATABASE로 만든 데이터베이스예요. 나머지 넷은 32에서 본 것처럼 MySQL이 스스로 쓰는 데이터베이스예요. SQL 낱말은 대문자로 쓰는 게 약속이에요. 소문자로 써도 돌아가지만, 대문자로 쓰면 내가 지은 이름과 구별이 잘 돼요." + REAL, ("p3", "데이터베이스와 표 만들기"))

o = frame("s-db", EB3, "CREATE DATABASE로 만들고 USE로 들어가요", C3)
rows = sess_rows("q-db")[1:]
t = Term(rows, 96, 214, size=22, w=880, lh=1.45, tid="t-db")
ic = [i for i, r in enumerate(t.rows) if r[1].startswith("mysql> CREATE")][0]
ish = [i for i, r in enumerate(t.rows) if "| shop" in r[1]][0]
iu = [i for i, r in enumerate(t.rows) if r[1] == "Database changed"][0]
ie = [i for i, r in enumerate(t.rows) if r[1].startswith("Empty set")][0]
t.band(ic, ic + 1, order=1, color="rgba(224,127,176,.2)")
t.band(ish, order=2, color="rgba(224,127,176,.22)")
o.append(t.html())
o += tag(t, ic + 1, "shop을 만들었어요", MAG, 1, at=t.x + 560)
o += tag(t, ish, "새로 생긴 shop", MAG, 2, at=t.x + 420)
o.append(underline(3, round(t.tx), round(t.tx + t.sw("Database changed")), round(t.top(iu) + t.lp - 3), MAG))
o += tag(t, iu, "이제 shop 안에서 쳐요", MAG, 3, at=t.x + 360)
o += tag(t, ie, "아직 표가 없어요", GRAY, 4, at=t.x + 360)
# right: server > databases picture
RX, RW = 1060, 764
o.append(f'<div{bi("rise", 1)} style="position:absolute;left:{RX}px;top:214px;width:{RW}px;height:500px;box-sizing:border-box;border:3px solid {MY};border-radius:22px;background:{MYBG}">'
         + p(f"position:absolute;left:28px;top:20px;font-size:28px;font-weight:700;color:{MY}", "MySQL 서버") + '</div>')
for k, (nm, sub, c, bg, od) in enumerate([("cafe", "orders 표를 만들 곳", INK, CARD, 1), ("shop", "새로 만든 빈 데이터베이스", MAG, "#FBEAF3", 2)]):
    y = 300 + k * 200
    o.append(f'<div{bi("pop", od)} id="db-{nm}" style="position:absolute;left:{RX + 40}px;top:{y}px;width:{RW - 80}px;height:160px;box-sizing:border-box;border:3px solid {c if c != INK else LINE};border-radius:16px;background:{bg}">'
             + p(f"position:absolute;left:28px;top:24px;font-family:{MONO};font-size:34px;font-weight:700;color:{c}", nm)
             + p(f"position:absolute;left:28px;top:84px;font-size:25px;color:{SUB}", e(sub)) + '</div>')
o.append(pill(RX + RW - 340, 300 + 200 + 24, "USE shop · 지금 여기", MAG, order=3))
o.append(p(f"position:absolute;left:{RX}px;top:750px;width:{RW}px;font-size:27px;line-height:1.6;color:{SUB}", "mysql, sys처럼 MySQL이 스스로 쓰는 데이터베이스는 그림에서 뺐어요.", bi("fade", 4)))
W("s-db", o, "CREATE DATABASE로 데이터베이스를 새로 만들어요. 32에서 본 것처럼 서버 안에 데이터베이스가 여러 개 들어가요. root로 들어가서 CREATE DATABASE shop;을 치면 shop이 생겨요. SHOW DATABASES로 다시 보면 목록에 shop이 더해져 있어요. USE shop;은 이제부터 shop 안에서 일하겠다는 뜻이에요. Database changed가 나오면 들어간 거예요. SHOW TABLES;는 지금 데이터베이스 안의 표 목록이에요. 방금 만든 shop은 비어 있어서 Empty set이 나와요. shop은 연습용이라 2파트 끝에서 지워요." + REAL)

o = frame("s-create", EB3, "CREATE TABLE로 빈 표를 만들어요", C3)
sq = session("sql")
cr = [l for l in sq if l.startswith("mysql> CREATE")][0]
ok = sq[sq.index(cr) + 1]
t = Term([("$", P_HOME, "docker exec -it db mysql -u root -p cafe", {"…cafe": f'id="sc-db" style="color:{MAG}"'}), ("d", "…"), ("m", "mysql>", cr[7:]), ("o", ok)], 96, 214, size=24, w=1728, lh=1.6, tid="t-create")
o.append(t.html())
o += tag(t, 0, "끝에 cafe를 적으면 cafe에 바로 들어가요", MAG, 1)
yb = t.y + t.h + 60
segs = [("CREATE TABLE orders (", MAG, "orders라는 표를 만들어요"), ("    id INT PRIMARY KEY,", VO, "정수 · 기본 키"), ("    menu VARCHAR(20),", INK, "20자까지의 글자"), ("    qty INT", INK, "정수"), (");", MAG, None)]
for k, (s_, c, lab) in enumerate(segs):
    y = yb + k * 66
    o.append(p(f"position:absolute;left:96px;top:{y}px;font-family:{MONO};font-size:38px;font-weight:700;line-height:1.4;color:{c};white-space:pre", e(s_), bi("rise", 2) + DELAY(k * 80)))
    if lab:
        o += leader(96 + tw(s_, 38) + 24, y + 27, 760, c if c != INK else SUB, 2, e(lab), size=27)
html_, g = sheet(1240, yb - 10, COLS, [], "sc-tab", [150, 280, 150], size=32, rh=80, types=TYPES, name="orders", attrs=bi("rise", 3), pk=True)
o.append(html_)
o.append(p(f"position:absolute;left:1240px;top:{g['y'] + g['h'] + 30:.0f}px;width:584px;font-size:27px;line-height:1.6;color:{SUB}", "열 이름과 타입만 있고 행은 아직 0개예요.", bi("fade", 3)))
o.append(caption("한 줄로 쳐도 되고, 여러 줄로 나눠 쳐도 돼요. 쉼표로 열을 나눠요.", 920, 4, size=28, color=SUB))
W("s-create", o, "CREATE TABLE로 빈 표를 만들어요. 이번에는 mysql -u root -p 뒤에 cafe를 적었어요. 그러면 cafe 데이터베이스 안으로 바로 들어가요. CREATE TABLE 다음에 표 이름 orders를 쓰고, 괄호 안에 열을 쉼표로 나눠 적어요. 열마다 이름과 타입을 써요. 32에서 본 그대로 id는 정수이면서 기본 키, menu는 20자까지의 글자, qty는 정수예요. Query OK, 0 rows affected는 잘 만들었고 바뀐 행은 0개라는 뜻이에요. 표는 생겼지만 아직 행이 없어요. 아래처럼 여러 줄로 나눠 적어도 돼요." + REAL)

o = frame("s-desc", EB3, "SHOW TABLES로 표 목록을, DESCRIBE로 열을 봐요", C3)
qt = session("q-tables")
qt = qt[1:]
i_cr = [i for i, l in enumerate(qt) if l.startswith("mysql> CREATE")][0]
i_de = [i for i, l in enumerate(qt) if l.startswith("mysql> DESCRIBE")][0]
i_in = [i for i, l in enumerate(qt) if l.startswith("mysql> INSERT")][0]
left = qt[:i_cr] + ["mysql> CREATE TABLE orders (…);"] + qt[i_cr + 1:i_de]
while left and not left[-1].strip():
    left.pop()
t = Term(mysql_rows(left), 96, 214, size=24, w=640, lh=1.5, tid="t-tabs")
ie = [i for i, r in enumerate(t.rows) if r[1].startswith("Empty set")][0]
io = [i for i, r in enumerate(t.rows) if "| orders" in r[1]][0]
t.band(ie, order=1, color="rgba(127,134,150,.22)")
t.band(io, order=2, color="rgba(224,127,176,.22)")
o.append(t.html())
o += tag(t, ie, "아직 없어요", GRAY, 1, at=t.x + 330)
o += tag(t, io, "생겼어요", MAG, 2, at=t.x + 330)
right = qt[i_de:i_in]
while right and not right[-1].strip():
    right.pop()
t2 = Term(mysql_rows(right), 776, 214, size=24, w=1048, lh=1.5, tid="t-desc")
o.append(t2.html())
o.append(svg(f'<rect x="{t2.sx(4, "PRI") - 8:.0f}" y="{t2.top(4) + 2:.0f}" width="{t2.sw("PRI") + 16:.0f}" height="{t2.lp - 4:.0f}" rx="8" fill="none" stroke="{VO}" stroke-width="5"/>', 4))
yb = t2.y + t2.h + 40
expl = [("Field", "열 이름", INK), ("Type", "열의 타입 · 32에서 본 INT, VARCHAR", INK), ("Null", "비워 둬도 되는지 · 기본 키는 NO", INK), ("Key", "PRI는 기본 키(PRIMARY KEY)", VO)]
o.append(f'<div{STAGGER(3)} style="position:absolute;left:776px;top:{yb}px;width:1048px;display:flex;flex-direction:column;gap:14px">'
         + "".join(f'<div style="display:flex;flex-direction:row;gap:24px;align-items:baseline"><div style="width:120px;flex:none;font-family:{MONO};font-size:28px;font-weight:700;color:{c}">{k}</div><div style="font-size:27px;line-height:1.4;color:{INK}">{e(v)}</div></div>' for k, v, c in expl)
         + '</div>')
W("s-desc", o, "표를 만들었으면 잘 만들어졌는지 확인해요. SHOW TABLES;는 지금 데이터베이스 안의 표 목록이에요. cafe에 처음 들어가면 Empty set으로 비어 있어요. CREATE TABLE을 친 뒤에 다시 보면 orders가 나와요. DESCRIBE orders;는 표의 열을 한 줄씩 보여 줘요. Field는 열 이름, Type은 타입이에요. Null은 그 칸을 비워 둬도 되는지예요. 기본 키 id는 비울 수 없어서 NO예요. Key의 PRI는 기본 키라는 뜻이에요. 왼쪽의 CREATE TABLE은 앞 장과 같은 문장이라 괄호 안을 …로 줄였어요." + REAL)

o = frame("s-insert", EB3, "INSERT INTO로 행을 한 줄씩 넣어요", C3)
ins = [l for l in sq if l.startswith("mysql> INSERT")]
rows = []
for l in ins:
    rows += [("m", "mysql>", l[7:]), ("o", sq[sq.index(l) + 1])]
t = Term(rows, 96, 214, size=28, w=1140, lh=1.7, tid="t-ins")
o.append(t.html())
for k in range(2):
    o.append(p(f"position:absolute;left:{t.sx(k * 2, '(') - 4:.0f}px;top:{t.top(k * 2):.0f}px;height:{t.lp:.0f}px;padding:0 4px;border-radius:6px;font-family:{MONO};font-size:28px;font-weight:700;line-height:{t.lp:.0f}px;color:transparent;white-space:pre", e(ins[k][ins[k].index("("):ins[k].index(")") + 1]), f' id="si-v{k}"'))
html_, g = sheet(1300, 214, COLS, ORD, "si-tab", [120, 260, 120], size=30, rh=76, name="orders", pk=True,
                 cell_attrs={(0, 1): f' data-build-in="fly order 1" data-from="si-v0"', (1, 1): f' data-build-in="fly order 2" data-from="si-v1"'})
o.append(html_)
o.append(underline(1, round(t.sx(0, "(")), round(t.sx(0, "(") + t.sw("(1, 'latte', 2)")), round(t.top(0) + t.lp - 4), MAG))
o += tag(t, 1, "1행이 들어갔어요", MAG, 1)
yb = t.y + t.h + 60
o.append(p(f"position:absolute;left:96px;top:{yb}px;width:1728px;font-size:32px;font-weight:700;line-height:1.5;color:{INK}", "값은 표를 만들 때 적은 열 순서대로 넣어요. id, menu, qty예요.", bi("fade", 3)))
o.append(p(f"position:absolute;left:96px;top:{yb + 70}px;width:1728px;font-size:28px;line-height:1.6;color:{SUB}", "글자는 <span style=\"font-family:" + MONO + ";font-weight:700;color:" + INK + "\">'latte'</span>처럼 작은따옴표로 감싸고, 숫자는 그대로 써요.", bi("fade", 3)))
W("s-insert", o, "INSERT INTO로 행을 한 줄씩 넣어요. INSERT INTO orders VALUES 뒤 괄호에 값을 적어요. 값은 표를 만들 때 적은 열 순서대로예요. id, menu, qty 순서라서 1, 'latte', 2는 1번 주문, 라테, 2잔이에요. 글자는 작은따옴표로 감싸고 숫자는 그대로 써요. Query OK, 1 row affected는 행 하나가 들어갔다는 뜻이에요. 두 번 넣었으니 표에 행이 두 개 생겼어요. 같은 id를 또 넣거나 qty에 글자를 넣으면 막혀요. 32에서 본 오류예요." + REAL)

o = frame("s-select", EB3, "SELECT로 표를 꺼내 봐요", C3)
se = [l for l in sq if l.startswith("mysql> SELECT")][0]
res = sq[sq.index(se) + 1: sq.index(se) + 8]
t = Term([("m", "mysql>", se[7:], {"*": f'style="color:{MAG}"'})] + [("o", l) for l in res], 96, 214, size=30, w=820, lh=1.5, tid="t-sel")
o.append(t.html())
qt_ = session("q-tables")
se2 = [l for l in qt_ if l.startswith("mysql> SELECT")][0]
res2 = qt_[qt_.index(se2) + 1: qt_.index(se2) + 8]
t2 = Term([("m", "mysql>", se2[7:], {"menu, qty": f'style="color:{MAG}"'})] + [("o", l) for l in res2], 1004, 214, size=30, w=820, lh=1.5, tid="t-sel2", attrs=bi("rise", 3))
o.append(t2.html())
o.append(underline(1, round(t.sx(0, "*") - 4), round(t.sx(0, "*") + t.sw("*") + 4), round(t.top(0) + t.lp - 4), MAG))
o.append(pill(t.x, t.y + t.h + 30, "* = 모든 열", MAG, order=1, size=26))
o.append(spot(2, t.x + 10, t.top(4) - 4, t.w - 20, 2 * t.lp + 8, pad=6, r=10))
o.append(spot_off(3))
o.append(underline(4, round(t2.sx(0, "menu, qty")), round(t2.sx(0, "menu, qty") + t2.sw("menu, qty")), round(t2.top(0) + t2.lp - 4), MAG))
o.append(pill(t2.x, t2.y + t2.h + 30, "적은 열만 꺼내요", MAG, order=4, size=26))
o.append(f'<div style="position:absolute;left:96px;top:{t.y + t.h + 130}px;width:1728px;height:1px;background:{LINE}"></div>')
o.append(p(f"position:absolute;left:96px;top:{t.y + t.h + 160}px;width:1728px;font-size:30px;line-height:1.6;color:{INK}", "FROM 뒤에 어느 표에서 꺼낼지 적어요. 조건으로 고르는 WHERE, 고치는 UPDATE, 지우는 DELETE는 다음에 배워요.", bi("fade", 5)))
W("s-select", o, "SELECT로 표를 꺼내 봐요. 왼쪽 SELECT * FROM orders;의 별표는 모든 열이라는 뜻이에요. FROM 뒤에 어느 표에서 꺼낼지 적어요. 넣은 두 행이 표 모양으로 나와요. 아래 줄은 행이 몇 개인지와 걸린 시간이에요. 오른쪽처럼 별표 대신 menu, qty처럼 열 이름을 쉼표로 적으면 그 열만 꺼내요. 조건을 붙여서 원하는 행만 고르는 WHERE, 고치는 UPDATE, 행을 지우는 DELETE는 다음에 배워요." + REAL)

o = frame("s-drop", EB3, "DROP으로 표와 데이터베이스를 지워요", C3)
qd = session("q-drop")
qd = [l for l in qd if l not in ("Bye",) and not l.startswith("mysql> exit")]
i_dd = [i for i, l in enumerate(qd) if l.startswith("mysql> DROP DATABASE")][0]
left = qd[1:i_dd]
while left and not left[-1].strip():
    left.pop()
rows = [("$", P_HOME, "docker exec -it db mysql -u root -p shop"), ("o", "Enter password:"), ("d", "…")] + mysql_rows(left)
t = Term(rows, 96, 214, size=22, w=860, lh=1.4, tid="t-drop1")
idt = [i for i, r in enumerate(t.rows) if r[1].startswith("mysql> DROP TABLE")][0]
ie = [i for i, r in enumerate(t.rows) if r[1].startswith("Empty set")][0]
t.band(idt, idt + 1, order=1, color="rgba(240,122,114,.22)")
o.append(t.html())
o += tag(t, idt, "test 표를 지워요", RED, 1, at=t.x + 480)
o += tag(t, ie, "표가 없어졌어요", GRAY, 2, at=t.x + 360)
right = qd[i_dd:]
while right and not right[-1].strip():
    right.pop()
t2 = Term(mysql_rows(right), 1004, 214, size=22, w=820, lh=1.4, tid="t-drop2")
t2.band(0, 1, order=3, color="rgba(240,122,114,.22)")
o.append(t2.html())
o += tag(t2, 0, "shop을 통째로", RED, 3, at=t2.x + 480)
ip = [i for i, r in enumerate(t2.rows) if "| performance_schema" in r[1]][0]
o += tag(t2, ip, "shop이 없어요", GRAY, 4, at=t2.x + 420)
yb = t2.y + t2.h + 40
o.append(f'<div{bi("rise", 5)} style="position:absolute;left:1004px;top:{yb}px;width:820px;box-sizing:border-box;padding:22px 30px;background:#FBE9E7;border-left:8px solid {RED};border-radius:14px">'
         + p(f"font-size:28px;font-weight:700;line-height:1.5;color:{RED}", "DROP은 묻지 않고 바로 지우고, 되돌릴 수 없어요.")
         + p(f"margin-top:6px;font-size:25px;line-height:1.6;color:{INK}", "안에 든 행까지 다 사라져요. 연습할 때는 지워도 되는 것에만 쳐요.") + '</div>')
W("s-drop", o, "DROP으로 표와 데이터베이스를 지워요. 이번에는 mysql -u root -p 뒤에 shop을 적어서 shop에 바로 들어갔어요. 연습용 test 표를 하나 만들고 DROP TABLE test;로 지웠어요. SHOW TABLES로 보면 다시 Empty set이에요. DROP DATABASE shop;은 데이터베이스를 안의 표까지 통째로 지워요. SHOW DATABASES 목록에서 shop이 빠졌어요. DROP은 정말 지울지 묻지 않아요. 지운 표와 행은 되돌릴 수 없으니, 연습할 때는 지워도 되는 것에만 쳐요." + REAL)

# =====================================================================
# part 3: accounts and ways to connect
# =====================================================================
o = frame("u-user", EBU, "-e 두 개를 더하면 앱이 쓸 계정이 생겨요", CU)
ua = session("u-app")
ua = [l for l in ua[1:] if l != "Bye" and not l.startswith("mysql> exit")]
while ua and not ua[-1].strip():
    ua.pop()
rows = [("$", P_HOME, "docker exec -it db mysql -u cafe -p cafe", {"-u cafe": f'style="color:{TEAL}"'}), ("o", "Enter password:"), ("d", "…")] + mysql_rows(ua)
t = Term(rows, 96, 214, size=22, w=1100, lh=1.4, tid="t-user")
i_s = [i for i, r in enumerate(t.rows) if "| cafe" in r[1]][0]
i_er = [i for i, r in enumerate(t.rows) if r[1].startswith("ERROR 1044")][0]
t.band(i_s, i_s + 2, order=2, color="rgba(79,184,194,.22)")
o.append(t.html())
o += tag(t, 1, "cafe5678을 쳐요", TEAL, 1)
o += tag(t, i_s + 1, "cafe 하나만 보여요", TEAL, 2, at=t.x + 420)
o.append(pen_box(3, round(t.tx - 10), round(t.top(i_er - 1) + 2), round(t.sw(t.rows[i_er][1]) + 20), round(2 * t.lp - 4), RED, 5))
RX, RW = 1240, 584
o.append(f'<div{bi("rise", 1)} style="position:absolute;left:{RX}px;top:214px;width:{RW}px;box-sizing:border-box;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:26px 30px;display:flex;flex-direction:column;gap:10px">'
         + p(f"font-size:25px;font-weight:700;color:{GRAY}", "docker run에 더한 -e 두 개")
         + p(f"font-family:{MONO};font-size:25px;font-weight:700;color:{TEAL};white-space:nowrap", "-e MYSQL_USER=cafe")
         + p(f"font-family:{MONO};font-size:25px;font-weight:700;color:{TEAL};white-space:nowrap", "-e MYSQL_PASSWORD=cafe5678")
         + p(f"font-size:23px;line-height:1.6;color:{SUB}", "cafe 사용자를 만들고, MYSQL_DATABASE의 cafe만 쓰게 해 줘요.") + '</div>')
cmpr = [("", "root", "cafe"), ("비밀번호", "cafe1234", "cafe5678"), ("보이는 DB", "전부", "cafe만"), ("새 DB 만들기", "돼요", "막혀요")]
cells = []
for r_, (a, b, c) in enumerate(cmpr):
    for j, v in enumerate((a, b, c)):
        hd = r_ == 0
        col = (MAG if j == 1 else TEAL) if hd else (RED if v == "막혀요" else (SUB if j == 0 else INK))
        cells.append(p(f"font-family:{MONO if (hd or r_ == 1) and j else SANS};font-size:{25 if hd else 23}px;font-weight:{700 if hd or j == 0 else 400};line-height:1.5;color:{col};white-space:nowrap", e(v)))
o.append(f'<div{bi("rise", 4)} style="position:absolute;left:{RX}px;top:560px;width:{RW}px;box-sizing:border-box;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:24px 30px;display:grid;grid-template-columns:190px 1fr 1fr;row-gap:12px">' + "".join(cells) + '</div>')
o.append(caption("앱에는 root 대신 cafe 계정을 줘요. 실수해도 cafe 밖은 건드리지 못해요.", t.y + t.h + 44, 5, size=28, width=1100))
W("u-user", o, "root는 서버 전체를 다루는 관리자예요. 앱이 쓸 계정은 따로 만들어 주는 게 좋아요. docker run에 -e MYSQL_USER=cafe와 -e MYSQL_PASSWORD=cafe5678을 더해 켜면, MySQL이 처음 준비할 때 cafe 사용자를 만들어요. cafe 사용자는 MYSQL_DATABASE로 만든 cafe 데이터베이스만 쓸 수 있어요. mysql -u cafe -p로 들어가 SHOW DATABASES를 치면 cafe와 MySQL 기본 둘만 보여요. 표는 만들 수 있지만 CREATE DATABASE는 ERROR 1044로 막혀요. 앱이 실수하거나 비밀번호가 새도 cafe 밖은 지킬 수 있어요. 따라 칠 때는 앞의 db를 docker stop, docker rm으로 지우고 -e 네 개로 다시 켜요. 이때 2파트에서 만든 표가 사라지는데, 왜 그런지는 4파트에서 봐요." + REAL, ("pu", "계정과 접속 방법"))

o = frame("u-bash", EBU, "bash로 먼저 들어가서 mysql을 열어도 돼요", CU)
ub = session("u-bash")
rows, prev_blank = [("$", P_HOME, "docker exec -it db bash")], False
for l in ub:
    if not l.strip():
        if prev_blank or rows[-1][1] == "Enter password:":
            continue
        prev_blank = True
    else:
        prev_blank = False
    if l.startswith("bash-5.1# "):
        rows.append(("#", "bash-5.1", l[10:]))
    elif l.startswith("mysql> ") or l.startswith("ERROR"):
        rows += mysql_rows([l])
    else:
        rows.append(("o", l))
    if l == "Enter password:":
        rows.append(("d", "…"))
t = Term(rows, 96, 214, size=24, w=960, lh=1.45, tid="t-bash")
ib = [i for i, r in enumerate(t.rows) if r[0] == "#"]
im = [i for i, r in enumerate(t.rows) if r[1].startswith("mysql> SHOW")][0]
ix = [i for i, r in enumerate(t.rows) if r[1].startswith("mysql> exit")][0]
o.append(t.html())
o += tag(t, 0, "컨테이너 안 bash로", DK, 1)
o += tag(t, ib[0], "그 안에서 mysql", MY, 2)
o += tag(t, im, "SQL을 쳐요", MAG, 3)
o += tag(t, ix, "mysql에서 나와요", MY, 4)
o += tag(t, ib[1], "bash에서도 나와요", DK, 4)
RX, RW = 1160, 664
lay = [("내 터미널", "~ $", INK, "#EEF0F3", 0), ("컨테이너 안 bash", "bash-5.1#", DK, "#E7EEFD", 1), ("MySQL", "mysql>", MY, MYBG, 2)]
for k, (h, pr, c, bg, od) in enumerate(lay):
    y = 236 + k * 230
    o.append(f'<div{bi("rise", od) if od else ""} style="position:absolute;left:{RX}px;top:{y}px;width:{RW - 120}px;height:150px;box-sizing:border-box;border:3px solid {c if c != INK else LINE};border-radius:18px;background:{bg}">'
             + p(f"position:absolute;left:28px;top:26px;font-size:30px;font-weight:700;color:{c}", e(h))
             + p(f"position:absolute;left:28px;top:84px;font-family:{MONO};font-size:28px;font-weight:700;color:{INK}", e(pr)) + '</div>')
    if k:
        y0 = 236 + (k - 1) * 230 + 150
        o.append(svg(arrow_path(f"M{RX + 200},{y0 + 8} L{RX + 200},{y - 12}", c, 4) + head_at(RX + 200, y - 8, 90, c, 14), od))
        o.append(svg(arrow_path(f"M{RX + RW - 70},{y + 60} L{RX + RW - 70},{y0 - 60}", GRAY, 4, dash="8 8") + head_at(RX + RW - 70, y0 - 64, -90, GRAY, 14), 4))
o.append(pill(RX + RW - 104, 236 + 150 + 22, "exit", GRAY, order=4, size=22))
o.append(pill(RX + RW - 104, 236 + 380 + 22, "exit", GRAY, order=4, size=22))
o.append(caption("컨테이너 안의 파일도 같이 볼 때 써요. 나올 때는 exit를 두 번 쳐요.", t.y + t.h + 36, 5, size=28, width=1000))
W("u-bash", o, "접속하는 방법이 하나 더 있어요. 30에서 배운 docker exec -it db bash로 컨테이너 안에 먼저 들어가요. 표시가 bash-5.1#로 바뀌어요. 그 안에서 mysql -u root -p cafe를 치면 앞에서처럼 mysql>이 나와요. 이 이미지의 bash는 표시가 bash-5.1#처럼 버전으로 나와요. 오른쪽 그림처럼 상자 안에 상자로 들어간 거예요. 그래서 나올 때도 두 번이에요. mysql에서 exit를 치면 bash로, bash에서 exit를 한 번 더 치면 내 터미널로 돌아와요. 컨테이너 안의 파일이나 로그를 같이 살펴볼 때 이 방법을 써요." + REAL)

o = frame("u-one", EBU, "-e로 SQL 한 문장만 실행하고 바로 나와요", CU)
one = RA("u-one")
rows = [("$", P_HOME, C("u-one"), {"-pcafe1234": f'style="color:{RED}"', '-e "SHOW TABLES;"': f'style="color:{MAG}"'})] + [("e", l) if l.startswith("mysql: [Warning]") else ("o", l) for l in one]
t = Term(rows, 96, 214, size=22, w=1160, lh=1.5, tid="t-one")
t.band(1, 2, order=1, color="rgba(224,127,176,.2)")
t.band(3, order=2, color="rgba(240,122,114,.18)")
o.append(t.html())
o.append(underline(1, round(t.sx(0, '-e "SHOW')), round(t.end(0)), round(t.top(0) + t.lp - 4), MAG))
o += tag(t, 2, "결과만 받고 끝나요", MAG, 1, at=t.x + 260)
o.append(p(f"position:absolute;left:96px;top:{t.y + t.h + 24}px;width:1160px;font-size:26px;line-height:1.6;color:{SUB}", "결과를 받기만 하니 키보드로 칠 일이 없어서 -it를 빼요. 31의 docker exec 이름 명령과 같아요.", bi("fade", 1)))
t2 = Term([("$", P_HOME, C("u-inline"), {"-pcafe1234": f'style="color:{RED}"'}), ("e", RA("u-inline")[0]), ("d", "…"), ("m", "mysql>", "exit"), ("o", "Bye")], 96, t.y + t.h + 96, size=22, w=1160, lh=1.5, tid="t-inline", attrs=bi("rise", 2))
t2.band(1, order=3, color="rgba(240,122,114,.18)")
o.append(t2.html())
o += tag(t2, 0, "비밀번호를 묻지 않아요", RED, 2)
yb = t2.y + t2.h + 30
o.append(f'<div{bi("rise", 3)} style="position:absolute;left:96px;top:{yb}px;width:1160px;box-sizing:border-box;padding:22px 30px;background:#FBE9E7;border-left:8px solid {RED};border-radius:14px">'
         + p(f"font-size:27px;font-weight:700;line-height:1.5;color:{RED}", "-p 바로 뒤에 띄우지 않고 붙이면 비밀번호를 묻지 않아요")
         + p(f"margin-top:6px;font-size:24px;line-height:1.6;color:{INK}", "비밀번호가 명령 기록에 남아서 Warning이 나와요. 연습할 때만 써요.") + '</div>')
RX, RW = 1300, 524
ways = [("docker exec -it db mysql -u root -p", "SQL을 여러 개 칠 때 · 기본", MY), ("docker exec -it db bash", "컨테이너 안도 같이 볼 때", DK), ('docker exec db mysql … -e "SQL"', "한 문장만 확인할 때", MAG)]
o.append(p(f"position:absolute;left:{RX}px;top:214px;font-size:28px;font-weight:700;color:{INK}", "언제 어떤 방법?", bi("fade", 4)))
o.append(f'<div{STAGGER(4)} style="position:absolute;left:{RX}px;top:276px;width:{RW}px;display:flex;flex-direction:column;gap:20px">'
         + "".join(f'<div style="box-sizing:border-box;padding:20px 24px;background:{CARD};border:2px solid {LINE};border-left:8px solid {c};border-radius:14px"><div style="font-family:{MONO};font-size:19px;font-weight:700;color:{INK};white-space:nowrap">{e(k)}</div><div style="margin-top:8px;font-size:23px;line-height:1.5;color:{SUB}">{e(v)}</div></div>' for k, v, c in ways)
         + '</div>')
W("u-one", o, "SQL 한 문장만 확인하고 싶을 때는 들어가지 않고 바로 실행해요. mysql 뒤에 -e와 따옴표로 감싼 SQL을 적으면, 그 문장만 실행하고 결과를 찍고 끝나요. 결과는 표 테두리 없이 줄만 나와요. 받기만 하니 키보드로 칠 일이 없어서 -it를 뺐어요. 31에서 배운 docker exec 이름 명령과 같은 모양이에요. 이번에는 -p 바로 뒤에 비밀번호를 붙여 썼어요. 그러면 비밀번호를 묻지 않아요. 아래처럼 -it로 들어갈 때도 똑같아요. 띄어 쓰면 비밀번호가 아니라 데이터베이스 이름으로 읽혀요. 비밀번호가 명령 기록에 남아서 Warning이 나와요. 그래서 연습할 때만 쓰고, 평소에는 -p만 적고 물어볼 때 쳐요. 오른쪽은 지금까지 본 세 가지 접속 방법이에요." + REAL)

# =====================================================================
# part 4: volume and compose
# =====================================================================
def short_id(scene, k=0):
    return ("d", RA(scene, k)[0][:12] + "…")


o = frame("v-gone", EB4, "볼륨 없이 켠 컨테이너를 지우면 표도 같이 사라져요", C4)
rows = [("$", P_HOME, "docker stop db"), ("o", "db"), ("$", P_HOME, "docker rm db"), ("o", "db"), ("$", P_HOME, C("rerun")), short_id("rerun"),
        ("$", P_HOME, C("gone")), ("o", "Enter password:"), ("d", "…")] + sess_rows("gone")[1:]
t = Term(rows, 96, 214, size=24, w=1728, lh=1.6, tid="t-gone")
t.band(len(t.rows) - 1, order=3, color="rgba(240,122,114,.22)")
o.append(t.html())
o += tag(t, 2, "앞 장까지 쓰던 db를 지우고", GRAY, 1, at=t.x + 560)
o += tag(t, 4, "같은 명령으로 다시 켜요", DK, 2, at=t.x + 1460, gap=0) if False else []
o.append(underline(2, round(t.sx(4, "docker run")), round(t.end(4)), round(t.top(4) + t.lp - 4), DK))
o.append(underline(3, round(t.sx(len(t.rows) - 1, "Table")), round(t.end(len(t.rows) - 1)), round(t.top(len(t.rows) - 1) + t.lp - 4), RED))
o.append(shake(3, "t-gone"))
yb = t.y + t.h + 50
o.append(p(f"position:absolute;left:96px;top:{yb}px;width:1728px;font-size:32px;font-weight:700;line-height:1.5;color:{INK}", "orders 표가 없대요. 표 안의 주문도 같이 사라졌어요.", bi("fade", 3)))
o.append(p(f"position:absolute;left:96px;top:{yb + 66}px;width:1728px;font-size:28px;line-height:1.6;color:{SUB}", "cafe 데이터베이스는 -e로 다시 만들어졌지만, 그 안은 텅 비어 있어요.", bi("fade", 3)))
W("v-gone", o, "볼륨 없이 켠 컨테이너를 지우면 표도 같이 사라져요. orders 표를 만들어 둔 db를 docker stop, docker rm으로 지웠어요. 그리고 똑같은 docker run 명령으로 다시 켰어요. 들어가서 SELECT를 치면 ERROR 1146, orders 표가 없다는 오류가 나요. 표 안의 주문도 같이 없어졌어요. cafe 데이터베이스는 -e MYSQL_DATABASE 덕분에 새로 만들어졌지만 그 안은 비어 있어요. 실제 카페라면 하루 주문이 다 날아간 거예요. 왜 그런지 다음 장에서 그림으로 봐요." + REAL, ("p4", "볼륨과 compose"))

o = frame("v-why", EB4, "표는 컨테이너 안 /var/lib/mysql 폴더에 저장돼요", C4)
for k, (head, col) in enumerate([("볼륨 없이", RED), ("볼륨을 붙이면", GR)]):
    x = 96 + k * 884
    od = 1 if k == 0 else 3
    o.append(p(f"position:absolute;left:{x}px;top:220px;font-size:32px;font-weight:700;color:{col}", head, bi("fade", od) if k else ""))
    o.append(f'<div id="vw-c{k}"{bi("rise", od) if k else ""} style="position:absolute;left:{x}px;top:280px;width:420px;height:340px;box-sizing:border-box;background:#EEF3FE;border:3px solid {DK};border-radius:20px"></div>')
    o.append(p(f"position:absolute;left:{x + 26}px;top:300px;font-size:26px;font-weight:700;color:{DK}", "컨테이너 db", bi("rise", od) if k else ""))
    if k == 0:
        o.append(f'<div style="position:absolute;left:{x + 26}px;top:370px;width:368px;height:220px;box-sizing:border-box;background:#FFFFFF;border:2px solid {VO};border-radius:14px;padding:20px 22px">'
                 + p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{VO}", "/var/lib/mysql") + p(f"margin-top:14px;font-size:24px;line-height:1.5;color:{INK}", "cafe 데이터베이스<br>orders 표와 주문") + '</div>')
        o.append(f'<div{bi("fade", 2)} style="position:absolute;left:{x}px;top:280px;width:420px;height:340px;border-radius:20px;background:rgba(246,245,241,.9);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px">'
                 + p(f"font-family:{MONO};font-size:34px;font-weight:700;color:{RED}", "docker rm db") + p(f"font-size:26px;color:{SUB}", "폴더째 같이 지워져요") + '</div>')
        o.append(p(f"position:absolute;left:{x}px;top:660px;width:820px;font-size:28px;line-height:1.6;color:{INK}", "30에서 본 것처럼, 컨테이너 안에서 만든 파일은 컨테이너와 운명을 같이해요.", bi("fade", 2)))
    else:
        o.append(f'<div{bi("rise", od)} style="position:absolute;left:{x + 26}px;top:370px;width:368px;height:220px;box-sizing:border-box;border:3px dashed {VO};border-radius:14px;padding:20px 22px">'
                 + p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{VO}", "/var/lib/mysql") + p(f"margin-top:14px;font-size:24px;line-height:1.5;color:{SUB}", "밖의 보관함과<br>연결된 자리") + '</div>')
        o.append(svg(arrow_path(f"M{x + 410},480 L{x + 520},480", VO, 5) + head_at(x + 522, 480, 0, VO), od))
        o.append(cyl(x + 540, 340, 288, 280, "cafe-data", "볼륨 · 표가 여기 있어요", VO, VOBG, "vw-vol", attrs=bi("rise", od) + DELAY(150), ssize=21))
        o.append(f'<div{bi("fade", 4)} style="position:absolute;left:{x}px;top:280px;width:420px;height:340px;border-radius:20px;background:rgba(246,245,241,.9);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px">'
                 + p(f"font-family:{MONO};font-size:34px;font-weight:700;color:{RED}", "docker rm db") + p(f"font-size:26px;color:{SUB}", "컨테이너만 지워져요") + '</div>')
        o.append(p(f"position:absolute;left:{x}px;top:660px;width:828px;font-size:28px;line-height:1.6;color:{INK}", "새 컨테이너에 같은 볼륨을 붙이면 예전 표를 그대로 읽어요.", bi("fade", 4)))
o.append(f'<div style="position:absolute;left:96px;top:800px;width:1728px;height:1px;background:{LINE}"></div>')
o.append(p(f"position:absolute;left:96px;top:830px;width:1728px;font-size:27px;line-height:1.6;color:{SUB}", "mysql 이미지는 -v를 안 붙여도 이름 없는 볼륨을 스스로 만들어요. 다만 새 컨테이너는 새 이름 없는 볼륨을 받아서 예전 표를 못 찾아요. docker volume ls에 긴 이름이 쌓이는 게 이 볼륨이에요.", bi("fade", 5)))
W("v-why", o, "표는 컨테이너 안 /var/lib/mysql 폴더에 저장돼요. MySQL은 데이터베이스와 표를 이 폴더에 파일로 남겨요. 볼륨이 없으면 이 폴더가 컨테이너 안에만 있어서, docker rm으로 컨테이너를 지울 때 폴더째 같이 지워져요. 30에서 nginx 안에서 고친 파일이 사라진 것과 같은 이유예요. 오른쪽처럼 30에서 배운 이름 있는 볼륨 cafe-data를 /var/lib/mysql 자리에 붙이면, 표는 붕어빵 밖 보관함인 볼륨에 저장돼요. 컨테이너를 지워도 볼륨은 남고, 새 컨테이너에 같은 볼륨을 붙이면 예전 표를 그대로 읽어요. 사실 mysql 이미지는 -v를 안 붙여도 이름 없는 볼륨을 만들어요. 하지만 새 컨테이너는 새 볼륨을 받아서 예전 것을 못 찾아요. 그래서 꼭 이름을 붙여요.")

o = frame("v-keep", EB4, "-v cafe-data:/var/lib/mysql을 붙이면 지웠다 켜도 남아요", C4)
o += parts(96, 214, [("docker run … -p 3306:3306", GRAY, None, None), ("-v cafe-data:/var/lib/mysql", VO, "이름 있는 볼륨을 MySQL 데이터 폴더에", "vk-v"), ("mysql:8.4", GRAY, None, None)], size=40, order=None, lw=620)
vs = sess_rows("vsql")
rows_a = [("$", P_HOME, "docker run … -v cafe-data:/var/lib/mysql mysql:8.4"), short_id("vrun"), ("$", P_HOME, "docker exec -it db mysql -u root -p cafe"), ("d", "…")] + [("m", "mysql>", "CREATE TABLE orders (…);"), ("o", "Query OK, 0 rows affected")] + [r for r in vs if (r[0] == "m" and r[2].startswith("INSERT")) or (r[1].startswith("Query OK, 1"))] + [("$", P_HOME, "docker stop db"), ("o", "db"), ("$", P_HOME, "docker rm db"), ("o", "db")]
ta = Term(rows_a, 96, 380, size=19, w=850, lh=1.55, tid="t-vk1", attrs=bi("rise", 1))
o.append(ta.html())
o.append(pill(96, ta.y + ta.h + 18, "주문을 넣고 컨테이너를 지워요", GRAY, 1))
kp = sess_rows("kept")
rows_b = [("$", P_HOME, "docker run … -v cafe-data:/var/lib/mysql mysql:8.4"), short_id("vrun2"), ("$", P_HOME, "docker exec -it db mysql -u root -p cafe"), ("d", "…")] + kp[1:]
tb = Term(rows_b, 974, 380, size=19, w=850, lh=1.55, tid="t-vk2", attrs=bi("rise", 2))
li = [i for i, r in enumerate(tb.rows) if "latte" in r[1]][0]
tb.band(li, order=3, color="rgba(127,209,139,.24)")
o.append(tb.html())
o.append(pill(974, tb.y + tb.h + 18, "같은 볼륨으로 다시 켜면 주문이 그대로예요", GR, 3))
W("v-keep", o, "-v cafe-data:/var/lib/mysql을 붙이면 지웠다 켜도 남아요. 왼쪽은 볼륨을 붙여 켠 db에 표를 만들고 주문 하나를 넣은 뒤, docker stop과 docker rm으로 지운 모습이에요. 오른쪽은 같은 명령으로 다시 켜서 SELECT를 친 결과예요. 이번에는 오류 없이 1번 주문 latte 2잔이 그대로 나와요. 컨테이너는 새로 만들었지만 표는 cafe-data 볼륨에 있었기 때문이에요. 비밀번호와 데이터베이스를 만드는 처음 준비도 볼륨에 이미 있어서 다시 하지 않아요. 터미널의 docker run은 앞 장과 같은 옵션이라 가운데를 …로 줄였어요." + REAL)

o = frame("c-yaml", EB4, "길어진 docker run을 compose.yaml에 옮겨 적어요", C4)
cy_ = COMPOSE.rstrip("\n").split("\n")
colmap = {"environment:": MAG, "MYSQL_ROOT_PASSWORD": MAG, "MYSQL_DATABASE": MAG, "ports:": DK, '"3306:3306"': DK, "volumes:": VO, "cafe-data": VO}


def ycol(l):
    s_ = yaml_html(l)
    for k_, c_ in colmap.items():
        if k_ in l:
            s_ = f'<span style="background:{c_}1A;border-radius:4px">' + s_ + '</span>'
            break
    return s_


ed, g = editor("cy-ed", "~/cafe-db/compose.yaml", [ycol(l) for l in cy_], 900, 214, 924, fs=30, color=GR)
o.append(ed)
flags = [("-e MYSQL_ROOT_PASSWORD=cafe1234", MAG, 4), ("-e MYSQL_DATABASE=cafe", MAG, 5), ("-p 3306:3306", DK, 7), ("-v cafe-data:/var/lib/mysql", VO, 9)]
for k, (f_, c_, li) in enumerate(flags):
    y = gcy(g, li)
    o.append(p(f"position:absolute;left:96px;top:{y - 22:.0f}px;font-family:{MONO};font-size:28px;font-weight:700;line-height:1.5;color:{c_};white-space:nowrap", e(f_), bi("rise", k + 1)))
    o.append(link(k + 1, 96 + tw(f_, 28) + 16, y, g["tx"] - 30, y, c_, 3))
o.append(lband(5, g, 11, 2, VO))
o += leader(g["left"] + g["w"] - 400, gcy(g, 12), g["left"] + g["w"] - 360, VO, 5) if False else []
o.append(p(f"position:absolute;left:96px;top:{gtop(g, 11):.0f}px;width:760px;font-size:28px;font-weight:700;line-height:1.5;color:{VO}", "맨 아래 volumes:는 이 파일에서 쓸<br>이름 있는 볼륨을 적는 칸이에요.", bi("fade", 5)))
o.append(p(f"position:absolute;left:96px;top:{gtop(g, 1):.0f}px;width:760px;font-size:28px;line-height:1.6;color:{SUB}", "30에서 쓴 ports, volumes에 <b style=\"color:" + MAG + "\">environment</b>가 하나 더 생겼어요. -e 자리예요.", bi("fade", 1)))
W("c-yaml", o, "길어진 docker run을 compose.yaml에 옮겨 적어요. 30에서 배운 compose 그대로예요. 새 폴더 ~/cafe-db를 만들고 그 안에 compose.yaml을 둬요. 서비스 이름은 db, 이미지는 mysql:8.4예요. -e 두 개는 environment 아래에 이름: 값 모양으로 적어요. -p는 ports, -v는 volumes 자리예요. 30과 다른 점은 맨 아래 volumes: 칸이에요. 이름 있는 볼륨을 compose에서 쓰려면 이 칸에 이름을 한 번 적어 둬야 해요. 들여쓰기는 30처럼 2칸씩이에요.")

o = frame("c-up", EB4, "docker compose up -d로 켜고, 서비스 이름 db로 들어가요", C4)
cu = RA("c-up")
cps = RA("c-ps")
rows = [("$", P_DB, "docker compose up -d")] + [("o", l) for l in cu] + [("o", ""), ("$", P_DB, "docker compose ps")] + [("o", l) for l in cps] + [("o", ""), ("$", P_DB, "docker compose exec db mysql -u root -p cafe", {"exec db": f'style="color:{GR}"'}), ("o", "Enter password:"), ("d", "…"), ("m", "mysql>", "")]
t = Term(rows, 96, 214, size=20, w=1728, lh=1.65, tid="t-cup")
vi = [i for i, r in enumerate(t.rows) if "Volume" in r[1]][0]
t.band(vi, order=1, color="rgba(242,196,109,.2)")
o.append(t.html())
o += tag(t, vi, "폴더 이름이 앞에 붙은 볼륨", VO, 1, gap=36)
ei = [i for i, r in enumerate(t.rows) if "compose exec" in r[1]][0]
o += tag(t, ei, "컨테이너 이름 대신 서비스 이름", GR, 2, gap=36)
o.append(caption("<span style=\"font-family:" + MONO + "\">docker compose exec 서비스 명령</span>은 31의 docker exec와 같은 일을 해요.", t.y + t.h + 44, 3, size=30))
W("c-up", o, "docker compose up -d로 켜고, 서비스 이름 db로 들어가요. ~/cafe-db 폴더에서 up -d를 치면 네트워크, 볼륨, 컨테이너가 차례로 만들어져요. 볼륨 이름이 cafe-db_cafe-data예요. compose는 폴더 이름을 앞에 붙여서 다른 폴더의 볼륨과 겹치지 않게 해요. docker compose ps로 보면 컨테이너 이름은 cafe-db-db-1이에요. 이 긴 이름을 칠 필요 없이 docker compose exec 뒤에 서비스 이름 db를 적으면 돼요. 31에서 docker exec cafe-web-1로 친 것과 같은 일을 더 짧게 하는 거예요. 처음 켤 때는 앞에서처럼 10초쯤 기다렸다가 들어가요." + REAL)

o = frame("cmp", EB4, "30, 31에서 쓴 컨테이너와 무엇이 같고 다를까요", C4)
hd = ["", "30, 31 · nginx", "33 · MySQL"]
rws = [("설정 건네기", "설정 파일을 -v ./conf로", "-e 환경 변수로"),
       ("볼륨에 담는 것", "./site의 html 파일 (내가 고쳐요)", "/var/lib/mysql 표 파일 (MySQL만 고쳐요)"),
       ("들어가기", "docker exec -it web bash", "docker exec -it db mysql -u root -p"),
       ("켜졌는지 보기", "curl localhost", "logs의 port: 3306, SHOW DATABASES;"),
       ("기다리는 포트", "80", "3306")]
xs = [96, 470, 1110]
ws = [360, 620, 714]
for j, h in enumerate(hd):
    o.append(p(f"position:absolute;left:{xs[j]}px;top:230px;width:{ws[j]}px;font-size:28px;font-weight:700;color:{[GRAY, NG, MY][j]};white-space:nowrap", e(h)))
for i, r in enumerate(rws):
    y = 290 + i * 126
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:1px;background:{LINE}"></div>')
    a = bi("rise", 1) + DELAY(i * 80)
    for j, v in enumerate(r):
        mono = j and (v.startswith("docker") or v.startswith("curl") or v.isdigit())
        o.append(p(f"position:absolute;left:{xs[j]}px;top:{y + 38}px;width:{ws[j]}px;{'font-family:' + MONO + ';font-size:25px;' if mono else 'font-size:27px;'}font-weight:{700 if j != 1 else 400};color:{INK if j != 1 else SUB};white-space:nowrap", e(v), a))
o.append(f'<div style="position:absolute;left:96px;top:{290 + 5 * 126}px;width:1728px;height:1px;background:{LINE}"></div>')
o.append(caption("run, ps, logs, stop, rm, exec, compose는 그대로예요. 이미지에 따라 옵션만 달라져요.", 950, 2, size=30))
W("cmp", o, "30, 31에서 쓴 nginx 컨테이너와 비교해 봐요. nginx는 설정 파일을 -v로 연결해서 건넸고, MySQL은 -e 환경 변수로 건네요. 볼륨에 담는 것도 달라요. nginx의 site 폴더는 내가 VS Code로 고치는 파일이었지만, /var/lib/mysql의 표 파일은 MySQL만 고쳐요. 그래서 내 폴더 대신 이름 있는 볼륨을 붙이고 손대지 않아요. 들어갈 때는 bash 대신 mysql을 열고, 켜졌는지는 curl 대신 logs와 SHOW DATABASES로 봐요. 포트는 80 대신 3306이에요. run, ps, logs, stop, rm, exec, compose는 다 그대로예요. 이미지가 달라지면 옵션만 달라져요.")

# =====================================================================
# part 4: errors
# =====================================================================
o = frame("x-nopw", EB5, "비밀번호 -e를 빠뜨리면 켜지자마자 꺼져요", C5)
nl = RA("nopw-logs")
pa = RA("nopw-ps")
rows = [("$", P_HOME, C("nopw")), short_id("nopw"), ("$", P_HOME, "docker ps -a")] + [("o", l) for l in pa] + [("$", P_HOME, "docker logs db"), ("d", "…")] + [("e" if "ERROR" in l else "o", short_log(l) if "ERROR" in l else l) for l in nl if "ERROR" in l or l.startswith("    ")]
t = Term(rows, 96, 214, size=24, w=1728, lh=1.6, tid="t-nopw")
o.append(t.html())
xi = [i for i, r in enumerate(t.rows) if "Exited (1)" in r[1]][0]
o.append(underline(1, round(t.sx(xi, "Exited")), round(t.sx(xi, "Exited") + t.sw("Exited (1) 3 seconds ago")), round(t.top(xi) + t.lp - 4), RED))
mi = [i for i, r in enumerate(t.rows) if "MYSQL_ROOT_PASSWORD" in r[1]][0]
t2 = None
o.append(pen_box(2, round(t.tx - 8), round(t.top(mi - 1) - 2), round(t.sw("You need to specify one of the following as an environment variable:") + 24), round(t.lp * 2 + 4), RED))
yb = t.y + t.h + 44
o.append(p(f"position:absolute;left:96px;top:{yb}px;width:1728px;font-size:30px;font-weight:700;line-height:1.5;color:{INK}", "<span style=\"font-family:" + MONO + "\">docker rm db</span>로 꺼진 컨테이너를 지우고, -e MYSQL_ROOT_PASSWORD를 붙여 다시 켜요.", bi("fade", 3)))
W("x-nopw", o, "비밀번호 -e를 빠뜨리면 켜지자마자 꺼져요. docker run은 컨테이너 ID를 찍고 끝나서 잘 켜진 것처럼 보여요. 그런데 docker ps -a로 보면 STATUS가 Exited (1)이에요. 몇 초 만에 꺼진 거예요. docker logs db로 이유를 보면, 데이터베이스를 처음 만드는데 비밀번호 옵션이 없다고 나와요. 아래 세 이름 중 하나를 환경 변수로 달라는 뜻이에요. 우리는 MYSQL_ROOT_PASSWORD를 써요. 꺼진 컨테이너도 이름 db를 차지하고 있어서, 29에서 배운 대로 docker rm db로 먼저 지우고 다시 켜요." + REAL, ("p5", "자주 나는 오류"))

o = frame("x-early", EB5, "켜지자마자 들어가면 아직 준비 중이라 접속이 안 돼요", C5)
eo = RA("early", wrap=True)
rows = [("$", P_HOME, RUNC), short_id("run"), ("$", P_HOME, "docker exec -it db mysql -u root -p"), ("o", "Enter password:")] + [("e", l) for l in eo if l.startswith("ERROR")]
t = Term(rows, 96, 214, size=24, w=1728, lh=1.6, tid="t-early")
o.append(t.html())
ei = len(t.rows) - 1
o.append(underline(1, round(t.sx(ei, "Can't connect")), round(t.end(ei)), round(t.top(ei) + t.lp - 4), RED))
yb = t.y + t.h + 50
o.append(p(f"position:absolute;left:96px;top:{yb}px;width:1000px;font-size:30px;font-weight:700;line-height:1.55;color:{INK}", "ERROR 2002는 MySQL 서버를 못 찾았다는 뜻이에요. 처음 켤 때 10초쯤 준비하는 동안 나와요.", bi("fade", 2)))
o.append(p(f"position:absolute;left:96px;top:{yb + 120}px;width:1000px;font-size:28px;line-height:1.6;color:{SUB}", "docker logs db에서 마지막 ready for connections 줄에 port: 3306이 보일 때 다시 들어가요.", bi("fade", 2)))
o.append(addr(1200, yb + 6, "port: 3306", GR, 3, size=34, anim="pop"))
o.append(p(f"position:absolute;left:1200px;top:{yb + 96}px;width:624px;font-size:26px;line-height:1.6;color:{SUB}", "port: 0이 나온 줄은 임시 서버라서 아직이에요.", bi("fade", 3)))
W("x-early", o, "켜지자마자 들어가면 아직 준비 중이라 접속이 안 돼요. docker run 바로 뒤에 docker exec로 들어가면 ERROR 2002가 나와요. 컨테이너 안의 MySQL 서버를 찾지 못했다는 뜻이에요. 1파트에서 본 것처럼 처음 켤 때는 데이터 파일을 만들고 임시 서버로 준비하느라 10초쯤 걸려요. 그동안에는 서버가 없거나 꺼졌다 켜지는 중이에요. docker logs db를 보고 port: 3306이 찍힌 줄이 나오면 다시 들어가요. port: 0이 나온 줄은 임시 서버라서 아직이에요. 볼륨에 이미 데이터가 있으면 준비가 짧아서 몇 초면 돼요." + REAL)

o = frame("x-auth", EB5, "비밀번호를 잘못 치면 Access denied가 나와요", C5)
wo = RA("wrongpw", wrap=True)
rows = [("$", P_HOME, "docker exec -it db mysql -u root -p"), ("o", "Enter password:")] + [("e", l) for l in wo if l.startswith("ERROR")]
t = Term(rows, 96, 214, size=28, w=1728, lh=1.6, tid="t-auth")
o.append(t.html())
o.append(underline(1, round(t.sx(2, "Access denied")), round(t.end(2)), round(t.top(2) + t.lp - 4), RED))
o += tag(t, 1, "cafe123을 쳤어요. 4가 빠졌어요", GRAY, 1)
yb = t.y + t.h + 60
tips = [("화면에 안 보여서 잘못 치기 쉬워요", "천천히 다시 쳐요"), ("using password: YES", "비밀번호를 받긴 했는데 틀렸다는 뜻이에요"), ("기억이 안 나면", "docker exec db env로 MYSQL_ROOT_PASSWORD를 봐요")]
for k, (a_, b_) in enumerate(tips):
    y = yb + k * 110
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:1px;background:{LINE}"></div>')
    mono = a_.startswith("using")
    o.append(p(f"position:absolute;left:96px;top:{y + 30}px;width:760px;{'font-family:' + MONO + ';font-size:28px;' if mono else 'font-size:30px;'}font-weight:700;color:{INK};white-space:nowrap", e(a_), bi("rise", 2) + DELAY(k * 80)))
    o.append(p(f"position:absolute;left:900px;top:{y + 32}px;width:924px;font-size:28px;color:{SUB};white-space:nowrap", e(b_).replace("docker exec db env", f'<b style="font-family:{MONO};color:{INK}">docker exec db env</b>'), bi("rise", 2) + DELAY(k * 80)))
W("x-auth", o, "비밀번호를 잘못 치면 Access denied가 나와요. 이번에는 cafe1234 대신 cafe123을 쳤어요. 비밀번호는 쳐도 화면에 안 보여서 하나 빠뜨려도 모르고 넘어가기 쉬워요. 메시지 끝의 using password: YES는 비밀번호를 받긴 했는데 맞지 않았다는 뜻이에요. 천천히 다시 치면 돼요. 정한 비밀번호가 기억나지 않으면 1파트에서 본 docker exec db env로 MYSQL_ROOT_PASSWORD 값을 확인해요. 볼륨을 붙였다면 다음다음 장의 함정도 같이 봐요." + REAL)

o = frame("x-port", EB5, "3306번을 이미 쓰고 있으면 3307:3306으로 바꿔요", C5)
po = rewrap(RA("port"), 132)
rows = [("$", P_HOME, C("port").replace("MYSQL_ROOT_PASSWORD=x", "MYSQL_ROOT_PASSWORD=x"))] + [("e" if l.startswith("docker:") or "Bind" in l or l.startswith("(") else "o", l) for l in po]
t = Term(rows, 96, 214, size=20, w=1728, lh=1.6, tid="t-port")
o.append(t.html())
bi_ = [i for i, r in enumerate(t.rows) if "Bind for" in r[1]][0]
o.append(underline(1, round(t.sx(bi_, "Bind for")), round(min(t.end(bi_), t.sx(bi_, "Bind for") + t.sw("Bind for 0.0.0.0:3306 failed: port is already allocated"))), round(t.top(bi_) + t.lp - 3), RED))
yb = t.y + t.h + 50
o.append(p(f"position:absolute;left:96px;top:{yb}px;width:1728px;font-size:30px;font-weight:700;line-height:1.5;color:{INK}", "앞의 db가 3306번을 쓰는 중이라 db2가 못 켜졌어요. 내 컴퓨터에 MySQL을 직접 설치해 둬도 같은 오류가 나요.", bi("fade", 2)))
py_ = yb + 110
o.append(p(f"position:absolute;left:96px;top:{py_}px;font-family:{MONO};font-size:52px;font-weight:700;line-height:1.3;white-space:pre", f'<span style="color:{GRAY}">-p </span><span id="xp-a" style="color:{GR}">3307</span><span style="color:{GRAY}">:</span><span style="color:{MY}">3306</span>'))
m1 = 96 + tw("-p ", 52) + tw("3307", 52) / 2
m2 = 96 + tw("-p 3307:", 52) + tw("3306", 52) / 2
for mx, dy, lab_, c_ in [(m1, 84, "내 컴퓨터 쪽만 바꿔요", GR), (m2, 34, "컨테이너 안 MySQL은 그대로", MY)]:
    o.append(f'<div{bi("fade", 3)} style="position:absolute;left:{mx - 1:.0f}px;top:{py_ + 72}px;width:2px;height:{dy}px;background:{c_}"></div>')
    o.append(p(f"position:absolute;left:{mx - 14:.0f}px;top:{py_ + 72 + dy + 8}px;font-size:24px;font-weight:700;line-height:1.35;color:{c_};white-space:nowrap", lab_, bi("pop", 3)))
o.append(p(f"position:absolute;left:1000px;top:{yb + 120}px;width:824px;font-size:28px;line-height:1.6;color:{SUB}", "먼저 docker ps로 3306번을 쓰는 컨테이너가 있는지 보고, 안 쓰는 것이면 꺼요.", bi("fade", 3)))
W("x-port", o, "29에서 본 포트 겹침이 3306번에서도 나요. 앞의 db가 3306번을 쓰는 중에 db2를 같은 포트로 켜려고 하니 port is already allocated가 나왔어요. 이미 MySQL을 컴퓨터에 직접 설치해 둔 사람도 같은 오류를 만나요. 설치한 MySQL이 3306번을 쓰고 있어서예요. 먼저 docker ps로 3306번을 쓰는 컨테이너가 있는지 보고 안 쓰는 것이면 꺼요. 둘 다 써야 하면 -p 3307:3306처럼 앞쪽, 내 컴퓨터 쪽 번호만 바꿔요. 컨테이너 안의 MySQL은 그대로 3306에서 기다려요. 긴 오류 줄은 화면 폭에 맞춰 줄만 바꿨어요." + REAL)

o = frame("x-sql", EB5, "SQL을 칠 때 자주 하는 실수 두 가지예요", C5)
sm = sess_rows("semi")
sm_rows = [r for r in sm if r[0] == "m"] + [r for r in sm if r[0] != "m"][:3] + [("d", "…")]
ta = Term(sm_rows[:2] + [r for r in sm if r[0] != "m"][1:4] + [("d", "…")], 96, 290, size=26, w=844, lh=1.6, tid="t-semi")
o.append(p(f"position:absolute;left:96px;top:226px;font-size:30px;font-weight:700;color:{RED}", "1  끝에 ;를 빠뜨렸어요"))
ta.band(1, order=1, color="rgba(240,122,114,.2)")
o.append(ta.html())
o += tag(ta, 1, "아직 안 끝났대요", RED, 1, at=ta.x + 200)
o.append(p(f"position:absolute;left:96px;top:{ta.y + ta.h + 24}px;width:844px;font-size:27px;line-height:1.6;color:{SUB}", "<span style=\"font-family:" + MONO + ";font-weight:700;color:" + INK + "\">-&gt;</span>가 나오면 ;만 치고 Enter를 눌러요.", bi("fade", 1)))
ty = sess_rows("typo")
tb = Term(ty[:1] + [("e", l) for l in rewrap([r[1] for r in ty[1:] if r[0] == "e"], 52)], 980, 290, size=26, w=844, lh=1.6, tid="t-typo", attrs=bi("rise", 2))
o.append(p(f"position:absolute;left:980px;top:226px;font-size:30px;font-weight:700;color:{RED}", "2  표 이름을 잘못 썼어요", bi("rise", 2)))
o.append(tb.html())
W("x-sql", o, "SQL을 칠 때 자주 하는 실수 두 가지예요. 첫째, 끝의 세미콜론을 빠뜨리면 Enter를 쳐도 실행되지 않고 화살표 표시가 나와요. 아직 문장이 안 끝났으니 더 치라는 뜻이에요. 세미콜론만 치고 Enter를 누르면 실행돼요. 둘째, 표 이름 orders를 order로 잘못 쓰면 ERROR 1064가 나와요. order는 SQL에서 정렬할 때 쓰는 낱말이라 문법이 틀렸다고 해요. near 뒤에 적힌 곳 근처를 보면 돼요. 32에서 본 같은 id 넣기, 수량에 글자 넣기도 이렇게 ERROR 번호와 이유가 나와요." + REAL)

o = frame("x-trap", EB5, "볼륨이 남아 있으면 바꾼 비밀번호가 적용되지 않아요", C5)
rows = [("$", P_HOME, C("trap-run"), {"new5678": f'style="color:{OR}"'}), short_id("trap-run"), ("$", P_HOME, "docker exec -it db mysql -u root -p"), ("o", "Enter password:")] + [("e", l) for l in RA("trap", wrap=True) if l.startswith("ERROR")]
t = Term(rows, 96, 214, size=20, w=1728, lh=1.6, tid="t-trap")
o.append(t.html())
o += tag(t, 3, "new5678을 쳤어요", GRAY, 1)
o.append(underline(1, round(t.sx(4, "Access denied")), round(t.end(4)), round(t.top(4) + t.lp - 3), RED))
yb = t.y + t.h + 40
tl = [short_log(l) for l in RA("trap-logs") if "[Entrypoint]" in l]
t2 = Term([("$", P_HOME, "docker logs db"), ] + [("o", l) for l in tl] + [("d", "…")], 96, yb, size=20, w=1000, lh=1.6, tid="t-trap2", attrs=bi("rise", 2))
o.append(t2.html())
o.append(p(f"position:absolute;left:{t2.x + t2.w + 50}px;top:{yb}px;width:{1824 - t2.x - t2.w - 50}px;font-size:27px;line-height:1.6;color:{SUB}", "Initializing, Creating database 줄이 없어요. 볼륨에 이미 데이터가 있어서 처음 준비를 건너뛰었어요.", bi("fade", 2)))
yc = t2.y + t2.h + 44
fx = [("예전 비밀번호 cafe1234로 들어가요", GR, "표가 그대로 있어요"), ("처음부터 다시: docker volume rm cafe-data", RED, "표도 같이 지워져요")]
for k, (a_, c_, b_) in enumerate(fx):
    x = 96 + k * 884
    o.append(f'<div{bi("rise", 3) + DELAY(k * 120)} style="position:absolute;left:{x}px;top:{yc}px;width:844px;box-sizing:border-box;padding:22px 28px;background:{CARD};border:2px solid {LINE};border-left:8px solid {c_};border-radius:14px">'
             + p(f"font-size:27px;font-weight:700;color:{INK};white-space:nowrap", e(a_).replace("docker volume rm cafe-data", f'<span style="font-family:{MONO}">docker volume rm cafe-data</span>'))
             + p(f"margin-top:6px;font-size:24px;color:{c_}", e(b_)) + '</div>')
W("x-trap", o, "볼륨이 남아 있으면 바꾼 비밀번호가 적용되지 않아요. 오류 메시지만 보면 원인을 찾기 어려운 함정이에요. 컨테이너를 지우고 -e로 새 비밀번호 new5678을 줘서 다시 켰어요. 그런데 cafe-data 볼륨은 그대로 붙였어요. 새 비밀번호로 들어가면 Access denied가 나와요. logs를 보면 처음 준비 단계 줄이 하나도 없어요. MySQL은 볼륨에 이미 데이터가 있으면 -e의 비밀번호와 데이터베이스 이름을 읽지 않고 건너뛰어요. 비밀번호도 예전 그대로예요. 예전 비밀번호로 들어가면 표가 그대로 있어요. 정말 처음부터 다시 하고 싶을 때만 docker volume rm으로 볼륨을 지워요. 그러면 표도 같이 지워져요." + REAL)

# =====================================================================
# part 6: real tasks
# =====================================================================
o = frame("e-day", EB6, "예제 1 · 오늘 문을 닫고 내일 열어도 어제 주문이 남아요", C6)
cs = sess_rows("c-sql")
cs_ins = [r for r in cs if r[0] == "m" and r[2].startswith("INSERT")]
rows_a = [("$", P_DB, "docker compose up -d"), ("d", "…"), ("$", P_DB, "docker compose exec db mysql -u root -p cafe"), ("d", "…"), ("m", "mysql>", "CREATE TABLE orders (…);")] + cs_ins + [("m", "mysql>", "exit"), ("$", P_DB, "docker compose down"), ("d", "…")]
ta = Term(rows_a, 96, 270, size=19, w=850, lh=1.6, tid="t-day1")
o.append(p(f"position:absolute;left:96px;top:214px;font-size:30px;font-weight:700;color:{GRAY}", "월요일"))
o.append(ta.html())
ck_ = sess_rows("c-kept")
rows_b = [("$", P_DB, "docker compose up -d"), ("d", "…"), ("$", P_DB, "docker compose exec db mysql -u root -p cafe"), ("d", "…")] + ck_[1:]
tb = Term(rows_b, 974, 270, size=19, w=850, lh=1.6, tid="t-day2", attrs=bi("rise", 1))
o.append(p(f"position:absolute;left:974px;top:214px;font-size:30px;font-weight:700;color:{C6}", "화요일", bi("rise", 1)))
li = [i for i, r in enumerate(tb.rows) if "| latte" in r[1]][0]
tb.band(li, li + 1, order=2, color="rgba(242,196,109,.2)")
tb.band(li + 2, order=3, color="rgba(127,209,139,.22)")
o.append(tb.html())
o += tag(tb, li, "월요일 주문", OR, 2, at=tb.x + 420)
o += tag(tb, li + 2, "오늘 주문", GR, 3, at=tb.x + 420)
o.append(caption("down은 컨테이너만 지우고 볼륨 cafe-db_cafe-data는 남겨 둬요.", max(ta.y + ta.h, tb.y + tb.h) + 40, 4, size=30))
W("e-day", o, "예제 1이에요. compose로 켠 카페 DB에 월요일 주문 두 개를 넣고, 가게 문을 닫듯 docker compose down으로 껐어요. 화요일에 다시 up -d로 켜고 오늘 주문 하나를 더 넣은 뒤 SELECT를 쳤어요. 월요일 주문 두 개 아래에 오늘 주문이 붙어서 세 행이 나와요. down은 컨테이너와 네트워크만 지우고 볼륨은 남겨 둬요. 그래서 compose.yaml에 볼륨만 적어 두면 매일 껐다 켜도 데이터가 이어져요. 터미널은 앞에서 본 출력과 CREATE TABLE의 열 목록을 …로 줄였어요." + REAL, ("p6", "실제 상황 예제"))

o = frame("e-init", EB6, "예제 2 · 처음 켤 때 메뉴 표를 SQL 파일로 채워요", C6)
ml = MENU_SQL.rstrip("\n").split("\n")
ed, g = editor("ei-sql", "~/cafe-db/init/menu.sql", ml, 96, 214, 1080, fs=20, color=C6, nums=False)
o.append(ed)
ci_ = COMPOSE_INIT.rstrip("\n").split("\n")
vix = [i for i, l in enumerate(ci_) if "initdb" in l][0]
ed2, g2 = editor("ei-yaml", "compose.yaml", [yaml_html(l) for l in ci_[vix - 2:vix + 1]], 1220, 214, 604, fs=20, color=GR, nums=False)
o.append(ed2)
o.append(lband(1, g2, 2, 1, C6))
yb = max(g["top"] + g["h"], g2["top"] + g2["h"]) + 30
o.append(p(f"position:absolute;left:1220px;top:{yb + 300}px;width:604px;font-size:24px;line-height:1.6;color:{SUB}", "./init 폴더의 .sql 파일은 볼륨이 빈 채로 처음 켤 때 한 번만 실행돼요.", bi("fade", 1)))
il = [l for l in RA("i-logs") if "running /docker-entrypoint-initdb.d" in l]
isq = sess_rows("i-sql")
rows = [("$", P_DB, "docker compose down -v", {"-v": f'style="color:{RED}"'}), ("d", "…"), ("$", P_DB, "docker compose up -d"), ("d", "…"), ("$", P_DB, "docker compose logs db"), ("d", "…")] + [("o", "… " + l[l.index("/usr/local/bin"):]) for l in il] + [("d", "…"), ("$", P_DB, "docker compose exec db mysql -u root -p cafe"), ("d", "…")] + isq[1:]
t = Term(rows, 96, yb, size=17, w=1080, lh=1.35, tid="t-init")
t.band(0, order=2, color="rgba(240,122,114,.2)")
t.band(6, order=3, color="rgba(242,196,109,.2)")
o.append(t.html())
o += tag(t, 0, "볼륨까지 지워요", RED, 2, at=t.x + 500)
o.append(f'<div{bi("rise", 2)} style="position:absolute;left:1220px;top:{yb}px;width:604px;box-sizing:border-box;padding:24px 28px;background:#FBE9E7;border-left:8px solid {RED};border-radius:14px">'
         + p(f"font-size:25px;font-weight:700;line-height:1.5;color:{RED}", "볼륨이 남아 있으면 안 돌아요")
         + p(f"margin-top:8px;font-size:23px;line-height:1.6;color:{INK}", "예제 1의 볼륨에서 up만 했더니 SHOW TABLES;에 orders만 있었어요. 그래서 down -v로 볼륨을 지우고 켰어요. 쌓인 주문도 같이 지워져요.") + '</div>')
o.append(p(f"position:absolute;left:1220px;top:{yb + 420}px;width:604px;font-size:24px;line-height:1.6;color:{SUB}", "새 팀원도 git clone 뒤 up -d 한 번이면 같은 메뉴 표를 받아요.", bi("fade", 4)))
W("e-init", o, "예제 2예요. 새로 켤 때마다 메뉴 표를 손으로 만들기 번거로워서 SQL 파일로 적어 뒀어요. init 폴더의 menu.sql에 CREATE TABLE과 INSERT 세 줄을 적었어요. compose.yaml의 volumes에 ./init 폴더를 /docker-entrypoint-initdb.d에 연결하는 줄을 더해요. mysql 이미지는 처음 켤 때 이 폴더의 .sql 파일을 한 번 실행해 줘요. 주의할 점이 있어요. 앞 장의 함정처럼 볼륨에 데이터가 이미 있으면 처음 준비를 건너뛰어서 이 파일도 안 돌아요. 실제로 예제 1의 볼륨으로 켰더니 표가 orders뿐이었어요. 그래서 docker compose down -v로 볼륨까지 지우고 다시 켰어요. -v를 붙이면 쌓인 주문도 같이 지워지니 연습할 때만 써요. logs에 menu.sql을 실행했다는 줄이 보이고, SELECT로 메뉴 세 개가 나와요. 이 폴더를 GitHub에 올려 두면 새 팀원도 up -d 한 번으로 같은 메뉴 표를 받아요." + REAL)

# =====================================================================
# wrap-up
# =====================================================================
o = frame("trouble", "정리", "막히면 이렇게 풀어요", RED)
tr = [("Exited (1) · You need to specify …", "비밀번호 -e를 빠뜨렸어요", "docker rm 뒤 -e를 붙여 다시"),
      ("ERROR 2002 · Can't connect", "서버가 아직 준비 중이에요", "logs에서 port: 3306 보기"),
      ("ERROR 1045 · Access denied", "비밀번호가 틀렸어요", "천천히 다시, 볼륨 함정 확인"),
      ("port is already allocated", "3306번을 다른 것이 써요", "\"3307:3306\"으로 바꾸기"),
      ("->  · ERROR 1064", "; 빠짐, SQL 문법 오류", "; 치기, near 뒤를 보기"),
      ("ERROR 1146 · doesn't exist", "표가 없어요. 볼륨 없이 지웠나요", "-v 이름:/var/lib/mysql")]
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
W("trouble", o, "오늘 만난 오류를 모았어요. 컨테이너가 바로 꺼지면 docker ps -a와 docker logs부터 봐요. 접속이 안 되면 서버가 준비됐는지, 비밀번호가 맞는지 차례로 봐요. 바꾼 비밀번호가 안 먹으면 볼륨에 예전 데이터가 남아 있는지 생각해요. SQL에서 화살표가 나오면 세미콜론을 치고, ERROR 번호 뒤의 설명과 near 뒤의 위치를 읽어요. 표가 사라졌다면 볼륨 없이 컨테이너를 지운 거예요.", ("trouble", "정리"))

o = frame("cheatsheet", "정리", "한 장 요약", INK)
groups = [("켜고 들어가기", DK, [("-e MYSQL_ROOT_PASSWORD=…", "비밀번호 · 꼭"), ("-e MYSQL_DATABASE=cafe", "처음 만들 데이터베이스"), ("docker logs db", "port: 3306이면 준비 끝"), ("docker exec -it db mysql -u root -p cafe", "접속, 나올 땐 exit")]),
          ("SQL", MAG, [("CREATE DATABASE shop; · USE shop;", "데이터베이스 만들고 들어가기"), ("CREATE TABLE 표 (열 타입, …);", "빈 표 · SHOW TABLES, DESCRIBE로 확인"), ("INSERT INTO 표 VALUES (…);", "행 넣기 · SELECT로 꺼내기"), ("DROP TABLE 표; · DROP DATABASE 이름;", "지우기 · 되돌릴 수 없어요")]),
          ("남기기", GR, [("-v cafe-data:/var/lib/mysql", "지워도 남는 표"), ("compose.yaml environment", "-e 자리"), ("docker compose down", "볼륨은 남겨요"), ("docker compose down -v", "볼륨까지 지워요 · 연습할 때만")])]
for i, (t_, c, rows) in enumerate(groups):
    x = 96 + i * 600
    o.append(p(f"position:absolute;left:{x}px;top:220px;font-size:30px;font-weight:700;color:{c}", e(t_)))
    o.append(f'<div style="position:absolute;left:{x}px;top:270px;width:540px;height:3px;background:{c}"></div>')
    for j, (k, d_) in enumerate(rows):
        y = 296 + j * 120
        fs = 23 if tw(k, 23) <= 560 else 19
        o.append(p(f"position:absolute;left:{x}px;top:{y}px;width:560px;font-family:{MONO};font-size:{fs}px;font-weight:700;color:{INK};white-space:nowrap", e(k)))
        o.append(p(f"position:absolute;left:{x}px;top:{y + 42}px;width:540px;font-size:23px;color:{SUB}", e(d_)))
o.append(caption("데이터베이스는 이미지 하나, 환경 변수 몇 개, 볼륨 하나로 켜고 지켜요.", 820, None, size=32))
o.append(caption("34에서는 같은 순서로 PostgreSQL을 켜고 둘을 비교해요.", 880, None, size=28, color=SUB))
W("cheatsheet", o, "오늘 쓴 것을 세 묶음으로 모았어요. MySQL 컨테이너는 -e로 비밀번호와 데이터베이스 이름을 건네서 켜고, logs에서 port: 3306을 확인한 뒤 exec로 들어가요. SQL은 데이터베이스를 만들고 들어가는 CREATE DATABASE와 USE, 표를 만들고 확인하는 CREATE TABLE, SHOW TABLES, DESCRIBE, 넣고 꺼내는 INSERT와 SELECT, 지우는 DROP을 쳐 봤어요. 앱에는 MYSQL_USER로 만든 계정을 줘요. 데이터를 남기려면 /var/lib/mysql에 이름 있는 볼륨을 붙이고, compose.yaml에 적어 두면 껐다 켜도 이어져요. 34에서는 같은 순서로 PostgreSQL을 켜 봐요.")

# =====================================================================
# toc
# =====================================================================
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
plist = [(DK, "MySQL 컨테이너 켜기", "공식 이미지, -e 환경 변수, logs, exec로 접속", "r-pull", "r-enter"),
         (MAG, "데이터베이스와 표 만들기", "CREATE DATABASE, USE, CREATE TABLE, DESCRIBE, INSERT, SELECT, DROP", "s-show", "s-drop"),
         (TEAL, "계정과 접속 방법", "root와 앱 계정, bash로 들어가기, -e로 한 문장만", "u-user", "u-one"),
         (GR, "볼륨과 compose", "지우면 날아가는 표, /var/lib/mysql에 볼륨, compose.yaml", "v-gone", "cmp"),
         (RED, "자주 나는 오류", "비밀번호, 준비 중, 포트 겹침, SQL 실수, 볼륨 함정", "x-nopw", "x-trap"),
         (OR, "실제 상황 예제", "다음 날에도 남는 주문, SQL 파일로 메뉴 채우기", "e-day", "e-init")]
o = frame("toc", "", "오늘의 순서", INK)
for i, (c, h, s_, a, b) in enumerate(plist):
    y = 214 + i * 112
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:1px;background:{LINE}"></div>')
    o.append(p(f"position:absolute;left:96px;top:{y + 18}px;width:80px;font-size:48px;font-weight:900;line-height:1.5;color:{c}", str(i + 1)))
    o.append(p(f"position:absolute;left:200px;top:{y + 16}px;font-size:34px;font-weight:700;color:{INK}", h))
    o.append(p(f"position:absolute;left:200px;top:{y + 66}px;font-size:23px;color:{SUB}", e(s_)))
    o.append(p(f"position:absolute;left:1524px;top:{y + 36}px;width:300px;text-align:right;font-size:28px;font-weight:700;color:{GRAY}", f"{page[a]}–{page[b]}쪽"))
o.append(f'<div style="position:absolute;left:96px;top:{214 + 6 * 112}px;width:1728px;height:1px;background:{LINE}"></div>')
o.append(p(f"position:absolute;left:96px;top:{214 + 6 * 112 + 34}px;font-size:26px;color:{SUB}", f"{page['why']}–{page['big']}쪽은 들어가기, {page['trouble']}–{page['cheatsheet']}쪽은 막힐 때와 한 장 요약이에요."))
o = [x for x in o if 'id="eyebrow"' not in x]
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(o) + f"\n<aside>{e('여섯 파트로 나눴어요. 1파트에서 MySQL을 컨테이너로 켜고 들어가요. 2파트에서 데이터베이스와 표를 직접 만들고, 넣고, 꺼내고, 지워요. 3파트에서 root와 앱 계정, 여러 접속 방법을 봐요. 4파트에서 컨테이너를 지우면 표가 날아가는 걸 보고 볼륨으로 지켜요. 5파트는 자주 나는 오류, 6파트에서 앞의 것을 섞은 예제 두 개를 풀어요.')}</aside>\n</section>\n")

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-12T00:00:00Z"}, "lists": "css", "title": "Docker 3 (MySQL 컨테이너)", "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
for w_ in WARN:
    print("WARN", w_)
print(len(ORDER), "slides")
