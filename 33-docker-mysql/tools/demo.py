"""Runs every command the deck shows, for real, and saves what the terminal printed in tools/out.json.

Needs a running Docker daemon (in the cloud container: sudo -n dockerd &) and pyte. Run from 32-docker-mysql:
    uv run --with pyte python tools/demo.py
The student's folder is /home/kim/cafe-db, so prompts read ~/cafe-db. The compose project is named after the folder.
"""
import json, os, shutil, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ptyrun  # noqa: E402
from files import COMPOSE, COMPOSE_INIT, MENU_SQL  # noqa: E402

HOME = "/home/kim"
DB = f"{HOME}/cafe-db"
ENV = {"HOME": HOME, "NO_COLOR": "1"}
OUT = {}
PW = "cafe1234"
PROMPT = rb"(# |password: |mysql> |-> )$"
RUN = f"docker run -d --name db -e MYSQL_ROOT_PASSWORD={PW} -e MYSQL_DATABASE=cafe -p 3306:3306 mysql:8.4"
RUNV = f"docker run -d --name db -e MYSQL_ROOT_PASSWORD={PW} -e MYSQL_DATABASE=cafe -p 3306:3306 -v cafe-data:/var/lib/mysql mysql:8.4"


def sh(cmd, cwd=HOME):
    return subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, env={**os.environ, **ENV})


def rec(scene, cmd, cwd=HOME, tty=False, inputs=()):
    if tty or inputs:
        lines = ptyrun.run(cmd, cwd, inputs=inputs, env=ENV, prompt=PROMPT)
    else:
        r = sh(cmd, cwd)
        lines = (r.stdout + r.stderr).rstrip("\n").split("\n") if (r.stdout + r.stderr).strip() else []
    OUT.setdefault(scene, []).append({"cmd": cmd, "cwd": cwd.replace(HOME, "~"), "out": lines})
    print(f"== {scene}: {cmd}")
    print("\n".join(lines))
    return lines


def write(path, text):
    os.makedirs(os.path.dirname(f"{DB}/{path}"), exist_ok=True)
    open(f"{DB}/{path}", "w").write(text)


def ready(name="db"):
    """MySQL first starts a setup server (port: 0), then the real one; wait for the real one (port: 3306)"""
    for _ in range(240):
        if sh(f"docker logs {name} 2>&1 | grep 'ready for connections' | grep -c 'port: 3306'").stdout.strip() not in ("", "0"):
            time.sleep(1)
            return
        time.sleep(0.5)
    raise SystemExit("mysql never got ready")


def fresh():
    sh("docker rm -f $(docker ps -aq) 2>/dev/null")
    sh("docker volume rm $(docker volume ls -q) 2>/dev/null")
    sh("docker network prune -f")
    shutil.rmtree(DB, ignore_errors=True)
    os.makedirs(DB)


def mysql(scene, sql, cmd="docker exec -it db mysql -u root -p cafe", cwd=HOME, pw=PW):
    return rec(scene, cmd, cwd, inputs=[pw] + sql + ["exit"])


fresh()
rec("pull", "docker pull mysql:8.4")
rec("images", "docker images mysql")

# ---------- part 1: run, logs, exec ----------
rec("run", RUN)
time.sleep(2)
rec("early", "docker exec -it db mysql -u root -p", inputs=[PW])     # too early: still setting up
rec("ps", "docker ps")
ready()
rec("logs", "docker logs db")
rec("enter", "docker exec -it db mysql -u root -p", inputs=[PW, "exit"])
rec("env", "docker exec db env")

# ---------- part 2: four SQL statements ----------
mysql("show", ["SHOW DATABASES;"], cmd="docker exec -it db mysql -u root -p")
mysql("sql", ["CREATE TABLE orders (id INT PRIMARY KEY, menu VARCHAR(20), qty INT);",
              "INSERT INTO orders VALUES (1, 'latte', 2);",
              "INSERT INTO orders VALUES (2, 'americano', 1);",
              "SELECT * FROM orders;"])
