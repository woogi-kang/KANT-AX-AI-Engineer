# 36 · SQL 1 (골라 보기, 고치기, 자료형)

> 34에서 PostgreSQL을 켜고 표 하나를 만들어 전부 꺼내 봤어요. 이번에는 35 수업의 `my-pg` 컨테이너와 `kant_shop` 데이터베이스를 그대로 써서, 열마다 자료형을 고르고 표에서 필요한 줄만 골라 보고 고치고 지워요. 마지막에 회원 목록으로 실제 상황 예제를 풀어요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/36-sql-basics/sql-basics-slides.html) · [PDF 받기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/36-sql-basics/sql-basics-slides.pdf) | [35 · Docker 5 (명령어 한눈에 보기)](../35-docker-cli) | [37 · SQL 2 (제약 조건으로 표 설계하기)](../37-sql-constraints) |

<!-- /curriculum:top -->

## 학습 목표

- 글자(`CHAR`, `VARCHAR`, `TEXT`), 정수(`SMALLINT`, `INTEGER`, `BIGINT`), 소수(`NUMERIC`, `REAL`, `DOUBLE PRECISION`), `BOOLEAN`, 날짜와 시간 자료형의 차이를 말하고 열에 맞게 골라요.
- `INSERT`로 여러 줄을 한 번에 넣고, 안 적은 열이 `NULL`(모름)로 비는 것을 봐요.
- `WHERE`에 비교(`=`, `<>`, `>=`), `AND`, `OR`, `IN`, `BETWEEN`, `LIKE`, `ILIKE`, `IS NULL`을 써서 줄을 골라요.
- `AS`로 결과 열에 새 이름을 붙이고, `price * 3`처럼 계산한 값을 열로 꺼내요.
- `DISTINCT`로 겹치는 줄을 하나만 남기고, `COUNT(*)`로 맞는 줄이 몇 개인지 세요.
- `ORDER BY`로 줄을 세우고 `LIMIT`, `OFFSET`으로 잘라요.
- `UPDATE ... SET ... WHERE`로 값을 고치고 `DELETE FROM ... WHERE`로 줄을 지워요.
- `RETURNING`으로 바뀐 줄을 바로 보고, `DROP ... IF EXISTS`로 오류 없이 지워요.
- `WHERE`를 빼면 모든 줄이 바뀌거나 지워진다는 것을 알고, 고치기 전에 같은 `WHERE`로 `SELECT`부터 해요.

## 시작하기 전에

| 할 일 | 챕터 |
| --- | :---: |
| 표, 행과 열, 기본 키, `CREATE TABLE`, `INSERT`, `SELECT` 읽기 | 32 |
| `docker exec -it pg psql -U postgres`, `\l`, `\c`, `\dt`, `\d`, `\q` | 34 |
| `my-pg` 컨테이너, `pgdata` 볼륨, `kant_shop` 데이터베이스 | 35 |
| 리스트 고르기와 정렬(`sorted`, `key=`, 컴프리헨션)과 비교할 때 | 15, 22, 23 |

Docker Desktop을 켜 두고 macOS 터미널이나 Windows Git Bash에서 따라 쳐요. psql 안에서 치는 SQL은 끝에 `;`를 붙여요.

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1–4 | 표지, 오늘의 순서, 몇 줄만 골라 보고 고치는 장면, 네 문장 큰 그림 |
| 1. kant_shop에 들어가기 | 5 | `my-pg`에 들어가 `kant_shop`을 새로 만들고 `\c`로 옮기기 |
| 2. 자료형 고르기 | 6–12 | 자료형 지도, `CHAR` `VARCHAR` `TEXT`, 정수 세 가지와 범위 오류, 0.1 + 0.2, `NUMERIC(5, 2)`, `BOOLEAN`, 날짜와 시간대 |
| 3. 넣고 골라 보기 | 13–23 | `product` 표, 여러 줄 `INSERT`와 `NULL`, `AS`와 계산 열, `WHERE` 비교, `AND` `OR`, `IN` `BETWEEN`, `LIKE` `ILIKE`(`%` 있을 때와 없을 때), `IS NULL`과 `COUNT(*)`, `ORDER BY`, 두 기준, `LIMIT` `OFFSET` |
| 4. 고치고 지우기 | 24–30 | `UPDATE`, 계산해서 고치기, `DELETE`, `RETURNING`, `WHERE`를 뺀 사고, `DROP ... IF EXISTS`, 파이썬과 비교 |
| 5. 자주 나는 오류 | 31–33 | 큰따옴표와 닫지 않은 작은따옴표, 열 이름 오타와 빠진 쉼표, 형식이 다른 값 |
| 6. 실제 상황 예제 | 34–37 | 회원 찾기, `DISTINCT`로 사는 구 보기, 등급 올리기, 탈퇴 처리 |
| 정리 | 38–40 | 37에서 배울 것, 막힐 때, 한 장 요약 |

