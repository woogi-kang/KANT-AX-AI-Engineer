# 34 · Docker 4 (PostgreSQL 컨테이너로 데이터베이스 쓰기)

> 33에서는 MySQL을 컨테이너로 켜서 주문을 표에 담았어요. 수업 자료나 회사에 따라 PostgreSQL을 쓰는 곳도 많아요. 이번에는 같은 순서로 PostgreSQL을 켜고, psql로 들어가 데이터베이스와 표를 만들고, 볼륨으로 주문을 지켜요. 마지막에 MySQL과 다른 점을 표 한 장으로 모아요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/34-docker-postgres/docker-postgres-slides.html) | [33 · Docker 3 (MySQL 컨테이너)](../33-docker-mysql) | [35 · Docker 5 (명령어 한눈에 보기)](../35-docker-cli) |

<!-- /curriculum:top -->

## 학습 목표

- `postgres:18` 이미지를 받아 `-e POSTGRES_PASSWORD`로 관리자 비밀번호를 주고 켜요.
- `docker logs`에서 `ready to accept connections`를 보고 준비가 끝났는지 알아봐요.
- `docker exec -it pg psql -U postgres`로 들어가고, `-d`, `-c`, `\q`를 써요.
- SQL(`CREATE DATABASE`, `CREATE TABLE`, `INSERT`, `SELECT`, `DROP`)과 psql의 백슬래시 명령(`\l`, `\c`, `\dt`, `\d`, `\du`)을 구별해요.
- 관리자 `postgres`와 일반 계정의 차이를 말하고, `POSTGRES_USER`가 MySQL의 `MYSQL_USER`와 어떻게 다른지 말해요.
- 컨테이너 안에서는 비밀번호를 안 묻고, 밖에서 5432번으로 붙으면 묻는다는 것을 말해요.
- 볼륨을 `/var/lib/postgresql`에 붙여 컨테이너를 지워도 데이터가 남게 하고, `compose.yaml`로 옮겨요.
- 자주 나는 오류(비밀번호 빠짐, 너무 빨리 접속, 5432 겹침, 18의 볼륨 자리, 남은 볼륨의 비밀번호)를 기록을 보고 고쳐요.

## 시작하기 전에

| 할 일 | 챕터 |
| --- | :---: |
| `docker run -d --name -p`, `ps`, `ps -a`, `stop`, `rm`, `logs`, 포트 겹침 오류 | 29 |
| `docker exec -it`, 볼륨 `-v 이름:경로`, `-v ./폴더:경로`, `compose.yaml`, `docker compose up -d`, `down` | 30 |
| `docker exec 이름 명령`으로 명령 하나만 실행 | 31 |
| 데이터베이스, 표, 행과 열, 기본 키, SQL 문장 읽기 | 32 |
| MySQL 컨테이너로 같은 순서 해 보기 | 33 |

Docker Desktop을 켜 두고 따라 쳐요. 터미널은 macOS 터미널이나 Windows Git Bash를 써요. 33의 MySQL 컨테이너가 켜져 있어도 포트가 3306과 5432로 달라서 같이 켤 수 있어요.

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1–4 | 표지, 오늘의 순서, MySQL 명령이 안 되는 장면, 큰 그림 |
| 1. PostgreSQL 컨테이너 켜기 | 5–9 | `docker pull postgres:18`, `docker run`, `-e` 이름 세 개, `docker logs`, `psql`로 들어가기 |
| 2. 데이터베이스와 표 만들기 | 10–15 | SQL과 백슬래시 명령, `CREATE DATABASE`와 `\l`, `\c`, `CREATE TABLE`과 `\dt` `\d`, `INSERT`와 `SELECT`, `DROP` |
| 3. 계정과 접속 방법 | 16–20 | 관리자와 일반 계정(`=#`, `=>`), `POSTGRES_USER`, bash로 들어가기, 밖에서 비밀번호, `-c` 한 문장 |
| 4. 볼륨과 compose | 21–25 | 지우면 사라지는 데이터베이스, `/var/lib/postgresql`, `-v pg-data:/var/lib/postgresql`, `compose.yaml`, `docker compose exec` |
| 5. 자주 나는 오류 | 26–31 | 비밀번호 빠짐, 너무 빨리 접속, 5432 겹침, 세미콜론과 이름 오타, 18의 볼륨 자리, 남은 볼륨의 비밀번호 |
| 6. 실제 상황 예제 | 32–33 | 다음 날에도 남는 주문, init 폴더로 메뉴 채우기 |
| 정리 | 34–37 | MySQL과 비교, 명령 비교, 막힐 때, 한 장 요약 |

