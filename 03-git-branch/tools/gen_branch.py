"""Generates the commit-graph scenes for the Git branch deck.

One idea per scene: a sentence title, the command in a terminal strip, a large commit graph
(nodes, edges, branch name tags, HEAD) and one caption. Elements keep the same id across
scenes so the magic transition animates only what the command changed.
Terminal output was captured from git 2.43 (see README).
Usage: python3 tools/gen_branch.py slides
"""
import html, os, sys

OUT = sys.argv[1]
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"

PANEL = dict(left=96, top=436, w=1728, h=428)
LANE = {"up": 570, "main": 704}           # node centre y
X0, STEP = 300, 200                       # node centre x of the first visible column
R = 26                                    # node radius

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
    return round(len(text) * 15.5 + 32)


def scene(sec_id, eyebrow, title, term=None, caption="", transition="magic", eyebrow_color="#2459C9"):
    """term: list of (kind, text); kind "$" is a command, others are output colours."""
    o = [f'<section id="{sec_id}" data-transition="{transition}" style="background:#F6F5F1;color:#1D2330;font-family:{SANS};padding:96px;display:flex;flex-direction:column">']
    o.append(p(f"position:absolute;left:96px;top:48px;width:1728px;font-size:26px;font-weight:700;color:{eyebrow_color}", e(eyebrow), ' id="eyebrow"'))
    o.append(f'<h2 id="title" style="position:absolute;left:96px;top:92px;width:1728px;font-size:56px;font-weight:700;line-height:1.2;color:#1D2330">{title}</h2>')
    if term:
        o.append(f'<div id="term" style="position:absolute;left:96px;top:196px;width:1728px;background:#1B2029;border-radius:20px;padding:22px 32px;display:flex;flex-direction:column;gap:4px;font-family:{MONO}">')
        for kind, text in term:
            t = e(text).replace("\t", "&#160;" * 4)
            lead = len(t) - len(t.lstrip(" "))
            t = "&#160;" * lead + t.lstrip(" ")
            if kind == "$":
                o.append(p(f"font-size:32px;font-weight:700;line-height:1.35;white-space:nowrap;color:{TERM_COLORS['$']}", "$ " + t))
            else:
                o.append(p(f"font-size:26px;line-height:1.35;white-space:nowrap;color:{TERM_COLORS[kind]}", t))
        o.append('</div>')
    o.append(f'<div id="panel" style="position:absolute;left:{PANEL["left"]}px;top:{PANEL["top"]}px;width:{PANEL["w"]}px;height:{PANEL["h"]}px;background:#FDFCF9;border:2px solid #E1DED6;border-radius:24px"></div>')
    if caption:
        o.append(p("position:absolute;left:96px;top:900px;width:1728px;font-size:34px;font-weight:700;line-height:1.4;color:#1D2330", caption, ' id="caption" data-build-in="rise"'))
    return o


