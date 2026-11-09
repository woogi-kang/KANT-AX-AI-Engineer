"""Generates every slide of the __str__ and __repr__ deck (25) and slides/deck.json.

Story: picks up the Bread class from chapter 24. A 붕어빵 printed whole shows <__main__.Bread object at 0x...>, so the
deck draws the special methods Python looks up at set moments (__init__ when made, __str__ for print/str/f-string,
__repr__ for the last line of a cell and values inside a list). Part 2 builds __str__ and compares it with 24's intro().
Part 3 finds the places __str__ does not cover, links them to '팥' versus 팥, builds __repr__ in code form and shows
print borrowing __repr__ (len and + are shown read-only). Part 4 sorts a list of objects with key=lambda and changes
state with methods guarded by if. Part 5 collects the usual errors, and part 6 is a 붕어빵 stall and a cafe menu.
Every cell and output comes from tools/demo.sh (tools/run_nb.py runs the cells with the project kernel).

Layout rules (2026-11-08 remake, from the Stageshow skill and tools/DESIGN.md):
- one hero per slide: the notebook cell, drawn as large as the slide allows (26 to 40px code)
- terms sit beside the code line they explain as "← label" leader tags, not in separate cards
- say it once: what the speaker notes already say stays out of the slide; one caption at most
- a fix is the wrong line struck through next to the right line
- highlights vary by job (tools/HIGHLIGHT.md): line tint, fly, spotlight, pen ring, underline and box; no typing
Usage: python3 tools/gen.py slides
"""

import html, json, os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from highlight import spot, spot_off, ring, box, underline

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
INK, SUB, LINE, CARD, HAIR = "#1D2330", "#4A5262", "#E1DED6", "#FFFFFF", "#D9D5CB"
BL, GR, OR, PUR, RED, TEAL, GRAY = "#2459C9", "#1F8A4C", "#B26A00", "#5A3BB8", "#A33131", "#0F7C86", "#6A7180"
JP = "#B8560F"          # Jupyter, same as chapters 09 and 10
SEL = "#2F7DE1"         # selected cell bar, like VS Code's focus color
K1, K2, K3, K4, K5, K6 = "#1E5FA8", "#A0620A", TEAL, "#A23B72", RED, PUR
BR, MD, MDBG = "#9A5B13", "#5B4636", "#EFE8DF"      # 붕어빵 (object) and 틀 (class), as in 24
W_ = "#E6E9EF"
CS, CA, CM, CK = "#F2C48D", "#8FD8DE", "#B8E8BE", "#C7B8F2"   # self / argument / method name / keyword on dark code
REAL = " 출력은 실제로 실행한 결과예요."


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


def sec(sid, bg="#F6F5F1"):
    return f'<section id="{sid}" data-transition="fade" style="background:{bg};color:{INK};font-family:{SANS};font-variant-ligatures:none;word-break:keep-all;padding:96px;display:flex;flex-direction:column">'


def head(eyebrow, title, color):
    return [p(f"position:absolute;left:96px;top:48px;width:1728px;font-size:26px;font-weight:700;color:{color}", e(eyebrow), ' id="eyebrow"'),
            f'<h2 id="title" style="position:absolute;left:96px;top:92px;width:1728px;font-size:56px;font-weight:700;line-height:1.2;color:{INK}">{title}</h2>']


def caption(text, top=944, order=None):
    at = f' data-build-in="rise order {order}"' if order else ""
    return p(f"position:absolute;left:96px;top:{top}px;width:1728px;font-size:34px;font-weight:700;line-height:1.4;color:{INK}", text, ' id="caption"' + at)


def kbd(text, size=30):
    caps = [p(f"font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.2;white-space:nowrap;color:{INK};background:#FFFFFF;border:2px solid #C9CED8;border-bottom-width:5px;border-radius:10px;padding:6px 14px", e(k)) for k in text.split("+")]
    plus = p(f"font-size:{size * 0.8:.0f}px;font-weight:700;color:{GRAY}", "+")
    return '<div style="display:flex;flex-direction:row;align-items:center;gap:8px">' + plus.join(caps) + '</div>'


# ---------- notebook cell, drawn at a size chosen per slide ----------
def LH(fs):
    return fs * 1.45


def box_h(n, fs):
    """Height of the code box of a cell with n lines."""
    return 20 + n * LH(fs)


def cell(c, left, top, w, fs=30, sel=True, attrs="", out_attrs="", gut=True, box_w=None):
    """c: dict(id, lines, n, out, err, oids). The code text starts at x = left + 105, y = top + 10.
    Output lines sit right under the box with no gap between them. oids: ids for output lines (fly sources)."""
    lines, n, lh = c.get("lines", [""]), c.get("n"), LH(fs)
    o = [f'<div id="{c["id"]}"{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;display:flex;flex-direction:column;gap:10px">']
    bar = f'<div style="width:7px;flex:none;border-radius:4px;background:{SEL if sel else "transparent"}"></div>'
    gutter = p(f"width:58px;flex:none;font-family:{MONO};font-size:22px;color:{GRAY};text-align:right;padding-top:{8 + (lh - 30) / 2:.0f}px", (f"[{n}]" if n else "[ ]") if gut else "")
    txt = "".join(p(f"font-family:{MONO};font-size:{fs}px;line-height:1.45;white-space:pre;color:{INK}", e(l) if l else "&#160;") for l in lines)
    tag = p(f"position:absolute;right:14px;bottom:8px;font-size:18px;color:{GRAY}", "Python")
    bw = f"width:{box_w + 85}px;" if box_w else ""
    o.append(f'<div style="{bw}display:flex;flex-direction:row;gap:10px;align-items:stretch">{bar}{gutter}'
             f'<div style="flex:1;position:relative;background:#FFFFFF;border:2px solid {LINE};border-radius:10px;padding:8px 18px;display:flex;flex-direction:column">{txt}{tag}</div></div>')
    if c.get("out"):
        oids = c.get("oids", [])
        col = lambda l: RED if c.get("err") and re.match(r"[A-Za-z]+(Error|Interrupt)", l) else INK
        o.append(f'<div{out_attrs} style="display:flex;flex-direction:column">' + "".join(
            p(f"margin-left:85px;padding:0 20px;font-family:{MONO};font-size:{fs}px;line-height:1.45;white-space:pre;color:{col(l)}", e(l) if l else "&#160;", f' id="{oids[j]}"' if j < len(oids) and oids[j] else "")
            for j, l in enumerate(c["out"])) + '</div>')
    o.append('</div>')
    return o


def ly(top, i, fs=30):
    """Centre y of code line i of a cell drawn at top."""
    return top + 10 + i * LH(fs) + LH(fs) / 2


def oy(top, n, j, fs=30):
    """Centre y of output line j of a cell with n code lines."""
    return top + box_h(n, fs) + 10 + j * LH(fs) + LH(fs) / 2


def tw(s, fs=30):
    """Drawn width of a code string: Hangul is one em wide, everything else 0.6 em (JetBrains Mono)."""
    return sum(fs * (1.0 if '가' <= ch <= '힣' else 0.6) for ch in s)


def cx(left, s, fs=30):
    """x where the code string s starts... or ends: left + 105 + width of s."""
    return left + 105 + tw(s, fs)


def hl(left, top, w, i, n=1, kind="run", order=1, fs=30):
    """Tints code lines i..i+n-1. Colors: green run, gray skip, red error, blue mark."""
    tint = {"run": "rgba(31,138,76,0.16)", "skip": "rgba(106,113,128,0.18)", "err": "rgba(163,49,49,0.14)", "mark": "rgba(36,89,201,0.13)"}[kind]
    at = f' data-build-in="fade order {order}"' if order else ""
    return f'<div{at} style="position:absolute;left:{left + 87}px;top:{top + 10 + i * LH(fs):.0f}px;width:{w - 89}px;height:{n * LH(fs):.0f}px;background:{tint};border-radius:6px"></div>'


def tag(x, y, text, color, order=None, size=28, anim="fade", lead=True):
    """A leader label: '← text', centred on y, no box."""
    at = f' data-build-in="{anim} order {order}"' if order else ""
    return p(f"position:absolute;left:{x:.0f}px;top:{y - size * 0.725:.0f}px;font-size:{size}px;font-weight:700;line-height:1.45;color:{color};white-space:nowrap",
             ("← " if lead else "") + e(text), at)


def anchor(sid, x, y, w, h):
    """An invisible box that a flying element starts from."""
    return f'<div id="{sid}" style="position:absolute;left:{x:.0f}px;top:{y:.0f}px;width:{w:.0f}px;height:{h:.0f}px"></div>'


def arrow(w=70, color="#C9CED8"):
    return f'<x-shape kind="arrow-right" style="width:{w}px;height:30px;flex:none;background:{color}"></x-shape>'


def fix(left, top, bad, good, order, size=30):
    """The wrong line struck through, an arrow, the right line."""
    return (f'<div data-build-in="rise order {order}" style="position:absolute;left:{left}px;top:{top}px;width:1728px;display:flex;flex-direction:row;align-items:center;gap:22px">'
            + p(f"font-size:{size}px;font-weight:900;color:{RED}", "✕")
            + p(f"font-family:{MONO};font-size:{size}px;font-weight:700;color:{RED};text-decoration:line-through;text-decoration-thickness:3px;white-space:pre", e(bad))
            + arrow()
            + p(f"font-size:{size}px;font-weight:900;color:{GR}", "✓")
            + p(f"font-family:{MONO};font-size:{size}px;font-weight:700;color:{INK};background:#E6F4EC;border:3px solid {GR};border-radius:14px;padding:6px 20px;white-space:pre", e(good)) + '</div>')


def is_code(c):
    return c.isascii() or re.search(r'[A-Za-z_]\.|[\[\]"=(]', c) is not None


