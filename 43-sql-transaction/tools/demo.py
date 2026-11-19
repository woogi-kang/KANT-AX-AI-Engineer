"""Runs every psql session of the SQL 8 deck (43, transactions) for real and saves what the student would see in tools/out.json.
    sudo -n dockerd &        (once, in the cloud container)
    uv run --with pyte python tools/demo.py              (all scenes)
    uv run --with pyte python tools/demo.py rb-many      (only these scenes, merged into out.json)
Real Docker and the official postgres:18 image, with the names of 35: container my-pg, password admin1234, database
kant_shop. The tables are the class example (a sports center) in tools/sports.sql, shared by the SQL 3-8 decks.
Each scene starts from a fresh kant_shop with sports.sql loaded. psql runs in a pseudo-terminal and the statements
are typed line by line after the prompt shows. Two-window scenes (duo.py) open two psql sessions at once."""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ptyrun, duo  # noqa: E402

HOME = "/home/kim"
ENV = {"HOME": HOME, "NO_COLOR": "1"}
OUTF = os.path.join(HERE, "out.json")
ONLY = set(sys.argv[1:])
OUT = json.load(open(OUTF)) if ONLY and os.path.exists(OUTF) else {}
PROMPT = rb"(=# |-# |'# |\(# |=> |\$ |# |\*# |!# )$"
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


def scene(name, inputs, seed=True, keep=False):
    """keep=True: do not reset the data first (the scene continues the one before)"""
    if ONLY and name not in ONLY:
        return
    if not keep:
        fresh(seed)
    lines = ptyrun.run(PSQL, HOME, inputs=list(inputs) + ["\\q"], env=ENV, prompt=PROMPT, cols=160)
    OUT[name] = [{"cmd": PSQL, "cwd": "~", "out": lines}]
    print(f"== {name}")
    print("\n".join(lines))


def two(name, steps):
    if ONLY and name not in ONLY:
        return
    fresh()
    snaps = duo.run(PSQL, HOME, steps, PROMPT.decode(), env=ENV, cols=110)
    OUT[name] = [{"cmd": PSQL, "cwd": "~", "snaps": snaps}]
    for k, v in snaps.items():
        for w in ("A", "B"):
            print(f"== {name} [{k}] window {w}")
            print("\n".join(v[w]))


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

# ---------- intro ----------
scene("why", ["UPDATE courses SET fee = 0;",
              "ROLLBACK;",
              "SELECT course_name, fee FROM courses ORDER BY course_id LIMIT 4;"])
scene("min", ["BEGIN;",
              "UPDATE courses SET fee = 0;",
              "SELECT course_name, fee FROM courses ORDER BY course_id LIMIT 3;",
              "ROLLBACK;",
              "SELECT course_name, fee FROM courses ORDER BY course_id LIMIT 3;"])

# ---------- part 1: BEGIN, COMMIT, ROLLBACK ----------
scene("auto", ["UPDATE courses SET fee = 65000 WHERE course_id = 5;",
               "SELECT course_name, fee FROM courses WHERE course_id = 5;"])
scene("begin", ["BEGIN;",
                "UPDATE courses SET fee = 65000 WHERE course_id = 5;",
                "SELECT course_name, fee FROM courses WHERE course_id = 5;",
                "COMMIT;",
                "SELECT course_name, fee FROM courses WHERE course_id = 5;"])
scene("commit-late", ["BEGIN;",
                      "UPDATE courses SET fee = 65000 WHERE course_id = 5;",
                      "COMMIT;",
                      "ROLLBACK;",
                      "SELECT course_name, fee FROM courses WHERE course_id = 5;"])
scene("rb-many", ["BEGIN;",
                  "UPDATE courses SET capacity = 30 WHERE course_id = 5;",
                  "DELETE FROM enrollments WHERE enroll_month = '2026-09';",
                  "ROLLBACK;",
                  "SELECT capacity FROM courses WHERE course_id = 5;",
                  "SELECT COUNT(*) FROM enrollments WHERE enroll_month = '2026-09';"])
scene("rb-trap", ["UPDATE courses",
                  "SET capacity = capacity + 5",
                  "WHERE course_id IN (SELECT course_id",
                  "                    FROM enrollments",
                  "                    WHERE enroll_month = '2026-11'",
                  "                    GROUP BY course_id",
                  "                    HAVING COUNT(*) >= 5)",
                  "RETURNING course_id, capacity;",
                  "ROLLBACK;",
                  "SELECT capacity FROM courses WHERE course_id = 5;"])
scene("begin2", ["BEGIN;",
                 "BEGIN;",
                 "ROLLBACK;",
                 "ROLLBACK;"])

