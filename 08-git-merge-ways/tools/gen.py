"""Generates every slide of the merge-ways deck and slides/deck.json.

One example for every method: A, B on main, then C on main and D, E on feature/login-button.
Each commit dot carries a letter and its hash sits under the dot. Elements keep the same id across
scenes so the magic transition animates only what the command changed.
Terminal output comes from tools/demo.sh (git 2.43).
Usage: python3 tools/gen.py slides
"""
import html, json, os, sys

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
INK, SUB, LINE = "#1D2330", "#4A5262", "#E1DED6"
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
TC = {"$": "#F2C46D", "o": "#D8DEE9", "g": "#7FD18B", "r": "#F28B82", "#": "#8C95A6", "H": "#FFE7A8"}


def e(s):
    return html.escape(s, quote=False)


def p(style, text, attrs=""):
    return f'<p{attrs} style="{style}">{text}</p>'


ORDER, SECTIONS = [], {}


def W(sid, parts, notes, section=None):
    if section:
        SECTIONS[section[0]] = {"description": section[1], "start": sid}
    ORDER.append(sid)
    with open(os.path.join(OUT, sid + ".html"), "w") as f:
        f.write("\n".join(parts) + f"\n<aside>{e(notes)}</aside>\n</section>\n")


def sec(sid, transition="fade", bg="#F6F5F1"):
    return f'<section id="{sid}" data-transition="{transition}" style="background:{bg};color:{INK};font-family:{SANS};padding:96px;display:flex;flex-direction:column">'


def head(eyebrow, title, color):
    return [p(f"position:absolute;left:96px;top:48px;width:1728px;font-size:26px;font-weight:700;color:{color}", e(eyebrow), ' id="eyebrow"'),
            f'<h2 id="title" style="position:absolute;left:96px;top:92px;width:1728px;font-size:56px;font-weight:700;line-height:1.2;color:{INK}">{title}</h2>']


def term_line(kind, text, size):
    t = e(text).replace("\t", "&#160;" * 8)
    lead = len(t) - len(t.lstrip(" "))
    t = "&#160;" * lead + t.lstrip(" ")
    if kind == "$":
        return p(f"font-size:{size[0]}px;font-weight:700;line-height:1.35;white-space:nowrap;color:{TC['$']}", "$ " + t)
    mark = "background:rgba(242,196,109,0.22);border-radius:6px;margin:0 -8px;padding:0 8px;font-weight:700;" if kind == "H" else ""
    return p(f"font-size:{size[1]}px;line-height:1.35;white-space:pre;{mark}color:{TC[kind]}", t if t else "&#160;")


def terminal(lines, left=96, top=196, w=1728, size=(30, 24), tid="term", h=None, attrs=""):
    hh = f"height:{h}px;" if h else ""
    o = [f'<div id="{tid}"{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;{hh}background:#1B2029;border-radius:20px;padding:18px 32px;display:flex;flex-direction:column;gap:2px;font-family:{MONO};font-variant-ligatures:none">']
    o += [term_line(k, t, size) for k, t in lines]
    o.append('</div>')
    return o


PANEL = dict(left=96, top=436, w=1728, h=428)


def scene(sid, eyebrow, title, term=None, caption="", color=BL, transition="magic", section=None, size=(30, 24)):
    o = [sec(sid, transition)] + head(eyebrow, title, color)
    if term:
        o += terminal(term, size=size)
    o.append(f'<div id="panel" style="position:absolute;left:{PANEL["left"]}px;top:{PANEL["top"]}px;width:{PANEL["w"]}px;height:{PANEL["h"]}px;background:#FDFCF9;border:2px solid {LINE};border-radius:24px"></div>')
    if caption:
        o.append(p(f"position:absolute;left:96px;top:900px;width:1728px;font-size:34px;font-weight:700;line-height:1.4;color:{INK}", caption, ' id="caption" data-build-in="rise"'))
    return o


# ---------- commit graph ----------
BIG = dict(x0=360, step=250, up=580, main=700, r=32, lf=30, hf=22, tf=26, th=46)


def tag_w(text, tf):
    return round(len(text) * tf * 0.6 + tf * 1.2)


