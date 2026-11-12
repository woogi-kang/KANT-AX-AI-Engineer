# 33 · Docker 3 (MySQL 컨테이너)

> 32에서 표, 타입, 기본 키를 그림으로 읽고 SQL을 맛봤어요. 이번에는 MySQL을 컴퓨터에 설치하지 않고 컨테이너로 켜요. 데이터베이스와 표를 직접 만들고, 컨테이너를 지워도 표가 남도록 볼륨에 연결해요. 29의 `docker run`, 30의 볼륨과 compose, 31의 `docker exec 이름 명령`을 이어서 써요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/33-docker-mysql/docker-mysql-slides.html) | [31 · nginx 기초 (웹 서버와 리버스 프록시)](../31-nginx-basics) | 준비 중 |

<!-- /curriculum:top -->

## 학습 목표

- 공식 이미지 `mysql:8.4`를 `-e` 환경 변수로 켜고, `docker logs`에서 `port: 3306`을 보고 준비가 끝났는지 알아요.
- `docker exec -it db mysql -u root -p`로 들어가서 SQL을 치고 `exit`로 나와요.
- `CREATE DATABASE`, `USE`, `CREATE TABLE`, `SHOW TABLES`, `DESCRIBE`, `INSERT`, `SELECT`, `DROP`으로 데이터베이스와 표를 만들고, 보고, 지워요.
- 관리자 root와 `MYSQL_USER`로 만든 앱 계정이 어떻게 다른지 말해요.
- 컨테이너를 지우면 표가 왜 사라지는지 말하고, `-v cafe-data:/var/lib/mysql`로 지켜요.
- 긴 `docker run`을 `compose.yaml`로 옮기고 `docker compose up -d`, `down`으로 켜고 꺼요.
- 비밀번호 빠짐, 너무 빨리 접속, 3306 포트 겹침, SQL 실수, 볼륨이 남아 바뀌지 않는 비밀번호를 오류 메시지로 찾아 고쳐요.

## 시작하기 전에

| 할 일 | 챕터 |
| --- | :---: |
| 표, 행과 열, 타입, 기본 키, SQL 네 문장 읽기 | 32 |
| `docker pull` `run -d --name -p` `ps -a` `stop` `rm` `logs`, 포트 겹침 오류 | 29 |
| `docker exec -it`, 볼륨 `-v 이름:경로`, `docker volume ls` `rm`, `compose.yaml`, `docker compose up -d` `ps` `down` | 30 |
| `docker exec 이름 명령`으로 명령 하나만 실행하기 | 31 |

Docker Desktop을 켜 두고 따라 쳐요. 터미널은 macOS 터미널이나 Windows Git Bash를 써요. Windows Git Bash에서는 30처럼 새 창마다 `export MSYS_NO_PATHCONV=1`을 먼저 쳐요.

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1–4 | 표지, 오늘의 순서, 직접 설치와 컨테이너, 큰 그림 |
| 1. MySQL 컨테이너 켜기 | 5–9 | `mysql:8.4` 받기, `docker run`, `-e` 환경 변수, `docker logs`, `docker exec -it db mysql` |
| 2. 데이터베이스와 표 만들기 | 10–16 | `SHOW DATABASES`, `CREATE DATABASE`와 `USE`, `CREATE TABLE`, `SHOW TABLES`와 `DESCRIBE`, `INSERT`, `SELECT`, `DROP` |
| 3. 계정과 접속 방법 | 17–19 | root와 앱 계정, bash로 먼저 들어가기, `-e`로 한 문장만 실행 |
| 4. 볼륨과 compose | 20–25 | 지우면 사라지는 표, `/var/lib/mysql`, 이름 있는 볼륨, `compose.yaml`, `docker compose exec`, nginx와 비교 |
| 5. 자주 나는 오류 | 26–31 | 비밀번호 빠짐, 너무 빨리 접속, 비밀번호 틀림, 3306 겹침, SQL 실수, 볼륨이 남은 함정 |
| 6. 실제 상황 예제 | 32–33 | 다음 날에도 남는 주문, SQL 파일로 메뉴 표 채우기 |
| 정리 | 34–35 | 막힐 때, 한 장 요약 |

## 핵심 개념

### 컨테이너, 서버, 데이터베이스, 표

