"""Generates every slide of the gh CLI deck (11) and slides/deck.json.

Story: kim installs gh, logs in with the browser code, clones team-intro (from 06),
makes a new repo my-notes from a local folder, fails to delete it until the delete_repo
scope is added with gh auth refresh, and ends with issue and PR commands on team-intro.
Terminal output comes from tools/demo.sh (gh 2.89.0 and git 2.43 run for real against
tools/mock_github.py, a small stand-in for github.com). The saved run is tools/demo-output.txt.

Layout: the terminal is the one big object on most slides. It is sized to its lines, and what a line
means is said by a small colored tag on that line (dot, short leader, pill), not by cards below it.
Browser windows are drawn as satellites that overlap the terminal's edge.
Usage (in 11-gh-cli): python3 tools/gen.py slides
"""
import html, json, os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from highlight import (spot, spot_off, cursor, cursor_off, ring, box as pen_box, underline,  # noqa: E402
                       SLAM, SLIDE, DIM, DELAY, PATH, pulse, shine, shake, zoom, zoom_off)

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT):
    if f.endswith(".html"):
        os.remove(os.path.join(OUT, f))
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
BG, INK, SUB, LINE, CARD = "#F6F5F1", "#1D2330", "#4A5262", "#DCD8CE", "#FFFFFF"
BL, GR, OR, PUR, RED, TEAL, GRAY = "#2459C9", "#1F8A4C", "#B26A00", "#5A3BB8", "#A33131", "#0F7C86", "#5B6270"
T_BG = "#1B2029"
TCOL = {"o": "#D8DEE9", "e": "#FF9C94", "g": "#7FD18B", "d": "#7D8696", "y": "#F2C46D", "sel": "#7FD18B", "c": "#7D8696"}
GH = PUR   # GitHub color in every deck
SHADOW = "0 18px 40px rgba(29,35,48,.16), 0 2px 6px rgba(29,35,48,.08)"
WARN = []


def e(s):
    return html.escape(s, quote=False)


def p(style, text, attrs=""):
    return f'<p{attrs} style="{style}">{text}</p>'


def tw(s, size, mono=True):
    """Width estimate in px. JetBrains Mono is 0.6em; Hangul falls back to Noto Sans KR at 0.92em."""
    w = 0.0
    for c in s:
        o = ord(c)
        if 0xAC00 <= o <= 0xD7A3 or 0x3130 <= o <= 0x318F:
            w += 0.92
        elif mono:
            w += 0.6
        elif c == " ":
            w += 0.25
        elif c.isupper() or c.isdigit():
            w += 0.64
        else:
            w += 0.54
    return w * size


def bi(kind, order):
    return f' data-build-in="{kind} order {order}"' if order else ""


ORDER, SECTIONS = [], {}


def W(sid, parts, notes, section=None):
    if section:
        SECTIONS[section[0]] = {"description": section[1], "start": sid}
    ORDER.append(sid)
    with open(os.path.join(OUT, sid + ".html"), "w") as f:
        f.write("\n".join(parts) + f"\n<aside>{e(notes)}</aside>\n</section>\n")


def frame(sid, eyebrow, title, color, transition="fade"):
    return [f'<section id="{sid}" data-transition="{transition}" style="background:{BG};color:{INK};font-family:{SANS};font-variant-ligatures:none;word-break:keep-all;padding:96px">',
            p(f"position:absolute;left:96px;top:48px;width:1728px;font-size:26px;font-weight:700;color:{color}", e(eyebrow), ' id="eyebrow"'),
            f'<h2 id="title" style="position:absolute;left:96px;top:92px;width:1728px;font-size:52px;font-weight:700;line-height:1.2;color:{INK}">{title}</h2>']


def caption(text, top, order=None, left=96, width=1728, size=32, color=INK):
    return p(f"position:absolute;left:{left}px;top:{top}px;width:{width}px;font-size:{size}px;font-weight:700;line-height:1.45;color:{color}", text, bi("rise", order))


def cmd(text):
    """inline command in body text"""
    return f'<span style="font-family:{MONO};font-weight:700">{e(text)}</span>'


def mark(text, marks):
    """wrap the first match of each key of marks in <span id=...>"""
    out, rest = "", text
    hits = sorted(((text.find(k), k, v) for k, v in marks.items() if k in text), key=lambda t: t[0])
    pos = 0
    for at, k, v in hits:
        if at < pos:
            continue
        out += e(text[pos:at]) + f'<span id="{v}">{e(k)}</span>'
        pos = at + len(k)
    out += e(text[pos:])
    return out.replace("  ", " &#160;") if out else "&#160;"


# ---------- terminal ----------
class Term:
    PT, PX, BAR = 24, 34, 36   # top/bottom padding, side padding, dots row + gap

    def __init__(self, lines, x, y, size=28, w=None, lh=1.5, tid="term", attrs="", room=0, bar=True, bleed=False):
        self.x, self.y, self.size, self.tid, self.attrs = x, y, size, tid, attrs
        self.lp = round(size * lh)
        self.bar = self.BAR if bar else 0
        self.rows = [self._row(l) for l in lines]
        self.tws = [tw(r[1], size) for r in self.rows]
        self.w = w or round(max(self.tws) + 2 * self.PX + room)
        self.h = round(2 * self.PT + self.bar + len(self.rows) * self.lp)
        self.inner = []
        self.bleed = bleed
        if x + self.w > 1824 and not bleed:
            WARN.append(f"{tid}: terminal right edge {x + self.w}")

    def _row(self, l):
        kind = l[0]
        marks = l[-1] if isinstance(l[-1], dict) else {}
        if kind == "$":
            path, c = l[1], l[2]
            return kind, f"{path} $ {c}", f'<span style="color:#8FB3FF">{e(path)} $</span> ' + mark(c, marks), "#F2C46D"
        t = l[1].replace("\t", "    ")
        return kind, t, mark(t, marks), TCOL[kind]

    tx = property(lambda s: s.x + s.PX)

    def top(self, i):
        return self.y + self.PT + self.bar + i * self.lp

    def cy(self, i):
        return self.top(i) + self.lp / 2

    def end(self, i):
        return self.tx + self.tws[i]

    def sx(self, i, sub):
        t = self.rows[i][1]
        return self.tx + tw(t[:t.index(sub)], self.size)

    def sw(self, sub):
        return tw(sub, self.size)

    def band(self, i, j=None, order=None, color="rgba(242,196,109,.17)"):
        j = i if j is None else j
        self.inner.append(f'<div{bi("fade", order)} style="position:absolute;left:{self.PX - 12}px;top:{self.PT + self.bar + i * self.lp:.0f}px;width:{self.w - 2 * self.PX + 24}px;height:{(j - i + 1) * self.lp:.0f}px;background:{color};border-radius:8px"></div>')

    def html(self):
        o = [f'<div id="{self.tid}"{self.attrs} style="position:absolute;left:{self.x}px;top:{self.y}px;width:{self.w}px;height:{self.h}px;background:{T_BG};border-radius:18px;padding:{self.PT}px {self.PX}px;font-family:{MONO};font-variant-ligatures:none;overflow:hidden;box-shadow:0 10px 30px rgba(29,35,48,.12)">']
        if self.bar:
            o.append('<div style="display:flex;flex-direction:row;gap:10px;height:16px;margin-bottom:20px">'
                     + "".join(f'<div style="width:16px;height:16px;border-radius:8px;background:{c}"></div>' for c in ("#F28B82", "#F2C46D", "#7FD18B")) + '</div>')
        o += self.inner
        for kind, _, h, col in self.rows:
            wt = "font-weight:700;" if kind in ("$", "sel") else ""
            o.append(p(f"position:relative;font-size:{self.size}px;line-height:{self.lp:.0f}px;height:{self.lp:.0f}px;white-space:pre;{wt}color:{col}", h))
        o.append('</div>')
        return "".join(o)


def tag(t, i, text, color, order=None, at=None, gap=44, dark=True):
    """A pill on terminal line i: dot right after the text, a short leader, then the words."""
    x0 = at if at is not None else t.end(i)
    cy = t.cy(i)
    pw = tw(text, 23, mono=False) + 30
    px = x0 + gap
    if px + pw > t.x + t.w - 14:
        WARN.append(f"{t.tid}: tag '{text}' ends at {px + pw:.0f}, terminal ends {t.x + t.w}")
    lc = {BL: "#6F9BF5", GR: "#5CC287", OR: "#E3A84A", RED: "#F07A72", TEAL: "#4FB8C2", GRAY: "#9AA3B5", PUR: "#A78BF2"}.get(color, color)
    return [f'<div{bi("fade", order)} style="position:absolute;left:{x0 + 12:.0f}px;top:{cy - 5:.0f}px;width:{gap - 12:.0f}px;height:10px">'
            f'<div style="position:absolute;left:0;top:0;width:10px;height:10px;border-radius:5px;background:{lc}"></div>'
            f'<div style="position:absolute;left:10px;top:4px;width:{gap - 22:.0f}px;height:2px;background:{lc}"></div></div>',
            p(f"position:absolute;left:{px:.0f}px;top:{cy - 20:.0f}px;height:40px;padding:0 15px;border-radius:10px;background:{color};font-family:{SANS};font-size:23px;font-weight:700;line-height:40px;color:#FFFFFF;white-space:nowrap", e(text), bi("pop", order))]


def kbd(x, y, text, order=None):
    return p(f"position:absolute;left:{x:.0f}px;top:{y:.0f}px;height:42px;padding:0 16px;border-radius:9px;background:#FFFFFF;border:2px solid #C9CED8;border-bottom-width:5px;font-family:{SANS};font-size:23px;font-weight:700;line-height:36px;color:{INK};white-space:nowrap", e(text), bi("pop", order))


# ---------- browser window (simplified GitHub page) ----------
def browser(x, y, w, h, url, inner, bid, attrs="", pad="28px 40px", align="center"):
    return (f'<div id="{bid}"{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:{CARD};border:1px solid #D2CEC4;border-radius:16px;overflow:hidden;box-shadow:{SHADOW};display:flex;flex-direction:column">'
            '<div style="height:52px;flex:none;background:#EEECE6;display:flex;flex-direction:row;align-items:center;gap:9px;padding:0 18px">'
            + "".join('<div style="width:13px;height:13px;border-radius:7px;background:#C9CED8"></div>' for _ in range(3))
            + p(f"margin-left:14px;font-family:{SANS};font-size:20px;font-weight:500;color:{SUB};background:#FFFFFF;border-radius:9px;padding:4px 16px;white-space:nowrap", e(url))
            + '</div>'
            f'<div style="flex:1;display:flex;flex-direction:column;align-items:{align};justify-content:center;gap:22px;padding:{pad}">{inner}</div></div>')


def gh_button(text, bid=None, color=GR, size=24):
    i = f' id="{bid}"' if bid else ""
    return p(f"font-size:{size}px;font-weight:700;color:#FFFFFF;background:{color};border-radius:10px;padding:10px 30px;white-space:nowrap", e(text), i)


def code_boxes(codestr, size=36, bid=None, attrs=""):
    cells = []
    for ch in codestr:
        if ch == "-":
            cells.append(p(f"font-family:{MONO};font-size:{size}px;font-weight:700;color:{GRAY}", "-"))
        else:
            cells.append(p(f"width:{size + 10}px;height:{size + 24}px;border:2px solid #B4B9C3;border-radius:8px;font-family:{MONO};font-size:{size}px;font-weight:700;line-height:{size + 20}px;text-align:center;color:{INK}", e(ch)))
    i = f' id="{bid}"' if bid else ""
    return f'<div{i}{attrs} style="display:flex;flex-direction:row;gap:7px;align-items:center">' + "".join(cells) + '</div>'


