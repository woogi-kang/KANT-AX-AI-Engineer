"""Runs every SQL of the SQL 5 deck (40, UNION and JOIN) for real and saves what the student would see in tools/out.json.
    sudo -n dockerd &        (once, in the cloud container)
    uv run --with pyte python tools/demo.py
Real Docker and the official postgres:18 image, with the class names of 35: container my-pg, password admin1234,
database kant_shop. The tables are the class sports center (sports, instructors, courses, members, enrollments) from
../sports.sql, the same file 38 to 41 use. psql runs in a pseudo-terminal of 160 columns and every SQL line is typed
after the prompt shows, so the screen is what a student sees. Nothing here changes a row, so the scenes share one load."""
import json, os, shutil, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ptyrun  # noqa: E402

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


def L(s):
    """a statement typed line by line"""
    return [l for l in s.strip("\n").split("\n")]


def ready():
    for _ in range(240):
        log = sh("docker logs my-pg 2>&1").stdout
        if "init process complete" in log and "ready to accept connections" in log.split("PostgreSQL init process complete")[-1]:
            time.sleep(1)
            return
        time.sleep(0.5)
    raise SystemExit("my-pg never got ready")


ONLY = set(sys.argv[1:])
if ONLY:
    OUT = json.load(open(os.path.join(HERE, "out.json")))
    for k in ONLY:
        OUT.pop(k, None)
    _rec = rec

    def rec(scene, cmd, inputs=(), tty=False):  # noqa: F811
        if scene in ONLY:
            return _rec(scene, cmd, inputs, tty)
else:
    os.makedirs(HOME, exist_ok=True)
    sh("docker rm -f $(docker ps -aq) 2>/dev/null")
    sh("docker volume rm $(docker volume ls -q) 2>/dev/null")
    os.makedirs(HOME, exist_ok=True)
    shutil.copy(os.path.join(HERE, "..", "sports.sql"), os.path.join(HOME, "sports.sql"))
    sh(RUN)
    ready()
    sh(PSQL.replace("-it ", "") + ' -c "CREATE DATABASE kant_shop"')

# ---------- setup: load the class tables ----------
rec("cp", "docker cp sports.sql my-pg:/tmp/")
rec("load", PSQL + " -d kant_shop -f /tmp/sports.sql", tty=True)
rec("dt", KS, ["\\dt"])

# ---------- intro ----------
rec("why", KS, L("""
SELECT * FROM enrollments
WHERE course_id = 6 AND enroll_month = '2026-11';
SELECT member_id, name FROM members
WHERE member_id IN (3, 24, 14, 30);
"""))
rec("min", KS, L("""
SELECT name FROM instructors WHERE instructor_id = 5
UNION ALL
SELECT name FROM members WHERE member_id = 1;
SELECT c.course_name, i.name
FROM courses c
JOIN instructors i ON c.instructor_id = i.instructor_id
WHERE c.course_id = 10;
"""))

# ---------- part 1: UNION ----------
rec("u-sep", KS, L("""
SELECT member_id FROM enrollments WHERE course_id = 4 AND enroll_month = '2026-09';
SELECT member_id FROM enrollments WHERE course_id = 4 AND enroll_month = '2026-10';
"""))
rec("u-all", KS, L("""
SELECT member_id
FROM enrollments
WHERE course_id = 4 AND enroll_month = '2026-09'
UNION ALL
SELECT member_id
FROM enrollments
WHERE course_id = 4 AND enroll_month = '2026-10';
"""))
for name, op in (("u-all3", "UNION ALL"), ("u-union", "UNION")):
    rec(name, KS, L(f"""
SELECT member_id
FROM enrollments
WHERE course_id = 4 AND enroll_month = '2026-09'
{op}
SELECT member_id
FROM enrollments
WHERE course_id = 4 AND enroll_month = '2026-10'
{op}
SELECT member_id
FROM enrollments
WHERE course_id = 4 AND enroll_month = '2026-11'
ORDER BY member_id;
"""))
rec("u-label", KS, L("""
SELECT '강사' AS 구분, name, phone
FROM instructors
WHERE sport_id = 4
UNION ALL
SELECT '회원' AS 구분, name, phone
FROM members
WHERE region = '영등포구';
"""))
rec("u-rule", KS, L("""
SELECT name, phone FROM instructors
UNION ALL
SELECT name FROM members;
SELECT name FROM instructors
UNION ALL
SELECT birth_year FROM members;
SELECT name AS 이름 FROM instructors WHERE sport_id = 4
UNION ALL
SELECT course_name FROM courses WHERE sport_id = 4;
"""))
rec("u-order", KS, L("""
SELECT name FROM instructors WHERE sport_id = 4
ORDER BY name
UNION ALL
SELECT name FROM members WHERE member_id = 1;
SELECT name FROM instructors WHERE sport_id = 4
UNION ALL
SELECT name FROM members WHERE member_id = 1
ORDER BY name;
"""))

