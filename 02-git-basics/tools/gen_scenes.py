"""Generates the practice-scene slides (shared 4-zone frame) for the Git deck."""
import html, os, sys

OUT = sys.argv[1]
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"

# zone geometry
Z = {
    "wd": dict(left=96, w=360, bg="#FDFCF9", bd="#9AA0AB", title="작업 폴더", tc="#3A4150", sc="#6A7180", icon="Code", num="①"),
    "st": dict(left=504, w=360, bg="#F1FAF4", bd="#4DB57A", title="대기실", tc="#1A7340", sc="#2D5E40", icon="CheckCircle", num="②"),
    "lr": dict(left=912, w=432, bg="#F0F5FE", bd="#5B8DEF", title="내 저장소", tc="#1E3F8F", sc="#2E4D8F", icon="Database", num="③"),
    "rm": dict(left=1392, w=432, bg="#F6F2FE", bd="#9A7BF0", title="원격 저장소", tc="#5A3BB8", sc="#5A4A8F", icon="Cloud", num="④"),
}
ZTOP, ZH = 236, 404
ROW0, PITCH = 352, 56          # commit rows
CARD_TOP, CARD_H, CARD_GAP = 344, 104, 12

FILE_STYLE = {
    "red":   ("#FBE4E2", "2px solid #E07A7A", "#A33131"),
    "green": ("#DDF2E5", "2px solid #4DB57A", "#1A7340"),
    "gray":  ("#EEEFF2", "2px solid #B4B9C3", "#3A4150"),
    "ghost": ("#F6F5F1", "2px dashed #B4B9C3", "#6A7180"),
    "new":   ("#E7DEFC", "2px solid #8E6FEA", "#4A2FA8"),
}


def e(s):
    return html.escape(s, quote=False)


def p(style, text, attrs=""):
    return f'<p{attrs} style="{style}">{text}</p>'


def frame(sec_id, eyebrow, cmd, cmd_size=52, local_label="내 컴퓨터", remote_label="GitHub", rm_dim=False,
          paths=None, transition="magic"):
    paths = paths or {}
    o = [f'<section id="{sec_id}" data-transition="{transition}" style="background:#F6F5F1;color:#1D2330;font-family:{SANS};padding:96px;display:flex;flex-direction:column">']
    o.append('<div id="bracket" style="position:absolute;left:80px;top:184px;width:1280px;height:472px;border:2px dashed #B9BDC6;border-radius:28px"></div>')
    o.append(p(f"position:absolute;left:96px;top:40px;width:1728px;font-size:24px;font-weight:700;color:#2459C9", e(eyebrow), ' id="eyebrow"'))
    o.append(p(f"position:absolute;left:96px;top:90px;width:1728px;font-family:{MONO};font-size:{cmd_size}px;font-weight:700;line-height:1.15;color:#1D2330", cmd, ' id="cmd"').replace("<p", "<h2", 1).replace("</p>", "</h2>"))
    o.append('<x-icon id="ic-local" name="Home" style="position:absolute;left:100px;top:196px;width:28px;height:28px;color:#6A7180"></x-icon>')
    o.append(p("position:absolute;left:136px;top:193px;width:600px;font-size:24px;font-weight:700;color:#6A7180", e(local_label), ' id="lbl-local"'))
    o.append('<x-icon id="ic-remote" name="Globe" style="position:absolute;left:1392px;top:196px;width:28px;height:28px;color:#5A3BB8"></x-icon>')
    o.append(p("position:absolute;left:1428px;top:193px;width:396px;font-size:24px;font-weight:700;color:#5A3BB8", e(remote_label), ' id="lbl-remote"'))
    for k, z in Z.items():
        op = ";opacity:0.4" if (k == "rm" and rm_dim) else ""
        path = paths.get(k, "")
        o.append(f'<div id="z-{k}" style="position:absolute;left:{z["left"]}px;top:{ZTOP}px;width:{z["w"]}px;height:{ZH}px;background:{z["bg"]};border:2px solid {z["bd"]};border-radius:20px;padding:18px 20px;display:flex;flex-direction:column;gap:4px{op}">')
        o.append('<div style="display:flex;flex-direction:row;gap:10px;align-items:center">')
        o.append(f'<x-icon name="{z["icon"]}" style="width:32px;height:32px;color:{z["tc"]}"></x-icon>')
        o.append(p(f"font-size:30px;font-weight:700;color:{z['tc']}", f'{z["num"]} {z["title"]}'))
        o.append('</div>')
        o.append(p(f"font-family:{MONO};font-size:24px;color:{z['sc']}", e(path) if path else "&#160;"))
        o.append('</div>')
    return o


def placeholder(k, text, top=360):
    z = Z[k]
    return p(f"position:absolute;left:{z['left']+20}px;top:{top}px;width:{z['w']-40}px;font-size:24px;color:{z['sc']}", e(text), f' id="ph-{k}"')


