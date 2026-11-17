"""Runs every psql session of the SQL 2 deck (37) for real and saves what the student would see in tools/out.json.
    sudo -n dockerd &        (once, in the cloud container)
    uv run --with pyte python tools/demo.py
Real Docker and the official postgres:18 image, with the names of 35 (the class repo): container my-pg,
password admin1234, database kant_shop. Each scene starts from an empty kant_shop. Statements a scene needs but
does not show run first without being recorded (setup). psql runs in a pseudo-terminal 160 columns wide, and the
statements are typed line by line after the prompt shows, the way a student types them."""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ptyrun  # noqa: E402

HOME = "/home/kim"
ENV = {"HOME": HOME, "NO_COLOR": "1"}
OUT = {}
PROMPT = rb"(=# |-# |\(# |=> |\$ |# )$"
RUN = "docker run -d --name my-pg -e POSTGRES_PASSWORD=admin1234 -p 5432:5432 postgres:18"
PSQL = "docker exec -it my-pg psql -U postgres -d kant_shop"


def sh(cmd, stdin=None):
    return subprocess.run(cmd, shell=True, cwd=HOME, capture_output=True, text=True, input=stdin, env={**os.environ, **ENV})


def fresh(setup=()):
    sh('docker exec my-pg psql -U postgres -c "DROP DATABASE IF EXISTS kant_shop WITH (FORCE)" -c "CREATE DATABASE kant_shop"')
    if setup:
        r = sh("docker exec -i my-pg psql -U postgres -d kant_shop -v ON_ERROR_STOP=1", "\n".join(setup) + "\n")
        if r.returncode:
            raise SystemExit(r.stderr)


def scene(name, inputs, setup=(), keep=False):
    if not keep:
        fresh(setup)
    lines = ptyrun.run(PSQL, HOME, inputs=list(inputs) + ["\\q"], env=ENV, prompt=PROMPT, cols=160)
    OUT.setdefault(name, []).append({"cmd": PSQL, "cwd": "~", "out": lines})
    print(f"== {name}")
    print("\n".join(lines))


os.makedirs(HOME, exist_ok=True)
sh("docker rm -f my-pg")
sh(RUN)
for _ in range(240):
    log = sh("docker logs my-pg 2>&1").stdout
    if "init process complete" in log and "ready to accept connections" in log.split("init process complete")[-1]:
        break
    subprocess.run("sleep 0.5", shell=True)
subprocess.run("sleep 1", shell=True)
OUT["version"] = [{"cmd": "", "cwd": "~", "out": [sh('docker exec my-pg psql -U postgres -tAc "SELECT version()"').stdout.strip()]}]

MEMBER0 = "CREATE TABLE member (id INTEGER, name VARCHAR(20), email VARCHAR(50), age INTEGER);"
# ---------- intro ----------
scene("why", [MEMBER0,
              "INSERT INTO member VALUES (1, 'kim', 'kim@mail.com', 25);",
              "INSERT INTO member VALUES (1, 'lee', 'kim@mail.com', -3);",
              "INSERT INTO member VALUES (2, NULL, NULL, 30);",
              "SELECT * FROM member;"])
scene("min", ["CREATE TABLE product (",
              "  id INTEGER,",
              "  name VARCHAR(20),",
              "  price INTEGER CHECK (price > 0)",
              ");",
              "INSERT INTO product VALUES (1, 'earphone', -89000);",
              "INSERT INTO product VALUES (1, 'earphone', 89000);"])

# ---------- part 1: NOT NULL, DEFAULT ----------
scene("nn", ["CREATE TABLE member (",
             "  id INTEGER,",
             "  name VARCHAR(20) NOT NULL,",
             "  email VARCHAR(50)",
             ");",
             "INSERT INTO member (id, email) VALUES (1, 'kim@mail.com');",
             "INSERT INTO member (id, name) VALUES (1, 'kim');",
             "SELECT * FROM member;"])
scene("df", ["CREATE TABLE member (",
             "  id INTEGER,",
             "  name VARCHAR(20) NOT NULL,",
             "  points INTEGER DEFAULT 0,",
             "  joined_at TIMESTAMPTZ DEFAULT now()",
             ");",
             "INSERT INTO member (id, name) VALUES (1, 'kim');",
             "INSERT INTO member (id, name, points) VALUES (2, 'lee', 500);",
             "SELECT * FROM member;",
             "\\d member"])

