# 40 · SQL 5 (UNION과 JOIN으로 결과 합치기)

> 지금까지는 표 하나에서만 골라 봤어요. 신청 표에는 회원 번호만 있어서 이름을 보려면 회원 표에 한 번 더 물어봐야 했어요. 이번에는 두 결과를 하나로 합쳐요. 결과를 위아래로 쌓는 `UNION`과, 두 표를 옆으로 붙이는 `JOIN`이에요. 예제는 수업에서 쓴 체육 센터 표 다섯 개예요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/40-sql-union-join/sql-union-join-slides.html) | [39 · SQL 4 (집계 함수와 GROUP BY)](../39-sql-aggregate) | [41 · SQL 6 (서브쿼리)](../41-sql-subquery) |

<!-- /curriculum:top -->

## 학습 목표

- `UNION ALL`로 두 SELECT의 결과를 위아래로 잇고, `UNION`으로 겹친 줄을 하나만 남겨요.
- `'강사' AS 구분`처럼 표에 없는 글자를 적어서 어느 쪽 줄인지 표시해요.
- 위아래로 이으려면 열 개수와 같은 자리의 자료형이 같아야 한다는 것을 실제 오류로 확인해요. `ORDER BY`는 맨 끝에 한 번만 적어요.
- `FROM enrollments e`처럼 표에 별명을 붙이고, `e.member_id`처럼 어느 표의 열인지 밝혀 적어요.
- `JOIN 표 ON 조건`으로 번호가 같은 줄끼리 옆으로 붙이고, 표 세 개를 `JOIN` 두 번으로 붙여요.
- `JOIN`, `LEFT JOIN`, `FULL JOIN`이 짝이 없는 줄을 어디까지 남기는지 비교해요.
- `LEFT JOIN ... WHERE 열 IS NULL`로 짝이 없는 줄만 찾아요.

## 시작하기 전에

| 할 일 | 챕터 |
| --- | :---: |
| `postgres:18` 컨테이너 켜기, `psql`로 들어가기, `\dt` `\q` | 34 |
| 컨테이너 `my-pg`, 데이터베이스 `kant_shop`, `docker cp`, `psql -f` | 35 |
| `SELECT`, `WHERE`, `AS`, `ORDER BY`, `IS NULL`, `DISTINCT`, `COUNT(*)` | 36 |
| 기본 키와 외래 키(`REFERENCES`) | 37 |
| 13의 리스트 더하기, 15의 딕셔너리와 `get()`, 16의 집합 합치기 | 13, 15, 16 |

35에서 켠 `my-pg` 컨테이너에 수업 표를 넣고 시작해요. 이 폴더의 [sports.sql](sports.sql)을 내 폴더에 받아 두고 그 폴더에서 쳐요. 38~41이 같은 파일을 써요. 이미 넣었으면 다시 넣지 않아도 돼요.

```bash
docker cp sports.sql my-pg:/tmp/
docker exec -it my-pg psql -U postgres -d kant_shop -f /tmp/sports.sql
docker exec -it my-pg psql -U postgres -d kant_shop
```

| 표 | 별명 | 줄 수 | 열 |
| --- | :---: | :---: | --- |
| `members` | m | 40 | `member_id`, `name`, `region`, `phone`, … |
| `enrollments` | e | 187 | `enrollment_id`, `member_id`, `course_id`, `enroll_month`, `status`, `pay_amount` |
| `courses` | c | 14 | `course_id`, `course_name`, `sport_id`, `instructor_id`, `fee`, … |
| `instructors` | i | 8 | `instructor_id`, `name`, `phone`, `sport_id` |
| `sports` | | 5 | 오늘은 안 써요 |

