"""Generates every slide of the merge-ways deck and slides/deck.json.

One example for every method: A, B on main, then C on main and D, E on feature/login-button.
Each commit dot carries a letter and its hash sits under the dot. Elements keep the same id across
scenes so the magic transition animates only what the command changed.

Design (tools/DESIGN.md, Stageshow): the commit graph is the hero, drawn large on the slide with no panel
behind it. The terminal is only as wide as its lines. What changed gets one short label tied to it by a
leader line (note()), in place of a caption card. Lists and tables use hairlines, not a card per row.
Highlights come from tools/highlight.py (tools/HIGHLIGHT.md). No typing animation.
Terminal output comes from tools/demo.sh (git 2.43), run at /tmp/merge-demo.
Usage: python3 tools/gen.py slides
"""
import html, json, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from highlight import spot, spot_off, cursor, cursor_off, box, underline  # noqa: E402

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
INK, SUB, MUTE, LINE = "#1D2330", "#4A5262", "#6A7180", "#E1DED6"
BL, GR, OR, PUR, RED, NAVY, TEAL = "#2459C9", "#1F8A4C", "#B26A00", "#5A3BB8", "#A33131", "#1E3F8F", "#0F7C86"
C_FF, C_MG, C_RB, C_SQ, C_PL = BL, NAVY, OR, TEAL, "#3A4150"   # one colour per method

COL = {  # node fill, light edge
    "main": (BL, "#9DB8F2"), "green": (GR, "#9ED3B4"), "gray": ("#7A8394", "#C3C8D2"),
    "purple": (PUR, "#C4B5EE"), "teal": (TEAL, "#9ED6DB"),
}
TAG = {
    "main": f"background:{BL};color:#FFFFFF",
    "green": f"background:{GR};color:#FFFFFF",
    "origin": "background:#E7DEFC;color:#4A2FA8;border:2px solid #8E6FEA",
}
TC = {"$": "#F2C46D", "o": "#D8DEE9", "g": "#7FD18B", "r": "#F28B82", "#": "#8C95A6"}


def e(s):
    return html.escape(s, quote=False)


def p(style, text, attrs=""):
    return f'<p{attrs} style="{style}">{text}</p>'


def text_w(t, size):
    """Rough ink width: Latin letters are 0.6 em in JetBrains Mono, Hangul about 1 em."""
    return sum(size if ord(ch) > 0x2E80 else size * 0.6 for ch in t)


def sans_w(t, size):
    """Rough ink width of bold Noto Sans KR: Hangul 1 em, Latin and digits about 0.58 em, spaces 0.28 em."""
    return sum(size if ord(ch) > 0x2E80 else size * 0.28 if ch == " " else size * 0.58 for ch in t)


ORDER, SECTIONS = [], {}
ANCH = {}      # element boxes (x, y, w, h) on the slide being drawn, for note()
LINES = []     # terminal line boxes (x, y, w, h) of the slide being drawn


def W(sid, parts, notes, section=None):
    if section:
        SECTIONS[section[0]] = {"description": section[1], "start": sid}
    ORDER.append(sid)
    with open(os.path.join(OUT, sid + ".html"), "w") as f:
        f.write("\n".join(parts) + f"\n<aside>{e(notes)}</aside>\n</section>\n")


def sec(sid, transition="fade", bg="#F6F5F1"):
    ANCH.clear()
    LINES.clear()
    return f'<section id="{sid}" data-transition="{transition}" style="background:{bg};color:{INK};font-family:{SANS};padding:96px;display:flex;flex-direction:column">'


def head(eyebrow, title, color):
    return [p(f"position:absolute;left:96px;top:48px;width:1728px;font-size:26px;font-weight:700;color:{color}", e(eyebrow), ' id="eyebrow"'),
            f'<h2 id="title" style="position:absolute;left:96px;top:92px;width:1728px;font-size:56px;font-weight:700;line-height:1.2;color:{INK}">{title}</h2>']


TPAD, TGAP = 20, 4


def terminal(lines, left=96, top=196, size=(30, 24), tid="term", w=None, attrs=""):
    """A terminal only as wide as its longest line. lines: [(kind, text)], kind "$" is a command,
    "#" a grey comment, others output colours. Line boxes go to LINES for pen boxes and underlines."""
    raw = [(k, ("$ " if k == "$" else "") + t.replace("\t", " " * 8)) for k, t in lines]
    tw = max(text_w(r, size[0] if k == "$" else size[1]) for k, r in raw)
    width = w or round(tw + 64 + 8)
    o = [f'<div id="{tid}"{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{width}px;background:#1B2029;border-radius:20px;padding:{TPAD}px 32px;display:flex;flex-direction:column;gap:{TGAP}px;font-family:{MONO};font-variant-ligatures:none">']
    y = top + TPAD
    for (kind, text), (_, r) in zip(lines, raw):
        fs = size[0] if kind == "$" else size[1]
        t = e(r)
        lead = len(t) - len(t.lstrip(" "))
        t = "&#160;" * lead + t.lstrip(" ")
        weight = "font-weight:700;" if kind == "$" else ""
        o.append(p(f"font-size:{fs}px;{weight}line-height:1.35;white-space:pre;color:{TC[kind]}", t if t else "&#160;"))
        LINES.append((left + 32, y, text_w(r, fs), fs * 1.35))
        y += fs * 1.35 + TGAP
    o.append('</div>')
    ANCH[tid] = (left, top, width, y - TGAP + TPAD - top)
    return o


def pen(order, i, color=RED, j=None):
    """Pen box around terminal line i (through line j)."""
    x, y, w, h = LINES[i]
    if j is not None:
        y2 = LINES[j][1] + LINES[j][3]
        w = max(LINES[k][2] for k in range(i, j + 1))
        h = y2 - y
    return box(order, round(x - 12), round(y - 3), round(w + 24), round(h + 6), color)


# ---------- commit graph ----------
BIG = dict(x0=300, step=250, up=620, main=800, solo=700, r=40, lf=34, hf=26, tf=28, th=44)
EX = dict(BIG, x0=240, step=220, main=820, solo=740)     # the worked examples have six columns


def tag_w(text, tf):
    return round(len(text) * tf * 0.6 + tf * 1.2)


