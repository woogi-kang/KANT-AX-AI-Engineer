"""Runs every psql session of the SQL 7 deck (42, insert, update and delete with other tables) for real and saves what
the student would see in tools/out.json.
    sudo -n dockerd &        (once, in the cloud container)
    uv run --with pyte python tools/demo.py              (all scenes)
    uv run --with pyte python tools/demo.py union        (only these scenes, merged into out.json)
Real Docker and the official postgres:18 image, with the names of 35: container my-pg, password admin1234, database
kant_shop. The tables are the class example (a sports center) in tools/sports.sql, shared by the SQL 3-7 decks
(38-42). Each scene starts from a fresh kant_shop with sports.sql loaded, then runs its `pre` statements quietly.
psql runs in a pseudo-terminal 160 columns wide, and the statements are typed line by line after the prompt shows,
the way a student types them."""
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

CONTACT = """CREATE TABLE contact_lists (
    request_id   SERIAL       PRIMARY KEY,
    member_id    INTEGER      NOT NULL,
    name         VARCHAR(20)  NOT NULL,
    reason       VARCHAR(50)  NOT NULL,
    request_date DATE         NOT NULL
);"""
FILL = """INSERT INTO contact_lists (member_id, name, reason, request_date)
SELECT member_id, name, '이메일 미등록' AS reason, CAST('2026-11-19' AS DATE) AS request_date FROM members WHERE email IS NULL
UNION
SELECT member_id, name, '전화번호 미등록', '2026-11-19'::DATE FROM members WHERE phone IS NULL
ORDER BY member_id, reason;"""


def sh(cmd, stdin=None, cwd=HOME):
    return subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, input=stdin, env={**os.environ, **ENV})


def fresh(seed=True, pre=""):
    sh('docker exec my-pg psql -U postgres -c "DROP DATABASE IF EXISTS kant_shop WITH (FORCE)" -c "CREATE DATABASE kant_shop"')
    if seed:
        r = sh("docker exec -i my-pg psql -q -U postgres -d kant_shop -v ON_ERROR_STOP=1", open(SEED).read() + "\n" + pre)
        if r.returncode:
            raise SystemExit(r.stderr)


def scene(name, inputs, seed=True, pre=""):
    if ONLY and name not in ONLY:
        return
    fresh(seed, pre)
    lines = ptyrun.run(PSQL, HOME, inputs=list(inputs) + ["\\q"], env=ENV, prompt=PROMPT, cols=160)
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

# ---------- intro ----------
scene("why", ["SELECT member_id, name FROM members WHERE email IS NULL;",
              "INSERT INTO contact_lists (member_id, name, reason, request_date) VALUES",
              "(3, '박도현', '이메일 미등록', '2026-11-19'),",
              "(5, '정하은', '이메일 미등록', '2026-11-19'),",
              "(10, '임준서', '이메일 미등록', '2026-11-19'),",
              "(16, '황민서', '이메일 미등록', '2026-11-19'),",
              "(17, '안태윤', '이메일 미등록', '2026-11-19'),",
              "(24, '양다인', '이메일 미등록', '2026-11-19'),",
              "(27, '백준혁', '이메일 미등록', '2026-11-19'),",
              "(31, '하동건', '이메일 미등록', '2026-11-19'),",
              "(38, '진우성', '이메일 미등록', '2026-11-19');"], pre=CONTACT)
scene("min", ["INSERT INTO contact_lists (member_id, name, reason, request_date)",
              "SELECT member_id, name, '이메일 미등록', '2026-11-19'",
              "FROM members",
              "WHERE email IS NULL;",
              "SELECT * FROM contact_lists;"], pre=CONTACT)

# ---------- part 1: insert rows picked from another table ----------
scene("create", CONTACT.split("\n") + ["SELECT * FROM contact_lists;"])
scene("fixed", ["SELECT member_id, name, '이메일 미등록' AS reason, '2026-11-19' AS request_date",
                "FROM members",
                "WHERE email IS NULL;"])
scene("union-err", ["INSERT INTO contact_lists (member_id, name, reason, request_date)",
                    "SELECT member_id, name, '이메일 미등록', '2026-11-19' FROM members WHERE email IS NULL",
                    "UNION",
                    "SELECT member_id, name, '전화번호 미등록', '2026-11-19' FROM members WHERE phone IS NULL;"], pre=CONTACT)
