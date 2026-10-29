"""Generates every slide of the Git Graph deck.

The Git Graph screen is redrawn from the extension's own source (mhutchie/vscode-git-graph):
labels with a branch icon, the checked-out branch in bold with a coloured border, a hollow dot on
the HEAD commit, "Uncommitted Changes (n)" as a grey hollow dot, 8-character hashes, default lane
colours #0085D9 and #D9008F. Terminal output and hashes come from tools/demo.sh (git 2.43).
Usage: python3 tools/gen.py slides
"""
import html, os, sys

OUT = sys.argv[1]
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
INK, SUB, LINE = "#1D2330", "#4A5262", "#E1DED6"
BL, GR, OR, RED, PUR = "#2459C9", "#1F8A4C", "#B26A00", "#A33131", "#5A3BB8"
VS = dict(bg="#1F1F1F", bar="#181818", txt="#CCCCCC", dim="#9D9D9D", bd="#3C3C3C", sel="#2A2D2E", input="#313131", blue="#0078D4")
LANE_C = ["#0085D9", "#D9008F"]
GRAY = "#808080"


def e(s):
    return html.escape(s, quote=False)


def p(style, text, attrs=""):
    return f'<p{attrs} style="{style}">{text}</p>'


def W(name, parts, notes):
    body = "\n".join(parts) + f"\n<aside>{e(notes)}</aside>\n</section>\n"
    open(os.path.join(OUT, name + ".html"), "w").write(body)


def sec(i, transition="fade", bg="#F6F5F1"):
    return f'<section id="{i}" data-transition="{transition}" style="background:{bg};color:{INK};font-family:{SANS};padding:96px;display:flex;flex-direction:column">'


def head(eyebrow, title, color=BL):
    return [p(f"position:absolute;left:96px;top:56px;width:1728px;font-size:26px;font-weight:700;color:{color}", e(eyebrow), ' id="eyebrow"'),
            f'<h2 id="title" style="position:absolute;left:96px;top:100px;width:1728px;font-size:56px;font-weight:700;line-height:1.2;color:{INK}">{title}</h2>']


# ---------- terminal ----------
TC = {"$": "#F2C46D", "o": "#D8DEE9", "#": "#8C95A6", "g": "#7FD18B", "r": "#F28B82"}


def terminal(lines, left=96, top=656, w=1150, h=368, size=24, lh=1.3, tid="term"):
    o = [f'<div id="{tid}" style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:#1B2029;border-radius:20px;padding:20px 28px;display:flex;flex-direction:column;font-family:{MONO};font-variant-ligatures:none">']
    for kind, text in lines:
        t = e(text).replace("\t", "        ")
        if kind == "$":
            t = "$ " + t
        bold = "font-weight:700;" if kind == "$" else ""
        o.append(p(f"font-size:{size}px;line-height:{lh};white-space:pre;{bold}color:{TC[kind]}", t if t else " "))
    o.append('</div>')
    return o


def callout(icon, title, sub=None, icolor=BL, top=656, h=368):
    o = [f'<div id="explain" data-build-in="rise" style="position:absolute;left:1278px;top:{top}px;width:546px;height:{h}px;background:#FFFFFF;border:2px solid {LINE};border-radius:20px;padding:32px;display:flex;flex-direction:column;justify-content:center;gap:16px">']
    o.append(f'<x-icon name="{icon}" style="width:56px;height:56px;color:{icolor}"></x-icon>')
    o.append(p(f"font-size:34px;font-weight:700;line-height:1.35;color:{INK}", title))
    if sub:
        o.append(p(f"font-size:26px;line-height:1.45;color:{SUB}", sub))
    o.append('</div>')
    return o


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


# A row is (key, lane, refs, is_head). A ref is (name, lane, active, with_origin).
# "U" is the Uncommitted Changes row.
def R(k, lane=0, refs=(), head=False):
    return (k, lane, list(refs), head)


MAIN = ("main", 0, True, False)
MAIN_O = ("main", 0, True, True)
MAIN_O_OFF = ("main", 0, False, True)
MAIN_OFF = ("main", 0, False, False)
OM = ("origin/main", 0, False, False)
FL = ("feature/login", 0, True, False)
FL_OFF = ("feature/login", 1, False, False)

ST = {
    "a0": [R("A", 0, [MAIN_O], True)],
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
}


def branch_svg(color, size):
    return (f'<svg viewBox="0 0 24 24" style="width:{size}px;height:{size}px;display:block" fill="none" stroke="{color}" stroke-width="3" stroke-linecap="round">'
            '<line x1="6" y1="3" x2="6" y2="15"/><circle cx="18" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M18 9a9 9 0 0 1-9 9"/></svg>')


def ref_html(ref, s):
    name, lane, active, origin = ref
    col = LANE_C[lane]
    bd = col if active else "rgba(128,128,128,0.75)"
    o = (f'<div style="display:flex;flex-direction:row;align-items:center;height:{round(38*s)}px;flex:none;border:{max(2, round(2*s))}px solid {bd};border-radius:{round(9*s)}px;background:rgba(128,128,128,0.15);overflow:hidden">'
         f'<div style="width:{round(30*s)}px;height:100%;flex:none;background:{col};display:flex;align-items:center;justify-content:center">{branch_svg(VS["bg"], round(20*s))}</div>'
         + p(f"padding:0 {round(10*s)}px;font-size:{round(21*s)}px;line-height:{round(30*s)}px;font-weight:{700 if active else 400};color:{VS['txt']}", e(name)))
    if origin:
        o += p(f"padding:0 {round(10*s)}px;font-size:{round(21*s)}px;line-height:{round(30*s)}px;font-style:italic;color:{VS['txt']};border-left:2px solid rgba(128,128,128,0.45)", "origin")
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


