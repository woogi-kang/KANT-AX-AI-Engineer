"""Runs every command of the Docker CLI deck (35) for real and saves what the student would see in tools/out.json.
    sudo -n dockerd &        (once, in the cloud container)
    uv run --with pyte python tools/demo.py
Real Docker and the official postgres:18 image. The example names are the class ones (IndieGameMaker/kant_docker):
container my-pg, password admin1234, database kant_shop, table product, volume pgdata. The student works in
~/kant-shop, where kant_shop.sql (the class file) and compose.yaml sit."""
import json, os, pty, select, shutil, signal, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ptyrun  # noqa: E402
import pyte  # noqa: E402
from files import SQL, COMPOSE, COMPOSE_NONAME, COMPOSE_FOUR, COMPOSE_TAB, COMPOSE_MIX, COMPOSE_COLON  # noqa: E402

HOME = "/home/kim"
KS = f"{HOME}/kant-shop"
ENV = {"HOME": HOME, "NO_COLOR": "1"}
OUT = {}
PROMPT = rb"(=# |-# |=> |: |\$ |# )$"
RUN = "docker run -d --name my-pg -e POSTGRES_PASSWORD=admin1234 -p 5432:5432 postgres:18"
RUN3 = "docker run -d --name my-pg \\\n-e POSTGRES_PASSWORD=admin1234 \\\n-p 5432:5432 postgres:18"
RUNSP = "docker run -d --name my-pg \\ \n-e POSTGRES_PASSWORD=admin1234 \\\n-p 5432:5432 postgres:18"
RUNV = "docker run -d --name my-pg -e POSTGRES_PASSWORD=admin1234 -p 5432:5432 -v pgdata:/var/lib/postgresql postgres:18"
SEL = 'docker exec -it my-pg psql -U postgres -d kant_shop -c "SELECT * FROM product"'


def sh(cmd, cwd=KS):
    return subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, env={**os.environ, **ENV})


def rec(scene, cmd, cwd=KS, tty=False, inputs=(), cols=160):
    if tty or inputs:
        lines = ptyrun.run(cmd, cwd, inputs=inputs, env=ENV, prompt=PROMPT, cols=cols)
    else:
        r = sh(cmd, cwd)
        lines = (r.stdout + r.stderr).rstrip("\n").split("\n") if (r.stdout + r.stderr).strip() else []
    OUT.setdefault(scene, []).append({"cmd": cmd, "cwd": cwd.replace(HOME, "~"), "out": lines})
    print(f"== {scene}: {cmd}")
    print("\n".join(lines))
    return lines


def rec_ctrl_c(scene, cmd, after, cwd=KS, cols=120):
    """runs cmd in a pty, waits until `after` shows up, then presses Ctrl+C like a student would"""
    pid, fd = pty.fork()
    if pid == 0:
        os.chdir(cwd)
        os.environ.update(ENV)
        os.environ["TERM"] = "xterm"
        os.execvp("bash", ["bash", "--noprofile", "--norc", "-c", f"stty cols {cols} rows 50; {cmd}"])
    raw, sent, t0 = b"", False, time.time()
    while True:
        r, _, _ = select.select([fd], [], [], 0.3)
        if r:
            try:
                chunk = os.read(fd, 65536)
            except OSError:
                break
            if not chunk:
                break
            raw += chunk
        if not sent and after.encode() in raw:
            time.sleep(1.5)
            os.write(fd, b"\x03")
            sent = True
        if time.time() - t0 > 30:
            os.kill(pid, signal.SIGKILL)
            break
    os.waitpid(pid, 0)
    screen = pyte.Screen(cols, 200)
    pyte.ByteStream(screen).feed(raw)
    lines = [l.rstrip() for l in screen.display]
    while lines and not lines[-1]:
        lines.pop()
    OUT.setdefault(scene, []).append({"cmd": cmd, "cwd": cwd.replace(HOME, "~"), "out": lines})
    print(f"== {scene}: {cmd}")
    print("\n".join(lines))


def ready(name="my-pg", fresh=True):
    """a new database first runs a setup server; the real one comes after 'init process complete'"""
    for _ in range(240):
        log = sh(f"docker logs {name} 2>&1").stdout
        tail = log.split("PostgreSQL init process complete")[-1] if fresh else log
        if (not fresh or "init process complete" in log or "Skipping initialization" in log) and "ready to accept connections" in tail:
            time.sleep(1)
            return
        time.sleep(0.5)
    raise SystemExit(f"{name} never got ready")


def clean():
    sh("docker rm -f $(docker ps -aq) 2>/dev/null")
    sh("docker volume rm $(docker volume ls -q) 2>/dev/null")
    sh("docker network prune -f")


def write(name, text):
    with open(os.path.join(KS, name), "w") as f:
        f.write(text)


shutil.rmtree(KS, ignore_errors=True)
os.makedirs(KS)
clean()
sh("docker rmi postgres:18")
write("kant_shop.sql", SQL)

# ---------- part 2: images and containers ----------
rec("pull", "docker pull postgres:18", tty=True, cols=80)
rec("images", "docker images")
rec("image-ls", "docker image ls")
rec("run", RUN)
ready()
rec("ps", "docker ps")
rec("container-ls", "docker container ls")
rec("conflict", RUN)
rec("port", "docker run -d --name my-pg2 -e POSTGRES_PASSWORD=admin1234 -p 5432:5432 postgres:18")
rec("port-ps", "docker ps -a")
sh("docker rm my-pg2")
rec("stop", "docker stop my-pg")
rec("psa-stop", "docker ps -a")
rec("start", "docker start my-pg")
rec("restart", "docker restart my-pg")
rec("psa-up", "docker ps -a")
ready(fresh=False)
time.sleep(2)
rec("logs-tail", "docker logs --tail 3 my-pg")
rec_ctrl_c("logs-f", "docker logs -f --tail 1 my-pg", "ready to accept connections\r\n", cols=160)
rec("rm-up", "docker rm my-pg")
rec("rmi-used", "docker rmi postgres:18")
rec("stop2", "docker stop my-pg")
rec("rm", "docker rm my-pg")

