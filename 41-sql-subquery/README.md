# 41 · SQL 6 (서브쿼리)

> SELECT 문을 괄호로 감싸서 다른 SELECT 안에 넣어요. 괄호 안 SELECT가 먼저 실행돼서 값, 목록, 표 중 하나가 되고, 바깥 SELECT가 그 결과를 써요. 39의 집계(`AVG`, `SUM`, `GROUP BY`)와 40의 `JOIN`을 이어서 써요. 예제는 38부터 쓰는 스포츠 센터 수업 데이터예요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/41-sql-subquery/sql-subquery-slides.html) | [40 · SQL 5 (UNION과 JOIN으로 결과 합치기)](../40-sql-union-join) | 준비 중 |

<!-- /curriculum:top -->

## 학습 목표

- 평균을 손으로 옮겨 적는 대신 `WHERE fee > (SELECT AVG(fee) FROM courses)`처럼 한 문장으로 써요.
- 안쪽 SELECT만 따로 쳐서 결과가 값 하나인지, 목록인지, 표인지 먼저 확인해요.
- 목록이 나오는 서브쿼리는 `IN (...)`과 `NOT IN (...)` 안에 넣고, 같은 일을 `JOIN`으로도 써 봐요.
- 회원별 합계 같은 결과를 `FROM (...) AS paid`로 임시 표로 만들고, 그 표에 `WHERE`와 `JOIN`을 붙여요.
- `SELECT` 칸에 값 하나가 나오는 서브쿼리를 넣어 모든 줄 옆에 전체 평균과 차이를 붙여요.
- 서브쿼리에서 자주 나는 오류 여섯 가지를 읽고 고쳐요.

## 시작하기 전에

| 할 일 | 챕터 |
| --- | :---: |
| 컨테이너 `my-pg`, 데이터베이스 `kant_shop`, `docker exec -i ... < 파일` | 35 |
| `WHERE`, `IN`, `ORDER BY`, `LIMIT`, `AS` | 36 |
| `AVG`, `SUM`, `COUNT`, `ROUND`, `GROUP BY`, `HAVING` | 39 |
| `JOIN ... ON`, `LEFT JOIN`, 표 별명(`members m`) | 40 |

스포츠 센터 데이터 [sports.sql](./sports.sql)을 받아 터미널에서 그 폴더로 옮긴 뒤 `kant_shop`에 넣어요. 38에서 이미 넣었다면 건너뛰어도 돼요. 표 다섯 개(`sports`, `instructors`, `courses`, `members`, `enrollments`)를 지우고 새로 만들어요.

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
| 들어가기 | 1–6 | 표지, 오늘의 순서, 평균을 손으로 옮겨 적는 불편함, 수학 괄호와 SQL 괄호, 결과 모양 세 가지, 가장 작은 서브쿼리 |
| 1. 값 하나와 비교하기 | 7–9 | `= (SELECT MAX(...))`, 안쪽 쿼리의 `WHERE`, 강좌가 늘면 새 평균으로 다시 계산 |
| 2. 목록과 IN | 10–13 | `=` 뒤에 여러 줄이 오면 나는 오류, `IN (서브쿼리)`, `NOT IN`, 같은 일을 `JOIN`으로 |
| 3. FROM에 넣는 임시 표 | 14–19 | `WHERE`에 `SUM`을 쓰면 나는 오류, 회원별 합계 표, `FROM (...) AS paid`, 회원 표와 `JOIN`, `HAVING`과 비교, 합계의 평균 |
| 4. SELECT 칸에 넣기 | 20–22 | 전체평균과 평균과차이, 구별 회원 비율, 열 두 개를 돌려주는 오류 |
| 5. 비교하고 속 들여다보기 | 23–25 | 파이썬 두 줄과 비교, 넣는 자리 네 곳, `EXPLAIN ANALYZE`(참고, 읽기만) |
| 6. 오류와 실제 상황 | 26–30 | 오류 여섯 가지, 괄호와 `AS` 빠뜨리기, 11월 남은 자리, 가장 많이 신청한 강좌, 문자 보낼 회원 |
| 정리 | 31–32 | 언제 어떤 자리에 쓰는지, 한 장 요약 |

## 핵심 개념

### 괄호 안이 먼저 풀려요

`(3 + 4) × 2`에서 괄호 안을 먼저 계산해 `7 × 2`로 바꾸듯, 괄호 안 SELECT가 먼저 실행돼서 그 자리에 결과가 들어가요.

