# 38 · SQL 3 (조건 조합과 CASE)

> 36에서 `WHERE`로 줄을 고르고 `ORDER BY`로 세웠어요. 이번에는 조건 여러 개를 섞을 때 괄호가 왜 필요한지 보고, `CASE`로 줄마다 할인이나 청소년 같은 값을 붙이고, 기준 여러 개와 빈칸(`NULL`)의 자리까지 정해서 줄을 세워요. 예제는 수업에서 쓴 체육 센터 데이터베이스(강좌, 회원, 수강 신청)예요. 39~41도 같은 표를 써요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/38-sql-case/sql-case-slides.html) | [37 · SQL 2 (제약 조건으로 표 설계하기)](../37-sql-constraints) | [41 · SQL 6 (서브쿼리)](../41-sql-subquery) |

<!-- /curriculum:top -->

## 학습 목표

- `AND`와 `OR`를 섞은 `WHERE`에서 괄호가 있을 때와 없을 때 결과가 왜 다른지 말해요.
- `NOT IN`, `NOT LIKE`, `NOT (조건)`으로 조건을 뒤집어요.
- `CASE WHEN ... THEN ... ELSE ... END AS 이름`으로 줄마다 값을 붙인 새 열을 만들어요.
- `WHEN`을 여러 개 쓸 때 좁은 조건부터 적고, `ELSE`가 없으면 `NULL`이 된다는 것을 알아요.
- `ORDER BY`에 기준을 여러 개 적고, 기준마다 `ASC`와 `DESC`를 따로 붙여요.
- `NULL`이 가장 큰 값처럼 선다는 것을 알고, `NULLS LAST`와 `NULLS FIRST`로 자리를 정해요.

## 시작하기 전에

| 할 일 | 챕터 |
| --- | :---: |
| `postgres:18` 컨테이너 켜기, `psql`로 들어가기, `\dt` `\q` | 34 |
| 컨테이너 `my-pg`, 데이터베이스 `kant_shop`, `docker cp`, `psql -f` | 35 |
| `WHERE`(`AND` `OR` `IN` `LIKE` `IS NULL`), `AS`, `ORDER BY`, `TIME` 자료형 | 36 |
| 파이썬 `if`, `elif`, `else`와 한 줄 `if else` | 17 |

35에서 켠 `my-pg` 컨테이너를 그대로 써요. 컨테이너가 없으면 먼저 켜요.

```bash
docker run -d --name my-pg -e POSTGRES_PASSWORD=admin1234 -p 5432:5432 -v pgdata:/var/lib/postgresql postgres:18
docker exec -it my-pg psql -U postgres -c "CREATE DATABASE kant_shop;"
```

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1–6 | 표지, 오늘의 순서, 수영만 물었는데 다른 종목이 섞인 결과, SELECT 안에서 오늘 배울 곳과 처리 순서, 예제 표 넣기, `courses` 표 |
| 1. 조건 섞기 | 7–11 | 줄마다 참과 거짓, `AND`가 `OR`보다 먼저, 괄호로 `OR` 묶기, 괄호 안을 `AND`로, `NOT` |
| 2. CASE로 값 붙이기 | 12–19 | `CASE` 한 줄, 부분 이름, `WHEN` 여러 개, 순서가 틀린 `WHEN`, `ELSE`가 없으면 `NULL`, `IS NULL`을 조건으로, 계산한 값, 17의 `if`와 비교 |
| 3. 여러 기준으로 줄 세우기 | 20–24 | 앞 기준이 같을 때만 뒤 기준, 기준마다 방향, `ORDER BY CASE`로 난이도 순서, `NULL`의 자리, `NULLS LAST` `NULLS FIRST` |
| 4. 자주 나는 오류와 함정 | 25–28 | 빠진 `END`, `THEN`과 `ELSE`의 자료형, `WHERE`에서 `AS` 이름, 한글 정렬과 `COLLATE "C"` |
| 5. 실제 상황 예제 | 29–31 | 회원 요금 안내, 강좌 시간표, 문자 보낼 명단 |
| 정리 | 32–34 | 39에서 배울 것, 막히면 이렇게 풀어요, 한 장 요약 |

## 핵심 개념

### AND가 OR보다 먼저 묶여요

곱셈이 덧셈보다 먼저인 것처럼, 괄호가 없으면 `AND`를 먼저 묶어요.

```
WHERE sport_id = 1 AND level = '초급' OR start_time < '09:00'
      └──────── 먼저 묶임 ────────┘ OR 9시 전인 강좌 전부
```

"수영 강좌 중에 초급이거나 9시 전"을 원하면 `OR` 쪽을 괄호로 묶어요.

```sql
WHERE sport_id = 1 AND (level = '초급' OR start_time < '09:00')
```

### CASE는 줄마다 위에서부터 물어봐요

```sql
CASE WHEN birth_year <= 1960 THEN '할인'
     WHEN birth_year >= 2000 THEN '청소년'
     ELSE '일반'
END AS 요금
```

