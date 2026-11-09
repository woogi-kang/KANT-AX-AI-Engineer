"""Generates every slide of the functions 3 deck (21, lambda, map, filter) and slides/deck.json.

Story: keeps writing in basics.ipynb from chapters 12-20. Starts from the for-and-append block written again for every
price change, draws map (change each value) and filter (keep the True ones) as pipes, then treats a function as a value
(store it, pass it), lambda next to def, map, map objects, built-in functions passed by name, filter with lists and
dictionaries, and filter feeding map. Part 5 collects the usual errors, and part 6 uses the café menu, stock and orders.
Every cell and output comes from tools/demo.sh (tools/run_nb.py runs the cells with the project kernel).

Layout (2026-11-08 remake, rules from the Stageshow skill, github.com/benjitaylor/skills):
1. one focal object per slide (the cell or the picture), drawn large; at most one small satellite beside it
2. terms are labelled on the code or the picture with leader tags and brackets, not in side cards
3. say it once: what the speaker notes explain stays out of the slide; one caption sentence at the bottom
4. values that change move: map and filter results fly out of their input boxes
5. a fix is the wrong line struck through next to the right line
Highlights come from tools/HIGHLIGHT.md (line tint, line spotlight, pen ring, underline, box, fly). No typing.
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


def num(i, color, size=56, extra=""):
    return p(f"width:{size + 16}px;height:{size + 16}px;flex:none;border-radius:50%;background:{color};color:#FFFFFF;font-size:{size * 0.6:.0f}px;font-weight:900;line-height:{size + 16}px;text-align:center;{extra}", str(i))


TRUE_C, FALSE_C = GR, RED


def tf(v, size=26):
    """True / False chip."""
    c = TRUE_C if v == "True" else FALSE_C
    bg = "#E6F4EC" if v == "True" else "#F8E6E6"
    return p(f"display:inline-block;font-family:{MONO};font-size:{size}px;font-weight:700;color:{c};background:{bg};border-radius:10px;padding:2px 14px;white-space:nowrap", v)


def mono(text, size=28, color=INK, bg="#F1F0EC", extra=""):
    return p(f"font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.4;color:{color};background:{bg};border-radius:10px;padding:4px 16px;white-space:pre;{extra}", e(text))


K1, K1BG = "#1E5FA8", "#E5EEF8"
K2, K2BG = "#A0620A", "#F7EEDD"
K3, K3BG = TEAL, "#E2F2F3"
K4, K4BG = "#A23B72", "#F6E7EF"


def chip(text, color=K1, bg=K1BG, fs=30, extra=""):
    return p(f"font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:1.2;color:{INK};background:{bg};border:3px solid {color};border-radius:999px;padding:6px 22px;white-space:pre;{extra}", e(text))


# line tints: green run, gray skip, red error, blue mark (tools/HIGHLIGHT.md)
HL = {"run": "rgba(31,138,76,0.16)", "skip": "rgba(106,113,128,0.20)", "err": "rgba(163,49,49,0.14)", "mark": "rgba(36,89,201,0.14)"}


K5, K5BG = RED, "#F8E6E6"
K6, K6BG = PUR, "#ECE7F8"
REAL = " 출력은 실제로 실행한 결과예요."


def arrow(w=60, color="#C9CED8"):
    return f'<x-shape kind="arrow-right" style="width:{w}px;height:30px;flex:none;background:{color}"></x-shape>'


def cover(lines, h1, sub, note, accent="#F2B27A", h1size=92):
    cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
           f'<p style="font-size:28px;font-weight:700;color:{accent};letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
           f'<h1 style="font-size:{h1size}px;font-weight:900;line-height:1.1;color:#F6F5F1">{h1}</h1>',
           f'<p style="font-size:40px;line-height:1.4;color:#BFC6D4">{sub}</p>']
    cov.append(f'<div style="position:absolute;left:900px;top:300px;width:900px;height:480px;background:#252B36;border-radius:24px;padding:44px 48px;display:flex;flex-direction:column;justify-content:center;gap:16px">')
    for line, c in lines:
        cov.append(p(f"font-family:{MONO};font-size:30px;font-weight:700;line-height:1.45;color:{c};white-space:pre", e(line)))
    cov.append('</div>')
    W("cover", cov, note, ("intro", "들어가기"))
    ORDER.append("toc")


EB1 = "1. 왜 필요한가"
EB2 = "2. 함수를 값처럼, lambda"
EB3 = "3. map"
EB4 = "4. filter"
EB5 = "5. 오류와 함정"
EB6 = "6. 실습"
PR = "prices = [4500, 5000, 6500]"


# ======================= 2026-11-08 remake helpers =======================
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from highlight import spot, spot_off, ring, box, underline

CFS = [30]          # code font size of the cells on the slide being drawn


def LHf():
    return CFS[0] * 1.45


def cell(c, left, top, w, sel=None, mode="cmd", pre="", attrs=""):
    """A notebook cell drawn at CFS[0] px. c: dict(id, lines, n, out, err)."""
    fs, lines, n = CFS[0], c.get("lines", [""]), c.get("n")
    chosen = sel == c["id"]
    o = [f'<div id="{pre}{c["id"]}"{attrs or c.get("attrs", "")} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;display:flex;flex-direction:column;gap:10px">']
    bar = f'<div style="width:7px;flex:none;border-radius:4px;background:{SEL if chosen else "transparent"}"></div>'
    gutter = p(f"width:58px;flex:none;font-family:{MONO};font-size:22px;color:{GRAY};text-align:right;padding-top:{max(8, fs * 0.3):.0f}px", f"[{n}]" if n else "[ ]")
    txt = "".join(p(f"font-family:{MONO};font-size:{fs}px;line-height:1.45;white-space:pre;color:{INK}", e(l) if l else "&#160;") for l in lines)
    tag_ = p(f"position:absolute;right:14px;bottom:8px;font-size:18px;color:{GRAY}", "Python")
    bx_ = f'<div style="flex:1;position:relative;background:#FFFFFF;border:2px solid {LINE};border-radius:10px;padding:8px 18px 8px;display:flex;flex-direction:column">{txt}{tag_}</div>'
    o.append(f'<div style="display:flex;flex-direction:row;gap:10px;align-items:stretch">{bar}{gutter}{bx_}</div>')
    if c.get("out"):
        col = lambda l: RED if c.get("err") and re.match(r"[A-Za-z]+(Error|Interrupt)", l) else INK
        o.append(''.join(p(f"margin-left:85px;padding:0 20px;font-family:{MONO};font-size:{fs}px;line-height:1.45;white-space:pre;color:{col(l)}", e(l) if l else "&#160;") for l in c["out"]))
    o.append('</div>')
    return o


def hl(left, top, w, i, n=1, kind="run", order=1):
    y = top + 10 + i * LHf()
    at = f' data-build-in="fade order {order}"' if order else ""
    return f'<div{at} style="position:absolute;left:{left + 87}px;top:{y:.0f}px;width:{w - 89}px;height:{n * LHf():.0f}px;background:{HL[kind]};border-radius:6px"></div>'


def ly(top, i):
    """Center y of code line i in a cell drawn at top."""
    return top + 10 + i * LHf() + LHf() / 2


def oy(top, n, j):
    """Center y of output line j of a cell with n code lines."""
    return top + 20 + n * LHf() + 10 + j * (LHf() + 10) + LHf() / 2


def tw(s, fs=None):
    """Rendered width of a code string: Hangul is one em, the rest 0.6 em."""
    f = fs or CFS[0]
    return sum(f * (1.0 if '가' <= ch <= '힣' else 0.6) for ch in s)


def cx(left, line, k):
    """x of character k of a code line in a cell at left."""
    return left + 105 + tw(line[:k])


def ox(left, line, k):
    """x of character k of an output line in a cell at left."""
    return left + 105 + tw(line[:k])


def tx(left, lines, gap=36):
    """x just right of the longest of the given lines."""
    return int(left + 105 + max(tw(l) for l in lines) + gap)


def tag(x, y, text, color, order=None, size=28, anim="fade"):
    """A leader label '← text' centred on y. No box."""
    at = f' data-build-in="{anim} order {order}"' if order else ""
    return p(f"position:absolute;left:{x:.0f}px;top:{y - size * 0.725:.0f}px;font-size:{size}px;font-weight:700;line-height:1.45;color:{color};white-space:nowrap", "← " + e(text), at)


def uline(order, left, line, k0, k1, y, color=OR):
    """Pen underline under characters k0..k1 of a code line (y = centre of that line)."""
    return underline(order, round(cx(left, line, k0)), round(cx(left, line, k1)), round(y + LHf() * 0.42), color)


def pen_box(order, left, line, k0, k1, y, color=RED):
    """A pen-drawn box tight around characters k0..k1 of a code or output line (y = centre of that line)."""
    x0, x1 = cx(left, line, k0), cx(left, line, k1)
    return box(order, round(x0 - 8), round(y - LHf() * 0.5), round(x1 - x0 + 16), round(LHf()), color)


def line_spot(order, left, top, i, n, x_end, pad=10):
    """Spotlight over code lines i..i+n-1 and their tags (the hole runs to x_end)."""
    y = top + 10 + i * LHf()
    return spot(order, left + 87, round(y), round(x_end - left - 87), round(n * LHf()), pad=pad, r=12)


def fix(left, top, bad, good, order, size=34, w=1728):
    """The wrong line struck through, an arrow, the right line."""
    return (f'<div data-build-in="rise order {order}" style="position:absolute;left:{left}px;top:{top}px;width:{w}px;display:flex;flex-direction:row;align-items:center;gap:22px">'
            + p(f"font-size:{size}px;font-weight:900;color:{RED}", "✕")
            + p(f"font-family:{MONO};font-size:{size}px;font-weight:700;color:{RED};text-decoration:line-through;text-decoration-thickness:3px;white-space:pre", e(bad))
            + arrow(70, "#C9CED8")
            + f'<svg width="{int(size*0.9)}" height="{int(size*0.9)}" viewBox="0 0 24 24" style="flex:none"><path d="M4 12.5l5 5L20 6.5" fill="none" stroke="{GR}" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
            + p(f"font-family:{MONO};font-size:{size}px;font-weight:700;color:{INK};background:#E6F4EC;border:3px solid {GR};border-radius:14px;padding:6px 20px;white-space:pre", e(good)) + '</div>')


def caption(text, top=944, order=None):
    at = f' data-build-in="rise order {order}"' if order else ""
    return p(f"position:absolute;left:96px;top:{top}px;width:1728px;font-size:34px;font-weight:700;line-height:1.4;color:{INK}", text, ' id="caption"' + at)


def bracket(order, x1, x2, y, color, width=5, tick=14):
    """A square bracket under a piece of code, drawn like a pen line."""
    return (f'<svg data-build-in="draw order {order}" viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible">'
            f'<path d="M{x1:.0f},{y - tick} L{x1:.0f},{y} L{x2:.0f},{y} L{x2:.0f},{y - tick}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def leader(order, x1, y1, x2, y2, color=GRAY):
    """A thin leader line ending in a dot at (x1, y1), the thing it explains."""
    return (f'<svg data-build-in="fade order {order}" viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible">'
            f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{color}" stroke-width="2.5"/><circle cx="{x1:.0f}" cy="{y1:.0f}" r="6" fill="{color}"/></svg>')


def txt(left, top, text, size=30, color=INK, weight=700, attrs="", mono_=False, w=None):
    ws = f"width:{w}px;" if w else ""
    font = f"font-family:{MONO};" if mono_ else ""
    return p(f"position:absolute;left:{left:.0f}px;top:{top:.0f}px;{ws}{font}font-size:{size}px;font-weight:{weight};line-height:1.4;color:{color};white-space:nowrap", text, attrs)


def vbox(bid, left, top, w, h, text, color, bg, attrs="", fs=36, dashed=False, crossed=False):
    """One value in a box (pipes and lists)."""
    st = "dashed" if dashed else "solid"
    deco = ";text-decoration:line-through;text-decoration-thickness:3px" if crossed else ""
    idt = f' id="{bid}"' if bid else ""
    return p(f"position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;border-radius:16px;border:3px {st} {color};background:{bg};"
             f"font-family:{MONO};font-size:{fs}px;font-weight:700;line-height:{h - 6}px;text-align:center;color:{INK if not crossed else '#A9AEB8'};white-space:pre{deco}", e(text), idt + attrs)


def down(x, y, color="#C9CED8", attrs=""):
    return f'<x-shape{attrs} kind="arrow-right" style="position:absolute;left:{x - 15:.0f}px;top:{y}px;width:30px;height:26px;transform:rotate(90deg);background:{color}"></x-shape>'


def pipe2(pre, left, top, items, fn, outs, color, bg, orders, w=240, h=130, gap=16, keep=None, fs=38, band_h=110):
    """Inputs on top, the function band, results below. Each result flies out of its input box at orders[i].
    keep (filter): False results stay as a crossed dashed box under the band."""
    o = []
    n = len(items)
    width = n * w + (n - 1) * gap
    for i, v in enumerate(items):
        o.append(vbox(f"{pre}i{i}", left + i * (w + gap), top, w, h, v, "#C9CED8", "#FFFFFF", fs=fs))
        o.append(down(left + i * (w + gap) + w / 2, top + h + 10))
    by = top + h + 46
    o.append(f'<div id="{pre}band" style="position:absolute;left:{left}px;top:{by}px;width:{width}px;height:{band_h}px;border-radius:20px;background:{color};display:flex;align-items:center;justify-content:center">'
             + p(f"font-family:{MONO};font-size:{fs - 2}px;font-weight:700;color:#FFFFFF;white-space:pre", e(fn)) + '</div>')
    ry = by + band_h + 46
    for i, v in enumerate(outs):
        x = left + i * (w + gap)
        ok = keep is None or keep[i]
        at = f' data-build-in="{"fly" if ok else "fade"} order {orders[i]}"' + (f' data-from="{pre}i{i}"' if ok else "")
        o.append(down(x + w / 2, by + band_h + 10, color if ok else "#E1DED6", f' data-build-in="fade order {orders[i]}"'))
        o.append(vbox(f"{pre}o{i}", x, ry, w, h, v, color if ok else "#C9CED8", bg if ok else "#FFFFFF", at, fs, dashed=not ok, crossed=not ok))
    return o, ry + h


def rows_plain(left, top, w, head_, rows, widths, order0=None, rh=78, fs=30, ids=None, chips=False):
    """A light table: gray header over a dark rule, rows split by thin rules, no boxes."""
    o = [f'<div style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:54px;display:flex;flex-direction:row;align-items:center;gap:20px;border-bottom:3px solid {INK}">'
         + "".join(p(f"width:{cw}px;flex:none;font-family:{MONO if h_.isascii() else SANS};font-size:24px;font-weight:700;color:{GRAY};white-space:nowrap", e(h_)) for h_, cw in zip(head_, widths)) + '</div>']
    for i, r in enumerate(rows):
        cells_ = ""
        for k, (c, cw) in enumerate(zip(r, widths)):
            if chips and c in ("True", "False"):
                cells_ += f'<div style="width:{cw}px;flex:none">' + tf(c, fs - 4) + '</div>'
            else:
                code = c.isascii() and c != ""
                cells_ += p(f"width:{cw}px;flex:none;font-family:{MONO if code else SANS};font-size:{fs}px;font-weight:{700 if (k == 0 or code) else 500};color:{INK};white-space:nowrap", e(c))
        at = f' data-build-in="rise order {order0 if isinstance(order0, int) else order0[i]}"' if order0 else ""
        rid = f' id="{ids[i]}"' if ids else ""
        o.append(f'<div{rid}{at} style="position:absolute;left:{left}px;top:{top + 54 + i * rh}px;width:{w}px;height:{rh}px;display:flex;flex-direction:row;align-items:center;gap:20px;border-bottom:2px solid {LINE}">{cells_}</div>')
    return o


def anchor(aid, left, top, line_i, line, k0, k1):
    """An invisible box over characters k0..k1 of a code line, used as the start of a fly."""
    x0, x1 = cx(left, line, k0), cx(left, line, k1)
    return f'<div id="{aid}" style="position:absolute;left:{x0:.0f}px;top:{top + 10 + line_i * LHf():.0f}px;width:{x1 - x0:.0f}px;height:{LHf():.0f}px"></div>'


def finish(parts, toc_note, title):
    page = {sid: i + 1 for i, sid in enumerate(ORDER)}
    t = [f'<section id="toc" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
         f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>']
    for i, (ic, c, h, s, a, b) in enumerate(parts, 1):
        y = 196 + (i - 1) * 118
        t.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:118px;display:flex;flex-direction:row;align-items:center;gap:36px;border-bottom:2px solid {LINE}">'
                 + p(f"width:64px;flex:none;font-size:56px;font-weight:900;color:{c};text-align:center", str(i))
                 + p(f"width:470px;flex:none;font-size:38px;font-weight:700;color:{INK};white-space:nowrap", e(h))
                 + p(f"flex:1;font-size:27px;line-height:1.4;color:{SUB}", e(s))
                 + p(f"width:150px;flex:none;font-size:27px;font-weight:700;color:{GRAY};text-align:right;white-space:nowrap", f"{page[a]}–{page[b]}쪽") + '</div>')
    t.append(p(f"position:absolute;left:96px;top:930px;width:1728px;font-size:28px;color:{SUB}", f'{page["ready"]}쪽은 노트북 준비, {page["trouble"]}–{page["cheatsheet"]}쪽은 막힐 때와 한 장 요약이에요.'))
    with open(os.path.join(OUT, "toc.html"), "w") as f:
        f.write("\n".join(t) + f"\n<aside>{e(toc_note)}</aside>\n</section>\n")
    deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-04T03:00:00Z"}, "lists": "css", "title": title, "order": ORDER,
            "sections": SECTIONS,
            "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                      "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
            "designSystems": []}
    with open(os.path.join(OUT, "deck.json"), "w") as f:
        json.dump(deck, f, ensure_ascii=False, indent=2)
    print(len(ORDER), "slides")


L = 96              # left edge of the content
FULL = 1728         # full content width

# ---------- cover ----------
cover([(PR, "#E6E9EF"), ("", "#E6E9EF"), ("list(map(lambda p: p + 500, prices))", "#8FD8DE"), ("# [5000, 5500, 7000]", "#9AA1AE"), ("", "#E6E9EF"),
       ("list(filter(lambda p: p >= 5000, prices))", "#E3B877"), ("# [5000, 6500]", "#9AA1AE")],
      "함수 3<br>lambda<br>map, filter", "짧은 함수는 이름 없이 만들고<br>리스트 전체에 한 번에 쓰기",
      "이번 챕터는 함수를 값처럼 넘겨서 리스트 전체에 한 번에 쓰는 법이에요. 19와 20에서 def로 함수를 만들었어요. 이번에는 함수를 변수에 담고 다른 함수에 넘겨요. 한 줄짜리 함수는 lambda로 이름 없이 만들어요. 값마다 함수를 쓰는 map, 조건에 맞는 값만 남기는 filter를 같이 배워요. 22의 정렬과 23의 리스트 컴프리헨션이 이 챕터를 바탕으로 해요.")

# ---------- ready ----------
o = [sec("ready")] + head("들어가기", "20에서 이어서 basics.ipynb에 적어요", JP)
STEPS = [("VS Code로 hello-uv 폴더 열기", None), ("탐색기에서 basics.ipynb 열기", None), ("오른쪽 위 커널이 .venv인지 보기", "venv-row"), ("셀에 적고 Shift+Enter로 실행", None)]
for i, (s_, rid) in enumerate(STEPS):
    y = 220 + i * 150
    idt = f' id="{rid}"' if rid else ""
    o.append(f'<div{idt} style="position:absolute;left:{L}px;top:{y}px;width:980px;height:110px;display:flex;flex-direction:row;align-items:center;gap:30px">'
             + num(i + 1, JP, 48) + p(f"font-size:38px;font-weight:700;color:{INK};white-space:nowrap", e(s_)) + '</div>')
o.append(spot(1, target="venv-row", pad=16, r=20))
o.append(spot_off(2))
o.append(txt(1180, 214, "앞에서 배운 것", 26, GRAY))
for i, (a_, b_) in enumerate([("리스트, 튜플, for, append", "13"), ("딕셔너리 키로 for 돌기", "15"), ("if, 한 줄 if else", "17"), ("def, return, 괄호를 뺀 hello", "19"), ("키워드 인자 reverse=True", "20")]):
    y = 266 + i * 104
    o.append(f'<div style="position:absolute;left:1180px;top:{y}px;width:644px;height:104px;display:flex;flex-direction:row;align-items:center;gap:20px;border-bottom:2px solid {LINE}">'
             + p(f"flex:1;font-size:30px;font-weight:500;color:{INK};white-space:nowrap", e(a_))
             + p(f"font-size:26px;font-weight:700;color:{JP};background:#F8EADF;border-radius:999px;padding:4px 18px", b_) + '</div>')
o.append(caption("기억이 안 나는 줄은 오른쪽 번호의 챕터를 먼저 다시 봐요."))
W("ready", o, "노트북을 열고 커널이 .venv인지 먼저 확인해요. 09에서 만든 hello-uv 폴더를 VS Code로 열고, 12부터 쓰던 basics.ipynb를 다시 열어요. 커널이 .venv가 아니면 셀이 실행되지 않거나 다른 파이썬으로 돌아가요. 13의 리스트와 튜플, 15의 딕셔너리, 17의 한 줄 if else, 19의 def와 return을 그대로 써요. 19에서 괄호를 빼고 hello만 적으면 함수 자체가 나왔던 장면을 기억해 두면 2파트가 쉬워요. 슬라이드의 출력은 tools/demo.sh가 hello-uv 커널에서 같은 셀을 실제로 실행한 결과예요. 셀 번호는 파트마다 [1]부터 다시 셌어요.")

# ---------- part 1 ----------
CFS[0] = 40
o = [sec("l-why")] + head(EB1, "가격을 바꿀 때마다 for 네 줄을 다시 적어요", K1)
WHY = [PR, "up = []", "for p in prices:", "    up.append(p + 500)", "print(up)", "down = []", "for p in prices:", "    down.append(p - 500)", "print(down)"]
T = 196
o += cell({"id": "c-why", "lines": WHY, "n": 1, "out": ["[5000, 5500, 7000]", "[4000, 4500, 6000]"]}, L, T, 1300, sel="c-why")
o.append(hl(L, T, 1300, 3, 1, "mark", 1))
o.append(hl(L, T, 1300, 7, 1, "mark", 1))
o.append(tag(tx(L, WHY[1:]), ly(T, 3), "500원 올리기", K1, 1, 32))
o.append(tag(tx(L, WHY[1:]), ly(T, 7), "500원 내리기", K1, 1, 32))
o.append(tag(tx(L, WHY[1:]), (ly(T, 1) + ly(T, 2)) / 2, "나머지는 똑같아요", GRAY, 2, 30))
o.append(tag(tx(L, WHY[1:]), (ly(T, 5) + ly(T, 6)) / 2, "나머지는 똑같아요", GRAY, 2, 30))
SAT = "up = list(map(lambda p: p + 500, prices))"
o.append(f'<div data-build-in="rise order 3" style="position:absolute;left:1030px;top:700px;width:794px;height:180px;background:#FFFFFF;border-radius:20px;box-shadow:0 1px 0 #E1DED6,0 14px 34px rgba(29,35,48,0.16);padding:28px 34px;display:flex;flex-direction:column;justify-content:center;gap:12px">'
         + p(f"font-size:26px;font-weight:700;color:{K3}", "이번 챕터에서 배우면 한 줄이에요")
         + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{INK};white-space:pre", e(SAT)) + '</div>')
o.append(caption("두 덩어리에서 다른 건 한 줄뿐이에요."))
W("l-why", o, "같은 틀을 두 번 적었는데 다른 건 한 줄뿐이에요. 13의 가격 리스트로 모든 가격을 500원 올리고, 다시 500원 내려 봐요. 빈 리스트를 만들고, for로 돌고, append로 담는 네 줄이 두 번 나와요. 두 덩어리에서 달라진 건 p + 500과 p - 500이에요. 값마다 같은 일을 해서 새 리스트를 만드는 틀은 앞으로도 자주 나와요. 오른쪽 아래 한 줄이 이번 챕터에서 배울 모양이에요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p1", "왜 필요한가"))

o = [sec("l-big")] + head(EB1, "map은 하나씩 바꾸고, filter는 골라내요", K1)
o.append(txt(L, 196, "map(함수, 리스트)", 36, K3, mono_=True))
o.append(txt(L + 400, 202, "값마다 바꿔요", 30, SUB))
pm, yb = pipe2("bm", L, 280, ["4500", "5000", "6500"], "p + 500", ["5000", "5500", "7000"], K3, K3BG, [1, 1, 1])
o += pm
o.append(txt(1072, 196, "filter(함수, 리스트)", 36, K4, mono_=True))
o.append(txt(1072 + 460, 202, "골라내요", 30, SUB))
pf, _ = pipe2("bf", 1072, 280, ["4500", "5000", "6500"], "p >= 5000", ["4500", "5000", "6500"], K4, K4BG, [2, 2, 2], keep=[False, True, True])
o += pf
o.append(txt(L, yb + 26, "결과도 3개예요", 30, K3, attrs=' data-build-in="fade order 3"'))
o.append(txt(1072, yb + 26, "True인 값만 남아서 2개예요", 30, K4, attrs=' data-build-in="fade order 3"'))
o.append(caption("가운데 띠에 넣는 짧은 함수를 lambda로 만들어요."))
W("l-big", o, "map은 값마다 바꾸고, filter는 조건에 맞는 값만 남겨요. map은 리스트의 값을 하나씩 가운데 함수에 넣어요. 함수가 돌려준 값을 순서대로 모아서 새 결과를 만들어요. 값이 셋이면 결과도 셋이에요. filter도 값을 하나씩 함수에 넣는데, 함수는 True나 False를 돌려줘요. True인 값만 아래로 내려가고 False인 값은 버려요. 값은 바뀌지 않고 개수만 줄어요. 가운데 띠에 들어가는 p + 500, p >= 5000 같은 짧은 함수를 lambda로 만들어요.")

CFS[0] = 34
o = [sec("l-min")] + head(EB1, "가장 짧은 map: 값마다 10 더하기", K1)
MIN = ["numbers = [1, 2, 3]", "print(list(map(lambda x: x + 10, numbers)))"]
o += cell({"id": "c-min", "lines": MIN, "n": 3, "out": ["[11, 12, 13]"]}, L, 196, FULL, sel="c-min")
AN = "list(map(lambda x: x + 10, numbers))"
AF = 52
ax = lambda k: 201 + k * AF * 0.6
o.append(txt(201, 470, e(AN), AF, INK, mono_=True))
for (k0, k1, y, col, lab, od) in [(9, 25, 572, K2, "x를 받아 x + 10을 돌려주는 함수", 1), (5, 35, 652, K3, "numbers의 값마다 그 함수를 써요", 2), (0, 36, 732, K1, "나온 값을 리스트로 모아요", 3)]:
    o.append(bracket(od, ax(k0), ax(k1), y, col))
    o.append(txt(ax(k0), y + 10, e(lab), 30, col, attrs=f' data-build-in="fade order {od}"'))
o.append(caption("함수와 리스트를 map에 넘기면, 값마다 함수를 써서 결과를 모아 줘요."))
W("l-min", o, "lambda로 함수를 만들고, map이 값마다 쓰고, list가 모아요. numbers의 값 1, 2, 3에 10씩 더해요. lambda x: x + 10은 x를 받아 x + 10을 돌려주는 함수예요. 2파트에서 자세히 봐요. map은 이 함수를 numbers의 값마다 써요. 1을 넣으면 11, 2를 넣으면 12, 3을 넣으면 13이 나와요. 마지막으로 list로 감싸서 [11, 12, 13] 리스트로 모아요. list가 왜 필요한지는 3파트에서 봐요. 앞 장의 for 네 줄이 한 줄이 됐어요." + REAL)

# ---------- part 2 ----------
CFS[0] = 40
o = [sec("v-value")] + head(EB2, "함수도 변수에 담을 수 있어요", K2)
VV = ["def add10(x):", "    return x + 10", "", "plus = add10", "print(plus(5))", "print(add10)"]
T = 196
VVO = ["15", "<function add10 at 0x7fdb817ce4b0>"]
o += cell({"id": "c-v1", "lines": VV, "n": 1, "out": VVO}, L, T, 1000, sel="c-v1")
o.append(anchor("a-plus", L, T, 3, VV[3], 0, 4))
o.append(hl(L, T, 1000, 3, 1, "mark", 1))
o.append(tag(tx(L, VV[:5]), ly(T, 3), "괄호 없이 담아요", K2, 1, 30))
# satellite: two name tags on one function
o.append(f'<div style="position:absolute;left:1250px;top:226px">{chip("add10", K2, K2BG, 36)}</div>')
o.append(f'<div id="sat-plus" data-build-in="fly order 2" data-from="a-plus" style="position:absolute;left:1580px;top:226px">{chip("plus", K2, K2BG, 36)}</div>')
o.append(down(1326, 316))
o.append(down(1636, 316, attrs=' data-build-in="fade order 2"'))
o.append(f'<div style="position:absolute;left:1180px;top:370px;width:644px;height:220px;border-radius:24px;background:{K2};display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px">'
         + p("font-size:28px;font-weight:700;color:#FFFFFF", "함수 하나") + p(f"font-family:{MONO};font-size:36px;font-weight:700;color:#FFFFFF", "x를 받아 x + 10") + '</div>')
o.append(txt(1180, 620, "같은 함수에 이름이 하나 더 생겨요", 30, K2, attrs=' data-build-in="fade order 2"'))
o.append(caption("괄호를 빼면 함수를 실행하지 않고 값처럼 다룰 수 있어요."))
W("v-value", o, "괄호 없이 적은 함수 이름은 함수 그 자체라서 변수에 담을 수 있어요. 19에서 괄호를 빼고 hello만 적었더니 함수 자체가 나왔어요. 함수도 숫자나 리스트처럼 하나의 값이에요. 그래서 plus = add10처럼 다른 변수에 담을 수 있어요. 괄호가 없으니 add10을 실행하지 않고 함수 그대로 담아요. 이제 plus와 add10은 같은 함수를 가리켜서 plus(5)도 15예요. print(add10)의 0x로 시작하는 숫자는 함수가 저장된 메모리 위치라서 화면마다 달라요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p2", "함수를 값처럼, lambda"))

CFS[0] = 38
o = [sec("v-pass")] + head(EB2, "함수를 다른 함수에 넘길 수 있어요", K2)
VP = ["def double(x):", "    return x * 2", "", "def apply(f, x):", "    return f(x)", "", "print(apply(add10, 5))", "print(apply(double, 5))"]
T = 196
o += cell({"id": "c-v2", "lines": VP, "n": 2, "out": ["15", "10"]}, L, T, 1000, sel="c-v2")
o.append(hl(L, T, 1000, 4, 1, "mark", 1))
o.append(tag(tx(L, VP), ly(T, 4), "받은 함수를 불러요", K2, 1, 30))
o.append(uline(2, L, VP[6], 12, 17, ly(T, 6), OR))
o.append(uline(2, L, VP[7], 12, 18, ly(T, 7), OR))
o.append(tag(tx(L, VP), (ly(T, 6) + ly(T, 7)) / 2, "이름만 넘겨요", OR, 2, 30))
for i, (a_, b_, c_) in enumerate([("apply(add10, 5)", "add10(5)", "15"), ("apply(double, 5)", "double(5)", "10")]):
    y = 300 + i * 220
    o.append(f'<div data-build-in="rise order {i + 3}" style="position:absolute;left:1180px;top:{y}px;width:644px;display:flex;flex-direction:column;gap:14px">'
             + p(f"font-family:{MONO};font-size:34px;font-weight:700;color:{INK};white-space:pre", e(a_))
             + '<div style="display:flex;flex-direction:row;align-items:center;gap:18px">' + arrow(46, K2) + mono(b_, 34, K2, K2BG) + arrow(46, K2) + p(f"font-family:{MONO};font-size:34px;font-weight:700;color:{INK}", c_) + '</div></div>')
o.append(caption("함수도 인자로 넘길 수 있어요. 넘길 때는 이름만 적어요."))
W("v-pass", o, "함수가 값이라서 다른 함수의 인자로도 넘길 수 있어요. apply는 함수 f와 값 x를 받아서 f(x)를 돌려줘요. apply(add10, 5)로 부르면 f 칸에 add10이 들어가서 add10(5)가 되고 15가 나와요. double을 넘기면 double(5)가 돼서 10이에요. 넘길 때 add10에 괄호를 붙이지 않은 점을 봐 둬요. 괄호를 붙이면 그 자리에서 실행해 버려요. 3파트의 map과 4파트의 filter가 바로 이렇게 함수를 받는 함수예요. add10은 앞 셀에서 정의했어요." + REAL)

o = [sec("d-side")] + head(EB2, "lambda는 한 줄로 만드는 이름 없는 함수예요", K2)
LB, LX, LC, LV = "#9DBDEB", "#8FD8DE", "#F2A0A0", "#B8E8BE"
WH = "#E6E9EF"
sp = lambda t, c, sid=None, at="": (f'<span{" id=" + chr(34) + sid + chr(34) if sid else ""}{at} style="display:inline-block;white-space:pre;color:{c}">{e(t)}</span>')
o.append(txt(L, 196, "19의 def", 26, GRAY))
o.append(f'<div style="position:absolute;left:{L}px;top:240px;width:760px;height:170px;background:#252B36;border-radius:22px;padding:24px 40px;display:flex;flex-direction:column;justify-content:center;gap:4px">'
         + p(f"font-family:{MONO};font-size:38px;font-weight:700;line-height:1.45;white-space:pre", sp("def", LB) + sp(" add10", "#E3B877") + sp("(", WH) + sp("x", LX, "dx") + sp("):", WH))
         + p(f"font-family:{MONO};font-size:38px;font-weight:700;line-height:1.45;white-space:pre", sp("    return ", WH) + sp("x + 10", LV, "dv")) + '</div>')
LF = 76
LX0 = 136
lxk = lambda k: LX0 + k * LF * 0.6
o.append(txt(L, 456, "lambda", 26, K2, attrs=' data-build-in="fade order 1"'))
o.append(f'<div data-build-in="rise order 1" style="position:absolute;left:{L}px;top:500px;width:980px;height:170px;background:#252B36;border-radius:22px;padding:0 40px;display:flex;align-items:center">'
         + p(f"font-family:{MONO};font-size:{LF}px;font-weight:700;line-height:1.2;white-space:pre", sp("lambda", LB) + sp(" ", WH) + sp("x", LX, None, ' data-build-in="fly order 2" data-from="dx"') + sp(":", LC) + sp(" ", WH) + sp("x + 10", LV, None, ' data-build-in="fly order 2" data-from="dv"')) + '</div>')
PIECES = [(0, 6, "lambda", "def 대신 써요", BL, 136), (7, 8, "x", "매개변수, 괄호 없이", TEAL, 480), (8, 9, ":", "뒤가 돌려줄 값", RED, 820), (10, 16, "x + 10", "return 없이 돌려줘요", GR, 1160)]
for i, (k0, k1, code, d_, c_, lx) in enumerate(PIECES):
    od = 3 + i
    pxc = (lxk(k0) + lxk(k1)) / 2
    o.append(leader(od, pxc, 650, lx + 10, 742, c_))
    o.append(f'<div data-build-in="fade order {od}" style="position:absolute;left:{lx}px;top:752px;width:400px;display:flex;flex-direction:column;gap:6px">'
             + p(f"font-family:{MONO};font-size:34px;font-weight:700;color:{c_}", e(code)) + p(f"font-size:28px;font-weight:700;color:{INK};white-space:nowrap", e(d_)) + '</div>')
o.append(caption("이름, 괄호, return을 빼고 매개변수와 돌려줄 값만 남긴 모양이에요."))
W("d-side", o, "lambda는 def에서 이름, 괄호, return을 빼고 매개변수와 돌려줄 값만 남긴 함수예요. 위는 19에서 배운 def 함수예요. 아래 lambda도 같은 일을 하는 함수예요. def의 x와 x + 10이 그대로 lambda로 옮겨 가요. lambda는 def처럼 함수를 만든다는 표시예요. 그 뒤 x가 매개변수인데 괄호 없이 적어요. 콜론 뒤에는 돌려줄 값을 적어요. return을 쓰지 않아도 이 값이 돌아가요. 함수 이름 자리가 없어서 이름 없는 함수라고 불러요. 몸통에는 값 하나만 적을 수 있어요.")

CFS[0] = 38
o = [sec("d-call")] + head(EB2, "lambda는 다른 함수에 바로 넘길 때 써요", K2)
D1 = ["add10 = lambda x: x + 10", "print(add10(5))", "print(add10)"]
D1O = ["15", "<function <lambda> at 0x7fdb817cf270>"]
o.append(txt(L, 196, "변수에 담아 부르기", 26, GRAY))
T1 = 236
o += cell({"id": "c-d1", "lines": D1, "n": 3, "out": D1O}, L, T1, FULL, sel="c-d1")
o.append(pen_box(1, L, D1O[1], 10, 18, oy(T1, 3, 1), K2))
o.append(tag(ox(L, D1O[1], 38) + 40, oy(T1, 3, 1), "이름 자리가 비어 있어요", K2, 1, 30))
T2 = 670
o.append(txt(L, T2 - 40, "이름 없이 바로 넘기기", 26, K2, attrs=' data-build-in="fade order 2"'))
D2 = ["print(apply(lambda x: x * 3, 5))"]
o += cell({"id": "c-d2", "lines": D2, "n": 4, "out": ["15"]}, L, T2, FULL, attrs=' data-build-in="rise order 2"')
o.append(uline(3, L, D2[0], 12, 27, ly(T2, 0), OR))
o.append(tag(tx(L, D2), ly(T2, 0), "앞 장의 apply에 그 자리에서 만들어 넘겨요", OR, 3, 30))
o.append(caption("한 번 쓰고 말 짧은 함수는 lambda로 그 자리에 적어요."))
W("d-call", o, "lambda는 한 번 쓰고 말 함수를 다른 함수에 바로 넘길 때 가장 많이 써요. lambda로 만든 함수도 변수에 담아 부를 수 있어요. add10(5)는 15예요. print로 찍으면 함수 이름 자리에 lambda가 나와요. 이름 없는 함수라서예요. 아래 셀은 앞 장의 apply에 x를 3배 하는 함수를 이름 없이 적어서 넘겼어요. 한 번 쓰고 말 함수에 def와 이름까지 붙이지 않아도 돼요. 반대로 여러 번 부를 함수라면 add10 = lambda보다 def add10(x):가 읽기 쉬워요. apply는 앞 셀에서 정의했어요." + REAL)

CFS[0] = 32
o = [sec("d-more")] + head(EB2, "매개변수 여러 개, 한 줄 if else도 돼요", K2)
DM = ["price_of = lambda price, qty: price * qty", "print(price_of(4500, 2))", 'label = lambda p: "비쌈" if p >= 5000 else "보통"', "print(label(6500), label(4500))"]
T = 196
o += cell({"id": "c-d3", "lines": DM, "n": 5, "out": ["9000", "비쌈 보통"]}, L, T, FULL, sel="c-d3")
o.append(uline(1, L, DM[0], 18, 28, ly(T, 0), K2))
o.append(tag(tx(L, DM), ly(T, 0), "쉼표로 둘", K2, 1, 30))
o.append(uline(2, L, DM[2], 18, len(DM[2]), ly(T, 2), K2))
o.append(tag(tx(L, DM), ly(T, 2), "17의 한 줄 if else", K2, 2, 30))
TR = [("이름", "있어요", "없어요"), ("몸통", "여러 줄", "값 하나"), ("return", "적어요", "안 적어요"), ("언제", "여러 번 부를 함수", "다른 함수에 바로 넘길 때")]
o += rows_plain(L, 540, FULL, ["", "def", "lambda"], TR, [240, 640, 760], 3, 80, 32, ids=["dm-r0", "dm-r1", "dm-r2", "dm-r3"])
o.append(spot(4, target="dm-r1", pad=10, r=12))
o.append(spot_off(5))
W("d-more", o, "lambda도 매개변수를 여러 개 받고, 값 하나로 계산되는 한 줄 if else를 쓸 수 있어요. price_of는 가격과 잔 수를 쉼표로 받아 곱한 값을 돌려줘요. 콜론 뒤에는 값 하나만 올 수 있어서 17의 if 문은 못 넣어요. 대신 17에서 배운 한 줄 if else는 값 하나로 계산되니까 쓸 수 있어요. 아래 표에 def와 lambda를 나란히 정리했어요. 가장 큰 차이는 몸통이에요. def는 여러 줄, lambda는 값 하나예요. 여러 번 부를 함수는 def, 다른 함수에 바로 넘길 짧은 함수는 lambda로 만들어요." + REAL)

# ---------- part 3 ----------
CFS[0] = 32
o = [sec("m-three")] + head(EB3, "for 네 줄이 map 한 줄이 돼요", K3)
MT = [PR, "", "def add500(p):", "    return p + 500", "", "print(list(map(add500, prices)))", "print(list(map(lambda p: p + 500, prices)))", "print(prices)"]
T = 196
o += cell({"id": "c-m1", "lines": MT, "n": 1, "out": ["[5000, 5500, 7000]", "[5000, 5500, 7000]", "[4500, 5000, 6500]"]}, L, T, FULL, sel="c-m1")
TX_ = tx(L, MT)
o.append(line_spot(1, L, T, 5, 1, TX_ + 360))
o.append(tag(TX_, ly(T, 5), "def로 만든 이름 넘기기", K3, 1, 30))
o.append(line_spot(2, L, T, 6, 1, TX_ + 360))
o.append(tag(TX_, ly(T, 6), "lambda 바로 넘기기", K3, 2, 30))
o.append(line_spot(3, L, T, 7, 1, TX_ + 360))
o.append(tag(TX_, ly(T, 7), "원본은 그대로", GRAY, 3, 30))
o.append(spot_off(4))
FOR3 = ["up = []", "for p in prices:", "    up.append(p + 500)"]
o.append(f'<div data-build-in="rise order 4" style="position:absolute;left:1180px;top:640px;width:644px;height:250px;background:#FFFFFF;border-radius:20px;box-shadow:0 1px 0 #E1DED6,0 14px 34px rgba(29,35,48,0.16);padding:26px 34px;display:flex;flex-direction:column;gap:6px">'
         + p(f"font-size:26px;font-weight:700;color:{GRAY};margin-bottom:6px", "1파트의 for도 같은 결과예요")
         + "".join(p(f"font-family:{MONO};font-size:30px;font-weight:700;line-height:1.45;color:{INK};white-space:pre", e(l)) for l in FOR3) + '</div>')
o.append(caption("map(함수, 리스트)는 for와 append로 새 리스트를 만드는 일을 한 줄로 줄여요."))
W("m-three", o, "for와 append 네 줄, def 넘기기, lambda 넘기기 모두 같은 결과예요. 결과는 셋 다 [5000, 5500, 7000]이에요. def로 넘길 때는 add500에 괄호를 붙이지 않아요. 2파트에서 본 것처럼 함수를 넘기는 거라서예요. map은 새 결과를 만들고 prices는 그대로 둬요. 13의 sorted가 원본을 두고 새 리스트를 준 것과 같아요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p3", "map"))

o = [sec("m-pic")] + head(EB3, "map은 값을 하나씩 함수에 넣어요", K3)
pp, yb = pipe2("mp", L, 230, ["4500", "5000", "6500"], "lambda p: p + 500", ["5000", "5500", "7000"], K3, K3BG, [1, 2, 3], w=280, h=140, fs=40, band_h=120)
o += pp
for i, (pv, rv) in enumerate([("4500", "5000"), ("5000", "5500"), ("6500", "7000")]):
    y = 250 + i * 170
    o.append(f'<div data-build-in="fade order {i + 1}" style="position:absolute;left:1060px;top:{y}px;width:764px;height:120px;display:flex;flex-direction:row;align-items:center;gap:22px;border-bottom:2px solid {LINE}">'
             + p(f"width:56px;flex:none;font-size:36px;font-weight:900;color:{K3}", str(i + 1))
             + p(f"width:250px;flex:none;font-family:{MONO};font-size:34px;font-weight:700;color:{INK};white-space:pre", f"p = {pv}")
             + arrow(46, K3) + p(f"font-family:{MONO};font-size:34px;font-weight:700;color:{K3}", rv) + '</div>')
o.append(txt(L, yb + 30, "넣은 순서대로 3개가 나와요", 30, K3, attrs=' data-build-in="fade order 4"'))
o.append(caption("map이 리스트의 값을 차례로 lambda의 p에 넣고, 돌려받은 값을 모아요."))
W("m-pic", o, "map은 리스트의 값을 하나씩 lambda의 p 칸에 넣고, 돌려받은 값을 순서대로 모아요. 첫 값 4500이 p 칸에 들어가서 5000이 돌아와요. 다음 5000이 들어가 5500, 6500이 들어가 7000이 돌아와요. 그래서 결과는 원래 순서 그대로이고 개수도 같아요. lambda의 p는 13에서 for p in prices:라고 적었을 때 p와 같은 역할이에요.")

CFS[0] = 34
o = [sec("m-obj")] + head(EB3, "map만 찍으면 &lt;map object&gt;가 나와요", K3)
MO = ["m = map(lambda p: p + 500, prices)", "print(m)", "print(list(m))"]
MOO = ["<map object at 0x7fe9b3214840>", "[5000, 5500, 7000]"]
T = 196
o += cell({"id": "c-m2", "lines": MO, "n": 2, "out": MOO}, L, T, FULL, sel="c-m2")
o.append(pen_box(1, L, MOO[0], 0, len(MOO[0]), oy(T, 3, 0), K3))
o.append(tag(ox(L, MOO[0], len(MOO[0])) + 40, oy(T, 3, 0), "값을 꺼내 줄 준비만 한 묶음이에요", K3, 1, 30))
o.append(tag(ox(L, MOO[0], len(MOO[0])) + 40, oy(T, 3, 1), "list()가 끝까지 꺼내 모아요", GR, 2, 30))
T2 = 560
MF = ["for p in map(lambda p: p + 500, prices):", "    print(p)"]
o += cell({"id": "c-m3", "lines": MF, "n": 3, "out": ["5000", "5500", "7000"]}, L, T2, FULL, attrs=' data-build-in="rise order 3"')
o.append(tag(tx(L, MF), ly(T2, 0), "for도 하나씩 꺼내 써요", K3, 3, 30))
o.append(caption("결과를 리스트로 보려면 list()로 감싸요."))
W("m-obj", o, "map만 찍으면 결과 대신 값을 꺼내 줄 준비만 한 map object가 나와요. 오류가 아니에요. map은 결과를 바로 다 만들지 않고, 달라고 하면 값을 하나씩 꺼내 주는 묶음을 돌려줘요. list로 감싸면 값을 끝까지 꺼내서 리스트로 모아요. 그래서 지금까지 list(map(...))처럼 적었어요. for도 값을 하나씩 꺼내니까 찍기만 할 때는 list 없이 for로 돌려도 돼요. 0x 뒤 숫자는 메모리 위치라서 화면마다 달라요." + REAL)

CFS[0] = 40
o = [sec("m-builtin")] + head(EB3, "이미 있는 함수도 이름만 넘겨요", K3)
MB = ["print(list(map(str, prices)))", 'print(", ".join(map(str, prices)))', 'print(list(map(int, ["3", "1", "2"])))', 'print(list(map(len, ["coffee", "latte", "tea"])))']
T = 196
o += cell({"id": "c-m4", "lines": MB, "n": 4, "out": ["['4500', '5000', '6500']", "4500, 5000, 6500", "[3, 1, 2]", "[6, 5, 3]"]}, L, T, FULL, sel="c-m4")
TX_ = tx(L, MB)
for od, (li, k0, k1, lab, col) in enumerate([(0, 15, 18, "str: 숫자를 글자로", K3), (1, 20, 23, "join 앞에서 글자로 바꾸기", K3), (2, 15, 18, "int: 글자를 숫자로", OR), (3, 15, 18, "len: 값마다 길이 재기", BL)], 1):
    o.append(uline(od, L, MB[li], k0, k1, ly(T, li), col))
    o.append(tag(TX_, ly(T, li), lab, col, od, 28))
o.append(caption("str, int, len처럼 이미 있는 함수로 되는 일은 lambda 없이 이름만 넘겨요."))
W("m-builtin", o, "str, int, len처럼 이미 있는 함수는 lambda 없이 괄호 뺀 이름만 map에 넘겨요. 12에서 배운 str, int와 13의 len도 함수라서 이름만 넘기면 돼요. map(str, prices)는 가격마다 str을 써서 글자 리스트를 만들어요. 13의 join은 글자만 이을 수 있어서 숫자 리스트를 넣으면 오류가 나요. map(str, prices)를 넘기면 쉼표로 이은 한 줄이 돼요. int는 반대로 글자를 숫자로 바꾸고, len은 값마다 길이를 재요." + REAL)

# ---------- part 4 ----------
CFS[0] = 40
o = [sec("f-for")] + head(EB4, "for와 if로 골라 담던 일을 filter 한 줄로", K4)
FF = ["prices = [4500, 5000, 6500, 3000]", "big = []", "for p in prices:", "    if p >= 5000:", "        big.append(p)", "print(big)", "print(list(filter(lambda p: p >= 5000, prices)))"]
T = 196
o += cell({"id": "c-f1", "lines": FF, "n": 1, "out": ["[5000, 6500]", "[5000, 6500]"]}, L, T, FULL, sel="c-f1")
o.append(hl(L, T, FULL, 1, 4, "mark", 1))
o.append(tag(tx(L, FF[1:6]), ly(T, 3), "17에서 for 안의 if로 골라 담기", K4, 1, 30))
o.append(hl(L, T, FULL, 6, 1, "run", 2))
o.append(tag(ox(L, "[5000, 6500]", 12) + 40, (oy(T, 7, 0) + oy(T, 7, 1)) / 2, "결과가 같아요", GR, 3, 30))
o.append(caption("for 안의 if로 골라 담는 일은 filter 한 줄로 줄여요."))
W("f-for", o, "for 안의 if로 골라 담던 다섯 줄을 filter 한 줄로 바꿀 수 있어요. 17에서 5000원 이상인 가격만 big에 담았어요. filter의 첫째 인자는 조건 함수이고, 둘째는 리스트예요. 조건 함수가 True를 돌려준 값만 남아요. lambda p: p >= 5000은 p가 5000 이상인지 True나 False로 답해요. filter도 map처럼 결과를 꺼내 줄 준비만 하니까 list로 감싸서 봐요. 원본 prices는 그대로예요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p4", "filter"))

o = [sec("f-pic")] + head(EB4, "True를 받은 값만 아래로 내려가요", K4)
pp, yb = pipe2("fp", L, 220, ["4500", "5000", "6500", "3000"], "lambda p: p >= 5000", ["4500", "5000", "6500", "3000"], K4, K4BG, [1, 2, 3, 4], w=210, h=130, gap=16, keep=[False, True, True, False], fs=36)
o += pp
o.append(txt(1060, 196, "check = lambda p: p >= 5000으로 하나씩 불러 본 결과", 24, GRAY))
o += rows_plain(1060, 250, 764, ["p", "check(p)", "filter는"], [("4500", "False", "버려요"), ("5000", "True", "남겨요"), ("6500", "True", "남겨요"), ("3000", "False", "버려요")], [160, 260, 240], [1, 2, 3, 4], 96, 32, ids=["fr0", "fr1", "fr2", "fr3"], chips=True)
o.append(spot(5, target="fr1", pad=8, r=12))
o.append(txt(1060, 700, "&gt;=라서 5000도 True예요", 30, OR, attrs=' data-build-in="fade order 6"'))
o.append(spot_off(6))
o.append(caption("filter에 넘기는 함수는 True나 False를 돌려주는 조건이에요."))
W("f-pic", o, "filter는 함수가 True를 돌려준 원래 값만 모아요. 값이 하나씩 lambda에 들어가요. 4500은 False라서 버리고, 5000과 6500은 True라서 남겨요. 3000도 False예요. 오른쪽 표는 같은 lambda를 check라는 이름에 담고 값마다 직접 불러 본 결과예요. 5000은 >=라서 같아도 True예요. map은 돌려받은 값을 모으고, filter는 True를 받은 원래 값을 모은다는 점이 달라요. 표의 True, False는 check(4500), check(5000), check(6500), check(3000)을 실제로 실행한 결과예요.")

CFS[0] = 34
o = [sec("f-dict")] + head(EB4, "딕셔너리를 넘기면 키가 하나씩 들어가요", K4)
RES_FD = "['coffee', 'cake']"
FD = ['stock = {"coffee": 3, "latte": 0, "cake": 2, "tea": 0}', "print(list(filter(lambda m: stock[m] > 0, stock)))"]
T = 196
o += cell({"id": "c-f3", "lines": FD, "n": 3, "out": ["['coffee', 'cake']"]}, L, T, FULL, sel="c-f3")
o.append(uline(1, L, FD[1], 29, 37, ly(T, 1), K4))
o.append(tag(ox(L, RES_FD, len(RES_FD)) + 40, oy(T, 2, 0), "m에는 키가 들어가고, 재고는 stock[m]으로 봐요", K4, 1, 30))
LK = [("coffee", "3"), ("latte", "0"), ("cake", "2"), ("tea", "0")]
for i, (k, v) in enumerate(LK):
    x = L + i * 300
    o.append(f'<div id="lk{i}" style="position:absolute;left:{x}px;top:460px;width:280px;height:230px;border-radius:16px;border:3px solid {K4 if v != "0" else "#C9CED8"};background:{K4BG if v != "0" else CARD};display:flex;flex-direction:column;overflow:hidden">'
             + p(f"height:62px;flex:none;background:{K4 if v != '0' else '#ECEAE3'};color:{'#FFFFFF' if v != '0' else INK};font-family:{MONO};font-size:32px;font-weight:700;line-height:62px;text-align:center", e(k))
             + '<div style="flex:1;display:flex;align-items:center;justify-content:center">' + p(f"font-family:{MONO};font-size:56px;font-weight:700;color:{INK}", v) + '</div></div>')
    if v == "0":
        o.append(f'<div data-build-in="fade order 2" style="position:absolute;left:{x}px;top:460px;width:280px;height:230px;border-radius:16px;background:rgba(246,245,241,0.72);border:3px dashed {RED}"></div>')
        o.append(txt(x + 70, 700, "0이라 False", 26, RED, attrs=' data-build-in="fade order 2"'))
o.append(f'<div data-build-in="fly order 3" data-from="lk0" style="position:absolute;left:{L}px;top:770px">{chip(RES_FD, K4, K4BG, 38)}</div>')
o.append(txt(L + 470, 782, "키만 담긴 리스트예요. 재고 숫자는 없어요.", 30, SUB, attrs=' data-build-in="fade order 3"'))
o.append(caption("딕셔너리를 넘기면 키로 골라서, 조건에 맞는 키만 남겨요."))
W("f-dict", o, "filter에 딕셔너리를 넘기면 키가 하나씩 들어가고, 조건에 맞는 키만 남아요. 15에서 딕셔너리를 for로 돌면 키가 나왔던 것과 같아요. 그래서 lambda의 m은 coffee, latte 같은 메뉴 이름이고, 재고는 stock[m]으로 꺼내요. 재고가 0인 latte와 tea는 False라서 빠지고 coffee와 cake만 남았어요. 결과는 키만 담은 리스트라서 재고 숫자는 없어요. 재고까지 같이 담은 딕셔너리로 고르는 방법은 23에서 배워요." + REAL)

CFS[0] = 30
o = [sec("f-chain")] + head(EB4, "고른 다음 바꾸려면 filter 결과를 map에 넘겨요", K4)
FC = ["big = list(filter(lambda p: p >= 5000, prices))", "print(big)", "print(list(map(lambda p: p * 9 // 10, big)))", "print(list(map(lambda p: p * 9 // 10, filter(lambda p: p >= 5000, prices))))"]
T = 196
o += cell({"id": "c-f4", "lines": FC, "n": 4, "out": ["[5000, 6500]", "[4500, 5850]", "[4500, 5850]"]}, L, T, FULL, sel="c-f4")
o.append(hl(L, T, FULL, 0, 3, "mark", 1))
o.append(tag(tx(L, FC[:3]), ly(T, 1), "두 번에 나눠 쓰면 중간 결과 big을 볼 수 있어요", K4, 1, 28))
AN2 = "list(map(lambda p: p * 9 // 10, filter(lambda p: p >= 5000, prices)))"
AF2 = 34
ax2 = lambda k: 201 + k * AF2 * 0.6
o.append(txt(201, 620, e(AN2), AF2, INK, mono_=True, attrs=' data-build-in="fade order 2"'))
i_f = AN2.index("filter")
o.append(bracket(2, ax2(i_f), ax2(len(AN2) - 2), 690, K4))
o.append(txt(ax2(i_f), 700, "① 안쪽 filter가 먼저 골라요", 30, K4, attrs=' data-build-in="fade order 2"'))
o.append(bracket(3, ax2(5), ax2(len(AN2) - 1), 780, K3))
o.append(txt(ax2(5), 790, "② 바깥 map이 고른 값을 바꿔요", 30, K3, attrs=' data-build-in="fade order 3"'))
o.append(caption("고르고 바꾸기를 같이 할 땐 filter로 고른 결과를 map에 넘겨요."))
W("f-chain", o, "고른 다음 바꾸려면 filter로 고른 결과를 map에 넘겨요. 5000원 이상인 메뉴만 10% 할인해 봐요. 먼저 filter로 5000원 이상을 골라 big에 담아요. 그다음 big을 map에 넘겨서 9를 곱하고 10으로 몫 나누기해요. 마지막 줄처럼 filter를 map 안에 바로 넣어도 결과는 같아요. 다만 괄호가 겹쳐서 안쪽 filter부터 읽어야 해요. 처음에는 두 번에 나눠 쓰고 중간 결과를 찍어 보는 편이 좋아요. 같은 일을 한 줄로 더 읽기 쉽게 쓰는 방법은 23의 리스트 컴프리헨션이에요." + REAL)

# ---------- part 5 ----------
CFS[0] = 32
o = [sec("t-list")] + head(EB5, "map 결과에는 번호도 len도 못 써요", K5)
E1 = ["doubled = map(lambda x: x * 2, [1, 2, 3])", "print(doubled[0])"]
E1O = "TypeError: 'map' object is not subscriptable"
T1 = 196
o += cell({"id": "c-t1", "lines": E1, "n": 1, "out": [E1O], "err": True}, L, T1, FULL, sel="c-t1")
o.append(pen_box(1, L, E1O, 0, len(E1O), oy(T1, 2, 0)))
T2 = 412
E2O = "TypeError: object of type 'map' has no len()"
o += cell({"id": "c-t2", "lines": ["print(len(doubled))"], "n": 2, "out": [E2O], "err": True}, L, T2, FULL, attrs=' data-build-in="rise order 2"')
o.append(underline(2, round(ox(L, E2O, 0)), round(ox(L, E2O, len(E2O))), round(oy(T2, 1, 0) + LHf() * 0.42), RED))
o.append(tag(ox(L, E2O, len(E2O)) + 40, oy(T2, 1, 0), "filter 결과도 같아요", RED, 2, 28))
T3 = 600
EF = ["doubled = list(map(lambda x: x * 2, [1, 2, 3]))", "print(doubled[0])", "print(len(doubled))"]
o += cell({"id": "c-t2f", "lines": EF, "n": 3, "out": ["2", "3"]}, L, T3, FULL, attrs=' data-build-in="rise order 3"')
o.append(uline(3, L, EF[0], 10, 15, ly(T3, 0), GR))
o.append(tag(tx(L, EF), ly(T3, 0), "list()로 바꾸면 돼요", GR, 3, 30))
o.append(caption("번호로 꺼내거나 길이를 재려면 먼저 list()로 바꿔요."))
W("t-list", o, "map 결과는 리스트가 아니라서 번호로 꺼내거나 len으로 잴 수 없어요. doubled는 map object예요. 그래서 doubled[0]처럼 번호로 꺼내면 subscriptable이 아니라는 TypeError가 나요. len으로 길이를 재도 map에는 len이 없다는 TypeError가 나요. filter 결과도 똑같아요. 아래처럼 list로 감싸 리스트로 만들어 두면 번호와 len을 쓸 수 있어요. Traceback 위쪽 줄은 빼고 마지막 줄만 옮겼어요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p5", "오류와 함정"))

CFS[0] = 34
o = [sec("t-twice")] + head(EB5, "map 결과는 한 번 꺼내면 비어요", K5)
TT = ["m = map(lambda p: p + 500, [4500, 5000])", "print(list(m))", "print(list(m))"]
T = 196
o += cell({"id": "c-t3", "lines": TT, "n": 4, "out": ["[5000, 5500]", "[]"]}, L, T, FULL, sel="c-t3")
o.append(ring(1, round(ox(L, "[]", 0)) - 4, round(oy(T, 3, 1) - LHf() * 0.42), round(tw("[]")) + 8, round(LHf() * 0.84)))
o.append(tag(ox(L, "[]", 2) + 50, oy(T, 3, 1), "다 꺼낸 뒤라 비었어요", RED, 1, 30))
for i, (lbl, items) in enumerate([("첫 번째 list(m)", ["5000", "5500"]), ("두 번째 list(m)", [])]):
    y = 580 + i * 140
    inner = "".join(chip(v, K3, K3BG, 32) for v in items) if items else chip("[]", RED, "#F8E6E6", 32) + p(f"font-size:28px;font-weight:700;color:{RED};white-space:nowrap", "남은 값이 없어요")
    o.append(f'<div data-build-in="fade order {i + 2}" style="position:absolute;left:{L}px;top:{y}px;width:820px;height:110px;display:flex;flex-direction:row;align-items:center;gap:22px;border-bottom:2px solid {LINE}">'
             + p(f"width:290px;flex:none;font-family:{MONO};font-size:30px;font-weight:700;color:{INK}", e(lbl)) + arrow(50, K3 if items else RED) + inner + '</div>')
CFS[0] = 26
TF = ["m = map(lambda p: p + 500, [4500, 5000])", "ups = list(m)", "print(ups)", "print(ups)"]
o.append(txt(1000, 540, "이렇게 고쳐요", 26, GR, attrs=' data-build-in="fade order 4"'))
o += cell({"id": "c-t3f", "lines": TF, "n": 5, "out": ["[5000, 5500]", "[5000, 5500]"]}, 1000, 584, 824, attrs=' data-build-in="rise order 4"')
o.append(uline(4, 1000, TF[1], 0, 13, ly(584, 1), GR))
o.append(caption("두 번 이상 쓸 결과는 list()로 바꿔 변수에 담아 둬요."))
W("t-twice", o, "map 결과는 한 번 끝까지 꺼내면 비어서, 두 번째부터는 빈 리스트가 나와요. 오류는 안 나서 더 헷갈리는 함정이에요. m에 map을 담고 list(m)을 두 번 찍었어요. 첫 번째는 [5000, 5500]인데 두 번째는 빈 리스트예요. map은 값을 하나씩 꺼내 주는 묶음이라서, 첫 list가 끝까지 꺼내고 나면 남은 값이 없어요. 결과를 두 번 이상 쓸 거라면 오른쪽 아래처럼 list(m)을 한 번만 해서 ups에 담아 두고 ups를 써요. 리스트는 몇 번을 찍어도 그대로예요." + REAL)

CFS[0] = 40
o = [sec("t-paren")] + head(EB5, "넘길 함수에 괄호를 붙이면 바로 실행돼요", K5)
TP = ["def add10(x):", "    return x + 10", "", "print(list(map(add10(), [1, 2, 3])))"]
TPO = "TypeError: add10() missing 1 required positional argument: 'x'"
T = 196
o += cell({"id": "c-t4", "lines": TP, "n": 6, "out": [TPO], "err": True}, L, T, FULL, sel="c-t4")
o.append(pen_box(1, L, TP[3], 15, 22, ly(T, 3)))
o.append(tag(tx(L, TP) + 20, ly(T, 3), "map보다 먼저 x 없이 실행돼요", RED, 1, 30))
o.append(underline(2, round(ox(L, TPO, 19)), round(ox(L, TPO, len(TPO))), round(oy(T, 4, 0) + LHf() * 0.42), RED))
o.append(fix(L, 600, "map(add10(), [1, 2, 3])", "map(add10, [1, 2, 3])", 3, 48))
o.append(caption("함수를 넘길 땐 괄호 없이 이름만 적어요."))
W("t-paren", o, "map에 넘길 함수에 괄호를 붙이면 map이 돌기 전에 그 자리에서 먼저 실행돼요. 습관처럼 add10()이라고 적으면 add10이 x 없이 불려요. x에 넣을 값이 없으니 19에서 본 missing 1 required positional argument 오류가 나요. 함수를 넘길 때는 괄호 없이 이름만 적어요. 괄호는 map이 값을 하나씩 넣으면서 대신 붙여 줘요." + REAL)

CFS[0] = 40
o = [sec("t-return")] + head(EB5, "lambda 안에 return을 쓰면 SyntaxError가 나요", K5)
TRN = ["add10 = lambda x: return x + 10"]
T = 196
o += cell({"id": "c-t5", "lines": TRN, "n": 7, "out": ["SyntaxError: invalid syntax"], "err": True}, L, T, FULL, sel="c-t5")
o.append(pen_box(1, L, TRN[0], 18, 24, ly(T, 0)))
o.append(tag(tx(L, TRN) + 20, ly(T, 0), "콜론 뒤에는 값만 와요", RED, 1, 32))
o.append(fix(L, 520, "lambda x: return x + 10", "lambda x: x + 10", 2, 52))
o.append(caption("lambda는 콜론 뒤에 돌려줄 값 하나만 적어요."))
W("t-return", o, "lambda 안에 return을 적으면 invalid syntax가 나요. lambda는 콜론 뒤에 적은 값을 알아서 돌려주고, 그 자리에는 값만 올 수 있어요. return, if 문, for 문, 변수에 넣는 =는 값이 아니라서 못 넣어요. return을 빼면 돼요. 줄을 나눠야 하는 일은 다음 장처럼 def로 만들어요. SyntaxError 끝에 붙는 파일 이름과 줄 번호는 셀마다 달라서 그 부분은 빼고 옮겼어요." + REAL)

CFS[0] = 30
o = [sec("t-long")] + head(EB5, "lambda가 길어지면 def로 바꿔요", K5)
LL = ['label = lambda p: "비쌈" if p >= 6000 else ("보통" if p >= 4500 else "쌈")', "print(label(6500), label(5000), label(3000))"]
T1 = 236
o.append(txt(L, 196, "lambda 한 줄", 26, GRAY))
o += cell({"id": "c-t6", "lines": LL, "n": 8, "out": ["비쌈 보통 쌈"]}, L, T1, FULL, sel="c-t6")
o.append(line_spot(1, L, T1, 0, 1, L + 105 + tw(LL[0]) + 20))
o.append(spot_off(2))
T2 = 480
LD = ["def label(p):", "    if p >= 6000:", '        return "비쌈"', "    elif p >= 4500:", '        return "보통"', '    return "쌈"', "", "print(label(6500), label(5000), label(3000))"]
o.append(txt(L, T2 - 40, "def로 나눠 쓰기", 26, GR, attrs=' data-build-in="fade order 2"'))
o += cell({"id": "c-t7", "lines": LD, "n": 9, "out": ["비쌈 보통 쌈"]}, L, T2, 1100, attrs=' data-build-in="rise order 2"')
o.append(tag(tx(L, LD[:6]), (ly(T2, 1) + ly(T2, 4)) / 2, "조건이 한 줄에 하나씩", GR, 2, 30))
o.append(tag(ox(L, "비쌈 보통 쌈", 8) + 40, oy(T2, 8, 0), "결과는 같아요", GRAY, 3, 30))
W("t-long", o, "조건이 두 개를 넘으면 lambda 대신 def로 나눠 써요. 한 줄 if else를 괄호로 겹치면 lambda 한 줄에 조건 두 개를 넣을 수 있고 결과도 맞아요. 그런데 어디까지가 어느 조건인지 읽기 어려워요. 아래 def처럼 if와 elif로 나눠 쓰면 19에서 본 모양이라 금방 읽혀요. map에는 map(label, prices)처럼 이름만 넘기면 돼요. lambda는 한 줄로 바로 읽히는 짧은 일에만 써요." + REAL)

# ---------- part 6 ----------
CFS[0] = 32
o = [sec("x-raise")] + head(EB6, "메뉴 가격을 10% 올린 표를 만들어요", K6)
RAISE = ['menu = {"coffee": 4500, "latte": 5000, "cake": 6500}', "print(list(map(lambda m: menu[m] * 11 // 10, menu)))", "", "def line(m):", "    new = menu[m] * 11 // 10", '    return f"{m:<7}{menu[m]:>6,}원 → {new:>6,}원"', "", 'print("\\n".join(map(line, menu)))']
T = 196
o += cell({"id": "c-x1", "lines": RAISE, "n": 1, "out": ["[4950, 5500, 7150]", "coffee  4,500원 →  4,950원", "latte   5,000원 →  5,500원", "cake    6,500원 →  7,150원"]}, L, T, FULL, sel="c-x1")
TX_ = tx(L, RAISE[1:])
o.append(line_spot(1, L, T, 1, 1, TX_ + 300))
o.append(tag(TX_, ly(T, 1), "새 가격만", K6, 1, 28))
o.append(line_spot(2, L, T, 3, 3, TX_ + 420))
o.append(tag(TX_, ly(T, 4), "줄 만들기는 길어서 def", K6, 2, 28))
o.append(line_spot(3, L, T, 7, 1, TX_ + 460))
o.append(tag(TX_, ly(T, 7), "메뉴마다 한 줄, \\n으로 이어 찍기", K6, 3, 28))
o.append(spot_off(4))
o.append(caption("한 줄 계산은 lambda, 줄 만들기처럼 긴 일은 def로 만들어 map에 넘겨요."))
W("x-raise", o, "한 줄 계산은 lambda로, 줄 만들기처럼 긴 일은 def로 만들어 map에 넘겨요. 메뉴 가격을 10% 올려 봐요. 11을 곱하고 10으로 몫 나누기하면 10% 오른 값이 돼요. 먼저 lambda로 새 가격만 리스트로 뽑았어요. 딕셔너리를 넘겨서 m에는 메뉴 이름이 들어가고, 가격은 menu[m]이에요. 원래 가격과 새 가격을 나란히 찍는 줄은 길어서 line이라는 def로 만들었어요. map(line, menu)가 메뉴마다 한 줄씩 만들고, join이 줄바꿈 \\n으로 이어서 한 번에 찍어요. 13의 칸 맞추기와 천 단위 콤마를 그대로 썼어요. 이 파트는 새 커널이라 셀 번호가 [1]부터예요." + REAL, ("p6", "실습"))

CFS[0] = 30
o = [sec("x-soldout")] + head(EB6, "품절이 아니고 5000원 미만인 메뉴를 골라요", K6)
XS = ['menu = {"coffee": 4500, "latte": 5000, "cake": 6500, "tea": 4000}', 'stock = {"coffee": 3, "latte": 0, "cake": 2, "tea": 5}', "print(list(filter(lambda m: stock[m] > 0, menu)))", "print(list(filter(lambda m: stock[m] > 0 and menu[m] < 5000, menu)))"]
T = 196
o += cell({"id": "c-x2", "lines": XS, "n": 2, "out": ["['coffee', 'cake', 'tea']", "['coffee', 'tea']"]}, L, T, FULL, sel="c-x2")
ia = XS[3].index(" and ") + 1
o.append(uline(1, L, XS[3], ia, ia + 3, ly(T, 3), K6))
o.append(tag(tx(L, XS[2:]), ly(T, 3), "17의 and", K6, 1, 28))
o += rows_plain(L, 540, FULL, ["m", "stock[m] > 0", "menu[m] < 5000", "둘 다"], [("coffee", "True", "True", "True"), ("latte", "False", "False", "False"), ("cake", "True", "False", "False"), ("tea", "True", "True", "True")], [300, 420, 440, 300], 2, 70, 30, ids=["xs0", "xs1", "xs2", "xs3"], chips=True)
o.append(spot(3, target="xs2", pad=8, r=12))
o.append(spot_off(4))
o.append(caption("조건이 두 개면 lambda 안에서 and로 이어요."))
W("x-soldout", o, "조건이 두 개면 lambda 안에서 17의 and로 이어요. 메뉴판과 재고 딕셔너리를 같이 써요. 먼저 재고가 남은 메뉴만 골랐어요. latte가 빠졌어요. 다음에는 재고가 있고 5000원 미만인 메뉴를 골라요. 표처럼 두 조건이 모두 True인 coffee와 tea만 남아요. cake는 재고가 있지만 6500원이라 빠져요. 조건이 더 늘어나면 앞에서 본 것처럼 def로 만들어 넘겨요." + REAL)

CFS[0] = 28
o = [sec("x-orders")] + head(EB6, "튜플로 적은 주문 기록을 고르고 꺼내요", K6)
ORD = ['orders = [("kim", "latte", 2), ("lee", "cake", 1), ("park", "coffee", 3), ("kim", "tea", 1)]', "many = list(filter(lambda o: o[2] >= 2, orders))", "print(many)", "print(list(map(lambda o: o[0], many)))", "print(sum(map(lambda o: o[2], orders)))"]
T = 196
o += cell({"id": "c-x3", "lines": ORD, "n": 3, "out": ["[('kim', 'latte', 2), ('park', 'coffee', 3)]", "['kim', 'park']", "7"]}, L, T, FULL, sel="c-x3")
TX_ = tx(L, ORD[1:])
for od, (li, k, lab, col) in enumerate([(1, "o[2]", "2잔 이상 산 주문만 골라요", K4), (3, "o[0]", "고른 주문에서 이름만 꺼내요", K3), (4, "o[2]", "잔 수만 꺼내 sum에 바로 넘겨요", K6)], 1):
    k0 = ORD[li].index(k)
    o.append(uline(od, L, ORD[li], k0, k0 + 4, ly(T, li), col))
    o.append(tag(TX_, ly(T, li), lab, col, od, 28))
# the tuple picture: slots with their numbers
TUP = [('"kim"', "0"), ('"latte"', "1"), ("2", "2")]
o.append(txt(L, 666, "o 칸에 들어오는 튜플 하나", 26, GRAY))
for i, (v, n_) in enumerate(TUP):
    x = L + 420 + i * 300
    o.append(txt(x + 130, 662, n_, 26, K6, mono_=True))
    o.append(vbox(f"tp{i}", x, 710, 280, 110, v, "#C9CED8", "#FFFFFF", fs=36))
o.append(txt(L + 372, 716, "(", 56, GRAY, mono_=True))
o.append(txt(L + 420 + 900 - 4, 716, ")", 56, GRAY, mono_=True))
o.append(box(1, L + 420 + 600 - 8, 702, 296, 126, K4))
o.append(box(2, L + 420 - 8, 702, 296, 126, K3))
o.append(caption("튜플 하나가 lambda의 o 칸에 들어가고, 번호로 칸을 꺼내요.", 900))
W("x-orders", o, "filter와 map에는 튜플 하나씩 들어가고, 번호로 칸을 꺼내요. 13에서 배운 튜플로 주문 기록을 적었어요. 튜플 하나가 이름, 메뉴, 잔 수예요. filter에 넘기면 튜플 하나씩 o 칸에 들어가요. o[2]가 잔 수라서 2잔 이상인 주문만 골랐어요. 그 결과를 map에 넘겨 o[0], 곧 이름만 꺼냈어요. 마지막 줄은 모든 주문의 잔 수를 map으로 꺼내 sum에 바로 넘겼어요. sum은 list로 바꾸지 않아도 값을 하나씩 꺼내 더해요. 모두 7잔이에요." + REAL)

# ---------- wrap up ----------
TRB = [("<map object at 0x...>가 나와요", "map 결과를 그대로 찍었어요", "list(map(...))"),
       ("TypeError: 'map' object is not subscriptable", "map 결과에 번호를 붙였어요", "list()로 바꾸기"),
       ("TypeError: object of type 'map' has no len()", "map 결과에 len을 썼어요", "list()로 바꾸기"),
       ("두 번째 list(m)이 []예요", "map은 한 번 꺼내면 비어요", "리스트로 담아 두기"),
       ("TypeError: add10() missing 1 required ...", "넘길 함수에 괄호를 붙였어요", "map(add10, xs)"),
       ("SyntaxError: invalid syntax", "lambda 안에 return을 적었어요", "lambda x: x + 10"),
       ("lambda가 한눈에 안 읽혀요", "조건이 여러 개예요", "def로 만들어 넘기기")]
o = [sec("trouble")] + head("정리", "막히면 오류의 마지막 줄을 봐요", RED)
o.append(f'<div style="position:absolute;left:{L}px;top:196px;width:{FULL}px;height:50px;display:flex;flex-direction:row;align-items:center;gap:30px;border-bottom:3px solid {INK}">'
         + p("width:50px;flex:none", "") + p(f"width:860px;flex:none;font-size:24px;font-weight:700;color:{GRAY}", "보이는 것") + p(f"width:400px;flex:none;font-size:24px;font-weight:700;color:{GRAY}", "까닭") + p(f"flex:1;font-size:24px;font-weight:700;color:{GRAY}", "고치기") + '</div>')
for i, (q, a_, cmd) in enumerate(TRB, 1):
    y = 246 + (i - 1) * 90
    o.append(f'<div style="position:absolute;left:{L}px;top:{y}px;width:{FULL}px;height:90px;display:flex;flex-direction:row;align-items:center;gap:30px;border-bottom:2px solid {LINE}">'
             + p(f"width:50px;flex:none;font-size:30px;font-weight:900;color:{RED}", str(i))
             + p(f"width:860px;flex:none;{'font-family:' + MONO + ';font-size:26px;' if q.isascii() else 'font-size:28px;'}font-weight:700;color:{INK};white-space:nowrap", e(q))
             + p(f"width:400px;flex:none;font-size:26px;font-weight:500;color:{SUB};white-space:nowrap", e(a_))
             + p(f"flex:1;{'font-family:' + MONO + ';font-size:26px;' if cmd.isascii() else 'font-size:27px;'}font-weight:700;color:{GR};white-space:nowrap", e(cmd)) + '</div>')
o.append(caption("결과가 이상하면 list()로 바꿔 중간 결과를 찍어 봐요."))
W("trouble", o, "이번 챕터에서 막히는 일은 대부분 list()로 바꿔 담으면 풀려요. 1번부터 4번은 map과 filter 결과가 리스트가 아니라서 생겨요. 5번은 함수를 넘길 때 괄호를 붙인 경우예요. 6번과 7번은 lambda에 너무 많은 걸 넣으려다 생겨요. 고르고 바꾸기를 겹쳐 쓸 때는 중간 결과를 list로 찍어 보면 어디서 틀렸는지 보여요.", ("trouble", "정리"))

CH = [("lambda x: x + 10", "이름 없는 한 줄 함수", K2), ("plus = add10", "괄호 없이 함수 담기", K2), ("map(f, xs)", "값마다 f를 써요", K3), ("list(map(...))", "리스트로 모으기", K3),
      ("map(str, xs)", "있는 함수는 이름만", K3), ("filter(f, xs)", "True인 값만 남겨요", K4), ("filter(f, d)", "딕셔너리는 키가 들어가요", K4), ("def label(p):", "길어지면 def로 넘기기", K6)]
o = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>']
for i, (k, d, c) in enumerate(CH):
    x, y = L + (i // 4) * 888, 196 + (i % 4) * 140
    o.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:840px;height:140px;display:flex;flex-direction:row;align-items:center;gap:28px;border-bottom:2px solid {LINE}">'
             + p(f"width:420px;flex:none;font-family:{MONO};font-size:36px;font-weight:700;color:{c};white-space:pre", e(k))
             + p(f"flex:1;font-size:34px;font-weight:700;color:{INK};white-space:nowrap", e(d)) + '</div>')
o.append(p(f"position:absolute;left:{L}px;top:820px;width:{FULL}px;font-size:38px;font-weight:700;color:{INK}", "함수를 넘길 땐 괄호 없이 이름만 적어요."))
o.append(p(f"position:absolute;left:{L}px;top:890px;width:{FULL}px;font-size:32px;font-weight:500;color:{SUB}", "다음 챕터 22에서는 sorted, max, min의 key에 lambda를 넣어 줄 세울 기준을 정해요."))
W("cheatsheet", o, "함수는 값이라서 담고 넘길 수 있고, 넘길 땐 괄호 없이 이름만 적어요. lambda는 이름 없이 값 하나를 돌려주는 짧은 함수예요. map은 값마다 함수를 써서 결과를 모으고, filter는 True를 받은 값만 남겨요. 결과를 리스트로 보려면 list로 감싸요. 22에서는 sorted, max, min에 lambda를 넘겨서 무엇을 기준으로 줄 세울지 정해요.")

finish([("Lightbulb", K1, "왜 필요한가", "되풀이하는 for와 append, map과 filter 그림, 가장 짧은 map", "l-why", "l-min"),
        ("Code", K2, "함수를 값처럼, lambda", "함수 담기와 넘기기, def와 lambda 비교, 바로 넘기기", "v-value", "d-more"),
        ("Settings", K3, "map", "for 네 줄을 한 줄로, 하나씩 넣는 그림, map object, str과 len 넘기기", "m-three", "m-builtin"),
        ("Search", K4, "filter", "골라 담기를 한 줄로, True만 남는 그림, 딕셔너리 키, map과 이어 쓰기", "f-for", "f-chain"),
        ("Warning", K5, "오류와 함정", "번호와 len, 한 번만 꺼내지는 map, 괄호, return, 긴 lambda", "t-list", "t-long"),
        ("Star", K6, "실습", "10% 인상 가격표, 품절 아닌 메뉴, 튜플 주문 기록", "x-raise", "x-orders")],
       "여섯 파트로 나눠서 map과 filter를 3, 4파트에서 집중해서 봐요. 1파트는 for와 append를 되풀이하는 장면과 map, filter 그림이에요. 2파트는 함수를 값처럼 담고 넘기는 법과 lambda예요. 5파트는 자주 나는 오류, 6파트는 카페 실습이에요. 파트마다 새 커널에서 위에서부터 차례로 실행해요.",
       "함수 3 (lambda, map, filter)")