def graph(nodes, edges, tags=(), head_tag=None, g=BIG, pre=""):
    """nodes: {key: (col, lane, colour, kind, letter, hash)}  kind: n | merge | ghost (not committed yet) | gone (old copy) | far (only on GitHub)
    edges: [(from_key, to_key)]   tags: [(name, key, kind)] stacked in list order per node
    head_tag: name of the tag HEAD points at"""
    o = []
    X = lambda c: g["x0"] + c * g["step"]
    r = g["r"]
    for a, b in edges:
        ca, la, cola, ka = nodes[a][:4]
        cb, lb, colb, kb = nodes[b][:4]
        x1, y1, x2, y2 = X(ca), g[la], X(cb), g[lb]
        light = COL[cola if (lb == "main" and la != "main") else colb][1]
        dashed = kb in ("ghost", "gone", "far") or ka == "gone"
        if "gone" in (ka, kb):
            light = COL["gray"][1]
        w = max(3, r // 5)
        if y1 == y2:
            st = f"border-top:{w}px dashed {light}" if dashed else f"background:{light}"
            o.append(f'<div id="{pre}e-{a}-{b}" style="position:absolute;left:{x1 + r}px;top:{y1 - w // 2}px;width:{x2 - x1 - 2 * r}px;height:{w}px;{st}"></div>')
        else:
            dash = ";border-style:dashed" if dashed else ""
            o.append(f'<x-connector id="{pre}e-{a}-{b}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" style="color:{light};border-width:{w}px{dash}"></x-connector>')
    for k, (col, lane, colour, kind, letter, h) in nodes.items():
        x, y = X(col), g[lane]
        fill = COL[colour][0]
        bw = max(3, r // 6)
        st = {"merge": f"background:#FFFFFF;border:{r * 3 // 10}px solid {fill};color:{fill}",
              "ghost": f"background:#FDFCF9;border:{bw}px dashed {fill};color:{fill}",
              "far": f"background:#FDFCF9;border:{bw}px dashed {fill};color:{fill}",
              "gone": f"background:#FDFCF9;border:{bw}px dashed #B4BAC5;color:#9AA0AB"}.get(kind, f"background:{fill};border:{bw}px solid {fill};color:#FFFFFF")
        o.append(f'<div id="{pre}n-{k}" style="position:absolute;left:{x - r}px;top:{y - r}px;width:{2 * r}px;height:{2 * r}px;border-radius:50%;{st};display:flex;align-items:center;justify-content:center">'
                 + p(f"font-family:{MONO};font-size:{g['lf']}px;font-weight:700;line-height:1;color:inherit", e(letter)) + '</div>')
        if g["hf"] and h:
            hc = "#9AA0AB" if kind in ("ghost", "gone", "far") else INK
            o.append(p(f"position:absolute;left:{x - 80}px;top:{y + r + 2}px;width:160px;font-family:{MONO};font-size:{g['hf']}px;font-weight:700;text-align:center;color:{hc}", e(h), f' id="{pre}h-{k}"'))
    stack = {}
    tf, th = g["tf"], g["th"]
    for name, k, kind in tags:
        col, lane = nodes[k][:2]
        i = stack.get(k, 0)
        stack[k] = i + 1
        x = X(col)
        w = tag_w(name, tf)
        below = g[lane] + r + (g["hf"] + 14 if g["hf"] else 10)
        top = (below + i * th) if lane == "main" else (g[lane] - r - round(tf * 1.5) - 10 - i * th)
        tid = pre + "t-" + name.replace("/", "-")
        o.append(p(f"position:absolute;left:{x - w // 2}px;top:{top}px;width:{w}px;font-family:{MONO};font-size:{tf}px;font-weight:700;line-height:1.5;text-align:center;border-radius:8px;{TAG[kind]}", e(name), f' id="{tid}"'))
        if name == head_tag:
            hw = tag_w("◀ HEAD", tf)
            o.append(p(f"position:absolute;left:{x - w // 2 + w + 10}px;top:{top}px;width:{hw}px;font-family:{MONO};font-size:{tf}px;font-weight:700;line-height:1.5;text-align:center;border-radius:8px;background:{INK};color:#F6F5F1", "◀ HEAD", f' id="{pre}t-head"'))
    return o


def legend(rows, top=470):
    """The commit list card at the right of the panel. rows: [(letter, colour, message)]"""
    o = [f'<div id="legend" style="position:absolute;left:1430px;top:{top}px;width:376px;background:#FFFFFF;border:2px solid {LINE};border-radius:18px;padding:18px 24px;display:flex;flex-direction:column;gap:10px">',
         p(f"font-size:22px;font-weight:700;color:{SUB}", "커밋 메시지")]
    for letter, colour, msg in rows:
        o.append(f'<div style="display:flex;flex-direction:row;gap:14px;align-items:center"><div style="width:34px;height:34px;flex:none;border-radius:50%;background:{COL[colour][0]};display:flex;align-items:center;justify-content:center">'
                 + p(f"font-family:{MONO};font-size:18px;font-weight:700;line-height:1;color:#FFFFFF", letter) + '</div>'
                 + p(f"font-size:24px;line-height:1.3;color:{INK}", e(msg)) + '</div>')
    o.append('</div>')
    return o


def num(i, color, size=56):
    return p(f"width:{size + 16}px;height:{size + 16}px;flex:none;border-radius:50%;background:{color};color:#FFFFFF;font-size:{size * 0.6:.0f}px;font-weight:900;line-height:{size + 16}px;text-align:center", str(i))


# ---------- the story (hashes from tools/demo.sh) ----------
A, B, C, D, E_ = "9f452aa", "6d19f01", "d51d818", "6a9792d", "3573c9a"
NM, M, D2, E2, S = "d847d12", "8818bb8", "a40dc47", "6852264", "8a6fe21"
PC, PD, PM, PD2 = "c4ea069", "521bc6f", "be1e0e1", "b63da4a"
GS = "d6514f3"
FB = "feature/login-button"
OFB = "origin/feature/login-button"

n_ab = {"A": (0, "main", "main", "n", "A", A), "B": (1, "main", "main", "n", "B", B)}
n_de = dict(n_ab, D=(2, "up", "green", "n", "D", D), E=(3, "up", "green", "n", "E", E_))
e_de = [("A", "B"), ("B", "D"), ("D", "E")]
n_split = dict(n_de, C=(2, "main", "main", "n", "C", C))
e_split = e_de + [("B", "C")]
LEG = [("A", "main", "feat: 로그인 화면 추가"), ("B", "main", "feat: 아이디 입력 추가"), ("D", "green", "feat: 로그인 버튼 추가"), ("E", "green", "fix: 버튼 글자 고치기")]
LEG_C = LEG[:2] + [("C", "main", "docs: README 추가")] + LEG[2:]

# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#8FB3FF;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
       '<h1 style="font-size:104px;font-weight:900;line-height:1.1;color:#F6F5F1">합치는 방법,<br>눈으로 비교하기</h1>',
       '<p style="font-size:40px;line-height:1.4;color:#BFC6D4">fast-forward, merge,<br>rebase, squash</p>']
cov.append(f'<div style="position:absolute;left:1080px;top:300px;width:700px;height:480px;background:#252B36;border-radius:24px;padding:40px 44px;display:flex;flex-direction:column;gap:10px;font-family:{MONO}">')
for k, l in [("$", "$ git merge 브랜치"), ("#", "  이름표만 앞으로, 또는 합치기 커밋"), ("$", "$ git rebase main"), ("#", "  커밋을 뒤로 옮겨 붙이기"),
             ("$", "$ git merge --squash 브랜치"), ("#", "  여러 커밋을 하나로")]:
    cov.append(p(f"font-size:32px;line-height:1.45;white-space:pre;font-weight:700;color:{TC[k]}", e(l)))
cov.append('</div>')
W("cover", cov, "03에서 merge를 배울 때 fast-forward와 merge 커밋 두 가지를 봤어요. 오늘은 같은 예시 하나로 합치는 방법 네 가지를 나란히 놓고 결과 그림을 비교해요. git pull이 이 중 무엇을 하는지, GitHub PR의 Merge 버튼 세 개가 각각 무엇인지도 이어서 봐요.", ("intro", "같은 예시 하나"))

# toc is written last, after page numbers are known
ORDER.append("toc")

# ---------- intro: the example ----------
EB0 = "같은 예시 하나로 비교해요"
o = scene("story1", EB0, "A, B까지 main에 있어요", [("$", "git log --oneline"), ("o", f"{B} (HEAD -> main) feat: 아이디 입력 추가"), ("o", f"{A} feat: 로그인 화면 추가")],
          "점 안의 글자가 커밋 이름이에요. 아래 글자는 해시예요.", color=SUB)
o += graph(n_ab, [("A", "B")], [("main", "B", "main")], "main")
o += legend(LEG[:2])
W("story1", o, "오늘은 hello-git 말고 연습용 저장소 merge-lab을 새로 만들어 써요. rebase처럼 기록을 바꾸는 명령도 해 보니까, 수업 저장소와 팀 레포는 건드리지 않아요. login.md 하나에 커밋 두 개를 쌓았어요. 그래프는 03처럼 왼쪽이 먼저 한 커밋이에요. 이 덱은 커밋마다 A, B 같은 글자를 붙여서 부르고, 아래에 진짜 해시를 적었어요.")

o = scene("story2", EB0, "브랜치에서 D, E를 커밋해요", [("$", f"git checkout -b {FB}"), ("o", f"[{FB} {D}] feat: 로그인 버튼 추가"), ("o", f"[{FB} {E_}] fix: 버튼 글자 고치기")],
          "로그인 버튼을 만들고, 글자를 한 번 더 고쳤어요.", color=SUB)
o += graph(n_de, e_de, [("main", "B", "main"), (FB, "E", "green")], FB)
o += legend(LEG)
W("story2", o, "브랜치를 만들고 login.md에 로그인 버튼 줄을 더해 커밋했어요(D). 버튼 글자를 [로그인] 버튼으로 고쳐 한 번 더 커밋했어요(E). 화면 폭 때문에 add와 commit 명령 줄은 뺐어요. 그다음 git checkout main으로 main에 돌아와 있어요.")

# ---------- part 1: not diverged ----------
EB1 = "1. 갈라지지 않았을 때"
o = scene("ff", EB1, "fast-forward: main 이름표만 앞으로 가요", [("$", "git checkout main"), ("$", f"git merge {FB}"), ("o", f"Updating {B}..{E_}"), ("g", "Fast-forward")],
          "main에 새 커밋이 없으면 새 커밋을 만들지 않아요.", color=C_FF, section=("plain", "갈라지지 않았을 때"))
o += graph(n_de, e_de, [(FB, "E", "green"), ("main", "E", "main")], "main")
W("ff", o, "03에서 본 빨리 감기(Fast-forward)예요. B 뒤로 main에는 커밋이 없었어요. 그래서 Git은 main 이름표를 E로 옮기기만 해요. 커밋 해시는 하나도 바뀌지 않아요. 출력의 파일 목록 줄은 뺐어요.")

n_noff = dict(n_de, NM=(4, "main", "main", "merge", "M", NM))
o = scene("noff", EB1, "--no-ff: 그래도 합치기 커밋을 만들어요", [("$", f"git merge --no-ff {FB}"), ("o", "Merge made by the 'ort' strategy."), ("$", "git log --oneline"),
          ("o", f"{NM} (HEAD -> main) Merge branch '{FB}'")],
          "브랜치에서 한 일이 한 덩어리로 보여요. GitHub PR 버튼도 이렇게 합쳐요.", color=C_FF)
o += graph(n_noff, e_de + [("B", "NM"), ("E", "NM")], [(FB, "E", "green"), ("main", "NM", "main")], "main")
W("noff", o, "앞 장과 같은 상태에서 --no-ff를 붙였어요. no fast-forward, 빨리 감기를 하지 말라는 뜻이에요. fast-forward가 되는 상황에서도 부모가 B와 E 둘인 합치기 커밋 M을 만들어요. 나중에 기록을 보면 D, E가 브랜치에서 온 커밋이라는 게 남아요. 메시지 편집기가 열리면 그대로 저장하고 닫아요. GitHub의 Create a merge commit 버튼이 항상 이 방식이에요(5부).")

# ---------- part 2: diverged ----------
EB2 = "2. 갈라졌을 때"
o = scene("split", EB2, "main에 C가 생기면 길이 갈라져요", [("$", "git add README.md"), ("$", 'git commit -m "docs: README 추가"'), ("o", f"[main {C}] docs: README 추가")],
          "이제 이름표만 옮겨서는 C와 D, E를 같이 담을 수 없어요.", color=SUB, transition="fade", section=("split", "갈라졌을 때"))
o += graph(n_split, e_split, [("main", "C", "main"), (FB, "E", "green")], "main")
o += legend(LEG_C)
W("split", o, "다시 story2 상태로 돌아가서, 이번엔 main에서 README.md를 만들어 커밋했어요(C). 팀에서 내가 브랜치에서 일하는 동안 다른 사람 작업이 main에 들어온 모습과 같아요. 이 장 그림이 이 덱의 출발점이에요. 다음 장부터 이 상태에서 merge, rebase, squash를 하나씩 해 봐요.")

n_merge = dict(n_split, M=(4, "main", "main", "merge", "M", M))
o = scene("merge", EB2, "merge: 두 길을 잇는 합치기 커밋이 생겨요", [("$", f"git merge {FB}"), ("o", "Merge made by the 'ort' strategy."), ("$", "git log --oneline"),
          ("o", f"{M} (HEAD -> main) Merge branch '{FB}'")],
          "M의 부모는 C와 E 둘이에요. D, E 해시는 그대로예요.", color=C_MG)
o += graph(n_merge, e_split + [("C", "M"), ("E", "M")], [("main", "M", "main"), (FB, "E", "green")], "main")
W("merge", o, "03의 갈라진 길 파트와 06의 pull에서 본 합치기 커밋이에요. 흰 점이 합치기 커밋이에요. 원래 커밋은 하나도 건드리지 않고, 둘을 잇는 커밋 하나를 더해요. 그래서 이미 push한 커밋이 있어도 안전해요. log 출력 아래쪽 줄은 뺐어요.")

n_rb = dict(n_split, Dx=(2, "up", "gray", "gone", "D", ""), Ex=(3, "up", "gray", "gone", "E", ""),
            D=(3, "main", "green", "n", "D'", D2), E=(4, "main", "green", "n", "E'", E2))
e_rb = [("A", "B"), ("B", "C"), ("C", "D"), ("D", "E"), ("B", "Dx"), ("Dx", "Ex")]
o = scene("rb1", EB2, "rebase: D, E를 C 뒤로 옮겨 붙여요", [("$", f"git checkout {FB}"), ("$", "git rebase main"), ("g", f"Successfully rebased and updated refs/heads/{FB}.")],
          "옛 D, E는 점선으로 남고, 같은 내용의 새 커밋 D', E'가 생겨요.", color=C_RB)
o += graph(n_rb, e_rb, [("main", "C", "main"), (FB, "E", "green")], FB)
W("rb1", o, "다시 split 상태에서 시작해요. rebase는 브랜치에서 쳐요. git rebase main은 내 브랜치 커밋을 main 끝(C) 뒤로 하나씩 다시 만들어 붙여요. 받침(base)을 바꾼다는 뜻이에요. 옛 D, E는 이제 어느 이름표도 가리키지 않아서 점선으로 그렸어요. 진짜 터미널에서는 Rebasing (1/2) 같은 진행 줄이 잠깐 보였다가 지워져요.")

o = [sec("rb-hash")] + head(EB2, "rebase하면 커밋 해시가 바뀌어요", C_RB)
o += [p(f"position:absolute;left:96px;top:226px;width:846px;font-size:28px;font-weight:700;color:{SUB}", "rebase 전")]
o += terminal([("$", "git log --oneline"), ("H", f"{E_} (HEAD -> {FB}) fix: 버튼 글자 고치기"), ("H", f"{D} feat: 로그인 버튼 추가"),
               ("o", f"{B} feat: 아이디 입력 추가"), ("o", f"{A} feat: 로그인 화면 추가")], left=96, top=276, w=846, size=(26, 21), tid="t1")
o += [p(f"position:absolute;left:978px;top:226px;width:846px;font-size:28px;font-weight:700;color:{C_RB}", "rebase 뒤")]
o += terminal([("$", "git log --oneline"), ("H", f"{E2} (HEAD -> {FB}) fix: 버튼 글자 고치기"), ("H", f"{D2} feat: 로그인 버튼 추가"),
               ("o", f"{C} (main) docs: README 추가"), ("o", f"{B} feat: 아이디 입력 추가")], left=978, top=276, w=846, size=(26, 21), tid="t2")
for i, (old, new, l1, l2) in enumerate([(D, D2, "D", "D'"), (E_, E2, "E", "E'")]):
    y = 600 + i * 130
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:96px;top:{y}px;width:1728px;height:110px;display:flex;flex-direction:row;align-items:center;gap:28px;background:#FFFFFF;border:2px solid {LINE};border-radius:20px;padding:0 40px">'
             + f'<div style="width:64px;height:64px;flex:none;border-radius:50%;background:{GR};display:flex;align-items:center;justify-content:center">' + p(f"font-family:{MONO};font-size:28px;font-weight:700;line-height:1;color:#FFFFFF", l1) + '</div>'
             + p(f"font-family:{MONO};font-size:36px;font-weight:700;color:#9AA0AB;text-decoration:line-through", old)
             + '<x-shape kind="arrow-right" style="width:70px;height:40px;background:' + C_RB + '"></x-shape>'
             + f'<div style="width:64px;height:64px;flex:none;border-radius:50%;background:{GR};display:flex;align-items:center;justify-content:center">' + p(f"font-family:{MONO};font-size:26px;font-weight:700;line-height:1;color:#FFFFFF", l2) + '</div>'
             + p(f"font-family:{MONO};font-size:36px;font-weight:700;color:{INK}", new)
             + p(f"flex:1;text-align:right;font-size:28px;color:{SUB}", "메시지와 바뀐 내용은 같아요") + '</div>')
