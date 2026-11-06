"""Generates the hand-laid slides of the Linux terminal deck: toc, why, prompt, warn, warn-rf, keys, cheatsheet.
Usage: python3 tools/gen_pages.py slides

Layout (2026-11-06, after the Stageshow skill): one object leads each slide (a terminal, a prompt line, a key
cap); lists sit on the page with thin rules between rows instead of a white card per item; labels hang off
the object they name on a thin stem."""
import html, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from highlight import underline  # noqa: E402

OUT = sys.argv[1]
SANS = "'Noto Sans KR', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Noto Sans KR', monospace"
INK, SUB, GRAY, RULE, BLUE = "#1D2330", "#4A5262", "#6A7180", "#E1DED6", "#2459C9"


def e(s):
    return html.escape(s, quote=False)


def p(style, text, attrs=""):
    return f'<p{attrs} style="{style}">{text}</p>'


def light(sec_id, title, extra=""):
    return [f'<section id="{sec_id}" data-transition="fade" style="background:#F6F5F1;color:{INK};font-family:{SANS};word-break:keep-all;padding:128px;display:flex;flex-direction:column{extra}">',
            f'<h2 style="position:absolute;left:128px;top:96px;width:1664px;font-size:60px;font-weight:700;line-height:1.15;color:{INK}">{title}</h2>']


def write(sec_id, parts, notes):
    with open(os.path.join(OUT, f"{sec_id}.html"), "w") as f:
        f.write("\n".join(parts) + f"\n<aside>{e(notes)}</aside>\n</section>\n")


def dots(gap=10):
    return (f'<div style="display:flex;flex-direction:row;gap:{gap}px;align-items:center">'
            + "".join(f'<div style="width:16px;height:16px;border-radius:8px;background:{c}"></div>' for c in ("#F28B82", "#F2C46D", "#7FD18B")) + '</div>')


# ---------- toc: two columns of four parts, thin rules, no cards ----------
PARTS = [("1", "개념 잡기", "터미널 · 프롬프트 · 폴더 트리", "3–5쪽", "#3A4150"),
         ("2", "둘러보기", "pwd · ls · mkdir · cd", "6–9쪽", "#1F8A4C"),
         ("3", "파일 만들기", "touch · echo · cat · 마크다운", "10–13쪽", BLUE),
         ("4", "경로", "절대 · 상대 경로 · . .. ~ /", "14–19쪽", "#6B47D6"),
         ("5", "옮기고 지우기", "mv · cp · rm · rm -r · rm -rf", "20–27쪽", "#B26A00"),
         ("6", "더 편하게", "ls -a · ls -al · Tab · 위 화살표", "28–30쪽", "#1D6B70"),
         ("7", "막힐 때", "자주 보는 에러 3가지", "31–33쪽", "#A33131"),
         ("8", "한 장 요약", "명령 모아 보기", "34쪽", INK)]
o = light("toc", "오늘의 순서")
for i, (n, t, sub, pg, c) in enumerate(PARTS):
    x, y = 128 + (i // 4) * 864, 236 + (i % 4) * 176
    o.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:800px;height:176px;border-top:2px solid {RULE};display:flex;flex-direction:row;gap:32px;align-items:center">'
             + p(f"font-size:64px;font-weight:900;line-height:1;width:56px;color:{c}", n)
             + '<div style="flex:1;display:flex;flex-direction:column;gap:10px">'
             + p(f"font-size:40px;font-weight:700;line-height:1.25;color:{INK}", e(t))
             + p(f"font-family:{MONO};font-size:26px;line-height:1.4;color:{GRAY}", e(sub)) + '</div>'
             + p(f"font-size:26px;font-weight:700;color:{GRAY};white-space:nowrap", pg) + '</div>')
write("toc", o, "6~33쪽은 kant 폴더 하나로 이어지는 실습이에요. 오른쪽 폴더 지도와 파란 현재 위치 표시를 계속 따라가요.")

# ---------- why: the folder window and the terminal show the same two folders ----------
o = light("why", "터미널은 글자로 다루는 폴더 창이에요")
W, H, TOP = 760, 520, 276
o.append(p(f"position:absolute;left:128px;top:{TOP-52}px;width:{W}px;font-size:28px;font-weight:700;color:{GRAY}", "마우스로 보기"))
folder = lambda name: (f'<div style="display:flex;flex-direction:column;gap:18px;align-items:center">'
                       f'<div style="width:176px;height:132px;background:#F2C46D;border-radius:14px;border-top:18px solid #E0A84A"></div>'
                       + p(f"font-size:32px;font-weight:700;color:{INK}", name) + '</div>')
