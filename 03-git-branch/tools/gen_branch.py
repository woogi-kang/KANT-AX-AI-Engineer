"""Generates the commit-graph practice scenes for the Git branch deck.

Every scene shares one frame: a commit graph panel (nodes, edges, branch name tags, HEAD),
an optional working-folder card on the right, a terminal and a callout. Elements keep the
same id across scenes so the magic transition animates nodes and tags moving.
Terminal output was captured from git 2.43 (see README).
"""
import html, os, sys

OUT = sys.argv[1]
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"

PANEL = dict(left=96, top=188, w=1728, h=468)
LANE = {"up": 360, "main": 504}          # node centre y
X0, STEP = 230, 170                       # node centre x of the first visible column
R = 22                                    # node radius

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


def e(s):
    return html.escape(s, quote=False)


def p(style, text, attrs=""):
    return f'<p{attrs} style="{style}">{text}</p>'


def cx(col, off):
    return X0 + (col - off) * STEP


def tag_w(text):
    return round(len(text) * 14.5 + 28)


def frame(sec_id, eyebrow, cmd, cmd_size=52, transition="magic", eyebrow_color="#2459C9"):
    o = [f'<section id="{sec_id}" data-transition="{transition}" style="background:#F6F5F1;color:#1D2330;font-family:{SANS};padding:96px;display:flex;flex-direction:column">']
    o.append(p(f"position:absolute;left:96px;top:40px;width:1728px;font-size:24px;font-weight:700;color:{eyebrow_color}", e(eyebrow), ' id="eyebrow"'))
    o.append(f'<h2 id="cmd" style="position:absolute;left:96px;top:90px;width:1728px;font-family:{MONO};font-size:{cmd_size}px;font-weight:700;line-height:1.15;color:#1D2330">{cmd}</h2>')
    o.append(f'<div id="panel" style="position:absolute;left:{PANEL["left"]}px;top:{PANEL["top"]}px;width:{PANEL["w"]}px;height:{PANEL["h"]}px;background:#FDFCF9;border:2px solid #E1DED6;border-radius:24px"></div>')
    o.append('<x-icon id="ic-graph" name="Activity" style="position:absolute;left:124px;top:208px;width:28px;height:28px;color:#6A7180"></x-icon>')
    o.append(p("position:absolute;left:160px;top:204px;width:400px;font-size:24px;font-weight:700;color:#6A7180", "커밋 그래프", ' id="lbl-graph"'))
    return o