def file_card(cid, k, slot, name, status, style, hidden=False, at=None):
    z = Z[at or k]
    bg, bd, col = FILE_STYLE[style]
    top = CARD_TOP + slot * (CARD_H + CARD_GAP)
    op = ";opacity:0" if hidden else ""
    return (f'<div id="{cid}" style="position:absolute;left:{z["left"]+20}px;top:{top}px;width:{z["w"]-40}px;height:{CARD_H}px;background:{bg};border:{bd};border-radius:16px;padding:14px 18px;display:flex;flex-direction:column;gap:4px{op}">'
            + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:#1D2330", e(name))
            + p(f"font-size:24px;font-weight:700;color:{col}", e(status))
            + '</div>')


def flyer(cid, k, row):
    """invisible small box at a commit row, target of a card flying into a repo"""
    z = Z[k]
    return f'<div id="{cid}" style="position:absolute;left:{z["left"]+20}px;top:{ROW0 + row*PITCH - 6}px;width:150px;height:44px;background:#DDF2E5;border:2px solid #4DB57A;border-radius:12px;opacity:0"></div>'


def commits(k, rows, prefix):
    """rows: list newest-first of (hash, ghost_bool). returns rail + rows"""
    z = Z[k]
    o = []
    if not rows:
        return o
    x = z["left"] + 20
    if len(rows) > 1:
        rop = ";opacity:0" if all(len(r) > 2 and r[2] for r in rows) else ""
        o.append(f'<div id="{prefix}-rail" style="position:absolute;left:{x+9}px;top:{ROW0+18}px;width:4px;height:{(len(rows)-1)*PITCH}px;background:#A9C0F0{rop}"></div>')
    for i, (h, ghost, *rest) in enumerate(rows):
        hidden = rest[0] if rest else False
        faded = len(rest) > 1 and rest[1]
        top = ROW0 + i * PITCH
        dot_bg = "#F0F5FE" if ghost else "#2459C9"
        dot_bd = "border:3px dashed #6B47D6;" if ghost else "border:3px solid #2459C9;"
        hc = "#6B47D6" if ghost else "#1E3F8F"
        op = "opacity:0;" if hidden else ("opacity:0.3;" if faded else "")
        o.append(f'<div id="{prefix}-{h}" style="position:absolute;left:{x}px;top:{top}px;width:150px;height:36px;display:flex;flex-direction:row;gap:12px;align-items:center;{op}">'
                 f'<x-shape kind="ellipse" style="width:22px;height:22px;background:{dot_bg};{dot_bd}"></x-shape>'
                 + p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{hc}", h)
                 + '</div>')
    return o


def tag(tid, k, row, slot, text, kind):
    z = Z[k]
    left = z["left"] + 20 + 146 + (0 if slot == 0 else 72)
    styles = {
        "main": "background:#2459C9;color:#FFFFFF",
        "rmain": "background:#6B47D6;color:#FFFFFF",
        "origin": "background:#E7DEFC;color:#4A2FA8;border:2px solid #8E6FEA",
    }
    width = 64 if text == "main" else 166
    return p(f"position:absolute;left:{left}px;top:{ROW0 + row*PITCH}px;width:{width}px;font-family:{MONO};font-size:24px;font-weight:700;line-height:1.5;text-align:center;border-radius:8px;{styles[kind]}", e(text), f' id="{tid}"')


def arrow(gap, direction="right", top=420, color="#2459C9", order=None):
    lefts = {"wd-st": 460, "st-lr": 868, "lr-rm": 1348}
    b = f' data-build-in="fade{" order "+str(order) if order else ""}"'
    return f'<x-shape kind="arrow-{direction}"{b} style="position:absolute;left:{lefts[gap]}px;top:{top}px;width:40px;height:28px;background:{color}"></x-shape>'


def pop(k, top, text, color="#1E3F8F", bg="#DCE7FB", bd="#5B8DEF", width=None, left=None, order=None):
    z = Z[k]
    b = f' data-build-in="pop{" order "+str(order) if order else ""}"'
    w = width or (z["w"] - 40)
    l = left if left is not None else z["left"] + 20
    return p(f"position:absolute;left:{l}px;top:{top}px;width:{w}px;font-size:24px;font-weight:700;color:{color};background:{bg};border:2px solid {bd};padding:10px 16px;border-radius:12px", text, b)


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


def callout(icon, title, sub=None, color="#1D2330", icolor="#2459C9"):
    o = ['<div id="explain" data-build-in="rise" style="position:absolute;left:1278px;top:676px;width:546px;height:348px;background:#FFFFFF;border:2px solid #E1DED6;border-radius:20px;padding:32px;display:flex;flex-direction:column;justify-content:center;gap:16px">']
    o.append(f'<x-icon name="{icon}" style="width:56px;height:56px;color:{icolor}"></x-icon>')
    o.append(p(f"font-size:34px;font-weight:700;line-height:1.35;color:{color}", title))
    if sub:
        o.append(p("font-size:26px;line-height:1.45;color:#4A5262", sub))
    o.append('</div>')
    return o


