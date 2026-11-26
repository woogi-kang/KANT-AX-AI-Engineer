# 학습 사이트 (site/)

AX 엔지니어 로드맵과 기초 강의를 한곳에 모은 공개 학습 사이트예요. Next.js(App Router, TypeScript)를 정적 파일로만 내보내 Cloudflare Pages에 올려요. 작업은 `develop` 브랜치에서 하고, 미리보기는 https://fullstack-ax-preview.pages.dev 예요. main은 수강생이 쓰고 있어서 사이트 작업으로 건드리지 않아요.

디자인 기준은 핸드북 시안 v16(`design/v16`, 미리보기 `/design/v16/home.html`)이에요. 그림(로고, 표지, 아이콘)은 크게, 글은 짧게 두고 긴 설명은 "펼쳐 보기" 안에 넣어요.

## 실행

Node는 최신 LTS(26)를 써요(`.node-version`). 패키지와 프레임워크는 모두 최신 안정 버전으로 맞춰요(`npm outdated`로 확인).

```bash
cd site
npm ci
npm run dev      # http://localhost:3000 (로드맵 레포를 받고 그림을 복사한 뒤 켜요)
npm run build    # out/에 정적 파일을 만들고, 페이지가 빠짐없이 생겼는지 세요
cd out && python3 -m http.server 8766 &   # 만든 사이트 띄우기
npm run qa       # 모든 화면을 1440, 390 폭으로 열어 넘침, 오류, 깨진 링크를 찾아요
```

## 내용이 오는 곳

원본은 두 레포예요. 사이트에서 내용을 고치지 않아요.