def graph(nodes, edges, tags, head=None, off=0, ghost_edges=()):
    """nodes: {hash: (col, lane, colour, kind)}  kind: normal | merge | ghost
    edges: [(from_hash, to_hash)]   tags: [(name, hash, kind)] stacked in list order per node
    head: name of the tag HEAD points at"""
    o = []
    if off:
        y = LANE["main"]
        o.append(f'<div id="e-past" style="position:absolute;left:{PANEL["left"] + 24}px;top:{y - 3}px;width:{X0 - R - PANEL["left"] - 24}px;height:6px;border-top:6px dotted #C3C8D2"></div>')
    for a, b in edges:
        ca, la, colour_a, _ = nodes[a]
        cb, lb, colour_b, kb = nodes[b]
        x1, y1, x2, y2 = cx(ca, off), LANE[la], cx(cb, off), LANE[lb]
        light = COL[colour_b if lb != "main" or la == "main" else colour_a][1]
        if lb == "main" and la != "main":
            light = COL[colour_a][1]
        dashed = (a, b) in ghost_edges or kb == "ghost"
        if y1 == y2:
            st = f"border-top:6px dashed {light}" if dashed else f"background:{light}"
            o.append(f'<div id="e-{a}-{b}" style="position:absolute;left:{x1 + R}px;top:{y1 - 3}px;width:{x2 - x1 - 2 * R}px;height:6px;{st}"></div>')
        else:
            dash = ";border-style:dashed" if dashed else ""
            o.append(f'<x-connector id="e-{a}-{b}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" style="color:{light};border-width:6px{dash}"></x-connector>')
    for h, (col, lane, colour, kind) in nodes.items():
        x, y = cx(col, off), LANE[lane]
        fill = COL[colour][0]
        if kind == "merge":
            st = f"background:#FFFFFF;border:8px solid {fill}"
        elif kind == "ghost":
            st = f"background:#FDFCF9;border:4px dashed {fill}"
        else:
            st = f"background:{fill};border:4px solid {fill}"
        o.append(f'<div id="n-{h}" style="position:absolute;left:{x - R}px;top:{y - R}px;width:{2 * R}px;height:{2 * R}px;border-radius:50%;{st}"></div>')
        label = "?" if kind == "ghost" else h
        hc = "#6A7180" if kind == "ghost" else "#1D2330"
        o.append(p(f"position:absolute;left:{x - 64}px;top:{y + R + 4}px;width:128px;font-family:{MONO};font-size:24px;font-weight:700;text-align:center;color:{hc}", e(label), f' id="h-{h}"'))
    stack = {}
    for name, h, kind in tags:
        col, lane, _, _ = nodes[h]
        i = stack.get(h, 0)
        stack[h] = i + 1
        x = cx(col, off)
        w = tag_w(name)
        top = (LANE[lane] + R + 46 + i * 44) if lane == "main" else (LANE[lane] - R - 50 - i * 44)
        tid = "t-" + name.replace("/", "-")
        o.append(p(f"position:absolute;left:{x - w // 2}px;top:{top}px;width:{w}px;font-family:{MONO};font-size:24px;font-weight:700;line-height:1.5;text-align:center;border-radius:8px;{TAG_KIND[kind]}", e(name), f' id="{tid}"'))
        if name == head:
            o.append(p(f"position:absolute;left:{x - w // 2 + w + 8}px;top:{top}px;width:96px;font-family:{MONO};font-size:24px;font-weight:700;line-height:1.5;text-align:center;border-radius:8px;background:#1D2330;color:#F6F5F1", "◀ HEAD", ' id="t-head"'))
    return o


def files(items, title="작업 폴더"):
    """items: list of (filename, [(text, colour_key)])  colour_key: o g r b h x (x = missing file)"""
    c = {"o": "#1D2330", "g": "#1A7340", "r": "#A33131", "b": "#1E3F8F", "h": "#6A7180"}
    bg = {"g": "#DDF2E5", "r": "#FBE4E2", "b": "#DCE7FB"}
    o = [f'<div id="files" style="position:absolute;left:1452px;top:212px;width:348px;height:420px;background:#FFFFFF;border:2px solid #E1DED6;border-radius:18px;padding:18px 20px;display:flex;flex-direction:column;gap:10px">']
    o.append('<div style="display:flex;flex-direction:row;gap:10px;align-items:center">'
             '<x-icon name="Code" style="width:28px;height:28px;color:#3A4150"></x-icon>'
             + p("font-size:24px;font-weight:700;color:#3A4150", e(title)) + '</div>')
    for name, lines in items:
        if lines is None:
            o.append(f'<div style="display:flex;flex-direction:column;background:#F6F5F1;border-radius:10px;padding:8px 12px">'
                     + p(f"font-family:{MONO};font-size:24px;font-weight:700;color:#6A7180", e(name)) + '</div>')
            continue
        if lines == "x":
            o.append(p(f"font-family:{MONO};font-size:24px;color:#9AA0AB;text-decoration:line-through", e(name)))
            continue
        o.append(f'<div style="display:flex;flex-direction:column;background:#F6F5F1;border-radius:10px;padding:8px 12px">')
        o.append(p(f"font-family:{MONO};font-size:24px;font-weight:700;color:#3A4150", e(name)))
        for text, k in lines:
            extra = f";background:{bg[k]};border-radius:4px" if k in bg else ""
            o.append(p(f"font-family:{MONO};font-size:24px;line-height:1.35;white-space:nowrap;color:{c[k]}{extra}", e(text) if text else "&#160;"))
        o.append('</div>')
    o.append('</div>')
    return o


