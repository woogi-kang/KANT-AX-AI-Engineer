# 39 · SQL 4 (집계 함수와 GROUP BY)

> 36에서는 표에서 필요한 줄을 골라 봤어요. 이번에는 여러 줄을 값 하나로 접는 집계 함수(`COUNT`, `MIN`, `MAX`, `SUM`, `AVG`)와, 같은 값끼리 묶어서 묶음마다 접는 `GROUP BY`를 배워요. 묶은 결과를 고르는 `HAVING`과, `WHERE`와 무엇이 다른지도 실행 순서 그림으로 봐요. 표는 38에서 넣은 스포츠 센터 데이터베이스(`sports`, `instructors`, `courses`, `members`, `enrollments`)예요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/39-sql-aggregate/sql-aggregate-slides.html) | [38 · SQL 3 (조건 조합과 CASE)](../38-sql-case) | 준비 중 |

<!-- /curriculum:top -->

## 학습 목표

- `COUNT(*)`, `MIN`, `MAX`, `SUM`, `AVG`로 여러 줄을 값 하나로 접어요.
- `ROUND(값, 2)`와 `ROUND(값)`으로 평균의 소수를 줄여요.
- `COUNT(*)`, `COUNT(열)`, `COUNT(DISTINCT 열)`이 각각 무엇을 세는지 말하고, 집계 함수가 NULL은 건너뛰지만 0은 센다는 것을 확인해요.
- `GROUP BY 열`로 같은 값끼리 묶고, 묶음마다 건수와 합계를 내요. 열 두 개로도 묶어요.
- `HAVING`으로 묶음을 고르고, `WHERE`(묶기 전에 줄 거르기)와 구별해요.
- SQL이 실행되는 순서(`FROM`, `WHERE`, `GROUP BY`, `HAVING`, `SELECT`, `ORDER BY`, `LIMIT`)로 자주 나는 오류 세 가지를 풀어요.

## 시작하기 전에

| 할 일 | 챕터 |
| --- | :---: |
| 컨테이너 `my-pg`, 데이터베이스 `kant_shop`, `docker cp`, `psql -f` | 35 |
| `SELECT`, `WHERE`, `AS`, `DISTINCT`, `COUNT(*)`로 줄 수 세기, `ORDER BY`, `LIMIT` | 36 |
| 스포츠 센터 데이터베이스 넣기 | 38 |
| 딕셔너리로 개수 세기(`counts.get(r, 0) + 1`) | 15 |

38에서 스포츠 센터 표를 넣었으면 다시 안 해도 돼요. 처음이면 이 폴더의 `sports.sql`을 받아서 넣어요. 같은 이름의 표가 있으면 지우고 다시 만들어요.

```bash
docker cp sports.sql my-pg:/tmp/sports.sql
docker exec -it my-pg psql -U postgres -d kant_shop -f /tmp/sports.sql
docker exec -it my-pg psql -U postgres -d kant_shop
```

| 표 | 줄 수 | 주요 열 |
| --- | :---: | --- |
| `sports` | 5 | `sport_id`, `sport_name` |
| `courses` | 14 | `course_id`, `sport_id`, `course_name`, `level`, `fee`, `capacity` |
| `members` | 40 | `member_id`, `name`, `email`, `phone`, `region` (이메일과 전화번호는 비어 있는 칸이 있어요) |
| `enrollments` | 187 | `member_id`, `course_id`, `enroll_month`, `status`(완료, 신청, 취소), `pay_amount`(취소는 0원) |

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1–5 | 표지, 오늘의 순서, 63줄을 다 더해야 하는 장면, 접기와 묶기 그림, `COUNT(*)` 한 줄 |
| 1. 집계 함수 다섯 개 | 6–10 | `MIN`과 `MAX`, `SUM`, `AVG`와 `ROUND`, 다섯 함수를 한 SELECT에, `WHERE`로 거른 뒤 접기 |
| 2. COUNT 세 가지와 NULL | 11–15 | `COUNT(열)`은 NULL을 빼고 세기, `COUNT(DISTINCT 열)`, 네 가지 비교, 0원도 평균에 들어가는 함정, 고른 줄이 없을 때 |
| 3. GROUP BY로 묶기 | 16–22 | `WHERE`를 세 번 바꿔 치는 불편, 바구니 그림, 달마다 매출, 난이도별 평균, 열 두 개로 묶기, 묶지 않은 열 오류와 고치기 |
| 4. HAVING으로 묶음 고르기 | 23–29 | `WHERE`에 `COUNT`를 넣는 오류, `HAVING` 막대 그림, 10명 넘는 구, `WHERE`와 `HAVING` 같이 쓰기, 실행 순서, `HAVING`에 AS 이름을 쓰는 오류 |
| 5. 앞에서 배운 것과 비교 | 30–31 | 36의 `DISTINCT`와 `GROUP BY`, 15의 딕셔너리로 세기와 `GROUP BY` |
| 6. 오류와 실제 상황 | 32–37 | 오류 네 가지, 글자 열과 집계 함수, 월별 매출 보고서, 인기 강좌 세 개, 단골 회원, 종목별 현황 |
| 정리 | 38–39 | 언제 무엇을 쓰는지, 치트시트 |