# ---------- part 1: reading commands (the line split) ----------
rec("run3", RUN3)
ready()
sh("docker rm -f my-pg")
rec("runsp", RUNSP, tty=True)
sh("docker rm -f my-pg")

# ---------- part 3: working inside ----------
rec("run-again", RUN)
ready()
rec("ls-before", "docker exec my-pg ls /tmp")
rec("cp", "docker cp kant_shop.sql my-pg:/tmp/kant_shop.sql", tty=True)
rec("ls-after", "docker exec my-pg ls /tmp")
rec("cp-typo", "docker cp kant_shop.sq my-pg:/tmp/kant_shop.sql")
rec("cp-out", "docker cp my-pg:/tmp/kant_shop.sql ./copy.sql", tty=True)
rec("cp-out-ls", "ls", tty=True)
os.remove(os.path.join(KS, "copy.sql"))
rec("f", "docker exec -it my-pg psql -U postgres -f /tmp/kant_shop.sql", tty=True)
rec("it-redirect", "docker exec -it my-pg psql -U postgres < kant_shop.sql", tty=True)
rec("i-redirect", "docker exec -i my-pg psql -U postgres < kant_shop.sql", tty=True)
rec("sel", SEL, tty=True)
rec("enter", "docker exec -it my-pg psql -U postgres -d kant_shop", inputs=["\\dt", "\\d product", "\\q"])
rec("bash", "docker exec -it my-pg bash", inputs=["ls /tmp", "exit"])
rec("help", "docker cp --help")
sh("docker rm -f my-pg")

# ---------- part 4: volumes ----------
# the runs above without -v left nameless volumes behind (33 and 34 showed them); clear them so the list reads
sh("docker volume rm $(docker volume ls -q) 2>/dev/null")
rec("v-create", "docker volume create pgdata")
rec("v-ls", "docker volume ls")
rec("v-inspect", "docker volume inspect pgdata")
rec("v-run", RUNV)
ready()
rec("v-load", "docker exec -i my-pg psql -U postgres < kant_shop.sql", tty=True)
rec("v-rm-used", "docker volume rm pgdata")
rec("v-gone", "docker stop my-pg")
rec("v-gone", "docker rm my-pg")
rec("v-rerun", RUNV)
ready(fresh=False)
rec("v-kept", SEL, tty=True)
sh("docker rm -f my-pg")
rec("v-rm", "docker volume rm pgdata")
rec("v-ls2", "docker volume ls")

# ---------- part 5: YAML and compose ----------
write("compose.yaml", COMPOSE)
rec("c-config", "docker compose config")
rec("c-up", "docker compose up -d", tty=True, cols=80)
ready()
rec("c-ps", "docker compose ps")
rec("c-dps", "docker ps")
rec("c-load", "docker exec -i my-pg psql -U postgres < kant_shop.sql", tty=True)
rec("c-exec", 'docker compose exec db psql -U postgres -d kant_shop -c "SELECT * FROM product"')
rec("c-logs", "docker compose logs --tail 3")
rec_ctrl_c("c-logs-f", "docker compose logs -f --tail 2", "ready to accept connections\r\n", cols=160)
rec("c-stop", "docker compose stop", tty=True, cols=80)
rec("c-ps-stop", "docker compose ps -a")
rec("c-start", "docker compose start", tty=True, cols=80)
rec("c-restart", "docker compose restart")
ready(fresh=False)
rec("c-ls", "docker compose ls")
rec("c-pull", "docker compose pull", tty=True, cols=80)
rec("c-down", "docker compose down", tty=True, cols=80)
rec("c-vol", "docker volume ls")
rec("c-up2", "docker compose up -d", tty=True, cols=80)
ready(fresh=False)
rec("c-kept", 'docker compose exec db psql -U postgres -d kant_shop -c "SELECT * FROM product"')
rec("c-downv", "docker compose down -v", tty=True, cols=80)
rec("c-vol2", "docker volume ls")

# container_name left out
write("compose.yaml", COMPOSE_NONAME)
rec("n-up", "docker compose up -d", tty=True, cols=80)
rec("n-ps", "docker compose ps")
rec("n-exec", "docker exec my-pg ls /tmp")
sh("docker compose down -v", KS)

# four spaces work the same
write("compose.yaml", COMPOSE_FOUR)
rec("four-config", "docker compose config")
rec("four-up", "docker compose up -d", tty=True, cols=80)
sh("docker compose down -v", KS)

# broken files
for name, text in (("tab", COMPOSE_TAB), ("mix", COMPOSE_MIX), ("colon", COMPOSE_COLON)):
    write("compose.yaml", text)
    rec(f"y-{name}", "docker compose up -d")
write("compose.yaml", COMPOSE)

# ---------- part 6: real tasks ----------
# the whole class flow with compose, then clean up
rec("e-up", "docker compose up -d", tty=True, cols=80)
ready()
rec("e-load", "docker exec -i my-pg psql -U postgres < kant_shop.sql", tty=True)
rec("e-sel", SEL, tty=True)
rec("e-down", "docker compose down -v", tty=True, cols=80)
rec("e-psa", "docker ps -a")
rec("e-vol", "docker volume ls")
rec("e-rmi", "docker rmi postgres:18")
rec("e-images", "docker images")

json.dump(OUT, open(os.path.join(HERE, "out.json"), "w"), ensure_ascii=False, indent=1)
print("wrote tools/out.json")
