"""Generates every slide of the AI agent harness extra deck and slides/deck.json.

Story: one small cafe-order project (main.py adds up an order, but a bug keeps only the last price). The same request,
"main.py를 실행하면 합계가 이상해. 고쳐 줘.", goes to Claude Code with nothing around the model, then with tools, then
with a five-line CLAUDE.md, then with the same rules in AGENTS.md only, and a hook stops rm -rf. Part 2 places this in
the trend of AI engineering (prompt, context, loop, graph, harness). Parts 3 to 5 take the harness apart (rules and
context, tools and permissions, checks, skills, subagents). Part 6: pitfalls, this repo's own harness, building one up
for the cafe project, and what survives a move to Codex CLI or Antigravity CLI.
Every transcript comes from tools/demo.sh (real `claude -p` runs, kept in tools/log). Long temp paths are shortened.

Layout rules (Stageshow skill, github.com/benjitaylor/skills, read in full for this deck):
1. one focal object per slide: a transcript, a file, or one diagram; the rest small and quiet (framing.md rule 1)
2. terms are labelled on the line they explain with leader tags, not in extra cards (annotations.md)
3. say it once: notes carry the explanation, the slide keeps one caption at most (craft.md, Say it once)
4. real words only where the story is: the request, the tool call, the result (craft.md, Restraint)
5. what changes moves: a dot travels the loop, the context bar fills and folds into a summary, values fly (motion.md)
6. one number gets to be big (52.8 → 66.5), the rest are lines (craft.md, Restraint)
7. no AI sparkles, no purple glow as "AI" (craft.md, Icons and logos); no invented product logos, names as text
Highlights come from tools/HIGHLIGHT.md, as many kinds as fit. No typing effect.
Usage: python3 tools/gen.py slides
"""

import html, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "tools"))
from highlight import (spot, spot_off, cursor, cursor_off, ring, box, underline, lspot, lspot_off, zoom, zoom_off,
                       shine, shake, pulse, grow, link, keys, SLAM, COUNT, MARK, DELAY, WIPE, STAGGER, MORPH, MORPH_FROM, tok, PATH, DIM)

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
INK, SUB, LINE, CARD = "#1D2330", "#4A5262", "#E1DED6", "#FFFFFF"
BL, GR, OR, PUR, RED, TEAL, GRAY = "#2459C9", "#1F8A4C", "#B26A00", "#5A3BB8", "#A33131", "#0F7C86", "#6A7180"
K1, K1BG = "#1E5FA8", "#E5EEF8"
K2, K2BG = "#A0620A", "#F7EEDD"
K3, K3BG = TEAL, "#E2F2F3"
K4, K4BG = "#A23B72", "#F6E7EF"
K5, K5BG = GR, "#E6F4EC"
K6, K6BG = PUR, "#ECE7F8"
REDBG, GRBG = "#F8E6E6", "#E6F4EC"
DARK = "#1E222A"
W_ = "#E6E9EF"
REAL = " 화면의 대화와 출력은 Claude Code로 실제로 실행한 결과예요. 긴 임시 폴더 경로는 줄였어요."
ASK = "main.py를 실행하면 합계가 이상해. 고쳐 줘."


def fam(s):
    """Mono only for strings without Hangul; Korean in a mono face spreads out."""
    return SANS if any("가" <= ch <= "힣" for ch in s) else MONO


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


def caption(text, top=950, order=None):
    at = f' data-build-in="rise order {order}"' if order else ' data-build-in="rise"'
    return p(f"position:absolute;left:96px;top:{top}px;width:1728px;font-size:34px;font-weight:700;line-height:1.4;color:{INK}", text, ' id="caption"' + at)


def rise(order):
    return f' data-build-in="rise order {order}"'


def fade(order):
    return f' data-build-in="fade order {order}"'


def fly(order, src):
    return f' data-build-in="fly order {order}" data-from="{src}"'


def num(i, color, size=40):
    return p(f"width:{size + 16}px;height:{size + 16}px;flex:none;border-radius:50%;background:{color};color:#FFFFFF;font-size:{size * 0.6:.0f}px;font-weight:900;line-height:{size + 16}px;text-align:center", str(i))


def arrow(w=60, color="#C9CED8", attrs="", style=""):
    return f'<x-shape{attrs} kind="arrow-right" style="width:{w}px;height:30px;flex:none;background:{color};{style}"></x-shape>'


def tag(x, y, text, color, order=None, size=28, lead=True, anim="fade", w=None):
    """A leader label: '← text' centred on y. No box."""
    at = f' data-build-in="{anim} order {order}"' if order else ""
    ws = f"width:{w}px;white-space:normal;" if w else "white-space:nowrap;"
    return p(f"position:absolute;left:{x:.0f}px;top:{y - size * 0.725:.0f}px;{ws}font-size:{size}px;font-weight:700;line-height:1.45;color:{color}", ("← " if lead else "") + e(text), at)


def label(x, y, text, color, size=28, attrs="", mono=False, w=None, align="left", weight=700):
    ws = f"width:{w}px;" if w else ""
    return p(f"position:absolute;left:{x:.0f}px;top:{y:.0f}px;{ws}text-align:{align};font-family:{MONO if mono else SANS};font-size:{size}px;font-weight:{weight};line-height:1.35;color:{color};white-space:nowrap", e(text), attrs)


def term(left, top, w, lines, fs=24, attrs="", tid=None, pad=(26, 34)):
    """A terminal: ('$', cmd) in white after a green $, ('o', text) output in gray, ('r', text) in red, ('g', text) in green."""
    idt = f' id="{tid}"' if tid else ""
    col = {"o": "#A7AEBB", "r": "#FF9C9C", "g": "#8FE3A8", "w": "#F2F4F8"}
    o = [f'<div{idt}{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;background:{DARK};border-radius:18px;padding:{pad[0]}px {pad[1]}px;display:flex;flex-direction:column">']
    for k, t in lines:
        if k == "$":
            o.append(p(f"font-family:{MONO};font-size:{fs}px;line-height:1.55;white-space:pre;color:#F2F4F8;font-weight:700", f'<span style="color:#7EE2A0">$ </span>{e(t)}'))
        else:
            o.append(p(f"font-family:{MONO};font-size:{fs}px;line-height:1.55;white-space:pre;color:{col[k]}", e(t) if t else "&#160;"))
    o.append('</div>')
    return "".join(o)


def tline(top, i, fs=24, pad=26):
    """Centre y of line i in term() drawn at top."""
    return top + pad + fs * 1.55 * (i + 0.5)


def sp(t, c=None, extra=""):
    """A coloured span inside a code line."""
    return f'<span style="color:{c or "inherit"};{extra}">{e(t)}</span>'


def code(left, top, w, lines, fs=28, title=None, tid=None, attrs="", lh=1.5, pad=28, h=None, tcolor=GRAY):
    """A light editor panel. lines: plain strings or already-built html (prefix 'H:'). title: file name on a tab bar."""
    idt = f' id="{tid}"' if tid else ""
    hs = f"height:{h}px;" if h else ""
    o = [f'<div{idt}{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;{hs}background:#FFFFFF;border:2px solid {LINE};border-radius:16px;display:flex;flex-direction:column;overflow:hidden">']
    if title:
        o.append(f'<div style="height:56px;flex:none;background:#F1F0EC;border-bottom:2px solid {LINE};display:flex;flex-direction:row;align-items:center;padding:0 24px">'
                 + p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{tcolor};white-space:pre", e(title)) + '</div>')
    o.append(f'<div style="padding:{pad}px 30px;display:flex;flex-direction:column">')
    for l in lines:
        body = l[2:] if l.startswith("H:") else (e(l) if l else "&#160;")
        o.append(p(f"font-family:{MONO};font-size:{fs}px;line-height:{lh};white-space:pre;color:{INK}", body))
    o.append('</div></div>')
    return "".join(o)


def cly(top, i, fs=28, title=True, pad=28, lh=1.5):
    """Top y of code line i in code() drawn at top."""
    return top + 2 + (58 if title else 0) + pad + i * fs * lh


def cw(s, fs=28):
    """Rendered width of a mono string: Hangul about one em, the rest 0.6 em."""
    return sum(fs * (1.0 if ('가' <= ch <= '힣') else 0.6) for ch in s)


def rule_row(left, top, w, h, cells, widths, attrs="", fs=28, bold=(), colors=None, mono=()):
    """One table row of plain cells over a thin rule."""
    cs = ""
    for k, (c, cw_) in enumerate(zip(cells, widths)):
        col = (colors or {}).get(k, INK)
        fam = MONO if k in mono else SANS
        cs += p(f"width:{cw_}px;flex:none;font-family:{fam};font-size:{fs}px;font-weight:{700 if k in bold else 500};line-height:1.35;color:{col};white-space:pre-wrap", c)
    return f'<div{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;display:flex;flex-direction:row;align-items:center;gap:24px;border-bottom:2px solid {LINE}">{cs}</div>'


def node(x, y, w, h, title, sub, color, bg, attrs="", tid=None, fs=32, sfs=24):
    """A diagram node: a rounded pill with a bold name and a quiet line under it. x, y are its centre."""
    idt = f' id="{tid}"' if tid else ""
    inner = p(f"font-size:{fs}px;font-weight:700;line-height:1.25;color:{color};white-space:nowrap", e(title))
    if sub:
        inner += p(f"font-family:{fam(sub)};font-size:{sfs}px;font-weight:700;line-height:1.3;color:{SUB};white-space:nowrap", e(sub))
    return (f'<div{idt}{attrs} style="position:absolute;left:{x - w / 2:.0f}px;top:{y - h / 2:.0f}px;width:{w}px;height:{h}px;background:{bg};border:3px solid {color};border-radius:22px;'
            f'display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px">{inner}</div>')


def svg(inner, attrs=""):
    return f'<svg{attrs} viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible">{inner}</svg>'


def arrowhead(mid, color):
    return f'<defs><marker id="{mid}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{color}"/></marker></defs>'


def dot(x, y, color, r=14, attrs=""):
    return f'<div{attrs} style="position:absolute;left:{x - r}px;top:{y - r}px;width:{2 * r}px;height:{2 * r}px;border-radius:50%;background:{color};border:4px solid #FFFFFF;box-shadow:0 2px 6px rgba(0,0,0,0.25)"></div>'


def chipline(items, left, top, color, bg, fs=26, gap=14, attrs=""):
    cs = "".join(p(f"font-family:{fam(t)};font-size:{fs}px;font-weight:700;line-height:1.2;color:{color};background:{bg};border-radius:999px;padding:8px 20px;white-space:nowrap", e(t)) for t in items)
    return f'<div{attrs} style="position:absolute;left:{left}px;top:{top}px;display:flex;flex-direction:row;flex-wrap:wrap;gap:{gap}px">{cs}</div>'


def fix(left, top, bad, good, order, size=30, w=1728):
    """The weak line struck through, an arrow, the better line."""
    return (f'<div data-build-in="rise order {order}" style="position:absolute;left:{left}px;top:{top}px;width:{w}px;display:flex;flex-direction:row;align-items:center;gap:22px">'
            + p(f"font-size:{size}px;font-weight:900;color:{RED}", "✕")
            + p(f"font-family:{MONO};font-size:{size}px;font-weight:700;color:{RED};text-decoration:line-through;text-decoration-thickness:3px;white-space:pre", e(bad))
            + arrow(60)
            + p(f"font-size:{size}px;font-weight:900;color:{GR}", "✓")
            + p(f"font-family:{MONO};font-size:{size - 2}px;font-weight:700;color:{INK};background:{GRBG};border:3px solid {GR};border-radius:14px;padding:6px 18px;white-space:pre", e(good)) + '</div>')


EB = ["1 · 왜 필요한가", "2 · AI 엔지니어링의 흐름", "3 · 규칙과 컨텍스트", "4 · 도구와 권한", "5 · 검사, 스킬, 서브에이전트", "6 · 함정과 실제 예"]

# =====================================================================================================
# cover
# =====================================================================================================
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;word-break:keep-all;padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#F2B27A;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 번외</p>',
       f'<h1{SLAM(1)} style="font-size:96px;font-weight:900;line-height:1.1;color:#F6F5F1">AI 에이전트<br>하네스 만들기</h1>',
       '<p style="font-size:40px;line-height:1.4;color:#BFC6D4">Claude Code로 보는<br>규칙, 도구, 권한, 검사</p>']
CX, CY = 1395, 540
cov.append(f'<div id="cov-card" style="position:absolute;left:1000px;top:200px;width:790px;height:680px;background:#FFFFFF;border-radius:28px"></div>')
ring_nodes = [("규칙 파일", -90), ("도구", -30), ("루프", 30), ("권한, 훅", 90), ("검사", 150), ("나눠 맡기기", 210)]
lines_ = ""
import math
for t, a in ring_nodes:
    x, y = CX + 270 * math.cos(math.radians(a)), CY + 230 * math.sin(math.radians(a))
    lines_ += f'<line x1="{CX}" y1="{CY}" x2="{x:.0f}" y2="{y:.0f}" stroke="#D5D9E0" stroke-width="4"/>'
cov.append(svg(lines_))
for i, (t, a) in enumerate(ring_nodes):
    x, y = CX + 270 * math.cos(math.radians(a)), CY + 230 * math.sin(math.radians(a))
    cov.append(node(x, y, 210, 76, t, None, K1 if i < 3 else K4, "#FFFFFF", fs=28))
cov.append(f'<div style="position:absolute;left:{CX - 95}px;top:{CY - 95}px;width:190px;height:190px;border-radius:50%;background:{INK};display:flex;align-items:center;justify-content:center">'
           + p("font-size:40px;font-weight:900;color:#FFFFFF", "모델") + '</div>')
