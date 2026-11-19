# 42 · SQL 7 (다른 표를 보고 넣고, 고치고, 지우기)

> SELECT로 고른 줄을 INSERT, UPDATE, DELETE에 바로 붙여 써요. 다른 표에서 골라 넣고, 다른 표를 보고 고치고, 다른 표에 있는지 없는지(`EXISTS`) 물어서 지워요. 36의 INSERT, UPDATE, DELETE와 41의 서브쿼리를 이어서 써요. 예제는 38부터 쓰는 스포츠 센터 수업 데이터예요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/42-sql-insert-select/sql-insert-select-slides.html) | [41 · SQL 6 (서브쿼리)](../41-sql-subquery) | 준비 중 |

<!-- /curriculum:top -->

## 학습 목표

- `INSERT INTO 표 (열, ...) SELECT ...`로 다른 표에서 고른 줄을 한 번에 넣어요.
- 넣을 열과 SELECT 칸이 이름이 아니라 순서대로 짝을 짓는다는 것을 알고, `'이메일 미등록' AS reason`처럼 모든 줄에 같은 값을 붙여요.
- UNION 결과를 넣을 때 날짜 글자를 `CAST('2026-11-19' AS DATE)`나 `'2026-11-19'::DATE`로 바꿔요.
- `ALTER TABLE ... ADD COLUMN`으로 열을 더하고, `SET a = ..., b = ...`로 여러 열을 한 번에 고쳐요.
- `UPDATE`의 `WHERE`에 서브쿼리를 넣어 다른 표의 조건으로 고칠 줄을 골라요.
- `EXISTS`와 `NOT EXISTS`로 다른 표에 줄이 있는지 묻고, 안쪽에 `SELECT 1`을 쓰는 이유를 알아요.
- 목록에 NULL이 섞이면 `NOT IN`이 0줄이 되는 함정을 보고 `NOT EXISTS`로 바꿔 써요.
- 지우기 전에 같은 `WHERE`로 SELECT부터 해 보고, `DELETE`, `TRUNCATE`, `DROP TABLE`의 차이를 구별해요.

## 시작하기 전에

| 할 일 | 챕터 |
| --- | :---: |
| 컨테이너 `my-pg`, 데이터베이스 `kant_shop`, `docker exec -i ... < 파일` | 35 |
| `INSERT`, `UPDATE ... SET ... WHERE`, `DELETE`, `RETURNING`, `AS` | 36 |
| `SERIAL`, `NOT NULL`, `DEFAULT`, 외래 키, `TRUNCATE ... RESTART IDENTITY` | 37 |
| `GROUP BY`, `HAVING`, `COUNT(*)` | 39 |
| `UNION`, `JOIN`, 표 별명(`members m`) | 40 |
| `IN (서브쿼리)`, `NOT IN` | 41 |

스포츠 센터 데이터 [sports.sql](./sports.sql)을 받아 터미널에서 그 폴더로 옮긴 뒤 `kant_shop`에 넣어요. 이 챕터는 표를 고치고 지우니, 앞 챕터에서 넣어 둔 표가 있어도 다시 넣고 시작해요. 표 다섯 개(`sports`, `instructors`, `courses`, `members`, `enrollments`)를 지우고 새로 만들어요.

```bash
docker exec -i my-pg psql -U postgres -d kant_shop < sports.sql
```

```
DROP TABLE
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE TABLE
INSERT 0 5
INSERT 0 8
INSERT 0 14
INSERT 0 40
INSERT 0 187
```

처음 넣을 때는 아래에 `NOTICE:  table "enrollments" does not exist, skipping` 같은 줄이 더 나와요. 지울 표가 아직 없다는 안내라서 그대로 두면 돼요. 그다음 psql로 들어가요.