def gg(rows, L=96, T=184, W=1728, s=1.0, tab=True, ctl=True, hdr=True, full=True, nrows=6, pre="", expand=None, expand_h=0, sel=None, win_h=None, pad_top=0, commit=True):
    """Draws the Git Graph tab. Every row, dot and line has its own id so magic move can slide them."""
    TAB = round(48 * s) if tab else 0
    CTL = round(56 * s) if ctl else 0
    HDR = round(44 * s) if hdr else 0
    ROW = round(48 * s)
    LANE = round(40 * s)
    GW = round(130 * s)
    RD = round(9 * s)
    LW = max(3, round(4 * s))
    top0 = T + TAB + CTL + HDR + pad_top
    gx = lambda lane: L + round(34 * s) + lane * LANE
    ys, y = [], top0 + ROW // 2
    for k, *_ in rows:
        ys.append(y)
        y += ROW + (expand_h if k == expand else 0)
    H = win_h or (TAB + CTL + HDR + pad_top + nrows * ROW + expand_h + round(14 * s))
    o = [f'<div id="{pre}gg-win" style="position:absolute;left:{L}px;top:{T}px;width:{W}px;height:{H}px;background:{VS["bg"]};border:2px solid {VS["bd"]};border-radius:{round(16*s)}px;overflow:hidden"></div>']
    if tab:
        o.append(f'<div id="{pre}gg-tab" style="position:absolute;left:{L+2}px;top:{T+2}px;width:{W-4}px;height:{TAB}px;background:{VS["bar"]};border-radius:{round(14*s)}px {round(14*s)}px 0 0;display:flex;flex-direction:row">'
                 f'<div style="height:100%;padding:0 {round(22*s)}px;background:{VS["bg"]};border-top:3px solid {VS["blue"]};display:flex;flex-direction:row;gap:{round(12*s)}px;align-items:center">'
                 + graph_icon(round(22 * s))
                 + p(f"font-size:{round(22*s)}px;color:#FFFFFF", "Git Graph") + p(f"font-size:{round(22*s)}px;color:{VS['dim']}", "×") + '</div></div>')
    if ctl:
        cy = T + TAB + 2
        dd = lambda t: (f'<div style="height:{round(38*s)}px;padding:0 {round(12*s)}px;background:{VS["input"]};border:1px solid {VS["bd"]};border-radius:{round(5*s)}px;display:flex;flex-direction:row;gap:{round(10*s)}px;align-items:center">'
                        + p(f"font-size:{round(21*s)}px;color:{VS['txt']}", t) + p(f"font-size:{round(16*s)}px;color:{VS['dim']}", "▼") + '</div>')
        lab = lambda t: p(f"font-size:{round(21*s)}px;color:{VS['txt']}", t)
        o.append(f'<div id="{pre}gg-ctl" style="position:absolute;left:{L+round(20*s)}px;top:{cy}px;width:{W-round(40*s)}px;height:{CTL}px;display:flex;flex-direction:row;gap:{round(14*s)}px;align-items:center">'
                 + lab("Repo:") + dd("hello-git") + f'<div style="width:{round(14*s)}px"></div>' + lab("Branches:") + dd("Show All") + f'<div style="width:{round(14*s)}px"></div>'
                 + f'<div style="width:{round(24*s)}px;height:{round(24*s)}px;border:2px solid {VS["txt"]};border-radius:4px;display:flex;align-items:center;justify-content:center;font-size:{round(18*s)}px;line-height:1;color:{VS["txt"]}">✓</div>'
                 + lab("Show Remote Branches") + '<div style="flex:1"></div>'
                 + "".join(ui_icon(n, VS["txt"], round(26 * s), f' id="{pre}ic-{n}"' if n == "refresh" else "") + f'<div style="width:{round(6*s)}px"></div>' for n in ["search", "terminal", "gear", "fetch", "refresh"])
                 + '</div>')
    colw = [round(260 * s), round(110 * s), round(150 * s)] if full else [0, 0, round(150 * s)]
    if hdr:
        hy = T + TAB + CTL + 2
        cells = p(f"width:{GW-round(20*s)}px;flex:none;font-size:{round(21*s)}px;font-weight:700;color:{VS['txt']}", "Graph") + p(f"flex:1;font-size:{round(21*s)}px;font-weight:700;color:{VS['txt']}", "Description")
        if full:
            cells += p(f"width:{colw[0]}px;flex:none;font-size:{round(21*s)}px;font-weight:700;color:{VS['txt']}", "Date") + p(f"width:{colw[1]}px;flex:none;font-size:{round(21*s)}px;font-weight:700;color:{VS['txt']}", "Author")
        cells += p(f"width:{colw[2]}px;flex:none;font-size:{round(21*s)}px;font-weight:700;color:{VS['txt']}", "Commit")
        o.append(f'<div id="{pre}gg-hdr" style="position:absolute;left:{L+round(20*s)}px;top:{hy}px;width:{W-round(40*s)}px;height:{HDR}px;display:flex;flex-direction:row;align-items:center;border-bottom:1px solid {VS["bd"]}">{cells}</div>')
    idx = {k: i for i, (k, *_) in enumerate(rows)}
    has_unc = rows[0][0] == "U"
    # selected row background
    if sel in idx:
        i = idx[sel]
        o.append(f'<div id="{pre}sel" style="position:absolute;left:{L+2}px;top:{ys[i]-ROW//2}px;width:{W-4}px;height:{ROW+expand_h}px;background:{VS["sel"]}"></div>')
    # lines
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
                d = [f"M{x1},{y1} L{x2},{y2}"]
            elif lp > lane:
                yb = ys[i + 1]
                d = [f"M{x1},{y1} C{x1},{y1 + (yb-y1)*0.6} {x2},{y1 + (yb-y1)*0.4} {x2},{yb} L{x2},{y2}"]
            else:
                ya = ys[j - 1]
                d = [f"M{x1},{y1} L{x1},{ya} C{x1},{ya + (y2-ya)*0.6} {x2},{ya + (y2-ya)*0.4} {x2},{y2}"]
            mx, Mx, my, My = min(x1, x2) - LW, max(x1, x2) + LW, min(y1, y2), max(y1, y2)
            o.append(f'<svg id="{pre}e-{k}-{par}" viewBox="{mx} {my} {Mx-mx} {My-my}" style="position:absolute;left:{mx}px;top:{my}px;width:{Mx-mx}px;height:{My-my}px;overflow:visible">'
                     f'<path d="{d[0]}" fill="none" stroke="{col}" stroke-width="{LW}"/></svg>')
    # dots
    for i, (k, lane, refs, hd) in enumerate(rows):
        col = GRAY if k == "U" else LANE_C[lane]
        hollow = k == "U" or (hd and not has_unc)
        st = f"background:{VS['bg']};border:{LW}px solid {col}" if hollow else f"background:{col};border:{LW}px solid {col}"
        o.append(f'<div id="{pre}d-{k}" style="position:absolute;left:{gx(lane)-RD}px;top:{ys[i]-RD}px;width:{2*RD}px;height:{2*RD}px;border-radius:50%;{st}"></div>')
    # row text
    for i, (k, lane, refs, hd) in enumerate(rows):
        fs = round(23 * s)
        if k == "U":
            desc = p(f"font-size:{fs}px;font-weight:700;color:{VS['txt']};white-space:nowrap", f"Uncommitted Changes ({UNC_N})")
            date, author, cm = "29 Oct 2026 10:02", "*", "*"
        else:
            full_h, msg, tm, au, _ = C[k]
            dot = f'<div style="width:{round(14*s)}px;height:{round(14*s)}px;flex:none;border:{max(2, round(3*s))}px solid {LANE_C[lane]};border-radius:50%"></div>' if hd else ""
            desc = dot + "".join(ref_html(r, s) for r in refs) + p(f"min-width:0;font-size:{fs}px;color:{VS['txt']};white-space:nowrap;overflow:hidden;text-overflow:ellipsis", e(msg))
            date, author, cm = f"29 Oct 2026 {tm}", au, h8(k)
        cells = f'<div style="flex:1;min-width:0;display:flex;flex-direction:row;gap:{round(10*s)}px;align-items:center;overflow:hidden;padding-right:{round(16*s)}px">{desc}</div>'
        if full:
            cells += p(f"width:{colw[0]}px;flex:none;font-size:{fs}px;color:{VS['txt']}", date) + p(f"width:{colw[1]}px;flex:none;font-size:{fs}px;color:{VS['txt']}", author)
        if commit:
            cells += p(f"width:{colw[2]}px;flex:none;font-size:{fs}px;color:{VS['txt']}", cm)
        o.append(f'<div id="{pre}r-{k}" style="position:absolute;left:{L+GW}px;top:{ys[i]-ROW//2}px;width:{W-GW-round(20*s)}px;height:{ROW}px;display:flex;flex-direction:row;align-items:center">{cells}</div>')
    return o, ys


UNC_N = 1


def graph_icon(size, color="#C5C5C5"):
    return (f'<svg viewBox="0 0 16 16" style="width:{size}px;height:{size}px;display:block;flex:none">'
            f'<path fill="{color}" d="M2.6 1h1.5v14H2.6z"/><path fill="{color}" d="M7.3 5h1.4v10H7.3z"/>'
            f'<circle fill="{color}" cx="3.3" cy="8" r="1.9"/><circle fill="{color}" cx="8" cy="2.8" r="1.9"/><circle fill="{color}" cx="12.7" cy="13.2" r="1.9"/>'
            f'<path stroke="{color}" stroke-width="1.4" fill="none" d="M3.3 9.6c2 1.6 6 1 9.4 3.6"/></svg>')