cov.append(shine(2, "cov-card"))
W("cover", cov, "모델 둘레에 붙이는 규칙, 도구, 권한, 검사를 묶어 하네스라고 불러요. 오늘은 Claude Code를 중심으로 하네스를 하나씩 뜯어 보고 직접 쌓아 봐요. 같은 생각이 Codex CLI, Antigravity CLI 같은 다른 에이전트 도구에도 그대로 이어져요. 가운데 모델은 그대로 두고, 둘레를 바꿔서 결과를 바꾸는 이야기예요.", ("intro", "들어가기"))
ORDER.append("toc")

# =====================================================================================================
# part 1
# =====================================================================================================
o = [sec("why")] + head(EB[0], "같은 모델도 도구가 없으면 글만 써요", K1)
o.append(f'<div style="position:absolute;left:96px;top:206px;width:1728px;height:76px;border-radius:16px;background:{K1BG};display:flex;flex-direction:row;align-items:center;gap:20px;padding:0 30px">'
         + p(f"font-size:28px;font-weight:700;color:{K1}", "같은 부탁") + p(f"font-size:32px;font-weight:700;color:{INK}", e(ASK)) + '</div>')
LX, RX, PW = 96, 984, 840
o.append(label(LX, 318, "도구 없이", GRAY, 30))
o.append(label(LX + 170, 322, 'claude -p "..." --tools ""', GRAY, 24, mono=True))
NT = [("w", '<invoke name="Bash">'), ("w", '<parameter name="command">'), ("w", "cd cafe-order && ls -la &&"), ("w", "cat main.py && python3 main.py"), ("w", "</parameter>"), ("w", "</invoke>")]
o.append(term(LX, 376, PW, NT, 26, tid="t-notool"))
o.append(box(1, LX + 18, 376 + 16, PW - 36, 26 * 1.55 * 6 + 20, RED, 5, 12))
o.append(p(f"position:absolute;left:{LX}px;top:{376 + 52 + 26 * 1.55 * 6 + 24:.0f}px;width:{PW}px;font-size:28px;font-weight:700;line-height:1.45;color:{RED}", "실행하고 싶은 명령을 글자로 적고 끝났어요.<br>실제로 돈 명령은 하나도 없어요.", rise(1)))
o.append(label(RX, 318, "도구와 함께", K1, 30, rise(2)))
o.append(label(RX + 210, 322, "Claude Code", GRAY, 24, rise(2), mono=True))
TR = [("Bash", "ls -la && cat *.py", "코드를 읽었어요"), ("Edit", "total = → total +=", "main.py를 고쳤어요"), ("Bash", "python3 main.py", "승인이 없어 못 돌렸어요")]
for i, (tn, ti, tr) in enumerate(TR):
    y = 376 + i * 118
    o.append(f'<div{rise(2)}{DELAY(i * 120)} style="position:absolute;left:{RX}px;top:{y}px;width:{PW}px;height:104px;display:flex;flex-direction:row;align-items:center;gap:22px;border-bottom:2px solid {LINE}">'
             + p(f"width:96px;flex:none;font-family:{MONO};font-size:26px;font-weight:700;color:#FFFFFF;background:{K1};border-radius:10px;text-align:center;padding:6px 0", tn)
             + '<div style="display:flex;flex-direction:column;gap:2px">'
             + p(f"font-family:{MONO};font-size:27px;font-weight:700;color:{INK};white-space:pre", e(ti))
             + p(f"font-size:25px;color:{RED if i == 2 else SUB}", e(tr)) + '</div></div>')
o.append(p(f"position:absolute;left:{RX}px;top:{376 + 3 * 118 + 20}px;width:{PW}px;font-size:28px;font-weight:700;line-height:1.45;color:{K1}", "main.py가 실제로 고쳐졌어요.<br>다만 다시 돌려 확인하지는 못했어요.", rise(3)))
o.append(caption("모델 둘레에 붙인 도구, 규칙, 권한, 검사를 묶어 하네스라고 불러요.", 950, 4))
W("why", o, "모델은 같아도 둘레에 무엇을 붙였는지에 따라 할 수 있는 일이 달라요. 왼쪽은 도구를 모두 뺀 채 같은 부탁을 한 결과예요. 모델은 파일을 읽고 실행하고 싶어서 그 명령을 글자로 적었지만, 손이 없으니 아무것도 실행되지 않았어요. 오른쪽은 Claude Code에 도구를 붙인 상태예요. 코드를 읽고, 한 줄을 고쳤어요. 마지막에 실행해서 확인하려다 승인을 받지 못해 멈췄어요. 이 모자란 부분을 채우는 일이 오늘 배울 하네스 만들기예요. 왼쪽 출력은 한 줄이 길어서 네 줄로 나눠 옮겼어요." + REAL, ("p1", "왜 필요한가"))

# big picture
o = [sec("big")] + head(EB[0], "하네스는 모델을 뺀 나머지 전부예요", K1)
o.append(p(f"position:absolute;left:96px;top:250px;width:560px;font-size:30px;line-height:1.6;color:{SUB}",
           f'<b style="color:{INK}">harness</b>는 말이 수레를 끌 수 있게 몸에 채우는 마구예요.<br><br>모델이 말이라면, 하네스는 힘을 일로 바꿔 주는 장비예요. 어디로 갈지 알려 주고, 손을 쥐여 주고, 위험한 길은 막아요.'))
BX, BY = 1250, 570
BN = [("규칙 파일", "CLAUDE.md", -90, K3, K3BG), ("도구", "Read · Edit · Bash", -30, K4, K4BG), ("권한과 훅", "allow · deny · 훅", 30, K4, K4BG),
      ("검사", "테스트 · 검사 스크립트", 90, K5, K5BG), ("나눠 맡기기", "서브에이전트", 150, K5, K5BG), ("루프", "될 때까지 반복", 210, K2, K2BG)]
ls_ = ""
pts = []
for t, s, a, c, bg in BN:
    x, y = BX + 420 * math.cos(math.radians(a)), BY + 275 * math.sin(math.radians(a))
    pts.append((x, y))
    ls_ += f'<line x1="{BX}" y1="{BY}" x2="{x:.0f}" y2="{y:.0f}" stroke="#C9CED8" stroke-width="5"/>'
o.append(svg(ls_, WIPE(1)))
o.append(f'<div style="position:absolute;left:{BX - 105}px;top:{BY - 105}px;width:210px;height:210px;border-radius:50%;background:{INK};display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px">'
         + p("font-size:42px;font-weight:900;color:#FFFFFF", "모델") + p("font-size:21px;line-height:1.3;color:#BFC6D4;text-align:center;white-space:nowrap", "Claude · GPT<br>Gemini") + '</div>')
for i, ((t, s, a, c, bg), (x, y)) in enumerate(zip(BN, pts)):
    o.append(node(x, y, 330, 112, t, s, c, bg, rise(1) + DELAY(200 + i * 90), fs=32, sfs=23))
o.append(caption("오늘은 바깥 여섯 칸을 하나씩 채워요. 가운데 모델은 그대로예요.", 950, 2))
W("big", o, "하네스는 모델을 뺀 나머지 전부예요. 원래 말에 채우는 마구를 뜻하는 영어 단어예요. 가운데 모델은 Claude든 GPT든 Gemini든 바꿀 수 있어요. 바깥 여섯 칸은 우리가 만들어요. 규칙 파일은 프로젝트의 약속을 알려 주고, 도구는 파일을 읽고 고치고 명령을 실행하게 해 줘요. 권한과 훅은 위험한 일을 막고, 루프는 될 때까지 반복하게 해요. 검사는 결과가 맞는지 확인하고, 서브에이전트는 큰일을 나눠 맡아요. 오늘 덱은 이 여섯 칸을 차례로 채워요.")

# agent loop
o = [sec("loop")] + head(EB[0], "에이전트는 끝날 때까지 같은 고리를 돌아요", K1)
LCX, LCY, LR = 560, 580, 250
LN = [("생각하기", "다음에 할 일 고르기", -90, K2, K2BG), ("도구 부르기", "Read · Edit · Bash", 30, K4, K4BG), ("결과 보기", "출력, 오류, 파일 내용", 150, K3, K3BG)]
lp = []
for t, s, a, c, bg in LN:
    lp.append((LCX + LR * math.cos(math.radians(a)), LCY + LR * math.sin(math.radians(a))))
arc = ""
for i in range(3):
    a0, a1 = LN[i][2] + 26, LN[(i + 1) % 3][2] - 26
    x0, y0 = LCX + LR * math.cos(math.radians(a0)), LCY + LR * math.sin(math.radians(a0))
    x1, y1 = LCX + LR * math.cos(math.radians(a1)), LCY + LR * math.sin(math.radians(a1))
    arc += f'<path d="M{x0:.0f},{y0:.0f} A{LR},{LR} 0 0 1 {x1:.0f},{y1:.0f}" fill="none" stroke="#C9CED8" stroke-width="6" marker-end="url(#ah-loop)"/>'
o.append(svg(arrowhead("ah-loop", "#C9CED8") + arc))
# the travelling dot: a full lap that ends back at "생각하기"
sx, sy = lp[0]
ex, ey = LCX + LR * math.cos(math.radians(-142)), LCY + LR * math.sin(math.radians(-142))
o.append(svg(f'<path id="lap" d="M{ex:.1f},{ey:.1f} A{LR},{LR} 0 1 1 {ex - 0.4:.1f},{ey + 0.4:.1f}" fill="none" stroke="none"/>'))
for (t, s, a, c, bg), (x, y) in zip(LN, lp):
    o.append(node(x, y, 300, 110, t, s, c, bg, fs=32, sfs=22))
o.append(dot(sx, sy - 70, OR, 14, PATH(1, "lap")) if False else "")
o.append(f'<div{PATH(1, "lap")} style="position:absolute;left:{ex - 16:.0f}px;top:{ey - 16:.0f}px;width:32px;height:32px;border-radius:50%;background:{OR};border:4px solid #FFFFFF;box-shadow:0 2px 6px rgba(0,0,0,0.3)"></div>')
o.append(f'<svg viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none">{arrowhead("ah-exit", GR)}<path{WIPE(2)} d="M{sx + 150:.0f},{sy:.0f} L{1000},{sy:.0f}" fill="none" stroke="{GR}" stroke-width="6" marker-end="url(#ah-exit)"/></svg>')
o.append(node(1130, sy, 230, 90, "끝: 답하기", None, GR, GRBG, rise(2), fs=30))
RT = [("1", "생각하기", "부탁과 지금까지의 결과를 보고 다음 할 일을 골라요.", K2),
      ("2", "도구 부르기", "파일 읽기, 고치기, 명령 실행 가운데 하나를 불러요.", K4),
      ("3", "결과 보기", "출력이나 오류가 다시 모델에게 들어가요.", K3)]
for i, (n_, h_, d_, c) in enumerate(RT):
    o.append(f'<div{rise(3)}{DELAY(i * 120)} style="position:absolute;left:1000px;top:{440 + i * 130}px;width:824px;height:116px;display:flex;flex-direction:row;align-items:center;gap:22px;border-bottom:2px solid {LINE}">'
             + num(n_, c, 34) + '<div style="display:flex;flex-direction:column;gap:2px">' + p(f"font-size:28px;font-weight:700;color:{c}", e(h_)) + p(f"font-size:25px;color:{INK}", e(d_)) + '</div></div>')
o.append(caption("모델이 더 할 일이 없다고 판단하면 고리를 빠져나와 답해요.", 950, 4))
W("loop", o, "에이전트는 생각하고, 도구를 부르고, 결과를 보는 고리를 끝날 때까지 돌아요. 주황 점이 한 바퀴 도는 것이 한 번의 반복이에요. 결과는 다시 모델에게 들어가서 다음 생각의 재료가 돼요. 오류가 나면 그 오류를 보고 다른 방법을 골라요. 더 할 일이 없다고 판단하면 고리를 빠져나와 사람에게 답해요. 언제 멈출지를 모델이 정한다는 점이 뒤에 나올 함정과 이어져요.")

# min: the real loop
o = [sec("min")] + head(EB[0], "실제로 돈 고리: 도구를 네 번 불렀어요", K1)
o.append(term(96, 200, 1728, [("$", f'claude -p "{ASK}" --permission-mode acceptEdits --allowedTools "Bash(uv run *)"')], 24, tid="t-min"))
MR = [("1", "Bash", "ls -la && cat *.py && python3 main.py", "승인이 필요해요: python3 main.py", RED),
      ("2", "Bash", "ls -la && cat *.py", "main.py 코드 8줄", INK),
      ("3", "Edit", "-  total = prices[item]\n+  total += prices[item]", "파일을 고쳤어요", GR),
      ("4", "Bash", "python3 main.py", "승인이 필요해요", RED)]
MW = [60, 110, 820, 600]
o.append(rule_row(96, 300, 1728, 54, ["", "도구", "넣은 값", "돌아온 결과"], MW, fs=24, colors={1: GRAY, 2: GRAY, 3: GRAY}, bold=(1, 2, 3)))
yy = 354
MRH = [100, 100, 128, 100]
for i, (n_, tn, ti, tr, c) in enumerate(MR):
    o.append(rule_row(96, yy, 1728, MRH[i], [n_, tn, e(ti), e(tr)], MW, fs=27, bold=(0, 1), mono=(1, 2), colors={0: K1, 1: K1, 3: c}, attrs=f' id="mr{i}"'))
    o.append(spot(i + 1, 96, yy, 1728, MRH[i], pad=6, dim=0.5))
    yy += MRH[i]
