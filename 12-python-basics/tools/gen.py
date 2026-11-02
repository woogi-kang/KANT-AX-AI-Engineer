"""Generates every slide of the Python basics deck and slides/deck.json.

Story: opens basics.ipynb in hello-uv (chapters 09, 10), puts values into variables, calculates
with the four operators and //, %, **, then compares values and joins conditions with and, or, not.
Every cell and output comes from tools/demo.sh (tools/run_nb.py runs the cells with the project kernel).
Usage: python3 tools/gen.py slides
"""

import html, json, os, sys

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
INK, SUB, LINE, CARD = "#1D2330", "#4A5262", "#E1DED6", "#FFFFFF"
BL, GR, OR, PUR, RED, NAVY, TEAL, GRAY = "#2459C9", "#1F8A4C", "#B26A00", "#5A3BB8", "#A33131", "#1E3F8F", "#0F7C86", "#6A7180"
JP = "#B8560F"          # Jupyter, same as chapters 09 and 10
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




def C(base, **kw):
    d = dict(base)
    d.update(kw)
    return d


TRUE_C, FALSE_C = GR, RED


def tf(v, size=26):
    """True / False chip."""
    c = TRUE_C if v == "True" else FALSE_C
    bg = "#E6F4EC" if v == "True" else "#F8E6E6"
    return p(f"display:inline-block;font-family:{MONO};font-size:{size}px;font-weight:700;color:{c};background:{bg};border-radius:10px;padding:2px 14px;white-space:nowrap", v)


def mono(text, size=28, color=INK, bg="#F1F0EC", extra=""):
    return p(f"font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.4;color:{color};background:{bg};border-radius:10px;padding:4px 16px;white-space:pre;{extra}", e(text))


def card(left, top, w, h, inner, color=None, attrs="", extra="", bg=CARD):
    bt = f"border-top:10px solid {color};" if color else ""
    return (f'<div{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:{bg};border:2px solid {LINE};{bt}border-radius:20px;'
            f'padding:24px 30px;display:flex;flex-direction:column;gap:14px;{extra}">' + inner + '</div>')


def var_box(sid, name, value, left, top, color=BL, w=420, attrs=""):
    """A variable drawn as a box with its name on top."""
    return (f'<div id="{sid}"{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:230px;background:{CARD};border:3px solid {color};border-radius:22px;display:flex;flex-direction:column;overflow:hidden">'
            + p(f"height:70px;flex:none;background:{color};color:#FFFFFF;font-family:{MONO};font-size:34px;font-weight:700;line-height:70px;padding:0 26px", e(name))
            + f'<div style="flex:1;display:flex;align-items:center;justify-content:center">' + p(f"font-family:{MONO};font-size:72px;font-weight:700;color:{INK}", e(value)) + '</div></div>')


def chain(rows, left, top, w, start=1, color=PUR, gap=74):
    """Evaluation steps shown one per click: (expression, result chip or None, label)."""
    o = []
    for i, (expr, res, lbl) in enumerate(rows):
        y = top + i * gap
        o.append(f'<div data-build-in="rise order {start + i}" style="position:absolute;left:{left}px;top:{y}px;width:{w}px;height:{gap - 12}px;display:flex;flex-direction:row;align-items:center;gap:18px">'
                 + (p(f"width:110px;flex:none;font-size:22px;font-weight:700;color:{color}", e(lbl)) if lbl is not None else "")
                 + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{INK};white-space:pre", expr)
                 + (f'<x-shape kind="arrow-right" style="width:44px;height:26px;flex:none;background:#C9CED8"></x-shape>' + tf(res) if res else "") + '</div>')
    return o


NB = "basics.ipynb"
CELL_W = 860

# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#F2B27A;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
       '<h1 style="font-size:104px;font-weight:900;line-height:1.1;color:#F6F5F1">파이썬 기초<br>변수, 타입, 연산</h1>',
       '<p style="font-size:40px;line-height:1.4;color:#BFC6D4">값에 이름 붙이고, 타입 알고,<br>계산하고, 참 거짓 따지기</p>']
cov.append(f'<div style="position:absolute;left:1100px;top:300px;width:680px;height:480px;background:#252B36;border-radius:24px;padding:44px 48px;display:flex;flex-direction:column;justify-content:center;gap:34px">')
for code, out_, c in [("age = 25", "넣기", "#8FB4FF"), ("type(age)", "int", "#9FB3E6"), ("7 // 3", "2", "#7FD3DA"), ("age >= 20", "True", "#C4B1FF")]:
    cov.append('<div style="display:flex;flex-direction:row;align-items:center;gap:28px">'
               + p(f"width:330px;flex:none;font-family:{MONO};font-size:38px;font-weight:700;color:{c};white-space:pre", e(code))
               + f'<x-shape kind="arrow-right" style="width:50px;height:30px;background:#5A6172"></x-shape>'
               + p(f"font-family:{MONO};font-size:36px;font-weight:700;color:#E6E9EF", e(out_)) + '</div>')
cov.append('</div>')
W("cover", cov, "10에서 노트북을 다루는 법과 자료형을 봤어요. 이번 챕터는 파이썬 코드를 직접 적어요. 값에 이름을 붙이는 변수, 값의 종류인 타입, 숫자를 계산하는 사칙연산, True와 False로 답하는 비교와 논리연산을 차례로 봐요. 모든 예제는 노트북 셀에 적고 실행해요.", ("intro", "들어가기"))

ORDER.append("toc")   # written last, after page numbers are known

# ---------- ready ----------
o = [sec("ready")] + head("들어가기", "10에서 이어서 해요", JP)
done = [("hello-uv 노트북, 커널 .venv", "09 · 25–27쪽"), ("변수 이름 규칙과 표기법", "10 · 19–21쪽"), ("자료형과 type()", "10 · 22–23쪽")]
for i, (a_, b_) in enumerate(done):
    y = 220 + i * 150
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:96px;top:{y}px;width:820px;height:126px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:0 28px;display:flex;flex-direction:row;gap:22px;align-items:center">'
             + f'<x-icon name="CheckCircle" style="width:48px;height:48px;color:{GR}"></x-icon>'
             + p(f"flex:1;font-size:30px;font-weight:700;color:{INK}", e(a_))
             + p(f"font-size:24px;font-weight:700;color:{GRAY};white-space:nowrap", e(b_)) + '</div>')
o.append(p(f"position:absolute;left:96px;top:690px;width:820px;font-size:26px;line-height:1.5;color:{SUB}", "기억이 안 나면 그 쪽을 먼저 다시 봐요.", ' data-build-in="fade order 3"'))
o.append(f'<div data-build-in="rise order 4" style="position:absolute;left:1000px;top:220px;width:824px;height:560px;background:{CARD};border:2px solid {LINE};border-top:10px solid {JP};border-radius:20px;padding:32px 40px;display:flex;flex-direction:column;gap:30px">'
         + p(f"font-size:32px;font-weight:700;color:{INK}", "새 노트북 만들기")
         + '<div style="display:flex;flex-direction:row;gap:18px;align-items:center">' + num(1, JP, 36) + p(f"font-size:28px;color:{INK}", "VS Code로 hello-uv 폴더 열기") + '</div>'
         + '<div style="display:flex;flex-direction:row;gap:18px;align-items:center">' + num(2, JP, 36) + p(f"font-size:28px;color:{INK}", "탐색기에서 새 파일") + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{JP}", NB) + '</div>'
         + '<div style="display:flex;flex-direction:row;gap:18px;align-items:center">' + num(3, JP, 36) + p(f"font-size:28px;color:{INK}", "오른쪽 위 커널로 .venv 고르기") + '</div>'
         + '<div style="display:flex;flex-direction:row;gap:18px;align-items:center">' + num(4, JP, 36) + p(f"font-size:28px;color:{INK}", "셀에 적고") + kbd("Shift+Enter", 26) + p(f"font-size:28px;color:{INK}", "로 실행") + '</div></div>')
o.append(caption("이번 챕터의 코드는 모두 노트북 셀에 적어요.", 880))
W("ready", o, "09에서 만든 hello-uv 폴더를 VS Code로 열고, 그 안에 basics.ipynb라는 새 노트북을 만들어요. 커널은 09에서 고른 .venv예요. 10에서 배운 변수 이름 규칙(스네이크 표기법)과 자료형 다섯 가지를 그대로 써요. 슬라이드의 출력은 tools/demo.sh가 hello-uv 커널에서 같은 셀을 실제로 실행한 결과예요. 셀 번호는 파트마다 [1]부터 다시 셌어요. 한 노트북에서 이어서 실행하면 번호가 계속 커져요.")

# ---------- part 1: variables ----------
EB1 = "1. 변수에 값 넣기"
o = [sec("assign")] + head(EB1, "= 는 오른쪽 값을 왼쪽 이름에 넣어요", BL)
o += cell({"id": "c-age", "lines": ["age = 25"], "n": 1}, 96, 220, CELL_W, sel="c-age")
o.append(p(f"position:absolute;left:96px;top:320px;width:{CELL_W}px;font-size:26px;line-height:1.5;color:{SUB}", "넣기만 해서 출력은 없어요. 값은 커널이 기억해요."))
o.append(var_box("box-age", "age", "", 1260, 220, attrs=' data-build-in="fade order 1"'))
o.append(f'<div id="v-age" data-build-in="pop order 3" style="position:absolute;left:1260px;top:290px;width:420px;height:160px;display:flex;align-items:center;justify-content:center">' + p(f"font-family:{MONO};font-size:72px;font-weight:700;color:{INK}", "25") + '</div>')
# big token line
toks = [("age", "이름", BL, 96), ("=", "넣어요", OR, 520), ("25", "값", GR, 820)]
o.append(f'<div style="position:absolute;left:96px;top:520px;width:1728px;height:330px;background:{CARD};border:2px solid {LINE};border-radius:24px"></div>')
for t, lbl, c, x in toks:
    o.append(p(f"position:absolute;left:{x + 120}px;top:560px;width:260px;font-family:{MONO};font-size:110px;font-weight:700;line-height:1.2;color:{c};text-align:center", e(t)))
    o.append(p(f"position:absolute;left:{x + 120}px;top:720px;width:260px;font-size:34px;font-weight:700;color:{c};text-align:center", lbl))
o.append(f'<div data-build-in="fade order 2" style="position:absolute;left:1240px;top:600px;width:520px;display:flex;flex-direction:column;align-items:center;gap:16px">'
         + f'<x-shape kind="arrow-left" style="width:300px;height:70px;background:{OR}"></x-shape>' + p(f"font-size:30px;font-weight:700;color:{OR}", "오른쪽에서 왼쪽으로 읽어요") + '</div>')
o.append(caption("수학의 '같다'가 아니에요. 25를 age라는 이름에 넣어요.", 900))
W("assign", o, "변수는 값에 붙인 이름이에요. 오른쪽 상자 그림처럼 age라는 이름의 상자에 25를 넣는다고 생각해요. 등호 = 는 수학처럼 양쪽이 같다는 뜻이 아니에요. 오른쪽 값을 왼쪽 이름에 넣으라는 명령이에요. 그래서 오른쪽에서 왼쪽으로 읽어요. 이름은 10에서 정한 대로 스네이크 표기법으로 적어요. 이 셀은 넣기만 해서 출력이 없고, 실행 번호 [1]만 생겨요.", ("var", "변수에 값 넣기"))

