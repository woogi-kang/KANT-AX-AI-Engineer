"""Generates every slide of the Git Graph deck.

The Git Graph screen is redrawn from the extension's own source (mhutchie/vscode-git-graph):
labels with a branch icon, the checked-out branch in bold with a coloured border, a hollow dot on
the HEAD commit, "Uncommitted Changes (n)" as a grey hollow dot, 8-character hashes, default lane
colours #0085D9 and #D9008F. Terminal output and hashes come from tools/demo.sh (git 2.43).

Layout follows the Stageshow skill (github.com/benjitaylor/skills): one hero per slide (the Git Graph
window, bled off the bottom), the terminal as a satellite straddling the window's right edge, words on
the drawing with leader lines instead of side cards, the result said once in the title.

Rings and leader lines that point at labels use boxes measured by tools/measure.js (tools/rects.json):
    python3 tools/gen.py slides && node tools/measure.js slides && python3 tools/gen.py slides
"""
import html, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "tools"))
from highlight import *  # noqa: E402,F403

OUT = sys.argv[1]
try:
    RECTS = json.load(open(os.path.join(HERE, "rects.json")))
except (OSError, ValueError):
    RECTS = {}


def rect(slide, eid, default=(0, 0, 10, 10)):
    return tuple(RECTS.get(slide, {}).get(eid, default))


SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
BG, INK, SUB, MUTE, HAIR = "#F6F5F1", "#1D2330", "#4A5262", "#6A7180", "#D9D5CB"
BL, GR, OR, RED, PUR = "#2459C9", "#1F8A4C", "#B26A00", "#A33131", "#5A3BB8"
VS = dict(bg="#1F1F1F", bar="#181818", txt="#CCCCCC", dim="#9D9D9D", bd="#3C3C3C", sel="#2A2D2E", input="#313131", blue="#0078D4")
LANE_C = ["#0085D9", "#D9008F"]
GRAY = "#808080"
SHADOW = "0 24px 60px rgba(20,24,34,.22), 0 2px 6px rgba(20,24,34,.12)"


def e(s):
    return html.escape(s, quote=False)


def p(style, text, attrs=""):
    return f'<p{attrs} style="{style}">{text}</p>'


def bi(kind, order):
    return f' data-build-in="{kind} order {order}"'


def W(name, parts, notes):
    body = "\n".join(parts) + f"\n<aside>{e(notes)}</aside>\n</section>\n"
    open(os.path.join(OUT, name + ".html"), "w").write(body)


def sec(i, transition="fade", bg=BG):
    return f'<section id="{i}" data-transition="{transition}" style="background:{bg};color:{INK};font-family:{SANS};padding:96px;display:flex;flex-direction:column;word-break:keep-all">'


def head(eyebrow, title, color=BL, size=52):
    return [p(f"position:absolute;left:96px;top:44px;width:1728px;font-size:26px;font-weight:700;color:{color}", e(eyebrow), ' id="eyebrow"'),
            f'<h2 id="title" style="position:absolute;left:96px;top:84px;width:1728px;font-size:{size}px;font-weight:700;line-height:1.25;color:{INK}">{title}</h2>']


def label(x, y, w, text, order=None, size=30, color=INK, weight=700, align="left", lid=None, extra=""):
    """Plain words on the slide, no box. A label explains the thing its leader line points at."""
    a = (bi("fade", order) if order else "") + (f' id="{lid}"' if lid else "") + extra
    return p(f"position:absolute;left:{x}px;top:{y}px;width:{w}px;font-size:{size}px;font-weight:{weight};line-height:1.4;text-align:{align};color:{color}", text, a)


def leader(order, pts, color=SUB, width=2.5):
    """A fine line with one bend at most, ending in a small dot 6px short of what it explains."""
    d = "M" + " L".join(f"{x},{y}" for x, y in pts)
    x2, y2 = pts[-1]
    return (f'<svg{bi("draw", order) if order else ""} viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible">'
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round"/>'
            f'<circle cx="{x2}" cy="{y2}" r="6" fill="{color}" stroke="{color}" stroke-width="1"/></svg>')


# ---------- terminal (a satellite: hugs its lines, title bar like a real window) ----------
TC = {"$": "#F2C46D", "o": "#D8DEE9", "#": "#8C95A6", "g": "#7FD18B", "r": "#F28B82"}
T_BAR = 40


def term_h(n, size=24, lh=1.3, pad=20):
    return T_BAR + 2 * pad + round(n * size * lh)


def terminal(lines, left, top, w, size=24, lh=1.3, tid="term", attrs="", pad=20):
    h = term_h(len(lines), size, lh, pad)
    o = [f'<div id="{tid}"{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:#1B2029;border:2px solid #343B48;border-radius:16px;overflow:hidden;box-shadow:{SHADOW};font-family:{MONO};font-variant-ligatures:none">',
         f'<div style="height:{T_BAR - 2}px;background:#262C38;display:flex;flex-direction:row;align-items:center;gap:8px;padding:0 16px">'
         + "".join(f'<div style="width:12px;height:12px;border-radius:6px;background:{c}"></div>' for c in ["#5B6272", "#5B6272", "#5B6272"])
         + p(f"margin-left:10px;font-family:{SANS};font-size:18px;color:#9AA3B2", "터미널") + '</div>',
         f'<div style="padding:{pad}px 26px">']
    for kind, text in lines:
        t = e(text).replace("\t", "        ")
        if kind == "$":
            t = "$ " + t
        bold = "font-weight:700;" if kind == "$" else ""
        o.append(p(f"font-size:{size}px;line-height:{lh};white-space:pre;{bold}color:{TC[kind]}", t if t else " "))
    o.append('</div></div>')
    return o, h


def line_y(top, i, size=24, lh=1.3, pad=20):
    """baseline-ish bottom of terminal line i (for underlines)"""
    return top + T_BAR + pad + round((i + 1) * size * lh) - 4


def col_x(left, col, size=24, pad=26):
    return left + 2 + pad + round(col * size * 0.6)


# ---------- commits (tools/demo.sh) ----------
C = {
    "A": ("e12ffc2ebe82f5222c822d3ab4c679437a44e7de", "feat: 로그인 화면 추가", "10:01", "kim", []),
    "B": ("15d92cbba8863e2c45123bc9075e79269840eb7d", "feat: 로그인 버튼 추가", "10:02", "kim", ["A"]),
    "L": ("b9f30e506669024d7ccb5c55a2f8708b0e2d9db7", "docs: README 추가", "10:03", "lee", ["B"]),
    "C": ("dd7f15afd87113c573611516bf2699f45cc00dd0", "feat: 비밀번호 찾기 추가", "10:04", "kim", ["L"]),
    "D": ("ad50d3571466f58342112c8761c42ca5097edee3", "docs: README에 실행 방법 추가", "10:05", "kim", ["L"]),
    "M": ("5991c3666a075a0d613595986ddaa830fc07178c", "Merge branch 'feature/login'", "10:06", "kim", ["D", "C"]),
}


def h7(k):
    return C[k][0][:7]


def h8(k):
    return C[k][0][:8]


# A row is (key, lane, refs, is_head). A ref is (name, lane, active, with_origin). "U" = Uncommitted Changes.
def R(k, lane=0, refs=(), head=False):
    return (k, lane, list(refs), head)


MAIN = ("main", 0, True, False)
MAIN_O = ("main", 0, True, True)
MAIN_O_OFF = ("main", 0, False, True)
OM = ("origin/main", 0, False, False)
FL = ("feature/login", 0, True, False)
FL_OFF = ("feature/login", 1, False, False)

ST = {
    "sc1": [R("U"), R("A", 0, [MAIN_O])],
    "sc2": [R("B", 0, [MAIN], True), R("A", 0, [OM])],
    "sc3": [R("B", 0, [MAIN_O], True), R("A")],
    "sc4": [R("L", 0, [OM]), R("B", 0, [MAIN], True), R("A")],
    "sc5": [R("L", 0, [MAIN_O], True), R("B"), R("A")],
    "sc6": [R("L", 0, [FL, MAIN_O_OFF], True), R("B"), R("A")],
    "sc7": [R("C", 0, [FL], True), R("L", 0, [MAIN_O_OFF]), R("B"), R("A")],
    "sc8": [R("D", 0, [MAIN], True), R("C", 1, [FL_OFF]), R("L", 0, [OM]), R("B"), R("A")],
    "sc9": [R("M", 0, [MAIN], True), R("D"), R("C", 1, [FL_OFF]), R("L", 0, [OM]), R("B"), R("A")],
    "sc10": [R("M", 0, [MAIN_O], True), R("D"), R("C", 1, [FL_OFF]), R("L"), R("B"), R("A")],
    "del": [R("M", 0, [MAIN_O], True), R("D"), R("C", 1), R("L"), R("B"), R("A")],
}


def branch_svg(color, size):
    return (f'<svg viewBox="0 0 24 24" style="width:{size}px;height:{size}px;display:block" fill="none" stroke="{color}" stroke-width="3" stroke-linecap="round">'
            '<line x1="6" y1="3" x2="6" y2="15"/><circle cx="18" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M18 9a9 9 0 0 1-9 9"/></svg>')


def ref_html(ref, s, rid):
    name, lane, active, origin = ref
    col = LANE_C[lane]
    bd = col if active else "rgba(128,128,128,0.75)"
    o = (f'<div id="{rid}" style="display:flex;flex-direction:row;align-items:center;height:{round(38*s)}px;flex:none;border:{max(2, round(2*s))}px solid {bd};border-radius:{round(9*s)}px;background:rgba(128,128,128,0.15);overflow:hidden">'
         f'<div style="width:{round(30*s)}px;height:100%;flex:none;background:{col};display:flex;align-items:center;justify-content:center">{branch_svg(VS["bg"], round(20*s))}</div>'
         + p(f"padding:0 {round(10*s)}px;font-size:{round(21*s)}px;line-height:{round(30*s)}px;font-weight:{700 if active else 400};color:{VS['txt']};white-space:nowrap", e(name)))
    if origin:
        o += p(f"padding:0 {round(10*s)}px;font-size:{round(21*s)}px;line-height:{round(30*s)}px;font-style:italic;color:{VS['txt']};border-left:2px solid rgba(128,128,128,0.45)", "origin", f' id="{rid}-o"')
    return o + '</div>'