o.append(spot_off(5))
o.append(p(f"position:absolute;left:96px;top:{yy + 30}px;width:1728px;font-size:30px;line-height:1.5;color:{INK}",
           '<span style="font-weight:700;color:' + K1 + '">마지막 답</span>  버그를 고쳤어요. 다만 <span id="min-no">python3 main.py 실행은 승인되지 않아서 직접 돌려 보지는 못했어요.</span>', rise(5)))
o.append(underline(6, 96 + 346, 96 + 1250, yy + 30 + 44, RED))
o.append(caption("고치긴 했지만 확인은 못 했어요. 무엇이 모자랐는지 3, 4파트에서 채워요.", 950, 6))
W("min", o, "고리를 실제로 돌려 보니 도구를 네 번 불렀어요. 이번 실행에는 uv run으로 시작하는 명령만 허락해 두었어요. 첫 번째에 모델은 파이썬을 python3 main.py로 실행하려다 승인이 필요하다는 답을 받았어요. 두 번째는 실행을 빼고 코드만 읽었어요. 세 번째에 덮어쓰던 줄을 더하는 줄로 고쳤어요. 네 번째에 다시 python3로 확인하려다 또 막혔어요. 이 프로젝트가 uv run을 쓴다는 것을 모델이 몰랐던 거예요. 규칙 파일이 있으면 이 문제가 풀려요. 3파트에서 같은 부탁을 다시 해 봐요." + REAL)

# =====================================================================================================
# part 2: trend
# =====================================================================================================
o = [sec("trend")] + head(EB[1], "AI 엔지니어링은 다듬는 범위가 넓어져 왔어요", K2)
TC = [("프롬프트", "2022~", "질문 한 문장", "모델이 모르는 것은 아무리 잘 물어도 못 답해요"),
      ("컨텍스트", "2025~", "모델에게 보여 줄 자료", "한 번 답하면 끝이라 실행해서 확인을 못 해요"),
      ("루프", "", "도구를 쓰며 반복하기", "길어지면 길을 잃고 매번 가는 길이 달라요"),
      ("그래프", "", "단계, 갈림길, 나눠 맡기기", "")]
for i, (n_, yr, wh, wall) in enumerate(TC):
    x = 96 + i * 444
    at = rise(i + 1)
    body = (p(f"font-size:26px;font-weight:700;color:{GRAY}", "다듬는 것") + p(f"font-size:34px;font-weight:700;line-height:1.35;color:{INK}", e(wh)))
    if wall:
        body += (p(f"margin-top:40px;font-size:26px;font-weight:700;color:{RED}", "부딪힌 벽") + p(f"font-size:31px;line-height:1.45;color:{INK}", e(wall)))
    else:
        body += (p(f"margin-top:40px;font-size:26px;font-weight:700;color:{K2}", "더 나아간 점") + p(f"font-size:31px;line-height:1.45;color:{INK}", "여러 고리를 지도처럼 이어서 큰 흐름은 사람이 정해요"))
    o.append(f'<div{at} style="position:absolute;left:{x}px;top:236px;width:400px;height:540px;display:flex;flex-direction:column;gap:6px;border-top:6px solid {K2};padding-top:28px">'
             + f'<div style="display:flex;flex-direction:row;align-items:baseline;gap:14px">' + p(f"font-size:30px;font-weight:900;color:{K2}", str(i + 1)) + p(f"font-size:50px;font-weight:900;color:{INK}", e(n_))
             + (p(f"font-family:{MONO};font-size:24px;color:{GRAY}", yr) if yr else "") + '</div>'
             + f'<div style="margin-top:20px;display:flex;flex-direction:column;gap:6px">{body}</div></div>')
    if i < 3:
        o.append(arrow(34, "#C9CED8", rise(i + 2), f"position:absolute;left:{x + 404}px;top:300px"))
o.append(f'<div{rise(5)} style="position:absolute;left:96px;top:700px;width:1728px;height:120px;border-radius:18px;background:{INK};display:flex;flex-direction:row;align-items:center;gap:24px;padding:0 36px">'
         + p("font-size:30px;font-weight:700;color:#F2B27A;white-space:nowrap", "하네스 (2026~)") + p("font-size:30px;font-weight:700;color:#FFFFFF", "넷을 묶어서 모델이 일하는 환경 전체를 설계해요") + '</div>')
W("trend", o, "AI를 잘 쓰는 방법은 다듬는 범위가 점점 넓어지는 쪽으로 바뀌어 왔어요. 처음에는 질문 한 문장을 다듬었어요. 그런데 모델이 모르는 정보는 아무리 잘 물어도 답할 수 없었어요. 그래서 모델에게 보여 줄 자료를 고르는 컨텍스트로 넘어갔어요. 자료를 잘 줘도 한 번 답하면 끝이라, 모델이 도구를 쓰며 스스로 반복하는 루프가 나왔어요. 루프가 길어지자 길을 잃는 일이 생겨서, 단계와 갈림길을 미리 그려 두는 그래프가 쓰여요. 이 순서는 연도보다 다듬는 범위가 넓어진 순서예요. 그래프 도구인 LangGraph는 2024년부터 있었어요. 2026년에는 이 넷을 묶어 하네스 엔지니어링이라고 불러요.", ("p2", "AI 엔지니어링의 흐름"))

# prompt
o = [sec("prompt")] + head(EB[1], "프롬프트 엔지니어링: 질문 한 문장을 다듬어요", K2)
PF = f"font-family:{SANS};font-size:42px;font-weight:700;line-height:1.55;color:{INK}"
before = (f'<div id="pm-a"{MORPH_FROM()} style="position:absolute;left:96px;top:230px;width:1150px;display:flex;flex-direction:column;gap:6px">'
          + p(PF, tok("s", "main.py를 실행하면&#160;") + tok("h", "합계가 이상해.&#160;") + tok("f", "고쳐 줘.")) + '</div>')
after = (f'<div{MORPH(1, "pm-a")} style="position:absolute;left:96px;top:230px;width:1150px;display:flex;flex-direction:column;gap:6px">'
         + p(PF, tok("r", "너는 파이썬 강사야.", f"color:{K2}"))
         + p(PF, tok("s", "아래 코드에서&#160;") + tok("h", "합계가 틀린 줄을 찾아"))
         + p(PF, tok("f", "고친 줄만 보여 줘.", f"color:{TEAL}"))
         + p(f"font-family:{MONO};font-size:32px;font-weight:700;line-height:1.5;color:{SUB};white-space:pre;margin-top:12px;padding:16px 26px;background:#FFFFFF;border:2px solid {LINE};border-radius:14px",
             tok("c", e("for item in order:\n    total = prices[item]\nprint(\"합계:\", total)"), f"color:{BL}")) + '</div>')
o.append(before)
o.append(after)
PT = [(237, "역할 주기", K2), (302, "할 일 좁히기", INK), (367, "답 모양 정하기", TEAL), (515, "자료 붙여 넣기", BL)]
for y, t, c in PT:
    o.append(tag(1300, y + 25, t, c, 2, 32))
o.append(f'<div{rise(3)} style="position:absolute;left:96px;top:690px;width:1728px;display:flex;flex-direction:row;align-items:center;gap:20px;padding:28px 30px;background:{REDBG};border-radius:16px">'
         + p(f"font-size:28px;font-weight:700;color:{RED};white-space:nowrap", "부딪힌 벽") + p(f"font-size:30px;line-height:1.45;color:{INK}", "코드를 직접 붙여 넣지 않으면 모델은 main.py를 볼 수 없어요. 다른 파일, 실행 결과, 팀의 규칙도 몰라요.") + '</div>')
o.append(caption("잘 묻는 기술은 지금도 쓸모 있어요. 다만 그것만으로는 모자라요.", 950, 4))
W("prompt", o, "프롬프트 엔지니어링은 질문 한 문장을 다듬는 일이에요. 짧은 부탁을 역할, 할 일, 답 모양이 분명한 부탁으로 바꾸면 답이 좋아져요. 코드를 붙여 넣으면 더 좋아져요. 그런데 붙여 넣은 것 말고는 모델이 아무것도 몰라요. 프로젝트의 다른 파일도, 실행 결과도, 팀이 정한 규칙도 모르죠. 앞에서 도구 없이 부탁했을 때 명령을 글로만 적고 끝난 것도 같은 벽이에요. 이 벽 때문에 무엇을 보여 줄지를 다듬는 쪽으로 관심이 옮겨 갔어요.")

# context
o = [sec("context")] + head(EB[1], "컨텍스트 엔지니어링: 모델 책상에 올릴 자료를 골라요", K2)
o.append(label(96, 220, "컨텍스트 창 (모델이 한 번에 보는 글 전체)", GRAY, 26))
SEG = [("시스템 안내", 210, "#D9DEE8", INK), ("규칙 파일", 230, K3BG, K3), ("도구 설명", 230, K4BG, K4), ("읽은 파일", 330, K1BG, K1), ("대화와 실행 결과", 420, K2BG, K2)]
x0 = 96
for i, (t, w, bg, c) in enumerate(SEG):
    o.append(f'<div{rise(1)}{DELAY(i * 110)} style="position:absolute;left:{x0}px;top:270px;width:{w - 8}px;height:150px;background:{bg};border-top:6px solid {c};border-radius:10px;display:flex;align-items:center;justify-content:center">'
             + p(f"font-size:28px;font-weight:700;color:{c};white-space:nowrap", e(t)) + '</div>')
    x0 += w
o.append(f'<div style="position:absolute;left:{x0}px;top:270px;width:{1824 - x0}px;height:150px;border:3px dashed #C9CED8;border-radius:10px;display:flex;align-items:center;justify-content:center">' + p(f"font-size:26px;color:{GRAY}", "빈자리") + '</div>')
o.append(label(96, 470, "창 밖에 있는 것은 모델이 몰라요", GRAY, 26, rise(2)))
OUTS = ["다른 폴더의 파일", "어제 나눈 대화", "팀이 정한 실행 명령", "회사 위키"]
o.append(chipline(OUTS, 96, 520, GRAY, "#ECEBE6", 28, 16, rise(2)))
o.append(p(f"position:absolute;left:96px;top:640px;width:1728px;font-size:31px;line-height:1.55;color:{INK}",
           '2025년 6월 Shopify CEO 토비 뤼트케가 "컨텍스트 엔지니어링"이라는 말을 쓰고 안드레이 카파시가 퍼뜨렸어요.<br>질문보다 <b>무엇을 창에 넣을지</b>가 결과를 더 크게 바꾼다는 뜻이에요.', rise(3)))
o.append(f'<div{rise(4)} style="position:absolute;left:96px;top:800px;width:1728px;display:flex;flex-direction:row;align-items:center;gap:20px;padding:28px 30px;background:{REDBG};border-radius:16px">'
         + p(f"font-size:28px;font-weight:700;color:{RED};white-space:nowrap", "부딪힌 벽") + p(f"font-size:30px;line-height:1.45;color:{INK}", "자료를 잘 줘도 한 번 답하면 끝이에요. 고친 코드가 도는지는 여전히 사람이 돌려 봐야 해요.") + '</div>')
o.append(caption("3파트에서 볼 CLAUDE.md가 바로 이 창에 늘 들어가는 규칙 파일이에요.", 950, 5))
W("context", o, "컨텍스트 엔지니어링은 모델 책상에 올릴 자료를 고르는 일이에요. 모델은 컨텍스트 창 안의 글만 봐요. 시스템 안내, 규칙 파일, 도구 설명, 읽은 파일, 지금까지의 대화가 모두 이 창에 들어가요. 창 밖의 파일이나 어제 대화는 모델이 몰라요. 2025년 6월에 Shopify CEO 토비 뤼트케가 이 말을 쓰고 안드레이 카파시가 퍼뜨리면서 널리 쓰였어요. 그래도 한 번 답하면 끝이라는 벽은 남았어요. 실행해서 확인하는 일은 사람 몫이었죠.")

# loop stage
o = [sec("loop2")] + head(EB[1], "루프: 모델이 직접 해 보고 다시 고쳐요", K2)
o.append(p(f"position:absolute;left:96px;top:236px;width:840px;font-size:30px;font-weight:700;color:{GR}", "좋아진 것", rise(1)))
GOOD = [("실행 결과를 도구가 바로 가져와요", "사람이 복사해서 붙여 주지 않아도 돼요"), ("오류를 보면 다른 방법을 골라요", "6쪽 실행에서 막힌 명령을 빼고 다시 했어요"), ("파일 여러 개를 다루는 긴 일도 해요", "읽고, 고치고, 다시 실행하기를 이어서")]
for i, (t, d) in enumerate(GOOD):
    o.append(f'<div{rise(1)}{DELAY(i * 100)} style="position:absolute;left:96px;top:{300 + i * 140}px;width:820px;height:128px;display:flex;flex-direction:row;align-items:center;gap:20px;border-bottom:2px solid {LINE}">'
             + p(f"font-size:34px;font-weight:900;color:{GR}", "✓") + '<div style="display:flex;flex-direction:column;gap:4px">' + p(f"font-size:31px;font-weight:700;color:{INK}", e(t)) + p(f"font-size:25px;color:{SUB}", e(d)) + '</div></div>')
o.append(p(f"position:absolute;left:1000px;top:236px;width:824px;font-size:30px;font-weight:700;color:{RED}", "새로 생긴 벽", rise(2)))
BAD = [("같은 일을 되풀이해요", "6쪽 실행에서 코드를 두 번 읽었어요"), ("프로젝트 방식을 몰라요", "uv run 대신 python3로 돌리다 막혔어요"), ("언제 멈출지 모델이 정해요", "확인을 못 했는데도 끝냈어요")]
for i, (t, d) in enumerate(BAD):
    o.append(f'<div{rise(2)}{DELAY(i * 100)} style="position:absolute;left:1000px;top:{300 + i * 140}px;width:824px;height:128px;display:flex;flex-direction:row;align-items:center;gap:20px;border-bottom:2px solid {LINE}">'
             + p(f"font-size:34px;font-weight:900;color:{RED}", "!") + '<div style="display:flex;flex-direction:column;gap:4px">' + p(f"font-size:31px;font-weight:700;color:{INK}", e(t)) + p(f"font-size:25px;color:{SUB}", e(d)) + '</div></div>')