```
mysql:8.4 컨테이너 (이름 db)
└── MySQL 서버 (3306번 포트)
    ├── cafe 데이터베이스
    │   └── orders 표 (id, menu, qty)
    └── mysql, sys …  (MySQL이 스스로 쓰는 것)
```

표는 컨테이너 안 `/var/lib/mysql` 폴더에 파일로 저장돼요. 이 폴더에 이름 있는 볼륨을 붙여야 컨테이너를 지워도 표가 남아요.

### -e 환경 변수

| 이름 | 하는 일 |
| --- | --- |
| `MYSQL_ROOT_PASSWORD` | 관리자 root의 비밀번호예요. 꼭 있어야 해요 |
| `MYSQL_DATABASE` | 처음 켤 때 만들 데이터베이스 이름이에요 |
| `MYSQL_USER`, `MYSQL_PASSWORD` | 앱이 쓸 계정과 비밀번호예요. 이 계정은 `MYSQL_DATABASE`만 쓸 수 있어요 |

이 값은 볼륨이 비어 있을 때, 처음 준비할 때 한 번만 읽어요. 볼륨에 데이터가 있으면 바꿔 줘도 그대로예요.

### 접속하는 세 가지 방법

| 명령 | 언제 |
| --- | --- |
| `docker exec -it db mysql -u root -p` | SQL을 여러 개 칠 때. 기본이에요 |
| `docker exec -it db bash` 뒤 `mysql -u root -p` | 컨테이너 안도 같이 볼 때. 나올 때 `exit` 두 번 |
| `docker exec db mysql -u root -pcafe1234 cafe -e "SHOW TABLES;"` | 한 문장만 확인할 때. 연습할 때만 |

`-p` 뒤에 비밀번호를 붙이면 묻지 않지만 명령 기록에 남아서 Warning이 나와요. 맨 끝에 `cafe`처럼 데이터베이스 이름을 적으면 그 데이터베이스에 바로 들어가요.

## 실습

출력은 실제로 실행한 결과예요. 컨테이너 ID, 시각, 걸린 시간은 내 화면과 달라요.

### 1. MySQL 컨테이너 켜기

```bash
docker pull mysql:8.4
docker run -d --name db -e MYSQL_ROOT_PASSWORD=cafe1234 -e MYSQL_DATABASE=cafe -p 3306:3306 mysql:8.4
docker logs db
```

처음에는 10초쯤 걸려요. 마지막 줄에 `port: 3306`이 보이면 다 켜진 거예요. `port: 0`이 나온 줄은 잠깐 켠 임시 서버라서 아직이에요.

```
… /usr/sbin/mysqld: ready for connections. Version: '8.4.13'  socket: '/var/run/mysqld/mysqld.sock'  port: 3306  MySQL Community Server - GPL.
```

```bash
docker exec db env
docker exec -it db mysql -u root -p
```

`Enter password:`가 나오면 `cafe1234`를 쳐요. 화면에 안 보여도 정상이에요. `mysql>`이 나오면 들어간 거예요.

### 2. 데이터베이스와 표 만들기

`mysql>` 뒤에 한 줄씩 쳐요. 끝의 `;`를 빠뜨리지 않아요.

```sql
SHOW DATABASES;
CREATE DATABASE shop;
USE shop;
SHOW TABLES;
exit
```

`USE shop;`을 치면 `Database changed`가 나오고, 방금 만든 shop은 비어 있어서 `Empty set`이 나와요. 이번에는 cafe에 바로 들어가서 표를 만들어요.

```bash
docker exec -it db mysql -u root -p cafe
```

```sql
CREATE TABLE orders (id INT PRIMARY KEY, menu VARCHAR(20), qty INT);
SHOW TABLES;
DESCRIBE orders;
INSERT INTO orders VALUES (1, 'latte', 2);
INSERT INTO orders VALUES (2, 'americano', 1);
SELECT * FROM orders;
SELECT menu, qty FROM orders;
```

```
+----+-----------+------+
| id | menu      | qty  |
+----+-----------+------+
|  1 | latte     |    2 |
|  2 | americano |    1 |
+----+-----------+------+
2 rows in set (0.00 sec)
```

연습용 shop은 지워요. DROP은 묻지 않고 바로 지우고, 되돌릴 수 없어요.

