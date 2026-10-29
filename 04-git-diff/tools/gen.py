"""Generates every slide of the git diff deck.

Diff scenes reuse the 4-zone frame of 02 (작업 폴더, 대기실, 내 저장소, 원격 저장소) and draw a bar
under the two zones a command compares. Branch pages reuse the commit graph look of 03.
Terminal output comes from tools/demo.sh (git 2.43).
Usage: python3 tools/gen.py slides
"""
import html, os, sys

OUT = sys.argv[1]
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
INK, SUB, LINE = "#1D2330", "#4A5262", "#E1DED6"
BL, BLL, GR, GRL, OR, RED, PUR = "#2459C9", "#9DB8F2", "#1F8A4C", "#9ED3B4", "#B26A00", "#A33131", "#5A3BB8"
C_WD, C_ST = "#A33131", "#1A7340"          # git diff = red side, git diff --staged = green side


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
TC = {"$": "#F2C46D", "o": "#D8DEE9", "h": "#FFFFFF", "c": "#7CC7E8", "r": "#F28B82", "g": "#7FD18B", "#": "#8C95A6"}


def kind_of(line):
    if line.startswith(("diff ", "index ", "--- ", "+++ ")):
        return "h"
    if line.startswith("@@"):
        return "c"
    if line.startswith("-"):
        return "r"
    if line.startswith(("+", " +")):
        return "g"
    return "o"


def diff_lines(text):
    return [(kind_of(l), l) for l in text.strip("\n").split("\n")]


def terminal(lines, left=96, top=636, w=1150, h=388, size=24, lh=1.25, tid="term"):
    o = [f'<div id="{tid}" style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:#1B2029;border-radius:20px;padding:20px 28px;display:flex;flex-direction:column;font-family:{MONO};font-variant-ligatures:none">']
    for kind, text in lines:
        t = e(text).replace("\t", "        ")
        if kind == "$":
            t = "$ " + t
        bold = "font-weight:700;" if kind in "h$" else ""
        o.append(p(f"font-size:{size}px;line-height:{lh};white-space:pre;{bold}color:{TC[kind]}", t if t else " "))
    o.append('</div>')
    return o


# ---------- real outputs (tools/demo.sh) ----------
DIFF1 = """diff --git a/login.md b/login.md
index ef88ce3..7d67f3e 100644
--- a/login.md
+++ b/login.md
@@ -1,3 +1,4 @@
 # 로그인
 아이디
-비밀번호
+비밀번호 (8자 이상)
+로그인 버튼"""
DIFF_MORE = """diff --git a/login.md b/login.md
index 7d67f3e..60a5971 100644
--- a/login.md
+++ b/login.md
@@ -2,3 +2,4 @@
 아이디
 비밀번호 (8자 이상)
 로그인 버튼
+아이디 저장"""
DIFF_BR = """diff --git a/login.md b/login.md
index 60a5971..14b3837 100644
--- a/login.md
+++ b/login.md
@@ -1,5 +1,6 @@
-# 로그인
+# 로그인하기
 아이디
 비밀번호 (8자 이상)
 로그인 버튼
 아이디 저장
+비밀번호 찾기"""
DIFF_BR_REV = """diff --git a/login.md b/login.md
index 14b3837..60a5971 100644
--- a/login.md
+++ b/login.md
@@ -1,6 +1,5 @@
-# 로그인하기
+# 로그인
 아이디
 비밀번호 (8자 이상)
 로그인 버튼
 아이디 저장
-비밀번호 찾기"""
DIFF_BR2 = """diff --git a/login.md b/login.md
index cea7b97..14b3837 100644
--- a/login.md
+++ b/login.md
@@ -1,5 +1,6 @@
-# 로그인 페이지
+# 로그인하기
 아이디
 비밀번호 (8자 이상)
 로그인 버튼
 아이디 저장
+비밀번호 찾기"""
DIFF_CC = """diff --cc login.md
index cea7b97,14b3837..0000000
--- a/login.md
+++ b/login.md
@@@ -1,4 -1,4 +1,8 @@@
++<<<<<<< HEAD
 +# 로그인 페이지
++=======
+ # 로그인하기
++>>>>>>> feature/login
  아이디
  비밀번호 (8자 이상)
  로그인 버튼"""
H0, H1, HB, HM, HR = "e12ffc2", "7e5303c", "acf05c1", "73080d0", "c36ee83"

# ---------- 4-zone frame ----------
Z = {
    "wd": dict(left=96, w=360, bg="#FDFCF9", bd="#9AA0AB", title="작업 폴더", tc="#3A4150", icon="Code", num="①"),
    "st": dict(left=504, w=360, bg="#F1FAF4", bd="#4DB57A", title="대기실", tc="#1A7340", icon="CheckCircle", num="②"),
    "lr": dict(left=912, w=432, bg="#F0F5FE", bd="#5B8DEF", title="내 저장소", tc="#1E3F8F", icon="Database", num="③"),
    "rm": dict(left=1392, w=432, bg="#F6F2FE", bd="#9A7BF0", title="원격 저장소", tc="#5A3BB8", icon="Cloud", num="④"),
}
ZTOP, ZH = 236, 320
ZBOT = ZTOP + ZH
CARD_TOP = 300


def zx(k):
    return Z[k]["left"] + Z[k]["w"] // 2


def frame(sid, eyebrow, cmd, transition="magic", cmd_size=52):
    o = [sec(sid, transition)]
    o.append('<div id="bracket" style="position:absolute;left:80px;top:184px;width:1280px;height:388px;border:2px dashed #B9BDC6;border-radius:28px"></div>')
    o.append(p(f"position:absolute;left:96px;top:40px;width:1728px;font-size:24px;font-weight:700;color:{BL}", e(eyebrow), ' id="eyebrow"'))
    o.append(f'<h2 id="cmd" style="position:absolute;left:96px;top:86px;width:1728px;font-family:{MONO};font-size:{cmd_size}px;font-weight:700;line-height:1.15;color:{INK}">{cmd}</h2>')
    o.append('<x-icon id="ic-local" name="Home" style="position:absolute;left:100px;top:196px;width:28px;height:28px;color:#6A7180"></x-icon>')
    o.append(p("position:absolute;left:136px;top:193px;width:600px;font-size:24px;font-weight:700;color:#6A7180", "내 컴퓨터", ' id="lbl-local"'))
    o.append('<x-icon id="ic-remote" name="Globe" style="position:absolute;left:1392px;top:196px;width:28px;height:28px;color:#5A3BB8"></x-icon>')
    o.append(p("position:absolute;left:1428px;top:193px;width:396px;font-size:24px;font-weight:700;color:#5A3BB8", "GitHub", ' id="lbl-remote"'))
    for k, z in Z.items():
        op = ";opacity:0.4" if k == "rm" else ""
        o.append(f'<div id="z-{k}" style="position:absolute;left:{z["left"]}px;top:{ZTOP}px;width:{z["w"]}px;height:{ZH}px;background:{z["bg"]};border:2px solid {z["bd"]};border-radius:20px;padding:16px 20px;display:flex;flex-direction:column{op}">'
                 '<div style="display:flex;flex-direction:row;gap:10px;align-items:center">'
                 f'<x-icon name="{z["icon"]}" style="width:32px;height:32px;color:{z["tc"]}"></x-icon>'
                 + p(f"font-size:30px;font-weight:700;color:{z['tc']}", f'{z["num"]} {z["title"]}') + '</div></div>')
    o.append(p("position:absolute;left:1412px;top:300px;width:392px;font-size:24px;color:#5A4A8F;opacity:0.6", "이번엔 쓰지 않아요", ' id="ph-rm"'))
    return o


DOC_ST = {"red": ("#FFFFFF", "#E07A7A", "#A33131"), "green": ("#FFFFFF", "#4DB57A", "#1A7340"), "gray": ("#FFFFFF", "#B4B9C3", "#3A4150")}
MARK = {"add": "background:#DDF2E5;color:#14532D", "del": "background:#FBE4E2;color:#7A1F1F", None: f"color:{INK}"}


