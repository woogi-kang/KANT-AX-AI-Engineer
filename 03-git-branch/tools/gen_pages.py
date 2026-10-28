# Generates the hand-drawn pages of the branch deck (cover, toc, concept, PR, error pages).
# Usage: python3 tools/gen_pages.py slides
import os, sys
OUT = sys.argv[1]
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
def W(name, s):
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
cov += [pill(1540, y1 - 72, "feat/login", "green"), pill(1760, y0 + 44, "main", "main")]
cov += ['<aside>02 Git 기본 흐름에서 쓰던 hello-git 저장소로 이어서 실습해요. 이번엔 커밋을 점(노드)으로, 브랜치를 그 점에 붙은 이름표로 그려서 명령마다 무엇이 움직이는지 봐요.</aside>', '</section>']
W("cover", "\n".join(cov))

# ---------- toc ----------
parts = [("Lightbulb", "#3A4150", "#3A4150", "브랜치란?", "왜 쓰는지<br>이름표와 HEAD", "3–4쪽"),
         ("Link", "#1F8A4C", "#1A7340", "만들고 합치기", "checkout -b · merge<br>이름 규칙", "5–13쪽"),
         ("Activity", "#B26A00", "#8A5200", "갈라진 길 합치기", "merge 커밋", "14–17쪽"),
         ("Warning", "#A33131", "#A33131", "충돌 풀기", "충돌 표시 읽기<br>해결하고 커밋", "18–21쪽"),
         ("Cloud", "#6B47D6", "#5A3BB8", "GitHub에서 함께", "push · Pull Request<br>GitHub Flow", "22–26쪽"),
         ("Wrench", "#2459C9", "#1E3F8F", "막힐 때", "자주 나는 에러", "27–29쪽")]
t = [f'<section id="toc" data-transition="fade" style="background:#F6F5F1;color:#1D2330;font-family:{SANS};padding:128px;display:flex;flex-direction:column;gap:56px">',
     '<h2 style="font-size:64px;font-weight:700;line-height:1.15;color:#1D2330">오늘의 순서</h2>', '<div style="display:flex;flex-direction:row;gap:20px;flex:1">']
for i, (ic, top, c, h, sub, pg) in enumerate(parts, 1):
    t.append(f'<div style="flex:1;display:flex;flex-direction:column;gap:14px;background:#FFFFFF;border:2px solid #E1DED6;border-top:12px solid {top};border-radius:20px;padding:28px 24px">'
             f'<x-icon name="{ic}" style="width:48px;height:48px;color:{c}"></x-icon>'
             f'<p style="font-size:64px;font-weight:900;line-height:1.15;color:{c}">{i}</p>'
             f'<h3 style="font-size:28px;font-weight:700;color:#1D2330">{h}</h3>'
             f'<p style="font-size:24px;line-height:1.5;color:#4A5262">{sub}</p><div style="flex:1"></div>'
             f'<p style="font-size:24px;color:#6A7180">{pg}</p></div>')
t += ['</div>', '<p style="font-size:26px;color:#4A5262">마지막 30쪽은 한 장 요약이에요.</p>',
      '<aside>02와 같은 hello-git 저장소로 이어서 실습해요. 2~5부는 커밋 그래프 하나가 계속 자라는 이야기예요.</aside>', '</section>']
W("toc", "\n".join(t))

# ---------- why ----------
w = [sec("why"), head("브랜치란?", "왜 브랜치를 쓸까요?")]
w.append('<div style="position:absolute;left:96px;top:260px;width:840px;height:560px;background:#FFFFFF;border:2px solid #E07A7A;border-radius:24px"></div>')
w.append('<div style="position:absolute;left:984px;top:260px;width:840px;height:560px;background:#FFFFFF;border:2px solid #9ED3B4;border-radius:24px"></div>')
w.append(f'<div style="position:absolute;left:136px;top:296px;width:760px;display:flex;flex-direction:row;gap:14px;align-items:center"><x-icon name="Warning" style="width:44px;height:44px;color:#A33131"></x-icon><h3 style="font-size:34px;font-weight:700;color:#A33131">모두 main에 바로 커밋</h3></div>')
w.append(f'<div style="position:absolute;left:1024px;top:296px;width:760px;display:flex;flex-direction:row;gap:14px;align-items:center"><x-icon name="CheckCircle" style="width:44px;height:44px;color:#1A7340"></x-icon><h3 style="font-size:34px;font-weight:700;color:#1A7340">각자 브랜치에서 작업</h3></div>')
cols = [BL, GR, OR, GR, BL, OR, GR]
y = 560
w.append(hline(176, 856, y, "#D5D9E0"))
for i, c in enumerate(cols):
    w.append(node(176 + i * 113, y, c, 22))
