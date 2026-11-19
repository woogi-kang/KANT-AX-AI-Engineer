# 44 · 파이썬에서 PostgreSQL 쓰기 (psycopg)

> 지금까지 psql 창에 직접 치던 SQL을 파이썬 프로그램이 보내게 해요. psycopg로 `my-pg`의 `kant_shop`에 접속해서 강좌 목록을 받아 찍고, 수강 신청을 한 줄 넣어요. 9의 uv, 13~25의 파이썬, 35의 컨테이너, 38부터 쓰는 스포츠 센터 데이터를 이어서 써요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/44-python-postgres/python-postgres-slides.html) | [43 · SQL 8 (트랜잭션)](../43-sql-transaction) | 준비 중 |

<!-- /curriculum:top -->

## 학습 목표

- `uv add "psycopg[binary]"`로 프로젝트에 psycopg를 넣고, DSN 한 줄로 접속해요.
- `conn.execute(SQL)` 뒤에 `fetchall()`과 `fetchone()`을 붙여 결과를 리스트와 튜플로 받아요.
- `row_factory=dict_row`를 붙여 `c["fee"]`처럼 열 이름으로 꺼내요.
- 바뀌는 값은 `%s` 자리와 튜플로 넘기고, f-string으로 붙이면 왜 위험한지(SQL 인젝션) 설명해요.
- 수강료를 `SELECT`로 꺼내서 `INSERT`에 넣는 신청 함수를 만들고, `with` 블록이 끝날 때 저장된다는 것을 psql로 확인해요.
- 접속, 설치, 값 넘기기에서 나는 오류를 읽고 고쳐요.

## 시작하기 전에

| 할 일 | 챕터 |
| --- | :---: |
| `uv init`, `uv add`, `uv run main.py` | 09 |
| 튜플과 리스트, `for`, f-string 포맷(`:>2`, `:,`) | 13 |
| 딕셔너리(`c["fee"]`) | 15 |
| `if`, 함수(`def`, `return`) | 17, 19 |
| 컨테이너 `my-pg`(비밀번호 `admin1234`, `-p 5432:5432`), 데이터베이스 `kant_shop` | 35 |
| `JOIN`, `LEFT JOIN`, `COUNT`, 서브쿼리 | 39~41 |
| `BEGIN`, `COMMIT`, `ROLLBACK` | 43 |

`my-pg` 컨테이너를 켜고, 스포츠 센터 데이터 [sports.sql](./sports.sql)을 받은 폴더에서 `kant_shop`에 넣어요. 38에서 이미 넣었다면 건너뛰어도 돼요.

```bash
docker start my-pg
docker exec -i my-pg psql -U postgres -d kant_shop < sports.sql
```

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 3~5 | psql과 프로그램의 차이, 큰 그림, 일곱 줄짜리 첫 예제 |
| 1 · 준비하고 접속하기 | 6~8 | `uv add "psycopg[binary]"`, DSN 읽기, `with` 블록 |
| 2 · 결과 꺼내기 | 9~13 | `fetchall`과 튜플, `for`와 번호, `fetchone`과 `None`, `dict_row`, 강좌 목록 |
| 3 · %s로 값 넣기 | 14~17 | `%s` 자리와 튜플, 여러 개면 순서대로, SQL 인젝션 |
| 4 · 저장되는 순간 | 18~22 | 수업 TODO(수강료 꺼내 `INSERT`), `with`가 끝날 때 commit, 오류면 rollback, `commit()` |
| 5 · 비교와 오류 | 23~28 | psql과 비교, 설치, 접속, 괄호, 값 넘기기, 열 이름 오류 |
| 6 · 실제 상황 | 29~31 | 남은 자리 목록, 신청 전에 막기, 신청 내역 영수증 |
| 정리 | 32~33 | 언제 무엇을 쓰는지 표, 한 장 요약 |

## 핵심 개념

```
main.py ──SQL 글자──▶ psycopg ──localhost:5432──▶ PostgreSQL (my-pg)
main.py ◀─튜플의 리스트── psycopg ◀──결과 표────── PostgreSQL
```

- psql과 같은 서버, 같은 SQL이에요. 사람 대신 프로그램이 묻는 것만 달라요.
- 결과 줄 하나가 튜플 하나, 여러 줄은 리스트 하나예요. `dict_row`를 붙이면 줄 하나가 딕셔너리가 돼요.
- DSN은 `host=localhost port=5432 dbname=kant_shop user=postgres password=admin1234`처럼 `이름=값`을 띄어 쓴 접속 주소예요. 35에서 컨테이너를 켠 명령과 짝이 맞아요.
- 바뀌는 값은 SQL에 직접 붙이지 않고 `%s` 자리에 튜플로 넘겨요. 값이 하나면 `(값,)`처럼 쉼표를 붙여요.
- psql은 문장마다 바로 저장해요. psycopg는 `with` 블록이 끝날 때 한 번에 저장(commit)하고, 블록 안에서 오류가 나면 모두 취소(rollback)해요.

## 실습

### 1. 프로젝트 만들기

