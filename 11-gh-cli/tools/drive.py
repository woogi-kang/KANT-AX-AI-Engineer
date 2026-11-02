"""Run gh/git commands in a pty as kim, answer prompts, and return what stays on screen.
import drive; drive.run(cwd, cmd, [(pattern, keys), ...])"""
import os, re, sys, pexpect

ENV = {"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": "/home/kim", "TERM": "xterm", "LANG": "C.UTF-8",
       "SSL_CERT_FILE": os.environ["GH_DEMO_CA"], "GIT_SSL_CAINFO": os.environ["GH_DEMO_CA"],
       "BROWSER": "true", "GH_NO_UPDATE_NOTIFIER": "1", "NO_COLOR": "1",
       "GIT_PAGER": "cat", "GH_PAGER": "cat", "PAGER": "cat", "GIT_TERMINAL_PROMPT": "0"}
KEYS = {"ENTER": "\r", "DOWN": "\x1b[B", "UP": "\x1b[A"}
TOK = re.compile(rb"\x1b\[(\??)(\d*)(?:;(\d+))?([A-Za-z])|\x1b([78])|\r\n|\r|\n|[^\x1b\r\n]+", re.S)


def render(raw):
    lines, y, x, sv = [""], 0, 0, (0, 0)
    for m in TOK.finditer(raw):
        t = m.group(0)
        if m.group(4):
            q, n, cmd = m.group(1), int(m.group(2) or 1), m.group(4).decode()
            if q:
                continue
            if cmd == "A":
                y = max(0, y - n)
            elif cmd == "B":
                y += n
            elif cmd == "G":
                x = 0
            elif cmd == "D":
                x = max(0, x - n)
            elif cmd in "fH":
                continue
            elif cmd == "K":
                while len(lines) <= y:
                    lines.append("")
                lines[y] = "" if m.group(2) == b"2" else lines[y][:x]
            while len(lines) <= y:
                lines.append("")
            continue
        if m.group(5):
            if m.group(5) == b"7":
                sv = (y, x)
            else:
                y, x = sv
            continue
        if t in (b"\r\n", b"\n"):
            y += 1
            x = 0
        elif t == b"\r":
            x = 0
        else:
            s = t.decode("utf-8", "replace")
            while len(lines) <= y:
                lines.append("")
            ln = lines[y].ljust(x)
            lines[y] = ln[:x] + s + ln[x + len(s):]
            x += len(s)
        while len(lines) <= y:
            lines.append("")
    while lines and not lines[-1].strip():
        lines.pop()
    return [l.rstrip() for l in lines]


def run(cwd, cmd, steps=()):
    child = pexpect.spawn("/bin/bash", ["-c", cmd], cwd=cwd, env=ENV, dimensions=(60, 200), timeout=20)
    raw = b""
    for exp, send in list(steps) + [(None, None)]:
        while True:
            i = child.expect([pexpect.EOF if exp is None else exp, rb"\x1b\[6n"], timeout=30)
            raw += child.before + (child.after if isinstance(child.after, bytes) else b"")
            if i == 0:
                break
            child.send("\x1b[1;1R")
        if send:
            for tok in send.split("+"):
                child.send(KEYS.get(tok, tok))
    child.close()
    raw = raw.replace(b"\x1b[6n", b"")
    return render(raw), child.exitstatus
