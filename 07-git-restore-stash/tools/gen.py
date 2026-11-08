"""Generates every slide of the git restore and stash deck (07).

Scenes reuse the zones of 02 (작업 폴더, 대기실, 내 저장소, 원격 저장소) as filled panels with no outline.
The restore parts crop to the three local zones. The stash part adds the remote zone and a drawer under
작업 폴더; the file card flies into the drawer and back out. Labels sit on the drawing, not in cards.
Highlights come from tools/HIGHLIGHT.md (spot, ring, underline, box, fly). No typing animation.
Terminal output comes from tools/demo.sh (git 2.43).
Usage (in 07-git-restore-stash): python3 tools/gen.py slides
"""
import html, os, sys, unicodedata

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from highlight import spot, spot_off, ring, box, underline  # noqa: E402

OUT = sys.argv[1]
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
INK, SUB, MUTE, HAIR = "#1D2330", "#4A5262", "#6A7180", "#D9D6CE"
BL, GR, OR, RED, PUR = "#2459C9", "#1F8A4C", "#B26A00", "#A33131", "#5A3BB8"
C_RS, C_UN, C_SH = "#A33131", "#1A7340", "#B26A00"   # restore = red (버림), --staged = green, stash = orange
BG = "#F6F5F1"


def e(s):
    return html.escape(s, quote=False)


def p(style, text, attrs=""):
    return f'<p{attrs} style="{style}">{text}</p>'


def W(name, parts, notes):
    body = "\n".join(parts) + f"\n<aside>{e(notes)}</aside>\n</section>\n"
    open(os.path.join(OUT, name + ".html"), "w").write(body)


def sec(i, transition="fade"):
    return f'<section id="{i}" data-transition="{transition}" style="background:{BG};color:{INK};font-family:{SANS};padding:96px;display:flex;flex-direction:column;word-break:keep-all">'


def head(eyebrow, title, color=BL):
    return [p(f"position:absolute;left:96px;top:48px;width:1728px;font-size:26px;font-weight:700;color:{color}", e(eyebrow), ' id="eyebrow"'),
            f'<h2 id="title" style="position:absolute;left:96px;top:92px;width:1728px;font-size:52px;font-weight:700;line-height:1.2;color:{INK}">{title}</h2>']


def hair(x, y, w, color=HAIR, h=2):
    return f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{color}"></div>'


def vhair(x, y, h, color=HAIR):
    return f'<div style="position:absolute;left:{x}px;top:{y}px;width:2px;height:{h}px;background:{color}"></div>'


def em_width(s):
    """Width of a mono line in em: ASCII 0.6, Hangul and other wide glyphs 1.0."""
    return sum(1.0 if unicodedata.east_asian_width(c) in "WF" else 0.6 for c in s)


# ---------- terminal ----------
# $ 명령, o 출력, r 빨강, g 초록, # 회색 안내, c 파랑(diff 머리), h 흰 굵게, H 눈여겨볼 줄
TC = {"$": "#F2C46D", "o": "#D8DEE9", "h": "#FFFFFF", "c": "#7CC7E8", "r": "#F28B82", "g": "#7FD18B", "#": "#9AA3B5", "H": "#FFE7A8", "Y": "#FFE7A8"}
TPAD_X, TPAD_Y = 36, 26


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


def text_of(kind, t):
    return ("$ " + t if kind == "$" else t).replace("\t", " " * 8)


class Term:
    """A terminal that hugs its lines. Font size fits the box width and the room below (max 34px).
    After building, .y(i) is the top of line i and .x(col, i) the x of a column, for drawn highlights."""

    def __init__(self, lines, left, top, w, room, size=None, lh=1.4, tid="term", maxsize=34):
        self.lines, self.left, self.top, self.w, self.lh = lines, left, top, w, lh
        widest = max(em_width(text_of(k, t)) for k, t in lines)
        fit_w = (w - 2 * TPAD_X) / widest
        fit_h = (room - 2 * TPAD_Y) / (len(lines) * lh)
        self.size = size or int(min(maxsize, fit_w, fit_h))
        self.h = round(len(lines) * self.size * lh + 2 * TPAD_Y)
        self.tid = tid

    def y(self, i):
        return self.top + TPAD_Y + i * self.size * self.lh

    def x(self, s):
        """x where text s (the part of the line before a column) ends."""
        return self.left + TPAD_X + em_width(s) * self.size

    def html(self):
        o = [f'<div id="{self.tid}" style="position:absolute;left:{self.left}px;top:{self.top}px;width:{self.w}px;height:{self.h}px;background:#1B2029;border-radius:20px;padding:{TPAD_Y}px {TPAD_X}px;display:flex;flex-direction:column;font-family:{MONO};font-variant-ligatures:none">']
        for kind, text in self.lines:
            t = e(text_of(kind, text))
            lead = len(t) - len(t.lstrip(" "))
            t = "&#160;" * lead + t.lstrip(" ") if t.strip() else "&#160;"
            bold = "font-weight:700;" if kind in "$hHY" else ""
            mark = "background:rgba(242,196,109,0.18);border-radius:6px;margin:0 -10px;padding:0 10px;align-self:flex-start;" if kind == "H" else ""
            o.append(p(f"font-size:{self.size}px;line-height:{self.lh};white-space:pre;{bold}{mark}color:{TC[kind]}", t))
        o.append('</div>')
        return o

    def line_box(self, i, pad=8):
        """x, y, w, h around the ink of line i."""
        k, t = self.lines[i]
        x0 = self.left + TPAD_X
        lead = len(t) - len(t.lstrip(" \t"))
        x0 += em_width(text_of(k, t)[:lead + (2 if k == "$" else 0)].replace("\t", " " * 8)) * self.size if lead else 0
        x1 = self.x(text_of(k, t))
        return round(x0 - pad), round(self.y(i) + 2), round(x1 - x0 + 2 * pad), round(self.size * self.lh - 4)


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
            ("r", "Please commit your changes or stash them before you merge."), ("o", "Aborting")]
PULL_OK = [("o", "From https://github.com/kim/hello-git"), ("o", " * branch            main       -> FETCH_HEAD"), ("o", f"Updating {H1}..{HL}"), ("o", "Fast-forward"),
           ("o", " login.md | 2 +-"), ("o", " 1 file changed, 1 insertion(+), 1 deletion(-)")]
WIP1 = f"WIP on main: {H1} feat: 로그인 버튼 추가"

V0 = ["# 로그인", "아이디", "비밀번호"]
V1 = V0 + ["로그인 버튼"]
VL = ["# 로그인 페이지", "아이디", "비밀번호", "로그인 버튼"]
VW = V1 + ["비밀번호 찾기"]
VM = VL + ["비밀번호 찾기"]

# ---------- zones ----------
# Filled panels with no outline, like the 02 deck. Two layouts:
#   LOCAL: the three zones on my computer, for the restore parts (GitHub is not used there).
#   FULL : four zones and a drawer under 작업 폴더, for the stash part.
ZSTYLE = {
    "wd": dict(bg="#FFFFFF", tc="#3A4150", sc="#6A7180", icon="Code", title="① 작업 폴더"),
    "st": dict(bg="#E9F6EE", tc="#1A7340", sc="#2D5E40", icon="CheckCircle", title="② 대기실"),
    "lr": dict(bg="#E8F0FD", tc="#1E3F8F", sc="#2E4D8F", icon="Database", title="③ 내 저장소"),
    "rm": dict(bg="#F0EBFD", tc="#5A3BB8", sc="#5A4A8F", icon="Cloud", title="④ 원격 저장소"),
}
GAP, IN = 32, 24
LOCAL = {"wd": (96, 600), "st": (728, 380), "lr": (1140, 684)}
FULL = {"wd": (96, 380), "st": (508, 240), "lr": (780, 508), "rm": (1320, 504)}
ZTOP, CARD_TOP = 228, 304
DRAWER_BG, DRAWER_TC = "#FCEFD9", "#8A5A12"
L = {"z": LOCAL, "zh": 340}


def zl(k):
    return L["z"][k][0]


def zw(k):
    return L["z"][k][1]


def zbot():
    return ZTOP + L["zh"]


def zone_box(k, pad=0):
    return zl(k) - pad, ZTOP - pad, zw(k) + 2 * pad, L["zh"] + 2 * pad


def frame(sid, eyebrow, title, layout="local", zh=340, transition="magic", color=BL):
    L["z"] = LOCAL if layout == "local" else FULL
    L["zh"] = zh
    o = [sec(sid, transition)] + head(eyebrow, title, color)
    zs = L["z"]
    last_local = "lr"
    lend = zl(last_local) + zw(last_local)
    o.append(f'<x-icon id="ic-local" name="Home" style="position:absolute;left:96px;top:178px;width:26px;height:26px;color:{MUTE}"></x-icon>')
    o.append(p(f"position:absolute;left:130px;top:175px;width:600px;font-size:24px;font-weight:700;color:{MUTE}", "내 컴퓨터", ' id="lbl-local"'))
    o.append(f'<div id="rule-local" style="position:absolute;left:96px;top:212px;width:{lend - 96}px;height:2px;background:#CDD0D6"></div>')
    if "rm" in zs:
        rl = zl("rm")
        o.append(f'<x-icon id="ic-remote" name="Globe" style="position:absolute;left:{rl}px;top:178px;width:26px;height:26px;color:{PUR}"></x-icon>')
        o.append(p(f"position:absolute;left:{rl + 34}px;top:175px;width:400px;font-size:24px;font-weight:700;color:{PUR}", "GitHub", ' id="lbl-remote"'))
        o.append(f'<div id="rule-remote" style="position:absolute;left:{rl}px;top:212px;width:{zw("rm")}px;height:2px;background:#C9BCF2"></div>')
    for k in zs:
        z = ZSTYLE[k]
        o.append(f'<div id="z-{k}" style="position:absolute;left:{zl(k)}px;top:{ZTOP}px;width:{zw(k)}px;height:{zh}px;background:{z["bg"]};border-radius:20px;padding:20px {IN}px">'
                 '<div style="display:flex;flex-direction:row;gap:12px;align-items:center">'
                 f'<x-icon name="{z["icon"]}" style="width:32px;height:32px;color:{z["tc"]}"></x-icon>'
                 + p(f"font-size:30px;font-weight:700;color:{z['tc']}", z["title"]) + '</div></div>')
    return o


