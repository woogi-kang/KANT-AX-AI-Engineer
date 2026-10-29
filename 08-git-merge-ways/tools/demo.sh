#!/usr/bin/env bash
# Replays every way of joining two lines of history in throwaway repos and prints each command with its real output.
# Every case starts from a copy of the same state: A, B on main, then C on main and D, E on feature/login-button.
# GitHub is a local bare repo reached through the https://github.com/kim/merge-lab.git address. Teammate lee is a second clone.
# Usage: bash tools/demo.sh /tmp/merge-demo
set -e
D=${1:?폴더 경로를 넣어 주세요}
rm -rf "$D"; mkdir -p "$D/home"
export HOME="$D/home" LANG=C.UTF-8 GIT_EDITOR=true
URL=https://github.com/kim/merge-lab.git
git config --global user.name kim
git config --global user.email kim@example.com
git config --global init.defaultBranch main
git config --global core.pager cat
git config --global log.decorate short
git config --global pull.rebase false
# point the GitHub address at another local bare repo
point() { git config --global --remove-section url."$GH" 2>/dev/null || true; GH=$1; git config --global url."$GH".insteadOf "$URL"; }
point "$D/github.git"
n=0
t() { n=$((n+1)); local d="2026-10-29T15:$(printf %02d $n):00+09:00"; export GIT_AUTHOR_DATE=$d GIT_COMMITTER_DATE=$d; }
at() { local d="2026-10-29T16:$1:00+09:00"; export GIT_AUTHOR_DATE=$d GIT_COMMITTER_DATE=$d; }
r() { echo "\$ $*"; eval "$@" 2>&1 | sed -E "s#$D/[a-z]+\.git#$URL#g; s#$D/[a-z]+#https://github.com/kim/merge-lab#g; s#.*\x1b\[K##; s#^(Rebasing \([0-9/]+\))+##" || true; }
step() { echo; echo "=== $*"; }
# copy a saved state into a new folder and move there
fresh() { rm -rf "$D/$2"; cp -r "$D/$1" "$D/$2"; cd "$D/$2"; }
B=feature/login-button

step "0 A, B"
mkdir "$D/base"; cd "$D/base"; git init -q
t; printf "# 로그인\n" > login.md; git add login.md; git commit -q -m "feat: 로그인 화면 추가"
t; printf "아이디\n" >> login.md; git add login.md; git commit -q -m "feat: 아이디 입력 추가"
r git log --oneline

step "1 브랜치에서 D, E"
r git checkout -b $B
t; r 'echo "로그인 버튼" >> login.md'; r git add login.md; r git commit -m '"feat: 로그인 버튼 추가"'
t; r 'sed -i "s/^로그인 버튼$/[로그인] 버튼/" login.md'; r git add login.md; r git commit -m '"fix: 버튼 글자 고치기"'
r git checkout main
cp -r "$D/base" "$D/straight"            # main에 새 커밋이 없는 상태
step "2 main에 C"
t; r 'echo "# merge-lab" > README.md'; r git add README.md; r git commit -m '"docs: README 추가"'
r git log --oneline
r git log --oneline $B
cp -r "$D/base" "$D/split"               # 갈라진 상태

step "3 fast-forward"
fresh straight ff
at 01; r git merge $B
r git log --oneline

step "4 --no-ff"
fresh straight noff
at 02; r git merge --no-ff $B
r git log --oneline

step "5 merge (갈라짐)"
fresh split merge
at 03; r git merge $B
r git log --oneline
r cat login.md

step "6 rebase"
fresh split rebase
r git checkout $B
r git log --oneline
at 04; r git rebase main
r git log --oneline
r git checkout main
r git merge $B
r git log --oneline

step "7 squash"
fresh split squash
at 05; r git merge --squash $B
r git status
r git commit -m '"feat: 로그인 버튼 추가"'
r git log --oneline
r git log --oneline $B
r git branch -d $B

