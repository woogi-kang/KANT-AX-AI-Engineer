# 07 · restore와 stash로 되돌리고 치워 두기

> 커밋하기 전의 변경을 다루는 명령 세 가지를 배워요. 고친 걸 버리는 `git restore`, add를 취소하는 `git restore --staged`, 고치던 걸 잠깐 치워 두는 `git stash`예요. 02의 네 칸 그림과 `hello-git` 저장소의 `login.md`를 그대로 써요.

| 슬라이드 | 분량 | 이전 모듈 | 다음 모듈 |
| --- | --- | --- | --- |
| [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/07-git-restore-stash/git-restore-stash-slides.html) | 24장 · 6개 파트 | [05 · VS Code Git Graph로 기록 보기](../05-git-graph) | 준비 중 |

## 학습 목표

이 모듈을 마치면 다음을 할 수 있어요.

- `git status`의 괄호 안 안내 줄을 읽고 다음에 칠 명령을 골라요.
- `git restore 파일`로 작업 폴더의 변경을 버리고, 버리기 전에 `git diff`로 확인해요.
- `git restore --staged 파일`로 add를 취소해요.
- restore는 파일을, reset은 이름표를 옮긴다는 차이를 말해요.
- pull이나 checkout이 막혔을 때 `git stash`, `git stash list`, `git stash pop`으로 풀어요.
- pop에서 충돌이 나면 03처럼 풀고 `git stash drop`으로 서랍을 비워요.

## 구성

| 파트 | 쪽 | 내용 |
| --- | :---: | --- |
| 들어가기 | 1–4 | 이럴 때 쓰는 명령, 네 칸 그림과 서랍 |
| 1. git restore | 5–8 | status 안내 읽기, 버리기 전 `git diff`, 되찾을 수 없다는 주의 |
| 2. git restore --staged | 9–11 | `git add .`로 올린 메모 내리기, `--staged`가 있고 없고의 차이 |
| 3. reset과 무엇이 달라요 | 12 | restore는 파일, reset은 이름표 |
| 4. git stash | 13–18 | pull이 막힐 때, stash, stash list 읽기, pull, pop, checkout이 막힐 때 |
| 5. 팀에서 쓰기 | 19–22 | stash, pull, pop 순서, pop 충돌과 `git stash drop`, 버릴까 치울까 남길까 |
| 6. 막힐 때 | 23 | 자주 나오는 메시지 네 가지 |
| 요약 | 24 | 한 장 요약 |

## 핵심 개념

### 네 칸 중 어디를 바꾸나

| 명령 | 바꾸는 곳 | 커밋 기록 | 언제 |
| --- | --- | --- | --- |
| `git restore 파일` | ① 작업 폴더를 마지막 커밋 모습으로 | 그대로 | 고친 게 필요 없을 때 |
| `git restore --staged 파일` | ② 대기실에서 내리기. ① 내용은 그대로 | 그대로 | add를 취소할 때 |
| `git stash` | ① ② 변경을 서랍에 넣고 마지막 커밋 모습으로 | 그대로 | 덜 끝났는데 pull, checkout 해야 할 때 |
| `git reset HEAD~1` | ③ 이름표를 한 칸 뒤로 (02, 03) | 커밋 취소 | push 전에 커밋을 없앨 때 |

서랍(stash)은 내 컴퓨터에만 있어요. push해도 GitHub에 올라가지 않아요.

### status가 알려 주는 다음 명령

```
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)          add 취소
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)   고친 것 버리기
```

pull이나 checkout이 `Please commit your changes or stash them`으로 멈추면 커밋하거나 stash 하라는 뜻이에요.

### 버릴까, 치울까, 남길까

| 상황 | 명령 |
| --- | --- |
| 고친 게 필요 없어요 | `git restore 파일` |
| 덜 끝났는데 pull이나 checkout을 해야 해요 | `git stash` 뒤 `git stash pop` |
| 커밋할 만큼 끝났어요 | `git add 파일` 뒤 `git commit -m "..."` |

> **주의** `git restore`로 버린 변경은 되찾을 수 없어요. 커밋하지 않은 변경은 Git에 기록이 없어서 reflog에도 남지 않아요. 버리기 전에 `git diff`로 보고, 파일 이름을 꼭 적어요. `git restore .`은 모든 파일의 변경을 한 번에 버려요.

## 실습

### 1. 망친 파일 되돌리기

GitHub에 올라간 커밋이 하나 있는 `hello-git` 저장소에서 시작해요. `login.md`에는 `# 로그인`, `아이디`, `비밀번호` 세 줄이 있어요.

```bash
echo "로그인 버튼" > login.md      # >> 대신 > 를 써서 덮어썼어요
cat login.md                       # 한 줄만 남았어요
git status                         # 안내 줄에 git restore가 보여요
git diff                           # 사라질 줄 확인
git restore login.md
cat login.md                       # 세 줄이 돌아왔어요
```

### 2. add 취소하기

```bash
echo "로그인 버튼" >> login.md
echo "내일 할 일: 디자인 묻기" > memo.md
git add .                          # memo.md까지 올라갔어요
git status
git restore --staged memo.md       # memo.md만 대기실에서 내려요
git status                         # memo.md는 Untracked, 파일은 그대로
git commit -m "feat: 로그인 버튼 추가"
git push origin main
rm memo.md
```