# ---------- a command taken apart: colored pieces with labels under them ----------
def parts(x, y, segs, size=48, order=None, lab=24, drop=34, stagger=False, sep=1):
    """segs: (text, color, label or None, id or None). Pieces are joined by one space."""
    o, cx = [], x
    spans = []
    for k, (t, c, label, sid) in enumerate(segs):
        w = tw(t, size)
        i = f' id="{sid}"' if sid else ""
        spans.append(f'<span{i} style="color:{c}">{e(t)}</span>')
        if label:
            ord_ = (order + k) if (order and stagger) else order
            mid = cx + w / 2
            o.append(f'<div{bi("fade", ord_)} style="position:absolute;left:{mid - 1:.0f}px;top:{y + size * 1.3 + 4:.0f}px;width:2px;height:{drop}px;background:{c}"></div>')
            o.append(p(f"position:absolute;left:{mid - 210:.0f}px;top:{y + size * 1.3 + drop + 10:.0f}px;width:420px;text-align:center;font-size:{lab}px;font-weight:700;line-height:1.35;color:{c}", label, bi("pop", ord_)))
        cx += w + tw(" " * sep, size)
    o.insert(0, p(f"position:absolute;left:{x}px;top:{y}px;font-family:{MONO};font-size:{size}px;font-weight:700;line-height:1.3;white-space:pre", (" " * sep).join(spans)))
    return o


def chip(text, color, bg, cid=None, attrs="", size=30, w=None, dashed=False):
    i = f' id="{cid}"' if cid else ""
    bd = f"border:3px dashed {color}" if dashed else f"border:3px solid {color}"
    ww = f"width:{w}px;" if w else ""
    return p(f"{ww}height:84px;flex:none;padding:0 26px;border-radius:14px;background:{bg};{bd};font-family:{MONO};font-size:{size}px;font-weight:700;line-height:78px;text-align:center;color:{color};white-space:nowrap", e(text), i + attrs)


def badge(x, y, chips, title="출입증 (토큰)", w=1728, bid="badge", attrs=""):
    """The token drawn as a pass with one chip per scope. chips: html strings."""
    return (f'<div id="{bid}"{attrs} style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:200px;background:{CARD};border:1px solid {LINE};border-radius:22px;box-shadow:0 2px 0 rgba(29,35,48,.04);padding:22px 36px;display:flex;flex-direction:column;gap:18px">'
            f'<div style="display:flex;flex-direction:row;gap:12px;align-items:center"><x-icon name="Key" style="width:30px;height:30px;color:{BL}"></x-icon>'
            + p(f"font-size:26px;font-weight:700;color:{SUB}", e(title)) + '</div>'
            f'<div style="display:flex;flex-direction:row;gap:20px;align-items:center">{"".join(chips)}</div></div>')


SC = [("repo", "레포 읽고 쓰기"), ("read:org", "조직 보기"), ("gist", "메모 조각"), ("workflow", "Actions 설정")]


def svg(inner, order=None, kind="draw"):
    return (f'<svg{bi(kind, order)} viewBox="0 0 1920 1080" style="position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none;overflow:visible">{inner}</svg>')


def arrow_path(d, color, width=5, dash=None, head=True):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"{da}/>')


def head_at(x, y, ang, color, size=18):
    import math
    a = math.radians(ang)
    p1 = (x - size * math.cos(a - 0.45), y - size * math.sin(a - 0.45))
    p2 = (x - size * math.cos(a + 0.45), y - size * math.sin(a + 0.45))
    return f'<path d="M{p1[0]:.0f},{p1[1]:.0f} L{x:.0f},{y:.0f} L{p2[0]:.0f},{p2[1]:.0f}" fill="none" stroke="{color}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'


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
LIST_HEAD = ["", "Showing 2 of 2 repositories in @kim", "", "NAME            DESCRIPTION  INFO    UPDATED"]
LIST2 = LIST_HEAD + ["kim/hello-git                public  about 3 minutes ago", "kim/team-intro               public  about 3 minutes ago"]
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
PUSH_HB_LAST = " * [new branch]      feature/kim-hobby -> feature/kim-hobby"
PR_NEW = ["", "Creating pull request for feature/kim-hobby into main in kim/team-intro", "", "https://github.com/kim/team-intro/pull/2"]
PR_LIST = ["", "Showing 1 of 1 open pull request in kim/team-intro", "", "ID  TITLE                BRANCH             CREATED AT", "#2  feat: kim 취미 추가  feature/kim-hobby  less than a minute ago"]
PR_VIEW = ["feat: kim 취미 추가 kim/team-intro#2", "Open • kim (kim) wants to merge 1 commit into main from feature/kim-hobby • less than a minute ago",
           "+1 -0 • No checks", "", "", "  kim.md에 취미를 적었어요", "", "", "View this pull request on GitHub: https://github.com/kim/team-intro/pull/2"]
PR_MERGED = "✓ Merged pull request kim/team-intro#2 (feat: kim 취미 추가)"
CO_MAIN = ["Switched to branch 'main'", "Your branch is up to date with 'origin/main'."]
PULL = ["From https://github.com/kim/team-intro", " * branch            main       -> FETCH_HEAD", "   1baff03..5487d25  main       -> origin/main",
        "Updating 1baff03..5487d25", "Fast-forward", " kim.md | 1 +", " 1 file changed, 1 insertion(+)"]
LOG_AFTER = ["5487d25 Merge pull request #2 from kim/feature/kim-hobby", "8039736 feat: kim 취미 추가", "1baff03 feat: kim 소개 추가", "a2a187e docs: README 추가"]
GH_HELP = ["Work seamlessly with GitHub from the command line.", "", "USAGE", "  gh <command> <subcommand> [flags]", "", "CORE COMMANDS",
           "  auth:          Authenticate gh and git with GitHub", "  browse:        Open repositories, issues, pull requests, and more in the browser",
           "  codespace:     Connect to and manage codespaces", "  gist:          Manage gists", "  issue:         Manage issues",
           "  org:           Manage organizations", "  pr:            Manage pull requests", "  project:       Work with GitHub Projects.",
           "  release:       Manage releases", "  repo:          Manage repositories", "  …"]

P_HOME, P_KANT, P_TI, P_MN = "~", "~/kant", "~/kant/team-intro", "~/kant/my-notes"
MADE = "출력은 tools/demo.sh로 실제 gh를 실행한 결과예요."

# ---------- cover ----------
cov = [f'<section id="cover" data-transition="fade" style="background:{INK};color:#F6F5F1;font-family:{SANS};font-variant-ligatures:none;padding:128px">',
       p("position:absolute;left:128px;top:300px;font-size:28px;font-weight:700;color:#F2B27A", "KANT AX/AI 엔지니어 트랙 · 11"),
       f'<h1{SLAM(1)} style="position:absolute;left:128px;top:360px;font-size:100px;font-weight:900;line-height:1.15;color:#F6F5F1">터미널에서<br>GitHub 다루기</h1>',
       p("position:absolute;left:128px;top:630px;font-size:40px;line-height:1.4;color:#BFC6D4", "gh로 로그인하고<br>레포 만들고 지우기")]
t = Term([("$", P_HOME, "gh auth login"), ("g", "✓ Logged in as kim"), ("o", ""), ("$", P_KANT, "gh repo clone kim/team-intro"), ("o", CLONE[0])],
         1060, 330, size=30, w=980, tid="cov-term", bleed=True)
cov.append(t.html())
cov.append(shine(2, "cov-term"))
W("cover", cov, "11 챕터는 GitHub 공식 터미널 도구 gh(GitHub CLI)를 다뤄요. 지금까지 레포 만들기, PR 만들기는 GitHub 웹사이트에서 버튼으로 했어요. 오늘은 같은 일을 터미널에서 해요. 로그인부터 시작해서 레포를 받고, 만들고, 지워요. 지울 때 권한이 모자라서 막히는 장면도 일부러 넣었어요. 마지막에는 이슈와 PR을 다루는 명령을 봐요.", ("intro", "들어가기"))

ORDER.append("toc")   # written last, after page numbers are known

# ---------- why: the trip to the browser ----------
o = frame("why", "들어가기", "push는 터미널에서, PR 버튼은 브라우저에서 눌렀어요", INK)
t = Term([("$", P_TI, "git push origin feature/kim-hobby"), ("d", "…"), ("o", PUSH_HB_LAST)], 96, 214, size=26, tid="t-push")
o.append(t.html())
rows = "".join(
    f'<div style="display:flex;flex-direction:row;align-items:center;gap:18px;height:68px;border-top:1px solid #E6E2D9;padding:0 26px">'
    f'<x-icon name="Book" style="width:26px;height:26px;color:#9AA3B5"></x-icon>' + p(f"font-family:{MONO};font-size:26px;color:{INK}", n)
    + f'<div style="margin-left:auto;width:{bw}px;height:12px;border-radius:6px;background:#E4E1DA"></div></div>'
    for n, bw in (("README.md", 260), ("kim.md", 190)))
inner = (f'<div style="width:100%;display:flex;flex-direction:row;gap:34px;align-items:flex-end;border-bottom:1px solid #E6E2D9;padding:0 6px">'
         + "".join(p(f"font-size:26px;font-weight:{700 if k == 0 else 500};color:{INK if k == 0 else SUB};padding:0 4px 14px;{'border-bottom:4px solid #F28B5A;' if k == 0 else ''}", n) for k, n in enumerate(["Code", "Issues", "Pull requests", "Settings"]))
         + '</div>'
         f'<div style="width:100%;display:flex;flex-direction:row;align-items:center;gap:20px;background:#FFF8E1;border:1px solid #F0D98A;border-radius:12px;padding:20px 26px">'
         + p(f"font-family:{MONO};font-size:26px;font-weight:700;color:{INK}", "feature/kim-hobby")
         + p(f"font-size:26px;color:{SUB}", "had recent pushes")
         + '<div style="margin-left:auto">' + gh_button("Compare & pull request", "btn-compare", size=26) + '</div></div>'
         f'<div style="width:100%;border:1px solid #E6E2D9;border-radius:12px;overflow:hidden">'
         + p(f"height:64px;padding:0 26px;font-size:24px;font-weight:700;line-height:64px;color:{SUB};background:#F7F6F2", "kim · feat: kim 소개 추가")
         + rows + '</div>')
o.append(browser(96, 460, 1900, 680, "github.com/kim/team-intro", inner, "br-repo", pad="30px 160px 30px 44px", align="stretch").replace("justify-content:center;gap:22px", "justify-content:flex-start;gap:26px"))
o.append(cursor(1, target="btn-compare"))
mini = Term([("$", P_TI, "gh pr create")], 1180, 214, size=26, w=644, tid="t-gh", attrs=SLIDE(2, 300, 0))
o.append(mini.html())
o.append(caption("오늘은 이 버튼도 터미널에서 눌러요.", 214 + mini.h + 20, 2, left=1180, width=644, size=28, color=OR))
o.append(cursor_off(2))
W("why", o, "03에서 브랜치를 push한 뒤에는 브라우저로 넘어갔어요. GitHub 레포 화면에 뜬 Compare & pull request 버튼을 눌러서 PR을 열었어요. 레포를 만들 때도, 이슈를 만들 때도 터미널을 두고 브라우저로 갔어요. gh를 쓰면 같은 버튼을 터미널에서 명령으로 눌러요. 브라우저 화면은 버튼 위치만 보이게 단순하게 그렸어요.")

