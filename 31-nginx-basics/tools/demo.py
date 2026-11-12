"""Runs every command the deck shows, for real, and saves what the terminal printed in tools/out.json.

Needs a running Docker daemon (in the cloud container: sudo -n dockerd &) and pyte. Run from 31-nginx-basics:
    uv run --with pyte python tools/demo.py
The student's folder is /home/kim/cafe, so prompts read ~/cafe. The compose project is named after the folder (cafe).
"""
import json, os, shutil, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ptyrun  # noqa: E402
from files import SITE, EVENT_HTML, CONF_FILES, CONF_MENU, CONF_BOTH, CONF_EVENT, COMPOSE, COMPOSE_EVENT  # noqa: E402

HOME = "/home/kim"
CAFE = f"{HOME}/cafe"
ENV = {"HOME": HOME, "NO_COLOR": "1"}
OUT = {}


def sh(cmd, cwd=CAFE, check=False):
    r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, env={**os.environ, **ENV})
    if check and r.returncode:
        raise SystemExit(f"{cmd}\n{r.stdout}{r.stderr}")
    return r


def rec(scene, cmd, cwd=CAFE, tty=False):
    if tty or cmd.startswith("curl"):          # curl hides its progress meter only on a real terminal
        lines = ptyrun.run(cmd, cwd, env=ENV)
    else:
        r = sh(cmd, cwd)
        lines = (r.stdout + r.stderr).rstrip("\n").split("\n") if (r.stdout + r.stderr).strip() else []
    OUT.setdefault(scene, []).append({"cmd": cmd, "cwd": cwd.replace(HOME, "~"), "out": lines})
    print(f"== {scene}: {cmd}")
    print("\n".join(lines))
    return lines


def write(path, text):
    os.makedirs(os.path.dirname(f"{CAFE}/{path}"), exist_ok=True)
    open(f"{CAFE}/{path}", "w").write(text)


def wait_http(url):
    for _ in range(40):
        if sh(f"curl -s -o /dev/null {url}").returncode == 0:
            return
        time.sleep(0.25)


def fresh():
    sh("docker rm -f $(docker ps -aq) 2>/dev/null", HOME)
    sh("docker network prune -f", HOME)
    shutil.rmtree(CAFE, ignore_errors=True)
    os.makedirs(f"{CAFE}/site")
    write("site/index.html", SITE)


fresh()

# ---------- why: three containers, three ports ----------
rec("why", "docker run -d --name menu -p 8001:80 traefik/whoami --name menu")
rec("why", "docker run -d --name order -p 8002:80 traefik/whoami --name order")
rec("why", "docker run -d --name web -p 8080:80 -v ./site:/usr/share/nginx/html nginx")
wait_http("localhost:8001"); wait_http("localhost:8080")
rec("why-ps", "docker ps")
rec("why-curl", "curl localhost:8001")
rec("why-curl", "curl localhost:8002")
rec("why-curl", "curl localhost:8080")
sh("docker rm -f menu order web")

# ---------- part 1: nginx serves files ----------
rec("w-run", "docker run -d --name web -p 8080:80 -v ./site:/usr/share/nginx/html nginx")
wait_http("localhost:8080")
rec("w-run", "curl localhost:8080")
rec("w-path", "curl localhost:8080/index.html")
rec("w-path", "curl localhost:8080/event.html")
write("site/event.html", EVENT_HTML)
rec("w-path2", "ls site")
rec("w-path2", "curl localhost:8080/event.html")
rec("w-logs", "docker logs web")
rec("w-conf", "docker exec web cat /etc/nginx/conf.d/default.conf")
rec("w-conf-short", "docker exec web grep -v '#' /etc/nginx/conf.d/default.conf")
sh("docker rm -f web")
os.remove(f"{CAFE}/site/event.html")

write("conf/default.conf", CONF_FILES)
rec("w-mine", "ls")
rec("w-mine", "docker run -d --name web -p 8080:80 -v ./site:/usr/share/nginx/html -v ./conf:/etc/nginx/conf.d nginx")
wait_http("localhost:8080")
rec("w-mine", "curl localhost:8080")
sh("docker rm -f web")

# ---------- part 2: reverse proxy with compose ----------
write("conf/default.conf", CONF_MENU)
write("compose.yaml", COMPOSE)
rec("p-ls", "ls")
rec("p-up", "docker compose up -d", tty=True)
wait_http("localhost")
rec("p-ps", "docker compose ps")
rec("p-curl", "curl localhost")
rec("p-curl", "curl localhost/menu/")
rec("p-curl2", "curl localhost/menu/today")
rec("p-order0", "curl localhost/order/")

write("conf/default.conf", CONF_BOTH)
rec("p-reload", "curl localhost/order/")
rec("p-reload", "docker exec cafe-web-1 nginx -t")
rec("p-reload", "docker exec cafe-web-1 nginx -s reload")
time.sleep(1)
rec("p-reload", "curl localhost/order/")
rec("p-closed", "curl localhost:8001")
rec("p-logs", "docker compose logs web")

# ---------- part 3: errors ----------
rec("x-502", "docker compose stop menu", tty=True)
rec("x-502", "curl localhost/menu/")
rec("x-502-log", "docker compose logs web")
rec("x-502", "docker compose start menu", tty=True)
time.sleep(1)

write("conf/default.conf", CONF_BOTH.replace("proxy_pass http://menu/;", "proxy_pass http://menu/"))
rec("x-semi", "docker exec cafe-web-1 nginx -t")
write("conf/default.conf", CONF_BOTH.replace("http://menu/", "http://menuu/"))
rec("x-host", "docker exec cafe-web-1 nginx -t")
write("conf/default.conf", CONF_BOTH.replace("http://menu/", "http://localhost:8001/"))
sh("docker exec cafe-web-1 nginx -s reload"); time.sleep(1)
rec("x-local", "curl localhost/menu/")
rec("x-local-log", "docker compose logs web")
write("conf/default.conf", CONF_BOTH.replace("http://menu/;", "http://menu;"))
sh("docker exec cafe-web-1 nginx -s reload"); time.sleep(1)
rec("x-slash", "curl localhost/menu/today")
write("conf/default.conf", CONF_BOTH)
sh("docker exec cafe-web-1 nginx -s reload"); time.sleep(1)
rec("x-slash-ok", "curl localhost/menu/today")

rec("x-port", "docker compose down", tty=True)
rec("x-port", "docker run -d --name old -p 80:80 nginx")
rec("x-port", "docker compose up -d", tty=True)
sh("docker rm -f old")
rec("x-port2", "docker compose down", tty=True)

# ---------- part 4: real tasks ----------
rec("r-site", "docker compose up -d", tty=True)
wait_http("localhost")
time.sleep(1)
rec("r-site", "curl localhost")
rec("r-site", "curl localhost/menu/")
rec("r-site", "curl localhost/order/")

write("compose.yaml", COMPOSE_EVENT)
write("conf/default.conf", CONF_EVENT)
rec("r-add", "docker compose up -d", tty=True)
rec("r-add", "docker exec cafe-web-1 nginx -t")
rec("r-add", "docker exec cafe-web-1 nginx -s reload")
time.sleep(1)
rec("r-add", "curl localhost/event/")
rec("r-add-ps", "docker compose ps")
rec("r-down", "docker compose down", tty=True)

json.dump(OUT, open(os.path.join(HERE, "out.json"), "w"), ensure_ascii=False, indent=1)
print("wrote tools/out.json")