def placeholder(k, text, top=None, pid=None):
    return p(f"position:absolute;left:{zl(k) + IN}px;top:{top or CARD_TOP}px;width:{zw(k) - 2 * IN}px;font-size:26px;color:{ZSTYLE[k]['sc']}", e(text), f' id="{pid or "ph-" + k}"')


DOC_ST = {"red": ("#FBE4E2", "#A33131"), "green": ("#D3EEDD", "#1A7340"), "gray": ("#EEEFF2", "#3A4150"),
          "white": ("#FFFFFF", "#3A4150"), "orange": ("#FFFFFF", "#8A5A12")}
MARK = {"add": "background:#D3EEDD;color:#14532D", "del": "background:#FBE4E2;color:#7A1F1F;text-decoration:line-through", None: f"color:{INK}"}
DOC_FS, DOC_LH = 24, 1.4


def doc_h(n):
    return round(14 * 2 + DOC_FS * 1.3 + 6 + n * DOC_FS * DOC_LH)


def card(cid, left, top, w, lines, label, style, marks=None, name="login.md", attrs=""):
    bg, col = DOC_ST[style]
    marks = marks or {}
    o = [f'<div id="{cid}"{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{doc_h(len(lines))}px;background:{bg};border-radius:14px;padding:14px 18px;display:flex;flex-direction:column;gap:6px">']
    o.append('<div style="display:flex;flex-direction:row;justify-content:space-between;align-items:baseline;gap:12px">'
             + p(f"font-family:{MONO};font-size:{DOC_FS}px;font-weight:700;line-height:1.3;color:{INK}", name)
             + p(f"font-size:20px;font-weight:700;line-height:1.3;white-space:nowrap;color:{col}", e(label)) + '</div>')
    o.append('<div style="display:flex;flex-direction:column">')
    for i, l in enumerate(lines):
        o.append(p(f"font-family:{MONO};font-size:{DOC_FS}px;line-height:{DOC_LH};padding:0 8px;margin:0 -8px;border-radius:6px;white-space:pre;{MARK[marks.get(i)]}", e(l)))
    o.append('</div></div>')
    return "".join(o)


def doc(cid, k, lines, label, style, top=CARD_TOP, marks=None, w=None, attrs=""):
    return card(cid, zl(k) + IN, top, w or (zw(k) - 2 * IN), lines, label, style, marks, attrs=attrs)


CHIP_H, CHIP_P = 92, 104


def chip(cid, k, name, status, style, top, attrs=""):
    bg, col = DOC_ST[style]
    return (f'<div id="{cid}"{attrs} style="position:absolute;left:{zl(k) + IN}px;top:{top}px;width:{zw(k) - 2 * IN}px;height:{CHIP_H}px;background:{bg};border-radius:14px;padding:12px 18px;display:flex;flex-direction:column;gap:2px">'
            + p(f"font-family:{MONO};font-size:28px;font-weight:700;line-height:1.3;color:{INK}", e(name))
            + p(f"font-size:22px;font-weight:700;line-height:1.3;white-space:nowrap;color:{col}", e(status)) + '</div>')


def cover(cid, k, top, h, attrs=""):
    """A plain patch in the zone's color, laid over something that leaves on a click."""
    return f'<div id="{cid}"{attrs} style="position:absolute;left:{zl(k) + IN - 4}px;top:{top - 4}px;width:{zw(k) - 2 * IN + 8}px;height:{h + 8}px;background:{ZSTYLE[k]["bg"]}"></div>'


FS_H = 26
CW_H = FS_H * 0.6


def commit_row(k, h, top=CARD_TOP, rid="lc", tag="main", color=BL, attrs=""):
    tag_html = (p(f"font-family:{MONO};font-size:{FS_H}px;font-weight:700;line-height:38px;padding:0 12px;border-radius:8px;background:{color};color:#FFFFFF", tag) if tag else "")
    return (f'<div id="{rid}-{h}"{attrs} style="position:absolute;left:{zl(k) + IN}px;top:{top}px;height:38px;display:flex;flex-direction:row;gap:12px;align-items:center">'
            f'<x-shape kind="ellipse" style="width:24px;height:24px;flex:none;background:{color};border:3px solid {color}"></x-shape>'
            + p(f"font-family:{MONO};font-size:{FS_H}px;font-weight:700;color:{INK}", h) + tag_html + '</div>')


def label(left, top, w, text, color=BL, order=None, size=26, attrs="", kind="pop"):
    """Words on the drawing, right beside what they explain. No box."""
    b = f' data-build-in="{kind} order {order}"' if order else ""
    return p(f"position:absolute;left:{left}px;top:{top}px;width:{w}px;font-size:{size}px;font-weight:700;line-height:1.4;color:{color}", text, b + attrs)


def zlabel(k, top, text, color=None, order=None, span_to=None):
    l = zl(k) + IN
    r = (zl(span_to) + zw(span_to) if span_to else zl(k) + zw(k)) - IN
    return label(l, top, r - l, text, color or ZSTYLE[k]["tc"], order)


# drawer: under 작업 폴더 in the FULL layout
def drawer(top, h):
    x, w = zl("wd"), zw("wd")
    return [f'<div id="drawer" style="position:absolute;left:{x}px;top:{top}px;width:{w}px;height:{h}px;background:{DRAWER_BG};border-radius:20px;padding:20px {IN}px">'
            '<div style="display:flex;flex-direction:row;gap:12px;align-items:center">'
            f'<x-icon name="Archive" style="width:32px;height:32px;color:{C_SH}"></x-icon>'
            + p(f"font-size:30px;font-weight:700;color:{C_SH}", "서랍 (stash)") + '</div></div>']


def dr_card(cid, top, lines, lab, marks=None, attrs=""):
    return card(cid, zl("wd") + IN, top + 76, zw("wd") - 2 * IN, lines, lab, "orange", marks, attrs=attrs)


def dr_cover(cid, top, h, attrs=""):
    return f'<div id="{cid}"{attrs} style="position:absolute;left:{zl("wd") + IN - 4}px;top:{top + 72}px;width:{zw("wd") - 2 * IN + 8}px;height:{h + 8}px;background:{DRAWER_BG}"></div>'


def num(i, color, size=56):
    return p(f"width:{size}px;height:{size}px;flex:none;font-size:{size // 2}px;font-weight:900;line-height:{size}px;text-align:center;color:#FFFFFF;background:{color};border-radius:{size // 2}px", str(i))


# ======================================================================
# cover
# ======================================================================
cov = [f'<section id="cover" data-transition="fade" style="background:#1D2330;color:#F6F5F1;font-family:{SANS};padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#8FB3FF">KANT AX/AI 엔지니어 트랙 · 07</p>',
       '<h1 style="font-size:104px;font-weight:900;line-height:1.1;color:#F6F5F1">커밋 전 변경<br>버리고, 잠깐 치우기</h1>',
       '<p style="font-size:40px;line-height:1.4;color:#BFC6D4">git restore와 git stash</p>']
cov.append(f'<div style="position:absolute;left:1120px;top:330px;width:672px;height:420px;background:#252B36;border-radius:24px;padding:44px 48px;display:flex;flex-direction:column;justify-content:center;gap:10px;font-family:{MONO}">')
for k, l in [("$", "$ git restore login.md"), ("#", "  고친 걸 버려요"), ("$", "$ git stash"), ("#", "  서랍에 넣어요"), ("$", "$ git stash pop"), ("#", "  서랍에서 꺼내요")]:
    cov.append(p(f"font-size:34px;line-height:1.45;white-space:pre;font-weight:{700 if k == '$' else 400};color:{TC[k]}", e(l)))
cov.append('</div>')
W("cover", cov, "커밋하기 전의 변경을 버리고, 잠깐 치워 두는 명령을 배워요. 02의 네 칸 그림과 hello-git 저장소, login.md로 이어서 실습해요. 고친 걸 버리는 git restore, add를 취소하는 git restore --staged, 고치던 걸 잠깐 치우는 git stash 세 가지예요. 팀 레포에서 pull이 막힐 때 바로 쓰는 명령이에요.")

# ======================================================================
# toc: hairline list, like the 02 deck
# ======================================================================
PARTS = [(C_RS, "git restore", "고친 걸 버리기, 버리기 전에 git diff", "5–8쪽"),
         (C_UN, "git restore --staged", "add 취소하기, --staged가 있고 없고", "9–11쪽"),
         (C_SH, "git stash", "pull이 막힐 때 서랍에 넣고 꺼내기", "12–16쪽"),
         (BL, "비교하기", "reset과의 차이, 버릴까 치울까 남길까", "17–18쪽"),
         (RED, "막힐 때", "pop 충돌 풀기, 자주 나오는 메시지", "19–21쪽"),
         (PUR, "팀에서 쓰기", "팀원이 push했을 때, 급히 브랜치를 옮길 때", "22–23쪽")]
t = [f'<section id="toc" data-transition="fade" style="background:{BG};color:{INK};font-family:{SANS};padding:96px;display:flex;flex-direction:column;word-break:keep-all">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>',
     hair(96, 196, 1728, INK)]
RH = 118
for i, (c, h, s, pg) in enumerate(PARTS):
    y = 198 + i * RH
    mono = h.startswith("git")
    t.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:{RH}px;display:flex;flex-direction:row;align-items:center;padding:0 10px">'
             + p(f"width:96px;flex:none;font-size:52px;font-weight:900;color:{c}", str(i + 1))
             + p(f"width:500px;flex:none;font-family:{MONO if mono else SANS};font-size:{36 if mono else 40}px;font-weight:700;color:{INK}", h)
             + p(f"flex:1;font-size:30px;color:{SUB}", s)
             + p(f"width:160px;flex:none;text-align:right;font-size:30px;font-weight:700;color:{c}", pg) + '</div>')
    t.append(hair(96, y + RH, 1728))