# ---------- big picture ----------
o = frame("big", "들어가기", "git은 커밋을 주고받고, gh는 웹 버튼을 맡아요", INK)
o.append(f'<x-icon name="Home" style="position:absolute;left:96px;top:222px;width:28px;height:28px;color:{GRAY}"></x-icon>')
o.append(p(f"position:absolute;left:134px;top:218px;font-size:26px;font-weight:700;color:{GRAY}", "내 컴퓨터"))
o.append(f'<div style="position:absolute;left:96px;top:262px;width:600px;height:2px;background:#CDD0D6"></div>')
o.append(f'<x-icon name="Globe" style="position:absolute;left:1224px;top:222px;width:28px;height:28px;color:{GH}"></x-icon>')
o.append(p(f"position:absolute;left:1262px;top:218px;font-size:26px;font-weight:700;color:{GH}", "GitHub"))
o.append(f'<div style="position:absolute;left:1224px;top:262px;width:600px;height:2px;background:#C9BCF2"></div>')
o.append(f'<div style="position:absolute;left:96px;top:300px;width:600px;height:400px;background:{T_BG};border-radius:22px;padding:28px 40px">'
         '<div style="display:flex;flex-direction:row;gap:10px;height:16px">' + "".join(f'<div style="width:16px;height:16px;border-radius:8px;background:{c}"></div>' for c in ("#F28B82", "#F2C46D", "#7FD18B")) + '</div>'
         + p("position:absolute;left:40px;top:64px;font-size:24px;font-weight:700;color:#9AA3B5", "터미널")
         + p(f"position:absolute;left:40px;top:120px;font-family:{MONO};font-size:72px;font-weight:700;line-height:1.2;color:#8FB3FF", "git")
         + p("position:absolute;left:40px;top:212px;font-size:24px;color:#C9D1DF", "02부터 써 온 기록 도구")
         + p(f"position:absolute;left:40px;top:268px;font-family:{MONO};font-size:72px;font-weight:700;line-height:1.2;color:#F2C46D", "gh")
         + p("position:absolute;left:40px;top:358px;font-size:24px;color:#C9D1DF", "오늘 배울 GitHub 도구") + '</div>')
o.append(f'<div style="position:absolute;left:1224px;top:300px;width:600px;height:400px;background:#F0EBFD;border-radius:22px"></div>')
o.append(p(f"position:absolute;left:1264px;top:340px;font-size:24px;font-weight:700;color:#5A4A8F", "kim/team-intro"))
o.append(f'<div style="position:absolute;left:1264px;top:392px;width:520px;height:112px;background:#FFFFFF;border-radius:16px;padding:18px 26px">'
         + p(f"font-size:30px;font-weight:700;color:{GH}", "저장소") + p(f"font-size:23px;color:{SUB}", "커밋 기록") + '</div>')
o.append(f'<div style="position:absolute;left:1264px;top:540px;width:520px;height:112px;background:#FFFFFF;border-radius:16px;padding:18px 26px">'
         + p(f"font-size:30px;font-weight:700;color:{GH}", "웹 버튼") + p(f"font-size:23px;color:{SUB}", "레포 만들기, PR, 이슈, 레포 지우기") + '</div>')
# arrows
g1 = arrow_path("M700,436 L1250,436", BL) + head_at(1252, 436, 0, BL) + arrow_path("M1250,470 L700,470", BL, dash="1 12") + head_at(698, 470, 180, BL)
o.append(svg(g1, 1))
o.append(svg('<path id="p-push" d="M700,436 L1240,436" fill="none" stroke="none"/><path id="p-gh" d="M700,596 L1240,596" fill="none" stroke="none"/>'))
o.append(f'<div{PATH(1, "p-push")} style="position:absolute;left:1222px;top:418px;width:36px;height:36px;border-radius:18px;background:{BL};border:4px solid #FFFFFF;box-shadow:0 2px 6px rgba(0,0,0,.18)"></div>')
o.append(p(f"position:absolute;left:760px;top:380px;width:440px;text-align:center;font-size:26px;font-weight:700;color:{BL}", "push, pull로 커밋 주고받기", bi("fade", 1)))
# browser path (old way)
o.append(f'<div style="position:absolute;left:760px;top:800px;width:400px;height:110px;background:#FFFFFF;border:1px solid {LINE};border-radius:16px;display:flex;flex-direction:row;gap:16px;align-items:center;padding:0 28px">'
         f'<x-icon name="Globe" style="width:34px;height:34px;color:{GRAY}"></x-icon>' + p(f"font-size:28px;font-weight:700;color:{SUB}", "브라우저") + '</div>')
g2 = arrow_path("M1160,855 C1300,855 1460,800 1490,668", GRAY, dash="2 14") + head_at(1492, 664, -80, GRAY)
o.append(svg(g2, 2))
o.append(p(f"position:absolute;left:1300px;top:860px;width:520px;font-size:26px;font-weight:700;color:{GRAY}", "지금까지는 마우스로 눌렀어요", bi("fade", 2)))
g3 = arrow_path("M700,596 L1250,596", OR) + head_at(1252, 596, 0, OR)
o.append(svg(g3, 3))
o.append(f'<div{PATH(3, "p-gh")} style="position:absolute;left:1222px;top:578px;width:36px;height:36px;border-radius:18px;background:{OR};border:4px solid #FFFFFF;box-shadow:0 2px 6px rgba(0,0,0,.18)"></div>')
o.append(p(f"position:absolute;left:760px;top:540px;width:440px;text-align:center;font-size:26px;font-weight:700;color:{OR}", "명령으로 버튼 누르기", bi("fade", 3)))
o.append(caption("gh가 git을 대신하지 않아요.<br>둘을 같이 써요.", 790, 3, width=600, size=30))
W("big", o, "오늘 쓰는 도구 셋이 어디에 있는지 그림으로 봐요. 왼쪽 터미널에서 git과 gh를 같이 써요. git은 push와 pull로 커밋 기록을 GitHub과 주고받아요. GitHub의 레포 만들기, PR, 이슈 같은 버튼은 지금까지 브라우저에서 마우스로 눌렀어요. gh는 그 버튼을 터미널 명령으로 눌러요. 그래서 커밋과 push는 계속 git으로 하고, 버튼 일은 gh로 해요. gh가 git을 대신하지 않아요.")

# ---------- map ----------
o = frame("map", "들어가기", "웹에서 누르던 버튼마다 gh 명령이 하나씩 있어요", INK)
rows = [("로그인", [("gh", INK), ("auth", BL), ("login", OR)]), ("Code › 주소 복사 뒤 clone", [("gh", INK), ("repo", BL), ("clone", OR), ("kim/team-intro", INK)]),
        ("New repository", [("gh", INK), ("repo", BL), ("create", OR), ("my-notes …", INK)]), ("Settings › Delete this repository", [("gh", INK), ("repo", BL), ("delete", OR), ("kim/my-notes", INK)]),
        ("New issue", [("gh", INK), ("issue", BL), ("create", OR)]), ("Compare & pull request", [("gh", INK), ("pr", BL), ("create", OR)])]
o.append(p(f"position:absolute;left:96px;top:222px;font-size:24px;font-weight:700;color:{GH}", "GitHub 웹에서"))
lg = 900 + tw("gh ", 34)
o.append(p(f"position:absolute;left:900px;top:222px;font-size:24px;font-weight:700;color:{GRAY}", "gh"))
o.append(p(f"position:absolute;left:{lg:.0f}px;top:222px;font-size:24px;font-weight:700;color:{BL}", "대상", bi("pop", 1)))
o.append(p(f"position:absolute;left:{lg + tw('repo ', 34):.0f}px;top:222px;font-size:24px;font-weight:700;color:{OR}", "할 일", bi("pop", 1)))
for i, (web, segs) in enumerate(rows):
    y = 270 + i * 106
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:1px;background:{LINE}"></div>')
    o.append(p(f"position:absolute;left:96px;top:{y + 28}px;width:760px;font-size:32px;font-weight:700;color:{INK}", e(web)))
    o.append(p(f"position:absolute;left:900px;top:{y + 26}px;font-family:{MONO};font-size:34px;font-weight:700;white-space:pre", " ".join(f'<span style="color:{c}">{e(s)}</span>' for s, c in segs), bi("rise", 1) + DELAY(i * 90)))
o.append(f'<div style="position:absolute;left:96px;top:{270 + 6 * 106}px;width:1728px;height:1px;background:{LINE}"></div>')
o.append(caption("gh 다음에 대상, 그다음에 할 일을 적어요.", 940, 1, size=30))
W("map", o, "오늘 쓸 명령을 웹 버튼과 나란히 놓았어요. 왼쪽은 GitHub 웹사이트에서 누르던 버튼, 오른쪽은 같은 일을 하는 gh 명령이에요. 1파트에서 로그인, 2파트에서 clone, 3파트에서 레포 만들기, 4파트에서 지우기, 5파트에서 이슈와 PR을 봐요. gh 명령은 모두 gh 다음에 대상(repo, issue, pr)과 할 일(create, list, delete)을 적는 모양이에요. 파란 글자가 대상, 주황 글자가 할 일이에요.")

# ---------- part 1: install and login ----------
EB1 = "1. 설치하고 로그인하기"
o = frame("install", EB1, "brew나 winget으로 설치하고 gh --version으로 확인해요", BL)
t = Term([("c", "# Mac"), ("$", P_HOME, "brew install gh"), ("c", ""), ("c", "# Windows (Git Bash)"), ("$", P_HOME, "winget install --id GitHub.cli -e"), ("c", ""),
          ("$", P_HOME, "gh --version"), ("o", VERSION[0]), ("o", VERSION[1])], 96, 214, size=36, w=1728, lh=1.62)
t.band(7, 8, order=2)
o.append(t.html())
o += tag(t, 1, "09에서 uv를 설치한 Homebrew", BL, 1)
o += tag(t, 4, "끝나면 Git Bash를 다시 열어요", BL, 1)
o += tag(t, 7, "숫자는 설치한 날마다 달라요", GRAY, 2)
W("install", o, "Mac은 09에서 uv를 설치할 때 쓴 Homebrew로 brew install gh를 쳐요. Windows는 winget으로 설치해요. 대소문자까지 GitHub.cli 그대로 적어요. 설치 직후 Git Bash가 gh를 못 찾으면 창을 닫고 다시 열어요. 마지막으로 gh --version을 쳐서 버전이 나오면 설치가 끝난 거예요. 설치 화면은 이 자료를 만든 환경에서 실행할 수 없어서 옮기지 않았어요. gh --version 출력은 실제로 실행한 결과예요. 버전 숫자는 설치한 날에 따라 달라요.")

o = frame("status0", EB1, "gh auth status로 로그인했는지 물어봐요", BL)
t = Term([("$", P_HOME, "gh auth status"), ("o", NOT_LOGGED)], 96, 214, size=32, w=1728)
o.append(t.html())
ux = t.sx(1, "gh auth login")
o.append(underline(1, round(ux), round(ux + t.sw("gh auth login")), round(t.top(1) + t.lp - 4), OR))
o.append(caption("출력 끝에 다음에 칠 명령까지 적혀 있어요.", t.y + t.h + 36, 1, color=OR, size=30))
o += parts(240, 600, [("gh", INK, "GitHub CLI", None), ("auth", BL, "대상: 로그인", None), ("status", OR, "할 일: 상태 보기", None)], size=88, order=2, lab=30, drop=40, sep=3)
W("status0", o, "설치하자마자 gh auth status를 쳐 봐요. 아직 로그인하지 않았다는 출력이 나와요. 출력 끝에 To log in, run: gh auth login이라고 다음에 칠 명령까지 알려 줘요. 번외 터미널 환경에 적응하기에서 본 것처럼 에러와 안내의 마지막 줄을 읽는 습관이 여기서도 통해요. 명령을 나눠 보면 auth는 로그인 관련 묶음이고, status는 상태를 보여 달라는 뜻이에요. 앞 장에서 본 gh 대상 할 일 모양 그대로예요.")

