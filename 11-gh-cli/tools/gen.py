"""Generates every slide of the gh CLI deck and slides/deck.json.

Story: kim installs gh, logs in with the browser code, clones team-intro (from 06),
makes a new repo my-notes from a local folder, fails to delete it until the delete_repo
scope is added with gh auth refresh, and ends with issue and PR commands on team-intro.
Terminal output comes from tools/demo.sh (gh 2.89.0 and git 2.43 run for real against
tools/mock_github.py, a small stand-in for github.com). The saved run is tools/demo-output.txt.
Usage: python3 tools/gen.py slides
"""
import html, json, os, re, sys

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
INK, SUB, LINE, CARD = "#1D2330", "#4A5262", "#E1DED6", "#FFFFFF"
BL, GR, OR, PUR, RED, NAVY, TEAL, GRAY = "#2459C9", "#1F8A4C", "#B26A00", "#5A3BB8", "#A33131", "#1E3F8F", "#0F7C86", "#6A7180"
T_BG, T_PROMPT, T_CMD, T_OUT, T_ERR, T_OK, T_DIM = "#1B2029", "#8FB3FF", "#F2C46D", "#D8DEE9", "#FF9C94", "#7FD18B", "#8A93A3"
GH = PUR   # GitHub color in every deck


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


def card(title, body, left, top, w, h, color, attrs="", tsize=30, bsize=24, mono_title=False):
    return box(p(f"font-size:{tsize}px;font-weight:700;color:{INK};{'font-family:' + MONO + ';' if mono_title else ''}", title)
               + p(f"font-size:{bsize}px;line-height:1.5;color:{SUB}", body), left, top, w, h, attrs, top_color=color)


def arrow(left, top, w=48, h=40, color="#C9CED8", attrs=""):
    return f'<x-shape kind="arrow-right"{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:{color}"></x-shape>'


# ---------- terminal ----------
def tline(l, size):
    kind = l[0]
    st = f"font-size:{size}px;line-height:1.45;white-space:pre;"
    if kind == "$":
        return p(st + f"color:{T_CMD}", f'<span style="color:{T_PROMPT}">{e(l[1])} $</span> {e(l[2])}')
    if kind == "m":
        t = l[1].replace("\t", "    ")
        tag = (f'<span style="display:inline-block;width:{size + 6}px;height:{size + 6}px;border-radius:50%;background:{l[3]};color:#FFFFFF;font-family:{SANS};font-size:{size * 0.7:.0f}px;font-weight:900;line-height:{size + 6}px;text-align:center;margin-left:14px">{l[2]}</span>') if l[2] else ""
        return p(st + f"color:{T_OUT};background:rgba(242,196,109,.16);border-radius:6px;margin:0 -10px;padding:0 10px", e(t) + tag)
    if kind == "sel":    # current choice in an arrow-key list
        return p(st + f"color:{T_OK};font-weight:700", e(l[1]))
    col = {"o": T_OUT, "e": T_ERR, "g": T_OK, "d": T_DIM, "y": T_CMD}[kind]
    t = l[1].replace("\t", "    ")
    return p(st + f"color:{col}", e(t) if t else "&#160;")


def term(lines, left, top, w, h, tid="term", size=24, attrs="", title=None):
    o = [f'<div id="{tid}"{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:{T_BG};border-radius:20px;padding:20px 28px;display:flex;flex-direction:column;gap:2px;font-family:{MONO};overflow:hidden">',
         '<div style="display:flex;flex-direction:row;gap:10px;align-items:center;padding:0 0 12px 0">'
         '<div style="width:16px;height:16px;border-radius:8px;background:#F28B82"></div><div style="width:16px;height:16px;border-radius:8px;background:#F2C46D"></div><div style="width:16px;height:16px;border-radius:8px;background:#7FD18B"></div>'
         + (p(f"margin-left:14px;font-family:{SANS};font-size:20px;font-weight:700;color:{T_DIM}", e(title)) if title else "") + '</div>']
    o += [tline(l, size) for l in lines]
    o.append('</div>')
    return "".join(o)


def label(text, left, top, w, color, attrs=""):
    return p(f"position:absolute;left:{left}px;top:{top}px;width:{w}px;font-size:26px;font-weight:700;color:{color}", text, attrs)


# ---------- browser window (simplified GitHub page) ----------
def browser(url, inner, left, top, w, h, bid="browser", attrs=""):
    return (f'<div id="{bid}"{attrs} style="position:absolute;left:{left}px;top:{top}px;width:{w}px;height:{h}px;background:{CARD};border:2px solid #D9D5CB;border-radius:20px;display:flex;flex-direction:column;overflow:hidden">'
            f'<div style="height:64px;flex:none;background:#ECEAE3;display:flex;flex-direction:row;align-items:center;gap:10px;padding:0 20px">'
            '<div style="width:14px;height:14px;border-radius:7px;background:#C9CED8"></div><div style="width:14px;height:14px;border-radius:7px;background:#C9CED8"></div><div style="width:14px;height:14px;border-radius:7px;background:#C9CED8"></div>'
            + p(f"flex:1;margin-left:12px;font-family:{MONO};font-size:20px;font-weight:700;color:{INK};background:#FFFFFF;border-radius:10px;padding:5px 14px;white-space:nowrap;overflow:hidden", e(url))
            + '</div>'
            f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:22px;padding:24px">{inner}</div></div>')


def gh_button(text, color=GR):
    return p(f"font-size:24px;font-weight:700;color:#FFFFFF;background:{color};border-radius:10px;padding:10px 34px", e(text))


def code_boxes(codestr, size=40):
    cells = []
    for ch in codestr:
        if ch == "-":
            cells.append(p(f"font-family:{MONO};font-size:{size}px;font-weight:700;color:{GRAY}", "-"))
        else:
            cells.append(p(f"width:{size + 12}px;height:{size + 26}px;border:2px solid #B4B9C3;border-radius:8px;font-family:{MONO};font-size:{size}px;font-weight:700;line-height:{size + 22}px;text-align:center;color:{INK}", e(ch)))
    return '<div style="display:flex;flex-direction:row;gap:8px;align-items:center">' + "".join(cells) + '</div>'


# ---------- real output (tools/demo-output.txt) ----------
CODE = "8F2A-71C4"
VERSION = ["gh version 2.89.0 (2026-03-26)", "https://github.com/cli/cli/releases/tag/v2.89.0"]
NOT_LOGGED = "You are not logged into any GitHub hosts. To log in, run: gh auth login"
Q_WHERE = "? Where do you use GitHub? GitHub.com"
Q_PROTO = "? What is your preferred protocol for Git operations on this host? HTTPS"
Q_GIT = "? Authenticate Git with your GitHub credentials? Yes"
Q_HOW = "? How would you like to authenticate GitHub CLI? Login with a web browser"
DEVICE = ["! First copy your one-time code: " + CODE, "Press Enter to open https://github.com/login/device in your browser..."]
LOGIN_TAIL = ["✓ Authentication complete.", "- gh config set -h github.com git_protocol https", "✓ Configured git protocol",
              "! Authentication credentials saved in plain text", "✓ Logged in as kim"]
STATUS = ["github.com", "  ✓ Logged in to github.com account kim (/home/kim/.config/gh/hosts.yml)", "  - Active account: true",
          "  - Git operations protocol: https", "  - Token: gho_*********"]
SCOPES = "  - Token scopes: 'gist', 'read:org', 'repo', 'workflow'"
SCOPES_DEL = "  - Token scopes: 'delete_repo', 'gist', 'read:org', 'repo', 'workflow'"
CLONE = ["Cloning into 'team-intro'...", "remote: Enumerating objects: 6, done.", "remote: Counting objects: 100% (6/6), done.",
         "remote: Compressing objects: 100% (3/3), done.", "remote: Total 6 (delta 0), reused 0 (delta 0), pack-reused 0",
         "Unpacking objects: 100% (6/6), 510 bytes | 510.00 KiB/s, done."]
REMOTE_TI = ["origin\thttps://github.com/kim/team-intro.git (fetch)", "origin\thttps://github.com/kim/team-intro.git (push)"]
LOG_TI = ["1baff03 (HEAD -> main, origin/main, origin/HEAD) feat: kim 소개 추가", "a2a187e docs: README 추가"]
VIEW = ["kim/team-intro", "No description provided", "", "", "  # team-intro", "", "  우리 팀 소개 페이지예요.", "", "",
        "View this repository on GitHub: https://github.com/kim/team-intro"]
BROWSE = "Opening https://github.com/kim/team-intro in your browser."
LIST2 = ["", "Showing 2 of 2 repositories in @kim", "", "NAME            DESCRIPTION  INFO    UPDATED",
         "kim/hello-git                public  about 3 minutes ago", "kim/team-intro               public  about 3 minutes ago"]
LIST3 = ["", "Showing 3 of 3 repositories in @kim", "", "NAME            DESCRIPTION  INFO    UPDATED",
         "kim/hello-git                public  about 3 minutes ago", "kim/my-notes                 public  about 3 minutes ago",
         "kim/team-intro               public  about 3 minutes ago"]
INIT = "Initialized empty Git repository in /home/kim/kant/my-notes/.git/"
COMMIT_MN = ["[main (root-commit) f5c3a4c] docs: README 추가", " 1 file changed, 1 insertion(+)", " create mode 100644 README.md"]
CREATE = ["✓ Created repository kim/my-notes on github.com", "  https://github.com/kim/my-notes", "✓ Added remote https://github.com/kim/my-notes.git"]
REMOTE_MN = ["origin\thttps://github.com/kim/my-notes.git (fetch)", "origin\thttps://github.com/kim/my-notes.git (push)"]
PUSH_MN = ["Enumerating objects: 3, done.", "Counting objects: 100% (3/3), done.", "Writing objects: 100% (3/3), 230 bytes | 230.00 KiB/s, done.",
           "Total 3 (delta 0), reused 0 (delta 0), pack-reused 0", "To https://github.com/kim/my-notes.git", " * [new branch]      main -> main"]
CREATE_Q = ["? What would you like to do?  [Use arrows to move, type to filter]", "> Create a new repository on github.com from scratch",
            "  Create a new repository on github.com from a template repository", "  Push an existing local repository to github.com"]
CONFIRM = "? Type kim/my-notes to confirm deletion: kim/my-notes"
DEL_403 = "HTTP 403: Must have admin rights to Repository. (https://api.github.com/repos/kim/my-notes)"
DEL_HINT = ['This API operation needs the "delete_repo" scope. To request it, run:', "  gh auth refresh -h github.com -s delete_repo"]
DELETED = "✓ Deleted repository kim/my-notes"
NOT_FOUND = "fatal: repository 'https://github.com/kim/my-notes.git/' not found"
ISSUE_NEW = ["", "Creating issue in kim/team-intro", "", "https://github.com/kim/team-intro/issues/1"]
ISSUE_LIST = ["", "Showing 1 of 1 open issue in kim/team-intro", "", "ID  TITLE                    LABELS  UPDATED", "#1  소개 페이지에 사진 넣기          less than a minute ago"]
BR_NEW = "Switched to a new branch 'feature/kim-hobby'"
COMMIT_HB = ["[feature/kim-hobby 8039736] feat: kim 취미 추가", " 1 file changed, 1 insertion(+)"]
PUSH_HB = ["Enumerating objects: 5, done.", "Counting objects: 100% (5/5), done.", "Delta compression using up to 4 threads",
           "Compressing objects: 100% (2/2), done.", "Writing objects: 100% (3/3), 308 bytes | 308.00 KiB/s, done.",
           "Total 3 (delta 0), reused 0 (delta 0), pack-reused 0", "To https://github.com/kim/team-intro.git", " * [new branch]      feature/kim-hobby -> feature/kim-hobby"]
PR_NEW = ["", "Creating pull request for feature/kim-hobby into main in kim/team-intro", "", "https://github.com/kim/team-intro/pull/2"]
PR_LIST = ["", "Showing 1 of 1 open pull request in kim/team-intro", "", "ID  TITLE                BRANCH             CREATED AT", "#2  feat: kim 취미 추가  feature/kim-hobby  less than a minute ago"]
PR_VIEW = ["feat: kim 취미 추가 kim/team-intro#2", "Open • kim (kim) wants to merge 1 commit into main from feature/kim-hobby • less than a minute ago",
           "+1 -0 • No checks", "", "", "  kim.md에 취미를 적었어요", "", "", "View this pull request on GitHub: https://github.com/kim/team-intro/pull/2"]
PR_MERGED = "✓ Merged pull request kim/team-intro#2 (feat: kim 취미 추가)"
CO_MAIN = ["Switched to branch 'main'", "Your branch is up to date with 'origin/main'."]
PULL = ["From https://github.com/kim/team-intro", " * branch            main       -> FETCH_HEAD", "   1baff03..5487d25  main       -> origin/main",
        "Updating 1baff03..5487d25", "Fast-forward", " kim.md | 1 +", " 1 file changed, 1 insertion(+)"]
LOG_AFTER = ["5487d25 (HEAD -> main, origin/main, origin/HEAD) Merge pull request #2 from kim/feature/kim-hobby",
             "8039736 (origin/feature/kim-hobby, feature/kim-hobby) feat: kim 취미 추가", "1baff03 feat: kim 소개 추가", "a2a187e docs: README 추가"]
GH_HELP = ["Work seamlessly with GitHub from the command line.", "", "USAGE", "  gh <command> <subcommand> [flags]", "", "CORE COMMANDS",
           "  auth:          Authenticate gh and git with GitHub", "  browse:        Open repositories, issues, pull requests, and more in the browser",
           "  codespace:     Connect to and manage codespaces", "  gist:          Manage gists", "  issue:         Manage issues",
           "  org:           Manage organizations", "  pr:            Manage pull requests", "  project:       Work with GitHub Projects.",
           "  release:       Manage releases", "  repo:          Manage repositories", "  …"]

P_HOME, P_KANT, P_TI, P_MN = "~", "~/kant", "~/kant/team-intro", "~/kant/my-notes"

# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
       '<p style="font-size:28px;font-weight:700;color:#F2B27A;letter-spacing:2px">KANT AX/AI 엔지니어 트랙 · 11</p>',
       '<h1 style="font-size:100px;font-weight:900;line-height:1.15;color:#F6F5F1">터미널에서<br>GitHub 다루기</h1>',
       '<p style="font-size:40px;line-height:1.4;color:#BFC6D4">gh로 로그인하고<br>레포 만들고 지우기</p>']
