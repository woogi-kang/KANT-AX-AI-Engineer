"""Generates every slide of the Docker 1 deck (29) and slides/deck.json.

Story: kim installs Docker Desktop (Windows: WSL 2, Mac: Apple silicon or Intel), checks it with hello-world,
looks around Docker Desktop, picks a Docker Official Image on Docker Hub, pulls nginx, runs it in the foreground,
in the background with a name, stops, starts and removes it, opens it in the browser with -p 8080:80,
meets five common errors, compares python:3.11 and python:3.12 without installing either, and ends with
the container's logs disappearing on rm (the bridge to 30, volumes).
Terminal output comes from tools/demo.sh (Docker 29.9.2 run for real), saved as tools/demo-output.txt.
Docker Hub pictures are real screenshots (tools/hubshots.js), the nginx page is a real screenshot
(tools/nginxshot.js). Docker Desktop, Task Manager and the Mac windows are drawn simply (not screenshots).
Usage (in 29-docker-basics): python3 tools/gen.py slides
"""
import html, json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from highlight import (spot, spot_off, cursor, cursor_off, ring, box as pen_box, underline, keys, link,  # noqa: E402
                       SLAM, SLIDE, DIM, DELAY, PATH, STAGGER, WIPE, MARK, COUNT, pulse, grow, shine, shake, zoom, zoom_off,
                       blur, blur_off, text as set_text)
import base64, io  # noqa: E402
from PIL import Image  # noqa: E402

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT):
    if f.endswith(".html"):
        os.remove(os.path.join(OUT, f))
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
BG, INK, SUB, LINE, CARD = "#F6F5F1", "#1D2330", "#4A5262", "#DCD8CE", "#FFFFFF"
BL, GR, OR, PUR, RED, TEAL, GRAY = "#2459C9", "#1F8A4C", "#B26A00", "#5A3BB8", "#A33131", "#0F7C86", "#5B6270"
T_BG = "#1B2029"
TCOL = {"o": "#D8DEE9", "e": "#FF9C94", "g": "#7FD18B", "d": "#7D8696", "y": "#F2C46D", "sel": "#7FD18B", "c": "#7D8696"}
DK = "#1D63ED"   # Docker blue (Docker Hub, Docker Desktop)
SHADOW = "0 18px 40px rgba(29,35,48,.16), 0 2px 6px rgba(29,35,48,.08)"
WARN = []


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
            w += 0.92
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
    return p(f"position:absolute;left:{left}px;top:{top}px;width:{width}px;font-size:{size}px;font-weight:700;line-height:1.45;color:{color}", text, bi("rise", order))


def cmd(text):
    """inline command in body text"""
    return f'<span style="font-family:{MONO};font-weight:700">{e(text)}</span>'


def mark(text, marks):
    """wrap the first match of each key of marks in <span id=...>"""
    out, rest = "", text
    hits = sorted(((text.find(k), k, v) for k, v in marks.items() if k in text), key=lambda t: t[0])
    pos = 0
    for at, k, v in hits:
        if at < pos:
            continue
        out += e(text[pos:at]) + f'<span id="{v}">{e(k)}</span>'
        pos = at + len(k)
    out += e(text[pos:])
    return out.replace("  ", " &#160;") if out else "&#160;"


# ---------- terminal ----------
class Term:
    PT, PX, BAR = 24, 34, 36   # top/bottom padding, side padding, dots row + gap

    def __init__(self, lines, x, y, size=28, w=None, lh=1.5, tid="term", attrs="", room=0, bar=True, bleed=False):
        self.x, self.y, self.size, self.tid, self.attrs = x, y, size, tid, attrs
        self.lp = round(size * lh)
        self.bar = self.BAR if bar else 0
        self.rows = [self._row(l) for l in lines]
        self.tws = [tw(r[1], size) for r in self.rows]
        self.w = w or round(max(self.tws) + 2 * self.PX + room)
        self.h = round(2 * self.PT + self.bar + len(self.rows) * self.lp)
        self.inner = []
        self.bleed = bleed
        if x + self.w > 1824 and not bleed:
            WARN.append(f"{tid}: terminal right edge {x + self.w}")

    def _row(self, l):
        kind = l[0]
        marks = l[-1] if isinstance(l[-1], dict) else {}
        if kind == "$":
            path, c = l[1], l[2]
            return kind, f"{path} $ {c}", f'<span style="color:#8FB3FF">{e(path)} $</span> ' + mark(c, marks), "#F2C46D"
        if kind == "#":   # a prompt inside a container: root@id:/# command
            pr, c = l[1], l[2]
            return kind, f"{pr} {c}", f'<span style="color:#7FD18B">{e(pr)}</span> ' + mark(c, marks), "#F2C46D"
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

    def band(self, i, j=None, order=None, color="rgba(242,196,109,.17)"):
        j = i if j is None else j
        self.inner.append(f'<div{bi("fade", order)} style="position:absolute;left:{self.PX - 12}px;top:{self.PT + self.bar + i * self.lp:.0f}px;width:{self.w - 2 * self.PX + 24}px;height:{(j - i + 1) * self.lp:.0f}px;background:{color};border-radius:8px"></div>')

    def html(self):
        o = [f'<div id="{self.tid}"{self.attrs} style="position:absolute;left:{self.x}px;top:{self.y}px;width:{self.w}px;height:{self.h}px;background:{T_BG};border-radius:18px;padding:{self.PT}px {self.PX}px;font-family:{MONO};font-variant-ligatures:none;overflow:hidden;box-shadow:0 10px 30px rgba(29,35,48,.12)">']
        if self.bar:
            o.append('<div style="display:flex;flex-direction:row;gap:10px;height:16px;margin-bottom:20px">'
                     + "".join(f'<div style="width:16px;height:16px;border-radius:8px;background:{c}"></div>' for c in ("#F28B82", "#F2C46D", "#7FD18B")) + '</div>')
        o += self.inner
        for kind, _, h, col in self.rows:
            wt = "font-weight:700;" if kind in ("$", "sel") else ""
            o.append(p(f"position:relative;font-size:{self.size}px;line-height:{self.lp:.0f}px;height:{self.lp:.0f}px;white-space:pre;{wt}color:{col}", h))
        o.append('</div>')
        return "".join(o)


def tag(t, i, text, color, order=None, at=None, gap=44, dark=True):
    """A pill on terminal line i: dot right after the text, a short leader, then the words."""
    x0 = at if at is not None else t.end(i)
    cy = t.cy(i)
    pw = tw(text, 23, mono=False) + 30
    px = x0 + gap
    if px + pw > t.x + t.w - 14:
        WARN.append(f"{t.tid}: tag '{text}' ends at {px + pw:.0f}, terminal ends {t.x + t.w}")
    lc = {BL: "#6F9BF5", GR: "#5CC287", OR: "#E3A84A", RED: "#F07A72", TEAL: "#4FB8C2", GRAY: "#9AA3B5", PUR: "#A78BF2"}.get(color, color)
    return [f'<div{bi("fade", order)} style="position:absolute;left:{x0 + 12:.0f}px;top:{cy - 5:.0f}px;width:{gap - 12:.0f}px;height:10px">'
            f'<div style="position:absolute;left:0;top:0;width:10px;height:10px;border-radius:5px;background:{lc}"></div>'
            f'<div style="position:absolute;left:10px;top:4px;width:{gap - 22:.0f}px;height:2px;background:{lc}"></div></div>',
            p(f"position:absolute;left:{px:.0f}px;top:{cy - 20:.0f}px;height:40px;padding:0 15px;border-radius:10px;background:{color};font-family:{SANS};font-size:23px;font-weight:700;line-height:40px;color:#FFFFFF;white-space:nowrap", e(text), bi("pop", order))]


def kbd(x, y, text, order=None):
    return p(f"position:absolute;left:{x:.0f}px;top:{y:.0f}px;height:42px;padding:0 16px;border-radius:9px;background:#FFFFFF;border:2px solid #C9CED8;border-bottom-width:5px;font-family:{SANS};font-size:23px;font-weight:700;line-height:36px;color:{INK};white-space:nowrap", e(text), bi("pop", order))


# ---------- browser window (simplified GitHub page) ----------
def browser(x, y, w, h, url, inner, bid, attrs="", pad="28px 40px", align="center"):
    return (f'<div id="{bid}"{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{CARD};border:1px solid #D2CEC4;border-radius:16px;overflow:hidden;box-shadow:{SHADOW};display:flex;flex-direction:column">'
            '<div style="height:52px;flex:none;background:#EEECE6;display:flex;flex-direction:row;align-items:center;gap:9px;padding:0 18px">'
            + "".join('<div style="width:13px;height:13px;border-radius:7px;background:#C9CED8"></div>' for _ in range(3))
            + p(f"margin-left:14px;font-family:{SANS};font-size:20px;font-weight:500;color:{SUB};background:#FFFFFF;border-radius:9px;padding:4px 16px;white-space:nowrap", e(url))
            + '</div>'
            f'<div style="flex:1;display:flex;flex-direction:column;align-items:{align};justify-content:center;gap:22px;padding:{pad}">{inner}</div></div>')


def gh_button(text, bid=None, color=GR, size=24):
    i = f' id="{bid}"' if bid else ""
    return p(f"font-size:{size}px;font-weight:700;color:#FFFFFF;background:{color};border-radius:10px;padding:10px 30px;white-space:nowrap", e(text), i)

# ---------- a command taken apart: colored pieces with labels under them ----------
def parts(x, y, segs, size=48, order=None, lab=24, drop=34, stagger=False, sep=1):
    """segs: (text, color, label or None, id or None). Pieces are joined by one space."""
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
            o.append(p(f"position:absolute;left:{mid - 210:.0f}px;top:{y + size * 1.3 + drop + 10:.0f}px;width:420px;text-align:center;font-size:{lab}px;font-weight:700;line-height:1.35;color:{c}", label, bi("pop", ord_)))
        cx += w + tw(" " * sep, size)
    o.insert(0, p(f"position:absolute;left:{x}px;top:{y}px;font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.3;white-space:pre", (" " * sep).join(spans)))
    return o


def chip(text, color, bg, cid=None, attrs="", size=30, w=None, dashed=False):
    i = f' id="{cid}"' if cid else ""
    bd = f"border:3px dashed {color}" if dashed else f"border:3px solid {color}"
    ww = f"width:{w}px;" if w else ""
    return p(f"{ww}height:84px;flex:none;padding:0 26px;border-radius:14px;background:{bg};{bd};font-family:{MONO};font-size:{size}px;font-weight:700;line-height:78px;text-align:center;color:{color};white-space:nowrap", e(text), i + attrs)


def svg(inner, order=None, kind="draw"):
    return (f'<svg{bi(kind, order)} viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible">{inner}</svg>')


def arrow_path(d, color, width=5, dash=None, head=True):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"{da}/>')


def head_at(x, y, ang, color, size=18):
    import math
    a = math.radians(ang)
    p1 = (x - size * math.cos(a - 0.45), y - size * math.sin(a - 0.45))
    p2 = (x - size * math.cos(a + 0.45), y - size * math.sin(a + 0.45))
    return f'<path d="M{p1[0]:.0f},{p1[1]:.0f} L{x:.0f},{y:.0f} L{p2[0]:.0f},{p2[1]:.0f}" fill="none" stroke="{color}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'



# ---------- more drawing helpers ----------
HERE = os.path.dirname(os.path.abspath(__file__))


def shot(name, crop, x, y, w, sid=None, attrs="", radius=14, border=True, q=88):
    """A real screenshot (tools/src/name.png) cropped to crop=(l, t, r, b), shown w px wide, embedded as JPEG."""
    im = Image.open(os.path.join(HERE, "src", name + ".png")).convert("RGB").crop(crop)
    h = round(w * im.height / im.width)
    im = im.resize((w, h), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=q)
    uri = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    i = f' id="{sid}"' if sid else ""
    bd = f"border:1px solid {LINE};" if border else ""
    return (f'<div{i}{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;{bd}border-radius:{radius}px;overflow:hidden;box-shadow:{SHADOW}">'
            f'<img src="{uri}" style="display:block;width:{w}px;height:{h}px"></div>'), h


def sx_(crop, w):
    """scale factor from screenshot px to slide px for a crop shown w wide"""
    return w / (crop[2] - crop[0])


def window(x, y, w, h, title, inner, wid, attrs="", bar=54, pad="0", bg=CARD):
    """A plain desktop app window (drawn, not a screenshot)."""
    return (f'<div id="{wid}"{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{bg};border:1px solid #D2CEC4;border-radius:16px;overflow:hidden;box-shadow:{SHADOW}">'
            f'<div style="height:{bar}px;background:#EEECE6;display:flex;flex-direction:row;align-items:center;gap:9px;padding:0 18px;border-bottom:1px solid #E2DED5">'
            + "".join('<div style="width:13px;height:13px;border-radius:7px;background:#C9CED8"></div>' for _ in range(3))
            + p(f"margin-left:14px;font-size:20px;font-weight:700;color:{SUB};white-space:nowrap", e(title)) + '</div>'
            f'<div style="position:relative;height:{h - bar - 2}px;padding:{pad}">{inner}</div></div>')


def bar_(w, color="#E4E1DA", h=12):
    return f'<div style="width:{w}px;height:{h}px;border-radius:{h // 2}px;background:{color};flex:none"></div>'


def pill(text, color, bg, size=22, attrs="", mono=False):
    f = f"font-family:{MONO};" if mono else ""
    return p(f"{f}font-size:{size}px;font-weight:700;color:{color};background:{bg};border-radius:10px;padding:4px 14px;white-space:nowrap", e(text), attrs)


def abs_pill(x, y, text, color, order=None, size=23, attrs=""):
    return p(f"position:absolute;left:{x:.0f}px;top:{y:.0f}px;height:40px;padding:0 15px;border-radius:10px;background:{color};font-size:{size}px;font-weight:700;line-height:40px;color:#FFFFFF;white-space:nowrap", e(text), bi("pop", order) + attrs)


def leader(x1, y1, x2, y2, color, order=None):
    """a fine line from a label (x1, y1) to a dot at what it explains (x2, y2)"""
    return (svg(f'<path d="M{x1:.0f},{y1:.0f} L{x2:.0f},{y2:.0f}" stroke="{color}" stroke-width="2.5" fill="none"/>'
                f'<circle cx="{x2:.0f}" cy="{y2:.0f}" r="6" fill="{color}" stroke="#FFFFFF" stroke-width="2"/>', order, "fade"))


def term_lines(cmd, out, path="~", kind="o", marks=None):
    l = [("$", path, cmd) if not marks else ("$", path, cmd, marks)]
    return l + [(kind, x) for x in out]


# ---------- real output (tools/demo-output.txt) ----------
BLOCKS = []


def _load():
    step, cur = None, None
    with open(os.path.join(HERE, "demo-output.txt")) as f:
        for raw in f:
            line = raw.rstrip("\n")
            if line.startswith("### "):
                step = line[4:].split()[0]
            elif line.startswith("$ ") and cur is None:
                cur = {"step": step, "cmd": line[2:], "out": []}
            elif line.startswith("[exit ") and cur is not None:
                cur["exit"] = int(line[6:-1])
                BLOCKS.append(cur)
                cur = None
            elif cur is not None:
                cur["out"].append(line.rstrip())


_load()


def OUTP(step, cmd):
    for b in BLOCKS:
        if b["step"] == step and b["cmd"].startswith(cmd):
            out = list(b["out"])
            while out and out[-1] == "":
                out.pop()
            return out
    raise KeyError(f"{step}: {cmd}")


def OUTN(step, cmd, n):
    """the output of the n-th run of exactly this command in a step"""
    return [b["out"] for b in BLOCKS if b["step"] == step and b["cmd"] == cmd][n]


def pick(lines, *subs):
    """the first line containing each sub, in order"""
    res = []
    for s_ in subs:
        res.append(next(l for l in lines if s_ in l))
    return res