## 핵심 개념

### 네 문장

| 하는 일 | SQL | 결과 줄 |
| --- | --- | --- |
| 넣기 | `INSERT INTO product VALUES (...);` | `INSERT 0 1` |
| 골라 보기 | `SELECT 열 FROM product WHERE 조건 ORDER BY 열 LIMIT 3;` | 표와 `(3 rows)` |
| 고치기 | `UPDATE product SET 열 = 값 WHERE 조건;` | `UPDATE 1` |
| 지우기 | `DELETE FROM product WHERE 조건;` | `DELETE 1` |

`UPDATE`와 `DELETE`는 되돌리는 명령이 없어요. 고치기 전에 같은 `WHERE`로 `SELECT`를 먼저 쳐서 몇 줄이 걸리는지 봐요.

### 자료형 고르기

| 담을 값 | 자료형 | 기억할 것 |
| --- | --- | --- |
| 길이가 늘 같은 코드 | `CHAR(5)` | 짧게 넣으면 뒤를 빈칸으로 채워요 |
| 이름, 분류처럼 길이 상한이 있는 글자 | `VARCHAR(20)` | 넘으면 `value too long` 오류 |
| 메모처럼 길이를 모르는 글자 | `TEXT` | 길이 제한 없음 |
| 개수, 원 단위 가격 | `INTEGER` | 약 21억까지, 작으면 `SMALLINT`(32767), 크면 `BIGINT` |
| 돈, 할인율처럼 정확해야 하는 소수 | `NUMERIC(5, 2)` | 전체 5자리 중 소수 2자리, 가장 큰 값 999.99 |
| 조금 틀려도 되는 소수 | `REAL`, `DOUBLE PRECISION` | 0.1 + 0.2가 0.30000000000000004 |
| 예, 아니요 | `BOOLEAN` | psql은 `t`, `f`로 보여 줘요 |
| 날짜, 시각 | `DATE`, `TIME`, `TIMESTAMP`, `TIMESTAMPTZ` | 컨테이너 시간대는 UTC, `TIMESTAMPTZ`만 시간대를 따라 바뀌어요 |

`UUID`와 `JSON`은 이름만 봐요. 번호를 자동으로 매기는 `SERIAL`과 `IDENTITY`는 37에서 배워요.

### 작은따옴표와 큰따옴표

글자 값과 날짜 값은 작은따옴표(`'웹캠'`, `'2026-10-01'`)로 감싸요. PostgreSQL은 큰따옴표를 열 이름으로 읽어서 `column "웹캠" does not exist` 오류가 나요.

## 실습

### 1. kant_shop 만들고 들어가기

35에서 켠 `my-pg`가 없으면 먼저 켜요.

```bash
docker run -d --name my-pg -e POSTGRES_PASSWORD=admin1234 -p 5432:5432 -v pgdata:/var/lib/postgresql postgres:18
docker exec -it my-pg psql -U postgres
```

```sql
DROP DATABASE IF EXISTS kant_shop;
CREATE DATABASE kant_shop;
\c kant_shop
```

```
NOTICE:  database "kant_shop" does not exist, skipping
DROP DATABASE
CREATE DATABASE
You are now connected to database "kant_shop" as user "postgres".
```

다음부터는 `docker exec -it my-pg psql -U postgres -d kant_shop`으로 바로 들어가요.

### 2. 표 만들고 넣기

