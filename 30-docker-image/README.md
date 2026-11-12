# 30 · Docker 2 (내 프로그램을 이미지로 만들기)

> 29에서는 남이 만든 이미지(nginx)를 받아서 컨테이너로 띄웠어요. 이번에는 컨테이너 안에 들어가 보고, 지워도 남는 볼륨을 붙이고, 28의 장바구니 프로젝트를 Dockerfile로 내 이미지로 만들어요. 마지막에는 긴 `docker run` 명령을 `compose.yaml`에 적어 두고 짧게 켜고 꺼요. 이미지는 붕어빵 틀, 컨테이너는 붕어빵이라는 29의 비유를 그대로 써요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/30-docker-image/docker-image-slides.html) | [29 · Docker 1 (컨테이너 실행하기)](../29-docker-basics) | 준비 중 |

<!-- /curriculum:top -->

## 학습 목표

이 챕터를 마치면 다음을 할 수 있어요.

- `docker exec -it 이름 bash`로 켜 둔 컨테이너 안에 들어가고 `exit`로 나와요. 29의 `docker run -it`과 달리 나와도 컨테이너가 계속 돌아요.
- 컨테이너를 지우면 안에서 고친 파일도 같이 사라지는 이유를 말해요.
- `-v 볼륨이름:경로`로 지워도 남는 보관함을 붙이고, `-v ./폴더:경로`로 내 폴더를 연결해요.
- Dockerfile 다섯 줄(`FROM`, `WORKDIR`, `COPY`, `RUN`, `CMD`)이 각각 무엇을 하는지 말해요.
- `docker build -t cart .`로 이미지를 만들고 `docker run cart`로 실행해요.
- 코드를 고치면 build부터 다시 해야 하는 이유를 말해요.
- `.dockerignore`로 이미지에 넣지 않을 파일을 정해요.
- `compose.yaml`을 적고 `docker compose up -d`, `docker compose down`으로 켜고 꺼요.

## 시작하기 전에

| 할 일 | 챕터 |
| --- | :---: |
| Docker Desktop 설치, `docker run`, `ps`, `stop`, `rm`, `-d`, `--name`, `-p`, `docker run -it ... bash`와 `exit` | 29 |
| uv 프로젝트, `uv sync`, `uv run main.py` | 09 |
| 장바구니 프로젝트(`product.py`, `cart.py`, `main.py`) | 28 |
| `git add`, `git commit -m`, `git push origin main` | 02 |

Docker Desktop을 켜 두고 따라 쳐요. 터미널은 macOS 터미널이나 Windows Git Bash를 써요.

Windows Git Bash에서는 `/usr/share/...` 같은 경로를 Git Bash가 `C:/Program Files/Git/usr/share/...`로 바꿔 버려요. 실습 전에 한 번 쳐 두세요. 터미널을 새로 열면 다시 쳐요.

```bash
export MSYS_NO_PATHCONV=1
```

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1–5 | 표지, 오늘의 순서, 지운 컨테이너와 함께 사라진 메뉴판, 큰 그림, 실습 폴더 준비 |
| 1. 컨테이너 안에 들어가기 | 6–9 | nginx 다시 띄우기, `docker exec -it`, 안에서 `index.html` 고치기, 지우면 사라지는 변경 |
| 2. 볼륨으로 남기기 | 10–14 | 볼륨이란, `-v cafe-html:경로`, `docker volume ls`, `-v ./site:경로`, 둘 비교 |
| 3. Dockerfile로 이미지 만들기 | 15–24 | 왜 이미지로 만드나, 다섯 줄, `FROM astral/uv`, `WORKDIR`과 `COPY`, `RUN`과 `CMD`, `docker build`, `docker run cart`, 고친 뒤 다시 build, `--rm`, `.dockerignore` |
| 4. docker compose 맛보기 | 25–26 | 긴 `docker run`을 `compose.yaml`로, `up -d`, `ps`, `down` |
| 5. 자주 나는 오류 | 27–29 | build 오류 세 가지, run과 exec 오류, `./`를 빼먹은 `-v` |
| 6. 실제 상황 예제 | 30–32 | 카페 메뉴판 compose로 고치기, 친구 컴퓨터에서 build와 run, 다 쓴 것 정리 |
| 정리 | 33–34 | 막힐 때, 한 장 요약 |

