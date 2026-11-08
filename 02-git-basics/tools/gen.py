"""Generates every slide of the Git basics deck (02).

Practice scenes share one 4-zone frame (working folder, staging, local repo, GitHub).
Terminal output comes from real git 2.43 runs; hashes are kept the same across slides.
Usage (in 02-git-basics): python3 tools/gen.py slides
"""
import html, math, os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from highlight import spot, spot_off, cursor, cursor_off, ring, box, underline  # noqa: E402

OUT = sys.argv[1]
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"

# zone geometry. Zones are filled panels with no outline; the zone that changes is lit by the spotlight.
GAP = 32
Z = {
    "wd": dict(left=96, w=340, bg="#FFFFFF", tc="#3A4150", sc="#6A7180", icon="Code", title="① 작업 폴더"),
    "st": dict(left=96 + 340 + GAP, w=340, bg="#E9F6EE", tc="#1A7340", sc="#2D5E40", icon="CheckCircle", title="② 대기실"),
    "lr": dict(left=96 + 680 + 2 * GAP, w=476, bg="#E8F0FD", tc="#1E3F8F", sc="#2E4D8F", icon="Database", title="③ 내 저장소"),
    "rm": dict(left=96 + 1156 + 3 * GAP, w=476, bg="#F0EBFD", tc="#5A3BB8", sc="#5A4A8F", icon="Cloud", title="④ GitHub"),
}
ZTOP = 228
IN = 20                         # inner padding of a zone
ROW0, PITCH = 312, 52           # commit rows
CARD_TOP, CARD_H, CARD_GAP = 304, 112, 14
FS = 26                         # hash and tag size
CW = FS * 0.6                   # mono glyph width
HASH_W = 24 + 12 + 7 * CW       # dot, gap, 7-char hash
CUR = {"zh": 404}              # zone height of the slide being built; parts with less to show use shorter zones

FILE_STYLE = {
    "red":   ("#FBE4E2", "#A33131"),
    "green": ("#D3EEDD", "#1A7340"),
    "gray":  ("#EEEFF2", "#3A4150"),
    "ghost": ("transparent", "#6A7180"),
    "new":   ("#E2D8FB", "#4A2FA8"),
}


def e(s):
    return html.escape(s, quote=False)


def p(style, text, attrs=""):
    return f'<p{attrs} style="{style}">{text}</p>'


def zx(k):
    return Z[k]["left"] + IN


def frame(sec_id, eyebrow, title, local_label="내 컴퓨터", rm_dim=False, transition="magic", zh=404):
    CUR["zh"] = zh
    o = [f'<section id="{sec_id}" data-transition="{transition}" style="background:#F6F5F1;color:#1D2330;font-family:{SANS};padding:96px;display:flex;flex-direction:column;word-break:keep-all">']
    o.append(p("position:absolute;left:96px;top:48px;width:1728px;font-size:26px;font-weight:700;color:#2459C9", e(eyebrow), ' id="eyebrow"'))
    o.append(f'<h2 id="title" style="position:absolute;left:96px;top:88px;width:1728px;font-size:52px;font-weight:700;line-height:1.2;color:#1D2330">{title}</h2>')
    # where the zones live: a quiet rule with its name, in place of a box around boxes
    lr_end = Z["lr"]["left"] + Z["lr"]["w"]
    o.append(f'<x-icon id="ic-local" name="Home" style="position:absolute;left:96px;top:178px;width:26px;height:26px;color:#6A7180"></x-icon>')
    o.append(p("position:absolute;left:130px;top:175px;width:600px;font-size:24px;font-weight:700;color:#6A7180", e(local_label), ' id="lbl-local"'))
    o.append(f'<div style="position:absolute;left:96px;top:212px;width:{lr_end - 96}px;height:2px;background:#CDD0D6"></div>')
    rl = Z["rm"]["left"]
    o.append(f'<x-icon id="ic-remote" name="Globe" style="position:absolute;left:{rl}px;top:178px;width:26px;height:26px;color:#5A3BB8"></x-icon>')
    o.append(p(f"position:absolute;left:{rl + 34}px;top:175px;width:400px;font-size:24px;font-weight:700;color:#5A3BB8", "인터넷", ' id="lbl-remote"'))
    o.append(f'<div style="position:absolute;left:{rl}px;top:212px;width:{Z["rm"]["w"]}px;height:2px;background:#C9BCF2"></div>')
    for k, z in Z.items():
        op = ";opacity:0.45" if (k == "rm" and rm_dim) else ""
        o.append(f'<div id="z-{k}" style="position:absolute;left:{z["left"]}px;top:{ZTOP}px;width:{z["w"]}px;height:{zh}px;background:{z["bg"]};border-radius:20px;padding:20px {IN}px{op}">'
                 '<div style="display:flex;flex-direction:row;gap:12px;align-items:center">'
                 f'<x-icon name="{z["icon"]}" style="width:32px;height:32px;color:{z["tc"]}"></x-icon>'
                 + p(f"font-size:30px;font-weight:700;color:{z['tc']}", z["title"]) + '</div></div>')
    return o


def placeholder(k, text, top=None):
    z = Z[k]
    return p(f"position:absolute;left:{zx(k)}px;top:{top or CARD_TOP + 8}px;width:{z['w'] - 2 * IN}px;font-size:26px;color:{z['sc']}", e(text), f' id="ph-{k}"')


def file_card(cid, k, slot, name, status, style, hidden=False, at=None):
    z = Z[at or k]
    bg, col = FILE_STYLE[style]
    top = CARD_TOP + slot * (CARD_H + CARD_GAP)
    op = ";opacity:0" if hidden else ""
    bd = "border:2px dashed #B4B9C3;" if style == "ghost" else ""
    return (f'<div id="{cid}" style="position:absolute;left:{z["left"] + IN}px;top:{top}px;width:{z["w"] - 2 * IN}px;height:{CARD_H}px;background:{bg};{bd}border-radius:14px;padding:16px 16px;display:flex;flex-direction:column;gap:6px{op}">'
            + p(f"font-family:{MONO};font-size:30px;font-weight:700;line-height:1.3;color:#1D2330", e(name))
            + p(f"font-size:23px;font-weight:700;line-height:1.3;white-space:nowrap;color:{col}", e(status))
            + '</div>')


def flyer(cid, k, row):
    """invisible box at a commit row, the landing spot of a card flying into a repo"""
    return f'<div id="{cid}" style="position:absolute;left:{zx(k)}px;top:{ROW0 + row * PITCH - 4}px;width:{HASH_W:.0f}px;height:44px;background:#D3EEDD;border-radius:12px;opacity:0"></div>'


def commits(k, rows, prefix):
    """rows: newest first, (hash, ghost[, hidden[, faded]])"""
    o = []
    if not rows:
        return o
    x = zx(k)
    if len(rows) > 1:
        rop = ";opacity:0" if all(len(r) > 2 and r[2] for r in rows) else ""
        o.append(f'<div id="{prefix}-rail" style="position:absolute;left:{x + 10}px;top:{ROW0 + 18}px;width:4px;height:{(len(rows) - 1) * PITCH}px;background:#A9C0F0{rop}"></div>')
    for i, (h, ghost, *rest) in enumerate(rows):
        hidden = rest[0] if rest else False
        faded = len(rest) > 1 and rest[1]
        dot = "background:#E8F0FD;border:3px dashed #6B47D6;" if ghost else "background:#2459C9;border:3px solid #2459C9;"
        hc = "#6B47D6" if ghost else "#1E3F8F"
        op = "opacity:0;" if hidden else ("opacity:0.3;" if faded else "")
        o.append(f'<div id="{prefix}-{h}" style="position:absolute;left:{x}px;top:{ROW0 + i * PITCH}px;width:{HASH_W:.0f}px;height:38px;display:flex;flex-direction:row;gap:12px;align-items:center;{op}">'
                 f'<x-shape kind="ellipse" style="width:24px;height:24px;flex:none;{dot}"></x-shape>'
                 + p(f"font-family:{MONO};font-size:{FS}px;font-weight:700;color:{hc}", h) + '</div>')
    return o


TAG_W = {"main": 3 * CW + 24 + 6, "origin/main": 11 * CW + 24 + 4}


def tag(tid, k, row, slot, text, kind):
    left = zx(k) + HASH_W + 14 + (0 if slot == 0 else TAG_W["main"] + 8)
    styles = {"main": "background:#2459C9;color:#FFFFFF", "rmain": "background:#6B47D6;color:#FFFFFF",
              "origin": "background:#FFFFFF;color:#4A2FA8;box-shadow:inset 0 0 0 2px #8E6FEA"}
    return p(f"position:absolute;left:{left:.0f}px;top:{ROW0 + row * PITCH}px;width:{TAG_W[text]:.0f}px;font-family:{MONO};font-size:{FS}px;font-weight:700;line-height:38px;text-align:center;border-radius:8px;{styles[kind]}", e(text), f' id="{tid}"')


def arrow(gap, direction="right", top=None, color="#2459C9", order=None):
    a, b = gap.split("-")
    left = Z[a]["left"] + Z[a]["w"] + (GAP - 28) // 2
    b_ = f' data-build-in="fade{" order " + str(order) if order else ""}"'
    return f'<x-shape kind="arrow-{direction}"{b_} style="position:absolute;left:{left}px;top:{top or CARD_TOP + 42}px;width:28px;height:28px;background:{color}"></x-shape>'


def pop(k, top, text, color="#1E3F8F", width=None, left=None, order=None, **_):
    """A label on the drawing: plain words right under the thing they explain, no box."""
    z = Z[k]
    b = f' data-build-in="pop{" order " + str(order) if order else ""}"'
    w = width or (z["w"] - 2 * IN)
    l = left if left is not None else zx(k)
    return p(f"position:absolute;left:{l}px;top:{top}px;width:{w}px;font-size:26px;font-weight:700;line-height:1.4;color:{color}", text, b)


def under(k, slot):
    """top of a label right under file card `slot` of zone k"""
    return CARD_TOP + (slot + 1) * (CARD_H + CARD_GAP) - 2


def below(nrows):
    """top of a label right under n commit rows"""
    return ROW0 + nrows * PITCH + 10


TERM_COLORS = {"$": "#F2C46D", "o": "#D8DEE9", "h": "#9AA3B5", "g": "#7FD18B", "r": "#F28B82", "#": "#9AA3B5"}


def tsteps(lines):
    """Click steps a typed terminal uses: one per command, one for the output lines after it."""
    cur, prev = 0, None
    for kind, _ in lines:
        if kind == "$" or prev == "$":
            cur += 1
        prev = kind
    return cur


def terminal(lines, left=96, top=None, w=1728, h=None, size=None, lh=1.4, build=None, tid="term"):
    top = top or ZTOP + CUR["zh"] + 32
    h = h or 1024 - top
    size = size or min(33, int((h - 52) / (len(lines) * lh)))
    """build: first click order (None = no animation). Each command is typed on its own click and the
    output lines after it come in together on the next click."""
    o = [f'<div id="{tid}" style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:#1B2029;border-radius:20px;padding:26px 36px;display:flex;flex-direction:column;font-family:{MONO};font-variant-ligatures:none">']
    cur, prev = (build or 1) - 1, None
    for kind, text in lines:
        t = e(text)
        lead = len(t) - len(t.lstrip(" "))
        t = "&#160;" * lead + t.lstrip(" ") if t.strip() else "&#160;"
        t = t.replace("\t", "&#160;" * 8)
        if kind == "$":
            t = "$ " + t
        at = ""
        if build is not None:
            if kind == "$":
                cur += 1
                at = f' data-build-in="fade order {cur}"'
            else:
                if prev == "$":
                    cur += 1
                at = f' data-build-in="fade order {cur}"' if cur >= (build or 1) else ""
        prev = kind
        bold = "font-weight:700;" if kind == "$" else ""
        o.append(p(f"font-size:{size}px;line-height:{lh};white-space:pre;{bold}color:{TERM_COLORS[kind]}", t, at))
    o.append('</div>')
    return o


def write(sec_id, parts, notes, hot=None, lines=None):
    """Scene slides: lines = the terminal lines. After the typed terminal, the next click lights up the
    zones that changed (hot) and brings in the labels on the drawing; the click after that turns the
    light off so the whole picture reads as one."""
    body = "\n".join(parts)
    if lines is not None:
        n = 0  # the terminal is shown whole from the start; no typing
        body = re.sub(r'data-build-in="(pop|fade)"', lambda m: f'data-build-in="{m.group(1)} order {n + 1}"', body)
        extra = []
        if hot:
            x0 = min(Z[k]["left"] for k in hot)
            x1 = max(Z[k]["left"] + Z[k]["w"] for k in hot)
            extra.append(spot(n + 1, x0, ZTOP, x1 - x0, CUR["zh"], pad=10, r=26))
            extra.append(spot_off(n + 2))
        body += "\n" + "\n".join(extra)
    body += f"\n<aside>{e(notes)}</aside>\n</section>\n"
    with open(os.path.join(OUT, f"{sec_id}.html"), "w") as f:
        f.write(body)


def span(a, b):
    """left and width covering zones a..b"""
    return Z[a]["left"] + IN, Z[b]["left"] + Z[b]["w"] - IN - (Z[a]["left"] + IN)


H1, H2, H3, H4 = "538dd06", "a7c21f4", "3f9a2c1", "e73617d"
EB1, EB2, EB3 = "혼자 기록하기", "GitHub과 연결하기", "함께 작업하기"

# ---------- 혼자 기록하기 ----------
o = frame("s1-init", f"실습 1 · {EB1}", "폴더를 Git 저장소로 만들어요", rm_dim=True, zh=300)
o += [placeholder("wd", "빈 폴더"), placeholder("st", "비어 있음"), placeholder("lr", "커밋 없음")]
l, w = span("st", "lr")
o.append(pop("st", 364, "숨김 폴더 .git이 생겼어요.<br>②와 ③은 이 폴더 안에 있어요.", left=l, width=w))
o += terminal(T := [("$", "mkdir hello-git && cd hello-git"), ("$", "git init"),
               ("o", "Initialized empty Git repository in /Users/kim/hello-git/.git/"),
               ("$", "git status"), ("o", "On branch main"), ("o", ""), ("o", "No commits yet"), ("o", ""),
               ("o", 'nothing to commit (create/copy files and use "git add" to track)')])
write("s1-init", o, "git init으로 이 폴더를 Git이 지켜보기 시작해요. 저장소마다 한 번만 해요. 홈 폴더나 바탕화면에서 실행하지 않도록 주의해요. .git 폴더가 안 보이면 macOS Finder에서 Cmd+Shift+. 을 누르세요.", hot=['st', 'lr'], lines=T)

