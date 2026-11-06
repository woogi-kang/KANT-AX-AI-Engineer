"""Generates the commit-graph scenes for the Git branch deck.

One idea per scene: a sentence title, the command in a terminal that is only as wide as its lines,
and the commit graph as the hero (nodes, edges, branch name tags, HEAD) drawn large on the slide
itself, with no panel behind it. What changed gets one short label with a leader line (NOTE table),
in place of a caption under the picture. Elements keep the same id across scenes so the magic
transition animates only what the command changed. Design rules: tools/DESIGN.md (Stageshow).
Terminal output was captured from git 2.43 (see README).
Usage: python3 tools/gen_branch.py slides
"""
import html, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from highlight import spot, spot_off, cursor, cursor_off, ring, box, underline, TYPE  # noqa: E402

OUT = sys.argv[1]
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"

LANE = {"up": 640, "main": 820}           # node centre y
X0, STEP = 240, 226                       # node centre x of the first visible column
R = 36                                    # node radius
TAG_FS, TAG_H, TAG_GAP = 30, 44, 10       # branch name tags: font size, height, gap between stacked tags
ANCH = {}                                 # element boxes (x, y, w, h) of the scene being drawn, for NOTE

COL = {  # branch colours: (node/tag fill, light edge)
    "main": ("#2459C9", "#9DB8F2"),
    "green": ("#1F8A4C", "#9ED3B4"),
    "orange": ("#B26A00", "#E4C08A"),
    "gray": ("#7A8394", "#C3C8D2"),
}
TAG_KIND = {
    "main": "background:#2459C9;color:#FFFFFF",
    "green": "background:#1F8A4C;color:#FFFFFF",
    "orange": "background:#B26A00;color:#FFFFFF",
    "origin": "background:#E7DEFC;color:#4A2FA8;border:2px solid #8E6FEA",
}
TERM_COLORS = {"$": "#F2C46D", "o": "#D8DEE9", "g": "#7FD18B", "r": "#F28B82"}


def e(s):
    return html.escape(s, quote=False)


def p(style, text, attrs=""):
    return f'<p{attrs} style="{style}">{text}</p>'


def cx(col, off):
    return X0 + (col - off) * STEP


def tag_w(text):
    return round(len(text) * TAG_FS * 0.6 + 36)


TERM_TOP, TERM_PAD, TERM_GAP = 196, 22, 4
CMD_SIZE, OUT_SIZE = 30, 24


def text_w(t, size):
    """Rough ink width of a terminal line: Latin letters are 0.6 em in JetBrains Mono, Hangul about 1 em."""
    return sum(size if ord(ch) > 0x2E80 else size * 0.6 for ch in t)


def scene(sec_id, eyebrow, title, term=None, caption="", transition="magic", eyebrow_color="#2459C9", hot=None, err=None, static=False, start=0):
    """term: list of (kind, text); kind "$" is a command, others are output colours.
    Clicks: each command is typed in, its output comes in on the next click, then the spot lights up
    what changed (hot: an element id or an (x, y, w, h) box), then the caption.
    err: index of a terminal line to circle in red instead of a spot. static: show the terminal at once."""
    o = [f'<section id="{sec_id}" data-transition="{transition}" style="background:#F6F5F1;color:#1D2330;font-family:{SANS};padding:96px;display:flex;flex-direction:column">']
    o.append(p(f"position:absolute;left:96px;top:48px;width:1728px;font-size:26px;font-weight:700;color:{eyebrow_color}", e(eyebrow), ' id="eyebrow"'))
    o.append(f'<h2 id="title" style="position:absolute;left:96px;top:92px;width:1728px;font-size:56px;font-weight:700;line-height:1.2;color:#1D2330">{title}</h2>')
    n, prev = start, None
    err = ERR.get(sec_id) if err is None else err
    scene.lines = []
    if term:
        tw_ = max(text_w(("$ " if k == "$" else "") + t.replace("\t", "    "), CMD_SIZE if k == "$" else OUT_SIZE) for k, t in term)
        o.append(f'<div id="term" style="position:absolute;left:96px;top:{TERM_TOP}px;width:{min(1728, max(640, round(tw_ + 96)))}px;background:#1B2029;border-radius:20px;padding:{TERM_PAD}px 32px;display:flex;flex-direction:column;gap:{TERM_GAP}px;font-family:{MONO}">')
        y = TERM_TOP + TERM_PAD
        for kind, text in term:
            t = e(text).replace("\t", "&#160;" * 4)
            lead = len(t) - len(t.lstrip(" "))
            t = "&#160;" * lead + t.lstrip(" ")
            size = CMD_SIZE if kind == "$" else OUT_SIZE
            at = ""
            if not static:
                if kind == "$":
                    n += 1
                    at = TYPE(n)
                else:
                    if prev == "$" or n == 0:
                        n += 1
                    at = f' data-build-in="fade order {n}"'
            prev = kind
            raw = ("$ " if kind == "$" else "") + text.replace("\t", "    ")
            scene.lines.append((128, y, text_w(raw, size), size * 1.35))
            y += size * 1.35 + TERM_GAP
            if kind == "$":
                o.append(p(f"font-size:{size}px;font-weight:700;line-height:1.35;white-space:nowrap;color:{TERM_COLORS['$']}", "$ " + t, at))
            else:
                o.append(p(f"font-size:{size}px;line-height:1.35;white-space:nowrap;color:{TERM_COLORS[kind]}", t, at))
        o.append('</div>')
    if err is not None:
        n += 1
        x, y, w, h = scene.lines[err]
        o.append(box(n, round(x - 10), round(y - 2), round(w + 20), round(h + 4), "#A33131"))
    scene.next = n + 1
    ANCH.clear()
    scene.last = n
    return o