t.append(p(f"position:absolute;left:96px;top:{198 + 6 * RH + 40}px;width:1728px;font-size:30px;color:{SUB}", "24쪽은 한 장 요약이에요. 1부부터 3부까지는 hello-git 저장소 하나로 이어서 실습해요."))
W("toc", t, "여섯 부분으로 나눠서 봐요. 1부부터 3부까지는 명령을 하나씩 실습하고, 4부에서 앞 챕터의 reset과 비교해요. 5부는 막혔을 때 푸는 법, 6부는 오늘 팀 실습에서 그대로 쓰는 순서예요.")

# ======================================================================
# why: three moments, one row each. The command arrives after the moment.
# ======================================================================
w = [sec("why")] + head("들어가기", "이럴 때 쓰는 명령이에요")
cases = [(C_RS, "파일을 망쳤어요", 'echo "로그인 버튼" > login.md', "&gt;&gt; 대신 &gt; 를 쳐서 세 줄이 사라졌어요", "git restore"),
         (C_UN, "엉뚱한 파일까지 올렸어요", "git add .", "개인 메모 memo.md까지 대기실에 올라갔어요", "git restore --staged"),
         (C_SH, "pull이 막혀요", "git pull origin main", "고치던 게 있는데 팀원이 push했대요", "git stash")]
w.append(hair(96, 228, 1728, INK))
RH = 214
for i, (c, q, cmd, d, sol) in enumerate(cases):
    y = 230 + i * RH
    w.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:{RH}px;display:flex;flex-direction:row;align-items:center;gap:40px;padding:0 10px">'
             + p(f"width:56px;flex:none;font-size:56px;font-weight:900;color:{c}", str(i + 1))
             + '<div style="flex:1;display:flex;flex-direction:column;gap:12px">'
             + p(f"font-size:42px;font-weight:700;line-height:1.25;color:{INK}", q)
             + '<div style="display:flex;flex-direction:row;gap:20px;align-items:baseline">'
             + p(f"font-family:{MONO};font-size:28px;font-weight:700;white-space:pre;color:{MUTE}", "$ " + e(cmd))
             + p(f"font-size:28px;color:{SUB}", d) + '</div></div>'
             + p(f"width:470px;flex:none;font-family:{MONO};font-size:36px;font-weight:700;color:{c}", sol, f' data-build-in="fade order {i + 1}"')
             + '</div>')
    w.append(hair(96, y + RH, 1728))
w.append(p(f"position:absolute;left:96px;top:{230 + 3 * RH + 44}px;width:1728px;font-size:32px;line-height:1.4;color:{SUB}", "셋 다 아직 커밋하지 않은 변경을 다뤄요.", ' data-build-in="fade order 4"'))
W("why", w, "셋 다 아직 커밋하지 않은 변경을 다루는 장면이에요. 첫째는 01에서 배운 > 와 >> 를 헷갈린 경우예요. > 는 파일을 새로 덮어쓰고, >> 는 끝에 붙여요. 둘째는 git add . 이 폴더 안 바뀐 파일을 모두 올려서 생겨요. 셋째는 오늘 팀 실습에서 가장 많이 막히는 곳이에요. 커밋한 뒤의 되돌리기는 02와 03에서 배운 reset과 revert가 맡아요.")

# ======================================================================
# map: the big picture. Four zones, the drawer under 작업 폴더, arrows with their command.
# The spotlight walks restore, --staged, stash in order.
# ======================================================================
m = [sec("map")] + head("들어가기", "커밋은 그대로 두고 ①과 ②만 바꿔요")
MT, MH = 400, 200
L["z"] = FULL
for k in FULL:
    z = ZSTYLE[k]
    op = ";opacity:0.45" if k == "rm" else ""
    desc = {"wd": "지금 고치는 파일", "st": "add로 올린 모습", "lr": "commit한 기록", "rm": "이번엔 거의 안 써요"}[k]
    m.append(f'<div style="position:absolute;left:{zl(k)}px;top:{MT}px;width:{zw(k)}px;height:{MH}px;background:{z["bg"]};border-radius:20px;padding:24px {IN}px;display:flex;flex-direction:column;gap:14px{op}">'
             '<div style="display:flex;flex-direction:row;gap:12px;align-items:center">'
             f'<x-icon name="{z["icon"]}" style="width:34px;height:34px;color:{z["tc"]}"></x-icon>'
             + p(f"font-size:32px;font-weight:700;color:{z['tc']}", z["title"]) + '</div>'
             + p(f"font-size:26px;line-height:1.4;color:{z['sc']}", desc) + '</div>')
# arrows above the zones; both land on 작업 폴더
ARCS = [("st", "git restore --staged", C_UN, 330, 300), ("lr", "git restore", C_RS, 250, 210)]
for src, lab, col, y, xin in ARCS:
    x1 = zl("wd") + xin
    x2 = zl(src) + zw(src) // 2
    m.append(f'<div style="position:absolute;left:{x1 - 3}px;top:{y}px;width:{x2 - x1 + 6}px;height:{MT - y - 4}px;border:6px solid {col};border-bottom:none;border-radius:16px 16px 0 0"></div>')
    m.append(f'<x-connector x1="{x1}" y1="{MT - 30}" x2="{x1}" y2="{MT - 4}" head="end" style="color:{col};border-width:6px"></x-connector>')
    lw = round(em_width(lab) * 26 + 36)
    m.append(p(f"position:absolute;left:{x2 - lw // 2}px;top:{y - 22}px;width:{lw}px;font-family:{MONO};font-size:26px;font-weight:700;line-height:44px;text-align:center;border-radius:10px;background:{col};color:#FFFFFF", lab))
# drawer under 작업 폴더
DT = MT + MH + 110
m.append(f'<div style="position:absolute;left:{zl("wd")}px;top:{DT}px;width:{zw("wd")}px;height:{1024 - DT}px;background:{DRAWER_BG};border-radius:20px;padding:24px {IN}px;display:flex;flex-direction:column;gap:14px">'
         '<div style="display:flex;flex-direction:row;gap:12px;align-items:center">'
         f'<x-icon name="Archive" style="width:34px;height:34px;color:{C_SH}"></x-icon>' + p(f"font-size:32px;font-weight:700;color:{C_SH}", "서랍 (stash)") + '</div>'
         + p(f"font-size:26px;line-height:1.4;color:{DRAWER_TC}", "고치던 걸 잠깐 넣어 두는 곳") + '<div style="flex:1"></div>'
         + p(f"font-size:24px;line-height:1.4;color:{DRAWER_TC}", "내 컴퓨터에만 있어요.<br>push해도 올라가지 않아요") + '</div>')
ax1, ax2 = zl("wd") + 200, zl("wd") + 280
m.append(f'<x-connector x1="{ax1}" y1="{MT + MH + 8}" x2="{ax1}" y2="{DT - 8}" head="end" style="color:{C_SH};border-width:6px"></x-connector>')
m.append(f'<x-connector x1="{ax2}" y1="{DT - 8}" x2="{ax2}" y2="{MT + MH + 8}" head="end" style="color:{C_SH};border-width:6px"></x-connector>')
m.append(p(f"position:absolute;left:{ax1 - 196}px;top:{MT + MH + 34}px;width:180px;text-align:right;font-family:{MONO};font-size:26px;font-weight:700;color:{C_SH}", "git stash"))
m.append(p(f"position:absolute;left:{ax2 + 20}px;top:{MT + MH + 34}px;width:300px;font-family:{MONO};font-size:26px;font-weight:700;color:{C_SH}", "git stash pop"))
# what each one does, written beside the drawing in one column
ex = zl("st")
m.append(hair(ex, DT, 1824 - ex))
rows = [(C_RS, "git restore 파일", "③ 마지막 커밋 모습으로 ①을 덮어요"), (C_UN, "git restore --staged 파일", "②에서 내려요. ① 내용은 그대로예요"),
        (C_SH, "git stash", "①의 변경을 서랍에 넣고, pop으로 다시 꺼내요")]
for i, (c, lab, d) in enumerate(rows):
    y = DT + i * 104
    m.append(f'<div style="position:absolute;left:{ex}px;top:{y}px;width:{1824 - ex}px;height:104px;display:flex;flex-direction:row;align-items:center;gap:24px;padding:0 8px">'
             + p(f"width:500px;flex:none;font-family:{MONO};font-size:28px;font-weight:700;color:{c}", lab)
             + p(f"flex:1;font-size:28px;color:{INK}", d) + '</div>')
    m.append(hair(ex, y + 104, 1824 - ex))
# spotlight walk: restore arc + ① ③, then --staged arc + ① ②, then the drawer
m.append(spot(1, zl("wd"), 200, zl("lr") + zw("lr") - zl("wd"), MT + MH - 200, pad=14, r=24))
m.append(spot(2, zl("wd"), 280, zl("st") + zw("st") - zl("wd"), MT + MH - 280, pad=14, r=24))
m.append(spot(3, zl("wd"), MT + MH, zw("wd"), 1024 - MT - MH, pad=14, r=24))
m.append(spot_off(4))
W("map", m, "오늘 배우는 명령은 모두 ① 작업 폴더나 ② 대기실을 바꾸고, ③ 내 저장소의 커밋은 건드리지 않아요. 02의 네 칸 그림이에요. git restore는 빨간 화살표처럼 ③의 마지막 커밋 모습을 ①로 가져와요. git restore --staged는 초록 화살표처럼 ②에 올린 것을 내려요. git stash는 ①의 변경을 아래 서랍에 넣었다가 git stash pop으로 다시 꺼내요. 서랍도 내 컴퓨터 안에 있어서 GitHub에는 올라가지 않아요.")

# ======================================================================
# part 1: git restore (LOCAL layout)
# ======================================================================
LCW = 330
LR0 = lambda marks=None: [commit_row("lr", H0), doc("lr-doc", "lr", V0, "마지막 커밋", "gray", top=356, marks=marks, w=LCW)]
RLX = LOCAL["lr"][0] + IN + LCW + 28
RLW = 1824 - IN - RLX