## 핵심 개념

### 그림 한 장

```
내 터미널 ── docker exec -it pg psql ──▶ ┌ 컨테이너 pg (postgres:18) ───────────┐
밖의 프로그램 ── 5432번 포트 ──────────▶ │ PostgreSQL 서버                       │
                                         │  ├ postgres (처음부터 있는 DB)        │
                                         │  └ shop (오늘 만드는 DB) └ orders 표  │
                                         └──────────── /var/lib/postgresql ──────┘
                                                              │
                                                       pg-data 볼륨 (붕어빵 밖 보관함)
```

### psql에 치는 두 가지

| | SQL | 백슬래시 명령 |
| --- | --- | --- |
| 예 | `CREATE DATABASE shop;` `SELECT * FROM orders;` | `\l` `\c shop` `\dt` `\d orders` `\du` `\q` |
| 누가 처리해요 | PostgreSQL 서버 | psql 프로그램 |
| 끝의 `;` | 꼭 붙여요 | 안 붙여요 |
| MySQL과 비교 | 똑같아요 | MySQL은 `SHOW DATABASES;`, `USE shop;`처럼 달라요 |

### 앞의 표시 읽기

| 표시 | 뜻 |
| --- | --- |
| `postgres=#` | `postgres` 데이터베이스에 관리자로 들어와 있어요 |
| `shop=#` | `\c shop`으로 `shop`에 옮겼어요 |
| `postgres=>` | 일반 계정으로 들어와 있어요 |
| `shop-#` | 문장이 아직 안 끝났어요. `;`만 치고 Enter를 눌러요 |

### 계정과 비밀번호

- 공식 이미지는 관리자 계정 `postgres`를 만들고, 비밀번호는 `-e POSTGRES_PASSWORD`로 정해요. 이 값이 없으면 켜지지 않아요.
- `-e POSTGRES_USER=cafe`를 주면 관리자 이름이 `cafe`로 바뀌고 `postgres` 계정은 생기지 않아요. 33의 `MYSQL_USER`는 root 옆에 일반 계정을 하나 더 만드는 것이라 반대예요.
- 일반 계정은 `CREATE USER app WITH PASSWORD 'app1234';`로 만들어요. 데이터베이스를 만들 권한이 없어요.
- 컨테이너 안(`docker exec`)에서 들어오면 비밀번호를 묻지 않아요. 밖에서 5432번으로 붙으면 비밀번호를 물어요. 나중에 파이썬 앱이 붙을 때 이 비밀번호가 필요해요.
- `POSTGRES_`로 시작하는 `-e`와 init 폴더는 데이터 폴더가 비어 있을 때 처음 한 번만 쓰여요.

### 데이터 자리는 18부터 바뀌었어요

| 버전 | 볼륨을 붙이는 자리 |
| --- | --- |
| 17까지 | `/var/lib/postgresql/data` |
| 18부터 | `/var/lib/postgresql` (안에 `18/docker` 폴더가 생겨요) |

인터넷의 예전 글을 따라 할 때는 이미지 버전을 먼저 봐요. 18에 예전 자리를 붙이면 `Error: in 18+`가 나고 바로 꺼져요.

## 실습

출력은 tools/demo.py로 실제 Docker와 PostgreSQL 18을 실행한 결과예요. 컨테이너 ID와 시간은 내 화면과 달라요.

### 1. 켜고 들어가기

```bash
docker pull postgres:18
docker run -d --name pg -e POSTGRES_PASSWORD=cafe1234 -p 5432:5432 postgres:18
docker ps
```

```
CONTAINER ID   IMAGE         COMMAND                  CREATED         STATUS         PORTS                    NAMES
b0771208641d   postgres:18   "docker-entrypoint.s…"   3 seconds ago   Up 2 seconds   0.0.0.0:5432->5432/tcp   pg
```

처음 켤 때는 몇 초 걸려요. `docker logs pg`의 마지막 줄이 `database system is ready to accept connections`이면 들어가요.

```bash
docker logs pg
docker exec -it pg psql -U postgres
```

### 2. 데이터베이스와 표 만들기

psql 안에서 차례로 쳐요.

```sql
CREATE DATABASE shop;
\l
\c shop
CREATE TABLE orders (id INT PRIMARY KEY, menu VARCHAR(20), qty INT);
\dt
\d orders
INSERT INTO orders VALUES (1, 'latte', 2);
INSERT INTO orders VALUES (2, 'americano', 1);
SELECT * FROM orders;
```

```
shop=# SELECT * FROM orders;
 id |   menu    | qty
----+-----------+-----
  1 | latte     |   2
  2 | americano |   1
(2 rows)
```