TERM_COLORS = {"$": "#F2C46D", "o": "#D8DEE9", "h": "#9AA3B5", "g": "#7FD18B", "r": "#F28B82", "#": "#9AA3B5"}


def terminal(lines):
    o = [f'<div id="term" style="position:absolute;left:96px;top:676px;width:1150px;height:348px;background:#1B2029;border-radius:20px;padding:20px 24px;display:flex;flex-direction:column;font-family:{MONO}">']
    for kind, text in lines:
        t = e(text)
        lead = len(t) - len(t.lstrip(" "))
        t = "&#160;" * lead + t.lstrip(" ") if t.strip() else "&#160;"
        t = t.replace("\t", "&#160;" * 8)
        if kind == "$":
            t = "$ " + t
        o.append(p(f"font-size:24px;line-height:1.3;white-space:nowrap;color:{TERM_COLORS[kind]}", t))
    o.append('</div>')
    return o


def callout(icon, title, sub=None, icolor="#2459C9"):
    o = ['<div id="explain" data-build-in="rise" style="position:absolute;left:1278px;top:676px;width:546px;height:348px;background:#FFFFFF;border:2px solid #E1DED6;border-radius:20px;padding:32px;display:flex;flex-direction:column;justify-content:center;gap:16px">']
    o.append(f'<x-icon name="{icon}" style="width:56px;height:56px;color:{icolor}"></x-icon>')
    o.append(p("font-size:34px;font-weight:700;line-height:1.35;color:#1D2330", title))
    if sub:
        o.append(p("font-size:26px;line-height:1.45;color:#4A5262", sub))
    o.append('</div>')
    return o


def pop(left, top, width, text, color="#1E3F8F", bg="#DCE7FB", bd="#5B8DEF"):
    return p(f"position:absolute;left:{left}px;top:{top}px;width:{width}px;font-size:24px;font-weight:700;color:{color};background:{bg};border:2px solid {bd};padding:8px 14px;border-radius:12px", text, ' data-build-in="pop"')


def write(sec_id, parts, notes):
    with open(os.path.join(OUT, f"{sec_id}.html"), "w") as f:
        f.write("\n".join(parts) + f"\n<aside>{e(notes)}</aside>\n</section>\n")


# ---------- the story (hashes from a real run, see README) ----------
A, B, C, D, E_, F, G, M = "560eba8", "1180617", "feff88d", "7ca17f8", "171d9dc", "d92e18b", "6bb4ada", "5438662"
K, L, RZ, P, Q = "d3acab4", "8007611", "397c77a", "2969484", "878b202"
FB = "feat/greeting"

HELLO2 = ("hello.md", [("hello", "o"), ("world", "o")])
HELLO3 = ("hello.md", [("hello", "o"), ("world", "o"), ("nice to meet you", "o")])
README = ("README.md", [("# hello-git", "o")])

base = {A: (0, "main", "main", "n"), B: (1, "main", "main", "n"), C: (2, "main", "main", "n")}
base_e = [(A, B), (B, C)]

# b0: log
o = frame("b0-log", "실습 1 · 지금 모습 보기", "git log --oneline --decorate")
o += graph(base, base_e, [("main", C, "main")], head="main")
o += files([HELLO2, README])
o += terminal([("$", "git log --oneline --decorate"), ("o", f"{C} (HEAD -> main) docs: README 추가"),
               ("o", f"{B} feat: 인사말 추가"), ("o", f"{A} feat: 인사 파일 추가")])
o += callout("Link", "main = 마지막 커밋에<br>붙은 이름표", "HEAD = 지금 내가 있는 브랜치")
write("b0-log", o, "02에서 만든 hello-git 저장소를 이어서 써요. 점 하나가 커밋 하나, 선은 순서예요. 왼쪽이 오래된 커밋이에요. 괄호 안 (HEAD -> main)은 지금 main 브랜치에 있고, main이 이 커밋을 가리킨다는 뜻이에요.")