w.append(pill(856, y + 40, "main", "main"))
w.append('<div style="position:absolute;left:136px;top:700px;width:760px;display:flex;flex-direction:column;gap:12px">'
         '<p style="font-size:28px;line-height:1.4;color:#1D2330">반쯤 만든 기능이 main에 섞여요</p>'
         '<p style="font-size:28px;line-height:1.4;color:#1D2330">누구 작업이 문제인지 찾기 어려워요</p></div>')
ym, yg, yo = 600, 450, 450
w += [hline(1064, 1744, ym, BLL), conn(1150, ym, 1250, yg, GRL), hline(1250, 1370, yg, GRL), conn(1370, yg, 1470, ym, GRL),
      conn(1470, ym, 1570, yo, ORL), hline(1570, 1640, yo, ORL), conn(1640, yo, 1744, ym, ORL)]
for x in (1064, 1150, 1470, 1744):
    w.append(node(x, ym, BL, 22, "merge" if x in (1470, 1744) else "n"))
for x in (1250, 1370):
    w.append(node(x, yg, GR, 22))
for x in (1570, 1640):
    w.append(node(x, yo, OR, 22))
w += [pill(1310, yg - 66, "feat/login", "green"), pill(1605, yo - 66, "fix/typo", "orange"), pill(1744, ym + 40, "main", "main")]
w.append('<div style="position:absolute;left:1024px;top:700px;width:760px;display:flex;flex-direction:column;gap:12px">'
         '<p style="font-size:28px;line-height:1.4;color:#1D2330">다 만든 다음에 main으로 합쳐요</p>'
         '<p style="font-size:28px;line-height:1.4;color:#1D2330">main은 늘 잘 돌아가는 상태로 남아요</p></div>')
w.append('<p style="position:absolute;left:96px;top:868px;width:1728px;font-size:28px;font-weight:700;color:#1D2330">브랜치 = 본 줄기(main)는 그대로 두고, 옆으로 갈래를 내서 작업하는 방법</p>')
w.append('<aside>왼쪽은 세 사람이 main 하나에 번갈아 커밋한 모습이에요. 색이 섞여 있죠. 오른쪽은 각자 갈래(브랜치)에서 작업하고 끝나면 합친 모습이에요. 흰 점은 두 줄기를 합친 커밋이에요. 혼자 일할 때도 실험은 브랜치에서 하면 main을 망가뜨릴 걱정이 없어요.</aside></section>')
W("why", "\n".join(w))

# ---------- naming ----------
n = [sec("naming"), head("만들고 합치기 · 이름 짓기", "브랜치 이름은 타입/하는 일")]
n.append(f'<div style="position:absolute;left:96px;top:250px;width:1728px;height:150px;background:#1D2330;border-radius:24px;display:flex;flex-direction:row;align-items:center;gap:8px;padding:0 48px">'
         f'<p style="font-family:{MONO};font-size:56px;font-weight:700;color:#7FD18B">feat</p>'
         f'<p style="font-family:{MONO};font-size:56px;font-weight:700;color:#BFC6D4">/</p>'
         f'<p style="font-family:{MONO};font-size:56px;font-weight:700;color:#F2C46D">login-button</p><div style="flex:1"></div>'
         f'<p style="font-size:26px;color:#BFC6D4">타입 · 슬래시 · 하는 일(소문자, 하이픈)</p></div>')
types = [("feat/", "새 기능", "feat/login-button", "#1A7340"), ("fix/", "버그 수정", "fix/signup-error", "#A33131"),
         ("docs/", "문서", "docs/readme-install", "#1E3F8F"), ("refactor/", "구조 개선", "refactor/user-api", "#8A5200"),
         ("chore/", "설정, 패키지", "chore/eslint-setup", "#4A5262")]
n.append('<div style="position:absolute;left:96px;top:440px;width:1728px;display:flex;flex-direction:row;gap:16px">')
for a, b, c, col in types:
    n.append(f'<div style="flex:1;display:flex;flex-direction:column;gap:10px;background:#FFFFFF;border:2px solid #E1DED6;border-radius:18px;padding:22px 20px">'
             f'<p style="font-family:{MONO};font-size:34px;font-weight:700;color:{col}">{a}</p>'
             f'<p style="font-size:26px;font-weight:700;color:#1D2330">{b}</p>'
             f'<p style="font-family:{MONO};font-size:24px;color:#4A5262">{c}</p></div>')
n.append('</div>')
n.append('<div style="position:absolute;left:96px;top:700px;width:1728px;display:flex;flex-direction:row;gap:24px">')
n.append(f'<div style="flex:1;display:flex;flex-direction:column;gap:12px;background:#F1FAF4;border:2px solid #4DB57A;border-radius:18px;padding:24px 28px">'
         f'<div style="display:flex;flex-direction:row;gap:12px;align-items:center"><x-icon name="CheckCircle" style="width:36px;height:36px;color:#1A7340"></x-icon><p style="font-size:28px;font-weight:700;color:#1A7340">이렇게</p></div>'
         f'<p style="font-family:{MONO};font-size:26px;color:#1D2330">feat/login-button</p>'
         f'<p style="font-family:{MONO};font-size:26px;color:#1D2330">fix/12-signup-error <span style="color:#6A7180">(이슈 12번)</span></p></div>')