def plain_rows(left, top, w, rows, widths, order0=None, rh=78, head_=None, fs=28, row_attrs=None):
    """A light table: gray header over a dark rule, rows split by hairlines, no boxes.
    Returns the parts and the y of each row (for spotlights)."""
    o, ys, y = [], [], top
    if head_:
        o.append(f'<div style="position:absolute;left:{left}px;top:{y}px;width:{w}px;height:48px;display:flex;flex-direction:row;align-items:center;gap:20px;border-bottom:3px solid {INK}">'
                 + "".join(p(f"width:{cw}px;flex:none;font-size:24px;font-weight:700;color:{GRAY}", e(c)) for c, cw in zip(head_, widths)) + '</div>')
        y += 48
    for i, r in enumerate(rows):
        at = f' data-build-in="rise order {order0 + i}"' if order0 else ""
        at += (row_attrs[i] if row_attrs else "")
        inner = "".join(p(f"width:{cw}px;flex:none;font-family:{MONO if is_code(c) else SANS};font-size:{fs}px;font-weight:700;line-height:1.3;color:{INK};white-space:pre", e(c)) for c, cw in zip(r, widths))
        o.append(f'<div{at} style="position:absolute;left:{left}px;top:{y}px;width:{w}px;height:{rh}px;display:flex;flex-direction:row;align-items:center;gap:20px;border-bottom:2px solid {HAIR}">{inner}</div>')
        ys.append(y)
        y += rh
    return o, ys


def seg(parts, size=40):
    return p(f"font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.5;color:{W_};white-space:pre",
             "".join(f'<span style="color:{c}">{e(t)}</span>' for t, c in parts))


EB1, EB2, EB3, EB4, EB5, EB6 = "1. 왜 필요한가", "2. __str__", "3. __repr__", "4. 붕어빵 여러 개 다루기", "5. 오류와 함정", "6. 실습"
B_INIT = ["class Bread:", "    def __init__(self, flavor, price):", "        self.flavor = flavor", "        self.price = price"]
B_STR = ["    def __str__(self):", '        return f"{self.flavor} 붕어빵 {self.price:,}원"']
B_REPR = ["    def __repr__(self):", "        return f\"Bread('{self.flavor}', {self.price})\""]
AB = ['a = Bread("팥", 1000)', 'b = Bread("슈크림", 1200)']
ADDR = "0x7f6735bb38c0"


def widest(lines, fs):
    return max(tw(l, fs) for l in lines)


# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       f'<p style="font-size:28px;font-weight:700;color:#F2B27A;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
       f'<h1 style="font-size:84px;font-weight:900;line-height:1.1;color:#F6F5F1">클래스 2<br>__str__과<br>__repr__</h1>',
       f'<p style="font-size:40px;line-height:1.4;color:#BFC6D4">print했을 때<br>붕어빵이 보이게 만들기</p>',
       '<div style="position:absolute;left:900px;top:300px;width:900px;height:480px;background:#252B36;border-radius:24px;padding:44px 48px;display:flex;flex-direction:column;justify-content:center;gap:16px">']
for line, c in [("class Bread:", CK), ("    def __str__(self):", W_), ('        return "팥 붕어빵 1,000원"', CS), ("", W_),
                ("print(a)", CA), ("# 팥 붕어빵 1,000원", "#9AA1AE"), ("# (전에는 <__main__.Bread object at ...>)", "#9AA1AE")]:
    cov.append(p(f"font-family:{MONO};font-size:30px;font-weight:700;line-height:1.45;color:{c};white-space:pre", e(line) if line else "&#160;"))
cov.append('</div>')
W("cover", cov, "24에서 붕어빵 틀을 만들었어요. 그런데 붕어빵을 통째로 print하면 꺾쇠괄호 안에 낯선 글자가 나왔어요. 이번 챕터는 그 글자를 우리가 원하는 글자로 바꿔요. 파이썬이 정해진 순간에 알아서 부르는 메서드 두 개, __str__과 __repr__을 배워요. 왜 필요한지, 언제 불리는지, 둘이 어떻게 다른지를 차례로 봐요. 그다음 붕어빵을 여러 개 담아 정렬하고, 판매할 때마다 재고가 줄어드는 노점을 만들어요.", ("intro", "들어가기"))
ORDER.append("toc")

# ---------- ready: a plain checklist and the four steps, no cards ----------
o = [sec("ready")] + head("들어가기", "24에서 이어서 해요", JP)
rows_, _ = plain_rows(96, 196, 780, [("class, __init__, self", "24"), ("메서드와 a.intro()", "24"), ("f-string과 칸 맞추기", "13"), ("return과 print의 차이", "19"), ("sorted와 key=lambda", "22")],
                      [620, 100], head_=["이번에 다시 쓰는 것", "챕터"], rh=96, fs=30)
o += rows_
o.append(p(f"position:absolute;left:1000px;top:196px;font-size:24px;font-weight:700;color:{GRAY}", "노트북 다시 열기"))
for i, part in enumerate([p(f"font-size:32px;color:{INK}", "VS Code로 hello-uv 폴더 열기"),
                          p(f"font-size:32px;color:{INK}", "탐색기에서") + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{JP}", "basics.ipynb") + p(f"font-size:32px;color:{INK}", "열기"),
                          p(f"font-size:32px;color:{INK}", "오른쪽 위 커널이 .venv인지 보기"),
                          p(f"font-size:32px;color:{INK}", "셀에 적고") + kbd("Shift+Enter", 28) + p(f"font-size:32px;color:{INK}", "로 실행")]):
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:1000px;top:{262 + i * 112}px;width:824px;height:80px;display:flex;flex-direction:row;align-items:center;gap:20px">'
             + p(f"width:56px;height:56px;flex:none;border-radius:50%;background:{JP};color:#FFFFFF;font-size:30px;font-weight:900;line-height:56px;text-align:center", str(i + 1)) + part + '</div>')
W("ready", o, "09에서 만든 hello-uv 폴더를 VS Code로 열고, basics.ipynb를 다시 열어요. 24의 Bread 틀에서 이어서 해요. 왼쪽 목록 오른쪽 숫자는 그 내용을 배운 챕터예요. 기억이 안 나면 그 챕터를 먼저 다시 봐요. 이번 챕터의 두 메서드는 글자를 return해야 해요. 19의 return과 print의 차이를 떠올려 두세요. 4파트에서는 22의 sorted와 key=lambda를 써요. 슬라이드의 출력은 tools/demo.sh가 hello-uv 커널에서 같은 셀을 실제로 실행한 결과예요. 0x로 시작하는 주소는 실행할 때마다 달라져요.")

# ---------- part 1 ----------
o = [sec("w-why")] + head(EB1, "숫자와 리스트는 잘 보이는데, 붕어빵은 안 보여요", K1)
c1 = {"id": "c-w1", "lines": ["print(3)", 'print("팥")', "print([1, 2])"], "n": 1, "out": ["3", "팥", "[1, 2]"]}
o += cell(c1, 96, 196, 760, 30, sel=False)
o.append(tag(500, oy(196, 3, 1), "넣은 그대로 보여요", GR))
c2 = {"id": "c-w2", "lines": B_INIT + [""] + AB + ["print(a)", "print([a, b])"], "n": 2, "err": False,
      "out": [f"<__main__.Bread object at {ADDR}>", "[<__main__.Bread object at 0x7f6735bb38c0>, <__main__.Bread object at 0x7f6735dc4a50>]"]}
o += cell(c2, 96, 500, 1728, 28, attrs=' data-build-in="rise order 1"', box_w=900)
y0 = oy(500, 9, 0, 28)
o.append(underline(2, 201, int(cx(96, c2["out"][0], 28)), int(y0 + 17), RED))
o.append(tag(cx(96, c2["out"][0], 28) + 40, y0, "Bread는 우리가 만든 틀이라 파이썬이 몰라요", RED, 2))
W("w-why", o, "24의 마지막 오류 장면에서 시작해요. 숫자, 글자, 리스트를 print하면 우리가 넣은 그대로 보여요. 그런데 우리가 만든 붕어빵을 print하면 꺾쇠괄호 안에 낯선 글자가 나와요. 리스트에 담아 찍어도 마찬가지예요. int, str, list는 파이썬이 만든 틀이라 어떻게 보여 줄지 이미 정해져 있어요. Bread는 우리가 오늘 만든 틀이라 파이썬이 보여 주는 법을 몰라요. 그래서 틀에 보여 주는 법을 적어 줘야 해요. 주소는 실행할 때마다 달라요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p1", "왜 필요한가"))

# w-big: the class is the hero; each trigger on the left draws a line to the method Python looks for
o = [sec("w-big")] + head(EB1, "정해진 순간에 파이썬이 틀에서 찾아 부르는 메서드", K1)
MX, MW = 1250, 574
o.append(f'<div style="position:absolute;left:{MX}px;top:196px;width:{MW}px;height:720px;background:{MDBG};border:6px dashed {MD};border-radius:30px"></div>')
o.append(f'<div style="position:absolute;left:{MX + 36}px;top:222px;display:flex;flex-direction:row;align-items:center;gap:14px">'
         + p(f"font-size:22px;font-weight:700;color:#FFFFFF;background:{MD};border-radius:10px;padding:4px 14px", "틀") + p(f"font-family:{MONO};font-size:34px;font-weight:700;color:{MD}", "class Bread") + '</div>')
METH = [("__init__", 340, BR), ("__str__", 480, BR), ("__repr__", 655, BR), ("intro", 810, GRAY)]
for name, y, c in METH:
    o.append(p(f"position:absolute;left:{MX + 60}px;top:{y - 32}px;font-family:{MONO};font-size:44px;font-weight:700;line-height:64px;color:{c}", e(name)))
TRIG = [('Bread("팥", 1000)', 340, 340, K3, 1), ("print(a)", 480, 480, K2, 2), ("셀 마지막 줄의 a", 600, 655, K3, 3), ("print([a, b])", 710, 655, K3, 4), ("a.intro()", 810, 810, GRAY, 5)]
svg = []
x0 = 600
for text, y, ty, c, k in TRIG:
    o.append(p(f"position:absolute;left:96px;top:{y - 30}px;font-family:{MONO if is_code(text) else SANS};font-size:36px;font-weight:700;line-height:60px;color:{INK};white-space:nowrap", e(text), f' data-build-in="fade order {k}"'))
    svg.append((k, f'<circle cx="{MX - 14}" cy="{ty}" r="7" fill="{c}" stroke="none"/>', c))
    svg.append((k, f'<path d="M{x0},{y} C{x0 + 220},{y} {MX - 260},{ty} {MX - 20},{ty}"/>', c))