def graph(nodes, edges, tags, head=None, off=0, ghost_edges=()):
    """nodes: {hash: (col, lane, colour, kind)}  kind: n | merge | ghost (not made yet) | far (only on GitHub)
    edges: [(from_hash, to_hash)]   tags: [(name, hash, kind)] stacked in list order per node
    head: name of the tag HEAD points at"""
    o = []
    if off:
        y = LANE["main"]
        o.append(f'<div id="e-past" style="position:absolute;left:{PANEL["left"] + 32}px;top:{y - 3}px;width:{X0 - R - PANEL["left"] - 40}px;height:6px;border-top:6px dotted #C3C8D2"></div>')
    for a, b in edges:
        ca, la, colour_a, _ = nodes[a]
        cb, lb, colour_b, kb = nodes[b]
        x1, y1, x2, y2 = cx(ca, off), LANE[la], cx(cb, off), LANE[lb]
        light = COL[colour_a if (lb == "main" and la != "main") else colour_b][1]
        dashed = (a, b) in ghost_edges or kb in ("ghost", "far")
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
              "far": f"background:#FDFCF9;border:5px dashed {fill}"}.get(kind, f"background:{fill};border:4px solid {fill}")
        o.append(f'<div id="n-{h}" style="position:absolute;left:{x - R}px;top:{y - R}px;width:{2 * R}px;height:{2 * R}px;border-radius:50%;{st}"></div>')
        label = "?" if kind == "ghost" else h
        hc = "#6A7180" if kind in ("ghost", "far") else "#1D2330"
        o.append(p(f"position:absolute;left:{x - 70}px;top:{y + R + 2}px;width:140px;font-family:{MONO};font-size:24px;font-weight:700;text-align:center;color:{hc}", e(label), f' id="h-{h}"'))
    stack = {}
    for name, h, kind in tags:
        col, lane, _, _ = nodes[h]
        i = stack.get(h, 0)
        stack[h] = i + 1
        x = cx(col, off)
        w = tag_w(name)
        top = (LANE[lane] + R + 38 + i * 46) if lane == "main" else (LANE[lane] - R - 56 - i * 46)
        tid = "t-" + name.replace("/", "-")
        o.append(p(f"position:absolute;left:{x - w // 2}px;top:{top}px;width:{w}px;font-family:{MONO};font-size:26px;font-weight:700;line-height:1.5;text-align:center;border-radius:8px;{TAG_KIND[kind]}", e(name), f' id="{tid}"'))
        if name == head:
            o.append(p(f"position:absolute;left:{x - w // 2 + w + 10}px;top:{top}px;width:112px;font-family:{MONO};font-size:26px;font-weight:700;line-height:1.5;text-align:center;border-radius:8px;background:#1D2330;color:#F6F5F1", "◀ HEAD", ' id="t-head"'))
    return o


def card(title, lines, top=470):
    """A small file card at the right of the graph panel. lines: [(text, colour_key)]  g = changed line."""
    c = {"o": "#1D2330", "g": "#1A7340", "b": "#1E3F8F", "x": "#9AA0AB"}
    bg = {"g": "#DDF2E5", "b": "#DCE7FB"}
    o = [f'<div id="card" style="position:absolute;left:1430px;top:{top}px;width:370px;background:#FFFFFF;border:2px solid #E1DED6;border-radius:18px;padding:20px 24px;display:flex;flex-direction:column;gap:8px">']
    o.append(p("font-size:24px;font-weight:700;color:#4A5262", e(title)))
    for text, k in lines:
        extra = f";background:{bg[k]};border-radius:4px;padding:0 6px" if k in bg else ""
        deco = ";text-decoration:line-through" if k == "x" else ""
        o.append(p(f"font-family:{MONO};font-size:26px;line-height:1.4;white-space:nowrap;color:{c[k]}{extra}{deco}", e(text)))
    o.append('</div>')
    return o


def write(sec_id, parts, notes):
    with open(os.path.join(OUT, f"{sec_id}.html"), "w") as f:
        f.write("\n".join(parts) + f"\n<aside>{e(notes)}</aside>\n</section>\n")


# ---------- the story (hashes from a real run, see README) ----------
A, B, C, D, E_, F, G, M = "560eba8", "1180617", "feff88d", "7ca17f8", "171d9dc", "d92e18b", "6bb4ada", "5438662"
K, L, RZ, P, Q = "d3acab4", "8007611", "397c77a", "2969484", "878b202"
FB, DU, FK, FE = "feat/greeting", "docs/usage", "feat/korean", "feat/emoji"

base = {A: (0, "main", "main", "n"), B: (1, "main", "main", "n"), C: (2, "main", "main", "n")}
base_e = [(A, B), (B, C)]

# ---------- 1. 그래프 읽기 ----------
EB1 = "브랜치란? · 그래프 읽기"
o = scene("g1-dots", EB1, "점 하나가 커밋 하나예요", [("$", "git log --oneline"), ("o", f"{C} (HEAD -> main) docs: README 추가"),
          ("o", f"{B} feat: 인사말 추가"), ("o", f"{A} feat: 인사 파일 추가")],
          "왼쪽이 먼저 한 커밋, 오른쪽이 최근 커밋이에요.")