o = frame("r1", "실습 1 · 고친 걸 버리기", "실수로 login.md를 덮어썼어요")
o.append(doc("wd-doc", "wd", ["로그인 버튼"], "덮어씀", "red", marks={0: "add"}, w=360))
o.append(zlabel("wd", CARD_TOP + doc_h(1) + 16, "세 줄이 사라지고<br>한 줄만 남았어요", RED))
o.append(placeholder("st", "비어 있음"))
o += LR0()
T = Term([("$", 'echo "로그인 버튼" > login.md'), ("$", "git status"), ("o", "On branch main"), ("o", "Changes not staged for commit:"), ("#", HINT_ADD),
          ("Y", HINT_RS), ("r", "\tmodified:   login.md"), ("o", ""), ("o", NO_ADD)], 96, zbot() + 32, 1728, 1024 - zbot() - 32)
o += T.html()
x, y, w_, h_ = T.line_box(5)
o.append(underline(1, x + 6, x + w_ - 6, round(y + h_ + 2), OR))
o.append(label(x + w_ + 24, round(y - 6), 1824 - (x + w_ + 24) - 36, "다음에 칠 명령을<br>알려 줘요", "#FFE7A8", 1, size=24))
W("r1", o, "status의 괄호 안 안내가 다음에 칠 명령을 알려 줘요. >> 대신 > 를 쳐서 login.md 세 줄이 사라지고 로그인 버튼 한 줄만 남았어요. 01에서 > 는 덮어쓰기, >> 는 끝에 붙이기라고 배웠어요. 밑줄 친 줄에 git restore가 나와요. 앞 챕터에서는 화면 때문에 이 안내 줄을 자주 뺐어요. 오늘은 이 줄을 읽어요.")

o = frame("r2", "실습 1 · 고친 걸 버리기", "버리기 전에 무엇이 사라질지 봐요")
o.append(doc("wd-doc", "wd", ["로그인 버튼"], "덮어씀", "red", marks={0: "add"}, w=360))
o.append(zlabel("wd", CARD_TOP + doc_h(1) + 16, "+ 줄: 버리면 사라져요", "#14532D"))
o.append(placeholder("st", "비어 있음"))
o += LR0({0: "del", 1: "del", 2: "del"})
o.append(label(RLX, 356 + 50, RLW, "- 줄: 버리면<br>돌아와요", RED, size=26))
T = Term([("$", "git diff")] + diff_lines(DIFF_OOPS), 96, zbot() + 32, 1728, 1024 - zbot() - 32)
o += T.html()
x, y, _, _ = T.line_box(6)
_, y2, _, h2 = T.line_box(8)
w3 = max(T.line_box(i)[2] for i in (6, 7, 8))
o.append(box(1, x - 4, y - 6, w3 + 8, y2 + h2 - y + 12, RED))
x9, y9, w9, h9 = T.line_box(9)
o.append(label(x + w3 + 48, round(y + 6), 700, "restore하면 돌아오는 세 줄", "#F28B82", 1, size=26))
W("r2", o, "restore는 되돌릴 수 없으니, 04에서 배운 git diff로 사라질 줄부터 봐요. - 세 줄이 원래 있던 줄, + 한 줄이 새로 생긴 줄이에요. restore를 치면 + 줄은 사라지고 - 줄이 돌아와요. 사라지는 + 줄 중에 남길 게 있는지 꼭 확인하고 넘어가요.")

o = frame("r3", "실습 1 · 고친 걸 버리기", "git restore로 마지막 커밋 모습으로 돌려요")
o.append(doc("wd-doc", "wd", ["로그인 버튼"], "덮어씀", "red", marks={0: "add"}, w=360))
o.append(cover("wd-cov", "wd", CARD_TOP, doc_h(3) + 60, ' data-build-in="fade order 1"'))
o.append(doc("wd-new", "wd", V0, "되돌림", "gray", w=360, attrs=' data-build-in="fly order 1" data-from="lr-doc"'))
o.append(placeholder("st", "비어 있음"))
o += LR0()
o.append(label(RLX, 356 + 50, RLW, "커밋은 그대로예요", ZSTYLE["lr"]["tc"], 2, size=26))
o.append(label(zl("wd") + IN, CARD_TOP + doc_h(3) + 16, zw("wd") - 2 * IN, "③ 모습으로 덮었어요", ZSTYLE["lr"]["tc"], 2))
T = Term([("$", "git restore login.md"), ("$", "cat login.md")] + [("o", l) for l in V0] + [("$", "git status"), ("o", "On branch main"), ("o", "nothing to commit, working tree clean")],
         96, zbot() + 32, 1728, 1024 - zbot() - 32)
o += T.html()
W("r3", o, "git restore 파일은 ③ 마지막 커밋의 모습을 ① 작업 폴더에 덮어써요. 아무 출력 없이 끝나요. cat으로 보면 세 줄이 돌아왔고, git status도 깨끗해요. 커밋 기록은 하나도 바뀌지 않았어요. 정확히는 ② 대기실의 모습으로 돌아가요. 대기실이 비어 있으면 마지막 커밋과 같은 모습이에요.")

# r-warn: the statement is the hero; three habits in a ruled list; the dangerous one is circled
wr = [sec("r-warn")] + head("실습 1 · 주의", "restore로 버린 줄은 되찾을 수 없어요", C_RS)
wr.append(p(f"position:absolute;left:96px;top:200px;width:1728px;font-size:32px;line-height:1.5;color:{SUB}",
            "커밋하지 않은 변경은 Git에 기록이 없어요. reset과 revert는 커밋을 다뤄서 기록이 남지만, restore로 버린 줄은 휴지통에도 가지 않아요."))
wr.append(hair(96, 330, 1728, INK))
tips = [("먼저 git diff로 봐요", "사라질 줄을 눈으로 확인해요", "git diff"),
        ("남길 게 있으면 커밋부터 해요", "커밋해 두면 나중에 되돌릴 수 있어요", 'git add 파일<br>git commit -m "..."'),
        ("파일 이름을 꼭 적어요", "점(.)을 쓰면 폴더 안 모든 파일의 변경을 한 번에 버려요", f'git restore login.md<br><span style="color:{C_RS}">git restore .</span>')]
RH = 216
for i, (h, d, cmd) in enumerate(tips):
    y = 332 + i * RH
    wr.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:{RH}px;display:flex;flex-direction:row;align-items:center;gap:36px;padding:0 10px">'
              + num(i + 1, C_RS) + '<div style="flex:1;display:flex;flex-direction:column;gap:10px">'
              + p(f"font-size:38px;font-weight:700;color:{INK}", h) + p(f"font-size:28px;color:{SUB}", d) + '</div>'
              + p(f"width:520px;flex:none;font-family:{MONO};font-size:30px;font-weight:700;line-height:1.5;color:{INK}", cmd) + '</div>')
    wr.append(hair(96, y + RH, 1728))
# underline "git restore ." inside the third row's description
y3 = 332 + 2 * RH
wr.append(underline(1, 1294, 1294 + round(em_width("git restore .") * 30), round(y3 + RH / 2 + 22.5 + 22), C_RS))
W("r-warn", wr, "restore로 버린 변경은 되찾을 수 없어서, 버리기 전에 세 가지를 지켜요. 02에서 본 reflog도 커밋만 기억해서 여기엔 소용없어요. 먼저 git diff로 보고, 남길 줄이 있으면 커밋부터 하고, 파일 이름을 꼭 적어요. git restore . 처럼 점을 쓰면 폴더 안 모든 파일의 변경이 한 번에 사라져요.")

# ======================================================================
# part 2: git restore --staged
# ======================================================================
o = frame("s1", "실습 2 · add 취소하기", "git add . 으로 memo.md까지 올라갔어요", color=C_UN)
o.append(chip("wd-login", "wd", "login.md", "고침", "gray", CARD_TOP))
o.append(chip("wd-memo", "wd", "memo.md", "새 파일", "gray", CARD_TOP + CHIP_P))
o.append(chip("st-login", "st", "login.md", "Staged · 고침", "green", CARD_TOP))
o.append(chip("st-memo", "st", "memo.md", "Staged · 새 파일", "green", CARD_TOP + CHIP_P))
o.append(commit_row("lr", H0))
o.append(label(zl("lr") + IN, CARD_TOP + 64, zw("lr") - 2 * IN, "이대로 commit, push하면<br>팀원 모두 내 메모를 받아요", RED, 1))
T = Term([("$", 'echo "로그인 버튼" >> login.md'), ("$", 'echo "내일 할 일: 디자인 묻기" > memo.md'), ("$", "git add ."), ("$", "git status"),
          ("o", "On branch main"), ("o", "Changes to be committed:"), ("H", HINT_UN), ("g", "\tmodified:   login.md"), ("g", "\tnew file:   memo.md")],
         96, zbot() + 32, 1728, 1024 - zbot() - 32)
o += T.html()
o.append(box(1, zl("st") + IN - 8, CARD_TOP + CHIP_P - 8, zw("st") - 2 * IN + 16, CHIP_H + 16, RED))
W("s1", o, "git add . 은 폴더 안 바뀐 파일을 모두 올려서, 개인 메모 memo.md까지 대기실에 들어갔어요. login.md에 로그인 버튼을 붙이고, 내 할 일을 적은 memo.md도 만든 상황이에요. 이대로 commit하고 push하면 팀원 모두가 내 메모를 받아요. 터미널의 노란 줄이 add를 취소하는 방법이에요. unstage는 대기실에서 내린다는 뜻이에요.")

