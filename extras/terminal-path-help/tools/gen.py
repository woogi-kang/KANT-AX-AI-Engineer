"""Generates every slide of the extra deck "터미널에서 길 잃지 않기" and slides/deck.json.

Story: the explorer window (Finder, Windows Explorer) and the terminal move in sync through
~/kant (hello-uv from 09, team-intro from 06). Then the same command run in the right and the
wrong folder, the check habit (pwd, ls, git status), the naming conventions behind -h, --help,
origin and main, and how to read help for ls, git and uv.
Terminal output comes from tools/demo.sh (real bash, git 2.43, uv 0.11.32).
Usage: python3 tools/gen.py slides
"""
import html, json, os, sys

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
INK, SUB, LINE, CARD = "#1D2330", "#4A5262", "#E1DED6", "#FFFFFF"
BL, GR, OR, PUR, RED, NAVY, TEAL, GRAY = "#2459C9", "#1F8A4C", "#B26A00", "#5A3BB8", "#A33131", "#1E3F8F", "#0F7C86", "#6A7180"
DIR_BG, DIR_BD, DIR_TX = "#FDF1DC", "#E0A84A", "#5C3A00"
T_BG, T_PROMPT, T_CMD, T_OUT, T_ERR, T_OK, T_DIM = "#1B2029", "#8FB3FF", "#F2C46D", "#D8DEE9", "#FF9C94", "#7FD18B", "#8A93A3"


def e(s):
    return html.escape(s, quote=False)


def p(style, text, attrs=""):
    return f'<p{attrs} style="{style}">{text}</p>'


ORDER, SECTIONS = [], {}


def W(sid, parts, notes, section=None):
    if section:
        SECTIONS[section[0]] = {"description": section[1], "start": sid}
    ORDER.append(sid)
    with open(os.path.join(OUT, sid + ".html"), "w") as f:
        f.write("\n".join(parts) + f"\n<aside>{e(notes)}</aside>\n</section>\n")


def sec(sid, transition="fade", bg="#F6F5F1"):
    return f'<section id="{sid}" data-transition="{transition}" style="background:{bg};color:{INK};font-family:{SANS};font-variant-ligatures:none;word-break:keep-all;padding:96px;display:flex;flex-direction:column">'


def head(eyebrow, title, color):
    return [p(f"position:absolute;left:96px;top:48px;width:1728px;font-size:26px;font-weight:700;color:{color}", e(eyebrow), ' id="eyebrow"'),
            f'<h2 id="title" style="position:absolute;left:96px;top:92px;width:1728px;font-size:56px;font-weight:700;line-height:1.2;color:{INK}">{title}</h2>']


def caption(text, top=944):
    return p(f"position:absolute;left:96px;top:{top}px;width:1728px;font-size:34px;font-weight:700;line-height:1.4;color:{INK}", text, ' id="caption" data-build-in="rise"')


def num(i, color, size=56, extra=""):
    return p(f"width:{size + 16}px;height:{size + 16}px;flex:none;border-radius:50%;background:{color};color:#FFFFFF;font-size:{size * 0.6:.0f}px;font-weight:900;line-height:{size + 16}px;text-align:center;{extra}", str(i))


def code(text, color=INK, size=28, bg="#ECEAE3"):
    return f'<span style="font-family:{MONO};font-size:{size}px;font-weight:700;color:{color};background:{bg};border-radius:8px;padding:2px 12px;white-space:nowrap">{e(text)}</span>'


def box(inner, left, top, w, h, attrs="", border=LINE, top_color=None, bg=CARD, pad="28px 32px", gap=14, extra=""):
    bt = f"border-top:10px solid {top_color};" if top_color else ""
    return (f'<div{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:{bg};border:2px solid {border};{bt}'
            f'border-radius:20px;padding:{pad};display:flex;flex-direction:column;gap:{gap}px;{extra}">' + inner + '</div>')


# ---------- terminal ----------
def tline(l, size):
    kind = l[0]
    st = f"font-size:{size}px;line-height:1.45;white-space:pre;"
    if kind == "$":
        return p(st + f"color:{T_CMD}", f'<span style="color:{T_PROMPT}">{e(l[1])} $</span> {e(l[2])}')
    if kind == "r":
        return p(st + f"color:{T_OUT}", l[1])
    if kind == "m":
        t = l[1].replace("\t", "    ")
        tag = (f'<span style="display:inline-block;width:{size + 6}px;height:{size + 6}px;border-radius:50%;background:{l[3]};color:#FFFFFF;font-family:{SANS};font-size:{size * 0.7:.0f}px;font-weight:900;line-height:{size + 6}px;text-align:center;margin-left:14px">{l[2]}</span>') if l[2] else ""
        return p(st + f"color:{T_OUT};background:rgba(242,196,109,.16);border-radius:6px;margin:0 -10px;padding:0 10px", e(t) + tag)
    col = {"o": T_OUT, "e": T_ERR, "g": T_OK, "d": T_DIM, "y": T_CMD}[kind]
    t = l[1].replace("\t", "    ")
    return p(st + f"color:{col}", e(t) if t else "&#160;")


def term(lines, left, top, w, h, tid="term", size=26, attrs="", title=None):
    o = [f'<div id="{tid}"{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:{T_BG};border-radius:20px;padding:20px 28px;display:flex;flex-direction:column;gap:2px;font-family:{MONO};overflow:hidden">',
         '<div style="display:flex;flex-direction:row;gap:10px;align-items:center;padding:0 0 12px 0">'
         '<div style="width:16px;height:16px;border-radius:8px;background:#F28B82"></div><div style="width:16px;height:16px;border-radius:8px;background:#F2C46D"></div><div style="width:16px;height:16px;border-radius:8px;background:#7FD18B"></div>'
         + (p(f"margin-left:14px;font-family:{SANS};font-size:20px;font-weight:700;color:{T_DIM}", e(title)) if title else "") + '</div>']
    o += [tline(l, size) for l in lines]
    o.append('</div>')
    return "".join(o)


# ---------- explorer window (Finder / Windows Explorer, simplified) ----------
def folder_glyph(w=58, h=44):
    return (f'<div style="position:relative;width:{w}px;height:{h}px;flex:none">'
            f'<div style="position:absolute;left:0;top:0;width:{w * 0.45:.0f}px;height:12px;background:{DIR_BD};border-radius:5px 5px 0 0"></div>'
            f'<div style="position:absolute;left:0;top:8px;width:{w}px;height:{h - 8}px;background:{DIR_BD};border-radius:6px"></div></div>')


def file_glyph(w=40, h=50):
    return f'<div style="width:{w}px;height:{h}px;flex:none;background:#FFFFFF;border:3px solid #B4B9C3;border-radius:6px 16px 6px 6px"></div>'


BTNS = [("back", "←"), ("fwd", "→"), ("up", "↑"), ("home", "⌂")]


def explorer(path, items, left, top, w, h, press=None, pick=None, fid="finder"):
    o = [f'<div id="{fid}" style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:{CARD};border:2px solid #D9D5CB;border-radius:20px;display:flex;flex-direction:column;overflow:hidden">']
    bar = ['<div style="height:76px;flex:none;background:#ECEAE3;display:flex;flex-direction:row;align-items:center;gap:10px;padding:0 20px">']
    for k, g in BTNS:
        on = press == k
        bar.append(p(f"width:52px;height:46px;flex:none;border-radius:10px;font-size:28px;font-weight:700;line-height:46px;text-align:center;"
                     f"color:{'#FFFFFF' if on else SUB};background:{OR if on else '#FFFFFF'};border:2px solid {OR if on else '#D9D5CB'}", g))
    crumbs = f' <span style="color:{GRAY}">›</span> '.join(e(c) for c in path)
    bar.append(p(f"flex:1;margin-left:10px;font-family:{MONO};font-size:24px;font-weight:700;color:{INK};background:#FFFFFF;border-radius:10px;padding:6px 16px;white-space:nowrap;overflow:hidden", crumbs))
    bar.append('</div>')
    o += bar
    o.append('<div style="flex:1;display:flex;flex-direction:row;flex-wrap:wrap;align-content:flex-start;gap:18px 14px;padding:30px 28px">')
    for name in items:
        is_dir = "." not in name
        sel = pick == name
        o.append(f'<div style="width:196px;height:118px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;border-radius:14px;'
                 f'background:{"#FDE7C2" if sel else "transparent"};border:2px solid {OR if sel else "transparent"}">'
                 + (folder_glyph() if is_dir else file_glyph())
                 + p(f"font-size:22px;font-weight:700;color:{INK};white-space:nowrap", e(name)) + '</div>')
    o.append('</div></div>')
    return "".join(o)


# ---------- folder map with the "현재 위치" pin ----------
MAP = [("kim", "kim/", 0, "~ 홈 폴더"), ("desk", "Desktop/", 1, ""), ("docs", "Documents/", 1, ""), ("kant", "kant/", 1, ""),
       ("hello", "hello-uv/", 2, "09에서 만든 폴더"), ("team", "team-intro/", 2, "06에서 clone한 폴더")]
M_ROW0, M_PITCH = 112, 84


def folder_map(left, top, w, h, here, prev=None, tint=None, title="폴더 지도", rows=MAP):
    o = [f'<div id="map" style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:#FDFCF9;border:2px solid #D9D5CB;border-radius:20px"></div>',
         p(f"position:absolute;left:{left + 32}px;top:{top + 22}px;width:400px;font-size:24px;font-weight:700;color:{GRAY}", e(title), ' id="map-title"')]
    ys = {}
    for i, (k, lab, d, note) in enumerate(rows):
        ys[k] = top + M_ROW0 + i * M_PITCH
    if tint:
        o.append(f'<div id="tint" style="position:absolute;left:{left + 16}px;top:{ys[tint] - 14}px;width:{w - 32}px;height:{(len(rows)) * M_PITCH - 6}px;background:#FBE4E2;border:3px dashed {RED};border-radius:16px"></div>')
    if prev:
        o.append(f'<div id="pin-prev" style="position:absolute;left:{left + 16}px;top:{ys[prev] - 10}px;width:{w - 32}px;height:76px;border:3px dashed {OR};border-radius:14px"></div>')
        o.append(p(f"position:absolute;left:{left + w - 200}px;top:{ys[prev] + 8}px;width:168px;font-size:22px;font-weight:700;text-align:center;color:{OR};background:#FDF1DC;border-radius:10px;padding:4px 0", "방금 전", ' id="prev-tag"'))
    if here:
        o.append(f'<div id="pin" style="position:absolute;left:{left + 16}px;top:{ys[here] - 10}px;width:{w - 32}px;height:76px;background:#E3ECFD;border:3px solid {BL};border-radius:14px"></div>')
        o.append(p(f"position:absolute;left:{left + w - 200}px;top:{ys[here] + 8}px;width:168px;font-size:22px;font-weight:700;text-align:center;color:#FFFFFF;background:{BL};border-radius:10px;padding:4px 0", "현재 위치", ' id="pin-tag"'))
    for i, (k, lab, d, note) in enumerate(rows):
        x = left + 36 + d * 56
        y = ys[k]
        if d:
            o.append(f'<div id="lv-{k}" style="position:absolute;left:{x - 30}px;top:{y - 30}px;width:3px;height:58px;background:#CFCABF"></div>')
            o.append(f'<div id="lh-{k}" style="position:absolute;left:{x - 30}px;top:{y + 26}px;width:24px;height:3px;background:#CFCABF"></div>')
        o.append(f'<div id="n-{k}" style="position:absolute;left:{x}px;top:{y}px;height:56px;background:{DIR_BG};border:2px solid {DIR_BD};border-radius:12px;padding:0 16px;display:flex;flex-direction:row;gap:12px;align-items:center">'
                 f'<div style="width:26px;height:20px;background:{DIR_BD};border-radius:4px"></div>'
                 + p(f"font-family:{MONO};font-size:26px;font-weight:700;white-space:nowrap;color:{DIR_TX}", e(lab)) + '</div>')
        if note:
            o.append(p(f"position:absolute;left:{x + 40 + len(lab) * 16 + 50}px;top:{y + 12}px;width:280px;font-size:22px;font-weight:700;color:{GRAY}", e(note), f' id="note-{k}"'))
    return o


