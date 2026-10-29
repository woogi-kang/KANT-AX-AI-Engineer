#!/usr/bin/env bash
# Replays the deck's practice in a throwaway repo and prints every command with its real output.
# GitHub is a local bare repo reached through the https://github.com/kim/hello-git.git address.
# Teammate lee works in a second clone of the same bare repo.
# Usage: bash tools/demo.sh /tmp/restore-demo
set -e
D=${1:?폴더 경로를 넣어 주세요}
rm -rf "$D"; mkdir -p "$D/home"
export HOME="$D/home" LANG=C.UTF-8
git config --global user.name kim
git config --global user.email kim@example.com
git config --global init.defaultBranch main
git config --global core.pager cat
git config --global log.decorate short
git config --global pull.rebase false
git config --global url."$D/github.git".insteadOf https://github.com/kim/hello-git.git
git init -q --bare "$D/github.git"
n=0
t() { n=$((n+1)); local d="2026-10-29T10:$(printf %02d $n):00+09:00"; export GIT_AUTHOR_DATE=$d GIT_COMMITTER_DATE=$d; }
r() { echo "\$ $*"; eval "$@" 2>&1 | sed "s#$D/github.git#https://github.com/kim/hello-git.git#; s#$D/github#https://github.com/kim/hello-git#" || true; }
step() { echo; echo "=== $*"; }
lee() { (cd "$D/lee" && GIT_AUTHOR_NAME=lee GIT_AUTHOR_EMAIL=lee@example.com GIT_COMMITTER_NAME=lee GIT_COMMITTER_EMAIL=lee@example.com "$@"); }

mkdir "$D/hello-git"; cd "$D/hello-git"
git init -q; t
printf "# 로그인\n아이디\n비밀번호\n" > login.md
git add login.md; git commit -q -m "feat: 로그인 화면 추가"
git remote add origin https://github.com/kim/hello-git.git
git push -q origin main 2>/dev/null
git clone -q https://github.com/kim/hello-git.git "$D/lee"
r git log --oneline

step "1 > 를 잘못 써서 파일을 덮어씀"
r 'echo "로그인 버튼" > login.md'
r cat login.md
r git status
r git diff
step "2 git restore"
r git restore login.md
r cat login.md
r git status

step "3 git add . 로 메모까지 올림"
r 'echo "로그인 버튼" >> login.md'
r 'echo "내일 할 일: 디자인 묻기" > memo.md'
r git add .
r git status
step "4 git restore --staged"
r git restore --staged memo.md
r git status
r cat memo.md
t; r git commit -m '"feat: 로그인 버튼 추가"'
r git push origin main
r rm memo.md

step "5 add 한 파일을 restore --staged 하면 내용은 그대로"
r 'echo "아이디 저장" >> login.md'
r git add login.md
r git restore --staged login.md
r git status
r git diff
r git restore login.md

step "6 팀원 lee가 제목을 고쳐 push"
lee git pull -q origin main
lee sed -i "1s/.*/# 로그인 페이지/" login.md
t; lee git add login.md; lee git commit -q -m "feat: 로그인 제목 바꾸기"; lee git push -q origin main 2>/dev/null

step "7 나는 고치던 중에 pull"
r 'echo "비밀번호 찾기" >> login.md'
r git pull origin main
step "8 git stash"
r git stash
r git status
r cat login.md
r git stash list
step "9 pull"
r git pull origin main
step "10 git stash pop"
r git stash pop
r cat login.md
r git stash list
r git diff
t; r git add login.md; r git commit -m '"feat: 비밀번호 찾기 추가"'
r git push origin main
r git log --oneline

step "11 같은 줄을 둘이 고침"
lee git pull -q origin main
lee sed -i "s/^비밀번호 찾기$/비밀번호 재설정/" login.md
t; lee git add login.md; lee git commit -q -m "fix: 비밀번호 찾기를 재설정으로 바꾸기"; lee git push -q origin main 2>/dev/null
r 'sed -i "s/^비밀번호 찾기$/비밀번호 찾기 (이메일)/" login.md'
r git stash
r git pull origin main
r git stash pop
r cat login.md
r git status
r git stash list
step "12 충돌 풀기"
printf "# 로그인 페이지\n아이디\n비밀번호\n로그인 버튼\n비밀번호 재설정 (이메일)\n" > login.md
r cat login.md
r git add login.md
r git stash drop
r git stash list
r git status
t; r git commit -m '"feat: 비밀번호 재설정에 이메일 안내 추가"'
r git push origin main

step "13 바뀐 게 없을 때 stash"
r git stash
step "14 새 파일은 stash에 안 들어감"
r 'echo "# 회원가입" > signup.md'
r git stash
r git add signup.md
r git stash
r git status
r git stash pop
r git status
step "15 restore에 없는 파일"
r git restore signup2.md
step "16 stash 두 번"
r 'echo "아이디 저장" >> login.md'
r git stash
r 'echo "자동 로그인" >> login.md'
r git stash
r git stash list

step "17 브랜치 옮길 때"
r git checkout -b feature/login
r 'echo "자동 로그인" >> login.md'
t; r git add login.md; r git commit -m '"feat: 자동 로그인 추가"'
r 'echo "비밀번호 보기" >> login.md'
r git checkout main
