# 31 · nginx 기초 (웹 서버와 리버스 프록시)

> 29, 30에서는 컨테이너마다 `-p`로 포트를 하나씩 열었어요. 앱이 늘면 손님이 외울 주소의 포트 번호도 같이 늘어요. 이번에는 nginx를 문 앞에 두고, 폴더 속 파일은 nginx가 바로 주고 앱 여러 개는 80번 포트 하나로 묶어요. 30의 `~/cafe` 폴더와 `compose.yaml`을 이어서 써요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/31-nginx-basics/nginx-basics-slides.html) | [30 · Docker 2 (내 프로그램을 이미지로 만들기)](../30-docker-image) | 준비 중 |

<!-- /curriculum:top -->

## 학습 목표

- 웹 서버(nginx)와 앱 서버(FastAPI 같은 것)가 하는 일이 어떻게 다른지 말해요.
- `curl 주소`로 브라우저가 받는 글자를 터미널에서 봐요.
- 주소 뒤의 경로가 폴더 속 파일 이름과 이어진다는 것을 말하고, `docker logs`로 결과 번호(200, 404)를 읽어요.
- `default.conf`를 읽고, 내 설정 파일을 `-v ./conf:/etc/nginx/conf.d`로 연결해요.
- 리버스 프록시가 무엇인지 말하고, `proxy_pass http://menu/;`로 요청을 뒤의 앱에 넘겨요.
- `compose.yaml`에 nginx와 앱 두 개를 적고, 밖으로 여는 포트를 nginx의 80번 하나로 둬요.
- 설정을 고친 뒤 `nginx -t`로 검사하고 `nginx -s reload`로 다시 읽혀요.
- 502, 504, `nginx -t` 오류, 80번 포트 겹침을 기록을 보고 고쳐요.

## 시작하기 전에

| 할 일 | 챕터 |
| --- | :---: |
| Docker Desktop, `docker run -d --name -p`, `ps`, `stop`, `rm`, `logs`, 포트 겹침 오류 | 29 |
| `docker exec -it`, `-v ./폴더:경로`, `compose.yaml`, `docker compose up -d`, `ps`, `down` | 30 |
| 들여쓰기를 상자 안의 상자로 읽기 | 28 |

Docker Desktop을 켜 두고 따라 쳐요. 터미널은 macOS 터미널이나 Windows Git Bash를 써요. `curl`은 두 곳 모두에 들어 있어요.

Windows Git Bash에서는 30처럼 새 창마다 `export MSYS_NO_PATHCONV=1`을 먼저 쳐요.

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1–6 | 표지, 오늘의 순서, 앱마다 늘어나는 포트, 큰 그림, 웹 서버와 앱 서버, 실습 폴더 준비 |
| 1. nginx로 파일 내주기 | 7–12 | `curl`, 경로와 파일, `docker logs`로 요청 기록 읽기, `default.conf`, `server`와 `location` 상자, 내 설정 파일 연결 |
| 2. 리버스 프록시 | 13–21 | 리버스 프록시란, 연습용 앱 whoami, `proxy_pass`, 서비스 셋인 `compose.yaml`, 포트 없이 `/menu/`, `nginx -t`와 `reload`, 닫힌 앱 포트, 주소 셋을 하나로, `-p`와 비교 |
| 3. 자주 나는 오류 | 22–25 | 502와 504, `nginx -t` 오류 두 가지, `proxy_pass` 끝의 `/`, 80번 포트 겹침 |
| 4. 실제 상황 예제 | 26–27 | 홈페이지와 앱 둘을 주소 하나로, 이벤트 앱 붙이기 |
| 정리 | 28–29 | 막힐 때, 한 장 요약 |

## 핵심 개념

### 웹 서버와 앱 서버