# ---------- real output (tools/demo.sh) ----------
OUT_LS = {"kim": "Desktop  Documents  kant", "kant": "hello-uv  team-intro", "hello": "README.md  main.py  pyproject.toml"}
GIT_FATAL = "fatal: not a git repository (or any of the parent directories): .git"
UV_FAIL = ["error: Failed to spawn: `main.py`", "  Caused by: No such file or directory (os error 2)"]
STATUS_CLEAN = ["On branch main", "Your branch is up to date with 'origin/main'.", "", "nothing to commit, working tree clean"]
STATUS_KIM = ["On branch main", "Your branch is up to date with 'origin/main'.", "", "Untracked files:",
              '  (use "git add <file>..." to include in what will be committed)', "\tkim.md", "",
              'nothing added to commit but untracked files present (use "git add" to track)']

# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#F2B27A;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 번외</p>',
       '<h1 style="font-size:100px;font-weight:900;line-height:1.15;color:#F6F5F1">터미널에서<br>길 잃지 않기</h1>',
       '<p style="font-size:40px;line-height:1.4;color:#BFC6D4">지금 위치 확인하는 습관과<br>-h, --help로 도움 받기</p>']
cov.append(term([("$", "~/kant", "pwd"), ("o", "/home/kim/kant"), ("$", "~/kant", "ls"), ("o", OUT_LS["kant"]), ("$", "~/kant", "uv --help"), ("o", "An extremely fast Python package manager.")],
                1060, 330, 740, 420, tid="cov-term", size=26))
W("cover", cov, "정규 챕터에 들어가지 않는 번외 자료예요. 수업에서 터미널이 낯설다는 이야기가 많아서 두 가지를 모았어요. 첫째, 터미널에서 지금 위치를 왜 계속 확인해야 하는지. 둘째, 명령을 잊었을 때 -h와 --help로 스스로 찾는 법이에요. 01 터미널 기초를 본 뒤라면 언제 봐도 돼요. git 장면은 02와 06, uv 장면은 09에서 만든 폴더를 그대로 써요.", ("intro", "들어가기"))

ORDER.append("toc")   # written last, after page numbers are known

# ---------- why: the explorer shows, the terminal has to be asked ----------
o = [sec("why")] + head("들어가기", "탐색기는 위치를 그림으로, 터미널은 글자로 보여 줘요", INK)
o.append(p(f"position:absolute;left:96px;top:220px;width:820px;font-size:28px;font-weight:700;color:{OR}", "탐색기 · 창을 보면 바로 알아요"))
o.append(explorer(["kim", "kant"], ["hello-uv", "team-intro"], 96, 270, 820, 420))
o.append(p(f"position:absolute;left:1004px;top:220px;width:820px;font-size:28px;font-weight:700;color:{BL}", "터미널 · 물어봐야 알려 줘요"))
o.append(term([("$", "~/kant", "")], 1004, 270, 820, 420, tid="why-term"))
asks = [("프롬프트", "$ 앞의 글자가 지금 위치"), ("pwd", "전체 경로를 한 줄로"), ("ls", "이 폴더 안에 든 것")]
for i, (k, d) in enumerate(asks):
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:{1004 + i * 280}px;top:720px;width:260px;height:150px;background:{CARD};border:2px solid {LINE};border-top:10px solid {BL};border-radius:18px;padding:18px 22px;display:flex;flex-direction:column;gap:8px">'
             + p(f"font-family:{MONO if k != '프롬프트' else SANS};font-size:30px;font-weight:700;color:{INK}", e(k)) + p(f"font-size:22px;line-height:1.4;color:{SUB}", e(d)) + '</div>')
o.append(caption("둘은 같은 폴더를 보고 있어요. 터미널은 화면에 안 보일 뿐이에요.", 920))
W("why", o, "왼쪽 탐색기(Mac은 Finder, Windows는 파일 탐색기)는 지금 열린 폴더와 안에 든 것을 그림으로 보여 줘요. 오른쪽 터미널도 똑같이 kant 폴더 안에 서 있지만 그림이 없어요. 그래서 터미널에서는 프롬프트, pwd, ls로 물어봐야 해요. 이번 자료의 첫 부분은 탐색기에서 하던 일을 터미널 명령과 하나씩 맞춰 보는 거예요. 탐색기 그림은 Mac과 Windows를 단순하게 섞어 그렸어요.")

# ---------- part 1: explorer and terminal in sync ----------
EB1 = "1. 탐색기와 터미널 맞춰 보기"
SYNC = [
    ("sync0", "터미널을 열면 홈 폴더에서 시작해요", ["kim"], "kim", None, None, None,
     [("$", "~", "pwd"), ("o", "/home/kim"), ("$", "~", "ls"), ("o", OUT_LS["kim"])],
     "탐색기에서 홈 폴더를 연 것과 같아요.",
     "터미널을 열면 홈 폴더에서 시작해요. 탐색기로 치면 홈 폴더 창을 연 상태예요. 탐색기 창의 Desktop, Documents, kant가 ls 결과와 똑같아요. 슬라이드는 Linux 기준이라 /home/kim이에요. Mac은 /Users/내이름, Windows Git Bash는 /c/Users/내이름이에요."),
    ("sync1", "폴더 더블클릭 = cd kant", ["kim", "kant"], "kant", None, "kant", None,
     [("$", "~", "pwd"), ("o", "/home/kim"), ("$", "~", "cd kant"), ("$", "~/kant", "ls"), ("o", OUT_LS["kant"])],
     "탐색기에서 들어간 폴더와 터미널의 프롬프트가 같이 바뀌어요.",
     "탐색기에서 kant 폴더를 더블클릭하면 창이 kant 안으로 바뀌어요. 터미널에서는 cd kant가 같은 일을 해요. 프롬프트 앞부분이 ~ 에서 ~/kant로 바뀐 것을 짚어 주세요. ls 결과 hello-uv, team-intro는 탐색기 창에 보이는 두 폴더와 같아요."),
    ("sync2", "한 칸 더 들어가기 = cd hello-uv", ["kim", "kant", "hello-uv"], "hello", None, "hello-uv", None,
     [("$", "~", "cd kant"), ("$", "~/kant", "ls"), ("o", OUT_LS["kant"]), ("$", "~/kant", "cd hello-uv"), ("$", "~/kant/hello-uv", "ls"), ("o", OUT_LS["hello"])],
     "주소 줄의 kim › kant › hello-uv가 pwd의 /home/kim/kant/hello-uv예요.",
     "hello-uv는 09에서 uv init으로 만든 폴더예요. 탐색기 주소 줄의 kim › kant › hello-uv와 터미널의 ~/kant/hello-uv는 같은 길을 다르게 적었을 뿐이에요. 점으로 시작하는 .venv, .gitignore는 탐색기도 ls도 기본으로 숨겨요. 01에서 본 ls -a로 보여요."),
    ("sync3", "위 폴더로(↑) = cd ..", ["kim", "kant"], "kant", None, None, "up",
     [("$", "~/kant", "cd hello-uv"), ("$", "~/kant/hello-uv", "ls"), ("o", OUT_LS["hello"]), ("$", "~/kant/hello-uv", "cd .."), ("$", "~/kant", "pwd"), ("o", "/home/kim/kant")],
     "..은 한 칸 위 폴더예요. 01에서 본 기호예요.",
     "Windows 탐색기의 위쪽 화살표, Mac Finder의 Cmd+↑가 cd ..과 같아요. 한 칸 위 폴더인 kant로 올라갔어요. 지도에서 현재 위치가 한 줄 위로 올라간 것을 보여 주세요."),
    ("sync4", "뒤로(←) = cd -", ["kim", "kant", "hello-uv"], "hello", "kant", None, "back",
     [("$", "~/kant/hello-uv", "cd .."), ("$", "~/kant", "pwd"), ("o", "/home/kim/kant"), ("$", "~/kant", "cd -"), ("o", "/home/kim/kant/hello-uv")],
     "cd -는 바로 전에 있던 폴더로 돌아가고, 간 곳을 한 줄 알려 줘요.",
     "탐색기의 뒤로 버튼은 바로 전에 보던 폴더로 돌아가요. 터미널에서는 cd 뒤에 빼기 기호 하나(cd -)를 쳐요. cd -는 돌아간 곳의 전체 경로를 한 줄 출력해요. 출력은 tools/demo.sh에서 실제로 실행한 결과예요. 위로(..)와 뒤로(-)는 달라요. 위로는 지도에서 한 칸 위, 뒤로는 내가 방금 있던 곳이에요."),
    ("sync5", "앞으로(→) = 한 번 더 cd -", ["kim", "kant"], "kant", "hello", None, "fwd",
     [("$", "~/kant", "cd -"), ("o", "/home/kim/kant/hello-uv"), ("$", "~/kant/hello-uv", "cd -"), ("o", "/home/kim/kant")],
     "터미널에는 앞으로 버튼이 따로 없어요. cd -를 다시 치면 두 폴더를 오가요.",
     "탐색기는 뒤로와 앞으로를 여러 번 기억하지만, 터미널의 cd -는 바로 전 한 곳만 기억해요. 그래서 cd -를 계속 치면 두 폴더 사이를 왔다 갔다 해요. 두 폴더를 번갈아 가며 작업할 때 편해요."),
    ("sync6", "홈으로(⌂) = cd ~", ["kim"], "kim", None, None, "home",
     [("$", "~/kant", "cd -"), ("o", "/home/kim/kant"), ("$", "~/kant", "cd ~"), ("$", "~", "pwd"), ("o", "/home/kim")],
     "어디에 있든 cd ~ 한 번이면 홈 폴더로 돌아와요.",
     "Mac Finder 사이드바의 홈, Windows 탐색기 주소 줄의 사용자 이름 폴더가 cd ~와 같아요. 01에서 배운 cd ~예요. 길을 잃으면 cd ~로 홈에 돌아온 뒤 다시 cd로 들어가요."),
]
for i, (sid, title, path, here, prev, pick, press, lines, cap, notes) in enumerate(SYNC):
    o = [sec(sid, "magic" if i else "fade")] + head(EB1, e(title), BL)
    items = OUT_LS[here].split("  ")
    o.append(p(f"position:absolute;left:96px;top:196px;width:860px;font-size:24px;font-weight:700;color:{OR}", "탐색기", ' id="lb-ex"'))
    o.append(explorer(path, items, 96, 236, 860, 340, press=press))
    o.append(p(f"position:absolute;left:96px;top:600px;width:860px;font-size:24px;font-weight:700;color:{BL}", "터미널", ' id="lb-term"'))
    o.append(term(lines, 96, 636, 860, 296, size=24))
    o += folder_map(1004, 196, 820, 724, here, prev)
    if pick:
        o.append(p(f"position:absolute;left:560px;top:190px;width:396px;font-size:22px;font-weight:700;text-align:right;color:{OR}", "더블클릭 = cd " + e(pick), ' data-build-in="pop order 1"'))
    o.append(caption(e(cap), 952))
    W(sid, o, notes, ("sync", "탐색기와 터미널 맞춰 보기") if i == 0 else None)