for k, d, c in svg:
    o.append(f'<svg data-build-in="draw order {k}" viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible">'
             f'<g fill="none" stroke="{c}" stroke-width="5" stroke-linecap="round">{d}</g></svg>')
o.append(p(f"position:absolute;left:{MX + 60}px;top:{810 + 38}px;font-size:24px;font-weight:700;color:{GRAY}", "우리가 이름 지은 메서드라 우리가 불러요", ' data-build-in="fade order 5"'))
o.append(caption("앞뒤 밑줄 두 개는 파이썬과 약속한 이름이에요. 틀에 없으면 기본 모양을 써요.", 950, 6))
W("w-big", o, "큰 그림을 봐요. 틀 안의 메서드 중에 앞뒤로 밑줄이 두 개씩 붙은 것들은 파이썬과 약속한 이름이에요. 24의 __init__이 그랬어요. 찍는 순간 파이썬이 틀에서 __init__을 찾아 불렀어요. 마찬가지로 print할 때는 __str__을, 셀 마지막 줄이나 리스트 안에서 보여 줄 때는 __repr__을 찾아요. 우리는 이 메서드를 직접 부르지 않고, 이름만 맞게 적어 둬요. 틀에 없으면 파이썬은 앞 장에서 본 기본 모양을 써요. intro처럼 우리가 이름을 지은 메서드는 우리가 직접 불러야 해요.")

# w-min: the returned text flies from the return line to the output
o = [sec("w-min")] + head(EB1, "가장 짧은 __str__: 글자 하나를 돌려주기", K1)
FS = 36
cm = {"id": "c-w3", "lines": B_INIT + ["", "    def __str__(self):", '        return "붕어빵이에요"', "", 'a = Bread("팥", 1000)', "print(a)"], "n": 3, "out": ["붕어빵이에요"]}
o += cell(cm, 96, 196, 1000, FS, out_attrs=' data-build-in="fly order 2" data-from="w-min-ret"')
o.append(hl(96, 196, 1000, 5, 2, "run", 1, FS))
rx = cx(96, '        return ', FS)
o.append(anchor("w-min-ret", rx, ly(196, 6, FS) - 24, tw('"붕어빵이에요"', FS), 48))
o.append(tag(1130, ly(196, 6, FS), "print하지 않고 return해요", GR, 1))
o.append(tag(cx(96, "붕어빵이에요", FS) + 40, oy(196, 10, 0, FS), "__str__이 돌려준 글자를 print가 찍어요", K1, 3))
W("w-min", o, "가장 짧은 __str__을 만들어요. 틀 안에 def __str__(self)를 적고 글자 하나를 return했어요. print(a)를 쳤더니 낯선 글자 대신 붕어빵이에요가 나왔어요. print가 a를 찍기 전에 a의 틀에서 __str__을 찾아 부르고, 돌려받은 글자를 찍은 거예요. __str__ 안에서 print하지 않고 return해요. 19에서 배운 것처럼 return한 글자를 print가 받아서 찍어요. 지금은 어떤 붕어빵이든 같은 글자가 나와요. 다음 파트에서 맛과 가격이 들어가게 바꿔요." + REAL)

# ---------- part 2 ----------
o = [sec("s-basic")] + head(EB2, "__str__에 self의 값을 넣어 붕어빵마다 다르게", K2)
FS = 32
cs = {"id": "c-s1", "lines": B_INIT + [""] + B_STR + [""] + AB + ["print(a)", "print(b)"], "n": 1, "out": ["팥 붕어빵 1,000원", "슈크림 붕어빵 1,200원"]}
o += cell(cs, 96, 196, 1220, FS)
o.append(hl(96, 196, 1220, 5, 2, "run", 1, FS))
o.append(tag(1350, ly(196, 6, FS), "손님에게 보여 줄 메뉴판 글씨", K2, 1))
pre = '        return f"'
y6 = ly(196, 6, FS) + 22
x1 = cx(96, pre, FS)
o.append(underline(2, int(x1), int(x1 + tw("{self.flavor}", FS)), int(y6), OR))
x2 = cx(96, pre + "{self.flavor} 붕어빵 ", FS)
o.append(underline(2, int(x2), int(x2 + tw("{self.price:,}", FS)), int(y6), OR))
o.append(tag(cx(96, "슈크림 붕어빵 1,200원", FS) + 50, oy(196, 12, 0, FS), "print(a): self가 a", K2, 3))
o.append(tag(cx(96, "슈크림 붕어빵 1,200원", FS) + 50, oy(196, 12, 1, FS), "print(b): self가 b", K2, 3))
W("s-basic", o, "__str__ 안에서 self를 쓰면 붕어빵마다 다른 글자를 돌려줄 수 있어요. 13의 f-string에 self.flavor와 self.price를 넣고, 가격에는 천 단위 콤마를 붙였어요. print(a)에서는 self가 a라서 팥 붕어빵 1,000원이, print(b)에서는 슈크림 붕어빵 1,200원이 나와요. __str__은 손님에게 보여 주는 메뉴판 글씨라고 생각하면 돼요. 사람이 읽기 좋은 글자로 적어요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p2", "__str__"))

o = [sec("s-where")] + head(EB2, "print 말고도 글자가 필요한 곳에서 불려요", K2)
FS = 34
c2a = {"id": "c-s2", "lines": ["print(str(a))", 'print(f"주문: {a}")', 'print("오늘의 빵:", b)'], "n": 2, "out": ["팥 붕어빵 1,000원", "주문: 팥 붕어빵 1,000원", "오늘의 빵: 슈크림 붕어빵 1,200원"]}
o += cell(c2a, 96, 196, 1000, FS)
TX = 1160
for i, t in enumerate(["12의 타입 바꾸기 str()에 넣어도", "f-string 중괄호 안에 넣어도", "print에 쉼표로 넘겨도"]):
    o.append(tag(TX, ly(196, i, FS), t, K2, i + 1))
c3a = {"id": "c-s3", "lines": ['msg = "포장할게요: " + str(a)', "print(msg)"], "n": 3, "out": ["포장할게요: 팥 붕어빵 1,000원"]}
T3 = 600
o += cell(c3a, 96, T3, 1000, FS, attrs=' data-build-in="rise order 4"')
o.append(tag(TX, ly(T3, 0, FS), "바꾼 글자는 더하기로 이을 수 있어요", K2, 4))
o.append(caption("파이썬이 붕어빵을 글자로 바꿔야 할 때마다 __str__을 불러요.", 920, 5))
W("s-where", o, "__str__은 print할 때만 불리는 게 아니에요. 12에서 숫자를 글자로 바꾸던 str()에 붕어빵을 넣어도, f-string 중괄호 안에 넣어도, print에 쉼표로 여러 개를 넘겨도 불려요. 공통점은 파이썬이 붕어빵을 글자로 바꿔야 하는 순간이라는 거예요. str(a)로 바꾼 글자는 더하기로 다른 글자와 이을 수도 있어요." + REAL)

o = [sec("s-intro")] + head(EB2, "intro는 우리가 부르고, __str__은 파이썬이 불러요", K2)
FS = 30
for k, (lbl, col, lines) in enumerate([("24의 intro", GRAY, ["    def intro(self):", '        print(self.flavor, "붕어빵")', "", "a.intro()", "print(a)   # 여전히 <... object>"]),
                                       ("__str__", K2, ["    def __str__(self):", '        return f"{self.flavor} 붕어빵"', "", "print(a)", 'f"주문: {a}"'])]):
    left = 96 + k * 882
    o.append(p(f"position:absolute;left:{left + 105}px;top:196px;font-family:{MONO};font-size:28px;font-weight:700;color:{col}", e(lbl)))
    o += cell({"id": f"c-si{k}", "lines": lines}, left, 246, 846, FS, sel=False, gut=False)
y4 = ly(246, 4, FS)
xu = 96 + 105 + int(tw("print(a)   ", FS))
o.append(underline(1, xu, xu + int(tw("# 여전히 <... object>", FS)), int(y4 + 19), RED))
rows_, _ = plain_rows(96, 560, 1728, [["누가 부르나요", "우리가 a.intro()로", "print, str, f-string이 알아서"],
                                      ["무엇을 하나요", "안에서 바로 print", "글자를 return"],
                                      ["다른 글자와 잇기", "안 돼요", "f-string, 더하기로 이어요"]],
                      [300, 680, 680], order0=2, rh=96, head_=["", "intro", "__str__"], fs=30)
o += rows_
W("s-intro", o, "24에서 만든 intro도 붕어빵을 소개했어요. 그런데 __str__을 쓰는 이유가 있어요. intro는 우리가 직접 a.intro()로 불러야 하고, 안에서 바로 print해 버려요. 그래서 print(a)는 여전히 낯선 글자가 나오고, 소개 글자를 주문서나 영수증에 이어 붙일 수도 없어요. __str__은 print, str, f-string이 알아서 부르고 글자를 돌려줘요. 돌려받은 글자는 어디에든 다시 쓸 수 있어요. 파이썬이 원래 쓰던 방법에 우리 붕어빵이 끼어드는 거예요.")