mysql("semi", ["SELECT * FROM orders", ";"])                          # missing ; then the -> prompt
mysql("typo", ["SELECT * FROM order;"])
mysql("dup", ["INSERT INTO orders VALUES (2, 'cake', 1);"])
mysql("type", ["INSERT INTO orders VALUES (3, 'cake', 'many');"])

# ---------- part 3: gone without a volume, kept with one ----------
rec("rm", "docker stop db")
rec("rm", "docker rm db")
rec("rerun", RUN)
ready()
mysql("gone", ["SELECT * FROM orders;"])
sh("docker rm -f db")

rec("vrun", RUNV)
ready()
mysql("vsql", ["CREATE TABLE orders (id INT PRIMARY KEY, menu VARCHAR(20), qty INT);", "INSERT INTO orders VALUES (1, 'latte', 2);"])
rec("vrm", "docker stop db")
rec("vrm", "docker rm db")
rec("vls", "docker volume ls")
rec("vrun2", RUNV)
ready()
rec("vlogs", "docker logs db")
mysql("kept", ["SELECT * FROM orders;"])
sh("docker rm -f db")

# ---------- part 4: errors ----------
rec("nopw", "docker run -d --name db mysql:8.4")
time.sleep(4)
rec("nopw-ps", "docker ps -a")
rec("nopw-logs", "docker logs db")
rec("nopw-fix", "docker rm db")

rec("vrun3", RUNV)
ready()
rec("wrongpw", "docker exec -it db mysql -u root -p", inputs=["cafe123"])
rec("port", "docker run -d --name db2 -e MYSQL_ROOT_PASSWORD=x -p 3306:3306 mysql:8.4")
sh("docker rm -f db2")
sh("docker rm -f db")
newpw = RUNV.replace(PW, "new5678")
rec("trap-run", newpw)
ready()
rec("trap", "docker exec -it db mysql -u root -p", inputs=["new5678"])
rec("trap-logs", "docker logs db")
sh("docker rm -f db")
rec("trap-fix", "docker volume rm cafe-data")

# ---------- part 5: compose ----------
write("compose.yaml", COMPOSE)
rec("c-ls", "ls", DB)
rec("c-up", "docker compose up -d", DB, tty=True)
ready("cafe-db-db-1")
rec("c-ps", "docker compose ps", DB)
rec("c-vls", "docker volume ls", DB)
mysql("c-sql", ["CREATE TABLE orders (id INT PRIMARY KEY, menu VARCHAR(20), qty INT);",
                "INSERT INTO orders VALUES (1, 'latte', 2);",
                "INSERT INTO orders VALUES (2, 'cake', 1);",
                "SELECT * FROM orders;"], cmd="docker compose exec db mysql -u root -p cafe", cwd=DB)
rec("c-down", "docker compose down", DB, tty=True)
rec("c-vls2", "docker volume ls", DB)
rec("c-up2", "docker compose up -d", DB, tty=True)
ready("cafe-db-db-1")
mysql("c-kept", ["INSERT INTO orders VALUES (3, 'americano', 3);", "SELECT * FROM orders;"], cmd="docker compose exec db mysql -u root -p cafe", cwd=DB)
rec("c-down2", "docker compose down", DB, tty=True)

# ---------- part 5: init folder ----------
write("init/menu.sql", MENU_SQL)
write("compose.yaml", COMPOSE_INIT)
rec("i-skip", "docker compose up -d", DB, tty=True)
ready("cafe-db-db-1")
mysql("i-skip-sql", ["SHOW TABLES;"], cmd="docker compose exec db mysql -u root -p cafe", cwd=DB)
rec("i-down", "docker compose down -v", DB, tty=True)
rec("i-up", "docker compose up -d", DB, tty=True)
ready("cafe-db-db-1")
rec("i-logs", "docker compose logs db", DB)
mysql("i-sql", ["SELECT * FROM menu;"], cmd="docker compose exec db mysql -u root -p cafe", cwd=DB)
rec("i-down2", "docker compose down", DB, tty=True)

json.dump(OUT, open(os.path.join(HERE, "out.json"), "w"), ensure_ascii=False, indent=1)
print("wrote tools/out.json")
