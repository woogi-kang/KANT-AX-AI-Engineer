"""Runs every command of the PostgreSQL deck (34) for real and saves what the student would see in tools/out.json.
    sudo -n dockerd &        (once, in the cloud container)
    uv run --with pyte python tools/demo.py
Real Docker and the official postgres:18 image. The student's folder is /home/kim. psql runs in a pseudo-terminal
of 160 columns (a maximized window): \\l is about 140 columns wide and a narrower window opens it in the pager
(q closes it). Commands typed inside psql or bash are sent one by one after the prompt shows."""
import json, os, shutil, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ptyrun  # noqa: E402
from files import COMPOSE, COMPOSE_INIT, MENU_SQL  # noqa: E402

HOME = "/home/kim"
PGD = f"{HOME}/cafe-pg"
ENV = {"HOME": HOME, "NO_COLOR": "1"}
OUT = {}
PROMPT = rb"(=# |-# |=> |: |\$ |# )$"
RUN = "docker run -d --name pg -e POSTGRES_PASSWORD=cafe1234 -p 5432:5432 postgres:18"
RUNV = "docker run -d --name pg -e POSTGRES_PASSWORD=cafe1234 -p 5432:5432 -v pg-data:/var/lib/postgresql postgres:18"
TABLE = "CREATE TABLE orders (id INT PRIMARY KEY, menu VARCHAR(20), qty INT);"
INS1 = "INSERT INTO orders VALUES (1, 'latte', 2);"
INS2 = "INSERT INTO orders VALUES (2, 'americano', 1);"
PSQL = "docker exec -it pg psql -U postgres"
# a second, throwaway container plays "a program outside": it reaches pg through port 5432 of my computer.
# host.docker.internal is my computer; --add-host makes the name work on Linux too (Docker Desktop knows it already)
OUTSIDE = "docker run --rm -it --add-host host.docker.internal:host-gateway postgres:18 psql -h host.docker.internal -U postgres"


def sh(cmd, cwd=HOME):
    return subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, env={**os.environ, **ENV})


def rec(scene, cmd, cwd=HOME, tty=False, inputs=(), cols=160):
    if tty or inputs:
        lines = ptyrun.run(cmd, cwd, inputs=inputs, env=ENV, prompt=PROMPT, cols=cols)
    else:
        r = sh(cmd, cwd)
        lines = (r.stdout + r.stderr).rstrip("\n").split("\n") if (r.stdout + r.stderr).strip() else []
    OUT.setdefault(scene, []).append({"cmd": cmd, "cwd": cwd.replace(HOME, "~"), "out": lines})
    print(f"== {scene}: {cmd}")
    print("\n".join(lines))
    return lines


def ready(name="pg", fresh=True):
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


clean()
sh("docker rmi postgres:18")
shutil.rmtree(PGD, ignore_errors=True)
os.makedirs(HOME, exist_ok=True)

# ---------- part 1: run ----------
rec("pull", "docker pull postgres:18", tty=True, cols=80)
rec("images", "docker images postgres")
rec("run", RUN)
rec("early", PSQL, inputs=["\\q"])               # straight after run: not ready yet
ready()
rec("logs", "docker logs pg")
rec("ps", "docker ps")
rec("env", "docker exec pg env")
rec("why", "docker exec -it pg mysql -u root -p", tty=True)

# ---------- part 2: psql ----------
rec("enter", PSQL, inputs=["\\q"])
rec("psql", PSQL, inputs=["\\conninfo", "\\q"])
rec("du", PSQL, inputs=["\\du", "\\q"])
rec("bash", "docker exec -it pg bash", inputs=["psql -U postgres", "\\q", "psql -U postgres -h localhost", "\\conninfo", "\\q", "exit"])
rec("out", OUTSIDE, inputs=["cafe1234", "\\conninfo", "\\q"])
rec("badpw", OUTSIDE, inputs=["cafe123"])
rec("oneshot", 'docker exec pg psql -U postgres -c "SELECT version();"')
rec("oneshot", 'docker exec pg psql -U postgres -c "\\l"')

# ---------- part 3: SQL ----------
rec("s-db", PSQL, inputs=["CREATE DATABASE shop;", "\\l", "\\q"])
rec("s-c", PSQL, inputs=["\\c shop", "\\q"])
rec("s-table", "docker exec -it pg psql -U postgres -d shop", inputs=[TABLE, "\\dt", "\\d orders", "\\q"])
rec("s-insert", "docker exec -it pg psql -U postgres -d shop", inputs=[INS1, INS2, "SELECT * FROM orders;", "SELECT menu, qty FROM orders;", "\\q"])
rec("s-semi", "docker exec -it pg psql -U postgres -d shop", inputs=["SELECT * FROM orders", ";", "\\q"])
rec("s-typo", PSQL, inputs=["\\c shopp", "\\q"])
rec("s-drop", "docker exec -it pg psql -U postgres -d shop", inputs=["DROP TABLE orders;", "\\dt", "DROP DATABASE shop;", "\\c postgres", "DROP DATABASE shop;", "\\l", "\\q"])