```sql
CREATE TABLE product (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    category VARCHAR(20),
    price INTEGER,
    stock INTEGER
);
INSERT INTO product (id, name, category, price, stock) VALUES
(1, '무선 이어폰', 'audio', 35000, 100),
(2, '게이밍 마우스', 'input', 28000, 85),
(3, '27인치 모니터', 'display', 259000, 15),
(4, 'USB-C 허브', 'acc', 19900, 200),
(5, '노트북 거치대', 'acc', 24000, 7),
(6, '기계식 키보드', 'input', 89000, 30),
(7, '블루투스 스피커', 'audio', 45000, 0),
(8, '웹캠', 'display', 52000, 12);
INSERT INTO product (id, name, category, stock) VALUES (9, '무선 충전기', 'acc', 40);
SELECT * FROM product;
```

```
 id |      name       | category | price  | stock
----+-----------------+----------+--------+-------
  1 | 무선 이어폰     | audio    |  35000 |   100
  2 | 게이밍 마우스   | input    |  28000 |    85
  3 | 27인치 모니터   | display  | 259000 |    15
  4 | USB-C 허브      | acc      |  19900 |   200
  5 | 노트북 거치대   | acc      |  24000 |     7
  6 | 기계식 키보드   | input    |  89000 |    30
  7 | 블루투스 스피커 | audio    |  45000 |     0
  8 | 웹캠            | display  |  52000 |    12
  9 | 무선 충전기     | acc      |        |    40
(9 rows)
```

9번은 가격을 안 적어서 `NULL`(빈칸)이에요.

### 3. 골라 보기

```sql
SELECT name, price FROM product WHERE price >= 50000;
SELECT name, category FROM product WHERE category IN ('audio', 'input');
SELECT name, price FROM product WHERE price BETWEEN 20000 AND 40000;
SELECT name FROM product WHERE name LIKE '무선%';
SELECT name FROM product WHERE name ILIKE 'usb%';
SELECT name, price FROM product WHERE price IS NULL;
SELECT name, price FROM product WHERE price IS NOT NULL ORDER BY price DESC LIMIT 3;
```

마지막 문장의 결과예요.

```
     name      | price
---------------+--------
 27인치 모니터 | 259000
 기계식 키보드 |  89000
 웹캠          |  52000
(3 rows)
```

`WHERE price = NULL`은 오류 없이 `(0 rows)`가 나와요. 빈칸은 늘 `IS NULL`로 찾아요.

`AS`로 열 이름을 바꾸고, 계산한 값도 열로 꺼내 봐요.

```sql
SELECT name AS 상품명, price AS 가격 FROM product WHERE id <= 3;
SELECT name, price, price * 3 FROM product WHERE id <= 3;
SELECT name AS 상품명, price * 3 AS "3개 가격" FROM product WHERE id <= 3;
```

```
    상품명     | 3개 가격
---------------+----------
 무선 이어폰   |   105000
 게이밍 마우스 |    84000
 27인치 모니터 |   777000
(3 rows)
```

이름을 안 붙인 계산 열은 `?column?`으로 나와요. 숫자로 시작하거나 띄어쓰기가 있는 이름은 큰따옴표로 감싸요. `AS 3개가격`처럼 그냥 적으면 `trailing junk after numeric literal` 오류가 나요.

`LIKE`에 `%`를 빼면 `=`와 같아요. `name LIKE '무선'`은 이름이 딱 "무선"인 줄만 찾아서 `(0 rows)`예요.

맞는 줄이 몇 개인지만 알고 싶으면 `COUNT(*)`를 써요.

```sql
SELECT COUNT(*) AS "가격 미정" FROM product WHERE price IS NULL;
```

```
 가격 미정
-----------
         1
(1 row)
```

`COUNT(*)`는 여기서 줄 수 세기로만 써요. `SUM`, `AVG` 같은 다른 계산과 묶어 세기는 다음 SQL 챕터에서 배워요.

### 4. 고치고 지우기

```sql
SELECT id, name, price FROM product WHERE id = 9;
UPDATE product SET price = 32000 WHERE id = 9;
UPDATE product SET price = price - 5000, stock = stock + 10 WHERE category = 'audio';
DELETE FROM product WHERE id = 8;
UPDATE product SET stock = 0 WHERE id = 5 RETURNING *;
```

