r"""Generates every slide of the 44 deck (Python and PostgreSQL with psycopg) and slides/deck.json.

Story: a course list read in psql is for a person's eyes; a Python program (the class's sign-up app, main.py) has to
send the SQL itself and get the rows back as values. psycopg is the driver between them: a DSN says where to connect,
conn.execute sends a statement, fetchall/fetchone give tuples (dict_row gives dictionaries), %s places take values
safely (an f-string pasted into SQL changes the statement: SQL injection), and a with block saves (commit) when it
ends and throws everything away (rollback) when an error stops it. Part 1 setup and connecting, part 2 getting rows,
part 3 %s, part 4 the class TODO (fee lookup and sign-up INSERT) and when changes are saved, part 5 psql comparison and
errors, part 6 three real cases on the shared sports-center data of 38-41.

Every terminal line comes from tools/demo.py (real Docker postgres:18, uv and psycopg 3; saved in tools/out.json). The
programs are tools/src/*.py, copied to ~/sports-app/main.py and run with `uv run main.py`.
Usage (in 44-python-postgres): python3 tools/gen.py slides
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
# chapter 41 helpers
# =====================================================================
MY, VO = "#00758F", "#B26A00"
EB1, EB2, EB3, EB4, EB5, EB6 = "1. 값 하나와 비교하기", "2. 목록과 IN", "3. FROM에 넣는 임시 표", "4. SELECT 칸에 넣기", "5. 비교하고 속 들여다보기", "6. 오류와 실제 상황"
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


# =====================================================================
# chapter 44 helpers
# =====================================================================
REAL = " 실행 화면은 tools/demo.py로 실제 PostgreSQL 18과 psycopg 3을 실행해서 옮긴 결과예요."
EB = ["1. 준비하고 접속하기", "2. 결과 꺼내기", "3. %s로 값 넣기", "4. 저장되는 순간", "5. 비교와 오류", "6. 실제 상황"]
CP = [BL, TEAL, OR, GR, RED, MAG]
PYB = "#3572A5"                       # Python's blue
SQLK = "#2459C9"
STR = "#1F7A3C"
COM = "#8A8F99"
PCT = "#B26A00"
SRCD = os.path.join(HERE, "src")
KW = {"import", "from", "with", "as", "def", "for", "in", "if", "not", "return", "None", "True", "False", "and", "or"}
SQLW = {"SELECT", "FROM", "JOIN", "LEFT", "ON", "WHERE", "ORDER", "BY", "GROUP", "AND", "INSERT", "INTO", "VALUES", "AS",
        "MAX", "COUNT", "BETWEEN", "UPDATE", "SET", "DESC", "LIMIT"}


def src(name, a=1, b=None):
    ls = open(os.path.join(SRCD, name + ".py")).read().rstrip("\n").split("\n")
    return ls[a - 1:b]


def _segs_sql(t):
    out = []
    for m in re.finditer(r"%s|'[^']*'|[A-Za-z_]+|\s+|.", t):
        w = m.group(0)
        if w == "%s":
            out.append((w, f"color:{PCT};font-weight:700"))
        elif w.startswith("'"):
            out.append((w, f"color:{STR}"))
        elif w in SQLW:
            out.append((w, f"color:{SQLK};font-weight:700"))
        else:
            out.append((w, ""))
    return out


def _segs_py(t):
    out = []
    pat = re.compile(r'#.*$|f?"""|f?"[^"]*"|f?\'[^\']*\'|[A-Za-z_][A-Za-z_0-9]*|\d[\d_]*|\s+|.')
    for m in pat.finditer(t):
        w = m.group(0)
        if w.startswith("#"):
            out.append((w, f"color:{COM}"))
        elif w.startswith('"') or w.startswith("'") or w.startswith('f"') or w.startswith("f'"):
            if "%s" in w:
                for k, part in enumerate(w.split("%s")):
                    if k:
                        out.append(("%s", f"color:{PCT};font-weight:700"))
                    if part:
                        out.append((part, f"color:{STR}"))
            else:
                out.append((w, f"color:{STR}"))
        elif w in KW:
            out.append((w, f"color:#0F4C9C;font-weight:700"))
        elif re.match(r"\d", w):
            out.append((w, f"color:{PCT}"))
        else:
            out.append((w, ""))
    return out


def _emit(segs, marks):
    """segs: [(text, style)]; marks: {substring: attrs or id} wrapped around that part of the plain line"""
    chars = [(c, st) for t, st in segs for c in t]
    plain = "".join(c for c, _ in chars)
    mk = [-1] * len(plain)
    attrs_ = []
    for k, v in (marks or {}).items():
        last = k.startswith("…")
        k2 = k[1:] if last else k
        at = plain.rfind(k2) if last else plain.find(k2)
        if at < 0:
            WARN.append(f"mark '{k2}' not in '{plain[:40]}'")
            continue
        attrs_.append(v if "=" in v else f'id="{v}"')
        for j in range(at, at + len(k2)):
            mk[j] = len(attrs_) - 1

    def run_html(i, j):
        h, a = "", i
        while a < j:
            b = a
            while b < j and chars[b][1] == chars[a][1]:
                b += 1
            t = e("".join(c for c, _ in chars[a:b]))
            h += f'<span style="{chars[a][1]}">{t}</span>' if chars[a][1] else t
            a = b
        return h

    out, i = "", 0
    while i < len(chars):
        j = i
        while j < len(chars) and mk[j] == mk[i]:
            j += 1
        inner = run_html(i, j)
        out += f'<span {attrs_[mk[i]]}>{inner}</span>' if mk[i] >= 0 else inner
        i = j
    return out or "&#160;"


def pyc(lines, marks=None):
    """python source lines to editor html; triple-quoted SQL blocks are colored as SQL. marks: {line index: {sub: attrs}}"""
    out, in_sql = [], False
    for i, l in enumerate(lines):
        mk = (marks or {}).get(i)
        if in_sql:
            if l.strip().startswith('"""'):
                in_sql = False
                out.append(_emit([(l, f"color:{STR}")], mk))
            else:
                out.append(_emit(_segs_sql(l), mk))
            continue
        if l.rstrip().endswith('"""') and l.count('"""') == 1:
            in_sql = True
        out.append(_emit(_segs_py(l), mk) if l else "")
    return out


def tb_short(lines):
    """keep the traceback frames of main.py and the error; library frames become one … line"""
    out, i, n = [], 0, len(lines)
    while i < n:
        l = lines[i]
        if l.startswith('  File "'):
            mine = "sports-app/main.py" in l
            j = i + 1
            while j < n and lines[j].startswith("    ") and not lines[j].startswith('  File "'):
                j += 1
            if mine:
                out += lines[i:j]
            elif not out or out[-1] != "  …":
                out.append("  …")
            i = j
        else:
            out.append(l)
            i += 1
    return out


ERRL = re.compile(r"^(Traceback|[A-Za-z_.]*(Error|Exception|Column|Datatype)\b|ImportError|ModuleNotFoundError)")


def run_rows(scene, k=0, short=True, cut=None, marks=None, wrap=None):
    ent = D[scene][k]
    rows = [("$", ent["cwd"], ent["cmd"])]
    ls = [l.rstrip() for l in ent["out"]]
    if short:
        ls = tb_short(ls)
    if cut:
        ls = cut(ls)
    if wrap:
        import textwrap
        w2 = []
        for l in ls:
            w2 += textwrap.wrap(l, wrap, subsequent_indent="    ", break_on_hyphens=False) if len(l) > wrap else [l]
        ls = w2
    kind = "o"
    for i, l in enumerate(ls):
        mk = (marks or {}).get(i)
        if ERRL.match(l):
            kind = "e"
        elif l.startswith('  File "') or l.strip() == "…" or re.match(r"^\s*[~^]+\s*$", l):
            kind = "d"
        elif l.startswith("HINT") or l.startswith("LINE ") or (l.strip() == "^"):
            kind = "y"
        elif l.startswith("\t") or l.startswith("Attempts") or l.startswith("- couldn't"):
            kind = "e"
        elif l.startswith("    ") and kind == "e":
            kind = "e"
        else:
            kind = "o"
        rows.append((kind, l) + ((mk,) if mk else ()))
    return rows


def TT(rows, x, y, size=26, w=1728, lh=1.45, tid="t", maxb=990, bar=True, **kw):
    """a terminal whose font shrinks until it ends above maxb and every line fits"""
    while True:
        n = len(WARN)
        t = Term(rows, x, y, size=size, w=w, lh=lh, tid=tid, bar=bar, **kw)
        wide = any(t.tx + t_ * 1.01 > x + t.w - Term.PX for t_ in t.tws)
        if (y + t.h <= maxb and not wide) or size <= 15:
            return t
        del WARN[n:]
        size -= 1


def rr(t, sub, start=0):
    return li(t, sub, start)


def ed(eid, name, lines, x, y, w, fs=24, start=1, marks=None, color=PYB, attrs="", h=None):
    return editor(eid, name, pyc(lines, marks), x, y, w, fs=fs, start=start, color=color, attrs=attrs, h=h)


def gline_x(g, line, sub):
    return g["tx"] + tw(line[:line.index(sub)], g["fs"])


def etag(g, i, line, text, color, order=None, gap=36, size=23, x0=None):
    """a pill after editor line i: dot, short leader, words"""
    x0 = x0 if x0 is not None else g["tx"] + tw(line, g["fs"])
    cy = gcy(g, i)
    pw = tw(text, size, mono=False) + 30
    px = x0 + gap
    if px + pw > g["left"] + g["w"] - 12:
        WARN.append(f"etag '{text}' ends at {px + pw:.0f}, editor ends {g['left'] + g['w']}")
    lc = LC.get(color, color)
    return [f'<div{bi("fade", order)} style="position:absolute;left:{x0 + 10:.0f}px;top:{cy - 5:.0f}px;width:{gap - 10:.0f}px;height:10px">'
            f'<div style="position:absolute;left:0;top:0;width:10px;height:10px;border-radius:5px;background:{lc}"></div>'
            f'<div style="position:absolute;left:10px;top:4px;width:{gap - 20:.0f}px;height:2px;background:{lc}"></div></div>',
            p(f"position:absolute;left:{px:.0f}px;top:{cy - size * 0.85:.0f}px;height:{size * 1.7:.0f}px;padding:0 14px;border-radius:10px;background:{color};font-family:{SANS};font-size:{size}px;font-weight:700;line-height:{size * 1.7:.0f}px;color:#FFFFFF;white-space:nowrap", text, bi("pop", order))]


def ed_spot(g, i, n, order, bg=CARD, bar=BL):
    """line spotlight over editor lines i..i+n-1"""
    return lspot(order, g["left"] + 2, g["top"] + 2 + TABH, g["w"] - 4, g["h"] - TABH - 4, gtop(g, i) - 2, n * g["lh"] + 4, bg=bg, bar=bar)


def label(x, y, text, color=GRAY, size=24, order=None, attrs=""):
    return p(f"position:absolute;left:{x:.0f}px;top:{y:.0f}px;font-size:{size}px;font-weight:700;color:{color};white-space:nowrap", text, bi("rise", order) + attrs)


def fixrow(x, y, bad, good, order, size=26, w=1728, note_=None):
    """a red (before) and green (after) code line with an arrow"""
    o = [p(f"position:absolute;left:{x}px;top:{y}px;font-size:22px;font-weight:700;color:{GR};white-space:nowrap", "고치기", bi("rise", order))]
    o.append(p(f"position:absolute;left:{x + 110}px;top:{y - 6}px;height:{size + 22}px;padding:0 14px;border-radius:10px;background:#FBE9E7;font-family:{MONO};font-size:{size}px;font-weight:700;line-height:{size + 22}px;color:{RED};white-space:nowrap;text-decoration:line-through;text-decoration-thickness:2px", e(bad), bi("rise", order)))
    bx = x + 110 + tw(bad, size) + 28 + 24
    o.append(p(f"position:absolute;left:{bx:.0f}px;top:{y - 4}px;font-size:{size + 4}px;font-weight:700;color:{GRAY}", "→", bi("rise", order)))
    gx_ = bx + 52
    o.append(p(f"position:absolute;left:{gx_:.0f}px;top:{y - 6}px;height:{size + 22}px;padding:0 14px;border-radius:10px;background:#E4F3EA;font-family:{MONO};font-size:{size}px;font-weight:700;line-height:{size + 22}px;color:{GR};white-space:nowrap", e(good), bi("pop", order)))
    end = gx_ + tw(good, size) + 28
    if note_:
        o.append(p(f"position:absolute;left:{end + 24:.0f}px;top:{y}px;font-size:24px;color:{SUB};white-space:nowrap", note_, bi("rise", order)))
        end += 24 + tw(re.sub(r"<[^>]+>", "", note_), 24, mono=False)
    if end > x + w:
        WARN.append(f"fixrow '{good}' ends at {end:.0f}")
    return o


