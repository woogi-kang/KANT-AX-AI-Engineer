# 35 · Docker 5 (명령어 한눈에 보기)

> 29부터 34까지 docker 명령을 스무 개쯤 배웠어요. 여섯 챕터에 흩어져 있어서 막혔을 때 찾기 어려워요. 이번 챕터는 오늘 수업 예제(`my-pg`, `kant_shop.sql`) 그대로 명령을 묶음별로 다시 실행해 보고, 새로 나온 `docker cp`, `docker exec -i`, YAML과 compose 명령을 더한 뒤 치트시트 두 장으로 모아요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/35-docker-cli/docker-cli-slides.html) | [34 · Docker 4 (PostgreSQL 컨테이너로 데이터베이스 쓰기)](../34-docker-postgres) | 준비 중 |

<!-- /curriculum:top -->

## 학습 목표

- docker 명령을 할 일, 옵션, 이름으로 끊어 읽고, 긴 명령을 줄 끝 `\`로 나눠 쳐요.
- 이미지와 컨테이너 명령(`pull`, `images`, `run`, `ps`, `stop`, `start`, `restart`, `logs`, `rm`, `rmi`)을 지우는 순서까지 다시 써요.
- `docker logs --tail`로 마지막 몇 줄만, `-f`로 새 기록을 계속 보고 `Ctrl+C`로 멈춰요.
- `docker cp`로 SQL 파일을 컨테이너에 넣고 `psql -f`로 실행해요. `docker exec -i ... < 파일`로 한 번에 넘기고, 이때 `-it`를 쓰면 왜 거절되는지 말해요.
- `docker volume create`, `ls`, `inspect`, `rm`으로 볼륨을 다루고, 볼륨을 붙이면 컨테이너를 지워도 상품이 남는 것을 확인해요.
- YAML이 무엇인지, 들여쓰기가 왜 구조를 정하는지, 2칸과 4칸의 차이를 말해요.
- `docker run`의 옵션을 `compose.yaml`의 칸으로 옮기고, compose 명령(`config`, `up -d`, `ps`, `exec`, `logs`, `stop`, `start`, `restart`, `down`, `down -v`, `ls`, `pull`)을 써요.

## 시작하기 전에

| 할 일 | 챕터 |
| --- | :---: |
| `docker pull`, `run -d --name -p`, `ps`, `stop`, `start`, `restart`, `rm`, `rmi`, `logs` | 29 |
| `docker exec -it`, 볼륨 `-v`, `docker volume ls` `rm`, `compose.yaml`, `docker compose up -d` `down` | 30 |
| `docker exec 이름 명령`, `docker compose logs` `stop` `start` | 31 |
| PostgreSQL 컨테이너, `psql -U postgres`, `-d`, `-c`, `\c`, `\dt`, `/var/lib/postgresql` 볼륨 | 34 |
| 파이썬 들여쓰기를 상자 안의 상자로 읽기 | 28 |

Docker Desktop을 켜 두고 따라 쳐요. 터미널은 macOS 터미널이나 Windows Git Bash를 써요. Windows Git Bash에서는 컨테이너 안 경로가 바뀌지 않게 `export MSYS_NO_PATHCONV=1`을 먼저 쳐요. 34의 `pg` 컨테이너가 켜져 있으면 5432번이 겹치니 `docker stop pg`로 먼저 꺼요.

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1–4 | 표지, 오늘의 순서, 흩어진 명령, 명령 지도 |
| 1. 명령 읽는 법 | 5–7 | 할 일, 옵션, 이름의 순서, 옵션 표, `\`로 줄 나누기와 띄어쓰기 오류 |
| 2. 이미지와 컨테이너 | 8–12 | `pull` `images`, `run` `ps`, `stop` `start` `restart`, `logs --tail` `-f`, 지우는 순서와 오류 |
| 3. 컨테이너 안에서 작업하기 | 13–18 | `kant_shop.sql` 읽기, `docker cp`, `exec` 세 가지, `psql -f`, `exec -i < 파일`, `-it` 함정 |
| 4. 볼륨 | 19–21 | `volume create` `ls` `inspect`, 지워도 남는 상품, `volume is in use` |
| 5. YAML과 compose | 22–31 | YAML 모양, 들여쓰기, 2칸과 4칸, 탭과 YAML 오류, `run`과 `compose.yaml` 짝, `config`, `up` `ps` `exec`, `logs` `stop` `start` `restart`, `down` `down -v`, `container_name` |
| 6. 오류와 실제 상황 | 32–35 | 오류 여덟 가지, 수업 흐름 그대로, compose로 다시, 다 쓴 것 지우기 |
| 정리 | 36–39 | 긴 이름과 `--help`, docker 치트시트, compose 치트시트 |

## 핵심 개념

### 명령 지도

```
Docker Hub ── docker pull ──▶ 이미지 postgres:18 (붕어빵 틀)
                                   │ docker run
                                   ▼