```
UPDATE 1
UPDATE 2
DELETE 1
 id |     name      | category | price | stock
----+---------------+----------+-------+-------
  5 | 노트북 거치대 | acc      | 24000 |     0
(1 row)

UPDATE 1
```

`ORDER BY` 없이 `SELECT`하면 고친 줄이 뒤로 가서 순서가 바뀌어 보일 수 있어요.

### 5. 겹치는 값 빼고 보기

슬라이드 34쪽의 `member` 표(`tools/files.py`)를 만든 뒤 쳐요. 사는 구 `region`은 `VARCHAR(10)`이에요.

```sql
SELECT region FROM member;
SELECT DISTINCT region FROM member;
SELECT DISTINCT region, grade FROM member;
```

```
 region
--------
 송파구
 마포구
 강남구
(3 rows)
```

`SELECT region`은 6줄, `DISTINCT region`은 3줄이에요. 열을 두 개 적으면 두 값의 짝이 겹칠 때만 하나로 합쳐요. `DISTINCT` 결과의 순서는 정해져 있지 않아서 수강생 화면과 다를 수 있어요. 순서가 필요하면 `ORDER BY region`을 붙여요.

### 6. 연습 표 지우기

```sql
DROP TABLE IF EXISTS type_text;
\q
```

표가 없으면 `NOTICE:  table "type_text" does not exist, skipping`만 나오고 오류는 아니에요.

## 명령어 요약

| 명령 | 하는 일 |
| --- | --- |
| `docker exec -it my-pg psql -U postgres -d kant_shop` | `kant_shop`으로 바로 들어가기 |
| `CREATE TABLE 표 (열 자료형, ...);` | 표 만들기 |
| `INSERT INTO 표 (열, ...) VALUES (...), (...);` | 여러 줄 넣기 |
| `SELECT 열 FROM 표 WHERE 조건;` | 조건에 맞는 줄만 보기 |
| `SELECT name AS 상품명 FROM 표;` | 결과 열에 새 이름 붙이기 |
| `SELECT price * 3 AS "3개 가격" FROM 표;` | 계산한 값을 열로, 숫자로 시작하거나 띄어 쓴 이름은 큰따옴표 |
| `SELECT DISTINCT region FROM 표;` | 겹치는 값을 하나만 |
| `SELECT DISTINCT region, grade FROM 표;` | 두 값의 짝이 겹칠 때만 하나로 |
| `SELECT COUNT(*) FROM 표 WHERE 조건;` | 맞는 줄 수 세기 |
| `WHERE a = 1 AND b <> 'x'` | 둘 다 맞는 줄 (`<>`는 같지 않음) |
| `WHERE a = 1 OR a = 2` | 하나라도 맞는 줄 |
| `WHERE category IN ('audio', 'input')` | 목록 중 하나 |
| `WHERE price BETWEEN 20000 AND 40000` | 양 끝을 포함한 범위 |
| `WHERE name LIKE '무선%'` | `%`는 아무 글자, 대소문자 구별 |
| `WHERE name LIKE '무선'` | `%`가 없으면 `=`와 같아요 (딱 그 글자만) |
| `WHERE name ILIKE 'usb%'` | 대소문자 구별 없이 |
| `WHERE price IS NULL` | 빈칸 찾기 (`= NULL`은 안 돼요) |
| `ORDER BY price DESC` | 큰 값부터 (기본은 `ASC`, 작은 값부터) |
| `ORDER BY category, price DESC` | 앞 기준이 같으면 뒤 기준으로 |
| `LIMIT 3 OFFSET 3` | 앞 3줄을 건너뛰고 3줄 |
| `UPDATE 표 SET 열 = 값 WHERE 조건;` | 값 고치기 |
| `UPDATE 표 SET price = price - 5000 WHERE ...;` | 원래 값으로 계산해서 고치기 |
| `DELETE FROM 표 WHERE 조건;` | 줄 지우기 |
| `... RETURNING *` | 넣거나 고치거나 지운 줄을 바로 보기 |
| `DROP TABLE IF EXISTS 표;` | 없으면 알림만 하고 지우기 |
| `DROP DATABASE IF EXISTS 이름;` | 데이터베이스 지우기 (`\c`로 다른 곳에 있을 때) |
| `SET TIME ZONE 'Asia/Seoul';` | 이 접속의 시간대를 한국으로 |

