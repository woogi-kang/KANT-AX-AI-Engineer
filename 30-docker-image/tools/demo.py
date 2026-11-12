"""Runs every Docker command the deck shows, for real, and saves what the terminal printed in tools/out.json.

Needs a running Docker daemon (in the cloud container: sudo -n dockerd &) and uv. Run from 30-docker-image:
    uv run --with pyte python tools/demo.py
The student's folders are /home/kim/cafe (nginx page) and /home/kim/shopping-cart (the 28 project), so prompts read ~/cafe.
Commands that redraw the screen (pull, build, compose, exec -it) run in a real 80-column terminal (tools/ptyrun.py).
"""
import json, os, re, shutil, subprocess, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "28-python-modules", "tools"))
import ptyrun  # noqa: E402
import scenes as cart28  # noqa: E402  (product.py, cart.py and main.py exactly as chapter 28 shows them)

HOME = "/home/kim"
CAFE, CART = f"{HOME}/cafe", f"{HOME}/shopping-cart"
ENV = {"HOME": HOME, "NO_COLOR": "1"}
OUT = {}

from files import SITE1, SITE2, COMPOSE, DOCKERFILE, DOCKERIGNORE  # noqa: E402

UV_IMAGE = "astral/uv:python3.14-bookworm-slim"


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
    OUT.setdefault(scene, []).append({"cmd": cmd, "cwd": cwd.replace(HOME, "~"), "out": lines})
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
    sh(f"docker rmi nginx cart {UV_IMAGE} 2>/dev/null; docker builder prune -af")
    for d in (CAFE, CART):
        shutil.rmtree(d, ignore_errors=True)
    os.makedirs(f"{CAFE}/site")
    # chapter 28's shopping-cart project, made with uv init like the class
    sh(f"uv init -q --python 3.14 {CART}", check=True)
    os.remove(f"{CART}/README.md")
    for name, text in (("product.py", cart28.PRODUCT), ("cart.py", cart28.CART_GUARDED), ("main.py", cart28.MAIN_SHOP)):
        open(f"{CART}/{name}", "w").write(text)
    sh("uv sync -q && uv run main.py >/dev/null", CART, check=True)
    sh('git add . && git -c user.name=kim -c user.email=kim@example.com commit -qm "feat: 장바구니"', CART, check=True)


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

# ---------- 3. Dockerfile, build, run ----------
rec("cart-ls", "ls -a", CART)
rec("cart-ls2", "ls", CART, tty=True)
open(f"{CART}/Dockerfile", "w").write(DOCKERFILE)
rec("build", "docker build -t cart .", CART, tty=True)
rec("images", "docker images", CART)
rec("run-cart", "docker run cart", CART)

main3 = cart28.MAIN_SHOP.replace("cart.add(tumbler, 2)", "cart.add(tumbler, 3)")
assert main3 != cart28.MAIN_SHOP
open(f"{CART}/main.py", "w").write(main3)
rec("stale", "docker run cart", CART)
rec("rebuild", "docker build -t cart .", CART, tty=True)
rec("rebuild", "docker run cart", CART)
rec("psa", "docker ps -a", CART)
rec("rm-run", "docker run --rm cart", CART)
rec("rm-run", "docker ps -a", CART)

# ---------- .dockerignore: the build context before and after ----------
sh("docker builder prune -af")
rec("ctx-before", "docker build -t cart .", CART, tty=True)
open(f"{CART}/.dockerignore", "w").write(DOCKERIGNORE)
rec("ctx-after", "docker build -t cart .", CART, tty=True)

# what COPY . . put in /app, with and without .dockerignore
rec("app-ls", "docker run --rm cart ls -a", CART)
os.rename(f"{CART}/.dockerignore", f"{CART}/.dockerignore.off")
sh("docker build -q -t cart-all .", CART, check=True)
rec("app-ls-all", "docker run --rm cart-all ls -a", CART)
rv = sh("docker build --no-cache --progress=plain -t cart-all .", CART)
OUT["venv-warning"] = [l for l in (rv.stdout + rv.stderr).split("\n") if "uv sync" in l or "virtual environment" in l.lower() or "Ignoring" in l]
os.rename(f"{CART}/.dockerignore.off", f"{CART}/.dockerignore")
sh("docker rmi cart-all; docker builder prune -af")
sh("docker build -q -t cart .", CART, check=True)

# ---------- 4. compose ----------
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

# ---------- 5. errors ----------
rec("err-nodot", "docker build -t cart", CART, tty=True)
rec("err-nofile", "docker build -t cart .", HOME, tty=True)
open(f"{CART}/Dockerfile", "w").write(DOCKERFILE.replace("bookworm", "bookwrom"))
rec("err-from", "docker build -t cart .", CART, tty=True)
open(f"{CART}/Dockerfile", "w").write(DOCKERFILE.replace('"main.py"', '"mian.py"'))
sh("docker build -q -t cart-typo .", CART, check=True)
rec("err-cmd", "docker run --rm cart-typo", CART)
sh("docker rmi cart-typo")
open(f"{CART}/Dockerfile", "w").write(DOCKERFILE)

# ---------- 6. clean up ----------
rec("clean", "docker ps -a", CART)
names = sh("docker ps -a --filter status=exited --format '{{.Names}}'").stdout.split()
rec("clean", "docker rm " + " ".join(names), CART)
rec("clean", "docker rmi cart", CART)
rec("clean-vol", "docker volume ls", CART)
rec("clean-vol", "docker volume rm cafe-html site", CART)
rec("clean-img", "docker images", CART)

json.dump(OUT, open(os.path.join(HERE, "out.json"), "w"), ensure_ascii=False, indent=1)
print("wrote tools/out.json")
