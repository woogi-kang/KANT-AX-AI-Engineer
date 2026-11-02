"""Generates every slide of the Python basics 2 deck (13) and slides/deck.json.

Story: keeps writing in basics.ipynb from chapter 12. Slices strings and formats output with %, format()
and f-string, then puts order data into lists and tuples and prints a receipt, first line by line, then with for.
Every cell and output comes from tools/demo.sh (tools/run_nb.py runs the cells with the project kernel).
Usage: python3 tools/gen.py slides
"""

import html, json, os, re, sys

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


def WIDE(t):
    """Draws each Hangul syllable two monospace columns wide, like a terminal."""
    return re.sub(r"([\uac00-\ud7a3])", r'<span style="display:inline-block;width:1.2em;text-align:center">\1</span>', t)


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
        wide = WIDE if c.get("wide") else (lambda t: t)
        o.append(''.join(p(f"margin-left:85px;padding:0 20px;font-family:{MONO};font-size:26px;line-height:1.45;white-space:pre;color:{col}", wide(e(l))) for l in c["out"]))
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
       '<h1 style="font-size:92px;font-weight:900;line-height:1.1;color:#F6F5F1">파이썬 기초 2<br>문자열, 리스트,<br>for</h1>',
       '<p style="font-size:40px;line-height:1.4;color:#BFC6D4">글자를 자르고, 여러 값을 담아<br>보기 좋게 출력하기</p>']
cov.append(f'<div style="position:absolute;left:1100px;top:300px;width:680px;height:480px;background:#252B36;border-radius:24px;padding:44px 48px;display:flex;flex-direction:column;justify-content:center;gap:34px">')
for code, out_, c in [('word[0:2]', "'py'", '#8FE0B0'), ('f"{pi:.2f}"', '3.14', '#8FE0B0'), ('orders[1][0]', "'latte'", '#E6A3C8'), ('len(words)', '3', '#E6A3C8')]:
    cov.append('<div style="display:flex;flex-direction:row;align-items:center;gap:28px">'
               + p(f"width:330px;flex:none;font-family:{MONO};font-size:38px;font-weight:700;color:{c};white-space:pre", e(code))
               + f'<x-shape kind="arrow-right" style="width:50px;height:30px;background:#5A6172"></x-shape>'
               + p(f"font-family:{MONO};font-size:36px;font-weight:700;color:#E6E9EF", e(out_)) + '</div>')
cov.append('</div>')
W("cover", cov, '12에서 변수, 타입, 계산, 비교를 봤어요. 이번 챕터는 그 위에서 글자와 여러 값을 다뤄요. 1파트는 문자열을 자르고 f-string으로 출력 모양을 맞춰요. 2파트는 주문 데이터를 리스트와 튜플에 담아 영수증을 찍고, for 문으로 되풀이를 줄여요. 모든 예제는 12에서 쓰던 노트북 셀에 이어서 적고 실행해요.', ("intro", "들어가기"))

ORDER.append("toc")   # written last, after page numbers are known

# ---------- ready ----------
o = [sec("ready")] + head("들어가기", "12에서 이어서 해요", JP)
done = [("hello-uv 노트북, 커널 .venv", "09 · 25–27쪽"), ("변수, 타입, print()", "12 · 1–2파트"), ("계산과 +=, 비교", "12 · 3–4파트")]
for i, (a_, b_) in enumerate(done):
    y = 220 + i * 150
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:96px;top:{y}px;width:820px;height:126px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:0 28px;display:flex;flex-direction:row;gap:22px;align-items:center">'
             + f'<x-icon name="CheckCircle" style="width:48px;height:48px;color:{GR}"></x-icon>'
             + p(f"flex:1;font-size:30px;font-weight:700;color:{INK}", e(a_))
             + p(f"font-size:24px;font-weight:700;color:{GRAY};white-space:nowrap", e(b_)) + '</div>')
o.append(p(f"position:absolute;left:96px;top:690px;width:820px;font-size:26px;line-height:1.5;color:{SUB}", "기억이 안 나면 그 쪽을 먼저 다시 봐요.", ' data-build-in="fade order 3"'))
o.append(f'<div data-build-in="rise order 4" style="position:absolute;left:1000px;top:220px;width:824px;height:560px;background:{CARD};border:2px solid {LINE};border-top:10px solid {JP};border-radius:20px;padding:32px 40px;display:flex;flex-direction:column;gap:30px">'
         + p(f"font-size:32px;font-weight:700;color:{INK}", "노트북 다시 열기")
         + '<div style="display:flex;flex-direction:row;gap:18px;align-items:center">' + num(1, JP, 36) + p(f"font-size:28px;color:{INK}", "VS Code로 hello-uv 폴더 열기") + '</div>'
         + '<div style="display:flex;flex-direction:row;gap:18px;align-items:center">' + num(2, JP, 36) + p(f"font-size:28px;color:{INK}", "탐색기에서") + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{JP}", NB) + p(f"font-size:28px;color:{INK}", "열기") + '</div>'
         + '<div style="display:flex;flex-direction:row;gap:18px;align-items:center">' + num(3, JP, 36) + p(f"font-size:28px;color:{INK}", "오른쪽 위 커널이 .venv인지 보기") + '</div>'
         + '<div style="display:flex;flex-direction:row;gap:18px;align-items:center">' + num(4, JP, 36) + p(f"font-size:28px;color:{INK}", "셀에 적고") + kbd("Shift+Enter", 26) + p(f"font-size:28px;color:{INK}", "로 실행") + '</div></div>')
o.append(caption("이번 챕터의 코드는 모두 노트북 셀에 적어요.", 880))
W("ready", o, "09에서 만든 hello-uv 폴더를 VS Code로 열고, 12에서 쓰던 basics.ipynb를 다시 열어요. 커널은 09에서 고른 .venv예요. 12에서 배운 변수, 타입, 계산, 비교를 그대로 써요. 슬라이드의 출력은 tools/demo.sh가 hello-uv 커널에서 같은 셀을 실제로 실행한 결과예요. 셀 번호는 파트마다 [1]부터 다시 셌어요. 한 노트북에서 이어서 실행하면 번호가 계속 커져요.")

# ---------- part 5: strings and output ----------
EB5S = "1. 문자열과 출력"
T5 = GR