o = frame("s2-create", f"실습 2 · {EB1}", "새 파일을 하나 만들어요", rm_dim=True, zh=300)
o.append(file_card("snap-1", "st", 0, "hello.md", "Staged · 새 파일", "green", hidden=True, at="wd"))
o.append(file_card("wd-hello", "wd", 0, "hello.md", "Untracked · 새 파일", "red"))
o.append(pop("wd", under("wd", 0), "Git이 처음 보는 파일", color="#A33131"))
o += terminal(T := [("$", 'echo "hello" > hello.md'), ("$", "git status"), ("o", "On branch main"), ("o", "No commits yet"),
               ("o", "Untracked files:"), ("h", '  (use "git add <file>..." to include in what will be committed)'),
               ("r", "\thello.md"), ("o", "nothing added to commit but untracked files present")])
write("s2-create", o, "에디터에서 새 파일을 저장해도 같은 상태예요. Git은 파일을 저절로 기록하지 않아요. 빨간 글씨는 아직 기록 대상이 아니라는 뜻이에요. 마지막 줄 끝의 (use \"git add\" to track) 안내는 화면 폭 때문에 생략했어요.", hot=['wd'], lines=T)

o = frame("s3-add", f"실습 3 · {EB1}", "파일을 대기실에 올려요", rm_dim=True, zh=300)
o.append(file_card("wd-hello", "wd", 0, "hello.md", "원본은 그대로", "ghost"))
o.append(file_card("snap-1", "st", 0, "hello.md", "Staged · 새 파일", "green"))
o.append(arrow("wd-st", color="#1F8A4C"))
l, w = span("wd", "st")
o.append(pop("wd", under("wd", 0), "그 순간의 사진이 올라가요", color="#1A7340", left=l, width=w))
o += terminal(T := [("$", "git add hello.md"), ("#", "# 아무 출력이 없으면 성공"), ("$", "git status"), ("o", "On branch main"),
               ("o", "No commits yet"), ("o", "Changes to be committed:"),
               ("h", '  (use "git rm --cached <file>..." to unstage)'), ("g", "\tnew file:   hello.md")])
write("s3-add", o, "add는 파일을 옮기는 게 아니라 그 순간의 사진을 대기실에 올리는 거예요. 그래서 작업 폴더 원본은 그대로 있어요. 초록 글씨는 커밋할 준비가 끝났다는 뜻이에요. 여러 파일을 한 번에 올릴 땐 git add . 을 써요.", hot=['wd', 'st'], lines=T)

o = frame("s4-commit", f"실습 4 · {EB1}", "대기실에 올린 모습을 커밋해요", rm_dim=True, zh=300)
o += [placeholder("st", "비어 있음")]
o.append(file_card("wd-hello", "wd", 0, "hello.md", "Committed · 변경 없음", "gray"))
o.append(flyer("snap-1", "lr", 0))
o += commits("lr", [(H1, False)], "lc")
o.append(tag("lt-main", "lr", 0, 0, "main", "main"))
o.append(arrow("st-lr"))
o.append(pop("lr", below(1), f"{H1} 번으로 기록됐어요"))
o += terminal(T := [("$", 'git commit -m "feat: 인사 파일 추가"'), ("o", f"[main (root-commit) {H1}] feat: 인사 파일 추가"),
               ("o", " 1 file changed, 1 insertion(+)"), ("o", " create mode 100644 hello.md"),
               ("$", "git status"), ("o", "On branch main"), ("o", "nothing to commit, working tree clean")])
write("s4-commit", o, "메시지 앞의 feat: 는 지금은 그대로 따라 쓰고, 두 번째 커밋 뒤에 자세히 봐요. 대기실에 있던 모습이 커밋 538dd06으로 저장됐어요. 해시는 사람마다 다르게 나와요. main 이름표는 지금 가장 최신 커밋을 가리켜요. GitHub에는 아직 없어요. -m을 빼먹어 vim이 열리면 Esc를 누르고 :q!, Enter를 쳐서 나온 뒤 다시 실행해요.", hot=['st', 'lr'], lines=T)

o = frame("s5-edit", f"실습 5 · {EB1}", "커밋한 파일을 다시 고쳐요", rm_dim=True, zh=300)
o.append(file_card("snap-2", "st", 0, "hello.md", "Staged · 수정", "green", hidden=True, at="wd"))
o.append(file_card("wd-hello", "wd", 0, "hello.md", "Modified · 수정됨", "red"))
o += commits("lr", [(H1, False)], "lc")
o.append(tag("lt-main", "lr", 0, 0, "main", "main"))
o.append(pop("wd", under("wd", 0), "마지막 커밋과 달라졌어요", color="#A33131"))
o += terminal(T := [("$", 'echo "world" >> hello.md'), ("$", "git status"), ("o", "On branch main"),
               ("o", "Changes not staged for commit:"),
               ("h", '  (use "git add <file>..." to update what will be committed)'),
               ("r", "\tmodified:   hello.md"), ("o", 'no changes added to commit (use "git add" and/or "git commit -a")')])
write("s5-edit", o, "Untracked는 처음 보는 파일, Modified는 이미 아는 파일이 바뀐 거예요. 다음은 다시 git add예요. 실제 status에는 안내 문구가 한 줄 더 나오지만 여기선 뺐어요.", hot=['wd'], lines=T)

o = frame("s6-mixed", "실습 6 · 헷갈림 주의", "add 한 뒤에 또 고치면 어떻게 될까요?", rm_dim=True, zh=300)
o.append(file_card("wd-hello", "wd", 0, "hello.md", "Modified · more 추가", "red"))
o.append(file_card("snap-2", "st", 0, "hello.md", "Staged · world까지", "green"))
o += commits("lr", [(H1, False)], "lc")
o.append(tag("lt-main", "lr", 0, 0, "main", "main"))
o.append(arrow("wd-st", color="#1F8A4C"))
l, w = span("wd", "st")
o.append(pop("wd", under("wd", 0), "같은 파일이 두 칸에 있어요.<br>지금 commit 하면 more는 빠져요.", color="#A33131", left=l, width=w))
o += terminal(T := [("$", "git add hello.md"), ("$", 'echo "more" >> hello.md'), ("$", "git status"),
               ("o", "Changes to be committed:"), ("g", "\tmodified:   hello.md"),
               ("o", "Changes not staged for commit:"), ("r", "\tmodified:   hello.md"), ("#", "# 안내 문구(use ...)는 생략")])
write("s6-mixed", o, "초록 줄과 빨간 줄에 같은 파일이 동시에 나오는 장면이에요. add는 그 순간의 사진이라는 걸 다시 짚어 주세요. 커밋 직전에 git status를 보고 빨간 글씨가 남아 있으면 add부터 해요.", hot=['wd', 'st'], lines=T)

o = frame("s7-commit2", f"실습 7 · {EB1}", "add, commit을 한 번 더 해요", rm_dim=True, zh=300)
o += [placeholder("st", "비어 있음")]
o.append(file_card("wd-hello", "wd", 0, "hello.md", "Committed · 변경 없음", "gray"))
o.append(flyer("snap-2", "lr", 0))
o += commits("lr", [(H2, False), (H1, False)], "lc")
o.append(tag("lt-main", "lr", 0, 0, "main", "main"))
o.append(arrow("st-lr"))
o.append(pop("lr", below(2), "main은 늘 최신 커밋에 붙어요"))
o += terminal(T := [("$", "git add hello.md"), ("$", 'git commit -m "feat: 인사말 추가"'),
               ("o", f"[main {H2}] feat: 인사말 추가"), ("o", " 1 file changed, 2 insertions(+)"),
               ("$", "git log --oneline"), ("o", f"{H2} (HEAD -> main) feat: 인사말 추가"), ("o", f"{H1} feat: 인사 파일 추가")])
write("s7-commit2", o, "커밋은 점, 점을 잇는 선은 순서예요. 위가 최신이에요. main 이름표가 새 커밋으로 옮겨 가는 걸 보여 주세요. git log --oneline이 이 그림을 글자로 보여 주는 명령이에요.", hot=['st', 'lr'], lines=T)

# ---------- GitHub 연결 ----------
o = frame("s9-remote", f"실습 9 · {EB2}", "GitHub 주소를 origin이라는 이름으로 등록해요", zh=340)
o += [placeholder("rm", "빈 저장소")]
o.append(file_card("wd-hello", "wd", 0, "hello.md", "Committed · 변경 없음", "gray"))
o += commits("lr", [(H2, False), (H1, False)], "lc")
o += commits("rm", [(H2, False, True), (H1, False, True)], "rc")
o.append(tag("lt-main", "lr", 0, 0, "main", "main"))
o.append(f'<x-icon name="Link" data-build-in="pop" style="position:absolute;left:{Z["rm"]["left"] - 30}px;top:{ROW0 + 4}px;width:28px;height:28px;color:#6B47D6"></x-icon>')
o.append(pop("rm", ROW0 + 56, "주소에 별명 origin을 붙였어요.<br>아직 보낸 건 없어요.", color="#4A2FA8"))
o += terminal(T := [("$", "git remote add origin https://github.com/kim/hello-git.git"), ("#", "# 출력 없음 = 등록 성공"),
               ("$", "git remote -v"), ("o", "origin  https://github.com/kim/hello-git.git (fetch)"),
               ("o", "origin  https://github.com/kim/hello-git.git (push)")])
write("s9-remote", o, "전화번호부에 번호를 저장한 것과 같아요. 저장만 했지 전화를 건 건 아니에요. origin은 이 주소에 붙인 별명이에요.", hot=['lr', 'rm'], lines=T)

o = frame("s10-push", f"실습 10 · {EB2}", "내 커밋을 GitHub으로 보내요", zh=340)
o.append(file_card("wd-hello", "wd", 0, "hello.md", "Committed · 변경 없음", "gray"))
o += commits("lr", [(H2, False), (H1, False)], "lc")
o += commits("rm", [(H2, False), (H1, False)], "rc")
o.append(tag("lt-main", "lr", 0, 0, "main", "main"))
o.append(tag("lt-origin", "lr", 0, 1, "origin/main", "origin"))
o.append(tag("rt-main", "rm", 0, 0, "main", "rmain"))
o.append(arrow("lr-rm", top=ROW0 + 5, color="#6B47D6"))
o.append(pop("rm", below(2), "해시가 같으면 같은 커밋이에요", color="#4A2FA8"))
o += terminal(T := [("$", "git push origin main"), ("o", "Enumerating objects: 6, done."),
               ("o", "Writing objects: 100% (6/6), 466 bytes | 466.00 KiB/s, done."),
               ("o", "To https://github.com/kim/hello-git.git"), ("o", " * [new branch]      main -> main"),
               ("$", "git log --oneline"), ("o", f"{H2} (HEAD -> main, origin/main) feat: 인사말 추가"),
               ("o", f"{H1} feat: 인사 파일 추가")])
write("s10-push", o, "push 뒤에 어디로(origin), 무엇을(main) 보낼지 적어요. 우리 과정에서는 -u를 쓰지 않고 매번 git push origin main처럼 둘 다 적어요. origin/main 이름표는 내 컴퓨터가 기억하는 GitHub의 main 위치예요. 처음 push 할 때 GitHub 로그인이나 토큰 입력 창이 뜰 수 있어요.", hot=['lr', 'rm'], lines=T)

o = frame("s11-ahead", "실습 11 · 커밋만 하고 push 안 하면?", "status는 깨끗한데, GitHub에는 없어요", zh=340)
o.append(file_card("wd-hello", "wd", 0, "hello.md", "Committed · 변경 없음", "gray"))
o += commits("lr", [(H3, False), (H2, False), (H1, False)], "lc")
o += commits("rm", [(H2, False), (H1, False)], "rc")
o.append(f'<div id="rc-{H3}" style="position:absolute;left:{zx("lr")}px;top:{ROW0}px;width:{HASH_W:.0f}px;height:38px;opacity:0"></div>')
o.append(tag("lt-main", "lr", 0, 0, "main", "main"))
o.append(tag("lt-origin", "lr", 1, 1, "origin/main", "origin"))
o.append(tag("rt-main", "rm", 0, 0, "main", "rmain"))
o.append(pop("lr", below(3), "main이 origin/main보다 한 칸 위,<br>아직 안 보낸 커밋이에요", color="#A33131"))
o += terminal(T := [("$", "git add hello.md"), ("$", 'git commit -m "feat: 끝인사 추가"'), ("o", f"[main {H3}] feat: 끝인사 추가"),
               ("$", "git status"), ("o", "nothing to commit, working tree clean"),
               ("$", "git log --oneline"), ("o", f"{H3} (HEAD -> main) feat: 끝인사 추가"),
               ("o", f"{H2} (origin/main) feat: 인사말 추가"), ("o", f"{H1} feat: 인사 파일 추가")])
write("s11-ahead", o, "-u 없이 작업하면 git status가 GitHub과 비교해 주지 않아요. 그래서 clean이라고만 나와요. 안 보낸 커밋은 git log --oneline에서 main이 origin/main보다 위에 있는지로 확인해요.", hot=['lr'], lines=T)

o = frame("s12-push2", f"실습 12 · {EB2}", "한 번 더 push 해서 맞춰요", zh=340)
o.append(file_card("wd-hello", "wd", 0, "hello.md", "Committed · 변경 없음", "gray"))
o += commits("lr", [(H3, False), (H2, False), (H1, False)], "lc")
o += commits("rm", [(H3, False), (H2, False), (H1, False)], "rc")
o.append(tag("lt-main", "lr", 0, 0, "main", "main"))
o.append(tag("lt-origin", "lr", 0, 1, "origin/main", "origin"))
o.append(tag("rt-main", "rm", 0, 0, "main", "rmain"))
o.append(arrow("lr-rm", top=ROW0 + 5, color="#6B47D6"))
o.append(pop("lr", below(3), "main과 origin/main이 같은 칸이에요", color="#1A7340"))
o += terminal(T := [("$", "git push origin main"), ("o", "To https://github.com/kim/hello-git.git"),
               ("o", f"   {H2}..{H3}  main -> main"), ("$", "git log --oneline"),
               ("o", f"{H3} (HEAD -> main, origin/main) feat: 끝인사 추가"), ("o", f"{H2} feat: 인사말 추가"),
               ("o", f"{H1} feat: 인사 파일 추가")])
write("s12-push2", o, f"두 번째 push부터는 바뀐 커밋만 보내요. {H2}..{H3}는 그 사이 커밋을 보냈다는 뜻이에요.", hot=['lr', 'rm'], lines=T)