o.append(p(f"position:absolute;left:96px;top:900px;width:1728px;font-size:34px;font-weight:700;line-height:1.4;color:{INK}", "부모가 B에서 C로 바뀌어서, Git에게는 다른 커밋이에요.", ' data-build-in="rise order 3"'))
W("rb-hash", o, "커밋 해시는 내용, 메시지, 날짜, 부모 커밋으로 정해져요. rebase는 부모를 바꿔 다시 만들기 때문에 해시가 새로 나와요. 내 컴퓨터에만 있는 커밋이면 문제가 없어요. 이미 push해서 팀원이 옛 D, E를 받아 갔다면 팀원 기록과 어긋나요. 6부에서 이 장면을 다시 봐요.")

n_rb2 = {k: v for k, v in n_rb.items() if k not in ("Dx", "Ex")}
o = scene("rb2", EB2, "main에서 merge하면 fast-forward로 끝나요", [("$", "git checkout main"), ("$", f"git merge {FB}"), ("o", f"Updating {C}..{E2}"), ("g", "Fast-forward")],
          "합치기 커밋 없이 기록이 한 줄이 됐어요.", color=C_RB)
o += graph(n_rb2, [("A", "B"), ("B", "C"), ("C", "D"), ("D", "E")], [(FB, "E", "green"), ("main", "E", "main")], "main")
W("rb2", o, "rebase 뒤에는 브랜치가 C 바로 뒤에 붙어 있어서 1부의 fast-forward와 같은 모양이에요. rebase는 합치기 전에 브랜치를 최신 main 뒤로 옮기는 일이고, 합치는 건 여전히 merge예요. 점선이던 옛 D, E는 이름표가 없어서 그래프에서 보이지 않아요.")

n_sq = dict(n_split, S=(3, "main", "teal", "ghost", "S", ""))
BX = lambda c: BIG["x0"] + c * BIG["step"]
box = [f'<div id="sqbox" style="position:absolute;left:{BX(2) - 90}px;top:538px;width:{BIG["step"] + 180}px;height:114px;border:4px dashed {TEAL};border-radius:28px"></div>',
       f'<x-connector id="sqarrow" x1="{BX(3) - 70}" y1="652" x2="{BX(3) - 30}" y2="672" head="end" style="color:{TEAL};border-width:5px"></x-connector>']
