"""Runs a command in a real pseudo-terminal (80 columns) and returns the screen a student would see at the end.
docker build and docker compose redraw their progress lines; pyte replays the escape codes so only the final
screen is kept. inputs are typed one by one after the shell inside shows its prompt (for docker exec -it)."""
import os, pty, select, time, re
import pyte


def run(cmd, cwd, inputs=(), cols=80, rows=400, prompt=rb"# $", env=None, wait=0.6):
    pid, fd = pty.fork()
    if pid == 0:
        os.chdir(cwd)
        os.environ.update(env or {})
        os.environ["TERM"] = "xterm"
        os.execvp("bash", ["bash", "--noprofile", "--norc", "-c", f"stty cols {cols} rows 50; {cmd}"])
    raw, pending = b"", list(inputs)

    def read(timeout):
        nonlocal raw
        r, _, _ = select.select([fd], [], [], timeout)
        if not r:
            return False
        try:
            chunk = os.read(fd, 65536)
        except OSError:
            raise EOFError
        if not chunk:
            raise EOFError
        raw += chunk
        return True

    try:
        while True:
            got = read(wait)
            if not got and pending and re.search(prompt, raw.rstrip(b" ")[-40:] + b" "):
                line = pending.pop(0)
                for ch in line:          # typed, not pasted
                    os.write(fd, ch.encode())
                    time.sleep(0.01)
                os.write(fd, b"\r")
    except EOFError:
        pass
    os.waitpid(pid, 0)
    screen = pyte.Screen(cols, rows)
    stream = pyte.ByteStream(screen)
    stream.feed(raw)
    lines = [l.rstrip() for l in screen.display]
    while lines and not lines[-1]:
        lines.pop()
    return lines
