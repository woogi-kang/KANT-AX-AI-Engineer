"""Generates every slide of the team repo deck (06).

Three people (kim, lee, park) share one GitHub repo. A scene shows the team as one picture: four lanes in a row
(GitHub and the three computers, one colour per person, no card outlines) with the commits drawn large, a label
on the picture for the one thing to look at, and the terminal of whoever is typing sized to its lines.
Terminal output and hashes come from tools/demo.sh and tools/cases.sh (git 2.43).
Usage (in 06-team-repo): python3 tools/gen.py slides
"""
import html, json, os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from highlight import (spot, spot_off, cursor, cursor_off, ring, underline, box, lspot, lspot_off, zoom, zoom_off,  # noqa: E402
                       blur, blur_off, pulse, shake, SLAM, STAGGER, DIM, DELAY, WIPE)

OUT = sys.argv[1]
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
BG, INK, SUB, LINE, MUTE, HAIR = "#F6F5F1", "#1D2330", "#4A5262", "#E1DED6", "#6A7180", "#D9D5CB"
BL, GR, OR, RED, PUR, NAVY = "#2459C9", "#1F8A4C", "#B26A00", "#A33131", "#5A3BB8", "#1E3F8F"
PC = {"gh": PUR, "kim": BL, "lee": GR, "park": OR}
TINT = {"gh": "#EFEAFB", "kim": "#E6EDFA", "lee": "#E3F2E9", "park": "#FAEEDB"}
PNAME = {"gh": "GitHub", "kim": "kim", "lee": "lee", "park": "park"}
PSUB = {"gh": "kim/team-intro", "kim": "팀장 컴퓨터", "lee": "팀원 컴퓨터", "park": "팀원 컴퓨터"}
PICON = {"gh": "Cloud", "kim": "Users", "lee": "Users", "park": "Users"}
GHT, GHS = "#1F2328", "#59636E"


def e(s):
    return html.escape(s, quote=False)


def p(style, text, attrs=""):
    return f'<p{attrs} style="{style}">{text}</p>'


def text_w(s, size):
    """Rough rendered width: mono glyphs 0.6em, Hangul (Noto Sans KR fallback) about 1em."""
    return sum(size * (1.0 if ord(c) > 0x2E80 else 0.6) for c in s)


ORDER, PAGES = [], {}


def W(name, parts, notes, add=True):
    if add:
        ORDER.append(name)
    PAGES[name] = "\n".join(parts) + f"\n<aside>{e(notes)}</aside>\n</section>\n"


def sec(i, transition="fade", bg=BG):
    return f'<section id="{i}" data-transition="{transition}" style="background:{bg};color:{INK};font-family:{SANS};padding:96px;display:flex;flex-direction:column;word-break:keep-all">'


def head(eyebrow, title, color=BL):
    return [p(f"position:absolute;left:96px;top:48px;width:1728px;font-size:24px;font-weight:700;color:{color}", e(eyebrow), ' id="eyebrow"'),
            f'<h2 id="title" style="position:absolute;left:96px;top:86px;width:1728px;font-size:50px;font-weight:700;line-height:1.2;color:{INK}">{title}</h2>']


def hair(x, y, w):
    return f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:2px;background:{HAIR}"></div>'


def bi(kind, order):
    return f' data-build-in="{kind} order {order}"'


# ---------- terminal ----------
TC = {"$": "#F2C46D", "o": "#D8DEE9", "#": "#9AA3B5", "g": "#7FD18B", "r": "#F28B82"}
T_PAD, T_HEAD, T_LH = 22, 52, 1.36


def term_fit(lines, w, h_max, cap=34):
    """Largest font size (<= cap) at which every line fits the width and all lines fit h_max."""
    longest = max(text_w(("$ " if k == "$" else "") + t.replace("\t", " " * 8), 1) for k, t in lines)
    by_w = (w - 64) / max(longest, 1)
    by_h = (h_max - 2 * T_PAD - T_HEAD) / (len(lines) * T_LH)
    return int(min(cap, by_w, by_h))


def term_h(lines, size):
    return round(2 * T_PAD + T_HEAD + len(lines) * size * T_LH)


def line_box(left, top, lines, size, i):
    """(x, y, w, h) of line i in a terminal drawn at left/top."""
    k, t = lines[i]
    t = ("$ " if k == "$" else "") + t.replace("\t", " " * 8)
    lead = len(t) - len(t.lstrip(" "))
    x = left + 32 + text_w(t[:lead], size)
    y = top + T_PAD + T_HEAD + i * size * T_LH
    return round(x), round(y), round(text_w(t.strip(), size)), round(size * T_LH)


def terminal(lines, who, left, top, w, size, tid="term"):
    ws = who if isinstance(who, tuple) else (who,) if who else ()
    h = term_h(lines, size)
    o = [f'<div id="{tid}" style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:#1B2029;border-radius:20px;padding:{T_PAD}px 32px;display:flex;flex-direction:column;font-family:{MONO};font-variant-ligatures:none">']
    o.append(f'<div style="height:{T_HEAD - 12}px;margin-bottom:12px;display:flex;flex-direction:row;gap:12px;align-items:center;border-bottom:1px solid #343B48">'
             + "".join(f'<div style="width:16px;height:16px;border-radius:8px;background:{PC[x]}"></div>' for x in ws)
             + p(f"font-family:{SANS};font-size:22px;font-weight:700;line-height:1;color:#FFFFFF", (", ".join(ws) + "의 터미널") if ws else "터미널")
             + p("font-size:20px;line-height:1;color:#8C95A6", "~/team-intro") + '</div>')
    for kind, text in lines:
        t = e(text).replace("\t", "&#160;" * 8)
        lead = len(t) - len(t.lstrip(" "))
        t = "&#160;" * lead + t.lstrip(" ") if t.strip() else "&#160;"
        if kind == "$":
            t = "$ " + t
        bold = "font-weight:700;" if kind == "$" else ""
        o.append(p(f"font-size:{size}px;line-height:{T_LH};white-space:pre;{bold}color:{TC[kind]}", t))
    o.append('</div>')
    return o, h


# ---------- commits (tools/demo.sh) ----------
# key: (hash, message, author, parents, is_merge)
C = {
    "I": ("7f7794e", "Initial commit", "kim", [], False),
    "K": ("11f6ff4", "docs: kim 자기소개 추가", "kim", ["I"], False),
    "L": ("a078082", "docs: lee 자기소개 추가", "lee", ["I"], False),
    "M": ("3c66163", "Merge branch 'main' of https://github.com/kim/team-intro", "lee", ["L", "K"], True),
    "N": ("0586354", "docs: 팀 이름을 깃벗으로 정하기", "kim", ["M"], False),
    "O": ("f08005f", "docs: 팀 이름을 커밋조로 정하기", "lee", ["M"], False),
    "X": ("b13c5dc", "fix: 팀 이름 충돌 해결", "lee", ["O", "N"], True),
}
POS = {"I": (0, 0), "K": (1, 0), "L": (1, 1), "M": (2, 0), "N": (3, 0), "O": (3, 1), "X": (4, 0)}


def repo(keys, moved=None, ghost=""):
    moved = moved or {}
    return [(k, *moved.get(k, POS[k]), False) for k in keys] + [(k, *POS[k], True) for k in ghost]


S_I = repo("I")
S_K = repo("IK")
S_L = repo("IL", {"L": (1, 0)})
S_M = repo("IKLM")
S_N = repo("IKLMN")
S_O = repo("IKLMO", {"O": (3, 0)})
S_NO = repo("IKLMNO")
S_X = repo("IKLMNOX")
F0 = ["README.md"]
FK = ["README.md", "kim.md"]
FL = ["README.md", "lee.md"]
FA = ["README.md", "kim.md", "lee.md"]

# band geometry: four lanes in one row, filled, no outline
LANES = ["gh", "kim", "lee", "park"]
LX = {k: 96 + i * 440 for i, k in enumerate(LANES)}
LW, BT = 408, 172
SLOTS = [4]  # widest commit slot on the slide being drawn, so every lane of one slide uses the same pitch


