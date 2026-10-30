"""Generates every slide of the VS Code Jupyter deck and slides/deck.json.

Story: picks up hello-uv and its notebook from chapter 09, then reads the notebook screen,
runs cells three ways, watches the run number and Restart, switches between command and
edit mode, and ends with the shortcut table (Windows, Mac). Cells keep the same id across
scenes so the magic transition animates only what a key changed.
Cell output comes from tools/demo.sh (tools/run_nb.py runs the cells with the project kernel).
Usage: python3 tools/gen.py slides
"""
import html, json, os, sys

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
INK, SUB, LINE, CARD = "#1D2330", "#4A5262", "#E1DED6", "#FFFFFF"
BL, GR, OR, PUR, RED, NAVY, TEAL, GRAY = "#2459C9", "#1F8A4C", "#B26A00", "#5A3BB8", "#A33131", "#1E3F8F", "#0F7C86", "#6A7180"
JP = "#B8560F"          # Jupyter, same as chapter 09 part 7
SEL = "#2F7DE1"         # selected cell bar, like VS Code's focus color
WIN, MAC = BL, "#3D4250"


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
    return f'<section id="{sid}" data-transition="{transition}" style="background:{bg};color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">'


def head(eyebrow, title, color):
    return [p(f"position:absolute;left:96px;top:48px;width:1728px;font-size:26px;font-weight:700;color:{color}", e(eyebrow), ' id="eyebrow"'),
            f'<h2 id="title" style="position:absolute;left:96px;top:92px;width:1728px;font-size:56px;font-weight:700;line-height:1.2;color:{INK}">{title}</h2>']


def caption(text, top=944):
    return p(f"position:absolute;left:96px;top:{top}px;width:1728px;font-size:34px;font-weight:700;line-height:1.4;color:{INK}", text, ' id="caption" data-build-in="rise"')


def num(i, color, size=56, extra=""):
    return p(f"width:{size + 16}px;height:{size + 16}px;flex:none;border-radius:50%;background:{color};color:#FFFFFF;font-size:{size * 0.6:.0f}px;font-weight:900;line-height:{size + 16}px;text-align:center;{extra}", str(i))


def kbd(text, size=30, color=INK):
    """Key caps. Keys joined with + are pressed together; keys split by spaces are separate keys."""
    if " " in text:
        return '<div style="display:flex;flex-direction:row;align-items:center;gap:14px">' + "".join(kbd(t, size, color) for t in text.split()) + '</div>'
    caps = []
    for k in text.split("+"):
        caps.append(p(f"font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.2;white-space:nowrap;color:{color};background:#FFFFFF;border:2px solid #C9CED8;border-bottom-width:5px;border-radius:10px;padding:6px 14px", e(k)))
    plus = p(f"font-size:{size * 0.8:.0f}px;font-weight:700;color:{GRAY}", "+")
    return f'<div style="display:flex;flex-direction:row;align-items:center;gap:8px">' + plus.join(caps) + '</div>'


def key_pair(win, mac, size=30):
    """Windows and Mac keys side by side, labelled."""
    lab = lambda t, c: p(f"width:110px;flex:none;font-size:22px;font-weight:700;color:{c}", t)
    return ('<div style="display:flex;flex-direction:column;gap:12px">'
            + '<div style="display:flex;flex-direction:row;align-items:center;gap:12px">' + lab("Windows", WIN) + kbd(win, size) + '</div>'
            + '<div style="display:flex;flex-direction:row;align-items:center;gap:12px">' + lab("Mac", MAC) + kbd(mac, size) + '</div></div>')


# ---------- notebook mock (each cell keeps its id across scenes) ----------
LH = 38          # code line height (26px * 1.45)


def cell_h(c):
    h = 22 + LH * len(c.get("lines", [""]))
    if c.get("kind") == "mdr":
        h = 20 + sum(56 if l.startswith("# ") else LH for l in c["lines"])
    if c.get("out"):
        h += 10 + LH * len(c["out"])
    return h


def cell(c, left, top, w, sel=None, mode="cmd", pre="", attrs=""):
    """c: dict(id, kind code|md|mdr, lines, n, out, err). sel: id of the selected cell."""
    kind, lines, n = c.get("kind", "code"), c.get("lines", [""]), c.get("n")
    chosen = sel == c["id"]
    edit = chosen and mode == "edit"
    o = [f'<div id="{pre}{c["id"]}"{attrs or c.get("attrs", "")} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;display:flex;flex-direction:column;gap:10px">']
    bar = f'<div style="width:7px;flex:none;border-radius:4px;background:{SEL if chosen else "transparent"}"></div>'
    gutter = p(f"width:58px;flex:none;font-family:{MONO};font-size:20px;color:{GRAY};text-align:right;padding-top:12px", "" if kind != "code" else (f"[{n}]" if n else "[ ]"))
    if kind == "mdr":
        body = "".join(p(f"font-size:{40 if l.startswith('# ') else 26}px;font-weight:{700 if l.startswith('# ') else 400};line-height:1.4;color:{INK}",
                         e(l[2:]) if l.startswith("# ") else ("• " + e(l[2:]) if l.startswith("- ") else e(l))) for l in lines)
        box = f'<div style="flex:1;padding:6px 18px;display:flex;flex-direction:column">{body}</div>'
    else:
        bd = f"3px solid {SEL}" if edit else f"2px solid {LINE}"
        bg = "#FFFFFF" if kind == "code" else "#FAF8F3"
        txt = "".join(p(f"font-family:{MONO};font-size:26px;line-height:1.45;white-space:pre;color:{INK}", (e(l) if l else "&#160;") + ('<span style="color:' + SEL + ';font-weight:700">|</span>' if edit and i == len(lines) - 1 else ""))
                      for i, l in enumerate(lines))
        tag = p(f"position:absolute;right:14px;bottom:8px;font-size:18px;color:{GRAY}", "Python" if kind == "code" else "Markdown")
        box = f'<div style="flex:1;position:relative;background:{bg};border:{bd};border-radius:10px;padding:8px 18px 8px;display:flex;flex-direction:column">{txt}{tag}</div>'
    o.append(f'<div style="display:flex;flex-direction:row;gap:10px;align-items:stretch">{bar}{gutter}{box}</div>')
    if c.get("out"):
        col = RED if c.get("err") else INK
        o.append(''.join(p(f"margin-left:85px;padding:0 20px;font-family:{MONO};font-size:26px;line-height:1.45;white-space:pre;color:{col}", e(l)) for l in c["out"]))
    o.append('</div>')
    return o


def notebook(cells, left, top, w, sel=None, mode="cmd", pre="", bar=True, gap=22, file="notebook.ipynb", toolbar=True):
    o = []
    y = top
    if bar:
        tools = ["+ Code", "+ Markdown", "▷ Run All", "↻ Restart", "Clear All Outputs", "Variables"] if toolbar else []
        o.append(f'<div id="{pre}nb-bar" style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:64px;background:#ECEAE3;border-radius:14px;display:flex;flex-direction:row;align-items:center;padding:0 20px;gap:18px">'
                 + p(f"font-family:{MONO};font-size:22px;font-weight:700;color:{INK};white-space:nowrap", e(file))
                 + "".join(p(f"font-size:19px;color:{SUB};white-space:nowrap", e(t)) for t in tools) + '<div style="flex:1"></div>'
                 + p(f"font-size:19px;font-weight:700;color:{GR};background:#E6F4EC;border-radius:8px;padding:4px 12px;white-space:nowrap", ".venv (Python 3.14.6)") + '</div>')
        y += 88
    for c in cells:
        o += cell(c, left, y, w, sel, mode, pre)
        y += cell_h(c) + gap
    return o


# ---------- real output (tools/demo.sh, tools/run_nb.py) ----------
C_X = {"id": "c-x", "lines": ["x = 10"]}
C_P = {"id": "c-p", "lines": ["print(x * 2)"]}
C_NAME = {"id": "c-name", "lines": ['name = "kim"', 'f"안녕하세요, {name}"']}
C_INC = {"id": "c-inc", "lines": ["x = x + 1", "x"]}
NAME_ERR = "NameError: name 'x' is not defined"
SYN_ERR = "SyntaxError: invalid syntax"


