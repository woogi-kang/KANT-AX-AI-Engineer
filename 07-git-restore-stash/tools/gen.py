"""Generates every slide of the git restore and stash deck.

Scenes reuse the 4-zone frame of 02 (작업 폴더, 대기실, 내 저장소, 원격 저장소). Stash scenes add a
서랍 box where the file card moves while it is put away.
Terminal output comes from tools/demo.sh (git 2.43).
Usage: python3 tools/gen.py slides
"""
import html, os, sys

OUT = sys.argv[1]
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
INK, SUB, LINE = "#1D2330", "#4A5262", "#E1DED6"
BL, BLL, GR, GRL, OR, RED, PUR = "#2459C9", "#9DB8F2", "#1F8A4C", "#9ED3B4", "#B26A00", "#A33131", "#5A3BB8"
C_RS, C_UN, C_SH = "#A33131", "#1A7340", "#B26A00"   # restore = red (버림), --staged = green, stash = orange


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
# o 출력, r 빨강, g 초록, # 회색 안내, H 눈여겨볼 줄, $ 명령
TC = {"$": "#F2C46D", "o": "#D8DEE9", "h": "#FFFFFF", "c": "#7CC7E8", "r": "#F28B82", "g": "#7FD18B", "#": "#8C95A6", "H": "#FFE7A8"}


def kind_of(line):
    if line.startswith(("diff ", "index ", "--- ", "+++ ")):
        return "h"
    if line.startswith("@@"):
        return "c"
    if line.startswith("-"):
        return "r"
    if line.startswith("+"):
        return "g"
    return "o"


def diff_lines(text):
    return [(kind_of(l), l) for l in text.strip("\n").split("\n")]


def terminal(lines, left=96, top=650, w=1150, h=374, size=22, lh=1.3, tid="term"):
    o = [f'<div id="{tid}" style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:#1B2029;border-radius:20px;padding:18px 28px;display:flex;flex-direction:column;font-family:{MONO};font-variant-ligatures:none">']
    for kind, text in lines:
        t = e(text).replace("\t", "        ")
        if kind == "$":
            t = "$ " + t
        bold = "font-weight:700;" if kind in "h$H" else ""
        mark = "background:rgba(242,196,109,0.22);border-radius:6px;margin:0 -8px;padding:0 8px;" if kind == "H" else ""
        o.append(p(f"font-size:{size}px;line-height:{lh};white-space:pre;{bold}{mark}color:{TC[kind]}", t if t else " "))
    o.append('</div>')
    return o


# ---------- real outputs (tools/demo.sh) ----------
H0, H1, HL, H2, HL2, H3 = "e12ffc2", "15d92cb", "0be6431", "8eacb89", "365260f", "dd746b3"
HINT_RS = '  (use "git restore <file>..." to discard changes in working directory)'
HINT_ADD = '  (use "git add <file>..." to update what will be committed)'
HINT_UN = '  (use "git restore --staged <file>..." to unstage)'
NO_ADD = 'no changes added to commit (use "git add" and/or "git commit -a")'
DIFF_OOPS = """diff --git a/login.md b/login.md
index ef88ce3..b4b694b 100644
--- a/login.md
+++ b/login.md
@@ -1,3 +1 @@
-# 로그인
-아이디
-비밀번호
+로그인 버튼"""
DIFF_KEEP = """diff --git a/login.md b/login.md
index 6e22a11..b8c799e 100644
--- a/login.md
+++ b/login.md
@@ -2,3 +2,4 @@
 아이디
 비밀번호
 로그인 버튼
+아이디 저장"""
PULL_ERR = [("o", "From https://github.com/kim/hello-git"), ("o", " * branch            main       -> FETCH_HEAD"), ("o", f"   {H1}..{HL}  main       -> origin/main"),
            ("o", f"Updating {H1}..{HL}"), ("r", "error: Your local changes to the following files would be overwritten by merge:"), ("r", "\tlogin.md"),
            ("H", "Please commit your changes or stash them before you merge."), ("o", "Aborting")]
PULL_OK = [("o", "From https://github.com/kim/hello-git"), ("o", " * branch            main       -> FETCH_HEAD"), ("o", f"Updating {H1}..{HL}"), ("o", "Fast-forward"),
           ("o", " login.md | 2 +-"), ("o", " 1 file changed, 1 insertion(+), 1 deletion(-)")]
WIP1 = f"WIP on main: {H1} feat: 로그인 버튼 추가"
WIP2 = f"WIP on main: {H2} feat: 비밀번호 찾기 추가"

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
DRAWER = dict(left=1278, top=650, w=546, h=374)


def zx(k):
    return Z[k]["left"] + Z[k]["w"] // 2


def drawer_box(empty_note=None):
    d = DRAWER
    o = [f'<div id="drawer" style="position:absolute;left:{d["left"]}px;top:{d["top"]}px;width:{d["w"]}px;height:{d["h"]}px;background:#FFF7EA;border:3px solid #E3A64A;border-radius:20px;padding:16px 20px;display:flex;flex-direction:column">'
         '<div style="display:flex;flex-direction:row;gap:10px;align-items:center">'
         f'<x-icon name="Archive" style="width:32px;height:32px;color:{C_SH}"></x-icon>'
         + p(f"font-size:30px;font-weight:700;color:{C_SH}", "서랍 (stash)") + '</div></div>']
    if empty_note:
        o.append(p(f"position:absolute;left:{d['left']+24}px;top:{d['top']+76}px;width:{d['w']-48}px;font-size:24px;line-height:1.4;color:#8A5A12", empty_note, ' id="drawer-note"'))
    return o


def frame(sid, eyebrow, cmd, transition="magic", cmd_size=52, remote=False, drawer=None):
    o = [sec(sid, transition)]
    o.append('<div id="bracket" style="position:absolute;left:80px;top:184px;width:1280px;height:388px;border:2px dashed #B9BDC6;border-radius:28px"></div>')
    o.append(p(f"position:absolute;left:96px;top:40px;width:1728px;font-size:24px;font-weight:700;color:{BL}", e(eyebrow), ' id="eyebrow"'))
    o.append(f'<h2 id="cmd" style="position:absolute;left:96px;top:86px;width:1728px;font-family:{MONO};font-size:{cmd_size}px;font-weight:700;line-height:1.15;color:{INK}">{cmd}</h2>')
    o.append('<x-icon id="ic-local" name="Home" style="position:absolute;left:100px;top:196px;width:28px;height:28px;color:#6A7180"></x-icon>')
    o.append(p("position:absolute;left:136px;top:193px;width:600px;font-size:24px;font-weight:700;color:#6A7180", "내 컴퓨터", ' id="lbl-local"'))
    o.append('<x-icon id="ic-remote" name="Globe" style="position:absolute;left:1392px;top:196px;width:28px;height:28px;color:#5A3BB8"></x-icon>')
    o.append(p("position:absolute;left:1428px;top:193px;width:396px;font-size:24px;font-weight:700;color:#5A3BB8", "GitHub", ' id="lbl-remote"'))
    for k, z in Z.items():
        op = ";opacity:0.4" if k == "rm" and not remote else ""
        o.append(f'<div id="z-{k}" style="position:absolute;left:{z["left"]}px;top:{ZTOP}px;width:{z["w"]}px;height:{ZH}px;background:{z["bg"]};border:2px solid {z["bd"]};border-radius:20px;padding:16px 20px;display:flex;flex-direction:column{op}">'
                 '<div style="display:flex;flex-direction:row;gap:10px;align-items:center">'
                 f'<x-icon name="{z["icon"]}" style="width:32px;height:32px;color:{z["tc"]}"></x-icon>'
                 + p(f"font-size:30px;font-weight:700;color:{z['tc']}", f'{z["num"]} {z["title"]}') + '</div></div>')
    if not remote:
        o.append(p("position:absolute;left:1412px;top:300px;width:392px;font-size:24px;color:#5A4A8F;opacity:0.6", "이번엔 쓰지 않아요", ' id="ph-rm"'))
    if drawer is not None:
        o += drawer_box(drawer or None)
    return o


DOC_ST = {"red": ("#FFFFFF", "#E07A7A", "#A33131"), "green": ("#FFFFFF", "#4DB57A", "#1A7340"), "gray": ("#FFFFFF", "#B4B9C3", "#3A4150"), "orange": ("#FFFFFF", "#E3A64A", "#8A5A12")}
MARK = {"add": "background:#DDF2E5;color:#14532D", "del": "background:#FBE4E2;color:#7A1F1F", None: f"color:{INK}"}