def doc(cid, k, lines, label, style, top=CARD_TOP, marks=None, height=None):
    z = Z[k]
    bg, bd, col = DOC_ST[style]
    marks = marks or {}
    h = height or (ZBOT - 16 - top)
    o = [f'<div id="{cid}" style="position:absolute;left:{z["left"]+20}px;top:{top}px;width:{z["w"]-40}px;height:{h}px;background:{bg};border:2px solid {bd};border-radius:14px;padding:10px 14px;display:flex;flex-direction:column;gap:2px">']
    o.append(f'<div style="display:flex;flex-direction:row;justify-content:space-between;align-items:center">'
             + p(f"font-family:{MONO};font-size:20px;font-weight:700;color:{INK}", "login.md")
             + p(f"font-size:18px;font-weight:700;color:{col}", e(label)) + '</div>')
    for i, l in enumerate(lines):
        o.append(p(f"font-family:{MONO};font-size:20px;line-height:1.35;padding:0 6px;border-radius:4px;{MARK[marks.get(i)]}", e(l)))
    o.append('</div>')
    return "".join(o)


def zone_note(k, text, sub=None, top=300):
    z = Z[k]
    s = p(f"font-size:24px;font-weight:700;color:{z['tc']}", e(text))
    if sub:
        s += p("font-size:22px;line-height:1.4;color:#4A5262", sub)
    return f'<div id="note-{k}" style="position:absolute;left:{z["left"]+20}px;top:{top}px;width:{z["w"]-40}px;display:flex;flex-direction:column;gap:8px">{s}</div>'


def commit_row(k, h, top=CARD_TOP, rid="lc"):
    z = Z[k]
    x = z["left"] + 20
    return (f'<div id="{rid}-{h}" style="position:absolute;left:{x}px;top:{top}px;width:300px;height:36px;display:flex;flex-direction:row;gap:12px;align-items:center">'
            f'<x-shape kind="ellipse" style="width:22px;height:22px;background:{BL};border:3px solid {BL}"></x-shape>'
            + p(f"font-family:{MONO};font-size:24px;font-weight:700;color:#1E3F8F", h)
            + p(f"font-family:{MONO};font-size:22px;font-weight:700;line-height:1.4;padding:0 10px;border-radius:8px;background:{BL};color:#FFFFFF", "main")
            + '</div>')


def cmp_bar(a, b, label, color, bid="cmp", y=596, order=None):
    x1, x2 = zx(a), zx(b)
    attr = f' data-build-in="fade order {order}"' if order else ""
    lw = round(len(label) * 15.6 + 36)
    mid = (x1 + x2) // 2
    return (f'<div id="{bid}"{attr} style="position:absolute;left:{x1-3}px;top:{ZBOT+2}px;width:{x2-x1+6}px;height:{y-ZBOT}px;border:6px solid {color};border-top:none;border-radius:0 0 14px 14px"></div>'
            + p(f"position:absolute;left:{mid-lw//2}px;top:{y-24}px;width:{lw}px;font-family:{MONO};font-size:26px;font-weight:700;line-height:1.6;text-align:center;border-radius:10px;background:{color};color:#FFFFFF", e(label), f' id="{bid}-lbl"{attr}'))


def callout(icon, title, sub=None, icolor=BL, top=650, h=374):
    o = [f'<div id="explain" data-build-in="rise" style="position:absolute;left:1278px;top:{top}px;width:546px;height:{h}px;background:#FFFFFF;border:2px solid {LINE};border-radius:20px;padding:32px;display:flex;flex-direction:column;justify-content:center;gap:16px">']
    o.append(f'<x-icon name="{icon}" style="width:56px;height:56px;color:{icolor}"></x-icon>')
    o.append(p(f"font-size:34px;font-weight:700;line-height:1.35;color:{INK}", title))
    if sub:
        o.append(p(f"font-size:26px;line-height:1.45;color:{SUB}", sub))
    o.append('</div>')
    return o


V1 = ["# 로그인", "아이디", "비밀번호"]
V2 = ["# 로그인", "아이디", "비밀번호 (8자 이상)", "로그인 버튼"]
V3 = V2 + ["아이디 저장"]
LR1 = [commit_row("lr", H0), doc("lr-doc", "lr", V1, "마지막 커밋", "gray", top=348)]
TERM_TOP, TERM_H = 650, 374

# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:#1D2330;color:#F6F5F1;font-family:{SANS};padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#8FB3FF;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
       '<h1 style="font-size:104px;font-weight:900;line-height:1.1;color:#F6F5F1">Git diff,<br>눈으로 보기</h1>',
       '<p style="font-size:40px;line-height:1.4;color:#BFC6D4">무엇이 바뀌었는지<br>커밋 전에 확인하는 법</p>']
cov.append(f'<div style="position:absolute;left:1120px;top:330px;width:640px;height:420px;background:#252B36;border-radius:24px;padding:36px 40px;display:flex;flex-direction:column;gap:10px;font-family:{MONO}">')
for k, l in [("c", "@@ -1,3 +1,4 @@"), ("o", " # 로그인"), ("o", " 아이디"), ("r", "-비밀번호"), ("g", "+비밀번호 (8자 이상)"), ("g", "+로그인 버튼")]:
    cov.append(p(f"font-size:34px;line-height:1.4;white-space:pre;font-weight:700;color:{TC[k]}", e(l)))
cov.append('</div>')
W("cover", cov, "03 Git 브랜치에서 쓰던 hello-git 저장소와 login.md로 이어서 실습해요. 오늘은 새 명령보다 확인하는 습관을 배워요. add 전, commit 전, merge 전에 무엇이 바뀌는지 눈으로 보고 넘어가요.")

# ---------- toc ----------
parts = [("Lightbulb", "#3A4150", "diff란?", "두 칸을 비교해요", "3–4쪽"),
         ("Search", C_WD, "git diff", "add 전에 고친 줄 보기", "5–8쪽"),
         ("CheckCircle", C_ST, "git diff --staged", "커밋 전에 최종 확인", "9–12쪽"),
         ("Book", BL, "git show", "커밋 하나 들여다보기", "13쪽"),
         ("Activity", OR, "브랜치 비교", "merge 전에 미리 보기", "14–16쪽"),
         ("Warning", RED, "충돌 볼 때", "충돌 난 곳만 보기", "17–18쪽"),
         ("Lock", PUR, ".gitignore", "올리면 안 되는 파일", "19–22쪽"),
         ("Wrench", "#1E3F8F", "막힐 때", "안 나오거나 안 끝날 때", "23–24쪽")]
t = [f'<section id="toc" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};padding:96px 128px;display:flex;flex-direction:column;gap:40px">',
     f'<h2 style="font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>',
     '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:24px;flex:1">']
for i, (ic, c, h, s, pg) in enumerate(parts, 1):
    t.append(f'<div style="display:flex;flex-direction:column;gap:10px;background:#FFFFFF;border:2px solid {LINE};border-top:10px solid {c};border-radius:20px;padding:24px 28px">'
             f'<div style="display:flex;flex-direction:row;gap:14px;align-items:center"><p style="font-size:52px;font-weight:900;line-height:1.25;color:{c}">{i}</p>'
             f'<x-icon name="{ic}" style="width:40px;height:40px;color:{c}"></x-icon></div>'
             f'<h3 style="font-family:{MONO if h.startswith(("git", ".")) else SANS};font-size:32px;font-weight:700;color:{INK}">{h}</h3>'
             f'<p style="font-size:26px;line-height:1.4;color:{SUB}">{s}</p><div style="flex:1"></div>'
             f'<p style="font-size:24px;color:#6A7180">{pg}</p></div>')
t += ['</div>', f'<p style="font-size:26px;color:{SUB}">마지막 25쪽은 한 장 요약이에요.</p>']
W("toc", t, "1~3부는 02에서 본 네 칸 그림 위에서 진행해요. 5~6부는 03의 브랜치 그래프를 다시 써요. 7부 .gitignore는 status와 diff에 나오지 않게 할 파일을 정하는 법이에요.")

# ---------- why ----------
w = [sec("why")] + head("diff란?", "커밋하기 전에, 뭘 고쳤는지 기억나요?")
for i, (lab, lines, marks, bd) in enumerate([("고치기 전", V1, {2: "del"}, "#B4B9C3"), ("고친 뒤", V2, {2: "add", 3: "add"}, "#B4B9C3")]):
    x = 96 + i * 640
    w.append(f'<div style="position:absolute;left:{x}px;top:270px;width:520px;height:380px;background:#FFFFFF;border:2px solid {bd};border-radius:20px;padding:28px 32px;display:flex;flex-direction:column;gap:10px">'
             + p(f"font-size:26px;font-weight:700;color:#6A7180", lab)
             + p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{INK}", "login.md")
             + "".join(p(f"font-family:{MONO};font-size:28px;line-height:1.5;padding:0 10px;border-radius:6px;{MARK[marks.get(j)] if i == 0 or j in marks else MARK[None]}", e(l)) for j, l in enumerate(lines))
             + '</div>')