o = scene("sq1", EB2, "squash: D, E의 변경을 모아 대기실에 올려요", [("$", f"git merge --squash {FB}"), ("o", "Automatic merge went well; stopped before committing as requested"), ("o", "Squash commit -- not updating HEAD")],
          "아직 커밋 전이에요. git status에 Changes to be committed로 보여요.", color=C_SQ)
o += graph(n_sq, e_split + [("C", "S")], [("main", "C", "main"), (FB, "E", "green")], "main")
o += box
W("sq1", o, "다시 split 상태에서 main에 있어요. --squash는 브랜치의 변경을 모두 모아 대기실(02의 ② 칸)에 올리고 멈춰요. 커밋은 직접 해요. 출력 첫 줄은 자동 합치기가 잘 됐고 요청대로 커밋 전에 멈췄다는 뜻이에요. 둘째 줄은 HEAD를 옮기지 않았다는 뜻이에요.")

n_sq2 = dict(n_split, S=(3, "main", "teal", "n", "S", S))
o = scene("sq2", EB2, "커밋하면 S 하나가 생겨요", [("$", 'git commit -m "feat: 로그인 버튼 추가"'), ("o", f"[main {S}] feat: 로그인 버튼 추가")],
          "S의 부모는 C 하나예요. 브랜치의 D, E와 선으로 이어지지 않아요.", color=C_SQ)
o += graph(n_sq2, e_split + [("C", "S")], [("main", "S", "main"), (FB, "E", "green")], "main")
o += box
W("sq2", o, "커밋 두 개(D, E)의 변경이 커밋 하나(S)로 main에 들어갔어요. 버튼을 만들다 고친 과정은 main 기록에 남지 않고 결과만 남아요. 그래서 작은 커밋이 많은 브랜치를 깔끔하게 합칠 때 써요. 메시지는 브랜치에서 한 일을 한 줄로 적어요. 출력의 1 file changed 줄은 뺐어요.")

o = scene("sq3", EB2, "squash 뒤에는 브랜치가 -d로 안 지워져요", [("$", f"git branch -d {FB}"), ("r", f"error: the branch '{FB}' is not fully merged."),
          ("o", f"If you are sure you want to delete it, run 'git branch -D {FB}'")],
          "Git은 D, E가 main에 없다고 봐요. 내용이 들어간 걸 확인했으면 -D로 지워요.", color=C_SQ)
o += graph(n_sq2, e_split + [("C", "S")], [("main", "S", "main"), (FB, "E", "green")], "main")
o += box
W("sq3", o, "-d는 합쳐진 브랜치만 지워요. Git은 커밋을 선으로 따라가서 합쳐졌는지 봐요. S는 D, E와 이어지지 않아서 합쳐지지 않은 걸로 보여요. git log --oneline이나 파일 내용으로 변경이 main에 있는 걸 확인한 뒤 git branch -D feature/login-button으로 지워요. 대문자 -D는 확인 없이 지우니 squash 뒤에만 써요.")

# ---------- part 3: compare ----------
EB3 = "3. 한눈에 비교"


def mini(left, top, nodes, edges, pre, tags=()):
    g = dict(x0=left + 70, step=112, up=top + 60, main=top + 150, r=22, lf=19, hf=0, tf=18, th=30)
    return graph(nodes, edges, tags, None, g, pre)


cards = [("fast-forward", C_FF, "갈라지지 않았을 때", {"A": (0, "main", "main", "n", "A", ""), "B": (1, "main", "main", "n", "B", ""), "D": (2, "main", "green", "n", "D", ""), "E": (3, "main", "green", "n", "E", "")},
          [("A", "B"), ("B", "D"), ("D", "E")], "새 커밋 없음, 이름표만 이동"),
         ("merge", C_MG, "--no-ff도 같은 모양", {**{k: (v[0], v[1], v[2], v[3], v[4], "") for k, v in n_merge.items()}},
          e_split + [("C", "M"), ("E", "M")], "합치기 커밋 M, D, E 그대로"),
         ("rebase", C_RB, "옮겨 붙인 뒤 fast-forward", {k: (v[0], v[1], v[2], v[3], v[4], "") for k, v in n_rb2.items()},
          [("A", "B"), ("B", "C"), ("C", "D"), ("D", "E")], "한 줄, D', E' 해시가 새로 생김"),
         ("squash", C_SQ, "변경을 모아 커밋 하나로", {**{k: (v[0], v[1], v[2], v[3], v[4], "") for k, v in n_sq2.items()}, "D": (2, "up", "gray", "n", "D", ""), "E": (3, "up", "gray", "n", "E", "")},
          e_split + [("C", "S")], "한 줄, main에는 S 하나만")]