## 핵심 개념

### 집계 함수는 여러 줄을 한 줄로 접어요

| 함수 | 돌려주는 값 | 예 |
| --- | --- | --- |
| `COUNT(*)` | 줄 수 | 강좌 14개 |
| `COUNT(열)` | 그 칸이 NULL이 아닌 줄 수 | 이메일을 남긴 회원 31명 |
| `COUNT(DISTINCT 열)` | 겹치지 않는 값의 수 | 회원이 사는 구 4개 |
| `SUM(열)` | 합계 (숫자 열만) | 전체 정원 191명 |
| `AVG(열)` | 평균 (숫자 열만) | 평균 수강료 97857.142857142857 |
| `MIN(열)` `MAX(열)` | 가장 작은 값, 가장 큰 값 | 60000, 160000 |
| `ROUND(값, 2)` `ROUND(값)` | 소수 둘째 자리까지, 정수로 반올림 | 97857.14, 97857 |

- 집계 함수만 적으면 표가 몇 줄이든 결과는 한 줄이에요.
- 집계 함수는 NULL만 건너뛰어요. 0은 값이라서 개수와 평균에 들어가요. 취소한 0원을 빼려면 `WHERE status <> '취소'`를 먼저 적어요.
- 고른 줄이 하나도 없으면 `COUNT`는 0, `SUM`과 `MAX`는 NULL(psql에서 빈칸)이에요.

### GROUP BY는 묶은 다음 묶음마다 접어요

`GROUP BY enroll_month`는 `enroll_month`가 같은 줄끼리 한 바구니에 담고, 집계 함수가 바구니마다 따로 계산해요. 결과는 바구니 수만큼 나와요. 묶음이 나오는 순서는 정해져 있지 않으니, 순서가 필요하면 `ORDER BY`를 붙여요.

`GROUP BY`를 쓴 `SELECT`에는 묶은 열과 집계 함수만 적어요. 묶지 않은 열을 적으면 바구니 하나에 값이 여러 개라서 오류가 나요.

### WHERE는 줄을, HAVING은 묶음을 걸러요

PostgreSQL은 적은 순서와 다른 순서로 실행해요.

1. `FROM` 표 고르기
2. `WHERE` 줄 거르기
3. `GROUP BY` 묶기
4. `HAVING` 묶음 거르기
5. `SELECT` 칸 고르기, AS 이름이 생겨요
6. `ORDER BY` 줄 세우기
7. `LIMIT` 자르기

그래서 `WHERE`에는 집계 함수를 못 쓰고(아직 안 묶었어요), `HAVING`에는 AS 이름을 못 써요(이름은 다음 단계인 `SELECT`에서 생겨요). `ORDER BY`에는 AS 이름을 써도 돼요.

## 실습

`docker exec -it my-pg psql -U postgres -d kant_shop`으로 들어가서 순서대로 쳐요. 출력은 실제 `postgres:18`에서 실행한 결과예요.

### 1. 집계 함수 다섯 개를 한 번에

