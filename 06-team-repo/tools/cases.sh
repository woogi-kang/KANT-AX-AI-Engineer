#!/usr/bin/env bash
# Replays the team work cases (part 5) with kim and lee and prints every command with its real output.
# GitHub is a local bare repo at https://github.com/kim/team-intro.git. A third clone ("web") stands in
# for the Merge pull request button on GitHub; its output is not shown on slides.
# Usage: bash tools/cases.sh /tmp/team-cases
set -e
D=${1:?폴더 경로를 넣어 주세요}
rm -rf "$D"; mkdir -p "$D"
export LANG=C.UTF-8 GIT_EDITOR=true
URL=https://github.com/kim/team-intro.git
n=0
t() { n=$((n+1)); local d="2026-10-29T16:$(printf %02d $n):00+09:00"; export GIT_AUTHOR_DATE=$d GIT_COMMITTER_DATE=$d; }
who() {
  export HOME="$D/home-$1"; mkdir -p "$HOME"
  if [ ! -f "$HOME/.gitconfig" ]; then
    git config --global user.name "$1"; git config --global user.email "$1@example.com"
    git config --global init.defaultBranch main; git config --global core.pager cat
    git config --global log.decorate short; git config --global pull.rebase false
    git config --global url."$D/github.git".insteadOf "$URL"
  fi
  cd "$D/$1/team-intro"
  echo; echo "##### $1"
}
r() { echo "\$ $*"; eval "$@" 2>&1 | sed "s#$D/github.git#$URL#g; s#$D/github#https://github.com/kim/team-intro#g" || true; }
step() { echo; echo "=== $*"; }
# GitHub의 Merge pull request 버튼 대신
web_merge() { # branch number author
  ( export HOME="$D/home-web"; cd "$D/web" && git fetch -q origin && git checkout -q main && git merge -q -q --ff-only origin/main 2>/dev/null || true
    t; git merge -q --no-ff "origin/$1" -m "Merge pull request #$2 from $3/$1" && git push -q origin main 2>/dev/null )
}

git init -q --bare -b main "$D/github.git"
mkdir -p "$D/home-web"; HOME="$D/home-web" git config --global user.name kim; HOME="$D/home-web" git config --global user.email kim@example.com
HOME="$D/home-web" git config --global url."$D/github.git".insteadOf "$URL"
t; git init -q -b main "$D/seed"; cd "$D/seed"
printf '# 깃벗 팀\n\n소개: 준비 중\n\n## 멤버\n' > README.md
git -c user.name=kim -c user.email=kim@example.com add README.md
git -c user.name=kim -c user.email=kim@example.com commit -q -m "docs: 팀 README 만들기"
git push -q "$D/github.git" main 2>/dev/null
for p in kim lee; do mkdir -p "$D/$p"; (cd "$D/$p"; git clone -q "$D/github.git" team-intro; cd team-intro; git remote set-url origin "$URL"); done
git clone -q "$D/github.git" "$D/web"; (cd "$D/web"; git remote set-url origin "$URL")

step "C1 작업 시작: main 받고 브랜치 만들기"
who lee
r git checkout main
r git pull origin main
r git checkout -b feature/lee-intro
step "C2 브랜치에서 커밋하고 브랜치 push"
r 'echo "안녕하세요, lee예요" > lee.md'
t; r git add lee.md; r git commit -m '"docs: lee 자기소개 추가"'
r git push origin feature/lee-intro
step "C3 PR 합친 뒤 main 받기 (lee PR #1 merge)"
web_merge feature/lee-intro 1 lee
r git checkout main
r git pull origin main
r git branch -d feature/lee-intro
r git checkout -b feature/lee-hobby
r git log --oneline

step "C4 다른 파일 PR 두 개"
who kim
r git checkout main
r git pull origin main
r git checkout -b feature/kim-intro
r 'echo "안녕하세요, kim이에요" > kim.md'
t; r git add kim.md; r git commit -m '"docs: kim 자기소개 추가"'
r git push origin feature/kim-intro
who lee
r 'echo "취미: 보드게임" >> lee.md'
t; r git add lee.md; r git commit -m '"docs: lee 취미 추가"'
r git push origin feature/lee-hobby
web_merge feature/kim-intro 2 kim
web_merge feature/lee-hobby 3 lee
for p in kim lee; do who $p; r git checkout main; r git pull origin main; r git log --oneline; done

step "C5 같은 줄을 고친 PR 두 개"
who kim
r git checkout -b feature/team-about
r "sed -i 's/소개: 준비 중/소개: 깃 공부 모임/' README.md"
t; r git add README.md; r git commit -m '"docs: 팀 소개 쓰기"'
r git push origin feature/team-about
who lee
r git checkout -b feature/team-about-lee
r "sed -i 's/소개: 준비 중/소개: 매주 화요일 스터디/' README.md"
t; r git add README.md; r git commit -m '"docs: 팀 소개에 모임 날짜 쓰기"'
r git push origin feature/team-about-lee
web_merge feature/team-about 4 kim
step "C5b lee: 내 브랜치에서 main 받아 충돌 풀기"
t; r git pull origin main
r cat README.md
r "printf '# 깃벗 팀\n\n소개: 매주 화요일 깃 공부 모임\n\n## 멤버\n' > README.md"
t; r git add README.md; r git commit -m '"fix: 팀 소개 충돌 해결"'
r git push origin feature/team-about-lee
web_merge feature/team-about-lee 5 lee
r git checkout main
r git pull origin main
r git log --oneline

step "C6 고친 파일이 있는데 pull"
who kim
r git checkout main
r git pull origin main
r git checkout -b feature/kim-member
r 'echo "- kim" >> README.md'
t; r git add README.md; r git commit -m '"docs: 멤버에 kim 추가"'
r git push origin feature/kim-member
web_merge feature/kim-member 6 kim
who lee
r 'echo "- lee" >> README.md'
r git pull origin main
step "C6b 커밋하고 다시 pull"
r git checkout -b feature/lee-member
t; r git add README.md; r git commit -m '"docs: 멤버에 lee 추가"'
t; r git pull origin main

step "C7 고친 파일이 있는데 checkout"
who kim
r git checkout main
r git pull origin main
r git checkout -b feature/kim-hobby
r 'echo "취미: 등산" >> kim.md'
t; r git add kim.md; r git commit -m '"docs: kim 취미 추가"'
r 'echo "좋아하는 음식: 김밥" >> kim.md'
r git checkout main
step "C7b 커밋하고 checkout"
t; r git add kim.md; r git commit -m '"docs: kim 좋아하는 음식 추가"'
r git checkout main

step "C8 main에 커밋해 버림 (push 전)"
who kim
r git pull origin main
r 'echo "- 다음 모임: 11월 5일" >> README.md'
t; r git add README.md; r git commit -m '"docs: 다음 모임 날짜 추가"'
r git branch feature/next-meeting
r git status
r git reset --hard HEAD~1
r git checkout feature/next-meeting
r git log --oneline