지울 때는 표부터 지우고, 데이터베이스는 다른 곳으로 옮긴 뒤 지워요. 들어가 있는 데이터베이스는 못 지워요.

```sql
DROP TABLE orders;
\c postgres
DROP DATABASE shop;
\q
```

### 3. 계정 보기와 한 문장 실행

```bash
docker exec -it pg psql -U postgres
```

```sql
CREATE USER app WITH PASSWORD 'app1234';
\du
\q
```

```
 Role name |                         Attributes
-----------+------------------------------------------------------------
 app       |
 postgres  | Superuser, Create role, Create DB, Replication, Bypass RLS
```

```bash
docker exec -it pg psql -U app -d postgres
```

```
postgres=> CREATE DATABASE test;
ERROR:  permission denied to create database
```

`\q`로 나와요. 한 문장만 실행할 때는 `-it` 없이 `-c`를 붙여요.

```bash
docker exec pg psql -U postgres -c "SELECT version();"
```

### 4. 볼륨으로 지키기

앞의 `pg`를 지우고 볼륨을 붙여 다시 켜요.

```bash
docker stop pg
docker rm pg
docker run -d --name pg -e POSTGRES_PASSWORD=cafe1234 -p 5432:5432 -v pg-data:/var/lib/postgresql postgres:18
```

2번처럼 `shop`과 `orders`를 만들고 주문을 넣은 뒤, `docker stop pg`, `docker rm pg`로 지우고 같은 `docker run`으로 다시 켜요. `docker exec -it pg psql -U postgres -d shop`으로 들어가 `SELECT * FROM orders;`를 치면 주문 두 개가 그대로 나와요.

연습이 끝나면 지워요. 볼륨을 지우면 데이터도 같이 사라져요.

```bash
docker stop pg
docker rm pg
docker volume rm pg-data
```

### 5. compose로 옮기기

```bash
mkdir ~/cafe-pg
cd ~/cafe-pg
```

`~/cafe-pg` 폴더에 아래 `compose.yaml`을 저장해요.

```yaml
services:
  pg:
    image: postgres:18
    environment:
      POSTGRES_PASSWORD: cafe1234
      POSTGRES_DB: cafe
    ports:
      - "5432:5432"
    volumes:
      - pg-data:/var/lib/postgresql

volumes:
  pg-data:
```

```bash
docker compose up -d
docker compose exec pg psql -U postgres -d cafe
```

`docker compose down`은 볼륨을 남기고, `docker compose down -v`는 볼륨까지 지워요.

### 6. init 폴더로 메뉴 채우기

`~/cafe-pg/init/menu.sql`을 만들어요.

```sql
CREATE TABLE menu (id INT PRIMARY KEY, name VARCHAR(20), price INT);
INSERT INTO menu VALUES (1, 'americano', 4000);
INSERT INTO menu VALUES (2, 'latte', 4500);
INSERT INTO menu VALUES (3, 'cake', 5000);
```

`compose.yaml`의 `volumes:` 아래에 한 줄을 더해요.

```yaml
      - ./init:/docker-entrypoint-initdb.d
```

볼륨이 비어 있을 때만 실행되니 `down -v` 뒤에 켜요.

```bash
docker compose down -v
docker compose up -d
docker compose exec pg psql -U postgres -d cafe -c "SELECT * FROM menu;"
```

```
 id |   name    | price
----+-----------+-------
  1 | americano |  4000
  2 | latte     |  4500
  3 | cake      |  5000
(3 rows)
```

## 명령어 요약

| 명령 | 하는 일 |
| --- | --- |
| `docker run -d --name pg -e POSTGRES_PASSWORD=cafe1234 -p 5432:5432 postgres:18` | PostgreSQL 켜기 |
| `docker exec -it pg psql -U postgres` | 관리자로 psql 열기 |
| `… psql -U postgres -d shop` | `shop`으로 바로 들어가기 |
| `docker exec pg psql -U postgres -c "…"` | 한 문장만 실행 |
| `docker exec -it pg bash` 뒤 `psql -U postgres` | bash에서 psql 열기 |
| `\l` / `\c shop` | 데이터베이스 목록 / 옮기기 |
| `\dt` / `\d orders` | 표 목록 / 표 모양 |
| `\du` | 계정 목록 |
| `\q` | psql 나가기 |
| `CREATE USER app WITH PASSWORD '…';` | 일반 계정 만들기 |
| `-v pg-data:/var/lib/postgresql` | 18부터 볼륨 자리 |
| `docker compose exec pg psql -U postgres -d cafe` | compose 서비스로 들어가기 |
| `docker compose down -v` | 볼륨까지 지우기 |