def write(sec_id, parts, notes):
    body = "\n".join(parts) + f"\n<aside>{e(notes)}</aside>\n</section>\n"
    with open(os.path.join(OUT, f"{sec_id}.html"), "w") as f:
        f.write(body)


P_INIT = {"wd": "hello-git/", "st": ".git/index", "lr": "hello-git/.git", "rm": "(아직 없음)"}
P_GH = dict(P_INIT, rm="github.com/kim/hello-git")
RM_LBL = "GitHub · 별명 origin"

H1, H2, H3, H4 = "538dd06", "a7c21f4", "3f9a2c1", "e73617d"

# ---------- 혼자 기록하기 ----------
o = frame("s1-init", "실습 1 · 혼자 기록하기", "git init", paths=dict(P_INIT, st=".git/index", lr="hello-git/.git"), rm_dim=True)
o += [placeholder("wd", "빈 폴더"), placeholder("st", "비어 있음"), placeholder("lr", "커밋 없음"), placeholder("rm", "연결 전")]
o.append(pop("lr", 420, "새로 생김: .git 폴더"))
o += terminal([("$", "mkdir hello-git && cd hello-git"), ("$", "git init"),
               ("o", "Initialized empty Git repository in /Users/kim/hello-git/.git/"),
               ("$", "git status"), ("o", "On branch main"), ("o", ""), ("o", "No commits yet"), ("o", ""),
               ("o", 'nothing to commit (create/copy files and use "git add" to track)')])
o += callout("Database", "이 폴더를 Git이<br>지켜보기 시작", "숨김 폴더 .git = ②③의 실체")
write("s1-init", o, "git init은 저장소마다 한 번만 해요. 홈 폴더나 바탕화면에서 실행하지 않도록 주의. .git 폴더가 안 보이면 macOS Finder에서 Cmd+Shift+. 을 누르세요.")

o = frame("s2-create", "실습 2 · 혼자 기록하기", 'echo "hello" &gt; hello.md', paths=P_INIT, rm_dim=True)
o += [placeholder("st", "비어 있음"), placeholder("lr", "커밋 없음"), placeholder("rm", "연결 전")]
o.append(file_card("snap-1", "st", 0, "hello.md", "Staged · 새 파일", "green", hidden=True, at="wd"))
o.append(file_card("wd-hello", "wd", 0, "hello.md", "Untracked · 새 파일", "red"))
o += terminal([("$", 'echo "hello" > hello.md'), ("$", "git status"), ("o", "On branch main"), ("o", "No commits yet"),
               ("o", "Untracked files:"), ("h", '  (use "git add <file>..." to include in what will be committed)'),
               ("r", "\thello.md"), ("o", "nothing added to commit but untracked files present")])
o += callout("Search", "Git이 처음 보는 파일", "빨간 글씨 = 아직 기록 대상 아님", icolor="#A33131")
write("s2-create", o, "에디터에서 새 파일을 저장해도 같은 상태예요. Git은 파일을 저절로 기록하지 않아요. 마지막 줄 끝의 (use \"git add\" to track) 안내는 화면 폭 때문에 생략했어요.")

o = frame("s3-add", "실습 3 · 혼자 기록하기", "git add hello.md", paths=P_INIT, rm_dim=True)
o += [placeholder("lr", "커밋 없음"), placeholder("rm", "연결 전")]
o.append(file_card("wd-hello", "wd", 0, "hello.md", "원본은 그대로", "ghost"))
o.append(file_card("snap-1", "st", 0, "hello.md", "Staged · 새 파일", "green"))
o.append(arrow("wd-st", color="#1F8A4C"))
o += terminal([("$", "git add hello.md"), ("#", "# 아무 출력이 없으면 성공"), ("$", "git status"), ("o", "On branch main"),
               ("o", "No commits yet"), ("o", "Changes to be committed:"),
               ("h", '  (use "git rm --cached <file>..." to unstage)'), ("g", "\tnew file:   hello.md")])
o += callout("CheckCircle", "지금 모습을 찍어<br>대기실에 올림", "초록 글씨 = 커밋 준비 끝", icolor="#1A7340")
write("s3-add", o, "add는 파일을 옮기는 게 아니라 그 순간의 사진을 대기실에 올리는 것. 그래서 작업 폴더 원본은 그대로 있어요. 여러 파일을 한 번에 올릴 땐 git add . 을 써요.")

o = frame("s4-commit", "실습 4 · 혼자 기록하기", 'git commit -m "feat: 인사 파일 추가"', paths=P_INIT, rm_dim=True)
o += [placeholder("st", "비어 있음"), placeholder("rm", "연결 전")]
o.append(file_card("wd-hello", "wd", 0, "hello.md", "Committed · 변경 없음", "gray"))
o.append(flyer("snap-1", "lr", 0))
o += commits("lr", [(H1, False)], "lc")
o.append(tag("lt-main", "lr", 0, 0, "main", "main"))
o.append(arrow("st-lr"))
o += terminal([("$", 'git commit -m "feat: 인사 파일 추가"'), ("o", f"[main (root-commit) {H1}] feat: 인사 파일 추가"),
               ("o", " 1 file changed, 1 insertion(+)"), ("o", " create mode 100644 hello.md"),
               ("$", "git status"), ("o", "On branch main"), ("o", "nothing to commit, working tree clean")])