o.append(p(f"position:absolute;left:96px;top:760px;width:1728px;font-size:31px;line-height:1.55;color:{INK}",
           "Claude Code, Codex CLI, Antigravity CLI가 모두 이 루프 위에서 돌아요.", rise(3)))
o.append(caption("루프를 어디로, 얼마나 돌릴지 정하는 장치가 필요해졌어요.", 950, 4))
W("loop2", o, "루프 단계에서는 모델이 직접 해 보고, 결과를 보고, 다시 고쳐요. 사람이 실행 결과를 복사해서 붙여 주던 일을 도구가 대신해요. 오류가 나면 모델이 스스로 다른 방법을 골라요. 대신 새 벽이 생겼어요. 앞에서 본 실행처럼 같은 파일을 두 번 읽기도 하고, 프로젝트가 uv run을 쓴다는 것을 몰라 막히기도 해요. 확인을 못 했는데도 모델이 끝났다고 판단하면 거기서 멈춰요. 그래서 루프를 어디로, 얼마나 돌릴지 정하는 장치가 필요해졌어요.")

# graph
o = [sec("graph")] + head(EB[1], "그래프: 단계와 갈림길을 미리 그려 둬요", K2)
GN = {"plan": (300, 520, "계획", "할 일 나누기", K2, K2BG), "a": (720, 400, "구현 A", "서브에이전트", K4, K4BG), "b": (720, 640, "구현 B", "서브에이전트", K4, K4BG),
      "chk": (1140, 520, "검사", "테스트, 검사 스크립트", K5, K5BG), "end": (1600, 520, "끝", "사람에게 보고", GR, GRBG)}
ed = (f'<path d="M450,500 L560,420" /><path d="M450,540 L560,620" /><path d="M880,420 L990,500" /><path d="M880,620 L990,540" /><path d="M1290,520 L1460,520" />')
o.append(svg(arrowhead("ah-g", "#9AA1AE") + f'<g{WIPE(1)} fill="none" stroke="#9AA1AE" stroke-width="5" marker-end="url(#ah-g)">{ed}</g>'))
o.append(svg(arrowhead("ah-r", RED) + f'<path{WIPE(2)} d="M1140,600 C1140,820 720,820 720,725" fill="none" stroke="{RED}" stroke-width="5" stroke-dasharray="14 10" marker-end="url(#ah-r)"/>'))
o.append(label(870, 800, "통과 못 하면 다시", RED, 28, rise(2)))
o.append(label(1305, 470, "통과", GR, 28, rise(1)))
for k, (x, y, t, s, c, bg) in GN.items():
    o.append(node(x, y, 300, 120, t, s, c, bg, rise(1) if k != "plan" else "", fs=34, sfs=22))
o.append(p(f"position:absolute;left:96px;top:250px;width:1728px;font-size:28px;line-height:1.5;color:{SUB}", "칸(노드)은 할 일, 화살표(엣지)는 다음 순서예요. 고리 하나가 아니라 고리 여러 개를 이은 지도예요."))
o.append(chipline(["LangGraph", "OpenAI Agents SDK", "Claude Code 서브에이전트"], 96, 880, K2, K2BG, 26, 16, rise(3)))
o.append(label(96, 836, "이렇게 쓰는 도구들", GRAY, 24, rise(3)))
W("graph", o, "그래프는 단계와 갈림길을 미리 그려 두는 방식이에요. 칸은 할 일이고 화살표는 다음 순서예요. 계획 칸이 일을 나누면 구현 칸 두 개가 동시에 일하고, 검사 칸이 결과를 확인해요. 통과하지 못하면 빨간 화살표를 따라 구현으로 돌아가요. 루프 하나에 모든 걸 맡기면 매번 가는 길이 달랐는데, 그래프는 큰 흐름을 사람이 정하고 칸 안에서만 모델이 자유롭게 움직여요. LangGraph나 OpenAI Agents SDK가 이런 구조를 코드로 만들고, Claude Code에서는 서브에이전트로 일을 나눠 맡겨요. 이 수업 자료도 챕터마다 작업을 나눠 동시에 만들고, 검사를 통과해야 미리보기로 넘어가요.")

# harness
o = [sec("harness")] + head(EB[1], "하네스 엔지니어링: 모델은 두고 환경을 바꿔요", K2)
NEST = [("하네스", 760, 600, INK), ("그래프", 640, 500, K2), ("루프", 520, 400, K2), ("컨텍스트", 400, 300, K2), ("프롬프트", 280, 200, K2)]
NX, NY = 96 + 380, 300 + 300
for i, (t, w, h, c) in enumerate(NEST):
    at = rise(1) + DELAY((4 - i) * 140)
    o.append(f'<div{at} style="position:absolute;left:{NX - w / 2:.0f}px;top:{NY - h / 2:.0f}px;width:{w}px;height:{h}px;border:4px solid {c};border-radius:{28 - i * 3}px;background:{"#FFFFFF" if i == 0 else "transparent"}"></div>')
    o.append(label(NX - w / 2 + 22, NY - h / 2 + 12, t, c, 26, at))
o.append(f'<div style="position:absolute;left:{NX - 70}px;top:{NY - 40}px;width:140px;height:80px;border-radius:40px;background:{INK};display:flex;align-items:center;justify-content:center">' + p("font-size:30px;font-weight:900;color:#FFFFFF", "모델") + '</div>')
o.append(p(f"position:absolute;left:1000px;top:250px;width:824px;font-size:28px;font-weight:700;color:{GRAY}", "같은 모델, 하네스만 바꿨을 때", rise(2)))
o.append(p(f"position:absolute;left:1000px;top:300px;width:824px;font-size:48px;font-weight:700;color:{GRAY};font-variant-numeric:tabular-nums", "52.8% <span style=\"font-size:32px\">에서</span>", rise(2)))
o.append(p(f"position:absolute;left:1000px;top:360px;width:824px;font-size:150px;font-weight:900;line-height:1.1;color:{INK};font-variant-numeric:tabular-nums", "66.5%", COUNT(2) + rise(2)))
o.append(p(f"position:absolute;left:1000px;top:540px;width:824px;font-size:27px;line-height:1.5;color:{SUB}", "LangChain이 코딩 에이전트 시험(Terminal Bench 2.0)에서<br>모델은 그대로 두고 하네스만 고쳐 얻은 점수예요.", rise(2)))
o.append(p(f"position:absolute;left:1000px;top:700px;width:824px;font-size:30px;line-height:1.55;color:{INK}", "그래서 2026년에는 규칙, 도구, 권한, 검사를 묶어 설계하는 일을 <b>하네스 엔지니어링</b>이라고 불러요.", rise(3)))
o.append(caption("다음 파트부터 Claude Code의 하네스를 한 칸씩 뜯어 봐요.", 950, 4))
W("harness", o, "하네스 엔지니어링은 모델을 그대로 두고 모델이 일하는 환경을 바꾸는 일이에요. 왼쪽 그림처럼 프롬프트, 컨텍스트, 루프, 그래프가 차례로 바깥을 감싸고, 맨 바깥이 하네스예요. 2026년 LangChain은 코딩 에이전트 시험인 Terminal Bench 2.0에서 모델은 바꾸지 않고 하네스만 고쳐서 52.8%를 66.5%로 올렸다고 발표했어요. 이 말은 2026년 초 미첼 하시모토, OpenAI 같은 곳에서 쓰기 시작해 널리 퍼졌어요. 다음 파트부터 Claude Code의 하네스를 한 칸씩 뜯어 봐요. 숫자는 LangChain 블로그 글 Improving Deep Agents with harness engineering에서 옮겼어요.")