w.append(f'<x-shape kind="arrow-right" style="position:absolute;left:644px;top:436px;width:64px;height:48px;background:#9AA0AB"></x-shape>')
w.append(f'<div data-build-in="rise" style="position:absolute;left:1376px;top:270px;width:448px;height:380px;background:#1B2029;border-radius:20px;padding:28px 32px;display:flex;flex-direction:column;gap:10px;font-family:{MONO}">'
         + p("font-family:'Noto Sans KR',sans-serif;font-size:26px;font-weight:700;color:#F2C46D", "git diff가 보여 주는 것")
         + "".join(p(f"font-size:28px;line-height:1.5;white-space:pre;font-weight:700;color:{TC[k]}", e(l)) for k, l in [("o", " # 로그인"), ("o", " 아이디"), ("r", "-비밀번호"), ("g", "+비밀번호 (8자 이상)"), ("g", "+로그인 버튼")])
         + '</div>')
w.append(f'<p data-build-in="fade" style="position:absolute;left:96px;top:720px;width:1728px;font-size:36px;font-weight:700;line-height:1.4;color:{INK}">diff는 두 모습을 나란히 놓고 <span style="color:{RED}">지운 줄</span>과 <span style="color:#1A7340">넣은 줄</span>만 골라 보여 줘요.</p>')
w.append(f'<p data-build-in="fade" style="position:absolute;left:96px;top:800px;width:1728px;font-size:30px;line-height:1.4;color:{SUB}">파일이 길어도 바뀐 곳만 보면 돼요. 이름은 difference(차이)에서 왔어요.</p>')
W("why", w, "git status는 어떤 파일이 바뀌었는지만 알려 줘요. 그 파일 안에서 어느 줄이 바뀌었는지는 diff로 봐요. 커밋 메시지를 쓸 때도 diff를 보면 무엇을 했는지 바로 적을 수 있어요.")

# ---------- map ----------
m = [sec("map")] + head("diff란?", "diff는 언제나 두 칸을 비교해요")
for k, z in Z.items():
    op = ";opacity:0.4" if k == "rm" else ""
    m.append(f'<div style="position:absolute;left:{z["left"]}px;top:300px;width:{z["w"]}px;height:200px;background:{z["bg"]};border:2px solid {z["bd"]};border-radius:20px;padding:24px;display:flex;flex-direction:column;gap:14px{op}">'
             '<div style="display:flex;flex-direction:row;gap:10px;align-items:center">'
             f'<x-icon name="{z["icon"]}" style="width:36px;height:36px;color:{z["tc"]}"></x-icon>'
             + p(f"font-size:34px;font-weight:700;color:{z['tc']}", f'{z["num"]} {z["title"]}') + '</div>'
             + p(f"font-size:24px;line-height:1.4;color:#4A5262", {"wd": "지금 고치는 파일", "st": "add로 올린 모습", "lr": "commit한 기록", "rm": "이번엔 쓰지 않아요"}[k]) + '</div>')
rows = [("wd", "st", "git diff", C_WD, "add 전에: 고쳤는데 아직 안 올린 것", "status의 빨간 글씨"),
        ("st", "lr", "git diff --staged", C_ST, "commit 전에: 올려서 커밋될 것", "status의 초록 글씨")]
for i, (a, b, lab, col, desc, hint) in enumerate(rows):
    y = 520 + i * 110
    x1, x2 = zx(a), zx(b)
    m.append(f'<div data-build-in="fade order {i+1}" style="position:absolute;left:{x1-3}px;top:500px;width:{x2-x1+6}px;height:{y+40-500}px;border:6px solid {col};border-top:none;border-radius:0 0 14px 14px"></div>')
    lw = round(len(lab) * 15.6 + 36)
    m.append(p(f"position:absolute;left:{(x1+x2)//2-lw//2}px;top:{y+16}px;width:{lw}px;font-family:{MONO};font-size:26px;font-weight:700;line-height:1.6;text-align:center;border-radius:10px;background:{col};color:#FFFFFF", lab, f' data-build-in="fade order {i+1}"'))
m.append(f'<div data-build-in="rise order 3" style="position:absolute;left:96px;top:800px;width:1728px;display:flex;flex-direction:row;gap:24px">')
for lab, col, desc, hint in [("git diff", C_WD, "add 전에 고친 줄", "status의 빨간 글씨 = 여기 나와요"), ("git diff --staged", C_ST, "commit될 줄", "status의 초록 글씨 = 여기 나와요"), ("git diff main feature/login", OR, "두 브랜치의 차이", "merge 전에 미리 보기")]:
    m.append(f'<div style="flex:1;display:flex;flex-direction:column;gap:8px;background:#FFFFFF;border:2px solid {LINE};border-left:10px solid {col};border-radius:16px;padding:20px 24px">'
             + p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{col}", lab)
             + p(f"font-size:28px;font-weight:700;color:{INK}", desc)
             + p(f"font-size:22px;color:{SUB}", hint) + '</div>')
m.append('</div>')
W("map", m, "02의 네 칸 그림이에요. git diff는 ①과 ②, git diff --staged는 ②와 ③을 비교해요. status에서 빨간 글씨로 나온 파일은 git diff로, 초록 글씨로 나온 파일은 git diff --staged로 내용을 본다고 외우면 쉬워요. 브랜치 비교는 ③ 안에서 커밋 두 개를 비교하는 거예요. --staged 대신 --cached라고 써도 같아요.")

# ---------- part 2: git diff ----------
o = frame("d1", "실습 1 · git diff", "git diff")
o.append(doc("wd-doc", "wd", V2, "고침", "red", marks={2: "add", 3: "add"}))
o.append(zone_note("st", "비어 있음", "비어 있으면<br>③ 마지막 커밋과<br>비교해요"))
o += LR1
o.append(cmp_bar("wd", "st", "git diff", C_WD))
o += terminal([("$", "git diff")] + diff_lines(DIFF1), top=TERM_TOP, h=TERM_H)
o += callout("Search", "고친 줄만<br>빨강, 초록으로", "아직 add 전이에요", icolor=C_WD)
W("d1", o, "login.md에서 비밀번호 줄에 (8자 이상)을 붙이고 로그인 버튼 줄을 더했어요. 아직 add하지 않았어요. 대기실이 비어 있으면 마지막 커밋과 같은 모습이 기준이 돼요. 그래서 커밋 e12ffc2와 비교한 결과가 나와요. 출력이 길면 화면 아래에 :가 보이고 멈춰요. q를 누르면 나와요.")

# read 1
LBL = [(0, 4, "#9AA0AB", "어느 파일인지", "a/ = 예전, b/ = 지금"), (4, 5, "#7CC7E8", "몇째 줄 근처인지", "다음 장에서 자세히"),
       (5, 7, "#D8DEE9", "그대로인 줄", "앞에 빈칸, 위치 참고용"), (7, 8, "#F28B82", "- 지운 줄", "빨강"), (8, 10, "#7FD18B", "+ 넣은 줄", "초록")]
r = [sec("read-lines")] + head("출력 읽기", "- 는 지운 줄, + 는 넣은 줄")
LH = 48
r.append(f'<div style="position:absolute;left:96px;top:250px;width:960px;height:{10*LH+56}px;background:#1B2029;border-radius:20px;padding:28px 32px;display:flex;flex-direction:column;font-family:{MONO}">')
for k, l in diff_lines(DIFF1):
    r.append(p(f"font-size:28px;line-height:{LH}px;white-space:pre;font-weight:700;color:{TC[k]}", e(l)))
r.append('</div>')
for i, (a, b, col, t1, t2) in enumerate(LBL, 1):
    top = 278 + a * LH
    hh = (b - a) * LH
    r.append(f'<div data-build-in="fade order {i}" style="position:absolute;left:1096px;top:{top+4}px;width:8px;height:{hh-8}px;background:{col};border-radius:4px"></div>')
    r.append(f'<div data-build-in="fade order {i}" style="position:absolute;left:1128px;top:{top}px;width:696px;height:{hh}px;display:flex;flex-direction:row;gap:16px;align-items:center">'
             + p(f"font-size:28px;font-weight:700;color:{INK}", e(t1)) + p(f"font-size:24px;color:#6A7180", e(t2)) + '</div>')