o += callout("Database", f"{H1} 번으로<br>기록 완료", "GitHub엔 아직 없음", icolor="#2459C9")
write("s4-commit", o, "메시지 앞의 feat: 는 지금은 그대로 따라 쓰고, 두 번째 커밋 뒤에 자세히 봐요. 대기실에 있던 모습이 커밋 538dd06으로 저장됐어요. 해시는 사람마다 다르게 나와요. main 이름표는 지금 가장 최신 커밋을 가리켜요. -m을 빼먹어 vim이 열리면 Esc를 누르고 :q!, Enter를 쳐서 나온 뒤 다시 실행해요.")

o = frame("s5-edit", "실습 5 · 혼자 기록하기", 'echo "world" &gt;&gt; hello.md', paths=P_INIT, rm_dim=True)
o += [placeholder("st", "비어 있음"), placeholder("rm", "연결 전")]
o.append(file_card("snap-2", "st", 0, "hello.md", "Staged · 수정", "green", hidden=True, at="wd"))
o.append(file_card("wd-hello", "wd", 0, "hello.md", "Modified · 수정됨", "red"))
o += commits("lr", [(H1, False)], "lc")
o.append(tag("lt-main", "lr", 0, 0, "main", "main"))
o += terminal([("$", 'echo "world" >> hello.md'), ("$", "git status"), ("o", "On branch main"),
               ("o", "Changes not staged for commit:"),
               ("h", '  (use "git add <file>..." to update what will be committed)'),
               ("r", "\tmodified:   hello.md"), ("o", 'no changes added to commit (use "git add" and/or "git commit -a")')])
o += callout("Search", "마지막 커밋과<br>달라진 걸 발견", "다음: git add", icolor="#A33131")
write("s5-edit", o, "Untracked는 처음 보는 파일, Modified는 이미 아는 파일이 바뀐 것. 실제 status에는 안내 문구가 한 줄 더 나오지만 여기선 뺐어요.")

o = frame("s6-mixed", "실습 6 · 헷갈림 주의", 'git add hello.md → echo "more" &gt;&gt; hello.md', cmd_size=46, paths=P_INIT, rm_dim=True)
o += [placeholder("rm", "연결 전")]
o.append(file_card("wd-hello", "wd", 0, "hello.md", "Modified · more 추가", "red"))
o.append(file_card("snap-2", "st", 0, "hello.md", "Staged · world까지", "green"))
o += commits("lr", [(H1, False)], "lc")
o.append(tag("lt-main", "lr", 0, 0, "main", "main"))
o.append(arrow("wd-st", color="#1F8A4C"))
o.append(pop("wd", 476, "같은 파일, 다른 내용", color="#A33131", bg="#FFFFFF", bd="#E07A7A", width=728))
o += terminal([("$", "git add hello.md"), ("$", 'echo "more" >> hello.md'), ("$", "git status"),
               ("o", "Changes to be committed:"), ("g", "\tmodified:   hello.md"),
               ("o", "Changes not staged for commit:"), ("r", "\tmodified:   hello.md"), ("#", "# 안내 문구(use ...)는 생략")])
o += callout("Warning", "지금 commit 하면<br>more는 빠져요", "커밋 직전에 한 번 더 add", icolor="#A33131")
write("s6-mixed", o, "초록 줄과 빨간 줄에 같은 파일이 동시에 나오는 장면. add는 그 순간의 사진이라는 걸 다시 짚어 주세요. 커밋 직전에 git status를 보고 빨간 글씨가 남아 있으면 add부터.")

o = frame("s7-commit2", "실습 7 · 혼자 기록하기", 'git add hello.md → git commit -m "feat: 인사말 추가"', cmd_size=44, paths=P_INIT, rm_dim=True)
o += [placeholder("st", "비어 있음"), placeholder("rm", "연결 전")]
o.append(file_card("wd-hello", "wd", 0, "hello.md", "Committed · 변경 없음", "gray"))
o.append(flyer("snap-2", "lr", 0))
o += commits("lr", [(H2, False), (H1, False)], "lc")
o.append(tag("lt-main", "lr", 0, 0, "main", "main"))
o.append(arrow("st-lr"))
o += terminal([("$", "git add hello.md"), ("$", 'git commit -m "feat: 인사말 추가"'),
               ("o", f"[main {H2}] feat: 인사말 추가"), ("o", " 1 file changed, 2 insertions(+)"),
               ("$", "git log --oneline"), ("o", f"{H2} (HEAD -> main) feat: 인사말 추가"), ("o", f"{H1} feat: 인사 파일 추가")])
o += callout("Activity", "커밋이 줄줄이<br>쌓여요", "main은 늘 최신 커밋을 가리켜요", icolor="#2459C9")
write("s7-commit2", o, "커밋은 점, 점을 잇는 선은 순서예요. 위가 최신. main 이름표가 새 커밋으로 옮겨 가는 걸 보여주세요. git log --oneline이 이 그림을 글자로 보여주는 명령이에요.")