o = [sec("cmp", "fade")] + head(EB3, "같은 출발점, 네 가지 결과", SUB)
for i, (name, c, sub, nodes, edges, res) in enumerate(cards):
    left, top = 96 + (i % 2) * 876, 220 + (i // 2) * 410
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:{left}px;top:{top}px;width:852px;height:390px;background:#FFFFFF;border:2px solid {LINE};border-top:10px solid {c};border-radius:20px"></div>')
    o.append(p(f"position:absolute;left:{left + 32}px;top:{top + 24}px;width:780px;font-size:34px;font-weight:700;color:{c}", f'{e(name)} <span style="font-size:24px;font-weight:500;color:{SUB}">{e(sub)}</span>', f' data-build-in="rise order {i + 1}"'))
    mg = mini(left + 30, top + 70, nodes, edges, f"c{i}")
    o += [x.replace(' id="', f' data-build-in="rise order {i + 1}" id="', 1) for x in mg]
    o.append(p(f"position:absolute;left:{left + 32}px;top:{top + 318}px;width:780px;font-size:28px;font-weight:700;color:{INK}", e(res), f' data-build-in="rise order {i + 1}"'))
W("cmp", o, "1부와 2부의 결과를 나란히 놓았어요. 모두 같은 A, B, C, D, E에서 출발했어요. 다 합친 뒤 login.md 내용은 넷 다 같아요. 다른 건 기록 모양이에요. VS Code Git Graph(05)로 열어 보면 이 그림과 같은 모양으로 보여요.", ("compare", "한눈에 비교"))

rows = [("방법", "명령", "새로 생기는 커밋", "D, E 해시", "main 기록"),
        ("fast-forward", "git merge 브랜치", "없음", "그대로", "한 줄"),
        ("merge", "git merge 브랜치\ngit merge --no-ff 브랜치", "합치기 커밋 M", "그대로", "두 줄이 만나요"),
        ("rebase", "git rebase main\n(브랜치에서)", "D', E'", "바뀌어요", "한 줄"),
        ("squash", "git merge --squash 브랜치\ngit commit -m \"...\"", "S 하나", "main에 없어요", "한 줄, 커밋 하나")]
o = [sec("cmp-table", "fade")] + head(EB3, "표로 다시 보기", SUB)
o.append('<div style="position:absolute;left:96px;top:220px;width:1728px;display:flex;flex-direction:column;gap:12px">')
widths = [260, 520, 330, 270, 348]
mcol = {"fast-forward": C_FF, "merge": C_MG, "rebase": C_RB, "squash": C_SQ}
for ri, row in enumerate(rows):
    bg = "#E9E7E0" if ri == 0 else "#FFFFFF"
    attrs = f' data-build-in="rise order {ri}"' if ri else ""
    o.append(f'<div{attrs} style="display:flex;flex-direction:row;align-items:center;background:{bg};border:2px solid {LINE};border-radius:16px;padding:{12 if ri == 0 else 18}px 24px;min-height:{60 if ri == 0 else 120}px">')
    for ci, cell in enumerate(row):
        if ri == 0:
            st = f"font-size:24px;font-weight:700;color:{SUB}"
        elif ci == 0:
            st = f"font-size:30px;font-weight:700;color:{mcol[cell]}"
        elif ci == 1:
            st = f"font-family:{MONO};font-size:24px;font-weight:700;line-height:1.5;color:{INK}"
        else:
            hot = cell in ("바뀌어요", "main에 없어요")
            st = f"font-size:28px;font-weight:{700 if hot else 500};color:{RED if hot else INK}"
        o.append(p(f"width:{widths[ci]}px;flex:none;{st}", "<br>".join(e(x) for x in cell.split("\n"))))
    o.append('</div>')
o.append('</div>')
W("cmp-table", o, "D, E 해시 칸을 봐요. merge와 fast-forward는 원래 커밋을 그대로 써요. rebase는 새 커밋을 만들어서 해시가 바뀌어요. squash는 D, E 대신 S를 만들어서 D, E가 main 기록에 들어가지 않아요. 해시가 바뀌거나 사라지는 방법은 이미 push한 커밋에 쓰면 팀원 기록과 어긋나요.")

# ---------- part 4: git pull ----------
EB4 = "4. git pull은 무엇을 하나"
n_pl = {"A": (0, "main", "main", "n", "A", A), "B": (1, "main", "main", "n", "B", B), "C": (2, "main", "purple", "far", "C", PC), "D": (2, "up", "main", "n", "D", PD)}
e_pl = [("A", "B"), ("B", "C"), ("B", "D")]
o = scene("pl0", EB4, "pull도 합치기예요", [("$", "git fetch origin"), ("$", "git log --oneline"), ("o", f"{PD} (HEAD -> main) feat: 로그인 버튼 추가"),
          ("$", "git log --oneline origin/main"), ("o", f"{PC} (origin/main) docs: README 추가")],
          "GitHub에는 팀원 lee의 C, 내 main에는 D. 내 컴퓨터와 GitHub이 갈라졌어요.", color=C_PL, section=("pull", "git pull"), size=(28, 22))
o += graph(n_pl, e_pl, [("origin/main", "C", "origin"), ("main", "D", "main")], "main")
W("pl0", o, "이번엔 브랜치 대신 main끼리 갈라진 상황이에요. lee가 README 추가(C)를 먼저 push했고, 나는 main에서 바로 로그인 버튼(D)을 커밋했어요. push는 06에서 본 것처럼 거절돼요. git pull은 git fetch로 C를 받아 온 뒤 내 main과 합쳐요. 어떻게 합칠지는 pull 설정이 정해요. 실습 저장소가 달라서 C, D 해시가 2부와 달라요. log 출력 아래쪽 줄은 뺐어요.")

o = [sec("pl-none")] + head(EB4, "설정이 없으면 pull이 멈추고 세 가지를 알려 줘요", C_PL)
o += terminal([("$", "git pull origin main"), ("o", "hint: You have divergent branches and need to specify how to reconcile them."),
               ("o", "hint: You can do so by running one of the following commands sometime before"), ("o", "hint: your next pull:"),
               ("H", "hint:   git config pull.rebase false  # merge"), ("H", "hint:   git config pull.rebase true   # rebase"),
               ("H", "hint:   git config pull.ff only       # fast-forward only"), ("r", "fatal: Need to specify how to reconcile divergent branches.")],
              top=200, size=(28, 24))
trio = [("pull.rebase false", "merge로 합쳐요", "수업 설정", C_MG), ("pull.rebase true", "rebase로 옮겨 붙여요", "보기만 해요", C_RB), ("pull.ff only", "fast-forward만 받아요", "보기만 해요", C_FF)]
for i, (k, v, tag, c) in enumerate(trio):
    left = 96 + i * 588
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:{left}px;top:590px;width:552px;height:240px;background:#FFFFFF;border:2px solid {LINE};border-top:10px solid {c};border-radius:20px;padding:24px 30px;display:flex;flex-direction:column;gap:12px">'
             + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{c}", e(k)) + p(f"font-size:32px;font-weight:700;color:{INK}", e(v))
             + '<div style="flex:1"></div>' + p(f"font-size:24px;font-weight:700;color:{'#FFFFFF' if i == 0 else SUB};background:{c if i == 0 else '#EEEFF2'};border-radius:8px;padding:2px 14px;align-self:flex-start", e(tag)) + '</div>')
o.append(p(f"position:absolute;left:96px;top:870px;width:1728px;font-size:34px;font-weight:700;line-height:1.4;color:{INK}", "세 줄이 곧 이 덱에서 본 합치는 방법이에요.", ' data-build-in="rise order 4"'))
W("pl-none", o, "06에서 본 그 메시지예요. 그때는 해결만 봤어요. 힌트 세 줄을 읽어 보면 merge, rebase, fast-forward only 중에서 고르라는 뜻이에요. 우리 과정은 06에서 git config --global pull.rebase false로 첫째 줄을 골랐어요. From 줄과 힌트 아래쪽 줄은 뺐어요.")

n_pl_m = dict(n_pl, C=(2, "main", "purple", "n", "C", PC), PM=(3, "main", "main", "merge", "M", PM))
o = scene("pl-false", EB4, "pull.rebase false: 합치기 커밋으로 합쳐요", [("$", "git config --global pull.rebase"), ("o", "false"), ("$", "git pull origin main"), ("o", "Merge made by the 'ort' strategy.")],
          "내 D 해시가 그대로예요. 06에서 본 모양이에요.", color=C_MG, size=(28, 22))
o += graph(n_pl_m, e_pl + [("C", "PM"), ("D", "PM")], [("origin/main", "C", "origin"), ("main", "PM", "main")], "main")
W("pl-false", o, "git config --global pull.rebase처럼 값 없이 치면 지금 설정을 보여 줘요. false가 나오면 수업 설정이 돼 있는 거예요. pull이 2부의 merge와 같은 일을 해요. 합치기 커밋 메시지는 Merge branch 'main' of https://github.com/kim/merge-lab이에요. 이제 git push origin main을 하면 올라가요. From 줄과 파일 목록 줄은 뺐어요.")

n_pl_r = {"A": n_pl["A"], "B": n_pl["B"], "C": (2, "main", "purple", "n", "C", PC), "Dx": (2, "up", "gray", "gone", "D", ""), "D": (3, "main", "main", "n", "D'", PD2)}
o = scene("pl-true", EB4, "pull.rebase true: 내 커밋을 C 뒤로 옮겨요", [("#", "# pull.rebase true인 컴퓨터"), ("$", "git pull origin main"), ("g", "Successfully rebased and updated refs/heads/main."),
          ("$", "git log --oneline"), ("o", f"{PD2} (HEAD -> main) feat: 로그인 버튼 추가")],
          "기록은 한 줄이지만 D의 해시가 바뀌었어요.", color=C_RB, size=(28, 22))
o += graph(n_pl_r, [("A", "B"), ("B", "C"), ("C", "D"), ("B", "Dx")], [("origin/main", "C", "origin"), ("main", "D", "main")], "main")
W("pl-true", o, "보기만 하는 장이에요. 설정을 바꾸지 않아요. pull이 2부의 rebase와 같은 일을 해요. 아직 push하지 않은 D를 옮기는 거라 이 경우엔 문제가 없어요. 대신 충돌이 나면 rebase 충돌로 풀어야 해서 처음 배울 때 헷갈려요(6부). 회사마다 이 설정을 쓰는 팀도 있으니 이름은 알아 둬요.")

o = scene("pl-ff", EB4, "pull.ff only: 갈라졌으면 받지 않아요", [("#", "# pull.ff only인 컴퓨터"), ("$", "git pull origin main"), ("r", "fatal: Not possible to fast-forward, aborting.")],
          "갈라지지 않았을 때만 fast-forward로 받아요. 갈라지면 직접 골라야 해요.", color=C_FF, size=(28, 22))
o += graph(n_pl, e_pl, [("origin/main", "C", "origin"), ("main", "D", "main")], "main")
W("pl-ff", o, "보기만 하는 장이에요. 내 main에 새 커밋이 없으면 fast-forward로 받고, 갈라졌으면 아무것도 하지 않고 멈춰요. 그래프가 앞 장과 같은 건 실패해서 바뀐 게 없기 때문이에요. 힌트 줄(git merge --no-ff 또는 git rebase)은 뺐어요.")

o = [sec("pl-why")] + head(EB4, "수업은 pull.rebase false로 통일해요", C_MG)
why = [("CheckCircle", "내 커밋 해시가 그대로예요", "push한 커밋과 어긋나지 않아요"), ("Link", "합친 자리가 기록에 남아요", "합치기 커밋 M이 언제 합쳤는지 보여 줘요"),
       ("Wrench", "충돌을 푸는 방법이 하나예요", "03, 06처럼 고치고 add, commit")]
