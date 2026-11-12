# 32 · 데이터베이스 기초 (표, 타입, 기본 키, SQL 맛보기)

> 지금까지 주문은 파이썬 리스트와 딕셔너리에 담았어요. 프로그램을 끄면 그 값도 같이 사라져요. 이번에는 데이터를 오래 담아 두는 데이터베이스를 보고, 표, 행, 열, 타입, 기본 키 같은 낱말을 익혀요. 그다음 SQL 네 문장으로 표를 만들고 넣고 꺼내는 화면을 MySQL과 PostgreSQL에서 나란히 읽어요. 서버를 직접 켜고 쳐 보는 건 33에서 해요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/32-database-basics/database-basics-slides.html) | [31 · nginx 기초 (웹 서버와 리버스 프록시)](../31-nginx-basics) | 준비 중 |

<!-- /curriculum:top -->

## 학습 목표

- 데이터베이스가 파이썬 변수, 엑셀 파일과 무엇이 다른지 말해요.
- DBMS, 관계형 데이터베이스(RDB), 표(테이블), 행(row), 열(column)이 무엇인지 말해요.
- 열마다 타입(`INT`, `VARCHAR(20)`)을 정하는 이유를 말해요.
- 기본 키(Primary Key)가 왜 필요한지 말하고, 표에서 기본 키 열을 골라요.
- 서버 안에 데이터베이스가, 그 안에 표가 있다는 구조를 그림으로 그려요.
- `CREATE DATABASE`, `CREATE TABLE`, `INSERT`, `SELECT`와 `WHERE`가 무엇을 하는지 읽어요.
- MySQL과 PostgreSQL에서 같은 것(SQL)과 다른 것(프롬프트, 데이터베이스 고르기, 자동 번호, 포트)을 구별해요.
- 겹친 기본 키, 타입에 안 맞는 값, 빠진 `;`, 빠진 작은따옴표, 고르지 않은 데이터베이스 오류를 읽고 고치는 법을 말해요.

## 시작하기 전에

| 할 일 | 챕터 |
| --- | :---: |
| 리스트에 `append`로 담고 `print`로 보기 | 13 |
| 딕셔너리와 딕셔너리 리스트 | 15 |
| `if`로 고르기, 리스트 컴프리헨션 | 17, 23 |
| Docker로 서버 프로그램(nginx)을 켜 본 경험 | 29~31 |

이 챕터는 설치하거나 칠 것이 없어요. 슬라이드의 터미널 화면을 읽으면서 따라가요.

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1–5 | 표지, 오늘의 순서, 끄면 사라지는 리스트, 큰 그림(프로그램, DBMS, 데이터 파일), SQL 한 줄 |
| 1. 데이터베이스와 표 | 6–11 | 변수, 파일과 비교, 관계형과 표, 행과 열, 열 타입, 기본 키, 서버 안의 데이터베이스와 표 |
| 2. SQL 네 문장 맛보기 | 12–19 | 네 문장 소개, `CREATE DATABASE`와 `USE`·`\c`, `CREATE TABLE`, `INSERT` 한 행, 열 이름과 여러 행, `SELECT`와 `WHERE`, 파이썬과 비교, 두 서버 비교 |
| 3. 자주 나는 오류 | 20–24 | 겹친 기본 키, 타입과 길이, 빠진 `;`, 빠진 작은따옴표, 고르지 않은 데이터베이스 |
| 4. 실제 상황 예제 | 25–26 | 오늘 주문 넣고 라테만 고르기, 메뉴판을 보고 menu 표 설계하기 |
| 정리 | 27–28 | 막힐 때, 한 장 요약 |

## 핵심 개념

### 데이터베이스와 DBMS

```
프로그램(터미널, 파이썬 앱, 키오스크) ──SQL로 부탁──▶ 데이터베이스 서버(DBMS) ──▶ 데이터 파일(디스크)
```