def chipbox(x, y, text, color, bg, size=26, attrs="", mono_=True, order=None, anim="pop"):
    ff = f"font-family:{MONO};" if mono_ else ""
    return p(f"position:absolute;left:{x:.0f}px;top:{y:.0f}px;height:{size + 24}px;padding:0 16px;border-radius:12px;background:{bg};border:2px solid {color};{ff}font-size:{size}px;font-weight:700;line-height:{size + 20}px;color:{color};white-space:nowrap", text, bi(anim, order) + attrs)


# =====================================================================
# cover
# =====================================================================
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px">',
       p("position:absolute;left:128px;top:290px;font-size:28px;font-weight:700;color:#9DC1E6", "KANT AX/AI 엔지니어 트랙 · 44"),
       f'<h1{SLAM(1)} style="position:absolute;left:128px;top:340px;padding-bottom:10px;font-size:84px;font-weight:900;line-height:1.25;color:#F6F5F1">파이썬에서<br>PostgreSQL 쓰기</h1>',
       p("position:absolute;left:128px;top:578px;font-family:" + MONO + ";font-size:40px;font-weight:700;color:#F2C46D", "psycopg"),
       p("position:absolute;left:128px;top:670px;width:700px;font-size:30px;line-height:1.5;color:#BFC6D4", "파이썬이 SQL을 보내고,<br>결과 줄을 값으로 받아요")]
t = TT(run_rows("receipt"), 900, 300, size=26, w=924, tid="cov-term", maxb=840)
cov.append(t.html())
cov.append(shine(2, "cov-term"))
W("cover", cov, "44 챕터는 파이썬 프로그램에서 PostgreSQL을 쓰는 방법이에요. 36부터 41까지는 psql 창에 SQL을 직접 쳤어요. 오늘은 파이썬 파일 안에서 SQL을 보내고, 돌아온 결과를 파이썬 값으로 받아서 써요. 이때 쓰는 라이브러리 이름이 psycopg예요. 오른쪽 화면은 오늘 마지막에 만드는 프로그램이에요. 회원 한 명의 11월 신청 내역을 데이터베이스에서 꺼내서 영수증처럼 찍어요. 예제 데이터는 38부터 쓰는 스포츠 센터 수업 데이터예요." + REAL, ("intro", "들어가기"))

ORDER.append("toc")   # written last, after page numbers are known

# =====================================================================
# why
# =====================================================================
o = frame("why", "들어가기", "psql 화면은 사람이 읽고, 프로그램은 값을 받아 써야 해요", INK)
o.append(label(96, 214, "psql: 사람이 보고 읽는 화면"))
t = PT(P("why"), 96, 262, size=24, w=820, tid="t-why", lh=1.5, maxb=700)
o.append(t.html())
# the app the class is building
AX, AY, AWW = 1040, 214, 784
o.append(label(AX, AY, "수강 신청 프로그램: 값을 받아서 쓰는 쪽", PYB, order=1))
rows_app = [("수영 초급 아침반", "70,000원"), ("수영 초급 저녁반", "70,000원"), ("수영 중급 새벽반", "80,000원")]
inner_ = "".join(
    f'<div style="width:100%;height:84px;flex:none;display:flex;flex-direction:row;align-items:center;gap:20px;border-bottom:2px solid #EEECE6">'
    + p(f"font-size:28px;font-weight:700;color:{INK};white-space:nowrap", nm)
    + p(f"margin-left:auto;font-size:26px;color:{SUB};white-space:nowrap", fee)
    + p(f"height:48px;padding:0 20px;border-radius:10px;background:{PYB};font-size:22px;font-weight:700;line-height:48px;color:#FFFFFF;white-space:nowrap", "신청")
    + '</div>' for nm, fee in rows_app)
o.append(browser(AX, AY + 48, AWW, 420, "11월 수강 신청", inner_, "app", attrs=bi("rise", 1), pad="18px 36px"))
# the gap between them
o.append(harrow(930, 1020, 470, GRAY, 2))
o.append(p(f"position:absolute;left:96px;top:{t.y + t.h + 40}px;width:820px;font-size:28px;line-height:1.5;color:{INK}", "강좌 이름과 수강료를 사람이 보고 옮겨 적으면, 강좌가 바뀔 때마다 다시 옮겨야 해요.", bi("rise", 2)))
o.append(p(f"position:absolute;left:{AX}px;top:720px;width:{AWW}px;font-size:28px;line-height:1.5;color:{INK}", f"프로그램이 직접 {kw('SELECT')}를 보내고, 돌아온 줄을 리스트와 딕셔너리로 받아서 화면을 만들어요.", bi("rise", 3)))
o.append(caption("파이썬과 PostgreSQL 사이를 이어 주는 라이브러리가 psycopg예요.", 900, 4, size=30, color=PYB))
W("why", o, "지금까지는 psql 창에 SELECT를 치고 결과 표를 눈으로 읽었어요. 왼쪽 화면이에요. 그런데 우리가 만들려는 건 오른쪽 같은 수강 신청 프로그램이에요. 강좌 이름과 수강료를 보여 주고, 신청 버튼을 누르면 신청 표에 한 줄을 넣어요. 사람이 psql 결과를 보고 파이썬 코드에 옮겨 적으면, 강좌가 하나 늘거나 수강료가 바뀔 때마다 코드를 고쳐야 해요. 그래서 프로그램이 직접 데이터베이스에 SQL을 보내고, 돌아온 줄을 파이썬 값으로 받아서 써야 해요. 이 둘을 이어 주는 라이브러리가 psycopg예요. 오른쪽 신청 화면은 이해를 돕는 예시 그림이고, 강좌 이름과 수강료는 실제 데이터와 같아요." + REAL)

# =====================================================================
# big picture
# =====================================================================
o = frame("big", "들어가기", "psycopg가 SQL을 보내고 결과 줄을 파이썬 값으로 바꿔 줘요", INK)
NY, NH = 500, 150
DX, DW = 1360, 320
DCX = DX + DW // 2
# old way (quiet): a person with psql, dashed line to the same drum
o.append(label(96, 214, "지금까지", GRAY, 24))
o.append(node(96, 258, 330, 96, "사람", "psql 창에 직접 입력", GRAY, "#F1F0EC", tsize=26, ssize=20))
o.append(svg(f'<path d="M430,306 L{DCX},306 L{DCX},{NY - 40}" fill="none" stroke="#C9CED8" stroke-width="4" stroke-dasharray="10 10"/>' + head_at(DCX, NY - 38, 90, "#C9CED8")))
o.append(p(f"position:absolute;left:470px;top:262px;font-family:{MONO};font-size:22px;font-weight:700;color:{GRAY};white-space:nowrap", "docker exec -it my-pg psql -U postgres -d kant_shop"))
# new way: straight request and answer lines, drawn first so the boxes sit on top
o.append(label(96, 450, "오늘", PYB, 24))
o.append(svg(f'<path id="req" d="M426,{NY + 48} L{DX},{NY + 48}" fill="none" stroke="{OR}" stroke-width="5" stroke-dasharray="2 12" stroke-linecap="round"/>', 2, "draw"))
o.append(svg(f'<path id="ans" d="M{DX},{NY + 104} L426,{NY + 104}" fill="none" stroke="{PYB}" stroke-width="5" stroke-dasharray="2 12" stroke-linecap="round"/>', 3, "draw"))
o.append(node(96, NY, 330, NH, "main.py", "파이썬 프로그램", PYB, "#E9F0F8", nid="n-py", attrs=bi("rise", 1), tsize=32))
o.append(node(620, NY, 330, NH, "psycopg", "가운데서 이어 줘요", OR, "#FBF0DF", nid="n-pg3", attrs=bi("rise", 1) + DELAY(100), tsize=32))
o.append(cyl(DX, NY - 36, DW, 222, "PostgreSQL", "my-pg 컨테이너", PG, PGBG, cid="n-db", attrs=bi("rise", 1) + DELAY(200)))
o.append(p(f"position:absolute;left:{DX + DW + 24}px;top:{NY + 20}px;font-family:{MONO};font-size:22px;font-weight:700;line-height:1.5;color:{PG};white-space:nowrap", "kant_shop<br>courses<br>members …", bi("rise", 1) + DELAY(250)))
o.append(addr(DX + 10, NY + 210, "localhost:5432", INK, order=1, size=24))
o.append(dot(DX, NY + 48, OR, 2, "req"))
o.append(p(f"position:absolute;left:470px;top:{NY - 54}px;font-family:{MONO};font-size:24px;font-weight:700;color:{OR};white-space:nowrap", "① \"SELECT course_name, fee FROM courses\"", bi("rise", 2) + DELAY(300)))
o.append(dot(426, NY + 104, PYB, 3, "ans"))
o.append(p(f"position:absolute;left:96px;top:{NY + NH + 34}px;font-family:{MONO};font-size:24px;font-weight:700;color:{PYB};white-space:nowrap", "③ [('수영 초급 아침반', 70000), ('수영 초급 저녁반', 70000), …]", bi("rise", 3) + DELAY(300)))
o.append(p(f"position:absolute;left:96px;top:{NY + NH + 120}px;width:1728px;font-size:28px;line-height:1.5;color:{SUB}", "① 파이썬이 SQL 문장을 글자로 보내요. ② PostgreSQL이 실행해요. ③ 결과 표가 튜플의 리스트로 돌아와요.", bi("rise", 4)))
o.append(caption("psql과 같은 서버, 같은 5432번 포트예요. 사람 대신 프로그램이 묻는 것만 달라요.", 920, 5, size=30))
W("big", o, "큰 그림이에요. 위쪽 회색 줄이 지금까지 쓰던 방법이에요. 사람이 docker exec로 psql을 열고 SQL을 직접 쳤어요. 아래가 오늘 방법이에요. 파이썬 파일 main.py가 psycopg에게 SQL 문장을 글자로 넘겨요. psycopg는 localhost의 5432번 포트로 PostgreSQL에 접속해서 그 문장을 보내요. PostgreSQL이 실행한 결과 표는 다시 psycopg를 거쳐 파이썬 값으로 돌아와요. 줄 하나가 튜플 하나가 되고, 여러 줄은 리스트로 모여요. 13에서 배운 튜플과 리스트예요. 서버도 데이터도 psql 때와 똑같아요. 사람 대신 프로그램이 묻는 것만 달라요.")

# =====================================================================
# smallest example
# =====================================================================
o = frame("min", "들어가기", "가장 작은 예제: 접속하고, 묻고, 받아요", INK)
L = src("hello")
html_, g = ed("e-min", "main.py", L, 96, 210, 1728, fs=28)
o.append(html_)
o.append(ed_spot(g, 0, 1, 1))
o.append(ed_spot(g, 2, 1, 2))
o.append(ed_spot(g, 4, 1, 3))
o.append(ed_spot(g, 5, 2, 4))
o.append(lspot_off(5))
ny = g["top"] + g["h"] + 26
steps = ["① import psycopg: PostgreSQL에 접속하는 라이브러리를 불러와요", "② DSN: 어느 서버의 어느 데이터베이스에, 누구로 들어갈지 적은 주소예요",
         "③ with psycopg.connect(DSN) as conn: 접속해서 연결에 conn이라는 이름을 붙여요", "④ conn.execute(SQL)로 보내고, .fetchone()으로 결과 한 줄을 받아요"]
o.append(p(f"position:absolute;left:96px;top:{ny}px;width:1728px;font-size:28px;font-weight:700;line-height:1.5;color:{BL}", e(steps[0]), ' id="min-note" data-start="' + e(steps[0]) + '"'))
for k_ in range(1, 4):
    o.append(set_text(k_ + 1, "min-note", steps[k_]))
o.append(set_text(5, "min-note", "실행은 uv run main.py예요. 튜플 하나가 돌아왔어요"))
t = TT(run_rows("hello"), 96, ny + 70, size=30, w=1728, tid="t-min", maxb=990)
o.append(f'<div{bi("rise", 5)}>' + t.html() + '</div>')
o += tag(t, 1, "('데이터베이스 이름', '접속한 계정')", GR, 5, gap=40)
W("min", o, "가장 작은 예제예요. 일곱 줄이에요. 첫 줄 import psycopg로 라이브러리를 불러와요. 셋째 줄 DSN은 접속할 주소예요. 다음 장에서 한 칸씩 봐요. 다섯째 줄 with psycopg.connect(DSN) as conn은 그 주소로 접속하고, 연결에 conn이라는 이름을 붙여요. 여섯째 줄에서 conn.execute로 SQL을 보내요. current_database()는 지금 데이터베이스 이름, current_user는 접속한 계정이에요. 뒤에 붙은 fetchone()이 결과 첫 줄을 꺼내요. 실행은 9에서 배운 uv run main.py예요. kant_shop과 postgres가 든 튜플 하나가 찍혔어요. 수업 코드에서 주석으로 막아 둔 연결 확인 코드와 같아요." + REAL)


