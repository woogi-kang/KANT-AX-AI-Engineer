"""Generates every slide of the git diff deck.

Layout follows tools/DESIGN.md (Stageshow rules): one hero per slide (usually the real terminal output),
labels written straight onto the terminal rows instead of side cards, and the zone stack on the right is a
quiet satellite that only shows which two places a command compares.
Terminal output comes from tools/demo.sh (git 2.43).
Usage: python3 tools/gen.py slides
"""
import html, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from highlight import (spot, spot_off, box, underline, lspot, lspot_off, pulse, shake, shine, keys,  # noqa: E402
                       SLAM, STAGGER, WIPE, DELAY, DIM)
from highlight import MARK as MARK_IN  # noqa: E402

OUT = sys.argv[1]
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
INK, SUB, MUTE, LINE = "#1D2330", "#4A5262", "#6A7180", "#E1DED6"
BG = "#F6F5F1"
BL, BLL, GR, GRL, OR, RED, PUR = "#2459C9", "#9DB8F2", "#1F8A4C", "#9ED3B4", "#B26A00", "#A33131", "#5A3BB8"
C_WD, C_ST = "#A33131", "#1A7340"          # git diff = red side, git diff --staged = green side
NAVY = "#1E3F8F"


def e(s):
    return html.escape(s, quote=False)


def p(style, text, attrs=""):
    return f'<p{attrs} style="{style}">{text}</p>'


def W(name, parts, notes):
    body = "\n".join(parts) + f"\n<aside>{e(notes)}</aside>\n</section>\n"
    open(os.path.join(OUT, name + ".html"), "w").write(body)


def sec(i, transition="fade"):
    return f'<section id="{i}" data-transition="{transition}" style="background:{BG};color:{INK};font-family:{SANS}">'


def head(eyebrow, title, color=BL, mono=False, size=None):
    size = size or (50 if mono else 54)
    fam = f"font-family:{MONO};" if mono else ""
    return [p(f"position:absolute;left:96px;top:56px;width:1728px;font-size:24px;font-weight:700;color:{color}", e(eyebrow), ' id="eyebrow"'),
            f'<h2 id="title" style="position:absolute;left:96px;top:96px;width:1728px;{fam}font-size:{size}px;font-weight:700;line-height:1.2;color:{INK}">{title}</h2>']


def cap(top, html_text, left=96, w=1728, size=30, color=SUB, attrs=""):
    return p(f"position:absolute;left:{left}px;top:{top}px;width:{w}px;font-size:{size}px;line-height:1.45;color:{color}", html_text, attrs)


def tw(s, size):
    """Rough width of a mono string: latin = 0.6em, Korean = 1em."""
    return sum((1.0 if ord(c) > 0x2E80 else 0.6) for c in s.replace("\t", "        ")) * size


# ---------- terminal ----------
TC = {"$": "#F2C46D", "o": "#D8DEE9", "h": "#FFFFFF", "c": "#7CC7E8", "r": "#F28B82", "g": "#7FD18B", "#": "#8C95A6"}
HLC = {"r": "rgba(242,139,130,.20)", "g": "rgba(127,209,139,.20)", "c": "rgba(124,199,232,.18)", "y": "rgba(242,196,109,.20)"}


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


