"""Runs every Docker command the deck shows, for real, and saves what the terminal printed in tools/out.json.

Needs a running Docker daemon (in the cloud container: sudo -n dockerd &) and uv. Run from 30-docker-image:
    uv run --with pyte python tools/demo.py
The student's folder is /home/kim/cafe (nginx page), so prompts read ~/cafe. The friend in example 2 is /home/lee.
Only official images from Docker Hub (nginx); the class does not make its own images.
Commands that redraw the screen (pull, compose, exec -it) run in a real 80-column terminal (tools/ptyrun.py).
"""
import json, os, re, shutil, subprocess, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ptyrun  # noqa: E402

HOME = "/home/kim"
CAFE, LEE = f"{HOME}/cafe", "/home/lee"
ENV = {"HOME": HOME, "NO_COLOR": "1"}
OUT = {}

from files import SITE1, SITE2, COMPOSE  # noqa: E402


def sh(cmd, cwd=HOME, check=False):
    r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, env={**os.environ, **ENV})
    if check and r.returncode:
        raise SystemExit(f"{cmd}\n{r.stdout}{r.stderr}")
    return r


def rec(scene, cmd, cwd, tty=False, inputs=()):
    """Runs cmd as the student would type it and stores the lines the terminal shows."""
    if tty:
        lines = ptyrun.run(cmd, cwd, inputs=inputs, env=ENV)
    else:
        r = sh(cmd, cwd)
        lines = (r.stdout + r.stderr).rstrip("\n").split("\n") if (r.stdout + r.stderr).strip() else []
    OUT.setdefault(scene, []).append({"cmd": cmd, "cwd": cwd.replace(HOME, "~").replace(LEE, "~"), "out": lines})
    print(f"== {scene}: {cmd}")
    print("\n".join(lines))
    return lines


def page():
    """What the browser shows at localhost:8080, as text (the deck draws the browser)."""
    for _ in range(30):
        try:
            return urllib.request.urlopen("http://localhost:8080", timeout=2).read().decode()
        except Exception:
            time.sleep(0.3)
    return "(no page)"


def web_gone():
    sh("docker stop web; docker rm web")


def fresh():
    sh("docker rm -f $(docker ps -aq) 2>/dev/null; docker volume rm $(docker volume ls -q) 2>/dev/null")
    sh("docker rmi nginx 2>/dev/null")
    for d in (CAFE, LEE):
        shutil.rmtree(d, ignore_errors=True)
    os.makedirs(f"{CAFE}/site")
    os.makedirs(LEE)


fresh()

# ---------- 1. exec: going inside a running container ----------
rec("run-web", "docker run -d --name web -p 8080:80 nginx", CAFE, tty=True)
OUT["page-default"] = page()
rec("exec", "docker exec -it web bash", CAFE, tty=True,
    inputs=["ls", "cd /usr/share/nginx/html", "ls", 'echo "<h1>KANT Cafe</h1>" > index.html', "cat index.html", "exit"])
OUT["page-exec"] = page()
rec("gone", "docker stop web", CAFE)
rec("gone", "docker rm web", CAFE)
rec("gone", "docker run -d --name web -p 8080:80 nginx", CAFE)
OUT["page-gone"] = page()
rec("exec-stopped", "docker stop web", CAFE)
rec("exec-stopped", "docker exec -it web bash", CAFE, tty=True)
sh("docker rm web")

# ---------- 2. volumes ----------
V = "docker run -d --name web -p 8080:80 -v cafe-html:/usr/share/nginx/html nginx"
rec("vol", V, CAFE)
rec("vol", "docker exec -it web bash", CAFE, tty=True,
    inputs=["cd /usr/share/nginx/html", 'echo "<h1>KANT Cafe</h1>" > index.html', "exit"])
rec("vol", "docker stop web", CAFE)
rec("vol", "docker rm web", CAFE)
rec("vol", V, CAFE)
OUT["page-vol"] = page()
rec("vol-ls", "docker volume ls", CAFE)
web_gone()

open(f"{CAFE}/site/index.html", "w").write(SITE1)
rec("bind", "ls site", CAFE)
rec("bind", "docker run -d --name web -p 8080:80 -v ./site:/usr/share/nginx/html nginx", CAFE)
OUT["page-bind1"] = page()
open(f"{CAFE}/site/index.html", "w").write(SITE2)
OUT["page-bind2"] = page()
web_gone()

rec("bind-typo", "docker run -d --name web -p 8080:80 -v site:/usr/share/nginx/html nginx", CAFE)
OUT["page-typo"] = page()
rec("bind-typo", "docker volume ls", CAFE)
web_gone()

# ---------- 3. compose ----------
open(f"{CAFE}/site/index.html", "w").write(SITE1)
open(f"{CAFE}/compose.yaml", "w").write(COMPOSE)
rec("cafe-ls", "ls", CAFE)
rec("compose-up", "docker compose up -d", CAFE, tty=True)
rec("compose-ps", "docker compose ps", CAFE)
OUT["page-compose"] = page()
rec("port-busy", "docker run -d --name web -p 8080:80 nginx", CAFE)
sh("docker rm web")
rec("compose-down", "docker compose down", CAFE, tty=True)
rec("compose-none", "docker compose up -d", HOME, tty=True)

# ---------- 5. example 2: the friend gets the folder with git and runs one line ----------
sh("git init -q -b main && git add compose.yaml site && git -c user.name=kim -c user.email=kim@example.com commit -qm 'feat: 카페 메뉴판'", CAFE, check=True)
sh(f"git clone -q {CAFE} cafe", LEE, check=True)
sh("docker rmi nginx")  # the friend's computer has no nginx image yet
rec("friend", "ls", f"{LEE}/cafe")
rec("friend", "docker compose up -d", f"{LEE}/cafe", tty=True)
rec("friend", "docker compose ps", f"{LEE}/cafe")
OUT["page-friend"] = page()
rec("friend", "docker compose down", f"{LEE}/cafe", tty=True)

# ---------- 5. example 3: clean up ----------
rec("clean", "docker ps -a", CAFE)
rec("clean", "docker volume ls", CAFE)
rec("clean", "docker volume rm cafe-html site", CAFE)
rec("clean", "docker volume ls", CAFE)
rec("clean", "docker images", CAFE)

json.dump(OUT, open(os.path.join(HERE, "out.json"), "w"), ensure_ascii=False, indent=1)
print("wrote tools/out.json")
