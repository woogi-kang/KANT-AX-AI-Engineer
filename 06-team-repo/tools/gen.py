"""Generates every slide of the team repo deck.

Three people (kim, lee, park) share one GitHub repo. Each scene shows four state cards side by side
(GitHub and the three computers, one colour per person) above the terminal of whoever is typing.
Terminal output and hashes come from tools/demo.sh (git 2.43).
Usage: python3 tools/gen.py slides
"""
import html, json, os, sys

OUT = sys.argv[1]
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
INK, SUB, LINE, MUTE = "#1D2330", "#4A5262", "#E1DED6", "#6A7180"
BL, GR, OR, RED, PUR = "#2459C9", "#1F8A4C", "#B26A00", "#A33131", "#5A3BB8"
PC = {"gh": PUR, "kim": BL, "lee": GR, "park": OR}
PNAME = {"gh": "GitHub", "kim": "kim", "lee": "lee", "park": "park"}
PSUB = {"gh": "github.com/kim/team-intro", "kim": "팀장 컴퓨터", "lee": "팀원 컴퓨터", "park": "팀원 컴퓨터"}
PICON = {"gh": "Cloud", "kim": "Users", "lee": "Users", "park": "Users"}
URL = "https://github.com/kim/team-intro.git"


def e(s):
    return html.escape(s, quote=False)


def p(style, text, attrs=""):
    return f'<p{attrs} style="{style}">{text}</p>'


ORDER = []


def W(name, parts, notes):
    ORDER.append(name)
    body = "\n".join(parts) + f"\n<aside>{e(notes)}</aside>\n</section>\n"
    open(os.path.join(OUT, name + ".html"), "w").write(body)


def sec(i, transition="fade", bg="#F6F5F1"):
    return f'<section id="{i}" data-transition="{transition}" style="background:{bg};color:{INK};font-family:{SANS};padding:96px;display:flex;flex-direction:column">'


def head(eyebrow, title, color=BL):
    return [p(f"position:absolute;left:96px;top:56px;width:1728px;font-size:26px;font-weight:700;color:{color}", e(eyebrow), ' id="eyebrow"'),
            f'<h2 id="title" style="position:absolute;left:96px;top:100px;width:1728px;font-size:56px;font-weight:700;line-height:1.2;color:{INK}">{title}</h2>']


def bi(parts, spec):
    """Adds a build-in to the first element of each html string."""
    return [x.replace(' style=', f' data-build-in="{spec}" style=', 1) for x in parts]


# ---------- terminal ----------
TC = {"$": "#F2C46D", "o": "#D8DEE9", "#": "#8C95A6", "g": "#7FD18B", "r": "#F28B82"}


def terminal(lines, who=None, left=96, top=448, w=1150, h=576, size=24, lh=1.3, tid="term"):
    o = [f'<div id="{tid}" style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:#1B2029;border-radius:20px;padding:18px 28px;display:flex;flex-direction:column;font-family:{MONO};font-variant-ligatures:none">']
    if who:
        ws = who if isinstance(who, tuple) else (who,)
        o.append(f'<div style="display:flex;flex-direction:row;gap:12px;align-items:center;padding-bottom:12px;margin-bottom:10px;border-bottom:1px solid #343B48">'
                 + "".join(f'<div style="width:18px;height:18px;border-radius:9px;background:{PC[x]}"></div>' for x in ws)
                 + p(f"font-family:{SANS};font-size:22px;font-weight:700;color:#FFFFFF", f"{', '.join(ws)}의 터미널") + p(f"font-size:20px;color:#8C95A6", "~/team-intro") + '</div>')
    for kind, text in lines:
        t = e(text).replace("\t", "        ")
        if kind == "$":
            t = "$ " + t
        bold = "font-weight:700;" if kind == "$" else ""
        o.append(p(f"font-size:{size}px;line-height:{lh};white-space:pre;{bold}color:{TC[kind]}", t if t else " "))
    o.append('</div>')
    return o


def callout(icon, title, sub=None, icolor=BL, top=448, h=576):
    o = [f'<div id="explain" data-build-in="rise" style="position:absolute;left:1278px;top:{top}px;width:546px;height:{h}px;background:#FFFFFF;border:2px solid {LINE};border-radius:20px;padding:36px;display:flex;flex-direction:column;justify-content:center;gap:18px">']
    o.append(f'<x-icon name="{icon}" style="width:56px;height:56px;color:{icolor}"></x-icon>')
    o.append(p(f"font-size:34px;font-weight:700;line-height:1.4;color:{INK}", title))
    if sub:
        o.append(p(f"font-size:26px;line-height:1.5;color:{SUB}", sub))
    o.append('</div>')
    return o


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
N_FULL = "058635425c086372cec618e885f0483ba8c58d08"

# A repo is a list of (key, slot, lane). Commits after "|" are fetched only (origin/main, not in main yet).
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


