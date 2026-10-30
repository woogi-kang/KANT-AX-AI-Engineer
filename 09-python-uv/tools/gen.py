"""Generates every slide of the uv deck and slides/deck.json.

Story: run a .py file, the old way (venv, pip, requirements.txt), then the same work with uv
(init, run, add, tree, remove, sync). Elements keep the same id across scenes so the magic
transition animates only what the command changed.
Terminal output comes from tools/demo.sh (uv 0.11.32, Python 3.14.6).
Usage: python3 tools/gen.py slides
"""
import html, json, os, sys

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
INK, SUB, LINE, CARD = "#1D2330", "#4A5262", "#E1DED6", "#FFFFFF"
BL, GR, OR, PUR, RED, NAVY, TEAL, GRAY = "#2459C9", "#1F8A4C", "#B26A00", "#5A3BB8", "#A33131", "#1E3F8F", "#0F7C86", "#6A7180"
OLD, UV = OR, TEAL          # old way, uv
F_PY, F_LOCK, F_VENV = NAVY, PUR, GR   # pyproject.toml, uv.lock, .venv
TC = {"$": "#F2C46D", "V": "#F2C46D", "A": "#F2C46D", "o": "#D8DEE9", "g": "#7FD18B", "r": "#F28B82", "#": "#8C95A6", "H": "#FFE7A8"}


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


def term_line(kind, text, size):
    t = e(text)
    lead = len(t) - len(t.lstrip(" "))
    t = "&#160;" * lead + t.lstrip(" ")
    if kind == "$":
        return p(f"font-size:{size[0]}px;font-weight:700;line-height:1.35;white-space:nowrap;color:{TC['$']}", "$ " + t)
    if kind == "A":
        return p(f"font-size:{size[0]}px;font-weight:700;line-height:1.35;white-space:nowrap;color:{TC['V']}", '<span style="color:#7FD18B">(hello-uv)</span> $ ' + t)
    if kind == "V":
        return p(f"font-size:{size[0]}px;font-weight:700;line-height:1.35;white-space:nowrap;color:{TC['V']}", '<span style="color:#7FD18B">(.venv)</span> $ ' + t)
    mark = "background:rgba(242,196,109,0.22);border-radius:6px;margin:0 -8px;padding:0 8px;font-weight:700;" if kind == "H" else ""
    return p(f"font-size:{size[1]}px;line-height:1.35;white-space:pre;{mark}color:{TC[kind]}", t if t else "&#160;")


def terminal(lines, left=96, top=196, w=1728, size=(30, 24), tid="term", h=None, attrs=""):
    hh = f"height:{h}px;" if h else ""
    o = [f'<div id="{tid}"{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;{hh}background:#1B2029;border-radius:20px;padding:18px 32px;display:flex;flex-direction:column;gap:2px;font-family:{MONO};font-variant-ligatures:none">']
    o += [term_line(k, t, size) for k, t in lines]
    o.append('</div>')
    return o


def caption(text, top=944):
    return p(f"position:absolute;left:96px;top:{top}px;width:1728px;font-size:34px;font-weight:700;line-height:1.4;color:{INK}", text, ' id="caption" data-build-in="rise"')


def num(i, color, size=56):
    return p(f"width:{size + 16}px;height:{size + 16}px;flex:none;border-radius:50%;background:{color};color:#FFFFFF;font-size:{size * 0.6:.0f}px;font-weight:900;line-height:{size + 16}px;text-align:center", str(i))


def chip(text, color, size=24, mono=True, extra=""):
    fam = f"font-family:{MONO};" if mono else ""
    return p(f"{fam}font-size:{size}px;font-weight:700;line-height:1.5;white-space:nowrap;color:{color};background:#F1F0EC;border-radius:10px;padding:6px 16px;{extra}", e(text))


def arrow(left, top, w, h, color, kind="arrow-right", attrs=""):
    return f'<x-shape kind="{kind}"{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:{color}"></x-shape>'


def code_card(cid, name, lines, left, top, w, color=NAVY, size=26, marks=(), attrs="", h=None, notes=None):
    """A file card: name tab on top, code below. marks: line indexes to highlight."""
    hh = f"height:{h}px;" if h else ""
    o = [f'<div id="{cid}"{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;{hh}background:{CARD};border:2px solid {LINE};border-top:8px solid {color};border-radius:18px;padding:16px 26px 20px;display:flex;flex-direction:column;gap:4px">',
         p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{color};margin-bottom:6px", e(name))]
    for i, ln in enumerate(lines):
        mk = f"background:#FFF1C9;border-radius:6px;margin:0 -10px;padding:0 10px;" if i in marks else ""
        code = p(f"font-family:{MONO};font-size:{size}px;line-height:1.4;white-space:pre;{mk}color:{INK}", e(ln) if ln else "&#160;")
        if notes and i in notes:
            k, txt = notes[i]
            code = (f'<div style="display:flex;flex-direction:row;align-items:center;gap:24px">' + code
                    + p(f"font-size:{size}px;font-weight:700;color:{color}", "◀ " + e(txt), f' data-build-in="fade order {k}"') + '</div>')
        o.append(code)
    o.append('</div>')
    return o


# ---------- folder panel (files keep ids across scenes) ----------
FNOTE = {".git": "Git 저장소 (02)", ".gitignore": "Git에 안 올릴 목록", ".python-version": "쓸 파이썬 버전", ".venv": "가상환경 (패키지 상자)",
         "README.md": "프로젝트 소개 글", "main.py": "실행할 코드", "pyproject.toml": "프로젝트 설명서", "uv.lock": "정확한 버전 목록"}
FDIR = {".git", ".venv"}


def folder(files, left=1000, top=200, w=824, title="hello-uv", new=(), notes=True, off=(), pre=""):
    """files: names in ls -a order. new: names drawn as just created (pop in). off: names crossed out (not uploaded)."""
    rh = 70
    h = 76 + len(files) * rh + 16
    o = [f'<div id="{pre}fold" style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:#FDFCF9;border:2px solid {LINE};border-radius:22px"></div>',
         p(f"position:absolute;left:{left + 28}px;top:{top + 20}px;width:{w - 56}px;font-family:{MONO};font-size:26px;font-weight:700;color:{GRAY}", e(title + "/"), f' id="{pre}fold-title"')]
    for i, name in enumerate(files):
        y = top + 76 + i * rh
        isnew = name in new
        crossed = name in off
        bg = "#E6F4EC" if isnew else ("#F1F0EC" if crossed else CARD)
        bd = f"2px solid {GR}" if isnew else f"2px solid {LINE}"
        glyph = (f'<div style="width:28px;height:22px;flex:none;background:{"#E0B54A" if name in FDIR else "#B9BFCB"};border-radius:4px"></div>' if name in FDIR
                 else f'<div style="width:22px;height:27px;flex:none;background:#B9BFCB;border-radius:3px"></div>')
        col = "#9AA0AB" if crossed else INK
        deco = "text-decoration:line-through;" if crossed else ""
        attrs = f' id="{pre}f-{name}"' + (' data-build-in="pop"' if isnew else "")
        o.append(f'<div{attrs} style="position:absolute;left:{left + 24}px;top:{y}px;width:{w - 48}px;height:58px;background:{bg};border:{bd};border-radius:12px;padding:0 18px;display:flex;flex-direction:row;gap:16px;align-items:center">'
                 + glyph + p(f"width:300px;flex:none;font-family:{MONO};font-size:26px;font-weight:700;white-space:nowrap;{deco}color:{col}", e(name))
                 + (p(f"flex:1;font-size:24px;color:{SUB}", e(FNOTE.get(name, ""))) if notes else "") + '</div>')
    return o


# ---------- the three places uv add/remove change ----------
def three(state, left=1060, top=200, w=764):
    """state: dict with keys py, lock, venv -> (main text, sub text, changed?)"""
    o = []
    items = [("py", "pyproject.toml", "내가 고른 패키지", F_PY), ("lock", "uv.lock", "따라온 것까지 정확한 버전", F_LOCK), ("venv", ".venv", "실제로 설치된 패키지", F_VENV)]
    for i, (k, name, role, c) in enumerate(items):
        y = top + i * 236
        main, subt, changed = state[k]
        ring = f"box-shadow:0 0 0 4px {c}33;" if changed else ""
        o.append(f'<div id="b-{k}" data-build-in="rise order {i + 1}" style="position:absolute;left:{left}px;top:{y}px;width:{w}px;height:212px;background:{CARD};border:2px solid {LINE};border-left:12px solid {c};border-radius:20px;padding:20px 30px;{ring}display:flex;flex-direction:column;gap:8px">'
                 + '<div style="display:flex;flex-direction:row;gap:18px;align-items:baseline">'
                 + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{c}", e(name)) + p(f"font-size:24px;color:{GRAY}", e(role)) + '</div>'
                 + p(f"font-family:{MONO};font-size:27px;font-weight:700;line-height:1.4;white-space:pre;color:{INK}", e(main))
                 + p(f"font-size:24px;line-height:1.4;color:{SUB}", e(subt)) + '</div>')
    return o


# ---------- real output (tools/demo.sh) ----------
INIT_OUT = [("o", "Downloading cpython-3.14.6-linux-x86_64-gnu (download) (34.3MiB)"), ("o", " Downloaded cpython-3.14.6-linux-x86_64-gnu (download)"),
            ("g", "Initialized project `hello-uv` at `/home/kim/hello-uv`")]
ADD = '"fastapi[standard]"'
PKGS = ["agent-detector==2.0.0", "annotated-doc==0.0.5", "annotated-types==0.8.0", "anyio==4.15.1", "websockets==17.3"]   # first 4 and last of 59
ADD_OUT = [("o", "Resolved 62 packages in 858ms"), ("#", "  ... Downloading 줄 생략 ..."), ("o", "Prepared 59 packages in 418ms"),
           ("o", "Installed 59 packages in 17ms")] + [("g", " + " + x) for x in PKGS[:4]] + [("#", "   ... 54줄 생략 ..."), ("g", " + " + PKGS[-1])]
SERVER = [("o", " ⚡️ Starting FastAPI in development mode"), ("H", " 🌐 Server started at http://127.0.0.1:8000"), ("o", "    Documentation at http://127.0.0.1:8000/docs"),
          ("o", "INFO:     Application startup complete."), ("o", 'INFO:     127.0.0.1:56432 - "GET / HTTP/1.1" 200 OK')]
FILES0 = [".git", ".gitignore", ".python-version", "README.md", "main.py", "pyproject.toml"]
FILES1 = [".git", ".gitignore", ".python-version", ".venv", "README.md", "main.py", "pyproject.toml", "uv.lock"]
MAIN_REQ = ["from fastapi import FastAPI", "", "app = FastAPI()", "", "", '@app.get("/")', "def home():", '    return {"message": "안녕하세요"}']

# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#7FD6DC;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 보충 학습 자료</p>',
       '<h1 style="font-size:104px;font-weight:900;line-height:1.1;color:#F6F5F1">uv로<br>파이썬 시작하기</h1>',
       '<p style="font-size:40px;line-height:1.4;color:#BFC6D4">예전 방식과 비교하고,<br>자주 쓰는 명령 익히기</p>']