cov.append(term([("$", P_HOME, "gh auth login"), ("g", "✓ Logged in as kim"), ("$", P_KANT, "gh repo create my-notes --public"), ("g", "✓ Created repository kim/my-notes on github.com")],
                1000, 340, 800, 380, tid="cov-term", size=24))
W("cover", cov, "11 챕터는 GitHub 공식 터미널 도구 gh(GitHub CLI)를 다뤄요. 지금까지 레포 만들기, PR 만들기 같은 일은 GitHub 웹사이트에서 버튼으로 했어요. 오늘은 같은 일을 터미널에서 해요. 로그인부터 시작해서 레포를 받고, 만들고, 지워요. 지울 때 권한이 모자라서 막히는 장면도 일부러 넣었어요. 마지막에는 이슈와 PR을 다루는 간단한 명령을 봐요.", ("intro", "들어가기"))

ORDER.append("toc")   # written last, after page numbers are known

# ---------- why: git, GitHub web, gh ----------
o = [sec("why")] + head("들어가기", "git, GitHub, gh는 서로 다른 도구예요", INK)
trio = [("git", BL, "내 컴퓨터의 기록 도구", ["add, commit", "push, pull로 주고받기"], "02부터 써 온 명령"),
        ("GitHub 웹사이트", GH, "브라우저로 여는 저장소 집", ["New repository 버튼", "Pull request 버튼"], "레포 만들기, PR은 여기서 했어요"),
        ("gh", OR, "GitHub 버튼을 터미널에서 누르는 도구", ["gh repo create", "gh pr create"], "오늘 배울 명령")]
for i, (t, c, d, items, foot) in enumerate(trio):
    x = 96 + i * 584
    inner = (p(f"font-family:{MONO if t != 'GitHub 웹사이트' else SANS};font-size:44px;font-weight:900;color:{c}", e(t))
             + p(f"font-size:28px;font-weight:700;line-height:1.4;color:{INK}", e(d))
             + "".join(p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{INK};background:#F1EFE9;border-radius:10px;padding:8px 16px", e(it)) for it in items)
             + '<div style="flex:1"></div>' + p(f"font-size:22px;color:{SUB}", e(foot)))
    o.append(box(inner, x, 220, 560, 520, f' data-build-in="rise order {i + 1}"', top_color=c, gap=18))
o.append(caption("gh는 git을 대신하지 않아요. 웹사이트에서 누르던 버튼을 맡아요.", 800))
W("why", o, "세 도구를 먼저 구분해요. git은 내 컴퓨터에서 기록을 남기고, push와 pull로 GitHub과 주고받아요. GitHub은 웹사이트예요. 레포를 만들거나 PR을 여는 일은 지금까지 브라우저에서 버튼으로 했어요. gh는 그 버튼을 터미널 명령으로 바꾼 도구예요. 그래서 커밋과 push는 계속 git으로 하고, 레포 만들기와 PR 만들기를 gh로 해요. 둘을 같이 써요.")

o = [sec("map")] + head("들어가기", "웹에서 누르던 버튼과 gh 명령", INK)
rows = [("로그인", "gh auth login", BL), ("저장소 받기 (Code › 주소 복사)", "gh repo clone kim/team-intro", GR),
        ("New repository", "gh repo create my-notes --public", TEAL), ("Settings › Delete this repository", "gh repo delete kim/my-notes", RED),
        ("New issue", "gh issue create", OR), ("Compare & pull request", "gh pr create", OR)]
for i, (a_, b_, c) in enumerate(rows):
    y = 214 + i * 108
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:96px;top:{y}px;width:1728px;height:92px;background:{CARD};border:2px solid {LINE};border-left:12px solid {c};border-radius:18px;padding:0 36px;display:flex;flex-direction:row;align-items:center;gap:30px">'
             + p(f"width:700px;flex:none;font-size:30px;font-weight:700;color:{GH}", e(a_))
             + '<x-shape kind="arrow-right" style="width:56px;height:36px;background:#C9CED8"></x-shape>'
             + p(f"flex:1;font-family:{MONO};font-size:30px;font-weight:700;color:{INK}", e(b_)) + '</div>')