| | 웹 서버 | 앱 서버 |
| --- | --- | --- |
| 예 | nginx | FastAPI (서버 켜기는 아직 안 배워서, 이 챕터는 연습용 `traefik/whoami`) |
| 요청이 오면 | 폴더에서 파일을 찾아 그대로 보내요 | 코드를 실행해서 그때그때 답을 만들어요 |
| 카페로 치면 | 진열대에서 빵을 집어 주는 카운터 | 주문받은 음료를 만드는 주방 |

보통은 둘을 같이 써요. nginx를 앞에 두고 파일은 nginx가 바로 주고, 앱의 일은 뒤의 앱 서버에 넘겨요.

### 리버스 프록시

```
브라우저 ──localhost/menu/──▶ nginx (80번) ──▶ menu 앱
         ◀───── 답을 그대로 ─────         ◀── 답
```

nginx는 직접 답하지 않고 뒤의 menu 앱에 요청을 대신 보내고, 받은 답을 브라우저에 그대로 건네요. 프록시(proxy)는 대신해 주는 사람이라는 뜻이에요. 서버 앞에서 대신 받아 주니 리버스(거꾸로) 프록시라고 불러요.

웹 주소에 포트를 안 적으면 80번으로 가요. 그래서 `localhost`는 `localhost:80`과 같아요. nginx 하나만 `"80:80"`으로 열고, 앱은 경로(`/menu/`, `/order/`)로 골라요. 앱을 늘릴 때는 새 포트 대신 `location` 상자를 하나 더 써요.

### 설정 파일 읽기

```nginx
server {
    listen 80;

    location / {
        root /usr/share/nginx/html;
        index index.html;
    }

    location /menu/ {
        proxy_pass http://menu/;
    }
}
```

| 줄 | 뜻 |
| --- | --- |
| `server { }` | 웹사이트 하나예요. 중괄호는 상자예요 |
| `listen 80;` | 80번 포트에서 요청을 기다려요 |
| `location / { }` | `/`로 시작하는 주소에 이 상자의 규칙을 써요 |
| `root`, `index` | 파일을 찾을 폴더, 파일 이름 없이 오면 줄 파일이에요 |
| `proxy_pass http://menu/;` | `menu`라는 서비스로 요청을 넘겨요 |

줄 끝의 `;`는 한 줄이 끝났다는 표시예요. `localhost/menu/`는 `/`로도 `/menu/`로도 시작하는데, nginx는 더 길게 맞는 `/menu/` 상자를 골라요. `proxy_pass` 끝에 `/`를 붙이면 앞의 `/menu/`를 떼고 넘겨서, `localhost/menu/today`를 앱은 `/today`로 받아요. 이 챕터에서는 붙이는 쪽으로 써요.

## 실습

출력은 실제로 실행한 결과예요. 컨테이너 ID, 시각, IP는 내 화면과 달라요.

### 1. 준비하기

30에서 만든 `~/cafe` 폴더로 가요. 30의 web이 켜져 있으면 먼저 꺼요.

```bash
cd ~/cafe
docker compose down
mkdir conf
docker pull traefik/whoami
```

VS Code로 `site/index.html`을 오늘의 홈페이지로 바꿔요.

```html
<meta charset="utf-8">
<h1>KANT 카페</h1>
<p><a href="/menu/">메뉴 보기</a></p>
<p><a href="/order/">주문하기</a></p>
```

### 2. nginx로 파일 내주기

```bash
docker run -d --name web -p 8080:80 -v ./site:/usr/share/nginx/html nginx
curl localhost:8080
```

`site/index.html`의 글자가 그대로 나와요. 브라우저도 같은 글자를 받아서 제목과 링크로 그려요. 이번에는 없는 파일을 달라고 해 봐요.

```bash
curl localhost:8080/event.html
```

```
<html>
<head><title>404 Not Found</title></head>
...
```

VS Code로 `site/event.html`을 만들고(`<meta charset="utf-8">`와 `<h1>이번 주 이벤트</h1>` 두 줄) 다시 쳐요. nginx를 다시 켜지 않아도 바로 나와요.

