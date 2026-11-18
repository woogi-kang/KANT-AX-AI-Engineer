"""Runs every SQL of the SQL 3 deck (38) for real and saves what the student would see in tools/out.json.
    sudo -n dockerd &        (once, in the cloud container)
    uv run --with pyte python tools/demo.py
Real Docker and the official postgres:18 image, with the class names of 35: container my-pg, password admin1234,
database kant_shop. The tables come from ../sports.sql (sports, instructors, courses, members, enrollments), the
example database 38 to 41 share. psql runs in a pseudo-terminal of 160 columns and every SQL line is typed after the
prompt shows, so the screen is what a student sees."""
import json, os, shutil, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ptyrun  # noqa: E402

HOME = "/home/kim"
ENV = {"HOME": HOME, "NO_COLOR": "1"}
OUT = {}
PROMPT = rb"(=# |-# |'# |\(# |=> |: |\$ |# )$"
RUN = "docker run -d --name my-pg -e POSTGRES_PASSWORD=admin1234 -p 5432:5432 -v pgdata:/var/lib/postgresql postgres:18"
KS = "docker exec -it my-pg psql -U postgres -d kant_shop"


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


os.makedirs(HOME, exist_ok=True)
sh("docker rm -f $(docker ps -aq) 2>/dev/null")
sh("docker volume rm $(docker volume ls -q) 2>/dev/null")
shutil.copy(os.path.join(HERE, "..", "sports.sql"), os.path.join(HOME, "sports.sql"))

# my-pg and kant_shop exist since 35 and 36
sh(RUN)
ready()
sh("docker exec my-pg psql -U postgres -c 'CREATE DATABASE kant_shop;'")

# ---------- setup: load the class tables ----------
rec("load", "docker cp sports.sql my-pg:/tmp/", tty=True)
rec("load", KS + " -f /tmp/sports.sql", tty=True)
rec("tables", KS, ["\\dt", "SELECT course_id, course_name, sport_id, level, start_time, fee FROM courses;"])

# ---------- part 1: AND, OR, parentheses, NOT ----------
rec("noparen", KS, ["SELECT course_name, level, start_time",
                    "FROM courses",
                    "WHERE sport_id = 1 AND level = '초급' OR start_time < '09:00';"])
rec("paren-or", KS, ["SELECT course_name, level, start_time",
                     "FROM courses",
                     "WHERE sport_id = 1",
                     "AND (level = '초급' OR start_time < '09:00');"])
rec("paren-and", KS, ["SELECT course_name, level, start_time",
                      "FROM courses",
                      "WHERE sport_id = 1",
                      "AND (level = '초급' AND start_time < '09:00');"])
rec("truth", KS, ["SELECT course_name, level = '초급' AS 초급, start_time < '09:00' AS 아침 FROM courses WHERE sport_id = 1;"])
rec("not", KS, ["SELECT course_name, level FROM courses WHERE level NOT IN ('초급', '중급');",
                "SELECT course_name FROM courses WHERE sport_id = 1 AND course_name NOT LIKE '%초급%';",
                "SELECT course_name FROM courses WHERE sport_id = 1 AND NOT (level = '초급' OR start_time < '09:00');"])

# ---------- part 2: CASE ----------
rec("case2", KS, ["SELECT course_name, fee,",
                  "       CASE WHEN fee >= 100000 THEN '고가' ELSE '일반' END AS 가격대",
                  "FROM courses",
                  "WHERE sport_id IN (2, 4);"])
rec("case3", KS, ["SELECT name, birth_year,",
                  "       CASE WHEN birth_year <= 1960 THEN '할인'",
                  "            WHEN birth_year >= 2000 THEN '청소년'",
                  "            ELSE '일반'",
                  "       END AS 요금",
                  "FROM members",
                  "WHERE region = '마포구'",
                  "ORDER BY birth_year, name;"])
rec("case-wrong", KS, ["SELECT name, birth_year,",
                       "       CASE WHEN birth_year < 2000 THEN '일반'",
                       "            WHEN birth_year <= 1960 THEN '할인'",
                       "            ELSE '청소년'",
                       "       END AS 요금",
                       "FROM members",
                       "WHERE region = '마포구'",
                       "ORDER BY birth_year, name;"])
rec("case-noelse", KS, ["SELECT name, birth_year,",
                        "       CASE WHEN birth_year <= 1960 THEN '할인'",
                        "            WHEN birth_year >= 2000 THEN '청소년'",
                        "       END AS 요금",
                        "FROM members",
                        "WHERE region = '마포구'",
                        "ORDER BY birth_year, name;"])