# ---------- GitHub 연결 ----------
o = frame("s9-remote", "실습 9 · GitHub과 연결하기", "git remote add origin https://github.com/kim/hello-git.git", cmd_size=46, paths=P_GH, remote_label=RM_LBL)
o += [placeholder("st", "비어 있음"), placeholder("rm", "빈 저장소")]
o.append(file_card("wd-hello", "wd", 0, "hello.md", "Committed · 변경 없음", "gray"))
o += commits("lr", [(H2, False), (H1, False)], "lc")
o += commits("lr", [(H2, False, True), (H1, False, True)], "rc")
o.append(tag("lt-main", "lr", 0, 0, "main", "main"))
o.append('<x-icon name="Link" data-build-in="pop" style="position:absolute;left:1350px;top:416px;width:36px;height:36px;color:#6B47D6"></x-icon>')
o.append(pop("rm", 420, "주소에 별명 origin", color="#4A2FA8", bg="#E7DEFC", bd="#8E6FEA"))
o += terminal([("$", "git remote add origin https://github.com/kim/hello-git.git"), ("#", "# 출력 없음 = 등록 성공"),
               ("$", "git remote -v"), ("o", "origin  https://github.com/kim/hello-git.git (fetch)"),
               ("o", "origin  https://github.com/kim/hello-git.git (push)")])
o += callout("Link", "주소록에<br>등록만 했어요", "아직 보낸 건 없음", icolor="#6B47D6")
write("s9-remote", o, "전화번호부에 번호를 저장한 것과 같아요. 저장만 했지 전화를 건 건 아니에요. origin은 명령어가 아니라 주소의 별명이에요.")

o = frame("s10-push", "실습 10 · GitHub과 연결하기", "git push origin main", paths=P_GH, remote_label=RM_LBL)
o += [placeholder("st", "비어 있음")]
o.append(file_card("wd-hello", "wd", 0, "hello.md", "Committed · 변경 없음", "gray"))
o += commits("lr", [(H2, False), (H1, False)], "lc")
o += commits("rm", [(H2, False), (H1, False)], "rc")
o.append(tag("lt-main", "lr", 0, 0, "main", "main"))
o.append(tag("lt-origin", "lr", 0, 1, "origin/main", "origin"))
o.append(tag("rt-main", "rm", 0, 0, "main", "rmain"))
o.append(arrow("lr-rm", color="#6B47D6"))
o.append(pop("rm", 500, "해시가 같아요 = 같은 커밋", color="#4A2FA8", bg="#E7DEFC", bd="#8E6FEA"))
o += terminal([("$", "git push origin main"), ("o", "Enumerating objects: 6, done."),
               ("o", "Writing objects: 100% (6/6), 466 bytes | 466.00 KiB/s, done."),
               ("o", "To https://github.com/kim/hello-git.git"), ("o", " * [new branch]      main -> main"),
               ("$", "git log --oneline"), ("o", f"{H2} (HEAD -> main, origin/main) feat: 인사말 추가"),
               ("o", f"{H1} feat: 인사 파일 추가")])
o += callout("PaperPlane", "origin으로<br>main을 보냄", "push 뒤에 어디로(origin)<br>무엇을(main)", icolor="#6B47D6")
write("s10-push", o, "우리 과정에서는 -u를 쓰지 않고 매번 git push origin main처럼 어디로(origin), 무엇을(main) 둘 다 적어요. origin/main 이름표는 내 컴퓨터가 기억하는 GitHub의 main 위치예요. 처음 push 할 때 GitHub 로그인이나 토큰 입력 창이 뜰 수 있어요.")

o = frame("s11-ahead", "실습 11 · 커밋만 하고 push 안 하면?", 'git commit -m "feat: 끝인사 추가"', paths=P_GH, remote_label=RM_LBL)
o += [placeholder("st", "비어 있음")]
o.append(file_card("wd-hello", "wd", 0, "hello.md", "Committed · 변경 없음", "gray"))
o += commits("lr", [(H3, False), (H2, False), (H1, False)], "lc")
o += commits("rm", [(H2, False), (H1, False)], "rc")
o.append(f'<div id="rc-{H3}" style="position:absolute;left:932px;top:{ROW0}px;width:150px;height:36px;opacity:0"></div>')
o.append(tag("lt-main", "lr", 0, 0, "main", "main"))
o.append(tag("lt-origin", "lr", 1, 1, "origin/main", "origin"))
o.append(tag("rt-main", "rm", 0, 0, "main", "rmain"))
o.append(pop("lr", 540, "1개 앞서 있음 (안 보냄)", color="#1E3F8F"))
o += terminal([("$", "git add hello.md"), ("$", 'git commit -m "feat: 끝인사 추가"'), ("o", f"[main {H3}] feat: 끝인사 추가"),
               ("$", "git status"), ("o", "nothing to commit, working tree clean"),
               ("$", "git log --oneline"), ("o", f"{H3} (HEAD -> main) feat: 끝인사 추가"),
               ("o", f"{H2} (origin/main) feat: 인사말 추가"), ("o", f"{H1} feat: 인사 파일 추가")])