# =====================================================================
# part 1: setup and connecting
# =====================================================================
o = frame("setup", EB[0], "프로젝트를 만들고 psycopg를 넣어요", CP[0])
o.append(label(96, 212, "준비: my-pg 컨테이너가 켜져 있고(35), kant_shop에 sports.sql을 넣어 뒀어요(38)", SUB, 26))
o.append(chipbox(96, 262, "docker start my-pg", INK, "#FFFFFF", size=24))
o.append(chipbox(470, 262, "docker exec -i my-pg psql -U postgres -d kant_shop &lt; sports.sql", INK, "#FFFFFF", size=24))
rows = []
for k_ in range(3):
    rows += run_rows("setup", k_)
t = TT(rows, 96, 360, size=26, w=1100, tid="t-setup", maxb=990)
o.append(t.html())
o.append(rbox(t, li(t, '"psycopg[binary]"'), '"psycopg[binary]"', 1, "#F2C46D"))
o.append(spot_rows(t, li(t, "+ psycopg=="), li(t, "+ psycopg-binary"), 2, dim=0.45))
o.append(spot_off(3))
# pyproject.toml
pj = D["pyproject"][0]["out"]
pl = [l if "psycopg" not in l else f'<span style="color:{GR};font-weight:700">{e(l)}</span>' for l in pj]
html_, gp = editor("e-pyproject", "pyproject.toml", pl, 1230, 360, 594, fs=17, color=GRAY, attrs=bi("rise", 3))
o.append(html_)
o += side(1230, 360 + gp["h"] + 30, 594, "[binary]를 꼭 붙여요", "PostgreSQL에 접속하는 부품까지 같이 받아요. 빼면 컴퓨터에 따라 import 줄에서 오류가 나요.", OR, 3, 28, 24)
W("setup", o, "준비부터 해요. 35에서 만든 my-pg 컨테이너를 켜 두고, 38에서처럼 kant_shop 데이터베이스에 sports.sql을 넣어 둬요. 그다음 9에서 배운 uv로 프로젝트 폴더를 만들어요. uv init sports-app, cd sports-app, 그리고 uv add로 psycopg를 넣어요. 이름 뒤에 대괄호로 binary를 붙이고, 대괄호가 셸에서 다르게 읽히지 않게 전체를 큰따옴표로 감싸요. binary는 PostgreSQL에 접속하는 부품까지 미리 만들어 둔 묶음이에요. 출력에 psycopg와 psycopg-binary 두 개가 설치됐다고 나와요. pyproject.toml의 dependencies에도 한 줄이 생겼어요. binary를 빼면 컴퓨터에 따라 import 줄에서 오류가 나요. 오류 장에서 봐요." + REAL, ("p1", EB[0][3:]))

# ---------- DSN ----------
o = frame("dsn", EB[0], "DSN은 어디에, 누구로 접속할지 적은 주소예요", CP[0])
segs = [("host=localhost", BL, "어느 컴퓨터<br>(내 컴퓨터)", "d-host"), ("port=5432", OR, "몇 번 포트", "d-port"),
        ("dbname=kant_shop", TEAL, "어느 데이터베이스", "d-db"), ("user=postgres", MAG, "어느 계정", "d-user"),
        ("password=admin1234", GR, "비밀번호", "d-pw")]
o += parts(96, 250, segs, size=36, order=1, lab=26, drop=40, stagger=True, lw=330)
o.append(f'<div style="position:absolute;left:96px;top:520px;width:1728px;height:2px;background:{LINE}"></div>')
o.append(label(96, 556, "35에서 컨테이너를 켠 명령과 맞춰 봐요", GRAY, 26, order=6))
run35 = f'docker run -d --name my-pg -e POSTGRES_PASSWORD=<span style="color:{GR}"{MARK(6)}>admin1234</span> -p <span style="color:{OR}"{MARK(6)}>5432</span>:5432 postgres:18'
o.append(p(f"position:absolute;left:96px;top:610px;font-family:{MONO};font-size:30px;font-weight:700;color:{INK};white-space:nowrap", run35, bi("rise", 6)))
o.append(p(f"position:absolute;left:96px;top:680px;font-family:{MONO};font-size:30px;font-weight:700;color:{INK};white-space:nowrap",
           f'CREATE DATABASE <span style="color:{TEAL}">kant_shop</span>;', bi("rise", 6)))
o.append(p(f"position:absolute;left:96px;top:760px;width:1728px;font-size:27px;line-height:1.55;color:{SUB}",
           f"관리자 계정 이름은 따로 정하지 않으면 {kw('postgres')}예요(34). 포트는 {kw('-p 5432:5432')}의 왼쪽 숫자, 내 컴퓨터 쪽 번호를 적어요.", bi("rise", 7)))
o.append(caption(f"수업 코드는 {kw('port=5433')}이었어요. 컨테이너를 {kw('-p 5433:5432')}로 켰을 때 맞는 값이에요.", 900, 8, size=29))
W("dsn", o, "DSN은 접속 정보를 한 줄로 적은 글자예요. 칸마다 이름=값이고, 칸 사이는 띄어쓰기예요. host=localhost는 서버가 내 컴퓨터에 있다는 뜻이에요. port=5432는 문 번호예요. dbname=kant_shop은 들어갈 데이터베이스, user=postgres는 계정, password=admin1234는 비밀번호예요. 이 값들은 35에서 컨테이너를 켠 명령과 짝이 맞아요. POSTGRES_PASSWORD에 적은 admin1234가 비밀번호이고, -p 5432:5432의 왼쪽 숫자가 내 컴퓨터 쪽 포트예요. 관리자 이름은 따로 정하지 않아서 postgres예요. 수업 코드에는 port=5433이 적혀 있었어요. 컨테이너를 -p 5433:5432로 켰다면 5433이 맞고, 35처럼 켰다면 5432로 고쳐요. 포트가 틀리면 어떤 오류가 나는지는 오류 장에서 봐요.")

# ---------- with ----------
o = frame("with", EB[0], "with 블록 안에서만 연결이 열려 있어요", CP[0])
L = src("e_closed")
html_, g = ed("e-with", "main.py", L, 96, 206, 1728, fs=26)
o.append(html_)
o.append(lband(1, g, 4, 3, GR))
o += etag(g, 4, L[4], "들여쓰기 안: 연결이 열려 있는 동안", GR, 1, gap=40)
o.append(lband(2, g, 8, 1, RED))
o += etag(g, 8, L[8], "블록 밖", RED, 2, gap=40)
t = TT(run_rows("e-closed"), 96, g["top"] + g["h"] + 28, size=24, w=1728, tid="t-with", maxb=990)
o.append(f'<div{bi("rise", 3)}>' + t.html() + '</div>')
o.append(rbox(t, li(t, "the connection is closed"), "the connection is closed", 4, "#FF9C94"))
o += tag(t, li(t, "the connection is closed"), "블록이 끝나면 연결이 닫혀요", RED, 4, gap=40)
W("with", o, "with는 오늘 처음 보는 문법이에요. with 다음 줄부터 네 칸 들여 쓴 곳이 한 덩어리예요. 17에서 if 아래를 들여 쓴 것과 같은 규칙이에요. 이 덩어리 안에서만 conn으로 데이터베이스에 말을 걸 수 있어요. 들여쓰기가 끝나면 psycopg가 연결을 알아서 닫아요. 아홉째 줄은 블록 밖에서 conn을 다시 썼어요. 실행하면 블록 안의 연결 성공은 찍히고, 아홉째 줄에서 the connection is closed 오류가 나요. 연결이 이미 닫혔다는 뜻이에요. 그래서 SQL을 보내는 코드는 모두 with 블록 안에 둬요. with 블록이 끝날 때 하는 일이 하나 더 있는데, 4파트에서 봐요." + REAL)

# =====================================================================
# part 2: getting rows
# =====================================================================
o = frame("fetchall", EB[1], "fetchall: 줄 하나가 튜플 하나, 모두 모아 리스트예요", CP[1])
L = src("fetchall")
html_, g = ed("e-fa", "main.py", L[5:], 96, 206, 1000, fs=24, start=6, marks={1: {"fetchall()": f'style="background:#E1F2F3;border-radius:6px"'}})
o.append(html_)
o.append(lband(None, g, 1, 4, TEAL, alpha="14"))
# picture: table rows fly into tuples
gx0 = 1150
o.append(label(gx0, 206, "courses 표의 3줄", GRAY, 22))
gh, _ = grid(gx0, 246, ["course_id", "course_name", "fee"], [["1", "수영 초급 아침반", "70000"], ["2", "수영 초급 저녁반", "70000"], ["3", "수영 중급 새벽반", "80000"]], [150, 300, 150], 50, "fa-grid", PG, size=20)
o.append(gh)
o.append(label(gx0, 452, "파이썬이 받은 값", TEAL, 22, order=1))
for k_, (a_, b_, c_) in enumerate([("1", "수영 초급 아침반", "70000"), ("2", "수영 초급 저녁반", "70000"), ("3", "수영 중급 새벽반", "80000")]):
    o.append(p(f"position:absolute;left:{gx0 + 30}px;top:{512 + k_ * 56}px;height:46px;padding:0 14px;border-radius:10px;background:#E1F2F3;font-family:{MONO};font-size:21px;font-weight:700;line-height:46px;color:{INK};white-space:nowrap",
               e(f"({a_}, '{b_}', {c_})" + ("," if k_ < 2 else "")), f' id="tp{k_}" data-build-in="fly order 1" data-from="fa-grid"' + DELAY(k_ * 120)))
o.append(p(f"position:absolute;left:{gx0}px;top:500px;font-family:{MONO};font-size:60px;font-weight:300;line-height:1.2;color:{TEAL}", "[", bi("fade", 1)))
o.append(p(f"position:absolute;left:{gx0 + 30 + tw("(3, '수영 중급 새벽반', 80000)", 21) + 40}px;top:620px;font-family:{MONO};font-size:60px;font-weight:300;line-height:1.2;color:{TEAL}", "]", bi("fade", 1)))
rows = run_rows("fetchall")[:4]
t = TT(rows, 96, 720, size=24, w=1728, tid="t-fa", maxb=990)
o.append(f'<div{bi("rise", 2)}>' + t.html() + '</div>')
o += tag(t, 2, "rows[0]: 첫 줄 튜플", TEAL, 3, gap=40)
o += tag(t, 3, "rows[0][1]: 첫 줄의 두 번째 칸", TEAL, 3, gap=40)
W("fetchall", o, "이제 표 결과를 파이썬으로 받아 봐요. conn.execute(SQL) 뒤에 fetchall()을 붙이면 결과를 모두 꺼내요. 오른쪽 위가 psql에서 보던 courses 표 세 줄이에요. 파이썬으로 오면 줄 하나가 튜플 하나가 되고, 세 줄이 리스트 하나로 모여요. 그래서 print(rows)는 대괄호 안에 소괄호 세 개가 찍혀요. 13에서 배운 대로 rows[0]은 첫 줄 튜플이고, rows[0][1]은 그 튜플의 두 번째 칸, 강좌 이름이에요. 열 순서는 SELECT에 적은 순서와 같아요." + REAL, ("p2", EB[1][3:]))

# ---------- for ----------
o = frame("for", EB[1], "for로 한 줄씩 꺼내고, 번호로 칸을 골라요", CP[1])
html_, g = ed("e-for", "main.py", L[5:], 96, 206, 1000, fs=24, start=6)
o.append(html_)
o.append(lband(1, g, 5, 2, TEAL))
# one tuple with its indexes
TX0, TY0 = 1180, 250
o.append(label(TX0, 214, "row 하나", GRAY, 22))
cells_ = [("1", 80), ("'수영 초급 아침반'", 290), ("70000", 130)]
cx = TX0
for k_, (v, w_) in enumerate(cells_):
    o.append(p(f"position:absolute;left:{cx}px;top:{TY0 + 30}px;width:{w_}px;height:64px;border:3px solid {TEAL};border-radius:10px;background:#FFFFFF;text-align:center;font-family:{MONO};font-size:22px;font-weight:700;line-height:58px;color:{INK};white-space:nowrap", e(v), f' id="cell{k_}"'))
    o.append(p(f"position:absolute;left:{cx + min(0, w_ - 120) / 2:.0f}px;top:{TY0 + 110}px;width:{max(w_, 120)}px;text-align:center;font-family:{MONO};font-size:24px;font-weight:700;color:{TEAL if k_ else GRAY}", f"row[{k_}]", bi("pop", 2) + DELAY(k_ * 100)))
    cx += w_ + 14