```sql
USE shop;
CREATE TABLE test (id INT);
DROP TABLE test;
DROP DATABASE shop;
SHOW DATABASES;
exit
```

### 3. 앱 계정과 여러 접속 방법

db를 지우고 `-e` 두 개를 더해 다시 켜요. 이때 2번에서 만든 표가 사라져요. 왜 그런지는 4번에서 봐요.

```bash
docker stop db
docker rm db
docker run -d --name db -e MYSQL_ROOT_PASSWORD=cafe1234 -e MYSQL_DATABASE=cafe -e MYSQL_USER=cafe -e MYSQL_PASSWORD=cafe5678 -p 3306:3306 mysql:8.4
docker logs db
docker exec -it db mysql -u cafe -p cafe
```

비밀번호는 `cafe5678`이에요.

```sql
SHOW DATABASES;
CREATE TABLE orders (id INT PRIMARY KEY, menu VARCHAR(20), qty INT);
CREATE DATABASE shop;
exit
```

```
ERROR 1044 (42000): Access denied for user 'cafe'@'%' to database 'shop'
```

cafe 계정에는 cafe 데이터베이스만 보이고, 새 데이터베이스는 못 만들어요. 앱에는 root 대신 이 계정을 줘요.

```bash
docker exec -it db bash
mysql -u root -p cafe
```

`bash-5.1#` 표시에서 mysql을 열었어요. `SHOW TABLES;`를 쳐 보고 `exit`를 두 번 쳐서 나와요. 한 문장만 볼 때는 들어가지 않고 실행해요.

```bash
docker exec db mysql -u root -pcafe1234 cafe -e "SHOW TABLES;"
```

```
Tables_in_cafe
orders
mysql: [Warning] Using a password on the command line interface can be insecure.
```

### 4. 지워도 남게 볼륨 붙이기

```bash
docker stop db
docker rm db
docker run -d --name db -e MYSQL_ROOT_PASSWORD=cafe1234 -e MYSQL_DATABASE=cafe -p 3306:3306 mysql:8.4
docker exec -it db mysql -u root -p cafe
```

```
mysql> SELECT * FROM orders;
ERROR 1146 (42S02): Table 'cafe.orders' doesn't exist
```

볼륨 없이 켠 컨테이너를 지우면 `/var/lib/mysql`이 같이 지워져요. 이번에는 이름 있는 볼륨을 붙여요.

```bash
docker stop db
docker rm db
docker run -d --name db -e MYSQL_ROOT_PASSWORD=cafe1234 -e MYSQL_DATABASE=cafe -p 3306:3306 -v cafe-data:/var/lib/mysql mysql:8.4
```

10초쯤 기다렸다가 들어가서 2번처럼 orders 표를 만들고 `(1, 'latte', 2)`를 넣어요. 그다음 지우고 같은 명령으로 다시 켜요.

```bash
docker stop db
docker rm db
docker volume ls
docker run -d --name db -e MYSQL_ROOT_PASSWORD=cafe1234 -e MYSQL_DATABASE=cafe -p 3306:3306 -v cafe-data:/var/lib/mysql mysql:8.4
docker exec -it db mysql -u root -p cafe
```

`SELECT * FROM orders;`를 치면 1번 주문이 그대로 나와요. 다 봤으면 db를 지우고 볼륨도 지워요.

```bash
docker stop db
docker rm db
docker volume rm cafe-data
```

`docker volume ls`에 긴 이름의 볼륨이 보이면 볼륨 없이 켰던 컨테이너가 남긴 것이에요. `docker volume rm 이름`으로 지워도 돼요.

### 5. compose로 옮기기

```bash
mkdir ~/cafe-db
cd ~/cafe-db
```

VS Code로 `compose.yaml`을 만들어요.

```yaml
services:
  db:
    image: mysql:8.4
    environment:
      MYSQL_ROOT_PASSWORD: cafe1234
      MYSQL_DATABASE: cafe
    ports:
      - "3306:3306"
    volumes:
      - cafe-data:/var/lib/mysql

volumes:
  cafe-data:
```

```bash
docker compose up -d
docker compose ps
docker compose exec db mysql -u root -p cafe
```

```
[+] up 3/3
 ✔ Network cafe-db_default  Created
 ✔ Volume cafe-db_cafe-data Created
 ✔ Container cafe-db-db-1   Started
```

