#!/usr/bin/env bash
# Replays the deck's practice in a throwaway repo and prints every command with its real output.
# Usage: bash tools/demo.sh /tmp/diff-demo
set -e
D=${1:?폴더 경로를 넣어 주세요}
rm -rf "$D"; mkdir -p "$D/home" "$D/hello-git"; cd "$D/hello-git"
export HOME="$D/home" LANG=C.UTF-8
git config --global user.name kim
git config --global user.email kim@example.com
git config --global init.defaultBranch main
git config --global core.pager cat
git config --global log.decorate short
git config --global pull.rebase false
n=0
t() { n=$((n+1)); local d="2026-10-29T10:$(printf %02d $n):00+09:00"; export GIT_AUTHOR_DATE=$d GIT_COMMITTER_DATE=$d; }
r() { echo "\$ $*"; eval "$@" || true; }
step() { echo; echo "=== $*"; }

git init -q; t
printf "# 로그인\n아이디\n비밀번호\n" > login.md
git add login.md; git commit -q -m "feat: 로그인 화면 추가"

step "1 고친 뒤 git diff"
printf "# 로그인\n아이디\n비밀번호 (8자 이상)\n로그인 버튼\n" > login.md
r git diff
step "2 add 뒤 git diff"
r git add login.md; r git diff
step "3 git diff --staged"
r git diff --staged
step "4 add 뒤 또 고침"
echo "아이디 저장" >> login.md
r git diff; r git diff --staged
step "5 commit 뒤"
t; r git add login.md; r git commit -m '"feat: 로그인 화면에 안내와 버튼 추가"'; r git diff; r git diff --staged
step "6 새 파일은 git diff에 안 나옴"
r 'echo "# 회원가입" > signup.md'; r git diff; r git status; rm signup.md
step "7 git show"
r git show
r git log --oneline

step "8 브랜치에서 작업"
r git checkout -b feature/login
printf "# 로그인하기\n아이디\n비밀번호 (8자 이상)\n로그인 버튼\n아이디 저장\n비밀번호 찾기\n" > login.md
t; r git add login.md; r git commit -m '"feat: 로그인 제목 바꾸고 비밀번호 찾기 추가"'
r git checkout main
step "9 브랜치 비교"
r git diff main feature/login
r git diff feature/login main
r git diff --stat main feature/login
step "10 main에서 같은 줄 고침"
printf "# 로그인 페이지\n아이디\n비밀번호 (8자 이상)\n로그인 버튼\n아이디 저장\n" > login.md
t; r git add login.md; r git commit -m '"feat: 로그인 제목 다듬기"'
r git diff main feature/login
step "11 충돌"
t; r git merge feature/login
r git diff
r git status
step "12 충돌 풀고 확인"
printf "# 로그인하기\n아이디\n비밀번호 (8자 이상)\n로그인 버튼\n아이디 저장\n비밀번호 찾기\n" > login.md
r git diff
r git add login.md
r git diff --staged
t; r git commit -m '"fix: 로그인 제목 충돌 해결"'
r git log --oneline

step "13 .gitignore"
r 'echo "API_KEY=abc123" > .env'
r git status
r 'echo ".env" > .gitignore'
r git status
r git add .gitignore
t; r git commit -m '"chore: .env를 gitignore에 추가"'
r git status

step "14 이미 커밋한 파일은 .gitignore로 안 숨겨짐"
r 'echo "start" > app.log'
r git add app.log
t; r git commit -m '"chore: 로그 파일 추가"'
r 'echo "*.log" >> .gitignore'
r 'echo "error" >> app.log'
r git status
r git rm --cached app.log
r git status