# =====================================================================================================
# part 3: rules and context
# =====================================================================================================
o = [sec("claude-md")] + head(EB[2], "CLAUDE.md는 프로젝트에 두는 안내문이에요", K3)
CM = ["# 카페 주문 프로젝트", "", "- 실행은 `uv run main.py`로 해요.", "- 돈은 천 단위 콤마와 \"원\"을 붙여 출력해요.", '  예: `print(f"합계: {total:,}원")`', "- 고친 뒤에는 꼭 다시 실행해서", "  결과를 확인해요."]
o.append(code(96, 220, 880, CM, 32, "cafe-order/CLAUDE.md", tid="cm-file", pad=34))
o.append(box(1, 96 + 30 - 8, cly(220, 2, 32, pad=34) - 4, cw("- 실행은 `uv run main.py`로 해요.", 32) + 16, 48 + 8, K3, 4, 10))
o.append(label(1040, 230, "어디에 두면 언제 읽나요", GRAY, 26))
WH = [("~/.claude/CLAUDE.md", "내 컴퓨터의 모든 프로젝트"), ("./CLAUDE.md", "이 프로젝트 (git에 올려 팀이 같이 써요)"), ("폴더/CLAUDE.md", "그 폴더 파일을 다룰 때")]
for i, (f, d) in enumerate(WH):
    o.append(f'<div{rise(2)}{DELAY(i * 110)} style="position:absolute;left:1040px;top:{290 + i * 120}px;width:784px;height:108px;display:flex;flex-direction:column;justify-content:center;gap:4px;border-bottom:2px solid {LINE}">'
             + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{K3}", e(f)) + p(f"font-size:26px;color:{INK}", e(d)) + '</div>')
o.append(p(f"position:absolute;left:1040px;top:680px;width:784px;font-size:27px;line-height:1.5;color:{SUB}", f'처음엔 Claude Code에서 <span style="font-family:{MONO};font-weight:700;color:{INK}">/init</span>을 치면 프로젝트를 읽고 초안을 만들어 줘요.', rise(3)))
o.append(caption("대화를 시작할 때마다 자동으로 컨텍스트 창에 들어가요.", 950, 4))
W("claude-md", o, "CLAUDE.md는 프로젝트 폴더에 두는 안내문이에요. Claude Code는 대화를 시작할 때마다 이 파일을 읽어서 컨텍스트 창에 넣어요. 그래서 매번 설명하지 않아도 실행 명령이나 팀의 약속을 알아요. 집 폴더의 .claude 안에 두면 내 컴퓨터의 모든 프로젝트에, 프로젝트 맨 위에 두면 그 프로젝트에 적용돼요. 프로젝트 파일은 git에 올려서 팀이 같이 써요. 하위 폴더에 두면 그 폴더의 파일을 다룰 때 읽어요. 처음 만들 때는 /init을 치면 Claude Code가 프로젝트를 훑어보고 초안을 써 줘요. 왼쪽은 이번 실습에 쓴 다섯 줄짜리 파일이에요.")

# effect
o = [sec("effect")] + head(EB[2], "규칙 몇 줄로 결과가 달라졌어요", K3)
o.append(label(96 + 380, 220, "규칙 없이", GRAY, 30))
o.append(label(96 + 1100, 220, "CLAUDE.md를 두고", K3, 30))
EF = [("확인 명령", "python3 main.py", "uv run main.py"), ("출력 모양", 'print("합계:", total)', 'print(f"합계: {total:,}원")'), ("확인한 결과", "승인이 없어 못 돌렸어요", "합계: 14,500원")]
for i, (k, a, b) in enumerate(EF):
    y = 290 + i * 200
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:180px;border-bottom:2px solid {LINE}"></div>')
    o.append(label(96, y + 66, k, GRAY, 30))
    o.append(p(f"position:absolute;left:476px;top:{y + 62}px;width:640px;font-family:{MONO if i < 2 else SANS};font-size:32px;font-weight:700;color:{RED if i == 2 else INK};white-space:pre", e(a)))
    o.append(p(f"position:absolute;left:1196px;top:{y + 52}px;font-family:{MONO};font-size:34px;font-weight:700;color:{INK};background:{K3BG};border-radius:12px;padding:6px 18px;white-space:pre", e(b), rise(i + 1) + f' id="ef{i}"'))
o.append(caption("두 번 모두 같은 모델, 같은 부탁이에요. 달라진 건 폴더에 둔 파일 하나예요.", 950, 4))
W("effect", o, "규칙 몇 줄로 결과가 달라졌어요. 왼쪽은 1파트에서 본 규칙 없는 실행이고, 오른쪽은 앞 장의 CLAUDE.md를 둔 뒤 같은 부탁을 한 실행이에요. CLAUDE.md에 실행 명령을 적어 두니 모델이 uv run main.py로 확인했어요. 허락해 둔 명령이라 막히지 않았죠. 출력도 규칙대로 천 단위 콤마와 원을 붙였어요. 마지막에 다시 실행해서 합계 14,500원을 직접 확인한 뒤 답했어요. 모델도 부탁도 같고, 달라진 건 폴더에 둔 파일 하나예요." + REAL)

# good rules
o = [sec("rule-good")] + head(EB[2], "규칙은 맞았는지 확인할 수 있게 써요", K3)
RF = f"font-family:{MONO};font-size:34px;font-weight:700;line-height:1.8;color:{INK};white-space:pre"
o.append(f'<div id="rg-a"{MORPH_FROM()} style="position:absolute;left:96px;top:230px;width:1100px;padding:30px 36px;background:#FFFFFF;border:2px solid {LINE};border-radius:16px">'
         + p(RF, tok("1", "- 코드를 깔끔하게 써 줘")) + p(RF, tok("2", "- 테스트를 잘 해 줘")) + p(RF, tok("3", "- 위험한 건 하지 마")) + '</div>')
o.append(f'<div{MORPH(1, "rg-a")} style="position:absolute;left:96px;top:230px;width:1100px;padding:30px 36px;background:#FFFFFF;border:2px solid {LINE};border-radius:16px">'
         + p(RF, tok("1", "- 실행은 uv run main.py")) + p(RF, tok("2", "- 고친 뒤 uv run main.py로 다시 확인")) + p(RF, tok("3", "- 지울 땐 rm -rf 말고 파일을 하나씩")) + '</div>')
CKS = [("확인할 수 있어요", "명령, 파일 이름, 예시처럼 맞았는지 볼 수 있게"), ("자주 틀리는 것만", "모델이 이미 잘하는 건 적지 않아요"), ("짧게", "길어지면 중요한 줄이 묻혀요. 긴 절차는 스킬로")]
for i, (h_, d_) in enumerate(CKS):
    o.append(f'<div{rise(2)}{DELAY(i * 110)} style="position:absolute;left:1260px;top:{236 + i * 140}px;width:564px;height:126px;display:flex;flex-direction:column;justify-content:center;gap:4px;border-bottom:2px solid {LINE}">'
             + p(f"font-size:30px;font-weight:700;color:{K3}", e(h_)) + p(f"font-size:24px;line-height:1.4;color:{SUB}", e(d_)) + '</div>')
o.append(p(f"position:absolute;left:96px;top:740px;width:1728px;font-size:30px;line-height:1.55;color:{INK}",
           "이 수업 자료 레포의 CLAUDE.md에는 수업 규칙이 모여 있어요. 덱 디자인 절차처럼 긴 내용은 <span style=\"font-family:" + MONO + ";font-weight:700\">tools/DESIGN.md</span>로 떼어 두고, 덱을 만들 때만 읽게 했어요.", rise(3)))
o.append(caption("세 번째 줄 같은 금지는 규칙만으로는 약해요. 4파트의 훅으로 막아요.", 950, 4))
W("rule-good", o, "규칙은 맞았는지 확인할 수 있게 써요. 깔끔하게, 잘, 위험한 것 같은 말은 사람마다 뜻이 달라서 모델도 제멋대로 읽어요. 명령, 파일 이름, 예시를 적으면 지켰는지 바로 보여요. 모델이 이미 잘하는 것은 적지 않고, 자주 틀리는 것만 적어요. 파일이 길어지면 중요한 줄이 묻히니, 가끔 쓰는 긴 절차는 5파트의 스킬로 떼어 내요. 이 레포도 덱 디자인 절차를 tools/DESIGN.md로 떼어 두었어요. 지우지 말라는 규칙은 모델이 잊을 수도 있어서, 꼭 막아야 하는 일은 훅으로 막아요.")

# context window
o = [sec("window")] + head(EB[2], "컨텍스트 창이 차면 앞부분을 요약해요", K3)
o.append(label(96, 214, "대화가 길어질수록 창이 차요", GRAY, 26))
BW = 1728
o.append(f'<div style="position:absolute;left:96px;top:262px;width:{BW}px;height:110px;border:3px solid #C9CED8;border-radius:14px"></div>')
FILL = [("규칙", 180, K3BG, K3), ("읽은 파일", 360, K1BG, K1), ("실행 결과", 420, K2BG, K2), ("대화", 480, "#E7E5DE", SUB)]
x0 = 102
for i, (t, w, bg, c) in enumerate(FILL):
    o.append(f'<div id="wf{i}"{rise(i + 1) if i else ""} style="position:absolute;left:{x0}px;top:268px;width:{w - 6}px;height:98px;background:{bg};border-radius:10px;display:flex;align-items:center;justify-content:center">' + p(f"font-size:27px;font-weight:700;color:{c}", e(t)) + '</div>')
    x0 += w
o.append(label(102 + 1440 + 20, 296, "거의 참", RED, 28, rise(3)))
o.append(f'<div style="position:absolute;left:96px;top:430px;width:{BW}px;height:110px;border:3px solid #C9CED8;border-radius:14px"></div>')
o.append(f'<div{fly(4, "wf0")} style="position:absolute;left:102px;top:436px;width:174px;height:98px;background:{K3BG};border-radius:10px;display:flex;align-items:center;justify-content:center">' + p(f"font-size:27px;font-weight:700;color:{K3}", "규칙") + '</div>')
o.append(f'<div{rise(4)} style="position:absolute;left:282px;top:436px;width:300px;height:98px;background:#ECEBE6;border:3px dashed #9AA1AE;border-radius:10px;display:flex;align-items:center;justify-content:center">' + p(f"font-size:27px;font-weight:700;color:{SUB}", "앞부분 요약") + '</div>')
o.append(label(600, 466, "요약한 뒤 규칙 파일은 다시 읽어 넣어요", K3, 28, rise(4)))
CMDS = [("/context", "창에 무엇이 얼마나 찼는지 봐요"), ("/compact", "지금까지를 요약하고 비워요"), ("/clear", "새 대화로 처음부터 시작해요")]
for i, (c, d) in enumerate(CMDS):
    o.append(f'<div{rise(5)}{DELAY(i * 100)} style="position:absolute;left:96px;top:{610 + i * 96}px;width:1728px;height:86px;display:flex;flex-direction:row;align-items:center;gap:30px;border-bottom:2px solid {LINE}">'
             + p(f"width:240px;flex:none;font-family:{MONO};font-size:32px;font-weight:700;color:{K3}", e(c)) + p(f"font-size:30px;color:{INK}", e(d)) + '</div>')
o.append(caption("오래 지켜야 할 약속은 대화가 아니라 CLAUDE.md에 적어요.", 950, 6))
W("window", o, "컨텍스트 창은 크지만 끝이 있어요. 파일을 읽고 명령을 돌릴수록 창이 차요. 거의 차면 Claude Code가 앞부분을 요약해서 자리를 만들어요. 이때 대화 중에 말로 한 약속은 요약되면서 흐려질 수 있어요. CLAUDE.md는 요약한 뒤에도 파일에서 다시 읽어 넣으니 오래 지켜야 할 약속은 파일에 적어요. /context로 창이 얼마나 찼는지 보고, /compact로 직접 요약하고, 다른 일로 넘어갈 때는 /clear로 새로 시작해요.")

# other tools
o = [sec("agents-table")] + head(EB[2], "다른 에이전트 도구도 같은 부품을 써요", K3)
AW = [300, 470, 440, 440]
o.append(rule_row(96, 220, 1728, 70, ["", "Claude Code", "Codex CLI (OpenAI)", "Antigravity CLI (Google)"], AW, fs=28, bold=(1, 2, 3), colors={1: K3, 2: INK, 3: INK}))
AR = [("실행 명령", "claude", "codex", "agy"), ("규칙 파일", "CLAUDE.md\n(없으면 AGENTS.md)", "AGENTS.md", "GEMINI.md, AGENTS.md"),
      ("스킬 폴더", ".claude/skills", ".agents/skills", ".agents/skills"), ("외부 도구 연결", "MCP", "MCP", "MCP")]
AH = [100, 140, 100, 100]
yy = 290
for i, r in enumerate(AR):
    o.append(rule_row(96, yy, 1728, AH[i], [e(c) for c in r], AW, fs=28, bold=(0,), mono=(1, 2, 3), colors={0: GRAY}, attrs=f' id="at{i}"'))
    yy += AH[i]
o.append(spot(1, 96, 290 + 100, 1728, 140, pad=6, dim=0.45))
o.append(spot(2, 96, 290 + 240, 1728, 100, pad=6, dim=0.45))
o.append(spot_off(3))
o.append(p(f"position:absolute;left:96px;top:{yy + 40}px;width:1728px;font-size:27px;line-height:1.6;color:{SUB}",
           "AGENTS.md는 Linux Foundation 산하 Agentic AI Foundation이 관리하는 공개 형식이에요.<br>Antigravity CLI는 2026년에 Gemini CLI 자리를 이어받은 도구예요.", rise(3)))
o.append(caption("이름만 다르고 규칙 파일, 스킬, MCP라는 뼈대는 같아요.", 950, 4))
W("agents-table", o, "다른 에이전트 도구도 같은 부품을 써요. OpenAI의 Codex CLI는 AGENTS.md를 읽고, Google의 Antigravity CLI는 GEMINI.md와 AGENTS.md를 읽어요. Claude Code는 CLAUDE.md를 읽고, CLAUDE.md가 없으면 AGENTS.md를 읽어요. 스킬도 같은 SKILL.md 형식이라 폴더만 달라요. 외부 서비스는 셋 다 MCP로 붙여요. AGENTS.md는 OpenAI가 내놓은 형식인데, 지금은 Linux Foundation 산하 Agentic AI Foundation이 관리해요. Gemini CLI는 2026년부터 Antigravity CLI로 옮겨 가는 중이에요. 도구 이름과 폴더는 자주 바뀌니 쓰기 전에 각 도구의 문서를 한 번 확인해요. 표의 내용은 2026년 11월 기준이에요.")

# AGENTS.md real
o = [sec("agents-real")] + head(EB[2], "AGENTS.md 하나를 여러 도구가 같이 읽어요", K3)
o.append(label(96, 220, "CLAUDE.md를 지우고 같은 규칙을 AGENTS.md에만 두면", GRAY, 26))
o.append(term(96, 270, 820, [("o", "cafe-order/"), ("o", "├─ AGENTS.md    규칙 다섯 줄"), ("o", "└─ main.py"), ("o", ""), ("$", "uv run main.py"), ("g", "합계: 14,500원")], 32, tid="t-ag"))
o.append(box(1, 96 + 34 - 10, tline(270, 5, 32) - 30, cw("합계: 14,500원", 32) + 20, 60, GR, 4, 10))
o.append(p(f"position:absolute;left:96px;top:660px;width:820px;font-size:28px;line-height:1.5;color:{INK}", "Claude Code가 AGENTS.md를 읽고 규칙대로 고쳤어요.", rise(1)))
o.append(label(1000, 220, "둘 다 있으면 CLAUDE.md만 읽어요", K3, 28, rise(2)))
o.append(code(1000, 270, 824, ["@AGENTS.md", "", "## Claude Code에서만", "- 훅은 .claude/settings.json에 있어요."], 28, "CLAUDE.md", tid="ag-cm", attrs=rise(2)))
o.append(underline(3, 1000 + 30, 1000 + 30 + cw("@AGENTS.md"), cly(270, 0) + 44, K3))
o.append(tag(1000 + 30 + cw("@AGENTS.md") + 30, cly(270, 0) + 21, "AGENTS.md 내용을 그대로 불러와요", K3, 3, 26))
o.append(p(f"position:absolute;left:1000px;top:600px;width:824px;font-size:27px;line-height:1.55;color:{SUB}", f'읽는 방식은 <span style="font-family:{MONO};font-weight:700;color:{INK}">/config</span>의 Project instructions에서 바꿀 수 있어요. 기본값은 CLAUDE.md가 없을 때만 AGENTS.md를 읽어요.', rise(3)))
o.append(caption("공통 규칙은 AGENTS.md에, Claude Code만의 설정은 CLAUDE.md에 둬요.", 950, 4))
W("agents-real", o, "AGENTS.md 하나를 여러 도구가 같이 읽을 수 있어요. CLAUDE.md를 지우고 같은 다섯 줄을 AGENTS.md에만 둔 뒤 같은 부탁을 했더니, Claude Code가 AGENTS.md를 읽고 규칙대로 고쳐서 14,500원을 확인했어요. 주의할 점이 있어요. 두 파일이 모두 있으면 기본값에서는 CLAUDE.md만 읽고 AGENTS.md는 건너뛰어요. 그래서 CLAUDE.md 첫 줄에 @AGENTS.md를 적어 AGENTS.md 내용을 불러오고, 그 아래에 Claude Code만의 내용을 적어요. 읽는 방식은 /config의 Project instructions에서 바꿀 수 있어요. AGENTS.md를 읽는 기능은 2026년 9월에 들어왔어요." + REAL)

# =====================================================================================================
# part 4: tools and permissions
# =====================================================================================================
o = [sec("tools")] + head(EB[3], "도구는 이름, 설명, 입력 칸으로 생겼어요", K4)
o.append(label(96, 214, "모델이 보는 도구 설명", GRAY, 26))
TDF = 30
TD = ["H:" + sp("이름 ", GRAY) + "  " + sp("Bash", K4, "font-weight:700"),
      "H:" + sp("설명 ", GRAY) + "  명령을 실행하고 출력을 돌려줘요",
      "H:" + sp("입력 ", GRAY) + "  " + sp("command", BL, "font-weight:700") + "      실행할 명령",
      "H:" + sp("입력 ", "transparent") + "  " + sp("description", TEAL, "font-weight:700") + "  무엇을 하는지 한 줄"]
o.append(code(96, 260, 860, TD, TDF, None, tid="td", pad=30))
o.append(label(1020, 214, "실제 호출 (3파트 실행)", GRAY, 26, rise(1)))
TC_ = ["H:{", "H:  " + sp('"name"', GRAY) + ': ' + sp('"Bash"', K4) + ',', "H:  " + sp('"input"', GRAY) + ": {",
       "H:    " + sp('"command"', BL) + ": " + sp('"uv run main.py"', BL, "font-weight:700") + ",", "H:    " + sp('"description"', TEAL) + ":", "H:      " + sp('"Run main.py to verify the total"', TEAL), "H:  }", "H:}"]
o.append(code(1020, 260, 804, TC_, 26, None, tid="tc", attrs=rise(1), pad=24))
o.append(p(f"position:absolute;left:1020px;top:650px;width:804px;font-size:28px;color:{SUB}", '돌아온 결과  <span style="font-family:' + MONO + ';font-weight:700;color:' + GR + '">합계: 14,500원</span>', rise(2)))
o.append(label(96, 540, "Claude Code의 기본 도구", GRAY, 26, rise(3)))
o.append(chipline(["Read", "Edit", "Write", "Bash", "Grep", "Glob", "WebSearch", "Task (서브에이전트)"], 96, 586, K4, K4BG, 26, 14, rise(3)).replace("display:flex;flex-direction:row;flex-wrap:wrap", "width:860px;display:flex;flex-direction:row;flex-wrap:wrap"))
o.append(label(96, 790, "도구를 직접 만들 땐 설명을 구체적으로", GRAY, 26, rise(4)))
o.append(fix(96, 840, "run: 실행해요", "uv_run: 프로젝트 가상환경으로 파이썬 파일을 실행해요", 4, 28))
W("tools", o, "도구는 이름, 설명, 입력 칸으로 생겼어요. 모델은 도구를 직접 만지지 않고, 도구 설명을 읽은 뒤 어떤 도구를 어떤 값으로 부를지 글로 적어요. 그러면 하네스가 그 도구를 대신 실행하고 결과를 돌려줘요. 오른쪽은 3파트 실행에서 모델이 실제로 적은 호출이에요. command 칸에 uv run main.py를 넣었고, 결과로 합계 14,500원이 돌아왔어요. Claude Code에는 파일 읽기, 고치기, 명령 실행 같은 기본 도구가 있어요. MCP로 도구를 직접 붙일 때는 설명을 구체적으로 써야 모델이 제때 골라요." + REAL)

# MCP
o = [sec("mcp")] + head(EB[3], "MCP는 에이전트와 서비스를 잇는 공통 규격이에요", K4)
AG = ["Claude Code", "Codex CLI", "Antigravity CLI"]
SV = ["GitHub", "PostgreSQL", "Slack", "브라우저"]
MY = 500
for i, t in enumerate(AG):
    o.append(node(330, MY - 170 + i * 170, 380, 110, t, None, INK, "#FFFFFF", fs=34))
for i, t in enumerate(SV):
    o.append(node(1590, MY - 225 + i * 150, 360, 104, t, None, K4, K4BG, rise(1) + DELAY(i * 90), fs=34))
o.append(f'<div style="position:absolute;left:880px;top:{MY - 230}px;width:160px;height:460px;border-radius:24px;background:{K4};display:flex;align-items:center;justify-content:center">' + p("font-size:48px;font-weight:900;color:#FFFFFF;writing-mode:vertical-rl;letter-spacing:6px", "MCP") + '</div>')
ml = "".join(f'<path d="M520,{MY - 170 + i * 170} L880,{MY}" />' for i in range(3))
mr = "".join(f'<path id="mcp{i}" d="M1040,{MY} L1410,{MY - 225 + i * 150}" />' for i in range(4))
o.append(svg(f'<g fill="none" stroke="#C9CED8" stroke-width="5">{ml}</g>'))
o.append(svg(f'<g{WIPE(1)} fill="none" stroke="#C9CED8" stroke-width="5">{mr}</g>'))
o.append(f'<div{PATH(2, "mcp1")} style="position:absolute;left:{1410 - 14}px;top:{MY - 75 - 14}px;width:28px;height:28px;border-radius:50%;background:{OR};border:4px solid #FFFFFF"></div>')
o.append(label(96, 780, "서버 하나를 붙이는 명령", GRAY, 24, rise(3)))
o.append(term(96, 826, 1728, [("$", "claude mcp add --transport http github https://api.githubcopilot.com/mcp/")], 28, tid="t-mcp", attrs=rise(3)))
W("mcp", o, "MCP는 에이전트와 외부 서비스를 잇는 공통 규격이에요. 노트북의 USB-C 포트처럼, 서비스가 MCP 서버를 하나 만들어 두면 어떤 에이전트든 같은 방식으로 꽂아 써요. GitHub 서버를 붙이면 이슈와 PR을 읽고 쓰는 도구가 생기고, PostgreSQL 서버를 붙이면 44에서 파이썬으로 하던 조회를 에이전트가 해요. Anthropic이 2024년 11월에 공개했고, 지금은 AGENTS.md와 같은 Agentic AI Foundation이 관리해요. 아래 명령은 Claude Code에 GitHub의 공식 MCP 서버를 붙이는 예예요. 실제로 붙이려면 GitHub 로그인이 더 필요해요.")

# permissions
o = [sec("perm")] + head(EB[3], "권한: 무엇을 묻고 무엇을 바로 할지 정해요", K4)
PM = [("manual", "도구를 쓸 때마다 물어요"), ("acceptEdits", "파일 고치기는 바로, 명령은 물어요"), ("plan", "읽기만 하고 계획을 세워 보여 줘요"), ("auto", "안전해 보이는 일은 바로, 위험하면 멈춰요"), ("bypassPermissions", "묻지 않아요. 격리된 곳에서만 써요")]
for i, (m, d) in enumerate(PM):
    o.append(f'<div id="pm{i}"{rise(1)}{DELAY(i * 90)} style="position:absolute;left:96px;top:{224 + i * 104}px;width:860px;height:94px;display:flex;flex-direction:row;align-items:center;gap:24px;border-bottom:2px solid {LINE}">'
             + p(f"width:330px;flex:none;font-family:{MONO};font-size:29px;font-weight:700;color:{RED if i == 4 else K4}", e(m)) + p(f"font-size:26px;color:{INK}", e(d)) + '</div>')
o.append(keys(2, 96, 770, "Shift+Tab"))
o.append(label(400, 780, "으로 대화 중에 모드를 바꿔요", INK, 28, rise(2)))
PJ = ["{", '  "permissions": {', '    "allow": ["Bash(uv run *)"],', '    "deny":  ["Read(./.env)", "Bash(rm -rf *)"]', "  }", "}"]
o.append(code(1010, 224, 814, PJ, 25, ".claude/settings.json", tid="pj", attrs=rise(3)))
o.append(box(4, 1010 + 30 - 8, cly(224, 2, 25, pad=28) - 4, cw('    "allow": ["Bash(uv run *)"],', 25) + 16, 25 * 1.5 + 8, GR, 4, 8))
o.append(tag(1010 + 30 + cw('    "allow": ["Bash(uv run *)"],', 25) + 24, cly(224, 2, 25) + 19, "묻지 않고 실행", GR, 4, 24))
o.append(box(5, 1010 + 30 - 8, cly(224, 3, 25, pad=28) - 4, cw('    "deny":  ["Read(./.env)", "Bash(rm -rf *)"]', 25) + 16, 25 * 1.5 + 8, RED, 4, 8))
o.append(p(f"position:absolute;left:1010px;top:620px;width:814px;font-size:26px;line-height:1.5;color:{SUB}", "deny에 적은 일은 모드와 상관없이 막혀요. 1파트에서 본 \"승인이 필요해요\"는 allow에 없던 python3 main.py가 걸린 거예요.", rise(5)))
W("perm", o, "권한은 무엇을 묻고 무엇을 바로 할지 정하는 장치예요. 처음엔 도구를 쓸 때마다 물어요. 파일 고치기를 믿을 만하면 acceptEdits로, 먼저 계획만 보고 싶으면 plan으로 바꿔요. auto는 안전해 보이는 일은 바로 하고 위험해 보이면 멈춰요. bypassPermissions는 아무것도 묻지 않아서 컨테이너처럼 격리된 곳에서만 써요. 대화 중에는 Shift+Tab으로 모드를 바꿔요. 자주 쓰는 명령은 settings.json의 allow에, 절대 안 될 일은 deny에 적어요. 1파트 실행이 막힌 것도 allow에 uv run만 있어서였어요.")

# hooks
o = [sec("hooks")] + head(EB[3], "훅은 도구가 돌기 전에 끼어드는 검문소예요", K4)
o.append(node(240, 260, 240, 84, "모델", "Bash 부르기", INK, "#FFFFFF", fs=30, sfs=22))
o.append(node(690, 260, 380, 84, "PreToolUse 훅", "block_rm.py", K4, K4BG, rise(1), fs=30, sfs=22))
o.append(node(1140, 260, 240, 84, "Bash", "실제 실행", GR, GRBG, fs=30, sfs=22))
o.append(arrow(80, "#C9CED8", "", "position:absolute;left:370px;top:245px"))
o.append(arrow(80, "#C9CED8", "", "position:absolute;left:890px;top:245px"))
o.append(p(f"position:absolute;left:1300px;top:232px;width:524px;font-size:26px;line-height:1.45;color:{RED}", "종료 코드 2면 여기서 멈추고<br>이유가 모델에게 전달돼요", rise(1)))
HP = ["import json", "import sys", "", "data = json.load(sys.stdin)", 'command = data["tool_input"].get("command", "")', "", 'if "rm -rf" in command:', '    print("rm -rf는 막아 두었어요. ...", file=sys.stderr)', "    sys.exit(2)"]
HT = 360
o.append(code(96, HT, 1000, HP, 25, ".claude/hooks/block_rm.py", tid="hp", pad=22))
HJ = ['"hooks": {', '  "PreToolUse": [{', '    "matcher": "Bash",', '    "hooks": [{', '      "type": "command",', '      "command":', '        "python3 .claude/hooks/block_rm.py"', "    }]", "  }]", "}"]
o.append(code(1140, HT, 684, HJ, 23, ".claude/settings.json", tid="hj", pad=22, attrs=rise(4)))
HB = 1000
for k, (i, t) in enumerate([(3, "도구 이름과 입력이 JSON으로 들어와요"), (6, "명령에 rm -rf가 있으면"), (8, "2로 끝내서 막아요")]):
    y = cly(HT, i, 25, pad=22)
    o.append(lspot(k + 1, 96 + 2, HT + 2, 996, 58 + 22 * 2 + 9 * 37.5, y, 37.5, bg="#FFFFFF", bar=K4))
o.append(lspot_off(4))
o.append(caption("훅은 모델이 잊어도 코드로 늘 돌아요. 규칙 파일과 다른 점이에요.", 950, 5))
W("hooks", o, "훅은 도구가 돌기 직전이나 직후에 끼어드는 검문소예요. PreToolUse 훅은 모델이 도구를 부른 뒤, 실제로 실행되기 전에 돌아요. 훅에는 도구 이름과 입력이 JSON으로 들어와요. 이 파이썬 파일은 명령에 rm -rf가 있으면 이유를 적고 종료 코드 2로 끝내요. 종료 코드 2를 받으면 Claude Code는 도구를 실행하지 않고, 그 이유를 모델에게 전해요. 연결은 settings.json의 hooks에 적어요. matcher가 Bash라서 Bash를 부를 때만 이 훅이 돌아요. 규칙 파일은 모델이 잊을 수 있지만 훅은 코드라서 매번 돌아요. 파일을 고친 뒤 검사를 돌리는 PostToolUse 훅도 같은 방식이에요.")

# hook run
o = [sec("hook-run")] + head(EB[3], "rm -rf를 시키자 훅이 막고, 모델은 다른 길을 찾았어요", K4)
o.append(term(96, 200, 1728, [("$", """echo '{"tool_name": "Bash", "tool_input": {"command": "rm -rf build"}}' | python3 .claude/hooks/block_rm.py"""),
                              ("r", "rm -rf는 막아 두었어요. 지울 파일을 하나씩 적어 주세요."), ("$", "echo $?"), ("o", "2")], 24, tid="t-hr"))
o.append(label(96, 430, '부탁: "rm -rf build 명령으로 build 폴더를 지워 줘."', K4, 28))
HR = [("1", "ls -la build && rm -rf build && ls", "PreToolUse:Bash hook error: rm -rf는 막아 두었어요.", RED),
      ("2", "find build", "build, build/old.txt", INK),
      ("3", "rm build/old.txt && rmdir build && ls", "main.py", GR)]
for i, (n_, c, r, col) in enumerate(HR):
    y = 492 + i * 108
    o.append(f'<div id="hr{i}"{rise(i + 1)} style="position:absolute;left:96px;top:{y}px;width:1728px;height:100px;display:flex;flex-direction:row;align-items:center;gap:24px;border-bottom:2px solid {LINE}">'
             + p(f"width:40px;flex:none;font-size:30px;font-weight:900;color:{K4}", n_)
             + p(f"width:760px;flex:none;font-family:{MONO};font-size:27px;font-weight:700;color:{INK};white-space:pre", e(c))
             + p(f"font-family:{MONO};font-size:25px;font-weight:700;color:{col};white-space:pre", e(r)) + '</div>')
o.append(shake(1, "hr0"))
o.append(p(f"position:absolute;left:96px;top:{492 + 3 * 108 + 26}px;width:1728px;font-size:29px;line-height:1.5;color:{INK}",
           f'<span style="font-weight:700;color:{K4}">마지막 답</span>  build 폴더를 지웠어요. 다만 rm -rf로 지우지는 않았어요.', rise(4)))
o.append(caption("막힌 이유가 모델에게 전달돼서, 모델이 허락된 방법으로 다시 했어요.", 950, 5))
W("hook-run", o, "rm -rf를 시키자 훅이 막고, 모델은 다른 길을 찾았어요. 맨 위는 훅 파일만 따로 돌려 본 결과예요. JSON을 넣어 주면 이유를 출력하고 종료 코드 2로 끝나요. 아래는 Claude Code에 같은 부탁을 한 실제 기록이에요. 첫 명령에 rm -rf가 들어 있어서 훅이 막았어요. 모델은 막힌 이유를 읽고 폴더 안을 먼저 확인했어요. 그다음 파일 하나를 rm으로 지우고 빈 폴더를 rmdir로 지웠어요. 훅이 알려 준 대로 파일을 하나씩 지운 거예요. 훅 메시지는 일부만 옮겼어요." + REAL)

# =====================================================================================================
# part 5: checks, skills, subagents
# =====================================================================================================
o = [sec("verify")] + head(EB[4], "검사는 사람 대신 스크립트가 돌려요", K5)
VC = [("만들기", 260, K1, K1BG), ("검사", 480, K5, K5BG), ("고치기", 700, K4, K4BG)]
for t, y, c, bg in VC:
    o.append(node(300, y, 300, 110, t, None, c, bg, f' id="vc-{t}"', fs=34))
o.append(svg(arrowhead("ah-v", "#C9CED8") + '<g fill="none" stroke="#C9CED8" stroke-width="5" marker-end="url(#ah-v)"><path d="M300,320 L300,415"/><path d="M300,540 L300,635"/><path d="M150,700 C40,700 40,480 140,480"/></g>'))
o.append(pulse(1, "vc-검사"))
o.append(label(620, 214, "이 덱을 만들며 실제로 돌린 검사", GRAY, 26))
VT = [("$", "node ../../tools/boxcheck.js slides"), ("g", BOXCHECK if (BOXCHECK := open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "log", "boxcheck.txt")).read().strip() if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "log", "boxcheck.txt")) else "no text leaves its box") else ""),
      ("o", ""), ("$", "python3 tools/build_readme.py --check"), ("o", "(아무것도 안 나오면 통과)")]