# ---------- part 4: accounts ----------
rec("u-app", PSQL, inputs=["CREATE USER app WITH PASSWORD 'app1234';", "\\du", "\\q"])
rec("u-deny", "docker exec -it pg psql -U app -d postgres", inputs=["CREATE DATABASE test;", "\\q"])
rec("u-run", "docker run -d --name pg2 -e POSTGRES_USER=cafe -e POSTGRES_PASSWORD=cafe1234 -p 5433:5432 postgres:18")
ready("pg2")
rec("u-nopg", "docker exec -it pg2 psql -U postgres", inputs=["\\q"])
rec("u-cafe", "docker exec -it pg2 psql -U cafe", inputs=["\\du", "CREATE DATABASE test;", "\\q"])
rec("u-port", "docker run -d --name pg3 -e POSTGRES_PASSWORD=cafe1234 -p 5432:5432 postgres:18")
rec("u-port", "docker ps -a")
sh("docker rm -f pg2 pg3")

# ---------- part 5: gone, volume ----------
rec("g-make", PSQL, inputs=["CREATE DATABASE shop;", "\\c shop", TABLE, INS1, INS2, "\\q"])
rec("g-rm", "docker stop pg")
rec("g-rm", "docker rm pg")
rec("g-rerun", RUN)
ready()
rec("g-gone", "docker exec -it pg psql -U postgres -d shop", inputs=["\\q"])
rec("g-gone2", PSQL, inputs=["\\l", "\\q"])
sh("docker rm -f pg")
rec("v-anon", "docker volume ls")
sh("docker volume rm $(docker volume ls -q) 2>/dev/null")

rec("v-run", RUNV)
ready()
rec("v-make", PSQL, inputs=["CREATE DATABASE shop;", "\\c shop", TABLE, INS1, INS2, "\\q"])
rec("v-rm", "docker stop pg")
rec("v-rm", "docker rm pg")
rec("v-ls", "docker volume ls")
rec("v-rerun", RUNV)
ready(fresh=False)
rec("v-logs", "docker logs pg")
rec("v-kept", "docker exec -it pg psql -U postgres -d shop", inputs=["SELECT * FROM orders;", "\\q"])
rec("v-inside", "docker exec pg ls /var/lib/postgresql /var/lib/postgresql/18/docker")

# trap: the password stays with the volume
rec("t-newpw-rm", "docker stop pg")
rec("t-newpw-rm", "docker rm pg")
rec("t-newpw", "docker run -d --name pg -e POSTGRES_PASSWORD=new5678 -p 5432:5432 -v pg-data:/var/lib/postgresql postgres:18")
ready(fresh=False)
rec("t-newpw-logs", "docker logs pg")
rec("t-newpw-in", OUTSIDE, inputs=["new5678"])
rec("t-newpw-old", OUTSIDE + " -d shop", inputs=["cafe1234", "SELECT * FROM orders;", "\\q"])
sh("docker rm -f pg")

# trap: the 17-and-older data path
rec("t-old", "docker run -d --name pg -e POSTGRES_PASSWORD=cafe1234 -p 5432:5432 -v old-data:/var/lib/postgresql/data postgres:18")
time.sleep(4)
rec("t-old-ps", "docker ps -a")
rec("t-old-logs", "docker logs pg")
sh("docker rm -f pg")
sh("docker volume rm $(docker volume ls -q) 2>/dev/null")

# trap: no password
rec("t-nopw", "docker run -d --name pg postgres:18")
time.sleep(3)
rec("t-nopw-ps", "docker ps -a")
rec("t-nopw-logs", "docker logs pg")
rec("t-nopw-rm", "docker rm pg")
sh("docker volume rm $(docker volume ls -q) 2>/dev/null")

# ---------- part 6: compose ----------
os.makedirs(PGD)
open(f"{PGD}/compose.yaml", "w").write(COMPOSE)
rec("c-up", "docker compose up -d", PGD, tty=True, cols=80)
ready("cafe-pg-pg-1")
rec("c-ps", "docker compose ps", PGD)
rec("c-sql", "docker compose exec pg psql -U postgres -d cafe", PGD, inputs=[TABLE, INS1, INS2, "SELECT * FROM orders;", "\\q"])
rec("c-down", "docker compose down", PGD, tty=True, cols=80)
rec("c-vol", "docker volume ls")
rec("e-up", "docker compose up -d", PGD, tty=True, cols=80)
ready("cafe-pg-pg-1", fresh=False)
rec("e-sql", "docker compose exec pg psql -U postgres -d cafe", PGD, inputs=["INSERT INTO orders VALUES (3, 'cake', 1);", "SELECT * FROM orders;", "\\q"])
rec("e-down", "docker compose down -v", PGD, tty=True, cols=80)

os.makedirs(f"{PGD}/init")
open(f"{PGD}/init/menu.sql", "w").write(MENU_SQL)
open(f"{PGD}/compose.yaml", "w").write(COMPOSE_INIT)
rec("i-up", "docker compose up -d", PGD, tty=True, cols=80)
ready("cafe-pg-pg-1")
rec("i-logs", "docker compose logs pg", PGD)
rec("i-sql", "docker compose exec pg psql -U postgres -d cafe", PGD, inputs=["\\dt", "SELECT * FROM menu;", "\\q"])
rec("i-down", "docker compose down -v", PGD, tty=True, cols=80)

json.dump(OUT, open(os.path.join(HERE, "out.json"), "w"), ensure_ascii=False, indent=1)
print("wrote tools/out.json")
