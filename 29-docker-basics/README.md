# 29 · Docker 1 (컨테이너 실행하기)

> 내 컴퓨터에서는 되는데 친구 컴퓨터에서는 안 되는 문제를 Docker로 풀어요. Windows와 Mac에 Docker Desktop을 설치하고, Docker Hub에서 공식 마크가 붙은 이미지를 받아서 컨테이너를 켜고 끄고 지워요. 명령은 01에서 배운 터미널에서 쳐요.

<!-- curriculum:top -->

| 슬&#8288;라&#8288;이&#8288;드 | 이전 챕터 | 다음 챕터 |
| --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/29-docker-basics/docker-basics-slides.html) | [28 · 미니 프로젝트: 장바구니 (들여쓰기, items, 모듈)](../28-python-modules) | [30 · Docker 2 (내 프로그램을 이미지로 만들기)](../30-docker-image) |

<!-- /curriculum:top -->

## 학습 목표

이 챕터를 마치면 다음을 할 수 있어요.

- 이미지(붕어빵 틀)와 컨테이너(붕어빵)의 차이를 말해요.
- 가상 머신과 컨테이너가 무엇을 담는지 비교해요.
- Windows에서 가상화와 WSL 2를 확인하고 Docker Desktop을 설치해요.
- Mac에서 칩 종류(Apple Silicon, Intel)를 보고 맞는 설치 파일을 골라요.
- Docker Hub에서 Docker Official Image 마크를 보고 이미지를 골라 `docker pull`로 받아요.
- `docker run`, `ps`, `stop`, `start`, `restart`, `rm`, `rmi`로 컨테이너와 이미지를 다뤄요.
- `-p 8080:80`으로 내 컴퓨터 문을 컨테이너 문에 이어서 브라우저로 열어요.
- `-it`로 우분투 컨테이너 안에 들어가 리눅스 명령을 치고 `exit`로 나와요.
- 자주 나는 오류 다섯 가지를 메시지로 알아보고 고쳐요.

## 시작하기 전에

| 할 일 | 챕터 |
| --- | :---: |
| 터미널 열기, 명령 치기 | 01 |
| Windows Git Bash 쓰기 | 02 |
| f-string (6파트 실습 코드) | 13 |
| 딕셔너리 `menu["latte"]` (6파트 실습 코드) | 15 |

- 설치에 관리자 권한이 필요해요. 회사 노트북이면 먼저 확인해요.
- Windows는 Windows 10 22H2 또는 Windows 11 23H2 이상, 메모리 8GB 이상이 필요해요.
- Mac은 최신 macOS와 그 앞 두 버전까지 설치돼요.
- 처음 받는 이미지는 수백 MB에서 1GB가 넘어요. 와이파이가 빠른 곳에서 따라 해요.

## 구성

| 파트 | 쪽 | 내용 |
| --- | --- | --- |
| 1 · Docker가 뭔가요 | 3~7 | 내 컴퓨터에서만 되는 문제, 컨테이너 상자, 이미지와 컨테이너, 큰 그림, 가상 머신과 비교 |
| 2 · 설치하기 | 8~14 | Windows 가상화 확인, WSL 2와 Hyper-V, Windows 설치, Mac 칩 고르기, Mac 설치, 처음 켜기, hello-world |
| 3 · Docker Desktop과 Docker Hub | 15~20 | Desktop 화면 둘러보기, Containers 목록, Hub 검색, 공식 마크, 태그, `docker pull` |
| 4 · 컨테이너 켜고 끄기 | 21~32 | `run`, `ps -a`, `-d --name`, `stop`과 `start`, `restart`, 상태 그림, localhost와 포트 번호, 포트가 필요한 이유, `-p 8080:80`, 두 개 켜기, `logs`, `-it`로 우분투 안에 들어가기 |
| 5 · 자주 나는 오류 | 33~37 | 엔진 꺼짐, 켜진 채 `rm`, 이름 겹침, 포트 겹침, 남은 컨테이너 때문에 `rmi` 안 됨 |
| 6 · 실습 | 38~39 | 파이썬 3.11과 3.12 비교, 컨테이너를 지우면 사라지는 기록 |
| 정리 | 40 | 한 장 요약 |