o.append(caption("오늘은 이 여섯 줄을 위에서부터 차례로 쳐 봐요.", 900))
W("map", o, "오늘 쓸 명령을 웹 버튼과 나란히 놓았어요. 왼쪽 보라색은 GitHub 웹사이트에서 누르던 버튼이에요. 오른쪽이 같은 일을 하는 gh 명령이에요. 1파트에서 로그인, 2파트에서 clone, 3파트에서 레포 만들기, 4파트에서 지우기, 5파트에서 이슈와 PR을 봐요. gh 명령은 모두 gh 다음에 대상(repo, issue, pr)과 할 일(create, list, delete)을 적는 모양이에요.")

# ---------- part 1: install and login ----------
EB1 = "1. 설치하고 로그인하기"
o = [sec("install")] + head(EB1, "gh 설치하기", BL)
o.append(card("Mac", f'{code("brew install gh", INK, 30)}<br><br>09에서 uv를 설치한 Homebrew로 설치해요.', 96, 220, 840, 300, BL, ' data-build-in="rise order 1"', tsize=34, bsize=26))
o.append(card("Windows", f'{code("winget install --id GitHub.cli -e", INK, 30)}<br><br>설치가 끝나면 Git Bash를 껐다 다시 열어요.', 984, 220, 840, 300, BL, ' data-build-in="rise order 2"', tsize=34, bsize=26))
o.append(label("설치됐는지 확인", 96, 570, 900, BL, ' data-build-in="fade order 3"'))
o.append(term([("$", P_HOME, "gh --version")] + [("o", l) for l in VERSION], 96, 620, 1728, 220, attrs=' data-build-in="rise order 3"', size=26))
o.append(caption("버전이 나오면 설치 끝이에요. 숫자는 설치한 날에 따라 달라요.", 880))
W("install", o, "Mac은 09에서 uv를 설치할 때 쓴 Homebrew로 brew install gh를 쳐요. Windows는 winget으로 설치해요. 대소문자까지 GitHub.cli 그대로 적어요. 설치 직후 Git Bash가 gh를 못 찾으면 창을 닫고 다시 열어요. 설치 화면은 이 자료를 만든 환경에서 실행할 수 없어서 옮기지 않았어요. gh --version 출력은 실제로 실행한 결과예요. 버전 숫자는 설치한 날에 따라 달라요.")

o = [sec("status0")] + head(EB1, "gh auth status · 로그인했는지 묻기", BL)
o.append(term([("$", P_HOME, "gh auth status"), ("m", NOT_LOGGED, "", "")], 96, 220, 1728, 200, size=24))
o.append(box(p(f"font-size:30px;font-weight:700;color:{INK}", "아직 로그인하지 않았어요")
             + p(f"font-size:26px;line-height:1.5;color:{SUB}", "gh는 내가 누구인지 모르면 GitHub에 아무것도 요청할 수 없어요. 출력 끝에 할 일이 적혀 있어요. gh auth login이에요."),
             96, 470, 1728, 190, ' data-build-in="rise order 1"', top_color=BL, pad="24px 36px"))
steps = [("auth", "로그인 관련"), ("status", "상태 보기")]
for i, (k, d) in enumerate(steps):
    o.append(box(p(f"font-family:{MONO};font-size:34px;font-weight:700;color:{BL}", k) + p(f"font-size:24px;color:{SUB}", d), 96 + i * 440, 700, 410, 150, f' data-build-in="rise order {i + 2}"', pad="20px 30px", gap=6))
o.append(p(f"position:absolute;left:1000px;top:730px;width:824px;font-size:28px;font-weight:700;line-height:1.5;color:{INK}", "gh 다음에 대상, 그다음에 할 일을 적어요.", ' data-build-in="fade order 3"'))
W("status0", o, "설치하자마자 gh auth status를 쳐 봐요. auth는 로그인 관련 명령 묶음이고, status는 상태를 보여 달라는 뜻이에요. 아직 로그인하지 않았다는 출력이 나와요. 끝에 To log in, run: gh auth login이라고 다음에 칠 명령까지 알려 줘요. 번외 터미널 환경에 적응하기에서 본 것처럼 에러와 안내의 마지막 줄을 읽는 습관이 여기서도 통해요.")

# login questions, one per slide (magic)
QS = [("login1", "질문 1 · 어디서 쓰나요?", "? Where do you use GitHub?  [Use arrows to move, type to filter]", ["> GitHub.com", "  Other"], "GitHub.com",
       "Enter", "github.com 웹사이트를 쓰니 그대로 Enter예요. Other는 회사 전용 GitHub일 때 골라요.",
       "gh auth login을 치면 질문이 네 개 나와요. 한 장에 하나씩 볼게요. 첫 질문은 어떤 GitHub을 쓰는지예요. 우리는 github.com을 쓰니 GitHub.com이 골라진 상태에서 Enter를 눌러요. 위아래 화살표로 고르고 Enter로 정해요. 질문 끝의 Use arrows to move가 그 뜻이에요."),
      ("login2", "질문 2 · git 주고받는 방식", "? What is your preferred protocol for Git operations on this host?  [Use arrows to move, type to filter]", ["> HTTPS", "  SSH"], "HTTPS",
       "Enter", "02부터 써 온 https:// 주소 방식이에요. SSH는 따로 열쇠 파일을 만들어야 해서 이 과정에서는 쓰지 않아요.",
       "두 번째 질문은 git이 GitHub과 주고받을 때 어떤 주소를 쓸지예요. 02에서 git remote add origin https://github.com/... 처럼 https 주소를 썼어요. 그래서 HTTPS 그대로 Enter예요. SSH는 내 컴퓨터에 열쇠 파일을 만들어 등록하는 방식이라 이 과정에서는 다루지 않아요."),
      ("login3", "질문 3 · git도 같이 로그인할까요?", "? Authenticate Git with your GitHub credentials? (Y/n)", [], "Yes",
       "Y 또는 Enter", "Yes로 하면 git push 할 때도 gh 로그인을 써요. 비밀번호나 토큰 창이 더는 뜨지 않아요.",
       "세 번째 질문이 오늘 가장 반가운 질문이에요. git도 gh의 로그인 정보를 쓰게 할지 물어요. (Y/n)에서 대문자 Y가 기본값이라 Enter만 눌러도 Yes예요. 02의 첫 push에서 GitHub 로그인 창이나 토큰 입력 창이 떴던 것 기억나죠? Yes로 하면 그 창이 더는 뜨지 않아요."),
      ("login4", "질문 4 · 어떻게 로그인할까요?", "? How would you like to authenticate GitHub CLI?  [Use arrows to move, type to filter]", ["> Login with a web browser", "  Paste an authentication token"], "Login with a web browser",
       "Enter", "브라우저로 로그인해요. 토큰을 직접 만들어 붙여 넣는 방법은 쓰지 않아요.",
       "마지막 질문은 로그인 방법이에요. Login with a web browser가 가장 쉬워요. 브라우저에서 GitHub에 이미 로그인돼 있으면 버튼 두 번이면 끝나요. Paste an authentication token은 GitHub 설정에서 토큰을 직접 만들어 붙이는 방법이에요. 이 과정에서는 쓰지 않아요.")]
done = []
ANS = [Q_WHERE, Q_PROTO, Q_GIT, Q_HOW]
for i, (sid, title, q, opts, pick, key, why, notes) in enumerate(QS):
    o = [sec(sid, "magic" if i else "fade")] + head(EB1, e(title), BL)
    lines = [("$", P_HOME, "gh auth login")] + [("o", a) for a in done] + [("y", q)] + [("sel" if x.startswith(">") else "o", x) for x in opts]
    o.append(term(lines, 96, 220, 1728, 360, size=24))
    for j in range(4):
        st = "done" if j < i else ("now" if j == i else "todo")
        c = {"done": GR, "now": BL, "todo": "#C9CED8"}[st]
        o.append(f'<div id="dot{j}" style="position:absolute;left:{96 + j * 120}px;top:620px;width:100px;height:14px;border-radius:7px;background:{c}"></div>')
    o.append(p(f"position:absolute;left:600px;top:606px;width:600px;font-size:24px;font-weight:700;color:{GRAY}", f"질문 {i + 1} / 4", ' id="qcount"'))
    o.append(box(p(f"font-size:24px;font-weight:700;color:{GRAY}", "고를 것") + p(f"font-family:{MONO};font-size:36px;font-weight:700;color:{GR}", e(pick))
                 + p(f"font-size:24px;color:{SUB}", "누를 키 · " + e(key)), 96, 670, 640, 230, f' id="pick{i}" data-build-in="rise order 1"', top_color=GR, gap=10))
    o.append(box(p(f"font-size:28px;font-weight:700;line-height:1.5;color:{INK}", e(why)), 776, 670, 1048, 230, f' id="why{i}" data-build-in="rise order 2"', pad="28px 36px", extra="justify-content:center"))
    W(sid, o, notes, ("login", "로그인") if i == 0 else None)
    done.append(ANS[i])

o = [sec("code", "magic")] + head(EB1, "한 번만 쓰는 코드를 브라우저에 넣어요", BL)
o.append(term([("$", P_HOME, "gh auth login")] + [("o", a) for a in ANS] + [("o", ""), ("m", DEVICE[0], "1", BL), ("m", DEVICE[1], "2", BL)], 96, 220, 1728, 340, size=22))
o.append(browser("github.com/login/device", p(f"font-size:30px;font-weight:700;color:{INK}", "Device Activation") + code_boxes(CODE, 34) + gh_button("Continue"),
                 96, 596, 840, 340, bid="br1", attrs=' data-build-in="rise order 1"'))