| 순서 | 묻는 것 | 맞으면 |
| --- | --- | --- |
| 1 | `birth_year <= 1960`? | `'할인'`을 붙이고 끝 |
| 2 | `birth_year >= 2000`? | `'청소년'`을 붙이고 끝 |
| 3 | 둘 다 아니면 | `ELSE`의 `'일반'` |

- 처음 맞는 `WHEN` 하나만 써요. 넓은 조건(`birth_year < 2000`)을 위에 두면 아래 `WHEN`은 보지도 않아요.
- `ELSE`를 빼면 아무 `WHEN`에도 안 맞는 줄은 `NULL`(빈칸)이 돼요.
- `THEN`과 `ELSE` 값은 모두 글자이거나 모두 숫자여야 해요.

### ORDER BY 기준은 왼쪽부터 차례로

- `ORDER BY fee DESC, course_name`은 수강료가 비싼 것부터 세우고, 수강료가 같은 줄끼리만 이름순으로 세워요.
- `DESC`는 바로 앞 기준 하나에만 붙어요. 방향을 안 적은 기준은 `ASC`(작은 것부터)예요.
- PostgreSQL에서 `NULL`은 가장 큰 값처럼 서요. 오름차순이면 맨 뒤, `DESC`면 맨 앞이에요. `NULLS LAST`, `NULLS FIRST`로 바꿔요.

### PostgreSQL이 처리하는 순서

| 적는 순서 | 처리 순서 |
| --- | --- |
| `SELECT` → `FROM` → `WHERE` → `ORDER BY` | `FROM` → `WHERE` → `SELECT` → `ORDER BY` |

`WHERE`는 `SELECT`보다 먼저 돌아서 `AS`로 붙인 이름을 몰라요. `ORDER BY`는 `SELECT` 뒤라서 `AS` 이름을 쓸 수 있어요.

## 실습

### 1. 예제 표 넣기

이 폴더의 [sports.sql](sports.sql)을 받아서, 그 파일이 있는 폴더에서 쳐요. 표 다섯 개(`sports`, `instructors`, `courses`, `members`, `enrollments`)가 만들어져요.

```bash
docker cp sports.sql my-pg:/tmp/
docker exec -it my-pg psql -U postgres -d kant_shop -f /tmp/sports.sql
docker exec -it my-pg psql -U postgres -d kant_shop
```

처음에는 지울 표가 없다는 `NOTICE`가 다섯 줄 나오고, `CREATE TABLE` 다섯 줄과 `INSERT 0 5`부터 `INSERT 0 187`까지 나와요. 몇 번 다시 넣어도 처음 상태로 돌아가요.

### 2. 괄호 없이, 괄호 넣고

```sql
SELECT course_name, level, start_time
FROM courses
WHERE sport_id = 1 AND level = '초급' OR start_time < '09:00';
```

```
   course_name    | level | start_time
------------------+-------+------------
 수영 초급 아침반 | 초급  | 06:30:00
 수영 초급 저녁반 | 초급  | 19:00:00
 수영 중급 새벽반 | 중급  | 06:00:00
 아쿠아로빅       | 초급  | 10:00:00
 헬스 PT 입문     | 초급  | 07:00:00
 아침 요가        | 초급  | 08:00:00
 테니스 중급 레슨 | 중급  | 07:30:00
(7 rows)
```

```sql
SELECT course_name, level, start_time
FROM courses
WHERE sport_id = 1
AND (level = '초급' OR start_time < '09:00');
```

```
   course_name    | level | start_time
------------------+-------+------------
 수영 초급 아침반 | 초급  | 06:30:00
 수영 초급 저녁반 | 초급  | 19:00:00
 수영 중급 새벽반 | 중급  | 06:00:00
 아쿠아로빅       | 초급  | 10:00:00
(4 rows)
```

### 3. CASE로 요금 등급 붙이기

```sql
SELECT name, birth_year,
       CASE WHEN birth_year <= 1960 THEN '할인'
            WHEN birth_year >= 2000 THEN '청소년'
            ELSE '일반'
       END AS 요금
FROM members
WHERE region = '마포구'
ORDER BY birth_year, name;
```

```
  name  | birth_year |  요금
--------+------------+--------
 전소율 |       1958 | 할인
 최지아 |       1975 | 일반
 정하은 |       1980 | 일반
 하동건 |       1981 | 일반
 임준서 |       1990 | 일반
 손현우 |       1997 | 일반
 권나연 |       1998 | 일반
 고은채 |       2000 | 청소년
 황민서 |       2001 | 청소년
 안태윤 |       2004 | 청소년
 백준혁 |       2007 | 청소년
(11 rows)
```

### 4. 빈칸의 자리 정하기

```sql
SELECT name, email FROM members WHERE region = '구로구' ORDER BY email DESC NULLS LAST, name;
```

```
  name  |      email
--------+------------------
 주경자 | user34@gmail.com
 신유찬 | user14@gmail.com
 서지민 | user13@gmail.com
 강시우 | user06@naver.com
 김민준 | user01@gmail.com
 박도현 |
 양다인 |
(7 rows)
```