n.append(f'<div style="flex:1;display:flex;flex-direction:column;gap:12px;background:#FBE4E2;border:2px solid #E07A7A;border-radius:18px;padding:24px 28px">'
         f'<div style="display:flex;flex-direction:row;gap:12px;align-items:center"><x-icon name="Warning" style="width:36px;height:36px;color:#A33131"></x-icon><p style="font-size:28px;font-weight:700;color:#A33131">이건 피해요</p></div>'
         f'<p style="font-family:{MONO};font-size:26px;color:#1D2330">test, 내작업, final2 <span style="color:#6A7180">(무슨 일인지 모름)</span></p>'
         f'<p style="font-family:{MONO};font-size:26px;color:#1D2330">Feat/Login Button <span style="color:#6A7180">(대문자, 띄어쓰기)</span></p></div>')
n.append('</div>')
n.append('<aside>앞부분 타입은 커밋 메시지 규칙(feat, fix, docs …)과 같은 말을 써요. 브랜치 이름만 봐도 무슨 작업인지 알 수 있어요. 띄어쓰기는 명령어에서 이름이 끊기니 하이픈(-)으로 이어요. 대문자는 운영체제에 따라 헷갈릴 수 있어 소문자로 통일해요. 이슈 번호를 쓰는 팀이면 fix/12-signup-error처럼 앞에 붙여요. 팀에 정해진 규칙이 있으면 그걸 따라요.</aside></section>')
W("naming", "\n".join(n))

# ---------- merge-kinds ----------
m = [sec("merge-kinds", "#ECEAE3"), head("개념 정리", "merge는 두 가지 모습으로 끝나요")]
for i, (title, sub, col) in enumerate([("Fast-forward", "main에 새 커밋이 없을 때<br>이름표만 앞으로 당겨요", BL), ("merge 커밋", "양쪽에 새 커밋이 있을 때<br>둘을 잇는 커밋을 새로 만들어요", OR)]):
    L = 96 + i * 888
    m.append(f'<div style="position:absolute;left:{L}px;top:260px;width:840px;height:600px;background:#FDFCF9;border-radius:24px"></div>')
    m.append(f'<h3 style="position:absolute;left:{L+40}px;top:296px;width:760px;font-size:36px;font-weight:700;color:{col}">{title}</h3>')
    m.append(f'<p style="position:absolute;left:{L+40}px;top:720px;width:760px;font-size:28px;line-height:1.45;color:#1D2330">{sub}</p>')
# FF
ym, yu = 560, 430
m += [hline(176, 400, ym, BLL), conn(400, ym, 520, yu, GRL), hline(520, 660, yu, GRL)]
for x in (176, 288, 400): m.append(node(x, ym, BL, 22))
for x in (520, 660): m.append(node(x, yu, GR, 22))
m += [pill(400, ym + 40, "main", "main", ' data-build-in="fade order 1"' if False else ''),
      pill(660, yu - 66, "feat", "green")]
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
m.append('<aside>왼쪽은 실습 7, 오른쪽은 실습 11의 모습이에요. merge 커밋(흰 점)은 부모가 둘이라 두 줄기의 기록을 모두 품고 있어요. 팀 작업에서는 GitHub의 Pull Request로 합칠 때 대부분 오른쪽처럼 merge 커밋이 생겨요.</aside></section>')
W("merge-kinds", "\n".join(m))

# ---------- conflict-read ----------
c = [sec("conflict-read", "#ECEAE3"), head("충돌 풀기", "충돌 표시 읽는 법", "#A33131")]
lines = [("<<<<<<< HEAD", "#F28B82"), ("hi", "#8FB3FF"), ("=======", "#F28B82"), ("안녕", "#7FD18B"), (">>>>>>> feat/korean", "#F28B82"), ("world", "#D8DEE9"), ("nice to meet you", "#D8DEE9")]
c.append(f'<div style="position:absolute;left:96px;top:260px;width:760px;height:600px;background:#1B2029;border-radius:24px"></div>')
c.append(f'<p style="position:absolute;left:136px;top:290px;width:600px;font-size:24px;color:#9AA3B5">hello.md</p>')
for i, (tx, col) in enumerate(lines):
    c.append(f'<p style="position:absolute;left:136px;top:{350 + i*64}px;width:680px;font-family:{MONO};font-size:36px;font-weight:700;line-height:1.4;color:{col}">{tx}</p>')