def lane(who, rep, files, h, active=False, badge=None, arrive=None, pre=""):
    """One lane. arrive = (order, keys, from_lane or None): those dots fly in from the same commit in from_lane
    (or pop in when from_lane is None) on that click, with their edges and the moved main tag."""
    x, y, col = LX[who], BT, PC[who]
    s = min(1.25, max(1.0, (h - 150) / 150))
    D = round(38 * s)
    P = min(round(100 * s), (LW - 68 - D - 40) // max(1, SLOTS[0]))
    L = round(62 * s)
    gx = lambda sl: x + 34 + D // 2 + sl * P
    gy0 = y + 70 + 40 + round((h - 70 - 52 - 40 - L - D) / 2) + D // 2
    gy = lambda ln: gy0 + ln * L
    bg = TINT[who] if (who == "gh" or active) else "#FFFFFF"
    o = [f'<div id="{pre}lane-{who}" style="position:absolute;left:{x}px;top:{y}px;width:{LW}px;height:{h}px;background:{bg};border-radius:20px"></div>',
         f'<div id="{pre}lh-{who}" style="position:absolute;left:{x + 24}px;top:{y + 18}px;width:{LW - 48}px;height:40px;display:flex;flex-direction:row;gap:12px;align-items:center">'
         f'<x-icon name="{PICON[who]}" style="width:30px;height:30px;color:{col}"></x-icon>'
         + p(f"font-size:30px;font-weight:700;line-height:1;color:{col}", PNAME[who])
         + p(f"font-size:20px;line-height:1;color:{MUTE};white-space:nowrap", PSUB[who]) + '</div>']
    if badge:
        o.append(p(f"position:absolute;left:{x + LW - 24 - 112}px;top:{y + 20}px;width:112px;font-size:20px;font-weight:700;line-height:36px;text-align:center;border-radius:18px;color:#FFFFFF;background:{badge[1]}", badge[0], f' id="{pre}badge-{who}"'))
    order, akeys, afrom = arrive if arrive else (None, "", None)
    keys = {k: (sl, ln, g) for k, sl, ln, g in rep}
    for k, (sl, ln, g) in keys.items():
        for par in C[k][3]:
            if par not in keys:
                continue
            ps, pl, pg = keys[par]
            x1, y1, x2, y2 = gx(ps), gy(pl), gx(sl), gy(ln)
            mx, Mx, my, My = min(x1, x2), max(x1, x2), min(y1, y2) - 3, max(y1, y2) + 3
            dash = ' stroke-dasharray="8 7"' if g or pg else ""
            b = bi("fade", order) if k in akeys else ""
            o.append(f'<svg id="{pre}{who}-e-{par}{k}"{b} viewBox="{mx} {my} {Mx - mx} {My - my}" style="position:absolute;left:{mx}px;top:{my}px;width:{Mx - mx}px;height:{My - my}px;overflow:visible">'
                     f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#B9B5AA" stroke-width="5"{dash}/></svg>')
    for k, (sl, ln, g) in keys.items():
        c = PC[C[k][2]]
        bw = max(5, round(D / 6))
        if g:
            st = f"background:#FFFFFF;border:3px dashed {c}"
        elif C[k][4]:
            st = f"background:#FFFFFF;border:{bw}px solid {c}"
        else:
            st = f"background:{c};border:{bw}px solid {c}"
        b = ""
        if k in akeys:
            b = f' data-build-in="fly order {order}" data-from="{pre}{afrom}-d-{k}"' if afrom else bi("pop", order)
        o.append(f'<div id="{pre}{who}-d-{k}"{b} style="position:absolute;left:{gx(sl) - D // 2}px;top:{gy(ln) - D // 2}px;width:{D}px;height:{D}px;border-radius:50%;{st}"></div>')
    tip = [t for t in rep if not t[3]][-1]
    tw = 72 if tip[2] == 0 else 64
    tx_ = gx(tip[1]) - tw // 2 if tip[2] == 0 else gx(tip[1]) + D // 2 + 8
    ty = gy(tip[2]) - D // 2 - 34 if tip[2] == 0 else gy(tip[2]) - 13
    tb = bi("fade", order) if tip[0] in akeys else ""
    o.append(p(f"position:absolute;left:{tx_}px;top:{ty}px;width:{tw}px;font-family:{MONO};font-size:19px;font-weight:700;line-height:26px;text-align:center;border-radius:7px;color:#FFFFFF;background:{INK}", "main", f' id="{pre}{who}-main"{tb}'))
    ghosts = [t for t in rep if t[3]]
    if ghosts:
        gt = ghosts[-1]
        o.append(p(f"position:absolute;left:{min(gx(gt[1]) - 68, x + LW - 24 - 136)}px;top:{gy(gt[2]) - D // 2 - 34}px;width:136px;font-family:{MONO};font-size:18px;font-weight:700;line-height:26px;text-align:center;border-radius:7px;color:#FFFFFF;background:{PUR}", "origin/main", f' id="{pre}{who}-om"' + (bi("fade", order) if gt[0] in akeys else "")))
    if files is not None:
        chips = "".join(p(f"font-family:{MONO};font-size:19px;line-height:32px;padding:0 10px;border-radius:8px;white-space:nowrap;"
                          + (f"color:#FFFFFF;background:{RED}" if f.endswith("!") else f"color:{INK};background:{'#FFFFFF' if bg != '#FFFFFF' else '#EEEFF2'}"), e(f.rstrip("!"))) for f in files)
        o.append(f'<div id="{pre}{who}-files" style="position:absolute;left:{x + 24}px;top:{y + h - 52}px;width:{LW - 48}px;height:32px;display:flex;flex-direction:row;gap:8px">{chips}</div>')
    return o


def band(states, h, active=None, badges=None, arrive=None, pre=""):
    o = []
    SLOTS[0] = max(t[1] for who in LANES for t in states[who][0])
    act = active if isinstance(active, tuple) else (active,)
    for who in LANES:
        rep, files = states[who]
        o += lane(who, rep, files, h, active=who in act, badge=(badges or {}).get(who), arrive=(arrive or {}).get(who), pre=pre)
    return o


def label(lane_key, top_of_band_bottom, text, color, order=None, width=None, kind="pop"):
    """A label on the picture, tied to its lane by a short leader ending in a dot (Stageshow annotations).
    The rightmost lane's label hangs to the left of its leader so it stays inside the slide."""
    right = lane_key == "park"
    x = LX[lane_key] + (LW - 40 if right else 40)
    y0 = top_of_band_bottom + 8
    b = bi(kind, order) if order else ""
    w = width or 900
    tl = x + 8 - w if right else x - 8
    al = "text-align:right;" if right else ""
    return [f'<svg{b} style="position:absolute;left:0;top:0;width:1920px;height:1080px;overflow:visible;pointer-events:none">'
            f'<circle cx="{x}" cy="{y0}" r="5" fill="{color}"/><line x1="{x}" y1="{y0}" x2="{x}" y2="{y0 + 30}" stroke="{color}" stroke-width="2"/></svg>',
            p(f"position:absolute;left:{tl}px;top:{y0 + 32}px;width:{w}px;{al}font-size:28px;font-weight:700;line-height:1.3;color:{color}", text, b)]


def scene(sid, eyebrow, title, states, who, term, notes, labels=(), arrive=None, hot=None, badges=None, color=None, transition="magic", extra=()):
    """labels: (lane, text, color[, width]). hot: (line index, 'ring'|'underline', color) drawn on click 1.
    Order: click 1 = commits fly in (arrive) or the pen mark (hot); labels come with click 1, or click 2 after a pen mark."""
    o = [sec(sid, transition)] + head(eyebrow, title, color or PC[who if isinstance(who, str) else who[0]])
    avail = 1024 - BT
    size = term_fit(term, 1728, 470, cap=32)
    th = term_h(term, size)
    bh = max(290, min(380, avail - th - 110))
    ttop = BT + bh + 110
    size = term_fit(term, 1728, 1024 - ttop, cap=40)
    th = term_h(term, size)
    o += band(states, bh, active=who, badges=badges, arrive=arrive)
    lo = 2 if hot else 1
    for lb in labels:
        o += label(lb[0], BT + bh, lb[1], lb[2], order=lo, width=lb[3] if len(lb) > 3 else None)
    t, _ = terminal(term, who, 96, ttop, 1728, size)
    o += t
    if hot:
        i, kind, c = hot
        x, y, w, h = line_box(96, ttop, term, size, i)
        o.append(box(1, x - 10, y, w + 20, h, c, width=4) if kind == "ring" else underline(1, x, x + w, y + h - 2, c))
    o += list(extra)
    W(sid, o, notes)


def person_dot(who, x, y, size=120, pre=""):
    return (f'<div id="{pre}pd-{who}" style="position:absolute;left:{x}px;top:{y}px;width:{size}px;height:{size}px;border-radius:50%;background:{PC[who]};display:flex;align-items:center;justify-content:center">'
            + p(f"font-size:{round(size * 0.3)}px;font-weight:900;line-height:1;color:#FFFFFF", PNAME[who]) + '</div>')


# =====================================================================
# cover
cov = [f'<section id="cover" data-transition="fade" style="background:#1D2330;color:#F6F5F1;font-family:{SANS};padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#8FB3FF">KANT AX/AI 엔지니어 트랙 · 06</p>',
       '<h1 style="font-size:92px;font-weight:900;line-height:1.2;color:#F6F5F1">팀 레포에서<br>같이 작업하고<br><span'+SLAM(1)+' style="display:inline-block">충돌 풀기</span></h1>',
       '<p style="font-size:36px;line-height:1.45;color:#BFC6D4">셋이 한 저장소에 push하고 pull하다<br>엉키는 순간을 일부러 만들고 풀어 봐요</p>']
cov.append(f'<div style="position:absolute;left:1220px;top:270px;width:520px;height:140px;border-radius:24px;background:#2A3242;display:flex;flex-direction:row;gap:18px;align-items:center;justify-content:center">'
           f'<x-icon name="Cloud" style="width:56px;height:56px;color:#B9A5F5"></x-icon>' + p("font-size:40px;font-weight:700;line-height:1;color:#F6F5F1", "GitHub") + '</div>')
cov.append('<svg style="position:absolute;left:0;top:0;width:1920px;height:1080px;overflow:visible">'
           + "".join(f'<line x1="1480" y1="410" x2="{1240 + i * 190 + 70}" y2="690" stroke="#4A5468" stroke-width="5" stroke-dasharray="12 10"/>' for i in range(3)) + '</svg>')
for i, who in enumerate(["kim", "lee", "park"]):
    cov.append(person_dot(who, 1240 + i * 190, 690, 140, "cv-"))
W("cover", cov, "오늘은 2~3명이 팀을 짜서 GitHub에 팀 레포를 하나 만들어요. 각자 clone해서 커밋하고 push, pull 하다 보면 서로 엉키는 순간이 와요. 그 순간을 일부러 만들어 보고 푸는 게 오늘의 목표예요.")

TOC_PARTS = [(PUR, "팀 레포 준비", "레포 만들기, 초대, clone, pull 설정", "roles", "config"),
             (GR, "다른 파일은 저절로 합쳐져요", "push 거절, pull로 합치기, fast-forward", "a1", "a7"),
             (RED, "같은 줄은 충돌이 나요", "CONFLICT 읽고 고쳐서 다시 push", "b1", "b6"),
             (OR, "팀 규칙", "작업 전 pull, 작게 자주 커밋, 작업 순서", "rules", "cycle"),
             (NAVY, "브랜치로 일할 때 8가지 경우", "브랜치, PR, 충돌, 실수했을 때", "cases", "c8")]

# why
w = [sec("why")] + head("오늘 하는 일", "저장소 하나를 셋이 같이 써요", PUR)
w.append(f'<div id="w-gh" style="position:absolute;left:640px;top:220px;width:640px;height:132px;border-radius:24px;background:{TINT["gh"]};display:flex;flex-direction:row;gap:20px;align-items:center;justify-content:center">'
         f'<x-icon name="Cloud" style="width:56px;height:56px;color:{PUR}"></x-icon>'
         + '<div style="display:flex;flex-direction:column;gap:6px">' + p(f"font-size:36px;font-weight:700;line-height:1.2;color:{PUR}", "GitHub 팀 레포") + p(f"font-family:{MONO};font-size:22px;line-height:1.2;color:{SUB}", "github.com/kim/team-intro") + '</div></div>')
w.append('<svg style="position:absolute;left:0;top:0;width:1920px;height:1080px;overflow:visible">'
         + "".join(f'<line x1="960" y1="352" x2="{cx}" y2="476" stroke="#B9B5AA" stroke-width="5" stroke-dasharray="12 10"/>' for cx in (390, 960, 1530)) + '</svg>')
for i, who in enumerate(["kim", "lee", "park"]):
    cx = 390 + i * 570
    w.append(person_dot(who, cx - 70, 476, 140, "w-"))
    w.append(p(f"position:absolute;left:{cx - 200}px;top:636px;width:400px;font-size:26px;line-height:1.3;text-align:center;color:{SUB}", "clone · commit · push · pull"))
w.append(p(f"position:absolute;left:96px;top:742px;width:1728px;font-size:26px;font-weight:700;line-height:1.3;color:{MUTE}", "오늘 일부러 만나 볼 메시지 셋"))
w.append(hair(96, 790, 1728))
outs = [("! [rejected]", "push가 거절돼요. 먼저 받으라는 뜻이에요.", OR), ("Merge made", "다른 파일은 pull 하면 저절로 합쳐져요.", GR), ("CONFLICT", "같은 줄은 둘 중 하나를 직접 골라요.", RED)]
for i, (code, txt, c) in enumerate(outs):
    x = 96 + i * 588
    if i:
        w.append(f'<div style="position:absolute;left:{x - 20}px;top:820px;width:2px;height:170px;background:{HAIR}"></div>')
    w.append(f'<div{bi("rise", 1)}{DELAY(i * 180)} style="position:absolute;left:{x + (16 if i else 0)}px;top:822px;width:540px;display:flex;flex-direction:column;gap:14px">'
             + p(f"font-family:{MONO};font-size:40px;font-weight:700;line-height:1.2;color:{c}", e(code)) + p(f"font-size:28px;line-height:1.45;color:{INK}", txt) + '</div>')
W("why", w, "GitHub의 저장소 하나를 kim, lee, park 셋이 각자 컴퓨터로 clone해서 써요. 혼자 쓸 때와 달리 남이 먼저 올린 커밋이 생겨요. 그래서 오늘은 세 가지 메시지를 일부러 만나 봐요. push가 거절되는 rejected, pull 하면 저절로 합쳐지는 Merge made, 같은 줄을 고쳐서 생기는 CONFLICT예요. 세 가지 모두 고장이 아니에요. Git이 다음에 할 일을 알려 주는 메시지예요.")

# roles
ro = [sec("roles")] + head("1부 · 팀 레포 준비", "한 명이 팀장이 되고, 나머지는 초대받아요", PUR)
roles = [("kim", "팀장", "GitHub에 레포 만들기<br>팀원 초대하기"), ("lee", "팀원", "초대 수락하기<br>clone 하기"), ("park", "팀원", "초대 수락하기<br>clone 하기")]
for i, (who, role, todo) in enumerate(roles):
    cx = 390 + i * 570
    ro.append(f'<div{bi("rise", 1)}{DELAY(i * 150)} style="position:absolute;left:{cx - 260}px;top:240px;width:520px;display:flex;flex-direction:column;align-items:center;gap:26px">'
              f'<div style="width:240px;height:240px;border-radius:50%;background:{PC[who]};display:flex;align-items:center;justify-content:center">' + p("font-size:64px;font-weight:900;line-height:1;color:#FFFFFF", who) + '</div>'
              + p(f"font-size:48px;font-weight:700;line-height:1.2;color:{PC[who]}", role)
              + p(f"font-size:34px;line-height:1.6;text-align:center;color:{INK}", todo) + '</div>')
ro.append(hair(96, 860, 1728))
ro.append(p(f"position:absolute;left:96px;top:890px;width:1728px;font-size:30px;line-height:1.6;color:{SUB}", "슬라이드의 kim, lee, park 자리에 팀원 이름을 넣어요. 2인 팀이면 park 차례는 건너뛰어요.<br>색은 끝까지 같아요. 파랑 kim, 초록 lee, 주황 park, 보라 GitHub.", bi("fade", 2)))
W("roles", ro, "한 명이 팀장이 돼서 레포를 만들고 나머지를 초대해요. 레포 주인만 처음에 push할 수 있어서 초대가 꼭 필요해요. 이 덱에서 kim은 파랑, lee는 초록, park는 주황, GitHub은 보라로 계속 그려요. 커밋 점의 색이 그 커밋을 만든 사람이에요.")


# new repo
def browser(x, y, w, h, url, pre):
    return [f'<div id="{pre}win" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:#FFFFFF;border-radius:16px;box-shadow:0 0 0 1px #D0D7DE,0 18px 48px rgba(29,35,48,.10);overflow:hidden"></div>',
            f'<div id="{pre}bar" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:58px;background:#F6F8FA;border-bottom:1px solid #D0D7DE;border-radius:16px 16px 0 0;display:flex;flex-direction:row;gap:12px;align-items:center;padding:0 22px">'
            + "".join(f'<div style="width:14px;height:14px;border-radius:7px;background:{c}"></div>' for c in ["#E5534B", "#E3B341", "#3FB950"])
            + f'<div style="margin-left:16px;flex:1;height:36px;border-radius:18px;background:#FFFFFF;border:1px solid #D0D7DE;display:flex;align-items:center;justify-content:center">'
            + p(f"font-family:{MONO};font-size:20px;line-height:1;color:{SUB}", e(url)) + '</div></div>']


def marker(n, x, y, color=OR):
    return (f'<div style="position:absolute;left:{x}px;top:{y}px;width:44px;height:44px;border-radius:22px;background:{color};display:flex;align-items:center;justify-content:center">'
            + p("font-size:24px;font-weight:900;line-height:1;color:#FFFFFF", str(n)) + '</div>')


def steps_list(x, y, w, items, color, start_order=1, gap=150):
    o = []
    for i, (t, sub) in enumerate(items):
        yy = y + i * gap
        if i:
            o.append(hair(x, yy - 24, w))
        o.append(f'<div{bi("rise", start_order + i)} style="position:absolute;left:{x}px;top:{yy}px;width:{w}px;display:flex;flex-direction:row;gap:20px">'
                 + p(f"width:44px;height:44px;flex:none;font-size:24px;font-weight:900;line-height:44px;text-align:center;border-radius:22px;color:#FFFFFF;background:{color}", str(i + 1))
                 + '<div style="display:flex;flex-direction:column;gap:6px">' + p(f"font-size:32px;font-weight:700;line-height:1.35;color:{INK}", t)
                 + (p(f"font-size:24px;line-height:1.45;color:{SUB}", sub) if sub else "") + '</div></div>')
    return o


nr = [sec("new-repo")] + head("1부 · 팀 레포 준비 · kim", "팀장이 GitHub에 레포를 만들어요", BL)
nr += browser(96, 184, 1080, 960, "github.com/new", "nr-")
fx, fy = 156, 284
nr.append(p(f"position:absolute;left:{fx}px;top:{fy}px;width:900px;font-size:36px;font-weight:700;line-height:1.2;color:{GHT}", "Create a new repository"))
nr.append(p(f"position:absolute;left:{fx}px;top:{fy + 84}px;width:200px;font-size:22px;font-weight:700;line-height:1.2;color:{GHT}", "Owner"))
nr.append(p(f"position:absolute;left:{fx + 244}px;top:{fy + 84}px;width:400px;font-size:22px;font-weight:700;line-height:1.2;color:{GHT}", "Repository name"))
nr.append(p(f"position:absolute;left:{fx}px;top:{fy + 122}px;width:200px;font-size:24px;line-height:50px;padding:0 16px;border:1px solid #D0D7DE;border-radius:8px;background:#F6F8FA;color:{GHT}", "kim ▾"))
nr.append(p(f"position:absolute;left:{fx + 214}px;top:{fy + 122}px;width:20px;font-size:30px;line-height:50px;color:{GHS}", "/"))
nr.append(p(f"position:absolute;left:{fx + 244}px;top:{fy + 122}px;width:420px;font-family:{MONO};font-size:26px;line-height:50px;padding:0 16px;border:2px solid #0969DA;border-radius:8px;color:{GHT}", "team-intro", ' id="nr-name"'))
nr.append(p(f"position:absolute;left:{fx}px;top:{fy + 222}px;width:400px;font-size:22px;font-weight:700;line-height:1.2;color:{GHT}", "Visibility"))
nr.append(p(f"position:absolute;left:{fx}px;top:{fy + 260}px;width:420px;font-size:24px;line-height:50px;padding:0 16px;border:1px solid #D0D7DE;border-radius:8px;color:{GHT}", "Public ▾", ' id="nr-vis"'))
nr.append(p(f"position:absolute;left:{fx}px;top:{fy + 360}px;width:400px;font-size:22px;font-weight:700;line-height:1.2;color:{GHT}", "Add README"))
nr.append(f'<div id="nr-tog" style="position:absolute;left:{fx}px;top:{fy + 400}px;width:80px;height:40px;border-radius:20px;background:#1F883D"><div style="position:absolute;left:44px;top:4px;width:32px;height:32px;border-radius:16px;background:#FFFFFF"></div></div>')
nr.append(p(f"position:absolute;left:{fx + 100}px;top:{fy + 402}px;width:200px;font-size:24px;line-height:36px;color:{GHT}", "On"))
nr.append(p(f"position:absolute;left:{fx}px;top:{fy + 560}px;width:280px;font-size:24px;font-weight:700;line-height:56px;text-align:center;border-radius:8px;color:#FFFFFF;background:#1F883D", "Create repository", ' id="nr-create"'))
nr += [marker(1, fx + 684, fy + 125), marker(2, fx + 440, fy + 263), marker(3, fx + 100 + 50, fy + 398), marker(4, fx + 300, fy + 566)]
nr += steps_list(1240, 290, 584, [("이름은 team-intro", "소문자와 하이픈만 써요"), ("Public 그대로", "Private이면 초대한 팀원만 보여요"),
                                   ("Add README를 켜요", "첫 커밋이 생겨서 바로 clone할 수 있어요"), ("Create repository", "주소는 github.com/kim/team-intro")], OR)
nr += [cursor(1, fx + 600, fy + 160), cursor(2, fx + 380, fy + 296), cursor_off(3), zoom(3, fx - 30, fy + 330, 640, 160, pad=30, max_scale=1.8), zoom_off(4),
       cursor(4, fx + 250, fy + 600), cursor_off(5)]
W("new-repo", nr, "오른쪽 위 + 버튼에서 New repository를 눌러요. 02에서는 README 없이 빈 저장소를 만들었어요. 팀 레포는 README를 켜서 만들어요. Initial commit이 하나 생겨서 셋이 바로 clone할 수 있어요. GitHub 화면은 자주 바뀌어요. 체크 상자로 보이면 Add a README file을 체크해요.")

# invite: the settings window leads, the invitation lee sees straddles its right edge
iv = [sec("invite")] + head("1부 · 팀 레포 준비", "kim이 초대하고, 팀원이 수락해요", BL)
iv += browser(96, 184, 1180, 960, "github.com/kim/team-intro/settings/access", "iv1-")
iv.append(p(f"position:absolute;left:144px;top:276px;width:300px;font-size:22px;line-height:1.2;color:{GHS}", "Settings"))
iv.append(f'<div style="position:absolute;left:136px;top:320px;width:240px;display:flex;flex-direction:column;gap:6px">'
          + "".join(p(f"font-size:24px;line-height:46px;padding:0 14px;border-radius:8px;{'font-weight:700;background:#EEF1F4;' if t == 'Collaborators' else ''}color:{GHT}", t) for t in ["General", "Collaborators", "Branches", "Webhooks", "Pages"]) + '</div>')
iv.append(p(f"position:absolute;left:450px;top:322px;width:500px;font-size:32px;font-weight:700;line-height:1.2;color:{GHT}", "Collaborators"))
iv.append(p(f"position:absolute;left:450px;top:392px;width:220px;font-size:22px;font-weight:700;line-height:50px;text-align:center;border-radius:8px;color:#FFFFFF;background:#1F883D", "Add people"))
iv.append(p(f"position:absolute;left:450px;top:484px;width:480px;font-size:26px;line-height:52px;padding:0 16px;border:2px solid #0969DA;border-radius:8px;color:{GHT}", "lee"))
iv.append(p(f"position:absolute;left:450px;top:556px;width:480px;font-size:22px;line-height:1.5;color:{GHS}", "아이디나 이메일로 찾아요.<br>park도 같은 방법으로 한 번 더 해요."))
iv += [marker(1, 388, 378), marker(2, 682, 395), marker(3, 890, 488)]
iv.append(f'<div id="iv-card"{bi("rise", 4)} style="position:absolute;left:1000px;top:400px;width:600px;height:500px;background:#FFFFFF;border-radius:20px;box-shadow:0 0 0 1px #D0D7DE,0 24px 60px rgba(29,35,48,.18);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:26px;padding-top:60px">'
          + p(f"position:absolute;left:28px;top:24px;font-size:24px;font-weight:700;line-height:1;color:{GR}", "lee, park가 보는 화면")
          + p(f"position:absolute;left:28px;top:60px;font-family:{MONO};font-size:18px;line-height:1;color:{GHS}", "github.com/kim/team-intro/invitations")
          + f'<div style="width:110px;height:110px;border-radius:50%;background:{BL};display:flex;align-items:center;justify-content:center">' + p("font-size:34px;font-weight:900;line-height:1;color:#FFFFFF", "kim") + '</div>'
          + p(f"font-size:28px;line-height:1.5;text-align:center;color:{GHT}", "kim invited you to collaborate<br>on <b>kim/team-intro</b>")
          + p(f"width:300px;font-size:24px;font-weight:700;line-height:56px;text-align:center;border-radius:8px;color:#FFFFFF;background:#1F883D", "Accept invitation") + '</div>')
iv += [cursor(1, 330, 392), cursor(2, 640, 420), cursor(3, 850, 512), cursor_off(4), blur(4, "iv-card"), blur_off(5), cursor(5, 1430, 816), cursor_off(6)]
W("invite", iv, "kim은 레포의 Settings에서 Collaborators를 열고 Add people로 팀원 아이디를 넣어요. 초대받은 사람은 GitHub에 가입한 이메일로 온 메일이나 레포 주소 뒤에 /invitations를 붙인 페이지에서 Accept invitation을 눌러요. 수락하지 않으면 clone은 돼도 push할 때 403 오류가 나요.")

# clone: one terminal (the output is the same on all three computers) and the team picture
scene("clone", "1부 · 팀 레포 준비 · 셋 다", "셋이 각자 컴퓨터에 clone해요",
      {"gh": (S_I, None), "kim": (S_I, F0), "lee": (S_I, F0), "park": (S_I, F0)}, ("kim", "lee", "park"),
      [("$", "git clone https://github.com/kim/team-intro.git"), ("o", "Cloning into 'team-intro'..."), ("o", "done."), ("$", "cd team-intro"),
       ("$", "git log --oneline"), ("o", "7f7794e (HEAD -> main, origin/main, origin/HEAD) Initial commit")],
      "레포 주소는 GitHub 레포 화면의 초록색 Code 버튼에서 복사해요. 셋이 같은 주소로 clone하면 Initial commit 하나가 든 똑같은 저장소가 세 개 생겨요. 위 네 칸이 오늘 내내 볼 그림이에요. 점 색은 커밋한 사람이에요. clone한 뒤에는 꼭 cd team-intro로 폴더에 들어가요. 셋의 출력이 같아서 터미널은 하나만 그렸어요. clone 출력 중 remote: 로 시작하는 진행 줄은 뺐어요.",
      labels=[("kim", "셋 다 Initial commit 하나가 든 같은 저장소예요", PUR, 1300)],
      arrive={k: (1, "I", "gh") for k in ("kim", "lee", "park")}, color=PUR, transition="fade")

# config
cf = [sec("config")] + head("1부 · 팀 레포 준비 · 셋 다", "pull 하기 전에 설정을 한 줄 쳐요", RED)
cf.append(f'<div style="position:absolute;left:96px;top:200px;width:1728px;height:160px;background:#1B2029;border-radius:24px;display:flex;flex-direction:row;align-items:center;padding:0 56px">'
          + p(f"font-family:{MONO};font-size:56px;font-weight:700;line-height:1;color:#F2C46D", "git config --global pull.rebase false") + '</div>')
fl = 152 + text_w("git config --global pull.rebase ", 56)
cf.append(underline(1, round(fl), round(fl + text_w("false", 56)), 322, OR))
cf.append(p(f"position:absolute;left:96px;top:392px;width:1728px;font-size:32px;font-weight:700;line-height:1.4;color:{OR}", "false는 합칠 때 merge로 하라는 뜻이에요. 셋 다 처음 한 번만 쳐요.", bi("fade", 1)))
cf.append(f'<div{bi("rise", 2)} style="position:absolute;left:96px;top:520px;width:1728px;height:200px;display:flex;flex-direction:row;gap:56px;align-items:flex-start">'
          + '<div style="display:flex;flex-direction:column;gap:10px">' + p(f"font-family:{MONO};font-size:72px;font-weight:700;line-height:1.1;color:{INK}", "git pull") + p(f"font-size:26px;line-height:1.3;color:{SUB}", "은 두 단계예요") + '</div>'
          + p(f"font-size:72px;font-weight:700;line-height:1.1;color:{MUTE}", "=")
          + '<div style="display:flex;flex-direction:column;gap:10px">' + p(f"font-family:{MONO};font-size:72px;font-weight:700;line-height:1.1;color:{PUR}", "fetch") + p(f"font-size:26px;line-height:1.3;color:{SUB}", "GitHub 커밋 받아 오기") + '</div>'
          + p(f"font-size:72px;font-weight:700;line-height:1.1;color:{MUTE}", "+")
          + '<div style="display:flex;flex-direction:column;gap:10px">' + p(f"font-family:{MONO};font-size:72px;font-weight:700;line-height:1.1;color:{GR}", "merge") + p(f"font-size:26px;line-height:1.3;color:{SUB}", "내 main과 합치기") + '</div></div>')
cf.append(hair(96, 790, 1728))
cf.append(f'<div{bi("rise", 3)} style="position:absolute;left:96px;top:830px;width:1728px;display:flex;flex-direction:row;gap:28px;align-items:flex-start">'
          f'<x-icon name="Warning" style="width:52px;height:52px;color:{RED}"></x-icon>'
          + '<div style="display:flex;flex-direction:column;gap:10px">' + p(f"font-family:{MONO};font-size:30px;font-weight:700;line-height:1.3;color:{RED}", "fatal: Need to specify how to reconcile divergent branches.")
          + p(f"font-size:28px;line-height:1.45;color:{INK}", "설정을 안 하면 오늘 실습 중간에 pull이 이 메시지로 멈춰요. {{pg:nocfg}}쪽에서 다시 봐요.") + '</div></div>')
W("config", cf, "03에서 본 설정이에요. 아직 안 했다면 셋 다 지금 쳐요. 출력은 없어요. --global이라 내 컴퓨터의 모든 저장소에 적용돼서 한 번만 하면 돼요. 이 설정이 없으면 내 main과 GitHub main이 갈라졌을 때 pull이 어떻게 합칠지 물으면서 fatal로 멈춰요. 오늘 실습은 그 상황이 반드시 생겨요. git config --global pull.rebase로 값을 확인할 수 있어요. false가 나오면 된 거예요. rebase는 08에서 다른 합치는 방법과 비교해 봐요.")

# =====================================================================
# part 2: different files
P2 = "2부 · 다른 파일은 저절로"
scene("a1", f"{P2} · kim", "먼저 push한 kim은 그냥 올라가요",
      {"gh": (S_K, None), "kim": (S_K, FK), "lee": (S_I, F0), "park": (S_I, F0)}, "kim",
      [("$", 'echo "안녕하세요, kim이에요" > kim.md'), ("$", "git add kim.md"), ("$", 'git commit -m "docs: kim 자기소개 추가"'),
       ("o", "[main 11f6ff4] docs: kim 자기소개 추가"), ("o", " 1 file changed, 1 insertion(+)"), ("o", " create mode 100644 kim.md"),
       ("$", "git push origin main"), ("o", "To https://github.com/kim/team-intro.git"), ("g", "   7f7794e..11f6ff4  main -> main")],
      "셋이 동시에 각자 파일을 만들기 시작했다고 해요. kim이 조금 빨랐어요. GitHub main이 kim이 clone했을 때 그대로라서 push가 바로 올라가요. 클릭하면 kim의 파란 점이 GitHub 칸으로 날아가요. lee, park 칸은 그대로예요. lee와 park 컴퓨터는 아직 이 커밋을 몰라요.",
      labels=[("gh", "파란 점 하나가 늘었어요", BL), ("lee", "lee와 park은 아직 몰라요", MUTE)],
      arrive={"gh": (1, "K", "kim")}, transition="fade")
scene("a2", f"{P2} · lee", "lee의 push는 거절돼요",
      {"gh": (S_K, None), "kim": (S_K, FK), "lee": (S_L, FL), "park": (S_I, F0)}, "lee",
      [("$", 'echo "안녕하세요, lee예요" > lee.md'), ("$", "git add lee.md"), ("$", 'git commit -m "docs: lee 자기소개 추가"'),
       ("o", "[main a078082] docs: lee 자기소개 추가"), ("$", "git push origin main"), ("o", "To https://github.com/kim/team-intro.git"),
       ("r", " ! [rejected]        main -> main (fetch first)"), ("r", "error: failed to push some refs to 'https://github.com/kim/team-intro.git'"),
       ("#", "hint: ..."), ("#", "hint: 'git pull' before pushing again.")],
      "lee도 커밋하고 push했는데 거절됐어요. GitHub 칸과 lee 칸을 비교해 보세요. GitHub에는 kim의 파란 점이 있는데 lee 컴퓨터에는 없어요. 그대로 올리면 kim의 커밋이 사라지니까 Git이 막는 거예요. hint가 말하듯 먼저 pull 해요. --force로 밀어 올리면 kim의 커밋이 지워져요. 쓰지 않아요. hint는 일부만 옮겼어요.",
      labels=[("lee", "GitHub의 파란 점이 lee 칸에는 없어요", OR, 800)], hot=(6, "ring", RED), extra=[shake(1, "term")])
scene("a3", f"{P2} · lee", "pull 하면 다른 파일이라 저절로 합쳐져요",
      {"gh": (S_K, None), "kim": (S_K, FK), "lee": (S_M, FA), "park": (S_I, F0)}, "lee",
      [("$", "git pull origin main"), ("o", "From https://github.com/kim/team-intro"), ("o", " * branch            main       -> FETCH_HEAD"),
       ("o", "   7f7794e..11f6ff4  main       -> origin/main"), ("g", "Merge made by the 'ort' strategy."), ("o", " kim.md | 1 +"), ("o", " 1 file changed, 1 insertion(+)"),
       ("$", "git log --oneline"), ("o", "3c66163 (HEAD -> main) Merge branch 'main' of https://github.com/kim/team-intro"), ("o", "a078082 docs: lee 자기소개 추가"),
       ("o", "11f6ff4 (origin/main, origin/HEAD) docs: kim 자기소개 추가"), ("o", "7f7794e Initial commit")],
      "pull은 kim의 커밋을 받아 와서 lee의 커밋과 합쳐요. kim은 kim.md, lee는 lee.md만 건드렸으니 Git이 알아서 합쳐요. 03에서 본 merge 커밋과 같은 흰 점이 생겨요. 이 merge 커밋은 아직 lee 컴퓨터에만 있어요. 그래서 다음에 push해야 해요. 중간에 vim이 열리는데 다음 장에서 봐요. pull 출력의 create mode 줄은 뺐어요.",
      labels=[("lee", "흰 점이 kim과 lee의 커밋을 잇는 merge 커밋이에요", GR, 1300)],
      arrive={"lee": (1, "KM", "gh")})

# vim
vm = [sec("vim")] + head(f"{P2} · lee", "pull 하다 이 화면이 열리면 저장하고 닫아요", GR)
VL = [("o", "Merge branch 'main' of https://github.com/kim/team-intro"), ("#", "# Please enter a commit message to explain why this merge is necessary,"),
      ("#", "# especially if it merges an updated upstream into a topic branch."), ("#", "#"), ("#", "# Lines starting with '#' will be ignored, and an empty message aborts"),
      ("#", "# the commit."), ("#", "~"), ("#", "~"), ("o", '".git/MERGE_MSG" 6L')]
vt, vh = terminal(VL, None, 96, 184, 1728, 33)
vm += vt
x, y, ww, hh = line_box(96, 184, VL, 33, 0)
vm.append(underline(1, x, x + ww, y + hh - 2, OR))
vm.append(p(f"position:absolute;left:{x + ww + 36}px;top:{y + 2}px;width:400px;font-size:28px;font-weight:700;line-height:1.3;color:#F2B45A", "이 줄이 메시지예요", bi("fade", 1)))
ky = 184 + vh + 56
for i, (k, t) in enumerate([("Esc", "입력 모드 끝내기"), (":wq", "저장하고 닫기"), ("Enter", "실행")]):
    kx = 96 + i * 300
    vm.append(f'<div{bi("pop", 2)}{DELAY(i * 260)} style="position:absolute;left:{kx}px;top:{ky}px;width:260px;display:flex;flex-direction:column;align-items:center;gap:16px">'
              + p(f"min-width:200px;font-family:{MONO};font-size:52px;font-weight:700;line-height:104px;text-align:center;padding:0 28px;border-radius:16px;background:#FFFFFF;box-shadow:inset 0 -6px 0 #DAD6CC,0 0 0 2px #DAD6CC;color:{INK}", k)
              + p(f"font-size:26px;line-height:1.3;color:{SUB}", t) + '</div>')
    if i < 2:
        vm.append(f'<x-shape kind="arrow-right"{bi("fade", 2)}{DELAY(i * 260 + 130)} style="position:absolute;left:{kx + 266}px;top:{ky + 38}px;width:28px;height:28px;background:#B9B5AA"></x-shape>')
vm.append(p(f"position:absolute;left:1020px;top:{ky + 14}px;width:800px;font-size:30px;font-weight:700;line-height:1.5;color:{INK}", "메시지를 그대로 두고 저장하고 닫으면 pull이 끝나요.", bi("fade", 3)))
W("vim", vm, "pull이 merge 커밋을 만들 때 메시지 편집기가 열려요. 03에서 merge할 때 본 화면과 같아요. 첫 줄이 메시지이고 #으로 시작하는 줄은 무시돼요. 그대로 두고 Esc, :wq, Enter를 치면 닫히면서 pull이 끝나요. VS Code가 편집기로 설정된 사람은 탭이 열려요. 그 탭을 닫으면 돼요. 화면 아래 상태 줄은 사람마다 조금 달라요.")

# no config
nc = [sec("nocfg")] + head(f"{P2} · lee", "설정을 안 했다면 pull이 멈춰요", RED)
NL = [("$", "git pull origin main"), ("o", "From https://github.com/kim/team-intro"), ("o", " * branch            main       -> FETCH_HEAD"),
      ("#", "hint: You have divergent branches and need to specify how to reconcile them."), ("#", "hint: ..."), ("#", "hint:   git config pull.rebase false  # merge"),
      ("#", "hint:   git config pull.rebase true   # rebase"), ("#", "hint:   git config pull.ff only       # fast-forward only"),
      ("#", "hint: ..."), ("r", "fatal: Need to specify how to reconcile divergent branches.")]
nt, nh = terminal(NL, "lee", 96, 184, 1728, 31)
nc += nt
x, y, ww, hh = line_box(96, 184, NL, 31, 9)
nc.append(box(1, x - 10, y, ww + 20, hh, RED, width=4))
for j, (n, cmd, col, note) in enumerate([("1", "git config --global pull.rebase false", RED, "설정을 넣고"), ("2", "git pull origin main", GR, "같은 pull을 다시 쳐요. 앞 장처럼 합쳐져요.")]):
    yy = 184 + nh + 48 + j * 120
    nc.append(f'<div{bi("rise", 2 + j)}{DIM("fix")} style="position:absolute;left:96px;top:{yy}px;width:1728px;height:96px;display:flex;flex-direction:row;gap:24px;align-items:center">'
              + p(f"width:56px;height:56px;flex:none;font-size:30px;font-weight:900;line-height:56px;text-align:center;border-radius:28px;color:#FFFFFF;background:{col}", n)
              + p(f"width:960px;flex:none;font-family:{MONO};font-size:36px;font-weight:700;line-height:96px;padding:0 32px;border-radius:18px;color:#F2C46D;background:#1B2029", cmd)
              + p(f"flex:1;font-size:28px;line-height:1.45;color:{SUB}", note) + '</div>')
W("nocfg", nc, "{{pg:config}}쪽 설정을 건너뛴 사람은 여기서 이 메시지를 봐요. 내 main과 GitHub main에 서로 모르는 커밋이 하나씩 있어서 Git이 merge로 합칠지 rebase로 합칠지 물어요. hint의 첫 번째 설정 줄이 우리가 고르는 merge예요. --global을 붙여 설정하고 같은 pull을 다시 치면 돼요. 멈춘 pull은 커밋도 파일도 바꾸지 않아요. hint 줄은 일부만 옮겼어요.")

scene("a4", f"{P2} · lee", "합친 뒤에 다시 push하면 올라가요",
      {"gh": (S_M, None), "kim": (S_K, FK), "lee": (S_M, FA), "park": (S_I, F0)}, "lee",
      [("$", "git push origin main"), ("o", "To https://github.com/kim/team-intro.git"), ("g", "   11f6ff4..3c66163  main -> main")],
      "pull로 kim의 커밋을 받아 합쳤으니 이번엔 push가 통과해요. lee가 kim의 커밋까지 품고 있어서 GitHub 것을 지우지 않아요. GitHub 칸이 lee 칸과 똑같아졌어요. 거절되면 pull, 합쳐지면 push예요.",
      labels=[("gh", "GitHub이 lee 칸과 같아졌어요", GR, 800)], arrive={"gh": (1, "LM", "lee")})
scene("a5", f"{P2} · kim", "새 커밋이 없는 kim은 fast-forward로 따라와요",
      {"gh": (S_M, None), "kim": (S_M, FA), "lee": (S_M, FA), "park": (S_I, F0)}, "kim",
      [("$", "git pull origin main"), ("o", "From https://github.com/kim/team-intro"), ("o", " * branch            main       -> FETCH_HEAD"), ("o", "   11f6ff4..3c66163  main       -> origin/main"),
       ("o", "Updating 11f6ff4..3c66163"), ("g", "Fast-forward"), ("o", " lee.md | 1 +"), ("o", " 1 file changed, 1 insertion(+)"), ("o", " create mode 100644 lee.md")],
      "kim은 push한 뒤로 커밋한 게 없어요. 받아 온 커밋을 그대로 이어 붙이면 되니까 03에서 본 fast-forward예요. merge 커밋이 새로 생기지 않고 vim도 안 열려요. main 이름표만 앞으로 옮겨요. 이제 kim 폴더에도 lee.md가 생겼어요.",
      labels=[("kim", "main 이름표만 앞으로 옮겨요", BL)], arrive={"kim": (1, "LM", "gh")}, hot=None)
scene("a6", f"{P2} · park", "park은 fetch로 먼저 보고 시작해요",
      {"gh": (S_M, None), "kim": (S_M, FA), "lee": (S_M, FA), "park": (repo("I", ghost="KLM"), F0)}, "park",
      [("$", "git fetch origin"), ("o", "From https://github.com/kim/team-intro"), ("o", "   7f7794e..3c66163  main       -> origin/main"),
       ("$", "git log --oneline"), ("o", "7f7794e (HEAD -> main) Initial commit"), ("$", "git log --oneline origin/main"),
       ("o", "3c66163 (origin/main, origin/HEAD) Merge branch 'main' of https://github.com/kim/team-intro"), ("o", "a078082 docs: lee 자기소개 추가"), ("o", "11f6ff4 docs: kim 자기소개 추가"), ("o", "7f7794e (HEAD -> main) Initial commit")],
      "park은 그동안 쉬고 있었어요. 작업을 시작하기 전에 팀원이 무엇을 올렸는지 먼저 봐요. 02에서 배운 대로 git fetch origin 뒤에 두 log를 비교해요. origin/main 쪽에만 커밋 세 개가 더 있어요. 그림의 점선 점이 그 세 개예요. fetch는 받아만 와서 폴더의 파일은 아직 README.md 하나예요.",
      labels=[("lee", "점선 점은 origin/main에만 있어요. 파일은 그대로예요.", PUR, 820)], arrive={"park": (1, "KLM", "gh")}, extra=[pulse(2, "park-om")])
scene("a7", f"{P2} · park", "pull 하면 넷이 같아져요",
      {"gh": (S_M, None), "kim": (S_M, FA), "lee": (S_M, FA), "park": (S_M, FA)}, "park",
      [("$", "git pull origin main"), ("o", "From https://github.com/kim/team-intro"), ("o", " * branch            main       -> FETCH_HEAD"), ("o", "Updating 7f7794e..3c66163"), ("g", "Fast-forward"),
       ("o", " kim.md | 1 +"), ("o", " lee.md | 1 +"), ("o", " 2 files changed, 2 insertions(+)"), ("o", " create mode 100644 kim.md"), ("o", " create mode 100644 lee.md")],
      "park도 커밋이 없어서 fast-forward로 따라잡아요. 네 칸이 모두 같은 그림이에요. park처럼 작업 전에 pull부터 하면 lee가 겪은 거절을 줄일 수 있어요. 2부에서 기억할 것은 하나예요. 다른 파일을 고쳤다면 pull 한 번으로 저절로 합쳐져요.",
      labels=[("park", "작업 전에 pull 하면 거절 없이 시작해요", GR, 800)], hot=(4, "underline", GR))

# =====================================================================
# part 3: same line
P3 = "3부 · 같은 줄은 충돌"
scene("b1", f"{P3} · kim", "kim이 README.md 첫 줄을 바꿔 먼저 올려요",
      {"gh": (S_N, None), "kim": (S_N, FA), "lee": (S_M, FA), "park": (S_M, FA)}, "kim",
      [("$", "git diff"), ("o", "--- a/README.md"), ("o", "+++ b/README.md"), ("o", "@@ -1 +1 @@"), ("r", "-# team-intro"), ("g", "+# 깃벗 팀"),
       ("$", "git add README.md"), ("$", 'git commit -m "docs: 팀 이름을 깃벗으로 정하기"'), ("o", "[main 0586354] docs: 팀 이름을 깃벗으로 정하기"),
       ("$", "git push origin main"), ("g", "   3c66163..0586354  main -> main")],
      "이번엔 팀 이름을 정해요. kim이 README.md 첫 줄을 # 깃벗 팀으로 바꾸고 push했어요. 04에서 배운 git diff로 바뀐 줄을 확인했어요. 이번에도 kim이 먼저 올려서 그냥 올라가요. diff의 diff --git, index 줄과 push의 To 줄은 뺐어요.",
      labels=[("kim", "첫 줄을 # 깃벗 팀으로 바꿨어요", BL)], arrive={"gh": (1, "N", "kim")}, transition="fade")
scene("b2", f"{P3} · lee", "lee도 같은 줄을 바꿔서 또 거절돼요",
      {"gh": (S_N, None), "kim": (S_N, FA), "lee": (S_O, FA), "park": (S_M, FA)}, "lee",
      [("$", "git diff"), ("r", "-# team-intro"), ("g", "+# 커밋조 팀"), ("$", "git add README.md"), ("$", 'git commit -m "docs: 팀 이름을 커밋조로 정하기"'), ("o", "[main f08005f] docs: 팀 이름을 커밋조로 정하기"),
       ("$", "git push origin main"), ("r", " ! [rejected]        main -> main (fetch first)"), ("r", "error: failed to push some refs to 'https://github.com/kim/team-intro.git'")],
      "lee는 같은 시간에 같은 줄을 # 커밋조 팀으로 바꿨어요. push하면 2부와 똑같이 거절돼요. 순서도 같아요. pull 해요. 다만 이번엔 두 사람이 같은 줄을 서로 다르게 고쳐서 Git이 하나를 고를 수 없어요. diff 머리 줄과 hint 줄은 뺐어요.",
      labels=[("lee", "같은 첫 줄을 # 커밋조 팀으로 바꿨어요", OR, 800)], hot=(2, "underline", OR), extra=[shake(1, "term")])
scene("b3", f"{P3} · lee", "pull 하면 같은 줄이라 CONFLICT가 나요",
      {"gh": (S_N, None), "kim": (S_N, FA), "lee": (S_NO, ["README.md!", "kim.md", "lee.md"]), "park": (S_M, FA)}, "lee",
      [("$", "git pull origin main"), ("o", "From https://github.com/kim/team-intro"), ("o", "   3c66163..0586354  main       -> origin/main"), ("o", "Auto-merging README.md"),
       ("r", "CONFLICT (content): Merge conflict in README.md"), ("r", "Automatic merge failed; fix conflicts and then commit the result."),
       ("$", "git status"), ("o", "You have unmerged paths."), ("o", "  (fix conflicts and run \"git commit\")"), ("o", "  (use \"git merge --abort\" to abort the merge)"), ("r", "\tboth modified:   README.md")],
      "pull이 kim의 커밋을 받아 합치려다 README.md에서 멈췄어요. 두 사람이 같은 줄을 고쳐서예요. 고를 때까지 merge 커밋이 안 생겨요. lee 칸을 보면 두 갈래가 아직 안 이어졌어요. git status가 알려 주듯 파일을 고치고 commit 하면 이어져요. 겁나면 03에서 배운 git merge --abort로 pull 전으로 돌아갈 수 있어요. pull의 * branch 줄은 빼고 status 출력은 일부만 옮겼어요.",
      labels=[("lee", "두 갈래가 아직 안 이어졌어요", RED, 800)], hot=(4, "ring", RED), badges={"lee": ("충돌 중", RED)})

# conflict file: the file leads; the two halves are named on the drawing
cr = [sec("b4")] + head(f"{P3} · lee", "README.md를 열면 두 사람의 줄이 다 들어 있어요", RED)
cr.append(f'<div style="position:absolute;left:96px;top:184px;width:1080px;height:550px;background:#FFFFFF;border-radius:20px;box-shadow:0 0 0 1px {LINE}"></div>')
cr.append(p(f"position:absolute;left:144px;top:212px;width:600px;font-size:22px;line-height:1.2;color:{MUTE}", "README.md"))
ROWS = [("&lt;&lt;&lt;&lt;&lt;&lt;&lt; HEAD", 38, MUTE, None), ("# 커밋조 팀", 52, GR, "#E3F2E9"), ("=======", 38, MUTE, None), ("# 깃벗 팀", 52, BL, "#E6EDFA"),
        ("&gt;&gt;&gt;&gt;&gt;&gt;&gt; 058635425c086372cec6…", 38, MUTE, None)]
yy = 268
RY = []
for t, sz, c, bgc in ROWS:
    hgt = round(sz * 1.6)
    st = f"background:{bgc};padding:0 14px;border-radius:8px;font-weight:700;" if bgc else "padding:0 14px;"
    cr.append(p(f"position:absolute;left:130px;top:{yy}px;width:1010px;font-family:{MONO};font-size:{sz}px;line-height:{hgt}px;{st}color:{c}", t))
    RY.append((yy, hgt))
    yy += hgt + 10
mark_y = [RY[1][0] + RY[1][1] // 2, RY[3][0] + RY[3][1] // 2]
for j, (txt, sub, c) in enumerate([("위는 HEAD, 내 것 (lee)", "pull 하기 전 lee 컴퓨터의 줄", GR), ("아래는 해시, 받아 온 것 (kim)", "GitHub에서 온 커밋 0586354의 줄", BL)]):
    my = mark_y[j]
    cr.append(f'<svg{bi("fade", j + 1)} style="position:absolute;left:0;top:0;width:1920px;height:1080px;overflow:visible;pointer-events:none">'
              f'<circle cx="{620 if j == 0 else 560}" cy="{my}" r="6" fill="{c}"/><line x1="{620 if j == 0 else 560}" y1="{my}" x2="1212" y2="{my}" stroke="{c}" stroke-width="2"/></svg>')
    cr.append(f'<div{bi("fade", j + 1)} style="position:absolute;left:1228px;top:{my - 26}px;width:600px;display:flex;flex-direction:column;gap:6px">'
              + p(f"font-size:32px;font-weight:700;line-height:1.3;color:{c}", txt) + p(f"font-size:24px;line-height:1.4;color:{SUB}", sub) + '</div>')
CB = (116, RY[0][0] - 12, 1044, RY[4][0] + RY[4][1] - RY[0][0] + 24)
cr.append(lspot(1, *CB, RY[0][0] - 6, RY[1][0] + RY[1][1] - RY[0][0] + 12, bar=GR))
cr.append(lspot(2, *CB, RY[2][0] - 6, RY[4][0] + RY[4][1] - RY[2][0] + 12, bar=BL))
cr.append(lspot_off(3))
cr.append(hair(96, 790, 1728))
cr.append(f'<div{bi("rise", 3)} style="position:absolute;left:96px;top:826px;width:1728px;display:flex;flex-direction:row;gap:32px;align-items:flex-start">'
          f'<x-icon name="Chat" style="width:64px;height:64px;color:{RED}"></x-icon>'
          + '<div style="display:flex;flex-direction:column;gap:14px">' + p(f"font-size:40px;font-weight:700;line-height:1.3;color:{INK}", "어느 쪽을 남길지 팀이 말로 정해요")
          + p(f"font-size:30px;line-height:1.5;color:{SUB}", "둘 중 하나, 둘 다, 새 이름 모두 돼요. 정한 내용만 남기고 표시 세 줄(&lt;&lt;&lt;, ===, &gt;&gt;&gt;)은 지워요.") + '</div></div>')
W("b4", cr, "03 충돌 시나리오 5와 같은 모양이에요. 위쪽 HEAD 아래가 lee 자기 것, 아래쪽이 GitHub에서 받아 온 kim의 것이에요. pull로 생긴 충돌은 아래 이름이 브랜치 대신 커밋 해시예요. 해시는 kim의 커밋 0586354예요. 화면에서는 뒤를 줄였어요. 여기서 Git이 대신 정해 줄 수 없으니 팀원과 이야기해서 정해요. 오늘은 깃벗 팀으로 정했다고 해요. VS Code로 열면 Accept Current Change 같은 버튼이 보여요. 눌러도 되고 직접 지워도 돼요.")

scene("b5", f"{P3} · lee", "고쳐서 commit 하면 두 갈래가 이어지고 push가 돼요",
      {"gh": (S_X, None), "kim": (S_N, FA), "lee": (S_X, FA), "park": (S_M, FA)}, "lee",
      [("#", "# README.md를 # 깃벗 팀 한 줄만 남기고 저장"), ("$", "git add README.md"), ("$", 'git commit -m "fix: 팀 이름 충돌 해결"'), ("o", "[main b13c5dc] fix: 팀 이름 충돌 해결"),
       ("$", "git push origin main"), ("o", "To https://github.com/kim/team-intro.git"), ("g", "   0586354..b13c5dc  main -> main"),
       ("$", "git log --oneline"), ("o", "b13c5dc (HEAD -> main, origin/main, origin/HEAD) fix: 팀 이름 충돌 해결"), ("o", "f08005f docs: 팀 이름을 커밋조로 정하기"), ("o", "0586354 docs: 팀 이름을 깃벗으로 정하기")],
      "파일을 고쳐 저장한 뒤 add, commit 하면 멈췄던 merge가 끝나요. 충돌을 푼 커밋도 merge 커밋이라 흰 점이에요. 이번 commit은 -m으로 메시지를 적어서 편집기가 안 열려요. 그다음 push해요. GitHub이 lee 칸과 같아졌어요. kim과 park은 아직 옛 그림이에요. git log 아래쪽 세 줄은 뺐어요.",
      labels=[("gh", "충돌을 푼 커밋도 merge 커밋이라 흰 점이에요", GR, 1260)], arrive={"gh": (1, "OX", "lee")})
scene("b6", f"{P3} · kim, park", "나머지는 pull로 받으면 다시 넷이 같아져요",
      {"gh": (S_X, None), "kim": (S_X, FA), "lee": (S_X, FA), "park": (S_X, FA)}, ("kim", "park"),
      [("#", "# kim"), ("$", "git pull origin main"), ("o", "Updating 0586354..b13c5dc"), ("g", "Fast-forward"),
       ("#", "# park"), ("$", "git pull origin main"), ("o", "Updating 3c66163..b13c5dc"), ("g", "Fast-forward"), ("o", " README.md | 2 +-"), ("$", "cat README.md"), ("o", "# 깃벗 팀")],
      "충돌은 lee 컴퓨터에서만 났어요. 한 사람이 풀고 push하면 나머지는 pull로 받아요. kim과 park은 pull 하면 fast-forward로 따라와요. park은 2부 뒤로 받은 게 없어서 README.md가 바뀌는 게 보여요. 이제 셋 다 # 깃벗 팀이에요. From 줄은 뺐어요.",
      labels=[("kim", "충돌은 한 사람만 풀어요. 나머지는 pull이면 돼요.", INK, 1300)],
      arrive={"kim": (1, "OX", "gh"), "park": (1, "NOX", "gh")}, color=INK)

# =====================================================================
# part 4: rules
ru = [sec("rules")] + head("4부 · 팀 규칙", "오늘 겪은 일에서 나온 규칙 다섯 가지", OR)
RL = [("1", "작업 전에 pull", "git pull origin main부터 쳐요. park처럼 거절 없이 시작해요."),
      ("2", "작게 자주 커밋하고 push", "커밋이 작을수록 충돌도 작아요. 한 커밋에 한 가지만 담아요."),
      ("3", "파일과 줄을 나눠 맡기", "같은 줄은 동시에 고치지 않기로 미리 말해요."),
      ("4", "거절되면 pull, --force는 금지", "--force는 팀원 커밋을 지워요."),
      ("5", "충돌은 같이 보고 정하기", "혼자 지우지 말고 고친 사람에게 물어봐요.")]
for i, (n, t, s) in enumerate(RL):
    y = 200 + i * 164
    if i:
        ru.append(hair(96, y - 18, 1728))
    ru.append(f'<div{bi("rise", i + 1)}{DIM("rule")} style="position:absolute;left:96px;top:{y}px;width:1728px;height:128px;display:flex;flex-direction:row;gap:40px;align-items:center">'
              + p(f"width:80px;flex:none;font-size:72px;font-weight:900;line-height:1;color:{OR}", n)
              + p(f"width:640px;flex:none;font-size:40px;font-weight:700;line-height:1.3;color:{INK}", t) + p(f"flex:1;font-size:30px;line-height:1.45;color:{SUB}", s) + '</div>')
W("rules", ru, "오늘 겪은 일에서 나온 규칙이에요. 1번은 park, 4번은 lee의 첫 push에서 봤어요. 3번은 3부 충돌을 막는 방법이에요. 2번은 충돌이 나더라도 고칠 양을 줄여 줘요. 팀이 처음 모였을 때 누가 어떤 파일을 맡을지 정해 두면 3번이 쉬워요.")

# cycle: five steps on one line, the loop back drawn under them
cy = [sec("cycle")] + head("4부 · 팀 규칙", "한 번 작업할 때 이 순서로 돌아요", OR)
STEPS = [("받기", "git pull origin main", PUR), ("작업", "파일 고치기", INK), ("담기", "git add 파일", GR), ("저장", 'git commit -m "..."', BL), ("올리기", "git push origin main", PUR)]
CX = [96 + 176 + i * 344 for i in range(5)]
for i, (t, cmd, c) in enumerate(STEPS):
    cx = CX[i]
    cy.append(f'<div{bi("rise", 1)}{DELAY(i * 160)} style="position:absolute;left:{cx - 165}px;top:240px;width:330px;display:flex;flex-direction:column;align-items:center;gap:20px">'
              + p(f"width:120px;height:120px;font-size:56px;font-weight:900;line-height:120px;text-align:center;border-radius:60px;color:#FFFFFF;background:{c}", str(i + 1))
              + p(f"font-size:40px;font-weight:700;line-height:1.2;color:{c}", t)
              + p(f"font-family:{MONO};font-size:25px;font-weight:700;line-height:1.4;text-align:center;white-space:nowrap;color:{INK}", e(cmd)) + '</div>')
    if i < 4:
        cy.append(f'<x-shape kind="arrow-right"{bi("fade", 1)}{DELAY(i * 160 + 90)} style="position:absolute;left:{cx + 154}px;top:286px;width:36px;height:28px;background:#B9B5AA"></x-shape>')
cy.append(f'<svg{WIPE(2)} viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;overflow:visible">'
          f'<path d="M{CX[4]},540 L{CX[4]},660 L{CX[0]},660 L{CX[0]},548" fill="none" stroke="{RED}" stroke-width="5" stroke-dasharray="14 10"/>'
          f'<polygon points="{CX[0]},536 {CX[0] - 12},560 {CX[0] + 12},560" fill="{RED}"/></svg>')
cy.append(p(f"position:absolute;left:560px;top:626px;width:800px;font-size:34px;font-weight:700;line-height:68px;text-align:center;color:{RED};background:{BG}", "push가 거절되면 1번으로", bi("fade", 2) + DELAY(300)))
cy.append(hair(96, 780, 1728))
cy.append(f'<div{bi("rise", 3)} style="position:absolute;left:96px;top:820px;width:1728px;display:flex;flex-direction:column;gap:20px">'
          + p(f"font-size:38px;font-weight:700;line-height:1.3;color:{INK}", "pull에서 CONFLICT가 나면")
          + p(f"font-family:{MONO};font-size:32px;line-height:1.5;color:{SUB}", "파일 고치기 → git add 파일 → git commit -m \"fix: ...\" → git push origin main") + '</div>')
W("cycle", cy, "하루에 이 순환을 여러 번 돌아요. push가 거절되면 놀라지 말고 다시 1번 pull로 돌아가요. pull에서 충돌이 나면 3부에서 한 것처럼 고치고 add, commit, push해요.")

# =====================================================================
# part 5: team work cases (tools/cases.sh)
P5 = "5부 · 브랜치로 일할 때"
CASES = [("c1", "작업 시작", "main 받고 새 브랜치 만들기", GR),
         ("c2", "브랜치 push, PR 만들기", "push origin 브랜치, Compare &amp; pull request", GR),
         ("c3", "PR 합친 뒤", "main으로 가서 pull, 브랜치 지우고 다음 브랜치", GR),
         ("c4", "다른 파일 PR 두 개", "둘 다 바로 Merge, 각자 pull", BL),
         ("c5", "같은 줄을 고친 PR 두 개", "내 브랜치에서 pull origin main, 충돌 풀고 다시 push", RED),
         ("c6", "고친 파일이 있는데 pull", "would be overwritten by merge", OR),
         ("c7", "고친 파일이 있는데 checkout", "would be overwritten by checkout", OR),
         ("c8", "main에 커밋해 버림", "push 전이면 브랜치로 옮기기", OR)]
CN = {sid: i + 1 for i, (sid, *_) in enumerate(CASES)}
TAKE_ICON = {GR: "CheckCircle", RED: "Warning", OR: "Warning", BL: "Lightbulb"}


def case(sid, who, title, situ, term, take, notes, hot, tcol=GR, start=False):
    """hot: (line index, 'ring'|'underline'|'spot', colour, n lines). Click 1 marks the line; click 2 brings the take-away."""
    n = CN[re.sub(r"(b|-pr)$", "", sid)]
    o = [sec(sid, "fade" if start else "magic")] + head(f"{P5} · 케이스 {n} · {who}", title, PC[who])
    size = term_fit(term, 1728, 1024 - 226 - 96, cap=44)
    th = term_h(term, size)
    # situation, terminal and take-away read as one block; a short terminal moves the block down a little
    # instead of leaving an empty band under it
    slack = 1024 - 226 - th - 96
    shift = max(0, slack // 2)
    o.append(p(f"position:absolute;left:96px;top:{160 + shift}px;width:1728px;font-size:28px;line-height:1.4;color:{SUB}", situ, ' id="situ"'))
    top = 226 + shift
    t, th = terminal(term, who, 96, top, 1728, size)
    o += t
    i, kind, c, nl = hot
    x, y, w, h = line_box(96, top, term, size, i)
    if kind == "ring":
        o.append(box(1, x - 10, y, w + 20, h, c, width=4))
    elif kind == "underline":
        o.append(underline(1, x, x + w, y + h - 2, c))
    elif kind == "lspot":
        tb = (96, top + T_PAD + T_HEAD - 6, 1728, th - T_PAD - T_HEAD)
        for k, (li, ln) in enumerate(nl):
            ly = line_box(96, top, term, size, li)[1]
            o.append(lspot(k + 1, *tb, ly - 2, ln * size * T_LH + 4, bg="#1B2029", bar=c))
        o.append(lspot_off(len(nl) + 1))
    else:
        ws = [line_box(96, top, term, size, j)[2] for j in range(i, i + nl)]
        o.append(spot(1, 96 + 20, y - 4, max(ws) + (x - 96 - 20) + 24, h * nl + 8, pad=6, r=12, dim=0.5))
        o.append(spot_off(2))
    ty = top + th + 30
    o.append(f'<div id="take"{bi("rise", len(nl) + 1 if kind == "lspot" else 2)} style="position:absolute;left:96px;top:{ty}px;width:1728px;display:flex;flex-direction:row;gap:24px;align-items:flex-start">'
             f'<x-icon name="{TAKE_ICON[tcol]}" style="width:48px;height:48px;color:{tcol}"></x-icon>' + p(f"font-size:32px;font-weight:700;line-height:1.5;color:{INK}", take) + '</div>')
    W(sid, o, notes)


def pr_page(sid, title, num, author, branch, ok, notes, n):
    o = [sec(sid)] + head(f"{P5} · 케이스 {n} · GitHub", title, PC[author])
    o += browser(96, 184, 1728, 960, f"github.com/kim/team-intro/pull/{num}", f"{sid}-")
    o.append(p(f"position:absolute;left:160px;top:290px;width:1600px;font-size:40px;line-height:1.2;color:{GHT}", f"<b>{e(branch)}</b> <span style='color:{GHS}'>#{num}</span>"))
    o.append(f'<div style="position:absolute;left:160px;top:362px;width:1600px;height:44px;display:flex;flex-direction:row;gap:14px;align-items:center">'
             + p(f"font-size:22px;font-weight:700;line-height:40px;padding:0 18px;border-radius:20px;color:#FFFFFF;background:#1F883D", "Open")
             + p(f"font-size:24px;line-height:1;color:{GHS}", f"{author} wants to merge 1 commit into")
             + p(f"font-family:{MONO};font-size:22px;line-height:36px;padding:0 10px;border-radius:6px;color:#0969DA;background:#DDF4FF", "main")
             + p(f"font-size:24px;line-height:1;color:{GHS}", "from")
             + p(f"font-family:{MONO};font-size:22px;line-height:36px;padding:0 10px;border-radius:6px;color:#0969DA;background:#DDF4FF", e(branch)) + '</div>')
    # the PR page's own tabs, then the merge box at reading size; the comment field below runs off the crop
    tabs = ["Conversation", "Commits", "Checks", "Files changed"]
    o.append(f'<div style="position:absolute;left:96px;top:486px;width:1728px;height:2px;background:#D0D7DE"></div>')
    tx = 160
    for k, tname in enumerate(tabs):
        tw = round(len(tname) * 13.5) + 8
        o.append(p(f"position:absolute;left:{tx}px;top:{446}px;width:{tw}px;font-size:24px;line-height:1;{'font-weight:700;' if k == 0 else ''}color:{GHT if k == 0 else GHS}", tname))
        if k == 0:
            o.append(f'<div style="position:absolute;left:{tx - 4}px;top:{482}px;width:{tw + 8}px;height:4px;border-radius:2px;background:#FD8C73"></div>')
        tx += tw + 48
    bc = "#1F883D" if ok else "#D1242F"
    head_txt = "✓ This branch has no conflicts with the base branch" if ok else "✕ This branch has conflicts that must be resolved"
    sub_txt = "Merging can be performed automatically." if ok else "Conflicting files: README.md"
    btn = "color:#FFFFFF;background:#1F883D" if ok else "color:#8C959F;background:#F6F8FA;box-shadow:inset 0 0 0 1px #D0D7DE"
    BX, BY = 160, 530
    o.append(f'<div style="position:absolute;left:{BX}px;top:{BY}px;width:1600px;height:330px;border:2px solid {bc};border-radius:12px;padding:40px 44px;display:flex;flex-direction:column;gap:20px">'
             + p(f"font-size:38px;font-weight:700;line-height:1.3;color:{GHT}", head_txt, f' id="{sid}-head"')
             + p(f"font-size:28px;line-height:1.3;color:{GHS}", sub_txt)
             + p(f"width:380px;margin-top:16px;font-size:30px;font-weight:700;line-height:72px;text-align:center;border-radius:8px;{btn}", "Merge pull request") + '</div>')
    by = BY + 2 + 40 + round(38 * 1.3) + 20 + round(28 * 1.3) + 20 + 16
    msg = "누르면 GitHub main에 merge 커밋이 생겨요" if ok else "버튼이 막혀요. 내 컴퓨터에서 main을 받아 풀고 다시 push해요."
    o.append(p(f"position:absolute;left:{BX + 46 + 380 + 36}px;top:{by + 16}px;width:1100px;font-size:30px;font-weight:700;line-height:1.35;color:{GR if ok else RED}", msg, bi("fade", 2)))
    o.append(p(f"position:absolute;left:{BX}px;top:910px;width:600px;font-size:26px;font-weight:700;line-height:1;color:{GHT}", "Add a comment"))
    o.append(f'<div style="position:absolute;left:{BX}px;top:956px;width:1600px;height:240px;border:1px solid #D0D7DE;border-radius:12px;background:#F6F8FA"></div>')
    if ok:
        o += [cursor(1, BX + 46 + 330, by + 50), cursor_off(3)]
    else:
        hw = round(len(head_txt) * 38 * 0.55)
        o += [zoom(1, BX, BY, 1600, 200, pad=40, max_scale=2), zoom_off(2), box(2, BX + 30, BY + 34, hw + 30, 62, RED, width=4)]
    W(sid, o, notes)


case("c1", "lee", "일을 시작할 땐 main을 받고 새 브랜치를 만들어요", "06 실습을 마친 팀이 이제 각자 브랜치에서 일해요. lee가 자기소개를 쓰려고 해요.",
     [("$", "git checkout main"), ("o", "Already on 'main'"), ("o", "Your branch is up to date with 'origin/main'."),
      ("$", "git pull origin main"), ("o", "From https://github.com/kim/team-intro"), ("o", " * branch            main       -> FETCH_HEAD"), ("o", "Already up to date."),
      ("$", "git checkout -b feature/lee-intro"), ("g", "Switched to a new branch 'feature/lee-intro'")],
     "순서는 늘 같아요. main으로 가서 pull, 그다음 새 브랜치.",
     "브랜치를 만들기 전에 main을 최신으로 맞추는 게 첫 단계예요. 오래된 main에서 브랜치를 만들면 팀원이 이미 합친 내용 없이 시작해서 나중에 충돌이 나기 쉬워요. 03 7부의 순서와 같아요. 이 파트의 출력은 tools/cases.sh로 새 저장소에서 실제로 실행했어요. README.md는 # 깃벗 팀, 소개: 준비 중, ## 멤버 세 부분으로 시작해요. 해시는 06 앞 파트와 달라요.",
     (0, "lspot", GR, [(0, 3), (3, 4), (7, 2)]), start=True)
case("c2", "lee", "커밋하고 내 브랜치를 push해요", "lee.md를 만들어 커밋했어요. main이 아니라 feature/lee-intro를 올려요.",
     [("$", 'echo "안녕하세요, lee예요" > lee.md'), ("$", "git add lee.md"), ("$", 'git commit -m "docs: lee 자기소개 추가"'),
      ("o", "[feature/lee-intro 6fb7cc2] docs: lee 자기소개 추가"), ("o", " 1 file changed, 1 insertion(+)"), ("o", " create mode 100644 lee.md"),
      ("$", "git push origin feature/lee-intro"), ("o", "To https://github.com/kim/team-intro.git"), ("g", " * [new branch]      feature/lee-intro -> feature/lee-intro")],
     "push origin 뒤에 브랜치 이름을 적어요. GitHub에 같은 이름 브랜치가 생겨요.",
     "main 대신 내 브랜치 이름을 적어서 push해요. 브랜치는 내 것이라 거절될 일이 거의 없어요. 실제 GitHub은 이 출력 사이에 remote: Create a pull request for 'feature/lee-intro' on GitHub by visiting: 줄과 주소를 함께 보여 줘요. 그 주소를 열거나 GitHub 레포 화면의 노란 Compare & pull request 버튼을 눌러 PR을 만들어요.",
     (8, "underline", GR, 1))
pr_page("c2-pr", "PR을 만들면 GitHub이 합칠 수 있는지 알려 줘요", 1, "lee", "feature/lee-intro", True,
        "PR 제목과 설명을 적고 Create pull request를 누르면 이 화면이 돼요. 초록 체크는 main과 충돌이 없다는 뜻이에요. 팀원이 Files changed 탭에서 바뀐 내용을 보고 괜찮으면 Merge pull request를 눌러요. GitHub 화면은 자주 바뀌어서 모양은 조금 다를 수 있어요.", 2)
case("c3", "lee", "PR이 합쳐지면 main을 받고 다음 브랜치로 가요", "kim이 lee의 PR #1을 Merge했어요. lee 컴퓨터의 main은 아직 옛날 그대로예요.",
     [("$", "git checkout main"), ("o", "Switched to branch 'main'"), ("$", "git pull origin main"), ("o", "   93715e4..ec7283e  main       -> origin/main"), ("o", "Updating 93715e4..ec7283e"), ("g", "Fast-forward"), ("o", " lee.md | 1 +"),
      ("$", "git branch -d feature/lee-intro"), ("o", "Deleted branch feature/lee-intro (was 6fb7cc2)."),
      ("$", "git checkout -b feature/lee-hobby"), ("g", "Switched to a new branch 'feature/lee-hobby'"),
      ("$", "git log --oneline"), ("o", "ec7283e (HEAD -> feature/lee-hobby, ..., main) Merge pull request #1 from lee/feature/lee-intro")],
     "합쳐진 브랜치는 지우고, 다음 일은 최신 main에서 새 브랜치로 시작해요.",
     "PR은 GitHub에서 합쳐져서 내 컴퓨터 main은 모르는 상태예요. main으로 가서 pull 하면 Merge pull request #1 커밋까지 받아요. 다 쓴 브랜치는 git branch -d로 지워요. 이미 합쳐져서 지워도 내용은 main에 남아요. pull의 From 줄과 log의 이름표 일부는 줄였어요. 03 7부와 같은 순서예요.",
     (7, "spot", GR, 2))
case("c4", "kim", "다른 파일을 고친 PR 두 개는 둘 다 바로 합쳐져요", "kim은 kim.md, lee는 lee.md를 고쳐서 PR #2, #3을 올렸어요. 둘 다 No conflicts예요.",
     [("#", "# GitHub에서 PR #2, #3을 차례로 Merge"), ("$", "git checkout main"), ("$", "git pull origin main"), ("o", "Updating ec7283e..09e7497"), ("g", "Fast-forward"),
      ("o", " kim.md | 1 +"), ("o", " lee.md | 1 +"), ("o", " 2 files changed, 2 insertions(+)"),
      ("$", "git log --oneline"), ("o", "09e7497 (HEAD -> main, origin/main, origin/HEAD) Merge pull request #3 from lee/feature/lee-hobby"),
      ("o", "4da19b6 Merge pull request #2 from kim/feature/kim-intro")],
     "PR 순서와 상관없이 둘 다 Merge돼요. 끝나면 각자 main에서 pull 해요.",
     "2부의 다른 파일 장면을 브랜치로 한 거예요. GitHub이 #2를 합친 뒤에도 #3은 다른 파일만 고쳐서 바로 합칠 수 있어요. 둘 다 합친 뒤 kim과 lee 모두 main으로 가서 pull 해요. lee 쪽 출력도 같아요. pull의 From 줄과 log 아래 세 줄은 뺐어요.",
     (9, "spot", BL, 2), tcol=GR)
pr_page("c5-pr", "같은 줄을 고친 PR은 Merge 버튼이 막혀요", 5, "lee", "feature/team-about-lee", False,
        "kim의 PR #4가 README.md의 소개 줄을 깃 공부 모임으로 바꿔 먼저 합쳐졌어요. lee도 같은 줄을 매주 화요일 스터디로 바꿔 PR #5를 올렸어요. GitHub이 충돌을 알려 주고 Merge 버튼을 막아요. GitHub 웹에서 Resolve conflicts로 풀 수도 있지만 수업에서는 3부처럼 터미널에서 풀어요.", 5)
case("c5", "lee", "내 브랜치에서 main을 받아 충돌을 풀어요", "lee는 feature/team-about-lee 브랜치에 그대로 있어요. 여기로 GitHub main을 받아 와요.",
     [("$", "git pull origin main"), ("o", "   09e7497..66421a6  main       -> origin/main"), ("o", "Auto-merging README.md"), ("r", "CONFLICT (content): Merge conflict in README.md"),
      ("$", "cat README.md"), ("o", "# 깃벗 팀"), ("o", ""), ("o", "<<<<<<< HEAD"), ("g", "소개: 매주 화요일 스터디"), ("o", "======="), ("o", "소개: 깃 공부 모임"), ("o", ">>>>>>> 66421a6213c2e39598e99a657405f57421cbd26d"), ("o", ""), ("o", "## 멤버")],
     "checkout main 하지 않고 내 브랜치에서 git pull origin main을 쳐요. 충돌은 3부와 똑같이 읽어요.",
     "충돌을 푸는 곳은 PR을 올린 내 브랜치예요. checkout main 하지 않고 그대로 git pull origin main을 쳐서 GitHub main을 내 브랜치로 합쳐요. 위 HEAD가 lee 것, 아래가 main에 먼저 들어간 kim 것이에요. From 줄은 뺐어요.",
     (3, "ring", RED, 1), tcol=RED)
case("c5b", "lee", "고쳐서 같은 브랜치로 다시 push하면 PR이 살아나요", "둘을 합쳐 소개: 매주 화요일 깃 공부 모임으로 정했어요.",
     [("#", "# README.md를 고쳐 저장"), ("$", "git add README.md"), ("$", 'git commit -m "fix: 팀 소개 충돌 해결"'), ("o", "[feature/team-about-lee da0214b] fix: 팀 소개 충돌 해결"),
      ("$", "git push origin feature/team-about-lee"), ("o", "To https://github.com/kim/team-intro.git"), ("g", "   af3284d..da0214b  feature/team-about-lee -> feature/team-about-lee"),
      ("#", "# PR #5가 다시 초록색이 되면 Merge, 그다음 모두 main에서 pull")],
     "같은 브랜치로 push하면 열린 PR에 커밋이 더해지고, Merge 버튼이 다시 살아나요.",
     "새 PR을 만들 필요 없어요. 같은 브랜치에 push하면 PR #5에 해결 커밋이 붙고 충돌 표시가 사라져요. Merge한 뒤에는 케이스 3처럼 모두 main으로 가서 pull 해요.",
     (6, "underline", GR, 1))
case("c6", "lee", "고친 파일이 있는데 pull 하면 멈춰요", "lee가 main에서 README.md에 - lee를 적고 커밋 전이에요. 그사이 kim의 - kim이 main에 합쳐졌어요.",
     [("$", 'echo "- lee" >> README.md'), ("$", "git pull origin main"), ("o", "   2647d0e..1ef2620  main       -> origin/main"),
      ("r", "error: Your local changes to the following files would be overwritten by merge:"), ("r", "\tREADME.md"), ("o", "Please commit your changes or stash them before you merge."), ("o", "Aborting")],
     "pull이 내 고친 내용을 덮을까 봐 멈췄어요. 아무것도 바뀌지 않았으니 먼저 커밋해요.",
     "커밋하지 않은 README.md를 GitHub 쪽에서도 바꿔서 pull이 시작도 안 하고 멈춰요. Aborting은 pull을 취소했다는 뜻이라 내 고친 내용은 그대로 있어요. 메시지의 stash는 커밋하지 않고 잠깐 치워 두는 방법이에요. 07에서 배워요. 여기서는 브랜치를 만들어 커밋하는 길로 가요. From 줄은 뺐어요.",
     (3, "ring", OR, 1), tcol=OR)
case("c6b", "lee", "브랜치를 만들어 커밋하면 pull이 진행돼요", "main에서 고치고 있었으니 브랜치를 만들어 거기에 커밋해요. 고친 내용은 따라와요.",
     [("$", "git checkout -b feature/lee-member"), ("o", "Switched to a new branch 'feature/lee-member'"), ("$", "git add README.md"), ("$", 'git commit -m "docs: 멤버에 lee 추가"'),
      ("o", "[feature/lee-member 2e4ddbd] docs: 멤버에 lee 추가"), ("$", "git pull origin main"), ("o", "Auto-merging README.md"), ("r", "CONFLICT (content): Merge conflict in README.md"),
      ("o", "Automatic merge failed; fix conflicts and then commit the result.")],
     "이번엔 둘 다 맨 끝 줄에 적어서 충돌이 났어요. 케이스 5처럼 풀어요.",
     "checkout -b는 커밋하지 않은 변경을 새 브랜치로 그대로 가져가요. 커밋한 뒤 pull은 정상으로 진행돼요. kim과 lee가 둘 다 파일 맨 끝에 한 줄을 더해서 같은 자리라 충돌이 났어요. - kim과 - lee 두 줄을 다 남기고 add, commit, push origin feature/lee-member 해요. 충돌이 안 나면 바로 push하면 돼요. From 줄은 뺐어요.",
     (7, "ring", RED, 1), tcol=RED)
case("c7", "kim", "고친 파일이 있는데 브랜치를 옮기면 멈춰요", "kim이 feature/kim-hobby에서 kim.md를 더 고쳤는데 커밋 전에 main으로 가려고 해요.",
     [("$", 'echo "좋아하는 음식: 김밥" >> kim.md'), ("$", "git checkout main"), ("r", "error: Your local changes to the following files would be overwritten by checkout:"), ("r", "\tkim.md"),
      ("o", "Please commit your changes or stash them before you switch branches."), ("o", "Aborting"),
      ("$", "git add kim.md"), ("$", 'git commit -m "docs: kim 좋아하는 음식 추가"'), ("o", "[feature/kim-hobby 1cd6246] docs: kim 좋아하는 음식 추가"),
      ("$", "git checkout main"), ("g", "Switched to branch 'main'")],
     "옮기기 전에 지금 브랜치에서 커밋해요. stash로 치워 두는 법은 07에서 배워요.",
     "옮겨 갈 main의 kim.md와 지금 고친 kim.md가 달라서 checkout이 멈췄어요. 03 문제 해결 표의 would be overwritten by checkout과 같아요. 지금 브랜치에서 커밋하면 옮길 수 있어요. 아직 덜 된 작업이면 07의 stash가 맞아요.",
     (2, "ring", OR, 1), tcol=OR)
case("c8", "kim", "main에 커밋했는데 아직 push 전이면 브랜치로 옮겨요", "브랜치를 깜빡하고 main에서 커밋했어요. 아직 push는 안 했어요.",
     [("$", 'git commit -m "docs: 다음 모임 날짜 추가"'), ("o", "[main 0af5f5a] docs: 다음 모임 날짜 추가"),
      ("$", "git branch feature/next-meeting"), ("#", "# 지금 커밋에 브랜치 이름표를 하나 더 붙여요"),
      ("$", "git status"), ("o", "Your branch is ahead of 'origin/main' by 1 commit."), ("o", "nothing to commit, working tree clean"),
      ("$", "git reset --hard HEAD~1"), ("o", "HEAD is now at 1ef2620 Merge pull request #6 from kim/feature/kim-member"),
      ("$", "git checkout feature/next-meeting"), ("$", "git log --oneline"),
      ("o", "0af5f5a (HEAD -> feature/next-meeting) docs: 다음 모임 날짜 추가"), ("o", "1ef2620 (origin/main, origin/HEAD, main) Merge pull request #6 ...")],
     "branch로 이름표를 붙이고, main만 한 칸 되돌리고, 그 브랜치로 옮겨요. push한 뒤라면 팀에 먼저 알려요.",
     "커밋은 그대로 두고 이름표만 옮기는 방법이에요. git branch 이름은 지금 커밋에 새 이름표만 붙여요. 그다음 main을 03에서 배운 reset --hard로 한 칸 되돌려요. --hard는 커밋 안 한 변경을 지우니 git status가 깨끗한지 먼저 봐요. 마지막으로 새 브랜치로 옮기면 커밋이 거기 있어요. 이미 push했다면 되돌리지 말고 팀에 말한 뒤 revert를 써요. echo, add 줄과 status의 On branch main 줄, 안내 줄, 마지막 log의 아래 줄들은 뺐어요.",
     (2, "lspot", BL, [(2, 2), (7, 2), (9, 4)]), tcol=BL)

# cheatsheet: five columns split by hairlines
ch = [sec("cheatsheet")] + [f'<h2 style="position:absolute;left:96px;top:72px;width:1728px;font-size:56px;font-weight:700;line-height:1.2;color:{INK}">한 장 요약</h2>']
cards = [("준비", PUR, "팀장: 레포 만들기<br>Add README 켜기<br>Collaborators 초대<br><br>팀원: 초대 수락<br>git clone 주소"),
         ("설정 한 번", RED, "git config --global<br>pull.rebase false<br><br>안 하면<br>pull이 fatal로 멈춤"),
         ("다른 파일", GR, "push 거절<br>→ git pull origin main<br>→ 저절로 합쳐짐<br>→ git push origin main"),
         ("같은 줄", BL, "CONFLICT<br>→ 남길 줄만 두고<br>표시 세 줄 지우기<br>→ git add 파일<br>→ git commit -m<br>→ git push origin main"),
         ("브랜치로", NAVY, "main에서 pull<br>→ checkout -b<br>→ push origin 내 브랜치<br>→ PR Merge<br>→ main에서 pull<br><br>막히면 {{pg:finder}}쪽")]
cw = (1728 - 4 * 48) / 5
for i, (h_, hc, body) in enumerate(cards):
    x = round(96 + i * (cw + 48))
    if i:
        ch.append(f'<div style="position:absolute;left:{x - 25}px;top:200px;width:2px;height:680px;background:{HAIR}"></div>')
    ch.append(f'<div{bi("rise", 1)}{DELAY(i * 120)} style="position:absolute;left:{x}px;top:204px;width:{round(cw)}px;display:flex;flex-direction:column;gap:22px">'
              f'<h3 style="font-size:36px;font-weight:700;line-height:1.2;color:{hc}">{h_}</h3>'
              f'<p style="font-size:28px;line-height:1.7;color:{INK}">{body}</p></div>')
ch.append(hair(96, 920, 1728))
ch.append(p(f"position:absolute;left:96px;top:948px;width:1728px;font-size:32px;font-weight:700;line-height:1.3;color:{INK}", "작업 전에 pull, 작게 자주 커밋, 거절되면 다시 pull."))
W("cheatsheet", ch, "수업 끝에 이 장을 띄워 두고 팀별로 오늘 몇 번 거절됐는지, 충돌은 몇 번 풀었는지 이야기해 보게 하세요. 시간이 남으면 역할을 바꿔서 lee가 먼저 push하고 kim이 충돌을 풀어 봐요.")

# final order: toc after cover, case list and finder before the first case
ORDER.insert(1, "toc")
ORDER.insert(ORDER.index("c1"), "cases")
ORDER.insert(ORDER.index("c1"), "finder")
pg = lambda sid: ORDER.index(sid) + 1

# case list (the next-step slide folded in: today was main only, real teams use branches)
cl5 = [sec("cases")] + head(P5, "브랜치로 일할 때 자주 만나는 8가지", NAVY)
cl5.append(p(f"position:absolute;left:96px;top:160px;width:1728px;font-size:28px;line-height:1.45;color:{SUB}", "오늘은 main 하나에 바로 push했어요. 실제 팀은 feature/이름 브랜치에서 일하고 Pull Request로 합쳐요."))
GROUPS = [("매번 하는 순서", 0, 3, 96), ("합칠 때", 3, 5, 96), ("실수했을 때", 5, 8, 984)]
gy_ = {"매번 하는 순서": 256, "합칠 때": 256 + 70 + 3 * 116 + 24, "실수했을 때": 256}
for gname, a, b, gx_ in GROUPS:
    y0 = gy_[gname]
    cl5.append(p(f"position:absolute;left:{gx_}px;top:{y0}px;width:840px;font-size:24px;font-weight:700;line-height:1.2;color:{MUTE}", gname, bi("fade", 1 if gx_ == 96 else 2)))
    for j, idx in enumerate(range(a, b)):
        sid, h, sub, c = CASES[idx]
        yy = y0 + 46 + j * 116
        cl5.append(hair(gx_, yy, 840))
        cl5.append(f'<div{bi("rise", 1 if gx_ == 96 else 2)} style="position:absolute;left:{gx_}px;top:{yy + 18}px;width:840px;height:80px;display:flex;flex-direction:row;gap:24px;align-items:center">'
                   + p(f"width:52px;height:52px;flex:none;font-size:26px;font-weight:900;line-height:52px;text-align:center;border-radius:26px;color:#FFFFFF;background:{c}", str(idx + 1))
                   + '<div style="flex:1;display:flex;flex-direction:column;gap:6px">' + p(f"font-size:32px;font-weight:700;line-height:1.2;color:{INK}", h) + p(f"font-size:23px;line-height:1.3;color:{SUB}", sub) + '</div>'
                   + p(f"width:90px;flex:none;font-size:26px;font-weight:700;line-height:1;text-align:right;color:{NAVY}", f"{pg(sid)}쪽") + '</div>')
cl5.append(p(f"position:absolute;left:984px;top:{256 + 46 + 3 * 116 + 40}px;width:840px;font-size:26px;line-height:1.5;color:{SUB}", "처음부터 다 보지 않아도 돼요.<br>막혔을 때 다음 장에서 메시지로 찾아요.", bi("fade", 2)))
W("cases", cl5, "실제 팀은 main에 바로 push하지 않고 각자 브랜치에서 일하고 Pull Request로 합쳐요. 그 흐름의 자세한 설명은 03 브랜치 덱의 7부에 있어요. 그때 자주 만나는 경우를 여덟 가지로 나눴어요. 1~3은 매번 하는 순서, 4~5는 합칠 때, 6~8은 실수했을 때예요. 처음부터 다 보지 않아도 돼요. 막혔을 때 다음 장에서 메시지로 찾아 해당 케이스만 봐요. 출력은 kim과 lee 두 사람으로 tools/cases.sh에서 실제로 실행했어요.", add=False)

# finder
FIND = [("! [rejected] main -> main (fetch first)", "main에 바로 push했는데 GitHub이 앞서요", "a2"),
        ("fatal: Need to specify how to reconcile ...", "pull 설정이 없어요", "nocfg"),
        ("pull 하다가 vim이 열려요", "merge 커밋 메시지 화면", "vim"),
        ("CONFLICT (content) (main에서 pull)", "같은 줄을 둘 다 고쳤어요", "b3"),
        ("Pulling is not possible because you have unmerged files.", "충돌을 덜 풀고 또 pull", "b4"),
        ("This branch has conflicts (PR 화면)", "PR이 main과 같은 줄을 고쳤어요", "c5-pr"),
        ("would be overwritten by merge", "커밋 안 한 파일이 있는데 pull", "c6"),
        ("would be overwritten by checkout", "커밋 안 한 파일이 있는데 브랜치 이동", "c7"),
        ("PR이 합쳐졌는데 내 main이 옛날 그대로", "GitHub에서 합친 건 pull해야 받아요", "c3"),
        ("main에 커밋해 버렸어요", "push 전이면 브랜치로 옮겨요", "c8"),
        ("Permission to kim/team-intro.git denied (403)", "초대를 아직 수락하지 않았어요", "invite")]
fd = [sec("finder")] + head(P5, "막혔을 때 어느 장을 볼까요?", NAVY)
for i, (msg, why_, sid) in enumerate(FIND):
    yy = 184 + i * 76
    fd.append(hair(96, yy, 1728))
    fd.append(f'<div{bi("rise", 1)}{DELAY(i * 60)} style="position:absolute;left:96px;top:{yy + 2}px;width:1728px;height:74px;display:flex;flex-direction:row;gap:24px;align-items:center">'
              + p(f"width:900px;flex:none;font-family:{MONO};font-variant-ligatures:none;font-size:24px;font-weight:700;line-height:1.2;color:{RED};white-space:nowrap;overflow:hidden", e(msg))
              + p(f"flex:1;font-size:26px;line-height:1.2;color:{SUB}", why_)
              + p(f"width:110px;flex:none;font-size:28px;font-weight:700;line-height:1;text-align:right;color:{NAVY}", f"{pg(sid)}쪽") + '</div>')
fd.append(hair(96, 184 + 11 * 76, 1728))
W("finder", fd, "터미널이나 GitHub에서 본 메시지를 왼쪽에서 찾고 오른쪽 쪽수로 가요. 쪽 번호를 치고 Enter를 누르면 그 장으로 바로 가요. 위 다섯 줄은 2부와 3부에서 main 하나로 일할 때, 아래 여섯 줄은 브랜치와 PR로 일할 때 자주 나와요. 403 메시지는 GitHub이 보내는 것이라 로컬에서 재현하지 못했어요.", add=False)

# toc
t = [sec("toc")] + [f'<h2 style="position:absolute;left:96px;top:72px;width:1728px;font-size:56px;font-weight:700;line-height:1.2;color:{INK}">오늘의 순서</h2>']
for i, (c, h, s_, a, b) in enumerate(TOC_PARTS):
    y = 186 + i * 154
    t.append(hair(96, y, 1728))
    t.append(f'<div{bi("rise", 1)}{DELAY(i * 110)} style="position:absolute;left:96px;top:{y + 2}px;width:1728px;height:150px;display:flex;flex-direction:row;gap:40px;align-items:center">'
             + p(f"width:80px;flex:none;font-size:72px;font-weight:900;line-height:1;color:{c}", str(i + 1))
             + '<div style="flex:1;display:flex;flex-direction:column;gap:10px">' + p(f"font-size:40px;font-weight:700;line-height:1.2;color:{INK}", h) + p(f"font-size:28px;line-height:1.3;color:{SUB}", s_) + '</div>'
             + p(f"width:200px;flex:none;font-size:28px;line-height:1;text-align:right;color:{MUTE}", f"{pg(a)}–{pg(b)}쪽") + '</div>')
t.append(hair(96, 186 + 5 * 154, 1728))
t.append(p(f"position:absolute;left:96px;top:996px;width:1728px;font-size:26px;line-height:1;color:{SUB}", f"마지막 {len(ORDER)}쪽은 한 장 요약이에요."))
W("toc", t, add=False, notes="1부에서 레포를 만들고 셋이 clone해요. 2부와 3부가 오늘의 중심이에요. 2부는 서로 다른 파일을 고쳐서 저절로 합쳐지는 경우, 3부는 같은 줄을 고쳐서 충돌이 나는 경우예요. 4부는 팀 규칙이에요. 5부는 브랜치와 PR로 일할 때 만나는 경우를 케이스별로 모았어요. 막혔을 땐 5부 첫 두 장에서 찾아요.")

for name, body in PAGES.items():
    body = re.sub(r"\{\{pg:([\w-]+)\}\}", lambda m: str(pg(m.group(1))), body)
    open(os.path.join(OUT, name + ".html"), "w").write(body)

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-10-29T03:00:00Z"}, "lists": "css", "title": "팀 레포에서 같이 작업하고 충돌 풀기", "order": ORDER,
        "sections": {"intro": {"description": "오늘 하는 일", "start": "cover"}, "setup": {"description": "팀 레포 준비", "start": "roles"},
                     "auto": {"description": "다른 파일은 저절로 합쳐져요", "start": "a1"}, "conflict": {"description": "같은 줄은 충돌", "start": "b1"},
                     "rules": {"description": "팀 규칙", "start": "rules"}, "cases": {"description": "브랜치로 일할 때, 막혔을 때 찾기, 요약", "start": "cases"}},
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
json.dump(deck, open(os.path.join(OUT, "deck.json"), "w"), ensure_ascii=False, indent=2)
print(len(ORDER), "slides")
