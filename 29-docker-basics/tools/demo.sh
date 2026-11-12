#!/usr/bin/env bash
# Runs every docker command the deck shows, in the deck's order, so the slides carry real output.
# Needs a running Docker engine. It removes every container and image on this machine first,
# so run it only on a practice machine (the deck was made in a throwaway Linux container).
# Usage (in 29-docker-basics): bash tools/demo.sh > tools/demo-output.txt 2>&1
set -u
run() { echo "\$ $*"; "$@" 2>&1; echo "[exit $?]"; echo; }
step() { echo "### $1"; }

docker rm -f $(docker ps -aq) >/dev/null 2>&1
docker rmi -f $(docker images -q) >/dev/null 2>&1

step daemon-off   # what the client prints when Docker Desktop is not running (Mac socket path)
DOCKER_HOST=unix:///Users/kim/.docker/run/docker.sock run docker ps

step check
run docker --version
run docker run hello-world

step pull
run docker pull nginx
run docker images

step foreground
echo '$ docker run nginx   (3초 뒤 Ctrl+C)'
timeout -s INT 3 docker run nginx 2>&1; echo "[exit $?]"; echo
run docker ps -a

step run-d
run docker run -d --name web nginx
run docker ps
run docker logs web

step stop
run docker stop web
run docker ps
run docker ps -a
run docker start web
run docker ps

step port-why
run curl -sS --max-time 3 http://localhost:8080

step error-rm-running
run docker rm web
run docker stop web
run docker rm web

step port
run docker run -d --name web -p 8080:80 nginx
run docker ps
sleep 1
run curl -sS http://localhost:8080

step error-name
run docker run -d --name web -p 8080:80 nginx

step error-port
run docker run -d --name web2 -p 8080:80 nginx
run docker ps -a
run docker rm web2

step two
run docker run -d --name web2 -p 8081:80 nginx
run docker ps

step logs
for i in 1 2 3; do curl -s -o /dev/null http://localhost:8080; done
run docker logs web

step lost
run docker stop web
run docker rm web
run docker run -d --name web -p 8080:80 nginx
sleep 1
run docker logs web

step error-rmi
run docker stop web web2
run docker rm web web2
run docker rmi nginx
run docker ps -a
docker ps -aq --filter ancestor=nginx --filter ancestor=hello-world | while read -r id; do
  name=$(docker inspect -f '{{.Name}}' "$id" | tr -d /); run docker rm "$name"; done
run docker rmi nginx hello-world
run docker images

step python
run docker run python:3.11 python -c 'menu = {"latte": 4500}; print(f"라떼: {menu["latte"]}원")'
run docker run python:3.12 python -c 'menu = {"latte": 4500}; print(f"라떼: {menu["latte"]}원")'
run docker images