# login questions, one per slide (magic move keeps the terminal and the answer slots in place)
QS = [("login1", "질문 1 · 어떤 GitHub을 쓰나요?", "? Where do you use GitHub?  [Use arrows to move, type to filter]", ["> GitHub.com", "  Other"], "GitHub.com", "Enter",
       "github.com 웹사이트를 쓰니 고른 그대로 Enter예요. Other는 회사 전용 GitHub일 때 골라요.",
       "gh auth login을 치면 질문이 네 개 나와요. 한 장에 하나씩 볼게요. 첫 질문은 어떤 GitHub을 쓰는지예요. 우리는 github.com을 쓰니 GitHub.com이 골라진 상태에서 Enter를 눌러요. 위아래 화살표로 고르고 Enter로 정해요. 질문 끝의 Use arrows to move가 그 뜻이에요. 아래 칸에 고른 답이 하나씩 쌓여요."),
      ("login2", "질문 2 · git은 어떤 주소로 주고받을까요?", "? What is your preferred protocol for Git operations on this host?  [Use arrows to move, type to filter]", ["> HTTPS", "  SSH"], "HTTPS", "Enter",
       "02부터 써 온 https:// 주소 방식이에요. SSH는 열쇠 파일을 따로 만들어야 해서 이 과정에서는 쓰지 않아요.",
       "두 번째 질문은 git이 GitHub과 주고받을 때 어떤 주소를 쓸지예요. 02에서 git remote add origin https://github.com/... 처럼 https 주소를 썼어요. 그래서 HTTPS 그대로 Enter예요. SSH는 내 컴퓨터에 열쇠 파일을 만들어 등록하는 방식이라 이 과정에서는 다루지 않아요."),
      ("login3", "질문 3 · git도 같이 로그인할까요?", "? Authenticate Git with your GitHub credentials? (Y/n)", [], "Yes", "Enter",
       "Yes로 하면 git push 할 때도 gh 로그인을 써요. 대문자 Y가 기본값이라 Enter만 눌러도 Yes예요.",
       "세 번째 질문이 오늘 가장 반가운 질문이에요. git도 gh의 로그인 정보를 쓰게 할지 물어요. (Y/n)에서 대문자 Y가 기본값이라 Enter만 눌러도 Yes예요. 02의 첫 push에서 GitHub 로그인 창이나 토큰 입력 창이 떴던 것 기억나죠? Yes로 하면 그 창이 더는 뜨지 않아요."),
      ("login4", "질문 4 · 어떻게 로그인할까요?", "? How would you like to authenticate GitHub CLI?  [Use arrows to move, type to filter]", ["> Login with a web browser", "  Paste an authentication token"], "Login with a web browser", "Enter",
       "브라우저로 로그인해요. 토큰을 직접 만들어 붙여 넣는 방법은 쓰지 않아요.",
       "마지막 질문은 로그인 방법이에요. Login with a web browser가 가장 쉬워요. 브라우저에서 GitHub에 이미 로그인돼 있으면 버튼 두 번이면 끝나요. Paste an authentication token은 GitHub 설정에서 토큰을 직접 만들어 붙이는 방법이에요. 이 과정에서는 쓰지 않아요.")]
ANS = [Q_WHERE, Q_PROTO, Q_GIT, Q_HOW]
SHORT = ["GitHub.com", "HTTPS", "Yes", "web browser"]
for i, (sid, title, q, opts, pick, key, why, notes) in enumerate(QS):
    o = frame(sid, EB1, e(title), BL, "magic" if i else "fade")
    lines = [("$", P_HOME, "gh auth login")] + [("d", a) for a in ANS[:i]] + [("y", q, {"(Y/n)": f"src{i}"} if not opts else {})]
    for x in opts:
        lines.append(("sel", x, {pick: f"src{i}"}) if x.startswith(">") else ("o", x))
    t = Term(lines, 96, 214, size=26, w=1728, lh=1.55)
    o.append(t.html())
    if opts:
        r = len(lines) - len(opts)
        bx, by = t.tx - 14, t.top(r) - 2
        bw = t.sw(opts[0]) + 28
        o.append(pen_box(1, round(bx), round(by), round(bw), round(t.lp + 4), GR))
        o.append(kbd(bx + bw + 24, t.cy(r) - 21, key, 1))
    else:
        r = len(lines) - 1
        bx = t.sx(r, "(Y/n)") - 10
        o.append(pen_box(1, round(bx), round(t.top(r) - 2), round(t.sw("(Y/n)") + 20), round(t.lp + 4), GR))
        o.append(kbd(bx + t.sw("(Y/n)") + 44, t.cy(r) - 21, key, 1))
    o.append(caption(e(why), t.y + t.h + 40, 1, size=30))
    # answer slots
    for j in range(4):
        x = 96 + j * 440
        if j < i:
            o.append(f'<div id="slot{j}" style="position:absolute;left:{x}px;top:790px;width:410px;height:150px;background:#E9F6EE;border-radius:16px;padding:18px 24px">'
                     + p(f"font-size:24px;font-weight:700;color:#2D5E40", f"질문 {j + 1}") + '</div>')
            o.append(p(f"position:absolute;left:{x + 24}px;top:854px;font-family:{MONO};font-size:36px;font-weight:700;color:{GR};white-space:nowrap", e(SHORT[j]), f' id="ans{j}"'))
        elif j == i:
            o.append(f'<div id="slot{j}" style="position:absolute;left:{x}px;top:790px;width:410px;height:150px;background:#FFFFFF;border:2px dashed #9FC9AE;border-radius:16px;padding:16px 22px">'
                     + p(f"font-size:24px;font-weight:700;color:#2D5E40", f"질문 {j + 1}") + '</div>')
            o.append(p(f"position:absolute;left:{x + 24}px;top:854px;font-family:{MONO};font-size:36px;font-weight:700;color:{GR};white-space:nowrap", e(SHORT[j]), f' id="ans{j}" data-build-in="fly order 1" data-from="src{i}"'))
        else:
            o.append(f'<div id="slot{j}" style="position:absolute;left:{x}px;top:790px;width:410px;height:150px;background:transparent;border:2px dashed #C9CED8;border-radius:16px;padding:16px 22px">'
                     + p(f"font-size:24px;font-weight:700;color:#8A93A3", f"질문 {j + 1}") + '</div>')
    W(sid, o, notes, ("login", "로그인") if i == 0 else None)

o = frame("code", EB1, "터미널에 나온 코드를 브라우저에 넣어요", BL, "magic")
t = Term([("$", P_HOME, "gh auth login")] + [("d", a) for a in ANS] + [("o", ""), ("y", DEVICE[0], {CODE: "codesrc"}), ("o", DEVICE[1])], 96, 214, size=24)
t.band(6, order=1)
o.append(t.html())
b1 = (p(f"font-size:30px;font-weight:700;color:{INK}", "Device Activation") + code_boxes(CODE, 34, "codedst", ' data-build-in="fly order 1" data-from="codesrc"') + gh_button("Continue", "btn-cont"))
o.append(browser(1200, 330, 624, 400, "github.com/login/device", b1, "br1"))
b2 = (p(f"font-size:30px;font-weight:700;color:{INK}", "Authorize GitHub CLI") + p(f"font-size:24px;color:{SUB}", "GitHub CLI가 내 계정을 쓰도록 허락해요") + gh_button("Authorize github", "btn-auth"))
o.append(browser(560, t.y + t.h - 16, 700, 400, "github.com/login/device", b2, "br2", attrs=bi("rise", 3)))
o.append(cursor(2, target="btn-cont"))
o.append(cursor(3, target="btn-auth"))
W("code", o, "질문이 끝나면 터미널에 여덟 글자 코드가 나와요. 코드는 로그인할 때마다 바뀌어요. Enter를 누르면 브라우저가 github.com/login/device를 열어요. 브라우저에서 코드를 넣고 Continue를 눌러요. 다음 화면에서 Authorize github를 누르면 허락이 끝나요. 브라우저가 저절로 안 열리면 주소를 직접 쳐서 들어가도 돼요. 브라우저 화면은 버튼 위치만 보이게 단순하게 그렸어요.")

o = frame("logged", EB1, "Logged in as 다음에 내 아이디가 보이면 성공이에요", BL, "magic")
t = Term([("$", P_HOME, "gh auth login")] + [("d", a) for a in ANS] + [("d", ""), ("d", DEVICE[0]), ("d", DEVICE[1]),
          ("g", LOGIN_TAIL[0]), ("o", LOGIN_TAIL[1]), ("g", LOGIN_TAIL[2]), ("d", LOGIN_TAIL[3]), ("g", LOGIN_TAIL[4], {"kim": "kimname"})], 96, 214, size=28, w=1728, lh=1.5)
o.append(t.html())
o += tag(t, 8, "브라우저 허락 끝", GR, 1)
o += tag(t, 10, "HTTPS로 저장", GR, 1)
o += tag(t, 11, "Mac, Windows에서는 보통 안 나와요", GRAY, 1)
o += tag(t, 12, "내 GitHub 아이디", GR, 2)
kx = t.sx(12, "kim")
o.append(underline(2, round(kx - 2), round(kx + t.sw("kim") + 2), round(t.top(12) + t.lp - 2), GR))
W("logged", o, "브라우저에서 Authorize를 누르면 터미널이 저절로 다음 줄을 출력해요. Authentication complete는 브라우저 허락이 끝났다는 뜻이에요. Configured git protocol은 앞에서 고른 HTTPS를 설정에 저장했다는 뜻이에요. 마지막 Logged in as kim에서 kim 자리에 내 GitHub 아이디가 보이면 성공이에요. 회색 saved in plain text 줄은 로그인 정보를 파일에 저장했다는 안내예요. 이 자료를 만든 환경에는 Mac의 키체인 같은 비밀 보관함이 없어서 나왔어요. Mac과 Windows는 보통 비밀 보관함에 저장해서 이 줄이 안 나와요.")

o = frame("status1", EB1, "로그인하면 출입증(토큰)과 열 수 있는 문(권한) 목록이 생겨요", BL)
t = Term([("$", P_HOME, "gh auth status")] + [("o", l) for l in STATUS] + [("o", SCOPES, {"'gist', 'read:org', 'repo', 'workflow'": "scsrc"})], 96, 214, size=30, w=1728)
t.band(5, order=1)
t.band(6, order=2)
o.append(t.html())
o += tag(t, 5, "출입증(토큰), 앞 네 글자만 보여요", BL, 1)
o += tag(t, 6, "출입증으로 열 수 있는 문(권한)", OR, 2)
chips = [chip(k, BL, "#E3ECFD", f"k{i}") for i, (k, _) in enumerate(SC)]
o.append(badge(96, 650, chips, attrs=' data-build-in="fly order 2" data-from="scsrc"'))
o.append(caption("이 목록에 없는 일은 못 해요. 4파트에서 여기에 한 칸이 늘어요.", 880, 2, size=30, color=SUB))
W("status1", o, "로그인한 뒤 gh auth status를 다시 쳐요. 이번에는 kim 계정으로 로그인했다고 나와요. Token 줄은 GitHub이 gh에게 준 출입증이에요. 비밀번호 같은 거라 화면에는 앞 네 글자만 보여 줘요. Token scopes 줄은 이 출입증으로 할 수 있는 일의 목록이에요. repo는 레포 읽고 쓰기, read:org는 조직 보기, gist는 메모 조각, workflow는 Actions 설정이에요. 레포 지우기(delete_repo)는 목록에 없어요. 4파트에서 지우기를 시도하다가 이 목록 때문에 막혀요.")

o = frame("gitcred", EB1, "질문 3의 Yes 덕분에 git push도 gh 로그인을 써요", BL)
t = Term([("$", P_HOME, "cat ~/.gitconfig"), ("d", "…"), ("o", "[pull]"), ("o", "\trebase = false"), ("o", '[credential "https://github.com"]'),
          ("o", "\thelper ="), ("o", "\thelper = !/usr/local/bin/gh auth git-credential"), ("d", "…")], 96, 214, size=32, w=1728, lh=1.6)
t.band(4, 6, order=1)
o.append(t.html())
o += tag(t, 6, "gh가 넣은 줄, 고치지 않아요", BL, 1)
fy = 760
nodes = [("git push origin main", INK, True), ("git이 gh에게 출입증을 받아요", BL, False), ("GitHub에 바로 올라가요", GH, False)]
xs = [96, 700, 1304]
for k, (txt, c, mono) in enumerate(nodes):
    o.append(f'<div{bi("rise", 2 + k)} style="position:absolute;left:{xs[k]}px;top:{fy}px;width:520px;height:110px;background:{CARD};border:1px solid {LINE};border-radius:18px;display:flex;align-items:center;justify-content:center">'
             + p(f"font-size:{28 if mono else 30}px;font-weight:700;color:{c};{'font-family:' + MONO + ';' if mono else ''}", e(txt)) + '</div>')