## 핵심 개념

### 틀, 붕어빵, 보관함

| 이름 | 비유 | 만드는 명령 | 지우는 명령 |
| --- | --- | --- | --- |
| 이미지 | 붕어빵 틀 | `docker build -t 이름 .` | `docker rmi 이름` |
| 컨테이너 | 붕어빵 | `docker run 이름` | `docker rm 이름` |
| 볼륨 | 붕어빵 밖 보관함 | `docker run -v 볼륨이름:경로 ...` | `docker volume rm 이름` |

컨테이너 안에서 고친 파일은 그 붕어빵에만 있어서, 붕어빵을 지우면 같이 사라져요. 남겨야 하는 파일은 보관함(볼륨)이나 내 폴더에 둬요.

### 볼륨과 폴더 연결

| | 볼륨 이름 | 내 폴더 연결 |
| --- | --- | --- |
| 쓰는 모양 | `-v cafe-html:/usr/share/nginx/html` | `-v ./site:/usr/share/nginx/html` |
| 파일이 있는 곳 | Docker가 관리하는 곳 | 내 폴더 (VS Code로 열려요) |
| 목록 보기 | `docker volume ls` | `ls site` |
| 고르는 때 | 컨테이너가 만든 데이터를 남길 때 | 내가 고친 파일을 바로 보고 싶을 때 |

`./`로 시작하면 내 폴더, 아니면 볼륨 이름이에요. `./`를 빼먹으면 오류 없이 새 볼륨이 생겨요.

### Dockerfile 다섯 줄

`shopping-cart` 폴더 맨 위, `main.py` 옆에 확장자 없이 `Dockerfile`이라는 파일을 만들어요. D는 대문자예요.

```dockerfile
FROM astral/uv:python3.14-bookworm-slim
WORKDIR /app
COPY . .
RUN uv sync
CMD ["uv", "run", "main.py"]
```

| 줄 | 하는 일 | 언제 실행돼요 |
| --- | --- | --- |
| `FROM` | 파이썬과 uv가 든 이미지 위에서 시작해요 | build |
| `WORKDIR /app` | 이미지 안에서 일할 폴더를 정해요. 없으면 만들고 들어가요 | build |
| `COPY . .` | 지금 폴더의 파일을 `/app`에 넣어요 | build |
| `RUN uv sync` | 패키지를 맞춰서 결과를 틀 안에 구워요 | build할 때 한 번 |
| `CMD [...]` | 컨테이너를 켜면 칠 명령을 적어 둬요 | run할 때마다 |

`astral/uv`는 uv를 만든 회사 Astral이 올린 이미지예요. Docker Hub의 공식 인증 마크는 없지만 uv 공식 문서가 이 이미지를 안내해요. `python3.14`는 프로젝트의 `.python-version`과 맞춰요.

### .dockerignore

```
.venv
__pycache__
.git
```

`.venv`는 내 컴퓨터용 가상환경이라 이미지에 넣지 않아요. 이미지 안의 `.venv`는 `RUN uv sync`가 리눅스용으로 새로 만들어요. 실습에서는 build할 때 보내는 재료가 83.15kB에서 300B로 줄었어요.

### compose.yaml

```yaml
services:
  web:
    image: nginx
    ports:
      - "8080:80"
    volumes:
      - ./site:/usr/share/nginx/html
```

`ports`는 `-p`, `volumes`는 `-v` 자리예요. 들여쓰기는 2칸씩이고, 목록은 `-`로 시작해요. 이 챕터에서는 컨테이너 하나만 적어요.

## 실습

출력은 실제로 실행한 결과예요. 컨테이너 ID, 시간, 크기는 내 화면과 달라요.

### 1. 컨테이너 안에 들어가기

```bash
cd cafe
docker run -d --name web -p 8080:80 nginx
docker exec -it web bash
```

프롬프트가 `root@b0ed4b95660e:/#`처럼 바뀌면 컨테이너 안이에요. 안에서 이렇게 쳐요.

```bash
cd /usr/share/nginx/html
ls
echo "<h1>KANT Cafe</h1>" > index.html
exit
```

```
root@b0ed4b95660e:/usr/share/nginx/html# ls
50x.html  index.html
```

브라우저에서 `localhost:8080`을 새로 고치면 KANT Cafe가 보여요. 이제 지우고 다시 띄워 봐요.