### 33 MySQL과 비교

| | 33 MySQL | 34 PostgreSQL |
| --- | --- | --- |
| 이미지 | `mysql:8.4` | `postgres:18` |
| 관리자 | `root` | `postgres` |
| 관리자 비밀번호 | `MYSQL_ROOT_PASSWORD` | `POSTGRES_PASSWORD` |
| 처음 만들 DB | `MYSQL_DATABASE` | `POSTGRES_DB` |
| 앱 계정 `-e` | `MYSQL_USER`: 일반 계정을 하나 더 | `POSTGRES_USER`: 관리자 이름이 바뀌어요 |
| 포트 | 3306 | 5432 |
| 데이터 자리 | `/var/lib/mysql` | `/var/lib/postgresql` |
| 들어가기 | `docker exec -it db mysql -u root -p` | `docker exec -it pg psql -U postgres` |
| 안에서 비밀번호 | 물어요 | 안 물어요 |
| 데이터베이스 목록 | `SHOW DATABASES;` | `\l` |
| 다른 데이터베이스로 | `USE shop;` | `\c shop` |
| 표 목록 / 표 모양 | `SHOW TABLES;` / `DESCRIBE orders;` | `\dt` / `\d orders` |
| 나가기 | `exit` | `\q` |
| 한 문장만 | `mysql … -e "…"` | `psql … -c "…"` |

## 문제 해결

| 메시지 | 원인 | 해결 |
| --- | --- | --- |
| `connection to server on socket … failed: No such file or directory` | 켜는 중이라 아직 서버가 없어요 | `docker logs pg`에서 `ready to accept connections`를 보고 다시 들어가요 |
| `Exited (1)`, logs에 `superuser password is not specified` | `-e POSTGRES_PASSWORD`가 빠졌어요 | `docker rm pg` 뒤 `-e`를 붙여 다시 켜요 |
| `Error: in 18+, these Docker images are configured …` | 17까지 쓰던 `/var/lib/postgresql/data`에 볼륨을 붙였어요 | `docker rm pg` 뒤 `-v pg-data:/var/lib/postgresql`로 켜요 |
| `port is already allocated` | 5432번을 다른 컨테이너나 설치한 PostgreSQL이 쓰고 있어요 | 하나를 끄거나 `-p 5433:5432`로 바꿔요 |
| `password authentication failed` | 비밀번호가 틀렸어요. 볼륨을 다시 쓰면 처음 정한 비밀번호가 맞아요 | 처음 비밀번호로 들어가요. 새로 하려면 `docker volume rm pg-data` |
| `role "postgres" does not exist` | `POSTGRES_USER`로 관리자 이름을 바꿨어요 | `-U` 뒤에 그 이름을 적어요 |
| `permission denied to create database` | 일반 계정이에요 | `-U postgres`로 들어가요 |
| `cannot drop the currently open database` | 지우려는 데이터베이스에 들어가 있어요 | `\c postgres`로 옮긴 뒤 지워요 |
| 표시가 `-#`로 바뀌어요 | 문장 끝 `;`가 빠졌어요 | `;`만 치고 Enter |
| `OCI runtime exec failed: … "mysql": executable file not found` | PostgreSQL 컨테이너에 MySQL 명령을 쳤어요 | `psql -U postgres`로 들어가요 |

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json                    슬라이드 순서와 파트 구분
  *.html                       한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  demo.py                      실제 Docker와 postgres:18을 실행해 out.json에 출력을 담아요
  files.py                     compose.yaml, menu.sql 내용
  out.json                     demo.py가 만든 출력
  gen.py                       이 챕터의 장 생성
docker-postgres-slides.html    배포용 HTML
docker-postgres-slides.pdf     강사용 PDF
```

`demo.py`는 Docker가 켜진 리눅스에서 약 5분 걸려요. 밖에서 붙는 장면은 `--add-host host.docker.internal:host-gateway`로 만들었어요. Mac과 Windows의 Docker Desktop은 이 옵션 없이도 같은 이름을 써요.

```bash
uv run --with pyte python tools/demo.py
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/boxcheck.js slides
node ../tools/build_player.js slides docker-postgres-slides.html
node ../tools/export.js slides docker-postgres-slides.pdf
```

</details>

---

<!-- curriculum:nav -->

[← 이전: 33 · Docker 3 (MySQL 컨테이너)](../33-docker-mysql) · [커리큘럼](../README.md) · [다음: 35 · Docker 5 (명령어 한눈에 보기) →](../35-docker-cli)

<!-- /curriculum:nav -->