o = frame("s2", "실습 2 · add 취소하기", "memo.md만 대기실에서 내려요", color=C_UN)
o.append(chip("wd-login", "wd", "login.md", "고침", "gray", CARD_TOP))
o.append(chip("wd-memo", "wd", "memo.md", "새 파일", "gray", CARD_TOP + CHIP_P))
o.append(chip("st-login", "st", "login.md", "Staged · 고침", "green", CARD_TOP))
o.append(chip("st-memo", "st", "memo.md", "Staged · 새 파일", "green", CARD_TOP + CHIP_P))
o.append(cover("st-cov", "st", CARD_TOP + CHIP_P, CHIP_H, ' data-build-in="fade order 1"'))
o.append(chip("wd-memo2", "wd", "memo.md", "Untracked · 내용 그대로", "red", CARD_TOP + CHIP_P, ' data-build-in="fly order 1" data-from="st-memo"'))
o.append(commit_row("lr", H0))
o.append(zlabel("wd", CARD_TOP + CHIP_P + CHIP_H + 14, "파일은 지워지지 않아요", RED, 2))
o.append(zlabel("st", CARD_TOP + CHIP_P, "login.md만 남았어요", C_UN, 2))
o.append(label(zl("lr") + IN, CARD_TOP + 64, zw("lr") - 2 * IN, "이제 login.md만<br>커밋해요", C_UN, 2))
T = Term([("$", "git restore --staged memo.md"), ("$", "git status"), ("o", "On branch main"), ("o", "Changes to be committed:"), ("#", HINT_UN), ("g", "\tmodified:   login.md"),
          ("o", ""), ("o", "Untracked files:"), ("#", '  (use "git add <file>..." to include in what will be committed)'), ("r", "\tmemo.md")],
         96, zbot() + 32, 1728, 1024 - zbot() - 32)
o += T.html()
W("s2", o, "git restore --staged는 대기실에서만 내리고, 파일은 작업 폴더에 그대로 둬요. memo.md는 처음 만든 파일이라 다시 Untracked가 됐어요. 이제 git commit -m \"feat: 로그인 버튼 추가\"로 login.md만 커밋하고 push해요. 실습에서는 memo.md를 rm으로 지우고 넘어가요. 계속 둘 파일이면 04에서 배운 .gitignore에 적어요.")

# s3: the two restores in a ruled table, then the proof in the terminal
c3 = [sec("s3")] + head("실습 2 · restore 두 가지", "--staged가 붙으면 대기실만 바꿔요", C_UN)
c3.append(hair(96, 200, 1728, INK))
rows = [("git restore 파일", C_RS, "③ → ①", "①의 고친 내용을 버려요", "되찾을 수 없어요"),
        ("git restore --staged 파일", C_UN, "② → ①", "②에서 ①로 내려요", "고친 내용은 그대로예요")]
for i, (lab, col, arrow_, desc, sub) in enumerate(rows):
    y = 202 + i * 120
    c3.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:120px;display:flex;flex-direction:row;align-items:center;gap:32px;padding:0 10px">'
              + p(f"width:560px;flex:none;font-family:{MONO};font-size:32px;font-weight:700;color:{col}", lab)
              + p(f"width:160px;flex:none;font-size:32px;font-weight:700;color:{col}", arrow_)
              + p(f"flex:1;font-size:32px;font-weight:700;color:{INK}", desc)
              + p(f"width:340px;flex:none;font-size:28px;color:{SUB}", sub) + '</div>')
    c3.append(hair(96, y + 120, 1728))
T = Term([("$", 'echo "아이디 저장" >> login.md'), ("$", "git add login.md"), ("$", "git restore --staged login.md"), ("$", "git diff")] + diff_lines(DIFF_KEEP),
         96, 482, 1000, 1024 - 482)
c3 += T.html()
xk, yk, wk, hk = T.line_box(len(T.lines) - 1)
c3.append(box(1, xk - 4, yk - 4, wk + 8, hk + 8, GR))
lx = round(xk + wk + 36)
c3.append(label(lx, round(yk + hk / 2) - 22, 96 + 1000 - 32 - lx, "add를 취소해도 남아요", "#7EE2A8", 1, size=28))
c3.append(label(1144, round(yk + hk) - 96, 680, "--staged를 빼면<br>이 줄까지 사라져요", SUB, 2, size=32, kind="fade"))
W("s3", c3, "--staged가 붙으면 대기실만 고치고, 붙지 않으면 작업 폴더의 파일을 덮어써요. 두 명령은 이름이 비슷해서 헷갈려요. 아래 터미널은 login.md를 add한 뒤 --staged로 내린 장면이에요. git diff에 아이디 저장이 그대로 나와요. 다시 올리려면 git add만 치면 돼요. 확인한 뒤 실습에서는 git restore login.md로 이 줄을 버리고 넘어가요.")

# ======================================================================
# part 3: git stash (FULL layout with the drawer)
# ======================================================================
ZH_S = 340
DTOP = ZTOP + ZH_S + 32
DH = 1024 - DTOP
TL = 508  # terminal left = 대기실 left


def remote(o, note=True):
    o.append(commit_row("rm", HL, rid="rc", tag="", color=PUR))
    o.append(commit_row("rm", H1, top=CARD_TOP + 52, rid="rc", tag="", color=PUR))
    if note:
        o.append(label(zl("rm") + IN, CARD_TOP + 120, zw("rm") - 2 * IN, "lee가 login.md 제목을<br>고쳐 올렸어요", PUR, size=26, attrs=' id="rm-note"'))


def stash_frame(sid, title, transition="magic"):
    o = frame(sid, "실습 3 · 잠깐 치우기", title, layout="full", zh=ZH_S, transition=transition, color=C_SH)
    o += drawer(DTOP, DH)
    return o


o = stash_frame("st0", "고치던 중에 pull하면 Git이 멈춰요", transition="fade")
o.append(doc("wd-doc", "wd", VW, "고치는 중", "red", marks={4: "add"}))
o.append(placeholder("st", "비어 있음"))
o.append(commit_row("lr", H1))
o.append(doc("lr-doc", "lr", V1, "마지막 커밋", "gray", top=356, w=360))
remote(o)
o.append(placeholder("wd", "비어 있음", top=DTOP + 76, pid="dr-empty"))
T = Term([("$", 'echo "비밀번호 찾기" >> login.md'), ("$", "git pull origin main")] + PULL_ERR, TL, DTOP, 1824 - TL, DH)
o += T.html()
x, y, w_, h_ = T.line_box(8)
o.append(box(1, x - 4, y - 4, w_ + 8, h_ + 8, RED))
W("st0", o, "고치던 파일을 pull이 덮을 수 있으면 Git이 멈추고, 커밋하거나 stash 하라고 알려 줘요. 팀원 lee가 login.md 제목을 로그인 페이지로 고쳐 push했어요. 나는 같은 파일에 비밀번호 찾기를 쓰던 중이고, 아직 커밋하기엔 덜 끝났어요. 상자 친 줄이 해결 방법이에요. 같은 파일을 둘 다 고쳤을 때만 이 메시지가 나와요.")

o = stash_frame("st1", "git stash로 고치던 걸 서랍에 넣어요")
o.append(doc("wd-doc", "wd", VW, "고치는 중", "red", marks={4: "add"}))
o.append(doc("wd-clean", "wd", V1 + [" "], "변경 없음", "gray", attrs=' data-build-in="fade order 1"'))
o.append(placeholder("st", "비어 있음"))
o.append(commit_row("lr", H1))
o.append(doc("lr-doc", "lr", V1, "마지막 커밋", "gray", top=356, w=360))
remote(o)
o.append(placeholder("wd", "비어 있음", top=DTOP + 76, pid="dr-empty"))
o.append(dr_cover("dr-cov", DTOP, 40, ' data-build-in="fade order 1"'))
o.append(dr_card("dr-doc", DTOP, VW, "stash@{0}", marks={4: "add"}, attrs=' data-build-in="fly order 1" data-from="wd-doc"'))
T = Term([("$", "git stash"), ("o", f"Saved working directory and index state {WIP1}"), ("$", "git status"), ("o", "On branch main"), ("o", "nothing to commit, working tree clean"),
          ("$", "git stash list"), ("H", f"stash@{{0}}: {WIP1}")], TL, DTOP, 1824 - TL, DH)
o += T.html()
o.append(label(TL, DTOP + T.h + 20, 1824 - TL, "작업 폴더가 마지막 커밋 모습으로 돌아왔어요", C_SH, 2))
W("st1", o, "git stash는 고치던 내용을 서랍에 넣고, 작업 폴더를 마지막 커밋 모습으로 돌려놓아요. 비밀번호 찾기 줄이 서랍으로 옮겨 갔어요. git status가 깨끗해져서 이제 pull할 수 있어요. git stash list로 서랍 안을 봐요. 서랍은 내 컴퓨터에만 있어서 push해도 GitHub에 올라가지 않아요. stash는 숨겨 둔다는 뜻이에요.")

# st-read: one line of stash list, read part by part; each part gets an underline and its words under it
rd = [sec("st-read")] + head("실습 3 · stash list 읽기", "stash list 한 줄은 네 부분이에요", C_SH)
segs = [("stash@{0}", "#F2C46D", "서랍 번호", "0이 가장 최근"), (": WIP on ", "#9AA3B5", "작업 중", "Work In Progress"), ("main", "#7CC7E8", "넣은 브랜치", "어디서 넣었나"),
        (f": {H1} feat: 로그인 버튼 추가", "#D8DEE9", "그때 마지막 커밋", "이 커밋 위에서 고치던 것")]
LS = 40
full = "".join(s for s, *_ in segs)
lw = em_width(full) * LS
lx = round(96 + (1728 - lw) / 2)
rd.append(f'<div style="position:absolute;left:96px;top:220px;width:1728px;height:140px;background:#1B2029;border-radius:20px"></div>')
rd.append(p(f"position:absolute;left:{lx}px;top:{220 + (140 - LS * 1.4) / 2:.0f}px;width:{lw + 20:.0f}px;font-family:{MONO};font-size:{LS}px;font-weight:700;line-height:1.4;white-space:pre;color:#D8DEE9",
            "".join(f'<span style="color:{c}">{e(s)}</span>' for s, c, *_ in segs)))