notes = [(0, 1, "#2459C9", "지금 내 브랜치(main) 내용"), (3, 4, "#1F8A4C", "합치려는 브랜치(feat/korean) 내용")]
for k, (a, b, col, txt) in enumerate(notes):
    y1, y2 = 350 + a*64, 350 + b*64 + 50
    c.append(f'<div data-build-in="fade order {k+1}" style="position:absolute;left:880px;top:{y1}px;width:10px;height:{y2-y1}px;background:{col};border-radius:5px"></div>')
    c.append(f'<p data-build-in="fade order {k+1}" style="position:absolute;left:912px;top:{(y1+y2)//2 - 20}px;width:420px;font-size:28px;font-weight:700;color:{col}">{txt}</p>')
c.append(f'<div data-build-in="rise order 3" style="position:absolute;left:1360px;top:260px;width:464px;height:600px;background:#FFFFFF;border-radius:24px;padding:36px;display:flex;flex-direction:column;gap:22px">'
         f'<h3 style="font-size:32px;font-weight:700;color:#1D2330">푸는 순서</h3>'
         f'<p style="font-size:26px;line-height:1.4;color:#1D2330"><span style="color:#A33131">1</span> 남길 내용으로 고치기<br><span style="color:#6A7180">둘 다 남겨도 돼요</span></p>'
         f'<p style="font-size:26px;line-height:1.4;color:#1D2330"><span style="color:#A33131">2</span> 표시 세 줄 지우고 저장</p>'
         f'<p style="font-family:{MONO};font-size:26px;line-height:1.4;color:#1D2330"><span style="color:#A33131;font-family:{SANS}">3</span> git add hello.md</p>'
         f'<p style="font-family:{MONO};font-size:26px;line-height:1.4;color:#1D2330"><span style="color:#A33131;font-family:{SANS}">4</span> git commit -m "..."</p></div>')
c.append('<p style="position:absolute;left:96px;top:900px;width:1728px;font-size:26px;font-weight:700;color:#A33131">&lt;&lt;&lt;&lt;&lt;&lt;&lt;, =======, &gt;&gt;&gt;&gt;&gt;&gt;&gt; 줄이 남은 채로 커밋하지 않아요.</p>')
c.append('<aside>HEAD는 지금 서 있는 브랜치예요. 위쪽이 내 것, 아래쪽이 가져오려는 것이에요. VS Code로 열면 Accept Current Change(내 것), Accept Incoming Change(가져온 것), Accept Both Changes(둘 다) 버튼이 떠서 클릭으로 골라도 돼요. 고른 뒤에도 저장하고 add, commit 하는 건 똑같아요.</aside></section>')
W("conflict-read", "\n".join(c))

# ---------- pr-flow ----------
f = [sec("pr-flow"), head("GitHub에서 함께", "팀에서는 이 순서로 일해요", "#6B47D6")]
steps = [("Link", "git checkout -b<br>feat/emoji", "브랜치 만들기", "#2459C9", "#F0F5FE", "#5B8DEF"),
         ("Code", "add, commit", "작업하고 커밋", "#2459C9", "#F0F5FE", "#5B8DEF"),
         ("Cloud", "git push origin<br>feat/emoji", "브랜치 올리기", "#2459C9", "#F0F5FE", "#5B8DEF"),
         ("Chat", "Pull Request", "합쳐 달라고 요청", "#5A3BB8", "#F6F2FE", "#9A7BF0"),
         ("Users", "리뷰 → Merge", "확인하고 합치기", "#5A3BB8", "#F6F2FE", "#9A7BF0"),
         ("Home", "git checkout main<br>git pull origin main", "내 main 맞추기", "#2459C9", "#F0F5FE", "#5B8DEF")]
for i, (ic, cmd, lab, col, bg, bd) in enumerate(steps):
    L = 96 + i * 292
    f.append(f'<div data-build-in="rise order {i+1}" style="position:absolute;left:{L}px;top:330px;width:260px;height:400px;background:{bg};border:2px solid {bd};border-radius:22px;padding:28px 22px;display:flex;flex-direction:column;gap:16px">'
             f'<p style="font-size:44px;font-weight:900;line-height:1.15;color:{col}">{i+1}</p>'
             f'<x-icon name="{ic}" style="width:52px;height:52px;color:{col}"></x-icon>'
             f'<p style="font-size:28px;font-weight:700;color:#1D2330">{lab}</p>'
             f'<p style="font-family:{MONO};font-size:24px;line-height:1.4;font-weight:700;color:{col}">{cmd}</p></div>')