cov.append(f'<div style="position:absolute;left:1060px;top:280px;width:720px;height:520px;background:#252B36;border-radius:24px;padding:40px 44px;display:flex;flex-direction:column;gap:8px;font-family:{MONO}">')
for k, l in [("$", "$ uv init hello-uv"), ("#", "  프로젝트 만들기"), ("$", "$ uv add \"fastapi[standard]\""), ("#", "  패키지 넣기"), ("$", "$ uv run main.py"), ("#", "  실행하기"),
             ("$", "$ uv sync"), ("#", "  다른 컴퓨터에서 그대로")]:
    cov.append(p(f"font-size:32px;line-height:1.45;white-space:pre;font-weight:700;color:{TC[k]}", e(l)))
cov.append('</div>')
W("cover", cov, "오늘부터 파이썬을 시작해요. 파이썬 프로젝트는 uv라는 도구 하나로 만들고 실행해요. 먼저 예전에는 어떻게 했는지 짧게 보고, uv로 바꾸면 무엇이 편해지는지 비교해요. 그다음 uv init, uv run, uv add, uv remove, uv sync를 순서대로 쳐 봐요.", ("intro", "파이썬 실행"))

ORDER.append("toc")   # written last, after page numbers are known

# ---------- part 1: how python runs ----------
EB1 = "1. 파이썬은 어떻게 실행되나"
o = [sec("run")] + head(EB1, "파이썬 코드는 python이 읽고 실행해요", BL)
o += code_card("c-hello", "hello.py", ['print("안녕하세요")'], 96, 300, 520, BL, 34)
o.append(arrow(660, 350, 110, 64, "#C9CED8", attrs=' data-build-in="fade order 1"'))
o.append(f'<div data-build-in="pop order 1" style="position:absolute;left:810px;top:270px;width:340px;height:220px;background:{BL};border-radius:28px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px">'
         + f'<x-icon name="Settings" style="width:64px;height:64px;color:#FFFFFF"></x-icon>' + p(f"font-family:{MONO};font-size:40px;font-weight:700;color:#FFFFFF", "python") + '</div>')
o.append(arrow(1194, 350, 110, 64, "#C9CED8", attrs=' data-build-in="fade order 2"'))
o += terminal([("o", "안녕하세요")], left=1344, top=322, w=480, size=(34, 34), tid="t-out", attrs=' data-build-in="pop order 2"')
o += terminal([("$", "python3 hello.py"), ("o", "안녕하세요")], top=600, w=1728, size=(34, 30), attrs=' data-build-in="rise order 3"')
o.append(caption(".py 파일은 글자일 뿐이에요. python 프로그램이 한 줄씩 읽어서 실행해요.", 860))
W("run", o, "hello.py는 메모장으로도 열 수 있는 글자 파일이에요. 이 파일을 읽어서 실제로 움직이게 하는 프로그램이 python이에요. 그래서 파이썬을 쓰려면 먼저 컴퓨터에 python 프로그램이 있어야 해요. Mac과 Linux는 python3, Windows는 python이라는 이름으로 부르는 경우가 많아요. 출력은 uv가 받은 Python 3.14.6에서 실행한 결과예요.", ("run", "파이썬은 어떻게 실행되나"))

o = [sec("pkg")] + head(EB1, "남이 만든 코드 묶음을 패키지라고 해요", BL)
o.append(f'<div style="position:absolute;left:96px;top:250px;width:760px;height:560px;background:{CARD};border:2px solid {LINE};border-radius:24px;padding:32px 40px;display:flex;flex-direction:column;gap:24px">'
         + '<div style="display:flex;flex-direction:row;gap:18px;align-items:center">' + f'<x-icon name="Archive" style="width:52px;height:52px;color:{PUR}"></x-icon>'
         + p(f"font-size:40px;font-weight:700;color:{PUR}", "PyPI") + p(f"font-size:28px;color:{GRAY}", "파이썬 패키지 창고") + '</div>'
         + '<div style="display:flex;flex-direction:row;flex-wrap:wrap;gap:16px">'
         + "".join(chip(n, INK, 28, extra=("background:#E7DEFC;" if n == "fastapi" else "")) for n in ["fastapi", "pandas", "numpy", "openai", "requests", "pytest", "matplotlib", "… 60만 개 넘게"])
         + '</div></div>')
o.append(arrow(900, 490, 160, 80, PUR, attrs=' data-build-in="fade order 1"'))
o.append(p(f"position:absolute;left:880px;top:420px;width:200px;font-size:26px;font-weight:700;text-align:center;color:{PUR}", "받아서 설치", ' data-build-in="fade order 1"'))
o.append(f'<div data-build-in="pop order 2" style="position:absolute;left:1104px;top:250px;width:720px;height:560px;background:#FDFCF9;border:2px dashed #B9BFCB;border-radius:24px;padding:32px 40px;display:flex;flex-direction:column;gap:24px">'
         + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:{GRAY}", "내 프로젝트/")
         + chip("main.py", INK, 28, extra="align-self:flex-start;background:#FFFFFF;border:2px solid #E1DED6;")
         + chip("fastapi", INK, 28, extra="align-self:flex-start;background:#E7DEFC;")
         + p(f"font-size:28px;line-height:1.5;color:{SUB}", "fastapi로 웹 서버를 만들고 켜요.") + '</div>')
o.append(caption("이 자료는 fastapi를 넣고, 쓰고, 빼 봐요.", 880))
W("pkg", o, "파이썬으로 하는 일 대부분은 남이 만들어 둔 코드를 가져다 써요. 이 코드 묶음을 패키지라고 하고, PyPI라는 인터넷 창고에 모여 있어요. 데이터 분석은 pandas, AI API는 openai 같은 패키지를 받아 써요. 오늘 예시는 웹 서버를 만드는 fastapi예요. 패키지를 받아서 내 프로젝트에 넣는 방법이 예전 방식과 uv에서 달라요.")

# ---------- part 2: old way vs uv ----------
EB2 = "2. 예전 방식과 비교"
o = [sec("old-venv")] + head(EB2, "가상환경은 프로젝트마다 따로 쓰는 패키지 상자예요", OLD)
o.append(f'<div style="position:absolute;left:96px;top:230px;width:1728px;height:120px;background:#ECEAE3;border-radius:20px;display:flex;flex-direction:row;gap:24px;align-items:center;padding:0 40px">'
         + f'<x-icon name="Settings" style="width:48px;height:48px;color:{GRAY}"></x-icon>' + p(f"font-size:32px;font-weight:700;color:{INK}", "컴퓨터에 설치한 파이썬") + p(f"font-size:26px;color:{GRAY}", "여기에 바로 넣으면 모든 프로젝트가 같이 써요") + '</div>')
for i, (name, ver, c) in enumerate([("project-a", "fastapi 0.162.0", BL), ("project-b", "fastapi 0.110.0", GR)]):
    x = 96 + i * 888
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:{x}px;top:420px;width:840px;height:400px;background:#FDFCF9;border:2px solid {LINE};border-radius:24px;padding:28px 36px;display:flex;flex-direction:column;gap:20px">'
             + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:{GRAY}", name + "/")
             + chip("main.py", INK, 28, extra="align-self:flex-start;background:#FFFFFF;border:2px solid #E1DED6;")
             + f'<div style="flex:1;background:#E6F4EC;border:3px solid {GR};border-radius:18px;padding:20px 28px;display:flex;flex-direction:column;gap:12px">'
             + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{GR}", ".venv/") + chip(ver, c, 28, extra="align-self:flex-start;background:#FFFFFF;") + '</div></div>')
o.append(caption("프로젝트끼리 패키지 버전이 달라도 부딪히지 않아요. uv도 이 .venv를 그대로 써요.", 880))
W("old-venv", o, "가상환경이 없으면 패키지가 컴퓨터 파이썬 한 곳에 쌓여요. 그러면 A 프로젝트는 fastapi 0.162, B 프로젝트는 0.110이 필요할 때 둘 중 하나가 깨져요. 그래서 프로젝트 폴더마다 .venv라는 상자를 두고 그 안에 패키지를 넣어요. .venv는 점으로 시작해서 ls -a로만 보여요(01). 이 개념은 uv에서도 똑같아요. 다른 건 누가 상자를 만들고 켜느냐예요.", ("old", "예전 방식과 비교"))

o = [sec("vs")] + head(EB2, "예전에 직접 치던 6개가 uv 명령 3개로 줄어요", UV)
o.append(f'<div style="position:absolute;left:96px;top:226px;width:1728px;height:60px;display:flex;flex-direction:row;gap:24px;align-items:center">'
         + p(f"width:250px;flex:none;font-size:26px;font-weight:700;color:{GRAY}", "할 일") + p(f"width:700px;flex:none;font-size:28px;font-weight:700;color:{OLD}", "예전")
         + p(f"flex:1;font-size:28px;font-weight:700;color:{UV}", "uv") + '</div>')
VS = [("파이썬 설치", "python.org에서 받아 설치", "없으면 uv가 받아요"), ("프로젝트 만들기", "python3 -m venv .venv", "uv init hello-uv"),
      ("가상환경 켜기", "source .venv/bin/activate", "uv run이 알아서 켜요"), ("패키지 넣기", 'pip install "fastapi[standard]"', 'uv add "fastapi[standard]"'),
      ("목록 적기", "pip freeze > requirements.txt", "uv add가 알아서 적어요"), ("실행", "fastapi dev main.py", "uv run fastapi dev main.py")]
for i, (job, old_, new) in enumerate(VS):
    y = 296 + i * 104
    cmd = new.startswith(("uv init", "uv add \"", "uv run fastapi"))
    right = (p(f"font-family:{MONO};font-size:28px;font-weight:700;white-space:nowrap;color:#FFFFFF;background:{UV};border-radius:12px;padding:12px 22px", e(new)) if cmd
             else p(f"font-size:27px;font-weight:700;color:{UV};border:2px dashed #8CC9CE;border-radius:12px;padding:10px 22px", e(new)))
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:88px;display:flex;flex-direction:row;gap:24px;align-items:center">'
             + p(f"width:250px;flex:none;font-size:28px;font-weight:700;color:{INK}", job)
             + f'<div data-build-in="rise order 1" style="width:700px;height:88px;flex:none;background:#FBEFD9;border-radius:14px;display:flex;align-items:center;padding:0 24px">'
             + p(f"{'' if i == 0 else 'font-family:' + MONO + ';'}font-size:27px;font-weight:700;white-space:nowrap;color:#8A6A33", e(old_)) + '</div>'
             + f'<div data-build-in="rise order {2 if cmd else 3}" style="flex:1;display:flex;flex-direction:row">' + right + '</div></div>')