# b1: git branch
o = frame("b1-branch", "실습 2 · 브랜치 목록", "git branch")
o += graph(base, base_e, [("main", C, "main")], head="main")
o += files([HELLO2, README])
o += terminal([("$", "git branch"), ("g", "* main")])
o += callout("Search", "브랜치 목록 보기", "* 표시가 지금 있는 브랜치")
write("b1-branch", o, "git branch는 목록만 보여 줘요. 아직 main 하나뿐이에요. 별표와 초록 글씨가 지금 서 있는 브랜치예요.")

# b2: checkout -b
o = frame("b2-create", "실습 3 · 브랜치 만들고 옮겨 가기", f"git checkout -b {FB}")
o += graph(base, base_e, [("main", C, "main"), (FB, C, "green")], head=FB)
o += files([HELLO2, README])
o += terminal([("$", f"git checkout -b {FB}"), ("o", f"Switched to a new branch '{FB}'"),
               ("$", "git branch"), ("g", f"* {FB}"), ("o", "  main")])
o += callout("Link", "이름표가 하나<br>더 생겼어요", "커밋도 파일도 그대로예요", icolor="#1F8A4C")
write("b2-create", o, "-b는 만들고 바로 옮겨 가라는 뜻이에요. git branch feat/greeting(만들기) + git checkout feat/greeting(옮기기)을 한 번에 한 거예요. 브랜치를 만들어도 커밋이 복사되지 않아요. 같은 커밋에 이름표만 하나 더 붙어요. 이름 규칙은 이 파트 끝에서 봐요.")

# b3: commit on branch
n3 = dict(base); n3[D] = (3, "up", "green", "n")
e3 = base_e + [(C, D)]
o = frame("b3-commit", "실습 4 · 브랜치에서 커밋", 'git commit -m "feat: 반가움 인사 추가"', cmd_size=48)
o += graph(n3, e3, [("main", C, "main"), (FB, D, "green")], head=FB)
o += files([("hello.md", [("hello", "o"), ("world", "o"), ("nice to meet you", "g")]), ("README.md", None)])
o += terminal([("#", "# hello.md에 한 줄 추가"), ("$", "git add hello.md"), ("$", 'git commit -m "feat: 반가움 인사 추가"'),
               ("o", f"[{FB} {D}] feat: 반가움 인사 추가"), ("o", " 1 file changed, 1 insertion(+)")])
o += callout("CheckCircle", f"{FB}만<br>앞으로 가요", "main은 제자리", icolor="#1F8A4C")
write("b3-commit", o, "커밋 결과 첫 줄 대괄호 안에 지금 브랜치 이름이 나와요. HEAD가 가리키는 이름표만 새 커밋으로 옮겨 가고, main은 그대로예요. 그래프에서 위로 갈라진 건 보기 쉽게 그린 것이에요.")

# b4: second commit
n4 = dict(n3); n4[E_] = (4, "up", "green", "n")
e4 = e3 + [(D, E_)]
o = frame("b4-commit2", "실습 5 · 한 번 더 커밋", 'git commit -m "feat: 끝인사 파일 추가"', cmd_size=48)
o += graph(n4, e4, [("main", C, "main"), (FB, E_, "green")], head=FB)
o += files([("bye.md", [("see you", "g")]), ("hello.md", None), ("README.md", None)])
o += terminal([("#", "# 새 파일 bye.md"), ("$", "git add bye.md"), ("$", 'git commit -m "feat: 끝인사 파일 추가"'),
               ("o", f"[{FB} {E_}] feat: 끝인사 파일 추가"), ("o", " 1 file changed, 1 insertion(+)"), ("o", " create mode 100644 bye.md")])
o += callout("Activity", "브랜치 위에<br>커밋이 쌓여요", "main에는 아직 아무 영향 없음", icolor="#1F8A4C")
write("b4-commit2", o, "기능 하나를 끝낼 때까지 브랜치에서 여러 번 커밋해도 돼요. main은 계속 처음 모습 그대로라 언제든 돌아갈 수 있어요.")