```bash
curl localhost:8080/event.html
docker logs web
```

```
...
172.17.0.1 - - [12/Nov/2026:02:02:30 +0000] "GET /event.html HTTP/1.1" 404 153 "-" "curl/8.5.0" "-"
172.17.0.1 - - [12/Nov/2026:02:02:30 +0000] "GET /event.html HTTP/1.1" 200 53 "-" "curl/8.5.0" "-"
```

한 줄은 보낸 쪽 주소, 시각, 받은 요청, 결과 번호 순서예요. 200은 잘 줬다, 404는 그런 파일이 없다는 뜻이에요.

`docker exec web cat /etc/nginx/conf.d/default.conf`로 기본 설정 파일도 봐요. `docker exec 이름 명령`은 컨테이너 안에서 명령 하나만 실행하고 돌아와요.

### 3. 내 설정 파일 연결하기

VS Code로 `conf/default.conf`를 만들어요. 내용은 위 "설정 파일 읽기"에서 `location /menu/` 상자를 뺀 여덟 줄이에요.

web을 지우고 `-v`를 하나 더 붙여 다시 띄워요.

```bash
docker stop web
docker rm web
docker run -d --name web -p 8080:80 -v ./site:/usr/share/nginx/html -v ./conf:/etc/nginx/conf.d nginx
curl localhost:8080
```

결과는 2번과 같아요. 이제 VS Code로 설정 파일을 고칠 수 있어요. 다 봤으면 지워요.

```bash
docker stop web
docker rm web
```

### 4. 연습용 앱 whoami 보기

```bash
docker run -d --name menu -p 8001:80 traefik/whoami --name menu
curl localhost:8001
```

```
Name: menu
Hostname: 2331288aea06
...
GET / HTTP/1.1
Host: localhost:8001
...
```

이미지 뒤의 `--name menu`는 whoami에게 전하는 옵션이에요. 답의 `Name`이 menu로 나와요. 다 봤으면 `docker stop menu`, `docker rm menu`로 지워요.

### 5. 리버스 프록시로 묶기

`conf/default.conf`에 `/menu/` 상자를 더해서 위 "설정 파일 읽기"와 같게 만들어요. 위의 `location /` 상자는 그대로 둬요.

30의 `compose.yaml`을 서비스 셋으로 바꿔요.

```yaml
services:
  web:
    image: nginx
    ports:
      - "80:80"
    volumes:
      - ./site:/usr/share/nginx/html
      - ./conf:/etc/nginx/conf.d
    depends_on:
      - menu
      - order
  menu:
    image: traefik/whoami
    command: --name menu
  order:
    image: traefik/whoami
    command: --name order
```

- 서비스 이름 `menu`가 `proxy_pass`에 적은 `menu`와 같아야 해요.
- `command`는 `docker run`에서 이미지 뒤에 붙이던 `--name menu` 자리예요.
- `depends_on`은 menu와 order를 먼저 켜고 web을 켜라는 뜻이에요. nginx는 켜질 때 `menu`를 찾는데, 없으면 켜지지 않아요.
- menu와 order에는 `ports`가 없어요. 밖에서는 nginx를 거쳐서만 들어와요.

```bash
docker compose up -d
curl localhost/menu/
```

```
Name: menu
Hostname: 33da5acf1b08
...
GET / HTTP/1.1
Host: menu
...
```

menu와 order가 먼저 켜지고 web이 켜져요. 포트를 안 적어서 80번의 nginx로 갔고, nginx가 menu 앱에 넘겼어요. `GET /`는 nginx가 앞의 `/menu/`를 떼고 넘겼다는 뜻이에요. 브라우저 주소창에 `localhost/menu/`를 쳐도 같은 글자가 나와요.

### 6. 설정을 고치고 다시 읽히기

`conf/default.conf`의 `/menu/` 상자 아래에 `/order/` 상자를 더하고 저장해요.