| 사이트 | 원본 |
| --- | --- |
| 강의 단계, 묶음, 레벨, 챕터, 꿀팁, 소식 | 이 레포 `curriculum.json` |
| 챕터 교안, 학습 목표, 구성(파트와 쪽) | 챕터 `README.md` (`lib/chapter.ts`) |
| 슬라이드, PDF | 덱 HTML과 PDF (`scripts/copy-assets.mjs`가 `public/decks/`로 복사) |
| 로드맵 5단계, 주제 문서, 업무 사례, 공개 사례, 실패·중단 사례, 템플릿, 채용 현황, 용어 사전 | 로드맵 레포 [woogi-kang/ax-engineer-roadmap](https://github.com/woogi-kang/ax-engineer-roadmap) (MIT). 빌드할 때 `scripts/fetch-roadmap.mjs`가 `site/.roadmap`에 받아요. 다른 폴더를 쓰려면 `ROADMAP_DIR=폴더` |
| 로드맵 주제와 강의 챕터 잇기 | `content/roadmap-links.json` |
| 덱 표지 그림 | `assets/covers/` (`npm run covers -- 폴더`로 찍어요. 표지의 KANT 글자는 사이트 이름으로 바꿔 찍어요) |
| 도구 로고 | `assets/logos/` (devicon MIT 컬러 로고, uv는 Simple Icons CC0) |

## 주소

| 주소 | 화면 | 영역 |
| --- | --- | --- |
| `/` | 홈 | 공통 |
| `/start/`, `/glossary/` | 시작하기, 용어 사전 | 로드맵 |
| `/roadmap/`, `/roadmap/<주제>/` | 로드맵 5단계, 주제 | 로드맵 |
| `/lectures/`, `/chapters/<폴더>/`, `/tips/`, `/extras/<폴더>/` | 강의 목록, 챕터, 꿀팁 | 강의 |
| `/library/`, `/library/cases/<id>/` | 업무 사례 목록과 상세 | 사례와 자료 |
| `/library/public/`, `/library/failures/`, `/library/templates/`(+`<양식>/`), `/library/jobs/` | 공개 사례, 실패·중단, 템플릿, 채용 현황 | 사례와 자료 |
| `/updates/`, `/updates/<폴더>/`, `/legal/` | 소식, 이 사이트에 대해 | 공통 |
| `/search.json` | 찾기 창 목록(`lib/search.ts`) | 공통 |

## 폴더

| 폴더 | 내용 |
| --- | --- |
| `app/layout.tsx` | 공통 틀: 머리글(찾기, 메뉴, 시작하기, 밝은/어두운 화면 버튼), 왼쪽 목차, 바닥글, 찾기 창 |
| `app/tokens.css` | 색 토큰. 밝은 화면과 어두운 화면(`[data-theme="dark"]`) 두 벌 |
| `app/globals.css` | 여러 화면이 같이 쓰는 모양(타일, 표지 카드, 펼쳐 보기, 거르기 버튼, 찾기 창) |
| `components/ui.tsx` | `Ic`(lucide 아이콘 이름으로), `Ict`(아이콘 칸), `Logo`, `Cover`, `More`(펼쳐 보기), `Crumb`, `PageHead`, `SecHead`, `Diff` |
| `components/` | `SideNav`, `SearchDialog`, `FilterChips`(거르기), `Player`(표지 뒤 덱), `LecCard`, `LibTiles` |
| `lib/` | `content.ts`(강의), `roadmap.ts`(로드맵 레포), `links.ts`, `chapter.ts`, `markdown.ts`, `search.ts`, `site.ts`(이름, 메뉴, 아이콘), `logos.ts` |
| `scripts/` | `fetch-roadmap.mjs`, `copy-assets.mjs`, `check-build.mjs`, `shoot-covers.mjs`, `qa.cjs` |
| `app/library/` | 사례와 자료 영역. 모양은 `library.css`, 데이터는 `lib/library.ts`(case.json, 공개·실패 사례 JSON, 월간 채용 JSON), 거르기는 `components/LibFilter.tsx`(묶음 여러 개와 찾기 칸, 주소 뒤 `?키=값`), 복사 버튼은 `components/CopyText.tsx` |
| `design/` | 디자인 시안. 사이트에서는 `/design/`으로 열려요 |

## 여러 작업이 동시에 고칠 때

- 한 화면에만 쓰는 모양은 그 화면 폴더에 `.css`를 두고 `page.tsx`에서 불러요. `globals.css`에는 여러 화면이 같이 쓰는 것만 더해요.
- `layout.tsx`, `tokens.css`, `components/ui.tsx`, `lib/roadmap.ts`는 공통 틀이에요. 고칠 때는 있던 이름을 바꾸지 말고 더하기만 해요.
- 올리기 전에 `git pull origin develop`으로 받고, merge로 합쳐요.
- 아이콘은 뜻이 있는 자리(단계, 기술 영역, 자료 묶음, 업무 분야)에만 써요. 색은 강조 파랑과 도구 로고 고유색만 써요.
- 숫자와 사례는 두 레포에 있는 값만 써요. 지어낸 숫자, 점검 질문, 출력은 넣지 않아요. 사이트에는 KANT라는 말을 쓰지 않아요.
- 챕터 화면의 실습 칸과 문제 칸 자리: `app/chapters/[dir]/page.tsx`가 교안 절 바로 위에서 `components/practice/ChapterPractice.tsx`(바로 쳐 보기, 코드 실행 영역)와 `components/quiz/ChapterQuiz.tsx`(확인 문제 영역)를 불러요. 두 영역은 그 폴더 안만 고치고 챕터 화면 파일은 건드리지 않아요. 내용이 없는 챕터는 `null`을 돌려줘요.
- 올리기 전에 `npm run build`와 `npm run qa`가 문제 0건으로 끝나는지 보고, 고친 화면은 1440과 390 폭 스크린샷을 직접 열어 봐요(밝은 화면, 어두운 화면 모두).

## 확인 문제

챕터 화면의 "확인 문제"는 챕터 폴더의 `quiz.json`에서 와요(`components/quiz/`). 파트마다 2~3문제를 두고, 틀리면 "다시 보기" 버튼이 위 슬라이드를 그 내용이 있는 쪽으로 열어요(`deck-go`). 고른 답은 화면에만 있고 저장하지 않아요.

```json
{
  "parts": [
    {
      "part": "문자열과 출력",
      "questions": [
        {
          "id": "s1",
          "q": "아래 코드를 실행하면 무엇이 찍히나요?",
          "code": "word = \"python\"\nprint(word[2:5])",
          "choices": ["`yth`", "`tho`", "`thon`"],
          "answer": 1,
          "explain": "`[2:5]`는 2번 선부터 5번 선까지 잘라요.",
          "page": 7,
          "verify": "py"
        }
      ]
    }
  ]
}
```

- `part`는 챕터 README 구성 표의 파트 이름에서 앞 번호를 뺀 것이에요. 들어가기와 정리 파트에는 문제를 두지 않아요.
- `answer`는 정답 보기 번호(0부터), `page`는 다시 볼 슬라이드 쪽이에요. 그 파트 쪽 안이어야 해요.
- 문제, 정답, 해설은 교안과 덱의 실제 출력에만 근거해요. 그 챕터까지 배운 범위(CLAUDE.md 수업 규칙)를 넘지 않아요.
- `verify: "py"`를 붙이면 점검할 때 `code`를 python3로 실행해서 출력이 정답 보기와 같은지 봐요.
- `npm run quiz`(빌드 뒤에도 저절로 돌아요)가 형식, 파트 이름, 쪽 번호, 정답 번호, 실행 결과를 확인해요.
