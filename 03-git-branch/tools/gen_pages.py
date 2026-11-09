# Generates the hand-drawn pages of the branch deck (cover, toc, concept, PR, error pages).
# Usage: python3 tools/gen_pages.py slides
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from highlight import spot, spot_off, cursor, cursor_off, ring, box, underline  # noqa: E402
OUT = sys.argv[1]
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
# The player shows the first sentence of a note in bold, so each note starts with the slide's point.
LEAD = {'toc': '오늘은 브랜치를 만들고, 합치고, 되돌리고, 충돌을 푸는 순서로 가요.', 'pr-github': 'Pull Request 화면에서는 제목, 합칠 방향, 설명, 바뀐 줄을 차례로 확인하고 합쳐요.', 'sc-adjacent': '바로 붙은 두 줄을 각자 고치면 다른 줄이어도 충돌이 나요.', 'sc-delete': '한쪽이 지운 파일을 다른 쪽이 고치면 modify/delete 충돌이 나요.', 'rs-delete': 'deleted by them이면 git rm으로 지우거나 git add로 남긴 뒤 커밋해요.', 'sc-addadd': '두 브랜치가 같은 이름의 새 파일을 따로 만들면 add/add 충돌이 나요.', 'sc-pull': 'pull 설정이 없으면 갈라진 상태에서 pull이 fatal로 멈춰요.', 'pull-config': 'git config --global pull.rebase false를 한 번 쳐 두면 pull이 merge로 합쳐요.', 'rs-pull': '설정한 뒤 다시 pull하면 시나리오 1과 같은 충돌 표시가 나와요.', 'sc-pr': 'PR을 올린 사이 main이 같은 줄을 바꾸면 PR 화면에 충돌이 떠요.', 'cheatsheet': '오늘 배운 명령을 브랜치, 합치기, 충돌, GitHub 네 묶음으로 모았어요.'}
def W(name, s):
    if name in LEAD:
        s = s.replace("<aside>", "<aside>" + LEAD[name] + " ", 1)
    open(os.path.join(OUT, name + ".html"), "w").write(s.strip() + "\n")
def sec(i, bg="#F6F5F1", extra=""):
    return f'<section id="{i}" data-transition="fade" style="background:{bg};color:#1D2330;font-family:{SANS};padding:96px;display:flex;flex-direction:column{extra}">'
def head(eyebrow, title, color="#2459C9", top=72):
    return (f'<p style="position:absolute;left:96px;top:{top}px;width:1728px;font-size:26px;font-weight:700;color:{color}">{eyebrow}</p>\n'
            f'<h2 style="position:absolute;left:96px;top:{top+50}px;width:1728px;font-size:60px;font-weight:700;line-height:1.15;color:#1D2330">{title}</h2>')
def node(x, y, color, r=20, kind="n", attrs=""):
    st = f"background:#FFFFFF;border:7px solid {color}" if kind == "merge" else f"background:{color};border:4px solid {color}"
    return f'<div{attrs} style="position:absolute;left:{x-r}px;top:{y-r}px;width:{2*r}px;height:{2*r}px;border-radius:50%;{st}"></div>'
def hline(x1, x2, y, color, attrs=""):
    return f'<div{attrs} style="position:absolute;left:{x1}px;top:{y-3}px;width:{x2-x1}px;height:6px;background:{color}"></div>'
def conn(x1, y1, x2, y2, color, attrs=""):
    return f'<x-connector{attrs} x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" style="color:{color};border-width:6px"></x-connector>'
def pill(x, y, text, kind="main", attrs=""):
    w = round(len(text) * 14.5 + 28)
    st = {"main": "background:#2459C9;color:#FFFFFF", "green": "background:#1F8A4C;color:#FFFFFF", "orange": "background:#B26A00;color:#FFFFFF",
          "head": "background:#1D2330;color:#F6F5F1", "origin": "background:#E7DEFC;color:#4A2FA8;border:2px solid #8E6FEA"}[kind]
    return f'<p{attrs} style="position:absolute;left:{x - w//2}px;top:{y}px;width:{w}px;font-family:{MONO};font-size:24px;font-weight:700;line-height:1.5;text-align:center;border-radius:8px;{st}">{text}</p>'
def code(text, bg="#EEEFF2", color="#1D2330", size=24):
    return f'<p style="font-family:{MONO};font-size:{size}px;font-weight:700;color:{color};background:{bg};padding:10px 16px;border-radius:10px">{text}</p>'
BL, BLL, GR, GRL, OR, ORL = "#2459C9", "#9DB8F2", "#1F8A4C", "#9ED3B4", "#B26A00", "#E4C08A"
HAIR = "#D9D6CD"   # 2px hairline that separates groups instead of a bordered card (Stageshow: compose, don't box)
def vrule(x, top, h, attrs=""):
    return f'<div{attrs} style="position:absolute;left:{x}px;top:{top}px;width:2px;height:{h}px;background:{HAIR}"></div>'

# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:#1D2330;color:#F6F5F1;font-family:{SANS};padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
 '<p style="font-size:28px;font-weight:700;color:#8FB3FF;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
 '<h1 style="font-size:104px;font-weight:900;line-height:1.1;color:#F6F5F1">Git 브랜치,<br>눈으로 보기</h1>',
 '<p style="font-size:40px;line-height:1.4;color:#BFC6D4">따로 작업하고, 합치고,<br>충돌을 푸는 법</p>']
# decorative graph on the right
y0, y1 = 560, 400
cov += [hline(1100, 1760, y0, "#5B7BC0"), conn(1260, y0, 1380, y1, "#4E9E70"), hline(1380, 1540, y1, "#4E9E70"), conn(1540, y1, 1660, y0, "#4E9E70")]
for x in (1100, 1260, 1660, 1760):
    cov.append(node(x, y0, "#8FB3FF", 24, "merge" if x == 1660 else "n"))
for x in (1380, 1540):
    cov.append(node(x, y1, "#7FD18B", 24))
cov += [pill(1540, y1 - 72, "feature/login", "green"), pill(1760, y0 + 44, "main", "main")]
cov += ['<aside>브랜치를 점(커밋)과 이름표(브랜치) 그림으로 배워요. 02 Git 기본 흐름에서 쓰던 hello-git 저장소로 이어서 실습해요. 명령마다 이름표와 HEAD가 어디로 움직이는지 봐요.</aside>', '</section>']
W("cover", "\n".join(cov))

# ---------- toc ----------
parts = [("Lightbulb", "#3A4150", "브랜치란?", "점, 이름표, HEAD", "3–6쪽"),
         ("Link", "#1A7340", "만들고 옮기기", "branch · checkout · switch", "7–14쪽"),
         ("Activity", "#2459C9", "합치기", "merge · 이름 규칙", "15–19쪽"),
         ("Activity", "#8A5200", "갈라진 길", "merge 커밋", "20–25쪽"),
         ("Wrench", "#8A5200", "되돌리기", "git reset 옵션 세 가지", "26–38쪽"),
         ("Warning", "#A33131", "충돌 풀기", "표시 읽고 고치기", "39–45쪽"),
         ("Cloud", "#5A3BB8", "GitHub에서 함께", "push · Pull Request", "46–56쪽"),
         ("Warning", "#A33131", "충돌 시나리오", "다섯 가지 상황", "57–68쪽"),
         ("Wrench", "#1E3F8F", "막힐 때", "자주 나는 에러", "69–71쪽")]
t = [f'<section id="toc" data-transition="fade" style="background:#F6F5F1;color:#1D2330;font-family:{SANS};padding:96px 128px;display:flex;flex-direction:column;gap:40px">',
     '<h2 style="font-size:64px;font-weight:700;line-height:1.15;color:#1D2330">오늘의 순서</h2>',
     '<div style="display:grid;grid-template-columns:repeat(3,1fr);column-gap:64px;flex:1">']
for i, (ic, c, h, sub, pg) in enumerate(parts, 1):
    t.append(f'<div style="display:flex;flex-direction:row;gap:28px;align-items:flex-start;border-top:2px solid {HAIR};padding:28px 0 0 0">'
             f'<p style="width:56px;flex:none;font-size:56px;font-weight:900;line-height:1.2;margin-top:-8px;color:{c}">{i}</p>'
             f'<div style="display:flex;flex-direction:column;gap:8px"><h3 style="font-size:36px;font-weight:700;line-height:1.2;color:#1D2330">{h}</h3>'
             f'<p style="font-size:26px;line-height:1.4;color:#4A5262">{sub}</p><p style="font-size:24px;color:#9AA0AB">{pg}</p></div></div>')
t += ['</div>', '<p style="font-size:26px;color:#4A5262">마지막 72쪽은 한 장 요약이에요.</p>',
      '<aside>02와 같은 hello-git 저장소로 이어서 실습해요. 2~6부는 커밋 그래프 하나가 계속 자라는 이야기예요. 7부는 충돌이 나는 다른 상황을 따로 모았어요.</aside>', '</section>']
W("toc", "\n".join(t))

# ---------- why ----------
w = [sec("why"), head("브랜치란?", "왜 브랜치를 쓸까요?")]
w.append('<div id="why-a" style="position:absolute;left:96px;top:250px;width:840px;height:620px;border-radius:24px"></div>')
w.append('<div id="why-b" style="position:absolute;left:984px;top:250px;width:840px;height:620px;border-radius:24px"></div>')
w.append(vrule(959, 280, 560))
w += [spot(1, target="why-a", pad=6, r=26), spot(2, target="why-b", pad=6, r=26), spot_off(3)]
w.append(f'<div style="position:absolute;left:136px;top:296px;width:760px;display:flex;flex-direction:row;gap:14px;align-items:center"><x-icon name="Warning" style="width:44px;height:44px;color:#A33131"></x-icon><h3 style="font-size:34px;font-weight:700;color:#A33131">모두 main에 바로 커밋</h3></div>')
w.append(f'<div style="position:absolute;left:1024px;top:296px;width:760px;display:flex;flex-direction:row;gap:14px;align-items:center"><x-icon name="CheckCircle" style="width:44px;height:44px;color:#1A7340"></x-icon><h3 style="font-size:34px;font-weight:700;color:#1A7340">각자 브랜치에서 작업</h3></div>')
cols = [BL, GR, OR, GR, BL, OR, GR]
y = 560
w.append(hline(176, 856, y, "#D5D9E0"))
for i, c in enumerate(cols):
    w.append(node(176 + i * 113, y, c, 22))
w.append(pill(856, y + 40, "main", "main"))
w.append('<div style="position:absolute;left:136px;top:720px;width:760px;display:flex;flex-direction:column;gap:14px">'
         '<p style="font-size:32px;line-height:1.4;color:#1D2330">반쯤 만든 기능이 main에 섞여요</p>'
         '<p style="font-size:32px;line-height:1.4;color:#1D2330">누구 작업이 문제인지 찾기 어려워요</p></div>')