def boxes(chars, left, top, size=110, hi=(), labels_top=None, labels_bot=None, attrs=""):
    """Characters in boxes with index numbers above (and negative numbers below)."""
    o = [f'<div{attrs} style="position:absolute;left:{left}px;top:{top}px;display:flex;flex-direction:row;gap:8px">']
    for i, ch in enumerate(chars):
        on = i in hi
        o.append('<div style="display:flex;flex-direction:column;align-items:center;gap:8px">'
                 + (p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{T5}", str(labels_top[i])) if labels_top else "")
                 + p(f"width:{size}px;height:{size}px;border-radius:14px;border:3px solid {T5 if on else LINE};background:{'#E6F4EC' if on else CARD};font-family:{MONO};font-size:{size * 0.5:.0f}px;font-weight:700;line-height:{size - 6}px;text-align:center;color:{INK};white-space:pre", e(ch) if ch != " " else "&#160;")
                 + (p(f"font-family:{MONO};font-size:22px;color:{GRAY}", str(labels_bot[i])) if labels_bot else "") + '</div>')
    o.append('</div>')
    return "".join(o)


o = [sec("str-make")] + head(EB5S, "문자열은 따옴표로 감싸요", T5)
o += cell({"id": "c-sm", "lines": ["a = 'kim'", 'b = "kim"', "print(a == b)", 'print(len("hello"))', 'print("It\'s me")'], "n": 1, "out": ["True", "5", "It's me"]}, 96, 210, 800, sel="c-sm")
sm = [("'kim'  \"kim\"", "작은따옴표, 큰따옴표 모두 같은 문자열", "a == b 는 True"),
      ('len("hello")', "글자 수를 세요", "h e l l o 다섯 글자라서 5"),
      ('"It\'s me"', "글자 안에 ' 가 있으면", "바깥을 \" 로 감싸요")]
for i, (code, d, sub) in enumerate(sm):
    o.append(card(960, 210 + i * 210, 864, 190, mono(code, 32, T5, "#E6F4EC", "align-self:flex-start") + p(f"font-size:28px;font-weight:700;color:{INK}", d) + p(f"font-size:22px;color:{SUB}", e(sub)), None, f' data-build-in="rise order {i + 1}"'))
o.append(caption("한 파일 안에서는 한 가지 따옴표로 맞춰 쓰면 읽기 쉬워요.", 900))
W("str-make", o, "문자열은 글자를 따옴표로 감싼 값이에요. 12의 2파트에서 본 str 타입이에요. 작은따옴표와 큰따옴표는 뜻이 같아서 a == b 가 True예요. len()은 글자 수를 세는 함수예요. hello는 다섯 글자라 5가 나와요. 공백도 한 글자로 세요. 글자 안에 작은따옴표가 들어가면 바깥을 큰따옴표로 감싸요. 반대도 마찬가지예요. 출력은 hello-uv 커널에서 실제로 실행한 결과예요. 이 파트도 새 커널이라 셀 번호가 [1]부터예요.", ("strings", "문자열과 출력"))

o = [sec("str-index")] + head(EB5S, "[번호]로 글자 하나를 꺼내요", T5)
o += cell({"id": "c-si", "lines": ['word = "python"', "print(word[0])", "print(word[1])", "print(word[-1])"], "n": 2, "out": ["p", "y", "n"]}, 96, 210, 700, sel="c-si")
o.append(boxes("python", 860, 210, 140, hi=(0, 1, 5), labels_top=list(range(6)), labels_bot=list(range(-6, 0)), attrs=' data-build-in="rise order 1"'))
o.append(p(f"position:absolute;left:860px;top:470px;width:964px;font-size:24px;color:{SUB}", "위 숫자는 앞에서부터, 아래 숫자는 뒤에서부터 센 번호예요.", ' data-build-in="fade order 1"'))
o += cell({"id": "c-si2", "lines": ["word[6]"], "n": 5, "out": ["IndexError: string index out of range"], "err": True}, 96, 560, 1728, attrs=' data-build-in="rise order 2"')
o.append(card(96, 720, 1728, 120, '<div style="display:flex;flex-direction:row;align-items:center;gap:24px">' + mono("0", 36, T5, "#E6F4EC") + p(f"font-size:28px;color:{INK}", "번호는 1이 아니라 0부터 세요. 여섯 글자의 마지막 번호는 5예요.") + '</div>', None, ' data-build-in="rise order 3"', "justify-content:center"))
o.append(caption("word[-1]은 맨 뒤 글자예요. 길이를 몰라도 끝을 꺼낼 수 있어요.", 900))
W("str-index", o, "문자열 뒤에 대괄호와 번호를 붙이면 그 자리의 글자 하나를 꺼내요. 이 번호를 인덱스라고 불러요. 첫 글자는 0번이에요. 그래서 python의 p는 0번, y는 1번, 마지막 n은 5번이에요. 음수 번호는 뒤에서부터 세요. -1이 맨 뒤 글자예요. 없는 번호 6을 쓰면 IndexError가 나요. 메시지는 번호가 범위를 벗어났다는 뜻이에요. 출력은 Traceback의 마지막 줄만 옮겼어요. 10에서 본 리스트도 같은 방식으로 꺼내요.")

o = [sec("str-slice")] + head(EB5S, "[시작:끝]으로 여러 글자를 잘라요", T5)
o += cell({"id": "c-ss1", "lines": ["word[0:2]"], "n": 3, "out": ["'py'"]}, 96, 210, 700)
o += cell({"id": "c-ss2", "lines": ["print(word[2:5])", "print(word[:2])", "print(word[2:])"], "n": 4, "out": ["tho", "py", "thon"]}, 96, 360, 700, sel="c-ss2")
sl = [("word[0:2]", (0, 1), "'py'", "0번부터 2번 앞까지"), ("word[2:5]", (2, 3, 4), "tho", "2번부터 5번 앞까지"), ("word[:2]", (0, 1), "py", "시작을 비우면 처음부터"), ("word[2:]", (2, 3, 4, 5), "thon", "끝을 비우면 끝까지")]
for i, (code, hi, out_, d) in enumerate(sl):
    y = 210 + i * 170
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:860px;top:{y}px;width:964px;height:150px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:0 24px;display:flex;flex-direction:row;align-items:center;gap:22px">'
             + '<div style="width:230px;flex:none;display:flex;flex-direction:column;gap:8px">' + mono(code, 26, T5, "#E6F4EC", "align-self:flex-start") + p(f"font-size:20px;color:{SUB}", d) + '</div>'
             + boxes("python", 0, 0, 62, hi=hi).replace("position:absolute;left:0px;top:0px;", "")
             + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{T5}", e(out_)) + '</div>')
o.append(caption("끝 번호의 글자는 들어가지 않아요. [0:2]는 0번, 1번 두 글자예요.", 920))
W("str-slice", o, "대괄호 안에 시작:끝을 적으면 그 사이의 글자를 잘라 와요. 슬라이싱이라고 불러요. 시작 번호의 글자는 들어가고, 끝 번호의 글자는 들어가지 않아요. 그래서 word[0:2]는 0번 p와 1번 y만 가져와 py예요. 끝 번호 빼기 시작 번호가 잘라 온 글자 수예요. 시작을 비우면 처음부터, 끝을 비우면 마지막까지예요. 출력은 같은 word로 실제로 실행한 결과예요.")

o = [sec("print-sep")] + head(EB5S, "print의 sep과 end로 모양을 바꿔요", T5)
o += cell({"id": "c-ps", "lines": ['print("kim", "lee")', 'print("kim", "lee", sep="-")', 'print("2026", "11", "02", sep=".")', 'print("hello", end=" ")', 'print("world")'], "n": 6,
           "out": ["kim lee", "kim-lee", "2026.11.02", "hello world"]}, 96, 210, 860, sel="c-ps")
ps = [("sep", "값 사이에 넣을 글자", 'sep="-"  →  kim-lee', "기본은 빈칸 한 개"), ("end", "줄 끝에 붙일 글자", 'end=" "  →  다음 print가 같은 줄에', "기본은 줄바꿈")]
for i, (k, d, ex, sub) in enumerate(ps):
    o.append(card(1020, 210 + i * 320, 804, 290, '<div style="display:flex;flex-direction:row;align-items:center;gap:18px">' + mono(k, 40, T5, "#E6F4EC") + p(f"font-size:30px;font-weight:700;color:{INK}", d) + '</div>'
                  + mono(ex, 26, INK, "#F6F5F1", "align-self:flex-start") + p(f"font-size:24px;color:{SUB}", sub), T5, f' data-build-in="rise order {i + 1}"'))
o.append(caption("print(\"설명\", 값)이 빈칸으로 이어진 건 sep의 기본값이 빈칸이라서예요.", 900))
W("print-sep", o, "print에 쉼표로 여러 값을 넣으면 사이에 빈칸이 하나씩 들어가요. 12의 1파트의 print(\"나이:\", age)도 그래서 나이: 25로 나왔어요. sep=\"-\"처럼 적으면 빈칸 대신 다른 글자를 넣어요. 날짜를 점으로 잇는 예처럼 써요. print는 끝에 줄바꿈을 붙여서 다음 print가 아랫줄에 나와요. end=\" \"를 주면 줄바꿈 대신 빈칸을 붙여서 다음 print가 같은 줄에 이어져요. sep, end 뒤의 = 는 넣기가 아니라 print에 옵션을 주는 표시예요.")

o = [sec("escape")] + head(EB5S, "\\ 로 시작하는 특수 문자", T5)
o += cell({"id": "c-es", "lines": ['print("첫째 줄\\n둘째 줄")', 'print("이름\\tkim")', 'print("경로: C:\\\\Users")'], "n": 7, "out": ["첫째 줄", "둘째 줄", "이름\tkim", "경로: C:\\Users"]}, 96, 210, 860, sel="c-es")
es = [("\\n", "줄바꿈", "글자 사이에서 다음 줄로"), ("\\t", "탭", "칸을 띄워 줄 맞추기"), ("\\\\", "역슬래시 하나", "\\ 자체를 쓰고 싶을 때")]
for i, (k, n_, d) in enumerate(es):
    o.append(card(1020, 210 + i * 210, 804, 190, '<div style="display:flex;flex-direction:row;align-items:center;gap:22px">' + mono(k, 44, T5, "#E6F4EC")
                  + '<div style="display:flex;flex-direction:column;gap:4px">' + p(f"font-size:30px;font-weight:700;color:{INK}", n_) + p(f"font-size:24px;color:{SUB}", d) + '</div></div>', None, f' data-build-in="rise order {i + 1}"', "justify-content:center"))
o.append(caption("Windows 키보드에서는 \\ 가 ₩ 로 보여요. 같은 키예요.", 900))
W("escape", o, "따옴표 안에서 역슬래시 \\ 뒤의 글자는 특별한 뜻이 돼요. \\n은 줄바꿈이라 print 한 번으로 두 줄이 나와요. \\t는 탭이라 칸을 띄워요. 역슬래시 자체를 쓰려면 \\\\처럼 두 번 적어요. Windows 경로를 적을 때 자주 만나요. 한글 Windows 키보드와 글꼴에서는 역슬래시가 원화 표시로 보이는데, 같은 키예요. 출력은 실제로 실행한 결과예요.")

OLD_C, NEW_C = OR, T5


def dual(sid, lc, rc, top=200, w=850, attrs_r=' data-build-in="rise order 1"'):
    """% cell on the left, f-string cell on the right."""
    o = [p(f"position:absolute;left:96px;top:{top}px;width:{w}px;font-size:26px;font-weight:700;color:{OLD_C}", "% 방식 · 옛 방식"),
         p(f"position:absolute;left:{1824 - w}px;top:{top}px;width:{w}px;font-size:26px;font-weight:700;color:{NEW_C}", "f-string · 요즘 방식", attrs_r)]
    o += cell(lc, 96, top + 46, w)
    o += cell(rc, 1824 - w, top + 46, w, sel=rc["id"], attrs=attrs_r)
    return o


def map_rows(rows, top, start=2, h=96):
    """Rows of (% code, f-string code, meaning) placed under the two cells."""
    o = []
    for i, (a, b, d) in enumerate(rows):
        y = top + i * (h + 12)
        o.append(f'<div data-build-in="rise order {start + i}" style="position:absolute;left:96px;top:{y}px;width:1728px;height:{h}px;background:{CARD};border:2px solid {LINE};border-radius:16px;padding:0 26px;display:flex;flex-direction:row;align-items:center;gap:22px">'
                 + f'<div style="width:420px;flex:none">' + mono(a, 28, OLD_C, "#FDF3E7", "display:inline-block") + '</div>'
                 + f'<x-shape kind="arrow-right" style="width:40px;height:24px;flex:none;background:#C9CED8"></x-shape>'
                 + f'<div style="width:480px;flex:none">' + mono(b, 28, NEW_C, "#E6F4EC", "display:inline-block") + '</div>'
                 + p(f"flex:1;font-size:24px;color:{SUB}", e(d)) + '</div>')
    return o


o = [sec("fmt-ways")] + head(EB5S, "값을 끼워 넣는 방법은 세 가지예요", T5)
o += cell({"id": "c-fw", "lines": ['name = "kim"', "age = 25", 'print("%s 님은 %d살이에요" % (name, age))', 'print("{} 님은 {}살이에요".format(name, age))', 'print(f"{name} 님은 {age}살이에요")'], "n": 8,
           "out": ["kim 님은 25살이에요"] * 3}, 96, 200, 1728, sel="c-fw")
ways = [("% 포맷팅", '"%s" % name', "C 언어에서 온 가장 옛 방식", "옛 코드와 책에서 자주 봐요", OLD_C),
        ("format()", '"{}".format(name)', "파이썬 3.0부터 (2008년)", "중간 세대예요", NAVY),
        ("f-string", 'f"{name}"', "파이썬 3.6부터 (2016년)", "요즘 표준. 새 코드는 이걸로 써요", NEW_C)]
for i, (t, code, when, d, c) in enumerate(ways):
    x = 96 + i * 584
    o.append(card(x, 566, 560, 296, p(f"font-size:32px;font-weight:700;color:{c}", t) + mono(code, 28, INK, "#F6F5F1", "align-self:flex-start")
                  + '<div style="flex:1"></div>' + p(f"font-size:24px;font-weight:700;color:{INK}", when) + p(f"font-size:22px;color:{SUB}", d), c, f' data-build-in="rise order {i + 1}"'))
o.append(caption("세 줄 모두 결과가 같아요. 이 챕터는 % 와 f-string을 나란히 봐요.", 920))
W("fmt-ways", o, "문자열 안에 변수 값을 끼워 넣는 방법은 세 가지예요. 셀의 세 줄은 실제로 실행하면 똑같은 문장을 출력해요. % 포맷팅은 C 언어에서 가져온 가장 오래된 방식이라 옛 코드, 오래된 책, 블로그에서 많이 보여요. format()은 파이썬 3.0에서 나온 중간 세대예요. f-string은 파이썬 3.6에서 나왔고 지금 표준이에요. 따옴표 앞에 f를 붙이고 중괄호 안에 변수 이름을 바로 적어서 가장 읽기 쉬워요. 새로 짜는 코드는 f-string으로 쓰고, % 는 남의 코드를 읽을 수 있을 만큼 알아 둬요. 다음 장부터 모든 예시를 % 와 f-string으로 나란히 실행해요.")

o = [sec("fmt-sd")] + head(EB5S, "%s, %d 자리와 f-string의 { }", T5)
o += dual("fmt-sd", {"id": "c-p1", "lines": ['print("이름: %s" % name)', 'print("나이: %d살" % age)'], "n": 9, "out": ["이름: kim", "나이: 25살"]},
          {"id": "c-f1", "lines": ['print(f"이름: {name}")', 'print(f"나이: {age}살")', 'print(f"내년: {age + 1}살")'], "n": 10, "out": ["이름: kim", "나이: 25살", "내년: 26살"]})
o += map_rows([('"%s" % name', 'f"{name}"', "문자열 자리"), ('"%d" % age', 'f"{age}"', "정수 자리. f-string은 타입을 안 적어도 돼요"),
               ('"%s %d" % (name, age)', 'f"{name} {age}"', "여러 개면 % 는 괄호로 묶어 순서대로")], 560)
o.append(caption("f-string은 따옴표 앞에 f, 중괄호 안에 이름이나 계산식을 바로 적어요.", 920))
W("fmt-sd", o, "왼쪽은 % 방식이에요. 문자열 안에 %s(문자열), %d(정수), %f(실수) 같은 빈자리를 만들고, 문자열 뒤 % 다음에 값을 적어요. 자리가 둘 이상이면 값을 괄호로 묶어 순서대로 적어요. 이 묶음은 튜플이라고 부르는데 뒤에서 배워요. 여기서 % 는 12의 3파트의 나머지가 아니라 끼워 넣기예요. 오른쪽은 f-string이에요. 따옴표 앞에 f를 붙이고, 값이 들어갈 자리에 중괄호와 변수 이름을 바로 적어요. 타입을 따로 적지 않아도 되고, {age + 1}처럼 계산식도 넣을 수 있어요. 출력은 두 셀을 실제로 실행한 결과예요.")

o = [sec("fmt-format")] + head(EB5S, "format()은 {0} {1} {2} 번호로 값을 넣어요", T5)
o += cell({"id": "c-fo", "lines": ['cake = "치즈케이크"', "price = 5000", "qty = 2", 'print("주문내역은 : {0}, {1}, {2}".format(cake, price, qty))', 'print("주문내역은 : {}, {}, {}".format(cake, price, qty))',
                                    'print("{0} {2}개, 하나에 {1}원".format(cake, price, qty))', 'print("{0}, {0}, {0}".format(cake))'], "n": 11,
           "out": ["주문내역은 : 치즈케이크, 5000, 2", "주문내역은 : 치즈케이크, 5000, 2", "치즈케이크 2개, 하나에 5000원", "치즈케이크, 치즈케이크, 치즈케이크"]}, 96, 200, 1728, sel="c-fo")
fo = [("{0}", "cake", "치즈케이크"), ("{1}", "price", "5000"), ("{2}", "qty", "2")]
for i, (k, v, r) in enumerate(fo):
    x = 96 + i * 584
    o.append(card(x, 716, 560, 150, '<div style="display:flex;flex-direction:row;align-items:center;gap:16px">' + mono(k, 34, NAVY, "#E8EEF8")
                  + '<x-shape kind="arrow-left" style="width:40px;height:24px;flex:none;background:#C9CED8"></x-shape>' + mono(v, 30, INK, "#F6F5F1") + '</div>'
                  + p(f"font-size:22px;color:{SUB}", e(f"{i}번째 값 → {r}")), NAVY, f' data-build-in="rise order {i + 1}"', "justify-content:center"))
o.append(caption("번호는 0부터 세요. 번호를 비우면 순서대로, 번호를 쓰면 순서를 바꾸거나 여러 번 쓸 수 있어요.", 920))
W("fmt-format", o, "가운데 세대인 format() 방식이에요. 문자열 안에 중괄호와 번호로 빈자리를 만들고, 뒤에 .format(괄호)를 붙여 값을 순서대로 적어요. 번호는 0부터 세요. cake가 0번, price가 1번, qty가 2번이라서 {0}, {1}, {2}에 차례로 들어가요. 둘째 줄처럼 번호를 비우면 적은 순서대로 들어가요. 셋째 줄은 번호로 순서를 바꿨어요. 넷째 줄은 {0}을 세 번 써서 같은 값을 여러 번 넣었어요. % 방식은 자리 순서와 값 순서가 꼭 같아야 해서 이렇게 못 해요. 모두 실제로 실행한 결과예요.")

o = [sec("fmt-order")] + head(EB5S, "같은 주문내역을 세 방식으로 적어 봐요", T5)
o += cell({"id": "c-fod", "lines": ['print("주문내역은 : %s, %d, %d" % (cake, price, qty))', 'print("주문내역은 : {0}, {1}, {2}".format(cake, price, qty))', 'print(f"주문내역은 : {cake}, {price}, {qty}")',
                                     'print(f"{cake} {qty}개, 하나에 {price}원")', 'print(f"{cake} {qty}개, 합계 {price * qty:,}원")'], "n": 12,
           "out": ["주문내역은 : 치즈케이크, 5000, 2", "주문내역은 : 치즈케이크, 5000, 2", "주문내역은 : 치즈케이크, 5000, 2", "치즈케이크 2개, 하나에 5000원", "치즈케이크 2개, 합계 10,000원"]}, 96, 200, 1728, sel="c-fod")
ow = [("% 방식", "%s, %d, %d", "자리 순서 = 값 순서", OLD_C), ("format()", "{0}, {1}, {2}", "번호로 값을 골라요", NAVY), ("f-string", "{cake}, {price}, {qty}", "이름을 바로 적어요", NEW_C)]
for i, (t, code, d, c) in enumerate(ow):
    x = 96 + i * 584
    o.append(card(x, 716, 560, 170, p(f"font-size:28px;font-weight:700;color:{c}", t) + mono(code, 26, INK, "#F6F5F1", "align-self:flex-start") + p(f"font-size:22px;color:{SUB}", d),
                  c, f' data-build-in="rise order {i + 1}"', "justify-content:center"))
o.append(caption("f-string은 { } 안에 계산식과 모양도 넣어요. {price * qty:,} 는 합계에 콤마를 찍어요.", 930))
W("fmt-order", o, "앞 장의 주문내역을 세 방식으로 나란히 적었어요. 첫 줄은 % 방식이에요. %s, %d, %d 자리에 괄호 안 값이 순서대로 들어가요. 둘째 줄은 format() 방식이라 번호로 값을 골라요. 셋째 줄은 f-string이에요. 중괄호 안에 cake, price, qty 이름을 바로 적어서 어떤 값이 어디 들어가는지 한눈에 보여요. 넷째 줄은 순서를 바꿔도 이름만 옮기면 돼요. 다섯째 줄처럼 중괄호 안에서 price * qty를 계산하고 콜론 뒤에 쉼표를 붙여 합계 10,000원을 바로 찍을 수도 있어요. 세 줄 모두 결과가 같고, 실제로 실행한 결과예요.")

o = [sec("fmt-width")] + head(EB5S, "%5d 와 {42:5d} 는 다섯 칸을 확보해요", T5)
o += dual("fmt-width", {"id": "c-p2", "lines": ['print("[%5d]" % 42)', 'print("[%-5d]" % 42)', 'print("[%05d]" % 42)', 'print("[%5s]" % "kim")'], "n": 13, "out": ["[   42]", "[42   ]", "[00042]", "[  kim]"]},
          {"id": "c-f2", "lines": ['print(f"[{42:5d}]")', 'print(f"[{42:<5d}]")', 'print(f"[{42:05d}]")', "print(f\"[{'kim':>5}]\")", "print(f\"[{'kim':5}]\")"], "n": 14,
           "out": ["[   42]", "[42   ]", "[00042]", "[  kim]", "[kim  ]"]})
wr = [("%5d", "{42:5d}", "   42", "다섯 칸, 오른쪽 맞춤"), ("%-5d", "{42:<5d}", "42   ", "왼쪽 맞춤. % 는 -, f-string은 <"), ("%05d", "{42:05d}", "00042", "빈칸을 0으로"), ("%5s", "{'kim':>5}", "  kim", "글자 오른쪽 맞춤. f-string은 > 를 붙여요")]
for i, (a, b, cells_, d) in enumerate(wr):
    y = 694 + i * 62
    o.append(f'<div data-build-in="rise order {i + 2}" style="position:absolute;left:96px;top:{y}px;width:1728px;height:56px;display:flex;flex-direction:row;align-items:center;gap:20px">'
             + f'<div style="width:170px;flex:none">' + mono(a, 26, OLD_C, "#FDF3E7", "display:inline-block") + '</div>'
             + f'<div style="width:230px;flex:none">' + mono(b, 26, NEW_C, "#E6F4EC", "display:inline-block") + '</div>'
             + boxes(cells_, 0, 0, 48, hi=tuple(j for j, ch in enumerate(cells_) if ch != " ")).replace("position:absolute;left:0px;top:0px;", "")
             + p(f"font-size:24px;color:{SUB}", e(d)) + '</div>')
o.append(caption("f-string에서 글자는 기본이 왼쪽 맞춤이에요. {'kim':5}는 [kim  ]이 돼요.", 962))
W("fmt-width", o, "% 와 d 사이, 또는 f-string의 콜론 뒤에 숫자를 넣으면 그만큼 칸을 확보해요. 대괄호는 칸이 보이게 일부러 붙였어요. 42는 두 글자라서 다섯 칸을 채우려고 빈칸 세 개가 붙어요. 왼쪽 맞춤은 % 에서는 - 를, f-string에서는 < 를 붙여요. 0을 붙이면 빈칸을 0으로 채워 00042처럼 번호표 모양이 돼요. 한 가지 다른 점이 있어요. % 방식은 글자도 오른쪽 맞춤인데, f-string은 글자가 기본으로 왼쪽 맞춤이라서 {'kim':5}는 [kim  ]이 돼요. 오른쪽으로 보내려면 > 를 붙여요. f-string 안에서 글자를 쓸 땐 바깥 큰따옴표와 겹치지 않게 작은따옴표로 감쌌어요. 모두 실제로 실행한 결과예요.")

o = [sec("fmt-float")] + head(EB5S, "%0.2f 와 {pi:.2f} 는 소수점 두 자리예요", T5)
o += dual("fmt-float", {"id": "c-p3", "lines": ["pi = 3.141592", 'print("%f" % pi)', 'print("%.2f" % pi)', 'print("%0.2f" % pi)', 'print("%.4f" % pi)', 'print("[%8.2f]" % pi)'], "n": 15,
                         "out": ["3.141592", "3.14", "3.14", "3.1416", "[    3.14]"]},
          {"id": "c-f3", "lines": ['print(f"{pi}")', 'print(f"{pi:.2f}")', 'print(f"{pi:0.2f}")', 'print(f"{pi:.4f}")', 'print(f"[{pi:8.2f}]")'], "n": 16,
           "out": ["3.141592", "3.14", "3.14", "3.1416", "[    3.14]"]}, w=830)
parts_ = [("0", "전체 칸 수", BL), (".2", "소수점 아래 자리", T5), ("f", "실수", NAVY)]
o.append(f'<div data-build-in="rise order 2" style="position:absolute;left:96px;top:740px;width:1728px;height:130px;background:{CARD};border:2px solid {LINE};border-radius:20px;padding:0 36px;display:flex;flex-direction:row;align-items:center;gap:30px">'
         + mono("%0.2f", 36, OLD_C, "#FDF3E7") + mono("{pi:0.2f}", 36, NEW_C, "#E6F4EC") + '<div style="flex:1"></div>'
         + "".join('<div style="display:flex;flex-direction:row;align-items:center;gap:10px">' + p(f"font-family:{MONO};font-size:36px;font-weight:700;color:{c}", e(t)) + p(f"font-size:22px;font-weight:700;color:{c};white-space:nowrap", d) + '</div>' for t, d, c in parts_) + '</div>')
o.append(caption("0은 최소 칸 수라 영향이 없어서 0.2f 와 .2f 는 결과가 같아요.", 920))
W("fmt-float", o, "실수는 소수점 아래 자리 수를 정해서 보여 줄 수 있어요. % 방식은 %.2f, f-string은 {pi:.2f}처럼 적어요. 둘 다 점 뒤 숫자가 소수점 아래 자리 수예요. %f 하나만 쓰면 여섯 자리까지 나와요. .4f는 다섯째 자리에서 반올림해 3.1416이 돼요. %0.2f에서 점 앞의 0은 앞 장의 전체 칸 수예요. 최소 0칸이라 영향이 없어서 .2f와 결과가 같아요. 8.2f는 여덟 칸을 확보하고 소수점 아래 두 자리를 보여 줘요. 점도 한 칸으로 세요. 원래 pi 값은 바뀌지 않고 보여 주는 모양만 바뀌어요. 2.675를 .2f로 보이면 2.67이 나오는 것처럼 반올림이 가끔 어긋나는 건 컴퓨터가 소수를 저장하는 방식 때문이에요.")

o = [sec("fmt-comma")] + head(EB5S, "가격은 {price:,} 로 천 단위 콤마를 찍어요", T5)
o += cell({"id": "c-fc", "lines": ["price = 1234567", 'print(f"{price:,}")', 'print(f"{price:,}원")', 'print(f"{1234567.891:,.2f}")', "fee = 35000", 'print(f"[{fee:8,}]")'], "n": 17,
           "out": ["1,234,567", "1,234,567원", "1,234,567.89", "[  35,000]"]}, 96, 200, 860, sel="c-fc")
cm = [("{price:,}", "1,234,567", "콤마만"), ("{x:,.2f}", "1,234,567.89", "콤마와 소수점 두 자리"), ("{fee:8,}", "  35,000", "여덟 칸 확보 + 콤마")]
for i, (k, r, d) in enumerate(cm):
    o.append(card(1020, 200 + i * 175, 804, 160, '<div style="display:flex;flex-direction:row;align-items:center;gap:18px">' + mono(k, 30, NEW_C, "#E6F4EC")
                  + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{INK};white-space:pre", "→ " + r) + '</div>' + p(f"font-size:22px;color:{SUB}", d), None, f' data-build-in="rise order {i + 1}"', "justify-content:center"))
o += cell({"id": "c-pc2", "lines": ['print("%,d" % price)'], "n": 18, "out": ["ValueError: unsupported format character ',' (0x2c) at index 1"], "err": True}, 96, 720, 1728, attrs=' data-build-in="rise order 4"')
o.append(p(f"position:absolute;left:96px;top:850px;width:1728px;font-size:26px;color:{SUB}", "% 방식에는 콤마 옵션이 없어요. 콤마가 필요하면 f-string을 써요.", ' data-build-in="fade order 4"'))
o.append(caption("콤마는 보여 주는 모양만 바꿔요. price 값은 그대로 1234567이에요.", 940))
W("fmt-comma", o, "가격이나 인원처럼 큰 수는 천 단위마다 콤마를 찍어야 읽기 쉬워요. f-string에서 콜론 뒤에 쉼표를 적으면 1,234,567처럼 찍혀요. 뒤에 원을 붙여 가격처럼 보일 수도 있어요. 소수점 자리와 같이 쓰려면 ,.2f처럼 쉼표를 먼저 적어요. 칸 수와 함께 쓰면 8,처럼 칸 수 뒤에 쉼표를 붙여요. 35,000은 여섯 글자라서 앞에 빈칸 두 개가 붙었어요. 콤마까지 넣은 길이가 칸 수보다 길면 칸을 무시하고 다 보여 줘요. % 방식에는 콤마 옵션이 없어서 %,d 는 ValueError가 나요. 모두 실제로 실행한 결과예요. format()으로는 \"{:,}\".format(price)처럼 같은 결과를 얻어요.")

o = [sec("fmt-format2")] + head(EB5S, "format()도 콜론 뒤 모양은 f-string과 같아요", T5)
o += cell({"id": "c-fo2", "lines": ["price = 5000", 'print("[{0:5d}]".format(qty))', 'print("{0:.2f}".format(3.141592))', 'print("{0:,}원".format(1234567))', 'print("{0}: {1:,}원 x {2}개".format(cake, price, qty))'], "n": 19,
           "out": ["[    2]", "3.14", "1,234,567원", "치즈케이크: 5,000원 x 2개"]}, 96, 200, 1728, sel="c-fo2")
OLD_C, NEW_C = NAVY, T5
o += [r.replace("#FDF3E7", "#E8EEF8") for r in map_rows([("{0:5d}", "{qty:5d}", "다섯 칸 확보"), ("{0:.2f}", "{pi:.2f}", "소수점 두 자리"), ("{1:,}", "{price:,}", "천 단위 콤마")], 656, h=80)]
OLD_C, NEW_C = OR, T5
o.append(caption("f-string은 이름을, format()은 번호를 콜론 앞에 적어요. 콜론 뒤는 똑같아요.", 960))
W("fmt-format2", o, "format() 방식도 콜론 뒤에 모양을 적어요. 5d는 다섯 칸, .2f는 소수점 두 자리, 쉼표는 천 단위 콤마예요. 앞에서 f-string으로 본 모양과 똑같아요. 첫 줄은 앞 장에서 price를 1234567로 바꿨기 때문에 케이크 값 5000으로 다시 넣은 거예요. 다른 점은 콜론 앞에 변수 이름 대신 번호를 적는다는 것뿐이에요. 아래 줄의 파란 칸이 format(), 초록 칸이 같은 뜻의 f-string이에요. 새 코드는 f-string으로 쓰고, format()은 남의 코드에서 만나면 읽을 수 있을 만큼 알아 둬요. 출력은 실제로 실행한 결과예요.")

o = [sec("fmt-align")] + head(EB5S, "칸을 맞추면 표처럼 보여요", T5)
o += dual("fmt-align", {"id": "c-p4", "lines": ['print("%-6s %5d" % ("kim", 90))', 'print("%-6s %5d" % ("lee", 100))', 'print("%-6s %5d" % ("park", 7))', 'print("할인 %d%%" % 30)'], "n": 20,
                         "out": ["kim       90", "lee      100", "park       7", "할인 30%"]},
          {"id": "c-f4", "lines": ["print(f\"{'kim':<6} {90:5d}\")", "print(f\"{'lee':<6} {100:5d}\")", "print(f\"{'park':<6} {7:5d}\")", 'print(f"할인 {30}%")'], "n": 21,
           "out": ["kim       90", "lee      100", "park       7", "할인 30%"]})
o += map_rows([("%-6s", "{:<6}", "여섯 칸 왼쪽 맞춤 (이름)"), ("%5d", "{:5d}", "다섯 칸 오른쪽 맞춤 (점수)"), ("%%", "%", "% 글자 그대로. % 방식만 두 번 적어요")], 624, h=80)
o.append(caption("성적표, 영수증처럼 줄을 맞춰 보여 줄 때 칸 수를 써요.", 940))
W("fmt-align", o, "칸 수 확보를 표에 써 봐요. 이름은 여섯 칸 왼쪽 맞춤, 점수는 다섯 칸 오른쪽 맞춤이에요. 이름 길이와 점수 자리 수가 달라도 점수 끝자리가 한 줄로 서요. 사람 이름은 팀 실습의 kim, lee, park을 썼어요. % 방식에서 % 글자 자체를 보이려면 %%처럼 두 번 적어요. 한 번만 적으면 끼워 넣을 자리로 읽어요. f-string은 % 를 그냥 적으면 돼요. 대신 f-string에서 중괄호 자체를 보이려면 {{ }}처럼 두 번 적어요. 출력은 두 셀을 실제로 실행한 결과예요.")

o = [sec("fmt-err")] + head(EB5S, "자리와 값이 안 맞으면 오류가 나요", T5)
pe = [('"%d살" % "kim"', "TypeError: %d format: a real number is required, not str", "%d 자리에 글자를 넣었어요", 22, OLD_C),
      ('"%s 님은 %d살" % name', "TypeError: not enough arguments for format string", "자리는 둘, 값은 하나예요", 23, OLD_C),
      ('"%s" % (name, age)', "TypeError: not all arguments converted during string formatting", "자리는 하나, 값은 둘이에요", 24, OLD_C),
      ('f"{name:d}"', "ValueError: Unknown format code 'd' for object of type 'str'", "글자에 정수 모양 d를 줬어요", 25, NEW_C)]
for i, (code, err, why, n_, c) in enumerate(pe):
    y = 200 + i * 172
    o += cell({"id": f"c-pe{i}", "lines": [code], "n": n_, "out": [err], "err": True}, 96, y, 1180, attrs=f' data-build-in="rise order {i + 1}"')
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:1320px;top:{y}px;width:504px;height:140px;background:{CARD};border:2px solid {LINE};border-left:12px solid {c};border-radius:16px;padding:0 24px;display:flex;flex-direction:column;justify-content:center;gap:6px">'
             + p(f"font-size:22px;font-weight:700;color:{c}", "% 방식" if c == OLD_C else "f-string") + p(f"font-size:25px;font-weight:700;color:{INK}", e(why)) + '</div>')
o.append(caption("% 는 자리 수와 값 수를, f-string은 콜론 뒤 모양과 타입을 먼저 봐요.", 920))
W("fmt-err", o, "포맷팅에서 자주 나는 오류예요. 위 세 개는 % 방식이에요. %d는 숫자 자리라서 글자 kim을 넣으면 TypeError가 나요. 반대로 %d에 3.141592 같은 실수를 넣으면 오류 없이 소수점 아래를 버린 3이 나와요. 자리가 두 개인데 값을 하나만 주면 값이 모자란다는 오류, 자리는 하나인데 값을 두 개 주면 남는 값이 있다는 오류가 나요. f-string은 자리와 값이 한곳에 있어서 개수 오류가 없어요. 대신 콜론 뒤 모양이 값의 타입과 안 맞으면 ValueError가 나요. 글자 name에 정수 모양 d를 준 경우예요. 모두 실제로 실행한 결과의 마지막 줄이에요.")

# ---------- part 6 ----------
EB6S = "2. 리스트와 튜플"
T6, T6BG = "#A23B72", "#F6E7EF"


def slots(items, left, top, w=170, h=96, hi=(), top_lbl=True, bot_lbl=False, attrs="", fs=34, color=None):
    """List items in a row of boxes with index numbers above (and negative numbers below)."""
    c = color or T6
    n = len(items)
    o = [f'<div{attrs} style="position:absolute;left:{left}px;top:{top}px;display:flex;flex-direction:row;gap:8px">']
    for i, it in enumerate(items):
        on = i in hi
        o.append('<div style="display:flex;flex-direction:column;align-items:center;gap:8px">'
                 + (p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{c}", str(i)) if top_lbl else "")
                 + p(f"width:{w}px;height:{h}px;border-radius:14px;border:3px solid {c if on else LINE};background:{T6BG if on else CARD};font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:{h - 6}px;text-align:center;color:{INK};white-space:pre", e(it))
                 + (p(f"font-family:{MONO};font-size:22px;color:{GRAY}", str(i - n)) if bot_lbl else "") + '</div>')
    o.append('</div>')
    return "".join(o)


o = [sec("list-make")] + head(EB6S, "리스트는 값 여러 개를 [ ] 에 담아요", T6)
o += cell({"id": "c-lm", "lines": ["prices = [4500, 5000, 6500]", "print(prices)", "print(len(prices))", "print(type(prices))"], "n": 1,
           "out": ["[4500, 5000, 6500]", "3", "<class 'list'>"]}, 96, 210, 800, sel="c-lm")
o.append(p(f"position:absolute;left:960px;top:210px;width:864px;font-family:{MONO};font-size:30px;font-weight:700;color:{T6}", "prices", ' data-build-in="fade order 1"'))
o.append(slots(["4500", "5000", "6500"], 960, 262, 250, 110, attrs=' data-build-in="rise order 1"', fs=40))
lm = [("[ ]", "대괄호로 감싸고 쉼표로 나눠요"), ("len(prices)", "담긴 개수예요. 3"), ("<class 'list'>", "타입 이름은 list예요")]
for i, (k, d) in enumerate(lm):
    o.append(card(960, 470 + i * 140, 864, 120, '<div style="display:flex;flex-direction:row;align-items:center;gap:24px">' + mono(k, 30, T6, T6BG) + p(f"font-size:26px;color:{INK}", e(d)) + '</div>',
                  None, f' data-build-in="rise order {i + 2}"', "justify-content:center"))
o.append(caption("변수 하나에 값 하나였다면, 리스트는 변수 하나에 값 여러 개예요.", 920))
W("list-make", o, "지금까지 변수 하나에는 값 하나만 넣었어요. 메뉴 가격 세 개를 넣으려면 변수 세 개가 필요했어요. 리스트는 값 여러 개를 대괄호로 감싸 한 변수에 담아요. 값 사이는 쉼표로 나눠요. len()은 1파트에서 글자 수를 셌던 함수인데, 리스트에 쓰면 담긴 값의 개수를 세요. type()으로 보면 list예요. 이 파트도 새 커널이라 셀 번호가 [1]부터예요. 출력은 실제로 실행한 결과예요.", ("lists", "리스트와 튜플"))

o = [sec("list-index")] + head(EB6S, "꺼내는 법은 문자열과 같아요", T6)
o += cell({"id": "c-li", "lines": ['menus = ["coffee", "latte", "cake"]', "print(menus[0])", "print(menus[-1])", "print(menus[0:2])"], "n": 2,
           "out": ["coffee", "cake", "['coffee', 'latte']"]}, 96, 210, 800, sel="c-li")
o.append(slots(["coffee", "latte", "cake"], 960, 210, 270, 110, hi=(0, 2), bot_lbl=True, attrs=' data-build-in="rise order 1"'))
li = [("menus[0]", "'coffee'", "0번, 맨 앞"), ("menus[-1]", "'cake'", "뒤에서 첫째"), ("menus[0:2]", "['coffee', 'latte']", "0번부터 2번 앞까지. 결과도 리스트")]
for i, (k, r, d) in enumerate(li):
    o.append(card(960, 460 + i * 140, 864, 120, '<div style="display:flex;flex-direction:row;align-items:center;gap:20px">' + mono(k, 28, T6, T6BG)
                  + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{INK};white-space:pre", e("→ " + r)) + '</div>' + p(f"font-size:22px;color:{SUB}", e(d)),
                  None, f' data-build-in="rise order {i + 2}"', "justify-content:center;gap:8px"))
o.append(caption("1파트의 word[0], word[0:2]와 똑같아요. 번호는 0부터 세요.", 920))
W("list-index", o, "리스트에서 값을 꺼내는 법은 1파트의 문자열과 똑같아요. 대괄호 안에 번호를 적으면 그 자리의 값을 꺼내요. 번호는 0부터 세고, -1은 맨 뒤예요. 시작과 끝 번호를 콜론으로 이으면 그 구간을 잘라요. 문자열을 자르면 문자열이 나왔듯이, 리스트를 자르면 리스트가 나와요. 출력의 ['coffee', 'latte']가 그 모양이에요. 출력은 실제로 실행한 결과예요.")

o = [sec("list-change")] + head(EB6S, "리스트는 값을 바꾸고 더할 수 있어요", T6)
o += cell({"id": "c-lc", "lines": ["prices[0] = 4800", "prices.append(3000)", "print(prices)", "print(sum(prices))", "print(max(prices))", "print(min(prices))"], "n": 3,
           "out": ["[4800, 5000, 6500, 3000]", "19300", "6500", "3000"]}, 96, 210, 800, sel="c-lc")
steps = [("처음", ["4500", "5000", "6500"], ()), ("prices[0] = 4800", ["4800", "5000", "6500"], (0,)), ("prices.append(3000)", ["4800", "5000", "6500", "3000"], (3,))]
for i, (k, its, hi) in enumerate(steps):
    y = 210 + i * 190
    o.append(p(f"position:absolute;left:960px;top:{y}px;width:864px;font-family:{MONO if i else SANS};font-size:26px;font-weight:700;color:{T6 if i else SUB}", e(k), f' data-build-in="rise order {i + 1}"'))
    o.append(slots(its, 960, y + 44, 190, 84, hi=hi, top_lbl=False, attrs=f' data-build-in="rise order {i + 1}"', fs=32))
o.append(card(960, 790, 864, 100, '<div style="display:flex;flex-direction:row;align-items:center;gap:18px">' + mono("sum()", 28, T6, T6BG) + mono("max()", 28, T6, T6BG) + mono("min()", 28, T6, T6BG)
              + p(f"font-size:24px;color:{INK}", "합계, 가장 큰 값, 가장 작은 값") + '</div>', None, ' data-build-in="rise order 4"', "justify-content:center"))
o.append(caption("append는 맨 뒤에 하나를 더해요. 담긴 개수가 3에서 4가 돼요.", 940))
W("list-change", o, "리스트는 담은 뒤에도 고칠 수 있어요. prices[0] = 4800은 12의 1파트의 = 와 같아요. 0번 자리에 새 값을 넣어서 4500이 4800으로 바뀌어요. prices.append(3000)은 맨 뒤에 3000을 하나 더해요. 점 뒤에 붙여 쓰는 함수라서 리스트 이름 뒤에 점을 찍고 적어요. sum, max, min은 숫자 리스트의 합계, 가장 큰 값, 가장 작은 값을 구해요. 앞 셀에서 만든 prices를 이어서 써요. 출력은 실제로 실행한 결과예요.")

o = [sec("list-methods")] + head(EB6S, "넣고 빼는 메서드: append, insert, remove, pop", T6)
o += cell({"id": "c-lmt", "lines": ['cart = ["coffee", "latte"]', 'cart.append("cake")', 'cart.insert(0, "tea")', "print(cart)", 'cart.remove("latte")', "print(cart)", "last = cart.pop()", "print(last)", "print(cart)"], "n": 4,
           "out": ["['tea', 'coffee', 'latte', 'cake']", "['tea', 'coffee', 'cake']", "cake", "['tea', 'coffee']"]}, 96, 200, 820, sel="c-lmt")
mt = [('cart.append("cake")', ["coffee", "latte", "cake"], (2,), "맨 뒤에 하나 더하기"), ('cart.insert(0, "tea")', ["tea", "coffee", "latte", "cake"], (0,), "0번 자리에 끼워 넣기"),
      ('cart.remove("latte")', ["tea", "coffee", "cake"], (), "값을 찾아 지우기"), ("cart.pop()", ["tea", "coffee"], (), "맨 뒤를 꺼내 돌려주기")]
for i, (k, its, hi, d) in enumerate(mt):
    y = 200 + i * 172
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:960px;top:{y}px;width:864px;height:156px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:12px 22px;display:flex;flex-direction:column;justify-content:center;gap:10px">'
             + '<div style="display:flex;flex-direction:row;align-items:center;gap:16px">' + mono(k, 24, T6, T6BG) + p(f"font-size:22px;color:{SUB}", e(d)) + '</div>'
             + slots(its, 0, 0, 150, 54, hi=hi, top_lbl=False, fs=24).replace("position:absolute;left:0px;top:0px;", "") + '</div>')
o += cell({"id": "c-lmt2", "lines": ['cart.remove("juice")'], "n": 5, "out": ["ValueError: list.remove(x): x not in list"], "err": True}, 96, 760, 820, attrs=' data-build-in="rise order 5"')
o.append(caption("없는 값을 remove 하면 ValueError가 나요.", 940))
W("list-methods", o, "리스트 이름 뒤에 점을 찍고 붙여 쓰는 함수를 메서드라고 불러요. append는 맨 뒤에 하나를 더해요. insert는 번호와 값을 받아 그 자리에 끼워 넣고, 원래 있던 값은 한 칸씩 뒤로 밀려요. remove는 번호가 아니라 값을 찾아 지워요. 같은 값이 여러 개면 앞의 하나만 지워요. pop은 맨 뒤 값을 꺼내 돌려줘서 last 같은 변수에 받을 수 있어요. pop(0)처럼 번호를 주면 그 자리를 꺼내요. 리스트에 없는 juice를 remove하면 ValueError가 나요. 출력은 실제로 실행한 결과예요.")

o = [sec("list-find")] + head(EB6S, "찾고 세고 정렬하는 메서드: count, index, sort", T6)
o += cell({"id": "c-lf", "lines": ["scores = [70, 95, 80, 95]", "print(scores.count(95))", "print(scores.index(80))", "print(95 in scores)", "scores.sort()", "print(scores)", "scores.sort(reverse=True)", "print(scores)"], "n": 6,
           "out": ["2", "2", "True", "[70, 80, 95, 95]", "[95, 95, 80, 70]"]}, 96, 200, 820, sel="c-lf")
o.append(slots(["70", "95", "80", "95"], 960, 200, 190, 90, hi=(1, 3), attrs=' data-build-in="rise order 1"', fs=34))
lf = [("scores.count(95)", "2", "95가 몇 개인지"), ("scores.index(80)", "2", "80이 몇 번 자리인지"), ("95 in scores", "True", "들어 있는지 True, False로"),
      ("scores.sort()", "[70, 80, 95, 95]", "작은 수부터 정렬. 리스트가 바뀌어요"), ("scores.sort(reverse=True)", "[95, 95, 80, 70]", "큰 수부터 정렬")]
for i, (k, r, d) in enumerate(lf):
    y = 360 + i * 108
    o.append(f'<div data-build-in="rise order {i + 2}" style="position:absolute;left:960px;top:{y}px;width:864px;height:96px;background:{CARD};border:2px solid {LINE};border-radius:16px;padding:0 22px;display:flex;flex-direction:row;align-items:center;gap:16px">'
             + '<div style="width:400px;flex:none">' + mono(k, 22, T6, T6BG, "display:inline-block") + '</div>'
             + '<div style="flex:1;display:flex;flex-direction:column;gap:2px">' + p(f"font-family:{MONO};font-size:22px;font-weight:700;color:{INK};white-space:pre", e(r)) + p(f"font-size:20px;color:{SUB}", e(d)) + '</div></div>')
o.append(caption("index의 답도 0부터 센 번호예요. 80은 0, 1, 2번째라서 2예요.", 940))
W("list-find", o, "count는 값이 몇 개 들어 있는지 세요. 95가 두 번 있어서 2예요. index는 그 값이 처음 나오는 번호를 알려 줘요. 번호는 0부터 세니까 80은 2번이에요. in은 메서드는 아니지만 같이 쓰면 좋아요. 12의 4파트의 비교처럼 True나 False로 답해요. in과 not in은 14의 1파트에서 자세히 봐요. sort는 리스트를 작은 수부터 정렬해요. 새 리스트를 만드는 게 아니라 scores 자체가 바뀌어요. reverse=True를 넣으면 큰 수부터예요. 글자 리스트도 sort하면 가나다, abc 순서로 정렬돼요. 출력은 실제로 실행한 결과예요.")

o = [sec("list-method-map")] + head(EB6S, "리스트에 쓰는 메서드와 함수 한눈에", T6)
mm = [("넣기", [("append(값)", "맨 뒤에 더하기"), ("insert(번호, 값)", "그 자리에 끼우기")]),
      ("빼기", [("remove(값)", "값을 찾아 지우기"), ("pop()", "맨 뒤를 꺼내기")]),
      ("찾기", [("count(값)", "몇 개인지"), ("index(값)", "몇 번 자리인지")]),
      ("정렬", [("sort()", "작은 수부터"), ("sort(reverse=True)", "큰 수부터")])]
for i, (t, rows) in enumerate(mm):
    x = 96 + i * 438
    o.append(card(x, 200, 414, 330, p(f"font-size:30px;font-weight:700;color:{T6}", t)
                  + "".join('<div style="display:flex;flex-direction:column;gap:6px">' + mono(k, 22, T6, T6BG, "align-self:flex-start") + p(f"font-size:21px;color:{SUB}", e(d)) + '</div>' for k, d in rows),
                  T6, f' data-build-in="rise order {i + 1}"', "gap:22px"))
o.append(card(96, 570, 1728, 230, p(f"font-size:28px;font-weight:700;color:{INK}", "점을 찍는 메서드와 괄호로 감싸는 함수")
              + '<div style="display:flex;flex-direction:row;gap:60px;align-items:center">'
              + '<div style="display:flex;flex-direction:column;gap:8px">' + mono("cart.append(\"cake\")", 26, T6, T6BG, "align-self:flex-start") + p(f"font-size:22px;color:{SUB}", "메서드. 리스트 이름 뒤에 점") + '</div>'
              + '<div style="display:flex;flex-direction:column;gap:8px">' + mono("len(cart)  sum(prices)  max(prices)  min(prices)", 26, INK, "#F1F0EC", "align-self:flex-start") + p(f"font-size:22px;color:{SUB}", "함수. 괄호 안에 리스트") + '</div></div>',
              None, ' data-build-in="rise order 5"', "justify-content:center;gap:16px"))
W("list-method-map", o, "앞 두 장의 메서드를 할 일별로 모았어요. 넣기는 append와 insert, 빼기는 remove와 pop, 찾기는 count와 index, 정렬은 sort예요. 아래는 헷갈리기 쉬운 두 모양이에요. append처럼 리스트 이름 뒤에 점을 찍고 쓰는 건 메서드예요. len, sum, max, min처럼 괄호 안에 리스트를 넣는 건 함수예요. 둘 다 결과는 비슷하게 쓰지만 적는 자리가 달라요.")

o = [sec("list-slice")] + head(EB6S, "[시작:끝:간격]으로 원하는 만큼 잘라요", T6)
o += cell({"id": "c-lsl", "lines": ["nums = [10, 20, 30, 40, 50, 60]", "print(nums[1:4])", "print(nums[:3])", "print(nums[3:])", "print(nums[-2:])", "print(nums[::2])", "print(nums[1::2])", "print(nums[::-1])"], "n": 7,
           "out": ["[20, 30, 40]", "[10, 20, 30]", "[40, 50, 60]", "[50, 60]", "[10, 30, 50]", "[20, 40, 60]", "[60, 50, 40, 30, 20, 10]"]}, 96, 200, 700, sel="c-lsl")
sl6 = [("nums[1:4]", (1, 2, 3), "1번부터 4번 앞까지"), ("nums[:3]", (0, 1, 2), "처음부터 세 개"), ("nums[3:]", (3, 4, 5), "3번부터 끝까지"), ("nums[-2:]", (4, 5), "뒤에서 두 개"),
       ("nums[::2]", (0, 2, 4), "처음부터 한 칸 건너뛰며"), ("nums[1::2]", (1, 3, 5), "1번부터 한 칸 건너뛰며"), ("nums[::-1]", (0, 1, 2, 3, 4, 5), "거꾸로 전부")]
for i, (k, hi, d) in enumerate(sl6):
    y = 200 + i * 104
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:840px;top:{y}px;width:984px;height:92px;background:{CARD};border:2px solid {LINE};border-radius:16px;padding:0 18px;display:flex;flex-direction:row;align-items:center;gap:16px">'
             + '<div style="width:250px;flex:none;display:flex;flex-direction:column;gap:2px">' + mono(k, 22, T6, T6BG, "align-self:flex-start") + p(f"font-size:18px;color:{SUB}", e(d)) + '</div>'
             + slots(["10", "20", "30", "40", "50", "60"], 0, 0, 100, 54, hi=hi, top_lbl=False, fs=24).replace("position:absolute;left:0px;top:0px;", "") + '</div>')
o.append(caption("세 번째 숫자는 간격이에요. 2면 한 칸씩 건너뛰고, -1이면 거꾸로 가요.", 944))
W("list-slice", o, "1파트에서 문자열을 자를 때 쓴 [시작:끝]을 리스트에도 그대로 써요. 끝 번호 자리는 들어가지 않아서 nums[1:4]는 1, 2, 3번이에요. 시작을 비우면 처음부터, 끝을 비우면 끝까지예요. 음수는 뒤에서 센 번호라서 nums[-2:]는 마지막 두 개예요. 콜론을 하나 더 붙이면 세 번째 숫자가 간격이에요. ::2는 하나 건너 하나씩, 1::2는 1번부터 하나 건너 하나씩이에요. ::-1은 거꾸로 전부라서 리스트를 뒤집은 새 리스트가 나와요. 자른 결과는 새 리스트라서 nums는 그대로예요. 출력은 실제로 실행한 결과예요.")

o = [sec("list-extract")] + head(EB6S, "안쪽 리스트와 글자도 번호로 꺼내요", T6)
o += cell({"id": "c-lex", "lines": ["table = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]", "print(table[1])", "print(table[1][2])", "print(table[-1][-1])", "print(table[0][:2])", "print(menus[0][0])", "print(menus[1][-3:])"], "n": 8,
           "out": ["[4, 5, 6]", "6", "9", "[1, 2]", "c", "tte"]}, 96, 200, 800, sel="c-lex")
for i, row in enumerate([["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"]]):
    hi = {0: (0, 1), 1: (2,), 2: (2,)}[i]
    o.append(p(f"position:absolute;left:960px;top:{[258, 334, 418][i]}px;width:140px;font-family:{MONO};font-size:22px;font-weight:700;color:{T6}", f"table[{i}]", ' data-build-in="fade order 1"'))
    o.append(slots(row, 1110, 200 + i * 84, 110, 70, hi=hi, top_lbl=(i == 0), attrs=' data-build-in="rise order 1"', fs=30).replace(f"top:{200 + i * 84}px", f"top:{(200 if i == 0 else 232 + i * 84)}px"))
ex = [("table[1][2]", "1번 줄의 2번 칸 → 6"), ("table[-1][-1]", "마지막 줄의 마지막 칸 → 9"), ("table[0][:2]", "0번 줄을 앞에서 두 개 → [1, 2]"), ("menus[0][0]  menus[1][-3:]", "글자도 꺼내고 잘라요 → c, tte")]
for i, (k, d) in enumerate(ex):
    o.append(card(960, 520 + i * 100, 864, 88, '<div style="display:flex;flex-direction:row;align-items:center;gap:18px">' + mono(k, 22, T6, T6BG) + p(f"font-size:21px;color:{INK}", e(d)) + '</div>',
                  None, f' data-build-in="rise order {i + 2}"', "justify-content:center;padding:0 22px"))
W("list-extract", o, "리스트 안에 리스트를 넣으면 표 모양이 돼요. 대괄호 번호를 두 번 쓰면 앞 번호로 줄을, 뒤 번호로 칸을 골라요. table[1][2]는 1번 줄의 2번 칸 6이에요. 음수 번호도 그대로 써서 table[-1][-1]은 마지막 줄의 마지막 칸 9예요. 줄을 고른 다음에 자를 수도 있어서 table[0][:2]는 [1, 2]예요. 리스트 안의 글자에도 번호를 한 번 더 쓰면 글자를 꺼내요. menus[0]은 coffee라서 menus[0][0]은 c, menus[1]은 latte라서 [-3:]은 tte예요. menus는 이 파트 2번 셀의 리스트예요. 출력은 실제로 실행한 결과예요.")

o = [sec("list-more")] + head(EB6S, "리스트를 잇고, 뒤집고, 복사하고, 비워요", T6)
o += cell({"id": "c-lmo", "lines": ["a = [3, 1, 2]", "b = [5, 4]", "print(a + b, a * 2)", "a.extend(b)", "print(a)", "print(sorted(a), a)", "a.reverse()", "print(a)", "c = a.copy()", "c.clear()", "print(a, c)"], "n": 9,
           "out": ["[3, 1, 2, 5, 4] [3, 1, 2, 3, 1, 2]", "[3, 1, 2, 5, 4]", "[1, 2, 3, 4, 5] [3, 1, 2, 5, 4]", "[4, 5, 2, 1, 3]", "[4, 5, 2, 1, 3] []"]}, 96, 190, 760, sel="c-lmo")
mo = [("a + b   a * 2", "두 리스트를 이은 새 리스트, 두 번 반복한 새 리스트"), ("a.extend(b)", "a 뒤에 b를 이어 붙여요. a가 바뀌어요"), ("sorted(a)", "정렬한 새 리스트를 돌려줘요. a는 그대로"),
      ("a.reverse()", "a를 거꾸로 뒤집어요. 정렬이 아니라 순서만 뒤집기"), ("a.copy()   c.clear()", "복사본을 만들고, 복사본만 비워요. a는 그대로")]
for i, (k, d) in enumerate(mo):
    o.append(card(900, 190 + i * 150, 924, 134, mono(k, 24, T6, T6BG, "align-self:flex-start") + p(f"font-size:22px;color:{INK}", e(d)), None, f' data-build-in="rise order {i + 1}"', "justify-content:center;gap:8px"))
W("list-more", o, "리스트를 다룰 때 자주 쓰는 것들을 더 봐요. + 는 두 리스트를 이어 붙인 새 리스트를, * 는 반복한 새 리스트를 만들어요. 12의 3파트에서 본 글자의 + 와 * 와 같은 모양이에요. extend는 a 자체에 b를 이어 붙여서 a가 바뀌어요. sorted는 sort와 달리 정렬한 새 리스트를 돌려주고 a는 그대로 둬요. 그래서 print(sorted(a), a)의 뒤쪽 a는 정렬 전 모양이에요. reverse는 크기와 상관없이 순서만 거꾸로 뒤집어요. copy는 복사본을 만들어요. 복사본 c를 clear로 비워도 a는 그대로 남아요. 출력은 실제로 실행한 결과예요.")

o = [sec("list-str")] + head(EB6S, "split 으로 글자를 리스트로, join 으로 리스트를 글자로", T6)
o += cell({"id": "c-lst", "lines": ['text = "coffee,latte,cake"', 'words = text.split(",")', "print(words)", "print(len(words))", 'print(" / ".join(words))', 'print("hello world".split())', 'print(list("abc"))'], "n": 10,
           "out": ["['coffee', 'latte', 'cake']", "3", "coffee / latte / cake", "['hello', 'world']", "['a', 'b', 'c']"]}, 96, 200, 860, sel="c-lst")
o.append(card(1010, 200, 814, 200, mono('"coffee,latte,cake"', 26, INK, "#F6F5F1", "align-self:flex-start")
              + '<div style="display:flex;flex-direction:row;align-items:center;gap:14px">' + mono('.split(",")', 24, T6, T6BG) + p(f"font-size:22px;color:{SUB}", "쉼표에서 잘라") + '</div>'
              + mono("['coffee', 'latte', 'cake']", 26, INK, "#F6F5F1", "align-self:flex-start"), None, ' data-build-in="rise order 1"', "gap:12px"))
o.append(card(1010, 420, 814, 200, mono("['coffee', 'latte', 'cake']", 26, INK, "#F6F5F1", "align-self:flex-start")
              + '<div style="display:flex;flex-direction:row;align-items:center;gap:14px">' + mono('" / ".join(words)', 24, T6, T6BG) + p(f"font-size:22px;color:{SUB}", "사이에 / 를 넣어 이어서") + '</div>'
              + mono('"coffee / latte / cake"', 26, INK, "#F6F5F1", "align-self:flex-start"), None, ' data-build-in="rise order 2"', "gap:12px"))
o.append(card(1010, 640, 814, 160, p(f"font-size:22px;color:{INK}", e("split()처럼 괄호를 비우면 빈칸에서 잘라요.")) + p(f"font-size:22px;color:{INK}", e('list("abc")는 글자를 한 글자씩 나눠 리스트로 만들어요.')),
              None, ' data-build-in="rise order 3"', "justify-content:center;gap:10px"))
W("list-str", o, "글자와 리스트를 오가는 두 메서드예요. split은 글자를 잘라 리스트로 만들어요. 괄호 안에 자를 기준을 적고, 비워 두면 빈칸에서 잘라요. 엑셀이나 CSV처럼 쉼표로 이어진 데이터를 나눌 때 자주 써요. join은 반대로 리스트의 글자들을 하나로 이어요. 사이에 넣을 글자를 앞에 적고 점 뒤에 join을 쓰는 순서가 조금 낯설어요. list(\"abc\")는 글자를 한 글자씩 나눠 리스트로 만들어요. 출력은 실제로 실행한 결과예요.")

o = [sec("tuple")] + head(EB6S, "튜플은 ( ) 에 담고 바꿀 수 없어요", T6)
o += cell({"id": "c-tp", "lines": ['order = ("coffee", 4500, 2)', "print(order[0])", "print(order[1] * order[2])", "print(type(order))"], "n": 11,
           "out": ["coffee", "9000", "<class 'tuple'>"]}, 96, 210, 860, sel="c-tp")
o += cell({"id": "c-tp2", "lines": ["order[1] = 5000"], "n": 12, "out": ["TypeError: 'tuple' object does not support item assignment"], "err": True}, 96, 640, 1728, attrs=' data-build-in="rise order 3"')
o.append(card(1010, 210, 814, 190, '<div style="display:flex;flex-direction:row;align-items:center;gap:20px">' + mono("[ ]", 34, T6, T6BG) + p(f"font-size:30px;font-weight:700;color:{INK}", "리스트") + '</div>'
              + p(f"font-size:24px;color:{SUB}", "값을 바꾸고 더할 수 있어요. 장바구니처럼 늘어나는 것"), None, ' data-build-in="rise order 1"', "justify-content:center"))
o.append(card(1010, 420, 814, 190, '<div style="display:flex;flex-direction:row;align-items:center;gap:20px">' + mono("( )", 34, T6, T6BG) + p(f"font-size:30px;font-weight:700;color:{INK}", "튜플") + '</div>'
              + p(f"font-size:24px;color:{SUB}", "만든 뒤 못 바꿔요. 주문 한 건처럼 한 묶음인 것"), None, ' data-build-in="rise order 2"', "justify-content:center"))
o.append(caption("1파트의 \"%s %d\" % (name, age)에서 괄호로 묶은 것도 튜플이었어요.", 900))
W("tuple", o, "튜플은 소괄호로 감싸요. 꺼내는 법은 리스트와 같아서 order[0]은 coffee예요. order[1] * order[2]처럼 꺼낸 값으로 계산도 해요. 다른 점은 한 번 만들면 바꿀 수 없다는 거예요. order[1] = 5000을 하면 TypeError가 나요. 메뉴, 가격, 수량처럼 한 묶음으로 같이 다니는 값은 튜플에 담고, 장바구니처럼 늘었다 줄었다 하는 건 리스트에 담아요. 1파트에서 % 뒤에 괄호로 묶어 넣은 (name, age)가 바로 튜플이었어요. 출력은 실제로 실행한 결과예요.")

o = [sec("tuple-more")] + head(EB6S, "튜플은 count, index, 꺼내 담기, 바꾸기", T6)
o += cell({"id": "c-tm", "lines": ["date = (2026, 11, 2)", "print(date.count(2))", "print(date.index(11))", "year, month, day = date", "print(year, month, day)",
                                   'a = "kim"', 'b = "lee"', "a, b = b, a", "print(a, b)", "print(list(date))", "print(tuple(cart))"], "n": 13,
           "out": ["1", "1", "2026 11 2", "lee kim", "[2026, 11, 2]", "('tea', 'coffee')"]}, 96, 200, 820, sel="c-tm")
tm = [("date.count(2)  date.index(11)", "튜플의 메서드는 둘뿐이에요. 바꾸는 메서드가 없어요"), ("year, month, day = date", "튜플 값을 변수 여러 개에 한 번에 꺼내 담아요"),
      ("a, b = b, a", "두 변수의 값을 맞바꿔요. lee kim"), ("list(date)  tuple(cart)", "튜플을 리스트로, 리스트를 튜플로 바꿔요")]
for i, (k, d) in enumerate(tm):
    o.append(card(960, 200 + i * 170, 864, 150, mono(k, 24, T6, T6BG, "align-self:flex-start") + p(f"font-size:22px;color:{INK}", e(d)), None, f' data-build-in="rise order {i + 1}"', "justify-content:center;gap:10px"))
o.append(caption("날짜, 좌표, 주문 한 건처럼 바뀌지 않는 한 묶음은 튜플에 담아요.", 970))
W("tuple-more", o, "튜플은 바꿀 수 없어서 메서드가 count와 index 둘뿐이에요. append, remove, sort 같은 바꾸는 메서드는 없어요. 튜플 값은 year, month, day = date처럼 이름을 나란히 적어 한 번에 꺼내 담아요. 이 모양으로 a, b = b, a를 쓰면 두 변수 값을 맞바꿀 수 있어요. 오른쪽 b, a가 먼저 ('lee', 'kim') 묶음이 되고, 그 값이 왼쪽 a, b에 나눠 들어가요. 튜플 값을 고쳐야 하면 list()로 바꿔서 고쳐요. 반대로 tuple()은 리스트를 튜플로 바꿔요. tuple(cart)의 cart는 앞 장에서 pop까지 한 장바구니예요. 출력은 실제로 실행한 결과예요.")

o = [sec("tuple-slice")] + head(EB6S, "튜플도 꺼내고, 자르고, 이어요", T6)
o += cell({"id": "c-tsl", "lines": ["t = (10, 20, 30, 40)", "print(t[1:3])", "print(t[::-1])", "print(t + (50,))", "print(len(t), sum(t), max(t))", "print(30 in t)", 'info = ("kim", (2026, 11, 2))', "print(info[1][0])"], "n": 14,
           "out": ["(20, 30)", "(40, 30, 20, 10)", "(10, 20, 30, 40, 50)", "4 100 40", "True", "2026"]}, 96, 200, 860, sel="c-tsl")
ts = [("t[1:3]   t[::-1]", "자르기는 리스트와 같아요. 결과는 튜플"), ("t + (50,)", "이어 붙인 새 튜플. 값 하나짜리 튜플은 뒤에 쉼표"), ("len(t)  sum(t)  max(t)  30 in t", "함수와 in도 그대로 써요"),
      ('info[1][0]', "튜플 안의 튜플도 번호 두 번 → 2026")]
for i, (k, d) in enumerate(ts):
    o.append(card(1010, 200 + i * 170, 814, 150, mono(k, 22, T6, T6BG, "align-self:flex-start") + p(f"font-size:22px;color:{INK}", e(d)), None, f' data-build-in="rise order {i + 1}"', "justify-content:center;gap:10px"))
o.append(caption("바꾸는 것만 안 되고, 꺼내고 자르는 건 리스트와 똑같아요.", 920))
W("tuple-slice", o, "튜플도 리스트처럼 번호로 꺼내고 [시작:끝:간격]으로 잘라요. 자른 결과는 튜플이에요. + 로 이어 붙이면 새 튜플이 생기고, 원래 t는 그대로예요. 값 하나짜리 튜플은 (50,)처럼 뒤에 쉼표를 붙여야 해요. 쉼표 없이 (50)이라고 쓰면 그냥 숫자 50이에요. len, sum, max, in도 리스트와 똑같이 써요. 이름과 날짜처럼 튜플 안에 튜플을 넣으면 info[1][0]처럼 번호를 두 번 써서 꺼내요. 출력은 실제로 실행한 결과예요.")

o = [sec("orders")] + head(EB6S, "주문 여러 건은 튜플을 리스트에 담아요", T6)
o += cell({"id": "c-od", "lines": ['orders = [("coffee", 4500, 2), ("latte", 5000, 1), ("cake", 6500, 3)]', "print(len(orders))", "print(orders[1])", "print(orders[1][0])",
                                    "print(orders[2][1] * orders[2][2])", "print(orders[0:2])"], "n": 15,
           "out": ["3", "('latte', 5000, 1)", "latte", "19500", "[('coffee', 4500, 2), ('latte', 5000, 1)]"]}, 96, 200, 1728, sel="c-od")
gx, gy = 330, 716
o.append(p(f"position:absolute;left:96px;top:{gy + 6}px;width:220px;font-size:22px;color:{SUB};line-height:1.5", "앞 번호는 몇째 주문,<br>뒤 번호는 몇째 값", ' data-build-in="fade order 1"'))
for j, hd in enumerate(["[0] 메뉴", "[1] 가격", "[2] 수량"]):
    o.append(p(f"position:absolute;left:{gx + 120 + j * 230}px;top:{gy}px;width:220px;text-align:center;font-family:{MONO};font-size:22px;font-weight:700;color:{T6}", e(hd), ' data-build-in="fade order 1"'))
rows = [("coffee", "4500", "2"), ("latte", "5000", "1"), ("cake", "6500", "3")]
hl = {(1, 0), (2, 1), (2, 2)}
for i, r in enumerate(rows):
    y = gy + 36 + i * 64
    o.append(f'<div data-build-in="rise order 1" style="position:absolute;left:{gx}px;top:{y}px;display:flex;flex-direction:row;gap:10px;align-items:center">'
             + p(f"width:130px;flex:none;font-family:{MONO};font-size:22px;font-weight:700;color:{T6}", f"orders[{i}]")
             + "".join(p(f"width:220px;height:56px;border-radius:12px;border:3px solid {T6 if (i, j) in hl else LINE};background:{T6BG if (i, j) in hl else CARD};font-family:{MONO};font-size:26px;font-weight:700;line-height:50px;text-align:center;color:{INK}", e(v)) for j, v in enumerate(r))
             + '</div>')
o.append(card(1180, gy, 644, 220, p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{T6}", "orders[1][0]") + p(f"font-size:22px;color:{SUB}", "1번 주문의 0번 값 → 'latte'")
              + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{T6}", "orders[2][1] * orders[2][2]") + p(f"font-size:22px;color:{SUB}", "cake 가격 × 수량 → 19500"),
              None, ' data-build-in="rise order 2"', "justify-content:center;gap:6px"))
W("orders", o, "가상의 카페 주문 데이터예요. 주문 한 건은 메뉴, 가격, 수량을 묶은 튜플이고, 주문 여러 건을 리스트에 담았어요. 표로 보면 줄이 주문이고 칸이 값이에요. 대괄호를 두 번 쓰면 표의 한 칸을 꺼내요. 앞 번호로 몇째 주문인지 고르고, 뒤 번호로 그 안의 몇째 값인지 골라요. orders[1]은 latte 주문 튜플 전체, orders[1][0]은 그중 메뉴 이름 latte예요. orders[2][1] * orders[2][2]는 cake 가격 6500에 수량 3을 곱해 19500이에요. 잘라 내는 orders[0:2]는 앞 두 주문을 담은 리스트예요. 출력은 실제로 실행한 결과예요.")

o = [sec("orders-unpack")] + head(EB6S, "튜플의 값을 변수 여러 개에 한 번에 꺼내 담아요", T6)
o += cell({"id": "c-up", "lines": ["menu, price, qty = orders[2]", "print(menu, price, qty)", 'print(f"{menu} {qty}개, {price * qty:,}원")'], "n": 16,
           "out": ["cake 6500 3", "cake 3개, 19,500원"]}, 96, 200, 1728, sel="c-up")
o.append(p(f"position:absolute;left:96px;top:520px;width:1728px;font-family:{MONO};font-size:30px;font-weight:700;color:{INK}", e('orders[2]  =  ("cake", 6500, 3)'), ' data-build-in="fade order 1"'))
for i, (nm, v) in enumerate([("menu", "'cake'"), ("price", "6500"), ("qty", "3")]):
    o.append(var_box(f"vb-up{i}", nm, v, 96 + i * 584, 600, T6, 560, f' data-build-in="rise order {i + 2}"'))
o.append(caption("왼쪽 이름 수와 튜플 값 수가 같아야 해요. 순서대로 하나씩 들어가요.", 900))
W("orders-unpack", o, "orders[2][0], orders[2][1]처럼 번호를 두 번씩 쓰면 읽기 어려워요. 왼쪽에 이름을 쉼표로 나란히 적고 오른쪽에 튜플을 주면, 튜플의 값이 순서대로 하나씩 들어가요. menu에는 cake, price에는 6500, qty에는 3이 들어가요. 그다음은 1파트의 f-string으로 보기 좋게 출력해요. {price * qty:,}는 계산한 합계에 천 단위 콤마를 찍어요. 왼쪽 이름이 두 개뿐이면 값 수가 안 맞아 ValueError가 나요. 출력은 실제로 실행한 결과예요.")

o = [sec("orders-receipt")] + head(EB6S, "f-string으로 주문 영수증을 찍어요", T6)
o += cell({"id": "c-rc", "lines": ['print(f"{orders[0][0]:<7}{orders[0][1]:>6,}원 {orders[0][2]:>2}개")', 'print(f"{orders[1][0]:<7}{orders[1][1]:>6,}원 {orders[1][2]:>2}개")',
                                    'print(f"{orders[2][0]:<7}{orders[2][1]:>6,}원 {orders[2][2]:>2}개")', "total = orders[0][1] * orders[0][2]", "total += orders[1][1] * orders[1][2]",
                                    "total += orders[2][1] * orders[2][2]", 'print(f"합계 {total:,}원")'], "n": 17,
           "out": ["coffee  4,500원  2개", "latte   5,000원  1개", "cake    6,500원  3개", "합계 33,500원"], "wide": True}, 96, 200, 1728, sel="c-rc")
rc = [("{orders[0][0]:<7}", "메뉴를 일곱 칸 왼쪽 맞춤"), ("{orders[0][1]:>6,}", "가격을 여섯 칸, 콤마"), ("{orders[0][2]:>2}", "수량을 두 칸 오른쪽 맞춤")]
for i, (k, d) in enumerate(rc):
    o.append(card(96 + i * 584, 760, 560, 130, mono(k, 24, T6, T6BG, "align-self:flex-start") + p(f"font-size:22px;color:{SUB}", d), None, f' data-build-in="rise order {i + 1}"', "justify-content:center;gap:8px"))
o.append(caption("주문 한 건에 한 줄씩 적었어요. 줄이 같은 모양이라 칸이 맞아요.", 940))
W("orders-receipt", o, "1파트의 칸 수와 콤마를 리스트 데이터에 써 봐요. 메뉴는 일곱 칸 왼쪽 맞춤, 가격은 여섯 칸 오른쪽 맞춤에 콤마, 수량은 두 칸 오른쪽 맞춤이에요. 세 줄이 같은 모양이라 가격과 수량의 끝자리가 한 줄로 서요. 합계는 12의 3파트의 += 로 주문마다 가격 곱하기 수량을 더했어요. 9000, 5000, 19500을 더해 33500이고, 콤마를 찍어 33,500원이에요. 주문이 늘면 줄도 같이 늘어나는데, 같은 줄을 되풀이하는 일은 잠시 뒤에 볼 for 문이 줄여 줘요. 여기서 만든 total을 다음 장 영수증에서 써요. 출력은 실제로 실행한 결과예요.")

o = [sec("receipt-head")] + head(EB6S, "머리글의 한글은 화면에서 두 칸을 차지해요", T6)
o += cell({"id": "c-rh", "lines": ["print(f\"{'메뉴명':<10}{'단가':>8}{'수량':>5}{'금액':>10}\")", "print(f\"{'menu':<10}{'price':>8}{'qty':>5}{'amount':>10}\")",
                                   'print(f"{orders[0][0]:<10}{orders[0][1]:>8,}{orders[0][2]:>5}{orders[0][1] * orders[0][2]:>10,}")'], "n": 18,
           "out": ["메뉴명             단가   수량        금액", "menu         price  qty    amount", "coffee       4,500    2     9,000"], "wide": True}, 96, 200, 1728, sel="c-rh")
rh = [("< > ^", "왼쪽, 오른쪽, 가운데 맞춤", "{'메뉴명':<10}  {'단가':>8}  {'qty':^5}", "^ 는 남는 칸을 양쪽에 나눠요"),
      ("한글은 두 칸", "파이썬은 한 글자로 세는데 화면에선 두 칸이에요", "'메뉴명'은 세 글자지만 화면에선 여섯 칸", "그래서 머리글만 오른쪽으로 밀려요"),
      ("칸 수 줄이기", "한글 글자 수만큼 칸 수를 빼요", "{'메뉴명':<7}  {'단가':>6}  {'수량':>3}  {'금액':>8}", "글꼴에 따라 조금 어긋나면 머리글을 영어로 써요")]
for i, (t, d, code, sub) in enumerate(rh):
    o.append(card(96 + i * 584, 560, 560, 330, p(f"font-size:30px;font-weight:700;color:{T6}", t) + p(f"font-size:24px;font-weight:700;color:{INK}", e(d))
                  + p(f"font-family:{MONO};font-size:21px;font-weight:700;line-height:1.5;color:{T6};background:{T6BG};border-radius:10px;padding:8px 14px", e(code))
                  + p(f"font-size:21px;color:{SUB}", e(sub)), None, f' data-build-in="rise order {i + 1}"'))
o.append(caption("영어 머리글은 칸이 맞고, 한글 머리글만 밀렸어요.", 940))
W("receipt-head", o, "영수증 위에 메뉴명, 단가, 수량, 금액 머리글을 달아 봐요. 글자에도 1파트의 맞춤을 그대로 써요. < 는 왼쪽, > 는 오른쪽, ^ 는 가운데 맞춤이에요. 셀을 실행하면 영어 머리글은 아래 숫자 줄과 칸이 맞는데, 한글 머리글은 오른쪽으로 밀려요. 파이썬은 한글 한 글자를 한 칸으로 세는데, 화면에서는 한글이 영어 두 칸 너비로 보여서예요. 메뉴명은 세 글자라 세 칸만큼 밀려요. 그래서 한글 머리글은 한글 글자 수만큼 칸 수를 빼서 적어요. 10칸이면 메뉴명은 7, 8칸이면 단가는 6이에요. 글꼴에 따라 한글 너비가 딱 두 칸이 아니라 조금 어긋날 수 있어요. 그럴 땐 머리글을 영어로 쓰면 정확히 맞아요. 출력은 실제로 실행한 결과예요.")

o = [sec("receipt")] + head(EB6S, "머리글, 줄, 합계를 붙여 영수증을 완성해요", T6)
o += cell({"id": "c-rcp", "lines": ['print("=" * 33)', "print(f\"{'메뉴명':<7}{'단가':>6}{'수량':>3}{'금액':>8}\")", 'print("-" * 33)',
                                    'print(f"{orders[0][0]:<10}{orders[0][1]:>8,}{orders[0][2]:>5}{orders[0][1] * orders[0][2]:>10,}")',
                                    'print(f"{orders[1][0]:<10}{orders[1][1]:>8,}{orders[1][2]:>5}{orders[1][1] * orders[1][2]:>10,}")',
                                    'print(f"{orders[2][0]:<10}{orders[2][1]:>8,}{orders[2][2]:>5}{orders[2][1] * orders[2][2]:>10,}")',
                                    'print("-" * 33)', "print(f\"{'합계':<6}{total:>25,}\")", 'print("=" * 33)'], "n": 19,
           "out": ["=================================", "메뉴명        단가 수량      금액", "---------------------------------", "coffee       4,500    2     9,000",
                   "latte        5,000    1     5,000", "cake         6,500    3    19,500", "---------------------------------", "합계                       33,500", "================================="], "wide": True}, 96, 190, 1728, sel="c-rcp")
W("receipt", o, "앞 장에서 배운 걸 모아 메뉴표 모양의 영수증을 완성해요. 맨 위와 맨 아래는 = 33개, 머리글 아래와 합계 위는 - 33개로 줄을 그었어요. 12의 3파트에서 본 글자 곱하기라서 \"=\" * 33은 = 를 33번 이어 붙여요. 머리글은 칸 수를 한글 글자 수만큼 뺐어요. 주문 줄은 메뉴 10칸, 단가 8칸, 수량 5칸, 금액 10칸이라 모두 33칸이에요. 금액은 가격과 수량을 중괄호 안에서 바로 곱하고 콤마를 찍었어요. 합계는 orders-receipt 장에서 만든 total이에요. 합계도 한글이 두 글자라서 8칸 대신 6칸을 줬어요. 출력은 실제로 실행한 결과예요.")

o = [sec("for-intro")] + head(EB6S, "for 는 리스트에서 하나씩 꺼내 같은 일을 되풀이해요", T6)
o += cell({"id": "c-fi", "lines": ["for menu in menus:", "    print(menu)"], "n": 20, "out": ["coffee", "latte", "cake"]}, 96, 210, 760, sel="c-fi")
fi = [("for menu in menus:", "menus에서 하나씩 꺼내 menu에 넣어요. 끝에 콜론"), ("    print(menu)", "네 칸 들여 쓴 줄이 되풀이할 일이에요")]
for i, (k, d) in enumerate(fi):
    o.append(card(96, 560 + i * 170, 760, 150, mono(k, 28, T6, T6BG, "align-self:flex-start") + p(f"font-size:24px;color:{INK}", e(d)), None, f' data-build-in="rise order {i + 1}"', "justify-content:center;gap:10px"))
for i, v in enumerate(["coffee", "latte", "cake"]):
    y = 210 + i * 230
    o.append(f'<div data-build-in="rise order {i + 3}" style="position:absolute;left:940px;top:{y}px;width:884px;height:200px;background:{CARD};border:2px solid {LINE};border-left:12px solid {T6};border-radius:18px;padding:0 30px;display:flex;flex-direction:row;align-items:center;gap:24px">'
             + p(f"width:110px;flex:none;font-size:28px;font-weight:700;color:{T6}", f"{i + 1}번째")
             + '<div style="flex:1;display:flex;flex-direction:column;gap:12px">' + mono(f"menu = '{v}'", 28, INK, "#F6F5F1", "align-self:flex-start")
             + p(f"font-family:{MONO};font-size:26px;color:{SUB}", e(f"print(menu)  →  {v}")) + '</div></div>')
o.append(caption("값이 세 개라서 세 번 되풀이하고 끝나요.", 940))
W("for-intro", o, "앞 장 영수증에서 주문 줄을 세 번 똑같은 모양으로 적었어요. 주문이 100건이면 100줄을 적어야 해요. for 문은 리스트에서 값을 하나씩 꺼내 같은 일을 되풀이해요. for 다음에 꺼낸 값을 담을 이름, in 다음에 리스트를 적고 끝에 콜론을 붙여요. 그 아래 네 칸 들여 쓴 줄이 되풀이할 일이에요. 첫 번째에는 menu에 coffee가 들어가 print가 coffee를 찍고, 두 번째에는 latte, 세 번째에는 cake가 들어가요. 꺼낼 값이 없으면 끝나요. menus는 이 파트 2번 셀에서 만든 리스트예요. 출력은 실제로 실행한 결과예요.")

o = [sec("for-orders")] + head(EB6S, "튜플을 꺼내 담으면서 되풀이해요", T6)
o += cell({"id": "c-fo3", "lines": ["for menu, price, qty in orders:", "    print(menu, price, qty)"], "n": 21, "out": ["coffee 4500 2", "latte 5000 1", "cake 6500 3"]}, 96, 210, 860, sel="c-fo3")
o.append(card(1010, 210, 814, 360, p(f"font-size:26px;font-weight:700;color:{SUB}", "for 없이 적으면")
              + p(f"font-family:{MONO};font-size:22px;line-height:1.6;color:{INK};white-space:pre", e("menu, price, qty = orders[0]\nprint(menu, price, qty)\nmenu, price, qty = orders[1]\nprint(menu, price, qty)\nmenu, price, qty = orders[2]\nprint(menu, price, qty)")),
              None, ' data-build-in="rise order 1"'))
o.append(p(f"position:absolute;left:96px;top:620px;width:1728px;font-size:24px;font-weight:700;color:{T6}", "한 번 돌 때마다 주문 튜플 하나가 세 이름에 나눠 들어가요", ' data-build-in="fade order 2"'))
for j, hd in enumerate(["menu", "price", "qty"]):
    o.append(p(f"position:absolute;left:{356 + j * 300}px;top:672px;width:280px;text-align:center;font-family:{MONO};font-size:24px;font-weight:700;color:{T6}", hd, ' data-build-in="fade order 2"'))
for i, r in enumerate([("coffee", "4500", "2"), ("latte", "5000", "1"), ("cake", "6500", "3")]):
    y = 712 + i * 64
    o.append(f'<div data-build-in="rise order {i + 2}" style="position:absolute;left:96px;top:{y}px;display:flex;flex-direction:row;gap:20px;align-items:center">'
             + p(f"width:240px;flex:none;font-size:24px;font-weight:700;color:{INK}", f"{i + 1}번째 · orders[{i}]")
             + "".join(p(f"width:280px;height:54px;border-radius:12px;border:3px solid {LINE};background:{CARD};font-family:{MONO};font-size:26px;font-weight:700;line-height:48px;text-align:center;color:{INK}", e(v)) for v in r) + '</div>')
W("for-orders", o, "orders 장에서 본 꺼내 담기를 for에 그대로 써요. for 다음에 이름 세 개를 쉼표로 적으면, 한 번 돌 때마다 주문 튜플 하나가 menu, price, qty에 나눠 들어가요. 첫 번째에는 coffee, 4500, 2가, 두 번째에는 latte, 5000, 1이 들어가요. 오른쪽은 for 없이 같은 일을 하는 코드예요. 주문 수만큼 두 줄씩 늘어나는데, for로 쓰면 주문이 몇 건이든 두 줄이면 돼요. 출력은 실제로 실행한 결과예요.")

o = [sec("for-total")] + head(EB6S, "되풀이하면서 합계를 쌓아요", T6)
o += cell({"id": "c-ft", "lines": ["total = 0", "for menu, price, qty in orders:", "    total += price * qty", "    print(menu, total)", 'print("합계:", total)'], "n": 22,
           "out": ["coffee 9000", "latte 14000", "cake 33500", "합계: 33500"]}, 96, 210, 860, sel="c-ft")
for j, hd in enumerate(["", "price * qty", "total"]):
    o.append(p(f"position:absolute;left:{1010 + [0, 260, 560][j]}px;top:210px;width:260px;font-family:{MONO};font-size:24px;font-weight:700;color:{T6}", e(hd), ' data-build-in="fade order 1"'))
tr6 = [("시작", "", "0"), ("1번째 coffee", "4500 * 2 = 9000", "9000"), ("2번째 latte", "5000 * 1 = 5000", "14000"), ("3번째 cake", "6500 * 3 = 19500", "33500")]
for i, (a_, b_, c_) in enumerate(tr6):
    y = 256 + i * 112
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:1010px;top:{y}px;width:814px;height:96px;background:{CARD};border:2px solid {LINE};border-radius:16px;padding:0 20px;display:flex;flex-direction:row;align-items:center">'
             + p(f"width:240px;flex:none;font-size:24px;font-weight:700;color:{INK}", e(a_))
             + p(f"width:300px;flex:none;font-family:{MONO};font-size:22px;color:{SUB}", e(b_))
             + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:{T6}", e(c_)) + '</div>')
o.append(caption("total = 0 은 for 앞에서 한 번만, total += 는 안쪽에서 매번 실행돼요.", 920))
W("for-total", o, "합계를 구할 땐 for 앞에서 total을 0으로 시작해요. for 안쪽에서는 12의 3파트의 += 로 가격 곱하기 수량을 더해요. 한 번 돌 때마다 total이 9000, 14000, 33500으로 쌓여요. 들여 쓴 두 줄은 매번 실행되고, 들여 쓰지 않은 마지막 print는 for가 끝난 뒤 한 번만 실행돼서 합계를 찍어요. total = 0을 for 안에 넣으면 매번 0으로 돌아가서 합계가 쌓이지 않아요. 출력은 실제로 실행한 결과예요.")

o = [sec("for-receipt")] + head(EB6S, "for 로 영수증 한 장을 완성해요", T6)
o += cell({"id": "c-fr", "lines": ['print("=" * 33)', 'print(f"{\'KANT 카페\':^31}")', 'print(f"{\'2026-11-02  14:30\':^33}")', 'print("=" * 33)', 'print(f"{\'메뉴명\':<7}{\'단가\':>6}{\'수량\':>3}{\'금액\':>8}")', 'print("-" * 33)', 'total = 0', 'count = 0', 'for menu, price, qty in orders:', '    print(f"{menu:<10}{price:>8,}{qty:>5}{price * qty:>10,}")', '    total += price * qty', '    count += qty', 'print("-" * 33)', 'print(f"{\'수량\':<6}{count:>15}")', 'print(f"{\'합계\':<6}{total:>25,}")', 'print("=" * 33)', 'print(f"{\'감사합니다\':^28}")'], "n": 23}, 96, 190, 1080, sel="c-fr")
RC_OUT = ['=================================', '            KANT 카페', '        2026-11-02  14:30', '=================================', '메뉴명        단가 수량      금액', '---------------------------------', 'coffee       4,500    2     9,000', 'latte        5,000    1     5,000', 'cake         6,500    3    19,500', '---------------------------------', '수량                  6', '합계                       33,500', '=================================', '           감사합니다']
o.append(f'<div data-build-in="rise order 1" style="position:absolute;left:1230px;top:190px;width:594px;background:#FFFFFF;border:2px solid {LINE};border-radius:6px;box-shadow:0 12px 30px rgba(29,35,48,0.12);padding:30px 34px">'
         + p(f"font-size:20px;font-weight:700;color:{GRAY};margin-bottom:12px", "실행 결과")
         + "".join(p(f"font-family:{MONO};font-size:26px;line-height:1.45;white-space:pre;color:{INK}", WIDE(e(l))) for l in RC_OUT) + '</div>')
o.append(caption("한 셀을 실행하면 영수증 한 장이 나와요. 주문이 늘어도 코드는 그대로예요.", 940))
W("for-receipt", o, "지금까지 배운 걸 모아 영수증 한 장을 찍어요. 맨 위는 = 줄 사이에 가게 이름과 날짜를 가운데 맞춤으로 넣었어요. KANT 카페는 한글이 두 글자라 33칸에서 2를 뺀 31칸으로 가운데 맞춤했어요. 머리글과 - 줄은 for 앞에서 한 번 찍어요. for 안에서는 주문 줄을 찍고, 합계 total과 전체 수량 count를 쌓아요. for가 끝나면 - 줄, 수량, 합계, = 줄을 찍고, 마지막에 감사합니다를 가운데에 넣어요. 감사합니다는 다섯 글자라 33에서 5를 뺀 28칸이에요. 날짜는 예시로 적은 글자예요. 오른쪽은 이 셀을 실제로 실행한 결과를 영수증 모양 상자에 옮긴 거예요.")

o = [sec("for-err")] + head(EB6S, "for 는 콜론과 들여쓰기를 꼭 지켜요", T6)
fe = [(["for menu in menus", "    print(menu)"], "SyntaxError: expected ':'", "for 줄 끝에 콜론을 빠뜨렸어요", 24),
      (["for menu in menus:", "print(menu)"], "IndentationError: expected an indented block after 'for' statement on line 1", "되풀이할 줄을 들여 쓰지 않았어요", 25)]
for i, (lines, err, why, n_) in enumerate(fe):
    y = 210 + i * 300
    o += cell({"id": f"c-fe{i}", "lines": lines, "n": n_, "out": [err], "err": True}, 96, y, 1340, attrs=f' data-build-in="rise order {i + 1}"')
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:1480px;top:{y}px;width:344px;height:200px;background:{CARD};border:2px solid {LINE};border-left:12px solid {T6};border-radius:16px;padding:0 24px;display:flex;flex-direction:column;justify-content:center;gap:6px">'
             + p(f"font-size:25px;font-weight:700;color:{INK}", e(why)) + '</div>')