```bash
uv init sports-app
cd sports-app
uv add "psycopg[binary]"
```

```
Initialized project `sports-app` at `/home/kim/sports-app`
Using CPython 3.13.18 interpreter at: /usr/local/bin/python3.13
Creating virtual environment at: .venv
Resolved 4 packages in 374ms
Downloading psycopg-binary (3.7MiB)
 Downloaded psycopg-binary
Prepared 2 packages in 131ms
Installed 2 packages in 2ms
 + psycopg==3.3.9
 + psycopg-binary==3.3.9
```

경로, 시간, 버전 숫자는 컴퓨터마다 달라요. 대괄호가 셸에서 다르게 읽히지 않게 `"psycopg[binary]"` 전체를 큰따옴표로 감싸요.

### 2. 접속 확인

`main.py`를 아래처럼 고치고 실행해요.

```python
import psycopg

DSN = "host=localhost port=5432 dbname=kant_shop user=postgres password=admin1234"

with psycopg.connect(DSN) as conn:
    row = conn.execute("SELECT current_database(), current_user").fetchone()
    print("연결 성공:", row)
```

```bash
uv run main.py
```

```
연결 성공: ('kant_shop', 'postgres')
```

### 3. 강좌 목록 찍기

```python
import psycopg
from psycopg.rows import dict_row

DSN = "host=localhost port=5432 dbname=kant_shop user=postgres password=admin1234"

LIST_SQL = """
SELECT c.course_id, s.sport_name, c.course_name, c.fee
FROM courses c
JOIN sports s ON c.sport_id = s.sport_id
ORDER BY c.course_id
"""


def list_courses(conn):
    for c in conn.execute(LIST_SQL):
        no = c["course_id"]
        fee = f"{c['fee']:,}원"
        print(f"{no:>2} | {c['sport_name']} | {fee:>8} | {c['course_name']}")


with psycopg.connect(DSN, row_factory=dict_row) as conn:
    list_courses(conn)
```

```
 1 | 수영 |  70,000원 | 수영 초급 아침반
 2 | 수영 |  70,000원 | 수영 초급 저녁반
 3 | 수영 |  80,000원 | 수영 중급 새벽반
 …
13 | 필라테스 | 150,000원 | 필라테스 기구 초급
14 | 필라테스 | 160,000원 | 필라테스 중급
```

수업 코드는 표의 열 이름(`sports_id`)과 쿼리의 열 이름(`sport_id`)이 서로 달랐어요. 여기서는 38부터 쓰는 데이터에 맞춰 양쪽 다 `sport_id`예요. 결과에 쓰이지 않던 `LEFT JOIN`과 `DISTINCT`도 뺐어요.

### 4. 수강 신청 넣기 (수업 TODO)

```python
import psycopg
from psycopg.rows import dict_row

DSN = "host=localhost port=5432 dbname=kant_shop user=postgres password=admin1234"
MONTH = "2026-11"
MEMBER_ID = 10
COURSE_ID = 5

INSERT_SQL = """
INSERT INTO enrollments
  (enrollment_id, member_id, course_id, enroll_month, status, pay_amount)
VALUES
  ((SELECT MAX(enrollment_id) + 1 FROM enrollments), %s, %s, %s, '신청', %s)
"""


def enroll(conn, member_id, course_id):
    # 신청한 강좌의 수강료 꺼내기
    sql = "SELECT fee FROM courses WHERE course_id = %s"
    row = conn.execute(sql, (course_id,)).fetchone()
    fee = row["fee"]

    conn.execute(INSERT_SQL, (member_id, course_id, MONTH, fee))
    print(f"{member_id}번 회원이 {course_id}번 강좌를 신청했어요 ({fee:,}원)")


with psycopg.connect(DSN, row_factory=dict_row) as conn:
    enroll(conn, MEMBER_ID, COURSE_ID)
```

```
10번 회원이 5번 강좌를 신청했어요 (60,000원)
```

psql에서 확인하면 188번 줄이 새로 생겼어요.

```bash
docker exec -it my-pg psql -U postgres -d kant_shop
```

```
kant_shop=# SELECT * FROM enrollments ORDER BY enrollment_id DESC LIMIT 2;
 enrollment_id | member_id | course_id | enroll_month | status | pay_amount
---------------+-----------+-----------+--------------+--------+------------
           188 |        10 |         5 | 2026-11      | 신청   |      60000
           187 |        39 |        14 | 2026-11      | 신청   |     160000
(2 rows)
```

`enrollments` 표는 번호를 직접 적어야 해서 41의 서브쿼리로 가장 큰 번호 더하기 1을 넣었어요. `input()`은 아직 배우지 않아서 입력 로직 TODO는 맨 위 `MEMBER_ID`와 `COURSE_ID`에 값을 적어 두는 방식으로 남겨요. 실습을 처음부터 다시 하려면 `sports.sql`을 다시 넣어요.

## 명령어 요약