# b5: checkout main
o = frame("b5-back", "실습 6 · main으로 돌아가기", "git checkout main")
o += graph(n4, e4, [("main", C, "main"), (FB, E_, "green")], head="main")
o += files([HELLO2, ("README.md", None), ("bye.md", "x")])
o += terminal([("$", "git checkout main"), ("o", "Switched to branch 'main'"), ("$", "ls"), ("o", "README.md  hello.md")])
o += callout("Home", "파일도 main 시점으로<br>바뀌어요", "bye.md는 사라진 게 아니라<br>브랜치에 있어요", icolor="#2459C9")
write("b5-back", o, "checkout은 HEAD를 옮기면서 작업 폴더 파일도 그 브랜치의 마지막 커밋 모습으로 바꿔요. bye.md가 안 보여 당황하는 학생이 많아요. git checkout feat/greeting 하면 다시 나타나요. 커밋하지 않은 변경이 있으면 checkout이 막힐 수 있어요(막힐 때 파트 참고).")

# b6: fast-forward merge
o = frame("b6-merge-ff", "실습 7 · 브랜치 합치기", f"git merge {FB}")
o += graph(n4, e4, [(FB, E_, "green"), ("main", E_, "main")], head="main")
o += files([("hello.md", [("hello", "o"), ("world", "o"), ("nice to meet you", "g")]), ("bye.md", [("see you", "g")]), ("README.md", None)])
o += terminal([("$", f"git merge {FB}"), ("o", f"Updating {C}..{E_}"), ("g", "Fast-forward"),
               ("o", " bye.md   | 1 +"), ("o", " hello.md | 1 +"), ("o", " 2 files changed, 2 insertions(+)"), ("o", " create mode 100644 bye.md")])
o += callout("Lightning", "Fast-forward:<br>이름표만 앞으로", "main 쪽에 새 커밋이 없어서<br>합칠 게 없었어요")
write("b6-merge-ff", o, "merge는 지금 있는 브랜치(main)로 다른 브랜치를 가져와요. 그래서 먼저 main으로 돌아간 거예요. main이 갈라진 뒤 커밋이 없었으니 Git은 main 이름표를 앞으로 당기기만 해요. 이걸 빨리 감기(Fast-forward)라고 해요.")

# b7: delete branch, straighten
n7 = dict(base); n7[D] = (3, "main", "main", "n"); n7[E_] = (4, "main", "main", "n")
e7 = base_e + [(C, D), (D, E_)]
o = frame("b7-delete", "실습 8 · 다 쓴 브랜치 지우기", f"git branch -d {FB}")
o += graph(n7, e7, [("main", E_, "main")], head="main")
o += files([("hello.md", None), ("README.md", None), ("bye.md", None)])
o += terminal([("$", f"git branch -d {FB}"), ("o", f"Deleted branch {FB} (was {E_})."), ("$", "git branch"), ("g", "* main")])
o += callout("CheckCircle", "이름표만 떼요", "커밋은 main에 한 줄로 남아요")
write("b7-delete", o, "-d는 이미 합친 브랜치만 지워요. 합치지 않은 브랜치는 경고를 내고 멈춰요(막힐 때 파트). 지워도 커밋은 남고, main의 기록이 한 줄로 이어져요.")

# ---------- 갈라진 길 합치기 ----------
DU = "docs/usage"
README2 = ("README.md", [("# hello-git", "o"), ("", "o"), ("인사 파일 모음", "g")])
BYE2 = ("bye.md", [("see you", "o"), ("bye", "g")])
n8 = dict(n7); n8[F] = (5, "up", "orange", "n")
e8 = e7 + [(E_, F)]
o = frame("b8-branch2", "실습 9 · 새 브랜치에서 커밋", f"git checkout -b {DU}")
o += graph(n8, e8, [("main", E_, "main"), (DU, F, "orange")], head=DU)
o += files([README2, ("hello.md", None), ("bye.md", None)])
o += terminal([("$", f"git checkout -b {DU}"), ("o", f"Switched to a new branch '{DU}'"), ("#", "# README.md에 소개 추가"),
               ("$", "git add README.md"), ("$", 'git commit -m "docs: README에 소개 추가"'),
               ("o", f"[{DU} {F}] docs: README에 소개 추가"), ("o", " 1 file changed, 2 insertions(+)")])
