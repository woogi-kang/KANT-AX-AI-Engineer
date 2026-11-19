"""Runs every program and psql session of the 44 deck (Python and PostgreSQL with psycopg) for real and saves what
the student would see in tools/out.json.
    sudo -n dockerd &        (once, in the cloud container)
    uv run --with pyte python tools/demo.py              (all scenes)
    uv run --with pyte python tools/demo.py enroll       (only these scenes, merged into out.json)
Real Docker and the official postgres:18 image with the names of 35 (container my-pg, password admin1234, port 5432,
database kant_shop) and the class data of 38-41 (sports.sql). The Python programs in tools/src are copied to
~/sports-app/main.py one by one and run with `uv run main.py`, after `uv init sports-app` and `uv add "psycopg[binary]"`.
Each scene starts from a fresh kant_shop with sports.sql loaded. The "no pq wrapper" scene runs in a clean
python:3.13-slim container (no libpq) with the same uv binary, so the error is the one a computer without libpq shows."""
import json, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ptyrun  # noqa: E402

HOME = "/home/kim"
APP = os.path.join(HOME, "sports-app")
ENV = {"HOME": HOME, "NO_COLOR": "1", "PYTHONUNBUFFERED": "1", "UV_NO_PROGRESS": "1"}
OUTF = os.path.join(HERE, "out.json")
ONLY = set(sys.argv[1:])
OUT = json.load(open(OUTF)) if ONLY and os.path.exists(OUTF) else {}
PROMPT = rb"(=# |-# |'# |\(# |=> |\$ |# )$"
RUN = "docker run -d --name my-pg -e POSTGRES_PASSWORD=admin1234 -p 5432:5432 postgres:18"
PSQL = "docker exec -it my-pg psql -U postgres -d kant_shop"
SEED = os.path.join(os.path.dirname(HERE), "sports.sql")
SRC = os.path.join(HERE, "src")


def sh(cmd, stdin=None, cwd=HOME):
    env = {k: v for k, v in os.environ.items() if k not in ("UV_NATIVE_TLS", "VIRTUAL_ENV")}
    return subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, input=stdin, env={**env, **ENV})


def fresh(seed=True):
    sh('docker exec my-pg psql -U postgres -c "DROP DATABASE IF EXISTS kant_shop WITH (FORCE)" -c "CREATE DATABASE kant_shop"')
    if seed:
        r = sh("docker exec -i my-pg psql -q -U postgres -d kant_shop -v ON_ERROR_STOP=1", open(SEED).read())
        if r.returncode:
            raise SystemExit(r.stderr)


def want(name):
    return not ONLY or name in ONLY


def save(name, cmd, cwd, lines, append=False):
    entry = {"cmd": cmd, "cwd": cwd, "out": lines}
    if append:
        OUT[name].append(entry)
    else:
        OUT[name] = [entry]
    print(f"== {name}: {cmd}")
    print("\n".join(lines))


def shell(name, cmd, cwd=APP, append=False, show="~/sports-app"):
    r = sh(cmd + " 2>&1", cwd=cwd)
    lines = r.stdout.rstrip("\n").split("\n") if r.stdout.strip() else []
    save(name, cmd, show, lines, append)


def prog(name, src, append=False, seed=True, reset=True):
    """copy tools/src/<src>.py to ~/sports-app/main.py and run it the way the student does"""
    if reset:
        fresh(seed)
    shutil.copy(os.path.join(SRC, src + ".py"), os.path.join(APP, "main.py"))
    shell(name, "uv run main.py", append=append)


def psql(name, inputs, append=True):
    lines = ptyrun.run(PSQL, HOME, inputs=list(inputs) + ["\\q"], env=ENV, prompt=PROMPT, cols=160)
    lines = [l for l in lines if not l.startswith("psql (18") and not l.startswith('Type "help"')]
    while lines and not lines[0].strip():
        lines = lines[1:]
    if lines and lines[-1].endswith("\\q"):
        lines = lines[:-1]
    while lines and not lines[-1].strip():
        lines = lines[:-1]
    entry = {"cmd": PSQL, "cwd": "~", "out": lines}
    if append and name in OUT:
        OUT[name].append(entry)
    else:
        OUT[name] = [entry]
    print(f"== {name} (psql)")
    print("\n".join(lines))


# ---------- the database ----------
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
fresh()

# ---------- the project ----------
# a project without psycopg first: the ModuleNotFoundError scene
shutil.rmtree(APP, ignore_errors=True)
sh("uv init -q sports-app", cwd=HOME)
if want("e-nomod"):
    prog("e-nomod", "e_nomod")