# ---------- part 2: UNIQUE, CHECK, names ----------
scene("uq", ["CREATE TABLE member (",
             "  id INTEGER,",
             "  name VARCHAR(20) NOT NULL,",
             "  email VARCHAR(50) UNIQUE",
             ");",
             "INSERT INTO member VALUES (1, 'kim', 'kim@mail.com');",
             "INSERT INTO member VALUES (2, 'lee', 'kim@mail.com');",
             "INSERT INTO member VALUES (2, 'lee', 'lee@mail.com');"])
scene("ck", ["CREATE TABLE product (",
             "  id INTEGER,",
             "  name VARCHAR(20) NOT NULL,",
             "  price INTEGER CHECK (price > 0),",
             "  stock INTEGER CHECK (stock >= 0)",
             ");",
             "INSERT INTO product VALUES (1, 'earphone', 0, 3);",
             "INSERT INTO product VALUES (1, 'earphone', 89000, -1);",
             "INSERT INTO product VALUES (1, 'earphone', 89000, 3);"])
scene("nm", ["CREATE TABLE product (",
             "  id INTEGER,",
             "  name VARCHAR(20) NOT NULL,",
             "  price INTEGER,",
             "  sale_price INTEGER,",
             "  CONSTRAINT price_positive CHECK (price > 0),",
             "  CONSTRAINT sale_lower CHECK (sale_price < price)",
             ");",
             "INSERT INTO product VALUES (1, 'tumbler', -15000, 12000);",
             "INSERT INTO product VALUES (1, 'tumbler', 15000, 18000);",
             "INSERT INTO product VALUES (1, 'tumbler', 15000, 12000);",
             "\\d product"])

# ---------- part 3: PRIMARY KEY, SERIAL, IDENTITY, composite ----------
scene("pk", ["CREATE TABLE member (",
             "  id INTEGER PRIMARY KEY,",
             "  name VARCHAR(20) NOT NULL",
             ");",
             "INSERT INTO member VALUES (1, 'kim');",
             "INSERT INTO member VALUES (1, 'lee');",
             "INSERT INTO member VALUES (NULL, 'park');",
             "\\d member"])
scene("sr", ["CREATE TABLE member (",
             "  id SERIAL PRIMARY KEY,",
             "  name VARCHAR(20) NOT NULL",
             ");",
             "INSERT INTO member (name) VALUES ('kim'), ('lee');",
             "SELECT * FROM member;",
             "\\d member"])
scene("sr-trap", ["INSERT INTO member VALUES (3, 'park');",
                  "INSERT INTO member (name) VALUES ('choi');",
                  "INSERT INTO member (name) VALUES ('choi');",
                  "SELECT * FROM member;"],
      setup=["CREATE TABLE member (id SERIAL PRIMARY KEY, name VARCHAR(20) NOT NULL);",
             "INSERT INTO member (name) VALUES ('kim'), ('lee');"])
scene("id", ["CREATE TABLE product (",
             "  id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,",
             "  name VARCHAR(20) NOT NULL,",
             "  price INTEGER",
             ");",
             "INSERT INTO product (name, price) VALUES ('earphone', 89000), ('tumbler', 15000);",
             "INSERT INTO product VALUES (3, 'battery', 32000);",
             "SELECT * FROM product;",
             "\\d product"])
scene("id-bd", ["CREATE TABLE product (",
                "  id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,",
                "  name VARCHAR(20) NOT NULL",
                ");",
                "INSERT INTO product (name) VALUES ('earphone');",
                "INSERT INTO product VALUES (2, 'tumbler');",
                "INSERT INTO product (name) VALUES ('battery');",
                "SELECT * FROM product;"])
scene("cp", ["CREATE TABLE order_item (",
             "  order_id INTEGER,",
             "  product_id INTEGER,",
             "  qty INTEGER NOT NULL,",
             "  PRIMARY KEY (order_id, product_id)",
             ");",
             "INSERT INTO order_item VALUES (1, 1, 1), (1, 2, 2), (2, 1, 1);",
             "INSERT INTO order_item VALUES (1, 1, 5);",
             "SELECT * FROM order_item;",
             "\\d order_item"])
scene("cu", ["CREATE TABLE cart_item (",
             "  id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,",
             "  member_id INTEGER,",
             "  product_id INTEGER,",
             "  qty INTEGER NOT NULL,",
             "  UNIQUE (member_id, product_id)",
             ");",
             "INSERT INTO cart_item (member_id, product_id, qty) VALUES (1, 1, 1), (1, 2, 2);",
             "INSERT INTO cart_item (member_id, product_id, qty) VALUES (1, 1, 3);",
             "INSERT INTO cart_item (member_id, product_id, qty) VALUES (NULL, 1, 1), (NULL, 1, 1);",
             "SELECT * FROM cart_item;"])