내 폴더 ~/kant-shop ── docker cp / exec -i < ──▶ 컨테이너 my-pg (붕어빵) ◀── docker exec -it
  ├ kant_shop.sql                                   │ /var/lib/postgresql
  └ compose.yaml ── docker compose up -d            ▼
                                              볼륨 pgdata (붕어빵 밖 보관함)
```

### SQL 파일을 컨테이너에 건네는 두 방법

| | 방법 1 | 방법 2 |
| --- | --- | --- |
| 명령 | `docker cp kant_shop.sql my-pg:/tmp/kant_shop.sql` 뒤 `docker exec -it my-pg psql -U postgres -f /tmp/kant_shop.sql` | `docker exec -i my-pg psql -U postgres < kant_shop.sql` |
| 단계 | 복사하고 실행하는 두 단계 | 한 단계 |
| 옵션 | 직접 보는 화면이라 `-it` | 파일을 넘겨서 `-i`만 (`-it`는 거절돼요) |

### YAML 들여쓰기

- `이름: 값`을 한 줄에 하나씩 적어요. 쌍점 뒤에는 한 칸 띄워요.
- 더 들여 쓴 줄은 위 줄 안에 들어가요. 괄호가 없어서 칸 수가 곧 구조예요.
- 2칸이든 4칸이든 같은 단계끼리 칸이 맞으면 똑같이 읽혀요. 보통 2칸으로 적고, 한 파일 안에서는 한 가지로 맞춰요.

### docker run 옵션과 compose.yaml 칸

| `docker run` | `compose.yaml` |
| --- | --- |
| `--name my-pg` | `container_name: my-pg` |
| `-e POSTGRES_PASSWORD=admin1234` | `environment:` 아래 `POSTGRES_PASSWORD: admin1234` |
| `-p 5432:5432` | `ports:` 아래 `- "5432:5432"` |
| `-v pgdata:/var/lib/postgresql` | `volumes:` 아래 `- pgdata:/var/lib/postgresql` |
| `postgres:18` | `image: postgres:18` |
| `-d` | 파일에 적지 않고 `docker compose up -d` |

## 실습

`~/kant-shop` 폴더에 수업 파일 [kant_shop.sql](tools/kant_shop.sql)을 두고 그 폴더에서 쳐요. 출력은 실제로 실행한 결과예요. ID와 시간은 내 화면과 달라요.

```bash
mkdir ~/kant-shop
cd ~/kant-shop
```

### 1. 켜고 SQL 파일 넣기

```bash
docker run -d --name my-pg \
  -e POSTGRES_PASSWORD=admin1234 \
  -p 5432:5432 postgres:18
docker logs --tail 3 my-pg
```

`ready to accept connections`가 보이면 준비가 끝났어요. 다음은 방법 1이에요.

```
~/kant-shop $ docker cp kant_shop.sql my-pg:/tmp/kant_shop.sql
Successfully copied 610B (transferred 2.56kB) to my-pg:/tmp/kant_shop.sql
```

```
~/kant-shop $ docker exec -it my-pg psql -U postgres -f /tmp/kant_shop.sql
psql:/tmp/kant_shop.sql:2: NOTICE:  database "kant_shop" does not exist, skipping
DROP DATABASE
CREATE DATABASE
You are now connected to database "kant_shop" as user "postgres".
CREATE TABLE
INSERT 0 5
```

방법 2는 한 줄이에요. `-it`가 아니라 `-i`예요.

```bash
docker exec -i my-pg psql -U postgres < kant_shop.sql
```

### 2. 들어가서 확인하기

```
~/kant-shop $ docker exec -it my-pg psql -U postgres -d kant_shop -c "SELECT * FROM product"
 id |     name      | price  | stock
----+---------------+--------+-------
  1 | 무선 이어폰   |  35000 |   100
  2 | 게이밍 마우스 |  28000 |    85
  3 | 27인치 모니터 | 259000 |    15
  4 | USB-C 허브    |  19900 |   200
  5 | 노트북 거치대 |  24000 |     7