o.append(card(96, 800, 1728, 110, '<div style="display:flex;flex-direction:row;align-items:center;gap:24px">' + kbd("Tab", 26) + p(f"font-size:26px;color:{INK}", "VS Code에서 콜론 뒤 Enter를 치면 네 칸이 자동으로 들어가요. 직접 넣을 땐 Tab 한 번이에요.") + '</div>',
              None, ' data-build-in="rise order 3"', "justify-content:center"))
W("for-err", o, "for에서 처음에 자주 나는 오류 두 가지예요. for 줄 끝의 콜론을 빠뜨리면 SyntaxError: expected ':'가 나요. 되풀이할 줄을 들여 쓰지 않으면 IndentationError가 나요. 파이썬은 들여쓰기로 어디까지가 for 안쪽인지 알아봐요. VS Code 노트북에서는 콜론 뒤에 Enter를 치면 다음 줄이 네 칸 들어간 채로 시작해요. 오류 메시지 뒤의 괄호 안 위치 표시는 빼고 옮겼어요. 실제로 실행한 결과예요.")

o = [sec("list-shapes")] + head(EB6S, "리스트에는 여러 모양의 값을 담아요", T6)
o += cell({"id": "c-ls", "lines": ['names = ["kim", "lee", "park"]', "scores = [90, 100, 7]", 'mixed = ["coffee", 4500, True]', 'carts = [["coffee", "cake"], ["latte"]]', "empty = []",
                                   "print(scores[1])", "print(mixed)", "print(carts[0][1])", "print(len(empty))"], "n": 26,
           "out": ["100", "['coffee', 4500, True]", "cake", "0"]}, 96, 200, 900, sel="c-ls")