5번 강좌 아쿠아로빅은 강사가 없고(`instructor_id`가 NULL), 8번 윤태호 강사는 맡은 강좌가 없어요. 40번 채윤서 회원은 신청이 없어요. 짝이 없는 줄을 볼 때 이 셋이 나와요.

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1–6 | 표지, 오늘의 순서, 두 번 묻던 장면, 쌓기와 붙이기 그림, 수업 표 다섯 개와 넣는 법, 가장 짧은 예제 |
| 1. 위아래로 쌓기 (UNION) | 7–12 | `UNION ALL`, 세 달 잇기, `UNION`, 구분 열 붙이기, 열 개수와 자료형, 맨 끝의 `ORDER BY` |
| 2. 옆으로 붙이기 (JOIN) | 13–18 | 표 별명, `JOIN ... ON` 읽기, 줄이 짝을 찾는 그림, 한 줄이 여러 줄과 짝, 짝 없는 줄은 빠져요, 표 세 개 |
| 3. 짝이 없어도 남기기 | 19–23 | `LEFT JOIN`과 NULL, 왼쪽은 먼저 적은 표, `FULL JOIN`, 세 JOIN 비교, 짝 없는 줄 찾기 |
| 4. 앞에서 배운 것과 비교 | 24–25 | 파이썬 리스트 `+`, 집합 `\|`, 딕셔너리 찾기와 `get()`, UNION과 JOIN 언제 쓰나 |
| 5. 자주 나는 오류와 함정 | 26–30 | `ambiguous`, 별명 대신 표 이름, ON 빠짐, 잘못 짝지은 ON, 열 없는 SELECT, LEFT JOIN 뒤 WHERE |
| 6. 실제 상황 예제 | 31–33 | 강좌 명단, 강사와 수강생 연락처 한 목록, 짝이 없는 강좌와 강사 점검 |
| 정리 | 34–35 | 언제 무엇을 쓰는지, 오늘 친 문장 모양 |

## 핵심 개념

### UNION은 위아래로, JOIN은 옆으로

| | `UNION` · `UNION ALL` | `JOIN` · `LEFT JOIN` · `FULL JOIN` |
| --- | --- | --- |
| 방향 | 위아래로 쌓기 | 옆으로 붙이기 |
| 늘어나는 것 | 줄 | 열 |
| 맞춰야 하는 것 | 열 개수와 같은 자리 자료형 | `ON` 조건(보통 외래 키) |
| 겹친 값 | `UNION`은 지우고 `UNION ALL`은 남겨요 | 짝마다 한 줄씩 만들어요 |
| 짝이 없는 줄 | 해당 없음 | `JOIN`은 빼고, `LEFT`·`FULL`은 NULL로 채워요 |

### UNION ALL과 UNION

| | 겹친 줄 | 파이썬으로 치면 |
| --- | --- | --- |
| `UNION ALL` | 그대로 남겨요 | 13의 리스트 더하기 `[27, 17] + [11, 17]` |
| `UNION` | 하나만 남겨요 | 16의 집합 합치기 `{27, 17} \| {11, 17}` |

겹칠 일이 없거나 건수를 세야 하면 `UNION ALL`을 써요. 열 이름은 첫 SELECT 것을 따르고, `ORDER BY`는 마지막 SELECT 뒤에 한 번만 적어서 합친 결과 전체를 세워요.

### 세 JOIN은 짝이 없는 줄을 어디까지 남기느냐만 달라요

`courses c`에 `instructors i`를 `c.instructor_id = i.instructor_id`로 붙이면 이렇게 나와요.

| 문장 | 결과 | 짝이 없는 줄 |
| --- | :---: | --- |
| `courses JOIN instructors` | 13줄 | 아쿠아로빅 빠짐, 윤태호 빠짐 |
| `courses LEFT JOIN instructors` | 14줄 | 아쿠아로빅 남음(강사 칸 NULL) |
| `courses FULL JOIN instructors` | 15줄 | 둘 다 남음(빈 쪽은 NULL) |

`JOIN`은 `INNER JOIN`을, `FULL JOIN`은 `FULL OUTER JOIN`을 줄인 말이에요. `RIGHT JOIN`이라는 반대 방향도 있지만, 표 순서를 바꾼 `LEFT JOIN`과 같아서 수업에서는 `LEFT JOIN`으로 써요.

## 실습

출력은 `tools/demo.py`로 실제 `postgres:18`(18.7)을 실행한 결과예요. 줄 순서는 `ORDER BY`가 없으면 내 화면과 다를 수 있어요.

### 1. 두 달 신청자를 위아래로 잇기

```sql
SELECT member_id
FROM enrollments
WHERE course_id = 4 AND enroll_month = '2026-09'
UNION ALL
SELECT member_id
FROM enrollments
WHERE course_id = 4 AND enroll_month = '2026-10';
```