scene("cp-null", ["INSERT INTO order_item VALUES (NULL, 1, 1);"],
      setup=["CREATE TABLE order_item (order_id INTEGER, product_id INTEGER, qty INTEGER NOT NULL, PRIMARY KEY (order_id, product_id));"])

# ---------- part 4: FOREIGN KEY ----------
FK_SETUP = ["CREATE TABLE member (id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY, name VARCHAR(20) NOT NULL);"]
scene("fk", ["CREATE TABLE orders (",
             "  id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,",
             "  member_id INTEGER REFERENCES member (id),",
             "  total INTEGER NOT NULL",
             ");",
             "INSERT INTO member (name) VALUES ('kim'), ('lee');",
             "INSERT INTO orders (member_id, total) VALUES (1, 104000);",
             "INSERT INTO orders (member_id, total) VALUES (99, 15000);",
             "SELECT * FROM orders;"], setup=FK_SETUP)
FK_DATA = FK_SETUP + ["CREATE TABLE orders (id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY, member_id INTEGER REFERENCES member (id), total INTEGER NOT NULL);",
                      "INSERT INTO member (name) VALUES ('kim'), ('lee');",
                      "INSERT INTO orders (member_id, total) VALUES (1, 104000);"]
scene("fk-del", ["DELETE FROM member WHERE id = 1;",
                 "DELETE FROM member WHERE id = 2;",
                 "SELECT * FROM member;"], setup=FK_DATA)
scene("fk-drop", ["DROP TABLE member;",
                  "DROP TABLE orders;",
                  "DROP TABLE member;"], setup=FK_DATA)
scene("fk-order", ["CREATE TABLE orders (",
                   "  id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,",
                   "  member_id INTEGER REFERENCES member (id)",
                   ");"])
scene("fk-cascade", ["CREATE TABLE orders (",
                     "  id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,",
                     "  member_id INTEGER REFERENCES member (id) ON DELETE CASCADE,",
                     "  total INTEGER NOT NULL",
                     ");",
                     "INSERT INTO orders (member_id, total) VALUES (1, 104000), (1, 9000), (2, 15000);",
                     "DELETE FROM member WHERE id = 1;",
                     "SELECT * FROM orders;"],
      setup=FK_SETUP + ["INSERT INTO member (name) VALUES ('kim'), ('lee');"])
scene("fk-restrict", ["CREATE TABLE orders (",
                      "  id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,",
                      "  member_id INTEGER REFERENCES member (id) ON DELETE RESTRICT,",
                      "  total INTEGER NOT NULL",
                      ");",
                      "INSERT INTO orders (member_id, total) VALUES (1, 104000);",
                      "DELETE FROM member WHERE id = 1;"],
      setup=FK_SETUP + ["INSERT INTO member (name) VALUES ('kim'), ('lee');"])
scene("fk-setnull", ["CREATE TABLE orders (",
                     "  id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,",
                     "  member_id INTEGER REFERENCES member (id) ON DELETE SET NULL,",
                     "  total INTEGER NOT NULL",
                     ");",
                     "INSERT INTO orders (member_id, total) VALUES (1, 104000);",
                     "DELETE FROM member WHERE id = 1;",
                     "SELECT * FROM orders;"],
      setup=FK_SETUP + ["INSERT INTO member (name) VALUES ('kim'), ('lee');"])

# ---------- part 5: ALTER TABLE ----------
ALT_SETUP = [MEMBER0.replace(", age INTEGER", ""),
             "INSERT INTO member VALUES (1, 'kim', 'kim@mail.com'), (2, 'lee', 'kim@mail.com'), (3, NULL, 'park@mail.com');"]
scene("al-add", ["SELECT * FROM member;",
                 "ALTER TABLE member ADD CONSTRAINT member_email_key UNIQUE (email);",
                 "UPDATE member SET email = 'lee@mail.com' WHERE id = 2;",
                 "ALTER TABLE member ADD CONSTRAINT member_email_key UNIQUE (email);"], setup=ALT_SETUP)
scene("al-col", ["ALTER TABLE member ALTER COLUMN name SET NOT NULL;",
                 "UPDATE member SET name = 'park' WHERE id = 3;",
                 "ALTER TABLE member ALTER COLUMN name SET NOT NULL;",
                 "ALTER TABLE member ADD PRIMARY KEY (id);",
                 "ALTER TABLE member ADD COLUMN points INTEGER DEFAULT 0;",
                 "\\d member"], setup=ALT_SETUP + ["UPDATE member SET email = 'lee@mail.com' WHERE id = 2;",
                                                   "ALTER TABLE member ADD CONSTRAINT member_email_key UNIQUE (email);"])