ls = [('["kim", "lee"]', "글자 리스트"), ("[90, 100, 7]", "숫자 리스트. sum, max를 쓸 수 있어요"), ('["coffee", 4500, True]', "타입을 섞어도 돼요"),
      ('[["coffee", "cake"], ["latte"]]', "리스트 안의 리스트. 손님별 장바구니"), ('[("coffee", 4500, 2)]', "튜플의 리스트. 앞 장의 orders"), ("[]", "빈 리스트. 나중에 append로 채워요")]
for i, (k, d) in enumerate(ls):
    o.append(card(1040, 200 + i * 118, 784, 106, mono(k, 22, T6, T6BG, "align-self:flex-start") + p(f"font-size:20px;color:{SUB}", e(d)), None, f' data-build-in="rise order {i + 1}"', "justify-content:center;gap:4px;padding:10px 24px"))
o.append(caption("carts[0][1]처럼 안쪽 리스트도 번호를 두 번 써서 꺼내요.", 940))
W("list-shapes", o, "리스트에는 어떤 값이든 담을 수 있어요. 팀 실습의 kim, lee, park 같은 글자도, 점수 같은 숫자도 담아요. 한 리스트에 글자, 숫자, True를 섞어도 돼요. 리스트 안에 리스트를 넣으면 손님별 장바구니처럼 표 모양이 돼요. 이 모양은 14의 2파트에서 2차원 리스트로 자세히 다뤄요. carts[0][1]은 0번 손님 장바구니의 1번 값 cake예요. 앞 장의 orders는 리스트 안에 튜플을 넣은 모양이에요. 빈 대괄호는 빈 리스트라 len()이 0이에요. 출력은 실제로 실행한 결과예요.")

