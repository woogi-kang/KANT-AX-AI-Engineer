# 학습 사이트 (site/)

레포의 챕터를 웹 페이지로 묶은 학습 사이트예요. Next.js(App Router, TypeScript)를 정적 파일로만 내보내 Cloudflare Pages에 올려요. 작업은 `develop` 브랜치에서 하고, 미리보기는 https://fullstack-ax-preview.pages.dev 예요.

## 실행

Node는 최신 LTS(26)를 써요(`.node-version`). 패키지와 프레임워크는 모두 최신 안정 버전으로 맞춰요.

```bash
cd site
npm ci
npm run dev      # http://localhost:3000
npm run build    # out/에 정적 파일을 만들고, 페이지가 빠짐없이 생겼는지 세요
```

## 내용이 오는 곳

원본은 레포예요. 사이트에서 내용을 고치지 않아요.

| 사이트 | 레포 |
| --- | --- |
| 단계, 묶음, 레벨, 챕터 목록, 번외, 새 소식 | `curriculum.json` |
| 챕터 본문 | 챕터 `README.md` (맨 위 표와 맨 아래 이동 링크는 빼요) |
| 장 목록, 발표자 노트 | 덱 HTML의 `section` 제목과 `aside` |
| 슬라이드 플레이어, PDF | 덱 HTML과 PDF를 빌드 전에 `public/decks/`로 복사 (`scripts/copy-assets.mjs`) |
| 새 챕터 날짜 | 챕터 README가 처음 커밋된 날 (git log) |

## 폴더

| 폴더 | 내용 |
| --- | --- |
| `app/` | 페이지(홈, `chapters/[dir]`, `extras/[dir]`, `updates`, `legal`, 404), 토큰(`tokens.css`), 공통 모양(`globals.css`), 글꼴 |
| `components/` | 머리, 왼쪽 메뉴, 커리큘럼 목록, 챕터 틀(플레이어와 장 목록), 바닥 저작권 줄 |
| `lib/` | 레포 읽기(`content.ts`), README 바꾸기(`markdown.ts`) |
| `scripts/` | 빌드 전 복사, 빌드 뒤 페이지 수 점검 |
| `design/` | 디자인 시안. 사이트에서는 `/design/`으로 열려요 |

토큰을 바꾸면 `design/index.html` 시안도 같이 고쳐요.