`NULLS LAST`를 빼고 쳐 보면 박도현, 양다인이 맨 앞으로 와요.

### 5. 더 해 보기

- 첫 `WHEN`을 `birth_year < 2000 THEN '일반'`으로 바꿔서 1958년생 전소율이 무엇을 받는지 봐요.
- 강좌를 난이도(초급, 중급, 고급) 순서로 세워요. `ORDER BY level`과 `ORDER BY CASE WHEN level = '초급' THEN 1 WHEN level = '중급' THEN 2 ELSE 3 END`를 비교해요.
- 시작 시각으로 새벽(7시 전), 오전(12시 전), 오후(18시 전), 저녁을 붙인 시간표를 만들어요.

## 명령어 요약

| 명령 | 하는 일 |
| --- | --- |
| `docker exec -it my-pg psql -U postgres -d kant_shop -f /tmp/sports.sql` | 예제 표 다섯 개를 한 번에 넣기 |
| `WHERE a AND (b OR c)` | `OR`를 먼저 묶기 |
| `NOT IN (...)`, `NOT LIKE '...'`, `NOT (조건)` | 조건 뒤집기 |
| `CASE WHEN 조건 THEN 값 ... ELSE 값 END AS 이름` | 줄마다 조건에 맞는 값을 붙인 새 열 |
| `ORDER BY a DESC, b` | `a`로 세우고, `a`가 같으면 `b`로 |
| `ORDER BY CASE WHEN ... THEN 1 ... END` | 원하는 순서로 번호를 매겨 세우기 |
| `ORDER BY 열 DESC NULLS LAST` | 빈칸을 맨 뒤로 |
| `ORDER BY 열 NULLS FIRST` | 빈칸을 맨 앞으로 |
| `ORDER BY 열 COLLATE "C"` | 한글을 가나다 순으로 세우기 |

## 문제 해결

| 메시지 | 원인 | 해결 |
| --- | --- | --- |
| 결과에 다른 종목이 섞여 나와요 | `AND`와 `OR`를 괄호 없이 섞었어요 | `OR` 쪽을 괄호로 묶어요 |
| `ERROR:  syntax error at or near "AS"` | `CASE`를 `END`로 닫지 않았어요 | `AS` 앞에 `END`를 넣어요 |
| `ERROR:  invalid input syntax for type integer: "고가"` | `THEN`과 `ELSE` 값의 자료형이 달라요 | 둘 다 글자(`'-'`)나 둘 다 숫자로 맞춰요 |
| `ERROR:  column "요금" does not exist` | `WHERE`에서 `AS` 이름을 썼어요 | 원래 열로 조건을 적어요(`WHERE birth_year <= 1960`) |
| `CASE` 결과가 모두 같은 값이에요 | 넓은 `WHEN`을 위에 적었어요 | 좁은 조건부터 적어요 |
| `CASE` 열에 빈칸이 생겨요 | `ELSE`를 안 적었어요 | `ELSE 값`을 적어요 |
| `DESC`로 세웠는데 빈칸이 맨 앞에 와요 | `NULL`은 가장 큰 값처럼 서요 | `NULLS LAST`를 붙여요 |
| 한글 이름이 가나다 순이 아니에요 | 데이터베이스 기본 정렬 규칙(`en_US.utf8`) 때문이에요 | 그 기준 뒤에 `COLLATE "C"`를 붙여요 |

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json             슬라이드 순서와 파트 구분
  *.html                한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
sports.sql              38~41이 같이 쓰는 예제 데이터베이스 (표 다섯 개)
tools/
  make_sports.py        sports.sql을 만드는 스크립트 (seed 38)
  demo.py               슬라이드의 SQL을 실제 postgres:18에서 실행해 out.json에 저장
  ptyrun.py             psql을 터미널처럼 띄워서 화면을 그대로 받기
  gen.py                이 챕터의 장 생성 (out.json을 읽어요)
sql-case-slides.html    배포용 HTML
sql-case-slides.pdf     강사용 PDF
```

출력은 실제 Docker와 `postgres:18`(PostgreSQL 18.7)로 만들었어요. 명령은 이 폴더에서 쳐요.

```bash
sudo -n dockerd &                       # 클라우드 컨테이너에서 한 번
uv run --with pyte python tools/demo.py
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/build_player.js slides sql-case-slides.html
node ../tools/export.js slides sql-case-slides.pdf
```

`kant_shop`의 기본 정렬 규칙이 `en_US.utf8`이라 `ORDER BY fee DESC, course_name`에서 테니스 입문이 수영 고급반보다 먼저 나와요. 학생 화면도 같게 나오니 4파트의 함정 장으로 넣었어요.

</details>

---

<!-- curriculum:nav -->

[← 이전: 37 · SQL 2 (제약 조건으로 표 설계하기)](../37-sql-constraints) · [커리큘럼](../README.md) · [다음: 41 · SQL 6 (서브쿼리) →](../41-sql-subquery)

<!-- /curriculum:nav -->