f.append('<div style="position:absolute;left:96px;top:270px;width:844px;height:6px;background:#5B8DEF;border-radius:3px"></div>')
f.append('<p style="position:absolute;left:96px;top:226px;width:500px;font-size:24px;font-weight:700;color:#1E3F8F">내 컴퓨터</p>')
f.append('<div style="position:absolute;left:972px;top:270px;width:552px;height:6px;background:#9A7BF0;border-radius:3px"></div>')
f.append('<p style="position:absolute;left:972px;top:226px;width:500px;font-size:24px;font-weight:700;color:#5A3BB8">GitHub 웹사이트</p>')
f.append('<div style="position:absolute;left:1556px;top:270px;width:268px;height:6px;background:#5B8DEF;border-radius:3px"></div>')
f.append('<p style="position:absolute;left:1556px;top:226px;width:268px;font-size:24px;font-weight:700;color:#1E3F8F">내 컴퓨터</p>')
f.append('<p style="position:absolute;left:96px;top:790px;width:1728px;font-size:30px;font-weight:700;color:#1D2330">main에는 직접 push하지 않고, 합치는 일은 Pull Request로 해요.</p>')
f.append('<aside>Pull Request(PR)는 "내 브랜치를 main에 합쳐 주세요"라는 요청서예요. 팀원이 바뀐 코드를 보고 의견을 남긴 뒤 합쳐요. 혼자 하는 프로젝트에서도 PR로 합치면 무엇을 언제 바꿨는지 기록이 깔끔하게 남아요.</aside></section>')
W("pr-flow", "\n".join(f))

# ---------- pr-github ----------
g = [sec("pr-github"), head("GitHub에서 함께", "Pull Request 화면에서 할 일", "#6B47D6")]
g.append('<div style="position:absolute;left:96px;top:260px;width:1100px;height:660px;background:#FFFFFF;border:2px solid #D0D7DE;border-radius:20px"></div>')
g.append(f'<p style="position:absolute;left:136px;top:296px;width:1020px;font-size:36px;font-weight:700;color:#1D2330">feat: 끝인사 하나 더 <span style="color:#6A7180">#1</span></p>')
g.append(f'<div style="position:absolute;left:136px;top:366px;width:1020px;display:flex;flex-direction:row;gap:12px;align-items:center">'
         f'<p style="font-size:24px;font-weight:700;color:#FFFFFF;background:#1F8A4C;padding:4px 16px;border-radius:20px">Open</p>'
         f'<p style="font-family:{MONO};font-size:24px;color:#1D2330;background:#DCE7FB;padding:4px 12px;border-radius:8px">main</p>'
         f'<p style="font-size:26px;color:#6A7180">←</p>'
         f'<p style="font-family:{MONO};font-size:24px;color:#1D2330;background:#FBEBD3;padding:4px 12px;border-radius:8px">feat/emoji</p></div>')
g.append('<div style="position:absolute;left:136px;top:440px;width:1020px;height:150px;background:#F6F8FA;border:2px solid #D0D7DE;border-radius:12px;padding:20px 24px;display:flex;flex-direction:column;gap:8px">'
         '<p style="font-size:24px;font-weight:700;color:#1D2330">설명</p><p style="font-size:24px;color:#4A5262">bye.md에 끝인사 한 줄을 더 넣었어요.</p></div>')
g.append(f'<div style="position:absolute;left:136px;top:614px;width:1020px;height:120px;background:#F6F8FA;border:2px solid #D0D7DE;border-radius:12px;padding:20px 24px;display:flex;flex-direction:column;gap:8px">'
         f'<p style="font-size:24px;font-weight:700;color:#1D2330">Files changed</p><p style="font-family:{MONO};font-size:24px;color:#1A7340">+ bye bye</p></div>')
g.append('<div style="position:absolute;left:136px;top:762px;width:1020px;display:flex;flex-direction:row;gap:16px;align-items:center">'
         '<p style="font-size:26px;font-weight:700;color:#FFFFFF;background:#1F8A4C;padding:12px 24px;border-radius:10px">Merge pull request</p>'
         '<p style="font-size:26px;font-weight:700;color:#1D2330;background:#F6F8FA;border:2px solid #D0D7DE;padding:10px 22px;border-radius:10px">Delete branch</p></div>')
anns = [(296, "제목: 커밋 메시지처럼 타입: 요약"), (366, "어디로 ← 무엇을 합치는지"), (440, "무엇을 왜 바꿨는지"), (614, "바뀐 줄 확인, 댓글로 리뷰"), (762, "합치고 나면 GitHub 브랜치 삭제")]
for i, (y, txt) in enumerate(anns):
    g.append(f'<div data-build-in="fade order {i+1}" style="position:absolute;left:1236px;top:{y}px;width:588px;display:flex;flex-direction:row;gap:14px;align-items:center">'
             f'<p style="width:44px;height:44px;flex:none;font-size:26px;font-weight:900;line-height:44px;text-align:center;color:#FFFFFF;background:#6B47D6;border-radius:22px">{i+1}</p>'
             f'<p style="font-size:26px;font-weight:700;color:#1D2330">{txt}</p></div>')