(5 rows)
```

`docker exec -it my-pg psql -U postgres -d kant_shop`으로 들어가면 `\dt`, `\d product`로 표를 보고 `\q`로 나와요.

### 3. 볼륨으로 지키기

```bash
docker stop my-pg
docker rm my-pg
docker volume create pgdata
docker volume inspect pgdata
docker run -d --name my-pg \
  -e POSTGRES_PASSWORD=admin1234 \
  -p 5432:5432 \
  -v pgdata:/var/lib/postgresql postgres:18
docker exec -i my-pg psql -U postgres < kant_shop.sql
docker stop my-pg
docker rm my-pg
```

같은 `docker run -v pgdata:...`로 다시 켜고 SELECT를 하면 상품 다섯 개가 그대로 나와요. 다 봤으면 컨테이너를 지우고 볼륨도 지워요.

```bash
docker stop my-pg
docker rm my-pg
docker volume rm pgdata
```

### 4. compose로 옮기기

`~/kant-shop/compose.yaml`을 만들어요. 들여쓰기는 띄어쓰기 2칸이에요.

```yaml
services:
  db:
    image: postgres:18
    container_name: my-pg
    environment:
      POSTGRES_PASSWORD: admin1234
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql

volumes:
  pgdata:
```

```bash
docker compose config
docker compose up -d
docker compose ps
docker exec -i my-pg psql -U postgres < kant_shop.sql
docker compose exec db psql -U postgres -d kant_shop -c "SELECT * FROM product"
docker compose logs --tail 3
```

```
~/kant-shop $ docker compose down
[+] down 2/2
 ✔ Container my-pg           Removed                                        0.2s
 ✔ Network kant-shop_default Removed                                        0.1s
~/kant-shop $ docker volume ls
DRIVER    VOLUME NAME
local     kant-shop_pgdata
```

`down`만 했다면 볼륨이 남아서, 다시 `docker compose up -d`로 켜면 상품이 그대로 있어요. 처음부터 다시 만들려면 `docker compose down -v`로 볼륨까지 지워요.

### 5. 다 쓴 것 지우기

```
~/kant-shop $ docker compose down -v
[+] down 3/3
 ✔ Container my-pg           Removed                                        0.2s
 ✔ Volume kant-shop_pgdata   Removed                                        0.1s
 ✔ Network kant-shop_default Removed                                        0.2s