r.append(f'<div data-build-in="rise order 6" style="position:absolute;left:96px;top:840px;width:1728px;display:flex;flex-direction:row;gap:20px;align-items:center;background:#FFFFFF;border:2px solid {LINE};border-radius:16px;padding:22px 28px">'
         f'<x-icon name="Lightbulb" style="width:40px;height:40px;color:{OR}"></x-icon>'
         + p(f"font-size:28px;font-weight:700;color:{INK}", "한 줄을 고치면 - 한 줄과 + 한 줄이 짝으로 나와요. 예전 줄을 지우고 새 줄을 넣은 걸로 보여요.") + '</div>')
W("read-lines", r, "맨 위 네 줄은 어느 파일을 비교했는지 알려 줘요. 처음엔 diff --git 줄의 파일 이름만 봐도 돼요. index 줄의 숫자는 Git이 파일 내용에 붙인 번호라서 몰라도 돼요. 터미널에서는 빼기 줄이 빨강, 더하기 줄이 초록으로 나와요. 줄 맨 앞의 기호 한 칸은 파일 내용이 아니라 diff가 붙인 표시예요.")

# read 2: @@
a = [sec("read-hunk")] + head("출력 읽기", "@@ 줄은 위치를 알려 줘요")
a.append(f'<div style="position:absolute;left:96px;top:250px;width:1728px;height:120px;background:#1B2029;border-radius:20px;display:flex;flex-direction:row;gap:28px;align-items:center;justify-content:center;font-family:{MONO}">'
         + p("font-size:56px;font-weight:700;color:#7CC7E8", "@@") + p(f"font-size:56px;font-weight:700;color:#F28B82", "-1,3")
         + p(f"font-size:56px;font-weight:700;color:#7FD18B", "+1,4") + p("font-size:56px;font-weight:700;color:#7CC7E8", "@@") + '</div>')
for i, (lab, sign, col, bd, lines, marks, desc) in enumerate([("예전 파일", "-1,3", "#A33131", "#E07A7A", V1, {2: "del"}, "1번째 줄부터 3줄"), ("지금 파일", "+1,4", "#1A7340", "#4DB57A", V2, {2: "add", 3: "add"}, "1번째 줄부터 4줄")]):
    x = 96 + i * 888
    a.append(f'<div data-build-in="rise order {i+1}" style="position:absolute;left:{x}px;top:420px;width:840px;height:400px;background:#FFFFFF;border:2px solid {bd};border-radius:20px;padding:28px 36px;display:flex;flex-direction:column;gap:12px">'
             + '<div style="display:flex;flex-direction:row;gap:20px;align-items:baseline">'
             + p(f"font-family:{MONO};font-size:40px;font-weight:700;color:{col}", sign) + p(f"font-size:30px;font-weight:700;color:{INK}", desc) + '</div>'
             + p(f"font-size:24px;color:#6A7180", lab)
             + "".join(f'<div style="display:flex;flex-direction:row;gap:20px;align-items:center">' + p(f"width:36px;font-family:{MONO};font-size:24px;color:#9AA0AB;text-align:right", str(j + 1))
                       + p(f"font-family:{MONO};font-size:28px;line-height:1.5;padding:0 10px;border-radius:6px;{MARK[marks.get(j)]}", e(l)) + '</div>' for j, l in enumerate(lines))
             + '</div>')
a.append(p(f"position:absolute;left:96px;top:870px;width:1728px;font-size:30px;line-height:1.4;color:{SUB}", "숫자는 몰라도 diff를 읽을 수 있어요. 긴 파일에서 고친 곳을 찾아갈 때 써요.", ' data-build-in="fade order 3"'))
W("read-hunk", a, "-1,3은 예전 파일의 1번째 줄부터 3줄을 보여 준다는 뜻이고, +1,4는 지금 파일의 1번째 줄부터 4줄이에요. 줄이 하나 늘어서 3이 4가 됐어요. 파일 여러 곳을 고치면 @@ 줄이 여러 번 나오고, 각각 고친 곳 하나씩이에요. 고친 줄 앞뒤로 바뀌지 않은 줄을 최대 3줄씩 같이 보여 줘서 어디쯤인지 알 수 있어요.")

o = frame("d2", "실습 2 · git diff", "git add login.md → git diff", cmd_size=48)
o.append(doc("wd-doc", "wd", V2, "올림", "gray"))
o.append(doc("st-doc", "st", V2, "Staged", "green"))
o += LR1
o.append(cmp_bar("wd", "st", "git diff", C_WD))
o += terminal([("$", "git add login.md"), ("$", "git diff"), ("#", "# 아무것도 안 나와요")], top=TERM_TOP, h=TERM_H)
o += callout("CheckCircle", "①과 ②가 같아서<br>보여 줄 게 없어요", "고친 게 사라진 게 아니에요", icolor=C_ST)
W("d2", o, "add하고 나서 git diff를 치면 아무것도 나오지 않아요. 고친 내용이 없어진 게 아니라 작업 폴더와 대기실이 같아진 거예요. 이제 커밋될 내용은 다음 장의 git diff --staged로 봐요.")

# ---------- part 3: --staged ----------
o = frame("d3", "실습 3 · git diff --staged", "git diff --staged")
o.append(doc("wd-doc", "wd", V2, "올림", "gray"))
o.append(doc("st-doc", "st", V2, "Staged", "green", marks={2: "add", 3: "add"}))
o.append(commit_row("lr", H0))
o.append(doc("lr-doc", "lr", V1, "마지막 커밋", "gray", top=348, marks={2: "del"}))
o.append(cmp_bar("st", "lr", "git diff --staged", C_ST))
o += terminal([("$", "git diff --staged")] + diff_lines(DIFF1), top=TERM_TOP, h=TERM_H)
o += callout("CheckCircle", "commit하면<br>들어갈 내용", "커밋 메시지 쓰기 전에 한 번", icolor=C_ST)
W("d3", o, "--staged는 대기실과 마지막 커밋을 비교해요. 지금 commit하면 이 내용이 그대로 커밋에 들어가요. 실습 1의 git diff와 같은 출력이 나왔어요. 고친 걸 그대로 다 올렸으니까요. --cached라고 써도 똑같이 동작해요.")

o = frame("d4a", "실습 4 · add 뒤에 또 고치면", 'echo "아이디 저장" &gt;&gt; login.md → git diff', cmd_size=44)
o.append(doc("wd-doc", "wd", V3, "또 고침", "red", marks={4: "add"}))
o.append(doc("st-doc", "st", V2, "Staged", "green"))
o += LR1
o.append(cmp_bar("wd", "st", "git diff", C_WD))
o += terminal([("$", 'echo "아이디 저장" >> login.md'), ("$", "git diff")] + diff_lines(DIFF_MORE), top=TERM_TOP, h=TERM_H)
o += callout("Search", "add 뒤에 고친<br>한 줄만 나와요", "기준이 대기실이라서", icolor=C_WD)
W("d4a", o, "add한 뒤에 한 줄을 더 고쳤어요. git diff는 대기실과 비교하니까 add 뒤에 고친 아이디 저장 한 줄만 보여 줘요. 02 실습 6에서 본 같은 파일, 다른 내용 장면을 diff로 다시 보는 거예요.")

o = frame("d4b", "실습 4 · add 뒤에 또 고치면", "git diff --staged", cmd_size=52)
o.append(doc("wd-doc", "wd", V3, "또 고침", "red"))
o.append(doc("st-doc", "st", V2, "Staged", "green", marks={2: "add", 3: "add"}))
o.append(commit_row("lr", H0))
o.append(doc("lr-doc", "lr", V1, "마지막 커밋", "gray", top=348, marks={2: "del"}))
o.append(cmp_bar("st", "lr", "git diff --staged", C_ST))
o += terminal([("$", "git diff --staged")] + diff_lines(DIFF1), top=TERM_TOP, h=TERM_H)
o += callout("Warning", "아이디 저장은<br>아직 빠져 있어요", "지금 commit하면 안 들어가요.<br>한 번 더 git add", icolor=RED)
W("d4b", o, "--staged에는 아이디 저장 줄이 없어요. 지금 commit하면 그 줄은 커밋에 들어가지 않아요. 커밋 직전에 git diff와 git diff --staged를 둘 다 보면 빠뜨린 걸 찾을 수 있어요.")