o = [sec("list-err")] + head(EB6S, "없는 번호를 꺼내면 IndexError가 나요", T6)
le = [("menus[3]", "IndexError: list index out of range", "menus는 0, 1, 2번까지", 27),
      ("orders[3]", "IndexError: list index out of range", "주문은 세 건, 마지막은 2번", 28),
      ("orders[0][3]", "IndexError: tuple index out of range", "튜플 안은 0, 1, 2번까지", 29),
      ("order[1] = 5000", "TypeError: 'tuple' object does not support item assignment", "튜플은 바꿀 수 없어요", 12)]
for i, (code, err, why, n_) in enumerate(le):
    y = 200 + i * 172
    o += cell({"id": f"c-le{i}", "lines": [code], "n": n_, "out": [err], "err": True}, 96, y, 1180, attrs=f' data-build-in="rise order {i + 1}"')
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:1320px;top:{y}px;width:504px;height:140px;background:{CARD};border:2px solid {LINE};border-left:12px solid {T6};border-radius:16px;padding:0 24px;display:flex;flex-direction:column;justify-content:center;gap:6px">'
             + p(f"font-size:25px;font-weight:700;color:{INK}", e(why)) + '</div>')
o.append(caption("마지막 번호는 len() - 1이에요. 메시지에 list인지 tuple인지 나와요.", 920))
W("list-err", o, "리스트와 튜플에서 자주 나는 오류예요. 번호는 0부터 세서, 값이 세 개면 마지막 번호는 2예요. menus[3]이나 orders[3]처럼 없는 번호를 쓰면 IndexError가 나요. 메시지의 list는 바깥 리스트에서, tuple은 안쪽 튜플에서 번호가 넘쳤다는 뜻이에요. orders[0][3]은 주문 튜플 안에 3번 값이 없어서 tuple index out of range예요. 마지막 줄은 튜플 장에서 본 오류예요. 튜플은 바꿀 수 없어서 바꿔야 하는 값은 리스트에 담아요. 셀 번호 [5]는 튜플 장의 셀이에요. 출력은 실제로 실행한 결과예요.")

