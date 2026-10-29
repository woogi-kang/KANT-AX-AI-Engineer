#!/usr/bin/env bash
# Replays the team practice (kim, lee, park) in throwaway repos and prints every command with its real output.
# GitHub is a local bare repo reached through the https://github.com/kim/team-intro.git address.
# Usage: bash tools/demo.sh /tmp/team-demo
set -e
D=${1:?폴더 경로를 넣어 주세요}
rm -rf "$D"; mkdir -p "$D"
export LANG=C.UTF-8 GIT_EDITOR=true
URL=https://github.com/kim/team-intro.git
git init -q --bare -b main "$D/github.git"
n=0
t() { n=$((n+1)); local d="2026-10-29T14:$(printf %02d $n):00+09:00"; export GIT_AUTHOR_DATE=$d GIT_COMMITTER_DATE=$d; }
# Each person gets their own HOME so their global config stays separate.
who() {
  export HOME="$D/home-$1"; mkdir -p "$HOME"
  if [ ! -f "$HOME/.gitconfig" ]; then
    git config --global user.name "$1"; git config --global user.email "$1@example.com"
    git config --global init.defaultBranch main; git config --global core.pager cat; git config --global log.decorate short
    git config --global url."$D/github.git".insteadOf "$URL"
  fi
  mkdir -p "$D/$1"; cd "$D/$1"; [ -d team-intro ] && cd team-intro
  echo; echo "##### $1"
}
r() { echo "\$ $*"; eval "$@" 2>&1 | sed "s#$D/github.git#$URL#g; s#$D/github#https://github.com/kim/team-intro#g" || true; }
step() { echo; echo "=== $*"; }

step "0 GitHub에서 README를 체크해 저장소 만들기"
who kim; t
git init -q -b main "$D/seed"; cd "$D/seed"; echo "# team-intro" > README.md; git add README.md; git commit -q -m "Initial commit"
git push -q "$D/github.git" main 2>/dev/null; cd "$D/kim"

step "1 셋이 clone"
for p in kim lee park; do who $p; r git clone $URL; cd team-intro; r git log --oneline; done
step "1b pull 설정 (lee, kim, park 모두)"
for p in kim park; do who $p; r git config --global pull.rebase false; done

step "2 kim: 다른 파일 커밋, push"
who kim
r 'echo "안녕하세요, kim이에요" > kim.md'
t; r git add kim.md; r git commit -m '"docs: kim 자기소개 추가"'
r git push origin main

step "3 lee: 다른 파일 커밋, push 거절"
who lee
r 'echo "안녕하세요, lee예요" > lee.md'
t; r git add lee.md; r git commit -m '"docs: lee 자기소개 추가"'
r git push origin main
step "3b lee: 설정 없이 pull"
r git pull origin main
r git log --oneline
step "3c lee: 설정하고 다시 pull"
r git config --global pull.rebase false
t; r git pull origin main
r git log --oneline
r ls
step "4 lee: push"
r git push origin main

step "5 kim: pull (fast-forward)"
who kim
r git pull origin main
r git log --oneline
step "6 park: fetch 하고 pull"
who park
r git fetch origin
r git log --oneline
r git log --oneline origin/main
r git pull origin main
r ls

step "7 kim: README 첫 줄 고치고 push"
who kim
r "printf '# 깃벗 팀\n' > README.md"
r git diff
t; r git add README.md; r git commit -m '"docs: 팀 이름을 깃벗으로 정하기"'
r git push origin main

step "8 lee: 같은 줄 고치고 push 거절, pull 충돌"
who lee
r "printf '# 커밋조 팀\n' > README.md"
t; r git add README.md; r git commit -m '"docs: 팀 이름을 커밋조로 정하기"'
r git push origin main
t; r git pull origin main
r git status
r cat README.md
step "8b 충돌 중에 또 pull"
r git pull origin main
step "9 lee: 고치고 add, commit, push"
r "printf '# 깃벗 팀\n' > README.md"
t; r git add README.md; r git commit -m '"fix: 팀 이름 충돌 해결"'
r git push origin main
r git log --oneline

step "10 kim, park: pull"
who kim
r git pull origin main
r git log --oneline
who park
r git pull origin main
r cat README.md

step "11 커밋 안 한 채 pull (park 고침, kim이 같은 파일 push)"
who kim
r 'echo "취미: 등산" >> kim.md'
t; r git add kim.md; r git commit -m '"docs: kim 취미 추가"'
r git push origin main
who park
r 'echo "kim 메모" >> kim.md'
r git pull origin main
