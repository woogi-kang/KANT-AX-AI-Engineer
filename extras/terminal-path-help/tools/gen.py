"""Generates every slide of the extra deck "터미널 환경에 적응하기" and slides/deck.json.

Story: the explorer window (Finder, Windows Explorer) and the terminal move in sync through
~/kant (hello-uv from 09, team-intro from 06). Then the same command run in the right and the
wrong folder, the check habit (pwd, ls, git status), the naming conventions behind -h, --help,
origin and main, and how to read help for ls, git and uv.
Terminal output comes from tools/demo.sh (real bash, git 2.43, uv 0.11.32).

Layout rules (Stageshow, see tools/DESIGN.md): one focal object per slide, terms labelled on the
picture with a leader line instead of side cards, hairline rows instead of bordered cards,
terminals sized to their lines. Highlights come from tools/highlight.py (tools/HIGHLIGHT.md).
Usage: python3 tools/gen.py slides
"""
import html, json, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "tools"))
from highlight import spot, spot_off, cursor, cursor_off, ring, box as pen_box, underline

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
BG, INK, SUB, LINE, CARD = "#F6F5F1", "#1D2330", "#4A5262", "#DCD8CE", "#FFFFFF"
BL, GR, OR, PUR, RED, GRAY = "#2459C9", "#1F8A4C", "#B26A00", "#5A3BB8", "#A33131", "#6A7180"
DIR = "#E0A84A"
T_BG, T_PROMPT, T_CMD, T_OUT, T_ERR, T_OK, T_DIM = "#1B2029", "#8FB3FF", "#F2C46D", "#D8DEE9", "#FF9C94", "#7FD18B", "#8A93A3"
SH_HERO = "0 24px 60px rgba(29,35,48,.14)"
SH_SAT = "0 14px 36px rgba(29,35,48,.32)"
L = 96          # side gutter
CW = 0.6        # JetBrains Mono advance width per em


def e(s):
    return html.escape(s, quote=False)


def p(style, text, attrs=""):
    return f'<p{attrs} style="{style}">{text}</p>'


def bi(kind, order):
    return f' data-build-in="{kind} order {order}"' if order else ""


ORDER, SECTIONS = [], {}


def W(sid, parts, notes, section=None):
    if section:
        SECTIONS[section[0]] = {"description": section[1], "start": sid}
    if sid not in ORDER:
        ORDER.append(sid)
    with open(os.path.join(OUT, sid + ".html"), "w") as f:
        f.write("\n".join(parts) + f"\n<aside>{e(notes)}</aside>\n</section>\n")


def sec(sid, transition="fade"):
    return (f'<section id="{sid}" data-transition="{transition}" style="background:{BG};color:{INK};font-family:{SANS};'
            f'font-variant-ligatures:none;word-break:keep-all;padding:96px;display:flex;flex-direction:column">')


def head(eyebrow, title, color):
    return [p(f"position:absolute;left:{L}px;top:44px;width:1728px;font-size:26px;font-weight:700;color:{color}", e(eyebrow), ' id="eyebrow"'),
            f'<h2 id="title" style="position:absolute;left:{L}px;top:92px;width:1728px;font-size:56px;font-weight:700;line-height:1.2;color:{INK}">{title}</h2>']


def caption(text, top=956, order=None):
    return p(f"position:absolute;left:{L}px;top:{top}px;width:1728px;font-size:32px;font-weight:700;line-height:1.4;color:{INK}", text, ' id="caption"' + bi("rise", order))


def lab(x, y, text, color=INK, size=28, order=None, w=None, weight=700, align="left", mono=False, kind="fade", lid=None, extra=""):
    wd = f"width:{w}px;" if w else "white-space:nowrap;"
    fam = f"font-family:{MONO};" if mono else ""
    i = f' id="{lid}"' if lid else ""
    return p(f"position:absolute;left:{x}px;top:{y}px;{wd}{fam}font-size:{size}px;font-weight:{weight};line-height:1.35;color:{color};text-align:{align};{extra}", text, i + bi(kind, order))


def lead(x1, y1, x2, y2, color=SUB, order=None, dot=True, width=3):
    """A thin leader line from a label (x1, y1) to the thing it explains (x2, y2), ending in a dot."""
    d = f'<circle cx="{x2}" cy="{y2}" r="7" fill="{color}" stroke="none"/>' if dot else ""
    return (f'<svg{bi("draw", order)} viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible">'
            f'<g fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"><path d="M{x1},{y1} L{x2},{y2}"/></g>{d}</svg>')


def path_svg(d, color, order=None, width=5, arrow=True, dashed=False):
    mk = (f'<defs><marker id="ah{abs(hash(d)) % 99999}" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
          f'<path d="M0,0 L10,5 L0,10 z" fill="{color}"/></marker></defs>') if arrow else ""
    me = f' marker-end="url(#ah{abs(hash(d)) % 99999})"' if arrow else ""
    da = ' stroke-dasharray="14 12"' if dashed else ""
    return (f'<svg{bi("draw", order)} viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible">'
            f'{mk}<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round"{da}{me}/></svg>')


def code(text, color=INK, size=28, bg="#ECEAE3"):
    return f'<span style="font-family:{MONO};font-size:{size}px;font-weight:700;color:{color};background:{bg};border-radius:8px;padding:2px 12px;white-space:nowrap">{e(text)}</span>'


def hair(x, y, w, color=LINE, order=None, h=2):
    return f'<div{bi("fade", order)} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{color}"></div>'


# ---------- terminal (sized to its lines) ----------
def lh(size):
    return round(size * 1.5)


TB, TP = 44, 24  # title bar height, top/bottom padding


def ty(top, i, size):
    """Top of line i inside a terminal placed at `top`."""
    return top + TP + TB + i * lh(size)


def tx(left, col, size, pad=32):
    return left + pad + col * size * CW


def theight(n, size):
    return TP + TB + n * lh(size) + TP


def tline(l, size):
    kind = l[0]
    st = f"height:{lh(size)}px;font-size:{size}px;line-height:{lh(size)}px;white-space:pre;"
    if kind == "$":
        return p(st + f"color:{T_CMD}", f'<span style="color:{T_PROMPT}">{e(l[1])} $</span> {e(l[2])}')
    if kind == "r":
        return p(st + f"color:{T_OUT}", l[1])
    if kind == "m":
        return p(st + f"color:{T_CMD};font-weight:700;background:rgba(242,196,109,.14);margin:0 -14px;padding:0 14px", e(l[1].replace("\t", "    ")))
    col = {"o": T_OUT, "e": T_ERR, "g": T_OK, "d": T_DIM, "y": T_CMD}[kind]
    t = l[1].replace("\t", "    ")
    return p(st + f"color:{col}", e(t) if t else "&#160;")


def term(lines, left, top, w, size=28, tid="term", attrs="", title=None, h=None, shadow=None, extra=""):
    hh = h or theight(len(lines), size)
    sh = f"box-shadow:{shadow};" if shadow else ""
    o = [f'<div id="{tid}"{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{hh}px;background:{T_BG};border-radius:18px;'
         f'padding:{TP}px 32px;display:flex;flex-direction:column;font-family:{MONO};overflow:hidden;{sh}{extra}">',
         f'<div style="height:{TB}px;flex:none;display:flex;flex-direction:row;gap:10px;align-items:flex-start">'
         '<div style="width:16px;height:16px;border-radius:8px;background:#F28B82"></div><div style="width:16px;height:16px;border-radius:8px;background:#F2C46D"></div><div style="width:16px;height:16px;border-radius:8px;background:#7FD18B"></div>'
         + (p(f"margin:-4px 0 0 14px;font-family:{SANS};font-size:20px;font-weight:700;line-height:1.2;color:{T_DIM}", e(title)) if title else "") + '</div>']
    o += [tline(l, size) for l in lines]
    o.append('</div>')
    return "".join(o)


def cmdcol(prompt):
    return len(prompt) + 3


# ---------- explorer window (Finder / Windows Explorer, simplified) ----------
def folder_glyph(w=84, h=64):
    return (f'<div style="position:relative;width:{w}px;height:{h}px;flex:none">'
            f'<div style="position:absolute;left:0;top:0;width:{w * 0.45:.0f}px;height:16px;background:{DIR};border-radius:6px 6px 0 0"></div>'
            f'<div style="position:absolute;left:0;top:10px;width:{w}px;height:{h - 10}px;background:{DIR};border-radius:8px"></div></div>')


def file_glyph(w=56, h=70):
    return f'<div style="width:{w}px;height:{h}px;flex:none;background:#FFFFFF;border:3px solid #B4B9C3;border-radius:6px 18px 6px 6px"></div>'


BTNS = [("back", "←"), ("fwd", "→"), ("up", "↑"), ("home", "⌂")]
EX_X, EX_Y, EX_W, EX_H = 96, 200, 1180, 520
EX_BAR = 88


def explorer(path, items, left=EX_X, top=EX_Y, w=EX_W, h=EX_H, press=None, fid="finder"):
    o = [f'<div id="{fid}" style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:{CARD};border-radius:20px;'
         f'box-shadow:{SH_HERO};display:flex;flex-direction:column;overflow:hidden">']
    bar = [f'<div style="height:{EX_BAR}px;flex:none;background:#ECEAE3;display:flex;flex-direction:row;align-items:center;gap:12px;padding:0 22px">']
    for k, g in BTNS:
        on = press == k
        bar.append(p(f"width:60px;height:52px;flex:none;border-radius:12px;font-size:30px;font-weight:700;line-height:52px;text-align:center;"
                     f"color:{'#FFFFFF' if on else SUB};background:{OR if on else '#FFFFFF'}", g, f' id="btn-{k}"'))
    crumbs = f' <span style="color:{GRAY}">›</span> '.join(e(c) for c in path)
    bar.append(f'<div id="crumbs" style="flex:1;margin-left:12px;height:52px;background:#FFFFFF;border-radius:12px;padding:0 20px;display:flex;align-items:center">'
               + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{INK};white-space:nowrap", crumbs) + '</div>')
    bar.append('</div>')
    o += bar
    o.append('<div style="flex:1;display:flex;flex-direction:row;flex-wrap:wrap;align-content:flex-start;gap:20px 8px;padding:40px 32px">')
    for name in items:
        is_dir = "." not in name
        o.append(f'<div id="it-{name.replace(".", "-")}" style="width:232px;height:150px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px">'
                 + (folder_glyph() if is_dir else file_glyph())
                 + p(f"font-size:26px;font-weight:700;color:{INK};white-space:nowrap", e(name)) + '</div>')
    o.append('</div></div>')
    return "".join(o)


# ---------- real output (tools/demo.sh) ----------
OUT_LS = {"kim": "Desktop  Documents  kant", "kant": "hello-uv  team-intro", "hello": "README.md  main.py  pyproject.toml"}
GIT_FATAL = "fatal: not a git repository (or any of the parent directories): .git"
UV_FAIL = ["error: Failed to spawn: `main.py`", "  Caused by: No such file or directory (os error 2)"]
STATUS_CLEAN = ["On branch main", "Your branch is up to date with 'origin/main'.", "", "nothing to commit, working tree clean"]
STATUS_KIM = ["On branch main", "Your branch is up to date with 'origin/main'.", "", "Untracked files:",
              '  (use "git add <file>..." to include in what will be committed)', "\tkim.md", "",
              'nothing added to commit but untracked files present (use "git add" to track)']

# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px;overflow:hidden">',
       '<p style="font-size:28px;font-weight:700;color:#F2B27A;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 번외</p>',
       '<h1 style="font-size:100px;font-weight:900;line-height:1.15;color:#F6F5F1">터미널 환경에<br>적응하기</h1>',
       '<p style="font-size:40px;line-height:1.4;color:#BFC6D4">지금 위치를 확인하는 습관과<br>-h, --help로 도움 받기</p>']