# then the real setup, from an empty folder and an empty uv cache, the way a first install looks
shutil.rmtree(APP, ignore_errors=True)
CACHE = "/tmp/uv-cache-44"
shutil.rmtree(CACHE, ignore_errors=True)
r = sh("uv init sports-app 2>&1", cwd=HOME)
if want("setup"):
    save("setup", "uv init sports-app", "~", r.stdout.rstrip("\n").split("\n"))
    shell("setup", "cd sports-app", cwd=HOME, append=True, show="~")
r = sh(f'UV_CACHE_DIR={CACHE} uv add "psycopg[binary]" 2>&1', cwd=APP)
if want("setup"):
    save("setup", 'uv add "psycopg[binary]"', "~/sports-app", r.stdout.rstrip("\n").split("\n"), append=True)
    OUT["pyproject"] = [{"cmd": "", "cwd": "", "out": open(os.path.join(APP, "pyproject.toml")).read().rstrip("\n").split("\n")}]
OUT["pyver"] = [{"cmd": "", "cwd": "", "out": [sh("uv run python --version", cwd=APP).stdout.strip(),
                                               sh("uv run python -c \"import psycopg; print(psycopg.__version__)\"", cwd=APP).stdout.strip()]}]

# ---------- programs ----------
for name, src in [("hello", "hello"), ("fetchall", "fetchall"), ("fetchone", "fetchone"), ("dictrow", "dictrow"),
                  ("list", "list"), ("param", "param"), ("param2", "param2"), ("inject-bad", "inject_bad"),
                  ("inject-ok", "inject_ok"), ("seats", "seats"),
                  ("e-port", "e_port"), ("e-pw", "e_pw"), ("e-fetch", "e_fetch"), ("e-tuple", "e_tuple"),
                  ("e-tuple-ok", "e_tuple_ok"), ("e-quote", "e_quote"), ("e-col", "e_col"), ("e-closed", "e_closed"), ("receipt", "receipt")]:
    if want(name):
        prog(name, src)

if want("enroll"):
    fresh()
    psql("enroll", ["SELECT COUNT(*) FROM enrollments;"], append=False)
    prog("enroll", "enroll", append=True, reset=False)
    psql("enroll", ["SELECT * FROM enrollments ORDER BY enrollment_id DESC LIMIT 2;"])

if want("rollback"):
    fresh()
    prog("rollback", "rollback", reset=False)
    psql("rollback", ["SELECT COUNT(*) FROM enrollments;"])

if want("dup"):
    fresh()
    prog("dup", "dup", reset=False)
    psql("dup", ["SELECT enrollment_id, member_id, course_id FROM enrollments ORDER BY enrollment_id DESC LIMIT 2;"])

if want("nocommit"):
    fresh()
    prog("nocommit", "nocommit", reset=False)
    psql("nocommit", ["SELECT member_id, name, phone FROM members WHERE member_id = 10;"])
    prog("nocommit", "commit", append=True, reset=False)
    psql("nocommit", ["SELECT member_id, name, phone FROM members WHERE member_id = 10;"])

if want("e-stopped"):
    fresh()
    sh("docker stop my-pg")
    shutil.copy(os.path.join(SRC, "hello.py"), os.path.join(APP, "main.py"))
    shell("e-stopped", "uv run main.py")
    sh("docker start my-pg")
    subprocess.run("sleep 3", shell=True)

# psql runs every statement on its own: the same UPDATE saves at once
if want("why"):
    fresh()
    psql("why", ["SELECT course_id, course_name, fee FROM courses LIMIT 3;"], append=False)

if want("psql-auto"):
    fresh()
    psql("psql-auto", ["UPDATE members SET phone = '010-1111-2222' WHERE member_id = 10;"], append=False)
    psql("psql-auto", ["SELECT member_id, name, phone FROM members WHERE member_id = 10;"])

# ---------- no libpq: psycopg without [binary] in a clean Linux container ----------
if want("e-nopq"):
    px = os.environ.get("HTTPS_PROXY", "")
    inner = ("mkdir -p /home/kim && cd /home/kim && uv init -q sports-app && cd sports-app && uv add -q psycopg && "
             "printf 'import psycopg\\n' > main.py && echo '__RUN__' && uv run main.py")
    r = sh(f"docker run --rm --network host -e HTTPS_PROXY='{px}' -e SSL_CERT_FILE=/ca.crt -v /root/.ccr/ca-bundle.crt:/ca.crt "
           f"-v $(command -v uv):/usr/local/bin/uv -e UV_NO_PROGRESS=1 python:3.13-slim bash -c \"{inner}\" 2>&1")
    lines = r.stdout.split("__RUN__\n", 1)[-1].rstrip("\n").split("\n")
    lines = [l for l in lines if "UV_NATIVE_TLS" not in l]
    save("e-nopq", "uv run main.py", "~/sports-app", lines)

json.dump(OUT, open(OUTF, "w"), ensure_ascii=False, indent=1)
print("saved", OUTF)