o.append(browser("github.com/login/device", p(f"font-size:30px;font-weight:700;color:{INK}", "Authorize GitHub CLI") + p(f"font-size:22px;color:{SUB}", "GitHub CLI가 내 계정을 쓰도록 허락해요") + gh_button("Authorize github"),
                 984, 596, 840, 340, bid="br2", attrs=' data-build-in="rise order 2"'))
o.append(arrow(944, 746, 32, 40, BL, ' data-build-in="fade order 2"'))
W("code", o, "질문이 끝나면 터미널에 여덟 글자 코드가 나와요. 1번 줄이에요. 코드는 로그인할 때마다 바뀌어요. Enter를 누르면 2번 줄대로 브라우저가 github.com/login/device를 열어요. 브라우저에서 코드를 넣고 Continue, 다음 화면에서 Authorize github를 눌러요. 브라우저 화면은 버튼 위치만 보이게 단순하게 그렸어요. 브라우저가 저절로 안 열리면 주소를 직접 쳐서 들어가도 돼요.")

o = [sec("logged", "magic")] + head(EB1, "로그인 끝 · 터미널이 알려 주는 다섯 줄", BL)
o.append(term([("$", P_HOME, "gh auth login")] + [("o", a) for a in ANS] + [("o", ""), ("o", DEVICE[0]), ("o", DEVICE[1]),
              ("m", LOGIN_TAIL[0], "1", GR), ("o", LOGIN_TAIL[1]), ("m", LOGIN_TAIL[2], "2", GR), ("o", LOGIN_TAIL[3]), ("m", LOGIN_TAIL[4], "3", GR)],
              96, 220, 1728, 560, size=24))
for i, (t, d) in enumerate([("1", "브라우저에서 허락 완료"), ("2", "git 주소 방식을 HTTPS로 저장"), ("3", "kim 계정으로 로그인")]):
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:{96 + i * 584}px;top:810px;width:560px;height:96px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:0 26px;display:flex;flex-direction:row;align-items:center;gap:20px">'
             + num(t, GR, 34) + p(f"font-size:28px;font-weight:700;color:{INK}", e(d)) + '</div>')
W("logged", o, "브라우저에서 Authorize를 누르면 터미널이 저절로 다음 줄을 출력해요. 1번 Authentication complete는 브라우저 허락이 끝났다는 뜻이에요. 2번은 앞에서 고른 HTTPS를 설정에 저장했다는 뜻이에요. 3번 Logged in as kim에서 kim 자리에 내 GitHub 아이디가 보이면 성공이에요. 가운데 saved in plain text 줄은 로그인 정보를 파일에 저장했다는 안내예요. 이 자료를 만든 환경에는 Mac의 키체인 같은 비밀 보관함이 없어서 나왔어요. Mac과 Windows는 보통 비밀 보관함에 저장해서 이 줄이 안 나와요.")

o = [sec("status1")] + head(EB1, "다시 gh auth status · 토큰과 권한 목록", BL)
o.append(term([("$", P_HOME, "gh auth status")] + [("o", l) for l in STATUS[:2]] + [("o", l) for l in STATUS[2:4]] + [("m", STATUS[4], "1", BL), ("m", SCOPES, "2", OR)], 96, 220, 1728, 330, size=24))
o.append(card("1 · 토큰 = 출입증", "로그인하면 GitHub이 gh에게 출입증(토큰)을 줘요. 화면에는 앞 네 글자만 보이고 나머지는 *로 가려요.", 96, 590, 840, 260, BL, ' data-build-in="rise order 1"'))
o.append(card("2 · 권한(scope) = 출입증으로 열 수 있는 문", "repo는 레포 읽고 쓰기, read:org는 조직 보기, gist는 메모 조각, workflow는 Actions 설정이에요. 이 목록에 없는 일은 못 해요.", 984, 590, 840, 260, OR, ' data-build-in="rise order 2"'))
o.append(caption("2번 목록을 기억해 둬요. 4파트에서 여기에 한 줄이 늘어요.", 890))
W("status1", o, "로그인한 뒤 gh auth status를 다시 쳐요. 이번에는 kim 계정으로 로그인했다고 나와요. 1번 Token은 GitHub이 준 출입증이에요. 비밀번호 같은 거라 화면에는 앞 네 글자만 보여 줘요. 2번 Token scopes는 이 출입증으로 할 수 있는 일의 목록이에요. 레포 읽고 쓰기(repo)는 있지만 레포 지우기(delete_repo)는 없어요. 4파트에서 지우기를 시도하다가 이 목록 때문에 막혀요.")

o = [sec("gitcred")] + head(EB1, "질문 3의 Yes가 바꾼 것 · git도 gh로 로그인해요", BL)
o.append(term([("$", P_HOME, "cat ~/.gitconfig"), ("d", "…"), ("o", "[pull]"), ("o", "\trebase = false"), ("m", '[credential "https://github.com"]', "", ""),
               ("o", "\thelper ="), ("m", "\thelper = !/usr/local/bin/gh auth git-credential", "", ""), ("d", "…")], 96, 220, 1000, 420, size=24))
flow = [("git push origin main", INK), ("git이 gh에게 출입증을 물어요", BL), ("GitHub에 바로 올라가요", GH)]
for i, (t, c) in enumerate(flow):
    y = 220 + i * 150
    o.append(box(p(f"font-size:28px;font-weight:700;color:{c};{'font-family:' + MONO + ';' if i == 0 else ''}", e(t)), 1160, y, 664, 110, f' data-build-in="rise order {i + 1}"', pad="0 30px", extra="justify-content:center"))
    if i < 2:
        o.append(f'<x-shape kind="arrow-right" data-build-in="fade order {i + 2}" style="position:absolute;left:1473px;top:{y + 112}px;width:34px;height:40px;background:#C9CED8;transform:rotate(90deg)"></x-shape>')
o.append(box(p(f"font-size:28px;font-weight:700;color:{INK}", "02의 첫 push에서 뜨던 로그인 창, 토큰 입력 창이 이제 안 떠요.")
             + p(f"font-size:24px;color:{SUB}", "이 줄은 gh가 넣었어요. 직접 고치지 않아요."), 96, 690, 1728, 170, ' data-build-in="rise order 4"', pad="24px 36px"))
W("gitcred", o, "질문 3에서 Yes를 고르면 gh가 git 설정 파일(~/.gitconfig)에 두 줄을 넣어요. credential은 로그인 정보라는 뜻이에요. github.com에 push 할 때 로그인 정보는 gh auth git-credential에게 물어보라는 설정이에요. 그래서 git push origin main을 치면 git이 gh에게 출입증을 받아서 바로 올려요. 위쪽 [pull] rebase = false는 06에서 넣은 pull 설정이에요. helper = 처럼 빈 줄도 gh가 일부러 넣은 거라 지우지 않아요. 파일 내용은 tools/demo.sh에서 실제로 실행한 결과고, 위아래는 …로 줄였어요. Windows는 /usr/local/bin 자리에 설치 경로가 달라요.")

# ---------- part 2: connect existing repos ----------
EB2 = "2. 이미 있는 레포 연결하기"
o = [sec("clone")] + head(EB2, "gh repo clone · 주소 대신 주인/이름", GR)
o += [label("git으로 받을 때 (02)", 96, 200, 840, GRAY),
      term([("$", P_KANT, "git clone https://github.com/kim/team-intro.git")], 96, 244, 840, 130, tid="t-git", size=22),
      label("gh로 받을 때", 984, 200, 840, GR, ' data-build-in="fade order 1"'),
      term([("$", P_KANT, "gh repo clone kim/team-intro")], 984, 244, 840, 130, tid="t-gh", size=22, attrs=' data-build-in="rise order 1"')]
o.append(term([("$", P_KANT, "gh repo clone kim/team-intro")] + [("o", l) for l in CLONE], 96, 420, 1728, 330, tid="t-out", size=24, attrs=' data-build-in="rise order 2"'))
o.append(caption("받는 내용은 같아요. 주소 앞뒤(https://github.com/, .git)를 안 적어도 돼요.", 800))
W("clone", o, "06에서 팀 레포 team-intro를 git clone으로 받았어요. gh는 같은 일을 gh repo clone 주인/이름으로 해요. 주소 전체를 복사해 오지 않아도 kim/team-intro만 적으면 돼요. 아래 출력의 첫 줄 Cloning into는 git clone과 똑같아요. gh가 속에서 git clone을 부르기 때문이에요. 출력은 tools/demo.sh에서 실제로 실행한 결과예요. 실습할 땐 kim 자리에 팀장 아이디를 적어요.", ("connect", "이미 있는 레포 연결하기"))

o = [sec("clone-check")] + head(EB2, "받은 폴더는 git clone과 똑같아요", GR)
o.append(term([("$", P_KANT, "cd team-intro"), ("$", P_TI, "git remote -v")] + [("m", l, "", "") for l in REMOTE_TI] + [("$", P_TI, "git log --oneline")] + [("o", l) for l in LOG_TI],
              96, 220, 1728, 330, size=24))
o.append(card("origin도 그대로", "gh가 origin 이름으로 https 주소를 등록했어요. git push origin main, git pull origin main을 지금까지처럼 쳐요.", 96, 600, 840, 230, GR, ' data-build-in="rise order 1"'))
o.append(card("git으로 받은 폴더도 OK", "06에서 git clone으로 받은 폴더에서도 gh를 바로 쓸 수 있어요. gh는 origin 주소를 보고 어느 레포인지 알아요.", 984, 600, 840, 230, GR, ' data-build-in="rise order 2"'))
W("clone-check", o, "받은 폴더에 들어가서 git remote -v를 쳐요. origin이 https://github.com/kim/team-intro.git으로 등록돼 있어요. git clone으로 받았을 때와 같아요. 그래서 push, pull 명령도 그대로예요. 반대로 06에서 git clone으로 받은 폴더에서도 gh 명령을 바로 쓸 수 있어요. 다음 장에서 보는 gh repo view는 origin 주소를 읽고 어느 레포인지 알아내요.")