o += graph(base, base_e, [])
write("g1-dots", o, "02에서 만든 hello-git 저장소를 이어서 써요. git log는 최근 커밋이 위에 나오고, 그래프는 오래된 커밋이 왼쪽이에요. 점 아래 글자는 커밋 해시(이름표 번호) 앞 7자리예요.")

o = scene("g2-main", EB1, "main은 마지막 커밋에 붙은 이름표예요", None, "새 커밋을 하면 이름표가 새 커밋으로 옮겨 가요.")
o += graph(base, base_e, [("main", C, "main")])
write("g2-main", o, "브랜치는 커밋을 담는 상자가 아니라 커밋 하나를 가리키는 이름표예요. 그래서 브랜치를 만들어도 무겁지 않아요. git log 출력의 (HEAD -> main)에서 main이 이 이름표예요.")

o = scene("g3-head", EB1, "HEAD는 지금 내가 있는 곳이에요", None, "커밋하면 HEAD가 붙은 이름표가 앞으로 가요.")
o += graph(base, base_e, [("main", C, "main")], head="main")
write("g3-head", o, "HEAD는 지금 내가 서 있는 브랜치를 가리켜요. git log의 HEAD -> main은 지금 main에 있다는 뜻이에요. 이 덱의 모든 장면은 이름표와 HEAD가 어디로 가는지만 보면 돼요.")

# ---------- 2. 만들고 옮기기 ----------
EB2 = "만들고 옮기기"
o = scene("b1-list", EB2, "브랜치 목록 보기", [("$", "git branch"), ("g", "* main")], "* 표시가 지금 있는 브랜치예요. 그래프의 HEAD와 같은 뜻이에요.")
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
o = scene("b4-commit", EB2, f"커밋하면 {FB}만 앞으로 가요", [("$", "git add hello.md"), ("$", 'git commit -m "feat: 반가움 인사 추가"'),
          ("o", f"[{FB} {D}] feat: 반가움 인사 추가")], "main은 제자리예요.")
o += graph(n4, e4, [("main", C, "main"), (FB, D, "green")], head=FB)
write("b4-commit", o, "hello.md에 nice to meet you 한 줄을 넣고 커밋했어요. 출력 대괄호 안에 지금 브랜치 이름이 나와요. 새 커밋을 위로 그린 건 보기 쉽게 하려는 것이에요. 출력의 1 file changed 줄은 뺐어요.")

n5 = dict(n4); n5[E_] = (4, "up", "green", "n")
e5 = e4 + [(D, E_)]
o = scene("b5-commit2", EB2, "한 번 더 커밋하면 한 칸 더", [("$", "git add bye.md"), ("$", 'git commit -m "feat: 끝인사 파일 추가"'),
          ("o", f"[{FB} {E_}] feat: 끝인사 파일 추가")], "기능이 끝날 때까지 브랜치에서 여러 번 커밋해도 돼요.")
o += graph(n5, e5, [("main", C, "main"), (FB, E_, "green")], head=FB)
write("b5-commit2", o, "새 파일 bye.md(see you)를 만들고 커밋했어요. main은 계속 처음 모습이라 언제든 돌아갈 수 있어요.")

o = scene("b6-back", EB2, "main으로 돌아가기", [("$", "git checkout main"), ("o", "Switched to branch 'main'")], "HEAD만 main으로 돌아왔어요.")
o += graph(n5, e5, [("main", C, "main"), (FB, E_, "green")], head="main")
write("b6-back", o, "HEAD가 main으로 옮겨 갔어요. 다음 장에서 작업 폴더 파일도 같이 바뀌는 걸 봐요.")

# ---------- 3. 합치기 ----------
EB3 = "합치기"
o = scene("b7-ff", EB3, "Fast-forward: main 이름표만 앞으로", [("$", f"git merge {FB}"), ("o", f"Updating {C}..{E_}"), ("g", "Fast-forward")],
          "main 쪽에 새 커밋이 없으면 이름표만 당겨요.")