step "8 pull: GitHub에 C(lee), 내 main에 D"
mkdir "$D/p"; cd "$D/p"
git init -q --bare "$D/github.git"
cp -r "$D/straight" "$D/p/kim"; cd "$D/p/kim"
git branch -q -D $B
git remote add origin $URL; git push -q origin main 2>/dev/null
git clone -q $URL "$D/p/lee"; cd "$D/p/lee"
GIT_AUTHOR_NAME=lee GIT_AUTHOR_EMAIL=lee@example.com GIT_COMMITTER_NAME=lee GIT_COMMITTER_EMAIL=lee@example.com bash -c 'echo "# merge-lab" > README.md; git add README.md; git commit -q -m "docs: README 추가"; git push -q origin main 2>/dev/null'
cd "$D/p/kim"
at 10; echo "로그인 버튼" >> login.md; git add login.md; git commit -q -m "feat: 로그인 버튼 추가"
r git push origin main
r git fetch origin
r git log --oneline
r git log --oneline origin/main
cp -r "$D/p/kim" "$D/p/kim0"

step "8a 설정 없음"
fresh p/kim0 p/none
r git config --global --unset pull.rebase
at 11; r git pull origin main
step "8b pull.rebase false"
fresh p/kim0 p/false
r git config --global pull.rebase false
r git config --global pull.rebase
at 12; r git pull origin main
r git log --oneline
step "8c pull.rebase true"
fresh p/kim0 p/true
at 13; r git -c pull.rebase=true pull origin main
r git log --oneline
step "8d pull.ff only"
fresh p/kim0 p/ffonly
r git -c pull.ff=only pull origin main
r git log --oneline
step "8e pull.ff only, 갈라지지 않았을 때"
cd "$D/p/lee"; r git -c pull.ff=only pull origin main

step "9 충돌: 같은 줄을 양쪽에서"
fresh straight conf
r git checkout -q -b feature/login-title
t; r 'sed -i "1s/.*/# 로그인하기/" login.md'; r git add login.md; r git commit -m '"feat: 로그인 제목 바꾸기"'
r git checkout -q main
t; r 'sed -i "1s/.*/# 로그인 페이지/" login.md'; r git add login.md; r git commit -m '"feat: 로그인 제목 다듬기"'
cp -r "$D/conf" "$D/conf0"
step "9a merge"
fresh conf0 c-merge
r git merge feature/login-title
r git merge --abort
step "9b rebase"
fresh conf0 c-rebase
r git checkout -q feature/login-title
r git rebase main
r git status
r cat login.md
r git rebase --abort
r git log --oneline
step "9c squash"
fresh conf0 c-squash
r git merge --squash feature/login-title
step "9d rebase 충돌 풀기"
fresh conf0 c-rebase2
r git checkout -q feature/login-title
r git rebase main
printf "# 로그인하기\n아이디\n" > login.md
r cat login.md
r git add login.md
at 30; r git rebase --continue
r git log --oneline

step "10 push한 브랜치를 rebase하면"
fresh split shared
git init -q --bare "$D/shared.git"; point "$D/shared.git"
git remote add origin $URL
git push -q origin main $B 2>/dev/null
r git checkout $B
at 20; r git rebase main
r git push origin $B

step "11 GitHub에서 Squash and merge 한 뒤"
fresh split gh
git init -q --bare "$D/gh.git"; point "$D/gh.git"
git remote add origin $URL
git push -q origin main $B 2>/dev/null
# the third clone stands in for GitHub's Squash and merge button
git clone -q $URL "$D/gh-web"; cd "$D/gh-web"
at 40; git merge -q --squash origin/$B >/dev/null 2>&1; git commit -q -m "feat: 로그인 버튼 추가 (#1)"; git push -q origin main 2>/dev/null
cd "$D/gh"
r git checkout main
at 41; r git pull origin main
r git log --oneline
r git branch -d $B
