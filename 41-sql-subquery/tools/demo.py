"""Runs every psql session of the SQL 6 deck (41, subqueries) for real and saves what the student would see in tools/out.json.
    sudo -n dockerd &        (once, in the cloud container)
    uv run --with pyte python tools/demo.py              (all scenes)
    uv run --with pyte python tools/demo.py f-wrap       (only these scenes, merged into out.json)
Real Docker and the official postgres:18 image, with the names of 35: container my-pg, password admin1234, database
kant_shop. The tables are the class example (a sports center) in tools/sports.sql, shared by the SQL 3-6 decks
(38-41). Each scene starts from a fresh kant_shop with sports.sql loaded. psql runs in a pseudo-terminal 160 columns
wide, and the statements are typed line by line after the prompt shows, the way a student types them."""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ptyrun  # noqa: E402

HOME = "/home/kim"
ENV = {"HOME": HOME, "NO_COLOR": "1"}
OUTF = os.path.join(HERE, "out.json")
ONLY = set(sys.argv[1:])
OUT = json.load(open(OUTF)) if ONLY and os.path.exists(OUTF) else {}
PROMPT = rb"(=# |-# |'# |\(# |=> |\$ |# )$"
RUN = "docker run -d --name my-pg -e POSTGRES_PASSWORD=admin1234 -p 5432:5432 postgres:18"
PSQL = "docker exec -it my-pg psql -U postgres -d kant_shop"
SEED = os.path.join(HERE, "sports.sql")


def sh(cmd, stdin=None, cwd=HOME):
    return subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, input=stdin, env={**os.environ, **ENV})


def fresh(seed=True):
    sh('docker exec my-pg psql -U postgres -c "DROP DATABASE IF EXISTS kant_shop WITH (FORCE)" -c "CREATE DATABASE kant_shop"')
    if seed:
        r = sh("docker exec -i my-pg psql -q -U postgres -d kant_shop -v ON_ERROR_STOP=1", open(SEED).read())
        if r.returncode:
            raise SystemExit(r.stderr)


def scene(name, inputs, seed=True):
    if ONLY and name not in ONLY:
        return
    fresh(seed)
    lines = ptyrun.run(PSQL, HOME, inputs=list(inputs) + ["\\q"], env=ENV, prompt=PROMPT, cols=160)
    OUT.setdefault(name, [])
    OUT[name] = [{"cmd": PSQL, "cwd": "~", "out": lines}]
    print(f"== {name}")
    print("\n".join(lines))


def shell(name, cmd, seed=False, cwd=HOME):
    if ONLY and name not in ONLY:
        return
    fresh(seed)
    r = sh(cmd, cwd=cwd)
    lines = (r.stdout + r.stderr).rstrip("\n").split("\n")
    OUT[name] = [{"cmd": cmd, "cwd": "~", "out": lines}]
    print(f"== {name}: {cmd}")
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

# ---------- setup: load the class file ----------
sh(f"cp {SEED} {HOME}/sports.sql")
shell("load", "docker exec -i my-pg psql -U postgres -d kant_shop < sports.sql")
scene("tables", ["\\dt"])

# ---------- intro ----------
scene("why", ["SELECT AVG(fee) FROM courses;",
              "SELECT course_name, fee FROM courses WHERE fee > 97857 ORDER BY fee DESC;"])
scene("min", ["SELECT course_name, fee",
              "FROM courses",
              "WHERE fee > (",
              "    SELECT AVG(fee) FROM courses",
              ")",
              "ORDER BY fee DESC, course_name;"])

# ---------- part 1: one value in WHERE ----------
scene("w-max", ["SELECT course_name, fee FROM courses WHERE fee = (SELECT MAX(fee) FROM courses);",
                "SELECT name, birth_year FROM members WHERE birth_year = (SELECT MIN(birth_year) FROM members);"])
scene("w-sport", ["SELECT AVG(fee) FROM courses WHERE sport_id = 1;",
                  "SELECT course_name, fee FROM courses",
                  "WHERE sport_id = 1",
                  "  AND fee > (SELECT AVG(fee) FROM courses WHERE sport_id = 1);"])
scene("w-auto", ["INSERT INTO courses VALUES (15, 2, '헬스 PT 집중', '고급', '21:30', 200000, 6, 3);",
                 "SELECT course_name, fee FROM courses WHERE fee > 97857 ORDER BY fee DESC;",
                 "SELECT course_name, fee FROM courses WHERE fee > (SELECT AVG(fee) FROM courses) ORDER BY fee DESC;",
                 "SELECT ROUND(AVG(fee), 2) FROM courses;"])

# ---------- part 2: a list with IN ----------
scene("i-err", ["SELECT member_id FROM enrollments WHERE course_id = 13 AND enroll_month = '2026-11';",
                "SELECT name FROM members",
                "WHERE member_id = (SELECT member_id FROM enrollments WHERE course_id = 13 AND enroll_month = '2026-11');"])
scene("i-in", ["SELECT name, phone FROM members WHERE member_id IN (11, 25);",
               "SELECT name, phone",
               "FROM members",
               "WHERE member_id IN (",
               "    SELECT member_id FROM enrollments",
               "    WHERE course_id = 13 AND enroll_month = '2026-11'",
               ");"])
scene("i-notin", ["SELECT name, region FROM members",
                  "WHERE member_id NOT IN (",
                  "    SELECT member_id FROM enrollments WHERE enroll_month = '2026-11'",
                  ")",
                  "ORDER BY name;"])