o = [sec("view")] + head(EB2, "레포 폴더 안에서 gh repo view, gh browse", GR)
o.append(term([("$", P_TI, "gh repo view")] + [("o", l) for l in VIEW], 96, 220, 1000, 600, size=24))
o.append(term([("$", P_TI, "gh browse"), ("o", BROWSE)], 1140, 220, 684, 200, tid="t-browse", size=17, attrs=' data-build-in="rise order 1"'))
o.append(card("gh repo view", "레포 이름과 README를 터미널에 보여 줘요.", 1140, 460, 684, 170, GR, ' data-build-in="rise order 2"', bsize=24, mono_title=True))
o.append(card("gh browse", "지금 레포를 브라우저로 열어요.", 1140, 660, 684, 160, GR, ' data-build-in="rise order 3"', bsize=24, mono_title=True))
o.append(caption("주인/이름을 안 적어도 돼요. 지금 폴더의 레포를 써요.", 870))
W("view", o, "레포 폴더 안에서 gh repo view를 치면 레포 이름, 설명, README 내용을 터미널에 보여 줘요. 설명을 안 적은 레포라 No description provided가 나와요. gh browse는 같은 레포를 브라우저 새 탭으로 열어요. 웹에서 할 일이 있을 때 주소를 찾지 않아도 돼요. 두 명령 모두 주인/이름을 적지 않았어요. 지금 폴더의 origin을 보고 kim/team-intro라고 알아낸 거예요.")

o = [sec("repo-list")] + head(EB2, "gh repo list · 내 레포 목록", GR)
o.append(term([("$", P_HOME, "gh repo list")] + [("o", l) for l in LIST2], 96, 220, 1728, 360, size=26))
o.append(card("어디서 쳐도 돼요", "내 계정의 레포 목록이라 레포 폴더 밖, 홈 폴더에서 쳐도 같아요.", 96, 620, 840, 220, GR, ' data-build-in="rise order 1"'))
o.append(card("이름을 확인하는 곳", "clone이나 delete에 적을 주인/이름을 여기서 복사해요.", 984, 620, 840, 220, GR, ' data-build-in="rise order 2"'))
W("repo-list", o, "gh repo list는 내 계정의 레포 목록을 보여 줘요. 특정 레포 안에서 쓰는 명령이 아니라서 어느 폴더에서 쳐도 결과가 같아요. kim/hello-git은 02에서 만든 레포, kim/team-intro는 06의 팀 레포예요. INFO 칸의 public은 누구나 볼 수 있는 레포라는 뜻이에요. clone이나 delete에 적을 주인/이름이 헷갈리면 이 목록에서 확인해요.")

# ---------- part 3: create ----------
EB3 = "3. 새 레포 만들기"
o = [sec("create-why")] + head(EB3, "웹에서 만들 때와 gh로 만들 때", TEAL)
web = ["GitHub에서 New 누르기", "이름 적고 Create", "주소 복사", "git remote add origin 주소"]
o.append(label("웹에서 (02)", 96, 210, 840, GH))
for i, t in enumerate(web):
    y = 260 + i * 120
    o.append(f'<div data-build-in="rise order {i + 1}" style="position:absolute;left:96px;top:{y}px;width:840px;height:100px;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:0 26px;display:flex;flex-direction:row;align-items:center;gap:20px">'
             + num(i + 1, GH, 34) + p(f"font-size:28px;font-weight:700;color:{INK};{'font-family:' + MONO + ';font-size:26px;' if i == 3 else ''}", e(t)) + '</div>')
o.append(label("gh로", 984, 210, 840, TEAL, ' data-build-in="fade order 5"'))
o.append(box(p(f"font-family:{MONO};font-size:30px;font-weight:700;line-height:1.5;color:{INK}", "gh repo create my-notes<br>&#160;&#160;--public --source=. --remote=origin")
             + p(f"font-size:26px;line-height:1.5;color:{SUB}", "브라우저 없이 한 줄로 레포를 만들고 origin까지 연결해요."),
             984, 260, 840, 460, ' data-build-in="rise order 5"', top_color=TEAL, gap=24, extra="justify-content:center"))
o.append(caption("만들고 연결하는 데까지 gh가 해요. push는 지금처럼 git으로 해요.", 840))
W("create-why", o, "02에서 레포를 GitHub에 올릴 때 네 단계를 거쳤어요. 웹에서 New를 누르고, 이름을 적고 Create를 누르고, 주소를 복사해서 git remote add origin으로 연결했어요. gh repo create는 이 네 단계를 한 줄로 해요. 다만 push는 하지 않아요. push는 지금까지처럼 git push origin main으로 직접 쳐요.", ("create", "새 레포 만들기"))

o = [sec("create-prep")] + head(EB3, "먼저 내 컴퓨터에 저장소와 커밋을 만들어요", TEAL)
o.append(term([("$", P_KANT, "mkdir my-notes"), ("$", P_KANT, "cd my-notes"), ("$", P_MN, "git init"), ("o", INIT),
               ("$", P_MN, "echo '# my-notes' > README.md"), ("$", P_MN, "git add README.md"), ("$", P_MN, "git commit -m 'docs: README 추가'")] + [("o", l) for l in COMMIT_MN],
              96, 220, 1728, 470, size=24))
o.append(caption("02에서 한 순서 그대로예요. 커밋이 하나 있어야 GitHub에 올릴 게 생겨요.", 740))
W("create-prep", o, "새 레포는 내 컴퓨터 폴더에서 시작해요. 01의 mkdir, cd로 my-notes 폴더를 만들고 들어가요. 02에서 한 대로 git init, README.md 만들기, git add, git commit -m까지 쳐요. 출력은 tools/demo.sh에서 실제로 실행한 결과고, 커밋 해시는 칠 때마다 달라요. 커밋이 있어야 다음 장에서 GitHub에 올릴 내용이 생겨요.")

o = [sec("create")] + head(EB3, "gh repo create · 만들고 origin 연결까지", TEAL)
o.append(term([("$", P_MN, "gh repo create my-notes --public --source=. --remote=origin"), ("m", CREATE[0], "1", TEAL), ("o", CREATE[1]), ("m", CREATE[2], "2", TEAL)], 96, 220, 1728, 250, size=24))
opts = [("my-notes", "GitHub에 만들 레포 이름"), ("--public", "누구나 볼 수 있게. 나만 보려면 --private"), ("--source=.", "지금 폴더(.)를 레포로 써요"), ("--remote=origin", "origin 이름으로 연결해요")]
for i, (k, d) in enumerate(opts):
    x = 96 + i * 440
    o.append(box(p(f"font-family:{MONO};font-size:28px;font-weight:700;color:{TEAL}", e(k)) + p(f"font-size:24px;line-height:1.45;color:{SUB}", e(d)), x, 510, 410, 220, f' data-build-in="rise order {i + 1}"', top_color=TEAL, gap=12))
o.append(box(p(f"font-size:26px;font-weight:700;color:{INK}", "--push 옵션은 붙이지 않아요. push는 다음 장에서 git push origin main으로 직접 쳐요."), 96, 770, 1728, 110, ' data-build-in="rise order 5"', pad="0 36px", extra="justify-content:center"))
W("create", o, "my-notes 폴더 안에서 gh repo create를 쳐요. 1번 줄은 GitHub에 kim/my-notes 레포를 만들었다는 뜻이고, 2번 줄은 origin으로 연결했다는 뜻이에요. 옵션은 네 개예요. 레포 이름, 공개 여부, 지금 폴더를 쓴다는 --source=., 원격 이름 --remote=origin이에요. gh repo create에는 --push 옵션도 있어요. 그런데 --push는 우리가 이 과정에서 쓰지 않기로 한 push 설정까지 같이 바꿔요. 그래서 붙이지 않고, push는 지금까지처럼 직접 쳐요.")

o = [sec("create-push")] + head(EB3, "push는 git으로 · 그리고 목록 확인", TEAL)
o.append(term([("$", P_MN, "git remote -v")] + [("o", l) for l in REMOTE_MN] + [("$", P_MN, "git push origin main")] + [("o", l) for l in PUSH_MN[:-1]] + [("m", PUSH_MN[-1], "", "")],
              96, 220, 1040, 500, size=22))
o.append(term([("$", P_HOME, "gh repo list")] + [("o", l) for l in LIST3[:4]] + [("o", LIST3[4][:29]), ("m", LIST3[5][:29], "", ""), ("o", LIST3[6][:29])], 1180, 220, 644, 500, tid="t-list", size=20, attrs=' data-build-in="rise order 1"'))
o.append(caption("로그인 창 없이 push가 끝났어요. 질문 3의 Yes 덕분이에요.", 780))
W("create-push", o, "git remote -v로 origin이 https://github.com/kim/my-notes.git인지 보고, git push origin main으로 올려요. 비밀번호나 토큰을 묻지 않고 바로 올라가요. 1파트 질문 3에서 Yes를 골라 git이 gh 로그인을 쓰기 때문이에요. 오른쪽 gh repo list에 kim/my-notes가 한 줄 늘었어요. 오른쪽 목록은 화면에 맞추려고 UPDATED 칸을 잘랐어요.")