def card(who, rep, files, x, y, w=414, h=250, active=False, badge=None, pre=""):
    col = PC[who]
    bd = f"4px solid {col}" if active else f"2px solid {LINE}"
    o = [f'<div id="{pre}card-{who}" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:#FFFFFF;border:{bd};border-radius:18px"></div>',
         f'<div id="{pre}ch-{who}" style="position:absolute;left:{x+22}px;top:{y+16}px;width:{w-44}px;height:40px;display:flex;flex-direction:row;gap:12px;align-items:center">'
         f'<x-icon name="{PICON[who]}" style="width:30px;height:30px;color:{col}"></x-icon>'
         + p(f"font-size:28px;font-weight:700;color:{col}", PNAME[who]) + p(f"font-size:18px;color:{MUTE};white-space:nowrap", PSUB[who]) + '</div>']
    if badge:
        o.append(p(f"position:absolute;left:{x+w-150}px;top:{y+18}px;width:128px;font-size:20px;font-weight:700;line-height:34px;text-align:center;border-radius:17px;color:#FFFFFF;background:{badge[1]}", badge[0], f' id="{pre}badge-{who}"'))
    gx = lambda s: x + 40 + s * 66
    gy = lambda l: y + 114 + l * 44
    keys = {k: (s, l, g) for k, s, l, g in rep}
    # edges
    for k, (s, l, g) in keys.items():
        for par in C[k][3]:
            if par not in keys:
                continue
            ps, pl, pg = keys[par]
            x1, y1, x2, y2 = gx(ps), gy(pl), gx(s), gy(l)
            mx, Mx, my, My = min(x1, x2), max(x1, x2), min(y1, y2) - 3, max(y1, y2) + 3
            dash = ' stroke-dasharray="7 6"' if g or pg else ""
            o.append(f'<svg id="{pre}{who}-e-{par}{k}" viewBox="{mx} {my} {Mx-mx} {My-my}" style="position:absolute;left:{mx}px;top:{my}px;width:{Mx-mx}px;height:{My-my}px;overflow:visible">'
                     f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#B9B5AA" stroke-width="4"{dash}/></svg>')
    # dots
    for k, (s, l, g) in keys.items():
        c = PC[C[k][2]]
        if g:
            st = f"background:#FFFFFF;border:3px dashed {c};opacity:.75"
        elif C[k][4]:
            st = f"background:#FFFFFF;border:5px solid {c}"
        else:
            st = f"background:{c};border:5px solid {c}"
        o.append(f'<div id="{pre}{who}-d-{k}" style="position:absolute;left:{gx(s)-15}px;top:{gy(l)-15}px;width:30px;height:30px;border-radius:50%;{st}"></div>')
    # main label at tip
    tip = [t for t in rep if not t[3]][-1]
    o.append(p(f"position:absolute;left:{gx(tip[1])-30}px;top:{gy(tip[2])-48 if tip[2] == 0 else gy(tip[2])+22}px;width:60px;font-family:{MONO};font-size:16px;font-weight:700;line-height:22px;text-align:center;border-radius:6px;color:#FFFFFF;background:{INK}", "main", f' id="{pre}{who}-main"'))
    ghosts = [t for t in rep if t[3]]
    if ghosts:
        gt = ghosts[-1]
        o.append(p(f"position:absolute;left:{gx(gt[1])+24}px;top:{gy(gt[2])-11}px;width:116px;font-family:{MONO};font-size:15px;font-weight:700;line-height:22px;text-align:center;border-radius:6px;color:#FFFFFF;background:{PUR}", "origin/main", f' id="{pre}{who}-om"'))
    if files is not None:
        chips = "".join(p(f"font-family:{MONO};font-size:17px;line-height:30px;padding:0 10px;border-radius:8px;white-space:nowrap;"
                          + (f"color:#FFFFFF;background:{RED}" if f.endswith("!") else f"color:{INK};background:#EEEFF2"), e(f.rstrip("!"))) for f in files)
        o.append(f'<div id="{pre}{who}-files" style="position:absolute;left:{x+22}px;top:{y+h-46}px;width:{w-44}px;height:32px;display:flex;flex-direction:row;gap:8px">{chips}</div>')
    return o


def band(states, active=None, badges=None, y=176, pre=""):
    """states: dict who -> (repo, files)."""
    o = []
    for i, who in enumerate(["gh", "kim", "lee", "park"]):
        rep, files = states[who]
        o += card(who, rep, files, 96 + i * 438, y, active=(who == active or (isinstance(active, tuple) and who in active)),
                  badge=(badges or {}).get(who), pre=pre)
    return o


def frame(sid, eyebrow, cmd, color=BL, transition="magic", cmd_size=50, font=MONO):
    return [sec(sid, transition),
            p(f"position:absolute;left:96px;top:40px;width:1728px;font-size:24px;font-weight:700;color:{color}", e(eyebrow), ' id="eyebrow"'),
            f'<h2 id="cmd" style="position:absolute;left:96px;top:84px;width:1728px;font-family:{font};font-size:{cmd_size}px;font-weight:700;line-height:1.15;color:{INK}">{cmd}</h2>']


def scene(sid, eyebrow, cmd, states, who, term, call, notes, badges=None, color=None, cmd_size=50, transition="magic"):
    o = frame(sid, eyebrow, cmd, color or PC[who], transition, cmd_size)
    o += band(states, active=who, badges=badges)
    o += terminal(term, who)
    o += callout(*call)
    W(sid, o, notes)


def person_dot(who, x, y, size=120, pre=""):
    return (f'<div id="{pre}pd-{who}" style="position:absolute;left:{x}px;top:{y}px;width:{size}px;height:{size}px;border-radius:50%;background:{PC[who]};display:flex;align-items:center;justify-content:center">'
            + p(f"font-size:{round(size*0.3)}px;font-weight:900;color:#FFFFFF", PNAME[who]) + '</div>')


# =====================================================================
# cover
cov = [f'<section id="cover" data-transition="fade" style="background:#1D2330;color:#F6F5F1;font-family:{SANS};padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#8FB3FF;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
       '<h1 style="font-size:100px;font-weight:900;line-height:1.15;color:#F6F5F1">팀 레포로<br>함께 커밋하기</h1>',
       '<p style="font-size:40px;line-height:1.45;color:#BFC6D4">셋이 한 저장소에 push, pull 하며<br>엉킨 것을 풀어요</p>']
cov.append(f'<div style="position:absolute;left:1240px;top:250px;width:480px;height:150px;border-radius:24px;background:#2A3242;border:3px solid {PUR};display:flex;flex-direction:row;gap:18px;align-items:center;justify-content:center">'
           f'<x-icon name="Cloud" style="width:56px;height:56px;color:#B9A5F5"></x-icon>' + p("font-size:40px;font-weight:700;color:#F6F5F1", "GitHub") + '</div>')
for i, who in enumerate(["kim", "lee", "park"]):
    cx = 1260 + i * 170
    cov.append(f'<svg style="position:absolute;left:0;top:0;width:1920px;height:1080px;overflow:visible"><line x1="1480" y1="400" x2="{cx+60}" y2="700" stroke="#4A5468" stroke-width="5" stroke-dasharray="12 10"/></svg>')
for i, who in enumerate(["kim", "lee", "park"]):
    cov.append(person_dot(who, 1260 + i * 170, 700, 120, "cv-"))
W("cover", cov, "오늘은 2~3명이 팀을 짜서 GitHub에 팀 레포를 하나 만들어요. 각자 clone해서 커밋하고 push, pull 하다 보면 서로 엉키는 순간이 와요. 그 순간을 일부러 만들어 보고 푸는 게 오늘의 목표예요.")

# toc (page numbers filled in after all slides are made)
TOC_PARTS = [("Settings", PUR, "팀 레포 준비", "레포 만들기, 초대, clone, pull 설정", "roles", "config"),
             ("Users", GR, "다른 파일은 저절로", "push 거절, pull로 합치기, fast-forward", "a1", "a7"),
             ("Warning", RED, "같은 줄은 충돌", "CONFLICT 읽고 고쳐서 다시 push", "b1", "b6"),
             ("Wrench", OR, "팀 규칙, 막힐 때", "작업 전 pull, 작게 자주 커밋, 오류", "rules", "next")]

# why
w = [sec("why")] + head("오늘 하는 일", "한 저장소를 셋이 같이 써요", PUR)
w.append(f'<div id="w-gh" style="position:absolute;left:660px;top:250px;width:600px;height:140px;border-radius:24px;background:#FFFFFF;border:4px solid {PUR};display:flex;flex-direction:row;gap:20px;align-items:center;justify-content:center">'
         f'<x-icon name="Cloud" style="width:56px;height:56px;color:{PUR}"></x-icon>'
         + '<div style="display:flex;flex-direction:column">' + p(f"font-size:36px;font-weight:700;color:{PUR}", "GitHub 팀 레포") + p(f"font-family:{MONO};font-size:22px;color:{SUB}", "github.com/kim/team-intro") + '</div></div>')
for i, who in enumerate(["kim", "lee", "park"]):
    cx = 360 + i * 600
    w.append(f'<svg style="position:absolute;left:0;top:0;width:1920px;height:1080px;overflow:visible">'
             f'<line x1="960" y1="390" x2="{cx}" y2="560" stroke="#B9B5AA" stroke-width="5" stroke-dasharray="12 10"/></svg>')
    w.append(person_dot(who, cx - 70, 560, 140, "w-"))
    w.append(p(f"position:absolute;left:{cx-200}px;top:716px;width:400px;font-size:26px;text-align:center;color:{SUB}", "clone · commit · push · pull"))
outs = [("! [rejected]", "먼저 받으라고 거절", OR), ("Merge made", "다른 파일은 저절로 합쳐짐", GR), ("CONFLICT", "같은 줄은 직접 골라야 함", RED)]
for i, (code, txt, c) in enumerate(outs):
    w.append(f'<div data-build-in="rise order {i+1}" style="position:absolute;left:{96+i*588}px;top:820px;width:552px;height:150px;background:#FFFFFF;border:2px solid {LINE};border-left:10px solid {c};border-radius:18px;padding:24px 32px;display:flex;flex-direction:column;justify-content:center;gap:8px">'
             + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:{c}", e(code)) + p(f"font-size:28px;color:{INK}", txt) + '</div>')
W("why", w, "GitHub의 저장소 하나를 kim, lee, park 셋이 각자 컴퓨터로 clone해서 써요. 혼자 쓸 때와 달리 남이 먼저 올린 커밋이 생겨요. 그래서 오늘은 세 가지 메시지를 일부러 만나 봐요. push가 거절되는 rejected, pull 하면 저절로 합쳐지는 Merge made, 같은 줄을 고쳐서 생기는 CONFLICT예요. 세 가지 모두 고장이 아니에요. Git이 다음에 할 일을 알려 주는 메시지예요.")

# roles
ro = [sec("roles")] + head("1부 · 팀 레포 준비", "팀을 짜고 역할을 나눠요", PUR)
roles = [("kim", "팀장", ["GitHub에 레포 만들기", "팀원 초대하기"]), ("lee", "팀원", ["초대 수락하기", "clone 하기"]), ("park", "팀원", ["초대 수락하기", "clone 하기"])]
for i, (who, role, todo) in enumerate(roles):
    x = 96 + i * 588
    ro.append(f'<div data-build-in="rise order {i+1}" style="position:absolute;left:{x}px;top:260px;width:552px;height:560px;background:#FFFFFF;border:2px solid {LINE};border-top:12px solid {PC[who]};border-radius:20px;padding:40px;display:flex;flex-direction:column;align-items:center;gap:22px">'
              f'<div style="width:150px;height:150px;border-radius:50%;background:{PC[who]};display:flex;align-items:center;justify-content:center">' + p("font-size:44px;font-weight:900;color:#FFFFFF", who) + '</div>'
              + p(f"font-size:40px;font-weight:700;color:{PC[who]}", role)
              + "".join(p(f"font-size:30px;line-height:1.5;color:{INK}", t) for t in todo) + '</div>')
ro.append(p(f"position:absolute;left:96px;top:870px;width:1728px;font-size:30px;line-height:1.5;color:{SUB}", "슬라이드의 kim, lee, park 자리에 팀원 이름을 넣어요. 2인 팀이면 park 차례는 건너뛰어요.", ' data-build-in="fade order 4"'))
ro.append(p(f"position:absolute;left:96px;top:930px;width:1728px;font-size:30px;line-height:1.5;color:{SUB}", "색은 끝까지 같아요. 파랑 kim, 초록 lee, 주황 park, 보라 GitHub.", ' data-build-in="fade order 4"'))
W("roles", ro, "한 명이 팀장이 돼서 레포를 만들고 나머지를 초대해요. 레포 주인만 처음에 push할 수 있어서 초대가 꼭 필요해요. 이 덱에서 kim은 파랑, lee는 초록, park는 주황, GitHub은 보라로 계속 그려요. 커밋 점의 색이 그 커밋을 만든 사람이에요.")


# new repo
def browser(x, y, w, h, url, pre):
    return [f'<div id="{pre}win" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:#FFFFFF;border:2px solid #D0D7DE;border-radius:16px;overflow:hidden"></div>',
            f'<div id="{pre}bar" style="position:absolute;left:{x+2}px;top:{y+2}px;width:{w-4}px;height:56px;background:#F6F8FA;border-bottom:1px solid #D0D7DE;border-radius:14px 14px 0 0;display:flex;flex-direction:row;gap:12px;align-items:center;padding:0 20px">'
            + "".join(f'<div style="width:14px;height:14px;border-radius:7px;background:{c}"></div>' for c in ["#E5534B", "#E3B341", "#3FB950"])
            + p(f"margin-left:16px;flex:1;font-family:{MONO};font-size:20px;line-height:36px;padding:0 16px;border-radius:8px;background:#FFFFFF;border:1px solid #D0D7DE;color:{SUB}", e(url)) + '</div>']


def marker(n, x, y, order, color=OR):
    return (f'<div data-build-in="pop order {order}" style="position:absolute;left:{x}px;top:{y}px;width:52px;height:52px;border-radius:26px;background:{color};display:flex;align-items:center;justify-content:center;box-shadow:0 0 0 6px rgba(178,106,0,.18)">'
            + p("font-size:28px;font-weight:900;color:#FFFFFF", str(n)) + '</div>')


def steps_card(x, y, w, h, items, title, color=OR):
    o = [f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:#FFFFFF;border:2px solid {LINE};border-radius:20px;padding:36px;display:flex;flex-direction:column;gap:22px">',
         p(f"font-size:30px;font-weight:700;color:{INK}", title)]
    for i, (t, sub) in enumerate(items, 1):
        o.append(f'<div data-build-in="rise order {i}" style="display:flex;flex-direction:row;gap:18px">'
                 + p(f"width:44px;height:44px;flex:none;font-size:24px;font-weight:900;line-height:44px;text-align:center;border-radius:22px;color:#FFFFFF;background:{color}", str(i))
                 + '<div style="display:flex;flex-direction:column;gap:4px">' + p(f"font-size:28px;font-weight:700;line-height:1.45;color:{INK}", t)
                 + (p(f"font-size:22px;line-height:1.45;color:{SUB}", sub) if sub else "") + '</div></div>')
    o.append('</div>')
    return o


nr = [sec("new-repo")] + head("1부 · 팀 레포 준비 · kim", "팀장이 GitHub에 레포를 만들어요", BL)
nr += browser(96, 236, 1000, 790, "github.com/new", "nr-")
GHT, GHS = "#1F2328", "#59636E"
fx, fy = 150, 330
nr.append(p(f"position:absolute;left:{fx}px;top:{fy}px;width:880px;font-size:34px;font-weight:700;color:{GHT}", "Create a new repository"))
nr.append(p(f"position:absolute;left:{fx}px;top:{fy+80}px;width:300px;font-size:22px;font-weight:700;color:{GHT}", "Owner"))
nr.append(p(f"position:absolute;left:{fx+240}px;top:{fy+80}px;width:400px;font-size:22px;font-weight:700;color:{GHT}", "Repository name"))
nr.append(p(f"position:absolute;left:{fx}px;top:{fy+120}px;width:200px;font-size:24px;line-height:48px;padding:0 16px;border:1px solid #D0D7DE;border-radius:8px;background:#F6F8FA;color:{GHT}", "kim ▾"))
nr.append(p(f"position:absolute;left:{fx+214}px;top:{fy+120}px;width:20px;font-size:30px;line-height:48px;color:{GHS}", "/"))
nr.append(p(f"position:absolute;left:{fx+240}px;top:{fy+120}px;width:420px;font-family:{MONO};font-size:26px;line-height:48px;padding:0 16px;border:2px solid #0969DA;border-radius:8px;color:{GHT}", "team-intro"))
nr.append(p(f"position:absolute;left:{fx}px;top:{fy+210}px;width:880px;font-size:22px;font-weight:700;color:{GHT}", "Visibility"))
nr.append(p(f"position:absolute;left:{fx}px;top:{fy+250}px;width:420px;font-size:24px;line-height:48px;padding:0 16px;border:1px solid #D0D7DE;border-radius:8px;color:{GHT}", "Public ▾"))
nr.append(p(f"position:absolute;left:{fx}px;top:{fy+340}px;width:880px;font-size:22px;font-weight:700;color:{GHT}", "Add README"))
nr.append(f'<div style="position:absolute;left:{fx}px;top:{fy+382}px;width:80px;height:40px;border-radius:20px;background:#1F883D"><div style="position:absolute;left:44px;top:4px;width:32px;height:32px;border-radius:16px;background:#FFFFFF"></div></div>')
nr.append(p(f"position:absolute;left:{fx+100}px;top:{fy+384}px;width:400px;font-size:24px;line-height:36px;color:{GHT}", "On"))
nr.append(p(f"position:absolute;left:{fx}px;top:{fy+580}px;width:280px;font-size:24px;font-weight:700;line-height:54px;text-align:center;border-radius:8px;color:#FFFFFF;background:#1F883D", "Create repository"))
nr += [marker(1, fx + 676, fy + 118, 1), marker(2, fx + 440, fy + 248, 2), marker(3, fx + 160, fy + 376, 3), marker(4, fx + 300, fy + 580, 4)]
nr += steps_card(1136, 236, 688, 790, [("이름은 team-intro", "소문자와 하이픈만 써요"), ("Public 그대로", "Private이면 초대한 팀원만 보여요"),
                                         ("Add README를 켜요", "첫 커밋이 생겨서 바로 clone할 수 있어요"), ("Create repository", "주소: github.com/kim/team-intro")], "kim만 해요")
W("new-repo", nr, "오른쪽 위 + 버튼에서 New repository를 눌러요. 02에서는 README 없이 빈 저장소를 만들었어요. 팀 레포는 README를 켜서 만들어요. Initial commit이 하나 생겨서 셋이 바로 clone할 수 있어요. GitHub 화면은 자주 바뀌어요. 체크 상자로 보이면 Add a README file을 체크해요.")

# invite
iv = [sec("invite")] + head("1부 · 팀 레포 준비", "kim이 초대하고, 팀원이 수락해요", BL)
iv += browser(96, 236, 852, 790, "github.com/kim/team-intro/settings/access", "iv1-")
iv.append(p(f"position:absolute;left:130px;top:322px;width:780px;font-size:22px;color:{GHS}", "Settings"))
iv.append(f'<div style="position:absolute;left:130px;top:370px;width:240px;height:560px;display:flex;flex-direction:column;gap:6px">'
          + "".join(p(f"font-size:22px;line-height:44px;padding:0 14px;border-radius:8px;{'font-weight:700;background:#EEF1F4;' if t == 'Collaborators' else ''}color:{GHT}", t) for t in ["General", "Collaborators", "Branches", "Webhooks", "Pages"]) + '</div>')
iv.append(p(f"position:absolute;left:400px;top:370px;width:520px;font-size:30px;font-weight:700;color:{GHT}", "Collaborators"))
iv.append(p(f"position:absolute;left:400px;top:440px;width:220px;font-size:22px;font-weight:700;line-height:48px;text-align:center;border-radius:8px;color:#FFFFFF;background:#1F883D", "Add people"))
iv.append(p(f"position:absolute;left:400px;top:530px;width:500px;font-size:24px;line-height:50px;padding:0 16px;border:2px solid #0969DA;border-radius:8px;color:{GHT}", "lee"))
iv.append(p(f"position:absolute;left:400px;top:600px;width:500px;font-size:22px;line-height:1.5;color:{GHS}", "아이디나 이메일로 찾아요. park도 같은 방법으로 한 번 더 해요."))
iv += [marker(1, 300, 386, 1, BL), marker(2, 636, 438, 2, BL), marker(3, 860, 528, 3, BL)]
iv += browser(972, 236, 852, 790, "github.com/kim/team-intro/invitations", "iv2-")
iv.append(f'<div data-build-in="rise order 4" style="position:absolute;left:1010px;top:340px;width:776px;height:640px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:28px">'
          f'<div style="width:120px;height:120px;border-radius:50%;background:{BL};display:flex;align-items:center;justify-content:center">' + p("font-size:36px;font-weight:900;color:#FFFFFF", "kim") + '</div>'
          + p(f"font-size:28px;line-height:1.5;text-align:center;color:{GHT}", "kim invited you to collaborate<br>on <b>kim/team-intro</b>")
          + p(f"width:300px;font-size:24px;font-weight:700;line-height:56px;text-align:center;border-radius:8px;color:#FFFFFF;background:#1F883D", "Accept invitation")
          + p(f"font-size:24px;line-height:1.5;text-align:center;color:{GR};font-weight:700", "lee, park: 메일이나 이 주소에서 수락해요") + '</div>')
iv.append(marker(4, 1700, 610, 4, GR))
W("invite", iv, "kim은 레포의 Settings에서 Collaborators를 열고 Add people로 팀원 아이디를 넣어요. 초대받은 사람은 GitHub에 가입한 이메일로 온 메일이나 레포 주소 뒤에 /invitations를 붙인 페이지에서 Accept invitation을 눌러요. 수락하지 않으면 clone은 돼도 push할 때 403 오류가 나요.")

# clone (three terminals)
cl = [sec("clone")] + head("1부 · 팀 레포 준비 · 셋 다", "셋이 각자 컴퓨터에 clone해요", PUR)
cl.append(p(f"position:absolute;left:96px;top:184px;width:1728px;font-family:{MONO};font-size:34px;font-weight:700;color:{INK}", "git clone https://github.com/kim/team-intro.git"))
for i, who in enumerate(["kim", "lee", "park"]):
    cl += terminal([("$", "git clone 주소"), ("o", "Cloning into 'team-intro'..."), ("o", "done."), ("$", "cd team-intro"), ("$", "git log --oneline"), ("o", "7f7794e (HEAD -> main, origin/main,"), ("o", "  origin/HEAD) Initial commit")],
                   who, left=96 + i * 588, top=270, w=552, h=330, size=22, tid=f"t-{who}")
cl += band({"gh": (S_I, None), "kim": (S_I, F0), "lee": (S_I, F0), "park": (S_I, F0)}, y=680, pre="cl-")
W("clone", cl, "레포 주소는 GitHub 레포 화면의 초록색 Code 버튼에서 복사해요. 셋이 같은 주소로 clone하면 Initial commit 하나가 든 똑같은 저장소가 세 개 생겨요. 아래 네 칸이 오늘 내내 볼 그림이에요. 점 색은 커밋한 사람이에요. clone한 뒤에는 꼭 cd team-intro로 폴더에 들어가요. git log --oneline 출력은 화면 폭 때문에 두 줄로 나눴어요. 실제로는 한 줄이에요. clone 출력 중 remote: 로 시작하는 진행 줄은 뺐어요.")

# config
cf = [sec("config")] + head("1부 · 팀 레포 준비 · 셋 다", "pull 하기 전에 설정 한 줄", RED)
cf.append(f'<div style="position:absolute;left:96px;top:250px;width:1728px;height:150px;background:#1D2330;border-radius:24px;display:flex;flex-direction:row;align-items:center;padding:0 48px">'
          + p(f"font-family:{MONO};font-size:50px;font-weight:700;color:#F2C46D", "git config --global pull.rebase false") + '</div>')
cf.append(f'<div data-build-in="rise order 1" style="position:absolute;left:96px;top:450px;width:1728px;height:230px;display:flex;flex-direction:row;gap:28px;align-items:center">'
          f'<div style="width:440px;height:200px;background:#FFFFFF;border:2px solid {LINE};border-radius:20px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px">'
          + p(f"font-family:{MONO};font-size:40px;font-weight:700;color:{INK}", "git pull") + p(f"font-size:24px;color:{SUB}", "은 두 단계예요") + '</div>'
          + p(f"font-size:60px;font-weight:700;color:{MUTE}", "=")
          + f'<div style="width:480px;height:200px;background:#FFFFFF;border:2px solid {LINE};border-top:10px solid {PUR};border-radius:20px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px">'
          + p(f"font-family:{MONO};font-size:40px;font-weight:700;color:{PUR}", "fetch") + p(f"font-size:24px;color:{SUB}", "GitHub 커밋 받아 오기") + '</div>'
          + p(f"font-size:60px;font-weight:700;color:{MUTE}", "+")
          + f'<div style="width:480px;height:200px;background:#FFFFFF;border:2px solid {LINE};border-top:10px solid {GR};border-radius:20px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px">'
          + p(f"font-family:{MONO};font-size:40px;font-weight:700;color:{GR}", "merge") + p(f"font-size:24px;color:{SUB}", "내 main과 합치기") + '</div></div>')
cf.append(p(f"position:absolute;left:96px;top:730px;width:1728px;font-size:34px;font-weight:700;line-height:1.45;color:{INK}", "pull.rebase false는 합칠 때 merge로 하라는 뜻이에요. 셋 다 처음 한 번만 쳐요.", ' data-build-in="fade order 2"'))
cf.append(f'<div data-build-in="rise order 3" style="position:absolute;left:96px;top:830px;width:1728px;height:160px;background:#FBEDED;border:2px solid #E7B8B8;border-radius:20px;padding:28px 40px;display:flex;flex-direction:row;gap:28px;align-items:center">'
          f'<x-icon name="Warning" style="width:56px;height:56px;color:{RED}"></x-icon>'
          + '<div style="display:flex;flex-direction:column;gap:6px">' + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{RED}", "fatal: Need to specify how to reconcile divergent branches.")
          + p(f"font-size:26px;color:{INK}", "설정을 안 하면 오늘 실습 중간에 pull이 이 메시지로 멈춰요. 13쪽에서 다시 봐요.") + '</div></div>')
W("config", cf, "03에서 본 설정이에요. 아직 안 했다면 셋 다 지금 쳐요. 출력은 없어요. --global이라 내 컴퓨터의 모든 저장소에 적용돼서 한 번만 하면 돼요. 이 설정이 없으면 내 main과 GitHub main이 갈라졌을 때 pull이 어떻게 합칠지 물으면서 fatal로 멈춰요. 오늘 실습은 그 상황이 반드시 생겨요. git config --global pull.rebase로 값을 확인할 수 있어요. false가 나오면 된 거예요. rebase는 이 과정에서 다루지 않아요.")

# =====================================================================
# part 2: different files
P2 = "2부 · 다른 파일은 저절로"
scene("a1", f"{P2} · kim", "kim: kim.md 만들고 push",
      {"gh": (S_K, None), "kim": (S_K, FK), "lee": (S_I, F0), "park": (S_I, F0)}, "kim",
      [("$", 'echo "안녕하세요, kim이에요" > kim.md'), ("$", "git add kim.md"), ("$", 'git commit -m "docs: kim 자기소개 추가"'),
       ("o", "[main 11f6ff4] docs: kim 자기소개 추가"), ("o", " 1 file changed, 1 insertion(+)"), ("o", " create mode 100644 kim.md"),
       ("$", "git push origin main"), ("o", "To https://github.com/kim/team-intro.git"), ("g", "   7f7794e..11f6ff4  main -> main")],
      ("CheckCircle", "먼저 올린 사람은 그냥 올라가요", "GitHub에 파란 점이 하나 늘었어요. lee와 park 컴퓨터는 아직 모르는 커밋이에요.", GR),
      "셋이 동시에 각자 파일을 만들기 시작했다고 해요. kim이 조금 빨랐어요. GitHub main이 kim이 clone했을 때 그대로라서 push가 바로 올라가요. 위 GitHub 칸에 파란 점이 생긴 걸 보여 주세요. lee, park 칸은 그대로예요.",
      transition="fade")
scene("a2", f"{P2} · lee", "lee: lee.md 만들고 push",
      {"gh": (S_K, None), "kim": (S_K, FK), "lee": (S_L, FL), "park": (S_I, F0)}, "lee",
      [("$", 'echo "안녕하세요, lee예요" > lee.md'), ("$", "git add lee.md"), ("$", 'git commit -m "docs: lee 자기소개 추가"'),
       ("o", "[main a078082] docs: lee 자기소개 추가"), ("$", "git push origin main"), ("o", "To https://github.com/kim/team-intro.git"),
       ("r", " ! [rejected]        main -> main (fetch first)"), ("r", "error: failed to push some refs to"), ("r", "  'https://github.com/kim/team-intro.git'"),
       ("#", "hint: ..."), ("#", "hint: the same ref. If you want to integrate the remote changes, use"), ("#", "hint: 'git pull' before pushing again.")],
      ("Warning", "GitHub에 lee가 모르는 커밋이 있어요", "파란 점(kim)이 lee 칸에는 없어요. 지우지 않으려고 Git이 push를 막아요.", OR),
      "lee도 커밋하고 push했는데 거절됐어요. 위 GitHub 칸과 lee 칸을 비교해 보세요. GitHub에는 kim의 파란 점이 있는데 lee 컴퓨터에는 없어요. 그대로 올리면 kim의 커밋이 사라지니까 Git이 막는 거예요. hint가 말하듯 먼저 pull 해요. --force로 밀어 올리면 kim의 커밋이 지워져요. 쓰지 않아요. error 줄은 폭 때문에 두 줄로 나눴고 hint는 일부만 옮겼어요.")
scene("a3", f"{P2} · lee", "lee: git pull origin main",
      {"gh": (S_K, None), "kim": (S_K, FK), "lee": (S_M, FA), "park": (S_I, F0)}, "lee",
      [("$", "git pull origin main"), ("o", "From https://github.com/kim/team-intro"), ("o", " * branch            main       -> FETCH_HEAD"),
       ("o", "   7f7794e..11f6ff4  main       -> origin/main"), ("g", "Merge made by the 'ort' strategy."), ("o", " kim.md | 1 +"), ("o", " 1 file changed, 1 insertion(+)"), ("o", " create mode 100644 kim.md"),
       ("$", "git log --oneline"), ("o", "3c66163 (HEAD -> main) Merge branch 'main' of ..."), ("o", "a078082 docs: lee 자기소개 추가"), ("o", "11f6ff4 (origin/main, origin/HEAD) docs: kim 자기소개 추가"), ("o", "7f7794e Initial commit")],
      ("CheckCircle", "다른 파일이라 저절로 합쳐졌어요", "흰 점이 kim과 lee의 커밋을 잇는 merge 커밋이에요. 폴더에 kim.md가 생겼어요.", GR),
      "pull은 kim의 커밋을 받아 와서 lee의 커밋과 합쳐요. kim은 kim.md, lee는 lee.md만 건드렸으니 Git이 알아서 합쳐요. 03에서 본 merge 커밋과 같은 흰 점이 생겨요. 이 merge 커밋은 아직 lee 컴퓨터에만 있어요. 그래서 다음에 push해야 해요. 중간에 vim이 열리는데 다음 장에서 봐요. git log의 Merge 줄 끝은 폭 때문에 ...로 줄였어요. 실제는 Merge branch 'main' of https://github.com/kim/team-intro예요.")

# vim
vm = frame("vim", f"{P2} · lee", "pull 하다 이 화면이 열리면", GR, "fade", font=SANS)
VL = [("o", "Merge branch 'main' of https://github.com/kim/team-intro"), ("#", "# Please enter a commit message to explain why this merge is necessary,"),
      ("#", "# especially if it merges an updated upstream into a topic branch."), ("#", "#"), ("#", "# Lines starting with '#' will be ignored, and an empty message aborts"),
      ("#", "# the commit."), ("#", "~"), ("#", "~"), ("#", "~"), ("o", '".git/MERGE_MSG" 6L')]
vm += terminal(VL, None, left=96, top=200, w=1728, h=440, size=26)
keys = [("Esc", "입력 모드 끝내기"), (":wq", "저장하고 닫기"), ("Enter", "실행")]
for i, (k, t) in enumerate(keys):
    vm.append(f'<div data-build-in="rise order {i+1}" style="position:absolute;left:{96+i*588}px;top:690px;width:552px;height:200px;background:#FFFFFF;border:2px solid {LINE};border-top:10px solid {GR};border-radius:20px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px">'
              + p(f"font-family:{MONO};font-size:56px;font-weight:700;color:{INK}", k) + p(f"font-size:28px;color:{SUB}", t) + '</div>')
vm.append(p(f"position:absolute;left:96px;top:930px;width:1728px;font-size:32px;font-weight:700;color:{INK}", "merge 커밋 메시지를 고칠 기회예요. 그대로 저장하고 닫으면 pull이 끝나요.", ' data-build-in="fade order 4"'))
W("vim", vm, "pull이 merge 커밋을 만들 때 메시지 편집기가 열려요. 03에서 merge할 때 본 화면과 같아요. 첫 줄이 메시지이고 #으로 시작하는 줄은 무시돼요. 그대로 두고 Esc, :wq, Enter를 치면 닫히면서 pull이 끝나요. VS Code가 편집기로 설정된 사람은 탭이 열려요. 그 탭을 닫으면 돼요. 화면 아래 상태 줄은 사람마다 조금 달라요.")

# no config
nc = frame("nocfg", f"{P2} · lee", "설정을 안 했다면 pull이 멈춰요", RED, "fade", font=SANS)
nc += terminal([("$", "git pull origin main"), ("o", "From https://github.com/kim/team-intro"), ("o", " * branch            main       -> FETCH_HEAD"),
                ("#", "hint: You have divergent branches and need to specify how to reconcile them."), ("#", "hint: ..."), ("#", "hint:   git config pull.rebase false  # merge"),
                ("#", "hint:   git config pull.rebase true   # rebase"), ("#", "hint:   git config pull.ff only       # fast-forward only"),
                ("#", "hint: ..."), ("r", "fatal: Need to specify how to reconcile divergent branches.")], "lee", left=96, top=200, w=1728, h=420, size=26)
nc.append(f'<div data-build-in="rise order 1" style="position:absolute;left:96px;top:660px;width:1728px;height:150px;display:flex;flex-direction:row;gap:24px;align-items:center">'
          + p(f"width:64px;height:64px;flex:none;font-size:34px;font-weight:900;line-height:64px;text-align:center;border-radius:32px;color:#FFFFFF;background:{RED}", "1")
          + p(f"flex:1;font-family:{MONO};font-size:40px;font-weight:700;line-height:110px;padding:0 36px;border-radius:20px;color:#F2C46D;background:#1D2330", "git config --global pull.rebase false") + '</div>')
nc.append(f'<div data-build-in="rise order 2" style="position:absolute;left:96px;top:840px;width:1728px;height:150px;display:flex;flex-direction:row;gap:24px;align-items:center">'
          + p(f"width:64px;height:64px;flex:none;font-size:34px;font-weight:900;line-height:64px;text-align:center;border-radius:32px;color:#FFFFFF;background:{GR}", "2")
          + p(f"flex:1;font-family:{MONO};font-size:40px;font-weight:700;line-height:110px;padding:0 36px;border-radius:20px;color:#F2C46D;background:#1D2330", "git pull origin main")
          + p(f"width:520px;font-size:28px;line-height:1.45;color:{SUB}", "다시 치면 앞 장처럼 합쳐져요. 멈췄을 땐 아무것도 바뀌지 않았어요.") + '</div>')
W("nocfg", nc, "8쪽 설정을 건너뛴 사람은 여기서 이 메시지를 봐요. 내 main과 GitHub main에 서로 모르는 커밋이 하나씩 있어서 Git이 merge로 합칠지 rebase로 합칠지 물어요. hint의 첫 번째 줄이 우리가 고르는 merge예요. --global을 붙여 설정하고 같은 pull을 다시 치면 돼요. 멈춘 pull은 커밋도 파일도 바꾸지 않아요. hint 줄은 일부만 옮겼어요.")

scene("a4", f"{P2} · lee", "lee: 다시 git push origin main",
      {"gh": (S_M, None), "kim": (S_K, FK), "lee": (S_M, FA), "park": (S_I, F0)}, "lee",
      [("$", "git push origin main"), ("o", "To https://github.com/kim/team-intro.git"), ("g", "   11f6ff4..3c66163  main -> main")],
      ("CheckCircle", "이번엔 올라가요", "lee가 kim의 커밋까지 품고 있어서 GitHub 것을 지우지 않아요.", GR),
      "pull로 kim의 커밋을 받아 합쳤으니 이번엔 push가 통과해요. GitHub 칸이 lee 칸과 똑같아졌어요. 정리하면 거절되면 pull, 합쳐지면 push예요.")
scene("a5", f"{P2} · kim", "kim: git pull origin main",
      {"gh": (S_M, None), "kim": (S_M, FA), "lee": (S_M, FA), "park": (S_I, F0)}, "kim",
      [("$", "git pull origin main"), ("o", "From https://github.com/kim/team-intro"), ("o", " * branch            main       -> FETCH_HEAD"), ("o", "   11f6ff4..3c66163  main       -> origin/main"),
       ("o", "Updating 11f6ff4..3c66163"), ("g", "Fast-forward"), ("o", " lee.md | 1 +"), ("o", " 1 file changed, 1 insertion(+)"), ("o", " create mode 100644 lee.md")],
      ("Lightbulb", "kim은 새 커밋이 없어서 Fast-forward", "main 이름표만 앞으로 옮겨요. 편집기도 안 열려요.", BL),
      "kim은 push한 뒤로 커밋한 게 없어요. 받아 온 커밋을 그대로 이어 붙이면 되니까 03에서 본 fast-forward예요. merge 커밋이 새로 생기지 않고 vim도 안 열려요. 이제 kim 폴더에도 lee.md가 생겼어요.")
scene("a6", f"{P2} · park", "park: fetch로 먼저 보기",
      {"gh": (S_M, None), "kim": (S_M, FA), "lee": (S_M, FA), "park": (repo("I", ghost="KLM"), F0)}, "park",
      [("$", "git fetch origin"), ("o", "From https://github.com/kim/team-intro"), ("o", "   7f7794e..3c66163  main       -> origin/main"),
       ("$", "git log --oneline"), ("o", "7f7794e (HEAD -> main) Initial commit"), ("$", "git log --oneline origin/main"),
       ("o", "3c66163 (origin/main, origin/HEAD) Merge branch 'main' of ..."), ("o", "a078082 docs: lee 자기소개 추가"), ("o", "11f6ff4 docs: kim 자기소개 추가"), ("o", "7f7794e (HEAD -> main) Initial commit")],
      ("Search", "받아만 오고 아직 안 합쳤어요", "점선 점이 origin/main에만 있는 커밋이에요. 폴더 파일은 그대로예요.", PUR),
      "park은 그동안 쉬고 있었어요. 작업을 시작하기 전에 팀원이 무엇을 올렸는지 먼저 봐요. 02에서 배운 대로 git fetch origin 뒤에 두 log를 비교해요. origin/main 쪽에만 커밋 세 개가 더 있어요. 그림의 점선 점이 그 세 개예요. fetch는 받아만 와서 폴더의 파일은 아직 README.md 하나예요. Merge 줄 끝은 폭 때문에 줄였어요.")
scene("a7", f"{P2} · park", "park: git pull origin main",
      {"gh": (S_M, None), "kim": (S_M, FA), "lee": (S_M, FA), "park": (S_M, FA)}, "park",
      [("$", "git pull origin main"), ("o", "From https://github.com/kim/team-intro"), ("o", " * branch            main       -> FETCH_HEAD"), ("o", "Updating 7f7794e..3c66163"), ("g", "Fast-forward"),
       ("o", " kim.md | 1 +"), ("o", " lee.md | 1 +"), ("o", " 2 files changed, 2 insertions(+)"), ("o", " create mode 100644 kim.md"), ("o", " create mode 100644 lee.md")],
      ("CheckCircle", "넷이 같아졌어요", "작업 전에 pull 하면 거절 없이 시작해요.", GR),
      "park도 커밋이 없어서 fast-forward로 따라잡아요. 네 칸이 모두 같은 그림이에요. park처럼 작업 전에 pull부터 하면 lee가 겪은 거절을 줄일 수 있어요. 2부에서 기억할 것은 하나예요. 다른 파일을 고쳤다면 pull 한 번으로 저절로 합쳐져요.")

# =====================================================================
# part 3: same line
P3 = "3부 · 같은 줄은 충돌"
scene("b1", f"{P3} · kim", "kim: README.md 첫 줄을 고치고 push",
      {"gh": (S_N, None), "kim": (S_N, FA), "lee": (S_M, FA), "park": (S_M, FA)}, "kim",
      [("$", "git diff"), ("o", "--- a/README.md"), ("o", "+++ b/README.md"), ("o", "@@ -1 +1 @@"), ("r", "-# team-intro"), ("g", "+# 깃벗 팀"),
       ("$", "git add README.md"), ("$", 'git commit -m "docs: 팀 이름을 깃벗으로 정하기"'), ("o", "[main 0586354] docs: 팀 이름을 깃벗으로 정하기"),
       ("$", "git push origin main"), ("g", "   3c66163..0586354  main -> main")],
      ("CheckCircle", "kim은 첫 줄을 # 깃벗 팀으로", "이번에도 kim이 먼저 올렸어요.", BL),
      "이번엔 팀 이름을 정해요. kim이 README.md 첫 줄을 # 깃벗 팀으로 바꾸고 push했어요. 04에서 배운 git diff로 바뀐 줄을 확인했어요. diff의 diff --git, index 줄과 push의 To 줄은 뺐어요.", transition="fade")
scene("b2", f"{P3} · lee", "lee: 같은 줄을 고치고 push",
      {"gh": (S_N, None), "kim": (S_N, FA), "lee": (S_O, FA), "park": (S_M, FA)}, "lee",
      [("$", "git diff"), ("r", "-# team-intro"), ("g", "+# 커밋조 팀"), ("$", "git add README.md"), ("$", 'git commit -m "docs: 팀 이름을 커밋조로 정하기"'), ("o", "[main f08005f] docs: 팀 이름을 커밋조로 정하기"),
       ("$", "git push origin main"), ("r", " ! [rejected]        main -> main (fetch first)"), ("r", "error: failed to push some refs to"), ("r", "  'https://github.com/kim/team-intro.git'")],
      ("Warning", "또 거절, 순서대로 pull 해요", "그런데 이번엔 kim과 lee가 같은 줄을 고쳤어요.", OR),
      "lee는 같은 시간에 같은 줄을 # 커밋조 팀으로 바꿨어요. push하면 2부와 똑같이 거절돼요. 순서도 같아요. pull 해요. 다만 이번엔 두 사람이 같은 줄을 서로 다르게 고쳐서 Git이 하나를 고를 수 없어요. diff 머리 줄과 hint 줄은 뺐어요.")
scene("b3", f"{P3} · lee", "lee: git pull origin main",
      {"gh": (S_N, None), "kim": (S_N, FA), "lee": (S_NO, ["README.md!", "kim.md", "lee.md"]), "park": (S_M, FA)}, "lee",
      [("$", "git pull origin main"), ("o", "From https://github.com/kim/team-intro"), ("o", "   3c66163..0586354  main       -> origin/main"), ("o", "Auto-merging README.md"),
       ("r", "CONFLICT (content): Merge conflict in README.md"), ("r", "Automatic merge failed; fix conflicts and then commit the result."),
       ("$", "git status"), ("o", "You have unmerged paths."), ("o", "  (fix conflicts and run \"git commit\")"), ("o", "  (use \"git merge --abort\" to abort the merge)"), ("r", "\tboth modified:   README.md")],
      ("Warning", "같은 줄이라 CONFLICT", "pull이 합치다 멈췄어요. 고를 때까지 merge 커밋이 안 생겨요.", RED),
      "pull이 kim의 커밋을 받아 합치려다 README.md에서 멈췄어요. 두 사람이 같은 줄을 고쳐서예요. lee 칸을 보면 두 갈래가 아직 안 이어졌어요. git status가 알려 주듯 파일을 고치고 commit 하면 이어져요. 겁나면 03에서 배운 git merge --abort로 pull 전으로 돌아갈 수 있어요. pull의 * branch 줄은 빼고 status 출력은 일부만 옮겼어요.",
      badges={"lee": ("충돌 중", RED)})

# conflict file
cr = frame("b4", f"{P3} · lee", "README.md를 열면", RED, "fade", font=SANS)
cr.append(f'<div style="position:absolute;left:96px;top:200px;width:1100px;height:460px;background:#FFFFFF;border:2px solid {LINE};border-radius:20px;padding:40px 48px;display:flex;flex-direction:column;gap:10px;font-family:{MONO}">'
          + p(f"font-size:22px;font-family:{SANS};color:{MUTE};padding-bottom:12px", "README.md")
          + p(f"font-size:36px;line-height:1.5;color:{MUTE}", "&lt;&lt;&lt;&lt;&lt;&lt;&lt; HEAD")
          + p(f"font-size:44px;font-weight:700;line-height:1.5;color:{GR};background:#E7F4EC;padding:0 12px;border-radius:8px", "# 커밋조 팀")
          + p(f"font-size:36px;line-height:1.5;color:{MUTE}", "=======")
          + p(f"font-size:44px;font-weight:700;line-height:1.5;color:{BL};background:#E8EEFA;padding:0 12px;border-radius:8px", "# 깃벗 팀")
          + p(f"font-size:36px;line-height:1.5;color:{MUTE}", "&gt;&gt;&gt;&gt;&gt;&gt;&gt; 058635425c086372cec618e8...") + '</div>')
cr.append(f'<div data-build-in="rise order 1" style="position:absolute;left:1236px;top:200px;width:588px;height:220px;background:#FFFFFF;border:2px solid {LINE};border-left:10px solid {GR};border-radius:20px;padding:28px 32px;display:flex;flex-direction:column;justify-content:center;gap:8px">'
          + p(f"font-size:30px;font-weight:700;color:{GR}", "위: HEAD = 내 것 (lee)") + p(f"font-size:24px;line-height:1.45;color:{SUB}", "pull 하기 전 lee 컴퓨터의 줄") + '</div>')
cr.append(f'<div data-build-in="rise order 2" style="position:absolute;left:1236px;top:440px;width:588px;height:220px;background:#FFFFFF;border:2px solid {LINE};border-left:10px solid {BL};border-radius:20px;padding:28px 32px;display:flex;flex-direction:column;justify-content:center;gap:8px">'
          + p(f"font-size:30px;font-weight:700;color:{BL}", "아래: 해시 = 받아 온 것 (kim)") + p(f"font-size:24px;line-height:1.45;color:{SUB}", "GitHub에서 온 커밋 0586354의 줄") + '</div>')
cr.append(f'<div data-build-in="rise order 3" style="position:absolute;left:96px;top:700px;width:1728px;height:300px;background:#FFFFFF;border:2px solid {LINE};border-radius:20px;padding:36px 48px;display:flex;flex-direction:row;gap:40px;align-items:center">'
          f'<x-icon name="Chat" style="width:80px;height:80px;color:{RED}"></x-icon>'
          + '<div style="display:flex;flex-direction:column;gap:14px">' + p(f"font-size:40px;font-weight:700;color:{INK}", "어느 쪽을 남길지 팀이 말로 정해요")
          + p(f"font-size:28px;line-height:1.5;color:{SUB}", "둘 중 하나, 둘 다, 새 이름 모두 돼요. 정한 내용만 남기고 표시 세 줄(&lt;&lt;&lt;, ===, &gt;&gt;&gt;)은 지워요.") + '</div></div>')
W("b4", cr, "03 충돌 시나리오 5와 같은 모양이에요. 위쪽 HEAD 아래가 lee 자기 것, 아래쪽이 GitHub에서 받아 온 kim의 것이에요. pull로 생긴 충돌은 아래 이름이 브랜치 대신 커밋 해시예요. 해시는 kim의 커밋 0586354예요. 화면에서는 뒤를 줄였어요. 여기서 Git이 대신 정해 줄 수 없으니 팀원과 이야기해서 정해요. 오늘은 깃벗 팀으로 정했다고 해요. VS Code로 열면 Accept Current Change 같은 버튼이 보여요. 눌러도 되고 직접 지워도 돼요.")

scene("b5", f"{P3} · lee", "lee: 고쳐서 add, commit, push",
      {"gh": (S_X, None), "kim": (S_N, FA), "lee": (S_X, FA), "park": (S_M, FA)}, "lee",
      [("#", "# README.md를 # 깃벗 팀 한 줄만 남기고 저장"), ("$", "git add README.md"), ("$", 'git commit -m "fix: 팀 이름 충돌 해결"'), ("o", "[main b13c5dc] fix: 팀 이름 충돌 해결"),
       ("$", "git push origin main"), ("o", "To https://github.com/kim/team-intro.git"), ("g", "   0586354..b13c5dc  main -> main"),
       ("$", "git log --oneline"), ("o", "b13c5dc (HEAD -> main, origin/main, origin/HEAD) fix: 팀 이름 충돌 해결"), ("o", "f08005f docs: 팀 이름을 커밋조로 정하기"), ("o", "0586354 docs: 팀 이름을 깃벗으로 정하기"), ("o", "3c66163 Merge branch 'main' of ...")],
      ("CheckCircle", "commit이 두 갈래를 이어요", "충돌을 푼 커밋도 merge 커밋이라 흰 점이에요. 이제 push가 통과해요.", GR),
      "파일을 고쳐 저장한 뒤 add, commit 하면 멈췄던 merge가 끝나요. 이번 commit은 -m으로 메시지를 적어서 편집기가 안 열려요. 그다음 push해요. GitHub이 lee 칸과 같아졌어요. kim과 park은 아직 옛 그림이에요. git log 아래쪽 두 줄은 뺐어요.")
scene("b6", f"{P3} · kim, park", "kim, park: git pull origin main",
      {"gh": (S_X, None), "kim": (S_X, FA), "lee": (S_X, FA), "park": (S_X, FA)}, ("kim", "park"),
      [("#", "# kim"), ("$", "git pull origin main"), ("o", "Updating 0586354..b13c5dc"), ("g", "Fast-forward"),
       ("#", "# park"), ("$", "git pull origin main"), ("o", "Updating 3c66163..b13c5dc"), ("g", "Fast-forward"), ("o", " README.md | 2 +-"), ("$", "cat README.md"), ("o", "# 깃벗 팀")],
      ("CheckCircle", "다시 넷이 같아졌어요", "충돌은 한 사람이 풀고 push하면 나머지는 pull로 받아요.", GR),
      "충돌은 lee 컴퓨터에서만 났어요. kim과 park은 pull 하면 fast-forward로 따라와요. park은 2부 뒤로 받은 게 없어서 README.md가 바뀌는 게 보여요. 이제 셋 다 # 깃벗 팀이에요. From 줄은 뺐어요.", color=INK)

# =====================================================================
# part 4: rules and trouble
ru = [sec("rules")] + head("4부 · 팀 규칙", "엉키지 않게, 엉켜도 쉽게", OR)
RL = [("1", "작업 전에 pull", "git pull origin main 부터. park처럼 거절 없이 시작해요"),
      ("2", "작게 자주 커밋하고 push", "커밋이 작을수록 충돌도 작아요. 한 커밋에 한 가지만"),
      ("3", "파일과 줄을 나눠 맡기", "같은 줄은 동시에 고치지 않기로 미리 말해요"),
      ("4", "거절되면 pull, --force는 금지", "--force는 팀원 커밋을 지워요"),
      ("5", "충돌은 같이 보고 정하기", "혼자 지우지 말고 고친 사람에게 물어봐요")]
for i, (n, t, s) in enumerate(RL):
    ru.append(f'<div data-build-in="rise order {i+1}" style="position:absolute;left:96px;top:{236+i*156}px;width:1728px;height:136px;background:#FFFFFF;border:2px solid {LINE};border-radius:20px;padding:0 40px;display:flex;flex-direction:row;gap:36px;align-items:center">'
              + p(f"width:72px;height:72px;flex:none;font-size:38px;font-weight:900;line-height:72px;text-align:center;border-radius:36px;color:#FFFFFF;background:{OR}", n)
              + p(f"width:620px;flex:none;font-size:38px;font-weight:700;color:{INK}", t) + p(f"flex:1;font-size:28px;line-height:1.45;color:{SUB}", s) + '</div>')
W("rules", ru, "오늘 겪은 일에서 나온 규칙이에요. 1번은 park, 4번은 lee의 첫 push에서 봤어요. 3번은 3부 충돌을 막는 방법이에요. 2번은 충돌이 나더라도 고칠 양을 줄여 줘요. 팀이 처음 모였을 때 누가 어떤 파일을 맡을지 정해 두면 3번이 쉬워요.")

# cycle
cy = [sec("cycle")] + head("4부 · 팀 규칙", "한 번 작업할 때 이 순서로 돌아요", OR)
STEPS = [("git pull origin main", "받기", PUR), ("파일 고치기", "작업", INK), ("git add 파일", "담기", GR), ('git commit -m "..."', "저장", BL), ("git push origin main", "올리기", PUR)]
for i, (cmd, t, c) in enumerate(STEPS):
    x = 96 + i * 352
    cy.append(f'<div data-build-in="rise order {i+1}" style="position:absolute;left:{x}px;top:300px;width:320px;height:220px;background:#FFFFFF;border:2px solid {LINE};border-top:10px solid {c};border-radius:20px;padding:24px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px">'
              + p(f"font-size:24px;font-weight:700;color:{MUTE}", f"{i+1} · {t}") + p(f"font-family:{MONO};font-size:24px;font-weight:700;line-height:1.35;text-align:center;color:{INK}", e(cmd)) + '</div>')
cy.append(f'<svg data-build-in="fade order 6" style="position:absolute;left:0;top:0;width:1920px;height:1080px;overflow:visible"><path d="M1664,530 L1664,640 L256,640 L256,530" fill="none" stroke="{RED}" stroke-width="5" stroke-dasharray="14 10"/>'
          f'<polygon points="256,522 244,546 268,546" fill="{RED}"/></svg>')
cy.append(p(f"position:absolute;left:560px;top:600px;width:800px;font-size:30px;font-weight:700;line-height:80px;text-align:center;color:{RED};background:#F6F5F1", "push가 거절되면 1번으로", ' data-build-in="fade order 6"'))
cy.append(f'<div data-build-in="rise order 7" style="position:absolute;left:96px;top:760px;width:1728px;height:220px;background:#FFFFFF;border:2px solid {LINE};border-radius:20px;padding:32px 48px;display:flex;flex-direction:column;justify-content:center;gap:14px">'
          + p(f"font-size:32px;font-weight:700;color:{INK}", "pull에서 CONFLICT가 나면")
          + p(f"font-family:{MONO};font-size:28px;line-height:1.5;color:{SUB}", "파일 고치기 → git add 파일 → git commit -m \"fix: ...\" → git push origin main") + '</div>')
W("cycle", cy, "하루에 이 순환을 여러 번 돌아요. push가 거절되면 놀라지 말고 다시 1번 pull로 돌아가요. pull에서 충돌이 나면 3부에서 한 것처럼 고치고 add, commit, push해요.")

# trouble
tb = [sec("trouble")] + head("4부 · 막힐 때", "자주 보는 메시지", "#1E3F8F")
cases = [("! [rejected] ... (fetch first)", "GitHub에 내가 모르는 커밋", "git pull origin main 뒤 push"),
         ("fatal: Need to specify how to reconcile ...", "pull 설정이 없음", "git config --global pull.rebase false"),
         ("error: Pulling is not possible because you have unmerged files.", "충돌을 덜 풀고 또 pull", "고치고 git add, git commit"),
         ("error: Your local changes ... would be overwritten by merge", "커밋 안 한 파일을 팀원도 고침", "git add, git commit 뒤 pull"),
         ("Permission to kim/team-intro.git denied", "초대를 수락하지 않음", "/invitations에서 Accept")]
for i, (msg, why_, fix) in enumerate(cases, 1):
    tb.append(f'<div data-build-in="rise order {i}" style="position:absolute;left:96px;top:{224+(i-1)*162}px;width:1728px;height:144px;background:#FFFFFF;border:2px solid {LINE};border-radius:20px;padding:0 32px;display:flex;flex-direction:row;gap:28px;align-items:center">'
              + p(f"width:56px;height:56px;flex:none;font-size:30px;font-weight:900;line-height:56px;text-align:center;border-radius:28px;color:#FFFFFF;background:#1E3F8F", str(i))
              + '<div style="flex:1;display:flex;flex-direction:column;gap:6px">' + p(f"font-family:{MONO};font-size:24px;font-weight:700;line-height:1.35;color:{RED}", e(msg)) + p(f"font-size:26px;color:{SUB}", why_) + '</div>'
              + p(f"width:560px;flex:none;font-family:{MONO};font-size:24px;font-weight:700;line-height:1.45;color:{INK};background:#EEEFF2;padding:14px 20px;border-radius:12px", e(fix)) + '</div>')
W("trouble", tb, "1, 2번은 오늘 실습에서 봤어요. 3번은 충돌 표시를 지우고 add, commit 하기 전에 pull을 또 친 경우예요. 4번은 커밋하지 않은 kim.md가 있는데 pull이 같은 파일을 바꾸려 할 때 나와요. 먼저 add, commit 하고 pull 하면 2부나 3부 모양으로 이어져요. 5번은 초대받은 사람이 수락하기 전에 push하면 GitHub이 403과 함께 보내는 메시지예요. 1~4번 출력은 git 2.43에서 실제로 실행해 옮겼고, 5번은 GitHub이 보내는 메시지라 로컬에서 재현하지 못했어요.")

# next
nx = [sec("next")] + head("4부 · 다음 단계", "main 하나를 같이 쓰는 건 연습용이에요", OR)
nx.append(f'<div style="position:absolute;left:96px;top:250px;width:840px;height:560px;background:#FFFFFF;border:2px solid {LINE};border-top:10px solid {OR};border-radius:20px;padding:40px;display:flex;flex-direction:column;gap:20px">'
          + p(f"font-size:36px;font-weight:700;color:{INK}", "오늘: 모두 main에 바로 push") + p(f"font-size:28px;line-height:1.55;color:{SUB}", "거절, pull, 충돌을 가장 빨리 겪어 보는 방법이에요. 사람이 늘면 서로 기다리는 일이 많아져요.") + '</div>')
nx.append(f'<div data-build-in="rise order 1" style="position:absolute;left:984px;top:250px;width:840px;height:560px;background:#FFFFFF;border:2px solid {LINE};border-top:10px solid {GR};border-radius:20px;padding:40px;display:flex;flex-direction:column;gap:20px">'
          + p(f"font-size:36px;font-weight:700;color:{INK}", "다음: 각자 브랜치, Pull Request") + p(f"font-size:28px;line-height:1.55;color:{SUB}", "feature/이름 브랜치에서 일하고 Pull Request로 main에 합쳐요. 03의 7부 GitHub에서 함께를 이어서 봐요.")
          + p(f"font-family:{MONO};font-size:26px;line-height:1.6;color:{INK};background:#EEEFF2;padding:16px 20px;border-radius:12px", "git checkout -b feature/kim-intro<br>git push origin feature/kim-intro") + '</div>')
nx.append(p(f"position:absolute;left:96px;top:860px;width:1728px;font-size:30px;line-height:1.5;color:{SUB}", "브랜치를 써도 Pull Request를 합친 뒤엔 오늘처럼 git pull origin main으로 맞춰요.", ' data-build-in="fade order 2"'))
W("next", nx, "실제 팀은 main에 바로 push하지 않고 브랜치와 Pull Request를 써요. 그 흐름은 03 브랜치 덱의 7부에 있어요. 오늘 익힌 pull과 충돌 풀기는 거기서도 그대로 써요. PR 화면의 This branch has conflicts도 내 브랜치에서 git pull origin main으로 푸는 같은 방법이에요.")

# cheatsheet
ch = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};padding:112px 128px;display:flex;flex-direction:column;gap:40px">',
      f'<h2 style="font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>', '<div style="display:flex;flex-direction:row;gap:24px;flex:1">']