# ---------- part 3 ----------
o = [sec("r-cell")] + head(EB3, "__str__을 만들었는데도 낯선 글자가 남아요", K3)
FS = 30
cr = {"id": "c-r1", "lines": B_INIT + [""] + B_STR + [""] + AB + ["a"], "n": 1, "out": ["<__main__.Bread at 0x7febaa53c6e0>"]}
o += cell(cr, 96, 196, 1240, FS)
o.append(hl(96, 196, 1240, 10, 1, "mark", 1, FS))
o.append(tag(cx(96, "a", FS) + 40, ly(196, 10, FS), "print 없이 셀 마지막 줄에 이름만", BL, 1))
yo = oy(196, 11, 0, FS)
o.append(box(2, 193, int(yo - 22), int(tw(cr["out"][0], FS)) + 16, 44, RED))
o.append(tag(cx(96, cr["out"][0], FS) + 60, yo, "__str__을 쓰지 않아요", RED, 2))
T2 = 800
cr2 = {"id": "c-r2", "lines": ["print([a, b])"], "n": 2, "out": ["[<__main__.Bread object at 0x7febaa53c6e0>, <__main__.Bread object at 0x7febaa7fb890>]"]}
o += cell(cr2, 96, T2, 1728, FS, attrs=' data-build-in="rise order 3"', box_w=1155)
o.append(tag(cx(96, "print([a, b])", FS) + 40, ly(T2, 0, FS), "리스트 안의 붕어빵도 __str__을 쓰지 않아요", RED, 3))
o.append(underline(4, 201, int(cx(96, cr2["out"][0], FS)), int(oy(T2, 1, 0, FS) + 20), RED))
W("r-cell", o, "__str__을 만들었는데도 낯선 글자가 남는 곳이 두 군데 있어요. 하나는 셀 마지막 줄에 print 없이 이름만 적었을 때예요. 10에서 배운 대로 셀 마지막 줄의 값은 저절로 보이는데, 이때는 __str__이 아닌 다른 메서드를 써요. 노트북은 object라는 말을 빼고 보여 줘서 모양이 조금 달라요. 다른 하나는 붕어빵을 리스트에 담아 print했을 때예요. 리스트는 __str__로 찍지만, 리스트 안의 값은 __repr__이라는 메서드로 보여 줘요. 다음 장에서 이 차이를 이미 본 적이 있다는 걸 확인해요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p3", "__repr__"))

# r-known: the big 팥 and '팥' fly out of the outputs they came from
o = [sec("r-known")] + head(EB3, "이 차이는 \"팥\"에서 이미 봤어요", K3)
FS = 32
o += cell({"id": "c-r3", "lines": ['"팥"'], "n": 3, "out": ["'팥'"], "oids": ["rk-repr"]}, 96, 196, 820, FS)
o += cell({"id": "c-r4", "lines": ['print("팥")', 'print(["팥", "슈크림"])', 'print(str("팥"))', 'print(repr("팥"))'], "n": 4,
           "out": ["팥", "['팥', '슈크림']", "팥", "'팥'"], "oids": ["rk-str"]}, 96, 400, 820, FS)
o.append(f'<div style="position:absolute;left:1370px;top:220px;width:3px;height:600px;background:{HAIR}"></div>')
for k, (lbl, big, sub, col, src) in enumerate([("str  손님용", "팥", "print, str()", K2, "rk-str"), ("repr  만든 사람용", "'팥'", "셀 마지막 줄, 리스트 안, repr()", K3, "rk-repr")]):
    x = 1000 + k * 430
    o.append(p(f"position:absolute;left:{x}px;top:220px;width:400px;font-size:30px;font-weight:700;color:{col}", e(lbl), f' data-build-in="fade order {k + 1}"'))
    o.append(p(f"position:absolute;left:{x}px;top:300px;font-family:{MONO};font-size:150px;font-weight:700;line-height:1.2;color:{INK};white-space:pre", e(big), f' data-build-in="fly order {k + 1}" data-from="{src}"'))
    o.append(p(f"position:absolute;left:{x}px;top:520px;width:{400 if k == 0 else 394}px;font-size:26px;line-height:1.45;color:{SUB}", e(sub), f' data-build-in="fade order {k + 1}"'))
o.append(ring(3, 1430, 318, int(tw("'팥'", 150)) - 10, 150, TEAL))
o.append(caption("글자라는 게 보이게 따옴표까지 붙이는 쪽이 repr이에요.", 920, 3))
W("r-known", o, "str과 repr의 차이는 이미 본 적이 있어요. 셀 마지막 줄에 팥을 적으면 따옴표가 붙은 팥이 나왔어요. print하면 따옴표 없이 팥만 나와요. 13에서 리스트를 찍었을 때 안의 글자마다 따옴표가 붙어 있던 것도 같은 이유예요. 파이썬은 글자를 보여 주는 방법을 두 가지 갖고 있어요. 손님에게 보여 주는 str은 따옴표 없이, 만든 사람이 보는 repr은 글자라는 게 보이게 따옴표까지 붙여요. str()과 repr() 함수로 직접 확인할 수도 있어요. 붕어빵의 __str__과 __repr__이 바로 이 두 방법이에요." + REAL)

o = [sec("r-basic")] + head(EB3, "__repr__까지 만들면 어디서나 보여요", K3)
FS = 26
c5 = {"id": "c-r5", "lines": B_INIT + [""] + B_STR + [""] + B_REPR + [""] + AB + ["a"], "n": 5, "out": ["Bread('팥', 1000)"]}
o += cell(c5, 96, 196, 1100, FS)
o.append(hl(96, 196, 1100, 8, 2, "run", 1, FS))
o.append(tag(1240, ly(196, 8.5, FS), "만든 사람이 보는 주문표 글씨", K3, 1))
o.append(tag(1240, ly(196, 8.5, FS) + 44, "다시 찍는 코드 모양으로 적어요", K3, 1, size=24, lead=False))
yo = oy(196, 14, 0, FS)
o.append(box(2, 186, int(yo - 22), int(tw(c5["out"][0], FS)) + 30, 44, TEAL))
o.append(tag(cx(96, c5["out"][0], FS) + 50, yo, "셀 마지막 줄도 이제 보여요", K3, 2))
T6 = 812
c6 = {"id": "c-r6", "lines": ["print(a)", "print([a, b])"], "n": 6, "out": ["팥 붕어빵 1,000원", "[Bread('팥', 1000), Bread('슈크림', 1200)]"]}
o += cell(c6, 96, T6, 1728, FS, attrs=' data-build-in="rise order 3"', box_w=1015)
ox = cx(96, c6["out"][1], FS) + 50
o.append(tag(ox, oy(T6, 2, 0, FS), "print는 여전히 __str__", K2, 4, size=26))
o.append(tag(ox, oy(T6, 2, 1, FS), "리스트 안은 __repr__", K3, 4, size=26))
W("r-basic", o, "__repr__을 더 만들어요. __repr__은 만든 사람이 보는 주문표 글씨예요. 보통 그 붕어빵을 다시 찍는 코드 모양으로 적어요. Bread('팥', 1000)을 그대로 복사해서 셀에 붙여 넣으면 같은 붕어빵이 다시 만들어져요. 맛 글자에는 따옴표를 직접 넣었어요. 이제 셀 마지막 줄에서도, 리스트 안에서도 낯선 글자 대신 Bread('팥', 1000)이 보여요. print(a)는 여전히 __str__의 메뉴판 글씨를 써요." + REAL)

# r-who: a plain table; the spotlight walks down the rows
o = [sec("r-who")] + head(EB3, "print는 __str__, 셀과 리스트 안은 __repr__을 찾아요", K3)
CW = [500, 380, 400, 388]
rows_, ys = plain_rows(96, 196, 1728, [['Bread("팥", 1000)', "__init__", "찍기", "재료 없이 찍기"],
                                       ["print(a), str(a), f\"{a}\"", "__str__", "팥 붕어빵 1,000원", "<... object at 0x...>"],
                                       ["셀 마지막 줄의 a", "__repr__", "Bread('팥', 1000)", "<... at 0x...>"],
                                       ["print([a, b])", "안의 값은 __repr__", "[Bread('팥', 1000), ...]", "[<... object ...>, ...]"],
                                       ["a.intro()", "우리가 부른 것", "우리가 부를 때만", "AttributeError"]],
                       CW, rh=104, head_=["이렇게 쓰면", "불리는 메서드", "둘 다 있을 때", "아무것도 없을 때"], fs=27)
o += rows_
for i, y in enumerate(ys):
    o.append(spot(i + 1, 96, y, 1728, 104, pad=6, r=12))
o.append(spot_off(6))
o.append(caption("손님에게 보여 줄 땐 __str__, 무엇이 들었는지 확인할 땐 __repr__이에요.", 840, 6))
W("r-who", o, "세 메서드가 언제 불리는지 표로 모았어요. 한 줄씩 짚어 가며 봐요. 찍을 때는 __init__, print와 str과 f-string은 __str__, 셀 마지막 줄과 리스트 안의 값은 __repr__이에요. 오른쪽 두 칸은 메서드가 있을 때와 없을 때 무엇이 보이는지예요. intro처럼 우리가 이름을 지은 메서드는 우리가 부를 때만 실행돼요. 손님에게 보여 줄 땐 __str__, 개발하면서 무엇이 들었는지 확인할 땐 __repr__이라고 기억하면 돼요.")

# ---------- 누가 불릴까: a slide students press in the browser (tools/lab_who.js) ----------
LW_CSS = ("<style>"
          "#r-lab button{font-family:" + SANS.replace("'", '"') + ";font-size:26px;font-weight:700;border-radius:14px;padding:10px 20px;cursor:pointer;border:3px solid #C9CED8;background:#FFFFFF;color:#1D2330}"
          "#r-lab button:disabled{opacity:.5;cursor:default}"
          "#r-lab #lw-asks button{font-family:" + MONO.replace("'", '"') + ";font-size:26px;height:64px}"
          "#r-lab #lw-asks button.lw-on{border-color:#0F7C86;background:#E2F2F3}"
          "#r-lab .lw-tg{background:#1F8A4C;border-color:#1F8A4C;color:#FFFFFF}"
          "#r-lab .lw-tg.lw-off{background:#FFFFFF;border-color:#C9CED8;color:#6A7180}"
          "#r-lab [data-st]{transition:all .3s}"
          "#r-lab [data-st=look]{border-color:#B26A00!important;background:#FFF4E0!important;transform:scale(1.06)}"
          "#r-lab [data-st=yes]{border-color:#1F8A4C!important;background:#E3F3E8!important}"
          "#r-lab [data-st=no]{border-color:#A33131!important;background:#F8E6E6!important;opacity:.8}"
          "#r-lab [data-st=skip]{opacity:.35;border-style:dashed!important}"
          "#r-lab #lw-out{transition:opacity .25s}"
          "</style>")