for k in range(2):
    x1, x2 = xs[k] + 520 + 10, xs[k + 1] - 12
    o.append(svg(arrow_path(f"M{x1},{fy + 55} L{x2},{fy + 55}", "#9AA3B5", 4) + head_at(x2 + 2, fy + 55, 0, "#9AA3B5", 14), 3 + k))
o.append(caption("02의 첫 push에서 뜨던 로그인 창이 이제 안 떠요.", 920, 4, size=30, color=SUB))
W("gitcred", o, "질문 3에서 Yes를 고르면 gh가 git 설정 파일(~/.gitconfig)에 두 줄을 넣어요. credential은 로그인 정보라는 뜻이에요. github.com에 push 할 때 로그인 정보는 gh auth git-credential에게 물어보라는 설정이에요. 그래서 git push origin main을 치면 git이 gh에게 출입증을 받아서 바로 올려요. 위쪽 [pull] rebase = false는 06에서 넣은 pull 설정이에요. helper = 처럼 빈 줄도 gh가 일부러 넣은 거라 지우지 않아요. 파일 내용은 tools/demo.sh에서 실제로 실행한 결과고, 위아래는 …로 줄였어요. Windows는 /usr/local/bin 자리의 설치 경로가 달라요.")

# ---------- part 2: connect existing repos ----------
EB2 = "2. 이미 있는 레포 연결하기"
o = frame("clone", EB2, "gh repo clone은 주소 대신 주인/이름만 적어요", GR)
o.append(p(f"position:absolute;left:96px;top:214px;font-size:24px;font-weight:700;color:{GRAY}", "git으로 받을 때 (06)"))
a = "git clone "
o.append(p(f"position:absolute;left:96px;top:256px;font-family:{MONO};font-size:40px;font-weight:700;line-height:1.3;white-space:pre;color:{INK}",
           f'git clone <span style="color:{GRAY}">https://github.com/</span><span id="own-src">kim/team-intro</span><span style="color:{GRAY}">.git</span>'))
x1 = 96 + tw(a, 40)
x2 = x1 + tw("https://github.com/", 40)
x3 = x2 + tw("kim/team-intro", 40)
o.append(underline(1, round(x1), round(x2 - 8), 284, RED))
o.append(underline(1, round(x3 + 6), round(x3 + tw(".git", 40)), 284, RED))
o.append(p(f"position:absolute;left:96px;top:352px;font-size:24px;font-weight:700;color:{GR}", "gh로 받을 때", bi("fade", 2)))
o.append(p(f"position:absolute;left:96px;top:394px;font-family:{MONO};font-size:40px;font-weight:700;line-height:1.3;white-space:pre;color:{INK}",
           f'gh repo clone <span id="own-dst" style="color:{GR}" data-build-in="fly order 2" data-from="own-src">kim/team-intro</span>', bi("fade", 2)))
t = Term([("$", P_KANT, "gh repo clone kim/team-intro")] + [("o", l) for l in CLONE], 96, 520, size=26, w=1728, attrs=bi("rise", 3))
o.append(t.html())
o += tag(t, 1, "git clone과 같은 출력", GR, 3)
W("clone", o, "06에서 팀 레포 team-intro를 git clone으로 받았어요. gh는 같은 일을 gh repo clone 주인/이름으로 해요. 주소 앞의 https://github.com/와 뒤의 .git을 안 적어도 돼요. 아래 출력의 첫 줄 Cloning into는 git clone과 똑같아요. gh가 속에서 git clone을 부르기 때문이에요. 실습할 땐 kim 자리에 팀장 아이디를 적어요. " + MADE, ("connect", "이미 있는 레포 연결하기"))

o = frame("clone-check", EB2, "gh로 받은 폴더도 git으로 받은 폴더와 똑같아요", GR)
t = Term([("$", P_KANT, "cd team-intro"), ("$", P_TI, "git remote -v")] + [("o", l) for l in REMOTE_TI] + [("o", ""), ("$", P_TI, "git log --oneline")] + [("o", l) for l in LOG_TI],
         96, 214, size=32, w=1728, lh=1.6)
t.band(2, 3, order=1)
t.band(6, 7, order=2)
o.append(t.html())
o += tag(t, 2, "origin도 그대로", GR, 1)
o += tag(t, 6, "06의 커밋 그대로", GR, 2)
o.append(caption(f"push, pull도 지금처럼 {cmd('git push origin main')}, {cmd('git pull origin main')}으로 해요.", t.y + t.h + 48, 3, size=30))
o.append(caption("반대로 git clone으로 받은 폴더에서도 gh를 바로 쓸 수 있어요.", t.y + t.h + 110, 3, size=30, color=SUB))
W("clone-check", o, "받은 폴더에 들어가서 git remote -v를 쳐요. origin이 https://github.com/kim/team-intro.git으로 등록돼 있어요. git clone으로 받았을 때와 같아요. git log --oneline에도 06에서 만든 커밋이 그대로 있어요. 그래서 push, pull 명령도 그대로예요. 반대로 06에서 git clone으로 받은 폴더에서도 gh 명령을 바로 쓸 수 있어요. 다음 장에서 보는 gh repo view는 origin 주소를 읽고 어느 레포인지 알아내요.")

o = frame("view", EB2, "레포 폴더 안에서는 gh repo view, gh browse만 쳐도 돼요", GR)
t = Term([("$", P_TI, "gh repo view")] + [("o", l) for l in VIEW], 96, 214, size=26, w=1100, lh=1.6)
t.band(1, order=1)
o.append(t.html())
o += tag(t, 1, "origin을 보고 알아냈어요", GR, 1)
t2 = Term([("$", P_TI, "gh browse"), ("o", "Opening https://github.com/kim/team-intro"), ("o", "in your browser.")], 1240, 214, size=20, w=584, tid="t-browse", attrs=SLIDE(2, 300, 0))
binner = (p(f"font-size:28px;font-weight:700;color:{INK}", "kim / team-intro") + f'<div style="width:100%;height:1px;background:#E6E2D9"></div>'
          + p(f"font-size:30px;font-weight:700;color:{INK}", "team-intro") + p(f"font-size:24px;color:{SUB}", "우리 팀 소개 페이지예요."))
o.append(browser(1240, 440, 584, 430, "github.com/kim/team-intro", binner, "br-view", attrs=SLIDE(2, 300, 0), align="flex-start", pad="30px 40px").replace("justify-content:center;gap:22px", "justify-content:flex-start;gap:18px"))
o.append(t2.html())
W("view", o, "레포 폴더 안에서 gh repo view를 치면 레포 이름, 설명, README 내용을 터미널에 보여 줘요. 설명을 안 적은 레포라 No description provided가 나와요. gh browse는 같은 레포를 브라우저 새 탭으로 열어요. 웹에서 할 일이 있을 때 주소를 찾지 않아도 돼요. 두 명령 모두 주인/이름을 적지 않았어요. 지금 폴더의 origin을 보고 kim/team-intro라고 알아낸 거예요. gh browse 출력은 화면에 맞추려고 두 줄로 나눴어요. 브라우저 화면은 단순하게 그린 그림이에요.")

o = frame("repo-list", EB2, "gh repo list는 어느 폴더에서 쳐도 내 레포 목록을 보여 줘요", GR)
t = Term([("$", P_HOME, "gh repo list")] + [("o", l) for l in LIST2], 96, 214, size=32, w=1728)
o.append(t.html())
nx = t.tx - 12
o.append(pen_box(1, round(nx), round(t.top(5) - 4), round(t.sw("kim/team-intro") + 24), round(2 * t.lp + 8), GR))
o.append(caption("clone, delete에 적을 주인/이름은 이 칸에서 복사해요.", t.y + t.h + 40, 1, color=GR, size=30))
W("repo-list", o, "gh repo list는 내 계정의 레포 목록을 보여 줘요. 특정 레포 안에서 쓰는 명령이 아니라서 어느 폴더에서 쳐도 결과가 같아요. kim/hello-git은 02에서 만든 레포, kim/team-intro는 06의 팀 레포예요. INFO 칸의 public은 누구나 볼 수 있는 레포라는 뜻이에요. clone이나 delete에 적을 주인/이름이 헷갈리면 NAME 칸에서 확인해요.")

# ---------- part 3: create ----------
EB3 = "3. 새 레포 만들기"
o = frame("create-why", EB3, "웹에서 네 단계로 하던 일을 gh는 한 줄로 해요", TEAL)
o.append(p(f"position:absolute;left:96px;top:214px;font-size:24px;font-weight:700;color:{GH}", "웹에서 (02)"))
web = [("GitHub에서 New 누르기", False), ("이름 적고 Create repository", False), ("주소 복사", False), ("git remote add origin 주소", True)]
for i, (txt, mono) in enumerate(web):
    y = 270 + i * 112
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:760px;height:1px;background:{LINE}"></div>')
    o.append(f'<div{bi("rise", i + 1)}{DIM("web")} style="position:absolute;left:96px;top:{y + 26}px;width:760px;height:60px">'
             + p(f"position:absolute;left:0;top:0;width:56px;height:56px;border-radius:28px;background:{GH};color:#FFFFFF;font-size:28px;font-weight:900;line-height:56px;text-align:center", str(i + 1))
             + p(f"position:absolute;left:80px;top:4px;font-size:{26 if mono else 30}px;font-weight:700;color:{INK};white-space:nowrap;{'font-family:' + MONO + ';' if mono else ''}", e(txt)) + '</div>')
o.append(f'<div style="position:absolute;left:96px;top:{270 + 4 * 112}px;width:760px;height:1px;background:{LINE}"></div>')
o.append(svg(arrow_path("M880,290 C930,290 930,290 930,370 L930,640 C930,700 930,718 880,718", TEAL, 4) + arrow_path("M930,504 L1000,504", TEAL, 4) + head_at(1002, 504, 0, TEAL, 14), 5))
t = Term([("$", P_MN, "gh repo create my-notes"), ("o", "    --public --source=. --remote=origin")], 1030, 420, size=28, w=794, attrs=bi("rise", 5))
o.append(t.html())
o.append(caption("만들고 origin에 연결하는 데까지 gh가 해요.<br>push는 지금처럼 git으로 해요.", 760, 5, left=1030, width=794, size=28))
W("create-why", o, "02에서 레포를 GitHub에 올릴 때 네 단계를 거쳤어요. 웹에서 New를 누르고, 이름을 적고 Create repository를 누르고, 주소를 복사해서 git remote add origin으로 연결했어요. gh repo create는 이 네 단계를 한 줄로 해요. 다만 push는 하지 않아요. push는 지금까지처럼 git push origin main으로 직접 쳐요. 오른쪽 명령은 화면에 맞추려고 두 줄로 나눠 적었어요. 실제로는 한 줄로 쳐요.", ("create", "새 레포 만들기"))

o = frame("create-prep", EB3, "먼저 내 컴퓨터에 저장소와 커밋 하나를 만들어요", TEAL)
t = Term([("$", P_KANT, "mkdir my-notes"), ("$", P_KANT, "cd my-notes"), ("$", P_MN, "git init"), ("o", INIT),
          ("$", P_MN, "echo '# my-notes' > README.md"), ("$", P_MN, "git add README.md"), ("$", P_MN, "git commit -m 'docs: README 추가'")] + [("o", l) for l in COMMIT_MN],
         96, 214, size=34, w=1728, lh=1.55)
t.band(6, 9, order=1)
o.append(t.html())
o += tag(t, 7, "이 커밋을 GitHub에 올려요", TEAL, 1)
W("create-prep", o, "새 레포는 내 컴퓨터 폴더에서 시작해요. 01의 mkdir, cd로 my-notes 폴더를 만들고 들어가요. 02에서 한 대로 git init, README.md 만들기, git add, git commit -m까지 쳐요. 커밋이 있어야 다음 장에서 GitHub에 올릴 내용이 생겨요. 출력은 tools/demo.sh에서 실제로 실행한 결과고, 커밋 해시는 칠 때마다 달라요.")