| 명령, 코드 | 하는 일 |
| --- | --- |
| `uv add "psycopg[binary]"` | psycopg와 PostgreSQL 접속 부품을 같이 넣어요 |
| `with psycopg.connect(DSN) as conn:` | 접속하고, 블록이 끝나면 저장하고 닫아요 |
| `conn.execute(SQL).fetchall()` | 결과 줄을 모두 튜플의 리스트로 받아요 |
| `conn.execute(SQL).fetchone()` | 첫 줄 하나만 받아요. 줄이 없으면 `None`이에요 |
| `for row in conn.execute(SQL):` | 한 줄씩 꺼내요 |
| `psycopg.connect(DSN, row_factory=dict_row)` | 줄 하나를 딕셔너리로 받아 `row["fee"]`로 꺼내요 |
| `conn.execute("... WHERE course_id = %s", (5,))` | 바뀌는 값을 `%s` 자리에 넘겨요 |
| `conn.commit()`, `conn.close()` | `with` 없이 연결했을 때 직접 저장하고 닫아요 |

## 문제 해결

| 메시지 | 원인 | 해결 |
| --- | --- | --- |
| `ModuleNotFoundError: No module named 'psycopg'` | 이 프로젝트에 psycopg를 안 넣었어요 | `uv add "psycopg[binary]"` 뒤 `uv run main.py` |
| `ImportError: no pq wrapper available.` | `[binary]` 없이 넣어서 접속 부품(libpq)을 못 찾았어요 | `uv add "psycopg[binary]"` |
| `connection failed: ... port 5433 failed: Connection refused` | DSN의 포트가 컨테이너와 다르거나 컨테이너가 꺼졌어요 | `docker ps`로 확인하고 `-p` 왼쪽 숫자를 `port=`에 적어요 |
| `FATAL:  password authentication failed for user "postgres"` | 비밀번호가 `POSTGRES_PASSWORD`와 달라요 | `password=admin1234` |
| `<bound method Cursor.fetchone of ...>`가 찍혀요 | `fetchone` 뒤 괄호를 뺐어요 | `fetchone()` |
| `TypeError: query parameters should be a sequence or a mapping, got str` | `(MONTH)`처럼 쉼표 없이 넘겨서 튜플이 아니에요 | `(MONTH,)` |
| `IndeterminateDatatype: could not determine data type of parameter $1` | `'%s'`처럼 `%s`를 따옴표로 감쌌어요 | `= %s` (따옴표는 psycopg가 붙여요) |
| `UndefinedColumn: column c.sports_id does not exist` | SQL의 열 이름이 표와 달라요 | `HINT`에 나온 `c.sport_id`로 고쳐요 |
| `OperationalError: the connection is closed` | `with` 블록 밖에서 `conn`을 썼어요 | SQL을 블록 안쪽으로 들여 써요 |
| `TypeError: 'NoneType' object is not subscriptable` | 없는 번호를 찾아 `fetchone()`이 `None`인데 칸을 꺼냈어요 | `if not row:`로 먼저 막아요(실제 상황 2) |

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
sports.sql         수강생이 받는 스포츠 센터 데이터 (38과 같은 파일)
slides/
  deck.json        슬라이드 순서와 파트 구분
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py           이 챕터의 장 생성
  demo.py          실제 Docker, PostgreSQL 18, uv, psycopg로 모든 장면을 실행해 out.json에 저장
  ptyrun.py        psql을 터미널처럼 실행하는 도우미 (37에서 가져옴)
  src/*.py         슬라이드에 넣은 파이썬 프로그램 (하나씩 ~/sports-app/main.py로 복사해 실행)
  out.json         슬라이드에 넣은 실제 출력
python-postgres-slides.html   배포용 HTML
python-postgres-slides.pdf    강사용 PDF
```

출력을 다시 만들려면 Docker를 켠 상태에서 `uv run --with pyte python tools/demo.py`를 쳐요. 장면 이름을 붙이면(`... demo.py enroll`) 그 장면만 다시 실행해요. 장면마다 `kant_shop`을 새로 만들고 `sports.sql`을 넣어서 시작해요. `no pq wrapper` 장면은 libpq가 없는 깨끗한 `python:3.13-slim` 컨테이너에서 같은 uv로 실행했어요.

수업 코드와 달라진 곳: `sport_id`와 `sports_id`가 어긋난 것을 맞췄고, 쓰이지 않던 `LEFT JOIN`과 `DISTINCT`를 뺐고, `fetchone` 괄호를 붙였어요. DSN의 포트는 35처럼 5432로 적었어요. 상태 값은 38 데이터에 맞춰 `'신청'`이에요.

검사, HTML, PDF를 만드는 공용 도구(`check.js`, `build_player.js`, `export.js`)는 맨 위 [tools/](../tools)에 한 벌만 있어요. 명령은 이 폴더에서 쳐요.

```bash
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/boxcheck.js slides
node ../tools/build_player.js slides python-postgres-slides.html
node ../tools/export.js slides python-postgres-slides.pdf
```

</details>

---

<!-- curriculum:nav -->

[← 이전: 43 · SQL 8 (트랜잭션)](../43-sql-transaction) · [커리큘럼](../README.md)

<!-- /curriculum:nav -->