def C(base, **kw):
    d = dict(base)
    d.update(kw)
    return d


# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#F2B27A;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
       '<h1 style="font-size:104px;font-weight:900;line-height:1.1;color:#F6F5F1">VS Code에서<br>Jupyter 노트북 쓰기</h1>',
       '<p style="font-size:40px;line-height:1.4;color:#BFC6D4">셀 실행하는 법과<br>자주 쓰는 단축키</p>']
cov.append(f'<div style="position:absolute;left:1100px;top:300px;width:680px;height:480px;background:#252B36;border-radius:24px;padding:44px 48px;display:flex;flex-direction:column;justify-content:center;gap:26px">')
for win, d in [("Shift+Enter", "실행하고 다음 셀로"), ("Esc", "명령 모드"), ("B", "아래에 셀 추가"), ("M", "마크다운 셀로")]:
    cov.append('<div style="display:flex;flex-direction:row;align-items:center;gap:28px">' + kbd(win, 30) + p("font-size:30px;color:#D8DEE9", d) + '</div>')
cov.append('</div>')
W("cover", cov, "09에서 VS Code에 Jupyter를 연결하고 첫 셀을 실행했어요. 이번 챕터는 노트북을 손에 익히는 시간이에요. 셀을 실행하는 세 가지 키, 셀 번호 읽는 법, 명령 모드와 편집 모드, 그리고 Windows와 Mac 단축키를 차례로 봐요.", ("intro", "들어가기"))

ORDER.append("toc")   # written last, after page numbers are known

# ---------- ready: what chapter 09 already did ----------
o = [sec("ready")] + head("들어가기", "준비는 09에서 마쳤어요", JP)
done = [("Python, Jupyter 확장 설치", "09 · 25쪽"), ("uv add --dev ipykernel", "09 · 26쪽"), ("커널로 .venv 고르기", "09 · 27쪽")]
for i, (a_, b_) in enumerate(done):
    y = 220 + i * 150
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:96px;top:{y}px;width:820px;height:126px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:0 28px;display:flex;flex-direction:row;gap:22px;align-items:center">'
             + f'<x-icon name="CheckCircle" style="width:48px;height:48px;color:{GR}"></x-icon>'
             + p(f"flex:1;{'font-family:' + MONO + ';' if a_.startswith('uv') else ''}font-size:30px;font-weight:700;color:{INK}", e(a_))
             + p(f"font-size:24px;font-weight:700;color:{GRAY};white-space:nowrap", e(b_)) + '</div>')
o.append(p(f"position:absolute;left:96px;top:690px;width:820px;font-size:26px;line-height:1.5;color:{SUB}", "셋 중 하나라도 안 했으면 09 슬라이드의 그 쪽부터 따라 해요.", ' data-build-in="fade order 3"'))
o.append(f'<div data-build-in="rise order 4" style="position:absolute;left:1000px;top:220px;width:824px;height:560px;background:{CARD};border:2px solid {LINE};border-top:10px solid {JP};border-radius:20px;padding:32px 40px;display:flex;flex-direction:column;gap:22px">'
         + p(f"font-size:32px;font-weight:700;color:{INK}", "새 노트북 만들기")
         + '<div style="display:flex;flex-direction:row;gap:18px;align-items:center">' + num(1, JP, 36) + p(f"font-size:28px;color:{INK}", "명령 팔레트 열기") + '</div>'
         + '<div style="margin-left:70px">' + key_pair("Ctrl+Shift+P", "Cmd+Shift+P", 26) + '</div>'
         + '<div style="display:flex;flex-direction:row;gap:18px;align-items:center">' + num(2, JP, 36) + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{INK}", "Create: New Jupyter Notebook") + '</div>'
         + '<div style="display:flex;flex-direction:row;gap:18px;align-items:center">' + num(3, JP, 36) + p(f"font-size:28px;color:{INK}", "저장하고 오른쪽 위 커널이 .venv인지 보기") + '</div></div>')
o.append(caption("이번 챕터는 09에서 만든 hello-uv 폴더를 VS Code로 열고 시작해요.", 880))
W("ready", o, "09의 7파트에서 확장 두 개를 설치하고, uv add --dev ipykernel로 커널을 넣고, 노트북 커널로 .venv를 골랐어요. 이 세 가지가 끝나야 셀이 실행돼요. 새 노트북은 09처럼 탐색기에서 notebook.ipynb 파일을 만들어도 되고, 명령 팔레트에서 Create: New Jupyter Notebook을 골라도 돼요. 명령 팔레트로 만들면 이름 없는 노트북이 열려서, 저장할 때 hello-uv 폴더 안에 이름을 붙여 저장해요. 새로 만들면 커널을 다시 골라야 할 수 있어요. VS Code 메뉴 글자는 버전에 따라 조금 다를 수 있어요.")

# ---------- part 1: the notebook screen ----------
EB1 = "1. 노트북 화면 읽기"
o = [sec("screen")] + head(EB1, "노트북 화면은 다섯 곳만 알면 돼요", BL)
o += notebook([C(C_X, n=1), C(C_P, n=2, out=["20"]), {"id": "c-md", "kind": "mdr", "lines": ["# 오늘 배운 것", "- 셀은 따로 실행해요"]}], 96, 220, 1160, sel="c-p")
marks = [(1, 1100, 196), (2, 300, 196), (3, 44, 396), (4, 120, 452), (5, 250, 452)]
for i, x, y in marks:
    o.append(f'<div data-build-in="pop order {i}" style="position:absolute;left:{x}px;top:{y}px">' + num(i, RED, 30, "box-shadow:0 0 0 4px #FFFFFF") + '</div>')
labels = [("커널", "셀을 실행하는 파이썬. .venv인지 봐요"), ("위쪽 버튼", "셀 추가, 전체 실행, 다시 시작"), ("선택 막대", "지금 고른 셀을 표시해요"),
          ("실행 번호", "몇 번째로 실행했는지"), ("출력", "실행 결과가 셀 바로 아래에")]
for i, (a_, b_) in enumerate(labels, 1):
    y = 220 + (i - 1) * 132
    o.append(f'<div data-build-in="rise order {i}" style="position:absolute;left:1300px;top:{y}px;width:524px;height:116px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:0 22px;display:flex;flex-direction:row;gap:18px;align-items:center">'
             + num(i, RED, 30) + '<div style="flex:1;display:flex;flex-direction:column;gap:4px">' + p(f"font-size:28px;font-weight:700;color:{INK}", a_) + p(f"font-size:21px;color:{SUB}", b_) + '</div></div>')
o.append(caption("셀은 칸이에요. 칸마다 따로 실행하고, 결과는 그 칸 아래에 남아요.", 900))
W("screen", o, "VS Code에서 노트북을 열면 보이는 화면을 단순하게 그렸어요. 1번 오른쪽 위는 커널 이름이에요. 09에서 고른 .venv가 보여야 해요. 2번 위쪽 줄에는 셀을 더하는 + Code, + Markdown과 전체 실행, 다시 시작 버튼이 있어요. 3번 셀 왼쪽의 파란 막대는 지금 고른 셀이에요. 4번 대괄호 숫자는 몇 번째로 실행했는지 보여 줘요. 실행하지 않은 셀은 비어 있어요. 5번 출력은 셀 바로 아래에 붙어요. 마지막 칸은 글을 적는 마크다운 셀이에요. 다음 장에서 봐요. 실제 화면은 VS Code 버전과 테마에 따라 색과 글자가 조금 달라요.", ("screen", "노트북 화면 읽기"))