## 핵심 개념

| 말 | 뜻 | 비유 |
| --- | --- | --- |
| 이미지 | 프로그램과 필요한 것을 묶어 둔 틀. 바뀌지 않아요 | 붕어빵 틀 |
| 컨테이너 | 이미지로 켠 실행 중인 상자. 여러 개 찍을 수 있어요 | 붕어빵 |
| Docker Hub | 이미지를 받는 인터넷 저장소(hub.docker.com) | 틀 가게 |
| Docker Desktop | 내 컴퓨터에서 엔진을 켜고 컨테이너를 화면으로 보여 주는 앱 | 붕어빵 기계 |
| localhost | 지금 쓰는 내 컴퓨터를 부르는 이름. 숫자로는 127.0.0.1 | 우리 집 |
| 포트 | 프로그램이 요청을 받는 문 번호. `localhost:8080`의 8080 | 가게 문 |

```
Docker Hub (nginx, python …)
   │  docker pull
   ▼
내 컴퓨터의 이미지 nginx
   │  docker run
   ▼
컨테이너 web, web2 …
```

컨테이너는 상태가 세 가지예요.

| 상태 | 들어가는 명령 | `docker ps`에 보이나요 |
| --- | --- | :---: |
| 켜짐 `Up` | `docker run`, `docker start`, `docker restart` | 예 |
| 꺼짐 `Exited` | `docker stop`, `Ctrl+C` | `-a`를 붙여야 보여요 |
| 없어짐 | `docker rm` (꺼진 뒤에) | 아니요 |

공식 마크는 이 순서로 믿고 골라요.

| 마크 | 누가 올렸나요 |
| --- | --- |
| Docker Official Image | Docker가 직접 관리 (nginx, python, ubuntu) |
| Verified Publisher | 회사가 직접 올림 |
| Sponsored OSS | Docker가 후원하는 오픈소스 프로젝트 |
| Docker Hardened Image | 보안을 더 다듬은 이미지 |
| 마크 없음 | 누구나 올린 이미지, 안에 무엇이 있는지 몰라요 |

## 실습

Windows는 Git Bash, Mac은 터미널에서 쳐요. 아래 출력은 실제로 실행한 결과예요. ID, 시간, 버전 숫자는 여러분 화면과 달라요.

### 1. 설치 확인

Windows는 관리자 PowerShell에서 WSL을 먼저 켜고 컴퓨터를 다시 시작해요.

```powershell
wsl --install
```

Docker Desktop을 설치해요.

```bash
# Windows (Git Bash 또는 PowerShell)
winget install -e --id Docker.DockerDesktop
# Mac
brew install --cask docker-desktop
```

Docker Desktop을 열고 약관에 Accept를 누른 뒤, 왼쪽 아래 Engine running이 보이면 확인해요.

```bash
docker --version
docker run hello-world
```

```
Docker version 29.9.2, build a82e528
Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
…
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

### 2. 이미지 받기

```bash
docker pull nginx
docker images
```

```
IMAGE                ID             DISK USAGE   CONTENT SIZE   EXTRA
hello-world:latest   c567b231f656       25.9kB         9.49kB   U
nginx:latest         165ddde8751e        243MB         66.8MB
```

### 3. 켜고 끄기

```bash
docker run -d --name web nginx
docker ps
docker stop web
docker ps -a
docker start web
docker restart web
```

`docker restart`는 stop과 start를 한 번에 해요. `docker ps -a`에는 꺼진 컨테이너가 `Exited`로 남아요.

```
CONTAINER ID   IMAGE         COMMAND                  CREATED         STATUS                              PORTS     NAMES
b4a5370848e4   nginx         "/docker-entrypoint.…"   1 second ago    Exited (0) Less than a second ago             web
```

### 4. 브라우저로 열기

포트를 이으려면 컨테이너를 새로 만들어야 해요. 먼저 끄고 지워요.

```bash
docker stop web
docker rm web
docker run -d --name web -p 8080:80 nginx
docker ps
```

```
CONTAINER ID   IMAGE     COMMAND                  CREATED                  STATUS                  PORTS                  NAMES
ba5cd077165e   nginx     "/docker-entrypoint.…"   Less than a second ago   Up Less than a second   0.0.0.0:8080->80/tcp   web
```

브라우저에서 `http://localhost:8080`을 열면 Welcome to nginx! 화면이 나와요. 몇 번 새로 고친 뒤 기록을 봐요.

