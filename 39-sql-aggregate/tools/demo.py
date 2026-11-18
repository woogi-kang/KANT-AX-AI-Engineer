"""Runs every psql session of the SQL 4 deck (39, aggregate functions and GROUP BY) for real and saves what the
student would see in tools/out.json.
    sudo -n dockerd &        (once, in the cloud container)
    uv run --with pyte python tools/demo.py              (all scenes)
    uv run --with pyte python tools/demo.py g-month      (only these scenes, merged into out.json)
Real Docker and the official postgres:18 image, with the names of 35 (the class repo): container my-pg, password
admin1234, database kant_shop. The tables are the class sports-center database of 38 to 41 (sports.sql in the chapter folder, made by
tools/make_sports.py with a fixed seed): sports, instructors, courses, members, enrollments. psql runs in a
pseudo-terminal 160 columns wide and every statement is typed line by line after the prompt shows."""
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


def sh(cmd, stdin=None):
    return subprocess.run(cmd, shell=True, cwd=HOME, capture_output=True, text=True, input=stdin, env={**os.environ, **ENV})


def scene(name, inputs):
    if ONLY and name not in ONLY:
        return
    lines = ptyrun.run(PSQL, HOME, inputs=list(inputs) + ["\\q"], env=ENV, prompt=PROMPT, cols=160)
    OUT[name] = [{"cmd": PSQL, "cwd": "~", "out": lines}]
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
sh('docker exec my-pg psql -U postgres -c "CREATE DATABASE kant_shop"')
r = sh("docker exec -i my-pg psql -U postgres -d kant_shop -q -v ON_ERROR_STOP=1", open(os.path.join(HERE, "..", "sports.sql")).read())
if r.returncode:
    raise SystemExit(r.stderr)
OUT["version"] = [{"cmd": "", "cwd": "~", "out": [sh('docker exec my-pg psql -U postgres -tAc "SELECT version()"').stdout.strip()]}]

NOV = "WHERE enroll_month = '2026-11'"

# ---------- intro ----------
scene("why", ["SELECT enrollment_id, pay_amount FROM enrollments",
              f"{NOV};"])
scene("why-sum", ["SELECT SUM(pay_amount) FROM enrollments",
                  f"{NOV};"])
scene("min", ["SELECT COUNT(*) FROM courses;"])

# ---------- part 1: five aggregate functions ----------
scene("courses", ["SELECT course_id, course_name, fee, capacity FROM courses;"])
scene("minmax", ["SELECT MIN(fee), MAX(fee) FROM courses;"])
scene("sum", ["SELECT SUM(capacity) FROM courses;"])
scene("avg", ["SELECT AVG(fee) FROM courses;",
              "SELECT ROUND(AVG(fee), 2) FROM courses;",
              "SELECT ROUND(AVG(fee)) FROM courses;"])
scene("avg-why", ["SELECT SUM(fee), COUNT(fee), AVG(fee) FROM courses;"])
scene("five", ["SELECT",
               "    COUNT(*)            AS 강좌수,",
               "    MIN(fee)            AS 최저수강료,",
               "    MAX(fee)            AS 최고수강료,",
               "    SUM(capacity)       AS 전체정원,",
               "    ROUND(AVG(fee), 2)  AS 평균수강료",
               "FROM courses;"])
scene("nov", ["SELECT COUNT(*) FROM enrollments;",
              "SELECT",
              "    COUNT(*)        AS 신청건수,",
              "    SUM(pay_amount) AS 매출,",
              "    MAX(pay_amount) AS 최고결제",
              "FROM enrollments",
              f"{NOV};"])

# ---------- part 2: COUNT and NULL ----------
scene("nulls", ["SELECT member_id, name, email, phone FROM members",
                "WHERE member_id <= 10;"])
scene("count3-10", ["SELECT COUNT(*), COUNT(email), COUNT(phone) FROM members",
                    "WHERE member_id <= 10;"])