o += callout("Book", "이번엔 docs/usage에서<br>README 작업", None, icolor="#B26A00")
write("b8-branch2", o, "문서 작업이라 docs/로 시작하는 이름을 썼어요. 커밋 타입과 브랜치 이름 앞부분을 맞추면 무슨 작업인지 바로 보여요.")

n9 = dict(n8); n9[G] = (5, "main", "main", "n")
e9 = e8 + [(E_, G)]
o = frame("b9-diverge", "실습 10 · 그 사이 main에도 커밋", 'git commit -m "feat: 끝인사 한 줄 추가"', cmd_size=48)
o += graph(n9, e9, [("main", G, "main"), (DU, F, "orange")], head="main")
o += files([BYE2, ("hello.md", None), ("README.md", None)])
o += terminal([("$", "git checkout main"), ("o", "Switched to branch 'main'"), ("#", "# bye.md에 한 줄 추가"),
               ("$", "git add bye.md"), ("$", 'git commit -m "feat: 끝인사 한 줄 추가"'),
               ("o", f"[main {G}] feat: 끝인사 한 줄 추가"), ("o", " 1 file changed, 1 insertion(+)")])
o += callout("Activity", "길이 두 갈래로", "main에도, docs/usage에도<br>새 커밋이 있어요")
write("b9-diverge", o, "팀에서는 내가 브랜치에서 일하는 동안 main에 다른 사람 작업이 합쳐지는 일이 흔해요. 이번엔 이름표만 앞으로 당길 수 없어요.")

n10 = dict(n9); n10[M] = (6, "main", "main", "merge")
e10 = e9 + [(G, M), (F, M)]
o = frame("b10-merge", "실습 11 · 갈라진 길 합치기", f"git merge {DU}")
o += graph(n10, e10, [("main", M, "main")], head="main")
o += files([README2, BYE2, ("hello.md", None)])
o += terminal([("$", f"git merge {DU}"), ("#", "# 메시지 편집기가 열리면 그대로 저장하고 닫기"), ("o", "Merge made by the 'ort' strategy."),
               ("o", " README.md | 2 ++"), ("o", " 1 file changed, 2 insertions(+)"), ("$", f"git branch -d {DU}"),
               ("o", f"Deleted branch {DU} (was {F}).")])
o += callout("Link", "두 줄기를 잇는<br>merge 커밋", "편집기가 vim이면 :wq 로 저장하고 닫아요")
write("b10-merge", o, "양쪽에 새 커밋이 있으니 Git이 둘을 합친 새 커밋(merge 커밋)을 만들어요. 이 커밋은 부모가 둘이에요. 편집기에 Merge branch 'docs/usage'라는 메시지가 미리 적혀 있어요. 그대로 저장하고 닫으면 돼요. vim이 열리면 Esc를 누른 뒤 :wq 와 Enter를 쳐요. 합친 뒤 docs/usage는 지웠어요. 그래서 그래프에서 docs/usage 이름표가 사라졌어요. 커밋 d92e18b는 main 기록 안에 그대로 남아요.")

# ---------- 충돌 ----------
FK = "feat/korean"
n11 = {D: (3, "main", "main", "n"), E_: (4, "main", "main", "n"), F: (5, "up", "gray", "n"), G: (5, "main", "main", "n"),
       M: (6, "main", "main", "merge")}
e11 = [(D, E_), (E_, F), (E_, G), (G, M), (F, M)]
n12 = dict(n11); n12[K] = (7, "up", "green", "n"); n12[L] = (7, "main", "main", "n")
e12 = e11 + [(M, K), (M, L)]
o = frame("b11-both", "실습 12 · 같은 줄을 서로 다르게", "hello.md 첫 줄: hi vs 안녕", eyebrow_color="#A33131", transition="fade")
o += graph(n12, e12, [("main", L, "main"), (FK, K, "green")], head="main", off=3)
o += files([("main의 hello.md", [("hi", "b"), ("world", "o"), ("nice to meet you", "o")]),
            ("feat/korean의 hello.md", [("안녕", "g"), ("world", "o"), ("nice to meet you", "o")])], title="첫 줄이 달라요")