o.append(term(620, 262, 1204, VT, 30, tid="t-v"))
o.append(p(f"position:absolute;left:620px;top:640px;width:1204px;font-size:30px;line-height:1.55;color:{INK}",
           "글자가 상자 밖으로 나가면 boxcheck가 장 이름을 찍어요. 에이전트는 그 출력을 보고 고친 뒤 다시 돌려요. 통과할 때까지가 한 번의 일이에요.", rise(2)))
o.append(caption("\"다 했어요\"를 믿지 말고, 기계가 확인할 수 있는 검사를 만들어 둬요.", 950, 3))
W("verify", o, "검사는 사람 대신 스크립트가 돌려요. 에이전트는 다 했다고 말하지만, 1파트처럼 확인을 못 하고 끝낼 때도 있어요. 그래서 맞았는지 기계가 판단할 수 있는 검사를 만들어 두고, 통과할 때까지 고치게 해요. 이 덱도 그렇게 만들었어요. boxcheck는 글자가 상자 밖으로 나간 장을 찾고, build_readme.py --check는 README 표가 curriculum.json과 어긋나면 알려 줘요. 테스트, 린트, 스크린샷 비교도 같은 역할이에요. CLAUDE.md에 검사 명령을 적어 두거나 PostToolUse 훅으로 자동으로 돌리게 해요. 위 출력은 이 덱을 만들며 실제로 돌린 결과예요.")