o.append(f'<div style="position:absolute;left:128px;top:{TOP}px;width:{W}px;height:{H}px;background:#FFFFFF;border:2px solid #D9D5CB;border-radius:20px;display:flex;flex-direction:column">'
         f'<div style="display:flex;flex-direction:row;gap:20px;align-items:center;background:#ECEAE3;border-radius:18px 18px 0 0;padding:18px 24px">{dots()}'
         + p(f"font-size:26px;font-weight:700;color:{SUB}", "kim") + '</div>'
         f'<div style="flex:1;display:flex;flex-direction:row;gap:96px;align-items:center;justify-content:center">{folder("Desktop")}{folder("Documents")}</div></div>')
o.append(p(f"position:absolute;left:{128+W}px;top:{TOP+H//2-56}px;width:{1664-2*W}px;font-size:96px;font-weight:900;line-height:1;text-align:center;color:#9AA0AB", "="))
TX = 1792 - W
o.append(p(f"position:absolute;left:{TX}px;top:{TOP-52}px;width:{W}px;font-size:28px;font-weight:700;color:{GRAY}", "글자로 보기"))
o.append(f'<div data-build-in="rise order 1" style="position:absolute;left:{TX}px;top:{TOP}px;width:{W}px;height:{H}px;background:#1B2029;border-radius:20px;padding:26px 32px;display:flex;flex-direction:column;gap:6px;font-family:{MONO}">'
         f'<div style="padding:0 0 22px 0">{dots()}</div>'
         + p("font-size:48px;line-height:1.45;white-space:nowrap;color:#F2C46D", f'<span style="color:#8FB3FF">~ $</span> ls')
         + p("font-size:48px;line-height:1.45;white-space:nowrap;color:#D8DEE9", "Desktop&#160;&#160;Documents")
         + p("font-size:48px;line-height:1.45;white-space:nowrap;color:#8FB3FF", '~ $ <span style="display:inline-block;width:26px;height:52px;vertical-align:-8px;background:#D8DEE9"></span>')
         + '</div>')
o.append(p(f"position:absolute;left:128px;top:{TOP+H+56}px;width:1664px;font-size:32px;line-height:1.5;color:{SUB}",
           "개발 도구는 대부분 터미널에서 실행해요. 그래서 폴더를 글자로 다루는 법부터 익혀요.", ' data-build-in="fade order 2"'))
write("why", o, "Finder나 파일 탐색기에서 보던 폴더를 글자로 보는 창이 터미널이에요. Mac은 터미널 앱, Windows는 Git을 설치할 때 같이 깔린 Git Bash를 열어요. 둘 다 오늘 배우는 명령이 똑같이 동작해요.")

# ---------- prompt: one prompt line, labels on stems, three real prompts compared ----------
o = light("prompt", "프롬프트에 현재 위치가 보여요")
CW, X0 = 43.2, 192                       # JetBrains Mono 72px advance, text left
o.append('<div style="position:absolute;left:128px;top:236px;width:1664px;height:200px;background:#1B2029;border-radius:20px"></div>')
o.append(p(f"position:absolute;left:{X0}px;top:288px;width:1200px;font-family:{MONO};font-size:72px;font-weight:700;line-height:1.3;white-space:nowrap;color:#D8DEE9",
           '<span style="color:#7FD18B">kim</span>@<span style="color:#F2C46D">laptop</span>:<span style="color:#8FB3FF">~/kant</span><span style="color:#F2C46D">$</span>'))
o.append(f'<div style="position:absolute;left:{X0 + 19 * CW:.0f}px;top:298px;width:36px;height:76px;background:#D8DEE9"></div>')
STEMS = [(0, 3, "사용자 이름", "#1A7340", 1), (4, 10, "컴퓨터 이름", "#8A5200", 2), (11, 17, "현재 위치", BLUE, 3), (19, 20, "입력 자리", "#8A5200", 4)]
for a, b, t, c, k in STEMS:
    cx = round(X0 + (a + b) / 2 * CW)
    big = t == "현재 위치"
    at = f' data-build-in="fade order 1"'
    o.append(f'<div{at} style="position:absolute;left:{cx-5}px;top:452px;width:10px;height:10px;border-radius:5px;background:{c}"></div>')
    o.append(f'<div{at} style="position:absolute;left:{cx-1}px;top:458px;width:2px;height:40px;background:{c}"></div>')
    o.append(p(f"position:absolute;left:{cx-150}px;top:506px;width:300px;font-size:{34 if big else 28}px;font-weight:700;line-height:1.3;text-align:center;color:{c}", e(t), at))
o.append(underline(2, round(X0 + 11 * CW), round(X0 + 16.6 * CW), 394, color="#5B8DEF", width=7))
COLS = [("Mac 터미널 앱", f'kim@MacBook <span style="color:{BLUE}">kant</span> %', GRAY),
        ("Windows Git Bash", f'kim@DESKTOP MINGW64 <span style="color:{BLUE}">~/kant</span><br>$', GRAY),
        ("이 자료에서는", f'<span style="color:{BLUE}">~/kant</span> $', BLUE)]