## 문제 해결

| 메시지 | 원인 | 해결 |
| --- | --- | --- |
| `column "웹캠" does not exist` | 글자 값을 큰따옴표로 감쌌어요 | 작은따옴표 `'웹캠'`으로 감싸요 |
| 프롬프트가 `kant_shop'#`로 바뀌고 실행이 안 돼요 | 닫는 작은따옴표가 빠졌어요 | `Ctrl+C`로 쓰던 문장을 지우고 다시 쳐요 |
| `column "nmae" does not exist` | 열 이름 오타 | `HINT` 줄에 나온 이름으로 고쳐요 |
| 열이 하나만 나오고 이름이 이상해요 | `SELECT name price`처럼 쉼표가 빠졌어요 | `SELECT name, price`로 쉼표를 넣어요 |
| `value too long for type character varying(5)` | `VARCHAR(5)`보다 긴 글자 | 값을 줄이거나 표를 만들 때 길이를 넉넉히 잡아요 |
| `smallint out of range`, `integer out of range` | 자료형이 담을 수 있는 범위를 넘었어요 | 더 큰 정수 자료형을 골라요 |
| `numeric field overflow` | `NUMERIC(5, 2)`에 정수 부분이 네 자리인 값 | 자릿수를 늘려 표를 만들어요 |
| `invalid input syntax for type integer: "24,000"` | 숫자 칸에 쉼표나 글자를 넣었어요 | `24000`처럼 숫자만 적어요 |
| `date/time field value out of range` | 2월 30일처럼 없는 날짜 | `'2026-02-28'`처럼 있는 날짜로 적어요 |
| `UPDATE 8`, `DELETE 8`처럼 숫자가 커요 | `WHERE`를 빼서 모든 줄이 바뀌었어요 | 되돌릴 수 없어요. 처음 `INSERT`부터 다시 넣고, 다음에는 `SELECT`로 먼저 확인해요 |
| `table "type_text" does not exist` | 없는 표를 지우려고 했어요 | `DROP TABLE IF EXISTS`를 써요 |
| `trailing junk after numeric literal at or near "3개가격"` | `AS` 뒤 이름이 숫자로 시작해요 | `AS "3개 가격"`처럼 큰따옴표로 감싸요 |
| `LIKE '김'`이 `(0 rows)` | `%`가 없으면 딱 그 글자만 찾아요 | `LIKE '김%'`처럼 `%`를 붙여요 |
| `WHERE price = NULL`이 `(0 rows)` | `NULL`은 `=`로 비교하지 않아요 | `IS NULL`, `IS NOT NULL`을 써요 |

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py           이 챕터의 장 생성
  demo.py          슬라이드에 넣은 출력을 실제 Docker와 PostgreSQL 18로 실행
  files.py         CREATE TABLE과 INSERT 문장 (product, member)
  ptyrun.py        psql을 진짜 터미널처럼 실행해 화면을 옮기는 도우미
  out.json         demo.py가 남긴 실제 출력
sql-basics-slides.html   배포용 HTML
sql-basics-slides.pdf    슬라이드 PDF
```

출력은 `postgres:18`(PostgreSQL 18.7) 컨테이너에서 실제로 실행한 결과예요. 컨테이너 시간대가 UTC라서 `now()`와 `TIMESTAMPTZ` 결과는 실행한 시각과 시간대에 따라 달라요. `ORDER BY` 없는 `SELECT`의 줄 순서도 수강생 화면과 다를 수 있어요.

검사, HTML, PDF를 만드는 공용 도구는 맨 위 [tools/](../tools)에 한 벌만 있어요. 명령은 이 폴더에서 쳐요.

```bash
uv run -q --with pyte python tools/demo.py
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/boxcheck.js slides
node ../tools/build_player.js slides sql-basics-slides.html
node ../tools/export.js slides sql-basics-slides.pdf
```

</details>

---

<!-- curriculum:nav -->

[← 이전: 35 · Docker 5 (명령어 한눈에 보기)](../35-docker-cli) · [커리큘럼](../README.md) · [다음: 37 · SQL 2 (제약 조건으로 표 설계하기) →](../37-sql-constraints)

<!-- /curriculum:nav -->