```sql
SELECT
    COUNT(*)            AS 강좌수,
    MIN(fee)            AS 최저수강료,
    MAX(fee)            AS 최고수강료,
    SUM(capacity)       AS 전체정원,
    ROUND(AVG(fee), 2)  AS 평균수강료
FROM courses;
```

```
 강좌수 | 최저수강료 | 최고수강료 | 전체정원 | 평균수강료
--------+------------+------------+----------+------------
     14 |      60000 |     160000 |      191 |   97857.14
(1 row)
```

### 2. COUNT 세 가지 비교

```sql
SELECT
    COUNT(*)               AS 회원수,
    COUNT(email)           AS 이메일있음,
    COUNT(phone)           AS 전화번호있음,
    COUNT(DISTINCT region) AS 사는구
FROM members;
```

```
 회원수 | 이메일있음 | 전화번호있음 | 사는구
--------+------------+--------------+--------
     40 |         31 |           33 |      4
(1 row)
```

### 3. 달마다 신청 건수와 매출

```sql
SELECT
    enroll_month    AS 신청월,
    COUNT(*)        AS 신청건수,
    SUM(pay_amount) AS 매출
FROM enrollments
GROUP BY enroll_month
ORDER BY enroll_month;
```

```
 신청월  | 신청건수 |  매출
---------+----------+---------
 2026-09 |       64 | 5265000
 2026-10 |       60 | 4565000
 2026-11 |       63 | 4950000
(3 rows)
```

열 두 개로 묶으면 월과 상태가 모두 같은 줄끼리 묶여요.

```sql
SELECT
    enroll_month, status, COUNT(*) AS 건수
FROM enrollments
GROUP BY enroll_month, status
ORDER BY enroll_month, status;
```

```
 enroll_month | status | 건수
--------------+--------+------
 2026-09      | 완료   |   58
 2026-09      | 취소   |    6
 2026-10      | 완료   |   52
 2026-10      | 취소   |    8
 2026-11      | 신청   |   57
 2026-11      | 취소   |    6
(6 rows)
```

### 4. 취소를 빼고 18건 이상인 인기 강좌

```sql
SELECT
    course_id, COUNT(*) AS 누적신청
FROM enrollments
WHERE status <> '취소'
GROUP BY course_id
HAVING COUNT(*) >= 18
ORDER BY 누적신청 DESC, course_id;
```

```
 course_id | 누적신청
-----------+----------
         2 |       25
         5 |       20
(2 rows)
```

`WHERE` 줄을 지우고 다시 쳐 보면 취소까지 세서 1번과 8번 강좌도 나와요(4줄).

### 5. 회원이 10명 넘게 사는 구

```sql
SELECT
    region, COUNT(*) AS 회원수
FROM members
GROUP BY region
HAVING COUNT(*) >= 10
ORDER BY 회원수 DESC, region;
```

```
  region  | 회원수
----------+--------
 영등포구 |     12
 마포구   |     11
 강서구   |     10
(3 rows)
```

### 6. 60만 원 넘게 결제한 단골 회원

```sql
SELECT
    member_id,
    COUNT(*)        AS 신청수,
    SUM(pay_amount) AS 누적결제
FROM enrollments
WHERE status <> '취소'
GROUP BY member_id
HAVING SUM(pay_amount) >= 600000
ORDER BY 누적결제 DESC, member_id;
```

```
 member_id | 신청수 | 누적결제
-----------+--------+----------
        16 |      8 |   745000
         3 |      8 |   740000
        26 |      7 |   705000
        17 |      7 |   630000
        39 |      6 |   615000
        11 |      7 |   610000
(6 rows)
```

끝나면 `\q`로 나와요.

## 명령어 요약