scene("cast", ["SELECT '2026-11-19' + 7;",
               "SELECT CAST('2026-11-19' AS DATE) + 7 AS 일주일뒤, '2026-11-19'::DATE + 7 AS 같은값;",
               "SELECT '120'::INTEGER + 1 AS 숫자로;"])
scene("union", ["INSERT INTO contact_lists (member_id, name, reason, request_date)",
                "SELECT member_id, name, '이메일 미등록' AS reason, CAST('2026-11-19' AS DATE) AS request_date",
                "FROM members WHERE email IS NULL",
                "UNION",
                "SELECT member_id, name, '전화번호 미등록', '2026-11-19'::DATE",
                "FROM members WHERE phone IS NULL",
                "ORDER BY member_id, reason",
                "RETURNING request_id, member_id, name, reason;"], pre=CONTACT)

# ---------- part 2: update several columns, by calculation, with a subquery ----------
scene("alter", ["ALTER TABLE courses ADD COLUMN class_days VARCHAR(10);",
                "ALTER TABLE courses ADD COLUMN is_open BOOLEAN NOT NULL DEFAULT true;",
                "SELECT course_id, course_name, class_days, is_open FROM courses WHERE course_id <= 4;"])
scene("multi", ["SELECT course_id, course_name, class_days, start_time FROM courses WHERE course_id = 9;",
                "UPDATE courses",
                "SET class_days = '월수금', start_time = '20:00'",
                "WHERE course_id = 9",
                "RETURNING course_id, course_name, class_days, start_time;"],
      pre="ALTER TABLE courses ADD COLUMN class_days VARCHAR(10);")
scene("calc", ["UPDATE courses SET fee = fee * 1.05 WHERE sport_id = 1 RETURNING course_id, fee;"])
scene("round", ["SELECT course_name, fee, fee / 1.1 AS 공급가 FROM courses WHERE course_id IN (1, 8);",
                "ALTER TABLE courses ADD COLUMN supply INTEGER;",
                "UPDATE courses SET supply = fee / 1.1 WHERE course_id IN (1, 8)",
                "RETURNING course_name, fee, supply;"])
scene("sub-upd", ["SELECT course_id FROM enrollments",
                  "WHERE enroll_month = '2026-11'",
                  "GROUP BY course_id",
                  "HAVING COUNT(*) >= 5",
                  "ORDER BY course_id;",
                  "UPDATE courses",
                  "SET capacity = capacity + 5",
                  "WHERE course_id IN (",
                  "    SELECT course_id FROM enrollments",
                  "    WHERE enroll_month = '2026-11'",
                  "    GROUP BY course_id",
                  "    HAVING COUNT(*) >= 5",
                  ")",
                  "RETURNING course_id, course_name, capacity;"])

# ---------- part 3: EXISTS and NOT EXISTS ----------
scene("ex-min", ["SELECT 1 FROM enrollments WHERE member_id = 10;",
                 "SELECT EXISTS (SELECT 1 FROM enrollments WHERE member_id = 10);",
                 "SELECT EXISTS (SELECT 1 FROM enrollments WHERE member_id = 40);"])
scene("exists", ["SELECT m.member_id, m.name",
                 "FROM members m",
                 "WHERE EXISTS (",
                 "    SELECT 1 FROM enrollments e",
                 "    WHERE e.member_id = m.member_id",
                 "      AND e.course_id = 13 AND e.enroll_month = '2026-11'",
                 ");",
                 "SELECT member_id, name FROM members",
                 "WHERE member_id IN (",
                 "    SELECT member_id FROM enrollments",
                 "    WHERE course_id = 13 AND enroll_month = '2026-11'",
                 ");"])
scene("not-exists", ["SELECT m.member_id, m.name, m.region",
                     "FROM members m",
                     "WHERE NOT EXISTS (",
                     "    SELECT 1 FROM enrollments e",
                     "    WHERE e.member_id = m.member_id",
                     ");"])
scene("notin-null", ["SELECT course_id, course_name, instructor_id FROM courses WHERE course_id IN (4, 5, 6);",
                     "SELECT name FROM instructors",
                     "WHERE instructor_id NOT IN (SELECT instructor_id FROM courses);",
                     "SELECT i.name FROM instructors i",
                     "WHERE NOT EXISTS (SELECT 1 FROM courses c WHERE c.instructor_id = i.instructor_id);"])