orders 표를 만들고 주문을 넣은 뒤 `docker compose down`으로 꺼요. 다시 `docker compose up -d`로 켜면 주문이 그대로 있어요. `down`은 볼륨을 남겨요.

### 6. SQL 파일로 메뉴 표 채우기

`~/cafe-db/init/menu.sql`을 만들어요.

```sql
CREATE TABLE menu (id INT PRIMARY KEY, name VARCHAR(20), price INT);
INSERT INTO menu VALUES (1, 'americano', 4000);
INSERT INTO menu VALUES (2, 'latte', 4500);
INSERT INTO menu VALUES (3, 'cake', 5000);
```

`compose.yaml`의 `volumes`에 한 줄을 더해요.

```yaml
    volumes:
      - cafe-data:/var/lib/mysql
      - ./init:/docker-entrypoint-initdb.d
```

이 파일은 처음 준비할 때만 실행돼요. 5번의 볼륨이 남아 있으면 건너뛰니, 볼륨까지 지우고 켜요. `-v`를 붙이면 쌓인 주문도 같이 지워지니 연습할 때만 써요.

```bash
docker compose down -v
docker compose up -d
docker compose logs db
docker compose exec db mysql -u root -p cafe
```

logs에 `running /docker-entrypoint-initdb.d/menu.sql`이 보이고, `SELECT * FROM menu;`로 메뉴 세 개가 나와요. 다 봤으면 `docker compose down`으로 꺼요.

## 명령어 요약

| 명령 | 하는 일 |
| --- | --- |
| `docker run -d --name db -e MYSQL_ROOT_PASSWORD=cafe1234 -e MYSQL_DATABASE=cafe -p 3306:3306 mysql:8.4` | MySQL 서버를 켜요 |
| `docker logs db` | 준비가 끝났는지 봐요. `port: 3306`이면 끝 |
| `docker exec -it db mysql -u root -p cafe` | root로 cafe에 들어가요. 나올 때는 `exit` |
| `docker exec db mysql -u root -p비밀번호 cafe -e "SQL"` | SQL 한 문장만 실행해요 |
| `-e MYSQL_USER=cafe -e MYSQL_PASSWORD=cafe5678` | 앱이 쓸 계정을 만들어요 |
| `-v cafe-data:/var/lib/mysql` | 지워도 남는 볼륨에 표를 저장해요 |
| `SHOW DATABASES;`, `CREATE DATABASE 이름;`, `USE 이름;` | 데이터베이스 목록, 만들기, 들어가기 |
| `SHOW TABLES;`, `DESCRIBE 표;` | 표 목록, 표의 열 보기 |
| `CREATE TABLE 표 (열 타입, …);` | 빈 표를 만들어요 |
| `INSERT INTO 표 VALUES (…);`, `SELECT * FROM 표;` | 행 넣기, 꺼내 보기 |
| `DROP TABLE 표;`, `DROP DATABASE 이름;` | 지워요. 되돌릴 수 없어요 |
| `docker compose exec db mysql -u root -p cafe` | compose로 켠 db에 들어가요 |
| `docker compose down`, `docker compose down -v` | 끄기, 볼륨까지 지우기 |

## 문제 해결

