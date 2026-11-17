"""Runs every SQL of the SQL 1 deck (36) for real and saves what the student would see in tools/out.json.
    sudo -n dockerd &        (once, in the cloud container)
    uv run --with pyte python tools/demo.py
Real Docker and the official postgres:18 image, with the class names of 35 (IndieGameMaker/kant_docker): container
my-pg, password admin1234, volume pgdata, database kant_shop. psql runs in a pseudo-terminal of 160 columns and every
SQL line is typed after the prompt shows, so the screen is what a student sees."""
import json, os, shutil, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ptyrun  # noqa: E402
from files import TABLE, ROWS, MEMBER, MEMBER_ROWS  # noqa: E402

HOME = "/home/kim"
ENV = {"HOME": HOME, "NO_COLOR": "1"}
OUT = {}
PROMPT = rb"(=# |-# |'# |\(# |=> |: |\$ |# )$"
RUN = "docker run -d --name my-pg -e POSTGRES_PASSWORD=admin1234 -p 5432:5432 -v pgdata:/var/lib/postgresql postgres:18"
PSQL = "docker exec -it my-pg psql -U postgres"
KS = PSQL + " -d kant_shop"


def sh(cmd, cwd=HOME):
    return subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, env={**os.environ, **ENV})


def rec(scene, cmd, inputs=(), tty=False):
    if tty or inputs:
        lines = ptyrun.run(cmd, HOME, inputs=list(inputs) + ["\\q"] if inputs else (), env=ENV, prompt=PROMPT, cols=160)
    else:
        r = sh(cmd)
        lines = (r.stdout + r.stderr).rstrip("\n").split("\n") if (r.stdout + r.stderr).strip() else []
    OUT.setdefault(scene, []).append({"cmd": cmd, "cwd": "~", "out": lines})
    print(f"== {scene}: {cmd}")
    print("\n".join(lines))
    return lines


def ready():
    for _ in range(240):
        log = sh("docker logs my-pg 2>&1").stdout
        if "init process complete" in log and "ready to accept connections" in log.split("PostgreSQL init process complete")[-1]:
            time.sleep(1)
            return
        time.sleep(0.5)
    raise SystemExit("my-pg never got ready")


sh("docker rm -f $(docker ps -aq) 2>/dev/null")
sh("docker volume rm $(docker volume ls -q) 2>/dev/null")
os.makedirs(HOME, exist_ok=True)

# ---------- part 1: enter ----------
rec("run", RUN)
ready()
rec("enter", PSQL, ["DROP DATABASE IF EXISTS kant_shop;", "CREATE DATABASE kant_shop;", "\\c kant_shop"])
rec("enter2", KS, ["\\conninfo", "\\dt"])

# ---------- part 2: data types ----------
rec("t-text", KS, ["CREATE TABLE type_text (code CHAR(5), name VARCHAR(5), memo TEXT);",
                   "INSERT INTO type_text VALUES ('A1', 'mouse', 'wireless mouse, 2 colors');",
                   "SELECT * FROM type_text;",
                   "INSERT INTO type_text VALUES ('A2', 'keyboard', 'mechanical');",
                   "INSERT INTO type_text VALUES ('A123456', 'mouse', 'too long code');"])
rec("t-int", KS, ["CREATE TABLE type_int (s SMALLINT, i INTEGER, b BIGINT);",
                  "INSERT INTO type_int VALUES (32767, 2147483647, 9223372036854775807);",
                  "INSERT INTO type_int VALUES (32768, 1, 1);",
                  "INSERT INTO type_int VALUES (1, 2147483648, 1);",
                  "SELECT * FROM type_int;"])
rec("t-float", KS, ["CREATE TABLE type_num (fa DOUBLE PRECISION, fb DOUBLE PRECISION, na NUMERIC(10, 2), nb NUMERIC(10, 2));",
                    "INSERT INTO type_num VALUES (0.1, 0.2, 0.1, 0.2);",
                    "SELECT fa + fb, na + nb FROM type_num;"])