def frame(sid, eyebrow, cmd, transition="magic", cmd_size=50, color=BL):
    return [sec(sid, transition),
            p(f"position:absolute;left:96px;top:40px;width:1728px;font-size:24px;font-weight:700;color:{color}", e(eyebrow), ' id="eyebrow"'),
            f'<h2 id="cmd" style="position:absolute;left:96px;top:84px;width:1728px;font-family:{MONO};font-size:{cmd_size}px;font-weight:700;line-height:1.15;color:{INK}">{cmd}</h2>']


def scene(sid, eyebrow, cmd, state, term, call, notes, transition="magic", cmd_size=50):
    o = frame(sid, eyebrow, cmd, transition, cmd_size)
    g, _ = gg(ST[state])
    o += g
    o += terminal(term)
    o += callout(*call)
    W(sid, o, notes)


# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:#1D2330;color:#F6F5F1;font-family:{SANS};padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#8FB3FF;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
       '<h1 style="font-size:104px;font-weight:900;line-height:1.1;color:#F6F5F1">Git Graph,<br>눈으로 보기</h1>',
       '<p style="font-size:40px;line-height:1.4;color:#BFC6D4">VS Code에서 커밋과 브랜치를<br>그림으로 확인하는 법</p>']
g, _ = gg(ST["sc10"], L=984, T=300, W=840, s=1.0, tab=True, ctl=False, hdr=False, full=False, pre="cv-", pad_top=16)
cov += g
W("cover", cov, "VS Code에 Git Graph 확장을 설치해서 지금까지 터미널로 만든 커밋과 브랜치를 그림으로 봐요. 명령은 지금처럼 터미널에서 치고, 친 결과를 Git Graph로 확인하는 게 오늘의 목표예요.")

# ---------- toc ----------
parts = [("Settings", "#3A4150", "설치하고 열기", "확장 설치, Git Graph 여는 세 가지 방법", "4–5쪽"),
         ("Search", BL, "화면 읽기", "점, 이름표, HEAD, origin/main", "6–9쪽"),
         ("Code", GR, "명령 치고 확인하기", "commit, push, fetch, pull, checkout, merge 뒤의 그림", "10–20쪽"),
         ("Wrench", OR, "쓸 때 주의, 막힐 때", "명령은 터미널에서, 안 보일 때", "21–22쪽")]
t = [f'<section id="toc" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};padding:96px 128px;display:flex;flex-direction:column;gap:40px">',
     f'<h2 style="font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>',
     '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:24px;flex:1">']
for i, (ic, c, h, s_, pg) in enumerate(parts, 1):
    t.append(f'<div style="display:flex;flex-direction:column;gap:12px;background:#FFFFFF;border:2px solid {LINE};border-top:10px solid {c};border-radius:20px;padding:28px 32px">'
             f'<div style="display:flex;flex-direction:row;gap:14px;align-items:center"><p style="font-size:56px;font-weight:900;line-height:1.25;color:{c}">{i}</p>'
             f'<x-icon name="{ic}" style="width:44px;height:44px;color:{c}"></x-icon></div>'
             f'<h3 style="font-size:36px;font-weight:700;color:{INK}">{h}</h3>'
             f'<p style="font-size:28px;line-height:1.45;color:{SUB}">{s_}</p><div style="flex:1"></div>'
             f'<p style="font-size:24px;color:#6A7180">{pg}</p></div>')
t += ['</div>', f'<p style="font-size:26px;color:{SUB}">마지막 23쪽은 한 장 요약이에요.</p>']
W("toc", t, "1부에서 설치하고 2부에서 화면 읽는 법을 익혀요. 3부가 오늘의 중심이에요. 02, 03에서 배운 명령을 하나씩 치고 Git Graph에서 무엇이 바뀌는지 봐요.")

# ---------- why ----------
w = [sec("why")] + head("Git Graph란?", "git log --oneline을 그림으로 보여 줘요")
LOG = [("$", "git log --oneline"), ("o", f"{h7('M')} (HEAD -> main, origin/main) Merge branch 'feature/login'"), ("o", f"{h7('D')} docs: README에 실행 방법 추가"),
       ("o", f"{h7('C')} (feature/login) feat: 비밀번호 찾기 추가"), ("o", f"{h7('L')} docs: README 추가"), ("o", f"{h7('B')} feat: 로그인 버튼 추가"), ("o", f"{h7('A')} feat: 로그인 화면 추가")]
w += terminal(LOG, left=96, top=232, w=1728, h=272, size=23, lh=1.3)
g, _ = gg(ST["sc10"], T=540, tab=False, ctl=False, hdr=True, pre="w-")
w += [x.replace(' style=', ' data-build-in="rise order 1" style=', 1) for x in g]
w.append(p(f"position:absolute;left:96px;top:968px;width:1728px;font-size:30px;font-weight:700;color:{INK}", "같은 기록이에요. 갈라진 길과 합쳐진 곳이 선으로 보여요.", ' data-build-in="fade order 2"'))
W("why", w, "위는 터미널에서 친 git log --oneline, 아래는 같은 저장소를 Git Graph로 연 화면이에요. 커밋 순서와 메시지가 같아요. 터미널에서는 feature/login에서 갈라졌다가 merge로 합쳐진 모양이 안 보이지만, Git Graph에서는 분홍 선으로 바로 보여요. Git Graph는 기록을 보여 주기만 해요. 저장소를 바꾸지 않아요.")

# ---------- part 1: install ----------
def vscode_shell(L, T, Wd, Hd, active="ext", panel_title="EXTENSIONS", status=False, pre=""):
    o = [f'<div id="{pre}vs-win" style="position:absolute;left:{L}px;top:{T}px;width:{Wd}px;height:{Hd}px;background:{VS["bg"]};border:2px solid {VS["bd"]};border-radius:16px;overflow:hidden"></div>',
         f'<div id="{pre}vs-act" style="position:absolute;left:{L+2}px;top:{T+2}px;width:76px;height:{Hd-4 - (40 if status else 0)}px;background:{VS["bar"]};border-radius:14px 0 0 0;display:flex;flex-direction:column;align-items:center;gap:30px;padding-top:28px">']
    for n in ["files", "search", "scm", "run", "ext"]:
        col = "#FFFFFF" if n == active else "#858585"
        bar = f'border-left:4px solid {VS["blue"]};' if n == active else 'border-left:4px solid transparent;'
        o[-1] += f'<div style="width:76px;height:44px;display:flex;align-items:center;justify-content:center;{bar}">{act_icon(n, col)}</div>'
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
    return f'<svg viewBox="0 0 24 24" style="width:36px;height:36px;display:block" fill="none" stroke="{col}" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round">{paths[n]}</svg>'


def marker(n, x, y, order, color=OR, mid=None):
    return f'<p{mid or ""} data-build-in="pop order {order}" style="position:absolute;left:{x}px;top:{y}px;width:52px;height:52px;font-size:30px;font-weight:900;line-height:52px;text-align:center;color:#FFFFFF;background:{color};border-radius:26px;box-shadow:0 0 0 4px #F6F5F1">{n}</p>'


def steps_card(L, T, Wd, Hd, items, title=None, foot=None):
    o = f'<div data-build-in="rise order 1" style="position:absolute;left:{L}px;top:{T}px;width:{Wd}px;height:{Hd}px;background:#FFFFFF;border:2px solid {LINE};border-radius:20px;padding:36px 36px;display:flex;flex-direction:column;gap:26px">'
    if title:
        o += p(f"font-size:32px;font-weight:700;color:{INK}", title)
    for n, (main_, sub_) in enumerate(items, 1):
        o += (f'<div style="display:flex;flex-direction:row;gap:18px;align-items:flex-start">'
              + p(f"width:48px;height:48px;flex:none;font-size:26px;font-weight:900;line-height:48px;text-align:center;color:#FFFFFF;background:{OR};border-radius:24px", str(n))
              + f'<div style="display:flex;flex-direction:column;gap:6px">' + p(f"font-size:28px;font-weight:700;line-height:1.4;color:{INK}", main_)
              + (p(f"font-size:24px;line-height:1.45;color:{SUB}", sub_) if sub_ else "") + '</div></div>')
    if foot:
        o += '<div style="flex:1"></div>' + p(f"font-size:24px;line-height:1.45;color:{SUB}", foot)
    return o + '</div>'