# ---------- summary ----------
EB5 = "정리"
o = [sec("trouble")] + head(EB5, "막히면 오류의 마지막 줄을 봐요", RED)
tr = [("IndexError: list index out of range", "없는 번호를 꺼냈어요", "마지막은 len() - 1"),
      ("TypeError: not enough arguments for format string", "% 자리 수와 값 수가 달라요", "f-string으로"),
      ("ValueError: list.remove(x): x not in list", "리스트에 없는 값을 지우려 했어요", "in 으로 먼저 확인"),
      ("TypeError: 'tuple' object does not support item assignment", "튜플은 담은 뒤 바꿀 수 없어요", "바꿀 값은 리스트로"),
      ("SyntaxError: expected ':'", "for 줄 끝에 콜론이 없어요", "for x in xs:"),
      ("IndentationError: expected an indented block after 'for' statement on line 1", "for 안쪽 줄을 들여 쓰지 않았어요", "네 칸 들여쓰기")]
o.append('<div style="position:absolute;left:96px;top:196px;width:1728px;height:724px;display:flex;flex-direction:column;gap:8px">')
for i, (q, a_, cmd) in enumerate(tr, 1):
    m = "Error" in q
    o.append(f'<div data-build-in="rise order {i}" style="flex:1;display:flex;flex-direction:row;gap:26px;align-items:center;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:8px 30px">'
             + num(i, RED, 32)
             + '<div style="flex:1;display:flex;flex-direction:column;gap:4px">' + p(f"{'font-family:' + MONO + ';font-size:22px;' if m else 'font-size:26px;'}font-weight:700;color:{INK};white-space:nowrap", e(q)) + p(f"font-size:22px;color:{SUB}", e(a_)) + '</div>'
             + p(f"width:300px;flex:none;font-size:24px;font-weight:700;line-height:1.5;color:{INK};background:#EEEFF2;padding:8px 18px;border-radius:12px;white-space:pre", e(cmd)) + '</div>')