o.append(caption("파이썬, 가상환경, 목록 적기는 uv가 대신해요. 직접 치는 건 uv로 시작하는 명령뿐이에요.", 944))
W("vs", o, "같은 웹 서버 프로젝트를 예전 방식과 uv로 만들 때 치는 명령이에요. 예전에는 왼쪽 여섯 단계를 순서대로 직접 챙겼어요. 하나라도 빼먹으면 ModuleNotFoundError가 났어요. uv는 init, add, run 세 명령만 쳐요. 나머지 세 칸은 uv가 알아서 해요. 예전 방식은 따라 치지 않고 눈으로만 봐요. Windows Git Bash에서는 예전 3번이 source .venv/Scripts/activate예요. 인터넷 자료에 pip install이 아직 많이 나와요. 우리 프로젝트에서는 uv add로 바꿔 쳐요.")

o = [sec("why")] + head(EB2, "uv가 대신 해 주는 세 가지", UV)
WHY = [("Settings", "파이썬을 받아요", "파이썬이 없으면 uv가 받아서 써요.", "설치 순서를 몰라도 돼요"),
       ("PaperPlane", "가상환경을 켜고 꺼요", "uv run이 실행할 때만 .venv를 써요.", "켜는 걸 잊을 일이 없어요"),
       ("Book", "목록을 적어요", "uv add, uv remove가 pyproject.toml과 uv.lock을 고쳐요.", "다른 컴퓨터는 uv sync 한 번")]
for i, (ic, h, a_, b_) in enumerate(WHY):
    x = 96 + i * 588
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:{x}px;top:240px;width:552px;height:560px;background:{CARD};border:2px solid {LINE};border-top:12px solid {UV};border-radius:24px;padding:40px 38px;display:flex;flex-direction:column;gap:26px">'
             + f'<x-icon name="{ic}" style="width:64px;height:64px;color:{UV}"></x-icon>'
             + p(f"font-size:40px;font-weight:700;line-height:1.3;color:{INK}", h) + p(f"font-size:30px;line-height:1.5;color:{SUB}", e(a_))
             + '<div style="flex:1"></div>' + p(f"font-size:28px;font-weight:700;color:{UV};background:#E3F3F4;border-radius:12px;padding:12px 20px", e(b_)) + '</div>')
o.append(caption("한 번 받은 패키지는 캐시에 두고 다시 받지 않아서 설치도 빨라요.", 880))
W("why", o, "uv는 Astral이라는 회사가 만든 파이썬 프로젝트 관리 도구예요. 예전에 python.org, venv, pip, requirements.txt로 따로 하던 일을 uv 하나가 해요. 세 칸 모두 5파트와 6파트에서 직접 확인해요. 속도도 pip보다 빨라요. 같은 패키지를 다시 넣을 때 0.01초 만에 끝나는 것을 5파트에서 봐요.")

# ---------- part 3: install uv ----------
EB3 = "3. uv 설치하기"
o = [sec("install")] + head(EB3, "명령 한 줄로 uv를 설치해요", UV)
for i, (osn, where, cmd, sub) in enumerate([("macOS", "터미널", "brew install uv", "Homebrew가 없으면 brew.sh의 설치 명령을 먼저 쳐요"),
                                            ("Windows", "PowerShell", "winget install --id=astral-sh.uv -e", "winget은 Windows 10, 11에 들어 있어요")]):
    y = 220 + i * 200
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:96px;top:{y}px;width:1728px;height:176px;background:{CARD};border:2px solid {LINE};border-left:12px solid {UV};border-radius:20px;padding:24px 36px;display:flex;flex-direction:column;gap:16px">'
             + '<div style="display:flex;flex-direction:row;gap:20px;align-items:baseline">' + p(f"font-size:34px;font-weight:700;color:{INK}", osn) + p(f"font-size:26px;color:{GRAY}", where + "에서 쳐요") + '</div>'
             + '<div style="display:flex;flex-direction:row;gap:28px;align-items:center">'
             + p(f"font-family:{MONO};font-size:32px;font-weight:700;white-space:nowrap;color:{INK};background:#F1F0EC;border-radius:10px;padding:10px 22px", e(cmd))
             + p(f"font-size:24px;color:{SUB}", e(sub)) + '</div></div>')
o.append(f'<div data-build-in="rise order 3" style="position:absolute;left:96px;top:640px;width:1728px;height:84px;display:flex;flex-direction:row;gap:24px;align-items:center">'
         + num(3, UV, 44) + p(f"font-size:32px;font-weight:700;color:{INK}", "터미널을 닫았다가 새로 열어요. Windows는 Git Bash를 새로 열어요.") + '</div>')
o += terminal([("$", "uv --version"), ("o", "uv 0.11.32 (x86_64-unknown-linux-gnu)")], top=750, size=(32, 28), attrs=' data-build-in="rise order 4"')
W("install", o, "설치는 컴퓨터마다 한 번만 해요. Mac은 Homebrew로 설치해요. brew --version에 버전이 나오면 Homebrew가 이미 있어요. 없으면 brew.sh에 있는 설치 명령을 터미널에 붙여 넣어 먼저 설치해요. Windows는 시작 메뉴에서 PowerShell을 열어 winget 명령을 쳐요. 약관 동의를 물으면 Y를 쳐요. 설치 프로그램이 출력하는 줄은 버전과 컴퓨터마다 달라서 옮기지 않았어요. 설치가 끝나면 터미널을 새로 열어야 uv 명령을 찾아요. uv --version에 버전이 나오면 준비가 끝났어요. 숫자는 설치한 날에 따라 달라요.", ("uv", "uv 설치하기"))

# ---------- part 4: uv init, uv run ----------
EB4 = "4. 프로젝트 만들고 실행하기"
o = [sec("init", "magic")] + head(EB4, "uv init으로 프로젝트를 만들어요", BL)
o += terminal([("$", "cd ~"), ("$", "uv init hello-uv")] + INIT_OUT + [("$", "cd hello-uv"), ("$", "ls -a")], w=910, size=(28, 21))
o += folder(FILES0, new=FILES0, left=1040, w=784)
o.append(caption("컴퓨터에 파이썬이 없으면 uv가 받아서 써요. 위 두 줄이 그 표시예요.", 900))
W("init", o, "수업 저장소 hello-git 안이 아니라 홈 폴더에서 시작해요. uv init 뒤에 적은 이름으로 폴더가 생겨요. 컴퓨터에 파이썬이 없어서 uv가 3.14.6을 받았어요. 파이썬이 이미 있는 컴퓨터는 Downloading 줄이 없고 그 버전을 써요. uv init은 git init까지 해 줘서 .git이 생겨요. ls -a 출력은 오른쪽 그림과 같아서 뺐어요. 출력의 폴더 주소는 01처럼 /home/kim으로 바꿨어요.", ("init", "프로젝트 만들고 실행하기"))

o = [sec("init-files")] + head(EB4, "pyproject.toml은 프로젝트 설명서예요", BL)
py0 = ['[project]', 'name = "hello-uv"', 'version = "0.1.0"', 'description = "Add your description here"', 'readme = "README.md"', 'requires-python = ">=3.14"', 'dependencies = []']
o += code_card("c-py", "pyproject.toml", py0, 96, 210, 1728, F_PY, 28, marks=(1, 5, 6), notes={1: (1, "프로젝트 이름"), 5: (2, "쓸 수 있는 파이썬 버전"), 6: (3, "쓰는 패키지, 아직 없어요")})
o += code_card("c-ver", ".python-version", ["3.14"], 96, 650, 480, BL, 30, attrs=' data-build-in="rise order 4"')
o += code_card("c-main", "main.py", ["def main():", '    print("Hello from hello-uv!")', "", "", 'if __name__ == "__main__":', "    main()"], 620, 650, 1204, BL, 24, attrs=' data-build-in="rise order 5"')
W("init-files", o, "pyproject.toml은 이 프로젝트가 무엇이고 무엇이 필요한지 적은 파일이에요. 예전의 requirements.txt가 하던 일도 여기 dependencies 칸이 해요. 이 파일은 손으로 고치지 않고 uv add, uv remove로 바꿔요. .python-version은 이 폴더에서 쓸 파이썬 버전이에요. main.py는 uv가 만들어 준 연습용 코드예요. 맨 아래 두 줄은 이 파일을 직접 실행할 때 main()을 부르라는 뜻이에요. 지금은 그대로 둬요.")

o = [sec("run1", "magic")] + head(EB4, "uv run으로 실행해요", BL)
o += terminal([("$", "uv run main.py"), ("o", "Using CPython 3.14.6"), ("o", "Creating virtual environment at: .venv"), ("H", "Hello from hello-uv!")], w=910, size=(28, 24))
o += folder(FILES1, new=(".venv", "uv.lock"), left=1040, w=784)
o.append(caption("처음 한 번 .venv와 uv.lock을 만들어요. activate는 치지 않아요.", 900))
W("run1", o, "uv run 뒤에 실행할 파일을 적어요. 처음 실행하면 uv가 가상환경 .venv를 만들고, 그 안의 파이썬으로 main.py를 실행해요. 예전의 python3 -m venv .venv와 activate를 uv run이 대신한 거예요. uv.lock은 패키지의 정확한 버전을 적는 파일이에요. 지금은 패키지가 없어서 거의 비어 있어요.")

o = [sec("run2")] + head(EB4, "두 번째부터는 바로 실행돼요", BL)
o += terminal([("$", "uv run main.py"), ("H", "Hello from hello-uv!")], size=(32, 28))
flow = [("uv run main.py", UV, True), (".venv 안의 파이썬", GR, False), ("main.py 실행", BL, False)]
for i, (t, c, mono) in enumerate(flow):
    x = 96 + i * 600
    o.append(f'<div data-build-in="pop order {i + 1}" style="position:absolute;left:{x}px;top:400px;width:520px;height:150px;background:{CARD};border:3px solid {c};border-radius:24px;display:flex;align-items:center;justify-content:center">'
             + p(f"{'font-family:' + MONO + ';' if mono else ''}font-size:34px;font-weight:700;color:{c}", e(t)) + '</div>')
    if i < 2:
        o.append(arrow(x + 530, 445, 60, 60, "#C9CED8", attrs=f' data-build-in="fade order {i + 2}"'))
