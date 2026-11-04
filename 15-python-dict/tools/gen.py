"""Generates every slide of the Python basics 4 deck (15, dictionaries) and slides/deck.json.

Story: keeps writing in basics.ipynb from chapters 12-14. Finds values by key instead of by index (lockers),
changes and deletes them, walks a dictionary with for, then mixes dictionaries with lists and reprints
the KANT cafe receipt from chapter 13 with a list of dictionaries.
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
K1, K1BG = "#1E5FA8", "#E5EEF8"
K2, K2BG = "#A0620A", "#F7EEDD"
K3, K3BG = TEAL, "#E2F2F3"
K4, K4BG = "#A23B72", "#F6E7EF"
T6, T6BG = K4, K4BG
EB1 = "1. 만들고 꺼내기"
EB2 = "2. 바꾸고 지우기"
EB3 = "3. 둘러보기"
EB4 = "4. 리스트와 섞기"


def slots(items, left, top, w=170, h=96, hi=(), top_lbl=True, attrs="", fs=34, color=None, bg=None):
    """List items in a row of boxes with index numbers above."""
    c, b = color or T6, bg or T6BG
    o = [f'<div{attrs} style="position:absolute;left:{left}px;top:{top}px;display:flex;flex-direction:row;gap:8px">']
    for i, it in enumerate(items):
        on = i in hi
        o.append('<div style="display:flex;flex-direction:column;align-items:center;gap:8px">'
                 + (p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{c}", str(i)) if top_lbl else "")
                 + p(f"width:{w}px;height:{h}px;border-radius:14px;border:3px solid {c if on else LINE};background:{b if on else CARD};font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:{h - 6}px;text-align:center;color:{INK};white-space:pre", e(it)) + '</div>')
    o.append('</div>')
    return "".join(o)


def grid(rows, left=0, top=0, cw=150, ch=84, hi=(), attrs="", fs=32, lbl=24, cols=None, color=T6, inline=False, bg=None):
    """A list of lists drawn as a table: row numbers on the left, column numbers on top.
    hi: set of (row, col) cells to highlight. cols: optional names under the column numbers."""
    pos = "" if inline else f"position:absolute;left:{left}px;top:{top}px;"
    rw = lbl * 2 + 12
    o = [f'<div{attrs} style="{pos}display:flex;flex-direction:column;gap:6px">']
    head_ = f'<div style="width:{rw}px;flex:none"></div>' + "".join(
        p(f"width:{cw}px;flex:none;text-align:center;font-family:{MONO};font-size:{lbl}px;font-weight:700;color:{color};line-height:1.2", str(j) + (f'<br><span style="font-family:{SANS};font-size:{lbl - 4}px;color:{GRAY}">{e(cols[j])}</span>' if cols else ""))
        for j in range(len(rows[0])))
    o.append(f'<div style="display:flex;flex-direction:row;gap:6px">{head_}</div>')
    for i, r in enumerate(rows):
        cells = "".join(p(f"width:{cw}px;height:{ch}px;flex:none;border-radius:10px;border:3px solid {color if (i, j) in hi else LINE};background:{(bg or T6BG) if (i, j) in hi else CARD};"
                          f"font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:{ch - 6}px;text-align:center;color:{INK};white-space:pre", e(str(v))) for j, v in enumerate(r))
        o.append(f'<div style="display:flex;flex-direction:row;gap:6px;align-items:center">' + p(f"width:{rw}px;flex:none;text-align:right;padding-right:8px;font-family:{MONO};font-size:{lbl}px;font-weight:700;color:{color}", str(i)) + cells + '</div>')
    o.append('</div>')
    return "".join(o)


def row_card(left, top, w, h, code, res, desc, start, color, bg, code_w=380):
    """One line: code, its result, and what it means."""
    return (f'<div data-build-in="rise order {start}" style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:{CARD};border:2px solid {LINE};border-radius:16px;padding:0 22px;display:flex;flex-direction:row;align-items:center;gap:18px">'
            + f'<div style="width:{code_w}px;flex:none">' + mono(code, 24, color, bg, "display:inline-block") + '</div>'
            + (tf(res, 24) if res in ("True", "False") else p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{INK};white-space:pre", e(res)))
            + p(f"flex:1;font-size:21px;color:{SUB}", e(desc)) + '</div>')




def lockers(pairs, left=0, top=0, w=200, h=170, color=K1, bg=K1BG, hi=(), attrs="", fs=34, kfs=24, gap=12, inline=False, mode=None):
    """A dictionary drawn as a row of lockers: the key is written on the door band, the value sits inside.
    mode "key" or "val" dims the other half (for keys() and values())."""
    pos = "" if inline else f"position:absolute;left:{left}px;top:{top}px;"
    o = [f'<div{attrs} style="{pos}display:flex;flex-direction:row;gap:{gap}px">']
    for i, (k, v) in enumerate(pairs):
        on = i in hi or mode is not None
        kc = color if (on and mode != "val") else "#ECEAE3"
        kt = "#FFFFFF" if (on and mode != "val") else (GRAY if mode == "val" else INK)
        vt = "#B4B9C3" if mode == "key" else INK
        o.append(f'<div style="width:{w}px;height:{h}px;flex:none;border-radius:14px;border:3px solid {color if on else "#C9CED8"};background:{bg if (on and mode != "key") else CARD};display:flex;flex-direction:column;overflow:hidden">'
                 + p(f"height:{kfs + 26}px;flex:none;background:{kc};color:{kt};font-family:{MONO};font-size:{kfs}px;font-weight:700;line-height:{kfs + 26}px;text-align:center;white-space:pre", e(k))
                 + '<div style="flex:1;display:flex;align-items:center;justify-content:center;position:relative">'
                 + p(f"font-family:{MONO};font-size:{fs}px;font-weight:700;color:{vt};white-space:pre", e(v))
                 + f'<div style="position:absolute;right:10px;top:50%;width:7px;height:34px;margin-top:-17px;border-radius:4px;background:#D5D8DE"></div></div></div>')
    o.append('</div>')
    return "".join(o)


def label(text, left, top, color, attrs="", w=700, size=26):
    return p(f"position:absolute;left:{left}px;top:{top}px;width:{w}px;font-family:{MONO};font-size:{size}px;font-weight:700;color:{color}", e(text), attrs)


MENU = 'menu = {"coffee": 4500, "latte": 5000, "cake": 6500}'
M0 = [('"coffee"', "4500"), ('"latte"', "5000"), ('"cake"', "6500")]

# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#F2B27A;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
       '<h1 style="font-size:92px;font-weight:900;line-height:1.1;color:#F6F5F1">파이썬 기초 4<br>딕셔너리</h1>',
       '<p style="font-size:40px;line-height:1.4;color:#BFC6D4">번호 대신 키로<br>값을 찾고 바꾸기</p>']
cov.append(f'<div style="position:absolute;left:1060px;top:300px;width:720px;height:480px;background:#252B36;border-radius:24px;padding:44px 48px;display:flex;flex-direction:column;justify-content:center;gap:34px">')
for code, out_, c in [('menu["latte"]', '5000', '#9DBDEB'), ('menu.get("tea", 0)', '0', '#9DBDEB'), ('"tea" in menu', 'False', '#E3B877'), ('len(menu)', '3', '#8FD8DE')]:
    cov.append('<div style="display:flex;flex-direction:row;align-items:center;gap:28px">'
               + p(f"width:420px;flex:none;font-family:{MONO};font-size:36px;font-weight:700;color:{c};white-space:pre", e(code))
               + f'<x-shape kind="arrow-right" style="width:50px;height:30px;background:#5A6172"></x-shape>'
               + p(f"font-family:{MONO};font-size:36px;font-weight:700;color:#E6E9EF", e(out_)) + '</div>')
cov.append('</div>')
W("cover", cov, "13에서 리스트와 튜플에 주문을 담고, 14에서 in과 2차원 리스트를 봤어요. 이번 챕터는 번호 대신 이름(키)으로 값을 찾는 딕셔너리예요. 1파트는 만들고 꺼내기, 2파트는 바꾸고 지우기, 3파트는 for로 둘러보기, 4파트는 리스트와 섞어서 13의 영수증을 다시 찍어요. 모든 예제는 12~14에서 쓰던 노트북 셀에 이어서 적고 실행해요.", ("intro", "들어가기"))

ORDER.append("toc")   # written last, after page numbers are known

# ---------- ready ----------
o = [sec("ready")] + head("들어가기", "14에서 이어서 해요", JP)
done = [("hello-uv 노트북, 커널 .venv", "09 · 25–27쪽"), ("f-string, 칸 수와 콤마", "13 · 1파트"), ("리스트, 튜플, for와 꺼내 담기", "13 · 2파트"), ("in과 not in, 2차원 리스트", "14")]
for i, (a_, b_) in enumerate(done):
    y = 210 + i * 130
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:96px;top:{y}px;width:820px;height:112px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:0 28px;display:flex;flex-direction:row;gap:22px;align-items:center">'
             + f'<x-icon name="CheckCircle" style="width:48px;height:48px;color:{GR}"></x-icon>'
             + p(f"flex:1;font-size:30px;font-weight:700;color:{INK}", e(a_))
             + p(f"font-size:24px;font-weight:700;color:{GRAY};white-space:nowrap", e(b_)) + '</div>')
o.append(p(f"position:absolute;left:96px;top:750px;width:820px;font-size:26px;line-height:1.5;color:{SUB}", "기억이 안 나면 그 쪽을 먼저 다시 봐요.", ' data-build-in="fade order 4"'))
o.append(f'<div data-build-in="rise order 5" style="position:absolute;left:1000px;top:210px;width:824px;height:560px;background:{CARD};border:2px solid {LINE};border-top:10px solid {JP};border-radius:20px;padding:32px 40px;display:flex;flex-direction:column;gap:30px">'
         + p(f"font-size:32px;font-weight:700;color:{INK}", "노트북 다시 열기")
         + '<div style="display:flex;flex-direction:row;gap:18px;align-items:center">' + num(1, JP, 36) + p(f"font-size:28px;color:{INK}", "VS Code로 hello-uv 폴더 열기") + '</div>'
         + '<div style="display:flex;flex-direction:row;gap:18px;align-items:center">' + num(2, JP, 36) + p(f"font-size:28px;color:{INK}", "탐색기에서") + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{JP}", NB) + p(f"font-size:28px;color:{INK}", "열기") + '</div>'
         + '<div style="display:flex;flex-direction:row;gap:18px;align-items:center">' + num(3, JP, 36) + p(f"font-size:28px;color:{INK}", "오른쪽 위 커널이 .venv인지 보기") + '</div>'
         + '<div style="display:flex;flex-direction:row;gap:18px;align-items:center">' + num(4, JP, 36) + p(f"font-size:28px;color:{INK}", "셀에 적고") + kbd("Shift+Enter", 26) + p(f"font-size:28px;color:{INK}", "로 실행") + '</div></div>')
o.append(caption("이번 챕터의 코드도 모두 노트북 셀에 적어요.", 880))
W("ready", o, "09에서 만든 hello-uv 폴더를 VS Code로 열고, 12~14에서 쓰던 basics.ipynb를 다시 열어요. 13의 f-string과 리스트, 튜플, for, 14의 in을 그대로 써요. 슬라이드의 출력은 tools/demo.sh가 hello-uv 커널에서 같은 셀을 실제로 실행한 결과예요. 셀 번호는 파트마다 [1]부터 다시 셌어요.")

# ---------- part 1: make and read ----------
o = [sec("d-why")] + head(EB1, "번호 대신 키로 찾아요", K1)
o += cell({"id": "c-w1", "lines": ['student = ["kim", 90, 85, 77]', "print(student[2])"], "n": 1, "out": ["85"]}, 96, 200, 840)
o += cell({"id": "c-w2", "lines": ['student = {"name": "kim", "kor": 90,', '           "eng": 85, "math": 77}', 'print(student["eng"])'], "n": 2, "out": ["85"]}, 984, 200, 840, sel="c-w2", attrs=' data-build-in="rise order 2"')
o.append(p(f"position:absolute;left:96px;top:420px;width:840px;font-size:26px;font-weight:700;color:{GRAY}", "리스트 · 칸마다 번호가 있어요", ' data-build-in="fade order 1"'))
o.append(lockers([("0", '"kim"'), ("1", "90"), ("2", "85"), ("3", "77")], 96, 470, 201, 180, GRAY, "#EEEFF2", hi=(2,), attrs=' data-build-in="rise order 1"'))
o.append(p(f"position:absolute;left:984px;top:420px;width:840px;font-size:26px;font-weight:700;color:{K1}", "딕셔너리 · 칸마다 이름(키)이 있어요", ' data-build-in="fade order 2"'))
o.append(lockers([("name", '"kim"'), ("kor", "90"), ("eng", "85"), ("math", "77")], 984, 470, 201, 180, K1, K1BG, hi=(2,), attrs=' data-build-in="rise order 2"'))
o.append(card(96, 690, 840, 180, mono("student[2]", 28, GRAY, "#EEEFF2", "align-self:flex-start") + p(f"font-size:26px;line-height:1.45;color:{INK}", "2번이 영어 점수라는 걸 외워야 해요"), None, ' data-build-in="rise order 1"', "justify-content:center"))
o.append(card(984, 690, 840, 180, mono('student["eng"]', 28, K1, K1BG, "align-self:flex-start") + p(f"font-size:26px;line-height:1.45;color:{INK}", "읽기만 해도 영어 점수인 걸 알아요"), None, ' data-build-in="rise order 2"', "justify-content:center"))
o.append(caption("사물함 문에 적힌 이름이 키(key), 안에 든 것이 값(value)이에요.", 920))
W("d-why", o, "13에서 학생 한 명의 점수를 리스트에 담으면 student[2]처럼 번호로 꺼냈어요. 그런데 2번이 영어라는 건 코드를 쓴 사람이 외워 둬야 해요. 딕셔너리는 사물함처럼 칸마다 문에 이름을 붙여 둬요. 이 이름을 키, 안에 든 것을 값이라고 불러요. student[\"eng\"]는 읽기만 해도 영어 점수라는 걸 알아요. 결과는 둘 다 85예요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요. 출력은 실제로 실행한 결과예요.", ("make", "만들고 꺼내기"))

o = [sec("d-make")] + head(EB1, "중괄호 안에 키: 값을 쉼표로 이어요", K1)
o += cell({"id": "c-m", "lines": [MENU, "print(menu)", "print(type(menu))", "print(len(menu))", "cart = {}", "print(cart)", "print(len(cart))"], "n": 3,
           "out": ["{'coffee': 4500, 'latte': 5000, 'cake': 6500}", "<class 'dict'>", "3", "{}", "0"]}, 96, 200, 960, sel="c-m")
anat = '<div style="display:flex;flex-direction:row;align-items:flex-end;gap:14px">'
for tok, lb in [('"coffee"', "키"), (":", "콜론"), ("4500", "값"), (",", "쉼표")]:
    anat += '<div style="display:flex;flex-direction:column;align-items:center;gap:8px">' + mono(tok, 34, K1, K1BG) + p(f"font-size:22px;font-weight:700;color:{SUB}", lb) + '</div>'
anat += p(f"font-size:24px;line-height:1.4;color:{INK};padding-left:18px;padding-bottom:40px", "키: 값 한 쌍을<br>쉼표로 이어요") + '</div>'
o.append(card(96, 720, 960, 180, anat, None, ' data-build-in="rise order 1"', "justify-content:center"))
o.append(label("menu", 1110, 200, K1, ' data-build-in="fade order 2"'))
o.append(lockers(M0, 1110, 246, 230, 170, K1, K1BG, hi=(0, 1, 2), attrs=' data-build-in="rise order 2"'))
mk = [("cart = {}", "{}", "빈 딕셔너리"), ("type(menu)", "<class 'dict'>", "dictionary(사전)"), ("len(menu)", "3", "키: 값 쌍의 개수")]
for i, (k, r, d) in enumerate(mk):
    o.append(row_card(1110, 460 + i * 112, 714, 96, k, r, d, i + 3, K1, K1BG, 190))
o.append(caption("중괄호 { }는 딕셔너리, 대괄호 [ ]는 리스트예요.", 940))
W("d-make", o, "딕셔너리는 중괄호 안에 키: 값을 적고, 쌍과 쌍 사이를 쉼표로 이어요. menu는 메뉴 이름이 키, 가격이 값이에요. print로 찍으면 적은 순서대로 나와요. type은 dict라고 알려 주는데, dictionary(사전)의 줄임말이에요. 사전에서 단어를 찾으면 뜻이 나오듯 키로 값을 찾아요. len은 쌍의 개수라 3이에요. 빈 중괄호는 빈 딕셔너리예요. 출력은 실제로 실행한 결과예요.")

o = [sec("d-key")] + head(EB1, "대괄호에 키를 넣어 꺼내요", K1)
o += cell({"id": "c-k1", "lines": ['print(menu["latte"])', 'price = menu["cake"]', "print(price * 2)"], "n": 4, "out": ["5000", "13000"]}, 96, 200, 860, sel="c-k1")
o += cell({"id": "c-k2", "lines": ['menu["tea"]'], "n": 5, "out": ["KeyError: 'tea'"], "err": True}, 96, 470, 860, attrs=' data-build-in="rise order 3"')
o.append(card(96, 640, 860, 220, '<div style="display:flex;flex-direction:row;align-items:center;gap:14px">' + f'<x-icon name="Warning" style="width:40px;height:40px;color:{RED}"></x-icon>' + p(f"font-size:28px;font-weight:700;color:{INK}", "KeyError 뒤에는 찾던 키가 나와요") + '</div>'
              + p(f"font-size:24px;line-height:1.5;color:{INK}", "menu에 tea라는 키가 없어요. 키에 오타가 없는지, 그 키를 넣었는지 봐요."), RED, ' data-build-in="rise order 4"'))
o.append(label("menu", 1010, 200, K1, ' data-build-in="fade order 1"'))
o.append(lockers(M0, 1010, 246, 262, 170, K1, K1BG, hi=(1,), attrs=' data-build-in="rise order 1"'))
ky = [('menu["latte"]', "5000", "latte 칸의 값"), ('menu["cake"] * 2', "13000", "꺼낸 값으로 바로 계산"), ('menu["tea"]', "KeyError", "tea라는 키가 없어요")]
for i, (k, r, d) in enumerate(ky):
    o.append(row_card(1010, 460 + i * 116, 814, 100, k, r, d, i + 1, K1, K1BG, 290))
o.append(caption("리스트는 [번호], 딕셔너리는 [키]로 꺼내요.", 920))
W("d-key", o, "딕셔너리에서 값을 꺼낼 때도 대괄호를 써요. 리스트는 대괄호 안에 번호를 넣었지만, 딕셔너리는 키를 넣어요. menu[\"latte\"]는 5000이에요. 꺼낸 값은 보통 숫자라서 변수에 담아 계산할 수 있어요. 없는 키를 꺼내면 KeyError가 나요. 오류 마지막 줄에 찾던 키 'tea'가 함께 나와서 어느 키가 문제인지 알 수 있어요. 출력은 실제로 실행한 결과예요.")

o = [sec("d-get")] + head(EB1, "get은 없는 키에도 오류 없이 답해요", K1)
o += cell({"id": "c-g", "lines": ['print(menu.get("latte"))', 'print(menu.get("tea"))', 'print(menu.get("tea", 0))'], "n": 6, "out": ["5000", "None", "0"]}, 96, 200, 860, sel="c-g")
gt = [('menu.get("latte")', "5000", "있으면 그 값"), ('menu.get("tea")', "None", "없으면 None"), ('menu.get("tea", 0)', "0", "없으면 정해 둔 값")]
for i, (k, r, d) in enumerate(gt):
    o.append(row_card(1010, 200 + i * 116, 814, 100, k, r, d, i + 1, K1, K1BG, 300))
o.append(card(96, 600, 840, 260, mono('menu["tea"]', 28, RED, "#F8E6E6", "align-self:flex-start") + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{RED}", "KeyError: 'tea'")
              + p(f"font-size:24px;line-height:1.45;color:{INK}", "오류가 나서 셀이 거기서 멈춰요"), RED, ' data-build-in="rise order 4"'))
o.append(card(984, 600, 840, 260, mono('menu.get("tea", 0)', 28, GR, "#E6F4EC", "align-self:flex-start") + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{GR}", "0")
              + p(f"font-size:24px;line-height:1.45;color:{INK}", "없으면 0을 돌려주고 다음 줄로 넘어가요"), GR, ' data-build-in="rise order 5"'))
o.append(caption("None은 '값이 없어요'를 뜻하는 파이썬 값이에요.", 920))
W("d-get", o, "get은 대괄호 꺼내기와 비슷하지만, 없는 키를 물어도 오류가 나지 않아요. 키가 있으면 값을 돌려주고, 없으면 None을 돌려줘요. None은 값이 없다는 뜻의 파이썬 값이에요. 괄호 안에 쉼표 뒤로 값을 하나 더 적으면, 키가 없을 때 None 대신 그 값을 돌려줘요. 가격이나 개수처럼 숫자를 다룰 때는 0을 많이 적어요. 키가 꼭 있어야 하는 곳은 대괄호, 없을 수도 있는 곳은 get을 써요. 실제로 쓰는 곳은 3파트 끝에서 봐요. 출력은 실제로 실행한 결과예요.")

o = [sec("d-short")] + head(EB1, "get은 긴 코드를 한 줄로 줄인 거예요", K1)
o += cell({"id": "c-s1", "lines": ['print(menu["cakee"] if "cakee" in menu else 5000)', 'print(menu.get("cakee", 5000))', 'print(menu["cake"] if "cake" in menu else 5000)', 'print(menu.get("cake", 5000))'], "n": 7,
           "out": ["5000", "5000", "6500", "6500"]}, 96, 200, 1100, sel="c-s1")
o.append(card(1240, 200, 584, 336, p(f"font-size:26px;font-weight:700;color:{INK}", "같은 뜻이에요")
              + p(f"font-size:21px;font-weight:700;color:{GRAY}", "참고 · 원래 긴 방법")
              + mono('menu["cakee"] if "cakee" in menu else 5000', 18, GRAY, "#EEEFF2", "align-self:flex-start")
              + p(f"font-size:21px;font-weight:700;color:{K1}", "줄인 방법")
              + mono('menu.get("cakee", 5000)', 24, K1, K1BG, "align-self:flex-start")
              + p(f"font-size:20px;line-height:1.4;color:{SUB}", "if는 나중에 배워요. 지금은 읽기만 해요"), None, ' data-build-in="rise order 1"', "gap:10px;padding:20px 26px"))
o += cell({"id": "c-s2", "lines": ['sale = {"cake": None}', 'print(sale.get("cake", 5000))', 'print(sale.get("cakee", 5000))'], "n": 8, "out": ["None", "5000"]}, 96, 590, 840, attrs=' data-build-in="rise order 2"')
sh = [('sale.get("cake", 5000)', "None", "키는 있어요. 값이 None이어도 그대로 줘요"), ('sale.get("cakee", 5000)', "5000", "키가 없을 때만 기본값을 줘요")]
o.append(card(984, 590, 840, 290, p(f"font-size:26px;font-weight:700;color:{INK}", "기본값은 키가 없을 때만 써요")
              + "".join('<div style="display:flex;flex-direction:row;align-items:center;gap:14px">' + mono(k, 22, K1, K1BG) + p(f"font-family:{MONO};font-size:22px;font-weight:700;color:{INK}", r) + '</div>'
                        + p(f"font-size:21px;color:{SUB};margin-top:-6px", e(d)) for k, r, d in sh), RED, ' data-build-in="rise order 3"', "gap:12px;padding:20px 26px"))
o.append(caption("get은 '키가 있으면 꺼내고, 없으면 기본값'을 한 줄로 줄인 거예요.", 920))
W("d-short", o, "파이썬에는 자주 쓰는 긴 코드를 줄여 둔 메서드가 많아요. get도 그중 하나예요. 원래는 키가 menu에 있는지 in으로 묻고, 있으면 대괄호로 꺼내고, 없으면 5000을 쓰는 코드를 써야 해요. if와 else는 나중에 배우니 지금은 이런 뜻이라고 읽기만 해요. cakee는 오타라 키가 없어서 두 줄 모두 5000, cake는 키가 있어서 두 줄 모두 6500이에요. 주의할 점이 하나 있어요. get의 기본값은 키가 없을 때만 써요. sale처럼 cake 키가 있고 값이 None이면 None이 그대로 나와요. 출력은 실제로 실행한 결과예요.")

# ---------- part 2: change ----------
o = [sec("d-add")] + head(EB2, "없는 키면 추가, 있는 키면 수정이에요", K2)
o += cell({"id": "c-a", "lines": [MENU, 'menu["tea"] = 4000', "print(menu)", 'menu["latte"] = 5500', "print(menu)", "print(len(menu))"], "n": 1,
           "out": ["{'coffee': 4500, 'latte': 5000, 'cake': 6500, 'tea': 4000}", "{'coffee': 4500, 'latte': 5500, 'cake': 6500, 'tea': 4000}", "4"]}, 96, 200, 1100, sel="c-a")
ad = [('menu["tea"] = 4000', "tea 키가 없어서 새 칸이 생겨요"), ('menu["latte"] = 5500', "latte 키가 있어서 값만 바뀌어요")]
for i, (k, d) in enumerate(ad):
    o.append(card(1240, 200 + i * 194, 584, 176, mono(k, 26, K2, K2BG, "align-self:flex-start") + p(f"font-size:24px;line-height:1.45;color:{INK}", e(d)), None, f' data-build-in="rise order {i + 1}"', "justify-content:center"))
o.append(p(f"position:absolute;left:96px;top:610px;width:820px;font-size:26px;font-weight:700;color:{K2}", "tea를 넣은 뒤", ' data-build-in="fade order 1"'))
o.append(lockers([('"coffee"', "4500"), ('"latte"', "5000"), ('"cake"', "6500"), ('"tea"', "4000")], 96, 656, 196, 160, K2, K2BG, hi=(3,), attrs=' data-build-in="rise order 1"'))
o.append(p(f"position:absolute;left:1000px;top:610px;width:820px;font-size:26px;font-weight:700;color:{K2}", "latte를 바꾼 뒤", ' data-build-in="fade order 2"'))
o.append(lockers([('"coffee"', "4500"), ('"latte"', "5500"), ('"cake"', "6500"), ('"tea"', "4000")], 1000, 656, 196, 160, K2, K2BG, hi=(1,), attrs=' data-build-in="rise order 2"'))
o.append(caption("수정은 칸 수를 늘리지 않아요. 그래서 len(menu)는 4예요.", 920))
W("d-add", o, "딕셔너리에 값을 넣는 문법은 하나예요. menu[키] = 값이에요. 키가 없으면 새 칸이 생기고, 키가 이미 있으면 그 칸의 값만 바뀌어요. tea는 없던 키라 맨 뒤에 추가됐어요. latte는 있던 키라 5000이 5500으로 바뀌었어요. 칸은 네 개 그대로라 len은 4예요. 리스트는 append로 더했지만, 딕셔너리는 대괄호에 새 키를 넣으면 돼요. 이 파트도 새 커널이라 menu를 다시 만들고 셀 번호가 [1]부터예요. 출력은 실제로 실행한 결과예요.", ("change", "바꾸고 지우기"))

o = [sec("d-dup")] + head(EB2, "키는 겹치지 않아요. 값은 겹쳐도 돼요", K2)
o += cell({"id": "c-d", "lines": ['dup = {"latte": 5000, "latte": 5500}', "print(dup)", "print(len(dup))", 'score = {"kim": 90, "lee": 90, "park": 90}', "print(score)"], "n": 2,
           "out": ["{'latte': 5500}", "1", "{'kim': 90, 'lee': 90, 'park': 90}"]}, 96, 200, 900, sel="c-d")
ov = ('<div style="display:flex;flex-direction:row;align-items:center;gap:28px">'
      + lockers([('"latte"', "5500")], w=240, h=150, color=K2, bg=K2BG, hi=(0,), inline=True)
      + '<div style="display:flex;flex-direction:column;gap:8px">' + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:#B4B9C3;text-decoration:line-through", "5000")
      + p(f"font-size:24px;line-height:1.45;color:{INK}", "먼저 넣은 5000은<br>5500으로 덮어써요") + '</div></div>')
o.append(card(1050, 200, 774, 330, p(f"font-size:28px;font-weight:700;color:{INK}", "같은 키를 두 번 적으면") + ov, K2, ' data-build-in="rise order 1"'))
o.append(card(1050, 550, 774, 330, p(f"font-size:28px;font-weight:700;color:{INK}", "값이 같아도 키가 다르면 따로 있어요")
              + lockers([('"kim"', "90"), ('"lee"', "90"), ('"park"', "90")], w=220, h=150, color=K2, bg=K2BG, hi=(0, 1, 2), inline=True), GR, ' data-build-in="rise order 2"'))
o.append(card(96, 580, 900, 300, p(f"font-size:28px;font-weight:700;color:{INK}", "키 하나에 값 하나")
              + p(f"font-size:24px;line-height:1.5;color:{INK}", "앞 장의 menu[\"latte\"] = 5500도 같은 일이에요. 키가 이미 있으면 새 칸 대신 그 칸의 값을 바꿔요.")
              + p(f"font-size:22px;color:{SUB}", "사물함 하나에 이름은 하나만 붙일 수 있어요"), None, ' data-build-in="rise order 3"'))
o.append(caption("같은 키를 두 번 적으면 마지막 값만 남아요.", 920))
W("d-dup", o, "딕셔너리의 키는 겹치지 않아요. 처음부터 같은 키를 두 번 적어도 오류는 나지 않고, 마지막에 적은 5500만 남아요. 그래서 len이 1이에요. 앞 장에서 latte를 5500으로 바꾼 것과 같은 일이에요. 값은 겹쳐도 괜찮아요. kim, lee, park이 모두 90점이어도 키가 달라서 칸이 세 개예요. 사물함 이름은 하나씩이지만, 안에 든 물건은 같아도 되는 것과 같아요. 출력은 실제로 실행한 결과예요.")

o = [sec("d-del")] + head(EB2, "del과 pop으로 지워요", K2)
o += cell({"id": "c-x", "lines": ['del menu["tea"]', "print(menu)", 'price = menu.pop("cake")', "print(price)", "print(menu)"], "n": 3,
           "out": ["{'coffee': 4500, 'latte': 5500, 'cake': 6500}", "6500", "{'coffee': 4500, 'latte': 5500}"]}, 96, 200, 900, sel="c-x")
o += cell({"id": "c-x2", "lines": ['del menu["tea"]'], "n": 4, "out": ["KeyError: 'tea'"], "err": True}, 96, 640, 900, attrs=' data-build-in="rise order 4"')
dl = [('del menu["tea"]', "", "키와 값을 같이 지워요"), ('menu.pop("cake")', "6500", "지우면서 값을 돌려줘요"), ("menus.pop(1)", "", "13의 리스트 pop은 번호를 넣어요")]
for i, (k, r, d) in enumerate(dl):
    o.append(row_card(1040, 200 + i * 124, 784, 108, k, r, d, i + 1, K2 if i < 2 else GRAY, K2BG if i < 2 else "#EEEFF2", 270))
o.append(label("남은 menu", 1040, 600, K2, ' data-build-in="fade order 3"'))
o.append(lockers([('"coffee"', "4500"), ('"latte"', "5500")], 1040, 646, 300, 200, K2, K2BG, hi=(0, 1), attrs=' data-build-in="rise order 3"', fs=40))
o.append(caption("없는 키를 지우려고 하면 KeyError가 나요.", 920))
W("d-del", o, "del 뒤에 menu[키]를 적으면 그 키와 값이 함께 사라져요. pop도 지우는데, 지운 값을 돌려줘서 변수에 담을 수 있어요. 13에서 리스트의 pop은 번호를 넣었어요. 딕셔너리의 pop은 키를 넣어요. 이미 지운 tea를 한 번 더 지우면 KeyError가 나요. 꺼낼 때와 같은 오류예요. 출력은 실제로 실행한 결과예요.")

o = [sec("d-in")] + head(EB2, "in은 키 쪽만 봐요", K2)
o += cell({"id": "c-i", "lines": ['print("latte" in menu)', 'print("tea" in menu)', 'print("tea" not in menu)', "print(5500 in menu)", "print(len(menu))"], "n": 5,
           "out": ["True", "False", "True", "False", "2"]}, 96, 200, 860, sel="c-i")
o.append(label("menu", 1010, 200, K2, ' data-build-in="fade order 1"'))
o.append(lockers([('"coffee"', "4500"), ('"latte"', "5500")], 1010, 246, 300, 150, K2, K2BG, hi=(0, 1), attrs=' data-build-in="rise order 1"', mode="key"))
inn = [('"latte" in menu', "True", "latte 키가 있어요"), ('"tea" not in menu', "True", "tea는 앞에서 지웠어요"), ("5500 in menu", "False", "5500은 값이라 안 봐요"), ("len(menu)", "2", "남은 쌍의 개수")]
for i, (k, r, d) in enumerate(inn):
    o.append(row_card(1010, 436 + i * 104, 814, 90, k, r, d, i + 1, K2, K2BG, 290))
o.append(card(96, 660, 860, 210, p(f"font-size:28px;font-weight:700;color:{INK}", "값이 있는지 물으려면")
              + mono("5500 in menu.values()", 26, K3, K3BG, "align-self:flex-start") + p(f"font-size:22px;color:{SUB}", "values()는 3파트에서 봐요"), K3, ' data-build-in="rise order 5"'))
o.append(caption("14에서 배운 in 그대로예요. 딕셔너리에서는 키만 찾아요.", 920))
W("d-in", o, "14에서 in은 들어 있는지 True, False로 답한다고 했어요. 딕셔너리에 in을 쓰면 키 쪽만 찾아요. latte는 키라 True고, tea는 앞에서 지워서 False예요. not in도 그대로 써요. 5500은 latte의 값이지만 키가 아니라서 False예요. 값에서 찾고 싶으면 3파트에서 볼 menu.values()에 in을 써요. 나중에 배울 if와 함께 쓰면 키가 있을 때만 꺼내는 코드를 만들어요. 출력은 실제로 실행한 결과예요.")

# ---------- part 3: browse ----------
o = [sec("d-views")] + head(EB3, "keys, values, items로 모아 봐요", K3)
o += cell({"id": "c-v", "lines": [MENU, "print(menu.keys())", "print(menu.values())", "print(menu.items())", "print(list(menu.keys()))"], "n": 1,
           "out": ["dict_keys(['coffee', 'latte', 'cake'])", "dict_values([4500, 5000, 6500])", "dict_items([('coffee', 4500), ('latte', 5000), ('cake', 6500)])", "['coffee', 'latte', 'cake']"]}, 96, 200, 1180, sel="c-v")
o.append(card(1320, 200, 504, 374, p(f"font-size:28px;font-weight:700;color:{INK}", "리스트가 필요하면")
              + mono("list(menu.keys())", 26, K3, K3BG, "align-self:flex-start") + p(f"font-size:24px;line-height:1.5;color:{INK}", "13의 list()로 감싸면 보통 리스트가 돼요. 다음 장에서 번호로 꺼내 봐요"), K3, ' data-build-in="rise order 4"'))
vw = [("menu.keys()", "키만", "key"), ("menu.values()", "값만", "val"), ("menu.items()", "(키, 값) 쌍", None)]
for i, (k, d, md) in enumerate(vw):
    o.append(card(96 + i * 584, 620, 560, 270, '<div style="display:flex;flex-direction:row;align-items:center;gap:16px">' + mono(k, 26, K3, K3BG) + p(f"font-size:26px;font-weight:700;color:{INK}", d) + '</div>'
                  + lockers(M0, w=152, h=130, color=K3, bg=K3BG, hi=(0, 1, 2), inline=True, fs=28, kfs=20, mode=md), None, f' data-build-in="rise order {i + 1}"', "padding:20px 24px"))
o.append(caption("items()는 (키, 값) 튜플을 하나씩 담아요.", 920))
W("d-views", o, "딕셔너리에서 키만, 값만, 쌍을 따로 모아 볼 수 있어요. keys는 키만, values는 값만 모아요. items는 키와 값을 튜플 하나로 묶어서 모아요. 출력의 dict_keys, dict_values, dict_items는 딕셔너리에서 꺼내 보여 주는 모양이라는 뜻이에요. 보통 리스트가 필요하면 13에서 배운 list()로 감싸요. 이 파트도 새 커널이라 menu를 다시 만들어요. 출력은 실제로 실행한 결과예요.", ("browse", "둘러보기"))

o = [sec("d-list")] + head(EB3, "list()로 바꾸면 번호로 꺼낼 수 있어요", K3)
o += cell({"id": "c-n", "lines": ["keys = list(menu.keys())", "print(keys)", "print(keys[0])", "print(list(menu.values())[-1])", "pair = list(menu.items())[1]", "print(pair)", "print(pair[0], pair[1])"], "n": 2,
           "out": ["['coffee', 'latte', 'cake']", "coffee", "6500", "('latte', 5000)", "latte 5000"]}, 96, 200, 860, sel="c-n")
o += cell({"id": "c-n2", "lines": ["menu.keys()[0]"], "n": 3, "out": ["TypeError: 'dict_keys' object is not subscriptable"], "err": True}, 96, 724, 860, attrs=' data-build-in="rise order 5"')
ln = [("list(menu.keys())[0]", "coffee", "키 0번"), ("list(menu.values())[-1]", "6500", "값 맨 뒤"), ("list(menu.items())[1]", "('latte', 5000)", "1번 쌍")]
for i, (k, r, d) in enumerate(ln):
    o.append(row_card(1000, 200 + i * 120, 824, 104, k, r, d, i + 1, K3, K3BG, 380))
o.append(card(1000, 572, 824, 124, '<div style="display:flex;flex-direction:row;align-items:center;gap:16px">' + mono("pair[0], pair[1]", 24, K3, K3BG) + p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{INK}", "latte 5000")
              + p(f"font-size:22px;color:{SUB}", "튜플도 번호로 꺼내요") + '</div>', None, ' data-build-in="rise order 4"', "justify-content:center;padding:14px 22px"))
o.append(card(1000, 716, 824, 150, '<div style="display:flex;flex-direction:row;align-items:center;gap:14px">' + f'<x-icon name="Warning" style="width:36px;height:36px;color:{RED}"></x-icon>' + p(f"font-size:26px;font-weight:700;color:{INK}", "keys()는 리스트가 아니에요") + '</div>'
              + p(f"font-size:23px;line-height:1.45;color:{INK}", "번호로 꺼내려면 list()로 먼저 바꿔요"), RED, ' data-build-in="rise order 5"', "padding:18px 26px;gap:8px"))
o.append(caption("번호가 꼭 필요할 때만 list()로 바꿔요. 보통은 키로 꺼내요.", 930))
W("d-list", o, "keys, values, items로 모은 것은 보여 주기용 모양이라 번호로 꺼낼 수 없어요. menu.keys()[0]처럼 바로 번호를 붙이면 TypeError가 나요. 13에서 배운 list()로 감싸면 보통 리스트가 돼서 [0], [-1]처럼 번호로 꺼내요. items()를 리스트로 바꾸면 값 하나하나가 (키, 값) 튜플이에요. 그래서 [1]로 꺼낸 pair에 다시 [0], [1]을 붙이면 키와 값이 나와요. 첫 번째 메뉴처럼 순서가 필요할 때 쓰고, 보통은 menu[\"latte\"]처럼 키로 꺼내요. 출력은 실제로 실행한 결과예요.")

o = [sec("d-for")] + head(EB3, "for로 한 쌍씩 꺼내요", K3)
o += cell({"id": "c-f1", "lines": ["for name in menu:", "    print(name)"], "n": 4, "out": ["coffee", "latte", "cake"]}, 96, 200, 700)
o += cell({"id": "c-f2", "lines": ["for name, price in menu.items():", '    print(f"{name:<8}{price:>6,}원")'], "n": 5, "out": ["coffee   4,500원", "latte    5,000원", "cake     6,500원"], "wide": True},
          860, 200, 964, sel="c-f2", attrs=' data-build-in="rise order 1"')
for i, (k, v, outl) in enumerate([("coffee", 4500, "coffee   4,500원"), ("latte", 5000, "latte    5,000원"), ("cake", 6500, "cake     6,500원")]):
    y = 480 + i * 128
    o.append(f'<div data-build-in="rise order {i + 2}" style="position:absolute;left:96px;top:{y}px;width:1728px;height:112px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:0 28px;display:flex;flex-direction:row;align-items:center;gap:24px">'
             + p(f"width:110px;flex:none;font-size:26px;font-weight:700;color:{K3}", f"{i + 1}번째") + mono(f'("{k}", {v})', 26, K3, K3BG)
             + f'<x-shape kind="arrow-right" style="width:44px;height:26px;flex:none;background:#C9CED8"></x-shape>'
             + mono(f'name = "{k}"', 26) + mono(f"price = {v}", 26)
             + f'<x-shape kind="arrow-right" style="width:44px;height:26px;flex:none;background:#C9CED8"></x-shape>'
             + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{INK};white-space:pre", WIDE(e(outl))) + '</div>')
o.append(caption("for 뒤에 변수를 두 개 적으면 쌍을 나눠 담아요. 13의 꺼내 담기와 같아요.", 920))
W("d-for", o, "딕셔너리를 for에 그대로 넣으면 키만 하나씩 나와요. 키와 값을 같이 쓰려면 items()를 넣어요. items()의 값 하나는 (키, 값) 튜플이라서, for 뒤에 변수를 두 개 적으면 name과 price에 나눠 담겨요. 13에서 for menu, price, qty in orders:로 튜플을 나눠 담은 것과 같은 모양이에요. 출력의 칸 맞추기와 콤마는 13의 1파트 f-string이에요. 출력은 실제로 실행한 결과예요.")

o = [sec("d-calc")] + head(EB3, "values()에도 sum, max, in을 써요", K3)
o += cell({"id": "c-c", "lines": ["print(sum(menu.values()))", "print(max(menu.values()))", "print(5000 in menu.values())", "print(sorted(menu))"], "n": 6,
           "out": ["16000", "6500", "True", "['cake', 'coffee', 'latte']"]}, 96, 200, 860, sel="c-c")
cc = [("sum(menu.values())", "16000", "값을 모두 더해요"), ("max(menu.values())", "6500", "가장 큰 값"), ("5000 in menu.values()", "True", "값 쪽에서 찾아요")]
for i, (k, r, d) in enumerate(cc):
    o.append(row_card(1010, 200 + i * 116, 814, 100, k, r, d, i + 1, K3, K3BG, 360))
o.append(card(96, 600, 860, 270, mono("sorted(menu)", 28, K3, K3BG, "align-self:flex-start") + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{INK}", e("['cake', 'coffee', 'latte']"))
              + p(f"font-size:24px;line-height:1.45;color:{INK}", "딕셔너리를 그대로 넣으면 키만 abc 순으로 정렬해 리스트로 줘요"), K3, ' data-build-in="rise order 4"'))
o.append(card(1010, 600, 814, 270, p(f"font-size:28px;font-weight:700;color:{INK}", "13에서 리스트에 쓴 함수 그대로")
              + p(f"font-size:24px;line-height:1.5;color:{INK}", "max, min, sorted는 keys()에도 써요. sum은 숫자가 담긴 values()에 써요."), None, ' data-build-in="rise order 5"'))
o.append(caption("값으로 계산할 때는 values()를 꺼내서 써요.", 920))
W("d-calc", o, "values()로 모은 값에는 13에서 리스트에 쓴 sum, max를 그대로 써요. 메뉴 가격을 모두 더하면 16000, 가장 비싼 값은 6500이에요. 2파트에서 in은 키만 본다고 했어요. 값에서 찾으려면 values()에 in을 써요. sorted에 딕셔너리를 그대로 넣으면 키만 abc 순으로 정렬한 리스트가 나와요. 딕셔너리 자체는 바뀌지 않아요. 출력은 실제로 실행한 결과예요.")

o = [sec("d-getuse")] + head(EB3, "get은 없을 수도 있는 키에 써요", K3)
o += cell({"id": "c-u1", "lines": ['settings = {"name": "kim"}', 'print(settings.get("name", "guest"))', 'print(settings.get("lang", "ko"))', 'print(settings.get("theme", "light"))', "print(settings)"], "n": 7,
           "out": ["kim", "ko", "light", "{'name': 'kim'}"]}, 96, 200, 840)
o += cell({"id": "c-u2", "lines": ['cart = {"coffee": 2, "tea": 1}', "total = 0", "for name, qty in cart.items():", "    price = menu.get(name, 0)", "    print(name, qty, price * qty)", "    total += price * qty", 'print("합계:", total)'], "n": 8,
           "out": ["coffee 2 9000", "tea 1 0", "합계: 9000"]}, 984, 200, 840, sel="c-u2", attrs=' data-build-in="rise order 2"')
o.append(card(96, 640, 840, 230, p(f"font-size:26px;font-weight:700;color:{INK}", "1. 넣지 않은 설정은 기본값으로")
              + mono('settings.get("lang", "ko")', 24, K3, K3BG, "align-self:flex-start") + p(f"font-size:23px;line-height:1.45;color:{INK}", "lang을 적지 않았으면 ko를 써요. settings는 그대로예요"), K3, ' data-build-in="rise order 1"'))
o.append(card(984, 660, 840, 210, p(f"font-size:26px;font-weight:700;color:{INK}", "2. 메뉴판에 없는 주문은 0원으로")
              + mono("menu.get(name, 0)", 24, K3, K3BG, "align-self:flex-start") + p(f"font-size:23px;line-height:1.45;color:{INK}", "menu[name]이었다면 tea에서 KeyError로 멈춰요"), K3, ' data-build-in="rise order 3"'))
o.append(caption("키가 꼭 있으면 대괄호, 없을 수도 있으면 get으로 꺼내요.", 920))
W("d-getuse", o, "1파트에서 본 get을 실제로 쓰는 곳이에요. 첫째는 설정값이에요. 사용자가 이름만 적고 언어와 테마는 적지 않았으면, get의 두 번째 값으로 정해 둔 기본값을 써요. get은 꺼내기만 해서 settings는 바뀌지 않아요. 둘째는 장바구니예요. 메뉴판에 없는 tea가 들어와도 menu.get(name, 0)은 0을 줘서 for가 끝까지 돌아요. menu[name]으로 꺼냈다면 tea에서 KeyError가 나고 셀이 멈춰요. 출력은 실제로 실행한 결과예요.")

o = [sec("d-count")] + head(EB3, "get으로 개수를 세요", K3)
o += cell({"id": "c-q1", "lines": ['words = "coffee latte coffee cake coffee latte".split()', "count = {}", "for w in words:", "    count[w] = count.get(w, 0) + 1", "print(count)", 'print(count["coffee"])'], "n": 9,
           "out": ["{'coffee': 3, 'latte': 2, 'cake': 1}", "3"]}, 96, 200, 1000, sel="c-q1")
o += cell({"id": "c-q2", "lines": ["votes = {}", 'votes["coffee"] = votes["coffee"] + 1'], "n": 10, "out": ["KeyError: 'coffee'"], "err": True}, 96, 590, 1000, attrs=' data-build-in="rise order 5"')
o.append(card(96, 756, 1000, 140, p(f"font-size:24px;line-height:1.45;color:{INK}", "대괄호로 꺼내면 처음 나온 키에서 멈춰요. 처음엔 아무 키도 없어서예요.")
              + '<div data-build-in="rise order 6" style="display:flex;flex-direction:row;align-items:center;gap:14px">'
              + p(f"font-size:20px;font-weight:700;color:{GRAY};white-space:nowrap", "참고 · 길게 쓰면")
              + mono("count[w] = (count[w] if w in count else 0) + 1", 18, GRAY, "#EEEFF2")
              + p(f"font-size:18px;color:{SUB};white-space:nowrap", "if는 나중에 배워요. 읽기만 해요") + '</div>', RED, ' data-build-in="rise order 5"', "justify-content:center;gap:8px;padding:12px 26px"))
hd = [("w", 170), ("count.get(w, 0)", 250), ("넣는 값", 150)]
o.append(f'<div data-build-in="fade order 1" style="position:absolute;left:1150px;top:200px;width:674px;height:50px;display:flex;flex-direction:row;align-items:center;padding:0 22px;gap:14px">'
         + "".join(p(f"width:{w_}px;flex:none;font-family:{MONO};font-size:20px;font-weight:700;color:{GRAY}", e(t)) for t, w_ in hd) + '</div>')
steps = [("coffee", 0), ("latte", 0), ("coffee", 1), ("cake", 0), ("coffee", 2), ("latte", 1)]
for i, (w_, g) in enumerate(steps):
    o.append(f'<div data-build-in="rise order {i // 2 + 1}" style="position:absolute;left:1150px;top:{254 + i * 68}px;width:674px;height:60px;background:{CARD};border:2px solid {LINE};border-radius:12px;padding:0 22px;display:flex;flex-direction:row;align-items:center;gap:14px">'
             + "".join(p(f"width:{w2}px;flex:none;font-family:{MONO};font-size:24px;font-weight:700;color:{c};white-space:pre", e(t)) for t, w2, c in ((f'"{w_}"', 170, INK), (str(g), 250, GRAY if g == 0 else INK), (f"{g} + 1 = {g + 1}", 150, K3))) + '</div>')
o.append(lockers([('"coffee"', "3"), ('"latte"', "2"), ('"cake"', "1")], 1150, 676, 210, 130, K3, K3BG, hi=(0, 1, 2), attrs=' data-build-in="rise order 4"', fs=40))
o.append(caption("처음 보는 키는 get이 0을 줘서 0 + 1 = 1부터 세요.", 920))
W("d-count", o, "주문이나 단어가 몇 번 나왔는지 세는 것도 get을 쓰는 대표적인 곳이에요. 빈 딕셔너리 count에서 시작해요. for로 단어를 하나씩 꺼내서 count.get(w, 0) + 1을 다시 그 키에 넣어요. 처음 나온 단어는 키가 없어서 get이 0을 주고, 1이 들어가요. 두 번째부터는 지금까지 센 값에 1을 더해요. 2파트에서 본 것처럼 없는 키면 추가, 있는 키면 수정이라 한 줄로 둘 다 돼요. 대괄호로 꺼내면 처음 나온 키에서 KeyError가 나요. 빨간 칸 아래 참고 줄은 get이 줄여 준 원래 코드예요. 키가 있으면 그 값, 없으면 0에 1을 더해요. if는 나중에 배우니 읽기만 해요. 출력은 실제로 실행한 결과예요.")

# ---------- part 4: mix with lists ----------
o = [sec("x-listval")] + head(EB4, "값에 리스트를 넣을 수 있어요", K4)
o += cell({"id": "c-l", "lines": ['scores = {"kim": [90, 85, 77],', '          "lee": [70, 95, 88],', '          "park": [60, 75, 99]}', 'print(scores["lee"])', 'print(scores["lee"][1])', "for name, s in scores.items():", "    print(name, sum(s), max(s))"], "n": 1,
           "out": ["[70, 95, 88]", "95", "kim 252 90", "lee 253 95", "park 234 99"]}, 96, 200, 860, sel="c-l")
o.append(label("scores", 1010, 200, K4, ' data-build-in="fade order 1"'))
o.append(lockers([('"kim"', "[90, 85, 77]"), ('"lee"', "[70, 95, 88]"), ('"park"', "[60, 75, 99]")], 1010, 246, 262, 150, K4, K4BG, hi=(1,), attrs=' data-build-in="rise order 1"', fs=24))
lv = [('scores["lee"]', "[70, 95, 88]", "키로 리스트를 꺼내요"), ('scores["lee"][1]', "95", "꺼낸 리스트의 1번"), ("sum(s)", "253", "s가 리스트라 sum을 써요")]
for i, (k, r, d) in enumerate(lv):
    o.append(row_card(1010, 446 + i * 116, 814, 100, k, r, d, i + 2, K4, K4BG, 280))
o.append(caption("키로 한 겹 꺼낸 뒤, 리스트 번호로 한 겹 더 꺼내요.", 920))
W("x-listval", o, "값 자리에는 숫자나 글자뿐 아니라 리스트도 넣을 수 있어요. 학생 이름을 키로, 세 과목 점수 리스트를 값으로 담았어요. scores[\"lee\"]는 lee의 점수 리스트예요. 거기에 [1]을 붙이면 그 리스트의 1번, 영어 95점이에요. 14의 scores[1][1]과 같은 점수를 이번에는 이름으로 찾았어요. for로 items()를 돌면 s에 리스트가 들어가서 sum, max를 바로 써요. 이 파트도 새 커널이라 셀 번호가 [1]부터예요. 출력은 실제로 실행한 결과예요.", ("mix", "리스트와 섞기"))

o = [sec("x-dictlist")] + head(EB4, "딕셔너리를 리스트에 담으면 주문 목록이 돼요", K4)
o += cell({"id": "c-o", "lines": ['orders = [{"menu": "coffee", "price": 4500, "qty": 2},', '          {"menu": "latte", "price": 5000, "qty": 1},', '          {"menu": "cake", "price": 6500, "qty": 3}]',
                                  "print(len(orders))", "print(orders[1])", 'print(orders[1]["menu"])', 'print(orders[2]["price"] * orders[2]["qty"])'], "n": 2,
           "out": ["3", "{'menu': 'latte', 'price': 5000, 'qty': 1}", "latte", "19500"]}, 96, 200, 1000, sel="c-o")
o.append(card(1150, 200, 674, 210, p(f"font-size:24px;font-weight:700;color:{GRAY}", "13 · 튜플을 담은 리스트") + mono("orders[1][0]", 28, GRAY, "#EEEFF2", "align-self:flex-start")
              + p(f"font-size:24px;color:{INK}", "0번이 메뉴라는 걸 외워야 해요"), GRAY, ' data-build-in="rise order 1"'))
o.append(card(1150, 430, 674, 210, p(f"font-size:24px;font-weight:700;color:{K4}", "15 · 딕셔너리를 담은 리스트") + mono('orders[1]["menu"]', 28, K4, K4BG, "align-self:flex-start")
              + p(f"font-size:24px;color:{INK}", "키 이름이 뜻을 말해 줘요"), K4, ' data-build-in="rise order 2"'))
for i, (m_, pr, q) in enumerate([("coffee", 4500, 2), ("latte", 5000, 1), ("cake", 6500, 3)]):
    o.append(f'<div data-build-in="rise order 3" style="position:absolute;left:{96 + i * 584}px;top:684px;width:560px;height:200px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:14px 20px;display:flex;flex-direction:column;gap:10px">'
             + p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{K4}", f"orders[{i}]")
             + lockers([('"menu"', f'"{m_}"'), ('"price"', str(pr)), ('"qty"', str(q))], w=164, h=116, color=K4, bg=K4BG, hi=(0, 1, 2), inline=True, fs=24, kfs=20) + '</div>')
o.append(caption("바깥은 리스트라 [번호], 안쪽은 딕셔너리라 [키]로 꺼내요.", 930))
W("x-dictlist", o, "13의 orders는 튜플을 담은 리스트라서 orders[1][0]처럼 번호 두 개로 꺼냈어요. 0번이 메뉴, 1번이 가격이라는 건 외워 둬야 했어요. 튜플 대신 딕셔너리를 담으면 orders[1][\"menu\"]처럼 이름으로 꺼내요. 바깥은 여전히 리스트라 앞 번호는 그대로 쓰고, 안쪽은 키로 꺼내요. 대괄호가 닫히기 전에는 줄을 바꿔 적어도 돼요. 출력은 실제로 실행한 결과예요.")

o = [sec("x-for")] + head(EB4, "for로 주문을 하나씩 꺼내요", K4)
o += cell({"id": "c-r", "lines": ["for order in orders:", '    print(order["menu"], order["price"] * order["qty"])'], "n": 3, "out": ["coffee 9000", "latte 5000", "cake 19500"]}, 96, 200, 1100, sel="c-r")
for i, (m_, pr, q) in enumerate([("coffee", 4500, 2), ("latte", 5000, 1), ("cake", 6500, 3)]):
    y = 480 + i * 140
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:96px;top:{y}px;width:1728px;height:124px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:0 28px;display:flex;flex-direction:row;align-items:center;gap:24px">'
             + p(f"width:110px;flex:none;font-size:26px;font-weight:700;color:{K4}", f"{i + 1}번째") + mono("order =", 24, K4, K4BG)
             + mono(f'{{"menu": "{m_}", "price": {pr}, "qty": {q}}}', 24)
             + f'<x-shape kind="arrow-right" style="width:44px;height:26px;flex:none;background:#C9CED8"></x-shape>'
             + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{INK};white-space:pre", f"{m_} {pr * q}") + '</div>')
o.append(caption("order에는 딕셔너리 하나가 통째로 들어가요.", 920))
W("x-for", o, "14에서 2차원 리스트를 for로 돌면 row에 행 리스트가 통째로 들어갔어요. 딕셔너리 리스트도 같아요. order에는 주문 딕셔너리 하나가 들어가서, order[\"menu\"], order[\"price\"]처럼 키로 꺼내요. 가격과 수량을 곱하면 주문마다 금액이 나와요. 출력은 실제로 실행한 결과예요.")

RECEIPT = ['print("=" * 33)', "print(f\"{'KANT 카페':^31}\")", "print(f\"{'2026-11-03  14:30':^33}\")", 'print("=" * 33)', "print(f\"{'메뉴명':<7}{'단가':>6}{'수량':>3}{'금액':>8}\")", 'print("-" * 33)',
           "total = 0", "count = 0", "for order in orders:", '    amount = order["price"] * order["qty"]', "    print(f\"{order['menu']:<10}{order['price']:>8,}{order['qty']:>5}{amount:>10,}\")",
           "    total += amount", '    count += order["qty"]', 'print("-" * 33)', "print(f\"{'수량':<6}{count:>15}\")", "print(f\"{'합계':<6}{total:>25,}\")", 'print("=" * 33)', "print(f\"{'감사합니다':^28}\")"]
RC_OUT = ["=================================", "            KANT 카페            ", "        2026-11-03  14:30        ", "=================================", "메뉴명        단가 수량      금액",
          "---------------------------------", "coffee       4,500    2     9,000", "latte        5,000    1     5,000", "cake         6,500    3    19,500", "---------------------------------",
          "수량                  6", "합계                       33,500", "=================================", "           감사합니다            "]
o = [sec("x-receipt")] + head(EB4, "KANT 카페 영수증을 딕셔너리로 다시 찍어요", K4)
o += [s.replace("font-size:26px;line-height:1.45", "font-size:21px;line-height:1.42") for s in cell({"id": "c-rc", "lines": RECEIPT, "n": 4}, 96, 186, 1200, sel="c-rc")]
o.append(f'<div data-build-in="rise order 1" style="position:absolute;left:1350px;top:186px;width:474px;height:520px;background:#FFFFFF;border:2px solid {LINE};border-radius:16px;padding:26px 20px;display:flex;flex-direction:column;box-shadow:0 10px 30px rgba(0,0,0,0.08)">'
         + "".join(p(f"font-family:{MONO};font-size:21px;line-height:1.5;white-space:pre;color:{INK}", WIDE(e(l))) for l in RC_OUT) + '</div>')
o.append(card(1350, 730, 474, 160, p(f"font-size:24px;font-weight:700;color:{INK}", "13의 영수증과 같은 결과")
              + p(f"font-size:22px;line-height:1.45;color:{INK}", 'orders[0][1] 대신 order["price"]로 읽어요'), K4, ' data-build-in="rise order 2"', "justify-content:center;padding:16px 24px"))
o.append(caption("for 안에서 키로 꺼내니 어느 값이 무엇인지 읽혀요.", 920))
W("x-receipt", o, "13의 2파트 끝에서 찍은 KANT 카페 영수증을 딕셔너리 리스트로 다시 찍어요. 머리글과 구분선은 13과 같아요. 바뀐 곳은 for 안쪽이에요. 13에서는 for menu, price, qty in orders:로 튜플을 나눠 담았어요. 이번에는 order 하나에 딕셔너리가 통째로 들어가서 order[\"price\"]처럼 키로 꺼내요. f-string 중괄호 안에서 키를 적을 때는 바깥 큰따옴표와 겹치지 않게 작은따옴표로 적어요. 결과는 13과 같은 영수증이에요. 영수증의 한글은 영어 두 칸 너비로 그렸어요. 출력은 실제로 실행한 결과예요.")

o = [sec("x-cart")] + head(EB4, "메뉴판 딕셔너리에서 가격을 찾아요", K4)
o += cell({"id": "c-t", "lines": [MENU, 'cart = {"coffee": 2, "cake": 3}', "total = 0", "for name, qty in cart.items():", "    price = menu[name]", '    print(f"{name} {qty}개 {price * qty:,}원")', "    total += price * qty", 'print(f"합계 {total:,}원")'], "n": 5,
           "out": ["coffee 2개 9,000원", "cake 3개 19,500원", "합계 28,500원"], "wide": True}, 96, 200, 980, sel="c-t")
o.append(p(f"position:absolute;left:1130px;top:200px;width:694px;font-size:24px;font-weight:700;color:{K1}", "menu · 메뉴판 (가격)", ' data-build-in="fade order 1"'))
o.append(lockers(M0, 1130, 240, 220, 120, K1, K1BG, hi=(0, 2), attrs=' data-build-in="rise order 1"', fs=30, kfs=22))
o.append(p(f"position:absolute;left:1130px;top:390px;width:694px;font-size:24px;font-weight:700;color:{K4}", "cart · 장바구니 (수량)", ' data-build-in="fade order 1"'))
o.append(lockers([('"coffee"', "2"), ('"cake"', "3")], 1130, 430, 220, 120, K4, K4BG, hi=(0, 1), attrs=' data-build-in="rise order 1"', fs=30, kfs=22))
for i, (k, pr, q) in enumerate([("coffee", 4500, 2), ("cake", 6500, 3)]):
    o.append(f'<div data-build-in="rise order {i + 2}" style="position:absolute;left:1130px;top:{600 + i * 116}px;width:694px;height:100px;background:{CARD};border:2px solid {LINE};border-radius:16px;padding:0 22px;display:flex;flex-direction:row;align-items:center;gap:16px">'
             + mono(f'menu["{k}"]', 24, K1, K1BG) + f'<x-shape kind="arrow-right" style="width:40px;height:24px;flex:none;background:#C9CED8"></x-shape>'
             + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{INK};white-space:pre", f"{pr} × {q} = {pr * q:,}") + '</div>')
o.append(caption("장바구니에는 수량만 두고, 가격은 메뉴판에서 키로 찾아요.", 920))
W("x-cart", o, "가게에서는 메뉴판과 주문을 따로 둬요. menu는 메뉴 이름으로 가격을 찾는 딕셔너리, cart는 메뉴 이름으로 수량을 찾는 딕셔너리예요. for로 cart의 items()를 돌면서, 메뉴 이름 name으로 menu[name]을 꺼내면 가격이 나와요. 가격과 수량을 곱해 줄마다 찍고 total에 쌓아요. 가격이 바뀌면 메뉴판 한 곳만 고치면 돼요. 출력은 실제로 실행한 결과예요.")

o = [sec("x-err")] + head(EB4, "딕셔너리에서 자주 나는 오류", K4)
me = [("menu[0]", "KeyError: 0", "딕셔너리에는 번호가 없어요. 0이라는 키를 찾았어요", 6),
      ('menu["Latte"]', "KeyError: 'Latte'", "키는 대문자와 소문자를 구분해요", 7),
      ('orders["menu"]', "TypeError: list indices must be integers or slices, not str", 'orders는 리스트예요. orders[0]["menu"]처럼 번호부터 적어요', 8)]
for i, (code, err, why, n_) in enumerate(me):
    y = 210 + i * 220
    o += cell({"id": f"c-e{i}", "lines": [code], "n": n_, "out": [err], "err": True}, 96, y, 1180, attrs=f' data-build-in="rise order {i + 1}"')
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:1320px;top:{y}px;width:504px;height:150px;background:{CARD};border:2px solid {LINE};border-left:12px solid {K4};border-radius:16px;padding:0 24px;display:flex;flex-direction:column;justify-content:center;gap:6px">'
             + p(f"font-size:24px;font-weight:700;line-height:1.4;color:{INK}", e(why)) + '</div>')
o.append(caption("KeyError 뒤에는 찾던 키가 나와요. 그 키가 정말 있는지 봐요.", 900))
W("x-err", o, "딕셔너리에서 자주 나는 오류예요. menu[0]은 리스트처럼 번호로 꺼낸 경우예요. 딕셔너리에는 번호가 없어서 0이라는 키를 찾다가 KeyError가 나요. menu[\"Latte\"]는 대문자 L로 적어서 latte와 다른 키예요. orders[\"menu\"]는 리스트에 키를 넣은 경우예요. orders는 바깥이 리스트라 번호부터 적고, 그다음에 키를 적어요. 출력은 실제로 실행한 결과예요.")

# ---------- summary ----------
o = [sec("trouble")] + head("정리", "막히면 오류의 마지막 줄을 봐요", RED)
tr = [("KeyError: 'tea'", "없는 키를 꺼냈어요", 'menu.get("tea", 0)'),
      ("KeyError: 0", "딕셔너리에서 번호로 꺼냈어요", 'menu["coffee"]'),
      ("KeyError: 'Latte'", "키의 대문자와 소문자가 달라요", 'menu["latte"]'),
      ("TypeError: list indices must be integers or slices, not str", "리스트에 키를 넣었어요", 'orders[0]["menu"]'),
      ("{'latte': 5500}", "같은 키를 두 번 넣어서 하나만 남았어요", "키를 다르게 적기"),
      ("5500 in menu  →  False", "in은 키만 봐요", "5500 in menu.values()")]
o.append('<div style="position:absolute;left:96px;top:196px;width:1728px;height:724px;display:flex;flex-direction:column;gap:8px">')
for i, (q, a_, cmd) in enumerate(tr, 1):
    o.append(f'<div data-build-in="rise order {i}" style="flex:1;display:flex;flex-direction:row;gap:26px;align-items:center;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:8px 30px">'
             + num(i, RED, 32)
             + '<div style="flex:1;display:flex;flex-direction:column;gap:4px">' + p(f"font-family:{MONO};font-size:22px;font-weight:700;color:{INK};white-space:nowrap", e(q)) + p(f"font-size:22px;color:{SUB}", e(a_)) + '</div>'
             + p(f"width:360px;flex:none;{'font-family:' + MONO + ';font-size:22px;' if cmd.isascii() else 'font-size:24px;'}font-weight:700;line-height:1.5;color:{INK};background:#EEEFF2;padding:8px 18px;border-radius:12px;white-space:pre", e(cmd)) + '</div>')
o.append('</div>')
o.append(caption("오류가 안 나도 결과가 이상하면 키가 겹치지 않았는지 봐요.", 940))
W("trouble", o, "1번부터 3번은 모두 KeyError예요. 오류 마지막 줄의 KeyError 뒤에 찾던 키가 나와서, 어떤 키가 없는지 바로 알 수 있어요. 없을 수도 있는 키는 get으로 꺼내요. 4번은 바깥이 리스트인데 키부터 적은 경우예요. 5번과 6번은 오류는 안 나지만 결과가 생각과 다른 경우예요. 같은 키를 두 번 넣으면 마지막 값만 남고, in은 값이 아니라 키를 봐요. 모두 hello-uv 커널에서 실제로 실행한 결과예요.", ("trouble", "정리"))

o = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>']
cheat = [('{"latte": 5000}', "키: 값으로 만들기", K1), ('menu["latte"]', "키로 꺼내기", K1), ('menu.get("tea", 0)', "없으면 기본값", K1), ('menu["tea"] = 4000', "없으면 추가, 있으면 수정", K2),
         ('del menu["tea"]', "키와 값 지우기", K2), ('"tea" in menu', "키가 있는지 묻기", K2), ("for k, v in menu.items():", "한 쌍씩 꺼내기", K3), ('orders[1]["menu"]', "리스트 안 딕셔너리", K4)]
for i, (k, d, c) in enumerate(cheat):
    x, y = 96 + (i % 4) * 438, 200 + (i // 4) * 290
    o.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:414px;height:264px;background:{CARD};border:2px solid {LINE};border-top:10px solid {c};border-radius:20px;padding:28px 28px;display:flex;flex-direction:column;gap:20px">'
             + mono(k, 26 if len(k) <= 18 else 21, c, "#F6F5F1", "align-self:flex-start") + p(f"font-size:28px;font-weight:700;color:{INK}", d) + '</div>')
o.append(f'<div style="position:absolute;left:96px;top:780px;width:1728px;height:210px;background:{CARD};border:2px solid {LINE};border-radius:20px;padding:24px 36px;display:flex;flex-direction:column;justify-content:center;gap:14px">'
         + p(f"font-size:30px;font-weight:700;color:{INK}", '리스트는 <span style="font-family:\'JetBrains Mono\';color:' + GRAY + '">[번호]</span>, 딕셔너리는 <span style="font-family:\'JetBrains Mono\';color:' + K1 + '">[키]</span>로 꺼내요')
         + p(f"font-size:30px;font-weight:700;color:{INK}", "키는 겹치지 않아요. 같은 키에 넣으면 값이 바뀌어요") + '</div>')
W("cheatsheet", o, "이번 챕터에서 쓴 코드를 한 장에 모았어요. 딕셔너리는 키로 값을 찾고, 키는 겹치지 않는다는 것을 기억해요. 노트북에 이 장의 내용을 마크다운 셀로 정리해 두면 복습할 때 같이 봐요. 다음에 배울 if 문과 in을 함께 쓰면 키가 있을 때만 꺼내는 코드를 만들 수 있어요.")

# ---------- toc ----------
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
parts = [("Key", K1, "만들고 꺼내기", "번호 대신 키로 찾기, { 키: 값 }, [키]로 꺼내기, KeyError와 get, get이 줄인 긴 코드", "d-why", "d-short"),
         ("Wrench", K2, "바꾸고 지우기", "추가와 수정, 키는 겹치지 않기, del과 pop, 키를 보는 in", "d-add", "d-in"),
         ("Search", K3, "둘러보기", "keys, values, items, list()로 바꿔 번호로 꺼내기, for로 한 쌍씩, sum과 sorted, get을 쓰는 곳(기본값, 개수 세기)", "d-views", "d-count"),
         ("Database", K4, "리스트와 섞기", "값이 리스트인 딕셔너리, 딕셔너리 리스트, 영수증, 메뉴판에서 가격 찾기, 오류", "x-listval", "x-err")]
TOC_NOTE = "네 파트로 나눴어요. 1파트는 딕셔너리를 만들고 키로 꺼내는 법, 2파트는 추가, 수정, 삭제예요. 3파트는 for로 딕셔너리를 둘러보고, 4파트는 리스트와 섞어 13의 영수증을 다시 찍어요. 파트마다 새 커널에서 위에서부터 차례로 실행해요."

DECK_TITLE = "파이썬 기초 4 (딕셔너리)"
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

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-03T01:00:00Z"}, "lists": "css", "title": DECK_TITLE, "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
print(len(ORDER), "slides")