o.append('</div>')
o.append(caption("오류가 나면 위쪽 Traceback보다 맨 아래 줄부터 읽어요.", 940))
W("trouble", o, "오류 메시지는 길어도 맨 아래 한 줄에 원인이 있어요. 1번은 리스트나 문자열에서 없는 번호를 꺼냈을 때예요. 값이 세 개면 마지막 번호는 2예요. 2번은 % 포맷팅의 자리 수와 값 수가 다를 때예요. f-string으로 쓰면 이 오류가 없어요. 3번은 remove로 없는 값을 지울 때, 4번은 튜플 값을 바꾸려 할 때예요. 5번과 6번은 for 줄의 콜론과 들여쓰기예요. 오류 메시지 뒤 괄호 안의 위치 표시는 빼고 옮겼어요. 위 출력은 모두 hello-uv 커널에서 실제로 실행한 결과의 마지막 줄이에요.", ("trouble", "정리"))

o = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>']
cheat = [("word[0:2]", "앞에서 두 글자 자르기", T5), ('f"{name} {age}살"', "값을 끼워 넣기", T5), ('f"{price:,}원"', "콤마 찍어 출력", T5), ('f"{pi:.2f}"', "소수점 둘째 자리까지", T5),
         ("prices.append(5000)", "리스트 끝에 하나 더하기", T6), ("orders[1][0]", "리스트 안 튜플에서 꺼내기", T6), ("a, b, c = order", "튜플 값을 나눠 담기", T6), ("for x in xs:", "하나씩 꺼내 되풀이", T6)]