ym, yg, yo = 600, 450, 450
w += [hline(1064, 1744, ym, BLL), conn(1150, ym, 1250, yg, GRL), hline(1250, 1370, yg, GRL), conn(1370, yg, 1470, ym, GRL),
      conn(1470, ym, 1570, yo, ORL), hline(1570, 1640, yo, ORL), conn(1640, yo, 1744, ym, ORL)]
for x in (1064, 1150, 1470, 1744):
    w.append(node(x, ym, BL, 22, "merge" if x in (1470, 1744) else "n"))
for x in (1250, 1370):
    w.append(node(x, yg, GR, 22))
for x in (1570, 1640):
    w.append(node(x, yo, OR, 22))
w += [pill(1310, yg - 66, "feature/login", "green"), pill(1605, yo - 66, "fix/typo", "orange"), pill(1744, ym + 40, "main", "main")]
w.append('<div style="position:absolute;left:1024px;top:720px;width:760px;display:flex;flex-direction:column;gap:14px">'
         '<p style="font-size:32px;line-height:1.4;color:#1D2330">다 만든 다음에 main으로 합쳐요</p>'
         '<p style="font-size:32px;line-height:1.4;color:#1D2330">main은 늘 잘 돌아가는 상태로 남아요</p></div>')
w.append('<p data-build-in="rise order 3" style="position:absolute;left:96px;top:916px;width:1728px;font-size:34px;font-weight:700;color:#1D2330">브랜치는 본 줄기(main)를 그대로 두고 옆으로 갈래를 내서 작업하는 방법이에요.</p>')
w.append('<aside>왼쪽은 세 사람이 main 하나에 번갈아 커밋한 모습이에요. 색이 섞여 있죠. 오른쪽은 각자 갈래(브랜치)에서 작업하고 끝나면 합친 모습이에요. 흰 점은 두 줄기를 합친 커밋이에요. 혼자 일할 때도 실험은 브랜치에서 하면 main을 망가뜨릴 걱정이 없어요.</aside></section>')
W("why", "\n".join(w))

# ---------- naming ----------
n = [sec("naming"), head("합치기 · 브랜치 이름", "브랜치 이름은 타입/하는 일")]
n.append(f'<div style="position:absolute;left:96px;top:250px;width:1728px;height:150px;background:#1D2330;border-radius:24px;display:flex;flex-direction:row;align-items:center;gap:8px;padding:0 48px">'
         f'<p style="font-family:{MONO};font-size:56px;font-weight:700;color:#7FD18B">feature</p>'
         f'<p style="font-family:{MONO};font-size:56px;font-weight:700;color:#BFC6D4">/</p>'
         f'<p style="font-family:{MONO};font-size:56px;font-weight:700;color:#F2C46D">login-button</p><div style="flex:1"></div>'
         f'<p style="font-size:26px;color:#BFC6D4">타입 · 슬래시 · 하는 일(소문자, 하이픈)</p></div>')
types = [("feature/", "새 기능", "feature/login-button", "#1A7340"), ("fix/", "버그 수정", "fix/login-error", "#A33131"),
         ("docs/", "문서", "docs/login-guide", "#1E3F8F"), ("refactor/", "구조 개선", "refactor/user-api", "#8A5200"),
         ("chore/", "설정, 패키지", "chore/eslint-setup", "#4A5262")]
n.append('<div style="position:absolute;left:96px;top:440px;width:1728px;display:flex;flex-direction:column">')
for k, (a, b, c, col) in enumerate(types):
    n.append(f'<div{" id=\"nm-feature\"" if k == 0 else ""} style="display:flex;flex-direction:row;align-items:center;height:84px;padding:0 24px;border-bottom:2px solid {HAIR}">'
             f'<p style="width:360px;flex:none;font-family:{MONO};font-size:40px;font-weight:700;color:{col}">{a}</p>'
             f'<p style="width:420px;flex:none;font-size:34px;font-weight:700;color:#1D2330">{b}</p>'
             f'<p style="font-family:{MONO};font-size:30px;color:#4A5262">{c}</p></div>')
n.append('</div>')
n.append(spot(1, target="nm-feature", pad=8, r=22))
n.append(spot_off(2))
n.append('<p data-build-in="rise order 2" style="position:absolute;left:96px;top:916px;width:1728px;font-size:34px;font-weight:700;color:#1D2330">새 기능은 feature/예요. 커밋 메시지 타입 feat:와 헷갈리지 않게 봐요.</p>')
n.append('<aside>브랜치 이름 앞부분만 봐도 무슨 작업인지 알 수 있어요. 새 기능 브랜치는 feature/로 시작하고, 그 브랜치에서 하는 커밋 메시지는 feat:로 써요. fix, docs, refactor, chore는 커밋 메시지와 같은 말이에요. 팀에 정해진 규칙이 있으면 그걸 따라요.</aside></section>')
W("naming", "\n".join(n))
n = [sec("naming-ok"), head("합치기 · 브랜치 이름", "이렇게 짓고, 이건 피해요")]
n.append('<div style="position:absolute;left:96px;top:250px;width:1728px;height:620px;display:flex;flex-direction:row;gap:24px">')
n.append(f'<div style="flex:1;display:flex;flex-direction:column;gap:28px;padding:40px 44px 40px 0">'
         f'<div style="display:flex;flex-direction:row;gap:12px;align-items:center"><x-icon name="CheckCircle" style="width:44px;height:44px;color:#1A7340"></x-icon><p style="font-size:34px;font-weight:700;color:#1A7340">이렇게</p></div>'
         f'<p style="font-family:{MONO};font-size:40px;line-height:1.5;color:#1D2330">feature/login-button</p>'
         f'<p style="font-family:{MONO};font-size:40px;line-height:1.5;color:#1D2330">fix/12-login-error<br><span style="font-family:{SANS};font-size:30px;color:#6A7180">이슈 12번</span></p></div>')
n.append(vrule(863, 30, 560))
n.append(f'<div style="flex:1;display:flex;flex-direction:column;gap:28px;padding:40px 0 40px 44px">'
         f'<div style="display:flex;flex-direction:row;gap:12px;align-items:center"><x-icon name="Warning" style="width:44px;height:44px;color:#A33131"></x-icon><p style="font-size:34px;font-weight:700;color:#A33131">이건 피해요</p></div>'
         f'<p style="font-family:{MONO};font-size:40px;line-height:1.5;color:#A33131;text-decoration:line-through">login, 내작업, final2</p><p style="font-family:{SANS};font-size:30px;line-height:1.2;color:#6A7180;margin-top:-20px">무슨 일인지 모름</p>'
         f'<p style="font-family:{MONO};font-size:40px;line-height:1.5;color:#A33131;text-decoration:line-through">Feature/Login Button</p><p style="font-family:{SANS};font-size:30px;line-height:1.2;color:#6A7180;margin-top:-20px">대문자, 띄어쓰기</p></div>')
n.append('</div>')
n.append('<p style="position:absolute;left:96px;top:916px;width:1728px;font-size:34px;font-weight:700;color:#1D2330">소문자와 하이픈(-)만 쓰고, 무슨 일인지 이름에 적어요.</p>')
n.append('<aside>띄어쓰기는 명령어에서 이름이 끊기니 하이픈(-)으로 이어요. 대문자는 운영체제에 따라 헷갈릴 수 있어 소문자로 통일해요. 이슈 번호를 쓰는 팀이면 fix/12-login-error처럼 앞에 붙여요. 팀에 정해진 규칙이 있으면 그걸 따라요.</aside></section>')
W("naming-ok", "\n".join(n))

# ---------- merge-kinds ----------
m = [sec("merge-kinds", "#ECEAE3"), head("개념 정리", "merge는 두 가지 모습으로 끝나요")]
for i, (title, sub, col) in enumerate([("Fast-forward", "main에 새 커밋이 없을 때<br>이름표만 앞으로 당겨요", BL), ("merge 커밋", "양쪽에 새 커밋이 있을 때<br>둘을 잇는 커밋을 새로 만들어요", OR)]):
    L = 96 + i * 888
    m.append(f'<h3 style="position:absolute;left:{L+40}px;top:296px;width:760px;font-size:36px;font-weight:700;color:{col}">{title}</h3>')
    m.append(f'<p style="position:absolute;left:{L+40}px;top:720px;width:760px;font-size:28px;line-height:1.45;color:#1D2330">{sub}</p>')
m.append(vrule(959, 280, 560))
# FF
ym, yu = 560, 430
m += [hline(176, 400, ym, BLL), conn(400, ym, 520, yu, GRL), hline(520, 660, yu, GRL)]
for x in (176, 288, 400): m.append(node(x, ym, BL, 22))
for x in (520, 660): m.append(node(x, yu, GR, 22))
m += [pill(400, ym + 40, "main", "main", ' data-build-in="fade order 1"' if False else ''),
      pill(660, yu - 66, "feature", "green")]
m.append(pill(660, yu - 110, "main", "main", ' data-build-in="rise order 1"'))
m.append(f'<p data-build-in="fade order 1" style="position:absolute;left:440px;top:600px;width:360px;font-size:24px;font-weight:700;color:#1E3F8F">main → 이 커밋으로 이동</p>')
# merge commit
o0 = 984
m += [hline(o0 + 80, o0 + 760, ym, BLL), conn(o0 + 304, ym, o0 + 424, yu, ORL), hline(o0 + 424, o0 + 544, yu, ORL)]
m.append(conn(o0 + 544, yu, o0 + 664, ym, ORL, ' data-build-in="fade order 2"'))
for x in (80, 192, 304, 474): m.append(node(o0 + x, ym, BL, 22))
for x in (424, 544): m.append(node(o0 + x, yu, OR, 22))
m.append(node(o0 + 664, ym, BL, 22, "merge", ' data-build-in="pop order 2"'))
m.append(pill(o0 + 544, yu - 66, "docs", "orange"))
m.append(pill(o0 + 664, ym + 40, "main", "main", ' data-build-in="rise order 2"'))
m.append('<p style="position:absolute;left:96px;top:900px;width:1728px;font-size:28px;font-weight:700;color:#1D2330">명령은 똑같이 git merge 브랜치이름. 어느 쪽이 될지는 Git이 정해요.</p>')
m.append('<aside>왼쪽은 feature/login, 오른쪽은 docs/login-guide를 합친 모습이에요. merge 커밋(흰 점)은 부모가 둘이라 두 줄기의 기록을 모두 품고 있어요. 팀 작업에서는 GitHub의 Pull Request로 합칠 때 대부분 오른쪽처럼 merge 커밋이 생겨요.</aside></section>')
W("merge-kinds", "\n".join(m))