# ---------- 함께 작업하기 ----------
o = frame("s13-clone", "실습 13 · 팀원 컴퓨터에서", "팀원이 저장소를 통째로 받아요", local_label="팀원 컴퓨터", transition="fade", zh=360)
o += commits("rm", [(H3, False), (H2, False), (H1, False)], "rc")
o.append(tag("rt-main", "rm", 0, 0, "main", "rmain"))
N13 = 0  # the terminal has no click steps
o.append(arrow("lr-rm", "left", top=ROW0 + 5, color="#6B47D6", order=N13 + 1))
o.append(f'<div data-build-in="left order {N13 + 1}" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none">')
o += commits("lr", [(H3, False), (H2, False), (H1, False)], "cl")
o.append(tag("cl-main", "lr", 0, 0, "main", "main"))
o.append(tag("cl-origin", "lr", 0, 1, "origin/main", "origin"))
o.append('</div>')
o.append(file_card("cl-hello", "wd", 0, "hello.md", "최신 커밋 모습", "gray").replace("<div ", f'<div data-build-in="left order {N13 + 2}" ', 1))
o.append(pop("lr", below(3), "origin 등록도 저절로 돼요", color="#4A2FA8", order=N13 + 2))
o += terminal(T := [("$", "cd ~/projects"), ("$", "git clone https://github.com/kim/hello-git.git"),
               ("o", "Cloning into 'hello-git'..."), ("o", "Receiving objects: 100% (9/9), done."),
               ("$", "cd hello-git"), ("#", "# 새로 생긴 폴더로 꼭 들어가기"), ("$", "ls"), ("o", "hello.md")])
write("s13-clone", o, "팀원이 이 저장소에 합류하는 장면이에요. clone은 폴더 만들기, git init, remote add origin, 커밋 받기를 한 번에 해요. clone한 폴더에서 init이나 remote add를 다시 하지 않아요. 팀원은 이어서 README.md를 만들고 add, commit, push 해요(docs: README 추가).", hot=None, lines=T)

o = frame("s14-fetch", "실습 14 · 다시 내 컴퓨터 (팀원이 README를 push했어요)", "GitHub 소식을 받아만 와요", transition="magic", zh=360)
o.append(file_card("wd-hello", "wd", 0, "hello.md", "Committed · 변경 없음", "gray"))
o.append(file_card("wd-readme", "wd", 1, "README.md", "pull로 생김", "new", hidden=True, at="lr"))
o += commits("lr", [(H4, True), (H3, False), (H2, False), (H1, False)], "lc")
o += commits("rm", [(H4, False), (H3, False), (H2, False), (H1, False)], "rc")
o.append(tag("lt-origin", "lr", 0, 1, "origin/main", "origin"))
o.append(tag("lt-main", "lr", 1, 0, "main", "main"))
o.append(tag("rt-main", "rm", 0, 0, "main", "rmain"))
o.append(arrow("lr-rm", "left", top=ROW0 + 5, color="#6B47D6"))
o.append(pop("lr", below(4), "origin/main만 올라갔어요", color="#4A2FA8"))
o.append(pop("wd", under("wd", 0), "작업 폴더는 그대로예요", color="#6A7180"))
o += terminal(T := [("$", "git fetch origin"), ("o", "From https://github.com/kim/hello-git"),
               ("o", f"   {H3}..{H4}  main       -> origin/main"), ("$", "git log --oneline origin/main"),
               ("o", f"{H4} (origin/main) docs: README 추가"), ("o", f"{H3} (HEAD -> main) feat: 끝인사 추가"),
               ("o", f"{H2} feat: 인사말 추가"), ("o", f"{H1} feat: 인사 파일 추가")])
write("s14-fetch", o, "fetch는 GitHub의 새 소식을 받아 origin/main 이름표만 옮겨요. 내 main보다 앞선 커밋은 git log --oneline origin/main으로 봐요. 그냥 git log --oneline에는 내 main까지만 나와요. 점선 커밋은 받아 왔지만 아직 내 main에 합치지 않은 커밋이에요. 작업 폴더에는 README.md가 아직 없어요.", hot=['lr', 'rm'], lines=T)

o = frame("s15-pull", "실습 15 · 받아서 합치기", "받아서 내 것에 합쳐요", zh=360)
o.append(file_card("wd-hello", "wd", 0, "hello.md", "Committed · 변경 없음", "gray"))
o.append(file_card("wd-readme", "wd", 1, "README.md", "pull로 생김", "new"))
o += commits("lr", [(H4, False), (H3, False), (H2, False), (H1, False)], "lc")
o += commits("rm", [(H4, False), (H3, False), (H2, False), (H1, False)], "rc")
o.append(tag("lt-main", "lr", 0, 0, "main", "main"))
o.append(tag("lt-origin", "lr", 0, 1, "origin/main", "origin"))
o.append(tag("rt-main", "rm", 0, 0, "main", "rmain"))
o.append(arrow("lr-rm", "left", top=ROW0 + 5, color="#6B47D6"))
o.append(arrow("wd-st", "left", top=CARD_TOP + CARD_H + CARD_GAP + 42, color="#2459C9"))
o.append(arrow("st-lr", "left", top=CARD_TOP + CARD_H + CARD_GAP + 42, color="#2459C9"))
o.append(pop("lr", below(4), "main이 origin/main까지 따라왔어요", color="#1A7340"))
o += terminal(T := [("$", "git pull origin main"), ("o", "From https://github.com/kim/hello-git"),
               ("o", " * branch            main       -> FETCH_HEAD"), ("o", f"Updating {H3}..{H4}"),
               ("o", "Fast-forward"), ("o", " README.md | 1 +"), ("o", " 1 file changed, 1 insertion(+)"),
               ("o", " create mode 100644 README.md")])
write("s15-pull", o, "pull은 fetch(받기)와 merge(합치기)를 한 번에 해요. main 이름표가 origin/main 위치로 따라 올라가고, 그 커밋의 파일이 작업 폴더에 나타나요. 습관: 작업 시작 전에 git pull origin main.", hot=['wd', 'lr'], lines=T)

# ---------- 되돌리기 ----------
H5, H6 = "b81d4e2", "c4e9a07"
WD2 = [file_card("wd-hello", "wd", 0, "hello.md", "Committed · 변경 없음", "gray"),
       file_card("wd-readme", "wd", 1, "README.md", "Committed · 변경 없음", "gray")]

o = frame("s16-oops", "실습 16 · 되돌리기", "앗, 잘못 커밋했어요", transition="magic")
o += WD2
o += commits("lr", [(H5, False), (H4, False), (H3, False), (H2, False), (H1, False)], "lc")
o += commits("rm", [(H4, False), (H3, False), (H2, False), (H1, False)], "rc")
o.append(tag("lt-main", "lr", 0, 0, "main", "main"))
o.append(tag("lt-origin", "lr", 1, 1, "origin/main", "origin"))
o.append(tag("rt-main", "rm", 0, 0, "main", "rmain"))
o.append(pop("rm", below(4), "GitHub에는 아직 없어요 (push 전)", color="#A33131"))
o += terminal(T := [("$", 'echo "oops" >> hello.md'), ("$", "git add hello.md"), ("$", 'git commit -m "feat: 실수한 커밋"'),
               ("o", f"[main {H5}] feat: 실수한 커밋"), ("o", " 1 file changed, 1 insertion(+)"),
               ("$", "git log --oneline"), ("o", f"{H5} (HEAD -> main) feat: 실수한 커밋"),
               ("o", f"{H4} (origin/main) docs: README 추가")])
write("s16-oops", o, "실수로 커밋을 하나 만든 상황이에요. 아직 push하지 않았으니 이 커밋은 내 저장소에만 있어요.", hot=['lr', 'rm'], lines=T)

o = frame("s17-reset", "실습 17 · 되돌리기 (push 전)", "push 전이면 reset으로 커밋을 취소해요", transition="fade")
o.append(file_card("wd-hello", "wd", 0, "hello.md", "Modified · oops 남음", "red"))
o.append(file_card("wd-readme", "wd", 1, "README.md", "Committed · 변경 없음", "gray"))
o += commits("lr", [(H5, True, False, True), (H4, False), (H3, False), (H2, False), (H1, False)], "lc")
o += commits("rm", [(H4, False), (H3, False), (H2, False), (H1, False)], "rc")
o.append(tag("lt-main", "lr", 1, 0, "main", "main"))
o.append(tag("lt-origin", "lr", 1, 1, "origin/main", "origin"))
o.append(tag("rt-main", "rm", 0, 0, "main", "rmain"))
o.append(arrow("wd-st", "left", top=CARD_TOP + 42, color="#A33131"))
o.append(arrow("st-lr", "left", top=CARD_TOP + 42, color="#A33131"))
o.append(pop("lr", below(5), "main이 한 칸 내려왔어요", color="#A33131"))
o += terminal(T := [("$", "git reset HEAD~1"), ("o", "Unstaged changes after reset:"), ("o", "M\thello.md"),
               ("$", "git log --oneline"), ("o", f"{H4} (HEAD -> main, origin/main) docs: README 추가"),
               ("o", f"{H3} feat: 끝인사 추가"), ("#", "# HEAD~1 = 지금보다 한 칸 아래 커밋")])
write("s17-reset", o, "reset은 main 이름표를 예전 커밋으로 옮겨서 그 위 커밋을 기록에서 빼요. 옵션 없이 쓰면 --mixed라서, 커밋했던 변경은 작업 폴더에 Modified로 남아요. 다시 고쳐서 커밋하면 돼요.", hot=['wd', 'lr'], lines=T)

o = frame("s18-revert", "실습 18 · 만약 push까지 했다면?", "push 한 커밋은 revert로 되돌려요", transition="fade")
o += WD2
o += commits("lr", [(H6, False), (H5, False), (H4, False), (H3, False), (H2, False)], "lc")
o += commits("rm", [(H6, False), (H5, False), (H4, False), (H3, False), (H2, False)], "rc")
o.append(tag("lt-main", "lr", 0, 0, "main", "main"))
o.append(tag("lt-origin", "lr", 0, 1, "origin/main", "origin"))
o.append(tag("rt-main", "rm", 0, 0, "main", "rmain"))
o.append(arrow("lr-rm", top=ROW0 + 5, color="#6B47D6"))
o.append(pop("lr", below(5), f"반대로 고친 {H6}을 더했어요", color="#1A7340"))
o += terminal(T := [("#", f"# {H5}(실수한 커밋)을 이미 push한 상태"), ("$", "git revert HEAD"),
               ("o", f'[main {H6}] Revert "feat: 실수한 커밋"'), ("o", " 1 file changed, 1 deletion(-)"),
               ("$", "git push origin main"), ("o", "To https://github.com/kim/hello-git.git"),
               ("o", f"   {H5}..{H6}  main -> main")])
write("s18-revert", o, "이미 GitHub에 올라간 커밋은 팀원이 받아 갔을 수 있어서 reset으로 지우면 안 돼요. revert는 실수한 커밋의 반대 내용을 담은 새 커밋을 만들어요. 기록은 그대로 남고 내용만 원래대로 돌아가요. 팀원 기록을 망치지 않아요. 맨 아래 538dd06은 공간 때문에 생략했어요.", hot=['lr', 'rm'], lines=T)

# ======================================================================
# Slides outside the 4-zone frame
# ======================================================================
INK, SUB, LINE = "#1D2330", "#4A5262", "#E1DED6"
BL, GR, OR, RED, PUR = "#2459C9", "#1F8A4C", "#B26A00", "#A33131", "#5A3BB8"
BG, BG2, CARD = "#F6F5F1", "#ECEAE3", "#FDFCF9"
ZC = {  # zone colours: background, border, text
    "wd": ("#FDFCF9", "#9AA0AB", "#3A4150"), "st": ("#F1FAF4", "#4DB57A", "#1A7340"),
    "lr": ("#F0F5FE", "#5B8DEF", "#1E3F8F"), "rm": ("#F6F2FE", "#9A7BF0", "#5A3BB8"),
}


def sec(i, bg=BG, transition="fade"):
    return f'<section id="{i}" data-transition="{transition}" style="background:{bg};color:{INK};font-family:{SANS};padding:96px;display:flex;flex-direction:column;word-break:keep-all">'


def head(eyebrow, title, color=BL):
    o = []
    if eyebrow:
        o.append(p(f"position:absolute;left:96px;top:56px;width:1728px;font-size:28px;font-weight:700;color:{color}", e(eyebrow), ' id="eyebrow"'))
    o.append(f'<h2 id="title" style="position:absolute;left:96px;top:{100 if eyebrow else 72}px;width:1728px;font-size:58px;font-weight:700;line-height:1.2;color:{INK}">{title}</h2>')
    return o


def bx(x, y, w, h, inner, style="", attrs=""):
    return f'<div{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;{style}">{inner}</div>'


def icon(name, size, color, extra=""):
    return f'<x-icon name="{name}" style="width:{size}px;height:{size}px;color:{color}{extra}"></x-icon>'


def arrow_svg(x1, y1, x2, y2, color, order=None, dashed=False, width=5, kind=None):
    """A straight arrow. It is drawn like a pen stroke on its click (dashed arrows fade in instead)."""
    ang = math.atan2(y2 - y1, x2 - x1)
    a1 = (x2 - 22 * math.cos(ang - 0.5), y2 - 22 * math.sin(ang - 0.5))
    a2 = (x2 - 22 * math.cos(ang + 0.5), y2 - 22 * math.sin(ang + 0.5))
    k = kind or ("fade" if dashed else "draw")
    b = f' data-build-in="{k} order {order}"' if order else ""
    dash = ' stroke-dasharray="16 12"' if dashed else ""
    return (f'<svg{b} viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible">'
            f'<g fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round">'
            f'<path d="M{x1},{y1} L{x2},{y2}"{dash}/><path d="M{a1[0]:.0f},{a1[1]:.0f} L{x2},{y2} L{a2[0]:.0f},{a2[1]:.0f}"/></g></svg>')


def bi(kind, order):
    return f' data-build-in="{kind} order {order}"'


def tline(kind, text, size, lh, attrs=""):
    t = e(text).replace("\t", "&#160;" * 8)
    lead = len(t) - len(t.lstrip(" "))
    t = "&#160;" * lead + t.lstrip(" ") if t.strip() else "&#160;"
    if kind == "$":
        t = "$ " + t
    bold = "font-weight:700;" if kind == "$" else ""
    return p(f"font-size:{size}px;line-height:{lh}px;height:{lh}px;white-space:pre;{bold}color:{TERM_COLORS[kind]}", t, attrs)


def term(lines, x, y, w, h, size=28, lh=None, build=None, pad=(28, 36), tid=None):
    """Dark terminal box with fixed line height, so rings and labels can be placed by line number.
    Line k (from 0) sits at y + pad[0] + k * lh."""
    lh = lh or round(size * 1.55)
    o = [f'<div{f" id={chr(34)}{tid}{chr(34)}" if tid else ""} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:#1B2029;border-radius:20px;padding:{pad[0]}px {pad[1]}px;display:flex;flex-direction:column;font-family:{MONO};font-variant-ligatures:none">']
    cur, prev = (build or 1) - 1, None
    for kind, text in lines:
        at = ""
        if build is not None:
            if kind == "$":
                cur += 1
                at = f' data-build-in="fade order {cur}"'
            else:
                if prev == "$":
                    cur += 1
                at = bi("fade", cur) if cur >= build else ""
        prev = kind
        o.append(tline(kind, text, size, lh, at))
    o.append('</div>')
    term.last = cur
    return o