o.append(p(f"position:absolute;left:{TX0}px;top:{TY0 + 170}px;width:640px;font-size:25px;line-height:1.5;color:{SUB}", "번호는 0부터예요. SELECT에 적은 열 순서 그대로예요.", bi("rise", 2)))
rows = run_rows("fetchall")
rows = rows[:1] + rows[4:]
t = TT(rows, 96, 600, size=30, w=1728, tid="t-for", maxb=990)
o.append(f'<div{bi("rise", 3)}>' + t.html() + '</div>')
o += tag(t, 2, "print(row[1], row[2])가 줄마다 한 번씩", TEAL, 3, gap=60)
W("for", o, "리스트니까 13에서 배운 for로 한 줄씩 꺼낼 수 있어요. for row in rows를 쓰면 row에 튜플이 하나씩 들어가요. 오른쪽 그림처럼 row[0]은 강좌 번호, row[1]은 이름, row[2]는 수강료예요. print(row[1], row[2])로 이름과 수강료만 찍으면 세 줄이 나와요. 번호로 칸을 고를 때는 SELECT에 적은 열 순서를 기억해야 해요. 열 순서를 바꾸면 번호도 바뀌어요. 이 불편함은 두 장 뒤에서 풀어요." + REAL)

# ---------- fetchone ----------
o = frame("fetchone", EB[1], "fetchone은 첫 줄 하나, 줄이 없으면 None이에요", CP[1])
L = src("fetchone")
html_, g = ed("e-fo", "main.py", L[4:], 96, 206, 1728, fs=28, start=5)
o.append(html_)
o.append(ed_spot(g, 1, 3, 1))
o.append(ed_spot(g, 4, 2, 2))
o.append(lspot_off(3))
t = TT(run_rows("fetchone"), 96, g["top"] + g["h"] + 26, size=28, w=820, tid="t-fo", maxb=990)
o.append(f'<div{bi("rise", 1)}>' + t.html() + '</div>')
nl = li(t, "None")
o.append(rbox(t, nl, "None", 2, "#FF9C94"))
tb, _ = table(980, g["top"] + g["h"] + 30, ["", "fetchall()", "fetchone()"],
              [["돌려주는 것", kw("[(…), (…)]"), kw("(…)")], ["줄이 없으면", kw("[]") + " 빈 리스트", kw("None")], ["언제", "목록을 다 볼 때", "개수, 합계, 한 명"]],
              [220, 330, 294], "fo-tb", size=25, rh=74, order=3)
o += tb
W("fetchone", o, "결과가 한 줄뿐일 때는 fetchone()을 써요. 첫 줄 튜플 하나만 꺼내요. COUNT(*)처럼 값이 하나인 결과도 튜플로 와서 (40,)이 찍혀요. 값만 쓰려면 row[0]처럼 번호로 꺼내요. 줄이 하나도 없으면 fetchone()은 None을 돌려줘요. 99번 회원은 없어서 None이 찍혔어요. fetchall()은 줄이 없으면 빈 리스트예요. None에서 row[0]처럼 칸을 꺼내려고 하면 오류가 나요. 4파트에서 실제로 봐요." + REAL)

# ---------- dict_row ----------
o = frame("dictrow", EB[1], "dict_row를 붙이면 열 이름으로 꺼내요", CP[1])
L = src("dictrow")
mk = {1: {"dict_row": f'style="background:#E1F2F3;border-radius:6px"{MARK(1)}'},
      6: {"row_factory=dict_row": f'style="background:#E1F2F3;border-radius:6px"{MARK(1)}'},
      10: {'c["course_name"], c["fee"]': f'style="background:#E1F2F3;border-radius:6px"{MARK(3)}'}}
html_, g = ed("e-dr", "main.py", L, 96, 206, 1190, fs=21, marks=mk)
o.append(html_)
# morph chips: row[2] -> c["fee"]
MX, MY = 1330, 260
o.append(label(MX, 214, "칸을 고르는 법", GRAY, 22))
o.append(p(f"position:absolute;left:{MX}px;top:{MY}px;font-family:{MONO};font-size:44px;font-weight:700;color:{INK};white-space:nowrap", tok("v", "row") + tok("o", "[") + tok("k", "2") + tok("c", "]"), ' id="m-a"' + MORPH_FROM()))
o.append(p(f"position:absolute;left:{MX}px;top:{MY}px;font-family:{MONO};font-size:44px;font-weight:700;color:{INK};white-space:nowrap", tok("v", "c") + tok("o", "[") + tok("k", f'<span style="color:{STR}">"fee"</span>') + tok("c", "]"), MORPH(2, "m-a")))
o.append(p(f"position:absolute;left:{MX}px;top:{MY + 80}px;width:494px;font-size:24px;line-height:1.5;color:{SUB}", "몇 번째 칸인지 세지 않고, 열 이름을 키로 써요. 15의 딕셔너리예요.", bi("rise", 2)))
rows = run_rows("dictrow")
t = TT(rows, 96, g["top"] + g["h"] + 28, size=26, w=1728, tid="t-dr", maxb=990)
o.append(f'<div{bi("rise", 3)}>' + t.html() + '</div>')
o += tag(t, 1, "줄 하나가 딕셔너리: {열 이름: 값}", TEAL, 3, gap=40)
W("dictrow", o, "번호로 칸을 고르면 SELECT의 열 순서를 계속 기억해야 해요. 둘째 줄처럼 psycopg.rows에서 dict_row를 불러오고, connect에 row_factory=dict_row를 붙이면 줄 하나가 딕셔너리로 와요. 키는 열 이름이에요. 그래서 row[2] 대신 c[\"fee\"]처럼 15에서 배운 딕셔너리 꺼내기로 써요. 열 순서를 바꿔도 코드를 안 고쳐도 돼요. 출력 첫 줄을 보면 중괄호 안에 열 이름과 값이 짝으로 들어 있어요. 수업 코드도 dict_row를 썼어요. 앞으로는 계속 이 방법으로 써요." + REAL)

# ---------- list ----------
o = frame("list", EB[1], "강좌 목록을 표처럼 찍어요", CP[1])
L = src("list")
mk = {8: {"c.sport_id = s.sport_id": f'style="background:#E1F2F3;border-radius:6px"'}}
html_, g = ed("e-list", "main.py", L[5:], 96, 206, 1110, fs=20, start=6, marks={k - 5: v for k, v in mk.items()})
o.append(html_)
o += etag(g, 0, L[5], "따옴표 세 개: 여러 줄 글자", GRAY, 1, gap=40)
o += etag(g, 3, L[8], "40의 JOIN, 종목 이름 붙이기", TEAL, 2, gap=40)
o.append(ed_spot(g, 8, 5, 3))
o.append(lspot_off(4))
t = TT(run_rows("list"), 1230, 206, size=22, w=594, tid="t-list", maxb=990)
o.append(f'<div{bi("rise", 4)}>' + t.html() + '</div>')
o.append(caption(f"수업 코드에서 고친 두 곳: 열 이름은 표에 맞춰 {kw('sport_id')}, 쓰이지 않던 {kw('LEFT JOIN')}과 {kw('DISTINCT')}는 뺐어요.", 900, 5, size=28))
W("list", o, "배운 것을 모아 강좌 14개를 표처럼 찍어 봐요. 수업에서 만든 list_courses 함수예요. SQL이 길어서 따옴표 세 개로 감쌌어요. 따옴표 세 개 사이에는 여러 줄 글자를 쓸 수 있어요. 40에서 배운 JOIN으로 종목 이름을 붙였어요. 수업 코드에서는 courses 표의 열이 sports_id인데 쿼리에는 sport_id를 써서 서로 맞지 않았어요. 여기서는 38부터 쓰는 데이터에 맞춰 양쪽 다 sport_id예요. 함수 안에서는 for로 한 줄씩 받아서 13에서 배운 f-string 포맷으로 찍어요. 콜론 오른쪽 2는 두 칸 오른쪽 맞춤, 쉼표는 천 단위 콤마예요. 수업 코드의 LEFT JOIN과 DISTINCT는 결과에 쓰이지 않아서 뺐어요. 신청 수를 세는 버전은 실제 상황 1에서 만들어요." + REAL)


# =====================================================================
# part 3: %s
# =====================================================================
o = frame("param", EB[2], "바뀌는 값 자리에 %s를 적고, 값은 따로 넘겨요", CP[2])
L = src("param")
mk = {9: {"%s": f'id="slot"'}, 15: {"(sport,)": f'id="arg-t" style="background:#FBF0DF;border-radius:6px"'},
      20: {'"테니스"': 'id="a-ten"'}, 21: {'"요가"': 'id="a-yoga"'}}
html_, g = ed("e-par", "main.py", L[5:], 96, 206, 1100, fs=22, start=6, marks={k - 5: v for k, v in mk.items()})
o.append(html_)
# "테니스" flies to the %s slot
sx = gline_x(g, L[9], "%s")
sy = gtop(g, 4)
o.append(p(f"position:absolute;left:{sx - 4:.0f}px;top:{sy - 2:.0f}px;height:{g['lh'] + 4:.0f}px;padding:0 6px;border-radius:6px;background:{OR};font-family:{MONO};font-size:22px;font-weight:700;line-height:{g['lh'] + 4:.0f}px;color:#FFFFFF;white-space:nowrap", "'테니스'", ' id="fly-ten" data-build-in="fly order 2" data-from="a-ten"'))
o += etag(g, 4, L[9], "값이 들어갈 자리", OR, 1, gap=40, x0=sx + 140)
o.append(ed_spot(g, 4, 1, 1, bar=OR))
o.append(lspot_off(2))
t = TT(run_rows("param"), 1220, 206, size=24, w=604, tid="t-par", maxb=990)
o.append(f'<div{bi("rise", 3)}>' + t.html() + '</div>')
o.append(p(f"position:absolute;left:1220px;top:{t.y + t.h + 30}px;width:604px;font-size:25px;line-height:1.55;color:{SUB}", "SQL은 그대로 두고, 넘기는 값만 바꿔서 두 번 물었어요.", bi("rise", 3)))
W("param", o, "종목마다 강좌를 보고 싶어요. SQL에서 바뀌는 값 자리에 퍼센트 s를 적어요. 따옴표 없이 퍼센트 s 두 글자만 적어요. 값은 execute의 두 번째 칸에 튜플로 따로 넘겨요. show 함수가 받은 sport가 그 튜플에 들어가요. show(conn, \"테니스\")를 부르면 테니스가 퍼센트 s 자리에 들어가서 테니스 강좌 세 개가 나와요. 요가로 부르면 요가 강좌 두 개예요. SQL 글자는 한 번만 적고, 넘기는 값만 바꿔서 여러 번 물을 수 있어요. 수업 코드의 LIST_SQL에서 enroll_month = %s, 그리고 (MONTH,)가 바로 이 모양이에요." + REAL, ("p3", EB[2][3:]))

# ---------- two %s ----------
o = frame("param2", EB[2], "%s가 여러 개면 튜플에 적은 순서대로 들어가요", CP[2])
L = src("param2")
sql_line = L[4]
CY = 250
code2 = (f'SQL = "SELECT course_name, fee FROM courses WHERE fee BETWEEN '
         f'<span id="s1" style="color:{PCT}">%s</span> AND <span id="s2" style="color:{PCT}">%s</span> ORDER BY fee"')
o.append(p(f"position:absolute;left:96px;top:{CY}px;font-family:{MONO};font-size:30px;font-weight:700;color:{INK};white-space:nowrap", code2))
code3 = f'conn.execute(SQL, (<span id="v1" style="color:{BL}">60000</span>, <span id="v2" style="color:{GR}">70000</span>))'
o.append(p(f"position:absolute;left:96px;top:{CY + 80}px;font-family:{MONO};font-size:30px;font-weight:700;color:{INK};white-space:nowrap", code3))
x1 = 96 + tw('SQL = "SELECT course_name, fee FROM courses WHERE fee BETWEEN ', 30)
x2 = x1 + tw("%s AND ", 30)
for k_, (xx, val, col) in enumerate([(x1, "60000", BL), (x2, "70000", GR)]):
    o.append(p(f"position:absolute;left:{xx - 30:.0f}px;top:{CY - 64}px;height:50px;padding:0 12px;border-radius:10px;background:{col};font-family:{MONO};font-size:28px;font-weight:700;line-height:50px;color:#FFFFFF;white-space:nowrap", val, f' data-build-in="fly order {k_ + 1}" data-from="v{k_ + 1}"'))