o.append(f'<div data-build-in="rise order 4" style="position:absolute;left:96px;top:620px;width:1728px;height:220px;display:flex;flex-direction:row;gap:28px">'
         + f'<div style="flex:1;background:{CARD};border:2px solid {LINE};border-top:8px solid {OLD};border-radius:20px;padding:24px 32px;display:flex;flex-direction:column;gap:12px">'
         + p(f"font-size:28px;font-weight:700;color:{OLD}", "예전") + p(f"font-family:{MONO};font-size:28px;font-weight:700;line-height:1.5;color:{INK}", "source .venv/bin/activate<br>python main.py") + '</div>'
         + f'<div style="flex:1;background:{CARD};border:2px solid {LINE};border-top:8px solid {UV};border-radius:20px;padding:24px 32px;display:flex;flex-direction:column;gap:12px">'
         + p(f"font-size:28px;font-weight:700;color:{UV}", "uv") + p(f"font-family:{MONO};font-size:28px;font-weight:700;line-height:1.5;color:{INK}", "uv run main.py") + '</div></div>')
o.append(caption("uv run은 켜고, 실행하고, 끄는 일을 한 번에 해요.", 900))
W("run2", o, ".venv가 이미 있어서 바로 결과만 나와요. uv run은 실행할 때만 .venv의 파이썬을 쓰고 끝나면 원래대로 돌아와요. 그래서 프롬프트에 (.venv)가 붙지 않고, 끄는 걸 잊을 일도 없어요. main.py를 고친 뒤에도 같은 명령으로 다시 실행해요. uv run python --version처럼 쓰면 이 프로젝트의 파이썬 버전을 볼 수 있어요.")

o = [sec("act")] + head(EB4, "가상환경을 직접 켤 수도 있어요", BL)
acts = [("macOS, Linux", "터미널", "source .venv/bin/activate"), ("Windows", "Git Bash", "source .venv/Scripts/activate"),
        ("Windows", "PowerShell", ".venv\\Scripts\\activate"), ("끄기", "모든 터미널", "deactivate")]
for i, (osn, where, cmd) in enumerate(acts):
    y = 210 + i * 132
    c = GRAY if i == 3 else GR
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:96px;top:{y}px;width:860px;height:116px;background:{CARD};border:2px solid {LINE};border-left:12px solid {c};border-radius:18px;padding:14px 28px;display:flex;flex-direction:column;justify-content:center;gap:8px">'
             + '<div style="display:flex;flex-direction:row;gap:16px;align-items:baseline">' + p(f"font-size:28px;font-weight:700;color:{INK}", osn) + p(f"font-size:24px;color:{GRAY}", where) + '</div>'
             + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{c}", e(cmd)) + '</div>')
o += terminal([("$", "source .venv/bin/activate"), ("A", "which python"), ("o", "/home/kim/hello-uv/.venv/bin/python"), ("A", "python --version"), ("o", "Python 3.14.6"),
               ("A", "python main.py"), ("H", "Hello from hello-uv!"), ("A", "deactivate"), ("$", "")], left=1000, top=210, w=824, size=(28, 24), attrs=' data-build-in="rise order 5"')
o.append(caption("켜면 프롬프트 앞에 (hello-uv)가 붙고, python으로 바로 실행돼요. 수업은 uv run을 기본으로 써요.", 900))
W("act", o, "uv가 만든 .venv도 예전 방식과 같은 가상환경이라 activate로 켤 수 있어요. 켜면 프롬프트 앞에 프로젝트 이름 (hello-uv)가 붙어요. which python으로 보면 .venv 안의 python을 쓰고 있어요. 켠 상태에서는 uv run 없이 python main.py로 실행해도 돼요. Mac은 python3, Windows는 python으로 부르던 차이도 켠 터미널에서는 python 하나로 같아요. Windows Git Bash는 bin 대신 Scripts 폴더예요. PowerShell에서 스크립트 실행이 막혔다는 오류가 나면 Git Bash에서 쳐요. 다 쓰면 deactivate로 꺼요. 켜는 걸 잊어도 uv run은 늘 동작하니 수업 실습은 uv run으로 적어요. 출력의 폴더 주소는 01처럼 /home/kim으로 바꿨어요.")

o = [sec("pyver")] + head(EB4, "파이썬 버전은 .python-version이 정해요", BL)
o += terminal([("$", "cd ~"), ("$", "uv init --python 3.13 hello-313"), ("o", "Initialized project `hello-313` at `/home/kim/hello-313`"), ("$", "cd hello-313"),
               ("$", "cat .python-version"), ("H", "3.13"), ("$", "uv run python --version"), ("o", "Downloading cpython-3.13.14-linux-x86_64-gnu (download) (33.2MiB)"),
               ("o", " Downloaded cpython-3.13.14-linux-x86_64-gnu (download)"), ("o", "Using CPython 3.13.14"), ("o", "Creating virtual environment at: .venv"), ("H", "Python 3.13.14")],
              size=(28, 23))
o.append(caption("버전을 정해서 만들려면 --python을 붙여요. 없는 버전은 uv가 받아요.", 900))
W("pyver", o, "보기만 해도 되는 장이에요. 수업 프로젝트는 uv init 이름으로 만들면 돼요. 회사나 강의에서 파이썬 버전을 정해 줄 때 --python 버전을 붙여요. 이 컴퓨터에 3.13이 없어서 uv가 받아 왔어요. 프로젝트마다 버전이 달라도 폴더에 들어가 uv run을 치면 그 폴더의 버전으로 실행돼요. 출력의 폴더 주소는 01처럼 /home/kim으로 바꿨어요.")

# ---------- part 5: uv add, uv tree, uv remove ----------
EB5 = "5. 패키지 넣고 빼기"
o = [sec("add", "magic")] + head(EB5, "uv add로 패키지를 넣어요", NAVY)
o += terminal([("$", "uv add " + ADD)] + ADD_OUT, w=900, size=(28, 22))
o += three({"py": ('"fastapi[standard]>=0.162.0",', "[standard]는 서버를 켜는 도구까지 함께", True), "lock": ("고른 1개와 따라온 58개", "pydantic 2.14.2, starlette 1.10.0 …", True),
            "venv": ("패키지 59개 설치", "uv run으로 실행하면 바로 써요", True)}, top=210)
o.append(f'<div data-build-in="rise order 4" style="position:absolute;left:96px;top:640px;width:900px;height:200px;background:{CARD};border:2px solid {LINE};border-left:12px solid {OR};border-radius:20px;padding:24px 32px;display:flex;flex-direction:column;gap:12px">'
         + p(f"font-size:30px;font-weight:700;color:{INK}", "큰따옴표까지 그대로 쳐요")
         + p(f"font-size:26px;line-height:1.45;color:{SUB}", "Mac 터미널(zsh)은 대괄호 [ ]를 특별한 글자로 읽어요.<br>따옴표로 감싸면 Mac, Windows 모두 같은 명령이에요.") + '</div>')
o.append(caption("명령 하나로 세 곳이 함께 바뀌어요.", 944))
W("add", o, "hello-uv 폴더에서 쳐요. fastapi[standard]는 fastapi에 서버를 켜는 도구까지 함께 넣으라는 뜻이에요. Mac 터미널(zsh)은 대괄호를 특별한 글자로 읽어서 큰따옴표로 감싸요. Windows에서도 같은 명령을 그대로 쳐요. uv add는 세 가지를 한 번에 해요. pyproject.toml의 dependencies 칸에 적고, uv.lock에 정확한 버전을 적고, .venv에 설치해요. 예전의 pip install과 pip freeze를 합친 일이에요. >=0.162.0은 0.162.0 이상이면 된다는 뜻이에요. 크기가 큰 패키지를 받는 Downloading 여섯 줄과 설치 목록 가운데 54줄은 뺐어요. 실제로 쓸 버전은 uv.lock이 정해요.", ("add", "패키지 넣고 빼기"))

o = [sec("tree")] + head(EB5, "하나를 넣었는데 59개가 들어왔어요", NAVY)
TREE = ["annotated-doc v0.0.5", "opentelemetry-api v1.45.2", "pydantic v2.14.2", "starlette v1.10.0", "typing-extensions v4.16.0", "typing-inspection v0.4.4",
        "email-validator v2.3.0 (extra: standard)", "fastapi-cli[standard] v0.0.32 (extra: standard)", "fastar v0.12.0 (extra: standard)", "httpx v0.28.1 (extra: standard)",
        "httpx2 v2.16.0 (extra: standard)", "jinja2 v3.1.6 (extra: standard)", "opentelemetry-exporter-otlp-proto-http v1.45.2 (extra: standard)",
        "opentelemetry-sdk v1.45.2 (extra: standard)", "pydantic-extra-types v2.11.1 (extra: standard)", "pydantic-settings v2.16.2 (extra: standard)",
        "python-multipart v0.0.32 (extra: standard)", "uvicorn[standard] v0.54.0 (extra: standard)"]
o += terminal([("$", "uv tree --depth 2"), ("o", "Resolved 62 packages in 1ms"), ("o", "hello-uv v0.1.0"), ("o", "└── fastapi[standard] v0.162.0")]
              + [("o", ("    └── " if i == len(TREE) - 1 else "    ├── ") + t) for i, t in enumerate(TREE)], w=1000, size=(22, 18))
o.append(f'<div data-build-in="pop order 1" style="position:absolute;left:1160px;top:210px;width:664px;height:90px;background:{NAVY};border-radius:20px;display:flex;align-items:center;justify-content:center">'
         + p(f"font-family:{MONO};font-size:32px;font-weight:700;color:#FFFFFF", "fastapi[standard]") + '</div>')
for i, n in enumerate(["pydantic", "starlette", "fastapi-cli", "httpx", "jinja2", "… 13개 더"]):
    y = 340 + i * 92
    o.append(f'<x-connector data-build-in="fade order 2" x1="1200" y1="300" x2="1200" y2="{y + 34}" style="color:#B9BFCB;border-width:4px"></x-connector>')
    o.append(f'<div data-build-in="fade order 2" style="position:absolute;left:1200px;top:{y + 32}px;width:40px;height:4px;background:#B9BFCB"></div>')
    o.append(f'<div data-build-in="pop order 2" style="position:absolute;left:1240px;top:{y}px;width:400px;height:68px;background:{CARD};border:3px solid #9DB8F2;border-radius:16px;display:flex;align-items:center;padding:0 20px">'
             + p(f"{'font-family:' + MONO + ';' if i < 5 else ''}font-size:26px;font-weight:700;white-space:nowrap;color:{INK}", e(n)) + '</div>')