def card(cid, left, top, w, h, lines, label, style, marks=None, name="login.md"):
    bg, bd, col = DOC_ST[style]
    marks = marks or {}
    o = [f'<div id="{cid}" style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:{bg};border:2px solid {bd};border-radius:14px;padding:10px 14px;display:flex;flex-direction:column;gap:2px">']
    o.append(f'<div style="display:flex;flex-direction:row;justify-content:space-between;align-items:center">'
             + p(f"font-family:{MONO};font-size:20px;font-weight:700;color:{INK}", name)
             + p(f"font-size:18px;font-weight:700;color:{col}", e(label)) + '</div>')
    for i, l in enumerate(lines):
        o.append(p(f"font-family:{MONO};font-size:20px;line-height:1.35;padding:0 6px;border-radius:4px;{MARK[marks.get(i)]}", e(l)))
    o.append('</div>')
    return "".join(o)


def doc(cid, k, lines, label, style, top=CARD_TOP, marks=None, height=None):
    z = Z[k]
    return card(cid, z["left"] + 20, top, z["w"] - 40, height or (ZBOT - 16 - top), lines, label, style, marks)


def in_drawer(cid, lines, label, marks=None):
    d = DRAWER
    return card(cid, d["left"] + 20, d["top"] + 70, d["w"] - 40, d["h"] - 90, lines, label, "orange", marks)