o = [sec("match")] + head(EB1, "탐색기 버튼과 터미널 명령 짝 맞추기", BL)
pairs = [("폴더 더블클릭", "cd 폴더이름", "들어가기"), ("↑ 위 폴더", "cd ..", "한 칸 위로"), ("← 뒤로", "cd -", "바로 전 폴더로"),
         ("→ 앞으로", "cd -", "한 번 더 치면 두 폴더를 오가요"), ("⌂ 홈", "cd ~", "홈 폴더로"), ("주소 줄 보기", "pwd", "지금 위치 전체")]
for i, (a_, b_, c_) in enumerate(pairs):
    y = 216 + i * 112
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:96px;top:{y}px;width:1728px;height:96px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:0 36px;display:flex;flex-direction:row;align-items:center;gap:30px">'
             + p(f"width:420px;flex:none;font-size:30px;font-weight:700;color:{OR}", e(a_))
             + f'<x-shape kind="arrow-right" style="width:56px;height:36px;background:#C9CED8"></x-shape>'
             + p(f"width:460px;flex:none;font-family:{MONO};font-size:32px;font-weight:700;color:{BL}", e(b_))
             + p(f"flex:1;font-size:26px;color:{SUB}", e(c_)) + '</div>')
o.append(caption("ls는 탐색기 창 안을 보는 것과 같아요. 그림이 없으니 자주 쳐서 확인해요.", 908))
W("match", o, "앞 장면을 한 장에 모았어요. 탐색기 버튼마다 같은 일을 하는 터미널 명령이 있어요. 탐색기는 창이 늘 열려 있어서 안이 보이지만, 터미널은 ls를 쳐야 보여요. 주소 줄에 해당하는 것이 pwd예요. 처음에는 탐색기를 옆에 띄워 두고 같이 움직여 보면 감이 빨리 와요.")

o = [sec("open")] + head(EB1, "탐색기와 터미널을 같은 폴더에서 열기", BL)
cards = [("터미널 → 탐색기", "지금 터미널 위치를 탐색기 창으로 열어요", [("Mac", "open ."), ("Windows Git Bash", "explorer .")], "점(.)은 지금 폴더예요"),
         ("탐색기 → 터미널", "탐색기에서 보던 폴더에서 터미널을 열어요", [("Mac", "폴더 오른쪽 클릭 › 서비스 › 폴더에서 새로운 터미널 열기"), ("Windows", "폴더 빈 곳 오른쪽 클릭 › Open Git Bash here")], "Windows 11은 추가 옵션 표시를 먼저 눌러요"),
         ("VS Code", "폴더를 연 뒤 터미널을 열면 그 폴더에서 시작해요", [("Windows", "Ctrl+`"), ("Mac", "control+`")], "백틱(`)은 숫자 1 왼쪽 키예요")]
for i, (t, d, rows, foot) in enumerate(cards):
    x = 96 + i * 584
    inner = (p(f"font-size:32px;font-weight:700;color:{INK}", e(t)) + p(f"font-size:24px;line-height:1.45;color:{SUB}", e(d))
             + "".join('<div style="display:flex;flex-direction:column;gap:6px;margin-top:6px">' + p(f"font-size:22px;font-weight:700;color:{GRAY}", e(k))
                       + p(f"font-family:{MONO if v.isascii() else SANS};font-size:{30 if v.isascii() else 24}px;font-weight:700;line-height:1.4;color:{BL}", e(v)) + '</div>' for k, v in rows)
             + '<div style="flex:1"></div>' + p(f"font-size:22px;color:{GRAY}", e(foot)))
    o.append(box(inner, x, 216, 560, 620, f' data-build-in="rise order {i + 1}"', top_color=BL))
o.append(caption("둘을 같은 폴더에 띄워 두고, 터미널에서 만든 파일이 탐색기에 생기는지 봐요.", 900))
W("open", o, "open .은 Mac에서, explorer .은 Windows Git Bash에서 지금 폴더를 탐색기 창으로 열어요. 점은 01에서 배운 지금 폴더예요. 반대로 탐색기에서 보던 폴더에서 터미널을 바로 열 수도 있어요. Mac은 Finder에서 폴더를 오른쪽 클릭하고 서비스 메뉴를 봐요. 메뉴가 없으면 시스템 설정의 키보드 단축키에서 켜요. Windows는 Git을 설치할 때 Open Git Bash here 메뉴가 같이 생겨요. VS Code는 연 폴더에서 터미널이 시작돼서 위치를 덜 헷갈려요. 이 명령들은 출력이 없고 창만 열려요.")

# ---------- part 2: the folder decides what a command does ----------
EB2 = "2. 위치가 맞아야 명령이 동작해요"


def two_terms(left_lines, right_lines, ltitle, rtitle, h=330, top=250, lcolor=RED, rcolor=GR):
    o = [p(f"position:absolute;left:96px;top:{top - 50}px;width:840px;font-size:28px;font-weight:700;color:{lcolor}", ltitle),
         term(left_lines, 96, top, 840, h, tid="t-left", size=24),
         p(f"position:absolute;left:984px;top:{top - 50}px;width:840px;font-size:28px;font-weight:700;color:{rcolor}", rtitle, ' data-build-in="fade order 1"'),
         term(right_lines, 984, top, 840, h, tid="t-right", size=24, attrs=' data-build-in="rise order 1"')]
    return o


o = [sec("same-uv")] + head(EB2, "같은 uv run main.py, 폴더에 따라 결과가 달라요", GR)
o += two_terms([("$", "~/kant", "pwd"), ("o", "/home/kim/kant"), ("$", "~/kant", "uv run main.py")] + [("e", l) for l in UV_FAIL],
               [("$", "~/kant/hello-uv", "ls"), ("o", "README.md  main.py  pyproject.toml"), ("$", "~/kant/hello-uv", "uv run main.py"), ("g", "Hello from hello-uv!")],
               "kant에서 · main.py가 없어요", "hello-uv에서 · main.py가 있어요")
o.append(box(p(f"font-size:30px;font-weight:700;color:{INK}", "명령 뒤의 파일 이름은 지금 폴더에서 찾아요")
             + p(f"font-size:26px;line-height:1.5;color:{SUB}", "main.py는 hello-uv 안에 있어요. kant에서 치면 uv가 main.py를 못 찾아요.<br>No such file or directory가 보이면 먼저 pwd와 ls를 쳐요."),
             96, 640, 1728, 200, ' data-build-in="rise order 2"', top_color=GR))
o.append(caption("명령이 틀린 게 아니라 서 있는 폴더가 틀렸어요.", 900))
W("same-uv", o, "같은 명령을 두 폴더에서 쳤어요. kant에는 main.py가 없어서 uv가 Failed to spawn, No such file or directory를 보여 줘요. hello-uv로 들어가서 치면 09에서 본 Hello from hello-uv!가 나와요. 출력은 tools/demo.sh에서 실제로 실행한 결과예요. 이런 에러를 보면 명령을 고치기 전에 pwd와 ls로 위치부터 봐요.", ("cwd", "위치가 맞아야 명령이 동작해요"))

o = [sec("same-git")] + head(EB2, "git status도 저장소 폴더 안에서만 동작해요", GR)
o += two_terms([("$", "~/kant", "git status")] + [("e", "fatal: not a git repository"), ("e", "(or any of the parent directories): .git")],
               [("$", "~/kant/team-intro", "git status")] + [("o", l) for l in STATUS_CLEAN],
               "kant에서 · 저장소 밖", "team-intro에서 · 저장소 안", h=260)
climb = [("kant/", "없음"), ("kim/", "없음"), ("home/", "없음"), ("/", "없음")]
o.append(p(f"position:absolute;left:96px;top:556px;width:840px;font-size:26px;font-weight:700;color:{INK}", "git이 .git 폴더를 찾는 길", ' data-build-in="fade order 2"'))
for i, (f_, r_) in enumerate(climb):
    x = 96 + i * 214
    o.append(f'<div data-build-in="rise order {i + 2}" style="position:absolute;left:{x}px;top:610px;width:180px;height:120px;background:{CARD};border:2px solid {LINE};border-radius:16px;padding:12px 18px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px">'
             + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{DIR_TX}", e(f_)) + p(f"font-size:22px;font-weight:700;color:{RED}", ".git " + r_) + '</div>')
    if i < 3:
        o.append(f'<x-shape kind="arrow-right" data-build-in="fade order {i + 2}" style="position:absolute;left:{x + 184}px;top:654px;width:26px;height:30px;background:#C9CED8"></x-shape>')
o.append(box(p(f"font-size:28px;font-weight:700;color:{INK}", "team-intro/.git")
             + p(f"font-size:24px;line-height:1.5;color:{SUB}", "clone한 폴더 안에는 숨김 폴더 .git이 있어요. 그 안이나 그 아래 폴더에서는 git 명령이 동작해요."),
             984, 556, 840, 174, ' data-build-in="rise order 6"', top_color=GR))
o.append(caption("parent directories는 위 폴더들이에요. 끝까지 올라가도 .git이 없다는 뜻이에요.", 900))
W("same-git", o, "git은 지금 폴더에서 .git이라는 숨김 폴더를 찾고, 없으면 한 칸씩 위로 올라가며 찾아요. 맨 위 / 까지 가도 없으면 not a git repository (or any of the parent directories)라고 말해요. 화면 폭 때문에 에러를 두 줄로 나눠 적었어요. 실제로는 한 줄이에요. team-intro는 06에서 clone해서 .git이 있어요. 그래서 team-intro 안이나 그 아래 폴더에서 git status가 동작해요. 에러가 나면 cd로 저장소 폴더에 들어가요.")

o = [sec("wrong-init")] + head(EB2, "엉뚱한 곳에서 git init을 치면", RED)
o.append(term([("$", "~", "pwd"), ("o", "/home/kim"), ("$", "~", "git init"), ("o", "Initialized empty Git repository in /home/kim/.git/"),
               ("$", "~", "git status"), ("o", "On branch main"), ("o", ""), ("o", "No commits yet"), ("o", ""), ("o", "Untracked files:"),
               ("o", '  (use "git add <file>..." to include in what will be committed)'), ("e", "\t.gitconfig"), ("e", "\tDesktop/"), ("e", "\tDocuments/"), ("e", "\tkant/")],
              96, 200, 1000, 700, tid="t-init", size=24))
o += folder_map(1140, 200, 684, 610, "kim", tint="kim", title="홈 폴더 전체가 저장소가 됐어요")
o.append(box(p(f"font-size:26px;font-weight:700;color:{RED}", "이럴 때 의심해요") + p(f"font-size:23px;line-height:1.5;color:{SUB}", "홈 폴더 프롬프트에 (main)이 보여요<br>VS Code에 바뀐 파일이 수천 개 떠요"),
             1140, 834, 684, 150, ' data-build-in="rise order 1"', border="#E07A7A", bg="#FBF1F0", pad="18px 28px", gap=6))
W("wrong-init", o, "02에서 git init은 프로젝트 폴더 안에서 쳤어요. 실수로 홈 폴더에서 치면 홈 폴더 전체가 저장소가 돼요. git status를 치면 Desktop, Documents까지 모두 Untracked로 나와요. 출력은 tools/demo.sh가 만든 연습용 홈 폴더에서 실제로 실행한 결과라 목록이 짧아요. 실제 컴퓨터에서는 훨씬 길어요. 그 아래 모든 폴더에서 git status가 동작해서, 저장소가 아닌 폴더인데도 에러가 안 나요. Windows Git Bash는 저장소 안이면 프롬프트에 (main)을 붙여서 홈 폴더에 (main)이 보이면 이 경우예요. 다음 장에서 되돌려요.")

o = [sec("init-fix")] + head(EB2, "홈 폴더의 .git만 지우면 돌아와요", RED)
steps = [("pwd", "/home/kim", "홈 폴더인지 먼저 확인해요"), ("ls -a", ".  ..  .git  .gitconfig  Desktop  Documents  kant", "숨김 폴더 .git이 보여요"),
         ("rm -rf .git", "", "홈 폴더의 .git 하나만 지워요"), ("git status", GIT_FATAL, "이제 홈 폴더는 저장소가 아니에요")]
for i, (c_, out, d) in enumerate(steps):
    y = 210 + i * 170
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:96px;top:{y}px;width:1728px;height:150px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:0 32px;display:flex;flex-direction:row;align-items:center;gap:30px">'
             + num(i + 1, RED, 40)
             + f'<div style="width:1140px;flex:none;height:110px;background:{T_BG};border-radius:14px;padding:14px 24px;display:flex;flex-direction:column;justify-content:center;gap:4px;font-family:{MONO}">'
             + tline(("$", "~", c_), 24) + (tline(("e" if out.startswith("fatal") else "o", out), 22) if out else "") + '</div>'
             + p(f"flex:1;font-size:26px;font-weight:700;line-height:1.4;color:{INK}", e(d)) + '</div>')