```bash
docker stop web
docker rm web
docker run -d --name web -p 8080:80 nginx
```

새로 고치면 다시 nginx 환영 페이지예요. 지운 붕어빵과 함께 고친 파일도 사라졌어요.

```bash
docker stop web
docker rm web
```

### 2. 볼륨 붙이기

```bash
docker run -d --name web -p 8080:80 -v cafe-html:/usr/share/nginx/html nginx
docker exec -it web bash
```

안에서 1번처럼 `index.html`을 고치고 `exit`로 나와요. 그다음 지우고 같은 볼륨을 붙여 다시 띄워요.

```bash
docker stop web
docker rm web
docker run -d --name web -p 8080:80 -v cafe-html:/usr/share/nginx/html nginx
docker volume ls
```

```
DRIVER    VOLUME NAME
local     cafe-html
```

새로 고치면 KANT Cafe가 그대로 있어요.

### 3. 내 폴더 연결하기

`cafe` 폴더 안에 `site` 폴더를 만들고, VS Code로 `site/index.html`을 만들어요.

```html
<meta charset="utf-8">
<h1>KANT 카페 메뉴</h1>
<p>아메리카노 4,500원</p>
```

```bash
docker stop web
docker rm web
docker run -d --name web -p 8080:80 -v ./site:/usr/share/nginx/html nginx
```

`index.html`에 `<p>카페라테 5,000원</p>`을 더하고 저장한 뒤 브라우저를 새로 고치면 바로 보여요. 다 봤으면 지워요.

```bash
docker stop web
docker rm web
```

### 4. 장바구니를 이미지로 만들기

28의 `shopping-cart` 폴더로 가서, 위 "Dockerfile 다섯 줄"을 `Dockerfile`로, "`.dockerignore`" 세 줄을 `.dockerignore`로 저장해요.

```bash
cd ~/shopping-cart
docker build -t cart .
docker images
docker run cart
```

```
텀블러 2개를 담았습니다.
무선 이어폰 1개를 담았습니다.
품절된 상품입니다.
----------------------------------------
텀블러        x 2   =       30,000원
무선 이어폰     x 1   =       89,000원
...
```

`main.py`에서 텀블러를 3개로 고친 뒤 `docker run cart`를 치면 그대로 2개예요. build부터 다시 해요.

```bash
docker build -t cart .
docker run --rm cart
```

`--rm`을 붙이면 프로그램이 끝날 때 컨테이너도 지워져서 `docker ps -a` 목록에 쌓이지 않아요.

### 5. compose로 켜고 끄기

`cafe` 폴더 맨 위(`site` 옆)에 위 `compose.yaml`을 저장해요.

```bash
cd ~/cafe
docker compose up -d
docker compose ps
docker compose down
```

```
[+] up 2/2
 ✔ Network cafe_default Created                                             0.0s
 ✔ Container cafe-web-1 Started                                             0.2s
```

`down`은 stop과 rm을 한 번에 해요. 컨테이너 이름은 `폴더 이름-서비스 이름-번호`로 compose가 붙여요.

### 6. 정리하기

```bash
docker ps -a
docker rm 이름1 이름2 이름3
docker rmi cart
docker volume ls
docker volume rm cafe-html
```

컨테이너부터 지우고 이미지와 볼륨을 지워요. 지운 볼륨의 파일은 되돌릴 수 없어요.

## 명령어 요약

| 명령 | 하는 일 |
| --- | --- |
| `docker exec -it 이름 bash` | 실행 중인 컨테이너 안에 들어가요 (`exit`로 나와요) |
| `docker run -v 볼륨이름:경로 ...` | 볼륨(지워도 남는 보관함)을 붙여요 |
| `docker run -v ./폴더:경로 ...` | 내 폴더를 컨테이너에 연결해요 |
| `docker volume ls` | 볼륨 목록을 봐요 |
| `docker volume rm 이름` | 볼륨을 지워요 |
| `docker build -t 이름 .` | 지금 폴더의 Dockerfile로 이미지를 만들어요 |
| `docker run 이름` | 내가 만든 이미지로 컨테이너를 실행해요 |
| `docker run --rm 이름` | 끝나면 컨테이너를 바로 지워요 |
| `docker compose up -d` | `compose.yaml`대로 켜요 |
| `docker compose ps` | 이 폴더의 compose 컨테이너만 봐요 |
| `docker compose down` | 끄고 지워요 |