프로그램은 데이터 파일을 직접 만지지 않아요. 데이터베이스 서버가 부탁을 차례대로 받아 대신 읽고 써요. 이 서버 프로그램을 DBMS(데이터베이스 관리 시스템)라고 부르고, MySQL과 PostgreSQL이 많이 쓰는 두 가지예요. 수업에서 둘을 번갈아 써도 이 챕터의 SQL은 똑같이 돌아요.

| | 끄고 켜면 | 여러 프로그램이 동시에 | 많은 데이터 중 하나 찾기 |
| --- | --- | --- | --- |
| 파이썬 변수 | 사라져요 | 한 프로그램 안에서만 | `for`로 처음부터 하나씩 |
| 파일 (엑셀, txt) | 남아요 | 둘이 같이 고치면 덮어써요 | 파일을 처음부터 읽어요 |
| 데이터베이스 | 남아요 | 차례대로 받아서 지켜 줘요 | 조건을 주면 바로 찾아요 |

### 표, 행, 열, 타입, 기본 키

| id `INT` 기본 키 | menu `VARCHAR(20)` | qty `INT` |
| :---: | :---: | :---: |
| 1 | latte | 2 |
| 2 | americano | 1 |
| 3 | cake | 1 |

- 표(테이블): 엑셀 시트 한 장 같은 것이에요. 이 표의 이름은 `orders`예요. 표끼리 번호로 이어 쓸 수 있어서 관계형 데이터베이스(RDB)라고 불러요.
- 행(row, 레코드): 가로 한 줄이에요. 주문 하나가 행 하나예요.
- 열(column, 필드): 세로 한 줄이에요. `id`, `menu`, `qty`처럼 항목 하나가 열 하나예요.
- 타입: 열마다 담을 값의 종류를 미리 정해요. `INT`는 정수(파이썬 `int`), `VARCHAR(20)`은 20자까지의 글자(파이썬 `str`)예요.
- 기본 키(Primary Key): 행마다 겹치지 않는 번호예요. 다른 행과 겹치면 안 되고, 비워 둘 수 없어요. 카페 진동벨 번호와 같아요.

15의 딕셔너리 리스트와 같은 모양이에요. 딕셔너리 하나가 행이고, 키가 열이에요. 다른 점은 표의 모든 행이 같은 열을 가진다는 것이에요.

### 서버 안의 구조

```
데이터베이스 서버
└── 데이터베이스 cafe
    ├── 표 orders
    └── 표 menu
```

파일로 치면 서버는 컴퓨터, 데이터베이스는 폴더, 표는 엑셀 파일이에요. 서버가 처음부터 갖고 있는 데이터베이스(MySQL의 `mysql`, `sys`, PostgreSQL의 `postgres`, `template0` 등)는 건드리지 않아요.

### SQL 네 문장

```sql
CREATE DATABASE cafe;

CREATE TABLE orders (
  id INT PRIMARY KEY,
  menu VARCHAR(20),
  qty INT
);

INSERT INTO orders VALUES (1, 'latte', 2);
INSERT INTO orders (id, menu, qty) VALUES (2, 'americano', 1), (3, 'cake', 1);

SELECT * FROM orders;
SELECT menu, qty FROM orders;
SELECT * FROM orders WHERE id = 2;
```

- 문장은 `;`로 끝나요. `;`가 나와야 서버가 실행해요.
- SQL 낱말은 대문자로 쓰는 게 약속이에요. 소문자로 써도 돌아가요.
- 글자 값은 `'latte'`처럼 작은따옴표로 감싸요. 숫자는 따옴표 없이 적어요.
- `WHERE`의 "같다"는 파이썬의 `==`와 달리 `=` 하나예요.

| 하는 일 | 파이썬 | SQL |
| --- | --- | --- |
| 담을 곳 만들기 | `orders = []` | `CREATE TABLE orders (…);` |
| 하나 넣기 | `orders.append({"id": 1, …})` | `INSERT INTO orders VALUES (1, …);` |
| 모두 보기 | `print(orders)` | `SELECT * FROM orders;` |
| 골라 보기 | `[o for o in orders if o["id"] == 2]` | `SELECT * FROM orders WHERE id = 2;` |
| 프로그램을 끄면 | 사라져요 | 서버에 남아요 |