o = frame("d5", "실습 5 · 커밋하고 나면", 'git add login.md → git commit -m "feat: 로그인 화면에 안내와 버튼 추가"', cmd_size=34)
o.append(doc("wd-doc", "wd", V3, "변경 없음", "gray"))
o.append(zone_note("st", "비어 있음", "커밋하고 나면<br>다시 비어요"))
o.append(commit_row("lr", H1))
o.append(doc("lr-doc", "lr", V3, "마지막 커밋", "gray", top=348))
o.append(cmp_bar("wd", "st", "git diff", C_WD, bid="cmp", y=596))
o.append(cmp_bar("st", "lr", "git diff --staged", C_ST, bid="cmp2", y=596))
o += terminal([("$", "git add login.md"), ("$", 'git commit -m "feat: 로그인 화면에 안내와 버튼 추가"'), ("o", f"[main {H1}] feat: 로그인 화면에 안내와 버튼 추가"),
               ("o", " 1 file changed, 3 insertions(+), 1 deletion(-)"), ("$", "git diff"), ("$", "git diff --staged"), ("#", "# 둘 다 아무것도 안 나와요")], top=TERM_TOP, h=TERM_H)
o += callout("Database", "세 칸이<br>모두 같아졌어요", "커밋한 내용은 git show로", icolor=BL)
W("d5", o, "커밋 출력의 3 insertions(+), 1 deletion(-)은 diff의 + 줄 3개, - 줄 1개와 같아요. 커밋하고 나면 git diff와 git diff --staged 모두 빈 화면이에요. 방금 커밋한 내용을 다시 보고 싶으면 다음 장의 git show를 써요.")