rec("t-real", KS, ["CREATE TABLE type_real (r REAL, d DOUBLE PRECISION);",
                   "INSERT INTO type_real VALUES (3.14159265358979, 3.14159265358979);",
                   "SELECT * FROM type_real;"])
rec("t-numps", KS, ["CREATE TABLE type_rate (rate NUMERIC(5, 2));",
                    "INSERT INTO type_rate VALUES (3.14159);",
                    "INSERT INTO type_rate VALUES (999.99);",
                    "INSERT INTO type_rate VALUES (1234.5);",
                    "SELECT * FROM type_rate;"])
rec("t-bool", KS, ["CREATE TABLE type_bool (name VARCHAR(20), on_sale BOOLEAN);",
                   "INSERT INTO type_bool VALUES ('mouse', true), ('keyboard', false);",
                   "SELECT * FROM type_bool;",
                   "SELECT * FROM type_bool WHERE on_sale = true;"])
rec("t-time", KS, ["SHOW TIME ZONE;",
                   "CREATE TABLE type_time (d DATE, t TIME, ts TIMESTAMP, tz TIMESTAMPTZ);",
                   "SET TIME ZONE 'Asia/Seoul';",
                   "INSERT INTO type_time VALUES ('2026-11-17', '09:30', '2026-11-17 09:30', '2026-11-17 09:30');",
                   "SELECT * FROM type_time;",
                   "SET TIME ZONE 'UTC';",
                   "SELECT * FROM type_time;"])
rec("t-date-bad", KS, ["INSERT INTO type_time (d) VALUES ('2026-02-30');"])
rec("t-now", KS, ["SELECT now();", "SET TIME ZONE 'Asia/Seoul';", "SELECT now();"])
rec("t-dt", KS, ["\\dt"])

# ---------- part 3: product table, INSERT, SELECT, WHERE ----------
rec("p-create", KS, TABLE + ["\\d product"])
rec("p-insert", KS, ROWS + ["INSERT INTO product (id, name, category, stock) VALUES (9, '무선 충전기', 'acc', 40);",
                            "SELECT * FROM product;"])
rec("a-alias", KS, ["SELECT name AS 상품명, price AS 가격 FROM product WHERE id <= 3;",
                    "SELECT name, price, price * 3 FROM product WHERE id <= 3;",
                    "SELECT name AS 상품명, price * 3 AS 3개가격 FROM product WHERE id <= 3;",
                    "SELECT name AS 상품명, price * 3 AS \"3개 가격\" FROM product WHERE id <= 3;"])
rec("w-cmp", KS, ["SELECT name, price FROM product WHERE price >= 50000;",
                  "SELECT name, category FROM product WHERE category <> 'acc';"])
rec("w-andor", KS, ["SELECT name, price, stock FROM product WHERE category = 'audio' AND stock > 0;",
                    "SELECT name, price FROM product WHERE price < 25000 OR price > 100000;"])
rec("w-in", KS, ["SELECT name, category FROM product WHERE category = 'audio' OR category = 'input';",
                 "SELECT name, category FROM product WHERE category IN ('audio', 'input');",
                 "SELECT name, price FROM product WHERE price >= 20000 AND price <= 40000;",
                 "SELECT name, price FROM product WHERE price BETWEEN 20000 AND 40000;"])
rec("w-like", KS, ["SELECT name FROM product WHERE name LIKE '%마우스%';",
                   "SELECT name FROM product WHERE name LIKE '무선';",
                   "SELECT name FROM product WHERE name LIKE '무선%';",
                   "SELECT name FROM product WHERE name LIKE 'usb%';",
                   "SELECT name FROM product WHERE name ILIKE 'usb%';"])
rec("w-null", KS, ["SELECT name, price FROM product WHERE price = NULL;",
                   "SELECT name, price FROM product WHERE price IS NULL;",
                   "SELECT COUNT(*) AS \"가격 미정\" FROM product WHERE price IS NULL;"])
rec("o-order", KS, ["SELECT name, price FROM product ORDER BY price;",
                    "SELECT name, price FROM product ORDER BY price DESC;"])