o = [sec("kinds")] + head(EB1, "셀은 코드 셀과 마크다운 셀 두 가지예요", BL)
o.append(p(f"position:absolute;left:96px;top:210px;width:820px;font-size:32px;font-weight:700;color:{BL}", "코드 셀 · 파이썬을 실행해요"))
o += cell(C(C_NAME, n=3, out=["'안녕하세요, kim'"]), 96, 270, 820, attrs=' data-build-in="rise order 1"')
o.append(p(f"position:absolute;left:96px;top:470px;width:820px;font-size:26px;line-height:1.5;color:{SUB}", "오른쪽 아래에 Python이라고 적혀요.<br>마지막 줄이 값이면 print 없이도 보여 줘요.", ' data-build-in="fade order 1"'))
o.append(p(f"position:absolute;left:1004px;top:210px;width:820px;font-size:32px;font-weight:700;color:{JP}", "마크다운 셀 · 설명 글을 적어요"))
o += cell({"id": "m-edit", "kind": "md", "lines": ["# 오늘 배운 것", "- 셀은 따로 실행해요", "- **Shift+Enter**로 실행"]}, 1004, 270, 820, attrs=' data-build-in="rise order 2"')
o.append(f'<x-shape kind="arrow-right" data-build-in="fade order 3" style="position:absolute;left:1380px;top:440px;width:60px;height:44px;background:#C9CED8;transform:rotate(90deg)"></x-shape>')
o.append(f'<div data-build-in="pop order 3" style="position:absolute;left:1004px;top:520px;width:820px;height:250px;background:{CARD};border:2px dashed {LINE};border-radius:16px;padding:22px 30px;display:flex;flex-direction:column;gap:6px">'
         + p(f"font-size:40px;font-weight:700;color:{INK}", "오늘 배운 것") + p(f"font-size:28px;color:{INK}", "• 셀은 따로 실행해요")
         + p(f"font-size:28px;color:{INK}", "• <b>Shift+Enter</b>로 실행") + p(f"font-size:20px;color:{GRAY};margin-top:6px", "실행하면 꾸며진 모습으로 바뀌어요") + '</div>')
o.append(caption("마크다운 기호는 01에서 본 것과 같아요. 셀 종류는 오른쪽 아래 글자로 구분해요.", 880))
W("kinds", o, "코드 셀은 파이썬 코드를 커널로 보내 실행하고 결과를 아래에 보여 줘요. 왼쪽 셀의 출력은 tools/demo.sh에서 hello-uv 커널로 실제로 실행한 결과예요. 마지막 줄이 값이라서 따옴표까지 그대로 보여요. 마크다운 셀은 실행하지 않고 글을 꾸며 보여 줘요. 01에서 README를 쓸 때 본 # 제목, - 목록, **굵게**를 그대로 써요. 마크다운 셀을 Shift+Enter로 실행하면 꾸며진 모습이 되고, 두 번 클릭하면 다시 고칠 수 있어요. 셀 종류는 셀 오른쪽 아래 글자를 눌러서도 바꿀 수 있어요.")

# ---------- part 2: running cells ----------
EB2 = "2. 셀 실행하기"
RUN_BEFORE = [C(C_X), C(C_P)]
runs = [("run-ctrl", "Ctrl+Enter", "control+Enter", "실행하고 그 셀에 머물러요", [C(C_X, n=1), C(C_P)], "c-x", "cmd",
         "같은 셀을 고치고 다시 돌려 볼 때 써요."),
        ("run-shift", "Shift+Enter", "Shift+Enter", "실행하고 다음 셀로 넘어가요", [C(C_X, n=1), C(C_P)], "c-p", "cmd",
         "위에서 아래로 차례대로 실행할 때 써요. 가장 많이 써요."),
        ("run-alt", "Alt+Enter", "option+Enter", "실행하고 바로 아래에 새 셀을 만들어요", [C(C_X, n=1), {"id": "c-new", "lines": [""]}, C(C_P)], "c-new", "edit",
         "실행 결과를 보고 이어서 새 코드를 적을 때 써요.")]
RUN_CAP = {"run-ctrl": "파란 막대가 1번 셀에 그대로 있어요.", "run-shift": "파란 막대가 2번 셀로 내려갔어요.", "run-alt": "새 셀이 끼어들고, 커서가 그 안에서 기다려요."}
for i, (sid, win, mac, title, after, sel, mode, cap) in enumerate(runs):
    o = [sec(sid, "magic" if i else "fade")] + head(EB2, e(title), BL)
    o.append(f'<div id="keys" style="position:absolute;left:96px;top:220px;width:1728px;height:150px;background:{CARD};border:2px solid {LINE};border-radius:20px;padding:0 40px;display:flex;flex-direction:row;align-items:center;gap:80px">'
             + key_pair(win, mac, 30) + p(f"flex:1;font-size:28px;line-height:1.5;color:{SUB}", e(cap)) + '</div>')
    o.append(p(f"position:absolute;left:96px;top:410px;width:780px;font-size:26px;font-weight:700;color:{GRAY}", "누르기 전", ' id="lb-before"'))
    o += notebook(RUN_BEFORE, 96, 460, 780, sel="c-x", bar=False, pre="b-")
    o.append(f'<x-shape id="run-arrow" kind="arrow-right" style="position:absolute;left:910px;top:540px;width:90px;height:60px;background:{BL}"></x-shape>')
    o.append(p(f"position:absolute;left:1044px;top:410px;width:780px;font-size:26px;font-weight:700;color:{BL}", "누른 뒤", ' id="lb-after"'))
    o += [x.replace(' style="position:absolute', ' data-build-in="pop order 1" style="position:absolute', 1) if x.startswith('<div id="a-c-') else x
          for x in notebook(after, 1044, 460, 780, sel=sel, mode=mode, bar=False, pre="a-")]
    notes = {"run-ctrl": "셀을 고른 상태에서 Ctrl+Enter를 치면 그 셀만 실행해요. x = 10은 값을 기억만 하고 출력이 없어서 실행 번호 [1]만 생겨요. 파란 선택 막대는 그대로 1번 셀에 있어요. Mac도 Cmd가 아니라 control 키예요. VS Code 기본 설정이 그래요.",
             "run-shift": "Shift+Enter는 실행하고 선택을 다음 셀로 옮겨요. 그래서 Shift+Enter를 계속 치면 위에서 아래로 차례대로 실행돼요. 마지막 셀에서 치면 아래에 빈 셀을 하나 만들어 줘요. Windows와 Mac이 같아요. 09에서 처음 실행할 때 쓴 키예요.",
             "run-alt": "Alt+Enter는 실행하고 바로 아래에 빈 코드 셀을 끼워 넣어요. 새 셀에는 커서가 있어서 바로 칠 수 있어요. Mac은 Alt 자리에 있는 option 키예요. 기존 2번 셀은 한 칸 아래로 밀려요."}[sid]
    o.append(caption(RUN_CAP[sid], 860))
    W(sid, o, notes, ("run", "셀 실행하기") if i == 0 else None)