o.append(caption("rm -rf 뒤에는 꼭 .git만 적어요. 점 하나라도 빠지면 다른 것이 지워져요.", 912))
W("init-fix", o, "홈 폴더를 저장소로 만든 것은 .git 폴더 하나예요. 그 폴더만 지우면 원래대로 돌아와요. 1번 pwd로 홈 폴더인지 꼭 확인해요. 프로젝트 폴더에서 치면 그 프로젝트의 기록이 지워져요. 2번 ls -a는 화면 폭에 맞춰 한 줄로 옮겼어요. 3번 rm -rf .git은 출력이 없어요. 01에서 본 대로 rm -rf는 묻지 않고 지우니 .git을 정확히 적어요. 4번처럼 not a git repository가 나오면 정상이에요. 그 아래의 kant/team-intro는 자기 .git이 있어서 그대로 저장소예요. 혼자 하기 불안하면 강사에게 화면을 보여 주고 같이 해요.")

o = [sec("habit")] + head(EB2, "치기 전에 보고, 친 뒤에 다시 봐요", GR)
cyc = [("어디?", "프롬프트, pwd", BL), ("무엇이?", "ls", BL), ("명령 치기", "cd, uv run, git add", OR), ("잘 됐나?", "ls, git status", GR)]
for i, (t, d, c) in enumerate(cyc):
    x = 96 + i * 444
    o.append(f'<div data-build-in="pop order {i + 1}" style="position:absolute;left:{x}px;top:240px;width:396px;height:400px;background:{CARD};border:2px solid {LINE};border-top:10px solid {c};border-radius:22px;padding:34px 30px;display:flex;flex-direction:column;align-items:center;gap:22px">'
             + f'<div style="width:130px;height:130px;flex:none;border-radius:50%;background:{c};display:flex;align-items:center;justify-content:center">' + p("font-size:56px;font-weight:900;color:#FFFFFF", str(i + 1)) + '</div>'
             + p(f"font-size:38px;font-weight:700;color:{INK};white-space:nowrap", e(t))
             + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{c};white-space:nowrap", e(d)) + '</div>')
    if i < 3:
        o.append(f'<x-shape kind="arrow-right" data-build-in="fade order {i + 2}" style="position:absolute;left:{x + 400}px;top:420px;width:40px;height:44px;background:#C9CED8"></x-shape>')
o.append(f'<div data-build-in="fade order 5" style="position:absolute;left:290px;top:640px;width:1338px;height:110px;border:5px dashed #C9CED8;border-top:none;border-radius:0 0 40px 40px"></div>')
o.append(p(f"position:absolute;left:660px;top:770px;width:600px;font-size:28px;font-weight:700;text-align:center;color:{GRAY}", "다음 명령도 1부터", ' data-build-in="fade order 5"'))
o.append(caption("명령이 바꾼 것은 화면에 안 보여요. 그래서 친 뒤에 한 번 더 봐요.", 900))
W("habit", o, "터미널 작업은 이 네 단계를 돌아요. 1번 프롬프트나 pwd로 어디에 있는지 보고, 2번 ls로 안에 무엇이 있는지 봐요. 3번 명령을 치고, 4번 ls나 git status로 결과가 내가 바란 대로인지 봐요. 탐색기는 파일이 생기면 바로 보이지만 터미널은 아무 말도 안 하는 명령이 많아요. cd, mkdir, git add는 성공해도 출력이 없어요. 그래서 4번에서 확인하는 습관이 필요해요. 4번을 마치면 다음 명령도 다시 1번부터 돌아요.")

o = [sec("status-read")] + head(EB2, "git status는 네 가지를 알려 줘요", GR)
SL = [("m", STATUS_KIM[0], 1, GR), ("m", STATUS_KIM[1], 2, GR), ("o", ""), ("m", STATUS_KIM[3], 3, GR), ("m", STATUS_KIM[4], 4, GR), ("o", STATUS_KIM[5]), ("o", ""),
      ("o", "nothing added to commit but untracked files present"), ("o", '(use "git add" to track)')]
o.append(term([("$", "~/kant/team-intro", 'echo "# kim" > kim.md'), ("$", "~/kant/team-intro", "git status")] + SL, 96, 200, 1100, 560, tid="t-status", size=24))
labels = [("지금 이름표", "main 브랜치에 있어요"), ("GitHub과 비교", "마지막 fetch 기준이에요"), ("바뀐 파일", "kim.md는 아직 Git이 몰라요"), ("다음 할 일 힌트", "git add로 올리라고 알려 줘요")]
for i, (lab, d) in enumerate(labels):
    y = 200 + i * 140
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:1240px;top:{y}px;width:584px;height:122px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:0 24px;display:flex;flex-direction:row;align-items:center;gap:18px">'
             + num(i + 1, GR, 34) + '<div style="flex:1;display:flex;flex-direction:column;gap:4px">' + p(f"font-size:28px;font-weight:700;color:{INK}", e(lab)) + p(f"font-size:22px;color:{SUB}", e(d)) + '</div></div>')
o.append(caption("모르겠으면 git status. 지금 상태와 다음에 칠 명령을 같이 알려 줘요.", 820))
W("status-read", o, "06에서 clone한 team-intro에 kim.md를 하나 만들고 git status를 쳤어요. 출력은 tools/demo.sh에서 실제로 실행한 결과예요. 1번 On branch main은 지금 main 이름표에 있다는 뜻이에요. 2번은 내 컴퓨터가 기억하는 origin/main과 비교한 결과예요. GitHub의 최신 상태는 git fetch origin을 해야 반영돼요. 3번 Untracked는 02에서 본 새 파일 상태예요. 4번 괄호 안은 다음에 칠 명령 힌트예요. 마지막 줄은 화면 폭 때문에 두 줄로 나눠 적었어요. git status는 아무것도 바꾸지 않으니 몇 번을 쳐도 괜찮아요.")

o = [sec("prompt")] + head(EB2, "프롬프트에서 위치 읽기", GR)
pr = [("Mac 터미널 (zsh)", [("kim@MacBook-Air hello-uv %", "")], [("kim@MacBook-Air", "나@컴퓨터"), ("hello-uv", "지금 폴더 이름만"), ("%", "입력 자리")], "폴더 이름만 보여서 전체 경로는 pwd로 봐요"),
      ("Windows Git Bash", [("kim@DESKTOP MINGW64 ~/kant/team-intro (main)", ""), ("$", "")], [("~/kant/team-intro", "홈에서부터 경로"), ("(main)", "저장소 안이면 이름표"), ("$", "입력 자리")], "(main)이 보이면 git 명령이 동작하는 폴더예요")]