```nginx
    location /order/ {
        proxy_pass http://order/;
    }
```

저장만 하고 `curl localhost/order/`를 치면 404가 나와요. nginx는 켜질 때 읽은 설정을 계속 써요. 검사하고 다시 읽혀요.

```bash
docker exec cafe-web-1 nginx -t
docker exec cafe-web-1 nginx -s reload
curl localhost/order/
```

```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
...
Name: order
...
```

`cafe-web-1`은 compose가 지은 web 컨테이너 이름이에요. reload는 컨테이너를 끄지 않아서 다른 요청이 끊기지 않아요.

### 7. 열린 포트 확인하기

```bash
docker compose ps
curl localhost:8001
```

```
NAME           IMAGE            COMMAND                  SERVICE   CREATED        STATUS                  PORTS
cafe-menu-1    traefik/whoami   "/whoami --name menu"    menu      1 second ago   Up Less than a second   80/tcp
cafe-order-1   traefik/whoami   "/whoami --name order"   order     1 second ago   Up Less than a second   80/tcp
cafe-web-1     nginx            "/docker-entrypoint.…"   web       1 second ago   Up Less than a second   0.0.0.0:80->80/tcp
```

```
curl: (7) Failed to connect to localhost port 8001 after 0 ms: Couldn't connect to server
```

menu와 order는 `80/tcp`로 컨테이너 안에서만 열려 있어요. 내 컴퓨터와 이어진 문은 web의 80번 하나예요.

### 8. 이벤트 앱 붙이기

`compose.yaml`의 web `depends_on`에 `- event`를 더하고, 맨 아래에 서비스를 하나 더 적어요.

```yaml
  event:
    image: traefik/whoami
    command: --name event
```

`conf/default.conf`에 `/event/` 상자를 더해요.

```nginx
    location /event/ {
        proxy_pass http://event/;
    }
```

```bash
docker compose up -d
docker exec cafe-web-1 nginx -t
docker exec cafe-web-1 nginx -s reload
curl localhost/event/
```

```
Name: event
...
```

compose up은 새 event만 켜고(Started) 나머지는 Running 그대로 둬요. `/menu/`, `/order/`는 끊기지 않았어요.

### 9. 정리하기

```bash
docker compose down
```

컨테이너 넷과 네트워크가 한 번에 지워져요.

## 명령어 요약

| 명령 | 하는 일 |
| --- | --- |
| `curl 주소` | 주소에서 받은 내용을 터미널에 찍어요 |
| `docker logs web` | nginx가 받은 요청 기록을 봐요 |
| `docker exec 이름 명령` | 컨테이너 안에서 명령 하나만 실행하고 돌아와요 |
| `-v ./conf:/etc/nginx/conf.d` | 내 설정 폴더를 nginx 설정 폴더에 연결해요 |
| `location /menu/ { proxy_pass http://menu/; }` | `/menu/`로 오는 요청을 menu 서비스에 넘겨요 |
| `docker exec cafe-web-1 nginx -t` | 설정 파일에 틀린 곳이 없는지 검사해요 |
| `docker exec cafe-web-1 nginx -s reload` | 끄지 않고 설정을 다시 읽혀요 |
| `docker compose logs web` | compose의 web 서비스 기록을 봐요 |
| `docker compose stop menu`, `docker compose start menu` | 서비스 하나만 끄고 켜요 |
| `docker compose ps` | 켜진 서비스와 열린 포트를 봐요 |

## 문제 해결