for i, (k, d, c) in enumerate(cheat):
    x, y = 96 + (i % 4) * 438, 200 + (i // 4) * 290
    o.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:414px;height:264px;background:{CARD};border:2px solid {LINE};border-top:10px solid {c};border-radius:20px;padding:28px 28px;display:flex;flex-direction:column;gap:20px">'
             + mono(k, 28, c, "#F6F5F1", "align-self:flex-start") + p(f"font-size:28px;font-weight:700;color:{INK}", d) + '</div>')
o.append(f'<div style="position:absolute;left:96px;top:780px;width:1728px;height:210px;background:{CARD};border:2px solid {LINE};border-radius:20px;padding:24px 36px;display:flex;flex-direction:column;justify-content:center;gap:14px">'
         + p(f"font-size:30px;font-weight:700;color:{INK}", '번호는 0부터 세요. <span style="font-family:\'JetBrains Mono\';color:' + T6 + '">[시작:끝]</span>에서 끝 번호 자리는 빠져요')
         + p(f"font-size:30px;font-weight:700;color:{INK}", '리스트 <span style="font-family:\'JetBrains Mono\';color:' + T6 + '">[ ]</span>는 바꿀 수 있고, 튜플 <span style="font-family:\'JetBrains Mono\';color:' + T6 + '">( )</span>는 바꿀 수 없어요') + '</div>')
W("cheatsheet", o, "이번 챕터에서 쓴 기호와 메서드를 한 장에 모았어요. 번호는 0부터 센다는 것, 새 출력 코드는 f-string으로 적는다는 것만은 꼭 기억해요. 노트북에 이 장의 내용을 마크다운 셀로 정리해 두면 복습할 때 같이 봐요. 다음 14에서는 in과 not in, 리스트 안에 리스트를 넣은 2차원 리스트를 봐요.")

# ---------- toc ----------
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
parts = [("Chat", T5, "문자열과 출력", "인덱스, 슬라이싱, sep, end, %, format(), f-string, 칸 수, 소수점, 콤마", "str-make", "fmt-err"),
         ("Table", T6, "리스트와 튜플", "[ ] 와 ( ), 자르기, 메서드, split과 join, 주문 데이터 orders, 꺼내 담기, 영수증 출력, for", "list-make", "list-err")]
TOC_NOTE = "두 파트는 앞 파트를 그대로 이어서 써요. 1파트는 문자열을 다루고 값을 보기 좋게 출력하는 법이에요. 2파트는 값 여러 개를 리스트와 튜플에 담아 주문 데이터를 영수증으로 찍고, for 문으로 되풀이를 줄여요. 셀은 위에서부터 차례로 실행해요."

DECK_TITLE = "파이썬 기초 2 (문자열, 리스트, for)"
t = [f'<section id="toc" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column;gap:40px">',
     f'<h2 style="font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>',
     f'<div style="display:grid;grid-template-columns:repeat({len(parts)},1fr);gap:18px;flex:1">']
for i, (ic, c, h, s, a, b) in enumerate(parts, 1):
    t.append(f'<div style="display:flex;flex-direction:column;gap:14px;background:#FFFFFF;border:2px solid {LINE};border-top:10px solid {c};border-radius:20px;padding:28px 26px">'
             f'<div style="display:flex;flex-direction:row;gap:16px;align-items:center"><p style="font-size:60px;font-weight:900;line-height:1.25;color:{c}">{i}</p>'
             f'<x-icon name="{ic}" style="width:48px;height:48px;color:{c}"></x-icon></div>'
             f'<h3 style="font-size:28px;font-weight:700;color:{INK}">{h}</h3>'
             f'<p style="font-size:24px;line-height:1.5;color:{SUB}">{e(s)}</p><div style="flex:1"></div>'
             f'<p style="font-size:26px;color:#6A7180">{page[a]}–{page[b]}쪽</p></div>')
t += ['</div>', f'<p style="font-size:26px;color:{SUB}">{page["ready"]}쪽은 노트북 준비, {page["trouble"]}–{page["cheatsheet"]}쪽은 막힐 때와 한 장 요약이에요.</p>']
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(t) + f"\n<aside>{e(TOC_NOTE)}</aside>\n</section>\n")

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-02T03:00:00Z"}, "lists": "css", "title": DECK_TITLE, "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
print(len(ORDER), "slides")