```bash
docker logs web
```

### 5. 우분투 컨테이너 안에 들어가기

`-it`는 내 키보드 입력을 컨테이너에 보내고(`-i`) 터미널 화면을 붙여 줘요(`-t`). 이미지 뒤의 `bash`는 컨테이너 안에서 켤 프로그램이에요.

```bash
docker run -it --name my-server ubuntu:24.04 bash
```

프롬프트가 `root@…:/#`로 바뀌면 컨테이너 안이에요. 01에서 배운 리눅스 명령을 쳐 보고 `exit`로 나와요.

```
root@ab7c906af182:/# cat /etc/os-release | head -2
PRETTY_NAME="Ubuntu 24.04.5 LTS"
NAME="Ubuntu"
root@ab7c906af182:/# whoami
root
root@ab7c906af182:/# exit
exit
```

`exit`로 나오면 bash가 끝나서 컨테이너도 꺼져요. 켜 둔 컨테이너에 다시 들어가는 `docker exec`는 30에서 배워요.

### 6. 파이썬 두 버전 비교

파이썬을 설치하지 않고 3.11과 3.12를 바로 돌려 봐요. 이미지가 1GB가 넘어서 받는 데 시간이 걸려요.

```bash
docker run python:3.11 python -c 'menu = {"latte": 4500}; print(f"라떼: {menu["latte"]}원")'
docker run python:3.12 python -c 'menu = {"latte": 4500}; print(f"라떼: {menu["latte"]}원")'
```

```
SyntaxError: f-string: unmatched '['
…
라떼: 4500원
```

3.11은 f-string 안에 같은 따옴표를 다시 쓰는 문법을 몰라서 오류가 나고, 3.12는 돼요.

### 7. 치우기

```bash
docker ps -a
docker stop web
docker rm web my-server
docker rmi nginx ubuntu:24.04
```

`docker ps -a`에 nginx로 만든 컨테이너가 더 남아 있으면 그 이름으로 `docker rm`을 먼저 해요.

## 명령어 요약

| 명령 | 하는 일 |
| --- | --- |
| `docker --version` | 설치된 버전 보기 |
| `docker run hello-world` | 설치 확인 |
| `docker pull 이름:태그` | Hub에서 이미지 받기 (태그를 안 쓰면 `latest`) |
| `docker images` | 받은 이미지 목록 |
| `docker run 이미지` | 새 컨테이너를 만들어 켜기 (터미널을 붙잡아요) |
| `docker run -d --name 이름 -p 8080:80 이미지` | 뒤에서 켜기, 이름 붙이기, 내 컴퓨터 8080을 컨테이너 80에 잇기 |
| `docker ps` | 켜진 컨테이너 목록 |
| `docker ps -a` | 꺼진 것까지 전부 |
| `docker stop 이름` | 끄기 |
| `docker start 이름` | 꺼 둔 컨테이너 다시 켜기 |
| `docker restart 이름` | 켜진 컨테이너를 껐다가 다시 켜기 (stop + start) |
| `docker rm 이름` | 꺼진 컨테이너 지우기 |
| `docker rmi 이미지` | 이미지 지우기 (쓰는 컨테이너가 없어야 해요) |
| `docker logs 이름` | 컨테이너가 남긴 기록 보기 |
| `docker run -it --name 이름 이미지 bash` | 컨테이너 안에 들어가서 명령 치기 (`exit`로 나오면 꺼져요) |
| `Ctrl+C` | 앞에서 켠 컨테이너 멈추기 |