o += terminal([("$", f"git checkout -b {FK}"), ("$", "git add hello.md"), ("$", 'git commit -m "feat: 인사를 한국어로"'),
               ("o", f"[{FK} {K}] feat: 인사를 한국어로"), ("$", "git checkout main"), ("$", "git add hello.md"),
               ("$", 'git commit -m "feat: 인사를 짧게"'), ("o", f"[main {L}] feat: 인사를 짧게")])
o += callout("Warning", "이대로 합치면?", "Git은 hi와 안녕 중<br>무엇을 남길지 몰라요", icolor="#A33131")
write("b11-both", o, "feat/korean에서는 첫 줄을 안녕으로, main에서는 hi로 고쳤어요. 출력 중 Switched to... 줄과 1 file changed 줄은 화면 폭 때문에 뺐어요. 그래프 왼쪽 점선은 앞의 커밋들이 이어진다는 뜻이에요.")

n13 = dict(n12); n13[RZ] = (8, "main", "main", "ghost")
e13 = e12 + [(L, RZ), (K, RZ)]
CONFLICT = [("<<<<<<< HEAD", "r"), ("hi", "b"), ("=======", "r"), ("안녕", "g"), (">>>>>>> feat/korean", "r"), ("world", "o"), ("nice to meet you", "o")]
o = frame("b12-conflict", "실습 13 · 충돌", f"git merge {FK}", eyebrow_color="#A33131")
o += graph(n13, e13, [("main", L, "main"), (FK, K, "green")], head="main", off=3, ghost_edges=[(L, RZ), (K, RZ)])
o += files([("hello.md", CONFLICT)])
o += terminal([("$", f"git merge {FK}"), ("o", "Auto-merging hello.md"), ("r", "CONFLICT (content): Merge conflict in hello.md"),
               ("o", "Automatic merge failed; fix conflicts and then commit the result."), ("$", "git status"),
               ("o", "Unmerged paths:"), ("h", '  (use "git add <file>..." to mark resolution)'), ("r", "\tboth modified:   hello.md")])
o += callout("Warning", "합치다 멈췄어요", "Git이 파일에 양쪽 내용을<br>모두 적어 뒀어요", icolor="#A33131")
write("b12-conflict", o, "충돌은 고장이 아니에요. Git이 고를 수 없는 부분만 표시해 두고 멈춘 상태예요. 다른 줄(world, nice to meet you)은 알아서 합쳐졌어요. git status 출력 앞뒤의 안내 줄 일부는 뺐어요. 그만두고 싶으면 git merge --abort로 합치기 전으로 돌아가요.")

n14 = dict(n12); n14[RZ] = (8, "main", "main", "merge")
o = frame("b13-resolve", "실습 14 · 충돌 해결하고 커밋", 'git commit -m "fix: 인사 충돌 해결"', cmd_size=48)
o += graph(n14, e13, [("main", RZ, "main")], head="main", off=3)
o += files([("hello.md", [("안녕", "g"), ("world", "o"), ("nice to meet you", "o")])])
o += terminal([("#", "# 표시 세 줄을 지우고 안녕만 남긴 뒤 저장"), ("$", "git add hello.md"), ("$", "git status"),
               ("o", "All conflicts fixed but you are still merging."), ("$", 'git commit -m "fix: 인사 충돌 해결"'),
               ("o", f"[main {RZ}] fix: 인사 충돌 해결"), ("$", f"git branch -d {FK}"), ("o", f"Deleted branch {FK} (was {K}).")])