ICON_PATHS = {
    "search": '<circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/>',
    "terminal": '<polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/>',
    "gear": '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1L7 17M17 7l2.1-2.1"/>',
    "fetch": '<path d="M12 3v12"/><polyline points="7 10 12 15 17 10"/><line x1="4" y1="20" x2="20" y2="20"/>',
    "refresh": '<path d="M20 11a8 8 0 1 0-2.3 5.7"/><polyline points="20 4 20 11 13 11"/>',
}


def ui_icon(name, color, size, sid=""):
    return (f'<svg{sid} viewBox="0 0 24 24" style="width:{size}px;height:{size}px;display:block;flex:none" fill="none" stroke="{color}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
            + ICON_PATHS[name] + '</svg>')


def graph_icon(size, color="#C5C5C5"):
    return (f'<svg viewBox="0 0 16 16" style="width:{size}px;height:{size}px;display:block;flex:none">'
            f'<path fill="{color}" d="M2.6 1h1.5v14H2.6z"/><path fill="{color}" d="M7.3 5h1.4v10H7.3z"/>'
            f'<circle fill="{color}" cx="3.3" cy="8" r="1.9"/><circle fill="{color}" cx="8" cy="2.8" r="1.9"/><circle fill="{color}" cx="12.7" cy="13.2" r="1.9"/>'
            f'<path stroke="{color}" stroke-width="1.4" fill="none" d="M3.3 9.6c2 1.6 6 1 9.4 3.6"/></svg>')


UNC_N = 1