o.append(caption("fastapi가 쓰는 패키지까지 uv가 함께 넣어요. 뺄 때도 함께 빠져요.", 944))
W("tree", o, "uv tree는 어떤 패키지가 어떤 패키지 때문에 들어왔는지 나무 모양으로 보여 줘요. 01에서 본 폴더 지도와 같은 모양이에요. --depth 2는 두 단계까지만 보여 달라는 뜻이에요. 빼고 치면 pydantic 아래 pydantic-core처럼 더 깊은 단계까지 나와서 화면이 길어져요. fastapi는 데이터 검사를 pydantic에, 웹 요청 처리를 starlette에 맡겨요. extra: standard가 붙은 줄은 [standard]를 붙여서 들어온 도구예요. fastapi-cli는 fastapi dev 명령을, uvicorn은 그 명령이 켜는 서버 엔진이에요. 코드에서 직접 부르지는 않아요. pyproject.toml에는 내가 고른 fastapi[standard] 하나만 적혀요.")

o = [sec("use")] + head(EB5, "넣은 패키지로 웹 서버를 켜요", NAVY)
o += code_card("c-main", "main.py", MAIN_REQ, 96, 200, 860, BL, 26, marks=(0, 2))
o.append(f'<div data-build-in="pop order 2" style="position:absolute;left:1000px;top:200px;width:824px;height:300px;background:{CARD};border:2px solid {LINE};border-radius:20px;overflow:hidden">'
         + '<div style="height:64px;background:#ECEAE3;display:flex;flex-direction:row;gap:12px;align-items:center;padding:0 22px">'
         + "".join(f'<div style="width:16px;height:16px;flex:none;border-radius:50%;background:{c}"></div>' for c in ("#E0857A", "#E8C068", "#7FC28F"))
         + p(f"flex:1;margin-left:12px;font-family:{MONO};font-size:24px;color:{INK};background:#FFFFFF;border-radius:10px;padding:4px 16px", "http://127.0.0.1:8000") + '</div>'
         + p(f"padding:40px 32px;font-family:{MONO};font-size:34px;font-weight:700;color:{INK}", e('{"message":"안녕하세요"}')) + '</div>')
o.append(p(f"position:absolute;left:1000px;top:520px;width:824px;font-size:26px;font-weight:700;color:{GRAY}", "브라우저 주소창에 http://127.0.0.1:8000", ' data-build-in="fade order 2"'))
o += terminal([("$", "uv run fastapi dev main.py")] + SERVER, top=630, size=(28, 22), attrs=' data-build-in="rise order 1"')
o.append(caption("서버는 Ctrl+C로 끌 때까지 켜져 있어요.", 944))
W("use", o, "main.py를 이 여덟 줄로 바꿔 저장해요. 첫 줄은 fastapi를 불러오고, app = FastAPI()가 웹 서버 앱을 만들어요. @app.get(\"/\")는 주소 / 로 들어오면 아래 home()의 대답을 돌려준다는 뜻이에요. 서버는 uv run fastapi dev main.py로 켜요. uv run 뒤에 파일 이름 대신 uv add로 들어온 fastapi 명령을 적은 거예요. dev는 개발용 모드라서 main.py를 고쳐 저장하면 서버가 알아서 다시 켜져요. Server started 줄이 보이면 브라우저로 http://127.0.0.1:8000을 열어요. 열 때마다 터미널에 GET / 200 OK 줄이 하나씩 생겨요. 서버는 켜진 채로 기다려서 프롬프트가 돌아오지 않아요. Ctrl+C로 꺼요. 코드 문법은 다음 수업부터 하나씩 배워요. 서버 출력의 빈 줄과 INFO 줄 몇 개는 뺐어요. GET 줄의 숫자는 실행할 때마다 달라요.")

o = [sec("remove", "magic")] + head(EB5, "uv remove로 패키지를 빼요", NAVY)
o += terminal([("$", "uv remove fastapi"), ("o", "Resolved 1 package in 2ms"), ("o", "Uninstalled 59 packages in 128ms")] + [("r", " - " + x) for x in PKGS[:4]]
              + [("#", "   ... 54줄 생략 ..."), ("r", " - " + PKGS[-1]), ("$", "uv run fastapi dev main.py"), ("r", "error: Failed to spawn: `fastapi`"),
                 ("r", "  Caused by: No such file or directory (os error 2)")], w=900, size=(28, 22))
o += three({"py": ("dependencies = []", "", True), "lock": ("프로젝트만 남아요", "따라왔던 58개도 지워요", True), "venv": ("패키지 59개 삭제", "딸린 패키지까지 같이 빠져요", True)}, top=210)
o.append(caption("뺄 때도 세 곳이 함께 바뀌어요. 예전 pip uninstall은 58개가 남았어요.", 944))
W("remove", o, "uv remove는 uv add를 거꾸로 해요. pyproject.toml에서 지우고, uv.lock과 .venv에서도 빼요. 뺄 때는 [standard] 없이 이름만 적어요. 함께 들어왔던 58개도 다른 패키지가 쓰지 않으면 같이 빠져요. fastapi 명령도 함께 지워져서 서버를 켜면 fastapi를 찾지 못한다는 오류가 나요. Caused by 줄은 운영체제마다 조금 달라요. 지운 목록 가운데 54줄은 뺐어요. 예전 방식으로 pip uninstall fastapi를 쳐 보면 fastapi 하나만 지워지고 58개가 남았어요. 다음 장에서 다시 넣어요.")

o = [sec("again")] + head(EB5, "다시 넣으면 바로 들어가요", NAVY)
o += terminal([("$", "uv add " + ADD), ("o", "Resolved 62 packages in 15ms"), ("H", "Installed 59 packages in 12ms")] + [("g", " + " + x) for x in PKGS[:4]]
              + [("#", "   ... 54줄 생략 ..."), ("g", " + " + PKGS[-1]), ("$", "uv run fastapi dev main.py"), ("o", " 🌐 Server started at http://127.0.0.1:8000")], w=900, size=(28, 22))
o.append(f'<div data-build-in="pop order 1" style="position:absolute;left:1060px;top:220px;width:764px;height:300px;background:{CARD};border:2px solid {LINE};border-top:10px solid {UV};border-radius:22px;padding:28px 34px;display:flex;flex-direction:column;gap:16px">'
         + '<div style="display:flex;flex-direction:row;gap:16px;align-items:center">' + f'<x-icon name="Database" style="width:48px;height:48px;color:{UV}"></x-icon>'
         + p(f"font-size:34px;font-weight:700;color:{UV}", "uv 캐시") + '</div>'
         + p(f"font-size:28px;line-height:1.45;color:{SUB}", "한 번 받은 패키지를 컴퓨터에 보관해요.<br>다른 프로젝트에서도 다시 받지 않아요.") + '</div>')
o.append(f'<div data-build-in="rise order 2" style="position:absolute;left:1060px;top:560px;width:764px;height:260px;background:#FDFCF9;border:2px dashed #B9BFCB;border-radius:22px;padding:28px 34px;display:flex;flex-direction:column;gap:14px">'
         + p(f"font-size:28px;font-weight:700;color:{GRAY}", "처음 넣을 때 있던 줄")
         + p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{INK}", "Prepared 59 packages in 418ms")
         + p(f"font-size:26px;color:{SUB}", "이번엔 받을 게 없어서 이 줄이 없어요.") + '</div>')
o.append(caption("uv가 빠른 이유 중 하나예요. 패키지 59개가 0.012초 만에 들어갔어요.", 944))
W("again", o, "앞에서 뺀 fastapi를 다시 넣었어요. 처음 넣을 때는 인터넷에서 받아 준비하는 Prepared 줄이 있었어요. 이번엔 캐시에 있어서 받지 않고 바로 설치했어요. 프로젝트를 여러 개 만들어도 같은 패키지는 한 번만 받아요. 다시 넣었으니 서버도 다시 켜져요. 설치 목록 가운데 54줄과 서버 출력의 나머지 줄은 뺐어요.")

# ---------- part 6: uv sync on another computer ----------
EB6 = "6. 다른 컴퓨터에서 그대로"
UP = [".gitignore", ".python-version", "README.md", "main.py", "pyproject.toml", "uv.lock"]
o = [sec("commit")] + head(EB6, "GitHub에는 무엇을 올리나요", PUR)
o += terminal([("$", "git status --short")] + [("r", "?? " + f) for f in UP] + [("$", "git add ."), ("$", 'git commit -m "feat: hello-uv 프로젝트 만들기"'),
              ("o", "[main (root-commit) 0cba23d] feat: hello-uv 프로젝트 만들기")], w=900, size=(26, 23))
o += folder([".gitignore", ".python-version", ".venv", "README.md", "main.py", "pyproject.toml", "uv.lock"], left=1040, w=784, off=(".venv",), notes=False, pre="u")
o.append(p(f"position:absolute;left:1500px;top:{200 + 76 + 2 * 70 + 14}px;width:300px;font-size:24px;font-weight:700;color:{RED}", ".gitignore가 막아요", ' data-build-in="fade order 1"'))
o.append(caption(".venv는 올리지 않아요. pyproject.toml과 uv.lock만 있으면 똑같이 다시 만들어요.", 900))
W("commit", o, "git status에 .venv가 없어요. uv init이 만든 .gitignore에 .venv가 적혀 있어서예요(04). .venv는 컴퓨터마다 다시 만들 수 있고 크기도 커서 올리지 않아요. 대신 pyproject.toml, uv.lock, .python-version을 꼭 같이 올려요. 이 세 파일이 다른 컴퓨터에서 같은 환경을 만드는 설명서예요. git add .는 지금 폴더의 바뀐 파일을 모두 올린다는 뜻이에요.", ("sync", "다른 컴퓨터에서 그대로"))

o = [sec("sync-flow")] + head(EB6, "lee 컴퓨터에서는 uv sync 한 번이면 돼요", PUR)
boxes = [("kim 컴퓨터", BL, [".venv", "pyproject.toml", "uv.lock"], "git push origin main"), ("GitHub", PUR, ["pyproject.toml", "uv.lock"], "git clone 주소"),
         ("lee 컴퓨터", GR, ["pyproject.toml", "uv.lock"], None)]
for i, (who, c, fs, act) in enumerate(boxes):
    x = 96 + i * 600
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:{x}px;top:240px;width:528px;height:520px;background:{CARD};border:3px solid {c};border-radius:26px;padding:28px 32px;display:flex;flex-direction:column;gap:16px">'
             + p(f"font-size:34px;font-weight:700;color:{c}", who)
             + "".join(chip(f, INK, 26, extra="align-self:flex-start;" + ("background:#E6F4EC;" if f == ".venv" else "")) for f in fs) + '</div>')
    if act:
        o.append(arrow(x + 536, 470, 56, 56, c, attrs=f' data-build-in="fade order {i + 2}"'))
        o.append(p(f"position:absolute;left:{x + 330}px;top:780px;width:470px;font-family:{MONO};font-size:24px;font-weight:700;text-align:center;color:{c}", e(act), f' data-build-in="fade order {i + 2}"'))