~/kant-shop $ docker ps -a
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
~/kant-shop $ docker volume ls
DRIVER    VOLUME NAME
~/kant-shop $ docker rmi postgres:18
Untagged: postgres:18
Deleted: sha256:b9f6b8ff03b62f3cfd9d9ba3fe56226a9991c79d3fb46fd46536263bf02be553
~/kant-shop $ docker images
IMAGE   ID             DISK USAGE   CONTENT SIZE   EXTRA
```

## 명령어 요약

| 명령 | 하는 일 |
| --- | --- |
| `docker pull postgres:18` | 이미지 받기 |
| `docker images` | 받은 이미지 목록 (`docker image ls`와 같아요) |
| `docker run -d --name my-pg -e ... -p 5432:5432 postgres:18` | 뒤에서 켜기, 이름, 환경 변수, 포트 |
| `docker ps` / `docker ps -a` | 켜진 컨테이너 / 꺼진 것까지 (`docker container ls`와 같아요) |
| `docker stop` / `start` / `restart my-pg` | 끄기 / 켜기 / 껐다가 바로 켜기 |
| `docker logs --tail 3 my-pg` | 기록의 마지막 3줄 |
| `docker logs -f my-pg` | 새 기록을 계속 보기, `Ctrl+C`로 멈춤 |
| `docker rm my-pg` | 꺼진 컨테이너 지우기 |
| `docker rmi postgres:18` | 이미지 지우기 (쓰는 컨테이너 먼저 지우기) |
| `docker cp kant_shop.sql my-pg:/tmp/kant_shop.sql` | 내 파일을 컨테이너로 복사 |
| `docker cp my-pg:/tmp/kant_shop.sql ./copy.sql` | 컨테이너 파일을 내 폴더로 꺼내기 |
| `docker exec -it my-pg bash` | 컨테이너 안 bash 열기, `exit`로 나오기 |
| `docker exec my-pg ls /tmp` | 명령 하나만 실행 |
| `docker exec -it my-pg psql -U postgres -f /tmp/kant_shop.sql` | 컨테이너 안 SQL 파일 실행 |
| `docker exec -i my-pg psql -U postgres < kant_shop.sql` | 내 폴더의 SQL 파일을 바로 넘겨 실행 |
| `docker volume create pgdata` | 볼륨 만들기 |
| `docker volume ls` / `inspect pgdata` / `rm pgdata` | 볼륨 목록 / 자세히 / 지우기 |
| `docker compose config` | compose.yaml을 읽은 그대로 보기, YAML 오류 확인 |
| `docker compose up -d` | 만들고 뒤에서 켜기 |
| `docker compose ps` / `ps -a` | 이 폴더의 컨테이너 / 꺼진 것까지 |
| `docker compose exec db psql -U postgres -d kant_shop` | 서비스 이름으로 들어가기 |
| `docker compose logs --tail 3` | 서비스 기록, `-f`로 계속 보기 |
| `docker compose stop` / `start` / `restart` | 끄기 / 켜기 / 껐다가 바로 켜기 |
| `docker compose down` | 컨테이너와 네트워크 지우기, 볼륨은 남김 |
| `docker compose down -v` | 볼륨까지 지우기 |
| `docker compose ls` | compose로 켠 프로젝트 목록 |
| `docker compose pull` | compose.yaml의 이미지를 미리 받기 |
| `docker cp --help` | 쓰는 모양(Usage), 긴 이름(Aliases), 옵션 보기 |

## 문제 해결

| 메시지 | 원인 | 해결 |
| --- | --- | --- |
| `Conflict. The container name "/my-pg" is already in use` | 같은 이름의 컨테이너가 있어요 | `docker rm my-pg` 뒤 다시 켜요 |
| `Bind for 0.0.0.0:5432 failed: port is already allocated` | 5432번을 다른 컨테이너가 써요 | 하나를 끄거나 `-p 5433:5432` |
| `docker: invalid reference format` 과 `-e: command not found` | 줄 끝 `\` 뒤에 띄어쓰기가 있어요 | 줄은 `\`로 끝나야 해요 |
| `cannot attach stdin to a TTY-enabled container because stdin is not a terminal` | `< 파일`과 `-it`를 같이 썼어요 | `-i`만 써요 |
| `lstat ...: no such file or directory` | `docker cp`로 보낼 파일 이름이 틀렸거나 다른 폴더예요 | `ls`로 이름과 위치를 확인해요 |
| `No such container: my-pg` | compose.yaml에 `container_name`이 없어 이름이 `kant-shop-db-1`이에요 | `docker compose ps`로 이름을 보거나 `docker compose exec db` |
| `volume is in use` | 그 볼륨을 쓰는 컨테이너가 있어요 | 컨테이너를 `stop`, `rm` 한 뒤 `docker volume rm` |
| `found character that cannot start any token` | compose.yaml에 탭이 있어요 | 탭을 띄어쓰기로 바꿔요 |
| `mapping values are not allowed in this context` | 한 줄만 칸이 어긋났거나 쌍점 뒤 띄어쓰기가 빠졌어요 | 알려 준 줄과 바로 위 줄을 같이 보고 `docker compose config`로 다시 확인해요 |

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json             슬라이드 순서와 파트 구분
  *.html                한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  demo.py               실제 Docker와 postgres:18을 실행해 out.json에 출력을 담아요
  ptyrun.py             터미널 화면 그대로 출력을 받는 도우미
  files.py              compose.yaml과 오류용 파일 내용
  kant_shop.sql         수업 레포(IndieGameMaker/kant_docker)의 파일 그대로
  out.json              demo.py가 만든 출력
  gen.py                이 챕터의 장 생성
docker-cli-slides.html  배포용 HTML
docker-cli-slides.pdf   강사용 PDF
```

`demo.py`는 Docker가 켜진 리눅스에서 약 3분 걸려요. 시작할 때 모든 컨테이너와 볼륨을 지우니 연습용 환경에서만 돌려요.

```bash
uv run --with pyte python tools/demo.py
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/boxcheck.js slides
node ../tools/build_player.js slides docker-cli-slides.html
node ../tools/export.js slides docker-cli-slides.pdf
```

</details>

---

<!-- curriculum:nav -->

[← 이전: 34 · Docker 4 (PostgreSQL 컨테이너로 데이터베이스 쓰기)](../34-docker-postgres) · [커리큘럼](../README.md)

<!-- /curriculum:nav -->
