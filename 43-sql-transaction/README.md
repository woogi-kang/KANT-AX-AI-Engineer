# 43 · SQL 8 (트랜잭션)

> 문장 여러 개를 `BEGIN`으로 묶고, 마음에 들면 `COMMIT`으로 확정하고, 실수했으면 `ROLLBACK`으로 한꺼번에 되돌려요. 36에서 본 `WHERE` 빠진 `UPDATE` 사고를 이제는 되돌릴 수 있어요. 예제는 38부터 쓰는 스포츠 센터 수업 데이터예요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/43-sql-transaction/sql-transaction-slides.html) | [42 · SQL 7 (다른 표를 보고 넣고, 고치고, 지우기)](../42-sql-insert-select) | 준비 중 |

<!-- /curriculum:top -->

## 학습 목표

- SQL 문장을 DDL, DML, TCL로 나누고, 트랜잭션이 DML을 묶는다는 것을 말해요.
- psql은 `BEGIN`이 없으면 문장마다 바로 저장한다(자동 커밋)는 것을 알고, 고칠 수도 있는 문장 앞에서 `BEGIN`부터 쳐요.
- 프롬프트의 `kant_shop=#`, `kant_shop=*#`, `kant_shop=!#`로 지금 상태를 읽어요.
- `COMMIT`하기 전의 변경은 다른 창에 안 보이고, `\q`로 나가면 버려진다는 것을 두 창으로 확인해요.
- 두 문장이 함께 성공해야 하는 일(강좌 옮기기, 회원 탈퇴)을 `BEGIN`과 `COMMIT` 사이에 묶어요.
- 지우기 전에 같은 `WHERE`로 세고, `BEGIN` 안에서 `DELETE ... RETURNING`으로 줄 수를 맞춘 뒤 `COMMIT`해요.

## 시작하기 전에

| 할 일 | 챕터 |
| --- | :---: |
| 컨테이너 `my-pg`, 데이터베이스 `kant_shop`, `docker exec -i ... < 파일` | 35 |
| `UPDATE`, `DELETE`, `RETURNING`, `WHERE`를 뺀 `UPDATE` 사고 | 36 |
| 기본 키 오류(`duplicate key`), 외래 키, `TRUNCATE` | 37 |
| `AND`와 `OR`의 차이 | 38 |

스포츠 센터 데이터 [sports.sql](./sports.sql)을 받아 터미널에서 그 폴더로 옮긴 뒤 `kant_shop`에 넣어요. 38과 같은 파일이에요. 표 다섯 개를 지우고 새로 만들어서, 앞 챕터에서 바꾼 값도 처음으로 돌아가요.

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

처음 넣을 때는 `NOTICE:  table "enrollments" does not exist, skipping` 같은 줄이 더 나와요. 지울 표가 아직 없다는 안내라서 그대로 두면 돼요. 그다음 psql로 들어가요.

```bash
docker exec -it my-pg psql -U postgres -d kant_shop
```

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 3~6 | `ROLLBACK`이 안 먹히는 사고, 저장 지점과 두 갈래 길 그림, 가장 작은 예제, DDL·DML·TCL |
| 1 · BEGIN, COMMIT, ROLLBACK | 7~11 | 자동 커밋, `*` 프롬프트, `COMMIT` 뒤의 `ROLLBACK`, 한꺼번에 되돌리기, 수업 코드의 함정 |
| 2 · 다른 창에서 보면 | 12~14 | 확정 전에는 안 보여요, 같은 줄은 기다려요, `\q`로 나가면 버려져요 |
| 3 · 모두 되거나 모두 안 되거나 | 15~19 | 강좌 옮기기, 오류와 `!#`, `COMMIT`이 `ROLLBACK`이 되는 때, `DROP TABLE` 되돌리기 |
| 4 · 지우기 전에 확인하기 | 20~21 | 같은 `WHERE`로 먼저 세기, 숫자가 다르면 `ROLLBACK` |
| 5 · 비교와 오류 | 22~24 | Git의 commit, restore와 비교, `WARNING` 두 가지, 메시지 모음 |
| 6 · 실제 상황 | 25~27 | 수강료 인상 미리보기, 정원 늘리기, 회원 탈퇴 |
| 정리 | 28~29 | 언제 쓰는지 표, 한 장 요약 |

## 핵심 개념

```
BEGIN;  ──  UPDATE …  DELETE …  INSERT …  ──┬──  COMMIT;    확정, 다른 창에도 보여요
저장 지점     (아직 내 창에만 있어요)         └──  ROLLBACK;  BEGIN 때로 한꺼번에 돌아가요
```