```bash
docker exec -it my-pg psql -U postgres -d kant_shop
```

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1–6 | 표지, 오늘의 순서, SELECT 결과를 손으로 옮겨 적는 불편함, 큰 그림, 명단 표 만들기, 가장 작은 `INSERT ... SELECT` |
| 1. 다른 표에서 골라 넣기 | 7–12 | 열과 칸의 짝, 모든 줄에 같은 값 붙이기, VALUES와 비교, UNION 날짜 오류, `CAST`와 `::`, UNION 결과 넣기 |
| 2. 여러 열과 계산으로 고치기 | 13–16 | `ALTER TABLE ... ADD COLUMN`, `SET` 여러 열, INTEGER 열의 반올림, `WHERE IN (서브쿼리)`로 고치기 |
| 3. 있는지 묻기 (EXISTS) | 17–22 | `EXISTS`와 `SELECT 1`, 바깥 줄마다 묻기, EXISTS와 IN, `NOT EXISTS`, `NOT IN`과 NULL, IN·EXISTS·JOIN 비교 |
| 4. 지우기와 표 비우기 | 23–26 | SELECT 먼저 보고 DELETE, 외래 키 오류, `DELETE`·`TRUNCATE`·`DROP TABLE` 그림과 실제 결과 |
| 5. 오류와 함정 | 27–29 | 열 개수와 순서, 잇는 조건 빠뜨리기, 줄이 있는 표에 `NOT NULL` 열 더하기 |
| 6. 실제 상황 | 30–32 | 취소한 신청을 보관 표로 옮기기, 강사가 없는 강좌에 강사 맡기기, 이메일을 받은 회원 명단에서 지우기 |
| 정리 | 33–34 | 할 일마다 쓰는 모양, 한 장 요약 |

## 핵심 개념

### VALUES 자리에 SELECT를 붙여요

36에서는 `INSERT ... VALUES`로 넣을 값을 줄마다 적었어요. 넣을 줄이 다른 표에 있으면 VALUES 자리에 SELECT 문을 그대로 붙여요. SELECT가 고른 줄이 모두 들어가요.

```
INSERT INTO contact_lists (member_id, name, reason, request_date)
SELECT member_id, name, '이메일 미등록', '2026-11-19'     ← VALUES 대신
FROM members
WHERE email IS NULL;
```

넣을 열과 SELECT 칸은 이름이 아니라 적은 순서대로 짝을 지어요. 첫 번째 칸이 첫 번째 열에 들어가요. `'이메일 미등록'`처럼 표에 없는 글자를 SELECT하면 모든 줄에 같은 값이 붙어요.

### EXISTS는 줄이 있는지만 물어요

```
SELECT m.name FROM members m
WHERE NOT EXISTS (SELECT 1 FROM enrollments e WHERE e.member_id = m.member_id);
```

| | IN (41) | EXISTS (42) |
| --- | --- | --- |
| 안쪽이 만드는 것 | 회원 번호 목록 | 줄이 있나요? (t, f) |
| 안쪽에 바깥 열 | 안 써요. 혼자 실행돼요 | `m.member_id`를 써요. 바깥 줄마다 다시 물어요 |
| 목록에 NULL이 섞이면 | `NOT IN`은 0줄이 돼요 | 맞게 나와요 |

EXISTS는 칸에 들어 있는 값을 보지 않고 줄이 있는지만 봐요. 그래서 안쪽은 짧게 `SELECT 1`로 적어요. 안쪽 `WHERE`에 바깥과 잇는 조건(`e.member_id = m.member_id`)을 꼭 적어요.

### 지우는 명령 세 가지

| 명령 | 지우는 것 | 남는 것 |
| --- | --- | --- |
| `DELETE FROM 표 WHERE ...` | 고른 줄 | 표와 나머지 줄 |
| `TRUNCATE 표` | 모든 줄 | 빈 표 (`RESTART IDENTITY`로 번호를 1부터) |
| `DROP TABLE 표` | 표까지 | 없음 |

셋 다 실행하면 바로 저장돼서 되돌릴 수 없어요. 지우기 전에 같은 `WHERE`로 SELECT부터 해서 줄 수를 봐요. 실행한 뒤에도 취소할 수 있게 묶는 트랜잭션은 43에서 배워요.