g.append('<aside>push 하면 GitHub 저장소 화면 위쪽에 Compare &amp; pull request 버튼이 떠요. 누르면 이 화면이 나와요. 화면 모양은 GitHub 업데이트에 따라 조금 다를 수 있어요. Merge pull request를 누르면 GitHub 안에서 merge 커밋이 생기고, 내 컴퓨터에는 다음 장처럼 pull로 받아요.</aside></section>')
W("pr-github", "\n".join(g))

# ---------- strategy ----------
s = [sec("strategy"), head("GitHub에서 함께 · 브랜치 전략", "우리는 GitHub Flow로 일해요", "#6B47D6")]
s.append('<div style="position:absolute;left:96px;top:260px;width:1728px;height:300px;background:#FDFCF9;border:2px solid #E1DED6;border-radius:24px"></div>')
ym, yu = 470, 340
s.append(hline(160, 1760, ym, BLL))
br = [(300, 560, "feat/login", "green", GR, GRL), (720, 980, "fix/12-signup-error", "orange", OR, ORL), (1140, 1440, "docs/readme-install", "green", GR, GRL)]
for k, (a, b, name, kind, col, light) in enumerate(br):
    s += [conn(a, ym, a + 90, yu, light), hline(a + 90, b - 90, yu, light), conn(b - 90, yu, b, ym, light)]
    s += [node(a + 90, yu, col, 18), node(b - 90, yu, col, 18), node(b, ym, BL, 20, "merge")]
    s.append(pill((a + b) // 2, yu - 62, name, kind))
for x in (160, 300, 720, 1140, 1760):
    s.append(node(x, ym, BL, 20))
s.append(pill(1760, ym + 36, "main", "main"))
rules = [("main은 늘 동작하는 상태.<br>직접 커밋하지 않아요", "Lock"), ("일 하나 = 브랜치 하나.<br>이름은 타입/하는 일", "Link"),
         ("작게 자주 Pull Request", "Chat"), ("merge 뒤 브랜치는 지워요", "CheckCircle")]
s.append('<div style="position:absolute;left:96px;top:600px;width:1728px;display:flex;flex-direction:row;gap:20px">')
for i, (txt, ic) in enumerate(rules):
    s.append(f'<div style="flex:1;display:flex;flex-direction:column;gap:14px;background:#FFFFFF;border:2px solid #E1DED6;border-radius:18px;padding:24px">'
             f'<x-icon name="{ic}" style="width:44px;height:44px;color:#5A3BB8"></x-icon>'
             f'<p style="font-size:26px;font-weight:700;line-height:1.4;color:#1D2330">{txt}</p></div>')
s.append('</div>')
s.append('<p style="position:absolute;left:96px;top:880px;width:1728px;font-size:24px;color:#4A5262">Git Flow(develop, release 브랜치를 따로 두는 방식)는 배포 일정이 복잡한 회사에서 써요. 처음엔 GitHub Flow면 충분해요.</p>')
s.append('<aside>GitHub Flow는 main 하나와 짧게 쓰고 지우는 작업 브랜치로만 일하는 방식이에요. 갈래가 길어질수록 main과 멀어져 충돌이 커지니, 하루 이틀 안에 합칠 수 있는 크기로 나눠요. GitHub 저장소 설정에서 main 브랜치 보호(Branch protection)를 켜면 main에 직접 push를 막고 PR로만 합치게 할 수 있어요.</aside></section>')
W("strategy", "\n".join(s))

# ---------- errors ----------
def errpage(i, eyebrow, title, panels, aside):
    o = [f'<section id="{i}" data-transition="fade" style="background:#ECEAE3;color:#1D2330;font-family:{SANS};padding:112px 128px;display:flex;flex-direction:column;gap:40px">',
         f'<div style="display:flex;flex-direction:column;gap:12px"><p style="font-size:26px;font-weight:700;color:#A33131">{eyebrow}</p>'
         f'<h2 style="font-size:60px;font-weight:700;line-height:1.15;color:#1D2330">{title}</h2></div>',
         '<div style="display:flex;flex-direction:row;gap:32px;flex:1">']
    for ic, h, err, why, fixes in panels:
        o.append(f'<div style="flex:1;display:flex;flex-direction:column;gap:20px;background:#FDFCF9;border-radius:20px;padding:32px">'
                 f'<div style="display:flex;flex-direction:row;gap:16px;align-items:center"><x-icon name="{ic}" style="width:48px;height:48px;color:#A33131"></x-icon><h3 style="font-size:30px;font-weight:700;color:#1D2330">{h}</h3></div>'
                 f'<p style="font-family:{MONO};font-size:24px;line-height:1.4;color:#F28B82;background:#1B2029;padding:16px 20px;border-radius:12px">{err}</p>'
                 f'<p style="font-size:26px;line-height:1.45;color:#4A5262">{why}</p><div style="flex:1"></div>'
                 + "".join(code(x) for x in fixes) + '</div>')
    o += ['</div>', f'<aside>{aside}</aside>', '</section>']
    W(i, "\n".join(o))

errpage("err-name", "에러 1 · 브랜치 이름", "옮기려는데, 만들려는데 안 돼요",
        [("Search", "없는 브랜치로 옮김", "$ git checkout feat/nope<br>error: pathspec 'feat/nope' did not match any file(s) known to git",
          "이름 오타이거나 아직 안 만든 브랜치예요", ["git branch", "git checkout -b feat/nope"]),
         ("Link", "이미 있는 이름으로 만듦", "$ git checkout -b feat/a<br>fatal: a branch named 'feat/a' already exists",
          "같은 이름이 벌써 있어요. -b 없이 옮겨 가요", ["git checkout feat/a"])],
        "pathspec 에러는 Git이 브랜치도 파일도 못 찾았다는 뜻이에요. git branch로 목록을 보고 철자를 확인해요. 새로 만들 생각이었다면 -b를 붙여요. already exists는 반대로 이미 있는 이름에 -b를 붙였을 때 나요.")
errpage("err-dirty", "에러 2 · 커밋 안 한 변경", "브랜치를 옮기려는데 막혀요",
        [("Warning", "고친 파일이 그대로 있음", "error: Your local changes to the following files would be overwritten by checkout:<br>&#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;hello.md<br>Please commit your changes or stash them before you switch branches.<br>Aborting",
          "옮겨 가면 고친 내용이 덮어써져서 Git이 멈췄어요. 먼저 커밋하고 옮겨요", ["git add hello.md", 'git commit -m "feat: ..."', "git checkout feat/b"])],
        "옮겨 갈 브랜치에서 같은 파일 내용이 다를 때만 나요. 고친 내용을 잃지 않게 지켜 주는 에러예요. 작업이 덜 끝났어도 지금 브랜치에 커밋해 두고 옮기면 돼요. 메시지에 나오는 stash(잠깐 치워 두기)는 이 과정에서 다루지 않아요.")
errpage("err-unmerged", "에러 3 · 브랜치 지우기", "브랜치가 안 지워져요",
        [("Lock", "아직 합치지 않은 커밋이 있음", "$ git branch -d feat/a<br>error: the branch 'feat/a' is not fully merged.<br>If you are sure you want to delete it, run 'git branch -D feat/a'",
          "지우면 그 커밋을 잃을 수 있어서 Git이 멈췄어요", ["git checkout main", "git merge feat/a", "git branch -d feat/a"])],
        "합치고 지우는 게 기본이에요. 정말 버릴 작업일 때만 대문자 -D로 강제로 지워요. GitHub에서 PR을 merge했는데도 이 에러가 나면, 먼저 git checkout main 후 git pull origin main으로 내 main을 최신으로 맞추고 다시 지워 봐요.")

# ---------- cheatsheet ----------
ch = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:#1D2330;font-family:{SANS};padding:112px 128px;display:flex;flex-direction:column;gap:40px">',
      '<h2 style="font-size:64px;font-weight:700;line-height:1.15;color:#1D2330">한 장 요약</h2>', '<div style="display:flex;flex-direction:row;gap:24px;flex:1">']
cards = [("브랜치", "#1A7340", "#FFFFFF", "#1D2330", "git branch<br>git checkout -b 이름<br>git checkout 이름<br>git branch -d 이름"),
         ("합치기", "#2459C9", "#FFFFFF", "#1D2330", "git checkout main<br>git merge 이름"),
         ("충돌", "#A33131", "#FFFFFF", "#1D2330", "파일에서 고르기<br>표시 세 줄 지우기<br>git add 파일<br>git commit -m &quot;...&quot;"),
         ("GitHub과 함께", "#F6F5F1", "#1D2330", "#F2C46D", "git push origin 이름<br>→ Pull Request<br>→ Merge<br>git checkout main<br>git pull origin main")]
for h, hc, bg, tc, body in cards:
    bd = "" if bg == "#1D2330" else "border:2px solid #E1DED6;"
    ch.append(f'<div style="flex:1;display:flex;flex-direction:column;gap:16px;background:{bg};{bd}border-radius:20px;padding:32px 28px">'
              f'<h3 style="font-size:32px;font-weight:700;color:{hc}">{h}</h3>'
              f'<p style="font-family:{MONO};font-size:24px;line-height:1.7;color:{tc}">{body}</p></div>')
ch += ['</div>', f'<p style="font-size:28px;font-weight:700;color:#1D2330">브랜치 이름: <span style="color:#1A7340">feat/login-button</span> · main에는 직접 커밋하지 않기</p>',
       '<aside>수업 끝에 이 장을 띄워 두고, 칠판에 그래프를 그리며 명령마다 이름표와 HEAD가 어디로 가는지 학생이 직접 말해 보게 하세요.</aside>', '</section>']
W("cheatsheet", "\n".join(ch))
print("pages ok")

# ---------- merge-how ----------
h = [sec("merge-how"), head("만들고 합치기 · merge", "merge는 받는 쪽에서 해요")]
h.append('<div style="position:absolute;left:96px;top:240px;width:1728px;height:400px;background:#FDFCF9;border:2px solid #E1DED6;border-radius:24px"></div>')
ym, yu = 500, 360
h += [hline(240, 600, ym, BLL), conn(600, ym, 760, yu, GRL), hline(760, 940, yu, GRL)]
for x, hs in ((240, "560eba8"), (420, "1180617"), (600, "feff88d")):
    h.append(node(x, ym, BL, 22))
    h.append(f'<p style="position:absolute;left:{x-80}px;top:{ym+30}px;width:160px;font-family:{MONO};font-size:24px;font-weight:700;text-align:center;color:#1D2330">{hs}</p>')
for x, hs in ((760, "7ca17f8"), (940, "171d9dc")):
    h.append(node(x, yu, GR, 22))
    h.append(f'<p style="position:absolute;left:{x-80}px;top:{yu+30}px;width:160px;font-family:{MONO};font-size:24px;font-weight:700;text-align:center;color:#1D2330">{hs}</p>')
h.append(pill(940, yu - 66, "feat/greeting", "green"))
h.append(pill(560, ym + 72, "main", "main"))
h.append(pill(668, ym + 72, "HEAD", "head", ' data-build-in="fade order 1"'))
h.append(conn(905, yu + 22, 640, ym - 14, GR, ' data-build-in="fade order 2" head="end"').replace('border-width:6px', 'border-width:5px;border-style:dashed'))
h.append(f'<p data-build-in="fade order 2" style="position:absolute;left:790px;top:450px;width:200px;font-size:26px;font-weight:700;color:#1A7340">가져와요</p>')
leg = [("main", "main", "받는 쪽", "먼저 checkout으로 가 있는 브랜치"), ("feat/greeting", "green", "가져올 쪽", "git merge 뒤에 적는 이름")]
for i, (t, k, a, b) in enumerate(leg):
    y = 300 + i * 150
    h.append(f'<div data-build-in="fade order {i+1}" style="position:absolute;left:1140px;top:{y}px;width:640px;display:flex;flex-direction:column;gap:8px">'
             f'<p style="font-size:30px;font-weight:700;color:{BL if i == 0 else "#1A7340"}">{a}</p>'
             f'<p style="font-size:26px;color:#4A5262">{b}</p></div>')
h.append('<div style="position:absolute;left:1100px;top:290px;width:4px;height:300px;background:#E1DED6"></div>')
steps = [("1", "받을 브랜치로 이동", "git checkout main", BL), ("2", "가져올 브랜치 이름을 적어요", "git merge feat/greeting", GR)]
h.append('<div style="position:absolute;left:96px;top:680px;width:1728px;display:flex;flex-direction:row;gap:24px">')
for n_, t, cmd, col in steps:
    h.append(f'<div data-build-in="rise order {n_}" style="flex:1;display:flex;flex-direction:row;gap:24px;align-items:center;background:#FFFFFF;border:2px solid #E1DED6;border-radius:20px;padding:28px 32px">'
             f'<p style="width:64px;height:64px;flex:none;font-size:34px;font-weight:900;line-height:64px;text-align:center;color:#FFFFFF;background:{col};border-radius:32px">{n_}</p>'
             f'<div style="display:flex;flex-direction:column;gap:12px"><p style="font-size:28px;font-weight:700;color:#1D2330">{t}</p>'
             f'<p style="font-family:{MONO};font-size:30px;font-weight:700;color:#1D2330">{cmd}</p></div></div>')
h.append('</div>')
h.append('<p style="position:absolute;left:96px;top:900px;width:1728px;font-size:28px;font-weight:700;color:#1D2330">02에서 본 git pull origin main도 받아 온 커밋을 이 방식으로 merge해요.</p>')
h.append('<aside>git merge 이름은 그 이름의 커밋을 지금 내가 있는 브랜치로 가져와요. 그래서 순서가 중요해요. 먼저 받을 쪽(main)으로 checkout하고, 그다음 가져올 브랜치 이름을 적어요. 반대로 feat/greeting에 있는 채로 git merge main을 치면 main의 커밋이 feat/greeting으로 들어가요. 02에서 git pull origin main을 배울 때 merge는 03에서 본다고 했죠. pull은 GitHub의 main을 받아 온 뒤 지금 브랜치로 merge해요.</aside></section>')
W("merge-how", "\n".join(h))
