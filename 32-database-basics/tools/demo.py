"""Runs every SQL line the deck shows, for real, in MySQL 8.4 and PostgreSQL 18, and saves the screens in tools/out.json.

Needs a running Docker daemon (in the cloud container: sudo -n dockerd &) and pyte. Run from 32-database-basics:
    uv run --with pyte python tools/demo.py
Each scene opens the client (mysql or psql) in a real pseudo-terminal, types the lines one by one at the prompt
and keeps the final screen. How to start the servers and open the clients is chapter 33; here only the SQL matters.
"""
import json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ptyrun  # noqa: E402

PW = "kant1234"
OUT = {}
PROMPT = rb"(mysql>|    ->|    '>|=#|-#|\(#|'#) $"


def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def client(db, database=None):
    if db == "my":
        return f"docker exec -it -e MYSQL_PWD={PW} my mysql -u root" + (f" -D {database}" if database else "")
    return "docker exec -it pg psql -U postgres -P pager=off" + (f" -d {database}" if database else "")


def clean(lines, db):
    """drop the client's welcome text (everything before the first prompt) and the exit at the end"""
    first = next(i for i, l in enumerate(lines) if l.startswith("mysql>") or "=#" in l[:20])
    lines = lines[first:]
    while lines and (lines[-1].strip() in ("Bye", "") or lines[-1].endswith(" exit") or lines[-1].endswith("\\q")):
        lines.pop()
    return lines


def rec(scene, db, inputs, database="cafe"):
    lines = ptyrun.run(client(db, database), "/", inputs=list(inputs) + (["exit"] if db == "my" else ["\\q"]),
                       cols=120, prompt=PROMPT, env={"PAGER": "cat"})
    lines = clean(lines, db)
    OUT.setdefault(scene, {})[db] = lines
    print(f"== {scene} [{db}]")
    print("\n".join(lines))


def wait(db):
    for _ in range(120):
        if db == "my":
            r = sh(f"docker exec -e MYSQL_PWD={PW} my mysql -u root -e 'SELECT 1'")
        else:
            r = sh("docker exec pg psql -U postgres -c 'SELECT 1'")
        if r.returncode == 0:
            return
        time.sleep(1)
    raise SystemExit(f"{db} did not start")


sh("docker rm -f my pg")
sh(f"docker run -d --name my -e MYSQL_ROOT_PASSWORD={PW} mysql:8.4")
sh(f"docker run -d --name pg -e POSTGRES_PASSWORD={PW} postgres:18")
wait("my"); wait("pg")
time.sleep(3)
OUT["versions"] = {"my": sh(f"docker exec -e MYSQL_PWD={PW} my mysql -u root -N -e 'SELECT VERSION()'").stdout.strip(),
                   "pg": sh("docker exec pg psql -U postgres -t -A -c 'SHOW server_version'").stdout.strip()}

for db in ("my", "pg"):
    rec("show", db, ["SHOW DATABASES;" if db == "my" else "\\l"], None)
    rec("db", db, ["CREATE DATABASE cafe;", "USE cafe;" if db == "my" else "\\c cafe"], None)
    rec("table", db, ["CREATE TABLE orders (", "  id INT PRIMARY KEY,", "  menu VARCHAR(20),", "  qty INT", ");"])
    rec("insert", db, ["INSERT INTO orders VALUES (1, 'latte', 2);"])
    rec("insert2", db, ["INSERT INTO orders (id, menu, qty) VALUES (2, 'americano', 1), (3, 'cake', 1);"])
    rec("select", db, ["SELECT * FROM orders;"])
    rec("select2", db, ["SELECT menu, qty FROM orders;", "SELECT * FROM orders WHERE id = 2;"])
    rec("x-dup", db, ["INSERT INTO orders VALUES (1, 'tea', 1);"])
    rec("x-type", db, ["INSERT INTO orders VALUES (4, 'tea', 'many');"])
    rec("x-long", db, ["INSERT INTO orders VALUES (4, 'vanilla caramel macchiato', 1);"])
    rec("x-semi", db, ["SELECT * FROM orders", ";"])
    rec("x-quote", db, ["INSERT INTO orders VALUES (4, latte, 1);"])
    rec("x-nodb", db, ["SELECT * FROM orders;"], None)
    rec("r-day", db, ["INSERT INTO orders VALUES (4, 'latte', 1), (5, 'tea', 2);", "SELECT * FROM orders WHERE menu = 'latte';"])
    rec("r-menu", db, ["CREATE TABLE menu (id INT PRIMARY KEY, name VARCHAR(20), price INT);",
                       "INSERT INTO menu VALUES (1, 'americano', 4000), (2, 'latte', 4500), (3, 'cake', 5500);",
                       "SELECT name, price FROM menu WHERE price < 5000;"])
    rec("smallest", db, ["SELECT * FROM orders;"])

json.dump(OUT, open(os.path.join(HERE, "out.json"), "w"), ensure_ascii=False, indent=1)
sh("docker rm -f my pg")