def mono(text, size, color=INK, weight=700, extra=""):
    return p(f"font-family:{MONO};font-size:{size}px;font-weight:{weight};color:{color};font-variant-ligatures:none{extra}", text)


def chip(text, size, fg, bg, bd=None, extra=""):
    b = f"border:2px solid {bd};" if bd else ""
    return p(f"font-family:{MONO};font-size:{size}px;font-weight:700;color:{fg};background:{bg};{b}padding:6px 18px;border-radius:12px;white-space:nowrap{extra}", text)


def zone_chip(k, label, icon_name, size=32, w=None):
    bg, bd, tc = ZC[k]
    wd = f"width:{w}px;" if w else ""
    return (f'<div style="{wd}display:flex;flex-direction:row;align-items:center;gap:14px;background:{bg};border-radius:16px;padding:16px 24px">'
            + icon(icon_name, size + 4, tc) + p(f"font-size:{size}px;font-weight:700;color:{tc};white-space:nowrap", label) + '</div>')


def table(x, y, cols, header, rows, row_h=96, head_h=64, size=32, rid=None):
    """cols: widths; rows: list of cells (html). Cell styles come from a (text, style) tuple or plain text."""
    o = [f'<div style="position:absolute;left:{x}px;top:{y}px;width:{sum(cols)}px;height:{head_h}px;background:#1D2330;border-radius:14px 14px 0 0;display:flex;flex-direction:row;align-items:center">']
    for w, hcell in zip(cols, header):
        o.append(p(f"width:{w}px;padding:0 28px;font-size:26px;font-weight:700;color:#FFFFFF", hcell))
    o.append('</div>')
    for i, r in enumerate(rows):
        bg = "#FFFFFF" if i % 2 == 0 else CARD
        last = ";border-radius:0 0 14px 14px" if i == len(rows) - 1 else ""
        idat = f' id="{rid}{i}"' if rid else ""
        o.append(f'<div{idat} style="position:absolute;left:{x}px;top:{y + head_h + i * row_h}px;width:{sum(cols)}px;height:{row_h}px;background:{bg};border-bottom:2px solid {LINE};display:flex;flex-direction:row;align-items:center{last}">')
        for w, c in zip(cols, r):
            text, st = c if isinstance(c, tuple) else (c, "")
            o.append(p(f"width:{w}px;padding:0 28px;font-size:{size}px;line-height:1.3;color:{INK};{st}", text))
        o.append('</div>')
    return o


def W(name, parts, notes):
    body = "\n".join(parts) + f"\n<aside>{e(notes)}</aside>\n</section>\n"
    with open(os.path.join(OUT, name + ".html"), "w") as f:
        f.write(body)


# ---------- 1. cover ----------
c = [sec("cover", bg="#1D2330")]
c.append(p("position:absolute;left:120px;top:176px;width:1680px;font-size:30px;font-weight:700;color:#8FB4FF", "KANT AX/AI 엔지니어 트랙 · 보충 학습 자료"))
c.append(f'<h1 style="position:absolute;left:120px;top:236px;width:1680px;font-size:128px;font-weight:900;line-height:1.12;color:#FFFFFF">Git 기본 흐름,<br>눈으로 보기</h1>')
c.append(p("position:absolute;left:120px;top:548px;width:1680px;font-size:42px;line-height:1.5;color:#C9D1DE", "add, commit, push, pull 할 때<br>내 파일은 어디로 갈까요?"))
c.append('<div style="position:absolute;left:120px;top:800px;width:1680px;display:flex;flex-direction:row;align-items:center;gap:22px">')
for i, (k, t, ic) in enumerate([("wd", "작업 폴더", "Code"), ("st", "대기실", "CheckCircle"), ("lr", "내 저장소", "Database"), ("rm", "원격 저장소 (GitHub)", "Cloud")]):
    if i:
        c.append(p("font-size:40px;color:#7D8798", "→"))
    c.append(zone_chip(k, t, ic, size=30))
c.append('</div>')
W("cover", c, "오늘은 명령을 칠 때마다 파일이 네 칸 중 어디로 가는지 눈으로 따라가 봐요. 아래 네 칸이 이 자료 전체에 계속 나오는 지도예요.")

# ---------- 2. toc ----------
TOC = [("1", "#3A4150", "Lightbulb", "개념 잡기", "4개의 공간<br>파일 상태와 용어", "3–8쪽"),
       ("2", GR, "Book", "혼자 기록하기", "init, add, commit<br>커밋 메시지 규칙", "9–18쪽"),
       ("3", BL, "Link", "GitHub과 연결", "remote add<br>push", "19–23쪽"),
       ("4", PUR, "Users", "함께 작업하기", "clone, fetch, pull", "24–28쪽"),
       ("5", OR, "Clock", "되돌리기", "reset, revert<br>reflog", "29–35쪽"),
       ("6", RED, "Wrench", "막힐 때", "status 읽기<br>자주 나는 에러", "36–43쪽")]
t = [sec("toc")] + head("", "오늘의 순서")
t.append(f'<div style="position:absolute;left:96px;top:196px;width:1728px;height:2px;background:{INK}"></div>')
for i, (n, col, ic, ttl, sub, pg) in enumerate(TOC):
    y = 198 + i * 118
    t.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:118px;border-bottom:2px solid {LINE};display:flex;flex-direction:row;align-items:center;gap:32px;padding:0 8px">'
             + p(f"width:56px;font-size:56px;font-weight:900;color:{col}", n)
             + p(f"width:400px;font-size:40px;font-weight:700;color:{INK}", ttl)
             + p(f"flex:1;font-size:32px;color:{SUB}", sub.replace("<br>", ", "))
             + p(f"font-size:30px;font-weight:700;color:{col}", pg) + '</div>')
t.append(p(f"position:absolute;left:96px;top:944px;width:1728px;font-size:32px;color:{SUB}", "44쪽은 한 장 요약이에요. 2부부터 4부까지는 hello-git 저장소 하나로 이어서 실습해요."))
W("toc", t, "왼쪽에서 오른쪽으로 진행해요. 2~4부는 같은 hello-git 저장소 하나로 이어지는 실습이에요.")

# ---------- 3. why ----------
w = [sec("why")] + head("왜 Git을 쓸까요?", "파일은 하나로 두고, 기록을 쌓아요")
w.append(p(f"position:absolute;left:96px;top:250px;width:560px;font-size:34px;font-weight:700;color:{RED}", "Git 없이"))
for i, n in enumerate(["보고서_최종.docx", "보고서_최종_수정.docx", "보고서_진짜최종.docx", "보고서_진짜최종_v3.docx"]):
    w.append(p(f"position:absolute;left:96px;top:{330 + i * 112}px;width:560px;height:84px;line-height:84px;padding:0 24px;font-family:{MONO};font-size:28px;color:#4A5262;background:#ECEAE3;border-radius:12px", n))
w.append(p(f"position:absolute;left:96px;top:{330 + 4 * 112 + 20}px;width:560px;font-size:32px;font-weight:700;color:{RED}", "어느 게 최신이지?"))
rows = "".join(f'<div style="display:flex;flex-direction:row;gap:28px;align-items:center;height:96px">'
               f'<x-shape kind="ellipse" style="width:36px;height:36px;flex:none;background:{BL}"></x-shape>'
               + p(f"font-size:38px;color:#1E3F8F", f'<b style="font-family:{MONO}">{h}</b>&#160; {m}') + '</div>'
               for h, m in [("e73617d", "팀장님 피드백 반영"), ("a7c21f4", "오타 수정"), ("538dd06", "첫 초안")])
w.append(f'<div{bi("rise", 1)} style="position:absolute;left:744px;top:236px;width:1080px;height:700px;background:#E8F0FD;border-radius:24px;padding:48px 56px;display:flex;flex-direction:column;justify-content:center;gap:28px">'
         + p(f"font-size:34px;font-weight:700;color:#1E3F8F", "Git과 함께")
         + p(f"font-family:{MONO};font-size:38px;font-weight:700;color:{INK};background:#FFFFFF;padding:20px 28px;border-radius:14px", "보고서.docx")
         + f'<div style="position:relative;display:flex;flex-direction:column"><div style="position:absolute;left:16px;top:48px;width:4px;height:192px;background:#A9C0F0"></div>{rows}</div>'
         + '<div style="height:20px"></div>' + p(f"font-size:36px;font-weight:700;color:#1E3F8F", "원하는 시점으로 돌아갈 수 있어요") + '</div>')
W("why", w, "파일명에 최종, 진짜최종을 붙여 본 경험을 먼저 물어보세요. Git은 파일을 여러 개 만드는 대신 한 파일의 변화 기록을 쌓아 둬요. 그 기록 하나가 커밋이고, 앞의 7자리는 커밋마다 붙는 고유 번호(해시)예요. 원하는 시점으로 언제든 돌아갈 수 있어요.")

# ---------- 4. map ----------
m = [sec("map")] + head("", "Git에는 4개의 공간이 있어요")
MZ = [("wd", 96, 340, "Code", "① 작업 폴더", "내가 고치는 파일"), ("st", 468, 340, "CheckCircle", "② 대기실", "커밋할 것만 골라 둠"),
      ("lr", 840, 476, "Database", "③ 내 저장소", "커밋이 쌓이는 곳"), ("rm", 1348, 476, "Cloud", "④ 원격 저장소", "GitHub, 팀과 공유")]
m.append(icon("Home", 28, "#6A7180", ";position:absolute;left:96px;top:192px"))
m.append(p("position:absolute;left:132px;top:188px;width:600px;font-size:26px;font-weight:700;color:#6A7180", "내 컴퓨터"))
m.append(f'<div style="position:absolute;left:96px;top:230px;width:1220px;height:2px;background:#CDD0D6"></div>')
m.append(icon("Globe", 28, PUR, ";position:absolute;left:1348px;top:192px"))
m.append(p(f"position:absolute;left:1384px;top:188px;width:400px;font-size:26px;font-weight:700;color:{PUR}", "인터넷"))
m.append(f'<div style="position:absolute;left:1348px;top:230px;width:476px;height:2px;background:#C9BCF2"></div>')
MBG = {"wd": "#FFFFFF", "st": "#E9F6EE", "lr": "#E8F0FD", "rm": "#F0EBFD"}
for k, x, wd, ic, t1, t2 in MZ:
    tc = ZC[k][2]
    m.append(f'<div id="m-{k}" style="position:absolute;left:{x}px;top:250px;width:{wd}px;height:400px;background:{MBG[k]};border-radius:22px;padding:28px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:20px">'
             + icon(ic, 112, tc) + p(f"font-size:40px;font-weight:700;color:{tc}", t1) + p(f"font-size:30px;color:{tc}", t2) + '</div>')
