#!/usr/bin/env bash
# Replays the deck's practice in a throwaway repo and prints every command with its real output.
# GitHub is a local bare repo reached through the https://github.com/kim/hello-git.git address.
# Usage: bash tools/demo.sh /tmp/graph-demo
set -e
D=${1:?폴더 경로를 넣어 주세요}
rm -rf "$D"; mkdir -p "$D/home" "$D/hello-git"
export HOME="$D/home" LANG=C.UTF-8
git config --global user.name kim
git config --global user.email kim@example.com
git config --global init.defaultBranch main
git config --global core.pager cat
git config --global log.decorate short
git config --global url."$D/github.git".insteadOf https://github.com/kim/hello-git.git
git init -q --bare "$D/github.git"
n=0
t() { n=$((n+1)); local d="2026-10-29T10:$(printf %02d $n):00+09:00"; export GIT_AUTHOR_DATE=$d GIT_COMMITTER_DATE=$d; }
r() { echo "\$ $*"; eval "$@" 2>&1 | sed "s#$D/github.git#https://github.com/kim/hello-git.git#; s#$D/github#https://github.com/kim/hello-git#" || true; }
step() { echo; echo "=== $*"; }
cd "$D/hello-git"

git init -q; t
printf "# 로그인\n아이디\n비밀번호\n" > login.md
git add login.md; git commit -q -m "feat: 로그인 화면 추가"
git remote add origin https://github.com/kim/hello-git.git
git push -q origin main 2>/dev/null
r git log --oneline

step "1 고치고 아직 add 전"
r 'echo "로그인 버튼" >> login.md'
r git status
step "2 commit"
t; r git add login.md; r git commit -m '"feat: 로그인 버튼 추가"'
r git log --oneline
step "3 push"
r git push origin main
r git log --oneline

step "4 팀원이 GitHub에 올림"
t
( cd "$D" && git clone -q https://github.com/kim/hello-git.git lee && cd lee &&
  git config user.name lee && git config user.email lee@example.com &&
  echo "# hello-git" > README.md && git add README.md && git commit -q -m "docs: README 추가" && git push -q origin main 2>/dev/null )
step "5 fetch"
r git fetch origin
r git log --oneline
r git log --oneline origin/main
step "6 pull"
r git pull origin main
r git log --oneline

step "7 브랜치 만들기"
r git checkout -b feature/login
r git log --oneline
step "8 브랜치에서 커밋"
r 'echo "비밀번호 찾기" >> login.md'
t; r git add login.md; r git commit -m '"feat: 비밀번호 찾기 추가"'
r git log --oneline
step "9 main으로 돌아와 커밋"
r git checkout main
r 'echo "실행 방법은 준비 중이에요" >> README.md'
t; r git add README.md; r git commit -m '"docs: README에 실행 방법 추가"'
r git log --oneline
step "10 merge"
# 수강생 화면에서는 vim이 열려요. 여기서는 기본 메시지 그대로 저장해요.
export GIT_EDITOR=true
t; r git merge feature/login
r git log --oneline
step "11 push"
r git push origin main
r git log --oneline
step "12 커밋 하나 보기"
r git show --stat HEAD~1
r "git log --format='%H %P %ad %an %s' --date=format:'%d %b %Y %H:%M'"