ins = [sec("install")] + head("설치하고 열기", "확장 탭에서 Git Graph를 찾아 설치해요", "#3A4150")
VL, VT, VW, VH = 96, 236, 1040, 740
ins += vscode_shell(VL, VT, VW, VH, active="ext")
PX = VL + 80
ins.append(f'<div style="position:absolute;left:{PX}px;top:{VT+2}px;width:{VW-82}px;height:{VH-4}px;background:{VS["bar"]};padding:24px 28px;display:flex;flex-direction:column;gap:20px">'
           + p(f"font-size:22px;font-weight:700;color:{VS['txt']};letter-spacing:1px", "EXTENSIONS: MARKETPLACE")
           + f'<div style="height:52px;background:{VS["input"]};border:2px solid {VS["blue"]};border-radius:6px;padding:0 16px;display:flex;align-items:center">' + p(f"font-size:26px;color:#FFFFFF", "git graph") + '</div>'
           + f'<div style="background:#04395E;border-radius:6px;padding:20px 20px;display:flex;flex-direction:row;gap:20px">'
           + f'<div style="width:96px;height:96px;flex:none;background:#2B2B2B;border-radius:8px;display:flex;align-items:center;justify-content:center">{graph_icon(64)}</div>'
           + '<div style="flex:1;display:flex;flex-direction:column;gap:6px">'
           + p(f"font-size:28px;font-weight:700;color:#FFFFFF", "Git Graph")
           + p(f"font-size:22px;line-height:1.4;color:{VS['txt']}", "View a Git Graph of your repository, and perform Git actions from the graph.")
           + '<div style="display:flex;flex-direction:row;align-items:center;justify-content:space-between;margin-top:6px">'
           + p(f"font-size:22px;font-weight:700;color:{VS['txt']}", "mhutchie")
           + p(f"font-size:22px;color:#FFFFFF;background:{VS['blue']};padding:2px 18px;border-radius:4px", "Install") + '</div></div></div>'
           + f'<div style="background:{VS["bar"]};border-radius:6px;padding:16px 20px;display:flex;flex-direction:row;gap:20px;opacity:0.5">'
           + '<div style="width:96px;height:72px;flex:none;background:#2B2B2B;border-radius:8px"></div>'
           + '<div style="flex:1;display:flex;flex-direction:column;gap:6px">' + p(f"font-size:24px;font-weight:700;color:{VS['txt']}", "이름이 비슷한 다른 확장") + p(f"font-size:22px;color:{VS['dim']}", "만든 사람이 다르면 설치하지 않아요") + '</div></div>'
           + '</div>')
ins.append(marker(1, VL + 12, VT + 4 * 74 + 18, 2))
ins.append(marker(2, PX + VW - 82 - 70, VT + 66, 3))
ins.append(marker(3, PX + VW - 82 - 70, VT + 250, 4))
ins.append(steps_card(1176, 236, 648, 740, [("왼쪽 막대의 확장 아이콘을 눌러요", "Windows Ctrl+Shift+X<br>Mac Cmd+Shift+X"),
                                            ("검색창에 git graph를 쳐요", None),
                                            ("만든 사람이 mhutchie인지 보고 Install을 눌러요", "설치는 한 번만 하면 돼요")],
                       foot="설치가 끝나면 Install 버튼 자리가 톱니바퀴로 바뀌어요."))
W("install", ins, "VS Code 왼쪽 세로 막대에서 네모 네 개 모양 아이콘이 확장(Extensions)이에요. 검색 결과에 비슷한 이름이 여러 개 나와요. 오늘 쓰는 건 mhutchie가 만든 Git Graph예요. 설치하고 VS Code를 다시 켤 필요는 없어요. 화면이 한국어로 되어 있으면 Install 대신 설치라고 나와요.")

# ---------- open ----------
op = [sec("open")] + head("설치하고 열기", "저장소 폴더를 열고, Git Graph를 눌러요", "#3A4150")
VL, VT, VW, VH = 96, 236, 1040, 740
op += vscode_shell(VL, VT, VW, VH, active="scm", status=True)
PX = VL + 80
op.append(f'<div style="position:absolute;left:{PX}px;top:{VT+2}px;width:420px;height:{VH-44}px;background:{VS["bar"]};padding:24px 24px;display:flex;flex-direction:column;gap:18px">'
          + '<div style="display:flex;flex-direction:row;align-items:center;justify-content:space-between">' + p(f"font-size:21px;font-weight:700;color:{VS['txt']};letter-spacing:1px", "SOURCE CONTROL")
          + f'<div style="display:flex;flex-direction:row;gap:12px;align-items:center;border:2px solid {OR};border-radius:6px;padding:4px 6px">{graph_icon(30)}</div></div>'
          + f'<div style="height:48px;background:{VS["input"]};border:1px solid {VS["bd"]};border-radius:4px;padding:0 14px;display:flex;align-items:center">' + p(f"font-size:21px;color:{VS['dim']}", "Message") + '</div>'
          + p(f"font-size:22px;color:{VS['txt']}", "Changes") + '</div>')
op.append(f'<div style="position:absolute;left:{PX+420}px;top:{VT+2}px;width:{VW-82-420}px;height:{VH-44}px;padding:28px 32px;display:flex;flex-direction:column;gap:16px">'
          + f'<div style="background:{VS["bar"]};border:1px solid {VS["bd"]};border-radius:8px;padding:12px 16px;display:flex;flex-direction:column;gap:10px">'
          + p(f"font-size:22px;color:#FFFFFF;background:{VS['input']};border:2px solid {VS['blue']};border-radius:4px;padding:4px 10px", "&gt; git graph")
          + p(f"font-size:21px;color:#FFFFFF;background:#04395E;padding:4px 10px;border-radius:4px", "Git Graph: View Git Graph (git log)") + '</div>'
          + p(f"font-size:22px;line-height:1.5;color:{VS['dim']}", "명령 팔레트<br>Windows Ctrl+Shift+P<br>Mac Cmd+Shift+P") + '</div>')
op.append(f'<div style="position:absolute;left:{VL+2}px;top:{VT+VH-42}px;width:{VW-4}px;height:40px;background:{VS["bar"]};border-top:1px solid {VS["bd"]};border-radius:0 0 14px 14px;padding:0 20px;display:flex;flex-direction:row;gap:28px;align-items:center">'
          + f'<div style="display:flex;flex-direction:row;gap:8px;align-items:center">{branch_svg(VS["txt"], 22)}' + p(f"font-size:21px;color:{VS['txt']}", "main") + '</div>' + p(f"font-size:21px;color:{VS['txt']}", "⊗ 0  ⚠ 0")
          + p(f"font-size:21px;color:{VS['txt']};border:2px solid {OR};border-radius:4px;padding:0 8px;line-height:30px", "Git Graph") + '</div>')
