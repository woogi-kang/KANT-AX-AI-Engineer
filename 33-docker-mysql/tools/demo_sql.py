"""Part 2's extra SQL (databases and tables: CREATE DATABASE, USE, SHOW TABLES, DESCRIBE, a column SELECT,
DROP TABLE, DROP DATABASE). Runs after demo.py and adds its scenes (q-*) to tools/out.json.
    uv run --with pyte python tools/demo_sql.py"""
import json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ptyrun  # noqa: E402

HOME = "/home/kim"
ENV = {"HOME": HOME, "NO_COLOR": "1"}
OUTF = os.path.join(HERE, "out.json")
OUT = json.load(open(OUTF))
for k in [k for k in OUT if k.startswith("q-")]:
    del OUT[k]
PROMPT = rb"(# |password: |mysql> |-> )$"
RUN = "docker run -d --name db -e MYSQL_ROOT_PASSWORD=cafe1234 -e MYSQL_DATABASE=cafe -p 3306:3306 mysql:8.4"


def sh(cmd):
    return subprocess.run(cmd, shell=True, cwd=HOME, capture_output=True, text=True, env={**os.environ, **ENV})


def rec(scene, cmd, inputs=()):
    lines = ptyrun.run(cmd, HOME, inputs=inputs, env=ENV, prompt=PROMPT)
    OUT.setdefault(scene, []).append({"cmd": cmd, "cwd": "~", "out": lines})
    print(f"== {scene}: {cmd}")
    print("\n".join(lines))


sh("docker rm -f $(docker ps -aq) 2>/dev/null")
sh(RUN)
for _ in range(240):
    if "port: 3306" in sh("docker logs db 2>&1 | grep 'ready for connections'").stdout:
        break
    time.sleep(0.5)
time.sleep(1)
M = "docker exec -it db mysql -u root -p"
rec("q-db", M, ["cafe1234", "CREATE DATABASE shop;", "SHOW DATABASES;", "USE shop;", "SHOW TABLES;", "exit"])
rec("q-tables", M + " cafe", ["cafe1234", "SHOW TABLES;",
                              "CREATE TABLE orders (id INT PRIMARY KEY, menu VARCHAR(20), qty INT);",
                              "SHOW TABLES;", "DESCRIBE orders;",
                              "INSERT INTO orders VALUES (1, 'latte', 2);", "INSERT INTO orders VALUES (2, 'americano', 1);",
                              "SELECT menu, qty FROM orders;", "exit"])
rec("q-drop", M + " shop", ["cafe1234", "CREATE TABLE test (id INT);", "SHOW TABLES;", "DROP TABLE test;", "SHOW TABLES;", "DROP DATABASE shop;", "SHOW DATABASES;", "exit"])
sh("docker rm -f db")
json.dump(OUT, open(OUTF, "w"), ensure_ascii=False, indent=1)
print("wrote tools/out.json")