## 실습

psql 안에서 차례대로 쳐요. 출력은 PostgreSQL 18에서 실제로 실행한 결과예요.

### 1. 연락할 회원 명단 표 만들기

```sql
CREATE TABLE contact_lists (
    request_id   SERIAL      PRIMARY KEY,
    member_id    INTEGER     NOT NULL,
    name         VARCHAR(20) NOT NULL,
    reason       VARCHAR(50) NOT NULL,
    request_date DATE        NOT NULL
);
```

```
CREATE TABLE
```

### 2. 이메일이 없는 회원을 한 번에 넣기

```sql
INSERT INTO contact_lists (member_id, name, reason, request_date)
SELECT member_id, name, '이메일 미등록', '2026-11-19'
FROM members
WHERE email IS NULL;

SELECT * FROM contact_lists;
```

```
INSERT 0 9
 request_id | member_id |  name  |    reason     | request_date
------------+-----------+--------+---------------+--------------
          1 |         3 | 박도현 | 이메일 미등록 | 2026-11-19
          2 |         5 | 정하은 | 이메일 미등록 | 2026-11-19
          3 |        10 | 임준서 | 이메일 미등록 | 2026-11-19
          4 |        16 | 황민서 | 이메일 미등록 | 2026-11-19
          5 |        17 | 안태윤 | 이메일 미등록 | 2026-11-19
          6 |        24 | 양다인 | 이메일 미등록 | 2026-11-19
          7 |        27 | 백준혁 | 이메일 미등록 | 2026-11-19
          8 |        31 | 하동건 | 이메일 미등록 | 2026-11-19
          9 |        38 | 진우성 | 이메일 미등록 | 2026-11-19
(9 rows)
```

### 3. 표를 비우고 UNION 결과를 넣기

이메일이 없는 회원과 전화번호가 없는 회원을 함께 넣어요. UNION으로 합칠 때는 날짜 글자를 DATE로 바꿔 줘야 해요. 첫 SELECT는 `CAST`, 둘째 SELECT는 `::`로 바꿨어요. 둘은 같은 뜻이에요.

```sql
TRUNCATE contact_lists RESTART IDENTITY;

INSERT INTO contact_lists (member_id, name, reason, request_date)
SELECT member_id, name, '이메일 미등록' AS reason, CAST('2026-11-19' AS DATE) AS request_date
FROM members WHERE email IS NULL
UNION
SELECT member_id, name, '전화번호 미등록', '2026-11-19'::DATE
FROM members WHERE phone IS NULL
ORDER BY member_id, reason;

SELECT COUNT(*) FROM contact_lists;
```

```
TRUNCATE TABLE
INSERT 0 16
 count
-------
    16
(1 row)
```

이메일 9명과 전화번호 7명이 모두 들어갔어요. 둘 다 없는 임준서와 황민서는 reason이 달라서 두 줄씩 남아요.

### 4. 열을 더하고 여러 열을 한 번에 고치기

```sql
ALTER TABLE courses ADD COLUMN class_days VARCHAR(10);

UPDATE courses
SET class_days = '월수금', start_time = '20:00'
WHERE course_id = 9
RETURNING course_id, course_name, class_days, start_time;
```

```
ALTER TABLE
 course_id | course_name | class_days | start_time
-----------+-------------+------------+------------
         9 | 요가 중급   | 월수금     | 20:00:00
(1 row)

UPDATE 1
```

### 5. 11월 인기 강좌의 정원 늘리기 (WHERE IN 서브쿼리)

```sql
UPDATE courses
SET capacity = capacity + 5
WHERE course_id IN (
    SELECT course_id FROM enrollments
    WHERE enroll_month = '2026-11'
    GROUP BY course_id
    HAVING COUNT(*) >= 5
)
RETURNING course_id, course_name, capacity;
```

