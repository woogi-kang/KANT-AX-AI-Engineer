// 사이트 이름, 메뉴, 아이콘처럼 여러 화면이 같이 쓰는 값이에요. 브라우저 쪽 컴포넌트도 쓰니 node 모듈을 쓰지 않아요.
export const NAME = "풀스택 AI/AX 엔지니어";
export const CONTACT = "woogi@memoriz.net";
export const COPYRIGHT = "Taewook Kang (woogi)";

/** 머리글 메뉴: [키, 이름, 주소] */
export const MENU = [
  ["roadmap", "로드맵", "/roadmap/"],
  ["lectures", "강의", "/lectures/"],
  ["library", "사례와 자료", "/library/"],
  ["news", "소식", "/updates/"],
] as const;
export type MenuKey = (typeof MENU)[number][0];

/** 주소로 머리글 메뉴 고르기 */
export function menuOf(path: string): MenuKey | "" {
  if (path.startsWith("/roadmap")) return "roadmap";
  if (/^\/(lectures|chapters|tips|extras)/.test(path)) return "lectures";
  if (path.startsWith("/library")) return "library";
  if (path.startsWith("/updates")) return "news";
  return "";
}

/* 뜻이 있는 자리에만 쓰는 아이콘(lucide 이름) */
export const STAGE_IC: Record<number, string> = { 1: "compass", 2: "layers", 3: "workflow", 4: "flag", 5: "building" };
export const AREA_IC: Record<string, string> = {
  "software-and-api": "plug",
  "llm-foundations": "brain",
  "agent-systems": "bot",
  "tools-and-mcp": "wrench",
  "evaluation-and-testing": "gauge",
  "production-operations": "activity",
  "security-and-privacy": "shield-check",
};
export const LIB_IC = { cases: "briefcase", public: "file-check", failures: "triangle-exclamation-point", templates: "clipboard-check", jobs: "chart-column" } as const;
export type LibKey = keyof typeof LIB_IC;
export const LIB_HREF: Record<LibKey, string> = { cases: "/library/", public: "/library/public/", failures: "/library/failures/", templates: "/library/templates/", jobs: "/library/jobs/" };
export const LIB_NAME: Record<LibKey, string> = { cases: "업무 사례", public: "공개 AX 사례", failures: "실패·중단 사례", templates: "실무 템플릿", jobs: "채용 현황" };
export const CASE_IC: Record<string, string> = { "고객·매출": "messages-square", "사람·협업": "users", "재무·구매": "receipt", "데이터·운영": "database", "공통 기능·운영": "layers" };
export const caseIcon = (area: string) => CASE_IC[area] ?? "briefcase";

/** 로드맵 단계 이름 줄이기: "직무 이해하기" → "직무" */
export const stageShort = (t: string) => t.replace(/ 익히기| 이해하기| 넓히기| 만들기/, "");
/** 챕터 이름의 괄호 풀이 빼기 */
export const shortTitle = (t: string) => t.replace(/\s*\(.*\)$/, "");