scene("al-drop", ["ALTER TABLE member DROP CONSTRAINT member_email_key;",
                  "ALTER TABLE member ALTER COLUMN name DROP NOT NULL;",
                  "ALTER TABLE member ALTER COLUMN points SET DEFAULT 100;",
                  "\\d member"],
      setup=["CREATE TABLE member (id INTEGER PRIMARY KEY, name VARCHAR(20) NOT NULL, email VARCHAR(50) CONSTRAINT member_email_key UNIQUE, points INTEGER DEFAULT 0);"])

# ---------- part 6: traps ----------
scene("tr-null", ["CREATE TABLE member (",
                  "  id INTEGER PRIMARY KEY,",
                  "  email VARCHAR(50) UNIQUE,",
                  "  points INTEGER DEFAULT 0 CHECK (points >= 0)",
                  ");",
                  "INSERT INTO member VALUES (1, NULL, NULL), (2, NULL, NULL);",
                  "SELECT * FROM member;"])
scene("tr-default", ["INSERT INTO member VALUES (3, 'kim@mail.com', DEFAULT);",
                     "SELECT * FROM member;"], keep=True)
scene("tr-fix", ["CREATE TABLE member (",
                 "  id INTEGER PRIMARY KEY,",
                 "  email VARCHAR(50) NOT NULL UNIQUE,",
                 "  points INTEGER NOT NULL DEFAULT 0 CHECK (points >= 0)",
                 ");",
                 "INSERT INTO member VALUES (1, NULL, NULL);",
                 "INSERT INTO member VALUES (1, 'kim@mail.com', NULL);",
                 "INSERT INTO member (id, email) VALUES (1, 'kim@mail.com');"])

# ---------- part 6: the shopping cart of 28 as tables ----------
SHOP = ["CREATE TABLE member (",
        "  id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,",
        "  name VARCHAR(20) NOT NULL,",
        "  email VARCHAR(50) NOT NULL UNIQUE",
        ");",
        "CREATE TABLE product (",
        "  id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,",
        "  name VARCHAR(20) NOT NULL,",
        "  price INTEGER NOT NULL CHECK (price > 0),",
        "  stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0)",
        ");",
        "CREATE TABLE cart_item (",
        "  member_id INTEGER REFERENCES member (id) ON DELETE CASCADE,",
        "  product_id INTEGER REFERENCES product (id),",
        "  qty INTEGER NOT NULL CHECK (qty > 0),",
        "  PRIMARY KEY (member_id, product_id)",
        ");"]
scene("ex-make", SHOP + ["\\dt"])
SHOP_SQL = [" ".join(SHOP[0:5]), " ".join(SHOP[5:11]), " ".join(SHOP[11:17])]
DATA = ["INSERT INTO member (name, email) VALUES ('kim', 'kim@mail.com'), ('lee', 'lee@mail.com');",
        "INSERT INTO product (name, price, stock) VALUES ('earphone', 89000, 3), ('tumbler', 15000, 10), ('battery', 32000, 5), ('mousepad', 9000, 0), ('usb hub', 30000, 10);"]
scene("ex-data", DATA + ["SELECT * FROM product;"], setup=SHOP_SQL)
scene("ex-cart", ["INSERT INTO cart_item VALUES (1, 1, 1), (1, 2, 2);",
                  "INSERT INTO cart_item VALUES (1, 2, 1);",
                  "UPDATE cart_item SET qty = qty + 1 WHERE member_id = 1 AND product_id = 2;",
                  "INSERT INTO cart_item VALUES (1, 9, 1);",
                  "INSERT INTO cart_item VALUES (1, 3, 0);",
                  "SELECT * FROM cart_item;"], setup=SHOP_SQL + DATA)
CART = ["INSERT INTO cart_item VALUES (1, 1, 1), (1, 2, 3), (2, 2, 1);"]
scene("ex-leave", ["DELETE FROM product WHERE id = 2;",
                   "DELETE FROM member WHERE id = 1;",
                   "SELECT * FROM cart_item;",
                   "INSERT INTO member (name, email) VALUES ('park', 'lee@mail.com');",
                   "UPDATE product SET stock = -1 WHERE id = 3;"], setup=SHOP_SQL + DATA + CART)

json.dump(OUT, open(os.path.join(HERE, "out.json"), "w"), ensure_ascii=False, indent=1)
sh("docker rm -f my-pg")
print("scenes:", len(OUT))