rec("o-two", KS, ["SELECT category, name, price FROM product ORDER BY category, price DESC;"])
rec("o-limit", KS, ["SELECT name, price FROM product WHERE price IS NOT NULL ORDER BY price DESC LIMIT 3;",
                    "SELECT id, name FROM product ORDER BY id LIMIT 3;",
                    "SELECT id, name FROM product ORDER BY id LIMIT 3 OFFSET 3;"])

# ---------- part 4: UPDATE, DELETE, RETURNING, DROP ----------
rec("u-one", KS, ["SELECT id, name, price FROM product WHERE id = 9;",
                  "UPDATE product SET price = 32000 WHERE id = 9;",
                  "SELECT id, name, price FROM product WHERE id = 9;"])
rec("u-calc", KS, ["UPDATE product SET price = price - 5000, stock = stock + 10 WHERE category = 'audio';",
                   "SELECT name, price, stock FROM product WHERE category = 'audio';"])
rec("d-one", KS, ["DELETE FROM product WHERE id = 8;", "SELECT id, name FROM product;"])
rec("r-ret", KS, ["UPDATE product SET stock = 0 WHERE id = 5 RETURNING *;",
                  "DELETE FROM product WHERE stock = 0 RETURNING id, name;",
                  "INSERT INTO product VALUES (10, '노트북 파우치', 'acc', 15000, 50) RETURNING *;"])
rec("u-oops", KS, ["SELECT id, name, price FROM product WHERE id = 3;",
                   "UPDATE product SET price = 0;",
                   "SELECT id, name, price FROM product;"])
rec("d-oops", KS, ["DELETE FROM product;", "SELECT * FROM product;"])
rec("d-drop", KS, ["\\dt", "DROP TABLE type_text;", "DROP TABLE type_text;", "DROP TABLE IF EXISTS type_text;",
                   "DROP TABLE type_int, type_num, type_real, type_rate, type_bool, type_time;", "\\dt"])
rec("d-dropdb", PSQL, ["DROP DATABASE IF EXISTS test;", "DROP DATABASE test;"])

# ---------- part 5: errors ----------
rec("p-reload", KS, ROWS)
rec("x-quote", KS, ["SELECT * FROM product WHERE name = \"웹캠\";",
                    "SELECT * FROM product WHERE name = '웹캠';"])
rec("x-open", KS, ["SELECT * FROM product WHERE name = '웹캠;", ";", "';"])
rec("x-ctrlc", KS, ["SELECT * FROM product WHERE name = '웹캠;", "\x03", "SELECT * FROM product WHERE name = '웹캠';"])
rec("x-typo", KS, ["SELECT nmae, price FROM product;",
                   "SELECT name price FROM product WHERE id < 4;"])
rec("x-type", KS, ["UPDATE product SET price = '24,000' WHERE id = 5;",
                   "SELECT name FROM product WHERE price = '비쌈';",
                   "UPDATE product SET price = '24000' WHERE id = 5;"])

# ---------- part 6: member list ----------
rec("m-make", KS, MEMBER + MEMBER_ROWS + ["SELECT * FROM member;"])
rec("m-region", KS, ["SELECT region FROM member;",
                     "SELECT DISTINCT region FROM member;",
                     "SELECT DISTINCT region, grade FROM member;"])
rec("m-find", KS, ["SELECT name, joined, phone FROM member WHERE joined BETWEEN '2026-10-01' AND '2026-10-31' AND phone IS NULL;",
                   "SELECT name, email FROM member WHERE email ILIKE '%@gmail.com' ORDER BY name;"])
rec("m-grade", KS, ["SELECT name, grade, points FROM member WHERE points >= 30000 AND grade <> 'gold';",
                    "UPDATE member SET grade = 'gold' WHERE points >= 30000 AND grade <> 'gold' RETURNING name, grade, points;"])
rec("m-leave", KS, ["SELECT id, name, email FROM member WHERE email = 'choi@naver.com';",
                    "DELETE FROM member WHERE id = 4 RETURNING *;",
                    "SELECT name, joined FROM member ORDER BY joined DESC LIMIT 3;"])

json.dump(OUT, open(os.path.join(HERE, "out.json"), "w"), ensure_ascii=False, indent=1)
print("wrote tools/out.json")