```
 course_id |   course_name    | capacity
-----------+------------------+----------
         1 | 수영 초급 아침반 |       25
         2 | 수영 초급 저녁반 |       25
         3 | 수영 중급 새벽반 |       20
         4 | 수영 고급반      |       17
         5 | 아쿠아로빅       |       30
         9 | 요가 중급        |       23
(6 rows)

UPDATE 6
```

`RETURNING` 줄 순서는 다를 수 있어요.

### 6. 신청 기록이 없는 회원 찾기 (NOT EXISTS)

```sql
SELECT m.member_id, m.name, m.region
FROM members m
WHERE NOT EXISTS (
    SELECT 1 FROM enrollments e
    WHERE e.member_id = m.member_id
);
```

```
 member_id |  name  | region
-----------+--------+--------
        40 | 채윤서 | 강서구
(1 row)
```

### 7. NOT IN과 NOT EXISTS 비교하기

5번 강좌 아쿠아로빅은 강사 칸이 NULL이에요. 강좌를 맡지 않은 강사를 두 가지로 찾아봐요.

```sql
SELECT name FROM instructors
WHERE instructor_id NOT IN (SELECT instructor_id FROM courses);

SELECT i.name FROM instructors i
WHERE NOT EXISTS (SELECT 1 FROM courses c WHERE c.instructor_id = i.instructor_id);
```

```
 name
------
(0 rows)

  name
--------
 윤태호
(1 row)
```

### 8. SELECT로 먼저 보고 같은 WHERE로 지우기

```sql
SELECT m.member_id, m.name
FROM members m
WHERE NOT EXISTS (SELECT 1 FROM enrollments e WHERE e.member_id = m.member_id);

DELETE FROM members m
WHERE NOT EXISTS (SELECT 1 FROM enrollments e WHERE e.member_id = m.member_id)
RETURNING m.member_id, m.name;
```

```
 member_id |  name
-----------+--------
        40 | 채윤서
(1 row)

 member_id |  name
-----------+--------
        40 | 채윤서
(1 row)

DELETE 1
```

SELECT에서 본 줄 수와 `DELETE` 뒤의 숫자가 같은지 봐요.

## 명령어 요약

| 쓰는 모양 | 하는 일 |
| --- | --- |
| `INSERT INTO 표 (열, ...) SELECT 칸, ... FROM ... WHERE ...` | 다른 표에서 고른 줄을 한 번에 넣어요 |
| `SELECT ..., '이메일 미등록' AS reason` | 모든 줄에 같은 값을 붙여요 |
| `CAST('2026-11-19' AS DATE)`, `'2026-11-19'::DATE` | 글자를 날짜로 바꿔요. UNION 결과를 DATE 열에 넣을 때 써요 |
| `ALTER TABLE 표 ADD COLUMN 열 자료형 [DEFAULT 값]` | 있는 표에 열을 더해요 |
| `UPDATE 표 SET a = ..., b = ... WHERE ...` | 한 줄의 여러 열을 한 번에 고쳐요 |
| `UPDATE ... WHERE id IN (SELECT ...)` | 다른 표의 조건으로 고칠 줄을 골라요 |
| `WHERE EXISTS (SELECT 1 FROM ... WHERE 잇는 조건)` | 다른 표에 줄이 있는 것만 골라요 |
| `WHERE NOT EXISTS (SELECT 1 FROM ... WHERE 잇는 조건)` | 다른 표에 줄이 없는 것만 골라요 |
| `DELETE FROM 표 별명 WHERE ... RETURNING ...` | 고른 줄을 지우고 지운 줄을 보여 줘요 |
| `TRUNCATE 표 RESTART IDENTITY` | 모든 줄을 비우고 번호를 1부터 다시 세요 |
| `DROP TABLE 표` | 표를 통째로 없애요 |

## 문제 해결