scene("i-join", ["SELECT m.name, m.phone",
                 "FROM enrollments e",
                 "JOIN members m ON e.member_id = m.member_id",
                 "WHERE e.course_id = 13 AND e.enroll_month = '2026-11';"])

# ---------- part 3: a table in FROM ----------
scene("f-err", ["SELECT member_id, SUM(pay_amount) FROM enrollments",
                "WHERE SUM(pay_amount) >= 600000",
                "GROUP BY member_id;"])
scene("f-inner", ["SELECT member_id, SUM(pay_amount) AS total_paid",
                  "FROM enrollments",
                  "GROUP BY member_id",
                  "ORDER BY member_id;"])
scene("f-wrap", ["SELECT *",
                 "FROM (",
                 "    SELECT member_id, SUM(pay_amount) AS total_paid",
                 "    FROM enrollments",
                 "    GROUP BY member_id",
                 ") AS paid",
                 "WHERE paid.total_paid >= 600000",
                 "ORDER BY paid.total_paid DESC;"])
scene("f-join", ["SELECT",
                 "    paid.member_id  AS 회원번호,",
                 "    m.name          AS 회원명,",
                 "    paid.total_paid AS 매출액",
                 "FROM (",
                 "    SELECT member_id, SUM(pay_amount) AS total_paid",
                 "    FROM enrollments",
                 "    GROUP BY member_id",
                 ") AS paid",
                 "LEFT JOIN members m ON paid.member_id = m.member_id",
                 "WHERE paid.total_paid >= 600000",
                 "ORDER BY paid.total_paid DESC, paid.member_id;"])
scene("f-having", ["SELECT member_id, SUM(pay_amount) AS total_paid",
                   "FROM enrollments",
                   "GROUP BY member_id",
                   "HAVING SUM(pay_amount) >= 600000",
                   "ORDER BY total_paid DESC;"])
scene("f-avg", ["SELECT ROUND(AVG(SUM(pay_amount))) FROM enrollments GROUP BY member_id;",
                "SELECT ROUND(AVG(total_paid)) AS 회원당평균",
                "FROM (",
                "    SELECT member_id, SUM(pay_amount) AS total_paid",
                "    FROM enrollments",
                "    GROUP BY member_id",
                ") AS paid;"])
scene("f-noalias", ["SELECT paid.member_id, m.name",
                    "FROM (SELECT member_id, SUM(pay_amount) AS total_paid FROM enrollments GROUP BY member_id)",
                    "JOIN members m ON paid.member_id = m.member_id;"])

# ---------- part 4: one value in SELECT ----------
scene("s-col", ["SELECT",
                "    course_name,",
                "    fee,",
                "    (SELECT ROUND(AVG(fee), 2) FROM courses) AS 전체평균,",
                "    fee - (SELECT ROUND(AVG(fee), 2) FROM courses) AS 평균과차이",
                "FROM courses;"])
scene("s-ratio", ["SELECT",
                  "    region,",
                  "    COUNT(*) AS 회원수,",
                  "    (SELECT COUNT(*) FROM members) AS 전체,",
                  "    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM members), 1) AS 비율",
                  "FROM members",
                  "GROUP BY region",
                  "ORDER BY 회원수 DESC;"])
scene("s-err", ["SELECT course_name, (SELECT AVG(fee), MAX(fee) FROM courses) FROM courses;"])

# ---------- part 5: look inside ----------
scene("explain", ["EXPLAIN ANALYZE",
                  "SELECT course_name, fee FROM courses",
                  "WHERE fee > (SELECT AVG(fee) FROM courses);"])

# ---------- part 6: errors and real cases ----------
scene("x-paren", ["SELECT course_name FROM courses WHERE fee > SELECT AVG(fee) FROM courses;",
                  "SELECT course_name FROM courses WHERE fee > (SELECT AVG(fee) FROM courses;"])
scene("r-seat", ["SELECT c.course_name, c.capacity AS 정원, n.cnt AS 신청, c.capacity - n.cnt AS 남은자리",
                 "FROM courses c",
                 "JOIN (",
                 "    SELECT course_id, COUNT(*) AS cnt",
                 "    FROM enrollments",
                 "    WHERE enroll_month = '2026-11' AND status <> '취소'",
                 "    GROUP BY course_id",
                 ") AS n ON c.course_id = n.course_id",
                 "ORDER BY 남은자리, c.course_name",
                 "LIMIT 5;"])
scene("r-pop", ["SELECT course_id, COUNT(*) FROM enrollments",
                "WHERE status <> '취소' GROUP BY course_id ORDER BY COUNT(*) DESC LIMIT 3;",
                "SELECT course_name, fee",
                "FROM courses",
                "WHERE course_id = (",
                "    SELECT course_id FROM enrollments",
                "    WHERE status <> '취소'",
                "    GROUP BY course_id",
                "    ORDER BY COUNT(*) DESC",
                "    LIMIT 1",
                ");"])
scene("r-sms", ["SELECT name, phone",
                "FROM members",
                "WHERE member_id NOT IN (",
                "    SELECT member_id FROM enrollments",
                "    WHERE enroll_month = '2026-11'",
                ")",
                "AND phone IS NOT NULL",
                "ORDER BY name;"])

# ---------- the same filter in Python (23's comprehension) ----------
if not ONLY or "py" in ONLY:
    r = subprocess.run(["python3", os.path.join(HERE, "fees.py")], capture_output=True, text=True)
    OUT["py"] = [{"cmd": "uv run fees.py", "cwd": "~", "out": r.stdout.rstrip("\n").split("\n")}]

json.dump(OUT, open(OUTF, "w"), ensure_ascii=False, indent=1)
print("saved", len(OUT), "scenes")