def graph(nodes, edges, tags=(), head_tag=None, g=BIG, pre="", build=""):
    """nodes: {key: (col, lane, colour, kind, letter, hash)}  kind: n | merge | ghost (not committed yet) | gone (old copy) | far (only on GitHub)
    edges: [(from_key, to_key)]   tags: [(name, key, kind)] stacked in list order per node
    head_tag: name of the tag HEAD points at.  build: data-build-in for every element (mini graphs)."""
    o = []
    if "solo" in g and not any(v[1] == "up" for v in nodes.values()):
        g = dict(g, main=g["solo"])      # one row only: move it up into the free space
    X = lambda c: g["x0"] + c * g["step"]
    r = g["r"]
    ba = f' data-build-in="{build}"' if build else ""
    for a, b in edges:
        ca, la, cola, ka = nodes[a][:4]
        cb, lb, colb, kb = nodes[b][:4]
        x1, y1, x2, y2 = X(ca), g[la], X(cb), g[lb]
        light = COL[cola if (lb == "main" and la != "main") else colb][1]
        dashed = kb in ("ghost", "gone", "far") or ka == "gone"
        if "gone" in (ka, kb):
            light = COL["gray"][1]
        w = max(3, r // 6)
        if y1 == y2:
            st = f"border-top:{w}px dashed {light}" if dashed else f"background:{light}"
            o.append(f'<div id="{pre}e-{a}-{b}"{ba} style="position:absolute;left:{x1 + r}px;top:{y1 - w // 2}px;width:{x2 - x1 - 2 * r}px;height:{w}px;{st}"></div>')
        else:
            dash = ";border-style:dashed" if dashed else ""
            o.append(f'<x-connector id="{pre}e-{a}-{b}"{ba} x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" style="color:{light};border-width:{w}px{dash}"></x-connector>')
    for k, (col, lane, colour, kind, letter, h) in nodes.items():
        x, y = X(col), g[lane]
        fill = COL[colour][0]
        bw = max(3, r // 7)
        st = {"merge": f"background:#FFFFFF;border:{max(4, r * 3 // 10)}px solid {fill};color:{fill}",
              "ghost": f"background:#FDFCF9;border:{bw}px dashed {fill};color:{fill}",
              "far": f"background:#FDFCF9;border:{bw}px dashed {fill};color:{fill}",
              "gone": f"background:#FDFCF9;border:{bw}px dashed #B4BAC5;color:#9AA0AB"}.get(kind, f"background:{fill};border:{bw}px solid {fill};color:#FFFFFF")
        o.append(f'<div id="{pre}n-{k}"{ba} style="position:absolute;left:{x - r}px;top:{y - r}px;width:{2 * r}px;height:{2 * r}px;border-radius:50%;{st};display:flex;align-items:center;justify-content:center">'
                 + p(f"font-family:{MONO};font-size:{g['lf']}px;font-weight:700;line-height:1;color:inherit", e(letter)) + '</div>')
        ANCH[pre + "n:" + k] = (x - r, y - r, 2 * r, 2 * r)
        if g["hf"] and h:
            hc = MUTE if kind in ("ghost", "gone", "far") else INK
            o.append(p(f"position:absolute;left:{x - 90}px;top:{y + r + 4}px;width:180px;font-family:{MONO};font-size:{g['hf']}px;font-weight:700;line-height:1.2;text-align:center;color:{hc}", e(h), f' id="{pre}h-{k}"{ba}'))
    stack = {}
    tf, th = g["tf"], g["th"]
    for name, k, kind in tags:
        col, lane = nodes[k][:2]
        i = stack.get(k, 0)
        stack[k] = i + 1
        x = X(col)
        w = tag_w(name, tf)
        below = g[lane] + r + (round(g["hf"] * 1.2) + 18 if g["hf"] else 10)
        top = (below + i * (th + 8)) if lane == "main" else (g[lane] - r - 16 - th - i * (th + 8))
        tid = pre + "t-" + name.replace("/", "-")
        o.append(p(f"position:absolute;left:{x - w // 2}px;top:{top}px;width:{w}px;height:{th}px;font-family:{MONO};font-size:{tf}px;font-weight:700;line-height:{th - (4 if kind == 'origin' else 0)}px;text-align:center;border-radius:8px;{TAG[kind]}", e(name), f' id="{tid}"{ba}'))
        ANCH[pre + "t:" + name] = (x - w // 2, top, w, th)
        if name == head_tag:
            hw = tag_w("◀ HEAD", tf)
            o.append(p(f"position:absolute;left:{x - w // 2 + w + 10}px;top:{top}px;width:{hw}px;height:{th}px;font-family:{MONO};font-size:{tf}px;font-weight:700;line-height:{th}px;text-align:center;border-radius:8px;background:{INK};color:#F6F5F1", "◀ HEAD", f' id="{pre}t-head"{ba}'))
            ANCH[pre + "t:HEAD"] = (x - w // 2 + w + 10, top, hw, th)
    return o


NOTE_FS = 32


def note(order, text, key, side="r", nudge=(0, 0), nid="note", run=56, size=NOTE_FS, color=INK):
    """One short label beside what changed, tied to it by a leader line drawn on like a pen.
    key: an ANCH key (n:<node>, t:<tag>, t:HEAD, term ...).  side: r, l, u, d, ur (above, reading rightwards)."""
    ax, ay, aw, ah = ANCH[key]
    rows = text.split("<br>")
    nh = round(size * 1.35 * len(rows))
    nw = round(max(sans_w(t, size) for t in rows)) + 12
    gap = 10
    if side == "r":
        x1, y1 = ax + aw + gap, ay + ah / 2
        x2, y2 = x1 + run, y1
        nx, ny = x2 + 14, y1 - nh / 2
    elif side == "l":
        x1, y1 = ax - gap, ay + ah / 2
        x2, y2 = x1 - run, y1
        nx, ny = x2 - 14 - nw, y1 - nh / 2
    elif side == "ur":
        x1, y1 = ax + aw / 2, ay - gap
        x2, y2 = x1, y1 - run
        nx, ny = x1 - 30, y2 - 10 - nh
    elif side == "u":
        x1, y1 = ax + aw / 2, ay - gap
        x2, y2 = x1, y1 - run
        nx, ny = x1 - nw / 2, y2 - 10 - nh
    else:
        x1, y1 = ax + aw / 2, ay + ah + gap
        x2, y2 = x1, y1 + run
        nx, ny = x1 - nw / 2, y2 + 10
    nx, ny = nx + nudge[0], ny + nudge[1]
    nx = max(96, min(1824 - nw, nx))
    ink = SUB
    align = "text-align:right;" if side == "l" else ""
    ANCH[nid] = (nx, ny, nw, nh)
    return [f'<svg data-build-in="draw order {order}" viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible">'
            f'<g fill="none" stroke="{ink}" stroke-width="3" stroke-linecap="round"><path d="M{x1:.0f},{y1:.0f} L{x2:.0f},{y2:.0f}"/></g></svg>',
            f'<svg data-build-in="fade order {order}" viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible">'
            f'<circle cx="{x1:.0f}" cy="{y1:.0f}" r="6" fill="{ink}"/></svg>',
            p(f"position:absolute;left:{nx:.0f}px;top:{ny:.0f}px;width:{nw}px;font-size:{size}px;font-weight:700;line-height:1.35;white-space:nowrap;{align}color:{color}",
              text, f' id="{nid}" data-build-in="fade order {order}"')]


def scene(sid, eyebrow, title, term=None, color=BL, transition="magic", section=None, size=(30, 24)):
    if section:
        SECTIONS[section[0]] = {"description": section[1], "start": sid}
    o = [sec(sid, transition)] + head(eyebrow, title, color)
    if term:
        o += terminal(term, size=size)
    return o


# ---------- the story (hashes from tools/demo.sh) ----------
A, B, C, D, E_ = "9f452aa", "6d19f01", "d51d818", "6a9792d", "3573c9a"
NM, M, D2, E2, S = "d847d12", "8818bb8", "a40dc47", "6852264", "8a6fe21"
PC, PD, PM, PD2 = "c4ea069", "521bc6f", "be1e0e1", "b63da4a"
XC, XD, XE, XF, XM, XS = "5649c8c", "a6ed801", "f1538e4", "1b7e41b", "149b2f0", "f70ca73"   # worked examples
FB = "feature/login-button"
OFB = "origin/feature/login-button"

n_ab = {"A": (0, "main", "main", "n", "A", A), "B": (1, "main", "main", "n", "B", B)}
n_de = dict(n_ab, D=(2, "up", "green", "n", "D", D), E=(3, "up", "green", "n", "E", E_))
e_de = [("A", "B"), ("B", "D"), ("D", "E")]
n_split = dict(n_de, C=(2, "main", "main", "n", "C", C))
e_split = e_de + [("B", "C")]
nohash = lambda nodes: {k: v[:5] + ("",) for k, v in nodes.items()}

# ---------- cover ----------
cov = [sec("cover", "fade", INK).replace(f"color:{INK}", "color:#F6F5F1"),
       p("position:absolute;left:128px;top:300px;width:900px;font-size:28px;font-weight:700;color:#8FB3FF", "KANT AX/AI 엔지니어 트랙 · 08"),
       f'<h1 style="position:absolute;left:128px;top:360px;width:900px;font-size:104px;font-weight:900;line-height:1.12;color:#F6F5F1">합치는 방법,<br>눈으로 비교하기</h1>',
       p("position:absolute;left:128px;top:620px;width:900px;font-size:40px;line-height:1.4;color:#BFC6D4", "fast-forward, merge, rebase, squash")]
CG = dict(x0=1060, step=170, up=420, main=600, r=40, lf=34, hf=0, tf=26, th=42)
n_cov = dict(nohash(n_split), Q=(4, "main", "gray", "ghost", "?", ""))
cov += graph(n_cov, e_split + [("C", "Q"), ("E", "Q")], g=CG, pre="cv")
cov.append(p(f"position:absolute;left:1060px;top:700px;width:680px;font-size:30px;font-weight:700;line-height:1.4;color:#BFC6D4", "갈라진 두 길을 어떻게 이을까요"))
W("cover", cov, "갈라진 두 길을 잇는 방법은 네 가지예요. 03에서 fast-forward와 merge 커밋 두 가지를 봤어요. 오늘은 같은 예시 하나로 rebase와 squash까지 네 가지를 나란히 놓고 결과 그림을 비교해요. git pull이 이 중 무엇을 하는지, GitHub PR의 Merge 버튼 세 개가 각각 무엇인지도 이어서 봐요.", ("intro", "들어가기"))

# toc is written last, after page numbers are known
ORDER.append("toc")

# ---------- why: same work, different history ----------
EB0 = "들어가기"
o = [sec("why")] + head(EB0, "같은 브랜치를 합쳤는데 기록이 달라요", SUB)
LOGM = [("$", "git log --oneline"), ("o", f"{M} (HEAD -> main) Merge branch '{FB}'"), ("o", f"{C} docs: README 추가"),
        ("o", f"{E_} ({FB}) fix: 버튼 글자 고치기"), ("o", f"{D} feat: 로그인 버튼 추가"), ("o", f"{B} feat: 아이디 입력 추가"),
        ("o", f"{A} feat: 로그인 화면 추가"), ("$", "cat login.md"), ("g", "# 로그인"), ("g", "아이디"), ("g", "[로그인] 버튼")]
LOGS = [("$", "git log --oneline"), ("o", f"{S} (HEAD -> main) feat: 로그인 버튼 추가"), ("o", f"{C} docs: README 추가"),
        ("o", f"{B} feat: 아이디 입력 추가"), ("o", f"{A} feat: 로그인 화면 추가"), ("$", "cat login.md"), ("g", "# 로그인"), ("g", "아이디"), ("g", "[로그인] 버튼")]
o.append(p(f"position:absolute;left:96px;top:206px;width:850px;font-size:30px;font-weight:700;color:{C_MG}", "merge로 합친 폴더"))
o += terminal(LOGM, left=96, top=256, size=(28, 24), tid="tm")
lm = list(LINES)
RX = ANCH["tm"][0] + ANCH["tm"][2] + 40
o.append(p(f"position:absolute;left:{RX}px;top:206px;width:{1824 - RX}px;font-size:30px;font-weight:700;color:{C_SQ}", "squash로 합친 폴더"))
LINES.clear()
o += terminal(LOGS, left=RX, top=256, size=(28, 24), tid="ts")
ls_ = list(LINES)
LINES[:] = lm
o.append(pen(1, 1, OR))
o.append(pen(1, 3, OR, 4))
LINES[:] = ls_
o.append(pen(2, 1, OR))
o.append(pen(3, 6, GR, 8))
LINES[:] = lm
o.append(pen(3, 8, GR, 10))
o.append(p(f"position:absolute;left:96px;top:{round(ANCH['tm'][1] + ANCH['tm'][3] + 50)}px;width:1728px;font-size:34px;font-weight:700;line-height:1.4;color:{INK}", "기록은 6줄과 4줄인데, 파일 내용은 똑같아요.", ' data-build-in="fade order 3"'))
W("why", o, "같은 브랜치를 합쳐도 방법에 따라 기록 모양이 달라져요. 두 폴더 모두 같은 출발점에서 feature/login-button을 main에 합쳤어요. 왼쪽은 merge로 합쳐서 합치기 커밋과 브랜치 커밋 D, E가 다 남았어요. 오른쪽은 squash로 합쳐서 커밋 하나만 남았어요. 그런데 login.md 내용은 두 폴더가 똑같아요. 팀 레포나 GitHub에서 이런 다른 모양을 보면 어떻게 합쳤는지 읽을 수 있게 되는 게 오늘 목표예요. 출력은 실제로 실행한 결과예요.")

# ---------- big picture: where merging happens ----------
o = [sec("map")] + head(EB0, "합치기는 세 곳에서 일어나요", SUB)
o.append(f'<div id="z-pc" style="position:absolute;left:96px;top:236px;width:840px;height:640px;background:#EEF3FC;border-radius:28px"></div>')
o.append(p(f"position:absolute;left:136px;top:266px;width:600px;font-size:34px;font-weight:700;color:{NAVY}", "내 컴퓨터"))
o.append(f'<div id="z-gh" style="position:absolute;left:1236px;top:236px;width:588px;height:640px;background:#F1EEFA;border-radius:28px"></div>')
o.append(p(f"position:absolute;left:1276px;top:266px;width:500px;font-size:34px;font-weight:700;color:{PUR}", "GitHub"))
MG = dict(x0=200, step=150, up=470, main=600, r=34, lf=28, hf=0, tf=24, th=38)
o += graph(dict(nohash(n_split), M=(4, "main", "main", "merge", "M", "")), e_split + [("C", "M"), ("E", "M")], g=MG, pre="pc")
# GitHub side: a pull request merge button
o.append(f'<div id="gh-pr" style="position:absolute;left:1276px;top:350px;width:508px;height:250px;background:#FFFFFF;border:2px solid #D0D7DE;border-radius:16px"></div>')
o.append(p(f"position:absolute;left:1304px;top:376px;width:460px;font-size:26px;font-weight:700;color:{INK}", "feat: 로그인 버튼 추가 #1"))
o.append(p(f"position:absolute;left:1304px;top:424px;width:460px;font-size:22px;color:{MUTE}", "kim wants to merge 2 commits into main"))
o.append(f'<div id="gh-mb" style="position:absolute;left:1304px;top:500px;width:340px;height:60px;background:#1F883D;border-radius:10px;display:flex;flex-direction:row;align-items:center">'
         + p("flex:1;font-size:24px;font-weight:700;color:#FFFFFF;text-align:center", "Merge pull request") + '<div style="width:2px;height:60px;background:#17692F"></div>'
         + p("width:56px;font-size:20px;color:#FFFFFF;text-align:center", "▼") + '</div>')
ANCH["gh-mb"] = (1304, 500, 340, 60)
# the pull arrow between the two places
o.append(f'<x-connector id="pull-arrow" x1="1220" y1="760" x2="952" y2="760" head="end" style="color:{PUR};border-width:6px"></x-connector>')
o.append(p(f"position:absolute;left:946px;top:700px;width:280px;font-family:{MONO};font-size:28px;font-weight:700;text-align:center;color:{PUR}", "git pull"))
MARKS = [(1, "pcn:M", "①", "git merge, git rebase<br>git merge --squash", "1~3부", (150, 690)),
         (2, "pull-arrow", "②", "받아 와서<br>합치기", "4부", (960, 796)),
         (3, "gh-mb", "③", "PR의 Merge 버튼", "5부", (1304, 636))]
for i, key, num, text, part, (x, y) in MARKS:
    o.append(f'<div data-build-in="rise order {i}" style="position:absolute;left:{x}px;top:{y}px;display:flex;flex-direction:row;gap:14px;align-items:flex-start">'
             + p(f"width:44px;height:44px;flex:none;border-radius:50%;background:{INK};color:#FFFFFF;font-size:26px;font-weight:700;line-height:44px;text-align:center", str(i))
             + '<div style="display:flex;flex-direction:column;gap:4px">' + p(f"font-size:30px;font-weight:700;line-height:1.35;color:{INK}", text)
             + p(f"font-size:24px;font-weight:700;color:{MUTE}", part) + '</div></div>')
W("map", o, "합치기는 내 컴퓨터, git pull, GitHub PR 버튼 세 곳에서 일어나요. 첫째는 내 컴퓨터에서 git merge나 git rebase를 직접 치는 경우예요. 1부부터 3부까지 이걸 봐요. 둘째는 git pull이에요. 06에서 pull이 받아 와서 합친다고 했죠. 어떻게 합칠지는 설정이 정하고, 4부에서 봐요. 셋째는 GitHub PR 화면의 Merge 버튼이에요. 버튼마다 합치는 방법이 달라요. 5부에서 봐요.")

# ---------- intro: the example ----------
EBX = "들어가기 · 오늘의 예시"
o = scene("story1", EBX, "A, B까지 main에 있어요", [("$", "git log --oneline"), ("o", f"{B} (HEAD -> main) feat: 아이디 입력 추가"), ("o", f"{A} feat: 로그인 화면 추가")], color=SUB, transition="fade")
o += graph(n_ab, [("A", "B")], [("main", "B", "main")], "main")
o += note(1, "점 안 글자는 커밋 이름, 아래는 해시", "n:B", "r")
W("story1", o, "커밋마다 A, B 같은 글자를 붙여서 부르고, 점 아래에 진짜 해시를 적었어요. 오늘은 hello-git 말고 연습용 저장소 merge-lab을 새로 만들어 써요. rebase처럼 기록을 바꾸는 명령도 해 보니까 수업 저장소와 팀 레포는 건드리지 않아요. login.md 하나에 커밋 두 개를 쌓았어요. 그래프는 03처럼 왼쪽이 먼저 한 커밋이에요.")

o = scene("story2", EBX, "브랜치에서 D, E를 커밋해요", [("$", f"git checkout -b {FB}"), ("$", 'git commit -m "feat: 로그인 버튼 추가"'), ("o", f"[{FB} {D}] feat: 로그인 버튼 추가"),
          ("$", 'git commit -m "fix: 버튼 글자 고치기"'), ("o", f"[{FB} {E_}] fix: 버튼 글자 고치기")], color=SUB)
o += graph(n_de, e_de, [("main", "B", "main"), (FB, "E", "green")], FB)
o += note(1, "main은 아직 B에 있어요", "t:main", "r")
W("story2", o, "브랜치에서 커밋 두 개 D, E를 쌓았어요. login.md에 로그인 버튼 줄을 더해 커밋했어요(D). 버튼 글자를 [로그인] 버튼으로 고쳐 한 번 더 커밋했어요(E). 지금 HEAD는 브랜치에 있어요. checkout 출력, git add 줄, 1 file changed 줄도 나오는데, 그 부분은 빼고 옮겼어요.")

# ---------- part 1: not diverged ----------
EB1 = "1. 갈라지지 않았을 때"
o = scene("ff", EB1, "fast-forward: main 이름표만 앞으로 가요", [("$", "git checkout main"), ("$", f"git merge {FB}"), ("o", f"Updating {B}..{E_}"), ("g", "Fast-forward")],
          color=C_FF, section=("plain", "갈라지지 않았을 때"))
o += graph(n_de, e_de, [(FB, "E", "green"), ("main", "E", "main")], "main")
o += note(1, "커밋은 그대로, 이름표만 E로", "t:HEAD", "r")
W("ff", o, "main 쪽에 새 커밋이 없으면 Git은 main 이름표를 E로 옮기기만 해요. 03에서 본 빨리 감기(Fast-forward)예요. B 뒤로 main에는 커밋이 없었어요. 커밋 해시는 하나도 바뀌지 않고, 합치기 커밋도 생기지 않아요. 파일 목록 줄도 나오는데, 그 부분은 빼고 옮겼어요.")

n_noff = dict(n_de, NM=(4, "main", "main", "merge", "M", NM))
o = scene("noff", EB1, "--no-ff: 그래도 합치기 커밋을 만들어요", [("$", f"git merge --no-ff {FB}"), ("o", "Merge made by the 'ort' strategy."), ("$", "git log --oneline"),
          ("o", f"{NM} (HEAD -> main) Merge branch '{FB}'")], color=C_FF)
o += graph(n_noff, e_de + [("B", "NM"), ("E", "NM")], [(FB, "E", "green"), ("main", "NM", "main")], "main")
o += note(1, "부모가 B와 E 둘", "n:NM", "r")
W("noff", o, "--no-ff를 붙이면 fast-forward가 되는 상황에서도 합치기 커밋 M을 만들어요. 앞 장과 같은 상태에서 쳤어요. no fast-forward, 빨리 감기를 하지 말라는 뜻이에요. 나중에 기록을 보면 D, E가 브랜치에서 온 커밋이라는 게 남아요. 메시지 편집기가 열리면 그대로 저장하고 닫아요. GitHub의 Create a merge commit 버튼이 늘 이 방식이에요(5부). log 출력 아래쪽 줄도 나오는데, 그 부분은 빼고 옮겼어요.")

# ---------- part 2: diverged ----------
EB2 = "2. 갈라졌을 때"
o = scene("split", EB2, "main에 C가 생기면 길이 갈라져요", [("$", "git add README.md"), ("$", 'git commit -m "docs: README 추가"'), ("o", f"[main {C}] docs: README 추가")],
          color=SUB, transition="fade", section=("split", "갈라졌을 때"))
o += graph(n_split, e_split, [("main", "C", "main"), (FB, "E", "green")], "main")
o += note(1, "이 모양에서 셋을 비교해요", "t:HEAD", "r")
W("split", o, "main에 C가 생기면 이름표만 옮겨서는 C와 D, E를 같이 담을 수 없어요. 다시 6쪽 상태로 돌아가서, 이번엔 main에서 README.md를 만들어 커밋했어요(C). 내가 브랜치에서 일하는 동안 팀원 작업이 main에 들어온 모습과 같아요. 이 그림이 이 덱의 출발점이에요. 다음 장부터 이 상태에서 merge, rebase, squash를 하나씩 해 봐요.")

n_merge = dict(n_split, M=(4, "main", "main", "merge", "M", M))
o = scene("merge", EB2, "merge: 두 길을 잇는 합치기 커밋이 생겨요", [("$", f"git merge {FB}"), ("o", "Merge made by the 'ort' strategy."), ("$", "git log --oneline"),
          ("o", f"{M} (HEAD -> main) Merge branch '{FB}'")], color=C_MG)
o += graph(n_merge, e_split + [("C", "M"), ("E", "M")], [("main", "M", "main"), (FB, "E", "green")], "main")
o += note(1, "부모가 C와 E 둘", "n:M", "r")
W("merge", o, "merge는 원래 커밋을 건드리지 않고, 둘을 잇는 합치기 커밋 M 하나를 더해요. 03의 갈라진 길 파트와 06의 pull에서 본 합치기 커밋이에요. 흰 점이 합치기 커밋이에요. D, E 해시가 그대로라서 이미 push한 커밋이 있어도 안전해요. log 출력 아래쪽 줄도 나오는데, 그 부분은 빼고 옮겼어요.")

n_rb = dict(n_split, Dx=(2, "up", "gray", "gone", "D", ""), Ex=(3, "up", "gray", "gone", "E", ""),
            D=(3, "main", "green", "n", "D'", D2), E=(4, "main", "green", "n", "E'", E2))
e_rb = [("A", "B"), ("B", "C"), ("C", "D"), ("D", "E"), ("B", "Dx"), ("Dx", "Ex")]
o = scene("rb1", EB2, "rebase: D, E를 C 뒤로 옮겨 붙여요", [("$", f"git checkout {FB}"), ("$", "git rebase main"), ("g", f"Successfully rebased and updated refs/heads/{FB}.")], color=C_RB)
o += graph(n_rb, e_rb, [("main", "C", "main"), (FB, "E", "green")], FB)
o += note(1, "옛 D, E는 점선으로 남아요", "n:Dx", "l")
W("rb1", o, "rebase는 내 브랜치 커밋을 main 끝(C) 뒤로 하나씩 다시 만들어 붙여요. 다시 9쪽 상태에서 시작해요. rebase는 브랜치에서 쳐요. 받침(base)을 바꾼다는 뜻이에요. 같은 내용의 새 커밋 D', E'가 생기고, 옛 D, E는 어느 이름표도 가리키지 않아서 점선으로 그렸어요. 진짜 터미널에서는 Rebasing (1/2) 같은 진행 줄이 잠깐 보였다가 지워져요.")

o = [sec("rb-hash")] + head(EB2, "rebase하면 커밋 해시가 바뀌어요", C_RB)
o.append(p(f"position:absolute;left:96px;top:226px;width:846px;font-size:28px;font-weight:700;color:{SUB}", "rebase 전"))
o += terminal([("$", "git log --oneline"), ("o", f"{E_} (HEAD -> {FB}) fix: 버튼 글자 고치기"), ("o", f"{D} feat: 로그인 버튼 추가"),
               ("o", f"{B} feat: 아이디 입력 추가"), ("o", f"{A} feat: 로그인 화면 추가")], left=96, top=276, size=(26, 22), tid="t1", w=852)
before = list(LINES)
o.append(p(f"position:absolute;left:984px;top:226px;width:840px;font-size:28px;font-weight:700;color:{C_RB}", "rebase 뒤"))
LINES.clear()
o += terminal([("$", "git log --oneline"), ("o", f"{E2} (HEAD -> {FB}) fix: 버튼 글자 고치기"), ("o", f"{D2} feat: 로그인 버튼 추가"),
               ("o", f"{C} (main) docs: README 추가"), ("o", f"{B} feat: 아이디 입력 추가")], left=984, top=276, size=(26, 22), tid="t2", w=840)
after = list(LINES)
hw7 = 7 * 22 * 0.6
for i in (1, 2):   # pen underline under the seven hash letters of D and E, before and after
    x, y, w, h = before[i]
    o.append(underline(1, round(x), round(x + hw7), round(y + h + 2), OR))
    x, y, w, h = after[i]
    o.append(underline(2, round(x), round(x + hw7), round(y + h + 2), OR))
MINI = dict(BIG, up=650, main=790, r=32, lf=26, hf=22, tf=24, th=36)
MINI.pop("solo")
n_bf = {"A": (0, "main", "main", "n", "A", ""), "B": (1, "main", "main", "n", "B", ""), "D": (2, "up", "green", "n", "D", D), "E": (3, "up", "green", "n", "E", E_)}
o += graph(n_bf, [("A", "B"), ("B", "D"), ("D", "E")], g=dict(MINI, x0=180, step=190), pre="L")
n_af = {"A": (0, "main", "main", "n", "A", ""), "B": (1, "main", "main", "n", "B", ""), "C": (2, "main", "main", "n", "C", ""),
        "D": (3, "main", "green", "n", "D'", D2), "E": (4, "main", "green", "n", "E'", E2)}
o += graph(n_af, [("A", "B"), ("B", "C"), ("C", "D"), ("D", "E")], g=dict(MINI, x0=1040, step=170), pre="R")
o += note(3, "부모는 B", "Ln:D", "u", nid="pb", run=36)
o += note(3, "부모는 C", "Rn:D", "u", nid="pc", run=36)
o.append(p(f"position:absolute;left:96px;top:900px;width:1728px;font-size:32px;font-weight:700;line-height:1.4;color:{INK}", "부모가 B에서 C로 바뀌어서 해시가 새로 나와요. 메시지와 내용은 그대로예요.", ' data-build-in="fade order 3"'))
W("rb-hash", o, "부모 커밋이 바뀌면 해시도 바뀌어요. 커밋 해시는 내용, 메시지, 날짜, 부모 커밋으로 정해져요. rebase는 D의 부모를 B에서 C로 바꿔 다시 만들어서 해시가 새로 나와요. D 뒤에 붙은 E도 부모가 바뀌니까 같이 새 커밋이 돼요. 내 컴퓨터에만 있는 커밋이면 문제가 없어요. 이미 push해서 팀원이 옛 D, E를 받아 갔다면 팀원 기록과 어긋나요. 6부에서 이 장면을 다시 봐요.")

n_rb2 = {k: v for k, v in n_rb.items() if k not in ("Dx", "Ex")}
o = scene("rb2", EB2, "main에서 merge하면 fast-forward로 끝나요", [("$", "git checkout main"), ("$", f"git merge {FB}"), ("o", f"Updating {C}..{E2}"), ("g", "Fast-forward")], color=C_RB)
o += graph(n_rb2, [("A", "B"), ("B", "C"), ("C", "D"), ("D", "E")], [(FB, "E", "green"), ("main", "E", "main")], "main")
o += note(1, "합치기 커밋 없이 한 줄", "t:main", "l")
W("rb2", o, "rebase 뒤에는 브랜치가 C 바로 뒤에 붙어 있어서 merge가 fast-forward로 끝나요. 1부의 fast-forward와 같은 모양이에요. rebase는 합치기 전에 브랜치를 최신 main 뒤로 옮기는 일이고, 합치는 건 여전히 merge예요. 옛 D, E는 이제 쓰지 않아서 그림에서 뺐어요. Git Graph(05)에도 보이지 않아요.")

n_sq = dict(n_split, S=(3, "main", "teal", "ghost", "S", ""))
BX = lambda c: BIG["x0"] + c * BIG["step"]
SQT, SQB = BIG["up"] - BIG["r"] - 6, BIG["up"] + BIG["r"] + 4 + 32 + 12
sqbox = f'<div id="sqbox" style="position:absolute;left:{BX(2) - 106}px;top:{SQT}px;width:{BIG["step"] + 212}px;height:{SQB - SQT}px;border:4px dashed {TEAL};border-radius:30px"></div>'
o = scene("sq1", EB2, "squash: D, E의 변경을 모아 대기실에 올려요", [("$", f"git merge --squash {FB}"), ("o", "Automatic merge went well; stopped before committing as requested"), ("o", "Squash commit -- not updating HEAD")], color=C_SQ)
o.append(sqbox)
gq = graph(n_sq, e_split + [("C", "S")], [("main", "C", "main"), (FB, "E", "green")], "main")
o += [x.replace('id="n-S"', 'id="n-S" data-build-in="fly order 1" data-from="sqbox"') for x in gq]
o += note(1, "아직 커밋 전이에요", "n:S", "r")
W("sq1", o, "--squash는 브랜치의 변경을 모두 모아 대기실(02의 ② 칸)에 올리고 멈춰요. 다시 9쪽 상태에서 main에 있어요. 커밋은 직접 해요. 출력 첫 줄은 자동 합치기가 잘 됐고 요청대로 커밋 전에 멈췄다는 뜻이에요. 둘째 줄은 HEAD를 옮기지 않았다는 뜻이에요. git status를 치면 Changes to be committed로 보여요.")

n_sq2 = dict(n_split, S=(3, "main", "teal", "n", "S", S))
o = scene("sq2", EB2, "커밋하면 S 하나가 생겨요", [("$", 'git commit -m "feat: 로그인 버튼 추가"'), ("o", f"[main {S}] feat: 로그인 버튼 추가")], color=C_SQ)
o += graph(n_sq2, e_split + [("C", "S")], [("main", "S", "main"), (FB, "E", "green")], "main")
o += note(1, "부모는 C 하나, D, E와 안 이어져요", "n:S", "r")
W("sq2", o, "커밋 두 개(D, E)의 변경이 커밋 하나(S)로 main에 들어갔어요. 버튼을 만들다 고친 과정은 main 기록에 남지 않고 결과만 남아요. 그래서 작은 커밋이 많은 브랜치를 깔끔하게 합칠 때 써요. 메시지는 브랜치에서 한 일을 한 줄로 적어요. 1 file changed 줄도 나오는데, 그 부분은 빼고 옮겼어요.")

o = scene("sq3", EB2, "squash 뒤에는 브랜치가 -d로 안 지워져요", [("$", f"git branch -d {FB}"), ("r", f"error: the branch '{FB}' is not fully merged."),
          ("o", f"If you are sure you want to delete it, run 'git branch -D {FB}'")], color=C_SQ)
o.append(pen(1, 1))
o += graph(n_sq2, e_split + [("C", "S")], [("main", "S", "main"), (FB, "E", "green")], "main")
o += note(1, "Git은 D, E가 main에 없다고 봐요", "t:" + FB, "r", (0, -10))
W("sq3", o, "S는 D, E와 선으로 이어지지 않아서 Git은 브랜치가 합쳐지지 않았다고 봐요. -d는 합쳐진 브랜치만 지워요. Git은 커밋을 선으로 따라가서 합쳐졌는지 봐요. git log --oneline이나 파일 내용으로 변경이 main에 있는 걸 확인한 뒤 git branch -D feature/login-button으로 지워요. 대문자 -D는 합쳐졌는지 확인하지 않고 지우니, 변경이 main에 있는 걸 본 뒤에만 써요.")

# ---------- part 3: compare ----------
EB3 = "3. 한눈에 비교"
CARDS = [("fast-forward", C_FF, "갈라지지 않았을 때", {"A": (0, "main", "main", "n", "A", ""), "B": (1, "main", "main", "n", "B", ""), "D": (2, "main", "green", "n", "D", ""), "E": (3, "main", "green", "n", "E", "")},
          [("A", "B"), ("B", "D"), ("D", "E")], "새 커밋 없이 이름표만 앞으로"),
         ("merge", C_MG, "--no-ff도 같아요", nohash(n_merge), e_split + [("C", "M"), ("E", "M")], "합치기 커밋 M, D와 E는 그대로"),
         ("rebase", C_RB, "옮겨 붙인 뒤 fast-forward", nohash(n_rb2), [("A", "B"), ("B", "C"), ("C", "D"), ("D", "E")], "한 줄, D'와 E'는 새 해시"),
         ("squash", C_SQ, "변경을 모아 커밋 하나로", dict(nohash(n_sq2), D=(2, "up", "gray", "n", "D", ""), E=(3, "up", "gray", "n", "E", "")),
          e_split + [("C", "S")], "한 줄, main에는 S 하나만")]
o = [sec("cmp", "fade")] + head(EB3, "합치기 커밋과 해시에서 갈려요", SUB)
o.append(f'<div style="position:absolute;left:96px;top:600px;width:1728px;height:2px;background:{LINE}"></div>')
o.append(f'<div style="position:absolute;left:959px;top:236px;width:2px;height:740px;background:{LINE}"></div>')
for i, (name, c, sub, nodes, edges, res) in enumerate(CARDS):
    left, top = 96 + (i % 2) * 896, 236 + (i // 2) * 384
    ba = f' data-build-in="rise order {i + 1}"'
    o.append(p(f"position:absolute;left:{left}px;top:{top}px;width:830px;font-size:38px;font-weight:700;color:{c}", f'{e(name)} <span style="font-size:26px;font-weight:500;color:{MUTE}">{e(sub)}</span>', ba))
    g = dict(x0=left + 50, step=140, up=top + 120, main=top + 230, r=30, lf=26, hf=0, tf=20, th=32)
    o += graph(nodes, edges, (), None, g, f"c{i}", f"rise order {i + 1}")
    o.append(p(f"position:absolute;left:{left}px;top:{top + 292}px;width:830px;font-size:30px;font-weight:700;color:{INK}", e(res), ba))
W("cmp", o, "네 방법은 합치기 커밋이 생기는지, 커밋 해시가 바뀌는지로 갈려요. fast-forward는 C가 생기기 전 모습에서, 나머지 셋은 C가 생긴 뒤 모습에서 출발했어요. 출발점이 같으면 어느 방법으로 합쳐도 파일 내용은 같아요. 다른 건 기록 모양이에요. VS Code Git Graph(05)로 열어 보면 이 그림과 같은 모양으로 보여요.", ("compare", "한눈에 비교"))

rows = [("방법", "명령", "새로 생기는 커밋", "D, E 해시", "main 기록"),
        ("fast-forward", "git merge 브랜치", "없음", "그대로", "한 줄"),
        ("merge", "git merge 브랜치\ngit merge --no-ff 브랜치", "합치기 커밋 M", "그대로", "두 줄이 만나요"),
        ("rebase", "git rebase main\n(브랜치에서)", "D', E'", "바뀌어요", "한 줄"),
        ("squash", "git merge --squash 브랜치\ngit commit -m \"...\"", "S 하나", "main에 없어요", "한 줄, 커밋 하나")]
o = [sec("cmp-table", "fade")] + head(EB3, "표로 보면 해시 칸이 달라요", SUB)
widths = [280, 560, 320, 270, 298]
mcol = {"fast-forward": C_FF, "merge": C_MG, "rebase": C_RB, "squash": C_SQ}
y = 240
for ri, row in enumerate(rows):
    hgt = 64 if ri == 0 else 136
    o.append(f'<div id="row{ri}" style="position:absolute;left:96px;top:{y}px;width:1728px;height:{hgt}px;display:flex;flex-direction:row;align-items:center;padding:0 16px">')
    for ci, cell in enumerate(row):
        if ri == 0:
            st = f"font-size:26px;font-weight:700;color:{MUTE}"
        elif ci == 0:
            st = f"font-size:34px;font-weight:700;color:{mcol[cell]}"
        elif ci == 1:
            st = f"font-family:{MONO};font-size:26px;font-weight:700;line-height:1.5;color:{INK}"
        else:
            hot = cell in ("바뀌어요", "main에 없어요")
            st = f"font-size:30px;font-weight:{700 if hot else 500};color:{RED if hot else INK}"
        o.append(p(f"width:{widths[ci]}px;flex:none;{st}", "<br>".join(e(x) for x in cell.split("\n"))))
    o.append('</div>')
    y += hgt
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:2px;background:{LINE if ri else "#C9C5BA"}"></div>')
    y += 2
o += [spot(1, target="row3", pad=4, r="14"), spot(2, target="row4", pad=4, r="14"), spot_off(3)]
W("cmp-table", o, "D, E 해시 칸을 보면 rebase와 squash만 달라요. merge와 fast-forward는 원래 커밋을 그대로 써요. rebase는 새 커밋을 만들어서 해시가 바뀌어요. squash는 D, E 대신 S를 만들어서 D, E가 main 기록에 들어가지 않아요. 해시가 바뀌거나 사라지는 방법을 이미 push한 커밋에 쓰면 팀원 기록과 어긋나요.")

# ---------- part 4: git pull ----------
EB4 = "4. git pull은 무엇을 하나"
n_pl = {"A": (0, "main", "main", "n", "A", A), "B": (1, "main", "main", "n", "B", B), "C": (2, "main", "purple", "far", "C", PC), "D": (2, "up", "main", "n", "D", PD)}
e_pl = [("A", "B"), ("B", "C"), ("B", "D")]
o = scene("pl0", EB4, "pull도 합치기예요", [("$", "git fetch origin"), ("$", "git log --oneline"), ("o", f"{PD} (HEAD -> main) feat: 로그인 버튼 추가"),
          ("$", "git log --oneline origin/main"), ("o", f"{PC} (origin/main) docs: README 추가")], color=C_PL, section=("pull", "git pull"), transition="fade")
o += graph(n_pl, e_pl, [("origin/main", "C", "origin"), ("main", "D", "main")], "main")
o += note(1, "GitHub에만 있는 lee의 C", "n:C", "r")
W("pl0", o, "git pull은 git fetch로 받아 온 커밋을 내 main과 합쳐요. 이번엔 브랜치 대신 main끼리 갈라졌어요. lee가 README 추가(C)를 먼저 push했고, 나는 main에서 바로 로그인 버튼(D)을 커밋했어요. push는 06에서 본 것처럼 거절돼요. 어떻게 합칠지는 pull 설정이 정해요. 실습 저장소가 달라서 C, D 해시가 2부와 달라요. log 출력 아래쪽 줄도 나오는데, 그 부분은 빼고 옮겼어요.")

o = [sec("pl-none")] + head(EB4, "설정이 없으면 pull이 멈추고 셋 중 고르라고 해요", C_PL)
o += terminal([("$", "git pull origin main"), ("o", "hint: You have divergent branches and need to specify how to reconcile them."),
               ("o", "hint: You can do so by running one of the following commands sometime before"), ("o", "hint: your next pull:"),
               ("o", "hint:   git config pull.rebase false  # merge"), ("o", "hint:   git config pull.rebase true   # rebase"),
               ("o", "hint:   git config pull.ff only       # fast-forward only"), ("r", "fatal: Need to specify how to reconcile divergent branches.")],
              top=220, size=(28, 24))
o.append(pen(1, 7))
LAB = [(4, "merge로 합쳐요 · 수업 설정", C_MG), (5, "rebase로 옮겨 붙여요", C_RB), (6, "fast-forward만 받아요", C_FF)]
for i, t, c in LAB:   # labels in a column right of the terminal, level with each hint line
    x, y, w, h = LINES[i]
    tx = ANCH["term"][0] + ANCH["term"][2] + 40
    o.append(p(f"position:absolute;left:{tx}px;top:{round(y)}px;font-size:26px;font-weight:700;line-height:{round(h)}px;white-space:nowrap;color:{c};border-left:5px solid {c};padding-left:14px",
               e(t), ' data-build-in="rise order 2"'))
o.append(p(f"position:absolute;left:96px;top:{round(ANCH['term'][1] + ANCH['term'][3] + 60)}px;width:1728px;font-size:34px;font-weight:700;line-height:1.4;color:{INK}", "06에서 git config --global pull.rebase false로 첫째 줄을 골랐어요.", ' data-build-in="fade order 3"'))
W("pl-none", o, "힌트 세 줄은 merge, rebase, fast-forward only 중에서 pull 방법을 고르라는 뜻이에요. 06에서 본 그 메시지예요. 그때는 해결만 봤어요. 우리 과정은 06에서 git config --global pull.rebase false로 첫째 줄을 골랐어요. From 줄, 빈 hint 줄, 힌트 아래쪽 줄도 나오는데, 그 부분은 빼고 옮겼어요.")

n_pl_m = dict(n_pl, C=(2, "main", "purple", "n", "C", PC), PM=(3, "main", "main", "merge", "M", PM))
o = scene("pl-false", EB4, "pull.rebase false: 합치기 커밋으로 합쳐요", [("$", "git config --global pull.rebase"), ("o", "false"), ("$", "git pull origin main"), ("o", "Merge made by the 'ort' strategy.")], color=C_MG)
o += graph(n_pl_m, e_pl + [("C", "PM"), ("D", "PM")], [("origin/main", "C", "origin"), ("main", "PM", "main")], "main")
o += note(1, "D 해시 그대로, 06에서 본 모양", "n:PM", "r")
W("pl-false", o, "pull.rebase false면 pull이 2부의 merge와 같은 일을 해요. git config --global pull.rebase처럼 값 없이 치면 지금 설정을 보여 줘요. false가 나오면 수업 설정이 돼 있는 거예요. 합치기 커밋 메시지는 Merge branch 'main' of https://github.com/kim/merge-lab이에요. 이제 git push origin main을 하면 올라가요. From 줄과 파일 목록 줄도 나오는데, 그 부분은 빼고 옮겼어요.")

n_pl_r = {"A": n_pl["A"], "B": n_pl["B"], "C": (2, "main", "purple", "n", "C", PC), "Dx": (2, "up", "gray", "gone", "D", ""), "D": (3, "main", "main", "n", "D'", PD2)}
o = scene("pl-true", EB4, "pull.rebase true: 내 커밋을 C 뒤로 옮겨요", [("#", "# pull.rebase true인 컴퓨터"), ("$", "git pull origin main"), ("g", "Successfully rebased and updated refs/heads/main."),
          ("$", "git log --oneline"), ("o", f"{PD2} (HEAD -> main) feat: 로그인 버튼 추가")], color=C_RB, size=(28, 22))
o += graph(n_pl_r, [("A", "B"), ("B", "C"), ("C", "D"), ("B", "Dx")], [("origin/main", "C", "origin"), ("main", "D", "main")], "main")
o += note(1, "기록은 한 줄, D 해시는 새것", "n:D", "r")
W("pl-true", o, "pull.rebase true면 pull이 2부의 rebase와 같은 일을 해요. 보기만 하는 장이에요. 설정을 바꾸지 않아요. 아직 push하지 않은 D를 옮기는 거라 이 경우엔 문제가 없어요. 대신 충돌이 나면 rebase 충돌로 풀어야 해서 처음 배울 때 헷갈려요(6부). 이 설정을 쓰는 회사도 있으니 이름은 알아 둬요.")

o = scene("pl-ff", EB4, "pull.ff only: 갈라졌으면 받지 않아요", [("#", "# pull.ff only인 컴퓨터"), ("$", "git pull origin main"), ("r", "fatal: Not possible to fast-forward, aborting.")], color=C_FF, size=(28, 24))
o.append(pen(1, 2))
o += graph(n_pl, e_pl, [("origin/main", "C", "origin"), ("main", "D", "main")], "main")
o += note(1, "멈춰서 그림이 그대로예요", "n:C", "r")
W("pl-ff", o, "pull.ff only면 갈라지지 않았을 때만 fast-forward로 받고, 갈라졌으면 멈춰요. 보기만 하는 장이에요. 그래프가 앞 장과 같은 건 실패해서 바뀐 게 없기 때문이에요. 이 설정이 있는 컴퓨터에서 이 메시지가 나오면 git config --global --unset pull.ff로 지우고 수업 설정만 남겨요. From 줄과 힌트 줄(git merge --no-ff 또는 git rebase)도 나오는데, 그 부분은 빼고 옮겼어요.")

o = [sec("pl-why")] + head(EB4, "수업은 pull.rebase false로 통일해요", C_MG)
o += terminal([("$", "git config --global pull.rebase false")], top=200, size=(30, 24))
o += graph(n_pl_m, e_pl + [("C", "PM"), ("D", "PM")], [("main", "PM", "main")], None, g=dict(BIG, up=480, main=680))
o += note(1, "내 커밋 해시가 그대로예요", "n:D", "r", nid="w1")
o += note(2, "합친 자리가 기록에 남아요", "n:PM", "r", nid="w2")
o += note(3, "충돌은 03, 06처럼 고치고 add, commit", "t:main", "r", nid="w3")
W("pl-why", o, "pull.rebase false는 기록을 바꾸지 않아서 처음 배울 때 가장 안전해요. 내가 한 커밋이 사라지거나 해시가 바뀌는 일이 없어요. 합치기 커밋 M이 언제 합쳤는지 보여 줘요. 충돌이 나도 03, 06에서 배운 방법 하나로 풀어요. rebase가 나쁜 방법은 아니에요. push 전 내 커밋에만 쓰는 규칙을 지키면 기록이 깔끔해져요. 06에서 처음 한 번 설정했으면 그대로 둬요.")

# ---------- part 5: GitHub PR buttons ----------
EB5 = "5. GitHub PR의 Merge 버튼"
o = [sec("gh-btn")] + head(EB5, "PR의 Merge 버튼은 세 가지예요", PUR)
WX, WY, WW = 96, 216, 1000
o.append(f'<div id="gh-win" style="position:absolute;left:{WX}px;top:{WY}px;width:{WW}px;height:900px;background:#FFFFFF;border:2px solid #D0D7DE;border-radius:20px;box-shadow:0 18px 40px rgba(29,35,48,.10)"></div>')
o.append(p(f"position:absolute;left:{WX + 40}px;top:{WY + 34}px;width:{WW - 80}px;font-size:34px;font-weight:700;color:{INK}", 'feat: 로그인 버튼 추가 <span style="font-weight:400;color:#59636E">#1</span>'))
o.append(p(f"position:absolute;left:{WX + 40}px;top:{WY + 96}px;height:40px;font-size:22px;font-weight:700;line-height:40px;color:#FFFFFF;background:#1F883D;border-radius:20px;padding:0 18px", "Open"))
o.append(p(f"position:absolute;left:{WX + 150}px;top:{WY + 98}px;width:{WW - 190}px;font-size:22px;line-height:36px;color:#59636E", f"kim wants to merge 2 commits into <b>main</b> from <b>{FB}</b>"))
o.append(f'<div style="position:absolute;left:{WX + 40}px;top:{WY + 150}px;width:{WW - 80}px;height:2px;background:#E5E8EB"></div>')
o.append(p(f"position:absolute;left:{WX + 40}px;top:{WY + 176}px;width:{WW - 80}px;font-size:24px;font-weight:700;color:{INK}", "This branch has no conflicts with the base branch"))
o.append(f'<div id="gh-mb" style="position:absolute;left:{WX + 40}px;top:{WY + 230}px;width:380px;height:64px;background:#1F883D;border-radius:10px;display:flex;flex-direction:row;align-items:center">'
         + p("flex:1;font-size:26px;font-weight:700;color:#FFFFFF;text-align:center", "Merge pull request") + '<div style="width:2px;height:64px;background:#17692F"></div>'
         + '<div id="gh-dd" style="width:62px;height:64px;display:flex;align-items:center;justify-content:center">' + p("font-size:22px;color:#FFFFFF", "▼") + '</div></div>')
OPTS = [("Create a merge commit", "All commits from this branch will be added to the base branch via a merge commit.", "git merge --no-ff", "합치기 커밋을 만들어요", C_MG),
        ("Squash and merge", "The 2 commits from this branch will be combined into one commit in the base branch.", "git merge --squash", "커밋 하나로 합쳐요", C_SQ),
        ("Rebase and merge", "The 2 commits from this branch will be rebased and added to the base branch.", "git rebase", "옮겨 붙여요", C_RB)]
MY = WY + 310
o.append(f'<div id="gh-menu" data-build-in="fade order 1" style="position:absolute;left:{WX + 40}px;top:{MY}px;width:{WW - 120}px;height:{len(OPTS) * 136 + 16}px;background:#FFFFFF;border:2px solid #D0D7DE;border-radius:14px;box-shadow:0 10px 26px rgba(29,35,48,.12)"></div>')
o.append(cursor(1, target="gh-dd"))
for i, (en, desc, cmd, ko, c) in enumerate(OPTS):
    top = MY + 8 + i * 136
    oid = f"opt{i}"
    o.append(f'<div id="{oid}" data-build-in="fade order 1" style="position:absolute;left:{WX + 50}px;top:{top}px;width:{WW - 140}px;height:136px;padding:16px 28px;display:flex;flex-direction:column;gap:8px">'
             + p(f"font-size:28px;font-weight:700;color:{INK}", e(en)) + p("font-size:21px;line-height:1.4;color:#59636E", e(desc)) + '</div>')
    ANCH[oid] = (WX + 50, top, WW - 140, 136)
    o.append(cursor(i + 2, target=oid, click=False))
    lx = WX + WW + 60
    o.append(f'<svg data-build-in="draw order {i + 2}" viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible">'
             f'<g fill="none" stroke="{SUB}" stroke-width="3" stroke-linecap="round"><path d="M{WX + WW - 70},{top + 68} L{lx - 14},{top + 68}"/></g></svg>')
    o.append(f'<div data-build-in="fade order {i + 2}" style="position:absolute;left:{lx}px;top:{top + 14}px;display:flex;flex-direction:column;gap:6px">'
             + p(f"font-family:{MONO};font-size:34px;font-weight:700;line-height:1.3;white-space:nowrap;color:{c}", e(cmd))
             + p(f"font-size:28px;font-weight:700;line-height:1.3;white-space:nowrap;color:{INK}", e(ko)) + '</div>')
o.append(cursor_off(5))
W("gh-btn", o, "PR 화면의 초록 버튼 오른쪽 ▼를 누르면 합치는 방법 세 가지가 나와요. Create a merge commit은 갈라지지 않았어도 늘 합치기 커밋을 만들어서 --no-ff와 같아요. Squash and merge는 2부의 squash, Rebase and merge는 2부의 rebase 뒤 fast-forward와 같아요. 버튼 아래 회색 글은 GitHub이 보여 주는 설명이에요. 저장소 설정에 따라 일부 버튼만 보일 수 있어요.", ("github", "GitHub PR 버튼"))

o = [sec("gh-res", "fade")] + head(EB5, "버튼마다 GitHub의 main 기록이 달라요", PUR)
gres = [("Create a merge commit", C_MG, nohash(n_merge), e_split + [("C", "M"), ("E", "M")], f"Merge pull request #1 from kim/{FB}"),
        ("Squash and merge", C_SQ, {k: v for k, v in nohash(n_split).items() if k not in ("D", "E")} | {"S": (3, "main", "teal", "n", "S", "")}, [("A", "B"), ("B", "C"), ("C", "S")], "feat: 로그인 버튼 추가 (#1)"),
        ("Rebase and merge", C_RB, CARDS[2][3], CARDS[2][4], "D', E' 해시가 새로 생겨요")]
for i, (name, c, nodes, edges, msg) in enumerate(gres):
    left = 96 + i * 592
    ba = f' data-build-in="rise order {i + 1}"'
    if i:
        o.append(f'<div style="position:absolute;left:{left - 22}px;top:250px;width:2px;height:640px;background:{LINE}"></div>')
    o.append(p(f"position:absolute;left:{left}px;top:256px;width:544px;font-size:34px;font-weight:700;color:{c}", e(name), ba))
    g = dict(x0=left + 40, step=114, up=470, main=600, r=30, lf=24, hf=0, tf=20, th=32)
    o += graph(nodes, edges, (), None, g, f"g{i}", f"rise order {i + 1}")
    o.append(p(f"position:absolute;left:{left}px;top:700px;width:530px;font-family:{MONO};font-size:24px;font-weight:700;line-height:1.5;color:{INK};background:#ECEAE4;border-radius:10px;padding:14px 18px", e(msg), ba))
W("gh-res", o, "그림은 GitHub에서 합친 뒤 GitHub 쪽 main 모양이에요. Create a merge commit 메시지는 03에서 본 Merge pull request #1 from kim/feature/login-button이에요. Squash and merge는 PR 제목 뒤에 (#1)을 붙인 커밋 하나가 생겨요. Rebase and merge는 갈라지지 않았어도 GitHub이 커밋을 새로 만들어서 해시가 바뀌어요. 어느 버튼을 쓸지는 팀이 정해요. 한 팀이 버튼을 섞어 쓰면 기록 모양이 PR마다 달라져서 읽기 어려워요.")

# ---------- part 6: conflicts and errors ----------
EB6 = "6. 충돌과 오류"
o = [sec("cf-all")] + head(EB6, "충돌은 어느 방법이든 같은 줄이면 나요", RED)
FG = dict(x0=200, step=200, up=430, main=640, r=36, lf=30, hf=0, tf=24, th=40)
o += graph({"A": (0, "main", "main", "n", "A", ""), "B": (1, "main", "main", "n", "B", ""), "K": (2, "main", "main", "n", "C", ""), "T": (2, "up", "green", "n", "D", "")},
           [("A", "B"), ("B", "K"), ("B", "T")], g=FG, pre="f")
o.append(p(f"position:absolute;left:{FG['x0'] + 2 * FG['step'] - 90}px;top:{FG['up'] - 120}px;font-size:24px;font-weight:700;color:{GR}", "feature/login-title"))
o.append(p(f"position:absolute;left:{FG['x0'] + 2 * FG['step'] - 120}px;top:{FG['up'] + 50}px;font-family:{MONO};font-size:30px;font-weight:700;color:{GR};background:#DDF2E5;border-radius:6px;padding:0 10px", "# 로그인하기"))
o.append(p(f"position:absolute;left:{FG['x0'] + 2 * FG['step'] - 120}px;top:{FG['main'] + 50}px;font-family:{MONO};font-size:30px;font-weight:700;color:{BL};background:#DCE7FB;border-radius:6px;padding:0 10px", "# 로그인 페이지"))
o.append(p(f"position:absolute;left:{FG['x0'] + 2 * FG['step'] - 40}px;top:{FG['main'] - 100}px;font-size:24px;font-weight:700;color:{BL}", "main"))
o += terminal([("#", "# main에서"), ("$", "git merge feature/login-title"), ("r", "CONFLICT (content): Merge conflict in login.md"), ("o", ""),
               ("#", "# feature/login-title에서"), ("$", "git rebase main"), ("r", "CONFLICT (content): Merge conflict in login.md"), ("o", ""),
               ("#", "# main에서"), ("$", "git merge --squash feature/login-title"), ("r", "CONFLICT (content): Merge conflict in login.md")],
              left=820, top=236, size=(28, 24))
for i in (2, 6, 10):
    x, y, w, h = LINES[i]
    o.append(underline(1, round(x), round(x + 8 * 24 * 0.6), round(y + h + 1), RED))
o.append(p(f"position:absolute;left:96px;top:880px;width:1728px;font-size:34px;font-weight:700;line-height:1.4;color:{INK}", "같은 줄을 다르게 고쳤으면 Git은 방법과 상관없이 물어봐요.", ' data-build-in="fade order 1"'))
W("cf-all", o, "합치는 방법은 기록 모양만 바꾸고, 충돌이 나는지는 바꾸지 않아요. B에서 갈라진 뒤 main은 첫 줄을 # 로그인 페이지로, 브랜치는 # 로그인하기로 고쳤어요. 03의 충돌 시나리오와 같은 상황이에요. merge, rebase, squash 모두 같은 줄에서 CONFLICT가 나요. 푸는 법도 같아요. 표시 줄을 지우고 남길 내용으로 고친 뒤 git add 해요. 다른 점은 그다음 명령 하나예요(다음 장). 출력의 Auto-merging 줄과 아래 안내 줄도 나오는데, 그 부분은 빼고 옮겼어요.", ("trouble", "충돌과 오류"))

o = [sec("cf-rb")] + head(EB6, "rebase 중 충돌은 add 뒤 --continue로 이어 가요", RED)
o += terminal([("$", "cat login.md"), ("r", "<<<<<<< HEAD"), ("o", "# 로그인 페이지"), ("r", "======="), ("o", "# 로그인하기"), ("r", ">>>>>>> bf59624 (feat: 로그인 제목 바꾸기)"), ("o", "아이디")],
              left=96, top=236, size=(28, 28))
o.append(pen(1, 1, OR, 2))
x, y, w, h = LINES[2]
ANCH["head-blk"] = (LINES[1][0] - 12, LINES[1][1], max(LINES[1][2], LINES[2][2]) + 24, LINES[2][1] + LINES[2][3] - LINES[1][1])
TR = ANCH["term"][0] + ANCH["term"][2]
o += note(1, "HEAD 쪽이 main 내용", "head-blk", "r", run=TR + 40 - (ANCH["head-blk"][0] + ANCH["head-blk"][2] + 10), nid="n1")
o.append(pen(2, 4, GR, 5))
ANCH["mine-blk"] = (LINES[4][0] - 12, LINES[4][1], max(LINES[4][2], LINES[5][2]) + 24, LINES[5][1] + LINES[5][3] - LINES[4][1])
o += note(2, "아래쪽이 옮기던 내 커밋", "mine-blk", "r", run=TR + 40 - (ANCH["mine-blk"][0] + ANCH["mine-blk"][2] + 10), nid="n2")
STEPS = [("1", "표시 세 줄을 지우고 남길 내용으로 고쳐요", False), ("2", "git add login.md", True), ("3", "git rebase --continue", True)]
sy = 620
for i, (n, t, mono) in enumerate(STEPS):
    top = sy + i * 84
    o.append(f'<div data-build-in="rise order 3" style="position:absolute;left:96px;top:{top}px;width:1100px;height:72px;display:flex;flex-direction:row;align-items:center;gap:24px">'
             + p(f"width:48px;height:48px;flex:none;border-radius:50%;background:{C_RB};color:#FFFFFF;font-size:28px;font-weight:700;line-height:48px;text-align:center", n)
             + p(f"font-size:{34 if mono else 32}px;font-weight:700;color:{INK}" + (f";font-family:{MONO}" if mono else ""), e(t)) + '</div>')
o.append(f'<div data-build-in="rise order 4" style="position:absolute;left:1240px;top:{sy + 84}px;width:584px;display:flex;flex-direction:column;gap:10px;border-left:4px solid {RED};padding-left:28px">'
         + p(f"font-size:28px;font-weight:700;color:{RED}", "헷갈리면 그만두기") + p(f"font-family:{MONO};font-size:34px;font-weight:700;color:{INK}", "git rebase --abort") + '</div>')
W("cf-rb", o, "rebase는 커밋을 하나씩 옮기다 멈춘 상태라서 commit 대신 git rebase --continue로 이어 가요. merge 충돌은 고치고 add 뒤 commit으로 끝냈어요(03). rebase는 main 끝으로 가서 내 커밋을 하나씩 얹기 때문에, 내 브랜치에서 쳤어도 HEAD 쪽이 main 내용이에요. 내 커밋은 아래쪽이에요. --continue 뒤 편집기가 열리면 그대로 저장하고 닫아요. 헷갈리면 git rebase --abort로 rebase 전 모습으로 돌아가요. squash 충돌은 merge처럼 고치고 add, commit 해요.")

n_sh = {"A": n_split["A"], "B": n_split["B"], "C": n_split["C"], "Dx": (2, "up", "purple", "far", "D", D), "Ex": (3, "up", "purple", "far", "E", E_),
        "D": (3, "main", "green", "n", "D'", D2), "E": (4, "main", "green", "n", "E'", E2)}
o = scene("warn", EB6, "push한 브랜치는 rebase하지 않아요", [("$", "git rebase main"), ("$", f"git push origin {FB}"), ("r", f" ! [rejected]        {FB} -> {FB} (non-fast-forward)")],
          color=RED, transition="fade", size=(30, 22))
o.append(pen(1, 2))
o += graph(n_sh, [("A", "B"), ("B", "C"), ("C", "D"), ("D", "E"), ("B", "Dx"), ("Dx", "Ex")], [(OFB, "Ex", "origin"), (FB, "E", "green")], FB)
o += note(1, "GitHub에는 옛 D, E", "n:Dx", "l")
W("warn", o, "rebase는 push 전, 나만 가진 커밋에만 써요. feature/login-button을 이미 push한 뒤에 rebase했어요. 내 컴퓨터에는 D', E', GitHub에는 D, E가 있어서 push가 거절돼요. 힌트는 pull하라고 하지만, pull하면 D, E와 D', E'가 둘 다 기록에 들어가고 합치기 커밋까지 생겨요. 메시지가 같은 커밋이 두 쌍 보여서 기록을 읽기 어려워져요. 강제로 덮어쓰는 방법도 있지만 팀원이 받아 간 커밋과 어긋나서 이 과정에서는 쓰지 않아요. 이 상태가 되면 더 치지 말고 강사에게 물어봐요. main처럼 같이 쓰는 브랜치에서는 rebase하지 않아요. rebase 출력 줄도 나오는데, 그 부분은 빼고 옮겼어요.")

o = [sec("trouble")] + head(EB6, "이 메시지가 나오면 이렇게 해요", RED)
cases = [("fatal: Need to specify how to reconcile divergent branches.", "pull 설정이 없어요", "git config --global pull.rebase false"),
         ("fatal: Not possible to fast-forward, aborting.", "pull.ff only가 설정돼 있어요", "git config --global --unset pull.ff"),
         ("error: the branch '...' is not fully merged.", "squash나 rebase로 합쳤어요. 합친 걸 확인하고", "git branch -D 브랜치"),
         ("error: could not apply ...  (rebase 중 CONFLICT)", "고치고 add 뒤 이어 가요. 그만두려면 --abort", "git rebase --continue"),
         ("! [rejected] ... (non-fast-forward)  rebase 뒤", "push한 브랜치를 rebase했어요. pull하지 말고", "강사에게 물어봐요")]
y = 236
for i, (q, a_, cmd) in enumerate(cases, 1):
    mono = cmd.startswith("git")
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:140px;display:flex;flex-direction:row;align-items:center;gap:32px">'
             + '<div style="flex:1;display:flex;flex-direction:column;gap:8px">' + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{RED}", e(q)) + p(f"font-size:28px;color:{SUB}", e(a_)) + '</div>'
             + p(f"width:640px;flex:none;{'font-family:' + MONO + ';' if mono else ''}font-size:28px;font-weight:700;line-height:1.4;color:{INK}", e(cmd)) + '</div>')
    y += 140
    if i < len(cases):
        o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:2px;background:{LINE}"></div>')
        y += 2
W("trouble", o, "합치다 막히면 대부분 이 다섯 메시지 중 하나예요. 1번은 06에서 본 메시지예요. 2번은 다른 자료를 보고 pull.ff only를 설정한 컴퓨터에서 나요. 설정을 지우고 06처럼 pull.rebase false만 남겨요. 3번은 squash나 Rebase and merge 뒤에 나요. 4번은 rebase 중 충돌이에요. 5번은 push한 브랜치를 rebase한 경우예요. pull로 풀면 같은 커밋이 두 번 들어가니 멈추고 물어봐요.")

# ---------- part 7: worked examples (one pull request from start to finish) ----------
EB7 = "7. 실제 상황 예제"
n_x1 = {"A": (0, "main", "main", "n", "A", A), "B": (1, "main", "main", "n", "B", B), "C": (2, "main", "purple", "n", "C", XC),
        "D": (3, "main", "green", "n", "D'", XD), "E": (4, "main", "green", "n", "E'", XE)}
o = scene("ex1", EB7, "PR을 올리기 전에 main이 앞서 갔어요", [("$", "git checkout main"), ("$", "git pull origin main"), ("o", f"Updating {B}..{XC}"), ("g", "Fast-forward"),
          ("$", f"git checkout {FB}"), ("$", "git rebase main"), ("g", f"Successfully rebased and updated refs/heads/{FB}."),
          ("$", f"git push origin {FB}"), ("o", f" * [new branch]      {FB} -> {FB}")], color=PUR, transition="fade", size=(26, 22), section=("examples", "실제 상황 예제"))
o += graph(n_x1, [("A", "B"), ("B", "C"), ("C", "D"), ("D", "E")], [("main", "C", "main"), (FB, "E", "green"), (OFB, "E", "origin")], FB, g=EX)
o += note(1, "push 전이라 rebase해도 돼요", "n:D", "u", run=40)
W("ex1", o, "아직 push하지 않은 브랜치는 최신 main 뒤로 rebase한 다음 올려요. 브랜치에서 D, E를 만드는 동안 lee가 README 추가(C)를 GitHub main에 올렸어요. main으로 가서 pull로 C를 받고, 브랜치로 돌아와 rebase해요. 그러면 PR에 C 뒤로 이어진 한 줄 기록이 올라가요. 이 브랜치는 이제 push했으니 다음부터는 rebase하지 않아요. 다음 두 장은 이 PR이 합쳐질 때까지 이어지는 이야기예요. checkout 출력, From 줄, 파일 목록 줄, To 줄도 나오는데, 그 부분은 빼고 옮겼어요.")

n_x2 = dict(n_x1, F=(4, "main", "purple", "n", "F", XF), E=(4, "up", "green", "n", "E'", XE), D=(3, "up", "green", "n", "D'", XD),
            M=(5, "up", "green", "merge", "M", XM))
e_x2 = [("A", "B"), ("B", "C"), ("C", "D"), ("D", "E"), ("C", "F"), ("E", "M"), ("F", "M")]
o = scene("ex2", EB7, "PR을 올린 뒤에 main이 또 앞서 갔어요", [("#", f"# {FB}에서"), ("$", "git pull origin main"), ("o", "Merge made by the 'ort' strategy."),
          ("$", f"git push origin {FB}"), ("o", f"   {XE}..{XM}  {FB} -> {FB}")], color=PUR, transition="fade", size=(26, 22))
o += graph(n_x2, e_x2, [("main", "C", "main"), ("origin/main", "F", "origin"), (FB, "M", "green")], FB, g=EX)
o += note(1, "rebase 대신 merge", "n:M", "r", run=40)
W("ex2", o, "이미 push한 브랜치에 최신 main을 받을 때는 rebase 대신 내 브랜치에서 git pull origin main으로 합쳐요. PR을 올리고 리뷰를 기다리는 동안 lee가 비밀번호 안내 커밋(F)을 main에 또 올렸어요. 이번엔 브랜치를 이미 push해서 rebase하면 6부의 거절이 나요. 06에서 본 것처럼 내 브랜치에서 pull하면 pull.rebase false 설정대로 합치기 커밋 M이 생겨요. M은 원래 커밋을 바꾸지 않으니 push가 거절 없이 올라가요. From 줄, 파일 목록 줄, To 줄도 나오는데, 그 부분은 빼고 옮겼어요.")

n_x3 = {"A": n_x1["A"], "B": n_x1["B"], "C": n_x1["C"], "F": (4, "main", "purple", "n", "F", XF), "S": (5, "main", "teal", "n", "S", XS),
        "D": (3, "up", "gray", "gone", "D'", ""), "E": (4, "up", "gray", "gone", "E'", ""), "M": (5, "up", "gray", "gone", "M", "")}
e_x3 = [("A", "B"), ("B", "C"), ("C", "F"), ("F", "S"), ("C", "D"), ("D", "E"), ("E", "M")]
o = scene("ex3", EB7, "팀이 Squash and merge로 PR을 합쳤어요", [("$", "git checkout main"), ("$", "git pull origin main"), ("o", f"Updating {XC}..{XS}"), ("g", "Fast-forward"),
          ("$", f"git branch -d {FB}"), ("r", f"error: the branch '{FB}' is not fully merged."),
          ("$", f"git branch -D {FB}"), ("o", f"Deleted branch {FB} (was {XM}).")], color=PUR, transition="fade", size=(26, 22))
o.append(pen(1, 5))
o += graph(n_x3, e_x3, [("main", "S", "main")], "main", g=EX)
o += note(1, "PR 하나가 S 하나로", "n:S", "u", (-60, 0), run=40)
W("ex3", o, "Squash and merge로 합쳐진 PR은 main으로 가서 pull한 뒤 내 브랜치를 -D로 지워요. GitHub이 D', E', M의 변경을 모아 S 하나로 main에 넣었어요. 03에서 배운 PR 뒤 순서(main으로 가서 pull, 브랜치 지우기) 그대로예요. 다만 S는 내 브랜치 커밋과 이어지지 않아서 -d가 거절해요. PR 화면에 보라색 Merged 표시가 있는지 확인하고 -D로 지워요. 다음 작업은 최신 main에서 새 브랜치를 만들어 시작해요. checkout 출력, From 줄, 파일 목록 줄, -d의 두 번째 줄도 나오는데, 그 부분은 빼고 옮겼어요.")

# ---------- summary ----------
o = [sec("cheatsheet")] + head("정리", "언제 무엇으로 합치나요", INK)
SUMC = [("fast-forward", C_FF, ["git merge 브랜치"], "main에 새 커밋이 없을 때 git merge가 알아서 해요", CARDS[0]),
        ("merge", C_MG, ["git merge 브랜치", "git pull origin main"], "pull할 때, push한 브랜치에 main을 받을 때", CARDS[1]),
        ("rebase", C_RB, ["git rebase main"], "push 전, 내 브랜치를 최신 main 뒤로", CARDS[2]),
        ("squash", C_SQ, ["git merge --squash 브랜치", "Squash and merge"], "작은 커밋 여러 개를 하나로, 뒤에는 -D", CARDS[3])]
for i, (h, c, cmds, when, cd) in enumerate(SUMC):
    left = 96 + i * 440
    if i:
        o.append(f'<div style="position:absolute;left:{left - 22}px;top:236px;width:2px;height:600px;background:{LINE}"></div>')
    o.append(p(f"position:absolute;left:{left}px;top:236px;width:400px;font-size:38px;font-weight:700;color:{c}", h))
    g = dict(x0=left + 30, step=84, up=356, main=440, r=20, lf=17, hf=0, tf=16, th=26)
    o += graph(cd[3], cd[4], (), None, g, f"s{i}")
    o.append(p(f"position:absolute;left:{left}px;top:510px;width:396px;font-family:{MONO};font-size:24px;font-weight:700;line-height:1.6;color:{INK}", "<br>".join(e(x) for x in cmds)))
    o.append(p(f"position:absolute;left:{left}px;top:620px;width:396px;font-size:30px;font-weight:700;line-height:1.45;color:{SUB}", e(when)))
o.append(f'<div style="position:absolute;left:96px;top:870px;width:1728px;height:2px;background:{LINE}"></div>')
o.append(p(f"position:absolute;left:96px;top:900px;width:1728px;font-size:30px;font-weight:700;line-height:1.5;color:{INK}",
           '헷갈리면 merge를 써요. 다음 챕터 <span style="color:#2459C9">09 uv로 파이썬 시작하기</span>에서는 파이썬 프로젝트를 만들어요.'))
W("cheatsheet", o, "수업에서는 merge를 기본으로 쓰고, 나머지는 기록을 읽을 수 있을 만큼 알아 두면 돼요. 출발점이 같으면 어느 방법으로 합쳐도 파일 내용은 같아요. 다른 건 기록 모양과 해시예요. pull은 pull.rebase false로 merge, PR은 팀이 정한 버튼 하나를 써요. rebase는 push 전 내 브랜치에만 써요. 충돌은 어느 방법이든 같은 줄에서 나요.", ("summary", "정리"))

# ---------- toc (page numbers from ORDER) ----------
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
parts = [(C_FF, "갈라지지 않았을 때", "fast-forward, --no-ff", "ff", "noff"),
         (C_MG, "갈라졌을 때", "merge, rebase, squash", "split", "sq3"),
         (SUB, "한눈에 비교", "네 가지 결과 그림과 표", "cmp", "cmp-table"),
         (C_PL, "git pull은 무엇을 하나", "pull 설정 세 가지", "pl0", "pl-why"),
         (PUR, "GitHub PR의 Merge 버튼", "버튼 세 개와 명령", "gh-btn", "gh-res"),
         (RED, "충돌과 오류", "충돌, push한 브랜치, 막힐 때", "cf-all", "trouble"),
         (PUR, "실제 상황 예제", "PR 하나를 올리고 합치기까지", "ex1", "ex3")]
t = [sec("toc"), f'<h2 id="title" style="position:absolute;left:96px;top:92px;width:1728px;font-size:56px;font-weight:700;line-height:1.2;color:{INK}">오늘의 순서</h2>']
y = 210
for i, (c, h, s, a, b) in enumerate(parts, 1):
    pg = f"{page[a]}–{page[b]}쪽"
    t.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:92px;display:flex;flex-direction:row;align-items:center;gap:32px">'
             + p(f"width:60px;flex:none;font-size:44px;font-weight:900;color:{c}", str(i))
             + p(f"width:620px;flex:none;font-size:36px;font-weight:700;color:{INK}", e(h))
             + p(f"flex:1;font-size:30px;color:{SUB}", e(s))
             + p(f"width:160px;flex:none;font-size:28px;color:{MUTE};text-align:right", pg) + '</div>')
    y += 92
    t.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:2px;background:{LINE}"></div>')
    y += 2
t.append(p(f"position:absolute;left:96px;top:{y + 30}px;width:1728px;font-size:28px;color:{SUB}",
           f'{page["why"]}–{page["story2"]}쪽은 왜 배우는지와 오늘의 예시, {page["cheatsheet"]}쪽은 한 장 정리예요.'))
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(t) + f"\n<aside>{e('1부와 2부는 같은 예시로 방법을 하나씩 봐요. 3부에서 결과를 나란히 비교해요. 4부와 5부는 그 방법이 git pull과 GitHub 버튼에서 어떻게 쓰이는지 연결해요. 6부는 충돌과 막힐 때, 7부는 PR 하나를 올리고 합치기까지 실제 순서대로 풀어 봐요.')}</aside>\n</section>\n")

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-10-29T05:00:00Z"}, "lists": "css", "title": "합치는 방법, 눈으로 비교하기", "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
print(len(ORDER), "slides")
