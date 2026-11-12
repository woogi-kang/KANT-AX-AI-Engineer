"""MySQL accounts and the ways into the server (root vs an app user, exec variants). Runs after demo.py and adds
its scenes (u-*) to tools/out.json.
    uv run --with pyte python tools/demo_user.py"""
import json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ptyrun  # noqa: E402

HOME = "/home/kim"
ENV = {"HOME": HOME, "NO_COLOR": "1"}
OUTF = os.path.join(HERE, "out.json")
OUT = json.load(open(OUTF))
for k in [k for k in OUT if k.startswith("u-")]:
    del OUT[k]
PROMPT = rb"(# |password: |mysql> |-> )$"
RUN = "docker run -d --name db -e MYSQL_ROOT_PASSWORD=cafe1234 -e MYSQL_DATABASE=cafe -e MYSQL_USER=cafe -e MYSQL_PASSWORD=cafe5678 -p 3306:3306 mysql:8.4"


def sh(cmd):
    return subprocess.run(cmd, shell=True, cwd=HOME, capture_output=True, text=True, env={**os.environ, **ENV})


def rec(scene, cmd, inputs=(), tty=False):
    if inputs or tty:
        lines = ptyrun.run(cmd, HOME, inputs=inputs, env=ENV, prompt=PROMPT)
    else:
        r = sh(cmd)
        lines = (r.stdout + r.stderr).rstrip("\n").split("\n") if (r.stdout + r.stderr).strip() else []
    OUT.setdefault(scene, []).append({"cmd": cmd, "cwd": "~", "out": lines})
    print(f"== {scene}: {cmd}")
    print("\n".join(lines))


sh("docker rm -f $(docker ps -aq) 2>/dev/null")
rec("u-run", RUN)
for _ in range(240):
    if "port: 3306" in sh("docker logs db 2>&1 | grep 'ready for connections'").stdout:
        break
    time.sleep(0.5)
time.sleep(1)
rec("u-app", "docker exec -it db mysql -u cafe -p cafe", inputs=["cafe5678", "SHOW DATABASES;", "CREATE TABLE orders (id INT PRIMARY KEY, menu VARCHAR(20), qty INT);", "CREATE DATABASE shop;", "exit"])
rec("u-root", "docker exec -it db mysql -u root -p", inputs=["cafe1234", "CREATE DATABASE shop;", "exit"])
rec("u-bash", "docker exec -it db bash", inputs=["mysql -u root -p cafe", "cafe1234", "SHOW TABLES;", "exit", "exit"])
rec("u-one", 'docker exec db mysql -u root -pcafe1234 cafe -e "SHOW TABLES;"')
rec("u-inline", "docker exec -it db mysql -u root -pcafe1234 cafe", inputs=["exit"])
sh("docker rm -f db")
json.dump(OUT, open(OUTF, "w"), ensure_ascii=False, indent=1)
print("wrote tools/out.json")