o = [sec("show")] + head(EB1, "넣은 값은 두 가지 방법으로 봐요", BL)
o.append(p(f"position:absolute;left:96px;top:210px;width:820px;font-size:30px;font-weight:700;color:{BL}", "셀 마지막 줄에 이름만 적기"))
o += cell({"id": "c-show1", "lines": ["age"], "n": 2, "out": ["25"]}, 96, 270, 820, attrs=' data-build-in="rise order 1"')
o.append(p(f"position:absolute;left:1004px;top:210px;width:820px;font-size:30px;font-weight:700;color:{BL}", "print()로 꺼내 보기"))
o += cell({"id": "c-show2", "lines": ["print(age)", 'print("나이:", age)'], "n": 3, "out": ["25", "나이: 25"]}, 1004, 270, 820, sel="c-show2", attrs=' data-build-in="rise order 2"')
o.append(card(1004, 560, 820, 280, p(f"font-size:28px;font-weight:700;color:{INK}", 'print("설명", 값)')
              + p(f"font-size:26px;line-height:1.5;color:{SUB}", "쉼표로 나누면 한 칸 띄워서 이어 보여 줘요.<br>따옴표 안 글자는 그대로, age는 값 25로 바뀌어요."), BL, ' data-build-in="rise order 3"'))
o.append(card(96, 560, 820, 280, p(f"font-size:28px;font-weight:700;color:{INK}", "이름만 적기")
              + p(f"font-size:26px;line-height:1.5;color:{SUB}", "10에서 본 대로 셀의 마지막 줄이<br>값이면 print 없이도 보여 줘요."), BL, ' data-build-in="rise order 1"'))
o.append(caption("빨리 확인할 땐 이름만, 설명을 붙일 땐 print(\"설명\", 값)을 써요.", 900))
W("show", o, "넣은 값을 보는 방법은 두 가지예요. 첫째, 셀 마지막 줄에 이름만 적으면 노트북이 그 값을 보여 줘요. 둘째, print()는 괄호 안의 값을 출력해요. 쉼표로 여러 개를 넣으면 한 칸씩 띄워서 한 줄로 보여 줘요. 따옴표로 감싼 글자는 그대로 나오고, 따옴표 없는 age는 그 안의 값 25로 바뀌어요. 이 챕터의 예제는 이 두 방법만 써요.")

o = [sec("reassign")] + head(EB1, "다시 넣으면 새 값으로 바뀌어요", BL)
o += cell({"id": "c-age", "lines": ["age = 26", "age"], "n": 4, "out": ["26"]}, 96, 220, CELL_W, sel="c-age")
o.append(var_box("box-age", "age", "", 1260, 220))
o.append(f'<div id="v-old" data-build-in="fade order 1" style="position:absolute;left:1260px;top:470px;width:420px;display:flex;flex-direction:row;align-items:center;justify-content:center;gap:16px">'
         + p(f"font-size:26px;color:{GRAY}", "예전 값") + p(f"font-family:{MONO};font-size:44px;font-weight:700;color:{GRAY};text-decoration:line-through", "25") + '</div>')
o.append(f'<div id="v-age26" data-build-in="pop order 1" style="position:absolute;left:1260px;top:290px;width:420px;height:160px;display:flex;align-items:center;justify-content:center">' + p(f"font-family:{MONO};font-size:72px;font-weight:700;color:{INK}", "26") + '</div>')
o.append(card(96, 600, 1728, 220, '<div style="display:flex;flex-direction:row;align-items:center;gap:30px">'
              + f'<x-icon name="Lightbulb" style="width:52px;height:52px;color:{OR}"></x-icon>'
              + p(f"flex:1;font-size:30px;line-height:1.5;color:{INK}", "상자 하나에는 값이 하나만 들어가요.<br>새 값을 넣으면 예전 값 25는 사라져요.") + '</div>', None, ' data-build-in="rise order 2"', "justify-content:center"))
o.append(caption("같은 이름에 넣을수록 마지막에 넣은 값만 남아요.", 900))
W("reassign", o, "같은 이름에 다시 값을 넣으면 예전 값을 지우고 새 값을 넣어요. 변수라는 이름도 값이 변할 수 있어서 붙었어요. age에 26을 넣고 마지막 줄에 age를 적어서 26이 보여요. 예전 값 25는 더 이상 꺼낼 수 없어요. 셀 번호가 [4]인 건 앞 장의 두 셀 [2], [3]을 실행한 다음이라서예요.")

o = [sec("update", "magic")] + head(EB1, "age = age + 1은 오른쪽부터 계산해요", BL)
o += cell({"id": "c-age", "lines": ["age = age + 1", "age"], "n": 5, "out": ["27"]}, 96, 220, CELL_W, sel="c-age")
o.append(var_box("box-age", "age", "", 1260, 220))
o.append(f'<div id="v-age27" data-build-in="pop order 3" style="position:absolute;left:1260px;top:290px;width:420px;height:160px;display:flex;align-items:center;justify-content:center">' + p(f"font-family:{MONO};font-size:72px;font-weight:700;color:{INK}", "27") + '</div>')
steps_ = [("오른쪽 age를 읽어요", "age  →  26"), ("계산해요", "26 + 1  →  27"), ("왼쪽 age에 넣어요", "age  ←  27")]
for i, (a_, b_) in enumerate(steps_):
    x = 96 + i * 584
    o.append(card(x, 520, 560, 300, '<div style="display:flex;flex-direction:row;align-items:center;gap:16px">' + num(i + 1, BL, 36) + p(f"font-size:30px;font-weight:700;color:{INK}", a_) + '</div>'
                  + '<div style="flex:1"></div>' + mono(b_, 34, BL, "#E9EFFB", "align-self:flex-start"), BL, f' data-build-in="rise order {i + 1}"'))
o.append(caption("10에서 실행한 x = x + 1도 같은 순서로 계산했어요.", 900))
W("update", o, "수학이라면 age = age + 1은 말이 안 되는 식이에요. 파이썬은 = 오른쪽을 먼저 계산해요. 1단계에서 지금 age에 든 26을 읽고, 2단계에서 1을 더해 27을 만들고, 3단계에서 그 27을 다시 age에 넣어요. 10의 실행 번호 장에서 x = x + 1을 두 번 실행했을 때 11, 12로 바뀐 것도 같은 원리예요. 이 셀도 실행할 때마다 1씩 커져요.")

o = [sec("last-line")] + head(EB1, "이름만 적으면 마지막 줄만 보여요", BL)
o.append(p(f"position:absolute;left:96px;top:210px;width:820px;font-size:30px;font-weight:700;color:{RED}", "age는 안 보여요"))
o += cell({"id": "c-ll1", "lines": ['user_name = "kim"', "age", "user_name"], "n": 6, "out": ["'kim'"]}, 96, 270, 820)
o.append(f'<div data-build-in="fade order 1" style="position:absolute;left:184px;top:314px;width:96px;height:44px;border:3px dashed {RED};border-radius:10px;background:rgba(163,49,49,.08)"></div>')
o.append(p(f"position:absolute;left:96px;top:500px;width:820px;font-size:26px;line-height:1.5;color:{SUB}", "가운데 줄 age는 실행은 되지만 화면에 나오지 않아요.", ' data-build-in="fade order 1"'))
o.append(p(f"position:absolute;left:1004px;top:210px;width:820px;font-size:30px;font-weight:700;color:{GR}", "print는 둘 다 보여요", ' data-build-in="fade order 2"'))
o += cell({"id": "c-ll2", "lines": ["print(age)", "print(user_name)"], "n": 7, "out": ["27", "kim"]}, 1004, 270, 820, sel="c-ll2", attrs=' data-build-in="rise order 2"')
o.append(card(96, 620, 1728, 200, '<div style="display:flex;flex-direction:row;align-items:center;gap:30px">'
              + mono("'kim'", 36) + p(f"font-size:28px;color:{SUB}", "이름만 적기는 따옴표까지") + '<div style="width:40px"></div>'
              + mono("kim", 36) + p(f"font-size:28px;color:{SUB}", "print는 글자만") + '</div>', None, ' data-build-in="rise order 3"', "justify-content:center"))
o.append(caption("여러 값을 보고 싶으면 줄마다 print()를 써요.", 900))
W("last-line", o, "셀 마지막 줄에 이름만 적는 방법은 딱 한 줄, 맨 마지막 줄만 보여 줘요. 왼쪽 셀에서 age 줄도 실행은 됐지만 화면에는 나오지 않았어요. 값을 여러 개 보고 싶으면 오른쪽처럼 줄마다 print()를 써요. 출력 모양도 조금 달라요. 이름만 적으면 문자열이라는 걸 알려 주려고 따옴표까지 보여 주고, print는 글자만 보여 줘요. age가 27인 건 앞 장의 셀을 실행한 뒤라서예요.")

o = [sec("name-err")] + head(EB1, "이름을 틀리게 적으면 NameError가 나요", BL)
o += cell({"id": "c-ne", "lines": ["Age"], "n": 8, "out": ["NameError: name 'Age' is not defined"], "err": True}, 96, 220, 1100, sel="c-ne")
o.append(card(96, 420, 840, 360, p(f"font-size:30px;font-weight:700;color:{INK}", "대문자와 소문자는 다른 이름이에요")
              + '<div style="display:flex;flex-direction:row;align-items:center;gap:20px">' + mono("age", 40, GR, "#E6F4EC") + p(f"font-size:28px;color:{SUB}", "넣은 이름") + '</div>'
              + '<div style="display:flex;flex-direction:row;align-items:center;gap:20px">' + mono("Age", 40, RED, "#F8E6E6") + p(f"font-size:28px;color:{SUB}", "한 번도 넣은 적 없는 이름") + '</div>', RED, ' data-build-in="rise order 1"'))
o.append(card(984, 420, 840, 360, p(f"font-size:30px;font-weight:700;color:{INK}", "이럴 때도 같은 오류가 나요")
              + p(f"font-size:28px;line-height:1.6;color:{SUB}", "• 철자를 틀렸어요 (agee)<br>• 넣는 셀을 아직 실행하지 않았어요<br>• Restart 뒤에 아래 셀만 실행했어요"), RED, ' data-build-in="rise order 2"'))
o.append(caption("NameError가 나면 철자부터 보고, 넣는 셀을 실행했는지 봐요.", 900))
W("name-err", o, "NameError는 파이썬이 모르는 이름을 썼다는 뜻이에요. 파이썬은 대문자와 소문자를 다른 글자로 봐서, age에 값을 넣었어도 Age는 모르는 이름이에요. 철자를 하나 틀려도 같은 오류가 나요. 10에서 본 것처럼 Restart 뒤에 넣는 셀을 건너뛰고 아래 셀만 실행해도 나요. 그럴 땐 Run All로 위에서부터 다시 실행해요. 출력은 Traceback 위쪽 줄을 빼고 마지막 줄만 옮겼어요.")