def graph(nodes, edges, tags, head=None, off=0, ghost_edges=()):
    """nodes: {hash: (col, lane, colour, kind)}  kind: n | merge | ghost (not made yet) | far (only on GitHub)
    edges: [(from_hash, to_hash)]   tags: [(name, hash, kind)] stacked in list order per node
    head: name of the tag HEAD points at
    With no commit on the upper row the graph sits in the middle of the free space; when a branch gets
    its own commit the main row moves down to make room (the magic transition carries it)."""
    o = []
    two = any(v[1] == "up" for v in nodes.values())
    LANE.update({"up": 600, "main": 780} if two else {"up": 520, "main": 680})
    if off:
        y = LANE["main"]
        o.append(f'<div id="e-past" style="position:absolute;left:112px;top:{y - 3}px;width:{X0 - R - 128}px;height:6px;border-top:6px dotted #C3C8D2"></div>')
    for a, b in edges:
        ca, la, colour_a, _ = nodes[a]
        cb, lb, colour_b, kb = nodes[b]
        x1, y1, x2, y2 = cx(ca, off), LANE[la], cx(cb, off), LANE[lb]
        light = COL[colour_a if (lb == "main" and la != "main") else colour_b][1]
        dashed = (a, b) in ghost_edges or kb in ("ghost", "far", "gone")
        if y1 == y2:
            st = f"border-top:6px dashed {light}" if dashed else f"background:{light}"
            o.append(f'<div id="e-{a}-{b}" style="position:absolute;left:{x1 + R}px;top:{y1 - 3}px;width:{x2 - x1 - 2 * R}px;height:6px;{st}"></div>')
        else:
            dash = ";border-style:dashed" if dashed else ""
            o.append(f'<x-connector id="e-{a}-{b}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" style="color:{light};border-width:6px{dash}"></x-connector>')
    for h, (col, lane, colour, kind) in nodes.items():
        x, y = cx(col, off), LANE[lane]
        fill = COL[colour][0]
        st = {"merge": f"background:#FFFFFF;border:9px solid {fill}",
              "ghost": f"background:#FDFCF9;border:5px dashed {fill}",
              "far": f"background:#FDFCF9;border:5px dashed {fill}",
              "gone": "background:#FDFCF9;border:5px dashed #C3C8D2"}.get(kind, f"background:{fill};border:4px solid {fill}")
        o.append(f'<div id="n-{h}" style="position:absolute;left:{x - R}px;top:{y - R}px;width:{2 * R}px;height:{2 * R}px;border-radius:50%;{st}"></div>')
        label = "?" if kind == "ghost" else h
        hc = "#6A7180" if kind in ("ghost", "far", "gone") else "#1D2330"
        o.append(p(f"position:absolute;left:{x - 80}px;top:{y + R + 4}px;width:160px;font-family:{MONO};font-size:28px;font-weight:700;line-height:1.2;text-align:center;color:{hc}", e(label), f' id="h-{h}"'))
        ANCH["n:" + h] = (x - R, y - R, 2 * R, 2 * R)
    stack = {}
    for name, h, kind, *pos in tags:
        col, lane, _, _ = nodes[h]
        if pos:                               # explicit (row, dx) when three tags share one commit
            i, dx = pos
        else:
            i, dx = stack.get(h, 0), 0
            stack[h] = i + 1
        x = cx(col, off) + dx
        w = tag_w(name)
        top = (LANE[lane] + R + 48 + i * (TAG_H + TAG_GAP)) if lane == "main" else (LANE[lane] - R - 16 - TAG_H - i * (TAG_H + TAG_GAP))
        tid = "t-" + name.replace("/", "-")
        o.append(p(f"position:absolute;left:{x - w // 2}px;top:{top}px;width:{w}px;height:{TAG_H}px;font-family:{MONO};font-size:{TAG_FS}px;font-weight:700;line-height:{TAG_H}px;text-align:center;border-radius:8px;{TAG_KIND[kind]}", e(name), f' id="{tid}"'))
        ANCH["t:" + name] = (x - w // 2, top, w, TAG_H)
        if name == head:
            hw = tag_w("◀ HEAD")
            o.append(p(f"position:absolute;left:{x - w // 2 + w + 10}px;top:{top}px;width:{hw}px;height:{TAG_H}px;font-family:{MONO};font-size:{TAG_FS}px;font-weight:700;line-height:{TAG_H}px;text-align:center;border-radius:8px;background:#1D2330;color:#F6F5F1", "◀ HEAD", ' id="t-head"'))
            ANCH["t:HEAD"] = (x - w // 2 + w + 10, top, hw, TAG_H)
    return o


def card(title, lines, top=TERM_TOP):
    """The file as it is now, in the right column beside the terminal. lines: [(text, colour_key)]  g = changed line."""
    c = {"o": "#1D2330", "g": "#1A7340", "b": "#1E3F8F", "x": "#9AA0AB"}
    bg = {"g": "#DDF2E5", "b": "#DCE7FB"}
    o = [f'<div id="card" style="position:absolute;left:1364px;top:{top}px;width:460px;background:#FFFFFF;border:2px solid #E1DED6;border-radius:18px;padding:24px 28px;display:flex;flex-direction:column;gap:10px">']
    o.append(p("font-size:26px;font-weight:700;color:#4A5262", e(title)))
    for text, k in lines:
        extra = f";background:{bg[k]};border-radius:6px;padding:0 10px;margin:0 -10px" if k in bg else ""
        deco = ";text-decoration:line-through" if k == "x" else ""
        o.append(p(f"font-family:{MONO};font-size:30px;line-height:1.4;white-space:nowrap;color:{c[k]}{extra}{deco}", e(text)))
    ANCH["card"] = (1364, top, 460, 24 * 2 + 36 + len(lines) * 52)
    o.append('</div>')
    return o


ZONES = [("③ 내 저장소", "#F0F5FE", "#9DB8F2", "#1E3F8F"), ("② 대기실", "#F1FAF4", "#9ED3B4", "#1A7340"),
         ("① 작업 폴더", "#FFFFFF", "#D5D9E0", "#3A4150")]
ZT, ZH = TERM_TOP, 136                    # zones column: top, height of one zone
CHIP = {0: "background:#DCE7FB;color:#1E3F8F", 1: "background:#DDF2E5;color:#1A7340", 2: "background:#FBE4E2;color:#A33131"}


def zones(where=None, text=""):
    """Three zones at the right of the graph panel. where: 0 repo, 1 staging, 2 working dir, None = the change is gone."""
    o = []
    for i, (name, bg, bd, fg) in enumerate(ZONES):
        top = ZT + i * (ZH + 14)
        o.append(f'<div id="z{i}" style="position:absolute;left:1364px;top:{top}px;width:460px;height:{ZH}px;background:{bg};border:2px solid {bd};border-radius:16px"></div>')
        o.append(p(f"position:absolute;left:1388px;top:{top + 14}px;width:412px;font-size:26px;font-weight:700;line-height:1.3;color:{fg}", e(name), f' id="zl{i}"'))
    ANCH["zones"] = (1364, ZT, 460, 3 * ZH + 28)
    if where is not None:
        top = ZT + where * (ZH + 14) + 62
        o.append(p(f"position:absolute;left:1388px;top:{top}px;width:412px;font-family:{MONO};font-size:28px;font-weight:700;line-height:1.6;padding:0 14px;border-radius:8px;{CHIP[where]}", e(text), ' id="z-chip"'))
    return o


NOTE_FS = 32


def note(sec_id):
    """One short label beside what changed, tied to it by a leader line that is drawn on like a pen,
    after the command. NOTE[sec_id] = (text, anchor key in ANCH, side r/l/u/d)."""
    if sec_id not in NOTE:
        return []
    text, key, side = NOTE[sec_id][:3]
    k = scene.next
    ax, ay, aw, ah = ANCH[key]
    lines = text.count("<br>") + 1
    nh = round(NOTE_FS * 1.35 * lines)
    nw = round(max(text_w(t, NOTE_FS) for t in text.split("<br>"))) + 8
    gap, run = 10, 56
    if side == "r" and ax + aw + gap + run + 14 + nw > 1824:
        side = "ur"                           # no room on the right: above, reading rightwards from the leader
    if side == "r":
        x1, y1 = ax + aw + gap, ay + ah / 2
        x2, y2 = x1 + run, y1
        nx, ny = x2 + 14, y1 - nh / 2
    elif side == "l":
        x1, y1 = ax - gap, ay + ah / 2
        x2, y2 = x1 - run, y1
        nx, ny = x2 - 14 - nw, y1 - nh / 2
    elif side == "ur":                        # left edge just left of the leader, so it clears the column to the left
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
    if len(NOTE[sec_id]) > 3:                 # optional nudge of the label (dx, dy) to clear a neighbour
        nx, ny = nx + NOTE[sec_id][3][0], ny + NOTE[sec_id][3][1]
    nx = max(96, min(1824 - nw, nx))
    ink = "#4A5262"
    return [f'<svg data-build-in="draw order {k}" viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible">'
            f'<g fill="none" stroke="{ink}" stroke-width="3" stroke-linecap="round"><path d="M{x1:.0f},{y1:.0f} L{x2:.0f},{y2:.0f}"/></g>'
            f'</svg>',
            f'<svg data-build-in="fade order {k}" viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible">'
            f'<circle cx="{x1:.0f}" cy="{y1:.0f}" r="6" fill="{ink}"/></svg>',
            p(f"position:absolute;left:{nx:.0f}px;top:{ny:.0f}px;width:{nw}px;font-size:{NOTE_FS}px;font-weight:700;line-height:1.35;white-space:nowrap;color:#1D2330",
              text, f' id="note" data-build-in="fade order {k}"')]


def write(sec_id, parts, notes):
    parts = parts + note(sec_id)
    with open(os.path.join(OUT, f"{sec_id}.html"), "w") as f:
        f.write("\n".join(parts) + f"\n<aside>{e(notes)}</aside>\n</section>\n")


# The label for what changed: (text, anchor, side[, (dx, dy)]). Anchors: n:<hash>, t:<branch name>, t:HEAD, card, zones.
_A, _C, _D, _E, _F, _G, _M, _X = "9e6cce4", "d6b044a", "eb05b65", "4e60a09", "29bd96c", "f0e6c3e", "486cb9c", "42209fe"
_RZ, _P, _Q = "a4c0a4f", "4776218", "0e04baf"
NOTE = {"g1-dots": ("오른쪽 점이 가장 최근 커밋", "n:" + _C, "r"),
        "g2-main": ("main 이름표는 마지막 커밋에 붙어요", "t:main", "r"),
        "g3-head": ("HEAD가 붙은 이름표가 지금 브랜치", "t:HEAD", "r"),
        "b1-list": ("그래프에선 HEAD가 붙은 이름표", "t:HEAD", "r"),
        "b2-create": ("커밋은 그대로, 이름표만 하나 더", "t:feature/login", "r"),
        "b3-move": ("HEAD만 옆 이름표로 왔어요", "t:HEAD", "r"),
        "b4-commit": ("main은 제자리", "t:main", "r"),
        "b5-commit2": ("브랜치에서 여러 번 커밋해도 돼요", "n:" + _E, "r"),
        "b6-back": ("HEAD만 main으로 돌아왔어요", "t:HEAD", "r"),
        "b7-ff": ("main 이름표가 당겨졌어요", "t:HEAD", "r"),
        "b8-delete": ("이름표만 떼요. 커밋은 그대로", "n:" + _E, "r"),
        "d1-create": ("만들고 바로 옮겨 왔어요", "t:HEAD", "d"),
        "d2-commit": ("docs/login-guide만 한 칸 앞으로", "t:docs/login-guide", "u"),
        "d3-back": ("이번엔 main에서도 커밋해요", "t:main", "l"),
        "d4-main": ("양쪽에 커밋이 하나씩", "n:" + _G, "r"),
        "d5-merge": ("부모가 둘인 merge 커밋", "n:" + _M, "ur"),
        "r1-oops": ("이 커밋을 없던 일로 해 볼게요", "n:" + _X, "u", (-60, -24)),
        "r2-soft": ("oops 줄은 대기실에 남아요", "zones", "d"),
        "r3-mixed": ("oops 줄은 작업 폴더에 남아요", "zones", "d"),
        "r4-hard": ("oops 줄이 어디에도 없어요", "zones", "d"),
        "u1-oops": ("merge로 들어온 줄은 내 저장소에", "zones", "d"),
        "u2-soft": ("합쳐 온 변경이 대기실에 남아요", "zones", "d"),
        "u3-mixed": ("합쳐 온 변경이 작업 폴더에 남아요", "zones", "d"),
        "u4-hard": ("세 칸 모두 merge 전 모습", "zones", "d"),
        "u5-again": ("브랜치가 있어서 다시 합쳤어요", "n:" + _M, "ur"),
        "d6-delete": ("커밋은 main 기록 안에 남아요", "n:" + _F, "r"),
        "c1-korean": ("첫 줄을 # 로그인하기로", "card", "d"),
        "c2-main": ("같은 줄을 # 로그인 페이지로", "card", "d"),
        "c3-conflict": ("Git이 고르지 못하고 멈췄어요", "n:" + _RZ, "ur"),
        "c4-resolve": ("두 길을 잇는 merge 커밋", "n:" + _RZ, "ur"),
        "p0-branch": ("아직 내 컴퓨터에만 있어요", "n:" + _P, "r"),
        "p1-push": ("GitHub에도 생긴 브랜치", "t:origin/feature/login-button", "r"),
        "p2-merged": ("아직 GitHub에만 있는 커밋", "n:" + _Q, "ur"),
        "p3-fetch": ("origin/main만 앞으로", "n:" + _Q, "ur"),
        "p3-log": ("main보다 앞서 있으면 pull할 차례", "n:" + _Q, "ur"),
        "p3-pull": ("main이 origin/main과 같은 곳에", "n:" + _Q, "ur"),
        "p4-delete": ("내 컴퓨터의 이름표만 지웠어요", "n:" + _P, "r"),
        "p5-next": ("최신 main에서 새로 따요", "t:HEAD", "r")}
ERR = {"c3-conflict": 1}

# ---------- the story (hashes from a real run, see README) ----------
A, B, C, D, E_, F, G, M = "9e6cce4", "5ec913c", "d6b044a", "eb05b65", "4e60a09", "29bd96c", "f0e6c3e", "486cb9c"
K, L, RZ, P, Q = "4ad88f3", "84f4952", "a4c0a4f", "4776218", "0e04baf"
FB, DU, FK, FE = "feature/login", "docs/login-guide", "feature/login-title", "feature/login-button"

base = {A: (0, "main", "main", "n"), B: (1, "main", "main", "n"), C: (2, "main", "main", "n")}
base_e = [(A, B), (B, C)]

# ---------- 1. 그래프 읽기 ----------
EB1 = "브랜치란? · 그래프 읽기"
LOG1 = [("$", "git log --oneline"), ("o", f"{C} (HEAD -> main, origin/main) docs: README 추가"),
          ("o", f"{B} feat: 인사말 추가"), ("o", f"{A} feat: 인사 파일 추가")]
o = scene("g1-dots", EB1, "점 하나가 커밋 하나예요", LOG1,
          "왼쪽이 먼저 한 커밋, 오른쪽이 최근 커밋이에요.")
o += graph(base, base_e, [])
write("g1-dots", o, "02에서 만든 hello-git 저장소를 이어서 써요. git log는 최근 커밋이 위에 나오고, 그래프는 오래된 커밋이 왼쪽이에요. 점 아래 글자는 커밋 해시 앞 7자리예요. 괄호 안 origin/main은 GitHub에 올라간 위치예요. GitHub 파트에서 다시 봐요.")

def log_mark(a, b):
    """Pen underline under characters a..b of the first log line, so the word lines up with the graph."""
    x, y, _, h = scene.lines[1]
    return underline(1, round(x + a * OUT_SIZE * 0.6), round(x + b * OUT_SIZE * 0.6), round(y + h), "#B26A00")


o = scene("g2-main", EB1, "main은 마지막 커밋에 붙은 이름표예요", LOG1, "새 커밋을 하면 이름표가 새 커밋으로 옮겨 가요.", static=True, start=1)
o.append(log_mark(17, 21))
o += graph(base, base_e, [("main", C, "main")])
write("g2-main", o, "브랜치는 커밋을 담는 상자가 아니라 커밋 하나를 가리키는 이름표예요. 그래서 브랜치를 만들어도 무겁지 않아요. git log 출력의 (HEAD -> main)에서 main이 이 이름표예요.")

o = scene("g3-head", EB1, "HEAD는 지금 내가 있는 곳이에요", LOG1, "커밋하면 HEAD가 붙은 이름표가 앞으로 가요.", static=True, start=1)
o.append(log_mark(9, 13))
o += graph(base, base_e, [("main", C, "main")], head="main")
write("g3-head", o, "HEAD는 지금 내가 서 있는 브랜치를 가리켜요. git log의 HEAD -> main은 지금 main에 있다는 뜻이에요. 이 덱의 모든 장면은 이름표와 HEAD가 어디로 가는지만 보면 돼요.")

# ---------- 2. 만들고 옮기기 ----------
EB2 = "만들고 옮기기"
o = scene("b1-list", EB2, "* 표시가 지금 있는 브랜치예요", [("$", "git branch"), ("g", "* main")], "* 표시가 지금 있는 브랜치예요. 그래프의 HEAD와 같은 뜻이에요.")
o += graph(base, base_e, [("main", C, "main")], head="main")
write("b1-list", o, "git branch는 목록만 보여 줘요. 아직 main 하나뿐이에요.")

o = scene("b2-create", EB2, "브랜치 만들기: 이름표가 하나 더 생겨요", [("$", f"git branch {FB}")], "커밋은 복사되지 않아요. HEAD는 아직 main에 있어요.")
o += graph(base, base_e, [("main", C, "main"), (FB, C, "green")], head="main")
write("b2-create", o, "git branch 이름은 출력 없이 이름표만 만들어요. 같은 커밋에 이름표가 두 개 붙었어요. 만들기만 했지 옮겨 가지는 않았어요.")

o = scene("b3-move", EB2, "브랜치로 옮겨 가기: HEAD가 움직여요", [("$", f"git checkout {FB}"), ("o", f"Switched to branch '{FB}'")],
          f"이제부터 하는 커밋은 {FB}에 쌓여요.")
o += graph(base, base_e, [("main", C, "main"), (FB, C, "green")], head=FB)
write("b3-move", o, "checkout은 HEAD를 옮겨요. 커밋도 이름표도 그대로고 HEAD만 옆 이름표로 갔어요.")

n4 = dict(base); n4[D] = (3, "up", "green", "n")
e4 = base_e + [(C, D)]
o = scene("b4-commit", EB2, f"커밋하면 {FB}만 앞으로 가요", [("$", "git add login.md"), ("$", 'git commit -m "feat: 로그인 화면 추가"'),
          ("o", f"[{FB} {D}] feat: 로그인 화면 추가")], "main은 제자리예요.")
o += graph(n4, e4, [("main", C, "main"), (FB, D, "green")], head=FB)
write("b4-commit", o, "로그인 화면 파일 login.md(# 로그인, 아이디)를 만들고 커밋했어요. 출력 대괄호 안에 지금 브랜치 이름이 나와요. 새 커밋을 위로 그린 건 보기 쉽게 하려는 것이에요. 출력의 1 file changed 줄은 뺐어요.")

n5 = dict(n4); n5[E_] = (4, "up", "green", "n")
e5 = e4 + [(D, E_)]
o = scene("b5-commit2", EB2, "한 번 더 커밋하면 한 칸 더", [("$", "git add login.md"), ("$", 'git commit -m "feat: 비밀번호 입력 추가"'),
          ("o", f"[{FB} {E_}] feat: 비밀번호 입력 추가")], "기능이 끝날 때까지 브랜치에서 여러 번 커밋해도 돼요.")
o += graph(n5, e5, [("main", C, "main"), (FB, E_, "green")], head=FB)
write("b5-commit2", o, "login.md에 비밀번호 줄을 더하고 커밋했어요. main은 계속 처음 모습이라 언제든 돌아갈 수 있어요.")

o = scene("b6-back", EB2, "main으로 돌아와도 feature/login 커밋은 남아요", [("$", "git checkout main"), ("o", "Switched to branch 'main'")], "HEAD만 main으로 돌아왔어요.")
o += graph(n5, e5, [("main", C, "main"), (FB, E_, "green")], head="main")
write("b6-back", o, "HEAD가 main으로 옮겨 갔어요. 다음 장에서 작업 폴더 파일도 같이 바뀌는 걸 봐요.")

# ---------- 3. 합치기 ----------
EB3 = "합치기"
o = scene("b7-ff", EB3, "Fast-forward: main 이름표만 앞으로", [("$", f"git merge {FB}"), ("o", f"Updating {C}..{E_}"), ("g", "Fast-forward")],
          "main 쪽에 새 커밋이 없으면 이름표만 당겨요.")
o += graph(n5, e5, [(FB, E_, "green"), ("main", E_, "main")], head="main")
write("b7-ff", o, "main이 갈라진 뒤 main에는 커밋이 없었어요. 그래서 Git은 main 이름표를 feature/login 자리로 옮기기만 해요. 빨리 감기(Fast-forward)라고 해요. 출력의 파일 목록 줄은 뺐어요.")

n8 = dict(base); n8[D] = (3, "main", "main", "n"); n8[E_] = (4, "main", "main", "n")
e8 = base_e + [(C, D), (D, E_)]
o = scene("b8-delete", EB3, "합친 브랜치는 -d로 지워요", [("$", f"git branch -d {FB}"), ("o", f"Deleted branch {FB} (was {E_}).")],
          "이름표만 떼요. 커밋은 main에 한 줄로 남아요.")
o += graph(n8, e8, [("main", E_, "main")], head="main")
write("b8-delete", o, "-d는 이미 합친 브랜치만 지워요. 합치지 않은 브랜치는 경고를 내고 멈춰요(막힐 때 파트). 위로 그렸던 커밋은 이제 main의 한 줄이에요.")

# ---------- 4. 갈라진 길 ----------
EB4 = "갈라진 길 합치기"
n9 = dict(n8); n9[F] = (5, "up", "orange", "n")
e9 = e8 + [(E_, F)]
o = scene("d1-create", EB4, f"새 브랜치 {DU} 만들고 옮겨 가기", [("$", f"git checkout -b {DU}"), ("o", f"Switched to a new branch '{DU}'")],
          "-b는 만들기와 옮기기를 한 번에 해요.")
o += graph(n8, e8, [("main", E_, "main"), (DU, E_, "orange")], head=DU)
write("d1-create", o, "git checkout -b docs/login-guide는 git branch docs/login-guide와 git checkout docs/login-guide를 한 번에 친 것과 같아요. 문서 작업이라 이름을 docs/로 시작했어요.")

o = scene("d2-commit", EB4, f"{DU}에서 커밋해요", [("$", "git add README.md"), ("$", 'git commit -m "docs: README에 로그인 안내 추가"'),
          ("o", f"[{DU} {F}] docs: README에 로그인 안내 추가")], f"{DU}만 한 칸 앞으로 가요.")
o += graph(n9, e9, [("main", E_, "main"), (DU, F, "orange")], head=DU)
write("d2-commit", o, "README.md에 로그인 방법은 login.md를 봐요라는 안내를 넣고 커밋했어요.")

o = scene("d3-back", EB4, "다시 main으로 돌아와요", [("$", "git checkout main"), ("o", "Switched to branch 'main'")], "이번엔 main에서도 커밋해 볼게요.")
o += graph(n9, e9, [("main", E_, "main"), (DU, F, "orange")], head="main")
write("d3-back", o, "팀에서는 내가 브랜치에서 일하는 동안 다른 사람 작업이 main에 들어오는 일이 흔해요. 그 상황을 혼자 만들어 봐요.")

n10 = dict(n9); n10[G] = (5, "main", "main", "n")
e10 = e9 + [(E_, G)]
o = scene("d4-main", EB4, "main에도 새 커밋: 길이 두 갈래가 됐어요", [("$", "git add hello.md"), ("$", 'git commit -m "feat: 반가움 인사 추가"'),
          ("o", f"[main {G}] feat: 반가움 인사 추가")], "이번엔 이름표만 당겨서는 합칠 수 없어요.")
o += graph(n10, e10, [("main", G, "main"), (DU, F, "orange")], head="main")
write("d4-main", o, "hello.md에 nice to meet you 한 줄을 더했어요. main과 docs/login-guide 양쪽에 서로 모르는 커밋이 하나씩 있어요.")

n11 = dict(n10); n11[M] = (6, "main", "main", "merge")
e11 = e10 + [(G, M), (F, M)]
o = scene("d5-merge", EB4, "merge 커밋이 두 길을 이어요", [("$", f"git merge {DU}"), ("o", "Merge made by the 'ort' strategy.")],
          "흰 점이 새로 생긴 merge 커밋이에요. 메시지 편집기가 열리면 그대로 저장하고 닫아요.")
o += graph(n11, e11, [("main", M, "main"), (DU, F, "orange")], head="main")
write("d5-merge", o, "양쪽에 새 커밋이 있으니 Git이 둘을 합친 커밋을 새로 만들어요. 부모가 둘인 커밋이에요. 편집기에 Merge branch 'docs/login-guide'가 미리 적혀 있어요. vim이 열리면 Esc를 누른 뒤 :wq 와 Enter를 쳐요. 출력의 파일 목록 줄은 뺐어요.")

# ---------- 5. merge 되돌리기 ----------
EBR = "되돌리기 · 케이스 1 일반 커밋"
EBU = "되돌리기 · 케이스 2 merge 커밋"
UC = "#8A5200"
CHG = "README.md · 로그인 안내"
nu = {k: v for k, v in n11.items() if k not in (A, B, C)}
nu_gone = dict(nu); nu_gone[M] = (6, "main", "main", "gone")
eu = [(D, E_), (E_, F), (E_, G), (G, M), (F, M)]

# 케이스 1: merge 뒤 main에 실수 커밋 하나 (hashes from a real run)
X = "42209fe"
OOPS = "hello.md · oops 줄"
nx = dict(nu); nx[X] = (7, "main", "main", "n")
nx_gone = dict(nu); nx_gone[X] = (7, "main", "main", "gone")
ex = eu + [(M, X)]
o = scene("r1-oops", EBR, "실수로 커밋했어요, 아직 push 전이에요", [("$", "git add hello.md"), ("$", 'git commit -m "feat: 실수한 커밋"'), ("o", f"[main {X}] feat: 실수한 커밋")],
          "이 커밋 하나를 없던 일로 해 볼게요.", eyebrow_color=UC)
o += graph(nx, ex, [("main", X, "main"), (DU, F, "orange")], head="main", off=3)
o += zones(0, OOPS)
write("r1-oops", o, f"merge 직후 main에서 hello.md에 oops 한 줄을 넣고 커밋했어요. 아직 push 전이라 {X}는 내 저장소에만 있어요. 오른쪽 세 칸은 02에서 본 작업 폴더, 대기실, 내 저장소예요. 다음 세 장은 모두 이 상태에서 옵션만 바꿔 실행한 결과예요. 따라 할 땐 한 옵션을 해 본 뒤 다시 커밋하고 다음 옵션을 해요. 출력의 1 file changed 줄은 뺐어요.")

o = scene("r2-soft", EBR, "--soft: 변경이 대기실에 남아요", [("$", "git reset --soft HEAD~1"), ("$", "git status"), ("g", "Changes to be committed:"), ("g", "\tmodified:   hello.md")],
          "main이 한 칸 뒤로 가고, oops 줄은 add된 채로 남아요.", eyebrow_color=UC)
o += graph(nx_gone, ex, [("main", M, "main"), (DU, F, "orange")], head="main", off=3)
o += zones(1, OOPS)
write("r2-soft", o, f"HEAD~1은 지금보다 한 칸 아래 커밋이에요. main 이름표가 {X}에서 {M}로 돌아가요. 커밋 메시지만 고쳐서 다시 커밋하고 싶을 때 써요. git status 출력의 On branch main 줄과 괄호 안내 줄은 뺐어요.")

o = scene("r3-mixed", EBR, "--mixed (기본값): 변경이 작업 폴더에 남아요", [("$", "git reset HEAD~1"), ("o", "Unstaged changes after reset:"), ("r", "M\thello.md")],
          "옵션을 안 쓰면 --mixed예요. oops 줄은 파일에 그대로 있어요.", eyebrow_color=UC)
o += graph(nx_gone, ex, [("main", M, "main"), (DU, F, "orange")], head="main", off=3)
o += zones(2, OOPS)
write("r3-mixed", o, "02 되돌리기 파트에서 쓴 git reset HEAD~1과 같은 명령이에요. 대기실은 비우고 고친 내용은 파일에 남겨요. 파일을 더 고친 뒤 add부터 다시 하고 싶을 때 써요.")

o = scene("r4-hard", EBR, "--hard: 변경까지 지워요", [("$", "git reset --hard HEAD~1"), ("o", f"HEAD is now at {M} Merge branch '{DU}'"), ("$", "git status"), ("g", "nothing to commit, working tree clean")],
          "oops 줄이 파일에서도 사라졌어요. 이 변경은 다른 곳에 남아 있지 않아요.", eyebrow_color="#A33131")
o += graph(nx_gone, ex, [("main", M, "main"), (DU, F, "orange")], head="main", off=3)
o += zones(None)
write("r4-hard", o, f"세 칸 모두 {X} 전 모습으로 돌아갔어요. 일반 커밋은 이 변경을 가진 브랜치가 따로 없어서 --hard로 지우면 파일에서 되찾기 어려워요. 02에서 본 git reflog로 해시를 찾는 방법만 남아요. 작업 폴더에 커밋하지 않은 다른 변경이 있었다면 그것도 같이 사라져요. 그래서 --hard 앞에는 git status를 봐요. git status 출력의 On branch main 줄은 뺐어요.")

o = scene("u1-oops", EBU, "이번엔 merge 커밋을 되돌려요", [("$", "git log --oneline"), ("o", f"{M} (HEAD -> main) Merge branch '{DU}'"),
          ("o", f"{G} feat: 반가움 인사 추가"), ("o", f"{F} ({DU}) docs: README에 로그인 안내 추가")],
          "merge 커밋도 같은 명령으로 한 칸 뒤로 가요.", eyebrow_color=UC)
o += graph(nu, eu, [("main", M, "main"), (DU, F, "orange")], head="main", off=3)
o += zones(0, CHG)
write("u1-oops", o, f"케이스 1을 --hard로 끝내서 다시 merge 직후 모습이에요. 아직 push하지 않았으니 merge 커밋 {M}은 내 저장소에만 있어요. 오른쪽 세 칸은 02에서 본 작업 폴더, 대기실, 내 저장소예요. merge로 들어온 README.md의 로그인 안내 줄이 지금 어느 칸에 있는지 봐요. 다음 세 장은 모두 이 상태에서 옵션만 바꿔 실행한 결과예요. log 출력 아래쪽 줄은 뺐어요.")

o = scene("u2-soft", EBU, "--soft: 변경이 대기실에 남아요", [("$", "git reset --soft HEAD~1"), ("$", "git status"), ("g", "Changes to be committed:"), ("g", "\tmodified:   README.md")],
          "main은 merge 전 커밋으로 돌아가고, 합쳐 온 변경은 대기실에 있어요.", eyebrow_color=UC)
o += graph(nu_gone, eu, [("main", G, "main"), (DU, F, "orange")], head="main", off=3)
o += zones(1, CHG)
write("u2-soft", o, f"HEAD~1은 지금보다 한 칸 아래 커밋이에요. merge 커밋의 첫 번째 부모인 {G}로 main이 돌아가요. 점선 {M}은 이제 어느 이름표도 가리키지 않아요. 변경은 이미 add된 상태라 바로 커밋할 수 있어요. git status 출력의 On branch main 줄과 괄호 안내 줄은 뺐어요.")

o = scene("u3-mixed", EBU, "--mixed (기본값): 변경이 작업 폴더에 남아요", [("$", "git reset HEAD~1"), ("o", "Unstaged changes after reset:"), ("r", "M\tREADME.md")],
          "옵션을 안 쓰면 --mixed예요. 고친 내용은 파일에 그대로 있어요.", eyebrow_color=UC)
o += graph(nu_gone, eu, [("main", G, "main"), (DU, F, "orange")], head="main", off=3)
o += zones(2, CHG)
write("u3-mixed", o, "02 되돌리기 파트에서 쓴 git reset HEAD~1과 같은 명령이에요. main은 똑같이 한 칸 돌아가고, 대기실은 비워요. README.md는 Modified 상태로 작업 폴더에 남아요. 다시 담으려면 git add부터 해요.")

o = scene("u4-hard", EBU, "--hard: 변경까지 지워요", [("$", "git reset --hard HEAD~1"), ("o", f"HEAD is now at {G} feat: 반가움 인사 추가"), ("$", "git status"), ("g", "nothing to commit, working tree clean")],
          "--hard는 커밋하지 않은 변경까지 지워요. 쓰기 전에 git status가 깨끗한지 봐요.", eyebrow_color="#A33131")
o += graph(nu_gone, eu, [("main", G, "main"), (DU, F, "orange")], head="main", off=3)
o += zones(None)
write("u4-hard", o, f"세 칸 모두 merge 전 모습이에요. 작업 폴더에 커밋하지 않은 다른 변경이 있었다면 그것도 같이 사라지고 되찾을 수 없어요. 그래서 --hard 앞에는 꼭 git status를 봐요. 로그인 안내 커밋 {F}는 {DU} 이름표가 아직 가리키고 있어서 잃어버리지 않았어요. git status 출력의 On branch main 줄은 뺐어요.")

nu_back = dict(nu)
o = scene("u5-again", EBU, "브랜치가 남아 있으면 다시 합칠 수 있어요", [("$", f"git merge {DU}"), ("o", "Merge made by the 'ort' strategy.")],
          f"{DU}를 지우기 전이라 merge를 몇 번이든 다시 할 수 있어요.", eyebrow_color=UC)
o += graph(nu_back, eu, [("main", M, "main"), (DU, F, "orange")], head="main", off=3)
o += zones(0, CHG)
write("u5-again", o, f"merge를 다시 하면 merge 커밋이 새로 만들어져요. 그래서 보통은 해시가 처음과 달라요. 이 덱은 날짜를 고정해서 같은 {M}이 나왔어요. 출력의 파일 목록 줄은 뺐어요.")

o = scene("d6-delete", "되돌리기 · 정리", f"확인이 끝나면 {DU} 지우기", [("$", f"git branch -d {DU}"), ("o", f"Deleted branch {DU} (was {F}).")],
          "이름표만 사라지고 커밋은 main 기록 안에 남아요.", eyebrow_color=UC)
o += graph(n11, e11, [("main", M, "main")], head="main")
write("d6-delete", o, f"되돌릴 일이 없는지 확인한 뒤에 지워요. 합친 브랜치는 지워서 목록을 깔끔하게 둬요. 커밋 {F}는 merge 커밋을 통해 main 기록에 그대로 있어요.")

# ---------- 5. 충돌 ----------
EB5 = "충돌 시나리오 1 · 같은 줄"
RED = "#A33131"
n12 = {E_: (4, "main", "main", "n"), F: (5, "up", "gray", "n"), G: (5, "main", "main", "n"),
       M: (6, "main", "main", "merge")}
e12 = [(E_, F), (E_, G), (G, M), (F, M)]
n13 = dict(n12); n13[K] = (7, "up", "green", "n")
e13 = e12 + [(M, K)]
o = scene("c1-korean", EB5, f"{FK}에서 제목을 바꿔요", [("$", f"git checkout -b {FK}"), ("$", "git add login.md"), ("$", 'git commit -m "feat: 로그인 제목 바꾸기"'),
          ("o", f"[{FK} {K}] feat: 로그인 제목 바꾸기")], "login.md 첫 줄을 # 로그인하기로 바꿨어요.", eyebrow_color=RED)
o += graph(n13, e13, [("main", M, "main"), (FK, K, "green")], head=FK, off=4)
o += card(f"{FK}의 login.md", [("# 로그인하기", "g"), ("아이디", "o"), ("비밀번호", "o")])
write("c1-korean", o, "login.md 첫 줄을 고친 뒤 add, commit 했어요. 그래프 왼쪽 점선은 앞의 커밋들이 이어진다는 뜻이에요. checkout 출력은 뺐어요.")

n14 = dict(n13); n14[L] = (7, "main", "main", "n")
e14 = e13 + [(M, L)]
o = scene("c2-main", EB5, "main에서는 같은 줄을 다르게", [("$", "git checkout main"), ("$", "git add login.md"), ("$", 'git commit -m "feat: 로그인 제목 다듬기"'),
          ("o", f"[main {L}] feat: 로그인 제목 다듬기")], "같은 줄을 양쪽에서 다르게 고쳤어요.", eyebrow_color=RED)
o += graph(n14, e14, [("main", L, "main"), (FK, K, "green")], head="main", off=4)
o += card("main의 login.md", [("# 로그인 페이지", "b"), ("아이디", "o"), ("비밀번호", "o")])
write("c2-main", o, "main에서는 첫 줄을 # 로그인 페이지로 바꿨어요. 두 사람이 같은 파일의 같은 줄을 고친 상황이에요.")

n15 = dict(n14); n15[RZ] = (8, "main", "main", "ghost")
e15 = e14 + [(L, RZ), (K, RZ)]
o = scene("c3-conflict", EB5, "합치려니 멈췄어요: 충돌", [("$", f"git merge {FK}"), ("r", "CONFLICT (content): Merge conflict in login.md"),
          ("o", "Automatic merge failed; fix conflicts and then commit the result.")],
          "Git이 두 제목 중 무엇을 남길지 몰라서 나에게 물어보는 거예요.", eyebrow_color=RED)
o += graph(n15, e15, [("main", L, "main"), (FK, K, "green")], head="main", off=4, ghost_edges=[(L, RZ), (K, RZ)])
write("c3-conflict", o, "충돌은 고장이 아니에요. Git이 고를 수 없는 부분만 표시해 두고 멈춘 상태예요. 다른 줄은 알아서 합쳐졌어요. 첫 줄 Auto-merging login.md는 뺐어요. 그만두고 싶으면 git merge --abort로 합치기 전으로 돌아가요.")

n16 = dict(n14); n16[RZ] = (8, "main", "main", "merge")
o = scene("c4-resolve", EB5, "고치고 add, commit하면 끝", [("$", "git add login.md"), ("$", 'git commit -m "fix: 로그인 제목 충돌 해결"'),
          ("o", f"[main {RZ}] fix: 로그인 제목 충돌 해결")], "이 커밋이 두 길을 잇는 merge 커밋이에요.", eyebrow_color=RED)
o += graph(n16, e15, [("main", RZ, "main"), (FK, K, "green")], head="main", off=4)
o += card("고친 login.md", [("# 로그인하기", "g"), ("아이디", "o"), ("비밀번호", "o")])
write("c4-resolve", o, "충돌 표시 세 줄을 지우고 # 로그인하기만 남긴 뒤 저장했어요. add는 이 파일 충돌을 풀었다는 표시예요. 다 쓴 feature/login-title은 git branch -d feature/login-title로 지워요.")

# ---------- 6. GitHub에서 함께 ----------
EB6 = "GitHub에서 함께"
PUR = "#6B47D6"
n17 = {F: (5, "up", "gray", "n"), G: (5, "main", "main", "n"), M: (6, "main", "main", "merge"), K: (7, "up", "gray", "n"),
       L: (7, "main", "main", "n"), RZ: (8, "main", "main", "merge"), P: (9, "up", "orange", "n")}
e17 = [(G, M), (F, M), (M, K), (M, L), (L, RZ), (K, RZ), (RZ, P)]
o = scene("p0-branch", EB6, "새 브랜치에서 로그인 버튼을 만들어요", [("$", f"git checkout -b {FE}"), ("$", "git add login.md"), ("$", 'git commit -m "feat: 로그인 버튼 추가"'),
          ("o", f"[{FE} {P}] feat: 로그인 버튼 추가")], "아직 내 컴퓨터에만 있는 커밋이에요.", eyebrow_color=PUR)
o += graph(n17, e17, [("main", RZ, "main"), ("origin/main", RZ, "origin"), (FE, P, "orange")], head=FE, off=5)
write("p0-branch", o, f"충돌을 푼 main을 git push origin main으로 올려 둔 상태예요. 그래서 origin/main이 main과 같은 곳에 있어요. login.md에 로그인 버튼 줄을 더하고 커밋했어요. checkout 출력과 1 file changed 줄은 뺐어요.")

o = scene("p1-push", EB6, "브랜치째 GitHub에 올려요", [("$", f"git push origin {FE}"), ("g", f" * [new branch]      {FE} -> {FE}")],
          "push할 때 main 대신 브랜치 이름을 끝까지 적어요.", eyebrow_color=PUR)
o += graph(n17, e17, [("main", RZ, "main"), ("origin/main", RZ, "origin"), (FE, P, "orange"), ("origin/feature/login-button", P, "origin")], head=FE, off=5)
write("p1-push", o, f"보라색 origin/ 이름표는 GitHub에 있는 브랜치 위치예요. 우리 과정 규칙대로 -u는 쓰지 않아요. 출력 앞부분(Enumerating objects..., remote: Create a pull request...)은 뺐어요.")

n18 = dict(n17); n18[Q] = (10, "main", "main", "far")
e18 = e17 + [(RZ, Q), (P, Q)]
o = scene("p2-merged", EB6, "GitHub에서 Merge하면 GitHub에만 커밋이 생겨요", None,
          "점선 커밋은 아직 GitHub에만 있어요. 내 컴퓨터는 몰라요.", eyebrow_color=PUR, start=1)
o.append(f'<div id="gh" style="position:absolute;left:96px;top:196px;width:1728px;height:200px;background:#FFFFFF;border:2px solid #D0D7DE;border-radius:20px;padding:28px 40px;display:flex;flex-direction:row;align-items:center;gap:40px">'
         f'<div style="flex:1;display:flex;flex-direction:column;gap:16px">' + p("font-size:36px;font-weight:700;color:#1D2330", 'feat: 로그인 버튼 추가 <span style="color:#6A7180">#1</span>')
         + f'<div style="display:flex;flex-direction:row;gap:12px;align-items:center">' + p(f"font-family:{MONO};font-size:26px;color:#1D2330;background:#DCE7FB;padding:2px 12px;border-radius:8px", "main")
         + p("font-size:28px;color:#6A7180", "←") + p(f"font-family:{MONO};font-size:26px;color:#1D2330;background:#FBEBD3;padding:2px 12px;border-radius:8px", e(FE)) + '</div></div>'
         + p("font-size:30px;font-weight:700;color:#FFFFFF;background:#1F8A4C;padding:16px 32px;border-radius:12px", "Merge pull request", ' id="gh-merge"') + '</div>')
o += [cursor(1, target="gh-merge"), cursor_off(2)]
o += graph(n18, e18, [("main", RZ, "main"), ("origin/main", RZ, "origin"), (FE, P, "orange"), ("origin/feature/login-button", P, "origin")], head=FE, off=5)
write("p2-merged", o, f"Merge pull request를 누르면 GitHub 안에서 merge 커밋({Q})이 생겨요. 메시지는 Merge pull request #1 from kim/{FE}예요. 내 컴퓨터로 가져오려면 pull해야 해요.")

o = scene("p3-fetch", EB6, "main으로 가서 fetch로 받아만 와요", [("$", "git checkout main"), ("o", "Switched to branch 'main'"), ("$", "git fetch origin"),
          ("o", f"   {RZ}..{Q}  main       -> origin/main")], "origin/main만 앞으로 갔어요. 내 main은 아직 그대로예요.", eyebrow_color=PUR)
o += graph(n18, e18, [("main", RZ, "main"), ("origin/main", Q, "origin"), (FE, P, "orange"), ("origin/feature/login-button", P, "origin")], head="main", off=5)
write("p3-fetch", o, f"PR이 합쳐졌으면 먼저 합친 쪽 브랜치인 main으로 옮겨 가요. fetch는 GitHub의 새 커밋을 받아서 origin/main 이름표만 옮기고, 내 main과 작업 폴더는 건드리지 않아요. 점선 {Q}는 받아 왔지만 아직 내 main에 합치지 않은 커밋이에요. 출력의 From 줄은 뺐어요.")

o = scene("p3-log", EB6, "GitHub 쪽 기록을 먼저 확인해요", [("$", "git log --oneline origin/main"), ("o", f"{Q} (origin/main) Merge pull request #1 from kim/{FE}"),
          ("o", f"{P} (origin/{FE}, {FE}) feat: 로그인 버튼 추가"), ("o", f"{RZ} (HEAD -> main) fix: 로그인 제목 충돌 해결")],
          "origin/main이 main보다 위에 있으면 pull할 차례예요.", eyebrow_color=PUR)
o += graph(n18, e18, [("main", RZ, "main"), ("origin/main", Q, "origin"), (FE, P, "orange"), ("origin/feature/login-button", P, "origin")], head="main", off=5)
write("p3-log", o, "02에서 배운 비교 방법 그대로예요. git log --oneline origin/main은 GitHub 쪽 main 기록을 보여 줘요. 내 main(HEAD -> main)이 아래에 있으니 받아 올 커밋이 있다는 뜻이에요. 출력 아래쪽 줄은 뺐어요.")

n19 = dict(n18); n19[Q] = (10, "main", "main", "merge")
o = scene("p3-pull", EB6, "pull로 내 main을 맞춰요", [("$", "git pull origin main"), ("o", f"Updating {RZ}..{Q}"), ("g", "Fast-forward")],
          "main이 origin/main과 같은 곳에 섰어요.", eyebrow_color=PUR)
o += graph(n19, e18, [("main", Q, "main"), ("origin/main", Q, "origin"), (FE, P, "orange"), ("origin/feature/login-button", P, "origin")], head="main", off=5)
write("p3-pull", o, f"내 main에는 새 커밋이 없었으니 pull이 Fast-forward로 받아요. 작업 폴더의 login.md에도 로그인 버튼 줄이 생겨요. 출력의 From, FETCH_HEAD 줄과 파일 목록 줄은 뺐어요.")

o = scene("p4-delete", EB6, f"합쳐진 {FE}는 지워요", [("$", f"git branch -d {FE}"), ("o", f"Deleted branch {FE} (was {P}).")],
          "커밋은 main 기록 안에 남아요.", eyebrow_color=PUR)
o += graph(n19, e18, [("main", Q, "main"), ("origin/main", Q, "origin"), ("origin/feature/login-button", P, "origin")], head="main", off=5)
write("p4-delete", o, f"main에 합쳐졌으니 -d로 지워져요. 보라색 origin/{FE} 이름표는 내 컴퓨터가 기억하는 GitHub 쪽 위치라서 남아 있어요. GitHub에서 Delete branch를 누른 뒤 git fetch origin --prune 하면 정리돼요.")

FL = "feature/login-error"
o = scene("p5-next", EB6, "다음 일은 최신 main에서 새 브랜치로", [("$", f"git checkout -b {FL}"), ("o", f"Switched to a new branch '{FL}'")],
          "합치고, main으로 가서 받고, 새로 따요. 브랜치마다 이 순서를 반복해요.", eyebrow_color=PUR)
o += graph(n19, e18, [(FL, Q, "green", 0, 0), ("main", Q, "main", 1, -150), ("origin/main", Q, "origin", 1, 70), ("origin/feature/login-button", P, "origin")], head=FL, off=5)
write("p5-next", o, f"새 브랜치를 pull 하기 전의 main에서 따면 방금 합친 로그인 버튼 커밋이 없는 채로 시작해요. 그러면 나중에 충돌이 날 가능성이 커져요. 그래서 PR이 합쳐질 때마다 git checkout main, git fetch origin, git pull origin main 순서로 맞춘 뒤 다음 브랜치를 만들어요. 이 흐름이 그다음 장의 GitHub Flow예요.")

print("ok")