o = [sec("create-ask")] + head(EB3, "옵션을 잊었으면 gh repo create만 쳐요", TEAL)
o.append(term([("$", P_KANT, "gh repo create"), ("y", CREATE_Q[0]), ("sel", CREATE_Q[1]), ("o", CREATE_Q[2]), ("o", CREATE_Q[3])], 96, 220, 1728, 260, size=24))
asks = [("빈 레포를 새로", "Create a new repository … from scratch"), ("템플릿에서", "… from a template repository"), ("내 폴더를 올리기", "Push an existing local repository …")]
for i, (k, d) in enumerate(asks):
    o.append(card(k, e(d), 96 + i * 584, 530, 560, 200, TEAL, f' data-build-in="rise order {i + 1}"', bsize=22))
o.append(caption("질문에 답하면 앞 장의 옵션을 gh가 채워요. 화살표와 Enter로 골라요.", 790))
W("create-ask", o, "옵션이 기억나지 않으면 gh repo create만 쳐도 돼요. 무엇을 할지부터 하나씩 물어봐요. 첫 질문의 세 번째 Push an existing local repository가 앞 장에서 한 일이에요. 그다음 폴더 위치, 레포 이름, 공개 여부, origin 이름을 차례로 물어요. 마지막에 지금 push 할지도 묻는데, 거기서는 No를 고르고 git push origin main으로 직접 올려요. 첫 질문 화면은 실제로 실행한 출력이에요.")

# ---------- part 4: delete and scope ----------
EB4 = "4. 레포 지우기와 권한 추가"
o = [sec("del-warn")] + head(EB4, "지우기 전에 · 되돌릴 수 없어요", RED)
gone = [("GitHub의 레포", "커밋 기록, README", True), ("이슈와 PR", "토론과 리뷰 기록", True), ("스타와 포크 연결", "다른 사람이 누른 것", True), ("내 컴퓨터 폴더", "~/kant/my-notes는 남아요", False)]
for i, (t, d, lost) in enumerate(gone):
    x = 96 + i * 440
    c = RED if lost else GR
    o.append(box(p(f"font-size:24px;font-weight:700;color:{c}", "사라져요" if lost else "남아요") + p(f"font-size:30px;font-weight:700;color:{INK}", e(t)) + p(f"font-size:24px;color:{SUB}", e(d)),
                 x, 230, 410, 280, f' data-build-in="rise order {i + 1}"', top_color=c, gap=12, bg="#FFFFFF" if lost else "#EEF7F1"))
o.append(box(p(f"font-size:30px;font-weight:700;color:{RED}", "휴지통이 없어요. 지운 레포는 다시 꺼낼 수 없어요.")
             + p(f"font-size:26px;line-height:1.5;color:{SUB}", "연습용으로 만든 my-notes만 지워요. team-intro처럼 팀이 쓰는 레포는 지우지 않아요."),
             96, 560, 1728, 210, ' data-build-in="rise order 5"', border=RED, pad="28px 36px"))
W("del-warn", o, "지우는 명령을 치기 전에 무엇이 사라지는지 먼저 봐요. GitHub에 있는 레포, 그 안의 이슈와 PR, 다른 사람이 누른 스타까지 모두 사라져요. 내 컴퓨터의 my-notes 폴더는 남아요. GitHub에는 휴지통이 없어서 지운 레포를 다시 꺼낼 수 없어요. 그래서 오늘은 방금 만든 연습용 my-notes만 지워요. 팀 레포는 절대 지우지 않아요.", ("delete", "레포 지우기"))

o = [sec("del-try")] + head(EB4, "gh repo delete · 첫 시도는 막혀요", RED)
o.append(term([("$", P_HOME, "gh repo delete kim/my-notes"), ("o", ""), ("m", CONFIRM, "1", BL), ("e", DEL_403), ("m", DEL_HINT[0], "2", OR), ("y", DEL_HINT[1])], 96, 220, 1728, 300, size=22))
o.append(card("1 · 이름을 한 번 더 쳐요", "실수로 지우지 않게 주인/이름을 그대로 다시 쳐야 해요.", 96, 570, 840, 220, BL, ' data-build-in="rise order 1"'))
o.append(card("2 · delete_repo 권한이 없어요", "출입증에 레포 지우기 권한이 없어서 GitHub이 거절했어요(403). 칠 명령까지 알려 줘요.", 984, 570, 840, 220, OR, ' data-build-in="rise order 2"'))
o.append(caption("고장이 아니에요. 처음 로그인할 땐 지우기 권한을 일부러 안 받아요.", 840))
W("del-try", o, "gh repo delete kim/my-notes를 쳐요. 1번처럼 지울 레포 이름을 한 번 더 쳐서 확인해요. 그런데 HTTP 403 에러가 나요. 403은 요청은 알아들었지만 허락할 수 없다는 뜻이에요. 2번 줄이 이유를 알려 줘요. 이 작업에는 delete_repo 권한(scope)이 필요하고, 받으려면 gh auth refresh -h github.com -s delete_repo를 치라고 해요. 1파트 마지막 status 장에서 본 권한 목록에 delete_repo가 없었죠? 실수로 레포를 지우지 않게 처음 로그인할 때는 이 권한을 빼고 받아요. 출력은 tools/demo.sh에서 실제로 실행한 결과예요.")

o = [sec("scope", "magic")] + head(EB4, "출입증에 지우기 권한을 한 칸 더해요", RED)
keys = [("repo", BL), ("read:org", BL), ("gist", BL), ("workflow", BL)]
o.append(box(p(f"font-size:26px;font-weight:700;color:{GRAY}", "지금 출입증 (토큰)"), 96, 220, 1728, 300, ' id="badge"', pad="24px 36px"))
for i, (k, c) in enumerate(keys):
    o.append(p(f"position:absolute;left:{140 + i * 330}px;top:310px;width:300px;height:100px;border-radius:16px;background:#E3ECFD;border:3px solid {c};font-family:{MONO};font-size:30px;font-weight:700;line-height:94px;text-align:center;color:{c}", e(k), f' id="k{i}"'))
o.append(p(f"position:absolute;left:{140 + 4 * 330}px;top:310px;width:330px;height:100px;border-radius:16px;border:3px dashed {RED};font-family:{MONO};font-size:30px;font-weight:700;line-height:94px;text-align:center;color:{RED}", "delete_repo ?", ' id="k4" data-build-in="pop order 1"'))
o.append(p(f"position:absolute;left:140px;top:440px;width:1640px;font-size:24px;color:{SUB}", "1파트 gh auth status의 Token scopes 줄이에요.", ' id="badge-note"'))
parts = [("gh auth refresh", "출입증을 새로 받아요"), ("-h github.com", "어느 GitHub인지"), ("-s delete_repo", "더할 권한(scope)")]
for i, (k, d) in enumerate(parts):
    o.append(box(p(f"font-family:{MONO};font-size:32px;font-weight:700;color:{RED}", e(k)) + p(f"font-size:26px;color:{SUB}", e(d)), 96 + i * 584, 580, 560, 180, f' data-build-in="rise order {i + 2}"', top_color=RED, gap=12))
o.append(caption("refresh는 질문 네 개 없이 출입증만 다시 받아요.", 820))
W("scope", o, "1파트에서 토큰을 출입증, 권한(scope)을 출입증으로 열 수 있는 문에 비유했어요. 지금 출입증에는 repo, read:org, gist, workflow 네 칸이 있고 delete_repo 칸이 없어요. 에러가 알려 준 명령을 나눠 읽어 봐요. gh auth refresh는 출입증을 새로 받는 명령이에요. -h github.com은 어느 GitHub인지, -s delete_repo는 더할 권한이에요. -h가 여기서는 도움말이 아니라 host(사이트 주소)의 줄임이라는 점을 짚어 주세요. 번외에서 본 예외와 같은 경우예요.")

o = [sec("refresh", "magic")] + head(EB4, "gh auth refresh · 코드를 한 번 더 넣어요", RED)
o.append(term([("$", P_HOME, "gh auth refresh -h github.com -s delete_repo"), ("o", ""), ("m", DEVICE[0], "1", BL), ("o", DEVICE[1]), ("m", "✓ Authentication complete.", "2", GR)], 96, 220, 1728, 270, size=24))
o.append(browser("github.com/login/device", p(f"font-size:30px;font-weight:700;color:{INK}", "Device Activation") + code_boxes(CODE, 34) + gh_button("Continue"),
                 96, 540, 840, 330, bid="br1", attrs=' data-build-in="rise order 1"'))
o.append(browser("github.com/login/device", p(f"font-size:30px;font-weight:700;color:{INK}", "Authorize GitHub CLI") + p(f"font-size:22px;color:{RED};font-weight:700", "Delete repositories 권한이 더해져요") + gh_button("Authorize github"),
                 984, 540, 840, 330, bid="br2", attrs=' data-build-in="rise order 2"'))
o.append(arrow(944, 685, 32, 40, RED, ' data-build-in="fade order 2"'))
W("refresh", o, "에러가 알려 준 명령을 그대로 쳐요. 1파트 로그인 때처럼 1번 코드가 나오고, Enter를 누르면 브라우저가 열려요. 코드를 넣고 Continue, Authorize를 누르면 돼요. 이번 허락 화면에는 레포 지우기 권한이 새로 들어 있어요. 2번 Authentication complete가 나오면 끝이에요. 질문 네 개는 다시 묻지 않아요. 코드는 칠 때마다 달라요. 브라우저 화면은 단순하게 그린 그림이에요.")