# ---------- part 4: git show ----------
SHOW = f"""commit 7e5303ce32924d91ff86f6f48d7f1d1af808f9ae (HEAD -> main)
Author: kim <kim@example.com>
Date:   Thu Oct 29 10:02:00 2026 +0900

    feat: 로그인 화면에 안내와 버튼 추가

diff --git a/login.md b/login.md
index ef88ce3..60a5971 100644
--- a/login.md
+++ b/login.md
@@ -1,3 +1,5 @@
 # 로그인
 아이디
-비밀번호
+비밀번호 (8자 이상)
+로그인 버튼
+아이디 저장"""
s = [sec("show")] + head("git show", "커밋 하나에 무엇이 바뀌었나")
lines = [("$", "git show")] + [("o" if i < 6 else kind_of(l), l) for i, l in enumerate(SHOW.split("\n"))]
s += terminal(lines, left=96, top=240, w=1100, h=600, size=24, lh=1.3)
s.append(f'<div data-build-in="fade order 1" style="position:absolute;left:1220px;top:276px;width:8px;height:150px;background:{BL};border-radius:4px"></div>')
s.append(p(f"position:absolute;left:1248px;top:300px;width:576px;font-size:30px;font-weight:700;color:{INK}", "커밋 정보<br><span style=\"font-size:24px;font-weight:400;color:#6A7180\">번호, 만든 사람, 날짜, 메시지</span>", ' data-build-in="fade order 1"'))
s.append(f'<div data-build-in="fade order 2" style="position:absolute;left:1220px;top:470px;width:8px;height:350px;background:{GR};border-radius:4px"></div>')
s.append(p(f"position:absolute;left:1248px;top:590px;width:576px;font-size:30px;font-weight:700;color:{INK}", "바꾼 내용<br><span style=\"font-size:24px;font-weight:400;color:#6A7180\">바로 전 커밋과 비교한 diff</span>", ' data-build-in="fade order 2"'))
s.append(f'<div data-build-in="rise order 3" style="position:absolute;left:96px;top:872px;width:1728px;display:flex;flex-direction:row;gap:24px">')
for cmd, desc in [("git show", "마지막 커밋 보기"), ("git show e12ffc2", "그 번호의 커밋 보기"), ("git log --oneline", "번호 찾기")]:
    s.append(f'<div style="flex:1;display:flex;flex-direction:column;gap:6px;background:#FFFFFF;border:2px solid {LINE};border-radius:16px;padding:16px 24px">'
             + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{BL}", cmd) + p(f"font-size:24px;color:{SUB}", desc) + '</div>')
s.append('</div>')
W("show", s, "git show는 커밋 하나를 열어 봐요. 위에는 커밋 번호, 만든 사람, 날짜, 메시지가 나오고 아래에는 바로 전 커밋과 비교한 diff가 나와요. 해시 없이 쓰면 HEAD, 즉 지금 브랜치의 마지막 커밋을 보여 줘요. 다른 커밋은 git log --oneline에서 번호를 찾아 git show 번호로 봐요. 팀원이 올린 커밋이 무엇을 바꿨는지 볼 때도 써요. 출력이 길면 q로 나와요.")


# ---------- part 5: branches ----------
def node(x, y, color, r=22, kind="n", attrs=""):
    st = f"background:#FFFFFF;border:7px solid {color}" if kind == "merge" else f"background:{color};border:4px solid {color}"
    return f'<div{attrs} style="position:absolute;left:{x-r}px;top:{y-r}px;width:{2*r}px;height:{2*r}px;border-radius:50%;{st}"></div>'


def hline(x1, x2, y, color, attrs=""):
    return f'<div{attrs} style="position:absolute;left:{x1}px;top:{y-3}px;width:{x2-x1}px;height:6px;background:{color}"></div>'


def conn(x1, y1, x2, y2, color, attrs=""):
    return f'<x-connector{attrs} x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" style="color:{color};border-width:6px"></x-connector>'


def pill(x, y, text, kind="main", attrs=""):
    w = round(len(text) * 14.5 + 28)
    st = {"main": f"background:{BL};color:#FFFFFF", "green": f"background:{GR};color:#FFFFFF", "head": "background:#1D2330;color:#F6F5F1"}[kind]
    return f'<p{attrs} style="position:absolute;left:{x - w//2}px;top:{y}px;width:{w}px;font-family:{MONO};font-size:24px;font-weight:700;line-height:1.5;text-align:center;border-radius:8px;{st}">{text}</p>'


def hlabel(x, y, h, hid):
    return p(f"position:absolute;left:{x-80}px;top:{y+30}px;width:160px;font-family:{MONO};font-size:22px;font-weight:700;text-align:center;color:{INK}", h, f' id="{hid}"')


YM, YB = 470, 340


def graph(main_moved=False):
    g = ['<div id="gbox" style="position:absolute;left:96px;top:236px;width:1728px;height:340px;background:#FDFCF9;border:2px solid #E1DED6;border-radius:24px"></div>']
    g.append(f'<div id="dots" style="position:absolute;left:130px;top:{YM-3}px;width:110px;height:6px;border-top:6px dotted {BLL}"></div>')
    end = 780 if main_moved else 560
    g += [hline(260, end, YM, BLL, ' id="e-main"'), conn(560, YM, 760, YB, GRL)]
    g += [node(300, YM, BL, attrs=' id="n0"'), hlabel(300, YM, H0, "h0"), node(560, YM, BL, attrs=' id="n1"'), hlabel(560, YM, H1, "h1")]
    g += [node(760, YB, GR, attrs=' id="nb"'), hlabel(760, YB, HB, "hb"), pill(760, YB - 70, "feature/login", "green", ' id="t-br"')]
    if main_moved:
        g += [node(780 + 0, YM, BL, attrs=' id="nm"'), hlabel(780, YM, HM, "hm")]
        g += [pill(780, YM + 66, "main", "main", ' id="t-main"')]
    else:
        g += [pill(560, YM + 66, "main", "main", ' id="t-main"')]
    return g


def order_boxes(a, b, ac, bc):
    o = []
    for i, (bid, lab, col) in enumerate([(a[0], a[1], ac), (b[0], b[1], bc)]):
        x = 1060 + i * 390
        o.append(f'<div id="{bid}" style="position:absolute;left:{x}px;top:300px;width:330px;height:150px;background:#FFFFFF;border:3px solid {col};border-radius:18px;padding:18px 22px;display:flex;flex-direction:column;gap:8px">'
                 + p(f"font-size:22px;font-weight:700;color:#6A7180", "앞 (기준)" if i == 0 else "뒤 (비교)")
                 + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{col}", lab) + '</div>')
    o.append('<x-shape id="ord-arrow" kind="arrow-right" style="position:absolute;left:1400px;top:356px;width:40px;height:36px;background:#9AA0AB"></x-shape>')
    o.append(p(f"position:absolute;left:1060px;top:476px;width:720px;font-size:24px;line-height:1.4;color:{SUB}", "앞에서 뒤로 가려면 무엇을 바꾸나", ' id="ord-cap"'))
    return o


def bscene(sid, eyebrow, title, cmd, out, call, notes, moved=False, swap=False, transition="magic"):
    o = [sec(sid, transition)] + head(eyebrow, title, OR)
    o += graph(moved)
    A, B = ("box-main", "main"), ("box-br", "feature/login")
    o += order_boxes(B, A, GR, BL) if swap else order_boxes(A, B, BL, GR)
    o += terminal([("$", cmd)] + diff_lines(out), top=608, h=416, size=23, lh=1.25)
    o += callout(*call, top=608, h=416)
    W(sid, o, notes)


bscene("br1", "브랜치 비교", "merge 전에 무엇이 들어올지 봐요", "git diff main feature/login", DIFF_BR,
       ("Activity", "feature/login에서<br>바꾼 것만 보여요", "제목 한 줄, 새 줄 하나", OR),
       "03처럼 feature/login 브랜치에서 제목을 # 로그인하기로 바꾸고 비밀번호 찾기 줄을 더해 커밋했어요. 그다음 git checkout main으로 돌아왔어요. git diff 브랜치1 브랜치2는 두 브랜치의 마지막 커밋을 비교해요. merge하면 main에 이 변경이 들어와요. 바뀐 파일 이름만 보고 싶으면 --stat을 붙여요.", transition="fade")
bscene("br2", "브랜치 비교", "순서를 바꾸면 +와 -가 뒤집혀요", "git diff feature/login main", DIFF_BR_REV,
       ("Warning", "받을 쪽을 앞에,<br>들어올 쪽을 뒤에", "git diff main feature/login", RED),
       "앞에 쓴 브랜치에서 뒤에 쓴 브랜치로 가려면 무엇을 바꿔야 하는지 보여 줘요. 그래서 순서를 바꾸면 같은 차이가 반대 기호로 나와요. merge 전에 볼 땐 git merge와 같은 감각으로 받을 쪽 main을 앞에 써요.", swap=True)
bscene("br3", "브랜치 비교", "같은 줄을 양쪽에서 고쳤다면", "git diff main feature/login", DIFF_BR2,
       ("Warning", "같은 줄이 양쪽에서<br>달라요", "merge하면 충돌이 날 수 있어요", RED),
       f"그사이 main에서도 제목을 # 로그인 페이지로 바꿔 커밋했어요({HM}). 이제 diff의 - 줄은 main의 제목, + 줄은 feature/login의 제목이에요. 두 브랜치가 같은 줄을 서로 다르게 고쳤다는 신호예요. 이 상태로 merge하면 다음 장처럼 충돌이 나요. 두 브랜치의 마지막 커밋끼리 비교하기 때문에, main에서만 고친 줄도 - 쪽에 나온다는 점을 짚어 주세요.", moved=True)

# ---------- part 6: conflict ----------
c = [sec("conflict")] + head("충돌 볼 때", "충돌 나면 git diff로 그곳만 봐요", RED)
cl = [("$", "git merge feature/login"), ("r", "CONFLICT (content): Merge conflict in login.md"), ("o", "Automatic merge failed; fix conflicts and then commit the result."), ("$", "git diff")] + diff_lines(DIFF_CC)
c += terminal(cl, left=96, top=236, w=1160, h=690, size=24, lh=1.4)
# line i top = 236 + 20 + i*33.6
def ly(i):
    return round(256 + i * 33.6)
c.append(f'<div data-build-in="fade order 1" style="position:absolute;left:1280px;top:{ly(9)}px;width:8px;height:{ly(14)-ly(9)}px;background:{RED};border-radius:4px"></div>')
c.append(f'<div data-build-in="fade order 1" style="position:absolute;left:1308px;top:{ly(9)-110}px;width:516px;display:flex;flex-direction:column;gap:6px">'
         + p(f"font-size:30px;font-weight:700;color:{RED}", "충돌 난 곳만 나와요") + p(f"font-size:24px;line-height:1.4;color:{SUB}", "++ 로 시작하는 줄이 충돌 표시") + '</div>')
c.append(f'<div data-build-in="fade order 2" style="position:absolute;left:1308px;top:{ly(10)}px;width:516px;height:34px;display:flex;flex-direction:row;gap:12px;align-items:center">'
         + p(f"font-size:26px;font-weight:700;color:{BL}", "↑ 위: main(HEAD) 쪽") + '</div>')
c.append(f'<div data-build-in="fade order 2" style="position:absolute;left:1308px;top:{ly(12)}px;width:516px;height:34px;display:flex;flex-direction:row;gap:12px;align-items:center">'
         + p(f"font-size:26px;font-weight:700;color:#1A7340", "↓ 아래: feature/login 쪽") + '</div>')
c.append(f'<div data-build-in="rise order 3" style="position:absolute;left:1308px;top:{ly(15)}px;width:516px;background:#FFFFFF;border:2px solid {LINE};border-radius:16px;padding:18px 22px;display:flex;flex-direction:column;gap:6px">'
         + p(f"font-size:24px;font-weight:700;color:{INK}", "앞의 두 칸 기호는") + p(f"font-size:24px;line-height:1.4;color:{SUB}", "어느 쪽에서 온 줄인지예요.<br>지금은 넘어가도 돼요.") + '</div>')
c.append(p(f"position:absolute;left:96px;top:954px;width:1728px;font-size:28px;font-weight:700;color:{INK}", "파일이 여러 개여도 git diff 하나로 충돌 표시가 남은 곳을 모두 찾아요.", ' data-build-in="fade order 4"'))
W("conflict", c, "br3 상태에서 git merge feature/login을 쳐서 충돌이 났어요. 첫 줄 Auto-merging login.md는 화면 때문에 뺐어요. 충돌 중에 git diff를 치면 diff --cc라는 모양으로 충돌 난 부분만 보여 줘요. 앞에 기호가 두 칸 붙는 건 두 브랜치와 각각 비교해서예요. 지금은 ++ 줄이 충돌 표시이고 그 사이 위아래가 양쪽 내용이라는 것만 기억하면 돼요. 푸는 순서는 03과 같아요.")

o = [sec("resolve")] + head("충돌 볼 때", "고친 뒤 add하고, 커밋 전에 한 번 더 봐요", RED)
rl = [("#", "# login.md에서 # 로그인하기만 남기고 표시 세 줄을 지움"), ("$", "git add login.md"), ("$", "git diff --staged")] + diff_lines(DIFF_BR2) + [("$", 'git commit -m "fix: 로그인 제목 충돌 해결"'), ("o", f"[main {HR}] fix: 로그인 제목 충돌 해결")]
o += terminal(rl, left=96, top=236, w=1160, h=720, size=24, lh=1.4)
o.append(f'<div data-build-in="rise" style="position:absolute;left:1296px;top:236px;width:528px;height:720px;background:#FFFFFF;border:2px solid {LINE};border-radius:20px;padding:36px 36px;display:flex;flex-direction:column;gap:22px">'
         + p(f"font-size:32px;font-weight:700;color:{INK}", "커밋 전 확인")
         + "".join(f'<div style="display:flex;flex-direction:row;gap:16px;align-items:flex-start">'
                   + p(f"width:44px;height:44px;flex:none;font-size:24px;font-weight:900;line-height:44px;text-align:center;color:#FFFFFF;background:{col};border-radius:22px", n_)
                   + p(f"font-size:26px;line-height:1.45;color:{INK}", t_) + '</div>'
                   for n_, t_, col in [("1", "<span style=\"font-family:'JetBrains Mono',monospace;font-weight:700\">&lt;&lt;&lt;</span> 같은 표시가 남지 않았나", RED),
                                       ("2", "남긴 제목이 맞나", BL), ("3", "merge로 main에 들어올 줄이 이게 다인가", C_ST)])
         + '<div style="flex:1"></div>'
         + p(f"font-size:24px;line-height:1.45;color:{SUB}", "--staged는 main의 마지막 커밋과 비교해요. merge 커밋에 들어갈 내용이에요.") + '</div>')
W("resolve", o, "충돌을 풀고 add한 뒤 git diff --staged를 보면 이 merge 커밋으로 main에 들어올 변경이 나와요. 브랜치 비교에서 본 것과 같은 내용이에요. 충돌 표시가 남아 있으면 여기서 + 줄로 보여요. 확인이 끝나면 커밋해요.")

# ---------- part 7: .gitignore ----------
def file_tile(fid, name, status, style, top, extra=""):
    bg, bd, col = {"red": ("#FBE4E2", "#E07A7A", "#A33131"), "gray": ("#EEEFF2", "#B4B9C3", "#3A4150"), "hide": ("#F6F5F1", "#B4B9C3", "#6A7180"), "green": ("#DDF2E5", "#4DB57A", "#1A7340")}[style]
    dash = "dashed" if style == "hide" else "solid"
    return (f'<div id="{fid}" style="position:absolute;left:136px;top:{top}px;width:520px;height:96px;background:{bg};border:2px {dash} {bd};border-radius:16px;padding:12px 20px;display:flex;flex-direction:column;gap:2px{extra}">'
            + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{INK}", e(name)) + p(f"font-size:22px;font-weight:700;color:{col}", e(status)) + '</div>')


def small_call(icon, text, icolor):
    return [f'<div id="explain" data-build-in="rise" style="position:absolute;left:736px;top:692px;width:1088px;height:184px;background:#FFFFFF;border:2px solid {LINE};border-radius:20px;padding:28px 36px;display:flex;flex-direction:row;gap:24px;align-items:center">'
            f'<x-icon name="{icon}" style="width:56px;height:56px;color:{icolor}"></x-icon>' + p(f"font-size:32px;font-weight:700;line-height:1.4;color:{INK}", text) + '</div>']


def ig(sid, title, files, term, icon, text, icolor, notes, transition="magic"):
    o = [sec(sid, transition)] + head(".gitignore", title, PUR)
    o.append('<div id="folder" style="position:absolute;left:96px;top:236px;width:600px;height:640px;background:#FDFCF9;border:2px solid #9AA0AB;border-radius:20px"></div>')
    o.append('<div id="folder-h" style="position:absolute;left:128px;top:262px;width:540px;display:flex;flex-direction:row;gap:10px;align-items:center"><x-icon name="Code" style="width:32px;height:32px;color:#3A4150"></x-icon>'
             + p("font-size:30px;font-weight:700;color:#3A4150", "① 작업 폴더 hello-git/") + '</div>')
    o += files
    o += terminal(term, left=736, top=236, w=1088, h=420, lh=1.3)
    o += small_call(icon, text, icolor)
    W(sid, o, notes)


F_LOGIN = file_tile("f-login", "login.md", "Committed · 변경 없음", "gray", 330)
ig("ig1", "비밀번호가 든 파일, 올리면 안 돼요",
   [F_LOGIN, file_tile("f-env", ".env", "Untracked · API_KEY=abc123", "red", 442), file_tile("f-ig", ".gitignore", "", "red", 554, ";opacity:0")],
   [("$", 'echo "API_KEY=abc123" > .env'), ("$", "git status"), ("o", "On branch main"), ("o", "Untracked files:"), ("#", '  (use "git add <file>..." to include in what will be committed)'),
    ("r", "\t.env"), ("o", ""), ("o", "nothing added to commit but untracked files present")],
   "Warning", "git add . 한 번이면 .env까지 올라가요.<br>GitHub에 올라간 키는 누구나 볼 수 있어요.", RED,
   ".env는 API 키 같은 비밀 값을 적어 두는 파일이에요. 수업에서 AI API를 쓸 때 자주 만들어요. status에 계속 빨간 글씨로 나오고, git add .을 치면 같이 올라가요. 한 번 push한 키는 지워도 기록에 남아요. 그래서 키를 새로 발급받아야 해요. status 마지막 줄 끝의 안내 문구는 화면 때문에 뺐어요.", transition="fade")
ig("ig2", ".gitignore에 이름을 적으면 Git이 못 본 척해요",
   [F_LOGIN, file_tile("f-env", ".env", "무시됨 · status에 안 나와요", "hide", 442), file_tile("f-ig", ".gitignore", "Untracked · 새 파일", "red", 554)],
   [("$", 'echo ".env" > .gitignore'), ("$", "git status"), ("o", "On branch main"), ("o", "Untracked files:"), ("#", '  (use "git add <file>..." to include in what will be committed)'),
    ("r", "\t.gitignore"), ("$", "git add .gitignore"), ("$", 'git commit -m "chore: .env를 gitignore에 추가"'), ("o", "[main 0e35512] chore: .env를 gitignore에 추가")],
   "CheckCircle", ".env가 status에서 사라지고<br>.gitignore는 커밋해서 팀과 같이 써요.", C_ST,
   ".gitignore는 저장소 맨 위 폴더에 두는 파일이에요. 한 줄에 하나씩 무시할 파일 이름을 적어요. .env 파일 자체는 지워지지 않고 그대로 있어요. Git이 못 본 척할 뿐이에요. .gitignore는 커밋해서 팀원도 같은 규칙을 쓰게 해요. status 출력 마지막 안내 줄은 화면 때문에 뺐어요.")

g = [sec("ig3")] + head(".gitignore", "자주 적는 것들", PUR)
rows = [(".env", "비밀 값", "API 키, 비밀번호"), ("node_modules/", "받은 패키지", "npm install로 다시 받아요"), ("__pycache__/", "파이썬 임시 파일", "실행하면 저절로 생겨요"),
        (".venv/", "파이썬 가상 환경", "내 컴퓨터에서만 써요"), ("*.log", "로그 파일", "* 는 아무 이름"), (".DS_Store", "macOS 폴더 설정", "Finder가 만들어요")]
g.append(f'<div style="position:absolute;left:96px;top:236px;width:1080px;height:704px;background:#FFFFFF;border:2px solid {LINE};border-radius:20px;padding:20px 36px;display:flex;flex-direction:column">')
for i, (pat, what, why) in enumerate(rows):
    bd = f"border-top:2px solid {LINE};" if i else ""
    g.append(f'<div data-build-in="fade order {i+1}" style="flex:1;display:flex;flex-direction:row;align-items:center;gap:24px;padding:0 12px;{bd}">'
             + p(f"width:340px;flex:none;font-family:{MONO};font-size:32px;font-weight:700;color:{PUR}", e(pat))
             + p(f"width:300px;flex:none;font-size:28px;font-weight:700;color:{INK}", what) + p(f"font-size:24px;color:#6A7180", why) + '</div>')
g.append('</div>')
g.append(f'<div style="position:absolute;left:1216px;top:236px;width:608px;height:704px;background:#1B2029;border-radius:20px;padding:32px 36px;display:flex;flex-direction:column;gap:6px;font-family:{MONO}">'
         + p("font-family:'Noto Sans KR',sans-serif;font-size:24px;font-weight:700;color:#8C95A6;margin-bottom:12px", ".gitignore 파일 예")
         + "".join(p(f"font-size:30px;line-height:1.5;font-weight:700;color:{c_}", e(l)) for c_, l in [("#8C95A6", "# 비밀 값"), ("#D8DEE9", ".env"), ("#8C95A6", "# 패키지, 임시 파일"), ("#D8DEE9", "node_modules/"), ("#D8DEE9", "__pycache__/"), ("#D8DEE9", ".venv/"), ("#D8DEE9", "*.log"), ("#D8DEE9", ".DS_Store")])
         + '</div>')
g.append(p(f"position:absolute;left:96px;top:968px;width:1728px;font-size:26px;color:{SUB}", "끝에 / 를 붙이면 폴더, # 으로 시작하면 메모 줄이에요."))
W("ig3", g, "프로젝트를 만들 때 처음부터 .gitignore를 두면 편해요. GitHub에서 새 저장소를 만들 때 Add .gitignore 메뉴로 Python, Node 같은 템플릿을 고를 수도 있어요. 공통 규칙은 이 정도만 알면 돼요. 한 줄에 하나, 끝에 /는 폴더, *는 아무 글자, #은 메모예요.")

g = [sec("ig4")] + head(".gitignore", "이미 커밋한 파일은 숨겨지지 않아요", PUR)
g += terminal([("$", 'echo "*.log" >> .gitignore'), ("$", 'echo "error" >> app.log'), ("$", "git status"), ("o", "Changes not staged for commit:"), ("r", "\tmodified:   .gitignore"), ("r", "\tmodified:   app.log"),
               ("#", "# app.log가 계속 나와요"), ("$", "git rm --cached app.log"), ("o", "rm 'app.log'"), ("$", "git status"), ("o", "Changes to be committed:"), ("g", "\tdeleted:    app.log"),
               ("o", "Changes not staged for commit:"), ("r", "\tmodified:   .gitignore")], left=96, top=236, w=1100, h=704, lh=1.35)
g.append(f'<div data-build-in="rise" style="position:absolute;left:1236px;top:236px;width:588px;height:704px;background:#FFFFFF;border:2px solid {LINE};border-radius:20px;padding:36px;display:flex;flex-direction:column;gap:22px">'
         + f'<x-icon name="Warning" style="width:52px;height:52px;color:{RED}"></x-icon>'
         + p(f"font-size:32px;font-weight:700;line-height:1.4;color:{INK}", ".gitignore는 Git이 아직 모르는 파일에만 통해요")
         + p(f"font-size:26px;line-height:1.5;color:{SUB}", "이미 커밋한 파일은 이 명령으로 기록 대상에서 빼요.") + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{INK};background:#EEEFF2;padding:10px 16px;border-radius:10px", "git rm --cached 파일")
         + p(f"font-size:26px;line-height:1.5;color:{SUB}", "내 폴더의 파일은 그대로 있어요. 그다음 add, commit 해요.")
         + '</div>')
W("ig4", g, "app.log를 먼저 커밋해 버린 뒤에 *.log를 .gitignore에 적은 상황이에요. Git은 이미 기록하던 파일은 계속 지켜봐요. git rm --cached는 파일은 내 폴더에 두고 Git 기록에서만 빼요. 그다음 .gitignore와 함께 add, commit 하면 돼요. 그래서 .gitignore는 프로젝트 처음에 만드는 게 좋아요. 비밀 값을 이미 push했다면 키를 새로 발급받아요. status 안내 줄과 On branch main 줄은 화면 때문에 뺐어요.")

# ---------- part 8: trouble ----------
tb = [sec("t-empty")] + head("막힐 때", "git diff에 아무것도 안 나와요", "#1E3F8F")
cases = [("이미 git add 했어요", "대기실에 올린 건 --staged로 봐요", "git diff --staged"),
         ("새로 만든 파일이에요", "Untracked 파일은 git diff에 안 나와요. add한 뒤에 봐요", "git add 파일<br>git diff --staged"),
         ("이미 commit 했어요", "커밋한 내용은 git show로 봐요", "git show")]
tb.append(f'<div style="position:absolute;left:96px;top:250px;width:1728px;display:flex;flex-direction:column;gap:24px">')
for i, (q, a_, cmd) in enumerate(cases, 1):
    tb.append(f'<div data-build-in="rise order {i}" style="height:200px;display:flex;flex-direction:row;gap:32px;align-items:center;background:#FFFFFF;border:2px solid {LINE};border-radius:20px;padding:24px 36px">'
              + p(f"width:64px;height:64px;flex:none;font-size:34px;font-weight:900;line-height:64px;text-align:center;color:#FFFFFF;background:#1E3F8F;border-radius:32px", str(i))
              + f'<div style="flex:1;display:flex;flex-direction:column;gap:10px">' + p(f"font-size:34px;font-weight:700;color:{INK}", q) + p(f"font-size:26px;color:{SUB}", a_) + '</div>'
              + p(f"width:460px;flex:none;font-family:{MONO};font-size:28px;font-weight:700;line-height:1.5;color:{INK};background:#EEEFF2;padding:14px 20px;border-radius:12px", cmd) + '</div>')
tb.append('</div>')
W("t-empty", tb, "가장 많이 나오는 질문이에요. 빈 화면은 오류가 아니라 비교한 두 칸이 같다는 뜻이에요. 먼저 git status를 보고 빨간 글씨면 git diff, 초록 글씨면 git diff --staged, 둘 다 없으면 git show를 써요. 새 파일은 git diff에 안 나오는 게 처음엔 가장 헷갈려요.")

tp = [sec("t-pager")] + head("막힐 때", "화면이 안 끝나거나, 너무 길어요", "#1E3F8F")
tp.append(f'<div style="position:absolute;left:96px;top:250px;width:842px;height:640px;background:#FFFFFF;border:2px solid {LINE};border-radius:20px;padding:36px;display:flex;flex-direction:column;gap:22px">'
          + p(f"font-size:32px;font-weight:700;color:{INK}", "아래에 : 나 (END)가 보이고 멈춰요")
          + f'<div style="background:#1B2029;border-radius:14px;padding:20px 24px;display:flex;flex-direction:column;font-family:{MONO}">'
          + "".join(p(f"font-size:24px;line-height:1.4;white-space:pre;font-weight:700;color:{TC[k]}", e(l)) for k, l in [("g", "+로그인 버튼"), ("g", "+아이디 저장"), ("o", "(END)")]) + '</div>'
          + p(f"font-size:26px;line-height:1.5;color:{SUB}", "출력이 길면 한 화면씩 보여 줘요.<br>Space는 다음 화면, q는 나가기예요.")
          + '<div style="flex:1"></div>'
          + p(f"font-family:{MONO};font-size:44px;font-weight:700;color:{BL}", "q") + '</div>')
tp.append(f'<div style="position:absolute;left:982px;top:250px;width:842px;height:640px;background:#FFFFFF;border:2px solid {LINE};border-radius:20px;padding:36px;display:flex;flex-direction:column;gap:22px">'
          + p(f"font-size:32px;font-weight:700;color:{INK}", "파일 이름과 줄 수만 보고 싶어요")
          + f'<div style="background:#1B2029;border-radius:14px;padding:20px 24px;display:flex;flex-direction:column;font-family:{MONO}">'
          + "".join(p(f"font-size:24px;line-height:1.4;white-space:pre;font-weight:700;color:{c_}", e(l)) for c_, l in [("#F2C46D", "$ git diff --stat main feature/login"), ("#D8DEE9", " login.md | 3 ++-"), ("#D8DEE9", " 1 file changed, 2 insertions(+), 1 deletion(-)")]) + '</div>'
          + p(f"font-size:26px;line-height:1.5;color:{SUB}", "--stat은 어떤 명령에도 붙여요.<br>+, - 개수로 얼마나 바뀌었는지 봐요.")
          + '<div style="flex:1"></div>'
          + p(f"font-family:{MONO};font-size:44px;font-weight:700;color:{BL}", "--stat") + '</div>')
W("t-pager", tp, "Git은 출력이 한 화면보다 길면 less라는 보기 프로그램으로 보여 줘요. 화살표나 Space로 내려가고 q로 나와요. 터미널이 멈춘 게 아니에요. --stat은 git diff, git diff --staged, git show에 모두 붙일 수 있어요. 파일이 많을 때 먼저 --stat으로 훑고, 궁금한 파일만 git diff 파일이름으로 봐요.")

# ---------- cheatsheet ----------
ch = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};padding:112px 128px;display:flex;flex-direction:column;gap:40px">',
      f'<h2 style="font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>', '<div style="display:flex;flex-direction:row;gap:24px;flex:1">']
cards = [("add 전", C_WD, "#FFFFFF", INK, "git status<br>빨간 글씨면<br>git diff"),
         ("commit 전", C_ST, "#FFFFFF", INK, "초록 글씨면<br>git diff --staged<br><br>커밋한 뒤엔<br>git show"),
         ("merge 전", OR, "#FFFFFF", INK, "git diff main 브랜치<br><br>충돌 나면<br>git diff"),
         ("처음부터", PUR, "#FFFFFF", INK, ".gitignore<br>.env<br>node_modules/<br>__pycache__/<br><br>나가기: q")]
for h, hc, bg, tc, body in cards:
    ch.append(f'<div style="flex:1;display:flex;flex-direction:column;gap:16px;background:{bg};border:2px solid {LINE};border-top:10px solid {hc};border-radius:20px;padding:32px 28px">'
              f'<h3 style="font-size:32px;font-weight:700;color:{hc}">{h}</h3>'
              f'<p style="font-family:{MONO};font-size:28px;line-height:1.7;color:{tc}">{body}</p></div>')
ch += ['</div>', f'<p style="font-size:28px;font-weight:700;color:{INK}"><span style="color:{RED}">-</span> 지운 줄 · <span style="color:#1A7340">+</span> 넣은 줄 · <span style="color:#1E7FA8">@@</span> 위치</p>']
W("cheatsheet", ch, "수업 끝에 이 장을 띄워 두고 add, commit, merge 직전에 무엇을 칠지 학생이 직접 말해 보게 하세요. 순서는 status로 보고, diff로 확인하고, 그다음 add나 commit이에요.")
print("ok")