o = [sec("order")] + head(EB2, "대괄호 숫자는 실행한 순서예요", BL)
o += notebook([C(C_X, n=1), C(C_P, n=2, out=["20"]), C(C_NAME, n=3, out=["'안녕하세요, kim'"]), C(C_INC, n=4, out=["11"])], 96, 210, 1100, sel="c-inc", bar=False)
o.append(f'<div id="mem" style="position:absolute;left:1260px;top:210px;width:564px;height:330px;background:{CARD};border:2px solid {LINE};border-top:10px solid {JP};border-radius:20px;padding:24px 32px;display:flex;flex-direction:column;gap:14px">'
         + p(f"font-size:28px;font-weight:700;color:{JP}", "커널이 기억하는 값")
         + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:{INK};background:#F1F0EC;border-radius:10px;padding:8px 18px", "x = 11")
         + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:{INK};background:#F1F0EC;border-radius:10px;padding:8px 18px", "name = 'kim'") + '</div>')
o.append(p(f"position:absolute;left:1260px;top:580px;width:564px;font-size:28px;line-height:1.5;color:{SUB}", "앞 셀에서 만든 값을 뒤 셀이 그대로 써요.", ' id="mem-note"'))
o.append(caption("4번 셀을 한 번 더 실행하면 어떻게 될까요?", 900))
W("order", o, "1번 셀에서 x에 10을 넣었고, 2번 셀은 그 x로 20을 출력했어요. 셀은 따로 실행해도 값은 커널 하나가 계속 기억해요. 오른쪽 상자가 지금 커널이 기억하는 값이에요. 4번 셀은 x에 1을 더하고 x를 보여 줘요. 출력은 tools/run_nb.py로 hello-uv 커널에서 실제로 실행한 결과예요. 다음 장에서 4번 셀을 한 번 더 실행해요.", None)

o = [sec("again", "magic")] + head(EB2, "같은 셀을 다시 실행하면 번호도 값도 바뀌어요", BL)
o += notebook([C(C_X, n=1), C(C_P, n=2, out=["20"]), C(C_NAME, n=3, out=["'안녕하세요, kim'"]), C(C_INC, n=5, out=["12"])], 96, 210, 1100, sel="c-inc", bar=False)
o.append(f'<div id="mem" style="position:absolute;left:1260px;top:210px;width:564px;height:330px;background:{CARD};border:2px solid {LINE};border-top:10px solid {JP};border-radius:20px;padding:24px 32px;display:flex;flex-direction:column;gap:14px">'
         + p(f"font-size:28px;font-weight:700;color:{JP}", "커널이 기억하는 값")
         + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:{INK};background:#FFF1C9;border-radius:10px;padding:8px 18px", "x = 12")
         + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:{INK};background:#F1F0EC;border-radius:10px;padding:8px 18px", "name = 'kim'") + '</div>')
o.append(p(f"position:absolute;left:1260px;top:580px;width:564px;font-size:28px;line-height:1.5;color:{SUB}", "[4]가 [5]로, 11이 12로 바뀌었어요. 화면 순서가 아니라 누른 순서대로 실행돼요.", ' id="mem-note"'))
o.append(caption("숫자가 1, 2, 3 차례가 아니면 위에서부터 다시 실행해 봐요.", 900))
W("again", o, "같은 셀을 다시 실행하면 새 번호 [5]가 붙고, x는 11에서 1이 더 커져 12가 돼요. 노트북은 화면에 보이는 위아래 순서가 아니라 내가 누른 순서대로 실행해요. 그래서 셀을 이리저리 실행하다 보면 같은 코드인데 결과가 달라져요. 번호가 뒤죽박죽이면 다음 장의 Restart와 Run All로 위에서부터 다시 실행해요. 출력은 run_nb.py로 같은 셀을 두 번 실행한 실제 결과예요.")

o = [sec("restart")] + head(EB2, "Restart는 기억한 값을 모두 지워요", BL)
o.append(f'<div style="position:absolute;left:96px;top:220px;width:520px;height:300px;background:{CARD};border:2px solid {LINE};border-top:10px solid {JP};border-radius:20px;padding:24px 32px;display:flex;flex-direction:column;gap:14px">'
         + p(f"font-size:26px;font-weight:700;color:{JP}", "Restart 전")
         + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{INK};background:#F1F0EC;border-radius:10px;padding:8px 18px", "x = 12")
         + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{INK};background:#F1F0EC;border-radius:10px;padding:8px 18px", "name = 'kim'") + '</div>')
o.append(f'<div data-build-in="fade order 1" style="position:absolute;left:650px;top:300px;width:200px;display:flex;flex-direction:column;align-items:center;gap:10px">'
         + p(f"font-size:24px;font-weight:700;color:{JP};white-space:nowrap", "↻ Restart") + f'<x-shape kind="arrow-right" style="width:110px;height:56px;background:{JP}"></x-shape></div>')
o.append(f'<div data-build-in="pop order 1" style="position:absolute;left:884px;top:220px;width:520px;height:300px;background:{CARD};border:2px dashed {LINE};border-top:10px solid {JP};border-radius:20px;padding:24px 32px;display:flex;flex-direction:column;gap:14px">'
         + p(f"font-size:26px;font-weight:700;color:{JP}", "Restart 뒤") + p(f"font-size:28px;color:{GRAY}", "비어 있어요") + '</div>')
o += cell(C(C_P, n=1, out=[NAME_ERR], err=True), 96, 580, 1308, sel="c-p", attrs=' data-build-in="rise order 2"')
o.append(p(f"position:absolute;left:96px;top:760px;width:1308px;font-size:26px;line-height:1.5;color:{SUB}", "2번 셀만 실행하면 x를 몰라서 오류가 나요. 번호도 [1]부터 다시 세요.", ' data-build-in="fade order 2"'))
o.append(f'<div data-build-in="rise order 3" style="position:absolute;left:1460px;top:220px;width:364px;height:300px;background:#E6F4EC;border-radius:20px;padding:32px 30px;display:flex;flex-direction:column;gap:20px">'
         + p(f"font-size:28px;font-weight:700;color:{GR}", "해결") + p(f"font-size:36px;font-weight:700;color:{INK}", "▷ Run All")
         + p(f"font-size:24px;line-height:1.5;color:{SUB}", "맨 위 셀부터 차례로 실행해서 x = 10부터 다시 기억해요.") + '</div>')
o.append(caption("뭔가 꼬였으면 Restart 뒤 Run All. 위에서부터 깨끗하게 다시 실행해요.", 900))
W("restart", o, "Restart는 커널을 껐다 켜요. 커널이 기억하던 x와 name이 모두 사라져요. 화면의 코드와 예전 출력은 그대로 남아 있어서 헷갈리기 쉬워요. 이 상태에서 2번 셀만 실행하면 NameError가 나요. 출력은 run_nb.py가 새 커널에서 2번 셀만 실행한 실제 결과예요. 오류 위에 Traceback 몇 줄이 더 나오는데 마지막 줄만 옮겼어요. 해결은 Run All이에요. 맨 위 셀부터 차례로 다시 실행해서 값을 다시 만들어요. 이미 불러온 패키지를 uv add로 바꾼 뒤에도 Restart를 눌러요.")

o = [sec("buttons")] + head(EB2, "위쪽 버튼으로 노트북 전체를 다뤄요", BL)
o += notebook([], 96, 210, 1728)
btns = [("▷ Run All", "맨 위부터 끝까지 실행", "처음 열었을 때, Restart 뒤"), ("↻ Restart", "커널이 기억한 값 지우기", "결과가 이상하거나 번호가 꼬였을 때"),
        ("□ Interrupt", "실행 중인 셀 멈추기", "셀이 안 끝날 때. 실행 중에만 보여요"), ("Clear All Outputs", "출력만 지우기", "값은 그대로 남아요"),
        ("Variables", "기억하는 값 표로 보기", "아래쪽에 표가 열려요")]
for i, (b_, a_, w_) in enumerate(btns):
    x, y = 96 + (i % 3) * 584, 330 + (i // 3) * 290
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:{x}px;top:{y}px;width:560px;height:264px;background:{CARD};border:2px solid {LINE};border-top:10px solid {BL};border-radius:20px;padding:26px 30px;display:flex;flex-direction:column;gap:14px">'
             + p(f"align-self:flex-start;font-size:28px;font-weight:700;color:{INK};background:#ECEAE3;border-radius:10px;padding:6px 16px;white-space:nowrap", e(b_))
             + p(f"font-size:30px;font-weight:700;color:{INK}", e(a_)) + p(f"font-size:24px;color:{SUB}", e(w_)) + '</div>')
o.append(f'<div data-build-in="rise order 6" style="position:absolute;left:1264px;top:620px;width:560px;height:264px;background:#FDF3E7;border-radius:20px;padding:26px 30px;display:flex;flex-direction:column;gap:12px">'
         + p(f"font-size:26px;font-weight:700;color:{JP}", "실행 중인 셀")
         + p(f"font-size:24px;line-height:1.5;color:{SUB}", "왼쪽에 도는 표시가 나와요. 오래 걸리면 Interrupt를 눌러요.") + '</div>')
W("buttons", o, "노트북 맨 위 줄의 버튼이에요. Run All은 맨 위 셀부터 끝까지 실행해요. 노트북을 새로 열었을 때도 커널은 아무것도 기억하지 않아서 Run All부터 눌러요. Restart는 앞 장에서 본 대로 기억을 지워요. Interrupt는 셀이 실행되는 동안에만 보이는 버튼이에요. 무한 반복처럼 끝나지 않는 셀을 멈춰요. Clear All Outputs는 화면의 출력만 지우고 커널의 값은 남겨요. Variables는 커널이 기억하는 값을 표로 보여 줘요. 화면이 좁으면 몇 개는 오른쪽 ... 메뉴 안에 들어가요.")

# ---------- part 3: command mode and edit mode ----------
EB3 = "3. 명령 모드와 편집 모드"
o = [sec("modes")] + head(EB3, "셀에는 두 가지 모드가 있어요", PUR)
for k, (lbl, mode, c, desc, x) in enumerate([("명령 모드", "cmd", PUR, "셀 자체를 다뤄요<br>추가, 삭제, 종류 바꾸기", 96), ("편집 모드", "edit", SEL, "셀 안의 글자를 고쳐요<br>코드 치기, 지우기", 1104)]):
    o.append(p(f"position:absolute;left:{x}px;top:220px;width:720px;font-size:36px;font-weight:700;color:{c}", lbl))
    o += cell(C(C_X), x, 290, 720, sel="c-x", mode=mode, pre=f"m{k}-")
    o.append(p(f"position:absolute;left:{x}px;top:400px;width:720px;font-size:24px;color:{GRAY}", "왼쪽 막대만" if mode == "cmd" else "왼쪽 막대 + 셀 테두리 + 커서"))
    o.append(p(f"position:absolute;left:{x}px;top:480px;width:720px;font-size:30px;line-height:1.5;color:{INK}", desc))
o.append(f'<div data-build-in="pop order 1" style="position:absolute;left:840px;top:250px;width:240px;display:flex;flex-direction:column;align-items:center;gap:12px">'
         + kbd("Enter", 30) + f'<x-shape kind="arrow-right" style="width:120px;height:50px;background:{SEL}"></x-shape></div>')
o.append(f'<div data-build-in="pop order 2" style="position:absolute;left:840px;top:450px;width:240px;display:flex;flex-direction:column;align-items:center;gap:12px">'
         + f'<x-shape kind="arrow-left" style="width:120px;height:50px;background:{PUR}"></x-shape>' + kbd("Esc", 30) + '</div>')
o.append(f'<div data-build-in="rise order 3" style="position:absolute;left:96px;top:660px;width:1728px;height:150px;background:{CARD};border:2px solid {LINE};border-radius:20px;padding:0 40px;display:flex;flex-direction:row;align-items:center;gap:40px">'
         + f'<x-icon name="Lightbulb" style="width:52px;height:52px;color:{OR}"></x-icon>'
         + p(f"flex:1;font-size:30px;line-height:1.5;color:{INK}", "셀 안을 클릭하면 편집 모드, 셀 왼쪽 빈 곳을 클릭하면 명령 모드예요.<br>Enter와 Esc는 Windows와 Mac이 같아요.") + '</div>')
o.append(caption("A, B, M 같은 글자 단축키는 명령 모드에서만 동작해요.", 880))
W("modes", o, "노트북 셀에는 두 가지 모드가 있어요. 명령 모드는 셀 하나를 통째로 다루는 상태예요. 왼쪽에 막대만 보여요. 편집 모드는 셀 안에 커서가 깜빡이는 상태예요. 막대와 함께 셀 테두리가 진해져요. 편집 모드에서 Esc를 치면 명령 모드, 명령 모드에서 Enter를 치면 편집 모드로 가요. 명령 모드에서 B를 치면 셀이 생기고, 편집 모드에서 B를 치면 글자 b가 들어가요. 같은 키가 모드에 따라 다르게 동작해서 처음에 많이 헷갈려요. 실제 색은 VS Code 테마에 따라 달라요.", ("modes", "명령 모드와 편집 모드"))

flow = [("flow1", "편집 모드에서 Esc", "Esc", "Esc", "명령 모드가 돼요. 커서와 테두리가 사라져요", [C(C_X, n=1)], "c-x", "cmd"),
        ("flow2", "명령 모드에서 B", "B", "B", "아래에 새 코드 셀이 생기고 그 셀이 골라져요", [C(C_X, n=1), {"id": "c-n2", "lines": [""]}], "c-n2", "cmd"),
        ("flow3", "M을 누르고 Enter, 글 적기", "M", "M", "마크다운 셀로 바뀌어요. Enter로 편집 모드에 들어가 적어요",
         [C(C_X, n=1), {"id": "c-n2", "kind": "md", "lines": ["# 오늘 배운 것"]}], "c-n2", "edit"),
        ("flow4", "Shift+Enter", "Shift+Enter", "Shift+Enter", "마크다운이 꾸며진 제목으로 바뀌고, 아래에 새 셀이 생겨요",
         [C(C_X, n=1), {"id": "c-n2", "kind": "mdr", "lines": ["# 오늘 배운 것"]}, {"id": "c-n3", "lines": [""]}], "c-n3", "edit")]
for i, (sid, t, win, mac, desc, cells, sel, mode) in enumerate(flow):
    o = [sec(sid, "magic" if i else "fade")] + head(EB3, f"키로만 셀 만들기 {i + 1}/4 · {e(t)}", PUR)
    o += notebook(cells, 96, 220, 1100, sel=sel, mode=mode, bar=False, pre="f-")
    o.append(f'<div id="flow-key" style="position:absolute;left:1260px;top:220px;width:564px;height:420px;background:{CARD};border:2px solid {LINE};border-top:10px solid {PUR};border-radius:20px;padding:32px 36px;display:flex;flex-direction:column;gap:26px">'
             + p(f"font-size:24px;font-weight:700;color:{GRAY}", "누른 키") + kbd(win, 40)
             + p(f"font-size:28px;line-height:1.5;color:{INK}", e(desc)) + '</div>')
    o.append(f'<div id="flow-dots" style="position:absolute;left:1260px;top:680px;width:564px;display:flex;flex-direction:row;gap:14px">'
             + "".join(f'<div style="flex:1;height:12px;border-radius:6px;background:{PUR if j <= i else LINE}"></div>' for j in range(4)) + '</div>')
    notes = {"flow1": "마우스 없이 셀을 만드는 흐름을 네 장에 걸쳐 봐요. 1번 셀에 x = 10을 적고 실행한 뒤, 셀 안을 다시 클릭해 편집 모드인 상태에서 시작해요. Esc를 치면 커서가 빠지고 명령 모드가 돼요.",
             "flow2": "명령 모드에서 B를 치면 아래(Below)에 빈 코드 셀이 생겨요. A는 위(Above)에 만들어요. 새 셀은 골라진 상태지만 아직 명령 모드예요.",
             "flow3": "M은 마크다운(Markdown), Y는 다시 코드 셀로 바꾸는 키예요. 셀 오른쪽 아래 글자가 Markdown으로 바뀌어요. Enter를 치면 편집 모드가 되고, 01에서 배운 # 제목을 적어요. 한글을 적은 뒤 Esc를 치기 전에는 한/영을 영문으로 바꿔 두면 다음 단축키가 잘 먹어요.",
             "flow4": "Shift+Enter로 마크다운 셀을 실행하면 꾸며진 제목이 돼요. 마지막 셀이었으니 아래에 새 코드 셀이 생기고 바로 칠 수 있어요. 키 네 번이면 마우스 없이 설명과 코드 칸을 만들어요."}[sid]
    o.append(caption({"flow1": "지금은 명령 모드예요. 다음 키는 글자 대신 명령으로 읽혀요.", "flow2": "아직 명령 모드라서 M을 치면 셀 종류가 바뀌어요.",
                      "flow3": "편집 모드에서 친 글자는 셀 안으로 들어가요.", "flow4": "마우스 없이 설명 칸과 코드 칸을 만들었어요."}[sid], 860))
    W(sid, o, notes)

o = [sec("cmdkeys")] + head(EB3, "명령 모드에서 쓰는 글자 키", PUR)
ck = [("A", "위에 셀 추가", "Above"), ("B", "아래에 셀 추가", "Below"), ("D+D", "셀 지우기", "D를 두 번"), ("Z", "지운 셀 되살리기", "방금 한 일 되돌리기"),
      ("M", "마크다운 셀로", "Markdown"), ("Y", "코드 셀로", "다시 코드로"), ("L", "줄 번호 켜고 끄기", "오류 줄 찾을 때"), ("Enter", "편집 모드로", "셀 안으로 들어가기")]
for i, (k, a_, b_) in enumerate(ck):
    x, y = 96 + (i % 4) * 438, 220 + (i // 4) * 300
    o.append(f'<div data-build-in="rise order {i // 2 + 1}" style="position:absolute;left:{x}px;top:{y}px;width:414px;height:276px;background:{CARD};border:2px solid {LINE};border-top:10px solid {PUR};border-radius:20px;padding:28px 30px;display:flex;flex-direction:column;gap:16px">'
             + kbd(k, 40) + p(f"font-size:30px;font-weight:700;color:{INK}", e(a_)) + p(f"font-size:24px;color:{SUB}", e(b_)) + '</div>')
o.append(caption("Windows와 Mac이 같아요. 글자가 셀에 들어가면 편집 모드예요. Esc부터 쳐요.", 860))
W("cmdkeys", o, "명령 모드에서만 동작하는 글자 키예요. 대문자로 적었지만 Shift 없이 그냥 눌러요. D는 한 번이 아니라 두 번 연달아 눌러야 지워요. 실수로 지웠으면 바로 Z로 되살려요. L은 셀 하나의 줄 번호를 켜요. 오류 메시지에 line 3처럼 줄 번호가 나올 때 써요. 한글 입력 상태에서는 글자 키가 먹지 않을 수 있어요. 한/영 키로 영문으로 바꿔요.")

# ---------- part 4: writing rules in a markdown cell ----------
EBM = "4. 마크다운 셀로 규칙 정리하기"
MD = TEAL


def md_src(sid, lines, left, top, w, attrs=""):
    """A markdown cell in edit mode, drawn standalone (not a magic-move cell)."""
    return cell({"id": sid, "kind": "md", "lines": lines}, left, top, w, sel=sid, mode="edit", attrs=attrs)


def md_view(lines, left, top, w, h, attrs=""):
    """What the markdown cell looks like after Shift+Enter."""
    o = [f'<div{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:{CARD};border:2px dashed {LINE};border-radius:16px;padding:24px 34px;display:flex;flex-direction:column;gap:8px">']
    for l in lines:
        if l == "---":
            o.append(f'<div style="height:3px;background:#C9CED8;margin:6px 0 10px"></div>')
        elif l.startswith("### "):
            o.append(p(f"font-size:36px;font-weight:700;line-height:1.3;color:{INK}", e(l[4:])))
        elif l.startswith("- "):
            body = e(l[2:])
            if ": " in body:
                a_, b_ = body.split(": ", 1)
                body = f'{a_}: <span style="font-family:{MONO};font-weight:700;color:{MD}">{b_}</span>'
            o.append(p(f"font-size:28px;line-height:1.45;color:{INK}", "• " + body))
    o.append('</div>')
    return o


RULES = ["---", "### 변수 이름 규칙", "- 숫자로 시작 불가", "- 공백 불가", "- 하이픈(-) 불가", "- 예약어 사용 불가"]
o = [sec("md-rules")] + head(EBM, "마크다운 셀에 규칙을 적어 둬요", MD)
o.append(p(f"position:absolute;left:96px;top:210px;width:860px;font-size:26px;font-weight:700;color:{GRAY}", "적는 모습 (편집 모드)"))
o += md_src("m-rules", RULES, 96, 260, 860, ' data-build-in="rise order 1"')
o.append(f'<x-shape kind="arrow-right" data-build-in="fade order 2" style="position:absolute;left:984px;top:420px;width:80px;height:56px;background:{MD}"></x-shape>')
o.append(p(f"position:absolute;left:1094px;top:210px;width:730px;font-size:26px;font-weight:700;color:{MD}", "Shift+Enter 뒤", ' data-build-in="fade order 2"'))
o += md_view(RULES, 1094, 260, 730, 420, ' data-build-in="pop order 2"')
sym = [("---", "가로줄"), ("###", "작은 제목"), ("-", "목록")]
o.append(f'<div data-build-in="rise order 3" style="position:absolute;left:96px;top:740px;width:1728px;height:110px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:0 36px;display:flex;flex-direction:row;align-items:center;gap:56px">'
         + "".join('<div style="display:flex;flex-direction:row;align-items:center;gap:16px">'
                   + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{MD};background:#E3F3F4;border-radius:10px;padding:4px 16px", e(k))
                   + p(f"font-size:28px;color:{INK}", d) + '</div>' for k, d in sym)
         + p(f"flex:1;font-size:24px;color:{SUB};text-align:right", "기호 뒤에는 한 칸 띄워요") + '</div>')
o.append(caption("수업에서 배운 규칙은 코드 옆 마크다운 셀에 적어 두면 복습할 때 같이 봐요.", 900))
W("md-rules", o, "노트북은 코드와 설명을 한 파일에 같이 둘 수 있어요. 수업에서 배운 변수 이름 규칙을 마크다운 셀에 적어 볼게요. --- 은 위 내용과 나누는 가로줄, ### 은 01에서 본 # 제목보다 작은 제목, - 는 목록이에요. 01과 같이 기호 뒤에는 한 칸을 띄워요. 적은 뒤 Shift+Enter를 치면 오른쪽처럼 꾸며져요. 다음 장에서 규칙을 어기면 실제로 어떤 오류가 나는지 봐요.", ("rules", "마크다운 셀로 규칙 정리하기"))

o = [sec("name-err")] + head(EBM, "규칙을 어기면 SyntaxError가 나요", MD)
bad = [("숫자로 시작", '1st_name = "kim"', "SyntaxError: invalid decimal literal", "first_name"),
       ("공백", 'my name = "kim"', "SyntaxError: invalid syntax", "my_name"),
       ("하이픈", 'my-name = "kim"', "SyntaxError: cannot assign to expression here.", "my_name"),
       ("예약어", 'class = "kim"', "SyntaxError: invalid syntax", "class_name")]
for i, (lbl, code, err, fix) in enumerate(bad):
    x, y = 96 + (i % 2) * 884, 210 + (i // 2) * 330
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:{x}px;top:{y}px;width:844px;height:306px;background:{CARD};border:2px solid {LINE};border-top:10px solid {RED};border-radius:20px;padding:22px 30px;display:flex;flex-direction:column;gap:12px">'
             + p(f"font-size:28px;font-weight:700;color:{RED}", e(lbl))
             + p(f"font-family:{MONO};font-size:28px;line-height:1.4;color:{INK};background:#F1F0EC;border-radius:10px;padding:8px 18px;white-space:pre", e(code))
             + p(f"font-family:{MONO};font-size:22px;line-height:1.4;color:{RED};white-space:nowrap", e(err))
             + '<div style="display:flex;flex-direction:row;align-items:center;gap:14px">' + p(f"font-size:24px;font-weight:700;color:{GR}", "이렇게")
             + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{GR};background:#E6F4EC;border-radius:10px;padding:4px 16px", e(fix)) + '</div></div>')
o.append(caption("띄어쓰기와 하이픈 자리에는 밑줄(_)을 써요. 예약어는 뒤에 단어를 붙여요.", 900))
W("name-err", o, "네 셀을 hello-uv 커널로 실제로 실행한 오류의 마지막 줄이에요. 괄호 안의 임시 파일 이름과 줄 번호는 뺐어요. 하이픈 오류는 뒤에 Maybe you meant '==' instead of '='? 가 더 붙어요. 파이썬이 my-name을 my 빼기 name이라는 계산으로 읽어서 나는 오류예요. 예약어는 if, for, class, True, None처럼 파이썬이 이미 쓰는 단어예요. 셀에서 import keyword 뒤 keyword.kwlist를 실행하면 전체 목록이 나와요. 오류 메시지 글자는 파이썬 버전에 따라 조금 다를 수 있어요.")

CONV = ["### 컨벤션", "- 스네이크 표기법: user_name", "- 파스칼 표기법: UserProfile", "- 카멜 표기법: userName"]
o = [sec("conv")] + head(EBM, "이름 짓는 표기법은 세 가지예요", MD)
o += md_src("m-conv", CONV, 96, 210, 860)
o += md_view(CONV, 1004, 210, 820, 240, ' data-build-in="pop order 1"')
kinds_ = [("스네이크 표기법", "snake_case", [("user", INK), ("_", RED), ("name", INK)], "파이썬 변수, 함수 이름", "우리는 이걸 써요", GR),
          ("파스칼 표기법", "PascalCase", [("U", RED), ("ser", INK), ("P", RED), ("rofile", INK)], "파이썬 클래스 이름", "단어 첫 글자를 모두 대문자로", BL),
          ("카멜 표기법", "camelCase", [("user", INK), ("N", RED), ("ame", INK)], "자바스크립트에서 많이 써요", "파이썬에서는 잘 안 써요", GRAY)]
for i, (k, en, parts_, use, note, c) in enumerate(kinds_):
    x = 96 + i * 584
    word = "".join(f'<span style="color:{col}">{e(t)}</span>' for t, col in parts_)
    o.append(f'<div data-build-in="rise order {i + 2}" style="position:absolute;left:{x}px;top:500px;width:560px;height:370px;background:{CARD};border:2px solid {LINE};border-top:10px solid {c};border-radius:20px;padding:26px 32px;display:flex;flex-direction:column;gap:14px">'
             + '<div style="display:flex;flex-direction:row;align-items:baseline;gap:14px">' + p(f"font-size:30px;font-weight:700;color:{c}", k) + p(f"font-family:{MONO};font-size:22px;color:{GRAY}", en) + '</div>'
             + p(f"font-family:{MONO};font-size:48px;font-weight:700;line-height:1.3;background:#F6F5F1;border-radius:12px;padding:12px 20px", word)
             + p(f"font-size:28px;font-weight:700;color:{INK}", e(use)) + p(f"font-size:24px;color:{SUB}", e(note)) + '</div>')
o.append(caption("변수 이름은 스네이크 표기법으로 user_name처럼 적어요.", 920))
W("conv", o, "같은 두 단어 user와 name을 이어 붙이는 방법이 세 가지예요. 붉은 글자가 단어를 나누는 자리예요. 스네이크 표기법은 소문자와 밑줄로 이어요. 뱀처럼 바닥에 붙어 있어서 붙은 이름이에요. 파이썬은 변수와 함수 이름에 이 방식을 써요. 파스칼 표기법은 단어마다 첫 글자를 대문자로 써요. 파이썬에서는 클래스 이름에만 써요. 클래스는 뒤에서 배워요. 카멜 표기법은 첫 단어만 소문자로 시작해서 낙타 혹처럼 보여요. 자바스크립트 같은 다른 언어에서 많이 쓰고, 파이썬 코드에서는 잘 쓰지 않아요. 파이썬의 이름 규칙 문서(PEP 8)가 이렇게 정해 두었어요.")

# ---------- part 5: shortcut tables ----------
EB4 = "5. 단축키 모음 (Windows, Mac)"


def key_table(rows, top=210):
    o = [f'<div style="position:absolute;left:96px;top:{top}px;width:1728px;display:flex;flex-direction:row;gap:24px;padding:0 30px">'
         + p(f"width:620px;flex:none;font-size:24px;font-weight:700;color:{GRAY}", "하는 일") + p(f"width:500px;flex:none;font-size:24px;font-weight:700;color:{WIN}", "Windows")
         + p(f"flex:1;font-size:24px;font-weight:700;color:{MAC}", "Mac") + '</div>']
    for i, (what, where, win, mac) in enumerate(rows):
        y = top + 50 + i * 96
        o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:96px;top:{y}px;width:1728px;height:84px;background:{CARD};border:2px solid {LINE};border-radius:16px;padding:0 30px;display:flex;flex-direction:row;align-items:center;gap:24px">'
                 + '<div style="width:620px;flex:none;display:flex;flex-direction:row;align-items:baseline;gap:14px">' + p(f"font-size:28px;font-weight:700;color:{INK}", e(what))
                 + (p(f"font-size:21px;color:{GRAY}", e(where)) if where else "") + '</div>'
                 + f'<div style="width:500px;flex:none">{kbd(win, 26)}</div><div style="flex:1">{kbd(mac, 26)}</div></div>')
    return o


o = [sec("keys-run")] + head(EB4, "실행하고 셀 다루는 키", NAVY)
o += key_table([("실행하고 머물기", "", "Ctrl+Enter", "control+Enter"), ("실행하고 다음 셀로", "", "Shift+Enter", "Shift+Enter"), ("실행하고 아래에 새 셀", "", "Alt+Enter", "option+Enter"),
                ("명령 모드로", "편집 모드에서", "Esc", "Esc"), ("편집 모드로", "명령 모드에서", "Enter", "Enter"), ("셀 위아래로 옮기기", "명령 모드에서", "Alt+↑", "option+↑"),
                ("셀 추가, 종류 바꾸기", "명령 모드에서", "A B M Y", "A B M Y")])
o.append(caption("Mac의 실행 키는 Cmd가 아니라 control이에요.", 960))
W("keys-run", o, "앞에서 본 키를 한 장에 모았어요. Windows의 Ctrl은 Mac에서 보통 Cmd가 되지만, 노트북 실행 키는 예외예요. VS Code 기본 설정에서 Mac의 셀 실행은 control+Enter예요. Alt 자리는 Mac의 option 키예요. 셀 옮기기는 아래로 옮길 때 ↓를 눌러요. 단축키는 VS Code 버전이나 다른 확장 설정에 따라 바뀔 수 있어요. 안 먹으면 명령 팔레트에서 Preferences: Open Keyboard Shortcuts를 열고 notebook으로 검색해 지금 키를 확인해요.", ("keys", "단축키 모음"))

o = [sec("keys-edit")] + head(EB4, "셀 안에서 글 고치는 키와 파일 키", NAVY)
o += key_table([("주석 넣고 빼기", "편집 모드에서", "Ctrl+/", "Cmd+/"), ("되돌리기", "편집 모드에서", "Ctrl+Z", "Cmd+Z"), ("들여쓰기 빼기", "편집 모드에서", "Shift+Tab", "Shift+Tab"),
                ("노트북에서 찾기", "", "Ctrl+F", "Cmd+F"), ("노트북 저장", "", "Ctrl+S", "Cmd+S"), ("명령 팔레트", "", "Ctrl+Shift+P", "Cmd+Shift+P"),
                ("확장 화면 열기", "", "Ctrl+Shift+X", "Cmd+Shift+X")])
o.append(caption("이 키들은 Windows의 Ctrl이 Mac에서 Cmd로 바뀌어요.", 960))
W("keys-edit", o, "셀 안에서 코드를 고칠 때는 VS Code의 보통 편집 키를 그대로 써요. 주석 키는 줄 앞에 #을 붙였다 뗐다 해요. 여러 줄을 고르고 누르면 한 번에 바뀌어요. 노트북은 저장해야 출력까지 .ipynb 파일에 남아요. 탭 이름 옆에 동그라미가 있으면 아직 저장하지 않은 거예요. 명령 팔레트는 메뉴를 몰라도 이름으로 기능을 찾는 창이에요. 확장 화면 키는 09에서 Jupyter 확장을 설치할 때 쓴 키예요.")

# ---------- summary ----------
EB5 = "정리"
o = [sec("trouble")] + head(EB5, "노트북에서 막히면", RED)
tr = [("글자를 쳤는데 셀이 생기거나 지워져요", "명령 모드였어요", "셀 안 클릭, Enter"), ("A, B, M을 눌러도 아무 일이 없어요", "편집 모드거나 한글 입력 상태예요", "Esc, 한/영 키"),
      (NAME_ERR, "앞 셀을 안 돌렸거나 Restart 뒤예요", "▷ Run All"), (SYN_ERR, "설명 글을 코드 셀에 적었어요", "명령 모드에서 M"),
      ("셀이 끝나지 않고 계속 돌아요", "오래 걸리거나 끝나지 않는 코드예요", "□ Interrupt"), ("Mac에서 Cmd+Enter로 실행이 안 돼요", "Mac 실행 키는 control이에요", "control+Enter")]
o.append('<div style="position:absolute;left:96px;top:210px;width:1728px;height:780px;display:flex;flex-direction:column;gap:14px">')
for i, (q, a_, cmd) in enumerate(tr, 1):
    mono = q.endswith(("defined", "syntax"))
    o.append(f'<div data-build-in="rise order {i}" style="flex:1;display:flex;flex-direction:row;gap:26px;align-items:center;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:8px 30px">'
             + num(i, RED, 36)
             + '<div style="flex:1;display:flex;flex-direction:column;gap:4px">' + p(f"{'font-family:' + MONO + ';font-size:23px;' if mono else 'font-size:27px;'}font-weight:700;color:{INK}", e(q)) + p(f"font-size:23px;color:{SUB}", e(a_)) + '</div>'
             + p(f"width:340px;flex:none;font-size:26px;font-weight:700;line-height:1.5;color:{INK};background:#EEEFF2;padding:10px 20px;border-radius:12px;white-space:nowrap", e(cmd)) + '</div>')
o.append('</div>')
W("trouble", o, "1번과 2번은 모드를 헷갈려서 나요. 셀 테두리와 커서로 지금 모드를 봐요. 한글 입력 상태에서는 명령 모드 글자 키가 먹지 않을 수 있어서 한/영 키로 영문으로 바꿔요. 3번은 Restart 장에서 본 오류예요. 4번 출력은 '오늘 배운 것'을 코드 셀에서 실행한 실제 결과예요. 실제로는 괄호 안에 임시 파일 이름과 줄 번호가 더 붙어요. 5번은 셀 왼쪽에 도는 표시가 계속 보일 때예요. 6번은 다른 프로그램의 Jupyter와 VS Code 기본 설정이 다른 곳이에요. 커널이 .venv가 아니라서 나는 ModuleNotFoundError는 09의 29쪽을 봐요.", ("trouble", "정리"))

o = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>']
cheat = [("Shift+Enter", "", "실행하고 다음 셀로", BL), ("Ctrl+Enter", "Mac control+Enter", "실행하고 머물기", BL), ("Esc", "", "명령 모드로", PUR),
         ("Enter", "", "편집 모드로", PUR), ("A B", "명령 모드", "위, 아래에 셀 추가", PUR), ("M Y", "명령 모드", "마크다운, 코드 셀로", PUR)]
for i, (k, mac, d, c) in enumerate(cheat):
    x, y = 96 + (i % 3) * 584, 200 + (i // 3) * 290
    o.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:560px;height:264px;background:{CARD};border:2px solid {LINE};border-top:10px solid {c};border-radius:20px;padding:28px 32px;display:flex;flex-direction:column;gap:16px">'
             + kbd(k, 34) + p(f"font-size:30px;font-weight:700;color:{INK}", d) + (p(f"font-size:22px;color:{GRAY}", e(mac)) if mac else "") + '</div>')
o.append(f'<div style="position:absolute;left:96px;top:780px;width:1728px;height:210px;background:{CARD};border:2px solid {LINE};border-radius:20px;padding:24px 36px;display:flex;flex-direction:column;justify-content:center;gap:12px">'
         + p(f"font-size:30px;font-weight:700;color:{INK}", '[숫자]는 실행한 순서예요. <span style="font-weight:400;color:' + SUB + '">화면 위아래 순서가 아니에요</span>')
         + p(f"font-size:30px;font-weight:700;color:{INK}", '꼬이면 <span style="color:' + JP + '">↻ Restart</span> 뒤 <span style="color:' + GR + '">▷ Run All</span>')
         + p(f"font-size:30px;font-weight:700;color:{INK}", '패키지는 <span style="font-family:\'JetBrains Mono\';color:' + TEAL + '">uv add 패키지</span>  <span style="font-weight:400;color:' + SUB + '">알림의 Install 대신 터미널에서</span>') + '</div>')
W("cheatsheet", o, "노트북에서 매일 쓰는 키는 이 여섯 개예요. 실행은 Shift+Enter 하나로 시작해도 충분해요. 결과가 이상하면 Restart 뒤 Run All로 위에서부터 다시 실행해요. 노트북에서 쓸 패키지도 09에서 배운 대로 터미널에서 uv add로 넣어요. VS Code 알림의 Install 버튼은 pip로 넣어서 쓰지 않아요.")

# ---------- toc (page numbers from ORDER) ----------
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
parts = [("Search", BL, "노트북 화면 읽기", "커널, 버튼, 실행 번호, 코드와 마크다운 셀", "screen", "kinds"),
         ("PaperPlane", BL, "셀 실행하기", "세 가지 실행 키, 실행 순서, Restart, 위쪽 버튼", "run-ctrl", "buttons"),
         ("Tool", PUR, "명령 모드와 편집 모드", "Esc와 Enter, 키로만 셀 만들기, 글자 키", "modes", "cmdkeys"),
         ("Book", TEAL, "마크다운 셀로 규칙 정리하기", "변수 이름 규칙, 컨벤션(표기법)", "md-rules", "conv"),
         ("Key", NAVY, "단축키 모음", "Windows와 Mac 나란히", "keys-run", "keys-edit")]
t = [f'<section id="toc" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};padding:96px 128px;display:flex;flex-direction:column;gap:40px">',
     f'<h2 style="font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>',
     '<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:24px;flex:1">']
for i, (ic, c, h, s, a, b) in enumerate(parts, 1):
    pg = f"{page[a]}–{page[b]}쪽" if a != b else f"{page[a]}쪽"
    t.append(f'<div style="display:flex;flex-direction:column;gap:10px;background:#FFFFFF;border:2px solid {LINE};border-top:10px solid {c};border-radius:20px;padding:24px 28px">'
             f'<div style="display:flex;flex-direction:row;gap:14px;align-items:center"><p style="font-size:48px;font-weight:900;line-height:1.25;color:{c}">{i}</p>'
             f'<x-icon name="{ic}" style="width:40px;height:40px;color:{c}"></x-icon></div>'
             f'<h3 style="font-size:26px;font-weight:700;color:{INK}">{h}</h3>'
             f'<p style="font-size:26px;line-height:1.4;color:{SUB}">{e(s)}</p><div style="flex:1"></div>'
             f'<p style="font-size:24px;color:#6A7180">{pg}</p></div>')
t += ['</div>', f'<p style="font-size:26px;color:{SUB}">{page["ready"]}쪽은 09에서 한 준비, {page["trouble"]}–{page["cheatsheet"]}쪽은 막힐 때와 한 장 요약이에요.</p>']
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(t) + f"\n<aside>{e('09에서 만든 hello-uv 폴더와 notebook.ipynb를 그대로 써요. 1파트는 화면을 읽는 법, 2파트부터 직접 키를 눌러 봐요. 4파트는 수업에서 배운 이름 규칙을 마크다운 셀로 정리해요. 5파트 표는 수업 중에 옆에 띄워 두고 봐도 돼요.')}</aside>\n</section>\n")

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-10-30T05:00:00Z"}, "lists": "css", "title": "VS Code에서 Jupyter 노트북 쓰기", "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
print(len(ORDER), "slides")