# ---------- part 2: another window ----------
two("w-see", [("A", "BEGIN;"),
              ("A", "UPDATE courses SET fee = 65000 WHERE course_id = 5;"),
              ("A", "SELECT fee FROM courses WHERE course_id = 5;"),
              ("B", "SELECT fee FROM courses WHERE course_id = 5;"),
              ("snap", "before"),
              ("A", "COMMIT;"),
              ("B", "SELECT fee FROM courses WHERE course_id = 5;")])
two("w-wait", [("A", "BEGIN;"),
               ("A", "UPDATE courses SET capacity = capacity + 5 WHERE course_id = 5;"),
               ("B", "UPDATE courses SET capacity = capacity + 1 WHERE course_id = 5;"),
               ("snap", "waiting"),
               ("A", "COMMIT;"),
               ("snap", "released"),
               ("B", "SELECT capacity FROM courses WHERE course_id = 5;")])
two("w-quit", [("A", "BEGIN;"),
               ("A", "UPDATE courses SET fee = 65000 WHERE course_id = 5;"),
               ("A", "\\q"),
               ("B", "SELECT fee FROM courses WHERE course_id = 5;")])

# ---------- part 3: all or nothing ----------
scene("move-ok", ["SELECT * FROM enrollments WHERE enrollment_id = 184;",
                  "BEGIN;",
                  "UPDATE enrollments SET status = '취소', pay_amount = 0 WHERE enrollment_id = 184;",
                  "INSERT INTO enrollments VALUES (188, 11, 9, '2026-11', '신청', 75000);",
                  "COMMIT;",
                  "SELECT * FROM enrollments WHERE member_id = 11 AND course_id IN (9, 13) AND enroll_month = '2026-11';"])
scene("move-err", ["BEGIN;",
                   "UPDATE enrollments SET status = '취소', pay_amount = 0 WHERE enrollment_id = 184;",
                   "INSERT INTO enrollments VALUES (187, 11, 9, '2026-11', '신청', 75000);",
                   "SELECT * FROM enrollments WHERE enrollment_id = 184;",
                   "ROLLBACK;",
                   "SELECT * FROM enrollments WHERE enrollment_id = 184;"])
scene("move-commit", ["BEGIN;",
                      "UPDATE enrollments SET status = '취소', pay_amount = 0 WHERE enrollment_id = 184;",
                      "INSERT INTO enrollments VALUES (187, 11, 9, '2026-11', '신청', 75000);",
                      "COMMIT;",
                      "SELECT enrollment_id, status, pay_amount FROM enrollments WHERE enrollment_id = 184;"])
scene("ddl", ["BEGIN;",
              "DROP TABLE enrollments;",
              "SELECT COUNT(*) FROM enrollments;",
              "ROLLBACK;",
              "SELECT COUNT(*) FROM enrollments;",
              "BEGIN;",
              "TRUNCATE enrollments;",
              "ROLLBACK;",
              "SELECT COUNT(*) FROM enrollments;"])

# ---------- part 4: delete safely ----------
scene("safe-del", ["SELECT COUNT(*) FROM enrollments WHERE enroll_month = '2026-11' AND status = '취소';",
                   "BEGIN;",
                   "DELETE FROM enrollments",
                   "WHERE enroll_month = '2026-11' AND status = '취소'",
                   "RETURNING enrollment_id, member_id, course_id;",
                   "COMMIT;"])
scene("oops-del", ["SELECT COUNT(*) FROM enrollments WHERE enroll_month = '2026-11' AND status = '취소';",
                   "BEGIN;",
                   "DELETE FROM enrollments WHERE enroll_month = '2026-11' OR status = '취소';",
                   "ROLLBACK;",
                   "SELECT COUNT(*) FROM enrollments;"])

# ---------- real cases ----------
scene("r-fee", ["BEGIN;",
                "UPDATE courses SET fee = fee * 1.05 WHERE sport_id = 3",
                "RETURNING course_name, fee;",
                "ROLLBACK;",
                "SELECT course_name, fee FROM courses WHERE sport_id = 3;"])
scene("r-cap", ["BEGIN;",
                "UPDATE courses",
                "SET capacity = capacity + 5",
                "WHERE course_id IN (SELECT course_id",
                "                    FROM enrollments",
                "                    WHERE enroll_month = '2026-11'",
                "                    GROUP BY course_id",
                "                    HAVING COUNT(*) >= 5)",
                "RETURNING course_id, capacity;",
                "COMMIT;"])

scene("r-quit", ["BEGIN;",
                 "DELETE FROM members WHERE member_id = 10;",
                 "ROLLBACK;",
                 "BEGIN;",
                 "DELETE FROM enrollments WHERE member_id = 10 RETURNING enrollment_id;",
                 "DELETE FROM members WHERE member_id = 10 RETURNING name;",
                 "COMMIT;"])

json.dump(OUT, open(OUTF, "w"), ensure_ascii=False, indent=1)
print("saved", len(OUT), "scenes")