def cl(txt, sid=None, fs=25):
    idp = f' id="{sid}"' if sid else ""
    return p(f"height:50px;font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:50px;color:{W_};white-space:pre", txt, idp)


def sp(t, c):
    return f'<span style="color:{c}">{e(t)}</span>'


def lbl(x, y, t, c=GRAY):
    return p(f"position:absolute;left:{x}px;top:{y}px;font-size:24px;font-weight:700;color:{c}", e(t))


o = [sec("r-lab"), LW_CSS] + head(EB3, "눌러 보기: 지금 누가 불릴까요", K3)
o.append('<div style="position:absolute;left:96px;top:196px;width:900px;height:520px;background:#252B36;border-radius:22px;padding:30px 34px">'
         + cl(sp("class", CK) + " Bread:")
         + cl("    " + sp("def", CK) + " " + sp("__init__", CM) + "(" + sp("self", CS) + ", flavor, price): ...")
         + '<div id="lw-str" style="border-radius:10px;transition:all .3s">'
         + cl("    " + sp("def", CK) + " " + sp("__str__", CM) + "(" + sp("self", CS) + "):")
         + cl("        " + sp("return", CK) + " " + sp('f"{self.flavor} 붕어빵 {self.price:,}원"', CA)) + '</div>'
         + '<div id="lw-repr" style="border-radius:10px;transition:all .3s">'
         + cl("    " + sp("def", CK) + " " + sp("__repr__", CM) + "(" + sp("self", CS) + "):")
         + cl("        " + sp("return", CK) + " " + sp("f\"Bread('{self.flavor}', {self.price})\"", CA)) + '</div>'
         + cl("&#160;") + cl(sp("a", CS) + ' = Bread("팥", 1000)') + cl(sp("b", CS) + ' = Bread("슈크림", 1200)') + '</div>')
o.append('<div style="position:absolute;left:96px;top:744px;width:860px;display:flex;flex-direction:row;gap:16px;align-items:center">'
         + p(f"font-size:26px;font-weight:700;color:{SUB}", "틀에")
         + '<button class="lw-tg">__str__ <span id="lw-t-str">있음</span></button><button class="lw-tg">__repr__ <span id="lw-t-repr">있음</span></button>'
         + p(f"font-size:24px;color:{GRAY}", "눌러서 빼기, 다시 넣기") + '</div>')
RX = 1040
o.append(lbl(RX, 196, "① 이렇게 보여 달라고 하면", K3))
o.append(f'<div id="lw-asks" style="position:absolute;left:{RX}px;top:240px;width:784px;display:grid;grid-template-columns:1fr 1fr;gap:14px">'
         + '<button data-k="print">print(a)</button><button data-k="fstr">f"주문: {a}"</button>'
         + '<button data-k="cell">셀 마지막 줄 a</button><button data-k="list">print([a, b])</button></div>')
o.append(lbl(RX, 430, "② 파이썬이 틀에서 찾는 순서", K3))
lane_ = ""
for i, (k, t) in enumerate([("str", "__str__"), ("repr", "__repr__"), ("base", "기본 모양")]):
    if i:
        lane_ += '<x-shape kind="arrow-right" style="width:40px;height:26px;background:#C9CED8"></x-shape>'
    lane_ += (f'<div id="lw-l-{k}" data-st="idle" style="width:216px;height:116px;flex:none;background:{CARD};border:3px solid {LINE};border-radius:18px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px">'
              + p(f"font-family:{MONO if k != 'base' else SANS};font-size:30px;font-weight:700;color:{INK}", e(t))
              + p(f"height:30px;font-size:22px;font-weight:700;color:{SUB}", "", f' id="lw-s-{k}"') + '</div>')
o.append(f'<div style="position:absolute;left:{RX}px;top:474px;width:784px;display:flex;flex-direction:row;align-items:center;gap:12px">{lane_}</div>')
o.append(lbl(RX, 640, "③ 출력", JP))
o.append(f'<div style="position:absolute;left:{RX}px;top:684px;width:784px;height:64px;border-bottom:3px solid {HAIR};display:flex;flex-direction:row;gap:16px;align-items:baseline">'
         + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{JP}", "", ' id="lw-n"')
         + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:{INK};white-space:pre", "", ' id="lw-out"') + '</div>')
o.append(f'<div style="position:absolute;left:96px;top:880px;width:1728px;border-left:8px solid {TEAL};padding:6px 0 6px 28px">'
         + p(f"font-size:32px;font-weight:700;line-height:1.4;color:{INK}", "①의 버튼을 눌러 보세요. 브라우저로 슬라이드를 열면 눌러져요.", ' id="lw-msg"') + '</div>')
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lab_who.js")) as f:
    o.append('<script type="text/slide-js">\n' + f.read() + '</script>')
W("r-lab", o, "앞 장의 표를 직접 눌러 보는 장이에요. 브라우저로 슬라이드를 열면 버튼이 눌러져요. 오른쪽 위에서 보여 주는 방법을 하나 고르면, 파이썬이 틀에서 어떤 메서드를 어떤 순서로 찾는지 상자에 불이 들어오고 출력이 나와요. print와 f-string은 __str__부터 찾고, 없으면 __repr__, 그것도 없으면 기본 모양을 써요. 셀 마지막 줄과 리스트 안은 __str__을 보지 않고 __repr__부터 찾아요. 왼쪽 아래 버튼으로 __str__이나 __repr__을 빼고 다시 눌러 보세요. 누르기 전에 무엇이 나올지 수강생에게 먼저 물어보면 좋아요. 출력은 데모에서 실제로 나온 글자예요. 주소는 실행할 때마다 달라요.")

o = [sec("r-only")] + head(EB3, "하나만 만든다면 __repr__이에요", K3)
FS = 30
c7 = {"id": "c-r7", "lines": B_INIT + [""] + B_REPR + [""] + AB + ["print(a)", "print([a, b])"], "n": 7, "out": ["Bread('팥', 1000)", "[Bread('팥', 1000), Bread('슈크림', 1200)]"]}
o += cell(c7, 96, 196, 1180, FS)
o.append(hl(96, 196, 1180, 5, 2, "run", 1, FS))
o.append(tag(1310, ly(196, 5.5, FS), "__str__ 없이 __repr__만", K3, 1))
yo = oy(196, 12, 0, FS)
o.append(box(2, 193, int(yo - 21), int(tw(c7["out"][0], FS)) + 16, 42, TEAL))
o.append(tag(cx(96, c7["out"][1], FS) + 50, yo, "print도 __repr__을 빌려 써요", K3, 2))
o.append(caption("영수증, 메뉴판처럼 손님용 글씨가 따로 필요할 때 __str__을 더해요.", 920, 3))
W("r-only", o, "이번엔 __str__ 없이 __repr__만 만들었어요. print(a)도 __repr__의 글자를 찍었어요. __str__이 없으면 print는 __repr__을 빌려 써요. 반대로 __str__만 있으면 리스트 안이나 셀 마지막 줄에서는 빌려 쓰지 않아서 3파트 첫 장처럼 낯선 글자가 남아요. 그래서 하나만 만든다면 __repr__이 더 많은 곳을 해결해요. 영수증이나 메뉴판처럼 손님에게 보여 줄 글씨가 따로 필요할 때 __str__을 더해요." + REAL)

o = [sec("r-more")] + head("3. __repr__ · 참고, 읽기만", "len과 +도 같은 원리예요", GRAY)
FS = 36
c8 = {"id": "c-r8", "lines": ["print(len([1, 2, 3]))", "print([1, 2, 3].__len__())", "print(3 + 4)", "print((3).__add__(4))"], "n": 8, "out": ["3", "3", "7", "7"]}
o += cell(c8, 96, 230, 960, FS)
o.append(hl(96, 230, 960, 0, 2, "skip", 1, FS))
o.append(tag(1100, ly(230, 0.5, FS), "len은 리스트 틀의 __len__을 불러요", SUB, 1))
o.append(hl(96, 230, 960, 2, 2, "skip", 2, FS))
o.append(tag(1100, ly(230, 2.5, FS), "+는 숫자 틀의 __add__를 불러요", SUB, 2))
o.append(caption("따라 치지 않아도 돼요. 이 과정에서 직접 만드는 건 __init__, __str__, __repr__ 세 개예요.", 880, 3))
W("r-more", o, "참고로 읽기만 하는 장이에요. 밑줄 두 개짜리 메서드는 세 개만 있는 게 아니에요. len을 부르면 파이썬은 리스트 틀의 __len__을, 더하기를 하면 숫자 틀의 __add__를 찾아 불러요. 직접 불러도 같은 결과가 나와요. 우리가 써 온 len과 더하기도 print와 __str__처럼 약속된 이름으로 돌아가고 있었어요. 이 과정에서는 __init__, __str__, __repr__ 세 개만 직접 만들고, 나머지는 이런 게 있다는 것만 알아 두세요." + REAL)

# ---------- part 4 ----------
o = [sec("l-for")] + head(EB4, "붕어빵 여러 개를 리스트에 담아 하나씩 찍어요", K4)
FS = 28
LB = B_INIT + [""] + B_STR + [""] + B_REPR + ["", 'breads = [Bread("팥", 1000), Bread("슈크림", 1200), Bread("피자", 1500)]', "for b in breads:", "    print(b)"]
cl1 = {"id": "c-l1", "lines": LB, "n": 1, "out": ["팥 붕어빵 1,000원", "슈크림 붕어빵 1,200원", "피자 붕어빵 1,500원"]}
o += cell(cl1, 96, 196, 1340, FS)
o.append(hl(96, 196, 1340, 12, 2, "run", 1, FS))
o.append(tag(cx(96, "for b in breads:", FS) + 40, ly(196, 12, FS), "하나씩 꺼내 print", GR, 1))
o.append(tag(cx(96, "슈크림 붕어빵 1,200원", FS) + 50, oy(196, 14, 1, FS), "b는 붕어빵 하나라서 __str__을 써요", K4, 2))
W("l-for", o, "이제 __str__과 __repr__이 모두 있는 틀로 붕어빵 세 개를 리스트에 담아요. for로 하나씩 꺼내 print하면 b는 붕어빵 하나라서 __str__의 메뉴판 글씨가 나와요. 24의 실습에서는 b.intro()를 불렀는데, 이제는 print(b)만 쳐도 돼요. 이 셀의 breads를 다음 두 장에서 계속 써요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p4", "붕어빵 여러 개 다루기"))