cards = [("준비", PUR, "팀장: 레포 만들기<br>Add README 켜기<br>Collaborators 초대<br><br>팀원: 초대 수락<br>git clone 주소"),
         ("설정 한 번", RED, "git config --global<br>pull.rebase false<br><br>안 하면<br>pull이 fatal로 멈춤"),
         ("다른 파일", GR, "push 거절<br>→ git pull origin main<br>→ 저절로 합쳐짐<br>→ git push origin main"),
         ("같은 줄", BL, "CONFLICT<br>→ 남길 줄만 두고<br>표시 세 줄 지우기<br>→ git add 파일<br>→ git commit -m<br>→ git push origin main")]
for h_, hc, body in cards:
    ch.append(f'<div style="flex:1;display:flex;flex-direction:column;gap:16px;background:#FFFFFF;border:2px solid {LINE};border-top:10px solid {hc};border-radius:20px;padding:32px 28px">'
              f'<h3 style="font-size:32px;font-weight:700;color:{hc}">{h_}</h3>'
              f'<p style="font-size:27px;line-height:1.7;color:{INK}">{body}</p></div>')
ch += ['</div>', f'<p style="font-size:28px;font-weight:700;color:{INK}">작업 전에 pull, 작게 자주 커밋, 거절되면 다시 pull.</p>']
W("cheatsheet", ch, "수업 끝에 이 장을 띄워 두고 팀별로 오늘 몇 번 거절됐는지, 충돌은 몇 번 풀었는지 이야기해 보게 하세요. 시간이 남으면 역할을 바꿔서 lee가 먼저 push하고 kim이 충돌을 풀어 봐요.")