o = frame("create", EB3, "gh repo create로 레포를 만들고 origin까지 연결해요", TEAL)
o += parts(96, 226, [("gh repo create", INK, None, None), ("my-notes", TEAL, "GitHub에 만들<br>레포 이름", None), ("--public", TEAL, "누구나 보기<br>(나만: --private)", None),
                     ("--source=.", TEAL, "지금 폴더(.)를<br>레포로 써요", None), ("--remote=origin", TEAL, "origin 이름으로<br>연결해요", None)], size=42, order=1, lab=26, drop=30)
t = Term([("$", P_MN, "gh repo create my-notes --public --source=. --remote=origin")] + [("g", CREATE[0]), ("o", CREATE[1]), ("g", CREATE[2])], 96, 500, size=32, w=1728, lh=1.6)
o.append(t.html())
o += tag(t, 1, "GitHub에 만들었어요", TEAL, 2)
o += tag(t, 3, "origin으로 연결했어요", TEAL, 2)
o.append(caption(f"{cmd('--push')} 옵션은 붙이지 않아요. push는 다음 장에서 직접 쳐요.", t.y + t.h + 44, 3, size=30, color=SUB))
W("create", o, "my-notes 폴더 안에서 gh repo create를 쳐요. 옵션은 네 개예요. 레포 이름, 공개 여부, 지금 폴더를 쓴다는 --source=., 원격 이름 --remote=origin이에요. 출력의 Created repository는 GitHub에 kim/my-notes 레포를 만들었다는 뜻이고, Added remote는 origin으로 연결했다는 뜻이에요. gh repo create에는 --push 옵션도 있어요. 그런데 --push는 이 과정에서 쓰지 않기로 한 push 설정까지 같이 바꿔요. 그래서 붙이지 않고, push는 지금까지처럼 직접 쳐요.")

o = frame("create-push", EB3, "push는 git으로 하고, gh repo list로 확인해요", TEAL)
t = Term([("$", P_MN, "git remote -v")] + [("o", l) for l in REMOTE_MN] + [("$", P_MN, "git push origin main"), ("d", "…")] + [("o", l) for l in PUSH_MN[-2:]],
         96, 214, size=28, w=1100, lh=1.6)
t.band(6, order=1)
o.append(t.html())
o += tag(t, 6, "로그인 창 없이 올라갔어요", TEAL, 1)
t2 = Term([("$", P_HOME, "gh repo list"), ("o", "NAME")] + [("o", l.split()[0]) for l in LIST3[4:]], 1240, 214, size=28, w=584, tid="t-list", attrs=bi("rise", 2))
o.append(t2.html())
o.append(pen_box(2, round(t2.tx - 12), round(t2.top(3) - 3), round(t2.sw("kim/my-notes") + 24), round(t2.lp + 6), TEAL))
o.append(caption("질문 3에서 Yes를 고른 덕분이에요.", t.y + t.h + 44, 1, size=30, color=SUB, width=1100))
W("create-push", o, "git remote -v로 origin이 https://github.com/kim/my-notes.git인지 보고, git push origin main으로 올려요. 비밀번호나 토큰을 묻지 않고 바로 올라가요. 1파트 질문 3에서 Yes를 골라 git이 gh 로그인을 쓰기 때문이에요. 오른쪽 gh repo list에 kim/my-notes가 한 줄 늘었어요. push 출력 가운데는 …로 줄였고, 오른쪽 목록은 화면에 맞추려고 뒤 칸을 잘랐어요.")

o = frame("create-ask", EB3, "옵션이 생각나지 않으면 gh repo create만 쳐요", TEAL)
t = Term([("$", P_KANT, "gh repo create"), ("y", CREATE_Q[0]), ("sel", CREATE_Q[1]), ("o", CREATE_Q[2]), ("o", CREATE_Q[3])], 96, 214, size=32, w=1728, lh=1.6)
o.append(t.html())
o.append(pen_box(1, round(t.tx - 12), round(t.top(4) - 3), round(t.sw(CREATE_Q[3]) + 24), round(t.lp + 6), TEAL))
o += tag(t, 4, "앞 장에서 한 일", TEAL, 1, at=t.end(4) + 12)
o.append(caption("화살표로 고르고 Enter를 누르면 폴더, 이름, 공개 여부를 차례로 물어요.", t.y + t.h + 44, 2, size=30))
o.append(caption(f"마지막에 push 할지 물으면 No를 고르고 {cmd('git push origin main')}으로 직접 올려요.", t.y + t.h + 104, 2, size=30, color=SUB))
W("create-ask", o, "옵션이 기억나지 않으면 gh repo create만 쳐도 돼요. 무엇을 할지부터 하나씩 물어봐요. 세 번째 Push an existing local repository가 앞 장에서 한 일이에요. 그다음 폴더 위치, 레포 이름, 공개 여부, origin 이름을 차례로 물어요. 마지막에 지금 push 할지도 묻는데, 거기서는 No를 고르고 git push origin main으로 직접 올려요. 첫 질문 화면은 실제로 실행한 출력이에요.")

# ---------- part 4: delete and scope ----------
EB4 = "4. 레포 지우기와 권한 추가"
o = frame("del-warn", EB4, "지운 레포는 되돌릴 수 없어요", RED)
ITEMS = (("Database", "커밋 기록과 README", "레포 안의 파일과 기록"), ("Chat", "이슈와 PR", "토론과 리뷰 기록"), ("Star", "스타와 포크 연결", "다른 사람이 누른 것"))
RH, WY, WH = 116, 226, 52 + 84 + 3 * 116
gin = "".join(f'<div style="display:flex;flex-direction:row;align-items:center;gap:22px;height:{RH}px;border-top:1px solid #E6E2D9;padding:0 36px">'
              f'<x-icon name="{ic}" style="width:34px;height:34px;color:{GRAY}"></x-icon>' + p(f"font-size:36px;font-weight:700;color:{INK}", t_) + p(f"margin-left:auto;font-size:26px;color:{SUB}", d_) + '</div>'
              for ic, t_, d_ in ITEMS)
o.append(f'<div id="gh-win" style="position:absolute;left:96px;top:{WY}px;width:1120px;height:{WH}px;background:{CARD};border:1px solid #D2CEC4;border-radius:16px;overflow:hidden;box-shadow:{SHADOW}">'
         '<div style="height:52px;background:#EEECE6;display:flex;flex-direction:row;align-items:center;gap:9px;padding:0 18px">'
         + "".join('<div style="width:13px;height:13px;border-radius:7px;background:#C9CED8"></div>' for _ in range(3))
         + p(f"margin-left:14px;font-size:20px;font-weight:500;color:{SUB};background:#FFFFFF;border-radius:9px;padding:4px 16px", "github.com/kim/my-notes") + '</div>'
         + p(f"height:84px;padding:0 36px;font-size:30px;font-weight:700;line-height:84px;color:{GH}", "GitHub의 kim/my-notes") + gin + '</div>')
for k, (_, t_, _) in enumerate(ITEMS):
    y = WY + 52 + 84 + k * RH + RH // 2 + 2
    x0 = 96 + 36 + 34 + 22
    o.append(underline(1, x0 - 6, round(x0 + tw(t_, 36, mono=False) + 6), y, RED, 5))
o.append(p(f"position:absolute;left:96px;top:{WY + WH + 30}px;font-size:32px;font-weight:700;color:{RED}", "모두 사라지고, GitHub에는 휴지통이 없어요.", bi("fade", 1)))
o.append(f'<div{bi("rise", 2)} style="position:absolute;left:1280px;top:{WY + 52 + 84}px;width:544px;height:{3 * RH}px;background:#E9F6EE;border-radius:20px;padding:34px 40px;display:flex;flex-direction:column;gap:18px">'
         f'<div style="display:flex;flex-direction:row;gap:14px;align-items:center"><x-icon name="Home" style="width:32px;height:32px;color:{GR}"></x-icon>' + p(f"font-size:28px;font-weight:700;color:#2D5E40", "내 컴퓨터") + '</div>'
         + p(f"font-family:{MONO};font-size:34px;font-weight:700;color:{INK}", "~/kant/my-notes") + p(f"font-size:32px;font-weight:700;color:{GR}", "폴더는 남아요") + '</div>')
o.append(caption("연습용으로 만든 my-notes만 지워요. team-intro처럼 팀이 쓰는 레포는 지우지 않아요.", 900, 3, size=32))
W("del-warn", o, "지우는 명령을 치기 전에 무엇이 사라지는지 먼저 봐요. GitHub에 있는 레포, 그 안의 이슈와 PR, 다른 사람이 누른 스타까지 모두 사라져요. 내 컴퓨터의 my-notes 폴더는 남아요. GitHub에는 휴지통이 없어서 지운 레포를 다시 꺼낼 수 없어요. 그래서 오늘은 방금 만든 연습용 my-notes만 지워요. 팀 레포는 절대 지우지 않아요.", ("delete", "레포 지우기"))

o = frame("del-try", EB4, "처음 gh repo delete는 권한이 없어서 막혀요", RED)
t = Term([("$", P_HOME, "gh repo delete kim/my-notes"), ("o", ""), ("o", CONFIRM), ("e", DEL_403), ("o", DEL_HINT[0]), ("y", DEL_HINT[1])], 96, 214, size=24, w=1728, lh=1.8, tid="t-del")
t.band(5, order=3)
o.append(t.html())
o += tag(t, 2, "실수하지 않게 이름을 한 번 더 쳐요", BL, 1)
rx = t.tx
o.append(pen_box(2, round(rx - 8), round(t.top(3) + 6), round(t.sw("HTTP 403") + 16), round(t.lp - 12), RED))
o += tag(t, 3, "허락할 수 없다는 뜻", RED, 2)
o.append(shake(2, "t-del"))
o += tag(t, 5, "칠 명령까지 알려 줘요", OR, 3)
chips = [chip(k, BL, "#E3ECFD", f"k{i}") for i, (k, _) in enumerate(SC)]
chips.append(f'<div id="slot-del" style="width:300px;height:84px;flex:none;border:3px dashed {RED};border-radius:14px;font-family:{MONO};font-size:30px;font-weight:700;line-height:78px;text-align:center;color:{RED}">delete_repo ?</div>')
o.append(badge(96, 600, chips, attrs=bi("rise", 3)))
o.append(caption("고장이 아니에요. 처음 로그인할 때는 지우기 권한을 일부러 빼고 받아요.", 840, 3, size=30))
W("del-try", o, "gh repo delete kim/my-notes를 쳐요. 지울 레포 이름을 한 번 더 쳐서 확인해요. 그런데 HTTP 403 에러가 나요. 403은 요청은 알아들었지만 허락할 수 없다는 뜻이에요. 다음 줄이 이유를 알려 줘요. 이 작업에는 delete_repo 권한(scope)이 필요하고, 받으려면 gh auth refresh -h github.com -s delete_repo를 치라고 해요. 1파트의 권한 목록에 delete_repo가 없었죠? 실수로 레포를 지우지 않게 처음 로그인할 때는 이 권한을 빼고 받아요. " + MADE)

o = frame("scope", EB4, "gh auth refresh로 출입증에 지우기 권한을 더해요", RED, "magic")
chips = [chip(k, BL, "#E3ECFD", f"k{i}") for i, (k, _) in enumerate(SC)]
chips.append(f'<div id="slot-del" style="position:relative;width:300px;height:84px;flex:none;border:3px dashed {RED};border-radius:14px">'
             + p(f"position:absolute;left:-3px;top:-3px;width:300px;height:84px;border-radius:14px;background:#FBE4E2;border:3px solid {RED};font-family:{MONO};font-size:30px;font-weight:700;line-height:78px;text-align:center;color:{RED}",
                 "delete_repo", ' id="k4" data-build-in="fly order 2" data-from="seg-del"') + '</div>')