class Term:
    """A terminal that hugs its lines. Row geometry is kept so labels, tints and pen marks land on a row."""

    def __init__(self, lines, left=96, top=232, w=1104, size=28, lh=1.45, tid="term", padx=32, pady=24, ids=None):
        self.lines, self.left, self.top, self.w, self.size, self.tid = lines, left, top, w, size, tid
        self.ids = ids or {}
        self.rh, self.padx, self.pady = round(size * lh, 1), padx, pady
        self.h = round(pady * 2 + self.rh * len(lines))
        self.extra = []

    @property
    def bottom(self):
        return self.top + self.h

    def y(self, i):
        return self.top + self.pady + i * self.rh

    def text_end(self, i):
        k, t = self.lines[i]
        return self.left + self.padx + tw(("$ " if k == "$" else "") + t, self.size)

    def tint(self, i, n=1, color="g", order=1):
        """Tints rows i..i+n-1 (line highlight). Drawn inside the terminal, under the text."""
        at = f' data-build-in="fade order {order}"' if order else ""
        self.extra.append(f'<div{at} style="position:absolute;left:12px;top:{self.pady + i * self.rh - 2:.0f}px;width:{self.w - 24}px;height:{self.rh * n + 4:.0f}px;background:{HLC[color]};border-radius:8px"></div>')

    def label(self, i, text, color="#FFFFFF", sub=None, order=1, x=None, n=1):
        """A note written on the terminal's empty right side, tied to row i by a fine leader ending in a dot."""
        at = f' data-build-in="fade order {order}"' if order else ""
        lx = (x or (self.left + self.w - 470)) - self.left
        end = max(self.text_end(i + k) for k in range(n)) - self.left + 26
        cy = self.pady + (i + n / 2) * self.rh
        lead = ""
        if n > 1:
            lead += f'<div style="position:absolute;left:{end - 4:.0f}px;top:{self.pady + i * self.rh + 6:.0f}px;width:3px;height:{self.rh * n - 12:.0f}px;background:#5C6575;border-radius:2px"></div>'
            end += 2
        if lx - end > 40:
            lead += f'<div style="position:absolute;left:{end:.0f}px;top:{cy - 1:.0f}px;width:{lx - end - 14:.0f}px;height:2px;background:#5C6575"></div>'
            if n == 1:
                lead += f'<div style="position:absolute;left:{end - 4:.0f}px;top:{cy - 5:.0f}px;width:10px;height:10px;border-radius:5px;background:#8C95A6"></div>'
        s = f'<span style="font-weight:700;color:{color}">{text}</span>'
        if sub:
            s += f'<span style="font-weight:400;color:#AEB6C4;margin-left:14px">{sub}</span>'
        hh = self.rh * n
        self.extra.append(f'<div{at}>{lead}<p style="position:absolute;left:{lx:.0f}px;top:{self.pady + i * self.rh:.0f}px;width:{self.w - lx - 24:.0f}px;height:{hh:.0f}px;'
                          f'display:flex;align-items:center;font-family:{SANS};font-size:{min(26, self.size)}px;line-height:1.3;white-space:nowrap">{s}</p></div>')

    def box(self, i, n=1, x0=None, x1=None):
        """Slide coordinates of rows i..i+n-1, for ring/box/spot."""
        x0 = x0 if x0 is not None else self.left + self.padx - 10
        x1 = x1 if x1 is not None else max(self.text_end(i + k) for k in range(n)) + 10
        return (round(x0), round(self.y(i)), round(x1 - x0), round(self.rh * n))

    def pen(self, i, n=1, order=1, x0=None, color=RED):
        """A pen-drawn box around rows (rows sit close together, so box() rather than ring())."""
        x, y, ww, hh = self.box(i, n, x0=x0)
        return box(order, x - 4, y - 2, ww + 8, hh + 4, color, 4)

    def html(self, attrs=""):
        o = [f'<div id="{self.tid}"{attrs} style="position:absolute;left:{self.left}px;top:{self.top}px;width:{self.w}px;height:{self.h}px;background:#1B2029;border-radius:20px;padding:{self.pady}px {self.padx}px;display:flex;flex-direction:column;font-family:{MONO};font-variant-ligatures:none">']
        o += self.extra
        for k_, (kind, text) in enumerate(self.lines):
            t = e(text).replace("\t", "        ")
            if kind == "$":
                t = "$ " + t
            bold = "font-weight:700;" if kind in "h$" else ""
            rid = f' id="{self.ids[k_]}"' if k_ in self.ids else ""
            o.append(p(f"position:relative;font-size:{self.size}px;line-height:{self.rh}px;white-space:pre;{bold}color:{TC[kind]}", t if t else " ", rid))
        o.append('</div>')
        return "".join(o)


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
SHOW = """commit 7e5303ce32924d91ff86f6f48d7f1d1af808f9ae (HEAD -> main)
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
H0, H1, HB, HM, HR = "e12ffc2", "7e5303c", "acf05c1", "73080d0", "c36ee83"

V1 = ["# 로그인", "아이디", "비밀번호"]
V2 = ["# 로그인", "아이디", "비밀번호 (8자 이상)", "로그인 버튼"]
V3 = V2 + ["아이디 저장"]

# ---------- zone stack (satellite on the right of diff scenes) ----------
Z = {
    "wd": dict(title="① 작업 폴더", bg="#FDFCF9", bd="#9AA0AB", tc="#3A4150", icon="Code"),
    "st": dict(title="② 대기실", bg="#F1FAF4", bd="#4DB57A", tc="#1A7340", icon="CheckCircle"),
    "lr": dict(title="③ 내 저장소", bg="#F0F5FE", bd="#5B8DEF", tc=NAVY, icon="Database"),
}
ZL, ZW, ZH, ZG = 1248, 576, 236, 30
ZT = {"wd": 232, "st": 232 + ZH + ZG, "lr": 232 + 2 * (ZH + ZG)}
CL_H, CL_TOP = 30, 62          # card line height, first line offset inside a card
MARK = {"add": "background:#DDF2E5;color:#14532D", "del": "background:#FBE4E2;color:#7A1F1F", "dim": "color:#9AA0AB", None: f"color:{INK}"}


def zcard(k, tag, lines=None, marks=None, empty=None, dim=False):
    z = Z[k]
    marks = marks or {}
    op = "opacity:.4;" if dim else ""
    o = [f'<div id="z-{k}" style="position:absolute;left:{ZL}px;top:{ZT[k]}px;width:{ZW}px;height:{ZH}px;{op}background:{z["bg"]};border:2px solid {z["bd"]};border-radius:18px;padding:14px 22px;display:flex;flex-direction:column">',
         '<div style="height:40px;display:flex;flex-direction:row;gap:10px;align-items:center">'
         f'<x-icon name="{z["icon"]}" style="width:28px;height:28px;color:{z["tc"]}"></x-icon>'
         + p(f"font-size:26px;font-weight:700;color:{z['tc']}", z["title"]) + '<div style="flex:1"></div>'
         + p(f"font-family:{MONO};font-size:20px;font-weight:700;color:{MUTE}", e(tag)) + '</div>',
         '<div style="height:6px"></div>']
    if empty:
        o.append(p(f"font-size:24px;font-weight:700;color:{z['tc']};margin-top:8px", e(empty[0])))
        o.append(p(f"font-size:22px;line-height:1.45;color:{SUB};margin-top:6px", empty[1]))
    else:
        for i, l in enumerate(lines):
            o.append(p(f"font-family:{MONO};font-size:21px;line-height:{CL_H}px;height:{CL_H}px;padding:0 8px;border-radius:5px;align-self:flex-start;{MARK[marks.get(i)]}", e(l)))
    o.append('</div>')
    return "".join(o)


def zline(k, i):
    """Slide y of line i inside zone card k."""
    return ZT[k] + CL_TOP + i * CL_H


def chip(a, b, label, color, cid="chip", order=1):
    """Command pill straddling the gap between the two cards it compares."""
    top_card = min((a, b), key=lambda k: ZT[k])
    y = ZT[top_card] + ZH + ZG // 2 - 24
    w = round(tw(label, 26) + 72)
    at = f' data-build-in="fade order {order}"' if order else ""
    return (f'<div id="{cid}"{at} style="position:absolute;left:{ZL + ZW // 2 - w // 2}px;top:{y}px;width:{w}px;height:48px;border-radius:24px;background:{color};'
            f'display:flex;flex-direction:row;gap:10px;align-items:center;justify-content:center;box-shadow:0 2px 6px rgba(0,0,0,.18)">'
            + p("font-size:24px;font-weight:700;color:#FFFFFF", "↕") + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:#FFFFFF", e(label)) + '</div>')


def ctop(n, size=30, lh=1.5, caph=46):
    """Top of a terminal (plus caption) centred beside the zone stack (232..1000)."""
    block = 48 + n * round(size * lh, 1) + (36 + caph if caph else 0)
    return max(232, round(232 + (768 - block) / 2))


def scene(sid, eyebrow, title, term, cards, chips, notes, extra=(), transition="magic", mono=True, tsize=None):
    o = [sec(sid, transition)] + head(eyebrow, title, mono=mono, size=tsize)
    o.append(term.html())
    o += cards
    o += chips
    o += list(extra)
    W(sid, o, notes)


# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:#1D2330;color:#F6F5F1;font-family:{SANS}">',
       p("position:absolute;left:128px;top:300px;width:900px;font-size:28px;font-weight:700;color:#8FB3FF", "KANT AX/AI 엔지니어 트랙 · 04"),
       f'<h1{SLAM(1)} style="position:absolute;left:128px;top:356px;width:900px;font-size:108px;font-weight:900;line-height:1.1;color:#F6F5F1">Git diff,<br>눈으로 보기</h1>',
       p("position:absolute;left:128px;top:620px;width:900px;font-size:40px;line-height:1.4;color:#BFC6D4", "무엇이 바뀌었는지<br>커밋 전에 확인해요")]
cov.append(f'<div id="cov-code" style="position:absolute;left:1080px;top:300px;width:900px;height:480px;background:#252B36;border-radius:24px 0 0 24px;padding:48px 56px;display:flex;flex-direction:column;gap:12px;font-family:{MONO}">')
for k, l in [("c", "@@ -1,3 +1,4 @@"), ("o", " # 로그인"), ("o", " 아이디"), ("r", "-비밀번호"), ("g", "+비밀번호 (8자 이상)"), ("g", "+로그인 버튼")]:
    cov.append(p(f"font-size:38px;line-height:1.4;white-space:pre;font-weight:700;color:{TC[k]}", e(l)))
cov.append('</div>')
cov.append(shine(2, "cov-code"))
W("cover", cov, "오늘은 새 명령을 많이 배우기보다 확인하는 습관을 만들어요. 03에서 쓰던 hello-git 저장소와 login.md로 이어서 실습해요. add 전, commit 전, merge 전에 무엇이 바뀌는지 눈으로 보고 넘어가요.")

# ---------- toc ----------
PARTS = [("diff란?", "status와 diff, 비교하는 두 칸", "3–4"),
         ("git diff", "add 전에 고친 줄 보기, 출력 읽기", "5–8"),
         ("git diff --staged", "커밋될 내용 확인하기", "9–12"),
         ("git show와 브랜치 비교", "커밋 하나 보기, merge 전에 미리 보기", "13–15"),
         (".gitignore", "올리면 안 되는 파일 빼기", "16–18"),
         ("비교와 막힐 때", "어떤 명령을 칠까, 빈 화면, 안 끝나는 화면", "19–22"),
         ("실제 상황", "충돌 미리 보고 풀기, 빠진 파일 찾기", "23–26"),
         ("한 장 요약", "", "27")]
t = [sec("toc"), f'<h2 style="position:absolute;left:128px;top:96px;font-size:60px;font-weight:700;line-height:1.2;color:{INK}">오늘의 순서</h2>']
RH = 92
t.append(f'<div{STAGGER(1, 80)} style="position:absolute;left:0;top:0;width:1920px;height:1080px">')
for i, (h, s, pg) in enumerate(PARTS):
    y = 236 + i * RH
    bd = f"border-top:2px solid {LINE};" if i else ""
    fam = MONO if h.startswith(("git", ".")) else SANS
    t.append(f'<div style="position:absolute;left:128px;top:{y}px;width:1664px;height:{RH}px;{bd}display:flex;flex-direction:row;align-items:center;gap:32px">'
             + p(f"width:56px;font-size:40px;font-weight:900;color:{BL}", str(i + 1))
             + p(f"width:620px;font-family:{fam};font-size:36px;font-weight:700;color:{INK}", e(h))
             + p(f"flex:1;font-size:28px;color:{SUB}", e(s))
             + p(f"width:120px;font-size:26px;text-align:right;color:{MUTE}", pg + "쪽") + '</div>')
t.append('</div>')
W("toc", t, "1~3부는 02에서 본 칸 그림 위에서 진행해요. 4부 브랜치 비교는 03의 그래프를 다시 써요. 6부까지 배운 것을 7부의 실제 상황 두 개에서 섞어서 써 봐요.")

# ---------- why ----------
w = [sec("why")] + head("diff란?", "status는 파일 이름만, diff는 바뀐 줄까지 보여 줘요")
ts = Term([("$", "git status"), ("o", "Changes not staged for commit:"), ("r", "\tmodified:   login.md")], top=228, w=1728, size=30, tid="t-status")
ts.label(2, "어느 파일이 바뀌었는지만 알려 줘요", "#FFFFFF", x=1100)
w.append(ts.html())
td = Term([("$", "git diff")] + diff_lines(DIFF1), top=ts.bottom + 32, w=1728, size=30, lh=1.42, tid="t-diff")
td.tint(8, 1, "r", order=2)
td.tint(9, 2, "g", order=2)
td.label(8, "어느 줄이 어떻게 바뀌었는지까지", "#FFFFFF", sub="- 지운 줄, + 넣은 줄", n=3, order=2, x=1100)
w.append(td.html(' data-build-in="rise order 1"'))
W("why", w, "git status는 어느 파일이 바뀌었는지만 알려 주고, 그 안의 어느 줄인지는 git diff가 알려 줘요. 커밋 메시지를 쓸 때도 diff를 보면 무엇을 했는지 바로 적을 수 있어요. status 출력의 안내 문장 줄은 화면 때문에 뺐어요. 출력은 tools/demo.sh로 실제로 실행한 결과예요.")

# ---------- map (big picture) ----------
m = [sec("map")] + head("diff란?", "diff는 두 칸을 골라 나란히 놓고 비교해요")
MZ = {"wd": (96, "지금 고치는 파일"), "st": (710, "add로 올린 모습"), "lr": (1324, "commit한 기록")}
MW, MT, MH = 500, 290, 230
for k, (x, desc) in MZ.items():
    z = Z[k]
    m.append(f'<div id="m-{k}" style="position:absolute;left:{x}px;top:{MT}px;width:{MW}px;height:{MH}px;background:{z["bg"]};border:2px solid {z["bd"]};border-radius:22px;padding:30px 36px;display:flex;flex-direction:column;gap:14px">'
             '<div style="display:flex;flex-direction:row;gap:14px;align-items:center">'
             f'<x-icon name="{z["icon"]}" style="width:40px;height:40px;color:{z["tc"]}"></x-icon>'
             + p(f"font-size:38px;font-weight:700;color:{z['tc']}", z["title"]) + '</div>'
             + p(f"font-size:28px;line-height:1.4;color:{SUB}", desc) + '</div>')
for x, lab in [(596, "add"), (1210, "commit")]:
    m.append(f'<x-shape kind="arrow-right" style="position:absolute;left:{x + 29}px;top:{MT + MH // 2 - 14}px;width:56px;height:28px;background:#9AA0AB"></x-shape>')
    m.append(p(f"position:absolute;left:{x}px;top:{MT + MH // 2 - 54}px;width:114px;font-family:{MONO};font-size:22px;font-weight:700;text-align:center;color:{MUTE}", lab))
# lr zone: two commits inside, compared by git show / branch diff
m.append(f'<div data-build-in="fade order 3" style="position:absolute;left:1360px;top:{MT + 160}px;width:448px;height:56px;display:flex;flex-direction:row;align-items:center;gap:14px">'
         f'<div style="width:22px;height:22px;border-radius:11px;background:{BL}"></div><div style="width:46px;height:4px;background:{BLL}"></div><div style="width:22px;height:22px;border-radius:11px;background:{BL}"></div>'
         + p(f"font-size:24px;font-weight:700;color:{OR};margin-left:8px", "커밋끼리도 비교해요") + '</div>')
BR_Y = MT + MH
for i, (a, b, lab, col, hint, dx) in enumerate([("wd", "st", "git diff", C_WD, "status의 빨간 글씨 파일", -14), ("st", "lr", "git diff --staged", C_ST, "status의 초록 글씨 파일", 14)]):
    x1 = MZ[a][0] + MW // 2 + (0 if i == 0 else 14)
    x2 = MZ[b][0] + MW // 2 + (-14 if i == 0 else 0)
    hgt = 120 + i * 170
    m.append(f'<div{WIPE(i + 1)} style="position:absolute;left:{x1}px;top:{BR_Y + 2}px;width:{x2 - x1}px;height:{hgt}px;border:6px solid {col};border-top:none;border-radius:0 0 16px 16px"></div>')
    lw = round(tw(lab, 30) + 44)
    mid = (x1 + x2) // 2
    m.append(p(f"position:absolute;left:{mid - lw // 2}px;top:{BR_Y + hgt - 26}px;width:{lw}px;height:52px;font-family:{MONO};font-size:30px;font-weight:700;line-height:52px;text-align:center;border-radius:12px;background:{col};color:#FFFFFF", e(lab), f' data-build-in="fade order {i + 1}"{DELAY(250)}'))
    m.append(p(f"position:absolute;left:{mid - 300}px;top:{BR_Y + hgt + 40}px;width:600px;font-size:28px;text-align:center;color:{SUB}", hint, f' data-build-in="fade order {i + 1}"{DELAY(400)}'))
W("map", m, "git diff는 ① 작업 폴더와 ② 대기실, git diff --staged는 ② 대기실과 ③ 마지막 커밋을 비교해요. status에서 빨간 글씨로 나온 파일은 git diff로, 초록 글씨로 나온 파일은 git diff --staged로 내용을 봐요. ③ 안의 커밋끼리 비교하는 git show와 브랜치 비교는 4부에서 봐요. ④ 원격 저장소는 이번 챕터에서 쓰지 않아서 그림에서 뺐어요. --staged 대신 --cached라고 써도 같아요.")

# ---------- part 2: git diff ----------
T1 = Term([("$", "git diff")] + diff_lines(DIFF1), top=ctop(11), size=30, lh=1.5)
T1.tint(8, 1, "r", order=2)
T1.tint(9, 2, "g", order=2)
T1.label(8, "고친 줄만 나와요", n=3, order=2, x=700)
LR1 = zcard("lr", H0, V1)
scene("d1", "실습 1 · git diff", "git diff", T1,
      [zcard("wd", "고침", V2, {2: "add", 3: "add"}), zcard("st", "", empty=("비어 있어요", "비어 있으면 ③ 마지막 커밋과<br>같은 모습이 기준이에요")), LR1],
      [chip("wd", "st", "git diff", C_WD)],
      "git diff는 아직 add하지 않은 고친 줄을 보여 줘요. login.md에서 비밀번호 줄에 (8자 이상)을 붙이고 로그인 버튼 줄을 더했어요. 대기실이 비어 있으면 마지막 커밋과 같은 모습이 기준이 돼서 커밋 e12ffc2와 비교한 결과가 나와요. 출력이 길면 화면 아래에 :가 보이고 멈춰요. q를 누르면 나와요.",
      extra=[cap(T1.bottom + 36, "출력이 길어서 아래에 : 가 보이고 멈추면 q를 눌러 나와요.", w=1104)], transition="fade")

# read 1: what each row means (spotlight walks down the rows)
RT = Term(diff_lines(DIFF1), top=228, w=1728, size=34, lh=1.55, tid="t-read")
GROUPS = [(0, 4, "어느 파일인지", "a/ = 예전, b/ = 지금", 1), (4, 1, "몇째 줄 근처인지", "다음 장에서 봐요", 2),
          (5, 2, "그대로인 줄", "앞이 빈칸, 위치 참고용", 3), (7, 1, "- 지운 줄", None, 4), (8, 2, "+ 넣은 줄", None, 4)]
LCOL = {"- 지운 줄": "#F28B82", "+ 넣은 줄": "#7FD18B", "몇째 줄 근처인지": "#7CC7E8"}
r = [sec("read-lines")] + head("출력 읽기", "- 는 지운 줄, + 는 넣은 줄이에요")
for (i, n, t1, t2, o_) in GROUPS:
    RT.label(i, e(t1), LCOL.get(t1, "#FFFFFF"), sub=t2, n=n, order=o_, x=1100)
r.append(RT.html())
for o_, (i, n) in enumerate([(0, 4), (4, 1), (5, 2), (7, 3)], 1):
    r.append(lspot(o_, RT.left, RT.top, RT.w, RT.h, RT.y(i) - 4, RT.rh * n + 8, bg="#1B2029"))
r.append(lspot_off(5))
r.append(cap(RT.bottom + 44, "한 줄을 고치면 <b style=\"color:#A33131\">-</b> 한 줄과 <b style=\"color:#1A7340\">+</b> 한 줄이 짝으로 나와요. 예전 줄을 지우고 새 줄을 넣은 걸로 보여 줘요.", size=32, color=INK, attrs=' data-build-in="fade order 5"'))
W("read-lines", r, "diff 출력은 위에서부터 파일, 위치, 바뀐 줄 순서로 읽어요. 처음엔 diff --git 줄의 파일 이름만 봐도 돼요. index 줄의 숫자는 Git이 파일 내용에 붙인 번호라서 몰라도 돼요. 줄 맨 앞의 기호 한 칸은 파일 내용이 아니라 diff가 붙인 표시예요. 터미널에서는 빼기 줄이 빨강, 더하기 줄이 초록으로 나와요.")

# read 2: @@
a = [sec("read-hunk")] + head("출력 읽기", "@@ 줄은 고친 곳의 위치를 알려 줘요")
HS = 64
hunk = "@@ -1,3 +1,4 @@"
hx = 960 - tw(hunk, HS) / 2
a.append(f'<div style="position:absolute;left:96px;top:232px;width:1728px;height:136px;background:#1B2029;border-radius:20px"></div>')
PAIR = {"-1,3": ("rgba(242,139,130,.30)", 1), "+1,4": ("rgba(127,209,139,.30)", 2)}
segs = [("@@ ", "#7CC7E8"), ("-1,3", "#F28B82"), (" ", "#7CC7E8"), ("+1,4", "#7FD18B"), (" @@", "#7CC7E8")]
a.append(p(f"position:absolute;left:{hx:.0f}px;top:254px;width:900px;font-family:{MONO};font-size:{HS}px;font-weight:700;line-height:92px;white-space:pre",
           "".join(f'<span style="color:{c}"><span{MARK_IN(PAIR[s][1])} style="color:{c};background:{PAIR[s][0]};border-radius:10px">{e(s)}</span></span>' if s in PAIR else f'<span style="color:{c}">{e(s)}</span>' for s, c in segs)))
xa = hx + tw("@@ ", HS)
xb = hx + tw("@@ -1,3 ", HS)
for i, (lab, sign, col, bd, lines, marks, desc) in enumerate([("예전 파일", "-1,3", C_WD, "#E07A7A", V1, {2: "del"}, "1번째 줄부터 3줄"), ("지금 파일", "+1,4", C_ST, "#4DB57A", V2, {2: "add", 3: "add"}, "1번째 줄부터 4줄")]):
    x = 96 + i * 888
    rows = "".join(f'<div style="height:58px;display:flex;flex-direction:row;gap:24px;align-items:center">' + p(f"width:36px;font-family:{MONO};font-size:28px;color:#9AA0AB;text-align:right", str(j + 1))
                   + p(f"font-family:{MONO};font-size:34px;line-height:1.5;padding:0 12px;border-radius:6px;{MARK[marks.get(j)]}", e(l)) + '</div>' for j, l in enumerate(lines))
    a.append(f'<div id="hunk-{i}" style="position:absolute;left:{x}px;top:416px;width:840px;height:420px;background:#FFFFFF;border:2px solid {LINE};border-radius:20px;padding:32px 40px;display:flex;flex-direction:column;gap:6px">'
             + '<div style="display:flex;flex-direction:row;gap:20px;align-items:baseline;margin-bottom:14px">'
             + f'<p style="font-family:{MONO};font-size:40px;font-weight:700;color:{col}"><span{MARK_IN(i + 1)} style="color:{col};background:{PAIR[sign][0]};border-radius:8px;padding:0 8px">{sign}</span></p>' + p(f"font-size:30px;font-weight:700;color:{INK}", desc)
             + p(f"font-size:24px;color:{MUTE}", lab) + '</div>' + rows + '</div>')
    # the bar beside the rows the numbers describe
    a.append(f'<div data-build-in="fade order {i + 1}" style="position:absolute;left:{x + 20}px;top:{416 + 32 + 60 + 14}px;width:8px;height:{58 * len(lines) + 6 * (len(lines) - 1)}px;background:{col};border-radius:4px"></div>')
a.append(cap(880, "숫자는 몰라도 diff를 읽을 수 있어요. 긴 파일에서 고친 곳을 찾아갈 때 써요.", attrs=' data-build-in="fade order 3"'))
W("read-hunk", a, "-1,3은 예전 파일의 1번째 줄부터 3줄, +1,4는 지금 파일의 1번째 줄부터 4줄을 보여 준다는 뜻이에요. 줄이 하나 늘어서 3이 4가 됐어요. 파일 여러 곳을 고치면 @@ 줄이 여러 번 나오고, 각각 고친 곳 하나씩이에요. 고친 줄 앞뒤로 바뀌지 않은 줄을 최대 3줄씩 같이 보여 줘서 어디쯤인지 알 수 있어요.")

T2 = Term([("$", "git add login.md"), ("$", "git diff"), ("#", "# 아무것도 안 나와요")], top=ctop(3, caph=94), size=30, lh=1.5)
scene("d2", "실습 2 · add한 다음 git diff", "git diff", T2,
      [zcard("wd", "고친 그대로", V2), zcard("st", "올림", V2), zcard("lr", H0, V1, dim=True)],
      [chip("wd", "st", "git diff", C_WD, order=0)],
      "add한 뒤 git diff가 빈 화면인 건 작업 폴더와 대기실이 같아졌기 때문이에요. 이제 커밋될 내용은 다음 장의 git diff --staged로 봐요.",
      extra=[pulse(1, "z-wd"), pulse(1, "z-st"),
             cap(T2.bottom + 40, "①과 ②가 똑같아서 보여 줄 줄이 없어요.<br>고친 내용은 ②로 옮겨 갔을 뿐 그대로 있어요.", w=1104, size=32, color=INK, attrs=' data-build-in="fade order 2"')])

# ---------- part 3: --staged ----------
T3 = Term([("$", "git diff --staged")] + diff_lines(DIFF1), top=ctop(11), size=30, lh=1.5)
T3.tint(8, 1, "r", order=1)
T3.tint(9, 2, "g", order=1)
T3.label(8, "commit하면 들어갈 줄", n=3, order=1, x=700)
scene("d3", "실습 3 · git diff --staged", "git diff --staged", T3,
      [zcard("wd", "고친 그대로", V2, dim=True), zcard("st", "올림", V2, {2: "add", 3: "add"}), zcard("lr", H0, V1, {2: "del"})],
      [chip("st", "lr", "git diff --staged", C_ST, order=0)],
      "git diff --staged는 지금 commit하면 들어갈 내용을 보여 줘요. 대기실과 마지막 커밋을 비교하기 때문이에요. 실습 1과 같은 출력이 나온 건 고친 걸 그대로 다 올렸기 때문이에요. --cached라고 써도 똑같이 동작해요.",
      extra=[cap(T3.bottom + 36, "커밋 메시지를 쓰기 전에 한 번 보면 무엇을 했는지 바로 적을 수 있어요.", w=1104)])

T4 = Term([("$", 'echo "아이디 저장" >> login.md'), ("$", "git diff")] + diff_lines(DIFF_MORE), top=ctop(11), size=30, lh=1.5)
T4.tint(10, 1, "g", order=2)
T4.label(10, "add 뒤에 고친 한 줄만", order=2, x=700)
scene("d4a", "실습 4 · add 뒤에 또 고치면", "git diff", T4,
      [zcard("wd", "또 고침", V3, {4: "add"}), zcard("st", "올림", V2), zcard("lr", H0, V1, dim=True)],
      [chip("wd", "st", "git diff", C_WD, order=0)],
      "add한 뒤에 또 고치면 git diff에는 그 뒤에 고친 줄만 나와요. 기준이 대기실이기 때문이에요. 02 실습 6에서 본 같은 파일, 다른 내용 장면을 diff로 다시 보는 거예요.",
      extra=[box(1, ZL + 18, zline("wd", 4) - 2, 150, CL_H + 4, RED, 4),
             cap(T4.bottom + 36, "기준이 대기실이라서 add 뒤에 고친 줄만 보여요.", w=1104, attrs=' data-build-in="fade order 2"')])

T5 = Term([("$", "git diff --staged")] + diff_lines(DIFF1), top=ctop(11), size=30, lh=1.5)
slot_y = zline("st", 4)
scene("d4b", "실습 4 · add 뒤에 또 고치면", "git diff --staged", T5,
      [zcard("wd", "또 고침", V3, {4: "dim"}, dim=True), zcard("st", "올림", V2, {2: "add", 3: "add"}), zcard("lr", H0, V1, {2: "del"})],
      [chip("st", "lr", "git diff --staged", C_ST, order=0)],
      "--staged에 아이디 저장 줄이 없으니 지금 commit하면 그 줄은 빠져요. 커밋 직전에 git diff와 git diff --staged를 둘 다 보면 빠뜨린 걸 찾을 수 있어요.",
      extra=[box(1, ZL + 18, slot_y + 2, 230, CL_H, RED, 4),
             p(f"position:absolute;left:{ZL + 38}px;top:{slot_y}px;width:240px;font-size:20px;font-weight:700;line-height:{CL_H}px;color:{RED}", "아이디 저장 없음", ' data-build-in="fade order 1"'),
             cap(T5.bottom + 36, "지금 commit하면 <b style=\"color:#A33131\">아이디 저장</b>은 빠져요. 한 번 더 git add 해요.", w=1104, size=32, color=INK, attrs=' data-build-in="fade order 2"')])

T6 = Term([("$", "git add login.md"), ("$", 'git commit -m "feat: 로그인 화면에 안내와 버튼 추가"'), ("o", f"[main {H1}] feat: 로그인 화면에 안내와 버튼 추가"),
           ("o", " 1 file changed, 3 insertions(+), 1 deletion(-)"), ("$", "git diff"), ("$", "git diff --staged"), ("#", "# 둘 다 아무것도 안 나와요")], top=ctop(7, size=29, lh=1.6), size=29, lh=1.6)
x0 = T6.left + T6.padx + tw(" 1 file changed, ", 29)
scene("d5", "실습 5 · 커밋하고 나면", "커밋하고 나면 git diff도 --staged도 비어요", T6,
      [zcard("wd", "변경 없음", V3), zcard("st", "", empty=("비어 있어요", "커밋하면 대기실은 다시 비어요")), zcard("lr", H1, V3)],
      [chip("wd", "st", "git diff", C_WD, order=0), chip("st", "lr", "git diff --staged", C_ST, cid="chip2", order=0)],
      "커밋하고 나면 git diff와 git diff --staged 모두 빈 화면이에요. 커밋 출력의 3 insertions(+), 1 deletion(-)은 diff의 + 줄 3개, - 줄 1개와 같은 숫자예요. 방금 커밋한 내용을 다시 보려면 다음 장의 git show를 써요.",
      extra=[underline(1, round(x0), round(x0 + tw("3 insertions(+), 1 deletion(-)", 29)), round(T6.y(4) - 6), OR, 5),
             cap(T6.bottom + 36, "<b style=\"color:#B26A00\">3 insertions(+), 1 deletion(-)</b>은 diff의 + 줄 3개, - 줄 1개예요.", w=1104, size=30, color=INK, attrs=' data-build-in="fade order 1"')],
      mono=False)

# ---------- part 4: git show and branches ----------
lines = [("$", "git show")] + [("o" if i < 6 else kind_of(l), l) for i, l in enumerate(SHOW.split("\n"))]
ST = Term(lines, top=228, w=1728, size=25, lh=1.4, tid="t-show")
ST.label(1, "커밋 정보", "#FFFFFF", sub="번호, 만든 사람, 날짜, 메시지", n=5, order=1, x=1150)
ST.label(7, "바뀐 내용", "#FFFFFF", sub="바로 전 커밋과 비교한 diff", n=11, order=2, x=1150)
s = [sec("show")] + head("git show", "git show는 커밋 하나가 바꾼 것을 보여 줘요", NAVY)
s.append(ST.html())
s += [spot(1, *ST.box(1, 5, x0=ST.left + 14, x1=ST.left + ST.w - 14), pad=6, r=12),
      spot(2, *ST.box(7, 11, x0=ST.left + 14, x1=ST.left + ST.w - 14), pad=6, r=12), spot_off(3)]
s.append(cap(ST.bottom + 28, f"다른 커밋은 <span style=\"font-family:{MONO};font-weight:700;color:{INK}\">git log --oneline</span>에서 번호를 찾아 <span style=\"font-family:{MONO};font-weight:700;color:{INK}\">git show {H0}</span>처럼 봐요.", attrs=' data-build-in="fade order 3"'))
W("show", s, "git show는 커밋 하나를 열어서 위에는 커밋 정보, 아래에는 바로 전 커밋과 비교한 diff를 보여 줘요. 번호 없이 쓰면 지금 브랜치의 마지막 커밋을 보여 줘요. 팀원이 올린 커밋이 무엇을 바꿨는지 볼 때도 써요. 출력이 길면 q로 나와요.")


def node(x, y, color, nid, r=20):
    return f'<div id="{nid}" style="position:absolute;left:{x - r}px;top:{y - r}px;width:{2 * r}px;height:{2 * r}px;border-radius:50%;background:{color}"></div>'


def hline(x1, x2, y, color, hid):
    return f'<div id="{hid}" style="position:absolute;left:{x1}px;top:{y - 3}px;width:{x2 - x1}px;height:6px;background:{color}"></div>'


def pill(x, y, text, kind, pid):
    w = round(tw(text, 22) + 28)
    st = {"main": f"background:{BL};color:#FFFFFF", "green": f"background:{GR};color:#FFFFFF"}[kind]
    return f'<p id="{pid}" style="position:absolute;left:{x - w // 2}px;top:{y}px;width:{w}px;font-family:{MONO};font-size:22px;font-weight:700;line-height:1.5;text-align:center;border-radius:8px;{st}">{text}</p>'


def hlabel(x, y, h, hid):
    return p(f"position:absolute;left:{x - 80}px;top:{y + 28}px;width:160px;font-family:{MONO};font-size:20px;font-weight:700;text-align:center;color:{SUB}", h, f' id="{hid}"')


YM, YB = 372, 270


def graph(main_moved=False):
    g = [f'<div id="dots" style="position:absolute;left:110px;top:{YM - 3}px;width:100px;height:6px;border-top:6px dotted {BLL}"></div>']
    end = 900 if main_moved else 560
    g += [hline(230, end, YM, BLL, "e-main"), f'<x-connector id="e-br" x1="560" y1="{YM}" x2="760" y2="{YB}" style="color:{GRL};border-width:6px"></x-connector>']
    g += [node(280, YM, BL, "n0"), hlabel(280, YM, H0, "h0"), node(560, YM, BL, "n1"), hlabel(560, YM, H1, "h1")]
    g += [node(760, YB, GR, "nb"), hlabel(760, YB, HB, "hb"), pill(760, YB - 64, "feature/login", "green", "t-br")]
    if main_moved:
        g += [node(900, YM, BL, "nm"), hlabel(900, YM, HM, "hm"), pill(900, YM + 64, "main", "main", "t-main")]
    else:
        g += [pill(560, YM + 64, "main", "main", "t-main")]
    return g


def order_pair(first, second):
    """Which branch is written first: the diff shows how to turn the first into the second."""
    col = {"main": BL, "feature/login": GR}
    o = []
    for slot, name in enumerate((first, second)):
        x = 1100 + slot * 380
        oid = "o-main" if name == "main" else "o-br"
        o.append(f'<div id="{oid}" style="position:absolute;left:{x}px;top:236px;width:320px;height:128px;background:#FFFFFF;border:3px solid {col[name]};border-radius:18px;padding:16px 24px;display:flex;flex-direction:column;gap:6px">'
                 + p(f"font-size:22px;font-weight:700;color:{MUTE}", "앞에 쓴 쪽" if slot == 0 else "뒤에 쓴 쪽")
                 + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{col[name]}", name) + '</div>')
    o.append('<x-shape id="o-arrow" kind="arrow-right" style="position:absolute;left:1428px;top:284px;width:44px;height:34px;background:#9AA0AB"></x-shape>')
    o.append(p(f"position:absolute;left:1100px;top:384px;width:700px;font-size:24px;line-height:1.4;color:{SUB}", f"{first}을 {second}으로 만들려면 무엇을 바꾸나", ' id="o-cap"'))
    return o


def bscene(sid, eyebrow, title, cmd, out, labels, notes, moved=False, pair=("main", "feature/login"), extra=(), transition="magic", ecolor=OR, cap_text=None):
    o = [sec(sid, transition)] + head(eyebrow, title, ecolor)
    o += graph(moved)
    o += order_pair(*pair)
    T = Term([("$", cmd)] + diff_lines(out), top=482, w=1728, size=26, lh=1.4, tid="t-br")
    for (i, n, kind, text, sub, order) in labels:
        T.tint(i, n, kind, order=order)
        T.label(i, text, {"r": "#F28B82", "g": "#7FD18B"}[kind], sub=sub, n=n, order=order, x=1000)
    o.append(T.html())
    o += list(extra(T) if callable(extra) else extra)
    if cap_text:
        o.append(p(f"position:absolute;left:1100px;top:428px;width:724px;font-size:26px;font-weight:700;line-height:1.4;color:{ecolor}", cap_text[0], cap_text[1]))
    W(sid, o, notes)


bscene("br1", "브랜치 비교", "merge 전에 무엇이 들어올지 미리 봐요", "git diff main feature/login", DIFF_BR,
       [(6, 1, "r", "main에만 있는 줄", None, 1), (7, 1, "g", "feature/login에만 있는 줄", None, 1), (12, 1, "g", "feature/login에서 새로 생긴 줄", None, 2)],
       "git diff main feature/login은 merge하면 main에 들어올 변경을 미리 보여 줘요. 03처럼 feature/login에서 제목을 # 로그인하기로 바꾸고 비밀번호 찾기 줄을 더해 커밋한 뒤 git checkout main으로 돌아왔어요. 두 브랜치의 마지막 커밋끼리 비교해요.",
       transition="fade")
bscene("br2", "브랜치 비교", "순서를 바꾸면 +와 -가 뒤집혀요", "git diff feature/login main", DIFF_BR_REV,
       [(6, 1, "r", "feature/login에만 있는 줄", None, 1), (7, 1, "g", "main에만 있는 줄", None, 1), (12, 1, "r", "앞 장에서는 + 였던 줄", None, 1)],
       "git diff A B는 A를 B로 만들려면 무엇을 바꿔야 하는지 보여 줘서 순서를 바꾸면 기호가 뒤집혀요. merge 전에 볼 땐 git merge와 같은 감각으로 받을 쪽 main을 앞에 써요.",
       pair=("feature/login", "main"),
       cap_text=("merge 전에는 받을 쪽 main을 앞에 써요.", ' data-build-in="fade order 2"'))

# ---------- part 5: .gitignore ----------
def file_tile(fid, name, status, style, top, extra=""):
    bg, bd, col = {"red": ("#FBE4E2", "#E07A7A", RED), "gray": ("#FFFFFF", "#C9CDD4", "#3A4150"), "hide": ("#F6F5F1", "#B4B9C3", MUTE)}[style]
    dash = "dashed" if style == "hide" else "solid"
    op = ";opacity:.75" if style == "hide" else ""
    return (f'<div id="{fid}" style="position:absolute;left:128px;top:{top}px;width:536px;height:132px;background:{bg};border:2px {dash} {bd};border-radius:16px;padding:20px 26px;display:flex;flex-direction:column;justify-content:center;gap:8px{op}{extra}">'
            + p(f"font-family:{MONO};font-size:36px;font-weight:700;color:{INK}", e(name)) + p(f"font-size:25px;font-weight:700;color:{col}", e(status)) + '</div>')


def ig_frame(sid, title, files, T, extras, notes, transition="magic", fh=676):
    o = [sec(sid, transition)] + head(".gitignore", title, PUR)
    o.append(f'<div id="folder" style="position:absolute;left:96px;top:232px;width:600px;height:{fh}px;background:#FDFCF9;border:2px solid #9AA0AB;border-radius:20px"></div>')
    o.append('<div id="folder-h" style="position:absolute;left:128px;top:262px;width:540px;display:flex;flex-direction:row;gap:12px;align-items:center"><x-icon name="Code" style="width:34px;height:34px;color:#3A4150"></x-icon>'
             + p("font-size:32px;font-weight:700;color:#3A4150", "① 작업 폴더 hello-git/") + '</div>')
    o += files
    o.append(T.html())
    o += extras
    W(sid, o, notes)


F_LOGIN = file_tile("f-login", "login.md", "커밋됨 · 바뀐 것 없음", "gray", 330)
G1 = Term([("$", 'echo "API_KEY=abc123" > .env'), ("$", "git status"), ("o", "On branch main"), ("o", "Untracked files:"),
           ("r", "\t.env")], left=744, top=232, w=1080, size=34, lh=1.5, tid="t-ig")
ig_frame("ig1", "비밀 값이 든 .env는 올리면 안 돼요",
         [F_LOGIN, file_tile("f-env", ".env", "Untracked · API_KEY=abc123", "red", 498), file_tile("f-ig", ".gitignore", "", "red", 666, ";opacity:0")], G1,
         [G1.pen(4, x0=G1.left + G1.padx + 110),
          cap(G1.bottom + 48, "<b style=\"color:#A33131\">git add .</b> 한 번이면 .env까지 올라가요.<br>GitHub에 올라간 키는 누구나 볼 수 있어요.", left=744, w=1080, size=38, color=INK, attrs=' data-build-in="fade order 1"')],
         ".env는 API 키 같은 비밀 값을 적어 두는 파일이라 GitHub에 올리면 안 돼요. 수업에서 AI API를 쓸 때 자주 만들어요. status에 계속 빨간 글씨로 나오고, git add .을 치면 같이 올라가요. 한 번 push한 키는 지워도 기록에 남아서 키를 새로 발급받아야 해요. status 출력의 안내 줄은 화면 때문에 뺐어요.", transition="fade", fh=520)

G2 = Term([("$", 'echo ".env" > .gitignore'), ("$", "git status"), ("o", "On branch main"), ("o", "Untracked files:"), ("r", "\t.gitignore"),
           ("$", "git add .gitignore"), ("$", 'git commit -m "chore: .env를 gitignore에 추가"'), ("o", "[main 0e35512] chore: .env를 gitignore에 추가")],
          left=744, top=232, w=1080, size=28, lh=1.5, tid="t-ig")
G2.label(4, ".env가 목록에서 빠졌어요", order=1, x=1340)
ig_frame("ig2", ".gitignore에 이름을 적으면 Git이 못 본 척해요",
         [F_LOGIN, file_tile("f-env", ".env", "무시됨 · status에 안 나와요", "hide", 498), file_tile("f-ig", ".gitignore", "새 파일 · 커밋해서 같이 써요", "red", 666)], G2,
         [box(1, 118, 488, 556, 152, PUR, 5, 20),
          cap(G2.bottom + 48, ".env 파일은 그대로 있고 Git만 못 본 척해요.<br>.gitignore는 커밋해서 팀원도 같은 규칙을 써요.", left=744, w=1080, size=32, color=INK, attrs=' data-build-in="fade order 2"')],
         ".gitignore에 이름을 적은 파일은 status에도 add에도 잡히지 않아요. .gitignore는 저장소 맨 위 폴더에 두고 한 줄에 하나씩 적어요. .env 파일 자체는 지워지지 않아요. status 출력의 안내 줄은 화면 때문에 뺐어요.")

g = [sec("ig3")] + head(".gitignore", "자주 적는 이름은 정해져 있어요", PUR)
ROWS = [(".env", "비밀 값", "API 키, 비밀번호"), ("node_modules/", "받은 패키지", "다시 받으면 돼요"), ("__pycache__/", "파이썬 임시 파일", "실행하면 저절로 생겨요"),
        (".venv/", "파이썬 가상환경", "uv sync로 다시 만들어요"), ("*.log", "로그 파일", "* 는 아무 이름"), (".DS_Store", "macOS 폴더 설정", "Finder가 만들어요")]
GH = 104
for i, (pat, what, why) in enumerate(ROWS):
    bd = f"border-top:2px solid {LINE};" if i else ""
    g.append(f'<div style="position:absolute;left:96px;top:{236 + i * GH}px;width:1120px;height:{GH}px;{bd}display:flex;flex-direction:row;align-items:center;gap:24px">'
             + f'<p id="pat-{i}" style="width:330px;flex:none;font-family:{MONO};font-size:34px;font-weight:700;color:{PUR}">{e(pat)}</p>'
             + p(f"width:300px;flex:none;font-size:30px;font-weight:700;color:{INK}", what) + p(f"font-size:26px;color:{MUTE}", why) + '</div>')
g.append(p(f"position:absolute;left:1280px;top:186px;width:544px;font-size:24px;font-weight:700;color:{MUTE}", ".gitignore 파일 안"))
g.append(f'<div id="ig-file" style="position:absolute;left:1280px;top:236px;width:544px;height:{GH * 6}px;background:#1B2029;border-radius:20px"></div>')
for i, (pat, _, _) in enumerate(ROWS):
    g.append(f'<p id="fl-{i}" data-build-in="fly order 1" data-from="pat-{i}" style="position:absolute;left:1320px;top:{236 + i * GH}px;width:460px;height:{GH}px;display:flex;align-items:center;font-family:{MONO};font-size:34px;font-weight:700;color:#D8DEE9">{e(pat)}</p>')
g.append(cap(236 + GH * 6 + 40, "끝에 / 를 붙이면 폴더, * 는 아무 글자, # 으로 시작하면 메모 줄이에요.", size=30, attrs=' data-build-in="fade order 2"'))
W("ig3", g, "프로젝트를 만들 때 처음부터 .gitignore에 이 이름들을 적어 두면 편해요. GitHub에서 새 저장소를 만들 때 Add .gitignore 메뉴로 Python 같은 템플릿을 고를 수도 있어요. .venv는 09에서 uv가 만든 가상환경 폴더예요. 한 줄에 하나, 끝에 /는 폴더, *는 아무 글자, #은 메모라는 것만 알면 돼요.")

# ---------- part 6: compare and trouble ----------
c = [sec("compare")] + head("한눈에 비교", "status를 보고 어떤 diff를 칠지 골라요")
CMP = [("add 전", "빨간 글씨 파일", "git diff", C_WD, "① 작업 폴더 ↔ ② 대기실"),
       ("commit 전", "초록 글씨 파일", "git diff --staged", C_ST, "② 대기실 ↔ ③ 마지막 커밋"),
       ("commit 뒤", "nothing to commit", "git show", NAVY, "마지막 커밋 ↔ 바로 전 커밋"),
       ("merge 전", "브랜치가 두 개", "git diff main 브랜치", OR, "두 브랜치의 마지막 커밋")]
CH = 150
c.append(f'<div style="position:absolute;left:96px;top:236px;width:1728px;height:52px;display:flex;flex-direction:row;align-items:center;gap:32px;padding:0 24px">'
         + "".join(p(f"width:{wd}px;flex:none;font-size:24px;font-weight:700;color:{MUTE}", h) for h, wd in [("언제", 220), ("status에 보이는 것", 360), ("칠 명령", 520), ("비교하는 두 곳", 500)]) + '</div>')
for i, (when, st, cmd, col, pair) in enumerate(CMP):
    y = 296 + i * CH
    c.append(f'<div id="cmp-{i}" data-build-in="rise order {i + 1}"{DIM("cmp")} style="position:absolute;left:96px;top:{y}px;width:1728px;height:{CH}px;border-top:2px solid {LINE};display:flex;flex-direction:row;align-items:center;gap:32px;padding:0 24px">'
             + p(f"width:220px;flex:none;font-size:34px;font-weight:700;color:{INK}", when)
             + p(f"width:360px;flex:none;font-size:28px;color:{SUB}", st)
             + p(f"width:520px;flex:none;font-family:{MONO};font-size:32px;font-weight:700;color:{col}", cmd)
             + p(f"width:500px;flex:none;font-size:28px;color:{INK}", pair) + '</div>')
c.append(cap(296 + 4 * CH + 36, "빈 화면은 오류가 아니라 비교한 두 곳이 같다는 뜻이에요.", size=30, color=INK, attrs=' data-build-in="fade order 4"'))
W("compare", c, "무엇을 칠지 헷갈리면 먼저 git status를 봐요. 빨간 글씨면 git diff, 초록 글씨면 git diff --staged, 깨끗하면 git show를 써요. merge 전에는 받을 쪽을 앞에 써서 git diff main 브랜치이름이에요. 수업에서는 이 장을 띄워 두고 상황마다 학생이 명령을 말해 보게 하세요.")

tb = [sec("t-empty")] + head("막힐 때", "git diff에 아무것도 안 나와요", NAVY)
CASES = [("이미 git add 했어요", "대기실에 올린 건 --staged로 봐요", "git diff --staged"),
         ("새로 만든 파일이에요", "Untracked 파일은 git diff에 안 나와요. add한 뒤에 봐요", "git add 파일<br>git diff --staged"),
         ("이미 commit 했어요", "커밋한 내용은 git show로 봐요", "git show")]
EH = 220
tb.append(f'<div{STAGGER(1, 160)} style="position:absolute;left:0;top:0;width:1920px;height:1080px">')
for i, (q, a_, cmd) in enumerate(CASES):
    bd = f"border-top:2px solid {LINE};" if i else ""
    tb.append(f'<div style="position:absolute;left:96px;top:{236 + i * EH}px;width:1728px;height:{EH}px;{bd}display:flex;flex-direction:row;gap:36px;align-items:center;padding:0 12px">'
              + p(f"width:60px;height:60px;flex:none;font-size:32px;font-weight:900;line-height:60px;text-align:center;color:#FFFFFF;background:{NAVY};border-radius:30px", str(i + 1))
              + f'<div style="flex:1;display:flex;flex-direction:column;gap:10px">' + p(f"font-size:38px;font-weight:700;color:{INK}", q) + p(f"font-size:28px;color:{SUB}", a_) + '</div>'
              + p(f"width:470px;flex:none;font-family:{MONO};font-size:30px;font-weight:700;line-height:1.5;color:{INK};background:#EBEDF1;padding:16px 24px;border-radius:12px", cmd) + '</div>')
tb.append('</div>')
tb.append(cap(236 + 3 * EH + 36, "셋 다 아니면 git status부터 봐요. 고친 파일이 없으면 diff도 비어요.", size=30, color=INK, attrs=' data-build-in="fade order 2"'))
W("t-empty", tb, "git diff가 빈 화면이면 비교한 두 곳이 같다는 뜻이고, 세 경우 중 하나예요. 새 파일이 git diff에 안 나오는 게 처음엔 가장 헷갈려요. Git이 아직 모르는 파일이라 비교할 예전 모습이 없어서예요.")

tp = [sec("t-pager")] + head("막힐 때", "화면이 안 끝나면 q, 너무 길면 --stat", NAVY)
pg_lines = [("$", "git show")] + [("o" if i < 6 else kind_of(l), l) for i, l in enumerate(SHOW.split("\n")[:13])] + [("o", ":")]
P1 = Term(pg_lines, left=96, top=300, w=1000, size=24, lh=1.4, tid="t-p1")
P1.label(14, "여기서 멈춰 있어요", "#F2C46D", order=1, x=560)
tp.append(p(f"position:absolute;left:96px;top:236px;width:1000px;font-size:30px;font-weight:700;color:{INK}", "맨 아래에 : 나 (END)가 보이고 멈춰요"))
tp.append(P1.html())
kx, ky = P1.left + P1.w - 110, P1.bottom - 66
tp.append(keys(1, kx + 8, ky + 14, "q", size=60))
tp.append(p(f"position:absolute;left:96px;top:{P1.bottom + 36}px;width:880px;font-size:28px;line-height:1.45;color:{SUB}", "q를 누르면 나와요. Space는 다음 화면이에요.", ' data-build-in="fade order 1"'))
P2 = Term([("$", "git diff --stat main feature/login"), ("o", " login.md | 3 ++-"), ("o", " 1 file changed, 2 insertions(+),"), ("o", " 1 deletion(-)")], left=1200, top=300, w=624, size=24, lh=1.6, tid="t-p2")
tp.append(p(f"position:absolute;left:1200px;top:236px;width:624px;font-size:30px;font-weight:700;color:{INK}", "파일 이름과 줄 수만 볼 때"))
tp.append(P2.html())
tp.append(f'<div style="position:absolute;left:1148px;top:236px;width:2px;height:{P1.bottom - 236}px;background:{LINE}"></div>')
ux = P2.left + P2.padx + tw(" login.md | ", 24)
tp.append(underline(2, round(ux), round(ux + tw("3 ++-", 24)), round(P2.y(2) - 4), OR, 5))
tp.append(p(f"position:absolute;left:1200px;top:{P2.bottom + 36}px;width:624px;font-size:28px;line-height:1.5;color:{SUB}", "+, - 개수로 얼마나 바뀌었는지 봐요.<br>git diff, --staged, git show에 모두 붙여요.", ' data-build-in="fade order 2"'))
W("t-pager", tp, "출력이 한 화면보다 길면 Git이 보기 프로그램으로 한 화면씩 보여 줘서 멈춘 것처럼 보여요. q로 나와요. 파일이 많을 때는 --stat으로 먼저 훑고, 궁금한 파일만 git diff 파일이름으로 봐요.")

g = [sec("ig4")] + head("함정", "이미 커밋한 파일은 .gitignore로 숨겨지지 않아요", PUR)
G4 = Term([("$", 'echo "*.log" >> .gitignore'), ("$", 'echo "error" >> app.log'), ("$", "git status"), ("o", "Changes not staged for commit:"), ("r", "\tmodified:   .gitignore"), ("r", "\tmodified:   app.log"),
           ("$", "git rm --cached app.log"), ("o", "rm 'app.log'"), ("$", "git status"), ("o", "Changes to be committed:"), ("g", "\tdeleted:    app.log"),
           ("o", "Changes not staged for commit:"), ("r", "\tmodified:   .gitignore"), ("$", "git add .gitignore"), ("$", 'git commit -m "chore: 로그 파일을 기록에서 빼기"')],
          left=96, top=228, w=1128, size=24, lh=1.45, tid="t-ig4")
G4.label(5, "*.log를 적었는데 계속 나와요", "#F28B82", order=1, x=700)
G4.label(10, "기록에서만 빠져요", "#7FD18B", order=2, x=700)
g.append(G4.html())
g.append(G4.pen(5, x0=G4.left + G4.padx + 110))
g.append(f'<div data-build-in="rise order 2" style="position:absolute;left:1272px;top:228px;width:552px;display:flex;flex-direction:column;gap:22px">'
         + p(f"font-size:34px;font-weight:700;line-height:1.4;color:{INK}", ".gitignore는 Git이 아직 모르는 파일에만 통해요")
         + p(f"font-size:28px;line-height:1.5;color:{SUB}", "이미 커밋한 파일은 기록 대상에서 빼요.")
         + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{INK};background:#EBEDF1;padding:14px 20px;border-radius:12px;align-self:flex-start", "git rm --cached 파일")
         + p(f"font-size:28px;line-height:1.5;color:{SUB}", "내 폴더의 파일은 그대로 있어요.<br>그다음 .gitignore와 같이 add, commit 해요.") + '</div>')
W("ig4", g, "Git은 이미 기록하던 파일은 .gitignore에 적어도 계속 지켜봐요. app.log를 먼저 커밋한 뒤에 *.log를 적은 상황이에요. git rm --cached는 파일은 내 폴더에 두고 Git 기록에서만 빼요. 그래서 .gitignore는 프로젝트 처음에 만드는 게 좋아요. 비밀 값을 이미 push했다면 키를 새로 발급받아요. status 안내 줄과 On branch main 줄은 화면 때문에 뺐어요.")

# ---------- part 7: real situations ----------
def br3_marks(T):
    x, y, ww, hh = T.box(6, 2)
    return [box(1, x - 6, y - 4, ww + 12, hh + 8, RED, 5)]


bscene("br3", "실제 상황 1 · merge 전에 충돌 미리 보기", "같은 줄을 양쪽에서 고쳤는지 merge 전에 봐요", "git diff main feature/login", DIFF_BR2,
       [(6, 1, "r", "main의 제목", None, 1), (7, 1, "g", "feature/login의 제목", None, 1)],
       f"diff의 - 줄과 + 줄이 같은 자리의 서로 다른 제목이면 merge할 때 충돌이 날 수 있어요. 그사이 main에서도 제목을 # 로그인 페이지로 바꿔 커밋했어요({HM}). 두 브랜치의 마지막 커밋끼리 비교하기 때문에 main에서만 고친 줄도 - 쪽에 나와요.",
       moved=True, extra=br3_marks, transition="fade", ecolor=RED,
       cap_text=("같은 줄이 양쪽에서 달라요. 이대로 merge하면 충돌이 나요.", ' data-build-in="fade order 2"'))

c = [sec("conflict")] + head("실제 상황 1 · merge 전에 충돌 미리 보기", "충돌이 나면 git diff로 충돌 난 곳만 봐요", RED)
CT = Term([("$", "git merge feature/login"), ("o", "Auto-merging login.md"), ("r", "CONFLICT (content): Merge conflict in login.md"), ("o", "Automatic merge failed; fix conflicts and then commit the result."), ("$", "git diff")] + diff_lines(DIFF_CC),
          top=228, w=1728, size=25, lh=1.42, tid="t-cf", ids={2: "cf-line"})
CT.label(11, "↑ 위: main(HEAD) 쪽", "#9DB8F2", n=1, order=2, x=1000)
CT.label(13, "↓ 아래: feature/login 쪽", "#7FD18B", n=1, order=2, x=1000)
CT.label(10, "++ 로 시작하는 줄이 충돌 표시", "#F28B82", order=2, x=1000)
CT.tint(10, 5, "r", order=2)
c.append(CT.html())
c.append(CT.pen(2))
c.append(shake(1, "cf-line"))
c.append(cap(CT.bottom + 28, "파일이 여러 개여도 git diff 하나로 충돌 표시가 남은 곳을 모두 찾아요.", size=30, color=INK, attrs=' data-build-in="fade order 3"'))
W("conflict", c, "충돌 중에 git diff를 치면 충돌 난 부분만 diff --cc 모양으로 보여 줘요. 앞에 기호가 두 칸 붙는 건 두 브랜치와 각각 비교해서예요. 지금은 ++ 줄이 충돌 표시이고 그 사이 위아래가 양쪽 내용이라는 것만 기억하면 돼요. 푸는 순서는 03과 같아요.")

o = [sec("resolve")] + head("실제 상황 1 · merge 전에 충돌 미리 보기", "고친 뒤 add하고, 커밋 전에 --staged로 한 번 더 봐요", RED, size=50)
RL = Term([("#", "# login.md에서 # 로그인하기만 남기고 표시 세 줄을 지움"), ("$", "git add login.md"), ("$", "git diff --staged")] + diff_lines(DIFF_BR2)
          + [("$", 'git commit -m "fix: 로그인 제목 충돌 해결"'), ("o", f"[main {HR}] fix: 로그인 제목 충돌 해결")], left=96, top=228, w=1128, size=26, lh=1.42, tid="t-rs")
RL.tint(8, 7, "y", order=1)
RL.tint(9, 1, "g", order=2)
o.append(RL.html())
CHECK = [("<span style=\"font-family:'JetBrains Mono',monospace;font-weight:700\">&lt;&lt;&lt;</span> 같은 표시가 남지 않았나", RED),
         ("남긴 제목이 맞나", BL), ("main에 들어올 줄이 이게 다인가", C_ST)]
o.append(p(f"position:absolute;left:1272px;top:236px;width:552px;font-size:32px;font-weight:700;color:{INK}", "커밋 전에 볼 것"))
for i, (t_, col) in enumerate(CHECK):
    bd = f"border-top:2px solid {LINE};"
    o.append(f'<div data-build-in="rise order {i + 1}"{DIM("chk")} style="position:absolute;left:1272px;top:{300 + i * 130}px;width:552px;height:130px;{bd}display:flex;flex-direction:row;gap:20px;align-items:center">'
             + p(f"width:48px;height:48px;flex:none;font-size:26px;font-weight:900;line-height:48px;text-align:center;color:#FFFFFF;background:{col};border-radius:24px", str(i + 1))
             + p(f"font-size:28px;line-height:1.45;color:{INK}", t_) + '</div>')
o.append(cap(RL.bottom + 28, "--staged는 main의 마지막 커밋과 비교해요. 이 merge 커밋에 들어갈 내용이에요.", w=1128, size=28, attrs=' data-build-in="fade order 3"'))
W("resolve", o, "충돌을 풀고 add한 뒤 git diff --staged를 보면 이 merge 커밋으로 main에 들어올 변경이 나와요. 브랜치 비교에서 본 것과 같은 내용이에요. 충돌 표시가 남아 있으면 여기서 + 줄로 보여요. 확인이 끝나면 커밋해요.")

x2 = [sec("ex2")] + head("실제 상황 2 · 커밋 전에 빠진 파일 찾기", "커밋 전에 --stat으로 파일 목록부터 훑어요", BL)
XT = Term([("$", 'echo "회원가입 링크" >> login.md'), ("$", 'echo "# 회원가입" > signup.md'), ("$", "git add login.md"), ("$", "git diff --staged --stat"),
           ("o", " login.md | 1 +"), ("o", " 1 file changed, 1 insertion(+)"), ("$", "git status"), ("o", "Changes to be committed:"), ("g", "\tmodified:   login.md"),
           ("o", "Untracked files:"), ("r", "\tsignup.md"), ("$", "git add signup.md"), ("$", "git diff --staged --stat"), ("o", " login.md  | 1 +"), ("o", " signup.md | 1 +"),
           ("o", " 2 files changed, 2 insertions(+)"), ("$", 'git commit -m "feat: 회원가입 화면과 링크 추가"'), ("o", "[main ae7574c] feat: 회원가입 화면과 링크 추가")],
          top=228, w=1728, size=26, lh=1.42, tid="t-ex2")
XT.label(5, "고친 건 두 파일인데 하나뿐이에요", "#F2C46D", order=1, x=1000)
XT.label(10, "회원가입 파일이 빠졌어요", "#F28B82", order=2, x=1000)
XT.label(13, "이제 두 파일이 다 들어가요", "#7FD18B", n=3, order=3, x=1000)
XT.tint(5, 1, "y", order=1)
XT.tint(13, 3, "g", order=3)
x2.append(XT.html())
x2.append(XT.pen(10, order=2, x0=XT.left + XT.padx + 110))
x2.append(cap(XT.bottom + 28, "새 파일은 git diff에 안 나와서 놓치기 쉬워요. 커밋 전에 파일 개수를 세어 봐요.", size=30, color=INK, attrs=' data-build-in="fade order 4"'))
W("ex2", x2, "커밋 직전에 git diff --staged --stat으로 들어갈 파일 목록을 보면 빠뜨린 파일을 찾아요. 회원가입 링크와 회원가입 파일을 같이 만들었는데 login.md만 add했어요. 파일 개수가 하나뿐이라 status를 보니 signup.md가 Untracked로 남아 있었어요. 다시 add하고 --stat으로 두 파일을 확인한 뒤 커밋했어요. status의 안내 줄과 On branch main 줄은 화면 때문에 뺐어요.")

# ---------- cheatsheet ----------
ch = [sec("cheatsheet"), f'<h2 style="position:absolute;left:96px;top:96px;font-size:60px;font-weight:700;line-height:1.2;color:{INK}">한 장 요약</h2>']
SUM = [("add 전", "git diff", C_WD, "status 빨간 글씨 파일의 고친 줄"),
       ("commit 전", "git diff --staged", C_ST, "커밋에 들어갈 줄, --stat으로 파일 수"),
       ("commit 뒤", "git show", NAVY, "커밋 하나가 바꾼 것"),
       ("merge 전", "git diff main 브랜치", OR, "받을 쪽을 앞에, 충돌 나면 git diff"),
       ("처음부터", ".gitignore", PUR, ".env, .venv/, __pycache__/, *.log")]
SH = 120
ch.append(f'<div{STAGGER(1, 90)} style="position:absolute;left:0;top:0;width:1920px;height:1080px">')
for i, (when, cmd, col, what) in enumerate(SUM):
    bd = f"border-top:2px solid {LINE};" if i else ""
    ch.append(f'<div style="position:absolute;left:96px;top:{224 + i * SH}px;width:1728px;height:{SH}px;{bd}display:flex;flex-direction:row;align-items:center;gap:32px;padding:0 12px">'
              + p(f"width:220px;flex:none;font-size:34px;font-weight:700;color:{INK}", when)
              + p(f"width:560px;flex:none;font-family:{MONO};font-size:34px;font-weight:700;color:{col}", e(cmd))
              + p(f"flex:1;font-size:28px;color:{SUB}", e(what)) + '</div>')
ch.append('</div>')
ch.append(f'<div data-build-in="rise order 2" style="position:absolute;left:96px;top:{224 + 5 * SH + 20}px;width:1728px;height:96px;background:#1B2029;border-radius:18px;padding:0 40px;display:flex;flex-direction:row;align-items:center;gap:56px;font-family:{MONO}">'
          + "".join(f'<p style="font-size:32px;font-weight:700;color:{c_}">{t_}<span style="font-family:{SANS};font-weight:400;color:#D8DEE9;margin-left:14px">{d_}</span></p>'
                    for t_, c_, d_ in [("-", "#F28B82", "지운 줄"), ("+", "#7FD18B", "넣은 줄"), ("@@", "#7CC7E8", "위치"), ("q", "#F2C46D", "나가기")]) + '</div>')
ch.append(cap(224 + 5 * SH + 156, "다음 05에서는 VS Code Git Graph로 이 기록을 그림으로 봐요.", size=30, color=INK, attrs=' data-build-in="fade order 2"'))
W("cheatsheet", ch, "add, commit, merge 직전에는 status로 보고 diff로 확인한 다음 넘어가요. 수업 끝에 이 장을 띄워 두고 상황마다 무엇을 칠지 학생이 직접 말해 보게 하세요.")
print("ok")