| 메시지 | 원인 | 해결 |
| --- | --- | --- |
| `column "request_date" is of type date but expression is of type text` | UNION으로 합친 날짜 글자가 text가 됐어요 | `CAST(... AS DATE)`나 `::DATE`를 붙여요 |
| `INSERT has more target columns than expressions` | 넣을 열보다 SELECT 칸이 적어요 | 첫 줄 괄호의 열과 SELECT 칸 개수를 맞춰요 |
| `column "member_id" is of type integer but expression is of type character varying` | SELECT 칸 순서가 넣을 열 순서와 달라요 | 열 순서대로 SELECT 칸을 다시 적어요 |
| `update or delete on table "members" violates foreign key constraint` | 지우려는 회원을 신청 표가 아직 가리켜요 | 자식 줄(신청 기록)부터 지우거나, `NOT EXISTS`로 기록이 없는 회원만 골라요 |
| `column "class_days" of relation "courses" contains null values` | 줄이 있는 표에 `NOT NULL` 열만 더했어요 | `DEFAULT 값`을 같이 붙여요 |
| `relation "contact_lists" does not exist` | `DROP TABLE`로 표를 없앴어요 | `CREATE TABLE`부터 다시 해요 |
| `NOT IN` 결과가 0줄이에요 | 안쪽 목록에 NULL이 섞였어요 | `NOT EXISTS`로 바꿔요 |
| EXISTS 결과가 0명이거나 전부예요 | 안쪽 `WHERE`에 바깥과 잇는 조건이 없어요 | `e.member_id = m.member_id`처럼 잇는 조건을 적어요 |
| INTEGER 열에 넣은 계산값의 소수가 사라졌어요 | INTEGER 열은 소수점 아래를 반올림해서 저장해요 | 소수까지 남기려면 열을 `NUMERIC`으로 만들어요 |

이 챕터는 트랜잭션(`BEGIN`, `COMMIT`, `ROLLBACK`, 43에서), `INSERT ... ON CONFLICT`, `UPDATE ... FROM`, `DELETE ... USING`, `MERGE`, `ANY`와 `ALL`, `WITH`(CTE)는 다루지 않아요.

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
  demo.py          실제 Docker와 PostgreSQL 18로 장면을 실행해 out.json에 저장
  ptyrun.py        psql을 터미널처럼 실행하는 도우미 (41에서 가져옴)
  sports.sql       demo.py가 장면마다 넣는 데이터
  out.json         슬라이드에 넣은 실제 출력
sql-insert-select-slides.html   배포용 HTML
sql-insert-select-slides.pdf    강사용 PDF
```

수업 코드에서 고친 곳이 있어요.

- UNION으로 넣는 문장 끝의 `ORDER BY reason`은 첫 SELECT에 `AS reason`, `AS request_date`가 없으면 열 이름을 못 찾아요. 수업 코드처럼 첫 SELECT에 `AS`를 붙였어요.
- 한 SELECT에서는 `'2026-11-19'`를 그대로 넣어도 되지만, UNION으로 합치면 text가 돼서 오류가 나요. 그래서 1파트에 오류 장을 넣고 `CAST`와 `::`를 그 해결로 보여 줘요.
- 강좌가 없는 강사를 `NOT IN`으로 찾으면 강사 칸이 NULL인 5번 강좌 때문에 0줄이에요. 수업 데이터 그대로 두고 `NOT EXISTS`와 비교하는 장으로 썼어요.

출력을 다시 만들려면 Docker를 켜 둔 상태에서 `uv run -q --with pyte python tools/demo.py`를 쳐요. 장면 이름을 붙이면(`... demo.py notin-null`) 그 장면만 다시 실행해요.

검사, HTML, PDF를 만드는 공용 도구(`check.js`, `build_player.js`, `export.js`)는 맨 위 [tools/](../tools)에 한 벌만 있어요. 명령은 이 폴더에서 쳐요.

```bash
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/boxcheck.js slides
node ../tools/build_player.js slides sql-insert-select-slides.html
node ../tools/export.js slides sql-insert-select-slides.pdf
```

</details>

---

<!-- curriculum:nav -->

[← 이전: 41 · SQL 6 (서브쿼리)](../41-sql-subquery) · [커리큘럼](../README.md)

<!-- /curriculum:nav -->