o = [sec("status2")] + head(EB4, "권한 목록에 delete_repo가 생겼어요", RED)
o.append(term([("$", P_HOME, "gh auth status")] + [("o", l) for l in STATUS] + [("d", SCOPES), ("m", SCOPES_DEL, "", "")], 96, 220, 1728, 360, size=24))
o.append(p(f"position:absolute;left:96px;top:596px;width:1200px;font-size:22px;font-weight:700;color:{GRAY}", "위 회색 줄은 refresh 전, 노란 줄이 지금이에요.", ' data-build-in="fade order 1"'))
for i, (k, c) in enumerate(keys + [("delete_repo", RED)]):
    o.append(p(f"position:absolute;left:{96 + i * 350}px;top:660px;width:320px;height:100px;border-radius:16px;background:{'#E3ECFD' if c == BL else '#FBE4E2'};border:3px solid {c};font-family:{MONO};font-size:30px;font-weight:700;line-height:94px;text-align:center;color:{c}", e(k), f' id="k{i}"'))
o.append(caption("이제 지우기를 다시 해 봐요.", 820))
W("status2", o, "gh auth status를 다시 쳐서 확인해요. Token scopes 맨 앞에 delete_repo가 생겼어요. 회색 줄은 비교하려고 refresh 전 줄을 같이 적은 거고, 실제 화면에는 노란 줄 하나만 나와요. 출입증에 다섯 번째 칸이 생겼으니 이제 지우기를 다시 해 봐요.")

o = [sec("del-ok")] + head(EB4, "두 번째 gh repo delete · 지워졌어요", RED)
o.append(term([("$", P_HOME, "gh repo delete kim/my-notes"), ("o", ""), ("o", CONFIRM), ("m", DELETED, "", ""), ("$", P_HOME, "gh repo list")] + [("o", l) for l in LIST2],
              96, 220, 1728, 450, size=22))
o.append(term([("$", P_MN, "git push origin main"), ("e", NOT_FOUND)], 96, 700, 1040, 150, tid="t-push", size=22, attrs=' data-build-in="rise order 1"'))
o.append(card("내 폴더는 그대로", "GitHub 쪽이 없어서 push하면 not found가 나요. 폴더가 필요 없으면 01의 rm -r로 지워요.", 1180, 700, 644, 190, GR, ' data-build-in="rise order 2"', bsize=22))
o.append(caption("지우기는 이름 확인, 권한 확인 두 번을 거쳐요.", 920))
W("del-ok", o, "같은 명령을 다시 쳐요. 이름을 한 번 더 치면 Deleted repository가 나와요. gh repo list에서도 my-notes가 사라졌어요. 내 컴퓨터의 my-notes 폴더는 남아 있어요. 거기서 git push origin main을 치면 GitHub 쪽 레포가 없어서 repository not found가 나요. 폴더가 필요 없으면 01에서 배운 rm -r로 지워요. 정리하면 레포 지우기는 이름을 다시 치는 확인과 delete_repo 권한 확인, 두 번을 거쳐요.")

# ---------- part 5: everyday gh ----------
EB5 = "5. 자주 쓰는 gh 명령"
o = [sec("issue")] + head(EB5, "gh issue · 할 일을 이슈로 남기기", OR)
o.append(term([("$", P_TI, 'gh issue create --title "소개 페이지에 사진 넣기" --body "각자 사진 한 장씩 넣어요"')] + [("o", l) for l in ISSUE_NEW[:-1]] + [("m", ISSUE_NEW[-1], "", "")],
              96, 220, 1728, 250, size=22))
o.append(term([("$", P_TI, "gh issue list")] + [("o", l) for l in ISSUE_LIST], 96, 500, 1728, 300, tid="t-ilist", size=24, attrs=' data-build-in="rise order 1"'))
o.append(caption("--title은 제목, --body는 내용이에요. 빼면 gh가 하나씩 물어봐요.", 850))
W("issue", o, "이슈는 레포에 남기는 할 일 메모예요. 웹에서는 Issues 탭의 New issue 버튼으로 만들어요. gh issue create에 --title로 제목, --body로 내용을 적으면 바로 만들어지고 주소를 알려 줘요. 둘을 빼고 gh issue create만 치면 제목과 내용을 하나씩 물어봐요. gh issue list는 열려 있는 이슈 목록이에요. #1이 이슈 번호예요. 출력은 tools/demo.sh에서 실제로 실행한 결과예요.", ("daily", "자주 쓰는 gh 명령"))

o = [sec("pr-create")] + head(EB5, "gh pr create · 브랜치 push 뒤 PR 만들기", OR)
o.append(term([("$", P_TI, "git checkout -b feature/kim-hobby"), ("o", BR_NEW), ("$", P_TI, "echo '취미: 등산' >> kim.md"), ("$", P_TI, "git add kim.md"),
               ("$", P_TI, "git commit -m 'feat: kim 취미 추가'")] + [("o", l) for l in COMMIT_HB] + [("$", P_TI, "git push origin feature/kim-hobby"), ("d", "…"), ("o", PUSH_HB[-1])],
              96, 200, 1728, 420, size=21))
o.append(term([("$", P_TI, 'gh pr create --title "feat: kim 취미 추가" --body "kim.md에 취미를 적었어요"')] + [("o", l) for l in PR_NEW[:-1]] + [("m", PR_NEW[-1], "", "")],
              96, 650, 1728, 230, tid="t-pr", size=21, attrs=' data-build-in="rise order 1"'))
o.append(caption("브랜치를 git push origin 브랜치로 먼저 올리고, 그다음 gh pr create예요.", 910))
W("pr-create", o, "03에서 브랜치를 만들어 push한 뒤 웹에서 Compare & pull request 버튼으로 PR을 열었어요. 위쪽은 03과 같은 순서예요. 브랜치를 만들고, 고치고, 커밋하고, git push origin feature/kim-hobby로 올려요. 아래 gh pr create가 웹 버튼을 대신해요. --title은 PR 제목, --body는 내용이에요. 꼭 push를 먼저 해요. push 전에 gh pr create를 치면 gh가 브랜치를 어디에 push할지 되물어요. push 출력의 가운데는 …로 줄였어요.")

o = [sec("pr-view")] + head(EB5, "gh pr list, gh pr view · PR 보기", OR)
o.append(term([("$", P_TI, "gh pr list")] + [("o", l) for l in PR_LIST], 96, 210, 1728, 300, size=24))
o.append(term([("$", P_TI, "gh pr view 2")] + [("m" if i == 1 else "o", l, "", "") if i == 1 else ("o", l) for i, l in enumerate(PR_VIEW)], 96, 540, 1728, 410, tid="t-view", size=21, attrs=' data-build-in="rise order 1"'))
W("pr-view", o, "gh pr list는 열린 PR 목록이에요. #2가 PR 번호예요. 이슈 #1 다음이라 2번이 됐어요. GitHub은 이슈와 PR 번호를 같이 세요. gh pr view 2는 2번 PR의 제목, 상태, 내용을 보여 줘요. 노란 줄은 kim이 feature/kim-hobby의 커밋 1개를 main에 합치고 싶어 한다는 뜻이에요. 웹에서 보고 싶으면 gh pr view 2 --web을 쳐요.")

o = [sec("pr-merge")] + head(EB5, "gh pr merge · 합치고 main 받아 오기", OR)
o.append(term([("$", P_TI, "gh pr merge 2 --merge"), ("g", PR_MERGED), ("$", P_TI, "git checkout main")] + [("o", l) for l in CO_MAIN] + [("$", P_TI, "git pull origin main"), ("d", "…")] + [("o", l) for l in PULL[2:5]],
              96, 220, 1000, 450, size=21))
o.append(term([("$", P_TI, "git log --oneline")] + [("m", re.sub(r" \(.*?\)", "", LOG_AFTER[0]), "", "")] + [("o", re.sub(r" \(.*?\)", "", l)) for l in LOG_AFTER[1:]],
              1130, 220, 694, 230, tid="t-log", size=17, attrs=' data-build-in="rise order 1"'))
o.append(card("--merge = Create a merge commit", "08에서 본 PR Merge 버튼 세 가지 중 첫째예요. squash, rebase 옵션도 있으니 팀이 정한 방식을 써요.", 1130, 480, 694, 190, OR, ' data-build-in="rise order 2"', tsize=26, bsize=22))
o.append(caption("합친 뒤에는 지금까지처럼 git pull origin main으로 받아 와요.", 730))
W("pr-merge", o, "리뷰가 끝난 PR은 gh pr merge로 합쳐요. --merge는 08에서 본 PR Merge 버튼 세 가지 중 Create a merge commit과 같아요. --squash, --rebase 옵션도 있으니 팀이 정한 방식을 골라요. 합친 것은 GitHub의 main이라 내 컴퓨터는 아직 그대로예요. git checkout main, git pull origin main으로 받아 와요. pull 출력은 위쪽 받는 과정을 …로 줄였어요. 오른쪽 git log 맨 위에 Merge pull request #2 커밋이 생겼어요. 화면에 맞추려고 이름표 괄호는 줄였어요.")