o.append(badge(96, 226, chips))
o.append(p(f"position:absolute;left:96px;top:446px;font-size:24px;color:{SUB}", "1파트 gh auth status의 Token scopes 줄이에요."))
o += parts(96, 580, [("gh auth refresh", RED, "출입증을 새로 받아요", None), ("-h github.com", RED, "어느 GitHub인지<br>(-h = host, 도움말 아님)", None), ("-s delete_repo", RED, "더할 권한(scope)", "seg-del")], size=48, order=1, lab=26)
o.append(caption("질문 네 개는 다시 묻지 않고 출입증만 다시 받아요.", 900, 2, size=30, color=SUB))
W("scope", o, "1파트에서 토큰을 출입증, 권한(scope)을 출입증으로 열 수 있는 문에 비유했어요. 지금 출입증에는 repo, read:org, gist, workflow 네 칸이 있고 delete_repo 칸이 없어요. 에러가 알려 준 명령을 나눠 읽어 봐요. gh auth refresh는 출입증을 새로 받는 명령이에요. -h github.com은 어느 GitHub인지, -s delete_repo는 더할 권한이에요. -h가 여기서는 도움말이 아니라 host(사이트 주소)의 줄임이라는 점을 짚어 주세요. 번외에서 본 예외와 같은 경우예요.")

o = frame("refresh", EB4, "브라우저에서 한 번 더 허락하면 권한이 더해져요", RED)
t = Term([("$", P_HOME, "gh auth refresh -h github.com -s delete_repo"), ("o", ""), ("y", DEVICE[0]), ("o", DEVICE[1]), ("g", "✓ Authentication complete.")], 96, 214, size=26)
o.append(t.html())
o += tag(t, 4, "권한 추가 끝", GR, 3)
rows_ = "".join(f'<div style="width:100%;display:flex;flex-direction:row;align-items:center;gap:16px;height:60px;border-top:1px solid #E6E2D9;padding:0 6px">'
                f'<x-icon name="{ic}" style="width:26px;height:26px;color:{c}"></x-icon>' + p(f"font-size:25px;font-weight:700;color:{c}", n) + '</div>'
                for ic, n, c in (("Database", "Repositories", SUB), ("Users", "Organizations", SUB)))
rows_ += (f'<div id="perm-del" style="width:100%;display:flex;flex-direction:row;align-items:center;gap:16px;height:60px;border-top:1px solid #E6E2D9;padding:0 6px">'
          f'<x-icon name="Warning" style="width:26px;height:26px;color:{RED}"></x-icon>' + p(f"font-size:25px;font-weight:700;color:{RED}", "Delete repositories") + '</div>')
binner = p(f"font-size:30px;font-weight:700;color:{INK}", "Authorize GitHub CLI") + f'<div style="width:100%">{rows_}</div>' + gh_button("Authorize github", "btn-auth2")
bx_, by_ = 820, t.y + t.h - 20
o.append(browser(bx_, by_, 760, 560, "github.com/login/device", binner, "br-auth", align="flex-start", pad="26px 40px").replace("justify-content:center;gap:22px", "justify-content:flex-start;gap:18px"))
o.append(zoom(1, bx_, by_ + 52, 760, 420, 40, 1.8))
o.append(ring(1, bx_ + 46, by_ + 52 + 26 + 45 + 18 + 120 + 10, 300, 40, RED))
o.append(p(f"position:absolute;left:96px;top:{by_ + 260}px;width:620px;font-size:30px;font-weight:700;line-height:1.45;color:{RED}", "새로 더해지는 권한이에요.<br>코드 넣기는 로그인 때와 같아요.", bi("fade", 1)))
o.append(zoom_off(2))
o.append(cursor(2, target="btn-auth2"))
o.append(cursor_off(3))
W("refresh", o, "에러가 알려 준 명령을 그대로 쳐요. 1파트 로그인 때처럼 코드가 나오고, Enter를 누르면 브라우저가 열려요. 코드를 넣고 Continue를 누르면 허락 화면이 나와요. 이번 허락 화면에는 레포 지우기 권한(Delete repositories)이 새로 들어 있어요. Authorize github를 누르고 터미널에 Authentication complete가 나오면 끝이에요. 질문 네 개는 다시 묻지 않아요. 코드는 칠 때마다 달라요. 브라우저 화면은 단순하게 그린 그림이에요.")

o = frame("status2", EB4, "권한 목록에 delete_repo가 생겼어요", RED, "magic")
t = Term([("$", P_HOME, "gh auth status")] + [("o", l) for l in STATUS] + [("o", SCOPES_DEL, {"'delete_repo'": "scdel"})], 96, 550, size=26, w=1728)
t.band(6, order=1)
o.append(t.html())
dx = t.sx(6, "'delete_repo'")
o.append(underline(1, round(dx), round(dx + t.sw("'delete_repo'")), round(t.top(6) + t.lp - 4), RED))
chips = [chip(k, BL, "#E3ECFD", f"k{i}") for i, (k, _) in enumerate(SC)]
chips.append(chip("delete_repo", RED, "#FBE4E2", "k4", w=300))
o.append(badge(96, 226, chips))
o.append(pulse(2, "k4"))
o.append(caption("이제 지우기를 다시 해 봐요.", 446, 2, size=30, color=SUB))
W("status2", o, "gh auth status를 다시 쳐서 확인해요. Token scopes 맨 앞에 delete_repo가 생겼어요. 출입증에 다섯 번째 칸이 생겼으니 이제 지우기를 다시 해 봐요. " + MADE)

o = frame("del-ok", EB4, "다시 gh repo delete를 치면 지워져요", RED)
t = Term([("$", P_HOME, "gh repo delete kim/my-notes"), ("o", ""), ("o", CONFIRM), ("g", DELETED), ("o", ""), ("$", P_HOME, "gh repo list")] + [("o", l) for l in LIST2[1:]],
         96, 214, size=24, w=1100)
t.band(3, order=1)
o.append(t.html())
o += tag(t, 3, "지워졌어요", GR, 1)
o += tag(t, 6, "my-notes가 없어요", GRAY, 1)
t2 = Term([("$", P_MN, "git push origin main"), ("e", "fatal: repository"), ("e", "'https://github.com/kim/my-notes.git/'"), ("e", "not found")], 1240, 300, size=22, w=584, tid="t-push", attrs=bi("rise", 2))
o.append(t2.html())
o.append(caption("내 폴더는 남아 있어요. GitHub 쪽이 없어서 push하면 not found가 나요.", t2.y + t2.h + 30, 2, left=1240, width=584, size=26))
o.append(caption(f"폴더도 필요 없으면 01의 {cmd('rm -r')}로 지워요.", t2.y + t2.h + 150, 2, left=1240, width=584, size=26, color=SUB))
W("del-ok", o, "같은 명령을 다시 쳐요. 이름을 한 번 더 치면 Deleted repository가 나와요. gh repo list에서도 my-notes가 사라졌어요. 내 컴퓨터의 my-notes 폴더는 남아 있어요. 거기서 git push origin main을 치면 GitHub 쪽 레포가 없어서 repository not found가 나요. 폴더가 필요 없으면 01에서 배운 rm -r로 지워요. 레포 지우기는 이름을 다시 치는 확인과 delete_repo 권한 확인, 두 번을 거쳐요. 오른쪽 에러는 화면에 맞추려고 세 줄로 나눴어요. " + MADE)

# ---------- part 5: everyday gh ----------
EB5 = "5. 자주 쓰는 gh 명령"
o = frame("issue", EB5, "gh issue create로 할 일을 이슈로 남겨요", OR)
o += parts(96, 226, [("gh issue create", INK, None, None), ('--title "소개 페이지에 사진 넣기"', OR, "제목", None), ('--body "각자 사진 한 장씩"', OR, "내용", None)], size=32, order=None, lab=24, drop=24)
t = Term([("$", P_TI, 'gh issue create --title "소개 페이지에 사진 넣기" --body "각자 사진 한 장씩 넣어요"')] + [("o", l) for l in ISSUE_NEW[1:]] + [("o", ""), ("$", P_TI, "gh issue list")] + [("o", l) for l in ISSUE_LIST[1:]],
         96, 400, size=24, w=1728)
o.append(t.html())
o += tag(t, 3, "만든 이슈 주소", OR, 1)
o.append(pen_box(2, round(t.tx - 10), round(t.top(9) - 3), round(t.sw("#1") + 20), round(t.lp + 6), OR))
o += tag(t, 9, "이슈 번호", OR, 2)
o.append(caption("--title, --body를 빼면 gh가 하나씩 물어봐요.", t.y + t.h + 40, 3, size=30, color=SUB))
W("issue", o, "이슈는 레포에 남기는 할 일 메모예요. 웹에서는 Issues 탭의 New issue 버튼으로 만들어요. gh issue create에 --title로 제목, --body로 내용을 적으면 바로 만들어지고 주소를 알려 줘요. 둘을 빼고 gh issue create만 치면 제목과 내용을 하나씩 물어봐요. gh issue list는 열려 있는 이슈 목록이에요. #1이 이슈 번호예요. 위쪽 명령 그림은 내용을 줄여 적었어요. " + MADE, ("daily", "자주 쓰는 gh 명령"))

o = frame("pr-create", EB5, "브랜치를 push한 뒤 gh pr create로 PR을 열어요", OR)
t = Term([("$", P_TI, "git checkout -b feature/kim-hobby"), ("d", BR_NEW), ("$", P_TI, "echo '취미: 등산' >> kim.md"), ("$", P_TI, "git add kim.md"),
          ("$", P_TI, "git commit -m 'feat: kim 취미 추가'")] + [("d", l) for l in COMMIT_HB] + [("$", P_TI, "git push origin feature/kim-hobby"), ("d", "…"), ("d", PUSH_HB_LAST), ("o", ""),
          ("$", P_TI, 'gh pr create --title "feat: kim 취미 추가" --body "kim.md에 취미를 적었어요"')] + [("o", l) for l in PR_NEW[1:]], 96, 214, size=23, w=1728, lh=1.45)
t.band(7, 9, order=1, color="rgba(143,179,255,.14)")
t.band(11, 14, order=2)
o.append(t.html())
o += tag(t, 7, "먼저 push", BL, 1)
o += tag(t, 14, "PR 주소", OR, 2)
W("pr-create", o, "03에서 브랜치를 만들어 push한 뒤 웹에서 Compare & pull request 버튼으로 PR을 열었어요. 위쪽은 03과 같은 순서예요. 브랜치를 만들고, 고치고, 커밋하고, git push origin feature/kim-hobby로 올려요. 아래 gh pr create가 웹 버튼을 대신해요. --title은 PR 제목, --body는 내용이에요. 꼭 push를 먼저 해요. push 전에 gh pr create를 치면 gh가 브랜치를 어디에 push할지 되물어요. push 출력의 가운데는 …로 줄였어요.")

o = frame("pr-view", EB5, "gh pr list, gh pr view로 PR을 터미널에서 봐요", OR)
t = Term([("$", P_TI, "gh pr list")] + [("o", l) for l in PR_LIST[1:]] + [("o", ""), ("$", P_TI, "gh pr view 2")] + [("o", l) for l in PR_VIEW], 96, 214, size=26, w=1728, lh=1.45)
t.band(8, order=2)
o.append(t.html())
o.append(pen_box(1, round(t.tx - 10), round(t.top(4) - 3), round(t.sw("#2") + 20), round(t.lp + 6), OR))
o += tag(t, 4, "이슈 #1 다음이라 2번", OR, 1)
o.append(caption("칠한 줄은 kim이 커밋 1개를 main에 합치고 싶다는 뜻이에요.", t.y + t.h + 36, 2, size=30))
W("pr-view", o, "gh pr list는 열린 PR 목록이에요. #2가 PR 번호예요. 이슈 #1 다음이라 2번이 됐어요. GitHub은 이슈와 PR 번호를 같이 세요. gh pr view 2는 2번 PR의 제목, 상태, 내용을 보여 줘요. 칠한 줄은 kim이 feature/kim-hobby의 커밋 1개를 main에 합치고 싶어 한다는 뜻이에요. 웹에서 보고 싶으면 gh pr view 2 --web을 쳐요.")

o = frame("pr-merge", EB5, "gh pr merge로 합치고, main은 git pull로 받아 와요", OR)
t = Term([("$", P_TI, "gh pr merge 2 --merge"), ("g", PR_MERGED), ("o", ""), ("$", P_TI, "git checkout main")] + [("o", l) for l in CO_MAIN] + [("$", P_TI, "git pull origin main"), ("d", "…")] + [("o", l) for l in PULL[2:5]],
         96, 214, size=26, w=1220)