for i, (ic, h, s) in enumerate(why):
    left = 96 + i * 588
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:{left}px;top:240px;width:552px;height:400px;background:#FFFFFF;border:2px solid {LINE};border-top:10px solid {C_MG};border-radius:20px;padding:40px 36px;display:flex;flex-direction:column;gap:24px">'
             + f'<x-icon name="{ic}" style="width:72px;height:72px;color:{C_MG}"></x-icon>' + p(f"font-size:36px;font-weight:700;line-height:1.3;color:{INK}", e(h)) + p(f"font-size:28px;line-height:1.45;color:{SUB}", e(s)) + '</div>')
o += terminal([("$", "git config --global pull.rebase false")], left=96, top=700, w=1728, size=(34, 24), tid="cmd", attrs=' data-build-in="rise order 4"')
o.append(p(f"position:absolute;left:96px;top:830px;width:1728px;font-size:34px;font-weight:700;line-height:1.4;color:{INK}", "06에서 처음 한 번 설정했으면 그대로 둬요.", ' data-build-in="rise order 4"'))
W("pl-why", o, "pull.rebase false는 기록을 바꾸지 않는 방법이라 처음 배울 때 가장 안전해요. 기록이 조금 복잡해 보이는 대신, 내가 한 커밋이 사라지거나 해시가 바뀌는 일이 없어요. rebase가 나쁜 방법은 아니에요. push 전 내 커밋에만 쓰는 규칙을 지키면 기록이 깔끔해져요. 익숙해진 뒤 팀이 정한 방법을 따르면 돼요.")

# ---------- part 5: GitHub PR buttons ----------
EB5 = "5. GitHub PR의 Merge 버튼"
o = [sec("gh-btn")] + head(EB5, "PR의 Merge 버튼은 세 가지예요", PUR)
o.append(f'<div style="position:absolute;left:96px;top:240px;width:860px;height:700px;background:#FFFFFF;border:2px solid #D0D7DE;border-radius:20px"></div>')
o.append(p(f"position:absolute;left:136px;top:270px;width:780px;font-size:28px;font-weight:700;color:{INK}", "feat: 로그인 버튼 추가 #1"))
o.append(f'<div style="position:absolute;left:136px;top:330px;width:400px;height:64px;background:#1F883D;border-radius:10px;display:flex;flex-direction:row;align-items:center">'
         + p("flex:1;font-size:26px;font-weight:700;color:#FFFFFF;text-align:center", "Merge pull request") + '<div style="width:2px;height:64px;background:#17692F"></div>'
         + p("width:64px;font-size:24px;color:#FFFFFF;text-align:center", "▼") + '</div>')
opts = [("Create a merge commit", "합치기 커밋을 만들어요", "git merge --no-ff", C_MG), ("Squash and merge", "커밋 하나로 합쳐요", "git merge --squash", C_SQ),
        ("Rebase and merge", "옮겨 붙여요", "git rebase", C_RB)]
o.append(f'<div style="position:absolute;left:136px;top:410px;width:780px;height:500px;background:#FFFFFF;border:2px solid #D0D7DE;border-radius:14px"></div>')
for i, (en, ko, cmd, c) in enumerate(opts):
    top = 430 + i * 160
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:156px;top:{top}px;width:740px;height:140px;border-radius:12px;background:#F6F8FA;border-left:10px solid {c};padding:22px 28px;display:flex;flex-direction:column;gap:10px">'
             + p(f"font-size:30px;font-weight:700;color:{INK}", e(en)) + p(f"font-size:26px;color:{SUB}", e(ko)) + '</div>')
    o.append(f'<x-shape data-build-in="rise order {i + 1}" kind="arrow-right" style="position:absolute;left:930px;top:{top + 46}px;width:100px;height:48px;background:{c}"></x-shape>')
    o.append(p(f"position:absolute;left:1060px;top:{top + 30}px;width:764px;height:80px;font-family:{MONO};font-size:36px;font-weight:700;line-height:80px;padding:0 28px;border-radius:14px;background:#FFFFFF;border:2px solid {LINE};color:{c}", e(cmd), f' data-build-in="rise order {i + 1}"'))
W("gh-btn", o, "PR 화면 아래 초록 버튼 오른쪽 ▼를 누르면 세 가지가 나와요. 처음 고른 것이 기본값으로 남아요. Create a merge commit은 갈라지지 않았어도 늘 합치기 커밋을 만들어서 --no-ff와 같아요. Squash and merge는 2부의 squash, Rebase and merge는 2부의 rebase 뒤 fast-forward와 같아요. 저장소 설정에 따라 일부 버튼만 보일 수 있어요.", ("github", "GitHub PR 버튼"))

o = [sec("gh-res", "fade")] + head(EB5, "버튼마다 GitHub의 main 기록이 달라요", PUR)
gres = [("Create a merge commit", C_MG, {k: (v[0], v[1], v[2], v[3], v[4], "") for k, v in n_merge.items()}, e_split + [("C", "M"), ("E", "M")], "Merge pull request #1 from kim/feature/login-button"),
        ("Squash and merge", C_SQ, {k: (v[0], v[1], v[2], v[3], v[4], "") for k, v in n_split.items() if k not in ("D", "E")} | {"S": (3, "main", "teal", "n", "S", "")}, [("A", "B"), ("B", "C"), ("C", "S")], "feat: 로그인 버튼 추가 (#1)"),
        ("Rebase and merge", C_RB, cards[2][3], cards[2][4], "D', E' 해시가 새로 생겨요")]
for i, (name, c, nodes, edges, msg) in enumerate(gres):
    left = 96 + i * 588
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:{left}px;top:240px;width:552px;height:560px;background:#FFFFFF;border:2px solid {LINE};border-top:10px solid {c};border-radius:20px"></div>')
    o.append(p(f"position:absolute;left:{left + 28}px;top:270px;width:500px;font-size:30px;font-weight:700;color:{c}", e(name), f' data-build-in="rise order {i + 1}"'))
    g = dict(x0=left + 66, step=105, up=440, main=560, r=24, lf=20, hf=0, tf=18, th=30)
    o += [x.replace(' id="', f' data-build-in="rise order {i + 1}" id="', 1) for x in graph(nodes, edges, (), None, g, f"g{i}")]
    o.append(p(f"position:absolute;left:{left + 28}px;top:650px;width:496px;font-family:{MONO};font-size:22px;font-weight:700;line-height:1.45;color:{INK};background:#F3F2EE;border-radius:10px;padding:12px 16px", e(msg), f' data-build-in="rise order {i + 1}"'))
o.append(p(f"position:absolute;left:96px;top:880px;width:1728px;font-size:34px;font-weight:700;line-height:1.4;color:{INK}", "어느 버튼을 쓸지는 팀이 정해요. 정한 버튼 하나만 써요.", ' data-build-in="rise order 4"'))
W("gh-res", o, "그림은 GitHub에서 합친 뒤 GitHub 쪽 main 모양이에요. Create a merge commit 메시지는 03에서 본 Merge pull request #1 from kim/feature/login-button이에요. Squash and merge는 PR 제목 뒤에 (#1)을 붙인 커밋 하나가 생겨요. Rebase and merge는 갈라지지 않았어도 GitHub이 커밋을 새로 만들어서 해시가 바뀌어요. 한 팀이 버튼을 섞어 쓰면 기록 모양이 PR마다 달라져서 읽기 어려워요.")

o = [sec("gh-after")] + head(EB5, "Squash나 Rebase 버튼 뒤에는 -D로 지워요", PUR)
o += terminal([("$", "git checkout main"), ("$", "git pull origin main"), ("o", f"Updating {C}..{GS}"), ("g", "Fast-forward"), ("$", "git log --oneline"),
               ("o", f"{GS} (HEAD -> main, origin/main) feat: 로그인 버튼 추가 (#1)"), ("$", f"git branch -d {FB}"),
               ("r", f"error: the branch '{FB}' is not fully merged."), ("o", f"If you are sure you want to delete it, run 'git branch -D {FB}'")], top=210, size=(28, 24))