# skills
o = [sec("skills")] + head(EB[4], "스킬은 필요할 때 펴 보는 레시피 카드예요", K5)
SK = ["---", "name: menu-update", "description: 메뉴나 가격을 바꿀 때 써요.", "  prices와 README 가격표를 같이 고쳐요.", "---", "", "1. main.py의 prices 딕셔너리를 고쳐요.", "2. README.md 가격표도 같은 값으로 고쳐요.", "3. uv run main.py로 합계를 확인해요."]
o.append(code(96, 220, 1000, SK, 28, ".claude/skills/menu-update/SKILL.md", tid="sk", pad=26))
o.append(box(1, 96 + 30 - 8, cly(220, 1, 28, pad=26) - 4, cw("  prices와 README 가격표를 같이 고쳐요.", 28) + 16, 28 * 1.5 * 3 + 8, K5, 4, 8))
o.append(label(1160, 220, "처음엔 이 두 줄만 창에 들어가요", K5, 28, rise(1)))
SL = [("menu-update", "메뉴나 가격을 바꿀 때 써요."), ("release-note", "학생 공지를 쓸 때 써요."), ("deck-check", "덱 검수할 때 써요.")]
for i, (n_, d) in enumerate(SL):
    o.append(f'<div{rise(1)}{DELAY(i * 100)} style="position:absolute;left:1160px;top:{280 + i * 92}px;width:664px;height:84px;display:flex;flex-direction:column;justify-content:center;border-bottom:2px solid {LINE}">'
             + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{K5 if i == 0 else GRAY}", e(n_)) + p(f"font-size:24px;color:{INK if i == 0 else GRAY}", e(d)) + '</div>')
o.append(p(f"position:absolute;left:1160px;top:590px;width:664px;font-size:27px;line-height:1.5;color:{INK}", '"라떼를 5500원으로 바꿔 줘" 같은 부탁이 오면 그때 본문을 읽어요. 직접 <span style="font-family:' + MONO + ';font-weight:700">/menu-update</span>로 불러도 돼요.', rise(2)))
o.append(p(f"position:absolute;left:96px;top:780px;width:1728px;font-size:28px;line-height:1.55;color:{SUB}", "같은 SKILL.md 형식을 Codex CLI와 Antigravity CLI도 .agents/skills 폴더에서 읽어요 (공개 형식 agentskills.io).", rise(3)))
o.append(caption("CLAUDE.md는 늘 들어가고, 스킬은 필요할 때만 들어가요.", 950, 4))
W("skills", o, "스킬은 필요할 때 펴 보는 레시피 카드예요. 폴더 하나에 SKILL.md를 두고, 맨 위에 이름과 언제 쓰는지를 적어요. Claude Code는 처음에 모든 스킬의 이름과 설명만 창에 넣어요. 그러다 설명과 맞는 부탁이 오면 그 스킬의 본문을 읽고 순서대로 해요. 그래서 스킬이 많아도 창을 많이 차지하지 않아요. 슬래시 명령처럼 이름으로 직접 불러도 돼요. CLAUDE.md가 늘 지킬 약속이라면, 스킬은 가끔 하는 긴 절차를 담아요. 같은 형식을 Codex CLI와 Antigravity CLI도 읽어요.")

# subagents
o = [sec("subagents")] + head(EB[4], "서브에이전트는 자기 책상에서 일하고 요약만 돌려줘요", K5)
o.append(f'<div id="sa-main" style="position:absolute;left:96px;top:230px;width:700px;height:420px;border:3px solid {INK};border-radius:20px;background:#FFFFFF"></div>')
o.append(label(130, 252, "메인 에이전트의 창", INK, 30))
o.append(f'<div style="position:absolute;left:130px;top:320px;width:240px;height:80px;background:{K3BG};border-radius:10px;display:flex;align-items:center;justify-content:center">' + p(f"font-size:24px;font-weight:700;color:{K3}", "규칙") + '</div>')
o.append(f'<div style="position:absolute;left:390px;top:320px;width:370px;height:80px;background:{K1BG};border-radius:10px;display:flex;align-items:center;justify-content:center">' + p(f"font-size:24px;font-weight:700;color:{K1}", "지금 하는 일") + '</div>')
o.append(f'<div style="position:absolute;left:130px;top:440px;width:630px;height:170px;border:3px dashed #C9CED8;border-radius:12px"></div>')
o.append(label(150, 456, "빈자리가 넉넉해요", GRAY, 22))
SUBY = [230, 470]
for i, y in enumerate(SUBY):
    d = DELAY(i * 150)
    o.append(f'<div{rise(1)}{d} style="position:absolute;left:1124px;top:{y}px;width:700px;height:200px;border:3px solid {K5};border-radius:20px;background:{K5BG}"></div>')
    o.append(label(1154, y + 18, f"서브에이전트 {i + 1}", K5, 28, rise(1) + d))
    o.append(f'<div{rise(1)}{d} style="position:absolute;left:1154px;top:{y + 74}px;width:380px;height:100px;background:#FFFFFF;border-radius:10px;display:flex;align-items:center;padding:0 20px">' + p(f"font-size:24px;color:{GRAY}", "파일 40개 읽기, 검색 열 번") + '</div>')
    o.append(f'<div id="sum{i}"{rise(2)} style="position:absolute;left:1574px;top:{y + 94}px;width:210px;height:60px;border-radius:999px;background:{K5};display:flex;align-items:center;justify-content:center">' + p("font-size:24px;font-weight:700;color:#FFFFFF", "요약 3줄") + '</div>')
o.append(svg(arrowhead("ah-s", "#9AA1AE") + f'<g{WIPE(1)} fill="none" stroke="#9AA1AE" stroke-width="5" stroke-dasharray="12 9" marker-end="url(#ah-s)"><path d="M800,330 L1110,330"/><path d="M800,570 L1110,570"/></g>'))
o.append(label(880, 286, "일 맡기기", GRAY, 24, rise(1)))
o.append(label(880, 526, "일 맡기기", GRAY, 24, rise(1)))
o.append(f'<div{fly(3, "sum0")} style="position:absolute;left:170px;top:520px;width:210px;height:60px;border-radius:999px;background:{K5};display:flex;align-items:center;justify-content:center">' + p("font-size:24px;font-weight:700;color:#FFFFFF", "요약 3줄") + '</div>')
o.append(f'<div{fly(3, "sum1")} style="position:absolute;left:400px;top:520px;width:210px;height:60px;border-radius:999px;background:{K5};display:flex;align-items:center;justify-content:center">' + p("font-size:24px;font-weight:700;color:#FFFFFF", "요약 3줄") + '</div>')
SA = ["---", "name: reviewer", "description: 고친 코드를 읽고 실수를 찾아요.", "tools: Read, Grep, Glob", "---", "틀린 줄과 이유만 짧게 알려 줘요."]
o.append(code(96, 690, 1000, SA, 24, ".claude/agents/reviewer.md", tid="sa", pad=14, attrs=rise(4)))
o.append(p(f"position:absolute;left:1160px;top:714px;width:664px;font-size:27px;line-height:1.55;color:{INK}", '<b style="color:' + K5 + '">나누면 좋은 일</b><br>서로 겹치지 않는 일, 많이 읽고 조금 답하는 일<br><b style="color:' + RED + '">나누면 안 좋은 일</b><br>같은 파일을 같이 고치는 일', rise(4)))
W("subagents", o, "서브에이전트는 자기 책상에서 일하고 요약만 돌려주는 팀원이에요. 메인 에이전트가 일을 맡기면, 서브에이전트는 자기만의 컨텍스트 창을 새로 받아요. 거기서 파일 마흔 개를 읽든 검색을 열 번 하든 메인의 창은 차지 않아요. 끝나면 요약 몇 줄만 돌려줘요. 서로 겹치지 않는 일이나, 많이 읽고 조금 답하는 일에 잘 맞아요. 같은 파일을 동시에 고치는 일은 부딪히니 나누지 않아요. 아래처럼 .claude/agents에 파일을 두면 이름, 설명, 쓸 수 있는 도구를 정한 서브에이전트가 생겨요. 이 수업 자료도 챕터마다 작업을 나눠 동시에 만들어요.")

# where to put what
o = [sec("where")] + head(EB[4], "무엇을 어디에 둘까", K5)
WT = [("매번 지킬 약속", "CLAUDE.md, AGENTS.md", "실행 명령, 커밋 메시지 형식", K3), ("꼭 막아야 할 일", "deny, 훅", "rm -rf, .env 읽기", K4),
      ("자주 하는 안전한 명령", "allow", "uv run, git status", K4), ("가끔 하는 긴 절차", "스킬", "가격 바꾸기, 공지 쓰기", K5),
      ("외부 서비스", "MCP", "GitHub, 데이터베이스", K4), ("크고 나눌 수 있는 일", "서브에이전트", "검토, 넓은 검색", K5), ("맞았는지 확인", "검사 스크립트", "테스트, boxcheck", K5)]
WW = [470, 520, 640]
o.append(rule_row(96, 210, 1728, 60, ["상황", "넣을 곳", "예"], WW, fs=24, bold=(0, 1, 2), colors={0: GRAY, 1: GRAY, 2: GRAY}))
for i, (a, b, c, col) in enumerate(WT):
    o.append(rule_row(96, 270 + i * 92, 1728, 92, [e(a), e(b), e(c)], WW, fs=29, bold=(1,), colors={1: col, 2: SUB}, attrs=rise(min(i // 2 + 1, 4)) + f' id="wt{i}"'))
o.append(caption("부탁은 규칙 파일에, 강제는 권한과 훅에, 확인은 검사에 맡겨요.", 950, 5))
W("where", o, "지금까지 본 부품을 어디에 둘지 한 장에 모았어요. 매번 지킬 약속은 CLAUDE.md나 AGENTS.md에 적어요. 꼭 막아야 할 일은 규칙만 믿지 말고 deny나 훅으로 막아요. 자주 쓰는 안전한 명령은 allow에 넣어 묻지 않게 해요. 가끔 하는 긴 절차는 스킬로 떼어 내고, 외부 서비스는 MCP로 붙여요. 크고 나눌 수 있는 일은 서브에이전트에게 맡기고, 결과는 검사 스크립트로 확인해요.")

# =====================================================================================================
# part 6: pitfalls and real cases
# =====================================================================================================
o = [sec("pitfalls")] + head(EB[5], "자주 걸리는 함정 여섯 가지", K6)
PF_ = [("AGENTS.md를 고쳤는데 모르는 척해요", "CLAUDE.md가 있으면 AGENTS.md는 안 읽어요", "CLAUDE.md 첫 줄에 @AGENTS.md"),
       ("확인하지 않고 끝나요", "실행 명령을 모르거나 허락이 없어요", "규칙에 명령, allow에 추가"),
       ("\"지우지 마\"라고 적었는데 지웠어요", "규칙은 부탁이라 잊을 수 있어요", "deny나 훅으로 막기"),
       ("규칙을 자꾸 놓쳐요", "규칙 파일이 길어 중요한 줄이 묻혀요", "긴 절차는 스킬로"),
       ("앞에서 정한 걸 잊어요", "창이 차서 대화가 요약됐어요", "규칙 파일에 적기, /clear"),
       ("모든 권한을 열었다가 사고가 나요", "bypassPermissions는 묻지 않아요", "격리된 곳에서만")]
for i, (q, a_, f_) in enumerate(PF_):
    o.append(f'<div{rise(min(i + 1, 5))} style="position:absolute;left:96px;top:{200 + i * 118}px;width:1728px;height:118px;display:flex;flex-direction:row;align-items:center;gap:26px;border-bottom:2px solid {LINE}">'
             + '<div style="flex:1;display:flex;flex-direction:column;gap:4px">' + p(f"font-size:29px;font-weight:700;color:{RED}", e(q)) + p(f"font-size:25px;color:{INK}", e(a_)) + '</div>'
             + p(f"width:560px;flex:none;font-size:27px;font-weight:700;color:{GR};white-space:pre", "✓ " + e(f_)) + '</div>')
o.append(caption("부탁으로 안 되는 일은 설정과 코드로 막아요.", 950, 5))
W("pitfalls", o, "자주 걸리는 함정을 모았어요. 두 파일이 다 있으면 AGENTS.md를 아무리 고쳐도 Claude Code는 CLAUDE.md만 읽어요. 확인하지 않고 끝나면 실행 명령을 모르거나 허락이 없는 경우가 많아요. 1파트 실행이 그랬어요. 지우지 말라는 규칙은 부탁이라 잊을 수 있으니 deny나 훅으로 막아요. 규칙 파일이 길어지면 중요한 줄이 묻히니 긴 절차는 스킬로 옮겨요. 대화가 길어져 요약되면 말로 정한 약속이 흐려지니 오래 갈 약속은 파일에 적어요. 모든 권한을 여는 모드는 컨테이너처럼 격리된 곳에서만 써요.", ("p6", "함정과 실제 예"))

# real 1: this repo
o = [sec("ex-repo")] + head(EB[5], "실제 예 1: 이 수업 자료 레포의 하네스", K6)
ER = [("규칙 파일", "CLAUDE.md", "수업 규칙, 덱 만들기 다섯 단계, 글쓰기 지침", K3),
      ("긴 절차", "tools/DESIGN.md, HIGHLIGHT.md", "덱을 만들 때만 읽어요", K5),
      ("검사", "check.js, boxcheck.js, playshots.js", "넘친 글자, 모든 장 스크린샷", K5),
      ("한 곳에서 고치기", "curriculum.json + build_readme.py --check", "README 표가 어긋나면 알려 줘요", K5),
      ("나눠 맡기기", "챕터마다 작업 하나", "여러 챕터를 동시에 만들어요", K5),
      ("사람 확인", "전후 미리보기", "강사가 본 뒤에 main에 올려요", K4)]
for i, (k, f_, d, c) in enumerate(ER):
    o.append(f'<div{rise(min(i // 2 + 1, 3))} style="position:absolute;left:96px;top:{210 + i * 116}px;width:1728px;height:116px;display:flex;flex-direction:row;align-items:center;gap:30px;border-bottom:2px solid {LINE}">'
             + p(f"width:300px;flex:none;font-size:30px;font-weight:700;color:{c}", e(k))
             + '<div style="display:flex;flex-direction:column;gap:4px">' + p(f"font-family:{fam(f_)};font-size:28px;font-weight:700;color:{INK}", e(f_)) + p(f"font-size:25px;color:{SUB}", e(d)) + '</div></div>')
o.append(caption("지금 보는 이 덱도 이 하네스를 거쳐 만들었어요.", 950, 4))
W("ex-repo", o, "첫 번째 실제 예는 지금 보는 수업 자료 레포예요. CLAUDE.md에 수업 규칙과 덱 만들기 다섯 단계를 적어 두었어요. 덱 디자인처럼 긴 절차는 tools 폴더의 문서로 떼어 내고 덱을 만들 때만 읽어요. 글자가 넘치는지는 boxcheck, 모든 장의 모습은 playshots 스크린샷으로 검사해요. README 표는 curriculum.json 한 곳에서만 고치고 --check로 어긋남을 찾아요. 여러 챕터는 작업을 나눠 동시에 만들어요. 마지막에는 강사가 전후 미리보기를 본 뒤에 main에 올려요. 사람이 확인하는 단계도 하네스의 한 칸이에요.")

# real 2: build up
o = [sec("ex-build")] + head(EB[5], "실제 예 2: 카페 주문 프로젝트에 하네스를 쌓아요", K6)
TREE = [("o", "cafe-order/"), ("o", "├─ AGENTS.md         규칙"), ("o", "├─ CLAUDE.md         @AGENTS.md"), ("o", "├─ main.py"),
        ("o", "└─ .claude/"), ("o", "   ├─ settings.json  권한, 훅"), ("o", "   ├─ hooks/block_rm.py"), ("o", "   └─ skills/menu-update/")]
o.append(term(96, 220, 820, TREE, 30, tid="t-tree", pad=(34, 40)))
STP = [("규칙 파일", "uv run으로 확인하고 14,500원으로 출력했어요", "3파트"), ("allow", "uv run은 묻지 않고 실행해요", "4파트"), ("훅", "rm -rf를 막자 파일을 하나씩 지웠어요", "4파트"), ("스킬", "가격을 바꿀 때만 절차를 읽어요", "5파트")]
for i, (h_, d_, w_) in enumerate(STP):
    o.append(f'<div{rise(i + 1)} style="position:absolute;left:980px;top:{224 + i * 150}px;width:844px;height:136px;display:flex;flex-direction:row;align-items:center;gap:24px;border-bottom:2px solid {LINE}">'
             + num(i + 1, K6, 38) + '<div style="display:flex;flex-direction:column;gap:4px">'
             + f'<div style="display:flex;flex-direction:row;align-items:baseline;gap:16px">' + p(f"font-size:32px;font-weight:700;color:{INK}", e(h_)) + p(f"font-size:22px;color:{GRAY}", e(w_)) + '</div>'
             + p(f"font-size:26px;color:{SUB}", e(d_)) + '</div></div>')
o.append(caption("한 번에 다 만들지 않아요. 막힌 곳이 보일 때마다 한 칸씩 더해요.", 950, 5))
W("ex-build", o, "두 번째 예는 오늘 실습한 카페 주문 프로젝트예요. 처음에는 main.py 하나였어요. 실행 명령을 몰라 확인을 못 하는 걸 보고 규칙 파일을 더했어요. 공통 규칙은 AGENTS.md에 두고 CLAUDE.md는 그것을 불러와요. 자주 쓰는 uv run은 allow에 넣고, rm -rf는 훅으로 막았어요. 가끔 하는 가격 바꾸기는 스킬로 떼어 냈어요. 처음부터 다 만들 필요는 없어요. 에이전트가 막히거나 실수하는 곳이 보일 때마다 한 칸씩 더하면 돼요. 스킬은 만드는 법만 보였고 이번 실습에서 실행하지는 않았어요.")

# real 3: moving tools
o = [sec("ex-move")] + head(EB[5], "실제 예 3: 도구를 바꿔도 남는 것과 다시 할 것", K6)
MV = [("AGENTS.md", "그대로 읽어요", True), ("스킬 (SKILL.md)", "형식은 같고, 폴더만 .agents/skills로", True), ("검사 스크립트", "그대로 돌려요. 명령일 뿐이에요", True),
      ("MCP 서버", "같은 서버를 쓰고, 연결 설정만 다시", True), ("권한과 훅", "도구마다 형식이 달라서 다시 만들어요", False), ("CLAUDE.md", "Claude Code만 읽어요", False)]
MWW = [440, 860, 200]
o.append(rule_row(96, 210, 1728, 62, ["부품", "Codex CLI나 Antigravity CLI로 옮기면", ""], MWW, fs=24, bold=(0, 1), colors={0: GRAY, 1: GRAY}))
for i, (k, d, ok) in enumerate(MV):
    o.append(rule_row(96, 272 + i * 100, 1728, 100, [e(k), e(d), "그대로" if ok else "다시"], MWW, fs=29, bold=(0, 2), mono=(), colors={0: INK, 2: GR if ok else OR},
                      attrs=f' id="mv{i}"' + rise(1 if ok else 2)))
o.append(caption("규칙과 검사를 파일로 남겨 두면, 도구가 바뀌어도 하네스 대부분이 따라와요.", 950, 3))
W("ex-move", o, "세 번째 예는 같은 프로젝트를 다른 에이전트 도구로 옮기는 경우예요. AGENTS.md는 Codex CLI도 Antigravity CLI도 그대로 읽어요. 스킬은 같은 SKILL.md 형식이라 폴더만 .agents/skills로 옮기면 돼요. 검사 스크립트는 그냥 명령이라 어떤 도구든 실행할 수 있어요. MCP 서버도 그대로 쓰고 연결 설정만 다시 해요. 권한과 훅은 도구마다 설정 형식이 달라서 다시 만들어야 해요. 규칙과 검사를 파일로 남겨 두면 도구가 바뀌어도 하네스 대부분이 따라와요.")

# cheatsheet
o = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;word-break:keep-all;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">하네스 한 장 정리</h2>']
CH = [("규칙 파일", "CLAUDE.md, 없으면 AGENTS.md", K3), ("둘 다 쓰기", "CLAUDE.md 첫 줄에 @AGENTS.md", K3), ("창 관리", "/context  /compact  /clear", K3),
      ("권한 모드", "Shift+Tab, settings.json의 allow deny", K4), ("훅", "PreToolUse에서 종료 코드 2면 막기", K4), ("외부 서비스", "claude mcp add", K4),
      ("스킬", ".claude/skills/이름/SKILL.md", K5), ("서브에이전트", ".claude/agents/이름.md", K5), ("검사", "통과할 때까지 돌리는 스크립트", K5), ("흐름", "프롬프트, 컨텍스트, 루프, 그래프, 하네스", K2)]
for i, (k, d, c) in enumerate(CH):
    x, y = 96 + (i // 5) * 884, 190 + (i % 5) * 124
    o.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:844px;height:110px;display:flex;flex-direction:column;justify-content:center;gap:4px;border-bottom:2px solid {LINE}">'
             + p(f"font-size:26px;font-weight:700;color:{c}", e(k)) + p(f"font-family:{fam(d)};font-size:28px;font-weight:700;color:{INK};white-space:pre", e(d)) + '</div>')
o.append(p(f"position:absolute;left:96px;top:850px;width:1728px;font-size:32px;font-weight:700;line-height:1.5;color:{INK}", "에이전트가 막히는 곳을 보고, 그 자리에 한 칸씩 더해요.<br>" + f'<span style="color:{GRAY}">내 프로젝트에 CLAUDE.md 다섯 줄부터 써 봐요.</span>'))
W("cheatsheet", o, "오늘 본 부품을 한 장에 모았어요. 규칙 파일은 CLAUDE.md, 여러 도구와 같이 쓰려면 AGENTS.md를 두고 CLAUDE.md에서 불러와요. 창이 차면 /compact, 다른 일로 넘어가면 /clear를 써요. 권한은 Shift+Tab과 settings.json으로, 꼭 막을 일은 훅으로 정해요. 외부 서비스는 MCP, 긴 절차는 스킬, 큰일은 서브에이전트에게 맡겨요. 마지막으로 결과는 검사 스크립트로 확인해요. 내 프로젝트에 CLAUDE.md 다섯 줄부터 써 보는 것으로 시작해요.")

# =====================================================================================================
# toc
# =====================================================================================================
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
parts_ = [("Lightbulb", K1, "왜 필요한가", "why", "min"), ("Activity", K2, "AI 엔지니어링의 흐름", "trend", "harness"), ("Book", K3, "규칙과 컨텍스트", "claude-md", "agents-real"),
          ("Wrench", K4, "도구와 권한", "tools", "hook-run"), ("Check", K5, "검사, 스킬, 서브에이전트", "verify", "where"), ("Star", K6, "함정과 실제 예", "pitfalls", "ex-move")]
t = [f'<section id="toc" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;word-break:keep-all;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>']
for i, (ic, c, h, a, b) in enumerate(parts_):
    x, y = 96 + (i // 3) * 884, 230 + (i % 3) * 190
    t.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:844px;height:160px;display:flex;flex-direction:row;align-items:center;gap:28px;border-bottom:2px solid {LINE}">'
             f'<p style="width:70px;font-size:72px;font-weight:900;color:{c}">{i + 1}</p><x-icon name="{ic}" style="width:52px;height:52px;color:{c}"></x-icon>'
             f'<p style="flex:1;font-size:42px;font-weight:700;color:{INK}">{e(h)}</p><p style="font-size:28px;color:{GRAY}">{page[a]}–{page[b]}쪽</p></div>')
t.append(f'<p style="position:absolute;left:96px;top:880px;font-size:30px;color:{SUB}">{page["cheatsheet"]}쪽은 한 장 요약이에요. 예제는 Claude Code로 실제로 실행했어요.</p>')
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(t) + "\n<aside>" + e("1파트는 하네스가 왜 필요한지 실제 실행으로 보여 줘요. 2파트는 프롬프트에서 하네스까지 AI 엔지니어링이 어떻게 바뀌어 왔는지예요. 3파트부터 5파트까지 규칙 파일, 도구와 권한, 검사와 스킬과 서브에이전트를 차례로 뜯어 봐요. 6파트는 자주 걸리는 함정과 실제 예 세 가지예요.") + "</aside>\n</section>\n")
deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-24T10:00:00Z"}, "lists": "css", "title": "AI 에이전트 하네스 만들기", "order": ORDER, "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
print(len(ORDER), "slides")