# ---------- part 2: types ----------
EBT = "2. 변수 타입"
TT = NAVY
TYPES4 = [("25", "int", "정수", "소수점 없는 숫자", BL), ("172.5", "float", "실수", "소수점 있는 숫자", NAVY), ('"kim"', "str", "문자열", "따옴표로 감싼 글자", GR), ("False", "bool", "불리언", "True 또는 False", PUR)]
o = [sec("types")] + head(EBT, "값마다 타입이 있어요", TT)
o += cell({"id": "c-ty", "lines": ["age = 25", "height = 172.5", 'user_name = "kim"', "is_member = False", "print(type(age))", "print(type(height))", "print(type(user_name))", "print(type(is_member))"],
           "n": 1, "out": [f"<class '{t[1]}'>" for t in TYPES4]}, 96, 210, 820, sel="c-ty")
for i, (v, t, k, d, c) in enumerate(TYPES4):
    x, y = 980 + (i % 2) * 432, 210 + (i // 2) * 330
    o.append(card(x, y, 412, 306, '<div style="display:flex;flex-direction:row;align-items:baseline;gap:14px">' + p(f"font-size:34px;font-weight:700;color:{c}", k)
                  + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{GRAY}", t) + '</div>'
                  + mono(v, 40, INK, "#F6F5F1", "align-self:flex-start") + '<div style="flex:1"></div>' + p(f"font-size:24px;color:{SUB}", d), c, f' data-build-in="rise order {i + 1}"'))
o.append(caption("타입은 값의 종류예요. 10에서 본 자료형과 같은 말이에요.", 900))
W("types", o, "변수에 넣는 값에는 종류가 있어요. 이 종류를 타입 또는 자료형이라고 불러요. 10의 22, 23쪽에서 다섯 가지를 type()으로 확인했어요. 이번 챕터에서 계산과 비교에 쓰는 네 가지를 다시 봐요. 정수 int, 실수 float, 문자열 str, 불리언 bool이에요. 리스트는 10에서 본 대로 여러 값을 묶는 타입이고, 뒤에서 따로 배워요. 출력은 hello-uv 커널에서 실제로 실행한 결과예요. 이 파트도 새 커널이라서 셀 번호가 [1]부터 시작해요.", ("types", "변수 타입"))

o = [sec("type-follows")] + head(EBT, "타입은 이름이 아니라 값을 따라가요", TT)
o += cell({"id": "c-tf", "lines": ["x = 10", "print(type(x))", 'x = "ten"', "print(type(x))"], "n": 2, "out": ["<class 'int'>", "<class 'str'>"]}, 96, 220, 820, sel="c-tf")
for i, (v, t, c) in enumerate([("10", "int", BL), ('"ten"', "str", GR)]):
    x = 1000 + i * 440
    o.append(f'<div data-build-in="pop order {i * 2 + 1}" style="position:absolute;left:{x}px;top:220px;width:360px;display:flex;flex-direction:column;align-items:center;gap:16px">'
             + f'<div style="width:360px;height:220px;background:{CARD};border:3px solid {TT};border-radius:22px;display:flex;flex-direction:column;overflow:hidden">'
             + p(f"height:64px;flex:none;background:{TT};color:#FFFFFF;font-family:{MONO};font-size:32px;font-weight:700;line-height:64px;padding:0 24px", "x")
             + '<div style="flex:1;display:flex;align-items:center;justify-content:center">' + p(f"font-family:{MONO};font-size:60px;font-weight:700;color:{INK}", e(v)) + '</div></div>'
             + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{c};background:#F1F0EC;border-radius:10px;padding:4px 18px", t) + '</div>')
o.append(f'<x-shape kind="arrow-right" data-build-in="fade order 2" style="position:absolute;left:1370px;top:310px;width:60px;height:40px;background:#C9CED8"></x-shape>')
o.append(card(96, 600, 1728, 220, '<div style="display:flex;flex-direction:row;align-items:center;gap:30px">'
              + f'<x-icon name="Lightbulb" style="width:52px;height:52px;color:{OR}"></x-icon>'
              + p(f"flex:1;font-size:30px;line-height:1.5;color:{INK}", "이름 x는 그대로인데, 넣은 값이 바뀌니 타입도 바뀌었어요.<br>타입을 미리 정하지 않아도 넣는 값을 보고 정해져요.") + '</div>', None, ' data-build-in="rise order 4"', "justify-content:center"))
o.append(caption("한 이름에는 한 가지 뜻의 값만 넣어요. 헷갈리면 type()으로 확인해요.", 900))
W("type-follows", o, "파이썬은 변수를 만들 때 타입을 따로 적지 않아요. 넣은 값을 보고 타입이 정해져요. 그래서 같은 x에 10을 넣으면 int, \"ten\"을 넣으면 str이 돼요. 다른 언어 중에는 변수마다 타입을 정해 두고 다른 값을 못 넣게 하는 언어도 있어요. 파이썬은 자유로운 대신 실수하기 쉬워서, 나이를 넣던 이름에 갑자기 글자를 넣는 일은 피해요.")

o = [sec("quotes")] + head(EBT, "따옴표 하나로 숫자가 글자가 돼요", TT)
o += cell({"id": "c-q", "lines": ["print(type(25))", 'print(type("25"))', "print(25 + 1)", 'print("25" + "1")'], "n": 3, "out": ["<class 'int'>", "<class 'str'>", "26", "251"]}, 96, 220, 820, sel="c-q")
for i, (v, t, calc, r, d, c) in enumerate([("25", "int", "25 + 1", "26", "숫자끼리 더해요", BL), ('"25"', "str", '"25" + "1"', "251", "글자끼리 이어 붙여요", GR)]):
    y = 220 + i * 320
    o.append(card(980, y, 844, 290, '<div style="display:flex;flex-direction:row;align-items:center;gap:20px">' + mono(v, 44, c, "#F6F5F1")
                  + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{GRAY}", t) + '</div>'
                  + '<div style="display:flex;flex-direction:row;align-items:center;gap:16px">' + mono(calc, 30)
                  + f'<x-shape kind="arrow-right" style="width:40px;height:24px;flex:none;background:#C9CED8"></x-shape>' + p(f"font-family:{MONO};font-size:36px;font-weight:700;color:{c}", r) + '</div>'
                  + p(f"font-size:26px;color:{SUB}", d), c, f' data-build-in="rise order {i + 1}"'))
o.append(caption("겉모습이 숫자여도 따옴표 안에 있으면 str이에요.", 900))
W("quotes", o, "25와 \"25\"는 화면에서는 비슷해 보여도 타입이 달라요. 따옴표가 없으면 int라서 + 가 더하기가 되고, 따옴표가 있으면 str이라서 + 가 이어 붙이기가 돼요. 그래서 \"25\" + \"1\"은 26이 아니라 251이에요. print는 따옴표를 빼고 보여 줘서 출력만 보면 구분이 안 돼요. 헷갈리면 type()으로 확인해요. 파일이나 사용자 입력에서 읽은 숫자는 대부분 글자로 들어와서 실제로 자주 만나는 문제예요.")

o = [sec("convert")] + head(EBT, "int(), float(), str()로 타입을 바꿔요", TT)
o += cell({"id": "c-cv", "lines": ['print(int("3") + 3)', 'print(str(3) + "3")', 'print(float("3.5"))', "print(int(3.9))"], "n": 4, "out": ["6", "33", "3.5", "3"]}, 96, 220, 760, sel="c-cv")
cv = [('int("3")', "3", "글자를 정수로", BL), ("str(3)", "'3'", "숫자를 글자로", GR), ('float("3.5")', "3.5", "글자를 실수로", NAVY), ("int(3.9)", "3", "소수점 아래는 버려요", OR)]
for i, (code, r, d, c) in enumerate(cv):
    x, y = 920 + (i % 2) * 464, 220 + (i // 2) * 330
    o.append(card(x, y, 440, 306, p(f"font-size:28px;font-weight:700;color:{c}", d) + '<div style="flex:1"></div>'
                  + mono(code, 32, INK, "#F6F5F1", "align-self:flex-start") + '<div style="display:flex;flex-direction:row;align-items:center;gap:16px">'
                  + f'<x-shape kind="arrow-right" style="width:40px;height:24px;flex:none;background:#C9CED8"></x-shape>' + p(f"font-family:{MONO};font-size:36px;font-weight:700;color:{c}", e(r)) + '</div>',
                  c, f' data-build-in="rise order {i + 1}"'))
o.append(caption("바꾸고 싶은 타입 이름을 함수처럼 쓰고 괄호 안에 값을 넣어요.", 900))
W("convert", o, "타입 이름 int, float, str을 type()처럼 괄호와 함께 쓰면 그 타입으로 바꾼 값을 돌려줘요. int(\"3\")은 글자 3을 정수 3으로 바꿔서 3을 더하면 6이 돼요. str(3)은 반대로 숫자를 글자로 바꿔서 \"3\"과 이어 붙이면 33이에요. int(3.9)는 반올림이 아니라 소수점 아래를 버려서 3이에요. 원래 변수의 값은 그대로이고, 바꾼 값을 쓰려면 age = int(age)처럼 다시 넣어요.")

o = [sec("convert-err")] + head(EBT, "숫자로 못 읽는 글자는 ValueError가 나요", TT)
o += cell({"id": "c-ce1", "lines": ['int("삼")'], "n": 5, "out": ["ValueError: invalid literal for int() with base 10: '삼'"], "err": True}, 96, 220, 1728, attrs=' data-build-in="rise order 1"')
o += cell({"id": "c-ce2", "lines": ['int("3.5")'], "n": 6, "out": ["ValueError: invalid literal for int() with base 10: '3.5'"], "err": True}, 96, 360, 1728, sel="c-ce2", attrs=' data-build-in="rise order 2"')
o.append(card(96, 540, 840, 280, p(f"font-size:30px;font-weight:700;color:{INK}", "한글 숫자는 못 읽어요")
              + p(f"font-size:26px;line-height:1.5;color:{SUB}", "int()는 0부터 9까지 숫자 글자만 읽어요.<br>\"삼\"은 사람에게만 숫자예요."), RED, ' data-build-in="rise order 3"'))
o.append(card(984, 540, 840, 280, p(f"font-size:30px;font-weight:700;color:{INK}", "소수점 글자는 float()로")
              + '<div style="display:flex;flex-direction:row;align-items:center;gap:16px">' + mono('float("3.5")', 30)
              + f'<x-shape kind="arrow-right" style="width:40px;height:24px;flex:none;background:#C9CED8"></x-shape>' + p(f"font-family:{MONO};font-size:34px;font-weight:700;color:{NAVY}", "3.5") + '</div>'
              + p(f"font-size:24px;color:{SUB}", "앞 장에서 실행한 결과예요"), NAVY, ' data-build-in="rise order 4"'))
o.append(caption("ValueError는 타입은 맞는데 값을 바꿀 수 없다는 뜻이에요.", 900))
W("convert-err", o, "int()에 숫자로 읽을 수 없는 글자를 넣으면 ValueError가 나요. 메시지의 base 10은 10진수로 읽으려 했다는 뜻이에요. 한글 \"삼\"은 사람에게는 숫자지만 파이썬은 못 읽어요. \"3.5\"처럼 소수점이 있는 글자도 int()는 바로 못 읽어요. 그럴 땐 float(\"3.5\")로 바꿔요. 앞 장의 int(3.9)는 글자가 아니라 실수를 넣어서 오류 없이 3이 됐어요. 출력은 Traceback의 마지막 줄만 옮겼어요.")

# ---------- part 3: arithmetic ----------
EB2 = "3. 사칙연산"
T2 = TEAL
o = [sec("ops4")] + head(EB2, "더하기, 빼기, 곱하기, 나누기", T2)
o += cell({"id": "c-ops", "lines": ["print(7 + 3)", "print(7 - 3)", "print(7 * 3)", "print(7 / 3)"], "n": 1, "out": ["10", "4", "21", "2.3333333333333335"]}, 96, 220, 760, sel="c-ops")
ops = [("+", "더하기", "7 + 3", "10", ""), ("-", "빼기", "7 - 3", "4", ""), ("*", "곱하기", "7 * 3", "21", "× 대신 별표"), ("/", "나누기", "7 / 3", "2.333…", "÷ 대신 빗금")]
for i, (s, n_, ex, r, note) in enumerate(ops):
    x, y = 920 + (i % 2) * 464, 220 + (i // 2) * 330
    o.append(card(x, y, 440, 306, '<div style="display:flex;flex-direction:row;align-items:center;gap:20px">'
                  + p(f"width:90px;height:90px;flex:none;border-radius:20px;background:#E3F3F4;font-family:{MONO};font-size:60px;font-weight:700;line-height:90px;text-align:center;color:{T2}", e(s))
                  + '<div style="display:flex;flex-direction:column;gap:4px">' + p(f"font-size:32px;font-weight:700;color:{INK}", n_) + (p(f"font-size:22px;color:{GRAY}", note) if note else "") + '</div></div>'
                  + '<div style="flex:1"></div><div style="display:flex;flex-direction:row;align-items:center;gap:16px">' + mono(ex, 30)
                  + f'<x-shape kind="arrow-right" style="width:40px;height:24px;flex:none;background:#C9CED8"></x-shape>' + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:{T2}", e(r)) + '</div>',
                  T2, f' data-build-in="rise order {i + 1}"'))
o.append(caption("키보드에 ×, ÷가 없어서 곱하기는 *, 나누기는 / 를 써요.", 900))
W("ops4", o, "사칙연산 기호예요. 더하기와 빼기는 수학과 같아요. 곱하기는 별표 *, 나누기는 빗금 / 를 써요. 셀 하나에 print 네 줄을 적어서 네 결과를 한 번에 봤어요. 7 나누기 3은 끝이 2.3333333333333335로 나와요. 컴퓨터가 소수를 저장하는 방식 때문에 마지막 자리가 조금 어긋나요. 지금은 그냥 2.333...으로 읽으면 돼요. 기호 양옆에 한 칸씩 띄워 적으면 읽기 쉬워요.", ("calc", "사칙연산"))

o = [sec("div")] + head(EB2, "/ 로 나누면 항상 소수점이 붙어요", T2)
o += cell({"id": "c-div", "lines": ["6 / 2"], "n": 2, "out": ["3.0"]}, 96, 220, 760, sel="c-div")
o.append(card(96, 420, 760, 400, p(f"font-size:30px;font-weight:700;color:{INK}", "딱 나눠떨어져도")
              + '<div style="display:flex;flex-direction:row;align-items:center;gap:24px">' + mono("6 / 2", 44)
              + f'<x-shape kind="arrow-right" style="width:60px;height:36px;flex:none;background:{T2}"></x-shape>' + mono("3.0", 44, T2, "#E3F3F4") + '</div>'
              + p(f"font-size:26px;line-height:1.5;color:{SUB}", "3이 아니라 3.0이에요."), T2, ' data-build-in="rise order 1"'))
for i, (v, t, k, c) in enumerate([("3", "int", "정수", BL), ("3.0", "float", "실수", NAVY)]):
    y = 220 + i * 300
    o.append(card(940, y, 884, 270, '<div style="display:flex;flex-direction:row;align-items:center;gap:30px">' + mono(v, 60, c, "#F1F0EC")
                  + '<div style="display:flex;flex-direction:column;gap:6px">' + '<div style="display:flex;flex-direction:row;align-items:baseline;gap:14px">' + p(f"font-size:34px;font-weight:700;color:{c}", k)
                  + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{GRAY}", t) + '</div>'
                  + p(f"font-size:26px;color:{SUB}", "소수점 없는 숫자" if t == "int" else "소수점 있는 숫자. / 의 결과는 늘 이쪽") + '</div></div>', c, f' data-build-in="rise order {i + 2}"', "justify-content:center"))
o.append(caption("값은 같아도 타입이 달라요. 2파트에서 본 int와 float예요.", 900))
W("div", o, "나누기 / 의 결과는 나눠떨어져도 항상 실수(float)예요. 6 / 2는 3이 아니라 3.0으로 나와요. 계산한 값은 같지만 타입이 달라요. 2파트에서 본 int와 float예요. 7 + 3처럼 정수끼리 더하면 int, 7 + 0.5처럼 실수가 섞이면 float가 돼요. type()으로 실제로 확인한 결과예요. 소수점 없는 몫만 필요하면 다음 장의 // 를 써요.")

o = [sec("ops3")] + head(EB2, "몫 //, 나머지 %, 거듭제곱 **", T2)
o.append(p(f"position:absolute;left:96px;top:210px;width:1000px;font-size:30px;font-weight:700;color:{INK}", "사탕 7개를 3개씩 나누면"))
for g in range(2):
    o.append(f'<div data-build-in="fade order 2" style="position:absolute;left:{96 + g * 330}px;top:280px;width:300px;height:130px;border:4px dashed {T2};border-radius:24px"></div>')
for i in range(7):
    x = 96 + (i // 3) * 330 + 26 + (i % 3) * 86 if i < 6 else 96 + 2 * 330 + 26
    o.append(f'<x-shape kind="ellipse" data-build-in="pop order 1" style="position:absolute;left:{x}px;top:305px;width:76px;height:76px;background:{OR if i == 6 else T2}"></x-shape>')
o.append(f'<div data-build-in="rise order 3" style="position:absolute;left:96px;top:430px;width:630px;display:flex;flex-direction:row;justify-content:center;gap:16px">' + p(f"font-size:30px;font-weight:700;color:{T2}", "몫 2") + p(f"font-size:26px;color:{SUB}", "(묶음 수)") + '</div>')
o.append(f'<div data-build-in="rise order 3" style="position:absolute;left:700px;top:430px;width:220px;display:flex;flex-direction:column;align-items:center">' + p(f"font-size:30px;font-weight:700;color:{OR}", "나머지 1") + '</div>')
o += cell({"id": "c-ops3", "lines": ["print(7 // 3)", "print(7 % 3)", "print(2 ** 3)"], "n": 3, "out": ["2", "1", "8"]}, 1100, 220, 724, sel="c-ops3", attrs=' data-build-in="rise order 4"')
o3 = [("//", "몫", "7 // 3  →  2", "나누고 소수점 아래는 버려요", T2), ("%", "나머지", "7 % 3  →  1", "나누고 남은 수", OR), ("**", "거듭제곱", "2 ** 3  →  8", "2 × 2 × 2", PUR)]
for i, (s, n_, ex, d, c) in enumerate(o3):
    x = 96 + i * 584
    o.append(card(x, 560, 560, 270, '<div style="display:flex;flex-direction:row;align-items:center;gap:18px">' + mono(s, 40, c, "#F1F0EC") + p(f"font-size:32px;font-weight:700;color:{INK}", n_) + '</div>'
                  + mono(ex, 28, INK, "transparent", "padding:0") + p(f"font-size:24px;color:{SUB}", d), c, f' data-build-in="rise order {i + 5}"'))
o.append(caption("% 는 퍼센트가 아니라 나머지예요.", 900))
W("ops3", o, "사칙연산 말고 자주 쓰는 연산 세 가지예요. 사탕 7개를 3개씩 묶으면 두 묶음이 되고 하나가 남아요. 묶음 수 2가 몫이고, 남은 1개가 나머지예요. // 는 빗금 두 개로 몫만 구해요. 소수점 아래를 버리니까 결과가 정수예요. % 는 나머지예요. 퍼센트 기호지만 파이썬에서는 나머지를 구해요. 짝수인지 볼 때 숫자 % 2가 0인지 확인하는 식으로 많이 써요. ** 는 별표 두 개로 거듭제곱이에요. 2 ** 3은 2를 세 번 곱한 8이에요.")

o = [sec("order")] + head(EB2, "곱하기를 더하기보다 먼저 계산해요", T2)
for k, (code, rows, cid, n_, out_, x) in enumerate([("2 + 3 * 4", [("2 + 3 * 4", "3 * 4 먼저"), ("2 + 12", "그다음 더하기"), ("14", "")], "c-o1", 4, "14", 96),
                                                   ("(2 + 3) * 4", [("(2 + 3) * 4", "괄호 먼저"), ("5 * 4", "그다음 곱하기"), ("20", "")], "c-o2", 5, "20", 984)]):
    o += cell({"id": cid, "lines": [code], "n": n_, "out": [out_]}, x, 220, 840, attrs=f' data-build-in="rise order {k * 3 + 1}"' if k else "")
    for i, (ex, lbl) in enumerate(rows):
        y = 400 + i * 100
        last = i == len(rows) - 1
        o.append(f'<div data-build-in="rise order {k * 3 + i + 1}" style="position:absolute;left:{x}px;top:{y}px;width:840px;height:84px;display:flex;flex-direction:row;align-items:center;gap:24px">'
                 + mono(ex, 40, T2 if last else INK, "#E3F3F4" if last else "#F1F0EC") + p(f"font-size:26px;color:{SUB}", lbl) + '</div>')
pri = ["( )", "**", "* / // %", "+ -"]
o.append(f'<div data-build-in="rise order 7" style="position:absolute;left:96px;top:720px;width:1728px;height:130px;background:{CARD};border:2px solid {LINE};border-radius:20px;padding:0 36px;display:flex;flex-direction:row;align-items:center;gap:22px">'
         + p(f"font-size:28px;font-weight:700;color:{INK};white-space:nowrap", "먼저 하는 순서")
         + f'<x-shape kind="arrow-right" style="width:40px;height:24px;flex:none;background:#C9CED8"></x-shape>'.join(mono(t, 32, T2, "#E3F3F4") for t in pri) + '</div>')
o.append(caption("헷갈리면 먼저 할 계산을 괄호로 묶어요.", 900))
W("order", o, "파이썬도 수학처럼 곱하기와 나누기를 더하기와 빼기보다 먼저 계산해요. 2 + 3 * 4는 3 * 4를 먼저 해서 12, 거기에 2를 더해 14예요. 더하기를 먼저 하고 싶으면 괄호로 묶어요. (2 + 3) * 4는 5 * 4라서 20이에요. 아래 줄은 먼저 하는 순서예요. 괄호가 가장 먼저, 그다음 거듭제곱, 곱하기 무리, 더하기 무리 순서예요. 순서를 외우기보다 헷갈릴 때 괄호를 치는 게 안전해요.")

LEVELS = [("( )", "괄호", "가장 먼저", NAVY), ("**", "거듭제곱", "", PUR), ("*  /  //  %", "곱하기, 나누기, 몫, 나머지", "넷은 같은 순위", T2), ("+  -", "더하기, 빼기", "가장 나중", OR)]
o = [sec("order-ladder")] + head(EB2, "계산 순위는 네 단계예요", T2)
for i, (sym, nm, note, c) in enumerate(LEVELS):
    x, y = 96 + i * 150, 220 + i * 150
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:{x}px;top:{y}px;width:{1728 - i * 150 - 430}px;height:130px;background:{CARD};border:2px solid {LINE};border-left:14px solid {c};border-radius:18px;padding:0 30px;display:flex;flex-direction:row;align-items:center;gap:26px">'
             + num(i + 1, c, 44) + mono(sym, 38, c, "#F6F5F1") + '<div style="display:flex;flex-direction:column;gap:4px">' + p(f"font-size:30px;font-weight:700;color:{INK}", nm)
             + (p(f"font-size:22px;color:{SUB}", note) if note else "") + '</div></div>')
o.append(card(1424, 220, 400, 580, p(f"font-size:28px;font-weight:700;color:{INK}", "몫과 나머지는")
              + p(f"font-size:26px;line-height:1.6;color:{SUB}", "// 와 % 는 곱하기, 나누기와 같은 3단계예요.<br><br>** 는 그보다 한 단계 위라서 먼저 계산해요.<br><br>같은 단계끼리는 왼쪽부터 풀어요."),
              T2, ' data-build-in="rise order 5"'))
o.append(caption("위 계단부터 풀어요. 같은 계단에서는 왼쪽부터예요.", 900))
W("order-ladder", o, "파이썬이 계산하는 순서를 네 계단으로 그렸어요. 1단계 괄호가 가장 먼저예요. 2단계는 거듭제곱 ** 예요. 3단계는 곱하기 *, 나누기 /, 몫 //, 나머지 % 네 가지가 같은 순위예요. 몫과 나머지를 따로 떼어 생각하기 쉬운데 곱하기, 나누기와 한 묶음이에요. 4단계가 더하기와 빼기예요. 같은 단계끼리 만나면 왼쪽부터 차례로 풀어요. 예외가 하나 있는데, 2 ** 3 ** 2처럼 거듭제곱끼리는 오른쪽부터 풀어서 3 ** 2 = 9를 먼저 하고 2 ** 9 = 512가 돼요. 실제로 실행해 확인한 값이에요. 이런 식은 괄호로 묶어 쓰는 게 좋아요.")


def steps_card(x, y, w, rows, start, c, h=None):
    """Rows of (expression, note) shown one per click; the last row is the answer."""
    o = []
    for i, (ex, note) in enumerate(rows):
        last = i == len(rows) - 1
        o.append(f'<div data-build-in="rise order {start + i}" style="position:absolute;left:{x}px;top:{y + i * 76}px;width:{w}px;height:66px;display:flex;flex-direction:row;align-items:center;gap:20px">'
                 + mono(ex, 32, c if last else INK, "#E3F3F4" if last else "#F1F0EC") + p(f"font-size:24px;color:{SUB};white-space:nowrap", e(note)) + '</div>')
    return o


o = [sec("order-pow")] + head(EB2, "** 는 곱하기와 몫보다 먼저 계산해요", T2)
o += cell({"id": "c-op", "lines": ["print(2 ** 3 // 3)", "print(2 * 3 ** 2)", "print(-2 ** 2)", "print((-2) ** 2)"], "n": 6, "out": ["2", "18", "-4", "4"]}, 96, 210, 560, sel="c-op")
ex_ = [("2 ** 3 // 3", [("2 ** 3 // 3", "** 먼저"), ("8 // 3", "그다음 몫"), ("2", "")]),
       ("2 * 3 ** 2", [("2 * 3 ** 2", "** 먼저"), ("2 * 9", "그다음 곱하기"), ("18", "")]),
       ("-2 ** 2", [("-2 ** 2", "2 ** 2 먼저"), ("-4", "빼기 기호는 나중")]),
       ("(-2) ** 2", [("(-2) ** 2", "괄호 먼저"), ("4", "")])]
for k, (_, rows) in enumerate(ex_):
    x, y = 720 + (k % 2) * 560, 210 + (k // 2) * 320
    o.append(f'<div style="position:absolute;left:{x - 16}px;top:{y - 10}px;width:540px;height:{rows.__len__() * 76 + 20}px;border-left:4px solid {LINE}"></div>')
    o += steps_card(x, y, 520, rows, 1 + sum(len(r) for _, r in ex_[:k]), T2)
o.append(caption("-2 ** 2는 -4예요. 음수를 거듭제곱하려면 (-2)처럼 괄호로 묶어요.", 900))
W("order-pow", o, "거듭제곱은 곱하기와 몫보다 한 단계 위라서 먼저 풀어요. 2 ** 3 // 3은 2 ** 3 = 8을 먼저 하고 8 // 3 = 2예요. 왼쪽부터 3 // 3을 먼저 한다고 생각하면 1이 나와서 틀려요. 2 * 3 ** 2도 3 ** 2 = 9가 먼저라서 18이에요. -2 ** 2는 많이 헷갈려요. 앞의 빼기 기호보다 ** 가 먼저라서 -(2 ** 2) = -4가 돼요. -2를 제곱하고 싶으면 (-2) ** 2처럼 괄호로 묶어서 4를 얻어요. 출력은 같은 셀을 실제로 실행한 결과예요.")

o = [sec("order-same")] + head(EB2, "같은 순위끼리는 왼쪽부터 풀어요", T2)
o += cell({"id": "c-os", "lines": ["print(10 - 4 + 2)", "print(8 / 2 * 4)", "print(7 // 2 * 2)"], "n": 7, "out": ["8", "16.0", "6"]}, 96, 210, 560, sel="c-os")
same = [([("10 - 4 + 2", "왼쪽 빼기 먼저"), ("6 + 2", ""), ("8", "")], "10 - 6 = 4가 아니에요"),
        ([("8 / 2 * 4", "왼쪽 나누기 먼저"), ("4.0 * 4", ""), ("16.0", "")], "8 / 8 = 1이 아니에요"),
        ([("7 // 2 * 2", "왼쪽 몫 먼저"), ("3 * 2", ""), ("6", "")], "// 와 * 도 같은 순위")]
for k, (rows, warn) in enumerate(same):
    x = 720 + k * 372
    for i, (ex, note) in enumerate(rows):
        last = i == len(rows) - 1
        o.append(f'<div data-build-in="rise order {k * 4 + i + 1}" style="position:absolute;left:{x}px;top:{210 + i * 110}px;width:352px;display:flex;flex-direction:column;gap:6px">'
                 + mono(ex, 32, T2 if last else INK, "#E3F3F4" if last else "#F1F0EC", "align-self:flex-start") + (p(f"font-size:22px;color:{SUB}", e(note)) if note else "") + '</div>')
    o.append(f'<div data-build-in="pop order {k * 4 + 4}" style="position:absolute;left:{x}px;top:560px;width:352px;display:flex;flex-direction:row;align-items:center;gap:10px">'
             + f'<x-icon name="Warning" style="width:32px;height:32px;flex:none;color:{OR}"></x-icon>' + p(f"font-size:22px;font-weight:700;color:{OR}", e(warn)) + '</div>')
o.append(card(96, 660, 1728, 170, '<div style="display:flex;flex-direction:row;align-items:center;gap:30px">' + p(f"font-size:30px;font-weight:700;color:{INK}", "8 ÷ 2 × 4를")
              + p(f"font-size:28px;color:{SUB}", "수학 시간처럼 앞에서부터 차례로 계산해요. 파이썬도 똑같아요.") + '</div>', None, ' data-build-in="rise order 13"', "justify-content:center"))
o.append(caption("뒤쪽을 먼저 하고 싶으면 그 부분을 괄호로 묶어요.", 900))
W("order-same", o, "같은 계단에 있는 연산끼리 만나면 왼쪽부터 풀어요. 10 - 4 + 2는 10 - 4 = 6을 먼저 하고 6 + 2 = 8이에요. 뒤의 4 + 2를 먼저 하면 4가 나와서 틀려요. 8 / 2 * 4도 8 / 2 = 4.0을 먼저 하고 4를 곱해 16.0이에요. 나누기가 들어가서 결과가 실수예요. 몫 // 도 곱하기와 같은 계단이라 7 // 2 * 2는 7 // 2 = 3을 먼저 하고 2를 곱해 6이에요. 출력은 같은 셀을 실제로 실행한 결과예요.")

o = [sec("order-mix")] + head(EB2, "섞여 있으면 한 계단씩 풀어요", T2)
o += cell({"id": "c-om", "lines": ["print(10 - 2 * 3 ** 2 // 4)"], "n": 8, "out": ["6"]}, 96, 210, 900, sel="c-om")
mix = [("10 - 2 * 3 ** 2 // 4", "시작", GRAY), ("10 - 2 * 9 // 4", "2단계 ** · 3 ** 2 = 9", PUR), ("10 - 18 // 4", "3단계 왼쪽부터 · 2 * 9 = 18", T2),
       ("10 - 4", "3단계 · 18 // 4 = 4", T2), ("6", "4단계 · 10 - 4 = 6", OR)]
for i, (ex, note, c) in enumerate(mix):
    y = 370 + i * 100
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:96px;top:{y}px;width:1100px;height:86px;display:flex;flex-direction:row;align-items:center;gap:26px">'
             + mono(ex, 38, OR if i == len(mix) - 1 else INK, "#FDF3E7" if i == len(mix) - 1 else "#F1F0EC") + p(f"font-size:26px;font-weight:700;color:{c};white-space:nowrap", e(note)) + '</div>')
o.append(card(1260, 210, 564, 560, p(f"font-size:28px;font-weight:700;color:{INK}", "계단 순서")
              + "".join('<div style="display:flex;flex-direction:row;align-items:center;gap:16px">' + num(i + 1, c, 28) + mono(sym, 26, c, "#F6F5F1") + '</div>' for i, (sym, _, _, c) in enumerate(LEVELS))
              + '<div style="flex:1"></div>' + p(f"font-size:24px;line-height:1.5;color:{SUB}", "괄호가 없으니 1단계는 건너뛰어요."), T2, ' data-build-in="fade order 1"', "gap:20px"))
o.append(caption("직접 짤 땐 10 - (2 * 3 ** 2) // 4처럼 괄호로 순서를 보여 줘요.", 920))
W("order-mix", o, "네 계단이 모두 섞인 식을 한 단계씩 풀어 봐요. 괄호가 없으니 2단계 거듭제곱부터예요. 3 ** 2 = 9. 다음은 3단계인데, 곱하기와 몫이 같은 순위라서 왼쪽의 2 * 9 = 18을 먼저 하고 18 // 4 = 4를 해요. 마지막 4단계에서 10 - 4 = 6이에요. 출력 6은 셀에서 실제로 실행한 결과예요. 이런 식을 직접 쓸 때는 괄호로 묶어서 읽는 사람이 순서를 바로 알게 해요. 괄호를 쳐도 결과는 같은 6이에요.")

o = [sec("vars-calc")] + head(EB2, "숫자에 이름을 붙여 계산해요", T2)
o.append(p(f"position:absolute;left:96px;top:210px;width:840px;font-size:30px;font-weight:700;color:{T2}", "장보기 합계"))
o += cell({"id": "c-vc1", "lines": ["price = 3000", "count = 2", "total = price * count", 'print("합계:", total)'], "n": 9, "out": ["합계: 6000"]}, 96, 270, 840, attrs=' data-build-in="rise order 1"')
o.append(p(f"position:absolute;left:984px;top:210px;width:840px;font-size:30px;font-weight:700;color:{T2}", "세 사람이 나눠 내기", ' data-build-in="fade order 2"'))
o += cell({"id": "c-vc2", "lines": ["total = 10000", "people = 3", 'print("한 사람:", total // people)', 'print("남는 돈:", total % people)'], "n": 10, "out": ["한 사람: 3333", "남는 돈: 1"]}, 984, 270, 840, sel="c-vc2", attrs=' data-build-in="rise order 2"')
o.append(card(96, 680, 1728, 170, '<div style="display:flex;flex-direction:row;align-items:center;gap:30px">'
              + mono("3000 * 2", 34, GRAY) + p(f"font-size:28px;color:{SUB}", "무슨 숫자인지 몰라요") + '<div style="width:30px"></div>'
              + mono("price * count", 34, T2, "#E3F3F4") + p(f"font-size:28px;color:{SUB}", "가격 곱하기 개수") + '</div>', None, ' data-build-in="rise order 3"', "justify-content:center"))
o.append(caption("price만 바꾸고 다시 실행하면 합계도 새로 계산돼요.", 900))
W("vars-calc", o, "숫자를 그대로 적어도 계산은 되지만, 변수에 이름을 붙여 두면 무슨 계산인지 읽혀요. 왼쪽은 3000원짜리를 2개 산 합계예요. total = price * count도 = 오른쪽을 먼저 계산해서 6000을 total에 넣어요. 오른쪽은 만 원을 세 사람이 나눠 내는 계산이에요. 몫 // 로 한 사람이 낼 돈 3333원, 나머지 % 로 남는 1원을 구했어요. 오른쪽 셀이 total에 10000을 다시 넣어서 왼쪽의 6000은 사라졌어요.")

o = [sec("plus-eq")] + head(EB2, "+= 는 지금 값에 더해서 다시 넣어요", T2)
o += cell({"id": "c-pe", "lines": ["score = 0", "score += 10", "score += 5", "score"], "n": 11, "out": ["15"]}, 96, 220, 760, sel="c-pe")
for i, (v, lbl) in enumerate([("0", "score = 0"), ("10", "score += 10"), ("15", "score += 5")]):
    x = 940 + i * 300
    o.append(f'<div data-build-in="pop order {i + 1}" style="position:absolute;left:{x}px;top:220px;width:240px;display:flex;flex-direction:column;align-items:center;gap:14px">'
             + f'<div style="width:240px;height:180px;background:{CARD};border:3px solid {T2};border-radius:20px;display:flex;flex-direction:column;overflow:hidden">'
             + p(f"height:50px;flex:none;background:{T2};color:#FFFFFF;font-family:{MONO};font-size:26px;font-weight:700;line-height:50px;padding:0 18px", "score")
             + f'<div style="flex:1;display:flex;align-items:center;justify-content:center">' + p(f"font-family:{MONO};font-size:56px;font-weight:700;color:{INK}", v) + '</div></div>'
             + p(f"font-family:{MONO};font-size:22px;font-weight:700;color:{SUB};white-space:nowrap", e(lbl)) + '</div>')
    if i:
        o.append(f'<x-shape kind="arrow-right" data-build-in="fade order {i + 1}" style="position:absolute;left:{x - 54}px;top:290px;width:44px;height:30px;background:#C9CED8"></x-shape>')
o.append(card(96, 560, 1728, 280, '<div style="display:flex;flex-direction:row;align-items:center;gap:30px">' + mono("score += 10", 40, T2, "#E3F3F4")
              + p(f"font-size:30px;font-weight:700;color:{GRAY}", "는") + mono("score = score + 10", 40) + p(f"font-size:30px;font-weight:700;color:{GRAY}", "를 줄인 거예요") + '</div>'
              + '<div style="display:flex;flex-direction:row;align-items:center;gap:20px">' + p(f"font-size:26px;color:{SUB}", "같은 모양")
              + "".join(mono(t, 28) for t in ["-=", "*=", "/="]) + p(f"font-size:26px;color:{SUB}", "도 있어요") + '</div>', T2, ' data-build-in="rise order 4"', "justify-content:center"))
o.append(caption("점수나 합계처럼 값을 쌓아 갈 때 써요.", 900))
W("plus-eq", o, "+= 는 지금 값에 오른쪽 값을 더해서 같은 이름에 다시 넣어요. 앞에서 본 age = age + 1을 짧게 적는 방법이에요. score는 0에서 시작해서 10을 더해 10, 5를 더해 15가 돼요. 빼기는 -=, 곱하기는 *=, 나누기는 /= 처럼 기호 뒤에 =를 붙여요. + 와 = 사이는 띄우지 않고 붙여 적어요.")

o = [sec("str-ops")] + head(EB2, "글자에도 + 와 * 를 써요", T2)
so = [('"kim" + "lee"', "'kimlee'", "이어 붙여요", T2, False), ('"ha" * 3', "'hahaha'", "3번 반복해요", T2, False),
      ('"3" + "3"', "'33'", "따옴표가 있으면 숫자도 글자예요", OR, False), ('"3" + 3', 'TypeError: can only concatenate str (not "int") to str', "글자와 숫자는 더할 수 없어요", RED, True)]
for i, (code, out_, d, c, err) in enumerate(so):
    x, y = 96 + (i % 2) * 884, 220 + (i // 2) * 330
    o.append(card(x, y, 844, 306, p(f"font-size:28px;font-weight:700;color:{c}", e(d))
                  + mono(code, 34) + '<div style="display:flex;flex-direction:row;align-items:center;gap:14px">'
                  + f'<x-shape kind="arrow-right" style="width:40px;height:24px;flex:none;background:#C9CED8"></x-shape>'
                  + p(f"font-family:{MONO};font-size:{20 if err else 34}px;font-weight:700;color:{c};white-space:{'normal' if err else 'nowrap'};line-height:1.4", e(out_)) + '</div>',
                  c, f' data-build-in="rise order {i + 1}"'))
o.append(caption("글자와 숫자를 섞어 더하면 TypeError예요. int(\"3\") + 3처럼 타입을 맞춰요.", 900))
W("str-ops", o, "문자열에도 + 와 * 를 쓸 수 있어요. + 는 두 글자를 이어 붙이고, * 는 정수만큼 반복해요. 셀 마지막 줄의 값이라서 출력에 따옴표가 붙었어요. 셋째 칸이 헷갈리기 쉬워요. 따옴표로 감싼 \"3\"은 숫자가 아니라 글자라서 \"3\" + \"3\"은 6이 아니라 '33'이에요. 넷째 칸처럼 글자와 숫자를 더하면 TypeError가 나요. 메시지는 str(문자열)에는 int(정수)를 이어 붙일 수 없다는 뜻이에요. 계산하려면 2파트에서 본 int(\"3\")처럼 숫자로 바꿔요. 출력은 Traceback의 마지막 줄만 옮겼어요.")

# ---------- part 4: comparison and logic ----------
EB3 = "4. 비교와 논리연산"
T3 = PUR
o = [sec("compare")] + head(EB3, "비교하면 답은 True 아니면 False예요", T3)
cmp_ = [(">", "크다", "age > 20", "True"), ("<", "작다", "age < 20", "False"), ("==", "같다", "age == 25", "True"),
        ("!=", "다르다", "age != 25", "False"), (">=", "크거나 같다", "age >= 25", "True"), ("<=", "작거나 같다", "age <= 24", "False")]
o += cell({"id": "c-cmp", "lines": ["age = 25"] + [f"print({c[2]})" for c in cmp_], "n": 1, "out": [c[3] for c in cmp_]}, 96, 210, 720, sel="c-cmp")
for i, (s, m, ex, r) in enumerate(cmp_):
    y = 210 + i * 108
    o.append(f'<div data-build-in="rise order {i // 2 + 1}" style="position:absolute;left:880px;top:{y}px;width:944px;height:94px;background:{CARD};border:2px solid {LINE};border-radius:16px;padding:0 26px;display:flex;flex-direction:row;align-items:center;gap:22px">'
             + p(f"width:90px;flex:none;font-family:{MONO};font-size:38px;font-weight:700;color:{T3};text-align:center", e(s))
             + p(f"width:200px;flex:none;font-size:28px;font-weight:700;color:{INK}", m)
             + p(f"flex:1;font-family:{MONO};font-size:26px;color:{SUB}", e(ex)) + tf(r, 28) + '</div>')
o.append(caption("결과는 10에서 본 불리언(bool)이에요. 같다는 = 를 두 번 써요.", 900))
W("compare", o, "비교 연산자 여섯 가지예요. 비교한 결과는 맞으면 True, 틀리면 False로 나와요. 10에서 본 불리언 자료형이에요. 같다는 = 를 두 번 써서 == 로, 다르다는 느낌표와 = 를 붙여 != 로 적어요. 크거나 같다는 >= 처럼 = 를 뒤에 붙여요. => 처럼 순서를 바꾸면 SyntaxError가 나요. 기호 두 개 사이는 띄우지 않아요. age는 25로 넣었어요.", ("logic", "비교와 논리연산"))

o = [sec("eq")] + head(EB3, "= 하나는 넣기, == 두 개는 묻기", T3)
o.append(p(f"position:absolute;left:96px;top:210px;width:840px;font-size:34px;font-weight:700;color:{T3}", "== 묻기"))
o += cell({"id": "c-eq1", "lines": ["age == 30"], "n": 2, "out": ["False"]}, 96, 270, 840, attrs=' data-build-in="rise order 1"')
o.append(p(f"position:absolute;left:96px;top:430px;width:840px;font-size:28px;line-height:1.5;color:{SUB}", "age가 30이냐고 물어요.<br>age는 25 그대로예요.", ' data-build-in="fade order 1"'))
o.append(var_box("box-eq1", "age", "25", 96, 560, T3, 360, ' data-build-in="pop order 1"'))
o.append(p(f"position:absolute;left:984px;top:210px;width:840px;font-size:34px;font-weight:700;color:{BL}", "= 넣기", ' data-build-in="fade order 2"'))
o += cell({"id": "c-eq2", "lines": ["age = 30", "age"], "n": 3, "out": ["30"]}, 984, 270, 840, sel="c-eq2", attrs=' data-build-in="rise order 2"')
o.append(p(f"position:absolute;left:984px;top:470px;width:840px;font-size:28px;line-height:1.5;color:{SUB}", "age에 30을 넣어요. 값이 바뀌어요.", ' data-build-in="fade order 2"'))
o.append(var_box("box-eq2", "age", "30", 984, 560, BL, 360, ' data-build-in="pop order 2"'))
o.append(caption("비교하려고 = 를 하나만 쓰면 값이 바뀌어 버려요.", 900))
W("eq", o, "가장 많이 헷갈리는 곳이에요. = 하나는 1파트에서 본 넣기예요. == 두 개는 같으냐고 묻는 비교예요. 왼쪽 셀은 age가 30인지 물어서 False가 나왔고, age는 25 그대로예요. 오른쪽 셀은 age에 30을 넣어서 값이 바뀌었어요. 비교하려다 = 하나만 적으면 오류 없이 값이 바뀌어서 알아채기 어려워요. 다음 장부터 다시 age를 25로 넣고 시작해요.")

o = [sec("bool-var")] + head(EB3, "비교한 결과도 변수에 넣을 수 있어요", T3)
o += cell({"id": "c-bv", "lines": ["age = 25", "is_adult = age >= 20", "print(is_adult)", "print(type(is_adult))"], "n": 4, "out": ["True", "<class 'bool'>"]}, 96, 220, 860, sel="c-bv")
o.append(f'<div data-build-in="rise order 1" style="position:absolute;left:1020px;top:230px;width:804px;display:flex;flex-direction:column;align-items:flex-start;gap:20px">'
         + mono("age >= 20", 40) + p(f"font-size:26px;color:{SUB}", "25 >= 20 을 먼저 계산해요") + '</div>')
o.append(f'<div data-build-in="rise order 2" style="position:absolute;left:1020px;top:420px;width:804px;display:flex;flex-direction:row;align-items:center;gap:20px">'
         + f'<x-shape kind="arrow-right" style="width:50px;height:30px;flex:none;background:#C9CED8;transform:rotate(90deg)"></x-shape>' + tf("True", 40) + '</div>')
o.append(var_box("box-adult", "is_adult", "True", 1020, 520, T3, 440, ' data-build-in="pop order 3"'))
o.append(card(96, 520, 860, 250, p(f"font-size:28px;font-weight:700;color:{INK}", "이름은 is_ 로 시작해요")
              + p(f"font-size:26px;line-height:1.5;color:{SUB}", "10의 is_alive처럼 True, False를 담는<br>변수는 is_adult로 지으면 읽기 쉬워요."), T3, ' data-build-in="rise order 4"'))
o.append(caption("= 오른쪽을 먼저 계산한다는 규칙은 비교에서도 같아요.", 900))
W("bool-var", o, "비교한 결과 True, False도 값이라서 변수에 넣을 수 있어요. is_adult = age >= 20은 1파트의 규칙대로 = 오른쪽을 먼저 계산해요. 25 >= 20은 True라서 is_adult에 True가 들어가요. type()으로 보면 bool이에요. True와 False를 담는 변수는 is_로 시작하면 '~인가요?'라고 읽혀서 뜻이 잘 보여요. age를 다시 25로 넣은 건 앞 장에서 30으로 바꿨기 때문이에요.")


def truth(sid, op, rows, title, cap, notes, n_, section=None):
    o = [sec(sid)] + head(EB3, title, T3)
    o += cell({"id": f"c-{op}", "lines": [f"print({a} {op} {b})" for a, b, _ in rows], "n": n_, "out": [r for _, _, r in rows]}, 96, 220, 760, sel=f"c-{op}")
    o.append(f'<div style="position:absolute;left:940px;top:220px;width:884px;display:flex;flex-direction:row;gap:20px;padding:0 30px">'
             + p(f"width:180px;flex:none;font-size:24px;font-weight:700;color:{GRAY}", "왼쪽") + p(f"width:160px;flex:none;font-size:24px;font-weight:700;color:{GRAY}", "")
             + p(f"width:180px;flex:none;font-size:24px;font-weight:700;color:{GRAY}", "오른쪽") + p(f"flex:1;font-size:24px;font-weight:700;color:{T3}", "결과") + '</div>')
    for i, (a, b, r) in enumerate(rows):
        y = 270 + i * 120
        hi = (r == "True") if op == "and" else (r == "False")
        o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:940px;top:{y}px;width:884px;height:104px;background:{"#F1ECFB" if hi else CARD};border:2px solid {T3 if hi else LINE};border-radius:16px;padding:0 30px;display:flex;flex-direction:row;align-items:center;gap:20px">'
                 + f'<div style="width:180px;flex:none">{tf(a, 28)}</div>' + p(f"width:160px;flex:none;font-family:{MONO};font-size:32px;font-weight:700;color:{T3};text-align:center", op)
                 + f'<div style="width:180px;flex:none">{tf(b, 28)}</div>' + f'<x-shape kind="arrow-right" style="width:44px;height:26px;flex:none;background:#C9CED8"></x-shape>' + tf(r, 32) + '</div>')
    o.append(caption(cap, 900))
    W(sid, o, notes, section)


truth("and", "and", [("True", "True", "True"), ("True", "False", "False"), ("False", "True", "False"), ("False", "False", "False")],
      "and 는 둘 다 True일 때만 True예요", "하나라도 False면 결과는 False예요.",
      "and는 '그리고'예요. 왼쪽과 오른쪽이 모두 True일 때만 True가 돼요. 네 가지 경우 중에 True는 맨 위 한 줄뿐이에요. 출력은 네 줄을 한 셀에서 실제로 실행한 결과예요. True와 False는 첫 글자를 대문자로 적어요. 실제 코드에서는 True, False를 직접 적기보다 age >= 20 같은 비교 결과를 양쪽에 둬요. 뒤에서 그렇게 써 봐요.", 5)
truth("or", "or", [("True", "True", "True"), ("True", "False", "True"), ("False", "True", "True"), ("False", "False", "False")],
      "or 는 하나만 True여도 True예요", "둘 다 False일 때만 False예요.",
      "or는 '또는'이에요. 둘 중 하나라도 True면 True예요. 네 가지 경우 중에 False는 맨 아래, 둘 다 False인 한 줄뿐이에요. and와 반대로 생각하면 쉬워요. and는 하나만 False여도 False, or는 하나만 True여도 True예요.", 6)

o = [sec("not")] + head(EB3, "not 은 True와 False를 뒤집어요", T3)
o += cell({"id": "c-not", "lines": ["print(not True)", "print(not False)"], "n": 7, "out": ["False", "True"]}, 96, 220, 760, sel="c-not")
for i, (a, b) in enumerate([("True", "False"), ("False", "True")]):
    y = 220 + i * 260
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:940px;top:{y}px;width:884px;height:220px;background:{CARD};border:2px solid {LINE};border-radius:20px;padding:0 40px;display:flex;flex-direction:row;align-items:center;gap:30px">'
             + p(f"font-family:{MONO};font-size:40px;font-weight:700;color:{T3}", "not") + tf(a, 44)
             + f'<x-shape kind="arrow-right" style="width:80px;height:46px;flex:none;background:{T3}"></x-shape>' + tf(b, 44) + '</div>')
o.append(card(96, 520, 760, 260, p(f"font-size:28px;font-weight:700;color:{INK}", "앞에 한 번만 붙여요")
              + p(f"font-size:26px;line-height:1.5;color:{SUB}", "and, or는 값 두 개 사이에 두고,<br>not은 값 하나 앞에 붙여요."), T3, ' data-build-in="rise order 3"'))
o.append(caption("not 은 '아니다'예요. 바로 뒤의 값을 반대로 바꿔요.", 900))
W("not", o, "not은 뒤에 오는 값 하나를 반대로 바꿔요. not True는 False, not False는 True예요. and와 or는 두 값 사이에 두는데, not은 값 하나 앞에 붙인다는 점이 달라요. is_member가 False일 때 not is_member는 '회원이 아니다'라는 뜻이라서 True가 돼요. 이 예는 다음 장에서 실제로 실행해요.")

o = [sec("ride")] + head(EB3, "놀이기구 탑승 조건을 and로 적어요", T3)
o.append(p(f"position:absolute;left:96px;top:205px;width:1728px;font-size:28px;color:{SUB}", "조건 · 키 120cm 이상 <b style=\"color:" + T3 + "\">그리고</b> 7살 이상"))
for k, (h, cid, n_, res, rows, x) in enumerate([("130", "c-r1", 8, "True", [("130 >= 120", "True"), ("9 >= 7", "True"), ("True and True", "True")], 96),
                                                ("110", "c-r2", 9, "False", [("110 >= 120", "False"), ("9 >= 7", "True"), ("False and True", "False")], 984)]):
    lines = [f"height = {h}", "age = 9", "height >= 120 and age >= 7"] if k == 0 else [f"height = {h}", "height >= 120 and age >= 7"]
    o += cell({"id": cid, "lines": lines, "n": n_, "out": [res]}, x, 260, 840, attrs=f' data-build-in="rise order 4"' if k else "")
    o += chain([(ex, r, None) for ex, r in rows], x + 20, 520, 820, start=1 + k * 4)
    o.append(f'<div data-build-in="pop order {4 + k * 4 - (0 if k else 0)}" style="position:absolute;left:{x}px;top:760px;width:840px;display:flex;flex-direction:row;align-items:center;gap:16px">'
             + f'<x-icon name="{"CheckCircle" if res == "True" else "Warning"}" style="width:44px;height:44px;color:{GR if res == "True" else RED}"></x-icon>'
             + p(f"font-size:30px;font-weight:700;color:{GR if res == 'True' else RED}", "탈 수 있어요" if res == "True" else "키가 모자라서 못 타요") + '</div>')
o.append(caption("조건을 모두 만족해야 하면 and예요.", 900))
W("ride", o, "키가 120cm 이상이고 7살 이상이어야 탈 수 있는 놀이기구예요. 두 조건을 모두 만족해야 하니까 and로 이어요. 왼쪽은 키 130, 나이 9살이라서 비교 두 개가 모두 True, True and True는 True예요. 오른쪽은 키만 110으로 다시 넣었어요. age는 앞 셀의 9가 그대로 남아 있어요. 110 >= 120이 False라서 나이가 맞아도 결과는 False예요. 비교를 먼저 하고 and를 나중에 해서 괄호가 없어도 돼요.")

o = [sec("discount")] + head(EB3, "할인 조건을 or로 적어요", T3)
o.append(p(f"position:absolute;left:96px;top:205px;width:1728px;font-size:28px;color:{SUB}", "조건 · 회원이거나 <b style=\"color:" + T3 + "\">또는</b> 5만 원 이상 샀으면 할인"))
o += cell({"id": "c-d1", "lines": ["is_member = False", "total = 60000", "is_member or total >= 50000"], "n": 10, "out": ["True"]}, 96, 260, 840)
o += chain([("is_member", "False", None), ("60000 >= 50000", "True", None), ("False or True", "True", None)], 116, 520, 820)
o.append(f'<div data-build-in="pop order 4" style="position:absolute;left:96px;top:760px;width:840px;display:flex;flex-direction:row;align-items:center;gap:16px">'
         + f'<x-icon name="CheckCircle" style="width:44px;height:44px;color:{GR}"></x-icon>' + p(f"font-size:30px;font-weight:700;color:{GR}", "회원이 아니어도 할인돼요") + '</div>')
o += cell({"id": "c-d2", "lines": ["not is_member"], "n": 11, "out": ["True"]}, 984, 260, 840, sel="c-d2", attrs=' data-build-in="rise order 5"')
o += chain([("not is_member", None, None), ("not False", "True", None)], 1004, 440, 820, start=6)
o.append(card(984, 620, 840, 200, p(f"font-size:28px;font-weight:700;color:{INK}", "회원이 아닌가요?") + p(f"font-size:26px;color:{SUB}", "not을 붙이면 뜻도 반대로 읽어요."), T3, ' data-build-in="rise order 7"'))
o.append(caption("둘 중 하나만 만족해도 되면 or예요.", 900))
W("discount", o, "회원이거나 5만 원 이상 사면 할인해 주는 가게예요. 둘 중 하나만 맞아도 되니까 or로 이어요. is_member는 False지만 60000 >= 50000이 True라서 False or True는 True예요. 오른쪽 셀의 not is_member는 '회원이 아닌가요?'라는 질문이에요. is_member가 False라서 뒤집으면 True예요. total은 2파트에서 쓴 이름이지만 여기서 60000을 다시 넣었어요.")

o = [sec("logic-order")] + head(EB3, "계산, 비교, not, and, or 순서로 풀어요", T3)
o += cell({"id": "c-lo", "lines": ["2 + 3 > 4 and not False"], "n": 14, "out": ["True"]}, 96, 220, 1000, sel="c-lo")
steps_lo = [("2 + 3 > 4 and not False", None, "시작"), ("5 > 4 and not False", None, "1 계산"), ("True and not False", None, "2 비교"), ("True and True", None, "3 not"), ("True", None, "4 and")]
o += chain([(e(a_), r, l) for a_, r, l in steps_lo], 116, 400, 1000, gap=86)
o.append(card(1160, 220, 664, 470, p(f"font-size:30px;font-weight:700;color:{INK}", "먼저 하는 순서")
              + "".join('<div style="display:flex;flex-direction:row;align-items:center;gap:18px">' + num(i + 1, T3, 30) + mono(t, 30, T3, "#F1ECFB") + p(f"font-size:24px;color:{SUB}", d) + '</div>'
                        for i, (t, d) in enumerate([("+ - * /", "계산"), ("> == !=", "비교"), ("not", "뒤집기"), ("and", "그리고"), ("or", "또는")])),
              T3, ' data-build-in="rise order 6"', "gap:22px"))
o.append(caption("헷갈리면 (age >= 20) and (age < 30)처럼 괄호로 묶어요.", 900))
W("logic-order", o, "여러 연산이 섞이면 정해진 순서대로 풀어요. 계산이 가장 먼저라서 2 + 3이 5가 돼요. 그다음 비교로 5 > 4가 True가 돼요. 그다음 not False가 True가 되고, 마지막에 True and True가 True예요. and와 or가 섞이면 and를 먼저 해요. 순서를 외우지 않아도 괄호로 묶으면 그 안을 먼저 계산해요. 예를 들어 age = 25일 때 age >= 20 and age < 30은 20대인지 묻는 식이고 True가 나와요. 출력은 같은 셀을 실제로 실행한 결과예요.")

# ---------- summary ----------
EB5 = "정리"
o = [sec("trouble")] + head(EB5, "막히면 오류의 마지막 줄을 봐요", RED)
tr = [("NameError: name 'Age' is not defined", "대문자와 소문자를 다르게 적었거나 넣는 셀을 안 돌렸어요", "철자 확인, Run All"),
      ("NameError: name 'true' is not defined", "True, False는 첫 글자가 대문자예요", "True  False"),
      ('TypeError: can only concatenate str (not "int") to str', "따옴표 글자와 숫자를 더했어요", 'int("3") + 3'),
      ("ValueError: invalid literal for int() with base 10: '삼'", "int()가 숫자로 못 읽는 글자예요", "소수 글자는 float()"),
      ("ZeroDivisionError: division by zero", "0으로 나눴어요", "나누는 수 확인"),
      ("비교했는데 값이 바뀌었어요", "= 를 하나만 썼어요", "== 두 개"),
      ("6 / 2가 3.0으로 나와요", "/ 의 결과는 항상 실수예요", "몫만 필요하면 //")]
o.append('<div style="position:absolute;left:96px;top:196px;width:1728px;height:716px;display:flex;flex-direction:column;gap:10px">')
for i, (q, a_, cmd) in enumerate(tr, 1):
    m = "Error" in q
    o.append(f'<div data-build-in="rise order {i}" style="flex:1;display:flex;flex-direction:row;gap:26px;align-items:center;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:8px 30px">'
             + num(i, RED, 32)
             + '<div style="flex:1;display:flex;flex-direction:column;gap:4px">' + p(f"{'font-family:' + MONO + ';font-size:22px;' if m else 'font-size:26px;'}font-weight:700;color:{INK};white-space:nowrap", e(q)) + p(f"font-size:22px;color:{SUB}", e(a_)) + '</div>'
             + p(f"width:300px;flex:none;font-size:24px;font-weight:700;line-height:1.5;color:{INK};background:#EEEFF2;padding:8px 18px;border-radius:12px;white-space:pre", e(cmd)) + '</div>')
o.append('</div>')
o.append(caption("오류가 나면 위쪽 Traceback보다 맨 아래 줄부터 읽어요.", 940))
W("trouble", o, "오류 메시지는 길어도 맨 아래 한 줄에 원인이 있어요. 1번과 2번은 NameError예요. 이름 철자, 대소문자, True와 False의 첫 글자를 봐요. 3번은 따옴표로 감싼 글자와 숫자를 더했을 때예요. int()로 타입을 맞춰요. 4번은 int()가 숫자로 못 읽는 글자를 받았을 때예요. 5번은 0으로 나눴을 때예요. 10 / 0을 실제로 실행한 결과예요. 6번은 오류 없이 값만 바뀌어서 알아채기 어려워요. 7번도 오류는 아니지만 자주 묻는 질문이에요. 위 출력은 모두 hello-uv 커널에서 실제로 실행한 결과의 마지막 줄이에요.", ("trouble", "정리"))

o = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>']
cheat = [("age = 25", "오른쪽 값을 왼쪽 이름에 넣기", BL), ('print("나이:", age)', "설명 붙여 값 보기", BL), ("type(age)", "타입 확인", TT), ('int("3")  str(3)', "타입 바꾸기", TT),
         ("+ - * /", "사칙연산. / 는 항상 실수", T2), ("// % **", "몫, 나머지, 거듭제곱", T2), ("score += 10", "지금 값에 더해 다시 넣기", T2), ("== != > <", "비교하면 True 아니면 False", T3)]
for i, (k, d, c) in enumerate(cheat):
    x, y = 96 + (i % 4) * 438, 200 + (i // 4) * 290
    o.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:414px;height:264px;background:{CARD};border:2px solid {LINE};border-top:10px solid {c};border-radius:20px;padding:28px 28px;display:flex;flex-direction:column;gap:20px">'
             + mono(k, 28, c, "#F6F5F1", "align-self:flex-start") + p(f"font-size:28px;font-weight:700;color:{INK}", d) + '</div>')
o.append(f'<div style="position:absolute;left:96px;top:780px;width:1728px;height:210px;background:{CARD};border:2px solid {LINE};border-radius:20px;padding:24px 36px;display:flex;flex-direction:column;justify-content:center;gap:14px">'
         + p(f"font-size:30px;font-weight:700;color:{INK}", f'<span style="font-family:\'JetBrains Mono\';color:{T3}">and</span> 둘 다 True · <span style="font-family:\'JetBrains Mono\';color:{T3}">or</span> 하나라도 True · <span style="font-family:\'JetBrains Mono\';color:{T3}">not</span> 뒤집기')
         + p(f"font-size:30px;font-weight:700;color:{INK}", '푸는 순서는 계산, 비교, not, and, or. <span style="font-weight:400;color:' + SUB + '">헷갈리면 괄호로 묶어요</span>') + '</div>')
W("cheatsheet", o, "이번 챕터에서 쓴 기호와 함수를 한 장에 모았어요. = 는 넣기, == 는 묻기라는 것만은 꼭 기억해요. 노트북에 이 장의 내용을 마크다운 셀로 정리해 두면 복습할 때 같이 봐요. 다음에 배울 if 문은 여기서 만든 True, False로 할 일을 고르는 문법이에요.")

# ---------- toc ----------
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
parts = [("Archive", BL, "변수에 값 넣기", "= 로 넣기, 값 보기, 다시 넣기, NameError", "assign", "name-err"),
         ("Database", TT, "변수 타입", "int, float, str, bool, type(), 타입 바꾸기", "types", "convert-err"),
         ("Activity", T2, "사칙연산", "+ - * /, 몫과 나머지, 계산 순서 네 계단, +=, 글자 연산", "ops4", "str-ops"),
         ("Check", T3, "비교와 논리연산", "== 와 =, True와 False, and, or, not", "compare", "logic-order")]
t = [f'<section id="toc" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px 128px;display:flex;flex-direction:column;gap:40px">',
     f'<h2 style="font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>',
     '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:28px;flex:1">']
for i, (ic, c, h, s, a, b) in enumerate(parts, 1):
    t.append(f'<div style="display:flex;flex-direction:column;gap:14px;background:#FFFFFF;border:2px solid {LINE};border-top:10px solid {c};border-radius:20px;padding:32px 36px">'
             f'<div style="display:flex;flex-direction:row;gap:16px;align-items:center"><p style="font-size:60px;font-weight:900;line-height:1.25;color:{c}">{i}</p>'
             f'<x-icon name="{ic}" style="width:48px;height:48px;color:{c}"></x-icon></div>'
             f'<h3 style="font-size:32px;font-weight:700;color:{INK}">{h}</h3>'
             f'<p style="font-size:28px;line-height:1.5;color:{SUB}">{e(s)}</p><div style="flex:1"></div>'
             f'<p style="font-size:26px;color:#6A7180">{page[a]}–{page[b]}쪽</p></div>')
t += ['</div>', f'<p style="font-size:26px;color:{SUB}">{page["ready"]}쪽은 노트북 준비, {page["trouble"]}–{page["cheatsheet"]}쪽은 막힐 때와 한 장 요약이에요.</p>']
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(t) + f"\n<aside>{e('네 파트는 앞 파트를 그대로 이어서 써요. 1파트의 = 로 넣는 법과 2파트의 타입을 3파트 계산과 4파트 비교에서 계속 써요. 셀은 위에서부터 차례로 실행해요.')}</aside>\n</section>\n")

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-02T03:00:00Z"}, "lists": "css", "title": "파이썬 기초 (변수, 타입, 연산)", "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
print(len(ORDER), "slides")