# ---------- conflict-read ----------
c = [sec("conflict-read", "#ECEAE3"), head("충돌 풀기", "충돌 표시 읽는 법", "#A33131")]
lines = [("<<<<<<< HEAD", "#F28B82"), ("# 로그인 페이지", "#8FB3FF"), ("=======", "#F28B82"), ("# 로그인하기", "#7FD18B"), (">>>>>>> feature/login-title", "#F28B82"), ("아이디", "#D8DEE9"), ("비밀번호", "#D8DEE9")]
c.append(f'<div style="position:absolute;left:96px;top:260px;width:760px;height:600px;background:#1B2029;border-radius:24px"></div>')
c.append(f'<p style="position:absolute;left:136px;top:290px;width:600px;font-size:24px;color:#9AA3B5">login.md</p>')
for i, (tx, col) in enumerate(lines):
    c.append(f'<p style="position:absolute;left:136px;top:{350 + i*64}px;width:680px;font-family:{MONO};font-size:36px;font-weight:700;line-height:1.4;color:{col}">{tx}</p>')
notes = [(0, 1, "#2459C9", "지금 내 브랜치(main) 내용"), (3, 4, "#1F8A4C", "합치려는 브랜치(feature/login-title) 내용")]
for k, (a, b, col, txt) in enumerate(notes):
    y1, y2 = 350 + a*64, 350 + b*64 + 50
    c.append(f'<div data-build-in="fade order {k+1}" style="position:absolute;left:880px;top:{y1}px;width:10px;height:{y2-y1}px;background:{col};border-radius:5px"></div>')
    c.append(f'<p data-build-in="fade order {k+1}" style="position:absolute;left:912px;top:{(y1+y2)//2 - 20}px;width:420px;font-size:28px;font-weight:700;color:{col}">{txt}</p>')
c.append(f'<div data-build-in="rise order 3" style="position:absolute;left:1360px;top:260px;width:464px;height:600px;border-left:2px solid #C9C5BA;padding:8px 0 8px 40px;display:flex;flex-direction:column;gap:22px">'
         f'<h3 style="font-size:32px;font-weight:700;color:#1D2330">푸는 순서</h3>'
         f'<p style="font-size:26px;line-height:1.4;color:#1D2330"><span style="color:#A33131">1</span> 남길 내용으로 고치기<br><span style="color:#6A7180">둘 다 남겨도 돼요</span></p>'
         f'<p style="font-size:26px;line-height:1.4;color:#1D2330"><span style="color:#A33131">2</span> 표시 세 줄 지우고 저장</p>'
         f'<p style="font-family:{MONO};font-size:26px;line-height:1.4;color:#1D2330"><span style="color:#A33131;font-family:{SANS}">3</span> git add login.md</p>'
         f'<p style="font-family:{MONO};font-size:26px;line-height:1.4;color:#1D2330"><span style="color:#A33131;font-family:{SANS}">4</span> git commit -m "..."</p></div>')
c.append('<p style="position:absolute;left:96px;top:900px;width:1728px;font-size:26px;font-weight:700;color:#A33131">&lt;&lt;&lt;&lt;&lt;&lt;&lt;, =======, &gt;&gt;&gt;&gt;&gt;&gt;&gt; 줄이 남은 채로 커밋하지 않아요.</p>')
c.append('<aside>HEAD는 지금 서 있는 브랜치예요. 위쪽이 내 것, 아래쪽이 가져오려는 것이에요. VS Code로 열면 Accept Current Change(내 것), Accept Incoming Change(가져온 것), Accept Both Changes(둘 다) 버튼이 떠서 클릭으로 골라도 돼요. 고른 뒤에도 저장하고 add, commit 하는 건 똑같아요.</aside></section>')
W("conflict-read", "\n".join(c))

# ---------- pr-flow ----------
f = [sec("pr-flow"), head("GitHub에서 함께", "팀에서는 이 순서로 일해요", "#6B47D6")]
steps = [("Link", "git checkout<br>-b feature/<br>login-button", "브랜치 만들기", "#2459C9", "#F0F5FE", "#5B8DEF"),
         ("Code", "add, commit", "작업하고 커밋", "#2459C9", "#F0F5FE", "#5B8DEF"),
         ("Cloud", "git push origin<br>feature/<br>login-button", "브랜치 올리기", "#2459C9", "#F0F5FE", "#5B8DEF"),
         ("Chat", "Pull Request", "합쳐 달라고 요청", "#5A3BB8", "#F6F2FE", "#9A7BF0"),
         ("Users", "리뷰 → Merge", "확인하고 합치기", "#5A3BB8", "#F6F2FE", "#9A7BF0"),
         ("Home", "git checkout main<br>git fetch origin<br>git pull origin main", "내 main 맞추기", "#2459C9", "#F0F5FE", "#5B8DEF")]
f.append('<div style="position:absolute;left:126px;top:425px;width:1668px;height:6px;background:#C9C5BA;border-radius:3px"></div>')
for i, (ic, cmd, lab, col, bg, bd) in enumerate(steps):
    L = 96 + i * 292
    f.append(f'<p data-build-in="rise order {(1, 1, 1, 2, 2, 3)[i]}" style="position:absolute;left:{L}px;top:398px;width:60px;height:60px;font-size:32px;font-weight:900;line-height:60px;text-align:center;color:#FFFFFF;background:{col};border-radius:30px">{i+1}</p>')
    f.append(f'<div data-build-in="rise order {(1, 1, 1, 2, 2, 3)[i]}" style="position:absolute;left:{L}px;top:500px;width:260px;display:flex;flex-direction:column;gap:16px">'
             f'<p style="font-size:32px;font-weight:700;line-height:1.3;color:#1D2330">{lab}</p>'
             f'<p style="font-family:{MONO};font-size:24px;line-height:1.45;font-weight:700;color:{col}">{cmd}</p></div>')
for L, w_, col, name in ((96, 844, "#5B8DEF", "내 컴퓨터"), (972, 552, "#9A7BF0", "GitHub 웹사이트"), (1556, 268, "#5B8DEF", "내 컴퓨터")):
    f.append(f'<div style="position:absolute;left:{L}px;top:316px;width:{w_}px;height:4px;background:{col};border-radius:2px"></div>')
    f.append(f'<p style="position:absolute;left:{L}px;top:264px;width:{w_}px;font-size:28px;font-weight:700;color:{"#5A3BB8" if "GitHub" in name else "#1E3F8F"}">{name}</p>')
f.append('<p style="position:absolute;left:96px;top:900px;width:1728px;font-size:32px;font-weight:700;color:#1D2330">main에는 직접 push하지 않아요. 6번을 마치면 다음 브랜치는 1번부터 다시 시작해요.</p>')
f.append('<aside>Pull Request(PR)는 "내 브랜치를 main에 합쳐 주세요"라는 요청서예요. 팀원이 바뀐 코드를 보고 의견을 남긴 뒤 합쳐요. 혼자 하는 프로젝트에서도 PR로 합치면 무엇을 언제 바꿨는지 기록이 깔끔하게 남아요.</aside></section>')
W("pr-flow", "\n".join(f))

# ---------- pr-github ----------
g = [sec("pr-github"), head("GitHub에서 함께", "Pull Request 화면에서 할 일", "#6B47D6")]
g.append('<div style="position:absolute;left:96px;top:260px;width:1100px;height:660px;background:#FFFFFF;border:2px solid #D0D7DE;border-radius:20px"></div>')
g.append(f'<p id="pr-title" style="position:absolute;left:136px;top:296px;width:1020px;font-size:36px;font-weight:700;color:#1D2330">feat: 로그인 버튼 추가 <span style="color:#6A7180">#1</span></p>')
g.append(f'<div id="pr-base" style="position:absolute;left:136px;top:366px;width:1020px;display:flex;flex-direction:row;gap:12px;align-items:center">'
         f'<p style="font-size:24px;font-weight:700;color:#FFFFFF;background:#1F8A4C;padding:4px 16px;border-radius:20px">Open</p>'
         f'<p style="font-family:{MONO};font-size:24px;color:#1D2330;background:#DCE7FB;padding:4px 12px;border-radius:8px">main</p>'
         f'<p style="font-size:26px;color:#6A7180">←</p>'
         f'<p style="font-family:{MONO};font-size:24px;color:#1D2330;background:#FBEBD3;padding:4px 12px;border-radius:8px">feature/login-button</p></div>')
g.append('<div id="pr-desc" style="position:absolute;left:136px;top:440px;width:1020px;height:150px;background:#F6F8FA;border:2px solid #D0D7DE;border-radius:12px;padding:20px 24px;display:flex;flex-direction:column;gap:8px">'
         '<p style="font-size:24px;font-weight:700;color:#1D2330">설명</p><p style="font-size:24px;color:#4A5262">login.md에 로그인 버튼 줄을 넣었어요.</p></div>')
g.append(f'<div id="pr-files" style="position:absolute;left:136px;top:614px;width:1020px;height:120px;background:#F6F8FA;border:2px solid #D0D7DE;border-radius:12px;padding:20px 24px;display:flex;flex-direction:column;gap:8px">'
         f'<p style="font-size:24px;font-weight:700;color:#1D2330">Files changed</p><p style="font-family:{MONO};font-size:24px;color:#1A7340">+ 로그인 버튼</p></div>')
g.append('<div id="pr-btns" style="position:absolute;left:136px;top:762px;width:1020px;display:flex;flex-direction:row;gap:16px;align-items:center">'
         '<p style="font-size:26px;font-weight:700;color:#FFFFFF;background:#1F8A4C;padding:12px 24px;border-radius:10px">Merge pull request</p>'
         '<p style="font-size:26px;font-weight:700;color:#1D2330;background:#F6F8FA;border:2px solid #D0D7DE;padding:10px 22px;border-radius:10px">Delete branch</p></div>')
anns = [(296, "제목: 커밋 메시지처럼 타입: 요약"), (366, "어디로 ← 무엇을 합치는지"), (440, "무엇을 왜 바꿨는지"), (614, "바뀐 줄 확인, 댓글로 리뷰"), (762, "합치고 나면 GitHub 브랜치 삭제")]
for i, (y, txt) in enumerate(anns):
    g.append(f'<div data-build-in="fade order {i+1}" style="position:absolute;left:1236px;top:{y}px;width:588px;display:flex;flex-direction:row;gap:14px;align-items:center">'
             f'<p style="width:44px;height:44px;flex:none;font-size:26px;font-weight:900;line-height:44px;text-align:center;color:#FFFFFF;background:#6B47D6;border-radius:22px">{i+1}</p>'
             f'<p style="font-size:26px;font-weight:700;color:#1D2330">{txt}</p></div>')
g += [spot(k + 1, target=t, pad=10, r=12, dim=0.5) for k, t in enumerate(["pr-title", "pr-base", "pr-desc", "pr-files", "pr-btns"])] + [spot_off(6)]
g.append('<aside>push 하면 GitHub 저장소 화면 위쪽에 Compare &amp; pull request 버튼이 떠요. 누르면 이 화면이 나와요. 화면 모양은 GitHub 업데이트에 따라 조금 다를 수 있어요. Merge pull request를 누르면 GitHub 안에서 merge 커밋이 생기고, 내 컴퓨터에는 다음 장처럼 pull로 받아요.</aside></section>')
W("pr-github", "\n".join(g))