## 문제 해결

| 메시지 | 원인 | 해결 |
| --- | --- | --- |
| `failed to connect to the docker API` | Docker Desktop(엔진)이 꺼져 있어요 | Docker Desktop을 열고 Engine running을 기다린 뒤 다시 쳐요 |
| `container is running: stop the container before removing` | 켜진 컨테이너를 `rm`했어요 | `docker stop 이름` 뒤 `docker rm 이름` |
| `Conflict. The container name "/web" is already in use` | 같은 이름의 컨테이너가 이미 있어요(꺼져 있어도) | `docker ps -a`로 보고 지우거나, 다른 이름으로 켜요 |
| `port is already allocated` | 내 컴퓨터의 그 문을 다른 컨테이너가 쓰고 있어요 | 실패한 컨테이너를 `docker rm` 하고 `-p 8081:80`처럼 다른 문으로 켜요 |
| `conflict: unable to delete … container … is using its referenced image` | 그 이미지로 만든 컨테이너가 남아 있어요 | `docker ps -a`로 찾아 `docker rm` 한 뒤 `docker rmi` |
| 작업 관리자에 가상화: 사용 안 함 | BIOS(UEFI)에서 가상화가 꺼져 있어요 | 컴퓨터를 켤 때 BIOS 설정에서 가상화를 켜요. 메뉴가 회사마다 달라서 강사와 같이 해요 |
| 브라우저에서 localhost:8080이 안 열려요 | `-p` 없이 켰어요 | 컨테이너를 지우고 `-p 8080:80`을 붙여 새로 켜요 |

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py           이 챕터의 장 생성 (demo-output.txt를 읽어서 터미널 출력을 넣어요)
  demo.sh          슬라이드에 넣은 docker 명령을 덱 순서대로 실제로 실행
  demo-output.txt  demo.sh 출력
  hubshots.js      Docker Hub 화면 캡처 (검색, nginx, python 태그)
  nginxshot.js     localhost:8080 Welcome to nginx! 화면 캡처
  src/             캡처한 그림
docker-basics-slides.html   배포용 HTML
docker-basics-slides.pdf    강사용 PDF
```

- 터미널 출력은 리눅스 컨테이너의 Docker 29.9.2로 실제로 실행한 결과예요. 엔진 꺼짐 오류(33쪽)는 Mac 소켓 경로를 `DOCKER_HOST`로 넣어서 실제로 냈어요.
- `winget`, `brew`, `wsl --install`은 이 환경에서 실행할 수 없어서 명령만 보여 줘요.
- Docker Desktop 창, 작업 관리자, 이 Mac에 관하여, 약관 창은 캡처할 수 없어서 간단한 그림으로 그렸어요. 발표자 노트에 적어 두었어요.
- `-it` 장(32쪽)은 터미널이 있어야 해서 `script`로 감싸 실행했어요. `restart` 장(25쪽)과 함께 그 부분만 다시 돌릴 때는 `bash tools/demo.sh extra`예요. `demo.sh`는 시작할 때 그 컴퓨터의 컨테이너와 이미지를 모두 지워요. 연습용 컴퓨터에서만 돌려요.

검사, HTML, PDF를 만드는 공용 도구(`check.js`, `build_player.js`, `export.js`)는 맨 위 [tools/](../tools)에 한 벌만 있어요. 명령은 이 폴더에서 쳐요.

```bash
bash tools/demo.sh > tools/demo-output.txt 2>&1
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/boxcheck.js slides
node ../tools/build_player.js slides docker-basics-slides.html
node ../tools/export.js slides docker-basics-slides.pdf
```

</details>

---

<!-- curriculum:nav -->

[← 이전: 28 · 미니 프로젝트: 장바구니 (들여쓰기, items, 모듈)](../28-python-modules) · [커리큘럼](../README.md) · [다음: 30 · Docker 2 (내 프로그램을 이미지로 만들기) →](../30-docker-image)

<!-- /curriculum:nav -->