o = [sec("l-comp")] + head(EB4, "23의 컴프리헨션으로 맛만, 가격만, 비싼 것만", K4)
FS = 40
cl2 = {"id": "c-l2", "lines": ["print([b.flavor for b in breads])", "print(sum([b.price for b in breads]))", "print([b for b in breads if b.price >= 1200])"], "n": 2,
       "out": ["['팥', '슈크림', '피자']", "3700", "[Bread('슈크림', 1200), Bread('피자', 1500)]"]}
TC = 236
o += cell(cl2, 96, TC, 1300, FS)
for i, t in enumerate(["맛 칸만 모아요", "가격만 모아 sum에 넘겨요", "비싼 붕어빵을 통째로"]):
    o.append(tag(1430, ly(TC, i, FS), t, K4, i + 1))
y2 = oy(TC, 3, 2, FS)
o.append(underline(4, 201, int(cx(96, cl2["out"][2], FS)), int(y2 + 26), TEAL))
o.append(tag(cx(96, cl2["out"][2], FS) + 50, y2, "리스트 안이라 __repr__", K3, 4))
o.append(caption("__repr__이 없었다면 마지막 줄은 <... object at 0x...>뿐이었어요.", 820, 5))
W("l-comp", o, "23의 컴프리헨션을 붕어빵 리스트에 써요. b.flavor로 맛 칸만 모으고, b.price로 가격만 모아 sum에 넘겼어요. 마지막 줄은 1200원 이상인 붕어빵을 통째로 골라 담았어요. 골라 담은 리스트를 print하니 안의 붕어빵은 __repr__로 보여요. __repr__을 만들지 않았다면 무엇이 골라졌는지 알 수 없는 낯선 글자만 나왔을 거예요." + REAL)

o = [sec("l-sort")] + head(EB4, "22의 key=lambda로 가격순 정렬과 가장 비싼 붕어빵", K4)
FS = 32
cl3 = {"id": "c-l3", "lines": ["print(sorted(breads, key=lambda b: b.price, reverse=True))", "print(max(breads, key=lambda b: b.price))"], "n": 3,
       "out": ["[Bread('피자', 1500), Bread('슈크림', 1200), Bread('팥', 1000)]", "피자 붕어빵 1,500원"]}
o += cell(cl3, 96, 196, 1728, FS, box_w=1215)
o.append(tag(cx(96, "피자 붕어빵 1,500원", FS) + 50, oy(196, 2, 1, FS), "max는 붕어빵 하나라서 __str__", K4, 1))
T4 = 500
cl4 = {"id": "c-l4", "lines": ["print(sorted(breads))"], "n": 4, "out": ["TypeError: '<' not supported between instances of 'Bread' and 'Bread'"], "err": True}
o += cell(cl4, 96, T4, 1728, FS, attrs=' data-build-in="rise order 2"', box_w=1215)
ye = oy(T4, 1, 0, FS)
o.append(box(3, 193, int(ye - 23), int(tw(cl4["out"][0], FS)) + 16, 46, RED))
o.append(tag(cx(96, "print(sorted(breads))", FS) + 40, ly(T4, 0, FS), "붕어빵끼리는 무엇으로 비교할지 몰라요", RED, 3))
o.append(fix(96, 760, "sorted(breads)", "sorted(breads, key=lambda b: b.price)", 4))
W("l-sort", o, "22에서 배운 key=lambda를 붕어빵에 써요. 가격 칸으로 비교하라고 알려 주면 비싼 순으로 정렬되고, max로 가장 비싼 붕어빵을 고를 수 있어요. key 없이 sorted를 부르면 TypeError가 나요. 숫자끼리는 크기를 비교할 수 있지만 붕어빵끼리는 맛으로 비교할지 가격으로 비교할지 몰라서예요. max가 돌려준 값은 붕어빵 하나라서 print가 __str__의 메뉴판 글씨를 찍었어요." + REAL)

o = [sec("st-sell")] + head(EB4, "메서드로 재고와 판매 개수를 바꿔요", K4)
FS = 27
SS = ["class Stall:", "    def __init__(self, name, stock):", "        self.name = name", "        self.stock = stock", "        self.sold = 0", "", "    def sell(self, qty):", "        self.stock = self.stock - qty", "        self.sold = self.sold + qty", "", "    def __str__(self):", '        return f"{self.name}: 남은 {self.stock}개, 판매 {self.sold}개"', "", 's = Stall("팥", 10)', "print(s)", "s.sell(3)", "print(s)"]
o += cell({"id": "c-st1", "lines": SS, "n": 5, "out": ["팥: 남은 10개, 판매 0개", "팥: 남은 7개, 판매 3개"]}, 96, 176, 1200, FS)
o.append(hl(96, 176, 1200, 6, 3, "mark", 1, FS))
o.append(tag(cx(96, "        self.stock = self.stock - qty", FS) + 40, ly(176, 7.5, FS), "값 바꾸기", BL, 1, size=26))
rows_, ys = plain_rows(1350, 196, 474, [["찍기", "10", "0"], ["sell(3)", "7", "3"]], [190, 110, 100], order0=2, rh=84, head_=["일", "stock", "sold"], fs=30)
o += rows_
o.append(box(3, 1350 + 200, ys[1] + 12, 230, 60, BL))
o.append(p(f"position:absolute;left:1350px;top:{ys[1] + 130}px;width:474px;font-size:28px;font-weight:700;line-height:1.5;color:{INK}", "바뀐 값은 다음에 부를 때까지 남아 있어요. 이걸 상태라고 불러요.", ' data-build-in="rise order 4"'))
W("st-sell", o, "붕어빵 노점 하나를 틀로 만들어요. 재고는 재료로 받고, 판매 개수는 24에서 본 것처럼 0에서 시작해요. sell 메서드는 판 개수만큼 재고를 빼고 판매 개수를 더해요. sell을 부를 때마다 칸의 값이 바뀌고, 바뀐 값은 다음에 부를 때까지 노점에 남아 있어요. 이렇게 객체가 지금 들고 있는 값을 상태라고 불러요. __str__이 있어서 print(s)만 쳐도 지금 상태가 보여요." + REAL)

o = [sec("st-if")] + head(EB4, "재고가 모자라면 팔지 않게 if로 막아요", K4)
SI = ["class Stall:", "    def __init__(self, name, stock):", "        self.name = name", "        self.stock = stock", "        self.sold = 0", "", "    def sell(self, qty):", "        if qty > self.stock:", '            return "재고가 모자라요"', "        self.stock = self.stock - qty", "        self.sold = self.sold + qty", '        return "판매 완료"', "", 's = Stall("팥", 5)', "print(s.sell(3))", "print(s.sell(4))", "print(s.stock, s.sold)"]
o += cell({"id": "c-st2", "lines": SI, "n": 6, "out": ["판매 완료", "재고가 모자라요", "2 3"]}, 96, 176, 1200, FS)
o.append(hl(96, 176, 1200, 7, 2, "err", 1, FS))
o.append(tag(cx(96, '            return "재고가 모자라요"', FS) + 40, ly(176, 7.5, FS), "17의 if로 막기", RED, 1, size=26))
OX = 520
for j, (t, c) in enumerate([("5개 중 3개를 팔았어요", GR), ("4개는 막혔어요. return에서 바로 끝나요", RED), ("남은 2개, 판매 3개 그대로", GR)]):
    o.append(tag(OX, oy(176, 17, j, FS), t, c, j + 2, size=26))
W("st-if", o, "재고보다 많이 팔면 재고가 마이너스가 돼요. sell 안에 17의 if를 넣어서, 재고가 모자라면 글자를 return하고 바로 끝나게 했어요. 19에서 배운 대로 return을 만나면 아래 줄은 실행하지 않아서 재고와 판매 개수가 바뀌지 않아요. 3개를 판 뒤 남은 2개는 그대로예요. 메서드 안에 값을 지키는 규칙을 둘 수 있어서 재고가 마이너스가 되는 일을 막아요." + REAL)

# ---------- part 5: the bad line, the error, one reading tag, the fix ----------
FS = 30
o = [sec("t-print")] + head(EB5, "__str__ 안에서 print하면 returned non-string", K5)
ct = {"id": "c-t1", "lines": B_INIT + ["", "    def __str__(self):", '        print(self.flavor, "붕어빵")', ""] + AB + ["print(a)"], "n": 1, "out": ["팥 붕어빵", "TypeError: __str__ returned non-string (type NoneType)"], "err": True}
o += cell(ct, 96, 196, 1300, FS)
o.append(hl(96, 196, 1300, 6, 1, "err", 1, FS))
o.append(tag(cx(96, ct["lines"][6], FS) + 40, ly(196, 6, FS), "return이 없어요", RED, 1))
ye = oy(196, 11, 1, FS)
o.append(box(2, 193, int(ye - 20), int(tw(ct["out"][1], FS)) + 16, 40, RED))
o.append(tag(cx(96, ct["out"][1], FS) + 60, ye, "글자 대신 None", RED, 2))
o.append(fix(96, 860, 'print(self.flavor, "붕어빵")', 'return f"{self.flavor} 붕어빵"', 3))
W("t-print", o, "가장 많이 하는 실수예요. __str__ 안에서 return 대신 print를 썼어요. 출력을 보면 팥 붕어빵이 먼저 찍히고 바로 TypeError가 나요. __str__이 불려서 안의 print가 실행된 뒤, 돌려준 값이 글자가 아니라 None이었기 때문이에요. 19에서 배운 대로 return이 없는 함수는 None을 돌려줘요. __str__과 __repr__은 꼭 글자를 return해요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p5", "오류와 함정"))