# ---------- part 4: delete, truncate, drop ----------
scene("del-check", ["SELECT m.member_id, m.name",
                    "FROM members m",
                    "WHERE NOT EXISTS (SELECT 1 FROM enrollments e WHERE e.member_id = m.member_id);",
                    "DELETE FROM members m",
                    "WHERE NOT EXISTS (SELECT 1 FROM enrollments e WHERE e.member_id = m.member_id)",
                    "RETURNING m.member_id, m.name;"])
scene("fk-err", ["DELETE FROM members WHERE member_id = 10;"])
scene("three", ["DELETE FROM contact_lists WHERE reason = '전화번호 미등록';",
                "SELECT COUNT(*) FROM contact_lists;",
                "TRUNCATE contact_lists RESTART IDENTITY;",
                "SELECT COUNT(*) FROM contact_lists;",
                "DROP TABLE contact_lists;",
                "SELECT COUNT(*) FROM contact_lists;"], pre=CONTACT + "\n" + FILL)

# ---------- part 5: errors and traps ----------
scene("err-count", ["INSERT INTO contact_lists (member_id, name, reason, request_date)",
                    "SELECT member_id, name, '이메일 미등록' FROM members WHERE email IS NULL;"], pre=CONTACT)
scene("err-order", ["INSERT INTO contact_lists (member_id, name, reason, request_date)",
                    "SELECT name, member_id, '이메일 미등록', '2026-11-19' FROM members WHERE email IS NULL;"], pre=CONTACT)
scene("err-link", ["SELECT COUNT(*) FROM members m",
                   "WHERE NOT EXISTS (SELECT 1 FROM enrollments e WHERE e.member_id = m.member_id);",
                   "SELECT COUNT(*) FROM members m",
                   "WHERE NOT EXISTS (SELECT 1 FROM enrollments e);",
                   "SELECT COUNT(*) FROM members m",
                   "WHERE EXISTS (SELECT 1 FROM enrollments e);"])
scene("err-notnull", ["ALTER TABLE courses ADD COLUMN class_days VARCHAR(10) NOT NULL;",
                      "ALTER TABLE courses ADD COLUMN class_days VARCHAR(10) NOT NULL DEFAULT '미정';",
                      "SELECT course_id, class_days FROM courses WHERE course_id <= 3;"])

# ---------- part 6: real cases ----------
scene("r-move", ["CREATE TABLE cancelled (",
                 "    enrollment_id INTEGER PRIMARY KEY,",
                 "    member_id     INTEGER,",
                 "    course_id     INTEGER,",
                 "    enroll_month  VARCHAR(7)",
                 ");",
                 "INSERT INTO cancelled",
                 "SELECT enrollment_id, member_id, course_id, enroll_month",
                 "FROM enrollments WHERE status = '취소';",
                 "DELETE FROM enrollments WHERE status = '취소';",
                 "SELECT COUNT(*) FROM enrollments;"])
scene("r-teacher", ["SELECT i.instructor_id, i.name, i.sport_id FROM instructors i",
                    "WHERE NOT EXISTS (SELECT 1 FROM courses c WHERE c.instructor_id = i.instructor_id);",
                    "SELECT course_id, course_name, sport_id FROM courses WHERE instructor_id IS NULL;",
                    "UPDATE courses",
                    "SET instructor_id = (SELECT instructor_id FROM instructors WHERE name = '윤태호')",
                    "WHERE course_id = 5",
                    "RETURNING course_id, course_name, instructor_id;"])
scene("r-contact", ["UPDATE members SET email = 'user03@gmail.com' WHERE member_id = 3;",
                    "UPDATE members SET email = 'user10@naver.com' WHERE member_id = 10;",
                    "DELETE FROM contact_lists",
                    "WHERE reason = '이메일 미등록'",
                    "  AND member_id IN (SELECT member_id FROM members WHERE email IS NOT NULL)",
                    "RETURNING request_id, member_id, name;",
                    "SELECT COUNT(*) FROM contact_lists;"], pre=CONTACT + "\n" + FILL)

json.dump(OUT, open(OUTF, "w"), ensure_ascii=False, indent=1)
sh("docker rm -f my-pg")
print("saved", OUTF)