| 명령 | 하는 일 |
| --- | --- |
| `SELECT COUNT(*) FROM 표;` | 줄 수 |
| `COUNT(열)` | 그 칸이 NULL이 아닌 줄 수 |
| `COUNT(DISTINCT 열)` | 겹치지 않는 값의 수 |
| `SUM(열)` `AVG(열)` | 합계, 평균 (숫자 열만) |
| `MIN(열)` `MAX(열)` | 가장 작은 값, 가장 큰 값 (글자 열도 돼요) |
| `ROUND(AVG(fee), 2)` | 소수 둘째 자리까지 반올림 |
| `ROUND(AVG(fee))` | 정수로 반올림 |
| `GROUP BY 열` | 같은 값끼리 묶어 묶음마다 한 줄 |
| `GROUP BY 열1, 열2` | 두 값이 모두 같은 줄끼리 묶기 |
| `HAVING COUNT(*) >= 18` | 묶음 거르기 (`GROUP BY` 뒤) |
| `HAVING SUM(pay_amount) >= 600000` | `HAVING`에는 다른 집계 함수도 써요 |
| `WHERE status <> '취소'` | 묶기 전에 줄 거르기 |
| `ORDER BY 이름 DESC` | AS로 붙인 이름으로 줄 세우기 |

## 문제 해결

| 메시지 | 원인 | 해결 |
| --- | --- | --- |
| `column "enrollments.member_id" must appear in the GROUP BY clause or be used in an aggregate function` | 묶지 않은 열을 `SELECT`에 적었거나, 집계 함수 옆에 열을 적고 `GROUP BY`를 빼먹었어요 | `GROUP BY`에 그 열을 더하거나 `COUNT(DISTINCT member_id)`처럼 집계 함수로 감싸요 |
| `aggregate functions are not allowed in WHERE` | `WHERE`에 `COUNT`, `SUM`을 적었어요 | 그 조건을 `GROUP BY` 뒤 `HAVING`으로 옮겨요 |
| `column "누적신청" does not exist` | `HAVING`에 AS 이름을 적었어요 | `HAVING COUNT(*) >= 18`처럼 함수를 다시 적어요 |
| `function sum(character varying) does not exist` | 글자 열을 `SUM`, `AVG`에 넣었어요 | 숫자 열인지 확인해요. 글자 열은 `COUNT`, `MIN`, `MAX`만 돼요 |
| 평균이 생각보다 낮아요 | 취소한 0원까지 개수에 들어갔어요 | `WHERE status <> '취소'`로 먼저 걸러요 |
| `SUM` 결과가 빈칸이에요 | `WHERE`로 고른 줄이 하나도 없어요 | `WHERE` 조건을 확인해요. 그때 `COUNT(*)`는 0이에요 |
| `GROUP BY` 결과 순서가 실행할 때마다 달라요 | 묶음 순서는 정해져 있지 않아요 | `ORDER BY`를 붙여요 |

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
sports.sql                 스포츠 센터 표 다섯 개 (38과 같은 파일)
slides/
  deck.json                슬라이드 순서와 파트 구분
  *.html                   한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py                   이 챕터의 장 생성
  demo.py                  슬라이드에 넣은 psql 출력을 실제 postgres:18에서 실행 (tools/out.json)
  ptyrun.py                psql을 터미널처럼 실행하는 도우미
  make_sports.py           sports.sql을 고정 시드로 만드는 스크립트
sql-aggregate-slides.html  배포용 HTML
sql-aggregate-slides.pdf   강사용 PDF
```

출력은 `docker run -d --name my-pg -e POSTGRES_PASSWORD=admin1234 postgres:18`로 켠 컨테이너에서 `uv run --with pyte python tools/demo.py`로 만들었어요. 장면 하나만 다시 만들려면 장면 이름을 뒤에 적어요(예: `tools/demo.py g-month`). 15 비교 장의 파이썬 출력은 `uv run count.py`로 실제로 실행한 결과예요.

검사, HTML, PDF를 만드는 공용 도구는 맨 위 [tools/](../tools)에 한 벌만 있어요. 명령은 이 폴더에서 쳐요.

```bash
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/boxcheck.js slides
node ../tools/build_player.js slides sql-aggregate-slides.html
node ../tools/export.js slides sql-aggregate-slides.pdf
```

</details>

---

<!-- curriculum:nav -->

[← 이전: 38 · SQL 3 (조건 조합과 CASE)](../38-sql-case) · [커리큘럼](../README.md)

<!-- /curriculum:nav -->