o.append(f'<div data-build-in="rise order 3" style="position:absolute;left:128px;top:668px;width:1664px;height:2px;background:{RULE}"></div>')
for (lab, pr, c), x, w in zip(COLS, (128, 640, 1312), (480, 640, 480)):
    o.append(f'<div data-build-in="rise order 3" style="position:absolute;left:{x}px;top:716px;width:{w}px;display:flex;flex-direction:column;gap:20px">'
             + p(f"font-size:30px;font-weight:700;color:{c}", e(lab))
             + p(f"font-family:{MONO};font-size:40px;font-weight:700;line-height:1.5;color:{INK}", pr) + '</div>')
write("prompt", o, "프롬프트는 명령을 기다리는 줄이에요. 컴퓨터마다 모양은 달라도 현재 위치가 꼭 들어 있어요. $ 뒤에 명령을 쳐요. 이 자료에서는 화면을 아끼려고 현재 위치와 $ 만 남긴 짧은 모양으로 보여 줘요. Mac은 맨 끝이 $ 대신 % 예요. 자료의 명령을 따라 칠 때 $ 는 치지 않아요.")


# ---------- warn, warn-rf: dark statement slides, the commands are the objects ----------
def dark(sec_id):
    return [f'<section id="{sec_id}" data-transition="fade" style="background:#1D2330;color:#F6F5F1;font-family:{SANS};word-break:keep-all;padding:128px;display:flex;flex-direction:column;justify-content:center;gap:40px">',
            '<x-icon name="Warning" style="width:96px;height:96px;color:#F28B82"></x-icon>']


o = dark("warn")
o.append(p("font-size:80px;font-weight:900;line-height:1.15;color:#F6F5F1", "rm은 휴지통을<br>거치지 않아요"))
o.append(p("font-size:40px;line-height:1.4;color:#BFC6D4", "지운 파일은 되살릴 수 없어요."))
steps = [("pwd", "지금 위치 확인"), ("ls", "지울 이름 확인"), ("rm", "그다음 지우기")]
row = ['<div style="display:flex;flex-direction:row;gap:0;align-items:flex-start;margin-top:24px">']
for i, (c, t) in enumerate(steps):
    if i:
        row.append(p("font-size:56px;line-height:72px;width:120px;text-align:center;color:#6A7180", "›", f' data-build-in="fade order {i+1}"'))
    row.append(f'<div data-build-in="rise order {i+1}" style="width:400px;display:flex;flex-direction:column;gap:12px">'
               + p(f"font-family:{MONO};font-size:64px;font-weight:700;line-height:72px;color:{'#F28B82' if c == 'rm' else '#F2C46D'}", c)
               + p("font-size:30px;line-height:1.4;color:#BFC6D4", e(t)) + '</div>')
o.append("".join(row) + '</div>')
write("warn", o, "마우스로 지울 때와 달리 rm은 확인도 묻지 않고 휴지통도 거치지 않아요. 그래서 지우기 전에 pwd와 ls로 위치와 이름을 꼭 확인하는 습관을 들여요. 다음 두 장면에서 파일과 폴더를 지워 봐요.")

o = dark("warn-rf")
o.append(p("font-size:80px;font-weight:900;line-height:1.15;color:#F6F5F1", "rm -rf를 치기 전에는<br>한 번 멈춰요"))
o.append(p("font-size:40px;line-height:1.4;color:#BFC6D4", "아래 명령은 절대 치지 않아요."))
rows = [("rm -rf ~", "내 홈 폴더 전부가 사라져요"), ("rm -rf /", "컴퓨터 전체가 사라져요"), ("rm -rf *", "지금 폴더 안 전부가 사라져요")]
o.append('<div style="display:flex;flex-direction:column">' + "".join(
    f'<div data-build-in="rise order {i+1}" style="height:96px;border-top:2px solid #3A4150;display:flex;flex-direction:row;align-items:center">'
    + p(f"font-family:{MONO};font-size:48px;font-weight:700;width:420px;color:#F28B82", e(c))
    + p("font-size:34px;color:#D8DEE9", e(t)) + '</div>' for i, (c, t) in enumerate(rows)) + '</div>')
write("warn-rf", o, "-f 때문에 rm -rf는 확인도 묻지 않고 에러도 알려 주지 않아요. 경로에 띄어쓰기 하나만 잘못 들어가도 엉뚱한 폴더가 지워져요. 예를 들어 rm -rf old /는 old와 맨 위 폴더 / 를 따로 지우라는 뜻이 돼요. 인터넷에서 본 rm -rf 명령을 그대로 복사해 붙이지 않아요. 치기 전에 pwd로 위치를, ls로 지울 이름을 확인해요. * 는 지금 폴더의 모든 이름을 뜻하는 기호예요.")