# toc (now that ORDER is known)
pg = lambda sid: ORDER.index(sid) + 2  # toc itself is inserted at index 1
t = [f'<section id="toc" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};padding:96px 128px;display:flex;flex-direction:column;gap:40px">',
     f'<h2 style="font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>',
     '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:24px;flex:1">']
for i, (ic, c, h, s_, a, b) in enumerate(TOC_PARTS, 1):
    t.append(f'<div style="display:flex;flex-direction:column;gap:12px;background:#FFFFFF;border:2px solid {LINE};border-top:10px solid {c};border-radius:20px;padding:28px 32px">'
             f'<div style="display:flex;flex-direction:row;gap:14px;align-items:center"><p style="font-size:56px;font-weight:900;line-height:1.25;color:{c}">{i}</p>'
             f'<x-icon name="{ic}" style="width:44px;height:44px;color:{c}"></x-icon></div>'
             f'<h3 style="font-size:36px;font-weight:700;color:{INK}">{h}</h3>'
             f'<p style="font-size:28px;line-height:1.45;color:{SUB}">{s_}</p><div style="flex:1"></div>'
             f'<p style="font-size:24px;color:{MUTE}">{pg(a)}–{pg(b)}쪽</p></div>')
t += ['</div>', f'<p style="font-size:26px;color:{SUB}">마지막 {len(ORDER)+1}쪽은 한 장 요약이에요.</p>']
W("toc", t, "1부에서 레포를 만들고 셋이 clone해요. 2부와 3부가 오늘의 중심이에요. 2부는 서로 다른 파일을 고쳐서 저절로 합쳐지는 경우, 3부는 같은 줄을 고쳐서 충돌이 나는 경우예요. 4부는 팀 규칙과 막힐 때 볼 메시지예요.")
ORDER.remove("toc")
ORDER.insert(1, "toc")

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-10-29T03:00:00Z"}, "lists": "css", "title": "팀 레포로 함께 커밋하기", "order": ORDER,
        "sections": {"intro": {"description": "오늘 하는 일", "start": "cover"}, "setup": {"description": "팀 레포 준비", "start": "roles"},
                     "auto": {"description": "다른 파일은 저절로 합쳐져요", "start": "a1"}, "conflict": {"description": "같은 줄은 충돌", "start": "b1"},
                     "rules": {"description": "팀 규칙, 막힐 때, 요약", "start": "rules"}},
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
json.dump(deck, open(os.path.join(OUT, "deck.json"), "w"), ensure_ascii=False, indent=2)
print(len(ORDER), "slides")