P = "~"
MADE = "출력은 tools/demo.sh로 Docker 29.9.2를 실제로 실행한 결과예요."
DESK_NOTE = "Docker Desktop 화면은 메뉴 위치만 보이게 단순하게 그렸어요. 버전마다 메뉴 이름과 순서가 조금 달라요."
LAB = {"img": OR, "ct": GR}

# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px">',
       p("position:absolute;left:128px;top:300px;font-size:28px;font-weight:700;color:#8FB3FF", "KANT AX/AI 엔지니어 트랙 · 29"),
       f'<h1{SLAM(1)} style="position:absolute;left:128px;top:360px;font-size:100px;font-weight:900;line-height:1.22;padding-bottom:16px;color:#F6F5F1">Docker 1<br>컨테이너 실행하기</h1>',
       p("position:absolute;left:128px;top:630px;font-size:40px;line-height:1.4;color:#BFC6D4", "설치하고, Hub에서 받고,<br>켜고 끄기")]
_ps = OUTP("port", "docker ps")
t = Term([("$", P, "docker run -d --name web -p 8080:80 nginx"), ("d", OUTP("port", "docker run")[0][:24] + "…"), ("o", ""), ("$", P, "docker ps"),
          ("o", "IMAGE   STATUS        PORTS"), ("g", "nginx   Up 1 second   0.0.0.0:8080->80/tcp")], 1000, 330, size=27, w=1040, tid="cov-term", bleed=True)
cov.append(t.html())
cov.append(shine(2, "cov-term"))
W("cover", cov, "29 챕터는 Docker를 처음 써 봐요. Docker는 프로그램을 실행 환경과 함께 상자에 담아 어느 컴퓨터에서나 똑같이 켜는 도구예요. 오늘은 Windows와 Mac에 Docker Desktop을 설치하고, Docker Hub에서 믿을 수 있는 이미지를 골라 받고, 컨테이너를 켜고 끄고 지워요. 마지막에는 브라우저로 컨테이너 안의 웹 서버에 들어가 봐요. 표지 오른쪽 docker ps 출력은 화면에 맞게 IMAGE, STATUS, PORTS 칸만 남겼어요.", ("intro", "들어가기"))

ORDER.append("toc")   # written last, after page numbers are known

# ---------- part 1: what is docker ----------
EB1 = "1. Docker가 뭔가요"
o = frame("why", EB1, "kim 컴퓨터에선 되는 코드가 lee 컴퓨터에선 SyntaxError가 나요", BL)
code = 'menu = {"latte": 4500}\nprint(f"라떼: {menu["latte"]}원")'
o.append(p(f"position:absolute;left:96px;top:222px;font-size:26px;font-weight:700;color:{GRAY}", "main.py"))
o.append(f'<div id="code" style="position:absolute;left:96px;top:266px;width:1728px;height:150px;background:#FFFFFF;border:1px solid {LINE};border-radius:18px;padding:30px 40px">'
         + "".join(p(f"font-family:{MONO};font-size:34px;line-height:46px;font-weight:700;color:{INK};white-space:pre", e(l)) for l in code.split("\n")) + '</div>')
py12 = OUTP("python", "docker run python:3.12")[-1:]
py11 = [l for l in OUTP("python", "docker run python:3.11") if l.startswith("  File") or l.startswith("    ") or l.startswith("SyntaxError")]
for k, (who, col, ver, lines, kind) in enumerate([("kim", BL, "Python 3.12", py12, "g"), ("lee", GR, "Python 3.11", py11, "e")]):
    y = 470 + k * 150 if k == 0 else 620
    o.append(f'<div{bi("rise", k + 1)} style="position:absolute;left:96px;top:{y}px;width:380px;display:flex;flex-direction:column;gap:12px">'
             f'<div style="display:flex;flex-direction:row;align-items:center;gap:16px"><div style="width:52px;height:52px;border-radius:26px;background:{col};color:#FFFFFF;font-size:24px;font-weight:900;line-height:52px;text-align:center">{who[0].upper()}</div>'
             + p(f"font-size:32px;font-weight:700;color:{col}", f"{who}의 컴퓨터") + '</div>'
             + '<div style="display:flex">' + pill(ver, col, "#FFFFFF", 24, mono=True).replace("border-radius", f"border:2px solid {col};border-radius") + '</div></div>')
    tt = Term([(kind, l) for l in lines], 500, y, size=28 if k else 32, w=1324, tid=f"t-{who}", attrs=bi("rise", k + 1), lh=1.5, bar=False)
    o.append(tt.html())
    if k:
        o.append(ring(3, tt.tx, tt.top(len(lines) - 1), tt.sw(lines[-1]), tt.lp, RED))
o.append(caption("같은 코드인데 컴퓨터마다 설치된 파이썬 버전이 달라요.", 900, 3, size=32))
W("why", o, "팀 프로젝트에서 자주 듣는 말이 \"제 컴퓨터에선 되는데요\"예요. kim은 파이썬 3.12, lee는 3.11을 설치해 두었어요. f-string 중괄호 안에서 같은 큰따옴표를 다시 쓰는 문법은 3.12부터 돼요. 그래서 같은 main.py가 kim 컴퓨터에서는 돌고 lee 컴퓨터에서는 SyntaxError가 나요. 패키지 버전, 운영체제가 달라도 같은 일이 생겨요. 출력은 tools/demo.sh에서 python:3.11, python:3.12 이미지로 실제로 실행한 결과예요. 이 비교는 6파트 실습에서 직접 해 봐요.", ("p1", "Docker가 뭔가요"))

o = frame("box", EB1, "프로그램과 실행 환경을 상자 하나에 담아서 옮겨요", BL)
# the container box
o.append(f'<div id="ctbox" style="position:absolute;left:96px;top:230px;width:620px;height:620px;background:#E9F0FE;border:4px solid {DK};border-radius:24px"></div>')
o.append(p(f"position:absolute;left:136px;top:258px;font-size:30px;font-weight:900;color:{DK}", "컨테이너"))
o.append(f'<div{STAGGER(1, 120)} style="position:absolute;left:136px;top:326px;width:540px;display:flex;flex-direction:column;gap:24px">'
         + "".join(f'<div style="height:140px;background:#FFFFFF;border-radius:16px;display:flex;flex-direction:column;justify-content:center;padding:0 30px;gap:4px">'
                   + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:{c}", e(a)) + p(f"font-size:24px;color:{SUB}", e(b_)) + '</div>'
                   for a, b_, c in [("main.py", "내가 만든 프로그램", INK), ("Python 3.12", "실행할 파이썬", BL), ("패키지, 설정", "필요한 것 전부", OR)]) + '</div>')
dest = [("kim의 노트북", "Windows", BL), ("lee의 노트북", "Mac", GR), ("회사 서버", "Linux", PUR)]
for i, (n, os_, c) in enumerate(dest):
    y = 230 + i * 220
    o.append(f'<div{bi("rise", 2)}{DELAY(i * 120)} style="position:absolute;left:1180px;top:{y}px;width:644px;height:180px;background:#FFFFFF;border:1px solid {LINE};border-radius:18px;padding:24px 34px">'
             + p(f"font-size:30px;font-weight:700;color:{c}", e(n)) + p(f"font-size:24px;color:{SUB};margin-top:2px", e(os_))
             + p(f"position:absolute;right:34px;top:64px;font-family:{MONO};font-size:30px;font-weight:700;color:{GR};background:#E8F4EC;border-radius:10px;padding:6px 18px", "라떼: 4500원") + '</div>')
    o.append(svg(arrow_path(f"M724,540 C900,540 1000,{y + 90} 1170,{y + 90}", DK, 4) + head_at(1172, y + 90, 0, DK), 2))
o.append(caption("상자째 옮기니까 어디서 켜도 결과가 같아요.", 900, 3, size=32))
W("box", o, "Docker는 프로그램만 보내지 않고, 프로그램이 돌아가는 데 필요한 파이썬과 패키지, 설정까지 상자 하나에 담아요. 이 상자를 컨테이너라고 불러요. 배에 싣는 화물 컨테이너를 떠올리면 돼요. 안에 무엇이 들었든 크기가 같아서 어느 배, 어느 트럭에도 그대로 실려요. Docker 컨테이너도 Windows 노트북, Mac, 회사 서버 어디서 켜도 안의 파이썬이 같으니 결과가 같아요.")

o = frame("mold", EB1, "이미지는 붕어빵 틀, 컨테이너는 그 틀로 찍은 붕어빵이에요", BL)
o.append(f'<div id="mold" style="position:absolute;left:96px;top:250px;width:560px;height:430px;background:#FFF4E2;border:4px solid {OR};border-radius:24px;padding:34px 40px">'
         + p(f"font-size:28px;font-weight:700;color:{OR}", "이미지 (틀)") + p(f"font-family:{MONO};font-size:64px;font-weight:700;color:{INK};margin-top:18px", "nginx")
         + p(f"font-size:26px;line-height:1.5;color:{SUB};margin-top:22px", "Docker Hub에서 받아 둔 설계도<br>받은 뒤로 바뀌지 않아요") + '</div>')
for i, (n, port) in enumerate([("web", "8080"), ("web2", "8081"), ("test", "8082")]):
    y = 250 + i * 150
    o.append(f'<div data-build-in="fly order {i + 1}" data-from="mold" style="position:absolute;left:1000px;top:{y}px;width:824px;height:124px;background:#E8F4EC;border:3px solid {GR};border-radius:62px;display:flex;flex-direction:row;align-items:center;gap:22px;padding:0 40px">'
             f'<div style="width:20px;height:20px;border-radius:10px;background:{GR}"></div>'
             + p(f"font-family:{MONO};font-size:40px;font-weight:700;color:{INK}", n) + p(f"margin-left:auto;font-size:24px;font-weight:700;color:{GR}", "컨테이너 (붕어빵)") + '</div>')
o.append(svg(arrow_path("M664,465 L980,465", OR, 5) + head_at(984, 465, 0, OR)))
o.append(p(f"position:absolute;left:700px;top:410px;width:260px;text-align:center;font-family:{MONO};font-size:28px;font-weight:700;color:{OR}", "docker run"))
rows = [("이미지", OR, "틀, 설계도", "docker images"), ("컨테이너", GR, "틀로 켠 실행 하나", "docker ps")]
for i, (a, c, b_, cm) in enumerate(rows):
    y = 760 + i * 92
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:1px;background:{LINE}"></div>')
    o.append(p(f"position:absolute;left:96px;top:{y + 22}px;font-size:32px;font-weight:700;color:{c}", a, bi("fade", 4)))
    o.append(p(f"position:absolute;left:420px;top:{y + 24}px;font-size:30px;color:{INK}", b_, bi("fade", 4)))
    o.append(p(f"position:absolute;left:1100px;top:{y + 24}px;font-family:{MONO};font-size:30px;font-weight:700;color:{INK}", cm, bi("fade", 4)))
o.append(f'<div style="position:absolute;left:96px;top:944px;width:1728px;height:1px;background:{LINE}"></div>')
W("mold", o, "24 클래스에서 클래스는 붕어빵 틀, 객체는 붕어빵이라고 했어요. Docker도 같아요. 이미지는 Docker Hub에서 받아 두는 틀이고, 받은 뒤로는 바뀌지 않아요. docker run으로 틀에서 찍어 낸 것이 컨테이너예요. 틀 하나로 붕어빵을 여러 개 찍듯이, nginx 이미지 하나로 컨테이너 web, web2, test를 따로 켤 수 있어요. 받은 이미지 목록은 docker images, 컨테이너 목록은 docker ps로 봐요.")

o = frame("big", EB1, "Docker Hub에서 이미지를 받아서 내 컴퓨터에서 컨테이너로 켜요", BL)
o.append(f'<x-icon name="Home" style="position:absolute;left:96px;top:222px;width:28px;height:28px;color:{GRAY}"></x-icon>')
o.append(p(f"position:absolute;left:134px;top:218px;font-size:26px;font-weight:700;color:{GRAY}", "내 컴퓨터"))
o.append(f'<div style="position:absolute;left:96px;top:270px;width:1060px;height:690px;background:#FFFFFF;border:1px solid {LINE};border-radius:24px"></div>')
tt = Term([("$", P, "docker pull nginx"), ("$", P, "docker run nginx")], 136, 310, size=28, w=440, tid="t-big", bar=True)
o.append(tt.html())
o.append(p(f"position:absolute;left:136px;top:{310 + tt.h + 14}px;font-size:24px;font-weight:700;color:{SUB}", "터미널에서 명령"))
o.append(f'<div id="engine" style="position:absolute;left:640px;top:310px;width:476px;height:610px;background:#E9F0FE;border:3px solid {DK};border-radius:20px;padding:24px 30px">'
         + p(f"font-size:28px;font-weight:900;color:{DK}", "Docker Desktop") + p(f"font-size:22px;color:{SUB};margin-top:4px", "엔진이 이미지와 컨테이너를 맡아요") + '</div>')