# ---------- part 2: alias and JOIN ----------
rec("j-long", KS, L("""
SELECT enrollments.member_id, enrollments.course_id, members.name
FROM enrollments
JOIN members ON enrollments.member_id = members.member_id
WHERE enrollments.course_id = 6 AND enrollments.enroll_month = '2026-11';
"""))
rec("j-basic", KS, L("""
SELECT e.member_id, e.course_id, m.name
FROM enrollments e
JOIN members m ON e.member_id = m.member_id
WHERE e.course_id = 6 AND e.enroll_month = '2026-11';
"""))
rec("j-many", KS, L("""
SELECT m.name, e.course_id, e.enroll_month, e.status
FROM members m
JOIN enrollments e ON m.member_id = e.member_id
WHERE m.member_id = 11
ORDER BY e.enroll_month, e.course_id;
"""))
rec("j-inner", KS, L("""
SELECT c.course_id, c.course_name, i.name
FROM courses c
JOIN instructors i ON c.instructor_id = i.instructor_id
ORDER BY c.course_id;
"""))
rec("j-3", KS, L("""
SELECT m.name, c.course_name, e.enroll_month, e.status
FROM enrollments e
JOIN members m ON e.member_id = m.member_id
JOIN courses c ON e.course_id = c.course_id
WHERE e.member_id = 11
ORDER BY e.enroll_month, e.course_id;
"""))

# ---------- part 3: LEFT JOIN, FULL JOIN ----------
rec("l-left", KS, L("""
SELECT c.course_id, c.course_name, i.name
FROM courses c
LEFT JOIN instructors i ON c.instructor_id = i.instructor_id
ORDER BY c.course_id;
"""))
rec("l-swap", KS, L("""
SELECT i.instructor_id, i.name, c.course_name
FROM instructors i
LEFT JOIN courses c ON i.instructor_id = c.instructor_id
ORDER BY i.instructor_id, c.course_id;
"""))
rec("f-full", KS, L("""
SELECT c.course_id, c.course_name, i.name
FROM courses c
FULL JOIN instructors i ON c.instructor_id = i.instructor_id
ORDER BY c.course_id;
"""))
rec("l-count", KS, L("""
SELECT COUNT(*) FROM courses c JOIN instructors i ON c.instructor_id = i.instructor_id;
SELECT COUNT(*) FROM courses c LEFT JOIN instructors i ON c.instructor_id = i.instructor_id;
SELECT COUNT(*) FROM courses c FULL JOIN instructors i ON c.instructor_id = i.instructor_id;
"""))

# ---------- part 5: errors and traps ----------
rec("x-amb", KS, L("""
SELECT member_id, name
FROM enrollments e
JOIN members m ON e.member_id = m.member_id
WHERE e.course_id = 6 AND e.enroll_month = '2026-11';
"""))
rec("x-alias", KS, L("""
SELECT members.name FROM members m WHERE m.member_id = 1;
SELECT * FROM courses c JOIN instructors i;
"""))
rec("x-on", KS, L("""
SELECT e.member_id, m.name, c.course_name
FROM enrollments e
LEFT JOIN members m ON e.member_id = m.member_id
LEFT JOIN courses c ON e.member_id = c.course_id
WHERE e.course_id = 1 AND e.enroll_month = '2026-11'
ORDER BY m.name;
"""))
rec("x-nocol", KS, L("""
SELECT FROM members m
FULL OUTER JOIN enrollments e
    ON m.member_id = e.member_id
LIMIT 3;
SELECT m.member_id, m.name, e.course_id
FROM members m
FULL OUTER JOIN enrollments e
    ON m.member_id = e.member_id
ORDER BY m.member_id DESC
LIMIT 3;
"""))
rec("x-where", KS, L("""
SELECT c.course_name, i.name
FROM courses c
LEFT JOIN instructors i ON c.instructor_id = i.instructor_id
WHERE i.name <> '박서연' AND c.sport_id = 1;
SELECT c.course_name, i.name
FROM courses c
LEFT JOIN instructors i ON c.instructor_id = i.instructor_id
WHERE c.sport_id = 1;
"""))

# ---------- part 6: real situations ----------
rec("e-roster", KS, L("""
SELECT
    e.member_id, m.name, c.course_name, e.enroll_month, e.status
FROM enrollments e
LEFT JOIN members m ON e.member_id = m.member_id
LEFT JOIN courses c ON e.course_id = c.course_id
WHERE e.course_id = 1 AND e.enroll_month = '2026-11'
ORDER BY m.name;
"""))
rec("e-never", KS, L("""
SELECT m.member_id, m.name, m.phone
FROM members m
LEFT JOIN enrollments e ON m.member_id = e.member_id
WHERE e.enrollment_id IS NULL;
"""))
rec("e-contact", KS, L("""
SELECT '강사' AS 구분, i.name, i.phone
FROM courses c
JOIN instructors i ON c.instructor_id = i.instructor_id
WHERE c.course_id = 4
UNION ALL
SELECT '회원' AS 구분, m.name, m.phone
FROM enrollments e
JOIN members m ON e.member_id = m.member_id
WHERE e.course_id = 4 AND e.enroll_month = '2026-11'
  AND e.status <> '취소';
"""))
rec("e-check", KS, L("""
SELECT '강사 없는 강좌' AS 구분, c.course_name AS 이름
FROM courses c
LEFT JOIN instructors i ON c.instructor_id = i.instructor_id
WHERE i.instructor_id IS NULL
UNION ALL
SELECT '강좌 없는 강사', i.name
FROM instructors i
LEFT JOIN courses c ON i.instructor_id = c.instructor_id
WHERE c.course_id IS NULL;
"""))

OUT["version"] = [{"cmd": "", "cwd": "~", "out": [sh(PSQL.replace("-it ", "") + ' -tAc "SELECT version()"').stdout.strip()]}]
with open(os.path.join(HERE, "out.json"), "w") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=1)
print("scenes:", len(OUT))