t.band(1, order=1)
o.append(t.html())
o += tag(t, 1, "합쳤어요", OR, 1)
t2 = Term([("$", P_TI, "git log --oneline")] + [("o", l[:30] + ("…" if len(l) > 30 else "")) for l in LOG_AFTER], 1350, 214, size=18, w=474, tid="t-log", attrs=SLIDE(2, 300, 0))
t2.band(1, order=2)
o.append(t2.html())
o.append(caption(f"{cmd('--merge')}는 08에서 본 Merge 버튼 세 가지 중 Create a merge commit이에요.", 480, 3, left=1350, width=474, size=26))
W("pr-merge", o, "리뷰가 끝난 PR은 gh pr merge로 합쳐요. --merge는 08에서 본 PR Merge 버튼 세 가지 중 Create a merge commit과 같아요. --squash, --rebase 옵션도 있으니 팀이 정한 방식을 골라요. 합친 것은 GitHub의 main이라 내 컴퓨터는 아직 그대로예요. git checkout main, git pull origin main으로 받아 와요. pull 출력은 위쪽 받는 과정을 …로 줄였어요. 오른쪽 git log 맨 위에 Merge pull request #2 커밋이 생겼어요. 화면에 맞추려고 커밋 메시지 뒤를 줄였어요.")

o = frame("help", EB5, "다른 명령은 gh --help에서 찾아요", OR)
used = ("auth", "browse", "issue", "pr", "repo")
lines = [("$", P_HOME, "gh --help")]
for l in GH_HELP:
    lines.append(("d", l) if l == "  …" else ("o", l))
t = Term(lines, 96, 214, size=22, w=1180, lh=1.42)
for i, l in enumerate(GH_HELP, 1):
    if l.startswith("  ") and l.split(":")[0].strip() in used:
        t.band(i, order=1)
o.append(t.html())
o.append(p(f"position:absolute;left:1340px;top:240px;font-size:26px;font-weight:700;color:{OR}", "칠한 줄이 오늘 쓴 묶음이에요.", bi("fade", 1)))
o.append(p(f"position:absolute;left:1340px;top:400px;font-size:26px;font-weight:700;color:{INK}", "한 단계 더 보려면", bi("fade", 2)))
t2 = Term([("$", P_HOME, "gh repo --help"), ("$", P_HOME, "gh pr create --help")], 1340, 450, size=24, w=484, tid="t-more", bar=False, attrs=bi("rise", 2))
o.append(t2.html())
o.append(p(f"position:absolute;left:1340px;top:{450 + t2.h + 24}px;width:484px;font-size:24px;line-height:1.5;color:{SUB}", "묶음 뒤에 붙이면 할 일 목록, 할 일 뒤에 붙이면 옵션 목록이 나와요.", bi("fade", 2)))
W("help", o, "gh --help는 gh의 명령 묶음 목록이에요. 칠한 줄이 오늘 쓴 다섯 묶음이에요. 묶음 이름 뒤에 --help를 붙이면 그 안의 할 일 목록이, 할 일 뒤에 붙이면 옵션 목록이 나와요. 번외 터미널 환경에 적응하기의 도움말 읽는 법이 gh에도 그대로 통해요. 출력은 tools/demo.sh에서 실제로 실행한 결과고 아래쪽은 …로 줄였어요.")

# ---------- summary ----------
EB6 = "정리"
o = frame("trouble", EB6, "gh에서 막히면 이렇게 풀어요", RED)
tr = [("gh: command not found", "설치 직후 터미널이 gh를 몰라요", "터미널 껐다 켜기"), ("You are not logged into any GitHub hosts", "아직 로그인 전이에요", "gh auth login"),
      ('needs the "delete_repo" scope', "지우기 권한이 없어요", "gh auth refresh -h github.com -s delete_repo"),
      ("failed to run git: fatal: not a git repository", "레포 폴더 밖에서 쳤어요", "pwd 뒤 cd 레포폴더"),
      ("Where should we push the 'feature/…' branch?", "브랜치를 push하기 전에 PR을 만들었어요", "Ctrl+C 뒤 git push origin 브랜치"),
      ("브라우저가 안 열려요", "주소를 직접 열어요", "github.com/login/device")]
o.append(p(f"position:absolute;left:96px;top:214px;font-size:24px;font-weight:700;color:{GRAY}", "이런 글이 보이면"))
o.append(p(f"position:absolute;left:1140px;top:214px;font-size:24px;font-weight:700;color:{GRAY}", "이렇게 해요"))
for i, (q, a_, c_) in enumerate(tr):
    y = 262 + i * 122
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:1px;background:{LINE}"></div>')
    mono = q.isascii()
    ra = bi("rise", 1) + DELAY(i * 80)
    o.append(p(f"position:absolute;left:96px;top:{y + 18}px;width:1000px;{'font-family:' + MONO + ';font-size:25px;' if mono else 'font-size:28px;'}font-weight:700;color:{RED if mono else INK}", e(q), ra))
    o.append(p(f"position:absolute;left:96px;top:{y + 66}px;width:1000px;font-size:24px;color:{SUB}", e(a_), ra))
    o.append(p(f"position:absolute;left:1140px;top:{y + 38}px;width:684px;font-family:{MONO};font-size:{22 if len(c_) > 30 else 25}px;font-weight:700;color:{INK};white-space:nowrap", e(c_), ra))
o.append(f'<div style="position:absolute;left:96px;top:{262 + 6 * 122}px;width:1728px;height:1px;background:{LINE}"></div>')
W("trouble", o, "첫 줄은 설치 직후 자주 나요. 터미널을 껐다 켜면 새로 설치한 gh를 찾아요. 둘째 줄은 로그인 전이라는 뜻이에요. 셋째 줄은 4파트에서 본 권한 에러예요. 넷째 줄은 레포 폴더 밖에서 gh repo view, gh pr list처럼 지금 레포를 쓰는 명령을 쳤을 때예요. pwd로 위치를 보고 레포 폴더로 들어가요. 다섯째 줄은 브랜치를 push하기 전에 gh pr create를 쳤을 때 나오는 질문이에요. Ctrl+C로 멈추고 git push origin 브랜치이름을 친 뒤 다시 해요. 여섯째 줄은 브라우저가 저절로 안 열릴 때예요. 터미널의 코드를 보고 주소를 직접 열어요. 넷째 줄은 실제로 뒤에 (or any of the parent directories): .git이 더 붙어요. 다섯째 줄 질문의 선택지 중 Cancel을 골라도 멈춰요.", ("trouble", "정리"))

o = frame("cheatsheet", EB6, "한 장 요약", INK)
groups = [("로그인", BL, [("gh auth login", "로그인"), ("gh auth status", "로그인 상태, 권한"), ("gh auth refresh -s 권한", "권한 더하기")]),
          ("레포", GR, [("gh repo clone 주인/이름", "받기"), ("gh repo view", "지금 레포 보기"), ("gh repo list", "내 레포 목록"), ("gh repo create 이름 …", "만들기"), ("gh repo delete 주인/이름", "지우기")]),
          ("이슈와 PR", OR, [("gh issue create", "이슈 만들기"), ("gh issue list", "이슈 목록"), ("gh pr create", "PR 만들기"), ("gh pr list / view", "PR 보기"), ("gh pr merge 번호", "PR 합치기")])]
for i, (t_, c, rows) in enumerate(groups):
    x = 96 + i * 600
    o.append(p(f"position:absolute;left:{x}px;top:220px;font-size:30px;font-weight:700;color:{c}", e(t_)))
    o.append(f'<div style="position:absolute;left:{x}px;top:270px;width:540px;height:3px;background:{c}"></div>')
    for j, (k, d) in enumerate(rows):
        y = 296 + j * 104
        o.append(p(f"position:absolute;left:{x}px;top:{y}px;width:560px;font-family:{MONO};font-size:26px;font-weight:700;color:{INK};white-space:nowrap", e(k)))
        o.append(p(f"position:absolute;left:{x}px;top:{y + 42}px;width:540px;font-size:23px;color:{SUB}", e(d)))
o.append(caption("커밋과 push는 git으로, 웹 버튼은 gh로 해요.", 860, None, size=32))
o.append(caption("레포 지우기는 되돌릴 수 없어요. 지우기 전에 주인/이름을 한 번 더 확인해요.", 914, None, size=28, color=SUB))
W("cheatsheet", o, "오늘 쓴 명령을 세 묶음으로 모았어요. 로그인 세 개, 레포 다섯 개, 이슈와 PR 다섯 개예요. 커밋과 push, pull은 계속 git으로 하고, 웹사이트에서 누르던 버튼은 gh로 해요. 다음 수업부터 팀 레포를 만들 때 gh repo create로 시작해 봐요.")

# ---------- toc ----------
page = {sid: i + 1 for i, sid in enumerate(ORDER)}
plist = [(BL, "설치하고 로그인하기", "gh auth login, 권한 목록, git도 같이 로그인", "install", "gitcred"),
         (GR, "이미 있는 레포 연결하기", "gh repo clone, view, browse, list", "clone", "repo-list"),
         (TEAL, "새 레포 만들기", "gh repo create 뒤 git push origin main", "create-why", "create-ask"),
         (RED, "레포 지우기와 권한 추가", "delete가 막힐 때 gh auth refresh", "del-warn", "del-ok"),
         (OR, "자주 쓰는 gh 명령", "이슈, PR 만들기와 합치기", "issue", "help")]
o = frame("toc", "", "오늘의 순서", INK)
o[0] = o[0]
for i, (c, h, s_, a, b) in enumerate(plist):
    y = 220 + i * 136
    o.append(f'<div style="position:absolute;left:96px;top:{y}px;width:1728px;height:1px;background:{LINE}"></div>')
    o.append(p(f"position:absolute;left:96px;top:{y + 22}px;width:80px;font-size:60px;font-weight:900;line-height:1.5;color:{c}", str(i + 1)))
    o.append(p(f"position:absolute;left:200px;top:{y + 24}px;font-size:38px;font-weight:700;color:{INK}", h))
    o.append(p(f"position:absolute;left:200px;top:{y + 80}px;font-family:{MONO};font-size:24px;font-weight:700;color:{SUB}", e(s_)))
    o.append(p(f"position:absolute;left:1524px;top:{y + 40}px;width:300px;text-align:right;font-size:30px;font-weight:700;color:{GRAY}", f"{page[a]}–{page[b]}쪽"))
o.append(f'<div style="position:absolute;left:96px;top:{220 + 5 * 136}px;width:1728px;height:1px;background:{LINE}"></div>')
o.append(p(f"position:absolute;left:96px;top:940px;font-size:26px;color:{SUB}", f"{page['why']}–{page['map']}쪽은 들어가기, {page['trouble']}–{page['cheatsheet']}쪽은 막힐 때와 한 장 요약이에요."))
o = [x for x in o if 'id="eyebrow"' not in x]
with open(os.path.join(OUT, "toc.html"), "w") as f:
    f.write("\n".join(o) + f"\n<aside>{e('다섯 파트로 나눴어요. 1파트에서 한 번 로그인해 두면 나머지는 모두 그 로그인을 써요. 2파트는 06의 team-intro를, 3파트와 4파트는 새로 만드는 연습용 레포 my-notes를 써요. 5파트는 다시 team-intro로 돌아와요.')}</aside>\n</section>\n")

deck = {"v": 4, "createdOnFiles": {"v": 1, "at": "2026-11-02T02:00:00Z"}, "lists": "css", "title": "터미널에서 GitHub 다루기", "order": ORDER,
        "sections": SECTIONS,
        "faces": {"noto-sans-kr": {"family": "Noto Sans KR", "href": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap"},
                  "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"}},
        "designSystems": []}
with open(os.path.join(OUT, "deck.json"), "w") as f:
    json.dump(deck, f, ensure_ascii=False, indent=2)
for w_ in WARN:
    print("WARN", w_)
print(len(ORDER), "slides")