o.append(f'<div data-build-in="pop order 4" style="position:absolute;left:1328px;top:500px;width:464px;height:220px;background:#E6F4EC;border:3px dashed {GR};border-radius:20px;padding:20px 26px;display:flex;flex-direction:column;gap:10px">'
         + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{GR}", "$ uv sync") + p(f"font-size:26px;line-height:1.4;color:{INK}", "파이썬 받기, .venv 만들기,<br>패키지 59개 설치") + '</div>')
o.append(caption("uv.lock에 적힌 버전 그대로 설치돼서 kim과 lee의 환경이 같아요.", 900))
W("sync-flow", o, "06의 팀 레포처럼 kim이 프로젝트를 GitHub에 올리고 lee가 clone했어요. GitHub에는 .venv가 없으니 lee 컴퓨터에도 없어요. lee는 uv sync 한 번으로 .python-version의 파이썬을 받고, .venv를 만들고, uv.lock에 적힌 버전 그대로 패키지를 설치해요. 예전에는 venv 만들기, activate, pip install -r requirements.txt 세 단계였어요.")

o = [sec("sync-term")] + head(EB6, "lee 컴퓨터에서 실제로 쳐 보면", GR)
o += terminal([("$", "git clone https://github.com/kim/hello-uv.git"), ("o", "Cloning into 'hello-uv'..."), ("$", "cd hello-uv"), ("$", "uv sync"),
               ("o", "Downloading cpython-3.14.6-linux-x86_64-gnu (download) (34.3MiB)"), ("o", " Downloaded cpython-3.14.6-linux-x86_64-gnu (download)"),
               ("o", "Using CPython 3.14.6"), ("o", "Creating virtual environment at: .venv"), ("o", "Resolved 62 packages in 1ms"), ("o", "Prepared 59 packages in 421ms"),
               ("o", "Installed 59 packages in 19ms"), ("g", " + agent-detector==2.0.0  + annotated-doc==0.0.5  + annotated-types==0.8.0  …"), ("$", "uv run fastapi dev main.py"),
               ("H", " 🌐 Server started at http://127.0.0.1:8000")],
              size=(30, 24))
W("sync-term", o, "lee 컴퓨터에는 파이썬도 패키지도 없는 상태에서 시작했어요. uv sync가 파이썬 3.14.6을 받고, .venv를 만들고, 패키지 59개를 설치했어요. 버전은 kim 컴퓨터와 똑같아요. 설치 목록은 화면 폭 때문에 한 줄로 줄였고, 실제로는 59줄이에요. 큰 패키지를 받는 Downloading 여섯 줄, clone 출력의 done. 줄, 서버 출력의 나머지 줄은 뺐어요.")

o = [sec("sync-when")] + head(EB6, "uv sync는 이럴 때 쳐요", GR)
whens = [("Link", "clone한 직후", "git clone 주소", "cd 폴더", "uv sync"), ("Users", "pull로 uv.lock이 바뀐 뒤", "git pull origin main", "uv sync", ""),
         ("CheckCircle", "uv run도 먼저 맞춰요", "uv run main.py", "실행 전에 sync를 알아서 해요", "")]
for i, (ic, h, *cmds) in enumerate(whens):
    x = 96 + i * 588
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:{x}px;top:240px;width:552px;height:440px;background:{CARD};border:2px solid {LINE};border-top:10px solid {GR};border-radius:22px;padding:32px 34px;display:flex;flex-direction:column;gap:20px">'
             + num(i + 1, GR, 44) + p(f"font-size:36px;font-weight:700;line-height:1.3;color:{INK}", h)
             + "".join(p(f"{'font-family:' + MONO + ';' if c.startswith(('git', 'uv', 'cd')) else ''}font-size:{26 if c.startswith(('git', 'uv', 'cd')) else 27}px;font-weight:700;color:{INK if c.startswith(('git', 'uv', 'cd')) else SUB};background:{'#F1F0EC' if c.startswith(('git', 'uv', 'cd')) else 'transparent'};border-radius:10px;padding:8px 16px", e(c)) for c in cmds if c)
             + '</div>')
o.append(caption("팀원이 패키지를 넣고 push했으면, pull 뒤 uv sync로 내 .venv를 맞춰요.", 740))
W("sync-when", o, "1번은 다른 사람 프로젝트를 처음 받을 때예요. 2번은 팀원이 uv add로 패키지를 넣고 push한 경우예요. pull로 pyproject.toml과 uv.lock은 바뀌었지만 내 .venv에는 아직 그 패키지가 없어요. uv sync가 .venv를 uv.lock에 맞춰요. 3번은 uv run도 실행 전에 같은 일을 해서, sync를 잊어도 uv run이면 돌아간다는 뜻이에요. 그래도 처음 받을 땐 uv sync로 설치가 끝났는지 눈으로 확인해요.")

# ---------- part 7: Jupyter in VS Code ----------
EB8 = "7. VS Code에서 Jupyter 쓰기"
JP = "#B8560F"


def cell(i, code_lines, out, left, top, w, attrs=""):
    o = [f'<div{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;display:flex;flex-direction:column;gap:0">',
         f'<div style="display:flex;flex-direction:row;gap:14px;align-items:stretch">'
         + p(f"width:64px;flex:none;font-family:{MONO};font-size:20px;color:{GRAY};text-align:right;padding-top:14px", f"[{i}]")
         + f'<div style="flex:1;background:#FFFFFF;border:2px solid {LINE};border-left:6px solid {BL};border-radius:10px;padding:10px 18px;display:flex;flex-direction:column">'
         + "".join(p(f"font-family:{MONO};font-size:24px;line-height:1.4;white-space:pre;color:{INK}", e(c)) for c in code_lines) + '</div></div>']
    if out is not None:
        o.append(p(f"margin-left:78px;padding:8px 24px;font-family:{MONO};font-size:24px;line-height:1.4;white-space:pre;color:{INK}", e(out)))
    o.append('</div>')
    return o


o = [sec("jup-what")] + head(EB8, "노트북은 코드를 셀 단위로 실행해요", JP)
o.append(f'<div style="position:absolute;left:96px;top:220px;width:700px;height:600px;background:{CARD};border:2px solid {LINE};border-radius:22px;padding:28px 34px;display:flex;flex-direction:column;gap:18px">'
         + p(f"font-family:{MONO};font-size:30px;font-weight:700;color:{BL}", "main.py")
         + p(f"font-family:{MONO};font-size:24px;line-height:1.6;color:{INK};background:#F1F0EC;border-radius:12px;padding:16px 20px", "데이터 읽기<br>정리하기<br>그래프 그리기")
         + f'<x-shape kind="arrow-right" style="width:60px;height:40px;background:#C9CED8;transform:rotate(90deg);align-self:center"></x-shape>'
         + p(f"font-size:28px;line-height:1.5;color:{SUB}", "처음부터 끝까지 한 번에 실행해요.<br>결과는 터미널에 모여서 나와요.") + '</div>')
o += cell(1, ["데이터 읽기"], "표 5줄", 860, 230, 960, ' data-build-in="rise order 1"')
o += cell(2, ["정리하기"], "빈칸 3개 지움", 860, 420, 960, ' data-build-in="rise order 2"')
o += cell(3, ["그래프 그리기"], "그래프 그림", 860, 610, 960, ' data-build-in="rise order 3"')
o.append(p(f"position:absolute;left:938px;top:180px;width:880px;font-family:{MONO};font-size:26px;font-weight:700;color:{JP}", "notebook.ipynb"))
o.append(caption("셀 하나씩 실행하고 결과를 바로 아래에서 봐요. 머신러닝 수업에서 데이터를 조금씩 확인할 때 써요.", 900))
W("jup-what", o, "Jupyter 노트북은 확장자가 .ipynb인 파일이에요. 코드를 셀이라는 칸으로 나누고, 셀마다 따로 실행해요. 실행 결과는 그 셀 바로 아래에 남아요. 앞 셀에서 만든 값은 뒤 셀에서 그대로 써요. 그래서 데이터를 읽고 모양을 보고, 고치고 다시 보는 머신러닝 실습에 잘 맞아요. VS Code 안에서 노트북을 열 수 있어서 따로 프로그램을 설치하지 않아요. 그림 속 셀 내용은 예시예요.", ("jupyter", "VS Code에서 Jupyter 쓰기"))

o = [sec("jup-ext")] + head(EB8, "VS Code에 확장 두 개를 설치해요", JP)
o.append(f'<div style="position:absolute;left:96px;top:220px;width:1000px;height:640px;background:#1F2430;border-radius:22px;overflow:hidden;display:flex;flex-direction:row">'
         + f'<div style="width:90px;flex:none;background:#181C25;display:flex;flex-direction:column;align-items:center;gap:30px;padding-top:30px">'
         + "".join(f'<div style="width:40px;height:40px;border-radius:8px;background:{c}"></div>' for c in ("#3A4150", "#3A4150", "#3A4150", "#3A4150"))
         + f'<div style="width:52px;height:52px;border-radius:10px;border:3px solid #F2C46D;display:flex;align-items:center;justify-content:center"><x-icon name="Archive" style="width:30px;height:30px;color:#F2C46D"></x-icon></div></div>'
         + '<div style="flex:1;padding:26px 30px;display:flex;flex-direction:column;gap:18px">'
         + p("font-size:22px;font-weight:700;letter-spacing:1px;color:#AEB6C4", "EXTENSIONS")
         + p(f"font-family:{MONO};font-size:24px;color:#E6E9EF;background:#2B3140;border:2px solid #4A90E2;border-radius:8px;padding:8px 16px", "Jupyter")
         + "".join(f'<div data-build-in="rise order {i + 2}" style="display:flex;flex-direction:row;gap:20px;align-items:center;background:#262C39;border-radius:12px;padding:18px 20px">'
                   + f'<div style="width:64px;height:64px;flex:none;border-radius:12px;background:{c}"></div>'
                   + '<div style="flex:1;display:flex;flex-direction:column;gap:4px">' + p("font-size:28px;font-weight:700;color:#FFFFFF", n) + p("font-size:22px;color:#AEB6C4", "Microsoft") + '</div>'
                   + p("font-size:22px;font-weight:700;color:#FFFFFF;background:#2F7D32;border-radius:6px;padding:6px 18px", "Install") + '</div>'
                   for i, (n, c) in enumerate([("Python", "#3A6FB0"), ("Jupyter", JP)]))
         + '</div></div>')