cov.append(term([("$", "~/kant", "pwd"), ("o", "/home/kim/kant"), ("$", "~/kant", "ls"), ("o", OUT_LS["kant"]), ("$", "~/kant", "uv --help"), ("o", "An extremely fast Python package manager."), ("d", "")],
                1080, 300, 1000, size=30, tid="cov-term", extra="background:#262D3A"))
W("cover", cov, "터미널이 낯선 분을 위한 번외 자료예요. 수업에서 자주 나온 두 가지를 모았어요. 첫째, 터미널에서 지금 위치를 왜 계속 확인해야 하는지예요. 둘째, 명령을 잊었을 때 -h와 --help로 스스로 찾는 법이에요. 01 터미널 기초를 본 뒤라면 언제 봐도 돼요. git 장면은 02와 06, uv 장면은 09에서 만든 폴더를 그대로 써요.", ("intro", "들어가기"))

ORDER.append("toc")   # written last, after page numbers are known

# ---------- why: the explorer shows, the terminal has to be asked ----------
o = [sec("why")] + head("들어가기", "탐색기는 그림으로, 터미널은 글자로 위치를 알려 줘요", INK)
o.append(explorer(["kim", "kant"], ["hello-uv", "team-intro"]))
WT_X, WT_S = 960, 34
wl = [("$", "~/kant", "pwd"), ("o", "/home/kim/kant"), ("$", "~/kant", "ls"), ("o", OUT_LS["kant"])]
WT_Y = 976 - theight(len(wl), WT_S)
o.append(term(wl, WT_X, WT_Y, 864, size=WT_S, tid="why-term", shadow=SH_SAT, title="터미널"))
o.append(underline(1, int(tx(WT_X, 0, WT_S)), int(tx(WT_X, 6, WT_S)), ty(WT_Y, 0, WT_S) + lh(WT_S) - 4, OR))
o.append(lab(WT_X, WT_Y - 52, "$ 앞의 ~/kant가 지금 위치예요", OR, 30, order=1))
o.append(lead(1500, ty(WT_Y, 1, WT_S) + lh(WT_S) // 2, int(tx(WT_X, 14, WT_S)) + 16, ty(WT_Y, 1, WT_S) + lh(WT_S) // 2, BL, order=2))
o.append(lab(1512, ty(WT_Y, 1, WT_S) + 2, "pwd = 주소 줄", BL, 30, order=2))
o.append(lead(1500, ty(WT_Y, 3, WT_S) + lh(WT_S) // 2, int(tx(WT_X, 20, WT_S)) + 16, ty(WT_Y, 3, WT_S) + lh(WT_S) // 2, BL, order=3))
o.append(lab(1512, ty(WT_Y, 3, WT_S) + 2, "ls = 창 안", BL, 30, order=3))
o.append(lab(L, EX_Y + EX_H + 60, "둘 다 kant 폴더 안이에요.<br>터미널은 물어봐야 알려 줘요.", INK, 34, w=820, lid="caption"))
W("why", o, "탐색기와 터미널은 같은 kant 폴더 안에 있어요. 왼쪽 탐색기(Mac은 Finder, Windows는 파일 탐색기)는 열린 폴더와 안에 든 것을 그림으로 보여 줘요. 터미널은 그림이 없어서 프롬프트, pwd, ls로 물어봐야 해요. 첫 클릭에 프롬프트의 ~/kant, 둘째 클릭에 pwd 결과를 짚어요. 이번 자료의 첫 부분은 탐색기에서 하던 일을 터미널 명령과 하나씩 맞춰 보는 거예요. 탐색기 그림은 Mac과 Windows를 단순하게 섞어 그렸어요.")

# ---------- part 1: explorer and terminal in sync ----------
EB1 = "1. 탐색기와 터미널 맞춰 보기"
SYNC = [
    ("sync0", "터미널을 열면 홈 폴더에서 시작해요", ["kim"], "kim", None,
     [("$", "~", "pwd"), ("o", "/home/kim"), ("$", "~", "ls"), ("o", OUT_LS["kim"])], 0, None,
     "탐색기에서 홈 폴더 창을 연 것과 같아요.",
     "터미널을 열면 홈 폴더에서 시작해요. 탐색기로 치면 홈 폴더 창을 연 상태예요. 탐색기 창의 Desktop, Documents, kant가 ls 결과와 똑같아요. 슬라이드는 Linux 기준이라 /home/kim이에요. Mac은 /Users/내이름, Windows Git Bash는 /c/Users/내이름이에요."),
    ("sync1", "폴더 더블클릭은 cd kant예요", ["kim", "kant"], "kant", None,
     [("$", "~", "pwd"), ("o", "/home/kim"), ("$", "~", "cd kant"), ("$", "~/kant", "ls"), ("o", OUT_LS["kant"])], 2, "더블클릭",
     "프롬프트가 ~에서 ~/kant로 바뀌었어요. 주소 줄도 같이 바뀌었어요.",
     "탐색기에서 kant 폴더를 더블클릭하면 창이 kant 안으로 바뀌어요. 터미널에서는 cd kant가 같은 일을 해요. 프롬프트 앞부분이 ~에서 ~/kant로 바뀐 것을 짚어 주세요. ls 결과 hello-uv, team-intro는 탐색기 창에 보이는 두 폴더와 같아요."),
    ("sync2", "한 칸 더 들어가기도 cd예요", ["kim", "kant", "hello-uv"], "hello", None,
     [("$", "~", "cd kant"), ("$", "~/kant", "ls"), ("o", OUT_LS["kant"]), ("$", "~/kant", "cd hello-uv"), ("$", "~/kant/hello-uv", "ls"), ("o", OUT_LS["hello"])], 3, "더블클릭",
     "주소 줄 kim › kant › hello-uv는 /home/kim/kant/hello-uv와 같은 길이에요.",
     "hello-uv는 09에서 uv init으로 만든 폴더예요. 탐색기 주소 줄의 kim › kant › hello-uv와 터미널의 ~/kant/hello-uv는 같은 길을 다르게 적었을 뿐이에요. 점으로 시작하는 .venv, .gitignore는 탐색기도 ls도 기본으로 숨겨요. 01에서 본 ls -a로 보여요."),
    ("sync3", "위 폴더(↑)는 cd ..이에요", ["kim", "kant"], "kant", "up",
     [("$", "~/kant", "cd hello-uv"), ("$", "~/kant/hello-uv", "ls"), ("o", OUT_LS["hello"]), ("$", "~/kant/hello-uv", "cd .."), ("$", "~/kant", "pwd"), ("o", "/home/kim/kant")], 3, None,
     "..은 한 칸 위 폴더예요. 01에서 본 기호예요.",
     "Windows 탐색기의 위쪽 화살표, Mac Finder의 Cmd+↑가 cd ..과 같아요. hello-uv에서 한 칸 위 폴더인 kant로 올라갔어요. 주소 줄에서 hello-uv가 빠진 것을 보여 주세요."),
    ("sync4", "뒤로(←)는 cd -예요", ["kim", "kant", "hello-uv"], "hello", "back",
     [("$", "~/kant/hello-uv", "cd .."), ("$", "~/kant", "pwd"), ("o", "/home/kim/kant"), ("$", "~/kant", "cd -"), ("o", "/home/kim/kant/hello-uv")], 3, None,
     "cd -는 바로 전 폴더로 돌아가고, 간 곳을 한 줄 알려 줘요.",
     "cd -는 바로 전에 있던 폴더로 돌아가요. 탐색기의 뒤로 버튼과 같아요. cd 뒤에 빼기 기호 하나를 쳐요. cd -는 돌아간 곳의 전체 경로를 한 줄 출력해요. 위로(..)와 뒤로(-)는 달라요. 위로는 폴더 지도에서 한 칸 위, 뒤로는 내가 방금 있던 곳이에요. 출력은 tools/demo.sh에서 실제로 실행한 결과예요."),
    ("sync5", "앞으로(→)는 cd -를 한 번 더 쳐요", ["kim", "kant"], "kant", "fwd",
     [("$", "~/kant", "cd -"), ("o", "/home/kim/kant/hello-uv"), ("$", "~/kant/hello-uv", "cd -"), ("o", "/home/kim/kant")], 2, None,
     "cd -는 바로 전 한 곳만 기억해요. 다시 치면 두 폴더를 오가요.",
     "터미널에는 앞으로 버튼이 따로 없어요. 탐색기는 뒤로와 앞으로를 여러 번 기억하지만, 터미널의 cd -는 바로 전 한 곳만 기억해요. 그래서 cd -를 계속 치면 두 폴더 사이를 왔다 갔다 해요. 두 폴더를 번갈아 가며 작업할 때 편해요."),
    ("sync6", "홈(⌂)은 cd ~예요", ["kim"], "kim", "home",
     [("$", "~/kant", "cd -"), ("o", "/home/kim/kant"), ("$", "~/kant", "cd ~"), ("$", "~", "pwd"), ("o", "/home/kim")], 2, None,
     "어디에 있든 cd ~ 한 번이면 홈 폴더로 돌아와요.",
     "어디에 있든 cd ~ 한 번이면 홈 폴더로 돌아와요. Mac Finder 사이드바의 홈, Windows 탐색기 주소 줄의 사용자 이름 폴더가 cd ~와 같아요. 01에서 배운 명령이에요. 길을 잃으면 cd ~로 홈에 돌아온 뒤 다시 cd로 들어가요."),
]
ST_X, ST_S = 960, 32
for i, (sid, title, path, here, press, lines, row, pick, cap, notes) in enumerate(SYNC):
    o = [sec(sid, "magic" if i else "fade")] + head(EB1, e(title), BL)
    o.append(explorer(path, OUT_LS[here].split("  "), press=press))
    th = theight(len(lines), ST_S)
    st_y = 976 - th
    o.append(term(lines, ST_X, st_y, 864, size=ST_S, tid="term", shadow=SH_SAT, title="터미널"))
    if row:
        prompt, cmd = lines[row][1], lines[row][2]
        c0 = cmdcol(prompt)
        x1, x2 = int(tx(ST_X, c0, ST_S)), int(tx(ST_X, c0 + len(cmd), ST_S))
        yline = ty(st_y, row, ST_S) + lh(ST_S) - 6
        if press:
            o.append(cursor(1, target=f"btn-{press}"))
            hint = {"up": "↑ 위 폴더", "back": "← 뒤로", "fwd": "→ 앞으로", "home": "⌂ 홈"}[press]
        else:
            o.append(spot(1, target="crumbs", pad=10, r=14, dim=0.45))
            hint = "주소 줄"
        o.append(underline(2, x1, x2, yline, OR))
        o.append(lab(x1, st_y - 52, f"{hint} = {e(cmd)}", OR, 30, order=2, mono=False, lid="pair"))
        o.append(cursor_off(2) if press else spot_off(2))
    o.append(lab(L, EX_Y + EX_H + 60, e(cap), INK, 34, w=820, lid="caption"))
    W(sid, o, notes, ("sync", "탐색기와 터미널 맞춰 보기") if i == 0 else None)

# ---------- match: the folder tree with every move drawn on it ----------
o = [sec("match")] + head(EB1, "탐색기 버튼과 cd를 폴더 지도 한 장에 모아요", BL)
NODES = {"kim": (230, 300, "kim/", "~ 홈 폴더"), "kant": (530, 520, "kant/", ""), "hello": (330, 780, "hello-uv/", ""), "team": (800, 780, "team-intro/", "")}


def node(k, hl=False):
    x, y, lab_, note = NODES[k]
    bd = f"border:3px solid {BL};" if hl else f"border:3px solid {DIR};"
    return (f'<div id="nd-{k}" style="position:absolute;left:{x}px;top:{y}px;height:76px;background:#FDF1DC;{bd}border-radius:14px;padding:0 22px;display:flex;flex-direction:row;gap:14px;align-items:center">'
            f'<div style="width:34px;height:26px;background:{DIR};border-radius:5px"></div>'
            + p(f"font-family:{MONO};font-size:32px;font-weight:700;white-space:nowrap;color:#5C3A00", e(lab_)) + '</div>'
            + (lab(x, y - 46, note, GRAY, 24) if note else ""))


# tree lines
o.append(path_svg("M300,376 L300,558 L524,558", "#CFCABF", arrow=False, width=4))
o.append(path_svg("M600,596 L600,690 L410,690 L410,776", "#CFCABF", arrow=False, width=4))
o.append(path_svg("M600,690 L900,690 L900,776", "#CFCABF", arrow=False, width=4))
for k in NODES:
    o.append(node(k))
# moves
o.append(path_svg("M760,540 C900,520 900,700 960,760", GR, order=1))
o.append(lab(910, 560, "cd 폴더이름", GR, 32, order=1, mono=True))
o.append(lab(910, 606, "폴더 더블클릭", SUB, 26, order=1))
o.append(path_svg("M420,770 C330,700 360,600 510,575", OR, order=2))
o.append(lab(140, 640, "cd ..", OR, 32, order=2, mono=True))
o.append(lab(140, 686, "↑ 위 폴더", SUB, 26, order=2))
o.append(path_svg("M640,512 C640,380 560,330 420,330", BL, order=3))
o.append(lab(660, 380, "cd ~", BL, 32, order=3, mono=True))
o.append(lab(660, 426, "⌂ 홈", SUB, 26, order=3))
o.append(path_svg("M520,860 C600,940 760,940 840,860", PUR, order=4, dashed=True))
o.append(path_svg("M840,860 C760,940 600,940 520,860", PUR, order=4, dashed=True, arrow=True))
o.append(lab(590, 936, "cd -  ← 뒤로 · → 앞으로", PUR, 30, order=4))
# right column: pwd and ls as the two "look" commands
o.append(hair(1180, 300, 4, LINE, h=620))
o.append(lab(1260, 300, "보는 명령", GRAY, 26))
o.append(lab(1260, 360, "pwd", INK, 44, mono=True))
o.append(lab(1260, 420, "주소 줄 · 지금 위치 전체", SUB, 28))
o.append(lab(1260, 520, "ls", INK, 44, mono=True))
o.append(lab(1260, 580, "창 안 · 이 폴더에 든 것", SUB, 28))
o.append(lab(1260, 700, "터미널은 창이 없어서<br>옮길 때마다 이 둘로 확인해요", INK, 30, w=560))
W("match", o, "앞 장면을 폴더 지도 한 장에 모았어요. 탐색기 버튼마다 같은 일을 하는 cd가 있어요. 초록은 들어가기, 주황은 한 칸 위로, 파랑은 홈으로, 보라 점선은 바로 전 폴더와 오가는 cd -예요. 위로와 뒤로를 헷갈리기 쉬워요. 위로는 지도에서 한 칸 위, 뒤로는 방금 있던 곳이에요. 탐색기는 창이 늘 열려 있어서 안이 보이지만, 터미널은 ls를 쳐야 보여요. 주소 줄에 해당하는 것이 pwd예요.")

# ---------- open: explorer and terminal in the same folder ----------
o = [sec("open")] + head(EB1, "탐색기와 터미널을 같은 폴더에서 열어요", BL)
OT_Y = 230
o.append(lab(L, OT_Y - 8, "터미널에서 지금 폴더를 탐색기로", GRAY, 28))
o.append(term([("$", "~/kant", "open .")], L, OT_Y + 44, 860, size=40, tid="open-mac", title="Mac"))
o.append(term([("$", "~/kant", "explorer .")], 964, OT_Y + 44, 860, size=40, tid="open-win", title="Windows Git Bash"))
o.append(ring(1, int(tx(L, 14, 40)) - 2, ty(OT_Y + 44, 0, 40) + 8, int(40 * CW) + 4, lh(40) - 16, OR, 5))
o.append(ring(1, int(tx(964, 18, 40)) - 2, ty(OT_Y + 44, 0, 40) + 8, int(40 * CW) + 4, lh(40) - 16, OR, 5))
o.append(lab(int(tx(L, 14, 40)) + 60, OT_Y + 44 + theight(1, 40) + 16, "점(.)은 지금 폴더예요", OR, 28, order=1))
rows = [("탐색기에서 터미널로", "Mac", "폴더 오른쪽 클릭 › 서비스 › 폴더에서 새로운 터미널 열기"),
        ("", "Windows", "폴더 빈 곳 오른쪽 클릭 › Open Git Bash here"),
        ("VS Code에서", "Windows / Mac", "폴더를 열고 Ctrl+` / control+` · 그 폴더에서 터미널이 시작돼요")]
ry = 520
for i, (a_, b_, c_) in enumerate(rows):
    y = ry + i * 96
    o.append(hair(L, y, 1728))
    if a_:
        o.append(lab(L, y + 26, a_, INK, 30, order=2 + (i > 1)))
    o.append(lab(560, y + 28, b_, GRAY, 26, order=2 + (i > 1)))
    o.append(lab(820, y + 26, e(c_), INK, 28, order=2 + (i > 1)))
o.append(hair(L, ry + 3 * 96, 1728))
o.append(caption("둘을 나란히 띄우고, 터미널에서 만든 파일이 탐색기에 생기는지 봐요.", 880))
W("open", o, "탐색기와 터미널을 같은 폴더에 띄워 두면 위치를 덜 헷갈려요. open .은 Mac에서, explorer .은 Windows Git Bash에서 지금 폴더를 탐색기 창으로 열어요. 점은 01에서 배운 지금 폴더예요. 반대로 탐색기에서 보던 폴더에서 터미널을 바로 열 수도 있어요. Mac은 Finder에서 폴더를 오른쪽 클릭하고 서비스 메뉴를 봐요. 메뉴가 없으면 시스템 설정의 키보드 단축키에서 켜요. Windows는 Git을 설치할 때 Open Git Bash here 메뉴가 같이 생겨요. Windows 11은 추가 옵션 표시를 먼저 눌러요. VS Code의 백틱(`)은 숫자 1 왼쪽 키예요. 이 명령들은 출력이 없고 창만 열려요.")

# ---------- part 2: the folder decides what a command does ----------
EB2 = "2. 위치가 맞아야 명령이 동작해요"


def pair(ll, rl, ltitle, rtitle, size=30, top=260, lcolor=RED, rcolor=GR):
    """Two terminals at one height: the same command, one thing different (Stageshow teaching pair)."""
    h = theight(max(len(ll), len(rl)), size)
    return [lab(L, top - 52, ltitle, lcolor, 30),
            term(ll, L, top, 840, size=size, tid="t-left", h=h),
            lab(984, top - 52, rtitle, rcolor, 30, order=1),
            term(rl, 984, top, 840, size=size, tid="t-right", attrs=bi("rise", 1), h=h)], h


o = [sec("same-uv")] + head(EB2, "같은 uv run main.py도 폴더에 따라 결과가 달라요", GR)
ll = [("$", "~/kant", "ls"), ("o", OUT_LS["kant"]), ("$", "~/kant", "uv run main.py"), ("e", UV_FAIL[0]), ("e", "  Caused by: No such file or"), ("e", "  directory (os error 2)")]
rl = [("$", "~/kant/hello-uv", "ls"), ("o", "README.md  main.py"), ("o", "pyproject.toml"), ("$", "~/kant/hello-uv", "uv run main.py"), ("g", "Hello from hello-uv!")]
parts, h = pair(ll, rl, "kant에서 · main.py가 없어요", "hello-uv에서 · main.py가 있어요")
o += parts
o.append(ring(2, int(tx(L, 0, 30)), ty(260, 1, 30) + 4, int(20 * 30 * CW), lh(30) - 8, RED))
o.append(ring(3, int(tx(984, 0, 30)), ty(260, 1, 30) + 4, int(18 * 30 * CW), lh(30) - 8, GR))
o.append(lab(L, 260 + h + 40, "명령 뒤의 파일 이름은 지금 폴더에서 찾아요.", INK, 34, order=2, w=1728))
o.append(lab(L, 260 + h + 96, "No such file or directory가 보이면 명령을 고치기 전에 pwd와 ls부터 쳐요.", SUB, 30, order=3, w=1728))
W("same-uv", o, "같은 명령인데, 서 있는 폴더가 달라서 결과가 달라요. kant에는 main.py가 없어서 uv가 Failed to spawn, No such file or directory를 보여 줘요. hello-uv로 들어가서 치면 09에서 본 Hello from hello-uv!가 나와요. 두 터미널의 ls 결과에서 main.py가 있는지부터 비교해 보여 주세요. 화면 폭 때문에 긴 줄은 나눠 적었어요. 출력은 tools/demo.sh에서 실제로 실행한 결과예요.", ("cwd", "위치가 맞아야 명령이 동작해요"))

o = [sec("same-git")] + head(EB2, "git status도 저장소 폴더 안에서만 동작해요", GR)
GL = [("$", "~/kant", "git status"), ("e", "fatal: not a git repository"), ("e", "(or any of the parent directories): .git")]
o.append(term(GL, L, 210, 1000, size=30, tid="t-left"))
o.append(underline(1, int(tx(L, 4, 30)), int(tx(L, 33, 30)), ty(210, 2, 30) + lh(30) - 6, OR))
gy = 210 + theight(3, 30) + 70
o.append(lab(L, gy, "git이 .git 폴더를 찾아 위로 올라가는 길", INK, 30, order=1))
climb = ["kant/", "kim/", "home/", "/"]
for i, f_ in enumerate(climb):
    x = L + i * 250
    o.append(f'<div{bi("rise", i + 1)} style="position:absolute;left:{x}px;top:{gy + 70}px;width:200px;height:84px;background:#FDF1DC;border:3px solid {DIR};border-radius:14px;display:flex;align-items:center;justify-content:center">'
             + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:#5C3A00", e(f_)) + '</div>')
    o.append(lab(x, gy + 172, ".git 없음", RED, 26, order=i + 1, w=200, align="center"))
    if i < 3:
        o.append(path_svg(f"M{x + 208},{gy + 112} L{x + 240},{gy + 112}", "#9AA0AC", order=i + 2, width=4))
o.append(lab(L, gy + 236, "parent directories는 이 위 폴더들이에요. 끝까지 없으면 fatal이 나요.", SUB, 28, order=4, w=1000))
RG = [("$", "~/kant/team-intro", "ls -a"), ("o", ".  ..  .git  README.md"), ("$", "~/kant/team-intro", "git status")] + [("o", l) for l in STATUS_CLEAN[:1]]
o.append(lab(1150, 210 - 6, "team-intro에서", GR, 30, order=5))
o.append(term([("$", "~/kant/team-intro", "git status"), ("o", "On branch main"), ("o", "nothing to commit,"), ("o", "working tree clean")], 1150, 260, 674, size=28, tid="t-right", attrs=bi("rise", 5), shadow=SH_SAT))
o.append(lab(1150, 260 + theight(4, 28) + 30, "06에서 clone한 폴더 안에는<br>숨김 폴더 .git이 있어요.", INK, 30, order=5, w=674))
W("same-git", o, "git은 지금 폴더에서 .git이라는 숨김 폴더를 찾고, 없으면 한 칸씩 위로 올라가며 찾아요. 맨 위 / 까지 가도 없으면 not a git repository (or any of the parent directories)라고 말해요. 화면 폭 때문에 에러를 두 줄로, team-intro의 마지막 줄도 두 줄로 나눠 적었어요. team-intro는 06에서 clone해서 .git이 있어요. 그래서 team-intro 안이나 그 아래 폴더에서 git status가 동작해요. 에러가 나면 cd로 저장소 폴더에 들어가요. 출력은 tools/demo.sh에서 실제로 실행한 결과예요.")

o = [sec("wrong-init")] + head(EB2, "홈 폴더에서 git init을 치면 홈 전체가 저장소가 돼요", RED)
IL = [("$", "~", "pwd"), ("o", "/home/kim"), ("$", "~", "git init"), ("o", "Initialized empty Git repository in /home/kim/.git/"),
      ("$", "~", "git status"), ("o", "On branch main"), ("o", ""), ("o", "No commits yet"), ("o", ""), ("o", "Untracked files:"),
      ("o", '  (use "git add <file>..." to include in what will be committed)'), ("e", "\t.gitconfig"), ("e", "\tDesktop/"), ("e", "\tDocuments/"), ("e", "\tkant/")]
IS = 25
o.append(term(IL, L, 200, 1180, size=IS, tid="t-init"))
o.append(ring(1, int(tx(L, 36, IS)), ty(200, 3, IS) + 2, int(15 * IS * CW), lh(IS) - 4, RED))
o.append(lead(1340, ty(200, 3, IS) + lh(IS) // 2, int(tx(L, 51, IS)) + 34, ty(200, 3, IS) + lh(IS) // 2, RED, order=1))
o.append(lab(1352, ty(200, 3, IS) - 18, ".git이 홈 폴더에<br>생겼어요", RED, 32, order=1, w=480))
o.append(pen_box(2, int(tx(L, 0, IS)) - 10, ty(200, 11, IS) - 4, 300, lh(IS) * 4 + 8, RED))
o.append(lead(1340, ty(200, 12, IS) + 20, int(tx(L, 0, IS)) + 300, ty(200, 12, IS) + 20, RED, order=2))
o.append(lab(1352, ty(200, 11, IS) - 6, "Desktop, Documents까지<br>모두 git이 지켜봐요", RED, 32, order=2, w=480))
o.append(caption("홈 폴더 프롬프트에 (main)이 보이거나 VS Code에 바뀐 파일이 수천 개 뜨면 의심해요.", 920, order=3))
W("wrong-init", o, "실수로 홈 폴더에서 git init을 치면 홈 폴더 전체가 저장소가 돼요. 02에서 git init은 프로젝트 폴더 안에서 쳤어요. git status를 치면 Desktop, Documents까지 모두 Untracked로 나와요. 그 아래 모든 폴더에서 git status가 동작해서, 저장소가 아닌 폴더인데도 에러가 안 나요. Windows Git Bash는 저장소 안이면 프롬프트에 (main)을 붙여서 홈 폴더에 (main)이 보이면 이 경우예요. 다음 장에서 되돌려요. 출력은 tools/demo.sh가 만든 연습용 홈 폴더에서 실제로 실행한 결과라 목록이 짧아요. 실제 컴퓨터에서는 훨씬 길어요.")

o = [sec("init-fix")] + head(EB2, "홈 폴더의 .git만 지우면 돌아와요", RED)
FS = 36
FL = [("$", "~", "pwd"), ("o", "/home/kim"), ("$", "~", "ls -a"), ("o", ".  ..  .git  .gitconfig  Desktop  Documents  kant"),
      ("$", "~", "rm -rf .git"), ("$", "~", "git status"), ("e", "fatal: not a git repository"), ("e", "(or any of the parent directories): .git")]
FX0, FY0 = 200, 220
o.append(term(FL, FX0, FY0, 1140, size=FS, tid="t-fix"))
steps = [(0, 2, "홈 폴더인지 먼저 확인해요"), (2, 2, "숨김 폴더 .git이 보여요"), (4, 1, "홈 폴더의 .git 하나만 지워요"), (5, 3, "이제 홈 폴더는 저장소가 아니에요")]
for i, (r0, n, d) in enumerate(steps):
    yc = ty(FY0, r0, FS)
    o.append(f'<p style="position:absolute;left:{L + 40}px;top:{yc + 5}px;width:44px;height:44px;border-radius:50%;background:{RED};color:#FFFFFF;font-size:26px;font-weight:900;line-height:44px;text-align:center">{i + 1}</p>')
    o.append(lab(1376, yc + 8, e(d), INK, 30, order=i + 1, w=448))
    o.append(spot(i + 1, int(tx(FX0, 0, FS)) - 14, yc, 1140 - 36, lh(FS) * n, pad=8, r=10, dim=0.5))
o.append(spot_off(5))
o.append(caption("rm -rf 뒤에는 꼭 .git만 적어요. 점 하나라도 빠지면 다른 것이 지워져요.", 880, order=5))
W("init-fix", o, "홈 폴더를 저장소로 만든 것은 .git 폴더 하나라서, 그 폴더만 지우면 원래대로 돌아와요. 1번 pwd로 홈 폴더인지 꼭 확인해요. 프로젝트 폴더에서 치면 그 프로젝트의 기록이 지워져요. 2번 ls -a는 화면 폭에 맞춰 한 줄로 옮겼어요. 3번 rm -rf .git은 출력이 없어요. 01에서 본 대로 rm -rf는 묻지 않고 지우니 .git을 정확히 적어요. 4번처럼 not a git repository가 나오면 정상이에요. 그 아래의 kant/team-intro는 자기 .git이 있어서 그대로 저장소예요. 혼자 하기 불안하면 강사에게 화면을 보여 주고 같이 해요.")

o = [sec("habit")] + head(EB2, "치기 전에 보고, 친 뒤에 다시 봐요", GR)
CX, CY, R = 700, 600, 270
cyc = [("어디?", "프롬프트, pwd", BL, 0, -1), ("무엇이?", "ls", BL, 1, 0), ("명령 치기", "cd, uv run, git add", OR, 0, 1), ("잘 됐나?", "ls, git status", GR, -1, 0)]
o.append(f'<svg viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px"><circle cx="{CX}" cy="{CY}" r="{R}" fill="none" stroke="#D5D1C6" stroke-width="5" stroke-dasharray="4 14" stroke-linecap="round"/></svg>')
for i, (t, d, c, dx, dy) in enumerate(cyc):
    nx, ny = CX + dx * R, CY + dy * R
    o.append(f'<div{bi("pop", i + 1)} style="position:absolute;left:{nx - 50}px;top:{ny - 50}px;width:100px;height:100px;border-radius:50%;background:{c};display:flex;align-items:center;justify-content:center">'
             + p("font-size:46px;font-weight:900;color:#FFFFFF", str(i + 1)) + '</div>')
    if dx == 0:
        tx_, ty_, al = nx + 80, ny - 44, "left"
    elif dx > 0:
        tx_, ty_, al = nx + 80, ny - 44, "left"
    else:
        tx_, ty_, al = nx - 80 - 360, ny - 44, "right"
    o.append(lab(tx_, ty_, e(t), INK, 38, order=i + 1, w=360, align=al))
    o.append(lab(tx_, ty_ + 54, e(d), c, 28, order=i + 1, w=360, align=al, mono=True))
o.append(lab(CX - 200, CY - 30, "명령마다 한 바퀴", GRAY, 34, w=400, align="center", order=5))
o.append(lab(1300, 360, "명령이 바꾼 것은<br>화면에 안 보여요.", INK, 40, w=540, order=5))
o.append(lab(1300, 500, "cd, mkdir, git add는 성공해도 아무 말이 없어요. 그래서 4번에서 한 번 더 봐요.", SUB, 30, w=540, order=5))
W("habit", o, "터미널 작업은 이 네 단계를 돌아요. 1번 프롬프트나 pwd로 어디에 있는지 보고, 2번 ls로 안에 무엇이 있는지 봐요. 3번 명령을 치고, 4번 ls나 git status로 결과가 내가 바란 대로인지 봐요. 탐색기는 파일이 생기면 바로 보이지만 터미널은 아무 말도 안 하는 명령이 많아요. cd, mkdir, git add는 성공해도 출력이 없어요. 4번을 마치면 다음 명령도 다시 1번부터 돌아요.")

o = [sec("status-read")] + head(EB2, "git status는 네 가지를 알려 줘요", GR)
SS = 28
SL = [("$", "~/kant/team-intro", 'echo "# kim" > kim.md'), ("$", "~/kant/team-intro", "git status"), ("o", STATUS_KIM[0]), ("o", STATUS_KIM[1]), ("o", ""), ("o", STATUS_KIM[3]),
      ("o", STATUS_KIM[4]), ("o", STATUS_KIM[5]), ("o", ""), ("o", "nothing added to commit but untracked files present"), ("o", '(use "git add" to track)')]
o.append(term(SL, L, 200, 1150, size=SS, tid="t-status"))
labels = [(2, "지금 이름표 · main 브랜치", 14), (3, "GitHub과 비교 · 마지막 fetch 기준", 45), (5, "바뀐 파일 · kim.md는 아직 Git이 몰라요", 16), (10, "다음 할 일 · git add 힌트", 24)]
for i, (row, a_, ncol) in enumerate(labels):
    yc = ty(200, row, SS) + lh(SS) // 2
    o.append(lead(1290, yc, int(tx(L, ncol, SS)) + 18, yc, GR, order=i + 1))
    o.append(f'<p{bi("fade", i + 1)} style="position:absolute;left:1300px;top:{yc - 19}px;width:38px;height:38px;border-radius:50%;background:{GR};color:#FFFFFF;font-size:22px;font-weight:900;line-height:38px;text-align:center">{i + 1}</p>')
    o.append(lab(1352, yc - 19, e(a_), INK, 26, order=i + 1))
o.append(caption("모르겠으면 git status. 지금 상태와 다음에 칠 명령을 같이 알려 줘요.", 880))
W("status-read", o, "git status는 지금 상태와 다음에 칠 명령을 같이 알려 줘요. 06에서 clone한 team-intro에 kim.md를 하나 만들고 git status를 쳤어요. 1번 On branch main은 지금 main 이름표에 있다는 뜻이에요. 2번은 내 컴퓨터가 기억하는 origin/main과 비교한 결과예요. GitHub의 최신 상태는 git fetch origin을 해야 반영돼요. 3번 Untracked는 02에서 본 새 파일 상태예요. 4번 괄호 안은 다음에 칠 명령 힌트예요. 마지막 줄은 화면 폭 때문에 두 줄로 나눠 적었어요. git status는 아무것도 바꾸지 않으니 몇 번을 쳐도 괜찮아요. 출력은 tools/demo.sh에서 실제로 실행한 결과예요.")

o = [sec("prompt")] + head(EB2, "프롬프트에서 위치를 읽어요", GR)
PS = 40
pr = [("Mac 터미널 (zsh)", ["kim@MacBook-Air hello-uv %"], [(0, 15, "나@컴퓨터", GRAY), (16, 24, "지금 폴더 이름만", BL), (25, 26, "입력 자리", GRAY)], "폴더 이름만 보여요. 전체 경로는 pwd로 봐요."),
      ("Windows Git Bash", ["kim@DESKTOP MINGW64 ~/kant/team-intro (main)", "$"], [(20, 37, "홈에서부터 경로", BL), (38, 44, "저장소 안이면 이름표", GR)], "(main)이 보이면 git 명령이 동작하는 폴더예요.")]
for i, (t, lines, parts_, foot) in enumerate(pr):
    y = 200 + i * 390
    o.append(lab(L, y, e(t), INK, 30))
    bh = 48 + lh(PS) * len(lines)
    o.append(f'<div id="pbar{i}" style="position:absolute;left:{L}px;top:{y + 52}px;width:1728px;height:{bh}px;background:{T_BG};border-radius:18px;padding:24px 36px;font-family:{MONO}">'
             + "".join(p(f"height:{lh(PS)}px;font-size:{PS}px;line-height:{lh(PS)}px;white-space:pre;color:{T_PROMPT}", e(l)) for l in lines) + '</div>')
    for j, (c0, c1, txt, col) in enumerate(parts_):
        order = i * 3 + j + 1
        x1, x2 = int(L + 36 + c0 * PS * CW), int(L + 36 + c1 * PS * CW)
        uy = y + 52 + 24 + lh(PS) - 2
        o.append(underline(order, x1 + 4, x2 - 4, uy, col))
        o.append(lab(x1, y + 52 + bh + 16, e(txt), col, 28, order=order))
    o.append(lab(L, y + 52 + bh + 70, e(foot), INK, 30, order=i * 3 + len(parts_)))
W("prompt", o, "프롬프트는 운영체제와 설정마다 모양이 달라요. 위는 Mac 기본 터미널(zsh)의 모양 예시예요. 지금 폴더 이름 하나만 보여서 같은 이름의 폴더가 여러 개면 헷갈려요. 그럴 땐 pwd를 쳐요. 아래는 Windows Git Bash 예시예요. 두 줄로 나오고 첫 줄에 홈에서부터 경로가 보여요. 저장소 안이면 괄호 안에 지금 이름표가 붙어요. 컴퓨터 이름은 사람마다 달라요. 이 자료의 다른 장은 01처럼 ~/kant $ 모양으로 줄여서 보여 줘요.")

# ---------- part 3: why these names ----------
EB3 = "3. 이름에 담긴 관례"


def rows(x, y, w, data, cols, row_h, order_of=None, size=30, line_top=True):
    """Hairline rows (no cards). cols: list of (x offset, width, style) ; data rows are lists of html strings."""
    o = []
    for i, r in enumerate(data):
        yy = y + i * row_h
        od = order_of(i) if order_of else None
        if line_top or i:
            o.append(hair(x, yy, w, order=None))
        for (cx, cw, st), cell in zip(cols, r):
            o.append(p(f"position:absolute;left:{x + cx}px;top:{yy}px;width:{cw}px;height:{row_h}px;display:flex;align-items:center;{st}", f"<span>{cell}</span>", bi("fade", od)))
    o.append(hair(x, y + len(data) * row_h, w))
    return o


def initials(word, letters):
    """Bold the letters that make up the abbreviation, e.g. print working directory -> p w d."""
    out, k = [], 0
    for ch in word:
        if k < len(letters) and ch.lower() == letters[k]:
            out.append(f'<b style="color:{PUR};font-weight:700">{e(ch)}</b>')
            k += 1
        else:
            out.append(e(ch))
    return "".join(out)


o = [sec("names")] + head(EB3, "명령 이름은 영어 단어를 줄인 거예요", PUR)
nm = [("pwd", "print working directory", "pwd", "지금 폴더 출력"), ("ls", "list", "ls", "목록"), ("cd", "change directory", "cd", "폴더 바꾸기"), ("mkdir", "make directory", "mkdir", "폴더 만들기"),
      ("mv", "move", "mv", "옮기기"), ("cp", "copy", "cp", "복사"), ("rm", "remove", "rm", "지우기"), ("cat", "concatenate", "cat", "이어 붙여 보여 주기")]
cols = [(0, 220, f"font-family:{MONO};font-size:52px;font-weight:700;color:{INK};padding-bottom:40px"), (230, 600, f"font-family:{MONO};font-size:34px;color:{SUB};white-space:nowrap;padding-bottom:40px"), (0, 0, "")]
o += rows(L, 210, 820, [[e(c), initials(en, ab)] for c, en, ab, _ in nm[:4]], cols[:2], 160, order_of=lambda i: 1)
o += rows(1004, 210, 820, [[e(c), initials(en, ab)] for c, en, ab, _ in nm[4:]], cols[:2], 160, order_of=lambda i: 2)
for i, (c, en, ab, ko) in enumerate(nm):
    x = L if i < 4 else 1004
    o.append(lab(x + 230, 210 + (i % 4) * 160 + 92, e(ko), GRAY, 28, order=1 if i < 4 else 2))
o.append(caption("뜻을 알면 외우지 않아도 떠올라요. 처음 보는 명령도 뜻부터 찾아봐요.", 900, order=3))
W("names", o, "01에서 쓴 명령 이름은 모두 영어 단어의 앞 글자나 줄임말이에요. 보라색 글자를 이어 읽으면 명령 이름이 돼요. pwd는 print working directory, 지금 작업 중인 폴더를 출력한다는 뜻이에요. 디렉터리(directory)는 폴더를 부르는 다른 이름이에요. cat은 원래 여러 파일을 이어 붙여 보여 주는 명령이라 이런 이름이 붙었어요. git과 uv도 git add, uv add처럼 영어 동사를 명령 이름으로 써요.", ("names", "이름에 담긴 관례"))

o = [sec("dash")] + head(EB3, "대시 하나는 한 글자, 대시 둘은 단어예요", PUR)
o.append(lab(L, 216, "짧은 이름", GRAY, 26))
o.append(lab(640, 216, "긴 이름", GRAY, 26))
o.append(lab(1340, 216, "--help에 적힌 줄", GRAY, 26))
dd = [("ls -a", "ls --all", "-a, --all"), ("uv -h", "uv --help", "-h, --help"), ("git commit -m", "git commit --message", "-m, --[no-]message")]
cols = [(0, 540, f"font-family:{MONO};font-size:40px;font-weight:700;color:{PUR}"), (544, 690, f"font-family:{MONO};font-size:40px;font-weight:700;color:{BL}"),
        (1244, 484, f"font-family:{MONO};font-size:26px;color:{SUB}")]
o += rows(L, 266, 1728, [[e(a), e(b), e(c)] for a, b, c in dd], cols, 150, order_of=lambda i: i + 1)
o.append(lab(L, 780, "한 글자 옵션은 붙여 써요", INK, 34, order=4))
o.append(lab(L, 850, "ls -a -l", PUR, 52, order=4, mono=True, lid="sep"))
o.append(lab(420, 850, "=", GRAY, 52, order=4))
o.append(p(f"position:absolute;left:510px;top:850px;font-family:{MONO};font-size:52px;font-weight:700;line-height:1.35;color:{PUR};white-space:nowrap", "ls -al", ' data-build-in="fly order 5" data-from="sep"'))
o.append(lab(820, 866, "01에서 쓴 ls -al이 이 모양이에요. 긴 이름은 붙일 수 없어요.", SUB, 30, order=5))
W("dash", o, "옵션 이름에는 대시 하나 뒤에 한 글자, 대시 둘 뒤에 단어를 적는 오래된 약속이 있어요. 옵션은 명령 뒤에 붙어서 동작을 조금 바꾸는 말이에요. 오른쪽은 각 도구의 도움말에 실제로 적힌 줄이에요. 짧은 이름과 긴 이름을 쉼표로 나란히 적어 둬요. git의 --[no-]message는 --message와 --no-message를 같이 적은 표기예요. 한 글자 옵션은 ls -al처럼 대시 하나 뒤에 여러 개를 붙일 수 있어요. 짧은 이름은 치기 편하고, 긴 이름은 읽기 쉬워요. 뜻은 같아요.")

o = [sec("common")] + head(EB3, "여러 도구에서 자주 만나는 옵션이 있어요", PUR)
cm = [("-h, --help", "help", "도움말 보기", ""), ("--version", "version", "버전 보기", ""), ("-m", "message", "메시지 적기", "git commit -m"), ("-r", "recursive", "폴더 안까지 전부", "rm -r"),
      ("-f", "force", "묻지 않고 강제로", "rm -rf"), ("-a", "all", "숨긴 것까지 전부", "ls -a"), ("-q", "quiet", "출력 줄이기", ""), ("-v", "verbose", "출력 자세히", "")]
cols = [(0, 250, f"font-family:{MONO};font-size:34px;font-weight:700;color:{PUR};white-space:nowrap"), (260, 220, f"font-family:{MONO};font-size:26px;color:{INK}"),
        (480, 340, f"font-size:28px;font-weight:700;color:{SUB}")]
for half in range(2):
    sub = cm[half * 4:(half + 1) * 4]
    o += rows(L + half * 908, 216, 820, [[e(a), e(b), e(c) + (f'&#160;&#160;<span style="font-family:{MONO};font-size:22px;font-weight:400;color:{GRAY}">{e(d)}</span>' if d else "")] for a, b, c, d in sub],
              cols, 140, order_of=lambda i, h=half: h + 1)
o.append(spot(3, L, 216, 820, 140, pad=6, r=10, dim=0.5))
o.append(lab(L, 816, "처음 보는 도구도 --help와 --version은 거의 다 통해요.", INK, 32, order=3))
o.append(spot_off(4))
o.append(caption("대부분 이 뜻이지만 도구마다 다를 수 있어요. 다음 장에서 예외를 봐요.", 900, order=4))
W("common", o, "여러 도구가 같은 글자에 같은 뜻을 붙이는 경우가 많아요. 그래서 처음 보는 도구도 --help, --version은 거의 다 통해요. -m은 git commit -m의 message, -r은 rm -r의 recursive(안쪽까지 되풀이), -f는 rm -rf의 force예요. -q는 quiet(조용히), -v는 verbose(자세히)예요. 이 표는 외울 표가 아니라 이런 약속이 있다는 것만 알면 돼요.")

o = [sec("except")] + head(EB3, "관례는 약속일 뿐이라 예외가 있어요", PUR)
XS = 32
XL = [("$", "~/kant/hello-uv", "ls -h"), ("o", "README.md  pyproject.toml"), ("o", "main.py    uv.lock"), ("$", "~", "git -v"), ("o", "git version 2.43.0"), ("$", "~", "uv -V"), ("o", "uv 0.11.32 (x86_64-unknown-linux-gnu)")]
o.append(term(XL, L, 210, 1100, size=XS, tid="t-ex"))
o.append(pen_box(1, int(tx(L, 0, XS)) - 10, ty(210, 1, XS), int(26 * XS * CW) + 20, lh(XS) * 2, RED))
o.append(lead(1240, ty(210, 1, XS) + lh(XS), int(tx(L, 26, XS)) + 12, ty(210, 1, XS) + lh(XS), RED, order=1))
o.append(lab(1252, ty(210, 1, XS) + 4, "ls -h는 help가 아니에요", RED, 32, order=1))
o.append(lab(1252, ty(210, 1, XS) + 54, "크기를 읽기 쉽게 보여 주는 옵션이에요", SUB, 26, order=1))
o.append(underline(2, int(tx(L, 8, XS)), int(tx(L, 10, XS)), ty(210, 3, XS) + lh(XS) - 6, OR))
o.append(underline(2, int(tx(L, 7, XS)), int(tx(L, 9, XS)), ty(210, 5, XS) + lh(XS) - 6, OR))
o.append(lead(1240, ty(210, 5, XS) + lh(XS) // 2, int(tx(L, 10, XS)) + 12, ty(210, 5, XS) + lh(XS) // 2, OR, order=2))
o.append(lab(1252, ty(210, 4, XS) + 20, "버전 글자가 달라요", OR, 32, order=2))
o.append(lab(1252, ty(210, 4, XS) + 70, "git은 -v, uv는 대문자 -V", SUB, 26, order=2))
ey = 210 + theight(len(XL), XS) + 50
o.append(lab(L, ey, "Mac 기본 ls는 --help를 몰라요. man ls로 설명서를 열고 q로 나와요.", INK, 32, order=3))
o.append(caption("헷갈리면 긴 이름 --help부터 쳐 봐요. 가장 많이 통해요.", ey + 70, order=3))
W("except", o, "ls -h는 도움말이 아니라 human-readable 옵션이라 그냥 목록이 나와요. ls -lh처럼 -l과 같이 쓸 때 파일 크기를 4.0K처럼 보여 줘요. 버전 글자도 도구마다 달라요. git은 -v와 --version이 같고, uv는 대문자 -V와 --version이 같아요. uv의 소문자 -v는 verbose예요. Mac 기본 ls, cp, mv는 --help를 몰라서 에러와 짧은 사용법만 보여 줘요. 이때는 man(manual, 설명서) 명령으로 설명서를 열어요. Windows Git Bash는 ls --help가 돼요. ls -h는 좁은 터미널(ls -C -w 40)에서 실행한 모양이에요. Mac 출력은 이 자료를 만든 환경에서 실행할 수 없어서 옮기지 않았어요. 출력은 tools/demo.sh에서 실제로 실행한 결과예요.")

o = [sec("origin-main")] + head(EB3, "origin과 main도 관례로 붙인 이름이에요", PUR)
OS_ = 30
OL = [("$", "~/kant/team-intro", "git remote -v"), ("o", "origin\thttps://github.com/kim/team-intro.git (fetch)"), ("o", "origin\thttps://github.com/kim/team-intro.git (push)"),
      ("$", "~/kant/team-intro", "git branch"), ("o", "* main")]
o.append(term(OL, L, 210, 1180, size=OS_, tid="t-om"))
o.append(pen_box(1, int(tx(L, 0, OS_)) - 8, ty(210, 1, OS_) + 2, int(6 * OS_ * CW) + 16, lh(OS_) * 2 - 4, PUR))
o.append(pen_box(2, int(tx(L, 2, OS_)) - 8, ty(210, 4, OS_) + 2, int(4 * OS_ * CW) + 16, lh(OS_) - 4, BL))
o.append(lab(1340, 220, "origin", PUR, 48, order=1, mono=True))
o.append(lab(1340, 290, "원래(origin) 가져온 곳", INK, 30, order=1))
o.append(lab(1340, 340, "02 · git remote add origin으로 직접<br>06 · clone하면 git이 붙여 줘요", SUB, 26, order=1, w=480))
o.append(lab(1340, 470, "main", BL, 48, order=2, mono=True))
o.append(lab(1340, 540, "주된 줄기, 첫 브랜치 이름", INK, 30, order=2))
o.append(lab(1340, 590, "02 · init.defaultBranch main<br>예전 기본 이름은 master", SUB, 26, order=2, w=480))
o.append(lab(L, 210 + theight(5, OS_) + 60, "바꿀 수 있는 이름이지만 모두 같은 이름을 써요.", INK, 34, order=3))
o.append(lab(L, 210 + theight(5, OS_) + 116, "그래서 검색한 글, 에러 메시지, 팀원의 명령을 그대로 따라 칠 수 있어요.", SUB, 30, order=3))
W("origin-main", o, "origin과 main은 git이 정한 명령이 아니라 사람들이 맞춘 이름이에요. origin은 영어로 출처, 원래 온 곳이라는 뜻이에요. 02에서는 git remote add origin 주소로 이 이름을 직접 붙였고, 06에서 clone할 때는 git이 자동으로 origin이라고 붙였어요. main은 첫 브랜치의 이름이에요. git의 예전 기본 이름은 master였고, GitHub은 2020년부터 새 저장소의 기본 이름을 main으로 바꿨어요. 02에서 init.defaultBranch main을 설정한 이유예요. 출력은 tools/demo.sh의 team-intro에서 실제로 실행한 결과예요.")

o = [sec("push-read")] + head(EB3, "git push origin main을 도움말로 읽어 봐요", PUR)
US = 40
o.append(lab(L, 220, "git push -h 첫 줄", GRAY, 26))
o.append(f'<div id="usage" style="position:absolute;left:{L}px;top:270px;width:1728px;height:120px;background:{T_BG};border-radius:18px;padding:0 40px;display:flex;align-items:center;font-family:{MONO}">'
         + p(f"font-size:{US}px;white-space:pre;color:{T_OUT}", 'usage: git push [&lt;options&gt;] [<span style="color:#C7B6FF;font-weight:700">&lt;repository&gt;</span> [<span style="color:#8FB3FF;font-weight:700">&lt;refspec&gt;</span>...]]') + '</div>')
cx = lambda c: int(L + 40 + c * US * CW)
# usage: git push [<options>] [<repository> [<refspec>...]]
#        0123456789012345678901234567890123456789
rep0, rep1, ref0, ref1 = 29, 41, 43, 52
o.append(f'<p style="position:absolute;left:{L + 40}px;top:640px;font-family:{MONO};font-size:64px;font-weight:700;line-height:1.3;white-space:pre;color:{INK}">git push <span style="color:{PUR}">origin</span> <span style="color:{BL}">main</span></p>')
W64 = 64 * CW
o_x0, o_x1 = int(L + 40 + 9 * W64), int(L + 40 + 15 * W64)
m_x0, m_x1 = int(L + 40 + 16 * W64), int(L + 40 + 20 * W64)
o.append(path_svg(f"M{(o_x0 + o_x1) // 2},630 C{(o_x0 + o_x1) // 2},520 {(cx(rep0) + cx(rep1)) // 2},500 {(cx(rep0) + cx(rep1)) // 2},400", PUR, order=1))
o.append(lab((o_x0 + o_x1) // 2 - 444, 560, "어디로 · 원격 이름", PUR, 30, order=1, w=420, align="right"))
o.append(path_svg(f"M{(m_x0 + m_x1) // 2},630 C{(m_x0 + m_x1) // 2},540 {(cx(ref0) + cx(ref1)) // 2},520 {(cx(ref0) + cx(ref1)) // 2},400", BL, order=2))
o.append(lab(m_x1 + 30, 664, "무엇을 · 브랜치 이름", BL, 30, order=2))
o.append(lab(L, 800, "도움말의 &lt;repository&gt; 자리에 origin, &lt;refspec&gt; 자리에 main을 넣었어요. git pull origin main도 같은 순서예요.", SUB, 30, order=3, w=1728))
o.append(caption("우리 과정은 이 두 칸을 매번 끝까지 적어요.", 900, order=3))
W("push-read", o, "git push origin main은 도움말 첫 줄의 두 자리에 origin과 main을 넣은 거예요. git push -h를 치면 맨 위에 사용법 한 줄이 나와요. 꺾쇠 안의 repository는 원격 저장소 이름, refspec은 보낼 브랜치를 가리키는 자리예요. 대괄호는 다음 파트에서 봐요. 우리 과정에서는 이 두 칸을 생략하지 않고 매번 적어요. 그래야 어디로 무엇을 보내는지 눈으로 확인할 수 있어요. 옵션 목록은 길어서 첫 줄만 옮겼어요.")

# ---------- part 4: reading help ----------
EB4 = "4. 도움말로 스스로 찾기"
o = [sec("usage")] + head(EB4, "Usage 줄의 기호 네 가지를 읽어요", OR)
U1 = "Usage: ls [OPTION]... [FILE]..."
U2 = "Usage: uv add [OPTIONS] <PACKAGES|--requirements <REQUIREMENTS>>"
o.append(lab(L, 216, "ls --help 첫 줄", GRAY, 26))
o.append(term([("o", U1)], L, 262, 1728, size=40, tid="u1"))
o.append(lab(L, 520, "uv add -h 첫 줄", GRAY, 26))
o.append(term([("o", U2)], L, 566, 1728, size=34, tid="u2"))
ux1 = lambda c: int(tx(L, c, 40))
ux2 = lambda c: int(tx(L, c, 34))
y1 = ty(262, 0, 40) + lh(40) - 4
y2 = ty(566, 0, 34) + lh(34) - 4
# [ ] around OPTION (cols 10-17), ... (18-20); < > (cols 22..63), | (col 31)
o.append(underline(1, ux1(10), ux1(18), y1, OR))
o.append(lab(ux1(10), 262 + theight(1, 40) + 10, "[ ] 넣어도 되고 빼도 돼요", OR, 28, order=1))
o.append(underline(2, ux1(18), ux1(21), y1, BL))
o.append(lab(ux1(18) + 300, 262 + theight(1, 40) + 10, "... 여러 개 적을 수 있어요", BL, 28, order=2))
o.append(underline(3, ux2(U2.index("<P")), ux2(len(U2)), y2, PUR))
o.append(lab(ux2(U2.index("<P")), 566 + theight(1, 34) + 10, "&lt; &gt; 내 값으로 바꿔 적어요 · 꼭 넣어요", PUR, 28, order=3))
o.append(ring(4, ux2(U2.index("|")), ty(566, 0, 34) + 6, int(34 * CW), lh(34) - 12, RED, 5))
o.append(lab(ux2(U2.index("|")) + 520, 566 + theight(1, 34) + 10, "| 둘 중 하나만 골라요", RED, 28, order=4))
o.append(lab(L, 850, "이렇게 쳐요", GRAY, 26, order=5))
o.append(p(f"position:absolute;left:{L + 170}px;top:842px;display:flex;gap:18px", code("ls", BL, 30) + code("ls -a", BL, 30) + code("ls -a -l notes", BL, 30) + code("uv add fastapi", BL, 30), bi("fade", 5)))
W("usage", o, "도움말 맨 위의 Usage(사용법) 줄은 명령을 어떤 순서로 적는지 보여 줘요. 대괄호는 생략할 수 있는 자리, 꺾쇠는 내 값으로 바꾸는 자리예요. 점 세 개는 여러 개를 적을 수 있다는 뜻이고, 세로 막대는 둘 중 하나예요. 대문자 OPTION, FILE은 그 자리에 무엇이 들어가는지 이름만 적은 거예요. ls의 사용법은 전부 대괄호라서 ls만 쳐도 돼요. uv add는 꺾쇠라서 패키지 이름을 꼭 적어요. 앞 장의 git push 사용법도 같은 기호예요. 두 Usage 줄은 tools/demo.sh에서 실제로 실행한 결과예요.", ("help", "도움말로 스스로 찾기"))

o = [sec("options")] + head(EB4, "옵션 목록은 짧은 이름, 긴 이름, 설명 순서예요", OR)
LSH = ["Usage: ls [OPTION]... [FILE]...", "List information about the FILEs (the current directory by default).", "",
       "Mandatory arguments to long options are mandatory for short options too.", "  -a, --all                  do not ignore entries starting with .",
       ]
OS2 = 30
OLL = [("$", "~", "ls --help")] + [("o", l) for l in LSH] + [("d", "…")]
o.append(term(OLL, L, 200, 1728, size=OS2, tid="t-lshelp"))
ar = 5  # row of "-a, --all"
yb = ty(200, ar, OS2) + lh(OS2) - 4
o.append(spot(1, int(tx(L, 0, OS2)), ty(200, ar, OS2), 1660, lh(OS2), pad=8, r=8, dim=0.45))
o.append(spot_off(2))
segs = [(2, 4, "짧은 이름", PUR), (6, 11, "긴 이름", BL), (29, 66, "설명 · 점으로 시작하는 것도 빼지 않아요", OR)]
ly = 200 + theight(len(OLL), OS2) + 90
LXS = [L, L + 330, int(tx(L, 29, OS2))]
for i, (c0, c1, t, col) in enumerate(segs):
    o.append(underline(2 + i, int(tx(L, c0, OS2)), int(tx(L, c1, OS2)), yb, col))
    sx = int(tx(L, (c0 + c1) / 2, OS2))
    lx = LXS[i]
    o.append(path_svg(f"M{sx},{yb + 12} L{sx},{ly - 26} L{lx + 40},{ly - 26} L{lx + 40},{ly - 2}", col, order=2 + i, width=3, arrow=False))
    o.append(lab(lx, ly + 6, e(t), col, 30, order=2 + i))
o.append(caption("01에서 쓴 ls -a가 목록 맨 위에 있어요.", 930, order=4))
W("options", o, "옵션 목록은 한 줄에 짧은 이름, 긴 이름, 설명이 차례로 있어요. ls --help의 앞부분이고 뒤는 길어서 줄였어요. Usage 아래에 한두 줄 설명이 나오고, 그 아래부터 옵션 목록이에요. -a, --all 줄은 점으로 시작하는 파일을 숨기지 않는다는 뜻이에요. 01에서 ls -a로 .git, .venv 같은 숨김 파일을 본 게 이 옵션이에요. 설명은 영어지만 짧아서 번역기에 넣어도 돼요. 출력이 길어서 위가 잘리면 터미널을 위로 스크롤해요. 출력은 tools/demo.sh에서 실제로 실행한 결과예요.")

o = [sec("git-help")] + head(EB4, "git은 도움말을 세 가지로 보여 줘요", OR)
gh = [("git --help", "자주 쓰는 명령 목록", "명령 이름이 기억나지 않을 때", "터미널에 바로"),
      ("git 명령 -h", "그 명령의 짧은 옵션표", "옵션 글자가 기억나지 않을 때", "터미널에 바로"),
      ("git 명령 --help", "그 명령의 설명서 전체", "자세한 설명과 예시가 필요할 때", "Mac은 설명서 화면<br>Windows는 브라우저")]
o.append(lab(L, 216, "명령", GRAY, 26))
o.append(lab(L + 470, 216, "보여 주는 것", GRAY, 26))
o.append(lab(L + 920, 216, "이럴 때", GRAY, 26))
o.append(lab(L + 1400, 216, "열리는 곳", GRAY, 26))
cols = [(0, 460, f"font-family:{MONO};font-size:38px;font-weight:700;color:{OR};white-space:nowrap"), (470, 440, f"font-size:30px;font-weight:700;color:{INK}"),
        (920, 470, f"font-size:28px;color:{SUB}"), (1400, 328, f"font-size:26px;color:{GRAY};line-height:1.4")]
o += rows(L, 266, 1728, [[e(a), e(b), e(c), d] for a, b, c, d in gh], cols, 150, order_of=lambda i: i + 1)
o.append(lab(L, 760, "예", GRAY, 28, order=4))
o.append(p(f"position:absolute;left:{L + 60}px;top:752px;display:flex;gap:18px;align-items:center;font-size:28px;color:{SUB}",
           code("git commit -h", BL, 32) + "짧게&#160;&#160;" + code("git commit --help", BL, 32) + "자세히&#160;&#160;" + code("git help commit", BL, 32) + "--help와 같아요", bi("fade", 4)))
o.append(caption("git에서는 -h와 --help가 달라요. 처음엔 -h부터 쳐요.", 900, order=4))
W("git-help", o, "git은 -h와 --help를 다르게 써요. git 명령 -h는 터미널에 옵션표를 짧게 바로 보여 줘요. git 명령 --help는 그 명령의 설명서 전체를 열어요. Mac과 Linux는 터미널 안에 설명서 화면이 열리고, Windows Git Bash는 브라우저에 설명서 웹 페이지가 열려요. git help commit은 git commit --help와 같아요. 명령 이름 자체가 기억나지 않으면 git --help로 목록부터 봐요.")

GITH = ["usage: git [-v | --version] [-h | --help] [-C <path>] [-c <name>=<value>]", "           …", "", "These are common Git commands used in various situations:", "",
        "start a working area (see also: git help tutorial)", "   clone     Clone a repository into a new directory", "   init      Create an empty Git repository or reinitialize an existing one", "",
        "…", "", "collaborate (see also: git help workflows)", "   fetch     Download objects and refs from another repository",
        "   pull      Fetch from and integrate with another repository or a local branch", "   push      Update remote refs along with associated objects"]
o = [sec("git-list")] + head(EB4, "git --help는 명령 이름이 기억나지 않을 때 봐요", OR)
GS = 24
o.append(term([("$", "~", "git --help")] + [("d" if l.strip() == "…" else "o", l) for l in GITH], L, 196, 1300, size=GS, tid="t-githelp"))
r_title, r_cmd = 6, 7
o.append(underline(1, int(tx(L, 0, GS)), int(tx(L, 20, GS)), ty(196, r_title, GS) + lh(GS) - 4, OR))
o.append(lead(1440, ty(196, r_title, GS) + lh(GS) // 2, int(tx(L, 50, GS)) + 14, ty(196, r_title, GS) + lh(GS) // 2, OR, order=1))
o.append(lab(1452, ty(196, r_title, GS) - 4, "묶음 제목 · 하는 일별로", OR, 28, order=1))
o.append(pen_box(2, int(tx(L, 3, GS)) - 6, ty(196, r_cmd, GS), int(5 * GS * CW) + 12, lh(GS) * 2, BL))
o.append(lead(1440, ty(196, r_cmd, GS) + lh(GS), int(tx(L, 8, GS)) + 10, ty(196, r_cmd, GS) + lh(GS), BL, order=2))
o.append(lab(1452, ty(196, r_cmd, GS) + lh(GS) - 22, "왼쪽 칸 · 명령 이름", BL, 28, order=2))
o.append(lab(1452, ty(196, r_cmd, GS) + lh(GS) + 20, "오른쪽 칸 · 한 줄 설명", SUB, 26, order=2))
o.append(lab(1440, 860, "02, 06에서 쓴 clone, init,<br>fetch, pull, push가 다 있어요.", INK, 30, order=3, w=400))
W("git-list", o, "git --help를 치면 자주 쓰는 명령을 하는 일별로 묶어서 보여 줘요. 화면 폭 때문에 가운데 묶음 세 개를 …로 줄였어요. 줄인 곳에는 add, status, log, commit, branch, merge처럼 02부터 배운 명령이 들어 있어요. 왼쪽이 명령 이름, 오른쪽이 한 줄 설명이에요. 맨 아래에는 git help -a로 전체 명령을 볼 수 있다는 안내가 나와요. 출력은 tools/demo.sh에서 실제로 실행한 결과예요.")

GITC = ["usage: git commit [-a | --interactive | --patch] [-s] [-v] [-u<mode>] [--amend]", "                  …", "", "    -q, --[no-]quiet      suppress summary after successful commit",
        "    -v, --[no-]verbose    show diff in commit message template", "", "Commit message options", "    -F, --[no-]file <file>", "                          read message from file",
        "    --[no-]author <author>", "                          override author for commit", "    --[no-]date <date>    override date for commit",
        "    -m, --[no-]message <message>", "                          commit message", "    …"]
o = [sec("git-h")] + head(EB4, "git commit -h는 옵션 글자가 기억나지 않을 때 봐요", OR)
o.append(term([("$", "~/kant/team-intro", "git commit -h")] + [("d" if l.strip() == "…" else "o", l) for l in GITC], L, 196, 1300, size=GS, tid="t-gitch"))
mr = 13
o.append(spot(1, int(tx(L, 0, GS)), ty(196, mr, GS), 1240, lh(GS) * 2, pad=8, r=8, dim=0.5))
o.append(spot_off(2))
o.append(ring(2, int(tx(L, 4, GS)), ty(196, mr, GS) + 2, int(28 * GS * CW), lh(GS) - 4, OR, 5))
o.append(lead(1440, ty(196, mr, GS) + lh(GS) // 2, int(tx(L, 32, GS)) + 40, ty(196, mr, GS) + lh(GS) // 2, OR, order=2))
o.append(lab(1452, ty(196, mr, GS) - 40, "찾던 줄", GRAY, 26, order=2))
o.append(lab(1452, ty(196, mr, GS) - 4, "-m &lt;message&gt;", OR, 34, order=2, mono=True))
o.append(lab(1452, ty(196, mr, GS) + 48, "&lt;message&gt;가 붙어 있으니<br>메시지를 꼭 적어요", INK, 28, order=2, w=420))
o.append(lab(1452, 260, "목록이 70줄쯤 돼요.<br>지금 찾는 한 줄만 봐요.", SUB, 28, order=3, w=420))
W("git-h", o, "커밋 메시지 옵션이 기억나지 않으면 git commit -h를 쳐요. 사용법 줄과 뒤쪽 목록은 …로 줄였어요. Commit message options 묶음 안에 -m, --[no-]message <message>가 있어요. 꺾쇠가 붙어 있으니 -m 뒤에 메시지를 적어야 해요. 그래서 git commit -m \"docs: 소개 추가\"처럼 써요. 위가 잘리면 터미널을 위로 스크롤해요. 출력은 tools/demo.sh에서 실제로 실행한 결과예요.")

o = [sec("pager")] + head(EB4, "설명서 화면이 열리면 q로 나와요", OR)
MAN = ["GIT-COMMIT(1)                Git Manual                GIT-COMMIT(1)", "", "NAME", "       git-commit - Record changes to the repository", "", "SYNOPSIS",
       "       git commit [-a | --interactive | --patch] [-s] [-v] [-u<mode>]", "                  …", "", "DESCRIPTION", "       Create a new commit containing the current contents of the", "       index and the given log message describing the changes. …"]
MS = 26
mh = TP + len(MAN) * lh(MS) + 60 + TP
o.append(f'<div id="man" style="position:absolute;left:{L}px;top:196px;width:1180px;height:{mh}px;background:{T_BG};border-radius:18px;padding:{TP}px 32px;display:flex;flex-direction:column;font-family:{MONO}">'
         + "".join(tline(("d" if l.strip() == "…" else "o", l), MS) for l in MAN) + '<div style="flex:1"></div>'
         + p(f"font-size:{MS}px;line-height:1.45;white-space:pre;color:{T_BG};background:{T_OUT};align-self:flex-start;padding:0 8px", " Manual page git-commit(1) line 1 (press h for help or q to quit)") + '</div>')
QS = " Manual page git-commit(1) line 1 (press h for help or q to quit)"
qx = int(L + 32 + 8 + QS.index("q to quit") * MS * CW)
qy = 196 + mh - TP - 38
o.append(ring(1, qx - 4, qy, int(9 * MS * CW), 38, RED, 5))
keys = [("q", "나가기"), ("Space", "다음 쪽"), ("b", "앞 쪽"), ("/단어", "단어 찾기")]
for i, (k, d) in enumerate(keys):
    y = 220 + i * 120
    big = k == "q"
    o.append(p(f"position:absolute;left:1340px;top:{y}px;width:170px;height:76px;font-family:{MONO};font-size:34px;font-weight:700;line-height:66px;text-align:center;"
               f"color:{RED if big else INK};background:#FFFFFF;border:2px solid #C9CED8;border-bottom-width:8px;border-radius:12px", e(k), bi("rise", 1 if big else 2)))
    o.append(lab(1540, y + 14, e(d), RED if big else INK, 34 if big else 30, order=1 if big else 2))
o.append(lab(1340, 720, "git log가 길 때도 이 화면이 나와요.<br>맨 아래에 : 이나 (END)가 보이면 q예요.", SUB, 26, order=3, w=484))
W("pager", o, "Mac과 Linux에서 git commit --help나 man ls를 치면 터미널 전체가 설명서 화면으로 바뀌고, q로 나와요. 명령을 쳐도 반응이 없어서 멈춘 것처럼 보여요. 이 화면에서는 Space로 다음 쪽, b로 앞 쪽, 슬래시 뒤에 단어를 치고 Enter로 찾아요. 왼쪽 그림은 설명서 화면을 줄여 그린 거예요. 설명서 화면은 이 자료를 만든 환경에서 열 수 없어서 실제 출력을 옮기지 않았어요. Windows Git Bash는 --help가 브라우저로 열려서 이 화면이 나오지 않아요. 02에서 git log 기록이 길 때도 같은 화면이 나와요. 그때도 q예요.")

UVH = ["An extremely fast Python package manager.", "", "Usage: uv [OPTIONS] <COMMAND>", "", "Commands:", "  auth       Manage authentication", "  run        Run a command or script",
       "  init       Create a new project", "  add        Add dependencies to the project", "  remove     Remove dependencies from the project",
       "  version    Read or update the project's version", "  sync       Update the project's environment", "  lock       Update the project's lockfile",
       "  export     Export the project's lockfile to an alternate format", "  tree       Display the project's dependency tree", "  …"]
o = [sec("uv-help")] + head(EB4, "uv --help로 uv 명령 목록을 봐요", OR)
USED = ("run", "init", "add", "remove", "sync", "tree")
UL = []
for l in UVH:
    w0 = l.split()[0] if l.strip() else ""
    UL.append(("d", l) if l.strip() == "…" else ("m", l) if w0 in USED and l.startswith("  ") else ("o", l))
o.append(term([("$", "~/kant/hello-uv", "uv --help")] + UL, L, 196, 1240, size=GS, tid="t-uvhelp"))
o.append(lab(1400, 230, "노란 줄", GRAY, 26))
o.append(lab(1400, 270, "09에서 쓴 명령", INK, 34))
o.append(lab(1400, 324, "run init add<br>remove sync tree", OR, 32, mono=True, w=440))
o.append(hair(1400, 470, 424))
o.append(lab(1400, 500, "uv는 -h와 --help가 같아요", INK, 30, order=1))
o.append(lab(1400, 548, "더 긴 설명은 help 뒤에 명령 이름", SUB, 26, order=1, w=430))
o.append(lab(1400, 590, "uv help add", BL, 30, order=1, mono=True))
W("uv-help", o, "uv --help는 uv에서 쓸 수 있는 명령을 한 줄 설명과 함께 보여 줘요. 아래쪽 명령과 옵션은 …로 줄였어요. 노랗게 칠한 줄은 09에서 쓴 명령이에요. uv는 git과 달리 -h와 --help가 같은 짧은 도움말을 보여 줘요. 더 자세한 설명은 uv help add처럼 help 뒤에 명령 이름을 적어요. 이때는 앞에서 본 설명서 화면처럼 열릴 수 있어서 q로 나와요. 출력은 tools/demo.sh에서 실제로 실행한 결과예요.")

o = [sec("typo")] + head(EB4, "오타를 내면 도구가 먼저 알려 줘요", OR)
TL = [("$", "~/kant/team-intro", "git stauts"), ("e", "git: 'stauts' is not a git command."), ("e", "See 'git --help'."), ("o", ""), ("y", "The most similar command is"), ("y", "\tstatus")]
TR = [("$", "~/kant/hello-uv", "uv ad fastapi"), ("e", "error: unrecognized subcommand 'ad'"), ("o", ""), ("y", "  tip: some similar subcommands"), ("y", "  exist: 'audit', 'add'"), ("o", ""),
      ("o", "Usage: uv [OPTIONS] <COMMAND>"), ("o", ""), ("o", "For more information, try '--help'.")]
parts, h = pair(TL, TR, "git stauts", "uv ad fastapi", size=32, top=260, lcolor=OR, rcolor=OR)
o += parts
o.append(underline(2, int(tx(L, 4, 32)), int(tx(L, 10, 32)), ty(260, 5, 32) + lh(32) - 4, OR))
o.append(underline(3, int(tx(984, 9, 32)), int(tx(984, 22, 32)), ty(260, 4, 32) + lh(32) - 4, OR))
o.append(lab(L, 260 + h + 40, "에러 메시지는 맨 아래 몇 줄을 읽어요. 노란 줄만 읽어도 고칠 수 있어요.", INK, 32, order=3, w=1728))
W("typo", o, "명령 이름을 잘못 치면 git과 uv 모두 비슷한 이름을 찾아 줘요. git stauts에는 status를, uv ad에는 audit과 add를 권해요. 끝에는 --help를 쳐 보라는 안내도 있어요. 에러가 나면 지우고 다시 치기 전에 맨 아래 몇 줄을 소리 내어 읽어 봐요. 위 화살표로 앞 명령을 불러와 고치면 빨라요. 화면 폭 때문에 긴 줄은 나눠 적었어요. 출력은 tools/demo.sh에서 실제로 실행한 결과예요.")

o = [sec("find")] + head(EB4, "모르는 기능을 도움말로 찾아가요", OR)
o.append(lab(L, 210, "하고 싶은 일 · 설치한 패키지를 나무 모양으로 보고 싶어요", INK, 32))
FSZ = 30
FLL = [("$", "~/kant/hello-uv", "uv --help"), ("d", "  …"), ("m", "  tree       Display the project's dependency tree"), ("d", "  …"),
       ("$", "~/kant/hello-uv", "uv tree -h"), ("o", "Display the project's dependency tree"), ("o", ""), ("o", "Usage: uv tree [OPTIONS]"),
       ("$", "~/kant/hello-uv", "uv tree"), ("o", "Resolved 1 package in 2ms"), ("o", "hello-uv v0.1.0")]
FX1 = 200
o.append(term(FLL, FX1, 290, 1100, size=FSZ, tid="t-find"))
fsteps = [(0, 4, "목록에서 tree를 찾았어요"), (4, 4, "옵션이 다 대괄호라<br>그냥 쳐도 돼요"), (8, 3, "패키지를 넣으면<br>아래로 가지가 늘어요")]
for i, (r0, n, d) in enumerate(fsteps):
    yc = ty(290, r0, FSZ)
    o.append(f'<p style="position:absolute;left:{L + 40}px;top:{yc}px;width:44px;height:44px;border-radius:50%;background:{OR};color:#FFFFFF;font-size:26px;font-weight:900;line-height:44px;text-align:center">{i + 1}</p>')
    o.append(spot(i + 1, int(tx(FX1, 0, FSZ)) - 14, yc, 1100 - 36, lh(FSZ) * n, pad=8, r=10, dim=0.5))
    o.append(lab(1340, yc + 4, d, INK, 30, order=i + 1, w=484))
o.append(spot_off(4))
o.append(caption("목록에서 이름 찾기, -h로 쓰는 법 보기, 쳐 보기. 이 세 단계면 돼요.", 930, order=4))
W("find", o, "목록에서 이름 찾기, -h로 쓰는 법 보기, 쳐 보기. 이 세 단계면 모르는 기능도 찾아가요. 09에서 uv tree를 배웠지만 이름을 잊었다고 해 볼게요. 1번 uv --help 목록에서 dependency tree라는 설명을 보고 tree를 찾아요. 2번 uv tree -h로 사용법을 보면 [OPTIONS]만 있어서 옵션 없이 쳐도 돼요. 3번 실제로 쳐요. 아직 패키지가 없어서 한 줄이에요. 09처럼 fastapi를 넣었다면 그 아래로 패키지가 줄줄이 나와요. git도 같은 순서로 git --help, git 명령 -h를 보면 돼요. 1번 출력은 앞뒤를 …로 줄였어요. 출력은 tools/demo.sh의 hello-uv에서 실제로 실행한 결과예요.")

# ---------- summary ----------
EB5 = "정리"
o = [sec("trouble")] + head(EB5, "터미널에서 막히면 이 표를 봐요", RED)
tr = [("fatal: not a git repository", "git 저장소 폴더 밖이에요", "pwd 뒤 cd 저장소"), ("error: Failed to spawn: `main.py`", "main.py가 없는 폴더예요", "ls 뒤 cd hello-uv"),
      ("No such file or directory", "위치나 이름이 틀렸어요", "pwd, ls, Tab"), ("화면이 멈추고 : 이나 (END)만 보여요", "설명서 화면이에요", "q"),
      ("홈 폴더에서 git status가 동작해요", "홈에서 git init을 쳤어요", "PG_INIT"), ("옵션이 기억나지 않아요", "도움말을 봐요", "명령 -h, --help")]
o.append(lab(L, 216, "보이는 것", GRAY, 26))
o.append(lab(L + 800, 216, "원인", GRAY, 26))
o.append(lab(L + 1320, 216, "칠 것", GRAY, 26))
cols = [(0, 790, ""), (800, 510, f"font-size:30px;color:{SUB}"), (1320, 408, f"font-family:{MONO};font-size:30px;font-weight:700;color:{INK};white-space:nowrap")]
data = [[(f'<span style="font-family:{MONO};font-size:28px;font-weight:700;color:{RED}">{e(q)}</span>' if q.isascii() else f'<span style="font-size:30px;font-weight:700;color:{INK}">{e(q)}</span>'), e(a_), e(c_)] for q, a_, c_ in tr]
o += rows(L, 266, 1728, data, cols, 108, order_of=lambda i: i + 1)
W("trouble", o, "막혔을 때 위에서부터 맞는 줄을 찾아요. 1번과 2번은 2파트에서 본 에러예요. 명령을 고치기 전에 서 있는 폴더부터 봐요. 1번은 실제로 (or any of the parent directories): .git이 뒤에 더 붙어요. 3번은 01에서 본 에러예요. 이름은 Tab으로 자동 완성하면 오타가 줄어요. 4번은 --help나 man, 긴 git log에서 열리는 설명서 화면이에요. 5번은 2파트의 순서대로 홈 폴더의 .git만 지워요. 6번은 4파트에서 본 순서대로 찾아요.", ("trouble", "정리"))

o = [f'<section id="cheatsheet" data-transition="fade" style="background:{BG};color:{INK};font-family:{SANS};font-variant-ligatures:none;word-break:keep-all;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:{L}px;top:80px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>']
groups = [("어디에 있나", BL, [("pwd", "지금 위치"), ("ls", "안에 든 것"), ("git status", "저장소 상태")]),
          ("옮겨 다니기", GR, [("cd 폴더", "들어가기"), ("cd ..", "한 칸 위로"), ("cd -", "바로 전 폴더"), ("cd ~", "홈 폴더")]),
          ("도움 받기", OR, [("명령 --help", "도움말"), ("git 명령 -h", "git 짧은 옵션표"), ("uv 명령 -h", "uv 도움말"), ("q", "설명서 화면 나가기")])]
for i, (t, c, rr) in enumerate(groups):
    x = L + i * 600
    if i:
        o.append(hair(x - 40, 230, 2, h=540))
    o.append(lab(x, 230, e(t), c, 34))
    for j, (k, d) in enumerate(rr):
        o.append(lab(x, 316 + j * 116, e(k), INK, 40, mono=True))
        o.append(lab(x, 372 + j * 116, e(d), SUB, 28))
o.append(hair(L, 820, 1728))
o.append(lab(L, 850, "치기 전에 어디인지 보고, 친 뒤에 잘 됐는지 봐요.", INK, 36))
o.append(lab(L, 912, "대시 하나는 한 글자(-h), 대시 둘은 단어(--help). 헷갈리면 --help.", SUB, 30))
W("cheatsheet", o, "오늘 본 내용을 세 묶음으로 모았어요. 어디에 있는지는 pwd, ls, git status로 보고, cd 네 가지로 옮겨 다녀요. 막히면 --help나 -h로 도움말을 봐요. 설명서 화면이 열리면 q로 나와요. 수업 중에 터미널이 이상하면 이 장을 띄워 두고 위에서부터 하나씩 쳐 봐요.")

# ---------- toc (page numbers from ORDER) ----------
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
tr_path = os.path.join(OUT, "trouble.html")
with open(tr_path) as f:
    s = f.read()
with open(tr_path, "w") as f:
    f.write(s.replace("PG_INIT", f"{page['init-fix']}쪽 순서"))
parts = [(BL, "탐색기와 터미널 맞춰 보기", "더블클릭, 위로, 뒤로, 홈과 cd", "sync0", "open"),
         (GR, "위치가 맞아야 명령이 동작해요", "같은 명령 다른 결과, 확인 습관, git status", "same-uv", "prompt"),
         (PUR, "이름에 담긴 관례", "명령 이름, -h와 --help, origin과 main", "names", "push-read"),
         (OR, "도움말로 스스로 찾기", "Usage 읽기, git과 uv 도움말, q로 나오기", "usage", "find")]
t = [f'<section id="toc" data-transition="fade" style="background:{BG};color:{INK};font-family:{SANS};word-break:keep-all;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:{L}px;top:80px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>']
for i, (c, h_, s_, a, b) in enumerate(parts, 1):
    y = 230 + (i - 1) * 160
    t.append(hair(L, y, 1728))
    t.append(lab(L, y + 30, str(i), c, 72, weight=900))
    t.append(lab(L + 130, y + 30, h_, INK, 40))
    t.append(lab(L + 130, y + 92, e(s_), SUB, 28))
    t.append(lab(L + 1428, y + 50, f"{page[a]}–{page[b]}쪽", GRAY, 32, w=300, align="right"))
t.append(hair(L, 230 + 4 * 160, 1728))
t.append(lab(L, 920, f"{page['why']}쪽은 들어가기, {page['trouble']}–{page['cheatsheet']}쪽은 막힐 때 보는 표와 한 장 요약이에요.", SUB, 28))
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(t) + f"\n<aside>{e('번외 자료라서 정해진 진도는 없어요. 터미널에서 자주 길을 잃으면 1, 2파트를, 명령을 자꾸 잊으면 3, 4파트를 봐요. 1파트는 01의 폴더 이동을 탐색기와 나란히 다시 보는 거예요.')}</aside>\n</section>\n")

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-10-31T09:00:00Z"}, "lists": "css", "title": "터미널 환경에 적응하기", "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
print(len(ORDER), "slides")