```
WHERE fee > (SELECT AVG(fee) FROM courses)
WHERE fee > 97857.142857142857          ← 안쪽이 먼저 값이 돼요
```

SELECT 안에 들어간 SELECT를 서브쿼리라고 해요. 바깥쪽은 메인 쿼리라고 불러요.

### 결과 모양이 들어갈 자리를 정해요

| 결과 모양 | 예 | 넣는 자리 |
| --- | --- | --- |
| 값 하나 (1줄 1칸) | 평균 97857.14 | `WHERE 열 > (...)`, `WHERE 열 = (...)`, `SELECT` 칸 |
| 목록 (여러 줄 1칸) | 회원 번호 11, 25 | `WHERE 열 IN (...)`, `NOT IN (...)` |
| 표 (여러 줄 여러 칸) | 회원별 합계 | `FROM (...) AS 이름` |

모양이 자리에 맞지 않으면 오류가 나요. 그래서 안쪽 SELECT만 먼저 따로 쳐서 결과 모양을 확인하고 넣어요.

### 쓰는 규칙

- 안쪽 SELECT 끝에는 `;`를 붙이지 않아요. `;`는 바깥 쿼리 끝에 하나만 써요.
- 괄호를 연 동안에는 psql 앞 표시가 `kant_shop(#`로 바뀌어요. 괄호를 닫아야 문장이 끝나요.
- `FROM` 자리에 넣은 서브쿼리에는 닫는 괄호 뒤에 `AS 이름`을 붙이고, 바깥에서 `이름.열`로 불러요.
- 바깥 `WHERE`와 안쪽 `WHERE`는 따로 일해요. 두 곳 다 거르려면 둘 다 적어요.

## 실습

psql 안에서 차례대로 쳐요. 출력은 PostgreSQL 18에서 실제로 실행한 결과예요.

### 1. 평균보다 비싼 강좌

```sql
SELECT course_name, fee
FROM courses
WHERE fee > (
    SELECT AVG(fee) FROM courses
)
ORDER BY fee DESC, course_name;
```

```
    course_name     |  fee
--------------------+--------
 필라테스 중급      | 160000
 필라테스 기구 초급 | 150000
 테니스 고급 레슨   | 130000
 헬스 PT 입문       | 120000
 테니스 중급 레슨   | 110000
 헬스 근력 중급     | 100000
(6 rows)
```

### 2. 11월에 13번 강좌를 신청한 회원 (IN)

```sql
SELECT name, phone
FROM members
WHERE member_id IN (
    SELECT member_id FROM enrollments
    WHERE course_id = 13 AND enroll_month = '2026-11'
);
```

```
  name  |     phone
--------+---------------
 손현우 | 010-3925-6325
 한수아 | 010-3407-5583
(2 rows)
```

`ORDER BY`를 붙이지 않아서 줄 순서는 다를 수 있어요.

### 3. 60만 원 이상 낸 회원 (FROM 임시 표)

```sql
SELECT *
FROM (
    SELECT member_id, SUM(pay_amount) AS total_paid
    FROM enrollments
    GROUP BY member_id
) AS paid
WHERE paid.total_paid >= 600000
ORDER BY paid.total_paid DESC;
```

```
 member_id | total_paid
-----------+------------
        16 |     745000
         3 |     740000
        26 |     705000
        17 |     630000
        39 |     615000
        11 |     610000
(6 rows)
```

### 4. 모든 강좌 옆에 전체 평균 붙이기 (SELECT 칸)

```sql
SELECT
    course_name,
    fee,
    (SELECT ROUND(AVG(fee), 2) FROM courses) AS 전체평균,
    fee - (SELECT ROUND(AVG(fee), 2) FROM courses) AS 평균과차이
FROM courses;
```

```
    course_name     |  fee   | 전체평균 | 평균과차이
--------------------+--------+----------+------------
 수영 초급 아침반   |  70000 | 97857.14 |  -27857.14
 수영 초급 저녁반   |  70000 | 97857.14 |  -27857.14
 수영 중급 새벽반   |  80000 | 97857.14 |  -17857.14
 …
 필라테스 중급      | 160000 | 97857.14 |   62142.86
(14 rows)
```

가운데 줄은 줄였어요. 슬라이드 20쪽에 14줄이 다 있어요.

## 명령어 요약