```
 member_id
-----------
        27
        17
        11
        19
        35
        17
        20
(7 rows)
```

`UNION ALL`을 `UNION`으로 바꾸면 두 번 나온 17이 하나만 남아요. 11월까지 세 달을 `UNION`으로 이으면 12줄이 10줄이 돼요.

### 2. 구분 열 붙이기

```sql
SELECT '강사' AS 구분, name, phone
FROM instructors
WHERE sport_id = 4
UNION ALL
SELECT '회원' AS 구분, name, phone
FROM members
WHERE region = '영등포구';
```

강사 2줄 아래에 회원 12줄이 이어지고, 맨 앞 칸에 `강사`, `회원`이 붙어요.

### 3. 신청 표에 회원 이름 붙이기

```sql
SELECT e.member_id, e.course_id, m.name
FROM enrollments e
JOIN members m ON e.member_id = m.member_id
WHERE e.course_id = 6 AND e.enroll_month = '2026-11';
```

```
 member_id | course_id |  name
-----------+-----------+--------
         3 |         6 | 박도현
        14 |         6 | 신유찬
        24 |         6 | 양다인
        30 |         6 | 노채원
(4 rows)
```

### 4. 강좌 표에 강사 이름 붙이기 (JOIN, LEFT JOIN, FULL JOIN)

```sql
SELECT c.course_id, c.course_name, i.name
FROM courses c
LEFT JOIN instructors i ON c.instructor_id = i.instructor_id
ORDER BY c.course_id;
```

```
 course_id |    course_name     |  name
-----------+--------------------+--------
         1 | 수영 초급 아침반   | 박서연
         2 | 수영 초급 저녁반   | 이도윤
         3 | 수영 중급 새벽반   | 박서연
         4 | 수영 고급반        | 이도윤
         5 | 아쿠아로빅         |
         6 | 헬스 PT 입문       | 김하준
         ...
(14 rows)
```

`LEFT JOIN`을 `JOIN`으로 바꾸면 아쿠아로빅이 빠져서 13줄, `FULL JOIN`으로 바꾸면 맨 아래에 윤태호가 더해져서 15줄이에요. 세 문장의 줄 수를 `COUNT(*)`로 세어 봐도 13, 14, 15예요.

### 5. 한 번도 신청하지 않은 회원 찾기

```sql
SELECT m.member_id, m.name, m.phone
FROM members m
LEFT JOIN enrollments e ON m.member_id = e.member_id
WHERE e.enrollment_id IS NULL;
```

```
 member_id |  name  | phone
-----------+--------+-------
        40 | 채윤서 |
(1 row)
```

### 6. 짝이 없는 강좌와 강사를 한 목록으로

```sql
SELECT '강사 없는 강좌' AS 구분, c.course_name AS 이름
FROM courses c
LEFT JOIN instructors i ON c.instructor_id = i.instructor_id
WHERE i.instructor_id IS NULL
UNION ALL
SELECT '강좌 없는 강사', i.name
FROM instructors i
LEFT JOIN courses c ON i.instructor_id = c.instructor_id
WHERE c.course_id IS NULL;
```

```
      구분      |    이름
----------------+------------
 강사 없는 강좌 | 아쿠아로빅
 강좌 없는 강사 | 윤태호
(2 rows)
```

## 명령어 요약

| 문장 | 하는 일 |
| --- | --- |
| `SELECT ... UNION ALL SELECT ...` | 두 결과를 그대로 위아래로 이어요 |
| `SELECT ... UNION SELECT ...` | 이은 뒤 겹친 줄을 하나만 남겨요 |
| `SELECT '강사' AS 구분, ...` | 모든 줄에 같은 글자를 붙여 어느 쪽 줄인지 표시해요 |
| `... UNION ALL SELECT ... ORDER BY 열;` | 합친 결과 전체를 세워요. 맨 끝에 한 번만 |
| `FROM enrollments e` | 표에 별명 e를 붙여요(`AS e`도 같아요) |
| `JOIN members m ON e.member_id = m.member_id` | 번호가 같은 줄끼리 옆으로 붙여요. 짝이 없으면 빠져요 |
| `JOIN 표 ... JOIN 표 ...` | 표 세 개를 차례로 붙여요 |
| `LEFT JOIN 표 ON ...` | 먼저 적은 표의 줄을 다 남기고, 짝이 없으면 NULL |
| `FULL JOIN 표 ON ...` | 양쪽 표의 줄을 다 남겨요 |
| `LEFT JOIN 표 b ON ... WHERE b.키 IS NULL` | 짝이 없는 줄만 골라요 |