### MySQL과 PostgreSQL

| | MySQL 8.4 | PostgreSQL 18 |
| --- | --- | --- |
| 프롬프트 | `mysql>` | `cafe=#` (지금 있는 데이터베이스 이름) |
| 이어지는 줄 | `->` | `cafe(#`, `cafe-#` |
| 데이터베이스 고르기 | `USE cafe;` | `\c cafe` |
| 데이터베이스 목록 | `SHOW DATABASES;` | `\l` |
| 결과 끝 줄 | `3 rows in set` | `(3 rows)` |
| 번호 자동으로 붙이기 | `id INT AUTO_INCREMENT` | `id SERIAL` |
| 기본 포트 | 3306 | 5432 |

`CREATE DATABASE`, `CREATE TABLE`, `INSERT`, `SELECT`, `WHERE`, `INT`, `VARCHAR`, `PRIMARY KEY`는 두 서버에서 그대로 같아요. `\c`, `\l`처럼 역슬래시로 시작하는 것은 SQL이 아니라 psql 프로그램의 명령이라서 끝에 `;`가 없어요. 자동 번호는 이름만 알아 두고, 이 챕터에서는 번호를 직접 넣어요.

## 실습

이 챕터는 종이와 연필로 해요. 서버를 켜고 직접 치는 실습은 33에서 해요.

1. 카페 회원을 담을 `members` 표를 설계해요. 회원 번호, 이름, 적립 도장 수를 담아요. 열 이름, 타입, 기본 키를 정해서 아래 빈칸을 채워요.

   ```sql
   CREATE TABLE members (
     ____ ____ PRIMARY KEY,
     ____ VARCHAR(20),
     ____ ____
   );
   ```

2. 회원 두 명(1번 kim 도장 3개, 2번 lee 도장 0개)을 한 문장으로 넣는 `INSERT`를 적어요.
3. 도장이 1개 이상인 회원만 꺼내는 `SELECT`를 적어요. 숫자 비교는 파이썬처럼 `>=`를 써요.
4. 아래 문장들이 어떤 오류를 내는지 3파트를 보고 적어요.

   ```sql
   INSERT INTO members VALUES (1, 'park', 2);
   INSERT INTO members VALUES (3, park, 2);
   SELECT * FROM members
   ```

<details>
<summary>답 보기</summary>

```sql
CREATE TABLE members (
  id INT PRIMARY KEY,
  name VARCHAR(20),
  stamps INT
);

INSERT INTO members VALUES (1, 'kim', 3), (2, 'lee', 0);

SELECT * FROM members WHERE stamps >= 1;
```

4번은 차례대로 겹친 기본 키(1번이 이미 있어요), 열 이름으로 읽힌 `park`(작은따옴표가 없어요), 다음 줄을 기다리는 프롬프트(`;`가 없어요)예요.

</details>

## 명령어 요약

| 명령 | 하는 일 |
| --- | --- |
| `CREATE DATABASE cafe;` | 데이터베이스 cafe를 만들어요 |
| `USE cafe;` | (MySQL) cafe 안으로 들어가요 |
| `\c cafe` | (PostgreSQL) cafe 안으로 들어가요 |
| `CREATE TABLE orders (id INT PRIMARY KEY, menu VARCHAR(20), qty INT);` | 열 이름, 타입, 기본 키를 정해 표를 만들어요 |
| `INSERT INTO orders VALUES (1, 'latte', 2);` | 열 순서대로 값을 넣어 행 하나를 더해요 |
| `INSERT INTO orders (id, menu, qty) VALUES (…), (…);` | 열 이름을 적고 여러 행을 한 번에 넣어요 |
| `SELECT * FROM orders;` | 모든 열, 모든 행을 꺼내요 |
| `SELECT menu, qty FROM orders;` | 고른 열만 꺼내요 |
| `SELECT * FROM orders WHERE id = 2;` | 조건에 맞는 행만 꺼내요 |
| `SHOW DATABASES;` / `\l` | 데이터베이스 목록을 봐요 (MySQL / PostgreSQL) |

