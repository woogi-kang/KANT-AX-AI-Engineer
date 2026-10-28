# Git 기본 흐름, 눈으로 보기

Git을 처음 배우는 수강생용 시각 자료(43장)예요. 명령을 칠 때마다 파일이 네 칸(작업 폴더, 대기실, 내 저장소, 원격 저장소) 중 어디로 가는지 그림과 애니메이션으로 따라갑니다.

- 발표용 덱: https://claude.ai/artifact/9Ng96bQJJporFMth1tdkcQ (공유 메뉴로 열어 줘야 다른 사람이 볼 수 있어요)
- 이 폴더는 덱의 원본이에요. 덱을 고친 뒤 여기도 같이 맞춰 둡니다.

## 구성

| 파트 | 내용 |
| --- | --- |
| 개념 잡기 | 4개의 공간, 택배 비유, 파일 상태 용어 |
| 혼자 기록하기 | config, init, add, commit, 커밋 메시지 규칙 |
| GitHub과 연결 | 빈 저장소 만들기, remote add, push origin main |
| 함께 작업하기 | clone, fetch, pull origin main |
| 되돌리기 | reset, reflog, revert |
| 막힐 때 | git status 읽기, 자주 나는 에러 |

## 수업 규칙

- `git push -u`(set-upstream)는 쓰지 않아요. push와 pull은 항상 `origin main`을 적습니다.
- 앞서 있는지/뒤처졌는지는 `git fetch origin` 뒤 `git log --oneline --graph --all`로 봐요.
- `git restore`는 다루지 않아요.
- 커밋 메시지는 Conventional Commits(`feat:`, `fix:`, `docs:` …) 형식을 써요.
- 터미널 출력은 git 2.43에서 실제로 실행해 확인한 결과예요. 해시는 이야기에 맞춰 고정한 값입니다.

## 파일

```
deck/
  deck.json        슬라이드 순서와 파트 구분
  slides/*.html    한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen_scenes.py    4칸 실습 장면(s1~s18)을 만드는 스크립트
  check.js         글자 넘침, 겹침, 여백을 검사하고 스크린샷을 남기는 스크립트
```

실습 장면을 고칠 땐 `slides/s*.html`을 직접 고치지 말고 스크립트를 고친 뒤 다시 만들어요.

```bash
python3 tools/gen_scenes.py deck/slides
node tools/check.js deck/slides shots          # 전체 검사 (Playwright 필요)
node tools/check.js deck/slides shots reflog   # 특정 장만
```