| 메시지 | 원인 | 해결 |
| --- | --- | --- |
| `404 Not Found` | 그 경로에 파일이나 `location`이 없어요. 설정을 고치고 reload를 안 했을 수도 있어요 | 파일 이름과 `location`을 보고 `nginx -s reload` |
| `502 Bad Gateway`, 기록에 `connect() failed (111: Connection refused)` | `proxy_pass`에 `localhost`를 적었어요. 컨테이너 안의 localhost는 nginx 자신이에요 | `proxy_pass http://menu/;`처럼 서비스 이름으로 적어요 |
| 1분쯤 기다린 뒤 `504 Gateway Time-out`, 기록에 `upstream timed out` | 뒤의 앱이 꺼져 있어요 | `docker compose ps`로 보고 `docker compose start menu` |
| `nginx: [emerg] unexpected "}" in /etc/nginx/conf.d/default.conf:11` | 알려 준 줄의 윗줄 끝에 `;`가 빠졌어요 | 알려 준 줄과 바로 윗줄을 같이 봐요 |
| `nginx: [emerg] host not found in upstream "menuu"` | `proxy_pass`의 서비스 이름이 `compose.yaml`과 달라요 | 이름을 똑같이 고치고 `nginx -t`부터 다시 |
| 오류는 없는데 앱이 `/menu/today`로 받아요 | `proxy_pass http://menu;`처럼 끝의 `/`가 없어요 | `proxy_pass http://menu/;` |
| `Bind for 0.0.0.0:80 failed: port is already allocated` | 다른 컨테이너나 프로그램이 80번을 쓰고 있어요 | `docker ps`로 찾아 끄거나, `ports`를 `"8080:80"`으로 바꾸고 `localhost:8080/menu/`로 열어요 |
| `curl: (7) Failed to connect to localhost port 8001` | 앱 포트는 열지 않았어요. 정상이에요 | `localhost/menu/`로 nginx를 거쳐 들어가요 |
| Git Bash에서 경로 앞에 `C:/Program Files/Git`이 붙어요 | Git Bash가 `/usr/...` 경로를 바꿨어요 | `export MSYS_NO_PATHCONV=1` |

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분 (gen.py가 만들어요)
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  files.py         실습 파일 내용 (site/index.html, event.html, default.conf 네 단계, compose.yaml 두 단계)
  ptyrun.py        화면을 다시 그리는 명령(compose up, down, curl)을 80칸 터미널에서 실행
  demo.py          모든 명령을 실제 Docker와 nginx로 실행해서 tools/out.json에 저장
  out.json         실제 실행 출력
  gen.py           모든 장과 deck.json 생성
nginx-basics-slides.html  배포용 HTML
nginx-basics-slides.pdf   강사용 PDF
```

검사, HTML, PDF를 만드는 공용 도구는 맨 위 [tools/](../tools)에 한 벌만 있어요. 명령은 이 폴더에서 쳐요. `demo.py`는 Docker 데몬이 있어야 하고, cafe 폴더의 컨테이너를 지우고 시작해요.

```bash
uv run -q --with pyte python tools/demo.py
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/build_player.js slides nginx-basics-slides.html
node ../tools/export.js slides nginx-basics-slides.pdf
```

출력은 Docker 29.9.2, Compose v5.6.1, nginx 1.31.8, curl 8.5.0에서 `/home/kim/cafe`를 두고 실행한 결과예요. 504는 nginx가 60초를 기다린 뒤에 나와서 demo.py가 1분쯤 걸려요.

범위: `curl`, `location`과 `root`, `index`, `proxy_pass`와 끝의 `/`, 가장 길게 맞는 `location`, 서비스 여러 개인 `compose.yaml`과 `command`, `depends_on`, `docker exec 이름 명령`, `nginx -t`와 `nginx -s reload`, `docker compose logs`, `stop`, `start`, 포트를 안 적으면 80번을 다뤄요. HTTPS와 인증서, 도메인과 DNS, 로드 밸런싱, 캐시와 gzip, 보안 헤더, `proxy_set_header`, FastAPI 서버 켜기, Kubernetes는 다루지 않아요.

</details>

---

<!-- curriculum:nav -->

[← 이전: 30 · Docker 2 (내 프로그램을 이미지로 만들기)](../30-docker-image) · [커리큘럼](../README.md)

<!-- /curriculum:nav -->
