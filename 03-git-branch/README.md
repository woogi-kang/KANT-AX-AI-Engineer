# 03. Git 브랜치

커밋을 점으로, 브랜치를 그 점에 붙은 이름표로 그려서 명령마다 그래프가 어떻게 바뀌는지 봐요. 브랜치를 만들고, 합치고, 충돌을 풀고, GitHub에서 Pull Request로 합치는 데까지 이어서 해요. 02에서 만든 `hello-git` 저장소로 이어서 실습해요.

## 슬라이드 받기

| 형식 | 받기 | 이럴 때 |
| --- | --- | --- |
| HTML (애니메이션 포함) | [브라우저로 열기](https://woogi-kang.github.io/KANT-AX-AI-Engineer/03-git-branch/git-branch-slides.html) | 키보드 →, ← 로 넘기고 N은 발표자 노트, F는 전체 화면이에요 |
| PDF (30장) | [바로 받기](https://github.com/woogi-kang/KANT-AX-AI-Engineer/raw/main/03-git-branch/git-branch-slides.pdf) · [GitHub에서 보기](./git-branch-slides.pdf) | 인쇄하거나 휴대폰으로 볼 때 |

PDF에는 애니메이션이 끝난 모습이 한 장씩 담겨 있어요.

## 그래프 읽는 법

| 모양 | 뜻 |
| --- | --- |
| 점 | 커밋 하나 |
| 흰 점 | 두 줄기를 합친 merge 커밋 |
| 색 이름표 (`main`, `feat/greeting`) | 브랜치. 커밋을 가리키는 이름표예요 |
| 검은 `HEAD` | 지금 내가 있는 브랜치 |

## 슬라이드 순서

| 파트 | 쪽 | 다루는 것 |
| --- | --- | --- |
| 1. 브랜치란? | 3–4 | 왜 쓰는지, 이름표와 HEAD |
| 2. 만들고 합치기 | 5–13 | `branch`, `checkout -b`, `merge`, fast-forward, `branch -d`, 이름 규칙 |
| 3. 갈라진 길 합치기 | 14–17 | merge 커밋 |
| 4. 충돌 풀기 | 18–21 | 충돌 표시 읽기, 고치고 커밋 |
| 5. GitHub에서 함께 | 22–26 | `push origin 브랜치`, Pull Request, GitHub Flow |
| 6. 막힐 때 | 27–29 | 자주 나는 에러 |

마지막 30쪽은 한 장 요약이에요.

## 따라 해 보기

**브랜치 만들고 커밋하기**

```bash
git branch                          # 브랜치 목록, * 가 지금 있는 곳
git checkout -b feat/greeting       # 만들고 바로 옮겨 가기
echo "nice to meet you" >> hello.md
git add hello.md
git commit -m "feat: 반가움 인사 추가"
```

**main으로 합치기**

merge는 받는 쪽에서 해요. 먼저 main으로 가고, 가져올 브랜치 이름을 적어요.

```bash
git checkout main
git merge feat/greeting
git branch -d feat/greeting         # 다 쓴 브랜치 지우기
git log --oneline --graph --all
```

**GitHub에서 Pull Request로 합치기**

```bash
git checkout -b feat/emoji
git add bye.md
git commit -m "feat: 끝인사 하나 더"
git push origin feat/emoji
```

GitHub에서 Pull Request를 만들고 Merge 버튼으로 합쳐요. 그다음 내 컴퓨터의 main도 맞춰요.

```bash
git checkout main
git pull origin main
git branch -d feat/emoji
```

## merge가 끝나는 두 모습

| 모습 | 언제 | 그래프 |
| --- | --- | --- |
| Fast-forward | main에 새 커밋이 없을 때 | main 이름표만 앞으로 옮겨져요 |
| merge 커밋 | main과 브랜치 양쪽에 새 커밋이 있을 때 | 둘을 잇는 흰 점이 새로 생겨요 |

merge 커밋을 만들 때 메시지 편집기가 열려요. 그대로 저장하고 닫으면 돼요. vim이면 Esc를 누르고 `:wq`, Enter를 쳐요.

## 충돌이 나면

1. `git status`로 `both modified:` 파일을 찾아요.
2. 파일을 열어 `<<<<<<<`, `=======`, `>>>>>>>` 사이에서 남길 내용만 두고 표시 세 줄을 지워요.
3. `git add 파일`
4. `git commit -m "fix: 충돌 해결"`

`<<<<<<< HEAD` 아래는 지금 내 브랜치 내용이고, `=======` 아래는 합치려는 브랜치 내용이에요.

## 브랜치 이름 규칙

`타입/하는-일` 형식으로 소문자와 하이픈만 써요. 타입은 커밋 메시지와 같은 말을 써요.

| 이렇게 | 피해요 |
| --- | --- |
| `feat/login-button` | `test`, `내작업`, `final2` |
| `fix/12-signup-error` | `Feat/Login Button` |

## 막혔을 때

| 이런 메시지가 나오면 | 이렇게 해요 |
| --- | --- |
| `pathspec 'feat/nope' did not match` | 없는 브랜치예요. `git branch`로 이름 확인, 새로 만들 땐 `git checkout -b` |
| `a branch named 'feat/a' already exists` | 이미 있어요. `-b` 없이 `git checkout feat/a` |
| `would be overwritten by checkout` | 고친 내용이 남아 있어요. `git add`, `git commit` 뒤에 옮기기 |
| `is not fully merged` | 아직 합치지 않은 커밋이 있어요. `git checkout main`, `git merge 브랜치` 뒤에 지우기 |

---

## 강사용

```
slides/
  deck.json        슬라이드 순서와 파트 구분
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen_branch.py    커밋 그래프 실습 장면(b0~b15)을 만드는 스크립트
  gen_pages.py     표지, 목차, 개념, PR, 에러 장을 만드는 스크립트
  check.js         글자 넘침, 겹침, 여백 검사
  deckrender.js    export.js와 build_player.js가 같이 쓰는 렌더링 코드
  export.js        PDF 한 파일로 뽑기
  build_player.js  애니메이션까지 재생되는 HTML 한 파일 만들기
  icons/           아이콘 (Lucide, ISC 라이선스)
git-branch-slides.html  수강생 배포용 HTML
git-branch-slides.pdf   수강생 배포용 PDF
```

슬라이드 HTML을 직접 고치지 말고 스크립트를 고친 뒤 다시 만들어요.

```bash
python3 tools/gen_branch.py slides
python3 tools/gen_pages.py slides
node tools/check.js slides shots
node tools/export.js slides git-branch-slides.pdf
node tools/build_player.js slides git-branch-slides.html
```

터미널 출력은 git 2.43에서 실제로 실행해 확인했어요. 해시는 날짜를 고정해서 만든 값이라 내 화면과 달라요. 화면 폭 때문에 줄인 출력은 발표자 노트에 적어 두었어요.