def chip(cid, k, name, status, style, top):
    z = Z[k]
    bg, bd, col = DOC_ST[style]
    return (f'<div id="{cid}" style="position:absolute;left:{z["left"]+20}px;top:{top}px;width:{z["w"]-40}px;height:96px;background:{bg};border:2px solid {bd};border-radius:14px;padding:12px 16px;display:flex;flex-direction:column;gap:4px">'
            + p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{INK}", e(name)) + p(f"font-size:20px;font-weight:700;color:{col}", e(status)) + '</div>')


def zone_note(k, text, sub=None, top=300):
    z = Z[k]
    s = p(f"font-size:24px;font-weight:700;color:{z['tc']}", e(text))
    if sub:
        s += p("font-size:22px;line-height:1.4;color:#4A5262", sub)
    return f'<div id="note-{k}" style="position:absolute;left:{z["left"]+20}px;top:{top}px;width:{z["w"]-40}px;display:flex;flex-direction:column;gap:8px">{s}</div>'


def commit_row(k, h, top=CARD_TOP, rid="lc", tag="main", color=BL):
    z = Z[k]
    tag_html = (p(f"font-family:{MONO};font-size:22px;font-weight:700;line-height:1.4;padding:0 10px;border-radius:8px;background:{color};color:#FFFFFF", tag) if tag else "")
    return (f'<div id="{rid}-{h}" style="position:absolute;left:{z["left"]+20}px;top:{top}px;width:{z["w"]-40}px;height:36px;display:flex;flex-direction:row;gap:12px;align-items:center">'
            f'<x-shape kind="ellipse" style="width:22px;height:22px;background:{color};border:3px solid {color}"></x-shape>'
            + p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{INK}", h) + tag_html + '</div>')


def back_bar(a, b, label, color, bid="bar", y=600, order=None):
    """U-shaped bar under zones a and b with an arrow head going up into zone b (b gets the change)."""
    x1, x2 = sorted([zx(a), zx(b)])
    attr = f' data-build-in="fade order {order}"' if order else ""
    lw = round(len(label) * 15.6 + 36)
    mid = (x1 + x2) // 2
    return (f'<div id="{bid}"{attr} style="position:absolute;left:{x1-3}px;top:{ZBOT+18}px;width:{x2-x1+6}px;height:{y-ZBOT-18}px;border:6px solid {color};border-top:none;border-radius:0 0 14px 14px"></div>'
            + f'<x-connector id="{bid}-head"{attr} x1="{zx(b)}" y1="{ZBOT+24}" x2="{zx(b)}" y2="{ZBOT+2}" head="end" style="color:{color};border-width:6px"></x-connector>'
            + p(f"position:absolute;left:{mid-lw//2}px;top:{y-24}px;width:{lw}px;font-family:{MONO};font-size:26px;font-weight:700;line-height:1.6;text-align:center;border-radius:10px;background:{color};color:#FFFFFF", e(label), f' id="{bid}-lbl"{attr}'))


def callout(icon, title, sub=None, icolor=BL, top=650, h=374):
    o = [f'<div id="explain" data-build-in="rise" style="position:absolute;left:1278px;top:{top}px;width:546px;height:{h}px;background:#FFFFFF;border:2px solid {LINE};border-radius:20px;padding:32px;display:flex;flex-direction:column;justify-content:center;gap:16px">']
    o.append(f'<x-icon name="{icon}" style="width:56px;height:56px;color:{icolor}"></x-icon>')
    o.append(p(f"font-size:34px;font-weight:700;line-height:1.35;color:{INK}", title))
    if sub:
        o.append(p(f"font-size:26px;line-height:1.45;color:{SUB}", sub))
    o.append('</div>')
    return o


def num(i, color, size=64):
    return p(f"width:{size}px;height:{size}px;flex:none;font-size:{size//2}px;font-weight:900;line-height:{size}px;text-align:center;color:#FFFFFF;background:{color};border-radius:{size//2}px", str(i))


V0 = ["# 로그인", "아이디", "비밀번호"]
V1 = V0 + ["로그인 버튼"]
VL = ["# 로그인 페이지", "아이디", "비밀번호", "로그인 버튼"]
LR0 = [commit_row("lr", H0), doc("lr-doc", "lr", V0, "마지막 커밋", "gray", top=348)]

# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:#1D2330;color:#F6F5F1;font-family:{SANS};padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#8FB3FF;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
       '<h1 style="font-size:104px;font-weight:900;line-height:1.1;color:#F6F5F1">restore와 stash,<br>눈으로 보기</h1>',
       '<p style="font-size:40px;line-height:1.4;color:#BFC6D4">고친 걸 버리거나<br>잠깐 치워 두는 법</p>']
cov.append(f'<div style="position:absolute;left:1120px;top:330px;width:640px;height:420px;background:#252B36;border-radius:24px;padding:40px 44px;display:flex;flex-direction:column;gap:12px;font-family:{MONO}">')
for k, l in [("$", "$ git restore login.md"), ("#", "  고친 것 버리기"), ("$", "$ git stash"), ("#", "  서랍에 넣기"), ("$", "$ git stash pop"), ("#", "  서랍에서 꺼내기")]:
    cov.append(p(f"font-size:34px;line-height:1.4;white-space:pre;font-weight:700;color:{TC[k]}", e(l)))
cov.append('</div>')
W("cover", cov, "02의 네 칸 그림과 hello-git 저장소, login.md로 이어서 실습해요. 오늘 배울 명령은 셋이에요. 고친 걸 버리는 git restore, add를 취소하는 git restore --staged, 고치던 걸 잠깐 치우는 git stash예요. 팀 레포에서 pull이 막힐 때 바로 쓰는 명령이에요.")

# ---------- toc ----------
parts = [("Wrench", C_RS, "git restore", "고친 걸 버리기", "5–8쪽"),
         ("CheckCircle", C_UN, "git restore --staged", "add 취소하기", "9–11쪽"),
         ("Activity", BL, "reset과 무엇이 달라요", "파일과 이름표", "12쪽"),
         ("Archive", C_SH, "git stash", "고치던 걸 서랍에 잠깐", "13–18쪽"),
         ("Users", PUR, "팀에서 쓰기", "pull 전에 치우고 꺼내기", "19–22쪽"),
         ("Warning", "#1E3F8F", "막힐 때", "자주 나오는 메시지", "23쪽")]
t = [f'<section id="toc" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};padding:96px 128px;display:flex;flex-direction:column;gap:40px">',
     f'<h2 style="font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>',
     '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:24px;flex:1">']
for i, (ic, c, h, s, pg) in enumerate(parts, 1):
    t.append(f'<div style="display:flex;flex-direction:column;gap:10px;background:#FFFFFF;border:2px solid {LINE};border-top:10px solid {c};border-radius:20px;padding:24px 28px">'
             f'<div style="display:flex;flex-direction:row;gap:14px;align-items:center"><p style="font-size:48px;font-weight:900;line-height:1.25;color:{c}">{i}</p>'
             f'<x-icon name="{ic}" style="width:40px;height:40px;color:{c}"></x-icon></div>'
             f'<h3 style="font-family:{MONO if h.startswith("git") else SANS};font-size:32px;font-weight:700;color:{INK}">{h}</h3>'
             f'<p style="font-size:26px;line-height:1.4;color:{SUB}">{s}</p><div style="flex:1"></div>'
             f'<p style="font-size:24px;color:#6A7180">{pg}</p></div>')
t += ['</div>', f'<p style="font-size:26px;color:{SUB}">마지막 24쪽은 한 장 요약이에요.</p>']
W("toc", t, "1~4부는 02의 네 칸 그림 위에서 진행해요. 4부부터는 그림 오른쪽 아래에 서랍이 하나 더 생겨요. 5부는 오늘 팀 레포에서 pull이 막혔을 때 쓰는 순서예요.")

# ---------- why ----------
w = [sec("why")] + head("들어가기", "이럴 때 쓰는 명령이에요")
cases = [("Warning", C_RS, "파일을 망쳤어요", "&gt;&gt; 대신 &gt; 를 쳐서<br>내용이 다 사라졌어요", "git restore"),
         ("CheckCircle", C_UN, "엉뚱한 파일까지 올렸어요", "git add . 로<br>개인 메모까지 올렸어요", "git restore --staged"),
         ("Archive", C_SH, "pull이 막혀요", "고치던 게 있는데<br>팀원이 push했대요", "git stash")]
for i, (ic, c, q, d, cmd) in enumerate(cases):
    x = 96 + i * 592
    w.append(f'<div data-build-in="rise order {i+1}" style="position:absolute;left:{x}px;top:270px;width:544px;height:560px;background:#FFFFFF;border:2px solid {LINE};border-top:10px solid {c};border-radius:20px;padding:40px 36px;display:flex;flex-direction:column;gap:20px">'
             f'<x-icon name="{ic}" style="width:64px;height:64px;color:{c}"></x-icon>'
             + p(f"font-size:38px;font-weight:700;line-height:1.3;color:{INK}", q)
             + p(f"font-size:28px;line-height:1.5;color:{SUB}", d) + '<div style="flex:1"></div>'
             + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{c};background:#F6F5F1;padding:14px 18px;border-radius:12px", cmd) + '</div>')
w.append(p(f"position:absolute;left:96px;top:880px;width:1728px;font-size:30px;line-height:1.4;color:{SUB}", "셋 다 아직 커밋하지 않은 변경을 다뤄요.", ' data-build-in="fade order 4"'))
W("why", w, "셋 다 수업 중에 실제로 자주 나오는 장면이에요. 첫째는 01에서 배운 > 와 >> 를 헷갈린 경우예요. > 는 파일을 새로 덮어쓰고, >> 는 끝에 붙여요. 둘째는 git add . 이 폴더 안 모든 파일을 올려서 생겨요. 셋째는 오늘 팀 실습에서 가장 많이 막히는 곳이에요. 커밋한 뒤의 되돌리기는 02와 03에서 배운 reset과 revert가 맡아요.")

# ---------- map ----------
m = [sec("map")] + head("들어가기", "네 칸 그림에서 보면")
MT, MH = 380, 170
for k, z in Z.items():
    op = ";opacity:0.4" if k == "rm" else ""
    m.append(f'<div style="position:absolute;left:{z["left"]}px;top:{MT}px;width:{z["w"]}px;height:{MH}px;background:{z["bg"]};border:2px solid {z["bd"]};border-radius:20px;padding:24px;display:flex;flex-direction:column;gap:14px{op}">'
             '<div style="display:flex;flex-direction:row;gap:10px;align-items:center">'
             f'<x-icon name="{z["icon"]}" style="width:36px;height:36px;color:{z["tc"]}"></x-icon>'
             + p(f"font-size:34px;font-weight:700;color:{z['tc']}", f'{z["num"]} {z["title"]}') + '</div>'
             + p(f"font-size:24px;line-height:1.4;color:#4A5262", {"wd": "지금 고치는 파일", "st": "add로 올린 모습", "lr": "commit한 기록", "rm": "이번엔 거의 안 써요"}[k]) + '</div>')
# arrows above the zones: both end in ①
for i, (src, lab, col, y) in enumerate([("st", "git restore --staged", C_UN, 320), ("lr", "git restore", C_RS, 256)]):
    x1, x2 = zx("wd") + (30 if i == 0 else -30), zx(src)
    o_ = f' data-build-in="fade order {i+1}"'
    m.append(f'<div{o_} style="position:absolute;left:{x1-3}px;top:{y}px;width:{x2-x1+6}px;height:{MT-y-2}px;border:6px solid {col};border-bottom:none;border-radius:14px 14px 0 0"></div>')
    m.append(f'<x-connector{o_} x1="{x1}" y1="{MT-26}" x2="{x1}" y2="{MT-2}" head="end" style="color:{col};border-width:6px"></x-connector>')
    lw = round(len(lab) * 15.6 + 36)
    m.append(p(f"position:absolute;left:{(x1+x2)//2-lw//2}px;top:{y-24}px;width:{lw}px;font-family:{MONO};font-size:26px;font-weight:700;line-height:1.6;text-align:center;border-radius:10px;background:{col};color:#FFFFFF", lab, o_))
# drawer below ①
o_ = ' data-build-in="fade order 3"'
m.append(f'<div{o_} style="position:absolute;left:96px;top:700px;width:768px;height:200px;background:#FFF7EA;border:3px solid #E3A64A;border-radius:20px;padding:24px;display:flex;flex-direction:column;gap:12px">'
         '<div style="display:flex;flex-direction:row;gap:10px;align-items:center">'
         f'<x-icon name="Archive" style="width:36px;height:36px;color:{C_SH}"></x-icon>' + p(f"font-size:34px;font-weight:700;color:{C_SH}", "서랍 (stash)") + '</div>'
         + p("font-size:24px;line-height:1.4;color:#8A5A12", "고치던 걸 잠깐 넣어 두는 곳") + '</div>')
m.append(f'<x-connector{o_} x1="236" y1="{MT+MH+4}" x2="236" y2="696" head="end" style="color:{C_SH};border-width:6px"></x-connector>')
m.append(f'<x-connector{o_} x1="316" y1="696" x2="316" y2="{MT+MH+4}" head="end" style="color:{C_SH};border-width:6px"></x-connector>')
m.append(p(f"position:absolute;left:350px;top:600px;width:500px;font-family:{MONO};font-size:24px;font-weight:700;color:{C_SH}", "↓ git stash   ↑ git stash pop", o_))
m.append(f'<div data-build-in="rise order 4" style="position:absolute;left:912px;top:620px;width:912px;display:flex;flex-direction:column;gap:16px">')
for lab, col, desc in [("git restore 파일", C_RS, "③ 마지막 커밋 모습으로 ①을 덮어요"), ("git restore --staged 파일", C_UN, "②에서 내려요. ① 내용은 그대로"), ("git stash", C_SH, "①② 변경을 서랍에 넣고 ③ 모습으로")]:
    m.append(f'<div style="display:flex;flex-direction:column;gap:6px;background:#FFFFFF;border:2px solid {LINE};border-left:10px solid {col};border-radius:16px;padding:14px 24px">'
             + p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{col}", lab) + p(f"font-size:26px;font-weight:700;color:{INK}", desc) + '</div>')
m.append('</div>')
W("map", m, "02의 네 칸 그림이에요. 오늘 명령은 모두 ① 작업 폴더나 ② 대기실을 바꿔요. ③ 내 저장소의 커밋은 건드리지 않아요. restore는 위쪽 화살표처럼 ③이나 ②의 모습을 ①로 가져와요. stash는 ① ②의 변경을 아래 서랍에 넣었다가 pop으로 다시 꺼내요. 서랍도 내 컴퓨터 안에 있어서 GitHub에는 올라가지 않아요.")

# ---------- part 1: git restore ----------
o = frame("r1", "실습 1 · 파일을 망쳤어요", 'echo "로그인 버튼" &gt; login.md', cmd_size=48)
o.append(doc("wd-doc", "wd", ["로그인 버튼"], "덮어씀", "red", marks={0: "add"}))
o.append(zone_note("st", "비어 있음"))
o += LR0
o += terminal([("$", 'echo "로그인 버튼" > login.md'), ("$", "git status"), ("o", "On branch main"), ("o", "Changes not staged for commit:"), ("#", HINT_ADD),
               ("H", HINT_RS), ("r", "\tmodified:   login.md"), ("o", ""), ("o", NO_ADD)], size=21)
o += callout("Lightbulb", "status가 방법을<br>알려 주고 있어요", "노란 줄: git restore로<br>고친 걸 버려요", icolor=OR)
W("r1", o, ">> 대신 > 를 쳐서 login.md 세 줄이 사라지고 로그인 버튼 한 줄만 남았어요. 01에서 > 는 덮어쓰기, >> 는 끝에 붙이기라고 배웠어요. git status를 보면 Git이 다음에 칠 명령을 괄호 안에 알려 줘요. 둘째 줄이 git restore예요. 앞 모듈에서는 화면 때문에 이 안내 줄을 자주 뺐어요. 오늘은 이 줄을 읽어요.")

o = frame("r2", "실습 1 · 버리기 전에 확인", "git diff")
o.append(doc("wd-doc", "wd", ["로그인 버튼"], "덮어씀", "red", marks={0: "add"}))
o.append(zone_note("st", "비어 있음"))
o.append(commit_row("lr", H0))
o.append(doc("lr-doc", "lr", V0, "마지막 커밋", "gray", top=348, marks={0: "del", 1: "del", 2: "del"}))
o += terminal([("$", "git diff")] + diff_lines(DIFF_OOPS))
o += callout("Search", "무엇이 바뀌는지<br>먼저 봐요", "restore하면 + 줄이 사라지고<br>- 줄이 돌아와요", icolor=C_RS)
W("r2", o, "04에서 배운 git diff로 지금 고친 내용을 봐요. - 세 줄이 원래 있던 줄, + 한 줄이 새로 생긴 줄이에요. restore를 치면 + 줄은 사라지고 - 줄이 돌아와요. 사라지는 + 줄 중에 남길 게 있는지 꼭 확인하고 넘어가요.")

o = frame("r3", "실습 1 · git restore", "git restore login.md")
o.append(doc("wd-doc", "wd", V0, "되돌림", "gray"))
o.append(zone_note("st", "비어 있음"))
o += LR0
o.append(back_bar("lr", "wd", "git restore", C_RS))
o += terminal([("$", "git restore login.md"), ("$", "cat login.md")] + [("o", l) for l in V0] + [("$", "git status"), ("o", "On branch main"), ("o", "nothing to commit, working tree clean")])
o += callout("CheckCircle", "마지막 커밋 모습으로<br>돌아왔어요", f"③ 커밋 {H0}는 그대로예요", icolor=C_UN)
W("r3", o, "git restore 파일이름은 ③ 마지막 커밋의 모습으로 ① 작업 폴더의 파일을 덮어써요. 아무 출력도 없이 끝나요. cat으로 보면 세 줄이 돌아왔어요. git status도 깨끗해요. 커밋 기록은 하나도 바뀌지 않았어요. 정확히는 ② 대기실의 모습으로 돌아가요. 대기실이 비어 있으면 마지막 커밋과 같은 모습이에요.")

wr = [sec("r-warn")] + head("git restore · 주의", "restore로 버린 건 되찾을 수 없어요", C_RS)
wr.append(f'<div style="position:absolute;left:96px;top:250px;width:760px;height:640px;background:#FFFFFF;border:2px solid {LINE};border-radius:20px;padding:40px;display:flex;flex-direction:column;gap:24px">'
          + f'<x-icon name="Warning" style="width:64px;height:64px;color:{C_RS}"></x-icon>'
          + p(f"font-size:36px;font-weight:700;line-height:1.4;color:{INK}", "커밋하지 않은 변경은<br>Git에 기록이 없어요")
          + p(f"font-size:28px;line-height:1.5;color:{SUB}", "reset이나 revert는 커밋을 다뤄서 기록이 남아요. restore로 버린 줄은 휴지통에도 가지 않아요.")
          + '<div style="flex:1"></div>'
          + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{C_RS};background:#FBE4E2;padding:16px 20px;border-radius:12px", "git restore . 은 특히 조심")
          + '</div>')
tips = [("git diff 먼저", "사라질 줄을 눈으로 확인해요", "git diff"),
        ("남길 게 있으면 커밋", "커밋해 두면 나중에 되돌릴 수 있어요", 'git add 파일<br>git commit -m "..."'),
        ("파일 이름을 꼭 적기", "git restore . 은 모든 파일을 한 번에 버려요", "git restore login.md")]
wr.append('<div style="position:absolute;left:904px;top:250px;width:920px;height:640px;display:flex;flex-direction:column;gap:24px">')
for i, (h, d, cmd) in enumerate(tips, 1):
    wr.append(f'<div data-build-in="rise order {i}" style="flex:1;display:flex;flex-direction:row;gap:28px;align-items:center;background:#FFFFFF;border:2px solid {LINE};border-radius:20px;padding:20px 32px">'
              + num(i, C_RS, 56) + f'<div style="flex:1;display:flex;flex-direction:column;gap:8px">' + p(f"font-size:30px;font-weight:700;color:{INK}", h) + p(f"font-size:24px;color:{SUB}", d) + '</div>'
              + p(f"width:360px;flex:none;font-family:{MONO};font-size:22px;font-weight:700;line-height:1.5;color:{INK};background:#EEEFF2;padding:12px 16px;border-radius:12px", cmd) + '</div>')
wr.append('</div>')
W("r-warn", wr, "restore는 고친 내용을 지우는 명령이라 되돌릴 수 없어요. 02에서 본 reflog도 커밋만 기억해서 여기엔 소용없어요. 그래서 세 가지를 지켜요. 먼저 git diff로 보고, 남길 줄이 있으면 커밋부터 하고, 파일 이름을 꼭 적어요. git restore . 처럼 점을 쓰면 폴더 안 모든 파일의 변경이 한 번에 사라져요.")

# ---------- part 2: git restore --staged ----------
o = frame("s1", "실습 2 · 엉뚱한 파일까지 올렸어요", "git add .")
o.append(chip("wd-login", "wd", "login.md", "올림", "gray", 300))
o.append(chip("wd-memo", "wd", "memo.md", "올림", "gray", 412))
o.append(chip("st-login", "st", "login.md", "Staged · 고침", "green", 300))
o.append(chip("st-memo", "st", "memo.md", "Staged · 새 파일", "green", 412))
o.append(commit_row("lr", H0))
o += terminal([("$", 'echo "로그인 버튼" >> login.md'), ("$", 'echo "내일 할 일: 디자인 묻기" > memo.md'), ("$", "git add ."), ("$", "git status"),
               ("o", "On branch main"), ("o", "Changes to be committed:"), ("H", HINT_UN), ("g", "\tmodified:   login.md"), ("g", "\tnew file:   memo.md")])
o += callout("Warning", "memo.md는<br>올리면 안 돼요", "노란 줄: add를 취소하는<br>명령이에요", icolor=RED)
W("s1", o, "login.md에 로그인 버튼을 붙이고, 내 할 일을 적은 memo.md도 만들었어요. git add . 은 폴더 안 바뀐 파일을 모두 올려서 memo.md까지 대기실에 들어갔어요. 이대로 commit하고 push하면 팀원 모두가 내 메모를 받아요. 초록 글씨 위 안내 줄이 add를 취소하는 방법이에요. unstage는 대기실에서 내린다는 뜻이에요.")

o = frame("s2", "실습 2 · git restore --staged", "git restore --staged memo.md", cmd_size=48)
o.append(chip("wd-login", "wd", "login.md", "올림", "gray", 300))
o.append(chip("st-memo", "wd", "memo.md", "Untracked · 내용 그대로", "red", 412))
o.append(chip("st-login", "st", "login.md", "Staged · 고침", "green", 300))
o.append(commit_row("lr", H0))
o.append(back_bar("st", "wd", "git restore --staged", C_UN))
o += terminal([("$", "git restore --staged memo.md"), ("$", "git status"), ("o", "On branch main"), ("o", "Changes to be committed:"), ("#", HINT_UN), ("g", "\tmodified:   login.md"),
               ("o", ""), ("o", "Untracked files:"), ("#", '  (use "git add <file>..." to include in what will be committed)'), ("r", "\tmemo.md")], size=21)
o += callout("CheckCircle", "② 대기실에서만<br>내렸어요", "memo.md 파일은<br>① 에 그대로 있어요", icolor=C_UN)
W("s2", o, "memo.md만 대기실에서 내렸어요. 파일은 지워지지 않고 작업 폴더에 그대로 있어요. 처음 만든 파일이라 다시 Untracked가 됐어요. 이제 git commit -m \"feat: 로그인 버튼 추가\"로 login.md만 커밋하고 push해요. 실습에서는 memo.md를 rm으로 지우고 넘어가요. 계속 둘 파일이면 04에서 배운 .gitignore에 적어요.")

c3 = [sec("s3")] + head("restore 두 가지", "--staged가 있고 없고는 크게 달라요", C_UN)
for i, (lab, col, src, desc, sub) in enumerate([("git restore 파일", C_RS, "③", "① 의 고친 내용을 버려요", "되찾을 수 없어요"),
                                                 ("git restore --staged 파일", C_UN, "②", "② 에서 ① 로 내려요", "고친 내용은 그대로 있어요")]):
    x = 96 + i * 888
    c3.append(f'<div data-build-in="rise order {i+1}" style="position:absolute;left:{x}px;top:240px;width:840px;height:300px;background:#FFFFFF;border:2px solid {LINE};border-top:10px solid {col};border-radius:20px;padding:28px 36px;display:flex;flex-direction:column;gap:16px">'
              + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:{col}", lab)
              + '<div style="display:flex;flex-direction:row;gap:16px;align-items:center">'
              + "".join(p(f"width:120px;font-size:28px;font-weight:700;line-height:64px;text-align:center;border-radius:14px;background:{Z[k]['bg']};border:2px solid {Z[k]['bd']};color:{Z[k]['tc']}", Z[k]["num"]) for k in ["wd", "st", "lr"])
              + p(f"font-size:26px;font-weight:700;color:{col}", f"{src} → ①") + '</div>'
              + p(f"font-size:30px;font-weight:700;color:{INK}", desc) + p(f"font-size:26px;color:{SUB}", sub) + '</div>')
c3 += terminal([("$", 'echo "아이디 저장" >> login.md'), ("$", "git add login.md"), ("$", "git restore --staged login.md"), ("$", "git diff")] + diff_lines(DIFF_KEEP),
               left=96, top=580, w=1100, h=420, size=22, lh=1.3)
c3.append(f'<div data-build-in="rise order 3" style="position:absolute;left:1236px;top:580px;width:588px;height:420px;background:#FFFFFF;border:2px solid {LINE};border-radius:20px;padding:36px;display:flex;flex-direction:column;justify-content:center;gap:18px">'
          + f'<x-icon name="Lightbulb" style="width:52px;height:52px;color:{OR}"></x-icon>'
          + p(f"font-size:32px;font-weight:700;line-height:1.4;color:{INK}", "add를 취소해도<br>+아이디 저장은 남아요")
          + p(f"font-size:26px;line-height:1.5;color:{SUB}", "--staged를 빼면 이 줄까지 사라져요.") + '</div>')
W("s3", c3, "두 명령은 이름이 비슷해서 헷갈려요. --staged가 붙으면 대기실만 고치고 작업 폴더는 건드리지 않아요. 붙지 않으면 작업 폴더의 파일을 덮어써요. 아래 터미널은 login.md를 add한 뒤 --staged로 내린 장면이에요. git diff에 아이디 저장이 그대로 나와요. 다시 올리려면 git add만 치면 돼요. 확인한 뒤 실습에서는 git restore login.md로 이 줄을 버리고 넘어가요.")

# ---------- part 3: reset과 차이 ----------
rv = [sec("reset-vs")] + head("reset과 무엇이 달라요", "restore는 파일, reset은 이름표를 옮겨요")


def mini_graph(x, y, moved):
    g = [f'<div style="position:absolute;left:{x}px;top:{y+19}px;width:240px;height:6px;background:{BLL}"></div>']
    for j, h in enumerate([H0, H1]):
        cx = x + j * 240
        g.append(f'<div style="position:absolute;left:{cx-20}px;top:{y+2}px;width:40px;height:40px;border-radius:50%;background:{BL};border:4px solid {BL}{";opacity:0.35" if moved and j == 1 else ""}"></div>')
        g.append(p(f"position:absolute;left:{cx-70}px;top:{y+54}px;width:140px;font-family:{MONO};font-size:22px;font-weight:700;text-align:center;color:{INK}", h))
    tx = x if moved else x + 240
    g.append(p(f"position:absolute;left:{tx-50}px;top:{y-58}px;width:100px;font-family:{MONO};font-size:24px;font-weight:700;line-height:1.5;text-align:center;border-radius:8px;background:{BL};color:#FFFFFF", "main"))
    return g


for i, (lab, col, title, sub, moved) in enumerate([("git restore 파일", C_RS, "커밋과 이름표는 그대로", "① ② 의 파일만 바꿔요", False),
                                                    ("git reset HEAD~1", BL, "이름표가 한 칸 뒤로", "커밋을 취소해요 (02, 03)", True)]):
    x = 96 + i * 888
    rv.append(f'<div data-build-in="rise order {i+1}" style="position:absolute;left:{x}px;top:240px;width:840px;height:400px;background:#FFFFFF;border:2px solid {LINE};border-top:10px solid {col};border-radius:20px;padding:28px 36px;display:flex;flex-direction:column;gap:10px">'
              + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:{col}", lab) + p(f"font-size:30px;font-weight:700;color:{INK}", title) + p(f"font-size:24px;color:{SUB}", sub) + '</div>')
    rv += [s.replace("<div ", f'<div data-build-in="rise order {i+1}" ', 1).replace("<p ", f'<p data-build-in="rise order {i+1}" ', 1) for s in mini_graph(x + 300, 500, moved)]
rows = [("", "바꾸는 곳", "커밋 기록", "언제"), ("git restore 파일", "① 작업 폴더", "그대로", "커밋 전, 고친 걸 버릴 때"), ("git restore --staged 파일", "② 대기실", "그대로", "commit 전, add를 취소할 때"),
        ("git reset HEAD~1", "③ 이름표", "한 칸 뒤로", "push 전, 커밋을 취소할 때")]
rv.append(f'<div data-build-in="fade order 3" style="position:absolute;left:96px;top:680px;width:1728px;height:300px;background:#FFFFFF;border:2px solid {LINE};border-radius:20px;padding:12px 36px;display:flex;flex-direction:column">')
for j, r_ in enumerate(rows):
    bd = f"border-top:2px solid {LINE};" if j else ""
    cells = "".join(p(f"width:{wd}px;flex:none;font-family:{MONO if (c == 0 and j) else SANS};font-size:{24 if j else 22}px;font-weight:{700 if (c == 0 or not j) else 400};color:{INK if j else '#6A7180'}", e(v))
                    for c, (v, wd) in enumerate(zip(r_, [500, 300, 260, 540])))
    rv.append(f'<div style="flex:1;display:flex;flex-direction:row;align-items:center;gap:16px;padding:0 12px;{bd}">{cells}</div>')
rv.append('</div>')
W("reset-vs", rv, "02와 03에서 배운 reset은 브랜치 이름표를 뒤로 옮겨서 커밋을 취소해요. restore는 커밋을 건드리지 않고 파일만 바꿔요. 그래서 커밋하기 전에는 restore, 커밋한 뒤에는 reset이나 revert를 써요. 옛날 자료에는 git reset HEAD 파일이름으로 add를 취소하는 법이 나와요. git restore --staged와 같은 일을 해요. 수업에서는 status가 알려 주는 restore --staged를 써요.")

# ---------- part 4: git stash ----------
VW = V1 + ["비밀번호 찾기"]
o = frame("st0", "실습 3 · pull하려는데 막혀요", "git pull origin main", remote=True)
o.append(doc("wd-doc", "wd", VW, "고치는 중", "red", marks={4: "add"}))
o.append(zone_note("st", "비어 있음"))
o.append(commit_row("lr", H1))
o.append(doc("lr-doc", "lr", V1, "마지막 커밋", "gray", top=348))
o.append(commit_row("rm", HL, rid="rc", tag="", color=PUR))
o.append(commit_row("rm", H1, top=344, rid="rc", tag="", color=PUR))
o.append(zone_note("rm", "lee가 제목을 고쳐 올렸어요", top=400))
o += terminal([("$", 'echo "비밀번호 찾기" >> login.md'), ("$", "git pull origin main")] + PULL_ERR, size=20, lh=1.35)
o += callout("Warning", "커밋하거나<br>stash 하래요", "고치던 게 덮일까 봐<br>Git이 멈췄어요", icolor=RED)
W("st0", o, "팀원 lee가 login.md 제목을 로그인 페이지로 고쳐 push했어요. 나는 같은 파일에 비밀번호 찾기를 쓰던 중이에요. 아직 커밋하기엔 덜 끝났어요. 이때 pull하면 Git이 멈춰요. 받은 내용으로 파일을 바꾸면 내가 고친 줄이 덮일 수 있어서예요. 노란 줄이 해결 방법이에요. 커밋하거나 stash 하라고 해요. 같은 파일을 둘 다 고쳤을 때만 이 메시지가 나와요.")

o = frame("st1", "실습 3 · git stash", "git stash", remote=True, drawer="")
o.append(in_drawer("wd-doc", VW, "stash@{0}", marks={4: "add"}))
o.append(doc("wd-clean", "wd", V1, "변경 없음", "gray"))
o.append(zone_note("st", "비어 있음"))
o.append(commit_row("lr", H1))
o.append(doc("lr-doc", "lr", V1, "마지막 커밋", "gray", top=348))
o.append(commit_row("rm", HL, rid="rc", tag="", color=PUR))
o.append(commit_row("rm", H1, top=344, rid="rc", tag="", color=PUR))
o.append(zone_note("rm", "lee가 제목을 고쳐 올렸어요", top=400))
o += terminal([("$", "git stash"), ("o", f"Saved working directory and index state {WIP1}"), ("$", "git status"), ("o", "On branch main"), ("o", "nothing to commit, working tree clean"),
               ("$", "git stash list"), ("H", f"stash@{{0}}: {WIP1}")], size=20, lh=1.4)
W("st1", o, "git stash는 고치던 내용을 서랍에 넣고 작업 폴더를 마지막 커밋 모습으로 돌려놓아요. 비밀번호 찾기 줄이 서랍으로 옮겨 갔어요. git status가 깨끗해져서 이제 pull할 수 있어요. git stash list로 서랍 안을 봐요. 서랍은 내 컴퓨터에만 있어요. push해도 GitHub에 올라가지 않아요. stash는 숨겨 둔다는 뜻이에요.")

rd = [sec("st-read")] + head("git stash list 읽기", "서랍 안 한 줄이 이렇게 생겼어요", C_SH)
segs = [("stash@{0}", "#F2C46D", "서랍 번호", "0이 가장 최근"), (":  WIP on ", "#8C95A6", "작업 중", "Work In Progress"), ("main", "#7CC7E8", "치운 브랜치", "어디서 넣었나"),
        (f":  {H1} feat: 로그인 버튼 추가", "#D8DEE9", "그때 마지막 커밋", "이 커밋 위에서 고치던 것")]
rd.append(f'<div style="position:absolute;left:96px;top:250px;width:1728px;height:120px;background:#1B2029;border-radius:20px;display:flex;flex-direction:row;align-items:center;justify-content:center;font-family:{MONO}">'
          + "".join(p(f"font-size:36px;font-weight:700;white-space:pre;color:{c}", e(s)) for s, c, _, _ in segs) + '</div>')
rd.append('<div style="position:absolute;left:96px;top:410px;width:1728px;display:flex;flex-direction:row;gap:24px">')
for i, (s, c, t1, t2) in enumerate(segs, 1):
    rd.append(f'<div data-build-in="rise order {i}" style="flex:1;display:flex;flex-direction:column;gap:8px;background:#FFFFFF;border:2px solid {LINE};border-top:8px solid {c if c != "#D8DEE9" else "#9AA0AB"};border-radius:16px;padding:20px 24px">'
              + p(f"font-size:28px;font-weight:700;color:{INK}", t1) + p(f"font-size:24px;color:{SUB}", t2) + '</div>')
rd.append('</div>')
rd += terminal([("$", "git stash"), ("$", "git stash list"), ("H", f"stash@{{0}}: WIP on main: {H3} feat: 비밀번호 재설정에 이메일 안내 추가"), ("o", f"stash@{{1}}: WIP on main: {H3} feat: 비밀번호 재설정에 이메일 안내 추가")],
               left=96, top=640, w=1100, h=200, size=22)
rd.append(f'<div data-build-in="rise order 5" style="position:absolute;left:1236px;top:640px;width:588px;height:200px;background:#FFFFFF;border:2px solid {LINE};border-radius:20px;padding:28px 32px;display:flex;flex-direction:column;justify-content:center;gap:10px">'
          + p(f"font-size:28px;font-weight:700;line-height:1.4;color:{INK}", "또 넣으면 새 것이 {0}") + p(f"font-size:24px;line-height:1.4;color:{SUB}", "예전 것은 {1}로 밀려요") + '</div>')
rd.append(p(f"position:absolute;left:96px;top:880px;width:1728px;font-size:28px;line-height:1.4;color:{SUB}", "pop은 맨 위 {0}부터 꺼내요. 서랍엔 한 번에 하나만 두는 게 편해요.", ' data-build-in="fade order 6"'))
W("st-read", rd, "stash list 한 줄은 네 부분이에요. 맨 앞 stash@{0}이 서랍 번호예요. WIP는 Work In Progress, 작업 중이라는 뜻이에요. 그 뒤로 어느 브랜치에서 넣었는지, 그때 마지막 커밋이 무엇이었는지 나와요. 아래 터미널은 실습을 다 끝낸 뒤 stash를 두 번 한 모습이에요. 새로 넣은 게 늘 0번이에요. 여러 개가 쌓이면 무엇이 무엇인지 헷갈려서 넣으면 바로 꺼내는 습관을 들여요.")

o = frame("st2", "실습 3 · 이제 pull", "git pull origin main", remote=True, drawer="")
o.append(in_drawer("wd-doc", VW, "stash@{0}", marks={4: "add"}))
o.append(doc("wd-clean", "wd", VL, "받음", "gray", marks={0: "add"}))
o.append(zone_note("st", "비어 있음"))
o.append(commit_row("lr", HL))
o.append(doc("lr-doc", "lr", VL, "마지막 커밋", "gray", top=348, marks={0: "add"}))
o.append(commit_row("rm", HL, rid="rc", tag="", color=PUR))
o.append(commit_row("rm", H1, top=344, rid="rc", tag="", color=PUR))
o.append(zone_note("rm", "lee가 제목을 고쳐 올렸어요", top=400))
o += terminal([("$", "git pull origin main")] + PULL_OK, size=20, lh=1.4)
W("st2", o, "작업 폴더가 깨끗하니 pull이 바로 끝나요. Fast-forward는 내 커밋 없이 앞으로만 따라간 거예요. 03에서 본 merge와 같은 말이에요. 제목이 로그인 페이지로 바뀌었어요. 서랍 안의 비밀번호 찾기는 그대로 기다리고 있어요.")

o = frame("st3", "실습 3 · git stash pop", "git stash pop", remote=True, drawer="서랍이 다시 비었어요")
o.append(doc("wd-doc", "wd", ["# 로그인 페이지", "아이디", "비밀번호", "로그인 버튼", "비밀번호 찾기"], "고치는 중", "red", marks={4: "add"}))
o.append(zone_note("st", "비어 있음"))
o.append(commit_row("lr", HL))
o.append(doc("lr-doc", "lr", VL, "마지막 커밋", "gray", top=348))
o.append(commit_row("rm", HL, rid="rc", tag="", color=PUR))
o.append(commit_row("rm", H1, top=344, rid="rc", tag="", color=PUR))
o.append(zone_note("rm", "lee가 제목을 고쳐 올렸어요", top=400))
o += terminal([("$", "git stash pop"), ("o", "Auto-merging login.md"), ("o", "On branch main"), ("o", "Changes not staged for commit:"), ("r", "\tmodified:   login.md"),
               ("o", ""), ("H", "Dropped refs/stash@{0} (ea47a275d168793f5d750db2514463f36986122d)")], size=20, lh=1.4)
W("st3", o, "pop은 서랍에서 꺼내서 작업 폴더에 다시 얹어요. Auto-merging은 받은 제목과 내 비밀번호 찾기를 Git이 알아서 합쳤다는 뜻이에요. 서로 다른 줄이라 충돌 없이 끝났어요. 마지막 Dropped 줄은 꺼낸 걸 서랍에서 지웠다는 뜻이에요. status 안내 줄 두 개와 마지막 no changes added 줄은 화면 때문에 뺐어요. 이제 하던 일을 마저 하고 add, commit, push해요.")

co = [sec("st-co")] + head("git stash · 브랜치 옮길 때", "checkout이 막힐 때도 같아요", C_SH)
co += terminal([("$", "git checkout main"), ("r", "error: Your local changes to the following files would be overwritten by checkout:"), ("r", "\tlogin.md"),
                ("H", "Please commit your changes or stash them before you switch branches."), ("o", "Aborting")], left=96, top=240, w=1728, h=230, size=26, lh=1.4)
flow = [("git stash", "feature/login에서<br>고치던 걸 넣기"), ("git checkout main", "main으로 가서"), ("급한 일", "고치고 commit, push"), ("git checkout feature/login", "돌아와서"), ("git stash pop", "꺼내서 이어서")]
co.append('<div style="position:absolute;left:96px;top:520px;width:1728px;height:300px;display:flex;flex-direction:row;gap:20px">')
for i, (cmd, d) in enumerate(flow, 1):
    mono = cmd.startswith("git")
    co.append(f'<div data-build-in="rise order {i}" style="flex:1;display:flex;flex-direction:column;gap:14px;background:#FFFFFF;border:2px solid {LINE};border-top:8px solid {C_SH if i in (1, 5) else "#9AA0AB"};border-radius:18px;padding:24px 22px">'
              + num(i, C_SH if i in (1, 5) else "#6A7180", 52)
              + p(f"font-family:{MONO if mono else SANS};font-size:{22 if mono else 26}px;font-weight:700;line-height:1.35;color:{INK}", cmd)
              + p(f"font-size:24px;line-height:1.4;color:{SUB}", d) + '</div>')
co.append('</div>')
co.append(p(f"position:absolute;left:96px;top:870px;width:1728px;font-size:28px;line-height:1.4;color:{SUB}", "서랍은 브랜치와 상관없이 하나예요. 꺼낼 때는 넣었던 브랜치로 돌아가서 pop 해요.", ' data-build-in="fade order 6"'))
W("st-co", co, "03에서 본 checkout 에러예요. 그때는 커밋하고 옮기라고 했어요. 덜 끝난 작업이면 stash로 치워도 돼요. feature/login에서 고치던 중에 main으로 가려고 하면 이 에러가 나요. 서랍은 저장소에 하나뿐이라 다른 브랜치에서도 같은 서랍이 보여요. 다른 브랜치에서 pop하면 그 브랜치에 얹혀서 헷갈려요. stash list의 on main, on feature/login 부분을 보고 넣었던 브랜치에서 꺼내요.")

# ---------- part 5: team ----------
tf = [sec("team-flow")] + head("팀에서 쓰기", "팀원이 push했대요. 나는 고치던 중이에요", PUR)
steps = [("git stash", "고치던 걸 서랍에", C_SH), ("git pull origin main", "팀원 커밋 받기", PUR), ("git stash pop", "서랍에서 꺼내 이어서", C_SH),
         ('git add login.md<br>git commit -m "feat: 비밀번호 찾기 추가"', "마저 하고 커밋", BL), ("git push origin main", "올리기", PUR)]
tf.append('<div style="position:absolute;left:96px;top:240px;width:1000px;height:760px;display:flex;flex-direction:column;gap:16px">')
for i, (cmd, d, c) in enumerate(steps, 1):
    tf.append(f'<div data-build-in="rise order {i}" style="flex:1;display:flex;flex-direction:row;gap:24px;align-items:center;background:#FFFFFF;border:2px solid {LINE};border-left:10px solid {c};border-radius:18px;padding:12px 28px">'
              + num(i, c, 52) + f'<div style="flex:1;display:flex;flex-direction:column;gap:4px">' + p(f"font-family:{MONO};font-size:24px;font-weight:700;line-height:1.35;color:{INK}", cmd) + p(f"font-size:22px;color:{SUB}", d) + '</div></div>')
tf.append('</div>')
tf += terminal([("$", "git log --oneline"), ("o", f"{H2} (HEAD -> main, origin/main) feat: 비밀번호 찾기 추가"), ("o", f"{HL} feat: 로그인 제목 바꾸기"), ("o", f"{H1} feat: 로그인 버튼 추가"), ("o", f"{H0} feat: 로그인 화면 추가")],
               left=1136, top=240, w=688, h=240, size=18, lh=1.5)
tf.append(f'<div data-build-in="rise order 6" style="position:absolute;left:1136px;top:520px;width:688px;height:480px;background:#FFFFFF;border:2px solid {LINE};border-radius:20px;padding:36px;display:flex;flex-direction:column;justify-content:center;gap:18px">'
          + f'<x-icon name="Users" style="width:52px;height:52px;color:{PUR}"></x-icon>'
          + p(f"font-size:32px;font-weight:700;line-height:1.4;color:{INK}", "merge 커밋 없이<br>한 줄로 이어졌어요")
          + p(f"font-size:26px;line-height:1.5;color:{SUB}", "lee의 커밋 위에 내 커밋이 올라갔어요.") + '</div>')
W("team-flow", tf, "오늘 팀 실습에서 그대로 쓰는 순서예요. 1번부터 3번이 stash, pull, pop이에요. 4번과 5번은 늘 하던 add, commit, push예요. 고치던 걸 먼저 커밋하고 pull해도 돼요. 그러면 03에서 본 merge 커밋이 하나 생겨요. stash를 쓰면 팀원 커밋 위에 내 커밋이 올라가서 git log가 한 줄로 이어져요. 커밋할 만큼 끝났으면 커밋, 덜 끝났으면 stash라고 기억하면 돼요.")

pc = [sec("pop-c")] + head("팀에서 쓰기 · 같은 줄을 고쳤다면", "pop 했더니 충돌이 났어요", RED)
pc += terminal([("$", "git stash pop"), ("o", "Auto-merging login.md"), ("r", "CONFLICT (content): Merge conflict in login.md"), ("o", "On branch main"), ("o", "Unmerged paths:"),
                ("#", HINT_UN), ("#", '  (use "git add <file>..." to mark resolution)'), ("r", "\tboth modified:   login.md"), ("o", ""), ("H", "The stash entry is kept in case you need it again.")],
               left=96, top=240, w=1100, h=420, size=20, lh=1.4)
fl = [("o", "# 로그인 페이지"), ("o", "아이디"), ("o", "비밀번호"), ("o", "로그인 버튼"), ("c", "<<<<<<< Updated upstream"), ("o", "비밀번호 재설정"), ("c", "======="), ("o", "비밀번호 찾기 (이메일)"), ("c", ">>>>>>> Stashed changes")]
pc.append(f'<div style="position:absolute;left:1236px;top:240px;width:588px;height:420px;background:#FFFFFF;border:2px solid #E07A7A;border-radius:20px;padding:20px 28px;display:flex;flex-direction:column;gap:2px">'
          + p(f"font-family:{MONO};font-size:22px;font-weight:700;color:{INK};margin-bottom:8px", "login.md")
          + "".join(p(f"font-family:{MONO};font-size:21px;line-height:1.5;padding:0 8px;border-radius:4px;{'background:#FBE4E2;color:#7A1F1F;font-weight:700' if k == 'c' else 'color:' + INK}", e(l)) for k, l in fl) + '</div>')
pc.append('<div style="position:absolute;left:96px;top:700px;width:1728px;height:300px;display:flex;flex-direction:row;gap:24px">')
for i, (t1, t2, c) in enumerate([("Updated upstream", "pull로 받은 쪽<br>lee가 고친 줄", PUR), ("Stashed changes", "서랍에서 꺼낸 쪽<br>내가 고친 줄", C_SH), ("서랍에 남아 있어요", "충돌이 나면 pop이 서랍을<br>비우지 않아요", RED)], 1):
    pc.append(f'<div data-build-in="rise order {i}" style="flex:1;display:flex;flex-direction:column;gap:12px;background:#FFFFFF;border:2px solid {LINE};border-top:8px solid {c};border-radius:18px;padding:28px 32px">'
              + p(f"font-family:{MONO if i < 3 else SANS};font-size:28px;font-weight:700;color:{c}", t1) + p(f"font-size:26px;line-height:1.45;color:{SUB}", t2) + '</div>')
pc.append('</div>')
W("pop-c", pc, "이번엔 lee가 비밀번호 찾기를 비밀번호 재설정으로 바꿔 push했고, 나는 같은 줄에 (이메일)을 붙이던 중이었어요. stash와 pull까지는 잘 되고 pop에서 충돌이 나요. 03에서 본 충돌 표시와 같아요. 다만 이름이 HEAD 대신 Updated upstream, 브랜치 이름 대신 Stashed changes로 나와요. 위가 받은 것, 아래가 내 것이에요. 충돌이 나면 서랍의 내용이 지워지지 않고 남아 있어요. 실수해도 다시 꺼낼 수 있게 지켜 주는 거예요.")

pr = [sec("pop-r")] + head("팀에서 쓰기 · 충돌 풀기", "03처럼 풀고, 서랍을 비워요", RED)
rsteps = [("파일을 고쳐요", "표시 줄 세 개를 지우고<br>남길 내용으로", None), ("git add login.md", "다 풀었다고 알려요", None), ("git stash drop", "남아 있던 서랍을 비워요", C_SH),
          ('git commit -m "..."<br>git push origin main', "늘 하던 대로", None)]
pr.append('<div style="position:absolute;left:96px;top:240px;width:880px;height:760px;display:flex;flex-direction:column;gap:16px">')
for i, (cmd, d, c) in enumerate(rsteps, 1):
    cc = c or "#6A7180"
    pr.append(f'<div data-build-in="rise order {i}" style="flex:1;display:flex;flex-direction:row;gap:24px;align-items:center;background:#FFFFFF;border:2px solid {LINE};border-left:10px solid {cc};border-radius:18px;padding:12px 28px">'
              + num(i, cc, 52) + f'<div style="flex:1;display:flex;flex-direction:column;gap:4px">' + p(f"font-family:{MONO if cmd.startswith('git') else SANS};font-size:26px;font-weight:700;line-height:1.35;color:{INK}", cmd) + p(f"font-size:22px;color:{SUB}", d) + '</div></div>')
pr.append('</div>')
pr += terminal([("$", "cat login.md"), ("o", "# 로그인 페이지"), ("o", "아이디"), ("o", "비밀번호"), ("o", "로그인 버튼"), ("o", "비밀번호 재설정 (이메일)"), ("$", "git add login.md"), ("$", "git stash drop"),
                ("H", "Dropped refs/stash@{0} (30ebc16b62d989d22d6cf5dc856d28b138dee3ba)"), ("$", "git stash list"), ("$", 'git commit -m "feat: 비밀번호 재설정에 이메일 안내 추가"'),
                ("o", f"[main {H3}] feat: 비밀번호 재설정에 이메일 안내 추가"), ("$", "git push origin main"), ("o", f"   {HL2}..{H3}  main -> main")],
               left=1016, top=240, w=808, h=760, size=19, lh=1.5)
W("pop-r", pr, "푸는 법은 03과 같아요. 표시 줄 세 개를 지우고 남길 내용으로 고친 뒤 git add해요. 여기서는 둘을 합쳐 비밀번호 재설정 (이메일)로 했어요. 그다음이 stash에만 있는 단계예요. 충돌 때문에 서랍에 남은 걸 git stash drop으로 지워요. drop은 꺼내지 않고 버리는 명령이라 이미 파일에 반영한 뒤에만 써요. git stash list에 아무것도 안 나오면 서랍이 빈 거예요. push 출력의 첫 줄 To https://github.com/kim/hello-git.git은 화면 때문에 뺐어요.")

ch_ = [sec("choose")] + head("팀에서 쓰기 · 정리", "고치던 게 있을 때: 버릴까, 치울까, 남길까", PUR)
opts = [("Wrench", C_RS, "버리기", "필요 없는 변경", "git restore 파일", "되찾을 수 없어요"),
        ("Archive", C_SH, "잠깐 치우기", "덜 끝났는데 pull, checkout 해야 할 때", "git stash<br>git stash pop", "내 컴퓨터에만 있어요"),
        ("Database", BL, "남기기", "커밋할 만큼 끝났을 때", 'git add 파일<br>git commit -m "..."', "기록에 남아요")]
for i, (ic, c, h, when, cmd, note) in enumerate(opts):
    x = 96 + i * 592
    ch_.append(f'<div data-build-in="rise order {i+1}" style="position:absolute;left:{x}px;top:240px;width:544px;height:700px;background:#FFFFFF;border:2px solid {LINE};border-top:10px solid {c};border-radius:20px;padding:40px 36px;display:flex;flex-direction:column;gap:20px">'
               f'<x-icon name="{ic}" style="width:64px;height:64px;color:{c}"></x-icon>'
               + p(f"font-size:44px;font-weight:900;color:{c}", h) + p(f"font-size:28px;line-height:1.45;color:{INK}", when) + '<div style="flex:1"></div>'
               + p(f"font-family:{MONO};font-size:26px;font-weight:700;line-height:1.5;color:{INK};background:#F6F5F1;padding:16px 20px;border-radius:12px", cmd)
               + p(f"font-size:24px;color:{SUB}", note) + '</div>')
W("choose", ch_, "pull이나 checkout이 막혔을 때 고르는 법이에요. 고친 게 필요 없으면 restore로 버려요. 덜 끝났으면 stash로 치웠다가 pop으로 꺼내요. 끝났으면 커밋해요. 어느 쪽인지 모르겠으면 stash가 가장 안전해요. 지우지 않고 서랍에 넣어 두니까요.")

# ---------- part 6: trouble ----------
tb = [sec("t-1")] + head("막힐 때", "이런 메시지가 나와요", "#1E3F8F")
cases = [("No local changes to save", "고친 게 없거나, 새 파일만 있어요. 새 파일은 add해야 서랍에 들어가요", "git add 파일<br>git stash"),
         ("stash list에 여러 줄이 있어요", "꺼내는 걸 잊었어요. 맨 위 {0}부터 하나씩 꺼내요", "git stash pop"),
         ("CONFLICT ... The stash entry is kept", "같은 줄을 둘 다 고쳤어요. 21쪽처럼 풀어요", "git add 파일<br>git stash drop"),
         ("error: pathspec 'signup2.md' did not match", "파일 이름이 틀렸어요. status로 이름을 확인해요", "git status")]
tb.append(f'<div style="position:absolute;left:96px;top:240px;width:1728px;height:760px;display:flex;flex-direction:column;gap:20px">')
for i, (q, a_, cmd) in enumerate(cases, 1):
    tb.append(f'<div data-build-in="rise order {i}" style="flex:1;display:flex;flex-direction:row;gap:32px;align-items:center;background:#FFFFFF;border:2px solid {LINE};border-radius:20px;padding:16px 36px">'
              + num(i, "#1E3F8F", 56)
              + f'<div style="flex:1;display:flex;flex-direction:column;gap:8px">' + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{INK}", e(q)) + p(f"font-size:24px;color:{SUB}", e(a_)) + '</div>'
              + p(f"width:380px;flex:none;font-family:{MONO};font-size:26px;font-weight:700;line-height:1.5;color:{INK};background:#EEEFF2;padding:12px 20px;border-radius:12px", cmd) + '</div>')
tb.append('</div>')
W("t-1", tb, "1번은 새로 만든 파일만 있을 때 나요. Git이 아직 모르는 Untracked 파일은 stash에 들어가지 않아요. git add로 올린 뒤 stash하면 들어가요. 2번은 pop을 잊고 또 stash했을 때예요. 3번은 20쪽과 21쪽의 장면이에요. 4번은 restore에 없는 파일 이름을 적었을 때예요. 파일 이름은 Tab 키로 자동 완성하면 틀리지 않아요.")

# ---------- cheatsheet ----------
cs = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};padding:112px 128px;display:flex;flex-direction:column;gap:40px">',
      f'<h2 style="font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>', '<div style="display:flex;flex-direction:row;gap:24px;flex:1">']
cards = [("버리기", C_RS, "git restore 파일<br><br>먼저 git diff<br>되찾을 수 없음"),
         ("add 취소", C_UN, "git restore --staged 파일<br><br>내용은 그대로"),
         ("잠깐 치우기", C_SH, "git stash<br>git stash list<br>git stash pop"),
         ("pop 충돌", RED, "파일 고치기<br>git add 파일<br>git stash drop")]
for h, hc, body in cards:
    cs.append(f'<div style="flex:1;display:flex;flex-direction:column;gap:16px;background:#FFFFFF;border:2px solid {LINE};border-top:10px solid {hc};border-radius:20px;padding:32px 28px">'
              f'<h3 style="font-size:32px;font-weight:700;color:{hc}">{h}</h3>'
              f'<p style="font-family:{MONO};font-size:26px;line-height:1.7;color:{INK}">{body}</p></div>')
cs += ['</div>', f'<p style="font-size:28px;font-weight:700;color:{INK}">막히면 git status의 괄호 안 안내부터 읽어요. 팀에서는 stash, pull, pop, commit, push 순서예요.</p>']
W("cheatsheet", cs, "수업 끝에 이 장을 띄워 두고, 팀 레포에서 pull이 막힌 상황을 한 번 더 만들어 직접 풀어 보게 하세요. 세 명령 모두 커밋하기 전의 변경만 다뤄요. 커밋한 뒤의 되돌리기는 02와 03의 reset, revert를 써요.")
print("ok")