# ---------- strategy ----------
s = [sec("strategy"), head("GitHub에서 함께 · 브랜치 전략", "우리는 GitHub Flow로 일해요", "#6B47D6")]
ym, yu = 500, 370
s.append(hline(160, 1760, ym, BLL))
br = [(300, 560, "feature/login", "green", GR, GRL), (720, 980, "fix/12-login-error", "orange", OR, ORL), (1140, 1440, "docs/login-guide", "green", GR, GRL)]
for k, (a, b, name, kind, col, light) in enumerate(br):
    s += [conn(a, ym, a + 90, yu, light), hline(a + 90, b - 90, yu, light), conn(b - 90, yu, b, ym, light)]
    s += [node(a + 90, yu, col, 18), node(b - 90, yu, col, 18), node(b, ym, BL, 20, "merge")]
    s.append(pill((a + b) // 2, yu - 62, name, kind))
for x in (160, 300, 720, 1140, 1760):
    s.append(node(x, ym, BL, 20))
s.append(pill(1760, ym + 36, "main", "main"))
rules = [("main은 늘 동작하는 상태.<br>직접 커밋하지 않아요", "Lock"), ("일 하나 = 브랜치 하나.<br>이름은 타입/하는 일", "Link"),
         ("작게 자주 Pull Request", "Chat"), ("merge 뒤 브랜치는 지워요", "CheckCircle")]
s.append(f'<div style="position:absolute;left:96px;top:640px;width:1728px;display:flex;flex-direction:row;gap:48px;border-top:2px solid {HAIR};padding-top:32px">')
for i, (txt, ic) in enumerate(rules):
    s.append(f'<div style="flex:1;display:flex;flex-direction:row;gap:16px">'
             f'<p style="font-size:30px;font-weight:900;line-height:1.4;color:#5A3BB8">{i+1}</p>'
             f'<p style="font-size:30px;font-weight:700;line-height:1.4;color:#1D2330">{txt}</p></div>')
s.append('</div>')
s.append('<p style="position:absolute;left:96px;top:916px;width:1728px;font-size:26px;color:#4A5262">Git Flow(develop, release 브랜치를 따로 두는 방식)는 배포 일정이 복잡한 회사에서 써요. 처음엔 GitHub Flow면 충분해요.</p>')
s.append('<aside>GitHub Flow는 main 하나와 짧게 쓰고 지우는 작업 브랜치로만 일하는 방식이에요. 갈래가 길어질수록 main과 멀어져 충돌이 커지니, 하루 이틀 안에 합칠 수 있는 크기로 나눠요. GitHub 저장소 설정에서 main 브랜치 보호(Branch protection)를 켜면 main에 직접 push를 막고 PR로만 합치게 할 수 있어요.</aside></section>')
W("strategy", "\n".join(s))

# ---------- errors ----------
# (x, y, w, h) of each error block for the pen box, measured in the built HTML. Change the error text, measure again.
ERR_BOX = {("err-name", 0): (154, 363, 764, 165), ("err-name", 1): (1002, 363, 764, 165),
           ("err-dirty", 0): (154, 363, 1612, 214), ("err-unmerged", 0): (154, 363, 1612, 174)}


def errpage(i, eyebrow, title, panels, aside):
    o = [f'<section id="{i}" data-transition="fade" style="background:#ECEAE3;color:#1D2330;font-family:{SANS};padding:112px 128px;display:flex;flex-direction:column;gap:40px">',
         f'<div style="display:flex;flex-direction:column;gap:12px"><p style="font-size:26px;font-weight:700;color:#A33131">{eyebrow}</p>'
         f'<h2 style="font-size:60px;font-weight:700;line-height:1.15;color:#1D2330">{title}</h2></div>',
         '<div style="display:flex;flex-direction:row;gap:32px;flex:1">']
    for k, (ic, h, err, why, fixes) in enumerate(panels):
        o.append(f'<div style="flex:1;display:flex;flex-direction:column;gap:20px;padding:32px">'
                 f'<div style="display:flex;flex-direction:row;gap:16px;align-items:center"><x-icon name="{ic}" style="width:48px;height:48px;color:#A33131"></x-icon><h3 style="font-size:34px;font-weight:700;color:#1D2330">{h}</h3></div>'
                 f'<p id="{i}-e{k}" style="font-family:{MONO};font-size:{26 if len(panels) > 1 else 28}px;line-height:1.45;color:#F28B82;background:#1B2029;padding:20px 24px;border-radius:12px">{err}</p>'
                 f'<p style="font-size:30px;line-height:1.45;color:#4A5262">{why}</p>'
                 f'<div data-build-in="rise order {len(panels) + 1}" style="display:flex;flex-direction:column;gap:12px;margin-top:28px;border-top:2px solid #C9C5BA;padding-top:32px">' + "".join(code(x, size=28) for x in fixes) + '</div></div>')
        if (i, k) in ERR_BOX:
            o.append(box(k + 1, *ERR_BOX[(i, k)], "#A33131"))
    o += ['</div>', f'<aside>{aside}</aside>', '</section>']
    W(i, "\n".join(o))

errpage("err-name", "에러 1 · 브랜치 이름", "옮기려는데, 만들려는데 안 돼요",
        [("Search", "없는 브랜치로 옮김", "$ git checkout feature/nope<br>error: pathspec 'feature/nope' did not match any file(s) known to git",
          "이름 오타이거나 아직 안 만든 브랜치예요", ["git branch", "git checkout -b feature/nope"]),
         ("Link", "이미 있는 이름으로 만듦", "$ git checkout -b feature/login<br>fatal: a branch named 'feature/login' already exists",
          "같은 이름이 벌써 있어요. -b 없이 옮겨 가요", ["git checkout feature/login"])],
        "pathspec 에러는 Git이 브랜치도 파일도 못 찾았다는 뜻이에요. git branch로 목록을 보고 철자를 확인해요. 새로 만들 생각이었다면 -b를 붙여요. already exists는 반대로 이미 있는 이름에 -b를 붙였을 때 나요.")
errpage("err-dirty", "에러 2 · 커밋 안 한 변경", "브랜치를 옮기려는데 막혀요",
        [("Warning", "고친 파일이 그대로 있음", "error: Your local changes to the following files would be overwritten by checkout:<br>&#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;login.md<br>Please commit your changes or stash them before you switch branches.<br>Aborting",
          "옮겨 가면 고친 내용이 덮어써져서 Git이 멈췄어요. 먼저 커밋하고 옮겨요", ["git add login.md", 'git commit -m "feat: ..."', "git checkout feature/login"])],
        "옮겨 갈 브랜치에서 같은 파일 내용이 다를 때만 나요. 고친 내용을 잃지 않게 지켜 주는 에러예요. 작업이 덜 끝났어도 지금 브랜치에 커밋해 두고 옮기면 돼요. 메시지에 나오는 stash(잠깐 치워 두기)는 07에서 배워요.")
errpage("err-unmerged", "에러 3 · 브랜치 지우기", "브랜치가 안 지워져요",
        [("Lock", "아직 합치지 않은 커밋이 있음", "$ git branch -d feature/login<br>error: the branch 'feature/login' is not fully merged.<br>If you are sure you want to delete it, run 'git branch -D feature/login'",
          "지우면 그 커밋을 잃을 수 있어서 Git이 멈췄어요", ["git checkout main", "git merge feature/login", "git branch -d feature/login"])],
        "-d는 합치지 않은 커밋이 있으면 지우지 않고 멈춰요. 먼저 main에 합친 뒤 지워요. 합치지 않고 버리는 방법은 08에서 다뤄요. GitHub에서 PR을 merge했는데도 이 에러가 나면, 먼저 git checkout main 후 git pull origin main으로 내 main을 최신으로 맞추고 다시 지워 봐요.")

# ---------- cheatsheet ----------
ch = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:#1D2330;font-family:{SANS};padding:112px 128px;display:flex;flex-direction:column;gap:40px">',
      '<h2 style="font-size:64px;font-weight:700;line-height:1.15;color:#1D2330">한 장 요약</h2>', '<div style="display:flex;flex-direction:row;gap:24px;flex:1">']
cards = [("브랜치", "#1A7340", "#FFFFFF", "#1D2330", "git branch<br>git branch 이름<br>git checkout 이름<br>git checkout -b 이름<br>git branch -d 이름<br><br>switch로 써도 돼요<br>git switch 이름<br>git switch -c 이름"),
         ("합치기", "#2459C9", "#FFFFFF", "#1D2330", "git checkout main<br>git merge 이름<br><br>push 전에 취소<br>git reset --hard HEAD~1"),
         ("충돌", "#A33131", "#FFFFFF", "#1D2330", "파일에서 고르기<br>표시 세 줄 지우기<br>git add 파일<br>git commit -m &quot;...&quot;<br>막히면 git merge --abort"),
         ("GitHub과 함께", "#F6F5F1", "#1D2330", "#F2C46D", "git push origin 이름<br>→ Pull Request<br>→ Merge<br>git checkout main<br>git fetch origin<br>git pull origin main")]
for k, (h, hc, bg, tc, body) in enumerate(cards):
    hc, tc = ("#5A3BB8", "#1D2330") if bg == "#1D2330" else (hc, tc)
    bd = "" if k == 0 else f"border-left:2px solid {HAIR};"
    ch.append(f'<div style="flex:1;display:flex;flex-direction:column;gap:16px;{bd}padding:8px 28px">'
              f'<h3 style="font-size:36px;font-weight:700;color:{hc}">{h}</h3>'
              f'<p style="font-family:{MONO};font-size:24px;line-height:1.8;color:{tc}">{body}</p></div>')
ch += ['</div>', f'<p style="font-size:28px;font-weight:700;color:#1D2330">브랜치 이름: <span style="color:#1A7340">feature/login-button</span> · main에는 직접 커밋하지 않기</p>',
       '<aside>수업 끝에 이 장을 띄워 두고, 칠판에 그래프를 그리며 명령마다 이름표와 HEAD가 어디로 가는지 학생이 직접 말해 보게 해요.</aside>', '</section>']
W("cheatsheet", "\n".join(ch))

# ---------- merge-how ----------
h = [sec("merge-how"), head("합치기", "merge는 받는 쪽에서 해요")]
ym, yu = 500, 360
h += [hline(240, 600, ym, BLL), conn(600, ym, 760, yu, GRL), hline(760, 940, yu, GRL)]
for x, hs in ((240, "9e6cce4"), (420, "5ec913c"), (600, "d6b044a")):
    h.append(node(x, ym, BL, 22))
    h.append(f'<p style="position:absolute;left:{x-80}px;top:{ym+30}px;width:160px;font-family:{MONO};font-size:24px;font-weight:700;text-align:center;color:#1D2330">{hs}</p>')
for x, hs in ((760, "eb05b65"), (940, "4e60a09")):
    h.append(node(x, yu, GR, 22))
    h.append(f'<p style="position:absolute;left:{x-80}px;top:{yu+30}px;width:160px;font-family:{MONO};font-size:24px;font-weight:700;text-align:center;color:#1D2330">{hs}</p>')
h.append(pill(940, yu - 66, "feature/login", "green"))
h.append(pill(560, ym + 72, "main", "main"))
h.append(pill(668, ym + 72, "HEAD", "head", ' data-build-in="fade order 1"'))
h.append(conn(905, yu + 22, 640, ym - 14, GR, ' data-build-in="fade order 2" head="end"').replace('border-width:6px', 'border-width:5px;border-style:dashed'))
h.append(f'<p data-build-in="fade order 2" style="position:absolute;left:790px;top:450px;width:200px;font-size:26px;font-weight:700;color:#1A7340">가져와요</p>')
leg = [("main", "main", "받는 쪽", "먼저 checkout으로 가 있는 브랜치"), ("feature/login", "green", "가져올 쪽", "git merge 뒤에 적는 이름")]
for i, (t, k, a, b) in enumerate(leg):
    y = 300 + i * 150
    h.append(f'<div data-build-in="fade order {i+1}" style="position:absolute;left:1140px;top:{y}px;width:640px;display:flex;flex-direction:column;gap:8px">'
             f'<p style="font-size:30px;font-weight:700;color:{BL if i == 0 else "#1A7340"}">{a}</p>'
             f'<p style="font-size:26px;color:#4A5262">{b}</p></div>')
h.append('<div style="position:absolute;left:1100px;top:290px;width:4px;height:300px;background:#E1DED6"></div>')
steps = [("1", "받을 브랜치로 이동", "git checkout main", BL), ("2", "가져올 브랜치 이름을 적어요", "git merge feature/login", GR)]
h.append(f'<div style="position:absolute;left:96px;top:690px;width:1728px;display:flex;flex-direction:row;gap:24px;border-top:2px solid {HAIR};padding-top:36px">')
for n_, t, cmd, col in steps:
    h.append(f'<div data-build-in="rise order {n_}" style="flex:1;display:flex;flex-direction:row;gap:24px;align-items:center">'
             f'<p style="width:64px;height:64px;flex:none;font-size:34px;font-weight:900;line-height:64px;text-align:center;color:#FFFFFF;background:{col};border-radius:32px">{n_}</p>'
             f'<div style="display:flex;flex-direction:column;gap:12px"><p style="font-size:28px;font-weight:700;color:#1D2330">{t}</p>'
             f'<p style="font-family:{MONO};font-size:30px;font-weight:700;color:#1D2330">{cmd}</p></div></div>')
h.append('</div>')
h.append('<p style="position:absolute;left:96px;top:900px;width:1728px;font-size:28px;font-weight:700;color:#1D2330">02에서 본 git pull origin main도 받아 온 커밋을 이 방식으로 merge해요.</p>')
h.append('<aside>git merge 이름은 그 이름의 커밋을 지금 내가 있는 브랜치로 가져와요. 그래서 순서가 중요해요. 먼저 받을 쪽(main)으로 checkout하고, 그다음 가져올 브랜치 이름을 적어요. 반대로 feature/login에 있는 채로 git merge main을 치면 main의 커밋이 feature/login으로 들어가요. 02에서 git pull origin main을 배울 때 merge는 03에서 본다고 했죠. pull은 GitHub의 main을 받아 온 뒤 지금 브랜치로 merge해요.</aside></section>')
W("merge-how", "\n".join(h))

# ---------- shared pieces for the conflict pages ----------
RED = "#A33131"
LINE_ST = {"o": "color:#1D2330", "g": "color:#1A7340;background:#DDF2E5", "b": "color:#1E3F8F;background:#DCE7FB",
           "x": "color:#9AA0AB;text-decoration:line-through"}
TERM_ST = {"$": "#F2C46D", "o": "#D8DEE9", "r": "#F28B82", "g": "#7FD18B", "h": "#9AA3B5"}
MARK_ST = {"m": "#F28B82", "b": "#8FB3FF", "g": "#7FD18B", "o": "#D8DEE9"}


def filecard(L, top, w, h, branch, kind, fname, lines, attrs="", big=False):
    """big: 44px lines with 18px gaps and 40px top padding, for a card that fills most of the slide."""
    fs, gap, pad = (44, 18, 40) if big else (34, 12, 28)
    o = [f'<div{attrs} style="position:absolute;left:{L}px;top:{top}px;width:{w}px;height:{h}px;background:#FFFFFF;border:2px solid #E1DED6;border-radius:22px;padding:{pad}px 36px;display:flex;flex-direction:column;gap:{gap}px">']
    o.append(f'<div style="display:flex;flex-direction:row;gap:16px;align-items:center">{pill_inline(branch, kind)}'
             f'<p style="font-size:26px;font-weight:700;color:#4A5262">{fname}</p></div>')
    for text, k in lines:
        o.append(f'<p style="font-family:{MONO};font-size:{fs}px;line-height:1.4;padding:0 10px;border-radius:6px;{LINE_ST[k]}">{text}</p>')
    o.append('</div>')
    return "".join(o)


def pill_inline(text, kind):
    st = {"main": "background:#2459C9;color:#FFFFFF", "green": "background:#1F8A4C;color:#FFFFFF", "orange": "background:#B26A00;color:#FFFFFF",
          "origin": "background:#E7DEFC;color:#4A2FA8;border:2px solid #8E6FEA", "gray": "background:#E1DED6;color:#1D2330"}[kind]
    return f'<p style="font-family:{MONO};font-size:26px;font-weight:700;line-height:1.5;padding:0 14px;border-radius:8px;{st}">{text}</p>'


def tw(t, size):
    """Rough ink width of a monospace line: Latin 0.6 em, Hangul about 1 em."""
    t = t.replace("&lt;", "<").replace("&gt;", ">").replace("&#160;", " ").replace("&quot;", '"')
    return sum(size if ord(ch) > 0x2E80 else size * 0.6 for ch in t)


def term(L, top, w, lines, attrs="", size=28, build=None):
    """build: click order the whole terminal comes in on (1 = on screen from the start). No typing, so a slide
    takes as few clicks as possible. term.last is the last order used, term.boxes[i] the (x, y, w, h) of line i for box()."""
    if build is not None and build > 1:
        attrs += f' data-build-in="fade order {build}"'
    o = [f'<div{attrs} style="position:absolute;left:{L}px;top:{top}px;width:{w}px;background:#1B2029;border-radius:20px;padding:24px 32px;display:flex;flex-direction:column;gap:6px;font-family:{MONO}">']
    cur, prev, y = (build or 1) - 1, None, top + 24
    term.boxes = []
    for k, text in lines:
        t = ("$ " + text) if k == "$" else text
        wgt = "700" if k == "$" else "400"
        at = ""
        if build is not None and build > 1:     # comes in after what is above it: the whole box on one click
            cur = build
        prev = k
        term.boxes.append((L + 32, y, tw(t, size), size * 1.35))
        y += size * 1.35 + 6
        o.append(f'<p{at} style="font-size:{size}px;font-weight:{wgt};line-height:1.35;white-space:nowrap;color:{TERM_ST[k]}">{t}</p>')
    o.append('</div>')
    term.last = cur
    return "".join(o)


def errbox(order, i):
    """Red pen box around terminal line i of the last term()."""
    x, y, w, h = term.boxes[i]
    return box(order, round(x - 10), round(y - 2), round(w + 20), round(h + 4), RED)


def markers(L, top, w, h, fname, lines, size=34):
    o = [f'<div style="position:absolute;left:{L}px;top:{top}px;width:{w}px;height:{h}px;background:#1B2029;border-radius:22px;padding:28px 36px;display:flex;flex-direction:column;gap:6px">']
    o.append(f'<p style="font-size:24px;color:#9AA3B5">{fname}</p>')
    for text, k in lines:
        o.append(f'<p style="font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.4;white-space:nowrap;color:{MARK_ST[k]}">{text}</p>')
    o.append('</div>')
    return "".join(o)


def arrow(L, top):
    return f'<x-shape kind="arrow-right" style="position:absolute;left:{L}px;top:{top}px;width:72px;height:64px;background:#C3C8D2"></x-shape>'


def takeaway(text, top=900, color="#1D2330", order=None):
    o = f" order {order}" if order else ""
    return f'<p data-build-in="rise{o}" style="position:absolute;left:96px;top:{top}px;width:1728px;font-size:34px;font-weight:700;line-height:1.4;color:{color}">{text}</p>'


def page(i, eyebrow, title, body, aside, color=RED, bg="#F6F5F1"):
    W(i, "\n".join([sec(i, bg), head(eyebrow, title, color)] + body + [f'<aside>{aside}</aside></section>']))


def scen(i, eyebrow, title, left, right, lines, take, aside, err=1):
    """Two file cards, then the merge is typed in, the error line gets a red box, then the takeaway."""
    t = term(96, 610, 1728, lines, build=1)
    n = term.last + 1
    body = [filecard(96, 250, 840, 320, *left), filecard(984, 250, 840, 320, *right), t, errbox(n, err), takeaway(take, order=n + 1)]
    page(i, eyebrow, title, body, aside)


# ---------- folder-switch ----------
fs = [filecard(96, 250, 780, 600, "feature/login", "green", "작업 폴더", [("hello.md", "o"), ("README.md", "o"), ("login.md", "g")], big=True),
      arrow(924, 500),
      filecard(1044, 250, 780, 600, "main", "main", "작업 폴더", [("hello.md", "o"), ("README.md", "o"), ("login.md", "x")], ' data-build-in="fade order 1"', big=True),
      '<p style="position:absolute;left:890px;top:580px;width:140px;font-family:' + MONO + ';font-size:24px;font-weight:700;text-align:center;color:#6A7180">checkout<br>main</p>',
      ring(2, 1090, 250 + 40 + 44 + 18 + 2 * 78, 230, 62, OR),
      takeaway("login.md는 사라진 게 아니에요. feature/login으로 가면 다시 보여요.", 916, order=3)]
page("folder-switch", "만들고 옮기기", "브랜치를 옮기면 폴더 파일도 바뀌어요", fs,
     "checkout은 HEAD를 옮기면서 작업 폴더 파일도 그 브랜치의 마지막 커밋 모습으로 바꿔요. main에서 ls를 쳐 보면 README.md와 hello.md만 보여요. login.md가 안 보여 당황하는 학생이 많아요. 커밋하지 않은 변경이 있으면 checkout이 막힐 수 있어요(막힐 때 파트).",
     color="#2459C9")

# ---------- switch ----------
sw = ['<div style="position:absolute;left:96px;top:250px;width:1728px;display:grid;grid-template-columns:420px 1fr 1fr;gap:12px">', '<div></div>']
for t, fg, bg in [("git checkout", "#1D2330", "#E1DED6"), ("git switch", "#FFFFFF", "#2459C9")]:
    sw.append(f'<p style="font-family:{MONO};font-size:30px;font-weight:700;text-align:center;color:{fg};background:{bg};padding:16px;border-radius:14px">{t}</p>')
for k, (what, a, b) in enumerate([("브랜치로 옮겨 가기", "git checkout 이름", "git switch 이름"), ("만들고 바로 옮겨 가기", "git checkout -b 이름", "git switch -c 이름")]):
    sw.append(f'<p data-build-in="fade order {k+1}" style="font-size:30px;font-weight:700;color:#1D2330;border-bottom:2px solid {HAIR};padding:22px 8px">{what}</p>')
    for c in (a, b):
        sw.append(f'<p data-build-in="fade order {k+1}" style="font-family:{MONO};font-size:30px;font-weight:700;text-align:center;color:#1D2330;border-bottom:2px solid {HAIR};padding:22px 16px">{c}</p>')
sw.append('</div>')
sw.append(term(96, 560, 1728, [("$", "git switch feature/login"), ("o", "Switched to branch 'feature/login'"),
                              ("$", "git switch -c feature/login-button"), ("o", "Switched to a new branch 'feature/login-button'")], ' data-build-in="fade order 3"'))
sw.append(takeaway("하는 일과 출력은 같아요. 이 덱은 checkout으로 보여 주고, switch로 쳐도 돼요.", 900))
page("switch", "만들고 옮기기", "브랜치만 옮기는 명령, git switch", sw,
     "git switch는 Git 2.23(2019년)에 생긴 명령이에요. checkout은 브랜치를 옮기는 일 말고 파일을 예전 모습으로 되돌리는 일도 해서 헷갈리기 쉬워요. 그래서 브랜치를 옮기는 일만 따로 떼어 switch를 만들었어요. -c는 create(만들기)의 첫 글자예요. 내 Git이 오래돼서 switch가 없다고 나오면 git --version으로 버전을 확인해요. 팀 자료나 인터넷 글에는 두 명령이 섞여 나오니 둘 다 읽을 수 있으면 돼요.",
     color="#2459C9")

# ---------- conflict-when ----------
cases = [("CheckCircle", "#1A7340", "#F1FAF4", "#4DB57A", "다른 파일을 고침", "알아서 합쳐요"),
         ("CheckCircle", "#1A7340", "#F1FAF4", "#4DB57A", "같은 파일, 멀리 떨어진 줄", "알아서 합쳐요"),
         ("Warning", RED, "#FBE4E2", "#E07A7A", "같은 줄, 바로 옆 줄", "충돌: 사람이 골라요"),
         ("Warning", RED, "#FBE4E2", "#E07A7A", "한쪽은 지우고, 한쪽은 고침", "충돌: 사람이 골라요")]
cw = [vrule(959, 280, 560)]
for g, (ic, col, head_) in enumerate([("CheckCircle", "#1A7340", "Git이 알아서 합쳐요"), ("Warning", RED, "충돌: 사람이 골라요")]):
    L = 96 + g * 912
    cw.append(f'<div data-build-in="rise order {g+1}" style="position:absolute;left:{L}px;top:290px;width:816px;display:flex;flex-direction:row;gap:18px;align-items:center">'
              f'<x-icon name="{ic}" style="width:56px;height:56px;color:{col}"></x-icon><p style="font-size:40px;font-weight:700;color:{col}">{head_}</p></div>')
    for j in range(2):
        k = 2 * g + j
        cw.append(f'<p data-build-in="rise order {g+1}" style="position:absolute;left:{L}px;top:{430 + j*180}px;width:816px;font-size:44px;font-weight:700;line-height:1.3;color:#1D2330;'
                  f'border-top:2px solid {HAIR};padding-top:40px">{cases[k][4]}</p>')
cw.append(takeaway("충돌은 Git이 고를 수 없는 곳만 사람에게 물어보는 거예요.", 916, order=3))
page("conflict-when", "충돌 풀기", "충돌은 언제 나요?", cw,
     "양쪽 브랜치가 같은 곳을 다르게 고쳤을 때만 충돌이 나요. 다른 파일이나 멀리 떨어진 줄은 Git이 알아서 합쳐요. 바로 옆 줄도 한 덩어리로 봐서 충돌이 나요(시나리오 2). 충돌은 고장이 아니에요.")

# ---------- abort ----------
ab = [term(96, 250, 1728, [("$", "git merge feature/login-email"), ("r", "CONFLICT (content): Merge conflict in login.md"),
                           ("o", "Automatic merge failed; fix conflicts and then commit the result."),
                           ("$", "git merge --abort"), ("$", "git status"), ("o", "On branch main"), ("g", "nothing to commit, working tree clean")], size=34, build=1)]
ab += [errbox(term.last + 1, 6).replace(RED, GR), takeaway("merge --abort는 합치기 전 모습으로 돌려놔요. 천천히 다시 해도 돼요.", 916, order=term.last + 2)]
page("abort", "충돌 풀기", "헷갈리면 merge 전으로 돌아가요", ab,
     "충돌을 풀다 꼬였거나 지금 풀 시간이 없으면 git merge --abort를 쳐요. 출력은 없고, git status가 깨끗해져요. pull 하다 난 충돌도 똑같이 git merge --abort로 돌아가요. 이 화면은 시나리오 2의 충돌이에요. 출력 중 Auto-merging 줄은 뺐어요.")

# ---------- 시나리오 2: 바로 옆 줄 ----------
EBS = "충돌 시나리오"
scen("sc-adjacent", EBS + " 2 · 바로 옆 줄", "다른 줄인데도 충돌이 나요",
     ("main", "main", "login.md", [("아이디", "o"), ("비밀번호 (8자 이상)", "b")]),
     ("feature/login-email", "green", "login.md", [("이메일", "g"), ("비밀번호", "o")]),
     [("$", "git merge feature/login-email"), ("r", "CONFLICT (content): Merge conflict in login.md"), ("o", "Automatic merge failed; fix conflicts and then commit the result.")],
     "붙어 있는 줄을 각자 고치면 Git은 한 덩어리로 봐요.",
     "main은 둘째 줄에 (8자 이상) 안내를 붙였고, feature/login-email은 첫째 줄 아이디를 이메일로 바꿨어요. 서로 다른 줄이지만 바로 붙어 있어서 Git이 어떻게 섞을지 정하지 못해요. 출력 중 Auto-merging 줄은 뺐어요.")
page("rs-adjacent", EBS + " 2 · 바로 옆 줄", "둘 다 남기면 돼요", [
    markers(96, 250, 800, 440, "login.md (충돌 표시)", [("&lt;&lt;&lt;&lt;&lt;&lt;&lt; HEAD", "m"), ("아이디", "b"), ("비밀번호 (8자 이상)", "b"), ("=======", "m"),
                                                    ("이메일", "g"), ("비밀번호", "g"), ("&gt;&gt;&gt;&gt;&gt;&gt;&gt; feature/login-email", "m")], size=32),
    arrow(920, 440),
    filecard(1016, 250, 808, 440, "main", "main", "고친 login.md", [("이메일", "g"), ("비밀번호 (8자 이상)", "b")], ' data-build-in="fade order 1"'),
    term(96, 714, 1728, [("$", "git add login.md"), ("$", 'git commit -m "fix: 로그인 입력 충돌 해결"'), ("o", "[main a7c76b5] fix: 로그인 입력 충돌 해결")], build=2),
    takeaway("양쪽에서 바뀐 줄을 하나씩 가져와 합치고, 표시 세 줄은 지워요.", 920, order=3)],
    "위 덩어리는 main의 두 줄, 아래 덩어리는 feature/login-email의 두 줄이에요. 둘 다 살리려면 바뀐 줄만 골라 이메일, 비밀번호 (8자 이상)으로 만들어요. 고친 뒤 add, commit은 시나리오 1과 같아요.")

# ---------- 시나리오 3: 지움 vs 고침 ----------
scen("sc-delete", EBS + " 3 · 지움 vs 고침", "한쪽은 파일을 지우고, 한쪽은 고쳤어요",
     ("main", "main", "old-login.md", [("임시 로그인 화면", "o"), ("아이디", "b")]),
     ("chore/remove-old-login", "orange", "old-login.md", [("파일 삭제", "x")]),
     [("$", "git merge chore/remove-old-login"), ("r", "CONFLICT (modify/delete): old-login.md deleted in chore/remove-old-login and modified in HEAD."),
      ("o", "Automatic merge failed; fix conflicts and then commit the result.")],
     "파일 안에 충돌 표시가 없어요. 지울지 남길지만 정하면 돼요.",
     "main은 old-login.md에 아이디 한 줄을 더했고, chore/remove-old-login은 old-login.md를 지웠어요(git rm). CONFLICT 줄 끝의 Version HEAD of old-login.md left in tree.는 화면 폭 때문에 뺐어요. main 쪽 old-login.md가 폴더에 남아 있다는 뜻이에요.")
choice = lambda L, ic, col, bg, bd, h, cmd, out, k: (
    f'<div data-build-in="rise order {k}" style="position:absolute;left:{L}px;top:520px;width:840px;height:300px;border-top:4px solid {bd};padding:32px 0;display:flex;flex-direction:column;gap:16px">'
    f'<div style="display:flex;flex-direction:row;gap:16px;align-items:center"><x-icon name="{ic}" style="width:44px;height:44px;color:{col}"></x-icon><p style="font-size:34px;font-weight:700;color:{col}">{h}</p></div>'
    f'<p style="font-family:{MONO};font-size:32px;font-weight:700;color:#1D2330">{cmd}</p>'
    f'<p style="font-family:{MONO};font-size:32px;font-weight:700;color:#1D2330">{out}</p></div>')
page("rs-delete", EBS + " 3 · 지움 vs 고침", "지울지 남길지 골라요", [
    term(96, 250, 1728, [("$", "git status"), ("o", "Unmerged paths:"), ("h", '  (use "git add/rm &lt;file&gt;..." as appropriate to mark resolution)'),
                         ("r", "&#160;&#160;&#160;&#160;deleted by them: old-login.md")]),
    underline(1, 128 + round(4 * 16.8), 128 + round(19 * 16.8), round(term.boxes[3][1] + term.boxes[3][3] + 2), OR),
    choice(96, "Warning", RED, "#FBE4E2", "#E07A7A", "지우기로 하면", "git rm old-login.md", 'git commit -m "..."', 2),
    choice(984, "CheckCircle", "#1A7340", "#F1FAF4", "#4DB57A", "남기기로 하면", "git add old-login.md", 'git commit -m "..."', 3),
    takeaway("deleted by them은 합치려는 브랜치(them)가 지웠다는 뜻이에요.", 880, order=4)],
    "git status 앞뒤 안내 줄은 뺐어요. 이번 실습에서는 git rm old-login.md로 지우기를 골랐고 출력은 rm 'old-login.md'였어요. 이어서 git commit -m \"chore: 옛 로그인 화면 삭제 반영\"을 하면 [main 7e68b90] chore: 옛 로그인 화면 삭제 반영이 나와요. 내가 지운 쪽이면 deleted by us로 보여요.")

# ---------- 시나리오 4: 같은 이름 새 파일 ----------
scen("sc-addadd", EBS + " 4 · 같은 이름 새 파일", "둘 다 signup.md를 새로 만들었어요",
     ("main", "main", "signup.md (새 파일)", [("- 전화번호", "b")]),
     ("feature/signup", "green", "signup.md (새 파일)", [("- 이메일", "g")]),
     [("$", "git merge feature/signup"), ("r", "CONFLICT (add/add): Merge conflict in signup.md"), ("o", "Automatic merge failed; fix conflicts and then commit the result.")],
     "처음부터 내용이 달라서, 파일 전체가 충돌 표시로 묶여요.",
     "두 사람이 회원가입 항목 파일을 같은 이름으로 따로 만든 상황이에요. git status에는 both added: signup.md로 나와요. 출력 중 Auto-merging 줄은 뺐어요.")
page("rs-addadd", EBS + " 4 · 같은 이름 새 파일", "목록이면 둘 다 살려요", [
    markers(96, 250, 800, 340, "signup.md (충돌 표시)", [("&lt;&lt;&lt;&lt;&lt;&lt;&lt; HEAD", "m"), ("- 전화번호", "b"), ("=======", "m"), ("- 이메일", "g"),
                                                    ("&gt;&gt;&gt;&gt;&gt;&gt;&gt; feature/signup", "m")]),
    arrow(920, 390),
    filecard(1016, 250, 808, 340, "main", "main", "고친 signup.md", [("- 이메일", "g"), ("- 전화번호", "b")], ' data-build-in="fade order 1"'),
    term(96, 640, 1728, [("$", "git add signup.md"), ("$", 'git commit -m "fix: 회원가입 항목 합치기"'), ("o", "[main 23d0c5f] fix: 회원가입 항목 합치기")], build=2),
    takeaway("푸는 방법은 시나리오 1과 같아요. 고르고, 표시 지우고, add, commit.", 880, order=3)],
    "회원가입 항목처럼 둘 다 필요한 내용이면 두 줄을 모두 남겨요. 한쪽만 맞는 내용이면 그쪽만 남겨요.")

# ---------- 시나리오 5: pull 할 때 ----------
EBP = EBS + " 5 · pull 할 때"
scen("sc-pull", EBP, "팀원이 먼저 같은 줄을 push했어요",
     ("origin/main", "origin", "GitHub의 login.md (팀원)", [("# Login", "g"), ("아이디", "o")]),
     ("main", "main", "내 login.md", [("# 로그인하기", "b"), ("아이디", "o")]),
     [("$", "git push origin main"), ("r", " ! [rejected]        main -&gt; main (fetch first)"),
      ("$", "git pull origin main"), ("r", "fatal: Need to specify how to reconcile divergent branches.")],
     "갈라진 상태에서 pull하면 어떻게 합칠지 정해 달라며 멈춰요.",
     "push가 거절돼서 pull했더니 fatal로 멈췄어요. 내 main과 GitHub main에 서로 모르는 커밋이 하나씩 있어서예요. 출력 중 error, hint 줄과 From 줄은 뺐어요. git 2.27부터 이렇게 물어봐요.", err=3)
page("pull-config", EBP, "처음 한 번만 설정해요", [
    f'<div style="position:absolute;left:96px;top:250px;width:1728px;height:180px;background:#1D2330;border-radius:24px;display:flex;flex-direction:row;align-items:center;padding:0 48px">'
    f'<p style="font-family:{MONO};font-size:48px;font-weight:700;color:#F2C46D">git config --global pull.rebase false</p></div>',
    '<div style="position:absolute;left:96px;top:520px;width:1728px;height:300px;display:flex;flex-direction:row;gap:24px;align-items:center">'
    + "".join(f'<div data-build-in="rise order {k+1}" style="flex:1;display:flex;flex-direction:column;gap:16px;padding:0 0 0 {0 if k == 0 else 40}px;justify-content:center">'
              f'<p style="font-family:{MONO};font-size:64px;font-weight:700;color:{c}">{a}</p><p style="font-size:32px;color:#4A5262">{b}</p></div>'
              for k, (a, b, c) in enumerate([("git pull", "pull은 두 단계예요", "#1D2330"), ("= fetch", "GitHub 커밋을 받아 오고", "#6B47D6"),
                                              ("+ merge", "내 main과 합쳐요", "#2459C9")]))
    + '</div>',
    underline(4, 144 + round(20 * 28.8), 144 + round(37 * 28.8), 380, OR),
    takeaway("pull.rebase false는 pull할 때 merge로 합치라는 뜻이에요. 설정한 뒤 다시 pull해요.", 916, order=4)],
    "출력은 없어요. --global이라 내 컴퓨터의 모든 저장소에 한 번에 적용돼요. rebase는 08에서 다른 합치는 방법과 비교해 봐요. 02의 처음 설정(user.name, user.email)과 같이 해 두면 좋아요.")
page("rs-pull", EBP, "다시 pull하면 익숙한 충돌이에요", [
    term(96, 250, 1060, [("$", "git pull origin main"), ("r", "CONFLICT (content): Merge conflict in login.md")], size=26),
    markers(96, 400, 1060, 320, "login.md (충돌 표시)", [("&lt;&lt;&lt;&lt;&lt;&lt;&lt; HEAD", "m"), ("# 로그인하기", "b"), ("=======", "m"), ("# Login", "g"),
                                                    ("&gt;&gt;&gt;&gt;&gt;&gt;&gt; 82b872cd8ac7e79ce6c6eb09ee3531e9108dff77", "m")], size=26),
    underline(1, 132 + round(8 * 15.6), 132 + round(48 * 15.6), 400 + 28 + 34 + 6 + 4 * 42 + 38, OR),
    term(1196, 250, 628, [("$", "git add login.md"), ("$", "git commit -m"), ("o", '  "fix: 팀원과 로그인 제목 충돌 해결"'), ("$", "git push origin main"),
                          ("g", "   82b872c..1ebdd15  main -&gt; main")], size=26, build=2),
    takeaway("pull 충돌은 아래쪽 이름이 브랜치 대신 커밋 해시예요. 푸는 법은 같아요.", 780, order=3)],
    "GitHub에서 받아 온 커밋은 브랜치 이름이 없어서 &gt;&gt;&gt;&gt;&gt;&gt;&gt; 뒤에 해시가 나와요. 위쪽 HEAD가 내 것, 아래쪽이 팀원 것이에요. 고치고 add, commit 한 다음 push하면 이번엔 올라가요. pull, commit, push 출력 일부는 뺐어요.")

# ---------- 시나리오 6: PR 충돌 ----------
EBR = EBS + " 6 · Pull Request"
pr = ['<div style="position:absolute;left:96px;top:250px;width:1728px;height:600px;background:#FFFFFF;border:2px solid #D0D7DE;border-radius:20px"></div>',
      f'<p style="position:absolute;left:144px;top:290px;width:1600px;font-size:38px;font-weight:700;color:#1D2330">feat: 로그인 제목 바꾸기 <span style="color:#6A7180">#2</span></p>',
      f'<div style="position:absolute;left:144px;top:364px;width:1600px;display:flex;flex-direction:row;gap:12px;align-items:center">'
      f'<p style="font-size:26px;font-weight:700;color:#FFFFFF;background:#1F8A4C;padding:4px 16px;border-radius:20px">Open</p>'
      f'<p style="font-family:{MONO};font-size:26px;color:#1D2330;background:#DCE7FB;padding:4px 12px;border-radius:8px">main</p>'
      f'<p style="font-size:28px;color:#6A7180">←</p>'
      f'<p style="font-family:{MONO};font-size:26px;color:#1D2330;background:#DDF2E5;padding:4px 12px;border-radius:8px">feature/login-title</p></div>',
      f'<div data-build-in="fade order 1" style="position:absolute;left:144px;top:450px;width:1632px;height:340px;background:#FFF8F0;border:2px solid #E4C08A;border-radius:14px;padding:32px 36px;display:flex;flex-direction:column;justify-content:center;gap:28px">'
      f'<div style="display:flex;flex-direction:row;gap:16px;align-items:center"><x-icon name="Warning" style="width:44px;height:44px;color:#B26A00"></x-icon>'
      f'<p style="font-size:34px;font-weight:700;color:#1D2330">This branch has conflicts that must be resolved</p></div>'
      f'<p style="font-family:{MONO};font-size:28px;color:#4A5262">Conflicting files: login.md</p>'
      f'<p style="font-size:28px;font-weight:700;color:#9AA0AB;background:#F0F1F3;border-radius:10px;padding:10px 24px;width:330px">Merge pull request</p></div>',
      underline(2, 252, 1044, 576, RED),
      takeaway("내가 PR을 올린 사이 main이 같은 줄을 바꿨어요. Merge 버튼이 막혀요.", 916, order=3)]
page("sc-pr", EBR, "PR 화면에 충돌이 떠요", pr,
     "feature/login-title을 push하고 PR을 만들었는데, 그 사이 팀원이 main의 같은 줄을 # 로그인 페이지로 바꿔 합쳤어요. GitHub 화면 문구와 모양은 업데이트에 따라 조금 다를 수 있어요. GitHub에서 Resolve conflicts 버튼으로 웹에서 풀 수도 있지만, 수업에서는 내 컴퓨터에서 푸는 법을 써요.")
page("rs-pr", EBR, "내 브랜치에서 main을 받아 풀고, 다시 push", [
    term(96, 250, 1728, [("$", "git checkout feature/login-title"), ("$", "git pull origin main"), ("r", "CONFLICT (content): Merge conflict in login.md"),
                         ("h", "# login.md 충돌 표시 지우고 저장"), ("$", "git add login.md"), ("$", 'git commit -m "fix: main과 로그인 제목 충돌 해결"'),
                         ("$", "git push origin feature/login-title"), ("g", "   c7149cd..8feb440  feature/login-title -&gt; feature/login-title")], size=32, build=1),
    errbox(1, 2),
    takeaway("push하면 PR 화면이 다시 Merge 할 수 있는 상태로 바뀌어요.", 916, order=2)],
    "main을 내 브랜치로 먼저 가져와서 충돌을 풀어요. 그래서 checkout feature/login-title 다음에 pull origin main이에요. 받는 쪽이 feature/login-title이라는 점이 merge와 같아요. checkout, pull, commit 출력 일부는 뺐어요.")

# ---------- conflict-sum ----------
rows = [("CONFLICT (content)", "같은 줄, 옆 줄", "고르고, 표시 지우고, add, commit"),
        ("CONFLICT (modify/delete)", "지움 vs 고침", "git rm 또는 git add, commit"),
        ("CONFLICT (add/add)", "같은 이름 새 파일", "고르고, 표시 지우고, add, commit"),
        ("fatal: Need to specify how to reconcile ...", "갈라진 채 pull", "git config --global pull.rebase false"),
        ("This branch has conflicts ...", "PR 충돌", "내 브랜치에서 pull origin main, 풀고 push")]
cs = [f'<div style="position:absolute;left:96px;top:250px;width:1728px;display:flex;flex-direction:column">',
      '<div style="display:flex;flex-direction:row;gap:24px;padding:0 8px 14px 8px;border-bottom:2px solid #9AA0AB">'
      + "".join(f'<p style="{w_}font-size:24px;font-weight:700;color:#6A7180">{t}</p>' for w_, t in (("width:720px;flex:none;", "메시지"), ("width:280px;flex:none;", "상황"), ("", "푸는 법"))) + '</div>']
for k, (msg, sit, fix) in enumerate(rows):
    cs.append(f'<div style="display:flex;flex-direction:row;gap:24px;align-items:center;border-bottom:2px solid {HAIR};padding:26px 8px">'
              f'<p style="width:720px;flex:none;font-family:{MONO};font-size:26px;font-weight:700;color:{RED}">{msg}</p>'
              f'<p style="width:280px;flex:none;font-size:28px;font-weight:700;color:#1D2330">{sit}</p>'
              f'<p style="font-size:28px;color:#4A5262">{fix}</p></div>')
cs.append('</div>')
cs.append(takeaway("어떤 충돌이든 막히면 git merge --abort로 처음으로 돌아갈 수 있어요.", 900))
page("conflict-sum", EBS, "메시지로 충돌 종류를 알아봐요", cs,
     "메시지 첫 단어만 봐도 무엇을 할지 알 수 있어요. 충돌을 푼 뒤에는 git status로 남은 충돌 파일이 없는지 확인하고 커밋해요.")

# ---------- 되돌리기 ----------
UC = "#8A5200"
rz = []
for i, (title, sub) in enumerate([("케이스 1 · 일반 커밋", "실수한 커밋 하나를 빼요"), ("케이스 2 · merge 커밋", "합친 것을 없던 일로 해요")]):
    L = 96 + i * 888
    rz.append(f'<p data-build-in="fade order {i+1}" style="position:absolute;left:{L+40}px;top:280px;width:760px;font-size:34px;font-weight:700;color:{UC}">{title}</p>')
    rz.append(f'<p data-build-in="fade order {i+1}" style="position:absolute;left:{L+40}px;top:336px;width:760px;font-size:28px;color:#4A5262">{sub}</p>')
ym, yu, o0 = 560, 450, 96
rz.append(vrule(959, 270, 430))
rz += [hline(o0 + 100, o0 + 560, ym, BLL)]
for x in (100, 300, 500):
    rz.append(node(o0 + x, ym, BL, 22))
rz.append(f'<div style="position:absolute;left:{o0+560}px;top:{ym-3}px;width:140px;height:6px;border-top:6px dashed #C3C8D2"></div>')
rz.append(f'<div style="position:absolute;left:{o0+678}px;top:{ym-22}px;width:44px;height:44px;border-radius:50%;background:#FDFCF9;border:5px dashed #C3C8D2"></div>')
rz.append(f'<p style="position:absolute;left:{o0+640}px;top:{ym+30}px;width:120px;font-family:{MONO};font-size:24px;font-weight:700;text-align:center;color:#6A7180">실수</p>')
rz.append(pill(o0 + 500, ym + 36, "main", "main"))
o1 = 984
rz += [hline(o1 + 100, o1 + 500, ym, BLL), conn(o1 + 300, ym, o1 + 400, yu, ORL), conn(o1 + 400, yu, o1 + 700, ym, ORL)]
rz.append(f'<div style="position:absolute;left:{o1+522}px;top:{ym-3}px;width:156px;height:6px;border-top:6px dashed #C3C8D2"></div>')
for x in (100, 300, 500):
    rz.append(node(o1 + x, ym, BL, 22))
rz.append(node(o1 + 400, yu, OR, 22))
rz.append(f'<div style="position:absolute;left:{o1+678}px;top:{ym-22}px;width:44px;height:44px;border-radius:50%;background:#FDFCF9;border:5px dashed #C3C8D2"></div>')
rz.append(f'<p style="position:absolute;left:{o1+640}px;top:{ym+30}px;width:120px;font-family:{MONO};font-size:24px;font-weight:700;text-align:center;color:#6A7180">merge</p>')
rz.append(pill(o1 + 500, ym + 36, "main", "main"))
rz.append(pill(o1 + 400, yu - 64, "docs/login-guide", "orange"))
rz.append(f'<div style="position:absolute;left:96px;top:760px;width:1728px;background:#1D2330;border-radius:20px;padding:24px 40px;display:flex;flex-direction:row;gap:32px;align-items:center">'
          f'<p style="font-family:{MONO};font-size:34px;font-weight:700;color:#F2C46D">git reset 옵션 HEAD~1</p>'
          f'<p style="font-size:28px;color:#D8DEE9">지금 브랜치 이름표를 한 칸 아래 커밋으로 옮겨요</p></div>')
page("r0-what", "되돌리기", "reset은 이름표를 뒤로 옮겨요", rz,
     "reset은 지금 브랜치 이름표를 예전 커밋으로 옮겨서 그 위 커밋을 기록에서 빼요. merge와 상관없이 쓰는 명령이에요. HEAD~1은 지금보다 한 칸 아래 커밋이에요. merge 커밋도 커밋 하나라서 똑같이 한 칸 뒤로 가요. 두 경우 모두 push 전에만 써요. 옵션 --soft, --mixed, --hard는 빠진 커밋의 변경을 어느 칸에 남길지 정해요.",
     color=UC)
cell = "font-size:26px;text-align:center;padding:24px 16px;border-radius:14px"
gone, keep, empty, same = ("color:#A33131;font-weight:700;background:#FBE4E2", "color:#1A7340;font-weight:700;background:#DDF2E5",
                           "color:#A33131;font-weight:700;background:#FBE4E2", "color:#4A5262;background:#FDFCF9")
rows = [("--soft", "#1D2330", [("커밋 취소", gone), ("변경이 여기 남음", keep), ("그대로", same), ("그대로", same)]),
        ("--mixed<br><span style=\"color:#6A7180\">(기본)</span>", "#1D2330", [("커밋 취소", gone), ("비움", empty), ("변경이 여기 남음", keep), ("그대로", same)]),
        ("--hard", RED, [("커밋 취소", gone), ("비움", empty), ("변경이 사라짐", "color:#FFFFFF;font-weight:700;background:#A33131"), ("그대로", same)])]
rc = ['<div style="position:absolute;left:96px;top:250px;width:1728px;display:grid;grid-template-columns:260px 1fr 1fr 1fr 1fr;gap:12px">', '<div></div>']
for t, fg, bg in [("③ 내 저장소", "#1E3F8F", "#F0F5FE"), ("② 대기실", "#1A7340", "#F1FAF4"), ("① 작업 폴더", "#3A4150", "#FDFCF9"), ("merge한 브랜치", "#8A5200", "#FBF1E1")]:
    ff = ""
    rc.append(f'<p style="{ff}font-size:28px;font-weight:700;text-align:center;color:{fg};background:{bg};padding:16px;border-radius:14px">{t}</p>')
for k, (opt, col, cells) in enumerate(rows):
    rc.append(f'<p data-build-in="fade order {k+1}" style="font-family:{MONO};font-size:30px;font-weight:700;color:{col};padding:24px 8px">{opt}</p>')
    for text, st in cells:
        rc.append(f'<p data-build-in="fade order {k+1}" style="{cell};{st}">{text}</p>')
rc.append('</div>')
rc.append(takeaway("--hard로 지운 변경은 일반 커밋이면 남는 곳이 없고, merge면 브랜치에 남아요.", 820))
page("reset-compare", EBU := "되돌리기 · 정리", "세 옵션, 무엇이 어디에 남을까?", rc,
     "02 되돌리기 파트의 reset 옵션 표와 같은 그림에 브랜치 칸을 하나 더했어요. 마지막 칸은 merge를 되돌릴 때만 해당해요. 어떤 옵션이든 docs/login-guide 이름표는 움직이지 않아서 브랜치에서 한 작업은 잃지 않아요. 일반 커밋은 그런 브랜치가 없으니 --hard를 더 조심해요.",
     color=UC, bg="#ECEAE3")

uw = [("충돌이 나서 merge가 멈췄어요", "git merge --abort", "합치기 전으로 돌아가요", "#3A4150"),
      ("커밋했는데 아직 push 전이에요", "git reset HEAD~1", "고친 내용은 작업 폴더에 남아요", "#1A7340"),
      ("merge를 끝냈고, 아직 push 전이에요", "git reset --hard HEAD~1", "git status가 깨끗한지 먼저 봐요", UC),
      ("push까지 했어요", "git revert 커밋", "merge 커밋이면 팀에 먼저 알려요", RED)]
wb = [f'<div style="position:absolute;left:96px;top:250px;width:1728px;display:flex;flex-direction:column;border-top:2px solid {HAIR}">']
for k, (sit, cmd, tip, col) in enumerate(uw):
    wb.append(f'<div style="display:flex;flex-direction:row;gap:32px;align-items:center;border-bottom:2px solid {HAIR};padding:22px 8px">'
              f'<p style="width:620px;flex:none;font-size:32px;font-weight:700;color:#1D2330">{sit}</p>'
              f'<div style="display:flex;flex-direction:column;gap:8px"><p style="font-family:{MONO};font-size:32px;font-weight:700;color:{col}">{cmd}</p>'
              f'<p style="font-size:26px;color:#4A5262">{tip}</p></div></div>')
wb.append('</div>')
wb.append(takeaway("기준은 하나예요. push 전이면 reset, push 후면 revert.", 900))
page("undo-when", EBU, "언제 무엇으로 되돌릴까?", wb,
     "일반 커밋은 기본값 --mixed가 가장 안전해요. 고친 내용이 파일에 남아요. merge를 되돌릴 땐 --hard가 깔끔해요. 브랜치에 작업이 그대로 있으니 다시 merge하면 되기 때문이에요. 단, 작업 폴더에 커밋하지 않은 변경이 있으면 같이 지워지니 git status부터 봐요. push한 일반 커밋은 02에서 배운 git revert로 되돌려요. push한 merge 커밋을 되돌리는 방법은 이 과정에서 다루지 않으니 강사나 팀과 먼저 이야기해요.",
     color=UC)

print("pages ok")