o += callout("Warning", "status는 clean,<br>그래도 GitHub엔 없음", "main이 origin/main보다 위", icolor="#A33131")
write("s11-ahead", o, "-u 없이 작업하면 git status가 GitHub과 비교해 주지 않아요. 그래서 clean이라고만 나와요. 안 보낸 커밋은 git log --oneline에서 main이 origin/main보다 위에 있는지로 확인해요.")

o = frame("s12-push2", "실습 12 · GitHub과 연결하기", "git push origin main", paths=P_GH, remote_label=RM_LBL)
o += [placeholder("st", "비어 있음")]
o.append(file_card("wd-hello", "wd", 0, "hello.md", "Committed · 변경 없음", "gray"))
o += commits("lr", [(H3, False), (H2, False), (H1, False)], "lc")
o += commits("rm", [(H3, False), (H2, False), (H1, False)], "rc")
o.append(tag("lt-main", "lr", 0, 0, "main", "main"))
o.append(tag("lt-origin", "lr", 0, 1, "origin/main", "origin"))
o.append(tag("rt-main", "rm", 0, 0, "main", "rmain"))
o.append(arrow("lr-rm", color="#6B47D6"))
o += terminal([("$", "git push origin main"), ("o", "To https://github.com/kim/hello-git.git"),
               ("o", f"   {H2}..{H3}  main -> main"), ("$", "git log --oneline"),
               ("o", f"{H3} (HEAD -> main, origin/main) feat: 끝인사 추가"), ("o", f"{H2} feat: 인사말 추가"),
               ("o", f"{H1} feat: 인사 파일 추가")])
o += callout("CheckCircle", "main = origin/main<br>이제 같아요", None, icolor="#1A7340")
write("s12-push2", o, f"두 번째 push부터는 바뀐 커밋만 보내요. {H2}..{H3}는 그 사이 커밋을 보냈다는 뜻이에요.")

# ---------- 함께 작업하기 ----------
o = frame("s13-clone", "실습 13 · 팀원 컴퓨터에서", "git clone https://github.com/kim/hello-git.git", cmd_size=48,
          local_label="팀원 컴퓨터", paths=dict(P_GH, wd="hello-git/"), remote_label="GitHub", transition="fade")
o += [placeholder("st", "비어 있음")]
o += commits("rm", [(H3, False), (H2, False), (H1, False)], "rc")
o.append(tag("rt-main", "rm", 0, 0, "main", "rmain"))
o.append(arrow("lr-rm", "left", color="#6B47D6", order=1))
lr = []
x = Z["lr"]["left"] + 20
lr.append(f'<div data-build-in="left order 2" style="position:absolute;left:{x}px;top:{ROW0}px;width:392px;height:{2*PITCH+36}px">')
lr.append(f'<div style="position:absolute;left:9px;top:18px;width:4px;height:{2*PITCH}px;background:#A9C0F0"></div>')
for i, h in enumerate([H3, H2, H1]):
    lr.append(f'<div style="position:absolute;left:0px;top:{i*PITCH}px;width:150px;height:36px;display:flex;flex-direction:row;gap:12px;align-items:center"><x-shape kind="ellipse" style="width:22px;height:22px;background:#2459C9;border:3px solid #2459C9"></x-shape><p style="font-family:{MONO};font-size:24px;font-weight:700;color:#1E3F8F">{h}</p></div>')
lr.append(f'<p style="position:absolute;left:146px;top:0px;width:64px;font-family:{MONO};font-size:24px;font-weight:700;line-height:1.5;text-align:center;border-radius:8px;background:#2459C9;color:#FFFFFF">main</p>')
lr.append(f'<p style="position:absolute;left:218px;top:0px;width:166px;font-family:{MONO};font-size:24px;font-weight:700;line-height:1.5;text-align:center;border-radius:8px;background:#E7DEFC;color:#4A2FA8;border:2px solid #8E6FEA">origin/main</p>')
lr.append('</div>')
o += lr
o.append(f'<div data-build-in="left order 3" style="position:absolute;left:116px;top:{CARD_TOP}px;width:320px;height:{CARD_H}px;background:#EEEFF2;border:2px solid #B4B9C3;border-radius:16px;padding:14px 18px;display:flex;flex-direction:column;gap:4px">'
         + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:#1D2330", "hello.md")
         + p("font-size:24px;font-weight:700;color:#3A4150", "최신 커밋 모습") + '</div>')
o.append(pop("lr", 540, "origin 등록도 자동", color="#4A2FA8", bg="#E7DEFC", bd="#8E6FEA", order=4))
o += terminal([("$", "cd ~/projects"), ("$", "git clone https://github.com/kim/hello-git.git"),
               ("o", "Cloning into 'hello-git'..."), ("o", "Receiving objects: 100% (9/9), done."),
               ("$", "cd hello-git"), ("#", "# 새로 생긴 폴더로 꼭 들어가기"), ("$", "ls"), ("o", "hello.md")])