# ---------- keys: the key caps lead, each row says what it does and one example ----------
o = light("keys", "키 세 개와 clear로 손을 덜 써요")
KEYS = [("Tab", "이름 자동 완성", f'<span style="font-family:{MONO}">cd no</span> 까지 치고 Tab을 누르면 <span style="font-family:{MONO}">cd notes/</span> 로 채워져요'),
        ("↑", "방금 친 명령 다시 불러오기", "누를수록 더 옛날 명령이 나와요"),
        ("Ctrl + C", "실행 멈추기, 치던 줄 취소", "터미널이 멈춘 것 같을 때 먼저 눌러 봐요"),
        ("clear", "화면 비우기", "파일은 그대로 두고 화면만 깨끗하게 해요")]
for i, (k, t, sb) in enumerate(KEYS):
    top = 236 + i * 180
    o.append(f'<div data-build-in="rise order {i+1}" style="position:absolute;left:128px;top:{top}px;width:1664px;height:180px;border-top:2px solid {RULE};display:flex;flex-direction:row;gap:56px;align-items:center">'
             f'<div style="width:300px;height:116px;flex:none;background:#FDFCF9;border:3px solid #9AA0AB;border-bottom:12px solid #9AA0AB;border-radius:18px;display:flex;align-items:center;justify-content:center">'
             + p(f"font-family:{MONO};font-size:44px;font-weight:700;color:{INK}", e(k)) + '</div>'
             f'<div style="flex:1;display:flex;flex-direction:column;gap:10px">' + p("font-size:40px;font-weight:700;line-height:1.3;color:#1D6B70", e(t))
             + p(f"font-size:30px;line-height:1.4;color:{SUB}", sb) + '</div></div>')
write("keys", o, "Tab은 이름을 앞 몇 글자만 치고 누르면 나머지를 채워 줘요. 오타가 줄고 폴더가 있는지도 바로 알 수 있어요. 후보가 여러 개면 Tab을 두 번 눌러 목록을 봐요. clear 대신 Ctrl + L 을 눌러도 화면이 비워져요.")

# ---------- cheatsheet: six groups on the page, a colored rule on top of each, no cards ----------
GROUPS = [("위치 보기", "#1A7340", [("pwd", "지금 위치 주소"), ("ls", "안에 든 것"), ("ls -a", "숨김까지 전부"), ("ls -al", "숨김까지 자세히")]),
          ("이동", "#5A3BB8", [("cd 폴더", "들어가기"), ("cd ..", "한 칸 위로"), ("cd ~", "홈 폴더로")]),
          ("만들고 읽기", "#1E3F8F", [("mkdir 폴더", "폴더 만들기"), ("touch 파일", "빈 파일 만들기"), ('echo "글" > 파일', "파일에 쓰기"), ("cat 파일", "내용 보기")]),
          ("옮기기", "#8A5200", [("mv 파일 폴더/", "다른 폴더로"), ("mv 옛이름 새이름", "이름 바꾸기"), ("cp 원본 복사본", "복사하기")]),
          ("지우기", "#A33131", [("rm 파일", "파일 지우기"), ("rm -r 폴더", "폴더째 지우기"), ("rm -rf 폴더", "묻지 않고 지우기")]),
          ("막히면", "#1D6B70", [("pwd", "어디 있는지"), ("ls", "이름이 맞는지"), ("Tab", "이름 자동 완성")])]
o = light("cheatsheet", "한 장 요약")
for i, (g, c, items) in enumerate(GROUPS):
    x, y = 128 + (i % 3) * 568, 236 + (i // 3) * 400
    o.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:528px;border-top:6px solid {c};padding-top:22px;display:flex;flex-direction:column;gap:16px">'
             + p(f"font-size:34px;font-weight:700;color:{c};margin-bottom:6px", e(g))
             + "".join('<div style="display:flex;flex-direction:row;align-items:baseline">'
                       + p(f"font-family:{MONO};font-size:28px;font-weight:700;width:300px;white-space:nowrap;color:{INK}", e(cmd))
                       + p(f"font-size:28px;color:{SUB};white-space:nowrap", e(m)) + '</div>' for cmd, m in items) + '</div>')
write("cheatsheet", o, "수업 끝에 이 장을 띄워 두고, 명령을 하나씩 가리키며 폴더 지도에서 무엇이 바뀌는지 학생이 직접 말해 보게 해요. 막히면 pwd와 ls 두 가지부터 쳐요.")
print("ok")