steps = [("왼쪽 확장 아이콘을 눌러요", "Mac Cmd+Shift+X, Windows Ctrl+Shift+X"), ("Python을 검색해 설치해요", "만든 곳이 Microsoft인지 봐요"), ("Jupyter를 검색해 설치해요", "같이 깔리는 확장은 그대로 둬요")]
for i, (a_, b_) in enumerate(steps):
    y = 230 + i * 210
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:1140px;top:{y}px;width:684px;height:186px;background:{CARD};border:2px solid {LINE};border-radius:20px;padding:24px 28px;display:flex;flex-direction:row;gap:22px;align-items:center">'
             + num(i + 1, JP, 44) + '<div style="flex:1;display:flex;flex-direction:column;gap:10px">' + p(f"font-size:30px;font-weight:700;color:{INK}", a_) + p(f"font-size:24px;color:{SUB}", b_) + '</div></div>')
o.append(caption("컴퓨터마다 한 번만 설치해요. 설치한 뒤에는 VS Code를 다시 열어요.", 900))
W("jup-ext", o, "확장은 VS Code에 기능을 더하는 프로그램이에요. 05에서 Git Graph를 설치한 것과 같은 화면이에요. Python 확장은 파이썬 코드를 읽고 실행하는 기능, Jupyter 확장은 .ipynb 노트북을 여는 기능이에요. 둘 다 만든 곳이 Microsoft인 것을 골라요. 이름이 비슷한 다른 확장이 많아요. Python을 설치하면 Pylance 같은 확장이 함께 깔려요. 그대로 둬요. 왼쪽 그림은 화면을 단순하게 그린 거예요.")

o = [sec("jup-kernel")] + head(EB8, "uv add --dev ipykernel로 커널을 넣어요", JP)
o += terminal([("$", "cd ~/hello-uv"), ("$", "uv add --dev ipykernel"), ("o", "Resolved 93 packages in 219ms"), ("#", "  ... Downloading 줄 생략 ..."), ("o", "Prepared 28 packages in 820ms"),
               ("H", "Installed 28 packages in 56ms"), ("g", " + asttokens==3.0.2"), ("g", " + comm==0.2.3"), ("#", "   ... 25줄 생략 ..."), ("g", " + wcwidth==0.9.4")], w=860, size=(28, 24))
o += code_card("c-py", "pyproject.toml", ["dependencies = [", '    "fastapi[standard]>=0.162.0",', "]", "", "[dependency-groups]", "dev = [", '    "ipykernel>=7.4.0",', "]"],
               1000, 210, 824, F_PY, 24, marks=(4, 5, 6, 7), attrs=' data-build-in="rise order 1"')
o.append(f'<div data-build-in="rise order 2" style="position:absolute;left:1000px;top:630px;width:824px;height:170px;background:{CARD};border:2px solid {LINE};border-left:12px solid {JP};border-radius:20px;padding:20px 28px;display:flex;flex-direction:column;gap:10px">'
         + p(f"font-size:28px;font-weight:700;color:{INK}", "커널 = 노트북 셀을 실행하는 파이썬")
         + p(f"font-size:24px;line-height:1.45;color:{SUB}", "--dev는 개발할 때만 쓰는 도구라는 표시예요.<br>서버를 켜는 데는 필요 없어서 따로 적혀요.") + '</div>')
o.append(caption("노트북도 .venv 안의 파이썬으로 실행해요. 그래서 ipykernel을 .venv에 넣어요.", 920))
W("jup-kernel", o, "노트북의 셀은 커널이라는 파이썬 프로그램이 실행해요. VS Code가 hello-uv의 .venv를 커널로 쓰려면 .venv 안에 ipykernel 패키지가 있어야 해요. --dev를 붙이면 pyproject.toml의 dependencies가 아니라 dependency-groups의 dev 칸에 적혀요. 서버를 켜는 데 꼭 필요한 패키지와, 내가 개발할 때만 쓰는 도구를 나눠 두는 거예요. uv sync는 dev 칸도 함께 설치해서, lee 컴퓨터에서도 uv sync 한 번이면 노트북을 열 수 있어요. 받는 줄과 설치 목록 가운데는 뺐어요. 실제로는 28개가 설치돼요.")

o = [sec("jup-pick")] + head(EB8, "노트북을 만들고 커널로 .venv를 골라요", JP)
picks = [("File > Open Folder로 hello-uv 열기", "폴더 자체를 열어요"), ("왼쪽 탐색기에서 새 파일 notebook.ipynb", "이름 끝이 .ipynb면 노트북으로 열려요"),
         ("오른쪽 위 Select Kernel 누르기", ""), ("Python Environments 고르기", ""), (".venv (Python 3.14.6) 고르기", "hello-uv 안의 .venv예요")]
for i, (a_, b_) in enumerate(picks):
    y = 210 + i * 132
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:96px;top:{y}px;width:860px;height:116px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:0 26px;display:flex;flex-direction:row;gap:22px;align-items:center">'
             + num(i + 1, JP, 40) + '<div style="flex:1;display:flex;flex-direction:column;gap:4px">' + p(f"font-size:28px;font-weight:700;color:{INK}", e(a_))
             + (p(f"font-size:22px;color:{SUB}", e(b_)) if b_ else "") + '</div></div>')
o.append(f'<div style="position:absolute;left:1000px;top:210px;width:824px;height:470px;background:#1F2430;border-radius:22px;overflow:hidden;display:flex;flex-direction:column">'
         + '<div style="height:70px;background:#181C25;display:flex;flex-direction:row;align-items:center;padding:0 24px;gap:16px">'
         + p(f"flex:1;font-family:{MONO};font-size:22px;color:#AEB6C4", "notebook.ipynb")
         + p("font-size:22px;font-weight:700;color:#FFFFFF;border:2px solid #F2C46D;border-radius:8px;padding:4px 14px", "Select Kernel") + '</div>'
         + f'<div data-build-in="pop order 4" style="margin:24px;background:#2B3140;border:2px solid #4A90E2;border-radius:12px;padding:16px;display:flex;flex-direction:column;gap:10px">'
         + p("font-size:22px;color:#AEB6C4", "Select Another Kernel")
         + p("font-size:26px;font-weight:700;color:#FFFFFF;background:#36507A;border-radius:8px;padding:10px 16px", "Python Environments...")
         + p("font-size:26px;color:#C9CED8;padding:10px 16px", "Existing Jupyter Server...") + '</div>'
         + f'<div data-build-in="pop order 5" style="margin:0 24px;background:#2B3140;border:2px solid #4A90E2;border-radius:12px;padding:16px;display:flex;flex-direction:column;gap:8px">'
         + '<div style="background:#36507A;border-radius:8px;padding:10px 16px;display:flex;flex-direction:column;gap:4px">'
         + p("font-size:26px;font-weight:700;color:#FFFFFF", "★ .venv (Python 3.14.6)") + p(f"font-family:{MONO};font-size:20px;color:#AEB6C4", ".venv/bin/python") + '</div>'
         + p("font-size:24px;color:#8C95A6;padding:6px 16px", "다른 파이썬은 고르지 않아요") + '</div></div>')
o.append(caption("커널을 한 번 고르면 이 노트북을 열 때마다 기억해요.", 900))
W("jup-pick", o, "VS Code는 열린 폴더 안의 .venv를 찾아서 목록 맨 위에 별표(Recommended)로 보여 줘요. 그래서 hello-uv의 부모 폴더가 아니라 hello-uv 폴더 자체를 열어요. Mac 메뉴에 Open Folder가 없으면 File > Open...으로 폴더를 골라요. Windows는 경로가 .venv\\Scripts\\python.exe로 보여요. 컴퓨터에 다른 파이썬이 있으면 목록에 여러 줄이 나오는데, 꼭 .venv를 골라요. VS Code 버전에 따라 글자가 조금 다를 수 있어요. 오른쪽 그림은 화면을 단순하게 그린 거예요.")

o = [sec("jup-run")] + head(EB8, "Shift+Enter로 셀을 실행해요", JP)
o.append(f'<div style="position:absolute;left:96px;top:210px;width:1728px;height:66px;background:#ECEAE3;border-radius:14px;display:flex;flex-direction:row;align-items:center;padding:0 24px;gap:16px">'
         + p(f"flex:1;font-family:{MONO};font-size:24px;font-weight:700;color:{INK}", "notebook.ipynb")
         + p(f"font-size:22px;font-weight:700;color:{GR};background:#E6F4EC;border-radius:8px;padding:4px 14px", ".venv (Python 3.14.6)") + '</div>')
o += cell(1, ['print("안녕하세요")'], "안녕하세요", 96, 300, 1728, ' data-build-in="rise order 1"')
o += cell(2, ["import sys", "print(sys.executable)"], "/home/kim/hello-uv/.venv/bin/python", 96, 440, 1728, ' data-build-in="rise order 2"')
o += cell(3, ["import fastapi", "print(fastapi.__version__)"], "0.162.0", 96, 620, 1728, ' data-build-in="rise order 3"')
o += cell(4, ["1 + 2"], "3", 96, 800, 1728, ' data-build-in="rise order 4"')
o.append(caption("2번 셀에 .venv가 보이면 커널을 잘 고른 거예요. uv add로 넣은 패키지도 바로 써요.", 950))
W("jup-run", o, "셀을 누르고 Shift+Enter를 치면 실행하고 다음 셀로 넘어가요. 셀 왼쪽의 실행 버튼을 눌러도 돼요. 2번 셀은 지금 커널이 어느 파이썬인지 보여 줘요. hello-uv/.venv 안이면 맞게 고른 거예요. 3번 셀처럼 uv add로 넣은 fastapi도 노트북에서 바로 불러와요. 4번 셀처럼 셀 마지막 줄이 값이면 print 없이도 그 값을 보여 줘요. 출력은 tools/demo.sh에서 hello-uv의 커널로 같은 셀을 실행한 결과예요. 폴더 주소만 01처럼 /home/kim으로 바꿨어요.")

o = [sec("jup-trouble")] + head(EB8, "노트북에서 막히면", JP)
jt = [("ipykernel을 설치하라는 알림이 떠요", "알림의 Install은 pip로 넣어서 pyproject.toml에 안 적혀요", "uv add --dev ipykernel"),
      ("커널 목록에 .venv가 없어요", "hello-uv 폴더 자체를 열었는지 봐요. 그다음 VS Code 다시 열기", "uv sync"),
      ("셀에서 ModuleNotFoundError", "커널이 .venv가 아니에요. 오른쪽 위 커널 이름을 눌러 바꿔요", ".venv (Python 3.14.6)")]
o.append('<div style="position:absolute;left:96px;top:220px;width:1728px;height:660px;display:flex;flex-direction:column;gap:20px">')
for i, (q, a_, cmd) in enumerate(jt, 1):
    o.append(f'<div data-build-in="rise order {i}" style="flex:1;display:flex;flex-direction:row;gap:28px;align-items:center;background:{CARD};border:2px solid {LINE};border-radius:20px;padding:12px 32px">'
             + num(i, JP, 44)
             + '<div style="flex:1;display:flex;flex-direction:column;gap:8px">' + p(f"font-size:30px;font-weight:700;color:{INK}", e(q)) + p(f"font-size:25px;color:{SUB}", e(a_)) + '</div>'
             + p(f"width:460px;flex:none;font-family:{MONO};font-size:26px;font-weight:700;line-height:1.5;color:{INK};background:#EEEFF2;padding:12px 20px;border-radius:12px", e(cmd)) + '</div>')