op.append(marker(1, VL + 300, VT + VH - 100, 2))
op.append(marker(2, PX + 420 - 50, VT + 70, 3))
op.append(marker(3, PX + VW - 82 - 70, VT + 10, 4))
op.append(steps_card(1176, 236, 648, 740, [("아래 상태 표시줄의 Git Graph", "가장 쉬워요"),
                                           ("소스 제어 탭 위의 그래프 아이콘", "왼쪽 막대의 갈래 모양 아이콘"),
                                           ("명령 팔레트에서 git graph", "View Git Graph (git log)를 골라요")],
                      title="여는 법 세 가지", foot="먼저 File &gt; Open Folder로<br>hello-git 폴더를 열어 둬요."))
W("open", op, "Git Graph는 VS Code에 열린 폴더가 Git 저장소일 때만 동작해요. File > Open Folder(한국어 화면은 파일 > 폴더 열기)로 git init을 했던 hello-git 폴더를 먼저 열어요. 그다음 세 방법 중 아무거나 쓰면 돼요. 상태 표시줄의 Git Graph 글자를 누르는 게 가장 빨라요. 열리면 편집기 자리에 Git Graph 탭이 생겨요.")

# ---------- part 2: overview ----------
ov = [sec("overview")] + head("화면 읽기", "한 줄이 커밋 하나예요", BL)
g, ys = gg(ST["sc10"], T=236, pre="", win_h=496)
ov += g
MY = 236 + 496 - 26
MK = [(1, 104, MY, "그래프", "점과 선"), (2, 300, MY, "설명", "이름표와 커밋 메시지"),
      (3, 1290, MY, "날짜", ""), (4, 1540, MY, "작성자", ""), (5, 1660, MY, "커밋 번호", "")]
for n, x, y, _, _ in MK:
    ov.append(marker(n, x, y, n, BL))
ov.append(f'<div data-build-in="rise order 6" style="position:absolute;left:96px;top:780px;width:1728px;display:flex;flex-direction:row;gap:20px">')
for n, _, _, t1, t2 in MK:
    ov.append(f'<div style="flex:1;display:flex;flex-direction:row;gap:14px;align-items:center;background:#FFFFFF;border:2px solid {LINE};border-radius:16px;padding:20px 22px">'
              + p(f"width:44px;height:44px;flex:none;font-size:24px;font-weight:900;line-height:44px;text-align:center;color:#FFFFFF;background:{BL};border-radius:22px", str(n))
              + '<div style="display:flex;flex-direction:column;gap:4px">' + p(f"font-size:28px;font-weight:700;color:{INK}", t1) + (p(f"font-size:22px;color:{SUB}", t2) if t2 else "") + '</div></div>')
ov.append('</div>')
ov.append(p(f"position:absolute;left:96px;top:940px;width:1728px;font-size:28px;line-height:1.45;color:{SUB}", "맨 위 줄의 Repo는 저장소 이름, Branches: Show All은 모든 브랜치를 보여 준다는 뜻이에요. 그대로 두면 돼요.", ' data-build-in="fade order 7"'))
W("overview", ov, "VS Code를 어두운 테마로 쓰면 이렇게 보여요. 밝은 테마여도 배치는 같아요. 표는 git log --oneline과 같은 순서로 맨 위가 가장 최근 커밋이에요. 작성자 칸의 lee는 팀원이 GitHub에 올린 커밋이에요. 오른쪽 위 아이콘은 찾기, 터미널, 설정, Fetch, 새로고침이에요. 이 중 새로고침만 쓰면 돼요.")

# ---------- dots ----------
dt = [sec("dots")] + head("화면 읽기", "03의 그래프를 세운 모양이에요", BL)
dt.append(f'<div style="position:absolute;left:96px;top:236px;width:840px;height:600px;background:#FDFCF9;border:2px solid {LINE};border-radius:24px"></div>')
dt.append(p(f"position:absolute;left:136px;top:266px;width:760px;font-size:28px;font-weight:700;color:#6A7180", "03 슬라이드의 그림"))
for i, k in enumerate(["A", "B", "L"]):
    x = 236 + i * 260
    if i:
        dt.append(f'<div style="position:absolute;left:{x-260}px;top:{533}px;width:260px;height:6px;background:#9DB8F2"></div>')
for i, k in enumerate(["A", "B", "L"]):
    x = 236 + i * 260
    dt.append(f'<div style="position:absolute;left:{x-26}px;top:{510}px;width:52px;height:52px;border-radius:50%;background:{BL};border:4px solid {BL}"></div>')
    dt.append(p(f"position:absolute;left:{x-90}px;top:580px;width:180px;font-family:{MONO};font-size:26px;font-weight:700;text-align:center;color:{INK}", h7(k)))
dt.append(f'<x-shape kind="arrow-right" style="position:absolute;left:236px;top:700px;width:560px;height:40px;background:#C9CCD3"></x-shape>')
dt.append(p(f"position:absolute;left:136px;top:756px;width:760px;font-size:26px;font-weight:700;text-align:center;color:#6A7180", "왼쪽에서 오른쪽으로 쌓여요"))
g, _ = gg(ST["sc5"], L=984, T=236, W=840, s=1.25, tab=False, ctl=False, hdr=True, full=False, nrows=3, pre="dg-", win_h=600)
dt += [x.replace(' style=', ' data-build-in="rise order 1" style=', 1) for x in g]
dt.append('<svg data-build-in="fade order 2" viewBox="0 0 40 230" style="position:absolute;left:1006px;top:480px;width:40px;height:230px"><line x1="20" y1="226" x2="20" y2="30" stroke="#8C95A6" stroke-width="8"/><polygon points="0,36 20,0 40,36" fill="#8C95A6"/></svg>')
dt.append(p(f"position:absolute;left:1070px;top:640px;width:720px;font-size:26px;font-weight:700;color:{VS['txt']}", "Git Graph는 아래에서 위로 쌓여요", ' data-build-in="fade order 2"'))
dt.append(p(f"position:absolute;left:96px;top:880px;width:1728px;font-size:30px;font-weight:700;line-height:1.45;color:{INK}", "점 하나가 커밋 하나, 맨 위가 가장 최근이에요. 커밋 번호는 8자리로 나와요. 터미널의 7자리와 앞부분이 같아요.", ' data-build-in="fade order 3"'))
W("dots", dt, "03에서는 시간이 왼쪽에서 오른쪽으로 흐르게 그렸어요. Git Graph는 git log처럼 위에 새 커밋을 올려요. 03 그림을 왼쪽으로 눕혀 세웠다고 생각하면 돼요. 선은 커밋이 어느 커밋 다음에 만들어졌는지 이어 줘요. 커밋 번호 e12ffc2와 e12ffc2e처럼 Git Graph 쪽이 한 글자 더 길어요.")

# ---------- labels ----------
lb = [sec("labels")] + head("화면 읽기", "굵은 이름표가 지금 있는 브랜치예요", BL)
g, ys = gg(ST["sc7"], L=96, T=236, W=1060, s=1.45, tab=False, ctl=False, hdr=False, full=False, nrows=4, pre="lb-", pad_top=64)
lb += g
lb.append(marker(1, 420, 250, 1, BL))
lb.append(marker(2, 119, 250, 2, BL))
lb.append(marker(3, 196, ys[1] - 26, 3, BL))
ANN = [("굵은 글씨, 색 테두리", "지금 있는 브랜치예요.<br>터미널의 HEAD -&gt; 와 같아요."),
       ("속이 빈 점", "HEAD가 가리키는 커밋이에요.<br>지금 내 폴더가 이 모습이에요."),
       ("main | origin", "main과 origin/main이<br>같은 커밋에 있어요.")]