x = lx
ucol = {0: "#E0A93A", 1: "#9AA3B5", 2: "#4FA3C7", 3: "#9AA0AB"}
for i, (s, c, t1, t2) in enumerate(segs):
    sw = em_width(s) * LS
    lead = em_width(s) - em_width(s.lstrip(": ").rstrip(" ")) if s.startswith(":") else 0
    ux0 = x + (em_width(s[:len(s) - len(s.lstrip(': '))]) * LS if s.startswith(":") else 0)
    ux1 = x + sw - (em_width(s) - em_width(s.rstrip(" "))) * LS
    rd.append(underline(i + 1, round(ux0), round(ux1), 330, ucol[i]))
    # four even columns under the line; a leader joins each underline to its words
    cx = 96 + i * 432 + 24
    mx = round((ux0 + ux1) / 2)
    rd.append(f'<x-connector data-build-in="fade order {i + 1}" x1="{mx}" y1="344" x2="{cx + 4}" y2="410" style="color:{ucol[i]};border-width:3px"></x-connector>')
    rd.append(f'<div data-build-in="pop order {i + 1}" style="position:absolute;left:{cx}px;top:420px;width:400px;display:flex;flex-direction:column;gap:6px">'
              + p(f"font-size:34px;font-weight:700;color:{INK}", t1) + p(f"font-size:28px;color:{SUB}", t2) + '</div>')
    x += sw
rd.append(hair(96, 600, 1728))
T = Term([("$", "git stash"), ("$", "git stash list"), ("H", f"stash@{{0}}: WIP on main: {H3} feat: 비밀번호 재설정에 이메일 안내 추가"), ("o", f"stash@{{1}}: WIP on main: {H3} feat: 비밀번호 재설정에 이메일 안내 추가")],
         96, 640, 1728, 300, maxsize=32, lh=1.5)
rd += T.html()
rd.append(label(96, 640 + T.h + 28, 1728, "또 넣으면 새 것이 {0}, 예전 것은 {1}로 밀려요. pop은 맨 위 {0}부터 꺼내요.", C_SH, 5, size=30))
W("st-read", rd, "stash list 한 줄은 서랍 번호, 작업 중 표시, 넣은 브랜치, 그때의 마지막 커밋 네 부분이에요. 맨 앞 stash@{0}이 서랍 번호예요. WIP는 Work In Progress, 작업 중이라는 뜻이에요. 아래 터미널은 실습을 다 끝낸 뒤 stash를 두 번 한 모습이에요. 새로 넣은 게 늘 0번이에요. 여러 개가 쌓이면 무엇이 무엇인지 헷갈리니, 넣으면 바로 꺼내는 습관을 들여요.")

o = stash_frame("st2", "작업 폴더가 깨끗하니 pull이 돼요", transition="fade")
o.append(doc("wd-doc", "wd", VL + [" "], "받음", "gray", marks={0: "add"}))
o.append(placeholder("st", "비어 있음"))
o.append(commit_row("lr", HL))
o.append(doc("lr-doc", "lr", VL, "마지막 커밋", "gray", top=356, w=360, marks={0: "add"}))
remote(o)
o.append(dr_card("dr-doc", DTOP, VW, "stash@{0}", marks={4: "add"}))
T = Term([("$", "git pull origin main")] + PULL_OK, TL, DTOP, 1824 - TL, DH)
o += T.html()
o.append(spot(1, zl("wd"), ZTOP, zl("lr") + zw("lr") - zl("wd"), ZH_S, pad=10, r=26))
o.append(spot_off(2))
o.append(label(zl("lr") + IN + 280, CARD_TOP + 2, zw("lr") - 2 * IN - 280, "lee의 커밋", ZSTYLE["lr"]["tc"], 2, size=26))
o.append(label(TL, DTOP + T.h + 20, 1824 - TL, "서랍 안의 비밀번호 찾기는 그대로 기다려요", C_SH, 2))
W("st2", o, "작업 폴더가 깨끗하니 pull이 바로 끝나요. Fast-forward는 내 커밋이 없어서 이름표가 앞으로만 따라갔다는 뜻이에요. 03에서 본 것과 같아요. ①과 ③의 제목이 로그인 페이지로 바뀌었어요. 서랍 안의 비밀번호 찾기는 그대로 기다리고 있어요.")

o = stash_frame("st3", "git stash pop으로 서랍에서 꺼내요")
o.append(doc("wd-doc", "wd", VL + [" "], "받음", "gray"))
o.append(doc("wd-pop", "wd", VM, "고치는 중", "red", marks={4: "add"}, attrs=' data-build-in="fly order 1" data-from="dr-doc"'))
o.append(placeholder("st", "비어 있음"))
o.append(commit_row("lr", HL))
o.append(doc("lr-doc", "lr", VL, "마지막 커밋", "gray", top=356, w=360))
remote(o)
o.append(placeholder("wd", "비어 있음", top=DTOP + 76, pid="dr-empty"))
o.append(dr_card("dr-doc", DTOP, VW, "stash@{0}", marks={4: "add"}))
o.append(dr_cover("dr-cov", DTOP, doc_h(5), ' data-build-in="fade order 1"'))
o.append(placeholder("wd", "비어 있음", top=DTOP + 76, pid="dr-empty2").replace('style="', 'data-build-in="fade order 1" style="', 1))
T = Term([("$", "git stash pop"), ("o", "Auto-merging login.md"), ("o", "On branch main"), ("o", "Changes not staged for commit:"), ("r", "\tmodified:   login.md"),
          ("o", ""), ("H", "Dropped refs/stash@{0} (ea47a275d168793f5d750db2514463f36986122d)")], TL, DTOP, 1824 - TL, DH)
o += T.html()
o.append(label(TL, DTOP + T.h + 20, 1824 - TL, "받은 제목과 내 줄이 함께 있어요. 서랍은 비었어요", C_SH, 2))
W("st3", o, "pop은 서랍에서 꺼내 작업 폴더에 다시 얹고, 꺼낸 서랍은 지워요. Auto-merging은 받은 제목과 내 비밀번호 찾기를 Git이 알아서 합쳤다는 뜻이에요. 서로 다른 줄이라 충돌 없이 끝났어요. 마지막 Dropped 줄이 서랍에서 지웠다는 뜻이에요. 이제 하던 일을 마저 하고 add, commit, push해요.")

# ======================================================================
# part 4: 비교하기
# ======================================================================
rv = [sec("reset-vs")] + head("비교하기 · reset과 무엇이 달라요", "restore는 파일을, reset은 이름표를 옮겨요")
rv.append(vhair(960, 210, 380))


def mini_graph(x, y, tag_at, gid, fly_from=None, faded=None):
    g = [f'<div style="position:absolute;left:{x}px;top:{y + 19}px;width:260px;height:6px;background:#A9C0F0"></div>']
    for j, h in enumerate([H0, H1]):
        cx = x + j * 260
        look = "background:#F6F5F1;border:4px dashed #9DB8F2" if faded == j else f"background:{BL}"
        g.append(f'<div id="{gid}-c{j}" style="position:absolute;left:{cx - 22}px;top:{y}px;width:44px;height:44px;border-radius:50%;{look}"></div>')
        g.append(p(f"position:absolute;left:{cx - 80}px;top:{y + 58}px;width:160px;font-family:{MONO};font-size:26px;font-weight:700;text-align:center;color:{INK}", h))
    tx = x + tag_at * 260
    attrs = f' id="{gid}-tag"' + (f' data-build-in="fly order 1" data-from="{fly_from}"' if fly_from else "")
    g.append(p(f"position:absolute;left:{tx - 56}px;top:{y - 66}px;width:112px;font-family:{MONO};font-size:28px;font-weight:700;line-height:46px;text-align:center;border-radius:10px;background:{BL};color:#FFFFFF", "main", attrs))
    return g


# left: restore
rv.append(p(f"position:absolute;left:96px;top:220px;width:820px;font-family:{MONO};font-size:34px;font-weight:700;color:{C_RS}", "git restore 파일"))
rv += mini_graph(250, 400, 1, "ga")
rv.append(p(f"position:absolute;left:96px;top:530px;width:820px;font-size:30px;font-weight:700;color:{INK}", "커밋과 이름표는 그대로, ① ②의 파일만 바뀌어요"))
# right: reset. a faded tag stays where main was; the live tag flies back one commit
rv.append(p(f"position:absolute;left:1008px;top:220px;width:816px;font-family:{MONO};font-size:34px;font-weight:700;color:{BL}", "git reset HEAD~1"))
rv.append(p(f"position:absolute;left:{1160 + 260 - 56}px;top:334px;width:112px;font-family:{MONO};font-size:28px;font-weight:700;line-height:42px;text-align:center;border-radius:10px;border:2px dashed #9DB8F2;color:#9DB8F2", "main", ' id="gb-old"'))
rv += mini_graph(1160, 400, 0, "gb", fly_from="gb-old", faded=1)
rv.append(p(f"position:absolute;left:1008px;top:530px;width:816px;font-size:30px;font-weight:700;color:{INK}", "이름표가 한 칸 뒤로 가서 커밋이 취소돼요 (02, 03)"))
rows = [("", "바꾸는 곳", "커밋 기록", "언제"), ("git restore 파일", "① 작업 폴더", "그대로", "커밋 전, 고친 걸 버릴 때"), ("git restore --staged 파일", "② 대기실", "그대로", "커밋 전, add를 취소할 때"),
        ("git reset HEAD~1", "③ 이름표", "한 칸 뒤로", "push 전, 커밋을 취소할 때")]
TY = 640
rv.append(hair(96, TY, 1728, INK))
for j, r_ in enumerate(rows):
    y = TY + (0 if j == 0 else 64 + (j - 1) * 96)
    hgt = 64 if j == 0 else 96
    cells = "".join(p(f"width:{wd}px;flex:none;font-family:{MONO if (c == 0 and j) else SANS};font-size:{24 if j == 0 else 30}px;font-weight:{700 if (c == 0 and j) else 400};color:{MUTE if j == 0 else INK}", e(v))
                    for c, (v, wd) in enumerate(zip(r_, [520, 300, 260, 560])))
    rv.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:{hgt}px;display:flex;flex-direction:row;align-items:center;gap:20px;padding:0 10px">{cells}</div>')
    rv.append(hair(96, y + hgt, 1728))
W("reset-vs", rv, "restore는 커밋을 건드리지 않고 파일만 바꾸고, 02와 03에서 배운 reset은 이름표를 뒤로 옮겨 커밋을 취소해요. 그래서 커밋하기 전에는 restore, 커밋한 뒤에는 reset이나 revert를 써요. 옛날 자료에는 git reset HEAD 파일이름으로 add를 취소하는 법이 나와요. git restore --staged와 같은 일을 해요. 수업에서는 status가 알려 주는 restore --staged를 써요.")