| 메시지 | 원인 | 해결 |
| --- | --- | --- |
| `docker ps -a`에 `Exited (1)`, logs에 `Database is uninitialized and password option is not specified` | `-e MYSQL_ROOT_PASSWORD`를 빠뜨렸어요 | `docker rm db` 뒤 `-e`를 넣어 다시 켜요 |
| `ERROR 2002 (HY000): Can't connect to local MySQL server through socket` | 아직 준비 중이에요 | `docker logs db`에 `port: 3306`이 나오면 다시 들어가요 |
| `ERROR 1045 (28000): Access denied for user 'root'@'localhost' (using password: YES)` | 비밀번호가 틀렸어요 | 다시 쳐요. `docker exec db env`로 정한 값을 봐요 |
| 새 비밀번호로 켰는데 `ERROR 1045` | 볼륨에 예전 데이터가 있어서 `-e`를 읽지 않았어요 | 예전 비밀번호로 들어가요. 처음부터 하려면 `docker volume rm cafe-data` (표도 지워져요) |
| `Bind for 0.0.0.0:3306 failed: port is already allocated` | 다른 컨테이너나 직접 설치한 MySQL이 3306을 써요 | `docker ps`로 찾아 끄거나 `-p 3307:3306` |
| `mysql>` 대신 `->`가 나와요 | 끝의 `;`가 빠졌어요 | `;`를 치고 Enter |
| `ERROR 1064 (42000): You have an error in your SQL syntax` | 철자나 문법이 틀렸어요(`order`는 SQL 낱말) | `near` 뒤에 적힌 곳 근처를 고쳐요 |
| `ERROR 1146 (42S02): Table 'cafe.orders' doesn't exist` | 표가 없어요. 볼륨 없이 컨테이너를 지웠을 수도 있어요 | `SHOW TABLES;`로 보고, 지켜야 하면 볼륨을 붙여요 |
| `ERROR 1044 (42000): Access denied for user 'cafe'@'%' to database 'shop'` | 앱 계정은 cafe만 쓸 수 있어요 | 새 데이터베이스는 root로 만들어요 |
| `ERROR 1062`, `ERROR 1366` | 같은 기본 키, 타입이 다른 값(32에서 봤어요) | id를 바꾸거나 타입에 맞는 값을 넣어요 |
| `menu.sql`이 실행되지 않아요 | 볼륨에 데이터가 있어서 처음 준비를 건너뛰었어요 | `docker compose down -v` 뒤 `up -d` (연습할 때만) |

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분 (gen.py가 만들어요)
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  files.py         실습 파일 내용 (compose.yaml 두 단계, init/menu.sql)
  ptyrun.py        mysql처럼 키보드로 치는 명령을 가짜 터미널에서 실행
  demo.py          1, 2, 4~6번 실습을 실제 Docker와 MySQL로 실행해서 tools/out.json에 저장
  demo_user.py     3번 실습(앱 계정, bash, -e 한 문장)을 실행해서 out.json에 더해요
  demo_sql.py      CREATE DATABASE, USE, DESCRIBE, DROP 장을 실행해서 out.json에 더해요
  out.json         실제 실행 출력
  gen.py           모든 장과 deck.json 생성
docker-mysql-slides.html  배포용 HTML
docker-mysql-slides.pdf   강사용 PDF
```

검사, HTML, PDF를 만드는 공용 도구는 맨 위 [tools/](../tools)에 한 벌만 있어요. 명령은 이 폴더에서 쳐요. demo 스크립트는 Docker 데몬이 있어야 하고, db 컨테이너와 cafe-data 볼륨을 지우고 시작해요. demo.py를 먼저 돌리고 나머지 둘을 돌려요.

```bash
uv run -q --with pyte python tools/demo.py
uv run -q --with pyte python tools/demo_user.py
uv run -q --with pyte python tools/demo_sql.py
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/boxcheck.js slides
node ../tools/build_player.js slides docker-mysql-slides.html
node ../tools/export.js slides docker-mysql-slides.pdf
```

출력은 Docker 29.9.2, Compose v5.6.1, MySQL 8.4.13에서 `/home/kim`을 두고 실행한 결과예요.

범위: `mysql:8.4`, `-e` 환경 변수 네 개, 처음 준비와 `port: 3306`, `docker exec -it db mysql -u root -p`와 bash, `-e "SQL"`, `-p비밀번호` 경고, root와 앱 계정, `SHOW DATABASES` `CREATE DATABASE` `USE` `SHOW TABLES` `CREATE TABLE` `DESCRIBE` `INSERT` `SELECT` `DROP TABLE` `DROP DATABASE`, `/var/lib/mysql`과 이름 있는 볼륨, 이름 없는 볼륨, `compose.yaml`의 `environment`와 맨 아래 `volumes:`, `docker compose exec`, `down -v`, `/docker-entrypoint-initdb.d`를 다뤄요. `WHERE`, `UPDATE`, `DELETE`, JOIN, 인덱스, 트랜잭션, `CREATE USER`와 `GRANT`, `mysqldump` 백업, 파이썬에서 접속하기, GUI 도구는 다루지 않아요. PostgreSQL은 34에서 다뤄요.

</details>

---

<!-- curriculum:nav -->

[← 이전: 31 · nginx 기초 (웹 서버와 리버스 프록시)](../31-nginx-basics) · [커리큘럼](../README.md)

<!-- /curriculum:nav -->