o.append(f'<div id="img-local" style="position:absolute;left:676px;top:430px;width:404px;height:96px;background:#FFF4E2;border:3px solid {OR};border-radius:16px;display:flex;flex-direction:row;align-items:center;gap:16px;padding:0 26px">'
         + p(f"font-size:22px;font-weight:700;color:{OR}", "이미지") + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{INK}", "nginx") + '</div>')
for i, n in enumerate(["web", "web2"]):
    o.append(f'<div{bi("rise", 3)}{DELAY(i * 120)} style="position:absolute;left:676px;top:{620 + i * 128}px;width:404px;height:100px;background:#E8F4EC;border:3px solid {GR};border-radius:50px;display:flex;flex-direction:row;align-items:center;gap:16px;padding:0 30px">'
             + p(f"font-size:22px;font-weight:700;color:{GR}", "컨테이너") + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{INK}", n) + '</div>')
o.append(svg(arrow_path("M878,530 L878,612", GR, 4) + head_at(878, 615, 90, GR), 3))
o.append(p(f"position:absolute;left:896px;top:552px;font-family:{MONO};font-size:24px;font-weight:700;color:{GR}", "run", bi("fade", 3)))
o.append(svg(arrow_path("M580,360 L632,360", GRAY, 4) + head_at(636, 360, 0, GRAY)))
# hub
o.append(f'<x-icon name="Cloud" style="position:absolute;left:1296px;top:222px;width:28px;height:28px;color:{DK}"></x-icon>')
o.append(p(f"position:absolute;left:1334px;top:218px;font-size:26px;font-weight:700;color:{DK}", "인터넷"))
o.append(f'<div id="hub" style="position:absolute;left:1296px;top:270px;width:528px;height:690px;background:{DK};border-radius:24px;padding:30px 36px">'
         + p("font-size:34px;font-weight:900;color:#FFFFFF", "Docker Hub") + p("font-size:22px;color:#D6E2FD;margin-top:4px", "hub.docker.com, 이미지 저장소")
         + '<div style="display:flex;flex-direction:column;gap:18px;margin-top:34px">'
         + "".join(f'<div style="height:84px;background:#FFFFFF;border-radius:14px;display:flex;flex-direction:row;align-items:center;padding:0 26px">'
                   + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{INK}", n) + '</div>' for n in ["nginx", "python", "hello-world", "…"]) + '</div></div>')
o.append(svg(f'<path id="p-pull" d="M1290,478 L1090,478" fill="none" stroke="none"/>'))
o.append(svg(arrow_path("M1290,478 L1092,478", OR, 5) + head_at(1088, 478, 180, OR), 1))
o.append(f'<div{PATH(2, "p-pull")} style="position:absolute;left:1072px;top:460px;width:36px;height:36px;border-radius:18px;background:{OR};border:4px solid #FFFFFF;box-shadow:0 2px 6px rgba(0,0,0,.18)"></div>')
o.append(p(f"position:absolute;left:1106px;top:420px;width:180px;text-align:center;font-family:{MONO};font-size:24px;font-weight:700;color:{OR}", "pull", bi("fade", 1)))
W("big", o, "오늘 쓰는 세 곳을 그림으로 봐요. 오른쪽 Docker Hub는 이미지를 모아 둔 인터넷 저장소예요. 코드를 GitHub에 모아 두듯이 이미지는 Docker Hub에 모여 있어요. 왼쪽 내 컴퓨터에는 Docker Desktop을 설치해요. 터미널에서 docker pull을 치면 Docker Desktop이 Hub에서 이미지를 받아 와요. docker run을 치면 받은 이미지로 컨테이너를 켜요. 같은 이미지로 컨테이너를 여러 개 켤 수도 있어요.")

o = frame("vm", EB1, "가상 머신은 컴퓨터를 통째로, 컨테이너는 프로그램만 담아요", BL)


def stack(x, title, col, layers, top_items, item_col, item_bg, order):
    out = [p(f"position:absolute;left:{x}px;top:222px;font-size:32px;font-weight:700;color:{col}", title)]
    y = 820
    for n, bg, c in layers:
        out.append(p(f"position:absolute;left:{x}px;top:{y}px;width:780px;height:84px;background:{bg};border-radius:14px;font-size:28px;font-weight:700;line-height:84px;text-align:center;color:{c}", n))
        y -= 96
    w_ = (780 - 24 * (len(top_items) - 1)) / len(top_items)
    out.append(f'<div{STAGGER(order, 120)} style="position:absolute;left:{x}px;top:{y - 300 + 84}px;width:780px;height:300px;display:flex;flex-direction:row;gap:24px">'
               + "".join(f'<div style="width:{w_:.0f}px;height:300px;display:flex;flex-direction:column;gap:12px;justify-content:flex-end">'
                         + "".join(p(f"height:{hh}px;background:{bg};border:3px solid {c};border-radius:14px;font-size:26px;font-weight:700;line-height:{hh - 6}px;text-align:center;color:{c}", n) for n, hh, bg, c in it)
                         + '</div>' for it in top_items) + '</div>')
    return out


o += stack(96, "가상 머신", GRAY, [("컴퓨터 (CPU, 메모리)", "#E4E1DA", INK), ("운영체제", "#E4E1DA", INK), ("가상화 프로그램", "#E4E1DA", INK)],
           [[("앱", 84, "#FFFFFF", INK), ("운영체제 하나 더", 180, "#EDEBE6", GRAY)]] * 2, GRAY, "#FFFFFF", 1)
o += stack(1044, "컨테이너", DK, [("컴퓨터 (CPU, 메모리)", "#E4E1DA", INK), ("운영체제", "#E4E1DA", INK), ("Docker", "#E9F0FE", DK)],
           [[("앱", 84, "#E8F4EC", GR)]] * 3, GR, "#E8F4EC", 2)
o.append(caption("컨테이너는 운영체제를 같이 써서 가볍고 몇 초 만에 켜져요.", 930, 3, size=30))
W("vm", o, "컨테이너를 처음 들으면 가상 머신과 헷갈려요. 가상 머신은 컴퓨터 안에 운영체제를 하나 더 통째로 켜요. 그래서 무겁고 켜는 데 오래 걸려요. 컨테이너는 아래 운영체제를 같이 쓰고, 앱과 앱에 필요한 것만 담아요. 그래서 가볍고 몇 초 만에 켜져요. 다만 컨테이너는 리눅스를 같이 쓰는 방식이라, Windows와 Mac에서는 Docker Desktop이 작은 리눅스를 하나 켜 두고 그 위에서 컨테이너를 돌려요. 그래서 Windows에서 설치할 때 WSL 2를 같이 켜요.")

# ---------- part 2: install ----------
EB2 = "2. 설치하기"
o = frame("win-check", EB2, "Windows는 작업 관리자에서 가상화가 켜져 있는지 먼저 봐요", TEAL)
# Task Manager, drawn
rows_ = [("사용률", "3%"), ("속도", "2.40GHz"), ("코어", "8"), ("논리 프로세서", "16"), ("가상화", "사용")]
graph = ('<svg viewBox="0 0 640 260" style="position:absolute;left:300px;top:110px;width:640px;height:260px">'
         '<rect x="0" y="0" width="640" height="260" fill="#F4F8FC" stroke="#9CC3E6"/>'
         '<polyline points="0,230 40,226 80,232 120,214 160,222 200,205 240,219 280,228 320,210 360,224 400,216 440,229 480,206 520,221 560,226 600,212 640,224" fill="none" stroke="#3B8ED4" stroke-width="3"/></svg>')
side = "".join(p(f"height:58px;padding:0 22px;border-radius:10px;font-size:23px;font-weight:{700 if n == '성능' else 500};line-height:58px;color:{INK};{'background:#E6EEF8;' if n == '성능' else ''}", n)
               for n in ["프로세스", "성능", "앱 기록", "시작 앱", "사용자", "세부 정보", "서비스"])
det = "".join(f'<div{" id=" + chr(34) + "virt" + chr(34) if a == "가상화" else ""} style="display:flex;flex-direction:row;gap:20px;height:48px;align-items:center">'
              + p(f"width:200px;font-size:23px;color:{SUB}", a + ":") + p(f"font-size:23px;font-weight:700;color:{INK}", b_) + '</div>' for a, b_ in rows_)
inner = (f'<div style="position:absolute;left:0;top:0;width:250px;height:100%;background:#F7F7F9;border-right:1px solid #E2DED5;padding:18px 14px;display:flex;flex-direction:column;gap:6px">{side}</div>'
         + p(f"position:absolute;left:300px;top:36px;font-size:34px;font-weight:700;color:{INK}", "CPU") + graph
         + f'<div style="position:absolute;left:300px;top:400px;width:640px;display:flex;flex-direction:column">{det}</div>')
o.append(window(96, 220, 1000, 740, "작업 관리자", inner, "taskmgr"))
o.append(keys(1, 1180, 236, "Ctrl+Shift+Esc", size=30))
steps = [("1", "Ctrl+Shift+Esc로 작업 관리자 열기"), ("2", "왼쪽 성능, 위의 CPU 누르기"), ("3", "가상화: 사용인지 보기")]
for i, (n, t_) in enumerate(steps):
    y = 340 + i * 96
    o.append(f'<div{bi("rise", i + 1)} style="position:absolute;left:1180px;top:{y}px;width:644px;display:flex;flex-direction:row;gap:18px;align-items:center">'
             f'<div style="width:48px;height:48px;border-radius:24px;background:{TEAL};color:#FFFFFF;font-size:24px;font-weight:900;line-height:48px;text-align:center;flex:none">{n}</div>'
             + p(f"font-size:28px;font-weight:700;color:{INK}", t_) + '</div>')
o.append(cursor(2, 96 + 1 + 14 + 125, 220 + 46 + 18 + 64 + 29))
o.append(cursor_off(3))
o.append(spot(3, target="virt", pad=10))
o.append(spot_off(4))
o.append(f'<div{bi("rise", 4)} style="position:absolute;left:1180px;top:690px;width:644px;background:#FFFFFF;border:1px solid {LINE};border-radius:18px;padding:26px 30px">'
         + p(f"font-size:26px;font-weight:700;color:{RED}", "사용 안 함이면") + p(f"font-size:24px;line-height:1.5;color:{INK};margin-top:8px", "컴퓨터를 켤 때 BIOS(UEFI) 설정에서 가상화를 켜야 해요. 메뉴가 회사마다 달라서 강사와 같이 해요.") + '</div>')
W("win-check", o, "Docker Desktop은 Windows 안에 작은 리눅스를 켜요. 그러려면 CPU의 가상화 기능이 켜져 있어야 해요. Ctrl+Shift+Esc로 작업 관리자를 열고 왼쪽 성능, 위의 CPU를 눌러요. 오른쪽 아래 가상화 줄이 사용이면 준비된 거예요. 사용 안 함이면 컴퓨터를 켤 때 BIOS(UEFI) 설정 화면에서 켜야 해요. Intel은 VT-x, AMD는 SVM이라는 이름이 많아요. 메뉴가 제조사마다 달라서 수업 시간에 같이 봐요. Windows 10은 22H2, Windows 11은 23H2 이상이고 메모리는 8GB 이상이어야 해요. 작업 관리자는 실제 화면이 아니라 위치만 보이게 그렸어요.", ("p2", "설치하기"))

o = frame("win-wsl", EB2, "WSL 2와 Hyper-V는 Windows 안에 리눅스를 켜는 두 방법이에요", TEAL)
o.append(f'<div style="position:absolute;left:96px;top:240px;width:880px;height:600px;background:#FFFFFF;border:3px solid #9AA3B5;border-radius:24px;padding:28px 36px">'
         + p(f"font-size:28px;font-weight:700;color:{GRAY}", "Windows") + '</div>')
o.append(f'<div id="linux" style="position:absolute;left:156px;top:330px;width:760px;height:440px;background:#EAF6F7;border:3px solid {TEAL};border-radius:20px;padding:24px 32px">'
         + p(f"font-size:28px;font-weight:700;color:{TEAL}", "작은 리눅스 (WSL 2)") + '</div>')
for i, n in enumerate(["web", "web2"]):
    o.append(f'<div{bi("rise", 1)}{DELAY(i * 120)} style="position:absolute;left:216px;top:{430 + i * 130}px;width:640px;height:100px;background:#E8F4EC;border:3px solid {GR};border-radius:50px;display:flex;flex-direction:row;align-items:center;gap:16px;padding:0 30px">'
             + p(f"font-size:24px;font-weight:700;color:{GR}", "컨테이너") + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{INK}", n) + '</div>')
cols = [("WSL 2", "추천", GR, ["Windows 안에서 리눅스를 켜는 기능", "Home, Pro 모두 돼요", "Docker Desktop이 기본으로 골라요"]),
        ("Hyper-V", "", GRAY, ["가상 컴퓨터를 켜는 Windows 기능", "Pro, Enterprise, Education만 있어요", "WSL 2를 못 쓸 때만 골라요"])]
for i, (n, tagt, c, ls) in enumerate(cols):
    y = 240 + i * 310
    box_ = (f'<div{bi("rise", 2 + i)} style="position:absolute;left:1040px;top:{y}px;width:784px;height:280px;background:#FFFFFF;border:1px solid {LINE};border-radius:20px;padding:28px 34px">'
            f'<div style="display:flex;flex-direction:row;gap:16px;align-items:center">' + p(f"font-family:{MONO};font-size:36px;font-weight:700;color:{c}", n)
            + (pill(tagt, "#FFFFFF", GR, 22) if tagt else "") + '</div>'
            + "".join(p(f"font-size:26px;line-height:1.5;color:{INK};margin-top:10px", "· " + e(x)) for x in ls) + '</div>')
    o.append(box_)
o.append(caption("Docker Desktop 설치 창에 Use WSL 2 instead of Hyper-V 칸이 있으면 켠 채로 둬요.", 900, 4, size=28))
W("win-wsl", o, "1파트 끝에서 Windows와 Mac은 컨테이너를 돌릴 작은 리눅스가 필요하다고 했어요. Windows에서 그 리눅스를 켜는 방법이 두 가지예요. WSL 2는 Windows 안에서 리눅스를 켜는 기능이에요. Windows Home에서도 되고 Docker Desktop이 기본으로 골라요. Hyper-V는 가상 컴퓨터를 켜는 Windows 기능인데 Pro, Enterprise, Education에만 있어요. 수업에서는 WSL 2로 통일해요. 설치 창의 Use WSL 2 instead of Hyper-V 칸이 보이면 켠 채로 두면 돼요.")

o = frame("win-install", EB2, "Windows는 WSL을 켠 뒤 Docker Desktop을 설치해요", TEAL)
st = [("1", "관리자 PowerShell", "시작 메뉴에서 PowerShell을 오른쪽 클릭, 관리자 권한으로 실행", "wsl --install", "끝나면 컴퓨터를 다시 시작해요"),
      ("2", "Git Bash 또는 PowerShell", "winget으로 Docker Desktop 설치", "winget install -e --id Docker.DockerDesktop", "설치 창이 뜨면 OK, 끝나면 Close"),
      ("3", "다시 시작", "컴퓨터를 한 번 더 다시 시작해요", None, "시작 메뉴에서 Docker Desktop을 열어요")]
for i, (n, where, what, c_, after) in enumerate(st):
    y = 230 + i * 236
    o.append(f'<div{bi("rise", i + 1)} style="position:absolute;left:96px;top:{y}px;width:1728px;height:212px;background:#FFFFFF;border:1px solid {LINE};border-radius:20px"></div>')
    o.append(p(f"position:absolute;left:130px;top:{y + 30}px;width:64px;height:64px;border-radius:32px;background:{TEAL};color:#FFFFFF;font-size:32px;font-weight:900;line-height:64px;text-align:center", n, bi("rise", i + 1)))
    o.append(p(f"position:absolute;left:224px;top:{y + 28}px;font-size:30px;font-weight:700;color:{INK}", e(where), bi("rise", i + 1)))
    o.append(p(f"position:absolute;left:224px;top:{y + 76}px;font-size:24px;color:{SUB}", e(what), bi("rise", i + 1)))
    if c_:
        tt = Term([("$", "PS" if i == 0 else P, c_)], 224, y + 120, size=28, w=1000, tid=f"t-win{i}", bar=False, attrs=bi("rise", i + 1))
        tt.PT = 14
        o.append(tt.html().replace(f"height:{tt.h}px", f"height:{tt.h - 20}px").replace("padding:24px", "padding:12px"))
    o.append(p(f"position:absolute;left:1290px;top:{y + 78}px;width:500px;font-size:26px;font-weight:700;line-height:1.45;color:{TEAL}", e(after), bi("rise", i + 1)))
W("win-install", o, "Windows 설치는 세 단계예요. 먼저 시작 메뉴에서 PowerShell을 오른쪽 클릭해 관리자 권한으로 열고 wsl --install을 쳐요. WSL과 기본 리눅스가 설치되고, 끝나면 컴퓨터를 다시 시작해요. 다음으로 winget install -e --id Docker.DockerDesktop을 쳐요. 09에서 uv를 winget으로 설치한 것과 같은 방법이에요. 설치 창이 뜨면 OK를 누르고 끝나면 Close를 눌러요. docker.com에서 Download for Windows 버튼으로 설치 파일을 받아도 같아요. 한 번 더 다시 시작한 뒤 시작 메뉴에서 Docker Desktop을 열어요. docker 명령은 01부터 써 온 Git Bash에서 쳐요. Windows 명령의 출력은 이 환경에서 실행할 수 없어서 옮기지 않았어요.")

o = frame("mac-chip", EB2, "Mac은 칩 종류를 보고 맞는 설치 파일을 골라요", TEAL)
for i, (lab, val, dl) in enumerate([("칩", "Apple M2", "Apple Silicon"), ("프로세서", "2.4 GHz Intel Core i5", "Intel Chip")]):
    x = 96 + i * 884
    inner = (f'<div style="display:flex;flex-direction:column;align-items:center;padding-top:40px;gap:8px">'
             f'<div style="width:220px;height:140px;border-radius:14px;background:#E4E1DA"></div>'
             + p(f"font-size:34px;font-weight:700;color:{INK};margin-top:14px", "MacBook Air" if i == 0 else "MacBook Pro")
             + f'<div id="chip{i}" style="display:flex;flex-direction:row;gap:24px;margin-top:22px">' + p(f"width:150px;text-align:right;font-size:26px;color:{SUB}", lab) + p(f"font-size:26px;font-weight:700;color:{INK}", val) + '</div>'
             + f'<div style="display:flex;flex-direction:row;gap:24px">' + p(f"width:150px;text-align:right;font-size:26px;color:{SUB}", "메모리") + p(f"font-size:26px;font-weight:700;color:{INK}", "16GB") + '</div></div>')
    o.append(window(x, 220, 844, 500, "이 Mac에 관하여", inner, f"about{i}"))
    o.append(spot(i + 1, target=f"chip{i}", pad=12))
    o.append(f'<div{bi("rise", i + 1)} style="position:absolute;left:{x}px;top:760px;width:844px;height:110px;background:{DK};border-radius:18px;display:flex;flex-direction:column;justify-content:center;padding:0 34px">'
             + p("font-size:22px;color:#D6E2FD", "docker.com에서") + p("font-size:30px;font-weight:700;color:#FFFFFF", "Download for Mac - " + dl) + '</div>')
o.append(spot_off(3))
o.append(caption("brew로 설치하면 칩에 맞는 파일을 알아서 골라요.", 920, 3, size=30))
W("mac-chip", o, "Mac은 칩이 두 종류라서 설치 파일도 두 가지예요. 화면 왼쪽 위 사과 메뉴에서 이 Mac에 관하여를 눌러요. 칩 줄에 Apple M1, M2처럼 나오면 Apple Silicon이고, 프로세서 줄에 Intel이 나오면 Intel Mac이에요. docker.com에서 직접 받을 때는 이 이름에 맞는 버튼을 눌러요. 다음 장의 brew로 설치하면 칩에 맞는 파일을 알아서 골라요. Docker Desktop은 최근 macOS 세 버전을 지원하고 메모리는 4GB 이상이면 돼요. 창은 실제 화면이 아니라 위치만 보이게 그렸어요.")

o = frame("mac-install", EB2, "Mac은 brew로 설치하고 Applications에서 Docker를 열어요", TEAL)
tt = Term([("$", P, "brew install --cask docker-desktop")], 96, 226, size=34, w=1728, tid="t-brew")
o.append(tt.html())
for k, (tok_, lab_, c_) in enumerate([("--cask", "앱 설치", OR), ("docker-desktop", "Docker Desktop", DK)]):
    x0 = tt.sx(0, tok_)
    o.append(underline(1, x0, x0 + tt.sw(tok_), tt.top(0) + tt.lp - 2, c_))
    o.append(p(f"position:absolute;left:{x0:.0f}px;top:{tt.y + tt.h + 16}px;font-size:26px;font-weight:700;color:{c_}", lab_, bi("fade", 1)))
fin = "".join(f'<div style="display:flex;flex-direction:row;align-items:center;gap:18px;height:64px;padding:0 26px;{"background:#E6EEF8;border-radius:10px;" if n == "Docker" else ""}">'
              f'<div style="width:36px;height:36px;border-radius:9px;background:{DK if n == "Docker" else "#D9D6CF"}"></div>' + p(f"font-size:26px;font-weight:{700 if n == 'Docker' else 500};color:{INK}", n) + '</div>'
              for n in ["Calculator", "Docker", "Safari", "Visual Studio Code"])
o.append(window(96, 480, 900, 470, "Applications", f'<div id="apps" style="padding:22px 20px;display:flex;flex-direction:column;gap:4px">{fin}</div>', "finder", attrs=bi("rise", 2)))
o.append(cursor(3, 96 + 20 + 26 + 18 + 120, 480 + 54 + 22 + 64 + 32))
o.append(f'<div{bi("rise", 4)} style="position:absolute;left:1080px;top:480px;width:744px;background:#FFFFFF;border:1px solid {LINE};border-radius:18px;padding:28px 34px">'
         + p(f"font-size:28px;font-weight:700;color:{INK}", "brew 없이 설치할 때") + p(f"font-size:25px;line-height:1.55;color:{SUB};margin-top:10px", "앞 장 버튼으로 Docker.dmg를 받아 열고, Docker 아이콘을 Applications 폴더로 끌어 놓아요.") + '</div>')
o.append(cursor_off(4))
W("mac-install", o, "Mac은 09에서 uv를 설치한 것처럼 brew로 설치해요. brew install --cask docker-desktop을 쳐요. --cask는 터미널 명령이 아니라 창이 있는 앱을 설치한다는 뜻이에요. 설치가 끝나면 Finder의 Applications 폴더에서 Docker를 두 번 눌러 열어요. brew를 쓰지 않으면 앞 장의 버튼으로 Docker.dmg를 받고, 열린 창에서 Docker 아이콘을 Applications 폴더로 끌어 놓아요. brew 설치 출력은 이 환경에서 실행할 수 없어서 옮기지 않았어요.")

o = frame("first-run", EB2, "처음 열면 약관에 Accept를 누르고 Engine running을 기다려요", TEAL)
agree = (p(f"position:absolute;left:60px;top:50px;font-size:34px;font-weight:700;color:{INK}", "Docker Subscription Service Agreement")
         + '<div style="position:absolute;left:60px;top:120px;display:flex;flex-direction:column;gap:18px">' + "".join(bar_(w_) for w_ in (640, 700, 560, 680, 600, 420)) + '</div>'
         + '<div style="position:absolute;right:50px;bottom:40px;display:flex;flex-direction:row;gap:16px">'
         + p(f"font-size:24px;font-weight:700;color:{SUB};border:2px solid #C9CED8;border-radius:10px;padding:10px 28px", "Close")
         + p(f"font-size:24px;font-weight:700;color:#FFFFFF;background:{DK};border-radius:10px;padding:10px 32px", "Accept", ' id="btn-accept"') + '</div>')
o.append(window(96, 220, 860, 520, "Docker Desktop", agree, "w-agree"))
o.append(cursor(1, target="btn-accept"))
side = "".join(p(f"height:52px;padding:0 20px;border-radius:10px;font-size:22px;font-weight:{700 if n == 'Containers' else 500};line-height:52px;color:{INK};{'background:#E6EEF8;' if n == 'Containers' else ''}", n)
               for n in ["Containers", "Images", "Volumes", "Builds"])
main = ('<div style="position:absolute;left:250px;top:40px;display:flex;flex-direction:column;gap:20px">' + p(f"font-size:30px;font-weight:700;color:{INK}", "Containers")
        + "".join(bar_(w_) for w_ in (420, 380, 450)) + '</div>')
foot = (f'<div id="engine-ok" style="position:absolute;left:0;bottom:0;width:100%;height:56px;background:#F7F7F9;border-top:1px solid #E2DED5;display:flex;flex-direction:row;align-items:center;gap:12px;padding:0 22px">'
        f'<div style="width:14px;height:14px;border-radius:7px;background:{GR}"></div>' + p(f"font-size:22px;font-weight:700;color:{INK}", "Engine running") + '</div>')
inner = f'<div style="position:absolute;left:0;top:0;width:220px;height:100%;background:#F7F7F9;border-right:1px solid #E2DED5;padding:16px 12px;display:flex;flex-direction:column;gap:4px">{side}</div>' + main + foot
o.append(window(1004, 380, 820, 520, "Docker Desktop", inner, "w-main", attrs=SLIDE(2, 0, 60)))
o.append(cursor_off(2))
o.append(spot(3, target="engine-ok", pad=8))
o.append(spot_off(4))
o.append(caption("로그인 화면이 나오면 건너뛰어도 돼요.<br>오늘 받는 이미지는 로그인 없이 받아요.", 790, 4, width=860, size=28))
W("first-run", o, "Windows와 Mac 모두 Docker Desktop을 처음 열면 약관 창이 떠요. Accept를 누르면 Docker Desktop이 켜져요. 계정 로그인이나 설문 화면이 나오면 건너뛰어도 돼요. 오늘 받는 공식 이미지는 로그인 없이 받을 수 있어요. 창 왼쪽 아래가 Engine running으로 바뀌면 준비된 거예요. 처음에는 작은 리눅스를 켜느라 1~2분 걸리기도 해요. Docker Desktop 창을 닫아도 엔진은 뒤에서 계속 돌아요. Windows는 화면 오른쪽 아래 알림 영역, Mac은 화면 위 메뉴 막대에 고래 아이콘이 보여요. " + DESK_NOTE)

o = frame("check", EB2, "터미널에서 docker --version과 hello-world로 확인해요", TEAL)
hw = OUTP("check", "docker run hello-world")
lines = [("$", P, "docker --version")] + [("o", l) for l in OUTP("check", "docker --version")] + [("$", P, "docker run hello-world")] + [("d" if i < 4 else "o", l) for i, l in enumerate(hw[:7])] + [("d", "…")]
t = Term(lines, 96, 214, size=30, w=1728, lh=1.45)
t.band(1, order=1, color="rgba(143,179,255,.14)")
t.band(8, order=3, color="rgba(127,209,139,.16)")
o.append(t.html())
o += tag(t, 1, "설치된 버전", BL, 1)
o += tag(t, 3, "이미지가 없어서 Hub에서 받아요", OR, 2)
o += tag(t, 8, "설치 성공", GR, 3)
o.append(caption("Windows는 Git Bash, Mac은 터미널에서 쳐요. 버전 숫자는 달라도 괜찮아요.", t.y + t.h + 36, 4, size=28, color=SUB))
W("check", o, "설치가 끝나면 터미널에서 두 명령으로 확인해요. docker --version은 설치된 Docker 버전을 보여 줘요. 숫자는 설치한 날에 따라 달라도 괜찮아요. docker run hello-world는 확인용 이미지를 받아서 컨테이너로 한 번 켜 봐요. 처음에는 내 컴퓨터에 이미지가 없어서 Unable to find image가 나오고 Hub에서 받아 와요. Hello from Docker!가 보이면 설치 성공이에요. 아래쪽 설명 문장은 …로 줄였어요. " + MADE)

# ---------- part 3: Docker Desktop and Docker Hub ----------
EB3 = "3. Docker Desktop과 Docker Hub"


def desktop(x, y, w, h, wid, active, main, attrs="", items=("Containers", "Images", "Volumes", "Builds", "Docker Hub", "Docker Scout", "Extensions"), hl=()):
    side = "".join(f'<div id="nav-{n.replace(" ", "")}" style="height:56px;padding:0 20px;border-radius:10px;display:flex;align-items:center;{"background:#E6EEF8;" if n == active else ""}">'
                   + p(f"font-size:23px;font-weight:{700 if n == active else 500};color:{INK}", n) + '</div>' for n in items)
    foot = (f'<div id="{wid}-engine" style="position:absolute;left:0;bottom:0;width:100%;height:56px;background:#F7F7F9;border-top:1px solid #E2DED5;display:flex;flex-direction:row;align-items:center;gap:12px;padding:0 22px">'
            f'<div style="width:14px;height:14px;border-radius:7px;background:{GR}"></div>' + p(f"font-size:22px;font-weight:700;color:{INK}", "Engine running") + '</div>')
    inner = (f'<div style="position:absolute;left:0;top:0;width:250px;height:calc(100% - 56px);background:#F7F7F9;border-right:1px solid #E2DED5;padding:16px 12px;display:flex;flex-direction:column;gap:4px">{side}</div>'
             + f'<div style="position:absolute;left:250px;top:0;right:0;bottom:56px">{main}</div>' + foot)
    return window(x, y, w, h, "Docker Desktop", inner, wid, attrs=attrs)


o = frame("desk-tour", EB3, "Docker Desktop은 왼쪽 메뉴 두 개만 먼저 기억해요", DK)
main = ('<div style="position:absolute;left:40px;top:34px;right:40px;display:flex;flex-direction:column;gap:22px">' + p(f"font-size:32px;font-weight:700;color:{INK}", "Containers")
        + '<div style="display:flex;flex-direction:row;gap:16px">' + bar_(260, "#E4E1DA", 40) + bar_(140, "#E4E1DA", 40) + '</div>'
        + "".join(f'<div style="height:64px;border-top:1px solid #E6E2D9;display:flex;flex-direction:row;align-items:center;gap:30px">{bar_(a)}{bar_(b_)}{bar_(c_)}</div>' for a, b_, c_ in ((160, 120, 200), (130, 150, 170), (180, 100, 140)))
        + '</div>')
WX = 700
o.append(desktop(WX, 214, 1124, 760, "dd", "Containers", main))
ny = lambda i: 214 + 54 + 16 + i * 60 + 28   # noqa: E731
for k, (i, lab, cmd_, c) in enumerate([(0, "컨테이너 목록", "docker ps -a", GR), (1, "받은 이미지 목록", "docker images", OR)]):
    ly = 250 + k * 170
    o.append(f'<div{bi("rise", k + 1)} style="position:absolute;left:96px;top:{ly}px;width:520px">'
             + p(f"font-size:30px;font-weight:700;color:{c}", lab) + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{INK};margin-top:6px", "터미널: " + cmd_) + '</div>')
    o.append(svg(f'<path d="M560,{ly + 22} L{WX - 30},{ly + 22} L{WX + 16},{ny(i)}" stroke="{c}" stroke-width="2.5" fill="none"/><circle cx="{WX + 16}" cy="{ny(i)}" r="6" fill="{c}" stroke="#FFFFFF" stroke-width="2"/>', k + 1, "fade"))
    o.append(spot(k + 1, target=f"nav-{['Containers', 'Images'][i]}", pad=6, dim=0.35))
o.append(spot(3, target="dd-engine", pad=4, dim=0.35))
o.append(spot_off(4))
o.append(f'<div{bi("rise", 3)} style="position:absolute;left:96px;top:820px;width:520px">' + p(f"font-size:30px;font-weight:700;color:{GR}", "엔진 상태") + p(f"font-size:26px;color:{INK};margin-top:6px", "Engine running이어야 명령이 돼요") + '</div>')
o.append(svg(f'<path d="M560,842 L{WX - 30},842 L{WX + 16},{214 + 760 - 29}" stroke="{GR}" stroke-width="2.5" fill="none"/><circle cx="{WX + 16}" cy="{214 + 760 - 29}" r="6" fill="{GR}" stroke="#FFFFFF" stroke-width="2"/>', 3, "fade"))
W("desk-tour", o, "Docker Desktop 왼쪽에 메뉴가 여러 개 있어요. 오늘은 두 개만 기억해요. Containers는 내 컴퓨터의 컨테이너 목록이고 터미널의 docker ps -a와 같아요. Images는 받아 둔 이미지 목록이고 docker images와 같아요. Volumes는 30에서 써요. 왼쪽 아래 엔진 상태가 Engine running이어야 터미널 명령도 돼요. " + DESK_NOTE)

o = frame("desk-list", EB3, "Containers 화면으로 상태를 보고, 명령은 터미널에서 쳐요", DK)
hdr = '<div style="display:flex;flex-direction:row;align-items:center;height:56px;border-bottom:1px solid #E6E2D9;padding:0 10px">' + "".join(p(f"width:{w_}px;font-size:21px;font-weight:700;color:{SUB}", n) for n, w_ in (("Name", 310), ("Image", 180), ("Status", 180), ("Port(s)", 160), ("Actions", 200))) + '</div>'


def crow(n, img, run_, port, rid):
    st_ = ('<div style="width:180px;display:flex;flex-direction:row;gap:10px;align-items:center">'
           f'<div style="width:14px;height:14px;border-radius:7px;background:{GR if run_ else "#B4B9C3"}"></div>' + p(f"font-size:22px;color:{INK}", "Running" if run_ else "Exited") + '</div>')
    btn = lambda t_, i_: p(f"font-size:20px;font-weight:700;color:{INK};border:2px solid #C9CED8;border-radius:9px;padding:4px 12px", t_, f' id="{i_}"')  # noqa: E731
    act = f'<div style="width:200px;display:flex;flex-direction:row;gap:10px">' + (btn("Stop", rid + "-stop") if run_ else btn("Start", rid + "-start")) + btn("Delete", rid + "-del") + '</div>'
    return (f'<div id="{rid}" style="display:flex;flex-direction:row;align-items:center;height:76px;border-bottom:1px solid #E6E2D9;padding:0 10px">'
            + p(f"width:310px;font-family:{MONO};font-size:23px;font-weight:700;color:{DK}", n) + p(f"width:180px;font-family:{MONO};font-size:22px;color:{INK}", img)
            + st_ + p(f"width:160px;font-family:{MONO};font-size:22px;color:{DK}", port) + act + '</div>')


main = ('<div style="position:absolute;left:36px;top:30px;right:30px">' + p(f"font-size:32px;font-weight:700;color:{INK};margin-bottom:22px", "Containers") + hdr
        + crow("web", "nginx", True, "8080:80", "r-web") + crow("flamboyant_thompson", "hello-world", False, "", "r-hello") + '</div>')
o.append(desktop(96, 214, 1330, 560, "dd2", "Containers", main))
o.append(spot(1, target="r-web-stop", pad=8))
o.append(spot(2, target="r-hello-start", pad=8))
o.append(spot(3, target="r-hello-del", pad=8))
o.append(spot_off(4))
maps = [("Stop", "docker stop web"), ("Start", "docker start 이름"), ("Delete", "docker rm 이름")]
for i, (b_, c_) in enumerate(maps):
    y = 820 + i * 62
    o.append(p(f"position:absolute;left:96px;top:{y}px;width:160px;font-size:28px;font-weight:700;color:{INK}", b_, bi("fade", i + 1)))
    o.append(p(f"position:absolute;left:260px;top:{y}px;font-family:{MONO};font-size:28px;font-weight:700;color:{DK}", e(c_), bi("fade", i + 1)))
o.append(p(f"position:absolute;left:1000px;top:830px;width:824px;font-size:30px;font-weight:700;line-height:1.5;color:{INK}", "버튼과 명령이 하는 일이 같아요.", bi("fade", 4)))
o.append(p(f"position:absolute;left:1000px;top:886px;width:824px;font-size:26px;line-height:1.55;color:{SUB}", "수업에서는 터미널 명령으로 하고, 결과는 이 화면으로 확인해요.", bi("fade", 4)))
W("desk-list", o, "Containers 화면에는 컨테이너마다 이름, 이미지, 상태, 포트가 한 줄씩 나와요. 초록 점은 켜짐, 회색 점은 꺼짐이에요. 줄 끝 버튼은 4파트에서 칠 명령과 같은 일을 해요. Stop은 docker stop, Start는 docker start, Delete는 docker rm이에요. 05에서 Git Graph는 결과를 그림으로 확인할 때만 썼죠. Docker Desktop도 같아요. 명령은 터미널에서 치고 결과는 이 화면으로 확인해요. 실제 화면은 버튼이 아이콘으로 나와요. " + DESK_NOTE)

o = frame("hub-search", EB3, "hub.docker.com에서 검색하면 같은 이름이 수십만 개 나와요", DK)
crop = (20, 96, 1590, 700)
k_ = sx_(crop, 1728)
h_ = shot("hub-search", crop, 96, 214, 1728, sid="s-search")
o.append(h_[0])
X = lambda v: 96 + (v - crop[0]) * k_   # noqa: E731
Y = lambda v: 214 + (v - crop[1]) * k_  # noqa: E731
o.append(pen_box(1, round(X(322)), round(Y(140)), round(232 * k_), round(34 * k_), RED))
o.append(spot(2, X(752), Y(222), 400 * k_, 222 * k_, pad=10))
o.append(spot_off(3))
o.append(caption("이름만 보고 고르지 않고, 이름 아래 마크를 봐요.", 214 + h_[1] + 30, 3, size=30))
W("hub-search", o, "브라우저에서 hub.docker.com에 들어가 위쪽 검색 칸에 nginx를 쳐 봤어요. 결과가 29만 개가 넘어요. 누구나 이미지를 올릴 수 있어서 이름이 비슷한 이미지가 아주 많아요. 그래서 이름만 보고 고르지 않고, 이름 아래 붙은 마크를 봐요. 가운데 nginx 카드에 Docker Official Image 마크가 있어요. 화면은 실제 Docker Hub 검색 결과를 찍은 거예요. 로고 그림은 찍은 환경에서 안 불러와져서 빈칸이에요.")

o = frame("hub-badge", EB3, "Docker Official Image 마크가 붙은 이미지부터 골라요", DK)
badges = [("Docker Official Image", GR, "Docker가 직접 관리하는 기본 이미지", "nginx, python, ubuntu", True),
          ("Verified Publisher", BL, "회사가 직접 올린 이미지", "nginx/nginx-ingress (NGINX Inc.)", False),
          ("Sponsored OSS", PUR, "Docker가 후원하는 오픈소스 프로젝트", "", False),
          ("Docker Hardened Image", TEAL, "보안을 더 다듬은 이미지", "", False),
          ("마크 없음", RED, "누구나 올린 이미지, 안에 무엇이 있는지 몰라요", "", False)]
for i, (n, c, d, ex, best) in enumerate(badges):
    y = 226 + i * 128
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:1px;background:{LINE}"></div>')
    ra = bi("rise", 1 if i < 1 else (2 if i < 4 else 3)) + DELAY((i % 3) * 80)
    o.append(f'<div{ra} style="position:absolute;left:96px;top:{y + 26}px;width:560px;display:flex;flex-direction:row;align-items:center;gap:14px">'
             + (f'<x-icon name="Verified" style="width:34px;height:34px;color:{c}"></x-icon>' if i < 4 else f'<x-icon name="Warning" style="width:34px;height:34px;color:{c}"></x-icon>')
             + p(f"font-size:30px;font-weight:700;color:{c}", e(n)) + '</div>')
    o.append(p(f"position:absolute;left:700px;top:{y + 22}px;width:1124px;font-size:28px;color:{INK}", e(d), ra))
    if ex:
        o.append(p(f"position:absolute;left:700px;top:{y + 66}px;width:1124px;font-family:{MONO};font-size:23px;color:{SUB}", e(ex), ra))
o.append(f'<div style="position:absolute;left:96px;top:{226 + 5 * 128}px;width:1728px;height:1px;background:{LINE}"></div>')
o.append(pulse(4, "x"))
o.append(f'<div id="x"{bi("rise", 4)} style="position:absolute;left:96px;top:{226 + 5 * 128 + 34}px;width:1728px;height:96px;background:#E8F4EC;border-radius:18px;display:flex;flex-direction:row;align-items:center;gap:26px;padding:0 34px">'
         + p(f"font-family:{MONO};font-size:34px;font-weight:700;color:{GR}", "nginx") + p(f"font-size:26px;color:{INK}", "공식 이미지는 이름에 / 가 없어요.")
         + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{BL};margin-left:30px", "회사/이름") + p(f"font-size:26px;color:{INK}", "다른 이미지는 앞에 올린 곳이 붙어요.") + '</div>')
W("hub-badge", o, "Docker Hub는 믿을 수 있는 이미지에 마크를 붙여요. 수업에서는 Docker Official Image부터 골라요. Docker가 직접 관리하고 보안 업데이트를 꾸준히 해요. nginx, python, ubuntu가 여기에 들어요. Verified Publisher는 그 소프트웨어를 만든 회사가 직접 올린 이미지예요. Sponsored OSS는 Docker가 후원하는 오픈소스 프로젝트, Docker Hardened Image는 보안을 더 다듬은 이미지예요. 마크가 없으면 누구나 올린 이미지라서 안에 무엇이 있는지 알 수 없어요. 연습할 때는 받지 않아요. 이름으로도 구별돼요. 공식 이미지는 nginx처럼 이름만 있고, 나머지는 nginx/nginx-ingress처럼 앞에 올린 곳이 붙어요. 마크 이름은 Docker Hub 검색 화면 왼쪽 Trusted content 칸에 있는 그대로 옮겼어요.")

o = frame("hub-tags", EB3, "이미지 이름 뒤 콜론 다음이 태그예요. 태그로 버전을 골라요", DK)
o += parts(96, 226, [("python", OR, "이미지 이름", "pt-name"), (":", GRAY, None, None), ("3.12-slim", BL, "태그 (버전)", "pt-tag")], size=60, order=1, lab=26, drop=26, sep=0)
crop = (40, 370, 1576, 800)
h_ = shot("hub-python-tags", crop, 96, 520, 1728, sid="s-tags")
k_ = sx_(crop, 1728)
o.append(h_[0])
o.append(spot(3, 96 + (1184 - 40) * k_, 520 + (482 - 370) * k_, 316 * k_, 42 * k_, pad=10))
o.append(spot_off(4))
rows = [("nginx", "태그를 안 쓰면 latest (최신)"), ("python:3.12", "파이썬 3.12"), ("python:3.12-slim", "필요 없는 것을 뺀 작은 버전")]
for i, (a, b_) in enumerate(rows):
    y = 214 + i * 96
    o.append(f'<div{bi("rise", 2)}{DELAY(i * 80)} style="position:absolute;left:1060px;top:{y}px;width:764px;display:flex;flex-direction:row;align-items:baseline;gap:24px">' + p(f"width:340px;font-family:{MONO};font-size:30px;font-weight:700;color:{INK}", e(a)) + p(f"font-size:25px;color:{SUB}", e(b_)) + '</div>')
W("hub-tags", o, "이미지 이름 뒤에 콜론을 찍고 태그를 붙여요. 태그는 버전 이름이에요. python:3.12는 파이썬 3.12가 든 이미지, python:3.12-slim은 그중 필요 없는 것을 빼서 작게 만든 버전이에요. 태그를 안 쓰고 nginx라고만 치면 latest, 가장 최신 태그를 받아요. 오른쪽은 실제 python 이미지의 Tags 탭에서 3.12-slim을 검색한 화면이에요. 태그마다 오른쪽에 docker pull 명령이 적혀 있어서 그대로 복사해 쓰면 돼요.")

o = frame("pull", EB3, "docker pull로 받고 docker images로 받은 이미지를 봐요", DK)
pl = OUTP("pull", "docker pull nginx")
layers = [l for l in pl if ": " in l and len(l.split(":")[0]) == 12]
head_ = pl[:2]
tail_ = [l for l in pl if l.startswith("Digest") or l.startswith("Status") or l.startswith("docker.io")]
lines = [("$", P, "docker pull nginx")] + [("o", l) for l in head_] + [("d", layers[0]), ("d", "…")] + [("o", l) for l in tail_] + [("o", ""), ("$", P, "docker images")] + [("o", l) for l in OUTP("pull", "docker images")]
t = Term(lines, 96, 214, size=29, w=1728, lh=1.45)
t.band(11, 12, order=3)
o.append(t.html())
o += tag(t, 1, "태그를 안 써서 latest", OR, 1)
o.append(pen_box(2, round(t.tx - 8), round(t.top(3) - 2), round(t.sw(layers[0][:12]) + 16), round(t.lp + 4), OR))
o += tag(t, 3, "이미지는 여러 층으로 받아요", OR, 2)
o += tag(t, 12, "받아 둔 이미지", OR, 3)
W("pull", o, "docker pull 뒤에 이미지 이름을 적으면 Docker Hub에서 받아요. 태그를 안 써서 Using default tag: latest가 나왔어요. 이미지는 여러 층으로 나뉘어 있어서 층마다 받는 줄이 나와요. 가운데 받는 줄은 …로 줄였어요. docker images는 내 컴퓨터에 받아 둔 이미지 목록이에요. 앞에서 받은 hello-world와 방금 받은 nginx가 보여요. DISK USAGE가 내 컴퓨터에서 차지하는 크기예요. Docker Desktop의 Images 화면에도 같은 목록이 나와요. " + MADE)

# ---------- part 4: run, stop, remove ----------
EB4 = "4. 컨테이너 켜고 끄기"
fg = []
with open(os.path.join(HERE, "demo-output.txt")) as f_:
    txt = f_.read()
fg = txt.split("### foreground\n", 1)[1].split("[exit", 1)[0].splitlines()[1:]
o = frame("run-fg", EB4, "docker run nginx는 터미널을 붙잡고 끝나지 않아요", GR)
lines = [("$", P, "docker run nginx")] + [("o", l) for l in fg[:3]] + [("d", "…")] + [("o", l) for l in pick(fg, "nginx/1", "start worker processes")] + [("y", "^C   (Ctrl+C)")] + [("o", l) for l in pick(fg, "SIGINT")] + [("d", "…")]
t = Term(lines, 96, 214, size=24, w=1728, lh=1.8)
t.band(8, order=2, color="rgba(255,156,148,.16)")
o.append(t.html())
o += tag(t, 6, "서버라서 계속 켜져 있어요", GR, 1, at=t.end(6) + 20)
o += tag(t, 8, "Ctrl+C를 받고 꺼져요", RED, 2)
o.append(keys(2, 1460, t.y + t.h + 40, "Ctrl+C", size=30))
o.append(caption("hello-world는 글을 찍고 바로 끝났지만,<br>nginx는 웹 서버라서 멈출 때까지 켜져 있어요.", t.y + t.h + 36, 3, width=1300, size=30))
W("run-fg", o, "이제 nginx로 컨테이너를 켜 봐요. nginx는 웹 페이지를 보내 주는 서버 프로그램이에요. docker run nginx를 치면 nginx가 켜지면서 준비 과정 글을 쭉 찍어요. 그런데 프롬프트가 돌아오지 않아요. hello-world는 글을 찍고 바로 끝났지만, 서버는 요청을 기다리느라 멈출 때까지 계속 켜져 있어요. 터미널을 쓰려면 Ctrl+C로 멈춰요. 아래 SIGINT 줄이 Ctrl+C를 받았다는 뜻이에요. 출력은 가운데를 …로 줄였어요. 실제 화면에서는 ^C 대신 커서만 보일 수 있어요. " + MADE, ("p4", "컨테이너 켜고 끄기"))

o = frame("ps-a", EB4, "docker ps -a에는 꺼진 컨테이너도 남아 있어요", GR)
psa = OUTP("foreground", "docker ps -a")
lines = [("$", P, "docker ps"), ("o", OUTP("stop", "docker ps")[0]), ("o", ""), ("$", P, "docker ps -a")] + [("o", l) for l in psa]
t = Term(lines, 96, 214, size=20, w=1728, lh=2.1)
o.append(t.html())
o += tag(t, 1, "켜진 컨테이너만: 없어요", GRAY, 1, at=t.tx + t.sw(lines[1][1].rstrip()) + 0)
nx = t.sx(4, "NAMES")
o.append(pen_box(2, round(nx - 10), round(t.top(5) - 2), round(t.sw("flamboyant_thompson") + 20), round(2 * t.lp + 4), OR))
sx_st = t.sx(4, "STATUS")
o.append(underline(3, sx_st, sx_st + t.sw("Exited (0)"), t.top(6) + t.lp - 2, GRAY))
o.append(f'<div{bi("rise", 2)} style="position:absolute;left:96px;top:{t.y + t.h + 40}px;width:820px">' + p(f"font-size:30px;font-weight:700;color:{OR}", "이름을 안 주면 Docker가 지어 줘요")
         + p(f"font-size:26px;line-height:1.5;color:{SUB};margin-top:8px", "exciting_mendeleev처럼 형용사와 과학자 이름을 섞어요. 다음 장에서 이름을 직접 붙여요.") + '</div>')
o.append(f'<div{bi("rise", 3)} style="position:absolute;left:1000px;top:{t.y + t.h + 40}px;width:824px">' + p(f"font-size:30px;font-weight:700;color:{GRAY}", "Exited는 꺼졌다는 뜻")
         + p(f"font-size:26px;line-height:1.5;color:{SUB};margin-top:8px", "꺼져도 지우기 전까지 목록에 남아요. Docker Desktop Containers 화면도 같아요.") + '</div>')
W("ps-a", o, "docker ps는 지금 켜져 있는 컨테이너 목록이에요. 방금 nginx를 Ctrl+C로 멈췄으니 아무것도 없어요. docker ps -a의 a는 all, 꺼진 것까지 전부라는 뜻이에요. hello-world와 nginx 컨테이너가 Exited 상태로 남아 있어요. 컨테이너는 꺼져도 지우기 전까지 남아요. NAMES 칸을 보면 우리가 이름을 준 적이 없는데 이름이 있어요. 이름을 안 주면 Docker가 형용사와 과학자 이름을 섞어서 지어 줘요. 이름은 실행할 때마다 달라요. " + MADE)

o = frame("run-d", EB4, "-d로 뒤에서 켜고, --name으로 이름을 붙여요", GR)
o += parts(96, 226, [("docker run", INK, None, None), ("-d", GR, "뒤에서 켜기", None), ("--name web", BL, "이름 붙이기", None), ("nginx", OR, "이미지", None)], size=52, order=1, lab=26, drop=28, stagger=True)
rid = OUTP("run-d", "docker run -d --name web nginx")[0]
lines = [("$", P, "docker run -d --name web nginx"), ("o", rid), ("$", P, "docker ps")] + [("o", l) for l in OUTP("run-d", "docker ps")]
t = Term(lines, 96, 480, size=23, w=1728, lh=1.5)
t.band(1, order=4, color="rgba(127,209,139,.14)")
o.append(t.html())
o += tag(t, 1, "컨테이너 ID, 바로 프롬프트가 돌아와요", GR, 4)
sx_st = t.sx(3, "STATUS")
o.append(underline(5, sx_st, sx_st + t.sw("Up"), t.top(4) + t.lp - 2, GR))
nx = t.sx(3, "NAMES")
o.append(pen_box(5, round(nx - 8), round(t.top(4) - 2), round(t.sw("web") + 16), round(t.lp + 4), BL))
o.append(caption("Up은 켜져 있다는 뜻이에요. 이제 이름 web으로 부를 수 있어요.", t.y + t.h + 40, 5, size=30))
W("run-d", o, "서버를 켤 때마다 터미널이 붙잡히면 불편해요. -d는 detach, 뒤에서 켜라는 옵션이에요. 켜자마자 긴 컨테이너 ID 한 줄만 찍고 프롬프트가 돌아와요. --name web은 이 컨테이너 이름을 web으로 정해요. 그다음부터 stop, start, rm, logs에 이 이름을 써요. 이미지 이름은 항상 맨 뒤에 둬요. docker ps의 STATUS가 Up이면 켜져 있는 거예요. " + MADE)

o = frame("stop-start", EB4, "docker stop으로 끄고 docker start로 다시 켜요", GR)
lines = [("$", P, "docker stop web")] + [("o", l) for l in OUTP("stop", "docker stop web")] + [("$", P, "docker ps")] + [("o", l) for l in OUTN("stop", "docker ps", 0)] \
    + [("$", P, "docker ps -a")] + [("o", l) for l in OUTP("stop", "docker ps -a")] + [("$", P, "docker start web")] + [("o", l) for l in OUTP("stop", "docker start web")] \
    + [("$", P, "docker ps")] + [("o", l) for l in OUTN("stop", "docker ps", 1)]
t = Term(lines, 96, 214, size=20, w=1728, lh=1.55)
t.band(6, order=1, color="rgba(125,134,150,.22)")
t.band(13, order=2, color="rgba(127,209,139,.14)")
o.append(t.html())
o += tag(t, 3, "켜진 것이 없어요", GRAY, 1)
o += tag(t, 6, "꺼졌어요", GRAY, 1, at=t.end(6) + 10)
o += tag(t, 13, "다시 켜졌어요", GR, 2, at=t.end(13) + 10)
o.append(caption("stop은 끄기만 해요. 컨테이너는 목록에 남아서 start로 다시 켤 수 있어요.", t.y + t.h + 36, 3, size=28))
W("stop-start", o, "docker stop web은 web 컨테이너를 꺼요. 성공하면 이름을 한 번 찍어요. docker ps에는 아무것도 없고, docker ps -a에는 web이 Exited로 남아 있어요. 끄기만 하고 지우지는 않았으니까요. docker start web으로 같은 컨테이너를 다시 켜요. 새로 만드는 게 아니라 꺼 둔 것을 다시 켜는 거라 컨테이너 ID가 그대로예요. " + MADE)

o = frame("restart", EB4, "docker restart는 끄고 켜기를 한 번에 해요", GR)
o += parts(96, 226, [("docker restart web", GR, None, None), ("=", GRAY, None, None), ("docker stop web", INK, None, None), ("+", GRAY, None, None), ("docker start web", INK, None, None)], size=44)
lines = [("$", P, "docker ps")] + [("o", l) for l in OUTN("restart", "docker ps", 0)] + [("$", P, "docker restart web")] + [("o", l) for l in OUTP("restart", "docker restart web")] \
    + [("$", P, "docker ps")] + [("o", l) for l in OUTN("restart", "docker ps", 1)]
t = Term(lines, 96, 360, size=24, w=1728, lh=1.7)
t.band(7, order=2, color="rgba(127,209,139,.14)")
o.append(t.html())
sx_st = t.sx(1, "STATUS")
o.append(underline(1, sx_st, sx_st + t.sw("Up 20 seconds"), t.top(2) + t.lp - 2, GRAY))
o += tag(t, 4, "끄고 다시 켰어요", GR, 2)
o.append(pen_box(3, round(sx_st - 8), round(t.top(7) - 2), round(t.sw("Up Less than a second") + 16), round(t.lp + 4), GR))
sx_cr = t.sx(6, "CREATED")
o.append(underline(4, sx_cr, sx_cr + t.sw("21 seconds ago"), t.top(7) + t.lp - 2, OR))
o.append(caption("STATUS는 처음부터 다시 세고, CREATED는 그대로예요. 새 컨테이너가 아니라 같은 컨테이너를 다시 켠 거예요.", t.y + t.h + 40, 4, size=30))
W("restart", o, "서버가 이상하게 굴거나 설정을 바꿨을 때는 껐다가 다시 켜요. docker stop과 docker start를 차례로 쳐도 되지만, docker restart 한 번이면 둘을 이어서 해 줘요. 다시 켠 뒤 docker ps를 보면 STATUS는 Up Less than a second로 처음부터 다시 세요. CREATED는 그대로예요. 컨테이너를 새로 만든 게 아니라 같은 컨테이너를 다시 켠 거라서 이름도, 남긴 기록도 그대로 있어요. Docker Desktop 앱 자체를 다시 켜는 건 위쪽 고래 아이콘 메뉴의 Restart예요. 이 장은 컨테이너를 다시 켜는 이야기예요. 이 출력은 따로 실행해서 컨테이너 ID가 앞 장과 달라요. " + MADE)

o = frame("life", EB4, "컨테이너는 켜짐과 꺼짐을 오가다가 rm으로 사라져요", GR)
nodes = [("n-img", "이미지 nginx", OR, "#FFF4E2", 96, 420), ("n-up", "켜짐 Up", GR, "#E8F4EC", 620, 420), ("n-ex", "꺼짐 Exited", GRAY, "#EDEBE6", 1160, 420), ("n-gone", "없어짐", RED, "#FBECEC", 1160, 760)]
for nid, n, c, bg, x, y in nodes:
    o.append(p(f"position:absolute;left:{x}px;top:{y}px;width:420px;height:120px;background:{bg};border:4px solid {c};border-radius:60px;font-size:36px;font-weight:700;line-height:112px;text-align:center;color:{c}", n, f' id="{nid}"'))
arrows = [("M516,480 L612,480", OR, "docker run", 564, 380, 1), ("M1040,450 L1152,450", GRAY, "docker stop", 1096, 368, 2), ("M1152,510 L1040,510", GR, "docker start", 1096, 560, 3), ("M1370,540 L1370,752", RED, "docker rm", 1400, 620, 4)]
for d, c, lab, lx, ly, od in arrows:
    pts = re.findall(r"[\d.]+", d)
    x2, y2, x1, y1 = float(pts[2]), float(pts[3]), float(pts[0]), float(pts[1])
    import math
    ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    o.append(svg(arrow_path(d, c, 5) + head_at(x2, y2, ang, c), od))
    o.append(p(f"position:absolute;left:{lx - 140 if od != 4 else lx}px;top:{ly}px;width:280px;text-align:{'center' if od != 4 else 'left'};font-family:{MONO};font-size:28px;font-weight:700;color:{c}", lab, bi("fade", od)))
o.append(p(f"position:absolute;left:96px;top:260px;width:900px;font-size:28px;line-height:1.5;color:{SUB}", "run은 새 컨테이너를 만들어서 켜요.<br>start는 꺼 둔 컨테이너를 다시 켜요."))
o.append(p(f"position:absolute;left:96px;top:760px;width:960px;font-size:28px;line-height:1.5;color:{SUB}", "rm은 꺼진 컨테이너만 지워요.<br>이미지를 지우는 명령은 docker rmi예요.", bi("fade", 4)))
W("life", o, "지금까지 본 명령을 한 그림에 모았어요. docker run은 이미지로 새 컨테이너를 만들어서 켜요. docker stop은 끄고, docker start는 꺼 둔 같은 컨테이너를 다시 켜요. docker rm은 꺼진 컨테이너를 지워요. 켜진 컨테이너는 바로 못 지우고 먼저 stop해야 해요. 5파트 오류에서 다시 봐요. 이미지는 컨테이너와 따로 남아 있고, 이미지까지 지울 때는 docker rmi를 써요. rmi의 i는 image예요.")

o = frame("localhost", EB4, "localhost는 내 컴퓨터, 8080은 그 안의 문 번호예요", GR)
o += parts(96, 214, [("http://", GRAY, "웹 주소 약속", None), ("localhost", BL, "내 컴퓨터", None), (":8080", OR, "문 번호 (포트)", None)], size=64, order=1, lab=28, drop=30, stagger=True, sep=0)
o.append(window(96, 540, 360, 240, "브라우저", p(f"position:absolute;left:24px;top:40px;width:310px;height:56px;background:#FFFFFF;border:2px solid #D2CEC4;border-radius:12px;font-family:{MONO};font-size:22px;line-height:52px;text-align:center;color:{INK}", "localhost:8080"), "lh-br", attrs=bi("rise", 4)))
doors = [("80", "http 기본 문", "번호를 안 적으면 여기로 가요"), ("443", "https 기본 문", "자물쇠가 붙은 주소가 쓰는 문"), ("8080", "연습용으로 자주 쓰는 문", "오늘 nginx를 이을 문")]
box = (f'<div style="position:absolute;left:600px;top:460px;width:1224px;height:430px;background:#FFFFFF;border:3px solid #9AA3B5;border-radius:26px">'
       + p(f"position:absolute;left:36px;top:26px;font-size:30px;font-weight:700;color:{BL}", "내 컴퓨터 = localhost = 127.0.0.1"))
for k, (num, name, desc) in enumerate(doors):
    dx = 50 + k * 386
    hi = num == "8080"
    box += (f'<div id="door-{num}" style="position:absolute;left:{dx}px;top:110px;width:350px;height:224px;background:{"#FFF4E0" if hi else "#F3F1EC"};border:3px solid {OR if hi else "#C9C4B8"};border-radius:18px">'
            + p(f"position:absolute;left:0;top:22px;width:350px;text-align:center;font-family:{MONO};font-size:48px;font-weight:700;color:{OR if hi else GRAY}", num)
            + p(f"position:absolute;left:0;top:98px;width:350px;text-align:center;font-size:25px;font-weight:700;color:{INK}", name)
            + p(f"position:absolute;left:20px;top:140px;width:310px;text-align:center;font-size:21px;line-height:1.4;color:{SUB}", desc) + '</div>')
box += '</div>'
o.append(box)
o.append(svg('<path id="p-lh" d="M456,660 L540,660 L540,856 L1617,856 L1617,798" fill="none" stroke="none"/>' + arrow_path("M456,660 L540,660 L540,856 L1617,856 L1617,802", OR, 5) + head_at(1617, 798, -90, OR), 5))
o.append(f'<div{PATH(5, "p-lh")} style="position:absolute;left:438px;top:642px;width:36px;height:36px;border-radius:18px;background:{OR};border:4px solid #FFFFFF;box-shadow:0 2px 6px rgba(0,0,0,.18)"></div>')
o.append(pulse(5, "door-8080"))
o.append(caption("한 컴퓨터에서 여러 프로그램이 요청을 기다려서, 문 번호로 어느 프로그램에 갈지 정해요.", 924, 6, size=30))
W("localhost", o, "localhost는 지금 앞에 있는 내 컴퓨터를 부르는 이름이에요. naver.com 같은 인터넷 주소 대신, 내 컴퓨터 안에서 켜 둔 프로그램에 들어갈 때 써요. 숫자로 적으면 127.0.0.1이고 뜻은 같아요. 한 컴퓨터 안에서 여러 프로그램이 동시에 요청을 기다릴 수 있어서, 주소 뒤의 :8080 같은 문 번호로 어느 프로그램에 갈지 정해요. 이 문 번호를 포트라고 불러요. 80은 http, 443은 https가 기본으로 쓰는 문이라 주소에 번호를 안 적어도 돼요. 8080은 연습할 때 80과 겹치지 않게 자주 고르는 번호예요. 다음 장에서 nginx에 localhost:8080으로 들어가 봐요. 그림은 단순하게 그렸어요.")

o = frame("port-why", EB4, "켜져 있는 nginx에 브라우저로 들어가면 안 열려요", GR)
err = ('<div style="display:flex;flex-direction:column;align-items:flex-start;gap:18px;padding:70px 90px">'
       + p(f"font-size:40px;font-weight:700;color:{INK}", "사이트에 연결할 수 없음") + p(f"font-size:26px;color:{SUB}", "localhost에서 연결을 거부했습니다.")
       + p(f"font-family:{MONO};font-size:22px;color:{GRAY};margin-top:20px", "ERR_CONNECTION_REFUSED") + '</div>')
o.append(browser(96, 214, 1000, 440, "localhost:8080", err, "br-err", pad="0", align="stretch").replace("justify-content:center;gap:22px", "justify-content:flex-start;gap:0"))
tc = Term([("$", P, "curl http://localhost:8080")] + [("e", l) for l in OUTP("port-why", "curl")], 96, 720, size=26, w=1728, tid="t-curl", attrs=bi("rise", 1))
o.append(tc.html())
o.append(f'<div id="ct-wall" style="position:absolute;left:1240px;top:214px;width:584px;height:440px;background:#E8F4EC;border:6px solid {GR};border-radius:26px">'
         + p(f"position:absolute;left:36px;top:30px;font-size:28px;font-weight:700;color:{GR}", "컨테이너 web")
         + p(f"position:absolute;left:150px;top:170px;width:280px;height:96px;background:#FFFFFF;border-radius:16px;font-family:{MONO};font-size:34px;font-weight:700;line-height:96px;text-align:center;color:{INK}", "nginx :80")
         + p(f"position:absolute;left:36px;top:330px;width:512px;font-size:26px;font-weight:700;line-height:1.45;color:{INK}", "닫힌 상자라서 밖에서 들어갈 문이 없어요.", bi("fade", 3)) + '</div>')
o.append(svg(arrow_path("M1110,434 L1200,434", RED, 5, dash="2 14") + f'<path d="M1196,410 L1224,458 M1224,410 L1196,458" stroke="{RED}" stroke-width="6" stroke-linecap="round"/>', 2))
o.append(shake(2, "ct-wall"))
W("port-why", o, "web 컨테이너 안에서 nginx가 켜져 있어요. 그런데 브라우저 주소창에 localhost:8080을 치면 사이트에 연결할 수 없다고 나와요. 터미널에서 curl로 주소에 들어가 봐도 연결이 안 된다고 나와요. 컨테이너는 내 컴퓨터와 분리된 닫힌 상자라서, 안에서 nginx가 80번 문으로 기다려도 밖에서 들어갈 길이 없어요. 다음 장에서 길을 이어요. curl은 주소의 내용을 터미널로 받아 보는 명령이에요. 브라우저 화면은 단순하게 그렸어요.")

o = frame("port", EB4, "-p 8080:80은 내 컴퓨터 8080번 문을 컨테이너 80번 문에 이어요", GR)
o += parts(96, 226, [("docker run -d --name web -p ", INK, None, None), ("8080", BL, None, "pp-host"), (":", GRAY, None, None), ("80", GR, None, "pp-ct"), (" nginx", OR, None, None)], size=46, sep=0)
_x0 = 96 + tw("docker run -d --name web -p ", 46)
_c1, _c2 = _x0 + tw("80", 46), _x0 + tw("8080:", 46) + tw("8", 46)
for cx_, lab_, c_, right in ((_c1, "내 컴퓨터 문", BL, True), (_c2, "컨테이너 문", GR, False)):
    o.append(f'<div{bi("fade", 1)} style="position:absolute;left:{cx_ - 1:.0f}px;top:290px;width:2px;height:30px;background:{c_}"></div>')
    st_ = f"right:{1920 - cx_ - 14:.0f}px;text-align:right" if right else f"left:{cx_ - 14:.0f}px"
    o.append(p(f"position:absolute;{st_};top:328px;font-size:24px;font-weight:700;color:{c_};white-space:nowrap", lab_, bi("pop", 1)))
o.append(f'<div style="position:absolute;left:96px;top:440px;width:700px;height:300px;background:#FFFFFF;border:3px solid #9AA3B5;border-radius:24px">'
         + p(f"position:absolute;left:30px;top:24px;font-size:26px;font-weight:700;color:{GRAY}", "내 컴퓨터")
         + p(f"position:absolute;left:30px;top:120px;width:200px;height:90px;background:#E6EEF8;border:3px solid {BL};border-radius:14px;font-family:{MONO};font-size:32px;font-weight:700;line-height:84px;text-align:center;color:{BL}", "8080")
         + f'<div id="ct-in" style="position:absolute;left:330px;top:60px;width:340px;height:210px;background:#E8F4EC;border:4px solid {GR};border-radius:20px">'
         + p(f"position:absolute;left:24px;top:16px;font-size:22px;font-weight:700;color:{GR}", "컨테이너 web")
         + p(f"position:absolute;left:24px;top:80px;width:290px;height:90px;background:#FFFFFF;border-radius:14px;font-family:{MONO};font-size:30px;font-weight:700;line-height:90px;text-align:center;color:{INK}", "nginx :80") + '</div></div>')
o.append(svg('<path id="p-port" d="M330,605 L452,605" fill="none" stroke="none"/>' + arrow_path("M330,605 L448,605", BL, 5) + head_at(452, 605, 0, BL), 2))
o.append(f'<div{PATH(2, "p-port")} style="position:absolute;left:434px;top:587px;width:36px;height:36px;border-radius:18px;background:{BL};border:4px solid #FFFFFF;box-shadow:0 2px 6px rgba(0,0,0,.18)"></div>')
sh, shh = shot("nginx-welcome", (220, 0, 900, 280), 0, 0, 900, border=False, radius=0)
o.append(browser(880, 440, 944, 470, "localhost:8080", sh.replace("position:absolute;left:0px;top:0px;", "position:relative;").replace(SHADOW, "none"), "br-ok", pad="20px 22px", attrs=bi("rise", 3)))
ps_ = OUTP("port", "docker ps")
cut = ps_[0].index("PORTS")
tp = Term([("o", "PORTS                  NAMES"), ("g", ps_[1][cut:])], 96, 790, size=24, w=700, tid="t-ports", bar=False, attrs=bi("rise", 4))
o.append(tp.html())
W("port", o, "-p는 publish, 문을 연다는 옵션이에요. 콜론 왼쪽이 내 컴퓨터의 문 번호, 오른쪽이 컨테이너 안의 문 번호예요. nginx는 컨테이너 안에서 80번 문으로 기다려요. -p 8080:80을 붙여 켜면 내 컴퓨터 8080번으로 들어온 요청이 컨테이너 80번으로 넘어가요. 그래서 브라우저에서 localhost:8080을 열면 Welcome to nginx! 화면이 나와요. docker ps의 PORTS 칸에도 0.0.0.0:8080->80/tcp가 생겼어요. 앞에서 -p 없이 만든 web은 지우고 새로 켰어요. 지우는 과정은 5파트에서 봐요. 브라우저 안 화면은 실제로 localhost:8080을 연 결과예요. docker ps 출력은 PORTS와 NAMES 칸만 남겼어요.")

o = frame("port-two", EB4, "같은 이미지로 두 개를 켤 때는 이름과 내 컴퓨터 문을 다르게 줘요", GR)
lines = [("$", P, "docker run -d --name web2 -p 8081:80 nginx")] + [("o", l) for l in OUTP("two", "docker run")] + [("$", P, "docker ps")] + [("o", l) for l in OUTP("two", "docker ps")]
t = Term(lines, 96, 214, size=21, w=1728, lh=1.5)
o.append(t.html())
px_ = t.sx(3, "PORTS")
o.append(pen_box(1, round(px_ - 8), round(t.top(4) - 2), round(t.sw("0.0.0.0:8081->80/tcp") + 16), round(2 * t.lp + 4), BL))
y0 = t.y + t.h + 50
o.append(p(f"position:absolute;left:96px;top:{y0 + 40}px;width:380px;height:120px;background:#FFF4E2;border:4px solid {OR};border-radius:20px;font-family:{MONO};font-size:40px;font-weight:700;line-height:112px;text-align:center;color:{INK}", "nginx", ' id="m2"'))
for i, (n, pt) in enumerate([("web", "localhost:8080"), ("web2", "localhost:8081")]):
    y = y0 + i * 130
    o.append(f'<div data-build-in="fly order 2" data-from="m2"{DELAY(i * 150)} style="position:absolute;left:640px;top:{y}px;width:1184px;height:104px;background:#E8F4EC;border:3px solid {GR};border-radius:52px;display:flex;flex-direction:row;align-items:center;gap:26px;padding:0 40px">'
             + p(f"width:160px;font-family:{MONO};font-size:34px;font-weight:700;color:{INK}", n) + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{BL}", pt) + p(f"margin-left:auto;font-size:24px;color:{SUB}", "같은 Welcome 화면") + '</div>')
o.append(svg(arrow_path(f"M484,{y0 + 100} L630,{y0 + 52}", OR, 4) + arrow_path(f"M484,{y0 + 100} L630,{y0 + 182}", OR, 4), 2))
W("port-two", o, "틀 하나로 붕어빵을 여러 개 찍듯이 nginx 이미지 하나로 컨테이너를 두 개 켤 수 있어요. 이름은 겹치면 안 돼서 web2로 주고, 내 컴퓨터 문도 8080은 web이 쓰고 있으니 8081로 줘요. 컨테이너 안의 문은 둘 다 80이어도 괜찮아요. 각자 다른 상자라서요. 브라우저에서 localhost:8080과 localhost:8081이 둘 다 열려요. " + MADE)

o = frame("logs", EB4, "docker logs로 컨테이너가 남긴 기록을 봐요", GR)
lg = OUTP("logs", "docker logs web")
gets = [l for l in lg if "GET /" in l]
lines = [("$", P, "docker logs web"), ("o", lg[0]), ("d", "…"), ("o", next(l for l in lg if "start worker process " in l))] + [("o", l) for l in gets]
t = Term(lines, 96, 214, size=25, w=1728, lh=1.9)
t.band(4, 3 + len(gets), order=1, color="rgba(143,179,255,.16)")
o.append(t.html())
gx = t.sx(4, '"GET / HTTP/1.1"')
o.append(underline(2, gx, gx + t.sw('"GET / HTTP/1.1" 200'), t.top(4) + t.lp - 2, BL))
o.append(f'<div{bi("rise", 1)} style="position:absolute;left:96px;top:{t.y + t.h + 40}px;width:1728px">'
         + p(f"font-size:30px;font-weight:700;color:{BL}", f"localhost:8080에 {len(gets)}번 들어온 기록이에요.")
         + p(f"font-size:26px;line-height:1.5;color:{SUB};margin-top:8px", "GET /는 첫 화면을 달라는 요청, 200은 잘 보냈다는 뜻이에요. Docker Desktop에서 컨테이너 이름을 누르면 같은 기록이 보여요.") + '</div>')
W("logs", o, "컨테이너는 뒤에서 켜져 있어서 무슨 일이 있었는지 안 보여요. docker logs web은 web 컨테이너가 지금까지 찍은 글을 보여 줘요. 위쪽은 켜질 때 준비 과정이고, 아래 파란 줄은 localhost:8080에 들어올 때마다 nginx가 남긴 기록이에요. GET /는 첫 화면을 달라는 요청, 200은 잘 보냈다는 뜻이에요. 서버가 이상하면 제일 먼저 logs를 봐요. 앞쪽 172.17.0.1은 Docker 안에서 본 내 컴퓨터 주소예요. 출력은 가운데를 …로 줄였어요. 이 출력은 curl로 들어갔을 때라 끝에 curl이 보여요. 브라우저로 들어가면 그 자리에 브라우저 이름이 나와요. " + MADE)

o = frame("run-it", EB4, "-it로 우분투 컨테이너 안에 들어가서 명령을 쳐요", GR)
o += parts(96, 226, [("docker run", INK, None, None), ("-it", GR, "키보드로 치고 화면으로 보기", None), ("--name my-server", BL, "이름 붙이기", None),
                     ("ubuntu:24.04", OR, "이미지:태그", None), ("bash", PUR, "안에서 켤 프로그램", None)], size=46, order=1, lab=26, drop=28, stagger=True)
ub = OUTP("ubuntu", "docker run -it --name my-server")
sess = ub[ub.index(next(l for l in ub if l.startswith("Status:"))) + 1:]
lines = [("$", P, "docker run -it --name my-server ubuntu:24.04 bash"), ("o", ub[0]), ("d", "…")]
skip_ls = False
for l in sess:
    if l.startswith("root@"):
        pr, c = l.split("# ", 1)
        skip_ls = c == "ls"
        if not skip_ls:
            lines.append(("#", pr + "#", c))
    elif l and not skip_ls and not l.startswith("[exit"):
        lines.append(("o", l))
t = Term(lines, 96, 470, size=24, w=1728, lh=1.5)
o.append(t.html())
prompt = lines[3][1]
o.append(underline(6, t.tx, t.tx + t.sw(prompt), t.top(3) + t.lp - 2, GR))
o += tag(t, 3, "root@로 바뀌면 컨테이너 안이에요", GR, 6)
vi = next(i for i, l in enumerate(lines) if l[0] == "o" and l[1].startswith("PRETTY_NAME"))
vx = t.sx(vi, '"Ubuntu')
o.append(pen_box(7, round(vx - 4), round(t.top(vi) - 2), round(t.sw('"Ubuntu 24.04.5 LTS"') + 8), round(t.lp + 4), OR))
ei = next(i for i, l in enumerate(lines) if l[0] == "#" and l[2] == "exit")
o += tag(t, ei, "exit로 나오면 컨테이너도 꺼져요", GRAY, 8)
o.append(caption("내 컴퓨터가 Windows나 Mac이어도 01에서 배운 리눅스 명령을 바로 쳐 볼 수 있어요.", t.y + t.h + 36, 8, size=30))
W("run-it", o, "nginx는 뒤에서 켜 두는 서버였어요. 이번에는 컨테이너 안에 들어가서 직접 명령을 쳐 봐요. -it는 -i와 -t를 합친 옵션이에요. -i는 내 키보드 입력을 컨테이너에 보내고, -t는 터미널 화면을 붙여 줘요. --name my-server로 이름을 붙이고, 이미지 ubuntu:24.04 뒤에 안에서 켤 프로그램 bash를 적어요. 순서는 옵션, 이미지, 안에서 켤 프로그램이에요. 프롬프트가 root@ID:/#로 바뀌면 컨테이너 안이에요. 여기는 작은 우분투 리눅스라서 01에서 배운 ls, cd, cat을 그대로 쓸 수 있어요. exit로 나오면 bash가 끝나면서 컨테이너도 꺼져요. docker ps -a에 Exited로 남아요. 켜 둔 컨테이너에 다시 들어가는 docker exec는 다음 챕터 30에서 배워요. 가운데 받는 줄과 ls 출력은 줄였어요. 프롬프트의 ID는 컨테이너마다 달라요. " + MADE)

# ---------- part 5: common errors ----------
EB5 = "5. 자주 나는 오류"


def wrap(s_, n):
    """split a long error line at spaces so each piece is at most n characters (no characters change)"""
    out, cur = [], ""
    for w_ in s_.split(" "):
        if cur and len(cur) + 1 + len(w_) > n:
            out.append(cur)
            cur = w_
        else:
            cur = (cur + " " + w_) if cur else w_
    out.append(cur)
    return out


def err_slide(sid, title, cmd_, err_lines, key, why, fix_lines, fix_note, notes, section=None, extra_top=None):
    o = frame(sid, EB5, title, RED)
    lines = [("$", P, cmd_)] + [("e", l) for l in err_lines]
    t = Term(lines, 96, 214, size=26, w=1728, lh=1.5)
    o.append(t.html())
    for i, l in enumerate(err_lines, 1):
        if key in l:
            x0 = t.sx(i, key)
            o.append(underline(1, x0, x0 + t.sw(key), t.top(i) + t.lp - 2, RED))
            break
    y = t.y + t.h + 40
    o.append(f'<div{bi("rise", 1)} style="position:absolute;left:96px;top:{y}px;width:1728px;display:flex;flex-direction:row;gap:18px;align-items:baseline">'
             + p(f"font-size:28px;font-weight:700;color:{RED};flex:none", "뜻") + p(f"font-size:32px;font-weight:700;color:{INK}", why) + '</div>')
    y += 90
    o.append(p(f"position:absolute;left:96px;top:{y}px;font-size:28px;font-weight:700;color:{GR}", "고치기", bi("rise", 2)))
    tf = Term(fix_lines, 96, y + 50, size=28, w=1100, tid=f"{sid}-fix", attrs=bi("rise", 2), lh=1.5)
    o.append(tf.html())
    o.append(p(f"position:absolute;left:1240px;top:{y + 50}px;width:584px;font-size:27px;line-height:1.55;color:{SUB}", fix_note, bi("rise", 2)))
    W(sid, o, notes, section)


err_slide("err-daemon", "failed to connect to the docker API가 나오면 Docker Desktop을 켜요",
          "docker ps", wrap(OUTP("daemon-off", "docker ps")[0], 100), "failed to connect to the docker API",
          "Docker Desktop(엔진)이 꺼져 있어서 명령을 받을 곳이 없어요.",
          [("o", "Docker Desktop 열기"), ("d", "왼쪽 아래 Engine running 기다리기"), ("$", P, "docker ps")],
          "컴퓨터를 다시 켠 뒤에 자주 나요. 엔진이 켜지는 동안 1~2분 기다려요.",
          "제일 자주 만나는 오류예요. docker 명령은 터미널이 Docker Desktop의 엔진에 일을 시키는 구조라서, Docker Desktop이 꺼져 있으면 일을 받을 곳이 없어요. Docker Desktop을 열고 왼쪽 아래가 Engine running이 될 때까지 기다린 뒤 다시 쳐요. 메시지 가운데 경로는 컴퓨터마다 달라요. 화면은 Mac 경로예요. Windows에서는 npipe로 시작하는 경로가 나와요. Docker 버전에 따라 Cannot connect to the Docker daemon으로 시작하는 문장으로 나오기도 해요. 같은 뜻이에요. 출력은 Mac과 같은 경로로 실제 docker를 실행해서 받았어요.", ("p5", "자주 나는 오류"))

err_slide("err-rm", "켜진 컨테이너는 rm으로 바로 못 지워요",
          "docker rm web", wrap(OUTP("error-rm-running", "docker rm web")[0], 100), "container is running",
          "web이 아직 켜져 있어요. 끄고 나서 지워요.",
          [("$", P, "docker stop web"), ("o", "web"), ("$", P, "docker rm web"), ("o", "web")],
          "지운 컨테이너는 되살릴 수 없어요. 이미지는 남아 있어서 docker run으로 새로 켜면 돼요.",
          "켜진 컨테이너를 docker rm으로 지우려고 하면 container is running이 나와요. 실수로 돌아가는 서버를 지우지 않게 막아 주는 거예요. 메시지 끝의 force remove는 -f 옵션으로 강제로 지우는 방법인데, 수업에서는 docker stop으로 끄고 docker rm으로 지우는 두 단계로 해요. 지운 컨테이너는 되살릴 수 없지만 이미지는 남아 있어서 docker run으로 새로 켜면 돼요. " + MADE)

err_slide("err-name", "Conflict. The container name이 나오면 이름이 겹친 거예요",
          "docker run -d --name web -p 8080:80 nginx", wrap(OUTP("error-name", "docker run")[0], 100) + [""] + OUTP("error-name", "docker run")[2:], "is already in use",
          "web이라는 컨테이너가 이미 있어요. 꺼져 있어도 이름은 그대로 차지해요.",
          [("$", P, "docker ps -a"), ("d", "web이 있는지 보고"), ("$", P, "docker stop web"), ("$", P, "docker rm web")],
          "지우기 싫으면 --name web3처럼 다른 이름으로 켜요.",
          "같은 이름으로 컨테이너를 또 만들면 Conflict가 나요. web이 켜져 있든 꺼져 있든 docker ps -a 목록에 있으면 이름을 차지하고 있어요. docker ps -a로 확인하고, 필요 없으면 stop과 rm으로 지운 뒤 다시 켜요. 앞의 컨테이너를 남겨 두고 싶으면 다른 이름을 주면 돼요. 메시지 가운데 긴 숫자는 이미 있는 컨테이너의 ID예요. " + MADE)

perr = OUTP("error-port", "docker run")
err_slide("err-port", "port is already allocated가 나오면 내 컴퓨터 문이 이미 쓰이고 있어요",
          "docker run -d --name web2 -p 8080:80 nginx", [perr[0]] + wrap(perr[1], 100) + [""] + perr[3:], "port is already allocated",
          "8080번 문은 web이 쓰고 있어요. 한 문에는 하나만 이을 수 있어요.",
          [("$", P, "docker rm web2"), ("$", P, "docker run -d --name web2 -p 8081:80 nginx")],
          "실패해도 web2가 Created 상태로 남아서 먼저 지워요. 그다음 다른 문 번호로 켜요.",
          "web이 내 컴퓨터 8080번 문을 쓰고 있는데 web2도 8080에 이으려고 하면 port is already allocated가 나와요. 내 컴퓨터의 한 문에는 컨테이너 하나만 이을 수 있어요. 첫 줄의 긴 ID를 보면 컨테이너는 만들어졌어요. docker ps -a로 보면 web2가 Created 상태로 남아 있어요. 그래서 docker rm web2로 지우고 8081처럼 다른 문 번호로 다시 켜요. Docker가 아닌 다른 프로그램이 8080을 쓰고 있어도 같은 오류가 나요. " + MADE)

err_slide("err-rmi", "이미지를 쓰는 컨테이너가 남아 있으면 rmi가 안 돼요",
          "docker rmi nginx", wrap(OUTP("error-rmi", "docker rmi nginx")[0], 100), "is using its referenced image",
          "꺼진 컨테이너라도 이 이미지로 만든 것이 남아 있어요.",
          [("$", P, "docker ps -a"), ("d", "nginx로 만든 컨테이너 이름 찾기"), ("$", P, "docker rm exciting_mendeleev"), ("$", P, "docker rmi nginx")],
          "4파트 처음에 Ctrl+C로 멈춘 nginx 컨테이너가 남아 있었어요.",
          "web과 web2를 다 지웠는데도 docker rmi nginx가 안 돼요. 메시지를 보면 a669a15ddb87 컨테이너가 이 이미지를 쓰고 있대요. 4파트 처음에 Ctrl+C로 멈춘 nginx 컨테이너가 꺼진 채로 남아 있었어요. 틀로 찍은 붕어빵이 하나라도 남아 있으면 틀을 버릴 수 없는 셈이에요. docker ps -a로 이름을 찾아 docker rm으로 지운 뒤 rmi를 다시 쳐요. 메시지의 must be forced는 -f로 강제로 지우는 방법인데 수업에서는 쓰지 않아요. 컨테이너 이름은 실행할 때마다 달라요. " + MADE)

# ---------- part 6: practice ----------
EB6 = "6. 실습"
o = frame("x-python", EB6, "파이썬을 설치하지 않고 3.11과 3.12를 바로 비교해요", PUR)
c11 = OUTP("python", "docker run python:3.11")
c12 = OUTP("python", "docker run python:3.12")
CODE_PY = "menu = {\"latte\": 4500}; print(f\"라떼: {menu[\"latte\"]}원\")"
lines = [("$", P, "docker run python:3.11 python -c '" + CODE_PY + "'"), ("d", c11[0]), ("d", "…")] + [("e", l) for l in c11 if l.startswith("  File") or l.startswith("    ") or l.startswith("SyntaxError")] \
    + [("o", ""), ("$", P, "docker run python:3.12 python -c '" + CODE_PY + "'"), ("d", c12[0]), ("d", "…"), ("g", c12[-1])]
t = Term(lines, 96, 214, size=22, w=1728, lh=1.45)
t.band(6, order=1, color="rgba(255,156,148,.14)")
t.band(11, order=2, color="rgba(127,209,139,.16)")
o.append(t.html())
o += tag(t, 6, "3.11은 이 문법을 몰라요", RED, 1)
o += tag(t, 11, "3.12는 돼요", GR, 2)
im = OUTP("python", "docker images")
t2 = Term([("$", P, "docker images")] + [("o", l) for l in im], 96, t.y + t.h + 30, size=22, w=1100, tid="t-im", attrs=bi("rise", 3))
o.append(t2.html())
o.append(p(f"position:absolute;left:1260px;top:{t2.y + 10}px;width:564px;font-size:27px;line-height:1.5;color:{INK}", "1파트의 kim과 lee 문제를 내 컴퓨터 하나에서 다시 봤어요.", bi("rise", 3)))
o.append(p(f"position:absolute;left:1260px;top:{t2.y + 110}px;width:564px;font-size:25px;line-height:1.5;color:{SUB}", "이미지가 1GB가 넘어요. 다 쓰면 docker rmi로 지워요.", bi("rise", 3)))
W("x-python", o, "1파트 첫 장의 문제를 직접 풀어 봐요. 내 컴퓨터에 파이썬 3.11이나 3.12를 따로 설치하지 않아도, Docker Hub의 공식 python 이미지로 두 버전을 바로 켤 수 있어요. docker run 이미지 뒤에 적은 python -c '코드'는 컨테이너 안에서 실행할 명령이에요. 3.11에서는 SyntaxError, 3.12에서는 라떼: 4500원이 나와요. 팀원 모두 같은 이미지를 쓰면 \"제 컴퓨터에선 되는데요\"가 없어져요. python 이미지는 1GB가 넘으니 다 쓰면 컨테이너를 rm으로 지우고 docker rmi python:3.11 python:3.12로 지워요. 받는 줄은 …로 줄였어요. 따옴표가 많으니 복사 버튼으로 복사해서 붙여 넣어요. " + MADE, ("p6", "실습"))

o = frame("x-lost", EB6, "컨테이너를 지우면 안에 쌓인 기록도 같이 사라져요", PUR)
lost = OUTP("lost", "docker logs web")
before = [l for l in OUTP("logs", "docker logs web") if "GET /" in l]
t1 = Term([("$", P, "docker logs web"), ("d", "…")] + [("o", l[:52] + "…") for l in before], 96, 214, size=24, w=840, tid="t-b", lh=1.5)
t1.band(2, 1 + len(before), order=None, color="rgba(143,179,255,.16)")
o.append(t1.html())
o.append(p(f"position:absolute;left:96px;top:{214 + t1.h + 18}px;font-size:26px;font-weight:700;color:{BL}", f"지우기 전: 들어온 기록 {len(before)}줄"))
t2 = Term([("$", P, "docker stop web"), ("$", P, "docker rm web"), ("$", P, "docker run -d --name web -p 8080:80 nginx"), ("$", P, "docker logs web"), ("o", lost[0][:52] + "…"), ("d", "…")], 984, 214, size=24, w=840, tid="t-a", lh=1.5, attrs=bi("rise", 1))
o.append(t2.html())
o.append(p(f"position:absolute;left:984px;top:{214 + t2.h + 18}px;font-size:26px;font-weight:700;color:{RED}", "새로 켠 뒤: GET 줄이 없어요", bi("rise", 1)))
yb = 214 + max(t1.h, t2.h) + 110
o.append(f'<div{bi("rise", 2)} style="position:absolute;left:96px;top:{yb}px;width:1728px;height:230px;background:#F0EBFD;border-radius:24px;padding:34px 44px">'
         + p(f"font-size:32px;font-weight:700;color:{PUR}", "다음 챕터 30에서")
         + p(f"font-size:28px;line-height:1.6;color:{INK};margin-top:12px", "볼륨으로 컨테이너 밖에 데이터를 남기고,<br>내 파이썬 프로그램을 이미지로 만들어요.") + '</div>')
W("x-lost", o, "logs 장에서 web에는 localhost:8080에 들어온 기록이 쌓여 있었어요. web을 stop, rm으로 지우고 같은 명령으로 새로 켠 뒤 logs를 보면 켜질 때 준비 과정만 있고 GET 줄이 없어요. 컨테이너 안에 쌓인 것은 컨테이너를 지우면 같이 사라져요. 로그뿐 아니라 컨테이너 안에서 만든 파일도 같아요. 그래서 데이터베이스처럼 남겨야 하는 데이터는 컨테이너 밖에 둬요. 그 방법인 볼륨과, 내 프로그램을 이미지로 만드는 Dockerfile을 30에서 배워요. 출력은 화면에 맞게 줄 뒤쪽을 …로 줄였어요. " + MADE)

# ---------- summary ----------
o = frame("cheatsheet", "정리", "한 장 요약", INK)
groups = [("확인", TEAL, [("docker --version", "설치된 버전"), ("docker run hello-world", "설치 확인")]),
          ("이미지 (틀)", OR, [("docker pull 이름:태그", "Hub에서 받기"), ("docker images", "받은 이미지 목록"), ("docker rmi 이름", "이미지 지우기")]),
          ("컨테이너 (붕어빵)", GR, [("docker run -d --name 이름 -p 8080:80 이미지", "새로 만들어 뒤에서 켜기"), ("docker ps / docker ps -a", "켜진 것 / 전부"), ("docker stop 이름 / docker start 이름", "끄기 / 다시 켜기"), ("docker restart 이름", "껐다가 다시 켜기"),
                                  ("docker rm 이름", "지우기 (끈 다음에)"), ("docker logs 이름", "남긴 기록 보기"),
                                  ("docker run -it --name 이름 이미지 bash", "안에 들어가기 (exit로 나오기)")])]
xs = [96, 96, 900]
ys = [220, 520, 220]
for (t_, c, rows), x, y0 in zip(groups, xs, ys):
    w_ = 740 if x == 96 else 924
    o.append(p(f"position:absolute;left:{x}px;top:{y0}px;font-size:30px;font-weight:700;color:{c}", e(t_)))
    o.append(f'<div style="position:absolute;left:{x}px;top:{y0 + 50}px;width:{w_}px;height:3px;background:{c}"></div>')
    for j, (k, d) in enumerate(rows):
        y = y0 + 76 + j * (100 if len(rows) <= 6 else 88)
        o.append(p(f"position:absolute;left:{x}px;top:{y}px;width:{w_}px;font-family:{MONO};font-size:{24 if len(k) > 34 else 27}px;font-weight:700;color:{INK};white-space:nowrap", e(k)))
        o.append(p(f"position:absolute;left:{x}px;top:{y + 42}px;width:{w_}px;font-size:23px;color:{SUB}", e(d)))
o.append(caption("이미지는 Docker Official Image 마크부터 골라요. 명령은 터미널, 확인은 Docker Desktop이에요.", 920, None, size=28))
W("cheatsheet", o, "오늘 쓴 명령을 세 묶음으로 모았어요. 설치 확인 두 개, 이미지 세 개, 컨테이너 일곱 줄이에요. 이미지는 Docker Hub에서 Docker Official Image 마크가 붙은 것부터 골라요. 명령은 터미널에서 치고, 결과는 Docker Desktop 화면으로 확인해요. 실습이 끝나면 docker ps -a와 docker images로 남은 것을 확인하고 rm, rmi로 정리해요. 다음 챕터 30에서는 볼륨과 Dockerfile을 배워요.", ("trouble", "정리"))

# ---------- toc ----------
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
plist = [(BL, "Docker가 뭔가요", "컨테이너, 이미지와 컨테이너, 가상 머신과 비교", "why", "vm"),
         (TEAL, "설치하기", "Windows WSL 2, Mac 칩 고르기, hello-world", "win-check", "check"),
         (DK, "Docker Desktop과 Docker Hub", "화면 둘러보기, 공식 마크, 태그, docker pull", "desk-tour", "pull"),
         (GR, "컨테이너 켜고 끄기", "run, ps, stop, start, restart, rm, -p 8080:80, logs, -it", "run-fg", "run-it"),
         (RED, "자주 나는 오류", "엔진 꺼짐, 켜진 채 rm, 이름, 포트, rmi", "err-daemon", "err-rmi"),
         (PUR, "실습", "파이썬 버전 비교, 지우면 사라지는 기록", "x-python", "x-lost")]
o = frame("toc", "", "오늘의 순서", INK)
for i, (c, h, s_, a, b) in enumerate(plist):
    y = 210 + i * 120
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:1px;background:{LINE}"></div>')
    o.append(p(f"position:absolute;left:96px;top:{y + 16}px;width:80px;font-size:54px;font-weight:900;line-height:1.5;color:{c}", str(i + 1)))
    o.append(p(f"position:absolute;left:200px;top:{y + 18}px;font-size:36px;font-weight:700;color:{INK}", h))
    o.append(p(f"position:absolute;left:200px;top:{y + 70}px;font-size:24px;font-weight:500;color:{SUB}", e(s_)))
    o.append(p(f"position:absolute;left:1524px;top:{y + 36}px;width:300px;text-align:right;font-size:30px;font-weight:700;color:{GRAY}", f"{page[a]}–{page[b]}쪽"))
o.append(f'<div style="position:absolute;left:96px;top:{210 + 6 * 120}px;width:1728px;height:1px;background:{LINE}"></div>')
o.append(p(f"position:absolute;left:96px;top:{210 + 6 * 120 + 36}px;font-size:26px;color:{SUB}", f"{page['cheatsheet']}쪽은 한 장 요약이에요."))
o = [x for x in o if 'id="eyebrow"' not in x]
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(o) + f"\n<aside>{e('여섯 파트로 나눴어요. 1파트에서 Docker가 무엇인지 그림으로 보고, 2파트에서 Windows와 Mac에 설치해요. 3파트에서 Docker Desktop 화면과 Docker Hub에서 이미지 고르는 법을 보고, 4파트에서 nginx 컨테이너를 켜고 끄고 브라우저로 열고, 우분투 컨테이너 안에 들어가 봐요. 5파트는 자주 나는 오류 다섯 가지, 6파트는 실습이에요.')}</aside>\n</section>\n")

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-12T01:00:00Z"}, "lists": "css", "title": "Docker 1 (컨테이너 실행하기)", "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
for w_ in WARN:
    print("WARN", w_)
print(len(ORDER), "slides")
