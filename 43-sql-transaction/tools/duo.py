"""Runs two psql windows side by side in real pseudo-terminals, for the two-window scenes of the SQL 8 deck (43).

steps is a list of (window, line) pairs, "A" or "B", typed in that order. After each line the runner waits until that
window shows its prompt again, or gives up after `block` seconds (an UPDATE waiting for the other window's lock never
prints a prompt). ("snap", name) saves both screens as they are at that moment. Returns {name: {"A": lines, "B": lines}}
with "end" added after the last step."""
import os, pty, re, select, time
import pyte


class Win:
    def __init__(self, cmd, cwd, env, cols):
        self.cols = cols
        pid, fd = pty.fork()
        if pid == 0:
            os.chdir(cwd)
            os.environ.update(env or {})
            os.environ["TERM"] = "xterm"
            os.execvp("bash", ["bash", "--noprofile", "--norc", "-c", f"stty cols {cols} rows 50; {cmd}"])
        self.pid, self.fd, self.raw, self.alive = pid, fd, b"", True

    def pump(self, timeout):
        if not self.alive:
            return False
        r, _, _ = select.select([self.fd], [], [], timeout)
        if not r:
            return False
        try:
            chunk = os.read(self.fd, 65536)
        except OSError:
            chunk = b""
        if not chunk:
            self.alive = False
            return False
        self.raw += chunk
        return True

    def screen(self):
        s = pyte.Screen(self.cols, 400)
        pyte.ByteStream(s).feed(self.raw)
        lines = [l.rstrip() for l in s.display]
        while lines and not lines[-1]:
            lines.pop()
        return lines

    def type(self, line):
        for ch in line:
            os.write(self.fd, ch.encode())
            time.sleep(0.01)
        os.write(self.fd, b"\r")


def run(cmd, cwd, steps, prompt, env=None, cols=100, block=2.5):
    wins = {"A": Win(cmd, cwd, env, cols), "B": Win(cmd, cwd, env, cols)}
    pat = re.compile(prompt.encode() if isinstance(prompt, str) else prompt)

    def settle(w, need_prompt, limit):
        t0 = time.time()
        mark = len(w.raw)
        while time.time() - t0 < limit:
            got = w.pump(0.3)
            if not got and need_prompt and len(w.raw) > mark and pat.search(w.raw.rstrip(b" ")[-40:] + b" "):
                return
            if not got and not w.alive:
                return

    for w in wins.values():          # wait for both banners and first prompts
        t0 = time.time()
        while time.time() - t0 < 15 and not pat.search(w.raw.rstrip(b" ")[-40:] + b" "):
            w.pump(0.3)
    snaps = {}
    for who, line in steps:
        if who == "snap":
            for w in wins.values():
                w.pump(0.4)
            snaps[line] = {k: w.screen() for k, w in wins.items()}
            continue
        w = wins[who]
        w.type(line)
        settle(w, True, block)
        for k, o in wins.items():    # a waiting window may have just been released
            if k != who:
                o.pump(0.5)
    for w in wins.values():
        w.pump(0.5)
    snaps["end"] = {k: w.screen() for k, w in wins.items()}
    for w in wins.values():
        if w.alive:
            w.type("\\q")
            w.pump(1)
        try:
            os.waitpid(w.pid, 0)
        except ChildProcessError:
            pass
    return snaps