o += graph(n5, e5, [(FB, E_, "green"), ("main", E_, "main")], head="main")
write("b7-ff", o, "main이 갈라진 뒤 main에는 커밋이 없었어요. 그래서 Git은 main 이름표를 feat/greeting 자리로 옮기기만 해요. 빨리 감기(Fast-forward)라고 해요. 출력의 파일 목록 줄은 뺐어요.")

n8 = dict(base); n8[D] = (3, "main", "main", "n"); n8[E_] = (4, "main", "main", "n")
e8 = base_e + [(C, D), (D, E_)]
o = scene("b8-delete", EB3, "다 쓴 브랜치 지우기", [("$", f"git branch -d {FB}"), ("o", f"Deleted branch {FB} (was {E_}).")],
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
write("d1-create", o, "git checkout -b docs/usage는 git branch docs/usage와 git checkout docs/usage를 한 번에 친 것과 같아요. 문서 작업이라 이름을 docs/로 시작했어요.")

o = scene("d2-commit", EB4, f"{DU}에서 커밋", [("$", "git add README.md"), ("$", 'git commit -m "docs: README에 소개 추가"'),
          ("o", f"[{DU} {F}] docs: README에 소개 추가")], f"{DU}만 한 칸 앞으로 가요.")
o += graph(n9, e9, [("main", E_, "main"), (DU, F, "orange")], head=DU)
write("d2-commit", o, "README.md에 인사 파일 모음이라는 소개를 넣고 커밋했어요.")

o = scene("d3-back", EB4, "다시 main으로", [("$", "git checkout main"), ("o", "Switched to branch 'main'")], "이번엔 main에서도 커밋해 볼게요.")
o += graph(n9, e9, [("main", E_, "main"), (DU, F, "orange")], head="main")
write("d3-back", o, "팀에서는 내가 브랜치에서 일하는 동안 다른 사람 작업이 main에 들어오는 일이 흔해요. 그 상황을 혼자 만들어 봐요.")

n10 = dict(n9); n10[G] = (5, "main", "main", "n")
e10 = e9 + [(E_, G)]
o = scene("d4-main", EB4, "main에도 새 커밋: 길이 두 갈래가 됐어요", [("$", "git add bye.md"), ("$", 'git commit -m "feat: 끝인사 한 줄 추가"'),
          ("o", f"[main {G}] feat: 끝인사 한 줄 추가")], "이번엔 이름표만 당겨서는 합칠 수 없어요.")
o += graph(n10, e10, [("main", G, "main"), (DU, F, "orange")], head="main")
write("d4-main", o, "bye.md에 bye 한 줄을 더했어요. main과 docs/usage 양쪽에 서로 모르는 커밋이 하나씩 있어요.")

n11 = dict(n10); n11[M] = (6, "main", "main", "merge")
e11 = e10 + [(G, M), (F, M)]
o = scene("d5-merge", EB4, "merge 커밋이 두 길을 이어요", [("$", f"git merge {DU}"), ("o", "Merge made by the 'ort' strategy.")],
          "흰 점이 새로 생긴 merge 커밋이에요. 메시지 편집기가 열리면 그대로 저장하고 닫아요.")
o += graph(n11, e11, [("main", M, "main"), (DU, F, "orange")], head="main")
write("d5-merge", o, "양쪽에 새 커밋이 있으니 Git이 둘을 합친 커밋을 새로 만들어요. 부모가 둘인 커밋이에요. 편집기에 Merge branch 'docs/usage'가 미리 적혀 있어요. vim이 열리면 Esc를 누른 뒤 :wq 와 Enter를 쳐요. 출력의 파일 목록 줄은 뺐어요.")

o = scene("d6-delete", EB4, f"{DU}도 지우기", [("$", f"git branch -d {DU}"), ("o", f"Deleted branch {DU} (was {F}).")],
          "이름표만 사라지고 커밋은 main 기록 안에 남아요.")
o += graph(n11, e11, [("main", M, "main")], head="main")
write("d6-delete", o, f"합친 브랜치는 지워서 목록을 깔끔하게 둬요. 커밋 {F}는 merge 커밋을 통해 main 기록에 그대로 있어요.")

# ---------- 5. 충돌 ----------
EB5 = "충돌 시나리오 1 · 같은 줄"
RED = "#A33131"
n12 = {E_: (4, "main", "main", "n"), F: (5, "up", "gray", "n"), G: (5, "main", "main", "n"),
       M: (6, "main", "main", "merge")}
e12 = [(E_, F), (E_, G), (G, M), (F, M)]
n13 = dict(n12); n13[K] = (7, "up", "green", "n")
e13 = e12 + [(M, K)]
o = scene("c1-korean", EB5, f"{FK}에서 첫 줄을 안녕으로", [("$", f"git checkout -b {FK}"), ("$", 'git commit -am "feat: 인사를 한국어로"'),
          ("o", f"[{FK} {K}] feat: 인사를 한국어로")], "hello.md 첫 줄 hello를 안녕으로 바꿨어요.", eyebrow_color=RED)
o += graph(n13, e13, [("main", M, "main"), (FK, K, "green")], head=FK, off=4)
o += card(f"{FK}의 hello.md", [("안녕", "g"), ("world", "o"), ("nice to meet you", "o")])
write("c1-korean", o, "commit -am은 이미 아는 파일의 add와 commit을 한 번에 해요. 새 파일엔 안 돼요. 그래프 왼쪽 점선은 앞의 커밋들이 이어진다는 뜻이에요. checkout 출력은 뺐어요.")

n14 = dict(n13); n14[L] = (7, "main", "main", "n")
e14 = e13 + [(M, L)]
o = scene("c2-main", EB5, "main에서는 같은 줄을 hi로", [("$", "git checkout main"), ("$", 'git commit -am "feat: 인사를 짧게"'),
          ("o", f"[main {L}] feat: 인사를 짧게")], "같은 줄을 양쪽에서 다르게 고쳤어요.", eyebrow_color=RED)
o += graph(n14, e14, [("main", L, "main"), (FK, K, "green")], head="main", off=4)
o += card("main의 hello.md", [("hi", "b"), ("world", "o"), ("nice to meet you", "o")])
write("c2-main", o, "main에서는 첫 줄 hello를 hi로 바꿨어요. 두 사람이 같은 파일의 같은 줄을 고친 상황이에요.")

n15 = dict(n14); n15[RZ] = (8, "main", "main", "ghost")
e15 = e14 + [(L, RZ), (K, RZ)]
o = scene("c3-conflict", EB5, "합치려니 멈췄어요: 충돌", [("$", f"git merge {FK}"), ("r", "CONFLICT (content): Merge conflict in hello.md"),
          ("o", "Automatic merge failed; fix conflicts and then commit the result.")],
          "Git이 hi와 안녕 중 무엇을 남길지 몰라서 나에게 물어보는 거예요.", eyebrow_color=RED)
o += graph(n15, e15, [("main", L, "main"), (FK, K, "green")], head="main", off=4, ghost_edges=[(L, RZ), (K, RZ)])
write("c3-conflict", o, "충돌은 고장이 아니에요. Git이 고를 수 없는 부분만 표시해 두고 멈춘 상태예요. 다른 줄은 알아서 합쳐졌어요. 첫 줄 Auto-merging hello.md는 뺐어요. 그만두고 싶으면 git merge --abort로 합치기 전으로 돌아가요.")

n16 = dict(n14); n16[RZ] = (8, "main", "main", "merge")
o = scene("c4-resolve", EB5, "고치고 add, commit하면 끝", [("$", "git add hello.md"), ("$", 'git commit -m "fix: 인사 충돌 해결"'),
          ("o", f"[main {RZ}] fix: 인사 충돌 해결")], "이 커밋이 두 길을 잇는 merge 커밋이에요.", eyebrow_color=RED)
o += graph(n16, e15, [("main", RZ, "main"), (FK, K, "green")], head="main", off=4)
o += card("고친 hello.md", [("안녕", "g"), ("world", "o"), ("nice to meet you", "o")])
write("c4-resolve", o, "충돌 표시 세 줄을 지우고 안녕만 남긴 뒤 저장했어요. add는 이 파일 충돌을 풀었다는 표시예요. 다 쓴 feat/korean은 git branch -d feat/korean으로 지워요.")

# ---------- 6. GitHub에서 함께 ----------
EB6 = "GitHub에서 함께"
PUR = "#6B47D6"
n17 = {F: (5, "up", "gray", "n"), G: (5, "main", "main", "n"), M: (6, "main", "main", "merge"), K: (7, "up", "gray", "n"),
       L: (7, "main", "main", "n"), RZ: (8, "main", "main", "merge"), P: (9, "up", "orange", "n")}
e17 = [(G, M), (F, M), (M, K), (M, L), (L, RZ), (K, RZ), (RZ, P)]
o = scene("p1-push", EB6, "브랜치째 GitHub에 올려요", [("$", f"git checkout -b {FE}"), ("$", 'git commit -am "feat: 끝인사 하나 더"'),
          ("$", f"git push origin {FE}"), ("g", f" * [new branch]      {FE} -> {FE}")],
          "push할 때 main 대신 브랜치 이름을 끝까지 적어요.", eyebrow_color=PUR)
o += graph(n17, e17, [("main", RZ, "main"), ("origin/main", RZ, "origin"), (FE, P, "orange"), ("origin/feat/emoji", P, "origin")], head=FE, off=5)
write("p1-push", o, f"bye.md에 bye bye를 더하고 커밋한 뒤 올렸어요. 보라색 origin/ 이름표는 GitHub에 있는 브랜치 위치예요. 우리 과정 규칙대로 -u는 쓰지 않아요. 출력의 commit 결과 줄과 앞부분(Enumerating objects..., remote: Create a pull request...)은 뺐어요.")

n18 = dict(n17); n18[Q] = (10, "main", "main", "far")
e18 = e17 + [(RZ, Q), (P, Q)]
o = scene("p2-merged", EB6, "GitHub에서 Merge하면 GitHub에만 커밋이 생겨요", None,
          "점선 커밋은 아직 GitHub에만 있어요. 내 컴퓨터는 몰라요.", eyebrow_color=PUR)
o += graph(n18, e18, [("main", RZ, "main"), ("origin/main", RZ, "origin"), (FE, P, "orange"), ("origin/feat/emoji", P, "origin")], head=FE, off=5)
write("p2-merged", o, f"Merge pull request를 누르면 GitHub 안에서 merge 커밋({Q})이 생겨요. 메시지는 Merge pull request #1 from kim/{FE}예요. 내 컴퓨터로 가져오려면 pull해야 해요.")

n19 = dict(n18); n19[Q] = (10, "main", "main", "merge")
o = scene("p3-pull", EB6, "main으로 가서 pull로 받아요", [("$", "git checkout main"), ("$", "git pull origin main"), ("o", f"Updating {RZ}..{Q}"), ("g", "Fast-forward")],
          f"다 쓴 {FE}는 git branch -d {FE}로 지워요.", eyebrow_color=PUR)
o += graph(n19, e18, [("main", Q, "main"), ("origin/main", Q, "origin"), (FE, P, "orange"), ("origin/feat/emoji", P, "origin")], head="main", off=5)
write("p3-pull", o, f"내 main에는 새 커밋이 없었으니 pull이 Fast-forward로 받아요. 출력의 From, FETCH_HEAD 줄과 파일 목록 줄은 뺐어요. origin/{FE} 이름표는 GitHub에서 브랜치를 지운 뒤에도 남아 있어요. git fetch origin --prune 하면 정리돼요.")

print("ok")