def gg(rows, L=96, T=200, W=1328, s=1.3, tab=True, ctl=False, hdr=True, cols=("author", "commit"), pre="",
       expand=None, expand_h=0, sel=None, win_h=1000, pad_top=0, shadow=True, row_attrs=None, bars=False):
    """Draws the Git Graph tab. Every row, dot and line has its own id so magic move can slide them between
    slides. win_h larger than the slide lets the window run off the bottom edge (bleed)."""
    TAB = round(48 * s) if tab else 0
    CTL = round(56 * s) if ctl else 0
    HDR = round(44 * s) if hdr else 0
    ROW = round(48 * s)
    LANE = round(40 * s)
    GW = round(130 * s)
    RD = round(9 * s)
    LW = max(3, round(4 * s))
    top0 = T + 2 + TAB + CTL + HDR + pad_top
    gx = lambda lane: L + round(34 * s) + lane * LANE
    ys, y = [], top0 + ROW // 2
    for k, *_ in rows:
        ys.append(y)
        y += ROW + (expand_h if k == expand else 0)
    sh = f";box-shadow:{SHADOW}" if shadow else ""
    o = [f'<div id="{pre}gg-win" style="position:absolute;left:{L}px;top:{T}px;width:{W}px;height:{win_h}px;background:{VS["bg"]};border:2px solid {VS["bd"]};border-radius:{round(14*s)}px;overflow:hidden{sh}"></div>']
    if tab:
        o.append(f'<div id="{pre}gg-tab" style="position:absolute;left:{L+2}px;top:{T+2}px;width:{W-4}px;height:{TAB}px;background:{VS["bar"]};border-radius:{round(12*s)}px {round(12*s)}px 0 0;display:flex;flex-direction:row">'
                 f'<div style="height:100%;padding:0 {round(22*s)}px;background:{VS["bg"]};border-top:3px solid {VS["blue"]};display:flex;flex-direction:row;gap:{round(12*s)}px;align-items:center">'
                 + graph_icon(round(22 * s))
                 + p(f"font-size:{round(22*s)}px;color:#FFFFFF", "Git Graph") + p(f"font-size:{round(22*s)}px;color:{VS['dim']}", "×") + '</div></div>')
    if ctl:
        cy = T + 2 + TAB
        dd = lambda t, i: (f'<div id="{pre}ctl-{i}" style="height:{round(38*s)}px;padding:0 {round(12*s)}px;background:{VS["input"]};border:1px solid {VS["bd"]};border-radius:{round(5*s)}px;display:flex;flex-direction:row;gap:{round(10*s)}px;align-items:center">'
                           + p(f"font-size:{round(21*s)}px;color:{VS['txt']}", t) + p(f"font-size:{round(16*s)}px;color:{VS['dim']}", "▼") + '</div>')
        lab = lambda t: p(f"font-size:{round(21*s)}px;color:{VS['txt']}", t)
        o.append(f'<div id="{pre}gg-ctl" style="position:absolute;left:{L+round(20*s)}px;top:{cy}px;width:{W-round(40*s)}px;height:{CTL}px;display:flex;flex-direction:row;gap:{round(14*s)}px;align-items:center">'
                 + lab("Repo:") + dd("hello-git", "repo") + f'<div style="width:{round(14*s)}px"></div>' + lab("Branches:") + dd("Show All", "br") + f'<div style="width:{round(14*s)}px"></div>'
                 + f'<div style="width:{round(24*s)}px;height:{round(24*s)}px;border:2px solid {VS["txt"]};border-radius:4px;display:flex;align-items:center;justify-content:center;font-size:{round(16*s)}px;line-height:1;color:{VS["txt"]}">✓</div>'
                 + lab("Show Remote Branches") + '<div style="flex:1"></div>'
                 + "".join(ui_icon(n, VS["txt"], round(26 * s), f' id="{pre}ic-{n}"') + f'<div style="width:{round(6*s)}px"></div>' for n in ["search", "terminal", "gear", "fetch", "refresh"])
                 + '</div>')
    CW = {"date": round(260 * s), "author": round(110 * s), "commit": round(150 * s)}
    NAMES = {"date": "Date", "author": "Author", "commit": "Commit"}
    fs = round(23 * s)
    if hdr:
        hy = T + 2 + TAB + CTL
        cells = p(f"width:{GW-round(20*s)}px;flex:none;font-size:{round(21*s)}px;font-weight:700;color:{VS['txt']}", "Graph", f' id="{pre}h-graph"') + p(f"flex:1;font-size:{round(21*s)}px;font-weight:700;color:{VS['txt']}", "Description", f' id="{pre}h-desc"')
        for c in cols:
            cells += p(f"width:{CW[c]}px;flex:none;font-size:{round(21*s)}px;font-weight:700;color:{VS['txt']}", NAMES[c], f' id="{pre}h-{c}"')
        o.append(f'<div id="{pre}gg-hdr" style="position:absolute;left:{L+round(20*s)}px;top:{hy}px;width:{W-round(40*s)}px;height:{HDR}px;display:flex;flex-direction:row;align-items:center;border-bottom:1px solid {VS["bd"]}">{cells}</div>')
    idx = {k: i for i, (k, *_) in enumerate(rows)}
    has_unc = rows[0][0] == "U"
    if sel in idx:
        i = idx[sel]
        o.append(f'<div id="{pre}sel" style="position:absolute;left:{L+2}px;top:{ys[i]-ROW//2}px;width:{W-4}px;height:{ROW+expand_h}px;background:{VS["sel"]}"></div>')
    for i, (k, lane, refs, hd) in enumerate(rows):
        parents = [rows[1][0]] if k == "U" else C[k][4]
        for par in parents:
            if par not in idx:
                continue
            j = idx[par]
            lp = rows[j][1]
            x1, y1, x2, y2 = gx(lane), ys[i], gx(lp), ys[j]
            col = GRAY if k == "U" else LANE_C[max(lane, lp)]
            if lane == lp:
                d = f"M{x1},{y1} L{x2},{y2}"
            elif lp > lane:
                yb = ys[i + 1]
                d = f"M{x1},{y1} C{x1},{y1 + (yb-y1)*0.6} {x2},{y1 + (yb-y1)*0.4} {x2},{yb} L{x2},{y2}"
            else:
                ya = ys[j - 1]
                d = f"M{x1},{y1} L{x1},{ya} C{x1},{ya + (y2-ya)*0.6} {x2},{ya + (y2-ya)*0.4} {x2},{y2}"
            mx, Mx, my, My = min(x1, x2) - LW, max(x1, x2) + LW, min(y1, y2), max(y1, y2)
            o.append(f'<svg id="{pre}e-{k}-{par}" viewBox="{mx} {my} {Mx-mx} {My-my}" style="position:absolute;left:{mx}px;top:{my}px;width:{Mx-mx}px;height:{My-my}px;overflow:visible">'
                     f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{LW}"/></svg>')
    for i, (k, lane, refs, hd) in enumerate(rows):
        col = GRAY if k == "U" else LANE_C[lane]
        hollow = k == "U" or (hd and not has_unc)
        st = f"background:{VS['bg']};border:{LW}px solid {col}" if hollow else f"background:{col};border:{LW}px solid {col}"
        extra = (row_attrs or {}).get("d-" + k, "")
        o.append(f'<div id="{pre}d-{k}"{extra} style="position:absolute;left:{gx(lane)-RD}px;top:{ys[i]-RD}px;width:{2*RD}px;height:{2*RD}px;border-radius:50%;{st}"></div>')
    for i, (k, lane, refs, hd) in enumerate(rows):
        if k == "U":
            desc = p(f"font-size:{fs}px;font-weight:700;color:{VS['txt']};white-space:nowrap", f"Uncommitted Changes ({UNC_N})", f' id="{pre}unc"')
            vals = {"date": "29 Oct 2026 10:02", "author": "*", "commit": "*"}
        else:
            msg, tm, au = C[k][1], C[k][2], C[k][3]
            dot = f'<div id="{pre}hd-{k}" style="width:{round(14*s)}px;height:{round(14*s)}px;flex:none;border:{max(2, round(3*s))}px solid {LANE_C[lane]};border-radius:50%"></div>' if hd else ""
            msg_html = (f'<div style="width:{[160, 120, 190, 140, 170, 130][i % 6]}px;height:{round(10*s)}px;flex:none;border-radius:{round(5*s)}px;background:#3A3A3A"></div>' if bars else p(f"min-width:0;font-size:{fs}px;color:{VS['txt']};white-space:nowrap;overflow:hidden;text-overflow:ellipsis", e(msg), f' id="{pre}msg-{k}"'))
            desc = dot + "".join(ref_html(r, s, f"{pre}ref-{k}-{n}") for n, r in enumerate(refs)) + msg_html
            vals = {"date": f"29 Oct 2026 {tm}", "author": au, "commit": h8(k)}
        cells = f'<div style="flex:1;min-width:0;display:flex;flex-direction:row;gap:{round(10*s)}px;align-items:center;overflow:hidden;padding-right:{round(16*s)}px">{desc}</div>'
        for c in cols:
            cells += p(f"width:{CW[c]}px;flex:none;font-size:{fs}px;color:{VS['txt']}", vals[c], f' id="{pre}{c}-{k}"')
        extra = (row_attrs or {}).get("r-" + k, "")
        o.append(f'<div id="{pre}r-{k}"{extra} style="position:absolute;left:{L+GW}px;top:{ys[i]-ROW//2}px;width:{W-GW-round(20*s)}px;height:{ROW}px;display:flex;flex-direction:row;align-items:center">{cells}</div>')
    geo = dict(ys=ys, ROW=ROW, gx=gx, L=L, W=W, RD=RD)
    return o, geo


def fade_all(parts, order, kind="fade"):
    return [x.replace(' style=', f'{bi(kind, order)} style=', 1) for x in parts]


# =====================================================================================
# 1. cover
# =====================================================================================
cov = [f'<section id="cover" data-transition="fade" style="background:#1D2330;color:#F6F5F1;font-family:{SANS};padding:128px;display:flex;flex-direction:column;justify-content:center;gap:36px;word-break:keep-all">',
       '<p style="font-size:28px;font-weight:700;color:#8FB3FF">KANT AX/AI 엔지니어 트랙 · 05</p>',
       f'<h1{SLAM(1)} style="font-size:104px;font-weight:900;line-height:1.1;color:#F6F5F1">Git Graph로<br>기록 보기</h1>',
       '<p style="font-size:40px;line-height:1.45;color:#BFC6D4">터미널에서 친 결과를<br>VS Code에서 그림으로 확인해요</p>']
g, _ = gg(ST["sc10"], L=930, T=250, W=1200, s=1.3, cols=(), pre="cv-", pad_top=10, win_h=900)
cov += g
W("cover", cov, "VS Code에 Git Graph 확장을 설치해서 지금까지 터미널로 만든 커밋과 브랜치를 그림으로 봐요. 명령은 지금처럼 터미널에서 치고, 친 결과를 Git Graph로 확인하는 게 오늘의 목표예요.")

# =====================================================================================
# 2. toc: one ruled list, no cards
# =====================================================================================
PARTS = [("들어가기", "터미널 기록과 Git Graph가 어떻게 다른지", "3–4"),
         ("1. 설치하고 열기", "확장 탭에서 설치하고, 저장소 폴더에서 열기", "5–6"),
         ("2. 화면 읽기", "칸, 점, 굵은 이름표, origin/main", "7–10"),
         ("3. 명령 치고 확인하기", "commit부터 merge까지 열 번, 커밋 상세 보기", "11–21"),
         ("4. 막힐 때와 실제 상황", "메뉴 대신 터미널, 안 보일 때, 그림 보고 명령 고르기", "22–26")]
t = [sec("toc")] + head("05 · Git Graph", "오늘의 순서", BL)
y0, RH = 236, 152
for i, (h_, s_, pg) in enumerate(PARTS):
    y = y0 + i * RH
    t.append(f'<div data-build-in="rise order 1"{DELAY(i * 90)} style="position:absolute;left:96px;top:{y}px;width:1728px;height:{RH}px;border-top:2px solid {HAIR};display:flex;flex-direction:row;align-items:center">'
             + p(f"width:620px;flex:none;font-size:44px;font-weight:700;color:{INK}", h_)
             + p(f"flex:1;font-size:32px;color:{SUB}", s_)
             + p(f"width:160px;flex:none;font-size:30px;text-align:right;color:{MUTE}", pg + "쪽") + '</div>')
t.append(f'<div style="position:absolute;left:96px;top:{y0 + 5 * RH}px;width:1728px;height:2px;background:{HAIR}"></div>')
W("toc", t, "3부가 오늘의 중심이에요. 02, 03에서 배운 명령을 하나씩 치고 Git Graph에서 무엇이 바뀌는지 봐요. 4부 끝에서는 그림만 보고 다음에 칠 명령을 골라 봐요.")

# =====================================================================================
# 3. why: the log hides the fork
# =====================================================================================
w = [sec("why")] + head("왜 필요할까요", "git log --oneline으로는 갈라진 길이 안 보여요", BL)
LOG = [("$", "git log --oneline"), ("o", f"{h7('M')} (HEAD -> main, origin/main) Merge branch 'feature/login'"), ("o", f"{h7('D')} docs: README에 실행 방법 추가"),
       ("o", f"{h7('C')} (feature/login) feat: 비밀번호 찾기 추가"), ("o", f"{h7('L')} docs: README 추가"), ("o", f"{h7('B')} feat: 로그인 버튼 추가"), ("o", f"{h7('A')} feat: 로그인 화면 추가")]
WT_TOP = 210
wterm, wth = terminal(LOG, 96, WT_TOP, 1090, size=24, lh=1.3, tid="why-term")
WIN_T = WT_TOP + wth + 36
g, geo = gg(ST["sc10"], L=700, T=WIN_T, W=1124, s=1.2, tab=False, cols=("commit",), pre="w-", win_h=900)
w += fade_all(g, 1, "rise") + wterm
ys = geo["ys"]
lane_x = geo["gx"](1)
w.append(ring(2, lane_x - 40, ys[1] - 10, 80, ys[3] - ys[1] + 20, OR))
w.append(leader(2, [(560, ys[2] + 30), (lane_x - 70, ys[2] + 10)], OR))
w.append(label(96, ys[2] - 10, 460, "feature/login에서 갈라졌다가<br>merge로 다시 만나요", 2, size=32, color=INK, extra=DELAY(250)))
W("why", w, "터미널 기록으로는 갈라졌다가 합쳐진 모양이 안 보여요. 같은 저장소를 터미널과 Git Graph로 본 화면이라 커밋 순서와 메시지는 같아요. Git Graph에서는 분홍 선으로 바로 보여요. Git Graph는 기록을 보여 주기만 하고 저장소를 바꾸지 않아요.")

# =====================================================================================
# 4. big picture: who writes, who reads
# =====================================================================================
bp = [sec("bigpic")] + head("큰 그림", "Git Graph는 내 컴퓨터에 있는 기록을 읽어서 그려요", BL)
# my computer band
bp.append(f'<div style="position:absolute;left:96px;top:450px;width:1728px;height:590px;border:3px dashed #B9C2D3;border-radius:28px"></div>')
bp.append(label(136, 470, 600, "내 컴퓨터", size=30, color=BL))
bterm, _ = terminal([("$", "git commit -m ..."), ("$", "git push origin main"), ("$", "git fetch origin")], 136, 640, 520, size=28, tid="bp-term")
bp += bterm
# repo: a column of dots
RX, RY = 960, 560
bp.append(f'<div id="bp-repo" style="position:absolute;left:{RX-140}px;top:{RY}px;width:280px;height:420px;background:#FFFFFF;border:2px solid {HAIR};border-radius:24px"></div>')
for i in range(1, 4):
    y = RY + 70 + i * 76
    bp.append(f'<div style="position:absolute;left:{RX-4}px;top:{y-76}px;width:8px;height:76px;background:#9DB8F2"></div>')
for i in range(4):
    y = RY + 70 + i * 76
    bp.append(f'<div style="position:absolute;left:{RX-22}px;top:{y-22}px;width:44px;height:44px;border-radius:50%;background:{BL}"></div>')
bp.append(label(RX - 140, RY + 352, 280, "저장소 기록 (.git)", size=28, color=INK, align="center"))
# git graph mini
g, _ = gg(ST["sc10"], L=1270, T=560, W=520, s=0.95, hdr=False, cols=(), pre="bp-", win_h=420, pad_top=10, bars=True)
bp += g
# GitHub on top
bp.append(f'<div id="bp-gh" style="position:absolute;left:{RX-190}px;top:210px;width:380px;height:130px;background:{PUR};border-radius:24px;display:flex;flex-direction:row;gap:18px;align-items:center;justify-content:center">'
          f'<x-icon name="Cloud" style="width:60px;height:60px;color:#FFFFFF"></x-icon>' + p("font-size:44px;font-weight:700;color:#FFFFFF", "GitHub") + '</div>')

def arrow(order, x1, y1, x2, y2, color, head=True):
    import math
    a = math.atan2(y2 - y1, x2 - x1)
    hx1, hy1 = x2 - 22 * math.cos(a - 0.45), y2 - 22 * math.sin(a - 0.45)
    hx2, hy2 = x2 - 22 * math.cos(a + 0.45), y2 - 22 * math.sin(a + 0.45)
    hd = f'<path d="M{hx1:.0f},{hy1:.0f} L{x2},{y2} L{hx2:.0f},{hy2:.0f}"/>' if head else ""
    return (f'<svg{bi("draw", order) if order else ""} viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible">'
            f'<g fill="none" stroke="{color}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"><path d="M{x1},{y1} L{x2},{y2}"/>{hd}</g></svg>')


bp.append(arrow(1, 680, 770, 800, 770, INK))
bp.append(label(650, 680, 180, "명령으로<br>바꿔요", 1, size=28, align="center"))
bp.append(arrow(2, 1120, 770, 1250, 770, GR))
bp.append(label(1095, 680, 180, "읽어서<br>그려요", 2, size=28, color=GR, align="center"))
bp.append(arrow(3, 925, 552, 925, 350, PUR))
bp.append(arrow(4, 995, 350, 995, 552, PUR))
bp.append(label(500, 380, 400, "git push origin main", 3, size=28, color=PUR, align="right", extra=DELAY(200)))
bp.append(label(1020, 380, 400, "git fetch origin", 4, size=28, color=PUR, extra=DELAY(200)))
# a commit dot travels along each road (push goes up, fetch comes down)
bp.append('<svg viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none">'
          '<path id="bp-road-up" d="M925,640 L925,360" fill="none" stroke="none"/><path id="bp-road-down" d="M995,300 L995,530" fill="none" stroke="none"/></svg>')
bp.append(f'<div{PATH(3, "bp-road-up", 1200)} style="position:absolute;left:{925-16}px;top:{360-16}px;width:32px;height:32px;border-radius:50%;background:{BL};box-shadow:0 0 0 5px #FFFFFF"></div>')
bp.append(f'<div{PATH(4, "bp-road-down", 1200)} style="position:absolute;left:{995-16}px;top:{530-16}px;width:32px;height:32px;border-radius:50%;background:{GR};box-shadow:0 0 0 5px #FFFFFF"></div>')
W("bigpic", bp, "Git Graph는 내 컴퓨터의 저장소 기록을 읽어서 그림으로 보여 줘요. 기록을 바꾸는 건 터미널에서 치는 명령이에요. Git Graph는 GitHub에 직접 물어보지 않아요. 팀원이 GitHub에 올린 커밋은 git fetch origin으로 받아 와야 그림에 나타나요. 막히면 지금 하려는 일이 이 그림의 어느 화살표인지 먼저 찾아봐요.")

# =====================================================================================
# part 1: install, open (VS Code is the hero, steps are plain words on the right)
# =====================================================================================
def vscode_shell(L, T, Wd, Hd, active="ext", pre=""):
    o = [f'<div id="{pre}vs-win" style="position:absolute;left:{L}px;top:{T}px;width:{Wd}px;height:{Hd}px;background:{VS["bg"]};border:2px solid {VS["bd"]};border-radius:16px;overflow:hidden;box-shadow:{SHADOW}"></div>',
         f'<div id="{pre}vs-act" style="position:absolute;left:{L+2}px;top:{T+2}px;width:84px;height:{Hd-4}px;background:{VS["bar"]};border-radius:14px 0 0 0;display:flex;flex-direction:column;align-items:center;gap:30px;padding-top:30px">']
    for n in ["files", "search", "scm", "run", "ext"]:
        col = "#FFFFFF" if n == active else "#858585"
        bar = f'border-left:4px solid {VS["blue"]};' if n == active else 'border-left:4px solid transparent;'
        o[-1] += f'<div id="{pre}act-{n}" style="width:84px;height:48px;display:flex;align-items:center;justify-content:center;{bar}">{act_icon(n, col)}</div>'
    o[-1] += '</div>'
    return o


def act_icon(n, col):
    paths = {
        "files": '<path d="M14 3H6v18h12V7z"/><polyline points="14 3 14 7 18 7"/>',
        "search": ICON_PATHS["search"],
        "scm": '<circle cx="6" cy="5" r="2.5"/><circle cx="6" cy="19" r="2.5"/><circle cx="18" cy="8" r="2.5"/><line x1="6" y1="7.5" x2="6" y2="16.5"/><path d="M18 10.5c0 4-6 3-11 6.5"/>',
        "run": '<polygon points="7 4 19 12 7 20"/>',
        "ext": '<rect x="3" y="10" width="6" height="6"/><rect x="9" y="10" width="6" height="6"/><rect x="3" y="16" width="6" height="5"/><rect x="13" y="3" width="7" height="7" transform="rotate(10 16 6)"/>',
    }
    return f'<svg viewBox="0 0 24 24" style="width:40px;height:40px;display:block" fill="none" stroke="{col}" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round">{paths[n]}</svg>'


def disc(n, color, size=48, extra=""):
    return p(f"width:{size}px;height:{size}px;flex:none;font-size:{round(size*0.55)}px;font-weight:900;line-height:{size}px;text-align:center;color:#FFFFFF;background:{color};border-radius:{size//2}px{extra}", str(n))


def marker(n, x, y, order, color=OR):
    return f'<div{bi("pop", order)} style="position:absolute;left:{x}px;top:{y}px">' + disc(n, color, 52, ";box-shadow:0 0 0 5px #1F1F1F") + '</div>'


def steps(L, T, Wd, items, order0=2, color=OR, gap=40, foot=None):
    """Numbered steps as plain words, separated by hairlines. Each appears with its spotlight."""
    o = []
    y = T
    for n, (main_, sub_) in enumerate(items, 1):
        o.append(f'<div{bi("rise", order0 + n - 1)}{DIM("steps")} style="position:absolute;left:{L}px;top:{y}px;width:{Wd}px;display:flex;flex-direction:row;gap:22px;align-items:flex-start">'
                 + disc(n, color, 52) + '<div style="display:flex;flex-direction:column;gap:8px;padding-top:4px">'
                 + p(f"font-size:34px;font-weight:700;line-height:1.35;color:{INK}", main_)
                 + (p(f"font-size:27px;line-height:1.45;color:{SUB}", sub_) if sub_ else "") + '</div></div>')
        nm = main_.count("<br>") + 1
        y += gap + round(34 * 1.35 * nm) + (round(27 * 1.45 * (sub_.count("<br>") + 1)) + 8 if sub_ else 0)
    if foot:
        o.append(label(L, 950, Wd, foot, order0 + len(items), size=26, color=SUB, weight=400))
    return o


ins = [sec("install")] + head("설치하고 열기", "확장 탭에서 Git Graph를 찾아 설치해요", "#3A4150")
VL, VT, VW = 96, 200, 1150
ins += vscode_shell(VL, VT, VW, 1000, active="ext")
PX = VL + 86
ins.append(f'<div style="position:absolute;left:{PX}px;top:{VT+2}px;width:{VW-88}px;height:1000px;background:{VS["bar"]};padding:30px 32px;display:flex;flex-direction:column;gap:22px">'
           + p(f"font-size:24px;font-weight:700;color:{VS['txt']}", "EXTENSIONS: MARKETPLACE")
           + f'<div id="ins-search" style="height:60px;background:{VS["input"]};border:2px solid {VS["blue"]};border-radius:6px;padding:0 18px;display:flex;align-items:center">' + p(f"font-size:30px;color:#FFFFFF", "git graph") + '</div>'
           + f'<div style="background:#04395E;border-radius:8px;padding:24px;display:flex;flex-direction:row;gap:24px">'
           + f'<div style="width:112px;height:112px;flex:none;background:#2B2B2B;border-radius:10px;display:flex;align-items:center;justify-content:center">{graph_icon(76)}</div>'
           + '<div style="flex:1;display:flex;flex-direction:column;gap:8px">'
           + p(f"font-size:32px;font-weight:700;color:#FFFFFF", "Git Graph")
           + p(f"font-size:24px;line-height:1.4;color:{VS['txt']}", "View a Git Graph of your repository, and perform Git actions from the graph.")
           + '<div style="display:flex;flex-direction:row;align-items:center;justify-content:space-between;margin-top:8px">'
           + p(f"font-size:26px;font-weight:700;color:{VS['txt']}", "mhutchie", ' id="ins-author"')
           + p(f"font-size:26px;color:#FFFFFF;background:{VS['blue']};padding:4px 22px;border-radius:4px", "Install", ' id="ins-install"') + '</div></div></div>'
           + ''.join(f'<div style="border-radius:8px;padding:18px 24px;display:flex;flex-direction:row;gap:24px;align-items:center">'
                     f'<div style="width:112px;height:84px;flex:none;background:#2B2B2B;border-radius:10px"></div>'
                     f'<div style="display:flex;flex-direction:column;gap:12px"><div style="width:{a}px;height:14px;border-radius:7px;background:#3A3A3A"></div><div style="width:{b}px;height:10px;border-radius:5px;background:#2E2E2E"></div></div></div>'
                     for a, b in [(260, 420), (200, 360), (300, 300)])
           + '</div>')
for k, tg in enumerate(["act-ext", "ins-search", "ins-install"]):
    ins += [spot(k + 2, target=tg, pad=10, r=10, dim=0.5), cursor(k + 2, target=tg)]
ins += [spot_off(5), cursor_off(5)]
ins += steps(1310, 250, 514, [("왼쪽 막대의 확장 아이콘", "Windows Ctrl+Shift+X<br>Mac Cmd+Shift+X"),
                              ("검색창에 git graph", None),
                              ("만든 사람이 mhutchie인지<br>보고 Install", None)], order0=2,
             foot="설치가 끝나면 Install 자리에<br>톱니바퀴가 나와요.")
W("install", ins, "확장 탭에서 mhutchie가 만든 Git Graph를 설치해요. VS Code 왼쪽 세로 막대에서 네모 네 개 모양 아이콘이 확장(Extensions)이에요. 검색 결과에 이름이 비슷한 확장이 여러 개 나오니 만든 사람을 꼭 봐요. 설치하고 VS Code를 다시 켤 필요는 없어요. 화면이 한국어로 되어 있으면 Install 대신 설치라고 나와요.")

op = [sec("open")] + head("설치하고 열기", "저장소 폴더를 열고, 아래 막대의 Git Graph를 눌러요", "#3A4150")
VL, VT, VW, VH = 96, 200, 1150, 840
op += vscode_shell(VL, VT, VW, VH, active="scm")
PX = VL + 86
op.append(f'<div style="position:absolute;left:{PX}px;top:{VT+2}px;width:440px;height:{VH-48}px;background:{VS["bar"]};padding:28px;display:flex;flex-direction:column;gap:20px">'
          + '<div style="display:flex;flex-direction:row;align-items:center;justify-content:space-between">' + p(f"font-size:22px;font-weight:700;color:{VS['txt']}", "SOURCE CONTROL")
          + f'<div id="op-scm" style="display:flex;padding:6px">{graph_icon(32)}</div></div>'
          + f'<div style="height:52px;background:{VS["input"]};border:1px solid {VS["bd"]};border-radius:4px;padding:0 16px;display:flex;align-items:center">' + p(f"font-size:22px;color:{VS['dim']}", "Message") + '</div>'
          + p(f"font-size:24px;color:{VS['txt']}", "Changes") + '</div>')
op.append(f'<div style="position:absolute;left:{PX+440}px;top:{VT+2}px;width:{VW-88-440}px;height:{VH-48}px;padding:32px;display:flex;flex-direction:column;gap:14px">'
          + f'<div style="background:{VS["bar"]};border:1px solid {VS["bd"]};border-radius:8px;padding:14px 16px;display:flex;flex-direction:column;gap:10px;box-shadow:0 8px 24px rgba(0,0,0,.35)">'
          + p(f"font-size:24px;color:#FFFFFF;background:{VS['input']};border:2px solid {VS['blue']};border-radius:4px;padding:6px 12px", "&gt; git graph", ' id="op-pal"')
          + p(f"font-size:23px;color:#FFFFFF;background:#04395E;padding:6px 12px;border-radius:4px", "Git Graph: View Git Graph (git log)") + '</div></div>')
op.append(f'<div style="position:absolute;left:{VL+2}px;top:{VT+VH-46}px;width:{VW-4}px;height:44px;background:{VS["bar"]};border-top:1px solid {VS["bd"]};border-radius:0 0 14px 14px;padding:0 24px;display:flex;flex-direction:row;gap:30px;align-items:center">'
          + f'<div style="display:flex;flex-direction:row;gap:8px;align-items:center">{branch_svg(VS["txt"], 24)}' + p(f"font-size:23px;color:{VS['txt']}", "main") + '</div>' + p(f"font-size:23px;color:{VS['txt']}", "⊗ 0  ⚠ 0")
          + p(f"font-size:23px;color:{VS['txt']};padding:0 8px;line-height:34px", "Git Graph", ' id="op-sb"') + '</div>')
for k, tg in enumerate(["op-sb", "op-scm"]):
    op += [spot(k + 2, target=tg, pad=10, r=10, dim=0.5), cursor(k + 2, target=tg)]
op += [spot(4, PX + 456, VT + 18, 590, 300, pad=0, r=12, dim=0.5), cursor_off(4), keys(4, PX + 490, VT + 200, "Ctrl+Shift+P", 28)]
op += [spot_off(5), cursor_off(5)]
op += steps(1310, 250, 514, [("아래 상태 표시줄의<br>Git Graph", "가장 빨라요"),
                             ("소스 제어 탭 위의<br>그래프 아이콘", None),
                             ("명령 팔레트에서<br>git graph", "Windows Ctrl+Shift+P<br>Mac Cmd+Shift+P")], order0=2,
            foot="먼저 File &gt; Open Folder로<br>hello-git 폴더를 열어 둬요.")
W("open", op, "Git Graph는 VS Code에 열린 폴더가 Git 저장소일 때만 동작해요. File > Open Folder(한국어 화면은 파일 > 폴더 열기)로 git init을 했던 hello-git 폴더를 먼저 열어요. 그다음 세 방법 중 아무거나 쓰면 돼요. 열리면 편집기 자리에 Git Graph 탭이 생겨요.")

# =====================================================================================
# part 2: reading the screen
# =====================================================================================
ov = [sec("overview")] + head("화면 읽기", "한 줄이 커밋 하나, 맨 위가 가장 최근이에요", BL)
OT = 330
g, geo = gg(ST["sc10"], T=OT, W=1728, s=1.15, ctl=True, cols=("date", "author", "commit"), pre="ov-", win_h=800)
ov += g
COLS = [("ov-h-graph", "그래프"), ("ov-h-desc", "이름표와 메시지"), ("ov-h-date", "날짜"), ("ov-h-author", "작성자"), ("ov-h-commit", "커밋 번호")]
rows_bottom = geo["ys"][-1] + geo["ROW"] // 2
for n, (hid, name) in enumerate(COLS, 1):
    x, y, w_, h_ = rect("overview", hid, (100 + n * 300, 470, 120, 30))
    if hid == "ov-h-graph":
        w_ = 110
    if hid == "ov-h-desc":
        w_ = 300
    cx = x + (250 if hid == "ov-h-desc" else min(w_, 200) // 2)
    ov.append(label(cx - 120, 228, 240, name, 1, size=30, color=BL, align="center", extra=DELAY((n - 1) * 110)))
    ov.append(leader(1, [(cx, 280), (cx, OT - 4)], BL, 2))
    sw = (rect("overview", "ov-h-date")[0] - x - 24) if hid == "ov-h-desc" else w_
    if hid in ("ov-h-desc", "ov-h-commit"):
        ov.append(spot(2 if hid == "ov-h-desc" else 3, x - 14, y - 6, sw + 20, rows_bottom - y + 12, pad=4, r=10, dim=0.55))
ov.append(spot_off(4))
W("overview", ov, "표 한 줄이 커밋 하나이고, git log --oneline처럼 맨 위가 가장 최근이에요. 어두운 테마 화면이지만 밝은 테마여도 배치는 같아요. 작성자 칸의 lee는 팀원이 GitHub에 올린 커밋이에요. 맨 위 줄의 Repo는 저장소 이름, Branches: Show All은 모든 브랜치를 보여 준다는 뜻이라 그대로 두면 돼요. 오른쪽 위 아이콘 중에서는 새로고침만 써요.")

# dots: 03 drawing as a small satellite, Git Graph as hero, the dots fly over
dt = [sec("dots")] + head("화면 읽기", "03의 그림을 세우면 Git Graph가 돼요", BL)
DY = 560
for i in range(3):
    x = 196 + i * 200
    if i:
        dt.append(f'<div style="position:absolute;left:{x-200}px;top:{DY-3}px;width:200px;height:6px;background:#9DB8F2"></div>')
for i, k in enumerate(["A", "B", "L"]):
    x = 196 + i * 200
    dt.append(f'<div id="o3-{k}" style="position:absolute;left:{x-24}px;top:{DY-24}px;width:48px;height:48px;border-radius:50%;background:{BL}"></div>')
    dt.append(p(f"position:absolute;left:{x-90}px;top:{DY+40}px;width:180px;font-family:{MONO};font-size:26px;font-weight:700;text-align:center;color:{INK}", h7(k)))
dt.append(label(96, 380, 700, "03 슬라이드", size=30, color=MUTE))
dt.append(label(96, DY + 130, 700, "왼쪽에서 오른쪽으로 쌓여요", size=30, color=SUB, weight=400))
dt.append(arrow(None, 146, DY + 210, 640, DY + 210, "#B6BCC8"))
g, geo = gg(ST["sc5"], L=820, T=300, W=1004, s=1.45, tab=False, hdr=True, cols=("commit",), pre="dg-", win_h=900, pad_top=10,
            row_attrs={f"d-{k}": f' data-build-in="fly order 1" data-from="o3-{k}"' for k in ["A", "B", "L"]})
dt += g
ys = geo["ys"]
gx0 = geo["gx"](0)
dt.append(arrow(2, gx0, ys[-1] + 150, gx0, ys[-1] + 60, "#8C95A6"))
dt.append(label(gx0 + 40, ys[-1] + 96, 640, "Git Graph는 아래에서 위로 쌓여요", 2, size=30, color=VS["txt"], extra=DELAY(250)))
dt.append(label(96, 900, 760, "커밋 번호는 8자리로 나와요.<br>터미널의 7자리와 앞부분이 같아요.", 3, size=30, color=INK, weight=400))
dt.append(pulse(3, "dg-commit-A"))
W("dots", dt, "03에서는 시간이 왼쪽에서 오른쪽으로 흐르게 그렸어요. Git Graph는 git log처럼 새 커밋을 위에 올려요. 03 그림을 세웠다고 생각하면 돼요. 선은 커밋이 어느 커밋 다음에 만들어졌는지 이어 줘요. e12ffc2와 e12ffc2e처럼 Git Graph 쪽이 한 글자 더 길어요.")

# labels: close-up on one row, three leader notes above it
lb = [sec("labels")] + head("화면 읽기", "굵은 이름표가 지금 있는 브랜치예요", BL)
LT = 470
g, geo = gg(ST["sc6"], L=96, T=LT, W=1728, s=1.75, tab=False, hdr=False, cols=("commit",), pre="lb-", win_h=420, pad_top=18)
lb += g
ys = geo["ys"]
hx, hy, hw, hh = rect("labels", "lb-hd-L", (230, ys[0] - 12, 24, 24))
fx, fy, fw, fh = rect("labels", "lb-ref-L-0", (270, ys[0] - 33, 330, 66))
ox, oy, ow, oh = rect("labels", "lb-ref-L-1-o", (900, ys[0] - 33, 120, 66))
NOTES = [(hx + hw // 2, hy, 96, "속이 빈 점", "HEAD가 가리키는 커밋"),
         (fx + fw // 2, fy, 560, "굵은 글씨, 색 테두리", "지금 있는 브랜치, HEAD -&gt;"),
         (ox + ow // 2, oy, 1130, "기울어진 origin", "origin/main도 같은 커밋")]
for n, (tx, ty, lx, t1, t2) in enumerate(NOTES, 1):
    lb.append(label(lx, 222, 420, f"{t1}<br><span style=\"font-weight:400;color:{SUB}\">{t2}</span>", n, size=32, color=INK, extra=DIM("notes")))
    lb.append(leader(n, [(lx + 12, 330), (lx + 12, 380), (tx, 420), (tx, ty - 10)] if abs(lx + 12 - tx) > 4 else [(tx, 330), (tx, ty - 10)], BL))
LOGT = 900
lterm, _ = terminal([("$", "git log --oneline"), ("o", f"{h7('L')} (HEAD -> feature/login, origin/main, main) docs: README 추가")], 96, LOGT - 40, 1728, size=26, tid="lb-term")
lterm[0] = lterm[0].replace(' style=', SLIDE(4, 0, 80) + ' style=', 1)
lb += lterm
lb.append(underline(5, col_x(96, 9, 26), col_x(96, 9 + len("HEAD -> feature/login"), 26), line_y(LOGT - 40, 1, 26) + 2, OR))
W("labels", lb, "굵은 글씨에 색 테두리인 이름표가 지금 있는 브랜치예요. 브랜치 feature/login을 막 만든 화면이라 이름표가 두 개인데, feature/login만 굵어요. 터미널의 HEAD -> feature/login과 같은 뜻이에요. 맨 앞의 빈 점은 HEAD가 가리키는 커밋이라는 표시예요. main 옆의 기울어진 origin은 origin/main도 여기 있다는 뜻이에요.")

# origin: GitHub panel beside my Git Graph
og = [sec("origin")] + head("화면 읽기", "origin/main은 마지막으로 GitHub과 주고받은 위치예요", PUR)
g, geo = gg(ST["sc3"], L=96, T=330, W=1060, s=1.75, cols=("commit",), pre="og-", win_h=408)
og += g
og.append(label(96, 250, 700, "내 Git Graph", size=32, color=INK))
GX, GY, GW_ = 1220, 330, 604
og.append(f'<div id="og-gh" style="position:absolute;left:{GX}px;top:{GY}px;width:{GW_}px;height:408px;background:#FFFFFF;border:2px solid {HAIR};border-radius:20px;overflow:hidden;box-shadow:{SHADOW}">'
          f'<div style="height:72px;background:{PUR};display:flex;flex-direction:row;align-items:center;gap:14px;padding:0 26px"><x-icon name="Cloud" style="width:36px;height:36px;color:#FFFFFF"></x-icon>'
          + p("font-size:28px;font-weight:700;color:#FFFFFF", "GitHub · kim/hello-git") + '</div>'
          + ''.join(f'<div style="height:110px;display:flex;flex-direction:row;align-items:center;gap:18px;padding:0 26px;border-top:{0 if i == 0 else 1}px solid #ECE9E2">'
                    + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{INK}", h7(k)) + p(f"flex:1;font-size:28px;color:{SUB};white-space:nowrap;overflow:hidden;text-overflow:ellipsis", e(C[k][1]))
                    + (p(f"font-size:22px;font-weight:700;color:#FFFFFF;background:{PUR};padding:2px 12px;border-radius:6px", "main") if i == 0 else "") + '</div>'
                    for i, k in enumerate(["L", "B", "A"]))
          + '</div>')
og.append(label(GX, 250, GW_, "GitHub의 실제 main", size=32, color=PUR))
og.append(f'<div{bi("fade", 1)} id="og-new" style="position:absolute;left:{GX+2}px;top:{GY+72}px;width:{GW_-4}px;height:110px;border:4px solid {OR};border-radius:6px"></div>')
og.append(f'<div style="position:absolute;left:96px;top:{GY + 480}px;width:1728px;height:2px;background:{HAIR}"></div>')
og.append(label(96, GY + 530, 1728, "팀원 lee가 올린 b9f30e5는 GitHub에만 있고 내 Git Graph에는 아직 없어요.", 1, size=36))
og.append('<svg viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none">'
          f'<path id="og-road" d="M{GX+30},{GY+127} C{GX-60},{GY-60} 1100,{GY-60} 1010,{GY+40}" fill="none" stroke="none"/></svg>')
og.append(f'<div{PATH(2, "og-road", 1300)} style="position:absolute;left:{1010-15}px;top:{GY+40-15}px;width:30px;height:30px;border-radius:50%;background:{LANE_C[0]};box-shadow:0 0 0 4px #1F1F1F"></div>')
og.append(label(96, GY + 620, 1728, f'<span style="font-family:{MONO};color:{PUR}">git fetch origin</span>을 쳐야 내 컴퓨터로 받아지고 그림에 나타나요.', 2, size=32, color=SUB, weight=400))
W("origin", og, "이름표가 main | origin 하나로 붙어 있어도 GitHub과 같다는 보장은 없어요. origin/main은 마지막으로 push하거나 fetch했을 때의 GitHub main 위치예요. 그 뒤에 팀원이 올린 커밋은 git fetch origin을 쳐야 내 컴퓨터로 받아지고 Git Graph에 나타나요. 02에서 git log --oneline과 git log --oneline origin/main을 따로 쳐서 비교했던 걸 Git Graph는 한 화면에 보여 줘요.")

# =====================================================================================
# part 3: scenes. Same window geometry on every scene so magic move slides rows up.
# =====================================================================================
SC_L, SC_T, SC_W, SC_S = 96, 200, 1520, 1.5
TERM_L, TERM_W, TERM_BOTTOM = 1100, 724, 1044


def geo_rows_end(rows):
    s = SC_S
    return SC_T + 2 + round(48 * s) + round(44 * s) + len(rows) * round(48 * s)


def scene(sid, eyebrow, title, state, term, notes, hl, transition="magic", color=BL):
    """hl is a list of highlight specs (kind, args) in click order. The terminal sits at the bottom right,
    straddling the window's right edge, and hugs its lines."""
    o = [sec(sid, transition)] + head(eyebrow, title, color, size=50)
    g, geo = gg(ST[state], L=SC_L, T=SC_T, W=SC_W, s=SC_S, pre="")
    o += g
    th = term_h(len(term))
    tt = min(geo_rows_end(ST[state]) + 32, TERM_BOTTOM - th)
    tparts, _ = terminal(term, TERM_L, tt, TERM_W, tid=f"term-{sid}")
    o += tparts
    ys, ROW = geo["ys"], geo["ROW"]
    for item in hl:
        kind, order = item[0], item[1]
        if kind == "rows":
            a, b = item[2]
            y0, y1 = ys[a] - ROW // 2, ys[b] + ROW // 2
            o.append(spot(order, SC_L + 4, y0, SC_W - 8, y1 - y0, pad=2, r=8))
        elif kind == "off":
            o.append(spot_off(order))
        elif kind == "ring":
            x, y, w_, h_ = item[2]
            o.append(ring(order, x, y, w_, h_, item[3] if len(item) > 3 else OR))
        elif kind == "ringid":
            x, y, w_, h_ = rect(sid, item[2], (300, ys[0] - 25, 200, 50))
            o.append(ring(order, x, y, w_, h_, item[3] if len(item) > 3 else OR))
        elif kind == "zoom":
            a, b, wz = item[2]
            y0, y1 = ys[a] - ROW // 2 - 10, ys[b] + ROW // 2 + 10
            o.append(zoom(order, SC_L, y0, wz, y1 - y0, 30, 2.2))
        elif kind == "zoomoff":
            o.append(zoom_off(order))
        elif kind == "pulse":
            o.append(pulse(order, item[2]))
        elif kind == "uline":
            line_i, c0, c1 = item[2]
            o.append(underline(order, col_x(TERM_L, c0), col_x(TERM_L, c1), line_y(tt, line_i) + 2, item[3] if len(item) > 3 else OR))
    W(sid, o, notes)
    return geo


g1 = scene("sc1", "실습 1 · 파일을 고치면", "맨 위에 회색 빈 점이 생겨요", "sc1",
           [("$", 'echo "로그인 버튼" >> login.md'), ("$", "git status"), ("o", "On branch main"), ("o", "Changes not staged for commit:"), ("r", "\tmodified:   login.md")],
           "e12ffc2 커밋 하나를 GitHub에 올려 둔 상태에서 시작해요. login.md에 한 줄을 더하면 Git Graph 맨 위에 Uncommitted Changes 줄이 생겨요. 괄호 안 숫자는 아직 커밋하지 않은 파일 수예요. git status에 나오는 파일과 같아요. status의 안내 문구 줄은 화면 폭 때문에 그 부분은 빼고 옮겼어요.",
           [("ringid", 1, "unc", "#6A7180"), ("uline", 2, (4, 8, 26), RED)], transition="fade")
scene("sc2", "실습 2 · git commit", "새 점이 위에 생기고 main이 따라 올라가요", "sc2",
      [("$", "git add login.md"), ("$", 'git commit -m "feat: 로그인 버튼 추가"'), ("o", f"[main {h7('B')}] feat: 로그인 버튼 추가"), ("o", " 1 file changed, 1 insertion(+)")],
      "회색 줄이 사라지고 그 자리에 새 커밋 15d92cbb가 생겼어요. main 이름표가 새 커밋으로 올라갔어요. origin/main은 GitHub에 마지막으로 올린 e12ffc2e에 그대로 있어요. 내 컴퓨터가 커밋 하나 앞선 상태예요.",
      [("rows", 1, (0, 1)), ("off", 2)])
scene("sc3", "실습 3 · git push origin main", "origin이 main 옆에 붙어요", "sc3",
      [("$", "git push origin main"), ("o", "To https://github.com/kim/hello-git.git"), ("o", f"   {h7('A')}..{h7('B')}  main -> main")],
      "push하면 origin/main이 main과 같은 커밋으로 올라와서 main | origin 이름표 하나로 합쳐져요. 출력의 main -> main이 GitHub의 main을 옮겼다는 뜻이에요. push 출력의 진행 줄(Enumerating objects 등)은 화면 폭 때문에 그 부분은 빼고 옮겼어요.",
      [("uline", 1, (2, 21, 33), PUR), ("ringid", 2, "ref-B-0", PUR)])
scene("sc4", "실습 4 · git fetch origin", "팀원 커밋이 받아지고 origin/main이 main보다 위로 가요", "sc4",
      [("#", "# 팀원 lee가 GitHub에 push했어요"), ("$", "git fetch origin"), ("o", "From https://github.com/kim/hello-git"), ("o", f"   {h7('B')}..{h7('L')}  main       -> origin/main")],
      "팀원 lee가 GitHub에 커밋을 올렸어요. git fetch origin으로 받아 오면 lee의 커밋 b9f30e50이 맨 위에 생기고 origin/main 이름표가 붙어요. 작성자 칸에 lee가 보여요. 굵은 main은 아직 아래에 있어요. fetch는 기록만 받아 오고 내 파일은 바꾸지 않아서 내 폴더는 아직 예전 모습이에요.",
      [("zoom", 1, (0, 1, 1304)), ("zoomoff", 2)], color=GR)
scene("sc5", "실습 5 · git pull origin main", "main이 올라가서 origin과 다시 붙어요", "sc5",
      [("$", "git pull origin main"), ("o", "From https://github.com/kim/hello-git"), ("o", " * branch            main       -> FETCH_HEAD"), ("o", f"Updating {h7('B')}..{h7('L')}"), ("o", "Fast-forward"),
       ("o", " README.md | 1 +"), ("o", " 1 file changed, 1 insertion(+)")],
      "pull하면 main이 origin/main 자리로 올라가서 다시 main | origin 하나가 돼요. 갈라진 게 없어서 Fast-forward로 이름표만 옮겨졌고 선은 한 줄 그대로예요. 이제 내 폴더에 README.md가 생겨요. 출력의 create mode 줄은 화면 폭 때문에 그 부분은 빼고 옮겼어요.",
      [("uline", 1, (4, 0, 12), GR), ("pulse", 2, "ref-L-0")], color=GR)
scene("sc6", "실습 6 · git checkout -b feature/login", "같은 점에 이름표가 하나 더 붙어요", "sc6",
      [("$", "git checkout -b feature/login"), ("o", "Switched to a new branch 'feature/login'")],
      "브랜치를 만들면 지금 커밋에 feature/login 이름표가 하나 더 붙어요. 새 커밋은 아직 없어서 점은 그대로예요. 굵은 글씨가 main에서 feature/login으로 옮겨 갔어요. HEAD가 feature/login으로 옮겨 갔다는 뜻이에요.",
      [("ringid", 1, "ref-L-0", OR)], color=OR)
scene("sc7", "실습 7 · 브랜치에서 git commit", "feature/login만 위로 올라가요", "sc7",
      [("$", 'echo "비밀번호 찾기" >> login.md'), ("$", "git add login.md"), ("$", 'git commit -m "feat: 비밀번호 찾기 추가"'), ("o", f"[feature/login {h7('C')}] feat: 비밀번호 찾기 추가"), ("o", " 1 file changed, 1 insertion(+)")],
      "feature/login에서 커밋하면 feature/login 이름표만 새 커밋으로 올라가요. main | origin은 b9f30e50에 남아요. main 쪽에 새 커밋이 없어서 아직 선은 한 줄로 보여요. 03의 fast-forward 장면과 같은 모양이에요.",
      [("rows", 1, (0, 1)), ("off", 2)], color=OR)
g8 = gg(ST["sc8"], L=SC_L, T=SC_T, W=SC_W, s=SC_S)[1]
ys8 = g8["ys"]
scene("sc8", "실습 8 · main으로 돌아가 git commit", "길이 둘로 갈라져요", "sc8",
      [("$", "git checkout main"), ("o", "Switched to branch 'main'"), ("$", 'echo "실행 방법은 준비 중이에요" >> README.md'), ("$", "git add README.md"), ("$", 'git commit -m "docs: README에 실행 방법 추가"'), ("o", f"[main {h7('D')}] docs: README에 실행 방법 추가")],
      "main으로 돌아와 README.md를 고쳐 커밋했어요. 이제 두 브랜치가 b9f30e50에서 서로 다른 커밋을 가졌어요. Git Graph는 feature/login 쪽을 오른쪽 분홍 선으로 따로 그려요. 03에서 그린 갈라진 길 그림과 같아요. 굵은 글씨와 빈 점이 다시 main으로 왔어요.",
      [("ring", 1, (g8["gx"](0) - 20, ys8[0] - 16, g8["gx"](1) - g8["gx"](0) + 40, ys8[2] - ys8[0] + 32), OR)], color=OR)
g9 = gg(ST["sc9"], L=SC_L, T=SC_T, W=SC_W, s=SC_S)[1]
ys9 = g9["ys"]
scene("sc9", "실습 9 · git merge feature/login", "두 선이 merge 커밋에서 만나요", "sc9",
      [("$", "git merge feature/login"), ("#", "# vim이 열리면 Esc, :wq, Enter"), ("o", "Merge made by the 'ort' strategy."), ("o", " login.md | 1 +"), ("o", " 1 file changed, 1 insertion(+)")],
      "main에서 git merge feature/login을 치면 merge 커밋 5991c366이 생겨요. 이 점에서 아래로 선이 두 개 나가요. 하나는 main의 ad50d357, 하나는 feature/login의 dd7f15af예요. 03처럼 merge 메시지를 쓰는 vim이 열리면 Esc를 누른 뒤 :wq와 Enter를 쳐요.",
      [("zoom", 1, (0, 2, 900)), ("zoomoff", 2), ("ring", 2, (g9["gx"](0) - 22, ys9[0] - 22, g9["gx"](1) - g9["gx"](0) + 44, ys9[2] - ys9[0] + 34), BL)], color=BL)
scene("sc10", "실습 10 · 다시 git push origin main", "main | origin이 맨 위에 같이 있어요", "sc10",
      [("$", "git push origin main"), ("o", "To https://github.com/kim/hello-git.git"), ("o", f"   {h7('L')}..{h7('M')}  main -> main")],
      "push하면 origin/main이 merge 커밋으로 올라와서 다시 main | origin이 돼요. feature/login은 push하지 않아서 origin이 붙지 않아요. GitHub에도 merge 커밋까지 올라갔어요.",
      [("rows", 1, (0, 0)), ("off", 2)], color=PUR)

# detail: a clicked row opens its files
dl = [sec("detail")] + head("명령 치고 확인하기", "커밋 줄을 누르면 바뀐 파일이 보여요", GR)
EXP = 250
g, geo = gg(ST["sc10"], L=96, T=200, W=1728, s=1.15, cols=("author", "commit"), expand="C", expand_h=EXP, sel="C", pre="", win_h=900)
dl += g
ys = geo["ys"]
cy = ys[2] + geo["ROW"] // 2
dl.append(cursor(1, 900, ys[2]))
dl.append(f'<div{bi("rise", 2)} style="position:absolute;left:250px;top:{cy+6}px;width:1550px;height:{EXP-14}px;background:#252526;border:1px solid {VS["bd"]};border-radius:8px;display:flex;flex-direction:row">'
          + f'<div style="flex:1;padding:20px 26px;display:flex;flex-direction:column;gap:2px;border-right:1px solid {VS["bd"]}">'
          + "".join(p(f"font-size:22px;line-height:1.45;color:{VS['txt']};white-space:nowrap", f"<b>{k_}</b> {e(v_)}") for k_, v_ in [("Commit:", C["C"][0]), ("Parents:", C["L"][0]), ("Author:", "kim <kim@example.com>"), ("Date:", "Thu Oct 29 2026 10:04:00 GMT+0900")])
          + p(f"font-size:22px;line-height:1.6;color:{VS['txt']};margin-top:8px", "feat: 비밀번호 찾기 추가") + '</div>'
          + '<div style="width:440px;flex:none;padding:20px 26px;display:flex;flex-direction:column;gap:12px">'
          + p(f"font-size:24px;color:{VS['txt']}", "hello-git")
          + f'<div id="dl-file" style="display:flex;flex-direction:row;gap:10px;align-items:center;padding:4px 10px">'
          + p(f"font-size:24px;color:#E2C08D", "login.md") + p(f"font-size:24px;color:{VS['txt']}", '(<span style="color:#7FD18B">+1</span>|<span style="color:#F28B82">-0</span>)') + '</div></div></div>')
dl.append(cursor(3, target="dl-file"))
dl.append(label(1386, cy + 158, 400, "누르면 04에서 본<br>diff 화면이 열려요", 3, size=26, color="#E2C08D", weight=400, extra=DELAY(700)))
W("detail", dl, "커밋 줄 아무 데나 한 번 누르면 아래에 상세 정보가 펼쳐져요. 왼쪽은 커밋 번호 전체, 부모 커밋, 만든 사람, 날짜, 메시지예요. 오른쪽은 이 커밋에서 바뀐 파일과 더한 줄, 지운 줄 수예요. 파일 이름을 누르면 왼쪽에 예전, 오른쪽에 바뀐 내용이 나란히 보여요. 터미널의 git show와 같은 내용이에요. 다시 누르면 닫혀요. Committer 줄과 시간대 이름은 화면 폭 때문에 그 부분은 빼고 옮겼어요.")

# =====================================================================================
# part 4: care, trouble, real situations, summary
# =====================================================================================
ru = [sec("rule")] + head("쓸 때 주의", "checkout, merge, reset은 메뉴 말고 터미널에 쳐요", OR)
g, geo = gg(ST["sc10"], L=96, T=200, W=1180, s=1.25, cols=("commit",), pre="ru-", sel="C", win_h=900)
ru += g
ys = geo["ys"]
MENU = ["Add Tag...", "Create Branch...", "Checkout...", "Cherry Pick...", "Revert...", "Drop...", "Merge into current branch...", "Rebase current branch on this Commit...", "Reset current branch to this Commit...", "Copy Commit Hash to Clipboard"]
ru.append(cursor(1, 520, ys[2]))
MT = ys[2] + 18
ru.append(f'<div{bi("pop", 2)} style="position:absolute;left:560px;top:{MT}px;width:580px;background:#252526;border:1px solid #454545;border-radius:8px;padding:8px 0;display:flex;flex-direction:column;box-shadow:0 12px 32px rgba(0,0,0,.45)">'
          + "".join(p(f"font-size:24px;line-height:42px;padding:0 22px;color:{VS['txt']}", e(m)) for m in MENU) + '</div>')
ru.append(box(3, 566, MT + 8 + 6 * 42 - 2, 568, 3 * 42 + 4, RED))
ru.append(cursor_off(3))
ru.append(label(1340, 236, 484, "메뉴 한 번에 merge, reset이 실행돼요", 3, size=36))
ru.append(label(1340, 400, 484, "터미널에 남아야 오류가 났을 때 읽고 고칠 수 있어요.", 3, size=30, color=SUB, weight=400, extra=DELAY(250)))
ru.append(f'<div{STAGGER(4, 160)} style="position:absolute;left:1340px;top:620px;width:484px;display:flex;flex-direction:column;gap:18px">'
          + p(f"font-size:30px;font-weight:700;line-height:1.5;padding:14px 24px;border-radius:12px;color:#FFFFFF;background:{INK}", "명령은 터미널")
          + p(f"font-size:30px;font-weight:700;line-height:1.5;padding:14px 24px;border-radius:12px;color:#FFFFFF;background:{GR}", "확인은 Git Graph")
          + p(f"font-size:26px;line-height:1.5;color:{SUB};margin-top:10px", f'Fetch 버튼 대신 <span style="font-family:{MONO}">git fetch origin</span>') + '</div>')
W("rule", ru, "checkout, merge, reset은 Git Graph 메뉴 대신 터미널에 쳐요. 커밋 줄이나 이름표를 오른쪽 클릭하면 이런 메뉴가 나와요. 버튼 한 번에 reset이나 merge가 실행돼서 무엇이 바뀌었는지 놓치기 쉬워요. 그래서 수업에서는 명령을 터미널에 직접 치고, 친 결과가 맞는지 Git Graph로 확인하는 데만 써요. 잘못 눌렀다면 창을 닫지 말고 터미널에서 git status와 git log --oneline부터 봐요.")

tb = [sec("trouble")] + head("막힐 때", "Git Graph가 안 열리거나 그림이 그대로일 때", "#1E3F8F")
CASES = [("저장소가 없다고 나와요", "No Git repositories were found...", "저장소가 아닌 폴더를 열었어요", "File &gt; Open Folder로<br>hello-git 폴더 열기"),
         ("팀원이 올린 커밋이 안 보여요", None, "내 컴퓨터에 받아 둔 기록만 그려요", "git fetch origin"),
         ("명령을 쳤는데 그림이 그대로예요", None, "보통 저절로 바뀌어요", "오른쪽 위 새로고침 ↻")]
TY, TH = 236, 250
tb.append(p(f"position:absolute;left:96px;top:{TY}px;width:640px;font-size:26px;font-weight:700;color:{MUTE}", "증상"))
tb.append(p(f"position:absolute;left:760px;top:{TY}px;width:500px;font-size:26px;font-weight:700;color:{MUTE}", "왜"))
tb.append(p(f"position:absolute;left:1300px;top:{TY}px;width:524px;font-size:26px;font-weight:700;color:{MUTE}", "이렇게"))
for i, (sym, err, why_, fix) in enumerate(CASES):
    y = TY + 56 + i * TH
    mono_fix = fix.startswith("git ")
    tb.append(f'<div{bi("rise", i + 1)}{DIM("tb")} style="position:absolute;left:96px;top:{y}px;width:1728px;height:{TH}px;border-top:2px solid {HAIR};display:flex;flex-direction:row;align-items:center">'
              + '<div style="width:664px;flex:none;display:flex;flex-direction:column;gap:14px;padding-right:24px">' + p(f"font-size:38px;font-weight:700;line-height:1.35;color:{INK}", sym)
              + (p(f"align-self:flex-start;font-family:{MONO};font-size:24px;color:#F28B82;background:#1F1F1F;padding:8px 16px;border-radius:8px", e(err), ' id="tb-err"') if err else "") + '</div>'
              + p(f"width:540px;flex:none;font-size:30px;line-height:1.45;color:{SUB};padding-right:24px", why_)
              + p(f"flex:1;font-size:30px;font-weight:700;line-height:1.45;color:{INK}" + (f";font-family:{MONO}" if mono_fix else ""), fix) + '</div>')
tb.append(shake(1, "tb-err"))
tb.append(f'<div style="position:absolute;left:96px;top:{TY + 56 + 3 * TH}px;width:1728px;height:2px;background:{HAIR}"></div>')
W("trouble", tb, "가장 흔한 건 1번이에요. 바탕화면이나 상위 폴더를 열면 Git 저장소를 못 찾아요. git init을 한 바로 그 폴더를 열어요. 2번은 큰 그림에서 본 대로 Git Graph가 GitHub에 직접 묻지 않기 때문이에요. 3번의 새로고침은 Git Graph 탭 오른쪽 위 둥근 화살표 아이콘이에요.")

# case 1: read the picture, pick the command
c1 = [sec("case1")] + head("실제 상황 1", "그림만 보고 다음에 칠 명령을 골라요", BL)
SIT = [("내가 커밋하고 아직 안 올렸어요", [R("B", 0, [MAIN], True), R("A", 0, [OM])], "git push origin main", BL),
       ("팀원 커밋을 fetch로 받아 왔어요", [R("L", 0, [OM]), R("B", 0, [MAIN], True)], "git pull origin main", GR),
       ("둘이 붙어 있어요", [R("B", 0, [MAIN_O], True), R("A")], "할 일 없음", "#3A4150")]
for i, (q, rows, cmd, col) in enumerate(SIT):
    x = 96 + i * 592
    g, _ = gg(rows, L=x, T=240, W=544, s=1.5, tab=False, hdr=False, cols=(), pre=f"c{i}-", win_h=196, pad_top=26, shadow=False, bars=True)
    c1 += g
    c1.append(label(x, 470, 544, q, size=32, color=INK))
    c1.append(p(f"position:absolute;left:{x}px;top:570px;width:544px;font-family:{MONO};font-size:28px;font-weight:700;line-height:1.7;text-align:center;border-radius:12px;color:#FFFFFF;background:{col}", cmd, bi("rise", i + 1)))
c1.append(f'<div style="position:absolute;left:96px;top:720px;width:1728px;height:2px;background:{HAIR}"></div>')
c1.append(label(96, 770, 1728, "위에 있는 쪽이 앞서요. main이 위면 push, origin/main이 위면 pull이에요.", 4, size=34))
c1.append(label(96, 850, 1728, extra=DELAY(300), text="origin/main이 안 움직였는데 팀원이 올렸다고 하면, 먼저 git fetch origin을 쳐서 그림을 새로 받아요.", order=4, size=30, color=SUB, weight=400))
W("case1", c1, "main과 origin/main 중 위에 있는 쪽이 앞선 쪽이에요. 학생에게 먼저 그림만 보여 주고 무엇을 칠지 말하게 한 뒤 한 칸씩 답을 보여 주세요. main이 origin/main보다 위에 있으면 내 컴퓨터가 앞선 거라 push해요. origin/main이 위에 있으면 GitHub이 앞선 거라 pull해요. 둘이 붙어 있으면 할 일이 없어요.")

# case 2: delete the finished branch, only the label goes
c2 = [sec("case2", "magic")] + head("실제 상황 2", "다 쓴 브랜치를 지우면 이름표만 사라져요", OR)
g, geo = gg(ST["sc10"], L=SC_L, T=SC_T, W=SC_W, s=SC_S, pre="", row_attrs={})
ys = geo["ys"]
c2 += [x for x in g if 'id="r-C"' not in x]
# row C twice: with its label (leaves on click 1) and without (arrives on click 1)
gC, _ = gg(ST["sc10"], L=SC_L, T=SC_T, W=SC_W, s=SC_S, pre="k-")
gD, _ = gg(ST["del"], L=SC_L, T=SC_T, W=SC_W, s=SC_S, pre="n-")
rowC_old = [x for x in gC if 'id="k-r-C"' in x][0]
rowC_new = [x for x in gD if 'id="n-r-C"' in x][0].replace(' style="', bi("fade", 2) + f' style="background:{VS["bg"]};', 1)
c2 += [rowC_old, rowC_new]
d_lines = [("$", "git branch -d feature/login"), ("o", f"Deleted branch feature/login (was {h7('C')}).")]
c2term, c2h = terminal(d_lines, TERM_L, geo_rows_end(ST["del"]) + 32, TERM_W, tid="term-case2", attrs=bi("rise", 1))
c2 += c2term
c2.append(ring(3, geo["gx"](1) - 30, ys[2] - 30, 60, 60, OR))
gx1 = geo["gx"](1)
c2.append(leader(3, [(gx1, ys[-1] + 90), (gx1, ys[2] + 36)], OR))
c2.append(label(gx1 - 30, ys[-1] + 100, 900, "점과 선은 그대로 남아요.<br>main의 기록에 이미 들어가 있어서예요.", 3, size=32, color=VS["txt"], extra=DELAY(250)))
W("case2", c2, "merge하고 push까지 끝났으면 feature/login 이름표는 더 쓸 일이 없어요. 03에서 배운 git branch -d feature/login으로 지워요. Git Graph에서 이름표만 사라지고 분홍 점과 선은 그대로 있어요. 커밋은 merge 커밋을 통해 main의 기록에 들어가 있기 때문이에요. 이름표는 커밋을 가리키는 표시일 뿐이라는 걸 다시 확인할 수 있어요.")

# summary: when to look where
sm = [sec("summary")] + head("정리", "명령을 칠 때마다 Git Graph에서 한 곳씩 봐요", BL)
ROWS = [("커밋했는지", "맨 위 회색 줄이 사라지고 새 점", "git commit"),
        ("GitHub에 올렸는지", "main | origin으로 붙었는지", "git push origin main"),
        ("팀원이 올린 게 있는지", "origin/main이 main보다 위", "git fetch origin"),
        ("지금 어느 브랜치인지", "굵은 글씨, 색 테두리 이름표", "git checkout 브랜치"),
        ("합쳐졌는지", "두 선이 만나는 점", "git merge 브랜치"),
        ("무엇이 바뀌었는지", "커밋 줄을 눌러 파일 목록", "git show")]
SY, SH = 226, 100
for j, (hname, x, w_) in enumerate([("확인할 것", 96, 520), ("Git Graph에서 볼 곳", 636, 640), ("관련 명령", 1296, 528)]):
    sm.append(p(f"position:absolute;left:{x}px;top:{SY}px;width:{w_}px;font-size:26px;font-weight:700;color:{MUTE}", hname))
for i, (a, b, c) in enumerate(ROWS):
    y = SY + 50 + i * SH
    sm.append(f'<div data-build-in="rise order 1"{DELAY(i * 90)} style="position:absolute;left:96px;top:{y}px;width:1728px;height:{SH}px;border-top:2px solid {HAIR};display:flex;flex-direction:row;align-items:center">'
              + p(f"width:540px;flex:none;font-size:32px;font-weight:700;color:{INK}", a) + p(f"width:660px;flex:none;font-size:30px;color:{SUB}", b)
              + p(f"flex:1;font-family:{MONO};font-size:28px;font-weight:700;color:{INK}", c) + '</div>')
sm.append(f'<div style="position:absolute;left:96px;top:{SY + 50 + 6 * SH}px;width:1728px;height:2px;background:{HAIR}"></div>')
sm.append(label(96, 940, 1728, "다음 06에서는 kim, lee, park이 팀 레포에서 같이 작업해요. 서로 올린 커밋을 Git Graph로 확인하면서 충돌을 풀어요.", size=30, color=SUB, weight=400))
W("summary", sm, "수업 끝에 이 장을 띄워 두고 학생에게 commit, push, checkout, merge 뒤에 Git Graph에서 무엇이 바뀌는지 말로 설명해 보게 하세요. 06에서는 세 사람이 같은 레포에 push하니까 origin/main이 자주 움직여요. 그때 이 표의 세 번째 줄이 가장 많이 쓰여요.")
print("ok")