- psql은 `BEGIN`이 없으면 문장 하나를 칠 때마다 바로 저장해요(자동 커밋). 그래서 `BEGIN` 없이 친 `UPDATE`는 `ROLLBACK`으로 돌아가지 않고 `WARNING:  there is no transaction in progress`가 나와요.
- 프롬프트로 상태를 읽어요.

| 프롬프트 | 뜻 |
| --- | --- |
| `kant_shop=#` | 자동 저장 중 |
| `kant_shop=*#` | 트랜잭션 안, 아직 확정 전 |
| `kant_shop=!#` | 트랜잭션 안에서 오류가 났어요. `ROLLBACK`만 받아요 |

- 트랜잭션 안에서 오류가 나면 그 뒤 문장은 모두 `current transaction is aborted`로 무시돼요. 이때 `COMMIT`을 쳐도 대답은 `ROLLBACK`이에요.
- PostgreSQL은 `DROP TABLE`과 `TRUNCATE`도 `ROLLBACK`으로 되돌려요. 모든 데이터베이스가 그렇지는 않아요(MySQL은 치는 순간 저장돼요).

## 실습

### 1. 같은 실수를 BEGIN 안에서 하고 되돌리기

```sql
BEGIN;
UPDATE courses SET fee = 0;
SELECT course_name, fee FROM courses ORDER BY course_id LIMIT 3;
ROLLBACK;
SELECT course_name, fee FROM courses ORDER BY course_id LIMIT 3;
```

```
kant_shop=# BEGIN;
BEGIN
kant_shop=*# UPDATE courses SET fee = 0;
UPDATE 14
kant_shop=*# SELECT course_name, fee FROM courses ORDER BY course_id LIMIT 3;
   course_name    | fee
------------------+-----
 수영 초급 아침반 |   0
 수영 초급 저녁반 |   0
 수영 중급 새벽반 |   0
(3 rows)

kant_shop=*# ROLLBACK;
ROLLBACK
kant_shop=# SELECT course_name, fee FROM courses ORDER BY course_id LIMIT 3;
   course_name    |  fee
------------------+-------
 수영 초급 아침반 | 70000
 수영 초급 저녁반 | 70000
 수영 중급 새벽반 | 80000
(3 rows)
```

### 2. 창 두 개로 COMMIT 전후 비교하기

터미널을 하나 더 열고 같은 명령(`docker exec -it my-pg psql -U postgres -d kant_shop`)으로 들어가요. 창 1과 창 2에서 아래 순서대로 쳐요.

| 순서 | 창 1 | 창 2 |
| :---: | --- | --- |
| 1 | `BEGIN;` | |
| 2 | `UPDATE courses SET fee = 65000 WHERE course_id = 5;` | |
| 3 | `SELECT fee FROM courses WHERE course_id = 5;` → `65000` | |
| 4 | | `SELECT fee FROM courses WHERE course_id = 5;` → `60000` |
| 5 | `COMMIT;` | |
| 6 | | `SELECT fee FROM courses WHERE course_id = 5;` → `65000` |

4번에서 창 2는 아직 옛 값 60000을 봐요. 창 1이 `COMMIT`한 뒤에야 65000이 보여요.

### 3. 중간에 오류가 나면

```sql
BEGIN;
UPDATE enrollments SET status = '취소', pay_amount = 0 WHERE enrollment_id = 184;
INSERT INTO enrollments VALUES (187, 11, 9, '2026-11', '신청', 75000);
SELECT * FROM enrollments WHERE enrollment_id = 184;
ROLLBACK;
SELECT * FROM enrollments WHERE enrollment_id = 184;
```

```
kant_shop=*# INSERT INTO enrollments VALUES (187, 11, 9, '2026-11', '신청', 75000);
ERROR:  duplicate key value violates unique constraint "enrollments_pkey"
DETAIL:  Key (enrollment_id)=(187) already exists.
kant_shop=!# SELECT * FROM enrollments WHERE enrollment_id = 184;
ERROR:  current transaction is aborted, commands ignored until end of transaction block
kant_shop=!# ROLLBACK;
ROLLBACK
kant_shop=# SELECT * FROM enrollments WHERE enrollment_id = 184;
 enrollment_id | member_id | course_id | enroll_month | status | pay_amount
---------------+-----------+-----------+--------------+--------+------------
           184 |        11 |        13 | 2026-11      | 신청   |     150000
(1 row)
```