o.append(p(f"position:absolute;left:96px;top:{CY + 150}px;font-size:26px;line-height:1.5;color:{SUB}", "첫 번째 %s에 튜플의 첫 번째 값, 두 번째 %s에 두 번째 값이 들어가요.", bi("rise", 2)))
t = TT(run_rows("param2"), 96, 470, size=30, w=820, tid="t-p2", maxb=840)
o.append(f'<div{bi("rise", 3)}>' + t.html() + '</div>')
o += tag(t, 1, "60000 이상 70000 이하", GR, 3, gap=40)
# one-value tuple
BX = 1000
o.append(label(BX, 470, "값이 하나여도 튜플로 넘겨요", OR, 28, order=4))
o.append(p(f"position:absolute;left:{BX}px;top:530px;font-family:{MONO};font-size:30px;font-weight:700;color:{GR};white-space:nowrap", e('("테니스",)'), bi("rise", 4)))
o.append(p(f"position:absolute;left:{BX + 270}px;top:534px;font-size:26px;color:{SUB};white-space:nowrap", "쉼표가 있어야 튜플이에요", bi("rise", 4)))
o.append(p(f"position:absolute;left:{BX}px;top:596px;font-family:{MONO};font-size:30px;font-weight:700;color:{RED};white-space:nowrap", e('("테니스")'), bi("rise", 4)))
o.append(p(f"position:absolute;left:{BX + 270}px;top:600px;font-size:26px;color:{SUB};white-space:nowrap", "괄호만 있으면 그냥 글자예요(오류 장)", bi("rise", 4)))
o.append(caption("%s 개수와 튜플의 값 개수를 똑같이 맞춰요.", 900, 5, size=30))
W("param2", o, "퍼센트 s는 여러 개 써도 돼요. 36에서 배운 BETWEEN에 최소 수강료와 최대 수강료 두 자리를 비워 뒀어요. 튜플에 60000, 70000을 넘기면 첫 번째 퍼센트 s에 60000, 두 번째에 70000이 순서대로 들어가요. 19에서 함수 인자가 순서대로 들어간 것과 같아요. 결과는 6만 원 이상 7만 원 이하인 강좌 네 개예요. 값이 하나일 때도 튜플로 넘겨요. 13에서 배운 대로 값 하나짜리 튜플은 뒤에 쉼표를 붙여야 해요. 쉼표가 없으면 괄호 안의 글자일 뿐이라 오류가 나요. 오류 장에서 실제 메시지를 봐요. 퍼센트 s 개수와 튜플의 값 개수는 항상 같게 맞춰요." + REAL)

# ---------- SQL injection ----------
K_OR, K_NX, K_11, K_ALL = kw("OR '1'='1'", RED), kw("name = 'x'"), kw("'1'='1'", RED), kw("x' OR '1'='1")
o = frame("inject", EB[2], "값을 f-string으로 SQL에 붙이면 문장이 바뀌어요", CP[2])
CW2 = 852
for k_, (scene, srcn, head, col) in enumerate([("inject-bad", "inject_bad", "f-string으로 붙이면", RED), ("inject-ok", "inject_ok", "%s로 넘기면", GR)]):
    x = 96 + k_ * (CW2 + 24)
    o.append(label(x, 206, head, col, 30))
    L = src(srcn)
    html_, g = ed(f"e-inj{k_}", "main.py", L[3:10], x, 262, CW2, fs=18, start=4, color=col)
    o.append(html_)
    rows = run_rows(scene)
    t = TT(rows, x, g["top"] + g["h"] + 24, size=21, w=CW2, tid=f"t-inj{k_}", maxb=760)
    o.append(f'<div{bi("rise", 1 + k_ * 2)}>' + t.html() + '</div>')
    if k_ == 0:
        sl = li(t, "SELECT name")
        o.append(rbox(t, sl, "OR '1'='1'", 2, "#FF9C94"))
        nl = li(t, "명이 나왔어요")
        o.append(rbox(t, nl, "40 명", 2, "#FF9C94"))
    else:
        nl = li(t, "명이 나왔어요")
        o.append(rbox(t, nl, "0 명", 4, "#7FD49B"))
o.append(p(f"position:absolute;left:96px;top:{t.y + t.h + 50}px;width:1728px;font-size:28px;line-height:1.55;color:{INK}", f"이름 칸에 따옴표와 {K_OR}를 넣었더니, 조건이 늘어나서 회원 40명이 다 나왔어요. 이런 공격을 SQL 인젝션이라고 해요.", bi("rise", 5)))
o.append(caption("SQL에 넣는 값은 f-string으로 붙이지 않고 항상 %s로 넘겨요.", t.y + t.h + 150, 6, size=30, color=GR))
W("inject", o, "이름으로 회원을 찾는 코드를 두 가지로 써 봤어요. 회원이 이름 칸에 x 따옴표 OR 따옴표 1 따옴표 = 따옴표 1처럼 이상한 글자를 넣었다고 해 봐요. 왼쪽은 13에서 배운 f-string으로 이름을 SQL 글자에 바로 붙였어요. 만들어진 SQL을 찍어 보면 따옴표가 중간에 닫히고 OR '1'='1'이라는 조건이 새로 생겼어요. '1'='1'은 언제나 참이라서 회원 40명이 모두 나왔어요. 남의 전화번호가 다 보이는 사고예요. 이렇게 값에 SQL 조각을 섞어 문장을 바꾸는 공격을 SQL 인젝션이라고 해요. 오른쪽은 같은 이름을 퍼센트 s로 넘겼어요. 이상한 글자 전체를 이름 하나로 보고 찾아서 0명이 나왔어요. 그래서 SQL에 넣는 값은 항상 퍼센트 s로 넘겨요." + REAL)

# ---------- why %s is safe (picture) ----------
o = frame("safe", EB[2], "%s는 SQL과 값을 따로 보내서 값이 문장을 못 바꿔요", CP[2])
RY1, RY2 = 290, 580
o.append(label(96, RY1, "f-string", RED, 28))
o.append(label(96, RY2, "%s", GR, 28))
# row 1: glued text
o.append(p(f"position:absolute;left:300px;top:{RY1 - 6}px;height:62px;padding:0 18px;border-radius:12px;background:#FBE9E7;border:2px solid {RED};font-family:{MONO};font-size:28px;font-weight:700;line-height:58px;color:{INK};white-space:nowrap",
           f"… WHERE name = 'x' <span style=\"color:{RED}\">OR '1'='1'</span>", bi("rise", 1)))
o.append(p(f"position:absolute;left:300px;top:{RY1 + 74}px;font-size:25px;color:{SUB};white-space:nowrap", "값이 SQL 글자에 녹아서 한 문장이 돼요", bi("rise", 1)))
o.append(harrow(1060, 1180, RY1 + 25, GRAY, 2))
o.append(p(f"position:absolute;left:1210px;top:{RY1 - 10}px;width:614px;font-size:27px;line-height:1.5;color:{INK}", f"PostgreSQL이 읽은 조건 두 개<br>{K_NX} 또는 {K_11} (늘 참)", bi("rise", 2)))
o.append(p(f"position:absolute;left:1210px;top:{RY1 + 94}px;font-size:30px;font-weight:700;color:{RED};white-space:nowrap", "40명 모두", bi("pop", 2)))
o.append(f'<div style="position:absolute;left:96px;top:{(RY1 + RY2) // 2 + 40}px;width:1728px;height:2px;background:{LINE}"></div>')
# row 2: two envelopes
o.append(p(f"position:absolute;left:300px;top:{RY2 - 6}px;height:62px;padding:0 18px;border-radius:12px;background:#FFFFFF;border:2px solid {GR};font-family:{MONO};font-size:28px;font-weight:700;line-height:58px;color:{INK};white-space:nowrap",
           f"… WHERE name = <span style=\"color:{PCT}\">%s</span>", bi("rise", 3)))
o.append(p(f"position:absolute;left:300px;top:{RY2 + 84}px;height:62px;padding:0 18px;border-radius:12px;background:#FFFFFF;border:2px dashed {GR};font-family:{MONO};font-size:28px;font-weight:700;line-height:58px;color:{INK};white-space:nowrap",
           e("x' OR '1'='1"), bi("rise", 3) + DELAY(150)))
o.append(p(f"position:absolute;left:780px;top:{RY2 + 4}px;font-size:25px;color:{SUB};white-space:nowrap", "SQL 따로", bi("rise", 3)))
o.append(p(f"position:absolute;left:640px;top:{RY2 + 94}px;font-size:25px;color:{SUB};white-space:nowrap", "값 따로", bi("rise", 3) + DELAY(150)))
o.append(harrow(1060, 1180, RY2 + 60, GRAY, 4))
o.append(p(f"position:absolute;left:1210px;top:{RY2 + 10}px;width:614px;font-size:27px;line-height:1.5;color:{INK}", f"이름이 글자 그대로<br>{K_ALL}인 회원", bi("rise", 4)))
o.append(p(f"position:absolute;left:1210px;top:{RY2 + 114}px;font-size:30px;font-weight:700;color:{GR};white-space:nowrap", "0명", bi("pop", 4)))
o.append(caption("숫자 하나를 넣을 때도 똑같이 %s로 넘겨요.", 860, 5, size=30))
W("safe", o, "왜 퍼센트 s는 안전한지 그림으로 봐요. f-string은 값을 SQL 글자 사이에 끼워 넣어서 한 문장을 만들어요. 값 안에 따옴표가 있으면 따옴표가 문장의 일부가 되고, 뒤의 OR가 새 조건이 돼요. PostgreSQL은 이름이 x인 회원 또는 늘 참인 조건으로 읽어서 40명을 다 줘요. 퍼센트 s를 쓰면 psycopg가 SQL 문장과 값을 따로 보내요. PostgreSQL은 문장을 먼저 정해 두고, 따로 온 값은 그 자리에 들어갈 글자 하나로만 써요. 그래서 따옴표가 들어 있어도 문장이 바뀌지 않아요. 값이 숫자 하나여도 같은 습관으로 퍼센트 s를 써요.")


# =====================================================================
# part 4: the class TODO and saving
# =====================================================================
o = frame("enroll", EB[3], "수업 TODO: 수강료를 SELECT로 꺼내서 INSERT에 넣어요", CP[3])
L = src("enroll")
P4 = {12: {"%s, %s, %s": 'id="s3"', "…%s": 'id="s4"'}, 22: {"member_id, course_id, MONTH, fee": 'id="tup"'}}
html_, g = ed("e-enr", "main.py", L[4:], 96, 200, 1110, fs=20, start=5, marks={k - 4: v for k, v in P4.items()})
o.append(html_)
o.append(ed_spot(g, 14, 4, 1, bar=GR))
o.append(ed_spot(g, 8, 1, 2, bar=GR))
o.append(ed_spot(g, 18, 1, 3, bar=GR))
o.append(lspot_off(4))
NX = 1240
notes_ = [("① TODO: 수강료 꺼내기", "fetchone()으로 강좌 한 줄을 받고 row[\"fee\"]로 수강료를 꺼내요. 5번 강좌면 60000이에요.", 1),
          ("② 번호는 SQL이 정해요", "가장 큰 enrollment_id + 1을 41의 서브쿼리로 구해요.", 2),
          ("③ %s 네 개, 값 네 개", "member_id, course_id, MONTH, fee가 순서대로 들어가요.", 3)]
yy = 214
for hd_, body_, od in notes_:
    o += side(NX, yy, 584, hd_, body_, GR, od, 28, 24)
    yy += 190