o = [sec("help")] + head(EB5, "다른 명령은 gh --help에서 찾아요", OR)
o.append(term([("$", P_HOME, "gh --help")] + [("m", l, "", "") if l.split(":")[0].strip() in ("auth", "browse", "issue", "pr", "repo") and l.startswith("  ") else ("d", l) if l == "  …" else ("o", l) for l in GH_HELP],
              96, 220, 1240, 680, size=21))
o.append(box(p(f"font-size:26px;font-weight:700;color:{INK}", "오늘 쓴 묶음") + p(f"font-family:{MONO};font-size:28px;font-weight:700;line-height:1.6;color:{OR}", "auth  browse<br>issue  pr  repo"),
             1380, 220, 444, 250, ' data-build-in="rise order 1"', top_color=OR))
o.append(box(p(f"font-size:26px;font-weight:700;color:{INK}", "한 단계 더 보기") + p(f"font-family:{MONO};font-size:24px;font-weight:700;line-height:1.6;color:{INK}", "gh repo --help<br>gh pr create --help"),
             1380, 510, 444, 250, ' data-build-in="rise order 2"'))
W("help", o, "gh --help는 gh의 명령 묶음 목록이에요. 노란 줄이 오늘 쓴 다섯 묶음이에요. 출력은 tools/demo.sh에서 실제로 실행한 결과고 아래쪽은 …로 줄였어요. 묶음 이름 뒤에 --help를 붙이면 그 안의 할 일 목록이, 할 일 뒤에 붙이면 옵션 목록이 나와요. 번외 터미널 환경에 적응하기의 도움말 읽는 법이 gh에도 그대로 통해요.")

# ---------- summary ----------
EB6 = "정리"
o = [sec("trouble")] + head(EB6, "gh에서 막히면", RED)
tr = [("gh: command not found", "설치 직후 터미널이 gh를 몰라요", "터미널 껐다 켜기"), ("You are not logged into any GitHub hosts", "아직 로그인 전이에요", "gh auth login"),
      ('needs the "delete_repo" scope', "지우기 권한이 없어요", "gh auth refresh -h github.com -s delete_repo"),
      ("failed to run git: fatal: not a git repository", "레포 폴더 밖에서 쳤어요", "pwd 뒤 cd 레포 폴더"),
      ("Where should we push the 'feature/…' branch?", "브랜치를 push하기 전에 PR을 만들었어요", "Ctrl+C 뒤 git push origin 브랜치"),
      ("브라우저가 안 열려요", "주소를 직접 열어요", "github.com/login/device")]
o.append('<div style="position:absolute;left:96px;top:210px;width:1728px;height:780px;display:flex;flex-direction:column;gap:14px">')
for i, (q, a_, cmd) in enumerate(tr, 1):
    mono = q.isascii()
    o.append(f'<div data-build-in="rise order {i}" style="flex:1;display:flex;flex-direction:row;gap:26px;align-items:center;background:{CARD};border:2px solid {LINE};border-radius:18px;padding:8px 30px">'
             + num(i, RED, 36)
             + '<div style="flex:1;display:flex;flex-direction:column;gap:4px">' + p(f"{'font-family:' + MONO + ';font-size:23px;' if mono else 'font-size:27px;'}font-weight:700;color:{INK}", e(q)) + p(f"font-size:23px;color:{SUB}", e(a_)) + '</div>'
             + p(f"width:{620 if i == 3 else 440}px;flex:none;font-family:{MONO};font-size:{20 if i == 3 else 22}px;font-weight:700;line-height:1.5;color:{INK};background:#EEEFF2;padding:10px 18px;border-radius:12px;white-space:nowrap", e(cmd)) + '</div>')
o.append('</div>')
W("trouble", o, "1번은 설치 직후 자주 나요. 터미널을 껐다 켜면 새로 설치한 gh를 찾아요. 2번은 로그인 전이라는 뜻이에요. 3번은 4파트에서 본 권한 에러예요. 4번은 레포 폴더 밖에서 gh repo view, gh pr list처럼 지금 레포를 쓰는 명령을 쳤을 때예요. pwd로 위치를 보고 레포 폴더로 들어가요. 5번은 브랜치를 push하기 전에 gh pr create를 쳤을 때 나오는 질문이에요. Ctrl+C로 멈추고 git push origin 브랜치이름을 친 뒤 다시 해요. 6번은 브라우저가 저절로 안 열릴 때예요. 터미널의 코드를 보고 주소를 직접 열어요. 4번은 실제로 (or any of the parent directories): .git이 뒤에 더 붙어요. 5번 질문의 선택지 중 Cancel을 골라도 멈춰요.", ("trouble", "정리"))

o = [f'<section id="cheatsheet" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};font-variant-ligatures:none;padding:96px;display:flex;flex-direction:column">',
     f'<h2 style="position:absolute;left:96px;top:72px;font-size:64px;font-weight:700;line-height:1.15;color:{INK}">한 장 요약</h2>']
groups = [("로그인", BL, [("gh auth login", "로그인"), ("gh auth status", "로그인 상태, 권한"), ("gh auth refresh -s 권한", "권한 더하기")]),
          ("레포", GR, [("gh repo clone 주인/이름", "받기"), ("gh repo view", "지금 레포 보기"), ("gh repo list", "내 레포 목록"), ("gh repo create 이름 …", "만들기"), ("gh repo delete 주인/이름", "지우기")]),
          ("이슈와 PR", OR, [("gh issue create", "이슈 만들기"), ("gh issue list", "이슈 목록"), ("gh pr create", "PR 만들기"), ("gh pr list / view", "PR 보기"), ("gh pr merge 번호", "PR 합치기")])]
for i, (t, c, rows) in enumerate(groups):
    x = 96 + i * 584
    inner = p(f"font-size:30px;font-weight:700;color:{c}", e(t)) + "".join(
        '<div style="display:flex;flex-direction:column;gap:2px">' + p(f"font-family:{MONO};font-size:24px;font-weight:700;color:{INK}", e(k)) + p(f"font-size:22px;color:{SUB}", e(d)) + '</div>' for k, d in rows)
    o.append(box(inner, x, 190, 560, 620, "", top_color=c, gap=18))
o.append(box(p(f"font-size:30px;font-weight:700;color:{INK}", "커밋과 push는 git으로, 웹 버튼은 gh로 해요.")
             + p(f"font-size:26px;color:{SUB}", "레포 지우기는 되돌릴 수 없어요. 지우기 전에 주인/이름을 한 번 더 확인해요."),
             96, 840, 1728, 150, "", pad="20px 36px", gap=8, extra="justify-content:center"))
W("cheatsheet", o, "오늘 쓴 명령을 세 묶음으로 모았어요. 로그인 세 개, 레포 다섯 개, 이슈와 PR 다섯 개예요. 커밋과 push, pull은 계속 git으로 하고, 웹사이트에서 누르던 버튼은 gh로 해요. 다음 수업부터 팀 레포를 만들 때 gh repo create로 시작해 봐요.")

# ---------- toc ----------
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
parts = [("Key", BL, "설치하고 로그인하기", "gh auth login, 권한 목록, git도 같이 로그인", "install", "gitcred"),
         ("Link", GR, "이미 있는 레포 연결하기", "gh repo clone, view, browse, list", "clone", "repo-list"),
         ("Star", TEAL, "새 레포 만들기", "gh repo create 뒤 git push origin main", "create-why", "create-ask"),
         ("Warning", RED, "레포 지우기와 권한 추가", "delete가 막힐 때 gh auth refresh", "del-warn", "del-ok"),
         ("Tool", OR, "자주 쓰는 gh 명령", "이슈, PR 만들기와 합치기", "issue", "help")]
t = [f'<section id="toc" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};word-break:keep-all;padding:96px 96px;display:flex;flex-direction:column;gap:40px">',
     f'<h2 style="font-size:64px;font-weight:700;line-height:1.15;color:{INK}">오늘의 순서</h2>',
     '<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:24px;flex:1">']
for i, (ic, c, h, s_, a, b) in enumerate(parts, 1):
    pg = f"{page[a]}–{page[b]}쪽"
    t.append(f'<div style="display:flex;flex-direction:column;gap:12px;background:#FFFFFF;border:2px solid {LINE};border-top:10px solid {c};border-radius:20px;padding:28px 28px">'
             f'<div style="display:flex;flex-direction:row;gap:14px;align-items:center"><p style="font-size:52px;font-weight:900;line-height:1.25;color:{c}">{i}</p>'
             f'<x-icon name="{ic}" style="width:44px;height:44px;color:{c}"></x-icon></div>'
             f'<h3 style="font-size:32px;font-weight:700;line-height:1.3;color:{INK}">{h}</h3>'
             f'<p style="font-size:24px;line-height:1.45;color:{SUB}">{e(s_)}</p><div style="flex:1"></div>'
             f'<p style="font-size:24px;color:#6A7180">{pg}</p></div>')
t += ['</div>', f'<p style="font-size:26px;color:{SUB}">{page["why"]}–{page["map"]}쪽은 들어가기, {page["trouble"]}–{page["cheatsheet"]}쪽은 막힐 때와 한 장 요약이에요.</p>']
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(t) + f"\n<aside>{e('다섯 파트로 나눴어요. 1파트에서 한 번 로그인해 두면 나머지는 모두 그 로그인을 써요. 2파트는 06의 team-intro를, 3파트와 4파트는 새로 만드는 연습용 레포 my-notes를 써요. 5파트는 다시 team-intro로 돌아와요.')}</aside>\n</section>\n")

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-02T02:00:00Z"}, "lists": "css", "title": "터미널에서 GitHub 다루기", "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
print(len(ORDER), "slides")