### 3. pull이 막힐 때 stash 쓰기

팀원이 `login.md` 첫 줄을 `# 로그인 페이지`로 고쳐 push해 둬요. 혼자 연습할 땐 GitHub 웹에서 `login.md`를 직접 고쳐 커밋해도 돼요.

```bash
echo "비밀번호 찾기" >> login.md   # 고치던 중
git pull origin main               # Please commit your changes or stash them
git stash                          # 서랍에 넣기
git status                         # working tree clean
git stash list                     # stash@{0}: WIP on main: ...
git pull origin main               # 이제 받아져요
git stash pop                      # 꺼내서 다시 얹기
cat login.md                       # 받은 제목과 내 줄이 같이 있어요
git add login.md
git commit -m "feat: 비밀번호 찾기 추가"
git push origin main
```

### 4. pop에서 충돌이 나면

팀원과 내가 같은 줄을 고쳤으면 `git stash pop`에서 충돌이 나요.

```
<<<<<<< Updated upstream
비밀번호 재설정                 pull로 받은 쪽 (팀원)
=======
비밀번호 찾기 (이메일)          서랍에서 꺼낸 쪽 (나)
>>>>>>> Stashed changes
```

1. 표시 줄 세 개를 지우고 남길 내용으로 고쳐요.
2. `git add login.md`
3. `git stash drop` 으로 서랍에 남은 걸 지워요. 충돌이 나면 pop이 서랍을 비우지 않아요.
4. `git commit -m "..."` 뒤 `git push origin main`

## 명령어 요약

| 명령 | 하는 일 |
| --- | --- |
| `git restore 파일` | 작업 폴더의 변경 버리기 (되찾을 수 없어요) |
| `git restore --staged 파일` | add 취소. 고친 내용은 그대로 |
| `git stash` | 고치던 걸 서랍에 넣기 |
| `git stash list` | 서랍 안 보기. `stash@{0}`이 가장 최근 |
| `git stash pop` | 맨 위 서랍을 꺼내 다시 얹기 |
| `git stash drop` | 맨 위 서랍을 꺼내지 않고 지우기 |

## 문제 해결

| 증상 | 원인과 해결 |
| --- | --- |
| `Please commit your changes or stash them before you merge.` | 고치던 파일을 pull이 덮을 수 있어요. 끝났으면 커밋, 덜 끝났으면 `git stash` 뒤 pull 해요 |
| `Please commit your changes or stash them before you switch branches.` | checkout도 같아요. `git stash`, checkout, 일 끝나면 돌아와서 `git stash pop` |
| `No local changes to save` | 고친 게 없거나 새 파일만 있어요. 새 파일은 `git add` 해야 서랍에 들어가요 |
| `stash list`에 여러 줄이 있어요 | pop을 잊고 또 stash 했어요. 맨 위 `stash@{0}`부터 하나씩 `git stash pop` |
| `CONFLICT ... The stash entry is kept in case you need it again.` | 같은 줄을 둘 다 고쳤어요. 실습 4처럼 풀고 `git stash drop` |
| `error: pathspec '...' did not match any file(s) known to git` | 파일 이름이 틀렸어요. `git status`로 이름을 확인하고 Tab으로 자동 완성해요 |
| restore로 버린 걸 되찾고 싶어요 | 되찾을 수 없어요. 다음엔 `git diff`로 먼저 보고, 남길 게 있으면 커밋부터 해요 |

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py           모든 장 생성 (네 칸 장면과 서랍, 비교표, 팀 순서)
  demo.sh          실습을 새 저장소에서 다시 실행해 실제 출력 확인 (팀원 lee 포함)
  check.js         글자 넘침, 겹침, 여백 검사와 스크린샷
  deckrender.js    export.js와 build_player.js가 같이 쓰는 렌더링 코드
  export.js        PDF 내보내기
  build_player.js  애니메이션이 재생되는 HTML 한 파일 만들기
  icons/           아이콘 (Lucide, ISC 라이선스)
git-restore-stash-slides.html  배포용 HTML
git-restore-stash-slides.pdf   강사용 PDF
```

슬라이드 HTML을 직접 고치지 말고 스크립트를 고친 뒤 다시 만들어요.

```bash
bash tools/demo.sh /tmp/restore-demo
python3 tools/gen.py slides
node tools/check.js slides shots
node tools/build_player.js slides git-restore-stash-slides.html
node tools/export.js slides git-restore-stash-slides.pdf
```

터미널 출력은 `tools/demo.sh`로 git 2.43에서 실제로 실행해 옮겼어요. GitHub 자리는 내 컴퓨터의 빈 저장소로 대신하고 주소만 `https://github.com/kim/hello-git.git`으로 보이게 했어요. 팀원 lee는 같은 저장소를 하나 더 clone해서 흉내 냈어요. 날짜를 고정해서 해시가 매번 같게 나와요(e12ffc2, 15d92cb는 05와 같아요). 화면 폭 때문에 뺀 줄은 발표자 노트에 적어 두었어요.

</details>

---

[← 이전: 05 · VS Code Git Graph로 기록 보기](../05-git-graph) · [커리큘럼](../README.md)