o.append(f'<div data-build-in="rise" style="position:absolute;left:96px;top:640px;width:1728px;height:180px;background:#FFFFFF;border:2px solid {LINE};border-left:10px solid {PUR};border-radius:20px;padding:28px 40px;display:flex;flex-direction:column;gap:12px">'
         + p(f"font-size:32px;font-weight:700;color:{INK}", "GitHub에서 PR이 Merged로 바뀐 걸 확인했으면 지워도 돼요.")
         + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{PUR}", e(f"git branch -D {FB}")) + '</div>')
W("gh-after", o, "03에서 배운 PR 뒤 순서(main으로 가서 pull, 브랜치 지우기) 그대로예요. Create a merge commit으로 합쳤으면 -d로 지워져요. Squash and merge나 Rebase and merge는 GitHub이 새 커밋을 만들어서, 내 컴퓨터의 브랜치 커밋은 main과 이어지지 않아요. 그래서 -d가 거절해요. PR 화면에 보라색 Merged 표시가 있으면 -D로 지워요. From 줄과 파일 목록 줄은 뺐어요.")

# ---------- part 6: conflicts and care ----------
EB6 = "6. 충돌과 주의"
o = [sec("cf-all")] + head(EB6, "충돌은 어느 방법이든 같은 줄이면 나요", RED)
for i, (who, line, c) in enumerate([("main의 login.md", "# 로그인 페이지", BL), ("feature/login-title의 login.md", "# 로그인하기", GR)]):
    top = 240 + i * 250
    o.append(f'<div style="position:absolute;left:96px;top:{top}px;width:600px;height:220px;background:#FFFFFF;border:2px solid {LINE};border-left:10px solid {c};border-radius:18px;padding:24px 30px;display:flex;flex-direction:column;gap:10px">'
             + p(f"font-size:24px;font-weight:700;color:{SUB}", e(who)) + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{c};background:{'#DCE7FB' if i == 0 else '#DDF2E5'};border-radius:6px;padding:0 10px;align-self:flex-start", e(line))
             + p(f"font-family:{MONO};font-size:30px;color:{INK};padding:0 10px", "아이디") + '</div>')
outs = [("merge", f"git merge feature/login-title", C_MG), ("rebase", "git rebase main", C_RB), ("squash", "git merge --squash feature/login-title", C_SQ)]
for i, (name, cmd, c) in enumerate(outs):
    top = 240 + i * 180
    o += terminal([("$", cmd), ("r", "CONFLICT (content): Merge conflict in login.md")], left=740, top=top, w=1084, size=(26, 24), tid=f"cf{i}", attrs=f' data-build-in="rise order {i + 1}"')
o.append(p(f"position:absolute;left:96px;top:820px;width:1728px;font-size:34px;font-weight:700;line-height:1.4;color:{INK}", "합치는 방법은 기록 모양만 바꿔요. 같은 줄을 다르게 고쳤으면 Git은 늘 물어봐요.", ' data-build-in="rise order 4"'))
W("cf-all", o, "B에서 갈라진 뒤 main은 첫 줄을 # 로그인 페이지로, 브랜치는 # 로그인하기로 고쳤어요. 03의 충돌 시나리오와 같은 상황이에요. merge, rebase, squash 모두 같은 줄에서 CONFLICT가 나요. 푸는 법도 같아요. 표시 줄을 지우고 남길 내용으로 고친 뒤 git add 해요. 다른 점은 그다음 명령 하나예요(다음 장). 출력의 Auto-merging 줄과 아래 안내 줄은 뺐어요.")

o = [sec("cf-rb")] + head(EB6, "rebase 중 충돌은 add 뒤 --continue로 이어 가요", RED)
o += terminal([("$", "cat login.md"), ("r", "<<<<<<< HEAD"), ("o", "# 로그인 페이지"), ("r", "======="), ("o", "# 로그인하기"), ("r", ">>>>>>> bf59624 (feat: 로그인 제목 바꾸기)"), ("o", "아이디")],
              left=96, top=230, w=860, size=(28, 26))
steps = [("1", "표시 세 줄을 지우고 남길 내용으로 고쳐요", None), ("2", "git add login.md", "mono"), ("3", "git rebase --continue", "mono")]
for i, (n, t, kind) in enumerate(steps):
    top = 230 + i * 130
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:1000px;top:{top}px;width:824px;height:110px;background:#FFFFFF;border:2px solid {LINE};border-radius:18px;padding:0 28px;display:flex;flex-direction:row;align-items:center;gap:24px">'
             + num(n, C_RB, 44) + p(f"font-size:{30 if kind else 28}px;font-weight:700;color:{INK}" + (f";font-family:{MONO}" if kind else ""), e(t)) + '</div>')
o.append(f'<div data-build-in="rise order 4" style="position:absolute;left:1000px;top:640px;width:824px;height:110px;background:#FBEDEC;border:2px solid #E8C4C1;border-radius:18px;padding:0 28px;display:flex;flex-direction:row;align-items:center;gap:24px">'
         + p(f"font-size:28px;font-weight:700;color:{RED}", "그만두기") + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{INK}", "git rebase --abort") + '</div>')
o.append(p(f"position:absolute;left:96px;top:820px;width:1728px;font-size:34px;font-weight:700;line-height:1.4;color:{INK}", "rebase 때 HEAD 쪽은 main이에요. merge 때와 반대로 보여요.", ' data-build-in="rise order 5"'))
W("cf-rb", o, "merge 충돌은 고치고 add 뒤 commit으로 끝냈어요(03). rebase는 커밋을 하나씩 옮기다 멈춘 상태라서 commit 대신 git rebase --continue로 다음 커밋을 이어서 옮겨요. 편집기가 열리면 그대로 저장하고 닫아요. 헷갈리면 git rebase --abort로 rebase 전 모습으로 돌아가요. rebase는 main 위에 내 커밋을 얹는 거라 HEAD가 main 쪽이에요. squash 충돌은 merge처럼 고치고 add, commit 해요.")

n_sh = {"A": n_split["A"], "B": n_split["B"], "C": n_split["C"], "Dx": (2, "up", "purple", "far", "D", D), "Ex": (3, "up", "purple", "far", "E", E_),
        "D": (3, "main", "green", "n", "D'", D2), "E": (4, "main", "green", "n", "E'", E2)}
o = scene("warn", EB6, "push한 브랜치는 rebase하지 않아요", [("$", "git rebase main"), ("$", f"git push origin {FB}"), ("r", f" ! [rejected]        {FB} -> {FB} (non-fast-forward)")],
          "GitHub에는 옛 D, E가 있어요. 여기서 pull하면 같은 변경이 두 번 들어가요.", color=RED, transition="fade")
o += graph(n_sh, [("A", "B"), ("B", "C"), ("C", "D"), ("D", "E"), ("B", "Dx"), ("Dx", "Ex")], [(OFB, "Ex", "origin"), (FB, "E", "green")], FB)
W("warn", o, "feature/login-button을 이미 push한 뒤에 rebase했어요. 내 컴퓨터에는 D', E', GitHub에는 D, E가 있어서 push가 거절돼요. 힌트는 pull하라고 하지만, pull하면 D, E와 D', E'가 둘 다 기록에 들어가요. 강제로 덮어쓰는 방법도 있지만 팀원이 받아 간 커밋과 어긋나서 이 과정에서는 쓰지 않아요. 이 상태가 되면 더 치지 말고 강사에게 물어봐요. 규칙은 하나예요. rebase는 push 전, 나만 가진 커밋에만 써요. main처럼 같이 쓰는 브랜치에서는 rebase하지 않아요.")

o = [sec("choose")] + head(EB6, "언제 무엇을 쓰나요", INK)
ch = [("git pull 할 때", "설정대로 merge", "pull.rebase false", C_MG), ("PR을 합칠 때", "팀이 정한 Merge 버튼 하나", "GitHub", PUR),
      ("push 전, 내 브랜치를 최신 main 뒤로", "rebase를 써도 돼요", "git rebase main", C_RB), ("push한 브랜치, main", "rebase하지 않아요", "merge만", RED)]
for i, (q, a_, cmd, c) in enumerate(ch):
    top = 230 + i * 170
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:96px;top:{top}px;width:1728px;height:150px;background:#FFFFFF;border:2px solid {LINE};border-left:10px solid {c};border-radius:20px;padding:0 40px;display:flex;flex-direction:row;align-items:center;gap:32px">'
             + p(f"width:620px;flex:none;font-size:32px;font-weight:700;color:{INK}", e(q))
             + f'<x-shape kind="arrow-right" style="width:60px;height:36px;background:{c}"></x-shape>'
             + p(f"flex:1;font-size:32px;font-weight:700;color:{c}", e(a_))
             + p(f"width:380px;flex:none;font-family:{MONO};font-size:26px;font-weight:700;color:{INK};background:#EEEFF2;border-radius:10px;padding:10px 18px;text-align:center", e(cmd)) + '</div>')