o.append(p(f"position:absolute;left:{NX}px;top:{yy + 10}px;width:584px;font-size:23px;line-height:1.55;color:{GRAY}", "수업 코드와 달라진 곳: 상태 값은 이 데이터에 맞춰 '신청', 입력 로직은 input()을 아직 안 배워서 MEMBER_ID와 COURSE_ID에 값을 적어 둬요.", bi("rise", 4)))
W("enroll", o, "수업 코드의 TODO를 채워 봐요. enroll 함수는 회원 번호와 강좌 번호를 받아서 신청 표에 한 줄을 넣어요. 첫 번째 TODO는 신청한 강좌의 수강료 꺼내기였어요. courses 표에서 그 강좌 번호의 fee를 SELECT하고, fetchone()으로 한 줄을 받아요. dict_row를 썼으니 row[\"fee\"]로 수강료를 꺼내요. 수업 코드는 fee = 0으로 비워 뒀던 자리예요. 두 번째로, 38부터 쓰는 데이터의 enrollments 표는 번호를 직접 적어야 해요. 그래서 VALUES 첫 칸에 41에서 배운 서브쿼리로 가장 큰 번호 더하기 1을 넣었어요. 수업 데이터는 SERIAL이라 번호를 안 적었어요. 세 번째로 INSERT의 퍼센트 s 네 개에 회원 번호, 강좌 번호, 달, 수강료가 순서대로 들어가요. 상태 값은 이 데이터에 맞춰 '신청'으로 적었어요. 입력 로직 TODO는 input()을 아직 배우지 않아서 맨 위 MEMBER_ID와 COURSE_ID에 값을 적어 두는 방식으로 남겨요.")

# ---------- run and check ----------
o = frame("check", EB[3], "실행하면 psql에서도 188번 줄이 보여요", CP[3])
o.append(label(96, 206, "① 실행 전 psql", GRAY, 24))
t1 = PT(D["enroll"][0]["out"], 96, 250, size=26, w=840, tid="t-c1", maxb=600)
o.append(t1.html())
o.append(label(984, 206, "② 프로그램 실행", GR, 24, order=1))
t2 = TT(run_rows("enroll", 1), 984, 250, size=26, w=840, tid="t-c2", maxb=600)
o.append(f'<div{bi("rise", 1)}>' + t2.html() + '</div>')
y3 = max(t1.y + t1.h, t2.y + t2.h) + 40
o.append(label(96, y3, "③ 실행 뒤 psql", PG, 24, order=2))
t3 = PT(D["enroll"][2]["out"], 96, y3 + 44, size=25, w=1728, tid="t-c3", maxb=930)
o.append(f'<div{bi("rise", 2)}>' + t3.html() + '</div>')
r188 = li(t3, "188 |")
o.append(spot_rows(t3, r188, r188, 3, dim=0.5))
o.append(spot_off(4))
o.append(caption("프로그램이 넣은 줄을 psql 창에서도 그대로 볼 수 있어요. 같은 데이터베이스이기 때문이에요.", t3.y + t3.h + 30, 4, size=28))
W("check", o, "실행해서 확인해요. 실행 전에 psql에서 신청 표를 세면 187줄이에요. uv run main.py를 치면 10번 회원이 5번 강좌를 신청했다는 메시지가 나와요. 다시 psql에서 번호가 큰 순으로 두 줄을 보면 188번 줄이 새로 생겼어요. 회원 10, 강좌 5, 2026-11, 신청, 60000이에요. 프로그램이 넣은 줄을 psql에서도 보는 건 둘이 같은 데이터베이스에 붙어 있어서예요. 다음 장에서는 이 줄이 언제 저장되는지 봐요." + REAL)

# ---------- when is it saved (picture) ----------
o = frame("commit", EB[3], "with 블록이 끝나는 순간 한 번에 저장해요", CP[3])
TLX, TLW = 260, 1500
for k_, (yy, col, head, endw, endc) in enumerate([(300, GR, "끝까지 성공", "COMMIT · 저장", GR), (620, RED, "중간에 오류", "ROLLBACK · 모두 취소", RED)]):
    od = 1 + k_ * 2
    o.append(label(96, yy - 18, head, col, 28, order=od))
    o.append(f'<div{bi("fade", od)} style="position:absolute;left:{TLX}px;top:{yy}px;width:{TLW - 300}px;height:6px;border-radius:3px;background:#D8D4CA"></div>')
    pts = [("with 시작", "연결"), ("SELECT fee", "수강료"), ("INSERT", "신청 한 줄")] if k_ == 0 else [("with 시작", "연결"), ("INSERT", "5번 강좌"), ("오류", "30번 강좌 없음")]
    for j, (a_, b_) in enumerate(pts):
        px = TLX + j * 400
        cc = RED if (k_ == 1 and j == 2) else INK
        o.append(f'<div{bi("pop", od)}{DELAY(j * 150)} style="position:absolute;left:{px - 12}px;top:{yy - 9}px;width:24px;height:24px;border-radius:12px;background:#FFFFFF;border:5px solid {cc}"></div>')
        o.append(p(f"position:absolute;left:{px - 150}px;top:{yy + 30}px;width:300px;text-align:center;font-family:{MONO};font-size:25px;font-weight:700;color:{cc};white-space:nowrap", a_, bi("rise", od) + DELAY(j * 150)))
        o.append(p(f"position:absolute;left:{px - 150}px;top:{yy + 72}px;width:300px;text-align:center;font-size:22px;color:{SUB};white-space:nowrap", b_, bi("rise", od) + DELAY(j * 150)))
    ex = TLX + TLW - 300
    o.append(p(f"position:absolute;left:{ex}px;top:{yy - 30}px;height:64px;padding:0 22px;border-radius:14px;background:{endc};font-size:28px;font-weight:700;line-height:64px;color:#FFFFFF;white-space:nowrap", endw, bi("pop", od + 1)))
    o.append(p(f"position:absolute;left:{ex}px;top:{yy + 50}px;width:{1824 - ex}px;font-size:23px;line-height:1.45;color:{SUB}", "블록 안에서 바꾼 것이 모두 남아요" if k_ == 0 else "앞에서 넣은 신청도 같이 사라져요", bi("rise", od + 1)))
o.append(p(f"position:absolute;left:96px;top:830px;width:1728px;font-size:27px;line-height:1.55;color:{INK}", f"43에서 직접 친 {kw('BEGIN')}, {kw('COMMIT')}, {kw('ROLLBACK')}을 psycopg가 대신 쳐요. 첫 SQL을 보낼 때 시작하고, 블록이 끝나면 저장하거나 취소해요.", bi("rise", 5)))
W("commit", o, "with 블록이 끝날 때 하는 일이 하나 더 있어요. 저장이에요. psycopg는 블록 안에서 첫 SQL을 보낼 때 트랜잭션을 시작해요. 블록 안의 SQL이 끝까지 성공하면, 블록이 끝나는 순간 COMMIT을 보내서 바꾼 것을 한 번에 저장해요. 위쪽 줄이에요. 중간에 오류가 나서 블록을 빠져나가면 COMMIT 대신 ROLLBACK을 보내요. 아래쪽 줄이에요. 이때는 앞에서 성공한 INSERT까지 모두 취소돼요. 43에서 psql에 직접 친 BEGIN, COMMIT, ROLLBACK을 psycopg가 대신 쳐 주는 거예요. 반쯤만 저장되는 일이 없어요.")

# ---------- rollback demo ----------
o = frame("rollback", EB[3], "두 번째 신청에서 멈추면 첫 번째 신청도 저장되지 않아요", CP[3])
L = src("rollback")
html_, g = ed("e-rb", "main.py", L[24:], 96, 206, 940, fs=24, start=25)
o.append(html_)
o.append(lband(1, g, 1, 1, GR))
o.append(lband(2, g, 2, 1, RED))
t2 = PT(D["rollback"][1]["out"], 1040, 206, size=22, w=784, tid="t-rb2", maxb=600)
o.append(f'<div{bi("rise", 3)}>' + t2.html() + '</div>')
o += tag(t2, li(t2, "187"), "그대로 187줄", PG, 3, gap=40)
t = TT(run_rows("rollback"), 96, max(g["top"] + g["h"], t2.y + t2.h) + 24, size=22, w=1728, tid="t-rb", maxb=960)
o.append(f'<div{bi("rise", 1)}>' + t.html() + '</div>')
o += tag(t, 1, "신청했다는 메시지는 찍혔어요", GR, 1, gap=40)
el = li(t, "TypeError")
o += tag(t, el, "30번 강좌가 없어서 row가 None", RED, 2, gap=40)
o.append(caption("오류로 블록을 빠져나가서 psycopg가 ROLLBACK했어요. 188번 줄은 생기지 않았어요.", t.y + t.h + 26, 4, size=28))
W("rollback", o, "실제로 확인해 봐요. with 블록 안에서 신청을 두 번 했어요. 5번 강좌 신청은 성공해서 메시지까지 찍혔어요. 30번 강좌는 없는 강좌라서 fetchone()이 None을 돌려줬고, None에서 fee를 꺼내다가 TypeError가 났어요. 오류 때문에 블록을 빠져나갔으니 psycopg는 COMMIT 대신 ROLLBACK을 보냈어요. psql에서 세어 보면 여전히 187줄이에요. 메시지가 찍혔어도 첫 번째 신청은 저장되지 않았어요. 신청과 결제처럼 함께 성공해야 하는 일을 한 블록에 두면 반만 저장되는 일을 막을 수 있어요. 없는 강좌를 미리 막는 방법은 실제 상황 2에서 봐요." + REAL)

# ---------- without with ----------
o = frame("nocommit", EB[3], "with 없이 연결하면 commit()을 직접 불러야 저장돼요", CP[3])
L = src("commit")
html_, g = ed("e-nc", "main.py", L[4:], 96, 200, 1728, fs=26, start=5)
o.append(html_)
o.append(lband(1, g, 2, 1, GR))
o += etag(g, 2, L[6], "이 줄이 없으면 저장되지 않아요", GR, 1, gap=40)
CW2 = 852
for k_, (k_psql, head, col) in enumerate([(1, "conn.commit() 줄 없이 실행했을 때", RED), (3, "conn.commit() 줄을 넣고 실행했을 때", GR)]):
    x = 96 + k_ * (CW2 + 24)
    od = 2 + k_
    yy = g["top"] + g["h"] + 30
    o.append(label(x, yy, head, col, 26, order=od))
    t = PT(D["nocommit"][k_psql]["out"], x, yy + 48, size=21, w=CW2, tid=f"t-nc{k_}", maxb=800)
    o.append(f'<div{bi("rise", od)}>' + t.html() + '</div>')
    rl = li(t, "임준서")
    o.append(rbox(t, rl, "임준서", od, "#9DC1E6", j=None) if False else "")
    o += tag(t, rl, "비어 있어요" if k_ == 0 else "저장됐어요", col, od, gap=30)
o.append(p(f"position:absolute;left:96px;top:830px;width:1728px;font-size:27px;line-height:1.55;color:{INK}", f"commit 없이 {kw('close()')}로 닫으면 바꾼 것이 취소돼요. psql은 문장마다 바로 저장했지만, psycopg는 commit해야 저장해요.", bi("rise", 4)))
o.append(caption("그래서 연결은 with 블록으로 열어요. 블록이 끝날 때 저장과 닫기를 알아서 해요.", 930, 5, size=29, color=GR))
W("nocommit", o, "with 없이 연결해도 돼요. psycopg.connect(DSN)의 결과를 conn에 담고, 다 쓰면 conn.close()로 닫아요. 10번 회원 임준서 님의 비어 있는 전화번호를 UPDATE로 넣어 봤어요. 먼저 일곱째 줄 conn.commit()을 빼고 실행했어요. 왼쪽처럼 commit() 없이 닫으면 바꿨어요가 찍혀도 psql에서 보면 전화번호가 여전히 비어 있어요. 저장하지 않은 변경은 연결을 닫을 때 취소돼요. 오른쪽은 이 줄을 넣고 다시 실행한 결과예요. close() 전에 conn.commit()을 부르면 저장돼요. psql에서는 문장 하나를 치면 바로 저장됐어요. 자동 커밋이라고 해요. psycopg는 commit해야 저장한다는 점이 달라요. 이걸 잊기 쉬워서 연결은 with 블록으로 여는 걸 권해요." + REAL)


# =====================================================================
# part 5: compare and errors
# =====================================================================
o = frame("cmp", EB[4], "psql과 파이썬은 같은 SQL을 다른 손으로 보내요", CP[4])
rows_ = [["접속", kw("docker exec -it my-pg psql -U postgres -d kant_shop"), kw("psycopg.connect(DSN)")],
         ["SQL 보내기", "치고 " + kw("Enter"), kw("conn.execute(SQL)")],
         ["결과", "화면에 표", kw("fetchall()") + " 리스트, " + kw("fetchone()") + " 튜플"],
         ["바뀌는 값", "SQL에 직접 적기", kw("%s") + "와 튜플 " + kw("(값,)")],
         ["저장", "문장마다 바로(자동 커밋)", "with 블록 끝, 또는 " + kw("commit()")],
         ["끝내기", kw("\\q"), "with 블록 끝, 또는 " + kw("close()")]]