rec("case-null", KS, ["SELECT name, email, phone,",
                      "       CASE WHEN email IS NOT NULL THEN '이메일'",
                      "            WHEN phone IS NOT NULL THEN '문자'",
                      "            ELSE '연락처 없음'",
                      "       END AS 연락",
                      "FROM members",
                      "WHERE region = '마포구';"])
rec("case-calc", KS, ["SELECT course_name, start_time, fee,",
                      "       CASE WHEN start_time < '09:00' THEN fee - 10000 ELSE fee END AS 이번달",
                      "FROM courses",
                      "WHERE sport_id IN (1, 3)",
                      "ORDER BY 이번달 DESC;"])

# ---------- part 3: ORDER BY ----------
rec("sort-two", KS, ["SELECT course_name, fee FROM courses WHERE sport_id = 1 ORDER BY fee DESC, course_name;",
                     "SELECT course_name, fee FROM courses WHERE sport_id = 1 ORDER BY fee DESC, course_name DESC;"])
rec("sort-dir", KS, ["SELECT course_name, level, fee FROM courses WHERE sport_id = 1 ORDER BY level, fee DESC;"])
rec("sort-level", KS, ["SELECT course_name, level, fee FROM courses WHERE sport_id IN (1, 4) ORDER BY level, fee;",
                       "SELECT course_name, level, fee FROM courses WHERE sport_id IN (1, 4)",
                       "ORDER BY CASE WHEN level = '초급' THEN 1 WHEN level = '중급' THEN 2 ELSE 3 END, fee, course_name;"])
rec("null-sort", KS, ["SELECT name, email FROM members WHERE region = '구로구' ORDER BY email;",
                      "SELECT name, email FROM members WHERE region = '구로구' ORDER BY email DESC, name;"])
rec("nulls-last", KS, ["SELECT name, email FROM members WHERE region = '구로구' ORDER BY email DESC NULLS LAST, name;",
                       "SELECT name, email FROM members WHERE region = '구로구' ORDER BY email NULLS FIRST, name;"])

# ---------- part 4: errors ----------
rec("x-end", KS, ["SELECT name,",
                  "       CASE WHEN birth_year <= 1960 THEN '할인' ELSE '일반' AS 요금",
                  "FROM members;"])
rec("x-type", KS, ["SELECT course_name,",
                   "       CASE WHEN fee >= 100000 THEN '고가' ELSE 0 END AS 가격대",
                   "FROM courses;",
                   "SELECT course_name,",
                   "       CASE WHEN fee >= 100000 THEN '고가' ELSE '-' END AS 가격대",
                   "FROM courses WHERE sport_id = 2;"])
rec("x-alias", KS, ["SELECT name, CASE WHEN birth_year <= 1960 THEN '할인' ELSE '일반' END AS 요금",
                    "FROM members WHERE 요금 = '할인';",
                    "SELECT name, birth_year FROM members WHERE birth_year <= 1960 ORDER BY birth_year;"])
rec("x-collate", KS, ["SELECT course_name, fee FROM courses WHERE fee >= 80000 ORDER BY fee DESC, course_name;",
                      "SELECT course_name, fee FROM courses WHERE fee >= 80000 ORDER BY fee DESC, course_name COLLATE \"C\";"])

# ---------- part 5: real situations ----------
rec("e-fee", KS, ["SELECT name, birth_year,",
                  "       CASE WHEN birth_year <= 1960 THEN '할인'",
                  "            WHEN birth_year >= 2000 THEN '청소년'",
                  "            ELSE '일반'",
                  "       END AS 요금",
                  "FROM members",
                  "WHERE region = '영등포구'",
                  "ORDER BY birth_year, name;"])
rec("e-time", KS, ["SELECT course_name, start_time,",
                   "       CASE WHEN start_time < '07:00' THEN '새벽'",
                   "            WHEN start_time < '12:00' THEN '오전'",
                   "            WHEN start_time < '18:00' THEN '오후'",
                   "            ELSE '저녁'",
                   "       END AS 시간대",
                   "FROM courses",
                   "ORDER BY start_time;"])
rec("e-sms", KS, ["SELECT name, birth_year, phone,",
                  "       CASE WHEN birth_year <= 1960 THEN '할인' ELSE '청소년' END AS 안내",
                  "FROM members",
                  "WHERE (birth_year <= 1960 OR birth_year >= 2000)",
                  "  AND phone IS NOT NULL",
                  "ORDER BY birth_year DESC, name;"])

with open(os.path.join(HERE, "out.json"), "w") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=1)
print("saved", len(OUT), "scenes")
