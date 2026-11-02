"""Generates every slide of the Python basics 3 deck (14) and slides/deck.json.

Story: keeps writing in basics.ipynb from chapters 12 and 13. Asks whether a value is in a list, tuple or string
with in and not in, then puts table-shaped data (scores, students, seats) into a list of lists.
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
T1, T1BG = TEAL, "#E2F2F3"
T6, T6BG = "#A23B72", "#F6E7EF"
EB1 = "1. in과 not in"
EB2 = "2. 2차원 리스트"


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


# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#F2B27A;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
       '<h1 style="font-size:92px;font-weight:900;line-height:1.1;color:#F6F5F1">파이썬 기초 3<br>in과<br>2차원 리스트</h1>',
       '<p style="font-size:40px;line-height:1.4;color:#BFC6D4">들어 있는지 묻고,<br>표 모양 데이터 다루기</p>']
cov.append(f'<div style="position:absolute;left:1060px;top:300px;width:720px;height:480px;background:#252B36;border-radius:24px;padding:44px 48px;display:flex;flex-direction:column;justify-content:center;gap:34px">')
for code, out_, c in [('"latte" in menu', 'True', '#8FD8DE'), ('"tea" not in menu', 'True', '#8FD8DE'), ('scores[1][2]', '88', '#E6A3C8'), ('len(scores[0])', '3', '#E6A3C8')]:
    cov.append('<div style="display:flex;flex-direction:row;align-items:center;gap:28px">'
               + p(f"width:420px;flex:none;font-family:{MONO};font-size:36px;font-weight:700;color:{c};white-space:pre", e(code))
               + f'<x-shape kind="arrow-right" style="width:50px;height:30px;background:#5A6172"></x-shape>'
               + p(f"font-family:{MONO};font-size:36px;font-weight:700;color:#E6E9EF", e(out_)) + '</div>')
cov.append('</div>')
W("cover", cov, "13에서 리스트와 튜플에 값을 담고 for로 하나씩 꺼냈어요. 이번 챕터는 그 위에서 두 가지를 더해요. 1파트는 in과 not in으로 값이 들어 있는지 True, False로 묻는 법이에요. 2파트는 리스트 안에 리스트를 넣은 2차원 리스트로 성적표, 좌석표 같은 표 모양 데이터를 다뤄요. 모든 예제는 12, 13에서 쓰던 노트북 셀에 이어서 적고 실행해요.", ("intro", "들어가기"))

ORDER.append("toc")   # written last, after page numbers are known

# ---------- ready ----------
o = [sec("ready")] + head("들어가기", "13에서 이어서 해요", JP)
done = [("hello-uv 노트북, 커널 .venv", "09 · 25–27쪽"), ("비교와 and, or, not", "12 · 4파트"), ("리스트, 튜플, [번호][번호]", "13 · 2파트"), ("for 문, += 로 합계 쌓기", "13 · 2파트")]
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
W("ready", o, "09에서 만든 hello-uv 폴더를 VS Code로 열고, 12와 13에서 쓰던 basics.ipynb를 다시 열어요. 12의 4파트에서 배운 비교와 and, or, not, 13의 2파트에서 배운 리스트, 튜플, for를 그대로 써요. 슬라이드의 출력은 tools/demo.sh가 hello-uv 커널에서 같은 셀을 실제로 실행한 결과예요. 셀 번호는 파트마다 [1]부터 다시 셌어요.")

# ---------- part 1: in / not in ----------
o = [sec("in-list")] + head(EB1, "in은 들어 있는지 True, False로 답해요", T1)
o += cell({"id": "c-il", "lines": ['menu = ["coffee", "latte", "cake"]', 'print("latte" in menu)', 'print("juice" in menu)', 'print("juice" not in menu)', 'print("latte" not in menu)'], "n": 1,
           "out": ["True", "False", "True", "False"]}, 96, 200, 820, sel="c-il")
o.append(p(f"position:absolute;left:980px;top:200px;width:844px;font-family:{MONO};font-size:28px;font-weight:700;color:{T1}", "menu", ' data-build-in="fade order 1"'))
o.append(slots(["coffee", "latte", "cake"], 980, 246, 260, 90, hi=(1,), attrs=' data-build-in="rise order 1"', fs=30, color=T1, bg=T1BG))
il = [('"latte" in menu', "True", "latte가 있어요"), ('"juice" in menu', "False", "juice는 없어요"), ('"juice" not in menu', "True", "없는 게 맞아요"), ('"latte" not in menu', "False", "있으니까 틀렸어요")]
for i, (k, r, d) in enumerate(il):
    o.append(row_card(980, 420 + i * 108, 844, 94, k, r, d, i + 2, T1, T1BG, 330))
o.append(caption("not in은 in의 반대예요. 없으면 True, 있으면 False예요.", 900))
W("in-list", o, "in은 왼쪽 값이 오른쪽 리스트 안에 들어 있는지 물어요. 답은 12의 4파트에서 본 비교처럼 True나 False예요. latte는 menu에 있어서 True, juice는 없어서 False예요. not in은 반대로 없는지 물어요. 그래서 juice not in menu는 True예요. 13의 2파트 찾기 장에서 95 in scores를 잠깐 봤는데, 이 파트에서 in과 not in을 한곳에 모아 정리해요. 이 파트도 새 커널이라 셀 번호가 [1]부터예요. 출력은 실제로 실행한 결과예요.", ("in", "in과 not in"))

o = [sec("in-tuple-str")] + head(EB1, "튜플과 문자열에도 in을 써요", T1)
o += cell({"id": "c-it", "lines": ['order = ("coffee", 4500, 2)', "print(4500 in order)", "print(5000 in order)", 'print("4500" in order)', 'print("tea" not in order)'], "n": 2,
           "out": ["True", "False", "False", "True"]}, 96, 200, 840)
o += cell({"id": "c-is", "lines": ['word = "python"', 'print("th" in word)', 'print("pt" in word)', 'print("P" in word)', 'print("z" not in word)'], "n": 3,
           "out": ["True", "False", "False", "True"]}, 984, 200, 840, sel="c-is", attrs=' data-build-in="rise order 1"')
its = [(96, '4500  "4500"', "숫자 4500과 글자 \"4500\"은 다른 값이에요", T1), (684, '"th" in word', "붙어 있는 글자 조각을 찾아요. pt는 떨어져 있어서 False", T1), (1272, '"P" in word', "대문자와 소문자를 구분해요. python에는 소문자 p만 있어요", T1)]
for i, (x, k, d, c) in enumerate(its):
    o.append(card(x, 620, 552, 240, mono(k, 28, c, T1BG, "align-self:flex-start") + p(f"font-size:25px;line-height:1.45;color:{INK}", e(d)), c, f' data-build-in="rise order {i + 2}"'))
o.append(caption("리스트, 튜플, 문자열 모두 in과 not in을 같은 모양으로 써요.", 920))
W("in-tuple-str", o, "in은 튜플에도 그대로 써요. 4500은 order 안에 있어서 True예요. 글자 \"4500\"은 숫자 4500과 다른 값이라 False예요. 12의 2파트에서 본 타입 차이가 여기서도 나와요. 문자열에 in을 쓰면 글자 조각이 붙어 있는지 찾아요. th는 python 안에 붙어 있어서 True고, p와 t는 떨어져 있어서 pt는 False예요. 대문자 P는 python에 없어서 False예요. 문자열에 숫자 3을 물으면 TypeError가 나는데, 정리 장에서 봐요. 출력은 실제로 실행한 결과예요.")

o = [sec("in-logic")] + head(EB1, "in의 결과는 and, or와 섞어 써요", T1)
o += cell({"id": "c-ig", "lines": ['print(not "juice" in menu)', 'print("juice" not in menu)', 'has_both = "latte" in menu and "cake" in menu', "print(has_both)", 'print("juice" in menu or "tea" in menu)'], "n": 4,
           "out": ["True", "True", "True", "False"]}, 96, 200, 1000, sel="c-ig")
ig = [('"juice" not in menu', "not \"juice\" in menu와 결과가 같아요. not in 쪽이 읽기 쉬워서 이렇게 써요"),
      ('A in menu and B in menu', "둘 다 있어야 True예요. latte와 cake가 모두 있어서 True"),
      ('A in menu or B in menu', "하나만 있어도 True예요. juice도 tea도 없어서 False")]
for i, (k, d) in enumerate(ig):
    o.append(card(1150, 200 + i * 228, 674, 208, mono(k, 26, T1, T1BG, "align-self:flex-start") + p(f"font-size:23px;line-height:1.45;color:{INK}", e(d)), None, f' data-build-in="rise order {i + 1}"'))
o.append(card(96, 620, 1000, 220, p(f"font-size:28px;font-weight:700;color:{INK}", "결과를 변수에 담아 둘 수 있어요")
              + mono('has_both = "latte" in menu and "cake" in menu', 24, T1, T1BG, "align-self:flex-start") + p(f"font-size:22px;color:{SUB}", "12의 4파트 is_adult = age >= 20 과 같은 모양이에요"), T1, ' data-build-in="rise order 4"'))
o.append(caption("나중에 배울 if 문은 이 True, False로 할 일을 골라요.", 920))
W("in-logic", o, "in의 답은 True나 False라서 12의 4파트에서 배운 and, or, not과 섞어 쓸 수 있어요. not \"juice\" in menu는 in을 먼저 계산한 뒤 not으로 뒤집어요. 결과는 \"juice\" not in menu와 같지만, not in으로 붙여 쓰는 쪽이 읽기 쉬워요. and는 둘 다 있어야, or는 하나만 있어도 True예요. has_both처럼 결과를 변수에 담아 둘 수도 있어요. 출력은 실제로 실행한 결과예요.")

o = [sec("in-orders")] + head(EB1, "in은 한 겹만 들여다봐요", T1)
o += cell({"id": "c-io", "lines": ['orders = [("coffee", 4500, 2), ("latte", 5000, 1), ("cake", 6500, 3)]', 'print(("cake", 6500, 3) in orders)', 'print("cake" in orders)', 'print("cake" in orders[2])'], "n": 5,
           "out": ["True", "False", "True"]}, 96, 200, 1728, sel="c-io")
o.append(p(f"position:absolute;left:96px;top:530px;width:1728px;font-family:{MONO};font-size:26px;font-weight:700;color:{T1}", "orders", ' data-build-in="fade order 1"'))
o.append(slots(['("coffee", 4500, 2)', '("latte", 5000, 1)', '("cake", 6500, 3)'], 96, 570, 560, 76, hi=(2,), attrs=' data-build-in="rise order 1"', fs=26, color=T1, bg=T1BG))
io = [('("cake", 6500, 3) in orders', "True", "튜플 통째로는 찾아요"), ('"cake" in orders', "False", "바깥에는 튜플 세 개만 있어요"), ('"cake" in orders[2]', "True", "한 겹 꺼낸 튜플 안에는 있어요")]
for i, (k, r, d) in enumerate(io):
    o.append(card(96 + i * 568, 716, 560, 170, '<div style="display:flex;flex-direction:row;align-items:center;gap:14px">' + mono(k, 23, T1, T1BG) + tf(r, 23) + '</div>'
                  + p(f"font-size:22px;color:{SUB}", e(d)), None, f' data-build-in="rise order {i + 2}"', "justify-content:center;padding:14px 20px"))
o.append(caption("안쪽까지 보려면 orders[2]처럼 한 겹 꺼낸 뒤 in을 써요.", 920))
W("in-orders", o, "13의 orders는 리스트 안에 튜플을 넣은 모양이에요. in은 바깥 리스트의 값 하나하나와 통째로 비교해요. 그래서 튜플 (\"cake\", 6500, 3)은 찾지만, 글자 \"cake\"는 바깥에 없어서 False예요. 튜플 안까지 보려면 orders[2]로 한 겹 꺼낸 뒤 in을 써요. 다음 파트의 2차원 리스트에서도 같은 일이 생겨요. 출력은 실제로 실행한 결과예요.")

# ---------- part 2: 2D lists ----------
SC0 = [[90, 85, 77], [70, 95, 88], [60, 75, 99]]
SC1 = [[90, 100, 77], [70, 95, 88], [65, 80, 90]]
SUBJ = ["kor", "eng", "math"]

o = [sec("m-make")] + head(EB2, "리스트 안에 리스트를 넣으면 표가 돼요", T6)
o += cell({"id": "c-mm", "lines": ["scores = [[90, 85, 77],", "          [70, 95, 88],", "          [60, 75, 99]]", "print(scores)", "print(len(scores))", "print(len(scores[0]))"], "n": 1,
           "out": ["[[90, 85, 77], [70, 95, 88], [60, 75, 99]]", "3", "3"]}, 96, 200, 840, sel="c-mm")
o.append(grid(SC0, 1040, 200, 170, 88, cols=SUBJ, attrs=' data-build-in="rise order 1"', fs=36))
o.append(p(f"position:absolute;left:1040px;top:200px;width:60px;font-size:20px;font-weight:700;color:{GRAY}", "행＼열", ' data-build-in="fade order 1"'))
mm = [("len(scores)", "3", "행 수. 바깥 리스트에 든 줄의 개수"), ("len(scores[0])", "3", "열 수. 0행 안에 든 칸의 개수")]
for i, (k, r, d) in enumerate(mm):
    o.append(row_card(1000, 640 + i * 116, 824, 100, k, r, d, i + 2, T6, T6BG, 250))
o.append(caption("바깥 리스트 하나가 표, 안쪽 리스트 하나가 한 줄(행)이에요.", 920))
W("m-make", o, "13의 리스트 모양 장에서 리스트 안에 리스트를 넣으면 표 모양이 된다고 했어요. 이 모양을 2차원 리스트라고 불러요. scores는 학생 세 명의 국어, 영어, 수학 점수예요. 안쪽 리스트 하나가 학생 한 명, 표의 가로 한 줄이에요. 가로 줄을 행, 세로 줄을 열이라고 불러요. 줄을 나눠 적으면 표처럼 읽기 쉬워요. 대괄호가 닫히기 전에는 줄을 바꿔도 돼요. len(scores)는 바깥 리스트의 개수라 행 수, len(scores[0])은 첫 행 안의 개수라 열 수예요. 이 파트도 새 커널이라 셀 번호가 [1]부터예요. 출력은 실제로 실행한 결과예요.", ("matrix", "2차원 리스트"))

o = [sec("m-index")] + head(EB2, "[행][열] 순서로 꺼내요", T6)
o += cell({"id": "c-mi", "lines": ["print(scores[1])", "print(scores[1][2])", "print(scores[0][0])", "print(scores[-1][-1])"], "n": 2,
           "out": ["[70, 95, 88]", "88", "90", "99"]}, 96, 200, 680, sel="c-mi")
mi = [("scores[1]", {(1, 0), (1, 1), (1, 2)}, "[70, 95, 88]", "1행 통째로"), ("scores[1][2]", {(1, 2)}, "88", "1행의 2열"),
      ("scores[0][0]", {(0, 0)}, "90", "맨 왼쪽 위"), ("scores[-1][-1]", {(2, 2)}, "99", "마지막 행의 마지막 열")]
for i, (k, hi, r, d) in enumerate(mi):
    x, y = 840 + (i % 2) * 502, 200 + (i // 2) * 350
    o.append(card(x, y, 482, 330, '<div style="display:flex;flex-direction:row;align-items:center;gap:14px">' + mono(k, 26, T6, T6BG) + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{INK};white-space:pre", e(r)) + '</div>'
                  + grid(SC0, cw=96, ch=52, hi=hi, fs=24, lbl=20, inline=True) + p(f"font-size:22px;color:{SUB}", e(d)), None, f' data-build-in="rise order {i + 1}"', "padding:20px 24px;gap:12px"))
o.append(caption("앞 번호가 행(가로 줄), 뒤 번호가 열(세로 줄)이에요.", 920))
W("m-index", o, "2차원 리스트도 13에서 orders[1][0]으로 꺼낸 것처럼 번호 두 개로 꺼내요. 번호 하나만 쓰면 행 하나가 리스트로 통째로 나와요. scores[1]은 1행 [70, 95, 88]이에요. 거기에 번호를 하나 더 붙이면 그 행 안의 칸이에요. scores[1][2]는 1행의 2열이라 88이에요. 번호는 행도 열도 0부터 세요. -1은 맨 뒤라서 scores[-1][-1]은 마지막 행의 마지막 열 99예요. 출력은 실제로 실행한 결과예요.")

o = [sec("m-change")] + head(EB2, "칸 하나도, 줄 하나도 바꿀 수 있어요", T6)
o += cell({"id": "c-mc", "lines": ["scores[0][1] = 100", "print(scores[0])", "scores[2] = [65, 80, 90]", "print(scores)"], "n": 3,
           "out": ["[90, 100, 77]", "[[90, 100, 77], [70, 95, 88], [65, 80, 90]]"]}, 96, 200, 900, sel="c-mc")
mc = [("scores[0][1] = 100", "번호 두 개", "칸 하나를 바꿔요"), ("scores[2] = [65, 80, 90]", "번호 하나", "행을 통째로 바꿔요")]
for i, (k, t, d) in enumerate(mc):
    o.append(card(96, 520 + i * 180, 900, 160, '<div style="display:flex;flex-direction:row;align-items:center;gap:18px">' + mono(k, 26, T6, T6BG) + '</div>'
                  + p(f"font-size:25px;color:{INK}", f'<b style="color:{T6}">{e(t)}</b> · {e(d)}'), None, f' data-build-in="rise order {i + 1}"', "justify-content:center"))
mid = [[90, 100, 77], [70, 95, 88], [60, 75, 99]]
o.append(p(f"position:absolute;left:1100px;top:200px;width:724px;font-size:24px;font-weight:700;color:{T6}", "첫째 줄 실행 뒤", ' data-build-in="fade order 1"'))
o.append(grid(mid, 1100, 240, 130, 62, hi={(0, 1)}, fs=28, lbl=22, attrs=' data-build-in="rise order 1"'))
o.append(p(f"position:absolute;left:1100px;top:540px;width:724px;font-size:24px;font-weight:700;color:{T6}", "셋째 줄 실행 뒤", ' data-build-in="fade order 2"'))
o.append(grid(SC1, 1100, 580, 130, 62, hi={(2, 0), (2, 1), (2, 2)}, fs=28, lbl=22, attrs=' data-build-in="rise order 2"'))
o.append(caption("13에서 본 리스트 바꾸기와 같아요. 번호를 몇 개 쓰는지만 달라요.", 920))
W("m-change", o, "리스트는 바꿀 수 있어서 2차원 리스트도 칸을 바꿀 수 있어요. 번호 두 개를 쓰면 칸 하나, 번호 하나를 쓰면 행 하나를 통째로 바꿔요. 0행 1열 85가 100으로, 2행 전체가 [65, 80, 90]으로 바뀌었어요. 다음 장부터는 이렇게 바뀐 scores를 계속 써요. 출력은 실제로 실행한 결과예요.")

o = [sec("m-for")] + head(EB2, "for로 한 줄(행)씩 꺼내요", T6)
o += cell({"id": "c-mf", "lines": ["for row in scores:", '    print(row, "합계:", sum(row), "최고:", max(row))'], "n": 4,
           "out": ["[90, 100, 77] 합계: 267 최고: 100", "[70, 95, 88] 합계: 253 최고: 95", "[65, 80, 90] 합계: 235 최고: 90"]}, 96, 200, 1300, sel="c-mf")
for i, (r, s, m) in enumerate([(SC1[0], 267, 100), (SC1[1], 253, 95), (SC1[2], 235, 90)]):
    y = 470 + i * 140
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:96px;top:{y}px;width:1728px;height:124px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:0 28px;display:flex;flex-direction:row;align-items:center;gap:26px">'
             + p(f"width:140px;flex:none;font-size:26px;font-weight:700;color:{T6}", f"{i + 1}번째") + mono("row =", 26, T6, T6BG)
             + slots([str(v) for v in r], 0, 0, 110, 70, top_lbl=False, fs=28).replace("position:absolute;left:0px;top:0px;", "")
             + f'<x-shape kind="arrow-right" style="width:44px;height:26px;flex:none;background:#C9CED8"></x-shape>'
             + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{INK};white-space:pre", f"sum {s}   max {m}") + '</div>')
o.append(caption("row에는 숫자 하나가 아니라 한 행 리스트가 통째로 들어가요.", 920))
W("m-for", o, "13의 2파트에서 for로 리스트 값을 하나씩 꺼냈어요. 2차원 리스트에 for를 쓰면 값 하나가 행 하나예요. 그래서 row에는 [90, 100, 77] 같은 리스트가 들어가요. row가 리스트니까 13에서 배운 sum, max를 바로 쓸 수 있어요. 학생마다 합계와 최고 점수가 한 줄씩 나와요. 출력은 실제로 실행한 결과예요.")

o = [sec("m-col")] + head(EB2, "열 하나는 for와 append로 모아요", T6)
o += cell({"id": "c-mo", "lines": ["eng = []", "for row in scores:", "    eng.append(row[1])", "print(eng)", 'print("영어 합계:", sum(eng))', 'print("영어 최저:", min(eng))'], "n": 5,
           "out": ["[100, 95, 80]", "영어 합계: 275", "영어 최저: 80"]}, 96, 200, 820, sel="c-mo")
o.append(grid(SC1, 1040, 200, 160, 80, hi={(0, 1), (1, 1), (2, 1)}, cols=SUBJ, fs=34, attrs=' data-build-in="rise order 1"'))
o.append(f'<x-shape kind="arrow-down" data-build-in="fade order 2" style="position:absolute;left:1270px;top:560px;width:40px;height:50px;background:#C9CED8"></x-shape>')
o.append(p(f"position:absolute;left:1040px;top:630px;width:200px;font-family:{MONO};font-size:28px;font-weight:700;color:{T6}", "eng", ' data-build-in="fade order 2"'))
o.append(slots(["100", "95", "80"], 1112, 620, 160, 80, attrs=' data-build-in="rise order 2"', fs=34, top_lbl=False))
o.append(caption("행은 scores[1]로 바로 꺼내지만, 열은 행마다 [1]을 꺼내 모아요.", 920))
W("m-col", o, "행은 scores[1]처럼 번호 하나로 바로 꺼내요. 열은 바로 꺼내는 방법이 없어서 행마다 같은 번호의 칸을 모아요. 빈 리스트 eng를 만들고, for로 행을 하나씩 꺼내 row[1]을 append해요. 영어는 1열이라 [1]이에요. 모은 eng는 보통 리스트라서 sum, min을 바로 써요. 출력은 실제로 실행한 결과예요.")

o = [sec("m-total")] + head(EB2, "전체 합계는 행 합계를 쌓아요", T6)
o += cell({"id": "c-mt", "lines": ["total = 0", "count = 0", "for row in scores:", "    total += sum(row)", "    count += len(row)", 'print("전체 합계:", total)', 'print("칸 수:", count)', 'print(f"평균: {total / count:.1f}")'], "n": 6,
           "out": ["전체 합계: 755", "칸 수: 9", "평균: 83.9"]}, 96, 200, 820, sel="c-mt")
hd = ["row", "sum(row)", "total", "count"]
o.append(f'<div data-build-in="fade order 1" style="position:absolute;left:980px;top:200px;width:844px;height:60px;display:flex;flex-direction:row;align-items:center;padding:0 22px;gap:12px">'
         + "".join(p(f"width:{w_}px;flex:none;font-family:{MONO};font-size:22px;font-weight:700;color:{GRAY}", e(t)) for t, w_ in zip(hd, (300, 170, 150, 120))) + '</div>')
for i, (r, s, t_, c_) in enumerate([(SC1[0], 267, 267, 3), (SC1[1], 253, 520, 6), (SC1[2], 235, 755, 9)]):
    o.append(f'<div data-build-in="rise order {i + 2}" style="position:absolute;left:980px;top:{270 + i * 110}px;width:844px;height:96px;background:{CARD};border:2px solid {LINE};border-radius:16px;padding:0 22px;display:flex;flex-direction:row;align-items:center;gap:12px">'
             + "".join(p(f"width:{w_}px;flex:none;font-family:{MONO};font-size:26px;font-weight:700;color:{c};white-space:pre", e(str(v))) for v, w_, c in ((r, 300, INK), (s, 170, INK), (t_, 150, T6), (c_, 120, T6))) + '</div>')
o.append(card(980, 640, 844, 200, p(f"font-size:26px;font-weight:700;color:{INK}", "평균 = 전체 합계 ÷ 칸 수")
              + mono('f"{total / count:.1f}"', 26, T6, T6BG, "align-self:flex-start") + p(f"font-size:22px;color:{SUB}", "13의 1파트 소수점 자리 맞추기로 한 자리만 보여 줘요"), None, ' data-build-in="rise order 5"'))
o.append(caption("total과 count는 for 앞에서 0으로 한 번만 시작해요.", 920))
W("m-total", o, "13의 for 합계 장처럼 for 앞에서 total을 0으로 시작해요. 이번에는 행마다 sum(row)를 더해서 표 전체의 합계를 쌓아요. count에는 len(row)를 더해서 칸 수를 세요. 세 행을 돌고 나면 total은 755, count는 9예요. 평균은 755 나누기 9라 83.888...인데, 13의 1파트에서 배운 .1f로 소수점 한 자리만 보여 줘요. 출력은 실제로 실행한 결과예요.")

o = [sec("m-table")] + head(EB2, "이름까지 넣으면 성적표가 돼요", T6)
o += cell({"id": "c-mb", "lines": ['students = [["kim", 90, 85, 77],', '            ["lee", 70, 95, 88],', '            ["park", 60, 75, 99]]', "print(f\"{'name':<6}{'kor':>5}{'eng':>5}{'math':>5}\")", 'print("-" * 21)',
                                   "for name, kor, eng, math in students:", '    print(f"{name:<6}{kor:>5}{eng:>5}{math:>5}")'], "n": 7,
           "out": ["name    kor  eng math", "---------------------", "kim      90   85   77", "lee      70   95   88", "park     60   75   99"]}, 96, 200, 1000, sel="c-mb")
mb = [("for name, kor, eng, math in students:", "한 행의 값 네 개를 변수 네 개에 나눠 담아요"), ("for menu, price, qty in orders:", "13의 영수증 for와 같은 모양이에요"), ("{kor:>5}", "오른쪽 맞춤 다섯 칸. 13의 1파트 칸 수 맞추기")]
for i, (k, d) in enumerate(mb):
    o.append(card(1140, 200 + i * 236, 684, 216, mono(k, 21, T6, T6BG, "align-self:flex-start") + p(f"font-size:24px;line-height:1.45;color:{INK}", e(d)), None, f' data-build-in="rise order {i + 1}"'))
o.append(caption("행 안의 값 개수와 for 뒤의 변수 개수가 같아야 해요.", 920))
W("m-table", o, "행마다 맨 앞에 이름을 넣으면 성적표가 돼요. 한 리스트 안에 글자와 숫자를 섞어도 된다는 건 13에서 봤어요. for 뒤에 변수를 네 개 적으면 행 하나의 값 네 개가 차례로 나뉘어 담겨요. 13의 영수증에서 쓴 for menu, price, qty in orders:와 같은 모양이에요. 머리글과 칸 수 맞추기는 13의 1파트 f-string이에요. 영어 머리글이라 한글 폭 문제가 없어요. 변수 개수가 행의 값 개수와 다르면 ValueError가 나요. 오류 장에서 봐요. 출력은 실제로 실행한 결과예요.")

o = [sec("m-in")] + head(EB2, "2차원 리스트에서 in은 행 단위로 찾아요", T6)
o += cell({"id": "c-mn", "lines": ["print(90 in students)", "print(90 in students[0])", 'print(["lee", 70, 95, 88] in students)', "for row in students:", "    print(row[0], 99 in row)"], "n": 8,
           "out": ["False", "True", "True", "kim False", "lee False", "park True"]}, 96, 200, 860, sel="c-mn")
mn = [("90 in students", "False", "바깥에는 행 리스트 세 개만 있어요"), ("90 in students[0]", "True", "kim 행 안에는 90이 있어요"), ('["lee", 70, 95, 88] in students', "True", "행 통째로는 찾아요"), ("99 in row", "park", "for로 행마다 물어요")]
for i, (k, r, d) in enumerate(mn):
    o.append(card(1010, 200 + i * 172, 814, 156, '<div style="display:flex;flex-direction:row;align-items:center;gap:16px">' + mono(k, 23, T6, T6BG) + (tf(r, 23) if r in ("True", "False") else "") + '</div>'
                  + p(f"font-size:22px;color:{SUB}", e(d)), None, f' data-build-in="rise order {i + 1}"', "justify-content:center;gap:10px;padding:14px 24px"))
o.append(caption("1파트의 orders와 같아요. in은 한 겹만 봐요.", 920))
W("m-in", o, "1파트에서 in은 한 겹만 들여다본다고 했어요. 2차원 리스트도 같아요. students의 값은 행 리스트 세 개라서 숫자 90을 물으면 False예요. students[0]으로 kim의 행을 꺼낸 뒤 물으면 True예요. 행을 통째로 적어서 물으면 찾아요. 어느 행에 99가 있는지 알고 싶으면 for로 행마다 99 in row를 물어요. park의 행만 True예요. 출력은 실제로 실행한 결과예요.")

o = [sec("m-slice")] + head(EB2, "자르기도 [행]과 [열]에 따로 써요", T6)
o += cell({"id": "c-ms", "lines": ["print(scores[:2])", "print(scores[1][:2])", "print(scores[0][::-1])"], "n": 9,
           "out": ["[[90, 100, 77], [70, 95, 88]]", "[70, 95]", "[77, 100, 90]"]}, 96, 200, 820, sel="c-ms")
ms = [("scores[:2]", {(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)}, "0행, 1행 두 줄"), ("scores[1][:2]", {(1, 0), (1, 1)}, "1행 안의 0열, 1열"), ("scores[0][::-1]", {(0, 0), (0, 1), (0, 2)}, "0행을 거꾸로")]
for i, (k, hi, d) in enumerate(ms):
    o.append(card(980, 200 + i * 236, 844, 220, '<div style="display:flex;flex-direction:row;align-items:center;gap:24px">'
                  + '<div style="width:300px;flex:none;display:flex;flex-direction:column;gap:10px">' + mono(k, 26, T6, T6BG, "align-self:flex-start") + p(f"font-size:22px;color:{SUB}", e(d)) + '</div>'
                  + grid(SC1, cw=96, ch=50, hi=hi, fs=24, lbl=18, inline=True) + '</div>', None, f' data-build-in="rise order {i + 1}"', "justify-content:center;padding:14px 26px"))
o.append(card(96, 520, 820, 320, p(f"font-size:28px;font-weight:700;color:{INK}", "자르는 위치가 달라요")
              + p(f"font-size:24px;line-height:1.5;color:{INK}", "scores[:2] 는 바깥 리스트를 잘라서 행을 가져와요.")
              + p(f"font-size:24px;line-height:1.5;color:{INK}", "scores[1][:2] 는 1행을 꺼낸 뒤 그 안의 칸을 잘라요.")
              + p(f"font-size:22px;color:{SUB}", "[시작:끝:간격]은 13의 2파트에서 배운 그대로예요"), T6, ' data-build-in="rise order 4"'))
o.append(caption("번호 하나째 자리는 행, 둘째 자리는 열이에요. 자르기도 같아요.", 920))
W("m-slice", o, "13의 2파트에서 배운 [시작:끝:간격] 자르기를 2차원 리스트에도 써요. scores[:2]는 바깥 리스트를 자르니까 행 두 개가 리스트로 나와요. scores[1][:2]는 1행을 먼저 꺼내고, 그 행의 0열과 1열을 잘라요. [::-1]은 거꾸로라서 0행이 [77, 100, 90]이 돼요. 열 하나를 통째로 자르는 문법은 없어서 앞의 for와 append로 모아요. 출력은 실제로 실행한 결과예요.")

o = [sec("m-add")] + head(EB2, "행은 append, 열은 for 안에서 append", T6)
o += cell({"id": "c-ma", "lines": ["scores.append([80, 70, 60])", "print(len(scores))", "for row in scores:", "    row.append(0)", "for row in scores:", "    print(row)"], "n": 10,
           "out": ["4", "[90, 100, 77, 0]", "[70, 95, 88, 0]", "[65, 80, 90, 0]", "[80, 70, 60, 0]"]}, 96, 200, 780, sel="c-ma")
SC2 = [r + [0] for r in SC1] + [[80, 70, 60, 0]]
o.append(grid(SC2, 1000, 200, 150, 78, hi={(3, 0), (3, 1), (3, 2), (3, 3), (0, 3), (1, 3), (2, 3)}, fs=32, attrs=' data-build-in="rise order 1"'))
ma = [("scores.append([80, 70, 60])", "새 행 하나. 바깥 리스트에 붙여요"), ("row.append(0)", "새 열. 행마다 하나씩 붙여요")]
for i, (k, d) in enumerate(ma):
    o.append(card(1000, 620 + i * 130, 824, 114, '<div style="display:flex;flex-direction:row;align-items:center;gap:18px">' + mono(k, 22, T6, T6BG) + p(f"font-size:22px;color:{SUB}", e(d)) + '</div>', None, f' data-build-in="rise order {i + 2}"', "justify-content:center;padding:10px 22px"))
o.append(caption("열을 더할 때는 행마다 하나씩 붙여야 해서 for를 써요.", 920))
W("m-add", o, "새 학생을 더하는 건 바깥 리스트에 행 하나를 append하는 거예요. 행 수가 4가 됐어요. 새 과목처럼 열을 더하려면 모든 행 끝에 하나씩 붙여야 해요. 그래서 for로 행을 꺼내 row.append(0)을 해요. row는 scores 안의 행 그 자체라서 row에 붙이면 scores도 바뀌어요. 출력은 실제로 실행한 결과예요.")

o = [sec("m-seats")] + head(EB2, "좌석표도 2차원 리스트예요", T6)
o += cell({"id": "c-mz", "lines": ['seats = [["O", "O", "X", "O"],', '         ["X", "O", "O", "O"],', '         ["O", "X", "X", "O"]]', 'seats[0][1] = "X"', "for row in seats:", '    print(" ".join(row))', 'print(seats[2].count("X"))', "print(len(seats) * len(seats[0]))"], "n": 11,
           "out": ["O X X O", "X O O O", "O X X O", "2", "12"]}, 96, 200, 820, sel="c-mz")
SE = [["O", "X", "X", "O"], ["X", "O", "O", "O"], ["O", "X", "X", "O"]]
taken = {(i, j) for i, r in enumerate(SE) for j, v in enumerate(r) if v == "X"}
o.append(p(f"position:absolute;left:1000px;top:200px;width:824px;height:44px;background:#E9E7E0;border-radius:10px;font-size:22px;font-weight:700;line-height:44px;text-align:center;color:{SUB}", "앞 (화면)", ' data-build-in="fade order 1"'))
o.append(grid(SE, 1000, 260, 150, 72, hi=taken, fs=32, attrs=' data-build-in="rise order 1"', color=RED, bg="#F8E6E6"))
sz = [('" ".join(row)', "13의 join으로 한 행을 글자 한 줄로"), ('seats[2].count("X")', "2행의 찬 자리 2개"), ("len(seats) * len(seats[0])", "행 수 × 열 수 = 좌석 12개")]
for i, (k, d) in enumerate(sz):
    o.append(row_card(1000, 590 + i * 104, 824, 92, k, "", d, i + 2, T6, T6BG, 400))
o.append(caption("행과 열이 있는 데이터는 모두 이 모양으로 담아요.", 920))
W("m-seats", o, "행과 열이 있는 건 무엇이든 2차원 리스트로 담아요. 극장 좌석표를 O는 빈자리, X는 찬 자리로 적었어요. seats[0][1] = \"X\"는 0행 1열 자리를 예약한 거예요. 13에서 배운 join으로 행마다 한 줄씩 찍으면 좌석표 모양이 나와요. count는 한 행 안의 X 개수를 세요. 행 수와 열 수를 곱하면 전체 좌석 수예요. 성적표, 좌석표, 달력, 엑셀 시트가 모두 이 모양이에요. 출력은 실제로 실행한 결과예요.")

o = [sec("m-trap")] + head(EB2, "[[0] * 3] * 3은 같은 행 하나를 세 번 담아요", T6)
o += cell({"id": "c-mp1", "lines": ["board = [[0] * 3] * 3", "board[0][0] = 9", "print(board)"], "n": 12, "out": ["[[9, 0, 0], [9, 0, 0], [9, 0, 0]]"], "err": True}, 96, 200, 900)
o += cell({"id": "c-mp2", "lines": ["board = [[0, 0, 0],", "         [0, 0, 0],", "         [0, 0, 0]]", "board[0][0] = 9", "print(board)"], "n": 13, "out": ["[[9, 0, 0], [0, 0, 0], [0, 0, 0]]"]}, 96, 450, 900, sel="c-mp2", attrs=' data-build-in="rise order 2"')


def lab_rows(boxes_, top, attrs):
    o_ = [f'<div{attrs} style="position:absolute;left:1060px;top:{top}px;width:764px;height:320px;background:{CARD};border:2px solid {LINE};border-radius:20px;padding:20px 28px;display:flex;flex-direction:row;align-items:center;gap:24px">']
    o_.append('<div style="display:flex;flex-direction:column;gap:22px">' + "".join(
        '<div style="display:flex;flex-direction:row;align-items:center;gap:14px">' + p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{T6}", f"board[{i}]") + f'<x-shape kind="arrow-right" style="width:60px;height:24px;flex:none;background:#C9CED8"></x-shape></div>' for i in range(3)) + '</div>')
    o_.append('<div style="display:flex;flex-direction:column;gap:12px;justify-content:center">' + "".join(boxes_) + '</div></div>')
    return "".join(o_)


bx = lambda t, on, h: p(f"width:300px;height:{h}px;border-radius:12px;border:3px solid {T6 if on else LINE};background:{T6BG if on else CARD};font-family:{MONO};font-size:28px;font-weight:700;line-height:{h - 6}px;text-align:center;color:{INK}", e(t))
o.append(p(f"position:absolute;left:1060px;top:200px;width:764px;font-size:24px;font-weight:700;color:{RED}", "[[0] * 3] * 3 · 행 하나를 셋이 같이 봐요", ' data-build-in="fade order 1"'))
o.append(lab_rows([bx("[9, 0, 0]", True, 200)], 240, ' data-build-in="rise order 1"'))
o.append(p(f"position:absolute;left:1060px;top:580px;width:764px;font-size:24px;font-weight:700;color:{GR}", "직접 적기 · 행이 세 개 따로 있어요", ' data-build-in="fade order 2"'))
o.append(lab_rows([bx("[9, 0, 0]", True, 64), bx("[0, 0, 0]", False, 64), bx("[0, 0, 0]", False, 64)], 600 + 20, ' data-build-in="rise order 2"').replace("height:320px", "height:290px"))
o.append(caption("빈 표는 행을 하나씩 직접 적어서 만들어요.", 940))
W("m-trap", o, "13에서 리스트에 * 3을 하면 값이 세 번 되풀이된다고 했어요. 그래서 [[0] * 3] * 3으로 0이 가득 찬 3행 3열 표를 만들고 싶어져요. 그런데 이렇게 만들면 행 리스트 하나를 세 번 담은 거라서, 세 행이 사실 같은 리스트예요. 0행 0열만 9로 바꿨는데 모든 행이 바뀌어요. 오류는 안 나지만 결과가 틀려요. 빈 표는 행을 하나씩 직접 적어서 만들면 행마다 따로 있어서 괜찮아요. 출력은 실제로 실행한 결과예요.")

o = [sec("m-err")] + head(EB2, "2차원 리스트에서 자주 나는 오류", T6)
me = [("scores[5][0]", "IndexError: list index out of range", "행은 0~3번까지 네 개예요", 14),
      ("scores[0][9]", "IndexError: list index out of range", "0행 안의 칸은 0~3번까지예요", 15),
      ("kor, eng, math = students[0]", "ValueError: too many values to unpack (expected 3)", "행에는 이름까지 값이 네 개예요", 16)]
for i, (code, err, why, n_) in enumerate(me):
    y = 210 + i * 220
    o += cell({"id": f"c-me{i}", "lines": [code], "n": n_, "out": [err], "err": True}, 96, y, 1180, attrs=f' data-build-in="rise order {i + 1}"')
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:1320px;top:{y}px;width:504px;height:140px;background:{CARD};border:2px solid {LINE};border-left:12px solid {T6};border-radius:16px;padding:0 24px;display:flex;flex-direction:column;justify-content:center;gap:6px">'
             + p(f"font-size:25px;font-weight:700;color:{INK}", e(why)) + '</div>')
o.append(caption("행 수는 len(scores), 열 수는 len(scores[0])로 확인해요.", 900))
W("m-err", o, "2차원 리스트에서 자주 나는 오류예요. 행을 하나 더해서 scores는 이제 4행 4열이에요. scores[5][0]은 없는 5행을 꺼내서 IndexError예요. scores[0][9]는 0행은 있지만 그 안에 9열이 없어서 같은 IndexError예요. 메시지가 같아서 앞 번호와 뒤 번호 중 어느 쪽이 넘쳤는지 len으로 확인해요. students의 행에는 이름까지 값이 네 개인데 변수를 세 개만 적으면 ValueError가 나요. 변수 개수를 값 개수에 맞춰요. 출력은 실제로 실행한 결과예요.")

# ---------- summary ----------
o = [sec("trouble")] + head("정리", "막히면 오류의 마지막 줄을 봐요", RED)
tr = [("TypeError: 'in <string>' requires string as left operand, not int", "문자열 안에 숫자가 있는지 물었어요", '"3" in word', True),
      ("IndexError: list index out of range", "행이나 열 번호가 넘쳤어요", "len()으로 확인", True),
      ("ValueError: too many values to unpack (expected 3)", "행의 값 개수와 변수 개수가 달라요", "변수를 값 수만큼", True),
      ("[[9, 0, 0], [9, 0, 0], [9, 0, 0]]", "칸 하나만 바꿨는데 모든 행이 바뀌었어요", "행을 직접 적기", True),
      ("90 in students  →  False", "in은 바깥 한 겹만 봐요", "90 in students[0]", True),
      ('"P" in word  →  False', "대문자와 소문자가 달라요", '"p" in word', True)]
o.append('<div style="position:absolute;left:96px;top:196px;width:1728px;height:724px;display:flex;flex-direction:column;gap:8px">')
for i, (q, a_, cmd, m) in enumerate(tr, 1):
    o.append(f'<div data-build-in="rise order {i}" style="flex:1;display:flex;flex-direction:row;gap:26px;align-items:center;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:8px 30px">'
             + num(i, RED, 32)
             + '<div style="flex:1;display:flex;flex-direction:column;gap:4px">' + p(f"font-family:{MONO};font-size:22px;font-weight:700;color:{INK};white-space:nowrap", e(q)) + p(f"font-size:22px;color:{SUB}", e(a_)) + '</div>'
             + p(f"width:300px;flex:none;{'font-family:' + MONO + ';font-size:22px;' if cmd.isascii() else 'font-size:24px;'}font-weight:700;line-height:1.5;color:{INK};background:#EEEFF2;padding:8px 18px;border-radius:12px;white-space:pre", e(cmd)) + '</div>')
o.append('</div>')
o.append(caption("오류가 안 나도 결과가 이상하면 몇 겹을 보고 있는지 따져 봐요.", 940))
W("trouble", o, "1번은 1파트의 word에 숫자 3을 물었을 때예요. 문자열 안에서는 글자만 찾을 수 있어서 \"3\"처럼 글자로 물어요. 2번과 3번은 2파트 오류 장에서 본 오류예요. 4번부터는 오류는 안 나지만 결과가 틀린 경우예요. 4번은 [[0] * 3] * 3으로 표를 만든 경우, 5번은 바깥 리스트에 안쪽 값을 물은 경우, 6번은 대소문자가 다른 경우예요. 1번 오류는 셀 [6]에서 3 in word를 실제로 실행한 결과예요. 나머지도 모두 hello-uv 커널에서 실제로 실행한 결과예요.", ("trouble", "정리"))

o = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>']
cheat = [('"latte" in menu', "들어 있으면 True", T1), ('"tea" not in menu', "없으면 True", T1), ('"th" in word', "붙어 있는 글자 조각 찾기", T1), ("a in xs and b in xs", "둘 다 들어 있는지", T1),
         ("scores[1][2]", "1행 2열 칸 꺼내기", T6), ("len(scores[0])", "열 수 세기", T6), ("for row in scores:", "한 행씩 꺼내기", T6), ("col.append(row[1])", "열 하나 모으기", T6)]
for i, (k, d, c) in enumerate(cheat):
    x, y = 96 + (i % 4) * 438, 200 + (i // 4) * 290
    o.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:414px;height:264px;background:{CARD};border:2px solid {LINE};border-top:10px solid {c};border-radius:20px;padding:28px 28px;display:flex;flex-direction:column;gap:20px">'
             + mono(k, 26, c, "#F6F5F1", "align-self:flex-start") + p(f"font-size:28px;font-weight:700;color:{INK}", d) + '</div>')
o.append(f'<div style="position:absolute;left:96px;top:780px;width:1728px;height:210px;background:{CARD};border:2px solid {LINE};border-radius:20px;padding:24px 36px;display:flex;flex-direction:column;justify-content:center;gap:14px">'
         + p(f"font-size:30px;font-weight:700;color:{INK}", 'in은 한 겹만 봐요. 안쪽은 <span style="font-family:\'JetBrains Mono\';color:' + T1 + '">[번호]</span>로 꺼낸 뒤 물어요')
         + p(f"font-size:30px;font-weight:700;color:{INK}", '<span style="font-family:\'JetBrains Mono\';color:' + T6 + '">[행][열]</span> 순서예요. 행 수는 len(scores), 열 수는 len(scores[0])') + '</div>')
W("cheatsheet", o, "이번 챕터에서 쓴 코드를 한 장에 모았어요. in과 not in은 True, False로 답하고, 바깥 한 겹만 본다는 것을 기억해요. 2차원 리스트는 앞 번호가 행, 뒤 번호가 열이에요. 노트북에 이 장의 내용을 마크다운 셀로 정리해 두면 복습할 때 같이 봐요. 다음에 배울 if 문은 in이 만든 True, False로 할 일을 고르는 문법이에요.")

# ---------- toc ----------
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
parts = [("Search", T1, "in과 not in", "리스트, 튜플, 문자열에서 들어 있는지 묻기, and와 or로 섞기, 한 겹만 보는 in", "in-list", "in-orders"),
         ("Database", T6, "2차원 리스트", "[행][열]로 꺼내기, len으로 행 수와 열 수, for로 행과 열 다루기, 성적표, 좌석표, 함정과 오류", "m-make", "m-err")]
TOC_NOTE = "두 파트는 앞 파트를 그대로 이어서 써요. 1파트는 in과 not in으로 값이 들어 있는지 묻는 법이에요. 2파트는 리스트 안에 리스트를 넣은 2차원 리스트로 표 모양 데이터를 다뤄요. 셀은 위에서부터 차례로 실행해요."

DECK_TITLE = "파이썬 기초 3 (in, 2차원 리스트)"
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

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-02T05:00:00Z"}, "lists": "css", "title": DECK_TITLE, "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
print(len(ORDER), "slides")