o += callout("Users", "GitHub 저장소를<br>통째로 복사", "init + remote add + 받기를 한 번에", icolor="#6B47D6")
write("s13-clone", o, "팀원이 이 저장소에 합류하는 장면이에요. clone은 폴더 만들기, git init, remote add origin, 커밋 받기를 한 번에 해요. clone한 폴더에서 init이나 remote add를 다시 하지 않아요. 팀원은 이어서 README.md를 만들고 add → commit → push 해요(docs: README 추가).")

o = frame("s14-fetch", "실습 14 · 다시 내 컴퓨터 (팀원이 README를 push함)", "git fetch origin", paths=P_GH, remote_label=RM_LBL, transition="magic")
o += [placeholder("st", "비어 있음")]
o.append(file_card("wd-hello", "wd", 0, "hello.md", "Committed · 변경 없음", "gray"))
o.append(file_card("wd-readme", "wd", 1, "README.md", "pull로 생김", "new", hidden=True, at="lr"))
o += commits("lr", [(H4, True), (H3, False), (H2, False), (H1, False)], "lc")
o += commits("rm", [(H4, False), (H3, False), (H2, False), (H1, False)], "rc")
o.append(tag("lt-origin", "lr", 0, 1, "origin/main", "origin"))
o.append(tag("lt-main", "lr", 1, 0, "main", "main"))
o.append(tag("rt-main", "rm", 0, 0, "main", "rmain"))
o.append(arrow("lr-rm", "left", color="#6B47D6"))
o += terminal([("$", "git fetch origin"), ("o", "From https://github.com/kim/hello-git"),
               ("o", f"   {H3}..{H4}  main       -> origin/main"), ("$", "git log --oneline origin/main"),
               ("o", f"{H4} (origin/main) docs: README 추가"), ("o", f"{H3} (HEAD -> main) feat: 끝인사 추가"),
               ("o", f"{H2} feat: 인사말 추가"), ("o", f"{H1} feat: 인사 파일 추가")])
o += callout("Search", "받아만 왔어요", "origin/main만 이동<br>작업 폴더는 그대로", icolor="#6B47D6")
write("s14-fetch", o, "fetch는 GitHub의 새 소식을 받아 origin/main 이름표만 옮겨요. 내 main보다 앞선 커밋은 git log --oneline origin/main으로 봐요. 그냥 git log --oneline에는 내 main까지만 나와요. 점선 커밋은 받아 왔지만 아직 내 main에 합치지 않은 커밋이에요. 작업 폴더에는 README.md가 아직 없어요.")

o = frame("s15-pull", "실습 15 · 받아서 합치기", "git pull origin main", paths=P_GH, remote_label=RM_LBL)
o += [placeholder("st", "비어 있음")]
o.append(file_card("wd-hello", "wd", 0, "hello.md", "Committed · 변경 없음", "gray"))
o.append(file_card("wd-readme", "wd", 1, "README.md", "pull로 생김", "new"))
o += commits("lr", [(H4, False), (H3, False), (H2, False), (H1, False)], "lc")
o += commits("rm", [(H4, False), (H3, False), (H2, False), (H1, False)], "rc")
o.append(tag("lt-main", "lr", 0, 0, "main", "main"))
o.append(tag("lt-origin", "lr", 0, 1, "origin/main", "origin"))
o.append(tag("rt-main", "rm", 0, 0, "main", "rmain"))
o.append(arrow("lr-rm", "left", color="#6B47D6", order=1))
o.append(arrow("wd-st", "left", top=560, color="#2459C9", order=2))
o.append(arrow("st-lr", "left", top=560, color="#2459C9", order=2))
o += terminal([("$", "git pull origin main"), ("o", "From https://github.com/kim/hello-git"),
               ("o", " * branch            main       -> FETCH_HEAD"), ("o", f"Updating {H3}..{H4}"),
               ("o", "Fast-forward"), ("o", " README.md | 1 +"), ("o", " 1 file changed, 1 insertion(+)"),
               ("o", " create mode 100644 README.md")])
o += callout("CheckCircle", "받고 + 합치고", "main이 따라오고<br>README.md가 생김", icolor="#1A7340")
write("s15-pull", o, "pull = fetch(받기) + merge(합치기). main 이름표가 origin/main 위치로 따라 올라가고, 그 커밋의 파일이 작업 폴더에 나타나요. 습관: 작업 시작 전에 git pull origin main.")

# ---------- 되돌리기 ----------
H5, H6 = "b81d4e2", "c4e9a07"
WD2 = [file_card("wd-hello", "wd", 0, "hello.md", "Committed · 변경 없음", "gray"),
       file_card("wd-readme", "wd", 1, "README.md", "Committed · 변경 없음", "gray")]