o += callout("CheckCircle", "고친 파일을 add,<br>그리고 commit", "이 커밋이 두 줄기를 이어요", icolor="#1F8A4C")
write("b13-resolve", o, "충돌 표시(<<<<<<<, =======, >>>>>>>)를 남긴 채 커밋하지 않도록 저장 전에 꼭 확인해요. add는 '이 파일 충돌 해결했어요'라는 표시예요. 커밋하면 merge 커밋이 생겨요.")

# ---------- GitHub에서 함께 ----------
FE = "feat/emoji"
n15 = {F: (5, "up", "gray", "n"), G: (5, "main", "main", "n"), M: (6, "main", "main", "merge"), K: (7, "up", "gray", "n"),
       L: (7, "main", "main", "n"), RZ: (8, "main", "main", "merge"), P: (9, "up", "orange", "n")}
e15 = [(G, M), (F, M), (M, K), (M, L), (L, RZ), (K, RZ), (RZ, P)]
o = frame("b14-push", "실습 15 · 브랜치를 GitHub에 올리기", f"git push origin {FE}")
o += graph(n15, e15, [("main", RZ, "main"), ("origin/main", RZ, "origin"), (FE, P, "orange"), ("origin/feat/emoji", P, "origin")], head=FE, off=5)
o += terminal([("$", f"git checkout -b {FE}"), ("$", 'git commit -am "feat: 끝인사 하나 더"'), ("o", f"[{FE} {P}] feat: 끝인사 하나 더"),
               ("$", f"git push origin {FE}"), ("h", f"remote: Create a pull request for '{FE}' on GitHub by visiting:"),
               ("h", f"remote:      https://github.com/kim/hello-git/pull/new/{FE}"), ("o", "To https://github.com/kim/hello-git.git"),
               ("g", f" * [new branch]      {FE} -> {FE}")])
o += callout("Cloud", "브랜치째 GitHub으로", "-u 없이 origin 브랜치이름까지<br>끝까지 적어요", icolor="#6B47D6")
o += files([("bye.md", [("see you", "o"), ("bye", "o"), ("bye bye", "g")])])
write("b14-push", o, "commit -am은 이미 아는 파일(bye.md)의 add와 commit을 한 번에 하는 옵션이에요. 새 파일엔 안 돼요. push할 때 main 대신 브랜치 이름을 적어요. 우리 과정 규칙대로 -u는 쓰지 않아요. GitHub이 Pull Request를 만들 주소를 알려 줘요. push 출력 앞부분(Enumerating objects...)은 뺐어요.")

n16 = dict(n15); n16[Q] = (10, "main", "main", "merge")
e16 = e15 + [(RZ, Q), (P, Q)]
o = frame("b15-after-pr", "실습 16 · GitHub에서 merge한 뒤", "git checkout main → git pull origin main", cmd_size=44)
o += graph(n16, e16, [("main", Q, "main"), ("origin/main", Q, "origin"), ("origin/feat/emoji", P, "origin")], head="main", off=5)
o += terminal([("$", "git checkout main"), ("o", "Switched to branch 'main'"), ("$", "git pull origin main"),
               ("o", f"Updating {RZ}..{Q}"), ("g", "Fast-forward"), ("o", " bye.md | 1 +"), ("$", f"git branch -d {FE}"),
               ("o", f"Deleted branch {FE} (was {P}).")])
o += callout("CheckCircle", "GitHub의 merge를<br>내 main으로 받아요", "Pull Request merge 커밋이<br>새로 생겨 있어요", icolor="#6B47D6")
o += files([("bye.md", [("see you", "o"), ("bye", "o"), ("bye bye", "o")])])
write("b15-after-pr", o, f"GitHub에서 Merge pull request를 누르면 GitHub에 merge 커밋({Q}, 메시지 Merge pull request #1 from kim/{FE})이 생겨요. 내 컴퓨터는 아직 모르니 main으로 돌아가 pull로 받아요. pull 출력의 From, FETCH_HEAD 줄은 뺐어요. 로컬 브랜치는 -d로 지워요. origin/{FE} 이름표는 GitHub에서 브랜치를 지운 뒤에도 내 컴퓨터에 남아 있어요. git fetch origin --prune 하면 정리돼요.")

print("ok")