lb.append('<div style="position:absolute;left:1196px;top:236px;width:628px;height:540px;display:flex;flex-direction:column;justify-content:space-between">')
for i, (t1, t2) in enumerate(ANN, 1):
    lb.append(f'<div data-build-in="fade order {i}" style="display:flex;flex-direction:row;gap:18px;align-items:flex-start">'
              + p(f"width:48px;height:48px;flex:none;font-size:26px;font-weight:900;line-height:48px;text-align:center;color:#FFFFFF;background:{BL};border-radius:24px", str(i))
              + '<div style="display:flex;flex-direction:column;gap:8px">' + p(f"font-size:32px;font-weight:700;color:{INK}", t1) + p(f"font-size:26px;line-height:1.45;color:{SUB}", t2) + '</div></div>')
lb.append('</div>')
lb += terminal([("$", "git log --oneline"), ("o", f"{h7('C')} (HEAD -> feature/login) feat: 비밀번호 찾기 추가"), ("o", f"{h7('L')} (origin/main, main) docs: README 추가")],
               left=96, top=820, w=1728, h=160, size=26, lh=1.4)
W("labels", lb, "feature/login 브랜치를 만들고 커밋 하나를 한 뒤의 화면이에요. 이름표가 두 개 있는데, 지금 있는 feature/login만 굵은 글씨에 색 테두리예요. 맨 위 커밋의 점은 속이 비어 있어요. HEAD가 가리키는 커밋이라는 표시예요. 설명 칸 맨 앞의 작은 빈 동그라미도 같은 뜻이에요. main 이름표 오른쪽의 기울어진 origin은 origin/main도 여기 있다는 뜻이에요.")

# ---------- origin ----------
og = [sec("origin")] + head("화면 읽기", "origin/main은 GitHub의 main이에요", PUR)
CASES = [("같아요", [R("B", 0, [MAIN_O], True), R("A")], "할 일 없음", "#3A4150"),
         ("내 컴퓨터가 앞서요", [R("B", 0, [MAIN], True), R("A", 0, [OM])], "git push origin main", BL),
         ("GitHub이 앞서요", [R("L", 0, [OM]), R("B", 0, [MAIN], True)], "git pull origin main", GR)]
for i, (t1, rows, cmd, col) in enumerate(CASES):
    x = 96 + i * 592
    og.append(p(f"position:absolute;left:{x}px;top:250px;width:544px;font-size:32px;font-weight:700;color:{INK}", t1, f' data-build-in="fade order {i+1}"'))
    g, _ = gg(rows, L=x, T=310, W=544, s=1.0, tab=False, ctl=False, hdr=False, full=False, nrows=2, pre=f"o{i}-", pad_top=14, commit=False)
    og += [y_.replace(' style=', f' data-build-in="fade order {i+1}" style=', 1) for y_ in g]
    og.append(p(f"position:absolute;left:{x}px;top:460px;width:544px;font-family:{MONO};font-size:26px;font-weight:700;line-height:1.6;text-align:center;border-radius:12px;color:#FFFFFF;background:{col}", cmd, f' data-build-in="fade order {i+1}"'))
og.append(f'<div data-build-in="rise order 4" style="position:absolute;left:96px;top:600px;width:1728px;display:flex;flex-direction:row;gap:28px;align-items:center;background:#FFFFFF;border:2px solid {LINE};border-radius:20px;padding:32px 40px">'
          f'<x-icon name="Cloud" style="width:56px;height:56px;color:{PUR}"></x-icon>'
          '<div style="display:flex;flex-direction:column;gap:10px">'
          + p(f"font-size:32px;font-weight:700;line-height:1.4;color:{INK}", "origin/main은 마지막으로 GitHub과 주고받았을 때의 main 위치예요.")
          + p(f"font-size:26px;line-height:1.45;color:{SUB}", "팀원이 GitHub에 새로 올린 커밋은 git fetch origin을 쳐야 Git Graph에 나타나요.") + '</div></div>')
og.append(p(f"position:absolute;left:96px;top:840px;width:1728px;font-size:28px;line-height:1.45;color:{SUB}", "02에서 git log --oneline과 git log --oneline origin/main을 따로 쳐서 비교했던 걸 한 화면에서 봐요.", ' data-build-in="fade order 5"'))
W("origin", og, "이름표가 main | origin 하나로 붙어 있으면 내 main과 GitHub의 main이 같아요. 내가 커밋하고 아직 push하지 않았으면 main이 origin/main보다 위에 있어요. 팀원이 push한 걸 git fetch origin으로 받아 오면 origin/main이 main보다 위로 올라가요. Git Graph가 GitHub에 직접 물어보는 게 아니라 내 컴퓨터에 받아 둔 기록을 보여 준다는 점을 짚어 주세요.")

# ---------- part 3: scenes ----------
scene("sc1", "실습 1 · 고치고 아직 커밋 전", 'echo "로그인 버튼" &gt;&gt; login.md', "sc1",
      [("$", 'echo "로그인 버튼" >> login.md'), ("$", "git status"), ("o", "On branch main"), ("o", "Changes not staged for commit:"), ("r", "\tmodified:   login.md")],
      ("Search", "맨 위에 회색 빈 점", "Uncommitted Changes (1)<br>= 아직 커밋 안 한 파일 1개", "#6A7180"),
      "e12ffc2 커밋 하나를 GitHub에 올려 둔 상태에서 시작해요. login.md에 한 줄을 더하면 Git Graph 맨 위에 Uncommitted Changes 줄이 생겨요. 괄호 안 숫자는 바뀐 파일 수예요. git status에 나오는 파일과 같아요. 이 줄을 누르면 바뀐 파일 목록이 나오고, 파일을 누르면 04에서 본 diff가 열려요. status의 안내 문구 줄은 화면 때문에 뺐어요.", transition="fade", cmd_size=46)
scene("sc2", "실습 2 · 커밋하면", 'git commit -m "feat: 로그인 버튼 추가"', "sc2",
      [("$", "git add login.md"), ("$", 'git commit -m "feat: 로그인 버튼 추가"'), ("o", f"[main {h7('B')}] feat: 로그인 버튼 추가"), ("o", " 1 file changed, 1 insertion(+)")],
      ("Database", "새 점이 위에 생기고<br>main이 따라 올라가요", "origin/main은 아직 아래에 있어요", BL),
      "회색 줄이 사라지고 그 자리에 새 커밋 15d92cbb가 생겼어요. main 이름표가 새 커밋으로 올라갔어요. origin/main은 GitHub에 마지막으로 올린 e12ffc2e에 그대로 있어요. 내 컴퓨터가 커밋 하나 앞선 상태예요.", cmd_size=46)
scene("sc3", "실습 3 · push하면", "git push origin main", "sc3",
      [("$", "git push origin main"), ("o", "To https://github.com/kim/hello-git.git"), ("o", f"   {h7('A')}..{h7('B')}  main -> main")],
      ("Cloud", "origin이 main 옆에<br>붙었어요", "GitHub도 같은 커밋이에요", PUR),
      "push하고 나면 origin/main이 main과 같은 커밋으로 올라와서 main | origin 이름표 하나로 합쳐져요. push 출력의 진행 줄(Enumerating objects 등)은 화면 때문에 뺐어요.")
scene("sc4", "실습 4 · 팀원이 올린 걸 확인하면", "git fetch origin", "sc4",
      [("#", "# 팀원 lee가 README.md를 만들어 GitHub에 push했어요"), ("$", "git fetch origin"), ("o", "From https://github.com/kim/hello-git"), ("o", f"   {h7('B')}..{h7('L')}  main       -> origin/main")],
      ("Users", "origin/main이<br>main보다 위로", "GitHub이 커밋 하나 앞서요", GR),
      "팀원 lee가 GitHub에 커밋을 올렸어요. git fetch origin으로 받아 오면 lee의 커밋 b9f30e50이 맨 위에 생기고 origin/main 이름표가 붙어요. 내 main은 아직 아래에 있어요. fetch는 기록만 받아 오고 내 파일은 바꾸지 않아요. 굵은 main이 아래에 있으니 내 폴더는 아직 예전 모습이에요.")