o = frame("s16-oops", "실습 16 · 되돌리기", 'git commit -m "feat: 실수한 커밋"', paths=P_GH, remote_label=RM_LBL, transition="magic")
o += [placeholder("st", "비어 있음")] + WD2
o += commits("lr", [(H5, False), (H4, False), (H3, False), (H2, False), (H1, False)], "lc")
o += commits("rm", [(H4, False), (H3, False), (H2, False), (H1, False)], "rc")
o.append(tag("lt-main", "lr", 0, 0, "main", "main"))
o.append(tag("lt-origin", "lr", 1, 1, "origin/main", "origin"))
o.append(tag("rt-main", "rm", 0, 0, "main", "rmain"))
o += terminal([("$", 'echo "oops" >> hello.md'), ("$", "git add hello.md"), ("$", 'git commit -m "feat: 실수한 커밋"'),
               ("o", f"[main {H5}] feat: 실수한 커밋"), ("o", " 1 file changed, 1 insertion(+)"),
               ("$", "git log --oneline"), ("o", f"{H5} (HEAD -> main) feat: 실수한 커밋"),
               ("o", f"{H4} (origin/main) docs: README 추가")])
o += callout("Warning", "앗, 잘못 커밋했다", "아직 push 전이에요", icolor="#A33131")
write("s16-oops", o, "실수로 커밋을 하나 만든 상황이에요. 아직 push하지 않았으니 이 커밋은 내 저장소에만 있어요.")

o = frame("s17-reset", "실습 17 · 되돌리기 (push 전)", "git reset HEAD~1", paths=P_GH, remote_label=RM_LBL, transition="fade")
o += [placeholder("st", "비어 있음")]
o.append(file_card("wd-hello", "wd", 0, "hello.md", "Modified · oops 남음", "red"))
o.append(file_card("wd-readme", "wd", 1, "README.md", "Committed · 변경 없음", "gray"))
o += commits("lr", [(H5, True, False, True), (H4, False), (H3, False), (H2, False), (H1, False)], "lc")
o += commits("rm", [(H4, False), (H3, False), (H2, False), (H1, False)], "rc")
o.append(tag("lt-main", "lr", 1, 0, "main", "main"))
o.append(tag("lt-origin", "lr", 1, 1, "origin/main", "origin"))
o.append(tag("rt-main", "rm", 0, 0, "main", "rmain"))
o.append(arrow("wd-st", "left", top=560, color="#A33131"))
o.append(arrow("st-lr", "left", top=560, color="#A33131"))
o += terminal([("$", "git reset HEAD~1"), ("o", "Unstaged changes after reset:"), ("o", "M\thello.md"),
               ("$", "git log --oneline"), ("o", f"{H4} (HEAD -> main, origin/main) docs: README 추가"),
               ("o", f"{H3} feat: 끝인사 추가"), ("#", "# HEAD~1 = 지금보다 한 칸 아래 커밋")])
o += callout("Clock", "main을<br>한 칸 뒤로", "고친 내용은 작업 폴더에 남아요", icolor="#A33131")
write("s17-reset", o, "reset은 main 이름표를 예전 커밋으로 옮겨서 그 위 커밋을 기록에서 빼요. 옵션 없이 쓰면 --mixed라서, 커밋했던 변경은 작업 폴더에 Modified로 남아요. 다시 고쳐서 커밋하면 돼요.")

o = frame("s18-revert", "실습 18 · 만약 push까지 했다면?", "git revert HEAD → git push origin main", cmd_size=48, paths=P_GH, remote_label=RM_LBL, transition="fade")
o += [placeholder("st", "비어 있음")] + WD2
o += commits("lr", [(H6, False), (H5, False), (H4, False), (H3, False), (H2, False)], "lc")
o += commits("rm", [(H6, False), (H5, False), (H4, False), (H3, False), (H2, False)], "rc")
o.append(tag("lt-main", "lr", 0, 0, "main", "main"))
o.append(tag("lt-origin", "lr", 0, 1, "origin/main", "origin"))
o.append(tag("rt-main", "rm", 0, 0, "main", "rmain"))
o.append(arrow("lr-rm", color="#6B47D6"))
o += terminal([("#", f"# {H5}(실수한 커밋)을 이미 push한 상태"), ("$", "git revert HEAD"),
               ("o", f'[main {H6}] Revert "feat: 실수한 커밋"'), ("o", " 1 file changed, 1 deletion(-)"),
               ("$", "git push origin main"), ("o", "To https://github.com/kim/hello-git.git"),
               ("o", f"   {H5}..{H6}  main -> main")])
o += callout("Activity", "지우지 않고<br>되돌리는 커밋 추가", "팀원 기록을 망치지 않아요", icolor="#1A7340")
write("s18-revert", o, "이미 GitHub에 올라간 커밋은 팀원이 받아 갔을 수 있어서 reset으로 지우면 안 돼요. revert는 실수한 커밋의 반대 내용을 담은 새 커밋을 만들어요. 기록은 그대로 남고 내용만 원래대로 돌아가요. 맨 아래 538dd06은 공간 때문에 생략했어요.")
print("ok")