| 쓰는 모양 | 하는 일 |
| --- | --- |
| `WHERE fee > (SELECT AVG(fee) FROM courses)` | 평균 같은 값 하나와 비교해요 |
| `WHERE fee = (SELECT MAX(fee) FROM courses)` | 가장 큰 값을 가진 줄을 이름까지 꺼내요 |
| `WHERE member_id IN (SELECT member_id FROM ...)` | 목록에 든 줄만 골라요 |
| `WHERE member_id NOT IN (SELECT member_id FROM ...)` | 목록에 없는 줄만 골라요. 목록 열에 NULL이 없어야 해요 |
| `FROM (SELECT ... GROUP BY ...) AS paid` | 묶은 결과를 임시 표로 두고 다시 거르거나 JOIN해요 |
| `SELECT AVG(total_paid) FROM (...) AS paid` | 합계의 평균처럼 집계를 두 번 해요 |
| `(SELECT COUNT(*) FROM members) AS 전체` | 모든 줄 옆에 같은 값을 붙여요 |
| `EXPLAIN ANALYZE 쿼리` | 쿼리를 실행하고 일한 순서를 보여 줘요 (참고, 읽기만) |

## 문제 해결

| 메시지 | 원인 | 해결 |
| --- | --- | --- |
| `more than one row returned by a subquery used as an expression` | `=` 뒤 서브쿼리가 여러 줄을 돌려줬어요 | `IN (...)`으로 바꿔요 |
| `subquery must return only one column` | `SELECT` 칸이나 `=` 뒤 서브쿼리가 열을 두 개 이상 꺼냈어요 | 열마다 서브쿼리를 하나씩 써요 |
| `aggregate functions are not allowed in WHERE` | `WHERE`에 `SUM`, `COUNT`를 썼어요 | `HAVING`이나 `FROM` 서브쿼리를 써요 |
| `aggregate function calls cannot be nested` | `AVG(SUM(...))`처럼 집계를 겹쳐 썼어요 | 안쪽 집계를 `FROM` 서브쿼리로 빼요 |
| `missing FROM-clause entry for table "paid"` | `FROM` 서브쿼리에 `AS paid`를 안 붙였어요 | 닫는 괄호 뒤에 `AS paid`를 붙여요 |
| `syntax error at or near "SELECT"` | 서브쿼리를 괄호로 감싸지 않았어요 | `( )`로 감싸요 |
| 앞 표시가 `kant_shop(#`에서 안 바뀌어요 | 괄호를 열고 닫지 않았어요 | `)`와 `;`를 마저 쳐요. 처음부터 다시 치려면 `Ctrl+C` |
| `NOT IN` 결과가 0줄이에요 | 안쪽 목록에 NULL이 섞였어요 | 비어 있지 않은 열(회원 번호 등)로 목록을 만들어요 |

이 챕터는 바깥 줄마다 안쪽을 다시 계산하는 서브쿼리(상관 서브쿼리), `EXISTS`, `ANY`와 `ALL`, `WITH`(CTE)는 다루지 않아요.

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
  ptyrun.py        psql을 터미널처럼 실행하는 도우미 (37에서 가져옴)
  fees.py          파이썬 비교 장에 쓴 코드
  sports.sql       demo.py가 장면마다 넣는 데이터
  out.json         슬라이드에 넣은 실제 출력
sql-subquery-slides.html   배포용 HTML
sql-subquery-slides.pdf    강사용 PDF
```

출력을 다시 만들려면 `my-pg` 컨테이너를 켜 둔 상태에서 `uv run --with pyte python tools/demo.py`를 쳐요. 장면 이름을 붙이면(`... demo.py i-notin`) 그 장면만 다시 실행해요. `EXPLAIN ANALYZE`의 시간 숫자는 칠 때마다 조금씩 달라요.

검사, HTML, PDF를 만드는 공용 도구(`check.js`, `build_player.js`, `export.js`)는 맨 위 [tools/](../tools)에 한 벌만 있어요. 명령은 이 폴더에서 쳐요.

```bash
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/boxcheck.js slides
node ../tools/build_player.js slides sql-subquery-slides.html
node ../tools/export.js slides sql-subquery-slides.pdf
```

</details>

---

<!-- curriculum:nav -->

[← 이전: 40 · SQL 5 (UNION과 JOIN으로 결과 합치기)](../40-sql-union-join) · [커리큘럼](../README.md)

<!-- /curriculum:nav -->