scene("sc5", "실습 5 · pull하면", "git pull origin main", "sc5",
      [("$", "git pull origin main"), ("o", "From https://github.com/kim/hello-git"), ("o", " * branch            main       -> FETCH_HEAD"), ("o", f"Updating {h7('B')}..{h7('L')}"), ("o", "Fast-forward"),
       ("o", " README.md | 1 +"), ("o", " 1 file changed, 1 insertion(+)")],
      ("CheckCircle", "main이 올라가서<br>다시 붙었어요", "내 폴더에 README.md가 생겨요", GR),
      "pull하면 main이 origin/main 자리로 올라가서 다시 main | origin 하나가 돼요. 갈라진 게 없어서 선은 한 줄 그대로예요. 출력의 create mode 줄은 화면 때문에 뺐어요.")
scene("sc6", "실습 6 · 브랜치를 만들면", "git checkout -b feature/login", "sc6",
      [("$", "git checkout -b feature/login"), ("o", "Switched to a new branch 'feature/login'"), ("$", "git log --oneline"), ("o", f"{h7('L')} (HEAD -> feature/login, origin/main, main) docs: README 추가")],
      ("Activity", "같은 점에<br>이름표가 하나 더", "굵은 글씨가 feature/login으로", OR),
      "브랜치를 만들면 지금 커밋에 feature/login 이름표가 하나 더 붙어요. 새 커밋은 아직 없어서 점은 그대로예요. 굵은 글씨가 main에서 feature/login으로 옮겨 갔어요. HEAD가 feature/login으로 옮겨 갔다는 뜻이에요.")
scene("sc7", "실습 7 · 브랜치에서 커밋하면", 'git commit -m "feat: 비밀번호 찾기 추가"', "sc7",
      [("$", 'echo "비밀번호 찾기" >> login.md'), ("$", "git add login.md"), ("$", 'git commit -m "feat: 비밀번호 찾기 추가"'), ("o", f"[feature/login {h7('C')}] feat: 비밀번호 찾기 추가"), ("o", " 1 file changed, 1 insertion(+)")],
      ("Activity", "feature/login만<br>위로 올라가요", "main은 제자리예요", OR),
      "feature/login에서 커밋하면 feature/login 이름표만 새 커밋으로 올라가요. main | origin은 b9f30e50에 남아요. main 쪽에 새 커밋이 없어서 아직 선은 한 줄로 보여요. 03의 fast-forward 장면과 같은 모양이에요.", cmd_size=46)
scene("sc8", "실습 8 · main으로 돌아가 커밋하면", 'git checkout main → git commit', "sc8",
      [("$", "git checkout main"), ("o", "Switched to branch 'main'"), ("$", 'echo "실행 방법은 준비 중이에요" >> README.md'), ("$", "git add README.md"), ("$", 'git commit -m "docs: README에 실행 방법 추가"'), ("o", f"[main {h7('D')}] docs: README에 실행 방법 추가")],
      ("Activity", "길이 둘로<br>갈라졌어요", "분홍 선이 feature/login", OR),
      "main으로 돌아와 README.md를 고쳐 커밋했어요. 이제 두 브랜치가 b9f30e50에서 서로 다른 커밋을 가졌어요. Git Graph는 feature/login 쪽을 오른쪽 분홍 선으로 따로 그려요. 03에서 그린 갈라진 길 그림과 같아요. 굵은 글씨와 빈 점이 다시 main으로 왔어요.")
scene("sc9", "실습 9 · merge하면", "git merge feature/login", "sc9",
      [("$", "git merge feature/login"), ("#", "# vim이 열리면 Esc, :wq, Enter"), ("o", "Merge made by the 'ort' strategy."), ("o", " login.md | 1 +"), ("o", " 1 file changed, 1 insertion(+)")],
      ("Link", "두 선이<br>merge 커밋에서 만나요", "점 하나에 선 두 개", BL),
      "main에서 git merge feature/login을 치면 merge 커밋 5991c366이 생겨요. 이 점에서 아래로 선이 두 개 나가요. 하나는 main의 ad50d357, 하나는 feature/login의 dd7f15af예요. 03과 같이 merge 메시지를 쓰는 vim이 열리면 Esc를 누른 뒤 :wq와 Enter를 쳐요.")
scene("sc10", "실습 10 · 다시 push하면", "git push origin main", "sc10",
      [("$", "git push origin main"), ("o", "To https://github.com/kim/hello-git.git"), ("o", f"   {h7('L')}..{h7('M')}  main -> main")],
      ("Cloud", "main | origin이<br>맨 위에 같이", "GitHub에도 merge가 올라갔어요", PUR),
      "push하면 origin/main이 merge 커밋으로 올라와서 다시 main | origin이 돼요. feature/login은 push하지 않아서 origin이 붙지 않아요. 다 쓴 브랜치는 03에서 배운 git branch -d feature/login으로 지우면 이름표만 사라지고 점과 선은 남아요.")

# ---------- detail ----------
dl = [sec("detail")] + head("명령 치고 확인하기", "커밋 줄을 누르면 바뀐 파일이 보여요", GR)
EXP = 236
g, ys = gg(ST["sc10"], T=200, tab=False, ctl=False, hdr=True, expand="C", expand_h=EXP, sel="C", pre="")
dl += g
cy = ys[2] + 24
dl.append(f'<div data-build-in="rise order 1" style="position:absolute;left:226px;top:{cy+4}px;width:1590px;height:{EXP-12}px;background:#252526;border:1px solid {VS["bd"]};border-radius:8px;display:flex;flex-direction:row">'
          + f'<div style="flex:1;padding:18px 24px;display:flex;flex-direction:column;gap:2px;border-right:1px solid {VS["bd"]}">'
          + "".join(p(f"font-size:20px;line-height:1.45;color:{VS['txt']};white-space:nowrap", f"<b>{k_}</b> {e(v_)}") for k_, v_ in [("Commit:", C["C"][0]), ("Parents:", C["L"][0]), ("Author:", "kim <kim@example.com>"), ("Committer:", "kim <kim@example.com>"), ("Date:", "Thu Oct 29 2026 10:04:00 GMT+0900")])
          + p(f"font-size:20px;line-height:1.6;color:{VS['txt']};margin-top:8px", "feat: 비밀번호 찾기 추가") + '</div>'
          + '<div style="width:420px;flex:none;padding:18px 24px;display:flex;flex-direction:column;gap:10px">'
          + p(f"font-size:22px;color:{VS['txt']}", "📁 hello-git".replace("📁 ", ""))
          + f'<div style="display:flex;flex-direction:row;gap:10px;align-items:center;border:2px solid {OR};border-radius:6px;padding:4px 10px">'
          + p(f"font-size:22px;color:#E2C08D", "login.md") + p(f"font-size:22px;color:{VS['txt']}", '(<span style="color:#7FD18B">+1</span>|<span style="color:#F28B82">-0</span>)') + '</div></div></div>')
dl.append(f'<div data-build-in="rise order 2" style="position:absolute;left:96px;top:{200 + 44 + 6*48 + EXP + 14 + 26}px;width:1728px;display:flex;flex-direction:row;gap:28px;align-items:center;background:#FFFFFF;border:2px solid {LINE};border-radius:20px;padding:26px 36px">'
          f'<x-icon name="Search" style="width:52px;height:52px;color:{GR}"></x-icon>'
          + '<div style="display:flex;flex-direction:column;gap:8px">' + p(f"font-size:30px;font-weight:700;color:{INK}", "파일 이름을 누르면 04에서 본 diff 화면이 열려요")
          + p(f"font-size:24px;color:{SUB}", "터미널의 git show와 같은 내용이에요. 다시 누르면 닫혀요.") + '</div></div>')