tb, y0 = table(96, 214, ["", "psql (36~43)", "파이썬 psycopg (44)"], rows_, [260, 830, 638], "cmp-tb", size=25, rh=92, order=1, stagger=True)
o += tb
o.append(f'<div{bi("fade", 5)} style="position:absolute;left:84px;top:{y0 + 4 * 92 + 6}px;width:1752px;height:84px;border:4px solid {OR};border-radius:14px"></div>')
o.append(caption("SQL 문장은 그대로 같아요. 저장되는 때가 가장 크게 달라요.", 900, 7, size=30))
W("cmp", o, "psql과 파이썬을 나란히 놓아 봤어요. psql은 docker exec로 들어가서 SQL을 치고 Enter를 눌렀어요. 파이썬은 connect로 접속하고 execute로 보내요. psql은 결과를 화면에 표로 그려 주고, 파이썬은 리스트와 튜플로 받아요. 바뀌는 값은 psql에서는 SQL에 직접 적었지만, 파이썬에서는 퍼센트 s와 튜플로 넘겨요. 가장 큰 차이는 저장되는 때예요. psql은 문장마다 바로 저장해요. psycopg는 with 블록이 끝나거나 commit()을 불러야 저장해요. SQL 문장 자체는 36부터 배운 것과 똑같아요.", ("p5", EB[4][3:]))


def err_slide(sid, title, items, note, fix_rows, cap=None, sizes=None, top=24):
    """two error cases side by side; both terminals get the same font size, the largest that fits"""
    CW, GAP = 852, 24
    def build(sz):
        cols = int((CW - 2 * Term.PX - 10) / tw("M", sz))
        ts = [Term(run_rows(scene, cut=cut, wrap=cols), 96 + k_ * (CW + GAP), 252, size=sz, w=CW, tid=f"t-{sid}{k_}")
              for k_, (head, scene, cut, tags) in enumerate(items)]
        wide = any(t.tx + t_ * 1.01 > t.x + t.w - Term.PX for t in ts for t_ in t.tws)
        return ts, wide
    for sz in range(top, 14, -1):
        n = len(WARN)
        ts, wide = build(sz)
        bottom = max(t.y + t.h for t in ts)
        ntag = max(len(it[3]) for it in items)
        need = bottom + 24 + ntag * 44 + 30 + 60 + 50 + (60 if cap else 0)
        del WARN[n:]
        if not wide and need <= 1010:
            break
    ts, _ = build(sz)
    o = frame(sid, EB[4], title, CP[4])
    fy = max(t.y + t.h for t in ts) + 24 + max(len(it[3]) for it in items) * 44 + 30
    for k_, ((head, scene, cut, tags), t) in enumerate(zip(items, ts)):
        od = k_ * 2 + 1
        x = t.x
        o.append(label(x, 206, head, RED, 26, order=od))
        o.append(f'<div{bi("rise", od)}>' + t.html() + '</div>')
        ty = t.y + t.h + 24
        for sub, text, col in tags:
            o.append(rbox(t, li(t, sub), sub, od, "#FF9C94"))
            o.append(p(f"position:absolute;left:{x}px;top:{ty}px;width:{CW}px;font-size:25px;font-weight:700;color:{col}", e(text), bi("rise", od)))
            ty += 44
        if k_ < len(fix_rows) and fix_rows[k_]:
            bad, good, nt = fix_rows[k_]
            o += fixrow(x, fy, bad, good, od + 1, size=22, w=CW)
            if nt:
                o.append(p(f"position:absolute;left:{x + 110}px;top:{fy + 56}px;font-size:24px;color:{SUB};white-space:nowrap", nt, bi("rise", od + 1)))
    if cap:
        o.append(caption(cap, fy + 120, len(items) * 2 + 1, size=28))
    W(sid, o, note)


def keep_tail(n):
    return lambda ls: ls[-n:]


err_slide("e-install", "설치 오류 두 가지: uv add를 안 했거나 [binary]를 뺐어요",
          [("uv add를 안 하고 실행", "e-nomod", lambda ls: ls[2:], [("ModuleNotFoundError", "이 프로젝트에 psycopg가 없어요", RED)]),
           ("uv add psycopg만 했을 때 (부품이 없는 컴퓨터)", "e-nopq", None, [("no pq wrapper", "PostgreSQL 접속 부품을 못 찾았어요", RED)])],
          "설치에서 나는 오류 두 가지예요. 첫째는 uv add를 하지 않고 실행했을 때예요. import psycopg 줄에서 ModuleNotFoundError가 나요. 그 프로젝트에 psycopg가 없다는 뜻이에요. 가상환경을 켜지 않고 python main.py로 실행해도 같은 오류가 나요. 둘째는 대괄호 binary를 빼고 uv add psycopg만 했을 때예요. psycopg는 PostgreSQL 접속 부품인 libpq가 필요한데, 그 부품이 없는 컴퓨터에서는 no pq wrapper available 오류가 나요. 마지막 줄의 libpq library not found가 이유예요. 이 화면은 libpq가 없는 깨끗한 리눅스 컨테이너에서 같은 uv로 실제로 실행했어요. 둘 다 uv add \"psycopg[binary]\"로 고쳐요." + REAL,
          [('uv run main.py', 'uv add "psycopg[binary]"', "먼저 넣고 실행해요"), ('uv add psycopg', 'uv add "psycopg[binary]"', None)])

err_slide("e-conn", "접속 오류 두 가지: 포트가 다르거나 비밀번호가 틀렸어요",
          [("port=5433 (컨테이너는 5432)", "e-port", None, []),
           ("password=admin123", "e-pw", None, [])],
          "접속에서 나는 오류 두 가지예요. 첫째는 Connection refused예요. 5433번 문을 두드렸는데 받는 서버가 없다는 뜻이에요. 수업 코드처럼 port=5433을 적고 컨테이너는 5432로 켰을 때 나요. 컨테이너가 꺼져 있어도 같은 메시지가 나요. docker ps로 my-pg가 켜져 있는지, -p 왼쪽 숫자가 DSN의 port와 같은지 봐요. 둘째는 password authentication failed예요. 서버는 찾았는데 비밀번호가 틀렸어요. 35에서 POSTGRES_PASSWORD에 적은 값과 맞춰요. 컨테이너를 켤 때 쓴 비밀번호는 볼륨이 남아 있는 동안 바뀌지 않는다는 것도 34에서 봤어요." + REAL,
          [("port=5433", "port=5432", "docker ps로 켜졌는지도 봐요"), ("password=admin123", "password=admin1234", None)])

o = frame("e-fetch", EB[4], "fetchone에 괄호를 빼면 값 대신 메서드가 찍혀요", CP[4])
L = src("e_fetch")
html_, g = ed("e-ef", "main.py", L[4:], 96, 206, 1728, fs=30, start=5)
o.append(html_)
o.append(rbox(type("G", (), {"sx": lambda s, i, sub: gline_x(g, L[5], sub), "sw": lambda s, sub: tw(sub, g["fs"]), "top": lambda s, i: gtop(g, 1), "lp": g["lh"]})(), 0, "fetchone", 1, RED))
t = TT(run_rows("e-fetch", wrap=72), 96, g["top"] + g["h"] + 30, size=28, w=1728, tid="t-ef", maxb=860)
o.append(f'<div{bi("rise", 2)}>' + t.html() + '</div>')
o.append(rbox(t, 1, "<bound method Cursor.fetchone", 3, "#FF9C94"))
o += fixrow(96, t.y + t.h + 40, ".fetchone", ".fetchone()", 4, size=28, note_="괄호를 붙여야 실행돼요")
o.append(caption("오류 없이 이상한 글자가 찍혀서 더 찾기 어려워요. bound method가 보이면 괄호부터 봐요.", 900, 5, size=28))
W("e-fetch", o, "수업 코드에서 실제로 있었던 실수예요. fetchone 뒤에 괄호를 빼먹었어요. 괄호가 없으면 fetchone을 실행하지 않고, fetchone이라는 메서드 자체를 row에 담아요. 19에서 함수 이름만 적고 괄호를 안 붙였을 때와 같아요. 그래서 오류 없이 bound method Cursor.fetchone이라는 글자가 찍혀요. 결과 튜플이 아니라 메서드를 찍은 거예요. 오류가 안 나서 오히려 찾기 어려워요. 출력에 bound method가 보이면 괄호부터 확인해요." + REAL)

err_slide("e-params", "값 넘기기 오류 두 가지: 쉼표가 빠졌거나 %s에 따옴표를 붙였어요",
          [("(MONTH): 쉼표가 없어서 튜플이 아니라 글자", "e-tuple", None, [("TypeError", "튜플이 아니라 글자 str이 왔어요", RED)]),
           ("'%s': 따옴표 안에 넣음", "e-quote", None, [])],
          "값을 넘길 때 나는 오류 두 가지예요. 첫째는 값 하나를 넘기면서 쉼표를 빼먹었을 때예요. (MONTH)는 괄호로 감싼 글자일 뿐이라서 TypeError가 나요. 끝에 got str, 글자가 왔다고 알려 줘요. (MONTH,)처럼 쉼표를 붙이면 (63,)이 나와요. 중간의 라이브러리 안쪽 줄은 길어서 점 세 개로 줄였어요. 둘째는 퍼센트 s를 작은따옴표로 감쌌을 때예요. SQL에서 글자에 따옴표를 붙이던 습관 때문에 자주 나요. 따옴표 안의 퍼센트 s는 값 자리로 쓰이지 못해서 could not determine data type 오류가 나요. 따옴표는 psycopg가 알아서 붙여 주니 퍼센트 s만 적어요." + REAL,
          [("(MONTH)", "(MONTH,)", "결과 (63,)"), ("= '%s'", "= %s", "따옴표는 psycopg가 붙여요")])

o = frame("e-col", EB[4], "SQL의 열 이름이 표와 다르면 HINT가 맞는 이름을 알려 줘요", CP[4])
t = TT(run_rows("e-col"), 96, 206, size=24, w=1728, tid="t-ecol", maxb=800)
o.append(t.html())
el = li(t, "UndefinedColumn")
o.append(spot_rows(t, el, el, 1, dim=0.5))
hl_ = li(t, "HINT")
o.append(spot_rows(t, hl_, hl_, 2, dim=0.5))
o.append(spot_off(3))
o += fixrow(96, t.y + t.h + 40, "c.sports_id = s.sports_id", "c.sport_id = s.sport_id", 3, size=26)
o.append(p(f"position:absolute;left:96px;top:{t.y + t.h + 120}px;width:1728px;font-size:27px;line-height:1.55;color:{INK}", "수업 코드는 표를 sports_id로 만들고 쿼리에는 sport_id를 써서 반대로 어긋났어요. 만든 표의 열 이름에 맞춰요.", bi("rise", 4)))
W("e-col", o, "SQL 안의 실수는 PostgreSQL이 찾아 줘요. 파이썬 오류 아래에 psql에서 보던 ERROR, LINE, HINT가 그대로 붙어 나와요. 여기서는 열 이름을 sports_id로 적었는데 표의 열은 sport_id라서 UndefinedColumn이 났어요. HINT가 c.sport_id를 쓰려던 것 아니냐고 알려 줘요. 수업 코드에서는 반대로, 표를 sports_id로 만들고 쿼리에 sport_id를 써서 어긋났어요. 어느 쪽이든 실제로 만든 표의 열 이름에 맞춰 고쳐요. psql에서 \\d courses로 열 이름을 확인할 수 있어요." + REAL)

# =====================================================================
# part 6: real cases
# =====================================================================
o = frame("r-seats", EB[5], "실제 상황 1 · 11월에 강좌마다 남은 자리를 보여 줘요", CP[5])
L = src("seats")
html_, g = ed("e-seats", "main.py", L[4:], 96, 206, 1220, fs=21, start=5)
o.append(html_)
o.append(ed_spot(g, 2, 8, 1, bar=MAG))
o.append(ed_spot(g, 12, 5, 2, bar=MAG))
o.append(lspot_off(3))
o += etag(g, 5, L[9], "39 COUNT, 40 LEFT JOIN", MAG, 1, gap=30)
t = TT(run_rows("seats"), 1340, 206, size=22, w=484, tid="t-seats", maxb=990)
o.append(f'<div{bi("rise", 3)}>' + t.html() + '</div>')
o.append(spot_rows(t, li(t, "3자리"), li(t, "3자리"), 4, dim=0.5))
o.append(spot_off(5))
W("r-seats", o, "첫 번째 실제 상황이에요. 수강 신청 화면에 강좌마다 11월에 남은 자리를 보여 주고 싶어요. 강좌 표에 신청 표를 40에서 배운 LEFT JOIN으로 붙이고, 39에서 배운 COUNT로 강좌별 신청 수를 세요. 달은 퍼센트 s로 넘기고, 취소한 신청은 빼요. 신청이 없는 강좌도 0으로 나오게 LEFT JOIN을 썼어요. 파이썬에서는 정원에서 신청 수를 빼서 남은 자리를 계산해요. 12번 테니스 고급 레슨이 3자리로 가장 적어요. 수업 코드의 LIST_SQL이 LEFT JOIN으로 신청 표를 붙였던 것도 이런 목록을 만들려던 거예요." + REAL, ("p6", EB[5][3:]))