187번은 이미 있어서 오류가 나고 프롬프트가 `!#`로 바뀌어요. `ROLLBACK`하면 첫 문장의 취소도 같이 되돌아가요.

### 4. 지우기 전에 세고, BEGIN 안에서 지우기

```sql
SELECT COUNT(*) FROM enrollments WHERE enroll_month = '2026-11' AND status = '취소';
BEGIN;
DELETE FROM enrollments
WHERE enroll_month = '2026-11' AND status = '취소'
RETURNING enrollment_id, member_id, course_id;
COMMIT;
```

```
 count
-------
     6
(1 row)
...
(6 rows)

DELETE 6
kant_shop=*# COMMIT;
COMMIT
```

처음에 센 6과 `DELETE 6`이 같을 때만 `COMMIT`해요. 숫자가 다르면 `ROLLBACK`을 쳐요. 실습을 처음부터 다시 하려면 `sports.sql`을 다시 넣어요.

## 명령어 요약

| 명령 | 하는 일 |
| --- | --- |
| `BEGIN;` | 저장 지점을 만들어요. 프롬프트에 `*`가 붙어요 |
| `COMMIT;` | `BEGIN` 뒤의 변경을 확정해요. 다른 창에도 보여요 |
| `ROLLBACK;` | `BEGIN` 뒤의 문장을 모두 되돌려요 |
| `SELECT COUNT(*) FROM 표 WHERE 조건;` | 지우기 전에 같은 조건으로 줄 수를 세요 |
| `DELETE FROM 표 WHERE 조건 RETURNING 열;` | `BEGIN` 안에서 지우고 지운 줄을 봐요 |
| `UPDATE ... RETURNING 열;` 뒤 `ROLLBACK;` | 바뀐 값을 미리 보고 되돌려요 |

## 문제 해결

| 메시지 | 원인 | 해결 |
| --- | --- | --- |
| `WARNING:  there is no transaction in progress` | `BEGIN` 없이 `ROLLBACK`이나 `COMMIT`을 쳤어요 | 이미 저장됐어요. 원래 값으로 다시 `UPDATE`하고, 다음엔 `BEGIN`부터 쳐요 |
| `WARNING:  there is already a transaction in progress` | `BEGIN` 상태에서 `BEGIN`을 또 쳤어요 | 그대로 이어서 쳐요 |
| `ERROR:  current transaction is aborted, commands ignored until end of transaction block` | 앞 문장의 오류로 트랜잭션이 실패했어요(`!#`) | `ROLLBACK;` 뒤 고쳐서 처음부터 |
| `COMMIT`을 쳤는데 `ROLLBACK` | 실패한 트랜잭션은 확정이 안 돼요 | 오류를 고쳐 다시 해요 |
| 다른 창의 `UPDATE`가 대답이 없어요 | `BEGIN`한 창이 같은 줄을 고치는 중이에요 | 그 창에서 `COMMIT`이나 `ROLLBACK`을 쳐요 |
| 나갔다 오니 바꾼 값이 없어요 | `COMMIT` 없이 `\q`로 나갔어요 | 끝내기 전에 프롬프트의 `*`를 확인해요 |

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
  duo.py           psql 두 개를 동시에 띄워 두 창 장면을 만드는 도우미
  ptyrun.py        psql을 터미널처럼 실행하는 도우미 (37에서 가져옴)
  sports.sql       demo.py가 장면마다 넣는 데이터
  out.json         슬라이드에 넣은 실제 출력
sql-transaction-slides.html   배포용 HTML
sql-transaction-slides.pdf    강사용 PDF
```

출력을 다시 만들려면 `uv run --with pyte python tools/demo.py`를 쳐요. 스크립트가 `my-pg` 컨테이너를 새로 켜고 장면마다 데이터를 다시 넣어요. 장면 이름을 붙이면(`... demo.py w-wait`) 그 장면만 다시 실행해요.

검사, HTML, PDF를 만드는 공용 도구(`check.js`, `build_player.js`, `export.js`)는 맨 위 [tools/](../tools)에 한 벌만 있어요. 명령은 이 폴더에서 쳐요.

```bash
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/boxcheck.js slides
node ../tools/build_player.js slides sql-transaction-slides.html
node ../tools/export.js slides sql-transaction-slides.pdf
```

</details>

---

<!-- curriculum:nav -->

[← 이전: 42 · SQL 7 (다른 표를 보고 넣고, 고치고, 지우기)](../42-sql-insert-select) · [커리큘럼](../README.md)

<!-- /curriculum:nav -->