scene("count3", ["SELECT",
                 "    COUNT(*)               AS 회원수,",
                 "    COUNT(email)           AS 이메일있음,",
                 "    COUNT(phone)           AS 전화번호있음,",
                 "    COUNT(DISTINCT region) AS 사는구",
                 "FROM members;"])
scene("distinct", ["SELECT DISTINCT region FROM members;",
                   "SELECT COUNT(region), COUNT(DISTINCT region) FROM members;"])
scene("zero", ["SELECT COUNT(*), ROUND(AVG(pay_amount)) AS 평균결제",
               "FROM enrollments",
               f"{NOV};",
               "SELECT COUNT(*), ROUND(AVG(pay_amount)) AS 평균결제",
               "FROM enrollments",
               f"{NOV} AND status <> '취소';"])
scene("empty", ["SELECT COUNT(*), SUM(pay_amount), MAX(pay_amount)",
                "FROM enrollments",
                "WHERE enroll_month = '2026-12';"])

# ---------- part 3: GROUP BY ----------
scene("g-why", ["SELECT COUNT(*), SUM(pay_amount) FROM enrollments WHERE enroll_month = '2026-09';",
                "SELECT COUNT(*), SUM(pay_amount) FROM enrollments WHERE enroll_month = '2026-10';",
                "SELECT COUNT(*), SUM(pay_amount) FROM enrollments WHERE enroll_month = '2026-11';"])
scene("g-small", ["SELECT enrollment_id, enroll_month, status, pay_amount",
                  "FROM enrollments WHERE course_id = 11;"])
scene("g-small-all", ["SELECT COUNT(*), SUM(pay_amount)",
                      "FROM enrollments WHERE course_id = 11;"])
scene("g-small-by", ["SELECT enroll_month, COUNT(*), SUM(pay_amount)",
                     "FROM enrollments WHERE course_id = 11",
                     "GROUP BY enroll_month;"])
scene("g-month", ["SELECT",
                  "    enroll_month    AS 신청월,",
                  "    COUNT(*)        AS 신청건수,",
                  "    SUM(pay_amount) AS 매출",
                  "FROM enrollments",
                  "GROUP BY enroll_month",
                  "ORDER BY enroll_month;"])
scene("g-level", ["SELECT level, COUNT(*) AS 강좌수, ROUND(AVG(fee)) AS 평균수강료",
                  "FROM courses",
                  "GROUP BY level;",
                  "SELECT level, COUNT(*) AS 강좌수, ROUND(AVG(fee)) AS 평균수강료",
                  "FROM courses",
                  "GROUP BY level",
                  "ORDER BY 평균수강료;"])
scene("g-two-small", ["SELECT enroll_month, status, COUNT(*)",
                      "FROM enrollments WHERE course_id = 11",
                      "GROUP BY enroll_month, status",
                      "ORDER BY enroll_month, status;"])
scene("g-two", ["SELECT",
                "    enroll_month, status, COUNT(*) AS 건수",
                "FROM enrollments",
                "GROUP BY enroll_month, status",
                "ORDER BY enroll_month, status;"])
scene("g-err", ["SELECT enroll_month, member_id, COUNT(*)",
                "FROM enrollments",
                "GROUP BY enroll_month;"])
scene("g-fix", ["SELECT enroll_month, COUNT(DISTINCT member_id) AS 회원수",
                "FROM enrollments",
                "GROUP BY enroll_month",
                "ORDER BY enroll_month;"])
scene("g-err2", ["SELECT enroll_month, COUNT(*) FROM enrollments;"])

# ---------- part 4: HAVING ----------
scene("h-course-all", ["SELECT course_id, COUNT(*) AS 누적신청",
                       "FROM enrollments",
                       "WHERE status <> '취소'",
                       "GROUP BY course_id",
                       "ORDER BY 누적신청 DESC, course_id;"])