# choose: one question branching into three answers; the spotlight lands on stash, the safe default
ch_ = [sec("choose")] + head("비교하기 · 고치던 게 있을 때", "버릴까, 치울까, 남길까")
opts = [(C_RS, "필요 없어요", "버리기", "git restore 파일", "되찾을 수 없어요"),
        (C_SH, "덜 끝났는데 pull, checkout 해야 해요", "잠깐 치우기", "git stash  →  git stash pop", "내 컴퓨터에만 있어요"),
        (BL, "커밋할 만큼 끝났어요", "남기기", 'git add 파일  →  git commit -m "..."', "기록에 남아요")]
RT, RH = 236, 256
ch_.append(f'<div style="position:absolute;left:96px;top:{RT + RH + 64}px;width:400px;height:128px;background:#FFFFFF;border-radius:20px;display:flex;align-items:center;justify-content:center">'
           + p(f"font-size:36px;font-weight:700;color:{INK}", "고치던 게 있어요") + '</div>')
BX = 640
for i, (c, cond, verb, cmd, note) in enumerate(opts):
    y = RT + i * RH
    cy = y + RH // 2
    ch_.append(f'<div id="opt-{i}" style="position:absolute;left:{BX}px;top:{y}px;width:{1824 - BX}px;height:{RH}px;display:flex;flex-direction:column;justify-content:center;gap:12px;padding:0 24px">'
               + '<div style="display:flex;flex-direction:row;gap:24px;align-items:baseline">'
               + p(f"font-size:44px;font-weight:900;color:{c}", verb) + p(f"font-size:30px;color:{SUB}", cond) + '</div>'
               + p(f"font-family:{MONO};font-size:32px;font-weight:700;white-space:pre;color:{INK}", e(cmd))
               + p(f"font-size:26px;color:{MUTE}", note) + '</div>')
    if i:
        ch_.append(hair(BX, y, 1824 - BX))
    # elbow from the question to this answer
    ch_.append(f'<div style="position:absolute;left:520px;top:{min(cy, RT + RH + 128):.0f}px;width:60px;height:{abs(cy - (RT + RH + 128)):.0f}px;border-left:4px solid #B9BDC6;{"border-top" if cy < RT + RH + 128 else "border-bottom"}:0"></div>' if False else "")
    ch_.append(f'<x-connector x1="500" y1="{RT + RH + 128}" x2="{BX - 12}" y2="{cy}" head="end" style="color:#9AA0AB;border-width:4px"></x-connector>')
ch_.append(spot(1, BX, RT + RH, 1824 - BX, RH, pad=4, r=20))
ch_.append(spot_off(2))
ch_.append(label(96, RT + RH + 64 + 128 + 28, 440, "모르겠으면 stash가<br>가장 안전해요", C_SH, 2, size=30))
W("choose", ch_, "고치던 게 있으면 셋 중 하나를 골라요. 고친 게 필요 없으면 restore로 버려요. 덜 끝났으면 stash로 치웠다가 pop으로 꺼내요. 끝났으면 커밋해요. 어느 쪽인지 모르겠으면 stash가 가장 안전해요. 지우지 않고 서랍에 넣어 두니까요.")

# ======================================================================
# part 5: 막힐 때
# ======================================================================
pc = [sec("pop-c")] + head("막힐 때 · 같은 줄을 고쳤다면", "pop에서 충돌이 나면 서랍이 비워지지 않아요", RED)
T = Term([("$", "git stash pop"), ("o", "Auto-merging login.md"), ("r", "CONFLICT (content): Merge conflict in login.md"), ("o", "On branch main"), ("o", "Unmerged paths:"),
          ("#", HINT_UN), ("#", '  (use "git add <file>..." to mark resolution)'), ("r", "\tboth modified:   login.md"), ("o", ""), ("o", "The stash entry is kept in case you need it again.")],
         96, 236, 1000, 814, lh=1.95)
pc += T.html()
x, y, w_, h_ = T.line_box(9)
pc.append(box(2, x - 4, y - 4, w_ + 8, h_ + 8, RED))
pc.append(label(96, 236 + T.h + 36, 1000, "실수해도 다시 꺼낼 수 있게 서랍에 남겨 둬요", RED, 2, size=32))
fl = [("o", "# 로그인 페이지"), ("o", "아이디"), ("o", "비밀번호"), ("o", "로그인 버튼"), ("c", "<<<<<<< Updated upstream"), ("u", "비밀번호 재설정"), ("c", "======="), ("s", "비밀번호 찾기 (이메일)"), ("c", ">>>>>>> Stashed changes")]
FX, FW = 1136, 688
FLH = 70
FT = 236
pc.append(f'<div id="file" style="position:absolute;left:{FX}px;top:{FT}px;width:{FW}px;height:{48 + 50 + len(fl) * FLH}px;background:#FFFFFF;border-radius:20px"></div>')
pc.append(p(f"position:absolute;left:{FX + 28}px;top:{FT + 24}px;width:300px;font-family:{MONO};font-size:28px;font-weight:700;color:{INK}", "login.md"))
for i, (k, l) in enumerate(fl):
    y = FT + 24 + 54 + i * FLH
    st = {"c": f"background:#FBE4E2;color:#7A1F1F;font-weight:700", "u": f"color:{PUR};font-weight:700", "s": f"color:{C_SH};font-weight:700", "o": f"color:{INK}"}[k]
    pc.append(p(f"position:absolute;left:{FX + 28}px;top:{y}px;width:{FW - 56}px;font-family:{MONO};font-size:27px;line-height:{FLH}px;padding:0 8px;margin-left:-8px;border-radius:6px;white-space:pre;{st}", e(l)))
for t1, c, line in [("받은 쪽 (lee)", PUR, 5), ("내 쪽 (서랍)", C_SH, 7)]:
    y = FT + 24 + 54 + line * FLH
    pc.append(p(f"position:absolute;left:{FX + FW - 40 - 240}px;top:{y}px;width:240px;text-align:right;font-size:26px;font-weight:700;line-height:{FLH}px;color:{c}", t1, ' data-build-in="pop order 1"'))
W("pop-c", pc, "같은 줄을 둘 다 고쳤으면 pop에서 충돌이 나고, 서랍의 내용은 지워지지 않고 남아요. 이번엔 lee가 비밀번호 찾기를 비밀번호 재설정으로 바꿔 push했고, 나는 같은 줄에 (이메일)을 붙이던 중이었어요. stash와 pull까지는 잘 되고 pop에서 충돌이 나요. 03에서 본 충돌 표시와 같지만, 이름이 HEAD 대신 Updated upstream, 브랜치 이름 대신 Stashed changes로 나와요. 위가 받은 것, 아래가 내 것이에요. 서랍이 남아 있으니 풀다가 틀려도 다시 꺼낼 수 있어요.")

pr = [sec("pop-r")] + head("막힐 때 · 충돌 풀기", "03처럼 풀고, 서랍을 비워요", RED)
rsteps = [("파일을 고쳐요", "표시 줄 세 개를 지우고 남길 내용으로", None), ("git add login.md", "다 풀었다고 알려요", None), ("git stash drop", "남아 있던 서랍을 비워요", C_SH),
          ('git commit -m "..."', "늘 하던 대로 커밋하고 push해요", None)]
SX, SW = 96, 600
pr.append(hair(SX, 210, SW, INK))
RH = 168
for i, (cmd, d, c) in enumerate(rsteps):
    y = 212 + i * RH
    cc = c or MUTE
    pr.append(f'<div data-build-in="fade order {i + 1}" style="position:absolute;left:{SX}px;top:{y}px;width:{SW}px;height:{RH}px;display:flex;flex-direction:row;gap:28px;align-items:center;padding:0 8px">'
              + num(i + 1, cc, 52) + '<div style="flex:1;display:flex;flex-direction:column;gap:16px">'
              + p(f"font-family:{MONO if cmd.startswith('git') else SANS};font-size:32px;font-weight:700;line-height:1.35;color:{INK}", cmd)
              + p(f"font-size:26px;color:{SUB}", d) + '</div></div>')
    pr.append(hair(SX, y + RH, SW))
y3 = 212 + 2 * RH
pr.append(underline(5, SX + 88, SX + 88 + round(em_width("git stash drop") * 32), round(y3 + (RH - 95) / 2 + 43 + 5), OR))
T = Term([("$", "cat login.md"), ("o", "# 로그인 페이지"), ("o", "아이디"), ("o", "비밀번호"), ("o", "로그인 버튼"), ("o", "비밀번호 재설정 (이메일)"), ("$", "git add login.md"), ("$", "git stash drop"),
          ("H", "Dropped refs/stash@{0} (30ebc16b62d989d22d6cf5dc856d28b138dee3ba)"), ("$", "git stash list"), ("$", 'git commit -m "feat: 비밀번호 재설정에 이메일 안내 추가"'),
          ("o", f"[main {H3}] feat: 비밀번호 재설정에 이메일 안내 추가"), ("$", "git push origin main"), ("o", f"   {HL2}..{H3}  main -> main")],
         736, 210, 1088, 814, lh=1.7)
pr += T.html()
W("pop-r", pr, "푸는 법은 03과 같고, 마지막에 git stash drop으로 남은 서랍을 지우는 단계만 더해요. 표시 줄 세 개를 지우고 남길 내용으로 고친 뒤 git add해요. 여기서는 둘을 합쳐 비밀번호 재설정 (이메일)로 했어요. drop은 꺼내지 않고 버리는 명령이라, 파일에 이미 반영한 뒤에만 써요. git stash list에 아무것도 안 나오면 서랍이 빈 거예요. push 출력의 첫 줄 To https://github.com/kim/hello-git.git은 화면 때문에 뺐어요.")