## 문제 해결

| 메시지 | 원인 | 해결 |
| --- | --- | --- |
| `ERROR:  column reference "member_id" is ambiguous` | 두 표에 다 있는 열을 표 없이 적었어요 | `e.member_id`처럼 별명을 붙여요 |
| `ERROR:  invalid reference to FROM-clause entry for table "members"` | `FROM members m`이라고 별명을 붙이고 `members.name`이라고 적었어요 | HINT대로 `m.name`이라고 적어요 |
| `ERROR:  syntax error at or near ";"` (JOIN 뒤) | `JOIN` 뒤에 `ON` 조건을 빠뜨렸어요 | `ON c.instructor_id = i.instructor_id`를 적어요 |
| `ERROR:  each UNION query must have the same number of columns` | 위아래 SELECT의 열 개수가 달라요 | 열 개수를 맞춰요 |
| `ERROR:  UNION types character varying and integer cannot be matched` | 같은 자리의 자료형이 달라요 | 같은 자리에 같은 종류의 열을 적어요 |
| `ERROR:  syntax error at or near "UNION"` | 첫 SELECT 뒤에 `ORDER BY`를 적었어요 | `ORDER BY`는 마지막 SELECT 뒤에 한 번만 |
| 오류 없이 이름 칸이 NULL투성이 | `ON e.member_id = c.course_id`처럼 뜻이 다른 열을 짝지었어요 | `ON e.course_id = c.course_id`처럼 같은 뜻의 열끼리 적어요 |
| `--`만 나오고 칸이 없어요 | `SELECT FROM ...`처럼 열 이름을 빠뜨렸어요 | `SELECT m.member_id, m.name, ...`처럼 열을 적어요 |
| `LEFT JOIN`인데 NULL 줄이 사라졌어요 | `WHERE i.name <> '박서연'`처럼 오른쪽 표 열을 비교해서 NULL 줄이 빠졌어요 | `OR i.name IS NULL`을 더하고 괄호로 묶어요 |

## 강사용

<details>
<summary>수업 코드에서 고친 두 곳</summary>

- `LEFT JOIN courses c ON e.member_id = c.course_id`는 회원 번호와 강좌 번호를 짝지은 실수예요. 덱 28쪽에서 그대로 실행한 결과를 보여 주고, `ON e.course_id = c.course_id`로 고친 문장을 31쪽 강좌 명단에 썼어요.
- `SELECT FROM members m FULL OUTER JOIN enrollments e ...`는 열 이름이 빠져서 칸이 없는 줄만 나와요. 29쪽에서 실제 결과(`--`)와 열을 적은 문장을 나란히 보여 줘요.

</details>

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
sports.sql         수업 표 다섯 개 (38~41 공용)
tools/
  gen.py           이 챕터의 장 생성
  demo.py          슬라이드에 넣은 출력을 실제 postgres:18로 실행 (out.json)
  ptyrun.py        psql을 터미널 화면처럼 실행하는 도우미
sql-union-join-slides.html   배포용 HTML
sql-union-join-slides.pdf    강사용 PDF
```

검사, HTML, PDF를 만드는 공용 도구(`check.js`, `boxcheck.js`, `playshots.js`, `build_player.js`, `export.js`)는 맨 위 [tools/](../tools)에 한 벌만 있어요. 명령은 이 폴더에서 쳐요.

```bash
sudo -n dockerd &                       # 클라우드 컨테이너에서 한 번
uv run --with pyte python tools/demo.py # 출력 다시 만들기
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/boxcheck.js slides
node ../tools/build_player.js slides sql-union-join-slides.html
node ../tools/export.js slides sql-union-join-slides.pdf
```

</details>

---

<!-- curriculum:nav -->

[← 이전: 39 · SQL 4 (집계 함수와 GROUP BY)](../39-sql-aggregate) · [커리큘럼](../README.md) · [다음: 41 · SQL 6 (서브쿼리) →](../41-sql-subquery)

<!-- /curriculum:nav -->