o = [sec("t-int")] + head(EB5, "숫자를 돌려줘도 returned non-string", K5)
ct = {"id": "c-t2", "lines": B_INIT + ["", "    def __str__(self):", "        return self.price", ""] + AB + ["print(a)"], "n": 2, "out": ["TypeError: __str__ returned non-string (type int)"], "err": True}
o += cell(ct, 96, 196, 1300, FS)
o.append(hl(96, 196, 1300, 6, 1, "err", 1, FS))
o.append(tag(cx(96, ct["lines"][6], FS) + 40, ly(196, 6, FS), "가격 숫자를 그대로", RED, 1))
ye = oy(196, 11, 0, FS)
xa = cx(96, "TypeError: __str__ returned non-string ", FS)
o.append(underline(2, int(xa), int(xa + tw("(type int)", FS)), int(ye + 18), RED))
o.append(tag(cx(96, ct["out"][0], FS) + 50, ye, "int = 숫자", RED, 2))
o.append(fix(96, 830, "return self.price", 'return f"{self.price}원"', 3))
W("t-int", o, "이번엔 return은 했는데 가격 숫자를 그대로 돌려줬어요. 오류 끝의 type int가 숫자를 돌려줬다는 뜻이에요. __str__과 __repr__은 이름 그대로 글자를 돌려줘야 해요. 12에서 배운 str()로 바꿔 return str(self.price)라고 적거나, 화면처럼 f-string으로 감싸서 돌려줘요." + REAL)

o = [sec("t-under")] + head(EB5, "밑줄이 하나면 오류 없이 그냥 무시돼요", K5)
ct = {"id": "c-t3", "lines": B_INIT + ["", "    def _str_(self):", '        return f"{self.flavor} 붕어빵"', ""] + AB + ["print(a)"], "n": 3, "out": ["<__main__.Bread object at 0x7fc8a2a6bcb0>"]}
o += cell(ct, 96, 196, 1300, FS)
y5 = ly(196, 5, FS)
xs = cx(96, "    def ", FS)
o.append(box(1, int(xs - 4), int(y5 - 21), int(tw("_str_", FS)) + 8, 42, RED))
o.append(tag(cx(96, ct["lines"][5], FS) + 40, y5, "밑줄이 하나씩이에요", RED, 1))
yo = oy(196, 11, 0, FS)
o.append(tag(cx(96, ct["out"][0], FS) + 50, yo, "오류 없이 기본 모양", RED, 2))
o.append(fix(96, 830, "def _str_(self):", "def __str__(self):", 3))
W("t-under", o, "밑줄을 하나씩만 적었어요. 24의 __init__ 때는 TypeError가 났는데, 이번에는 오류가 안 나요. 파이썬이 print할 때 __str__을 찾았는데 없어서 그냥 기본 모양을 쓴 거예요. _str_은 이름이 비슷한 평범한 메서드일 뿐이에요. 오류가 없어서 오히려 찾기 어려우니, 낯선 글자가 그대로 나오면 밑줄 개수부터 봐요." + REAL)

o = [sec("t-plus")] + head(EB5, "글자에 붕어빵을 바로 더하면 can only concatenate", K5)
ct = {"id": "c-t4", "lines": B_INIT + [""] + B_STR + [""] + AB + ['print("주문: " + a)'], "n": 4, "out": ['TypeError: can only concatenate str (not "Bread") to str'], "err": True}
o += cell(ct, 96, 196, 1300, FS)
o.append(hl(96, 196, 1300, 10, 1, "err", 1, FS))
o.append(tag(cx(96, ct["lines"][10], FS) + 40, ly(196, 10, FS), "더하기는 __str__을 부르지 않아요", RED, 1))
ye = oy(196, 11, 0, FS)
o.append(underline(2, 201, int(cx(96, ct["out"][0], FS)), int(ye + 18), RED))
o.append(fix(96, 820, '"주문: " + a', '"주문: " + str(a)', 3))
o.append(caption('f"주문: {a}"나 print("주문:", a)처럼 적어도 __str__이 불려요.', 920, 4))
W("t-plus", o, "__str__을 만들었으니 글자에 바로 더해도 될 것 같지만 TypeError가 나요. 글자에는 글자만 더할 수 있다는 뜻이에요. 더하기는 붕어빵을 글자로 바꿔 주지 않아요. 2파트에서 본 것처럼 str(a)로 먼저 바꾸거나, f-string 중괄호에 넣거나, print에 쉼표로 넘기면 __str__이 불려요. 12에서 숫자와 글자를 더할 때 난 오류와 같은 원리예요." + REAL)

# ---------- part 6 ----------
XS = ["class Stall:", "    def __init__(self, flavor, price, stock):", "        self.flavor = flavor", "        self.price = price", "        self.stock = stock", "        self.sold = 0", "", "    def sell(self, qty):", "        if qty > self.stock:", '            return f"{self.flavor} 재고가 모자라요"', "        self.stock = self.stock - qty", "        self.sold = self.sold + qty", '        return f"{self.flavor} {qty}개 판매"', "", "    def __str__(self):", '        return f"{self.flavor}: 판매 {self.sold}개, 매출 {self.sold * self.price:,}원"']
XS2 = ['pat = Stall("팥", 1000, 20)', 'cream = Stall("슈크림", 1200, 10)', "print(pat.sell(5))", "print(cream.sell(12))", "print(cream.sell(4))", "print(pat)", "print(cream)"]
FS = 28
o = [sec("x-stall")] + head(EB6, "붕어빵 노점의 하루 ①: 노점 틀 만들기", K6)
o += cell({"id": "c-x1", "lines": XS, "n": 1}, 96, 176, 1728, FS)
for k, (i, n, t, c) in enumerate([(1, 5, "__init__: 재료 셋, 판매는 0", BL), (7, 6, "sell: if로 막고 상태 바꾸기", RED), (14, 2, "__str__: 매출 글씨", GR)]):
    yt = 176 + 10 + i * LH(FS)
    o.append(spot(k + 1, 183, yt, 1638, n * LH(FS), pad=8, r=10))
    o.append(p(f"position:absolute;left:1430px;top:{yt + 4:.0f}px;width:370px;text-align:right;font-size:26px;font-weight:700;line-height:1.45;color:{c}", e(t), f' data-build-in="fade order {k + 1}"'))
o.append(spot_off(4))
o.append(caption("출력이 없는 셀이에요. 틀을 만들기만 했어요.", 900, 4))
W("x-stall", o, "노점의 하루를 두 장에 걸쳐 만들어요. 먼저 틀이에요. 한 덩어리씩 짚어 봐요. __init__은 맛, 가격, 재고를 받고 판매 개수는 0에서 시작해요. sell은 4파트처럼 재고를 확인하고, 팔 수 있으면 상태를 바꾼 뒤 글자를 return해요. __str__은 판매 개수와 가격을 곱한 매출을 천 단위 콤마로 보여 줘요. 이 셀은 틀만 만들어서 출력이 없어요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p6", "실습"))

o = [sec("x-stall2")] + head(EB6, "붕어빵 노점의 하루 ②: 팔고, 막고, 매출 찍기", K6)
FS = 30
o += cell({"id": "c-x1b", "lines": XS2, "n": 2, "out": ["팥 5개 판매", "슈크림 재고가 모자라요", "슈크림 4개 판매", "팥: 판매 5개, 매출 5,000원", "슈크림: 판매 4개, 매출 4,800원"]}, 96, 176, 880, FS)
rows_, ys = plain_rows(1060, 196, 764, [["찍기", "20", "10"], ["pat.sell(5)", "15", "10"], ["cream.sell(12)", "15", "10"], ["cream.sell(4)", "15", "6"]],
                       [300, 180, 220], order0=1, rh=84, head_=["일", "팥 stock", "슈크림 stock"], fs=30)
o += rows_
o.append(box(5, 1050, ys[2] + 8, 774, 68, RED))
o.append(p(f"position:absolute;left:1060px;top:{ys[3] + 110}px;width:764px;font-size:28px;font-weight:700;line-height:1.5;color:{RED}", "12개는 재고 10개보다 많아서 if에서 return했어요. 재고는 그대로예요.", ' data-build-in="rise order 5"'))
o.append(caption("__init__으로 찍고, 메서드로 상태를 바꾸고, if로 막고, __str__로 찍었어요.", 900, 6))
W("x-stall2", o, "앞 셀에서 만든 틀로 팥 노점과 슈크림 노점을 따로 찍었어요. 팥은 5개 팔렸어요. 슈크림 12개는 재고 10개보다 많아서 막혔고, 4개는 팔렸어요. 오른쪽 표에서 줄마다 재고가 어떻게 바뀌는지 보세요. 하루가 끝나면 print로 판매 개수와 매출을 찍어요. __str__이 있어서 print(pat)만 쳐도 돼요. 이 챕터에서 배운 것을 모두 썼어요." + REAL)