o.append('</div>')
W("jup-trouble", o, "1번은 ipykernel 없이 셀을 실행하면 VS Code가 띄우는 알림이에요. Install 버튼은 pip로 설치해서 pyproject.toml과 uv.lock에 적히지 않아요. 알림을 닫고 터미널에서 uv add --dev ipykernel을 쳐요. 그다음 커널을 다시 골라요. 2번은 VS Code로 hello-uv의 부모 폴더를 열었거나, clone 뒤 uv sync를 안 해서 .venv가 없을 때 나요. 3번은 컴퓨터에 원래 있던 파이썬을 커널로 고른 경우예요. 2번 셀 출력으로 어느 파이썬인지 확인해요.")

# ---------- summary ----------
EB7 = "정리"
o = [sec("map")] + head(EB7, "예전 명령은 이렇게 바뀌었어요", INK)
pairs = [("python.org에서 설치", "없으면 uv가 받아요"), ("python3 -m venv .venv", "uv run, uv sync가 만들어요"), ("source .venv/bin/activate", "uv run이 대신해요. 켜도 돼요"),
         ("pip install fastapi", "uv add fastapi"), ("pip uninstall fastapi", "uv remove fastapi"), ("pip install -r requirements.txt", "uv sync"), ("python main.py", "uv run main.py")]
for i, (a_, b_) in enumerate(pairs):
    y = 210 + i * 104
    mo = not a_.startswith("python.org")
    mn = b_.startswith("uv ") and " " not in b_[3:].replace(" fastapi", "").replace(" main.py", "")
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:96px;top:{y}px;width:1728px;height:88px;display:flex;flex-direction:row;gap:28px;align-items:center">'
             + p(f"width:760px;flex:none;{'font-family:' + MONO + ';' if mo else ''}font-size:28px;font-weight:700;color:#8A6A33;background:#FBEFD9;border-radius:12px;padding:16px 24px", e(a_))
             + f'<x-shape kind="arrow-right" style="width:70px;height:40px;background:{UV}"></x-shape>'
             + p(f"flex:1;{'font-family:' + MONO + ';' if mn else ''}font-size:30px;font-weight:700;color:{UV};background:#E3F3F4;border-radius:12px;padding:14px 24px", e(b_)) + '</div>')
W("map", o, "인터넷 자료나 옛 강의에 왼쪽 명령이 나오면 오른쪽으로 바꿔 쳐요. 특히 pip install 패키지는 uv add 패키지로 바꿔요. pip로 넣으면 pyproject.toml과 uv.lock에 적히지 않아서 다른 컴퓨터에서 uv sync로 받을 수 없어요.", ("trouble", "정리"))

o = [sec("trouble")] + head(EB7, "이런 메시지가 나와요", NAVY)
cases = [("bash: uv: command not found", "설치 뒤 터미널을 새로 열지 않았어요", "터미널 닫고 다시 열기"),
         ("error: No `pyproject.toml` found in current directory or any parent directory", "프로젝트 폴더 밖에서 쳤어요", "cd hello-uv"),
         ("ModuleNotFoundError: No module named 'fastapi'", "패키지를 안 넣었거나 python3로 실행했어요", "uv add \"fastapi[standard]\"\nuv run main.py"),
         ("error: Project is already initialized in `...`", "이미 만든 프로젝트 안에서 uv init을 쳤어요", "uv init은 처음 한 번만")]
o.append('<div style="position:absolute;left:96px;top:220px;width:1728px;height:780px;display:flex;flex-direction:column;gap:18px">')
for i, (q, a_, cmd) in enumerate(cases, 1):
    mono = cmd.startswith(("uv add", "cd "))
    o.append(f'<div data-build-in="rise order {i}" style="flex:1;display:flex;flex-direction:row;gap:28px;align-items:center;background:{CARD};border:2px solid {LINE};border-radius:20px;padding:12px 32px">'
             + num(i, NAVY, 44)
             + '<div style="flex:1;display:flex;flex-direction:column;gap:8px">' + p(f"font-family:{MONO};font-size:21px;font-weight:700;color:{INK}", e(q)) + p(f"font-size:26px;color:{SUB}", e(a_)) + '</div>'
             + p(f"width:470px;flex:none;white-space:nowrap;{'font-family:' + MONO + ';' if mono else ''}font-size:26px;font-weight:700;line-height:1.5;color:{INK};background:#EEEFF2;padding:12px 20px;border-radius:12px", e(cmd).replace("\n", "<br>")) + '</div>')
o.append('</div>')
W("trouble", o, "1번은 설치 직후에 가장 많이 나요. Mac 기본 터미널은 zsh라서 zsh: command not found: uv로 보여요. 2번은 홈 폴더처럼 pyproject.toml이 없는 곳에서 uv add를 친 경우예요. pwd로 위치를 보고 프로젝트 폴더로 cd 해요. 3번은 가상환경을 켜지 않고 python3 main.py로 실행했거나, uv add를 안 한 경우예요. 서버는 uv run fastapi dev main.py로 켜요. 4번은 폴더 주소가 들어간 메시지예요. 이미 pyproject.toml이 있어서 다시 만들 필요가 없어요.")

o = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>']
cheat = [("uv init 이름", "프로젝트 폴더 만들기", "Star", BL), ("uv run main.py", "가상환경에서 실행", "PaperPlane", BL), ("uv add 패키지", "패키지 넣기", "Archive", NAVY),
         ("uv remove 패키지", "패키지 빼기", "Archive", NAVY), ("uv sync", "uv.lock대로 맞추기", "Users", GR), ("uv tree", "패키지 관계 보기", "Search", GRAY)]
for i, (cmd, d, ic, c) in enumerate(cheat):
    x, y = 96 + (i % 3) * 584, 200 + (i // 3) * 290
    o.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:560px;height:264px;background:{CARD};border:2px solid {LINE};border-top:10px solid {c};border-radius:20px;padding:28px 32px;display:flex;flex-direction:column;gap:18px">'
             + f'<x-icon name="{ic}" style="width:44px;height:44px;color:{c}"></x-icon>'
             + p(f"font-family:{MONO};font-size:34px;font-weight:700;color:{INK}", e(cmd)) + p(f"font-size:30px;color:{SUB}", d) + '</div>')
o.append(f'<div style="position:absolute;left:96px;top:780px;width:1728px;height:210px;background:{CARD};border:2px solid {LINE};border-radius:20px;padding:24px 36px;display:flex;flex-direction:column;justify-content:center;gap:12px">'
         + p(f"font-size:30px;font-weight:700;color:{INK}", 'GitHub에 올려요 <span style="font-family:\'JetBrains Mono\';color:' + GR + '">pyproject.toml  uv.lock  .python-version</span>')
         + p(f"font-size:30px;font-weight:700;color:{INK}", '올리지 않아요 <span style="font-family:\'JetBrains Mono\';color:' + RED + '">.venv</span>  <span style="font-weight:400;color:' + SUB + '">uv init이 .gitignore에 적어 둬요</span>')
         + p(f"font-size:30px;font-weight:700;color:{INK}", '노트북 <span style="font-family:\'JetBrains Mono\';color:' + JP + '">uv add --dev ipykernel</span>  <span style="font-weight:400;color:' + SUB + '">뒤 커널로 .venv 고르기</span>') + '</div>')
W("cheatsheet", o, "파이썬 프로젝트에서 치는 명령은 거의 이 여섯 개예요. 새 프로젝트는 uv init, 실행은 uv run, 패키지는 uv add와 uv remove, 받은 프로젝트는 uv sync예요. pip install이 보이면 uv add로 바꿔 쳐요.")

# ---------- toc (page numbers from ORDER) ----------
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
parts = [("Code", BL, "파이썬은 어떻게 실행되나", "python, 패키지", "run", "pkg"),
         ("Archive", OLD, "예전 방식과 비교", "venv, pip와 uv", "old-venv", "why"),
         ("Star", UV, "uv 설치하기", "brew, winget", "install", "install"),
         ("Tool", BL, "프로젝트 만들고 실행하기", "uv init, uv run, 가상환경 켜기", "init", "pyver"),
         ("Database", NAVY, "패키지 넣고 빼기", "uv add, uv tree, uv remove", "add", "again"),
         ("Users", GR, "다른 컴퓨터에서 그대로", "GitHub, uv sync", "commit", "sync-when"),
         ("Book", "#B8560F", "VS Code에서 Jupyter 쓰기", "확장 설치, ipykernel, 커널 고르기", "jup-what", "jup-trouble")]
t = [f'<section id="toc" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};padding:96px 128px;display:flex;flex-direction:column;gap:40px">',
     f'<h2 style="font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>',
     '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:24px;flex:1">']
for i, (ic, c, h, s, a, b) in enumerate(parts, 1):
    pg = f"{page[a]}–{page[b]}쪽" if a != b else f"{page[a]}쪽"
    t.append(f'<div style="display:flex;flex-direction:column;gap:10px;background:#FFFFFF;border:2px solid {LINE};border-top:10px solid {c};border-radius:20px;padding:24px 28px">'
             f'<div style="display:flex;flex-direction:row;gap:14px;align-items:center"><p style="font-size:48px;font-weight:900;line-height:1.25;color:{c}">{i}</p>'
             f'<x-icon name="{ic}" style="width:40px;height:40px;color:{c}"></x-icon></div>'
             f'<h3 style="font-size:27px;font-weight:700;color:{INK}">{h}</h3>'
             f'<p style="font-size:26px;line-height:1.4;color:{SUB}">{e(s)}</p><div style="flex:1"></div>'
             f'<p style="font-size:24px;color:#6A7180">{pg}</p></div>')
t += ['</div>', f'<p style="font-size:26px;color:{SUB}">{page["map"]}–{page["cheatsheet"]}쪽은 명령 바꿔 치기, 막힐 때, 한 장 요약이에요.</p>']
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(t) + f"\n<aside>{e('1, 2파트는 눈으로만 보는 배경이에요. 3파트에서 uv를 설치하고, 4파트부터 직접 따라 쳐요. 4파트에서 만든 hello-uv 폴더를 5, 6, 7파트에서 계속 써요.')}</aside>\n</section>\n")

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-10-30T02:00:00Z"}, "lists": "css", "title": "uv로 파이썬 시작하기", "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
print(len(ORDER), "slides")