W("detail", dl, "커밋 줄 아무 데나 한 번 누르면 아래에 상세 정보가 펼쳐져요. 왼쪽은 커밋 번호 전체, 부모 커밋, 만든 사람, 날짜, 메시지예요. 오른쪽은 이 커밋에서 바뀐 파일과 더한 줄, 지운 줄 수예요. 파일 이름을 누르면 VS Code의 diff 화면이 열려서 왼쪽에 예전, 오른쪽에 바뀐 내용이 나란히 보여요. Date 줄 끝의 시간대 이름은 화면 때문에 뺐어요.")

# ---------- part 4: rule ----------
ru = [sec("rule")] + head("쓸 때 주의", "명령은 터미널에서, 확인은 Git Graph에서", OR)
g, ys = gg(ST["sc10"], L=96, T=236, W=1000, s=1.0, tab=False, ctl=False, hdr=False, full=False, nrows=6, pre="ru-", pad_top=10, sel="C")
ru += g
MENU = ["Add Tag...", "Create Branch...", "Checkout...", "Cherry Pick...", "Revert...", "Drop...", "Merge into current branch...", "Rebase current branch on this Commit...", "Reset current branch to this Commit...", "Copy Commit Hash to Clipboard"]
ru.append(f'<div style="position:absolute;left:560px;top:{ys[2]+16}px;width:500px;background:#252526;border:1px solid #454545;border-radius:8px;padding:8px 0;display:flex;flex-direction:column;box-shadow:0 8px 24px rgba(0,0,0,.35)">'
          + "".join(p(f"font-size:20px;line-height:36px;padding:0 20px;color:{VS['txt']}", e(m)) for m in MENU) + '</div>')
ru.append(f'<div data-build-in="rise order 1" style="position:absolute;left:1136px;top:236px;width:688px;height:720px;background:#FFFFFF;border:2px solid {LINE};border-radius:20px;padding:36px;display:flex;flex-direction:column;gap:22px">'
          + f'<x-icon name="Warning" style="width:52px;height:52px;color:{OR}"></x-icon>'
          + p(f"font-size:32px;font-weight:700;line-height:1.4;color:{INK}", "오른쪽 클릭 메뉴로 checkout, merge, reset도 할 수 있어요")
          + p(f"font-size:26px;line-height:1.5;color:{SUB}", "수업에서는 메뉴를 쓰지 않아요. 무엇을 쳤는지 터미널에 남아야 오류가 났을 때 읽고 고칠 수 있어요.")
          + p(f"font-size:26px;line-height:1.5;color:{SUB}", "오른쪽 위 Fetch 버튼 대신 git fetch origin을 쳐요.")
          + '<div style="flex:1"></div>'
          + f'<div style="display:flex;flex-direction:row;gap:16px">'
          + p(f"flex:1;font-size:26px;font-weight:700;line-height:1.5;text-align:center;padding:14px 0;border-radius:12px;color:#FFFFFF;background:{INK}", "터미널: 명령")
          + p(f"flex:1;font-size:26px;font-weight:700;line-height:1.5;text-align:center;padding:14px 0;border-radius:12px;color:#FFFFFF;background:{GR}", "Git Graph: 확인") + '</div></div>')
W("rule", ru, "커밋 줄이나 이름표를 오른쪽 클릭하면 이런 메뉴가 나와요. 버튼 한 번에 reset이나 merge가 실행돼서 무엇이 바뀌었는지 놓치기 쉬워요. 그래서 수업에서는 명령을 터미널에 직접 치고, 친 결과가 맞는지 Git Graph로 확인하는 데만 써요. 잘못 눌렀다면 창을 닫지 말고 터미널에서 git status와 git log --oneline부터 봐요.")

# ---------- trouble ----------
tb = [sec("trouble")] + head("막힐 때", "Git Graph가 안 열리거나 그림이 그대로예요", "#1E3F8F")
cases = [("Git Graph를 눌러도 저장소가 없다고 나와요", "No Git repositories were found... 가 보이면 폴더를 잘못 연 거예요", "File &gt; Open Folder<br>hello-git 폴더 열기"),
         ("팀원이 올린 커밋이 안 보여요", "Git Graph는 내 컴퓨터에 받아 둔 기록만 보여 줘요", "git fetch origin"),
         ("명령을 쳤는데 그림이 그대로예요", "보통 저절로 바뀌어요. 안 바뀌면 오른쪽 위 새로고침", "↻ Refresh")]
tb.append('<div style="position:absolute;left:96px;top:250px;width:1728px;display:flex;flex-direction:column;gap:24px">')
for i, (q, a_, cmd) in enumerate(cases, 1):
    tb.append(f'<div data-build-in="rise order {i}" style="height:200px;display:flex;flex-direction:row;gap:32px;align-items:center;background:#FFFFFF;border:2px solid {LINE};border-radius:20px;padding:24px 36px">'
              + p(f"width:64px;height:64px;flex:none;font-size:34px;font-weight:900;line-height:64px;text-align:center;color:#FFFFFF;background:#1E3F8F;border-radius:32px", str(i))
              + '<div style="flex:1;display:flex;flex-direction:column;gap:10px">' + p(f"font-size:34px;font-weight:700;color:{INK}", q) + p(f"font-size:26px;color:{SUB}", a_) + '</div>'
              + p(f"width:460px;flex:none;font-family:{MONO};font-size:28px;font-weight:700;line-height:1.5;color:{INK};background:#EEEFF2;padding:14px 20px;border-radius:12px", cmd) + '</div>')
tb.append('</div>')
W("trouble", tb, "가장 흔한 건 1번이에요. 바탕화면이나 상위 폴더를 열면 Git 저장소를 못 찾아요. git init을 한 바로 그 폴더를 열어요. 2번은 02의 fetch 규칙과 같아요. 3번의 새로고침은 Git Graph 탭 오른쪽 위 둥근 화살표 아이콘이에요.")

# ---------- cheatsheet ----------
ch = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};padding:112px 128px;display:flex;flex-direction:column;gap:40px">',
      f'<h2 style="font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>', '<div style="display:flex;flex-direction:row;gap:24px;flex:1">']
cards = [("설치", "#3A4150", "확장 탭<br>Ctrl+Shift+X<br>git graph 검색<br>mhutchie<br>Install"),
         ("열기", BL, "폴더 열기<br>hello-git<br><br>상태 표시줄의<br>Git Graph"),
         ("읽기", GR, "점 = 커밋<br>맨 위 = 최신<br>굵은 이름표 = HEAD<br>빈 점 = 지금 커밋<br>main | origin<br>= GitHub과 같음"),
         ("확인", OR, "명령은 터미널<br>결과는 Git Graph<br><br>팀원 커밋은<br>git fetch origin")]
for h_, hc, body in cards:
    ch.append(f'<div style="flex:1;display:flex;flex-direction:column;gap:16px;background:#FFFFFF;border:2px solid {LINE};border-top:10px solid {hc};border-radius:20px;padding:32px 28px">'
              f'<h3 style="font-size:32px;font-weight:700;color:{hc}">{h_}</h3>'
              f'<p style="font-size:28px;line-height:1.7;color:{INK}">{body}</p></div>')
ch += ['</div>', f'<p style="font-size:28px;font-weight:700;color:{INK}">명령을 칠 때마다 Git Graph를 한 번씩 보는 습관을 들여요.</p>']
W("cheatsheet", ch, "수업 끝에 이 장을 띄워 두고 학생에게 commit, push, checkout, merge 뒤에 Git Graph에서 무엇이 바뀌는지 말로 설명해 보게 하세요.")
print("ok")