m.append(p("position:absolute;left:468px;top:666px;width:848px;font-size:26px;font-weight:700;text-align:center;color:#6A7180", "②와 ③은 숨김 폴더 .git 안에 있어요"))
cx = {k: x + wd // 2 for k, x, wd, *_ in MZ}
for i, (a, b, col, lbl) in enumerate([("wd", "st", GR, "add"), ("st", "lr", BL, "commit"), ("lr", "rm", PUR, "push origin main")], 1):
    m.append(arrow_svg(cx[a] + 20, 806, cx[b] - 20, 806, col, order=i))
    m.append(p(f"position:absolute;left:{(cx[a] + cx[b]) // 2 - 220}px;top:744px;width:440px;font-family:{MONO};font-size:32px;font-weight:700;text-align:center;color:{col}", lbl, bi("fade", i)))
m.append(arrow_svg(cx["rm"], 880, cx["wd"], 880, PUR, order=4, dashed=True))
m.append(p(f"position:absolute;left:660px;top:904px;width:600px;font-family:{MONO};font-size:32px;font-weight:700;text-align:center;color:{PUR}", "pull origin main", bi("fade", 4)))
W("map", m, "네 칸을 왼쪽부터 소개해요. 1~3번은 내 컴퓨터 안, 4번만 인터넷에 있어요. 대기실과 내 저장소는 .git 숨김 폴더 안에 있어서 눈에 안 보여요. 그래서 헷갈려요. 클릭할 때마다 화살표 이름이 하나씩 나타나요.")

# ---------- 5. analogy ----------
an = [sec("analogy", bg=BG2)] + head("택배로 비유하면", "택배를 보내는 순서와 같아요")
AN = [("add", GR, "CheckCircle", "상자에 담기"), ("commit", BL, "Lock", "봉하고<br>송장 붙이기"), ("remote add", PUR, "Link", "받는 주소<br>등록"),
      ("push", PUR, "PaperPlane", "발송"), ("pull", PUR, "Home", "도착한 택배<br>받아서 풀기")]
AW = 1728 // 5
an.append(f'<div style="position:absolute;left:{96 + AW // 2}px;top:388px;width:{AW * 4}px;height:4px;background:#C9CCD3"></div>')
for i, (cmd, col, ic, desc) in enumerate(AN):
    x = 96 + i * AW
    an.append(f'<div{bi("rise", i + 1)} style="position:absolute;left:{x}px;top:290px;width:{AW}px;display:flex;flex-direction:column;align-items:center;gap:30px">'
              + f'<div style="width:200px;height:200px;border-radius:50%;background:#FFFFFF;display:flex;align-items:center;justify-content:center">' + icon(ic, 88, col) + '</div>'
              + mono(cmd, 40, col) + p(f"font-size:34px;line-height:1.45;text-align:center;color:{INK}", desc) + '</div>')
an.append(f'<div{bi("fade", 6)} style="position:absolute;left:96px;top:800px;width:1728px;height:140px;background:#FFFFFF;border-radius:22px;display:flex;flex-direction:row;align-items:center;justify-content:center;gap:120px">'
          + "".join(p(f"font-size:38px;font-weight:700;color:{INK}", f'<span style="color:{BL}">{a}</span> = {b}') for a, b in [("커밋 메시지", "송장"), ("커밋 해시", "운송장 번호")]) + '</div>')
W("analogy", an, "담기(add)와 봉하기(commit)를 나누는 이유는, 여러 파일을 고쳤어도 이번 기록에 넣을 것만 골라 담을 수 있게 하려는 거예요. 송장에 무엇을 보냈는지 적듯 커밋 메시지에 무엇을 했는지 적고, 운송장 번호로 택배를 찾듯 커밋 해시로 커밋을 찾아요.")

# ---------- 6. terms ----------
tm = [sec("terms")] + head("용어 ① 파일의 상태", "git status 글씨 색으로 상태를 알아요")
tm += table(96, 236, [380, 560, 788], ["상태", "뜻", "git status에 보이는 말"],
            [[("Untracked", f"font-weight:700;color:{RED}"), "처음 보는 새 파일", (e("Untracked files:"), f"font-family:{MONO};font-size:28px;color:{RED}")],
             [("Modified", f"font-weight:700;color:{RED}"), "고쳤지만 add 전", (e("Changes not staged for commit:"), f"font-family:{MONO};font-size:28px;color:{RED}")],
             [("Staged", f"font-weight:700;color:{GR}"), "대기실에 올라감", (e("Changes to be committed:"), f"font-family:{MONO};font-size:28px;color:{GR}")],
             [("Committed", "font-weight:700"), "마지막 커밋과 같음", (e("working tree clean"), f"font-family:{MONO};font-size:28px")]],
            row_h=124, rid="tm-r")
for i in range(4):
    tm.append(spot(i + 1, target=f"tm-r{i}", pad=6, r=12, dim=0.5))
tm.append(spot_off(5))
tm.append(p(f"position:absolute;left:96px;top:900px;width:1728px;font-size:40px;font-weight:700;color:{INK}",
            f'<span style="color:{RED}">빨간 글씨</span>는 대기실 밖, <span style="color:{GR}">초록 글씨</span>는 대기실 안이에요.', bi("rise", 5)))
W("terms", tm, "Untracked와 Modified는 둘 다 빨간색이지만 달라요. Untracked는 Git이 처음 보는 파일, Modified는 이미 아는 파일이 바뀐 거예요. 둘 다 git add로 대기실에 올려요. 한 번이라도 커밋된 파일을 Tracked(추적 중)라고 불러요.")

# ---------- 7. terms2 ----------
t2 = [sec("terms2")] + head("용어 ② 저장소와 이름표", "origin은 명령어가 아니라 주소의 별명이에요")
T2 = [("Repository", "커밋 기록 보관함 (.git, GitHub)"), ("Index", "대기실의 정식 이름"), ("Commit, 해시", "저장된 한 시점과 그 고유 번호"),
      ("branch (브랜치)", "커밋에 붙이는 이름표. 03에서 자세히 봐요"), ("main", "기본 브랜치. 최신 커밋에 붙은 이름표"), ("HEAD", "내가 지금 서 있는 곳"),
      ("origin", "GitHub 주소의 별명"), ("origin/main", "내 컴퓨터가 기억하는 GitHub main 위치")]
t2 += table(96, 220, [480, 1248], ["용어", "한 줄 뜻"],
            [[(e(a), f"font-family:{MONO};font-size:30px;font-weight:700"), e(b)] for a, b in T2], row_h=88, head_h=60, size=32, rid="t2-r")
t2.append(spot(1, 96, 220 + 60 + 6 * 88, 1728, 2 * 88, pad=4, r=12, dim=0.5))
t2.append(spot_off(2))
W("terms2", t2, "origin/main은 마지막으로 push하거나 fetch한 시점의 GitHub 모습이라, 최신 상태를 보려면 git fetch origin으로 다시 확인해요. index는 뒤에서 나올 index.lock 에러의 그 index예요.")

# ---------- 8. lifecycle ----------
lc = [sec("lifecycle")] + head("", "파일 하나의 한살이")
LB = {"u": (96, 260, "Untracked", "새 파일", RED, "#FBE4E2", "#E07A7A"), "s": (740, 260, "Staged", "대기실에 올라감", GR, "#DDF2E5", "#4DB57A"),
      "c": (1384, 260, "Committed", "마지막 커밋과 같음", "#3A4150", "#EEEFF2", "#B4B9C3"), "m": (1384, 740, "Modified", "커밋한 뒤 고침", RED, "#FBE4E2", "#E07A7A")}
LO = {"u": None, "s": 1, "c": 2, "m": 3}
for k, (x, y, t1, t2_, fg, bg, bd) in LB.items():
    b = bi("rise", LO[k]) if LO[k] else ""
    lc.append(f'<div id="lc-{k}"{b} style="position:absolute;left:{x}px;top:{y}px;width:440px;height:200px;background:{bg};border-radius:22px;padding:28px 36px;display:flex;flex-direction:column;justify-content:center;gap:10px">'
              + p(f"font-size:46px;font-weight:700;color:{fg}", t1) + p(f"font-size:30px;color:{SUB}", t2_) + '</div>')
lc.append(arrow_svg(552, 360, 724, 360, GR, order=1))
lc.append(mono("add", 32, GR, extra=";position:absolute;left:548px;top:296px;width:180px;text-align:center").replace("<p", "<p" + bi("fade", 1), 1))
lc.append(arrow_svg(1196, 360, 1368, 360, BL, order=2))
lc.append(mono("commit", 32, BL, extra=";position:absolute;left:1192px;top:296px;width:180px;text-align:center").replace("<p", "<p" + bi("fade", 2), 1))
lc.append(arrow_svg(1604, 476, 1604, 724, RED, order=3))
lc.append(p(f"position:absolute;left:1630px;top:580px;width:200px;font-size:30px;font-weight:700;color:{RED}", "파일 수정", bi("fade", 3)))
lc.append(arrow_svg(1368, 820, 1000, 476, GR, order=4, dashed=True))
lc.append(mono("add (다시)", 32, GR, extra=";position:absolute;left:900px;top:660px;width:260px;text-align:center").replace("<p", "<p" + bi("fade", 4), 1))
lc.append(p(f"position:absolute;left:96px;top:760px;width:700px;font-size:34px;line-height:1.5;color:{SUB}", "고치고, add, commit.<br>파일은 이 고리를 계속 돌아요.", bi("fade", 4)))
W("lifecycle", lc, "새 파일은 Untracked로 시작해요. add 하면 Staged, commit 하면 Committed. 책에 따라 Committed를 Unmodified라고 부르기도 하지만, git status에는 어느 단어도 나오지 않고 working tree clean으로만 보여요. 그 뒤로 파일을 고치면 Modified가 되고 다시 add, commit을 반복해요. 이 고리가 Git 작업의 기본 리듬이에요.")

# ---------- 9. s0-config ----------
cf = [sec("s0-config")] + head("실습 0 · 컴퓨터마다 처음 한 번만", "Git에게 내 이름을 알려 줘요")
CFL = [("$", 'git config --global user.name "홍길동"'), ("$", 'git config --global user.email "gildong@example.com"'),
       ("$", "git config --global init.defaultBranch main"), ("o", ""), ("$", "git config --global --list"),
       ("o", "user.name=홍길동"), ("o", "user.email=gildong@example.com"), ("o", "init.defaultbranch=main")]
cf += term(CFL, 96, 236, 1728, 660, size=32, lh=70, build=None, pad=(40, 44))
for i, lbl in enumerate(["커밋마다 붙는 작성자 이름", "GitHub 가입 메일과 같게", "기본 브랜치 이름을 main으로"]):
    y = 236 + 40 + i * 70 + 4
    cf.append(p(f"position:absolute;left:1236px;top:{y + 6}px;width:560px;height:50px;line-height:50px;font-size:28px;font-weight:700;color:#C9D1DE", "← " + lbl, bi("fade", i + 1)))
cf.append(p(f"position:absolute;left:96px;top:936px;width:1728px;font-size:32px;color:{SUB}", "<b style=\"color:#1D2330\">--global</b>은 이 컴퓨터 전체에 적용돼요. 그래서 한 번만 하면 돼요."))
W("s0-config", cf, "설정은 컴퓨터마다 한 번만 하면 돼요. 안 하면 첫 커밋 때 \"Author identity unknown *** Please tell me who you are.\" 에러가 나요. init.defaultBranch main을 해 두면 git init으로 만든 저장소의 브랜치 이름이 GitHub과 같은 main이 돼요. GitHub의 main 기본값은 GitHub에서 만든 저장소에만 적용돼요. 이 설정이 없으면 git init이 master 브랜치를 만들 수 있고, 그러면 git push origin main에서 \"src refspec main does not match any\" 에러가 나요.")

# ---------- 17. commit-why ----------
cw = [sec("commit-why", bg=BG2)] + head("커밋 메시지 ① · 방금 쓴 feat: 는 뭘까?", "한 달 뒤, 어느 쪽 기록을 읽고 싶나요?")
LH = 62
BAD = [("9f1c2aa", "수정"), ("4b7e0d1", "ㅇㅇ"), ("c21a9f3", "asdf"), ("7d0e5b2", "최종"), ("1a2b3c4", "진짜최종")]
GOOD = [("9f1c2aa", "fix", "#F28B82", "로그인 버튼이 안 눌리는 문제 수정"), ("4b7e0d1", "feat", "#7FD18B", "회원가입 이메일 인증 추가"),
        ("c21a9f3", "docs", "#8FB4FF", "README에 설치 방법 추가"), ("7d0e5b2", "style", "#C9A7FF", "들여쓰기 정리"), ("1a2b3c4", "refactor", "#F2C46D", "로그인 함수 분리")]


def logbox(x, w, title, tcol, bd, rows, attrs=""):
    o = [f'<div{attrs} style="position:absolute;left:{x}px;top:236px;width:{w}px;height:500px;background:#1B2029;border-radius:20px;padding:30px 36px;font-family:{MONO};font-variant-ligatures:none">']
    o.append(p(f"font-family:{SANS};font-size:28px;font-weight:700;line-height:{LH}px;color:{tcol}", title))
    o.append(p(f"font-size:28px;font-weight:700;line-height:{LH}px;color:#F2C46D", "$ git log --oneline"))
    o += [p(f"font-size:28px;line-height:{LH}px;white-space:nowrap;color:#D8DEE9", r) for r in rows]
    o.append('</div>')
    return o


cw += logbox(96, 620, "아무렇게나", "#F28B82", "#E07A7A", [f"{h} {m}" for h, m in BAD])
cw += logbox(748, 1076, "규칙대로", "#7FD18B", "#4DB57A", [f'{h} <span style="color:{c}">{t}</span>: {m}' for h, t, c, m in GOOD], bi("rise", 1))
# hash 7 chars + space at 28px mono = 8 * 16.8 px
cw.append(spot(2, round(748 + 36 + 8 * 16.8 - 8), 236 + 30 + 2 * LH, round(9 * 16.8 + 16), 5 * LH, pad=6, r=10, dim=0.55))
cw.append(spot_off(3))
cw.append('<div style="position:absolute;left:96px;top:790px;width:1728px;height:136px;display:flex;flex-direction:row;align-items:center;justify-content:space-between;padding:0 24px">')
for ic, txt in [("Search", "무엇이 바뀌었는지 바로 보여요"), ("Users", "팀원이 리뷰하기 쉬워요"), ("Clock", "문제 생긴 시점을 찾기 쉬워요")]:
    cw.append('<div style="display:flex;flex-direction:row;align-items:center;gap:16px">' + icon(ic, 44, BL) + p(f"font-size:32px;font-weight:700;color:{INK}", txt) + '</div>')
cw.append('</div>')
W("commit-why", cw, "방금 두 번 커밋하면서 메시지 앞에 feat: 를 붙였죠. 그게 무슨 뜻인지 여기서 짚고 넘어가요. 오른쪽에서 동그라미 친 칸이 타입이에요. 커밋 메시지는 미래의 나와 팀원에게 남기는 송장이에요. 버그가 생겼을 때 fix 커밋만 훑어보거나, 어떤 기능이 언제 들어왔는지 feat 커밋으로 바로 찾을 수 있어요.")

# ---------- 18. commit-convention ----------
cc = [sec("commit-convention", bg=BG2)] + head("커밋 메시지 ②", "타입, 콜론과 공백, 요약 순서로 써요")
CX = 96 + 56
cc.append(f'<div style="position:absolute;left:96px;top:236px;width:1728px;height:150px;background:#1B2029;border-radius:22px;padding:0 56px;display:flex;align-items:center">'
          + p(f"font-family:{MONO};font-size:64px;font-weight:700;white-space:nowrap;color:#FFFFFF;font-variant-ligatures:none", '<span style="color:#7FD18B">feat</span><span style="color:#F2C46D">: </span>회원가입 이메일 인증 추가') + '</div>')
CH = 64 * 0.6
for x0, x1, lbl, col, lx in [(CX, CX + 4 * CH, "타입", GR, CX), (CX + 4 * CH, CX + 6 * CH, "콜론과 공백", OR, CX + 4 * CH - 30), (CX + 6 * CH + 10, CX + 6 * CH + 760, "무엇을 했는지", BL, CX + 6 * CH + 300)]:
    cc.append(underline(1, round(x0 + 4), round(x1 - 4), 408, col))
    cc.append(p(f"position:absolute;left:{round(lx)}px;top:{470 if lbl == '콜론과 공백' else 424}px;width:300px;font-size:30px;font-weight:700;color:{col}", lbl, bi("fade", 1)))
TY = [("feat", GR, "새 기능"), ("fix", RED, "버그 수정"), ("docs", BL, "문서 (README 등)"), ("style", PUR, "모양만 정리"),
      ("refactor", OR, "동작은 같게, 구조 개선"), ("test", "#3A4150", "테스트 코드"), ("chore", "#6A7180", "설정, 패키지")]
for i, (ty, col, desc) in enumerate(TY):
    x, y = 96 + (i // 4) * 888, 560 + (i % 4) * 104
    cc.append(f'<div{bi("rise", 2)} style="position:absolute;left:{x}px;top:{y}px;width:840px;height:104px;border-bottom:2px solid #D9D6CD;display:flex;flex-direction:row;align-items:center;gap:24px">'
              + mono(ty, 38, col, extra=";width:220px") + p(f"font-size:32px;color:{INK}", desc) + '</div>')
cc.append(p(f"position:absolute;left:984px;top:{560 + 3 * 104}px;width:840px;height:104px;line-height:104px;font-size:34px;font-weight:700;color:{INK}", "한 커밋에 한 가지 일, 요약은 짧게", bi("rise", 2)))
W("commit-convention", cc, "Conventional Commits라는 널리 쓰는 규칙을 바탕으로 했어요. 요약은 50자 안쪽으로, 무엇을 했는지 끝까지 읽지 않아도 알 수 있게 써요. 팀이나 회사에 정한 규칙이 있으면 그걸 먼저 따라요. 앞에서 쓴 feat: 인사 파일 추가, feat: 인사말 추가가 바로 이 형식이에요. 다음 GitHub 실습부터는 docs: 도 나와요.")

# ---------- 19. s8-github ----------
gh = [sec("s8-github")] + head("실습 8 · GitHub과 연결하기", "GitHub에 빈 저장소를 만들어요")
GX, GY = 96, 228
gh.append(f'<div style="position:absolute;left:{GX}px;top:{GY}px;width:1728px;height:740px;background:#FFFFFF;border:2px solid #D0D7DE;border-radius:18px;overflow:hidden">'
          f'<div style="height:56px;background:#F6F8FA;border-bottom:2px solid #D0D7DE;display:flex;align-items:center;gap:12px;padding:0 24px">'
          + "".join(f'<x-shape kind="ellipse" style="width:16px;height:16px;background:{c}"></x-shape>' for c in ["#E5534B", "#E3B341", "#57AB5A"])
          + p("font-family:" + MONO + ";font-size:22px;color:#57606A;margin-left:24px", "github.com/new") + '</div></div>')
F0 = GX + 64
gh.append(p(f"position:absolute;left:{F0}px;top:{GY + 92}px;width:900px;font-size:40px;font-weight:700;color:#1F2328", "Create a new repository"))
gh.append(p(f"position:absolute;left:{F0}px;top:{GY + 176}px;width:900px;font-size:26px;font-weight:700;color:#1F2328", "Repository name *"))
gh.append(f'<div style="position:absolute;left:{F0}px;top:{GY + 222}px;width:260px;height:64px;border:2px solid #D0D7DE;border-radius:10px;background:#F6F8FA;padding:0 18px;display:flex;align-items:center">' + p("font-size:28px;color:#1F2328", "kim") + '</div>')
gh.append(p(f"position:absolute;left:{F0 + 276}px;top:{GY + 228}px;width:30px;font-size:34px;color:#57606A", "/"))
gh.append(f'<div id="gh-name" style="position:absolute;left:{F0 + 312}px;top:{GY + 222}px;width:460px;height:64px;border:2px solid #0969DA;border-radius:10px;padding:0 18px;display:flex;align-items:center">' + p("font-size:30px;font-weight:700;color:#1F2328", "hello-git") + '</div>')
gh.append(f'<div style="position:absolute;left:{F0}px;top:{GY + 360}px;width:820px;display:flex;flex-direction:row;gap:18px;align-items:center">'
          '<x-shape kind="ellipse" style="width:28px;height:28px;background:#FFFFFF;border:8px solid #0969DA"></x-shape>' + p("font-size:28px;color:#1F2328", "Public") + '</div>')
gh.append(f'<div id="gh-readme" style="position:absolute;left:{F0}px;top:{GY + 470}px;width:520px;height:60px;display:flex;flex-direction:row;gap:18px;align-items:center">'
          '<div style="width:30px;height:30px;border:3px solid #57606A;border-radius:6px;background:#FFFFFF"></div>' + p("font-size:28px;color:#1F2328", "Add a README file") + '</div>')
gh.append(p(f"position:absolute;left:{F0}px;top:{GY + 600}px;width:330px;height:68px;line-height:68px;text-align:center;font-size:28px;font-weight:700;color:#FFFFFF;background:#1F883D;border-radius:10px", "Create repository", ' id="gh-create"'))
for i, (y, txt) in enumerate([(GY + 236, "① 이름은 hello-git"), (GY + 482, "② README는 체크하지 않아요"), (GY + 614, "③ 만들기")]):
    gh.append(p(f"position:absolute;left:{F0 + 800 if i == 0 else F0 + 330 if i == 1 else F0 + 370}px;top:{y}px;width:420px;font-size:28px;font-weight:700;color:{OR}", txt, bi("fade", i + 1)))
QX = GX + 1080
gh.append(f'<div{bi("rise", 4)} style="position:absolute;left:{QX}px;top:{GY + 360}px;width:600px;height:308px;background:#DDF4FF;border:2px solid #54AEFF;border-radius:14px;padding:28px 30px;display:flex;flex-direction:column;gap:18px">'
          + p("font-size:28px;font-weight:700;color:#1F2328", "Quick setup")
          + '<div style="display:flex;flex-direction:row;gap:10px">' + p("font-size:24px;font-weight:700;color:#FFFFFF;background:#0969DA;padding:4px 16px;border-radius:8px", "HTTPS") + p("font-size:24px;color:#57606A;padding:4px 16px", "SSH") + '</div>'
          + f'<div style="display:flex;flex-direction:row;align-items:center;gap:14px;background:#FFFFFF;border:2px solid #D0D7DE;border-radius:10px;padding:12px 16px">'
          + p(f"font-family:{MONO};font-size:22px;color:#1F2328;white-space:nowrap", "https://github.com/kim/hello-git.git") + '<div id="gh-copy">' + icon("Archive", 28, "#57606A") + '</div></div>'
          + p(f"font-size:26px;font-weight:700;color:{OR}", "④ 주소를 복사해 다음 장에서 써요") + '</div>')
gh += [cursor(1, 880, 482), cursor(2, 178, 728, click=False), cursor(3, 462, 850), cursor(4, target="gh-copy"), cursor_off(5)]
W("s8-github", gh, "github.com에 로그인하고 오른쪽 위 + 버튼에서 New repository를 눌러요. 이름만 hello-git으로 적고 README는 체크하지 않아요. README를 체크하면 GitHub에 커밋이 하나 생겨서, 내 컴퓨터의 커밋과 서로 모르는 기록이 돼요. 그러면 첫 push가 거절돼요(42쪽). GitHub 화면이 바뀌어 README가 토글로 보이면 꺼진(Off) 채로 둬요. 만든 뒤 나오는 Quick setup에서 HTTPS 주소를 복사해요. 화면은 간단히 다시 그린 모습이라 실제와 조금 달라요.")

# ---------- 27. pull-concept ----------
pc = [sec("pull-concept", bg=BG2)] + head("개념 정리", "pull은 fetch와 merge를 한 번에 해요")
PB = [(96, "GitHub의 main", PUR, "#F6F2FE", "solid #9A7BF0", "Cloud"), (740, "origin/main", PUR, "#F6F2FE", "dashed #9A7BF0", "Globe"), (1384, "내 main + 파일", "#1E3F8F", "#F0F5FE", "solid #5B8DEF", "Database")]
for x, t1, col, bg, bd, ic in PB:
    pc.append(f'<div style="position:absolute;left:{x}px;top:248px;width:440px;height:260px;background:{bg};border:{'3px dashed #9A7BF0' if 'dashed' in bd else 'none'};border-radius:22px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:22px">'
              + icon(ic, 80, col) + mono(e(t1), 34, col) + '</div>')
for i, (x1, x2, num, cmd, sub, col) in enumerate([(536, 740, "①", "git fetch origin", "받아만 와요", PUR), (1180, 1384, "②", "git merge origin/main", "내 것과 합쳐요", BL)], 1):
    pc.append(arrow_svg(x1 + 14, 378, x2 - 14, 378, col, order=i))
    cxm = (x1 + x2) // 2
    pc.append(f'<div{bi("fade", i)} style="position:absolute;left:{cxm - 310}px;top:548px;width:620px;display:flex;flex-direction:column;align-items:center;gap:8px">'
              + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:{col}", f"{num} {cmd}") + p(f"font-size:30px;color:{SUB}", sub) + '</div>')
pc.append(f'<div{bi("rise", 3)} style="position:absolute;left:96px;top:760px;width:1728px;height:168px;background:#1D2330;border-radius:22px;display:flex;flex-direction:row;align-items:center;justify-content:center;gap:36px">'
          + mono("git pull origin main", 48, "#F2C46D") + p("font-size:44px;color:#9AA3B5", "=") + p("font-size:44px;font-weight:700;color:#FFFFFF", "① + ② 한 번에") + '</div>')
W("pull-concept", pc, "pull을 두 단계로 나눠 보여주세요. fetch는 GitHub 소식을 받아 origin/main만 옮기고 내 파일은 건드리지 않아요. merge가 그걸 내 main과 작업 폴더에 합쳐요. 여기서는 \"받아서 합친다\"까지만 기억하면 돼요. merge가 어떻게 합치는지, 충돌(CONFLICT)이 나면 어떻게 푸는지는 03 브랜치 자료에서 봐요.")

# ---------- 28. clone-vs-init ----------
ci = [sec("clone-vs-init", bg=BG2)] + head("init과 clone", "GitHub에 저장소가 있으면 clone, 없으면 init")
CV = [(96, "GitHub에 아직 없으면", "#1E3F8F", "#DCE7FB", "Home", ["git init", "git remote add origin 주소"], ""),
      (1008, "GitHub에 이미 있으면", PUR, "#ECE5FC", "Cloud", ["git clone 주소", "cd 폴더이름"], bi("rise", 1))]
for x, ttl, col, fill, ic, steps, at in CV:
    ci.append(f'<div{at} style="position:absolute;left:{x}px;top:236px;width:816px;display:flex;flex-direction:column;gap:18px">'
              + '<div style="display:flex;flex-direction:row;gap:16px;align-items:center;margin-bottom:6px">' + icon(ic, 44, col) + p(f"font-size:38px;font-weight:700;color:{col}", ttl) + '</div>'
              + "".join(p(f"font-family:{MONO};font-size:36px;font-weight:700;height:96px;line-height:96px;padding:0 32px;border-radius:16px;color:{INK};background:{fill}", e(s_)) for s_ in steps) + '</div>')
ci.append(arrow_svg(504, 560, 820, 676, "#1E3F8F", order=2))
ci.append(arrow_svg(1416, 560, 1100, 676, PUR, order=2))
ci.append(f'<div{bi("rise", 2)} style="position:absolute;left:96px;top:700px;width:1728px;height:200px;background:#1D2330;border-radius:22px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px">'
          + p("font-size:32px;font-weight:700;color:#C9D1DE", "시작한 뒤에는 똑같아요")
          + mono("add → commit → git push origin main", 44, "#F2C46D") + '</div>')
W("clone-vs-init", ci, "판단 기준은 하나예요. GitHub에 저장소가 이미 있나? 있으면 clone, 없으면 init. 과제 템플릿이나 팀 프로젝트는 대부분 clone이에요. 왼쪽에서 remote add는 commit 뒤에 해도 돼요(실습에서는 커밋 두 개 뒤에 했어요). clone한 폴더에서 init이나 remote add를 또 하면 error: remote origin already exists. 가 나요.")

# ---------- 29. undo-map ----------
um = [sec("undo-map")] + head("되돌리기", "커밋을 되돌릴 땐 push 했는지부터 봐요", RED)
um.append(p(f"position:absolute;left:560px;top:256px;width:800px;height:108px;line-height:108px;text-align:center;font-size:42px;font-weight:700;color:#FFFFFF;background:#1D2330;border-radius:50px", "이 커밋, push 했나요?"))
um.append(arrow_svg(760, 384, 520, 530, "#1E3F8F", order=1))
um.append(arrow_svg(1160, 384, 1400, 530, PUR, order=2))
for i, (x, col, fill, ans, cmd, l1, l2) in enumerate([(96, "#1E3F8F", "#DCE7FB", "아니요 · 내 저장소에만 있어요", "git reset HEAD~1", "커밋을 없던 일로 해요", "잘못 지웠다면 git reflog로 다시 찾아요"),
                                                     (1008, PUR, "#ECE5FC", "네 · GitHub에도 올라갔어요", "git revert 커밋", "반대로 고친 커밋을 더해요", "팀원 기록은 그대로 둬요")], 1):
    um.append(f'<div{bi("rise", i)} style="position:absolute;left:{x}px;top:560px;width:816px;display:flex;flex-direction:column;gap:28px">'
              + p(f"font-size:38px;font-weight:700;color:{col}", ans)
              + p(f"font-family:{MONO};font-size:56px;font-weight:700;color:{INK};background:{fill};padding:40px 40px;border-radius:18px", cmd)
              + p(f"font-size:36px;font-weight:700;color:{INK};margin-top:8px", l1) + p(f"font-size:32px;color:{SUB}", l2) + '</div>')
W("undo-map", um, "이번 파트는 커밋한 뒤의 실수만 다뤄요. 기준은 하나, push 했는지예요. 나만 가진 커밋은 reset으로 없던 일로 만들고, 이미 GitHub에 올린 커밋은 revert로 반대 커밋을 하나 더 쌓아요. 이어지는 실습에서 둘을 그림으로 봐요.")

# ---------- 32. reset-modes ----------
rm_ = [sec("reset-modes")] + head("되돌리기 · reset 옵션 3가지", "커밋한 변경은 어디로 갈까요?", RED)
KEEP = ("변경이 여기 남음", f"font-weight:700;color:{GR};background:#DDF2E5;border-radius:12px;margin:0 12px;padding:18px 16px;text-align:center")
CANCEL = ("커밋 취소", f"color:{RED};text-align:center")
EMPTY = ("비움", f"color:{SUB};text-align:center")
SAME = ("그대로", f"color:{SUB};text-align:center")
GONE = ("변경이 사라짐", "font-weight:700;color:#FFFFFF;background:#A33131;border-radius:12px;margin:0 12px;padding:18px 16px;text-align:center")
rm_ += table(96, 236, [372, 452, 452, 452], ["옵션", "③ 내 저장소", "② 대기실", "① 작업 폴더"],
             [[(f'<span style="font-family:{MONO};font-weight:700">--soft</span>', ""), CANCEL, KEEP, SAME],
              [(f'<span style="font-family:{MONO};font-weight:700">--mixed</span><br><span style="font-size:26px;color:{SUB}">옵션 없이 쓰면 이것</span>', ""), CANCEL, EMPTY, KEEP],
              [(f'<span style="font-family:{MONO};font-weight:700;color:{RED}">--hard</span>', ""), CANCEL, EMPTY, GONE]],
             row_h=170, head_h=72, size=32, rid="rm-r")
for i in range(3):
    rm_.append(spot(i + 1, target=f"rm-r{i}", pad=6, r=12, dim=0.5))
rm_.append(spot_off(4))
rm_.append(p(f"position:absolute;left:96px;top:880px;width:1728px;font-size:34px;font-weight:700;color:{INK}", "처음엔 옵션 없이 git reset HEAD~1만 써요.", bi("fade", 4)))
W("reset-modes", rm_, "세 옵션 모두 main 이름표를 뒤로 옮겨 커밋을 취소해요. 차이는 그 커밋에 들어 있던 변경을 어디에 남기느냐예요. --soft는 대기실에, 기본값 --mixed는 작업 폴더에 남기고, --hard는 지워 버려요. --hard는 되돌리기 어려우니 처음엔 기본값만 쓰게 하세요.")

# ---------- 33. reflog ----------
rf = [sec("reflog")] + head("되돌리기 · 지운 커밋 다시 찾기", "reset으로 지운 커밋, git reflog로 찾아요", RED)
LX, LY = 96, 236
rf.append(f'<div style="position:absolute;left:{LX}px;top:{LY}px;width:560px;height:560px;background:#E8F0FD;border-radius:22px;padding:30px 36px">'
          + '<div style="display:flex;flex-direction:row;gap:12px;align-items:center">' + icon("Database", 36, "#1E3F8F") + p("font-size:32px;font-weight:700;color:#1E3F8F", "③ 내 저장소") + '</div></div>')
RY0, RP = LY + 130, 104
rf.append(f'<div style="position:absolute;left:{LX + 50}px;top:{RY0 + RP + 22}px;width:5px;height:{2 * RP}px;background:#A9C0F0"></div>')
for i, h in enumerate(["b81d4e2", "e73617d", "3f9a2c1", "a7c21f4"]):
    faded = i == 0
    dot = f"background:#F0F5FE;border:4px dashed #6A7180" if faded else f"background:{BL};border:4px solid {BL}"
    rf.append(f'<div id="rf-c{i}" style="position:absolute;left:{LX + 36}px;top:{RY0 + i * RP}px;width:480px;height:52px;display:flex;flex-direction:row;gap:20px;align-items:center;{"opacity:0.45" if faded else ""}">'
              f'<x-shape kind="ellipse" style="width:34px;height:34px;{dot}"></x-shape>' + mono(h, 32, "#1E3F8F") + '</div>')
rf.append(p(f"position:absolute;left:{LX + 280}px;top:{RY0 + 6}px;width:240px;font-size:26px;color:{SUB}", "log엔 안 보여요", ' id="rf-hidden"'))
rf.append(chip("main", 28, "#FFFFFF", BL, extra=f";position:absolute;left:{LX + 260}px;top:{RY0 + RP + 4}px", ).replace("<p", '<p id="rf-main0"', 1))
# order 3: the commit comes back and main moves up
rf.append(f'<div{bi("fade", 2)} style="position:absolute;left:{LX + 20}px;top:{RY0 - 14}px;width:520px;height:80px;background:#FFFFFF;border:3px solid {GR};border-radius:16px;display:flex;flex-direction:row;gap:20px;align-items:center;padding:0 16px">'
          f'<x-shape kind="ellipse" style="width:34px;height:34px;background:{BL}"></x-shape>' + mono("b81d4e2", 32, "#1E3F8F") + chip("main", 28, "#FFFFFF", BL) + p(f"font-size:26px;font-weight:700;color:{GR}", "다시 찾음") + '</div>')
rf.append(f'<div{bi("fade", 2)} style="position:absolute;left:{LX + 250}px;top:{RY0 + RP - 4}px;width:120px;height:60px;background:#E8F0FD"></div>')
RL = [("$", "git reflog"), ("o", "e73617d HEAD@{0}: reset: moving to HEAD~1"), ("o", "b81d4e2 HEAD@{1}: commit: feat: 실수한 커밋"),
      ("o", "e73617d HEAD@{2}: pull origin main: Fast-forward"), ("o", "3f9a2c1 HEAD@{3}: commit: feat: 끝인사 추가")]
rf += term(RL, 696, LY, 1128, 340, size=27, lh=50, build=None, pad=(32, 36))
rf.append(box(1, 696 + 36 - 8, LY + 32 + 2 * 50 + 2, 17 * 16.2 + 16, 46, OR, width=4))
RL2 = [("$", "git reset --hard b81d4e2"), ("o", "HEAD is now at b81d4e2 feat: 실수한 커밋")]
rf += [f'<div{bi("fade", 2)}>'] + term(RL2, 696, LY + 376, 1128, 168, size=27, lh=50, build=None, pad=(32, 36)) + ["</div>"]
rf.append(p(f"position:absolute;left:696px;top:{LY + 580}px;width:1128px;font-size:30px;line-height:1.5;color:{SUB}", "HEAD가 움직인 기록이 최신순으로 남아요.<br>reflog는 내 컴퓨터에만 있고 GitHub에는 없어요.", bi("fade", 3)))
W("reflog", rf, "앞 장의 reset HEAD~1로 b81d4e2가 log에서 사라졌어요. 그래도 커밋은 바로 지워지지 않고 .git 안에 남아 있어요. reflog는 HEAD가 지나간 자리를 최신순으로 보여 주는 기록이라, reset 직전 커밋(HEAD@{1})의 해시를 찾을 수 있어요. 그 해시로 reset --hard 하면 main이 다시 그 커밋을 가리켜요. --hard는 작업 폴더의 고친 내용을 지우니, 실행 전에 git status로 남은 변경이 없는지 확인하세요. reflog 기록은 기본 90일 정도 지나면 정리돼요. clone 받은 팀원 컴퓨터에는 내 reflog가 없어요.")

# ---------- 35. reset-vs-revert ----------
rr = [sec("reset-vs-revert")] + head("되돌리기 · 정리", "reset은 지우고, revert는 덧붙여요", RED)


def dots(x, y, items):
    """items: (label, kind) kind in n (normal), x (removed), r (revert)."""
    o, cx = [], x
    for i, (lb, kd) in enumerate(items):
        if i:
            o.append(f'<div style="position:absolute;left:{cx - 44}px;top:{y + 36}px;width:36px;height:5px;background:#B9BDC6"></div>')
        if kd == "r":
            o.append(p(f"position:absolute;left:{cx}px;top:{y}px;width:150px;height:76px;line-height:76px;text-align:center;font-size:30px;font-weight:700;color:#FFFFFF;background:{GR};border-radius:38px", lb))
            cx += 150 + 52
        else:
            st = f"background:#FFFFFF;border:4px dashed #B9BDC6;color:#B9BDC6" if kd == "x" else f"background:{BL};color:#FFFFFF"
            o.append(p(f"position:absolute;left:{cx}px;top:{y}px;width:76px;height:76px;line-height:{68 if kd == 'x' else 76}px;text-align:center;font-family:{MONO};font-size:32px;font-weight:700;border-radius:50%;{st}", lb))
            cx += 76 + 52
    return o


for i, (y, ttl, col, items, main_i, l1, l2, foot) in enumerate([
        (300, "reset", BL, [("A", "n"), ("B", "n"), ("X", "x")], 1, "main을 B로 되감아요", "X는 기록에서 빠져요", "push 전, 나만 가진 커밋"),
        (660, "revert", PUR, [("A", "n"), ("B", "n"), ("X", "n"), ("X 반대", "r")], 3, "X를 지우지 않아요", "반대로 고친 커밋을 더해요", "push 후, 공유된 커밋")]):
    at = bi("rise", 2) if i else ""
    grp = [mono(ttl, 52, col, extra=f";position:absolute;left:96px;top:{y + 4}px"),
           p(f"position:absolute;left:96px;top:{y + 84}px;width:300px;font-size:28px;font-weight:700;color:{col}", foot)]
    grp += dots(420, y, items)
    mx = 420 + main_i * 128 + (38 if main_i < 3 else 75) - 44
    grp.append(chip("main", 28, "#FFFFFF", BL, extra=f";position:absolute;left:{mx}px;top:{y + 100}px"))
    grp.append(p(f"position:absolute;left:1240px;top:{y}px;width:584px;font-size:36px;font-weight:700;line-height:1.5;color:{INK}", l1))
    grp.append(p(f"position:absolute;left:1240px;top:{y + 60}px;width:584px;font-size:32px;line-height:1.5;color:{SUB}", l2))
    rr.append(f'<div{at} style="position:absolute;left:0;top:0;width:1920px;height:1080px">' + "".join(grp) + '</div>')
rr.append(f'<div style="position:absolute;left:96px;top:572px;width:1728px;height:2px;background:{LINE}"></div>')
rr.append(ring(1, 676, 300, 76, 76, RED, width=5))
rr.append(ring(3, 804, 660, 150, 76, GR, width=5))
W("reset-vs-revert", rr, "이미 push한 커밋을 reset으로 지우면 팀원의 기록과 어긋나서 push가 거절되고, 억지로 밀어 넣으면(--force) 팀원 작업이 날아갈 수 있어요. 그래서 공유된 커밋은 revert로 되돌려요.")

# ---------- 36. status-table ----------
stt = [sec("status-table")] + head("막힐 때", "막히면 git status부터 봐요", "#1E3F8F")
ST_ = [("No commits yet", INK, "커밋 0개", "add → commit"), ("Untracked files:", RED, "① 새 파일", "git add"),
       ("Changes not staged for commit:", RED, "① 고쳤지만 add 전", "git add"), ("Changes to be committed:", GR, "② 커밋 대기", "git commit"),
       ("nothing to commit, working tree clean", INK, "모두 커밋됨", "push 했는지 확인")]
stt += table(96, 220, [760, 440, 528], ["이 문장이 보이면", "지금 상태", "다음 할 일"],
             [[(e(a), f"font-family:{MONO};font-size:27px;color:{c}"), b, (e(d), f"font-family:{MONO};font-size:29px;font-weight:700")] for a, c, b, d in ST_],
             row_h=92, head_h=60, size=31, rid="st-r")
for i in range(5):
    stt.append(spot(i + 1, target=f"st-r{i}", pad=6, r=12, dim=0.5))
stt.append(spot_off(6))
stt.append(f'<div{bi("rise", 6)} style="position:absolute;left:96px;top:780px;width:1728px;height:196px;background:#1D2330;border-radius:22px;padding:28px 40px;display:flex;flex-direction:row;align-items:center;gap:40px">'
           + '<div style="flex:1;display:flex;flex-direction:column;gap:12px">' + p("font-size:30px;font-weight:700;color:#FFFFFF", "GitHub과 비교는 log로 해요")
           + p(f"font-family:{MONO};font-size:27px;color:#F2C46D", "git fetch origin → git log --oneline origin/main") + '</div>'
           + '<div style="display:flex;flex-direction:column;gap:12px">' + p("font-size:28px;color:#D8DEE9", '<b style="color:#8FB4FF">main</b>이 위 → git push origin main')
           + p("font-size:28px;color:#D8DEE9", '<b style="color:#C9A7FF">origin/main</b>이 위 → git pull origin main') + '</div></div>')
W("status-table", stt, "우리 과정은 -u를 쓰지 않아서 git status가 GitHub과 비교한 결과(ahead, behind)를 보여주지 않아요. 그래서 마지막 줄이 clean이어도 push를 안 했을 수 있어요. GitHub과의 차이는 fetch한 뒤 git log --oneline에서 main과 origin/main 이름표 위치로 확인해요.")

# ---------- 37. err-lock ----------
el = [sec("err-lock", bg=BG2)] + head("에러 1 · index.lock", "index.lock은 Git의 ‘사용 중’ 팻말이에요", RED)
EW = 500
el.append(f'<div style="position:absolute;left:96px;top:236px;width:1728px;height:420px;background:#E9F6EE;border-radius:22px"></div>')
for i, (ic, t1, t2) in enumerate([("Lock", "명령 시작", "팻말 걸기"), ("Clock", "작업 중", "다른 명령은 기다려요"), ("CheckCircle", "명령 끝", "팻말 떼기")]):
    x = 96 + i * (EW + 114)
    el.append(f'<div{bi("rise", i + 1)} style="position:absolute;left:{x}px;top:236px;width:{EW}px;height:420px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:24px">'
              + icon(ic, 96, "#1A7340") + p("font-size:40px;font-weight:700;color:#1A7340", t1) + p(f"font-size:30px;color:{SUB}", t2) + '</div>')
    if i:
        el.append(arrow_svg(x - 98, 446, x - 18, 446, "#1A7340", order=i + 1))
el.append(f'<div{bi("rise", 4)} style="position:absolute;left:96px;top:712px;width:1728px;display:flex;flex-direction:column;gap:18px">'
          + '<div style="display:flex;flex-direction:row;gap:20px;align-items:center">' + icon("Warning", 56, RED) + p(f"font-size:42px;font-weight:700;color:{RED}", "끝나기 전에 멈추면 팻말이 남아요") + '</div>'
          + "".join(p(f"font-size:34px;line-height:1.5;color:{INK};padding-left:76px", c_) for c_ in ["터미널 창을 강제로 닫았을 때", "커밋 메시지 에디터를 닫지 않았을 때", "VS Code가 같은 저장소에서 git을 실행 중일 때"]) + '</div>')
W("err-lock", el, "index는 대기실의 정식 이름이에요. add, commit, pull처럼 대기실을 고치는 명령이 일하는 동안 다른 명령이 끼어들지 못하게 Git이 스스로 잠가 둬요. 정상이라면 명령이 끝날 때 저절로 사라지고, 비정상 종료됐을 때만 남아서 에러를 내요.")

# ---------- 38. err-lock-fix ----------
ef = [sec("err-lock-fix", bg=BG2)] + head("에러 1 · index.lock", "이 메시지가 보이면 팻말만 떼요", RED)
EL = [("$", "git add hello.md"), ("r", "fatal: Unable to create '/Users/kim/hello-git/.git/index.lock': File exists."),
      ("r", "Another git process seems to be running in this repository, ...")]
ef += term(EL, 96, 236, 1728, 220, size=27, lh=48, pad=(36, 40))
_i = EL[1][1].index("File exists.")
ef.append(underline(1, round(96 + 40 + _i * 16.2), round(96 + 40 + (_i + 12) * 16.2), 236 + 36 + 2 * 48 - 4, OR))
FX = [("1", "다른 git 작업이 끝났는지 봐요", "커밋 에디터, 다른 터미널 창, VS Code", None),
      ("2", "팻말을 떼요", None, "rm .git/index.lock"),
      ("3", "아까 명령을 다시 쳐요", None, "git add hello.md")]
FW = (1728 - 2 * 48) // 3
for i, (n, t1, t2, cmd) in enumerate(FX):
    x = 96 + i * (FW + 48)
    inner = (p(f"font-size:60px;font-weight:900;line-height:1;color:{BL}", n) + p(f"font-size:36px;font-weight:700;line-height:1.35;color:{INK}", t1)
             + (p(f"font-size:30px;line-height:1.45;color:{SUB}", t2) if t2 else "")
             + (p(f"font-family:{MONO};font-size:32px;font-weight:700;color:{INK};background:#FFFFFF;padding:18px 22px;border-radius:12px", cmd) if cmd else ""))
    ef.append(f'<div{bi("rise", 2)} style="position:absolute;left:{x}px;top:512px;width:{FW}px;display:flex;flex-direction:column;gap:20px">{inner}</div>')
ef.append(p(f"position:absolute;left:{96 + FW + 48}px;top:756px;width:{FW}px;font-size:28px;color:{SUB}", "Mac 터미널, Windows Git Bash 똑같아요", bi("rise", 2)))
ef.append(p(f"position:absolute;left:96px;top:900px;width:1728px;font-size:34px;font-weight:700;color:{RED}", "지우는 건 index.lock 하나뿐이에요. index나 .git 폴더는 지우지 않아요.", bi("fade", 2)))
W("err-lock-fix", ef, "1번은 열려 있는 커밋 에디터, 다른 터미널 창, VS Code의 Git 작업을 확인하는 단계예요. 이걸 건너뛰고 지우면 실제로 돌던 작업과 부딪힐 수 있어요. 명령은 .git 폴더가 있는 저장소 맨 위에서 쳐요. 우리 과정은 Windows에서도 Git Bash를 쓰니 rm 명령이 똑같이 돼요. 메시지 원문 뒷부분은 \"다른 git이 실행 중인 것 같다, 예전에 비정상 종료됐다면 파일을 직접 지워라\"라는 뜻이에요.")

# ---------- 39. err-nothing ----------
en = [sec("err-nothing", bg=BG2)] + head("에러 2 · add 없이 commit", "commit 했는데 아무 일도 없어요", RED)
ENL = [("$", 'git commit -m "feat: 새 파일"'), ("o", "Untracked files:"), ("r", "\tnew.md"), ("o", "nothing added to commit but untracked files present"),
       ("o", ""), ("$", 'git commit -m "fix: 오타 수정"'), ("o", "Changes not staged for commit:"), ("r", "\tmodified:   hello.md"), ("o", "no changes added to commit")]
en += term(ENL, 96, 236, 1100, 700, size=27, lh=62, pad=(48, 40))
en.append(underline(1, 96 + 40, round(96 + 40 + 51 * 16.2), 236 + 48 + 3 * 62 + 50, OR))
en.append(underline(2, 96 + 40, round(96 + 40 + 26 * 16.2), 236 + 48 + 8 * 62 + 50, OR))
en.append(f'<div{bi("rise", 3)} style="position:absolute;left:1260px;top:260px;width:564px;display:flex;flex-direction:column;gap:22px">'
          + icon("CheckCircle", 64, "#1A7340") + p("font-size:40px;font-weight:700;line-height:1.35;color:#1A7340", "② 대기실이<br>비어 있어요")
          + p(f"font-size:32px;line-height:1.5;color:{INK}", "commit은 대기실에 있는 것만 기록해요.") + '</div>')
en.append(f'<div{bi("rise", 4)} style="position:absolute;left:1260px;top:640px;width:564px;display:flex;flex-direction:column;gap:16px">'
          + p(f"font-size:30px;font-weight:700;color:{SUB}", "이렇게 고쳐요")
          + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:{INK};background:#DDF2E5;padding:16px 24px;border-radius:12px", "git add 파일")
          + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:{INK};background:#DCE7FB;padding:16px 24px;border-radius:12px", 'git commit -m "..."') + '</div>')
W("err-nothing", en, "빨간 글씨가 보이면 아직 대기실 밖이라는 뜻이니 add부터 해요. 출력 끝의 (use \"git add\" to track) 같은 안내 문구는 화면 폭 때문에 줄였어요.")

# ---------- 40. err-remote ----------
er = [sec("err-remote", bg=BG2)] + head("에러 3 · origin 설정", "origin이 이미 있대요, 혹은 없대요", RED)
for i, (x, ic, ttl, err, why, fixes) in enumerate([
        (96, "Link", "두 번 등록했어요", "error: remote origin already exists.", "remote add를 두 번 쳤거나<br>clone한 폴더에서 또 등록했어요", ["git remote -v", "git remote set-url origin 새주소"]),
        (984, "Search", "등록하지 않았어요", "fatal: 'origin' does not appear<br>to be a git repository", "init으로 시작하고<br>remote add를 빠뜨렸어요", ["git remote add origin 주소", "git push origin main"])]):
    er.append(f'<div style="position:absolute;left:{x}px;top:236px;width:840px;height:720px;background:{CARD};border-radius:22px;padding:40px 44px;display:flex;flex-direction:column;gap:24px">'
              + '<div style="display:flex;flex-direction:row;gap:16px;align-items:center">' + icon(ic, 44, RED) + p(f"font-size:38px;font-weight:700;color:{INK}", ttl) + '</div>'
              + p(f"font-family:{MONO};font-size:27px;line-height:1.5;color:#F28B82;background:#1B2029;padding:24px 28px;border-radius:14px;height:136px", err)
              + p(f"font-size:30px;line-height:1.5;color:{SUB}", why)
              + '<div style="flex:1"></div>'
              + f'<div{bi("rise", i + 1)} style="display:flex;flex-direction:column;gap:14px">' + p(f"font-size:28px;font-weight:700;color:{GR}", "이렇게 고쳐요")
              + "".join(p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{INK};background:#EEEFF2;padding:16px 24px;border-radius:12px", e(f_)) for f_ in fixes) + '</div></div>')
W("err-remote", er, "어느 쪽이든 git remote -v로 지금 등록된 주소를 먼저 확인하세요. 주소를 잘못 넣었으면 set-url로 고쳐요.")

# ---------- 41. err-upstream ----------
eu = [sec("err-upstream", bg=BG2)] + head("에러 4 · 어디로 보낼지 안 적음", "git push만 쳤더니 멈춰요", RED)
EUL = [("$", "git push"), ("r", "fatal: The current branch main has no upstream branch."), ("$", "git pull"), ("r", "There is no tracking information for the current branch.")]
eu += term(EUL, 96, 236, 1728, 272, size=28, lh=50, pad=(36, 40))
_i = EUL[1][1].index("has no")
eu.append(underline(1, round(96 + 40 + _i * 16.8), round(96 + 40 + len(EUL[1][1]) * 16.8), 236 + 36 + 50 + 44, OR))
eu.append(underline(1, 96 + 40, round(96 + 40 + len(EUL[3][1]) * 16.8), 236 + 36 + 3 * 50 + 44, OR))
eu.append(p(f"position:absolute;left:96px;top:560px;width:1180px;font-size:34px;font-weight:700;color:#1A7340", "어디로, 무엇을 항상 적어요", bi("rise", 2)))
for j, cmd in enumerate(["push", "pull"]):
    y = 640 + j * 120
    eu.append(f'<div{bi("rise", 2)} style="position:absolute;left:96px;top:{y}px;width:1180px;display:flex;flex-direction:row;gap:20px;align-items:center">'
              + mono(f"git {cmd}", 52, INK) + chip("origin", 52, PUR, "#ECE5FC") + chip("main", 52, BL, "#DCE7FB") + '</div>')
for lx, lw, lt, lc_ in [(96 + 8 * 31.2 + 20, 6 * 31.2 + 36, "어디로", PUR), (96 + 14 * 31.2 + 76, 4 * 31.2 + 36, "무엇을", BL)]:
    eu.append(p(f"position:absolute;left:{round(lx)}px;top:878px;width:{round(lw)}px;text-align:center;font-size:30px;font-weight:700;color:{lc_}", lt, bi("fade", 2)))
eu.append(f'<div{bi("rise", 3)} style="position:absolute;left:1340px;top:560px;width:484px;display:flex;flex-direction:column;gap:20px">'
          + icon("Warning", 56, RED) + p(f"font-size:36px;font-weight:700;line-height:1.45;color:{RED}", "에러가 --set-upstream(-u)을 권해도 쓰지 않아요") + '</div>')
W("err-upstream", eu, "-u로 짝을 지어 두지 않았기 때문에 git push, git pull만 치면 Git이 어디로 보낼지 몰라서 멈춰요. 우리 과정에서는 -u를 쓰지 않기로 했으니, 에러 메시지가 git push --set-upstream origin main을 권해도 따르지 말고 git push origin main처럼 끝까지 적어요.")

# ---------- 42. err-rejected ----------
ej = [sec("err-rejected", bg=BG2)] + head("에러 5 · push 거절", "push 했더니 rejected가 나와요", RED)
EJL = [("$", "git push origin main"), ("r", " ! [rejected]        main -> main (fetch first)"),
       ("r", "error: failed to push some refs to 'https://github.com/kim/hello-git.git'"),
       ("h", "hint: Updates were rejected because the remote contains work that you do not"), ("h", "hint: have locally. ...")]
ej += term(EJL, 96, 236, 1728, 300, size=27, lh=46, pad=(32, 40))
_i = EJL[1][1].index("(fetch")
ej.append(box(1, round(96 + 40 + _i * 16.2) - 8, 236 + 32 + 46 + 2, round(13 * 16.2) + 16, 42, RED, width=4))
ej.append(f'<div{bi("rise", 2)} style="position:absolute;left:96px;top:576px;width:1180px;height:372px;background:#FFFFFF;border-radius:22px"></div>')
for j, (lbl, col, last, lcol) in enumerate([("③ 내 저장소", "#1E3F8F", "내 커밋", "#1E3F8F"), ("④ GitHub", PUR, "팀원 커밋", "#6B47D6")]):
    y = 636 + j * 120
    row = [p(f"font-size:34px;font-weight:700;color:{col};width:270px", lbl)]
    for k_, lb in enumerate(["A", "B"]):
        row.append(p(f"width:72px;height:72px;line-height:72px;text-align:center;border-radius:50%;font-family:{MONO};font-size:32px;font-weight:700;color:#FFFFFF;background:{BL}", lb))
        row.append('<div style="width:44px;height:5px;background:#B9BDC6"></div>')
    row.append(p(f"font-size:32px;font-weight:700;color:#FFFFFF;background:{lcol};padding:12px 28px;border-radius:36px", last))
    ej.append(f'<div{bi("rise", 2)} style="position:absolute;left:144px;top:{y}px;width:1100px;display:flex;flex-direction:row;align-items:center;gap:12px">' + "".join(row) + '</div>')
ej.append(p(f"position:absolute;left:144px;top:872px;width:1100px;font-size:32px;color:{SUB}", "서로 모르는 커밋이 하나씩 생겼어요", bi("rise", 2)))
ej.append(f'<div{bi("rise", 3)} style="position:absolute;left:1340px;top:600px;width:484px;display:flex;flex-direction:column;gap:22px">'
          + p("font-size:40px;font-weight:700;line-height:1.4;color:#1A7340", "받아서 합친 뒤<br>다시 push 해요") + p(f"font-size:30px;color:{SUB}", "다음 장에서 순서대로 봐요")
          + p(f"font-size:30px;font-weight:700;color:{RED};margin-top:24px", "--force는 쓰지 않아요") + '</div>')
W("err-rejected", ej, "Git은 팀원의 커밋을 지우지 않으려고 push를 막아요. 먼저 받아서 합친 뒤 다시 보내면 돼요. GitHub에서 README를 체크해 저장소를 만들었거나 웹에서 파일을 고친 경우 혼자 작업해도 이 에러가 나요. --force는 팀원 커밋을 지워 버려요. hint 줄은 앞부분만 옮겼어요.")

# ---------- 43. err-rejected-fix ----------
ex = [sec("err-rejected-fix", bg=BG2)] + head("에러 5 · push 거절", "pull 설정을 한 번 해 두고 받아서 합쳐요", RED)
EXL = [("$", "git pull origin main"), ("o", "From https://github.com/kim/hello-git"), ("o", " * branch            main       -> FETCH_HEAD"),
       ("h", "hint: You have divergent branches and need to specify how to reconcile them."), ("r", "fatal: Need to specify how to reconcile divergent branches."),
       ("$", "git config --global pull.rebase false"),
       ("$", "git pull origin main"), ("o", "Merge made by the 'ort' strategy."), ("o", " README.md | 1 +"),
       ("$", "git push origin main"), ("o", "   dac2ff4..71f86b2  main -> main")]
ex += term(EXL, 96, 220, 1728, 744, size=26, lh=60, build=None, pad=(36, 40))
ex.append(box(1, 96 + 40 - 10, 220 + 36 + 4 * 60 + 6, round(len(EXL[4][1]) * 15.6 + 20), 48, RED, width=4))
for ln, txt, order in [(5, "처음 한 번만 쳐요 (03에서 다시 봐요)", 2), (7, "vim이 열리면 :wq 치고 Enter", 3)]:
    y = 220 + 36 + ln * 60
    ex.append(p(f"position:absolute;left:1236px;top:{y + 5}px;width:560px;height:50px;line-height:50px;font-size:27px;font-weight:700;color:#C9D1DE", "← " + txt, bi("fade", order)))
W("err-rejected-fix", ex, "pull.rebase 설정이 없으면 내 main과 GitHub main이 갈라졌을 때 Git이 어떻게 합칠지 물으면서 fatal로 멈춰요. 멈춘 pull은 커밋도 파일도 바꾸지 않아요. hint 첫 줄에 나온 pull.rebase false가 우리가 고르는 merge예요. --global을 붙여 한 번 설정하고 같은 pull을 다시 치면 두 커밋이 합쳐진 merge 커밋이 생겨요. 이때 커밋 메시지를 적는 vim이 열리면 그대로 :wq, Enter로 닫아요. 합친 뒤에는 push가 돼요. merge 커밋 모양은 03에서 자세히 봐요. hint 줄은 앞부분만 옮겼고, 해시는 사람마다 달라요.")

# ---------- 44. cheatsheet ----------
cs = [sec("cheatsheet")] + head("", "한 장 요약")
ZW, ZG = 384, 64
ZX = [96 + i * (ZW + 64) for i in range(4)]
for x, (k, t_, ic) in zip(ZX, [("wd", "① 작업 폴더", "Code"), ("st", "② 대기실", "CheckCircle"), ("lr", "③ 내 저장소", "Database"), ("rm", "④ GitHub", "Cloud")]):
    cs.append(f'<div style="position:absolute;left:{x}px;top:196px">' + zone_chip(k, t_, ic, size=32, w=ZW) + '</div>')
for i, (col, lbl) in enumerate([(GR, "add"), (BL, "commit"), (PUR, "push origin main")]):
    a, b = ZX[i] + ZW // 2, ZX[i + 1] + ZW // 2
    cs.append(arrow_svg(a + 10, 340, b - 10, 340, col, order=None))
    cs.append(p(f"position:absolute;left:{(a + b) // 2 - 200}px;top:290px;width:400px;font-family:{MONO};font-size:28px;font-weight:700;text-align:center;color:{col}", lbl))
cs.append(arrow_svg(ZX[3] + ZW // 2, 410, ZX[0] + ZW // 2, 410, PUR, dashed=True))
cs.append(p(f"position:absolute;left:660px;top:424px;width:600px;font-family:{MONO};font-size:28px;font-weight:700;text-align:center;color:{PUR}", "pull origin main"))
CSC = [("새로 시작", "#1E3F8F", "#5B8DEF", "#FFFFFF", ["git init", "add → commit", "git remote add", "&#160;&#160;origin 주소", "git push origin main"]),
       ("GitHub에서 받기", PUR, "#9A7BF0", "#FFFFFF", ["git clone 주소", "cd 폴더이름"]),
       ("매일 반복", "#FFFFFF", "#1D2330", "#1D2330", ["git pull origin main", "(작업)", "git status", "git add 파일", 'git commit -m "..."', "git push origin main"]),
       ("되돌리기", RED, "#E07A7A", "#FFFFFF", ["git reset HEAD~1", "git revert 커밋", "git reflog"])]
for x, (ttl, col, bd, bg, cmds) in zip(ZX, CSC):
    dark = bg == "#1D2330"
    cs.append(f'<div style="position:absolute;left:{x}px;top:500px;width:{ZW}px;height:430px;background:{bg};border-radius:20px;padding:30px 30px;display:flex;flex-direction:column;gap:10px">'
              + p(f"font-size:32px;font-weight:700;color:{col};margin-bottom:8px", ttl)
              + "".join(p(f"font-family:{MONO};font-size:27px;line-height:1.5;white-space:nowrap;color:{'#F2C46D' if dark else INK}", c_) for c_ in cmds) + '</div>')
W("cheatsheet", cs, "수업 끝에 이 장을 띄워 두고, 지금 내 파일이 몇 번 칸에 있는지 학생이 직접 말해 보게 하세요. 막히면 git status, GitHub과 비교할 땐 fetch 후 git log --oneline. 이 두 가지만 기억해도 대부분 풀려요.")

print("ok")