scene("h-where", ["SELECT course_id, COUNT(*) AS 누적신청",
                  "FROM enrollments",
                  "WHERE status <> '취소' AND COUNT(*) >= 18",
                  "GROUP BY course_id;"])
scene("h-course", ["SELECT",
                   "    course_id, COUNT(*) AS 누적신청",
                   "FROM enrollments",
                   "WHERE status <> '취소'",
                   "GROUP BY course_id",
                   "HAVING COUNT(*) >= 18",
                   "ORDER BY 누적신청 DESC, course_id;"])
scene("h-nowhere", ["SELECT",
                    "    course_id, COUNT(*) AS 누적신청",
                    "FROM enrollments",
                    "GROUP BY course_id",
                    "HAVING COUNT(*) >= 18",
                    "ORDER BY 누적신청 DESC, course_id;"])
scene("h-region", ["SELECT",
                   "    region, COUNT(*) AS 회원수",
                   "FROM members",
                   "GROUP BY region",
                   "HAVING COUNT(*) >= 10",
                   "ORDER BY 회원수 DESC, region;"])
scene("h-alias", ["SELECT course_id, COUNT(*) AS 누적신청",
                  "FROM enrollments",
                  "GROUP BY course_id",
                  "HAVING 누적신청 >= 18;"])
scene("h-small", ["SELECT enroll_month, COUNT(*)",
                  "FROM enrollments WHERE course_id = 11 AND status <> '취소'",
                  "GROUP BY enroll_month",
                  "HAVING COUNT(*) >= 2;"])

# ---------- part 5: compare, errors ----------
scene("c-distinct", ["SELECT DISTINCT region FROM members ORDER BY region;",
                     "SELECT region FROM members GROUP BY region ORDER BY region;",
                     "SELECT region, COUNT(*) FROM members GROUP BY region ORDER BY region;"])
scene("c-py-sql", ["SELECT region, COUNT(*)",
                   "FROM members",
                   "GROUP BY region;"])
scene("x-sum-text", ["SELECT COUNT(name), MIN(name), MAX(name) FROM members;",
                     "SELECT SUM(name) FROM members;"])

# ---------- part 6: real situations ----------
scene("ex-report", ["SELECT",
                    "    enroll_month           AS 신청월,",
                    "    COUNT(*)               AS 건수,",
                    "    SUM(pay_amount)        AS 매출,",
                    "    ROUND(AVG(pay_amount)) AS 평균결제",
                    "FROM enrollments",
                    "WHERE status <> '취소'",
                    "GROUP BY enroll_month",
                    "ORDER BY enroll_month;"])
scene("ex-top", ["SELECT course_id, COUNT(*) AS 신청수",
                 "FROM enrollments",
                 "WHERE status <> '취소'",
                 "GROUP BY course_id",
                 "ORDER BY 신청수 DESC",
                 "LIMIT 3;",
                 "SELECT course_id, course_name, fee FROM courses",
                 "WHERE course_id IN (2, 5, 8);"])
scene("ex-vip", ["SELECT",
                 "    member_id,",
                 "    COUNT(*)        AS 신청수,",
                 "    SUM(pay_amount) AS 누적결제",
                 "FROM enrollments",
                 "WHERE status <> '취소'",
                 "GROUP BY member_id",
                 "HAVING SUM(pay_amount) >= 600000",
                 "ORDER BY 누적결제 DESC, member_id;"])
scene("ex-sport", ["SELECT",
                   "    sport_id,",
                   "    COUNT(*)      AS 강좌수,",
                   "    MIN(fee)      AS 최저,",
                   "    MAX(fee)      AS 최고,",
                   "    SUM(capacity) AS 정원",
                   "FROM courses",
                   "GROUP BY sport_id",
                   "ORDER BY sport_id;",
                   "SELECT * FROM sports;"])

with open(OUTF, "w") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=1)
print("saved", len(OUT), "scenes")