## 문제 해결

| MySQL 메시지 | PostgreSQL 메시지 | 원인 | 해결 |
| --- | --- | --- | --- |
| `Duplicate entry '1' for key 'orders.PRIMARY'` | `duplicate key value violates unique constraint "orders_pkey"` | 기본 키가 겹쳐요 | 아직 안 쓴 번호로 바꿔요 |
| `Incorrect integer value: 'many'` | `invalid input syntax for type integer: "many"` | `INT` 열에 글자를 넣었어요 | 숫자로 고쳐요 |
| `Data too long for column 'menu'` | `value too long for type character varying(20)` | `VARCHAR(20)`보다 길어요 | 줄이거나 표를 만들 때 숫자를 넉넉히 정해요 |
| `Unknown column 'latte' in 'field list'` | `column "latte" does not exist` | 글자 값에 작은따옴표가 없어서 열 이름으로 읽었어요 | `'latte'`처럼 감싸요 |
| `No database selected` | `relation "orders" does not exist` (프롬프트가 `postgres=#`) | 데이터베이스를 고르지 않았어요 | `USE cafe;` 또는 `\c cafe` |
| 프롬프트가 `->` | 프롬프트가 `cafe-#` | 문장 끝에 `;`가 없어서 다음 줄을 기다려요 | `;`만 치고 Enter |

큰따옴표로 글자를 감싸면 MySQL은 받아 주지만 PostgreSQL은 열 이름으로 읽어요(`column "latte" does not exist`). 두 서버에서 다 되도록 작은따옴표로 적어요.

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분 (gen.py가 만들어요)
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  ptyrun.py        mysql, psql 화면을 120칸 터미널에서 실행 (31에서 가져옴)
  demo.py          모든 SQL을 실제 MySQL과 PostgreSQL 컨테이너에서 실행해서 tools/out.json에 저장
  out.json         실제 실행 출력
  gen.py           모든 장과 deck.json 생성
database-basics-slides.html  배포용 HTML
database-basics-slides.pdf   강사용 PDF
```

검사, HTML, PDF를 만드는 공용 도구는 맨 위 [tools/](../tools)에 한 벌만 있어요. 명령은 이 폴더에서 쳐요. `demo.py`는 Docker 데몬이 있어야 하고, `my`, `pg` 컨테이너를 지우고 새로 켜요.

```bash
uv run -q --with pyte python tools/demo.py
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/build_player.js slides database-basics-slides.html
node ../tools/export.js slides database-basics-slides.pdf
```

출력은 Docker 29.9.2에서 `mysql:8.4`(MySQL 8.4.13)와 `postgres:18`(PostgreSQL 18.6) 이미지로 실행한 결과예요. 실행 시간(`0.01 sec`)은 수강생 화면과 조금 다를 수 있어요. 3쪽의 `uv run main.py` 출력도 실제로 두 번 실행해서 옮겼어요.

범위: 데이터베이스와 DBMS, 관계형과 표, 행과 열, `INT`와 `VARCHAR`, 기본 키, 서버 안의 데이터베이스와 표, SQL 네 문장(`CREATE DATABASE`, `CREATE TABLE`, `INSERT`, `SELECT`)과 `WHERE`, MySQL과 PostgreSQL의 차이를 다뤄요. 화면은 읽기만 하고, 서버 켜기와 접속은 33에서 해요. `JOIN`, 인덱스, 트랜잭션, `UPDATE`와 `DELETE`, `AUTO_INCREMENT`와 `SERIAL` 실습, 날짜와 소수 타입, 파이썬에서 데이터베이스 연결하기는 다루지 않아요.

</details>

---

<!-- curriculum:nav -->

[← 이전: 31 · nginx 기초 (웹 서버와 리버스 프록시)](../31-nginx-basics) · [커리큘럼](../README.md)

<!-- /curriculum:nav -->