tb = [sec("t-1")] + head("막힐 때", "이런 메시지가 나오면 이렇게 해요", RED)
cases = [("No local changes to save", "고친 게 없거나 새 파일만 있어요. 새 파일은 add해야 서랍에 들어가요", "git add 파일<br>git stash"),
         ("stash list에 여러 줄이 있어요", "꺼내는 걸 잊었어요. 맨 위 {0}부터 하나씩 꺼내요", "git stash pop"),
         ("CONFLICT ... The stash entry is kept", "같은 줄을 둘 다 고쳤어요. 20쪽처럼 풀어요", "git add 파일<br>git stash drop"),
         ("error: pathspec 'signup2.md' did not match", "파일 이름이 틀렸어요. status로 이름을 확인해요", "git status"),
         ("fatal: Need to specify how to reconcile divergent branches.", "pull 설정이 없어요. 06에서 한 설정을 한 번 쳐요", "git config --global<br>pull.rebase false")]
tb.append(hair(96, 210, 1728, INK))
RH = 162
for i, (q, a_, cmd) in enumerate(cases):
    y = 212 + i * RH
    tb.append(f'<div data-build-in="fade order {i + 1}" style="position:absolute;left:96px;top:{y}px;width:1728px;height:{RH}px;display:flex;flex-direction:row;gap:32px;align-items:center;padding:0 10px">'
              + p(f"width:48px;flex:none;font-size:40px;font-weight:900;color:{RED}", str(i + 1))
              + '<div style="flex:1;display:flex;flex-direction:column;gap:10px">' + p(f"font-family:{MONO if q.isascii() else SANS};font-size:{28 if q.isascii() else 30}px;font-weight:700;color:{RED}", e(q))
              + p(f"font-size:26px;color:{SUB}", e(a_)) + '</div>'
              + p(f"width:420px;flex:none;font-family:{MONO};font-size:28px;font-weight:700;line-height:1.45;color:{INK}", cmd) + '</div>')
    tb.append(hair(96, y + RH, 1728))
W("t-1", tb, "자주 나오는 메시지 다섯 가지와 고치는 명령이에요. 1번은 새로 만든 파일만 있을 때 나요. Git이 아직 모르는 Untracked 파일은 stash에 들어가지 않아서, git add로 올린 뒤 stash해요. 2번은 pop을 잊고 또 stash했을 때예요. 3번은 19쪽과 20쪽의 장면이에요. 4번은 restore에 없는 파일 이름을 적었을 때예요. 파일 이름은 Tab 키로 자동 완성하면 틀리지 않아요. 5번은 pull 설정을 안 한 컴퓨터에서 내 main과 GitHub main이 갈라졌을 때 나요. 06에서 친 git config --global pull.rebase false를 한 번 치면 돼요.")

# ======================================================================
# part 6: 팀에서 쓰기 (real situations). A five-step timeline on top, the proof below.
# ======================================================================


def timeline(o, steps, top, hot, order0=1, size=28):
    """Five numbered nodes on one line; commands under them. hot: indices drawn in the stash color."""
    n = len(steps)
    cw = 1728 / n
    o.append(f'<div style="position:absolute;left:{96 + cw / 2:.0f}px;top:{top + 27}px;width:{cw * (n - 1):.0f}px;height:4px;background:#CDD0D6"></div>')
    for i, (cmd, d, c) in enumerate(steps):
        cx = 96 + cw * i + cw / 2
        o.append(f'<div data-build-in="fade order {order0 + i}" style="position:absolute;left:{96 + cw * i:.0f}px;top:{top}px;width:{cw:.0f}px;display:flex;flex-direction:column;align-items:center;gap:16px;padding:0 10px">'
                 + num(i + 1, c, 58)
                 + p(f"height:{round(2 * size * 1.4)}px;font-family:{MONO if cmd.startswith('git') else SANS};font-size:{size}px;font-weight:700;line-height:1.4;text-align:center;white-space:nowrap;color:{INK}", cmd)
                 + p(f"font-size:26px;line-height:1.4;text-align:center;color:{SUB}", d) + '</div>')


tf = [sec("team-flow")] + head("팀에서 쓰기 · 팀원이 먼저 push했을 때", "stash, pull, pop 뒤에 커밋해요", PUR)
steps = [("git stash", "고치던 걸 서랍에", C_SH), ("git pull origin main", "팀원 커밋 받기", PUR), ("git stash pop", "꺼내서 이어서", C_SH),
         ('git add login.md<br>git commit -m "..."', "마저 하고 커밋", BL), ("git push origin main", "올리기", PUR)]
timeline(tf, steps, 250, {0, 2}, size=24)
T = Term([("$", "git log --oneline"), ("o", f"{H2} (HEAD -> main, origin/main) feat: 비밀번호 찾기 추가"), ("o", f"{HL} feat: 로그인 제목 바꾸기"), ("o", f"{H1} feat: 로그인 버튼 추가"), ("o", f"{H0} feat: 로그인 화면 추가")],
         96, 536, 1260, 1024 - 536, lh=2.1)
tf += T.html()
xa, ya, wa, ha = T.line_box(1)
xb, yb, wb, hb = T.line_box(2)
tf.append(box(6, xa - 4, ya - 4, max(wa, wb) + 8, yb + hb - ya + 8, BL))
tf.append(label(1396, 536 + 40, 428, "merge 커밋 없이<br>한 줄로 이어졌어요", BL, 6, size=34))
tf.append(label(1396, 536 + 190, 428, "lee의 커밋 위에<br>내 커밋이 올라갔어요", SUB, 6, size=30, kind="fade"))
W("team-flow", tf, "팀원이 먼저 push했고 나는 고치던 중이면, stash, pull, pop 순서로 받고 나서 커밋해요. 오늘 팀 실습에서 그대로 쓰는 순서예요. 1번부터 3번이 stash, pull, pop이고, 4번과 5번은 늘 하던 add, commit, push예요. 고치던 걸 먼저 커밋하고 pull해도 돼요. 그러면 03에서 본 merge 커밋이 하나 생겨요. stash를 쓰면 팀원 커밋 위에 내 커밋이 올라가서 git log가 한 줄로 이어져요. 커밋할 만큼 끝났으면 커밋, 덜 끝났으면 stash라고 기억해요.")

co = [sec("st-co")] + head("팀에서 쓰기 · 급히 브랜치를 옮길 때", "checkout이 막혀도 stash로 치우고 가요", PUR)
T = Term([("$", "git checkout main"), ("r", "error: Your local changes to the following files would be overwritten by checkout:"), ("r", "\tlogin.md"),
          ("r", "Please commit your changes or stash them before you switch branches."), ("o", "Aborting")], 96, 210, 1728, 300)
co += T.html()
x, y, w_, h_ = T.line_box(3)
co.append(underline(1, x + 6, x + w_ - 6, round(y + h_ + 2), RED))
flow = [("git stash", "feature/login에서<br>고치던 걸 넣기", C_SH), ("git checkout main", "main으로 가서", MUTE), ("급한 일", "고치고 commit, push", MUTE),
        ("git checkout<br>feature/login", "돌아와서", MUTE), ("git stash pop", "꺼내서 이어서", C_SH)]
timeline(co, flow, 210 + T.h + 64, {0, 4}, order0=2, size=24)
co.append(label(96, 880, 1728, "서랍은 저장소에 하나예요. 꺼낼 때는 넣었던 브랜치로 돌아가서 pop해요.", SUB, 7, size=30, kind="fade"))
W("st-co", co, "브랜치를 옮길 때 checkout이 막혀도, stash로 치우고 갔다가 돌아와서 pop하면 돼요. 03에서 본 checkout 에러예요. 그때는 커밋하고 옮기라고 했어요. 덜 끝난 작업이면 stash로 치워도 돼요. 서랍은 저장소에 하나뿐이라 다른 브랜치에서도 같은 서랍이 보여요. 다른 브랜치에서 pop하면 그 브랜치에 얹혀서 헷갈려요. stash list의 on main, on feature/login 부분을 보고 넣었던 브랜치에서 꺼내요.")

# ======================================================================
# cheatsheet: when to use what, and what comes next
# ======================================================================
cs = [f'<section id="cheatsheet" data-transition="fade" style="background:{BG};color:{INK};font-family:{SANS};padding:96px;display:flex;flex-direction:column;word-break:keep-all">',
      f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>']
rows = [(C_RS, "고친 게 필요 없어요", "git restore 파일", "먼저 git diff. 되찾을 수 없어요"),
        (C_UN, "add를 취소하고 싶어요", "git restore --staged 파일", "고친 내용은 그대로예요"),
        (C_SH, "덜 끝났는데 pull, checkout", "git stash<br>git stash pop", "서랍은 내 컴퓨터에만 있어요"),
        (C_SH, "pop에서 충돌이 났어요", "파일 고치기<br>git add 파일<br>git stash drop", "서랍에 남아 있어요"),
        (BL, "커밋할 만큼 끝났어요", 'git add 파일<br>git commit -m "..."', "기록에 남아요")]
cs.append(hair(96, 196, 1728, INK))
y = 198
for c, sit, cmd, note in rows:
    hgt = 104 + 42 * (cmd.count("<br>"))
    cs.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:{hgt}px;display:flex;flex-direction:row;align-items:center;gap:32px;padding:0 10px">'
              + f'<div style="width:12px;height:{hgt - 40}px;flex:none;border-radius:6px;background:{c}"></div>'
              + p(f"width:520px;flex:none;font-size:32px;font-weight:700;color:{INK}", sit)
              + p(f"width:560px;flex:none;font-family:{MONO};font-size:28px;font-weight:700;line-height:1.5;color:{c}", cmd)
              + p(f"flex:1;font-size:28px;color:{SUB}", note) + '</div>')
    y += hgt
    cs.append(hair(96, y, 1728))
cs.append(p(f"position:absolute;left:96px;top:{y + 40}px;width:1728px;font-size:30px;font-weight:700;color:{INK}", "막히면 git status의 괄호 안 안내부터 읽어요. 08에서는 갈라진 기록을 합치는 여러 방법을 비교해요."))
W("cheatsheet", cs, "언제 무엇을 쓰는지 한 장으로 모았어요. 수업 끝에 이 장을 띄워 두고, 팀 레포에서 pull이 막힌 상황을 한 번 더 만들어 직접 풀어 보게 해요. 세 명령 모두 커밋하기 전의 변경만 다뤄요. 커밋한 뒤의 되돌리기는 02와 03의 reset, revert를 써요.")
print("ok")