W("choose", o, "수업에서 직접 치는 건 첫째 줄과 둘째 줄이에요. 셋째 줄은 개인 브랜치에서 연습할 때만 써요. 넷째 줄은 꼭 지켜요. 헷갈리면 merge를 써요. merge는 기록을 바꾸지 않아서 잘못해도 되돌리기 쉬워요.")

# ---------- part 7: trouble ----------
EB7 = "막힐 때"
o = [sec("trouble")] + head(EB7, "이런 메시지가 나와요", NAVY)
cases = [("fatal: Need to specify how to reconcile divergent branches.", "pull 설정이 없어요", "git config --global pull.rebase false"),
         ("fatal: Not possible to fast-forward, aborting.", "pull.ff only가 설정돼 있어요", "git config --global --unset pull.ff"),
         ("error: the branch '...' is not fully merged.", "squash나 rebase로 합쳤어요. 합친 걸 확인하고", "git branch -D 브랜치"),
         ("error: could not apply ... (rebase 중 CONFLICT)", "고치고 add 뒤 이어 가요. 그만두려면 --abort", "git rebase --continue"),
         ("! [rejected] ... (non-fast-forward)  rebase 뒤", "push한 브랜치를 rebase했어요. pull하지 말고", "강사에게 물어봐요")]
o.append('<div style="position:absolute;left:96px;top:220px;width:1728px;height:800px;display:flex;flex-direction:column;gap:16px">')
for i, (q, a_, cmd) in enumerate(cases, 1):
    mono = cmd.startswith("git")
    o.append(f'<div data-build-in="rise order {i}" style="flex:1;display:flex;flex-direction:row;gap:28px;align-items:center;background:#FFFFFF;border:2px solid {LINE};border-radius:20px;padding:12px 32px">'
             + num(i, NAVY, 44)
             + '<div style="flex:1;display:flex;flex-direction:column;gap:6px">' + p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{INK}", e(q)) + p(f"font-size:24px;color:{SUB}", e(a_)) + '</div>'
             + p(f"width:620px;flex:none;{'font-family:' + MONO + ';' if mono else ''}font-size:24px;font-weight:700;line-height:1.5;color:{INK};background:#EEEFF2;padding:12px 20px;border-radius:12px", e(cmd)) + '</div>')
o.append('</div>')
W("trouble", o, "1번은 06에서 본 메시지예요. 2번은 다른 자료를 보고 pull.ff only를 설정한 컴퓨터에서 나요. 설정을 지우고 06처럼 pull.rebase false만 남겨요. 3번은 squash나 Rebase and merge 뒤에 나요. 4번은 rebase 중 충돌이에요. 5번은 push한 브랜치를 rebase한 경우예요. pull로 풀면 같은 커밋이 두 번 들어가니 멈추고 물어봐요.", ("trouble", "막힐 때와 요약"))

o = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>']
sumc = [("fast-forward", C_FF, ["git merge 브랜치"], ["갈라지지 않았을 때", "이름표만 앞으로"], cards[0]),
        ("merge", C_MG, ["git merge 브랜치", "git merge --no-ff 브랜치"], ["합치기 커밋 M", "해시 그대로"], cards[1]),
        ("rebase", C_RB, ["git rebase main"], ["옮겨 붙이기, 해시가 바뀜", "push 전 내 브랜치에만"], cards[2]),
        ("squash", C_SQ, ["git merge --squash 브랜치", "git commit -m \"...\""], ["커밋 하나로", "브랜치는 -D로 지우기"], cards[3])]
for i, (h, c, cmds, desc, cd) in enumerate(sumc):
    left = 96 + i * 438
    o.append(f'<div style="position:absolute;left:{left}px;top:200px;width:414px;height:600px;background:#FFFFFF;border:2px solid {LINE};border-top:10px solid {c};border-radius:20px;padding:28px 26px;display:flex;flex-direction:column;gap:14px">'
             + f'<h3 style="font-size:36px;font-weight:700;color:{c}">{h}</h3>'
             + p(f"font-family:{MONO};font-size:22px;font-weight:700;line-height:1.6;color:{INK};background:#F1F0EC;border-radius:10px;padding:10px 14px", "<br>".join(e(x) for x in cmds))
             + "".join(p(f"font-size:27px;line-height:1.4;color:{SUB}", e(x)) for x in desc) + '</div>')
    g = dict(x0=left + 50, step=78, up=660, main=740, r=17, lf=15, hf=0, tf=16, th=26)
    o += graph(cd[3], cd[4], (), None, g, f"s{i}")
o.append(p(f"position:absolute;left:96px;top:850px;width:1728px;font-size:30px;font-weight:700;color:{INK}", "pull은 pull.rebase false로 merge, PR은 팀이 정한 버튼, 충돌은 어느 방법이든 같은 줄에서 나요."))
W("cheatsheet", o, "네 방법 모두 다 합친 뒤 파일 내용은 같아요. 다른 건 기록 모양과 해시예요. 수업에서는 merge를 기본으로 쓰고, 나머지는 기록을 읽을 수 있을 만큼 알아 두면 돼요.")

# ---------- toc (page numbers from ORDER) ----------
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
parts = [("Activity", C_FF, "갈라지지 않았을 때", "fast-forward, --no-ff", "ff", "noff"),
         ("Link", C_MG, "갈라졌을 때", "merge, rebase, squash", "split", "sq3"),
         ("Search", SUB, "한눈에 비교", "네 가지 결과 그림과 표", "cmp", "cmp-table"),
         ("Cloud", C_PL, "git pull은 무엇을 하나", "pull 설정 세 가지", "pl0", "pl-why"),
         ("Globe", PUR, "GitHub PR의 Merge 버튼", "버튼 세 개와 명령", "gh-btn", "gh-after"),
         ("Warning", RED, "충돌과 주의", "충돌, push한 브랜치", "cf-all", "choose")]
t = [f'<section id="toc" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};padding:96px 128px;display:flex;flex-direction:column;gap:40px">',
     f'<h2 style="font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>',
     '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:24px;flex:1">']
for i, (ic, c, h, s, a, b) in enumerate(parts, 1):
    pg = f"{page[a]}–{page[b]}쪽" if a != b else f"{page[a]}쪽"
    t.append(f'<div style="display:flex;flex-direction:column;gap:10px;background:#FFFFFF;border:2px solid {LINE};border-top:10px solid {c};border-radius:20px;padding:24px 28px">'
             f'<div style="display:flex;flex-direction:row;gap:14px;align-items:center"><p style="font-size:48px;font-weight:900;line-height:1.25;color:{c}">{i}</p>'
             f'<x-icon name="{ic}" style="width:40px;height:40px;color:{c}"></x-icon></div>'
             f'<h3 style="font-size:32px;font-weight:700;color:{INK}">{h}</h3>'
             f'<p style="font-size:26px;line-height:1.4;color:{SUB}">{e(s)}</p><div style="flex:1"></div>'
             f'<p style="font-size:24px;color:#6A7180">{pg}</p></div>')
t += ['</div>', f'<p style="font-size:26px;color:{SUB}">{page["story1"]}–{page["story2"]}쪽은 예시 소개, {page["trouble"]}–{page["cheatsheet"]}쪽은 막힐 때와 한 장 요약이에요.</p>']
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(t) + f"\n<aside>{e('1부와 2부는 같은 예시로 방법 하나씩 봐요. 3부에서 결과를 나란히 비교해요. 4부와 5부는 그 방법이 git pull과 GitHub 버튼에서 어떻게 쓰이는지 연결해요. 6부는 충돌과 rebase를 쓸 때 지킬 규칙이에요.')}</aside>\n</section>\n")

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-10-29T05:00:00Z"}, "lists": "css", "title": "합치는 방법, 눈으로 비교하기", "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
print(len(ORDER), "slides")