for i, (t, lines, parts, foot) in enumerate(pr):
    y = 200 + i * 380
    o.append(p(f"position:absolute;left:96px;top:{y}px;width:1728px;font-size:28px;font-weight:700;color:{INK}", e(t)))
    o.append(f'<div data-build-in="rise order {i * 2 + 1}" style="position:absolute;left:96px;top:{y + 50}px;width:1728px;height:{70 + 40 * len(lines)}px;background:{T_BG};border-radius:18px;padding:20px 32px;display:flex;flex-direction:column;gap:4px;font-family:{MONO}">'
             + "".join(p(f"font-size:30px;line-height:1.3;white-space:pre;color:{T_PROMPT}", e(l)) for l, _ in lines) + '</div>')
    o.append(f'<div data-build-in="rise order {i * 2 + 2}" style="position:absolute;left:96px;top:{y + 70 + 70 + 40 * len(lines)}px;width:1728px;display:flex;flex-direction:row;gap:20px;align-items:center">'
             + "".join('<div style="display:flex;flex-direction:row;gap:10px;align-items:center;background:#FFFFFF;border:2px solid ' + LINE + ';border-radius:14px;padding:8px 18px">'
                       + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{BL};white-space:nowrap", e(a_)) + p(f"font-size:26px;color:{SUB};white-space:nowrap", e(b_)) + '</div>' for a_, b_ in parts)
             + '</div>')
    o.append(p(f"position:absolute;left:96px;top:{y + 70 + 70 + 40 * len(lines) + 76}px;width:1728px;font-size:26px;font-weight:700;color:{GR}", e(foot), f' data-build-in="fade order {i * 2 + 2}"'))
W("prompt", o, "프롬프트는 운영체제와 설정마다 모양이 달라요. 위는 Mac 기본 터미널(zsh)의 모양 예시예요. 지금 폴더 이름 하나만 보여서 같은 이름의 폴더가 여러 개면 헷갈려요. 그럴 땐 pwd를 쳐요. 아래는 Windows Git Bash 예시예요. 두 줄로 나오고 첫 줄에 홈에서부터 경로가 보여요. 저장소 안이면 괄호 안에 지금 이름표가 붙어요. 컴퓨터 이름은 사람마다 달라요. 이 자료의 다른 장은 01처럼 ~/kant $ 모양으로 줄여서 보여 줘요.")

# ---------- part 3: why these names ----------
EB3 = "3. 이름에 담긴 관례"
o = [sec("names")] + head(EB3, "명령 이름은 영어 단어를 줄인 거예요", PUR)
nm = [("pwd", "print working directory", "지금 폴더 출력"), ("ls", "list", "목록"), ("cd", "change directory", "폴더 바꾸기"), ("mkdir", "make directory", "폴더 만들기"),
      ("mv", "move", "옮기기"), ("cp", "copy", "복사"), ("rm", "remove", "지우기"), ("cat", "concatenate", "이어 붙여 보여 주기")]
for i, (c_, en, ko) in enumerate(nm):
    x, y = 96 + (i % 4) * 438, 210 + (i // 4) * 320
    o.append(box(p(f"font-family:{MONO};font-size:52px;font-weight:700;color:{PUR}", e(c_)) + p(f"font-family:{MONO};font-size:24px;color:{INK}", e(en))
                 + '<div style="flex:1"></div>' + p(f"font-size:28px;font-weight:700;color:{SUB}", e(ko)),
                 x, y, 414, 290, f' data-build-in="rise order {i // 4 + 1}"', top_color=PUR))
o.append(caption("뜻을 알면 외우지 않아도 떠올라요. 처음 보는 명령도 뜻부터 찾아봐요.", 900))
W("names", o, "01에서 쓴 명령 이름은 모두 영어 단어의 앞 글자나 줄임말이에요. pwd는 print working directory, 지금 작업 중인 폴더를 출력한다는 뜻이에요. 디렉터리(directory)는 폴더를 부르는 다른 이름이에요. cat은 원래 여러 파일을 이어 붙여 보여 주는 명령이라 이런 이름이 붙었어요. git과 uv도 git add, uv add처럼 영어 동사를 명령 이름으로 써요.", ("names", "이름에 담긴 관례"))

o = [sec("dash")] + head(EB3, "대시 하나는 한 글자, 대시 둘은 단어", PUR)
o.append(p(f"position:absolute;left:96px;top:206px;width:500px;font-size:26px;font-weight:700;color:{GRAY}", "짧은 이름"))
o.append(p(f"position:absolute;left:640px;top:206px;width:600px;font-size:26px;font-weight:700;color:{GRAY}", "긴 이름"))
o.append(p(f"position:absolute;left:1300px;top:206px;width:524px;font-size:26px;font-weight:700;color:{GRAY}", "--help에 적힌 줄"))
dd = [("ls -a", "ls --all", "-a, --all"), ("uv -h", "uv --help", "-h, --help"), ("git commit -m", "git commit --message", "-m, --[no-]message")]
for i, (s_, l_, src) in enumerate(dd):
    y = 256 + i * 150
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:96px;top:{y}px;width:1728px;height:126px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:0 32px;display:flex;flex-direction:row;align-items:center">'
             + p(f"width:512px;flex:none;font-family:{MONO};font-size:34px;font-weight:700;color:{PUR}", e(s_))
             + p(f"width:660px;flex:none;font-family:{MONO};font-size:34px;font-weight:700;color:{BL}", e(l_))
             + p(f"flex:1;font-family:{MONO};font-size:24px;color:{SUB};background:#F1F0EC;border-radius:10px;padding:6px 16px", e(src)) + '</div>')
o.append(box('<div style="display:flex;flex-direction:row;align-items:center;gap:40px">'
             + p(f"font-size:30px;font-weight:700;color:{INK}", "한 글자 옵션은 붙여 써요")
             + code("ls -al", PUR, 34) + p(f"font-size:34px;font-weight:700;color:{GRAY}", "=") + code("ls -a -l", PUR, 34)
             + p(f"flex:1;font-size:24px;color:{SUB}", "01에서 쓴 ls -al이 이 모양이에요") + '</div>',
             96, 730, 1728, 140, ' data-build-in="rise order 4"', pad="0 36px", extra="justify-content:center"))
o.append(caption("짧은 이름은 치기 편하고, 긴 이름은 읽기 쉬워요. 뜻은 같아요.", 920))
W("dash", o, "옵션은 명령 뒤에 붙어서 동작을 조금 바꾸는 말이에요. 대시 하나 뒤에는 한 글자, 대시 둘 뒤에는 단어 전체를 적는 것이 오래된 약속이에요. 오른쪽은 각 도구의 도움말에 실제로 적힌 줄이에요. 짧은 이름과 긴 이름을 쉼표로 나란히 적어 둬요. git의 --[no-]message는 --message와 --no-message를 같이 적은 표기예요. 한 글자 옵션은 ls -al처럼 대시 하나 뒤에 여러 개를 붙일 수 있어요. 긴 이름은 붙일 수 없어요.")

o = [sec("common")] + head(EB3, "여러 도구에서 자주 만나는 옵션", PUR)
cm = [("-h  --help", "help", "도움말 보기"), ("--version", "version", "버전 보기"), ("-m", "message", "메시지 적기", "git commit -m"), ("-r", "recursive", "폴더 안까지 전부", "rm -r"),
      ("-f", "force", "묻지 않고 강제로", "rm -rf"), ("-a", "all", "숨긴 것까지 전부", "ls -a"), ("-q", "quiet", "출력 줄이기"), ("-v", "verbose", "출력 자세히")]
for i, row in enumerate(cm):
    o_, en, ko = row[:3]
    ex = row[3] if len(row) > 3 else ""
    x, y = 96 + (i % 4) * 438, 210 + (i // 4) * 320
    o.append(box(p(f"font-family:{MONO};font-size:{40 if len(o_) < 8 else 32}px;font-weight:700;color:{PUR};white-space:pre", e(o_)) + p(f"font-family:{MONO};font-size:24px;color:{INK}", e(en))
                 + p(f"font-size:28px;font-weight:700;color:{SUB}", e(ko)) + '<div style="flex:1"></div>'
                 + (p(f"font-size:22px;color:{GRAY}", "예: " + code(ex, BL, 22)) if ex else ""),
                 x, y, 414, 290, f' data-build-in="rise order {i // 4 + 1}"', top_color=PUR))
o.append(caption("대부분 이 뜻이지만 도구마다 다를 수 있어요. 다음 장에서 예외를 봐요.", 900))
W("common", o, "여러 도구가 같은 글자에 같은 뜻을 붙이는 경우가 많아요. 그래서 처음 보는 도구도 --help, --version은 거의 다 통해요. -m은 git commit -m의 message, -r은 rm -r의 recursive(안쪽까지 되풀이), -f는 rm -rf의 force예요. -q는 quiet(조용히), -v는 verbose(자세히)예요. 이 표는 외울 표가 아니라 이런 약속이 있다는 것만 알면 돼요.")

o = [sec("except")] + head(EB3, "관례는 약속일 뿐이라 예외가 있어요", PUR)
ex = [("ls -h", [("$", "~/kant/hello-uv", "ls -h"), ("o", "README.md  pyproject.toml"), ("o", "main.py    uv.lock")], "ls의 -h는 help가 아니에요", "크기를 K, M처럼 읽기 쉽게(human-readable) 보여 주는 옵션이에요. 도움말은 ls --help예요."),
      ("git -v · uv -V", [("$", "~", "git -v"), ("o", "git version 2.43.0"), ("$", "~", "uv -V"), ("o", "uv 0.11.32 (x86_64-unknown-linux-gnu)")], "버전 글자가 달라요", "git은 -v, uv는 대문자 -V예요. uv의 소문자 -v는 verbose예요. 둘 다 --version은 같아요."),
      ("Mac의 ls --help", [], "Mac 기본 ls는 --help를 몰라요", "Mac은 man ls로 설명서를 봐요. 나올 땐 q예요. Windows Git Bash는 ls --help가 돼요.")]
for i, (t, lines, h_, d) in enumerate(ex):
    x = 96 + i * 584
    inner = (p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{PUR}", e(t))
             + (f'<div style="height:180px;flex:none;background:{T_BG};border-radius:14px;padding:16px 20px;display:flex;flex-direction:column;gap:2px;font-family:{MONO}">' + "".join(tline(l, 20) for l in lines) + '</div>'
                if lines else f'<div style="height:180px;flex:none;background:#F1F0EC;border-radius:14px;padding:16px 20px;display:flex;flex-direction:column;justify-content:center;gap:10px">'
                + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{INK}", "man ls") + p(f"font-size:20px;color:{GRAY}", "manual(설명서)의 줄임말") + '</div>')
             + p(f"font-size:28px;font-weight:700;color:{INK}", e(h_)) + p(f"font-size:23px;line-height:1.5;color:{SUB}", e(d)))
    o.append(box(inner, x, 210, 560, 640, f' data-build-in="rise order {i + 1}"', top_color=PUR))
o.append(caption("헷갈리면 긴 이름 --help부터 쳐 봐요. 가장 많이 통해요.", 900))
W("except", o, "ls -h는 도움말이 아니라 human-readable 옵션이라 그냥 목록이 나와요. ls -lh처럼 -l과 같이 쓸 때 파일 크기를 4.0K처럼 보여 줘요. 버전 글자도 도구마다 달라요. git은 -v와 --version이 같고, uv는 대문자 -V와 --version이 같아요. 출력은 tools/demo.sh에서 실제로 실행한 결과예요. ls -h는 상자 폭에 맞게 좁은 터미널(ls -C -w 40)에서 실행한 모양이에요. Mac 기본 ls, cp, mv는 --help를 몰라서 에러와 짧은 사용법만 보여 줘요. 이때는 man 명령으로 설명서를 열어요. Mac 출력은 이 자료를 만든 환경에서 실행할 수 없어서 옮기지 않았어요.")

o = [sec("origin-main")] + head(EB3, "origin과 main도 관례로 붙인 이름이에요", PUR)
om = [("origin", "원래(origin) 가져온 곳", [("$", "~/kant/team-intro", "git remote -v"), ("o", "origin\thttps://github.com/kim/team-intro.git (fetch)"), ("o", "origin\thttps://github.com/kim/team-intro.git (push)")],
       ["02 · git remote add origin 주소로 직접 붙였어요", "06 · clone하면 git이 origin으로 붙여 줘요"], "#5A3BB8"),
      ("main", "주된 줄기, 첫 브랜치 이름", [("$", "~/kant/team-intro", "git branch"), ("o", "* main")],
       ["02 · init.defaultBranch main으로 정했어요", "예전 기본 이름은 master, 지금 GitHub은 main"], BL)]
for i, (t, d, lines, facts, c) in enumerate(om):
    x = 96 + i * 876
    inner = ('<div style="display:flex;flex-direction:row;align-items:baseline;gap:20px">' + p(f"font-family:{MONO};font-size:48px;font-weight:700;color:{c}", e(t)) + p(f"font-size:28px;font-weight:700;color:{SUB}", e(d)) + '</div>'
             + f'<div style="height:150px;flex:none;background:{T_BG};border-radius:14px;padding:16px 22px;display:flex;flex-direction:column;gap:2px;font-family:{MONO}">' + "".join(tline(l, 20) for l in lines) + '</div>'
             + "".join(p(f"font-size:24px;line-height:1.5;color:{INK}", "• " + e(f_)) for f_ in facts))
    o.append(box(inner, x, 210, 852, 480, f' data-build-in="rise order {i + 1}"', top_color=c))
o.append(box(p(f"font-size:30px;font-weight:700;color:{INK}", "바꿀 수 있는 이름이지만 모두 같은 이름을 써요")
             + p(f"font-size:24px;line-height:1.5;color:{SUB}", "그래서 검색한 글, 에러 메시지, 팀원의 명령을 그대로 따라 칠 수 있어요."),
             96, 720, 1728, 160, ' data-build-in="rise order 3"', pad="24px 36px"))
o.append(caption("git이 정한 명령이 아니라 사람들이 맞춘 이름이에요.", 920))
W("origin-main", o, "origin은 영어로 출처, 원래 온 곳이라는 뜻이에요. 02에서는 git remote add origin 주소로 이 이름을 직접 붙였고, 06에서 clone할 때는 git이 자동으로 origin이라고 붙였어요. main은 첫 브랜치의 이름이에요. git의 예전 기본 이름은 master였고, GitHub은 2020년부터 새 저장소의 기본 이름을 main으로 바꿨어요. 02에서 init.defaultBranch main을 설정한 이유예요. 출력은 tools/demo.sh의 team-intro에서 실제로 실행한 결과예요. 이름을 바꿀 수는 있지만, 모두 같은 이름을 쓰면 자료와 에러 메시지를 그대로 따라 할 수 있어요.")

o = [sec("push-read")] + head(EB3, "git push origin main을 도움말로 읽어 봐요", PUR)
o.append(p(f"position:absolute;left:96px;top:214px;width:1728px;font-size:26px;font-weight:700;color:{GRAY}", "git push -h 첫 줄 (실제 출력)"))
o.append(f'<div style="position:absolute;left:96px;top:262px;width:1728px;height:120px;background:{T_BG};border-radius:18px;padding:0 40px;display:flex;flex-direction:row;align-items:center;font-family:{MONO}">'
         + p(f"font-size:40px;white-space:pre;color:{T_OUT}", 'usage: git push [&lt;options&gt;] [<span style="color:#C7B6FF;font-weight:700">&lt;repository&gt;</span> [<span style="color:#8FB3FF;font-weight:700">&lt;refspec&gt;</span>...]]') + '</div>')
o.append(f'<div data-build-in="rise order 1" style="position:absolute;left:96px;top:420px;width:1728px;height:120px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:0 40px;display:flex;flex-direction:row;align-items:center;gap:0;font-family:{MONO}">'
         + p(f"font-size:48px;font-weight:700;white-space:pre;color:{INK}", f'git push <span style="color:{PUR}">origin</span> <span style="color:{BL}">main</span>') + '</div>')
for i, (w_, slot, d, c) in enumerate([("origin", "<repository>", "어디로 · 원격 이름", PUR), ("main", "<refspec>", "무엇을 · 브랜치 이름", BL)]):
    o.append(box('<div style="display:flex;flex-direction:row;align-items:center;gap:18px">' + code(w_, c, 34) + p(f"font-size:30px;font-weight:700;color:{GRAY}", "=")
                 + code(slot, c, 30, "#F1F0EC") + '</div>' + p(f"font-size:28px;font-weight:700;color:{c}", e(d)),
                 96 + i * 876, 570, 852, 124, f' data-build-in="rise order {i + 2}"', pad="14px 32px", gap=8, extra="justify-content:center"))
o.append(box(p(f"font-size:28px;line-height:1.5;color:{INK}", "도움말의 <b>&lt;repository&gt;</b> 자리에 origin, <b>&lt;refspec&gt;</b> 자리에 main을 넣은 거예요.<br>git pull origin main도 같은 순서예요."),
             96, 720, 1728, 150, ' data-build-in="rise order 4"', pad="0 36px", extra="justify-content:center"))
o.append(caption("우리 과정은 이 두 칸을 매번 끝까지 적어요.", 920))
W("push-read", o, "git push -h를 치면 맨 위에 사용법 한 줄이 나와요. 꺾쇠 안의 repository는 원격 저장소 이름, refspec은 보낼 브랜치를 가리키는 자리예요. 우리가 매일 치는 git push origin main은 이 자리에 origin과 main을 넣은 거예요. 대괄호는 다음 파트에서 봐요. 우리 과정에서는 이 두 칸을 생략하지 않고 매번 적어요. 그래야 어디로 무엇을 보내는지 눈으로 확인할 수 있어요. 옵션 목록은 길어서 첫 줄만 옮겼어요.")

# ---------- part 4: reading help ----------
EB4 = "4. 도움말로 스스로 찾기"
o = [sec("usage")] + head(EB4, "Usage 줄의 기호 네 가지", OR)
sym = [("[ ]", "넣어도 되고 빼도 돼요"), ("< >", "내 값으로 바꿔 적어요"), ("...", "여러 개 적을 수 있어요"), ("|", "둘 중 하나만 골라요")]
for i, (s_, d) in enumerate(sym):
    x = 96 + i * 438
    o.append(box(p(f"font-family:{MONO};font-size:56px;font-weight:700;color:{OR}", e(s_)) + p(f"font-size:28px;font-weight:700;line-height:1.4;color:{INK}", e(d)),
                 x, 200, 414, 220, f' data-build-in="rise order {i + 1}"', top_color=OR))
ex2 = [("ls --help", "Usage: ls [OPTION]... [FILE]...", ["ls", "ls -a", "ls -a -l notes"], "옵션도 파일도 없어도 돼요"),
       ("uv add -h", "Usage: uv add [OPTIONS] <PACKAGES|--requirements <REQUIREMENTS>>", ["uv add fastapi"], "패키지 이름은 꼭 넣어요")]
for i, (c_, u, tries, d) in enumerate(ex2):
    y = 470 + i * 220
    o.append(f'<div data-build-in="rise order {i + 5}" style="position:absolute;left:96px;top:{y}px;width:1728px;height:196px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:22px 32px;display:flex;flex-direction:column;gap:14px">'
             + '<div style="display:flex;flex-direction:row;align-items:center;gap:20px">' + p(f"font-size:22px;font-weight:700;color:{GRAY};width:150px;flex:none", e(c_))
             + f'<div style="flex:1;background:{T_BG};border-radius:12px;padding:10px 20px">' + p(f"font-family:{MONO};font-size:26px;white-space:pre;color:{T_OUT}", e(u)) + '</div></div>'
             + '<div style="display:flex;flex-direction:row;align-items:center;gap:16px;padding-left:170px">' + p(f"font-size:22px;font-weight:700;color:{OR}", "이렇게 쳐요")
             + "".join(code(t, BL, 26) for t in tries) + p(f"flex:1;text-align:right;font-size:22px;color:{SUB}", e(d)) + '</div></div>')
W("usage", o, "도움말 맨 위의 Usage(사용법) 줄은 명령을 어떤 순서로 적는지 보여 줘요. 대괄호는 생략할 수 있는 자리, 꺾쇠는 내 값으로 바꾸는 자리예요. 점 세 개는 여러 개를 적을 수 있다는 뜻이고, 세로 막대는 둘 중 하나예요. 대문자 OPTION, FILE은 그 자리에 무엇이 들어가는지 이름만 적은 거예요. ls의 사용법은 전부 대괄호라서 ls만 쳐도 돼요. uv add는 꺾쇠라서 패키지 이름을 꼭 적어요. 두 Usage 줄은 tools/demo.sh에서 실제로 실행한 출력이에요. 앞 장의 git push 사용법도 같은 기호예요.", ("help", "도움말로 스스로 찾기"))

o = [sec("options")] + head(EB4, "옵션 목록은 이름, 이름, 설명 순서예요", OR)
LSH = ["Usage: ls [OPTION]... [FILE]...", "List information about the FILEs (the current directory by default).", "Sort entries alphabetically if none of -cftuvSUX nor --sort is specified.", "",
       "Mandatory arguments to long options are mandatory for short options too.", "  -a, --all                  do not ignore entries starting with .",
       "  -A, --almost-all           do not list implied . and ..", "      --author               with -l, print the author of each file"]
HLA = (f'  <span style="color:#C7B6FF;font-weight:700;background:rgba(199,182,255,.2);border-radius:6px">-a</span>, '
       f'<span style="color:#8FB3FF;font-weight:700;background:rgba(143,179,255,.2);border-radius:6px">--all</span>                  '
       f'<span style="color:{T_CMD};font-weight:700;background:rgba(242,196,109,.18);border-radius:6px">do not ignore entries starting with .</span>')
LL = [("o", l) for l in LSH]
LL[5] = ("r", HLA)
o.append(term([("$", "~", "ls --help")] + LL + [("d", "…")], 96, 200, 1728, 470, tid="t-lshelp", size=24))
parts3 = [("-a", "짧은 이름", PUR), ("--all", "긴 이름", BL), ("do not ignore entries starting with .", "설명 · 점으로 시작하는 것도 빼지 않아요", OR)]
for i, (a_, b_, c) in enumerate(parts3):
    x = 96 + [0, 360, 720][i]
    w = [336, 336, 1008][i]
    o.append(box(p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{c};white-space:nowrap", e(a_)) + p(f"font-size:24px;color:{SUB}", e(b_)),
                 x, 710, w, 140, f' data-build-in="rise order {i + 2}"', pad="20px 26px", gap=8))
o.append(caption("01에서 쓴 ls -a가 목록 맨 위에 있어요.", 900))
W("options", o, "ls --help의 앞부분이에요. tools/demo.sh에서 실제로 실행한 출력이고 뒤는 길어서 줄였어요. Usage 아래에 한두 줄 설명이 나오고, 그 아래부터 옵션 목록이에요. 한 줄에 짧은 이름, 긴 이름, 설명이 차례로 있어요. -a, --all 줄은 점으로 시작하는 파일을 숨기지 않는다는 뜻이에요. 01에서 ls -a로 .git, .venv 같은 숨김 파일을 본 게 이 옵션이에요. 설명은 영어지만 짧아서 번역기에 넣어도 돼요. 출력이 길어서 위가 잘리면 터미널을 위로 스크롤해요.")

o = [sec("git-help")] + head(EB4, "git은 도움말을 세 가지로 보여 줘요", OR)
gh = [("git --help", "자주 쓰는 명령 목록", "명령 이름이 기억나지 않을 때", "터미널에 바로"),
      ("git 명령 -h", "그 명령의 짧은 옵션표", "옵션 글자가 기억나지 않을 때", "터미널에 바로"),
      ("git 명령 --help", "그 명령의 설명서 전체", "자세한 설명과 예시가 필요할 때", "Mac은 설명서 화면, Windows는 브라우저")]
for i, (c_, a_, w_, where) in enumerate(gh):
    x = 96 + i * 584
    o.append(box(p(f"font-family:{MONO};font-size:34px;font-weight:700;color:{OR}", e(c_)) + p(f"font-size:30px;font-weight:700;color:{INK}", e(a_))
                 + p(f"font-size:24px;line-height:1.5;color:{SUB}", e(w_)) + '<div style="flex:1"></div>'
                 + p(f"font-size:22px;font-weight:700;color:{GRAY};background:#F1F0EC;border-radius:10px;padding:8px 14px", e(where)),
                 x, 210, 560, 420, f' data-build-in="rise order {i + 1}"', top_color=OR))
o.append(box('<div style="display:flex;flex-direction:row;align-items:center;gap:26px">' + p(f"font-size:28px;font-weight:700;color:{INK}", "예")
             + code("git commit -h", BL, 30) + p(f"font-size:26px;color:{SUB}", "짧게") + code("git commit --help", BL, 30) + p(f"font-size:26px;color:{SUB}", "자세히")
             + code("git help commit", BL, 30) + p(f"font-size:26px;color:{SUB}", "--help와 같아요") + '</div>',
             96, 670, 1728, 140, ' data-build-in="rise order 4"', pad="0 36px", extra="justify-content:center"))
o.append(caption("git에서는 -h와 --help가 달라요. 처음엔 -h부터 쳐요.", 900))
W("git-help", o, "git은 -h와 --help를 다르게 써요. git 명령 -h는 터미널에 옵션표를 짧게 바로 보여 줘요. git 명령 --help는 그 명령의 설명서 전체를 열어요. Mac과 Linux는 터미널 안에 설명서 화면이 열리고, Windows Git Bash는 브라우저에 설명서 웹 페이지가 열려요. git help commit은 git commit --help와 같아요. 명령 이름 자체가 기억나지 않으면 git --help로 목록부터 봐요.")

GITH = ["usage: git [-v | --version] [-h | --help] [-C <path>] [-c <name>=<value>]", "           …", "", "These are common Git commands used in various situations:", "",
        "start a working area (see also: git help tutorial)", "   clone     Clone a repository into a new directory", "   init      Create an empty Git repository or reinitialize an existing one", "",
        "…", "", "collaborate (see also: git help workflows)", "   fetch     Download objects and refs from another repository",
        "   pull      Fetch from and integrate with another repository or a local branch", "   push      Update remote refs along with associated objects"]
o = [sec("git-list")] + head(EB4, "git --help · 명령 이름이 기억나지 않을 때", OR)
o.append(term([("$", "~", "git --help")] + [("d" if l.strip() == "…" else "o", l) for l in GITH], 96, 200, 1240, 700, tid="t-githelp", size=22))
gl = [("묶음 제목", "하는 일별로 나눠 둬요"), ("명령 이름", "왼쪽 칸"), ("한 줄 설명", "오른쪽 칸")]
for i, (a_, b_) in enumerate(gl):
    o.append(box(p(f"font-size:28px;font-weight:700;color:{INK}", e(a_)) + p(f"font-size:22px;color:{SUB}", e(b_)), 1380, 200 + i * 150, 444, 128, f' data-build-in="rise order {i + 1}"', pad="18px 26px", gap=6))
o.append(box(p(f"font-size:24px;line-height:1.5;color:{INK}", "02, 06에서 쓴 clone, init, fetch, pull, push가 다 여기 있어요."), 1380, 660, 444, 240, ' data-build-in="rise order 4"', top_color=OR))
W("git-list", o, "git --help를 치면 자주 쓰는 명령을 하는 일별로 묶어서 보여 줘요. tools/demo.sh에서 실제로 실행한 출력이고, 화면 폭 때문에 가운데 묶음 세 개를 …로 줄였어요. 줄인 곳에는 add, status, log, commit, branch, merge처럼 02부터 배운 명령이 들어 있어요. 왼쪽이 명령 이름, 오른쪽이 한 줄 설명이에요. 맨 아래에는 git help -a로 전체 명령을 볼 수 있다는 안내가 나와요.")

GITC = ["usage: git commit [-a | --interactive | --patch] [-s] [-v] [-u<mode>] [--amend]", "                  …", "", "    -q, --[no-]quiet      suppress summary after successful commit",
        "    -v, --[no-]verbose    show diff in commit message template", "", "Commit message options", "    -F, --[no-]file <file>", "                          read message from file",
        "    --[no-]author <author>", "                          override author for commit", "    --[no-]date <date>    override date for commit",
        "    -m, --[no-]message <message>", "                          commit message", "    …"]
o = [sec("git-h")] + head(EB4, "git commit -h · 옵션 글자가 기억나지 않을 때", OR)
o.append(term([("$", "~/kant/team-intro", "git commit -h")] + [("d" if l.strip() == "…" else ("m", l, "", "") if i in (12, 13) else "o", l) if i not in (12, 13) else ("m", l, "", "") for i, l in enumerate(GITC)], 96, 200, 1240, 720, tid="t-gitch", size=22))
o.append(box(p(f"font-size:26px;font-weight:700;color:{GRAY}", "찾던 줄") + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{OR}", "-m &lt;message&gt;")
             + p(f"font-size:26px;line-height:1.5;color:{INK}", "커밋 메시지를 바로 적는 옵션이에요."),
             1380, 200, 444, 300, ' data-build-in="rise order 1"', top_color=OR))
o.append(box(p(f"font-size:24px;line-height:1.5;color:{SUB}", "목록이 70줄쯤 돼요. 위가 잘리면 터미널을 위로 스크롤해요."), 1380, 540, 444, 180, ' data-build-in="rise order 2"'))
o.append(caption("-m 뒤에 &lt;message&gt;가 있으니 메시지를 꼭 붙여요.", 944))
W("git-h", o, "커밋 메시지 옵션이 기억나지 않으면 git commit -h를 쳐요. tools/demo.sh에서 실제로 실행한 출력의 앞부분이고, 사용법 줄과 뒤쪽 목록은 …로 줄였어요. Commit message options 묶음 안에 -m, --[no-]message <message>가 있어요. 꺾쇠가 붙어 있으니 -m 뒤에 메시지를 적어야 해요. 그래서 git commit -m \"docs: 소개 추가\"처럼 써요. 목록에는 처음 보는 옵션이 많아요. 지금 찾는 한 줄만 보면 돼요.")

o = [sec("pager")] + head(EB4, "설명서 화면이 열리면 q로 나와요", OR)
MAN = ["GIT-COMMIT(1)                Git Manual                GIT-COMMIT(1)", "", "NAME", "       git-commit - Record changes to the repository", "", "SYNOPSIS",
       "       git commit [-a | --interactive | --patch] [-s] [-v] [-u<mode>]", "                  …", "", "DESCRIPTION", "       Create a new commit containing the current contents of the", "       index and the given log message describing the changes. …", ""]
o.append(f'<div style="position:absolute;left:96px;top:200px;width:1100px;height:700px;background:{T_BG};border-radius:20px;padding:24px 30px;display:flex;flex-direction:column;gap:2px;font-family:{MONO}">'
         + "".join(tline(("d" if l.strip() == "…" else "o", l), 22) for l in MAN) + '<div style="flex:1"></div>'
         + p(f"font-size:22px;line-height:1.45;white-space:pre;color:{T_BG};background:{T_OUT};align-self:flex-start;padding:0 8px", " Manual page git-commit(1) line 1 (press h for help or q to quit)") + '</div>')
keys = [("Space", "다음 쪽"), ("b", "앞 쪽"), ("/단어", "단어 찾기"), ("q", "나가기")]
for i, (k, d) in enumerate(keys):
    hl = k == "q"
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:1240px;top:{200 + i * 140}px;width:584px;height:120px;background:{"#FDF1DC" if hl else CARD};border:2px solid {OR if hl else LINE};border-radius:18px;padding:0 28px;display:flex;flex-direction:row;align-items:center;gap:26px">'
             + p(f"width:170px;flex:none;font-family:{MONO};font-size:34px;font-weight:700;color:{OR};background:#FFFFFF;border:2px solid #C9CED8;border-bottom-width:5px;border-radius:10px;padding:4px 0;text-align:center", e(k))
             + p(f"font-size:30px;font-weight:700;color:{INK}", e(d)) + '</div>')
o.append(box(p(f"font-size:24px;line-height:1.5;color:{SUB}", "git log가 길 때 나오는 화면도 같아요. 화면 맨 아래에 : 이나 (END)가 보이면 q예요."), 1240, 770, 584, 130, ' data-build-in="rise order 5"', pad="16px 26px"))
W("pager", o, "Mac과 Linux에서 git commit --help나 man ls를 치면 터미널 전체가 설명서 화면으로 바뀌어요. 명령을 쳐도 반응이 없어서 멈춘 것처럼 보여요. 이 화면에서는 Space로 다음 쪽, b로 앞 쪽, 슬래시 뒤에 단어를 치고 Enter로 찾고, q로 나가요. 왼쪽 그림은 설명서 화면을 줄여 그린 거예요. 설명서 화면은 이 자료를 만든 환경에서 열 수 없어서 실제 출력을 옮기지 않았어요. Windows Git Bash는 --help가 브라우저로 열려서 이 화면이 나오지 않아요. 02에서 git log 기록이 길 때도 같은 화면이 나와요. 그때도 q예요.")

UVH = ["An extremely fast Python package manager.", "", "Usage: uv [OPTIONS] <COMMAND>", "", "Commands:", "  auth       Manage authentication", "  run        Run a command or script",
       "  init       Create a new project", "  add        Add dependencies to the project", "  remove     Remove dependencies from the project",
       "  version    Read or update the project's version", "  sync       Update the project's environment", "  lock       Update the project's lockfile",
       "  export     Export the project's lockfile to an alternate format", "  tree       Display the project's dependency tree", "  …"]
o = [sec("uv-help")] + head(EB4, "uv --help · uv 명령 목록 보기", OR)
USED = ("run", "init", "add", "remove", "sync", "tree")
UL = []
for l in UVH:
    w0 = l.split()[0] if l.strip() else ""
    UL.append(("d", l) if l.strip() == "…" else ("m", l, "", "") if w0 in USED and l.startswith("  ") else ("o", l))
o.append(term([("$", "~/kant/hello-uv", "uv --help")] + UL, 96, 200, 1240, 760, tid="t-uvhelp", size=22))
o.append(box(p(f"font-size:26px;font-weight:700;color:{INK}", "09에서 쓴 명령") + p(f"font-family:{MONO};font-size:26px;font-weight:700;line-height:1.6;color:{OR}", "run  init  add<br>remove  sync  tree"),
             1380, 200, 444, 260, ' data-build-in="rise order 1"', top_color=OR))
o.append(box(p(f"font-size:26px;font-weight:700;color:{INK}", "uv는 -h와 --help가 같아요") + p(f"font-size:22px;line-height:1.5;color:{SUB}", "더 긴 설명은 uv help 명령<br>예: uv help add"),
             1380, 500, 444, 220, ' data-build-in="rise order 2"'))
W("uv-help", o, "uv --help는 uv에서 쓸 수 있는 명령을 한 줄 설명과 함께 보여 줘요. tools/demo.sh에서 실제로 실행한 출력이고, 아래쪽 명령과 옵션은 …로 줄였어요. 노랗게 칠한 줄은 09에서 쓴 명령이에요. uv는 git과 달리 -h와 --help가 같은 짧은 도움말을 보여 줘요. 더 자세한 설명은 uv help add처럼 help 뒤에 명령 이름을 적어요. 이때는 앞에서 본 설명서 화면처럼 열릴 수 있어서 q로 나와요.")

o = [sec("typo")] + head(EB4, "오타를 내면 도구가 먼저 알려 줘요", OR)
o += two_terms([("$", "~/kant/team-intro", "git stauts"), ("e", "git: 'stauts' is not a git command. See 'git --help'."), ("o", ""), ("y", "The most similar command is"), ("y", "\tstatus")],
               [("$", "~/kant/hello-uv", "uv ad fastapi"), ("e", "error: unrecognized subcommand 'ad'"), ("o", ""), ("y", "  tip: some similar subcommands exist: 'audit', 'add'"), ("o", ""),
                ("o", "Usage: uv [OPTIONS] <COMMAND>"), ("o", ""), ("o", "For more information, try '--help'.")],
               "git stauts", "uv ad fastapi", h=420, top=250, lcolor=OR, rcolor=OR)
o.append(box(p(f"font-size:28px;font-weight:700;color:{INK}", "에러 메시지의 마지막 몇 줄을 읽어요")
             + p(f"font-size:24px;line-height:1.5;color:{SUB}", "비슷한 명령(similar command)과 --help 안내가 나와요. 노란 줄만 읽어도 고칠 수 있어요."),
             96, 710, 1728, 160, ' data-build-in="rise order 2"', pad="22px 36px"))
o.append(caption("에러는 꾸중이 아니라 힌트예요.", 920))
W("typo", o, "명령 이름을 잘못 치면 git과 uv 모두 비슷한 이름을 찾아 줘요. git stauts에는 status를, uv ad에는 audit과 add를 권해요. 출력은 tools/demo.sh에서 실제로 실행한 결과예요. 끝에는 --help를 쳐 보라는 안내도 있어요. 에러가 나면 지우고 다시 치기 전에 맨 아래 몇 줄을 소리 내어 읽어 봐요. 위 화살표로 앞 명령을 불러와 고치면 빨라요.")

o = [sec("find")] + head(EB4, "모르는 기능을 도움말로 찾아가기", OR)
o.append(box(p(f"font-size:24px;font-weight:700;color:{GRAY}", "하고 싶은 일") + p(f"font-size:32px;font-weight:700;color:{INK}", "설치한 패키지를 나무 모양으로 보고 싶어요"),
             96, 200, 1728, 130, "", pad="18px 36px", gap=6))
fl = [("uv --help", ["  tree       Display the project's dependency tree"], "명령 목록에서 tree를 찾았어요"),
      ("uv tree -h", ["Display the project's dependency tree", "", "Usage: uv tree [OPTIONS]"], "옵션이 다 대괄호라 그냥 쳐도 돼요"),
      ("uv tree", ["Resolved 1 package in 2ms", "hello-uv v0.1.0"], "패키지를 넣으면 아래로 가지가 늘어요")]
FX, FW = [96, 790, 1344], [660, 520, 480]
for i, (c_, out, d) in enumerate(fl):
    x = FX[i]
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:{x}px;top:370px;width:{FW[i]}px;height:500px;background:{CARD};border:2px solid {LINE};border-top:10px solid {OR};border-radius:20px;padding:26px 28px;display:flex;flex-direction:column;gap:18px">'
             + '<div style="display:flex;flex-direction:row;align-items:center;gap:16px">' + num(i + 1, OR, 30) + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{INK}", e(c_)) + '</div>'
             + f'<div style="height:220px;flex:none;background:{T_BG};border-radius:14px;padding:16px 20px;display:flex;flex-direction:column;gap:2px;font-family:{MONO}">'
             + "".join(tline(("o", l), 17) for l in out) + '</div>'
             + p(f"font-size:26px;font-weight:700;line-height:1.45;color:{INK}", e(d)) + '</div>')
    if i < 2:
        o.append(f'<x-shape kind="arrow-right" data-build-in="fade order {i + 2}" style="position:absolute;left:{x + FW[i] + 4}px;top:600px;width:26px;height:40px;background:{OR}"></x-shape>')
o.append(caption("목록에서 이름 찾기, -h로 쓰는 법 보기, 쳐 보기. 이 세 단계면 돼요.", 912))
W("find", o, "09에서 uv tree를 배웠지만 이름을 잊었다고 해 볼게요. 1번 uv --help 목록에서 dependency tree라는 설명을 보고 tree를 찾아요. 2번 uv tree -h로 사용법을 보면 [OPTIONS]만 있어서 옵션 없이 쳐도 돼요. 3번 실제로 쳐요. 출력은 tools/demo.sh의 hello-uv에서 실제로 실행한 결과예요. 아직 패키지가 없어서 한 줄이에요. 09처럼 fastapi를 넣었다면 그 아래로 패키지가 줄줄이 나와요. git도 같은 순서로 git --help, git 명령 -h를 보면 돼요.")

# ---------- summary ----------
EB5 = "정리"
o = [sec("trouble")] + head(EB5, "터미널에서 막히면", RED)
tr = [(GIT_FATAL[:27], "git 저장소 폴더 밖이에요", "pwd 뒤 cd 저장소"), ("error: Failed to spawn: `main.py`", "main.py가 없는 폴더예요", "ls 뒤 cd hello-uv"),
      ("No such file or directory", "위치나 이름이 틀렸어요", "pwd, ls, Tab"), ("화면이 멈추고 : 이나 (END)만 보여요", "설명서 화면이에요", "q"),
      ("홈 폴더에서 git status가 동작해요", "홈에서 git init을 쳤어요", "PG_INIT"), ("옵션이 기억나지 않아요", "도움말을 봐요", "명령 -h, --help")]
o.append('<div style="position:absolute;left:96px;top:210px;width:1728px;height:780px;display:flex;flex-direction:column;gap:14px">')
for i, (q, a_, cmd) in enumerate(tr, 1):
    mono = q.isascii()
    o.append(f'<div data-build-in="rise order {i}" style="flex:1;display:flex;flex-direction:row;gap:26px;align-items:center;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:8px 30px">'
             + num(i, RED, 36)
             + '<div style="flex:1;display:flex;flex-direction:column;gap:4px">' + p(f"{'font-family:' + MONO + ';font-size:24px;' if mono else 'font-size:27px;'}font-weight:700;color:{INK}", e(q)) + p(f"font-size:23px;color:{SUB}", e(a_)) + '</div>'
             + p(f"width:400px;flex:none;font-size:26px;font-weight:700;line-height:1.5;color:{INK};background:#EEEFF2;padding:10px 20px;border-radius:12px;white-space:nowrap", e(cmd)) + '</div>')
o.append('</div>')
W("trouble", o, "1번과 2번은 2파트에서 본 에러예요. 명령을 고치기 전에 서 있는 폴더부터 봐요. 1번은 실제로 (or any of the parent directories): .git이 뒤에 더 붙어요. 3번은 01에서 본 에러예요. 이름은 Tab으로 자동 완성하면 오타가 줄어요. 4번은 --help나 man, 긴 git log에서 열리는 설명서 화면이에요. 5번은 init-fix 장의 순서대로 홈 폴더의 .git만 지워요. 6번은 4파트에서 본 순서대로 찾아요.", ("trouble", "정리"))

o = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>']
groups = [("어디에 있나", BL, [("pwd", "지금 위치"), ("ls", "안에 든 것"), ("git status", "저장소 상태")]),
          ("옮겨 다니기", GR, [("cd 폴더", "들어가기"), ("cd ..", "한 칸 위로"), ("cd -", "바로 전 폴더"), ("cd ~", "홈 폴더")]),
          ("도움 받기", OR, [("명령 --help", "도움말"), ("git 명령 -h", "git 짧은 옵션표"), ("uv 명령 -h", "uv 도움말"), ("q", "설명서 화면 나가기")])]
for i, (t, c, rows) in enumerate(groups):
    x = 96 + i * 584
    inner = p(f"font-size:30px;font-weight:700;color:{c}", e(t)) + "".join(
        '<div style="display:flex;flex-direction:row;align-items:center;gap:18px">' + p(f"width:270px;flex:none;font-family:{MONO};font-size:28px;font-weight:700;color:{INK}", e(k)) + p(f"font-size:24px;color:{SUB}", e(d)) + '</div>' for k, d in rows)
    o.append(box(inner, x, 200, 560, 560, "", top_color=c, gap=26))
o.append(box(p(f"font-size:30px;font-weight:700;color:{INK}", "치기 전에 어디인지 보고, 친 뒤에 잘 됐는지 봐요.")
             + p(f"font-size:26px;color:{SUB}", "대시 하나는 한 글자(-h), 대시 둘은 단어(--help). 헷갈리면 --help."),
             96, 800, 1728, 190, "", pad="26px 36px", gap=12, extra="justify-content:center"))
W("cheatsheet", o, "오늘 본 내용을 세 묶음으로 모았어요. 어디에 있는지는 pwd, ls, git status로 보고, cd 네 가지로 옮겨 다녀요. 막히면 --help나 -h로 도움말을 봐요. 설명서 화면이 열리면 q로 나와요. 수업 중에 터미널이 이상하면 이 장을 띄워 두고 위에서부터 하나씩 쳐 봐요.")

# ---------- toc (page numbers from ORDER) ----------
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
tr_path = os.path.join(OUT, "trouble.html")
with open(tr_path) as f:
    s = f.read()
with open(tr_path, "w") as f:
    f.write(s.replace("PG_INIT", f"{page['init-fix']}쪽"))
parts = [("Home", BL, "탐색기와 터미널 맞춰 보기", "더블클릭, 위로, 뒤로, 홈과 cd", "sync0", "open"),
         ("Warning", GR, "위치가 맞아야 명령이 동작해요", "같은 명령 다른 결과, 확인 습관, git status", "same-uv", "prompt"),
         ("Book", PUR, "이름에 담긴 관례", "명령 이름, -h와 --help, origin과 main", "names", "push-read"),
         ("Search", OR, "도움말로 스스로 찾기", "Usage 읽기, git과 uv 도움말, q로 나오기", "usage", "find")]
t = [f'<section id="toc" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};word-break:keep-all;padding:96px 128px;display:flex;flex-direction:column;gap:40px">',
     f'<h2 style="font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>',
     '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:28px;flex:1">']
for i, (ic, c, h, s_, a, b) in enumerate(parts, 1):
    pg = f"{page[a]}–{page[b]}쪽"
    t.append(f'<div style="display:flex;flex-direction:column;gap:12px;background:#FFFFFF;border:2px solid {LINE};border-top:10px solid {c};border-radius:20px;padding:28px 32px">'
             f'<div style="display:flex;flex-direction:row;gap:14px;align-items:center"><p style="font-size:52px;font-weight:900;line-height:1.25;color:{c}">{i}</p>'
             f'<x-icon name="{ic}" style="width:44px;height:44px;color:{c}"></x-icon></div>'
             f'<h3 style="font-size:32px;font-weight:700;line-height:1.3;color:{INK}">{h}</h3>'
             f'<p style="font-size:26px;line-height:1.45;color:{SUB}">{e(s_)}</p><div style="flex:1"></div>'
             f'<p style="font-size:24px;color:#6A7180">{pg}</p></div>')
t += ['</div>', f'<p style="font-size:26px;color:{SUB}">{page["why"]}쪽은 들어가기, {page["trouble"]}–{page["cheatsheet"]}쪽은 막힐 때와 한 장 요약이에요.</p>']
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(t) + f"\n<aside>{e('번외 자료라서 정해진 진도는 없어요. 터미널에서 자주 길을 잃으면 1, 2파트를, 명령을 자꾸 잊으면 3, 4파트를 봐요. 1파트는 01의 폴더 이동을 탐색기와 나란히 다시 보는 거예요.')}</aside>\n</section>\n")

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-10-31T09:00:00Z"}, "lists": "css", "title": "터미널에서 길 잃지 않기", "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
print(len(ORDER), "slides")