o = [sec("x-menu")] + head(EB6, "카페 메뉴판: 손님용 줄 맞춤과 개발자용 확인", K6)
FS = 27
XM = ["class Drink:", "    def __init__(self, name, price):", "        self.name = name", "        self.price = price", "", "    def __str__(self):", '        return f"{self.name:<7}{self.price:>6,}원"', "", "    def __repr__(self):", "        return f\"Drink('{self.name}', {self.price})\"", "", 'menu = [Drink("latte", 5000), Drink("tea", 4000), Drink("coffee", 4500)]', "for d in sorted(menu, key=lambda d: d.price):", "    print(d)", "print([d for d in menu if d.price < 5000])"]
o += cell({"id": "c-x2", "lines": XM, "n": 3, "out": ["tea     4,000원", "coffee  4,500원", "latte   5,000원", "[Drink('tea', 4000), Drink('coffee', 4500)]"]}, 96, 176, 1340, FS)
o.append(hl(96, 176, 1340, 5, 2, "run", 1, FS))
o.append(tag(1470, ly(176, 5.5, FS), "손님용: 13의 칸 맞추기", GR, 1, size=26))
o.append(hl(96, 176, 1340, 8, 2, "mark", 2, FS))
o.append(tag(1470, ly(176, 8.5, FS), "개발자용: 코드 모양", BL, 2, size=26))
mx = cx(96, "latte   5,000원", FS) + 60
o.append(f'<div data-build-in="fade order 3" style="position:absolute;left:{mx - 30:.0f}px;top:{oy(176, 15, 0, FS) - 18:.0f}px;width:6px;height:{LH(FS) * 2 + 36:.0f}px;border-radius:3px;background:{GR}"></div>')
o.append(tag(mx, oy(176, 15, 1, FS), "가격순 메뉴판 줄은 __str__", GR, 3, size=26, lead=False))
o.append(tag(cx(96, "[Drink('tea', 4000), Drink('coffee', 4500)]", FS) + 50, oy(176, 15, 3, FS), "골라 담은 리스트는 __repr__", BL, 4, size=26))
W("x-menu", o, "카페 메뉴판을 만들어요. __str__은 13의 칸 맞추기로 이름은 왼쪽 7칸, 가격은 오른쪽 6칸에 맞춰 손님용 줄을 만들어요. __repr__은 개발자가 확인할 때 쓰는 주문표 모양이에요. 22의 sorted와 key로 가격순 정렬해 하나씩 print하면 메뉴판 줄이 나오고, 23의 컴프리헨션으로 골라 담은 리스트를 print하면 주문표 모양이 나와요. 한 틀에 두 메서드를 다 두면 어디서 찍어도 알아보기 쉬워요." + REAL)

# ---------- wrap up: plain rows, no boxes ----------
o = [sec("trouble")] + head("정리", "막히면 오류의 마지막 줄을 봐요", RED)
TR = [("<__main__.Bread object at 0x...>", "__str__이나 __repr__이 없거나 밑줄이 하나예요", "__repr__ 만들기"),
      ("리스트 안만 <... object ...>", "__str__만 만들었어요", "__repr__도 만들기"),
      ("TypeError: __str__ returned non-string (type NoneType)", "안에서 print했어요", "return으로"),
      ("TypeError: __str__ returned non-string (type int)", "숫자를 돌려줬어요", "str()이나 f-string"),
      ("TypeError: can only concatenate str (not \"Bread\") to str", "글자에 붕어빵을 바로 더했어요", "str(a), f\"{a}\""),
      ("TypeError: '<' not supported between instances", "붕어빵끼리 비교할 기준이 없어요", "key=lambda b: b.price"),
      ("재고가 마이너스가 돼요", "메서드에서 값을 확인하지 않았어요", "if와 return으로 막기")]
o.append(f'<div style="position:absolute;left:96px;top:196px;width:1728px;height:48px;display:flex;flex-direction:row;align-items:center;gap:24px;border-bottom:3px solid {INK}">'
         + p(f"width:1300px;flex:none;font-size:24px;font-weight:700;color:{GRAY}", "보이는 것과 이유") + p(f"font-size:24px;font-weight:700;color:{GRAY}", "고치기") + '</div>')
for i, (q, a_, cmd) in enumerate(TR):
    o.append(f'<div style="position:absolute;left:96px;top:{244 + i * 94}px;width:1728px;height:94px;display:flex;flex-direction:row;align-items:center;gap:24px;border-bottom:2px solid {HAIR}">'
             + '<div style="width:1300px;flex:none;display:flex;flex-direction:column;gap:2px">'
             + p(f"{'font-family:' + MONO + ';' if q.isascii() else ''}font-size:25px;font-weight:700;color:{INK};white-space:nowrap", e(q))
             + p(f"font-size:23px;color:{SUB}", e(a_)) + '</div>'
             + p(f"{'font-family:' + MONO + ';font-size:25px;' if cmd.isascii() else 'font-size:26px;'}font-weight:700;color:{GR};white-space:pre", e(cmd)) + '</div>')
o.append(caption("낯선 글자가 나오면 \"지금 파이썬이 어느 메서드를 찾았을까\"부터 생각해요.", 944))
W("trouble", o, "이번 챕터에서 자주 만나는 일을 모았어요. 1번과 2번은 어느 메서드가 불리는지와 관련돼요. print는 __str__, 리스트 안은 __repr__이에요. 3번부터 5번은 두 메서드가 꼭 글자를 돌려줘야 해서 생기는 오류예요. 6번은 22의 key를, 7번은 17의 if를 메서드 안에서 쓰면 해결돼요. 낯선 글자가 나오면 지금 파이썬이 어느 메서드를 찾았을지부터 생각해 보세요.", ("trouble", "정리"))

o = [sec("cheatsheet")] + [f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>']
CH = [("def __str__(self):", "print, str(), f-string에서 보일 글자", K2), ("def __repr__(self):", "셀 마지막 줄, 리스트 안에서 보일 글자", K3),
      ('return f"..."', "두 메서드 모두 꼭 글자를 돌려줘요", K2), ("Bread('팥', 1000)", "repr은 다시 찍는 코드 모양으로", K3),
      ("str(a)", "글자로 바꿔 다른 글자와 잇기", K2), ("__repr__만", "하나만 만든다면. print도 빌려 써요", K3),
      ("key=lambda b: b.price", "붕어빵을 가격으로 줄 세우기", K4), ("self.stock - qty", "메서드로 상태 바꾸기, if로 막기", K4)]
for i, (k, d, c) in enumerate(CH):
    x, y = 96 + (i % 2) * 884, 196 + (i // 2) * 150
    o.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:844px;height:150px;display:flex;flex-direction:column;justify-content:center;gap:10px;border-bottom:2px solid {HAIR}">'
             + p(f"font-family:{MONO};font-size:34px;font-weight:700;color:{c};white-space:pre", e(k)) + p(f"font-size:28px;font-weight:500;color:{INK}", e(d)) + '</div>')
o.append(p(f"position:absolute;left:96px;top:830px;width:1728px;font-size:34px;font-weight:700;line-height:1.5;color:{INK}", "__str__은 손님용 메뉴판, __repr__은 만든 사람용 주문표예요."))
o.append(p(f"position:absolute;left:96px;top:900px;width:1728px;font-size:30px;font-weight:500;line-height:1.5;color:{SUB}", "다음 챕터: 26에서 틀을 물려받아 슈크림 붕어빵 틀을 만들어요."))
W("cheatsheet", o, "이번 챕터에서 배운 것을 한 장에 모았어요. __str__과 __repr__은 파이썬이 정해진 순간에 알아서 부르는 메서드예요. print와 str과 f-string은 __str__을, 셀 마지막 줄과 리스트 안의 값은 __repr__을 찾아요. 둘 다 꼭 글자를 return해요. 하나만 만든다면 __repr__이에요. 붕어빵 여러 개는 22의 key로 정렬하고, 메서드 안에서 재고 같은 상태를 바꿔요. 26에서는 이 틀을 물려받아 새 틀을 만드는 상속을 배워요.")

# ---------- toc: number, title, what is inside, pages; split by hairlines ----------
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
PARTS = [(K1, "왜 필요한가", "print했을 때 낯선 글자, 파이썬이 찾아 부르는 메서드, 가장 짧은 __str__", "w-why", "w-min"),
         (K2, "__str__", "붕어빵마다 다른 글자, 불리는 곳, intro와 비교", "s-basic", "s-intro"),
         (K3, "__repr__", "남는 낯선 글자, '팥'과 팥, 주문표 모양, 한 장 표, 눌러 보기, 하나만 만든다면", "r-cell", "r-more"),
         (K4, "붕어빵 여러 개 다루기", "for, 컴프리헨션, key 정렬, 재고 바꾸기, if로 막기", "l-for", "st-if"),
         (K5, "오류와 함정", "print를 쓴 __str__, 숫자 돌려주기, 밑줄 하나, 글자 더하기", "t-print", "t-plus"),
         (K6, "실습", "노점의 하루 두 장, 카페 메뉴판", "x-stall", "x-menu")]
t = [sec("toc"), f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>']
for i, (c, h, s, a, b) in enumerate(PARTS):
    y = 196 + i * 118
    t.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:118px;display:flex;flex-direction:row;align-items:center;gap:32px;border-bottom:2px solid {HAIR}">'
             + p(f"width:60px;flex:none;font-size:52px;font-weight:900;color:{c}", str(i + 1))
             + p(f"width:520px;flex:none;font-family:{MONO if h.isascii() else SANS};font-size:36px;font-weight:700;color:{INK}", e(h))
             + p(f"flex:1;font-size:26px;line-height:1.4;color:{SUB}", e(s))
             + p(f"width:130px;flex:none;text-align:right;font-size:26px;font-weight:700;color:{GRAY}", f"{page[a]}–{page[b]}쪽") + '</div>')
t.append(p(f"position:absolute;left:96px;top:930px;font-size:26px;color:{SUB}", f"{page['ready']}쪽은 노트북 준비, {page['trouble']}–{page['cheatsheet']}쪽은 막힐 때와 한 장 요약이에요."))
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(t) + "\n<aside>" + e("여섯 파트로 나눴어요. 1파트는 붕어빵을 print했을 때의 문제와 파이썬이 알아서 부르는 메서드 그림이에요. 2파트와 3파트가 중심이에요. __str__과 __repr__을 하나씩 만들고, 언제 어느 쪽이 불리는지 표로 정리해요. 4파트는 붕어빵 여러 개를 정렬하고 상태를 바꾸는 메서드, 5파트는 자주 나는 오류, 6파트는 노점과 카페 실습이에요. 파트마다 새 커널에서 위에서부터 차례로 실행해요.") + "</aside>\n</section>\n")

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-05T06:00:00Z"}, "lists": "css", "title": "클래스 2 (__str__과 __repr__)", "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
print(len(ORDER), "slides")