o = frame("r-dup", EB[5], "실제 상황 2 · 없는 강좌와 이미 한 신청을 먼저 막아요", CP[5])
L = src("dup")
html_, g = ed("e-dup", "main.py", L[19:], 96, 206, 1100, fs=22, start=20)
o.append(html_)
o.append(ed_spot(g, 1, 4, 1, bar=MAG))
o.append(ed_spot(g, 5, 3, 2, bar=MAG))
o.append(ed_spot(g, 13, 3, 3, bar=MAG))
o.append(lspot_off(4))
t = TT(run_rows("dup"), 1220, 206, size=22, w=604, tid="t-dup", maxb=520)
o.append(f'<div{bi("rise", 3)}>' + t.html() + '</div>')
t2 = PT(rewrap(D["dup"][1]["out"], 48), 1220, t.y + t.h + 24, size=21, w=604, tid="t-dup2", maxb=990)
o.append(f'<div{bi("rise", 4)}>' + t2.html() + '</div>')
o += [p(f"position:absolute;left:1220px;top:{t2.y + t2.h + 20}px;width:604px;font-size:24px;line-height:1.5;color:{SUB}", "188번 한 줄만 들어갔어요.", bi("rise", 4))]
o.append(caption(f"강좌가 없으면 {kw('if not row')}로, 이미 신청했으면 {kw('fetchone()')} 결과로 먼저 막고 {kw('return')}으로 끝내요.", 900, 5, size=28))
W("r-dup", o, "두 번째 실제 상황이에요. 4파트에서 없는 강좌를 신청했다가 TypeError가 났어요. 같은 강좌를 두 번 신청하는 것도 막아야 해요. 신청하기 전에 두 가지를 먼저 물어봐요. 수강료를 꺼낸 fetchone() 결과가 None이면 없는 강좌예요. 17에서 배운 대로 None은 False로 읽혀서 if not row로 쓸 수 있어요. 메시지를 찍고 19에서 배운 return으로 함수를 바로 끝내요. 그다음 같은 회원, 같은 강좌, 같은 달의 신청이 있는지 SELECT해요. 한 줄이라도 있으면 막아요. 30번, 5번, 5번 순서로 세 번 불렀더니 없는 강좌, 신청, 이미 신청 순서로 찍혔고, psql에서는 188번 한 줄만 들어갔어요." + REAL)

o = frame("r-receipt", EB[5], "실제 상황 3 · 회원 한 명의 11월 신청 내역을 영수증처럼 찍어요", CP[5])
L = src("receipt")
html_, g = ed("e-rc", "main.py", L[6:], 96, 206, 1140, fs=22, start=7)
o.append(html_)
o.append(ed_spot(g, 0, 8, 1, bar=MAG))
o.append(ed_spot(g, 10, 7, 2, bar=MAG))
o.append(lspot_off(3))
o += etag(g, 3, L[9], "JOIN 두 번(40)", MAG, 1, gap=30)
t = TT(run_rows("receipt"), 1260, 206, size=22, w=564, tid="t-rc", maxb=760)
o.append(f'<div{bi("rise", 3)}>' + t.html() + '</div>')
o.append(underline(4, round(t.tx), round(t.tx + t.sw("  405,000원  합계 (4개)")), round(t.top(li(t, "합계")) + t.lp - 2), MAG))
o.append(p(f"position:absolute;left:1260px;top:{t.y + t.h + 30}px;width:564px;font-size:24px;line-height:1.55;color:{SUB}", "합계는 23의 컴프리헨션과 sum으로 파이썬에서 더했어요. 39의 SUM으로 SQL에서 더해도 같아요.", bi("rise", 4)))
W("r-receipt", o, "세 번째 실제 상황이에요. 회원 한 명의 11월 신청 내역을 영수증처럼 찍어요. 신청 표에 회원 표와 강좌 표를 JOIN 두 번으로 붙였어요. 40에서 배운 표 세 개 JOIN이에요. 회원 번호와 달은 퍼센트 s 두 개로 넘기고, 취소는 빼요. fetchall()로 받은 리스트에서 첫 줄의 이름으로 제목을 찍고, for로 강좌마다 수강료와 이름을 찍어요. 합계는 23에서 배운 컴프리헨션으로 수강료만 모아 sum으로 더했어요. 39의 SUM으로 SQL에서 더해도 결과는 같아요. 26번 배서진 회원이 네 강좌, 405,000원이에요." + REAL)

# =====================================================================
# wrap-up
# =====================================================================
o = frame("sum", "정리", "SQL은 그대로, 값은 %s로, 저장은 with 블록 끝에서", INK)
rows_ = [["PostgreSQL에 접속해요", kw("with psycopg.connect(DSN, row_factory=dict_row) as conn:")],
         ["여러 줄을 받아요", kw("rows = conn.execute(SQL).fetchall()")],
         ["한 줄, 값 하나를 받아요", kw("row = conn.execute(SQL, (값,)).fetchone()")],
         ["바뀌는 값을 넣어요", kw("WHERE course_id = %s") + " 와 " + kw("(course_id,)")],
         ["바꾼 것을 저장해요", "with 블록 끝(오류면 취소), 또는 " + kw("conn.commit()")]]
tb, y0 = table(96, 214, ["이럴 때", "이렇게 써요"], rows_, [520, 1208], "sum-tb", size=26, rh=96, order=1, stagger=True, bold_first=False)
o += tb
o.append(p(f"position:absolute;left:96px;top:{y0 + 5 * 96 + 50}px;width:1728px;font-size:28px;line-height:1.55;color:{INK}", "다음에는 이 함수들을 웹 서버에 붙여서, 브라우저에서 누른 신청 버튼이 같은 INSERT를 실행하게 만들어요.", bi("rise", 6)))
W("sum", o, "오늘 쓴 것을 다섯 줄로 모았어요. 접속은 with 블록과 connect, row_factory=dict_row예요. 여러 줄은 fetchall, 한 줄은 fetchone으로 받아요. 바뀌는 값은 SQL에 퍼센트 s를 적고 튜플로 따로 넘겨요. f-string으로 붙이지 않아요. 바꾼 것은 with 블록이 끝날 때 저장되고, 중간에 오류가 나면 모두 취소돼요. with 없이 쓰면 commit()을 직접 불러요. 다음에는 이 함수들을 웹 서버에 붙여서 브라우저 버튼으로 신청하게 만들어요.", ("outro", "정리"))

o = frame("cheat", "정리", "한 장 요약", INK)
CL = ["import psycopg", "from psycopg.rows import dict_row", "",
      'DSN = "host=localhost port=5432 dbname=kant_shop user=postgres password=admin1234"', "",
      "with psycopg.connect(DSN, row_factory=dict_row) as conn:",
      '    rows = conn.execute("SELECT course_name, fee FROM courses").fetchall()',
      '    row = conn.execute("SELECT fee FROM courses WHERE course_id = %s", (5,)).fetchone()',
      '    print(row["fee"])',
      '    conn.execute("UPDATE members SET phone = %s WHERE member_id = %s", ("010-1111-2222", 10))',
      "# 블록이 끝나면 저장(commit), 중간에 오류가 나면 모두 취소(rollback)"]
html_, g = ed("e-cheat", "main.py", CL, 96, 206, 1728, fs=24)
o.append(html_)
o.append(f'<div style="position:absolute;left:96px;top:{g["top"] + g["h"] + 30}px;width:1728px;height:2px;background:{LINE}"></div>')
o.append(p(f"position:absolute;left:96px;top:{g['top'] + g['h'] + 54}px;font-size:26px;font-weight:700;color:{RED}", "막히면"))
errs = [("ModuleNotFoundError, no pq wrapper", 'uv add "psycopg[binary]"'), ("Connection refused", "docker ps, DSN의 port"),
        ("password authentication failed", "POSTGRES_PASSWORD와 맞추기"), ("bound method …fetchone", "fetchone()에 괄호"),
        ("query parameters should be a sequence", "(값,) 쉼표"), ("could not determine data type", "'%s' 대신 %s")]
for k, (a_, b_) in enumerate(errs):
    x = 96 + (k % 3) * 584
    y = g["top"] + g["h"] + 112 + (k // 3) * 112
    o.append(p(f"position:absolute;left:{x}px;top:{y}px;width:560px;font-family:{MONO};font-size:21px;font-weight:700;color:{RED};white-space:nowrap", e(a_)))
    o.append(p(f"position:absolute;left:{x}px;top:{y + 38}px;width:560px;font-size:26px;color:{SUB}", e(b_)))
W("cheat", o, "오늘 배운 코드를 한 파일에 모았어요. import 두 줄, DSN 한 줄, 그리고 with 블록 안에서 execute로 SQL을 보내요. 여러 줄은 fetchall, 한 줄은 fetchone, 바뀌는 값은 퍼센트 s와 튜플이에요. UPDATE와 INSERT도 같은 execute로 보내고, 블록이 끝나면 저장돼요. 아래는 자주 만나는 오류와 고치는 곳이에요.")

# =====================================================================
# toc
# =====================================================================
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
PL = [(CP[0], EB[0][3:], "uv add \"psycopg[binary]\", DSN 읽기, with 블록", "setup", "with"),
      (CP[1], EB[1][3:], "fetchall과 튜플, for와 번호, fetchone과 None, dict_row, 강좌 목록", "fetchall", "list"),
      (CP[2], EB[2][3:], "%s 자리와 튜플, 여러 개면 순서대로, SQL 인젝션", "param", "safe"),
      (CP[3], EB[3][3:], "수업 TODO(수강료 꺼내 INSERT), with가 끝날 때 commit, 오류면 rollback", "enroll", "nocommit"),
      (CP[4], EB[4][3:], "psql과 비교, 설치, 접속, 괄호, 값 넘기기, 열 이름 오류", "cmp", "e-col"),
      (CP[5], EB[5][3:], "남은 자리 목록, 신청 전에 막기, 신청 내역 영수증", "r-seats", "r-receipt")]
o = frame("toc", "", "오늘의 순서", INK)
for i, (c, h, s_, a, b) in enumerate(PL):
    y = 214 + i * 112
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:2px;background:{LINE}"></div>')
    o.append(p(f"position:absolute;left:96px;top:{y + 22}px;width:80px;font-size:48px;font-weight:900;line-height:1.5;color:{c}", str(i + 1)))
    o.append(p(f"position:absolute;left:190px;top:{y + 18}px;font-size:34px;font-weight:700;color:{INK}", e(h)))
    o.append(p(f"position:absolute;left:190px;top:{y + 70}px;font-size:22px;color:{SUB};white-space:nowrap", e(s_)))
    o.append(p(f"position:absolute;left:1524px;top:{y + 40}px;width:300px;text-align:right;font-size:28px;font-weight:700;color:{GRAY}", f"{page[a]}–{page[b]}쪽"))
o.append(f'<div style="position:absolute;left:96px;top:{214 + len(PL) * 112}px;width:1728px;height:2px;background:{LINE}"></div>')
o.append(p(f"position:absolute;left:96px;top:{214 + len(PL) * 112 + 34}px;font-size:26px;color:{SUB}", f"{page['why']}–{page['min']}쪽은 들어가기, {page['sum']}–{page['cheat']}쪽은 정리예요. 예제는 38부터 쓰는 스포츠 센터 수업 데이터예요."))
o = [x for x in o if 'id="eyebrow"' not in x]
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(o) + f"\n<aside>{e('여섯 파트로 나눴어요. 1파트는 프로젝트를 만들고 접속해요. 2파트는 결과를 튜플과 딕셔너리로 꺼내요. 3파트는 퍼센트 s로 값을 넣고, 왜 f-string으로 붙이면 안 되는지 봐요. 4파트는 수업 코드의 TODO를 채우고, 바꾼 것이 언제 저장되는지 봐요. 5파트는 psql과 비교하고 자주 나는 오류를 봐요. 6파트는 실제 상황 예제 세 개예요.')}</aside>\n</section>\n")

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-19T00:00:00Z"}, "lists": "css", "title": "파이썬에서 PostgreSQL 쓰기 (psycopg)", "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
for w_ in WARN:
    print("WARN", w_)
print(len(ORDER), "slides")