## 문제 해결

| 메시지 | 원인 | 해결 |
| --- | --- | --- |
| `Error response from daemon: container ... is not running` | 멈춘 컨테이너에 exec 했어요 | `docker start 이름` 뒤 다시 exec |
| `ERROR: docker: 'docker buildx build' requires 1 argument` | `docker build` 끝의 점(`.`)을 빼먹었어요 | `docker build -t cart .` |
| `ERROR: failed to build: failed to solve: failed to read dockerfile: open Dockerfile: no such file or directory` | Dockerfile이 없는 폴더에서 쳤어요 | `pwd`로 확인하고 `cd shopping-cart` |
| `... failed to resolve source metadata for docker.io/astral/uv:python3.14-bookwrom-slim ... not found` | `FROM`의 이미지 이름이나 태그에 오타가 있어요 | `bookwrom`을 `bookworm`으로 고쳐요 |
| `error: Failed to spawn: mian.py` | `CMD`의 파일 이름 오타예요 | Dockerfile을 고치고 다시 build |
| `Bind for 0.0.0.0:8080 failed: port is already allocated` | 다른 컨테이너가 8080을 쓰고 있어요 | `docker ps`로 찾아 stop, 또는 `docker compose down`, 또는 `-p 8081:80` |
| `no configuration file provided: not found` | `compose.yaml`이 없는 폴더에서 compose를 쳤어요 | `cd cafe` |
| 오류는 없는데 메뉴 대신 nginx 환영 페이지가 나와요 | `-v site:`처럼 `./`를 빼서 새 볼륨이 생겼어요 | `-v ./site:`로 다시 만들고 `docker volume rm site` |
| 코드를 고쳤는데 결과가 그대로예요 | 이미지에는 build할 때의 코드가 들어 있어요 | `docker build -t cart .` 다시 |
| Git Bash에서 경로 앞에 `C:/Program Files/Git`이 붙어요 | Git Bash가 `/usr/...` 경로를 바꿨어요 | `export MSYS_NO_PATHCONV=1` |

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분 (gen.py가 만들어요)
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  files.py         실습 파일 내용 (site/index.html, compose.yaml, Dockerfile, .dockerignore)
  ptyrun.py        화면을 다시 그리는 명령(pull, build, compose, exec -it)을 80칸 터미널에서 실행
  demo.py          모든 명령을 실제 Docker로 실행해서 tools/out.json에 저장
  out.json         실제 실행 출력
  gen.py           모든 장과 deck.json 생성
docker-image-slides.html  배포용 HTML
docker-image-slides.pdf   강사용 PDF
```

검사, HTML, PDF를 만드는 공용 도구는 맨 위 [tools/](../tools)에 한 벌만 있어요. 명령은 이 폴더에서 쳐요. `demo.py`는 Docker 데몬과 uv가 있어야 하고, 이미지와 볼륨을 지우고 시작해요.

```bash
uv run --with pyte python tools/demo.py
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/build_player.js slides docker-image-slides.html
node ../tools/export.js slides docker-image-slides.pdf
```

출력은 Docker 29.9.2, Compose v5.6.1에서 `/home/kim/cafe`와 `/home/kim/shopping-cart`(28의 `product.py`, `cart.py`, `main.py`를 `uv init --python 3.14`로 만든 프로젝트)를 두고 실행한 결과예요. 장바구니 코드는 28의 `tools/scenes.py`에서 그대로 가져와요.

범위: `docker exec -it`, 볼륨 `-v 이름:경로`와 `-v ./폴더:경로`, `docker volume ls`와 `rm`, Dockerfile 다섯 줄(`astral/uv` 이미지), `docker build -t`, `--rm`, `.dockerignore`, `compose.yaml` 하나짜리 서비스와 `up -d`, `ps`, `down`을 다뤄요. Docker Hub에 push, 네트워크, 멀티 스테이지 빌드, 서비스 여러 개인 compose, Kubernetes는 다루지 않아요.

</details>

---

<!-- curriculum:nav -->

[← 이전: 29 · Docker 1 (컨테이너 실행하기)](../29-docker-basics) · [커리큘럼](../README.md)

<!-- /curriculum:nav -->
